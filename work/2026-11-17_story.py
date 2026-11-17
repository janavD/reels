"""Extra story reel w/ voiceover: making mom breakfast in bed for her birthday (pancake on ceiling, fire,
smoke alarm, flour ghost, mom walks in, laughs on the floor, cereal together, pancake falls on my head)."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, WHITE, head, limb, hand, ik, floor, window, label, sub, caption,
                 punch, blinkf, back, ease, eout, seg, lerp, mix, rot, star, glow_img)
from PIL import Image

rig.CAP = ["i tried making my mom", "breakfast in bed", "for her birthday"]

SKIN0 = rig.SKIN
WALL = ((214, 236, 226), (186, 214, 202))       # minty kitchen
SHIRT = (90, 150, 220)
APRON = (250, 250, 246)
ROBE = (236, 140, 170)
HAIR = (96, 62, 44)
PANCAKE = (232, 178, 96)
FLOUR = (246, 244, 238)
GOLD = (255, 205, 60)
PAN_X, PAN_Y = 800, 1352
CEIL_PC = (800, 452)          # where pancake #1 is stuck

# ---------- set ----------
def tiles(c):
    for y in range(1180, 1360, 45):
        for x in range(330, 1140, 70):
            c.rect(x + (35 if (y // 45) % 2 else 0) - 35, y, x + 35 + (35 if (y // 45) % 2 else 0), y + 45,
                   (238, 246, 242), w=2, ol=(170, 196, 186))

def door(c, open_k=1.0):
    c.rect(20, 640, 320, 1645, (250, 244, 232), w=7)
    c.rect(48, 668, 292, 1645, (126, 104, 90), w=6)        # dark hallway
    c.rect(48, 668, 292, 900, (110, 90, 80), ol=None)
    # door leaf swinging open (shrinks toward hinge on the left)
    wdt = 244 * (1 - open_k) + 26 * open_k
    c.rect(48, 668, 48 + wdt, 1645, (236, 196, 150), w=6)
    if open_k < 0.6: c.circ(48 + wdt - 30, 1180, 12, GOLD, w=4)

def cabinets(c):
    for x0 in (340, 480):
        c.rect(x0, 470, x0 + 135, 740, (250, 250, 244), w=6, r=8)
        c.line([(x0 + 105, 590), (x0 + 105, 640)], w=7)

def ceiling(c):
    c.rect(-600, -900, 1700, 440, (232, 240, 236), ol=None)
    c.line([(-600, 440), (1700, 440)], w=7)

def smoke_alarm(c, t, on=False):
    c.ell(410, 432, 530, 470, WHITE, w=6)
    lit = on and (t * 4) % 1 < 0.5
    c.circ(470, 452, 8, (255, 60, 60) if lit else (150, 150, 150), ol=None)
    if lit: c.glow(470, 455, 160, (255, 80, 80), 0.45)

def ceil_pancake(c, t, k=1.0, drip=True):
    if k <= 0: return
    x, y = CEIL_PC
    c.ell(x - 80 * k, y - 8, x + 80 * k, y + 22 * k, PANCAKE, w=6)
    if drip:
        ph = (t * 0.6) % 1
        dy = 22 + ph * 50
        c.ell(x + 20 - 7, y + 10, x + 20 + 7, y + dy, PANCAKE, ol=INK, w=4)

def counter(c):
    c.rect(330, 1380, 1160, 1660, (150, 196, 186), w=7)
    for x0 in (360, 640, 920):
        c.rect(x0, 1430, x0 + 240, 1630, (166, 210, 200), w=5, r=6)
        c.line([(x0 + 100, 1470), (x0 + 140, 1470)], w=7)
    c.rect(310, 1356, 1180, 1396, (245, 236, 220), w=7, r=6)   # top

def stove(c):
    c.ell(PAN_X - 110, PAN_Y - 2, PAN_X + 110, PAN_Y + 22, (60, 60, 66), w=5)

def pan(c, contents=None, t=0.0, tilt=0.0):
    hx = PAN_X - 120
    c.line([(PAN_X - 90, PAN_Y - 12), (hx - 70, PAN_Y - 22 - tilt * 40)], w=16)
    c.ell(PAN_X - 100, PAN_Y - 30 - tilt * 10, PAN_X + 100, PAN_Y + 6, (70, 72, 82), w=7)
    c.ell(PAN_X - 82, PAN_Y - 26 - tilt * 10, PAN_X + 82, PAN_Y - 2, (40, 42, 50), ol=None)
    if contents == "pancake":
        c.ell(PAN_X - 58, PAN_Y - 28, PAN_X + 58, PAN_Y - 6, PANCAKE, w=5)
    elif contents == "burnt":
        c.ell(PAN_X - 58, PAN_Y - 28, PAN_X + 58, PAN_Y - 6, (60, 40, 30), w=5)
        c.ell(PAN_X - 20, PAN_Y - 22, PAN_X + 20, PAN_Y - 12, (250, 236, 200), ol=None)   # raw middle

def flame(c, x, y, s, t):
    if s <= 0.02: return
    for k, col in ((1.0, (240, 90, 40)), (0.7, (255, 170, 40)), (0.42, (255, 236, 120))):
        pts = []
        for i in range(9):
            a = math.pi + i * math.pi / 8
            ww = 90 * s * k
            hh = (170 + 60 * math.sin(t * 13 + i * 1.7)) * s * k if i % 2 else 50 * s * k
            pts.append((x + math.cos(a) * ww, y + math.sin(a) * hh))
        pts.append((x + 90 * s * k, y)); pts.append((x - 90 * s * k, y))
        c.poly(pts, col, ol=INK if k == 1.0 else None, w=5)
    c.glow(x, y - 80 * s, int(300 * s) + 1, (255, 160, 60), 0.4)

def kitchen(c, t, door_k=0.0, alarm=False, pancake_k=1.0, drip=True):
    window(c, False, t); ceiling(c); cabinets(c); smoke_alarm(c, t, alarm)
    ceil_pancake(c, t, pancake_k, drip)
    floor(c, False); door(c, door_k); tiles(c)

def smoke(c, t, amt):
    for i in range(7):
        ph = (t * 0.25 + i / 7) % 1
        x = 820 + math.sin(t + i * 1.9) * 120 - ph * 250
        y = 1300 - ph * 820
        r = (30 + ph * 55) * amt
        if r > 3: c.circ(x, y, r, mix((170, 172, 180), WALL[0], ph * 0.7), ol=None)

# ---------- characters ----------
class ghost:
    def __enter__(self): rig.SKIN = FLOUR
    def __exit__(self, *a): rig.SKIN = SKIN0

def chef(c, x, y, t, armL, armR, bendL=1, bendR=-1, spatula=None, hat=True, flour=False, **face):
    """standing behind the counter (legs hidden). arm targets in world coords."""
    shirt = FLOUR if flour else SHIRT
    c.line([(x, y + 100), (x, y + 260)], w=14)
    c.poly([(x - 60, y + 128), (x + 60, y + 128), (x + 70, y + 230), (x + 62, y + 420), (x - 62, y + 420), (x - 70, y + 230)], shirt, w=6)
    c.poly([(x - 40, y + 170), (x + 40, y + 170), (x + 50, y + 420), (x - 50, y + 420)], FLOUR if flour else APRON, w=5)
    c.line([(x - 40, y + 172), (x - 22, y + 135)], w=4, caps=False); c.line([(x + 40, y + 172), (x + 22, y + 135)], w=4, caps=False)
    for (tgt, b, side) in ((armL, bendL, -1), (armR, bendR, 1)):
        sh = (x + side * 42, y + 150)
        e = ik(*sh, *tgt, 118, 118, b); c.line([sh, e, tgt], w=14, fill=INK)
    if spatula:
        sx, sy, a = spatula
        ex, ey = sx + math.cos(a) * 120, sy + math.sin(a) * 120
        c.line([(sx, sy), (ex, ey)], w=9, fill=(70, 60, 60))
        px, py = rot(0, 34, 0)
        pts = [(ex + rot(dx, dy, a)[0], ey + rot(dx, dy, a)[1]) for dx, dy in ((0, -30), (70, -34), (70, 34), (0, 30))]
        c.poly(pts, (190, 194, 204), w=5)
    for tgt in (armL, armR): hand(c, *tgt, 22)
    head(c, x, y, 110, t=t, **face)
    if hat:
        hx, hy = x + math.sin(face.get('tilt', 0)) * 100, y - 100
        c.rect(hx - 70, hy - 50, hx + 70, hy + 4, WHITE, w=6, r=6)
        for dx in (-50, 0, 50): c.circ(hx + dx, hy - 64, 44, WHITE, w=6)
        c.rect(hx - 66, hy - 60, hx + 66, hy - 2, WHITE, ol=None)

def mom(c, x, y, t, armL=None, armR=None, robe=ROBE, legs=True, **face):
    if legs:
        for side in (-1, 1):
            c.line([(x + side * 30, y + 430), (x + side * 34, y + 560)], w=14)
            c.ell(x + side * 34 - 36 + side * 12, y + 548, x + side * 34 + 36 + side * 12, y + 582, (250, 200, 220), w=6)
    c.line([(x, y + 100), (x, y + 200)], w=14)
    c.poly([(x - 62, y + 130), (x + 62, y + 130), (x + 92, y + 450), (x - 92, y + 450)], robe, w=6)
    c.line([(x, y + 140), (x - 22, y + 300), (x + 40, y + 450)], w=5, caps=False)
    c.line([(x - 80, y + 300), (x + 82, y + 300)], w=7)     # belt
    armL = armL or (x - 90, y + 330); armR = armR or (x + 90, y + 330)
    for tgt, side in ((armL, -1), (armR, 1)):
        sh = (x + side * 48, y + 150)
        e = ik(*sh, *tgt, 118, 118, -side); c.line([sh, e, tgt], w=14)
        hand(c, *tgt, 21)
    momhead(c, x, y, t, **face)

def momhead(c, x, y, t, r=106, **face):
    tilt = face.get('tilt', 0.0)
    bx, by = x + math.sin(tilt) * 125, y - 128 * math.cos(tilt)
    c.circ(bx, by, 46, HAIR, w=6)
    head(c, x, y, r, t=t, **face)
    k = r / 110
    # hair cap (rotated chord approximated with poly)
    pts = []
    for i in range(17):
        a = math.pi + i * math.pi / 16
        pts.append((math.cos(a) * 114 * k, math.sin(a) * 112 * k - 14 * k))
    pts.append((112 * k, 30 * k)); pts.append((88 * k, -40 * k)); pts.append((-20 * k, -62 * k)); pts.append((-112 * k, 30 * k))
    pts = [(x + rot(px, py, tilt)[0], y + rot(px, py, tilt)[1]) for px, py in pts]
    c.poly(pts, HAIR, w=6)

def sitter(c, x, t, shirt, legs_dir=1, armL=None, armR=None, momstyle=False, **face):
    hy = 1262
    hip = (x, 1612)
    for dx in (0, 22):
        fx = x + legs_dir * (210 + dx)
        limb(c, hip, (fx, 1628), 125, 125, bend=-legs_dir)
        c.line([(fx, 1628), (fx + legs_dir * 30, 1600)], w=14)
    c.line([(x, hy + 100), hip], w=14)
    c.poly([(x - 56, hy + 128), (x + 56, hy + 128), (x + 66, hy + 360), (x - 66, hy + 360)], shirt, w=6)
    if momstyle: c.line([(x - 62, hy + 280), (x + 62, hy + 280)], w=7)
    armL = armL or (x - 80, 1600); armR = armR or (x + 80, 1600)
    for tgt, side in ((armL, -1), (armR, 1)):
        sh = (x + side * 44, hy + 150)
        e = ik(*sh, *tgt, 112, 112, -side); c.line([sh, e, tgt], w=14)
        hand(c, *tgt, 21)
    if momstyle: momhead(c, x, hy, t, **face)
    else: head(c, x, hy, 110, t=t, **face)

def bowl(c, x, y, spoon=0.0):
    c.chord(x - 70, y - 50, x + 70, y + 60, 0, 180, (240, 110, 110), w=6)
    c.line([(x - 72, y + 5), (x + 72, y + 5)], w=6)
    for i in range(6): c.circ(x - 45 + i * 18, y - 2 - (i % 2) * 8, 10, GOLD, w=3)

def hearts(c, t, x, y, n=4):
    for i in range(n):
        ph = (t * 0.45 + i / n) % 1
        hx = x + math.sin(t * 2 + i * 2) * 60 + (i - n / 2) * 70
        hy = y - ph * 380
        s = 26 * (1 - ph * 0.4)
        c.circ(hx - s * 0.5, hy, s * 0.6, (240, 90, 120), ol=None)
        c.circ(hx + s * 0.5, hy, s * 0.6, (240, 90, 120), ol=None)
        c.poly([(hx - s * 1.08, hy + s * 0.15), (hx + s * 1.08, hy + s * 0.15), (hx, hy + s * 1.3)], (240, 90, 120), ol=None)

def pop_text(c, t, x, y, s, start, sz=90, col=GOLD, dur=0.6):
    if start <= t < start + dur:
        with c.ui(): c.text(x, y, s, sz * back(seg(t, start, start + 0.2)), fill=col, sw=10)

CX, CY = 560, 1000      # chef position

# ---------- scenes ----------
def k1(t, dur=7.0):
    z = punch(t, lerp(1.0, 1.1, ease(t / dur)))
    c = C(*WALL, cam=(600, 1150, z)); kitchen(c, t, pancake_k=0)
    counter(c); stove(c); pan(c)
    # bowl of batter on counter + mixing
    c.chord(360, 1260, 520, 1400, 180, 360, (240, 240, 250), w=6)
    c.line([(356, 1330), (524, 1330)], w=6)
    bob = math.sin(t * 5) * 6
    mixing = t < 3.4
    if mixing:
        wx, wy = 440 + math.cos(t * 12) * 30, 1300 + math.sin(t * 12) * 10
        armL = (wx, wy); c.line([(wx, wy), (wx + 20, 1335)], w=7, fill=(160, 160, 170))
    else:
        armL = (CX - 150, CY + 300)
    thumbs = seg(t, 3.6, 3.9)
    armR = (lerp(CX + 140, CX + 190, back(thumbs)), lerp(CY + 320, CY + 90, back(thumbs)))
    chef(c, CX, CY + bob, t, armL, armR, eyes="happy" if 3.9 < t < 6 else "open", mouth="grin" if t > 3.6 else "smile",
         look=(-1, 0.6) if mixing else (0, 0), blink=blinkf(t, 2.6), tilt=math.sin(t * 3) * 0.05, brows=-0.2 if t > 3.6 else None)
    if thumbs > 0.5:  # thumb
        c.ell(armR[0] - 10, armR[1] - 48, armR[0] + 10, armR[1] - 14, SKIN0, w=5)
        sp = 1 - seg(t, 3.9, 4.4)
        if sp > 0:
            for a in range(4):
                ang = a * math.pi / 2 + t * 4
                c.line([(armR[0] + 60 + math.cos(ang) * 10, armR[1] - 70 + math.sin(ang) * 10),
                        (armR[0] + 60 + math.cos(ang) * 36 * sp, armR[1] - 70 + math.sin(ang) * 36 * sp)], w=6, fill=GOLD)
    caption(c)
    label(c, t, "6:00 AM")
    sub(c, t, "chef mode: ON", 3.7)
    return c.out()

FLIP = 2.2
def k2(t, dur=9.0):
    # camera looks up during the flight, then holds
    up = ease(seg(t, FLIP, FLIP + 0.5)) * (1 - ease(seg(t, 5.6, 6.4)))
    z = punch(t, 1.0)
    cam = (600, lerp(1150, 900, up), z)
    if FLIP + 0.6 < t < FLIP + 0.75: cam = (cam[0] + random.Random(int(t * 99)).uniform(-12, 12), cam[1], cam[2])
    c = C(*WALL, cam=cam)
    stuck = t > FLIP + 0.6
    kitchen(c, t, pancake_k=back(seg(t, FLIP + 0.6, FLIP + 0.8)) if stuck else 0, drip=t > FLIP + 2)
    counter(c); stove(c)
    # pan tilt flick
    flick = math.sin(math.pi * seg(t, FLIP - 0.25, FLIP + 0.1))
    second = t > 6.6
    pan(c, "pancake" if (t < FLIP or (second and t > 7.4)) else None, t, tilt=flick)
    # flying pancake
    if FLIP <= t < FLIP + 0.6:
        f = seg(t, FLIP, FLIP + 0.6)
        px, py = lerp(PAN_X, CEIL_PC[0], f), lerp(PAN_Y - 20, CEIL_PC[1] + 10, eout(f))
        sq = abs(math.cos(f * 9))
        c.ell(px - 60, py - 14 - 30 * (1 - sq), px + 60, py + 14 + 30 * (1 - sq), PANCAKE, w=5)
        for i in range(3): c.line([(px - 40 + i * 40, py + 40), (px - 40 + i * 40, py + 110)], w=5, fill=WHITE)
    # chef
    look_up = t > FLIP
    hold = (PAN_X - 190, PAN_Y - 22 - flick * 40)
    if t > 6.0 and not (second and t > 7.4):
        armR = (lerp(hold[0], 700, seg(t, 6.0, 6.6)), lerp(hold[1], 1250, seg(t, 6.0, 6.6)))  # pours again
    else:
        armR = hold
    shrug = math.sin(math.pi * seg(t, 5.0, 6.0))
    armL = (CX - 160 - shrug * 30, CY + 300 - shrug * 200)
    eyes = "wide" if FLIP + 0.5 < t < 5.0 else "open"
    mouth = "o" if FLIP + 0.5 < t < 4.2 else ("flat" if t < 6.0 and t > FLIP else "smile")
    chef(c, CX, CY, t, armL, armR, eyes=eyes, mouth=mouth, look=(1, -1) if look_up and t < 5.6 else (1, 0.5),
         tilt=-0.15 * ease(seg(t, FLIP, FLIP + 0.4)) * (1 - seg(t, 5.0, 5.6)), blink=blinkf(t, 3.1, 1.0))
    if 6.0 < t < 7.4:
        c.chord(650, 1170, 760, 1250, 0, 180, (240, 240, 250), w=5)       # batter bowl in hand
        c.line([(690, 1250), (700, 1340)], w=12, fill=(250, 236, 200))
    if FLIP + 0.6 <= t < FLIP + 1.2:
        with c.ui(): c.text(800, 520 + (900 - cam[1]) * 0, "SPLAT", 90 * back(seg(t, FLIP + 0.6, FLIP + 0.8)), fill=GOLD, sw=10)
    caption(c)
    label(c, t, "pancake #1")
    sub(c, t, "still up there", 4.3)
    return c.out()

FIRE = 2.5
def k3(t, dur=8.5):
    z = punch(t, lerp(1.04, 1.16, ease(t / dur)))
    c = C(*WALL, cam=(640, 1180, z)); kitchen(c, t)
    counter(c); stove(c); pan(c, "burnt", t)
    blow = seg(t, 4.3, 4.9)
    out_ = 4.9 < t < 5.7
    fire = 0 if t < FIRE else back(seg(t, FIRE, FIRE + 0.4))
    if t > 4.6: fire *= max(0.0, 1 - seg(t, 4.6, 4.9))
    if t > 5.7: fire = back(seg(t, 5.7, 6.0)) * 1.25
    flame(c, PAN_X, PAN_Y - 24, fire, t)
    if out_:  # little smoke wisp
        k = seg(t, 4.9, 5.7)
        c.line([(PAN_X, PAN_Y - 30), (PAN_X + 20 * math.sin(t * 9), PAN_Y - 30 - 160 * k)], w=8, fill=(150, 150, 158))
    lean = ease(seg(t, 3.9, 4.3)) * (1 - ease(seg(t, 5.0, 5.4)))
    x = CX + 70 * lean
    poke = (PAN_X - 150 + math.sin(t * 6) * 10, PAN_Y - 60)
    armR = (x + 150, CY + 330) if t > FIRE else poke
    armL = (x - 150, CY + 300)
    if t > 6.0:  # hands on cheeks panic
        armL, armR = (x - 95, CY + 40), (x + 95, CY + 40)
    if 4.3 < t < 4.9:
        eyes, mouth = "closed", "o"
        puff = seg(t, 4.3, 4.9)
        for i in range(3):
            c.line([(x + 120 + puff * 60, CY + 30 + i * 30), (x + 170 + puff * 110, CY + 50 + i * 40)], w=5, fill=WHITE)
    elif out_:
        eyes, mouth = "happy", "grin"
    elif t > FIRE:
        eyes, mouth = "wide", "scream" if t > 5.8 else "o"
    else:
        eyes, mouth = "half", "flat"
    chef(c, x, CY - 20 * lean, t, armL, armR, spatula=(armR[0], armR[1], 0.15) if t < FIRE else None,
         eyes=eyes, mouth=mouth, look=(1, 0.5), sweat=t > 5.8, tilt=0.2 * lean + (math.sin(t * 30) * 0.04 if t > 5.8 else 0),
         brows=0.4 if t > 5.8 else None)
    if out_: sub(c, t, "phew", 4.95)
    if 5.7 < t < 6.4:
        with c.ui(): c.text(850, 980, "FWOOSH", 84 * back(seg(t, 5.7, 5.9)), fill=(255, 140, 40), sw=10)
    caption(c)
    label(c, t, "pancake #2")
    if t > 6.0: sub(c, t, "trick candle?!", 6.0)
    return c.out()

POOF = 6.1
def k4(t, dur=12.0):
    rnd = random.Random(int(t * 30))
    shake = 6 if t < POOF else 0
    z = punch(t, lerp(1.02, 1.12, ease(t / dur)))
    cam = (600 + rnd.uniform(-shake, shake), 1140 + rnd.uniform(-shake, shake), z)
    if POOF < t < POOF + 0.2: cam = (cam[0] + rnd.uniform(-18, 18), cam[1] + rnd.uniform(-18, 18), cam[2])
    c = C(*WALL, cam=cam)
    alarm = t < 10.5
    kitchen(c, t, alarm=alarm)
    smoke(c, t, 1 - seg(t, 8.5, 11.5))
    if alarm:
        for i in range(3):
            r0 = 60 + i * 26 + (t * 220) % 26
            c.arc(470 - r0, 452 - r0, 470 + r0, 452 + r0, 30, 150, w=5, fill=(255, 90, 90))
        if (t * 2) % 1 < 0.5:
            with c.ui(): c.text(250, 560, "BEEP", 64, fill=(255, 90, 90), sw=8)
    counter(c); stove(c); pan(c, "burnt", t)
    floured = t > POOF
    fan = t < 4.3
    if fan:
        a = -1.2 + math.sin(t * 18) * 0.6
        armR = (CX + 130, CY - 40); armL = (CX - 150, CY + 280)
        spat = (armR[0], armR[1], a)
    elif t < POOF:  # grabs the flour bag and shakes it
        k = seg(t, 4.3, 4.8)
        armR = (lerp(CX + 130, CX + 110, k), lerp(CY - 40, CY - 30 + math.sin(t * 25) * 30 * seg(t, 5.0, POOF), k))
        armL = (lerp(CX - 150, CX + 60, k), lerp(CY + 280, CY + 0, k))
        spat = None
    else:
        armL, armR = (CX - 150, CY + 320), (CX + 150, CY + 320)
        spat = None
    if floured:
        with ghost():
            chef(c, CX, CY, t, armL, armR, flour=True, hat=True,
                 eyes="open" if t > POOF + 0.6 else "closed", mouth="flat" if t > POOF + 1.0 else "o",
                 blink=blinkf(t, 1.4) if t > POOF + 0.6 else 0, look=(0, 0), tilt=math.sin(t * 2) * 0.04)
        for i in range(3):   # cough puffs
            ph = (t * 0.9 + i / 3) % 1
            if t > POOF + 1.2: c.circ(CX + 120 + ph * 120, CY + 30 - ph * 80, 16 + ph * 26, FLOUR, w=3)
    else:
        chef(c, CX, CY, t, armL, armR, spatula=spat, eyes="wide", mouth="scream" if (t % 0.8) < 0.5 else "grit",
             look=(-0.6, -1), sweat=True, brows=0.45, tilt=math.sin(t * 11) * 0.06)
    if not fan and not floured:   # flour bag in hands
        bx, by = armR[0] - 30, armR[1] - 10
        c.rect(bx - 60, by - 30, bx + 60, by + 120, (236, 226, 200), w=6, r=10)
        c.text(bx, by + 50, "FLOUR", 30, fill=INK, stroke=None)
    # poof cloud
    if t > POOF - 0.05:
        k = eout(seg(t, POOF - 0.05, POOF + 0.5)); fade = 1 - seg(t, POOF + 0.6, POOF + 2.2)
        if fade > 0:
            for i in range(14):
                a = i * 2 * math.pi / 14
                r = 320 * k
                c.circ(CX + math.cos(a) * r * 0.8, CY + 150 + math.sin(a) * r * 0.6, (110 - 30 * (i % 3)) * fade + 1, FLOUR, w=4)
            c.circ(CX, CY + 120, 230 * k * fade + 1, FLOUR, ol=None)
    pop_text(c, t, 540, 920, "POOF", POOF, 120, WHITE, 0.8)
    caption(c)
    if t < POOF: label(c, t, "6:01 AM"); sub(c, t, "panic mode", 1.8)
    else: label(c, t - POOF, "ghost mode"); sub(c, t, "*cough*", POOF + 1.4)
    return c.out()

DOOR, LOOK1, LOOK2 = 0.3, 2.1, 3.3
def k5(t, dur=9.5):
    z = punch(t, lerp(1.0, 1.07, ease(t / dur)))
    c = C(*WALL, cam=(560, 1150, z))
    dk = ease(seg(t, DOOR, DOOR + 0.6))
    kitchen(c, t, door_k=dk)
    smoke(c, t, 0.25)
    # mom in doorway
    if t > DOOR + 0.4:
        mx = lerp(120, 175, ease(seg(t, DOOR + 0.4, 1.3)))
        if t < LOOK1: look = (0, 0)
        elif t < LOOK2: look = (1, -1)                 # the kitchen / ceiling
        else: look = (1, 0.2)                          # at me
        mouth = "flat"
        if t > 8.3: mouth = "smile" if (t * 6) % 1 < 0.5 else "flat"   # trying not to laugh
        mom(c, mx, 1045, t, eyes="open" if t < 4.2 else "half", mouth=mouth, look=look,
            blink=blinkf(t, 3.0, 1.5) if t < 4.2 else 0, armL=(mx - 95, 1360), armR=(mx + 95, 1360))
        if t > 4.6:
            with c.ui():
                k = back(seg(t, 4.6, 4.9))
                c.rect(175 - 90 * k, 830 - 50 * k, 175 + 90 * k, 830 + 50 * k, WHITE, w=6, r=34 * k)
                c.text(175, 828, "...", 60 * k, fill=INK, stroke=None)
    counter(c); stove(c); pan(c, "burnt", t)
    wave_ = seg(t, 5.6, 8.6)
    with ghost():
        armR = (CX + 150, CY + 320)
        if wave_ > 0 and wave_ < 1:
            armL = (CX - 170 + math.sin(t * 10) * 30, CY - 40)
        else:
            armL = (CX - 150, CY + 320)
        chef(c, CX, CY, t, armL, armR, flour=True, eyes="open", mouth="grit" if t > 5.5 else "flat",
             look=(-1, 0), blink=blinkf(t, 2.2), tilt=-0.08, sweat=t > 5.0)
    caption(c)
    if t > 1.0: label(c, t - 1.0, "mom.")
    if t > 5.6: sub(c, t, "hi mom :)", 5.6)
    return c.out()

def k6(t, dur=6.5):
    z = punch(t, lerp(1.0, 1.08, ease(t / dur)))
    c = C(*WALL, cam=(560, 1150, z)); kitchen(c, t, door_k=1)
    sit = ease(seg(t, 1.2, 2.2))
    shake = math.sin(t * 24) * 8
    if sit < 0.5:
        mom(c, 175, 1045 + 300 * sit * 2 + shake * 0.5, t, eyes="happy", mouth="laugh", tilt=math.sin(t * 6) * 0.1, blush=True,
            armL=(110, 1370 + 300 * sit), armR=(240, 1280 + 300 * sit), legs=sit < 0.2)
    else:
        sitter(c, 170, t, ROBE, legs_dir=1, momstyle=True, eyes="happy", mouth="laugh", blush=True,
               tilt=math.sin(t * 6) * 0.1, armL=(110, 1600), armR=(240 + shake, 1440))
    if t > 0.4:
        for i in range(3):
            ph = (t * 1.2 + i / 3) % 1
            c.text(300 + i * 30 + ph * 40, 900 - ph * 200 + (300 if sit > 0.5 else 0), "HA", 50 + 16 * (1 - ph), fill=WHITE, sw=6)
    counter(c); stove(c); pan(c, "burnt", t)
    with ghost():
        laugh = t > 3.0
        chef(c, CX, CY + (abs(math.sin(t * 12)) * 8 if laugh else 0), t, (CX - 150, CY + 320), (CX + 150, CY + 320), flour=True,
             eyes="happy" if laugh else "open", mouth="laugh" if laugh else "o", look=(-1, 0.5), tilt=math.sin(t * 6) * 0.06 if laugh else 0)
    caption(c)
    label(c, t, "she couldn't breathe")
    return c.out()

def k7(t, dur=9.0):
    z = punch(t, lerp(1.02, 1.12, ease(t / dur)))
    c = C(*WALL, cam=(560, 1260, z))
    window(c, False, t); ceiling(c); cabinets(c); smoke_alarm(c, t); ceil_pancake(c, t)
    floor(c, False)
    counter(c)
    # sitting in front of the counter
    for who in (0, 1):
        x = 400 if who == 0 else 700
        ch = (math.sin(t * 7 + who * 2) + 1) / 2
        hy = 1262
        sp = (x + (60 if who == 0 else -60), lerp(1480, 1370, ch))
        if who == 0:
            sitter(c, x, t, ROBE, legs_dir=-1, momstyle=True, eyes="happy" if t > 4 else "open", mouth="smile",
                   look=(1, 0.3), blush=t > 4, armL=(x - 20, 1500), armR=sp, blink=blinkf(t, 2.8))
            bowl(c, x - 10, 1505)
        else:
            with ghost():
                sitter(c, x, t, FLOUR, legs_dir=-1, eyes="happy" if t > 4 else "open", mouth="grin" if t > 4 else "smile",
                       look=(-1, 0.3), armL=sp, armR=(x + 20, 1500), blink=blinkf(t, 2.4, 0.7))
            bowl(c, x + 10, 1505)
        c.line([sp, (sp[0] + (30 if who == 0 else -30), sp[1] + 40)], w=8, fill=(180, 180, 190))
    if t > 4.0: hearts(c, t, 550, 1130, 3)
    caption(c)
    label(c, t, "cereal on the floor")
    if t > 4.2: sub(c, t, "best breakfast ever", 4.2)
    return c.out()

PLOP = 3.6
def k8(t, dur=5.5):
    z = punch(t, lerp(1.04, 1.14, ease(t / dur)))
    cam = (560, 1260, z)
    if PLOP < t < PLOP + 0.15: cam = (cam[0] + random.Random(int(t * 99)).uniform(-14, 14), cam[1], cam[2])
    c = C(*WALL, cam=cam)
    window(c, False, t); ceiling(c); cabinets(c); smoke_alarm(c, t)
    fallen = t > PLOP - 0.55
    if not fallen:
        wob = math.sin(t * 20) * 4 * seg(t, 2.2, PLOP - 0.55)
        c.ell(CEIL_PC[0] - 80 + wob, CEIL_PC[1] - 8, CEIL_PC[0] + 80 + wob, CEIL_PC[1] + 22, PANCAKE, w=6)
    floor(c, False); counter(c)
    x0, x1 = 400, 700
    hit = t > PLOP
    sitter(c, x0, t, ROBE, legs_dir=-1, momstyle=True, eyes="happy" if t > PLOP + 0.3 else ("wide" if t > PLOP - 0.5 else "happy"),
           mouth="laugh" if t > PLOP + 0.3 else "smile", blush=True, look=(1, -0.5),
           armL=(x0 - 20, 1500), armR=(x0 + 120, 1420 + (math.sin(t * 20) * 20 if t > PLOP + 0.3 else 0)), tilt=math.sin(t * 6) * 0.08 if hit else 0)
    bowl(c, x0 - 10, 1505)
    with ghost():
        sitter(c, x1, t, FLOUR, legs_dir=-1, eyes="closed" if hit else "happy", mouth="flat" if hit else "grin",
               look=(-1, 0.3), armL=(x1 - 60, 1480), armR=(x1 + 20, 1500))
    bowl(c, x1 + 10, 1505)
    if fallen:
        f = seg(t, PLOP - 0.55, PLOP)
        py = lerp(CEIL_PC[1] + 10, 1262 - 105, f * f)
        px = lerp(CEIL_PC[0], x1, f)
        if not hit:
            c.ell(px - 70, py - 16, px + 70, py + 16, PANCAKE, w=5)
        else:
            c.chord(x1 - 125, 1262 - 140, x1 + 125, 1262 + 60, 180, 360, PANCAKE, w=6)     # pancake hat
            for dx in (-90, 90): c.ell(x1 + dx - 14, 1262 - 50, x1 + dx + 14, 1262 + 10, PANCAKE, w=4)
    pop_text(c, t, 760, 960, "PLOP", PLOP, 110, GOLD, 0.8)
    caption(c)
    if t < PLOP: label(c, t, "still can't cook")
    else: label(c, t - PLOP, "part 2?")
    if t > PLOP + 0.5: sub(c, t, "follow for part 2", PLOP + 0.5)
    return c.out()

SCENES = [
    ("k1", 7.0, k1),
    ("k2", 9.0, k2),
    ("k3", 8.5, k3),
    ("k4", 12.0, k4),
    ("k5", 9.5, k5),
    ("k6", 6.5, k6),
    ("k7", 9.0, k7),
    ("k8", 5.5, k8),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"k1": [1.0, 4.2], "k2": [2.5, 4.0, 6.8], "k3": [3.2, 4.6, 6.2], "k4": [2.0, 5.5, 6.2, 8.0],
                 "k5": [2.5, 6.5], "k6": [1.0, 4.0], "k7": [5.0], "k8": [3.0, 4.6]}
        ims = [fn(tt).resize((270, 480)) for name, dur, fn in SCENES for tt in times[name]]
        cols = 6
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (270 * cols, 480 * rows), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
