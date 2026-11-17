"""Servizi di ricerca online (052): «cerca online …» e «approfondisci online …».

Stesso schema dei servizi online: un file per servizio (servizi/), chiavi cifrate DPAPI
(servizi_online.Chiavi, in un file a parte), scelta e ordine nelle impostazioni. Lumi prova il
primo servizio pronto (spunta + chiave + ricerca collegata) e, se finiscono i crediti o c'è un
errore, passa al successivo. Riassunto e link vanno nella finestra dei risultati; il browser
non si apre. Le chiavi non compaiono mai nei messaggi né nel registro.
Nessun altro comando di ricerca: nuovi comandi si propongono prima all'utente.
"""
from __future__ import annotations

import importlib
import json
import os
import pkgutil
import re
import urllib.error
from pathlib import Path

from servizi_online import Chiavi, _post

from . import quota
from .base import Ricerca, Risultato


def _carica_servizi() -> tuple:
    from . import servizi as package
    found = []
    for info in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(package.__name__ + "." + info.name)
        service = getattr(module, "SERVIZIO", None)
        if isinstance(service, Ricerca):
            found.append(service)
    return tuple(sorted(found, key=lambda s: (s.ordine, s.id)))


SERVIZI = _carica_servizi()
PER_ID = {s.id: s for s in SERVIZI}

_END = r"[\s.!?]*$"
_WAKE = re.compile(r"^\s*(?:(?:ehi|hey|ok)\s+)?lumi[\s,!.:]*", re.I)
_COMANDO = re.compile(r"^(?P<verbo>cerca|approfondisci)\s+online\b[\s,:]*(?:(?:su|sul|sulla|di|per|riguardo\s+a)\s+)?"
                      r"(?P<testo>.+?)" + _END, re.I)


def parse(text: str):
    """«cerca online X» → («cerca», X); «approfondisci online X» → («approfondisci», X).
    «approfondisci X» senza «online» non è un comando di ricerca (resta a Gemma)."""
    if not isinstance(text, str) or len(text) > 300:
        return None
    match = _COMANDO.match(_WAKE.sub("", text).strip())
    if not match or not match.group("testo").strip():
        return None
    return match.group("verbo").casefold(), match.group("testo").strip()


_APPROFONDISCI = re.compile(r"^approfondisci\b(?!\s+online\b)", re.I)


def approfondisci_locale(text: str) -> bool:
    """«approfondisci X» senza «online»: risponde Gemma offline (decisione 17/11)."""
    return isinstance(text, str) and bool(_APPROFONDISCI.match(_WAKE.sub("", text).strip()))


# --- impostazioni e chiavi (stesso schema dei servizi online) ---------------------------------
def _cartella() -> Path:
    from settings import default_path
    return default_path().parent


def carica_impostazioni(path: Path | None = None) -> dict:
    data = {"ordine": [s.id for s in SERVIZI], "attivi": []}
    acceso = True                                   # interruttore «RICERCA ON/OFF» in alto
    try:
        saved = json.loads((path or _cartella() / "servizi_ricerca.json").read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            acceso = saved.get("acceso", True) is not False
            for key in data:
                if isinstance(saved.get(key), list):
                    data[key] = [str(i) for i in saved[key]]
    except (OSError, ValueError, RuntimeError):
        pass
    order = [i for i in data["ordine"] if i in PER_ID]
    order += [s.id for s in SERVIZI if s.id not in order]
    data["ordine"] = order
    data["attivi"] = [i for i in data["attivi"] if i in PER_ID]
    data["acceso"] = acceso
    return data


def ricerca_accesa(path: Path | None = None) -> bool:
    return bool(carica_impostazioni(path).get("acceso", True))


def imposta_accesa(value: bool, path: Path | None = None) -> bool:
    """Salva l'interruttore nelle impostazioni dei servizi di ricerca; ritorna il nuovo valore."""
    data = carica_impostazioni(path)
    data["acceso"] = bool(value)
    salva_impostazioni(data, path)
    return data["acceso"]


def salva_impostazioni(data: dict, path: Path | None = None) -> None:
    path = path or _cartella() / "servizi_ricerca.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(temp, path)


def chiavi(path: Path | None = None) -> Chiavi:
    """Chiavi cifrate DPAPI, in un file separato da quello dei servizi online."""
    return Chiavi(path=path or _cartella() / "servizi_ricerca.keys", ids=PER_ID)


def pronti(settings: dict | None = None, keys: Chiavi | None = None) -> list:
    """Servizi spuntati, con chiave e ricerca collegata, nell'ordine scelto."""
    settings = settings or carica_impostazioni()
    keys = keys or chiavi()
    return [PER_ID[i] for i in settings["ordine"]
            if i in settings["attivi"] and PER_ID[i].adattatore is not None and keys.presente(i)
            and keys.leggi(i).strip()]


# --- ricerca ------------------------------------------------------------------------------
def _motivo(exc: Exception) -> str:
    """Motivo breve, senza mai includere la chiave."""
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code in (402, 429, 432, 433):
            return "crediti finiti o troppe richieste"
        if exc.code in (401, 403):
            return "chiave rifiutata"
        return "errore %d" % exc.code
    return "non raggiungibile" if isinstance(exc, (urllib.error.URLError, OSError)) else "errore"


def cerca(query: str, approfondisci: bool = False, *, settings=None, keys=None, post=_post,
          timeout: float = 25, counter: bool = True):
    """(nome servizio, Risultato) dal primo servizio che risponde; (None, [motivi]) se nessuno."""
    keys = keys or chiavi()
    reasons = []
    for service in pronti(settings, keys):
        try:
            result = service.adattatore(keys.leggi(service.id), query, approfondisci, timeout, post)
        except Exception as exc:                         # crediti, rete, chiave: passa al successivo
            reasons.append("%s: %s" % (service.nome, _motivo(exc)))
            continue
        if isinstance(result, Risultato) and (result.riassunto or result.link):
            if counter:
                try:
                    from . import quota
                    quota.registra(service.id)
                except Exception:                      # il contatore non deve mai bloccare la ricerca
                    pass
            return service.nome, result
        reasons.append("%s: nessun risultato" % service.nome)
    return None, reasons


def avviso_senza_chiave(settings: dict | None = None) -> str:
    """Messaggio chiaro quando nessun servizio di ricerca è pronto, col link per la chiave."""
    link = next((s.chiavi for s in SERVIZI if s.adattatore is not None and s.chiavi), "")
    nome = next((s.nome for s in SERVIZI if s.adattatore is not None), "Tavily")
    return ("Per cercare online manca la chiave di %s. Creala qui: %s e incollala in "
            "Impostazioni, Servizi di ricerca." % (nome, link))


def frase_breve(result: Risultato, limit: int = 280) -> str:
    """Poche parole da dire a voce (il resto resta in chat e nella finestra)."""
    text = " ".join(result.riassunto.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    return (cut[:end + 1] if end > 80 else cut.rsplit(" ", 1)[0] + "…")


def dominio(url: str) -> str:
    """Dominio reale della destinazione (FIX 7): si vede accanto al titolo prima del clic."""
    from urllib.parse import urlparse
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        host = ""
    return host[4:] if host.startswith("www.") else host


def testo_chat(nome: str, result: Risultato) -> str:
    """Messaggio di Lumi in chat: riassunto, poi le fonti come link markdown («[titolo](url)»)
    con una breve anteprima sotto; chat_link li rende cliccabili."""
    lines = ["Ricerca online (%s): %s" % (nome, " ".join(result.riassunto.split()) or "nessun riassunto.")]
    if result.link:
        lines += ["", "Fonti:"]
    for n, (title, url) in enumerate(result.link, 1):
        safe = title.replace("[", "(").replace("]", ")").replace("\n", " ")
        lines.append("%d. [%s](%s)  (%s)" % (n, safe, url, dominio(url) or "dominio ignoto"))
        preview = result.anteprime[n - 1] if n <= len(result.anteprime) else ""
        if preview:
            lines.append("    " + preview)
    return "\n".join(lines)


def elenco_finestra(nome: str, result: Risultato) -> dict:
    """Voci per la finestra dei risultati (stesso formato dell'elenco file): Tipo, Nome, Percorso."""
    summary = " ".join(result.riassunto.split())
    return {"token": "ricerca-" + nome.casefold() + "-" + str(abs(hash(summary)) % 10**8),
            "items": [("Link", title, url) for title, url in result.link],
            "summary": ("%s: %s" % (nome, summary))[:900]}


# --- interfaccia (Impostazioni → Modelli → «Servizi di ricerca») ----------------------------
def costruisci_sezione(parent, notify, *, ask_key=None, open_url=None, keys: Chiavi | None = None,
                       post=_post, run_async=None):
    import threading
    import tkinter as tk
    import webbrowser
    from tkinter import simpledialog, ttk
    keys = keys or chiavi()
    ask_key = ask_key or (lambda name: simpledialog.askstring(
        "Lumi // Chiave API", "Chiave di " + name + " (resta cifrata su questo PC; vuota = togli):",
        show="*", parent=parent))
    open_url = open_url or webbrowser.open
    run_async = run_async or (lambda fn: threading.Thread(target=fn, daemon=True,
                                                          name="lumi-prova-ricerca").start())
    settings = carica_impostazioni()
    box = ttk.LabelFrame(parent, text="Servizi di ricerca")
    box.pack(fill="x", padx=8, pady=8)
    ttk.Label(box, wraplength=540, text=(
        "Spunta i servizi da usare e metti la loro chiave: «cerca online …» e «approfondisci "
        "online …» provano il primo pronto e passano al successivo se i crediti finiscono o c'è "
        "un errore. Riassunto e link compaiono nella finestra dei risultati; il browser non si apre."
    )).pack(anchor="w", padx=8, pady=5)
    rows = ttk.Frame(box)
    rows.pack(fill="x", padx=8, pady=(0, 6))
    state = {"vars": {}}

    def save(*_):
        settings["attivi"] = [i for i in settings["ordine"] if state["vars"][i].get()]
        try:
            salva_impostazioni(settings)
        except (OSError, RuntimeError) as exc:
            notify("RICERCA / ERRORE > Scelta non salvata: " + str(exc)[:120])

    def set_key(service):
        value = ask_key(service.nome)
        if value is None:
            return
        try:
            keys.salva(service.id, value)
        except Exception as exc:
            notify("RICERCA / ERRORE > Chiave non salvata: " + str(exc)[:120])
            return
        notify("RICERCA > Chiave di " + service.nome + (" salvata (cifrata)." if value.strip() else " tolta."))
        draw()

    def test(service):
        def work():
            try:
                result = service.adattatore(keys.leggi(service.id), "ciao", False, 30, post)
                ok = bool(result.riassunto or result.link)
                notify("RICERCA > Prova " + service.nome + ": " + ("funziona." if ok else "nessun risultato."))
            except Exception as exc:
                notify("RICERCA > Prova " + service.nome + ": " + _motivo(exc) + ".")
        save()
        run_async(work)

    def move(service_id, delta):
        order = settings["ordine"]
        i = order.index(service_id)
        j = max(0, min(len(order) - 1, i + delta))
        order[i], order[j] = order[j], order[i]
        save()
        draw()

    def draw():
        for child in rows.winfo_children():
            child.destroy()
        for service_id in settings["ordine"]:
            service = PER_ID[service_id]
            line = ttk.Frame(rows)
            line.pack(fill="x", pady=1)
            var = state["vars"].setdefault(service_id, tk.BooleanVar(value=service_id in settings["attivi"]))
            ttk.Checkbutton(line, variable=var, command=save, width=2).pack(side="left")
            ttk.Label(line, width=14, text=service.nome).pack(side="left")
            ttk.Button(line, text="Chiave ✓" if keys.presente(service_id) else "Chiave…", width=9,
                       command=lambda s=service: set_key(s)).pack(side="left", padx=2)
            if service.adattatore is not None:
                ttk.Button(line, text="Prova", width=6, command=lambda s=service: test(s)).pack(side="left")
            ttk.Button(line, text="↑", width=2, command=lambda i=service_id: move(i, -1)).pack(side="left")
            ttk.Button(line, text="↓", width=2, command=lambda i=service_id: move(i, 1)).pack(side="left")
            ttk.Button(line, text="Prendi la chiave", command=lambda u=service.chiavi: open_url(u)
                       ).pack(side="left", padx=2)
            note = service.limite + ("" if service.adattatore is not None
                                     else " Ricerca non ancora collegata: per ora Lumi la salta.")
            if keys.presente(service_id):
                from . import quota
                info = quota.stato(service_id, service.limite_mese)
                bar = tk.Canvas(rows, width=110, height=8, bg="#10293a", highlightthickness=0)
                bar.pack(anchor="w", padx=(28, 0))
                left = 1.0 if info["usato"] is None else 1 - info["usato"]
                bar.create_rectangle(0, 0, int(110 * left), 8, fill=info["colore"], width=0)
                ttk.Label(rows, text=info["testo"], foreground="#888").pack(anchor="w", padx=(28, 0))
            ttk.Label(rows, text=note, foreground="#888", wraplength=480, justify="left"
                      ).pack(anchor="w", padx=(28, 0), pady=(0, 3))

    draw()
    box.redraw = draw
    return box
