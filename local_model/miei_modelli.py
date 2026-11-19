"""«I miei modelli» (054, rifatto nella 055): 3 caselle fisse, elenco completo, profili per modello.

Nessun doppione con «cambia modello» a voce: l'elenco è scelta_modello.elenca_modelli, il
salvataggio è scelta_modello.salva_scelta (via on_use, che in jarvis.py è la stessa funzione
della scelta a voce, con riavvio del motore) e il Cestino è pulizia_dati.al_cestino.
«Aggiungi modello…» NON copia il file: lo ricorda dov'è (registro_modelli) e segnala se sparisce.
In memoria resta UN solo modello alla volta (RAM del Pavilion): le caselle sono scorciatoie.
"""
from __future__ import annotations

import threading
from pathlib import Path

from . import profili_famiglia, registro_modelli, scelta_modello


def aggiungi_modello(sorgente, config_path=None, progress=None, cancel=None, chunk=None) -> Path:
    """Aggiunge un .gguf all'elenco usandolo da dove si trova (nessuna copia). I parametri
    progress/cancel/chunk restano per compatibilità e non servono più."""
    target = registro_modelli.aggiungi(sorgente, config_path)
    # Legge i metadati subito: se la famiglia non si capisce lo si dice, non si indovina.
    profili_famiglia.riconosci_famiglia(target)
    return target


def rimuovi_modello(percorso, config_path=None, al_cestino=None) -> None:
    """Manda il file nel Cestino; mai il modello in uso."""
    target = Path(percorso)
    in_uso = scelta_modello.modello_in_uso(config_path)
    if in_uso and str(target).casefold() == str(Path(in_uso)).casefold():
        raise ValueError("Questo è il modello in uso: scegline un altro prima di rimuoverlo.")
    if registro_modelli.e_registrato(target, config_path):
        registro_modelli.togli(target, config_path)       # il file resta dov'è: lo togli solo dall'elenco
        return
    if al_cestino is None:
        from pulizia_dati import al_cestino
    if not target.is_file():
        raise ValueError("Il file non esiste più.")
    if not al_cestino([target]):
        raise OSError("Non riesco a spostare il file nel Cestino.")


def mancanti(config_path=None) -> list[Path]:
    return registro_modelli.mancanti(config_path)


def righe(config_path=None) -> list[tuple[Path, bool]]:
    """(percorso, in_uso) per ogni modello dell'elenco."""
    in_uso = scelta_modello.modello_in_uso(config_path)
    return [(m, bool(in_uso) and str(m).casefold() == str(Path(in_uso)).casefold())
            for m in scelta_modello.elenca_modelli(config_path)]


ACCESO_BG, ACCESO_FG = "#46ccfa", "#04202f"       # tema Lumi: selezionato = azzurro acceso
SPENTO_BG, SPENTO_FG = "#0b2f44", "#8fb8cc"


def costruisci_sezione(parent, notify, *, on_use, config_path=None, ask_file=None, confirm=None,
                       run_async=None, al_cestino=None, impostazioni=None):
    """Sezione «Modelli» (Tk): 3 caselle fisse 1/2/3 con un modello ciascuna, sotto l'elenco
    completo (modello in uso evidenziato), «Aggiungi modello…» (senza copiare), «Usa questo»,
    «Metti nella casella…», «Rimuovi», e i profili 1/2/3 del modello in uso."""
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    ask_file = ask_file or (lambda: filedialog.askopenfilename(
        parent=parent, title="Aggiungi modello", filetypes=[("Modello GGUF", "*.gguf")]))
    confirm = confirm or (lambda text: messagebox.askyesno("Rimuovi modello", text, parent=parent))
    run_async = run_async or (lambda fn: threading.Thread(
        target=fn, daemon=True, name="lumi-aggiungi-modello").start())
    box = ttk.LabelFrame(parent, text="Modelli offline")
    box.pack(fill="x", padx=8, pady=8)
    state = {"rows": [], "busy": False, "slots": {}}
    status = tk.StringVar(value="")

    # Caselle fisse 1/2/3.
    slots_bar = ttk.Frame(box)
    slots_bar.pack(fill="x", padx=8, pady=(6, 0))
    slot_buttons, slot_labels = {}, {}
    for number in registro_modelli.CASELLE:
        cell = ttk.Frame(slots_bar)
        cell.pack(side="left", padx=(0, 8))
        slot_labels[number] = tk.StringVar(value="")
        slot_buttons[number] = tk.Button(cell, textvariable=slot_labels[number], width=22,
                                         command=lambda n=number: use_slot(n), relief="flat", bd=1,
                                         bg=SPENTO_BG, fg=SPENTO_FG, activebackground=ACCESO_BG,
                                         activeforeground=ACCESO_FG, disabledforeground="#4a6a7e",
                                         cursor="hand2")
        slot_buttons[number].pack()
    ttk.Label(box, text="Un solo modello alla volta resta in memoria: le caselle servono per "
              "passare in fretta dall'uno all'altro.", wraplength=520).pack(anchor="w", padx=8)
    listbox = tk.Listbox(box, height=6, exportselection=False)
    listbox.pack(fill="x", padx=8, pady=6)
    progress = ttk.Progressbar(box, mode="indeterminate")

    def set_busy(value):
        state["busy"] = value
        add_button.configure(state="disabled" if value else "normal")   # FIX 2: pulsante bloccato

    def refresh():
        state["rows"] = righe(config_path)
        in_use = next((p for p, active in state["rows"] if active), "")
        state["slots"] = registro_modelli.caselle([p for p, _a in state["rows"]], str(in_use), config_path)
        listbox.delete(0, "end")
        for index, (path, active) in enumerate(state["rows"]):
            listbox.insert("end", scelta_modello.nome_breve(path) + ("   ← in uso" if active else ""))
            if active:
                listbox.itemconfigure(index, background="#0b2f44", foreground="#46ccfa")
        for number in registro_modelli.CASELLE:
            model = state["slots"].get(number)
            slot_labels[number].set("%d  %s" % (number, scelta_modello.nome_breve(model)[:20]
                                                 if model else "(vuota)"))
            usato = bool(model and in_use and registro_modelli.chiave(model) == registro_modelli.chiave(in_use))
            slot_buttons[number].configure(state="normal" if model else "disabled",
                                           bg=ACCESO_BG if usato else SPENTO_BG,
                                           fg=ACCESO_FG if usato else SPENTO_FG)
        lost = mancanti(config_path)
        if lost:
            status.set("Attenzione: non trovo più %d modello/i aggiunto/i: %s." % (
                len(lost), ", ".join(p.name for p in lost[:3])))

    def selected():
        picked = listbox.curselection()
        return state["rows"][picked[0]][0] if picked else None

    def add():
        if state["busy"]:
            return
        source = ask_file()
        if not source:
            return
        set_busy(True)
        progress.pack(fill="x", padx=8)
        progress.start(12)

        def work():
            try:
                target = aggiungi_modello(source, config_path)
                family, known = profili_famiglia.riconosci_famiglia(target)
                message = "Modello aggiunto, resta dov'è: " + scelta_modello.nome_breve(target) + (
                    "." if known else ". Famiglia incerta.")
            except (OSError, ValueError) as exc:
                message = "Modello non aggiunto: " + str(exc)[:120]

            def finish():
                progress.stop()
                progress.pack_forget()
                set_busy(False)
                status.set(message)
                notify("MODELLO LOCALE > " + message)
                refresh()
            try:
                parent.after(0, finish)
            except (RuntimeError, tk.TclError):
                state["busy"] = False
        run_async(work)

    def use():
        target = selected()
        if target is None:
            status.set("Scegli prima un modello dall'elenco.")
            return
        on_use(target)
        refresh()
        profile_refresh()

    def use_slot(number):
        model = state["slots"].get(number)
        if model is None:
            return
        on_use(model)
        refresh()
        profile_refresh()

    def assign(number):
        target = selected()
        if target is None:
            status.set("Scegli prima un modello dall'elenco.")
            return
        try:
            registro_modelli.assegna_casella(number, target, config_path)
            status.set("«%s» è nella casella %d." % (scelta_modello.nome_breve(target), number))
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])
        refresh()

    def remove():
        target = selected()
        if target is None:
            status.set("Scegli prima un modello dall'elenco.")
            return
        added = registro_modelli.e_registrato(target, config_path)
        if not confirm(("Togliere «%s» dall'elenco? Il file resta dov'è." if added
                        else "Spostare «%s» nel Cestino?") % scelta_modello.nome_breve(target)):
            return
        try:
            rimuovi_modello(target, config_path, al_cestino)
            status.set("Modello tolto dall'elenco." if added else "Modello spostato nel Cestino.")
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])
        refresh()

    bar = ttk.Frame(box)
    bar.pack(fill="x", padx=8)
    add_button = ttk.Button(bar, text="Aggiungi modello…", command=add)
    add_button.pack(side="left")
    ttk.Button(bar, text="Usa questo", command=use).pack(side="left", padx=4)
    cell_menu = ttk.Menubutton(bar, text="Metti nella casella…")
    menu = tk.Menu(cell_menu, tearoff=False)
    for number in registro_modelli.CASELLE:
        menu.add_command(label="Casella %d" % number, command=lambda n=number: assign(n))
    cell_menu.configure(menu=menu)
    cell_menu.pack(side="left", padx=4)
    ttk.Button(bar, text="Rimuovi", command=remove).pack(side="left")
    ttk.Label(box, textvariable=status, wraplength=520).pack(anchor="w", padx=8, pady=(4, 0))

    # Profili del modello in uso (3 slot per modello).
    prof = ttk.Frame(box)
    prof.pack(fill="x", padx=8, pady=6)
    slot_var = tk.IntVar(value=1)
    family_var = tk.StringVar(value="")
    info_state = {}

    panel = {}

    def reload_panel():
        if panel.get("p") is not None:
            panel["p"].ricarica()

    profile_buttons = {}

    def colora_profili():
        """057: il profilo in uso è azzurro acceso, gli altri spenti; il pulsante di salvataggio
        porta il suo numero («Salva nel profilo N»)."""
        for n, button in profile_buttons.items():
            acceso = n == slot_var.get()
            button.configure(bg=ACCESO_BG if acceso else SPENTO_BG, fg=ACCESO_FG if acceso else SPENTO_FG)
        if panel.get("p") is not None and hasattr(panel["p"], "imposta_profilo"):
            panel["p"].imposta_profilo(slot_var.get())

    def profile_refresh():
        """Aggiorna etichetta e slot dal file; da chiamare SOLO quando serve rileggere."""
        info = profili_famiglia.assicura(config_path)
        info_state.update(info)
        family_var.set("Profili di: %s (famiglia %s)" % (
            Path(info["modello"]).name if info.get("modello") else "nessun modello",
            info["famiglia"] if info["riconosciuta"] else "incerta"))
        slot_var.set(info["slot"])
        reload_panel()
        colora_profili()

    def model_path():
        return info_state.get("modello") or scelta_modello.modello_in_uso(config_path)

    def choose_slot():
        number = slot_var.get()            # FIX 1: il numero cliccato si legge PRIMA di ogni refresh
        try:
            result = profili_famiglia.scegli_slot(model_path(), number, config_path)
            reload_panel()
            colora_profili()
            status.set("Profilo %d caricato." % number + (
                " Per applicare %s serve riavviare il motore." % ", ".join(result["campi_riavvio"])
                if result["serve_riavvio"] else " Nessun riavvio necessario."))
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])

    def save_slot():
        number = slot_var.get()
        try:
            profili_famiglia.salva_in_slot(model_path(), number, config_path)
            colora_profili()
            status.set("Valori salvati nel profilo %d." % number)
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])

    def reset_slot():
        number = slot_var.get()
        try:
            result = profili_famiglia.ripristina_default(model_path(), number, config_path)
            reload_panel()
            status.set("Profilo %d riportato ai valori di fabbrica." % number + (
                " Serve riavviare il motore." if result["serve_riavvio"] else ""))
        except (OSError, ValueError) as exc:
            status.set(str(exc)[:140])

    ttk.Label(prof, textvariable=family_var).pack(side="left")
    for number in profili_famiglia.SLOT:
        profile_buttons[number] = tk.Button(
            prof, text="Profilo %d" % number, relief="flat", bd=1, padx=8, cursor="hand2",
            bg=SPENTO_BG, fg=SPENTO_FG, activebackground=ACCESO_BG, activeforeground=ACCESO_FG,
            command=lambda n=number: (slot_var.set(n), choose_slot()))
        profile_buttons[number].pack(side="left", padx=4)
    ttk.Button(prof, text="Ripristina default", command=reset_slot).pack(side="left")
    # 056b: sotto i profili, nella stessa pagina, tutte le impostazioni del modello selezionato
    # (base native.json) con UN solo Salva che scrive anche nel profilo caricato.
    if impostazioni is not None:
        settings_frame = ttk.Frame(box)
        settings_frame.pack(fill="x", padx=8, pady=(4, 8))
        panel["p"] = impostazioni(settings_frame)
    box.panel = panel
    box.add, box.use, box.remove, box.refresh = add, use, remove, refresh
    box.listbox, box.choose_slot, box.save_slot, box.reset_slot = listbox, choose_slot, save_slot, reset_slot
    box.use_slot, box.assign, box.profile_refresh = use_slot, assign, profile_refresh
    box.slot_var, box.state = slot_var, state
    box.slot_buttons, box.profile_buttons, box.colora_profili = slot_buttons, profile_buttons, colora_profili
    colora_profili()
    try:
        profile_refresh()
    except (OSError, ValueError):
        pass
    refresh()
    return box
