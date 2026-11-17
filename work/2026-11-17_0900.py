"""Funny work-from-home reel: finally speaking up in the meeting -> 2-minute passionate pitch -> "you're on mute"
-> unmute "ok so as i was saying" -> host ended the meeting."""
import sys, math, random, os
sys.path.insert(0, 'engine'); sys.path.insert(0, 'engine/library')
import rig
from rig import (C, INK, WHITE, hand, label, sub, caption, punch, blinkf, back, ease, eout, seg, lerp, mix,
                 room, desk, laptop_back, WALL_DAY)
from gaming_room import bubble
from quiet_morning import burst
from video_call import caller, under_desk_legs, call_grid, toast, RED
from PIL import Image

rig.CAP = ['POV: you finally speak', 'up in the work meeting']

def shk(t, amt):
    r = random.Random(int(t * 30) + 5); return r.uniform(-amt, amt), r.uniform(-amt, amt)

def office(t, z, sx=0, sy=0, cy=1180):
    c = C(*WALL_DAY, cam=(540 + sx, cy + sy, z)); room(c, False, t, cal=None)
    return c

def s_ready(t, dur=3.0):
    z = punch(t, lerp(0.9, 0.97, ease(t / dur)))
    c = office(t, z)
    under_desk_legs(c, 540, t, wiggle=6)
    k = ease(seg(t, 0.2, 0.9)); thumbs = t > 1.4
    la = (lerp(430, 440, k), lerp(1300, 820, k))                    # fixing hair
    ra = (720, 960) if thumbs else (640, 1300)
    caller(c, t, 540, 905, la, ra, eyes="happy" if thumbs else "open", mouth="grin" if thumbs else "smile",
           look=(0, 1), blink=blinkf(t, 2.4, 0.5))
    hand(c, *la, 21); hand(c, *ra, 21, thumb=-math.pi / 2 if thumbs else None)
    desk(c, False); laptop_back(c)
    bubble(c, 300, 700, "camera on. looking pro.", t, 0.5)
    pk = back(seg(t, 1.6, 1.9))
    if pk > 0.05:
        c.text(860, 1500, "pajama pants", 40 * pk, sw=7); c.line([(800, 1530), (660, 1545)], w=7)
    caption(c); label(c, t, "9:00 AM")
    return c.out()

def s_ideas(t, dur=3.0):
    z = punch(t, 1.0)
    c = C((38, 40, 50), (30, 32, 40), cam=(540, 1060, z))
    raise_k = ease(seg(t, 1.0, 1.4))
    call_grid(c, t, {
        "boss": dict(talk=t < 1.2, brows=-0.1, blink=blinkf(t, 2.2)),
        "kai": dict(eyes="half", mouth="flat"),
        "mia": dict(mouth="flat", look=(-1, 0), blink=blinkf(t, 2.6, 1.0)),
        "me": dict(eyes="wide" if t > 1.0 else "open", mouth="grin" if t > 1.0 else "flat", brows=-0.2 if t > 1.0 else None,
                   arm=(lerp(60, 110, raise_k), lerp(150, -120, raise_k)) if raise_k > 0 else None),
    }, muted=True)
    bubble(c, 330, 480, "any ideas, team?", t, 0.2)
    burst(c, 690, 1060, "ME!!", t, 1.3, 90)
    caption(c); sub(c, t, "i've been waiting for this", 1.6)
    return c.out()

def s_pitch(t, dur=3.6):
    sx, sy = shk(t, 3)
    z = punch(t, lerp(1.0, 1.12, ease(t / dur)))
    c = office(t, z, sx, sy, cy=1120)
    w = math.sin(t * 7)
    la = (lerp(330, 360, w), 900 + 90 * math.sin(t * 6.3))
    ra = (lerp(720, 760, -w), 850 + 110 * math.sin(t * 5.1 + 1))
    caller(c, t, 540, 905, la, ra, eyes="wide" if (t % 1.2) < 0.6 else "happy", mouth="laugh", brows=-0.25,
           tilt=0.08 * math.sin(t * 4), look=(0, 1))
    hand(c, *la, 21); hand(c, *ra, 21)
    desk(c, False); laptop_back(c)
    bubble(c, 290, 500, "ok so what if we...", t, 0.2)
    bubble(c, 820, 630, "and THEN...", t, 1.2)
    bubble(c, 290, 760, "trust me on this", t, 2.1)
    secs = int(lerp(3, 128, ease(seg(t, 0.0, 3.0))))
    with c.ui():
        c.rect(800, 1000, 1040, 1080, WHITE, w=6, r=30); c.text(920, 1040, f"{secs // 60}:{secs % 60:02d}", 50, fill=INK, stroke=None)
    caption(c); label(c, t, "2 MINUTES LATER"); sub(c, t, "best idea of my life", 2.4)
    return c.out()

def s_mute(t, dur=3.2):
    zk = ease(seg(t, 1.2, 1.9))
    z = lerp(1.0, 1.55, zk)
    c = C((38, 40, 50), (30, 32, 40), cam=(lerp(540, 790, zk), lerp(1060, 1230, zk), z))
    pulse = abs(math.sin(t * 9)) if t > 1.3 else 0
    call_grid(c, t, {
        "boss": dict(talk=0.3 < t < 1.2, eyes="half", mouth="flat"),
        "kai": dict(eyes="half", mouth="flat", brows=0.2),
        "mia": dict(eyes="half", mouth="flat", brows=-0.2),
        "me": dict(eyes="wide" if t > 1.9 else "happy", mouth="scream" if t > 1.9 else "laugh",
                   brows=0.4 if t > 1.9 else -0.2, sweat=t > 1.9, arm=(110, -100), shake=5 if t > 1.9 else 0),
    }, muted=True, pulse=pulse)
    with c.ui():
        bubble(c, 330, 520, "...you're on mute", t, 0.3)
        burst(c, 540, 1480, "MUTED", t, 1.4, 130, fill=(255, 110, 110))
    caption(c); sub(c, t, "the whole time.", 2.0)
    return c.out()

def s_end(t, dur=3.8):
    sh = 10 if 0.3 < t < 0.6 else 0; sx, sy = shk(t, sh)
    z = punch(t, lerp(1.0, 1.1, ease(t / dur)))
    c = office(t, z, sx, sy, cy=1120)
    slam = t > 0.3; ended = t > 1.9
    ra = (640, 1260) if slam else (720, 980)
    la = (360, 1000) if (slam and not ended) else (420, 1290)
    caller(c, t, 540, 905, la, ra,
           eyes="half" if ended else ("open" if slam else "wide"),
           mouth="flat" if ended else ("grin" if slam else "o"),
           brows=0.15 if ended else (-0.2 if slam else 0.4), look=(0, 1), sweat=not ended, blink=blinkf(t, 3.0, 0.4))
    hand(c, *la, 21); hand(c, *ra, 21)
    desk(c, False); laptop_back(c)
    if t < 1.85: burst(c, 820, 1250, "*CLICK*", t, 0.3, 80, fill=WHITE)
    bubble(c, 330, 600, "ok so as i was saying-", t, 0.9)
    with c.ui():
        toast(c, 540, 1240, "the host ended the meeting", t, 1.9)
    caption(c); sub(c, t, "follow for part 2", 2.6)
    return c.out()

SCENES = [
    ("c1", 3.0, s_ready),
    ("c2", 3.0, s_ideas),
    ("c3", 3.6, s_pitch),
    ("c4", 3.2, s_mute),
    ("c5", 3.8, s_end),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"c1": [2.2], "c2": [2.2], "c3": [2.6], "c4": [0.9, 2.6], "c5": [2.8]}
        ims = []
        for name, dur, fn in SCENES:
            for x in times[name]: ims.append(fn(x).resize((300, 533)))
        sheet = Image.new("RGB", (300 * 3, 533 * 2), WHITE)
        for i, im in enumerate(ims[:6]): sheet.paste(im, ((i % 3) * 300, (i // 3) * 533))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
