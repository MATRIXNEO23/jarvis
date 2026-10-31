"""Lightweight animated Jarvis HUD for Tkinter on older Windows hardware.

Pure Python + standard Tk widgets. No videos, browser engine, GPU, extra
packages, audio capturing or network requests. Animation is decorative and
never changes listening, GPT, saving or document state.
"""
from __future__ import annotations

import ctypes
import math
import os
import shutil
import time
import tkinter as tk
from datetime import datetime

BG = "#020b13"
PANEL = "#051723"
FRAME = "#0b526a"
BLUE = "#18a9ff"
CYAN = "#20d7ff"
TURQUOISE = "#48ffe0"
MUTED = "#74a5bc"
WHITE = "#d8f6ff"
GREEN = "#39edb0"
AMBER = "#f4bf69"
TICK_MS = 110


def interpolate_color(first: str, second: str, amount: float) -> str:
    """Fade the core between blue and teal without abrupt color changes."""
    amount = min(1.0, max(0.0, float(amount)))
    aa = [int(first[i:i+2], 16) for i in (1, 3, 5)]
    bb = [int(second[i:i+2], 16) for i in (1, 3, 5)]
    result = [round(a + (b - a) * amount) for a, b in zip(aa, bb)]
    return "#" + "".join(f"{ch:02x}" for ch in result)


def projected_earth_point(lat: float, lon: float, turn: float, radius: float):
    """Orthographic front-hemisphere projection; None when behind globe."""
    latitude = math.radians(lat)
    longitude = math.radians(lon) + turn
    depth = math.cos(latitude) * math.cos(longitude)
    if depth < 0:
        return None
    return (radius * math.cos(latitude) * math.sin(longitude),
            -radius * math.sin(latitude))


def _continents():
    # Approximate decorative dots, not a cartographic or location source.
    # These modest samples form recognizable Africa/Europe/Asia/Americas.
    areas = [
        [(-17, 35), (2, 37), (14, 32), (30, 31), (36, 11),
         (43, 12), (31, -8), (21, -35), (10, -32), (-4, -20),
         (-16, 6), (-17, 35)],
        [(-10, 36), (-9, 43), (1, 43), (7, 54), (19, 59),
         (29, 64), (39, 57), (30, 43), (18, 40), (11, 36), (-10, 36)],
        [(30, 37), (42, 46), (64, 50), (82, 55), (102, 62),
         (131, 53), (143, 42), (125, 22), (109, 4), (95, 7),
         (83, 9), (74, 22), (58, 24), (43, 11), (30, 37)],
        [(-169, 62), (-133, 65), (-123, 50), (-119, 33),
         (-105, 25), (-96, 16), (-85, 11), (-81, 24),
         (-69, 43), (-60, 50), (-89, 59), (-114, 72), (-169, 62)],
        [(-81, 11), (-68, 13), (-52, 6), (-36, -5),
         (-46, -24), (-57, -36), (-72, -55), (-77, -31),
         (-81, 11)],
        [(113, -11), (134, -11), (151, -24), (142, -39),
         (116, -35), (113, -11)],
    ]
    points = []
    for poly in areas:
        for (lon1, lat1), (lon2, lat2) in zip(poly[:-1], poly[1:]):
            distance = max(abs(lon2-lon1), abs(lat2-lat1))
            steps = max(2, int(distance / 3))
            for i in range(steps):
                fraction = i / steps
                points.append((lat1+(lat2-lat1)*fraction,
                               lon1+(lon2-lon1)*fraction))
    return tuple(points)


LAND = _continents()


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
        info = MemoryStatus()
        info.length = ctypes.sizeof(MemoryStatus)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(info)):
            return info.total_phys, info.avail_phys
    except (AttributeError, OSError, ValueError):
        return None
    return None


class JarvisHUD:
    """Main app shell. Settings and actual actions remain in existing Tk code."""

    def __init__(self, parent: tk.Tk, on_settings):
        self.parent = parent
        self.closed = False
        self.frame = tk.Frame(parent, bg=BG)
        self.frame.pack(fill="both", expand=True)
        self.state_provider = lambda: {}
        self.last_state = {}
        self.speech_color_amount = 0.0
        self.phase = 0.0
        self.last_metrics = 0.0
        self.last_tick = time.monotonic()
        self._land_items = []
        self._core_items = []
        self._earth_items = []
        self._rings = []
        self._drawn_size = None
        self._font = ("Segoe UI", 10)

        header = tk.Frame(self.frame, bg=BG, height=68,
                          highlightbackground=FRAME, highlightthickness=1)
        header.pack(fill="x", padx=13, pady=(12, 6))
        tk.Label(header, text="◈  J A R V I S   //   ASSISTENTE",
                 font=("Segoe UI", 16, "bold"), bg=BG,
                 fg=CYAN).pack(side="left", padx=(18, 8), pady=15)
        self.exit_button = tk.Button(
            header, text="×", command=lambda: None,
            fg=MUTED, bg=BG, activebackground=PANEL,
            activeforeground=WHITE, relief="flat",
            font=("Segoe UI", 19), cursor="hand2", bd=0)
        self.exit_button.pack(side="right", padx=(0, 8))
        self.gear = tk.Button(
            header, text="⚙", command=on_settings,
            fg=CYAN, bg=BG, activebackground=PANEL,
            activeforeground=TURQUOISE, relief="flat",
            font=("Segoe UI Symbol", 22), cursor="hand2", bd=0,
            highlightthickness=0)
        self.gear.pack(side="right", padx=(0, 10))
        self.state_text = tk.StringVar(
            value="MIC  SPENTO    •    GPT  NON CONNESSO")
        tk.Label(header, textvariable=self.state_text,
                 font=("Consolas", 10), bg=BG, fg=MUTED).pack(
            side="right", padx=(10, 25))

        area = tk.Frame(self.frame, bg=BG)
        area.pack(fill="both", expand=True, padx=13, pady=(5, 8))
        self.left = tk.Frame(
            area, bg=PANEL, highlightbackground=FRAME,
            highlightthickness=1, width=380)
        self.left.pack(side="left", fill="both", padx=(0, 8))
        self.left.pack_propagate(False)
        tk.Label(self.left, text="   CONSOLE  //  CONVERSAZIONE",
                 bg=PANEL, fg=CYAN, font=("Consolas", 11, "bold"),
                 anchor="w").pack(fill="x", pady=(14, 8))

        self.console_host = tk.Frame(self.left, bg=PANEL)
        self.console_host.pack(fill="both", expand=True, padx=9)

        self.command_host = tk.Frame(self.left, bg=PANEL)
        self.command_host.pack(fill="x", padx=10, pady=(8, 12))
        self.chat_info = tk.StringVar(value="Pronto.")
        tk.Label(self.command_host, textvariable=self.chat_info,
                 bg=PANEL, fg=MUTED,
                 font=("Consolas", 9), anchor="w").pack(
                     fill="x", pady=(0, 4))

        self.visual = tk.Frame(area, bg=BG)
        self.visual.pack(side="left", fill="both", expand=True)
        self.main_visuals = tk.Frame(self.visual, bg=BG)
        self.main_visuals.pack(fill="both", expand=True)
        self.core_canvas = tk.Canvas(
            self.main_visuals, bg=BG, highlightthickness=0,
            borderwidth=0, width=410, height=410)
        self.core_canvas.pack(side="left", fill="both", expand=True)
        self.earth_canvas = tk.Canvas(
            self.main_visuals, bg=BG, highlightthickness=0,
            borderwidth=0, width=260, height=410)
        self.earth_canvas.pack(side="left", fill="both", expand=True)
        self.core_canvas.bind("<Configure>", self._on_resize)
        self.earth_canvas.bind("<Configure>", self._on_resize)
        self.visual_status = tk.StringVar(value="STANDBY  //  IN ATTESA")
        tk.Label(self.visual, textvariable=self.visual_status,
                 bg=BG, fg=MUTED,
                 font=("Consolas", 12), pady=7).pack(fill="x")
        stats = tk.Frame(self.visual, bg=BG)
        stats.pack(fill="x", padx=6, pady=(8, 3))
        self.ram_text = tk.StringVar(value="RAM: --")
        self.disk_text = tk.StringVar(value="DISCO C: --")
        self.clock_text = tk.StringVar(value="--:--")
        for var in (self.ram_text, self.disk_text, self.clock_text):
            tk.Label(stats, textvariable=var, bg=PANEL, fg=CYAN,
                     font=("Consolas", 10), padx=9, pady=12,
                     highlightbackground=FRAME, highlightthickness=1).pack(
                         side="left", fill="x", expand=True, padx=3)
        self._update_metrics()
        self.parent.after(TICK_MS, self._tick)

    def set_state_provider(self, callback):
        self.state_provider = callback

    def set_close_handler(self, callback):
        self.exit_button.configure(command=callback)

    def _on_resize(self, _event=None):
        self._drawn_size = None

    def _base(self, canvas):
        w, h = max(100, canvas.winfo_width()), max(100, canvas.winfo_height())
        return w, h, w/2, h/2, min(w, h)

    def _rebuild_core(self):
        c = self.core_canvas
        c.delete("all")
        w, h, cx, cy, size = self._base(c)
        radius = max(50, min(size*0.43, 225))
        c.create_oval(cx-radius*1.14, cy-radius*1.14,
                      cx+radius*1.14, cy+radius*1.14,
                      outline="#07364f", width=1)
        for scale, color, width in (
                (1.00, "#0a5d8f", 2), (.85, BLUE, 2),
                (.68, "#125679", 2), (.48, CYAN, 2),
                (.31, "#092d45", 3)):
            r = radius * scale
            item = c.create_oval(cx-r, cy-r, cx+r, cy+r,
                                 outline=color, width=width)
            self._core_items.append(item)
        self._rings = []
        for i in range(16):
            scale = .9 if i % 2 else .73
            r = radius * scale
            item = c.create_arc(
                cx-r, cy-r, cx+r, cy+r, start=i*22.5,
                extent=10 if i % 2 else 14, style="arc",
                outline=CYAN if i % 2 == 0 else BLUE, width=5)
            self._rings.append((item, i*22.5, i%2))
        for i in range(48):
            angle = (i / 48) * 2 * math.pi
            r1 = radius*1.06
            r2 = radius*(1.12 if i%4==0 else 1.075)
            x1, y1 = cx+math.sin(angle)*r1, cy+math.cos(angle)*r1
            x2, y2 = cx+math.sin(angle)*r2, cy+math.cos(angle)*r2
            c.create_line(x1, y1, x2, y2,
                          fill="#16536f" if i%4 else BLUE, width=1)
        self.core_glow = c.create_oval(
            cx-radius*.39, cy-radius*.39,
            cx+radius*.39, cy+radius*.39,
            outline=BLUE, width=3)
        self.core_name = c.create_text(
            cx, cy, text="JARVIS", fill=WHITE,
            font=("Segoe UI", max(18, round(radius*.23)), "bold"))
        self.core_state = c.create_text(
            cx, cy+radius*.43, text="SISTEMA PRONTO",
            fill=MUTED, font=("Consolas", max(9, round(radius*.083))))
        self._core_items.append(self.core_glow)

    def _rebuild_earth(self):
        c = self.earth_canvas
        c.delete("all")
        w, h, cx, cy, size = self._base(c)
        radius = min(w*.43, h*.31, 190)
        self.globe_dimensions = (cx, cy, radius)
        c.create_text(cx, max(23, cy-radius-40),
                      text="RETE  //  MONDO", fill=CYAN,
                      font=("Consolas", 11, "bold"))
        c.create_oval(cx-radius,cy-radius,cx+radius,cy+radius,
                      outline="#0f79aa", width=2)
        for i in (-2, -1, 0, 1, 2):
            latitude = math.radians(i*25)
            ry = radius * math.sin(latitude)
            rr = radius * math.cos(latitude)
            c.create_oval(cx-rr,cy-ry*.3-radius*.07,
                          cx+rr,cy-ry*.3+radius*.07,
                          outline="#0a354d", width=1)
        self._meridians = []
        for i in range(6):
            item = c.create_oval(0, 0, 0, 0,
                                 outline="#155c82", width=1)
            self._meridians.append(item)
        self._land_items = [
            c.create_oval(0,0,0,0, fill="#12678b",
                          outline="") for _ in LAND
        ]
        c.create_text(cx, cy+radius+24,
                      text="ROTAZIONE  //  ATTIVA", fill=MUTED,
                      font=("Consolas", 9))

    def _update_metrics(self):
        try:
            memory = memory_usage_windows()
            if memory is not None:
                total, available = memory
                used_percent = round((1-available/total)*100) if total else 0
                self.ram_text.set(f"RAM  {used_percent}%")
            else:
                self.ram_text.set("RAM  --")
            drive = os.environ.get("SystemDrive", "C:") + "\\"
            if os.name == "nt":
                disk = shutil.disk_usage(drive)
                usage = round((disk.used / disk.total)*100) if disk.total else 0
                self.disk_text.set(f"DISCO C  {usage}%")
            else:
                self.disk_text.set("DISCO C  --")
        except (OSError, ValueError):
            self.disk_text.set("DISCO C  --")
        self.clock_text.set(datetime.now().strftime("%H:%M"))

    def _tick(self):
        if self.closed:
            return
        try:
            self._advance()
        except (tk.TclError, ValueError, OSError, TypeError):
            # Decorative drawing may fail on very small/minimized windows.
            # Never take down the actual voice assistant for a visual failure.
            pass
        if not self.closed:
            self.parent.after(TICK_MS, self._tick)

    def _advance(self):
        now = time.monotonic()
        elapsed = min(max(0, now-self.last_tick), .25)
        self.last_tick = now
        if now - self.last_metrics >= 7:
            self._update_metrics()
            self.last_metrics = now
        state = self.state_provider() or {}
        speaking = bool(state.get("speaking", False))
        listening = bool(state.get("listening", False))
        thinking = bool(state.get("thinking", False))
        connected = bool(state.get("connected", False))
        memory = bool(state.get("memory", False))
        self.state_text.set(
            f"MIC  {'ATTIVO' if listening else 'SPENTO'}    •    "
            f"GPT  {'CONNESSO' if connected else 'OFFLINE'}    •    "
            f"MEMORIA  {'ON' if memory else 'OFF'}")
        self.visual_status.set(
            "JARVIS  //  PARLO" if speaking else
            "JARVIS  //  ELABORAZIONE" if thinking else
            "JARVIS  //  ASCOLTO" if listening else
            "JARVIS  //  STANDBY")
        self.chat_info.set(
            "Riproduzione vocale in corso..." if speaking else
            "Sto elaborando la tua richiesta..." if thinking else
            "Microfono attivo" if listening else
            "Microfono spento  •  attivazione manuale")
        target = 1.0 if speaking else 0.0
        # Smooth easing: blue at rest, turquoise/teal in the center
        # while Jarvis *actually* speaks, then ease back toward blue.
        self.speech_color_amount += (target-self.speech_color_amount)*.17
        if not self.parent.winfo_viewable():
            return
        size = (self.core_canvas.winfo_width(),
                self.core_canvas.winfo_height(),
                self.earth_canvas.winfo_width(),
                self.earth_canvas.winfo_height())
        if self._drawn_size != size:
            self._core_items = []
            self._rebuild_core()
            self._rebuild_earth()
            self._drawn_size = size
        self.phase += elapsed
        pulse = .3+.22*math.sin(self.phase*6)
        active_color = interpolate_color(
            BLUE, TURQUOISE,
            max(0.0, min(1.0, self.speech_color_amount*(.78+pulse))))
        self.core_canvas.itemconfigure(self.core_glow, outline=active_color,
                                       width=4 if speaking else 2)
        self.core_canvas.itemconfigure(
            self.core_name, fill=interpolate_color(WHITE, TURQUOISE,
                                                  self.speech_color_amount*.6))
        self.core_canvas.itemconfigure(
            self.core_state,
            text=("TRASMISSIONE VOCE" if speaking else
                  "ELABORAZIONE" if thinking else
                  "ASCOLTO" if listening else "STANDBY"))
        for item, base, parity in self._rings:
            rotation = (self.phase*10 if parity else -self.phase*7)
            self.core_canvas.itemconfigure(
                item, start=(base+rotation)%360,
                outline=(active_color if parity else
                         interpolate_color(BLUE, TURQUOISE,
                                           self.speech_color_amount*.48)))
        cx,cy,r = self.globe_dimensions
        rotation = self.phase*.09
        for i, item in enumerate(self._meridians):
            width = max(1, abs(math.sin(rotation+i*math.pi/6))*r)
            self.earth_canvas.coords(item,cx-width,cy-r,cx+width,cy+r)
        for (lat,lon),item in zip(LAND,self._land_items):
            pos = projected_earth_point(lat,lon,rotation,r)
            if pos is None:
                self.earth_canvas.itemconfigure(item,state="hidden")
            else:
                self.earth_canvas.coords(item,cx+pos[0]-1.2,cy+pos[1]-1.2,
                                          cx+pos[0]+1.2,cy+pos[1]+1.2)
                self.earth_canvas.itemconfigure(item,state="normal")

    def close(self):
        self.closed = True
