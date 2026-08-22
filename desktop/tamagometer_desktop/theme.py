"""Tk/ttk visual theme for Tamagometer Desktop."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


BG = "#F3F5FA"
CARD = "#FFFFFF"
INK = "#182230"
MUTED = "#667085"
ACCENT = "#6757D9"
ACCENT_HOVER = "#5748C5"
ACCENT_SOFT = "#EEEAFE"
BORDER = "#E3E7EF"
LOG_BG = "#101828"


def configure_theme(root: tk.Tk) -> None:
    root.configure(bg=BG)
    root.option_add("*Font", ("Segoe UI", 10))
    root.option_add("*selectBackground", ACCENT)
    root.option_add("*selectForeground", "white")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("App.TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("Hero.TFrame", background=ACCENT)
    style.configure("TLabel", background=BG, foreground=INK)
    style.configure("Card.TLabel", background=CARD, foreground=INK)
    style.configure(
        "HeroTitle.TLabel",
        background=ACCENT,
        foreground="white",
        font=("Segoe UI Semibold", 23),
    )
    style.configure(
        "HeroText.TLabel",
        background=ACCENT,
        foreground="#E8E5FF",
        font=("Segoe UI", 10),
    )
    style.configure(
        "Section.TLabel",
        background=CARD,
        foreground=INK,
        font=("Segoe UI Semibold", 12),
    )
    style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
    style.configure(
        "Selected.TLabel",
        background=CARD,
        foreground=ACCENT,
        font=("Segoe UI Semibold", 9),
    )
    style.configure(
        "Status.TLabel",
        background=ACCENT_SOFT,
        foreground=ACCENT,
        font=("Segoe UI Semibold", 9),
        padding=(10, 5),
    )
    style.configure(
        "TButton",
        background="#F8F9FC",
        foreground=INK,
        bordercolor=BORDER,
        padding=(12, 8),
        relief="flat",
    )
    style.map(
        "TButton",
        background=[("active", "#EEF1F6"), ("disabled", "#F5F6F8")],
        foreground=[("disabled", "#98A2B3")],
    )
    style.configure(
        "Primary.TButton",
        background=ACCENT,
        foreground="white",
        bordercolor=ACCENT,
        padding=(16, 10),
        font=("Segoe UI Semibold", 10),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_HOVER), ("disabled", "#B7B0E8")],
        foreground=[("disabled", "#F4F2FF")],
    )
    style.configure(
        "Mode.TRadiobutton",
        background=CARD,
        foreground=MUTED,
        indicatorcolor=CARD,
        padding=(13, 8),
        font=("Segoe UI Semibold", 9),
    )
    style.map(
        "Mode.TRadiobutton",
        background=[("selected", ACCENT_SOFT), ("active", "#F7F5FF")],
        foreground=[("selected", ACCENT), ("active", ACCENT)],
        indicatorcolor=[("selected", ACCENT_SOFT)],
    )
    style.configure(
        "TCombobox",
        fieldbackground="#F9FAFB",
        background="#F9FAFB",
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=7,
    )
    style.configure(
        "Search.TEntry",
        fieldbackground="#F9FAFB",
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        padding=8,
    )
    style.configure(
        "Horizontal.TProgressbar",
        background=ACCENT,
        troughcolor=ACCENT_SOFT,
        bordercolor=ACCENT_SOFT,
        lightcolor=ACCENT,
        darkcolor=ACCENT,
        thickness=8,
    )
    style.configure(
        "Gift.Treeview",
        background=CARD,
        fieldbackground=CARD,
        foreground=INK,
        rowheight=34,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Gift.Treeview.Heading",
        background="#F8F9FC",
        foreground=MUTED,
        relief="flat",
        font=("Segoe UI Semibold", 9),
        padding=(7, 7),
    )
    style.map(
        "Gift.Treeview",
        background=[("selected", ACCENT_SOFT)],
        foreground=[("selected", ACCENT)],
    )


def card(parent, padding=(18, 16)) -> ttk.Frame:
    return ttk.Frame(parent, style="Card.TFrame", padding=padding)
