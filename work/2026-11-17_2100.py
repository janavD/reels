"""9pm motivational reel: first pull-up. Fails day 1, almost day 12, wants to quit day 23, keeps showing up, day 47 gets it."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, SKIN, WHITE, WALL_DAY, WALL_NIGHT, head, limb, hand, ik, floor, label, sub, caption,
                 punch, blinkf, back, ease, eout, seg, lerp, mix, rot, star)
from PIL import Image

rig.CAP = ["me trying to do", "my first pull-up"]

BAR = 800
SHIRT = (235, 120, 70)
EVE = ((240, 214, 186), (214, 184, 156))
GOLD = (255, 205, 60)

# ---------- set ----------
def daycard(c, n):
    c.rect(70, 560, 250, 770, WHITE, w=6, r=12)
    c.rect(70, 560, 250, 615, (70, 150, 220), w=6, r=12)
    c.text(160, 588, "DAY", 26, fill=WHITE, stroke=None)
    c.text(160, 690, str(n), 76, fill=INK, stroke=None)
    c.circ(160, 552, 8, (200, 200, 200), w=4)

def poster(c, flag=False, t=0.0):
    c.rect(830, 580, 1020, 850, (250, 246, 236), w=6, r=6)
    c.rect(848, 598, 1002, 832, (170, 210, 240), ol=None)
    c.poly([(848, 832), (925, 660), (1002, 832)], (120, 130, 150), w=5)
    c.poly([(902, 712), (925, 660), (948, 712), (935, 704), (925, 716), (913, 704)], WHITE, ol=None)
    c.line([(925, 660), (925, 610)], w=5)
    wav = math.sin(t * 8) * 4
    c.poly([(925, 612), (970, 622 + wav), (925, 636)], (230, 70, 70), w=4)

def doorway(c):
    c.rect(320, 620, 760, 1660, (250, 244, 232), w=7)
    c.rect(352, 652, 728, 1660, (120, 100, 92), w=6)
    c.rect(352, 652, 728, 900, (104, 86, 80), ol=None)

def pullbar(c):
    for x0 in (300, 756):
        c.rect(x0, BAR - 30, x0 + 24, BAR + 30, (150, 155, 165), w=5, r=6)
    c.rect(300, BAR - 13, 780, BAR + 13, (195, 200, 210), w=6, r=12)

def set_(c, day, night=False, t=0.0, flag=False):
    doorway(c); daycard(c, day); poster(c, flag, t); floor(c, night)
    pullbar(c)

def shirt(c, x, y):
    c.poly([(x - 55, y + 135), (x + 55, y + 135), (x + 62, y + 220), (x + 40, y + 340),
            (x - 40, y + 340), (x - 62, y + 220)], SHIRT, w=6)

# ---------- poses ----------
def hanger(c, x, p, t, shake=0.0, kick=0.0, **face):
    """hanging from the bar; p = 0 (dead hang) .. 1 (chin over bar)."""
    jx = math.sin(t * 57) * shake
    hy = lerp(BAR + 150, BAR - 140, p) + math.sin(t * 43) * shake * 0.6
    hx = x + jx
    hip = (hx, hy + 360)
    for side in (-1, 1):
        sw = math.sin(t * 9 + side) * kick
        fx, fy = hx + side * 30 + sw * 40, hip[1] + 215 - abs(sw) * 30
        limb(c, hip, (fx, fy), 118, 118, bend=-side)
        c.line([(fx, fy), (fx + side * 34, fy + 4)], w=14)
    c.line([(hx, hy + 105), hip], w=14)
    shirt(c, hx, hy)
    for side in (-1, 1):
        sh = (hx + side * 34, hy + 118)
        limb(c, sh, (x + side * 82, BAR - 4), 140, 140, bend=side)
    head(c, hx, hy, 110, t=t, **face)
    for side in (-1, 1):
        hand(c, x + side * 82, BAR - 4, 23)

def sitter(c, x, t, **face):
    hy = 1262
    hip = (x, 1612)
    limb(c, hip, (x + 230, 1628), 125, 125, bend=-1); c.line([(x + 230, 1628), (x + 262, 1600)], w=14)
    limb(c, hip, (x + 250, 1636), 125, 125, bend=-1); c.line([(x + 250, 1636), (x + 282, 1606)], w=14)
    c.line([(x, hy + 105), hip], w=14)
    shirt(c, x, hy)
    for side in (-1, 1):
        limb(c, (x + side * 30, hy + 165), (x - 70 + side * 60, 1630), 118, 118, bend=1)
        hand(c, x - 70 + side * 60, 1630, 21)
    head(c, x, hy, 110, t=t, **face)

def lier(c, x, t, **face):
    """lying on the floor, head at left, looking up at the bar."""
    hy = 1532
    hip = (x + 370, 1595)
    c.line([(x + 100, 1565), hip], w=14)
    c.poly([(x + 120, 1530), (x + 330, 1555), (x + 330, 1630), (x + 120, 1625)], SHIRT, w=6)
    limb(c, hip, (x + 620, 1630), 130, 130, bend=-1); c.line([(x + 620, 1630), (x + 640, 1596)], w=14)
    limb(c, hip, (x + 560, 1632), 130, 130, bend=1); c.line([(x + 560, 1632), (x + 580, 1598)], w=14)
    for dx in (170, 250):
        c.line([(x + dx, 1580), (x + dx + 40, 1632)], w=14); hand(c, x + dx + 40, 1632, 20)
    head(c, x, hy, 105, t=t, **face)

def stander(c, x, y, t, armL, armR, bendL=1, bendR=-1):
    hip = (x, y + 360)
    c.ell(x - 140, 1625, x + 140, 1655, mix((178, 128, 86), (0, 0, 0), 0.25), ol=None)
    for side in (-1, 1):
        fx, fy = x + side * 60, min(1630, y + 580)
        limb(c, hip, (fx, fy), 118, 118, bend=side)
        c.line([(fx, fy), (fx + side * 40, fy + 2)], w=14)
    c.line([(x, y + 105), hip], w=14)
    shirt(c, x, y)
    sh = (x, y + 170)
    for tgt, b in ((armL, bendL), (armR, bendR)):
        limb(c, sh, tgt, 115, 115, bend=b); hand(c, *tgt, 22)

def strain_lines(c, x, y, t):
    for i, a in enumerate((-2.5, -0.65)):
        ph = (t * 3 + i * 0.5) % 1
        r0 = 150 + ph * 30
        c.line([(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * (r0 + 40), y + math.sin(a) * (r0 + 40))], w=6)

# ---------- scenes ----------
def s_day1(t, dur=3.0):
    drop = 1.95
    fall = ease(seg(t, drop, drop + 0.25))
    z = punch(t, lerp(1.0, 1.08, ease(t / dur)))
    c = C(*WALL_DAY, cam=(540, lerp(1160, 1290, fall), z))
    set_(c, 1, t=t)
    if t < drop:
        p = 0.07 * ease(seg(t, 0.3, 1.0)) + 0.02 * math.sin(t * 6)
        hanger(c, 540, p, t, shake=3 + 4 * seg(t, 0.4, drop), kick=0.6 * seg(t, 1.0, drop),
               eyes="closed" if t > 0.6 else "open", mouth="grit", brows=0.45, sweat=t > 0.7, tilt=math.sin(t * 13) * 0.05)
        if t > 0.6: strain_lines(c, 540, BAR + 150, t)
        if 0.8 < t < drop:
            c.text(800, 1000, "nngh", 56 * back(seg(t, 0.8, 1.0)), fill=WHITE, sw=7)
    else:
        sitter(c, 470, t, eyes="spiral", mouth="frown", tilt=math.sin(t * 5) * 0.08)
        tt = t - drop
        for i in range(3):
            a = tt * 6 + i * 2.1
            star(c, 470 + math.cos(a) * 130, 1130 + math.sin(a) * 30, 18)
        if tt < 0.4:
            c.text(720, 1400, "THUD", 90 * back(tt / 0.2), fill=(255, 220, 60), sw=10)
    caption(c); label(c, t, "Day 1"); sub(c, t, "0 pull-ups", 2.2)
    return c.out()

def s_day12(t, dur=2.8):
    z = punch(t, lerp(1.05, 1.16, ease(t / dur)))
    c = C(*EVE, cam=(540, 1100, z)); set_(c, 12, t=t)
    up = ease(seg(t, 0.15, 1.3)) * 0.55
    slide = ease(seg(t, 1.9, 2.35))
    p = up * (1 - slide)
    sh = 3 + 6 * seg(t, 0.6, 1.9)
    fail = t > 1.9
    hanger(c, 540, p, t, shake=sh, kick=0.3 + 0.5 * seg(t, 1.0, 1.9),
           eyes="wide" if not fail else "half", mouth="grit" if not fail else "frown", brows=0.5 if not fail else -0.2,
           sweat=True, look=(0, -1) if not fail else (0, 1), tilt=math.sin(t * 15) * 0.05 if not fail else 0)
    if not fail: strain_lines(c, 540, lerp(BAR + 150, BAR - 140, p), t)
    caption(c); label(c, t, "Day 12"); sub(c, t, "so close...", 1.95)
    return c.out()

def s_day23(t, dur=3.4):
    cut = 1.75
    if t < cut:
        z = punch(t, lerp(1.08, 1.18, ease(t / cut)))
        c = C(*WALL_NIGHT, cam=(560, 1330, z)); set_(c, 23, night=True, t=t)
        lier(c, 330, t, eyes="open", mouth="frown", look=(1, -1), blink=blinkf(t, 1.4, 0.4), brows=-0.25)
        # rain-cloud of doubt
        cx, cy = 330 + math.sin(t * 2) * 10, 1300
        for dx, r in ((-50, 45), (0, 60), (55, 45)): c.circ(cx + dx, cy, r, (150, 155, 175), ol=None)
        for i in range(5):
            ph = (t * 2.2 + i / 5) % 1
            c.line([(cx - 60 + i * 30, cy + 40 + ph * 90), (cx - 64 + i * 30, cy + 60 + ph * 90)], w=5, fill=(150, 200, 255))
        caption(c); label(c, t, "Day 23"); sub(c, t, "wanted to quit", 0.4)
    else:
        tt = t - cut
        z = punch(tt, lerp(1.05, 1.22, ease(tt / (dur - cut))), 0.1)
        c = C(*WALL_NIGHT, cam=(540, 1130, z)); set_(c, 23, night=True, t=t)
        x, y = 540, 1060
        clap = abs(math.sin(tt * 9)) if tt < 0.8 else 0
        if tt < 0.8:
            aL, aR = (x - 25 - 40 * clap, y + 230), (x + 25 + 40 * clap, y + 230)
        else:
            k = ease(seg(tt, 0.8, 1.15))
            aL, aR = (lerp(x - 25, x - 140, k), lerp(y + 230, y - 80, k)), (lerp(x + 25, x + 140, k), lerp(y + 230, y - 80, k))
        stander(c, x, y, tt, aL, aR, bendL=-1, bendR=1)
        if tt < 0.9:
            for i in range(6):  # chalk dust
                r = random.Random(i)
                ph = (tt * 1.5 + i / 6) % 1
                c.circ(x + r.uniform(-80, 80) + ph * r.uniform(-60, 60), y + 220 - ph * 140, 10 + 14 * ph,
                       mix((255, 255, 255), (88, 92, 128), ph), ol=None)
        head(c, x, y, 110, t=tt, eyes="open", mouth="flat", look=(0, -1), brows=0.45, blink=blinkf(tt, 3, 0.5))
        caption(c); label(c, 1, "Day 23"); sub(c, tt, "...one more try", 0.2)
    return c.out()

def s_grind(t, dur=2.8):
    days = list(range(24, 47))
    per = dur / len(days)
    i = min(len(days) - 1, int(t / per))
    night = i % 2 == 1
    z = 1.04 + 0.04 * math.sin(t * 3)
    c = C(*(WALL_NIGHT if night else WALL_DAY), cam=(540, 1130, z)); set_(c, days[i], night=night, t=t)
    prog = i / (len(days) - 1)
    rep = abs(math.sin(t * math.pi / (per * 2)))
    p = rep * (0.25 + 0.55 * prog)
    hanger(c, 540, p, t, shake=2 + 3 * rep, kick=0.2, eyes="closed" if rep > 0.5 else "open", mouth="grit",
           brows=0.45, sweat=True, look=(0, -1))
    # progress bar
    with c.ui():
        c.rect(240, 1520, 840, 1560, WHITE, w=6, r=20)
        c.rect(246, 1526, 246 + 588 * (prog * 0.95 + 0.04), 1554, (70, 200, 110), ol=None, r=16)
    caption(c); label(c, t, "kept showing up"); sub(c, t, "every. single. day.", 0.5)
    return c.out()

CONF = [(random.Random(i).uniform(0, 1080), random.Random(i + 50).uniform(0.5, 1.2), i % 5) for i in range(38)]
CCOL = [(235, 80, 80), (80, 150, 230), GOLD, (90, 200, 120), (190, 110, 220)]

def s_day47(t, dur=4.6):
    top = 2.25; cut = 3.0
    if t < cut:
        zk = ease(seg(t, 0.2, top))
        rnd = random.Random(int(t * 30))
        shk = 6 * seg(t, 1.2, top) if t < top else 0
        c = C(*EVE, cam=(540 + rnd.uniform(-shk, shk), lerp(1100, 920, zk), lerp(1.04, 1.38, zk)))
        set_(c, 47, t=t)
        p = ease(seg(t, 0.35, top)) * 1.0 + (0.03 * math.sin((t - top) * 10) if t > top else 0)
        made = t > top
        hanger(c, 540, p, t, shake=0 if made else 2 + 6 * seg(t, 0.8, top), kick=0.2 if made else 0.5,
               eyes="happy" if made else ("closed" if t > 1.5 else "wide"), mouth="grin" if made else "grit",
               brows=None if made else 0.5, sweat=not made, look=(0, -1), blush=made)
        if not made: strain_lines(c, 540, lerp(BAR + 150, BAR - 140, p), t)
        if made:
            f = 1 - seg(t, top, top + 0.35)
            c.glow(540, BAR - 100, 520, (255, 240, 200), 0.65 * f + 0.15)
            with c.ui():
                k = back(seg(t, top, top + 0.3))
                c.text(540, 1520, "1 PULL-UP", 120 * k, fill=GOLD, sw=12)
        caption(c)
        if not made: label(c, t, "Day 47")
    else:
        tt = t - cut
        z = punch(tt, lerp(1.0, 1.06, ease(tt / (dur - cut))), 0.1)
        c = C(*EVE, cam=(540, 1160, z)); set_(c, 47, t=t)
        jump = abs(math.sin(tt * 7)) * 50 * (1 - seg(tt, 1.0, 1.6))
        x, y = 540, 1060 - jump
        c.glow(540, 1000, 500, (255, 230, 170), 0.3)
        stander(c, x, y, tt, (x - 150, y - 90 + math.sin(tt * 14) * 15), (x + 150, y - 90 - math.sin(tt * 14) * 15),
                bendL=-1, bendR=1)
        head(c, x, y, 110, t=tt, eyes="happy", mouth="laugh", blush=True, tilt=math.sin(tt * 6) * 0.08)
        for i, (cx0, sp, ci) in enumerate(CONF):
            ph = (tt * sp + i * 0.031) % 1.3
            cy = 380 + ph * 1300
            a = tt * 6 + i
            pts = [(cx0 + math.sin(tt * 3 + i) * 30 + rot(dx, dy, a)[0], cy + rot(dx, dy, a)[1]) for dx, dy in ((-12, -7), (12, -7), (12, 7), (-12, 7))]
            c.poly(pts, CCOL[ci], ol=None)
        for i in range(3):
            aa = tt * 3 + i * 2.1
            star(c, x + math.cos(aa) * 210, y - 60 + math.sin(aa) * 50, 20)
        caption(c)
        with c.ui(): c.text(540, 1650, "1 PULL-UP", 110, fill=GOLD, sw=12)
        sub(c, tt, "small wins still count", 0.35)
    return c.out()

SCENES = [
    ("m1", 3.0, s_day1),
    ("m2", 2.8, s_day12),
    ("m3", 3.4, s_day23),
    ("m4", 2.8, s_grind),
    ("m5", 4.6, s_day47),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"m1": [1.2, 2.0, 2.6], "m2": [1.3, 2.5], "m3": [0.9, 2.2, 3.2], "m4": [0.7, 2.5], "m5": [1.8, 2.5, 3.8]}
        ims = [fn(tt).resize((270, 480)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (270 * 7, 480 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 7) * 270, (i // 7) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
