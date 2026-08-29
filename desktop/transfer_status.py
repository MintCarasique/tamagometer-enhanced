"""Structured transfer states shared by the serial transport and UI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TransferState(str, Enum):
    IDLE = "idle"
    PREPARING = "preparing"
    WAITING_FIRST_MESSAGE = "waiting_first_message"
    SENDING_ACKNOWLEDGEMENT = "sending_acknowledgement"
    WAITING_GIFT_REQUEST = "waiting_gift_request"
    SENDING_GIFT = "sending_gift"
    SENDING_RESULT = "sending_result"
    BROADCASTING = "broadcasting"
    VERIFYING = "verifying"
    CANCELLING = "cancelling"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    DISCONNECTED = "disconnected"


@dataclass(frozen=True)
class TransferUpdate:
    state: TransferState
    text: str
    current: int | None = None
    total: int | None = None
