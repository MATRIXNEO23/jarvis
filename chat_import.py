"""Importa UNA conversazione da un export ufficiale di ChatGPT o Claude (passo 9).

L'export si scarica dal sito (ChatGPT: Impostazioni → Controlli dati → Esporta;
Claude: Impostazioni → Privacy → Esporta dati) e contiene `conversations.json`.
Lumi mostra l'elenco dei titoli, ne importi una: diventa una chat di Lumi nel progetto
attivo (o in «Generale»). Si legge solo il file scelto; niente accesso ai siti.
Formati:
- ChatGPT: lista di {title, mapping: {id: {message: {author: {role}, content: {parts}},
  parent, children}}, current_node}.
- Claude: lista di {name, chat_messages: [{sender: human|assistant, text | content}]}.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

MAX_BYTES = 200 * 1024 * 1024
LIMITE = 16000           # limite di un messaggio nell'archivio di Lumi (16384)


class ImportError_(ValueError):
    pass


def carica(path) -> list:
    """Le conversazioni dal file .json o dallo .zip dell'export."""
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ImportError_("File troppo grande.")
    try:
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                name = next((n for n in archive.namelist()
                             if n.rsplit("/", 1)[-1] == "conversations.json"), None)
                if name is None:
                    raise ImportError_("Nello zip manca conversations.json.")
                data = json.loads(archive.read(name).decode("utf-8"))
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, zipfile.BadZipFile) as exc:
        if isinstance(exc, ImportError_):
            raise
        raise ImportError_("File non leggibile come export di chat.") from exc
    if isinstance(data, dict) and isinstance(data.get("conversations"), list):
        data = data["conversations"]
    if not isinstance(data, list):
        raise ImportError_("Formato non riconosciuto.")
    return [c for c in data if isinstance(c, dict)]


def titolo(conversation: dict) -> str:
    return str(conversation.get("title") or conversation.get("name") or "Chat importata").strip()[:80]


def _testo(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        if isinstance(content.get("parts"), list):
            return "\n".join(_testo(p) for p in content["parts"] if _testo(p))
        return str(content.get("text") or "")
    if isinstance(content, list):
        return "\n".join(_testo(p) for p in content if _testo(p))
    return ""


def messaggi(conversation: dict) -> list[tuple[str, str]]:
    """[(«user»|«assistant», testo)] in ordine."""
    out = []
    if isinstance(conversation.get("mapping"), dict):            # ChatGPT
        mapping = conversation["mapping"]
        node = conversation.get("current_node")
        chain = []
        while node in mapping and len(chain) < 100_000:
            chain.append(mapping[node])
            node = mapping[node].get("parent")
        for item in reversed(chain):
            message = item.get("message") or {}
            role = (message.get("author") or {}).get("role")
            text = _testo(message.get("content")).strip()
            if role in ("user", "assistant") and text:
                out.append((role, text))
    elif isinstance(conversation.get("chat_messages"), list):     # Claude
        for message in conversation["chat_messages"]:
            if not isinstance(message, dict):
                continue
            role = {"human": "user", "assistant": "assistant"}.get(message.get("sender"))
            text = (message.get("text") or _testo(message.get("content"))).strip()
            if role and text:
                out.append((role, text))
    return out


def scambi(conversation: dict) -> list[tuple[str, str]]:
    """Coppie domanda/risposta (domande o risposte di fila vengono unite)."""
    pairs, question, answer = [], [], []
    for role, text in messaggi(conversation):
        if role == "user":
            if answer:
                pairs.append(("\n\n".join(question) or "(senza domanda)", "\n\n".join(answer)))
                question, answer = [], []
            question.append(text)
        else:
            answer.append(text)
    if question and answer:
        pairs.append(("\n\n".join(question), "\n\n".join(answer)))
    return [(q[:LIMITE], a[:LIMITE]) for q, a in pairs]


def importa(conversation: dict, store, *, project_id=None) -> tuple[str, int]:
    """Crea la chat nell'archivio di Lumi; (id della chat, scambi importati)."""
    pairs = scambi(conversation)
    if not pairs:
        raise ImportError_("La conversazione non ha scambi da importare.")
    info = store.create_chat(titolo(conversation)[:60], project_id=project_id, activate=True)
    for question, answer in pairs:
        store.append_exchange(info.id, question, answer, project_id=project_id)
    return info.id, len(pairs)


def scegli_dialogo(parent, conversations: list):
    """Finestra con l'elenco dei titoli; restituisce la conversazione scelta o None."""
    import tkinter as tk
    from tkinter import ttk
    window = tk.Toplevel(parent)
    window.title("Lumi // Importa una chat")
    window.geometry("520x420")
    ttk.Label(window, text="Scegli la conversazione da importare:").pack(anchor="w", padx=10, pady=6)
    box = tk.Listbox(window, activestyle="none", exportselection=False)
    box.pack(fill="both", expand=True, padx=10)
    for conversation in conversations:
        box.insert("end", titolo(conversation))
    chosen = {"value": None}

    def ok(_event=None):
        if box.curselection():
            chosen["value"] = conversations[box.curselection()[0]]
        window.destroy()

    box.bind("<Double-Button-1>", ok)
    row = ttk.Frame(window)
    row.pack(fill="x", padx=10, pady=8)
    ttk.Button(row, text="Importa", command=ok).pack(side="right")
    ttk.Button(row, text="Annulla", command=window.destroy).pack(side="right", padx=6)
    window.transient(parent)
    window.grab_set()
    parent.wait_window(window)
    return chosen["value"]
