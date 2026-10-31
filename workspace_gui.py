"""Simple local workspace manager for the Windows Tkinter JARVIS HUD.

No unrelated data is read or written; a project's summary is explicitly
edited and saved by the owner, while its last turns are automatically copied
to its own CONTINUITA.md snapshot by WorkspaceMemory.
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox,simpledialog,ttk

from workspace_memory import WorkspaceError


class ProjectManagerWindow:
    def __init__(self,parent,memory,on_open,on_general,on_change,
                 can_modify=None,on_renamed=None,on_trashed=None):
        self.parent=parent
        self.memory=memory
        self.on_open=on_open
        self.on_general=on_general
        self.on_change=on_change
        self.can_modify=can_modify or (lambda:True)
        self.on_renamed=on_renamed or (lambda _ident,_name:None)
        self.on_trashed=on_trashed or (lambda _ident:None)
        self.show_trash=False
        self.window=None
        self._rows=[]

    def show(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()
            return
        w=tk.Toplevel(self.parent)
        self.window=w
        w.title("JARVIS // Memoria e progetti")
        w.geometry("820x620")
        w.minsize(570,450)
        w.configure(bg="#020b14")
        area=ttk.Frame(w,padding=12)
        area.pack(fill="both",expand=True)
        ttk.Label(area,text="Progetti e continuità",
                  font=("Segoe UI",15,"bold")).pack(anchor="w")
        ttk.Label(area,text=(
            "I progetti attivi hanno un pallino orbitante. Clicca il pallino "
            "o seleziona Apri. Il file CONTINUITA.md viene salvato sul PC; "
            "uno stato consolidato va inserito qui esplicitamente."),
            wraplength=700).pack(anchor="w",pady=(2,8))

        self.listbox=tk.Listbox(
            area,selectmode=tk.SINGLE,height=9,
            font=("Segoe UI",11),bg="#041726",
            fg="#ceeafa",selectbackground="#12658a")
        self.listbox.pack(fill="x",pady=(0,6))
        self.listbox.bind("<<ListboxSelect>>",lambda _e:self._load_summary())
        actions=ttk.Frame(area)
        actions.pack(fill="x")
        for title,action in (
                ("Nuovo progetto",self._create),
                ("Apri",self._open),
                ("Attiva / archivia",self._toggle),
                ("Generale",self._general),
                ("Apri CONTINUITA.md",self._open_file)):
            ttk.Button(actions,text=title,command=action).pack(
                side="left",padx=(0,6))
        manage=ttk.Frame(area)
        manage.pack(fill="x",pady=(6,4))
        for title,action in (
                ("Rinomina",self._rename),
                ("Elimina (cestino)",self._trash),
                ("Mostra cestino / progetti",self._toggle_trash_view),
                ("Ripristina selezionato",self._restore)):
            ttk.Button(manage,text=title,command=action).pack(
                side="left",padx=(0,6))
        ttk.Label(area,text="Stato consolidato del progetto (modificabile):").pack(
            anchor="w",pady=(14,5))
        self.editor=tk.Text(
            area,height=8,wrap="word",font=("Segoe UI",10),
            bg="#041726",fg="#dbfaff",insertbackground="#16d8ff")
        self.editor.pack(fill="both",expand=True)
        ttk.Button(area,text="Salva stato del progetto",
                   command=self._save_summary).pack(anchor="e",pady=(8,3))
        self.refresh()

    def refresh(self):
        if not self.window or not self.window.winfo_exists():
            return
        self._rows=list(self.memory.trashed_projects() if self.show_trash
                        else self.memory.projects())
        self.listbox.delete(0,"end")
        for p in self._rows:
            icon="♻" if self.show_trash else "●" if p["active"] else "○"
            self.listbox.insert("end",f"{icon}  {p['name']}")
        self.on_change()

    def _selected(self):
        selected=self.listbox.curselection()
        if not selected:
            return None
        idx=selected[0]
        return self._rows[idx] if 0<=idx<len(self._rows) else None

    def _load_summary(self):
        project=self._selected()
        self.editor.delete("1.0","end")
        if project:
            details=self.memory.project(project["id"])
            if details:
                self.editor.insert("1.0",details["summary"])

    def _create(self):
        if not self.can_modify():
            messagebox.showwarning("Progetti",
                "Concludi prima l'attività o chiudi Blocco note.",
                parent=self.window)
            return
        name=simpledialog.askstring(
            "Nuovo progetto","Nome del progetto:",
            parent=self.window)
        if not name:
            return
        try:
            ident=self.memory.create_project(name)
        except (WorkspaceError,OSError) as exc:
            messagebox.showerror("Progetto",str(exc),parent=self.window)
            return
        self.refresh()
        self.on_open(ident)

    def _open(self):
        project=self._selected()
        if project and not self.show_trash:
            self.on_open(project["id"])

    def _general(self):
        self.on_general()

    def _toggle(self):
        project=self._selected()
        if not project or self.show_trash or not self.can_modify():
            return
        try:
            self.memory.set_active(project["id"],not project["active"])
        except (WorkspaceError,OSError) as exc:
            messagebox.showerror("Progetto",str(exc),parent=self.window)
        self.refresh()

    def _toggle_trash_view(self):
        self.show_trash=not self.show_trash
        self.refresh()

    def _rename(self):
        project=self._selected()
        if not project or self.show_trash:
            messagebox.showinfo("Progetti","Seleziona un progetto attivo.",parent=self.window)
            return
        if not self.can_modify():
            messagebox.showwarning("Progetti","Concludi prima l'attività o chiudi Blocco note.",
                                   parent=self.window)
            return
        name=simpledialog.askstring("Rinomina progetto",
             "Nuovo nome per "+project["name"]+":",
             parent=self.window,initialvalue=project["name"])
        if name is None:
            return
        try:
            self.memory.rename_project(project["id"],name)
            self.on_renamed(project["id"],self.memory.project(project["id"])["name"])
        except (WorkspaceError,OSError,ValueError) as exc:
            messagebox.showerror("Rinomina",str(exc),parent=self.window)
            return
        self.refresh()

    def _trash(self):
        project=self._selected()
        if not project or self.show_trash:
            messagebox.showinfo("Progetti","Seleziona un progetto attivo.",parent=self.window)
            return
        if not self.can_modify():
            messagebox.showwarning("Progetti","Concludi prima l'attività o chiudi Blocco note.",
                                   parent=self.window)
            return
        if not messagebox.askyesno(
                "Elimina progetto",
                "Spostare '"+project["name"]+"' nel cestino di Jarvis?\n"
                "Memoria, documenti e cartella NON saranno cancellati.",
                parent=self.window):
            return
        try:
            self.memory.trash_project(project["id"])
            self.on_trashed(project["id"])
        except (WorkspaceError,OSError) as exc:
            messagebox.showerror("Progetti",str(exc),parent=self.window)
            return
        self.refresh()

    def _restore(self):
        project=self._selected()
        if not project or not self.show_trash:
            messagebox.showinfo("Progetti","Apri il cestino e seleziona un progetto.",
                                parent=self.window)
            return
        if not self.can_modify():
            messagebox.showwarning("Progetti","Concludi prima l'attività.",parent=self.window)
            return
        try:
            self.memory.restore_project(project["id"])
        except (WorkspaceError,OSError) as exc:
            messagebox.showerror("Ripristino",str(exc),parent=self.window)
            return
        self.refresh()

    def _save_summary(self):
        project=self._selected()
        if not project or self.show_trash:
            return
        try:
            self.memory.set_summary(
                project["id"],self.editor.get("1.0","end-1c").strip())
        except (WorkspaceError,OSError) as exc:
            messagebox.showerror("Continuità",str(exc),parent=self.window)
            return
        self.refresh()
        messagebox.showinfo(
            "Continuità","Stato salvato localmente nel progetto.",
            parent=self.window)

    def _open_file(self):
        project=self._selected()
        if not project:
            return
        file=self.memory.continuity_file(project["id"])
        if os.name=="nt" and file.is_file():
            os.startfile(str(file))
        else:
            messagebox.showinfo(
                "Continuità",str(file),parent=self.window)
