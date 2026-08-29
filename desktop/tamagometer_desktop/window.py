"""Main Tk window and UI event handling."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from pathlib import Path
import queue
import time
import tkinter as tk
from tkinter import filedialog, ttk

from flipper_serial import FlipperConnection, SerialPortInfo, find_flipper_port, list_ports
from transfer_status import TransferState

from . import __version__
from .alignment import AlignmentGuide
from .assets import item_sprite_path
from .catalog import (
    ALL_CATEGORY,
    FAVORITES_CATEGORY,
    RECENT_CATEGORY,
    categories_for,
    category_for,
    item_key,
    item_name,
    parse_item_key,
    sprite_filename,
)
from .diagnostics import build_diagnostic_report
from .modes import CONNECTION_MODE, FRIENDS_MODE, LEGACY_MODE, ModeDefinition, get_mode
from .onboarding import OnboardingWindow
from .settings import AppSettings, SettingsStore
from .theme import card, configure_theme
from .transfer import AppEvent, TransferController


STATE_PROGRESS = {
    TransferState.PREPARING: 5,
    TransferState.WAITING_FIRST_MESSAGE: 20,
    TransferState.SENDING_ACKNOWLEDGEMENT: 45,
    TransferState.WAITING_GIFT_REQUEST: 62,
    TransferState.SENDING_GIFT: 88,
    TransferState.VERIFYING: 95,
    TransferState.COMPLETED: 100,
    TransferState.CANCELLED: 0,
    TransferState.FAILED: 0,
    TransferState.DISCONNECTED: 0,
}


class TamagometerDesktop(tk.Tk):
    def __init__(self, config_path: Path | None = None):
        super().__init__()
        self.title("Tamagometer Desktop")
        self.geometry("1040x850")
        self.minsize(900, 760)

        self.settings_store = SettingsStore(config_path)
        self.settings = self.settings_store.load()
        self.palette = configure_theme(self, self.settings.theme)
        self.events: queue.Queue[AppEvent] = queue.Queue()
        self.connection = FlipperConnection(
            trace=lambda text: self.events.put(AppEvent("log", text)),
        )
        self.transfer = TransferController(self.connection, self.events)
        self.visible_items: list[tuple[int, str]] = []
        self.visible_by_key: dict[str, tuple[int, str]] = {}
        self.ports: list[SerialPortInfo] = []
        self.auto_reconnect = False
        self.manual_disconnect = False
        self.reconnect_port = ""
        self.reconnecting = False
        self.next_reconnect_at = 0.0
        self.next_initial_connect_at = 0.0
        self.pending_transfer = ""
        self.busy = False
        self.item_sprite: tk.PhotoImage | None = None
        self.notice_after: str | None = None
        self.onboarding: OnboardingWindow | None = None

        self._build_ui()
        self.refresh_ports()
        self._change_mode(save=False)
        self.after(80, self._poll_events)
        self.after(800, self._initial_connection)
        self.after(1200, self._monitor_connection)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    @property
    def current_mode(self) -> ModeDefinition:
        return get_mode(self.mode_var.get())

    def _build_ui(self) -> None:
        self.root_frame = ttk.Frame(self, style="App.TFrame", padding=(24, 20, 24, 22))
        self.root_frame.pack(fill="both", expand=True)
        self.root_frame.columnconfigure(0, weight=3)
        self.root_frame.columnconfigure(1, weight=2)
        self.root_frame.rowconfigure(4, weight=1)
        self._build_hero()
        self._build_notice()
        self._build_mode_card()
        self._build_connection_card()
        self._build_item_picker()
        self._build_action_panel()

    def _build_hero(self) -> None:
        hero = ttk.Frame(self.root_frame, style="Hero.TFrame", padding=(22, 17))
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        hero.columnconfigure(0, weight=1)
        ttk.Label(hero, text=f"Tamagometer {__version__}", style="HeroTitle.TLabel").grid(
            row=0, column=0, sticky="w",
        )
        ttk.Label(
            hero,
            text="Connection gifts, original V2/V3 fallback, and Friends rewards",
            style="HeroText.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        right = ttk.Frame(hero, style="Hero.TFrame")
        right.grid(row=0, column=1, rowspan=2, sticky="e")
        self.status_var = tk.StringVar(value="Flipper not connected")
        ttk.Label(right, textvariable=self.status_var, style="Status.TLabel").pack(side="left")
        self.theme_button = ttk.Button(right, command=self.toggle_theme, width=10)
        self.theme_button.pack(side="left", padx=(8, 0))
        self._update_theme_button()

    def _build_notice(self) -> None:
        self.notice_var = tk.StringVar()
        self.notice_label = ttk.Label(
            self.root_frame, textvariable=self.notice_var, style="Notice.TLabel",
            wraplength=920, justify="left",
        )
        self.notice_label.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.notice_label.grid_remove()

    def _build_mode_card(self) -> None:
        mode_card = card(self.root_frame, (18, 12))
        mode_card.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(mode_card, text="Device", style="Section.TLabel").pack(side="left", padx=(0, 14))
        self.mode_var = tk.StringVar(value=get_mode(self.settings.mode).key)
        self.connection_mode = ttk.Radiobutton(
            mode_card, text=CONNECTION_MODE.selector_label, value=CONNECTION_MODE.key,
            variable=self.mode_var, command=self._change_mode, style="Mode.TRadiobutton",
        )
        self.connection_mode.pack(side="left")
        self.friends_mode = ttk.Radiobutton(
            mode_card, text=FRIENDS_MODE.selector_label, value=FRIENDS_MODE.key,
            variable=self.mode_var, command=self._change_mode, style="Mode.TRadiobutton",
        )
        self.friends_mode.pack(side="left", padx=(6, 0))
        self.legacy_mode = ttk.Radiobutton(
            mode_card, text=LEGACY_MODE.selector_label, value=LEGACY_MODE.key,
            variable=self.mode_var, command=self._change_mode, style="Mode.TRadiobutton",
        )
        self.legacy_mode.pack(side="left", padx=(6, 0))

    def _build_connection_card(self) -> None:
        connect_card = card(self.root_frame)
        connect_card.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        connect_card.columnconfigure(0, weight=1)
        ttk.Label(connect_card, text="Flipper Zero", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            connect_card,
            text="Enhanced Companion must be open; close qFlipper first. Compatible ports reconnect automatically.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        controls = ttk.Frame(connect_card, style="Card.TFrame")
        controls.grid(row=0, column=1, rowspan=2, sticky="e")
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(controls, textvariable=self.port_var, state="readonly", width=31)
        self.port_combo.pack(side="left")
        ttk.Button(controls, text="Refresh", command=self.refresh_ports).pack(side="left", padx=(7, 0))
        self.connect_button = ttk.Button(controls, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side="left", padx=(7, 0))

    def _build_item_picker(self) -> None:
        picker = card(self.root_frame)
        picker.grid(row=4, column=0, sticky="nsew", padx=(0, 6))
        picker.columnconfigure(0, weight=1)
        picker.rowconfigure(4, weight=1)
        self.picker_title = tk.StringVar()
        self.picker_hint = tk.StringVar()
        ttk.Label(picker, textvariable=self.picker_title, style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(picker, textvariable=self.picker_hint, style="Muted.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 10))

        filters = ttk.Frame(picker, style="Card.TFrame")
        filters.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        filters.columnconfigure(1, weight=1)
        self.category_var = tk.StringVar(value=ALL_CATEGORY)
        self.category_combo = ttk.Combobox(filters, textvariable=self.category_var, state="readonly", width=20)
        self.category_combo.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.category_combo.bind("<<ComboboxSelected>>", lambda _event: self._filter_items())
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_items())
        ttk.Entry(filters, textvariable=self.search_var, style="Search.TEntry").grid(row=0, column=1, sticky="ew")

        list_frame = ttk.Frame(picker, style="Card.TFrame")
        list_frame.grid(row=4, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        self.item_list = ttk.Treeview(
            list_frame, columns=("favorite", "id", "name", "category"),
            show="headings", selectmode="browse", style="Gift.Treeview",
        )
        self.item_list.heading("favorite", text="★")
        self.item_list.heading("id", text="ID")
        self.item_list.heading("name", text="ITEM")
        self.item_list.heading("category", text="CATEGORY")
        self.item_list.column("favorite", width=38, stretch=False, anchor="center")
        self.item_list.column("id", width=58, stretch=False, anchor="center")
        self.item_list.column("name", width=230, anchor="w")
        self.item_list.column("category", width=125, anchor="w")
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.item_list.yview)
        self.item_list.configure(yscrollcommand=scroll.set)
        self.item_list.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.item_list.bind("<<TreeviewSelect>>", lambda _event: self._selection_changed())
        self.item_list.bind("<Double-1>", lambda _event: self._toggle_favorite())

        preview = ttk.Frame(picker, style="Card.TFrame")
        preview.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        preview.columnconfigure(1, weight=1)
        self.sprite_label = ttk.Label(preview, style="Card.TLabel", width=7, anchor="center")
        self.sprite_label.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 10))
        self.selection_var = tk.StringVar()
        ttk.Label(preview, textvariable=self.selection_var, style="Selected.TLabel").grid(row=0, column=1, sticky="w")
        self.favorite_button = ttk.Button(preview, text="Add to favorites", command=self._toggle_favorite)
        self.favorite_button.grid(row=1, column=1, sticky="w", pady=(5, 0))

    def _build_action_panel(self) -> None:
        side = ttk.Frame(self.root_frame, style="App.TFrame")
        side.grid(row=4, column=1, sticky="nsew", padx=(6, 0))
        side.columnconfigure(0, weight=1)
        side.rowconfigure(1, weight=1)
        action = card(side)
        action.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        action.columnconfigure(0, weight=1)
        ttk.Label(action, text="Transfer guide", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.alignment = AlignmentGuide(action, self.palette)
        self.alignment.grid(row=1, column=0, sticky="ew", pady=(6, 8))
        self.instructions_var = tk.StringVar()
        ttk.Label(
            action, textvariable=self.instructions_var, style="Muted.TLabel",
            wraplength=330, justify="left",
        ).grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.transfer_stage_var = tk.StringVar(value="Ready")
        ttk.Label(action, textvariable=self.transfer_stage_var, style="Selected.TLabel").grid(row=3, column=0, sticky="w", pady=(0, 6))
        self.transfer_progress = ttk.Progressbar(action, mode="determinate", maximum=100, value=0)
        self.transfer_progress.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        self.send_button = ttk.Button(
            action, text="Start transfer", style="Primary.TButton",
            command=self.start_delivery, state="disabled",
        )
        self.send_button.grid(row=5, column=0, sticky="ew")
        self.repeat_button = ttk.Button(action, text="Repeat last transfer", command=self.repeat_last_transfer, state="disabled")
        self.repeat_button.grid(row=6, column=0, sticky="ew", pady=(7, 0))
        self.cancel_button = ttk.Button(action, text="Cancel", command=self.cancel_delivery, state="disabled")
        self.cancel_button.grid(row=7, column=0, sticky="ew", pady=(7, 0))
        self._build_diagnostics(side)

    def _build_diagnostics(self, side: ttk.Frame) -> None:
        diagnostics = card(side)
        diagnostics.grid(row=1, column=0, sticky="nsew")
        diagnostics.columnconfigure(0, weight=1)
        diagnostics.rowconfigure(1, weight=1)
        log_head = ttk.Frame(diagnostics, style="Card.TFrame")
        log_head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(log_head, text="Diagnostics", style="Section.TLabel").pack(side="left")
        ttk.Button(log_head, text="Export report", command=self.export_diagnostics).pack(side="right")
        ttk.Button(log_head, text="Copy", command=self.copy_log).pack(side="right", padx=(0, 7))
        self.log_text = tk.Text(
            diagnostics, height=9, wrap="word", state="disabled",
            bg=self.palette["log_bg"], fg=self.palette["log_fg"],
            insertbackground="white", selectbackground=self.palette["accent"],
            relief="flat", padx=11, pady=10, font=("Cascadia Mono", 8),
        )
        self.log_text.grid(row=1, column=0, sticky="nsew")

    def _notify(self, text: str, kind: str = "info", timeout: int = 5500) -> None:
        if self.notice_after:
            self.after_cancel(self.notice_after)
        style = "Error.Notice.TLabel" if kind == "error" else (
            "Success.Notice.TLabel" if kind == "success" else "Notice.TLabel"
        )
        self.notice_label.configure(style=style)
        self.notice_var.set(text)
        self.notice_label.grid()
        self.notice_after = self.after(timeout, self._hide_notice)

    def _hide_notice(self) -> None:
        self.notice_label.grid_remove()
        self.notice_after = None

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def copy_log(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get("1.0", "end-1c"))
        self._notify("Diagnostics copied to the clipboard.", "success")

    def export_diagnostics(self) -> None:
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Export diagnostic report",
            defaultextension=".txt",
            initialfile=f"tamagometer-diagnostics-{datetime.now():%Y%m%d-%H%M%S}.txt",
            filetypes=(("Text report", "*.txt"),),
        )
        if not filename:
            return
        report = build_diagnostic_report(
            self.settings, self.connection, self.ports,
            self.log_text.get("1.0", "end-1c"),
        )
        try:
            Path(filename).write_text(report, encoding="utf-8")
        except OSError as error:
            self._notify(f"Could not export the report: {error}", "error")
            return
        self._notify(f"Diagnostic report saved to {filename}", "success")

    def _save_settings(self, **changes) -> None:
        self.settings = replace(self.settings, **changes)
        self.settings_store.save(self.settings)

    def refresh_ports(self) -> None:
        self.ports = list_ports()
        self.port_combo["values"] = [port.display_name for port in self.ports]
        selected_device = self.port_var.get().split(" — ", 1)[0]
        candidate = find_flipper_port(self.ports, selected_device or self.settings.port)
        self.port_var.set(candidate.display_name if candidate else "")
        if not self.ports:
            self.status_var.set("No COM ports found")

    def toggle_connection(self) -> None:
        if self.connection.connected:
            self.auto_reconnect = False
            self.manual_disconnect = True
            self.connection.close()
            self.connect_button.configure(text="Connect")
            self.status_var.set("Flipper disconnected")
            self._update_action_buttons()
            self._notify("Flipper disconnected. Automatic reconnect is paused.")
            return
        selection = self.port_var.get()
        if not selection:
            self._notify("Connect Flipper by USB, open the Enhanced Companion, and click Refresh.", "error")
            return
        self._connect_to(selection.split(" — ", 1)[0])

    def _connect_to(self, port: str, automatic: bool = False) -> bool:
        if self.reconnecting:
            return False
        self.reconnecting = True
        self.status_var.set(f"Checking Companion · {port}")
        try:
            info = self.connection.open(port)
        except Exception as error:
            self.status_var.set(f"Waiting for Flipper · {port}" if automatic else "Flipper not connected")
            self._append_log(f"Connection failed on {port}: {error}")
            self._notify(str(error), "error")
            if automatic:
                self.next_reconnect_at = time.monotonic() + 4.0
            return False
        finally:
            self.reconnecting = False
        self.connect_button.configure(text="Disconnect")
        version = info.version if info else "unknown"
        self.status_var.set(f"Connected · {port} · Companion {version}")
        self._append_log(f"{'Reconnected' if automatic else 'Opened'} {port} at 460800 baud; Companion {version}")
        self._notify(f"Flipper connected on {port}. Companion {version} is ready.", "success")
        self.auto_reconnect = True
        self.manual_disconnect = False
        self.reconnect_port = port
        self._save_settings(port=port)
        self._update_action_buttons()
        return True

    def _try_detected_connect(self) -> bool:
        self.refresh_ports()
        candidate = find_flipper_port(self.ports, self.settings.port)
        if not candidate:
            return False
        self.port_var.set(candidate.display_name)
        return self._connect_to(candidate.device, automatic=True)

    def _initial_connection(self) -> None:
        if not self.settings.onboarding_complete:
            self.onboarding = OnboardingWindow(self, self._try_detected_connect, self._finish_onboarding)
        elif self.settings.auto_connect:
            self._try_detected_connect()

    def _finish_onboarding(self) -> None:
        self._save_settings(onboarding_complete=True)
        self._notify("Initial setup complete. You can reopen the guide by deleting the app settings file.", "success")

    def _monitor_connection(self) -> None:
        try:
            ports = list_ports()
            devices = {port.device.casefold() for port in ports}
            if self.connection.connected and self.connection.port.casefold() not in devices:
                lost_port = self.connection.port
                self.connection.close()
                self.connect_button.configure(text="Connect")
                self.status_var.set(f"Flipper disconnected · waiting for {lost_port}")
                self._append_log(f"USB connection lost on {lost_port}; automatic reconnect enabled")
                self._notify("USB connection lost. Tamagometer will reconnect when Flipper returns.", "error")
                self._update_action_buttons()
            elif (
                self.auto_reconnect and not self.connection.connected and not self.transfer.active
                and time.monotonic() >= self.next_reconnect_at
            ):
                candidate = find_flipper_port(ports, self.reconnect_port)
                if candidate:
                    self._connect_to(candidate.device, automatic=True)
            elif (
                self.settings.auto_connect
                and self.settings.onboarding_complete
                and not self.manual_disconnect
                and not self.connection.connected
                and not self.transfer.active
                and time.monotonic() >= self.next_initial_connect_at
            ):
                self.next_initial_connect_at = time.monotonic() + 8.0
                candidate = find_flipper_port(ports, self.settings.port)
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

    def toggle_theme(self) -> None:
        theme = "dark" if self.settings.theme == "light" else "light"
        self._save_settings(theme=theme)
        self.palette = configure_theme(self, theme)
        self.log_text.configure(
            bg=self.palette["log_bg"], fg=self.palette["log_fg"],
            selectbackground=self.palette["accent"],
        )
        self.alignment.set_palette(self.palette)
        self._update_theme_button()
        self._notify(f"{theme.title()} theme enabled.")

    def _update_theme_button(self) -> None:
        self.theme_button.configure(text="☾ Dark" if self.settings.theme == "light" else "☀ Light")

    def _change_mode(self, save: bool = True) -> None:
        mode = self.current_mode
        self.picker_title.set(mode.picker_title)
        self.picker_hint.set(mode.picker_hint)
        self.instructions_var.set(mode.instructions)
        self.send_button.configure(text=mode.send_label)
        self.category_combo["values"] = categories_for(mode)
        self.category_var.set(ALL_CATEGORY)
        self.alignment.set_mode(mode.key)
        if self.search_var.get():
            self.search_var.set("")
        else:
            self._filter_items()
        if save:
            self._save_settings(mode=mode.key)

    def _filter_items(self) -> None:
        mode = self.current_mode
        category = self.category_var.get() or ALL_CATEGORY
        query = self.search_var.get().strip().casefold()
        recent_order = {key: index for index, key in enumerate(self.settings.recent)}
        candidates = list(mode.items)
        if category == RECENT_CATEGORY:
            candidates.sort(key=lambda item: recent_order.get(item_key(mode.key, item[0]), 9999))
        self.visible_items = []
        for item_id, name in candidates:
            key = item_key(mode.key, item_id)
            if category == FAVORITES_CATEGORY and key not in self.settings.favorites:
                continue
            if category == RECENT_CATEGORY and key not in recent_order:
                continue
            if category not in {ALL_CATEGORY, FAVORITES_CATEGORY, RECENT_CATEGORY} and category_for(mode, item_id) != category:
                continue
            if query and query not in name.casefold() and query not in category_for(mode, item_id).casefold():
                continue
            self.visible_items.append((item_id, name))
        self.visible_by_key = {item_key(mode.key, item_id): (item_id, name) for item_id, name in self.visible_items}
        previous = self.item_list.selection()[0] if self.item_list.selection() else ""
        self.item_list.delete(*self.item_list.get_children())
        for item_id, name in self.visible_items:
            key = item_key(mode.key, item_id)
            self.item_list.insert(
                "", "end", iid=key,
                values=("★" if key in self.settings.favorites else "", mode.list_id(item_id), name, category_for(mode, item_id)),
            )
        children = self.item_list.get_children()
        if previous in children:
            chosen = previous
        else:
            chosen = children[0] if children else ""
        if chosen:
            self.item_list.selection_set(chosen)
            self.item_list.focus(chosen)
        self._selection_changed()

    def _selection_changed(self) -> None:
        selected = self._selected_item()
        if not selected:
            self.selection_var.set("No item matches this filter")
            self.sprite_label.configure(image="", text="—")
            self.favorite_button.configure(state="disabled")
            self._update_action_buttons()
            return
        item_id, name = selected
        key = item_key(self.current_mode.key, item_id)
        self.selection_var.set(f"{name} · {self.current_mode.selected_id(item_id)}")
        self.favorite_button.configure(
            text="Remove from favorites" if key in self.settings.favorites else "Add to favorites",
            state="normal",
        )
        path = item_sprite_path(sprite_filename(self.current_mode, name))
        try:
            self.item_sprite = tk.PhotoImage(file=str(path)) if path else None
        except tk.TclError:
            self.item_sprite = None
        if self.item_sprite:
            scale = max(1, min(3, 64 // max(self.item_sprite.width(), self.item_sprite.height())))
            if scale > 1:
                self.item_sprite = self.item_sprite.zoom(scale, scale)
            self.sprite_label.configure(image=self.item_sprite, text="")
        else:
            self.sprite_label.configure(image="", text="No sprite")
        self._update_action_buttons()

    def _selected_item(self) -> tuple[int, str] | None:
        selection = self.item_list.selection()
        return self.visible_by_key.get(selection[0]) if selection else None

    def _toggle_favorite(self) -> None:
        selected = self._selected_item()
        if not selected:
            return
        key = item_key(self.current_mode.key, selected[0])
        favorites = list(self.settings.favorites)
        if key in favorites:
            favorites.remove(key)
            message = f"{selected[1]} removed from favorites."
        else:
            favorites.append(key)
            message = f"{selected[1]} added to favorites."
        self._save_settings(favorites=tuple(favorites))
        self._filter_items()
        self._notify(message, "success")

    def _update_action_buttons(self) -> None:
        ready = self.connection.connected and not self.busy and not self.transfer.active
        self.send_button.configure(state="normal" if ready and self._selected_item() else "disabled")
        self.repeat_button.configure(state="normal" if ready and parse_item_key(self.settings.last_transfer) else "disabled")

    def _set_busy(self, busy: bool) -> None:
        self.busy = busy
        self.cancel_button.configure(state="normal" if busy else "disabled")
        self.connection_mode.configure(state="disabled" if busy else "normal")
        self.friends_mode.configure(state="disabled" if busy else "normal")
        self.legacy_mode.configure(state="disabled" if busy else "normal")
        self.connect_button.configure(state="disabled" if busy else "normal")
        self.port_combo.configure(state="disabled" if busy else "readonly")
        self.category_combo.configure(state="disabled" if busy else "readonly")
        self._update_action_buttons()

    def start_delivery(self) -> None:
        selected = self._selected_item()
        if selected is None:
            self._notify("Choose an item from the list first.", "error")
            return
        if not self.connection.connected:
            self._notify("Connect to the Flipper before starting a transfer.", "error")
            return
        item_id, item_name_value = selected
        mode = self.current_mode
        self.pending_transfer = item_key(mode.key, item_id)
        self._append_log(f"--- {mode.attempt_label}: {item_name_value}, ID {item_id} ---")
        self._set_busy(True)
        self.transfer_progress.configure(value=0)
        self.transfer.start(mode, item_id, item_name_value)

    def repeat_last_transfer(self) -> None:
        parsed = parse_item_key(self.settings.last_transfer)
        if not parsed:
            self._notify("No completed transfer is available to repeat.", "error")
            return
        mode, item_id = parsed
        self.mode_var.set(mode.key)
        self._change_mode()
        key = item_key(mode.key, item_id)
        if key in self.item_list.get_children():
            self.item_list.selection_set(key)
            self.item_list.focus(key)
            self.item_list.see(key)
            self._selection_changed()
            self.start_delivery()

    def cancel_delivery(self) -> None:
        self.transfer.cancel()
        self.status_var.set("Cancelling…")

    def _record_success(self) -> None:
        if not self.pending_transfer:
            return
        recent = [key for key in self.settings.recent if key != self.pending_transfer]
        recent.insert(0, self.pending_transfer)
        self._save_settings(
            recent=tuple(recent[:12]),
            last_transfer=self.pending_transfer,
        )
        self.pending_transfer = ""

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
                self.alignment.set_state(event.state)
                if event.current is not None and event.total:
                    self.transfer_progress.configure(value=100 * event.current / event.total)
                elif event.state in STATE_PROGRESS:
                    self.transfer_progress.configure(value=STATE_PROGRESS[event.state])
                if event.kind in {"done", "cancelled", "error", "disconnected"}:
                    self._set_busy(False)
                if event.kind == "done":
                    self._record_success()
                    self._filter_items()
                    self._notify(event.text, "success")
                elif event.kind in {"error", "disconnected"}:
                    self.pending_transfer = ""
                    self._notify(event.text, "error")
                elif event.kind == "cancelled":
                    self.pending_transfer = ""
                    self._notify(event.text)
        except queue.Empty:
            pass
        self.after(80, self._poll_events)

    def _on_close(self) -> None:
        self.transfer.cancel()
        self.connection.close()
        self.destroy()
