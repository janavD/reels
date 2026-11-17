"""Video-call props: desk caller (shirt + tie on top, pajama pants + fuzzy slippers under the desk, free arms),
call_grid (2x2 tiles of coworkers + me, green talking border, muted-mic icon, toolbar), toast card.
From 2026-11-17_0900 "speaking up in the meeting while on mute" reel."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, hand, limb, back, seg, lerp, mix, ease)

PJ = (130, 160, 220); SHIRT = (245, 246, 250); TIE = (205, 60, 70)
RED = (230, 70, 70); GRN = (80, 210, 120); SCREEN = (38, 40, 50)

def under_desk_legs(c, x, t, wiggle=0.0):
    """pajama pants + fuzzy pink slippers, visible between the desk drawers (desk top y 1385-1462)."""
    for side in (-1, 1):
        sw = math.sin(t * 8 + side) * wiggle
        x0 = x + side * 65
        c.rect(x0 - 42, 1462, x0 + 42, 1585, PJ, w=7)
        for (sx, sy) in ((x0 - 15, 1500), (x0 + 18, 1545)):
            c.circ(sx, sy, 7, (250, 230, 120), ol=None)
        c.ell(x0 - 58 + sw, 1572, x0 + 58 + sw, 1640, (255, 170, 200), w=6)
        for k in range(5):
            fx = x0 - 46 + k * 23 + sw
            c.line([(fx, 1580), (fx - 6, 1566)], w=4, fill=(255, 210, 225), caps=False)

def caller(c, t, x, y, la, ra, eyes="open", mouth="smile", brows=None, look=(0, 0), tilt=0.0, sweat=False,
           blink=0.0, shake=0.0, blush=False):
    """seated guy behind the desk, head centre (x, y); la/ra hand targets (absolute). Draw desk + laptop after."""
    r = random.Random(int(t * 30) + 11)
    dx, dy = r.uniform(-shake, shake), r.uniform(-shake, shake); x += dx; y += dy
    c.poly([(x - 75, y + 110), (x + 75, y + 110), (x + 95, 1400), (x - 95, 1400)], SHIRT, w=7)
    c.poly([(x - 14, y + 118), (x + 14, y + 118), (x + 24, y + 300), (x, y + 330), (x - 24, y + 300)], TIE, w=5)
    c.poly([(x - 40, y + 106), (x, y + 128), (x - 30, y + 150)], WHITE, w=5)
    c.poly([(x + 40, y + 106), (x, y + 128), (x + 30, y + 150)], WHITE, w=5)
    la = (la[0] + dx, la[1] + dy); ra = (ra[0] + dx, ra[1] + dy)
    limb(c, (x - 62, y + 150), la, 112, 112, bend=1)
    limb(c, (x + 62, y + 150), ra, 112, 112, bend=-1)
    head(c, x, y, 108, tilt=tilt, eyes=eyes, mouth=mouth, look=look, brows=brows, t=t, sweat=sweat, blink=blink, blush=blush)
    return la, ra

# ---------- call screen ----------
TILES = [(50, 450, 530, 950), (550, 450, 1030, 950), (50, 970, 530, 1470), (550, 970, 1030, 1470)]

def tile_person(c, box, t, kind, eyes="open", mouth="smile", brows=None, talk=False, look=(0, 0), sweat=False,
                arm=None, blink=0.0, shake=0.0):
    x0, y0, x1, y1 = box
    walls = {"boss": (196, 214, 230), "kai": (234, 214, 180), "mia": (214, 230, 200), "me": (236, 222, 200)}
    c.rect(x0, y0, x1, y1, walls[kind], ol=None, r=18)
    # tiny background props
    if kind == "boss":
        c.rect(x0 + 30, y0 + 60, x0 + 150, y0 + 150, (250, 250, 250), w=5); c.line([(x0 + 45, y0 + 130), (x0 + 80, y0 + 95), (x0 + 105, y0 + 115), (x0 + 135, y0 + 75)], w=5, fill=GRN)
    elif kind == "kai":
        c.rect(x1 - 120, y0 + 160, x1 - 50, y0 + 240, (240, 240, 240), w=5, r=8)
        for a in (-0.5, 0, 0.5): c.line([(x1 - 85, y0 + 160), (x1 - 85 + math.sin(a) * 50, y0 + 100)], w=10, fill=(90, 170, 90))
    elif kind == "mia":
        for i, col in enumerate(((220, 80, 80), (80, 140, 220), (240, 190, 70))):
            c.rect(x0 + 40 + i * 34, y0 + 70, x0 + 68 + i * 34, y0 + 160, col, w=4)
    else:
        c.rect(x1 - 150, y0 + 60, x1 - 40, y0 + 160, (140, 200, 245), w=5)
    r = random.Random(int(t * 30) + len(kind))
    sx, sy = r.uniform(-shake, shake), r.uniform(-shake, shake)
    cx, cy = (x0 + x1) / 2 + sx, y0 + 260 + sy
    # body
    body = {"boss": (70, 80, 110), "kai": (230, 150, 70), "mia": (150, 110, 190), "me": SHIRT}[kind]
    c.poly([(cx - 70, cy + 70), (cx + 70, cy + 70), (cx + 130, y1), (cx - 130, y1)], body, w=6)
    if kind == "me":
        c.poly([(cx - 10, cy + 76), (cx + 10, cy + 76), (cx + 18, y1 - 30), (cx - 18, y1 - 30)], TIE, w=4)
    if arm is not None:  # raised / gesturing hand (offset from centre)
        hx, hy = cx + arm[0], cy + arm[1]
        limb(c, (cx + 55, cy + 110), (hx, hy), 80, 80, bend=-1, w=11); hand(c, hx, hy, 17)
    # hair behind head
    if kind == "mia":
        c.ell(cx - 92, cy - 90, cx + 92, cy + 110, (110, 70, 50), w=6)
    hk = 0.72
    m = mouth
    if talk: m = "o" if math.sin(t * 20) > 0 else "smile"
    head(c, cx, cy, 108 * hk, eyes=eyes, mouth=m, brows=brows, look=look, t=t, sweat=sweat, blink=blink)
    if kind == "boss":
        for gx in (-40, 40):
            c.arc(cx + gx * hk - 22, cy - 14 * hk - 22, cx + gx * hk + 22, cy - 14 * hk + 22, 0, 360, w=5)
        c.line([(cx - 7, cy - 12), (cx + 7, cy - 12)], w=5)
        c.arc(cx - 80, cy - 95, cx + 80, cy - 20, 200, 340, w=12, fill=(170, 170, 175))
    elif kind == "kai":
        c.chord(cx - 80, cy - 105, cx + 80, cy - 20, 180, 360, (40, 40, 48), w=5)
        c.rect(cx - 10, cy - 70, cx + 110, cy - 52, (40, 40, 48), w=5, r=6)
    elif kind == "mia":
        c.chord(cx - 80, cy - 100, cx + 80, cy - 10, 180, 360, (110, 70, 50), w=5)
    # name tag
    names = {"boss": "boss", "kai": "Kai", "mia": "Mia", "me": "me"}
    c.rect(x0 + 16, y1 - 62, x0 + 30 + 26 * len(names[kind]) + 40, y1 - 16, (20, 20, 26), ol=None, r=12)
    c.text(x0 + 30 + 13 * len(names[kind]) + 26, y1 - 39, names[kind], 30, fill=WHITE, stroke=None)
    if talk:
        c.rect(x0, y0, x1, y1, None, ol=GRN, w=10, r=18)

def mute_icon(c, x, y, s=1.0, muted=True, pulse=0.0):
    rr = 34 * s * (1 + 0.15 * pulse)
    c.circ(x, y, rr, RED if muted else (70, 74, 88), w=5)
    c.rect(x - 9 * s, y - 20 * s, x + 9 * s, y + 6 * s, WHITE, ol=None, r=9 * s)
    c.arc(x - 15 * s, y - 14 * s, x + 15 * s, y + 14 * s, 0, 180, w=4 * s, fill=WHITE)
    c.line([(x, y + 14 * s), (x, y + 22 * s)], w=4 * s, fill=WHITE, caps=False)
    if muted: c.line([(x - 20 * s, y - 20 * s), (x + 20 * s, y + 20 * s)], w=6 * s, fill=WHITE)

def toolbar(c, muted=True, pulse=0.0):
    c.rect(200, 1495, 880, 1585, (24, 24, 30), ol=None, r=40)
    mute_icon(c, 330, 1540, 1.0, muted, pulse)
    c.circ(470, 1540, 34, (70, 74, 88), w=5); c.rect(452, 1528, 480, 1552, WHITE, ol=None, r=5)   # camera
    c.poly([(480, 1534), (494, 1526), (494, 1554), (480, 1546)], WHITE, ol=None)
    c.circ(610, 1540, 34, (70, 74, 88), w=5)                                                        # chat
    c.rect(592, 1526, 628, 1550, WHITE, ol=None, r=6)
    c.rect(700, 1512, 840, 1568, RED, w=5, r=28); c.text(770, 1540, "leave", 30, fill=WHITE, stroke=None)

def call_grid(c, t, people, muted=True, pulse=0.0):
    """people: dict kind -> kwargs for tile_person. order boss, kai, mia, me."""
    c.rect(0, 400, 1080, 1640, SCREEN, ol=None)
    c.text(540, 425, "Weekly Team Sync  ·  00:14:32", 28, fill=(180, 184, 196), stroke=None)
    for box, kind in zip(TILES, ("boss", "kai", "mia", "me")):
        tile_person(c, box, t, kind, **people.get(kind, {}))
    bx0, by0, bx1, by1 = TILES[3]
    if muted: mute_icon(c, bx1 - 50, by1 - 40, 0.85, True, pulse)
    toolbar(c, muted, pulse)

def toast(c, x, y, s, t, start, w=760, col=(24, 24, 30)):
    k = back(seg(t, start, start + 0.3))
    if k <= 0.01: return
    c.rect(x - w / 2 * k, y - 70 * k, x + w / 2 * k, y + 70 * k, col, w=6, r=30 * k)
    c.text(x, y, s, 44 * k, fill=WHITE, stroke=None)
