import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QUICK_BACKEND", "software")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from tamagometer_desktop.catalog import FAVORITES_CATEGORY
from tamagometer_desktop.modes import CONNECTION_MODE, LEGACY_MODE
from tamagometer_desktop.qt.app_view_model import AppViewModel
from tamagometer_desktop.qt.application import qml_root
from tamagometer_desktop.qt.catalog_model import CatalogModel
from tamagometer_desktop.settings import SettingsStore


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
    def test_main_qml_loads_headlessly(self):
        with tempfile.TemporaryDirectory() as temporary:
            engine = QQmlApplicationEngine()
            view_model = AppViewModel(SettingsStore(Path(temporary) / "settings.json"))
            engine.rootContext().setContextProperty("appViewModel", view_model)
            engine.addImportPath(str(qml_root()))
            engine.load(QUrl.fromLocalFile(str(qml_root() / "Main.qml")))
            self.assertEqual(len(engine.rootObjects()), 1)
            engine.clearComponentCache()


if __name__ == "__main__":
    unittest.main()
