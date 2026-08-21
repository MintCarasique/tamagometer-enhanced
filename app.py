"""Small Russian-language desktop UI for sending Connection gifts."""

from __future__ import annotations

import json
from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from flipper_serial import CancelledError, FlipperConnection, list_ports
from tamagometer_core import GIFT_ITEMS, GIFT_RESPONSE_2, make_gift_response_for_request


APP_DIR = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
CONFIG_PATH = APP_DIR / ".tamagometer-desktop.json"


class TamagometerDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tamagometer Desktop")
        self.geometry("760x760")
        self.minsize(640, 650)
        self.connection = FlipperConnection(trace=lambda text: self.events.put(("log", text)))
        self.cancel_event = threading.Event()
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.worker: threading.Thread | None = None
        self.all_items = list(GIFT_ITEMS)
        self.visible_items = list(GIFT_ITEMS)
        self.config_data = self._load_config()
        self._configure_style()
        self._build_ui()
        self.refresh_ports()
        self.after(80, self._poll_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_style(self):
        self.option_add("*Font", ("Segoe UI", 10))
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 20))
        style.configure("Hint.TLabel", foreground="#555555")
        style.configure("Send.TButton", font=("Segoe UI Semibold", 11), padding=(16, 9))

    def _build_ui(self):
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)
        ttk.Label(root, text="Tamagometer Desktop", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            root,
            text="A simple gift sender for Tamagotchi Connection via Flipper Zero",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(0, 18))

        device = ttk.LabelFrame(root, text="1. Connect your Flipper", padding=12)
        device.pack(fill="x")
        row = ttk.Frame(device)
        row.pack(fill="x")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(row, textvariable=self.port_var, state="readonly")
        self.port_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Refresh", command=self.refresh_ports).pack(side="left", padx=(8, 0))
        self.connect_button = ttk.Button(row, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side="left", padx=(8, 0))
        ttk.Label(
            device,
            text="Keep Tamagometer Companion open on the Flipper and close qFlipper.",
            style="Hint.TLabel",
        ).pack(anchor="w", pady=(8, 0))

        gifts = ttk.LabelFrame(root, text="2. Choose a gift", padding=12)
        gifts.pack(fill="both", expand=True, pady=14)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_items())
        ttk.Label(gifts, text="Search by name:").pack(anchor="w", pady=(0, 4))
        ttk.Entry(gifts, textvariable=self.search_var).pack(fill="x", pady=(0, 8))
        list_frame = ttk.Frame(gifts)
        list_frame.pack(fill="both", expand=True)
        self.item_list = tk.Listbox(
            list_frame, activestyle="none", exportselection=False, height=12,
            selectmode="browse", borderwidth=0, highlightthickness=1,
        )
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.item_list.yview)
        self.item_list.configure(yscrollcommand=scroll.set)
        self.item_list.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.item_list.bind("<<ListboxSelect>>", lambda _event: self._selection_changed())
        self._filter_items()

        action = ttk.LabelFrame(root, text="3. Start the transfer", padding=12)
        action.pack(fill="x")
        ttk.Label(
            action,
            text="First click the button below. Then select Connection → Present\n"
                 "on the Tamagotchi, start the connection, and align the IR ports.",
        ).pack(anchor="w")
        buttons = ttk.Frame(action)
        buttons.pack(fill="x", pady=(10, 0))
        self.send_button = ttk.Button(
            buttons, text="Wait for Tamagotchi and send", style="Send.TButton",
            command=self.start_delivery, state="disabled",
        )
        self.send_button.pack(side="left")
        self.cancel_button = ttk.Button(buttons, text="Cancel", command=self.cancel_delivery, state="disabled")
        self.cancel_button.pack(side="left", padx=8)
        self.status_var = tk.StringVar(value="Flipper is not connected")
        ttk.Label(action, textvariable=self.status_var).pack(anchor="w", pady=(10, 0))

        diagnostics = ttk.LabelFrame(root, text="Diagnostics", padding=10)
        diagnostics.pack(fill="x", pady=(14, 0))
        self.log_text = tk.Text(
            diagnostics, height=6, wrap="word", state="disabled",
            font=("Consolas", 9), borderwidth=0, highlightthickness=1,
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        ttk.Button(diagnostics, text="Copy log", command=self.copy_log).pack(
            side="right", anchor="n", padx=(8, 0),
        )

    def _append_log(self, text: str):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def copy_log(self):
        text = self.log_text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)

    def _load_config(self) -> dict:
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save_config(self):
        try:
            CONFIG_PATH.write_text(json.dumps({"port": self.port_var.get()}), encoding="utf-8")
        except OSError:
            pass

    def refresh_ports(self):
        ports = list_ports()
        values = [f"{device} — {description}" for device, description in ports]
        self.port_combo["values"] = values
        previous = self.config_data.get("port", "")
        chosen = next((value for value in values if value.split(" — ", 1)[0] == previous), "")
        if not chosen and values:
            chosen = values[0]
        self.port_var.set(chosen)
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
        self.status_var.set(f"Connected: {port}")
        self._append_log(f"Opened {port} at 460800 baud")
        self._save_config()

    def _filter_items(self):
        query = self.search_var.get().strip().casefold()
        self.visible_items = [item for item in self.all_items if query in item[1].casefold()]
        self.item_list.delete(0, "end")
        for item_id, name in self.visible_items:
            self.item_list.insert("end", f"{item_id:03d}   {name}")
        if self.visible_items:
            self.item_list.selection_set(0)

    def _selection_changed(self):
        selection = self.item_list.curselection()
        if selection:
            item_id, name = self.visible_items[selection[0]]
            self.status_var.set(f"Selected gift: {name} (ID {item_id})")

    def _selected_item(self) -> tuple[int, str] | None:
        selection = self.item_list.curselection()
        return self.visible_items[selection[0]] if selection else None

    def start_delivery(self):
        selected = self._selected_item()
        if selected is None:
            messagebox.showwarning("No gift selected", "Select a gift from the list.")
            return
        if not self.connection.connected:
            messagebox.showwarning("Flipper not connected", "Connect to the Flipper COM port first.")
            return
        item_id, item_name = selected
        self._append_log(f"--- New attempt: {item_name}, ID {item_id} ---")
        self.cancel_event.clear()
        self.send_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")
        self.status_var.set(f"Preparing gift: {item_name}")

        def run():
            try:
                self.connection.deliver_gift(
                    GIFT_RESPONSE_2,
                    lambda request: make_gift_response_for_request(item_id, request),
                    self.cancel_event,
                    lambda status: self.events.put(("status", status)),
                )
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
                    self.cancel_button.configure(state="disabled")
                    self.send_button.configure(state="normal" if self.connection.connected else "disabled")
                if kind == "done":
                    messagebox.showinfo("Done", text)
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
