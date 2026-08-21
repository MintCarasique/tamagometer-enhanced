"""Protocol helpers for Tamagotchi Friends BFF bump emulation.

The packet layout is based on the public Tamagotchi Friends captures and the
Proxmark transmitter published by Natalie Silvanovich and MrBlinky.
"""

from __future__ import annotations


FRIENDS_IDENTITY = 0x0B


def _packet(*data: int) -> bytes:
    """Build a Friends packet with its F0 sync byte and byte-sum checksum."""
    if any(not 0 <= value <= 0xFF for value in data):
        raise ValueError("Packet bytes must be between 0 and 255")
    return bytes((0xF0, *data, sum(data) & 0xFF))


FRIENDS_CONNECT_ACK = _packet(
    0x01, 0x0F,
    0x01, 0x01, 0x0F, FRIENDS_IDENTITY,
    0x00, 0x06, 0x80,
    0x02, 0x08, 0x01, 0x08, 0x1A, 0x1A, 0x1A, 0x1A,
)


def make_bff_reward_packet(outcome: int) -> bytes:
    """Return the receiver's final BFF packet for an outcome byte."""
    if not 0 <= outcome <= 0xFF:
        raise ValueError("Friends outcome must be between 0 and 255")
    return _packet(0x07, 0x05, 0x01, 0x07, 0x0F, FRIENDS_IDENTITY, outcome)


FRIENDS_REWARDS = (
    (0xFF, "1,000 Gotchi Points — cherries"),
    (0xFE, "800 Gotchi Points — flowers"),
    (0xFD, "600 Gotchi Points — music notes"),
    (0xFC, "400 Gotchi Points — stars"),
    (0xFB, "200 Gotchi Points — hearts"),
    *((index, f"Jewelry #{index + 1:02d}") for index in range(60)),
)

