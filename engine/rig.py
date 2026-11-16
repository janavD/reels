"""Reel v2: rigged cartoon character, camera moves, detailed sets, lighting."""
import math, random, subprocess, sys, os
from contextlib import contextmanager
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, S = 1080, 1920, 30, 2
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
INK = (22, 20, 24)
SKIN = (255, 238, 196)
WHITE = (255, 255, 255)
_f = {}
def font(sz):
    sz = max(8, int(sz * S))
    if sz not in _f: _f[sz] = ImageFont.truetype(FONT, sz)
    return _f[sz]

# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):  # overshoot pop
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def seg(t, a, b): return clamp((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))

# ---------------- canvas with camera ----------------
_grad = {}
def gradient(top, bot):
    key = (top, bot)
    if key not in _grad:
        y = np.linspace(0, 1, H * S)[:, None, None]
        arr = (np.array(top)[None, None, :] * (1 - y) + np.array(bot)[None, None, :] * y)
        arr = np.repeat(arr, W * S, axis=1).astype(np.uint8)
        _grad[key] = Image.fromarray(arr, "RGB")
    return _grad[key]

class C:
    def __init__(self, top, bot, cam=(540, 1160, 1.0)):
        self.im = gradient(top, bot).copy()
        self.d = ImageDraw.Draw(self.im)
        self.cam = cam
        self.glows = []
    def P(self, x, y):
        cx, cy, z = self.cam
        return ((x - cx) * z + 540) * S, ((y - cy) * z + 1160) * S
    def k(self): return self.cam[2] * S
    def pts(self, pts): return [c for p in pts for c in self.P(*p)]
    def box(self, x0, y0, x1, y1):
        a, b = self.P(x0, y0); c, d = self.P(x1, y1)
        return [min(a, c), min(b, d), max(a, c), max(b, d)]
    @contextmanager
    def ui(self):
        old = self.cam; self.cam = (540, 1160, 1.0)
        try: yield
        finally: self.cam = old
    def rect(self, x0, y0, x1, y1, fill, ol=INK, w=6, r=0):
        b = self.box(x0, y0, x1, y1); wd = int(w * self.k()) if ol else 0
        if r: self.d.rounded_rectangle(b, r * self.k(), fill=fill, outline=ol, width=wd)
        else: self.d.rectangle(b, fill=fill, outline=ol, width=wd)
    def circ(self, x, y, r, fill, ol=INK, w=7):
        self.ell(x - r, y - r, x + r, y + r, fill, ol, w)
    def ell(self, x0, y0, x1, y1, fill, ol=INK, w=6):
        self.d.ellipse(self.box(x0, y0, x1, y1), fill=fill, outline=ol, width=int(w * self.k()) if ol else 0)
    def line(self, pts, w=10, fill=INK, caps=True):
        wd = max(1, int(w * self.k()))
        self.d.line(self.pts(pts), fill=fill, width=wd, joint="curve")
        if caps:
            for p in pts:
                x, y = self.P(*p); r = wd / 2
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
    def arc(self, x0, y0, x1, y1, a0, a1, w=7, fill=INK):
        self.d.arc(self.box(x0, y0, x1, y1), a0, a1, fill=fill, width=max(1, int(w * self.k())))
    def chord(self, x0, y0, x1, y1, a0, a1, fill, ol=INK, w=6):
        self.d.chord(self.box(x0, y0, x1, y1), a0, a1, fill=fill, outline=ol, width=int(w * self.k()) if ol else 0)
    def poly(self, pts, fill, ol=INK, w=6):
        self.d.polygon(self.pts(pts), fill=fill, outline=ol, width=int(w * self.k()) if ol else 0)
    def text(self, x, y, s, sz, fill=WHITE, stroke=INK, sw=8, anchor="mm"):
        k = self.cam[2]
        self.d.text(self.P(x, y), s, font=font(sz * k), fill=fill, stroke_width=int(sw * S * k) if stroke else 0,
                    stroke_fill=stroke, anchor=anchor, align="center")
    def glow(self, x, y, r, col, a):
        X, Y = self.P(x, y); self.glows.append((X / S, Y / S, r * self.cam[2], col, a))
    def out(self):
        im = self.im.reduce(S).convert("RGBA")
        for (x, y, r, col, a) in self.glows:
            g = glow_img(int(r), col, a)
            im.alpha_composite(g, (int(x - r), int(y - r))) if 0 <= x - r and 0 <= y - r and x + r <= W and y + r <= H \
                else _paste_clip(im, g, int(x - r), int(y - r))
        im.alpha_composite(VIGNETTE)
        return im.convert("RGB")

def _paste_clip(im, g, x, y):
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); layer.paste(g, (x, y)); im.alpha_composite(layer)

_gl = {}
def glow_img(r, col, a):
    key = (r, col, a)
    if key not in _gl:
        yy, xx = np.mgrid[-r:r, -r:r]
        d = np.sqrt(xx ** 2 + yy ** 2) / r
        al = (np.clip(1 - d, 0, 1) ** 2 * a * 255).astype(np.uint8)
        arr = np.zeros((2 * r, 2 * r, 4), np.uint8); arr[..., :3] = col; arr[..., 3] = al
        _gl[key] = Image.fromarray(arr, "RGBA")
    return _gl[key]

def make_vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    al = (np.clip(d - 0.55, 0, 1) * 150).astype(np.uint8); al[:400] = 0
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 3] = al
    return Image.fromarray(arr, "RGBA")
VIGNETTE = make_vignette()

# ---------------- rig ----------------
def ik(sx, sy, tx, ty, l1, l2, bend=1):
    dx, dy = tx - sx, ty - sy; d = max(1e-3, math.hypot(dx, dy)); d2 = min(d, l1 + l2 - 1)
    a = math.acos(clamp((l1 * l1 + d2 * d2 - l2 * l2) / (2 * l1 * d2), -1, 1))
    th = math.atan2(dy, dx)
    ex, ey = sx + l1 * math.cos(th + bend * a), sy + l1 * math.sin(th + bend * a)
    return ex, ey

def limb(c, s, t, l1=120, l2=120, bend=1, w=14):
    e = ik(*s, *t, l1, l2, bend); c.line([s, e, t], w=w)
    return e

def hand(c, x, y, r=22, thumb=None):
    if thumb is not None:  # thumb direction angle (radians)
        tx, ty = x + math.cos(thumb) * r * 1.2, y + math.sin(thumb) * r * 1.2
        c.ell(tx - r * 0.45, ty - r * 0.75, tx + r * 0.45, ty + r * 0.75, SKIN, w=5)
    c.circ(x, y, r, SKIN, w=6)

def rot(dx, dy, a): return dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)

def head(c, x, y, r=110, tilt=0.0, eyes="open", mouth="smile", look=(0, 0), blink=0.0, brows=None,
         blush=False, t=0.0, sweat=False, squash=1.0):
    k = r / 110
    def F(dx, dy):
        ox, oy = rot(dx * k, dy * k, tilt); return x + ox, y + oy
    c.ell(x - r * (2 - squash), y - r * squash, x + r * (2 - squash), y + r * squash, SKIN, w=10)
    if blush:
        for sx in (-62, 62):
            px, py = F(sx, 28); c.ell(px - 24 * k, py - 12 * k, px + 24 * k, py + 12 * k, (255, 175, 165), ol=None)
    for side, sx in ((0, -40), (1, 40)):
        ex, ey = F(sx, -14)
        kind = eyes if not isinstance(eyes, tuple) else eyes[side]
        if blink > 0.5 and kind in ("open", "wide"): kind = "closed"
        if kind == "open":
            c.circ(ex + look[0] * 6 * k, ey + look[1] * 6 * k, 11 * k, INK, ol=None)
            c.circ(ex + look[0] * 6 * k + 4 * k, ey + look[1] * 6 * k - 4 * k, 3.5 * k, WHITE, ol=None)
        elif kind == "wide":
            c.circ(ex, ey, 30 * k, WHITE, w=6 * k)
            jit = math.sin(t * 47 + side) * 2.5 * k
            c.circ(ex + look[0] * 12 * k + jit, ey + look[1] * 12 * k, 8 * k, INK, ol=None)
        elif kind == "happy":
            c.arc(ex - 22 * k, ey - 18 * k, ex + 22 * k, ey + 22 * k, 200, 340, w=7 * k)
        elif kind == "closed":
            c.arc(ex - 22 * k, ey - 22 * k, ex + 22 * k, ey + 14 * k, 25, 155, w=7 * k)
        elif kind == "half":
            c.circ(ex + look[0] * 5 * k, ey + 6 * k, 10 * k, INK, ol=None)
            c.line([(ex - 20 * k, ey - 2 * k), (ex + 20 * k, ey - 2 * k)], w=6 * k)
        elif kind == "x":
            c.line([(ex - 16 * k, ey - 16 * k), (ex + 16 * k, ey + 16 * k)], w=7 * k)
            c.line([(ex + 16 * k, ey - 16 * k), (ex - 16 * k, ey + 16 * k)], w=7 * k)
        elif kind == "spiral":
            pts = [(ex + math.cos(a) * a * 2.4 * k, ey + math.sin(a) * a * 2.4 * k) for a in np.linspace(0, 12, 30)]
            c.line(pts, w=4.5 * k, caps=False)
        if brows:
            ang = brows if side == 0 else -brows
            bx, by = F(sx, -58)
            dx, dy = rot(20 * k, 0, ang + tilt)
            c.line([(bx - dx, by - dy), (bx + dx, by + dy)], w=7 * k)
    mx, my = F(0, 34)
    if mouth == "smile":
        c.arc(mx - 42 * k, my - 40 * k, mx + 42 * k, my + 14 * k, 20, 160, w=7 * k)
    elif mouth == "grin":
        c.chord(mx - 44 * k, my - 34 * k, mx + 44 * k, my + 30 * k, 0, 180, INK, w=5 * k)
        c.chord(mx - 22 * k, my + 4 * k, mx + 22 * k, my + 28 * k, 180, 360, (240, 110, 120), ol=None)
    elif mouth == "laugh":
        o = abs(math.sin(t * 22)) * 10 * k
        c.chord(mx - 40 * k, my - 30 * k, mx + 40 * k, my + 30 * k + o, 0, 180, INK, w=5 * k)
        c.chord(mx - 20 * k, my + 6 * k + o * 0.5, mx + 20 * k, my + 28 * k + o, 180, 360, (240, 110, 120), ol=None)
    elif mouth == "o":
        c.ell(mx - 18 * k, my - 10 * k, mx + 18 * k, my + 34 * k, INK, ol=None)
    elif mouth == "scream":
        o = abs(math.sin(t * 30)) * 6 * k
        c.ell(mx - 26 * k, my - 14 * k, mx + 26 * k, my + 50 * k + o, INK, ol=None)
        c.ell(mx - 14 * k, my + 24 * k, mx + 14 * k, my + 46 * k + o, (240, 110, 120), ol=None)
    elif mouth == "grit":
        c.rect(mx - 38 * k, my - 6 * k, mx + 38 * k, my + 26 * k, WHITE, w=5 * k, r=6 * k)
        for dx in (-19, 0, 19): c.line([(mx + dx * k, my - 6 * k), (mx + dx * k, my + 26 * k)], w=3 * k, caps=False)
        c.line([(mx - 38 * k, my + 10 * k), (mx + 38 * k, my + 10 * k)], w=3 * k, caps=False)
    elif mouth == "frown":
        c.arc(mx - 34 * k, my + 4 * k, mx + 34 * k, my + 50 * k, 200, 340, w=7 * k)
    elif mouth == "flat":
        c.line([(mx - 22 * k, my + 10 * k), (mx + 22 * k, my + 10 * k)], w=7 * k)
    elif mouth == "dead":
        c.arc(mx - 34 * k, my + 4 * k, mx + 34 * k, my + 44 * k, 200, 340, w=7 * k)
        c.chord(mx + 2 * k, my + 4 * k, mx + 30 * k, my + 44 * k, 0, 180, (240, 110, 120), w=5 * k)
    elif mouth == "drool":
        c.arc(mx - 26 * k, my - 10 * k, mx + 26 * k, my + 20 * k, 20, 160, w=6 * k)
        px, py = F(22, 44); c.ell(px - 7 * k, py - 4 * k, px + 7 * k, py + 18 * k, (150, 210, 255), w=3 * k)
    if sweat:
        for i, (sx, sy) in enumerate([(-100, -60), (98, -40), (-92, 10)]):
            ph = (t * 1.6 + i * 0.37) % 1
            px, py = F(sx, sy); py += ph * 60 * k
            if ph < 0.85:
                rr = 13 * k
                c.poly([(px, py - rr * 2.2), (px - rr * 0.95, py - rr * 0.2), (px + rr * 0.95, py - rr * 0.2)], (120, 195, 255), ol=None)
                c.circ(px, py, rr, (120, 195, 255), ol=INK, w=3 * k)

# ---------------- sets ----------------
WALL_DAY = ((236, 222, 200), (214, 196, 170))
WALL_NIGHT = ((88, 92, 128), (60, 62, 92))
def floor(c, night):
    base = (178, 128, 86) if not night else (92, 72, 70)
    c.rect(-600, 1640, 1700, 2600, base, ol=None)
    c.line([(-600, 1640), (1700, 1640)], w=8)
    for x in range(-600, 1700, 150):
        c.line([(x, 1640), (x - 90, 2600)], w=4, fill=mix(base, (0, 0, 0), 0.2), caps=False)
    c.rect(-600, 1600, 1700, 1640, mix(base, WHITE, 0.4), w=5)  # baseboard

def window(c, night, t=0):
    c.rect(625, 505, 1015, 915, (240, 240, 235), w=8)
    sky_top, sky_bot = ((120, 185, 240), (190, 225, 250)) if not night else ((18, 22, 52), (40, 46, 92))
    for i in range(8):
        c.rect(645, 525 + i * 46, 995, 525 + (i + 1) * 46 + 1, mix(sky_top, sky_bot, i / 7), ol=None)
    if night:
        c.circ(915, 600, 34, (250, 246, 215), ol=None)
        c.circ(930, 590, 30, mix(sky_top, sky_bot, 0.15), ol=None)  # crescent
        for i, (sx, sy) in enumerate([(690, 580), (760, 660), (850, 760), (965, 700), (700, 830), (800, 560)]):
            tw = 4 + 2.5 * math.sin(t * 5 + i * 2)
            c.circ(sx, sy, tw, (255, 255, 225), ol=None)
        # city lights silhouette
        c.poly([(645, 895), (645, 820), (700, 820), (700, 790), (760, 790), (760, 840), (830, 840), (830, 770),
                (880, 770), (880, 830), (995, 830), (995, 895)], (24, 26, 44), ol=None)
        for (wx, wy) in [(660, 840), (720, 805), (845, 790), (900, 850), (950, 860), (780, 860)]:
            c.rect(wx, wy, wx + 14, wy + 14, (255, 214, 120), ol=None)
    else:
        dx = (t * 12) % 400
        for (cx0, cy0) in [(690 + dx, 620), (880 + dx - 400 if 880 + dx > 1000 else 880 + dx, 700)]:
            if 650 < cx0 < 990:
                c.ell(cx0 - 50, cy0 - 18, cx0 + 50, cy0 + 18, WHITE, ol=None)
                c.ell(cx0 - 25, cy0 - 38, cx0 + 30, cy0 + 6, WHITE, ol=None)
        c.poly([(645, 895), (645, 840), (760, 800), (880, 840), (995, 810), (995, 895)], (120, 170, 110), ol=None)
    c.line([(820, 525), (820, 895)], w=10); c.line([(645, 710), (995, 710)], w=10)
    c.rect(605, 905, 1035, 935, (245, 245, 240), w=6)  # sill
    cur = (78, 118, 178) if not night else (52, 66, 110)
    for (x0, x1) in ((585, 660), (980, 1055)):
        c.rect(x0, 480, x1, 990, cur, w=6)
        for fx in (x0 + 25, x0 + 50): c.line([(fx, 500), (fx, 975)], w=3, fill=mix(cur, (0, 0, 0), 0.3), caps=False)
    c.line([(560, 482), (1080, 482)], w=12)

def shelf(c, night):
    dim = 0.35 if night else 0
    c.rect(70, 860, 360, 885, mix((170, 110, 60), (0, 0, 0), dim), w=6)
    cols = [(220, 80, 80), (80, 140, 220), (240, 190, 70), (110, 180, 120), (170, 110, 200)]
    x = 90
    for i, col in enumerate(cols):
        h = [110, 90, 120, 100, 80][i]; wdt = [36, 30, 40, 34, 30][i]
        c.rect(x, 860 - h, x + wdt, 860, mix(col, (0, 0, 0), dim), w=5)
        x += wdt + 4
    c.rect(290, 790, 350, 860, mix((230, 230, 230), (0, 0, 0), dim), w=5, r=8)   # pot
    for a in (-0.6, -0.2, 0.25, 0.6):
        c.line([(320, 790), (320 + math.sin(a) * 70, 790 - math.cos(a) * 80)], w=12, fill=mix((90, 170, 90), (0, 0, 0), dim))

def calendar(c, txt, red=False, shake=0.0):
    ox = shake
    c.rect(400 + ox, 560, 570 + ox, 760, WHITE, w=6, r=12)
    c.rect(400 + ox, 560, 570 + ox, 615, (225, 70, 70), w=6, r=12)
    c.text(485 + ox, 588, "DUE IN", 25, fill=WHITE, stroke=None)
    c.text(485 + ox, 676, txt, 62, fill=(225, 60, 60) if red else INK, stroke=None)
    c.text(485 + ox, 734, "days" if txt != "1" else "day", 24, fill=INK, stroke=None)
    c.circ(485 + ox, 552, 8, (200, 200, 200), w=4)

def room(c, night, t, cal="7", red=False):
    window(c, night, t); shelf(c, night)
    if cal: calendar(c, cal, red)
    floor(c, night)

def bed(c, night):
    wood = (176, 114, 64) if not night else (112, 76, 56)
    c.rect(150, 1170, 590, 1340, wood, w=7, r=50)
    c.rect(150, 1170, 200, 1650, mix(wood, (0, 0, 0), 0.15), w=7, r=10)
    c.rect(150, 1390, 1010, 1570, wood, w=7)
    c.rect(950, 1290, 1010, 1650, mix(wood, (0, 0, 0), 0.15), w=7, r=10)
    c.rect(170, 1300, 990, 1420, (240, 240, 245) if not night else (170, 172, 196), w=7, r=22)
    c.ell(190, 1215, 450, 1350, (172, 210, 205) if not night else (110, 140, 150), w=7)

def blanket(c, night, kick=0.0, breathe=0.0):
    col = (82, 118, 185) if not night else (58, 76, 132)
    top = 1270 - breathe
    c.poly([(400, top + 30), (540, top - 4), (700, top + 6 + kick * 0.3), (860, top - 6 - kick),
            (990, top + 12), (1010, 1450), (380, 1460)], col, w=7)
    shade = mix(col, (0, 0, 0), 0.28)
    c.line([(560, 1320), (690, 1400)], w=5, fill=shade); c.line([(780, 1310 - kick * 0.5), (880, 1395)], w=5, fill=shade)
    c.line([(470, 1300), (520, 1380)], w=5, fill=shade)

def nightstand(c, night):
    wood = (176, 114, 64) if not night else (112, 76, 56)
    c.rect(-40, 1430, 140, 1640, wood, w=7)
    c.line([(-40, 1530), (140, 1530)], w=5); c.circ(60, 1490, 8, INK, ol=None); c.circ(60, 1585, 8, INK, ol=None)

def desk(c, night):
    wood = (166, 108, 62) if not night else (118, 80, 58)
    c.rect(-60, 1385, 1140, 1450, wood, w=8)
    c.rect(-60, 1450, 1140, 1462, mix(wood, (0, 0, 0), 0.35), ol=None)
    for x0 in (40, 900):
        c.rect(x0, 1450, x0 + 150, 1700, mix(wood, (0, 0, 0), 0.12), w=7)
        c.line([(x0, 1575), (x0 + 150, 1575)], w=5); c.line([(x0 + 55, 1515), (x0 + 95, 1515)], w=8)
        c.line([(x0 + 55, 1635), (x0 + 95, 1635)], w=8)

def laptop_back(c, open_k=1.0, glow=True):
    top = lerp(1380, 1150, open_k)
    c.poly([(330, 1388), (750, 1388), (725, top), (355, top)], (196, 200, 212), w=8)
    c.circ(540, (1388 + top) / 2, 22 * open_k + 0.1, (245, 245, 250), w=4)
    if glow: c.glow(540, top + 40, 380, (150, 200, 255), 0.33)

def lamp(c, x, y, on):
    c.poly([(x - 70, y - 120), (x + 70, y - 120), (x + 45, y - 210), (x - 45, y - 210)], (250, 210, 110) if on else (220, 200, 150), w=6)
    c.line([(x, y - 120), (x, y)], w=10); c.ell(x - 60, y - 14, x + 60, y + 10, (80, 80, 90), w=6)
    if on: c.glow(x, y - 150, 330, (255, 210, 120), 0.42)

# ---------------- UI text ----------------
CAP = ["me: \"i'll start the", "assignment early", "this time\""]
def caption(c):
    with c.ui():
        c.rect(-10, -10, 1090, 400, WHITE, ol=None)
        for i, s in enumerate(CAP): c.text(540, 150 + i * 92, s, 68, fill=INK, stroke=None)

def label(c, t, s, y=1650, sz=88):
    y = 1650
    k = back(seg(t, 0.05, 0.35))
    if k <= 0.01: return
    with c.ui(): c.text(540, y, s, sz * k, sw=10)

def sub(c, t, s, start=0.5):
    k = back(seg(t, start, start + 0.3))
    if k <= 0.01: return
    with c.ui(): c.text(540, 1772, s, 60 * k, sw=8)

def bubble(c, x, y, s, t, start):
    k = back(seg(t, start, start + 0.3))
    if k <= 0.01: return
    w = 330 * k; h = 120 * k
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, WHITE, w=6, r=40 * k)
    c.poly([(x - 30 * k, y + h / 2 - 3), (x + 10 * k, y + h / 2 - 3), (x - 50 * k, y + h / 2 + 50 * k)], WHITE, ol=None)
    c.line([(x - 30 * k, y + h / 2), (x - 50 * k, y + h / 2 + 50 * k), (x + 10 * k, y + h / 2)], w=6)
    c.text(x, y, s, 42 * k, fill=INK, stroke=None)

def punch(t, z=1.0, amt=0.07):  # camera punch-in at scene start
    return z + amt * (1 - eout(seg(t, 0, 0.35)))

def blinkf(t, every=2.7, off=0.0):
    ph = (t + off) % every
    return 1.0 if ph < 0.12 else 0.0

# ---------------- scenes ----------------
def s_day1(t):
    z = punch(t, lerp(1.0, 1.12, ease(t / 3.0)))
    c = C(*WALL_DAY, cam=(540, 1180, z)); room(c, False, t, "7")
    desk_x = 760
    # small desk on the right with closed laptop + books
    c.rect(700, 1390, 1100, 1430, (166, 108, 62), w=7); c.rect(720, 1430, 760, 1640, (150, 96, 56), w=6)
    c.rect(1040, 1430, 1080, 1640, (150, 96, 56), w=6)
    c.rect(760, 1360, 980, 1390, (190, 196, 210), w=6, r=6)
    c.rect(1000, 1300, 1070, 1390, (220, 80, 80), w=5); c.rect(1005, 1250, 1065, 1300, (80, 140, 220), w=5)
    # character
    bob = math.sin(t * 2 * math.pi * 85 / 60) * 6
    x, y = 420, 1050 + bob
    hip = (x, y + 360)
    c.ell(x - 140, 1625, x + 140, 1655, mix((178, 128, 86), (0, 0, 0), 0.25), ol=None)
    limb(c, hip, (x - 60, 1630), 118, 118, bend=-1); limb(c, hip, (x + 60, 1630), 118, 118, bend=1)
    c.line([(x - 60, 1630), (x - 100, 1632)], w=14); c.line([(x + 60, 1630), (x + 100, 1632)], w=14)
    c.line([(x, y + 105), hip], w=14)
    sh = (x, y + 170)
    # left hand on hip
    limb(c, sh, (x - 40, y + 330), 115, 115, bend=1); hand(c, x - 40, y + 330, 20)
    # right arm: hip -> thumbs up
    k = back(seg(t, 0.75, 1.15))
    tx, ty = lerp(x + 40, x + 175, k), lerp(y + 330, y + 120, k)
    limb(c, sh, (tx, ty), 115, 115, bend=-1)
    hand(c, tx, ty, 26, thumb=-math.pi / 2 if k > 0.5 else None)
    tilt = 0.12 * ease(seg(t, 0.8, 1.2)) + math.sin(t * 5) * 0.03
    wink = 1.2 < t < 2.4
    head(c, x, y, 110, tilt=tilt, eyes=("open", "happy") if wink else "open", mouth="grin" if t > 0.9 else "smile",
         blink=blinkf(t, 2.6, 0.5) if not wink else 0, brows=-0.25 if t > 0.9 else None, t=t)
    if wink:  # sparkle
        sp = 1 - seg(t, 1.25, 1.7)
        if sp > 0:
            for a in range(4):
                ang = a * math.pi / 2 + t * 4
                c.line([(x + 150 + math.cos(ang) * 10, y - 80 + math.sin(ang) * 10),
                        (x + 150 + math.cos(ang) * 36 * sp, y - 80 + math.sin(ang) * 36 * sp)], w=6, fill=(255, 200, 40))
    bubble(c, x + 230, y - 210, "easy. i got this", t, 1.3)
    caption(c); label(c, t, "Day 1", 1775)
    return c.out()

def lying(c, t, night, phone_xy, eyes, mouth, kick=0.0, tilt=0.0, blink=0.0, blush=False, phone_glow=False,
          arms=True, thumb_scroll=True, look=(0, -1), brows=None, sweat=False, phone_on_face=False):
    bed(c, night)
    hx, hy = 315, 1235
    if phone_on_face:
        head(c, hx, hy, 105, tilt=tilt, eyes=eyes, mouth=mouth, t=t)
    else:
        head(c, hx, hy, 105, tilt=tilt, eyes=eyes, mouth=mouth, look=look, blink=blink, blush=blush, t=t, brows=brows, sweat=sweat)
    blanket(c, night, kick=kick)
    px, py = phone_xy
    if arms:
        sh = (430, 1330)
        e1 = ik(*sh, px - 30, py + 40, 120, 120, -1); c.line([sh, e1, (px - 30, py + 40)], w=14)
    # phone
    if phone_on_face:
        c.rect(hx - 70, hy - 45, hx + 70, hy + 45, (34, 34, 40), w=6, r=16)
    else:
        c.rect(px - 45, py - 80, px + 45, py + 80, (34, 34, 40), w=6, r=14)
        c.rect(px - 36, py - 68, px + 36, py + 68, (150, 205, 255), ol=None, r=8)
        # fake feed on screen
        sc = (t * 260) % 60 if thumb_scroll else 0
        for i in range(-1, 4):
            yy = py - 60 + i * 40 - sc
            if py - 66 < yy < py + 40:
                c.rect(px - 28, yy, px + 28, yy + 26, (255, 255, 255), ol=None, r=4)
        if phone_glow: c.glow(px, py, 260, (160, 210, 255), 0.35)
    if arms:
        sh2 = (470, 1335)
        tt = (px + 20, py + 50 - (abs(math.sin(t * 9)) * 16 if thumb_scroll else 0))
        e2 = ik(*sh2, *tt, 125, 125, -1); c.line([sh2, e2, tt], w=14)
        hand(c, px - 30, py + 40, 21); hand(c, *tt, 21)

def s_6days(t):
    z = punch(t, lerp(1.05, 1.16, ease(t / 2.8)))
    c = C(*WALL_DAY, cam=(470, 1180, z)); room(c, False, t, "6")
    sway = math.sin(t * 3) * 10
    lying(c, t, False, (430 + sway, 1060), eyes="happy", mouth="laugh", kick=abs(math.sin(t * 14)) * 30,
          tilt=math.sin(t * 20) * 0.08, blush=True)
    for i in range(3):
        ph = (t * 1.3 + i / 3) % 1
        a = 1 - ph
        if t > 0.3:
            c.text(160 - i * 20 + ph * 40, 1100 - ph * 200, "haha", 46 + 10 * a, fill=WHITE, sw=6)
    caption(c); label(c, t, "6 days left", 1000 + 0); sub(c, t, "plenty of time")
    return c.out()

def s_3days(t):
    z = punch(t, lerp(1.08, 1.22, ease(t / 2.6)))
    c = C(*WALL_DAY, cam=(440, 1190, z)); room(c, False, t, "3")
    drop = 1.45
    if t < drop:
        droop = ease(seg(t, 0.3, drop)) * 60
        lying(c, t, False, (430, 1060 + droop), eyes="half", mouth="smile", look=(0, -1),
              tilt=math.sin(t * 2) * 0.05, thumb_scroll=t < 0.9)
    elif t < drop + 0.12:
        f = seg(t, drop, drop + 0.12)
        lying(c, t, False, (lerp(430, 315, f), lerp(1120, 1235, f)), eyes="wide", mouth="o", arms=False, thumb_scroll=False)
        for (ax, ay, bx, by) in ((380, 1310, 520, 1280), (470, 1330, 600, 1290)): c.line([(ax, ay), (bx, by)], w=14)
    else:
        lying(c, t, False, (315, 1235), eyes="x", mouth="o", arms=False, phone_on_face=True)
        for (ax, ay, bx, by) in ((430, 1330, 560, 1260), (470, 1335, 620, 1300)): c.line([(ax, ay), (bx, by)], w=14)
        # bonk stars
        tt = t - drop
        for i in range(4):
            a = tt * 6 + i * math.pi / 2
            sx, sy = 315 + math.cos(a) * 140, 1130 + math.sin(a) * 40
            star(c, sx, sy, 20)
        if tt < 0.35:
            with c.ui(): c.text(330, 1000, "BONK", 90 * back(tt / 0.2), fill=(255, 220, 60), sw=10)
    caption(c); label(c, t, "3 days left", 1000); sub(c, t, "tomorrow for sure", 0.4)
    return c.out()

def star(c, x, y, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    c.poly(pts, (255, 215, 60), w=4)

def s_1day(t):
    z = punch(t, lerp(1.05, 1.15, ease(t / 2.8)))
    c = C(*WALL_NIGHT, cam=(380, 1220, z)); room(c, True, t, "1", red=True)
    nightstand(c, True)
    ring = 0.5 < t < 1.55
    slap = seg(t, 1.25, 1.5)
    # alarm clock
    jx = math.sin(t * 90) * 7 if ring else 0
    squash = 1 - 0.35 * (1 - seg(t, 1.5, 1.8)) if t > 1.5 else 1
    cx0, cy0 = 60 + jx, 1430
    h = 90 * squash
    c.circ(cx0 - 38, cy0 - h - 12, 18, (230, 60, 60), w=5); c.circ(cx0 + 38, cy0 - h - 12, 18, (230, 60, 60), w=5)
    c.rect(cx0 - 55, cy0 - h, cx0 + 55, cy0, (230, 60, 60), w=6, r=20)
    c.rect(cx0 - 40, cy0 - h + 14, cx0 + 40, cy0 - 14, (25, 25, 30), w=4, r=6)
    c.text(cx0, cy0 - h / 2, "7:00", 26 * squash, fill=(255, 80, 80), stroke=None)
    if ring:
        for i in range(3):
            r0 = 70 + i * 22 + (t * 200) % 22
            c.arc(cx0 - r0, cy0 - 50 - r0, cx0 + r0, cy0 - 50 + r0, 200, 250, w=5, fill=(255, 230, 120))
            c.arc(cx0 - r0, cy0 - 50 - r0, cx0 + r0, cy0 - 50 + r0, 290, 340, w=5, fill=(255, 230, 120))
        c.glow(cx0, cy0 - 50, 200, (255, 120, 100), 0.25 * (0.5 + 0.5 * math.sin(t * 40)))
    breathe = math.sin(t * 2.2) * 8
    bed(c, True)
    annoyed = 0.5 < t < 1.6
    head(c, 315, 1235 + breathe * 0.3, 105, tilt=-0.15, eyes="closed", mouth="frown" if annoyed else "drool",
         brows=0.35 if annoyed else None, t=t)
    blanket(c, True, breathe=breathe)
    # arm swings out to slap the clock
    if 1.0 < t < 2.2:
        out_k = ease(seg(t, 1.0, 1.25)) * (1 - ease(seg(t, 1.8, 2.2)))
        sh = (420, 1300)
        tx = lerp(430, cx0, out_k); ty = lerp(1290, cy0 - h - 20 + slap * 40, out_k)
        e = ik(*sh, tx, ty, 130, 130, 1); c.line([sh, e, (tx, ty)], w=14); hand(c, tx, ty, 24)
        if 1.45 < t < 1.7:
            for a in (-2.4, -1.9, -1.2):
                c.line([(cx0 + math.cos(a) * 80, cy0 - 60 + math.sin(a) * 80), (cx0 + math.cos(a) * 125, cy0 - 60 + math.sin(a) * 125)], w=7, fill=WHITE)
    for i in range(3):
        ph = (t * 0.7 + i / 3) % 1
        if not annoyed:
            c.text(430 + ph * 120 + i * 8, 1130 - ph * 220, "z", 46 + ph * 46, fill=WHITE, sw=6)
    caption(c); label(c, t, "1 day left", 960); sub(c, t, "i'll wake up early", 0.35)
    return c.out()

PAPERS = [(random.Random(i).uniform(150, 930), random.Random(i + 9).uniform(-1, 1), random.Random(i + 3).uniform(0.3, 1.0)) for i in range(7)]

def s_panic(t, dur=5.0):
    rnd = random.Random(int(t * FPS))
    z = lerp(1.0, 1.28, ease(t / dur))
    shake = 4 + 10 * (t / dur)
    cam = (540 + rnd.uniform(-shake, shake), 1150 + rnd.uniform(-shake, shake) - 60 * ease(t / dur), z)
    c = C(*WALL_NIGHT, cam=cam); room(c, True, t, None)
    # chair back
    c.rect(400, 1080, 680, 1300, (70, 70, 80), w=7, r=30)
    x, y = 540, 1070
    bob = abs(math.sin(t * 16)) * 10
    hx, hy = x + math.sin(t * 7) * 12, y + bob
    sh = (x, y + 180)
    c.line([(x, y + 100), (x, y + 330)], w=14)
    look = (1, -0.3) if (t % 1.2) < 0.35 else (0, 0.6)
    head(c, hx, hy, 118, tilt=math.sin(t * 9) * 0.07, eyes="wide", mouth="grit" if (t % 1.0) < 0.6 else "scream",
         look=look, brows=0.45, t=t, sweat=True)
    desk(c, True); lamp(c, 990, 1385, True)
    for cx0 in (790, 860):
        c.rect(cx0 - 30, 1265, cx0 + 30, 1388, (70, 205, 100), w=6, r=8); c.line([(cx0 - 30, 1300), (cx0 + 30, 1300)], w=4)
    laptop_back(c)
    for side in (-1, 1):
        ph = t * 34 + (0 if side < 0 else math.pi)
        tx = x + side * (150 + 20 * math.sin(ph * 0.37))
        ty = 1385 - abs(math.sin(ph)) * 34
        e = ik(x + side * 30, y + 180, tx, ty, 120, 120, side)
        c.line([(x + side * 10, y + 170), e, (tx, ty)], w=14)
        hand(c, tx, ty, 22)
        if abs(math.sin(ph)) < 0.25:
            c.line([(tx - 20, ty + 30), (tx - 34, ty + 46)], w=5, fill=WHITE); c.line([(tx + 20, ty + 30), (tx + 34, ty + 46)], w=5, fill=WHITE)
    # flying papers
    for i, (px0, vx, sp) in enumerate(PAPERS):
        ph = (t * sp + i * 0.21) % 1
        px = px0 + vx * 200 * ph; py = 1380 - 600 * ph + 500 * ph * ph
        a = ph * 6 * vx
        pts = [(px + rot(dx, dy, a)[0], py + rot(dx, dy, a)[1]) for dx, dy in ((-40, -50), (40, -50), (40, 50), (-40, 50))]
        c.poly(pts, (250, 250, 245), w=4)
        c.line([(px + rot(-25, -20, a)[0], py + rot(-25, -20, a)[1]), (px + rot(25, -20, a)[0], py + rot(25, -20, a)[1])], w=3, caps=False)
    caption(c)
    mins = 47 + min(11, int(t / dur * 12))
    tick = (t / dur * 12) % 1
    pop = 1 + 0.18 * (1 - eout(tick / 0.3)) if tick < 0.3 else 1
    red = (255, 70, 70) if (t * 4) % 1 < 0.55 else WHITE
    with c.ui():
        c.text(540, 590, f"11:{mins:02d} PM", 120 * pop, fill=red, sw=12)
        c.text(540, 715, "due at 11:59", 56, sw=8)
    return c.out()

def s_submit(t):
    hit = 0.55
    zk = ease(seg(t, 0, hit)) * (1 - ease(seg(t, hit, hit + 0.25))) + 0.0
    cam = (540, lerp(1150, 1300, zk), lerp(1.0, 1.3, zk))
    if hit < t < hit + 0.15: cam = (cam[0] + random.Random(int(t * 99)).uniform(-14, 14), cam[1], cam[2])
    c = C(*WALL_NIGHT, cam=cam); room(c, True, t, None)
    melt = ease(seg(t, 1.0, 1.7))
    x, y = 540 - 270 * melt, 1070 + 120 * melt
    c.rect(400, 1080, 680, 1300, (70, 70, 80), w=7, r=30)
    c.line([(x, y + 100), (x, y + 330)], w=14)
    if t < 1.0:
        eyes, mouth = ("wide", "grit") if t < hit else ("wide", "o")
    else:
        eyes, mouth = "x", "dead"
    head(c, x, y, 118, tilt=-0.45 * melt, eyes=eyes, mouth=mouth, look=(0, 0.8), t=t, brows=0.45 if t < hit else None,
         squash=1 - 0.06 * melt)
    desk(c, True); lamp(c, 990, 1385, True)
    for cx0 in (790, 860):
        c.rect(cx0 - 30, 1265, cx0 + 30, 1388, (70, 205, 100), w=6, r=8)
    laptop_back(c)
    flash = 1 - seg(t, hit, hit + 0.3)
    if t > hit and flash > 0: c.glow(540, 1200, 600, (255, 255, 255), 0.6 * flash)
    # left arm resting, right arm: raise finger then slam
    if t < 1.0:
        c.line([(x - 10, y + 170), (x - 150, y + 260), (x - 170, 1385)], w=14); hand(c, x - 170, 1385, 22)
        up = ease(seg(t, 0.0, 0.35)); down = eout(seg(t, 0.42, hit))
        tx = x + 160; ty = lerp(lerp(1385, 900, up), 1385, down)
        e = ik(x + 10, y + 170, tx, ty, 130, 130, 1); c.line([(x + 10, y + 170), e, (tx, ty)], w=14)
        hand(c, tx, ty, 22)
        c.ell(tx - 7, ty - 52, tx + 7, ty - 12, SKIN, w=5)  # pointing finger
        if t > hit:
            for a in (-2.6, -2.0, -1.1, -0.5):
                c.line([(tx + math.cos(a) * 50, ty + math.sin(a) * 50), (tx + math.cos(a) * 100, ty + math.sin(a) * 100)], w=7, fill=WHITE)
    else:  # arms dangling
        for side in (-1, 1):
            c.line([(x + side * 10, y + 170), (x + side * 180, 1395)], w=14); hand(c, x + side * 180, 1395, 22)
    # soul floating out
    if t > 1.35:
        st = t - 1.35
        sx, sy = x + math.sin(st * 4) * 40, y - 140 - st * 260
        c.ell(sx - 70, sy - 80, sx + 70, sy + 80, (235, 240, 255), ol=(120, 130, 170), w=5)
        c.poly([(sx - 70, sy + 10), (sx + 70, sy + 10), (sx + 30 + math.sin(st * 9) * 15, sy + 160), (sx - 10, sy + 110)], (235, 240, 255), ol=None)
        c.line([(sx - 70, sy + 10), (sx - 10, sy + 110), (sx + 30 + math.sin(st * 9) * 15, sy + 160), (sx + 70, sy + 10)], w=5, fill=(120, 130, 170))
        c.arc(sx - 30, sy - 30, sx - 6, sy - 6, 200, 340, w=5); c.arc(sx + 6, sy - 30, sx + 30, sy - 6, 200, 340, w=5)
        c.arc(sx - 16, sy, sx + 16, sy + 26, 20, 160, w=5)
        c.glow(sx, sy, 180, (220, 230, 255), 0.35)
    caption(c)
    with c.ui():
        c.text(540, 590, "11:59 PM", 120, sw=12)
        k = back(seg(t, hit + 0.02, hit + 0.32))
        if k > 0.01:
            c.rect(540 - 320 * k, 720 - 60 * k, 540 + 320 * k, 720 + 60 * k, (55, 190, 100), w=8, r=34 * k)
            c.text(540, 720, "SUBMITTED", 64 * k, stroke=None)
    sub(c, t, "every. single. time.", 1.5)
    return c.out()

SCENES = [
    ("s1", 3.0, s_day1),
    ("s2", 2.8, s_6days),
    ("s3", 2.6, s_3days),
    ("s4", 2.8, s_1day),
    ("s5", 5.0, s_panic),
    ("s6", 3.8, s_submit),
]

def render(name, dur, fn, outdir):
    tmp, final = f"{outdir}/{name}.tmp.mp4", f"{outdir}/{name}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                          "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, final)

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    if mode == "stills":
        times = {"s1": [0.5, 1.6], "s2": [1.4], "s3": [1.0, 1.7], "s4": [0.9, 1.45], "s5": [2.5, 4.6], "s6": [0.4, 0.8, 2.6]}
        ims = []
        for name, dur, fn in SCENES:
            for tt in times[name]: ims.append(fn(tt).resize((270, 480)))
        sheet = Image.new("RGB", (270 * 6, 480 * 2), WHITE)
        for i, im in enumerate(ims): sheet.paste(im, ((i % 6) * 270, (i // 6) * 480))
        sheet.save(f"{out}/sheet.png")
    else:
        only = sys.argv[3:] or [s[0] for s in SCENES]
        for name, dur, fn in SCENES:
            if name in only: render(name, dur, fn, out)
