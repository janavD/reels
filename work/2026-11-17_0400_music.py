"""Soundtrack: sneaky pizzicato -> horror drone + scream -> cozy lo-fi purr outro (noise at 4am)."""
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 19.4
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(47)

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
def sq(f, d, amp=0.08, dec=6):  # chiptune square
    t = tt(d); return amp * np.sign(np.sin(2 * np.pi * f * t)) * np.minimum(1, t * 400) * np.exp(-t * dec)


def addm(buf, sig, t):
    i = int(t * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i + n] += sig[:n]
def pluck(f, d=0.3, amp=0.12):
    t = tt(d); return amp * np.exp(-t * 14) * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t))

mus = np.zeros(len(L))
# n1-n3 (0-9.4): sneaky D-minor pizzicato walk, tempo 104
b = 60 / 104
line = [50, 53, 57, 53, 50, 52, 53, 56, 57, 56, 53, 52]
roots = [38, 38, 34, 33]
i = 0; tb = 0.9
while tb < 9.3:
    addm(mus, pluck(mtof(line[i % len(line)] + 12), 0.3, 0.11), tb)
    if i % 2 == 0: addm(mus, pluck(mtof(roots[(i // 4) % 4]), 0.5, 0.2), tb)
    if i % 4 == 2: addm(mus, hat(0.06), tb)
    i += 1; tb += b / 2
# hide under blanket: heartbeat 3.0-6.0
for k in range(5):
    addm(mus, kick(0.5), 3.1 + k * 0.6); addm(mus, kick(0.35), 3.32 + k * 0.6)
# n4 (9.4-12.2): horror drone + stinger
t = tt(2.8); dr = 0.09 * (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 58.3 * t)) * np.minimum(1, t * 3)
addm(mus, lp(dr, 800), 9.4)
for m in (74, 75, 80): addm(mus, saw(mtof(m), 0.9, 0.08, cut=3000), 10.0)
# n5-n6 (12.2-19.4): cozy lofi in Bb
b2 = 60 / 84; sw = b2 * 0.55
chords = [[58, 62, 65, 69], [55, 58, 62, 65], [51, 55, 58, 62], [53, 57, 60, 63]]
rts = [46, 43, 39, 41]
t0 = 12.25; bar = 0
while t0 < 19.4:
    ch = chords[bar % 4]
    for st in (0, b2 * 2 + sw):
        for k, m in enumerate(ch): addm(mus, rhodes(mtof(m), 1.4, 0.09), t0 + st + k * 0.014)
    addm(mus, bass(mtof(rts[bar % 4]), b2 * 2.2), t0)
    for beat in range(4):
        tb = t0 + beat * b2
        if beat in (0, 2): addm(mus, kick(0.6), tb)
        if beat in (1, 3): addm(mus, snare(0.25), tb)
        addm(mus, hat(0.08), tb); addm(mus, hat(0.05), tb + sw)
    bar += 1; t0 += 4 * b2
mus = lp(mus, 5000)
L += mus; R += mus

# SFX
thud = tone(70, 0.5, 0.6, 9) + lp(rng.uniform(-1, 1, int(SR * 0.5)), 300) * np.exp(-tt(0.5) * 14) * 0.5
add(thud, 0.38)
t = tt(0.9); f = 180 + 60 * np.sin(2 * np.pi * 3 * t)
add(lp(0.12 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 1500) * np.minimum(1, t * 8) * np.minimum(1, (0.9 - t) * 8), 4.0, pan=0.4)  # creak
for k in range(5): add(bp(rng.uniform(-1, 1, int(SR * 0.06)), 300, 2000) * np.exp(-tt(0.06) * 60) * 0.3, 6.35 + k * 0.71)  # steps
add(noise_sweep(1.4, 800, 4000, 0.18), 10.6)                         # scream
t = tt(1.3); add(0.18 * np.sin(2 * np.pi * np.cumsum(500 + 300 * np.sin(2 * np.pi * 9 * t)) / SR) * np.exp(-t * 1.5), 10.62)
add(bp(rng.uniform(-1, 1, int(SR * 0.02)), 2000, 8000) * 0.4, 12.22)   # light switch click
for f0 in (2400, 3100, 3700): add(bell(f0, 0.6, 0.07), 13.95 + rng.uniform(0, 0.05))  # clink
t = tt(0.35); f = np.interp(t, [0, 0.15, 0.35], [400, 700, 500])
add(0.13 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / 0.35), 14.45, pan=0.3)  # mrrp
t = tt(3.4); purr = lp(rng.uniform(-1, 1, len(t)), 120) * (0.5 + 0.5 * np.sin(2 * np.pi * 25 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t))
add(purr * 1.2, 16.0, pan=0.3)

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
