"""First-run setup window for Companion installation and automatic connection."""

from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk


class OnboardingWindow(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Tk,
        connect: Callable[[], bool],
        finish: Callable[[], None],
    ):
        super().__init__(parent)
        self.connect_callback = connect
        self.finish_callback = finish
        self.step = 0
        self.title("Set up Tamagometer")
        self.geometry("560x430")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._finish)

        shell = ttk.Frame(self, style="App.TFrame", padding=28)
        shell.pack(fill="both", expand=True)
        self.eyebrow = ttk.Label(shell, text="FIRST-RUN SETUP · 1 OF 3")
        self.eyebrow.pack(anchor="w")
        self.title_var = tk.StringVar()
        ttk.Label(shell, textvariable=self.title_var, font=("Segoe UI Semibold", 20)).pack(
            anchor="w", pady=(10, 6),
        )
        self.body_var = tk.StringVar()
        ttk.Label(
            shell, textvariable=self.body_var, wraplength=490, justify="left",
        ).pack(anchor="w", fill="x")
        self.state_var = tk.StringVar()
        ttk.Label(
            shell, textvariable=self.state_var, style="Status.TLabel",
            wraplength=480, justify="left",
        ).pack(anchor="w", fill="x", pady=(24, 0))

        controls = ttk.Frame(shell, style="App.TFrame")
        controls.pack(side="bottom", fill="x")
        ttk.Button(controls, text="Skip setup", command=self._finish).pack(side="left")
        self.back_button = ttk.Button(controls, text="Back", command=self._back)
        self.back_button.pack(side="right", padx=(7, 0))
        self.next_button = ttk.Button(
            controls, text="Continue", style="Primary.TButton", command=self._next,
        )
        self.next_button.pack(side="right")
        self._render()

    def _render(self) -> None:
        pages = (
            (
                "Welcome to Tamagometer Enhanced",
                "This short setup checks that Desktop can find your Flipper Zero and the matching Enhanced Companion. No account or personal information is required.",
                "Have a USB data cable and your Flipper ready.",
            ),
            (
                "Install and open the Companion",
                "Copy TamagometerEnhanced.fap to SD Card/apps/Tools, close qFlipper, then open Apps → Tools → Tamagometer Enhanced on the Flipper.",
                "Leave the Companion open and connect Flipper by USB.",
            ),
            (
                "Connect automatically",
                "Desktop will select a likely Flipper COM port, verify Companion compatibility, and remember it for automatic reconnection.",
                "Click Find Flipper when the device is ready.",
            ),
        )
        title, body, state = pages[self.step]
        self.eyebrow.configure(text=f"FIRST-RUN SETUP · {self.step + 1} OF 3")
        self.title_var.set(title)
        self.body_var.set(body)
        self.state_var.set(state)
        self.back_button.configure(state="normal" if self.step else "disabled")
        self.next_button.configure(text="Find Flipper" if self.step == 2 else "Continue")

    def _back(self) -> None:
        if self.step:
            self.step -= 1
            self._render()

    def _next(self) -> None:
        if self.step < 2:
            self.step += 1
            self._render()
            return
        self.state_var.set("Looking for a compatible Flipper…")
        self.update_idletasks()
        if self.connect_callback():
            self.state_var.set("Connected successfully. Setup is complete.")
            self.back_button.configure(state="disabled")
            self.next_button.configure(text="Start using Tamagometer", command=self._finish)
        else:
            self.state_var.set(
                "Flipper was not ready. Check the USB cable, close qFlipper, open the Enhanced Companion, and try again.",
            )

    def _finish(self) -> None:
        self.finish_callback()
        self.destroy()
