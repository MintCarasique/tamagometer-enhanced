"""Serial bridge for Tamagometer Enhanced Companion on Flipper Zero."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import re
import threading
import time

from transfer_status import TransferState, TransferUpdate


BAUD_RATE = 460_800
MIN_COMPANION_VERSION = (2, 0, 0)
REQUIRED_CAPABILITIES = frozenset({
    "connection_ir",
    "connection_legacy",
    "friends_lf",
    "friends_progress",
})
COMMAND_RE = re.compile(rb"\[PICO\]([01]{160})\[END\]")
INFO_RE = re.compile(
    rb"\[TAMAGOMETER\]version=([^;\]]+);protocol=(\d+);capabilities=([a-z0-9_,.-]+)\[END\]",
)
FRIENDS_PROGRESS_RE = re.compile(rb"\[TAMAFRIENDS\]progress=(\d+)/(\d+)\[END\]")
LEGACY_PROGRESS_RE = re.compile(rb"\[TAMALEGACY\]progress=(\d+)/(\d+)\[END\]")
LEGACY_RESULT_RE = re.compile(
    rb"\[TAMALEGACY\]result=([^;\]]+);activity=([^;\]]+);peer=([^;\]]+)\[END\]",
)
TIMEOUT_TOKEN = b"[PICO]timed out[END]"
FRIENDS_OK_TOKEN = b"[TAMAFRIENDS]ok[END]"
FRIENDS_CANCELLED_TOKEN = b"[TAMAFRIENDS]cancelled[END]"


@dataclass(frozen=True)
class SerialPortInfo:
    device: str
    description: str
    vid: int | None = None
    pid: int | None = None
    manufacturer: str = ""
    hwid: str = ""

    @property
    def display_name(self) -> str:
        return f"{self.device} — {self.description or self.device}"


@dataclass(frozen=True)
class CompanionInfo:
    version: str
    protocol: int
    capabilities: frozenset[str]


class CancelledError(Exception):
    pass


class SerialDisconnectedError(RuntimeError):
    pass


class IncompatibleCompanionError(RuntimeError):
    pass


def list_ports() -> list[SerialPortInfo]:
    try:
        from serial.tools import list_ports as serial_list_ports
    except ImportError:
        return []
    return [
        SerialPortInfo(
            device=port.device,
            description=port.description or port.device,
            vid=port.vid,
            pid=port.pid,
            manufacturer=port.manufacturer or "",
            hwid=port.hwid or "",
        )
        for port in serial_list_ports.comports()
    ]


def find_flipper_port(
    ports: Iterable[SerialPortInfo], preferred: str = "",
) -> SerialPortInfo | None:
    """Select a remembered or likely Flipper USB serial port."""
    candidates = list(ports)
    for port in candidates:
        if preferred and port.device.casefold() == preferred.casefold():
            return port

    def score(port: SerialPortInfo) -> int:
        identity = " ".join((port.description, port.manufacturer, port.hwid)).casefold()
        value = 100 if "flipper" in identity else 0
        if port.vid == 0x0483 and port.pid == 0x5740:
            value += 40
        return value

    ranked = sorted(candidates, key=score, reverse=True)
    if ranked and score(ranked[0]) > 0:
        return ranked[0]
    return candidates[0] if len(candidates) == 1 else None


def _version_tuple(version: str) -> tuple[int, int, int]:
    match = re.match(r"^(\d+)\.(\d+)(?:\.(\d+))?", version)
    if not match:
        return (0, 0, 0)
    return tuple(int(part or 0) for part in match.groups())  # type: ignore[return-value]


class FlipperConnection:
    def __init__(self, serial_port=None, trace: Callable[[str], None] | None = None):
        self.serial = serial_port
        self._buffer = bytearray()
        self.trace = trace or (lambda _message: None)
        self.port = getattr(serial_port, "port", "") if serial_port else ""
        self.companion: CompanionInfo | None = None

    @property
    def connected(self) -> bool:
        try:
            return bool(self.serial and getattr(self.serial, "is_open", True))
        except Exception:
            return False

    def open(self, port: str, verify: bool = True) -> CompanionInfo | None:
        if self.connected:
            self.close()
        try:
            import serial
        except ImportError as error:
            raise RuntimeError("The pyserial module is not installed") from error
        try:
            self.serial = serial.Serial(
                port=port, baudrate=BAUD_RATE, timeout=0.08, write_timeout=2,
            )
            self.port = port
            self._buffer.clear()
            if verify:
                self.companion = self.get_info()
            return self.companion
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        serial_port, self.serial = self.serial, None
        if serial_port:
            try:
                serial_port.close()
            except Exception:
                pass
        self._buffer.clear()
        self.companion = None

    def _disconnect(self, error: Exception) -> SerialDisconnectedError:
        port = self.port
        self.close()
        return SerialDisconnectedError(f"Flipper disconnected from {port or 'the COM port'}")

    def _write(self, data: bytes) -> None:
        if not self.connected:
            raise SerialDisconnectedError("Flipper is not connected")
        try:
            self.serial.write(data)
            self.serial.flush()
        except Exception as error:
            raise self._disconnect(error) from error

    def _write_line(self, text: str) -> None:
        self._write((text + "\r\n").encode("ascii"))

    def _read_chunk(self) -> bytes:
        if not self.connected:
            raise SerialDisconnectedError("Flipper is not connected")
        try:
            waiting = getattr(self.serial, "in_waiting", 0)
            return self.serial.read(max(1, waiting))
        except Exception as error:
            raise self._disconnect(error) from error

    def _clear_input(self) -> None:
        self._buffer.clear()
        reset = getattr(self.serial, "reset_input_buffer", None)
        if reset:
            try:
                reset()
            except Exception as error:
                raise self._disconnect(error) from error

    def get_info(self, timeout: float = 1.8) -> CompanionInfo:
        """Perform the versioned Companion capability handshake."""
        self._clear_input()
        self._write_line("tamagometer info")
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            chunk = self._read_chunk()
            if chunk:
                self._buffer.extend(chunk)
                match = INFO_RE.search(self._buffer)
                if match:
                    info = CompanionInfo(
                        version=match.group(1).decode("ascii"),
                        protocol=int(match.group(2)),
                        capabilities=frozenset(match.group(3).decode("ascii").split(",")),
                    )
                    self._buffer.clear()
                    missing = REQUIRED_CAPABILITIES - info.capabilities
                    if info.protocol != 1 or _version_tuple(info.version) < MIN_COMPANION_VERSION or missing:
                        if missing:
                            details = f"missing: {', '.join(sorted(missing))}"
                        elif info.protocol != 1:
                            details = f"unsupported protocol {info.protocol}"
                        else:
                            details = "version 2.0.0 or newer is required"
                        raise IncompatibleCompanionError(
                            f"Companion {info.version} is incompatible ({details}). "
                            "Install and open Tamagometer Enhanced Companion 2.0.0 or newer."
                        )
                    self.companion = info
                    return info
                text = self._buffer.decode("utf-8", errors="replace").casefold()
                if "invalid argument" in text or "command not found" in text:
                    break
                if len(self._buffer) > 4096:
                    del self._buffer[:-1024]
        self._buffer.clear()
        raise IncompatibleCompanionError(
            "The open Flipper app does not support the required capability handshake. "
            "Install and open Tamagometer Enhanced Companion 2.0.0 or newer."
        )

    def send_message(self, bits: str) -> None:
        self._write_line("tamagometer send" + bits)

    def _read_ir_once(self, cancel: threading.Event, deadline: float) -> str | None:
        self._write_line("tamagometer listen")
        while time.monotonic() < deadline:
            if cancel.is_set():
                raise CancelledError
            chunk = self._read_chunk()
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
        status: Callable[[TransferUpdate], None] = lambda _update: None,
    ) -> None:
        status(TransferUpdate(TransferState.WAITING_FIRST_MESSAGE, "Waiting for the first message from Tamagotchi…"))
        first = self.wait_for_message(cancel)
        if first is None:
            raise RuntimeError("The first message was not received")
        status(TransferUpdate(TransferState.SENDING_ACKNOWLEDGEMENT, "Connection established — sending acknowledgement…"))
        self.trace("RX1 OK; sending TX2: " + response2)
        self.send_message(response2)
        status(TransferUpdate(TransferState.WAITING_GIFT_REQUEST, "Waiting for the gift request…"))
        third = self.wait_for_message(cancel, attempts=3)
        if third is None:
            raise RuntimeError("Tamagotchi did not send the second part of the exchange")
        status(TransferUpdate(TransferState.SENDING_GIFT, "Sending the gift…"))
        if callable(response4):
            response4 = response4(third)
        self.trace("RX3 OK; sending TX4: " + response4)
        self.send_message(response4)
        self.send_message(response4)
        self.trace("TX4 sent twice; exchange complete")

    def send_friends_reward(
        self,
        outcome: int,
        cancel: threading.Event,
        status: Callable[[TransferUpdate], None] = lambda _update: None,
        timeout: float = 20.0,
    ) -> None:
        if not 0 <= outcome <= 0xFF:
            raise ValueError("Friends outcome must be between 0 and 255")
        self._clear_input()
        status(TransferUpdate(TransferState.BROADCASTING, "Broadcasting Friends BFF response · 0/10", 0, 10))
        self.trace(f"Sending LF RFID BFF outcome 0x{outcome:02X}")
        self._write_line(f"tamagometer friends{outcome}")
        deadline = time.monotonic() + timeout
        reported = 0
        while time.monotonic() < deadline:
            if cancel.is_set():
                self._write(b"\x03")
                cancel_deadline = time.monotonic() + 2.0
                while time.monotonic() < cancel_deadline:
                    chunk = self._read_chunk()
                    if chunk:
                        self._buffer.extend(chunk)
                        if FRIENDS_CANCELLED_TOKEN in self._buffer:
                            break
                self._buffer.clear()
                raise CancelledError
            chunk = self._read_chunk()
            if not chunk:
                continue
            self._buffer.extend(chunk)
            for match in FRIENDS_PROGRESS_RE.finditer(self._buffer):
                current, total = int(match.group(1)), int(match.group(2))
                if current > reported:
                    reported = current
                    status(TransferUpdate(
                        TransferState.BROADCASTING,
                        f"Broadcasting Friends BFF response · {current}/{total}",
                        current,
                        total,
                    ))
            if FRIENDS_OK_TOKEN in self._buffer:
                self.trace("LF RFID broadcast complete")
                status(TransferUpdate(TransferState.VERIFYING, "Flipper confirmed the BFF transmission"))
                self._buffer.clear()
                return
            if FRIENDS_CANCELLED_TOKEN in self._buffer:
                self._buffer.clear()
                raise CancelledError
            response = self._buffer.decode("utf-8", errors="replace")
            if "Invalid argument" in response or "command not found" in response.casefold():
                self._buffer.clear()
                raise IncompatibleCompanionError(
                    "This Flipper app does not support Tamagotchi Friends. "
                    "Install and open Tamagometer Enhanced Companion 2.0.0 or newer."
                )
            if len(self._buffer) > 4096:
                del self._buffer[:-1024]
        self._buffer.clear()
        raise RuntimeError(
            "The Flipper did not confirm the Friends transmission. "
            "Keep the enhanced Companion open and try again."
        )

    def run_legacy_fallback(
        self,
        cancel: threading.Event,
        status: Callable[[TransferUpdate], None] = lambda _update: None,
        timeout: float = 90.0,
    ) -> tuple[str, str]:
        """Run one original V2/V3 compatibility exchange on the Flipper."""
        self._clear_input()
        self.trace("Starting original V2/V3 compatibility fallback")
        self._write_line("tamagometer legacy")
        deadline = time.monotonic() + timeout
        highest_progress = -1
        progress_states = {
            5: (TransferState.WAITING_FIRST_MESSAGE, "Waiting for original Tamagotchi…"),
            35: (TransferState.SENDING_ACKNOWLEDGEMENT, "Sending legacy identity…"),
            55: (TransferState.WAITING_GIFT_REQUEST, "Waiting for random activity request…"),
            85: (TransferState.SENDING_RESULT, "Sending game or gift result…"),
        }
        while time.monotonic() < deadline:
            if cancel.is_set():
                self._write(b"\x03")
                self._buffer.clear()
                raise CancelledError
            chunk = self._read_chunk()
            if not chunk:
                continue
            self._buffer.extend(chunk)
            for match in LEGACY_PROGRESS_RE.finditer(self._buffer):
                current, total = int(match.group(1)), int(match.group(2))
                if current <= highest_progress or current not in progress_states:
                    continue
                highest_progress = current
                state, text = progress_states[current]
                status(TransferUpdate(state, text, current, total))
            result_match = LEGACY_RESULT_RE.search(self._buffer)
            if result_match:
                result, activity, peer = (
                    group.decode("ascii") for group in result_match.groups()
                )
                self._buffer.clear()
                self.trace(f"Legacy result: {result}; activity={activity}; peer={peer}")
                if result != "Transfer complete":
                    if result == "Transfer cancelled":
                        raise CancelledError
                    raise RuntimeError(result)
                return activity, peer
            response = self._buffer.decode("utf-8", errors="replace")
            if "Invalid argument" in response or "command not found" in response.casefold():
                self._buffer.clear()
                raise IncompatibleCompanionError(
                    "This Flipper app does not support original V2/V3 fallback. "
                    "Install the matching Tamagometer Enhanced Companion."
                )
            if len(self._buffer) > 8192:
                del self._buffer[:-2048]
        self._write(b"\x03")
        self._buffer.clear()
        raise RuntimeError("The original Tamagotchi exchange timed out")
