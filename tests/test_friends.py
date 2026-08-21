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


if __name__ == "__main__":
    unittest.main()
