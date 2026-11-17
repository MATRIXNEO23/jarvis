"""«I miei modelli» (054): elenco dei .gguf, aggiungi, usa, rimuovi, profili 1/2/3.

Nessun doppione con «cambia modello» a voce: l'elenco è scelta_modello.elenca_modelli, il
salvataggio è scelta_modello.salva_scelta (via on_use, che in jarvis.py è la stessa funzione
della scelta a voce, con riavvio del motore) e il Cestino è pulizia_dati.al_cestino.
"""
from __future__ import annotations

import shutil
import threading
from pathlib import Path

from . import profili_famiglia, scelta_modello

CHUNK = 8 * 1024 * 1024


def cartella_modelli(config_path=None) -> Path:
    return scelta_modello.cartelle_modelli(config_path)[-1]


def aggiungi_modello(sorgente, config_path=None, progress=None, cancel=None, chunk=CHUNK) -> Path:
    """Copia un .gguf in addon-data/modello_locale/modelli a blocchi (progress(copiati, totale)),
    con nome temporaneo e rinomina finale: un file a metà non compare mai nell'elenco."""
    source = Path(sorgente)
    if source.suffix.lower() != ".gguf" or not source.is_file():
        raise ValueError("Scegli un file .gguf esistente.")
    if "mmproj" in source.name.casefold():
        raise ValueError("Questo è un proiettore di immagini, non un modello di testo.")
    folder = cartella_modelli(config_path)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / source.name
    if target.exists():
        raise ValueError("C'è già un modello con questo nome.")
    temp = folder / (source.name + ".copia")
    total, done = source.stat().st_size, 0
    try:
        with source.open("rb") as src, temp.open("wb") as dst:
            while True:
                if cancel is not None and cancel():
                    raise ValueError("Copia annullata.")
                block = src.read(chunk)
                if not block:
                    break
                dst.write(block)
                done += len(block)
                if progress is not None:
                    progress(done, total)
        temp.replace(target)
    finally:
        if temp.exists():
            temp.unlink()
    return target


def rimuovi_modello(percorso, config_path=None, al_cestino=None) -> None:
    """Manda il file nel Cestino; mai il modello in uso."""
    target = Path(percorso)
    in_uso = scelta_modello.modello_in_uso(config_path)
    if in_uso and str(target).casefold() == str(Path(in_uso)).casefold():
        raise ValueError("Questo è il modello in uso: scegline un altro prima di rimuoverlo.")
    if al_cestino is None:
        from pulizia_dati import al_cestino
    if not target.is_file():
        raise ValueError("Il file non esiste più.")
    if not al_cestino([target]):
        raise OSError("Non riesco a spostare il file nel Cestino.")


def righe(config_path=None) -> list[tuple[Path, bool]]:
    """(percorso, in_uso) per ogni modello dell'elenco."""
    in_uso = scelta_modello.modello_in_uso(config_path)
    return [(m, bool(in_uso) and str(m).casefold() == str(Path(in_uso)).casefold())
            for m in scelta_modello.elenca_modelli(config_path)]


def costruisci_sezione(parent, notify, *, on_use, config_path=None, ask_file=None, confirm=None,
                       run_async=None, al_cestino=None):
    """Sezione «I miei modelli» (Tk): elenco con il modello in uso evidenziato, «Aggiungi
    modello…» (copia con avanzamento, senza bloccare), «Usa questo», «Rimuovi», e i profili
    1/2/3 della famiglia in uso («Salva in questo profilo», «Ripristina default»)."""
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    ask_file = ask_file or (lambda: filedialog.askopenfilename(
        parent=parent, title="Aggiungi modello", filetypes=[("Modello GGUF", "*.gguf")]))
    confirm = confirm or (lambda text: messagebox.askyesno("Rimuovi modello", text, parent=parent))
    run_async = run_async or (lambda fn: threading.Thread(
        target=fn, daemon=True, name="lumi-aggiungi-modello").start())
    box = ttk.LabelFrame(parent, text="I miei modelli")
    box.pack(fill="x", padx=8, pady=8)
    listbox = tk.Listbox(box, height=6, exportselection=False)
    listbox.pack(fill="x", padx=8, pady=6)
    state = {"rows": []}
    progress = ttk.Progressbar(box, mode="determinate", maximum=100)
    status = tk.StringVar(value="")

    def refresh():
        state["rows"] = righe(config_path)
        listbox.delete(0, "end")
        for index, (path, active) in enumerate(state["rows"]):
            listbox.insert("end", scelta_modello.nome_breve(path) + ("   ← in uso" if active else ""))
            if active:
                listbox.itemconfigure(index, background="#0b2f44", foreground="#46ccfa")

    def selected():
        picked = listbox.curselection()
        return state["rows"][picked[0]][0] if picked else None

    def add():
        source = ask_file()
        if not source:
            return
        progress.pack(fill="x", padx=8)
        state["busy"] = True

        def work():
            def tick(done, total):
                value = int(100 * done / total) if total else 100
                try:
                    parent.after(0, lambda: (progress.configure(value=value),
                                             status.set("Copio il modello… %d%%" % value)))
                except (RuntimeError, tk.TclError):
                    pass
            try:
                target = aggiungi_modello(source, config_path, progress=tick)
                message = "Modello aggiunto: " + scelta_modello.nome_breve(target) + "."
            except (OSError, ValueError) as exc:
                message = "Modello non aggiunto: " + str(exc)[:120]

            def finish():
                progress.pack_forget()
                status.set(message)
                notify("MODELLO LOCALE > " + message)
                refresh()
            try:
                parent.after(0, finish)
            except (RuntimeError, tk.TclError):
                pass
        run_async(work)

    def use():
        target = selected()
        if target is None:
            status.set("Scegli prima un modello dall'elenco.")
            return
        on_use(target)
        refresh()

    def remove():
        target = selected()
        if target is None:
            status.set("Scegli prima un modello dall'elenco.")
            return
        if not confirm("Spostare «%s» nel Cestino?" % scelta_modello.nome_breve(target)):
            return
        try:
            rimuovi_modello(target, config_path, al_cestino)
            status.set("Modello spostato nel Cestino.")
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])
        refresh()

    bar = ttk.Frame(box)
    bar.pack(fill="x", padx=8)
    ttk.Button(bar, text="Aggiungi modello…", command=add).pack(side="left")
    ttk.Button(bar, text="Usa questo", command=use).pack(side="left", padx=4)
    ttk.Button(bar, text="Rimuovi", command=remove).pack(side="left")
    ttk.Label(box, textvariable=status, wraplength=520).pack(anchor="w", padx=8, pady=(4, 0))

    # Profili della famiglia in uso (3 slot).
    prof = ttk.Frame(box)
    prof.pack(fill="x", padx=8, pady=6)
    slot_var = tk.IntVar(value=1)
    family_var = tk.StringVar(value="")

    def family():
        info = profili_famiglia.assicura(config_path)
        family_var.set("Famiglia: %s%s" % (info["famiglia"], "" if info["riconosciuta"] else " (generico)"))
        slot_var.set(info["slot"])
        return info["famiglia"]

    def choose_slot():
        try:
            result = profili_famiglia.scegli_slot(family(), slot_var.get(), config_path)
            status.set("Profilo %d caricato." % slot_var.get() + (
                " Per applicare %s serve riavviare il motore." % ", ".join(result["campi_riavvio"])
                if result["serve_riavvio"] else " Nessun riavvio necessario."))
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])

    def save_slot():
        try:
            profili_famiglia.salva_in_slot(family(), slot_var.get(), config_path)
            status.set("Valori salvati nel profilo %d." % slot_var.get())
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])

    def reset_slot():
        try:
            result = profili_famiglia.ripristina_default(family(), slot_var.get(), config_path)
            status.set("Profilo %d riportato ai valori di fabbrica." % slot_var.get() + (
                " Serve riavviare il motore." if result["serve_riavvio"] else ""))
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])

    ttk.Label(prof, textvariable=family_var).pack(side="left")
    for number in profili_famiglia.SLOT:
        ttk.Radiobutton(prof, text="Profilo %d" % number, value=number, variable=slot_var,
                        command=choose_slot).pack(side="left", padx=4)
    ttk.Button(prof, text="Salva in questo profilo", command=save_slot).pack(side="left", padx=4)
    ttk.Button(prof, text="Ripristina default", command=reset_slot).pack(side="left")
    box.add, box.use, box.remove, box.refresh = add, use, remove, refresh
    box.listbox, box.choose_slot, box.save_slot, box.reset_slot = listbox, choose_slot, save_slot, reset_slot
    try:
        family()
    except (OSError, ValueError):
        pass
    refresh()
    return box
