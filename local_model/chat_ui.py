"""Opt-in chat and instance selector embedded in the existing Jarvis HUD.

ARCH-01/F2: Tk widgets and sidecar storage only. No inference, model loads,
implicit legacy migration, Second Brain or credential handling in this module.
"""
from pathlib import Path
import sqlite3
import tkinter as tk
from tkinter import simpledialog, ttk

from .chat_sessions import ChatSessionError, ChatSessionStore


class ChatSessionsPanel:
    """Lightweight Kobold-style multi-chat pane; explicit first activation."""

    def __init__(self, parent, *, store_path, get_project_id, can_change,
                 on_change, on_settings):
        self.store_path = Path(store_path)
        self.get_project_id = get_project_id
        self.can_change = can_change
        self.on_change = on_change
        self.on_settings = on_settings
        self.store = None
        self._active = False
        self._scope = None
        self._selected = None
        self._labels = {}
        self.frame = ttk.Frame(parent)
        self.status = tk.StringVar(master=self.frame, value=(
            "Apri la scheda Chat per usare le conversazioni indipendenti."))
        self.scope_label = tk.StringVar(master=self.frame, value="Chat locali · Gemma")
        header = ttk.Frame(self.frame)
        header.pack(fill="x", pady=(2, 4))
        ttk.Label(header, textvariable=self.scope_label,
                  font=("Segoe UI", 10, "bold")).pack(side="left")
        self.settings_button = ttk.Button(header, text="Impostazioni...",
                                          command=self.on_settings)
        self.settings_button.pack(side="right")
        actions = ttk.Frame(self.frame)
        actions.pack(fill="x", pady=(0, 5))
        ttk.Label(actions, text="Istanza:").pack(side="left", padx=(0, 5))
        self.chat_choice = ttk.Combobox(actions, state="readonly", width=18)
        self.chat_choice.pack(side="left", fill="x", expand=True)
        self.chat_choice.bind("<<ComboboxSelected>>", self._on_combo_change)
        ttk.Button(actions, text="+ Nuova", command=self.create_new).pack(
            side="left", padx=(5, 2))
        ttk.Button(actions, text="Rinomina", command=self.ask_rename).pack(
            side="left")
        body = ttk.Frame(self.frame)
        body.pack(fill="both", expand=True)
        self.view = tk.Text(
            body, height=9, wrap="word", state="disabled", bg="#020d17",
            fg="#d7f6ff", insertbackground="#46ccfa",
            font=("Segoe UI", 10), relief="flat", padx=10, pady=8,
            selectbackground="#136488", selectforeground="#ffffff")
        scroll = ttk.Scrollbar(body, orient="vertical", command=self.view.yview)
        self.view.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.view.pack(side="left", fill="both", expand=True)
        self.view.tag_configure("user", foreground="#caeaff",
                                font=("Segoe UI", 10, "bold"), spacing1=8)
        self.view.tag_configure("model", foreground="#46ccfa",
                                font=("Segoe UI", 10, "bold"), spacing1=8)
        self.view.tag_configure("body", foreground="#e1f5ff", spacing3=9)
        ttk.Label(self.frame, textvariable=self.status,
                  wraplength=390).pack(fill="x", pady=(5, 1))
        self._set_view("Le conversazioni locali non sono ancora aperte.")

    def _set_view(self, value):
        self.view.configure(state="normal")
        self.view.delete("1.0", "end")
        self.view.insert("1.0", value)
        self.view.configure(state="disabled")

    def current_target(self):
        if not self._active or self._selected is None:
            return None
        return (self._selected, self._scope)

    def _ensure(self):
        if self.store is None:
            self.store = ChatSessionStore(self.store_path)

    def _populate(self):
        rows = self.store.list_chats(project_id=self._scope)
        self._labels = {f"{chat.title[:42]} · {chat.id[:6]}": chat.id
                        for chat in rows}
        labels = list(self._labels)
        self.chat_choice["values"] = labels
        selected = next((label for label, chat_id in self._labels.items()
                         if chat_id == self._selected), "")
        self.chat_choice.set(selected)

    def _render(self):
        target = self.current_target()
        if target is None:
            self._set_view("Non è stata selezionata alcuna conversazione.")
            return
        chat_id, project_id = target
        pairs = self.store.recent_pairs(chat_id, project_id=project_id, count=32)
        self.view.configure(state="normal")
        self.view.delete("1.0", "end")
        if not pairs:
            self.view.insert("end", "Nuova conversazione. Scrivi una domanda a Gemma.\n")
        for pair in pairs:
            self.view.insert("end", "TU\n", "user")
            self.view.insert("end", pair[0][1] + "\n\n", "body")
            self.view.insert("end", "GEMMA\n", "model")
            self.view.insert("end", pair[1][1] + "\n\n", "body")
        self.view.see("end")
        self.view.configure(state="disabled")
        self.status.set(
            ("Progetto: " + project_id[:8] if project_id else "Chat generale")
            + " · Ultimi " + str(len(pairs))
            + " scambi visibili (tutti conservati su disco). "
            + "Second Brain non allegato automaticamente.")

    def activate(self):
        """Explicit user action; opens storage and initial chat only on demand."""
        if not self.can_change():
            self.status.set("Operazione in corso: cambia chat dopo la risposta.")
            return False
        try:
            self._ensure()
            scope = self.get_project_id()
            previous = self._selected if self._active else None
            active = self.store.active_chat(project_id=scope)
            if active is None:
                active = self.store.create_chat(project_id=scope,
                                                activate=True).id
            self._active = True
            self._scope = scope
            self._selected = active
            self.scope_label.set("Chat locali · Gemma"
                                 + (" · Progetto" if scope else " · Generale"))
            self._populate()
            self._render()
            if previous != active:
                self.on_change(previous, active)
            return True
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.status.set("Chat non disponibile: " + type(exc).__name__
                            + ". Console e memoria originali invariati.")
            return False

    def scope_changed(self):
        if not self._active:
            return True
        return self.activate()

    def _can_switch(self):
        if not self.can_change():
            self.status.set("Attendi la fine della richiesta prima di cambiare chat.")
            self._populate()
            return False
        return True

    def create_new(self):
        if not self._active:
            if not self.activate():
                return None
        if not self._can_switch():
            return None
        try:
            previous = self._selected
            chat = self.store.create_chat(project_id=self._scope, activate=True)
            self._selected = chat.id
            self._populate()
            self._render()
            self.on_change(previous, chat.id)
            return chat.id
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.status.set("Nuova chat non salvata: " + type(exc).__name__)
            return None

    def select(self, chat_id):
        if not self._active or not self._can_switch():
            return False
        if chat_id == self._selected:
            return True
        try:
            self.store.select_chat(chat_id, project_id=self._scope)
            previous, self._selected = self._selected, chat_id
            self._populate()
            self._render()
            self.on_change(previous, chat_id)
            return True
        except (OSError, sqlite3.Error, ChatSessionError) as exc:
            self.status.set("Impossibile aprire la chat: " + type(exc).__name__)
            self._populate()
            return False

    def _on_combo_change(self, _event=None):
        value = self.chat_choice.get()
        chat_id = self._labels.get(value)
        if chat_id is not None:
            self.select(chat_id)

    def rename_current(self, title):
        if not self._active or not self._can_switch():
            return False
        if self._selected is None:
            return False
        try:
            self.store.rename_chat(self._selected, title,
                                   project_id=self._scope)
            self._populate()
            self._render()
            return True
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.status.set("Rinomina non salvata: " + type(exc).__name__)
            return False

    def ask_rename(self):
        if self.current_target() is None or not self._can_switch():
            return
        name = simpledialog.askstring("Jarvis / Rinomina chat",
                                     "Nuovo titolo:", parent=self.frame)
        if name is not None:
            self.rename_current(name)

    def persist_answer(self, chat_id, question, answer, *, project_id=None):
        if self.store is None:
            raise ChatSessionError("Chat locale non attivata.")
        self.store.append_exchange(chat_id, question, answer,
                                   project_id=project_id)
        if self.current_target() == (chat_id, project_id):
            self._render()

    def report_error(self, message):
        self.status.set(message)
