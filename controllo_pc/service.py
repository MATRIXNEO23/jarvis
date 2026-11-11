"""Controllo PC: finestre, clic, scrittura, scorciatoie e scorrimento, offline.

Conferme: le prime volte Lumi chiede «sì» prima di agire; dopo `confirm_times`
conferme della stessa azione sullo stesso programma la ricorda e la fa da sola.
Le azioni delicate (inviare, eliminare, non salvare, pagare…) chiedono sempre.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
import unicodedata
from pathlib import Path

from . import windows as win

CONFIRM_TIMEOUT = 60
# Mai ricordate: chiedono sempre conferma.
_DELICATE = re.compile(
    r"\b(invia|inviare|send|elimina|eliminare|cancella|delete|remove|rimuovi|non\s+salvare|"
    r"don'?t\s+save|discard|scarta|paga|pay|acquista|compra|buy|ordina|conferma\s+ordine|"
    r"formatta|disinstalla|uninstall|esci\s+senza|spegni|shutdown|riavvia|restart)\b", re.I)
_DELICATE_KEYS = ({"alt", "f4"}, {"ctrl", "w"}, {"ctrl", "enter"}, {"shift", "canc"},
                  {"shift", "delete"}, {"invio"}, {"enter"})
# Destinazioni che appartengono ad altri comandi di Lumi: mai finestre.
_RESERVED = re.compile(
    r"^(gpt|chatgpt|gemma|il\s+modello|modello|modello\s+locale|conversazione(\s+generale)?|"
    r"progetto.*|la\s+conversazione.*|musica|timer|sveglia|cartella.*|indietro.*)$", re.I)


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def data_folder() -> Path:
    try:
        from settings import default_path
        return default_path().parent / "addon-data" / "controllo_pc"
    except Exception:
        return Path.home() / ".lumi" / "addon-data" / "controllo_pc"


def helper_path() -> Path:
    return Path(__file__).resolve().parent / "uia_bin" / "LumiControl.exe"


def list_elements(hwnd: int, timeout: float = 8.0) -> list[dict]:
    """Elementi della finestra tramite LumiControl.exe (UI Automation, sola lettura)."""
    exe = helper_path()
    if not exe.is_file():
        raise FileNotFoundError(f"Manca {exe} (reinstalla il pacchetto completo).")
    flags = 0x08000000 if sys.platform == "win32" else 0      # CREATE_NO_WINDOW
    done = subprocess.run([str(exe), "list", str(int(hwnd)), "400"], capture_output=True,
                          timeout=timeout, creationflags=flags)
    data = json.loads(done.stdout.decode("utf-8", "replace").strip() or "{}")
    if not data.get("ok"):
        raise RuntimeError(str(data.get("error", "lettura non riuscita"))[:160])
    return [i for i in data.get("items", []) if isinstance(i, dict)]


class ControlService:
    def __init__(self, is_enabled=lambda: False, folder: Path | None = None,
                 backend=win, elements=list_elements, clock=time.monotonic):
        self.is_enabled = is_enabled
        self.folder = Path(folder or data_folder())
        self.backend = backend
        self.elements = elements
        self.clock = clock
        self.pending = None           # (scadenza, chiave, delicata, descrizione, esecuzione)
        self.last_list: list[dict] = []
        self.target = None            # ultima finestra usata da Lumi
        self._lock = threading.Lock()
        self.settings = self._load()

    # --- impostazioni nel profilo ------------------------------------------
    def _load(self) -> dict:
        data = {"confirm_times": 2, "visible_mouse": True, "approved": {}, "nicknames": {}}
        try:
            saved = json.loads((self.folder / "config.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            saved = {}
        if isinstance(saved, dict):
            if type(saved.get("confirm_times")) is int and 0 <= saved["confirm_times"] <= 10:
                data["confirm_times"] = saved["confirm_times"]
            if type(saved.get("visible_mouse")) is bool:
                data["visible_mouse"] = saved["visible_mouse"]
            if isinstance(saved.get("approved"), dict):
                data["approved"] = {str(k)[:200]: int(v) for k, v in list(saved["approved"].items())[:2000]
                                    if type(v) is int}
            if isinstance(saved.get("nicknames"), dict):
                for name, value in list(saved["nicknames"].items())[:200]:
                    if isinstance(value, dict) and isinstance(value.get("process"), str):
                        data["nicknames"][normalized(name)[:40]] = {
                            "label": str(value.get("label", name))[:40],
                            "process": value["process"][:120],
                            "title": str(value.get("title", ""))[:200]}
        return data

    def save(self) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        tmp = self.folder / "config.json.tmp"
        tmp.write_text(json.dumps(self.settings, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, self.folder / "config.json")

    def set_nickname(self, name: str, window: dict) -> str:
        key = normalized(name)
        if not key or len(key) > 40:
            return "Nome non valido."
        if _RESERVED.match(key):
            return f"«{name}» è già un comando di Lumi: scegli un altro nome."
        self.settings["nicknames"][key] = {"label": " ".join(name.split())[:40],
                                           "process": window.get("process", ""),
                                           "title": window.get("title", "")}
        self.save()
        return f"D'ora in poi «{name}» è {window.get('title', '')[:60]}."

    def remove_nickname(self, name: str) -> None:
        self.settings["nicknames"].pop(normalized(name), None)
        self.save()

    def forget_approvals(self) -> str:
        self.settings["approved"] = {}
        self.save()
        return "Azioni ricordate dimenticate: chiederò di nuovo conferma."

    # --- finestre -------------------------------------------------------------
    def windows(self) -> list[dict]:
        return self.backend.open_windows()

    def nickname_of(self, window: dict) -> str:
        for item in self.settings["nicknames"].values():
            if item["process"].lower() == window.get("process", "").lower() and (
                    not item["title"] or item["title"] == window.get("title")):
                return item["label"]
        for item in self.settings["nicknames"].values():
            if item["process"].lower() == window.get("process", "").lower():
                return item["label"]
        return ""

    def find_window(self, query: str | None):
        """Per numero dell'ultimo elenco, nome tuo, titolo o programma."""
        items = self.windows()
        if not query:
            return self._current(items)
        from .commands import number_of
        number = number_of(query)
        if number is not None and self.last_list:
            if 1 <= number <= len(self.last_list):
                wanted = self.last_list[number - 1]["hwnd"]
                return next((w for w in items if w["hwnd"] == wanted), None)
            return None
        key = normalized(query)
        if not key or _RESERVED.match(key):
            return None
        nick = self.settings["nicknames"].get(key)
        if nick:
            same = [w for w in items if w["process"].lower() == nick["process"].lower()]
            exact = [w for w in same if nick["title"] and w["title"] == nick["title"]]
            if exact or same:
                return (exact or same)[0]
        words = key.split()
        for field in ("title", "process"):
            for w in items:
                text = normalized(w[field].rsplit(".", 1)[0] if field == "process" else w[field])
                if all(word in text.split() or word in text for word in words):
                    return w
        return None

    def _current(self, items):
        if self.target is not None:
            match = next((w for w in items if w["hwnd"] == self.target), None)
            if match:
                return match
        return items[0] if items else None       # la più recente dopo Lumi

    # --- conferme ---------------------------------------------------------------
    def _ask(self, key: str, delicate: bool, description: str, run) -> str:
        times = self.settings["confirm_times"]
        if not delicate and self.settings["approved"].get(key, 0) >= times:
            return run()
        self.pending = (self.clock() + CONFIRM_TIMEOUT, key, delicate, description, run)
        tail = " (azione delicata: chiedo sempre)" if delicate else ""
        return f"{description}? Di' «sì» per confermare o «no».{tail}"

    def answer(self, text: str):
        """Risposta a una conferma in sospeso: messaggio, oppure None se non è una risposta."""
        if self.pending is None:
            return None
        deadline, key, delicate, _description, run = self.pending
        word = normalized(text)
        if self.clock() > deadline:
            self.pending = None
            return None
        if word in ("si", "sì", "conferma", "confermo", "ok", "va bene", "procedi", "vai", "fallo"):
            self.pending = None
            if not delicate:
                approved = self.settings["approved"]
                approved[key] = approved.get(key, 0) + 1
                try:
                    self.save()
                except OSError:
                    pass
            return run()
        if word in ("no", "annulla", "lascia stare", "non farlo", "stop"):
            self.pending = None
            return "Annullato."
        self.pending = None            # altra frase: la conferma decade
        return None

    # --- azioni -------------------------------------------------------------
    def handle(self, action: str, values: dict):
        """Messaggio, oppure None se la frase non riguarda una finestra/elemento esistente."""
        if not self.is_enabled():
            return None
        method = getattr(self, "_do_" + action, None)
        return method(**values) if method else None

    def _do_list_windows(self):
        items = self.windows()
        self.last_list = items[:20]
        if not items:
            return "Nessuna finestra aperta oltre a Lumi."
        lines = []
        for index, w in enumerate(self.last_list, start=1):
            nick = self.nickname_of(w)
            lines.append(f"{index}. {w['title'][:70]}" + (f"  [«{nick}»]" if nick else "")
                         + f"  ({w['process']})")
        return "Finestre aperte (di' «passa alla 2» o il nome):\n" + "\n".join(lines)

    def _do_switch(self, window):
        found = self.find_window(window)
        if found is None:
            return None
        self.target = found["hwnd"]
        if self.backend.focus(found["hwnd"]):
            return "Passo a " + found["title"][:60] + "."
        return "Windows non mi ha lasciato portare davanti " + found["title"][:60] + "."

    def _do_close(self, window=None):
        found = self.find_window(window)
        if found is None:
            return None
        key = "close|" + found["process"].lower()

        def run():
            ok = self.backend.close(found["hwnd"])
            if self.target == found["hwnd"]:
                self.target = None
            return ("Chiudo " + found["title"][:60] + " (se c'è da salvare lo chiede lui)."
                    if ok else "Non riesco a chiudere " + found["title"][:60] + ".")
        return self._ask(key, False, "Chiudo " + found["title"][:60], run)

    def _do_name_window(self, name, window=None):
        found = self.find_window(window)
        if found is None:
            return "Non trovo la finestra." if window else None
        return self.set_nickname(name, found)

    def _element(self, window, target, kinds=None):
        found = self.find_window(window)
        if found is None:
            return None, None, "Non trovo la finestra."
        try:
            items = self.elements(found["hwnd"])
        except FileNotFoundError as exc:
            return found, None, "Controllo PC incompleto: " + str(exc)
        except Exception as exc:
            return found, None, "Non riesco a leggere la finestra: " + str(exc)[:100]
        key = normalized(target)
        candidates = [i for i in items if i.get("enabled", True)
                      and (kinds is None or i.get("type") in kinds)]
        exact = [i for i in candidates if normalized(i.get("name", "")) == key]
        partial = [i for i in candidates if key and key in normalized(i.get("name", ""))]
        chosen = (exact or partial or [None])[0]
        if chosen is None:
            return found, None, f"In {found['title'][:40]} non trovo «{target}»."
        return found, chosen, ""

    def _do_list_elements(self, window=None):
        found = self.find_window(window)
        if found is None:
            return None
        try:
            items = self.elements(found["hwnd"])
        except Exception as exc:
            return "Non riesco a leggere la finestra: " + str(exc)[:100]
        names = []
        for item in items:
            name = item.get("name", "").strip()
            if name and name not in names:
                names.append(f"{name} ({item.get('type', '')})")
        self.target = found["hwnd"]
        return (f"In {found['title'][:50]} puoi cliccare:\n" + "\n".join(names[:60])
                if names else f"{found['title'][:50]} non dichiara pulsanti a Windows.")

    def _center(self, item):
        return item["x"] + item["w"] // 2, item["y"] + item["h"] // 2

    def _do_click(self, target, window=None, double=False):
        from .commands import number_of
        if number_of(target) is not None:
            return None                         # «seleziona il secondo»: non è un pulsante
        found, item, error = self._element(window, target)
        if found is None:
            return None
        if item is None:
            return error
        delicate = bool(_DELICATE.search(item.get("name", "")) or _DELICATE.search(target))
        key = f"click|{found['process'].lower()}|{normalized(item.get('name', ''))}"

        def run():
            self.target = found["hwnd"]
            self.backend.focus(found["hwnd"])
            x, y = self._center(item)
            self.backend.click(x, y, self.settings["visible_mouse"], double)
            return f"Clic su «{item.get('name', target)[:50]}»."
        return self._ask(key, delicate, f"Clicco «{item.get('name', target)[:50]}» in "
                                        f"{found['title'][:40]}", run)

    def _do_type_in(self, text, target, window=None):
        found, item, error = self._element(window, target, kinds=("Edit", "Document", "ComboBox"))
        if found is None:
            return None
        if item is None:
            return error
        key = f"type|{found['process'].lower()}|{normalized(item.get('name', ''))}"

        def run():
            self.target = found["hwnd"]
            self.backend.focus(found["hwnd"])
            x, y = self._center(item)
            self.backend.click(x, y, self.settings["visible_mouse"])
            time.sleep(0.1)
            self.backend.type_text(text)
            return f"Scritto in «{item.get('name', target)[:40]}»."
        return self._ask(key, False, f"Scrivo «{text[:40]}» in «{item.get('name', target)[:40]}»",
                         run)

    def _do_type(self, text):
        found = self.find_window(None)
        if found is None:
            return "Nessuna finestra dove scrivere."
        key = f"type|{found['process'].lower()}|"

        def run():
            self.target = found["hwnd"]
            self.backend.focus(found["hwnd"])
            self.backend.type_text(text)
            return "Scritto in " + found["title"][:50] + "."
        return self._ask(key, False, f"Scrivo «{text[:40]}» in {found['title'][:40]}", run)

    def _do_press(self, keys):
        found = self.find_window(None)
        if found is None:
            return "Nessuna finestra dove premere i tasti."
        combo = "+".join(keys)
        delicate = set(keys) in _DELICATE_KEYS
        key = f"press|{found['process'].lower()}|{combo}"

        def run():
            self.target = found["hwnd"]
            self.backend.focus(found["hwnd"])
            ok = self.backend.press(keys)
            return f"Premuto {combo.upper()} in {found['title'][:40]}." if ok else "Tasti non validi."
        return self._ask(key, delicate, f"Premo {combo.upper()} in {found['title'][:40]}", run)

    def _do_scroll(self, amount):
        found = self.find_window(None)
        if found is None:
            return "Nessuna finestra da scorrere."
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        rect = self.backend.window_rect(found["hwnd"])
        if rect:
            self.backend.move_mouse((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2,
                                    self.settings["visible_mouse"])
        self.backend.scroll(amount)
        return "Scorro " + ("su." if amount > 0 else "giù.")
