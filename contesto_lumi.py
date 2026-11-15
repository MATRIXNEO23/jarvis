"""Sezione «Contesto» (passo 4, 15/11): cosa riceve il modello locale oltre alla domanda.

- Cronologia: sempre quella della chat selezionata nell'elenco (chat unica).
- «Chat continua» (spenta di serie): come KoboldCpp, l'inizio del prompt resta fisso e i
  messaggi si accodano; quando il contesto è pieno i più vecchi escono a blocchi di
  BLOCCO scambi, così per molti turni l'inizio non cambia e il fast forwarding del
  motore riusa il lavoro già fatto (sul Pavilion conta). Usa il contesto del modello,
  non il tetto «token cronologia» della chat normale.
- Ricordi (Second Brain / progetto): «mai», «se pertinenti» (predefinito: solo i ricordi
  trovati cercando le parole della domanda, niente «ultimi scambi» generici che la
  cronologia della chat già contiene), «sempre» (come prima del 15/11).

Il riassunto automatico dei vecchi scambi non c'è: richiede una generazione in più del
modello (lenta sull'i3); i vecchi escono interi a blocchi. Il contesto per i servizi
online si regola con il passo 8 (servizi online).
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

BLOCCO = 8
MAX_SCAMBI = 32          # tetto di lettura dell'archivio (ChatSessionStore.recent_pairs)
RICORDI = ("mai", "pertinenti", "sempre")
RICORDI_ETICHETTE = {"mai": "Mai", "pertinenti": "Se pertinenti alla domanda",
                     "sempre": "Sempre"}


@dataclass(frozen=True)
class Contesto:
    chat_continua: bool = False
    ricordi_locale: str = "pertinenti"

    def validate(self) -> "Contesto":
        if type(self.chat_continua) is not bool or self.ricordi_locale not in RICORDI:
            raise ValueError("Impostazioni contesto non valide.")
        return self


def percorso() -> Path:
    trial = os.environ.get("JARVIS_TRIAL_HOME")
    if trial:
        return Path(trial) / "contesto.json"
    local = os.environ.get("LOCALAPPDATA")
    if not local:
        raise RuntimeError("LOCALAPPDATA non disponibile.")
    return Path(local) / "Jarvis" / "contesto.json"


def carica(path: Path | None = None) -> Contesto:
    """Valori iniziali se il file manca o è danneggiato (non viene riscritto)."""
    try:
        path = path or percorso()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return Contesto()
        known = {k: data[k] for k in Contesto.__dataclass_fields__ if k in data}
        return Contesto(**known).validate()
    except (OSError, RuntimeError, ValueError, TypeError, UnicodeError):
        return Contesto()


def salva(value: Contesto, path: Path | None = None) -> None:
    value.validate()
    path = Path(path or percorso())
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(asdict(value), stream, indent=2)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def filtra_ricordi(raw: str, mode: str) -> str:
    """Applica la scelta «Ricordi» al JSON di Second Brain o del progetto."""
    if mode == "sempre" or not raw:
        return raw
    if mode == "mai":
        return ""
    try:
        value = json.loads(raw)
    except ValueError:
        return ""
    if not isinstance(value, dict):
        return ""
    value.pop("recent", None)
    if not any(value.get(key) for key in ("related", "evidence")):
        # Niente trovato per questa domanda: nessun ricordo (lo stato del progetto
        # resta, è il contesto stesso del progetto attivo).
        value = {k: v for k, v in value.items() if k in ("project", "state", "steps")}
    if not any(value.values()):
        return ""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def finestra_continua(total_pairs, recent_pairs, fits):
    """Scambi per la «chat continua», o None se non c'è niente da usare.

    total_pairs(): scambi nella chat; recent_pairs(n): ultimi n in ordine;
    fits(storia): True se il prompt con quella storia sta nel contesto.
    L'inizio scelto è un multiplo di BLOCCO: cambia solo quando il contesto si riempie.
    """
    total = total_pairs()
    if type(total) is not int or total <= 0:
        return None
    count = min(total, MAX_SCAMBI)
    pairs = list(recent_pairs(count))
    if not pairs:
        return None
    first = total - len(pairs)                  # indice assoluto del primo letto
    start = -(-first // BLOCCO) * BLOCCO        # primo multiplo di BLOCCO leggibile
    while start < total:
        history = pairs[start - first:]
        if fits(history):
            return history, {"whole": len(history), "extracted": 0,
                             "omitted": total - len(history), "continua_inizio": start}
        start += BLOCCO
    return None


_ULTIMA_CHAT = [None]


def lettore_chat(reader, *, forget=None, settings: Contesto | None = None):
    """Lettore per NativeConversationSession.prepare_turn con la chat selezionata.

    reader: lettore dei ricordi esistente (o None); forget(): svuota la cronologia in
    RAM del modello quando si cambia chat, così si rilegge quella giusta dall'archivio.
    """
    import chat_elenco
    settings = settings or carica()
    elenco = chat_elenco._CURRENT["elenco"]
    chat_id = elenco.current() if elenco is not None else None
    if chat_id != _ULTIMA_CHAT[0]:
        _ULTIMA_CHAT[0] = chat_id
        if forget is not None:
            forget()

    def read(budget):
        raw = reader(budget) if reader is not None else ""
        return filtra_ricordi(raw, settings.ricordi_locale)

    for name in ("diagnostic_history_source", "diagnostic_recall_source"):
        if hasattr(reader, name):
            setattr(read, name, getattr(reader, name))
    if chat_id is not None:
        store, scope = elenco.store, elenco._scope()
        read.recent_pairs = lambda count: store.recent_pairs(
            chat_id, project_id=scope, count=max(1, min(int(count), MAX_SCAMBI)))
        read.total_pairs = lambda: store.exchange_count(chat_id, project_id=scope)
        read.continuous = settings.chat_continua
        read.diagnostic_history_source = "Chat selezionata (chat_elenco)" + (
            ", chat continua" if settings.chat_continua else "")
    elif reader is not None and hasattr(reader, "recent_pairs"):
        read.recent_pairs = reader.recent_pairs
    return read


def costruisci_sezione(parent, notify):
    """Riquadro «Contesto» nelle Impostazioni; salva subito a ogni modifica."""
    import tkinter as tk
    from tkinter import ttk
    current = carica()
    box = ttk.LabelFrame(parent, text="Contesto del modello locale")
    box.pack(fill="x", padx=8, pady=8)
    ttk.Label(box, wraplength=540, text=(
        "La cronologia è quella della chat scelta nell'elenco (☰). «Chat continua»: come "
        "KoboldCpp, l'inizio resta fisso e i messaggi si accodano, i più vecchi escono a "
        "blocchi solo a contesto pieno; risposte più veloci nelle chat lunghe, più memoria "
        "usata.")).pack(anchor="w", padx=8, pady=5)
    continua = tk.BooleanVar(value=current.chat_continua)
    labels = [RICORDI_ETICHETTE[k] for k in RICORDI]
    ricordi = tk.StringVar(value=RICORDI_ETICHETTE[current.ricordi_locale])

    def save(*_):
        mode = RICORDI[labels.index(ricordi.get())] if ricordi.get() in labels else "pertinenti"
        try:
            salva(Contesto(chat_continua=continua.get(), ricordi_locale=mode))
        except (OSError, RuntimeError, ValueError) as exc:
            notify("CONTESTO / ERRORE > Scelta non salvata: " + str(exc)[:120])
            return
        notify("CONTESTO > Salvato: vale dalla prossima domanda.")

    ttk.Checkbutton(box, text="Chat continua (come KoboldCpp)", variable=continua,
                    command=save).pack(anchor="w", padx=8, pady=(0, 4))
    row = ttk.Frame(box)
    row.pack(fill="x", padx=8, pady=(0, 8))
    ttk.Label(row, text="Ricordi di Second Brain e del progetto:").pack(side="left")
    combo = ttk.Combobox(row, textvariable=ricordi, values=labels, state="readonly", width=28)
    combo.pack(side="left", padx=6)
    combo.bind("<<ComboboxSelected>>", save)
    return box


def altre_chat(max_chats: int = 3, pairs: int = 2, limit: int = 600) -> list[str]:
    """Le chat dello stesso progetto si vedono tra loro (15/11 sera): gli ultimi scambi
    delle altre chat del progetto attivo, corti, come dati di riferimento."""
    import chat_elenco
    elenco = chat_elenco._CURRENT["elenco"]
    if elenco is None:
        return []
    project = elenco._scope()
    if project is None:
        return []
    current = elenco.current()
    out = []
    try:
        chats = [c for c in elenco.store.list_chats(project_id=project) if c.id != current]
        for chat in chats[:max_chats]:
            recent = elenco.store.recent_pairs(chat.id, project_id=project, count=pairs)
            if recent:
                lines = ["Tu: %s\nLumi: %s" % (q[1][:limit // 2], a[1][:limit // 2]) for q, a in recent]
                out.append("[Altra chat del progetto: %s]\n%s" % (chat.title, "\n".join(lines)))
    except Exception:
        return []
    return out
