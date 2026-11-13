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

from controllo_comune import windows as win
from controllo_comune.uia import (focused_element, helper_path, list_elements, ocr_elements,
                                  play_shapes)
from frasi_lumi import say

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


def _overlap(a, b) -> bool:
    return not (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"]
                or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])


# Tasto per lo schermo intero in base al programma (minuscolo, senza .exe).
VIDEO_APPS = ("netflix", "youtube", "disney", "primevideo", "vlc")
FULLSCREEN_KEYS = {"netflix": (["f"], ["esc"]), "vlc": (["f"], ["esc"]),
                   "wmplayer": (["alt", "invio"], ["esc"]), "mpc-hc64": (["alt", "invio"], ["esc"]),
                   "mpc-hc": (["alt", "invio"], ["esc"]), "potplayermini64": (["invio"], ["esc"])}
BROWSERS = {"chrome", "msedge", "firefox", "brave", "opera", "vivaldi"}
# Programmi a griglia (copertine): elemento = destra/sinistra, riga = giù/su.
GRID_APPS = {"netflix", "disney", "primevideo", "spotify"}


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
        self.selected = None          # (hwnd, elemento) scelto per ultimo
        self.numbered = None          # (hwnd, elementi numerati, momento)
        self.last_used = -1e9         # ultimo comando del Controllo PC (per le parole corte)
        self.help_page = 0
        self.show_overlay = lambda items: None     # numeri sullo schermo (impostato da Lumi)
        self.focused = focused_element
        self.ocr = ocr_elements           # scritte sullo schermo (OCR di Windows)
        self.play_shapes = play_shapes    # pulsanti play disegnati
        self.grid = None                  # (x, y, w, h, storico) mentre la griglia è attiva
        self.last_nudge = None
        self.show_grid = lambda rect: None
        self.show_strip = lambda text: None
        self.pointer_mode = False
        try:
            from controllo_comune import gate
            gate.register("controllo_pc", self.is_enabled)
        except ImportError:
            pass

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

    def find_window(self, query: str | None, allow_lumi=False):
        """Per numero dell'ultimo elenco, nome tuo, titolo o programma."""
        items = self.windows()
        if not query:
            return self._current(items, allow_lumi)
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

    def _current(self, items, allow_lumi=False):
        """La finestra in primo piano ADESSO (richiesta utente: non l'ultima usata da
        Lumi). Se davanti c'è Lumi stessa (es. comando scritto nella sua casella), le
        azioni vanno alla finestra subito sotto, salvo chiudi/minimizza (con conferma)."""
        try:
            front = int(self.backend.foreground())
        except Exception:
            front = 0
        match = next((w for w in items if w["hwnd"] == front), None)
        if match is not None and (allow_lumi or not match.get("lumi")):
            return match
        others = [w for w in items if not w.get("lumi")]
        if match is not None and match.get("lumi"):
            return others[0] if others else None
        return others[0] if others else (items[0] if allow_lumi and items else None)

    # --- conferme ---------------------------------------------------------------
    def _ask(self, key: str, delicate: bool, description: str, run) -> str:
        times = self.settings["confirm_times"]
        if not delicate and self.settings["approved"].get(key, 0) >= times:
            return run()
        self.pending = (self.clock() + CONFIRM_TIMEOUT, key, delicate, description, run)
        import risposte
        risposte.expect_answer(speech_text=description)
        tail = " (azione delicata: chiedo sempre)" if delicate else ""
        return say("conferma", testo=description) + " Di' «sì» o «no»." + tail

    def answer(self, text: str):
        """Risposta a una conferma in sospeso: messaggio, oppure None se non è una risposta."""
        if self.pending is None:
            return None
        deadline, key, delicate, _description, run = self.pending
        word = normalized(text)
        if self.clock() > deadline:
            self.pending = None
            return None
        import risposte
        if risposte.is_yes(text) or word in ("conferma", "confermo", "procedi", "fallo"):
            self.pending = None
            if not delicate:
                approved = self.settings["approved"]
                approved[key] = approved.get(key, 0) + 1
                try:
                    self.save()
                except OSError:
                    pass
            return run()
        if risposte.is_no(text) or word in ("non farlo",):
            self.pending = None
            return say("annullato")
        self.pending = None            # altra frase: la conferma decade
        return None

    # --- azioni -------------------------------------------------------------
    def handle(self, action: str, values: dict):
        """Messaggio, oppure None se la frase non riguarda una finestra/elemento esistente."""
        if not self.is_enabled():
            return None
        action, values = self._redirect(action, values)
        method = getattr(self, "_do_" + action, None)
        if method is None:
            return None
        reply = method(**values)
        if action in ("nudge", "grid_start", "grid_pick", "grid_back"):
            self.pointer_mode = True
        elif action not in ("click_here",):
            self.pointer_mode = False
        if reply is not None:
            self.last_used = self.clock()
        return reply

    # Parole corte («giù», «indietro», «apri», «il 3»…) valgono come comando solo
    # se il Controllo PC è stato usato da poco: altrimenti vanno agli altri comandi
    # e al modello, così non si interrompe il parlare normale.
    CONTEXT_SECONDS = 120
    SHORT_ACTIONS = ("step", "nav", "open_bare", "open_selected", "click_selected", "more_help",
                     "media_pause")

    # Azioni che, se riconosciute, vanno al Controllo PC prima della musica.
    # «play» e «schermo intero» restano prima alla musica (riprendi / video di Lumi),
    # tranne «play» mentre stai usando il Controllo PC.
    FIRST_ACTIONS = ("pick", "row_scroll", "grid_start", "grid_close", "nudge",
                     "click_here", "task_manager", "force_close")

    def _redirect(self, action, values):
        """Con la griglia aperta i numeri scelgono la casella, «indietro» torna alla
        griglia più grande, «clicca» clicca al centro; dopo «mouse a destra» «clicca»
        clicca dove si trova il puntatore."""
        if self.grid_active():
            if action == "pick" and values.get("bare") and 1 <= (values.get("position") or 0) <= 9:
                return "grid_pick", {"number": values["position"]}
            if action == "nav" and values.get("dir", "").endswith("indietro"):
                return "grid_back", {}
        if self.grid_active() or self.pointer_mode:
            if action == "click_selected":
                return "click_here", {}
            if action == "open_selected":
                return "click_here", {"double": True}
        return action, values

    def recent(self) -> bool:
        return self.clock() - self.last_used <= self.CONTEXT_SECONDS

    def claims(self, action: str, values: dict) -> bool:
        if action == "nudge" and values.get("dir") == "ancora":
            return self.last_nudge is not None and self.recent()
        if action == "fullscreen" and values.get("bare"):
            return self.is_fullscreen_front()
        if action in self.SHORT_ACTIONS or (action == "pick" and values.get("bare")):
            return self.recent()
        return True

    def _do_list_windows(self):
        items = self.windows()
        self.last_list = items[:20]
        if not items:
            return "Nessuna finestra aperta oltre a Lumi."
        lines = []
        for index, w in enumerate(self.last_list, start=1):
            nick = self.nickname_of(w)
            lines.append(f"{index}. {w['title'][:70]}" + (f"  [«{nick}»]" if nick else "")
                         + ("  (Lumi)" if w.get("lumi") else f"  ({w['process']})"))
        return "Finestre aperte (di' «passa alla 2» o il nome):\n" + "\n".join(lines)

    def _do_switch(self, window):
        # «vai al 5» subito dopo «mostra i numeri» sceglie l'elemento 5;
        # altrimenti «passa/vai alla 2» resta la finestra 2 dell'elenco finestre.
        from .commands import number_of
        number = number_of(window)
        if (number is not None and self.numbered is not None
                and self.clock() - self.numbered[2] <= self.CONTEXT_SECONDS):
            return self._do_pick(number, "", "select")
        # In Esplora file «vai su Download / Disco C» apre la voce nella finestra.
        current = self._current(self.windows()) if self.recent() else None
        if (current is not None and current["process"].lower() == "explorer.exe"
                and normalized(window) and not _RESERVED.match(normalized(window))):
            found, item, _error = self._element(None, window,
                                                kinds=("TreeItem", "ListItem", "Hyperlink",
                                                       "Button", "DataItem"))
            if item is not None:
                self._point(found, item, "click")
                self.selected = (found["hwnd"], item)
                return say("passo", finestra=item.get("name", window)[:60])
        found = self.find_window(window)
        if found is None:
            return None
        self.target = found["hwnd"]
        if self.backend.focus(found["hwnd"]):
            return say("passo", finestra=found["title"][:60])
        return "Windows non mi ha lasciato portare davanti " + found["title"][:60] + "."

    def _do_close(self, window=None):
        found = self.find_window(window, allow_lumi=True)
        if found is None:
            return None
        key = "close|" + found["process"].lower()
        if found.get("lumi"):
            return self._ask("", True, "Chiudo Lumi stessa",
                             lambda: (self.backend.close(found["hwnd"]), say("chiudo", finestra="Lumi"))[1])

        def run():
            ok = self.backend.close(found["hwnd"])
            if self.target == found["hwnd"]:
                self.target = None
            return (say("chiudo", finestra=found["title"][:60]) +
                    " Se c'è da salvare, lo chiede il programma."
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
        texts = []
        candidates = [i for i in items if i.get("enabled", True)
                      and (kinds is None or i.get("type") in kinds)]
        exact = [i for i in candidates if normalized(i.get("name", "")) == key]
        partial = [i for i in candidates if key and key in normalized(i.get("name", ""))]
        chosen = (exact or partial or [None])[0]
        if chosen is None and kinds is None:
            # Il programma non dichiara quell'elemento: provo a leggere le scritte (OCR).
            try:
                texts = self.ocr(found["hwnd"])
            except Exception:
                texts = []
            exact = [i for i in texts if normalized(i.get("name", "")) == key]
            partial = [i for i in texts if key and key in normalized(i.get("name", ""))]
            chosen = (exact or partial or [None])[0]
        if chosen is None and kinds is None:
            # Titoli storpiati dal microfono («dip impact» → «Deep Impact»): somiglianza
            # di scrittura e suono, offline. Se due nomi si somigliano troppo non indovino.
            pool = candidates + texts
            ranked = sorted(((_sounds_like(key, normalized(i.get("name", ""))), n, i)
                             for n, i in enumerate(pool) if i.get("name")), reverse=True)
            if ranked and ranked[0][0] >= 0.72 and (len(ranked) == 1 or ranked[0][0] - ranked[1][0] >= 0.08
                                                   or normalized(ranked[0][2]["name"]) == normalized(ranked[1][2]["name"])):
                chosen = ranked[0][2]
            elif ranked and ranked[0][0] >= 0.72:
                names = " o ".join("«" + r[2]["name"][:30] + "»" for r in ranked[:2])
                return found, None, f"Intendi {names}? Dillo con «clicca» e il nome, o usa i numeri."
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
        # Ricordata per programma (non per singolo pulsante): dopo le prime conferme
        # i clic in quel programma non chiedono più (le azioni delicate sì).
        key = f"click|{found['process'].lower()}"

        def run():
            self.target = found["hwnd"]
            self.backend.focus(found["hwnd"])
            x, y = self._center(item)
            self.backend.click(x, y, self.settings["visible_mouse"], double)
            self.selected = (found["hwnd"], item)
            return say("doppio" if double else "clic", nome=item.get("name", target)[:50])
        return self._ask(key, delicate, f"Clicco «{item.get('name', target)[:50]}» in "
                                        f"{found['title'][:40]}", run)

    def _do_type_in(self, text, target, window=None, append=False):
        found, item, error = self._element(window, target, kinds=("Edit", "Document", "ComboBox"))
        if found is None:
            return None
        if item is None:
            return error
        key = f"type|{found['process'].lower()}"

        def run():
            self.target = found["hwnd"]
            self.backend.focus(found["hwnd"])
            x, y = self._center(item)
            self.backend.click(x, y, self.settings["visible_mouse"])
            time.sleep(0.1)
            if append:
                self.backend.press(["fine"])          # in fondo al testo che c'è
            else:
                self.backend.press(["ctrl", "a"])     # sostituisce il testo che c'è
            self.backend.type_text(text)
            self.selected = (found["hwnd"], item)
            return say("aggiunto" if append else "scritto", nome=item.get("name", target)[:40])
        verb = "Aggiungo" if append else "Scrivo"
        return self._ask(key, False, f"{verb} «{text[:40]}» in «{item.get('name', target)[:40]}»",
                         run)

    def _do_clear_field(self, target):
        found = self.find_window(None)
        if found is None:
            return None
        try:
            items = self.elements(found["hwnd"])
        except Exception as exc:
            return "Non riesco a leggere la finestra: " + str(exc)[:100]
        # Prima la X «Cancella/Annulla ricerca» se c'è, poi il campo svuotato a mano.
        clear = [i for i in items if i.get("type") == "Button" and re.search(
            r"cancella|annulla ricerca|clear|cancel", i.get("name", ""), re.I)]
        key = normalized(target)
        fields = [i for i in items if i.get("type") in ("Edit", "ComboBox")
                  and key in normalized(i.get("name", ""))]
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        if clear:
            self._point(found, clear[0], "click")
            return say("pulito")
        if not fields:
            return f"In {found['title'][:40]} non trovo il campo «{target}»."
        self._point(found, fields[0], "click")
        self.backend.press(["ctrl", "a"])
        self.backend.press(["canc"])
        return say("pulito")

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
            return say("tasti", tasti=combo.upper()) if ok else "Tasti non validi."
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
        return say("scorro_su" if amount > 0 else "scorro_giu")

    # --- puntatore visibile sull'elemento ------------------------------------------
    def _point(self, found, item, how="move"):
        """Porta davanti la finestra, sposta il puntatore (visibile) sull'elemento e,
        se richiesto, fa clic o doppio clic."""
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        x, y = self._center(item)
        if how == "move":
            self.backend.move_mouse(x, y, True)
        else:
            self.backend.click(x, y, True, how == "double")

    # --- numeri sullo schermo e scelta per numero o posizione -------------------------
    CLICKABLE = ("Button", "ListItem", "TreeItem", "TabItem", "MenuItem", "Hyperlink", "Edit",
                 "CheckBox", "RadioButton", "DataItem", "ComboBox", "SplitButton")
    MAX_NUMBERS = 80

    def _do_show_numbers(self):
        found = self.find_window(None)
        if found is None:
            return None
        try:
            items = self.elements(found["hwnd"])
        except Exception as exc:
            return "Non riesco a leggere la finestra: " + str(exc)[:100]
        shown = [i for i in items if i.get("type") in self.CLICKABLE][:self.MAX_NUMBERS]
        if len(shown) < 8:
            # Pochi elementi dichiarati (es. Netflix): aggiungo le scritte lette con l'OCR.
            try:
                texts = self.ocr(found["hwnd"])
            except Exception:
                texts = []
            for text in texts:
                if len(shown) >= self.MAX_NUMBERS:
                    break
                if not any(_overlap(text, other) for other in shown):
                    shown.append(text)
        if not shown:
            return f"{found['title'][:50]} non dichiara elementi a Windows: prova «scorri» o i tasti."
        self.target = found["hwnd"]
        self.numbered = (found["hwnd"], shown, self.clock())
        self.show_overlay(shown)
        lines = [f"{n}. {i.get('name') or '(senza nome)'} ({i.get('type')})"
                 for n, i in enumerate(shown, start=1)]
        return say("numeri") + "\n" + "\n".join(lines)

    def _do_hide_numbers(self):
        self.numbered = None
        self.show_overlay(None)
        return "Numeri tolti."

    _KIND_EXT = {
        "immagine": (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic", ".tif", ".tiff"),
        "foto": (".jpg", ".jpeg", ".png", ".heic", ".webp"),
        "video": (".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".m4v"),
        "documento": (".pdf", ".doc", ".docx", ".txt", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"),
    }

    def _content(self, items, kind):
        """Elementi «del contenuto» (i file di una cartella, le righe di un elenco)."""
        rows = [i for i in items if i.get("type") in ("ListItem", "DataItem")]
        if not rows:
            rows = [i for i in items if i.get("type") in ("TreeItem", "ListItem", "Button",
                                                          "Hyperlink", "MenuItem", "TabItem")]
        name = lambda i: i.get("name", "").lower()
        if kind in self._KIND_EXT:
            rows = [i for i in rows if name(i).endswith(self._KIND_EXT[kind])]
        elif kind == "cartella":
            rows = [i for i in rows if "." not in name(i)[-6:]]
        elif kind == "file":
            rows = [i for i in rows if "." in name(i)[-6:]]
        return rows

    def _do_pick(self, position, kind="", how="select", bare=False):
        if position is None:
            return None
        recent_numbers = (self.numbered is not None
                          and self.clock() - self.numbered[2] <= self.CONTEXT_SECONDS)
        if recent_numbers and not kind and position > 0:
            hwnd, shown, _when = self.numbered
            found = next((w for w in self.windows() if w["hwnd"] == hwnd), None)
            if found is None:
                return "La finestra con i numeri non c'è più."
            if position > len(shown):
                return f"Ci sono solo {len(shown)} numeri."
            item = shown[position - 1]
        else:
            if bare:
                return None
            found = self.find_window(None)
            if found is None:
                return None
            try:
                items = self.elements(found["hwnd"])
            except Exception as exc:
                return "Non riesco a leggere la finestra: " + str(exc)[:100]
            rows = self._content(items, kind)
            if not rows:
                return "Non trovo " + (kind or "elementi") + " in " + found["title"][:40] + "."
            index = position - 1 if position > 0 else len(rows) + position
            if not 0 <= index < len(rows):
                return f"Ce ne sono solo {len(rows)}."
            item = rows[index]
        name = item.get("name") or "(senza nome)"
        delicate = how != "select" and bool(_DELICATE.search(name))

        def run():
            self._point(found, item, {"select": "click", "click": "click", "double": "double"}[how])
            self.selected = (found["hwnd"], item)
            self.show_overlay(None)
            return say({"select": "selezionato", "click": "clic", "double": "doppio"}[how], nome=name[:60])
        if delicate:
            return self._ask("pick|" + normalized(name), True, f"Clicco «{name[:50]}»", run)
        return run()

    # --- elemento selezionato --------------------------------------------------------
    def _selected_item(self):
        if self.selected is None:
            return None, None
        hwnd, item = self.selected
        found = next((w for w in self.windows() if w["hwnd"] == hwnd), None)
        if found is None:
            self.selected = None
            return None, None
        try:                              # posizione aggiornata (la finestra può essere scorsa)
            fresh = [i for i in self.elements(hwnd) if i.get("name") == item.get("name")
                     and i.get("type") == item.get("type")]
            if fresh:
                item = fresh[0]
        except Exception:
            pass
        return found, item

    def _do_open_selected(self):
        found, item = self._selected_item()
        if found is None:
            return "Prima scegli un elemento (es. «seleziona il primo» o «mostra i numeri»)."
        self._point(found, item, "double")
        return say("doppio", nome=(item.get("name") or "elemento")[:60])

    def _do_click_selected(self):
        found, item = self._selected_item()
        if found is None:
            return "Prima scegli un elemento (es. «seleziona il primo» o «mostra i numeri»)."
        self._point(found, item, "click")
        return say("clic", nome=(item.get("name") or "elemento")[:60])

    def _do_open_bare(self):
        """«Apri» da solo: con un elemento selezionato chiede prima (poteva mancare il
        nome di un programma)."""
        found, item = self._selected_item()
        if found is None:
            return None
        name = (item.get("name") or "elemento")[:60]
        self.pending = (self.clock() + CONFIRM_TIMEOUT, "", True, "",
                        lambda: (self._point(found, item, "double"), say("doppio", nome=name))[1])
        import risposte
        risposte.expect_answer(speech_text=name)
        return say("apri_selezionato", nome=name)

    # --- passo passo con le frecce -------------------------------------------------------
    _STEP_KEYS = {"giù": "giu", "giu": "giu", "sotto": "giu", "prossimo": "giu", "successivo": "giu",
                  "su": "su", "sopra": "su", "precedente": "su", "destra": "destra",
                  "sinistra": "sinistra"}

    def _step_key(self, dir, process):
        """«file successivo» va a destra nei programmi a griglia (copertine), giù negli
        elenchi; «riga successiva» va sempre giù."""
        grid = process in GRID_APPS
        if dir in ("file successivo", "elemento successivo", "prossimo", "successivo"):
            return "destra" if grid else "giu"
        if dir in ("file precedente", "elemento precedente", "precedente"):
            return "sinistra" if grid else "su"
        if dir in ("riga successiva", "riga sotto"):
            return "giu"
        if dir in ("riga precedente", "riga sopra"):
            return "su"
        return self._STEP_KEYS.get(dir, "giu")

    def _do_step(self, dir):
        found = self.find_window(None)
        if found is None:
            return None
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        self.backend.press([self._step_key(dir, self._app_name(found))])
        time.sleep(0.15)
        try:
            item = self.focused()
        except Exception:
            item = None
        if not item:
            return "Spostato, ma Windows non mi dice su cosa sei."
        self.backend.move_mouse(*self._center(item), True)
        self.selected = (found["hwnd"], item)
        return say("selezionato", nome=(item.get("name") or "(senza nome)")[:60])

    # --- navigazione: indietro, avanti, su di un livello, barra degli indirizzi ----------
    _NAV = {"indietro": (r"^(indietro|back)", ["alt", "sinistra"], "indietro"),
            "torna indietro": (r"^(indietro|back)", ["alt", "sinistra"], "indietro"),
            "avanti": (r"^(avanti|forward)", ["alt", "destra"], "avanti"),
            "vai avanti": (r"^(avanti|forward)", ["alt", "destra"], "avanti")}

    def _do_nav(self, dir):
        found = self.find_window(None)
        if found is None:
            return None
        pattern, keys, phrase = self._NAV.get(
            dir, (r"^(su\b|up\b|livello superiore|cartella superiore|su a)", ["alt", "su"], "su_livello"))
        try:
            items = self.elements(found["hwnd"])
        except Exception:
            items = []
        button = next((i for i in items if i.get("type") in ("Button", "SplitButton")
                       and i.get("enabled", True) and re.search(pattern, i.get("name", ""), re.I)), None)
        if button is not None:
            self._point(found, button, "click")          # il puntatore va sulla freccia
        else:
            self.target = found["hwnd"]
            self.backend.focus(found["hwnd"])
            self.backend.press(keys)
        return say(phrase)

    def _do_address(self):
        found = self.find_window(None)
        if found is None:
            return None
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        try:
            items = self.elements(found["hwnd"])
        except Exception:
            items = []
        bar = next((i for i in items if i.get("type") in ("Edit", "ComboBox", "ToolBar")
                    and re.search(r"indirizz|address", i.get("name", ""), re.I)), None)
        if bar is not None:
            self.backend.move_mouse(*self._center(bar), True)
        self.backend.press(["alt", "d"])                  # campo indirizzo pronto per scrivere
        return say("indirizzi")

    # --- finestre: minimizza, ingrandisci, ripristina -----------------------------------
    def _do_window_state(self, how, window=None):
        found = self.find_window(window, allow_lumi=True)
        if found is None:
            return None
        if found.get("lumi") and how != "ripristina":
            def on_lumi():
                # Lumi si riduce da sola (come «Lumi, minimizzati»): ShowWindow su una sua
                # finestra senza cornice la nascondeva senza icona e sembrava chiusa.
                if how == "minimizza" and _lumi_action("minimize"):
                    return ""
                self.backend.show_window(found["hwnd"], how)
                return say(how, finestra="Lumi")
            return self._ask("", True, ("Riduco a icona" if how == "minimizza" else "Ingrandisco")
                             + " Lumi stessa", on_lumi)
        self.backend.show_window(found["hwnd"], how)
        if how != "minimizza":
            self.target = found["hwnd"]
        return say(how, finestra=found["title"][:60])

    # --- aiuto in base alla finestra --------------------------------------------------------
    _HELP = {
        "explorer.exe": ["«vai su Download»", "«mostra i numeri» e poi «il 3»", "«apri il primo»",
                         "«giù» e «su» per scorrere i file uno alla volta", "«aprilo»", "«indietro»",
                         "«su di un livello»", "«scrivi gatti nel campo cerca»", "«pulisci la ricerca»",
                         "«vai alla barra degli indirizzi»", "«l'ultima cartella»", "«minimizza»"],
        "notepad.exe": ["«digita buongiorno»", "«premi invio»", "«premi Ctrl più S» per salvare",
                        "«scorri giù»", "«ingrandisci»", "«chiudi la finestra»"],
        "": ["«mostra i numeri» e poi «clicca il» e il numero", "«clicca su» e il nome del pulsante",
             "«scrivi … nel campo …»", "«scorri giù»", "«premi Invio»", "«finestre aperte»",
             "«passa a» e il nome", "«minimizza» o «ingrandisci»", "«chiudi la finestra»"],
    }

    def _do_context_help(self):
        found = self.find_window(None)
        process = found["process"].lower() if found else ""
        self.help_page = 0
        self._help_items = self._HELP.get(process, self._HELP[""])
        return self._help_text(found)

    def _do_more_help(self):
        if not getattr(self, "_help_items", None):
            return None
        self.help_page += 1
        return self._help_text(None)

    def _help_text(self, found):
        items = self._help_items
        start = (self.help_page * 4) % max(len(items), 1)
        chunk = items[start:start + 4]
        where = f"In {found['title'][:40]}" if found else "Qui"
        return f"{where} puoi dire: " + ", ".join(chunk) + ". Di' «altri» per altri comandi."

    # --- «riproduci» / «play» ------------------------------------------------------
    def _do_play(self):
        """Prima la scritta «Riproduci/Play» (elementi o OCR), poi il pulsante tondo con
        il triangolo, infine Invio sull'elemento selezionato."""
        found = self.find_window(None)
        if found is None:
            return None
        candidates = []
        try:
            candidates = [i for i in self.elements(found["hwnd"])
                          if re.match(r"^(riproduci|play|riprendi|guarda)\b", i.get("name", ""), re.I)]
        except Exception:
            pass
        if not candidates:
            try:
                candidates = [i for i in self.ocr(found["hwnd"])
                              if re.match(r"^(riproduci|play|riprendi|guarda)\b", i.get("name", ""), re.I)]
            except Exception:
                candidates = []
        if not candidates:
            try:
                candidates = self.play_shapes(found["hwnd"])
            except Exception:
                candidates = []
        if candidates:
            self._point(found, candidates[0], "click")
            return say("clic", nome=candidates[0].get("name") or "play")
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        if self._app_name(found) in VIDEO_APPS:
            self.backend.press(["spazio"])        # video in pausa: lo spazio riprende
            return "Play."
        self.backend.press(["invio"])
        return "Non vedo il pulsante play: ho premuto Invio sull'elemento selezionato."

    # --- comandi comuni dei video: pausa e home -------------------------------------------
    def _do_media_pause(self):
        found = self.find_window(None)
        if found is None or self._app_name(found) not in VIDEO_APPS:
            return None
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        self.backend.press(["spazio"])
        return "Pausa."

    def _do_home(self):
        found = self.find_window(None)
        if found is None:
            return None
        for source in (self.elements, self.ocr):
            try:
                items = [i for i in source(found["hwnd"])
                         if normalized(i.get("name", "")) in ("home", "pagina iniziale", "inizio")]
            except Exception:
                items = []
            if items:
                self._point(found, items[0], "click")
                return "Torno alla home."
        if found["process"].lower().rsplit(".", 1)[0] in BROWSERS:
            self.backend.focus(found["hwnd"])
            self.backend.press(["alt", "home"])
            return "Torno alla pagina iniziale."
        return "Non trovo la home in questa finestra."

    # --- striscia con i comandi del momento ----------------------------------------------------
    def _do_show_commands(self):
        text = self._do_context_help()
        self.show_strip(text)
        return "Ecco i comandi per questa finestra."

    def _do_hide_commands(self):
        self.show_strip(None)
        return "Comandi nascosti."

    # --- frecce ai lati delle righe (es. Netflix) ---------------------------------------
    def _do_row_scroll(self, dir):
        return self._renumber(self._row_scroll(dir))

    def _row_scroll(self, dir):
        found = self.find_window(None)
        if found is None:
            return None
        right = dir == "destra"
        pattern = r"(successiv|next|avanti|destra|scorri a destra)" if right else \
            r"(precedent|previous|indietro|sinistra|scorri a sinistra)"
        try:
            buttons = [i for i in self.elements(found["hwnd"]) if i.get("type") in ("Button", "Hyperlink")
                       and re.search(pattern, i.get("name", ""), re.I)]
        except Exception:
            buttons = []
        if buttons:
            self._point(found, buttons[0], "click")
            return "Riga " + ("avanti." if right else "indietro.")
        # Freccia non dichiarata: la freccia compare al bordo della riga dell'elemento
        # selezionato; ci porto il puntatore e clicco. Altrimenti uso i tasti.
        rect = self.backend.window_rect(found["hwnd"])
        if self.selected is not None and self.selected[0] == found["hwnd"] and rect:
            item = self.selected[1]
            x = rect[2] - 60 if right else rect[0] + 45
            y = item["y"] + item["h"] // 2
            self.backend.focus(found["hwnd"])
            self.backend.click(x, y, True)
            return "Riga " + ("avanti." if right else "indietro.")
        self.backend.focus(found["hwnd"])
        for _ in range(4):
            self.backend.press(["destra" if right else "sinistra"])
        return "Riga " + ("avanti" if right else "indietro") + " (con i tasti freccia)."

    def _renumber(self, reply):
        """Dopo lo scorrimento di una riga i numeri vecchi non valgono più: li rimetto."""
        if reply is None or self.numbered is None or self.clock() - self.numbered[2] > self.CONTEXT_SECONDS:
            return reply
        time.sleep(0.7)                    # l'animazione della riga
        again = self._do_show_numbers()
        return reply + (" " + again.split("\n", 1)[0] if again else "")

    # --- schermo intero per programma ------------------------------------------------------
    @staticmethod
    def _app_name(found) -> str:
        """Nome del programma senza .exe; per browser e app dello Store il sito/app
        dal titolo (Netflix, YouTube, Disney+, Prime Video)."""
        process = found["process"].lower().rsplit(".", 1)[0]
        if process in BROWSERS or process in ("applicationframehost", "wwahost", "msedgewebview2"):
            title = found["title"].lower()
            for name, key in (("netflix", "netflix"), ("youtube", "youtube"),
                              ("disney", "disney"), ("prime video", "primevideo")):
                if name in title:
                    return key
        return process

    def _fullscreen_keys(self, found):
        app = self._app_name(found)
        if app in FULLSCREEN_KEYS:
            return FULLSCREEN_KEYS[app]
        if app in ("youtube", "disney", "primevideo"):
            return (["f"], ["esc"])
        return (["f11"], ["f11"])           # browser, Esplora file e programmi sconosciuti

    def _do_fullscreen(self, on=True, bare=False):
        if bare and not self.is_fullscreen_front():
            return None                     # «esci» da solo: solo se qualcosa è a schermo intero
        found = self.find_window(None)
        if found is None:
            return None
        keys = self._fullscreen_keys(found)[0 if on else 1]
        self.target = found["hwnd"]
        self.backend.focus(found["hwnd"])
        self.backend.press(keys)
        return ("Schermo intero" if on else "Esco dallo schermo intero") + f" ({'+'.join(keys).upper()})."

    def is_fullscreen_front(self) -> bool:
        """La finestra davanti occupa tutto lo schermo?"""
        try:
            found = self._current(self.windows())
            rect = self.backend.window_rect(found["hwnd"]) if found else None
            screen = self.backend.screen_size()
        except Exception:
            return False
        return bool(rect and screen and rect[0] <= 0 and rect[1] <= 0
                    and rect[2] >= screen[0] and rect[3] >= screen[1])

    # --- Gestione attività e chiusura forzata ------------------------------------------------
    def _do_task_manager(self):
        self.backend.press(["ctrl", "shift", "esc"])
        return "Apro Gestione attività."

    def _do_force_close(self, window):
        found = self.find_window(window, allow_lumi=True)
        if found is None:
            return None
        if found.get("lumi"):
            return "Non chiudo forzatamente Lumi: di' «chiudi Lumi» o «riavvia Lumi»."

        def run():
            ok = self.backend.kill(found["pid"])
            return ("Chiuso forzatamente " + found["title"][:50] + "." if ok else
                    "Non riesco a chiudere " + found["title"][:50] + ".")
        return self._ask("", True, "Chiudo forzatamente " + found["title"][:50]
                         + " (si perde quello che non è salvato)", run)

    # --- griglia a 9 caselle e mouse a piccoli passi -----------------------------------------
    GRID_SECONDS = 90

    def grid_active(self) -> bool:
        return self.grid is not None and self.clock() - self.grid[5] <= self.GRID_SECONDS

    def _do_grid_start(self):
        screen = self.backend.screen_size() or (1280, 720)
        self.grid = (0, 0, screen[0], screen[1], [], self.clock())
        self.show_grid(self.grid[:4])
        _numbers(True)
        return "Griglia: di' un numero da 1 a 9 per stringere, poi «clicca». «Chiudi griglia» per uscire."

    def _do_grid_pick(self, number):
        if not self.grid_active() or not 1 <= number <= 9:
            return None
        x, y, w, h, history, _ = self.grid
        col, row = (number - 1) % 3, (number - 1) // 3
        cell = (x + col * w // 3, y + row * h // 3, max(1, w // 3), max(1, h // 3))
        self.grid = (*cell, history + [(x, y, w, h)], self.clock())
        self.backend.move_mouse(cell[0] + cell[2] // 2, cell[1] + cell[3] // 2, True)
        self.show_grid(cell)
        if cell[2] < 45 or cell[3] < 45:
            return "Casella piccola: di' «clicca», oppure «mouse di poco a destra»."
        return f"Casella {number}. Ancora un numero o «clicca»."

    def _do_grid_back(self):
        if not self.grid_active() or not self.grid[4]:
            return None
        previous = self.grid[4][-1]
        self.grid = (*previous, self.grid[4][:-1], self.clock())
        self.show_grid(previous)
        return "Torno alla griglia più grande."

    def _do_grid_close(self):
        if self.grid is None:
            return None
        self.grid = None
        self.show_grid(None)
        _numbers(False)
        return "Griglia chiusa."

    def _do_click_here(self, double=False, right=False):
        """Clic dove si trova il puntatore (centro della griglia o dopo uno spostamento)."""
        if self.grid_active():
            x, y, w, h = self.grid[:4]
            point = (x + w // 2, y + h // 2)
            self.grid = None
            self.show_grid(None)
            _numbers(False)
        else:
            point = self.backend.cursor()
        if point is None:
            return None
        if right:
            self.backend.click(point[0], point[1], True, double, True)
        else:
            self.backend.click(point[0], point[1], True, double)
        return "Doppio clic." if double else ("Clic destro." if right else "Clic.")

    def _do_nudge(self, dir, amount=50):
        steps = {"destra": (1, 0), "sinistra": (-1, 0), "su": (0, -1), "giu": (0, 1), "giù": (0, 1)}
        if dir == "ancora":
            if self.last_nudge is None:
                return None
            dir, amount = self.last_nudge
        dx, dy = steps[dir]
        point = self.backend.cursor()
        if point is None:
            return None
        self.backend.move_mouse(point[0] + dx * amount, point[1] + dy * amount, True)
        self.last_nudge = (dir, amount)
        return "Mouse " + ("di poco " if amount < 50 else "") + "a " + dir + "."


def _numbers(on: bool) -> None:
    """Con la griglia aperta i numeri valgono senza dire «Lumi» (vedi risposte.py)."""
    try:
        import risposte
        risposte.expect_numbers(ControlService.GRID_SECONDS) if on else risposte.numbers_done()
    except ImportError:
        pass


def _phonetic(text: str) -> str:
    """Scrittura semplificata «come suona» (italiano/inglese): dip→dip, deep→dip."""
    t = text.lower()
    for a, b in (("ee", "i"), ("ea", "i"), ("oo", "u"), ("ou", "au"), ("ph", "f"), ("th", "t"),
                 ("ck", "k"), ("ch", "k"), ("sh", "sc"), ("w", "u"), ("y", "i"), ("q", "k"),
                 ("c", "k"), ("h", ""), ("x", "ks"), ("j", "g")):
        t = t.replace(a, b)
    out = []
    for ch in t:
        if not out or out[-1] != ch:
            out.append(ch)
    return "".join(out)


def _sounds_like(spoken: str, name: str) -> float:
    import difflib
    if not spoken or not name:
        return 0.0
    written = difflib.SequenceMatcher(None, spoken, name).ratio()
    sound = difflib.SequenceMatcher(None, _phonetic(spoken), _phonetic(name)).ratio()
    return max(written, sound)


def _lumi_action(action: str) -> bool:
    try:
        import lumi_comandi
        return lumi_comandi.run_action(action)
    except ImportError:
        return False
