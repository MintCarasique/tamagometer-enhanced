from pathlib import Path
import re
import unittest

from tamagometer_desktop.assets import item_sprite_path
from tamagometer_desktop.catalog import category_for, item_key, parse_item_key, sprite_filename
from tamagometer_desktop.modes import CONNECTION_MODE, FRIENDS_MODE


class CatalogPresentationTests(unittest.TestCase):
    def test_connection_catalog_has_stable_categories(self):
        self.assertEqual(category_for(CONNECTION_MODE, 0), "Food")
        self.assertEqual(category_for(CONNECTION_MODE, 36), "Snacks")
        self.assertEqual(category_for(CONNECTION_MODE, 78), "Items & Toys")
        self.assertEqual(category_for(CONNECTION_MODE, 132), "Animations")
        self.assertEqual(category_for(CONNECTION_MODE, 142), "Souvenirs & Special")

    def test_friends_points_and_jewelry_are_separate(self):
        self.assertEqual(category_for(FRIENDS_MODE, 0xFF), "Gotchi Points")
        self.assertEqual(category_for(FRIENDS_MODE, 0x00), "Jewelry")

    def test_persistent_item_keys_round_trip(self):
        parsed = parse_item_key(item_key("connection", 4))
        self.assertIsNotNone(parsed)
        self.assertEqual((parsed[0].key, parsed[1]), ("connection", 4))
        self.assertIsNone(parse_item_key("unknown:4"))
        self.assertIsNone(parse_item_key("connection:999"))

    def test_upstream_sprites_cover_most_connection_items(self):
        available = sum(
            item_sprite_path(sprite_filename(CONNECTION_MODE, name)) is not None
            for _item_id, name in CONNECTION_MODE.items
        )
        self.assertGreaterEqual(available, 170)
        self.assertIsNotNone(item_sprite_path(sprite_filename(CONNECTION_MODE, "Scone")))

    def test_flipper_catalog_and_generated_icons_stay_in_sync(self):
        flipper = Path(__file__).resolve().parents[2] / "flipper"
        source = (flipper / "tamagometer_catalog.c").read_text(encoding="utf-8")
        body = re.search(
            r"connection_items\[\]\s*=\s*\{(?P<body>.*?)\};",
            source,
            re.DOTALL,
        )
        self.assertIsNotNone(body)
        names = tuple(re.findall(r'"([^"]+)"', body.group("body")))
        self.assertEqual(names, tuple(name for _item_id, name in CONNECTION_MODE.items))
        self.assertGreaterEqual(len(tuple((flipper / "item_icons").glob("item_*.png"))), 170)


if __name__ == "__main__":
    unittest.main()
