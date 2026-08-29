"""Background transfer orchestration with an explicit state machine."""

from __future__ import annotations

from dataclasses import dataclass
import queue
import threading

from flipper_serial import CancelledError, FlipperConnection, SerialDisconnectedError
from tamagometer_core import GIFT_RESPONSE_2, make_gift_response_for_request
from transfer_status import TransferState, TransferUpdate

from .modes import ModeDefinition


TERMINAL_STATES = frozenset({
    TransferState.COMPLETED,
    TransferState.CANCELLED,
    TransferState.FAILED,
    TransferState.DISCONNECTED,
})

ALLOWED_TRANSITIONS = {
    TransferState.IDLE: {TransferState.PREPARING},
    TransferState.PREPARING: {
        TransferState.WAITING_FIRST_MESSAGE,
        TransferState.BROADCASTING,
    },
    TransferState.WAITING_FIRST_MESSAGE: {TransferState.SENDING_ACKNOWLEDGEMENT},
    TransferState.SENDING_ACKNOWLEDGEMENT: {TransferState.WAITING_GIFT_REQUEST},
    TransferState.WAITING_GIFT_REQUEST: {
        TransferState.SENDING_GIFT,
        TransferState.SENDING_RESULT,
    },
    TransferState.SENDING_GIFT: {TransferState.COMPLETED},
    TransferState.SENDING_RESULT: {TransferState.COMPLETED},
    TransferState.BROADCASTING: {TransferState.BROADCASTING, TransferState.VERIFYING},
    TransferState.VERIFYING: {TransferState.COMPLETED},
}


@dataclass(frozen=True)
class AppEvent:
    kind: str
    text: str
    state: TransferState | None = None
    current: int | None = None
    total: int | None = None


class TransferController:
    def __init__(self, connection: FlipperConnection, events: queue.Queue[AppEvent]):
        self.connection = connection
        self.events = events
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.state = TransferState.IDLE
        self._state_lock = threading.Lock()

    @property
    def active(self) -> bool:
        return bool(self.worker and self.worker.is_alive())

    def start(self, mode: ModeDefinition, item_id: int, item_name: str) -> None:
        if self.active:
            raise RuntimeError("A transfer is already running")
        self.cancel_event.clear()
        with self._state_lock:
            self.state = TransferState.IDLE
        self._transition(TransferUpdate(TransferState.PREPARING, f"Preparing · {item_name}"))
        self.worker = threading.Thread(
            target=self._run,
            args=(mode, item_id, item_name),
            daemon=True,
        )
        self.worker.start()

    def cancel(self) -> None:
        self.cancel_event.set()
        if self.active:
            self._terminal_or_cancel(TransferState.CANCELLING, "Cancelling…", "state")

    def _terminal_or_cancel(self, state: TransferState, text: str, kind: str) -> None:
        with self._state_lock:
            self.state = state
        self.events.put(AppEvent(kind, text, state))

    def _transition(self, update: TransferUpdate) -> bool:
        with self._state_lock:
            if self.state == TransferState.CANCELLING:
                return False
            allowed = ALLOWED_TRANSITIONS.get(self.state, set())
            if update.state not in allowed:
                raise RuntimeError(
                    f"Invalid transfer state transition: {self.state.value} -> {update.state.value}",
                )
            self.state = update.state
        self.events.put(AppEvent(
            "state", update.text, update.state, update.current, update.total,
        ))
        return True

    def _run(self, mode: ModeDefinition, item_id: int, item_name: str) -> None:
        try:
            if mode.key == "friends":
                self.connection.send_friends_reward(item_id, self.cancel_event, self._transition)
            elif mode.key == "legacy":
                self.connection.run_legacy_fallback(self.cancel_event, self._transition)
            else:
                self.connection.deliver_gift(
                    GIFT_RESPONSE_2,
                    lambda request: make_gift_response_for_request(item_id, request),
                    self.cancel_event,
                    self._transition,
                )
        except CancelledError:
            self._terminal_or_cancel(TransferState.CANCELLED, "Transfer cancelled", "cancelled")
        except SerialDisconnectedError as error:
            self._terminal_or_cancel(TransferState.DISCONNECTED, str(error), "disconnected")
        except Exception as error:
            self._terminal_or_cancel(TransferState.FAILED, str(error), "error")
        else:
            try:
                completed = self._transition(
                    TransferUpdate(TransferState.COMPLETED, f"{item_name} sent"),
                )
            except RuntimeError as error:
                self._terminal_or_cancel(TransferState.FAILED, str(error), "error")
            else:
                if not completed:
                    self._terminal_or_cancel(
                        TransferState.CANCELLED, "Transfer cancelled", "cancelled",
                    )
                    return
                self.events.put(AppEvent("done", f"{item_name} sent", TransferState.COMPLETED))
