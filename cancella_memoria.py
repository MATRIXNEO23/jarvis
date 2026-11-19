"""Cancellazione della memoria a sezioni (decisione utente 17/11): l'utente sceglie che
cosa cancellare. Sezioni: chat, ricordi, progetti, tutto. Ogni cancellazione chiede
conferma sì/no (pulsante o voce) con un messaggio in parole semplici."""
from __future__ import annotations

import re

SEZIONI = ("chat", "ricordi", "progetti", "tutto")
ETICHETTE = {"chat": "Cancella chat", "ricordi": "Cancella ricordi",
             "progetti": "Cancella progetti", "tutto": "Cancella tutto"}
COMANDI = {"chat": "cancella le chat", "ricordi": "cancella i ricordi",
           "progetti": "cancella i progetti", "tutto": "cancella tutto"}
_CHAT = ("le conversazioni salvate da Lia, le ricevute delle operazioni e le "
         "correzioni vocali imparate")
_RICORDI = "tutti i ricordi che Lia ha salvato su di te, sulle persone e sulle cose da fare"
_PROGETTI = ("tutti i progetti con le loro chat, i loro ricordi e le loro cartelle "
             "(le cartelle vanno nel Cestino di Windows)")
MESSAGGI = {
    "chat": "Cancello " + _CHAT + ". I ricordi e i progetti restano.",
    "ricordi": "Cancello " + _RICORDI + ". Le chat e i progetti restano.",
    "progetti": "Cancello " + _PROGETTI + ". Le altre chat e i ricordi generali restano.",
    "tutto": "Cancello tutto: " + _CHAT + "; " + _RICORDI + "; " + _PROGETTI + ".",
}
FATTO = {"chat": "Chat e correzioni vocali cancellate.", "ricordi": "Ricordi cancellati.",
         "progetti": "Progetti cancellati.", "tutto": "Chat, ricordi e progetti cancellati."}


def domanda(sezione: str) -> str:
    return MESSAGGI[sezione] + " Non si può annullare. Confermi? Di' sì o no."


_PREFISSO = re.compile(r"^\W*(?:(?:ehi|ok)\s+)?lumi\W+", re.I)
_VERBO = r"(?:cancella|elimina|svuota|dimentica)"
_COMANDO = re.compile(
    r"^" + _VERBO + r"\s+(?:(?:tutte?\s+)?(?:le\s+)?(?P<chat>chat|conversazioni)"
    r"|(?:tutti\s+)?(?:i\s+)?(?P<ricordi>ricordi)"
    r"|(?:tutti\s+)?(?:i\s+)?(?P<progetti>progetti)"
    r"|(?P<tutto>tutto|tutta\s+la\s+memoria|la\s+memoria))$", re.I)


def parse(text: str) -> str | None:
    """Frase a voce -> sezione, oppure None. Solo frasi complete e esplicite."""
    t = _PREFISSO.sub("", (text or "").strip()).strip(" .!?,;:")
    m = _COMANDO.match(t)
    if not m:
        return None
    return next(k for k in SEZIONI if m.group(k))


def esegui(sezione: str, brain, workspace=None, store=None, trash_folders=None) -> str:
    """Esegue la cancellazione già confermata; ritorna il messaggio finale."""
    if sezione not in SEZIONI:
        raise ValueError(sezione)
    if sezione in ("progetti", "tutto") and workspace is not None and store is not None:
        import menu_laterale
        menu_laterale.cancella_tutti_i_progetti(
            workspace, store, trash_folders=trash_folders, brain=brain)
    if sezione in ("chat", "tutto"):
        brain.clear_all()
    if sezione in ("ricordi", "tutto"):
        brain.clear_ricordi()
    return FATTO[sezione]
