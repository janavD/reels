"""Funny late-night reel: POV you hear a noise downstairs at 4am -> it was the cat."""
import sys, math, random, os
sys.path.insert(0, 'engine'); sys.path.insert(0, 'engine/library')
import rig
from rig import (C, INK, SKIN, WHITE, head, hand, label, sub, caption, punch, blinkf, back, ease, eout, seg, lerp,
                 mix, room, bed, blanket, nightstand, WALL_NIGHT)
from gaming_room import bubble
from night_noise import (cat, cat_curled, kitchen, cup, hallway, beam, person, phone_pos, bedside_clock, dk)
from PIL import Image

rig.CAP = ['POV: you hear a noise', 'downstairs at 4am']
YEL = (255, 220, 60)

def tag(c, x, y, s, t, start, sz=70, fill=YEL, end=None):
    if end is not None and t > end: return
    k = back(seg(t, start, start + 0.22))
    if k > 0.01: c.text(x, y, s, sz * k, fill=fill, sw=9)

def shaker(t, amt):
    r = random.Random(int(t * 30) + 3); return r.uniform(-amt, amt), r.uniform(-amt, amt)

def s_wake(t, dur=3.0):
    z = punch(t, lerp(1.08, 1.2, ease(t / dur)))
    sx, sy = shaker(t, 7 if 0.35 < t < 0.6 else 0)
    c = C(*WALL_NIGHT, cam=(400 + sx, 1180 + sy, z)); room(c, True, t, cal=None)
    nightstand(c, True); bedside_clock(c, "4:07")
    bed(c, True)
    up = t > 0.45
    head(c, 315, 1235, 105, tilt=-0.15 if not up else 0.05, eyes="closed" if not up else "wide",
         mouth="drool" if not up else "flat", brows=0.35 if up else None, look=(1, 0) if up else (0, 0), t=t)
    blanket(c, True, breathe=0 if up else math.sin(t * 2.2) * 8)
    if not up:
        for i in range(2):
            ph = (t * 0.8 + i / 2) % 1; c.text(430 + ph * 100, 1120 - ph * 180, "z", 44 + ph * 40, fill=WHITE, sw=6)
    tag(c, 520, 900, "*THUD*", t, 0.35, 80)
    bubble(c, 560, 1060, "...what was that", t, 1.3)
    caption(c); label(c, t, "4:07 AM"); sub(c, t, "something fell downstairs", 0.5)
    return c.out()

def s_hide(t, dur=3.0):
    z = punch(t, lerp(1.15, 1.3, ease(t / dur)))
    c = C(*WALL_NIGHT, cam=(380, 1220, z)); room(c, True, t, cal=None)
    nightstand(c, True); bedside_clock(c, "4:08")
    bed(c, True)
    jx = math.sin(t * 60) * 4
    look = (math.copysign(1, math.sin(t * 4)), 0)
    head(c, 315 + jx, 1235, 105, eyes="wide", mouth="o", brows=0.4, look=look, t=t, sweat=True)
    # blanket pulled up to the nose
    col = (58, 76, 132)
    c.poly([(150 + jx, 1250), (300, 1238), (470, 1250 + jx), (700, 1270), (990, 1282), (1010, 1460), (170, 1470)], col, w=7)
    for (hx, hy) in ((250, 1245), (370, 1245)): hand(c, hx + jx, hy, 22)
    tag(c, 470, 920, "*creeak*", t, 1.0, 66, end=1.8)
    bubble(c, 450, 1060, "what if it's a ghost", t, 1.8)
    caption(c); label(c, t, "4:08 AM"); sub(c, t, "nope. not my problem", 0.3)
    return c.out()

HX, HY = 300, 1030
def s_brave(t, dur=3.4):
    z = punch(t, lerp(1.0, 1.06, ease(t / dur)))
    x = lerp(200, 430, ease(t / dur))
    c = C((40, 40, 66), (30, 30, 50), cam=(560, 1170, z)); hallway(c, 0.45)
    px, py = phone_pos(x, HY)
    beam(c, px + 20, py - 40, 1100, 1300 + math.sin(t * 2) * 60, 170, wall=(50, 50, 76))
    person(c, t, x, HY, eyes="open", mouth="grit", brows=0.45, look=(1, 0), walk=0.7, pillow_up=1.0, flash=True,
           blink=blinkf(t, 2.0, 0.4))
    bubble(c, x + 60, 690, "who's there?? i have a pillow", t, 1.4)
    caption(c); label(c, t, "4:09 AM"); sub(c, t, "armed and dangerous", 0.4)
    return c.out()

def s_eyes(t, dur=2.8):
    z = punch(t, lerp(1.04, 1.12, ease(t / dur)))
    scream = t > 1.2
    sx, sy = shaker(t, 12 if scream else 0)
    c = C((22, 22, 34), (16, 16, 26), cam=(560 + sx, 1170 + sy, z)); kitchen(c, 0.78)
    px, py = phone_pos(260, HY)
    if t > 0.25:
        beam(c, px + 20, py - 40, 860, 1120, 120, wall=(30, 30, 44), k=0.3)
    cat(c, 860, 1230, t, d=0.85, glow_eyes=(int(t * 10) % 14 != 0) and t > 0.6, tail=False)
    person(c, t, 260, HY, eyes="wide" if t > 0.6 else "open", mouth="scream" if scream else "o",
           brows=0.5 if t > 0.6 else 0.3, look=(1, 0), pillow_up=1.0 if not scream else 0.0, flash=True,
           shake=10 if scream else 0, sweat=scream, arms_out=ease(seg(t, 1.2, 1.4)) if scream else 0)
    tag(c, 300, 780, "AAAAAA", t, 1.2, 100, fill=WHITE)
    caption(c); label(c, t, "4:10 AM"); sub(c, t, "two eyes. in the dark.", 0.5)
    return c.out()

def s_cat(t, dur=3.8):
    z = punch(t, lerp(1.05, 1.15, ease(t / dur)))
    c = C((60, 60, 80), (40, 40, 56), cam=(620, 1170, z)); kitchen(c, 0.15)
    c.glow(700, 700, 500, (255, 230, 170), 0.2)  # light switched on
    # paw swipes the mug off at 1.3
    paw = ease(seg(t, 1.0, 1.35)) * (1 - ease(seg(t, 1.5, 1.9)))
    fall = seg(t, 1.3, 1.75)
    if t < 1.3: cup(c, 700, 1232)
    elif fall < 1:
        cup(c, 700 - fall * 120, 1232 + fall ** 2 * 400, a=-fall * 2.2)
    else:
        for i, (dx, a) in enumerate(((-60, 0.6), (-10, -1.2), (40, 2.0))):  # shards
            c.poly([(560 + dx, 1636), (590 + dx, 1600 + i * 6), (610 + dx, 1636)], (240, 110, 110), w=5)
    cat(c, 860, 1230, t, eyes="open" if t < 2.2 else "half", paw=paw)
    tag(c, 470, 1440, "clink", t, 1.75, 60, fill=WHITE)
    person(c, t, 300, HY, eyes="half", mouth="flat", brows=-0.2, look=(1, 0), pillow_up=0.0, flash=None,
           blink=blinkf(t, 2.4, 1.0))
    bubble(c, 880, 900, "mrrp.", t, 2.2)
    caption(c); label(c, t, "it was the cat"); sub(c, t, "...and she did it again", 1.8)
    return c.out()

def s_bed(t, dur=3.4):
    z = punch(t, lerp(1.1, 1.22, ease(t / dur)))
    c = C(*WALL_NIGHT, cam=(420, 1200, z)); room(c, True, t, cal=None)
    nightstand(c, True); bedside_clock(c, "4:12")
    bed(c, True)
    head(c, 315, 1235, 105, eyes="wide", mouth="flat", look=(0, -1), t=t, blink=blinkf(t, 3.5, 2.0))
    blanket(c, True)
    cat_curled(c, 680, 1290, t)
    for i in range(2):
        ph = (t * 0.7 + i / 2) % 1
        c.text(720 + ph * 50, 1215 - ph * 90, "prrr", 40 + ph * 16, fill=WHITE, sw=6)
    bubble(c, 450, 1000, "great. i'm awake forever", t, 0.9)
    caption(c); label(c, t, "4:12 AM"); sub(c, t, "follow for part 2", 1.6)
    return c.out()

SCENES = [
    ("n1", 3.0, s_wake),
    ("n2", 3.0, s_hide),
    ("n3", 3.4, s_brave),
    ("n4", 2.8, s_eyes),
    ("n5", 3.8, s_cat),
    ("n6", 3.4, s_bed),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"n1": 1.8, "n2": 2.4, "n3": 2.2, "n4": 1.6, "n5": [1.5, 2.8], "n6": 2.4}
        ims = []
        for name, dur, fn in SCENES:
            tt = times[name]
            for x in (tt if isinstance(tt, list) else [tt]): ims.append(fn(x).resize((300, 533)))
        sheet = Image.new("RGB", (300 * 4, 533 * 2), WHITE)
        for i, im in enumerate(ims[:8]): sheet.paste(im, ((i % 4) * 300, (i // 4) * 533))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
