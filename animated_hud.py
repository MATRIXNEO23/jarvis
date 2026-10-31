"""Reference-inspired animated JARVIS HUD, lightweight Tkinter edition.

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

from hud_reference import (
    AMBER, BG as REF_BG, CYAN as REF_CYAN, GREEN as REF_GREEN,
    LAND, ReactorArt, GlobeArt, projected_earth_point,
    core_mode, core_light, lerp_color,
)

BG = REF_BG
PANEL = "#031321"
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
    def __init__(self,parent,label):
        self.canvas=tk.Canvas(parent,height=82,bg="#031424",
                              highlightthickness=1,
                              highlightbackground="#104968",bd=0)
        self.canvas.pack(side="left",fill="both",expand=True,padx=4)
        self.label=label
        self.value=None
        self.history=deque(maxlen=21)
        self.canvas.bind("<Configure>",self._draw)
        self._draw()

    def update(self,value,caption=""):
        self.value=value
        self.caption=caption
        if isinstance(value,(int,float)):
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
            cx,cy=39,h*.62
            r=min(26,h*.31)
            c.create_arc(cx-r,cy-r,cx+r,cy+r,start=90,extent=359,
                         outline="#13314b",width=5,style="arc")
            v=self.value
            if isinstance(v,(int,float)):
                c.create_arc(cx-r,cy-r,cx+r,cy+r,start=90,
                             extent=-max(0.2,360*v/100),
                             outline=CYAN,width=5,style="arc")
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
                c.create_line(x,y,x,h-10,fill="#16658a",
                              width=max(1,bar_w*.5))
            if not history and self.label=="GPT":
                c.create_text(w-12,h*.64,anchor="e",
                              text=getattr(self,"caption","OFF"),
                              fill=MUTED,font=("Consolas",8))
        except tk.TclError:
            return


class JarvisHUD:
    """Chat left, animated JARVIS nucleus center, rotating Earth right."""

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
        self._tab="CONSOLE"
        self._console=None
        self._tabs={}
        self._cpu=WindowsCPU()
        self._last_mode="idle"

        self.frame=tk.Frame(parent,bg=BG)
        self.frame.pack(fill="both",expand=True)

        header=tk.Frame(self.frame,bg=BG,height=54)
        header.pack(fill="x",padx=13,pady=(9,0))
        tk.Label(header,text="◈  J A R V I S",
                 bg=BG,fg=CYAN,
                 font=("Segoe UI",15,"bold")).pack(
                     side="left",padx=(5,12))
        tk.Label(header,text="//  INTERFACCIA NEURALE",
                 bg=BG,fg="#4985a7",
                 font=("Consolas",9)).pack(side="left")
        self.exit_button=tk.Button(
            header,text="×",command=lambda:None,
            fg=MUTED,bg=BG,activeforeground=WHITE,
            activebackground=BG,font=("Segoe UI",18),
            bd=0,relief="flat",cursor="hand2")
        self.exit_button.pack(side="right",padx=(5,4))
        self.gear=tk.Button(
            header,text="⚙",command=on_settings,
            fg=CYAN,bg=BG,activeforeground=WHITE,
            activebackground=BG,font=("Segoe UI Symbol",21),
            bd=0,relief="flat",cursor="hand2")
        self.gear.pack(side="right",padx=(8,12))
        self.state_text=tk.StringVar(
            value="MIC  OFF    /    GPT  OFF    /    MEMORIA  OFF")
        tk.Label(header,textvariable=self.state_text,
                 bg=BG,fg="#8ab5ca",
                 font=("Consolas",9)).pack(side="right",padx=(0,12))

        # Reference's full-height console. Fixed min to preserve readability.
        layout=tk.Frame(self.frame,bg=BG)
        layout.pack(fill="both",expand=True,padx=12,pady=(7,5))
        self.left=tk.Frame(layout,bg=PANEL,
                           highlightbackground=FRAME,
                           highlightthickness=1,width=360)
        self.left.pack(side="left",fill="both",padx=(0,8))
        self.left.pack_propagate(False)
        nav=tk.Frame(self.left,bg=PANEL,height=45)
        nav.pack(fill="x",padx=9,pady=(8,4))
        for name in ("CONSOLE","ATTIVITÀ","SISTEMA"):
            button=tk.Button(
                nav,text=name,command=lambda tab=name:self.select_tab(tab),
                bg=PANEL,fg=MUTED,activeforeground=WHITE,
                activebackground="#0b3650",font=("Consolas",9),
                bd=0,relief="flat",padx=9,pady=8,cursor="hand2")
            button.pack(side="left",fill="x",expand=True)
            self._tabs[name]=button
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
        self.main_visuals.grid_columnconfigure(0,weight=11)
        self.main_visuals.grid_columnconfigure(1,weight=9)
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

        self.visual_status=tk.StringVar(value="JARVIS  //  STANDBY")
        tk.Label(self.visual,textvariable=self.visual_status,
                 bg=BG,fg="#60abc5",
                 font=("Consolas",9),pady=3).pack(fill="x")

        footer=tk.Frame(self.visual,bg=BG,height=90)
        footer.pack(fill="x",pady=(7,3))
        self.cpu_tile=MetricTile(footer,"CPU")
        self.ram_tile=MetricTile(footer,"RAM")
        self.disk_tile=MetricTile(footer,"DISCO C")
        self.gpt_tile=MetricTile(footer,"GPT")
        # Compatibility with previous public HUD state API.
        self.ram_text=tk.StringVar(value="RAM --")
        self.disk_text=tk.StringVar(value="DISCO C --")
        self.clock_text=tk.StringVar(value="--:--")
        self._update_metrics()
        self.last_metrics=time.monotonic()
        self.select_tab("CONSOLE")
        self.parent.after(TICK_MS,self._tick)

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
        roles=("utente","jarvis","azione","errore","sistema")
        visible=(
            set(roles) if tab=="CONSOLE" else
            {"azione","errore"} if tab=="ATTIVITÀ" else
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
        connected=bool(state.get("connected",False))
        memory=bool(state.get("memory",False))
        mic_enabled=bool(state.get("mic_enabled",listening))
        mode=core_mode(speaking=speaking,listening=listening)
        title=(
            f"MIC  {'ATTIVO' if mic_enabled else 'OFF'}    /    "
            f"GPT  {'ON' if connected else 'OFF'}    /    "
            f"MEMORIA  {'ON' if memory else 'OFF'}")
        status=("JARVIS // TRASMISSIONE VOCALE" if speaking else
                "JARVIS // VOCE RILEVATA" if listening else
                "JARVIS // ELABORAZIONE" if thinking else
                "JARVIS // MICROFONO ATTIVO - IN ATTESA" if mic_enabled else
                "JARVIS // STANDBY")
        info=("JARVIS STA PARLANDO" if speaking else
              "LA TUA VOCE È RILEVATA" if listening else
              "ELABORAZIONE IN CORSO" if thinking else
              "MICROFONO ATTIVO  •  ATTESA VOCE" if mic_enabled else
              "MICROFONO SPENTO  •  CONTROLLO MANUALE")
        if self.state_text.get()!=title:
            self.state_text.set(title)
        if self.visual_status.get()!=status:
            self.visual_status.set(status)
        if self.chat_info.get()!=info:
            self.chat_info.set(info)
        # Connection status is event-like, not a sampled percentage:
        # update its tile only when the value changes.
        desired_gpt = 100 if connected else 0
        if self.gpt_tile.value != desired_gpt:
            self.gpt_tile.update(
                desired_gpt, "ONLINE" if connected else "OFFLINE")
        if not self.parent.winfo_viewable():
            return
        size=(self.core_canvas.winfo_width(),
              self.core_canvas.winfo_height(),
              self.earth_canvas.winfo_width(),
              self.earth_canvas.winfo_height())
        if size!=self._drawn_size:
            self.core_art.build(self.core_canvas)
            self.earth_art.build(self.earth_canvas)
            self._drawn_size=size
        self.phase+=elapsed
        self.core_art.tick(self.phase,mode,connected=connected,
                           memory=memory,listening=mic_enabled)
        self.earth_art.tick(self.phase)

    def close(self):
        self.closed=True
