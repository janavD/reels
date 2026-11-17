"""Extra funny reel: opening the fridge every 10 minutes hoping new food spawned."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, SKIN, WHITE, head, limb, hand, ik, floor, label, sub, caption, punch, blinkf, back,
                 ease, eout, seg, lerp, mix, rot, star, bubble)
from PIL import Image

rig.CAP = ['me opening the fridge', 'every 10 minutes like', 'new food spawned']

KITCH = ((214, 232, 226), (186, 208, 200))   # mint kitchen wall
RED = (225, 70, 70)
LEMON = (250, 220, 70)
FX0, FX1, FY0, FY1 = 120, 560, 800, 1640    # fridge box

# ---------- set ----------
def wallclock(c, x, y, mins):
    c.circ(x, y, 74, WHITE, w=7)
    for i in range(12):
        a = i * math.pi / 6
        c.line([(x + math.cos(a) * 56, y + math.sin(a) * 56), (x + math.cos(a) * 64, y + math.sin(a) * 64)], w=4, caps=False)
    hr = (1 + mins / 60) / 12 * 2 * math.pi - math.pi / 2
    mn = mins / 60 * 2 * math.pi - math.pi / 2
    c.line([(x, y), (x + math.cos(hr) * 34, y + math.sin(hr) * 34)], w=8)
    c.line([(x, y), (x + math.cos(mn) * 52, y + math.sin(mn) * 52)], w=6, fill=RED)
    c.circ(x, y, 7, INK, ol=None)

def kitchen(c, t, mins):
    # backsplash tiles
    for yy in range(1140, 1300, 50):
        for xx in range(600, 1160, 70):
            c.rect(xx, yy, xx + 70, yy + 50, (238, 244, 246), w=3)
    # upper cabinets
    for x0 in (640, 870):
        c.rect(x0, 470, x0 + 220, 760, (236, 196, 140), w=7, r=8)
        c.line([(x0 + 110, 520), (x0 + 110, 710)], w=8)
    # counter
    c.rect(590, 1300, 1160, 1340, (120, 124, 136), w=7)
    c.rect(610, 1340, 1140, 1600, (230, 190, 134), w=7)
    for x0 in (610, 875):
        c.rect(x0 + 20, 1360, x0 + 245, 1580, (240, 204, 152), w=5, r=6)
        c.line([(x0 + 110, 1450), (x0 + 150, 1450)], w=8)
    # stuff on counter: kettle + plant
    c.rect(1010, 1200, 1100, 1300, (230, 90, 90), w=6, r=20); c.line([(1020, 1200), (1055, 1160), (1090, 1200)], w=8, caps=False)
    wallclock(c, 340, 640, mins)
    floor(c, False)

def lemon(c, x, y, face=None, t=0.0, shake=0.0):
    x += math.sin(t * 30) * 8 * shake
    s = 1.45
    c.ell(x - 46 * s, y - 34 * s, x + 46 * s, y + 34 * s, LEMON, w=6)
    c.circ(x + 48 * s, y - 2, 9, LEMON, w=4)
    c.line([(x - 4, y - 34 * s), (x + 8, y - 52 * s)], w=6)
    if face == "meh":
        c.line([(x - 30, y - 8), (x - 10, y - 8)], w=6); c.line([(x + 10, y - 8), (x + 30, y - 8)], w=6)
        c.line([(x - 14, y + 20), (x + 14, y + 20)], w=6)
    elif face == "talk":
        c.circ(x - 20, y - 8, 8, INK, ol=None); c.circ(x + 20, y - 8, 8, INK, ol=None)
        o = abs(math.sin(t * 18)) * 10
        c.ell(x - 12, y + 8, x + 12, y + 18 + o, INK, ol=None)

def ketchup(c, x, y):  # y = shelf top
    c.rect(x - 28, y - 120, x + 28, y, RED, w=6, r=14)
    c.rect(x - 14, y - 150, x + 14, y - 118, WHITE, w=5, r=4)
    c.rect(x - 20, y - 82, x + 20, y - 46, WHITE, w=3, r=4)

def jar(c, x, y):
    c.rect(x - 40, y - 90, x + 40, y, (205, 230, 210), w=6, r=10)
    c.rect(x - 44, y - 110, x + 44, y - 88, (110, 160, 90), w=5, r=4)
    c.ell(x - 26, y - 32, x + 4, y - 6, (110, 170, 80), w=3)   # one sad pickle

SHELVES = (1060, 1270, 1480)
def fridge(c, t, k, mins_light=True, lemon_xy=None, lemon_face=None, lemon_shake=0.0, jar_on=True):
    """k = door open amount 0..1"""
    if k > 0.02:
        c.rect(FX0, FY0, FX1, FY1, (232, 232, 236), w=8, r=26)
        c.rect(FX0 + 22, FY0 + 22, FX1 - 22, FY1 - 40, (255, 250, 226), w=5, r=12)
        c.rect(FX0 + 22, FY0 + 22, FX1 - 22, FY0 + 230, (240, 244, 250), w=5, r=12)  # freezer box
        c.line([(FX0 + 22, FY0 + 230), (FX1 - 22, FY0 + 230)], w=6)
        for sy in SHELVES: c.line([(FX0 + 22, sy), (FX1 - 22, sy)], w=6, fill=(170, 200, 220))
        ketchup(c, 220, SHELVES[0])
        if jar_on: jar(c, 300, SHELVES[2])
        if lemon_xy is None: lemon(c, 410, SHELVES[1] - 50, lemon_face, t, lemon_shake)
        c.glow(340, 1200, 420, (255, 248, 200), 0.45 * k)
        # door panel swung open toward the left edge
        ex = lerp(FX1, FX0 - 100, k)
        pts = [(FX0, FY0), (ex, FY0 - 30 * k), (ex, FY1 + 10 * k), (FX0, FY1)]
        c.poly(pts, (246, 246, 250), w=8)
        if k < 0.7:
            hx = lerp(ex, FX0, 0.12); c.line([(hx, 1000), (hx, 1180)], w=14, fill=(170, 170, 180))
    else:
        c.rect(FX0, FY0, FX1, FY1, (246, 246, 250), w=8, r=26)
        c.line([(FX0, FY0 + 250), (FX1, FY0 + 250)], w=6)
        c.line([(FX1 - 50, 1100), (FX1 - 50, 1280)], w=14, fill=(170, 170, 180))
        c.line([(FX1 - 50, 860), (FX1 - 50, 980)], w=14, fill=(170, 170, 180))
        # magnets
        c.circ(220, 900, 18, (90, 160, 230), w=4); c.rect(250, 1100, 340, 1190, WHITE, w=4)
        c.circ(295, 1095, 12, RED, w=3)

def person(c, x, y, t, armL=None, armR=None, shirt=(240, 150, 70), walk=0.0):
    hip = (x, y + 360)
    c.ell(x - 140, 1625, x + 140, 1655, mix((178, 128, 86), (0, 0, 0), 0.25), ol=None)
    for side in (-1, 1):
        ph = math.sin(t * 14 + (0 if side < 0 else math.pi)) * walk
        fx = x + side * 60 + ph * 60; fy = 1630 - max(0, ph) * 60
        limb(c, hip, (fx, fy), 118, 118, bend=side)
        c.line([(fx, fy), (fx + side * 40, fy + 2)], w=14)
    c.line([(x, y + 105), hip], w=14)
    c.poly([(x - 55, y + 135), (x + 55, y + 135), (x + 70, y + 210), (x + 42, y + 215), (x + 40, y + 340),
            (x - 40, y + 340), (x - 42, y + 215), (x - 70, y + 210)], shirt, w=6)
    sh = (x, y + 170)
    for tgt, b in ((armL, 1), (armR, -1)):
        if tgt is None: continue
        limb(c, sh, tgt, 115, 115, bend=b); hand(c, *tgt, 22)

PX, PY = 780, 1050
def base(t, mins, z, cx=560, cy=1180, shake=0.0):
    r = random.Random(int(t * 30))
    c = C(*KITCH, cam=(cx + r.uniform(-shake, shake), cy + r.uniform(-shake, shake), z))
    kitchen(c, t, mins)
    return c

def door_k(t, a, b):
    return eout(seg(t, a, b))

# ---------- scenes ----------
def s_first(t, dur=3.2):
    z = punch(t, lerp(1.0, 1.08, ease(t / dur)))
    c = base(t, 0, z)
    k = door_k(t, 0.4, 0.8)
    fridge(c, t, k)
    reach = (lerp(FX1 - 50, FX1 - 10, k), 1160)
    hum = math.sin(t * 6) * 0.04
    person(c, PX, PY, t, armL=reach if t < 1.6 else (PX - 60, PY + 330), armR=(PX + 50, PY + 330))
    look = (-1, 0.2) if t > 0.8 else (-0.5, 0)
    head(c, PX, PY, 110, tilt=hum, eyes="open", mouth="smile" if t < 1.2 else "flat", look=look,
         blink=blinkf(t, 2.4, 0.3), brows=None if t < 1.2 else 0.15, t=t)
    caption(c); label(c, t, "1:00 PM"); sub(c, t, "nothing to eat", 1.3)
    return c.out()

def s_second(t, dur=2.6):
    z = punch(t, lerp(1.08, 1.2, ease(t / dur)))
    c = base(t, 10, z, cx=500)
    fridge(c, t, door_k(t, 0.0, 0.3))
    lean = ease(seg(t, 0.4, 1.0))
    x = PX - 90 * lean; y = PY + 30 * lean
    person(c, x, y, t, armL=(FX1 - 40, 1080), armR=(x + 50, y + 330))
    head(c, x - 10 * lean, y, 110, tilt=-0.18 * lean, eyes="half" if lean > 0.5 else "open", mouth="flat",
         look=(-1, 0.3), brows=0.3 * lean, t=t)
    if lean > 0.9:
        for i in range(3):
            k = back(seg(t, 1.2 + i * 0.2, 1.4 + i * 0.2))
            if k > 0.01: c.text(x + 120 + i * 40, y - 150 - i * 20, "?", 80 * k, fill=WHITE, sw=9)
    caption(c); label(c, t, "1:10 PM"); sub(c, t, "maybe i missed something", 0.9)
    return c.out()

def s_third(t, dur=2.8):
    z = punch(t, lerp(1.1, 1.22, ease(t / dur)))
    c = base(t, 20, z, cx=520)
    grab = ease(seg(t, 0.3, 0.8))
    lifted = t > 0.8
    fridge(c, t, 1.0, lemon_xy=(1, 1) if lifted else None)
    # left hand reaches in, grabs the lemon, holds it up to face
    if not lifted:
        tgt = (lerp(PX - 60, 440, grab), lerp(PY + 300, SHELVES[1] - 40, grab))
    else:
        up = eout(seg(t, 0.8, 1.2))
        tgt = (lerp(440, PX - 170, up), lerp(SHELVES[1] - 40, PY - 20, up))
    person(c, PX, PY, t, armL=tgt, armR=(PX + 50, PY + 330))
    if lifted: lemon(c, tgt[0] - 10, tgt[1] - 60, None, t)
    sad = t > 1.3
    head(c, PX, PY, 110, tilt=0.12 if sad else 0, eyes="open", mouth="frown" if sad else "o", look=(-1, -0.2),
         brows=-0.3 if sad else None, blink=blinkf(t, 2.0, 0.6), t=t)
    caption(c); label(c, t, "1:20 PM"); sub(c, t, "lemon. again.", 1.3)
    return c.out()

def s_fourth(t, dur=3.0):
    open_t = 1.0
    sh = 6 if t > open_t + 0.5 else 0
    z = lerp(1.0, 1.15, ease(seg(t, 0, open_t))) if t < open_t + 0.5 else 1.15 + 0.05 * ease(seg(t, open_t + 0.5, dur))
    c = base(t, 30, z, cx=520, shake=sh)
    k = door_k(t, open_t, open_t + 0.45)
    fridge(c, t, k)
    # praying hands before opening, then reach
    if t < open_t:
        hands = (PX + math.sin(t * 20) * 4, PY + 190)
        person(c, PX, PY, t, armL=(hands[0] - 14, hands[1]), armR=(hands[0] + 14, hands[1]))
        head(c, PX, PY, 110, tilt=-0.05, eyes="closed", mouth="flat", brows=-0.35, t=t)
        bubble(c, PX - 40, PY - 230, "please please", t, 0.15)
    else:
        reach = (lerp(FX1 - 50, FX1 - 10, k), 1160) if t < open_t + 0.5 else (PX - 60, PY + 330)
        person(c, PX, PY, t, armL=reach, armR=(PX + 50, PY + 330))
        hope = t < open_t + 0.5
        head(c, PX, PY, 110, eyes="wide", mouth="grin" if hope else "frown", look=(-1, 0), brows=-0.3 if hope else 0.4,
             t=t, sweat=not hope)
        if hope:
            for i in range(4):
                a = t * 5 + i * math.pi / 2
                star(c, 340 + math.cos(a) * 200, 1150 + math.sin(a) * 200, 34)
    caption(c); label(c, t, "1:30 PM")
    if t > open_t + 0.5: sub(c, t, "SAME. EXACT. STUFF.", open_t + 0.5)
    return c.out()

def s_lemon(t, dur=4.4):
    close_a, close_b = 1.9, 2.15
    reopen_a, reopen_b = 3.05, 3.25
    if t < close_a:
        k = 1.0
    elif t < reopen_a:
        k = 1 - ease(seg(t, close_a, close_b))
    else:
        k = eout(seg(t, reopen_a, reopen_b))
    z = punch(t, lerp(1.12, 1.2, ease(t / dur)))
    slam = close_b < t < close_b + 0.2
    c = base(t, 40, z, cx=500, shake=12 if slam else 0)
    talking = 0.4 < t < 1.8
    face = "talk" if talking else "meh"
    fridge(c, t, k, lemon_face=face if (t < close_a or t > reopen_b) else None, lemon_shake=1.0 if 0.4 < t < 0.9 else 0)
    if t < close_a:
        person(c, PX, PY, t, armL=(PX - 60, PY + 330), armR=(PX + 50, PY + 330))
        head(c, PX, PY, 110, eyes="wide" if talking else "open", mouth="o" if talking else "flat", look=(-1, 0.3),
             brows=0.2, t=t)
        bubble(c, 400, 860, "bro. it's just me", t, 0.45)
    elif t < reopen_a:
        walk = seg(t, 2.3, 2.9)
        x = PX + 120 * ease(walk) - 120 * ease(seg(t, 2.85, 3.05))
        push = 1 - ease(seg(t, close_b, close_b + 0.3))
        person(c, x, PY, t, armL=(lerp(x - 60, FX1 - 40, push), lerp(PY + 330, 1150, push)), armR=(x + 50, PY + 330),
               walk=1.0 if 2.3 < t < 2.85 else 0.0)
        head(c, x, PY, 110, eyes="closed" if t < 2.6 else "open", mouth="flat", look=(-1, 0), brows=0.2, t=t)
        if slam: c.text(FX1 - 20, 960, "SLAM", 90 * back(seg(t, close_b, close_b + 0.12)), fill=WHITE, sw=10)
        if t > 2.85:
            c.text(PX + 140, PY - 170, "!", 120 * back(seg(t, 2.85, 3.0)), fill=(255, 220, 60), sw=10)
    else:
        reach = (lerp(FX1 - 50, FX1 - 10, k), 1160)
        person(c, PX, PY, t, armL=reach, armR=(PX + 50, PY + 330))
        head(c, PX, PY, 110, eyes="open", mouth="grin", look=(-1, 0), brows=-0.25, t=t, blink=blinkf(t, 2.5))
    caption(c); label(c, t, "1:40 PM")
    if t > reopen_a: sub(c, t, "ok one more check", reopen_a + 0.05)
    return c.out()

SCENES = [
    ("f1", 3.2, s_first),
    ("f2", 2.6, s_second),
    ("f3", 2.8, s_third),
    ("f4", 3.0, s_fourth),
    ("f5", 4.4, s_lemon),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"f1": [0.3, 2.0], "f2": [1.6], "f3": [0.6, 1.8], "f4": [0.5, 1.3, 2.4], "f5": [1.0, 2.2, 2.95, 3.8]}
        ims = [fn(tt).resize((270, 480)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (270 * 6, 480 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 6) * 270, (i // 6) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
