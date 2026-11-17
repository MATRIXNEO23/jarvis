"""Icone del meteo disegnate sul canvas dell'HUD (sole, nuvola, pioggia, neve, temporale).

Solo linee e ovali: niente immagini, niente riquadro. `disegna` mette l'icona centrata in (x, y)."""
from __future__ import annotations

CATEGORIE = ("sole", "nuvola", "pioggia", "neve", "temporale")


def _nuvola(c, x, y, colore):
    c.create_oval(x - 11, y - 3, x - 1, y + 7, outline=colore, width=2)
    c.create_oval(x - 6, y - 10, x + 6, y + 2, outline=colore, width=2)
    c.create_oval(x + 1, y - 4, x + 11, y + 7, outline=colore, width=2)
    c.create_line(x - 7, y + 7, x + 7, y + 7, fill=colore, width=2)


def disegna(canvas, x: float, y: float, categoria: str, colore: str = "#46ccfa") -> None:
    c = canvas
    if categoria == "sole":
        c.create_oval(x - 6, y - 6, x + 6, y + 6, outline=colore, width=2)
        for dx, dy in ((0, -11), (0, 11), (-11, 0), (11, 0), (-8, -8), (8, -8), (-8, 8), (8, 8)):
            c.create_line(x + dx * .72, y + dy * .72, x + dx, y + dy, fill=colore, width=2)
        return
    _nuvola(c, x, y - 4, colore)
    if categoria == "pioggia":
        for dx in (-6, 0, 6):
            c.create_line(x + dx, y + 6, x + dx - 2, y + 12, fill=colore, width=2)
    elif categoria == "neve":
        for dx in (-6, 0, 6):
            c.create_text(x + dx, y + 9, text="*", fill=colore, font=("Consolas", 9, "bold"))
    elif categoria == "temporale":
        c.create_polygon(x + 1, y + 3, x - 4, y + 10, x, y + 10, x - 3, y + 16, x + 5, y + 8,
                         x + 1, y + 8, outline=colore, fill=colore)
