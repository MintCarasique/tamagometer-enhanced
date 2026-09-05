"""Qt list-model adapter for the existing Tamagometer catalogs."""

from __future__ import annotations

from PySide6.QtCore import (
    QAbstractListModel,
    QByteArray,
    QModelIndex,
    Property,
    Qt,
    QUrl,
    Signal,
    Slot,
)

from ..assets import item_sprite_path
from ..catalog import (
    ALL_CATEGORY,
    FAVORITES_CATEGORY,
    RECENT_CATEGORY,
    category_for,
    item_key,
    sprite_filename,
)
from ..modes import ModeDefinition


class CatalogModel(QAbstractListModel):
    ItemIdRole = Qt.UserRole + 1
    DisplayIdRole = Qt.UserRole + 2
    NameRole = Qt.UserRole + 3
    CategoryRole = Qt.UserRole + 4
    FavoriteRole = Qt.UserRole + 5
    RecentRole = Qt.UserRole + 6
    SpriteUrlRole = Qt.UserRole + 7
    KeyRole = Qt.UserRole + 8

    ROLE_FIELDS = {
        ItemIdRole: "itemId",
        DisplayIdRole: "displayId",
        NameRole: "name",
        CategoryRole: "category",
        FavoriteRole: "favorite",
        RecentRole: "recent",
        SpriteUrlRole: "spriteUrl",
        KeyRole: "itemKey",
    }

    countChanged = Signal()
    queryChanged = Signal()
    categoryChanged = Signal()
    selectionChanged = Signal()
    favoritesChanged = Signal(object)

    def __init__(self, mode: ModeDefinition, favorites=(), recent=(), parent=None):
        super().__init__(parent)
        self._mode = mode
        self._favorites = tuple(favorites)
        self._recent = tuple(recent)
        self._query = ""
        self._category = ALL_CATEGORY
        self._rows: list[dict] = []
        self._selected_key = ""
        self._rebuild()

    def roleNames(self):
        return {
            role: QByteArray(field.encode("ascii"))
            for role, field in self.ROLE_FIELDS.items()
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._rows):
            return None
        row = self._rows[index.row()]
        field = "name" if role == Qt.DisplayRole else self.ROLE_FIELDS.get(role)
        return row.get(field) if field else None

    def _display_id(self, item_id: int) -> str:
        if self._mode.hexadecimal_ids:
            return f"0x{item_id:02X} · {item_id}"
        return f"{item_id:03d} · 0x{item_id:02X}"

    def _make_row(self, item_id: int, name: str) -> dict:
        key = item_key(self._mode.key, item_id)
        path = item_sprite_path(sprite_filename(self._mode, name))
        return {
            "itemId": item_id,
            "displayId": self._display_id(item_id),
            "name": name,
            "category": category_for(self._mode, item_id),
            "favorite": key in self._favorites,
            "recent": key in self._recent,
            "spriteUrl": QUrl.fromLocalFile(str(path)).toString() if path else "",
            "itemKey": key,
        }

    def _matches_query(self, row: dict) -> bool:
        query = self._query.strip().casefold()
        if not query:
            return True
        item_id = row["itemId"]
        searchable = " ".join(
            (
                row["name"],
                row["category"],
                str(item_id),
                f"{item_id:03d}",
                f"0x{item_id:02x}",
                f"{item_id:02x}",
            )
        ).casefold()
        return query in searchable

    def _rebuild(self) -> None:
        selected = self._selected_key
        candidates = [] if self._mode.key == "legacy" else list(self._mode.items)
        recent_order = {key: index for index, key in enumerate(self._recent)}
        if self._category == RECENT_CATEGORY:
            candidates.sort(
                key=lambda item: recent_order.get(
                    item_key(self._mode.key, item[0]), 9999
                )
            )
        rows = []
        for item_id, name in candidates:
            row = self._make_row(item_id, name)
            if self._category == FAVORITES_CATEGORY and not row["favorite"]:
                continue
            if self._category == RECENT_CATEGORY and not row["recent"]:
                continue
            if (
                self._category
                not in {ALL_CATEGORY, FAVORITES_CATEGORY, RECENT_CATEGORY}
                and row["category"] != self._category
            ):
                continue
            if self._matches_query(row):
                rows.append(row)
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
        keys = [row["itemKey"] for row in rows]
        self._selected_key = selected if selected in keys else (keys[0] if keys else "")
        self.countChanged.emit()
        self.selectionChanged.emit()

    def set_mode(self, mode: ModeDefinition) -> None:
        self._mode = mode
        self._category = ALL_CATEGORY
        self._query = ""
        self.queryChanged.emit()
        self.categoryChanged.emit()
        self._rebuild()

    def set_recent(self, recent) -> None:
        self._recent = tuple(recent)
        self._rebuild()

    @Property(int, notify=countChanged)
    def count(self):
        return len(self._rows)

    @Property(str, notify=queryChanged)
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        value = str(value)
        if value == self._query:
            return
        self._query = value
        self.queryChanged.emit()
        self._rebuild()

    @Property(str, notify=categoryChanged)
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        value = str(value) or ALL_CATEGORY
        if value == self._category:
            return
        self._category = value
        self.categoryChanged.emit()
        self._rebuild()

    @Property(int, notify=selectionChanged)
    def selectedIndex(self):
        return next(
            (
                index
                for index, row in enumerate(self._rows)
                if row["itemKey"] == self._selected_key
            ),
            -1,
        )

    def _selected_value(self, field: str, default=""):
        index = self.selectedIndex
        return self._rows[index][field] if index >= 0 else default

    @Property(str, notify=selectionChanged)
    def selectedName(self):
        return self._selected_value("name")

    @Property(int, notify=selectionChanged)
    def selectedItemId(self):
        return int(self._selected_value("itemId", -1))

    @Property(str, notify=selectionChanged)
    def selectedItemKey(self):
        return self._selected_value("itemKey")

    @Property(str, notify=selectionChanged)
    def selectedDisplayId(self):
        return self._selected_value("displayId")

    @Property(str, notify=selectionChanged)
    def selectedSpriteUrl(self):
        return self._selected_value("spriteUrl")

    @Property(bool, notify=selectionChanged)
    def selectedFavorite(self):
        return bool(self._selected_value("favorite", False))

    @Slot(int)
    def select(self, index: int):
        if not 0 <= index < len(self._rows):
            return
        key = self._rows[index]["itemKey"]
        if key != self._selected_key:
            self._selected_key = key
            self.selectionChanged.emit()

    def select_key(self, key: str) -> bool:
        index = next(
            (i for i, row in enumerate(self._rows) if row["itemKey"] == key), -1
        )
        if index < 0:
            return False
        self.select(index)
        return True

    @Slot(int)
    def toggleFavorite(self, index: int):
        if not 0 <= index < len(self._rows):
            return
        key = self._rows[index]["itemKey"]
        favorites = list(self._favorites)
        if key in favorites:
            favorites.remove(key)
        else:
            favorites.append(key)
        self._favorites = tuple(favorites)
        self._selected_key = key
        self.favoritesChanged.emit(self._favorites)
        self._rebuild()
