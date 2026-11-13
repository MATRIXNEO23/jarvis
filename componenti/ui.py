"""Finestre per installare i componenti da dentro Lumi (niente .bat da lanciare).

- ComponentsWindow: elenco con spunte, «Installa selezionati», registro dell'avanzamento.
  Compare al primo avvio e si riapre da Gestisci add-on > «Installa componenti...».
- RequirementsPanel: nella sezione di un add-on, i suoi componenti e chiavi API,
  ognuno con stato, link ufficiale modificabile, «Apri link» e «Installa».
Ogni installazione chiede conferma; i comandi girano in un thread separato.
"""
from __future__ import annotations

import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from . import catalog


def run_install(item, log, done) -> None:
    """Esegue i comandi dell'elemento in un thread; log(riga) e done(ok) dal thread
    vanno riportati nel thread grafico dal chiamante (after)."""
    def worker():
        ok = True
        flags = 0x08000000 if sys.platform == "win32" else 0       # niente finestra nera
        for command in catalog.install_commands(item):
            log("> " + " ".join(command[:6]) + (" …" if len(command) > 6 else ""))
            try:
                proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        stdin=subprocess.DEVNULL, cwd=str(catalog.ROOT),
                                        creationflags=flags)
                for raw in proc.stdout:
                    line = raw.decode("utf-8", "replace").rstrip()
                    if line.strip():
                        log(line[:200])
                code = proc.wait(timeout=1800)
            except (OSError, subprocess.SubprocessError) as exc:
                log("Errore: " + str(exc)[:160])
                ok = False
                break
            if code != 0:
                log(f"Comando terminato con codice {code}.")
                ok = False
                break
        done(ok)
    threading.Thread(target=worker, daemon=True, name="lumi-installa-" + item["id"]).start()


def confirm_install(parent, item) -> bool:
    lines = [f"Installo {item['name']}?", "", item["purpose"]]
    if item["kind"] == "winget":
        lines.append("Scarico dal sito ufficiale tramite Gestione pacchetti di Windows; "
                     "Windows può chiedere il permesso di amministratore.")
    elif "pip" in item["kind"]:
        lines.append("Scarico il pacchetto Python ufficiale (PyPI) per il tuo utente.")
    else:
        lines.append("Uso il programma di installazione incluso in Lumi (scarica da internet).")
    if item.get("online"):
        lines.append("Nota: questo componente usa un servizio online quando lo usi.")
    return messagebox.askyesno("Installa componente", "\n".join(lines), parent=parent)


class ComponentsWindow:
    def __init__(self, parent, on_close=None):
        self.on_close = on_close or (lambda: None)
        self.window = tk.Toplevel(parent)
        self.window.title("LUMI // Installa componenti")
        self.window.geometry("760x560")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        frame = ttk.Frame(self.window, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Componenti facoltativi", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(frame, wraplength=720, text=(
            "Spunta quello che vuoi e premi «Installa selezionati»: Lumi li installa da sola, "
            "senza file .bat. Quelli già presenti sono segnati. Puoi riaprire questa finestra "
            "da Gestisci add-on > «Installa componenti...».")).pack(anchor="w", pady=(2, 8))
        self.rows = ttk.Frame(frame)
        self.rows.pack(fill="x")
        self.checks = {}
        self.states = {}
        bar = ttk.Frame(frame)
        bar.pack(fill="x", pady=(8, 4))
        self.install_button = ttk.Button(bar, text="Installa selezionati", command=self.install)
        self.install_button.pack(side="left")
        ttk.Button(bar, text="Ricontrolla", command=self.fill).pack(side="left", padx=6)
        ttk.Button(bar, text="Chiudi", command=self.close).pack(side="right")
        self.log = tk.Text(frame, height=12, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True)
        self.queue = []
        self.fill()

    def fill(self):
        for child in self.rows.winfo_children():
            child.destroy()
        names = {"base": "Lumi", "telegram": "Telegram", "musica": "Musica"}
        for index, item in enumerate(catalog.COMPONENTS):
            present = catalog.is_installed(item)
            var = tk.BooleanVar(value=False)
            box = ttk.Checkbutton(self.rows, variable=var, text=item["name"])
            box.grid(row=index, column=0, sticky="w")
            if present:
                box.state(["disabled"])
            ttk.Label(self.rows, text=names.get(item["addon"], item["addon"])).grid(
                row=index, column=1, sticky="w", padx=8)
            ttk.Label(self.rows, text="✓ presente" if present else "manca").grid(
                row=index, column=2, sticky="w", padx=8)
            ttk.Label(self.rows, text=item["purpose"], wraplength=330).grid(
                row=index, column=3, sticky="w")
            self.checks[item["id"]] = var

    def write(self, text):
        def add():
            try:
                self.log.configure(state="normal")
                self.log.insert("end", text + "\n")
                self.log.see("end")
                self.log.configure(state="disabled")
            except tk.TclError:
                pass
        self.window.after(0, add)

    def install(self):
        chosen = [catalog.by_id(i) for i, v in self.checks.items() if v.get()]
        # Ordine del catalogo: Node.js prima del modulo GPT.
        chosen = [c for c in catalog.COMPONENTS if c in chosen]
        if not chosen:
            self.write("Nessun componente spuntato.")
            return
        names = "\n".join("• " + c["name"] for c in chosen)
        if not messagebox.askyesno("Installa componenti",
                                   "Installo questi componenti?\n\n" + names +
                                   "\n\nScarico dai siti ufficiali; Windows può chiedere "
                                   "il permesso di amministratore.", parent=self.window):
            return
        self.queue = chosen
        self.install_button.state(["disabled"])
        self._next()

    def _next(self):
        if not self.queue:
            self.write("Fine. Se un componente chiede di riavviare Lumi, chiudila e riaprila.")
            self.install_button.state(["!disabled"])
            self.fill()
            return
        item = self.queue.pop(0)
        reason = catalog.can_install_here(item)
        if reason:
            # Es. Node.js appena installato: serve riavviare Lumi prima del modulo GPT.
            self.write(f"{item['name']}: {reason} " + (
                "(se l'hai appena installato, riavvia Lumi e riprova)"
                if reason.startswith("Prima installa") else catalog.link_for(item)))
            self.window.after(0, self._next)
            return
        self.write(f"--- {item['name']} ---")

        def done(ok):
            message = ("installato." if ok else "NON installato: vedi le righe sopra o usa il link "
                       + catalog.link_for(item))
            if ok and item.get("restart"):
                message += " Riavvia Lumi per usarlo."
            self.write(f"{item['name']}: {message}")
            self.window.after(0, self._next)
        run_install(item, self.write, done)

    def close(self):
        try:
            state = catalog.load_state()
            state["wizard_shown"] = True
            catalog.save_state(state)
        except OSError:
            pass
        self.window.destroy()
        self.on_close()

    def exists(self):
        try:
            return bool(self.window.winfo_exists())
        except tk.TclError:
            return False


class RequirementsPanel(ttk.Frame):
    """Componenti e chiavi API di un add-on, nella sua sezione."""

    def __init__(self, parent, addon_id):
        super().__init__(parent)
        self.addon_id = addon_id
        self.status = tk.StringVar()
        self.fill()

    def fill(self):
        for child in self.winfo_children():
            child.destroy()
        components = catalog.for_addon(self.addon_id)
        keys = catalog.keys_for_addon(self.addon_id)
        if not components and not keys:
            ttk.Label(self, text="Non serve installare altro.").pack(anchor="w")
            return
        state = catalog.load_state()
        grid = ttk.Frame(self)
        grid.pack(fill="x")
        row = 0
        for item in components:
            present = catalog.is_installed(item)
            ttk.Label(grid, text=item["name"], font=("Segoe UI", 9, "bold")).grid(
                row=row, column=0, sticky="w")
            ttk.Label(grid, text="✓ presente" if present else "manca").grid(
                row=row, column=1, sticky="w", padx=6)
            link = tk.StringVar(value=catalog.link_for(item, state))
            ttk.Entry(grid, textvariable=link, width=42).grid(row=row, column=2, sticky="w")
            ttk.Button(grid, text="Salva link", command=lambda i=item, v=link: self._save_link(i, v)
                       ).grid(row=row, column=3, padx=2)
            ttk.Button(grid, text="Apri link", command=lambda v=link: webbrowser.open(v.get())
                       ).grid(row=row, column=4, padx=2)
            install = ttk.Button(grid, text="Installa", command=lambda i=item: self._install(i))
            install.grid(row=row, column=5, padx=2)
            if present:
                install.state(["disabled"])
            ttk.Label(grid, text=item["purpose"], wraplength=560).grid(
                row=row + 1, column=0, columnspan=6, sticky="w", pady=(0, 4))
            row += 2
        for key in keys:
            ttk.Label(grid, text=key["name"], font=("Segoe UI", 9, "bold")).grid(
                row=row, column=0, sticky="w")
            link = tk.StringVar(value=catalog.link_for(key, state))
            ttk.Entry(grid, textvariable=link, width=42).grid(row=row, column=2, sticky="w")
            ttk.Button(grid, text="Salva link", command=lambda i=key, v=link: self._save_link(i, v)
                       ).grid(row=row, column=3, padx=2)
            ttk.Button(grid, text="Crea la chiave", command=lambda v=link: webbrowser.open(v.get())
                       ).grid(row=row, column=4, columnspan=2, padx=2, sticky="w")
            ttk.Label(grid, wraplength=560, text=key["purpose"] + " Poi inseriscila in: " +
                      key["where"] + ". Come fare: F1 > Chiavi API.").grid(
                row=row + 1, column=0, columnspan=6, sticky="w", pady=(0, 4))
            row += 2
        ttk.Label(self, textvariable=self.status, wraplength=600).pack(anchor="w")

    def _save_link(self, item, var):
        try:
            self.status.set(catalog.set_link(item["id"], var.get()))
        except OSError as exc:
            self.status.set("Non salvato: " + str(exc)[:80])
        self.fill()

    def _install(self, item):
        reason = catalog.can_install_here(item)
        if reason:
            self.status.set(reason)
            return
        if not confirm_install(self, item):
            return
        self.status.set("Installo " + item["name"] + "…")

        def log(line):
            self.after(0, lambda: self.status.set(line[-160:]))

        def done(ok):
            def finish():
                text = (item["name"] + (" installato." if ok else " NON installato: usa «Apri link»."))
                if ok and item.get("restart"):
                    text += " Riavvia Lumi per usarlo."
                self.fill()
                self.status.set(text)
            self.after(0, finish)
        run_install(item, log, done)
