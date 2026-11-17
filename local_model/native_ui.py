"""Opt-in native Gemma settings dialog; no model loading or activation."""
import tkinter as tk
import threading
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .native_config import NativeModelConfig, PERSONALITY_LIMIT
from .native_settings import (
    EDITABLE_FIELDS, default_native_settings_path, update_native_settings,
)


class NativeSettingsWindow:
    def __init__(self, parent, *, path=None, on_save=None, get_session=None, on_use=None, embed=False):
        self.path = path or default_native_settings_path()
        self.on_save = on_save
        self.get_session = get_session
        self.current = (NativeModelConfig.load(self.path)
                        if self.path.exists() else NativeModelConfig())
        self.embed = bool(embed)
        if self.embed:
            # 056b: le impostazioni del modello stanno DENTRO la pagina Modelli (nessuna finestra).
            self.window = parent
            frame = ttk.Frame(parent, padding=(8, 4))
            frame.pack(fill="x")
            bottom = ttk.Frame(parent, padding=(8, 4))
            bottom.pack(fill="x")
        else:
            self.window = tk.Toplevel(parent)
            self.window.bind("<FocusIn>", lambda _e: self.sync_modello(), add="+")
            self.window.title("Lumi // Modello offline")
            # 028 fix: on a 768 px screen the 780 px window hid Salva/Prova at the
            # bottom (the 026 options made the form taller). Buttons now live in a
            # fixed bar at the bottom and the form scrolls.
            screen_h = self.window.winfo_screenheight()
            height = max(420, min(780, screen_h - 90))
            self.window.geometry(f"640x{height}")
            self.window.minsize(480, 380)
            bottom = ttk.Frame(self.window, padding=(14, 4, 14, 10))
            bottom.pack(side="bottom", fill="x")
            holder = ttk.Frame(self.window)
            holder.pack(side="top", fill="both", expand=True)
            canvas = tk.Canvas(holder, highlightthickness=0, borderwidth=0)
            scrollbar = ttk.Scrollbar(holder, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            frame = ttk.Frame(canvas, padding=14)
            inner = canvas.create_window((0, 0), window=frame, anchor="nw")
            frame.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.bind("<Configure>", lambda e: canvas.itemconfigure(inner, width=e.width))

            def wheel(event):
                if getattr(event, "delta", 0):
                    canvas.yview_scroll(int(-event.delta / 120), "units")
            self.window.bind("<MouseWheel>", wheel)
        ttk.Label(frame, text="Impostazioni del modello selezionato",
                  font=("Segoe UI", 11 if self.embed else 13, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Salvare non avvia il modello. I nuovi valori saranno usati "
                  "dalla prossima richiesta, con ricaricamento solo se necessario.",
                  wraplength=520).pack(anchor="w", pady=(5, 12))
        # 055: «Modelli» (caselle, elenco, profili) vive nella pagina Impostazioni > Modelli, non qui.
        self.values = {}
        labels = {
            "model": "Modello GGUF", "threads": "Thread CPU",
            "batch_threads": "Thread batch", "context_size": "Context Size (token)",
            "max_output": "Max Output (token)", "temperature": "Temperatura",
            "top_k": "Top-K", "top_p": "Top-P", "seed": "Seed (-1 casuale)",
        }
        for key in EDITABLE_FIELDS:
            if key not in labels:
                continue
            if self.embed and key == "model":      # il modello si sceglie dall'elenco, non qui
                self.model_label = tk.StringVar(value="Modello: " + (Path(self.current.model).name
                                                                     if self.current.model else "nessuno"))
                ttk.Label(frame, textvariable=self.model_label).pack(anchor="w", pady=3)
                continue
            line = ttk.Frame(frame)
            line.pack(fill="x", pady=3)
            ttk.Label(line, text=labels[key], width=19).pack(side="left")
            variable = tk.StringVar(value=str(getattr(self.current, key)))
            self.values[key] = variable
            ttk.Entry(line, textvariable=variable).pack(side="left", fill="x", expand=True)
            if key == "model":
                ttk.Button(line, text="Sfoglia...", command=self.browse).pack(side="left", padx=5)
        ttk.Label(frame, text=f"Carattere e stile (facoltativo, max {PERSONALITY_LIMIT} caratteri)").pack(
            anchor="w", pady=(6, 2))
        self.personality = tk.Text(frame, height=3, width=1, wrap="word",
                                   bg="#031522", fg="#d7f6ff", insertbackground="#d7f6ff")
        self.personality.insert("1.0", self.current.personality)
        self.personality.pack(fill="x")
        ttk.Label(frame, text="Es. Parla come Lumi: preciso, con ironia secca.",
                  wraplength=420).pack(anchor="w", pady=(2, 0))
        # 026: carattere a menu, lunghezza delle risposte, note sull'utente,
        # fast forwarding. Tutto breve: poche parole in cima al prompt.
        from .persona import CHARACTERS, EXPLAIN_MAX, EXPLAIN_MIN, LENGTHS, NONE_LABEL, NOTES_LIMIT
        self._character_choices = [NONE_LABEL] + list(CHARACTERS)
        persona = ttk.Frame(frame)
        persona.pack(fill="x", pady=(8, 0))
        ttk.Label(persona, text="Carattere principale").grid(row=0, column=0, sticky="w")
        ttk.Label(persona, text="Tocco in più").grid(row=0, column=1, sticky="w", padx=(10, 0))
        self.character_main = tk.StringVar(value=self.current.character_main or NONE_LABEL)
        self.character_extra = tk.StringVar(value=self.current.character_extra or NONE_LABEL)
        ttk.Combobox(persona, textvariable=self.character_main, values=self._character_choices,
                     state="readonly", width=18).grid(row=1, column=0, sticky="w")
        ttk.Combobox(persona, textvariable=self.character_extra, values=self._character_choices,
                     state="readonly", width=18).grid(row=1, column=1, sticky="w", padx=(10, 0))
        ttk.Label(persona, text="Lunghezza risposte").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(persona, text="Spiegazioni (frasi)").grid(row=2, column=1, sticky="w",
                                                            padx=(10, 0), pady=(6, 0))
        self._length_labels = dict(LENGTHS)
        self.reply_length = tk.StringVar(value=LENGTHS.get(self.current.reply_length, NONE_LABEL))
        ttk.Combobox(persona, textvariable=self.reply_length, values=list(LENGTHS.values()),
                     state="readonly", width=18).grid(row=3, column=0, sticky="w")
        self.explain_sentences = tk.StringVar(value=str(self.current.explain_sentences))
        ttk.Spinbox(persona, from_=EXPLAIN_MIN, to=EXPLAIN_MAX, textvariable=self.explain_sentences,
                    width=6).grid(row=3, column=1, sticky="w", padx=(10, 0))
        ttk.Label(frame, text=("Con «spiegami», «come funziona», «approfondisci», «in dettaglio», "
                               "«descrivimi» o «consigliami» la risposta può arrivare al numero "
                               "di frasi per le spiegazioni."), wraplength=560).pack(anchor="w", pady=(3, 0))
        ttk.Label(frame, text=f"Note su di te (facoltativo, max {NOTES_LIMIT} caratteri)").pack(
            anchor="w", pady=(8, 2))
        self.user_notes = tk.StringVar(value=self.current.user_notes)
        ttk.Entry(frame, textvariable=self.user_notes).pack(fill="x")
        self.fast_forward = tk.BooleanVar(value=self.current.fast_forward)
        ttk.Checkbutton(frame, variable=self.fast_forward, text=(
            "Fast forwarding: riusa l'inizio del prompt già elaborato (più veloce). "
            "Cambiarlo richiede di riavviare Lumi.")).pack(anchor="w", pady=(8, 0))
        self.mem_values = {}
        if self.embed:
            self._build_memory(frame)
        self.status = tk.StringVar(value="Salva il GGUF, poi premi Prova generazione. Nessun invio online.")
        ttk.Label(bottom, textvariable=self.status, wraplength=600).pack(
            anchor="w", pady=(0, 6))
        buttons = ttk.Frame(bottom)
        buttons.pack(fill="x")
        self.profilo = None
        self.on_change = None
        self.save_button = ttk.Button(buttons, text="Salva", command=self.save)
        self.save_button.pack(side="left")
        self.cancel_button = ttk.Button(buttons, text="Annulla modifiche", command=self.annulla)
        self.cancel_button.pack(side="left", padx=6)
        self.dirty_text = tk.StringVar(value="")
        ttk.Label(buttons, textvariable=self.dirty_text, foreground="#ff9a1f").pack(side="left", padx=6)
        self._base = self._snapshot()
        for variable in list(self.values.values()) + list(self.mem_values.values()) + [
                self.fast_forward, self.character_main, self.character_extra, self.reply_length,
                self.explain_sentences, self.user_notes] + (
                [self.ricordi_var] if hasattr(self, "ricordi_var") else []):
            variable.trace_add("write", lambda *_a: self._aggiorna_modifiche())
        self.personality.bind("<KeyRelease>", lambda _e: self._aggiorna_modifiche(), add="+")
        self.test_button = ttk.Button(buttons, text="Prova generazione", command=self.test_model)
        self.test_button.pack(side="left", padx=6)
        ttk.Button(buttons, text="Ripristina campi", command=self.reset).pack(
            side="left", padx=6)
        if not self.embed:
            ttk.Button(buttons, text="Chiudi", command=self.window.destroy).pack(side="right")
        ttk.Button(buttons, text="Diagnostica prompt...", command=self.open_prompt_diagnostics).pack(
            side="right", padx=5)

    _MEM_LABELS = (
        ("history_max_tokens", "Token cronologia e ricordi (128-600)"),
        ("recent_messages", "Messaggi recenti nel prompt"),
        ("summarize_every", "Sintesi ogni N messaggi"),
        ("summary_max_tokens", "Limite riassunto (token)"),
        ("idle_seconds", "Inattività prima della sintesi (secondi)"),
        ("prompt_max_tokens", "Tetto del prompt (token)"))
    _MEM_FLAGS = (
        ("conversation_priority", "Priorità assoluta alla conversazione"),
        ("pause_on_heavy_load", "Sospendi con carico elevato"),
        ("background_summaries", "Abilita sintesi in inattività"),
        ("cronologia_ridotta", "Cronologia ridotta per domande brevi"),
        ("chat_continua", "Chat continua (come KoboldCpp): inizio fisso, messaggi accodati"))

    def _memory_path(self):
        return Path(self.path).parent / "memory.json"

    def _build_memory(self, frame):
        """056b: le impostazioni della memoria del prompt sono qui, nel profilo del modello.
        Il Second Brain (accensione, cancellazione) resta in Memoria ed è unico per tutti."""
        from .memory_preferences import MemoryPreferences
        try:
            prefs = MemoryPreferences.load(self._memory_path())
        except (OSError, ValueError):
            prefs = MemoryPreferences()
        # 056c: un solo blocco «Contesto e memoria» (prima erano due), salvato nel profilo.
        frame = ttk.LabelFrame(frame, text="Contesto e memoria del prompt (parte del profilo)")
        frame.pack(fill="x", pady=(10, 2))
        ttk.Label(frame, wraplength=520, text=(
            "La cronologia è quella della chat scelta nell'elenco. Contesto e tetto del prompt "
            "valgono per questo modello: ogni modello nuovo parte da contesto 896, tetto del prompt 550 e risposta massima 256. Prompt + risposta non possono superare il contesto.")).pack(anchor="w", padx=6, pady=3)
        for key, title in self._MEM_LABELS:
            line = ttk.Frame(frame)
            line.pack(fill="x", pady=2)
            ttk.Label(line, text=title, width=38).pack(side="left")
            variable = tk.StringVar(value=str(getattr(prefs, key)))
            self.mem_values[key] = variable
            ttk.Entry(line, textvariable=variable, width=10).pack(side="left")
        for key, title in self._MEM_FLAGS:
            variable = tk.BooleanVar(value=bool(getattr(prefs, key)))
            self.mem_values[key] = variable
            ttk.Checkbutton(frame, text=title, variable=variable).pack(anchor="w", pady=1)
        from contesto_lumi import RICORDI, RICORDI_ETICHETTE
        riga = ttk.Frame(frame)
        riga.pack(fill="x", pady=2)
        ttk.Label(riga, text="Ricordi di Second Brain e del progetto", width=38).pack(side="left")
        self._ricordi_codici = list(RICORDI)
        self.ricordi_var = tk.StringVar(value=RICORDI_ETICHETTE[prefs.ricordi_locale])
        ttk.Combobox(riga, textvariable=self.ricordi_var, state="readonly", width=26,
                     values=[RICORDI_ETICHETTE[k] for k in RICORDI]).pack(side="left")
        ttk.Button(frame, text="Dettagli ultimo contesto",
                   command=self.show_context_metrics).pack(anchor="w", pady=(4, 2), padx=4)

    # 056c: «Modifiche non salvate», «Salva nel profilo N», «Annulla modifiche». Niente salvataggio automatico.
    def _snapshot(self):
        keys = (list(self.values) + list(self.mem_values))
        data = {k: str((self.values.get(k) or self.mem_values.get(k)).get()) for k in keys}
        for name in ("fast_forward", "character_main", "character_extra", "reply_length",
                     "explain_sentences", "user_notes", "ricordi_var"):
            if hasattr(self, name):
                data[name] = str(getattr(self, name).get())
        data["personality"] = self.personality.get("1.0", "end-1c")
        return data

    def modificato(self):
        return self._snapshot() != self._base

    def _aggiorna_modifiche(self):
        if hasattr(self, "dirty_text"):
            self.dirty_text.set("Modifiche non salvate" if self.modificato() else "")
        if callable(self.on_change):
            self.on_change(self.modificato())

    def imposta_profilo(self, numero):
        """Il profilo in uso per questo modello: dà il nome al pulsante di salvataggio."""
        self.profilo = numero
        self.save_button.configure(text="Salva nel profilo %d" % numero if numero else "Salva")

    def annulla(self):
        self.ricarica()
        self.status.set("Modifiche annullate: valori del profilo in uso.")

    def show_context_metrics(self):
        try:
            session = self.get_session() if callable(self.get_session) else None
            metrics = getattr(session, "last_context_metrics", {}) or {}
        except Exception as exc:
            metrics = {"errore": str(exc)[:120]}
        text = "\n".join("%s: %s" % (k, v) for k, v in metrics.items()) or "Nessun contesto ancora costruito."
        messagebox.showinfo("Ultimo contesto", text, parent=self.window)

    def _riallinea(self):
        self.personality.delete("1.0", "end")
        self.personality.insert("1.0", self.current.personality)
        self.character_main.set(self.current.character_main or self._character_choices[0])
        self.character_extra.set(self.current.character_extra or self._character_choices[0])
        self.reply_length.set(self._length_labels.get(self.current.reply_length, self._character_choices[0]))
        self.explain_sentences.set(str(self.current.explain_sentences))
        self.user_notes.set(self.current.user_notes)
        self._base = self._snapshot()
        self._aggiorna_modifiche()

    def ricarica(self):
        """Rilegge dal disco modello in uso, profilo caricato e memoria (dopo un cambio)."""
        try:
            disk = NativeModelConfig.load(self.path) if self.path.exists() else NativeModelConfig()
        except (OSError, ValueError):
            return
        self.current = disk
        for key, variable in self.values.items():
            variable.set(str(getattr(disk, key)))
        self.fast_forward.set(bool(disk.fast_forward))
        if hasattr(self, "model_label"):
            self.model_label.set("Modello: " + (Path(disk.model).name if disk.model else "nessuno"))
        if self.mem_values:
            from .memory_preferences import MemoryPreferences
            try:
                prefs = MemoryPreferences.load(self._memory_path())
            except (OSError, ValueError):
                prefs = MemoryPreferences()
            for key, variable in self.mem_values.items():
                variable.set(getattr(prefs, key) if isinstance(variable, tk.BooleanVar)
                             else str(getattr(prefs, key)))
            from contesto_lumi import RICORDI_ETICHETTE
            self.ricordi_var.set(RICORDI_ETICHETTE[prefs.ricordi_locale])
        self._riallinea()

    def _save_memory(self):
        from dataclasses import replace
        from .memory_preferences import MemoryPreferences
        try:
            current = MemoryPreferences.load(self._memory_path())
        except (OSError, ValueError):
            current = MemoryPreferences()
        valori = {k: (bool(v.get()) if isinstance(v, tk.BooleanVar) else int(v.get().strip()))
                  for k, v in self.mem_values.items()}
        from contesto_lumi import RICORDI, RICORDI_ETICHETTE
        etichette = {RICORDI_ETICHETTE[k]: k for k in RICORDI}
        valori["ricordi_locale"] = etichette.get(self.ricordi_var.get(), current.ricordi_locale)
        replace(current, **valori).save(self._memory_path())

    def open_prompt_diagnostics(self):
        """Manual one-turn RAM capture; opening this UI never loads a GGUF."""
        dialog = tk.Toplevel(self.window)
        dialog.title("Lumi // Diagnostica prompt Gemma")
        dialog.geometry("840x620")
        dialog.minsize(570, 380)
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=(
            "Chi costruisce il prompt, da dove proviene ogni parte, "
            "quanti token occupa e testo esatto inviato al modello."),
            wraplength=780).pack(anchor="w")
        ttk.Label(frame, text=(
            "Cattura manuale della PROSSIMA domanda normale a Gemma. "
            "Nessun file, rete, log automatico o nuova generazione. "
            "NON include il pulsante Prova generazione e le risposte Telegram."),
            wraplength=780).pack(anchor="w", pady=(5, 8))
        status = tk.StringVar(value="Non attiva: premi Acquisisci, poi fai una domanda a Gemma.")
        row = ttk.Frame(frame)
        row.pack(fill="x")
        viewframe = ttk.Frame(frame)
        viewframe.pack(fill="both", expand=True, pady=8)
        view = tk.Text(viewframe, wrap="word", font=("Consolas", 10),
                       bg="#031522", fg="#d7f6ff", insertbackground="#d7f6ff")
        scroll = ttk.Scrollbar(viewframe, orient="vertical", command=view.yview)
        view.configure(yscrollcommand=scroll.set, state="disabled")
        scroll.pack(side="right", fill="y")
        view.pack(side="left", fill="both", expand=True)

        def session():
            if not callable(self.get_session):
                raise RuntimeError("Sessione Gemma non disponibile.")
            return self.get_session()

        def display(value):
            view.configure(state="normal")
            view.delete("1.0", "end")
            view.insert("1.0", value)
            view.configure(state="disabled")

        def arm():
            try:
                session().arm_prompt_diagnostic()
                display("")
                status.set("Pronta: fai UNA domanda a Gemma e premi Aggiorna.")
            except Exception as exc:
                status.set("Cattura non disponibile: " + type(exc).__name__)

        def refresh():
            try:
                report = session().prompt_diagnostic()
                if report is None:
                    status.set("Nessun prompt catturato. Attiva, invia una domanda e aggiorna.")
                    return
                display(report)
                status.set("Prompt acquisito. Contiene potenzialmente dati personali.")
            except Exception as exc:
                status.set("Lettura non disponibile: " + type(exc).__name__)

        def discard():
            try:
                session().clear_prompt_diagnostic()
                display("")
                status.set("Cattura cancellata dalla RAM; nessun dato salvato.")
            except Exception as exc:
                status.set("Cancellazione non disponibile: " + type(exc).__name__)

        def copy():
            content = view.get("1.0", "end-1c")
            if not content.strip():
                status.set("Nessun report da copiare.")
                return
            if not messagebox.askyesno(
                    "Lumi / Prompt privato",
                    "Il report può contenere conversazioni e ricordi privati. "
                    "Vuoi copiarlo negli appunti di Windows?", parent=dialog):
                return
            dialog.clipboard_clear()
            dialog.clipboard_append(content)
            status.set("Copiato negli appunti. Incolla solo dove vuoi condividerlo.")

        ttk.Button(row, text="Acquisisci prossima domanda", command=arm).pack(side="left")
        ttk.Button(row, text="Aggiorna", command=refresh).pack(side="left", padx=5)
        ttk.Button(row, text="Scarta", command=discard).pack(side="left")
        ttk.Button(row, text="Copia con conferma", command=copy).pack(side="right")
        ttk.Label(frame, textvariable=status, wraplength=780).pack(anchor="w", pady=4)

    def browse(self):
        selected = filedialog.askopenfilename(
            parent=self.window, title="Scegli modello GGUF",
            filetypes=[("Modello GGUF", "*.gguf")])
        if selected:
            self.values["model"].set(selected)

    def reset(self):
        defaults = NativeModelConfig()
        for key, variable in self.values.items():
            variable.set(str(getattr(defaults, key)))
        self.personality.delete("1.0", "end")
        from .persona import NONE_LABEL
        self.character_main.set(NONE_LABEL)
        self.character_extra.set(NONE_LABEL)
        self.reply_length.set(NONE_LABEL)
        self.explain_sentences.set(str(defaults.explain_sentences))
        self.user_notes.set("")
        self.fast_forward.set(True)
        self.status.set("Valori predefiniti mostrati; premi Salva per confermare.")

    def sync_modello(self):
        """056b: UNA sola fonte (native.json). Se il modello in uso è cambiato altrove (elenco,
        caselle, tendina, voce) il modulo mostra quello e il suo profilo, mai uno vecchio."""
        try:
            disk = NativeModelConfig.load(self.path) if self.path.exists() else None
        except (OSError, ValueError):
            return False
        if disk is None or disk.model == self.current.model:
            return False
        self.current = disk
        for key, variable in self.values.items():
            variable.set(str(getattr(disk, key)))
        self.fast_forward.set(bool(disk.fast_forward))
        self._riallinea()
        self.status.set("Modello cambiato: ora mostro le impostazioni di quello in uso.")
        return True

    def save(self):
        if self.sync_modello():
            return False        # niente scrittura sopra la scelta fatta altrove
        try:
            changes = {"personality": self.personality.get("1.0", "end-1c").strip()}
            from .persona import CHARACTERS
            for key, variable in (("character_main", self.character_main),
                                  ("character_extra", self.character_extra)):
                value = variable.get()
                changes[key] = value if value in CHARACTERS else ""
            by_label = {label: key for key, label in self._length_labels.items()}
            changes["reply_length"] = by_label.get(self.reply_length.get(), "")
            changes["explain_sentences"] = int(self.explain_sentences.get())
            changes["user_notes"] = " ".join(self.user_notes.get().split())
            changes["fast_forward"] = bool(self.fast_forward.get())
            for key, variable in self.values.items():
                value = variable.get().strip()
                if key in ("threads", "batch_threads", "context_size",
                           "max_output", "top_k", "seed"):
                    changes[key] = int(value)
                elif key in ("temperature", "top_p"):
                    changes[key] = float(value)
                else:
                    changes[key] = value
            if self.mem_values:
                prompt = int(self.mem_values["prompt_max_tokens"].get().strip())
                contesto = changes.get("context_size", self.current.context_size)
                risposta = changes.get("max_output", self.current.max_output)
                if prompt + risposta > contesto:
                    raise ValueError(
                        "tetto del prompt (%d) + risposta massima (%d) = %d superano il contesto (%d). "
                        "Aumenta il contesto o abbassa uno dei due." % (prompt, risposta, prompt + risposta, contesto))
            revised, reload_needed = update_native_settings(self.current, changes)
            revised.save(self.path)
            self.current = revised
            if self.mem_values:
                self._save_memory()      # prima del profilo: salva_in_slot copia anche la memoria
            if revised.model:
                # 056b: native.json è la base; le modifiche vanno anche nel profilo (slot in uso)
                # del modello selezionato, così caselle e profili non restano indietro.
                try:
                    from . import profili_famiglia
                    profili_famiglia.salva_in_slot(
                        revised.model, profili_famiglia.slot_ricordato(revised.model, self.path),
                        self.path)
                except (OSError, ValueError, RuntimeError):
                    pass
            self._base = self._snapshot()
            self._aggiorna_modifiche()
            if callable(self.on_save):
                self.on_save(revised, reload_needed)
            self.status.set("Impostazioni salvate. " + (
                "Ricaricamento automatico alla prossima richiesta." if reload_needed
                else "Valori usati dalla prossima generazione."))
            return True
        except (OSError, ValueError, TypeError) as exc:
            messagebox.showerror("Lumi / Modelli",
                                 "Impostazioni non valide: " + str(exc),
                                 parent=self.window)
            return False

    def test_model(self):
        """Run one real native generation without using GPT online."""
        try:
            if not self.save():
                return
            if not self.current.model or not Path(self.current.model).is_file():
                raise ValueError("Seleziona prima un file GGUF esistente.")
            get_session = self.get_session
            if not callable(get_session):
                raise ValueError("Sessione Gemma di Lumi non disponibile.")
            config = self.current
            self.test_button.configure(state="disabled")
            self.status.set("Caricamento DLL e GGUF in corso...")
            def worker():
                try:
                    session = get_session()
                    answer = session.test_generation(config=config, timeout=180)
                    result = "TEST RIUSCITO. Risposta: " + str(answer)[:200]
                except Exception as exc:
                    result = "TEST FALLITO: " + str(exc)[:300]
                def finish():
                    if self.window.winfo_exists():
                        self.status.set(result)
                        self.test_button.configure(state="normal")
                try:
                    self.window.after(0, finish)
                except RuntimeError:
                    pass
            threading.Thread(target=worker, daemon=True, name="jarvis-gemma-test").start()
        except (OSError, ValueError, TypeError) as exc:
            self.status.set("TEST FALLITO: " + str(exc))
