"""Clickable orbiting HUD markers for active projects and Telegram.

Single Tk Canvas, zero extra background threads. Markers move at the existing
HUD tick rate and use the current ReactorArt geometry. Mouse hover shows
a label; click opens a handler supplied by Lumi, never runs code from memory.
"""
from __future__ import annotations

import math

MARKER_COLORS={"project":"#25d4ff","telegram":"#8061ad",
               "telegram_unread":"#d6afff",
               "pending":"#ffbc61"}
TELEGRAM_PULSE_DIM="#9b72cc"
MAX_MARKERS=36


def orbit_position(index:int,count:int,phase:float,cx:float,cy:float,
                   radius:float) -> tuple[float,float]:
    if not 0<=index<count or count<=0:
        raise ValueError("Indice orbita non valido.")
    # Second ring activates only when a large number of projects exist.
    ring=index//18
    slot=index%18
    ring_count=min(18,count-ring*18)
    angle=(math.tau*slot/ring_count)+phase*.11*(1 if ring==0 else -.7)-math.pi/2
    d=radius*(1.045 if ring==0 else 1.15)
    return (cx+math.cos(angle)*d,cy+math.sin(angle)*d)


def sanitize_nodes(nodes):
    if not isinstance(nodes,(tuple,list)):
        return ()
    result=[]
    for entry in nodes[:MAX_MARKERS]:
        if (not isinstance(entry,dict)
                or entry.get("kind") not in MARKER_COLORS):
            continue
        key=entry.get("id")
        name=entry.get("name")
        if (not isinstance(key,str) or not 1<=len(key)<=90
                or not isinstance(name,str) or not 1<=len(name.strip())<=90):
            continue
        result.append((key,entry["kind"],name.strip()[:90]))
    return tuple(result)


class OrbitMarkers:
    def __init__(self,canvas,on_open=None):
        self.canvas=canvas
        self.on_open=on_open or (lambda ident:None)
        self.nodes=()
        self._items=[]
        self._hover=None
        self._tip=None
        self._tip_box=None
        self._geometry=None
        self._pulse_bright=None

    def reset(self):
        # Called after ReactorArt.build clears the whole canvas.
        self.nodes=()
        self._items=[]
        self._hover=None
        self._tip=None
        self._tip_box=None

    def update(self,nodes,cx,cy,r,phase):
        clean=sanitize_nodes(nodes)
        geometry=(round(cx),round(cy),round(r))
        if clean!=self.nodes or geometry!=self._geometry:
            self._build(clean,geometry)
        if not self._items:
            return
        pulse_bright=phase % 1.4 < 0.7
        pulse_changed=pulse_bright!=self._pulse_bright
        self._pulse_bright=pulse_bright
        n=len(self._items)
        for index,(circle,halo) in enumerate(self._items):
            x,y=orbit_position(index,n,phase,cx,cy,r)
            self.canvas.coords(halo,x-7,y-7,x+7,y+7)
            self.canvas.coords(circle,x-4,y-4,x+4,y+4)
            if pulse_changed and self.nodes[index][1]=="telegram_unread":
                color=MARKER_COLORS["telegram_unread"] if pulse_bright else TELEGRAM_PULSE_DIM
                self.canvas.itemconfigure(circle,fill=color)
                self.canvas.itemconfigure(halo,outline=color)
            if self._hover==index:
                self._show_tip(index,x,y)

    def _build(self,clean,geometry):
        for item in self._items:
            self.canvas.delete(item[0])
            self.canvas.delete(item[1])
        if self._tip is not None:
            self.canvas.delete(self._tip)
            self.canvas.delete(self._tip_box)
        self._tip=None
        self._tip_box=None
        self._hover=None
        self._items=[]
        self._pulse_bright=None
        self.nodes=clean
        self._geometry=geometry
        for index,(_id,kind,_name) in enumerate(clean):
            color=MARKER_COLORS[kind]
            halo=self.canvas.create_oval(0,0,1,1,fill="",
                                        outline=color,width=1)
            circle=self.canvas.create_oval(0,0,1,1,fill=color,
                                          outline="#e8faff",width=1)
            self._items.append((circle,halo))
            for item in (circle,halo):
                self.canvas.tag_bind(
                    item,"<Enter>",lambda _e,i=index:self._enter(i))
                self.canvas.tag_bind(
                    item,"<Leave>",lambda _e,i=index:self._leave(i))
                self.canvas.tag_bind(
                    item,"<Button-1>",lambda _e,i=index:self._click(i))

    def _enter(self,index):
        self._hover=index

    def _leave(self,index):
        if self._hover==index:
            self._hover=None
            if self._tip is not None:
                self.canvas.itemconfigure(self._tip,state="hidden")
                self.canvas.itemconfigure(self._tip_box,state="hidden")

    def _click(self,index):
        if 0<=index<len(self.nodes):
            self.on_open(self.nodes[index][0])

    def _show_tip(self,index,x,y):
        _,kind,name=self.nodes[index]
        text=("PROGETTO  " if kind=="project" else
              "TELEGRAM  " if kind in ("telegram","telegram_unread") else "IN ATTESA  ")+name
        cw=self.canvas.winfo_width()
        ch=self.canvas.winfo_height()
        tx=max(8,min(cw-240,x+11))
        ty=max(18,min(ch-20,y-17))
        if self._tip is None:
            self._tip_box=self.canvas.create_rectangle(
                0,0,1,1,fill="#031323",outline="#208bbb",width=1)
            self._tip=self.canvas.create_text(
                0,0,text=text,fill="#d9f8ff",
                font=("Consolas",9,"bold"),anchor="w")
        self.canvas.coords(self._tip,tx+6,ty)
        self.canvas.itemconfigure(self._tip,text=text,state="normal")
        bbox=self.canvas.bbox(self._tip)
        if bbox:
            self.canvas.coords(self._tip_box,bbox[0]-5,bbox[1]-3,
                               bbox[2]+5,bbox[3]+3)
            self.canvas.itemconfigure(self._tip_box,state="normal")
        self.canvas.tag_raise(self._tip_box)
        self.canvas.tag_raise(self._tip)
