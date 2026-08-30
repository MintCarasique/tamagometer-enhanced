"""Qt application bootstrap kept separate from protocol and serial modules."""

from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QCoreApplication, Qt, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from .app_view_model import AppViewModel


def qml_root() -> Path:
    return Path(__file__).resolve().parent / "qml"


def run(argv: list[str] | None = None) -> int:
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # Avoid inheriting a partly dark Windows style when the in-app theme is
    # light. The Basic style is fully paletteable and consistent in packages.
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication(argv or sys.argv)
    app.setApplicationName("Tamagometer Enhanced")
    app.setOrganizationName("Tamagometer Enhanced")
    engine = QQmlApplicationEngine()
    view_model = AppViewModel()
    app.aboutToQuit.connect(view_model.shutdown)
    engine.rootContext().setContextProperty("appViewModel", view_model)
    engine.addImportPath(str(qml_root()))
    engine.load(QUrl.fromLocalFile(str(qml_root() / "Main.qml")))
    if not engine.rootObjects():
        return 1
    return app.exec()
