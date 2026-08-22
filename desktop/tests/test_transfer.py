import queue
import unittest

from flipper_serial import CancelledError
from tamagometer_desktop.modes import CONNECTION_MODE, FRIENDS_MODE
from tamagometer_desktop.transfer import TransferController


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.cancelled = False

    def deliver_gift(self, response2, response4, cancel, status):
        self.calls.append(("connection", response2, callable(response4)))
        status("Gift sent")
        if self.cancelled:
            raise CancelledError

    def send_friends_reward(self, item_id, cancel, status):
        self.calls.append(("friends", item_id))
        status("BFF reward sent")
        if self.cancelled:
            raise CancelledError


class TransferControllerTests(unittest.TestCase):
    def _run(self, mode, item_id, item_name, cancelled=False):
        events = queue.Queue()
        connection = FakeConnection()
        connection.cancelled = cancelled
        controller = TransferController(connection, events)
        controller.start(mode, item_id, item_name)
        controller.worker.join(timeout=1)
        self.assertFalse(controller.active)
        collected = []
        while not events.empty():
            collected.append(events.get_nowait())
        return connection.calls, collected

    def test_dispatches_connection_transfer(self):
        calls, events = self._run(CONNECTION_MODE, 4, "Cereal")
        self.assertEqual(calls[0][0], "connection")
        self.assertEqual([event.kind for event in events], ["status", "done"])

    def test_dispatches_friends_transfer(self):
        calls, events = self._run(FRIENDS_MODE, 255, "1,000 Gotchi Points")
        self.assertEqual(calls, [("friends", 255)])
        self.assertEqual(events[-1].kind, "done")

    def test_reports_cancellation(self):
        _calls, events = self._run(FRIENDS_MODE, 255, "Reward", cancelled=True)
        self.assertEqual(events[-1].kind, "cancelled")


if __name__ == "__main__":
    unittest.main()
