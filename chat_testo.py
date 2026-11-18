"""Testo della chat di Lumi in un solo file (riordino 060: unione di chat_ruoli, chat_link, chat_stream).

Tre parti, nessuna logica cambiata:
  1. ruoli  - classify(), IDENTITY, ROLES
  2. link   - segmenti(), ha_link(), inserisci()
  3. stream - ChatStream e lo STREAM unico (configurato da jarvis.main)
"""
from __future__ import annotations

from datetime import datetime
import queue
import re


# ======================================================================
# RUOLI: chi ha scritto un messaggio
# Chi ha scritto un messaggio della chat di Lumi (decisione 1A, 15/11).
#
# Prima il ruolo si indovinava dalle prime parole sparse in jarvis.py (bug del messaggio
# doppio: «UTENTE / VOCE >» finiva tra i messaggi di sistema). Ora è deciso qui, in un
# solo posto: chi scrive può passarlo esplicitamente (`write_line(testo, role="comando")`),
# altrimenti vale la tabella dei prefissi. Ruoli:
#   utente   — i tuoi messaggi
#   jarvis   — Lumi e i modelli che rispondono
#   comando  — risposta a un tuo comando (timer, musica, file, programmi…): resta in chat
#   azione   — operazione completata
#   errore   — errori
#   sistema  — messaggi interni (diagnostica, impostazioni…): in futuro solo in DIAGNOSTICA
# ======================================================================

ROLES = ("utente", "jarvis", "comando", "azione", "errore", "sistema")

_USER = ("utente >", "utente / voce >", "tu >", "domanda a gpt >", "comando locale >")
_LUMI = ("jarvis >", "gpt >", "lia >", "lumi >")
_ACTION = ("documento >", "[completed]", "correzione voce >")
# Risposte ai comandi: il nome prima di «>» diventa l'intestazione del messaggio.
_COMMAND = ("timer", "sveglia", "orologio", "musica", "programmi", "file", "accesso file",
            "controllo pc", "pc", "telegram", "modello locale", "modello off", "memoria",
            "documenti", "comando personale", "cervello", "progetti", "progetto",
            "diagnostica", "chat", "impostazioni", "componenti", "cervello locale spento")
# Solo questi sono interni: in chat non si vedono, restano in DIAGNOSTICA (15/11, passo 2a).
_INTERNAL = ("vocabolario lia",)

IDENTITY = {"utente": "●  TU", "jarvis": "◉  LUMI", "azione": "✓  OPERAZIONE",
            "errore": "!  ERRORE", "sistema": "·  SISTEMA", "comando": "▸  COMANDO"}


def classify(text: str, role: str | None = None) -> tuple[str, str, str]:
    """(ruolo, intestazione, corpo) per un messaggio della console."""
    label = str(text).strip()
    low = label.casefold()
    if role is None:
        if low.startswith(_USER):
            role = "utente"
        elif low.startswith(_ACTION):
            role = "azione"
        elif low.startswith(_LUMI):
            role = "jarvis"
        elif ("[failed]" in low or "[rejected]" in low
              or low.startswith(("errore", "gpt: impossibile", "microfono >"))
              or (" > " in label and label.split(" > ", 1)[0].strip().casefold().endswith(
                  ("/ errore", "/ configurazione")))):
            role = "errore"
        elif " > " in label and label.split(" > ", 1)[0].strip().casefold() in _INTERNAL:
            role = "sistema"
        else:
            # Tutto il resto è una risposta visibile: niente si perde dalla chat.
            role = "comando"
    elif role not in ROLES:
        role = "sistema"
    identity = IDENTITY[role]
    body = label
    for prefix in _USER + _LUMI + ("documento >", "correzione voce >"):
        if low.startswith(prefix):
            body = label[len(prefix):].strip()
            break
    if role == "comando":
        source, rest = label.split(" > ", 1) if " > " in label else ("LUMI", label)
        if len(source) > 40:                      # non è un prefisso: testo intero
            source, rest = "LUMI", label
        identity = "▸  " + source.strip().upper()
        body = rest.strip()
    return role, identity, body


# ======================================================================
# LINK cliccabili
# Link cliccabili nella chat (054): «[titolo](https://…)» e indirizzi nudi.
#
# La chat è un widget Text senza markdown: qui ogni link diventa un tag con sottolineatura,
# cursore a mano al passaggio e clic che apre il browser. Usato da write_line (jarvis.py).
# ======================================================================

COLORE = "#46ccfa"
_LINK = re.compile(r"\[([^\]\n]{1,200})\]\((https?://[^\s)]+)\)|(?<![(\w/])(https?://[^\s)<>\]]+)")


def segmenti(body: str) -> list[tuple[str, str | None]]:
    """[(testo, url o None)] nell'ordine: il testo di un link markdown è il titolo."""
    out, pos = [], 0
    for match in _LINK.finditer(body):
        if match.start() > pos:
            out.append((body[pos:match.start()], None))
        if match.group(2):
            out.append((match.group(1), match.group(2)))
        else:
            url = match.group(3).rstrip(".,;:!?")
            out.append((url, url))
            if len(match.group(3)) > len(url):
                out.append((match.group(3)[len(url):], None))
        pos = match.end()
    if pos < len(body):
        out.append((body[pos:], None))
    return out


def ha_link(body: str) -> bool:
    return _LINK.search(body) is not None


def inserisci(text, body: str, role: str, open_url, counter: list | None = None) -> dict:
    """Inserisce `body` in fondo al Text con i link cliccabili; ritorna {tag: url}."""
    counter = counter if counter is not None else _CONTATORE
    found = {}
    for piece, url in segmenti(body):
        if url is None:
            text.insert("end", piece, role)
            continue
        counter[0] += 1
        tag = "link_%d" % counter[0]
        text.tag_configure(tag, foreground=COLORE, underline=True)
        text.tag_bind(tag, "<Enter>", lambda _e: text.configure(cursor="hand2"))
        text.tag_bind(tag, "<Leave>", lambda _e: text.configure(cursor=""))
        text.tag_bind(tag, "<Button-1>", lambda _e, u=url: open_url(u))
        text.insert("end", piece, (role, tag))
        found[tag] = url
    return found


_CONTATORE = [0]


# ======================================================================
# STREAM: testo del modello in diretta e voce
# Live text of the local model in the console + voice from the first sentence.
#
# Configured once by jarvis.main(); until then every method is a harmless no-op,
# so the existing callbacks keep their behaviour (and their tests).
# ======================================================================

_SENTENCE_END = re.compile(r"[.!?…:;](?=\s)|\n")
_CLAUSE_END = re.compile(r",(?=\s)")


class ChatStream:
    def __init__(self):
        self.queue: queue.Queue = queue.Queue()
        self.output = None
        self.speak = None          # callable(text) -> bool, or None
        self.voice_enabled = lambda: False
        self.shown = False
        self.spoken = ""

    def configure(self, *, output, speak, voice_enabled) -> None:
        self.output, self.speak, self.voice_enabled = output, speak, voice_enabled

    # worker side -------------------------------------------------------
    def sink(self, epoch):
        if self.output is None:
            return None
        return lambda text: self.queue.put((text, epoch))

    # UI side -----------------------------------------------------------
    def start_request(self) -> None:
        self.spoken = ""

    def drain(self, epoch, active: bool) -> None:
        latest = None
        try:
            while True:
                text, item_epoch = self.queue.get_nowait()
                if item_epoch == epoch and active:
                    latest = text
        except queue.Empty:
            pass
        if latest is not None and self.output is not None:
            self._show(latest)
            self._speak_sentences(latest)

    def clear(self) -> None:
        if self.shown and self.output is not None:
            self.output.configure(state="normal")
            self.output.delete("lumi_stream_start", "lumi_stream_end")
            self.output.configure(state="disabled")
        self.shown = False

    def _show(self, text: str) -> None:
        out = self.output
        out.configure(state="normal")
        if self.shown:
            out.delete("lumi_stream_start", "lumi_stream_end")
        else:
            out.mark_set("lumi_stream_start", "end-1c")
            out.mark_gravity("lumi_stream_start", "left")
            out.mark_set("lumi_stream_end", "end-1c")
            out.mark_gravity("lumi_stream_end", "right")
            self.shown = True
        out.insert("lumi_stream_start",
                   "◉  LUMI         " + datetime.now().strftime("%H:%M:%S") + "  …\n",
                   ("jarvis", "message_head"))
        out.insert("lumi_stream_end", text.strip() + "\n\n", "jarvis")
        out.see("end")
        out.configure(state="disabled")

    def _speak_sentences(self, text: str) -> None:
        if self.speak is None or not self.voice_enabled():
            return
        done = self.spoken
        if not text.startswith(done):
            return
        rest = text[len(done):]
        last = None
        for match in _SENTENCE_END.finditer(rest):
            last = match
        if last is None:
            # Frase molto lunga: parte alla virgola, cosi' la voce non aspetta.
            if len(rest) < 140:
                return
            for match in _CLAUSE_END.finditer(rest):
                if match.end() >= 60:
                    last = match
        if last is None or len(rest[:last.end()].strip()) < 2:
            return
        chunk = rest[:last.end()]
        if self.speak(chunk.strip()):
            self.spoken = done + chunk

    def speak_final(self, text: str, speak_result) -> None:
        """Say only what streaming has not already said."""
        done, self.spoken = self.spoken, ""
        if not done:
            speak_result(text)
            return
        flat_text, flat_done = " ".join(text.split()), " ".join(done.split())
        if flat_text.startswith(flat_done):
            rest = flat_text[len(flat_done):].strip()
            if rest:
                speak_result(rest)


STREAM = ChatStream()
