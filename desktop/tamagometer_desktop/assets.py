"""Runtime paths for bundled desktop assets."""

from __future__ import annotations

from pathlib import Path
import sys


def asset_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "assets"
    return Path(__file__).resolve().parent.parent / "assets"


def item_sprite_path(filename: str | None) -> Path | None:
    if not filename:
        return None
    path = asset_root() / "item-sprites" / filename
    return path if path.is_file() else None
