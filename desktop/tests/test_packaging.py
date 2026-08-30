import ast
import unittest
from pathlib import Path

from tools.build_desktop import PROJECT_DIR, build_arguments


class PackagingTests(unittest.TestCase):
    def test_release_entry_point_is_qt_only(self):
        source = (PROJECT_DIR / "qt_app.py").read_text(encoding="utf-8")
        self.assertIn("tamagometer_desktop.qt.application", source)
        tree = ast.parse(source)
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module or ""
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        self.assertFalse(any(name.startswith("tkinter") for name in imports))

    def test_build_includes_runtime_assets_and_excludes_tk(self):
        arguments = build_arguments(clean=True)
        command = " ".join(str(value) for value in arguments)
        self.assertIn("--onefile", arguments)
        self.assertIn("tamagometer_desktop/qt/qml", command)
        self.assertIn(str(PROJECT_DIR / "assets"), command)
        self.assertIn("tkinter", arguments)
        self.assertTrue(arguments[-1].endswith("qt_app.py"))


if __name__ == "__main__":
    unittest.main()
