import threading
import unittest

from flipper_serial import (
    FRIENDS_CANCELLED_TOKEN,
    FRIENDS_OK_TOKEN,
    LEGACY_RESULT_RE,
    TIMEOUT_TOKEN,
    CancelledError,
    FlipperConnection,
    IncompatibleCompanionError,
    SerialDisconnectedError,
    SerialPortInfo,
    find_flipper_port,
)
from tamagometer_core import GIFT_RESPONSE_2, make_gift_response
from transfer_status import TransferState


INCOMING = "00001110" + "00000110" + "0" * 144
INFO = (
    b"[TAMAGOMETER]version=2.0.0;protocol=1;"
    b"capabilities=connection_ir,connection_legacy,friends_lf,friends_progress[END]"
)


class FakeSerial:
    is_open = True

    def __init__(self, chunk_size=4096):
        self.output = []
        self.input = bytearray()
        self.listen_count = 0
        self.chunk_size = chunk_size
        self.disconnect_on_read = False

    @property
    def in_waiting(self):
        return len(self.input)

    def write(self, data):
        if data == b"\x03":
            self.output.append("<ETX>")
            self.input.extend(FRIENDS_CANCELLED_TOKEN)
            return len(data)
        line = data.decode("ascii").strip()
        self.output.append(line)
        if line == "tamagometer info":
            self.input.extend(b"cli noise\r\n" + INFO + b"\r\n>: ")
        elif line == "tamagometer listen":
            self.listen_count += 1
            self.input.extend(f"noise[PICO]{INCOMING}[END]prompt>".encode("ascii"))
        elif line.startswith("tamagometer friends"):
            for repeat in range(1, 11):
                self.input.extend(f"[TAMAFRIENDS]progress={repeat}/10[END]".encode("ascii"))
            self.input.extend(FRIENDS_OK_TOKEN)
        elif line == "tamagometer legacy":
            for progress in (5, 35, 55, 85, 100):
                self.input.extend(
                    f"[TAMALEGACY]progress={progress}/100[END]".encode("ascii")
                )
            self.input.extend(
                b"[TAMALEGACY]result=Transfer complete;"
                b"activity=Balloon game;peer=v2[END]"
            )
        return len(data)

    def read(self, size):
        if self.disconnect_on_read:
            raise OSError("USB cable removed")
        size = min(size, self.chunk_size)
        result = bytes(self.input[:size])
        del self.input[:size]
        return result

    def flush(self):
        pass

    def close(self):
        self.is_open = False


class SerialFlowTests(unittest.TestCase):
    def test_capability_handshake_handles_fragmented_noisy_frames(self):
        fake = FakeSerial(chunk_size=3)
        connection = FlipperConnection(fake)

        info = connection.get_info(timeout=0.2)

        self.assertEqual(info.version, "2.0.0")
        self.assertEqual(info.protocol, 1)
        self.assertIn("friends_progress", info.capabilities)

    def test_old_companion_is_rejected_with_upgrade_message(self):
        class OldSerial(FakeSerial):
            def write(self, data):
                self.output.append(data.decode("ascii").strip())
                self.input.extend(b"Invalid argument(s). Use listen or send<bits>.\r\n")
                return len(data)

        with self.assertRaisesRegex(IncompatibleCompanionError, "2.0"):
            FlipperConnection(OldSerial()).get_info(timeout=0.05)

    def test_gift_exchange_uses_listen_send_listen_send_send(self):
        fake = FakeSerial(chunk_size=7)
        trace = []
        connection = FlipperConnection(fake, trace.append)
        gift = make_gift_response(124)
        states = []

        connection.deliver_gift(
            GIFT_RESPONSE_2, gift, threading.Event(), states.append,
        )

        self.assertEqual(fake.output, [
            "tamagometer listen",
            "tamagometer send" + GIFT_RESPONSE_2,
            "tamagometer listen",
            "tamagometer send" + gift,
            "tamagometer send" + gift,
        ])
        self.assertEqual(states[-1].state, TransferState.SENDING_GIFT)
        self.assertTrue(any(line.startswith("RX1 OK") for line in trace))
        self.assertTrue(any(line.startswith("RX3 OK") for line in trace))

    def test_ir_timeout_retries_before_valid_frame(self):
        class RetrySerial(FakeSerial):
            def write(self, data):
                line = data.decode("ascii").strip()
                self.output.append(line)
                if line == "tamagometer listen":
                    self.listen_count += 1
                    if self.listen_count == 1:
                        self.input.extend(TIMEOUT_TOKEN)
                    else:
                        self.input.extend(f"[PICO]{INCOMING}[END]".encode("ascii"))
                return len(data)

        fake = RetrySerial(chunk_size=2)
        result = FlipperConnection(fake).wait_for_message(threading.Event(), attempts=2)
        self.assertEqual(result, INCOMING)
        self.assertEqual(fake.listen_count, 2)

    def test_disconnect_mid_transfer_is_reported(self):
        fake = FakeSerial()
        fake.disconnect_on_read = True
        connection = FlipperConnection(fake)
        with self.assertRaises(SerialDisconnectedError):
            connection.wait_for_message(threading.Event(), attempts=1)
        self.assertFalse(connection.connected)

    def test_friends_progress_is_reported_for_each_repeat(self):
        fake = FakeSerial(chunk_size=5)
        connection = FlipperConnection(fake)
        updates = []

        connection.send_friends_reward(255, threading.Event(), updates.append)

        progress = [update.current for update in updates if update.current is not None]
        self.assertEqual(fake.output, ["tamagometer friends255"])
        self.assertEqual(progress, list(range(11)))
        self.assertEqual(updates[-1].state, TransferState.VERIFYING)

    def test_friends_cancellation_sends_ctrl_c(self):
        class WaitingSerial(FakeSerial):
            def write(self, data):
                if data == b"\x03":
                    return super().write(data)
                self.output.append(data.decode("ascii").strip())
                return len(data)

        fake = WaitingSerial()
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(CancelledError):
            FlipperConnection(fake).send_friends_reward(1, cancel)
        self.assertEqual(fake.output, ["tamagometer friends1", "<ETX>"])

    def test_legacy_fallback_reports_activity_and_progress(self):
        fake = FakeSerial(chunk_size=5)
        updates = []
        connection = FlipperConnection(fake)

        activity, peer = connection.run_legacy_fallback(
            threading.Event(), updates.append, timeout=0.2,
        )

        self.assertEqual(fake.output, ["tamagometer legacy"])
        self.assertEqual((activity, peer), ("Balloon game", "v2"))
        self.assertEqual(
            [update.state for update in updates],
            [
                TransferState.WAITING_FIRST_MESSAGE,
                TransferState.SENDING_ACKNOWLEDGEMENT,
                TransferState.WAITING_GIFT_REQUEST,
                TransferState.SENDING_RESULT,
            ],
        )
        self.assertIsNotNone(LEGACY_RESULT_RE.search(
            b"[TAMALEGACY]result=Transfer complete;activity=Random gift;peer=v3[END]",
        ))

    def test_friends_confirmation_timeout_is_reported(self):
        class SilentSerial(FakeSerial):
            def write(self, data):
                self.output.append(data.decode("ascii").strip())
                return len(data)

        with self.assertRaisesRegex(RuntimeError, "did not confirm"):
            FlipperConnection(SilentSerial()).send_friends_reward(
                1, threading.Event(), timeout=0.01,
            )

    def test_flipper_port_detection_prefers_remembered_then_identity(self):
        ports = [
            SerialPortInfo("COM3", "Bluetooth"),
            SerialPortInfo("COM6", "Flipper Zero", manufacturer="Flipper Devices Inc."),
        ]
        self.assertEqual(find_flipper_port(ports).device, "COM6")
        self.assertEqual(find_flipper_port(ports, "COM3").device, "COM3")

    def test_unknown_single_port_is_not_silently_selected(self):
        ports = [SerialPortInfo("COM3", "USB Serial Device")]
        self.assertIsNone(find_flipper_port(ports))
        self.assertEqual(find_flipper_port(ports, "COM3").device, "COM3")


if __name__ == "__main__":
    unittest.main()
