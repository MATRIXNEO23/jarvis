"""Chi ha scritto un messaggio della chat di Lumi (decisione 1A, 15/11).

Prima il ruolo si indovinava dalle prime parole sparse in jarvis.py (bug del messaggio
doppio: «UTENTE / VOCE >» finiva tra i messaggi di sistema). Ora è deciso qui, in un
solo posto: chi scrive può passarlo esplicitamente (`write_line(testo, role="comando")`),
altrimenti vale la tabella dei prefissi. Ruoli:
  utente   — i tuoi messaggi
  jarvis   — Lumi e i modelli che rispondono
  comando  — risposta a un tuo comando (timer, musica, file, programmi…): resta in chat
  azione   — operazione completata
  errore   — errori
  sistema  — messaggi interni (diagnostica, impostazioni…): in futuro solo in DIAGNOSTICA
"""
from __future__ import annotations

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
