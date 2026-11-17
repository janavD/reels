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
    while tb < t1 - 0.2:
        addm(mus, bell(mtof(box[i % len(box)]), 1.0, 0.07), tb)
        if i % 4 == 0: addm(mus, rhodes(mtof([52, 49][(i // 4) % 2]), 1.6, 0.08), tb)
        i += 1; tb += 0.4
    k = t0
    while k < t1: addm(mus, hat(0.05, 0.02), k); k += 0.5
# a2-a3 (3.2-9.4): hype bouncy A major, 132 bpm
b = 60 / 132
prog = [[57, 61, 64], [62, 66, 69], [64, 68, 71], [57, 61, 64]]; rts = [45, 50, 52, 45]
mel = [69, 73, 76, 73, 74, 78, 81, 78, 76, 80, 83, 80, 81, 76, 73, 69]
t0 = 3.2; n = 0
while t0 < 9.35:
    bar = (n // 8) % 4
    if n % 2 == 0: addm(mus, saw(mtof(mel[n % 16]), b * 0.9, 0.09, cut=2600), t0)
    if n % 4 == 0:
        for m in prog[bar]: addm(mus, saw(mtof(m), b * 1.5, 0.05, cut=1500), t0)
        addm(mus, kick(0.7), t0); addm(mus, bass(mtof(rts[bar]), b * 1.8, 0.3), t0)
    if n % 8 == 4: addm(mus, snare(0.3), t0)
    addm(mus, hat(0.07), t0)
    n += 1; t0 += b / 2
# a4 (9.4-12.8): drowsy detuned rhodes, slowing
t0 = 9.4; i = 0; step = 0.55
while t0 < 12.7:
    m = [64, 61, 57, 56, 54, 52][i % 6]
    addm(mus, rhodes(mtof(m) * (1 - 0.006 * i), 1.2, 0.1), t0); addm(mus, rhodes(mtof(m - 12) * 0.997, 1.2, 0.06), t0)
    i += 1; t0 += step; step *= 1.06
# a5 (12.8-16.2): soft lofi
b2 = 60 / 80; t0 = 12.8; bar = 0
chords = [[57, 60, 64, 67], [53, 57, 60, 64]]
while t0 < 16.2:
    for k2, m in enumerate(chords[bar % 2]): addm(mus, rhodes(mtof(m), 1.6, 0.07), t0 + k2 * 0.015)
    for beat in range(4):
        tb = t0 + beat * b2
        if tb > 16.2: break
        if beat in (0, 2): addm(mus, kick(0.45), tb)
        if beat in (1, 3): addm(mus, snare(0.18), tb)
        addm(mus, hat(0.05), tb)
    bar += 1; t0 += 4 * b2
mus = lp(mus, 6000)
L += mus; R += mus

# SFX
for k in range(2): add(pluck(mtof(84 + k * 3), 0.2, 0.12), 0.55 + k * 0.6)               # finger count blips
t = tt(0.6); add(0.15 * np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, 0.6], [300, 900])) / SR) * np.exp(-t * 3), 3.25)  # jump up whoosh
for k in range(3): add(tone(1400 + k * 200, 0.15, 0.15, 20), 3.75 + k * 0.15)            # ! pops
for k, tk in enumerate((6.6, 7.4, 8.2)):                                               # checklist dings
    add(bell(mtof(84 + k * 2), 0.8, 0.1), tk); add(bell(mtof(91 + k * 2), 0.8, 0.06), tk + 0.06)
sz = hp(rng.uniform(-1, 1, int(SR * 3.2)), 3000) * 0.05 * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * tt(3.2)))
add(sz, 6.1, pan=-0.3)                                                                 # pan sizzle
add(noise_sweep(0.5, 3000, 300, 0.2), 9.25)                                            # tape stop
for k in range(3):                                                                     # head-jerk boings
    tj = 9.4 + 0.94 + k * 1.1
    t = tt(0.3); add(0.16 * np.sin(2 * np.pi * np.cumsum(np.interp(t, [0, 0.3], [200, 600])) / SR) * np.exp(-t * 6), tj)
for k in range(3):                                                                     # snores
    t = tt(0.9); add(lp(rng.uniform(-1, 1, len(t)), 250) * np.sin(np.pi * t / 0.9) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t)) * 0.7, 13.2 + k * 1.1)
for k in range(10):                                                                    # crickets
    tc = 16.5 + k * 0.32
    t = tt(0.08); add(0.06 * np.sin(2 * np.pi * 4500 * t) * (np.sin(2 * np.pi * 60 * t) > 0), tc, pan=0.5 if k % 2 else -0.5)

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
