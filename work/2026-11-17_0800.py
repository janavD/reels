"""Funny commute reel: the bus app says "1 min away" for 20 minutes -> it goes UP -> i give up and walk ->
the bus flies past and splashes me -> "arrived", next bus 30 min."""
import sys, math, random, os
sys.path.insert(0, 'engine'); sys.path.insert(0, 'engine/library')
import rig
from rig import (C, INK, WHITE, hand, label, sub, caption, punch, blinkf, back, ease, eout, seg, lerp, mix)
from gaming_room import bubble
from quiet_morning import burst, YEL
from bus_stop import street, stop_sign, commuter, phone_in_hand, app_card, rain, bus, puddle, splash
from PIL import Image

rig.CAP = ['the bus app:', '"arriving in 1 min"', '(it lies)']

SKY = ((150, 200, 240), (205, 228, 245))
GREY = ((128, 136, 150), (168, 174, 186))
STORM = ((96, 102, 116), (136, 140, 152))

def shk(t, amt):
    r = random.Random(int(t * 30) + 5); return r.uniform(-amt, amt), r.uniform(-amt, amt)

def sky_for(k):
    return (mix(SKY[0], GREY[0], k), mix(SKY[1], GREY[1], k))

def s_arrive(t, dur=3.0):
    z = punch(t, lerp(1.0, 1.1, ease(t / dur)))
    c = C(*SKY, cam=(540, 1180, z)); street(c, t)
    run = seg(t, 0, 1.0)
    x = lerp(-120, 400, eout(run))
    moving = t < 1.0
    pant = math.sin(t * 14) * 8 if not moving else 0
    ph = ease(seg(t, 1.1, 1.4))
    ra = (lerp(x + 120, x + 150, ph), lerp(1290, 1110, ph) + pant)
    la = (x - 110, 1300) if moving else (x - 40, 1260 + pant)      # hand on knee-ish while panting
    commuter(c, t, x, 960 + pant, la, ra, eyes="closed" if 1.0 < t < 1.35 else "open",
             mouth="o" if moving or t < 1.4 else "smile", look=(1, 0), walk=2.6 if moving else 0,
             tilt=0.12 if moving else 0, sweat=t > 0.6)
    if ph > 0.5: phone_in_hand(c, *ra)
    hand(c, *la, 21); hand(c, *ra, 21)
    app_card(c, 760, 760, t, 1.4, "1 min")
    bubble(c, 330, 690, "made it.", t, 2.0)
    caption(c); label(c, t, "8:00 AM"); sub(c, t, "running for the bus", 0.3)
    return c.out()

def s_wait(t, dur=3.0):
    g = ease(seg(t, 0, dur)) * 0.7
    z = punch(t, lerp(1.04, 1.14, ease(t / dur)))
    c = C(*sky_for(g), cam=(540, 1180, z)); street(c, t, gloom=g * 0.3)
    x = 400
    ra = (x + 150, 1110)
    sigh = t > 1.6
    commuter(c, t, x, 960, (x - 110, 1300), ra, eyes="half", mouth="flat", look=(1, -0.5) if not sigh else (0, 0),
             tap=2.2, tilt=-0.1 if sigh else 0.05, brows=-0.2 if sigh else None)
    phone_in_hand(c, *ra); hand(c, x - 110, 1300, 21); hand(c, *ra, 21)
    app_card(c, 760, 760, t, 0.05, "1 min")
    bubble(c, 330, 690, "...still 1 min?", t, 1.0)
    if t > 2.3: rain(c, t, 0.25)
    caption(c); label(c, t, "8:09 AM"); sub(c, t, "it's been 9 minutes", 0.4)
    return c.out()

def s_up(t, dur=3.0):
    up = t > 0.9
    sh = 9 if 0.9 < t < 1.7 else 0; sx, sy = shk(t, sh)
    z = punch(t, lerp(1.06, 1.18 if up else 1.1, ease(t / dur)))
    c = C(*STORM, cam=(540 + sx, 1180 + sy, z)); street(c, t, gloom=0.35)
    rain(c, t, 1.0, 1)
    x = 400
    ra = (x + 150, 1110) if not up else (x + 170, 960)
    la = (x - 110, 1300) if not up else (x - 120, 880)           # hand to head
    commuter(c, t, x, 960, la, ra, eyes="half" if not up else "wide", mouth="flat" if not up else "scream",
             brows=0.4 if up else None, look=(1, -0.5), wet=0.6, shake=4 if up else 0, sweat=up)
    phone_in_hand(c, *ra); hand(c, *la, 21); hand(c, *ra, 21)
    if not up: app_card(c, 760, 760, t, 0.05, "1 min")
    else: app_card(c, 760, 760, t, 0.9, "4 min", col=(225, 70, 60), shake=6)
    burst(c, 540, 1440, "IT WENT UP??", t, 1.0, 96)
    caption(c); label(c, t, "8:17 AM"); sub(c, t, "the bus is driving backwards", 1.6)
    return c.out()

def s_walk(t, dur=3.4):
    hit = 1.75
    sh = 10 if hit < t < hit + 0.5 else 0; sx, sy = shk(t, sh)
    z = punch(t, lerp(1.0, 1.06, ease(t / dur)))
    c = C(*STORM, cam=(560 + sx, 1180 + sy, z)); street(c, t, gloom=0.35, bus_sign=False)
    puddle(c, 420, 1455)
    bx = lerp(1500, -1300, seg(t, 1.25, 2.35))
    if 1.2 < t < 2.4: bus(c, bx, shake=4)
    stop_sign(c, 0.35)
    rain(c, t, 1.0, 2)
    froze = t > hit
    x = lerp(400, 260, ease(seg(t, 0.5, hit))) if not froze else 260
    walking = 0.5 < t < hit
    la = (x - 110, 1300) if not froze else (x - 150, 1100)
    ra = (x + 110, 1300) if not froze else (x + 150, 1100)
    commuter(c, t, x, 960, la, ra, eyes="half" if not froze else "wide", mouth="flat" if not froze else "o",
             brows=-0.25 if not froze else 0.35, look=(-1, 0) if not froze else (1, 0), walk=1.6 if walking else 0,
             face=-1 if t > 0.4 else 1, wet=0.6 if not froze else 1.0, shake=3 if froze and t < hit + 0.6 else 0)
    hand(c, *la, 21); hand(c, *ra, 21)
    splash(c, t, hit - 0.1, 360, 1450, toward=-1)
    bubble(c, 420, 690, "fine. i'll walk.", t, 0.15) if t < 1.3 else None
    burst(c, 700, 860, "WHOOSH", t, 1.3, 110, fill=WHITE)
    burst(c, 300, 1440, "*SPLASH*", t, hit, 100)
    caption(c); label(c, t, "8:20 AM"); sub(c, t, "the moment i leave...", 0.6)
    return c.out()

def s_end(t, dur=3.8):
    z = punch(t, lerp(1.08, 1.24, ease(t / dur)))
    c = C(*STORM, cam=(400, 1150, z)); street(c, t, gloom=0.35)
    rain(c, t, 1.0, 3)
    x = 260
    ra = (x + 150, 1110)
    commuter(c, t, x, 960, (x - 110, 1300), ra, eyes="half", mouth="flat", look=(1, -0.5), wet=1.0,
             blink=blinkf(t, 2.4, 0.6), brows=-0.15)
    phone_in_hand(c, *ra); hand(c, x - 110, 1300, 21); hand(c, *ra, 21)
    app_card(c, 760, 740, t, 0.2, "arrived", col=(60, 190, 110), sz=72)
    app_card(c, 760, 1040, t, 1.2, "next: 30 min", small="BUS 12 - Downtown", col=(225, 70, 60), sz=58)
    caption(c); label(c, t, "8:21 AM"); sub(c, t, "follow for part 2", 2.2)
    return c.out()

SCENES = [
    ("b1", 3.0, s_arrive),
    ("b2", 3.0, s_wait),
    ("b3", 3.0, s_up),
    ("b4", 3.4, s_walk),
    ("b5", 3.8, s_end),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"b1": [0.5, 2.4], "b2": 2.6, "b3": [0.5, 1.8], "b4": [1.7, 2.1], "b5": 2.8}
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
