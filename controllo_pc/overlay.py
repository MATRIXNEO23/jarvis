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
