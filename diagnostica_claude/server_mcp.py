"""Server MCP (stdio) «Diagnostica per Claude»: lo avvia Claude desktop.

Non tocca il PC: inoltra le richieste al ponte di Lumi (127.0.0.1, chiave nel file
%LOCALAPPDATA%\\Jarvis\\diagnostica_claude.json, presente solo con l'add-on acceso).
Nessuna dipendenza: JSON-RPC 2.0 una riga per messaggio, come da specifica MCP stdio.
"""
from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path

VERSIONE_PROTOCOLLO = "2025-06-18"

STRUMENTI = [
    {"name": "lumi_stato", "description": "Stato di Lumi: microfono, modello, GPT, occupato.",
     "op": "stato", "props": {}},
    {"name": "lumi_console", "description": "Ultime righe della console/chat di Lumi.",
     "op": "console", "props": {"righe": {"type": "integer", "description": "quante (max 400)"}}},
    {"name": "lumi_errori", "description": "Ultimi errori mostrati da Lumi.",
     "op": "errori", "props": {"righe": {"type": "integer"}}},
    {"name": "lumi_log_motore", "description": "Coda di motore.log del modello locale.",
     "op": "log_motore", "props": {"righe": {"type": "integer"}}},
    {"name": "lumi_scrivi_in_chat", "description": "Scrive un messaggio nella chat di Lumi.",
     "op": "scrivi_in_chat", "props": {"testo": {"type": "string"}}, "required": ["testo"]},
    {"name": "lumi_prova_comando",
     "description": ("Prova un comando come se l'utente l'avesse scritto in Lumi. Solo comandi "
                     "dentro Lumi: Controllo PC, programmi e file sono rifiutati."),
     "op": "prova_comando", "props": {"testo": {"type": "string"}}, "required": ["testo"]},
    {"name": "lumi_riavvia_modello", "description": "Riavvia il modello locale di Lumi.",
     "op": "riavvia_modello", "props": {}},
    # 15/11 sera: strumenti per le novità (regola: diagnostica sempre aggiornata).
    {"name": "lumi_impostazioni",
     "description": ("Impostazioni di Lumi: senza argomenti elenca categorie e voci; con "
                     "categoria (e voce) apre la finestra delle impostazioni in quel punto."),
     "op": "impostazioni", "props": {"categoria": {"type": "string"}, "voce": {"type": "string"}}},
    {"name": "lumi_addon",
     "description": ("Add-on di Lumi: elenco con stato acceso/spento; con id e acceso "
                     "(true/false) li accende o spegne come l'interruttore nelle impostazioni."),
     "op": "addon", "props": {"id": {"type": "string"}, "acceso": {"type": "boolean"}}},
    {"name": "lumi_ricordi", "description": "Ricordi salvati da Lumi (sola lettura), con ricerca.",
     "op": "ricordi", "props": {"cerca": {"type": "string"},
                                "categoria": {"type": "string"}}},
    {"name": "lumi_chat",
     "description": ("Chat del menu laterale con i simboli dei modelli (🤖 offline, 📡 online) e "
                     "gli ultimi scambi della chat aperta (sola lettura)."),
     "op": "chat", "props": {"scambi": {"type": "integer", "description": "quanti (max 32)"}}},
]
PER_NOME = {t["name"]: t for t in STRUMENTI}


def percorso_porta() -> Path:
    local = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(local) / "Jarvis" / "diagnostica_claude.json"


def chiedi_al_ponte(op: str, args: dict, path: Path | None = None, timeout: float = 15) -> dict:
    try:
        info = json.loads((path or percorso_porta()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"ok": False, "errore": "Lumi non è aperta o l'add-on Diagnostica per Claude è spento."}
    try:
        with socket.create_connection(("127.0.0.1", int(info["port"])), timeout=timeout) as conn:
            conn.sendall(json.dumps({"token": info["token"], "op": op, "args": args}).encode("utf-8") + b"\n")
            data = b""
            while b"\n" not in data:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                data += chunk
        return json.loads(data.split(b"\n", 1)[0].decode("utf-8"))
    except (OSError, ValueError, KeyError, TypeError):
        return {"ok": False, "errore": "Lumi non risponde."}


def gestisci(message: dict, ask=chiedi_al_ponte):
    """Risposta JSON-RPC (dict) oppure None per le notifiche."""
    method, ident = message.get("method"), message.get("id")
    if ident is None:
        return None
    if method == "initialize":
        version = (message.get("params") or {}).get("protocolVersion") or VERSIONE_PROTOCOLLO
        result = {"protocolVersion": version, "capabilities": {"tools": {}},
                  "serverInfo": {"name": "lumi-diagnostica", "version": "1.0"}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [{"name": t["name"], "description": t["description"],
                             "inputSchema": {"type": "object", "properties": t["props"],
                                             "required": t.get("required", [])}}
                            for t in STRUMENTI]}
    elif method == "tools/call":
        params = message.get("params") or {}
        tool = PER_NOME.get(params.get("name"))
        if tool is None:
            return {"jsonrpc": "2.0", "id": ident,
                    "error": {"code": -32602, "message": "Strumento sconosciuto"}}
        reply = ask(tool["op"], params.get("arguments") or {})
        ok = bool(reply.get("ok"))
        text = json.dumps({k: v for k, v in reply.items() if k != "ok"}, ensure_ascii=False, indent=1)
        result = {"content": [{"type": "text", "text": text if ok else reply.get("errore", text)}],
                  "isError": not ok}
    else:
        return {"jsonrpc": "2.0", "id": ident, "error": {"code": -32601, "message": "Metodo non supportato"}}
    return {"jsonrpc": "2.0", "id": ident, "result": result}


def main(stdin=sys.stdin, stdout=sys.stdout) -> None:
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            continue
        reply = gestisci(message) if isinstance(message, dict) else None
        if reply is not None:
            stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            stdout.flush()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")
    main()
