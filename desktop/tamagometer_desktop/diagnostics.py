"""Create a privacy-conscious, single-file diagnostic report."""

from __future__ import annotations

from datetime import datetime, timezone
import platform

from flipper_serial import FlipperConnection, SerialPortInfo

from . import __version__
from .settings import AppSettings


def build_diagnostic_report(
    settings: AppSettings,
    connection: FlipperConnection,
    ports: list[SerialPortInfo],
    log_text: str,
) -> str:
    companion = connection.companion
    lines = [
        "Tamagometer Enhanced diagnostic report",
        f"Generated (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"Desktop version: {__version__}",
        f"Operating system: {platform.platform()}",
        f"Python: {platform.python_version()}",
        f"Selected mode: {settings.mode}",
        f"Theme: {settings.theme}",
        f"Configured port: {settings.port or '(none)'}",
        f"Connected: {connection.connected}",
        f"Companion version: {companion.version if companion else '(unavailable)'}",
        f"Companion protocol: {companion.protocol if companion else '(unavailable)'}",
        "Detected ports:",
    ]
    lines.extend(
        f"  - {port.device}: {port.description}" for port in ports
    )
    lines.extend(("", "Diagnostics log:", log_text.rstrip() or "(empty)", ""))
    return "\n".join(lines)
