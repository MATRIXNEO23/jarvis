"""Icone del meteo disegnate sul canvas dell'HUD: stilizzate, piene, senza riquadro.

Sole, sole con nuvola, nuvola, pioggia, temporale, neve, nebbia e luna di notte con la fase
lunare (calcolata qui, senza rete). `disegna` mette l'icona centrata in (x, y), alta ~28 px."""
from __future__ import annotations

import math
from datetime import datetime, timezone

CATEGORIE = ("sole", "sole_nuvola", "nuvola", "pioggia", "temporale", "neve", "nebbia", "luna")

SOLE = "#ffc933"
NUVOLA = "#bfeeff"
NUVOLA_SCURA = "#8fb8cc"
PIOGGIA = "#46ccfa"
FULMINE = "#ffd24a"
NEVE = "#ffffff"
LUNA = "#ece9c0"
LUNA_OMBRA = "#1b3a55"
try:
    from hud_reference import BG as SFONDO       # sfondo dell'HUD: copre il sole dietro la nuvola
except ImportError:                              # pragma: no cover
    SFONDO = "#020d17"

MESE_SINODICO = 29.530588853                     # giorni
_LUNA_NUOVA = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)


def fase_lunare(quando: datetime | None = None) -> float:
    """Fase in [0, 1): 0 luna nuova, 0.25 primo quarto, 0.5 piena, 0.75 ultimo quarto."""
    quando = quando or datetime.now(timezone.utc)
    if quando.tzinfo is None:
        quando = quando.replace(tzinfo=timezone.utc)
    giorni = (quando - _LUNA_NUOVA).total_seconds() / 86400.0
    return (giorni % MESE_SINODICO) / MESE_SINODICO


def punti_luce(fase: float, r: float, x: float, y: float, passi: int = 24):
    """Poligono della parte illuminata della luna (vuoto con luna nuova)."""
    fase %= 1.0
    k = r * math.cos(2 * math.pi * fase)          # r = nuova, -r = piena
    verso = 1 if fase < 0.5 else -1               # crescente: luce a destra
    arco = [(verso * r * math.sin(t), -r * math.cos(t))
            for t in (math.pi * i / passi for i in range(passi + 1))]
    termine = [(verso * k * math.sin(t), -r * math.cos(t))
               for t in (math.pi * i / passi for i in range(passi, -1, -1))]
    return [(x + px, y + py) for px, py in arco + termine]


def _nuvola(c, x, y, colore, s=1.0, tratto=2):
    """Nuvola a contorno (come l'anteprima 057): un unico profilo, interno vuoto."""
    pts = [(-11, 8), (-12, 3), (-8, -1), (-6, -6), (0, -8), (5, -5), (7, -2), (11, 0), (12, 5), (9, 8)]
    flat = [v for px, py in pts for v in (x + px * s, y + py * s)]
    c.create_line(*flat, fill=colore, width=tratto, smooth=True, capstyle="round", joinstyle="round")
    c.create_line(x - 11 * s, y + 8 * s, x + 9 * s, y + 8 * s, fill=colore, width=tratto, capstyle="round")


def _sole(c, x, y, r=6, raggi=True):
    c.create_oval(x - r, y - r, x + r, y + r, fill="", outline=SOLE, width=2)
    if raggi:
        for i in range(8):
            a = math.pi / 4 * i
            c.create_line(x + math.cos(a) * (r + 3), y + math.sin(a) * (r + 3),
                          x + math.cos(a) * (r + 6), y + math.sin(a) * (r + 6),
                          fill=SOLE, width=2, capstyle="round")


def _luna(c, x, y, fase, r=9):
    """Luna piena di colore chiaro; la parte in ombra non si disegna (come l'anteprima)."""
    pts = punti_luce(fase, r, x, y)
    if len(pts) >= 6 and max(abs(p[0] - x) for p in pts) > 0.5:
        c.create_polygon(*[v for p in pts for v in p], fill=LUNA, outline="")


def disegna(canvas, x: float, y: float, categoria: str, colore: str = "#46ccfa",
            fase: float | None = None) -> None:
    c = canvas
    if categoria == "sole":
        _sole(c, x, y, 6)
    elif categoria == "sole_nuvola":
        _sole(c, x - 6, y - 6, 4)
        c.create_oval(x - 4, y - 2, x + 12, y + 10, fill=SFONDO, outline="")
        _nuvola(c, x + 3, y + 3, NUVOLA, .75, 2)
    elif categoria == "luna":
        _luna(c, x, y, fase_lunare() if fase is None else fase)
    elif categoria == "nebbia":
        for dy in (-8, -3, 2, 7):
            c.create_line(x - 11, y + dy, x + 11, y + dy, fill=NUVOLA_SCURA, width=2, capstyle="round")
    elif categoria in ("pioggia", "temporale", "neve"):
        _nuvola(c, x, y - 6, NUVOLA, .9)
        if categoria == "pioggia":
            for dx in (-6, 0, 6):
                c.create_line(x + dx + 1, y + 5, x + dx - 2, y + 12, fill=PIOGGIA, width=2,
                              capstyle="round")
        elif categoria == "neve":
            for dx in (-6, 0, 6):
                c.create_text(x + dx, y + 10, text="*", fill=NEVE, font=("Consolas", 9, "bold"))
        else:
            c.create_polygon(x + 2, y + 1, x - 4, y + 9, x - 1, y + 9, x - 3, y + 15,
                             x + 5, y + 6, x + 1, y + 6, x + 4, y + 1, fill=FULMINE, outline="")
    else:                                                  # nuvola e categorie sconosciute
        _nuvola(c, x, y - 1, NUVOLA)
