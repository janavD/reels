"""Funny morning reel: trying to be quiet at 6am so i don't wake my roommate -> every sound is 400% louder ->
roommate was awake the whole time."""
import sys, math, random, os
sys.path.insert(0, 'engine'); sys.path.insert(0, 'engine/library')
import rig
from rig import (C, INK, WHITE, hand, label, sub, caption, punch, blinkf, back, ease, eout, seg, lerp, mix, floor)
from gaming_room import bubble
from night_noise import kitchen, hallway, dk
from quiet_morning import quiet_guy, burst, spoon, bowl, cereal_box, microwave, roommate, YEL
from PIL import Image

rig.CAP = ['me trying to be quiet', "at 6am so i don't", 'wake my roommate']

def shk(t, amt):
    r = random.Random(int(t * 30) + 3); return r.uniform(-amt, amt), r.uniform(-amt, amt)

def zzz_sign(c, d):
    c.rect(850, 960, 970, 1030, dk((250, 245, 230), d), w=5, r=8)
    c.text(910, 995, "zzz", 34, fill=INK, stroke=None)

def s_creak(t, dur=3.0):
    sh = 8 if 1.5 < t < 2.0 else 0; sx, sy = shk(t, sh)
    z = punch(t, lerp(1.05, 1.16, ease(t / dur)))
    c = C((96, 98, 136), (70, 72, 104), cam=(520 + sx, 1180 + sy, z)); hallway(c, 0.3); zzz_sign(c, 0.3)
    stop = t > 1.5
    x = lerp(220, 440, ease(seg(t, 0, 1.5)))
    la = (x - 150, 1260 + math.sin(t * 9) * 10)          # arms out for balance
    ra = (x + 40, 1050)                                   # finger to lips
    quiet_guy(c, t, x, 960, la, ra, eyes="wide" if stop else "open", mouth="o" if stop else "flat",
              brows=0.35 if stop else None, look=(1, 0) if not stop else (0, 1), walk=0 if stop else 1.6,
              sweat=stop, freeze=stop)
    c.line([(x + 40, 1050), (x + 40, 985)], w=12); hand(c, *ra, 20)
    burst(c, x + 30, 1480, "CREEEAK", t, 1.5, 100)
    caption(c); label(c, t, "6:00 AM"); sub(c, t, "roommate is still asleep", 0.4)
    return c.out()

def s_spoon(t, dur=3.0):
    sh = 10 if 0.9 < t < 1.5 else 0; sx, sy = shk(t, sh)
    z = punch(t, lerp(1.0, 1.08, ease(t / dur)))
    c = C((150, 160, 182), (120, 128, 150), cam=(540 + sx, 1180 + sy, z)); kitchen(c, 0.25)
    c.glow(880, 700, 420, (255, 210, 150), 0.15)
    x = 330
    panic = t > 1.0
    # spoon falls from right hand 0.5..0.9, bounces until 1.6
    hx, hy = x + 170, 1230
    if t < 0.5: spoon(c, hx, hy, -0.6)
    elif t < 0.9:
        k = seg(t, 0.5, 0.9); spoon(c, hx + 20 * k, lerp(hy, 1600, k * k), -0.6 + k * 4)
    else:
        b = abs(math.sin((t - 0.9) * 14)) * 60 * max(0, 1 - (t - 0.9) / 0.8)
        spoon(c, hx + 40, 1600 - b, 3.4 + math.sin(t * 20) * 0.3 * max(0, 1 - (t - 0.9)))
    if panic:
        la, ra = (x - 115, 885), (x + 115, 885)            # hands on head
    else:
        la, ra = (x - 120, 1300), (hx - 10, hy + 10)
    quiet_guy(c, t, x, 960, la, ra, eyes="wide" if t > 0.55 else "open", mouth="scream" if panic else ("o" if t > 0.55 else "flat"),
              brows=0.4 if t > 0.55 else None, look=(1, 1) if t < 1.0 else (0, 0), sweat=panic, shake=4 if panic else 0)
    hand(c, *la, 21); hand(c, *ra, 21)
    burst(c, 760, 1470, "CLANG!!!", t, 0.9, 120)
    caption(c); label(c, t, "6:03 AM"); sub(c, t, "every sound is 400% louder", 1.4)
    return c.out()

def s_cereal(t, dur=3.0):
    pour = t > 0.6
    sh = 9 if pour else 0; sx, sy = shk(t, sh)
    z = punch(t, lerp(1.05, 1.14, ease(t / dur)))
    c = C((150, 160, 182), (120, 128, 150), cam=(600 + sx, 1180 + sy, z)); kitchen(c, 0.2)
    bx, by = 820, 1228
    bowl(c, bx, by, fill=ease(seg(t, 0.7, 2.6)))
    a = lerp(0, 2.0, ease(seg(t, 0.2, 0.6)))
    cx, cy = bx - 60, 1000
    if pour:
        for i in range(9):
            ph = (t * 3 + i / 9) % 1
            rr = random.Random(i)
            c.circ(cx + 70 + rr.uniform(-20, 20), lerp(cy + 40, by - 20, ph), 12, (235, 170, 70), w=4)
    cereal_box(c, cx, cy, a)
    x = 380
    quiet_guy(c, t, x, 960, (cx - 30, cy + 60), (cx + 30, cy - 40), eyes="wide" if pour else "open",
              mouth="grit" if pour else "flat", brows=0.35 if pour else None, look=(1, 0), sweat=pour)
    hand(c, cx - 30, cy + 60, 21); hand(c, cx + 30, cy - 40, 21)
    burst(c, 560, 1480, "*AVALANCHE*", t, 0.7, 96)
    bubble(c, 400, 720, "why is cereal SO LOUD", t, 1.5)
    caption(c); label(c, t, "6:05 AM"); sub(c, t, "it sounds like rocks", 2.0)
    return c.out()

def s_micro(t, dur=3.0):
    sh = 7 if 0.3 < t < 1.3 else 0; sx, sy = shk(t, sh)
    z = punch(t, lerp(1.0, 1.1, ease(t / dur)))
    c = C((150, 160, 182), (120, 128, 150), cam=(600 + sx, 1180 + sy, z)); kitchen(c, 0.2)
    mx, my = 860, 1230
    beep = t < 1.25
    microwave(c, mx, my, t, beep)
    dive = ease(seg(t, 0.6, 1.1))
    x = lerp(330, 470, dive)
    ra = (lerp(x + 120, mx + 30, dive), lerp(1250, my - 120, dive))
    quiet_guy(c, t, x, lerp(960, 990, dive), (x - 140, lerp(1250, 1000, dive)), ra,
              eyes="wide" if t < 1.6 else "closed", mouth="scream" if t < 1.25 else "grit",
              brows=0.4, tilt=0.12 * dive, look=(1, 0), sweat=True)
    hand(c, *ra, 22)
    for i, st in enumerate((0.25, 0.6, 0.95)):
        if t < 1.25: burst(c, 640 + i * 150, 820 - i * 70, "BEEP", t, st, 74)
    if t > 1.25: burst(c, mx, 1480, "*SLAP*", t, 1.2, 90, fill=WHITE)
    caption(c); label(c, t, "6:08 AM"); sub(c, t, "it was on 0:01. i was so close", 1.4)
    return c.out()

def s_reveal(t, dur=3.8):
    z = punch(t, lerp(1.05, 1.2, ease(t / dur)))
    c = C((96, 98, 136), (70, 72, 104), cam=(600, 1180, z)); hallway(c, 0.15)
    # roommate door opens: draw dark gap then roommate leaning out
    op = ease(seg(t, 0.9, 1.3))
    if op > 0:
        c.rect(780, 820, 780 + 60 * op, 1640, (30, 28, 40), ol=None)
    zzz_sign(c, 0.15)
    if op > 0: roommate(c, t, 860, 1010, peek=op, mouth="smile", eyes="half")
    x = 330
    relief = t < 0.9
    quiet_guy(c, t, x, 960, (x - 120, 1300), (x + 60, 1100) if relief else (x + 120, 1290),
              eyes="happy" if relief else ("wide" if t < 2.3 else "half"),
              mouth="smile" if relief else ("o" if t < 2.3 else "flat"),
              brows=None if relief else 0.3, look=(1, 0), blink=blinkf(t, 3.0, 1.0))
    if relief: hand(c, x + 60, 1100, 20)
    burst(c, 330, 700, "phew...", t, 0.15, 60, fill=WHITE, wob=False) if relief else None
    bubble(c, 640, 760, "bro i've been up since 5", t, 1.4)
    caption(c); label(c, t, "6:10 AM"); sub(c, t, "follow for part 2", 2.5)
    return c.out()

SCENES = [
    ("b1", 3.0, s_creak),
    ("b2", 3.0, s_spoon),
    ("b3", 3.0, s_cereal),
    ("b4", 3.0, s_micro),
    ("b5", 3.8, s_reveal),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"b1": 1.8, "b2": [0.7, 1.6], "b3": 2.0, "b4": [0.9, 1.6], "b5": 2.8}
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
