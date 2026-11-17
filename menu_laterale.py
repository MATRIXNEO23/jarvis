"""Menu laterale come ChatGPT (15/11 sera, punto 1 della lista concordata).

    ☰                       apre/chiude il menu
    ＋ Nuovo progetto
    📁 Lavoro          ▾    clic: apre o chiude
        💬 Preventivi
        ＋ Nuova chat qui
    ─────────
    💬 Chat libera          chat fuori dai progetti
    ＋ Nuova chat
    ─────────
    ✈ Telegram              (punto 5: chat dei messaggi del bot)

Clic destro su chat o progetto: Rinomina, Elimina, Sposta in progetto…
Aprire una chat di un altro progetto cambia anche il progetto attivo (switch_context).
I progetti sono quelli di workspace_memory (stesso archivio della memoria di progetto);
le chat quelle di ChatSessionStore. Logica senza Tk in `Albero`, così si prova facilmente.
"""
from __future__ import annotations

import sqlite3


class Albero:
    """Operazioni del menu: progetti (workspace) + chat (ChatSessionStore)."""

    def __init__(self, store, *, projects, create_project, rename_project, trash_project,
                 current_project, switch, after_change, notify=lambda text: None):
        self.store = store
        self.projects = projects                  # () -> [(id, nome)]
        self.create_project = create_project      # nome -> id
        self.rename_project = rename_project
        self.trash_project = trash_project
        self.current_project = current_project    # () -> id | None
        self.switch = switch                      # id | None -> bool
        self.after_change = after_change          # ridisegna chat e menu
        self.notify = notify

    def chats(self, project_id):
        try:
            return list(self.store.list_chats(project_id=project_id))
        except (OSError, sqlite3.Error, ValueError):
            return []

    def modelli(self):
        """{chat_id: {"online","offline"}}; vuoto se il database non risponde."""
        try:
            return self.store.models()
        except (OSError, sqlite3.Error, ValueError, AttributeError):
            return {}

    def active(self, project_id):
        try:
            return self.store.active_chat(project_id=project_id)
        except (OSError, sqlite3.Error, ValueError):
            return None

    def apri_chat(self, chat_id, project_id) -> bool:
        try:
            self.store.select_chat(chat_id, project_id=project_id)
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT / ERRORE > Chat non aperta: " + type(exc).__name__)
            return False
        if project_id != self.current_project():
            return bool(self.switch(project_id))      # mostra la chat scelta del progetto
        self.after_change()
        return True

    def nuova_chat(self, project_id):
        try:
            info = self.store.create_chat("Nuova chat", project_id=project_id, activate=True)
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT / ERRORE > Nuova chat non creata: " + type(exc).__name__)
            return None
        if project_id != self.current_project():
            self.switch(project_id)
        else:
            self.after_change()
        return info.id

    def nuovo_progetto(self, name):
        name = (name or "").strip()
        if not name:
            return None
        try:
            ident = self.create_project(name)
        except Exception as exc:          # nome non valido o archivio non disponibile
            self.notify("PROGETTI / ERRORE > " + str(exc)[:120])
            return None
        self.notify("PROGETTI > Progetto creato: " + name + ".")
        self.switch(ident)
        return ident

    def rinomina_chat(self, chat_id, project_id, title):
        try:
            self.store.rename_chat(chat_id, (title or "").strip(), project_id=project_id)
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT / ERRORE > Nome non cambiato: " + str(exc)[:100])
            return False
        self.after_change()
        return True

    def elimina_chat(self, chat_id, project_id):
        try:
            self.store.delete_chat(chat_id, project_id=project_id)
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT / ERRORE > Chat non eliminata: " + type(exc).__name__)
            return False
        self.after_change()
        return True

    def sposta_chat(self, chat_id, from_project, to_project):
        if from_project == to_project:
            return False
        try:
            self.store.move_chat(chat_id, from_project=from_project, to_project=to_project)
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT / ERRORE > Chat non spostata: " + type(exc).__name__)
            return False
        self.after_change()
        return True

    def rinomina_progetto(self, project_id, name):
        try:
            self.rename_project(project_id, (name or "").strip())
        except Exception as exc:
            self.notify("PROGETTI / ERRORE > " + str(exc)[:120])
            return False
        self.after_change()
        return True

    def elimina_progetto(self, project_id):
        """Elimina il progetto e le sue chat (dopo conferma nella vista)."""
        if project_id == self.current_project():
            if not self.switch(None):
                return False
        for chat in self.chats(project_id):
            try:
                self.store.delete_chat(chat.id, project_id=project_id)
            except (OSError, sqlite3.Error, ValueError):
                pass
        try:
            self.trash_project(project_id)
        except Exception as exc:
            self.notify("PROGETTI / ERRORE > " + str(exc)[:120])
            return False
        self.after_change()
        return True


SIMBOLI = {"offline": "🤖", "online": "📡"}


def etichetta(title, models=None) -> str:
    """Simboli piccoli prima del nome: 🤖 modello offline, 📡 online; 💬 se nessuno."""
    marks = "".join(SIMBOLI[m] for m in ("offline", "online") if m in (models or ()))
    return (marks or "💬") + " " + title


def esporta_json(store, chat_id, project_id, path) -> int:
    """Scrive tutta la chat in un file JSON; ritorna il numero di messaggi."""
    import json
    from pathlib import Path
    data = store.export_chat(chat_id, project_id=project_id)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(data["messages"])


class MenuView:
    """Il menu in Tk: albero verticale, clic per aprire, clic destro per le azioni."""

    def __init__(self, header, body, before, albero: Albero, *, ask_text, confirm,
                 ask_file=None, import_chat=None, ask_save=None, notify=None):
        import tkinter as tk
        from tkinter import ttk
        self.tk = tk
        self.albero = albero
        self.ask_save = ask_save
        self.notify = notify or (lambda text: None)
        self.ask_text = ask_text
        self.confirm = confirm
        self.items = {}                        # iid -> (tipo, project_id, chat_id)
        self.open_projects = set()
        self.title = tk.StringVar(master=header, value="Nuova chat")
        ttk.Button(header, text="☰", width=3, command=self.toggle).pack(side="left")
        ttk.Label(header, textvariable=self.title).pack(side="left", padx=6)
        ttk.Button(header, text="+", width=3,
                   command=lambda: albero.nuova_chat(albero.current_project())).pack(side="right")
        self.side = ttk.Frame(body)
        ttk.Button(self.side, text="＋ Nuovo progetto", command=self._new_project).pack(fill="x")
        style = ttk.Style(body)
        style.configure("Lumi.Menu.Treeview", background="#031522", fieldbackground="#031522",
                        foreground="#bfeeff", rowheight=22, borderwidth=0)
        self.tree = ttk.Treeview(self.side, show="tree", selectmode="browse",
                                 style="Lumi.Menu.Treeview", height=18)
        self.tree.column("#0", width=190)
        self.tree.pack(fill="both", expand=True, pady=(3, 0))
        self.tree.bind("<ButtonRelease-1>", self._click)
        self.tree.bind("<Button-3>", self._context)
        self.tree.bind("<Return>", self._click)
        if ask_file is not None and import_chat is not None:
            ttk.Button(self.side, text="Importa da ChatGPT/Claude…",
                       command=lambda: (lambda path: path and import_chat(path))(ask_file())
                       ).pack(fill="x", pady=(3, 0))
        self.before = before
        self.open = False
        self.extra = []      # voci in fondo (lista o funzione), es. un ✈ per contatto Telegram

    def toggle(self):
        if self.open:
            self.side.pack_forget()
        else:
            self.side.pack(side="left", fill="y", padx=(0, 6), before=self.before)
            self.populate()
        self.open = not self.open

    # ElencoChat chiama populate(chats, current) dopo ogni cambio: si ridisegna tutto.
    def populate(self, _chats=None, _current=None):
        tree = self.tree
        tree.delete(*tree.get_children())
        self.items.clear()
        current_project = self.albero.current_project()
        current_chat = self.albero.active(current_project)
        marks = self.albero.modelli()
        self.titles = {}
        selected = None
        for project_id, name in self.albero.projects():
            is_open = project_id in self.open_projects or project_id == current_project
            node = tree.insert("", "end", text="📁 " + name, open=is_open)
            self.items[node] = ("progetto", project_id, None)
            for chat in self.albero.chats(project_id):
                iid = tree.insert(node, "end", text=etichetta(chat.title, marks.get(chat.id)))
                self.titles[iid] = chat.title
                self.items[iid] = ("chat", project_id, chat.id)
                if project_id == current_project and chat.id == current_chat:
                    selected = iid
            iid = tree.insert(node, "end", text="＋ Nuova chat qui")
            self.items[iid] = ("nuova", project_id, None)
        sep = tree.insert("", "end", text="──────────")
        self.items[sep] = ("sep", None, None)
        for chat in self.albero.chats(None):
            iid = tree.insert("", "end", text=etichetta(chat.title, marks.get(chat.id)))
            self.titles[iid] = chat.title
            self.items[iid] = ("chat", None, chat.id)
            if current_project is None and chat.id == current_chat:
                selected = iid
        iid = tree.insert("", "end", text="＋ Nuova chat")
        self.items[iid] = ("nuova", None, None)
        extra = self.extra() if callable(self.extra) else self.extra
        for label, action in extra:
            sep = tree.insert("", "end", text="──────────")
            self.items[sep] = ("sep", None, None)
            iid = tree.insert("", "end", text=label)
            self.items[iid] = ("extra", None, action)
        title = "Nuova chat"
        if selected is not None:
            tree.selection_set(selected)
            tree.see(selected)
            title = self.titles.get(selected, title)
        self.title.set(title)

    def _click(self, _event=None):
        iid = self.tree.focus()
        kind, project_id, chat_id = self.items.get(iid, ("sep", None, None))
        if kind == "progetto":
            if project_id in self.open_projects:
                self.open_projects.discard(project_id)
            else:
                self.open_projects.add(project_id)
            self.tree.item(iid, open=project_id in self.open_projects)
        elif kind == "chat":
            self.albero.apri_chat(chat_id, project_id)
        elif kind == "nuova":
            self.albero.nuova_chat(project_id)
        elif kind == "extra":
            chat_id()

    def _new_project(self):
        name = self.ask_text("Nuovo progetto", "Nome del progetto:")
        if name:
            ident = self.albero.nuovo_progetto(name)
            if ident:
                self.open_projects.add(ident)

    def _context(self, event):
        iid = self.tree.identify_row(event.y)
        kind, project_id, chat_id = self.items.get(iid, ("sep", None, None))
        if kind not in ("chat", "progetto"):
            return
        self.tree.selection_set(iid)
        menu = self.tk.Menu(self.tree, tearoff=0)
        if kind == "chat":
            menu.add_command(label="Rinomina", command=lambda: self._rename_chat(iid, project_id, chat_id))
            move = self.tk.Menu(menu, tearoff=0)
            for other_id, name in self.albero.projects():
                if other_id != project_id:
                    move.add_command(label="📁 " + name, command=lambda o=other_id: self.albero.sposta_chat(
                        chat_id, project_id, o))
            if project_id is not None:
                move.add_command(label="Fuori dai progetti",
                                 command=lambda: self.albero.sposta_chat(chat_id, project_id, None))
            menu.add_cascade(label="Sposta in progetto", menu=move)
            if self.ask_save is not None:
                menu.add_command(label="Esporta (JSON)…",
                                 command=lambda: self._export_chat(iid, project_id, chat_id))
            menu.add_separator()
            menu.add_command(label="Elimina", command=lambda: self._delete_chat(iid, project_id, chat_id))
        else:
            menu.add_command(label="Nuova chat qui", command=lambda: self.albero.nuova_chat(project_id))
            menu.add_command(label="Rinomina", command=lambda: self._rename_project(iid, project_id))
            menu.add_separator()
            menu.add_command(label="Elimina progetto", command=lambda: self._delete_project(iid, project_id))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _export_chat(self, iid, project_id, chat_id):
        title = getattr(self, "titles", {}).get(iid, "chat")
        path = self.ask_save(title)
        if not path:
            return
        try:
            count = esporta_json(self.albero.store, chat_id, project_id, path)
        except (OSError, sqlite3.Error, ValueError) as exc:
            self.notify("CHAT / ERRORE > Esportazione non riuscita: " + str(exc)[:100])
            return
        self.notify("CHAT > Esportata «%s»: %d messaggi in %s" % (title, count, path))

    def _rename_chat(self, iid, project_id, chat_id):
        name = self.ask_text("Rinomina chat", "Nuovo nome:")
        if name:
            self.albero.rinomina_chat(chat_id, project_id, name)

    def _delete_chat(self, iid, project_id, chat_id):
        if self.confirm("Elimina chat", "Eliminare «%s» e i suoi messaggi?"
                        % getattr(self, "titles", {}).get(iid, self.tree.item(iid, "text")[2:])):
            self.albero.elimina_chat(chat_id, project_id)

    def _rename_project(self, iid, project_id):
        name = self.ask_text("Rinomina progetto", "Nuovo nome:")
        if name:
            self.albero.rinomina_progetto(project_id, name)

    def _delete_project(self, iid, project_id):
        if self.confirm("Elimina progetto", "Eliminare il progetto «%s» con tutte le sue chat?"
                        % self.tree.item(iid, "text")[2:]):
            self.albero.elimina_progetto(project_id)


# --- vecchi progetti: si riparte da zero (decisione dell'utente, 15/11 sera) ----------------
def vecchi_progetti_da_chiedere(flag_path) -> bool:
    from pathlib import Path
    return not Path(flag_path).exists()


def cancella_tutti_i_progetti(workspace, store, *, trash_folders=None, brain=None) -> int:
    """Elimina i progetti esistenti: chat, cartelle (nel Cestino) e ricordi collegati."""
    from pathlib import Path
    removed = 0
    folders = []
    ids = []
    for project in workspace.projects(limit=200):
        ident = project["id"]
        try:
            for chat in store.list_chats(project_id=ident):
                store.delete_chat(chat.id, project_id=ident)
        except (OSError, sqlite3.Error, ValueError):
            pass
        try:
            folders.append(workspace.project_directory(ident))
        except Exception:
            pass
        try:
            workspace.trash_project(ident)
            removed += 1
            ids.append(ident)
        except Exception:
            pass
    if brain is not None and ids:
        brain.clear_ricordi(project_ids=ids)
    if trash_folders is not None:
        trash_folders([f for f in folders if Path(f).exists()])
    return removed


def cancella_vecchi_progetti(workspace, store, flag_path, *, trash_folders=None) -> int:
    """Elimina i progetti esistenti (cartelle nel Cestino) e le loro chat; poi segna fatto."""
    removed = cancella_tutti_i_progetti(workspace, store, trash_folders=trash_folders)
    segna_fatto(flag_path)
    return removed


def segna_fatto(flag_path) -> None:
    import json
    from pathlib import Path
    path = Path(flag_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"progetti_nuovi": True}), encoding="utf-8")
