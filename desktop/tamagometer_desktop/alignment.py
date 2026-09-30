"""Animated placement guide for Connection IR and Friends LF transfers."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from transfer_status import TransferState
from .device_art import draw_flipper, draw_tamagotchi


class AlignmentGuide(ttk.Frame):
    def __init__(self, parent, palette: dict[str, str]):
        super().__init__(parent, style="Card.TFrame")
        self.palette = palette
        self.mode = "connection"
        self.state = TransferState.IDLE
        self.phase = 0
        self.canvas = tk.Canvas(
            self, height=118, highlightthickness=0, background=palette["card"],
        )
        self.canvas.pack(fill="x")
        self.caption = tk.StringVar()
        ttk.Label(
            self, textvariable=self.caption, style="Muted.TLabel",
            wraplength=300, justify="center",
        ).pack(fill="x", pady=(2, 0))
        self.after(90, self._animate)

    def set_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette
        self.canvas.configure(background=palette["card"])

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.phase = 0
        self._draw()

    def set_state(self, state: TransferState | None) -> None:
        if state:
            self.state = state
        self._draw()

    def _animate(self) -> None:
        if self.winfo_exists():
            self.phase = (self.phase + 1) % 24
            self._draw()
            self.after(90, self._animate)

    def _draw(self) -> None:
        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 300)
        accent = self.palette["accent"]
        active = self.state not in {
            TransferState.IDLE,
            TransferState.COMPLETED,
            TransferState.CANCELLED,
            TransferState.FAILED,
            TransferState.DISCONNECTED,
        }
        pulse = (self.phase % 12) / 12

        if self.mode == "friends":
            cx = width / 2
            draw_flipper(canvas, cx - 56, 35, back=True)
            lift = 5 + (3 if active else 0) * pulse
            draw_tamagotchi(canvas, cx - 32, lift, self.palette, back=True)
            self.caption.set("Place the back of Tamagotchi flat against the Flipper LF antenna and keep it still.")
        else:
            cy = 58
            draw_tamagotchi(canvas, 20, 25, self.palette, sideways=True)
            draw_flipper(canvas, width - 132, 25)
            for index in range(3):
                offset = index * 13 + (pulse * 8 if active else 0)
                canvas.create_arc(84 + offset, cy - 16, 104 + offset, cy + 16,
                                  start=285, extent=150, style="arc", outline=accent, width=2)
            if self.mode == "legacy":
                self.caption.set(
                    "Point the original Tamagotchi IR window at the Flipper and keep both devices still."
                )
            else:
                self.caption.set("Point the Tamagotchi IR window directly at the Flipper infrared port.")
