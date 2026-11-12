"""Numeri sopra gli elementi della finestra («mostra i numeri»): una finestrella
trasparente sempre in primo piano con un'etichetta per elemento. Sparisce da sola
dopo 40 secondi, con «nascondi i numeri» o dopo una scelta."""
from __future__ import annotations

import tkinter as tk

_STATE = {"window": None, "job": None}
KEY = "#010203"


def hide(root) -> None:
    window, _STATE["window"] = _STATE["window"], None
    if _STATE["job"] is not None:
        try:
            root.after_cancel(_STATE["job"])
        except tk.TclError:
            pass
        _STATE["job"] = None
    if window is not None:
        try:
            window.destroy()
        except tk.TclError:
            pass


def show(root, items) -> None:
    hide(root)
    if not items:
        return
    window = tk.Toplevel(root)
    window.overrideredirect(True)
    window.configure(bg=KEY)
    try:
        window.attributes("-topmost", True)
        window.attributes("-transparentcolor", KEY)
    except tk.TclError:
        pass
    left = min(i["x"] for i in items) - 30
    top = min(i["y"] for i in items) - 30
    right = max(i["x"] + i["w"] for i in items) + 30
    bottom = max(i["y"] + i["h"] for i in items) + 30
    window.geometry(f"{right - left}x{bottom - top}+{left}+{top}")
    canvas = tk.Canvas(window, bg=KEY, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)
    for number, item in enumerate(items, start=1):
        x, y = item["x"] - left, item["y"] - top
        label = str(number)
        width = 8 + 8 * len(label)
        canvas.create_rectangle(x, y, x + width, y + 18, fill="#ffd400", outline="#000000")
        canvas.create_text(x + width / 2, y + 9, text=label, fill="#000000",
                           font=("Segoe UI", 10, "bold"))
    _STATE["window"] = window
    _STATE["job"] = root.after(40000, lambda: hide(root))


# --- griglia a 9 caselle («griglia», poi un numero, poi «clicca») ------------------------
_GRID = {"window": None, "job": None}


def hide_grid(root) -> None:
    window, _GRID["window"] = _GRID["window"], None
    if _GRID["job"] is not None:
        try:
            root.after_cancel(_GRID["job"])
        except tk.TclError:
            pass
        _GRID["job"] = None
    if window is not None:
        try:
            window.destroy()
        except tk.TclError:
            pass


def grid(root, rect) -> None:
    """rect = (x, y, larghezza, altezza) dell'area da dividere in 3×3; None la chiude."""
    hide_grid(root)
    if not rect:
        return
    x, y, w, h = (int(v) for v in rect)
    window = tk.Toplevel(root)
    window.overrideredirect(True)
    window.configure(bg=KEY)
    try:
        window.attributes("-topmost", True)
        window.attributes("-transparentcolor", KEY)
    except tk.TclError:
        pass
    window.geometry(f"{max(w, 6)}x{max(h, 6)}+{x}+{y}")
    canvas = tk.Canvas(window, bg=KEY, highlightthickness=0, bd=0)
    canvas.pack(fill="both", expand=True)
    for i in range(4):
        cx = min(w - 1, i * w // 3)
        cy = min(h - 1, i * h // 3)
        canvas.create_line(cx, 0, cx, h, fill="#ffd400", width=2)
        canvas.create_line(0, cy, w, cy, fill="#ffd400", width=2)
    size = 16 if min(w, h) >= 150 else 10
    if min(w, h) >= 45:
        for number in range(1, 10):
            col, row = (number - 1) % 3, (number - 1) // 3
            tx, ty = col * w // 3 + w // 6, row * h // 3 + h // 6
            canvas.create_rectangle(tx - size, ty - size, tx + size, ty + size,
                                    fill="#ffd400", outline="#000000")
            canvas.create_text(tx, ty, text=str(number), fill="#000000",
                               font=("Segoe UI", max(8, size - 2), "bold"))
    _GRID["window"] = window
    _GRID["job"] = root.after(90000, lambda: hide_grid(root))


# --- striscia con i comandi del momento («mostra i comandi» / «nascondi i comandi») ---------
_STRIP = {"window": None}


def strip(root, text) -> None:
    window, _STRIP["window"] = _STRIP["window"], None
    if window is not None:
        try:
            window.destroy()
        except tk.TclError:
            pass
    if not text:
        return
    window = tk.Toplevel(root)
    window.overrideredirect(True)
    try:
        window.attributes("-topmost", True)
        window.attributes("-alpha", 0.92)
    except tk.TclError:
        pass
    label = tk.Label(window, text=str(text)[:700], justify="left", anchor="w", bg="#101820",
                     fg="#ffd400", font=("Segoe UI", 10), padx=10, pady=8, wraplength=360)
    label.pack()
    window.update_idletasks()
    x = window.winfo_screenwidth() - window.winfo_reqwidth() - 12
    window.geometry(f"+{max(0, x)}+60")
    _STRIP["window"] = window
