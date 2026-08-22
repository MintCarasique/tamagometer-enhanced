from pathlib import Path
import re
import unittest

from friends_core import (
    FRIENDS_CONNECT_ACK, FRIENDS_REWARDS, make_bff_reward_packet,
)


class FriendsProtocolTests(unittest.TestCase):
    def test_connect_ack_matches_documented_capture(self):
        self.assertEqual(
            FRIENDS_CONNECT_ACK.hex(" ").upper(),
            "F0 01 0F 01 01 0F 0B 00 06 80 02 08 01 08 1A 1A 1A 1A 2D",
        )

    def test_reward_packet_and_checksum(self):
        self.assertEqual(
            make_bff_reward_packet(0x06).hex(" ").upper(),
            "F0 07 05 01 07 0F 0B 06 34",
        )
        self.assertEqual(
            make_bff_reward_packet(0xFD).hex(" ").upper(),
            "F0 07 05 01 07 0F 0B FD 2B",
        )

    def test_reward_catalog(self):
        self.assertEqual(len(FRIENDS_REWARDS), 65)
        self.assertEqual({item_id for item_id, _ in FRIENDS_REWARDS[:5]}, set(range(251, 256)))
        self.assertEqual([item_id for item_id, _ in FRIENDS_REWARDS[5:]], list(range(60)))

    def test_invalid_outcome_is_rejected(self):
        with self.assertRaises(ValueError):
            make_bff_reward_packet(256)

    def test_flipper_and_python_share_the_same_packet_constants(self):
        source_path = Path(__file__).resolve().parents[2] / "flipper" / "tamagometer_protocol.c"
        source = source_path.read_text(encoding="utf-8")
        connect_body = re.search(r"connect_ack\[\]\s*=\s*\{([^}]+)\}", source, re.DOTALL)
        reward_body = re.search(r"uint8_t reward\[\]\s*=\s*\{([^}]+)\}", source, re.DOTALL)
        self.assertIsNotNone(connect_body)
        self.assertIsNotNone(reward_body)

        connect = bytes(int(value, 16) for value in re.findall(r"0x([0-9A-Fa-f]{2})", connect_body.group(1)))
        reward = []
        for token in reward_body.group(1).split(","):
            token = token.strip()
            reward.append(0x06 if token == "outcome" else int(token, 16))
        reward[-1] = (0x2E + 0x06) & 0xFF

        self.assertEqual(connect, FRIENDS_CONNECT_ACK)
        self.assertEqual(bytes(reward), make_bff_reward_packet(0x06))
        self.assertRegex(source, r"reward\[8\]\s*=\s*\(uint8_t\)\(0x2E \+ outcome\)")


if __name__ == "__main__":
    unittest.main()
