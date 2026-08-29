"""Catalog categories, persistent item keys, and sprite filename mapping."""

from __future__ import annotations

from .modes import ModeDefinition, get_mode


ALL_CATEGORY = "All"
FAVORITES_CATEGORY = "★ Favorites"
RECENT_CATEGORY = "Recently sent"

CONNECTION_CATEGORIES = (
    ALL_CATEGORY,
    FAVORITES_CATEGORY,
    RECENT_CATEGORY,
    "Food",
    "Snacks",
    "Items & Toys",
    "Animations",
    "Souvenirs & Special",
)
FRIENDS_CATEGORIES = (
    ALL_CATEGORY,
    FAVORITES_CATEGORY,
    RECENT_CATEGORY,
    "Gotchi Points",
    "Jewelry",
)

SPRITE_ALIASES = {
    "RC Car 2 (duck)": "rc_car_2_duck_sprite.png",
    "Building Block": "bldg_block_sprite.png",
    "! ! (Clone)": "!_!_sprite.png",
    "Cone (animation)": "cone_sprite.png",
    "Flower (animation)": "flower_sprite.png",
    "Poop (animation)": "poop_sprite.png",
    "Cake (animation)": "cake_sprite.png",
    "Heart (animation)": "heart_sprite.png",
    "Snake (animation)": "snake_sprite.png",
}


def item_key(mode_key: str, item_id: int) -> str:
    return f"{mode_key}:{item_id}"


def parse_item_key(value: str) -> tuple[ModeDefinition, int] | None:
    try:
        mode_key, raw_id = value.split(":", 1)
        mode = get_mode(mode_key)
        item_id = int(raw_id)
    except (AttributeError, ValueError):
        return None
    if mode.key != mode_key or not any(candidate == item_id for candidate, _ in mode.items):
        return None
    return mode, item_id


def categories_for(mode: ModeDefinition) -> tuple[str, ...]:
    if mode.key == "legacy":
        return (ALL_CATEGORY,)
    return FRIENDS_CATEGORIES if mode.key == "friends" else CONNECTION_CATEGORIES


def category_for(mode: ModeDefinition, item_id: int) -> str:
    if mode.key == "legacy":
        return "Automatic"
    if mode.key == "friends":
        return "Gotchi Points" if item_id >= 0xFB else "Jewelry"
    if item_id <= 35:
        return "Food"
    if item_id <= 77:
        return "Snacks"
    if item_id <= 131:
        return "Items & Toys"
    if item_id <= 141:
        return "Animations"
    return "Souvenirs & Special"


def sprite_filename(mode: ModeDefinition, item_name: str) -> str | None:
    if mode.key != "connection":
        return None
    return SPRITE_ALIASES.get(
        item_name,
        item_name.lower().replace(" ", "_") + "_sprite.png",
    )


def item_name(mode: ModeDefinition, item_id: int) -> str | None:
    return next((name for candidate, name in mode.items if candidate == item_id), None)
