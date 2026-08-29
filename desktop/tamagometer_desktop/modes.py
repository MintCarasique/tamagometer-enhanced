"""Presentation metadata and item catalogs for supported Tamagotchi modes."""

from __future__ import annotations

from dataclasses import dataclass

from friends_core import FRIENDS_REWARDS
from tamagometer_core import GIFT_ITEMS


Item = tuple[int, str]


@dataclass(frozen=True)
class ModeDefinition:
    key: str
    selector_label: str
    picker_title: str
    picker_hint: str
    instructions: str
    send_label: str
    attempt_label: str
    items: tuple[Item, ...]
    hexadecimal_ids: bool = False

    def list_id(self, item_id: int) -> str:
        return f"{item_id:02X}" if self.hexadecimal_ids else f"{item_id:03d}"

    def selected_id(self, item_id: int) -> str:
        return f"0x{item_id:02X}" if self.hexadecimal_ids else str(item_id)


CONNECTION_MODE = ModeDefinition(
    key="connection",
    selector_label="Connection 2024 · IR",
    picker_title="Choose a gift",
    picker_hint="181 items supported by the Connection 2024 protocol",
    instructions=(
        "Click Wait and send gift first. On the Tamagotchi, choose "
        "Connection → Present, start the connection, and align the IR ports."
    ),
    send_label="Wait and send gift",
    attempt_label="Connection gift",
    items=GIFT_ITEMS,
)

FRIENDS_MODE = ModeDefinition(
    key="friends",
    selector_label="Friends · LF RFID",
    picker_title="Choose a BFF reward",
    picker_hint="60 jewelry outcomes and five Gotchi Point bonuses",
    instructions=(
        "On Tamagotchi Friends, open BFF BUMP and start a bump. Hold its back "
        "directly against the Flipper's LF RFID antenna, then click Send BFF reward."
    ),
    send_label="Send BFF reward",
    attempt_label="Friends BFF",
    items=FRIENDS_REWARDS,
    hexadecimal_ids=True,
)

LEGACY_MODE = ModeDefinition(
    key="legacy",
    selector_label="Original V2/V3 · IR",
    picker_title="Compatibility fallback",
    picker_hint="Automatic random game or gift through the Flipper app",
    instructions=(
        "Click Start fallback first. On V2 choose Version 1, or on V3 choose "
        "Others, start the connection, and align the IR ports."
    ),
    send_label="Start fallback",
    attempt_label="Original fallback",
    items=((0, "Automatic game or gift"),),
)

MODES = {mode.key: mode for mode in (CONNECTION_MODE, FRIENDS_MODE, LEGACY_MODE)}


def get_mode(key: str) -> ModeDefinition:
    return MODES.get(key, CONNECTION_MODE)
