"""Extra funny reel: 'i'll just have one chip' -> eats the whole bag."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, SKIN, WHITE, WALL_NIGHT, head, limb, hand, floor, shelf, window, lamp, label, sub,
                 caption, punch, blinkf, back, ease, eout, seg, lerp, mix, rot, star, font)
from PIL import Image

rig.CAP = ['me: "i\'ll just have', 'ONE chip"']

BAG = (225, 62, 70)
CHIP = (246, 196, 72)

# ---------- props ----------
def tv(c, t):
    c.rect(840, 1400, 1080, 1640, (110, 78, 60), w=7)
    c.line([(840, 1520), (1080, 1520)], w=5)
    c.rect(810, 1150, 1090, 1395, (30, 30, 36), w=8, r=10)
    flick = 0.5 + 0.5 * math.sin(t * 9) * math.sin(t * 3.3)
    scr = mix((90, 150, 230), (150, 120, 220), flick)
    c.rect(828, 1168, 1072, 1377, scr, ol=None, r=6)
    c.circ(900, 1250, 34, mix(scr, WHITE, 0.4), ol=None)
    c.rect(950, 1300, 1050, 1340, mix(scr, (0, 0, 0), 0.25), ol=None, r=8)
    c.glow(950, 1270, 340, (150, 170, 255), 0.25 + 0.08 * flick)

def couch(c):
    col = (90, 150, 140)
    c.rect(60, 1110, 800, 1420, mix(col, (0, 0, 0), 0.12), w=8, r=40)   # back
    c.rect(60, 1380, 800, 1600, col, w=8, r=30)                           # seat
    c.rect(30, 1260, 150, 1600, mix(col, (0, 0, 0), 0.2), w=8, r=34)      # arms
    c.rect(710, 1260, 830, 1600, mix(col, (0, 0, 0), 0.2), w=8, r=34)
    c.line([(430, 1395), (430, 1590)], w=5)
    c.rect(170, 1600, 200, 1640, INK, ol=None); c.rect(660, 1600, 690, 1640, INK, ol=None)

def chip(c, x, y, s=1.0, a=0.0):
    pts = [(x + rot(dx * s, dy * s, a)[0], y + rot(dx * s, dy * s, a)[1]) for dx, dy in ((-24, 14), (0, -22), (24, 12), (2, 20))]
    c.poly(pts, CHIP, w=4)

def bag(c, x, y, a=0.0, s=1.0, empty=False):
    def P(dx, dy): r = rot(dx * s, dy * s, a); return (x + r[0], y + r[1])
    c.poly([P(-70, -95), P(70, -95), P(80, 95), P(-80, 95)], BAG, w=6)
    for dx in range(-60, 70, 20):  # crimped top
        c.line([P(dx, -95), P(dx + 10, -105), P(dx + 20, -95)], w=5, caps=False)
    lx, ly = P(0, 10)
    c.ell(lx - 55 * s, ly - 40 * s, lx + 55 * s, ly + 40 * s, (255, 220, 80), w=5)
    c.text(lx, ly, "CHIPS", 30 * s, fill=BAG, stroke=None)
    ox, oy = P(0, -96)
    c.ell(ox - 62 * s, oy - 14 * s, ox + 62 * s, oy + 14 * s, (40, 22, 26), w=5)
    if not empty:
        for dx in (-34, -8, 22):
            chip(c, ox + dx * s, oy - 8 * s, 0.8 * s, dx * 0.03)

def sit(c, x, y, shirt=(240, 190, 60)):
    """Sitting on the couch facing camera; y = head centre."""
    hip = (x, y + 340)
    for side in (-1, 1):
        knee = (x + side * 95, y + 400); foot = (x + side * 110, 1630)
        c.line([(x + side * 30, hip[1]), knee, foot], w=14)
        c.line([foot, (foot[0] + side * 40, foot[1] + 2)], w=14)
    c.line([(x, y + 105), hip], w=14)
    c.poly([(x - 55, y + 135), (x + 55, y + 135), (x + 70, y + 210), (x + 42, y + 215), (x + 40, y + 340),
            (x - 40, y + 340), (x - 42, y + 215), (x - 70, y + 210)], shirt, w=6)

def set_(c, t):
    window(c, True, t); shelf(c, True); floor(c, True)
    lamp(c, 120, 1100, True) if False else None
    tv(c, t); couch(c)

def crumbs(c, x, y, t, n=6, rate=1.6, spread=80, seed=0):
    for i in range(n):
        r = random.Random(seed * 31 + i)
        ph = (t * rate + i / n) % 1
        cx = x + r.uniform(-1, 1) * spread * ph
        cy = y + 360 * ph * ph
        c.circ(cx, cy, 6 + r.uniform(0, 4), CHIP, w=3)

# eat cycle: returns hand target, whether chip in hand, mouth
def eat(x, y, bx, by, p):
    top = (bx + 15, by - 95); mouth = (x + 8, y + 72)
    if p < 0.4:
        k = ease(p / 0.4); return (lerp(top[0], mouth[0], k), lerp(top[1], mouth[1], k) - math.sin(k * math.pi) * 60), True, "o"
    if p < 0.55:
        return mouth, False, "grin"
    k = ease((p - 0.55) / 0.45)
    return (lerp(mouth[0], top[0], k), lerp(mouth[1], top[1], k) - math.sin(k * math.pi) * 40), False, "smile"

def body_scene(c, t, x, y, p, eyes, extra_mouth=None, tilt=0.0, brows=None, sweat=False, bag_a=0.15, chew_fast=8, blush=False, look=(0, 0)):
    sit(c, x, y)
    bx, by = x - 60, y + 300
    limb(c, (x - 10, y + 170), (bx - 50, by + 40), 115, 115, bend=1)
    bag(c, bx, by, bag_a)
    hand(c, bx - 50, by + 40, 22)
    tgt, has, mo = eat(x, y, bx, by, p)
    if mo == "grin":
        mo = "laugh" if math.sin(t * chew_fast * 2) > 0 else "smile"
    head(c, x, y, 110, tilt=tilt, eyes=eyes, mouth=extra_mouth or mo, look=look, blink=blinkf(t, 2.3),
         brows=brows, t=t, sweat=sweat, blush=blush)
    limb(c, (x + 10, y + 170), tgt, 118, 118, bend=-1)
    if has: chip(c, tgt[0] + 6, tgt[1] - 26, 1.0, t * 3)
    hand(c, *tgt, 22)
    return (bx, by), tgt

# ---------- scenes ----------
X, Y = 430, 1080

def s_one(t, dur=3.0):
    z = punch(t, lerp(1.02, 1.14, ease(t / dur)))
    c = C(*WALL_NIGHT, cam=(450, 1230, z + 0.12)); set_(c, t)
    sit(c, X, Y)
    bx, by = X - 60, Y + 300
    limb(c, (X - 10, Y + 170), (bx - 50, by + 40), 115, 115, bend=1)
    rip = ease(seg(t, 0.3, 0.7))
    bag(c, bx, by, 0.15 - 0.1 * math.sin(rip * math.pi), 1.0, empty=rip < 0.5)
    hand(c, bx - 50, by + 40, 22)
    # right hand: pulls top open, then lifts ONE chip up and inspects it
    lift = back(seg(t, 1.0, 1.5))
    tx = lerp(bx + 30, X + 200, lift); ty = lerp(by - 100, Y - 20, lift)
    head(c, X, Y, 110, tilt=-0.12 * lift, eyes="open" if t < 1.6 else "happy", mouth="smile" if t < 1.6 else "grin",
         look=(1, -0.5) if t > 1.0 else (0, 0.8), blink=blinkf(t, 2.4, 0.6), brows=-0.3 if t > 1.6 else None, t=t)
    limb(c, (X + 10, Y + 170), (tx, ty), 118, 118, bend=-1)
    if t > 0.9: chip(c, tx + 6, ty - 34, 1.3, -0.3)
    hand(c, tx, ty, 22)
    if 1.6 < t:
        for i in range(3):
            a = i * 2.1 + t * 3
            star(c, tx + 6 + math.cos(a) * 70, ty - 40 + math.sin(a) * 55, 14)
    caption(c); label(c, t, "just one.", 1650); sub(c, t, "i have self control", 1.6)
    return c.out()

def s_two(t, dur=2.6):
    z = punch(t, lerp(1.08, 1.18, ease(t / dur)))
    c = C(*WALL_NIGHT, cam=(440, 1230, z + 0.12)); set_(c, t)
    p = (t / 1.3) % 1
    n = 1 + int(t / 1.3)
    body_scene(c, t, X, Y, p, eyes="happy", tilt=math.sin(t * 3) * 0.06, blush=True)
    if p > 0.4 and p < 0.6:
        c.text(X + 220, Y - 40, "crunch", 56, fill=CHIP, sw=8)
    caption(c); label(c, t, f"chip #{n}", 1650); sub(c, t, "ok two. that's it.", 1.25)
    return c.out()

def s_more(t, dur=2.8):
    z = punch(t, lerp(1.05, 1.16, ease(t / dur)))
    c = C(*WALL_NIGHT, cam=(440, 1230, z + 0.12)); set_(c, t)
    per = 0.55
    p = (t / per) % 1
    n = 9 + int(t / per) * 2
    body_scene(c, t, X, Y, p, eyes="happy", tilt=math.sin(t * 6) * 0.08, chew_fast=12)
    crumbs(c, X, Y + 110, t, n=5, rate=1.4, seed=3)
    for i in range(3):
        ph = (t * 1.5 + i / 3) % 1
        c.text(X + 230 + ph * 30, Y - 20 - ph * 160, "crunch", 40 + 14 * (1 - ph), fill=CHIP, sw=6)
    caption(c); label(c, t, f"chip #{n}", 1650); sub(c, t, "they're small tho", 0.5)
    return c.out()

def s_frenzy(t, dur=3.0):
    rnd = random.Random(int(t * 30))
    sh = 4 + 8 * (t / dur)
    z = lerp(1.05, 1.22, ease(t / dur))
    c = C(*WALL_NIGHT, cam=(440 + rnd.uniform(-sh, sh), 1220 + rnd.uniform(-sh, sh), z + 0.1)); set_(c, t)
    per = 0.26
    p = (t / per) % 1
    n = 31 + int(t / per) * 6
    body_scene(c, t, X, Y + math.sin(t * 25) * 6, p, eyes="spiral" if (t % 1.0) < 0.5 else "wide",
               tilt=math.sin(t * 14) * 0.1, brows=0.45, sweat=True, chew_fast=20, bag_a=0.15 + math.sin(t * 20) * 0.06)
    crumbs(c, X, Y + 110, t, n=12, rate=2.4, spread=200, seed=7)
    for i in range(6):  # chips flying everywhere
        r = random.Random(i)
        ph = (t * 1.3 + i / 6) % 1
        if t < 0.2: break
        cx0 = X - 40 + r.uniform(-1, 1) * 420 * ph; cy0 = Y + 200 - 600 * ph + 760 * ph * ph
        chip(c, cx0, cy0, 1.1, ph * 9 * (1 if i % 2 else -1))
    caption(c); label(c, t, f"chip #{n}", 1650); sub(c, t, "i can stop whenever", 0.4)
    return c.out()

def s_empty(t, dur=4.6):
    reach = 0.6    # hand finds nothing
    tip = 2.3      # tips bag over mouth
    zk = ease(seg(t, reach + 0.2, reach + 0.9)) * (1 - ease(seg(t, tip - 0.2, tip + 0.2)))
    cam = (lerp(440, 400, zk), lerp(1230, 1180, zk), lerp(1.15, 1.5, zk))
    c = C(*WALL_NIGHT, cam=cam); set_(c, t)
    x, y = X, Y
    sit(c, x, y)
    if t < tip:
        # bag held up to face, peering in
        up = ease(seg(t, reach, reach + 0.4))
        bx, by = lerp(x - 60, x - 20, up), lerp(y + 300, y + 250, up)
        ba = lerp(0.15, -0.5, up)
        limb(c, (x - 10, y + 170), (bx - 50, by + 40), 115, 115, bend=1)
        bag(c, bx, by, ba, empty=True); hand(c, bx - 50, by + 40, 22)
        dig = math.sin(t * 22) * 10 if t < reach else 0
        tx, ty = (bx + 10 + dig, by - 80) if t < reach + 0.2 else (lerp(bx + 10, x + 170, ease(seg(t, reach + 0.2, reach + 0.5))), lerp(by - 80, y + 230, ease(seg(t, reach + 0.2, reach + 0.5))))
        shocked = t > reach + 0.3
        head(c, x, y, 110, tilt=0.15 * up, eyes="wide" if shocked else "open", mouth="o" if shocked else "smile",
             look=(-0.6, 0.8), brows=0.4 if shocked else None, t=t, blink=0 if shocked else blinkf(t, 2.4))
        limb(c, (x + 10, y + 170), (tx, ty), 118, 118, bend=-1); hand(c, tx, ty, 22)
        if shocked and t > reach + 0.9:
            for i, s in enumerate(("?", "?", "!")):
                k = back(seg(t, reach + 0.9 + i * 0.15, reach + 1.15 + i * 0.15))
                if k > 0.01: c.text(x + 120 + i * 55, y - 170 - (i % 2) * 30, s, 90 * k, fill=(255, 220, 60), sw=9)
    else:
        # bag upside down over open mouth, crumbs pouring in
        k = ease(seg(t, tip, tip + 0.35))
        bx, by = lerp(x - 20, x + 10, k), lerp(y + 250, y - 250, k)
        ba = lerp(-0.5, math.pi - 0.2, k) + math.sin(t * 18) * 0.08 * k
        for side in (-1, 1):
            hx, hy = bx + side * 70, by + 60
            limb(c, (x + side * 10, y + 170), (hx, hy), 160, 160, bend=-side)
        head(c, x, y, 110, tilt=-0.25 * k, eyes="closed" if k > 0.5 else "wide",
             mouth="scream" if k > 0.5 else "o", t=t)
        bag(c, bx, by, ba, empty=True)
        for side in (-1, 1): hand(c, bx + side * 70, by + 60, 22)
        if k > 0.8:
            for i in range(10):
                r = random.Random(i)
                ph = (t * 2.2 + i / 10) % 1
                c.circ(x + r.uniform(-30, 30) + 6, by + 110 + ph * (y - by - 50), 7 + r.uniform(0, 4), CHIP, w=3)
    caption(c)
    if t < tip: label(c, t - reach - 0.4, "...who ate my chips??", 1650, sz=74)
    else:
        label(c, t - tip, "the crumbs count too", 1650, sz=74)
        sub(c, t, "bag #2 tomorrow. maybe.", tip + 1.1)
    return c.out()

SCENES = [
    ("b1", 3.0, s_one),
    ("b2", 2.6, s_two),
    ("b3", 2.8, s_more),
    ("b4", 3.0, s_frenzy),
    ("b5", 4.6, s_empty),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"b1": [0.5, 2.2], "b2": [0.5, 2.0], "b3": [1.0], "b4": [1.0, 2.5], "b5": [0.3, 1.8, 2.4, 3.2, 4.3]}
        ims = [fn(tt).resize((270, 480)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (270 * 6, 480 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 6) * 270, (i // 6) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
