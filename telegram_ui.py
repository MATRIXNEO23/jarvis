"""Small on-demand Tk windows for Telegram selection and owner voice send.

UI only: Telegram network/voice synthesis run in Lumi workers, never in Tk.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


class TelegramContactsWindow:
    def __init__(self, parent, stored, on_load, on_save,
                 on_open_history=None, on_clear_history=None, on_edit_context=None):
        self.on_edit_context=on_edit_context
        self.on_open_history=on_open_history
        self.on_clear_history=on_clear_history
        self.window=tk.Toplevel(parent)
        self.window.title("LUMI // Telegram — autorizza contatti")
        self.window.geometry("720x550")
        self.window.minsize(540,330)
        self.saved={c["id"]:c for c in stored}
        self.on_save=on_save
        self.on_load=on_load
        self.rows=[]
        panel=ttk.Frame(self.window,padding=12)
        panel.pack(fill="both",expand=True)
        ttk.Label(panel,text="Contatti Telegram autorizzati",
                  font=("Segoe UI",12,"bold")).pack(anchor="w")
        ttk.Label(panel,wraplength=550,
                  text="Spunta i contatti che Lumi può usare. "
                       "Gruppi e bot non vengono mostrati; "
                       "un contatto non selezionato non riceve risposte né vocali.").pack(
                           fill="x",pady=(5,8))
        self.status=tk.StringVar(value="Carica la rubrica e le chat private dall'account.")
        ttk.Label(panel,textvariable=self.status,wraplength=540).pack(anchor="w")
        body=ttk.Frame(panel)
        body.pack(fill="both",expand=True,pady=8)
        self.canvas=tk.Canvas(body,highlightthickness=0)
        scrollbar=ttk.Scrollbar(body,orient="vertical",command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right",fill="y")
        self.canvas.pack(side="left",fill="both",expand=True)
        self.inner=ttk.Frame(self.canvas)
        self.inner_id=self.canvas.create_window((0,0),window=self.inner,anchor="nw")
        self.inner.bind("<Configure>",lambda _e:self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",lambda e:self.canvas.itemconfigure(
            self.inner_id,width=e.width))
        actions=ttk.Frame(panel)
        actions.pack(fill="x")
        self.load_button=ttk.Button(actions,text="Carica contatti Telegram",
                                     command=self.load)
        self.load_button.pack(side="left")
        ttk.Button(actions,text="Annulla",command=self.window.destroy).pack(
            side="right",padx=(6,0))
        self.save_button=ttk.Button(actions,text="Salva le spunte",
                                    command=self.save,state="disabled")
        self.save_button.pack(side="right")
        self.show_local()

    def exists(self):
        return bool(self.window.winfo_exists())

    def focus(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_set()

    def show_local(self):
        if self.saved:
            self.status.set("Contatti già salvati (carica Telegram prima di modificare).")
            for c in self.saved.values():
                line=ttk.Frame(self.inner)
                line.pack(fill="x",pady=2)
                ttk.Label(line,text=(
                    ("✓ " if c["enabled"] else "○ ")+c["name"]+
                    " — elenco non aggiornato")).pack(side="left")
                if c["enabled"]:
                    self.add_history_buttons(line,c["id"])

    def load(self):
        self.load_button.configure(state="disabled")
        self.status.set("Leggo contatti e chat private dal tuo account Telegram...")
        self.on_load()

    def loaded(self, contacts):
        self.load_button.configure(state="normal")
        self.save_button.configure(state="normal")
        for child in self.inner.winfo_children():
            child.destroy()
        self.rows=[]
        for item in contacts:
            pid=item["id"]
            name=item["name"]
            var=tk.BooleanVar(value=self.saved.get(pid,{}).get("enabled",False))
            line=ttk.Frame(self.inner)
            line.pack(fill="x",pady=2)
            ttk.Checkbutton(line,text=f"{name}  [ID {pid}]",
                            variable=var).pack(side="left",padx=5)
            if self.saved.get(pid,{}).get("enabled",False):
                self.add_history_buttons(line,pid)
            self.rows.append((pid,name,var))
        self.status.set(f"Caricati {len(self.rows)} contatti. "
                        "Spunta i destinatari e premi Salva.")
        if not self.rows:
            self.save_button.configure(state="disabled")

    def add_history_buttons(self,frame,peer_id):
        """Local history tools only for contacts already authorized."""
        if self.on_edit_context is not None:
            ttk.Button(frame, text="Contesto del contatto",
                       command=lambda: self.on_edit_context(self.window, peer_id)).pack(
                           side="right", padx=(4, 0))
        if self.on_open_history is not None:
            ttk.Button(frame,text="Apri conversazione",
                       command=lambda p=peer_id:self.on_open_history(p)).pack(
                           side="right",padx=(4,0))
        if self.on_clear_history is not None:
            ttk.Button(frame,text="Cancella cronologia",
                       command=lambda p=peer_id:self.on_clear_history(p)).pack(
                           side="right",padx=(4,0))

    def failed(self, reason):
        self.load_button.configure(state="normal")
        self.status.set("Impossibile caricare i contatti: "+str(reason)[:160])

    def save(self):
        rows=[]
        for pid,name,var in self.rows:
            if var.get() or pid in self.saved:
                rows.append({"id":pid,"name":name,"enabled":bool(var.get())})
        if len(rows)>80:
            messagebox.showwarning("Telegram", "Massimo 80 contatti salvati.",
                                   parent=self.window)
            return
        if self.on_save(rows):
            self.window.destroy()


def edit_telegram_context(parent, name, current, limit):
    return simpledialog.askstring(
        "Contesto del contatto",
        f"{name} — solo con Gemma locale (massimo {limit} caratteri).\n"
        "Scrivi poche indicazioni. Lascia vuoto per rimuovere il contesto.",
        initialvalue=current, parent=parent)


def show_telegram_manual_send(parent, selected_contacts, on_send):
    """Explicit recipient dropdown + editable text + native confirmation."""
    if not selected_contacts:
        messagebox.showinfo("Telegram",
                            "Prima seleziona un contatto in Gestisci contatti.",
                            parent=parent)
        return
    win=tk.Toplevel(parent)
    win.title("LUMI // Invia messaggio vocale Telegram")
    win.geometry("540x310")
    win.minsize(430,280)
    frame=ttk.Frame(win,padding=14)
    frame.pack(fill="both",expand=True)
    ttk.Label(frame,text="Destinatario (solo contatti con spunta)").pack(anchor="w")
    names=[f"{c['name']}  [ID {c['id']}]" for c in selected_contacts]
    picker=ttk.Combobox(frame,state="readonly",values=names,width=55)
    picker.current(0)
    picker.pack(fill="x",pady=(3,9))
    ttk.Label(frame,text="Scrivi il messaggio: Lumi lo convertirà in OGG/Opus").pack(
        anchor="w")
    editor=tk.Text(frame,height=6,wrap="word")
    editor.pack(fill="both",expand=True,pady=(4,8))
    row=ttk.Frame(frame)
    row.pack(fill="x")
    ttk.Button(row,text="Annulla",command=win.destroy).pack(side="right",padx=(6,0))

    def confirm_send():
        index=picker.current()
        if index<0:
            return
        content=" ".join(editor.get("1.0","end-1c").split())
        if not 1<=len(content)<=480:
            messagebox.showwarning("Telegram",
                                   "Il messaggio deve essere lungo da 1 a 480 caratteri.",
                                   parent=win)
            return
        contact=selected_contacts[index]
        if messagebox.askyesno("Conferma invio vocale",
            f"Inviare una nota vocale a {contact['name']}?\n\n{content}",
            parent=win,default="no"):
            if on_send(contact["id"],contact["name"],content):
                win.destroy()
    ttk.Button(row,text="Conferma e invia vocale",command=confirm_send).pack(
        side="right")
    editor.focus_set()
