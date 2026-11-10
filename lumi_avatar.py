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


class AvatarDock:
    """Mini avatar in basso a destra quando LUMI e' ridotta a icona.

    Doppio clic: ripristina la finestra principale.
    """

    HEIGHT = 190
    KEY = "#010203"

    def __init__(self, root, mode_provider=lambda: "idle"):
        self.root = root
        self.mode_provider = mode_provider
        self.window = None
        self.face = AvatarFace()
        self._job = None
        root.bind("<Unmap>", self._on_unmap, add="+")
        root.bind("<Map>", self._on_map, add="+")

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
        height = self.HEIGHT
        width = round(height * .94)
        left, top, right, bottom = _work_area(self.root)
        win.geometry(f"{width}x{height}+{right - width - 12}+{bottom - height}")
        canvas = tk.Canvas(win, width=width, height=height, bg=self.KEY,
                           highlightthickness=0, bd=0)
        canvas.pack()
        face_y = float(manifest().get("face_y", .5))
        if not self.face.attach(canvas, width / 2, face_y * height, height):
            canvas.create_text(width / 2, height / 2, text="LUMI", fill="#d9f8ff",
                               font=("Segoe UI", 18, "bold"))
        for widget in (win, canvas):
            widget.bind("<Double-Button-1>", self.restore)
        self.window = win
        self.face.start(self.mode_provider)

    def hide(self):
        win, self.window = self.window, None
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
