import unittest

from tamagometer_desktop.modes import CONNECTION_MODE, FRIENDS_MODE, get_mode


class ModeDefinitionTests(unittest.TestCase):
    def test_catalogs_and_id_formats(self):
        self.assertEqual(len(CONNECTION_MODE.items), 181)
        self.assertEqual(CONNECTION_MODE.list_id(4), "004")
        self.assertEqual(CONNECTION_MODE.selected_id(4), "4")
        self.assertEqual(len(FRIENDS_MODE.items), 65)
        self.assertEqual(FRIENDS_MODE.list_id(255), "FF")
        self.assertEqual(FRIENDS_MODE.selected_id(255), "0xFF")

    def test_unknown_mode_falls_back_to_connection(self):
        self.assertIs(get_mode("unknown"), CONNECTION_MODE)


if __name__ == "__main__":
    unittest.main()
