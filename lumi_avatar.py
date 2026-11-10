"""Avatar 2D di LUMI: occhi vivi (battito, sguardo) e bocca in lip sync.

Usa solo Tk PhotoImage (nessuna dipendenza): l'immagine di base e le
piccole toppe per palpebre/sguardo/bocca sono generate in anticipo da
tools/build_lumi_avatar_assets.py partendo dall'immagine originale.
"""
from __future__ import annotations

import json
import random
import sys
import threading
import time
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent / "assets" / "lumi"
_MANIFEST_CACHE: dict | None = None


def manifest() -> dict:
    global _MANIFEST_CACHE
    if _MANIFEST_CACHE is None:
        try:
            _MANIFEST_CACHE = json.loads(
                (ASSET_DIR / "lumi_avatar.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _MANIFEST_CACHE = {"sizes": {}}
    return _MANIFEST_CACHE


def pick_size(height: float) -> int | None:
    """Altezza disponibile in pixel -> altezza dell'immagine pronta piu' adatta."""
    sizes = sorted(int(s) for s in manifest().get("sizes", {}))
    if not sizes:
        return None
    fitting = [s for s in sizes if s <= height]
    return fitting[-1] if fitting else sizes[0]


MOUTH_STEPS = 5


def mouth_level(value: float, steps: int = MOUTH_STEPS) -> int:
    """Volume (gia' ammorbidito) 0..1 -> apertura 0..steps; silenzio = chiusa."""
    if value < .08:
        return 0
    return max(1, min(steps, int(round(value * steps + .2))))


class LipSync:
    """Curva del volume condivisa tra il thread della voce e la UI.

    Il lettore audio comunica la posizione reale di riproduzione
    (update_position): la bocca parte quando parte il suono e resta agganciata
    anche se l'apertura del file tarda. Senza posizione si usa l'orologio
    con il ritardo stimato ``delay``.
    """

    def __init__(self, fps: int = 30):
        self.fps = fps
        self._lock = threading.Lock()
        self._envelope: list[float] = []
        self._start = 0.0
        self._position = None          # (secondi audio, istante della lettura)
        self._ended = False
        self._grace = 0.0

    def push(self, envelope, delay: float = 0.0, grace: float = 0.0) -> None:
        """``grace``: attesa massima della prima posizione dal lettore prima di
        ripiegare sull'orologio (evita una bocca che parte prima del suono)."""
        with self._lock:
            self._envelope = [float(v) for v in (envelope or ())]
            self._start = time.monotonic() + max(0.0, float(delay))
            self._grace = max(0.0, float(grace))
            self._position = None
            self._ended = False

    def update_position(self, seconds: float) -> None:
        """Dal lettore audio: posizione corrente; negativa = audio finito."""
        with self._lock:
            if seconds < 0:
                self._ended = True
                self._position = None
                return
            self._position = (float(seconds), time.monotonic())

    def level(self, now: float | None = None) -> float | None:
        """Valore corrente o None se non c'e' audio con curva in corso."""
        now = time.monotonic() if now is None else now
        with self._lock:
            if not self._envelope or self._ended:
                return None
            if self._position is not None:
                seconds, at = self._position
                if now - at > 0.5:            # posizione ferma: lettore bloccato
                    return None
                t = seconds + (now - at)
            else:
                if now < self._start + self._grace:
                    return None
                t = now - self._start - self._grace
            index = int(t * self.fps)
            if index < 0 or index >= len(self._envelope):
                return None
            return self._envelope[index]


LIPSYNC = LipSync()
PLAYBACK_LATENCY = 0.12   # secondi tra la chiamata al lettore e il primo suono


class HeadMotion:
    """Rotazioni lente e naturali della testa: sceglie ogni tanto una nuova
    direzione e ci arriva con un movimento morbido, poi resta ferma.
    Parlando i cambi sono un po' piu' frequenti e piccoli. Nessun tremolio."""

    def __init__(self, rng: random.Random):
        self.rng = rng
        self.yaw = 0.0
        self.start = 0.0
        self.target = 0.0
        self.t0 = None
        self.duration = 1.0
        self.next_change = 0.0

    def update(self, now: float, talking: bool) -> float:
        if self.t0 is None:
            self.t0, self.next_change = now, now + self.rng.uniform(1.5, 3.0)
        if now >= self.next_change:
            self.start, self.t0 = self.yaw, now
            if talking:
                self.target = self.rng.uniform(-.55, .55)
                hold = self.rng.uniform(1.2, 2.8)
            else:
                self.target = 0.0 if self.rng.random() < .35 else self.rng.uniform(-.9, .9)
                hold = self.rng.uniform(2.5, 6.0)
            self.duration = .9 + abs(self.target - self.start) * .9
            self.next_change = now + self.duration + hold
        k = min(1.0, max(0.0, (now - self.t0) / self.duration))
        ease = k * k * (3 - 2 * k)          # smoothstep: parte e arriva piano
        self.yaw = self.start + (self.target - self.start) * ease
        return self.yaw


class HairLag:
    """Le ciocche seguono la testa con un piccolo ritardo e si assestano
    (molla smorzata): -1..1, zero da ferma."""

    def __init__(self):
        self.value = 0.0
        self.speed = 0.0
        self.last = None
        self.last_yaw = 0.0

    def update(self, now: float, yaw: float) -> float:
        if self.last is None:
            self.last, self.last_yaw = now, yaw
            return 0.0
        dt = min(.1, max(0.0, now - self.last))
        if dt <= 0:
            return self.value
        velocity = (yaw - self.last_yaw) / dt
        self.last, self.last_yaw = now, yaw
        target = max(-1.0, min(1.0, -velocity * 1.4))   # restano indietro
        # molla: rigidezza 30, smorzamento 7 -> un piccolo assestamento
        accel = 30.0 * (target - self.value) - 7.0 * self.speed
        self.speed += accel * dt
        self.value = max(-1.0, min(1.0, self.value + self.speed * dt))
        return self.value


class AvatarFace:
    """Volto animato disegnato su un Canvas Tk esistente."""

    def __init__(self, rng: random.Random | None = None):
        self.canvas = None
        self.size = None
        self.items = {}
        self.photos = {}
        self.offsets = []          # per posa: {stato: [x, y]}
        self.poses = [0.0]
        self.pose = 0
        self.rng = rng or random.Random()
        self.head = HeadMotion(self.rng)
        self.hair = HairLag()
        self.hair_levels = [0.0]
        self.hair_index = 0
        self.breath_boxes = []
        self.breath_index = 0
        self._breath_period = self.rng.uniform(3.8, 4.8)
        self._breath_phase = self.rng.uniform(0, 6.28)
        self._mouth_value = 0.0
        self.mouth_steps = MOUTH_STEPS
        self._loop_job = None
        self._mode_provider = None
        self._next_blink = 0.0
        self._blink_until = 0.0
        self._next_gaze = 0.0
        self._gaze = None
        self._eye_state = None
        self._mouth_state = None

    def attach(self, canvas, cx: float, cy: float, height: float) -> bool:
        """Figura intera centrata in orizzontale, volto all'altezza cy."""
        import tkinter as tk
        self.canvas = canvas
        self.items = {}
        self._eye_state = self._mouth_state = None
        size = pick_size(height)
        if size is None:
            return False
        data = manifest()
        try:
            if size != self.size or not self.photos:
                photos = {}
                entry = data["sizes"][str(size)]
                hair = [float(h) for h in data.get("hair", [0.0])]
                for index, patches in enumerate(entry["poses"]):
                    for h in range(len(hair)):
                        photos[(index, "base", h)] = tk.PhotoImage(
                            master=canvas, file=str(ASSET_DIR / f"lumi_{size}_p{index}_h{h}.png"))
                    for name in patches:
                        photos[(index, name)] = tk.PhotoImage(
                            master=canvas, file=str(ASSET_DIR / f"lumi_{size}_p{index}_{name}.png"))
                for level, box in enumerate(entry.get("breath", [])):
                    if box:
                        photos[("breath", level)] = tk.PhotoImage(
                            master=canvas, file=str(ASSET_DIR / f"lumi_{size}_b{level}.png"))
                self.photos, self.offsets, self.size = photos, entry["poses"], size
                self.breath_boxes = entry.get("breath", [])
                self.poses = [float(p) for p in data.get("poses", [0.0])]
                self.hair_levels = hair
        except (tk.TclError, OSError, KeyError, TypeError):
            self.photos = {}
            return False
        self.pose = int(data.get("rest_pose", 0))
        self.hair_index = int(data.get("rest_hair", 0))
        self.mouth_steps = int(data.get("mouth_levels", MOUTH_STEPS))
        self.breath_index = 0
        base = self.photos[(self.pose, "base", self.hair_index)]
        face_y = float(data.get("face_y", .5))
        x0, y0 = cx - base.width() / 2, cy - face_y * size
        self.origin = (x0, y0)
        self.items["base"] = canvas.create_image(x0, y0, anchor="nw", image=base)
        self.items["breath"] = canvas.create_image(x0, y0, anchor="nw", state="hidden")
        self.items["eyes"] = canvas.create_image(x0, y0, anchor="nw", state="hidden")
        self.items["mouth"] = canvas.create_image(x0, y0, anchor="nw", state="hidden")
        return True

    def _show(self, slot: str, name: str | None) -> None:
        item = self.items.get(slot)
        if item is None:
            return
        key = (self.pose, name)
        if name is None or key not in self.photos:
            self.canvas.itemconfigure(item, state="hidden")
            return
        dx, dy = self.offsets[self.pose][name]
        x0, y0 = self.origin
        self.canvas.coords(item, x0 + dx, y0 + dy)
        self.canvas.itemconfigure(item, image=self.photos[key], state="normal")

    def eye_frame(self, now: float) -> str | None:
        if now >= self._next_blink:
            self._blink_until = now + .13
            # Ogni tanto un doppio battito, come una persona vera.
            gap = .25 if self.rng.random() < .15 else self.rng.uniform(2.5, 6.0)
            self._next_blink = now + gap
        if now < self._blink_until:
            return "blink"
        if now >= self._next_gaze:
            self._gaze = self.rng.choice((None, None, "look_l", "look_r"))
            self._next_gaze = now + self.rng.uniform(1.2, 4.0)
        return self._gaze

    def mouth_frame(self, now: float, speaking: bool = False) -> str | None:
        """Bocca guidata SOLO dall'audio in riproduzione.

        La curva arriva un istante prima che parta il suono (dopo la sintesi),
        quindi la bocca non si muove mentre la voce viene ancora preparata.
        Anche la voce Windows ora passa da un file WAV con la sua curva
        (offline_tts). `speaking` resta solo per compatibilita'.
        """
        raw = LIPSYNC.level(now) or 0.0
        # Apertura rapida, chiusura un po' piu' lenta: niente sfarfallio.
        k = .65 if raw > self._mouth_value else .35
        self._mouth_value += (raw - self._mouth_value) * k
        if raw == 0 and self._mouth_value < .05:
            self._mouth_value = 0.0
        level = mouth_level(self._mouth_value, self.mouth_steps)
        return f"mouth{level}" if level else None

    def pose_for(self, yaw: float) -> int:
        return min(range(len(self.poses)), key=lambda i: abs(self.poses[i] - yaw))

    def start(self, mode_provider=lambda: "idle", interval_ms: int = 40) -> None:
        """Animazione a 25 fotogrammi/s, indipendente dal ritmo del HUD:
        bocca e testa non restano agganciate ai 110 ms del nucleo."""
        self.stop()
        self._mode_provider = mode_provider
        canvas = self.canvas

        def step():
            if self.canvas is not canvas or not self.items:
                return
            delay = interval_ms
            try:
                if canvas.winfo_viewable():
                    self.tick(self._mode_provider())
                else:
                    delay = 250           # finestra nascosta: quasi nessun lavoro
            except Exception:
                return
            try:
                self._loop_job = canvas.after(delay, step)
            except Exception:
                self._loop_job = None
        step()

    def stop(self) -> None:
        job, self._loop_job = self._loop_job, None
        if job is not None and self.canvas is not None:
            try:
                self.canvas.after_cancel(job)
            except Exception:
                pass

    def breath_level(self, now: float) -> int:
        """Respiro lento (~4 s): spalle e petto salgono e scendono."""
        if not self.breath_boxes:
            return 0
        import math
        wave = (1 - math.cos(2 * math.pi * now / self._breath_period + self._breath_phase)) / 2
        return int(round(wave * (len(self.breath_boxes) - 1)))

    def _set_base(self) -> None:
        key = (self.pose, "base", self.hair_index)
        if key in self.photos:
            self.canvas.itemconfigure(self.items["base"], image=self.photos[key])

    def tick(self, mode: str = "idle", now: float | None = None) -> None:
        if not self.items:
            return
        now = time.monotonic() if now is None else now
        yaw = self.head.update(now, LIPSYNC.level(now) is not None)
        pose = self.pose_for(yaw)
        hair_value = self.hair.update(now, yaw)
        hair = min(range(len(self.hair_levels)),
                   key=lambda i: abs(self.hair_levels[i] - hair_value))
        moved = pose != self.pose
        if moved or hair != self.hair_index:
            self.pose, self.hair_index = pose, hair
            self._set_base()
        breath = self.breath_level(now)
        if breath != self.breath_index:
            self.breath_index = breath
            item = self.items.get("breath")
            box = self.breath_boxes[breath] if breath < len(self.breath_boxes) else None
            if item is not None:
                if box and ("breath", breath) in self.photos:
                    x0, y0 = self.origin
                    self.canvas.coords(item, x0 + box[0], y0 + box[1])
                    self.canvas.itemconfigure(item, image=self.photos[("breath", breath)],
                                              state="normal")
                else:
                    self.canvas.itemconfigure(item, state="hidden")
        eye = self.eye_frame(now)
        if eye != self._eye_state or moved:
            self._show("eyes", eye)
            self._eye_state = eye
        mouth = self.mouth_frame(now)
        if mouth != self._mouth_state or moved:
            self._show("mouth", mouth)
            self._mouth_state = mouth


def _work_area(root) -> tuple[int, int, int, int]:
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            rect = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                return rect.left, rect.top, rect.right, rect.bottom
        except Exception:
            pass
    return 0, 0, root.winfo_screenwidth(), root.winfo_screenheight() - 48


def _dock_file() -> Path | None:
    try:
        from settings import default_path
        return default_path().parent / "avatar-dock.json"
    except Exception:
        return None


def load_dock_position(path: Path | None) -> tuple[int, int] | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        x, y = data["x"], data["y"]
        if type(x) is int and type(y) is int and -10000 < x < 20000 and -10000 < y < 20000:
            return x, y
    except Exception:
        pass
    return None


def save_dock_position(path: Path | None, x: int, y: int) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"x": int(x), "y": int(y)}), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def clamp_dock(x: int, y: int, width: int, height: int, area) -> tuple[int, int]:
    """Tiene il mini avatar dentro l'area utile (mai sotto la barra delle applicazioni)."""
    left, top, right, bottom = area
    x = max(left, min(int(x), right - width))
    y = max(top, min(int(y), bottom - height))
    return x, y


class AvatarDock:
    """Mini avatar quando LUMI e' ridotta a icona.

    Trascinalo col mouse per spostarlo (la posizione resta salvata).
    Doppio clic: ripristina la finestra principale.
    Con la musica attiva, accanto compaiono i comandi del lettore (⏮ ⏯ ⏭ e titolo).
    """

    HEIGHT = 190
    KEY = "#010203"
    PANEL_W = 150
    MARGIN = 16

    def __init__(self, root, mode_provider=lambda: "idle", position_file="auto",
                 music_provider=None):
        self.root = root
        self.mode_provider = mode_provider
        self.position_file = _dock_file() if position_file == "auto" else position_file
        self.music_provider = music_provider or self._default_music
        self.window = None
        self.face = AvatarFace()
        self._job = None
        self._panel = None
        self._panel_shown = False
        self._drag = None
        self._avatar_xy = None
        root.bind("<Unmap>", self._on_unmap, add="+")
        root.bind("<Map>", self._on_map, add="+")

    @staticmethod
    def _default_music():
        try:
            from musica import runtime
            service = runtime.service()
            if service is not None and service.is_enabled():
                return service
        except Exception:
            pass
        return None

    def _on_unmap(self, event=None):
        if event is not None and event.widget is not self.root:
            return
        self.root.after(120, self._check_iconic)

    def _check_iconic(self):
        try:
            if self.root.state() == "iconic":
                self.show()
        except Exception:
            pass

    def _on_map(self, event=None):
        if event is not None and event.widget is not self.root:
            return
        self.hide()

    def _size(self):
        height = self.HEIGHT
        return round(height * .94), height

    def _place(self):
        """Posiziona la finestra: l'avatar resta fermo, il pannello musica va a sinistra."""
        width, height = self._size()
        extra = self.PANEL_W if self._panel_shown else 0
        area = _work_area(self.root)
        x, y = self._avatar_xy
        x, y = clamp_dock(x - extra, y, width + extra, height, area)
        self._avatar_xy = (x + extra, y)
        self.window.geometry(f"{width + extra}x{height}+{x}+{y}")

    def show(self):
        import tkinter as tk
        if self.window is not None:
            return
        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.configure(bg=self.KEY)
        try:
            win.attributes("-topmost", True)
            win.attributes("-transparentcolor", self.KEY)
        except tk.TclError:
            pass
        width, height = self._size()
        left, top, right, bottom = _work_area(self.root)
        saved = load_dock_position(self.position_file)
        # Predefinito: in basso a destra, staccato dalla barra delle applicazioni.
        self._avatar_xy = saved or (right - width - 12, bottom - height - self.MARGIN)
        self.window = win
        self._panel = self._build_panel(win)
        canvas = tk.Canvas(win, width=width, height=height, bg=self.KEY,
                           highlightthickness=0, bd=0)
        canvas.pack(side="right")
        self._place()
        face_y = float(manifest().get("face_y", .5))
        if not self.face.attach(canvas, width / 2, face_y * height, height):
            canvas.create_text(width / 2, height / 2, text="LUMI", fill="#d9f8ff",
                               font=("Segoe UI", 18, "bold"))
        for widget in (win, canvas):
            widget.bind("<Double-Button-1>", self.restore)
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)
            widget.bind("<ButtonRelease-1>", self._drag_end)
        self.face.start(self.mode_provider)
        self._music_tick()

    # --- trascinamento ----------------------------------------------------
    def _drag_start(self, event):
        self._drag = (event.x_root, event.y_root, self.window.winfo_x(), self.window.winfo_y())

    def _drag_move(self, event):
        if self._drag is None or self.window is None:
            return
        x0, y0, wx, wy = self._drag
        extra = self.PANEL_W if self._panel_shown else 0
        self._avatar_xy = (wx + event.x_root - x0 + extra, wy + event.y_root - y0)
        self._place()

    def _drag_end(self, _event=None):
        if self._drag is not None and self._avatar_xy is not None:
            save_dock_position(self.position_file, *self._avatar_xy)
        self._drag = None

    # --- comandi musica (tipo PiP) ----------------------------------------
    def _build_panel(self, win):
        import tkinter as tk
        panel = tk.Frame(win, bg="#031522", highlightthickness=1,
                         highlightbackground="#1b6f8f", width=self.PANEL_W - 6)
        self._title = tk.StringVar(value="")
        tk.Label(panel, textvariable=self._title, bg="#031522", fg="#d7f6ff",
                 font=("Segoe UI", 8), anchor="w", width=1).pack(fill="x", padx=4, pady=(4, 2))
        row = tk.Frame(panel, bg="#031522")
        row.pack(pady=(0, 4))
        style = dict(bg="#06263a", fg="#d7f6ff", activebackground="#1b6f8f", bd=0, width=3,
                     font=("Segoe UI Symbol", 10))
        tk.Button(row, text="⏮", command=lambda: self._music("prev"), **style).pack(side="left", padx=1)
        self._toggle = tk.Button(row, text="⏸", command=lambda: self._music("toggle"), **style)
        self._toggle.pack(side="left", padx=1)
        tk.Button(row, text="⏭", command=lambda: self._music("next"), **style).pack(side="left", padx=1)
        tk.Button(row, text="⏹", command=lambda: self._music("stop"), **style).pack(side="left", padx=1)
        for widget in (panel,):
            widget.bind("<ButtonPress-1>", self._drag_start)
            widget.bind("<B1-Motion>", self._drag_move)
            widget.bind("<ButtonRelease-1>", self._drag_end)
        return panel

    def _music(self, action):
        service = self.music_provider()
        if service is None:
            return
        try:
            if action == "toggle":
                action = "resume" if service.snapshot().get("state") == "paused" else "pause"
            service.handle(action)
        except Exception:
            pass
        self._music_tick(reschedule=False)

    def _music_tick(self, reschedule=True):
        if self.window is None:
            return
        try:
            service = self.music_provider()
            snap = service.snapshot() if service is not None else {}
            active = snap.get("mode") is not None and snap.get("state") not in (None, "stopped")
            if active:
                title = str(snap.get("title", ""))
                self._title.set(title if len(title) <= 22 else title[:21] + "…")
                self._toggle.configure(text="▶" if snap.get("state") == "paused" else "⏸")
            if active != self._panel_shown:
                if active:
                    self._panel.pack(side="left", anchor="s", pady=(0, 24), padx=(0, 6))
                else:
                    self._panel.pack_forget()
                self._panel_shown = active
                self._place()
        except Exception:
            pass
        if reschedule and self.window is not None:
            self._job = self.window.after(700, self._music_tick)

    def hide(self):
        win, self.window = self.window, None
        self._panel_shown = False
        if win is not None:
            self.face.stop()
            self.face.items = {}
            win.destroy()

    def restore(self, _event=None):
        self.hide()
        self.root.deiconify()
        self.root.lift()
        try:
            self.root.focus_force()
        except Exception:
            pass
