"""Pagina «Ricordi» in Impostazioni → Memoria (15/11 sera): casella di ricerca (i risultati
compaiono mentre scrivi), ricordi divisi per categoria come cartelle, suggerimenti su come
cercare, dettagli del ricordo scelto e «Cancella»."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ricordi import CATEGORIE

SUGGERIMENTI = ("Scrivi una parola: bastano le prime lettere («progett» trova progetto e "
                "progetti). Apri una cartella per vedere solo quella categoria. "
                "Puoi anche dire «ricordati che …» e, subito dopo un salvataggio, «cancellalo».")


class PaginaRicordi:
    def __init__(self, parent, get_brain, *, confirm, after=None):
        self.get_brain = get_brain
        self.confirm = confirm
        self.after = after or (lambda ms, fn: parent.after(ms, fn))
        self.box = ttk.LabelFrame(parent, text="Ricordi", padding=10)
        self.box.pack(fill="x", pady=(0, 8))
        top = ttk.Frame(self.box)
        top.pack(fill="x")
        ttk.Label(top, text="Cerca:").pack(side="left")
        self.query = tk.StringVar(master=self.box)
        entry = ttk.Entry(top, textvariable=self.query)
        entry.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(top, text="Cancella", command=self.cancella).pack(side="right")
        ttk.Label(self.box, text=SUGGERIMENTI, wraplength=620, foreground="#7f9fb3").pack(
            anchor="w", pady=(4, 4))
        self.tree = ttk.Treeview(self.box, show="tree", height=10, selectmode="browse")
        self.tree.pack(fill="x")
        self.detail = tk.StringVar(master=self.box, value="")
        ttk.Label(self.box, textvariable=self.detail, wraplength=620, justify="left").pack(
            anchor="w", pady=(6, 0))
        self.rows = {}
        self._job = None
        self.query.trace_add("write", lambda *_: self._later())
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._show())
        self.box.bind("<Map>", lambda _e: self.aggiorna())      # nuovi ricordi quando la apri
        self.aggiorna()

    def _later(self):
        if self._job is not None:
            return
        def run():
            self._job = None
            self.aggiorna()
        self._job = True
        self.after(200, run)

    def aggiorna(self):
        self.tree.delete(*self.tree.get_children())
        self.rows = {}
        brain = self.get_brain()
        if brain is None:
            self.detail.set("Second Brain spento: accendilo in «Second Brain» per salvare ricordi.")
            return
        try:
            items = brain.ricordi(self.query.get(), limit=500)
        except Exception as exc:
            self.detail.set("Ricordi non leggibili: " + str(exc)[:100])
            return
        searching = bool(self.query.get().strip())
        for key, label in CATEGORIE.items():
            group = [item for item in items if item["categoria"] == key]
            node = self.tree.insert("", "end", text="📁 %s (%d)" % (label, len(group)),
                                    open=searching and bool(group))
            for item in group:
                iid = self.tree.insert(node, "end", text=item["breve"])
                self.rows[iid] = item
        self.detail.set("%d ricordi%s." % (len(items), " trovati" if searching else ""))

    def _show(self):
        item = self.rows.get(self.tree.focus())
        if item is None:
            return
        who = {"online": "dal modello online", "gemma": "da Gemma (confermato)",
               "utente": "da te"}.get(item["fonte"], "")
        self.detail.set("%s\nCompleto: %s\nSalvato %s il %s." % (
            item["breve"], item["completo"], who, item["quando"][:16].replace("T", " ")))

    def cancella(self):
        item = self.rows.get(self.tree.focus())
        brain = self.get_brain()
        if item is None or brain is None:
            self.detail.set("Scegli prima un ricordo nell'elenco.")
            return
        if not self.confirm("Cancella ricordo", "Cancellare «%s»?" % item["breve"]):
            return
        try:
            brain.cancella_ricordo(item["id"])
        except Exception as exc:
            self.detail.set("Non cancellato: " + str(exc)[:100])
            return
        self.aggiorna()
