"""Serial bridge for the Tamagometer Companion app on Flipper Zero."""

from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable


BAUD_RATE = 460_800
COMMAND_RE = re.compile(rb"\[PICO\]([01]{160})\[END\]")
TIMEOUT_TOKEN = b"[PICO]timed out[END]"


def list_ports() -> list[tuple[str, str]]:
    try:
        from serial.tools import list_ports as serial_list_ports
    except ImportError:
        return []
    return [(port.device, port.description or port.device)
            for port in serial_list_ports.comports()]


class CancelledError(Exception):
    pass


class FlipperConnection:
    def __init__(self, serial_port=None, trace: Callable[[str], None] | None = None):
        self.serial = serial_port
        self._buffer = bytearray()
        self.trace = trace or (lambda _message: None)

    @property
    def connected(self) -> bool:
        return bool(self.serial and getattr(self.serial, "is_open", True))

    def open(self, port: str) -> None:
        if self.connected:
            self.close()
        try:
            import serial
        except ImportError as error:
            raise RuntimeError("The pyserial module is not installed") from error
        self.serial = serial.Serial(
            port=port, baudrate=BAUD_RATE, timeout=0.08, write_timeout=2,
        )
        self._buffer.clear()

    def close(self) -> None:
        if self.serial:
            try:
                self.serial.close()
            finally:
                self.serial = None
                self._buffer.clear()

    def _write_line(self, text: str) -> None:
        if not self.connected:
            raise RuntimeError("Flipper is not connected")
        self.serial.write((text + "\r\n").encode("ascii"))
        self.serial.flush()

    def send_message(self, bits: str) -> None:
        self._write_line("tamagometer send" + bits)

    def _read_ir_once(self, cancel: threading.Event, deadline: float) -> str | None:
        self._write_line("tamagometer listen")
        while time.monotonic() < deadline:
            if cancel.is_set():
                raise CancelledError
            waiting = getattr(self.serial, "in_waiting", 0)
            chunk = self.serial.read(max(1, waiting))
            if chunk:
                self._buffer.extend(chunk)
                match = COMMAND_RE.search(self._buffer)
                if match:
                    result = match.group(1).decode("ascii")
                    del self._buffer[:match.end()]
                    self.trace("Received IR message: " + result)
                    return result
                timeout_at = self._buffer.find(TIMEOUT_TOKEN)
                if timeout_at >= 0:
                    del self._buffer[:timeout_at + len(TIMEOUT_TOKEN)]
                    self.trace("IR receive timeout (retrying)")
                    return None
                if len(self._buffer) > 4096:
                    del self._buffer[:-512]
        return None

    def wait_for_message(
        self, cancel: threading.Event, attempts: int | None = None,
    ) -> str | None:
        count = 0
        while attempts is None or count < attempts:
            if cancel.is_set():
                raise CancelledError
            result = self._read_ir_once(cancel, time.monotonic() + 2.2)
            if result is not None:
                return result
            count += 1
        return None

    def deliver_gift(
        self,
        response2: str,
        response4: str | Callable[[str], str],
        cancel: threading.Event,
        status: Callable[[str], None] = lambda _message: None,
    ) -> None:
        """Act as the waiting Tamagotchi in the four-message exchange."""
        status("Waiting for the first message from Tamagotchi…")
        first = self.wait_for_message(cancel)
        if first is None:
            raise RuntimeError("The first message was not received")

        status("Connection established — sending acknowledgement…")
        self.trace("RX1 OK; sending TX2: " + response2)
        self.send_message(response2)

        status("Waiting for the gift request…")
        third = self.wait_for_message(cancel, attempts=3)
        if third is None:
            raise RuntimeError("Tamagotchi did not send the second part of the exchange")

        status("Sending the gift…")
        if callable(response4):
            response4 = response4(third)
        self.trace("RX3 OK; sending TX4: " + response4)
        self.send_message(response4)
        self.send_message(response4)
        self.trace("TX4 sent twice; exchange complete")
        status("Gift sent")
