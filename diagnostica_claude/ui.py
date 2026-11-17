"""Riquadro «Diagnostica per Claude» nelle Impostazioni (spento di serie)."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def configurazione_claude(python: str | None = None) -> str:
    """Testo da incollare in claude_desktop_config.json."""
    server = Path(__file__).with_name("server_mcp.py").resolve()
    return json.dumps({"mcpServers": {"lumi-diagnostica": {
        "command": python or sys.executable, "args": [str(server)]}}}, indent=2)


def configurazione_codex(python: str | None = None) -> str:
    """Blocco TOML per config.toml di Codex: stessi command e args, apici singoli (le barre
    dei percorsi Windows restano come sono)."""
    server = Path(__file__).with_name("server_mcp.py").resolve()
    return ("[mcp_servers.lumi-diagnostica]\n"
            "command = '%s'\n"
            "args = ['%s']\n"
            "startup_timeout_sec = 30\n"
            "tool_timeout_sec = 120\n") % (python or sys.executable, server)


def percorso_codex() -> Path:
    """config.toml di Codex nel profilo reale di questo PC."""
    return Path.home() / ".codex" / "config.toml"


def costruisci_sezione(parent, notify, make_ponte, *, clipboard):
    import tkinter as tk
    from tkinter import ttk
    box = ttk.LabelFrame(parent, text="Diagnostica per Claude (add-on, spento di serie)")
    box.pack(fill="x", padx=8, pady=8)
    ttk.Label(box, wraplength=540, text=(
        "L'app Claude desktop può leggere console, errori e motore.log di Lumi e provare comandi "
        "solo dentro Lumi (niente Controllo PC, programmi o file). Acceso solo finché c'è la "
        "spunta.")).pack(anchor="w", padx=8, pady=5)
    on = tk.BooleanVar(value=False)
    state = {"ponte": None}

    def toggle():
        if on.get():
            try:
                state["ponte"] = state["ponte"] or make_ponte()
                state["ponte"].avvia()
            except OSError as exc:
                on.set(False)
                notify("DIAGNOSTICA / ERRORE > Ponte non avviato: " + str(exc)[:120])
                return
            notify("DIAGNOSTICA > Diagnostica per Claude accesa (solo su questo PC).")
        elif state["ponte"] is not None:
            state["ponte"].ferma()
            notify("DIAGNOSTICA > Diagnostica per Claude spenta.")

    def copy():
        clipboard(configurazione_claude())
        notify("DIAGNOSTICA > Configurazione copiata: incollala in claude_desktop_config.json "
               "e riavvia Claude.")

    def copy_codex():
        clipboard(configurazione_codex())
        notify("DIAGNOSTICA > Configurazione per Codex copiata: incollala in "
               + str(percorso_codex()) + " e riavvia Codex.")

    ttk.Checkbutton(box, text="Attiva", variable=on, command=toggle).pack(anchor="w", padx=8)
    ttk.Button(box, text="Copia configurazione per Claude desktop", command=copy
               ).pack(anchor="w", padx=8, pady=(2, 6))
    ttk.Button(box, text="Copia configurazione per Codex", command=copy_codex
               ).pack(anchor="w", padx=8, pady=(0, 2))
    ttk.Label(box, wraplength=540, text=(
        "Incolla in " + str(percorso_codex()) + ", riavvia Codex e chiedigli di leggere "
        "docs/audit/ISTRUZIONI-PROVE-CODEX.md")).pack(anchor="w", padx=8, pady=(0, 6))
    box.state = state
    box.var = on
    return box
