"""Soundtrack v2: lo-fi beat -> tense panic beat -> sad lo-fi outro, plus SFX."""
import sys
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 17.0
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(1630)

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

def addm(buf, sig, t):
    i = int(t * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i + n] += sig[:n]

def pop(t, hi=True):  # message bubble sound
    add(tone(mtof(83 if hi else 76), 0.12, 0.16, dec=18) + tone(mtof(90 if hi else 83), 0.12, 0.08, dec=22), t, pan=0.2)

def vibrate(t, d=0.45):
    tt_ = tt(d); s = 0.22 * np.sin(2 * np.pi * 150 * tt_) * (np.sin(2 * np.pi * 9 * tt_) > -0.2)
    add(lp(s, 900), t, pan=-0.2)

# ---------- section 1: bouncy lo-fi in G, 0 -> 9.2 ----------
bpm = 96; b = 60 / bpm; sw = b * 0.6
chords = [[55, 59, 62, 66], [52, 55, 59, 62], [48, 52, 55, 59], [50, 54, 57, 60]]  # Gmaj7 Em7 Cmaj7 D7
roots = [43, 40, 36, 38]
mels = [[74, 79, 78], [76, 74], [72, 76, 79], [78, 74, 72]]
lofi = np.zeros(len(L)); bar = 0; t0 = 0.0
while t0 < 9.2:
    ch = chords[bar % 4]
    for st in (0, b * 1 + sw, b * 3):
        for k, m in enumerate(ch): addm(lofi, rhodes(mtof(m), 1.2, 0.1), t0 + st + k * 0.01)
    addm(lofi, bass(mtof(roots[bar % 4]), b * 1.4), t0); addm(lofi, bass(mtof(roots[bar % 4] + 12), b * 0.5, 0.2), t0 + b * 1.5)
    addm(lofi, bass(mtof(roots[bar % 4] + 7), b * 1.2), t0 + b * 2.5)
    for beat in range(4):
        tb = t0 + beat * b
        if beat in (0, 2): addm(lofi, kick(), tb)
        if beat == 2: addm(lofi, kick(0.4), tb + sw)
        if beat in (1, 3): addm(lofi, snare(0.3), tb)
        addm(lofi, hat(), tb); addm(lofi, hat(0.07), tb + sw)
    for j, m in enumerate(mels[bar % 4]): addm(lofi, bell(mtof(m)), t0 + b * (0.5 + j * 1.0))
    bar += 1; t0 += 4 * b
lofi = lp(lofi, 4500)
cr = np.zeros(len(L)); idx = rng.integers(0, int(9.2 * SR), 200); cr[idx] = rng.uniform(-0.2, 0.2, 200)
lofi += lp(cr, 5000)
f = np.ones(len(L)); f[int(9.15 * SR):] = 0; lofi *= f
L += lofi; R += lofi

# SFX section 1
vibrate(0.4); pop(0.45, False); pop(1.85)
for i in range(6): add(tone(1000 + (i % 3) * 180, 0.05, 0.05), 3.5 + i * 0.16)    # giggle blips
pop(4.5, False); pop(5.1)
tsw = 6.0
while tsw < 9.15:   # shirt swaps
    add(noise_sweep(0.18, 800, 4000, 0.1), tsw + 0.05, pan=rng.uniform(-0.4, 0.4)); tsw += 0.38
for j, m in enumerate((67, 64, 60)): add(tone(mtof(m), 0.22, 0.12, dec=7), 6.5 + j * 0.85)   # nah / ew / no honk

# ---------- section 2: frantic, 9.2 -> 12.4 ----------
pb = 60 / 150; s16 = pb / 4; i = 0
ost = [40, 40, 52, 40, 43, 40, 51, 40]  # E minor
while 9.2 + i * s16 < 12.35:
    tb = 9.2 + i * s16; k = (tb - 9.2) / 3.2
    add(saw(mtof(ost[i % 8] + int(k * 3)), s16 * 0.9, 0.15, cut=600 + 2200 * k), tb)
    if i % 4 == 0: add(kick(0.8), tb)
    if i % 8 == 4: add(snare(0.36), tb)
    add(hat(0.08, 0.03), tb, pan=0.3)
    i += 1
for _ in range(25): add(lp(rng.uniform(-1, 1, int(SR * 0.08)), 700) * np.exp(-tt(0.08) * 40) * 0.35, rng.uniform(9.4, 12.2), pan=rng.uniform(-0.5, 0.5))  # cushion thumps
pop(9.6, False); pop(10.5)
add(noise_sweep(0.9, 500, 7000, 0.14), 11.5)

# ---------- section 3: triumph -> letdown ----------
for j in range(10):  # key jingle
    add(bell(mtof(96 + (j % 3) * 2), 0.25, 0.05), 12.42 + j * 0.035, pan=-0.3)
win = np.zeros(len(L))
for k2, m in enumerate((55, 59, 62, 67, 71)): addm(win, saw(mtof(m), 1.4, 0.07, cut=2200), 12.45 + k2 * 0.02)
for j, m in enumerate((79, 83, 86)): addm(win, bell(mtof(m), 0.6, 0.1), 12.5 + j * 0.12)
addm(win, kick(0.9), 12.45)
f = np.ones(len(L)); f[int(13.95 * SR):] = 0; win *= f
L += win; R += win
vibrate(13.9)
n = int(SR * 0.4); scr = np.sin(2 * np.pi * np.cumsum(np.linspace(1500, 100, n)) / SR) * rng.uniform(0.5, 1, n)
add(lp(scr, 3500) * np.linspace(0.6, 0, n), 13.95)
pop(14.0, False); pop(14.35, False)
add(tone(2000, 0.02, 0.1, 50), 15.0); add(tone(2000, 0.02, 0.1, 50), 15.5)  # awkward crickets
out = np.zeros(len(L))
for j, (f0, f1) in enumerate(((349, 340), (330, 320), (311, 300), (294, 255))):   # sad trombone
    d = 0.4 if j < 3 else 1.0; t_ = tt(d); fr = np.linspace(f0, f1, len(t_)) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t_))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    sig = sum(np.sin(ph * h) / h ** 1.3 for h in range(1, 7)) * np.minimum(1, t_ * 25) * np.minimum(1, (d - t_) * 12) * 0.14
    addm(out, lp(sig, 1800), 15.85 + j * 0.42)
L += out; R += out

def verb(x):
    y = x.copy()
    for dly, g in ((0.029, 0.3), (0.043, 0.25), (0.067, 0.2), (0.109, 0.15)):
        n = int(dly * SR); y[n:] += x[:-n] * g
    return y
L, R = verb(L), verb(R)
end = np.ones(len(L)); end[-int(SR * 0.3):] = np.linspace(1, 0, int(SR * 0.3))
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.3) * 0.89 * end, np.tanh(R / peak * 1.3) * 0.89 * end
st = np.empty(len(L) * 2); st[0::2] = L; st[1::2] = R
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
