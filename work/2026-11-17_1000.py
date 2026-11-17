"""Funny store reel: self checkout -> scans a banana (easy) -> 'unexpected item in bagging area' -> lift it:
'please place item in bagging area' -> put back: unexpected item again -> frozen mid-air -> the line behind me ->
employee taps once without looking, 'there you go.' -> 9 minutes for one banana."""
import sys, math, random, os
sys.path.insert(0, 'engine'); sys.path.insert(0, 'engine/library')
import rig
from rig import (C, INK, WHITE, hand, label, sub, caption, punch, blinkf, back, ease, eout, seg, lerp, mix)
from gaming_room import bubble
from quiet_morning import burst, YEL
from self_checkout import (STORE, RED, GRN, BLUE, store, bag_stand, plastic_bag, kiosk, banana, shopper,
                           employee, line_person, cart)
from PIL import Image

rig.CAP = ['me at self checkout:', '"unexpected item in', 'the bagging area"']
X, Y = 500, 960
BAGX, BAGY = 215, 1110
UNEXP = ["UNEXPECTED ITEM", "IN BAGGING", "AREA"]
PLEASE = ["PLEASE PLACE ITEM", "IN BAGGING AREA"]
AMBER = (235, 160, 40)

def shk(t, amt):
    r = random.Random(int(t * 30) + 5); return r.uniform(-amt, amt), r.uniform(-amt, amt)

def base(t, z, cx=540, cy=1160, sh=0.0):
    sx, sy = shk(t, sh)
    c = C(*STORE, cam=(cx + sx, cy + sy, z)); store(c, t); bag_stand(c)
    return c

def s_scan(t, dur=3.0):
    c = base(t, punch(t, lerp(1.0, 1.08, ease(t / dur))))
    plastic_bag(c, BAGX, BAGY)
    beep = t > 1.2
    kiosk(c, t, ["BANANA", "$0.29"] if beep else ["SCAN YOUR", "FIRST ITEM"], col=BLUE, scan=0.9 < t < 1.5)
    k = ease(seg(t, 0.0, 0.9)); sw = ease(seg(t, 0.9, 1.5))
    ra = (lerp(640, 700, k) + sw * 110, lerp(1320, 1030, k) - math.sin(sw * math.pi) * 10)
    if t > 1.7: ra = (lerp(810, 610, ease(seg(t, 1.7, 2.3))), lerp(1030, 1320, ease(seg(t, 1.7, 2.3))))
    la = (X - 120, 1320)
    shopper(c, t, X, Y, la, ra, eyes="happy" if beep and t < 1.9 else "open", mouth="grin" if beep else "smile",
            look=(1, 0.3), blink=blinkf(t, 2.6, 0.5))
    banana(c, ra[0] + 10, ra[1] - 20, a=0.3)
    hand(c, *la, 21); hand(c, *ra, 21)
    burst(c, 850, 990, "*BEEP*", t, 1.2, 80, fill=WHITE)
    bubble(c, 300, 690, "easy.", t, 1.8)
    caption(c); label(c, t, "10:02 AM"); sub(c, t, "self checkout. so easy.", 0.3)
    return c.out()

def s_bag(t, dur=3.2):
    hit = 1.0
    c = base(t, punch(t, lerp(1.02, 1.12, ease(t / dur))), sh=8 if hit < t < hit + 0.5 else 0)
    k = ease(seg(t, 0.0, 0.8))
    la = (lerp(X - 140, BAGX + 20, k), lerp(1230, 1000, k))
    plastic_bag(c, BAGX, BAGY)
    if t > 0.8: banana(c, BAGX + 10, 975, a=-0.2)
    bad = t > hit
    kiosk(c, t, UNEXP if bad else ["BANANA", "$0.29"], col=RED if bad else BLUE, shake=5 if hit < t < hit + 0.6 else 0)
    ra = (610, 1320)
    shopper(c, t, X, Y, la, ra, eyes="wide" if t > 1.2 else "open", mouth="o" if t > 1.2 else "smile",
            brows=0.35 if t > 1.2 else None, look=(1, -0.3) if t > 1.2 else (-1, 0.3), blink=blinkf(t, 2.6, 0.2) if t < 1.2 else 0)
    if t <= 0.8: banana(c, la[0] + 10, la[1] - 20, a=-0.3)
    hand(c, *la, 21); hand(c, *ra, 21)
    bubble(c, 330, 690, "it's a banana.", t, 1.8)
    caption(c); label(c, t, "10:03 AM"); sub(c, t, "into the bag it goes", 0.2) if t < 1.0 else \
        sub(c, t, "*angry robot noises*", 1.0)
    return c.out()

def s_flip(t, dur=3.2):
    back_in = 1.5
    rage = t > 2.0
    c = base(t, punch(t, lerp(1.05, 1.2, ease(t / dur))), sh=10 if rage else (6 if back_in < t < back_in + 0.4 else 0))
    plastic_bag(c, BAGX, BAGY)
    up = ease(seg(t, 0.0, 0.5)) * (1 - ease(seg(t, 1.1, back_in)))
    la = (BAGX + 20, lerp(1000, 860, up))
    if t < 0.5: msg, col = UNEXP, RED
    elif t < back_in: msg, col = PLEASE, AMBER
    else: msg, col = UNEXP, RED
    kiosk(c, t, msg, col=col, shake=5 if (0.5 < t < 0.9 or back_in < t < back_in + 0.5) else 0)
    ra = (610, 1320) if not rage else (X + 120, 830 + math.sin(t * 30) * 8)
    shopper(c, t, X, Y, la, ra, eyes="wide", mouth="flat" if t < back_in else ("scream" if rage else "o"),
            brows=0.4 if rage else 0.2, look=(1, -0.3), sweat=t > 1.0, shake=5 if rage else 0)
    banana(c, la[0] + 10, la[1] - 25, a=-0.2)
    hand(c, *la, 21); hand(c, *ra, 21)
    burst(c, 540, 1440, "MAKE UP YOUR MIND", t, 2.0, 76)
    caption(c); label(c, t, "10:05 AM")
    sub(c, t, "ok it's out... ok it's back", 0.4) if t < 2.0 else None
    return c.out()

def s_freeze(t, dur=2.0):
    z = lerp(1.1, 1.26, ease(t / dur))
    c = base(t, z, cx=520, cy=1020)
    plastic_bag(c, BAGX, BAGY)
    kiosk(c, t, UNEXP, col=RED, flash=True)
    la = (BAGX + 40, 935)
    shopper(c, t, X, Y, la, (610, 1320), eyes="wide", mouth="grit", brows=0.3, look=(1, -0.4), sweat=True, frozen=True)
    banana(c, la[0] + 10, la[1] - 25, a=-0.2)
    hand(c, *la, 21); hand(c, 610, 1320, 21)
    caption(c); label(c, t, "10:09 AM"); sub(c, t, "if i don't move it can't see me", 0.3)
    return c.out()

def s_line(t, dur=1.8):
    c = C(*STORE, cam=(540, 1160, punch(t, lerp(1.0, 1.06, ease(t / dur)))))
    store(c, t)
    line_person(c, t, 900, 930, (230, 120, 90), (40, 30, 30), arms="crossed", tap=2.4, look=(-1, 0))
    line_person(c, t, 560, 950, (150, 120, 200), (200, 150, 60), arms="watch", eyes="half", look=(1, 0.6), brows=-0.35)
    line_person(c, t, 190, 960, (100, 180, 160), (90, 60, 40), arms="crossed", mouth="frown", look=(-1, 0), tap=3.0)
    cart(c, 960, 1480, 0.9)
    bubble(c, 560, 690, "bro...", t, 0.6)
    caption(c); label(c, t, "the line behind me:", sz=74)
    return c.out()

def s_end(t, dur=4.2):
    tap_t = 1.0
    c = base(t, punch(t, lerp(0.9, 0.97, ease(t / dur))), cx=600, cy=1160)
    plastic_bag(c, BAGX, BAGY)
    ok = t > tap_t + 0.1
    kiosk(c, t, ["THANK YOU!", "have a nice day"] if ok else UNEXP, col=GRN if ok else RED, flash=not ok)
    la = (BAGX + 40, 935) if t < 1.9 else (lerp(BAGX + 40, BAGX + 30, ease(seg(t, 1.9, 2.3))), lerp(935, 1000, ease(seg(t, 1.9, 2.3))))
    shopper(c, t, X, Y, la, (610, 1320), eyes="half" if ok else "wide", mouth="flat", brows=-0.2 if ok else 0.3,
            look=(1, -0.3), blink=blinkf(t, 2.2, 0.4) if t > 2.0 else 0, sweat=not ok)
    banana(c, la[0] + 10, la[1] - 25, a=-0.2)
    hand(c, *la, 21); hand(c, 610, 1320, 21)
    ex = lerp(1350, 1060, eout(seg(t, 0.0, 0.8)))
    tk = ease(seg(t, 0.75, tap_t)) * (1 - ease(seg(t, tap_t + 0.3, tap_t + 0.7)))
    tap = (lerp(ex - 100, 880, tk), lerp(1180, 770, tk))
    employee(c, t, ex, 800, tap=tap, walk=1.8 if t < 0.8 else 0, look=(1, 0.3))
    burst(c, 860, 1000, "*tap*", t, tap_t, 70, fill=WHITE)
    bubble(c, 760, 515, "there you go.", t, 1.3)
    bubble(c, 330, 690, "...", t, 2.3)
    caption(c); label(c, t, "10:11 AM"); sub(c, t, "9 minutes. for one banana.", 2.6)
    return c.out()

SCENES = [
    ("k1", 3.0, s_scan),
    ("k2", 3.2, s_bag),
    ("k3", 3.2, s_flip),
    ("k4", 2.0, s_freeze),
    ("k5", 1.8, s_line),
    ("k6", 4.2, s_end),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"k1": 1.3, "k2": 1.9, "k3": [0.9, 2.4], "k4": 1.0, "k5": 1.2, "k6": [1.05, 3.2]}
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
