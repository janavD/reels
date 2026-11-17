"""Self-checkout props: grocery store back wall (shelves of generic boxes + tiled floor), self-checkout kiosk
(screen with message, scanner glass with red laser, flashing help light), bagging area with a plastic bag,
banana, shopper with free hand targets, store employee in a green vest, waiting-line people.
From 2026-11-17_1000 "unexpected item in the bagging area" reel."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, hand, limb, ik, back, seg, lerp, mix, ease)

STORE = ((226, 238, 232), (196, 214, 206))
TEE = (120, 150, 230)
VEST = (70, 160, 90)
BANANA = (255, 214, 60)
RED = (230, 70, 70); GRN = (70, 190, 110); BLUE = (60, 120, 200)
GREY = (176, 182, 192); DGREY = (110, 116, 128)
BOXCOL = [(240, 120, 100), (110, 170, 230), (250, 200, 80), (140, 200, 140), (210, 150, 220), (250, 160, 70)]

def dk(col, d): return mix(col, (0, 0, 0), d)

def store(c, t, cx=0):
    """back wall shelves + tile floor."""
    for row, y in enumerate((520, 700, 880)):
        c.rect(-200, y + 120, 1300, y + 140, (200, 170, 130), w=5)
        r = random.Random(row * 7)
        x = -180
        while x < 1280:
            w = r.randint(60, 110); h = r.randint(70, 115); col = r.choice(BOXCOL)
            c.rect(x, y + 120 - h, x + w, y + 120, col, w=5, r=6)
            c.rect(x + 12, y + 120 - h * 0.65, x + w - 12, y + 120 - h * 0.35, mix(col, WHITE, 0.55), ol=None)
            x += w + 8
    c.rect(-200, 1060, 1300, 1080, (200, 170, 130), w=5)
    c.rect(-200, 1080, 1300, 2100, (232, 230, 222), ol=None)
    for i in range(-3, 14):
        c.line([(i * 120 - 100, 1080), (i * 160 - 300, 2100)], w=3, fill=(205, 202, 192), caps=False)
    for j, y in enumerate((1180, 1330, 1520, 1760)):
        c.line([(-200, y), (1300, y)], w=3, fill=(205, 202, 192), caps=False)

def bag_stand(c, x0=80, x1=350, y=1110):
    c.rect(x0, y, x1, y + 34, GREY, w=6, r=8)                        # scale plate
    c.line([(x0 + 30, y + 34), (x0 + 30, 1630)], w=10, fill=DGREY)
    c.line([(x1 - 30, y + 34), (x1 - 30, 1630)], w=10, fill=DGREY)

def plastic_bag(c, x, y, puff=0.0):
    """bag sitting on plate, bottom centre (x, y)."""
    w0, w1, h = 95 + puff * 8, 80, 150
    c.poly([(x - w0, y), (x + w0, y), (x + w1, y - h), (x - w1, y - h)], (250, 250, 246), w=6)
    c.arc(x - 70, y - h - 60, x - 20, y - h + 20, 180, 360, w=7)
    c.arc(x + 20, y - h - 60, x + 70, y - h + 20, 180, 360, w=7)
    c.line([(x - 40, y - 40), (x - 10, y - 90)], w=3, fill=(210, 210, 205), caps=False)

def kiosk(c, t, msg=None, col=BLUE, flash=False, scan=False, shake=0.0):
    """kiosk on the right. msg = list of screen lines."""
    j = math.sin(t * 50) * shake
    c.rect(640, 1090, 1010, 1630, GREY, w=7, r=16)
    c.rect(680, 1200, 970, 1260, DGREY, w=5, r=10)                    # card slot / coin tray
    c.rect(700, 1330, 950, 1560, mix(GREY, WHITE, 0.3), w=5, r=12)
    c.rect(650, 1060, 1000, 1100, mix(GREY, WHITE, 0.2), w=6, r=8)     # top
    c.rect(680, 1068, 820, 1094, (60, 64, 80), w=4, r=4)               # scanner glass
    if scan:
        c.line([(690, 1081), (810, 1081)], w=5, fill=RED, caps=False); c.glow(750, 1081, 90, RED, 0.5)
    c.line([(830, 1060), (830, 900)], w=18, fill=DGREY)                 # screen stem
    # screen
    c.rect(650 + j, 590, 1010 + j, 900, (40, 42, 52), w=8, r=18)
    c.rect(668 + j, 608, 992 + j, 882, col, ol=None, r=10)
    if msg:
        n = len(msg); sz = 40 if max(len(s) for s in msg) < 13 else 33
        for i, s in enumerate(msg):
            c.text(830 + j, 745 + (i - (n - 1) / 2) * (sz + 14), s, sz, fill=WHITE, stroke=None)
    # help light
    c.line([(985, 590), (985, 500)], w=8, fill=DGREY)
    on = flash and int(t * 6) % 2 == 0
    c.chord(950, 445, 1020, 515, 180, 360, RED if on else (150, 70, 70), w=6)
    c.rect(945, 478, 1025, 500, DGREY, w=5, r=4)
    if on: c.glow(985, 470, 130, RED, 0.6)

def banana(c, x, y, a=0.0, s=1.0):
    pts = []
    for i in range(9):
        u = (i / 8 - 0.5) * 1.6
        px, py = math.sin(u) * 80 * s, (1 - math.cos(u)) * 70 * s - 40 * s
        pts.append((x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)))
    c.line(pts, w=40 * s, fill=INK); c.line(pts, w=27 * s, fill=BANANA)
    c.line(pts[2:7], w=6 * s, fill=(225, 180, 40), caps=False)
    c.circ(*pts[0], 9 * s, (90, 70, 40), ol=None); c.circ(*pts[-1], 7 * s, (90, 70, 40), ol=None)

def shopper(c, t, x, y, la, ra, eyes="open", mouth="smile", brows=None, look=(0, 0), tilt=0.0, sweat=False,
            blink=0.0, shake=0.0, frozen=False, walk=0.0, shirt=TEE):
    """shopper, head centre (x, y); la / ra = hand targets. frozen = statue-still (no idle bob)."""
    r = random.Random(int(t * 30))
    dx, dy = r.uniform(-shake, shake), r.uniform(-shake, shake)
    x += dx; y += dy
    if not frozen and not walk: y += math.sin(t * 3) * 4
    if walk: y -= abs(math.sin(t * walk * math.pi)) * 10
    hip = (x, y + 360)
    for i, side in enumerate((-1, 1)):
        ph = math.sin(t * walk * 2 * math.pi + i * math.pi) if walk else -1
        lift = max(0, ph) * 46
        ft = (x + side * 55 + (ph * 46 if walk else 0), 1630 - lift)
        kn = ik(*hip, *ft, 120, 120, bend=-side if not walk else -1)
        c.line([hip, kn, ft], w=14); c.line([ft, (ft[0] + side * 34 if not walk else ft[0] + 34, ft[1] + 2)], w=14)
    c.poly([(x - 64, y + 112), (x + 64, y + 112), (x + 78, y + 372), (x - 78, y + 372)], shirt, w=7)
    c.line([(x - 30, y + 112), (x, y + 150), (x + 30, y + 112)], w=5, caps=False)
    la = (la[0] + dx, la[1] + dy); ra = (ra[0] + dx, ra[1] + dy)
    limb(c, (x - 56, y + 150), la, 132, 132, bend=1)
    limb(c, (x + 56, y + 150), ra, 132, 132, bend=-1)
    head(c, x, y, 108, tilt=tilt, eyes=eyes, mouth=mouth, look=look, brows=brows, t=t, sweat=sweat, blink=blink)
    for i in range(5):  # hair tufts
        a = math.pi * (1.1 + i * 0.2)
        c.circ(x + math.cos(a) * 96, y + math.sin(a) * 96, 26, (60, 45, 35), w=5)
    return la, ra

def employee(c, t, x, y, tap=None, mouth="flat", eyes="half", look=(-1, 0), walk=0.0):
    """bored store employee in a green vest. tap = left hand target or None."""
    y -= abs(math.sin(t * walk * math.pi)) * 10 if walk else 0
    hip = (x, y + 400)
    for i, side in enumerate((-1, 1)):
        ph = math.sin(t * walk * 2 * math.pi + i * math.pi) if walk else -1
        ft = (x + side * 50 + (ph * 44 if walk else 0), 1630 - max(0, ph) * 40)
        kn = ik(*hip, *ft, 130, 130, bend=1)
        c.line([hip, kn, ft], w=14); c.line([ft, (ft[0] - 34, ft[1] + 2)], w=14)
    c.poly([(x - 66, y + 112), (x + 66, y + 112), (x + 80, y + 412), (x - 80, y + 412)], (245, 245, 240), w=7)
    c.poly([(x - 66, y + 112), (x - 20, y + 112), (x - 14, y + 412), (x - 80, y + 412)], VEST, w=6)
    c.poly([(x + 20, y + 112), (x + 66, y + 112), (x + 80, y + 412), (x + 14, y + 412)], VEST, w=6)
    c.rect(x - 70, y + 190, x - 26, y + 222, WHITE, w=4, r=4)          # name tag
    tl = tap if tap else (x - 100, y + 380)
    limb(c, (x - 56, y + 150), tl, 125, 125, bend=1); hand(c, *tl, 21)
    limb(c, (x + 56, y + 150), (x + 100, y + 380), 125, 125, bend=-1); hand(c, x + 100, y + 380, 21)
    head(c, x, y, 102, eyes=eyes, mouth=mouth, look=look, t=t)
    c.chord(x - 102, y - 108, x + 102, y + 10, 180, 360, VEST, w=6)    # cap
    c.rect(x - 150, y - 52, x - 20, y - 34, VEST, w=5, r=8)            # cap brim (facing left)

def line_person(c, t, x, y, shirt, hair, mouth="flat", eyes="half", brows=-0.3, arms="crossed", look=(1, 0), tap=0.0, s=1.0):
    """waiting-line customer (scaled), head centre (x, y)."""
    k = s
    hip = (x, y + 360 * k); floor_y = y + 670 * k
    for side in (-1, 1):
        lift = abs(math.sin(t * tap * math.pi)) * 18 * k if (tap and side == 1) else 0
        ft = (x + side * 50 * k, floor_y - lift); kn = ik(*hip, *ft, 120 * k, 120 * k, bend=-side)
        c.line([hip, kn, ft], w=14 * k); c.line([ft, (ft[0] + side * 30 * k, ft[1])], w=14 * k)
    c.poly([(x - 64 * k, y + 112 * k), (x + 64 * k, y + 112 * k), (x + 78 * k, y + 372 * k), (x - 78 * k, y + 372 * k)], shirt, w=7 * k)
    if arms == "crossed":
        c.line([(x - 56 * k, y + 150 * k), (x - 70 * k, y + 230 * k), (x + 50 * k, y + 220 * k)], w=14 * k)
        c.line([(x + 56 * k, y + 150 * k), (x + 70 * k, y + 240 * k), (x - 50 * k, y + 232 * k)], w=14 * k)
        hand(c, x + 50 * k, y + 220 * k, 19 * k); hand(c, x - 50 * k, y + 232 * k, 19 * k)
    else:  # checking watch
        wy = y + 200 * k + math.sin(t * 5) * 4
        limb(c, (x - 56 * k, y + 150 * k), (x + 20 * k, wy), 110 * k, 110 * k, bend=1)
        c.rect(x - 2 * k, wy - 12 * k, x + 22 * k, wy + 12 * k, (60, 60, 70), w=4 * k, r=4)
        hand(c, x + 30 * k, wy, 19 * k)
        limb(c, (x + 56 * k, y + 150 * k), (x + 100 * k, y + 340 * k), 110 * k, 110 * k, bend=-1)
        hand(c, x + 100 * k, y + 340 * k, 19 * k)
    head(c, x, y, 108 * k, eyes=eyes, mouth=mouth, brows=brows, look=look, t=t)
    for i in range(5):
        a = math.pi * (1.1 + i * 0.2)
        c.circ(x + math.cos(a) * 96 * k, y + math.sin(a) * 96 * k, 26 * k, hair, w=5 * k)

def cart(c, x, y, s=1.0):
    k = s
    c.poly([(x - 130 * k, y - 120 * k), (x + 120 * k, y - 120 * k), (x + 90 * k, y + 40 * k), (x - 100 * k, y + 40 * k)], None, w=7 * k)
    for i in range(1, 5):
        xx = x - 130 * k + i * 50 * k; c.line([(xx, y - 120 * k), (xx - 6 * k, y + 40 * k)], w=4 * k, caps=False)
    c.line([(x - 130 * k, y - 120 * k), (x - 170 * k, y - 170 * k)], w=8 * k)
    c.line([(x - 100 * k, y + 40 * k), (x - 90 * k, y + 110 * k), (x + 80 * k, y + 110 * k)], w=7 * k)
    for wx in (-80, 70): c.circ(x + wx * k, y + 130 * k, 18 * k, DGREY, w=5 * k)
    for i, col in enumerate(BOXCOL[:4]):
        c.rect(x - 110 * k + i * 52 * k, y - 190 * k + (i % 2) * 30 * k, x - 64 * k + i * 52 * k, y - 110 * k, col, w=5 * k, r=5)
