"""Night-noise props: orange cat (sitting / curled sleeping, paw swipe, glowing eyes in the dark),
dark kitchen (counter, cabinets, cup), hallway (door, frames), standing pajama guy with pillow + phone
flashlight beam, tiptoe walk, bedside digital clock. From 2026-11-17_0400 "noise at 4am" reel."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, hand, limb, ik, back, seg, lerp, mix, ease, floor)

CAT = (238, 150, 70)
CAT_D = (200, 112, 46)
BLACK = (0, 0, 0)

def dk(col, d): return mix(col, BLACK, d)

def bedside_clock(c, txt, x=60, y=1430):
    c.rect(x - 70, y - 70, x + 70, y, (40, 40, 48), w=6, r=12)
    c.text(x, y - 35, txt, 40, fill=(255, 90, 90), stroke=None)
    c.glow(x, y - 35, 120, (255, 90, 90), 0.18)

def cat(c, x, y, t, eyes="open", paw=0.0, d=0.0, glow_eyes=False, tail=True, s=1.0):
    """sitting cat, feet at (x, y). paw 0..1 swipes the left paw out. d = darkness 0..1."""
    col, cd = dk(CAT, d), dk(CAT_D, d)
    ol = INK
    if tail:
        sw = math.sin(t * 3) * 30
        pts = [(x + 50 * s, y - 15 * s), (x + 110 * s, y - 30 * s), (x + 130 * s + sw * s * 0.4, y - 110 * s),
               (x + 110 * s + sw * s, y - 170 * s)]
        c.line(pts, w=26 * s, fill=ol); c.line(pts, w=14 * s, fill=col)
    c.ell(x - 70 * s, y - 150 * s, x + 70 * s, y, col, w=6)                     # body
    c.ell(x - 35 * s, y - 120 * s, x + 35 * s, y - 20 * s, dk((255, 220, 180), d), ol=None)  # chest
    # paw
    px = x - 30 * s - paw * 110 * s; py = y - 8 * s - math.sin(paw * math.pi) * 30 * s
    c.line([(x - 30 * s, y - 60 * s), (px, py)], w=30 * s, fill=ol); c.line([(x - 30 * s, y - 60 * s), (px, py)], w=18 * s, fill=col)
    c.ell(x + 10 * s, y - 22 * s, x + 50 * s, y, col, w=5)
    hx, hy = x, y - 190 * s
    for side in (-1, 1):  # ears
        c.poly([(hx + side * 20 * s, hy - 45 * s), (hx + side * 62 * s, hy - 90 * s), (hx + side * 62 * s, hy - 20 * s)], col, w=6)
        c.poly([(hx + side * 34 * s, hy - 45 * s), (hx + side * 55 * s, hy - 70 * s), (hx + side * 55 * s, hy - 35 * s)],
               dk((255, 170, 165), d), ol=None)
    c.circ(hx, hy, 66 * s, col, w=6)
    c.line([(hx - 20 * s, hy - 60 * s), (hx - 14 * s, hy - 40 * s)], w=6 * s, fill=cd)
    c.line([(hx + 20 * s, hy - 60 * s), (hx + 14 * s, hy - 40 * s)], w=6 * s, fill=cd)
    for side in (-1, 1):
        ex, ey = hx + side * 26 * s, hy - 4 * s
        if glow_eyes:
            c.ell(ex - 16 * s, ey - 13 * s, ex + 16 * s, ey + 13 * s, (255, 235, 90), ol=None)
            c.ell(ex - 4 * s, ey - 11 * s, ex + 4 * s, ey + 11 * s, BLACK, ol=None)
            c.glow(ex, ey, 70 * s, (255, 230, 80), 0.35)
        elif eyes == "open":
            c.ell(ex - 14 * s, ey - 13 * s, ex + 14 * s, ey + 13 * s, (170, 220, 120), w=4)
            c.ell(ex - 4 * s, ey - 11 * s, ex + 4 * s, ey + 11 * s, INK, ol=None)
        elif eyes == "half":
            c.ell(ex - 14 * s, ey - 6 * s, ex + 14 * s, ey + 10 * s, (170, 220, 120), w=4)
            c.line([(ex - 16 * s, ey - 6 * s), (ex + 16 * s, ey - 6 * s)], w=6 * s)
        else:
            c.arc(ex - 14 * s, ey - 14 * s, ex + 14 * s, ey + 8 * s, 20, 160, w=6 * s)
    if not glow_eyes:
        c.poly([(hx - 8 * s, hy + 14 * s), (hx + 8 * s, hy + 14 * s), (hx, hy + 24 * s)], dk((255, 150, 160), d), w=3)
        c.arc(hx - 16 * s, hy + 14 * s, hx, hy + 34 * s, 20, 160, w=4 * s); c.arc(hx, hy + 14 * s, hx + 16 * s, hy + 34 * s, 20, 160, w=4 * s)
        for side in (-1, 1):
            for dy in (-6, 8):
                c.line([(hx + side * 34 * s, hy + 20 * s), (hx + side * 90 * s, hy + (20 + dy) * s)], w=3 * s, caps=False)

def cat_curled(c, x, y, t):
    """sleeping cat loaf on a blanket, breathing."""
    br = math.sin(t * 3) * 5
    c.ell(x - 110, y - 70 - br, x + 110, y, CAT, w=6)
    c.line([(x + 90, y - 10), (x + 40, y + 5), (x - 60, y + 2)], w=24, fill=INK); c.line([(x + 90, y - 10), (x + 40, y + 5), (x - 60, y + 2)], w=12, fill=CAT)
    hx, hy = x - 80, y - 60 - br
    for side in (-1, 1):
        c.poly([(hx + side * 18, hy - 35), (hx + side * 50, hy - 75), (hx + side * 52, hy - 15)], CAT, w=6)
    c.circ(hx, hy, 52, CAT, w=6)
    for side in (-1, 1):
        ex = hx + side * 22; c.arc(ex - 12, hy - 14, ex + 12, hy + 6, 20, 160, w=5)
    c.poly([(hx - 6, hy + 12), (hx + 6, hy + 12), (hx, hy + 20)], (255, 150, 160), w=3)

def kitchen(c, d=0.0, t=0.0):
    wall = dk((120, 128, 150), d)
    c.rect(-100, 380, 1200, 1640, wall, ol=None)
    for x in range(-100, 1200, 70):  # tiles behind counter
        c.line([(x, 880), (x, 1230)], w=3, fill=dk((140, 148, 170), d), caps=False)
    for y in range(880, 1230, 70): c.line([(540, y), (1200, y)], w=3, fill=dk((140, 148, 170), d), caps=False)
    cab = dk((150, 190, 170), d)
    c.rect(560, 560, 1120, 860, cab, w=7)
    for x0 in (560, 750, 940): c.rect(x0 + 15, 575, x0 + 175, 845, dk(mix(cab, WHITE, 0.15), d), w=5, r=8)
    c.rect(540, 1230, 1140, 1275, dk((235, 225, 210), d), w=7)                  # counter top
    c.rect(560, 1275, 1120, 1640, cab, w=7)
    for x0 in (560, 750, 940):
        c.rect(x0 + 15, 1295, x0 + 175, 1620, dk(mix(cab, WHITE, 0.15), d), w=5, r=8)
        c.line([(x0 + 150, 1440), (x0 + 150, 1480)], w=8)
    floor(c, True)

def cup(c, x, y, a=0.0, d=0.0):
    """mug standing with its bottom at (x, y), rotated a radians."""
    pts = [(-32, 0), (32, 0), (36, -80), (-36, -80)]
    P = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) for px, py in pts]
    hx, hy = x + 50 * math.cos(a) + 40 * math.sin(a), y + 50 * math.sin(a) - 40 * math.cos(a)
    c.circ(hx, hy, 18, None, w=7)
    c.poly(P, dk((240, 110, 110), d), w=6)

def hallway(c, d=0.0):
    wall = dk((96, 98, 136), d)
    c.rect(-100, 380, 1200, 1640, wall, ol=None)
    c.rect(780, 820, 1040, 1640, dk((150, 110, 80), d), w=8)                     # door
    c.circ(810, 1250, 12, dk((240, 200, 90), d), w=4)
    for (x0, y0, w0, h0, col) in ((120, 720, 170, 140, (240, 190, 90)), (360, 760, 120, 160, (120, 180, 230))):
        c.rect(x0, y0, x0 + w0, y0 + h0, dk((90, 60, 40), d), w=6)
        c.rect(x0 + 16, y0 + 16, x0 + w0 - 16, y0 + h0 - 16, dk(col, d), ol=None)
    floor(c, True)

def pillow(c, x, y, a=0.0):
    w, h = 80, 52
    pts = [(-w, -h), (w, -h), (w, h), (-w, h)]
    P = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) for px, py in pts]
    c.poly(P, (236, 236, 248), w=7)

def beam(c, x, y, tx, ty, spread=140, col=(255, 240, 170), k=0.45, wall=(60, 60, 90)):
    ang = math.atan2(ty - y, tx - x); nx, ny = -math.sin(ang), math.cos(ang)
    c.poly([(x, y), (tx + nx * spread, ty + ny * spread), (tx - nx * spread, ty - ny * spread)], mix(wall, col, k), ol=None)
    c.glow(tx, ty, spread * 1.4, col, 0.3)

def phone_pos(x, y): return (x + 150, y + 210)

def person(c, t, x, y, eyes="open", mouth="smile", brows=None, look=(0, 0), tilt=0.0, walk=0.0, sweat=False,
           blink=0.0, pillow_up=1.0, flash=None, shake=0.0, arms_out=0.0):
    """standing pajama guy. walk = tiptoe phase speed (0 = still). flash = (tx, ty) beam target or None."""
    r = random.Random(int(t * 30))
    x += r.uniform(-shake, shake); y += r.uniform(-shake, shake)
    hip = (x, y + 360)
    for i, side in enumerate((-1, 1)):
        ph = math.sin(t * walk * 2 * math.pi + i * math.pi) if walk else -1
        lift = max(0, ph) * 70
        ft = (x + side * 55 + (ph * 40 if walk else 0), 1630 - lift)
        kn = ik(*hip, *ft, 120, 120, bend=-side if not walk else -1)
        c.line([hip, kn, ft], w=14)
        c.line([ft, (ft[0] + 34, ft[1] + 2 - (12 if lift > 5 else 0))], w=14)   # tiptoe
    c.poly([(x - 62, y + 112), (x + 62, y + 112), (x + 74, y + 370), (x - 74, y + 370)], (130, 160, 220), w=7)
    for yy in (y + 180, y + 260, y + 340): c.line([(x - 66, yy), (x + 70, yy)], w=4, fill=(230, 235, 250), caps=False)
    sh_l, sh_r = (x - 55, y + 150), (x + 55, y + 150)
    # left hand: pillow raised
    pr = (lerp(x - 120, x - 150, pillow_up), lerp(y + 300, y - 90, pillow_up))
    if arms_out: pr = (lerp(pr[0], x - 200, arms_out), lerp(pr[1], y - 150, arms_out))
    limb(c, sh_l, pr, 110, 110, bend=1)
    if not arms_out: pillow(c, pr[0] - 20, pr[1] - 50, -0.3 + math.sin(t * 6) * 0.05)
    hand(c, *pr, 21)
    # right hand: phone flashlight
    pl = phone_pos(x, y) if not arms_out else (x + 200, y - 150)
    limb(c, sh_r, pl, 110, 110, bend=-1)
    if flash is not None and not arms_out:
        c.rect(pl[0] - 26, pl[1] - 46, pl[0] + 26, pl[1] + 46, (34, 34, 40), w=5, r=10)
        c.circ(pl[0] + 10, pl[1] - 30, 7, (255, 250, 210), ol=None)
    hand(c, *pl, 21)
    head(c, x, y, 108, tilt=tilt, eyes=eyes, mouth=mouth, look=look, brows=brows, t=t, sweat=sweat, blink=blink)
