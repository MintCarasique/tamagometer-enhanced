import threading
import unittest

from flipper_serial import FlipperConnection
from tamagometer_core import GIFT_RESPONSE_2, make_gift_response


INCOMING = "00001110" + "00000110" + "0" * 144


class FakeSerial:
    is_open = True

    def __init__(self):
        self.output = []
        self.input = bytearray()
        self.listen_count = 0

    @property
    def in_waiting(self):
        return len(self.input)

    def write(self, data):
        line = data.decode("ascii").strip()
        self.output.append(line)
        if line == "tamagometer listen":
            self.listen_count += 1
            self.input.extend(f"noise[PICO]{INCOMING}[END]prompt>".encode("ascii"))
        return len(data)

    def read(self, size):
        result = bytes(self.input[:size])
        del self.input[:size]
        return result

    def flush(self):
        pass


class SerialFlowTests(unittest.TestCase):
    def test_gift_exchange_uses_listen_send_listen_send_send(self):
        fake = FakeSerial()
        trace = []
        connection = FlipperConnection(fake, trace.append)
        gift = make_gift_response(124)
        statuses = []

        connection.deliver_gift(
            GIFT_RESPONSE_2, gift, threading.Event(), statuses.append,
        )

        self.assertEqual(fake.output, [
            "tamagometer listen",
            "tamagometer send" + GIFT_RESPONSE_2,
            "tamagometer listen",
            "tamagometer send" + gift,
            "tamagometer send" + gift,
        ])
        self.assertEqual(statuses[-1], "Gift sent")
        self.assertTrue(any(line.startswith("RX1 OK") for line in trace))
        self.assertTrue(any(line.startswith("RX3 OK") for line in trace))


if __name__ == "__main__":
    unittest.main()
