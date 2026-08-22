"""Main Tk window and UI event handling."""

from __future__ import annotations

from pathlib import Path
import queue
import time
import tkinter as tk
from tkinter import messagebox, ttk

from flipper_serial import (
    FlipperConnection,
    SerialPortInfo,
    find_flipper_port,
    list_ports,
)
from transfer_status import TransferState

from . import __version__
from .modes import CONNECTION_MODE, FRIENDS_MODE, ModeDefinition, get_mode
from .settings import AppSettings, SettingsStore
from .theme import ACCENT, LOG_BG, card, configure_theme
from .transfer import AppEvent, TransferController


class TamagometerDesktop(tk.Tk):
    def __init__(self, config_path: Path | None = None):
        super().__init__()
        self.title("Tamagometer Desktop")
        self.geometry("920x790")
        self.minsize(780, 700)
        configure_theme(self)

        self.events: queue.Queue[AppEvent] = queue.Queue()
        self.connection = FlipperConnection(
            trace=lambda text: self.events.put(AppEvent("log", text)),
        )
        self.transfer = TransferController(self.connection, self.events)
        self.settings_store = SettingsStore(config_path)
        self.settings = self.settings_store.load()
        self.visible_items: list[tuple[int, str]] = []
        self.ports: list[SerialPortInfo] = []
        self.auto_reconnect = False
        self.reconnect_port = ""
        self.reconnecting = False
        self.next_reconnect_at = 0.0

        self._build_ui()
        self.refresh_ports()
        self._change_mode()
        self.after(80, self._poll_events)
        self.after(1200, self._monitor_connection)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    @property
    def current_mode(self) -> ModeDefinition:
        return get_mode(self.mode_var.get())

    def _build_ui(self) -> None:
        root = ttk.Frame(self, style="App.TFrame", padding=(24, 20, 24, 22))
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=2)
        root.rowconfigure(3, weight=1)

        self._build_hero(root)
        self._build_mode_card(root)
        self._build_connection_card(root)
        self._build_item_picker(root)
        self._build_action_panel(root)

    def _build_hero(self, root: ttk.Frame) -> None:
        hero = ttk.Frame(root, style="Hero.TFrame", padding=(22, 17))
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        hero.columnconfigure(0, weight=1)
        ttk.Label(hero, text=f"Tamagometer {__version__}", style="HeroTitle.TLabel").grid(
            row=0, column=0, sticky="w",
        )
        ttk.Label(
            hero,
            text="Connection gifts and Friends BFF rewards with Flipper Zero",
            style="HeroText.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        self.status_var = tk.StringVar(value="Flipper not connected")
        ttk.Label(hero, textvariable=self.status_var, style="Status.TLabel").grid(
            row=0, column=1, rowspan=2, sticky="e",
        )

    def _build_mode_card(self, root: ttk.Frame) -> None:
        mode_card = card(root, (18, 12))
        mode_card.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(mode_card, text="Device", style="Section.TLabel").pack(
            side="left", padx=(0, 14),
        )
        self.mode_var = tk.StringVar(value=get_mode(self.settings.mode).key)
        self.connection_mode = ttk.Radiobutton(
            mode_card,
            text=CONNECTION_MODE.selector_label,
            value=CONNECTION_MODE.key,
            variable=self.mode_var,
            command=self._change_mode,
            style="Mode.TRadiobutton",
        )
        self.connection_mode.pack(side="left")
        self.friends_mode = ttk.Radiobutton(
            mode_card,
            text=FRIENDS_MODE.selector_label,
            value=FRIENDS_MODE.key,
            variable=self.mode_var,
            command=self._change_mode,
            style="Mode.TRadiobutton",
        )
        self.friends_mode.pack(side="left", padx=(6, 0))

    def _build_connection_card(self, root: ttk.Frame) -> None:
        connect_card = card(root)
        connect_card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        connect_card.columnconfigure(0, weight=1)
        ttk.Label(connect_card, text="Flipper Zero", style="Section.TLabel").grid(
            row=0, column=0, sticky="w",
        )
        ttk.Label(
            connect_card,
            text="Enhanced Companion must be open; close qFlipper first.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        controls = ttk.Frame(connect_card, style="Card.TFrame")
        controls.grid(row=0, column=1, rowspan=2, sticky="e")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            controls, textvariable=self.port_var, state="readonly", width=31,
        )
        self.port_combo.pack(side="left")
        ttk.Button(controls, text="Refresh", command=self.refresh_ports).pack(
            side="left", padx=(7, 0),
        )
        self.connect_button = ttk.Button(
            controls, text="Connect", command=self.toggle_connection,
        )
        self.connect_button.pack(side="left", padx=(7, 0))

    def _build_item_picker(self, root: ttk.Frame) -> None:
        picker = card(root)
        picker.grid(row=3, column=0, sticky="nsew", padx=(0, 6))
        picker.columnconfigure(0, weight=1)
        picker.rowconfigure(3, weight=1)
        self.picker_title = tk.StringVar()
        self.picker_hint = tk.StringVar()
        ttk.Label(picker, textvariable=self.picker_title, style="Section.TLabel").grid(
            row=0, column=0, sticky="w",
        )
        ttk.Label(picker, textvariable=self.picker_hint, style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(2, 10),
        )
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_items())
        ttk.Entry(picker, textvariable=self.search_var, style="Search.TEntry").grid(
            row=2, column=0, sticky="ew", pady=(0, 10),
        )

        list_frame = ttk.Frame(picker, style="Card.TFrame")
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.item_list = ttk.Treeview(
            list_frame,
            columns=("id", "name"),
            show="headings",
            selectmode="browse",
            style="Gift.Treeview",
        )
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
        ttk.Label(picker, textvariable=self.selection_var, style="Selected.TLabel").grid(
            row=4, column=0, sticky="w", pady=(9, 0),
        )

    def _build_action_panel(self, root: ttk.Frame) -> None:
        side = ttk.Frame(root, style="App.TFrame")
        side.grid(row=3, column=1, sticky="nsew", padx=(6, 0))
        side.columnconfigure(0, weight=1)
        side.rowconfigure(1, weight=1)

        action = card(side)
        action.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        action.columnconfigure(0, weight=1)
        ttk.Label(action, text="Transfer", style="Section.TLabel").grid(
            row=0, column=0, sticky="w",
        )
        self.instructions_var = tk.StringVar()
        ttk.Label(
            action,
            textvariable=self.instructions_var,
            style="Muted.TLabel",
            wraplength=315,
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(7, 14))
        self.transfer_stage_var = tk.StringVar(value="Ready")
        ttk.Label(
            action,
            textvariable=self.transfer_stage_var,
            style="Selected.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.transfer_progress = ttk.Progressbar(
            action, mode="determinate", maximum=10, value=0,
        )
        self.transfer_progress.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        self.send_button = ttk.Button(
            action,
            text="Start transfer",
            style="Primary.TButton",
            command=self.start_delivery,
            state="disabled",
        )
        self.send_button.grid(row=4, column=0, sticky="ew")
        self.cancel_button = ttk.Button(
            action, text="Cancel", command=self.cancel_delivery, state="disabled",
        )
        self.cancel_button.grid(row=5, column=0, sticky="ew", pady=(7, 0))
        self._build_diagnostics(side)

    def _build_diagnostics(self, side: ttk.Frame) -> None:
        diagnostics = card(side)
        diagnostics.grid(row=1, column=0, sticky="nsew")
        diagnostics.columnconfigure(0, weight=1)
        diagnostics.rowconfigure(1, weight=1)
        log_head = ttk.Frame(diagnostics, style="Card.TFrame")
        log_head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(log_head, text="Diagnostics", style="Section.TLabel").pack(side="left")
        ttk.Button(log_head, text="Copy", command=self.copy_log).pack(side="right")
        self.log_text = tk.Text(
            diagnostics,
            height=10,
            wrap="word",
            state="disabled",
            bg=LOG_BG,
            fg="#D0D5DD",
            insertbackground="white",
            selectbackground=ACCENT,
            relief="flat",
            padx=11,
            pady=10,
            font=("Cascadia Mono", 8),
        )
        self.log_text.grid(row=1, column=0, sticky="nsew")

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def copy_log(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get("1.0", "end-1c"))

    def _save_settings(self) -> None:
        self.settings = AppSettings(
            port=self.port_var.get().split(" — ", 1)[0],
            mode=self.current_mode.key,
        )
        self.settings_store.save(self.settings)

    def refresh_ports(self) -> None:
        self.ports = list_ports()
        values = [port.display_name for port in self.ports]
        self.port_combo["values"] = values
        selected_device = self.port_var.get().split(" — ", 1)[0]
        candidate = find_flipper_port(
            self.ports,
            selected_device or self.settings.port,
        )
        self.port_var.set(candidate.display_name if candidate else "")
        if not values:
            self.status_var.set("No COM ports found")

    def toggle_connection(self) -> None:
        if self.connection.connected:
            self.auto_reconnect = False
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
        self._connect_to(port)

    def _connect_to(self, port: str, automatic: bool = False) -> bool:
        if self.reconnecting:
            return False
        self.reconnecting = True
        self.status_var.set(f"Checking Companion · {port}")
        try:
            info = self.connection.open(port)
        except Exception as error:
            if automatic:
                self._append_log(f"Reconnect failed on {port}: {error}")
                self.status_var.set(f"Waiting for Flipper · {port}")
                self.next_reconnect_at = time.monotonic() + 4.0
            else:
                messagebox.showerror("Connection failed", str(error))
                self.status_var.set("Flipper not connected")
            return False
        finally:
            self.reconnecting = False
        self.connect_button.configure(text="Disconnect")
        self.send_button.configure(state="normal")
        version = info.version if info else "unknown"
        self.status_var.set(f"Connected · {port} · Companion {version}")
        action = "Reconnected" if automatic else "Opened"
        self._append_log(f"{action} {port} at 460800 baud; Companion {version}")
        self.auto_reconnect = True
        self.reconnect_port = port
        self._save_settings()
        return True

    def _monitor_connection(self) -> None:
        try:
            ports = list_ports()
            devices = {port.device.casefold() for port in ports}
            if self.connection.connected and self.connection.port.casefold() not in devices:
                lost_port = self.connection.port
                self.connection.close()
                self.connect_button.configure(text="Connect")
                self.send_button.configure(state="disabled")
                self.status_var.set(f"Flipper disconnected · waiting for {lost_port}")
                self._append_log(f"USB connection lost on {lost_port}; automatic reconnect enabled")
            elif (
                self.auto_reconnect
                and not self.connection.connected
                and not self.transfer.active
                and time.monotonic() >= self.next_reconnect_at
            ):
                candidate = find_flipper_port(ports, self.reconnect_port)
                if candidate:
                    self._connect_to(candidate.device, automatic=True)
            elif not self.connection.connected:
                self.ports = ports
                self.port_combo["values"] = [port.display_name for port in ports]
                if not self.port_var.get():
                    candidate = find_flipper_port(ports, self.settings.port)
                    if candidate:
                        self.port_var.set(candidate.display_name)
        finally:
            self.after(1200, self._monitor_connection)

    def _change_mode(self) -> None:
        mode = self.current_mode
        self.picker_title.set(mode.picker_title)
        self.picker_hint.set(mode.picker_hint)
        self.instructions_var.set(mode.instructions)
        self.send_button.configure(text=mode.send_label)
        if self.search_var.get():
            self.search_var.set("")
        else:
            self._filter_items()
        self._save_settings()

    def _filter_items(self) -> None:
        mode = self.current_mode
        query = self.search_var.get().strip().casefold()
        self.visible_items = [item for item in mode.items if query in item[1].casefold()]
        self.item_list.delete(*self.item_list.get_children())
        for item_id, name in self.visible_items:
            self.item_list.insert("", "end", values=(mode.list_id(item_id), name))
        children = self.item_list.get_children()
        if children:
            self.item_list.selection_set(children[0])
            self.item_list.focus(children[0])
            self._selection_changed()

    def _selection_changed(self) -> None:
        selected = self._selected_item()
        if selected:
            item_id, name = selected
            self.selection_var.set(
                f"Selected · {name} ({self.current_mode.selected_id(item_id)})",
            )

    def _selected_item(self) -> tuple[int, str] | None:
        selection = self.item_list.selection()
        if not selection:
            return None
        return self.visible_items[self.item_list.index(selection[0])]

    def _set_busy(self, busy: bool) -> None:
        self.send_button.configure(
            state="disabled" if busy or not self.connection.connected else "normal",
        )
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self.connection_mode.configure(state="disabled" if busy else "normal")
        self.friends_mode.configure(state="disabled" if busy else "normal")
        self.connect_button.configure(state="disabled" if busy else "normal")

    def start_delivery(self) -> None:
        selected = self._selected_item()
        if selected is None:
            messagebox.showwarning("Nothing selected", "Choose an item from the list.")
            return
        if not self.connection.connected:
            messagebox.showwarning("Flipper not connected", "Connect to the Flipper COM port first.")
            return
        item_id, item_name = selected
        mode = self.current_mode
        self._append_log(f"--- {mode.attempt_label}: {item_name}, ID {item_id} ---")
        self._set_busy(True)
        self.transfer_progress.configure(value=0, maximum=10)
        self.transfer.start(mode, item_id, item_name)

    def cancel_delivery(self) -> None:
        self.transfer.cancel()
        self.status_var.set("Cancelling…")

    def _poll_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                if event.kind == "log":
                    self._append_log(event.text)
                    continue
                self.status_var.set(event.text)
                self.transfer_stage_var.set(event.text)
                self._append_log(event.text)
                if event.current is not None and event.total:
                    self.transfer_progress.configure(maximum=event.total, value=event.current)
                elif event.state == TransferState.COMPLETED:
                    maximum = float(self.transfer_progress.cget("maximum"))
                    self.transfer_progress.configure(value=maximum)
                if event.kind in {"done", "cancelled", "error", "disconnected"}:
                    self._set_busy(False)
                if event.kind == "error":
                    messagebox.showerror("Transfer error", event.text)
        except queue.Empty:
            pass
        self.after(80, self._poll_events)

    def _on_close(self) -> None:
        self.transfer.cancel()
        self.connection.close()
        self.destroy()
