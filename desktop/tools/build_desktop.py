"""Build a reproducible Qt-only Windows package with PyInstaller."""

from __future__ import annotations

import argparse
from pathlib import Path

from PyInstaller.__main__ import run


PROJECT_DIR = Path(__file__).resolve().parents[1]


def build_arguments(
    mode: str = "onefile",
    dist_dir: Path = Path("../release"),
    name: str = "TamagometerDesktop",
    clean: bool = False,
) -> list[str]:
    """Return the PyInstaller arguments used locally and by GitHub Actions."""
    command = [
        "--noconfirm",
        "--windowed",
        f"--{mode}",
        "--name", name,
        "--distpath", str(dist_dir),
        "--workpath", str(PROJECT_DIR / "build" / name),
        "--specpath", str(PROJECT_DIR / "build" / name),
        "--add-data", f"{PROJECT_DIR / 'assets'};assets",
        "--add-data",
        f"{PROJECT_DIR / 'tamagometer_desktop' / 'qt' / 'qml'};tamagometer_desktop/qt/qml",
        "--exclude-module", "tkinter",
        "--exclude-module", "_tkinter",
        "--exclude-module", "PySide6.QtWebEngineCore",
        "--exclude-module", "PySide6.QtWebEngineQuick",
        "--exclude-module", "PySide6.QtWebEngineWidgets",
        str(PROJECT_DIR / "qt_app.py"),
    ]
    if clean:
        command.insert(1, "--clean")
    return command


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("onefile", "onedir"), default="onefile")
    parser.add_argument("--dist-dir", type=Path, default=Path("../release"))
    parser.add_argument("--name", default="TamagometerDesktop")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    run(build_arguments(args.mode, args.dist_dir, args.name, args.clean))


if __name__ == "__main__":
    main()
