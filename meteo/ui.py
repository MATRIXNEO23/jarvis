"""Pagina dell'add-on Meteo in Impostazioni > Add-on: attivo/disattivo sta nella riga standard;
qui solo la città predefinita (la prima volta si sceglie qui)."""
from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk

from . import config
from .service import ErroreMeteo, cerca_citta


def costruisci_sezione(parent, *, notify, on_change, search=cerca_citta, run_async=None):
    run_async = run_async or (lambda fn: threading.Thread(target=fn, daemon=True, name="lumi-meteo-citta").start())
    box = ttk.LabelFrame(parent, text="Città predefinita")
    box.pack(fill="x", pady=(6, 8))
    current = config.load()["citta"]
    ttk.Label(box, wraplength=560, text=(
        "Il meteo nell'HUD (icona, città e temperatura) usa questa città. Quelle che chiedi a voce, "
        "«che tempo fa a Roma» o «meteo domani», funzionano per qualsiasi città. Dati: Open-Meteo, gratuiti e senza chiave."
    )).pack(anchor="w", padx=8, pady=5)
    line = ttk.Frame(box)
    line.pack(fill="x", padx=8, pady=(0, 4))
    name = tk.StringVar(value=current["nome"] if current else "")
    status = tk.StringVar(value=("Città scelta: " + current["nome"]) if current
                          else "Nessuna città scelta: scrivila e premi Salva.")
    entry = ttk.Entry(line, textvariable=name, width=28)
    entry.pack(side="left")

    def save(*_):
        wanted = name.get().strip()
        if not wanted:
            status.set("Scrivi il nome di una città.")
            return
        status.set("Cerco «" + wanted[:40] + "»...")

        def work():
            try:
                city = search(wanted)
                config.save(city)
                message = "Città salvata: " + city["nome"]
            except ErroreMeteo as exc:
                city, message = None, str(exc)
            except OSError as exc:
                city, message = None, "Non riesco a salvare: " + str(exc)[:80]
            try:
                parent.after(0, lambda: (status.set(message), city and on_change()))
            except (tk.TclError, RuntimeError):
                pass
        run_async(work)

    ttk.Button(line, text="Salva", command=save).pack(side="left", padx=6)
    entry.bind("<Return>", save)
    ttk.Label(box, textvariable=status, wraplength=560).pack(anchor="w", padx=8, pady=(0, 6))
    return box
