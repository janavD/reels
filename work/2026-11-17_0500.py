"""Funny late-night reel: 5am "no point sleeping now, i'll just stay up" -> productive -> crash in class -> awake again at night."""
import sys, math, random, os
sys.path.insert(0, 'engine'); sys.path.insert(0, 'engine/library')
import rig
from rig import (C, INK, SKIN, WHITE, head, hand, limb, label, sub, caption, punch, blinkf, back, ease, eout, seg, lerp,
                 mix, room, bed, blanket, nightstand, floor, shelf, WALL_NIGHT, WALL_DAY)
from gaming_room import bubble, sky_window
from night_noise import bedside_clock, kitchen
from all_nighter import stander, checklist, classroom, student_desk, seated, teacher
from PIL import Image

rig.CAP = ['me at 5am: "no point', 'sleeping now, i\'ll', 'just stay up"']
YEL = (255, 220, 60)

def tag(c, x, y, s, t, start, sz=70, fill=YEL, end=None):
    if end is not None and t > end: return
    k = back(seg(t, start, start + 0.22))
    if k > 0.01: c.text(x, y, s, sz * k, fill=fill, sw=9)

def shaker(t, amt):
    r = random.Random(int(t * 30) + 5); return r.uniform(-amt, amt), r.uniform(-amt, amt)

def bedroom(t, z, sky, cx=420, cy=1190, shake=0.0):
    sx, sy = shaker(t, shake)
    wall = tuple(mix(a, b, sky) for a, b in zip(WALL_NIGHT, WALL_DAY))
    c = C(*wall, cam=(cx + sx, cy + sy, z))
    sky_window(c, t, sky); shelf(c, sky < 0.5); floor(c, sky < 0.5)
    return c

def s_math(t, dur=3.2):
    z = punch(t, lerp(1.1, 1.22, ease(t / dur)))
    c = bedroom(t, z, 0.0); nightstand(c, True); bedside_clock(c, "5:00")
    bed(c, True)
    head(c, 315, 1235, 105, eyes="wide", mouth="flat", look=(1, -1), brows=0.2 if t > 1.6 else None, t=t,
         blink=blinkf(t, 2.2, 0.6))
    blanket(c, True)
    # hand pops out, counting fingers
    n = min(2, int(seg(t, 0.5, 1.9) * 3))
    hx, hy = 470, 1090 + math.sin(t * 8) * 6
    limb(c, (440, 1320), (hx, hy), 120, 120, bend=-1)
    for i in range(n): c.line([(hx - 12 + i * 22, hy - 10), (hx - 16 + i * 22, hy - 62)], w=13)
    hand(c, hx, hy, 23)
    if t > 0.5: tag(c, 600, 1000, ["1 hr...", "2 hrs..."][max(0, n - 1)] if n else "", t, 0.5, 56, fill=WHITE)
    bubble(c, 560, 870, "2 hours?? not worth it", t, 2.0)
    caption(c); label(c, t, "5:00 AM"); sub(c, t, "alarm is at 7", 0.4)
    return c.out()

def s_hype(t, dur=2.8):
    z = punch(t, lerp(1.0, 1.08, ease(t / dur)), 0.12)
    c = bedroom(t, z, lerp(0.35, 0.55, t / dur), cx=560, cy=1160)
    bed(c, True)
    jump = abs(math.sin(t * 7)) * 40 if t > 0.3 else 0
    stander(c, t, 440, 1000 - jump, eyes="wide", mouth="grin", brows=-0.3, look=(0, -0.5), arms_up=ease(seg(t, 0.1, 0.5)))
    for i, (sx, sy) in enumerate(((240, 780), (650, 760), (720, 1000))):
        k = back(seg(t, 0.5 + i * 0.15, 0.75 + i * 0.15))
        if k > 0.01: c.text(sx, sy, "!", 90 * k, fill=YEL, sw=8)
    bubble(c, 780, 1190, "i'm built different", t, 0.9)
    caption(c); label(c, t, "5:01 AM"); sub(c, t, "who needs sleep anyway", 0.5)
    return c.out()

def s_productive(t, dur=3.4):
    z = punch(t, lerp(1.0, 1.06, ease(t / dur)))
    c = C((150, 160, 182), (120, 128, 150), cam=(560, 1160, z)); kitchen(c, 0.0)
    c.glow(820, 650, 520, (255, 210, 150), 0.22)       # morning light
    stander(c, t, 330, 990, eyes="happy", mouth="laugh", pan=True, bounce=18, blush=True)
    with c.ui():
        checklist(c, 790, 560, ["clean room", "make breakfast", "plan my life"], t, (0.6, 1.4, 2.2))
    caption(c); label(c, t, "5:30 AM"); sub(c, t, "most productive man alive", 0.4)
    return c.out()

def s_nod(t, dur=3.4):
    z = punch(t, lerp(1.06, 1.16, ease(t / dur)))
    c = C((226, 214, 186), (206, 192, 160), cam=(540, 1160, z)); classroom(c, t, "9:00")
    ph = (t % 1.1) / 1.1                              # slow droop, sudden jerk back up
    nod = ease(seg(ph, 0.0, 0.85)) if ph < 0.85 else 1 - seg(ph, 0.85, 0.95)
    jerk = 0.85 < ph < 1.0
    seated(c, t, nod=nod * 0.9, eyes="wide" if jerk else "half", mouth="o" if jerk else "flat",
           brows=0.35 if jerk else None, look=(0, 0) if jerk else (0, 1))
    student_desk(c)
    if jerk: tag(c, 400, 900, "!", t, (t // 1.1) * 1.1 + 0.94, 90)
    caption(c); label(c, t, "9:00 AM"); sub(c, t, "the crash hits", 0.4)
    return c.out()

def s_sleep(t, dur=3.4):
    z = punch(t, lerp(1.08, 1.18, ease(t / dur)))
    c = C((226, 214, 186), (206, 192, 160), cam=(600, 1180, z)); classroom(c, t, "9:04")
    seated(c, t, sleep=True)
    student_desk(c)
    teacher(c, t, x=930, y=980, mouth="o" if t < 1.4 else "flat", brows=0.35)
    for i in range(3):
        ph = (t * 0.8 + i / 3) % 1
        c.text(430 - ph * 80, 1150 - ph * 220, "z", 40 + ph * 40, fill=WHITE, sw=6)
    bubble(c, 820, 830, "...is he okay?", t, 0.6)
    tag(c, 260, 1120, "*snore*", t, 1.6, 56, fill=WHITE)
    caption(c); label(c, t, "9:04 AM"); sub(c, t, "asleep in 4 minutes", 0.4)
    return c.out()

def s_night(t, dur=3.6):
    z = punch(t, lerp(1.1, 1.22, ease(t / dur)))
    c = bedroom(t, z, 0.0, cy=1200); nightstand(c, True); bedside_clock(c, "2:47")
    bed(c, True)
    head(c, 315, 1235, 105, eyes="wide", mouth="flat" if t < 1.6 else "frown", look=(0, -1),
         brows=0.3 if t > 1.6 else None, t=t, blink=blinkf(t, 3.0, 1.8))
    blanket(c, True)
    tag(c, 560, 1060, "*crickets*", t, 0.4, 46, fill=WHITE, end=1.5)
    bubble(c, 560, 900, "...why am i not tired now", t, 1.5)
    caption(c); label(c, t, "that night"); sub(c, t, "follow for part 2", 2.0)
    return c.out()

SCENES = [
    ("a1", 3.2, s_math),
    ("a2", 2.8, s_hype),
    ("a3", 3.4, s_productive),
    ("a4", 3.4, s_nod),
    ("a5", 3.4, s_sleep),
    ("a6", 3.6, s_night),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"a1": 2.6, "a2": 1.6, "a3": 2.6, "a4": [0.7, 1.0], "a5": 2.0, "a6": 2.6}
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
