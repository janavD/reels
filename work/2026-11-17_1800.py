"""6pm funny reel: '5 more minutes' snooze spiral -> panic speedrun -> it's saturday."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, SKIN, WHITE, WALL_DAY, head, limb, hand, ik, floor, shelf, window, bed, blanket,
                 nightstand, label, sub, caption, punch, blinkf, back, ease, eout, seg, lerp, mix, rot, star)
from PIL import Image

rig.CAP = ['alarm: *rings*', 'me: "5 more minutes"']

RED = (225, 70, 70)
MORN = ((246, 224, 196), (222, 196, 166))   # warm early-morning wall

# ---------- props ----------
def clock(c, x, y, txt, ring=0.0, t=0.0, s=1.0):
    j = math.sin(t * 60) * 7 * ring
    a = math.sin(t * 55) * 0.12 * ring
    x += j
    for side in (-1, 1):  # bells
        bx, by = x + side * 48 * s, y - 62 * s
        c.circ(bx, by, 26 * s, (250, 200, 60), w=5)
    c.line([(x, y - 70 * s), (x, y - 92 * s)], w=6)
    c.circ(x, y - 96 * s, 9 * s, INK, ol=None)
    def P(dx, dy): r = rot(dx * s, dy * s, a); return (x + r[0], y + r[1])
    c.poly([P(-88, -55), P(88, -55), P(88, 55), P(-88, 55)], RED, w=6)
    c.rect(x - 70 * s, y - 38 * s, x + 70 * s, y + 38 * s, (30, 34, 40), w=4, r=8 * s)
    c.text(x, y, txt, 44 * s, fill=(255, 90, 90) if ring else (120, 255, 150), stroke=None)
    c.line([(x - 70 * s, y + 55 * s), (x - 80 * s, y + 75 * s)], w=7)
    c.line([(x + 70 * s, y + 55 * s), (x + 80 * s, y + 75 * s)], w=7)
    if ring > 0.3:
        c.glow(x, y, 200, (255, 120, 100), 0.25)
        for i in range(3):  # ring lines
            ph = (t * 4 + i / 3) % 1
            for side in (-1, 1):
                rx = x + side * (110 + ph * 50) * s
                c.arc(rx - 30, y - 90 - 30, rx + 30, y - 90 + 30, 200 if side < 0 else -20, 340 if side < 0 else 20 + 120, w=6)

def ringtxt(c, x, y, t, start=0.0):
    k = back(seg(t, start, start + 0.2))
    if k > 0.01:
        c.text(x, y, "RIIING", 64 * k, fill=(255, 220, 60), sw=9)

def bedroom(c, t):
    window(c, False, t); shelf(c, False); floor(c, False)
    nightstand(c, False)

def zzz(c, x, y, t, n=3):
    for i in range(n):
        ph = (t * 0.8 + i / n) % 1
        c.text(x + ph * 90 + math.sin(ph * 6) * 12, y - ph * 200, "z", 40 + 40 * ph, fill=WHITE, sw=6)

HX, HY = 315, 1235
CLK = (100, 1362)

def sleeper(c, t, eyes="closed", mouth="drool", slap=None, tilt=0.0, kick=0.0, look=(0, 0), brows=None, sweat=False):
    """lying in bed; slap = 0..1 arm progress toward the clock (None = arm under blanket)."""
    bed(c, False)
    head(c, HX, HY, 105, tilt=tilt, eyes=eyes, mouth=mouth, look=look, t=t, brows=brows, sweat=sweat)
    blanket(c, False, kick=kick)
    if slap is not None and slap > 0.03:
        sh = (430, 1320)
        rest = (520, 1300)
        tgt = (lerp(rest[0], CLK[0] + 10, slap), lerp(rest[1], CLK[1] - 70, slap) - math.sin(slap * math.pi) * 120)
        e = ik(*sh, *tgt, 190, 190, -1); c.line([sh, e, tgt], w=14)
        hand(c, *tgt, 24)

def slap_curve(t, hits):
    """arm goes out and back for each hit time; returns progress 0..1."""
    best = 0.0
    for h in hits:
        if h - 0.35 < t < h + 0.35:
            best = max(best, ease(seg(t, h - 0.3, h)) if t < h else 1 - ease(seg(t, h + 0.08, h + 0.35)))
    return best

def stand(c, x, y, t, run=0.0, armL=None, armR=None, shirt=(90, 160, 230), backwards=False):
    hip = (x, y + 360)
    c.ell(x - 140, 1625, x + 140, 1655, mix((178, 128, 86), (0, 0, 0), 0.25), ol=None)
    for side in (-1, 1):
        ph = math.sin(t * 22 + (0 if side < 0 else math.pi)) * run
        fx = x + side * 60 + ph * 70; fy = 1630 - max(0, ph) * 90
        limb(c, hip, (fx, fy), 118, 118, bend=side)
        c.line([(fx, fy), (fx + side * 40, fy + 2)], w=14)
    c.line([(x, y + 105), hip], w=14)
    c.poly([(x - 55, y + 135), (x + 55, y + 135), (x + 70, y + 210), (x + 42, y + 215), (x + 40, y + 340),
            (x - 40, y + 340), (x - 42, y + 215), (x - 70, y + 210)], shirt, w=6)
    if backwards:  # tag sticking out the front
        c.rect(x - 14, y + 140, x + 14, y + 170, WHITE, w=4)
    sh = (x, y + 170)
    for tgt, b in ((armL, 1), (armR, -1)):
        if tgt is None: continue
        limb(c, sh, tgt, 115, 115, bend=b); hand(c, *tgt, 22)

def sock(c, x, y, a, col=(240, 240, 240)):
    def P(dx, dy): r = rot(dx, dy, a); return (x + r[0], y + r[1])
    c.poly([P(-20, -60), P(20, -60), P(20, 20), P(60, 30), P(60, 60), P(-20, 60)], col, w=5)
    c.line([P(-20, -40), P(20, -40)], w=5, fill=RED)

# ---------- scenes ----------
def s_alarm(t, dur=3.2):
    z = punch(t, lerp(1.05, 1.16, ease(t / dur)))
    c = C(*MORN, cam=(380, 1220, z + 0.05)); bedroom(c, t)
    ring = 1.0 if t < 1.4 else 0.0
    sl = slap_curve(t, [1.4])
    sleeper(c, t, eyes="closed", mouth="flat" if 0.6 < t < 1.7 else "drool", slap=sl if t > 1.0 else None,
            brows=0.3 if 0.5 < t < 1.6 else None, tilt=math.sin(t * 2) * 0.03)
    clock(c, *CLK, "7:00", ring, t)
    if ring: ringtxt(c, 160, 1120, t, 0.1)
    if 1.4 < t < 1.75:
        c.text(CLK[0] + 60, CLK[1] - 180, "SLAP", 80 * back(seg(t, 1.4, 1.55)), fill=WHITE, sw=10)
    if t > 1.9: zzz(c, 420, 1100, t)
    caption(c); label(c, t, "7:00 AM"); sub(c, t, "just 5 more minutes", 1.8)
    return c.out()

def s_snooze2(t, dur=2.4):
    z = punch(t, lerp(1.1, 1.2, ease(t / dur)))
    c = C(*MORN, cam=(370, 1230, z + 0.05)); bedroom(c, t)
    ring = 1.0 if t < 0.9 else 0.0
    sl = slap_curve(t, [0.9])
    sleeper(c, t, eyes=("half", "closed") if t < 1.2 else "closed", mouth="frown" if t < 1.2 else "drool",
            slap=sl if t > 0.5 else None, tilt=-0.08)
    clock(c, *CLK, "7:05", ring, t)
    if ring: ringtxt(c, 160, 1120, t)
    if 0.9 < t < 1.25:
        c.text(CLK[0] + 60, CLK[1] - 180, "SLAP", 80 * back(seg(t, 0.9, 1.05)), fill=WHITE, sw=10)
    if t > 1.3: zzz(c, 420, 1100, t)
    caption(c); label(c, t, "7:05 AM"); sub(c, t, "ok 5 MORE", 1.2)
    return c.out()

TIMES = ["7:10", "7:15", "7:20", "7:25", "7:35", "7:45", "7:55", "8:10", "8:25"]
def s_spiral(t, dur=2.8):
    rnd = random.Random(int(t * 30))
    z = lerp(1.12, 1.28, ease(t / dur))
    c = C(*MORN, cam=(330 + rnd.uniform(-3, 3), 1260, z)); bedroom(c, t)
    per = dur / len(TIMES)
    i = min(len(TIMES) - 1, int(t / per))
    hits = [per * (k + 0.6) for k in range(len(TIMES))]
    sl = slap_curve(t, hits)
    bed(c, False)
    # blanket pulled fully over the head: a lump with hair tuft peeking
    col = (82, 118, 185)
    br = math.sin(t * 3) * 6
    c.poly([(150, 1250 - br), (250, 1140 - br), (420, 1150 - br), (560, 1240), (760, 1250), (990, 1262),
            (1010, 1450), (160, 1460)], col, w=7)
    c.line([(300, 1170), (330, 1330)], w=5, fill=mix(col, (0, 0, 0), 0.28))
    c.line([(620, 1300), (760, 1400)], w=5, fill=mix(col, (0, 0, 0), 0.28))
    sh = (430, 1250)
    tgt = (lerp(470, CLK[0] + 10, sl), lerp(1250, CLK[1] - 70, sl) - math.sin(sl * math.pi) * 100)
    e = ik(*sh, *tgt, 190, 190, -1); c.line([sh, e, tgt], w=14); hand(c, *tgt, 24)
    c.poly([(395, 1255), (470, 1255), (470, 1300), (395, 1300)], col, ol=None)  # sleeve hole
    ringing = (t % per) < per * 0.6
    clock(c, *CLK, TIMES[i], 1.0 if ringing else 0.0, t)
    caption(c)
    with c.ui():
        k = back(seg(t, 0.05, 0.3))
        c.text(540, 1650, f"snooze x{i + 3}", 88 * k, sw=10)
    sub(c, t, "i'm resting my eyes", 0.6)
    return c.out()

def s_wake(t, dur=3.0):
    pop = 1.1
    rnd = random.Random(int(t * 30))
    sh = 10 if t > pop else 0
    zk = ease(seg(t, 0, pop))
    c = C(*MORN, cam=(lerp(330, 300, zk) + rnd.uniform(-sh, sh), lerp(1250, 1230, zk) + rnd.uniform(-sh, sh),
                      lerp(1.15, 1.45, zk) - 0.2 * ease(seg(t, pop, pop + 0.3)))); bedroom(c, t)
    if t < pop:
        sleeper(c, t, eyes=("half", "closed") if t < 0.6 else ("half", "half"), mouth="flat", look=(-1, 0.5), tilt=0.05)
    else:
        sleeper(c, t, eyes="wide", mouth="scream", look=(-1, 0.6), tilt=math.sin(t * 30) * 0.06,
                kick=abs(math.sin(t * 18)) * 50, brows=0.5, sweat=True)
    clock(c, *CLK, "8:52", 0.0, t, s=1.0 + 0.25 * back(seg(t, pop, pop + 0.25)))
    if t > pop:
        k = back(seg(t, pop, pop + 0.2))
        c.text(180, 1060, "!!!", 110 * k, fill=(255, 220, 60), sw=10)
    caption(c)
    if t > pop:
        label(c, t - pop, "8:52 AM", sz=100); sub(c, t, "i start at 9", pop + 0.5)
    return c.out()

def s_speedrun(t, dur=3.4):
    rnd = random.Random(int(t * 30))
    c = C(*MORN, cam=(540 + rnd.uniform(-7, 7), 1200 + rnd.uniform(-7, 7), 1.0 + 0.06 * (1 - eout(seg(t, 0, 0.3)))))
    window(c, False, t); shelf(c, False); floor(c, False)
    # clothes flying across
    for i in range(5):
        r = random.Random(i + 40)
        ph = (t * 0.9 + i / 5) % 1
        x0 = -100 + ph * 1300; y0 = 700 + r.uniform(0, 300) - math.sin(ph * math.pi) * 200
        if i % 2: sock(c, x0, y0, ph * 10)
        else:
            c.poly([(x0 - 50, y0 - 40), (x0 + 50, y0 - 40), (x0 + 60, y0 + 50), (x0 - 60, y0 + 50)],
                   (240, 190, 60) if i == 0 else (130, 200, 140), w=5)
    x = 540 + math.sin(t * 5) * 140; y = 1050 + abs(math.sin(t * 22)) * -14
    # arms: left scrubs teeth, right flails holding a shoe
    brush = (x + 30 + math.sin(t * 40) * 25, y + 75)
    shoe = (x + 190 + math.sin(t * 9) * 30, y + 60 + math.cos(t * 9) * 60)
    stand(c, x, y, t, run=1.0, armL=None, armR=shoe, backwards=True)
    c.ell(shoe[0] - 10, shoe[1] - 50, shoe[0] + 90, shoe[1] - 10, (60, 60, 70), w=5)
    head(c, x, y, 110, tilt=math.sin(t * 14) * 0.1, eyes="wide", mouth="grit", look=(1, 0), brows=0.5, sweat=True, t=t)
    # sock on head
    sock(c, x + 20, y - 130, 1.3)
    # toothbrush + foam
    c.line([(brush[0] - 70, brush[1] + 40), brush], w=12, fill=(120, 200, 255))
    for i in range(5):
        a = t * 10 + i * 1.3
        c.circ(x + math.cos(a) * 38, y + 78 + math.sin(a) * 12, 13, WHITE, w=3)
    limb(c, (x, y + 170), (brush[0] - 70, brush[1] + 40), 115, 115, bend=1); hand(c, brush[0] - 70, brush[1] + 40, 22)
    caption(c); label(c, t, "any% speedrun"); sub(c, t, "shirt's on backwards", 1.3)
    return c.out()

def s_saturday(t, dur=4.6):
    see = 0.5; flop = 2.4
    if t < flop:
        zk = ease(seg(t, see, see + 0.5))
        c = C(*MORN, cam=(lerp(540, 600, zk), lerp(1200, 1080, zk), lerp(1.0, 1.25, zk)))
        window(c, False, t); shelf(c, False); floor(c, False)
        x, y = 470, 1050
        ph = (x + 170, y + 30)
        stand(c, x, y, t, armL=(x - 40, y + 330), armR=ph, backwards=True)
        # phone
        c.rect(ph[0] - 60, ph[1] - 200, ph[0] + 60, ph[1] + 20, (34, 34, 40), w=6, r=16)
        c.rect(ph[0] - 50, ph[1] - 188, ph[0] + 50, ph[1] + 8, (150, 205, 255), ol=None, r=10)
        c.text(ph[0], ph[1] - 140, "9:01", 30, fill=INK, stroke=None)
        c.text(ph[0], ph[1] - 80, "SAT", 44, fill=RED, stroke=None)
        c.glow(ph[0], ph[1] - 90, 220, (160, 210, 255), 0.3)
        hand(c, *ph, 22)
        frozen = t > see
        head(c, x, y, 110, tilt=0.05, eyes="open" if not frozen else "wide", mouth="grit" if not frozen else "flat",
             look=(1, -0.3), t=t, blink=0, sweat=not frozen, brows=None if frozen else 0.5)
        sock(c, x + 20, y - 130, 1.3)
        if t > see + 0.6:
            for i in range(3):
                k = back(seg(t, see + 0.6 + i * 0.25, see + 0.85 + i * 0.25))
                if k > 0.01: c.text(x - 200 + i * 40, y - 150 - i * 30, ".", 120 * k, fill=WHITE, sw=10)
        caption(c); label(c, t - see, "...it's saturday", sz=84)
    else:
        tt = t - flop
        z = punch(tt, lerp(1.08, 1.18, ease(tt / (dur - flop))), 0.12)
        c = C(*MORN, cam=(400, 1220, z)); bedroom(c, t)
        bounce = math.sin(seg(tt, 0, 0.4) * math.pi * 2) * (1 - seg(tt, 0, 0.6)) * 25
        sleeper(c, t, eyes="happy" if tt < 0.9 else "closed", mouth="grin" if tt < 0.9 else "drool",
                tilt=0.08, kick=bounce, )
        clock(c, *CLK, "9:01", 0.0, t)
        if tt > 0.8: zzz(c, 420, 1100, t)
        with c.ui():
            for i in range(3):
                a = tt * 3 + i * 2.1
                star(c, 330 + math.cos(a) * 160, 1090 + math.sin(a) * 40, 16)
        caption(c); label(c, 1, "...it's saturday", sz=84); sub(c, tt, "5 more HOURS", 0.4)
    return c.out()

SCENES = [
    ("c1", 3.2, s_alarm),
    ("c2", 2.4, s_snooze2),
    ("c3", 2.8, s_spiral),
    ("c4", 3.0, s_wake),
    ("c5", 3.4, s_speedrun),
    ("c6", 4.6, s_saturday),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"c1": [0.4, 1.4, 2.6], "c2": [0.9], "c3": [1.0, 2.5], "c4": [0.5, 1.8], "c5": [0.6, 2.0],
                 "c6": [1.6, 3.6]}
        ims = [fn(tt).resize((270, 480)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (270 * 6, 480 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 6) * 270, (i // 6) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
