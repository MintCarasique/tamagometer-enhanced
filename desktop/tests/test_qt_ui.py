import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Basic")

from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from tamagometer_desktop.catalog import FAVORITES_CATEGORY
from tamagometer_desktop.modes import CONNECTION_MODE, LEGACY_MODE
from tamagometer_desktop.qt.app_view_model import AppViewModel
from tamagometer_desktop.qt.application import qml_root
from tamagometer_desktop.qt.catalog_model import CatalogModel
from tamagometer_desktop.settings import AppSettings, SettingsStore
from tamagometer_desktop.transfer import AppEvent
from flipper_serial import CompanionInfo
from transfer_status import TransferState, TransferUpdate


APP = QGuiApplication.instance() or QGuiApplication(["tamagometer-tests"])


class QtCatalogModelTests(unittest.TestCase):
    def test_roles_filter_by_name_category_decimal_and_hex_id(self):
        model = CatalogModel(CONNECTION_MODE)
        self.assertEqual(model.count, 181)

        model.query = "Scone"
        self.assertEqual(model.count, 1)
        selected = model.index(0, 0)
        self.assertEqual(model.data(selected, model.NameRole), "Scone")

        item_id = model.data(selected, model.ItemIdRole)
        model.query = str(item_id)
        self.assertGreaterEqual(model.count, 1)
        model.query = f"0x{item_id:02X}"
        self.assertGreaterEqual(model.count, 1)

        model.query = ""
        model.category = "Snacks"
        self.assertTrue(model.count)
        for row in range(model.count):
            self.assertEqual(model.data(model.index(row, 0), model.CategoryRole), "Snacks")

    def test_selection_survives_filter_and_favorite_is_explicit(self):
        model = CatalogModel(CONNECTION_MODE)
        model.select(4)
        selected_name = model.selectedName
        model.query = selected_name
        self.assertEqual(model.selectedName, selected_name)
        self.assertFalse(model.selectedFavorite)

        model.toggleFavorite(model.selectedIndex)
        self.assertTrue(model.selectedFavorite)
        model.query = ""
        model.category = FAVORITES_CATEGORY
        self.assertEqual(model.count, 1)
        self.assertEqual(model.selectedName, selected_name)

    def test_legacy_mode_has_no_fake_catalog(self):
        model = CatalogModel(CONNECTION_MODE)
        model.set_mode(LEGACY_MODE)
        self.assertEqual(model.count, 0)
        self.assertEqual(model.selectedIndex, -1)


class QmlSmokeTests(unittest.TestCase):
    def load_window(self, temporary):
        engine = QQmlApplicationEngine()
        store = SettingsStore(Path(temporary) / "settings.json")
        store.save(AppSettings(auto_connect=False, onboarding_skipped=True))
        view_model = AppViewModel(store, port_provider=lambda: [], start_timer=False)
        engine.rootContext().setContextProperty("appViewModel", view_model)
        engine.addImportPath(str(qml_root()))
        engine.load(QUrl.fromLocalFile(str(qml_root() / "Main.qml")))
        self.assertEqual(len(engine.rootObjects()), 1)
        return engine, view_model, engine.rootObjects()[0]

    def test_main_qml_loads_headlessly(self):
        with tempfile.TemporaryDirectory() as temporary:
            engine, _view_model, window = self.load_window(temporary)
            APP.processEvents()
            self.assertEqual(window.width(), 1280)
            self.assertEqual(window.height(), 940)
            scroll = window.findChild(QObject, "mainScrollView")
            catalog = window.findChild(QObject, "catalogGrid")
            self.assertIsNotNone(scroll)
            self.assertEqual(catalog.property("scrollbarGutter"), 18)
            self.assertLessEqual(
                float(scroll.property("contentHeight")),
                float(scroll.property("availableHeight")) + 1,
            )
            engine.clearComponentCache()

    def test_interactive_icons_do_not_use_font_glyphs(self):
        qml_directory = qml_root()
        sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in qml_directory.rglob("*.qml")
        )
        for glyph in ("★", "☆", "☀", "☾", "⌄", "▼", "▲"):
            self.assertNotIn(glyph, sources)
        icon_source = (qml_directory / "components" / "UiIcon.qml").read_text(encoding="utf-8")
        for icon_name in ("chevron-down", "star", "sun", "moon", "settings", "diagnostics"):
            self.assertIn(f'root.name === "{icon_name}"', icon_source)

    def test_control_palette_follows_the_app_theme(self):
        with tempfile.TemporaryDirectory() as temporary:
            engine, view_model, window = self.load_window(temporary)
            APP.processEvents()
            header_button = window.findChild(QObject, "headerDiagnosticsButton")
            primary_button = window.findChild(QObject, "primaryTransferAction")
            port_selector = window.findChild(QObject, "portSelector")
            self.assertEqual(header_button.property("resolvedTextColor").name(), "#182230")
            self.assertEqual(primary_button.property("resolvedTextColor").name(), "#667085")
            self.assertEqual(port_selector.property("resolvedBaseColor").name(), "#f9fafb")
            self.assertEqual(port_selector.property("resolvedIndicatorColor").name(), "#182230")

            view_model.toggleTheme(); APP.processEvents()
            self.assertEqual(header_button.property("resolvedTextColor").name(), "#f2f4f7")
            self.assertEqual(primary_button.property("resolvedTextColor").name(), "#aab2c0")
            self.assertEqual(port_selector.property("resolvedBaseColor").name(), "#1d2435")
            self.assertEqual(port_selector.property("resolvedIndicatorColor").name(), "#f2f4f7")
            engine.clearComponentCache()

    def test_responsive_breakpoints_preserve_selection_and_theme(self):
        with tempfile.TemporaryDirectory() as temporary:
            engine, view_model, window = self.load_window(temporary)
            view_model.catalogModel.select(7)
            selected = view_model.catalogModel.selectedItemKey
            for width, expected in ((720, "compact"), (900, "medium"), (1280, "wide")):
                window.setWidth(width); APP.processEvents()
                self.assertEqual(window.property("layoutClass"), expected)
                self.assertEqual(view_model.catalogModel.selectedItemKey, selected)
            view_model.toggleTheme(); APP.processEvents()
            self.assertTrue(view_model.darkTheme)
            self.assertEqual(view_model.catalogModel.selectedItemKey, selected)
            for object_name in ("portSelector", "catalogSearch", "catalogGrid", "primaryTransferAction"):
                self.assertIsNotNone(window.findChild(QObject, object_name))
            engine.clearComponentCache()


class QtWorkflowTests(unittest.TestCase):
    class FakeConnection:
        connected = True
        port = "COM6"
        companion = CompanionInfo("2.0.0", 1, frozenset())

        def open(self, port):
            self.port = port
            return CompanionInfo("2.0.0", 1, frozenset())

        def close(self):
            self.connected = False

        def deliver_gift(self, _response, _gift, _cancel, status):
            for state in (TransferState.WAITING_FIRST_MESSAGE, TransferState.SENDING_ACKNOWLEDGEMENT,
                          TransferState.WAITING_GIFT_REQUEST, TransferState.SENDING_GIFT):
                status(TransferUpdate(state, state.value))

        def send_friends_reward(self, _item, _cancel, status):
            status(TransferUpdate(TransferState.BROADCASTING, "Broadcasting", 0, 10))
            status(TransferUpdate(TransferState.BROADCASTING, "Broadcasting", 10, 10))
            status(TransferUpdate(TransferState.VERIFYING, "Verifying"))

        def run_legacy_fallback(self, _cancel, status):
            for state in (TransferState.WAITING_FIRST_MESSAGE, TransferState.SENDING_ACKNOWLEDGEMENT,
                          TransferState.WAITING_GIFT_REQUEST, TransferState.SENDING_RESULT):
                status(TransferUpdate(state, state.value))

    def make_view_model(self, directory):
        store = SettingsStore(Path(directory) / "settings.json")
        store.save(AppSettings(auto_connect=False))
        view_model = AppViewModel(store, self.FakeConnection(), lambda: [], start_timer=False)
        view_model._connection_results.put((True, "COM6", CompanionInfo("2.0.0", 1, frozenset())))
        view_model.drainEvents()
        return view_model

    def test_all_three_workflows_complete_and_enable_repeat(self):
        with tempfile.TemporaryDirectory() as temporary:
            view_model = self.make_view_model(temporary)
            for mode in ("connection", "friends", "legacy"):
                view_model.setMode(mode)
                self.assertTrue(view_model.canStartTransfer)
                view_model.startTransfer()
                view_model._transfer.worker.join(1)
                view_model.drainEvents()
                self.assertEqual(view_model.transferState, "completed")
                self.assertEqual(view_model.transferProgress, 1.0)
                self.assertTrue(view_model.canRepeatTransfer)

    def test_disconnect_event_exposes_friendly_summary_and_detail(self):
        with tempfile.TemporaryDirectory() as temporary:
            view_model = self.make_view_model(temporary)
            view_model._events.put(AppEvent(
                "disconnected", "USB cable removed", TransferState.DISCONNECTED,
            ))
            view_model.drainEvents()
            self.assertEqual(view_model.connectionState, "disconnected")
            self.assertEqual(view_model.noticeSummary, "The transfer could not be completed.")
            self.assertEqual(view_model.noticeDetail, "USB cable removed")

    def test_onboarding_close_skip_and_success_are_distinct(self):
        with tempfile.TemporaryDirectory() as temporary:
            store = SettingsStore(Path(temporary) / "settings.json")
            store.save(AppSettings(auto_connect=False))
            view_model = AppViewModel(store, self.FakeConnection(), lambda: [], start_timer=False)
            self.assertTrue(view_model.onboardingVisible)
            view_model.closeOnboarding()
            self.assertFalse(store.load().onboarding_complete)
            self.assertFalse(store.load().onboarding_skipped)
            view_model.runSetupAgain(); view_model.skipOnboarding()
            self.assertTrue(store.load().onboarding_skipped)
            view_model.runSetupAgain()
            view_model._connection_results.put((True, "COM6", CompanionInfo("2.0.0", 1, frozenset())))
            view_model.drainEvents()
            view_model.onboardingNext(); view_model.onboardingNext(); view_model.onboardingNext()
            self.assertTrue(view_model.onboardingReady)
            self.assertFalse(store.load().onboarding_complete)
            view_model.onboardingNext()
            self.assertTrue(store.load().onboarding_complete)
            self.assertFalse(store.load().onboarding_skipped)

    def test_settings_and_diagnostic_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            view_model = self.make_view_model(temporary)
            view_model.setAutoConnect(True)
            view_model.setReducedMotion(True)
            self.assertTrue(view_model.autoConnect)
            self.assertTrue(view_model.reducedMotion)
            destination = Path(temporary) / "diagnostics.txt"
            view_model.exportDiagnostics(destination.as_uri())
            report = destination.read_text(encoding="utf-8")
            self.assertIn("Desktop version: 3.0.0-dev", report)
            self.assertIn("Diagnostics log:", report)


if __name__ == "__main__":
    unittest.main()
