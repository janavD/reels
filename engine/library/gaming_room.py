"""Gaming-room props: sunrise window (sky_window k=0 night..1 day), wall_clock, game_desk (generic can),
monitor(mode=play/lose/win), gaming chair, seated gamer with controller + headset (arms_up for celebrating),
bird on the sill, alarm, auto-width bubble. From 2026-11-17_0000 "ok last game" reel."""
import math, random
from rig import (C, INK, SKIN, WHITE, head, hand, limb, back, seg, lerp, mix, floor, shelf, WALL_NIGHT, WALL_DAY)
RED = (225, 70, 70); GRN = (90, 200, 120); X0, Y0 = 380, 1010

def bubble(c, x, y, s, t, start):
    k = back(seg(t, start, start + 0.3))
    if k <= 0.01: return
    w = (len(s) * 23 + 60) * k; h = 110 * k
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, WHITE, w=6, r=40 * k)
    c.poly([(x - 30 * k, y + h / 2 - 3), (x + 10 * k, y + h / 2 - 3), (x - 50 * k, y + h / 2 + 50 * k)], WHITE, ol=None)
    c.line([(x - 30 * k, y + h / 2), (x - 50 * k, y + h / 2 + 50 * k), (x + 10 * k, y + h / 2)], w=6)
    c.text(x, y, s, 42 * k, fill=INK, stroke=None)


RED = (225, 70, 70)
GRN = (90, 200, 120)
X0, Y0 = 380, 1010          # gamer head

# ---------- sets ----------
def sky_window(c, t, k):
    """window whose sky goes night (k=0) -> sunrise (k=0.6) -> day (k=1)."""
    c.rect(625, 505, 1015, 915, (240, 240, 235), w=8)
    if k < 0.6:
        kk = k / 0.6
        top = mix((18, 22, 52), (120, 110, 190), kk); bot = mix((40, 46, 92), (255, 170, 110), kk)
    else:
        kk = (k - 0.6) / 0.4
        top = mix((120, 110, 190), (120, 185, 240), kk); bot = mix((255, 170, 110), (190, 225, 250), kk)
    for i in range(8):
        c.rect(645, 525 + i * 46, 995, 525 + (i + 1) * 46 + 1, mix(top, bot, i / 7), ol=None)
    if k < 0.35:
        c.circ(915, 600, 34, (250, 246, 215), ol=None); c.circ(930, 590, 30, mix(top, bot, 0.15), ol=None)
        for i, (sx, sy) in enumerate([(690, 580), (760, 660), (850, 760), (965, 700), (700, 830), (800, 560)]):
            c.circ(sx, sy, 4 + 2.5 * math.sin(t * 5 + i * 2), (255, 255, 225), ol=None)
    if k > 0.3:  # sun rising behind the city
        sy = lerp(900, 650, clamp01((k - 0.3) / 0.7))
        c.glow(820, sy, 240, (255, 200, 120), 0.5)
        c.circ(820, sy, 55, (255, 214, 110), ol=None)
    city = mix((24, 26, 44), (90, 90, 120), k)
    c.poly([(645, 895), (645, 820), (700, 820), (700, 790), (760, 790), (760, 840), (830, 840), (830, 770),
            (880, 770), (880, 830), (995, 830), (995, 895)], city, ol=None)
    if k < 0.5:
        for (wx, wy) in [(660, 840), (720, 805), (845, 790), (900, 850), (950, 860), (780, 860)]:
            c.rect(wx, wy, wx + 14, wy + 14, (255, 214, 120), ol=None)
    c.line([(820, 525), (820, 895)], w=10); c.line([(645, 710), (995, 710)], w=10)
    c.rect(605, 905, 1035, 935, (245, 245, 240), w=6)
    cur = mix((52, 66, 110), (78, 118, 178), k)
    for (x0, x1) in ((585, 660), (980, 1055)):
        c.rect(x0, 480, x1, 990, cur, w=6)
        for fx in (x0 + 25, x0 + 50): c.line([(fx, 500), (fx, 975)], w=3, fill=mix(cur, (0, 0, 0), 0.3), caps=False)
    c.line([(560, 482), (1080, 482)], w=12)

def clamp01(x): return max(0.0, min(1.0, x))

def wall_clock(c, txt, x=210, y=640):
    c.rect(x - 105, y - 52, x + 105, y + 52, (40, 40, 48), w=7, r=16)
    c.text(x, y, txt, 58, fill=(255, 90, 90), stroke=None)

def game_desk(c, night):
    wood = (118, 80, 58) if night else (166, 108, 62)
    c.rect(620, 1400, 1120, 1450, wood, w=8)
    c.rect(1010, 1450, 1060, 1650, mix(wood, (0, 0, 0), 0.15), w=6)
    c.rect(660, 1450, 710, 1650, mix(wood, (0, 0, 0), 0.15), w=6)
    # energy-drink can (generic, sponsor slot) + snack bowl
    c.rect(1030, 1300, 1080, 1400, (120, 210, 170), w=5, r=8)
    c.rect(1030, 1330, 1080, 1360, WHITE, ol=None); c.line([(1036, 1300), (1074, 1300)], w=6)

def monitor(c, t, mode, night=True):
    # stand
    c.rect(840, 1340, 880, 1400, (60, 60, 70), w=5); c.ell(790, 1385, 930, 1410, (60, 60, 70), w=5)
    c.rect(690, 1080, 1030, 1350, (35, 35, 42), w=8, r=14)
    x0, y0, x1, y1 = 712, 1100, 1008, 1328
    scr = {"play": (40, 70, 140), "lose": (120, 30, 40), "win": (40, 120, 70)}[mode]
    c.rect(x0, y0, x1, y1, scr, ol=None)
    c.rect(x0, 1270, x1, y1, mix(scr, (0, 0, 0), 0.35), ol=None)  # ground
    # two tiny fighters
    j = math.sin(t * 14) * 8
    for i, (fx, col) in enumerate(((800 + j, (255, 220, 80)), (920 - j, (240, 120, 200)))):
        if mode == "lose" and i == 0:
            c.line([(fx - 25, 1262), (fx + 25, 1262)], w=8, fill=col); c.circ(fx + 34, 1258, 11, col, ol=None)
            continue
        if mode == "win" and i == 1:
            c.line([(fx - 25, 1262), (fx + 25, 1262)], w=8, fill=col); c.circ(fx + 34, 1258, 11, col, ol=None)
            continue
        c.circ(fx, 1200, 14, col, ol=None); c.line([(fx, 1212), (fx, 1240)], w=7, fill=col)
        c.line([(fx, 1240), (fx - 12, 1268)], w=6, fill=col); c.line([(fx, 1240), (fx + 12, 1268)], w=6, fill=col)
        c.line([(fx, 1222), (fx + (18 if i == 0 else -18), 1214 + j * 0.6)], w=6, fill=col)
    # health bars
    c.rect(725, 1112, 845, 1126, (255, 255, 255), ol=None); c.rect(875, 1112, 995, 1126, WHITE, ol=None)
    hp1 = {"play": 0.7, "lose": 0.0, "win": 0.4}[mode]; hp2 = {"play": 0.6, "lose": 0.8, "win": 0.0}[mode]
    if hp1: c.rect(725, 1112, 725 + 120 * hp1, 1126, GRN, ol=None)
    if hp2: c.rect(995 - 120 * hp2, 1112, 995, 1126, GRN, ol=None)
    if mode in ("lose", "win"):
        k = back(seg(t, 0.2, 0.5))
        if k > 0.01:
            c.text(860, 1165, "DEFEAT" if mode == "lose" else "VICTORY", 50 * k,
                   fill=(255, 120, 120) if mode == "lose" else (255, 235, 120), sw=6)
    c.glow(860, 1215, 420, mix(scr, WHITE, 0.4), 0.35 if night else 0.15)

def chair(c):
    c.rect(220, 1080, 540, 1420, (200, 60, 70), w=8, r=60)           # back
    c.rect(250, 1120, 510, 1380, mix((200, 60, 70), (0, 0, 0), 0.2), ol=None, r=40)
    c.rect(230, 1390, 530, 1460, (180, 50, 60), w=7, r=20)            # seat
    c.line([(380, 1460), (380, 1580)], w=16)
    c.line([(270, 1610), (490, 1610)], w=12)
    for x in (270, 380, 490): c.circ(x, 1625, 16, (60, 60, 70), w=5)

def gamer(c, t, eyes="open", mouth="smile", brows=None, tilt=0.0, look=(1, 0.2), mash=1.0, arms_up=0.0,
          sweat=False, blink=0.0, yoff=0.0, bags=False):
    x, y = X0, Y0 + yoff
    hip = (x, 1400)
    # legs (seated, knees apart, feet down)
    for side in (-1, 1):
        kn = (x + side * 95, 1440); ft = (x + side * 110, 1630)
        c.line([hip, kn, ft], w=14); c.line([ft, (ft[0] + side * 38, ft[1] + 2)], w=14)
    # torso + hoodie
    c.poly([(x - 70, y + 120), (x + 70, y + 120), (x + 85, 1405), (x - 85, 1405)], (90, 96, 120), w=7)
    c.line([(x - 20, y + 140), (x - 26, y + 230)], w=4, fill=WHITE); c.line([(x + 20, y + 140), (x + 26, y + 230)], w=4, fill=WHITE)
    sh_l, sh_r = (x - 62, y + 150), (x + 62, y + 150)
    # controller position (mash jitter)
    r = random.Random(int(t * 30))
    jx, jy = r.uniform(-6, 6) * mash, r.uniform(-5, 5) * mash
    cx, cy = x + 40 + jx, y + 300 + jy
    if arms_up > 0.01:
        ku = arms_up; wig = math.sin(t * 18) * 18 * ku
        tl = (lerp(cx - 70, x - 175, ku), lerp(cy, y - 150 + wig, ku))
        tr = (lerp(cx + 70, x + 175, ku), lerp(cy, y - 150 - wig, ku))
        cx, cy = lerp(cx, tr[0], ku), lerp(cy, tr[1] - 40, ku)
    else:
        tl, tr = (cx - 70, cy + 8), (cx + 70, cy + 8)
    limb(c, sh_l, tl, 108, 108, bend=1); limb(c, sh_r, tr, 108, 108, bend=-1)
    # controller
    c.rect(cx - 85, cy - 32, cx + 85, cy + 32, (60, 62, 74), w=6, r=30)
    c.circ(cx + 45, cy - 6, 8, RED, ol=None); c.circ(cx + 62, cy + 8, 8, GRN, ol=None)
    c.line([(cx - 60, cy), (cx - 36, cy)], w=6, fill=WHITE); c.line([(cx - 48, cy - 12), (cx - 48, cy + 12)], w=6, fill=WHITE)
    hand(c, *tl, 22); hand(c, *tr, 22)
    # headset
    head(c, x, y, 110, tilt=tilt, eyes=eyes, mouth=mouth, look=look, brows=brows, t=t, sweat=sweat, blink=blink)
    c.arc(x - 118, y - 135, x + 118, y + 70, 190, 350, w=16, fill=(50, 50, 60))
    c.ell(x - 135, y - 40, x - 95, y + 40, (50, 50, 60), w=5); c.ell(x + 95, y - 40, x + 135, y + 40, (50, 50, 60), w=5)
    if bags:
        for sx in (-40, 40): c.arc(x + sx - 24, y - 4, x + sx + 24, y + 22, 20, 160, w=5, fill=(140, 120, 170))
    c.glow(x + 60, y + 20, 200, (150, 190, 255), 0.18)

def base(t, z, sky=0.0, shake=0.0, cx=560, cy=1120):
    r = random.Random(int(t * 30) + 7)
    wall = tuple(mix(a, b, sky) for a, b in zip(WALL_NIGHT, WALL_DAY))
    c = C(*wall, cam=(cx + r.uniform(-shake, shake), cy + r.uniform(-shake, shake), z))
    sky_window(c, t, sky); shelf(c, sky < 0.5); floor(c, sky < 0.5)
    return c

def bird(c, t, x=900, y=905, chirp=True):
    hop = abs(math.sin(t * 6)) * 10
    y -= hop
    c.ell(x - 34, y - 48, x + 30, y, (120, 170, 230), w=6)
    c.circ(x + 22, y - 54, 22, (120, 170, 230), w=6)
    c.circ(x + 28, y - 58, 4, INK, ol=None)
    op = 6 if (chirp and math.sin(t * 20) > 0) else 0
    c.poly([(x + 42, y - 60), (x + 62, y - 54 + op * 0.3), (x + 42, y - 48)], (255, 190, 60), w=4)
    c.line([(x - 8, y), (x - 8, y + 10 + hop)], w=4); c.line([(x + 8, y), (x + 8, y + 10 + hop)], w=4)

def tag(c, x, y, s, t, start, sz=46, fill=WHITE):
    k = back(seg(t, start, start + 0.25))
    if k > 0.01: c.text(x, y, s, sz * k, fill=fill, sw=7)

def alarm(c, t, ring, x=700, y=905):
    jx = math.sin(t * 90) * 7 if ring else 0
    cx0 = x + jx; h = 90
    c.circ(cx0 - 38, y - h - 12, 18, RED, w=5); c.circ(cx0 + 38, y - h - 12, 18, RED, w=5)
    c.rect(cx0 - 55, y - h, cx0 + 55, y, RED, w=6, r=20)
    c.rect(cx0 - 40, y - h + 14, cx0 + 40, y - 14, (25, 25, 30), w=4, r=6)
    c.text(cx0, y - h / 2, "7:00", 26, fill=(255, 80, 80), stroke=None)
    if ring:
        for i in range(3):
            r0 = 70 + i * 22 + (t * 200) % 22
            c.arc(cx0 - r0, y - 50 - r0, cx0 + r0, y - 50 + r0, 200, 250, w=5, fill=(255, 230, 120))
            c.arc(cx0 - r0, y - 50 - r0, cx0 + r0, y - 50 + r0, 290, 340, w=5, fill=(255, 230, 120))

