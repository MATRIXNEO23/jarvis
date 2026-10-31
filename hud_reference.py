"""Vector HUD art modelled after Jarvis's approved cinematic reference.

All drawing uses stock Tk Canvas. Nothing here controls Windows, audio,
microphone state, files or model tools. Real-time values come from the host UI.
"""
from __future__ import annotations

import math
import random

CYAN = "#16d8ff"
AMBER = "#ff9d26"
GREEN = "#39f3a7"
BG = "#010711"
MUTED = "#6597b2"

# Decorative continents on a longitude/latitude grid. They are stylized,
# not a detailed political map and do not imply live satellite imagery.
COASTS = (
    # Africa
    ((-17,36),(-6,36),(1,37),(10,37),(14,33),(20,33),(29,31),
     (32,24),(37,20),(43,12),(50,12),(47,5),(43,-4),(42,-12),
     (35,-17),(33,-26),(27,-33),(20,-35),(16,-30),(12,-22),
     (9,-13),(5,-4),(-1,4),(-11,5),(-15,14),(-16,25)),
    # Europe
    ((-11,36),(-10,43),(-6,44),(-9,51),(-5,55),(0,52),(3,57),
     (8,54),(12,59),(17,58),(21,69),(26,70),(30,67),
     (28,61),(33,60),(42,57),(39,53),(31,49),(29,45),
     (26,42),(24,36),(19,39),(14,45),(9,43),(7,38),(2,41)),
    # Asia and Middle East
    ((30,40),(36,47),(43,49),(50,55),(64,55),(75,56),(88,61),
     (101,63),(112,58),(125,59),(134,54),(142,50),(149,43),
     (143,39),(136,34),(130,30),(123,22),(120,13),(111,10),
     (105,2),(100,-3),(99,12),(95,17),(89,22),(83,26),
     (79,16),(74,8),(68,22),(58,26),(53,16),(49,16),
     (44,19),(41,28),(35,34)),
    # North America
    ((-167,70),(-152,72),(-144,66),(-135,60),(-127,55),(-124,49),
     (-125,44),(-122,38),(-117,33),(-112,31),(-110,25),
     (-105,23),(-98,19),(-96,16),(-91,15),(-89,21),
     (-86,21),(-84,17),(-80,24),(-81,30),(-76,34),
     (-72,41),(-66,45),(-60,51),(-64,55),(-72,58),
     (-81,60),(-91,62),(-101,70),(-111,72),(-130,71),
     (-144,72)),
    # South America
    ((-81,12),(-75,11),(-69,11),(-62,9),(-55,6),(-51,3),
     (-47,0),(-40,-3),(-35,-7),(-38,-12),(-41,-18),
     (-45,-21),(-48,-27),(-53,-32),(-57,-37),(-62,-42),
     (-66,-48),(-70,-53),(-73,-43),(-75,-35),(-73,-26),
     (-75,-16),(-78,-5),(-81,2)),
    # Australia
    ((113,-12),(121,-14),(130,-11),(135,-12),(140,-17),
     (147,-19),(153,-25),(150,-32),(146,-38),(138,-38),
     (133,-35),(124,-36),(115,-32),(113,-24)),
    # Greenland
    ((-52,60),(-42,60),(-37,67),(-41,76),(-48,83),
     (-56,82),(-60,76),(-54,68)),
    # Japan
    ((130,32),(133,34),(137,36),(140,41),(143,45),
     (146,42),(141,37),(136,34)),
    # Madagascar
    ((49,-12),(50,-18),(47,-25),(44,-23),(45,-16)),
)

LIGHTS = (
    (51,-.1),(48.85,2.35),(52.52,13.4),(41.9,12.5),
    (45.46,9.2),(40.42,-3.7),(38.7,-9.1),(55.75,37.6),
    (41,29),(30,31),(28,-26),(19,-99),(40.7,-74),
    (34,-118),(43,-79),(23,-102),(19,-70),
    (-23,-46),(-34,-58),(-12,-77),(-34,151),
    (28,77),(19,72),(13,80),(35,139),(37,127),
    (31,121),(39,116),(22,114),(1,104),(14,121),
)


def lerp_color(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, float(t)))
    aa = [int(a[i:i+2],16) for i in (1,3,5)]
    bb = [int(b[i:i+2],16) for i in (1,3,5)]
    return "#" + "".join(f"{round(x+(y-x)*t):02x}" for x,y in zip(aa,bb))


def core_mode(*, speaking: bool, listening: bool) -> str:
    # If SAPI is playing, the microphone may still be open: speech wins.
    if speaking:
        return "speaking"
    if listening:
        return "listening"
    return "idle"


def core_light(mode: str, phase: float) -> tuple[str,float]:
    """Return light hue and pulse factor for the three *actual* audio modes."""
    if mode == "speaking":
        return GREEN, .52+.48*(.5+.5*math.sin(phase*14.0))
    if mode == "listening":
        return AMBER, .38+.62*(.5+.5*math.sin(phase*9.0))
    return CYAN, .65


def projected_earth_point(lat: float, lon: float,
                          turn: float, radius: float):
    latitude = math.radians(lat)
    longitude = math.radians(lon) + turn
    depth = math.cos(latitude)*math.cos(longitude)
    if depth < 0:
        return None
    return (radius*math.cos(latitude)*math.sin(longitude),
            -radius*math.sin(latitude))


def coast_samples():
    result=[]
    for poly in COASTS:
        for (lon1,lat1),(lon2,lat2) in zip(poly,poly[1:]+poly[:1]):
            segments=max(1, int(max(abs(lon2-lon1),abs(lat2-lat1))/3.7))
            for j in range(segments):
                t=j/segments
                result.append((lat1+(lat2-lat1)*t,
                               lon1+(lon2-lon1)*t))
    return tuple(result)

LAND = coast_samples()


def _inside_land(lon,lat,poly):
    """Point-in-polygon for decorative ocean/land shading samples."""
    inside=False
    previous=poly[-1]
    for current in poly:
        x1,y1=previous
        x2,y2=current
        if ((y1>lat)!=(y2>lat)):
            crossing=x1+(lat-y1)*(x2-x1)/(y2-y1)
            if lon<crossing:
                inside=not inside
        previous=current
    return inside


def land_texture():
    rng=random.Random(47)
    points=[]
    for polygon in COASTS:
        low_lon=min(p[0] for p in polygon)
        high_lon=max(p[0] for p in polygon)
        low_lat=min(p[1] for p in polygon)
        high_lat=max(p[1] for p in polygon)
        lon=int(low_lon)
        while lon<=int(high_lon):
            lat=int(low_lat)
            while lat<=int(high_lat):
                jitter_lon=lon+rng.uniform(-2,2)
                jitter_lat=lat+rng.uniform(-2,2)
                if _inside_land(jitter_lon,jitter_lat,polygon):
                    points.append((jitter_lat,jitter_lon))
                lat+=5
            lon+=5
    rng.shuffle(points)
    return tuple(points[:170])

LAND_TEXTURE = land_texture()


def _ellipse(c,cx,cy,r,*,outline="",fill="",width=1):
    return c.create_oval(cx-r,cy-r,cx+r,cy+r,outline=outline,fill=fill,width=width)


class ReactorArt:
    """Multi-layer illuminated segmented rings with a purely visual pulse."""

    def __init__(self):
        self.arc_items=[]
        self.pulse_items=[]
        self.core_name=None
        self.core_fill=[]
        self.rim=None
        self.system_lamps=[]
        self.canvas=None

    def build(self, canvas) -> None:
        self.canvas=canvas
        c=canvas
        c.delete("all")
        w=max(c.winfo_width(),120)
        h=max(c.winfo_height(),120)
        cx,cy=w*.51,h*.51
        r=max(45,min(w*.45,h*.44,245))
        self.geometry=(cx,cy,r)
        rng=random.Random(33)
        # Fine blueprint lines and small connection nodes.
        for x in range(16,int(w),36):
            c.create_line(x,5,x,h-5,fill="#061a2a")
        for y in range(18,int(h),36):
            c.create_line(6,y,w-6,y,fill="#061827")
        for i in range(32):
            x=rng.randrange(12,max(13,int(w-12)))
            y=rng.randrange(12,max(13,int(h-12)))
            sz=1.1 if i%5 else 1.8
            c.create_oval(x-sz,y-sz,x+sz,y+sz,fill="#135375",outline="")
        # Smaller telemetry card, similar to the approved concept, without
        # inventing the state of any external service.
        if w>345:
            x1,y1=10,9
            x2,y2=146,99
            c.create_polygon(x1+13,y1,x2-13,y1,x2,y1+12,x2,y2-14,
                             x2-13,y2,x1,y2,x1,y1+12,
                             fill="#051624",outline="#145574")
            c.create_text(x1+15,y1+17,text="SISTEMA",fill=CYAN,
                          font=("Consolas",9,"bold"),anchor="w")
            self.system_lamps=[]
            for j,name in enumerate(("MIC","GPT","MEMORIA")):
                y=y1+37+j*18
                c.create_text(x1+15,y,text=name,fill=MUTED,
                              font=("Consolas",8),anchor="w")
                led=c.create_oval(x2-26,y-3,x2-20,y+3,
                                  fill="#345568",outline="")
                self.system_lamps.append(led)
        # Crosshair, outer orbits, and small peripheral highlights.
        for scale,color,width in (
                (1.14,"#052d47",1),(1.08,"#0b3c5a",1),
                (1.02,"#0a567d",1),(.965,"#1377a7",1),
                (.89,"#12496c",1),(.81,"#1473a7",2),
                (.70,"#0e3d60",1),(.60,"#0b6587",1),
                (.52,"#184d71",1),(.38,"#0a4872",1)):
            _ellipse(c,cx,cy,r*scale,outline=color,width=width)
        for j in range(58):
            angle=math.tau*j/58
            inner=r*(1.088 if j%5 else 1.082)
            outer=r*(1.111 if j%5 else 1.138)
            c.create_line(cx+inner*math.cos(angle),
                          cy+inner*math.sin(angle),
                          cx+outer*math.cos(angle),
                          cy+outer*math.sin(angle),
                          fill="#12678b" if j%5 else "#38b8dd",
                          width=1 if j%5 else 2)
        self.arc_items=[]
        for row,(scale,count,extent,width,speed) in enumerate((
                (.99,28,5.2,2.0,2.7),
                (.935,13,12.5,4.0,-4.3),
                (.86,20,10.4,3.0,3.8),
                (.775,13,11.3,5.0,-5.2),
                (.68,18,8.5,2.0,4.8),
                (.48,12,16.5,4.0,-7.4),
                (.405,12,10.0,2.0,5.8),
        )):
            rr=r*scale
            for i in range(count):
                a=i*(360/count)+(row*7)%19
                seg_extent=extent*(1.38 if i%4==0 else .9)
                item=c.create_arc(cx-rr,cy-rr,cx+rr,cy+rr,
                                  start=a,extent=seg_extent,style="arc",
                                  outline=("#17b8f5" if i%4==0
                                           else "#125477"),width=width)
                # Most fine arcs remain static, while selected bright arcs
                # rotate to give depth without thousands of Tk calls/sec.
                if i%3 == 0:
                    self.arc_items.append((item,a,speed, i%4==0))
        # Animated hub inner illumination is layered; no large video assets.
        self.core_fill=[]
        for scale,base,tint in (
                (.355,"#061729","#144b51"),
                (.30,"#071b2e","#0d5c54"),
                (.25,"#071d30","#0e7a5b"),
                (.17,"#092238","#17835a"),
        ):
            item=_ellipse(c,cx,cy,r*scale,fill=base)
            self.core_fill.append((item,base,tint))
        self.rim=_ellipse(c,cx,cy,r*.36,outline=CYAN,width=3)
        self.pulse_items=[
            _ellipse(c,cx,cy,r*.43,outline="#165f83",width=2),
            _ellipse(c,cx,cy,r*.54,outline="#165f83",width=2)]
        self.core_name=c.create_text(cx,cy-1,
                                     text="JARVIS",
                                     fill="#d9f8ff",
                                     font=("Segoe UI",max(16,int(r*.24)),"bold"))
        # Tiny status lines below the reactor (never "ASCOLTO" inside it).
        c.create_text(cx,cy+r*.61,text="◈  ARCHITETTURA VOCALE",
                      fill="#4093b8",font=("Consolas",max(7,int(r*.052))))
        for ang in (30,120,212,306):
            a=math.radians(ang)
            nx,ny=cx+r*.97*math.cos(a),cy+r*.97*math.sin(a)
            _ellipse(c,nx,ny,2.6,fill="#42cfff")
        self.last_mode="idle"

    def tick(self,phase:float,mode:str,*,connected:bool=False,
             memory:bool=False,listening:bool=False):
        if not self.canvas:
            return
        c=self.canvas
        cx,cy,r=self.geometry
        hue,strength=core_light(mode,phase)
        # Small oscillation while listening or talking; cyan steady when idle.
        amount=strength if mode!="idle" else .23
        self.last_mode=mode
        for item,base,tint in self.core_fill:
            target=hue if mode!="idle" else CYAN
            c.itemconfigure(item,fill=lerp_color(base,target,
                                                  amount*(.14 if mode=="idle"
                                                          else .44)))
        c.itemconfigure(self.rim,
                        outline=lerp_color("#0e72a3",hue,amount),
                        width=2.8+1.2*amount)
        for n,item in enumerate(self.pulse_items):
            rr=r*(.43+n*.11)
            ring_strength=amount*(.56 if n==0 else .31)
            c.itemconfigure(item,outline=lerp_color("#0b3854",hue,ring_strength))
        for item,start,speed,bright in self.arc_items:
            a=(start+phase*speed)%360
            c.itemconfigure(item,start=a)
            if bright:
                c.itemconfigure(item,outline=lerp_color(
                    "#1296d1",hue,amount*.92))
        c.itemconfigure(self.core_name,fill=lerp_color(
            "#e3f8ff",hue,amount*(.35 if mode!="idle" else .04)))
        for item,enabled in zip(self.system_lamps,
                                (listening,connected,memory)):
            c.itemconfigure(item,fill=GREEN if enabled else "#2a5161")


def clip_coast(poly,turn,radius):
    """Clip simplified spherical coast to visible hemisphere."""
    result=[]
    points=list(poly)
    if not points:
        return []
    points.append(points[0])
    for (lon1,lat1),(lon2,lat2) in zip(points[:-1],points[1:]):
        p1=projected_earth_point(lat1,lon1,turn,radius)
        p2=projected_earth_point(lat2,lon2,turn,radius)
        if p1 is not None:
            result.append(p1)
        # Interpolate spherical limb crossing to avoid polygon spikes.
        if (p1 is None) != (p2 is None):
            first,second=0.0,1.0
            for _ in range(8):
                middle=(first+second)/2
                lat=lat1+(lat2-lat1)*middle
                lon=lon1+(lon2-lon1)*middle
                if (projected_earth_point(lat,lon,turn,radius)
                        is not None)==(p1 is not None):
                    first=middle
                else:
                    second=middle
            t=(first+second)/2
            q=projected_earth_point(lat1+(lat2-lat1)*t,
                                    lon1+(lon2-lon1)*t,turn,radius)
            if q is not None:
                result.append(q)
    return result if len(result)>=3 else []


class GlobeArt:
    """Rotating geographic globe, schematic orbit and atmospheric rim."""

    def __init__(self):
        self.canvas=None
        self.earth_coast=[]
        self.earth_lights=[]
        self.land_texture_items=[]
        self.meridians=[]
        self.latitudes=[]
        self.orbits=[]
        self.frame=0

    def build(self,canvas):
        self.canvas=canvas
        c=canvas
        c.delete("all")
        w=max(c.winfo_width(),160)
        h=max(c.winfo_height(),160)
        cx,cy=w*.51,h*.48
        r=max(38,min(w*.46,h*.355,220))
        self.geometry=(cx,cy,r)
        rng=random.Random(20)
        for i in range(28):
            px=rng.randint(4,max(5,int(w-4)))
            py=rng.randint(4,max(5,int(h-4)))
            c.create_oval(px,py,px+1.3,py+1.3,
                          outline="",fill="#174b69")
        c.create_text(13,16,text="TERMINALE  //  TERRA",
                      anchor="w",fill=CYAN,font=("Consolas",10,"bold"))
        c.create_line(12,31,w-12,31,fill="#124b6e")
        # Multiple dark fills give the water much more depth than wireframe.
        for i in range(11,0,-1):
            q=r*(1.035+(11-i)*.004)
            _ellipse(c,cx,cy,q,fill=lerp_color(
                "#02172b","#164e6c",(11-i)/22))
        _ellipse(c,cx,cy,r,fill="#061b31",outline="#36baf5",width=2)
        for i in range(5,0,-1):
            inner_r=r*(.78 +i*.032)
            _ellipse(c,cx,cy,inner_r,
                     fill=lerp_color("#0b2a45","#032039",i/6))
        self.latitudes=[c.create_line(0,0,1,1,fill="#134c70",
                                       smooth=True,width=1)
                        for _ in (-60,-40,-20,0,20,40,60)]
        self.meridians=[c.create_line(0,0,1,1,fill="#125578",
                                       smooth=True,width=1)
                        for _ in range(10)]
        self.earth_coast=[
            c.create_polygon(0,0,1,0,1,1,fill="#16486b",
                             outline="#3f9dcc",width=1,
                             smooth=False) for _ in COASTS
        ]
        # Sparse terrain texture creates visible continental depth while
        # remaining far cheaper than redrawing a raster globe on the old i3.
        tones=("#257497","#3f8baa","#70b3bf","#5585a3")
        self.land_texture_items=[
            _ellipse(c,-8,-8,.7,fill=tones[i%len(tones)])
            for i in range(len(LAND_TEXTURE))
        ]
        self.earth_lights=[_ellipse(c,-8,-8,1.3,
                                    fill="#ead6a2") for _ in LIGHTS]
        # Front transparent-looking equator and orbiting cyan paths.
        self.orbits=[
            c.create_arc(cx-r*1.14,cy-r*.36,cx+r*1.14,cy+r*.36,
                         start=10,extent=170,outline="#258ec9",
                         width=1,style="arc"),
            c.create_arc(cx-r*1.20,cy-r*.5,cx+r*1.20,cy+r*.5,
                         start=185,extent=160,outline="#2385b1",
                         width=1,style="arc"),
        ]
        _ellipse(c,cx,cy,r*1.015,outline="#2992c1",width=1)
        c.create_text(cx,max(40,cy-r-23),
                      text="ROTATION  //  ACTIVE",fill="#63b5d0",
                      font=("Consolas",8))
        # Radar scanner and satellite ornament, as in the approved concept.
        px,py=w-40,62
        c.create_polygon(px-13,py-5,px-5,py-13,px+6,py-3,
                         px-2,py+5,fill="#123b61",outline="#47bfff")
        c.create_rectangle(px-27,py-17,px-16,py-7,
                           fill="#072a4b",outline="#3ea8d7")
        c.create_rectangle(px+6,py+9,px+18,py+19,
                           fill="#072a4b",outline="#3ea8d7")
        # Bottom mini telemetry map, all schematic rather than fake live data.
        by=h-35
        c.create_line(10,by,w-10,by,fill="#0e4563")
        c.create_text(13,by+14,anchor="w",
                      text="PROIEZIONE ORTOGRAFICA",
                      fill="#3e89a5",font=("Consolas",8))
        self.tick(0,force=True)

    def tick(self,phase,*,force=False):
        if not self.canvas:
            return
        self.frame+=1
        if not force and self.frame%3:
            return
        c=self.canvas
        cx,cy,r=self.geometry
        # One full rotation takes several minutes; never block voice commands.
        turn=phase*.045
        for item,poly in zip(self.earth_coast,COASTS):
            visible=clip_coast(poly,turn,r)
            if visible:
                coords=[q for x,y in visible for q in (cx+x,cy+y)]
                c.coords(item,*coords)
                c.itemconfigure(item,state="normal")
            else:
                c.itemconfigure(item,state="hidden")
        for item,(lat,lon) in zip(self.land_texture_items,LAND_TEXTURE):
            p=projected_earth_point(lat,lon,turn,r)
            if p is None:
                c.itemconfigure(item,state="hidden")
            else:
                x,y=cx+p[0],cy+p[1]
                c.coords(item,x-.7,y-.7,x+.7,y+.7)
                c.itemconfigure(item,state="normal")
        for item,(lat,lon) in zip(self.earth_lights,LIGHTS):
            pos=projected_earth_point(lat,lon,turn,r)
            if pos is None:
                c.itemconfigure(item,state="hidden")
            else:
                x,y=cx+pos[0],cy+pos[1]
                c.coords(item,x-1.4,y-1.4,x+1.4,y+1.4)
                c.itemconfigure(item,state="normal")
        for lat,item in zip((-60,-40,-20,0,20,40,60),
                            self.latitudes):
            pts=[]
            for lon in range(-180,181,8):
                p=projected_earth_point(lat,lon,turn,r)
                if p is not None:
                    pts.extend([cx+p[0],cy+p[1]])
            if len(pts)>=4:
                c.coords(item,*pts)
        for j,item in enumerate(self.meridians):
            lon=-180+j*36
            pts=[]
            for lat in range(-85,86,7):
                p=projected_earth_point(lat,lon,turn,r)
                if p is not None:
                    pts.extend([cx+p[0],cy+p[1]])
            if len(pts)>=4:
                c.coords(item,*pts)
            else:
                c.coords(item,0,0,1,1)
        for i,item in enumerate(self.orbits):
            c.itemconfigure(item,start=(phase*5+i*177)%360)
