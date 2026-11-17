"""Funny late-night reel: "ok last game, then i sleep" -> plays till sunrise."""
import sys, math, random, os
sys.path.insert(0, 'engine')
import rig
from rig import (C, INK, SKIN, WHITE, head, hand, limb, ik, label, sub, caption, punch, blinkf, back,
                 ease, eout, seg, lerp, mix, floor, shelf, WALL_NIGHT, WALL_DAY)
from PIL import Image

def bubble(c, x, y, s, t, start):
    k = back(seg(t, start, start + 0.3))
    if k <= 0.01: return
    w = (len(s) * 23 + 60) * k; h = 110 * k
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, WHITE, w=6, r=40 * k)
    c.poly([(x - 30 * k, y + h / 2 - 3), (x + 10 * k, y + h / 2 - 3), (x - 50 * k, y + h / 2 + 50 * k)], WHITE, ol=None)
    c.line([(x - 30 * k, y + h / 2), (x - 50 * k, y + h / 2 + 50 * k), (x + 10 * k, y + h / 2)], w=6)
    c.text(x, y, s, 42 * k, fill=INK, stroke=None)

rig.CAP = ['me at midnight:', '"ok last game,', 'then i sleep"']

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

# ---------- scenes ----------
def s_start(t, dur=3.0):
    z = punch(t, lerp(1.0, 1.08, ease(t / dur)))
    c = base(t, z); wall_clock(c, "11:58")
    chair(c); game_desk(c, True); monitor(c, t, "play")
    gamer(c, t, eyes="open", mouth="smile", blink=blinkf(t, 2.4, 0.6), mash=0.6, tilt=math.sin(t * 3) * 0.03)
    bubble(c, 390, 790, "just one more", t, 0.6)
    caption(c); label(c, t, "11:58 PM"); sub(c, t, "gaming before bed", 0.5)
    return c.out()

def s_lose(t, dur=3.2):
    z = punch(t, lerp(1.06, 1.16, ease(t / dur)))
    c = base(t, z, shake=6 if t > 0.4 else 0); wall_clock(c, "1:34")
    chair(c); game_desk(c, True); monitor(c, t, "lose")
    mad = ease(seg(t, 0.35, 0.6))
    gamer(c, t, eyes="wide" if t < 0.6 else "open", mouth="o" if t < 0.6 else "grit", brows=0.45 * mad,
          mash=0.2 if t < 0.5 else 2.5, look=(1, 0), tilt=math.sin(t * 20) * 0.05 * mad)
    if t > 0.6:  # steam
        for i in range(3):
            ph = (t * 1.5 + i / 3) % 1
            c.circ(X0 - 80 + i * 80, Y0 - 140 - ph * 120, 16 + ph * 22, (230, 230, 240), ol=None)
    bubble(c, 400, 780, "can't end on a loss", t, 0.9)
    caption(c); label(c, t, "1:34 AM"); sub(c, t, "ok ONE more", 1.3)
    return c.out()

def s_win(t, dur=3.2):
    z = punch(t, lerp(1.06, 1.14, ease(t / dur)))
    c = base(t, z); wall_clock(c, "3:52")
    chair(c); game_desk(c, True); monitor(c, t, "win")
    up = back(seg(t, 0.35, 0.7))
    hop = -abs(math.sin(t * 10)) * 25 * up
    gamer(c, t, eyes="happy" if t > 0.4 else "open", mouth="laugh" if t > 0.4 else "smile", arms_up=up, mash=0.0,
          yoff=hop, look=(1, 0))
    for i in range(10):  # confetti
        rr = random.Random(i)
        ph = ((t - 0.4) * 0.9 + rr.random()) % 1
        if t > 0.4:
            px = rr.uniform(120, 1000); py = 700 + ph * 900
            c.rect(px, py, px + 18, py + 30, rr.choice([(255, 210, 60), (110, 200, 255), (255, 120, 160)]), ol=None)
    bubble(c, 400, 745, "now i'm warmed up", t, 1.2)
    caption(c); label(c, t, "3:52 AM"); sub(c, t, "best of 3?", 1.6)
    return c.out()

def s_birds(t, dur=3.4):
    z = punch(t, lerp(1.04, 1.12, ease(t / dur)))
    sky = lerp(0.35, 0.6, ease(t / dur))
    c = base(t, z, sky=sky, cx=600); wall_clock(c, "5:41")
    bird(c, t, chirp=t > 0.6)
    if t > 0.6:
        tag(c, 760, 840, "tweet", t, 0.6, 40); tag(c, 990, 790, "tweet!", t, 1.0, 40)
    chair(c); game_desk(c, sky < 0.5); monitor(c, t, "play")
    turned = t > 1.7
    gamer(c, t, eyes=("half" if not turned else "wide"), mouth="drool" if not turned else "o",
          brows=0.4 if turned else None, look=(1, -0.8) if turned else (1, 0.2), mash=0.4 if not turned else 0,
          bags=True, tilt=-0.08 if turned else 0.12, sweat=turned)
    if turned:
        c.text(X0 + 160, Y0 - 170, "!", 130 * back(seg(t, 1.7, 1.9)), fill=(255, 220, 60), sw=10)
    caption(c); label(c, t, "5:41 AM"); sub(c, t, "wait... the sun???", 1.8)
    return c.out()

def s_alarm(t, dur=3.8):
    z = punch(t, lerp(1.04, 1.12, ease(t / dur)))
    c = base(t, z, sky=1.0, cx=600); wall_clock(c, "7:00")
    chair(c); game_desk(c, False); monitor(c, t, "play", night=False)
    ring = 0.1 < t < 1.6
    alarm(c, t, ring)
    if ring: tag(c, 860, 790, "RING", t, 0.1, 48, fill=(255, 230, 120))
    gamer(c, t, eyes="spiral" if t < 1.6 else "half", mouth="flat" if t < 2.0 else "smile", bags=True,
          mash=0.5, tilt=math.sin(t * 3) * 0.05)
    bubble(c, 400, 780, "ok LAST game", t, 2.0)
    caption(c); label(c, t, "7:00 AM"); sub(c, t, "school in 30 min", 0.6)
    return c.out()

SCENES = [
    ("g1", 3.0, s_start),
    ("g2", 3.2, s_lose),
    ("g3", 3.2, s_win),
    ("g4", 3.4, s_birds),
    ("g5", 3.8, s_alarm),
]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"g1": [1.5], "g2": [1.5], "g3": [1.6], "g4": [2.6], "g5": [3.0]}
        ims = [fn(tt).resize((300, 533)) for name, dur, fn in SCENES for tt in times[name]]
        sheet = Image.new("RGB", (300 * 4, 533 * 2), WHITE)
        for i, im in enumerate(ims[:8]): sheet.paste(im, ((i % 4) * 300, (i // 4) * 533))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: rig.render(name, dur, fn, out)
