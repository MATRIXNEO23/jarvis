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
    def __init__(self, parent, *, path=None, on_save=None, get_session=None):
        self.path = path or default_native_settings_path()
        self.on_save = on_save
        self.get_session = get_session
        self.current = (NativeModelConfig.load(self.path)
                        if self.path.exists() else NativeModelConfig())
        self.window = tk.Toplevel(parent)
        self.window.title("Lumi // Modello locale Gemma")
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
        ttk.Label(frame, text="Gemma locale - configurazione",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Salvare non avvia il modello. I nuovi valori saranno usati "
                  "dalla prossima richiesta, con ricaricamento solo se necessario.",
                  wraplength=520).pack(anchor="w", pady=(5, 12))
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
        self.status = tk.StringVar(value="Salva il GGUF, poi premi Prova generazione. Nessun invio online.")
        ttk.Label(bottom, textvariable=self.status, wraplength=600).pack(
            anchor="w", pady=(0, 6))
        buttons = ttk.Frame(bottom)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Salva", command=self.save).pack(side="left")
        self.test_button = ttk.Button(buttons, text="Prova generazione", command=self.test_model)
        self.test_button.pack(side="left", padx=6)
        ttk.Button(buttons, text="Ripristina campi", command=self.reset).pack(
            side="left", padx=6)
        ttk.Button(buttons, text="Chiudi", command=self.window.destroy).pack(side="right")
        ttk.Button(buttons, text="Diagnostica prompt...", command=self.open_prompt_diagnostics).pack(
            side="right", padx=5)

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

    def save(self):
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
            revised, reload_needed = update_native_settings(self.current, changes)
            revised.save(self.path)
            self.current = revised
            if callable(self.on_save):
                self.on_save(revised, reload_needed)
            self.status.set("Impostazioni salvate. " + (
                "Ricaricamento automatico alla prossima richiesta." if reload_needed
                else "Valori usati dalla prossima generazione."))
            return True
        except (OSError, ValueError, TypeError) as exc:
            messagebox.showerror("Lumi / Gemma",
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
