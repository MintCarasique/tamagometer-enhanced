import json
from pathlib import Path
import tempfile
import unittest

from tamagometer_desktop.settings import AppSettings, SettingsStore


class SettingsStoreTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            store = SettingsStore(path)
            expected = AppSettings(port="COM6", mode="friends")

            store.save(expected)

            self.assertEqual(store.load(), expected)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["port"], "COM6")

    def test_missing_or_invalid_file_uses_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            store = SettingsStore(path)
            self.assertEqual(store.load(), AppSettings())
            path.write_text("[]", encoding="utf-8")
            self.assertEqual(store.load(), AppSettings())


if __name__ == "__main__":
    unittest.main()
