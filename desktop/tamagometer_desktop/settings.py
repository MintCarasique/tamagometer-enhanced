"""Persistent desktop application settings."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys


DEFAULT_MODE = "connection"


@dataclass(frozen=True)
class AppSettings:
    port: str = ""
    mode: str = DEFAULT_MODE
    theme: str = "light"
    auto_connect: bool = True
    onboarding_complete: bool = False
    onboarding_skipped: bool = False
    reduced_motion: bool = False
    favorites: tuple[str, ...] = ()
    recent: tuple[str, ...] = ()
    last_transfer: str = ""


def default_config_path() -> Path:
    """Return the legacy-compatible config location beside the app."""
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).resolve().parent
    else:
        app_dir = Path(__file__).resolve().parent.parent
    return app_dir / ".tamagometer-desktop.json"


class SettingsStore:
    def __init__(self, path: Path | None = None):
        self.path = path or default_config_path()

    def load(self) -> AppSettings:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return AppSettings()
        if not isinstance(data, dict):
            return AppSettings()
        port = data.get("port", "")
        mode = data.get("mode", DEFAULT_MODE)
        theme = data.get("theme", "light")
        favorites = data.get("favorites", [])
        recent = data.get("recent", [])
        return AppSettings(
            port=port if isinstance(port, str) else "",
            mode=mode if isinstance(mode, str) else DEFAULT_MODE,
            theme=theme if theme in {"light", "dark"} else "light",
            auto_connect=data.get("auto_connect", True) is not False,
            onboarding_complete=data.get("onboarding_complete", False) is True,
            onboarding_skipped=data.get("onboarding_skipped", False) is True,
            reduced_motion=data.get("reduced_motion", False) is True,
            favorites=tuple(value for value in favorites if isinstance(value, str))
            if isinstance(favorites, list) else (),
            recent=tuple(value for value in recent if isinstance(value, str))[:12]
            if isinstance(recent, list) else (),
            last_transfer=data.get("last_transfer", "")
            if isinstance(data.get("last_transfer", ""), str) else "",
        )

    def save(self, settings: AppSettings) -> None:
        try:
            self.path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
        except OSError:
            pass
