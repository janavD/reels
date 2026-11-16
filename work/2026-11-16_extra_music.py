"""Soundtrack: one chip -> whole bag. bouncy lo-fi -> frenzy -> scratch/silence -> goofy outro."""
import sys
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 16.0
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(1117)

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


def crunch(t, amp=0.35, pan=0.0):
    d = 0.12; n = rng.uniform(-1, 1, int(SR * d)) * (rng.uniform(0, 1, int(SR * d)) > 0.55)
    add(bp(n, 1500, 7000) * np.exp(-tt(d) * 25) * amp, t, pan=pan)

# ---------- section 1: bouncy lo-fi in F, 0 -> 8.4 ----------
bpm = 100; b = 60 / bpm; sw = b * 0.58
chords = [[53, 57, 60, 64], [50, 53, 57, 60], [46, 50, 53, 57], [48, 52, 55, 58]]  # Fmaj7 Dm7 Bbmaj7 C7
roots = [41, 38, 34, 36]
mels = [[77, 81, 84], [81, 77], [74, 77, 81], [79, 76, 72]]
lofi = np.zeros(len(L)); bar = 0; t0 = 0.0
while t0 < 8.4:
    ch = chords[bar % 4]
    for st in (0, b + sw, b * 3):
        for k, m in enumerate(ch): addm(lofi, rhodes(mtof(m), 1.2, 0.1), t0 + st + k * 0.01)
    addm(lofi, bass(mtof(roots[bar % 4]), b * 1.4), t0); addm(lofi, bass(mtof(roots[bar % 4] + 7), b * 1.2), t0 + b * 2.5)
    for beat in range(4):
        tb = t0 + beat * b
        if t0 + beat * b > 1.2:
            if beat in (0, 2): addm(lofi, kick(), tb)
            if beat in (1, 3): addm(lofi, snare(0.28), tb)
            addm(lofi, hat(), tb); addm(lofi, hat(0.07), tb + sw)
    for j, m in enumerate(mels[bar % 4]): addm(lofi, bell(mtof(m)), t0 + b * (0.5 + j * 1.0))
    bar += 1; t0 += 4 * b
lofi = lp(lofi, 4500)
f = np.ones(len(L)); f[int(8.38 * SR):] = 0; lofi *= f
L += lofi; R += lofi

# bag rip + sparkle
add(noise_sweep(0.35, 1500, 6000, 0.18), 0.3)
for j, m in enumerate((84, 88, 91, 96)): add(bell(mtof(m), 0.5, 0.07), 1.6 + j * 0.06, pan=0.3)
for k in range(2): crunch(3.0 + 0.52 + k * 1.3, 0.4)
k = 0
while 5.6 + 0.22 + k * 0.55 < 8.4: crunch(5.6 + 0.22 + k * 0.55, 0.36, pan=0.15); k += 1

# ---------- section 2: frenzy 8.4 -> 11.4, Gm and speeding ----------
pb = 60 / 160; s16 = pb / 4; i = 0
ost = [43, 55, 43, 50, 43, 53, 43, 58]
while 8.4 + i * s16 < 11.4:
    tb = 8.4 + i * s16; kk = (tb - 8.4) / 3.0
    add(saw(mtof(ost[i % 8] + int(kk * 4)), s16 * 0.9, 0.14, cut=700 + 2500 * kk), tb)
    if i % 4 == 0: add(kick(0.8), tb)
    if i % 8 == 4: add(snare(0.36), tb)
    add(hat(0.08, 0.03), tb, pan=0.3)
    i += 1
k = 0
while 8.4 + 0.1 + k * 0.26 < 11.4: crunch(8.4 + 0.1 + k * 0.26, 0.38, pan=rng.uniform(-0.3, 0.3)); k += 1
add(noise_sweep(1.0, 400, 8000, 0.13), 10.4)

# ---------- section 3: empty bag ----------
for j in range(8): add(lp(rng.uniform(-1, 1, int(SR * 0.05)), 2500) * 0.12, 11.5 + j * 0.06)  # rustle
n = int(SR * 0.4); scr = np.sin(2 * np.pi * np.cumsum(np.linspace(1500, 100, n)) / SR) * rng.uniform(0.5, 1, n)
add(lp(scr, 3500) * np.linspace(0.6, 0, n), 12.0)   # record scratch
for j in range(3): add(tone(mtof(88 + j * 3), 0.15, 0.13, dec=10), 12.9 + j * 0.15)  # ? ? !
add(tone(2000, 0.02, 0.1, 50), 13.1); add(tone(2000, 0.02, 0.1, 50), 13.45)          # crickets
add(noise_sweep(0.3, 600, 3000, 0.15), 13.7)
for j in range(30): crunch(13.95 + j * 0.06 + rng.uniform(0, 0.03), 0.18, pan=rng.uniform(-0.2, 0.2))  # crumb pour
out = np.zeros(len(L)); tb = 14.3; pbb = 60 / 120
for j, m in enumerate((41, 45, 48, 53, 48, 41)):  # goofy tuba bounce in F
    d = pbb * 0.45; t_ = tt(d); fr = mtof(m)
    ph = 2 * np.pi * fr * t_
    sig = sum(np.sin(ph * h) / h ** 1.2 for h in range(1, 6)) * np.minimum(1, t_ * 40) * np.exp(-t_ * 4) * 0.2
    addm(out, lp(sig, 1500), tb + j * pbb * 0.5)
    if j % 2 == 0: addm(out, kick(0.5), tb + j * pbb * 0.5)
    if j % 2 == 1: addm(out, snare(0.18), tb + j * pbb * 0.5)
addm(out, bell(mtof(89), 1.0, 0.1), 14.3 + 6 * pbb * 0.5)
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
