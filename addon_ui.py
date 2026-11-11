"""Optional on-demand Tk control panel for the trusted Lumi addon manager.

No network, no script execution, no automatic enable after install or update.
All changes are local and explicit; failures are visible to the user.
"""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from addon_manager import AddonError, AddonManager


_DESCRIPTIONS_CONFIG = {"musica", "programmi_app", "accesso_file", "controllo_pc"}


class AddonSettingsWindow:
    """Elenco degli add-on a sinistra; clic su uno: la sua sezione a destra
    (stato, Attiva/Disattiva, Configura, i suoi comandi personalizzabili)."""

    def __init__(self, parent, manager: AddonManager, on_change=None, engine=None,
                 section_builders=None):
        self.manager=manager
        self.engine=engine
        # Sezioni costruite da Lumi (es. Telegram, che usa lo stato del programma).
        self.section_builders=dict(section_builders or {})
        self.on_change=on_change or (lambda:None)
        self.window=tk.Toplevel(parent)
        self.window.title("LUMI // Gestisci add-on")
        self.window.geometry("980x640")
        self.window.minsize(760,480)
        holder=ttk.Frame(self.window,padding=12)
        holder.pack(fill="both",expand=True)
        ttk.Label(holder,text="Add-on di Lumi",
                  font=("Segoe UI",13,"bold")).pack(anchor="w")
        ttk.Label(holder,wraplength=940,
                  text=("Scegli un add-on a sinistra per vederne stato, configurazione e "
                        "comandi. Ogni nuova installazione o aggiornamento resta SPENTO.")).pack(
                            fill="x",pady=(4,8))
        bottom=ttk.Frame(holder)
        bottom.pack(side="bottom",fill="x",pady=(8,0))
        ttk.Button(bottom,text="Installa / aggiorna...",
                   command=self.install).pack(side="left",padx=(0,6))
        ttk.Button(bottom,text="Ricarica",command=self.reload).pack(side="left")
        ttk.Button(bottom,text="Installa componenti...",
                   command=self.open_components).pack(side="left",padx=(6,0))
        ttk.Button(bottom,text="Chiudi",command=self.window.destroy).pack(side="right")
        self.status=tk.StringVar(value="")
        ttk.Label(holder,textvariable=self.status,wraplength=940).pack(
            side="bottom",anchor="w",pady=(6,0))
        body=ttk.Frame(holder)
        body.pack(fill="both",expand=True)
        self.table=ttk.Treeview(body,columns=("name","enabled"),show="headings",
                                selectmode="browse",height=14)
        self.table.heading("name",text="Add-on")
        self.table.heading("enabled",text="Stato")
        self.table.column("name",width=190,stretch=False)
        self.table.column("enabled",width=75,stretch=False)
        self.table.pack(side="left",fill="y")
        self.table.bind("<<TreeviewSelect>>",lambda _e:self.show_section())
        outer=ttk.Frame(body,padding=(12,0,0,0))
        outer.pack(side="left",fill="both",expand=True)
        self.section_canvas=tk.Canvas(outer,highlightthickness=0)
        scroll=ttk.Scrollbar(outer,orient="vertical",command=self.section_canvas.yview)
        self.section_canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right",fill="y")
        self.section_canvas.pack(side="left",fill="both",expand=True)
        self.section=ttk.Frame(self.section_canvas)
        window_id=self.section_canvas.create_window(0,0,window=self.section,anchor="nw")
        self.section.bind("<Configure>",lambda _e:self.section_canvas.configure(
            scrollregion=self.section_canvas.bbox("all")))
        self.section_canvas.bind("<Configure>",lambda e:self.section_canvas.itemconfigure(
            window_id,width=e.width))
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
            keep=self._selected()
            self.manager.refresh()
            for ident in self.table.get_children():
                self.table.delete(ident)
            installed=self.manager.list_installed()
            for item in installed:
                self.table.insert("", "end", iid=item["id"],values=(
                    item["name"],"ATTIVO" if item["enabled"] else "SPENTO"))
            warnings=self.manager.warnings()
            self.status.set(
                str(len(installed))+" add-on installati. "
                +(str(len(warnings))+" file non validi ignorati." if warnings
                  else "Modifiche sincronizzate al prossimo comando GPT."))
            if keep and self.table.exists(keep):
                self.table.selection_set(keep)
            elif installed:
                self.table.selection_set(installed[0]["id"])
            self.show_section()
        except (AddonError,OSError,ValueError) as exc:
            self._error(exc)

    def open_components(self):
        try:
            from componenti.ui import ComponentsWindow
            ComponentsWindow(self.window,on_close=lambda: self.exists() and self.show_section())
        except (ImportError,tk.TclError) as exc:
            self._error("Installazione componenti non disponibile: "+str(exc)[:100])

    def show_section(self):
        """Sezione dell'add-on scelto: descrizione, stato, azioni, comandi."""
        for child in self.section.winfo_children():
            child.destroy()
        ident=self._selected()
        item=next((c for c in self.manager.list_installed() if c["id"]==ident),None)
        if item is None:
            ttk.Label(self.section,text="Scegli un add-on dall'elenco.").pack(anchor="w")
            return
        ttk.Label(self.section,text=item["name"]+"  "+item["version"],
                  font=("Segoe UI",12,"bold")).pack(anchor="w")
        description=str(item.get("description",""))
        if description:
            ttk.Label(self.section,text=description,wraplength=640).pack(anchor="w",pady=(2,4))
        ttk.Label(self.section,text=("ATTIVO" if item["enabled"] else "SPENTO")+
                  " · "+str(item["action_count"])+" funzioni").pack(anchor="w")
        row=ttk.Frame(self.section)
        row.pack(fill="x",pady=(6,8))
        ttk.Button(row,text="Disattiva" if item["enabled"] else "Attiva",
                   command=self.toggle).pack(side="left",padx=(0,6))
        if ident in _DESCRIPTIONS_CONFIG:
            ttk.Button(row,text="Configura...",command=self.configure).pack(side="left",padx=(0,6))
        ttk.Button(row,text="Rimuovi",command=self.remove).pack(side="left")
        builder=self.section_builders.get(ident)
        if builder is not None:
            try:
                builder(self.section)
            except tk.TclError as exc:
                ttk.Label(self.section,text="Sezione non disponibile: "+str(exc)[:80]).pack(anchor="w")
        try:
            from componenti import catalog
            if catalog.for_addon(ident) or catalog.keys_for_addon(ident):
                ttk.Label(self.section,text="Cosa serve installare e chiavi",
                          font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(6,0))
                from componenti.ui import RequirementsPanel
                RequirementsPanel(self.section,ident).pack(fill="x")
        except ImportError as exc:
            ttk.Label(self.section,text="Requisiti non disponibili: "+str(exc)[:80]).pack(anchor="w")
        try:
            import command_aliases
            section=command_aliases.ADDON_SECTIONS.get(ident)
            if section:
                ttk.Label(self.section,text="Comandi di "+item["name"],
                          font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(4,0))
                from command_words_ui import AliasPanel
                AliasPanel(self.section,section,self.engine,height=260).pack(
                    fill="both",expand=True)
        except (ImportError,tk.TclError) as exc:
            ttk.Label(self.section,text="Comandi non disponibili: "+str(exc)[:80]).pack(anchor="w")

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
        if self._selected() == 'controllo_pc':
            service = getattr(self.manager, 'pc_service', None)
            if service is None:
                self._error('Controllo PC non disponibile: reinstalla la cartella controllo_pc dal pacchetto completo.')
                return
            try:
                from controllo_pc.ui import ControlSettings
                ControlSettings(self.window, service, on_change=self.on_change)
            except (ImportError, OSError, ValueError) as exc:
                self._error('Controllo PC non disponibile: ' + str(exc)[:120])
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

