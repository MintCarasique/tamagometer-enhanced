"""Top-level state exposed to the Qt Quick presentation layer."""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QObject, Property, Signal, Slot

from .. import __version__
from ..catalog import categories_for
from ..modes import MODES, get_mode
from ..settings import SettingsStore
from .catalog_model import CatalogModel


class AppViewModel(QObject):
    modeChanged = Signal()
    themeChanged = Signal()

    def __init__(self, settings_store: SettingsStore | None = None, parent=None):
        super().__init__(parent)
        self._store = settings_store or SettingsStore()
        self._settings = self._store.load()
        self._mode = get_mode(self._settings.mode)
        self._catalog = CatalogModel(
            self._mode, self._settings.favorites, self._settings.recent, self,
        )
        self._catalog.favoritesChanged.connect(self._save_favorites)

    def _save(self, **changes) -> None:
        self._settings = replace(self._settings, **changes)
        self._store.save(self._settings)

    @Slot(object)
    def _save_favorites(self, favorites) -> None:
        self._save(favorites=tuple(favorites))

    @Property(str, constant=True)
    def version(self):
        return __version__

    @Property(QObject, constant=True)
    def catalogModel(self):
        return self._catalog

    @Property("QVariantList", constant=True)
    def modes(self):
        return [{"key": mode.key, "label": mode.selector_label} for mode in MODES.values()]

    @Property(str, notify=modeChanged)
    def modeKey(self):
        return self._mode.key

    @Property(str, notify=modeChanged)
    def pickerTitle(self):
        return self._mode.picker_title

    @Property(str, notify=modeChanged)
    def pickerHint(self):
        return self._mode.picker_hint

    @Property(str, notify=modeChanged)
    def instructions(self):
        return self._mode.instructions

    @Property(str, notify=modeChanged)
    def primaryActionLabel(self):
        return self._mode.send_label

    @Property(str, notify=modeChanged)
    def primaryActionHint(self):
        return "Connect a verified Flipper to enable transfers. Live controls remain in the Tk fallback during this migration slice."

    @Property(bool, notify=modeChanged)
    def legacyMode(self):
        return self._mode.key == "legacy"

    @Property("QStringList", notify=modeChanged)
    def categories(self):
        return list(categories_for(self._mode))

    @Slot(str)
    def setMode(self, key: str):
        mode = get_mode(key)
        if mode.key == self._mode.key:
            return
        self._mode = mode
        self._catalog.set_mode(mode)
        self._save(mode=mode.key)
        self.modeChanged.emit()

    @Property(bool, notify=themeChanged)
    def darkTheme(self):
        return self._settings.theme == "dark"

    @Slot()
    def toggleTheme(self):
        theme = "light" if self.darkTheme else "dark"
        self._save(theme=theme)
        self.themeChanged.emit()

