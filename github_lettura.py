"""Add-on «GitHub» in sola lettura (passo 9): API REST ufficiali con la chiave dell'utente.

Spento di serie (Impostazioni → GPT e memoria → «GitHub (sola lettura)»). Comandi:
- «i miei repository» / «repository GitHub»
- «issue aperte di <repository>» / «problemi aperti di <repository>»
- «ultimi commit di <repository>»
Il nome del repository può essere «proprietario/nome» o solo il nome di uno dei tuoi.
Gli elenchi si vedono in chat e non vengono letti a voce (regola: elenchi mai recitati).
Chiave (token «fine-grained» con sola lettura) cifrata DPAPI nel profilo. Nessuna
scrittura su GitHub: solo richieste GET.
"""
from __future__ import annotations

import base64
import json
import os
import re
import urllib.request
from pathlib import Path

API = "https://api.github.com"
_END = r"[\s.!?]*$"
_REPOS = re.compile(r"^(?:mostra\s+|elenca\s+)?(?:i\s+)?(?:miei\s+)?repository(?:\s+(?:su\s+)?github)?"
                    + _END, re.I)
_ISSUES = re.compile(r"^(?:mostra\s+)?(?:le\s+)?(?:issue|problemi)(?:\s+aperti|\s+aperte)?\s+(?:di|del|su)\s+"
                     r"(?P<repo>[\w.\-/ ]{1,100}?)" + _END, re.I)
_COMMITS = re.compile(r"^(?:mostra\s+)?(?:gli\s+)?ultimi\s+commit\s+(?:di|del|su)\s+"
                      r"(?P<repo>[\w.\-/ ]{1,100}?)" + _END, re.I)
_WAKE = re.compile(r"^\s*(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*", re.I)


def parse(text: str):
    """(«repos», None) | («issues», repo) | («commits», repo) | None."""
    if not isinstance(text, str) or len(text) > 140:
        return None
    value = _WAKE.sub("", text).strip()
    if _REPOS.match(value):
        return "repos", None
    for kind, pattern in (("issues", _ISSUES), ("commits", _COMMITS)):
        match = pattern.match(value)
        if match:
            return kind, match.group("repo").strip()
    return None


def _cartella() -> Path:
    from settings import default_path
    return default_path().parent


class Configurazione:
    def __init__(self, folder: Path | None = None, protect=None):
        self.folder = folder
        if protect is None:
            from online.servizi_online import _dpapi
            protect = _dpapi
        self.protect = protect

    def _file(self) -> Path:
        return (self.folder or _cartella()) / "github.json"

    def _load(self) -> dict:
        try:
            data = json.loads(self._file().read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, RuntimeError):
            return {}

    def _save(self, data: dict) -> None:
        path = self._file()
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        temp.write_text(json.dumps(data), encoding="utf-8")
        os.replace(temp, path)

    @property
    def attivo(self) -> bool:
        return self._load().get("attivo") is True

    def imposta_attivo(self, on: bool) -> None:
        data = self._load()
        data["attivo"] = bool(on)
        self._save(data)

    def token(self) -> str:
        blob = self._load().get("token")
        if not blob:
            return ""
        try:
            return self.protect(base64.b64decode(blob), False).decode("utf-8")
        except Exception:
            return ""

    def salva_token(self, token: str) -> None:
        data = self._load()
        token = (token or "").strip()
        if token:
            data["token"] = base64.b64encode(self.protect(token.encode("utf-8"), True)).decode("ascii")
        else:
            data.pop("token", None)
        self._save(data)


def _get(path: str, token: str, timeout: float = 20):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Lumi",
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(API + path, headers=headers, method="GET")
    with urllib.request.urlopen(request, timeout=timeout) as response:   # noqa: S310 — https fisso
        return json.loads(response.read().decode("utf-8"))


def _repo(name: str, token: str, get) -> str:
    """«owner/repo» oppure il repository dell'utente con quel nome (o simile)."""
    name = name.strip().replace(" ", "-")
    if "/" in name:
        return name
    repos = get("/user/repos?per_page=100&sort=updated", token) if token else []
    low = name.casefold()
    for repo in repos:
        if repo.get("name", "").casefold() == low:
            return repo["full_name"]
    for repo in repos:
        if low in repo.get("name", "").casefold():
            return repo["full_name"]
    raise LookupError("Non trovo il repository «%s» tra i tuoi." % name)


def esegui(kind: str, repo: str | None, token: str, get=_get) -> str:
    """Testo da mostrare in chat (elenco) o messaggio d'errore comprensibile."""
    try:
        if kind == "repos":
            if not token:
                return "Per i tuoi repository serve la chiave GitHub (Impostazioni)."
            items = get("/user/repos?per_page=30&sort=updated", token)
            lines = ["%s%s" % (r["full_name"], "  (privato)" if r.get("private") else "") for r in items]
            return "Repository (%d):\n" % len(lines) + "\n".join("• " + x for x in lines)
        full = _repo(repo or "", token, get)
        if kind == "issues":
            items = [i for i in get("/repos/%s/issues?state=open&per_page=20" % full, token)
                     if "pull_request" not in i]
            if not items:
                return "Nessuna issue aperta in %s." % full
            return ("Issue aperte in %s (%d):\n" % (full, len(items))
                    + "\n".join("• #%d %s" % (i["number"], i["title"][:100]) for i in items))
        items = get("/repos/%s/commits?per_page=10" % full, token)
        return ("Ultimi commit di %s:\n" % full + "\n".join(
            "• %s %s" % (c["sha"][:7], c["commit"]["message"].splitlines()[0][:90]) for c in items))
    except LookupError as exc:
        return str(exc)
    except Exception as exc:
        code = getattr(exc, "code", None)
        return {401: "Chiave GitHub non valida.", 403: "GitHub ha rifiutato (limite o permessi).",
                404: "Repository non trovato o non accessibile."}.get(
            code, "GitHub non risponde (rete?).")


def costruisci_sezione(parent, notify, *, config: Configurazione | None = None, ask_key=None,
                       open_url=None):
    import tkinter as tk
    import webbrowser
    from tkinter import simpledialog, ttk
    config = config or Configurazione()
    ask_key = ask_key or (lambda: simpledialog.askstring(
        "Lumi // GitHub", "Token GitHub di sola lettura (resta cifrato su questo PC; vuoto = togli):",
        show="*", parent=parent))
    open_url = open_url or webbrowser.open
    box = ttk.LabelFrame(parent, text="GitHub (sola lettura, add-on spento di serie)")
    box.pack(fill="x", padx=8, pady=8)
    ttk.Label(box, wraplength=540, text=(
        "Comandi: «i miei repository», «issue aperte di …», «ultimi commit di …». Lumi legge "
        "soltanto, non scrive niente su GitHub.")).pack(anchor="w", padx=8, pady=5)
    on = tk.BooleanVar(value=config.attivo)
    ttk.Checkbutton(box, text="Attivo", variable=on,
                    command=lambda: config.imposta_attivo(on.get())).pack(anchor="w", padx=8)
    row = ttk.Frame(box)
    row.pack(fill="x", padx=8, pady=(2, 6))
    label = tk.StringVar(value="Chiave ✓" if config.token() else "Chiave…")

    def set_key():
        value = ask_key()
        if value is None:
            return
        config.salva_token(value)
        label.set("Chiave ✓" if value.strip() else "Chiave…")
        notify("GITHUB > " + ("Chiave salvata (cifrata)." if value.strip() else "Chiave tolta."))

    ttk.Button(row, textvariable=label, command=set_key).pack(side="left")
    ttk.Button(row, text="Crea un token di sola lettura",
               command=lambda: open_url("https://github.com/settings/personal-access-tokens/new")
               ).pack(side="left", padx=6)
    return box
