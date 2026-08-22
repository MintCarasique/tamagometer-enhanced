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
        return AppSettings(
            port=port if isinstance(port, str) else "",
            mode=mode if isinstance(mode, str) else DEFAULT_MODE,
        )

    def save(self, settings: AppSettings) -> None:
        try:
            self.path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
        except OSError:
            pass
