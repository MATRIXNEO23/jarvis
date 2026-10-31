"""Small standalone Tk digital countdown popup, unrelated to Jarvis HUD layout.

All widget operations occur on Tk's main thread; countdown uses monotonic time.
"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from timer_core import Countdown, MAX_TIMER_SECONDS, format_remaining

BG="#010915"
PANEL="#041525"
CYAN="#22d9ff"
MUTED="#779db2"
TEXT="#dcf7ff"


class TimerPopup:
    def __init__(self,root,alarm_player,alarm_settings):
        self.root=root
        self.alarm=alarm_player
        self.alarm_settings=alarm_settings
        self.model=Countdown(300)
        self.window=None
        self._job=None

    def _ui(self):
        if self.window is not None:
            return
        win=tk.Toplevel(self.root)
        self.window=win
        win.title("JARVIS // TIMER")
        win.configure(bg=BG)
        win.geometry("414x252")
        win.resizable(False,False)
        win.protocol("WM_DELETE_WINDOW",self.close)
        shell=tk.Frame(win,bg=PANEL,highlightbackground="#135472",
                       highlightthickness=1,padx=14,pady=10)
        shell.pack(fill="both",expand=True,padx=7,pady=7)
        tk.Label(shell,text="◈  TIMER   /   CONTO ALLA ROVESCIA",
                 bg=PANEL,fg=MUTED,font=("Consolas",9,"bold")).pack(
                     anchor="w",pady=(0,6))
        self.display=tk.StringVar(value=format_remaining(self.model.remaining()))
        tk.Label(shell,textvariable=self.display,bg=PANEL,fg=CYAN,
                 font=("Consolas",46,"bold"),anchor="center").pack(
                     fill="x",pady=(1,2))
        self.status=tk.StringVar(value="PRONTO")
        tk.Label(shell,textvariable=self.status,bg=PANEL,fg="#76b5cd",
                 font=("Consolas",8)).pack(pady=(0,5))
        controls=tk.Frame(shell,bg=PANEL)
        controls.pack(fill="x")
        self.buttons={}
        for index,(name,command) in enumerate((
                ("START",self.start),("PAUSA",self.pause),
                ("STOP",self.stop),("RESET",self.reset))):
            btn=tk.Button(controls,text=name,command=command,
                    bg="#0b3048" if index==0 else "#061e31",
                    fg=CYAN if index==0 else TEXT,
                    activebackground="#175070",activeforeground="#ffffff",
                    bd=0,relief="flat",font=("Consolas",9,"bold"),
                    cursor="hand2",pady=6)
            btn.grid(row=0,column=index,sticky="nsew",padx=3)
            controls.grid_columnconfigure(index,weight=1,uniform="buttons")
            self.buttons[name]=btn
        entry_row=tk.Frame(shell,bg=PANEL)
        entry_row.pack(fill="x",pady=(9,0))
        tk.Label(entry_row,text="IMPOSTA  ",bg=PANEL,fg=MUTED,
                 font=("Consolas",9)).pack(side="left")
        self.hours=tk.StringVar(value="00")
        self.minutes=tk.StringVar(value="05")
        self.seconds=tk.StringVar(value="00")
        for label,variable,maximum in (
                ("H",self.hours,23),("M",self.minutes,59),
                ("S",self.seconds,59)):
            tk.Label(entry_row,text=label,bg=PANEL,fg="#73bfd9",
                     font=("Consolas",8)).pack(side="left",padx=(3,2))
            sp=tk.Spinbox(entry_row,from_=0,to=maximum,width=3,
                          textvariable=variable,format="%02.0f",
                          bg="#071e30",fg=TEXT,buttonbackground="#10354d",
                          insertbackground=TEXT,highlightthickness=0,
                          relief="flat",font=("Consolas",10),
                          justify="center")
            sp.pack(side="left",padx=(0,6))
        self._render()

    def _input_duration(self):
        try:
            values=(int(self.hours.get()),int(self.minutes.get()),
                    int(self.seconds.get()))
        except (TypeError,ValueError):
            return None
        h,m,s=values
        seconds=h*3600+m*60+s
        if not (0<=h<=23 and 0<=m<=59 and 0<=s<=59
                and 1<=seconds<=MAX_TIMER_SECONDS):
            return None
        return seconds

    def _set_inputs(self,seconds):
        h,r=divmod(seconds,3600)
        m,s=divmod(r,60)
        self.hours.set(f"{h:02d}")
        self.minutes.set(f"{m:02d}")
        self.seconds.set(f"{s:02d}")

    def open(self,seconds: int | None = None,*,autostart=False):
        self._ui()
        if seconds is not None:
            self.model.set_duration(seconds)
            self._set_inputs(seconds)
            self.alarm.stop()
            if autostart:
                self.model.start()
        if self.window is None:
            return
        self.window.deiconify()
        self.window.lift()
        self._render()
        if self._job is None:
            self._tick()

    def _render(self):
        if self.window is None:
            return
        self.display.set(format_remaining(self.model.remaining()))
        label={"running":"IN CORSO","paused":"IN PAUSA",
               "stopped":"PRONTO","finished":"TEMPO SCADUTO"}
        self.status.set(label[self.model.state])
        self.buttons["START"].configure(
            state="disabled" if self.model.state=="running" else "normal")
        self.buttons["PAUSA"].configure(
            state="normal" if self.model.state=="running" else "disabled")

    def _tick(self):
        if self.window is None:
            return
        self._job=None
        if self.model.check_finished():
            name,volume,repeat=self.alarm_settings()
            self.alarm.play(name,volume,repeat=repeat)
        self._render()
        self._job=self.window.after(100,self._tick)

    def start(self):
        self._ui()
        if self.model.state in ("stopped","finished"):
            duration=self._input_duration()
            if duration is None:
                self.status.set("DURATA NON VALIDA")
                return
            self.model.set_duration(duration)
        self.alarm.stop()
        self.model.start()
        self._render()

    def pause(self):
        if self.model.pause():
            self._render()

    def stop(self):
        self.alarm.stop()
        self.model.stop()
        self._render()

    def reset(self):
        self.alarm.stop()
        duration=self._input_duration()
        if duration is None:
            if self.window is not None:
                self.status.set("DURATA NON VALIDA")
            return
        self.model.set_duration(duration)
        self._render()

    def action(self,action:str):
        if action in ("resume","start"):
            self.open()
            self.start()
        elif action=="pause":
            self.pause()
            self.open()
        elif action=="stop":
            self.stop()
            self.open()
        elif action=="reset":
            self.reset()
            self.open()
        elif action=="open":
            self.open()

    def close(self):
        self.alarm.stop()
        self.model.stop()
        window=self.window
        self.window=None
        if window is not None:
            if self._job is not None:
                try:
                    window.after_cancel(self._job)
                except tk.TclError:
                    pass
                self._job=None
            window.destroy()
