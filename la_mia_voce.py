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


# --- passo 11: conflitti, lettere perse, trascrizione dal vivo ---------------------------
PARZIALE = {"testo": "", "ascolta": None}       # finestra aperta: riceve il parlato dal vivo
LETTERE = "sz"                                   # lettere che Vosk perde più spesso


def conflitto(source: str, phrases=None) -> str:
    """Motivo se la parola da correggere è anche un comando (o parte di uno)."""
    word = _norm(source)
    if not word:
        return ""
    for phrase in phrases or PHRASES:
        if word == _norm(phrase) or (" " + word + " ") in (" " + _norm(phrase) + " "):
            return "«%s» è anche nel comando «%s»" % (word, phrase)
    return ""


def lettere_perse(results) -> list[str]:
    """Lettere che mancano di continuo nelle frasi capite (≥3 volte): es. la S."""
    counts = {}
    for expected, heard, _outcome in results:
        want, got = _norm(expected).split(), _norm(heard).split()
        if len(want) != len(got):
            continue
        for w, g in zip(want, got):
            for letter in LETTERE:
                if w != g and w.replace(letter, "") == g.replace(letter, "") and w.count(letter) > g.count(letter):
                    counts[letter] = counts.get(letter, 0) + 1
    return sorted(letter for letter, count in counts.items() if count >= 3)


def facoltative() -> str:
    return "".join(_load().get("lettere_facoltative", []))


def salva_facoltative(letters) -> None:
    path = _path()
    if path is None:
        return
    data = _load()
    data["lettere_facoltative"] = sorted(set(letters) & set(LETTERE))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def senza_facoltative(text: str) -> str:
    """Confronto con i comandi: le lettere che la tua voce perde non contano."""
    value = _norm(text)
    for letter in facoltative():
        value = value.replace(letter, "")
    return value


def parziale(text: str) -> None:
    """Dal microfono: parlato in corso (solo mentre la finestra è aperta)."""
    PARZIALE["testo"] = text
    listener = PARZIALE["ascolta"]
    if listener is not None:
        try:
            listener(text)
        except Exception:
            pass


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
        changed = " ".join(w for w in got.split() if w not in want.split())
        clash = conflitto(changed, [p for p in self.phrases if _norm(p) != want]) if changed else ""
        if got == want:
            outcome = "Capito bene."
        elif clash:
            # Passo 11: niente correzioni che confonderebbero un altro comando.
            outcome = "Capito «%s», non imparo per non confondere i comandi: %s." % (heard, clash)
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
        ttk.Button(buttons, text="Cambia la parola di questo comando…",
                   command=self.change_word).pack(side="left", padx=(8, 0))
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
        # Passo 11: parlato dal vivo, lettere perse, correzioni da vedere e togliere,
        # frase capita male scritta a mano.
        self.live = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.live, foreground="#46a0c8", wraplength=520).pack(anchor="w")
        PARZIALE["ascolta"] = lambda text: self.window.after(0, self.live.set, "Sento: " + text)
        letters = ttk.Frame(frame)
        letters.pack(fill="x", pady=(8, 0))
        ttk.Label(letters, text="Lettere che la tua voce perde (nei comandi non contano):").pack(side="left")
        self.letters = {}
        for letter in LETTERE:
            var = tk.BooleanVar(value=letter in facoltative())
            self.letters[letter] = var
            ttk.Checkbutton(letters, text=letter.upper(), variable=var,
                            command=self._save_letters).pack(side="left", padx=4)
        smart = tk.BooleanVar(value=__import__("classificatore").attivo())
        ttk.Checkbutton(frame, variable=smart, text=(
            "Classificatore leggero: se nessun comando corrisponde, Lumi chiede «Intendevi…?» "
            "(spento di serie)"),
            command=lambda: __import__("classificatore").imposta(smart.get())).pack(anchor="w", pady=(6, 0))
        fix = ttk.LabelFrame(frame, text="Lumi ha capito male un comando?", padding=6)
        fix.pack(fill="x", pady=(8, 0))
        self.heard = tk.StringVar(value=_ultima_frase())
        self.meant = tk.StringVar()
        for label, var in (("Lumi ha capito:", self.heard), ("Io avevo detto:", self.meant)):
            row = ttk.Frame(fix)
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=label, width=16).pack(side="left")
            ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True)
        ttk.Button(fix, text="Impara la differenza", command=self.learn_typed).pack(anchor="e", pady=(3, 0))
        listing = ttk.LabelFrame(frame, text="Correzioni imparate", padding=6)
        listing.pack(fill="both", expand=True, pady=(8, 0))
        self.list = tk.Listbox(listing, height=5, activestyle="none")
        self.list.pack(side="left", fill="both", expand=True)
        ttk.Button(listing, text="Togli", command=self.remove_selected).pack(side="left", padx=6)
        self.window.geometry("580x700")
        self.refresh_list()

    def last_phrase(self) -> str | None:
        """Il comando appena letto (o quello in lettura se non ce n'è uno prima)."""
        session = self.session or getattr(self, "_finished", None)
        if session is None:
            return None
        if session.results:
            return session.results[-1][0]
        return session.expected

    def change_word(self, ask=None):
        """Passo 11: un modo tuo di dire il comando (il comando standard resta valido)."""
        phrase = self.last_phrase()
        if phrase is None:
            self.status.set("Premi «Inizia» e leggi un comando, poi puoi cambiarne la parola.")
            return None
        if ask is None:
            from tkinter import simpledialog
            ask = lambda: simpledialog.askstring(
                "La mia voce", "Come vuoi dire «%s»?" % phrase, parent=self.window)
        new = ask()
        if not new or not new.strip():
            return None
        clash = conflitto(new)
        if clash and _norm(new) != _norm(phrase):
            self.status.set("Non la uso per non confondere i comandi: " + clash + ".")
            return None
        import command_aliases
        result = command_aliases.add_phrase("La mia voce", phrase, new.strip())
        self.status.set(result + " Anche «%s» resta valido." % phrase)
        return result

    def _lexicon(self):
        from adaptive_voice import SpeechCorrections
        return SpeechCorrections()

    def _save_letters(self):
        salva_facoltative([l for l, var in self.letters.items() if var.get()])

    def learn_typed(self):
        heard, meant = self.heard.get().strip(), self.meant.get().strip()
        if not heard or not meant:
            self.status.set("Scrivi cosa ha capito Lumi e cosa avevi detto.")
            return
        changed = " ".join(w for w in _norm(heard).split() if w not in _norm(meant).split())
        clash = conflitto(changed) if changed else ""
        if clash:
            self.status.set("Non imparo per non confondere i comandi: " + clash + ".")
            return
        try:
            source, target = self._lexicon().learn_phrase(heard, meant, user_confirmed=True)
        except Exception as exc:
            self.status.set("Non imparo: " + str(exc)[:100])
            return
        for callback in ON_LEARNED:
            try:
                callback()
            except Exception:
                pass
        self.status.set(f"Imparato: «{source}» → «{target}».")
        self.meant.set("")
        self.refresh_list()

    def refresh_list(self):
        self.list.delete(0, "end")
        try:
            self.items = self._lexicon().elenco()
        except Exception:
            self.items = []
        for heard, meant in self.items:
            self.list.insert("end", f"«{heard}» → «{meant}»")

    def remove_selected(self):
        if not self.list.curselection():
            return
        heard = self.items[self.list.curselection()[0]][0]
        try:
            self._lexicon().rimuovi(heard)
        except Exception as exc:
            self.status.set("Non tolta: " + str(exc)[:100])
            return
        for callback in ON_LEARNED:
            try:
                callback()
            except Exception:
                pass
        self.refresh_list()

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
        ask = ("  Va bene questa parola o la vuoi cambiare? («Cambia la parola…»)"
               if outcome and not outcome.startswith("Saltata") else "")
        self.status.set((outcome + ask + "   " if outcome else "") + f"Frase {min(done + 1, total)} di {total}.")
        if expected is None:
            learned = sum(1 for r in self.session.results if r[2].startswith("Imparato"))
            self.phrase.set("Fatto!")
            lost = lettere_perse(self.session.results)
            note = ""
            if lost:
                salva_facoltative(set(facoltative()) | set(lost))
                for letter in lost:
                    self.letters[letter].set(True)
                note = (" La tua voce perde spesso la " + ", ".join(l.upper() for l in lost)
                        + ": nei comandi non conterà (togli la spunta per annullare).")
            self.status.set(f"Finito: {learned} correzioni nuove su {total} frasi." + note)
            self._finished = self.session
            self.session = None
            self.refresh_list()
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
        PARZIALE["ascolta"] = None
        self.window.destroy()


def _ultima_frase() -> str:
    """L'ultima frase tua mostrata in chat (per correggerla a mano)."""
    try:
        from diagnostica_claude.ponte import RIGHE
        for _time, role, text in reversed(RIGHE):
            if role == "utente":
                return text
    except ImportError:
        pass
    return ""
