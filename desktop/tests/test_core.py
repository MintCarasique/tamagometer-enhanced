from pathlib import Path
import re
import unittest

from tamagometer_core import (
    GIFT_ITEMS, GIFT_RESPONSE_2, GIFT_RESPONSE_4, gift_response_type_for,
    make_gift_response, make_gift_response_for_request, validate_message,
)


class ProtocolTests(unittest.TestCase):
    def test_templates_are_valid(self):
        self.assertTrue(validate_message(GIFT_RESPONSE_2))
        self.assertTrue(validate_message(GIFT_RESPONSE_4))

    def test_flipper_and_desktop_share_connection_templates(self):
        source = (
            Path(__file__).resolve().parents[2]
            / "flipper"
            / "tamagometer_protocol.c"
        ).read_text(encoding="utf-8")

        def c_string(name):
            match = re.search(
                rf"{name}\[\]\s*=\s*(?P<body>(?:\s*\"[01]+\")+)\s*;",
                source,
            )
            self.assertIsNotNone(match)
            return "".join(re.findall(r'\"([01]+)\"', match.group("body")))

        self.assertEqual(c_string("gift_response_2"), GIFT_RESPONSE_2)
        self.assertEqual(c_string("gift_response_4_template"), GIFT_RESPONSE_4)

    def test_every_documented_gift_generates_valid_message(self):
        self.assertEqual(len(GIFT_ITEMS), 181)
        for item_id, _name in GIFT_ITEMS:
            message = make_gift_response(item_id)
            self.assertTrue(validate_message(message))
            self.assertEqual(int(message[112:120], 2), item_id)

    def test_invalid_gift_is_rejected(self):
        with self.assertRaises(ValueError):
            make_gift_response(181)

    def test_live_gift_and_visit_request_gets_matching_response(self):
        request = "00001110" + "00000110" + "0" * 144
        response = make_gift_response_for_request(124, request)
        self.assertEqual(gift_response_type_for(request), 0x07)
        self.assertEqual(int(response[8:16], 2), 0x07)
        self.assertEqual(int(response[112:120], 2), 124)
        self.assertTrue(validate_message(response))


if __name__ == "__main__":
    unittest.main()
