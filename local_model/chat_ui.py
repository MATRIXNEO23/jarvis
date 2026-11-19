"""Opt-in chat and instance selector embedded in the existing Lumi HUD.

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
        self.frame = ttk.Frame(parent)
        self.status = tk.StringVar(master=self.frame, value=(
            "Apri la scheda Chat per usare le conversazioni indipendenti."))
        self.scope_label = tk.StringVar(master=self.frame, value="Chat locali")
        header = ttk.Frame(self.frame)
        header.pack(fill="x", pady=(2, 4))
        # Collapsible conversation list (open/close like ChatGPT's sidebar).
        self.sidebar_button = ttk.Button(header, text="☰", width=3,
                                         command=self.toggle_sidebar)
        self.sidebar_button.pack(side="left", padx=(0, 6))
        ttk.Label(header, textvariable=self.scope_label,
                  font=("Segoe UI", 10, "bold")).pack(side="left")
        self.settings_button = ttk.Button(header, text="Impostazioni...",
                                          command=self.on_settings)
        self.settings_button.pack(side="right")
        body = ttk.Frame(self.frame)
        body.pack(fill="both", expand=True)
        # ChatGPT/Kobold-style layout: conversation list left, messages right.
        sidebar = self.sidebar = ttk.Frame(body)
        sidebar.pack(side="left", fill="y", padx=(0, 6))
        self.sidebar_open = True
        ttk.Button(sidebar, text="+ Nuova chat", command=self.create_new).pack(
            fill="x", pady=(0, 4))
        self.chat_list = tk.Listbox(
            sidebar, width=18, activestyle="none", exportselection=False,
            bg="#031522", fg="#bfeeff", selectbackground="#136488",
            selectforeground="#ffffff", relief="flat", highlightthickness=0,
            font=("Segoe UI", 9))
        self.chat_list.pack(fill="y", expand=True)
        self.chat_list.bind("<<ListboxSelect>>", self._on_list_select)
        self.chat_list.bind("<Double-Button-1>", lambda _e: self.ask_rename())
        ttk.Button(sidebar, text="Rinomina", command=self.ask_rename).pack(
            fill="x", pady=(4, 0))
        self._row_ids = []
        self._pending = []
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

    def toggle_sidebar(self):
        if self.sidebar_open:
            self.sidebar.pack_forget()
        else:
            self.sidebar.pack(side="left", fill="y", padx=(0, 6), before=self.view)
        self.sidebar_open = not self.sidebar_open
        return self.sidebar_open

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
        self._row_ids = [chat.id for chat in rows]
        self.chat_list.delete(0, "end")
        for chat in rows:
            self.chat_list.insert("end", chat.title[:40])
        self.chat_list.selection_clear(0, "end")
        if self._selected in self._row_ids:
            index = self._row_ids.index(self._selected)
            self.chat_list.selection_set(index)
            self.chat_list.see(index)

    def _render(self):
        target = self.current_target()
        if target is None:
            self._set_view("Non è stata selezionata alcuna conversazione.")
            return
        chat_id, project_id = target
        pairs = self.store.display_pairs(chat_id, project_id=project_id)
        self.view.configure(state="normal")
        self.view.delete("1.0", "end")
        if not pairs:
            self.view.insert("end", "Nuova conversazione. Scrivi una domanda.\n")
        for question, answer in pairs:
            self.view.insert("end", "TU\n", "user")
            self.view.insert("end", question + "\n\n", "body")
            self.view.insert("end", "LUMI\n", "model")
            self.view.insert("end", answer + "\n\n", "body")
        self.view.see("end")
        self.view.configure(state="disabled")
        self.status.set(
            ("Progetto: " + project_id[:8] if project_id else "Chat generale")
            + " · " + str(len(pairs)) + " scambi salvati su disco. "
            + "Al modello arrivano solo gli ultimi, entro il limite di contesto.")

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
            self.scope_label.set("Chat locali"
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

    def _on_list_select(self, _event=None):
        chosen = self.chat_list.curselection()
        if chosen and chosen[0] < len(self._row_ids):
            self.select(self._row_ids[chosen[0]])

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
        name = simpledialog.askstring("Lumi / Rinomina chat",
                                     "Nuovo titolo:", parent=self.frame)
        if name is not None:
            self.rename_current(name)

    def persist_answer(self, chat_id, question, answer, *, project_id=None):
        """Save an exchange; unsaved ones are retried, in order, on the next save.

        Review bug 3 (9/11): a failed write used to be lost silently.
        """
        if self.store is None:
            raise ChatSessionError("Chat locale non attivata.")
        self._pending.append((chat_id, question, answer, project_id))
        while self._pending:
            item_chat, item_q, item_a, item_project = self._pending[0]
            chat = self.store.get_chat(item_chat, project_id=item_project)
            self.store.append_exchange(item_chat, item_q, item_a,
                                       project_id=item_project)
            self._pending.pop(0)
            if chat.title == "Nuova chat":
                # Title from the first question, like classic chat apps.
                title = " ".join(item_q.split())[:40].strip()
                if title:
                    self.store.rename_chat(item_chat, title, project_id=item_project)
        if self.current_target() == (chat_id, project_id):
            self._populate()
            self._render()

    @property
    def pending_count(self):
        return len(self._pending)

    def report_error(self, message):
        self.status.set(message)
