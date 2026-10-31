"""Static cinematic background for the JARVIS Tkinter canvases.

The approved reference is almost black with sparse PCB-like circuit traces,
small cyan junctions and a few fine sightlines. It is *not* a bright uniform
square grid. Drawing only happens when a canvas is built/resized. No new
graphics dependencies, background threads, network access or audio state.
"""
from __future__ import annotations

import math


DEEP_BLACK = "#01040a"
TRACE_DARK = "#071a2b"
TRACE_MUTED = "#0c3047"
TRACE_CYAN = "#135b7a"
TRACE_HIGHLIGHT = "#1b8fb1"
LED_BLUE = "#1cb9e4"


def _hex(rgb: tuple[int,int,int]) -> str:
    return "#" + "".join(f"{max(0,min(255,v)):02x}" for v in rgb)


def backdrop_tone(row: int, bands: int = 24) -> str:
    """Dark navy-black with a faint central cold-blue atmospheric cast."""
    if type(row) is not int or type(bands) is not int or bands < 2:
        raise ValueError("Invalid background band index")
    if not 0 <= row < bands:
        raise ValueError("Background row is out of range")
    p = row/(bands-1)
    # The pale blue screen-wide square grid from the first version is gone.
    # Values intentionally stay below 18 on every RGB channel.
    hush = math.sin(math.pi*p) ** 2
    return _hex((1, 4 + round(2*hush), 9 + round(7*hush)))


def _trace(canvas, width: int, height: int,
           vertices: tuple[tuple[float,float],...], color: str,
           line_width: float = 1.0) -> None:
    coordinates = [
        n for px,py in vertices for n in (px*width,py*height)
    ]
    canvas.create_line(*coordinates, fill=color,
                       width=line_width, capstyle="round")


def draw_cinematic_backdrop(canvas, width: int, height: int,
                            region: str) -> None:
    """Draw a quiet circuit-board backdrop behind either main HUD visual.

    All shapes stay fixed between resizes, leaving the user's microphone,
    voice-reactive centerpiece, chat and rotating globe untouched.
    """
    if region not in ("reactor","earth"):
        raise ValueError("Unknown HUD backdrop region")
    if type(width) is not int or type(height) is not int:
        raise ValueError("Invalid HUD dimensions")
    if width < 64 or height < 64 or width > 5000 or height > 5000:
        raise ValueError("Unsupported HUD canvas size")

    # 24 flat, dark bands create depth rather than a blue flat-color block.
    bands = 24
    for index in range(bands):
        top = height * index/bands
        bottom = height*(index+1)/bands + 1
        canvas.create_rectangle(
            0,top,width,bottom, fill=backdrop_tone(index,bands),
            outline="")

    if region == "reactor":
        # Deliberately asymmetric technology traces. The center remains
        # mostly empty to keep the glow/ring silhouette legible.
        circuits = (
            ((.012,.08),(.05,.035),(.29,.035),(.32,.067),(.37,.067)),
            ((.05,.16),(.10,.11),(.21,.11),(.255,.065)),
            ((.66,.035),(.84,.035),(.88,.08),(.975,.08)),
            ((.75,.14),(.86,.14),(.91,.09),(.985,.09)),
            ((.01,.34),(.05,.34),(.09,.30),(.17,.30)),
            ((.013,.76),(.09,.76),(.14,.80),(.23,.80)),
            ((.025,.94),(.16,.94),(.20,.90),(.38,.90)),
            ((.51,.96),(.70,.96),(.75,.915),(.90,.915)),
            ((.84,.83),(.94,.83),(.98,.79)),
            ((.95,.27),(.97,.24),(.998,.24)),
            ((.02,.51),(.07,.51),(.11,.54)),
            ((.93,.60),(.97,.60),(.99,.63)),
            ((.19,.035),(.19,.08)),
            ((.89,.14),(.89,.18)),
        )
        for i,path in enumerate(circuits):
            _trace(canvas,width,height,path,
                   TRACE_MUTED if i%4 else TRACE_CYAN,
                   1.1 if i%5==0 else 1.0)

        # One or two extremely faint targeting lines like the reference,
        # not a uniform square grid covering the entire screen.
        for px in (.49,.53):
            _trace(canvas,width,height,
                   ((px,.015),(px,.16)),TRACE_DARK)
            _trace(canvas,width,height,
                   ((px,.87),(px,.99)),TRACE_DARK)
        _trace(canvas,width,height,
               ((.02,.47),(.17,.47)),TRACE_DARK)
        _trace(canvas,width,height,
               ((.85,.48),(.99,.48)),TRACE_DARK)

        # Partial HUD scales, located away from the reactor text.
        for i in range(23):
            x = (.02 + i*.009)*width
            y = .89*height
            canvas.create_line(
                x,y,x,y+(5 if i%5==0 else 2),
                fill=TRACE_CYAN if i%5==0 else TRACE_DARK)
        for i in range(16):
            x = (.79 + i*.012)*width
            y = .74*height
            canvas.create_line(
                x,y,x,y-(5 if i%5==0 else 2),
                fill=TRACE_MUTED if i%5==0 else TRACE_DARK)

        nodes=((.05,.035),(.32,.067),(.84,.035),(.91,.09),
               (.09,.76),(.20,.90),(.70,.96),(.97,.24),
               (.07,.51),(.94,.83),(.19,.11),(.985,.09))
    else:
        # The original preview has dotted schematics and narrow technical
        # corners around the globe, not a luminous blue checkerboard.
        circuits = (
            ((.02,.045),(.10,.015),(.35,.015),(.39,.045)),
            ((.59,.025),(.74,.025),(.81,.07),(.96,.07)),
            ((.08,.20),(.12,.16),(.22,.16)),
            ((.78,.20),(.89,.20),(.95,.15)),
            ((.02,.65),(.08,.65),(.13,.69)),
            ((.85,.66),(.91,.66),(.97,.72)),
            ((.02,.90),(.08,.86),(.32,.86),(.37,.90)),
            ((.61,.91),(.78,.91),(.83,.87),(.98,.87)),
            ((.03,.99),(.34,.99)),
            ((.66,.99),(.96,.99)),
        )
        for i,path in enumerate(circuits):
            _trace(canvas,width,height,path,
                   TRACE_DARK if i%2 else TRACE_MUTED)

        # Several hairline readouts below/right of the planet, without any
        # invented GPS or live satellite/network claims.
        for i in range(12):
            yy=(.795+i*.011)*height
            x0=.03*width
            canvas.create_line(
                x0,yy,x0+(10 if i%3==0 else 4),
                yy,fill=TRACE_MUTED if i%3==0 else TRACE_DARK)
        for j in range(14):
            yy=(.75+j*.015)*height
            x0=.90*width
            canvas.create_line(
                x0,yy,x0+(11 if j%4==0 else 5),
                yy,fill=TRACE_CYAN if j%4==0 else TRACE_DARK)
        nodes=((.10,.015),(.39,.045),(.81,.07),(.96,.07),
               (.08,.65),(.91,.66),(.32,.86),(.83,.87),
               (.03,.99),(.96,.99))

    for i,(x,y) in enumerate(nodes):
        px,py=width*x,height*y
        r=1.7 if i%3==0 else .9
        canvas.create_oval(
            px-r,py-r,px+r,py+r,
            fill=LED_BLUE if i%4==0 else TRACE_HIGHLIGHT,
            outline="")

    # Sparse pixels, fixed seeded layout: restrained texture and identical
    # visual output after every resize, with no animation CPU overhead.
    for i in range(42 if region=="reactor" else 31):
        x=((i*73+19)%997)/997.0
        y=((i*191+47)%991)/991.0
        if region=="reactor" and (.28 < x < .75 and .19 < y < .83):
            continue
        if region=="earth" and (.09 < x < .93 and .18 < y < .76):
            continue
        px,py=x*width,y*height
        canvas.create_rectangle(
            px,py,px+1,py+1,
            fill=TRACE_CYAN if i%9==0 else TRACE_DARK,
            outline="")
