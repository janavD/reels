"""Soundtrack: bouncy lofi in F -> rain + tense minor when the app says 4 min -> whoosh + splash -> deadpan sad wah (bus app 1 min)."""
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 16.2
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(808)

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
# 0-6.0: bouncy lofi in F major, 96 bpm
b = 60 / 96
chords = [[53, 57, 60, 64], [50, 53, 57, 60], [46, 50, 53, 57], [48, 52, 55, 58]]
mel = [72, 0, 69, 72, 74, 0, 72, 69, 70, 0, 69, 67, 65, 0, 67, 69]
t0 = 0.0; n = 0
while t0 < 5.95:
    ch = chords[(n // 4) % 4]
    if n % 4 == 0:
        for m in ch: addm(mus, rhodes(mtof(m), b * 2, 0.05), t0)
        addm(mus, bass(mtof(ch[0] - 12), b * 0.9, 0.24), t0)
    if n % 2 == 0: addm(mus, kick(0.4), t0)
    if n % 4 == 2: addm(mus, snare(0.22), t0)
    addm(mus, hat(0.05), t0 + b / 2)
    if mel[n % 16]: addm(mus, pluck(mtof(mel[n % 16]), 0.3, 0.09), t0)
    n += 1; t0 += b / 2 if False else b / 2 * 1
# 6.0-10.6: tense F minor pulse, faster, stops dead at the splash
b2 = 60 / 132; t0 = 6.0; n = 0
while t0 < 10.55:
    m = [41, 41, 44, 41, 39, 41, 46, 44][n % 8]
    addm(mus, saw(mtof(m), b2 / 2, 0.16, cut=700), t0)
    if n % 4 == 0: addm(mus, kick(0.45), t0)
    if n % 2 == 1: addm(mus, hat(0.06), t0)
    if t0 > 6.85 and n % 8 == 0:
        for mm in (65, 68, 72): addm(mus, saw(mtof(mm), b2 * 3, 0.05, cut=1600), t0)
    n += 1; t0 += b2 / 2
# 12.4-16.2: deadpan lofi
t0 = 12.45
for k2, m in enumerate([53, 56, 60, 63]): addm(mus, rhodes(mtof(m), 3.6, 0.07), t0 + k2 * 0.03)
for k in range(7): addm(mus, hat(0.035), t0 + k * 0.55)
mus = lp(mus, 5200)
L += mus; R += mus

# SFX
rain_n = lp(hp(rng.uniform(-1, 1, int(SR * 10.9)), 1500), 7000) * 0.07
rain_n *= np.minimum(1, tt(10.9) / 1.2)
add(rain_n, 5.3, pan=-0.1); add(rain_n[::-1].copy(), 5.3, pan=0.1)
for tk in np.arange(0.05, 0.95, 0.16): add(hat(0.12, 0.06), tk)                       # running footsteps
for tk, f in ((1.4, 1568), (1.52, 2093)): add(tone(f, 0.5, 0.18, 6), tk)              # app ding
for tk in np.arange(3.0, 6.0, 0.45): add(tone(1200, 0.04, 0.08, 60), tk, pan=0.3)       # foot taps / clock
add(noise_sweep(0.35, 4000, 400, 0.25), 6.85)                                           # record scratch
add(tone(1100, 0.3, 0.2, 8), 6.9); add(tone(740, 0.5, 0.2, 5), 7.05)                    # wrong-notification
add(noise_sweep(1.1, 300, 3000, 0.35), 10.2, pan=0.4)                                   # bus whoosh
t = tt(0.6); add(0.2 * np.sin(2 * np.pi * 70 * t) * np.exp(-t * 4), 10.25)              # engine rumble
sp = lp(rng.uniform(-1, 1, int(SR * 0.9)), 3000) * np.exp(-tt(0.9) * 4) * 0.55          # splash
add(sp, 10.65); add(kick(0.4), 10.65)
for tk, f in ((12.65, 1568), (13.65, 1046)): add(tone(f, 0.5, 0.15, 6), tk)            # arrived / next ding
for k, m in enumerate((58, 57, 56, 55)):                                                # sad wah-wah
    d = 0.35 if k < 3 else 1.0
    add(saw(mtof(m), d, 0.13, cut=1200) * (1 + 0.3 * np.sin(2 * np.pi * 6 * tt(d))), 14.0 + k * 0.33)
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
