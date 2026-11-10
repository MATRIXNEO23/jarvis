"""Optional on-demand Tk control panel for the trusted Lumi addon manager.

No network, no script execution, no automatic enable after install or update.
All changes are local and explicit; failures are visible to the user.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from addon_manager import AddonError, AddonManager


class AddonSettingsWindow:
    def __init__(self, parent, manager: AddonManager, on_change=None):
        self.manager=manager
        self.on_change=on_change or (lambda:None)
        self.window=tk.Toplevel(parent)
        self.window.title("LUMI // Gestisci add-on")
        self.window.geometry("790x500")
        self.window.minsize(610,390)
        holder=ttk.Frame(self.window,padding=12)
        holder.pack(fill="both",expand=True)
        ttk.Label(holder,text="Add-on di Lumi",
                  font=("Segoe UI",13,"bold")).pack(anchor="w")
        ttk.Label(holder,wraplength=760,
                  text=("I pacchetti .jaddon sono solo descrizioni JSON, "
                        "non installano programmi né eseguono codice. "
                        "Ogni nuova installazione o aggiornamento resta SPENTO. "
                        "Un add-on attivo utilizza esclusivamente azioni "
                        "già approvate dal motore locale.")).pack(
                            fill="x",pady=(6,8))
        self.table=ttk.Treeview(
            holder,columns=("name","version","enabled","actions"),
            show="headings",selectmode="browse",height=12)
        for key,label,width in (
                ("name","Add-on",260),("version","Versione",85),
                ("enabled","Stato",125),("actions","Funzioni",90)):
            self.table.heading(key,text=label)
            self.table.column(key,width=width,stretch=(key=="name"))
        self.table.pack(fill="both",expand=True)
        self.status=tk.StringVar(value="")
        ttk.Label(holder,textvariable=self.status,wraplength=760).pack(
            anchor="w",pady=6)
        controls=ttk.Frame(holder)
        controls.pack(fill="x")
        ttk.Button(controls,text="Installa / aggiorna...",
                   command=self.install).pack(side="left",padx=(0,6))
        ttk.Button(controls,text="Attiva / Disattiva",
                   command=self.toggle).pack(side="left",padx=(0,6))
        ttk.Button(controls,text="Configura",
                   command=self.configure).pack(side="left",padx=(0,6))
        ttk.Button(controls,text="Rimuovi",
                   command=self.remove).pack(side="left",padx=(0,6))
        ttk.Button(controls,text="Ricarica",
                   command=self.reload).pack(side="left")
        ttk.Button(controls,text="Chiudi",
                   command=self.window.destroy).pack(side="right")
        self.reload()

    def exists(self):
        return bool(self.window.winfo_exists())

    def focus(self):
        self.window.deiconify()
        self.window.lift()
        self.window.focus_set()

    def _selected(self):
        selected=self.table.selection()
        return selected[0] if selected else None

    def _error(self, exc):
        messagebox.showerror("Lumi / Add-on",
                             str(exc)[:240],parent=self.window)

    def reload(self):
        try:
            self.manager.refresh()
            for ident in self.table.get_children():
                self.table.delete(ident)
            for item in self.manager.list_installed():
                self.table.insert("", "end", iid=item["id"],values=(
                    item["name"],item["version"],
                    "ATTIVO" if item["enabled"] else "SPENTO",
                    item["action_count"],
                ))
            warnings=self.manager.warnings()
            self.status.set(
                str(len(self.manager.list_installed()))+" add-on installati. "
                +(str(len(warnings))+" file non validi ignorati." if warnings
                  else "Modifiche sincronizzate al prossimo comando GPT."))
        except (AddonError,OSError,ValueError) as exc:
            self._error(exc)

    def install(self):
        path=filedialog.askopenfilename(
            parent=self.window,title="Scegli un add-on verificato",
            filetypes=[("Pacchetto Lumi (.jaddon)","*.jaddon")])
        if not path:
            return
        if not messagebox.askyesno(
            "Lumi / Conferma installazione",
            "Installare o aggiornare questo add-on descrittivo? "
            "Non verrà avviato automaticamente e non verrà eseguito alcun codice.",
            parent=self.window,default="no"):
            return
        try:
            result=self.manager.install(Path(path))
            self.reload()
            self.on_change()
            self.status.set(
                ("Aggiornato " if result["updated"] else "Installato ")+
                result["id"]+" "+result["version"]+". Resta SPENTO.")
        except (AddonError,OSError,ValueError) as exc:
            self._error(exc)

    def toggle(self):
        ident=self._selected()
        if ident is None:
            self.status.set("Seleziona un add-on dall'elenco.")
            return
        try:
            item=next(c for c in self.manager.list_installed() if c["id"]==ident)
        except StopIteration:
            self.reload()
            return
        enabled=not item["enabled"]
        if enabled and not messagebox.askyesno(
                "Autorizza add-on",
                "Attivare "+item["name"]+"? Le azioni descritte saranno visibili "
                "a Lumi GPT e richiamabili solo tramite il motore locale "
                "con le normali verifiche.",
                parent=self.window,default="no"):
            return
        try:
            self.manager.set_enabled(ident,enabled)
            self.reload()
            self.on_change()
        except (AddonError,OSError,ValueError) as exc:
            self._error(exc)

    def configure(self):
        if self._selected() == 'musica':
            service = getattr(self.manager, 'music_service', None)
            if service is None:
                self._error('Musica non disponibile: reinstalla la cartella musica dal pacchetto completo.')
                return
            try:
                from musica.ui import MusicSettings
                MusicSettings(self.window, service, on_change=self.on_change)
            except (ImportError, OSError, ValueError) as exc:
                self._error('Musica non disponibile: ' + str(exc)[:120])
            return
        if self._selected() == 'programmi_app':
            try:
                from program_apps.ui import ProgramSettings
                ProgramSettings(self.window,self.manager.program_service,on_change=self.on_change)
            except (ImportError,OSError,ValueError) as exc:
                self._error('Programmi e app non disponibile: '+str(exc)+
                            '. Reinstalla la cartella program_apps dal pacchetto completo.')
            return
        if self._selected() != "accesso_file":
            self.status.set("Seleziona un’add-on con configurazione disponibile.")
            return
        try:
            from file_access.ui import FolderSettings
            FolderSettings(self.window,self.manager.file_service,on_change=self.on_change)
        except (ImportError,OSError,ValueError) as exc:
            self._error("Configurazione Accesso file non disponibile: "+str(exc)+
                        ". Reinstalla il pacchetto completo se manca file_access/.")

    def remove(self):
        ident=self._selected()
        if ident is None:
            self.status.set("Seleziona un add-on.")
            return
        if not messagebox.askyesno(
                "Rimuovi add-on",
                "Eliminare la registrazione di "+ident+"? "
                "Le capacità spariranno dal GPT alla prossima richiesta.",
                parent=self.window,default="no"):
            return
        try:
            self.manager.remove(ident)
            self.reload()
            self.on_change()
        except (AddonError,OSError,ValueError) as exc:
            self._error(exc)

