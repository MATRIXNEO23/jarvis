"""058: finestre e pagine con tasti e campi sempre visibili anche senza schermo intero.

Regola unica per ogni finestra secondaria (Toplevel) di Lumi, applicata alla prima apertura:
- non è mai più grande dell'area utile dello schermo (schermo meno barra delle applicazioni);
- la dimensione minima è quella che serve al contenuto (mai oltre l'area utile), così tasti e
  campi non vengono tagliati rimpicciolendo la finestra;
- sta tutta dentro lo schermo.
Il contenuto più alto dell'area utile resta raggiungibile con lo scorrimento già presente nelle
pagine (tela con barra); `fuori_area` serve al test automatico a 1366x768."""
from __future__ import annotations

import tkinter as tk

MARGINE_X = 16          # pixel lasciati ai lati
MARGINE_Y = 72          # barra di Windows + barra del titolo
MINIMO = (320, 200)


def area_utile(window, schermo=None):
    larghezza, altezza = schermo or (window.winfo_screenwidth(), window.winfo_screenheight())
    return max(MINIMO[0], larghezza - MARGINE_X), max(MINIMO[1], altezza - MARGINE_Y)


def adatta(window, schermo=None) -> bool:
    """Applica la regola; True se ha cambiato qualcosa. Sicura da richiamare più volte."""
    if getattr(window, "_lumi_adattata", False) or isinstance(window, tk.Tk):
        return False
    try:
        if window.overrideredirect():
            return False
        window.update_idletasks()
        utile_l, utile_a = area_utile(window, schermo)
        richiesta = (window.winfo_reqwidth(), window.winfo_reqheight())
        minimo = (min(utile_l, max(MINIMO[0], richiesta[0])),
                  min(utile_a, max(MINIMO[1], richiesta[1])))
        window.minsize(*minimo)
        larghezza = min(utile_l, max(window.winfo_width(), minimo[0]))
        altezza = min(utile_a, max(window.winfo_height(), minimo[1]))
        schermo_l, schermo_a = schermo or (window.winfo_screenwidth(), window.winfo_screenheight())
        x = min(max(0, window.winfo_x()), max(0, schermo_l - larghezza))
        y = min(max(0, window.winfo_y()), max(0, schermo_a - MARGINE_Y // 2 - altezza))
        window.geometry("%dx%d+%d+%d" % (larghezza, altezza, x, y))
        window._lumi_adattata = True
        return True
    except tk.TclError:
        return False
