"""Bus-stop props: street set (sky, city buildings, road behind a sidewalk, bus-stop sign + bench),
commuter guy with backpack (free arms, walk, wet look), bus-app phone card, rain, generic city bus, puddle splash.
From 2026-11-17_0800 "bus app says 1 min away" reel."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, hand, limb, ik, back, seg, lerp, mix, ease)

JACKET = (236, 176, 70)
BAG = (80, 110, 170)
WATER = (120, 170, 235)

def dk(col, d): return mix(col, (0, 0, 0), d)

def street(c, t, gloom=0.0, bus_sign=True):
    """sky gradient is the canvas; draws buildings, road (y 1290-1470), sidewalk, stop sign, bench."""
    for i, (x0, w, h, col) in enumerate([(-200, 300, 760, (190, 150, 140)), (110, 260, 620, (150, 170, 190)),
                                          (380, 330, 820, (200, 180, 150)), (720, 260, 680, (160, 140, 170)),
                                          (990, 300, 780, (180, 160, 140))]):
        y0 = 1290 - h
        c.rect(x0, y0, x0 + w, 1290, dk(col, gloom * 0.45), w=6)
        for wx in range(int(x0) + 36, int(x0 + w) - 40, 70):
            for wy in range(int(y0) + 40, 1240, 90):
                lit = random.Random(wx * 7 + wy).random() < 0.25 + gloom * 0.4
                c.rect(wx, wy, wx + 36, wy + 50, dk((255, 220, 140), 0.1) if lit else dk((120, 140, 170), gloom * 0.4), w=3)
    c.rect(-600, 1290, 1700, 1470, dk((96, 98, 108), gloom * 0.3), ol=None)        # road
    c.line([(-600, 1290), (1700, 1290)], w=6)
    for x in range(-600, 1700, 180):
        c.rect(x, 1372, x + 100, 1386, dk((240, 230, 180), gloom * 0.3), ol=None)
    c.rect(-600, 1470, 1700, 1500, dk((205, 205, 210), gloom * 0.3), w=6)          # curb
    c.rect(-600, 1500, 1700, 2600, dk((176, 176, 184), gloom * 0.3), ol=None)      # sidewalk
    for x in range(-600, 1700, 200):
        c.line([(x, 1500), (x - 60, 2600)], w=4, fill=dk((150, 150, 160), gloom * 0.3), caps=False)
    if bus_sign: stop_sign(c, gloom)

def stop_sign(c, gloom=0.0):
    if True:
        c.rect(905, 1000, 921, 1640, (110, 115, 125), w=5)
        c.rect(840, 900, 990, 1010, dk((60, 120, 200), gloom * 0.3), w=6, r=12)
        c.text(915, 940, "BUS", 34, fill=WHITE, stroke=None); c.text(915, 980, "12", 34, fill=WHITE, stroke=None)
        c.rect(700, 1520, 1040, 1550, dk((150, 100, 60), gloom * 0.3), w=6, r=6)   # bench
        c.rect(720, 1550, 740, 1630, (90, 90, 96), w=4); c.rect(1000, 1550, 1020, 1630, (90, 90, 96), w=4)

def commuter(c, t, x, y, la, ra, eyes="open", mouth="flat", brows=None, look=(0, 0), tilt=0.0, walk=0.0,
             sweat=False, blink=0.0, shake=0.0, wet=0.0, tap=0.0, face=1):
    """commuter in a yellow rain jacket + backpack. head centre (x, y); la / ra = hand targets. face = 1 right / -1 left."""
    r = random.Random(int(t * 30))
    dx, dy = r.uniform(-shake, shake), r.uniform(-shake, shake)
    x += dx; y += dy
    y += abs(math.sin(t * walk * math.pi)) * -10 if walk else 0
    hip = (x, y + 360)
    jk = mix(JACKET, (150, 120, 60), wet * 0.5)
    c.rect(x - face * 120, y + 140, x - face * 50, y + 330, dk(BAG, wet * 0.3), w=6, r=20)  # backpack behind
    for i, side in enumerate((-1, 1)):
        ph = math.sin(t * walk * 2 * math.pi + i * math.pi) if walk else -1
        lift = max(0, ph) * 50
        if tap and side == 1: lift = abs(math.sin(t * tap * math.pi)) * 22
        ft = (x + side * 50 + (ph * 50 * face if walk else 0), 1630 - lift)
        kn = ik(*hip, *ft, 120, 120, bend=(-1 if face > 0 else 1) if walk else -side)
        c.line([hip, kn, ft], w=14)
        c.line([ft, (ft[0] + 34 * face, ft[1] + 2)], w=14)
    c.poly([(x - 64, y + 112), (x + 64, y + 112), (x + 80, y + 372), (x - 80, y + 372)], jk, w=7)
    c.line([(x, y + 120), (x, y + 372)], w=4, caps=False)
    c.line([(x - face * 40, y + 118), (x - face * 54, y + 300)], w=8, fill=dk(BAG, 0.2 + wet * 0.3))  # strap
    la = (la[0] + dx, la[1] + dy); ra = (ra[0] + dx, ra[1] + dy)
    limb(c, (x - 56, y + 150), la, 110, 110, bend=1)
    limb(c, (x + 56, y + 150), ra, 110, 110, bend=-1)
    head(c, x, y, 108, tilt=tilt, eyes=eyes, mouth=mouth, look=look, brows=brows, t=t, sweat=sweat, blink=blink)
    if wet > 0:  # flat wet hair + drips
        c.chord(x - 100, y - 112, x + 100, y + 20, 190, 350, dk((90, 70, 55), 0.1), w=6)
        for i in range(4):
            ph = (t * 1.4 + i * 0.27) % 1
            px = x + (-80, -30, 40, 85)[i]
            c.ell(px - 8, y + 60 + ph * 140 - 12, px + 8, y + 60 + ph * 140 + 12, WATER, w=3)
    else:
        for i in range(5):
            a = math.pi * (1.1 + i * 0.2)
            c.circ(x + math.cos(a) * 96, y + math.sin(a) * 96, 26, (90, 70, 55), w=5)
    return la, ra

def phone_in_hand(c, x, y, glow=True):
    c.rect(x - 30, y - 54, x + 30, y + 54, (40, 40, 48), w=5, r=10)
    c.rect(x - 22, y - 44, x + 22, y + 42, (150, 200, 255) if glow else (60, 60, 70), ol=None, r=6)
    if glow: c.glow(x, y, 130, (150, 200, 255), 0.22)

def app_card(c, x, y, t, start, big, small="BUS 12 - Downtown", col=(60, 190, 110), shake=0.0, sz=88):
    """big floating bus-app card (screen space)."""
    k = back(seg(t, start, start + 0.3))
    if k <= 0.01: return
    j = math.sin(t * 50) * shake
    with c.ui():
        w, h = 400 * k, 270 * k
        c.rect(x - w / 2 + j, y - h / 2, x + w / 2 + j, y + h / 2, WHITE, w=7, r=34 * k)
        c.rect(x - w / 2 + j, y - h / 2, x + w / 2 + j, y - h / 2 + 70 * k, (60, 120, 200), w=7, r=34 * k)
        c.rect(x - w / 2 + j + 4, y - h / 2 + 40 * k, x + w / 2 + j - 4, y - h / 2 + 70 * k, (60, 120, 200), ol=None)
        c.text(x + j, y - h / 2 + 36 * k, small, 30 * k, fill=WHITE, stroke=None)
        c.text(x + j, y + 34 * k, big, sz * k, fill=col, stroke=None)

def rain(c, t, amt=1.0, seed=0):
    n = int(70 * amt)
    for i in range(n):
        rr = random.Random(i + seed * 1000)
        x0 = rr.uniform(-200, 1300); sp = rr.uniform(1.6, 2.4); ph = (t * sp + rr.random()) % 1
        y0 = lerp(300, 1900, ph)
        c.line([(x0, y0), (x0 - 14, y0 + 60)], w=4, fill=(200, 220, 250), caps=False)

def bus(c, x, y=1460, shake=0.0):
    """generic city bus, bottom of wheels at y, front at the left (x = front)."""
    j = math.sin(x * 0.05) * shake
    c.rect(x, y - 520 + j, x + 1000, y - 70 + j, (70, 150, 220), w=8, r=40)
    c.rect(x, y - 200 + j, x + 1000, y - 150 + j, WHITE, w=5)
    for i in range(5):
        c.rect(x + 150 + i * 165, y - 470 + j, x + 290 + i * 165, y - 290 + j, (190, 225, 250), w=6, r=12)
    c.rect(x + 20, y - 470 + j, x + 120, y - 120 + j, (190, 225, 250), w=6, r=10)   # front door
    c.rect(x + 30, y - 510 + j, x + 220, y - 478 + j, (30, 30, 36), w=4, r=6)
    c.text(x + 125, y - 494 + j, "12", 26, fill=(255, 190, 60), stroke=None)
    for wx in (x + 180, x + 820):
        c.circ(wx, y - 60, 62, (40, 40, 46), w=7); c.circ(wx, y - 60, 24, (170, 170, 180), w=5)

def puddle(c, x, y, w=260):
    c.ell(x - w / 2, y - 22, x + w / 2, y + 22, (110, 140, 190), w=5)

def splash(c, t, start, x, y, toward=-1, dur=0.9):
    k = seg(t, start, start + dur)
    if k <= 0 or k >= 1: return
    for i in range(34):
        rr = random.Random(i + 77)
        vx = toward * rr.uniform(80, 420); vy = -rr.uniform(700, 1500)
        px, py = x + vx * k, y + vy * k + 1700 * k * k
        s = rr.uniform(18, 40) * (1 - k * 0.4)
        c.ell(px - s, py - s * 1.3, px + s, py + s * 1.3, WATER, w=4)
