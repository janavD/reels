"""4:30pm funny reel: texting 'omw' vs the actual timeline."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, SKIN, WHITE, WALL_NIGHT, head, limb, ik, hand, room, bed, lying, lamp, label, sub,
                 caption, punch, blinkf, back, ease, eout, seg, lerp, mix, rot, star, font)
from PIL import Image

rig.CAP = ['me: "on my way!"', "the actual timeline:"]

BLUE = (60, 140, 255)
GRAY = (232, 232, 238)

# ---------- chat overlay ----------
def chat(c, t, msgs, y0=470):
    """msgs: list of (side 'L'/'R', text, start). Stacks downward."""
    y = y0
    with c.ui():
        for side, s, st in msgs:
            k = back(seg(t, st, st + 0.28))
            if k <= 0.01: continue
            sz = 52
            tw = font(sz).getlength(s) / rig.S
            w = (tw + 70) * k; h = 100 * k
            cx = 300 + (tw + 70) / 2 - 40 if side == "L" else 780 - (tw + 70) / 2 + 40
            cx = max(w / 2 + 40, min(1040 - w / 2, cx))
            col = GRAY if side == "L" else BLUE
            c.rect(cx - w / 2, y - h / 2, cx + w / 2, y + h / 2, col, w=5, r=40 * k)
            c.text(cx, y, s, sz * k, fill=INK if side == "L" else WHITE, stroke=None)
            if side == "L":
                c.circ(cx - w / 2 - 48 * k, y, 34 * k, (255, 190, 120), w=5)
                c.text(cx - w / 2 - 48 * k, y + 2, "B", 34 * k, fill=INK, stroke=None)
            y += 125

def buzz(c, x, y, t, st, dur=0.6):
    if st < t < st + dur:
        for i in range(2):
            r0 = 40 + i * 22 + ((t - st) * 160) % 22
            c.arc(x - r0, y - r0, x + r0, y + r0, 200, 250, w=5, fill=(255, 230, 120))
            c.arc(x - r0, y - r0, x + r0, y + r0, 290, 340, w=5, fill=(255, 230, 120))

def phone(c, x, y, s=1.0, ang=0.0):
    pts = [(x + rot(dx * s, dy * s, ang)[0], y + rot(dx * s, dy * s, ang)[1]) for dx, dy in ((-32, -58), (32, -58), (32, 58), (-32, 58))]
    c.poly(pts, (34, 34, 40), w=5)
    pts2 = [(x + rot(dx * s, dy * s, ang)[0], y + rot(dx * s, dy * s, ang)[1]) for dx, dy in ((-24, -48), (24, -48), (24, 48), (-24, 48))]
    c.poly(pts2, (150, 205, 255), ol=None)

def door(c):
    wood = (130, 86, 58)
    c.rect(790, 880, 1060, 1640, mix(wood, (0, 0, 0), 0.3), w=8)
    c.rect(810, 900, 1040, 1640, wood, w=6)
    c.rect(840, 940, 1010, 1180, mix(wood, (0, 0, 0), 0.15), w=5, r=6)
    c.rect(840, 1240, 1010, 1560, mix(wood, (0, 0, 0), 0.15), w=5, r=6)
    c.circ(830, 1270, 14, (240, 200, 80), w=5)
    c.rect(870, 840, 980, 875, (240, 240, 230), w=4, r=6)
    c.text(925, 858, "EXIT", 22, fill=(60, 170, 90), stroke=None)

def wardrobe(c):
    wood = (150, 100, 66)
    c.rect(-40, 820, 300, 1640, wood, w=8)
    c.line([(130, 830), (130, 1630)], w=6)
    c.circ(110, 1220, 9, INK, ol=None); c.circ(150, 1220, 9, INK, ol=None)
    # open drawer with stuff spilling
    c.rect(-20, 1500, 280, 1600, mix(wood, (0, 0, 0), 0.15), w=6)

def keys(c, x, y, t, scale=1.0):
    sw = math.sin(t * 14) * 0.4
    c.arc(x - 20 * scale, y - 20 * scale, x + 20 * scale, y + 20 * scale, 0, 360, w=10, fill=INK)
    c.arc(x - 18 * scale, y - 18 * scale, x + 18 * scale, y + 18 * scale, 0, 360, w=5, fill=(190, 190, 200))
    for i, off in enumerate((-0.4, 0.35)):
        a = math.pi / 2 + off + sw
        bx, by = x + math.cos(a) * 18 * scale, y + math.sin(a) * 18 * scale
        ex, ey = bx + math.cos(a) * 60 * scale, by + math.sin(a) * 60 * scale
        col = (245, 200, 70) if i == 0 else (200, 205, 215)
        c.line([(bx, by), (ex, ey)], w=12 * scale, fill=INK)
        c.line([(bx, by), (ex, ey)], w=7 * scale, fill=col)
        c.circ(bx + math.cos(a) * 8, by + math.sin(a) * 8, 13 * scale, col, w=4)

def stand(c, x, y, t, shirt=None, **hk):
    """Standing body without arms; returns shoulder point. y = head center."""
    hip = (x, y + 360)
    c.ell(x - 140, 1625, x + 140, 1655, (60, 48, 50), ol=None)
    limb(c, hip, (x - 60, 1630), 118, 118, bend=-1); limb(c, hip, (x + 60, 1630), 118, 118, bend=1)
    c.line([(x - 60, 1630), (x - 100, 1632)], w=14); c.line([(x + 60, 1630), (x + 100, 1632)], w=14)
    c.line([(x, y + 105), hip], w=14)
    if shirt:
        c.poly([(x - 55, y + 135), (x + 55, y + 135), (x + 70, y + 210), (x + 42, y + 215), (x + 40, y + 340),
                (x - 40, y + 340), (x - 42, y + 215), (x - 70, y + 210)], shirt, w=6)
    return (x, y + 170)

# ---------- scenes ----------
def s_omw(t):
    z = punch(t, lerp(1.05, 1.14, ease(t / 3.2)))
    c = C(*WALL_NIGHT, cam=(470, 1180, z)); room(c, True, t, None)
    lamp(c, 1000, 1640, True)
    typing = 1.2 < t < 1.9
    lying(c, t, True, (430, 1060), eyes="open" if t < 0.6 else ("half" if not typing else "open"),
          mouth="smile" if t > 1.9 else "flat", look=(0, -1), blink=blinkf(t, 2.4, 0.3),
          phone_glow=True, thumb_scroll=typing or t < 0.6)
    buzz(c, 430, 1060, t, 0.45)
    chat(c, t, [("L", "where r u??", 0.45), ("R", "omw!!", 1.85)])
    caption(c); label(c, t, "6:58 PM", 1650); sub(c, t, "*still in bed*", 2.1)
    return c.out()

def s_scroll(t):
    z = punch(t, lerp(1.08, 1.2, ease(t / 2.8)))
    c = C(*WALL_NIGHT, cam=(440, 1190, z)); room(c, True, t, None)
    sway = math.sin(t * 3) * 10
    lying(c, t, True, (430 + sway, 1060), eyes="happy", mouth="laugh", kick=abs(math.sin(t * 14)) * 30,
          tilt=math.sin(t * 20) * 0.08, blush=True, phone_glow=True)
    for i in range(3):
        ph = (t * 1.3 + i / 3) % 1
        if t > 0.3: c.text(170 - i * 20 + ph * 40, 1100 - ph * 200, "lol", 46 + 10 * (1 - ph), fill=WHITE, sw=6)
    chat(c, t, [("L", "u close?", 1.3), ("R", "5 min!", 1.9)])
    caption(c); label(c, t, "7:15 PM", 1650); sub(c, t, "one more reel", 0.4)
    return c.out()

SHIRTS = [(230, 80, 80), (80, 170, 110), (240, 190, 60), (150, 100, 210), (70, 140, 230), (245, 245, 245), (40, 40, 48)]
FLY = [(random.Random(i).uniform(-1, 1), random.Random(i + 5).uniform(0.7, 1.2)) for i in range(8)]

def s_outfit(t, dur=3.2):
    z = punch(t, lerp(1.0, 1.1, ease(t / dur)))
    c = C(*WALL_NIGHT, cam=(540, 1170, z)); room(c, True, t, None)
    wardrobe(c)
    # clothes pile growing on floor
    pile = int(seg(t, 0.3, dur) * 7) + 2
    for i in range(pile):
        col = SHIRTS[i % 7]
        px = 760 + (i % 3) * 70 - 70; py = 1625 - (i // 3) * 28
        c.ell(px - 80, py - 24, px + 80, py + 18, col, w=5)
    x, y = 560, 1060 + math.sin(t * 6) * 5
    idx = int(t / 0.38) % 7
    swap = (t % 0.38) / 0.38
    sh = stand(c, x, y, t, shirt=SHIRTS[idx])
    # arms: pulling shirt over head on each swap
    up = 1 - abs(swap * 2 - 1) if swap < 0.5 else 0
    for side in (-1, 1):
        tx = x + side * lerp(130, 70, up); ty = lerp(y + 320, y - 120, up)
        limb(c, (x + side * 10, y + 165), (tx, ty), 115, 115, bend=side); hand(c, tx, ty, 21)
    # thrown shirt arcing away
    for i, (vx, sp) in enumerate(FLY):
        ph = (t * sp * 1.4 + i * 0.13) % 1
        if t < 0.3: break
        px = x + 260 * ph * (1 if vx > 0 else -0.6) + 100; py = y - 100 - 500 * ph + 700 * ph * ph
        a = ph * 8
        pts = [(px + rot(dx, dy, a)[0], py + rot(dx, dy, a)[1]) for dx, dy in ((-50, -30), (50, -30), (40, 35), (-40, 35))]
        c.poly(pts, SHIRTS[i % 7], w=4)
    head(c, x, y, 110, tilt=math.sin(t * 4) * 0.12, eyes="open", mouth="frown" if idx % 2 else "flat",
         look=(0, 0.6), blink=blinkf(t, 2.0), brows=0.3, t=t)
    for i, s in enumerate(("nah", "ew", "no")):
        k = back(seg(t, 0.5 + i * 0.85, 0.75 + i * 0.85)) * (1 - seg(t, 1.1 + i * 0.85, 1.25 + i * 0.85))
        if k > 0.01: c.text(x + 240, y - 120, s, 64 * k, fill=(255, 220, 60), sw=8)
    caption(c); label(c, t, "7:30 PM", 1650); sub(c, t, "nothing fits??", 0.5)
    return c.out()

def s_keys(t, dur=3.2):
    rnd = random.Random(int(t * 30))
    sh_amt = 3 + 6 * (t / dur)
    z = lerp(1.0, 1.12, ease(t / dur))
    c = C(*WALL_NIGHT, cam=(540 + rnd.uniform(-sh_amt, sh_amt), 1170 + rnd.uniform(-sh_amt, sh_amt), z))
    room(c, True, t, None); door(c)
    # couch
    c.rect(60, 1380, 620, 1600, (190, 90, 80), w=7, r=30); c.rect(40, 1300, 140, 1600, (170, 78, 70), w=7, r=30)
    c.rect(540, 1300, 640, 1600, (170, 78, 70), w=7, r=30)
    c.line([(340, 1390), (340, 1520)], w=5)
    x = 400 + math.sin(t * 5) * 120; y = 1040 + abs(math.sin(t * 12)) * 8
    stand(c, x, y, t)
    look = (1, 0.2) if math.sin(t * 5) > 0 else (-1, 0.2)
    # one arm digs couch, other holds phone texting
    dig = abs(math.sin(t * 18))
    tx, ty = x - 120, 1390 + dig * 40
    limb(c, (x - 10, y + 170), (tx, ty), 120, 120, bend=-1); hand(c, tx, ty, 22)
    px, py = x + 120, y + 200
    limb(c, (x + 10, y + 170), (px, py + 30), 115, 115, bend=1); phone(c, px, py, 0.9, 0.2); hand(c, px, py + 30, 20)
    head(c, x, y, 115, tilt=math.sin(t * 9) * 0.08, eyes="wide", mouth="grit" if (t % 0.8) < 0.5 else "scream",
         look=look, brows=0.45, t=t, sweat=True)
    # cushions/socks flying out
    for i in range(5):
        ph = (t * 1.1 + i * 0.2) % 1
        if t < 0.25: break
        cx0 = 300 + (i - 2) * 50 + ph * (i - 2) * 160; cy0 = 1380 - 520 * ph + 650 * ph * ph
        a = ph * 7 * (1 if i % 2 else -1)
        col = [(240, 200, 90), (120, 170, 220), WHITE, (230, 120, 150), (150, 210, 140)][i]
        pts = [(cx0 + rot(dx, dy, a)[0], cy0 + rot(dx, dy, a)[1]) for dx, dy in ((-45, -35), (45, -35), (45, 35), (-45, 35))]
        c.poly(pts, col, w=5)
    chat(c, t, [("L", "we ordered already", 0.4), ("R", "2 min away!!", 1.3)])
    caption(c); label(c, t, "7:52 PM", 1650); sub(c, t, "where are my keys", 0.5)
    return c.out()

def s_punch(t, dur=4.4):
    found = 0.0
    msg = 1.6
    zk = ease(seg(t, msg + 0.3, msg + 1.1))
    cam = (lerp(540, 520, zk), lerp(1170, 1050, zk), lerp(1.0, 1.45, zk))
    c = C(*WALL_NIGHT, cam=cam); room(c, True, t, None); door(c)
    x, y = 520, 1050
    stand(c, x, y, t, shirt=SHIRTS[3])
    # left arm raises keys triumphantly
    up = back(seg(t, 0.05, 0.4)) * (1 - ease(seg(t, msg + 0.1, msg + 0.5)))
    kx, ky = lerp(x - 150, x - 190, up), lerp(y + 320, y - 140, up)
    limb(c, (x - 10, y + 170), (kx, ky), 120, 120, bend=-1)
    keys(c, kx, ky + 22, t * (1 if t < msg else 0.2)); hand(c, kx, ky, 22)
    # right arm holds phone up to face after buzz
    lift = ease(seg(t, msg + 0.05, msg + 0.35))
    px, py = lerp(x + 140, x + 170, lift), lerp(y + 300, y + 60, lift)
    limb(c, (x + 10, y + 170), (px, py + 30), 115, 115, bend=1); phone(c, px, py, 1.0, -0.15 * lift); hand(c, px, py + 30, 20)
    buzz(c, px, py, t, msg - 0.1, 0.5)
    if t < msg:
        head(c, x, y, 110, tilt=0.1 * up, eyes="happy", mouth="grin", t=t, brows=-0.25)
        if up > 0.6:
            for i in range(4):
                a = i * math.pi / 2 + t * 4
                star(c, kx + math.cos(a) * 80, ky + math.sin(a) * 60, 16)
    else:
        tw = math.sin(t * 40) * 0.12 if (t - msg) > 1.4 and (t * 3) % 1 < 0.35 else 0
        eyes = "open" if t < msg + 0.5 else "half"
        head(c, x, y, 110, tilt=0, eyes=eyes, mouth="o" if t < msg + 0.5 else "flat", look=(1, 0.3) if t < msg + 0.5 else (0, 0),
             t=t, brows=(-0.35 + tw) if t > msg + 0.5 else None)
    chat(c, t, [("L", "omg sorry", msg), ("L", "i just woke up lol", msg + 0.35)])
    caption(c)
    if t < msg: label(c, t, "8:10 PM", 1650); sub(c, t, "FINALLY.", 0.35)
    else: label(c, t - msg - 2.0, "every. single. time.", 1650, sz=72)
    return c.out()

SCENES = [
    ("a1", 3.2, s_omw),
    ("a2", 2.8, s_scroll),
    ("a3", 3.2, s_outfit),
    ("a4", 3.2, s_keys),
    ("a5", 4.6, s_punch),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"a1": [0.8, 2.6], "a2": [2.4], "a3": [0.6, 2.0], "a4": [1.0, 2.6], "a5": [0.8, 2.0, 2.9, 4.3]}
        ims = [fn(tt).resize((270, 480)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (270 * 6, 480 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 6) * 270, (i // 6) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
