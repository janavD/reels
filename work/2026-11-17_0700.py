"""7am motivational reel: day 1 vs day 90 of learning guitar. Sour notes + sore fingers, string snaps,
mom 'make it stop', day 31 wants to quit -> calluses, grind montage, day 90 open mic applause."""
import sys, math, random, os
sys.path.insert(0, 'engine'); sys.path.insert(0, 'engine/library')
import rig
from rig import (C, INK, SKIN, WHITE, WALL_DAY, WALL_NIGHT, head, limb, hand, ik, floor, label, caption,
                 punch, blinkf, back, ease, eout, seg, lerp, mix, rot, star, window, shelf, bed, nightstand)
from night_noise import cat
from quiet_morning import burst
from PIL import Image

rig.CAP = ["day 1 vs day 90 of", "learning guitar"]

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

# ---------- scenes ----------
def s_day1(t, dur=9.0):
    z = punch(t, lerp(1.0, 1.1, ease(t / dur)))
    c = C(*WALL_DAY, cam=(560, 1180, z))
    leave = ease(seg(t, 4.2, 5.4))
    bedroom(c, t, 1, cat_x=lerp(880, 1250, leave), cat_eyes="half" if t > 2.0 else "open")
    ow = 5.6 < t
    if not ow:
        player(c, t, strum=3.0 if (0.0 < t < 1.2 or 2.4 < t < 3.6) else 0.0, fret=340,
               eyes="wide" if t > 1.2 else "open", mouth="grit" if t > 1.2 else "smile",
               brows=0.4 if t > 1.2 else None, sweat=t > 2.4, tilt=math.sin(t * 10) * 0.04 if t > 2.4 else 0)
        float_notes(c, t, 660, 1150, n=4, sour=True, spd=0.8, seed=1)
    else:
        sh = math.sin(t * 30) * 25
        B = player(c, t, strum=0, la=(370 + sh, 960), eyes="x" if t < 6.6 else "closed", mouth="frown", brows=-0.3,
                   tilt=0.1)
        red_tips(c, 370 + sh, 960, t)
    if t < 2.4: burst(c, 300, 1000, "CLUNK", t, 0.5, sz=100, fill=(200, 200, 200))
    if 2.6 < t < 4.3: burst(c, 820, 950, "BWOOONG", t, 2.6, sz=92, fill=(200, 200, 200))
    if 4.3 < t < 5.6: burst(c, 900, 1060, "nope.", t, 4.3, sz=70, fill=WHITE)
    if t > 5.6: burst(c, 760, 960, "ow ow ow", t, 5.65, sz=80, fill=RED)
    caption(c); label(c, t, "Day 1")
    subs(c, t, [(0.6, "this sounds... wrong"), (3.0, "even the cat left"), (5.8, "my fingers HURT")])
    return c.out()

def s_day9(t, dur=8.0):
    snap = 3.6
    rnd = random.Random(int(t * 30))
    shk = 18 * (1 - seg(t, snap, snap + 0.5)) if t > snap else 0
    zk = ease(seg(t, 0.2, snap))
    c = C(*WALL_DAY, cam=(420 + rnd.uniform(-shk, shk), lerp(1150, 1080, zk), lerp(1.12, 1.45, zk)))
    bedroom(c, t, 9)
    pre = t < snap
    B = player(c, t, strum=0, fret=380 if pre else 360, eyes="wide" if pre else ("x" if t < snap + 1.6 else "half"),
               mouth="grit" if pre else ("o" if t < snap + 1.6 else "flat"), brows=0.5 if pre else -0.2, sweat=pre,
               look=(-1, 0.3) if pre else (0, 0), tilt=-0.05 if pre else 0.12 * math.sin(t * 4))
    if pre:
        # twisting the tuning peg harder and harder
        k = seg(t, 0.4, snap)
        px, py = gp(B, 480, 34)
        c.circ(px, py, 14, (230, 230, 230), w=4)
        for i in range(3):
            a = t * (6 + 12 * k) + i * 2.1
            c.line([(px + math.cos(a) * 30, py + math.sin(a) * 30), (px + math.cos(a) * 44, py + math.sin(a) * 44)], w=5)
        burst(c, 260, 780, "tighter...", t, 0.6, sz=64, fill=WHITE, wob=False)
        if t > 2.2: burst(c, 300, 860, "TIGHTER", t, 2.2, sz=80, fill=GOLD)
    else:
        tt = t - snap
        wh = 1 - seg(tt, 0, 0.5)
        if wh > 0:
            a0 = gp(B, 435, 9)
            pts = [a0] + [(a0[0] + 60 * i + math.sin(tt * 40 + i) * 50 * wh, a0[1] - 40 * i * wh + 30 * i) for i in range(1, 6)]
            c.line(pts, w=4, fill=(240, 240, 240))
        if tt > 0.25:  # band-aid on the forehead
            hx, hy = 600, 975
            c.rect(hx - 70, hy - 90, hx + 70, hy - 55, (245, 200, 160), w=4, r=14)
            c.line([(hx - 15, hy - 72), (hx + 15, hy - 72)], w=4, fill=(220, 170, 130))
        burst(c, 560, 760, "PING!", tt, 0.0, sz=130, fill=GOLD)
        for i in range(3):
            aa = tt * 6 + i * 2.1
            star(c, 600 + math.cos(aa) * 160, 860 + math.sin(aa) * 35, 18)
    caption(c); label(c, t, "Day 9")
    subs(c, t, [(0.5, "learning to tune it"), (snap + 0.2, "the string fought back"), (snap + 2.4, "still showed up")])
    return c.out()

def s_day20(t, dur=9.0):
    z = punch(t, lerp(1.0, 1.06, ease(t / dur)))
    c = C(*WALL_DAY, cam=(560, 1170, z))
    shelf(c, False); daycard(c, 20); floor(c, False)
    op = ease(seg(t, 1.6, 2.1)) * (1 - ease(seg(t, 5.2, 5.6)))
    door(c, 660, op)
    if op > 0.05:
        mx = lerp(1000, 880, op)
        mom(c, 880, 900, t, mouth="smile" if t < 4.2 else "flat", eyes="happy" if t < 4.2 else "half",
            thumb=seg(t, 2.5, 2.9) * (1 - seg(t, 4.2, 4.6)))
        door(c, 660, op) if False else None
        c.rect(660, 600, 680, 1300, (250, 244, 232), ol=None)
    bed(c, False)
    stop = t > 5.6
    player(c, t, strum=0 if stop else 2.2, fret=300 + 40 * math.sin(t * 1.3),
           eyes=("happy" if t < 5.6 else "open"), mouth="smile" if not stop else "frown",
           brows=-0.3 if t > 6.4 else None, blush=2.5 < t < 5.6, bob=6 if not stop else 0,
           look=(1, -0.4) if 2 < t < 5.6 else (0, 0), blink=blinkf(t, 3, 0.4))
    if not stop: float_notes(c, t, 640, 1150, n=4, sour=(int(t * 2) % 2 == 0), spd=0.6, seed=2)
    if 2.6 < t < 4.4: burst(c, 860, 720, "so nice sweetie!", t, 2.6, sz=56, fill=WHITE, wob=False)
    if t > 6.0:
        k = back(seg(t, 6.0, 6.3))
        c.rect(700, 700 - 60 * k, 1060, 700 + 60 * k, WHITE, w=6, r=40 * k)
        c.text(880, 690, "(muffled)", 30 * k, fill=(140, 140, 140), stroke=None)
        c.text(880, 728, "make it stop", 42 * k, fill=INK, stroke=None)
    caption(c); label(c, t, "Day 20")
    subs(c, t, [(0.5, "played for my mom"), (6.2, "...she was being nice")])
    return c.out()

def s_day31(t, dur=11.0):
    look = 4.2; grab = 8.0
    z = punch(t, lerp(1.04, 1.22, ease(t / grab)) if t < grab else 1.08)
    c = C(*WALL_NIGHT, cam=(570, 1150, z))
    bedroom(c, t, 31, night=True)
    if t < grab:
        c.glow(260, 1300, 300, (255, 210, 120), 0.0)
        leaning_guitar(c, 950, 1640)
        if t < look:
            player(c, t, guitar_on=False, la=(560, 1260), ra=(640, 1260), eyes="half", mouth="frown",
                   brows=-0.3, look=(0, 1), blink=blinkf(t, 2.6, 0.3), tilt=0.05)
            phone(c, 600, 1230)
            cloud(c, t, 600, 760)
            with c.ui():
                k = back(seg(t, 0.8, 1.1))
                if k > 0.01:
                    c.rect(160, 1430, 920, 1530, WHITE, w=6, r=30)
                    c.text(540, 1480, "how long to learn guitar", 40 * min(1, k), fill=INK, stroke=None)
        else:
            tt = t - look
            hx, hy = 470, 1000
            player(c, t, guitar_on=False, la=(hx, hy), ra=(680, 1300), eyes="wide" if tt > 1.2 else "open",
                   mouth="o" if tt > 1.2 else "flat", look=(-1, 0.2), brows=0.3 if tt > 1.2 else None)
            hand(c, hx, hy, 30)
            for i, a in enumerate((-2.2, -1.75, -1.35, -0.95)):
                fx, fy = hx + math.cos(a) * 46, hy + math.sin(a) * 46
                c.line([(hx + math.cos(a) * 20, hy + math.sin(a) * 20), (fx, fy)], w=18, fill=INK)
                c.line([(hx + math.cos(a) * 20, hy + math.sin(a) * 20), (fx, fy)], w=10, fill=SKIN)
                c.circ(fx, fy, 9, (235, 215, 170), w=3)
            if tt > 1.2:
                c.glow(hx, hy - 30, 180, (255, 240, 180), 0.35 + 0.1 * math.sin(t * 6))
                for i in range(3):
                    aa = t * 3 + i * 2.1
                    star(c, hx + math.cos(aa) * 110, hy - 40 + math.sin(aa) * 60, 14)
    else:
        tt = t - grab
        player(c, t, strum=0, fret=340, eyes="open", mouth="flat", brows=0.5, look=(-1, 0.3),
               blink=blinkf(tt, 3, 1.0))
    caption(c); label(c, t, "Day 31")
    subs(c, t, [(0.4, "wanted to quit"), (2.2, "maybe i'm not musical"), (look + 1.3, "wait... it doesn't hurt"),
                (look + 2.6, "calluses. it's working"), (grab + 0.2, "ok. again.")])
    return c.out()

def s_grind(t, dur=12.0):
    d0, d1 = 32, 89
    k = t / dur
    day = int(lerp(d0, d1 + 0.99, k))
    night = (day // 6) % 2 == 1
    z = 1.04 + 0.03 * math.sin(t * 2)
    c = C(*(WALL_NIGHT if night else WALL_DAY), cam=(560, 1170, z))
    cx = lerp(1250, 880, ease(seg(t, 2.0, 8.5)))
    bedroom(c, t, day, night=night, cat_x=cx, cat_eyes="closed" if t > 9 else "open")
    nightstand(c, night) if False else None
    metronome(c, 120, 1630, t, bpm=lerp(60, 120, k))
    player(c, t, strum=lerp(1.0, 3.0, k), fret=300 + 60 * math.sin(t * lerp(1, 4, k)), eyes="closed" if k > 0.5 else "open",
           mouth="flat" if k < 0.6 else "smile", brows=0.3 if k < 0.6 else None, bob=lerp(0, 8, k),
           look=(-1, 0.4) if k < 0.5 else (0, 0), blink=blinkf(t, 2.5))
    float_notes(c, t, 650, 1150, n=int(lerp(3, 7, k)), sour=k < 0.4, spd=lerp(0.5, 1.0, k), seed=3)
    with c.ui():
        c.text(540, 1460, "first song", 40, fill=WHITE, sw=6)
        c.rect(240, 1500, 840, 1545, WHITE, w=6, r=20)
        c.rect(246, 1506, 246 + 588 * (k * 0.95 + 0.04), 1539, (70, 200, 110), ol=None, r=16)
    caption(c); label(c, t, "kept practicing")
    subs(c, t, [(0.4, "15 minutes a day"), (2.6, "slow. then slower."), (5.0, "same 3 chords"),
                (7.4, "even when it sounded bad"), (9.8, "every. single. day.")])
    return c.out()

CROWD = [(x, random.Random(x).uniform(0, 6)) for x in range(-40, 1200, 150)]

def s_stage(t, dur=11.0):
    play = 3.0; clap = 7.4
    zk = ease(seg(t, 0.0, play))
    shk = 6 * (1 - seg(t, play - 0.3, play)) if t < play else 0
    c = C(*STAGE, cam=(560, lerp(1080, 1180, zk) if t < clap else 1180, lerp(1.32, 1.0, zk)))
    for x0, s in ((-200, 1), (1080, -1)):  # curtains
        c.rect(x0, 380, x0 + 200 * 1.0 + (0 if s > 0 else 0), 1650, (170, 40, 60), w=7)
        for fx in range(x0 + 40, x0 + 200, 50): c.line([(fx, 400), (fx, 1640)], w=5, fill=(120, 26, 44), caps=False)
    c.rect(-200, 380, 1280, 580, (150, 30, 50), w=7)
    c.text(540, 520, "OPEN MIC NIGHT", 50, fill=GOLD, sw=6)
    c.rect(-600, 1600, 1700, 2600, (120, 80, 54), ol=None); c.line([(-600, 1600), (1700, 1600)], w=8)
    c.glow(600, 1200, 620, (255, 240, 200), 0.32 + (0.1 * math.sin(t * 5) if t > clap else 0))
    # stool
    c.rect(500, 1335, 700, 1370, (60, 60, 70), w=6, r=10)
    for lx in (520, 680): c.line([(lx, 1370), (lx + (lx - 600) * 0.3, 1600)], w=12, fill=(60, 60, 70))
    # mic stand
    c.line([(880, 1600), (880, 1100), (770, 1020)], w=10, fill=(70, 70, 80))
    c.ell(840, 1585, 920, 1610, (70, 70, 80), w=5)
    c.ell(735, 985, 795, 1045, (60, 60, 66), w=6)
    nerv = t < play
    player(c, t, strum=0 if nerv else 2.6, fret=320 + 50 * math.sin(t * 2.5), shake=4 if nerv else 0,
           eyes="wide" if nerv else ("closed" if t < clap else "happy"), mouth="grit" if nerv else ("smile" if t < clap else "grin"),
           brows=0.5 if nerv else None, sweat=nerv, look=(0, 0.5) if nerv else (0, 0), bob=0 if nerv else 7,
           blush=t > clap, tilt=0.06 * math.sin(t * 2) if not nerv else 0)
    if not nerv: float_notes(c, t, 600, 1120, n=7, spd=0.9, spread=520, seed=4)
    # crowd
    sway = 0 if t < play + 1 else 1
    for i, (x, ph) in enumerate(CROWD):
        jump = abs(math.sin(t * 8 + ph)) * 30 if t > clap else 0
        bx = x + math.sin(t * 2.5 + ph) * 18 * sway
        c.circ(bx, 1820 - jump, 95, (34, 26, 48), ol=None)
        c.rect(bx - 120, 1870 - jump, bx + 120, 2300, (34, 26, 48), ol=None)
        if t > clap and i % 2 == 0:
            hy = 1640 - jump + math.sin(t * 16 + ph) * 20
            c.circ(bx - 40, hy, 26, (34, 26, 48), ol=None); c.circ(bx + 40, hy + 10, 26, (34, 26, 48), ol=None)
    if t > clap:
        tt = t - clap
        for i in range(6):
            ph = (tt * 0.8 + i / 6) % 1
            hx = 150 + i * 160 + math.sin(tt * 3 + i) * 30; hy = 1500 - ph * 600
            s = 26 * (1 - ph * 0.4)
            c.circ(hx - s * 0.5, hy, s * 0.6, RED, ol=None); c.circ(hx + s * 0.5, hy, s * 0.6, RED, ol=None)
            c.poly([(hx - s * 1.08, hy + s * 0.15), (hx + s * 1.08, hy + s * 0.15), (hx, hy + s * 1.2)], RED, ol=None)
        burst(c, 260, 760, "CLAP", tt, 0.0, sz=90, fill=GOLD)
        burst(c, 820, 700, "CLAP CLAP", tt, 0.35, sz=80, fill=GOLD)
        burst(c, 540, 820, "WOOO!", tt, 0.8, sz=96, fill=WHITE)
    caption(c); label(c, t, "Day 90")
    subs(c, t, [(0.4, "my first open mic"), (1.6, "hands shaking..."), (play + 0.4, "and then i just played"),
                (clap + 0.3, "they CLAPPED"), (clap + 2.0, "day 1 me would cry")])
    return c.out()

def s_end(t, dur=7.0):
    z = punch(t, lerp(1.0, 1.07, ease(t / dur)))
    c = C(*WALL_DAY, cam=(560, 1180, z))
    bedroom(c, t, 91, cat_x=880, cat_eyes="closed")
    player(c, t, strum=1.6, fret=330 + 40 * math.sin(t * 1.5), eyes="happy", mouth="smile", bob=5, blush=True,
           tilt=0.05 * math.sin(t * 2))
    float_notes(c, t, 660, 1150, n=5, spd=0.6, seed=5)
    for i in range(2):
        ph = (t * 0.7 + i / 2) % 1
        hx, hy, s = 900 + math.sin(t * 2 + i) * 20, 1100 - ph * 250, 18
        c.circ(hx - s * 0.5, hy, s * 0.6, RED, ol=None); c.circ(hx + s * 0.5, hy, s * 0.6, RED, ol=None)
        c.poly([(hx - s * 1.08, hy + s * 0.15), (hx + s * 1.08, hy + s * 0.15), (hx, hy + s * 1.2)], RED, ol=None)
    burst(c, 900, 1260 - 220, "purr", t, 1.0, sz=50, fill=WHITE, wob=False) if t < 3 else None
    caption(c)
    with c.ui():
        k = back(seg(t, 0.3, 0.6))
        if k > 0.01: c.text(540, 1650, "start bad.", 92 * k, fill=WHITE, sw=10)
    subs(c, t, [(1.4, "just keep showing up"), (4.4, "follow for day 180")])
    return c.out()

SCENES = [
    ("g1", 9.0, s_day1),
    ("g2", 8.0, s_day9),
    ("g3", 9.0, s_day20),
    ("g4", 11.0, s_day31),
    ("g5", 12.0, s_grind),
    ("g6", 11.0, s_stage),
    ("g7", 7.0, s_end),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"g1": [1.0, 6.0], "g2": [3.0, 4.5], "g3": [3.0, 6.5], "g4": [1.5, 6.0], "g5": [3.0, 10.5], "g6": [1.5, 8.5], "g7": [2.0]}
        ims = [fn(tt).resize((270, 480)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (270 * 7, 480 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 7) * 270, (i // 7) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
