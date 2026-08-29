"""Convert every catalog sprite to a deterministic, correctly labelled PNG."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def normalize_sprite(path: Path) -> bool:
    """Rewrite *path* as PNG when its content does not have a PNG signature."""
    if path.read_bytes().startswith(PNG_SIGNATURE):
        return False
    temporary = path.with_suffix(".normalized.png")
    with Image.open(path) as image:
        image.convert("RGBA").save(temporary, format="PNG", optimize=True)
    temporary.replace(path)
    return True


def normalize_directory(directory: Path) -> int:
    converted = 0
    for path in sorted(directory.glob("*.png")):
        converted += normalize_sprite(path)
    return converted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "assets" / "item-sprites",
    )
    args = parser.parse_args()
    print(f"Normalized {normalize_directory(args.directory)} sprite(s).")


if __name__ == "__main__":
    main()
