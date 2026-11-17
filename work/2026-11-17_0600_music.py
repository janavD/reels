"""Soundtrack: sleepy music box -> hype bouncy A-major -> tape-stop drowsy -> lofi snore -> crickets (i'll just stay up)."""
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 19.8
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(505)

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
def pluck(f, d=0.3, amp=0.12):
    t = tt(d); return amp * np.exp(-t * 14) * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))

mus = np.zeros(len(L))
# a1 (0-3.2) + a6 (16.2-19.8): sleepy music box in E, clock tick
box = [76, 71, 68, 71, 73, 71, 68, 64]
for t0, t1 in ((0.0, 3.2), (16.2, 19.8)):
    i = 0; tb = t0 + 0.05

mus = np.zeros(len(L))
# 0-12.9: sneaky tiptoe pizzicato in D minor, 104 bpm, staccato bass + plucks
b = 60 / 104
walk = [50, 53, 57, 53, 50, 52, 53, 55, 57, 55, 53, 52, 50, 49, 50, 45]
top = [74, 0, 77, 0, 76, 0, 74, 73, 74, 0, 81, 0, 79, 77, 76, 0]
t0 = 0.0; n = 0
while t0 < 12.85:
    addm(mus, pluck(mtof(walk[n % 16] - 12), 0.25, 0.22), t0)
    if top[n % 16]: addm(mus, pluck(mtof(top[n % 16]), 0.2, 0.08), t0 + 0.02)
    if n % 4 == 0: addm(mus, kick(0.25), t0)
    if n % 4 == 2: addm(mus, hat(0.05, 0.03), t0)
    n += 1; t0 += b / 2
# 13.0-15.8: deadpan lofi after reveal
t0 = 13.1
for k2, m in enumerate([50, 53, 57, 60]): addm(mus, rhodes(mtof(m), 2.6, 0.07), t0 + k2 * 0.02)
for k in range(5):
    addm(mus, hat(0.04), t0 + k * 0.55)
mus = lp(mus, 5000)
L += mus; R += mus

# SFX
def creak(d=0.55, f0=180, f1=120):
    t = tt(d); f = np.interp(t, [0, d], [f0, f1]) * (1 + 0.15 * np.sin(2 * np.pi * 23 * t))
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.5 + 0.5 * np.sin(2 * np.pi * 37 * t))
    return 0.22 * bp(s, 300, 3000) * np.sin(np.pi * t / d)
add(creak(), 1.5)
def clang(amp=0.35):
    t = tt(0.9); s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dc) for f, dc in ((1870, 4), (2630, 5), (3410, 7), (4980, 9)))
    return amp * s / 3
for k, tk in enumerate((3.9, 4.15, 4.35, 4.5)): add(clang(0.4 * 0.6 ** k), tk, pan=0.2)
nz = lp(rng.uniform(-1, 1, int(SR * 2.3)), 2500)                                        # cereal avalanche
grit = (rng.uniform(0, 1, len(nz)) > 0.997).astype(float); grit = bp(grit * 4, 1500, 6000)
add((nz * 0.25 + grit * 0.4) * np.minimum(1, tt(2.3) * 6) * np.minimum(1, (2.3 - tt(2.3)) * 4), 6.7)
for tk in (9.25, 9.6, 9.95): add(tone(2000, 0.22, 0.28, 3), tk)                         # microwave beeps
add(snare(0.6), 10.2); add(kick(0.5), 10.2)                                             # slap
t = tt(0.5); add(0.07 * hp(rng.uniform(-1, 1, len(t)), 2000) * np.exp(-t * 6), 12.15)   # phew breath
add(creak(0.7, 150, 90), 12.9)                                                          # door opens
add(noise_sweep(0.35, 4000, 400, 0.25), 12.85)                                          # record scratch
for k, m in enumerate((55, 54, 53, 52)):                                                # sad wah-wah
    d = 0.35 if k < 3 else 0.9
    add(saw(mtof(m), d, 0.13, cut=1200) * (1 + 0.3 * np.sin(2 * np.pi * 6 * tt(d))), 14.2 + k * 0.33)
def verb(x):
    y = x.copy()
    for dly, g in ((0.031, 0.3), (0.047, 0.25), (0.071, 0.2), (0.113, 0.14)):
        n = int(dly * SR); y[n:] += x[:-n] * g
    return y
L, R = verb(L), verb(R)
end = np.ones(len(L)); end[-int(SR * 0.3):] = np.linspace(1, 0, int(SR * 0.3))
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.3) * 0.89 * end, np.tanh(R / peak * 1.3) * 0.89 * end
st = np.empty(len(L) * 2); st[0::2] = L; st[1::2] = R
import sys
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
