"""Reference-inspired animated LUMI HUD, lightweight Tkinter edition.

Faithful layout and layered vector artwork without false live telemetry.
Appearance never controls the microphone, GPT, executable tools or documents.
"""
from __future__ import annotations

import ctypes
from collections import deque
from datetime import datetime
import os
import shutil
import time
import tkinter as tk

from network_telemetry import NetworkTelemetry, friendly_rate
from hud_orbits import OrbitMarkers
from slide_modalita import SlideModalita
from hud_reference import (
    AMBER, BG as REF_BG, CYAN as REF_CYAN, GREEN as REF_GREEN,
    LAND, ReactorArt, GlobeArt, projected_earth_point,
    core_mode, core_light, lerp_color,
)

BG = REF_BG
PANEL = "#020b14"
FRAME = "#11506f"
BLUE = "#169ef1"
CYAN = REF_CYAN
TURQUOISE = "#4affdb"
MUTED = "#729bb3"
WHITE = "#d9f5ff"
GREEN = REF_GREEN
TICK_MS = 110


def interpolate_color(first: str, second: str, amount: float) -> str:
    return lerp_color(first, second, amount)


def memory_usage_windows() -> tuple[int, int] | None:
    if os.name != "nt":
        return None

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("avail_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("avail_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("avail_virtual", ctypes.c_ulonglong),
            ("avail_extended", ctypes.c_ulonglong),
        ]

    try:
        status = MemoryStatus()
        status.length = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(
                ctypes.byref(status)):
            return status.total_phys, status.avail_phys
    except (AttributeError, OSError, ValueError):
        return None
    return None


def draw_lumi_wordmark(canvas, color, background, scale=0.62):
    """Disegna «LUMI» (rombo, lettere a linee spesse con taglio, righe sottili)."""
    def p(points):
        return [v*scale for v in points]
    canvas.create_polygon(p([4,24, 13,15, 22,24, 13,33]),outline=color,fill="",width=2)
    thick=max(3,round(7*scale))
    for points in ((44,6, 44,42, 70,42),
                   (88,6, 88,36, 94,42, 112,42, 118,36, 118,6),
                   (138,42, 138,6, 154,28, 170,6, 170,42),
                   (192,6, 192,42)):
        canvas.create_line(*p(points),fill=color,width=thick,capstyle="projecting",
                           joinstyle="miter")
    canvas.create_line(*p([38,24, 198,24]),fill=background,width=2)
    for points in ((40,54, 68,54),(80,54, 196,54),(206,8, 218,8),(201,40, 226,40)):
        canvas.create_line(*p(points),fill=color,width=1)


class WindowsCPU:
    """CPU total-use sampling from the Windows kernel; no psutil install."""

    def __init__(self):
        self.previous = None

    def sample(self) -> float | None:
        if os.name != "nt":
            return None

        class FileTime(ctypes.Structure):
            _fields_ = [("low",ctypes.c_ulong),("high",ctypes.c_ulong)]

        idle, kernel, user = FileTime(), FileTime(), FileTime()
        try:
            ok = ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle),ctypes.byref(kernel),ctypes.byref(user))
            if not ok:
                return None
        except (AttributeError, OSError):
            return None
        def stamp(x):
            return (x.high << 32) | x.low
        current = (stamp(idle),stamp(kernel),stamp(user))
        before = self.previous
        self.previous = current
        if before is None:
            return None
        idle_delta = current[0]-before[0]
        total_delta = (current[1]-before[1])+(current[2]-before[2])
        if total_delta <= 0:
            return None
        return max(0.0,min(100.0,(1.0-idle_delta/total_delta)*100))


def _outline_box(canvas, w, h, color="#124a6e", inset=4, cut=14):
    """Thin angled circuit-border corners reminiscent of the concept image."""
    x=inset
    y=inset
    max_x=max(x+1,w-inset)
    max_y=max(y+1,h-inset)
    coords=(x+cut,y,max_x-cut,y,max_x,y+cut,
            max_x,max_y-cut,max_x-cut,max_y,x+cut,max_y,
            x,max_y-cut,x,y+cut,x+cut,y)
    canvas.create_line(*coords,fill=color,width=1.5)


class MetricTile:
    """Identical-size telemetry cells: parent controls the four-column grid."""
    def __init__(self,parent,label,column):
        self.canvas=tk.Canvas(parent,width=130,height=92,bg="#020b15",
                              highlightthickness=0,bd=0)
        self.canvas.grid(row=0,column=column,sticky="nsew",padx=4)
        self.label=label
        self.value=None
        self.caption="--"
        self.history=deque(maxlen=21)
        self.network_history=deque(maxlen=21)
        self.canvas.bind("<Configure>",self._draw)
        self._draw()

    def update(self,value,caption=""):
        self.value=value
        self.caption=caption
        if self.label=="RETE" and isinstance(value,(tuple,list)):
            rx,tx=value
            self.network_history.append((max(0.0,float(rx)),
                                         max(0.0,float(tx))))
        elif isinstance(value,(int,float)):
            self.history.append(max(0.0,min(100.0,float(value))))
        self._draw()

    def _draw(self,_event=None):
        c=self.canvas
        try:
            c.delete("all")
            w=max(c.winfo_width(),110)
            h=max(c.winfo_height(),64)
            _outline_box(c,w,h,color="#164d70",inset=3,cut=10)
            c.create_text(12,12,anchor="w",text=self.label,
                          font=("Consolas",8,"bold"),fill="#8eb9d0")
            if self.label=="RETE":
                rates=self.value if isinstance(self.value,tuple) else None
                rx,tx=rates if rates else (None,None)
                c.create_text(12,35,anchor="w",text="↓  "+friendly_rate(rx),
                              fill=CYAN,font=("Consolas",9,"bold"))
                c.create_text(12,53,anchor="w",text="↑  "+friendly_rate(tx),
                              fill="#70b5d7",font=("Consolas",9))
                hist=list(self.network_history)
                maximum=max((max(pair) for pair in hist),default=1.0) or 1.0
                bar_width=max(2,(w*.39)/21)
                start=w*.58
                for i,(rx_value,tx_value) in enumerate(hist):
                    x=start+i*bar_width
                    c.create_line(x,h-12,x,h-12-(h*.38*rx_value/maximum),
                                  fill="#28b6ff",width=max(1,bar_width*.6))
                    c.create_line(x,h-12,x,h-12-(h*.25*tx_value/maximum),
                                  fill="#2b7291",width=1)
            else:
                cx,cy=39,h*.61
                r=min(26,h*.30)
                for scale,color,width in (
                        (1.13,"#0a3552",1),(1.00,"#14446d",5),
                        (.80,"#0d3551",1)):
                    rr=r*scale
                    c.create_arc(cx-rr,cy-rr,cx+rr,cy+rr,start=90,
                                 extent=359,outline=color,
                                 width=width,style="arc")
                v=self.value
                if isinstance(v,(int,float)):
                    c.create_arc(cx-r,cy-r,cx+r,cy+r,start=90,
                                 extent=-max(.2,360*v/100),
                                 outline="#20cfff",width=5,style="arc")
                    label=f"{v:.0f}%"
                else:
                    label="--"
                c.create_text(cx,cy,text=label,fill=WHITE,
                              font=("Consolas",11,"bold"))
                bar_start=78
                bar_right=w-9
                bar_w=max(2,(bar_right-bar_start)/23)
                history=list(self.history)
                for i,v in enumerate(history):
                    height=(h-38)*v/100
                    x=bar_start+i*bar_w
                    y=h-10-height
                    c.create_line(x,y,x,h-10,fill="#1a91bd",
                                  width=max(1,bar_w*.57))
            # Fine corner glints are static and cheap to paint.
            c.create_line(3,22,3,9,11,3,35,3,fill="#1ac9fd",width=1)
            c.create_line(w-35,h-3,w-11,h-3,w-3,h-11,w-3,h-22,
                          fill="#145376",width=1)
        except tk.TclError:
            return


class JarvisHUD:
    """Chat left, animated LUMI nucleus center, rotating Earth right."""

    def __init__(self,parent,on_settings):
        self.parent=parent
        self.closed=False
        self.state_provider=lambda:{}
        self.last_tick=time.monotonic()
        self.last_metrics=0.0
        self.phase=0.0
        self._drawn_size=None
        self.core_art=ReactorArt()
        self.earth_art=GlobeArt()
        self._orbit_click=lambda _marker:None
        self._tab="CONSOLE"
        self._console=None
        self._tabs={}
        self._cpu=WindowsCPU()
        self._network=NetworkTelemetry()
        self._last_mode="idle"

        self.frame=tk.Frame(parent,bg=BG)
        self.frame.pack(fill="both",expand=True)

        header=tk.Frame(self.frame,bg=BG,height=54)
        parent._jarvis_window_header = header
        header.pack(fill="x",padx=13,pady=(9,0))
        header_chrome=tk.Canvas(header,bg=BG,highlightthickness=0,bd=0)
        # Created before controls, so header text/buttons paint on top.
        # Canvas.lower() would lower an *item* and fails on Windows Tk.
        header_chrome.place(x=0,y=0,relwidth=1,relheight=1)

        def draw_header(event):
            header_chrome.delete("all")
            w,h=event.width,event.height
            header_chrome.create_line(
                5,h-6,5,14,17,2,240,2,252,13,
                fill="#1485aa",width=1.5)
            header_chrome.create_line(
                270,11,w*.65,11,w*.68,2,w-210,2,
                fill="#0c3d64",width=1)
            header_chrome.create_line(
                w-210,h-6,w-17,h-6,w-4,h-19,
                fill="#0a3b5e",width=1.3)
            for index in range(18):
                x=280+index*19
                if x<w-250:
                    header_chrome.create_line(
                        x,h-4,x+7,h-4,fill="#0b3451")
            for x,y in ((w*.69,11),(w*.79,2),(w-210,2)):
                header_chrome.create_oval(
                    x-1.5,y-1.5,x+1.5,y+1.5,
                    fill="#1d9bc4",outline="")
        header.bind("<Configure>",draw_header)
        # Scritta LUMI disegnata a linee (stile «B» scelto dall'utente il 12/11):
        # rombo, lettere squadrate di tratto medio, taglio orizzontale e righe
        # sottili. Non dipende da caratteri installati sul PC.
        self.wordmark=tk.Canvas(header,width=168,height=40,bg=BG,
                                highlightthickness=0,bd=0)
        self.wordmark.pack(side="left",padx=(5,12))
        draw_lumi_wordmark(self.wordmark,CYAN,BG)
        # 056 B: al posto di «INTERFACCIA NEURALE», slide Basso consumo / Veloce.
        self._mode_handler=None
        self.mode_slide=SlideModalita(
            header,bg=BG,on_change=lambda mode:(self._mode_handler(mode)
                                                if self._mode_handler else True))
        self.mode_slide.pack(side="left")
        self.exit_button=tk.Button(
            header,text="×",command=lambda:None,
            fg=MUTED,bg=BG,activeforeground=WHITE,
            activebackground=BG,font=("Segoe UI",18),
            bd=0,relief="flat",cursor="hand2")
        if self.frame.tk.call("tk", "windowingsystem") != "win32":
            self.exit_button.pack(side="right",padx=(5,4))
        # 055: colonna a destra = pulsanti _ □ X (aggiunti da window_chrome) sopra l'ingranaggio.
        corner=tk.Frame(header,bg=BG)
        corner.pack(side="right")
        parent._jarvis_window_corner=corner
        self.gear=tk.Button(
            corner,text="⚙",command=on_settings,
            fg=CYAN,bg=BG,activeforeground=WHITE,
            activebackground=BG,font=("Segoe UI Symbol",17),
            bd=0,relief="flat",cursor="hand2")
        self.gear.pack(side="top",anchor="e",padx=(8,12))
        parent._jarvis_window_anchor=self.gear     # 055: _ □ X sopra l'ingranaggio
        self.state_text=tk.StringVar(
            value="MIC  OFF    /    GPT  OFF    /    MEMORIA  OFF")
        self._quick_toggle_handlers = {}
        self._quick_state_cache = None
        quick_controls = tk.Frame(header, bg=BG)
        quick_controls.pack(side="right", padx=(0, 12))
        # 056b: ogni voce è un tasto con lo stesso stile (barra_tasti.TastoBarra). «Modello ▾»
        # ha il ⏻ nello stesso tasto; Mic e Memoria sono tasti con ⏻. Online, Ricerca e
        # Telegram si aggiungono con add_quick_button (Online e Ricerca vicini).
        from barra_tasti import TastoBarra
        for key, label, has_menu in (("mic", "Mic", False), ("model", "Modello ▾", True),
                                     ("memory", "Memoria", False)):
            button = TastoBarra(
                quick_controls, label, None, power=True,
                power_command=lambda name=key: self._invoke_quick_toggle(name))
            button.configure(state="disabled")
            button.pack(side="left", padx=(0, 5))
            setattr(self, key + "_toggle_button", button)
        self.quick_controls = quick_controls

        # Reference's full-height console. Fixed min to preserve readability.
        layout=tk.Frame(self.frame,bg=BG)
        layout.pack(fill="both",expand=True,padx=12,pady=(7,5))
        self.left=tk.Frame(layout,bg=PANEL,
                           highlightbackground="#1191c6",
                           highlightthickness=1,width=360)
        self.left.pack(side="left",fill="both",padx=(0,8))
        self.left.pack_propagate(False)
        # A thin luminous edge reproduces the polished panel outline.
        tk.Frame(self.left,bg="#0d668e",width=2).place(
            x=0,y=19,relheight=.89)
        nav=tk.Frame(self.left,bg=PANEL,height=45)
        nav.pack(fill="x",padx=9,pady=(8,4))
        # Un solo livello (15/11): la chat resta qui; attività e messaggi di
        # sistema si aprono quando servono dal pulsantino DIAGNOSTICA.
        tk.Label(nav,text="CHAT",bg=PANEL,fg=CYAN,font=("Consolas",9),
                 padx=9,pady=8).pack(side="left")
        self.diagnostics_button=tk.Button(
            nav,text="DIAGNOSTICA ▸",command=self.open_diagnostics,
            bg=PANEL,fg=MUTED,activeforeground=WHITE,
            activebackground="#0b3650",font=("Consolas",8),
            bd=0,relief="flat",padx=7,pady=6,cursor="hand2")
        self.diagnostics_button.pack(side="right")
        self._diagnostics=None
        tk.Frame(self.left,height=1,bg="#12608a").pack(
            fill="x",padx=11,pady=(0,8))
        self.console_host=tk.Frame(self.left,bg=PANEL)
        self.console_host.pack(fill="both",expand=True,padx=7)
        self.command_host=tk.Frame(self.left,bg=PANEL)
        self.command_host.pack(fill="x",padx=10,pady=(8,9))
        self.chat_info=tk.StringVar(value="Microfono spento")
        tk.Label(self.command_host,textvariable=self.chat_info,
                 bg=PANEL,fg=MUTED,font=("Consolas",8),
                 anchor="w").pack(fill="x",pady=(0,5))

        self.visual=tk.Frame(layout,bg=BG)
        self.visual.pack(side="left",fill="both",expand=True)
        self.main_visuals=tk.Frame(self.visual,bg=BG)
        self.main_visuals.pack(fill="both",expand=True)
        self.main_visuals.grid_rowconfigure(0,weight=1)
        # The reference keeps the reactor dominant but leaves room for a
        # recognizable, fully framed Earth (no clip or flattened disk).
        self.main_visuals.grid_columnconfigure(0,weight=11,minsize=250)
        self.main_visuals.grid_columnconfigure(1,weight=9,minsize=220)
        self.core_canvas=tk.Canvas(
            self.main_visuals,bg=BG,bd=0,
            highlightthickness=0,width=440,height=490)
        self.core_canvas.grid(row=0,column=0,sticky="nsew")
        self.earth_canvas=tk.Canvas(
            self.main_visuals,bg=BG,bd=0,
            highlightthickness=0,width=320,height=490)
        self.earth_canvas.grid(row=0,column=1,sticky="nsew")
        self.core_canvas.bind("<Configure>",self._resize)
        self.earth_canvas.bind("<Configure>",self._resize)
        self.orbit_markers=OrbitMarkers(
            self.core_canvas,lambda ident:self._orbit_click(ident))

        self.visual_status=tk.StringVar(value="LUMI  //  STANDBY")
        self.status_label=tk.Label(self.visual,textvariable=self.visual_status,
                 bg=BG,fg="#60abc5",
                 font=("Consolas",9),pady=3)
        self.status_label.pack(fill="x")

        footer=tk.Frame(self.visual,bg=BG,height=102)
        footer.pack(fill="x",pady=(8,4))     # posizione definitiva: _layout_bottom()
        # Tk pack gave each Canvas a different requested natural width:
        # at narrower sizes DISCO C became visibly smaller than CPU/RAM.
        # A uniform weighted grid guarantees equal panel proportions.
        for column in range(4):
            footer.grid_columnconfigure(column,weight=1,uniform="telemetry")
        footer.grid_rowconfigure(0,weight=1)
        self.footer=footer
        # 056 C2: meteo sotto il globo e sopra DISCO C / RETE, senza riquadro; compare solo con dati.
        self.weather_canvas=tk.Canvas(self.visual,height=34,width=260,bg=BG,
                                      highlightthickness=0,bd=0)
        self._weather=None
        self.cpu_tile=MetricTile(footer,"CPU",0)
        self.ram_tile=MetricTile(footer,"RAM",1)
        self.disk_tile=MetricTile(footer,"DISCO C",2)
        self.network_tile=MetricTile(footer,"RETE",3)
        # Connectivity remains visible in the header and nucleus status card;
        # the fourth telemetry tile shows only real measured traffic.
        # Compatibility with previous public HUD state API.
        self.ram_text=tk.StringVar(value="RAM --")
        self.disk_text=tk.StringVar(value="DISCO C --")
        self.clock_text=tk.StringVar(value="--:--")
        clock_row = tk.Frame(self.visual, bg=BG)
        clock_row.pack(anchor="e", padx=10)   # posizione definitiva: _layout_bottom()
        self.clock_row=clock_row
        self.alarm_stop_button = tk.Button(clock_row, text="⏰ Ferma", bg=BG, fg=CYAN,
                                           activebackground=PANEL, activeforeground=WHITE,
                                           bd=0, highlightthickness=0)
        tk.Label(clock_row, textvariable=self.clock_text, bg=BG, fg=CYAN,
                 font=("Consolas", 11)).pack(side="right")
        self._layout_bottom()
        self._update_metrics()
        self.last_metrics=time.monotonic()
        self.select_tab("CONSOLE")
        self.parent.after(TICK_MS,self._tick)

    def _layout_bottom(self):
        """056b: ora, sveglia, meteo, DISCO C e RETE hanno ciascuno il proprio posto in basso.
        Le parti in basso si impacchettano PRIMA del globo (side=bottom): se manca spazio si
        stringe il globo, mai l'ora o la sveglia (regressione 056: sparivano sotto il meteo)."""
        for widget in (self.clock_row,self.footer,self.weather_canvas,self.status_label,self.main_visuals):
            widget.pack_forget()
        self.clock_row.pack(side="bottom",anchor="e",padx=10)
        self.footer.pack(side="bottom",fill="x",pady=(8,4))
        if self._weather:
            self.weather_canvas.pack(side="bottom",anchor="e",padx=14)
        self.status_label.pack(side="bottom",fill="x")
        self.main_visuals.pack(side="top",fill="both",expand=True)

    def open_diagnostics(self):
        """Finestra separata con tutti i messaggi (Tutto / Attività / Sistema).
        È una copia di sola lettura della console: la chat non cambia."""
        if self._diagnostics is not None:
            try:
                self._diagnostics["window"].deiconify()
                self._diagnostics["window"].lift()
                return
            except tk.TclError:
                self._diagnostics=None
        window=tk.Toplevel(self.parent)
        window.title("Lumi - Diagnostica")
        window.geometry("620x460")
        window.configure(bg=BG)
        bar=tk.Frame(window,bg=PANEL)
        bar.pack(fill="x")
        text=tk.Text(window,bg=PANEL,fg=WHITE,font=("Consolas",9),wrap="word",
                     bd=0,highlightthickness=0,state="disabled")
        text.pack(fill="both",expand=True,padx=6,pady=6)
        state={"window":window,"text":text,"filter":"TUTTO","buttons":{}}
        roles=("utente","jarvis","comando","azione","errore","sistema")
        colors={"utente":CYAN,"jarvis":WHITE,"comando":"#9fe3c8","azione":"#7fe0a0",
                "errore":"#ff7a7a","sistema":MUTED}
        for role in roles:
            text.tag_configure(role,foreground=colors[role])

        def apply(name):
            state["filter"]=name
            visible=(set(roles) if name=="TUTTO" else
                     {"comando","azione","errore"} if name=="ATTIVITÀ" else {"sistema","errore"})
            for role in roles:
                text.tag_configure(role,elide=(role not in visible))
            for key,button in state["buttons"].items():
                button.configure(bg="#0b2c43" if key==name else PANEL,
                                 fg=CYAN if key==name else MUTED)
            text.see("end")

        def refresh():
            if self._diagnostics is not state:
                return
            source=self._console
            try:
                if not window.winfo_exists():
                    return
                end=source.index("end-1c") if source is not None else None
                if source is not None and end!=state.get("end"):
                    # Ricopia solo se la console è cambiata (leggero sull'i3).
                    state["end"]=end
                    dump=source.dump("1.0","end-1c",text=True,tag=True)
                    text.configure(state="normal")
                    text.delete("1.0","end")
                    active=[]
                    for kind,value,_index in dump:
                        if kind=="tagon":
                            active.append(value)
                        elif kind=="tagoff" and value in active:
                            active.remove(value)
                        elif kind=="text":
                            text.insert("end",value,tuple(t for t in active if t in roles))
                    text.configure(state="disabled")
                    apply(state["filter"])
                window.after(2000,refresh)
            except tk.TclError:
                pass

        for name in ("TUTTO","ATTIVITÀ","SISTEMA"):
            button=tk.Button(bar,text=name,command=lambda n=name:apply(n),bg=PANEL,fg=MUTED,
                             activebackground="#0b3650",activeforeground=WHITE,
                             font=("Consolas",9),bd=0,relief="flat",padx=9,pady=7)
            button.pack(side="left")
            state["buttons"][name]=button

        def close():
            self._diagnostics=None
            window.destroy()

        window.protocol("WM_DELETE_WINDOW",close)
        self._diagnostics=state
        refresh()

    def attach_console(self,console):
        """Bind existing history without changing its content or commands."""
        self._console=console
        self.select_tab(self._tab)

    def select_tab(self,tab):
        if tab not in ("CONSOLE","ATTIVITÀ","SISTEMA"):
            return
        self._tab=tab
        for key,button in self._tabs.items():
            chosen=key==tab
            button.configure(
                bg="#0b2c43" if chosen else PANEL,
                fg=CYAN if chosen else MUTED)
        if self._console is None:
            return
        # Tk's elide tags filter existing text in place. Nothing is deleted.
        roles=("utente","jarvis","comando","azione","errore","sistema")
        # 15/11 passo 2a: in chat i messaggi interni («sistema») non si vedono;
        # restano in DIAGNOSTICA.
        visible=(
            set(roles)-{"sistema"} if tab=="CONSOLE" else
            {"comando","azione","errore"} if tab=="ATTIVITÀ" else
            {"sistema","errore"}
        )
        try:
            self._console.configure(state="normal")
            for role in roles:
                self._console.tag_configure(
                    role,elide=(role not in visible))
            self._console.configure(state="disabled")
            self._console.see("end")
        except tk.TclError:
            pass

    def set_state_provider(self,callback):
        self.state_provider=callback

    def set_weather(self, data):
        """data = {"citta", "temp", "categoria"} oppure None (add-on spento: sparisce)."""
        if data==self._weather:
            return
        self._weather=data
        if not data:
            self.weather_canvas.delete("all")
            self.weather_canvas.pack_forget()
            return
        self._draw_weather()
        self._layout_bottom()

    def _draw_weather(self):
        """Icona + città + temperatura + ora (anteprima 057); l'ora segue il tick del clock."""
        data, canvas = self._weather, self.weather_canvas
        canvas.delete("all")
        if not data:
            return
        from meteo.icone import disegna
        disegna(canvas,22,17,data["categoria"],CYAN)
        ora=datetime.now().strftime("%H:%M")
        canvas.create_text(46,17,anchor="w",fill=CYAN,font=("Consolas",10,"bold"),
                           text="%s %d°   %s"%(str(data["citta"])[:16],round(data["temp"]),ora))
        self._weather_ora=ora
        self._layout_bottom()

    def set_mode_handler(self, callback):
        """056 B: callback(modalita) -> bool (True se salvata); la slide scorre solo se salva."""
        self._mode_handler=callback

    def set_quick_toggle_handlers(self, *, microphone, memory, model=None, gpt=None):
        """Bind trusted existing controls; this HUD owns no setting state."""
        handlers = {"mic": microphone, "memory": memory}
        if model is not None:
            handlers["model"] = model
        if not all(callable(callback) for callback in handlers.values()):
            raise TypeError("Quick controls require callable handlers.")
        self._quick_toggle_handlers = handlers
        for key in handlers:
            getattr(self, key + "_toggle_button").configure(state="normal")

    def add_quick_button(self, key, text, command, *, after=None, power=False, simbolo=None):
        """Tasto in più nella fila in alto (Online ▾, Ricerca ▾, Telegram), dopo `after`."""
        from barra_tasti import TastoBarra
        anchor = None
        if after:
            anchor = (getattr(self, after + "_toggle_button", None)
                      or getattr(self, after + "_extra_button", None))
        button = TastoBarra(self.quick_controls, text, command, power=power, simbolo=simbolo)
        if anchor is not None:
            button.pack(side="left", padx=(0, 5), after=anchor)
        else:
            button.pack(side="left", padx=(0, 5))
        setattr(self, key + "_extra_button", button)
        return button

    def _invoke_quick_toggle(self, name):
        callback = self._quick_toggle_handlers.get(name)
        if callback is not None:
            callback()

    def set_orbit_open_handler(self,callback):
        """Open a known project or Telegram activity by its trusted ID."""
        self._orbit_click=callback

    def set_alarm_active(self, active):
        if active:
            self.alarm_stop_button.pack(side="right", padx=(6, 0))
        else:
            self.alarm_stop_button.pack_forget()

    def set_close_handler(self,callback):
        self.exit_button.configure(command=callback)

    def _resize(self,_event=None):
        self._drawn_size=None

    def _update_metrics(self):
        cpu=self._cpu.sample()
        self.cpu_tile.update(cpu)
        memory=memory_usage_windows()
        if memory:
            total,free=memory
            pct=100*(1-free/total) if total else None
            self.ram_tile.update(pct)
            self.ram_text.set(
                f"RAM {pct:.0f}%" if pct is not None else "RAM --")
        else:
            self.ram_tile.update(None)
            self.ram_text.set("RAM --")
        if os.name=="nt":
            try:
                drive=os.environ.get("SystemDrive","C:")+"\\"
                disk=shutil.disk_usage(drive)
                pct=100*disk.used/disk.total if disk.total else None
                self.disk_tile.update(pct)
                self.disk_text.set(
                    f"DISCO C {pct:.0f}%" if pct is not None else "DISCO C --")
            except (OSError,ValueError):
                self.disk_tile.update(None)
                self.disk_text.set("DISCO C --")
        else:
            self.disk_tile.update(None)
            self.disk_text.set("DISCO C --")
        self.clock_text.set(datetime.now().strftime("%H:%M"))
        if self._weather and getattr(self,"_weather_ora","")!=self.clock_text.get():
            self._draw_weather()
        # Slow, read-only network polling occurs off the UI thread.
        measured=self._network.result()
        self.network_tile.update(measured)
        self._network.request()

    def _tick(self):
        if self.closed:
            return
        try:
            self._advance()
        except (tk.TclError,ValueError,TypeError,OSError):
            # A decorative error cannot interrupt voice or file operations.
            pass
        if not self.closed:
            self.parent.after(TICK_MS,self._tick)

    def _advance(self):
        now=time.monotonic()
        elapsed=min(max(now-self.last_tick,0.0),.25)
        self.last_tick=now
        if now-self.last_metrics>5:
            self._update_metrics()
            self.last_metrics=now
        state=self.state_provider() or {}
        speaking=bool(state.get("speaking",False))
        listening=bool(state.get("listening",False))
        thinking=bool(state.get("thinking",False))
        reasoning=bool(state.get("reasoning",False))
        searching=bool(state.get("searching",False))
        connected=bool(state.get("connected",False))
        memory=bool(state.get("memory",False))
        mic_enabled=bool(state.get("mic_enabled",listening))
        mode=core_mode(speaking=speaking,listening=listening)
        self._last_mode=mode
        title=(
            f"MIC  {'ATTIVO' if mic_enabled else 'OFF'}    /    "
            f"GPT  {'ON' if connected else 'OFF'}    /    "
            f"MEMORIA  {'ON' if memory else 'OFF'}")
        status=("LUMI // TRASMISSIONE VOCALE" if speaking else
                "LUMI // VOCE RILEVATA" if listening else
                "LUMI // STA RAGIONANDO" if reasoning else
                "LUMI // RICERCA SUL PC" if searching else
                "LUMI // ELABORAZIONE" if thinking else
                "LUMI // MICROFONO ATTIVO - IN ATTESA" if mic_enabled else
                "LUMI // STANDBY")
        info=("LUMI STA PARLANDO" if speaking else
              "LA TUA VOCE È RILEVATA" if listening else
              "LUMI STA RAGIONANDO" if reasoning else
              "RICERCA SUL PC IN CORSO" if searching else
              "ELABORAZIONE IN CORSO" if thinking else
              "MICROFONO ATTIVO  •  ATTESA VOCE" if mic_enabled else
              "MICROFONO SPENTO  •  CONTROLLO MANUALE")
        if self.state_text.get()!=title:
            self.state_text.set(title)
        mic_selected = bool(state.get("mic_selected", mic_enabled))
        gpt_enabled = bool(state.get("gpt_enabled", connected))
        mic_label = "Mic"      # 057: come l'anteprima; lo stato lo dà il ⏻ (azzurro/arancione)
        from model_gate import enabled as model_enabled
        model_on = bool(state.get("model_enabled", model_enabled()))
        controls = (("mic", mic_label, mic_enabled or mic_selected),
                    ("model", None, model_on),
                    ("memory", "Memoria", memory))
        if controls != self._quick_state_cache:
            for key, label, enabled in controls:
                button = getattr(self, key + "_toggle_button")
                if label is None:
                    button.configure(power_on=enabled)
                else:
                    button.configure(text=label, power_on=enabled)
            self._quick_state_cache = controls
        if state.get("modalita") in ("basso_consumo","veloce"):
            self.mode_slide.imposta(state["modalita"])
        if self.visual_status.get()!=status:
            self.visual_status.set(status)
        if self.chat_info.get()!=info:
            self.chat_info.set(info)
        if not self.parent.winfo_viewable():
            return
        size=(self.core_canvas.winfo_width(),
              self.core_canvas.winfo_height(),
              self.earth_canvas.winfo_width(),
              self.earth_canvas.winfo_height())
        if size!=self._drawn_size:
            self.core_art.build(self.core_canvas)
            self.earth_art.build(self.earth_canvas)
            self.orbit_markers.reset()
            self._drawn_size=size
        self.phase+=elapsed
        self.core_art.tick(self.phase,mode,connected=connected,
                           memory=memory,listening=mic_enabled)
        self.earth_art.tick(self.phase)
        cx,cy,r=self.core_art.geometry
        self.orbit_markers.update(
            state.get("orbit_nodes",()),cx,cy,r,self.phase)

    def close(self):
        self.closed=True
