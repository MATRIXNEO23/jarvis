"""Chat unica di Lumi (scelta A, 15/11): elenco delle chat del progetto attivo + archivio.

Una sola finestra per modello locale e GPT. Ogni scambio con un modello finisce nella chat
selezionata (`registra_scambio`), qualunque modello abbia risposto; le risposte ai comandi
restano visibili in chat ma non si salvano nella conversazione. Le chat vivono nel
`ChatSessionStore` già esistente, una lista per progetto («Generale» fuori dai progetti).
Le vecchie chat non vengono convertite (decisione utente): si possono eliminare.
"""
from __future__ import annotations

import sqlite3
import threading

_CURRENT = {"elenco": None}
_LOCK = threading.Lock()


def registra_scambio(question: str, answer: str) -> bool:
    """Salva domanda e risposta nella chat selezionata; False se l'elenco non c'è."""
    elenco = _CURRENT["elenco"]
    if elenco is None or not str(question).strip() or not str(answer).strip():
        return False
    return elenco.save(str(question), str(answer))


def contesto_recente(count: int = 6) -> list[tuple[str, str]]:
    """Ultimi scambi della chat selezionata (per i modelli; vedi sezione Contesto)."""
    elenco = _CURRENT["elenco"]
    return elenco.recent(count) if elenco is not None else []


def progetto_cambiato() -> None:
    elenco = _CURRENT["elenco"]
    if elenco is not None:
        elenco.refresh(show=True)


class ElencoChat:
    """Logica dell'elenco (senza Tk, così si prova facilmente) + interfaccia opzionale."""

    def __init__(self, store, get_project_id, show_history, notify=lambda text: None):
        self.store = store
        self.get_project_id = get_project_id
        self.show_history = show_history       # (titolo, coppie) -> ridisegna la chat
        self.notify = notify
        self.view = None
        _CURRENT["elenco"] = self

    # --- archivio --------------------------------------------------------------------
    def _scope(self):
        return self.get_project_id()

    def current(self):
        try:
            return self.store.active_chat(project_id=self._scope())
        except (OSError, sqlite3.Error, ValueError):
            return None

    def chats(self):
        try:
            return self.store.list_chats(project_id=self._scope())
        except (OSError, sqlite3.Error, ValueError):
            return []

    def new_chat(self, title="Nuova chat"):
        try:
            info = self.store.create_chat(title, project_id=self._scope(), activate=True)
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT > Nuova chat non creata: " + type(exc).__name__)
            return None
        self.refresh(show=True)
        return info.id

    def select(self, chat_id):
        try:
            self.store.select_chat(chat_id, project_id=self._scope())
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT > Chat non aperta: " + type(exc).__name__)
            return False
        self.refresh(show=True)
        return True

    def rename(self, chat_id, title):
        try:
            self.store.rename_chat(chat_id, title, project_id=self._scope())
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT > Nome non cambiato: " + str(exc)[:80])
            return False
        self.refresh(show=False)
        return True

    def delete(self, chat_id):
        try:
            self.store.delete_chat(chat_id, project_id=self._scope())
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT > Chat non eliminata: " + type(exc).__name__)
            return False
        remaining = self.chats()
        if remaining:
            self.store.select_chat(remaining[0].id, project_id=self._scope())
        self.refresh(show=True)
        return True

    def save(self, question, answer):
        with _LOCK:
            chat_id = self.current()
            try:
                if chat_id is None:
                    title = " ".join(question.split())[:40] or "Nuova chat"
                    chat_id = self.store.create_chat(title, project_id=self._scope(),
                                                     activate=True).id
                    self.refresh(show=False)
                self.store.append_exchange(chat_id, question, answer,
                                           project_id=self._scope())
                return True
            except (OSError, sqlite3.Error, ValueError):
                return False

    def recent(self, count):
        chat_id = self.current()
        if chat_id is None:
            return []
        try:
            return list(self.store.recent_pairs(chat_id, project_id=self._scope(), count=count))
        except (OSError, sqlite3.Error, ValueError):
            return []

    def refresh(self, show=True):
        chats = self.chats()
        current = self.current()
        if self.view is not None:
            self.view.populate(chats, current)
        if show:
            pairs = []
            title = "Nuova chat"
            if current is not None:
                try:
                    pairs = self.store.display_pairs(current, project_id=self._scope(), limit=100)
                    title = next((c.title for c in chats if c.id == current), title)
                except (OSError, sqlite3.Error, ValueError):
                    pairs = []
            self.show_history(title, pairs)


class ElencoView:
    """Barra laterale apribile (☰) con le chat: nuova, rinomina, elimina."""

    def __init__(self, header, body, before, elenco, *, ask_text, confirm):
        import tkinter as tk
        from tkinter import ttk
        self.elenco = elenco
        self.ask_text = ask_text
        self.confirm = confirm
        self.ids = []
        self.title = tk.StringVar(master=header, value="Nuova chat")
        ttk.Button(header, text="☰", width=3, command=self.toggle).pack(side="left")
        ttk.Label(header, textvariable=self.title).pack(side="left", padx=6)
        ttk.Button(header, text="+", width=3, command=elenco.new_chat).pack(side="right")
        self.side = ttk.Frame(body)
        self.listbox = tk.Listbox(self.side, width=16, activestyle="none", exportselection=False,
                                  bg="#031522", fg="#bfeeff", selectbackground="#136488",
                                  relief="flat", highlightthickness=0, font=("Segoe UI", 9))
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self._picked)
        row = ttk.Frame(self.side)
        row.pack(fill="x", pady=(3, 0))
        ttk.Button(row, text="Rinomina", command=self._rename).pack(side="left", expand=True, fill="x")
        ttk.Button(row, text="Elimina", command=self._delete).pack(side="left", expand=True, fill="x")
        self.before = before
        self.open = False
        elenco.view = self

    def toggle(self):
        if self.open:
            self.side.pack_forget()
        else:
            self.side.pack(side="left", fill="y", padx=(0, 6), before=self.before)
        self.open = not self.open

    def populate(self, chats, current):
        self.ids = [c.id for c in chats]
        self.listbox.delete(0, "end")
        for chat in chats:
            self.listbox.insert("end", chat.title)
        if current in self.ids:
            self.listbox.selection_set(self.ids.index(current))
            self.title.set(chats[self.ids.index(current)].title)
        else:
            self.title.set("Nuova chat")

    def _selected(self):
        picked = self.listbox.curselection()
        return self.ids[picked[0]] if picked else None

    def _picked(self, _event=None):
        chat_id = self._selected()
        if chat_id is not None and chat_id != self.elenco.current():
            self.elenco.select(chat_id)

    def _rename(self):
        chat_id = self._selected()
        if chat_id is not None:
            title = self.ask_text("Rinomina chat", "Nuovo nome della chat:")
            if title:
                self.elenco.rename(chat_id, title)

    def _delete(self):
        chat_id = self._selected()
        if chat_id is not None and self.confirm("Elimina chat", "Eliminare questa chat e i suoi messaggi?"):
            self.elenco.delete(chat_id)
