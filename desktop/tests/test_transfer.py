import queue
import threading
import unittest

from flipper_serial import CancelledError, SerialDisconnectedError
from tamagometer_desktop.modes import CONNECTION_MODE, FRIENDS_MODE, LEGACY_MODE
from tamagometer_desktop.transfer import TransferController
from transfer_status import TransferState, TransferUpdate


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.failure = None

    def deliver_gift(self, response2, response4, cancel, status):
        self.calls.append(("connection", response2, callable(response4)))
        status(TransferUpdate(TransferState.WAITING_FIRST_MESSAGE, "Waiting"))
        status(TransferUpdate(TransferState.SENDING_ACKNOWLEDGEMENT, "Acknowledging"))
        status(TransferUpdate(TransferState.WAITING_GIFT_REQUEST, "Waiting request"))
        status(TransferUpdate(TransferState.SENDING_GIFT, "Sending"))
        if self.failure:
            raise self.failure

    def send_friends_reward(self, item_id, cancel, status):
        self.calls.append(("friends", item_id))
        status(TransferUpdate(TransferState.BROADCASTING, "Broadcasting", 0, 10))
        if self.failure:
            raise self.failure
        status(TransferUpdate(TransferState.BROADCASTING, "Broadcasting", 10, 10))
        status(TransferUpdate(TransferState.VERIFYING, "Verified"))

    def run_legacy_fallback(self, cancel, status):
        self.calls.append(("legacy",))
        status(TransferUpdate(TransferState.WAITING_FIRST_MESSAGE, "Waiting"))
        status(TransferUpdate(TransferState.SENDING_ACKNOWLEDGEMENT, "Acknowledging"))
        status(TransferUpdate(TransferState.WAITING_GIFT_REQUEST, "Waiting request"))
        status(TransferUpdate(TransferState.SENDING_RESULT, "Sending result"))
        if self.failure:
            raise self.failure
        return "Balloon game", "v2"


class TransferControllerTests(unittest.TestCase):
    def _run(self, mode, item_id, item_name, failure=None):
        events = queue.Queue()
        connection = FakeConnection()
        connection.failure = failure
        controller = TransferController(connection, events)
        controller.start(mode, item_id, item_name)
        controller.worker.join(timeout=1)
        self.assertFalse(controller.active)
        collected = []
        while not events.empty():
            collected.append(events.get_nowait())
        return connection.calls, collected, controller

    def test_connection_follows_explicit_state_machine(self):
        calls, events, controller = self._run(CONNECTION_MODE, 4, "Cereal")
        self.assertEqual(calls[0][0], "connection")
        states = [event.state for event in events if event.kind == "state"]
        self.assertEqual(states, [
            TransferState.PREPARING,
            TransferState.WAITING_FIRST_MESSAGE,
            TransferState.SENDING_ACKNOWLEDGEMENT,
            TransferState.WAITING_GIFT_REQUEST,
            TransferState.SENDING_GIFT,
            TransferState.COMPLETED,
        ])
        self.assertEqual(events[-1].kind, "done")
        self.assertEqual(controller.state, TransferState.COMPLETED)

    def test_friends_progress_reaches_completion(self):
        calls, events, controller = self._run(FRIENDS_MODE, 255, "1,000 Gotchi Points")
        self.assertEqual(calls, [("friends", 255)])
        progress = [(event.current, event.total) for event in events if event.current is not None]
        self.assertEqual(progress, [(0, 10), (10, 10)])
        self.assertEqual(controller.state, TransferState.COMPLETED)

    def test_legacy_fallback_uses_companion_command(self):
        calls, events, controller = self._run(
            LEGACY_MODE, 0, "Automatic game or gift",
        )
        self.assertEqual(calls, [("legacy",)])
        states = [event.state for event in events if event.kind == "state"]
        self.assertEqual(states, [
            TransferState.PREPARING,
            TransferState.WAITING_FIRST_MESSAGE,
            TransferState.SENDING_ACKNOWLEDGEMENT,
            TransferState.WAITING_GIFT_REQUEST,
            TransferState.SENDING_RESULT,
            TransferState.COMPLETED,
        ])
        self.assertEqual(controller.state, TransferState.COMPLETED)

    def test_reports_cancellation(self):
        _calls, events, controller = self._run(
            FRIENDS_MODE, 255, "Reward", CancelledError(),
        )
        self.assertEqual(events[-1].kind, "cancelled")
        self.assertEqual(controller.state, TransferState.CANCELLED)

    def test_reports_disconnect_separately_from_protocol_failure(self):
        _calls, events, controller = self._run(
            FRIENDS_MODE, 255, "Reward", SerialDisconnectedError("Flipper disconnected"),
        )
        self.assertEqual(events[-1].kind, "disconnected")
        self.assertEqual(controller.state, TransferState.DISCONNECTED)

    def test_late_worker_completion_cannot_override_cancellation(self):
        class ReturningAfterCancel(FakeConnection):
            def __init__(self):
                super().__init__()
                self.entered = threading.Event()
                self.release = threading.Event()

            def send_friends_reward(self, item_id, cancel, status):
                status(TransferUpdate(TransferState.BROADCASTING, "Broadcasting", 0, 10))
                self.entered.set()
                self.release.wait(timeout=1)

        events = queue.Queue()
        connection = ReturningAfterCancel()
        controller = TransferController(connection, events)
        controller.start(FRIENDS_MODE, 1, "Reward")
        self.assertTrue(connection.entered.wait(timeout=1))
        controller.cancel()
        connection.release.set()
        controller.worker.join(timeout=1)
        collected = []
        while not events.empty():
            collected.append(events.get_nowait())
        self.assertNotIn("done", [event.kind for event in collected])
        self.assertEqual(collected[-1].kind, "cancelled")
        self.assertEqual(controller.state, TransferState.CANCELLED)


if __name__ == "__main__":
    unittest.main()
