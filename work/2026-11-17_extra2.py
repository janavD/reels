"""Extra funny reel: brain replays a cringe memory from 2019 at 3am."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, SKIN, WHITE, head, hand, ik, label, sub, caption, punch, blinkf, back,
                 ease, eout, seg, lerp, mix, star, bed, blanket, nightstand, room, WALL_NIGHT)
from PIL import Image

rig.CAP = ['me trying to sleep', 'and my brain at 3am:']

RED = (225, 70, 70)
PINK = (255, 160, 180)
BLK = (58, 76, 132)          # night blanket colour
HX, HY = 315, 1235           # head on pillow

# ---------- helpers ----------
def cloud(c, t, start, cx=470, cy=800, w=310, h=200):
    k = back(seg(t, start, start + 0.35))
    if k <= 0.01: return 0
    w *= k; h *= k
    # thought trail from head
    for i, (fx, r) in enumerate(((0.25, 14), (0.5, 22), (0.75, 30))):
        if k > 0.3 + i * 0.15:
            x = lerp(HX + 40, cx - w * 0.25, fx); y = lerp(HY - 125, cy + h * 0.95, fx)
            c.circ(x, y, r, WHITE, w=5)
    puffs = [(-0.75, -0.35, 0.42), (-0.3, -0.62, 0.48), (0.25, -0.62, 0.48), (0.72, -0.35, 0.42),
             (0.8, 0.25, 0.4), (0.35, 0.6, 0.45), (-0.25, 0.62, 0.45), (-0.78, 0.28, 0.4)]
    for (px, py, pr) in puffs: c.circ(cx + px * w, cy + py * h, pr * h * 1.2, WHITE, w=6)
    for (px, py, pr) in puffs: c.circ(cx + px * w, cy + py * h, pr * h * 1.2 - 7, WHITE, ol=None)
    c.ell(cx - w * 0.92, cy - h * 0.72, cx + w * 0.92, cy + h * 0.72, WHITE, ol=None)
    return k

def mini_person(c, x, y, t, r=38, arm_up=None, mouth="smile", eyes="open", shirt=(240, 150, 70), bow=False, look=(0, 0)):
    c.line([(x, y + r), (x, y + r + 95)], w=8)
    c.line([(x, y + r + 95), (x - 26, y + r + 150)], w=8); c.line([(x, y + r + 95), (x + 26, y + r + 150)], w=8)
    c.poly([(x - 26, y + r + 8), (x + 26, y + r + 8), (x + 22, y + r + 80), (x - 22, y + r + 80)], shirt, w=4)
    sh = (x, y + r + 22)
    for side in (-1, 1):
        if arm_up == side:
            wv = math.sin(t * 16) * 18
            tgt = (x + side * 62 + wv, y - 10)
        else:
            tgt = (x + side * 38, y + r + 88)
        c.line([sh, tgt], w=8); c.circ(*tgt, 11, SKIN, w=4)
    head(c, x, y, r, eyes=eyes, mouth=mouth, look=look, t=t)
    if bow:
        c.poly([(x - 18, y + r + 2), (x, y + r + 12), (x - 18, y + r + 22)], INK, ol=None)
        c.poly([(x + 18, y + r + 2), (x, y + r + 12), (x + 18, y + r + 22)], INK, ol=None)

def tiny_text(c, x, y, s, t, start, sz=30, fill=INK):
    k = back(seg(t, start, start + 0.25))
    if k > 0.01: c.text(x, y, s, sz * k, fill=fill, stroke=None)

def brain(c, x, y, t, r=70):
    bob = math.sin(t * 4) * 6; y += bob
    c.ell(x - r * 1.25, y - r, x + r * 1.25, y + r * 0.9, PINK, w=6)
    for dx, dy in ((-50, -30), (10, -45), (40, 10), (-30, 25)):
        c.arc(x + dx - 22, y + dy - 14, x + dx + 22, y + dy + 14, 180, 360, w=4, fill=mix(PINK, INK, 0.4))
    c.line([(x, y - r + 8), (x, y + r * 0.8)], w=4, fill=mix(PINK, INK, 0.4), caps=False)
    c.arc(x - 44, y - 6, x - 16, y + 18, 200, 340, w=6); c.arc(x + 16, y - 6, x + 44, y + 18, 200, 340, w=6)
    c.arc(x - 20, y + 14, x + 20, y + 44, 20, 160, w=6)
    c.line([(x + r * 1.1, y), (x + r * 1.1 + 40, y - 40 + math.sin(t * 12) * 10)], w=8)  # waving arm
    c.circ(x + r * 1.1 + 40, y - 40 + math.sin(t * 12) * 10, 12, PINK, w=4)

def sleeper(c, t, eyes="closed", mouth="smile", kick=0.0, tilt=0.0, cover=0.0, brows=None, sweat=False, look=(0, 0),
            squash=1.0, yoff=0.0):
    bed(c, True)
    head(c, HX, HY + yoff, 105, tilt=tilt, eyes=eyes, mouth=mouth, brows=brows, sweat=sweat, look=look, t=t, squash=squash)
    blanket(c, True, kick=kick)
    if cover > 0.01:  # blanket pulled up over the mouth
        top = lerp(1300, 1250, cover)
        c.poly([(170, top + 10), (300, top - 6), (440, top + 6), (520, top + 40), (540, 1330), (180, 1330)], BLK, w=7)
        for side in (-1, 1):
            hx = HX + side * 70; c.circ(hx, top + 14, 22, SKIN, w=6)   # fists gripping blanket

def base(t, z, cx=470, cy=1150, shake=0.0):
    r = random.Random(int(t * 30))
    c = C(*WALL_NIGHT, cam=(cx + r.uniform(-shake, shake), cy + r.uniform(-shake, shake), z))
    room(c, True, t, None)
    return c

# ---------- scenes ----------
def s_sleep(t, dur=2.8):
    z = punch(t, lerp(1.05, 1.12, ease(t / dur)))
    c = base(t, z)
    br = math.sin(t * 2.2) * 6
    sleeper(c, t, eyes="closed", mouth="smile", yoff=br * 0.3)
    for i in range(3):
        ph = (t * 0.7 + i / 3) % 1
        if t > 0.4: c.text(440 + ph * 140 + i * 8, 1120 - ph * 240, "z", 46 + ph * 50, fill=WHITE, sw=6)
    caption(c); label(c, t, "2:47 AM"); sub(c, t, "finally... sleep", 0.5)
    return c.out()

def s_waiter(t, dur=3.6):
    z = punch(t, lerp(1.08, 1.16, ease(t / dur)))
    c = base(t, z)
    pop = 1.95
    if t < pop:
        sleeper(c, t, eyes="closed", mouth="smile" if t < 1.2 else "flat")
    else:
        jolt = (1 - eout(seg(t, pop, pop + 0.25))) * 30
        sleeper(c, t, eyes="wide", mouth="o", brows=0.4, yoff=-jolt, look=(1, -0.6))
        c.text(HX + 150, HY - 170, "!", 130 * back(seg(t, pop, pop + 0.2)), fill=(255, 220, 60), sw=10)
    k = cloud(c, t, 0.2)
    if k > 0.9:
        mini_person(c, 360, 790, t, shirt=WHITE, bow=True, mouth="smile", look=(1, 0))
        mini_person(c, 590, 790, t, mouth="grin" if t > 1.3 else "smile", look=(-1, 0))
        tiny_text(c, 395, 660, "enjoy your meal!", t, 0.6, 35)
        tiny_text(c, 610, 690, "you too!", t, 1.2, 44, fill=RED)
        tiny_text(c, 230, 920, "2019", t, 0.6, 30, fill=(120, 120, 140))
    caption(c); label(c, t, "2:48 AM"); sub(c, t, "brain: remember this?", 0.5)
    return c.out()

def s_cringe(t, dur=3.0):
    z = lerp(1.1, 1.2, ease(t / dur))
    c = base(t, z, shake=9)
    kick = abs(math.sin(t * 16)) * 60
    tilt = math.sin(t * 18) * 0.25
    sleeper(c, t, eyes="closed", mouth="scream", kick=kick, tilt=tilt, brows=0.5, squash=0.94 + 0.06 * math.sin(t * 30))
    # flailing fists above blanket
    for side, ph in ((-1, 0), (1, math.pi)):
        sh = (440 + side * 30, 1330)
        tx = 500 + side * 90 + math.sin(t * 20 + ph) * 40; ty = 1170 + math.cos(t * 20 + ph) * 45
        e = ik(*sh, tx, ty, 95, 95, -side); c.line([sh, e, (tx, ty)], w=14); hand(c, tx, ty, 22)
    for i in range(3):
        k = back(seg(t, 0.15 + i * 0.25, 0.4 + i * 0.25))
        if k > 0.01:
            c.text(260 + i * 170, 960 - i * 70 + math.sin(t * 40 + i) * 6, "A" * (3 + i), (70 + i * 10) * k, fill=WHITE, sw=9)
    caption(c); label(c, t, "2:49 AM"); sub(c, t, "it was 7 years ago", 0.6)
    return c.out()

def s_wave(t, dur=3.6):
    z = punch(t, lerp(1.08, 1.15, ease(t / dur)))
    c = base(t, z)
    cov = ease(seg(t, 1.9, 2.4))
    sleeper(c, t, eyes="wide", mouth="frown", brows=0.4, cover=cov, sweat=t > 2.2, look=(1, -0.6))
    k = cloud(c, t, 0.15)
    if k > 0.9:
        mini_person(c, 670, 800, t, arm_up=-1, mouth="grin", shirt=(110, 180, 120), look=(-1, 0))
        mini_person(c, 480, 800, t, arm_up=1 if t > 0.9 else None, mouth="grin" if t > 0.9 else "smile",
                    look=(1, 0))
        mini_person(c, 290, 800, t, arm_up=-1 if t > 1.4 else None, mouth="grin", shirt=(170, 110, 200), look=(1, 0))
        if t < 1.5: tiny_text(c, 660, 690, "heyyy!", t, 0.5, 40)
        if t > 1.4:
            kk = eout(seg(t, 1.4, 1.7))
            c.line([(640, 735), (lerp(640, 320, kk), 735)], w=7, fill=RED)
            if kk > 0.95: c.poly([(305, 735), (335, 720), (335, 750)], RED, ol=None)
            tiny_text(c, 480, 665, "(not at me)", t, 1.6, 42, fill=RED)
    caption(c); label(c, t, "3:12 AM"); sub(c, t, "brain: and this one", 0.5)
    return c.out()

def alarm(c, t, ring, x=60, y=1430):
    jx = math.sin(t * 90) * 7 if ring else 0
    cx0 = x + jx; h = 90
    c.circ(cx0 - 38, y - h - 12, 18, RED, w=5); c.circ(cx0 + 38, y - h - 12, 18, RED, w=5)
    c.rect(cx0 - 55, y - h, cx0 + 55, y, RED, w=6, r=20)
    c.rect(cx0 - 40, y - h + 14, cx0 + 40, y - 14, (25, 25, 30), w=4, r=6)
    c.text(cx0, y - h / 2, "7:00", 26, fill=(255, 80, 80), stroke=None)
    if ring:
        for i in range(3):
            r0 = 70 + i * 22 + (t * 200) % 22
            c.arc(cx0 - r0, y - 50 - r0, cx0 + r0, y - 50 + r0, 200, 250, w=5, fill=(255, 230, 120))
            c.arc(cx0 - r0, y - 50 - r0, cx0 + r0, y - 50 + r0, 290, 340, w=5, fill=(255, 230, 120))
        c.glow(cx0, y - 50, 200, (255, 120, 100), 0.25 * (0.5 + 0.5 * math.sin(t * 40)))

def s_morning(t, dur=3.8):
    z = punch(t, lerp(1.04, 1.12, ease(t / dur)))
    c = C((150, 180, 220), (120, 140, 180), cam=(430, 1150, z))
    room(c, False, t, None)
    nightstand(c, False)
    ring = 0.2 < t < 2.4
    alarm(c, t, ring)
    bed(c, False)
    head(c, HX, HY, 105, tilt=-0.1 + math.sin(t * 3) * 0.04, eyes="spiral", mouth="flat", t=t)
    blanket(c, False)
    # dark circles under eyes
    for sx in (-40, 40): c.arc(HX + sx - 24, HY - 6, HX + sx + 24, HY + 20, 20, 160, w=5, fill=(140, 120, 170))
    k = cloud(c, t, 1.0, cx=440, cy=820, w=270, h=180)
    if k > 0.9:
        brain(c, 420, 840, t)
        tiny_text(c, 440, 715, "ok goodnight :)", t, 1.35, 42)
    caption(c); label(c, t, "7:00 AM"); sub(c, t, "thanks brain", 1.8)
    return c.out()

SCENES = [
    ("c1", 2.8, s_sleep),
    ("c2", 3.6, s_waiter),
    ("c3", 3.0, s_cringe),
    ("c4", 3.6, s_wave),
    ("c5", 3.8, s_morning),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"c1": [1.5], "c2": [1.5, 2.6], "c3": [0.4, 1.5], "c4": [1.5, 3.0], "c5": [0.5, 2.5]}
        ims = [fn(tt).resize((360, 640)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (360 * 5, 640 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 5) * 360, (i // 5) * 640))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
