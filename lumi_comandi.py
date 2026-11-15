"""Comandi a voce su Lumi stessa: riduci a icona, chiudi, riavvia, nascondi/sveglia
l'avatar, spegni il PC (solo detto esplicitamente e con conferma).

Funzionano anche con Lumi ridotta a icona (il microfono resta attivo).
jarvis.py registra le azioni (register); qui nessuna variabile nuova nelle sue funzioni.
"""
from __future__ import annotations

import re
import time

_WAKE = re.compile(r"^\s*(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*", re.IGNORECASE)
_END = r"[\s.!?]*$"
_PATTERNS = (
    # «minimizza» da solo resta del Controllo PC (finestra in uso): qui solo forme
    # riferite a Lumi.
    ("minimize", re.compile(r"^(?:minimizzati|riduciti|riduci\s+a\s+icona|"
                            r"mettiti\s+(?:da\s+parte|in\s+basso))" + _END, re.I)),
    ("minimize", re.compile(r"^(?:minimizza|riduci\s+a\s+icona|riduci)\s+(?:lumi|jarvis)" + _END, re.I)),
    ("close", re.compile(r"^(?:chiudi(?:ti)?|spegni(?:ti)?|esci\s+da|termina)\s+(?:lumi|jarvis)" + _END, re.I)),
    ("close", re.compile(r"^(?:chiuditi|spegniti)" + _END, re.I)),
    ("restart", re.compile(r"^(?:riavvia(?:ti)?)(?:\s+lumi|\s+jarvis)?" + _END, re.I)),
    ("shutdown_pc", re.compile(r"^spegni\s+(?:il\s+)?(?:pc|computer)" + _END, re.I)),
    ("cancel_shutdown", re.compile(r"^annulla\s+(?:lo\s+)?spegnimento" + _END, re.I)),
    ("hide", re.compile(r"^(?:nascondi(?:ti)?|nascondi\s+(?:l'\s*)?avatar|sparisci)" + _END, re.I)),
    # Cervelli: locale (Gemma sul PC) e online (GPT e futuri gratuiti), con o senza articolo.
    ("brain_local_on", re.compile(
        r"^(?:(?:attiva|accendi|riattiva|abilita)\s+(?:il\s+)?cervello\s+locale|"
        r"(?:il\s+)?cervello\s+locale\s+(?:on|acceso|attivo))" + _END, re.I)),
    ("brain_local_off", re.compile(
        r"^(?:(?:spegni|disattiva|disabilita)\s+(?:il\s+)?cervello\s+locale|"
        r"(?:il\s+)?cervello\s+locale\s+(?:off|spento))" + _END, re.I)),
    ("brain_online_on", re.compile(
        r"^(?:(?:attiva|accendi|riattiva|abilita)\s+(?:il\s+)?cervello\s+online|"
        r"(?:il\s+)?cervello\s+online\s+(?:on|acceso|attivo))" + _END, re.I)),
    ("brain_online_off", re.compile(
        r"^(?:(?:spegni|disattiva|disabilita)\s+(?:il\s+)?cervello\s+online|"
        r"(?:il\s+)?cervello\s+online\s+(?:off|spento))" + _END, re.I)),
    ("model_restart", re.compile(
        r"^(?:riavvia|ricarica)\s+(?:il\s+)?(?:modello(?:\s+locale)?|cervello\s+locale|motore)"
        + _END, re.I)),
    ("tutorial_skip", re.compile(r"^(?:salta(?:\s+il)?\s+passo|passo\s+successivo)" + _END, re.I)),
    ("tutorial_stop", re.compile(r"^(?:esci\s+dal\s+tutorial|basta\s+tutorial|chiudi\s+il\s+tutorial)"
                                 + _END, re.I)),
    ("tutorial_start", re.compile(r"^(?:avvia|fammi|inizia|fai)\s+(?:il\s+)?tutorial" + _END, re.I)),
    ("data_cleanup", re.compile(
        r"^(?:apri\s+)?(?:la\s+)?(?:pulizia(?:\s+(?:dei\s+)?dati)?|libera\s+spazio(?:\s+su\s+disco)?)"
        + _END, re.I)),
    ("attachments_clear", re.compile(
        r"^(?:togli|rimuovi|elimina|cancella)\s+(?:gli\s+|l'\s*|tutti\s+gli\s+)?allegat[oi]"
        + _END, re.I)),
    ("wake", re.compile(r"^(?:svegliati|sveglia|torna\s+qui|fatti\s+vedere|mostrati|"
                        r"mostra\s+(?:l'\s*)?avatar)" + _END, re.I)),
)
_ALWAYS = {"sempre", "sempre attivo", "tienilo attivo", "tienilo acceso", "sì sempre", "si sempre",
           "finché non lo spengo", "fino a quando non lo spengo"}
_YES = {"si", "sì", "conferma", "confermo", "ok", "va bene", "certo", "procedi"}
_NO = {"no", "annulla", "lascia stare", "no grazie"}

_STATE = {"actions": None, "pending": None, "is_hidden_ui": lambda: False}


def parse(text: str):
    if not isinstance(text, str) or len(text) > 80:
        return None
    value = _WAKE.sub("", text).strip()
    for action, pattern in _PATTERNS:
        if pattern.match(value):
            return action
    return None


def register(actions: dict, is_hidden_ui) -> None:
    """actions: minimize, close, restart, shutdown_pc, hide, wake → funzioni senza argomenti.
    is_hidden_ui(): True se Lumi è ridotta a icona o l'avatar è nascosto."""
    _STATE.update(actions=actions, is_hidden_ui=is_hidden_ui, pending=None)


def handle_text(spoken: str, write_line, speak) -> bool:
    actions = _STATE["actions"]
    if actions is None:
        return False
    from frasi_lumi import say
    pending = _STATE["pending"]
    if pending is not None:
        _STATE["pending"] = None
        action, deadline, *rest = pending
        no_action = rest[0] if rest else None
        always_action = rest[1] if len(rest) > 1 else None
        word = " ".join(_WAKE.sub("", spoken).casefold().strip(" .!?").split())
        import risposte
        if (time.monotonic() <= deadline and always_action in actions
                and word in _ALWAYS):
            actions[always_action]()
            return True
        if time.monotonic() <= deadline and (word in _YES or risposte.is_yes(spoken)):
            actions[action]()
            return True
        if (time.monotonic() <= deadline and no_action in actions
                and (word in _NO or risposte.is_no(spoken))):
            actions[no_action]()
            return True
        if time.monotonic() <= deadline and (word in _NO or risposte.is_no(spoken)):
            reply = say("annullato")
            write_line("LUMI > " + reply)
            speak(reply)
            return True
    github = actions.get("github")          # add-on GitHub in sola lettura (passo 9)
    if github is not None and __import__("github_lettura").parse(spoken) and github(spoken):
        return True
    stop_all = actions.get("stop_all")
    if stop_all is not None and __import__("stato_lumi").is_stop(spoken) and stop_all():
        return True
    action = parse(spoken)
    if action is None:
        return False
    # «sveglia» / «Lumi, sveglia» riapre SEMPRE Lumi (richiesta utente): la sveglia
    # dell'add-on si imposta solo con «imposta/metti la sveglia (alle …)».
    if action in ("restart", "shutdown_pc"):
        _STATE["pending"] = (action, time.monotonic() + 60)
        question = ("Mi riavvio adesso? Di' sì o no." if action == "restart" else
                    "Spengo davvero il computer? Salva prima il tuo lavoro. Di' sì o no.")
        write_line("LUMI > " + question)
        speak(question)
        import risposte
        risposte.expect_answer(speech_text=question)
        return True
    actions[action]()
    return True


def chiedi(action: str, question: str, write_line, speak, seconds: float = 60,
           no_action: str | None = None, always_action: str | None = None) -> None:
    """Domanda sì/no per un'azione registrata (es. «help_off»): sì la esegue; no esegue
    `no_action` se c'è, altrimenti «annullato»; «sempre» esegue `always_action` se c'è."""
    _STATE["pending"] = (action, time.monotonic() + seconds, no_action, always_action)
    write_line("LUMI > " + question)
    speak(question)
    import risposte
    # «sì»/«no» senza dire «Lumi» (punto 10): finestra di 20 s dopo la domanda, non di più,
    # perché intanto il riconoscimento ascolta solo le parole di risposta.
    risposte.expect_answer(seconds=20, speech_text=question)


def run_action(action: str) -> bool:
    """Esegue un'azione su Lumi registrata da jarvis.py (es. «minimize»); False se manca.
    Usata dal Controllo PC: le finestre di Lumi (senza cornice di Windows) non vanno
    ridotte con ShowWindow, che le nasconde senza icona e sembrano chiuse."""
    actions = _STATE["actions"] or {}
    if action not in actions:
        return False
    actions[action]()
    return True
