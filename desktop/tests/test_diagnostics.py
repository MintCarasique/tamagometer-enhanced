import unittest

from flipper_serial import FlipperConnection, SerialPortInfo
from tamagometer_desktop.diagnostics import build_diagnostic_report
from tamagometer_desktop.settings import AppSettings


class DiagnosticReportTests(unittest.TestCase):
    def test_report_contains_support_data_without_hardware_ids(self):
        report = build_diagnostic_report(
            AppSettings(port="COM6", mode="friends", theme="dark"),
            FlipperConnection(),
            [SerialPortInfo("COM6", "Flipper Zero", hwid="PRIVATE-HARDWARE-ID")],
            "example log",
        )
        self.assertIn("Desktop version:", report)
        self.assertIn("COM6: Flipper Zero", report)
        self.assertIn("example log", report)
        self.assertNotIn("PRIVATE-HARDWARE-ID", report)


if __name__ == "__main__":
    unittest.main()
