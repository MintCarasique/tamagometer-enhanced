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
            expected = AppSettings(
                port="COM6",
                mode="friends",
                theme="dark",
                onboarding_complete=True,
                onboarding_skipped=False,
                favorites=("connection:4",),
                recent=("friends:255", "connection:4"),
                last_transfer="friends:255",
            )

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

    def test_invalid_extended_fields_are_safely_normalized(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(
                '{"theme":"neon","favorites":"bad","recent":[1,"connection:4"],"auto_connect":false}',
                encoding="utf-8",
            )
            settings = SettingsStore(path).load()
            self.assertEqual(settings.theme, "light")
            self.assertEqual(settings.favorites, ())
            self.assertEqual(settings.recent, ("connection:4",))
            self.assertFalse(settings.auto_connect)

    def test_skipped_onboarding_is_distinct_from_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text('{"onboarding_skipped":true}', encoding="utf-8")
            settings = SettingsStore(path).load()
            self.assertTrue(settings.onboarding_skipped)
            self.assertFalse(settings.onboarding_complete)


if __name__ == "__main__":
    unittest.main()
