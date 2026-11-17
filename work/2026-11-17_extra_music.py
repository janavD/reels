"""Soundtrack v2: lo-fi beat -> tense panic beat -> sad lo-fi outro, plus SFX."""
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 20.0
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(3)

def add(sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= len(L): return
    n = min(len(sig), len(L) - i)
    L[i:i + n] += sig[:n] * gain * (1 - max(0, pan)); R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))

def tt(d): return np.arange(int(SR * d)) / SR
def lp(x, f): b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)
def hp(x, f): b, a = butter(2, f / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, f0, f1): b, a = butter(2, [f0 / (SR / 2), f1 / (SR / 2)], "band"); return lfilter(b, a, x)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)

def rhodes(f, d, amp=0.12):
    t = tt(d); env = np.minimum(1, t * 80) * np.exp(-t * 1.6)
    trem = 1 + 0.15 * np.sin(2 * np.pi * 4.5 * t)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6) + 0.1 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 9)
    return amp * env * trem * s

def bell(f, d=1.2, amp=0.09):
    t = tt(d); env = np.minimum(1, t * 200) * np.exp(-t * 3.5)
    return amp * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 4.01 * f * t) * np.exp(-t * 8))

def kick(amp=0.75):
    t = tt(0.35); f = 45 + 90 * np.exp(-t * 28)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def snare(amp=0.35):
    t = tt(0.25); n = bp(rng.uniform(-1, 1, len(t)), 1200, 6000) * np.exp(-t * 18)
    return amp * (n + 0.4 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25))

def hat(amp=0.12, d=0.05):
    t = tt(d); return amp * hp(rng.uniform(-1, 1, len(t)), 7000) * np.exp(-t * 70)

def bass(f, d, amp=0.28):
    t = tt(d); env = np.minimum(1, t * 60) * np.minimum(1, (d - t) * 30) * np.exp(-t * 1.0)
    return amp * env * (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t))

def saw(f, d, amp=0.2, cut=900):
    t = tt(d); x = 2 * ((f * t) % 1) - 1
    env = np.minimum(1, t * 200) * np.exp(-t * 7)
    return amp * lp(x, cut) * env

def tone(f, d, amp=0.3, dec=4):
    t = tt(d); return amp * np.minimum(1, t * 300) * np.exp(-t * dec) * np.sin(2 * np.pi * f * t)

def noise_sweep(d, f0, f1, amp=0.25):
    n = rng.uniform(-1, 1, int(SR * d)); out = np.zeros_like(n); chunk = 2048
    for i in range(0, len(n), chunk):
        f = f0 + (f1 - f0) * i / len(n); out[i:i + chunk] = bp(n[i:i + chunk], f * 0.7, min(f * 1.3, 20000))
    return amp * out * np.linspace(0.2, 1, len(n))

# ---------- extra reel: fridge every 10 minutes (F major, bouncy, 96 bpm) ----------
import sys
T = 16.0
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
def addm(buf, sig, t):
    i = int(t * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i + n] += sig[:n]

def fridge_open(t):  # rubber seal pop + cold hum
    n = int(SR * 0.08); add(lp(rng.uniform(-1, 1, n), 1800) * np.exp(-tt(0.08) * 50) * 0.5, t, pan=-0.4)
    h = tt(1.2); add(0.05 * np.sin(2 * np.pi * 110 * h) * np.minimum(1, h * 8) * np.exp(-h * 2), t + 0.05, pan=-0.4)
    add(bell(mtof(96), 0.6, 0.05), t + 0.08, pan=-0.4)   # interior light "ting"
def slam(t):
    add(kick(0.9), t); n = int(SR * 0.15); add(lp(rng.uniform(-1, 1, n), 2500) * np.exp(-tt(0.15) * 30) * 0.6, t, pan=-0.3)
def step(t):
    add(tone(140, 0.08, 0.25, dec=40), t, pan=0.3)
def blip(t, f):
    add(tone(f, 0.07, 0.1, dec=20) + tone(f * 1.5, 0.07, 0.04, dec=25), t, pan=-0.3)

bpm = 96; b = 60 / bpm; sw = b * 0.58
chords = [[53, 57, 60, 64], [50, 53, 57, 60], [55, 58, 62, 65], [48, 52, 55, 58]]  # Fmaj7 Dm7 Gm7 C7
roots = [41, 38, 43, 36]
mels = [[72, 74, 77], [76, 74], [74, 70, 72], [70, 67, 69]]
mus = np.zeros(len(L)); bar = 0; t0 = 0.0
while t0 < 16.0:
    ch = chords[bar % 4]
    for st in (0, b * 1.5, b * 3):
        for k, m in enumerate(ch): addm(mus, rhodes(mtof(m), 1.0, 0.07), t0 + st + k * 0.012)
    for beat in range(4):
        tb = t0 + beat * b
        addm(mus, bass(mtof(roots[bar % 4] + (0, 12, 7, 12)[beat]), b * 0.8, 0.24), tb)
        if beat in (0, 2): addm(mus, kick(0.55), tb)
        if beat in (1, 3): addm(mus, snare(0.2), tb)
        addm(mus, hat(0.07), tb); addm(mus, hat(0.045), tb + sw)
    for j, m in enumerate(mels[bar % 4]): addm(mus, bell(mtof(m), 1.0, 0.06), t0 + b * (0.5 + j * 1.1))
    bar += 1; t0 += 4 * b
mus = lp(mus, 4200)
env = np.ones(len(L))
def duck(a, c, lvl):
    i0, i1 = int(a * SR), int(c * SR); env[i0:i1] = lvl
duck(9.4, 10.1, 0.25)    # hush while praying
duck(10.1, 11.6, 0.55)
duck(13.75, 14.65, 0.0)  # silence after slam
mus *= lp(env, 30)
L += mus; R += mus

fridge_open(0.4); fridge_open(3.2); fridge_open(5.75)
for k in range(3): add(tone(mtof(79 + k * 2), 0.12, 0.07, dec=12), 7.0 + k * 0.2)   # "?" pops
add(tone(mtof(67), 0.5, 0.08, dec=5), 7.15)  # lemon. again. sad note
add(tone(mtof(62), 0.7, 0.08, dec=4), 7.4)
# 1:30 hope: shimmer -> open -> choir chord -> sad trombone
add(noise_sweep(1.0, 400, 5000, 0.06), 8.8)
fridge_open(9.6)
for k, m in enumerate((65, 69, 72, 77, 81)): add(bell(mtof(m), 1.2, 0.08), 9.62 + k * 0.03)
for j, m in enumerate((58, 57, 56, 55)):
    d = 0.32 if j < 3 else 0.8
    add(saw(mtof(m), d, 0.16, cut=1100) * (1 + 0.3 * np.sin(2 * np.pi * 6 * tt(d))), 10.15 + j * 0.3)
# lemon talks
for k in range(9): blip(12.05 + k * 0.15, 900 + (k % 3) * 160)
slam(13.75)
for k in range(4): step(13.95 + k * 0.14)
add(tone(mtof(88), 0.15, 0.12, dec=10), 14.45)  # "!"
fridge_open(14.65)
for j, m in enumerate((77, 81, 84)): add(bell(mtof(m), 0.8, 0.08), 14.8 + j * 0.12)

def verb(x):
    y = x.copy()
    for dly, g in ((0.029, 0.3), (0.043, 0.25), (0.067, 0.2), (0.109, 0.15)):
        n = int(dly * SR); y[n:] += x[:-n] * g
    return y
L, R = verb(L), verb(R)
end = np.ones(len(L)); end[-int(SR * 0.4):] = np.linspace(1, 0, int(SR * 0.4))
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.3) * 0.89 * end, np.tanh(R / peak * 1.3) * 0.89 * end
st = np.empty(len(L) * 2); st[0::2] = L; st[1::2] = R
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
