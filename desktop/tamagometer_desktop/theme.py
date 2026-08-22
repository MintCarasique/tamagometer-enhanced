"""Light and dark ttk themes for Tamagometer Desktop."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


PALETTES = {
    "light": {
        "bg": "#F3F5FA",
        "card": "#FFFFFF",
        "ink": "#182230",
        "muted": "#667085",
        "accent": "#6757D9",
        "accent_hover": "#5748C5",
        "accent_soft": "#EEEAFE",
        "border": "#E3E7EF",
        "field": "#F9FAFB",
        "log_bg": "#101828",
        "log_fg": "#D0D5DD",
        "success": "#067647",
        "success_bg": "#ECFDF3",
        "error": "#B42318",
        "error_bg": "#FEF3F2",
    },
    "dark": {
        "bg": "#0B1020",
        "card": "#151B2B",
        "ink": "#F2F4F7",
        "muted": "#98A2B3",
        "accent": "#9B8CFF",
        "accent_hover": "#B4A9FF",
        "accent_soft": "#29234A",
        "border": "#344054",
        "field": "#1D2435",
        "log_bg": "#070B14",
        "log_fg": "#D0D5DD",
        "success": "#75E0A7",
        "success_bg": "#12372A",
        "error": "#FDA29B",
        "error_bg": "#471B1B",
    },
}


def get_palette(theme: str) -> dict[str, str]:
    return PALETTES.get(theme, PALETTES["light"])


def configure_theme(root: tk.Tk, theme: str = "light") -> dict[str, str]:
    palette = get_palette(theme)
    root.configure(bg=palette["bg"])
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*selectBackground", palette["accent"])
    root.option_add("*selectForeground", "white")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("App.TFrame", background=palette["bg"])
    style.configure("Card.TFrame", background=palette["card"])
    style.configure("Hero.TFrame", background=palette["accent"])
    style.configure("TLabel", background=palette["bg"], foreground=palette["ink"])
    style.configure("Card.TLabel", background=palette["card"], foreground=palette["ink"])
    style.configure(
        "HeroTitle.TLabel", background=palette["accent"], foreground="white",
        font=("Segoe UI Semibold", 23),
    )
    style.configure(
        "HeroText.TLabel", background=palette["accent"], foreground="#E8E5FF",
        font=("Segoe UI", 10),
    )
    style.configure(
        "Section.TLabel", background=palette["card"], foreground=palette["ink"],
        font=("Segoe UI Semibold", 12),
    )
    style.configure(
        "Muted.TLabel", background=palette["card"], foreground=palette["muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "Selected.TLabel", background=palette["card"], foreground=palette["accent"],
        font=("Segoe UI Semibold", 9),
    )
    style.configure(
        "Status.TLabel", background=palette["accent_soft"], foreground=palette["accent"],
        font=("Segoe UI Semibold", 9), padding=(10, 5),
    )
    style.configure(
        "Notice.TLabel", background=palette["accent_soft"], foreground=palette["accent"],
        padding=(14, 9), font=("Segoe UI Semibold", 9),
    )
    style.configure(
        "Success.Notice.TLabel", background=palette["success_bg"],
        foreground=palette["success"], padding=(14, 9), font=("Segoe UI Semibold", 9),
    )
    style.configure(
        "Error.Notice.TLabel", background=palette["error_bg"],
        foreground=palette["error"], padding=(14, 9), font=("Segoe UI Semibold", 9),
    )
    style.configure(
        "TButton", background=palette["field"], foreground=palette["ink"],
        bordercolor=palette["border"], padding=(12, 8), relief="flat",
    )
    style.map(
        "TButton", background=[("active", palette["accent_soft"]), ("disabled", palette["card"])],
        foreground=[("disabled", palette["muted"])],
    )
    style.configure(
        "Primary.TButton", background=palette["accent"], foreground="white",
        bordercolor=palette["accent"], padding=(16, 10), font=("Segoe UI Semibold", 10),
    )
    style.map(
        "Primary.TButton", background=[("active", palette["accent_hover"]), ("disabled", palette["muted"])],
        foreground=[("disabled", palette["card"])],
    )
    style.configure(
        "Mode.TRadiobutton", background=palette["card"], foreground=palette["muted"],
        indicatorcolor=palette["card"], padding=(13, 8), font=("Segoe UI Semibold", 9),
    )
    style.map(
        "Mode.TRadiobutton", background=[("selected", palette["accent_soft"]), ("active", palette["accent_soft"])],
        foreground=[("selected", palette["accent"]), ("active", palette["accent"])],
        indicatorcolor=[("selected", palette["accent_soft"])],
    )
    style.configure(
        "TCombobox", fieldbackground=palette["field"], background=palette["field"],
        foreground=palette["ink"], bordercolor=palette["border"],
        lightcolor=palette["border"], darkcolor=palette["border"], padding=7,
    )
    style.configure(
        "Search.TEntry", fieldbackground=palette["field"], foreground=palette["ink"],
        bordercolor=palette["border"], lightcolor=palette["border"],
        darkcolor=palette["border"], padding=8,
    )
    style.configure(
        "Horizontal.TProgressbar", background=palette["accent"],
        troughcolor=palette["accent_soft"], bordercolor=palette["accent_soft"],
        lightcolor=palette["accent"], darkcolor=palette["accent"], thickness=8,
    )
    style.configure(
        "Gift.Treeview", background=palette["card"], fieldbackground=palette["card"],
        foreground=palette["ink"], rowheight=38, borderwidth=0, font=("Segoe UI", 10),
    )
    style.configure(
        "Gift.Treeview.Heading", background=palette["field"], foreground=palette["muted"],
        relief="flat", font=("Segoe UI Semibold", 9), padding=(7, 7),
    )
    style.map(
        "Gift.Treeview", background=[("selected", palette["accent_soft"])],
        foreground=[("selected", palette["accent"])],
    )
    return palette


def card(parent, padding=(18, 16)) -> ttk.Frame:
    return ttk.Frame(parent, style="Card.TFrame", padding=padding)
