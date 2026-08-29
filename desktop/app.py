"""Entry point for Tamagometer Desktop.

Qt Quick is the default UI during the 2.1 migration. Use ``--tk`` or set
``TAMAGOMETER_UI=tk`` to run the retained Tkinter implementation.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    use_tk = "--tk" in sys.argv or os.environ.get("TAMAGOMETER_UI", "").casefold() == "tk"
    if use_tk:
        if "--tk" in sys.argv:
            sys.argv.remove("--tk")
        from tamagometer_desktop.window import TamagometerDesktop

        TamagometerDesktop().mainloop()
        return 0
    from tamagometer_desktop.qt.application import run

    return run()


if __name__ == "__main__":
    raise SystemExit(main())
