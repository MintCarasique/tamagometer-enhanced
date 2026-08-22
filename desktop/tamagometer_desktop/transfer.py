"""Background transfer orchestration, independent of Tk widgets."""

from __future__ import annotations

from dataclasses import dataclass
import queue
import threading

from flipper_serial import CancelledError, FlipperConnection
from tamagometer_core import GIFT_RESPONSE_2, make_gift_response_for_request

from .modes import ModeDefinition


@dataclass(frozen=True)
class AppEvent:
    kind: str
    text: str


class TransferController:
    def __init__(self, connection: FlipperConnection, events: queue.Queue[AppEvent]):
        self.connection = connection
        self.events = events
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None

    @property
    def active(self) -> bool:
        return bool(self.worker and self.worker.is_alive())

    def start(self, mode: ModeDefinition, item_id: int, item_name: str) -> None:
        if self.active:
            raise RuntimeError("A transfer is already running")
        self.cancel_event.clear()
        self.worker = threading.Thread(
            target=self._run,
            args=(mode, item_id, item_name),
            daemon=True,
        )
        self.worker.start()

    def cancel(self) -> None:
        self.cancel_event.set()

    def _status(self, text: str) -> None:
        self.events.put(AppEvent("status", text))

    def _run(self, mode: ModeDefinition, item_id: int, item_name: str) -> None:
        try:
            if mode.key == "friends":
                self.connection.send_friends_reward(item_id, self.cancel_event, self._status)
            else:
                self.connection.deliver_gift(
                    GIFT_RESPONSE_2,
                    lambda request: make_gift_response_for_request(item_id, request),
                    self.cancel_event,
                    self._status,
                )
        except CancelledError:
            self.events.put(AppEvent("cancelled", "Transfer cancelled"))
        except Exception as error:
            self.events.put(AppEvent("error", str(error)))
        else:
            self.events.put(AppEvent("done", f"{item_name} sent"))
