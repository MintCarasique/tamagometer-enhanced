# Third-party notices — Tamagometer Desktop

This file describes the principal third-party software included in the Windows
Desktop build. It is informational and is not legal advice. The exact package
versions used for an official build are pinned in `requirements.txt` and
`requirements-dev.txt`.

## Qt for Python / PySide6 Essentials and Shiboken6

- Project: Qt for Python
- Version used by Desktop 3.0.0 builds: 6.11.2
- License choice used for this open-source distribution: GNU Lesser General
  Public License v3.0
- Homepage and source: <https://code.qt.io/cgit/pyside/pyside-setup.git/>
- License information: <https://doc.qt.io/qtforpython-6/licenses.html>

The application uses the unmodified dynamically linked Qt/PySide libraries
provided by the official Python wheels. This repository includes the complete
application source and build instructions, including an `onedir` build option,
so recipients can rebuild the application with a compatible modified library.
Corresponding Qt for Python source is available from the source link above.

## pySerial

- Version: 3.5
- License: BSD-3-Clause
- Source: <https://github.com/pyserial/pyserial>

## PyInstaller bootloader

- Version: 6.22.2
- License: GPL-2.0-or-later with the PyInstaller bootloader exception
- Source and license: <https://github.com/pyinstaller/pyinstaller>

The PyInstaller exception permits distribution of applications produced with
its bootloader under the application's own license.

## Tamagometer-derived assets and protocol work

Connection catalog data and sprites are derived from Zach Resmer's
MIT-licensed Tamagometer project. Friends packet data and timing work are based
on the public research credited in the repository README. See the repository
`LICENSE.md` and `README.md` for full attribution.
