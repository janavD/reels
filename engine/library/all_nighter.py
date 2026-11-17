"""All-nighter props: standing hoodie guy (free arms: arms_up wiggle / hold a frying pan / point),
pan with egg, checklist paper with pop-in ticks, classroom (chalkboard + student desk + notebook),
seated student who nods off / sleeps face down on the desk, teacher side character.
From 2026-11-17_0500 "i'll just stay up" reel."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, hand, limb, ik, back, seg, lerp, mix, ease, floor)

HOOD = (232, 120, 90)
GREEN_BOARD = (52, 98, 78)

def stander(c, t, x, y, eyes="open", mouth="smile", brows=None, look=(0, 0), tilt=0.0, blink=0.0, sweat=False,
            arms_up=0.0, bounce=0.0, pan=False, shirt=HOOD, blush=False):
    """standing guy, head centre (x, y). arms_up 0..1 raises both arms with a wiggle. pan = holds a frying pan."""
    y -= abs(math.sin(t * 9)) * bounce
    hip = (x, y + 360)
    for side in (-1, 1):
        ft = (x + side * 60, 1630); kn = ik(*hip, *ft, 120, 120, bend=-side)
        c.line([hip, kn, ft], w=14); c.line([ft, (ft[0] + side * 34, ft[1] + 2)], w=14)
    c.poly([(x - 64, y + 112), (x + 64, y + 112), (x + 78, y + 372), (x - 78, y + 372)], shirt, w=7)
    c.rect(x - 40, y + 260, x + 40, y + 300, mix(shirt, (0, 0, 0), 0.18), w=4, r=10)   # hoodie pocket
    sh_l, sh_r = (x - 56, y + 150), (x + 56, y + 150)
    wig = math.sin(t * 16) * 22 * arms_up
    tl = (lerp(x - 110, x - 190, arms_up), lerp(y + 330, y - 120 + wig, arms_up))
    tr = (lerp(x + 110, x + 190, arms_up), lerp(y + 330, y - 120 - wig, arms_up))
    if pan:
        tr = (x + 200, y + 220 + math.sin(t * 10) * 14)
    limb(c, sh_l, tl, 112, 112, bend=1); limb(c, sh_r, tr, 112, 112, bend=-1)
    if pan: frying_pan(c, tr[0], tr[1], t)
    hand(c, *tl, 21); hand(c, *tr, 21)
    head(c, x, y, 108, tilt=tilt, eyes=eyes, mouth=mouth, look=look, brows=brows, t=t, sweat=sweat, blink=blink,
         blush=blush)

def frying_pan(c, hx, hy, t):
    flip = abs(math.sin(t * 5))
    c.line([(hx, hy), (hx + 90, hy - 10)], w=14, fill=(60, 60, 66))
    px, py = hx + 170, hy - 18
    c.ell(px - 90, py - 26, px + 90, py + 26, (70, 70, 78), w=7)
    ey = py - 10 - flip * 110
    c.ell(px - 44, ey - 16, px + 44, ey + 16, WHITE, w=5)
    c.circ(px + 4, ey - 2, 14, (255, 200, 60), w=4)

def checklist(c, x, y, items, t, starts):
    c.rect(x - 235, y - 40, x + 235, y + 90 * len(items) + 20, (252, 250, 240), w=7, r=18)
    for i, s in enumerate(items):
        yy = y + 30 + i * 90
        c.rect(x - 210, yy - 26, x - 158, yy + 26, WHITE, w=5, r=8)
        c.text(x + 30, yy, s, 38, fill=INK, stroke=None)
        k = back(seg(t, starts[i], starts[i] + 0.2))
        if k > 0.01:
            c.line([(x - 205, yy - 4), (x - 185, yy + 22 * k), (x - 185 + 50 * k, yy - 40 * k)], w=10, fill=(60, 170, 90))

def classroom(c, t, clock="9:00"):
    c.rect(-100, 380, 1200, 1640, (226, 214, 186), ol=None)
    c.rect(90, 520, 990, 900, (120, 84, 54), w=8, r=10)
    c.rect(115, 545, 965, 875, GREEN_BOARD, ol=None)
    for i, (sx, sy, s) in enumerate(((330, 640, "x² + 4x = ?"), (360, 760, "f(x) = 2x + 1"), (780, 700, "y = mx + b"))):
        c.text(sx, sy, s, 44, fill=(235, 240, 230), stroke=None)
    c.line([(620, 610), (700, 650), (650, 800)], w=4, fill=(235, 240, 230), caps=False)
    c.rect(400, 890, 680, 912, (120, 84, 54), w=5)                       # chalk tray
    c.rect(80, 970, 260, 1050, (40, 40, 48), w=6, r=14)                 # wall clock
    c.text(170, 1010, clock, 46, fill=(255, 90, 90), stroke=None)
    floor(c, False)

def student_desk(c):
    wood = (196, 146, 92)
    c.rect(180, 1370, 900, 1430, wood, w=8, r=8)
    for x0 in (230, 810): c.rect(x0, 1430, x0 + 40, 1650, (90, 90, 100), w=6)
    c.rect(600, 1340, 800, 1374, WHITE, w=5, r=4)                       # notebook
    c.line([(620, 1357), (770, 1357)], w=3, fill=(120, 160, 220), caps=False)

def seated(c, t, nod=0.0, sleep=False, eyes="half", mouth="flat", brows=None, look=(0, 0), blink=0.0, sweat=False):
    """student behind the desk. nod 0..1 drops the head forward. sleep = face down on the desk."""
    x = 540
    c.poly([(x - 70, 1150), (x + 70, 1150), (x + 92, 1372), (x - 92, 1372)], HOOD, w=7)
    if sleep:
        for side in (-1, 1):
            limb(c, (x + side * 60, 1190), (x + side * 150, 1350), 105, 105, bend=side)
            hand(c, x + side * 150, 1350, 21)
        head(c, x, 1262, 108, tilt=0.12, eyes="closed", mouth="drool", t=t, squash=0.88)
        return
    hy = 1040 + nod * 120
    for side in (-1, 1):
        limb(c, (x + side * 58, 1190), (x + side * 130, 1360), 105, 105, bend=side)
        hand(c, x + side * 130, 1360, 21)
    head(c, x, hy, 108, tilt=nod * 0.15, eyes=eyes, mouth=mouth, brows=brows, look=look, blink=blink, t=t, sweat=sweat)

def teacher(c, t, x=930, y=960, mouth="o", brows=0.3):
    c.poly([(x - 66, y + 112), (x + 66, y + 112), (x + 80, y + 680), (x - 80, y + 680)], (110, 150, 110), w=7)
    c.line([(x, y + 112), (x, y + 300)], w=6, fill=(220, 60, 70))       # tie
    limb(c, (x - 56, y + 150), (x - 150, y + 120 + math.sin(t * 6) * 10), 110, 110, bend=1)
    hand(c, x - 150, y + 120 + math.sin(t * 6) * 10, 21)
    head(c, x, y, 104, eyes="open", mouth=mouth, brows=brows, look=(-1, 0.3), t=t)
    c.rect(x - 70, y - 25, x - 10, y + 5, None, w=5, r=8); c.rect(x + 10, y - 25, x + 70, y + 5, None, w=5, r=8)
    c.line([(x - 10, y - 12), (x + 10, y - 12)], w=5)
