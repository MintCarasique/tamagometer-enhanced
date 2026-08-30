"""Qt-only release entry point.

The development entry point in ``app.py`` retains the Tkinter fallback. Release
packaging uses this module so Tcl/Tk is not bundled into the Qt application.
"""

from tamagometer_desktop.qt.application import run


if __name__ == "__main__":
    raise SystemExit(run())
