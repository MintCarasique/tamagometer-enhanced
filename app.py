"""Modern desktop UI for Tamagotchi Connection and Friends transfers."""

from __future__ import annotations

import json
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from flipper_serial import CancelledError, FlipperConnection, list_ports
from friends_core import FRIENDS_REWARDS
from tamagometer_core import GIFT_ITEMS, GIFT_RESPONSE_2, make_gift_response_for_request


APP_DIR = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
CONFIG_PATH = APP_DIR / ".tamagometer-desktop.json"

BG = "#F3F5FA"
CARD = "#FFFFFF"
INK = "#182230"
MUTED = "#667085"
ACCENT = "#6757D9"
ACCENT_HOVER = "#5748C5"
ACCENT_SOFT = "#EEEAFE"
BORDER = "#E3E7EF"
LOG_BG = "#101828"


class TamagometerDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tamagometer Desktop")
        self.geometry("920x790")
        self.minsize(780, 700)
        self.configure(bg=BG)

        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.connection = FlipperConnection(trace=lambda text: self.events.put(("log", text)))
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.config_data = self._load_config()
        self.visible_items: list[tuple[int, str]] = []

        self._configure_style()
        self._build_ui()
        self.refresh_ports()
        self._change_mode()
        self.after(80, self._poll_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_style(self):
        self.option_add("*Font", ("Segoe UI", 10))
        self.option_add("*selectBackground", ACCENT)
        self.option_add("*selectForeground", "white")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("App.TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("Hero.TFrame", background=ACCENT)
        style.configure("TLabel", background=BG, foreground=INK)
        style.configure("Card.TLabel", background=CARD, foreground=INK)
        style.configure("HeroTitle.TLabel", background=ACCENT, foreground="white", font=("Segoe UI Semibold", 23))
        style.configure("HeroText.TLabel", background=ACCENT, foreground="#E8E5FF", font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=CARD, foreground=INK, font=("Segoe UI Semibold", 12))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Selected.TLabel", background=CARD, foreground=ACCENT, font=("Segoe UI Semibold", 9))
        style.configure("Status.TLabel", background=ACCENT_SOFT, foreground=ACCENT, font=("Segoe UI Semibold", 9), padding=(10, 5))
        style.configure("TButton", background="#F8F9FC", foreground=INK, bordercolor=BORDER, padding=(12, 8), relief="flat")
        style.map("TButton", background=[("active", "#EEF1F6"), ("disabled", "#F5F6F8")], foreground=[("disabled", "#98A2B3")])
        style.configure("Primary.TButton", background=ACCENT, foreground="white", bordercolor=ACCENT, padding=(16, 10), font=("Segoe UI Semibold", 10))
        style.map("Primary.TButton", background=[("active", ACCENT_HOVER), ("disabled", "#B7B0E8")], foreground=[("disabled", "#F4F2FF")])
        style.configure("Mode.TRadiobutton", background=CARD, foreground=MUTED, indicatorcolor=CARD, padding=(13, 8), font=("Segoe UI Semibold", 9))
        style.map("Mode.TRadiobutton", background=[("selected", ACCENT_SOFT), ("active", "#F7F5FF")], foreground=[("selected", ACCENT), ("active", ACCENT)], indicatorcolor=[("selected", ACCENT_SOFT)])
        style.configure("TCombobox", fieldbackground="#F9FAFB", background="#F9FAFB", bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=7)
        style.configure("Search.TEntry", fieldbackground="#F9FAFB", bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER, padding=8)
        style.configure("Gift.Treeview", background=CARD, fieldbackground=CARD, foreground=INK, rowheight=34, borderwidth=0, font=("Segoe UI", 10))
        style.configure("Gift.Treeview.Heading", background="#F8F9FC", foreground=MUTED, relief="flat", font=("Segoe UI Semibold", 9), padding=(7, 7))
        style.map("Gift.Treeview", background=[("selected", ACCENT_SOFT)], foreground=[("selected", ACCENT)])

    @staticmethod
    def _card(parent, padding=(18, 16)) -> ttk.Frame:
        return ttk.Frame(parent, style="Card.TFrame", padding=padding)

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame", padding=(24, 20, 24, 22))
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=2)
        root.rowconfigure(3, weight=1)

        hero = ttk.Frame(root, style="Hero.TFrame", padding=(22, 17))
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        hero.columnconfigure(0, weight=1)
        ttk.Label(hero, text="Tamagometer", style="HeroTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(hero, text="Connection gifts and Friends BFF rewards with Flipper Zero", style="HeroText.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.status_var = tk.StringVar(value="Flipper not connected")
        ttk.Label(hero, textvariable=self.status_var, style="Status.TLabel").grid(row=0, column=1, rowspan=2, sticky="e")

        mode_card = self._card(root, (18, 12))
        mode_card.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(mode_card, text="Device", style="Section.TLabel").pack(side="left", padx=(0, 14))
        self.mode_var = tk.StringVar(value=self.config_data.get("mode", "connection"))
        if self.mode_var.get() not in {"connection", "friends"}:
            self.mode_var.set("connection")
        self.connection_mode = ttk.Radiobutton(mode_card, text="Connection 2024 · IR", value="connection", variable=self.mode_var, command=self._change_mode, style="Mode.TRadiobutton")
        self.connection_mode.pack(side="left")
        self.friends_mode = ttk.Radiobutton(mode_card, text="Friends · LF RFID", value="friends", variable=self.mode_var, command=self._change_mode, style="Mode.TRadiobutton")
        self.friends_mode.pack(side="left", padx=(6, 0))

        connect_card = self._card(root)
        connect_card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        connect_card.columnconfigure(0, weight=1)
        ttk.Label(connect_card, text="Flipper Zero", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(connect_card, text="Enhanced Companion must be open; close qFlipper first.", style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 0))
        controls = ttk.Frame(connect_card, style="Card.TFrame")
        controls.grid(row=0, column=1, rowspan=2, sticky="e")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(controls, textvariable=self.port_var, state="readonly", width=31)
        self.port_combo.pack(side="left")
        ttk.Button(controls, text="Refresh", command=self.refresh_ports).pack(side="left", padx=(7, 0))
        self.connect_button = ttk.Button(controls, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side="left", padx=(7, 0))

        picker = self._card(root)
        picker.grid(row=3, column=0, sticky="nsew", padx=(0, 6))
        picker.columnconfigure(0, weight=1)
        picker.rowconfigure(3, weight=1)
        self.picker_title = tk.StringVar()
        self.picker_hint = tk.StringVar()
        ttk.Label(picker, textvariable=self.picker_title, style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(picker, textvariable=self.picker_hint, style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 10))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_items())
        ttk.Entry(picker, textvariable=self.search_var, style="Search.TEntry").grid(row=2, column=0, sticky="ew", pady=(0, 10))
        list_frame = ttk.Frame(picker, style="Card.TFrame")
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.item_list = ttk.Treeview(list_frame, columns=("id", "name"), show="headings", selectmode="browse", style="Gift.Treeview")
        self.item_list.heading("id", text="ID")
        self.item_list.heading("name", text="ITEM")
        self.item_list.column("id", width=58, minwidth=58, stretch=False, anchor="center")
        self.item_list.column("name", width=300, anchor="w")
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.item_list.yview)
        self.item_list.configure(yscrollcommand=scroll.set)
        self.item_list.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.item_list.bind("<<TreeviewSelect>>", lambda _event: self._selection_changed())
        self.selection_var = tk.StringVar()
        ttk.Label(picker, textvariable=self.selection_var, style="Selected.TLabel").grid(row=4, column=0, sticky="w", pady=(9, 0))

        side = ttk.Frame(root, style="App.TFrame")
        side.grid(row=3, column=1, sticky="nsew", padx=(6, 0))
        side.columnconfigure(0, weight=1)
        side.rowconfigure(1, weight=1)
        action = self._card(side)
        action.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        action.columnconfigure(0, weight=1)
        ttk.Label(action, text="Transfer", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.instructions_var = tk.StringVar()
        ttk.Label(action, textvariable=self.instructions_var, style="Muted.TLabel", wraplength=315, justify="left").grid(row=1, column=0, sticky="ew", pady=(7, 14))
        self.send_button = ttk.Button(action, text="Start transfer", style="Primary.TButton", command=self.start_delivery, state="disabled")
        self.send_button.grid(row=2, column=0, sticky="ew")
        self.cancel_button = ttk.Button(action, text="Cancel", command=self.cancel_delivery, state="disabled")
        self.cancel_button.grid(row=3, column=0, sticky="ew", pady=(7, 0))

        diagnostics = self._card(side)
        diagnostics.grid(row=1, column=0, sticky="nsew")
        diagnostics.columnconfigure(0, weight=1)
        diagnostics.rowconfigure(1, weight=1)
        log_head = ttk.Frame(diagnostics, style="Card.TFrame")
        log_head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(log_head, text="Diagnostics", style="Section.TLabel").pack(side="left")
        ttk.Button(log_head, text="Copy", command=self.copy_log).pack(side="right")
        self.log_text = tk.Text(diagnostics, height=10, wrap="word", state="disabled", bg=LOG_BG, fg="#D0D5DD", insertbackground="white", selectbackground=ACCENT, relief="flat", padx=11, pady=10, font=("Cascadia Mono", 8))
        self.log_text.grid(row=1, column=0, sticky="nsew")

    def _append_log(self, text: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get("1.0", "end-1c"))

    def _load_config(self) -> dict:
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save_config(self):
        data = {"port": self.port_var.get().split(" — ", 1)[0], "mode": self.mode_var.get()}
        try:
            CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError:
            pass

    def refresh_ports(self):
        ports = list_ports()
        values = [f"{device} — {description}" for device, description in ports]
        self.port_combo["values"] = values
        previous = self.config_data.get("port", "")
        chosen = next((value for value in values if value.split(" — ", 1)[0] == previous), "")
        self.port_var.set(chosen or (values[0] if values else ""))
        if not values:
            self.status_var.set("No COM ports found")

    def toggle_connection(self):
        if self.connection.connected:
            self.connection.close()
            self.connect_button.configure(text="Connect")
            self.send_button.configure(state="disabled")
            self.status_var.set("Flipper disconnected")
            return
        selection = self.port_var.get()
        if not selection:
            messagebox.showwarning("No port selected", "Connect the Flipper and click Refresh.")
            return
        port = selection.split(" — ", 1)[0]
        try:
            self.connection.open(port)
        except Exception as error:
            messagebox.showerror("Connection failed", str(error))
            return
        self.connect_button.configure(text="Disconnect")
        self.send_button.configure(state="normal")
        self.status_var.set(f"Connected · {port}")
        self._append_log(f"Opened {port} at 460800 baud")
        self._save_config()

    def _change_mode(self):
        friends = self.mode_var.get() == "friends"
        self.picker_title.set("Choose a BFF reward" if friends else "Choose a gift")
        self.picker_hint.set("60 jewelry outcomes and five Gotchi Point bonuses" if friends else "181 items supported by the Connection 2024 protocol")
        self.instructions_var.set(
            "On Tamagotchi Friends, open BFF BUMP and start a bump. Hold its back directly against the Flipper's LF RFID antenna, then click Send BFF reward."
            if friends else
            "Click Wait and send gift first. On the Tamagotchi, choose Connection → Present, start the connection, and align the IR ports."
        )
        self.send_button.configure(text="Send BFF reward" if friends else "Wait and send gift")
        self.search_var.set("")
        self._filter_items()
        self._save_config()

    def _filter_items(self):
        items = FRIENDS_REWARDS if self.mode_var.get() == "friends" else GIFT_ITEMS
        query = self.search_var.get().strip().casefold()
        self.visible_items = [item for item in items if query in item[1].casefold()]
        self.item_list.delete(*self.item_list.get_children())
        for item_id, name in self.visible_items:
            identifier = f"{item_id:02X}" if self.mode_var.get() == "friends" else f"{item_id:03d}"
            self.item_list.insert("", "end", values=(identifier, name))
        children = self.item_list.get_children()
        if children:
            self.item_list.selection_set(children[0])
            self.item_list.focus(children[0])
            self._selection_changed()

    def _selection_changed(self):
        selected = self._selected_item()
        if selected:
            item_id, name = selected
            identifier = f"0x{item_id:02X}" if self.mode_var.get() == "friends" else str(item_id)
            self.selection_var.set(f"Selected · {name} ({identifier})")

    def _selected_item(self) -> tuple[int, str] | None:
        selection = self.item_list.selection()
        if not selection:
            return None
        return self.visible_items[self.item_list.index(selection[0])]

    def _set_busy(self, busy: bool):
        self.send_button.configure(state="disabled" if busy or not self.connection.connected else "normal")
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self.connection_mode.configure(state="disabled" if busy else "normal")
        self.friends_mode.configure(state="disabled" if busy else "normal")
        self.connect_button.configure(state="disabled" if busy else "normal")

    def start_delivery(self):
        selected = self._selected_item()
        if selected is None:
            messagebox.showwarning("Nothing selected", "Choose an item from the list.")
            return
        if not self.connection.connected:
            messagebox.showwarning("Flipper not connected", "Connect to the Flipper COM port first.")
            return
        item_id, item_name = selected
        mode = self.mode_var.get()
        self._append_log(f"--- {('Friends BFF' if mode == 'friends' else 'Connection gift')}: {item_name}, ID {item_id} ---")
        self.cancel_event.clear()
        self._set_busy(True)
        self.status_var.set(f"Preparing · {item_name}")

        def run():
            try:
                if mode == "friends":
                    self.connection.send_friends_reward(item_id, self.cancel_event, lambda status: self.events.put(("status", status)))
                else:
                    self.connection.deliver_gift(GIFT_RESPONSE_2, lambda request: make_gift_response_for_request(item_id, request), self.cancel_event, lambda status: self.events.put(("status", status)))
            except CancelledError:
                self.events.put(("cancelled", "Transfer cancelled"))
            except Exception as error:
                self.events.put(("error", str(error)))
            else:
                self.events.put(("done", f"{item_name} sent"))

        self.worker = threading.Thread(target=run, daemon=True)
        self.worker.start()

    def cancel_delivery(self):
        self.cancel_event.set()
        self.status_var.set("Cancelling…")

    def _poll_events(self):
        try:
            while True:
                kind, text = self.events.get_nowait()
                if kind == "log":
                    self._append_log(text)
                    continue
                self.status_var.set(text)
                self._append_log(text)
                if kind in {"done", "cancelled", "error"}:
                    self._set_busy(False)
                if kind == "done":
                    messagebox.showinfo("Transfer complete", text)
                elif kind == "error":
                    messagebox.showerror("Transfer error", text)
        except queue.Empty:
            pass
        self.after(80, self._poll_events)

    def _on_close(self):
        self.cancel_event.set()
        self.connection.close()
        self.destroy()


if __name__ == "__main__":
    TamagometerDesktop().mainloop()
