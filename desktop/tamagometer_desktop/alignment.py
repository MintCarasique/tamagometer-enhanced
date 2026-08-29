"""Animated placement guide for Connection IR and Friends LF transfers."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from transfer_status import TransferState


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
        ink = self.palette["ink"]
        accent = self.palette["accent"]
        muted = self.palette["muted"]
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
            canvas.create_oval(cx - 67, 19, cx + 67, 105, fill=muted, outline="")
            canvas.create_text(cx, 90, text="Flipper LF", fill=self.palette["card"], font=("Segoe UI Semibold", 9))
            lift = 5 + (3 if active else 0) * pulse
            canvas.create_oval(cx - 43, lift, cx + 43, 68 + lift, fill=self.palette["card"], outline=accent, width=3)
            canvas.create_text(cx, 35 + lift, text="Tamagotchi\nback", fill=ink, justify="center", font=("Segoe UI Semibold", 9))
            self.caption.set("Place the back of Tamagotchi flat against the Flipper LF antenna and keep it still.")
        else:
            cy = 58
            canvas.create_oval(18, 17, 116, 103, fill=self.palette["card"], outline=ink, width=2)
            canvas.create_text(67, 61, text="Flipper", fill=ink, font=("Segoe UI Semibold", 9))
            canvas.create_oval(width - 116, 17, width - 18, 103, fill=self.palette["card"], outline=ink, width=2)
            canvas.create_text(width - 67, 61, text="Tamagotchi", fill=ink, font=("Segoe UI Semibold", 9))
            for index in range(3):
                offset = index * 13 + (pulse * 8 if active else 0)
                canvas.create_arc(116 + offset, cy - 20 - index * 2, 158 + offset, cy + 20 + index * 2, start=285, extent=150, style="arc", outline=accent, width=2)
                canvas.create_arc(width - 158 - offset, cy - 20 - index * 2, width - 116 - offset, cy + 20 + index * 2, start=105, extent=150, style="arc", outline=accent, width=2)
            if self.mode == "legacy":
                self.caption.set(
                    "Point the original Tamagotchi IR window at the Flipper and keep both devices still."
                )
            else:
                self.caption.set("Point the Tamagotchi IR window directly at the Flipper infrared port.")
