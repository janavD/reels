"""Guitar props: acoustic guitar (any angle via U/N), seated guitar player on a bed edge (strum + fret hand,
or free hands), leaning guitar, music notes (sour grey / colourful, floating), metronome, phone, bedroom door that
opens, mom peeking (bun, thumbs up), rain cloud of doubt, red sore fingertips, day card, timed subtitle helper subs().
From 2026-11-17_0700 "day 1 vs day 90 of learning guitar" reel (also has an open-mic stage scene in work/)."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, limb, hand, ik, back, seg, lerp, mix, ease, floor, window, shelf, bed, star)
from night_noise import cat

TEE = (90, 170, 150)
WOOD = (214, 140, 66)
NECK = (120, 74, 44)
GOLD = (255, 205, 60)
RED = (230, 80, 80)
STAGE = ((44, 30, 70), (20, 16, 36))
NCOL = [(255, 120, 120), (120, 190, 255), GOLD, (130, 220, 150), (210, 140, 240)]
ANG = math.radians(200)
U = (math.cos(ANG), math.sin(ANG)); N = (-U[1], U[0])

def gp(B, a, b=0.0): return (B[0] + U[0] * a + N[0] * b, B[1] + U[1] * a + N[1] * b)

# ---------- props ----------
def daycard(c, n, night=False):
    c.rect(70, 450, 250, 660, WHITE if not night else (200, 200, 215), w=6, r=12)
    c.rect(70, 450, 250, 505, (70, 150, 220), w=6, r=12)
    c.text(160, 478, "DAY", 26, fill=WHITE, stroke=None)
    c.text(160, 582, str(n), 72 if n < 100 else 60, fill=INK, stroke=None)

def guitar(c, B, shake=0.0):
    Bx = (B[0] + shake, B[1])
    for a, r in ((-45, 112), (75, 86)):
        x, y = gp(Bx, a); c.circ(x, y, r, WOOD, w=7)
    x, y = gp(Bx, -45); c.circ(x, y, 104, WOOD, ol=None)
    x, y = gp(Bx, 15); c.circ(x, y, 34, (70, 40, 26), w=5)
    c.line([gp(Bx, 150), gp(Bx, 440)], w=40, fill=INK); c.line([gp(Bx, 150), gp(Bx, 440)], w=28, fill=NECK)
    for f in range(170, 440, 45): c.line([gp(Bx, f, -14), gp(Bx, f, 14)], w=3, fill=(220, 210, 190), caps=False)
    hp = [gp(Bx, 430, -26), gp(Bx, 430, 26), gp(Bx, 510, 22), gp(Bx, 510, -22)]
    c.poly(hp, NECK, w=6)
    for k in (450, 480):
        for s in (-1, 1):
            x, y = gp(Bx, k, s * 34); c.circ(x, y, 7, (230, 230, 230), w=3)
    bx, by = gp(Bx, -110); c.line([gp(Bx, -110, -30), gp(Bx, -110, 30)], w=12)
    for s in (-9, -3, 3, 9): c.line([gp(Bx, -110, s), gp(Bx, 435, s)], w=2, fill=(240, 240, 240), caps=False)

def leaning_guitar(c, x, y):
    """guitar leaning against the bed, standing on the floor."""
    old = (U, N)
    c.ell(x - 110, y - 10, x + 110, y + 14, (0, 0, 0, 0), ol=None) if False else None
    g = globals(); g['U'] = (math.cos(math.radians(-78)), math.sin(math.radians(-78))); g['N'] = (-g['U'][1], g['U'][0])
    guitar(c, (x, y - 150))
    g['U'], g['N'] = old

def note(c, x, y, s=1.0, col=GOLD, sour=False, a=0.0):
    col = (150, 150, 150) if sour else col
    hx, hy = x + math.sin(a) * 8 * s, y
    c.ell(hx - 24 * s, hy - 17 * s, hx + 24 * s, hy + 17 * s, col, w=5)
    top = (hx + 20 * s + (18 * s if sour else 0), hy - 95 * s)
    c.line([(hx + 20 * s, hy - 4 * s), top], w=7 * s)
    c.line([top, (top[0] + 34 * s, top[1] + (40 if not sour else 10) * s)], w=7 * s)

def float_notes(c, t, x, y, n=5, sour=False, spd=0.7, spread=320, seed=0):
    for i in range(n):
        r = random.Random(seed * 31 + i)
        ph = (t * spd + i / n) % 1
        side = -1 if i % 2 else 1
        nx = x + side * r.uniform(190, 190 + spread / 2) + math.sin(t * 3 + i) * 30
        ny = y - ph * 420
        s = 0.7 + 0.5 * math.sin(ph * math.pi)
        note(c, nx, ny, s, NCOL[i % 5], sour=sour, a=t * 8 + i if sour else 0)

def metronome(c, x, y, t, bpm=60):
    c.poly([(x - 55, y), (x + 55, y), (x + 25, y - 170), (x - 25, y - 170)], (150, 90, 60), w=6)
    a = math.sin(t * math.pi * bpm / 60) * 0.5
    c.line([(x, y - 20), (x + math.sin(a) * 140, y - 20 - math.cos(a) * 140)], w=6)
    c.circ(x + math.sin(a) * 100, y - 20 - math.cos(a) * 100, 12, GOLD, w=4)

def phone(c, x, y, glow=True):
    c.rect(x - 34, y - 60, x + 34, y + 60, (40, 40, 48), w=5, r=10)
    c.rect(x - 26, y - 50, x + 26, y + 48, (150, 200, 255) if glow else (60, 60, 70), ol=None, r=6)
    if glow: c.glow(x, y, 160, (150, 200, 255), 0.25)

def door(c, x0=660, open_k=0.0, night=False):
    c.rect(x0, 600, x0 + 320, 1300, (250, 244, 232), w=7)
    c.rect(x0 + 24, 624, x0 + 296, 1300, (70, 60, 60), ol=None)
    w = 272 * (1 - 0.55 * open_k)
    c.rect(x0 + 24, 624, x0 + 24 + w, 1300, (196, 140, 96), w=6)
    c.circ(x0 + 24 + w - 30, 960, 12, GOLD, w=4)

def mom(c, x, y, t, mouth="smile", eyes="happy", thumb=0.0):
    c.circ(x + 10, y - 120, 58, (90, 60, 50), w=6)  # bun
    c.ell(x - 125, y - 115, x + 125, y + 40, (90, 60, 50), w=6)
    c.poly([(x - 80, y + 100), (x + 80, y + 100), (x + 100, y + 340), (x - 100, y + 340)], (220, 120, 170), w=7)
    head(c, x, y, 100, eyes=eyes, mouth=mouth, t=t, blush=True)
    if thumb > 0.01:
        hx, hy = x + 140, lerp(y + 300, y + 120, back(thumb))
        limb(c, (x + 70, y + 160), (hx, hy), 90, 90, bend=1)
        hand(c, hx, hy, 24, thumb=-math.pi / 2)

def cloud(c, t, cx, cy):
    cx += math.sin(t * 2) * 10
    for dx, r in ((-50, 45), (0, 60), (55, 45)): c.circ(cx + dx, cy, r, (150, 155, 175), ol=None)
    for i in range(5):
        ph = (t * 2.2 + i / 5) % 1
        c.line([(cx - 60 + i * 30, cy + 40 + ph * 90), (cx - 64 + i * 30, cy + 60 + ph * 90)], w=5, fill=(150, 200, 255))

# ---------- guy ----------
def player(c, t, x=600, y=975, strum=0.0, fret=330, guitar_on=True, la=None, ra=None, shake=0.0, bob=0.0, **face):
    """seated on the bed edge (hips ~y+360). strum = strum speed (Hz), la/ra override hand targets."""
    r = random.Random(int(t * 30))
    dx = r.uniform(-shake, shake)
    y += math.sin(t * 6) * bob
    hipy = 1335
    for side in (-1, 1):
        kn = (x + side * 75, 1420); ft = (x + side * 90, 1630)
        c.line([(x + side * 40, hipy), kn, ft], w=14); c.line([ft, (ft[0] + side * 36, ft[1] + 2)], w=14)
    c.poly([(x - 64, y + 112), (x + 64, y + 112), (x + 82, hipy + 10), (x - 82, hipy + 10)], TEE, w=7)
    B = (x + 60 + dx, y + 320)
    if guitar_on:
        guitar(c, B)
        sp = math.sin(t * strum * 2 * math.pi) if strum else -0.3
        ra = ra or gp(B, -5, sp * 45)
        la = la or gp(B, fret + math.sin(t * 2.3) * 8, -24)
    limb(c, (x + 55, y + 150), ra, 120, 120, bend=-1)
    limb(c, (x - 55, y + 150), la, 120, 120, bend=-1 if guitar_on else 1)
    hand(c, *ra, 22); hand(c, *la, 22)
    head(c, x + dx, y, 108, t=t, **face)
    return B

def bedroom(c, t, day, night=False, cat_x=None, cat_eyes="open", win=True):
    if win: window(c, night, t)
    shelf(c, night); daycard(c, day, night); floor(c, night); bed(c, night)
    if cat_x is not None: cat(c, cat_x, 1312, t, eyes=cat_eyes, s=0.72, d=0.35 if night else 0)

def subs(c, t, items):
    cur = None
    for st, s in items:
        if t >= st: cur = (st, s)
    if not cur: return
    k = back(seg(t, cur[0], cur[0] + 0.3))
    with c.ui(): c.text(540, 1772, cur[1], 60 * k, sw=8)

def red_tips(c, x, y, t):
    hand(c, x, y, 30)
    for i, a in enumerate((-2.2, -1.75, -1.35, -0.95)):
        fx, fy = x + math.cos(a) * 46, y + math.sin(a) * 46
        c.line([(x + math.cos(a) * 20, y + math.sin(a) * 20), (fx, fy)], w=18, fill=INK)
        c.line([(x + math.cos(a) * 20, y + math.sin(a) * 20), (fx, fy)], w=10, fill=SKIN)
        c.circ(fx, fy, 9, RED, ol=None)

