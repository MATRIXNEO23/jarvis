"""«La mia voce»: Lumi impara come il riconoscimento offline (Vosk) capisce chi parla.

Vosk non si riaddestra sul PC: si leggono parole e frasi scelte per i suoni difficili
(S, P, F, vocali, doppie, nomi inglesi); quando il testo capito è diverso da quello atteso,
la differenza viene salvata come correzione vocale (adaptive_voice.SpeechCorrections,
lo stesso dizionario già usato da Lumi) e da lì in poi corretta da sola.
Qui c'è anche la pausa tra le parole: quanto Lumi aspetta prima di considerare finita
una frase (profilo: voce.json). Nessun audio salvato, niente internet.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

PHRASES = [
    # S, Z e doppie
    "sì", "sei", "sette", "sasso", "stessa strada", "scorri giù", "sposta il mouse a sinistra",
    "spegni lo schermo intero", "zucchero e sale", "scrivi questo nella ricerca",
    # P, B, T, D
    "play", "pausa", "premi invio", "apri il pannello", "doppio clic", "torna indietro",
    "bottone blu", "dieci dita",
    # F, V
    "file successivo", "file precedente", "finestra", "Facebook", "va bene", "favoloso",
    # vocali e parole corte
    "uno", "due", "tre", "quattro", "cinque", "otto", "nove", "no", "ok", "io e te",
    "aiuto", "eh", "home", "esci",
    # nomi inglesi e titoli
    "Netflix", "YouTube", "Deep Impact", "Stranger Things", "The Office", "Spotify",
    # frasi complete
    "Lumi apri gestione attività",
    "mostra i numeri e poi clicca sul quinto",
    "scorri a destra fino al prossimo film",
    "metti lo schermo intero e poi esci",
    "chiudi forzatamente il programma bloccato",
    "imposta la sveglia alle sette e mezza",
    "riproduci la playlist preferita sul computer",
    "spegni il cervello locale e attiva quello online",
]

DEFAULT_PAUSE = 0.6
MAX_PAUSE = 2.0
_LOCK = threading.Lock()
_STATE = {"trainer": None, "pause": None}
ON_LEARNED: list = []        # jarvis.py: ricarica il dizionario in uso


def _path() -> Path | None:
    try:
        from settings import default_path
        return default_path().parent / "voce.json"
    except Exception:
        return None


def _load() -> dict:
    path = _path()
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path and path.exists() else {}
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def pause_seconds() -> float:
    """Attesa in più dopo la fine di una frase (0 = come prima)."""
    if _STATE["pause"] is None:
        try:
            value = float(_load().get("pause", DEFAULT_PAUSE))
        except (TypeError, ValueError):
            value = DEFAULT_PAUSE
        _STATE["pause"] = max(0.0, min(MAX_PAUSE, value))
    return _STATE["pause"]


def set_pause(value: float) -> float:
    value = max(0.0, min(MAX_PAUSE, round(float(value), 1)))
    _STATE["pause"] = value
    path = _path()
    if path is not None:
        data = _load()
        data["pause"] = value
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, path)
        except OSError:
            pass
    return value


def _norm(text: str) -> str:
    return " ".join(str(text).casefold().replace(",", " ").replace("'", " ").strip(" .!?").split())


class Session:
    """Una lettura guidata: frase attesa → testo capito → correzione (se serve)."""

    def __init__(self, lexicon=None, phrases=None, report=None):
        if lexicon is None:
            from adaptive_voice import SpeechCorrections
            lexicon = SpeechCorrections()
        self.lexicon = lexicon
        self.phrases = list(phrases or PHRASES)
        self.index = 0
        self.report = report or (lambda result: None)
        self.results: list[tuple[str, str, str]] = []

    @property
    def expected(self) -> str | None:
        return self.phrases[self.index] if self.index < len(self.phrases) else None

    def hear(self, heard: str) -> str:
        expected = self.expected
        if expected is None:
            return ""
        got, want = _norm(heard), _norm(expected)
        if got == want:
            outcome = "Capito bene."
        else:
            try:
                source, target = self.lexicon.learn_phrase(got, want, user_confirmed=True)
                outcome = f"Imparato: «{source}» → «{target}»."
                for callback in ON_LEARNED:
                    try:
                        callback()
                    except Exception:
                        pass
            except Exception as exc:          # parole di controllo, dizionario pieno…
                outcome = f"Capito «{heard}», non imparo: {str(exc)[:80]}"
        self.results.append((expected, heard, outcome))
        self.index += 1
        self.report(outcome)
        return outcome


def start(session: Session) -> None:
    with _LOCK:
        _STATE["trainer"] = session


def stop() -> None:
    with _LOCK:
        _STATE["trainer"] = None


def receive(speech: str) -> bool:
    """Chiamata dal microfono: True se la frase era per l'addestramento."""
    with _LOCK:
        session = _STATE["trainer"]
    if session is None or not str(speech).strip():
        return False
    session.hear(speech)
    if session.expected is None:
        stop()
    return True


class VoiceWindow:
    """Finestra «La mia voce» (Impostazioni)."""

    def __init__(self, parent):
        import tkinter as tk
        from tkinter import ttk
        self.window = tk.Toplevel(parent)
        self.window.title("La mia voce")
        self.window.geometry("560x430")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        frame = ttk.Frame(self.window, padding=12)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, wraplength=520, text=(
            "Leggi ad alta voce la frase in grande, con il microfono acceso. Se Lumi capisce "
            "qualcosa di diverso, si ricorda la differenza e la corregge da sola nei comandi. "
            "Non serve dire «Lumi». Le correzioni si usano con la memoria (Second Brain) attiva."
        )).pack(anchor="w")
        self.phrase = tk.StringVar(value="Premi «Inizia».")
        ttk.Label(frame, textvariable=self.phrase, font=("Segoe UI", 20, "bold"),
                  wraplength=520).pack(anchor="w", pady=(14, 4))
        self.status = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.status, wraplength=520).pack(anchor="w")
        buttons = ttk.Frame(frame)
        buttons.pack(anchor="w", pady=10)
        ttk.Button(buttons, text="Inizia", command=self.begin).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Salta frase", command=self.skip).pack(side="left", padx=(0, 8))
        ttk.Button(buttons, text="Ferma", command=self.end).pack(side="left")
        pause = ttk.LabelFrame(frame, text="Pausa tra le parole prima che il comando parta",
                               padding=8)
        pause.pack(fill="x", pady=(10, 0))
        self.pause = tk.DoubleVar(value=pause_seconds())
        self.pause_text = tk.StringVar()
        ttk.Scale(pause, from_=0.0, to=MAX_PAUSE, variable=self.pause,
                  command=self._pause_changed).pack(side="left", fill="x", expand=True)
        ttk.Label(pause, textvariable=self.pause_text, width=12).pack(side="left", padx=8)
        self._pause_changed()
        self.session = None

    def _pause_changed(self, *_):
        value = set_pause(self.pause.get())
        self.pause_text.set(f"{value:.1f} secondi")

    def begin(self):
        try:
            self.session = Session(report=lambda text: self.window.after(0, self._next, text))
        except Exception as exc:
            self.status.set("Dizionario delle correzioni non disponibile: " + str(exc)[:90])
            return
        start(self.session)
        self._next("")

    def _next(self, outcome):
        if self.session is None:
            return
        expected = self.session.expected
        done = self.session.index
        total = len(self.session.phrases)
        self.status.set((outcome + "   " if outcome else "") + f"Frase {min(done + 1, total)} di {total}.")
        if expected is None:
            learned = sum(1 for r in self.session.results if r[2].startswith("Imparato"))
            self.phrase.set("Fatto!")
            self.status.set(f"Finito: {learned} correzioni nuove su {total} frasi.")
            self.session = None
        else:
            self.phrase.set(expected)

    def skip(self):
        if self.session is not None and self.session.expected is not None:
            self.session.index += 1
            self._next("Saltata.")
            if self.session is not None and self.session.expected is None:
                stop()

    def end(self):
        stop()
        self.session = None
        self.phrase.set("Fermato. Premi «Inizia» per ricominciare.")

    def close(self):
        stop()
        self.window.destroy()
