"""Quiet-morning props: free-arm pajama guy (tiptoe walk, arms set per pose), spoon, cereal box + bowl,
microwave with beeping display, roommate peeking from a door (messy dark hair, green tee), sound-word burst.
From 2026-11-17_0600 "trying to be quiet at 6am" reel."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, hand, limb, ik, back, seg, lerp, mix, ease)

PJ = (130, 160, 220)
YEL = (255, 220, 60)

def quiet_guy(c, t, x, y, la, ra, eyes="open", mouth="flat", brows=None, look=(0, 0), tilt=0.0, walk=0.0,
              sweat=False, blink=0.0, shake=0.0, freeze=False):
    """pajama guy, head centre (x, y). la / ra = left / right hand target points (absolute)."""
    r = random.Random(int(t * 30))
    dx, dy = r.uniform(-shake, shake), r.uniform(-shake, shake)
    x += dx; y += dy
    hip = (x, y + 360)
    for i, side in enumerate((-1, 1)):
        ph = math.sin(t * walk * 2 * math.pi + i * math.pi) if walk else -1
        if freeze: ph = 0.6 if i == 0 else -1
        lift = max(0, ph) * 60
        ft = (x + side * 55 + (ph * 36 if walk else 0), 1630 - lift)
        kn = ik(*hip, *ft, 120, 120, bend=-1 if (walk or freeze) else -side)
        c.line([hip, kn, ft], w=14)
        c.line([ft, (ft[0] + 34, ft[1] + 2 - (12 if lift > 5 else 0))], w=14)
    c.poly([(x - 62, y + 112), (x + 62, y + 112), (x + 74, y + 370), (x - 74, y + 370)], PJ, w=7)
    for yy in (y + 180, y + 260, y + 340): c.line([(x - 66, yy), (x + 70, yy)], w=4, fill=(230, 235, 250), caps=False)
    la = (la[0] + dx, la[1] + dy); ra = (ra[0] + dx, ra[1] + dy)
    limb(c, (x - 55, y + 150), la, 110, 110, bend=1)
    limb(c, (x + 55, y + 150), ra, 110, 110, bend=-1)
    head(c, x, y, 108, tilt=tilt, eyes=eyes, mouth=mouth, look=look, brows=brows, t=t, sweat=sweat, blink=blink)
    return la, ra

def burst(c, x, y, s, t, start, sz=110, fill=YEL, wob=True):
    k = back(seg(t, start, start + 0.2))
    if k <= 0.01: return
    j = math.sin(t * 40) * 6 if wob else 0
    c.text(x + j, y, s, sz * k, fill=fill, sw=11)

def spoon(c, x, y, a):
    ex, ey = x + math.cos(a) * 90, y + math.sin(a) * 90
    c.line([(x, y), (ex, ey)], w=16, fill=INK); c.line([(x, y), (ex, ey)], w=8, fill=(200, 205, 215))
    c.ell(ex - 22, ey - 15, ex + 22, ey + 15, (200, 205, 215), w=5)

def bowl(c, x, y, fill=0.0):
    c.chord(x - 110, y - 80, x + 110, y + 70, 0, 180, (250, 250, 255), w=7)
    if fill > 0:
        for i in range(int(fill * 14)):
            rr = random.Random(i)
            c.circ(x + rr.uniform(-80, 80), y - 4 - rr.uniform(0, 26) * fill, 13, (235, 170, 70), w=4)

def cereal_box(c, x, y, a):
    pts = [(-70, -120), (70, -120), (70, 120), (-70, 120)]
    P = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) for px, py in pts]
    c.poly(P, (240, 90, 90), w=7)
    c.circ(x, y, 40, (255, 220, 120), w=5)

def microwave(c, x, y, t, beep=False):
    c.rect(x - 200, y - 230, x + 200, y, (225, 228, 235), w=8, r=14)
    c.rect(x - 175, y - 205, x + 70, y - 25, (60, 70, 90), w=6, r=8)
    on = beep and (t * 6) % 1 < 0.6
    c.rect(x + 95, y - 200, x + 180, y - 150, (30, 30, 36), w=4, r=6)
    c.text(x + 137, y - 175, "0:00", 26, fill=(120, 255, 140) if on else (40, 90, 50), stroke=None)
    for i in range(3):
        c.circ(x + 115 + i * 22, y - 110, 8, (180, 184, 196), w=3)
    if on: c.glow(x + 137, y - 175, 110, (120, 255, 140), 0.25)

def roommate(c, t, x, y, peek=1.0, mouth="smile", eyes="half"):
    """roommate head + shoulder leaning out from the right edge of a door at x."""
    hx = lerp(x + 120, x - 40, ease(peek))
    c.poly([(hx - 60, y + 110), (hx + 120, y + 110), (hx + 140, y + 400), (hx - 70, y + 400)], (110, 190, 130), w=7)
    head(c, hx, y, 100, tilt=-0.18, eyes=eyes, mouth=mouth, look=(-1, 0), t=t)
    for i in range(6):  # messy hair tufts
        a = math.pi * (1.05 + i * 0.16)
        bx, by = hx + math.cos(a - 0.18) * 92, y + math.sin(a - 0.18) * 92
        c.circ(bx, by, 34, (60, 46, 40), w=5)
