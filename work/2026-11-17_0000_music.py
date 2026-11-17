"""Soundtrack v2: lo-fi beat -> tense panic beat -> sad lo-fi outro, plus SFX."""
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 16.6
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(11)

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

bpm = 96; b = 60 / bpm; sw = b * 0.56
chords = [[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 62]]  # Am7 Fmaj7 G7 Em7
roots = [45, 41, 43, 40]
def lofi_block(t_start, t_end, mel_shift=0, gain=1.0):
    buf = np.zeros(len(L)); bar = 0; t0 = t_start
    while t0 < t_end:
        ch = chords[bar % 4]
        for st in (0, b * 2 + sw):
            for k, m in enumerate(ch): addm(buf, rhodes(mtof(m), 1.4, 0.1), t0 + st + k * 0.012)
        addm(buf, bass(mtof(roots[bar % 4]), b * 2.2), t0)
        for beat in range(4):
            tb = t0 + beat * b
            if beat in (0, 2): addm(buf, kick(0.7), tb)
            if beat in (1, 3): addm(buf, snare(0.3), tb)
            addm(buf, hat(), tb); addm(buf, hat(0.07), tb + sw)
        mel = [[76, 79, 81], [77, 76], [74, 79, 77], [76, 71]][bar % 4]
        for j, m in enumerate(mel): addm(buf, sq(mtof(m + mel_shift), 0.22, 0.045), t0 + b * (0.5 + j * 1.2))
        bar += 1; t0 += 4 * b
    i0, i1 = int(t_start * SR), int(t_end * SR); buf[:i0] = 0; buf[i1:] = 0
    return lp(buf, 4500) * gain

mus = lofi_block(0.0, 3.05) + lofi_block(14.7, 16.6)
# g2 defeat: sad chip descend + tense pulse
for j, m in enumerate((67, 63, 60, 55)): addm(mus, sq(mtof(m), 0.32, 0.09, 3), 3.2 + j * 0.22)
pb = 60 / 132
for i in range(int(2.0 / (pb / 2))):
    tb = 4.2 + i * pb / 2
    addm(mus, saw(mtof([40, 40, 43, 40][i % 4]), pb * 0.45, 0.14, cut=700), tb)
    if i % 2 == 0: addm(mus, kick(0.75), tb)
# g3 victory fanfare + bouncy
for j, (m, d) in enumerate(((72, 0.14), (76, 0.14), (79, 0.14), (84, 0.5))): addm(mus, sq(mtof(m), d + 0.2, 0.09, 2.5), 6.5 + j * 0.15)
bb = 60 / 128
for i in range(12):
    tb = 7.2 + i * bb / 2
    if tb > 9.35: break
    addm(mus, sq(mtof([60, 64, 67, 72, 67, 64][i % 6]), 0.15, 0.05, 8), tb)
    if i % 2 == 0: addm(mus, kick(0.7), tb)
    else: addm(mus, hat(0.1), tb)
    if i % 4 == 2: addm(mus, snare(0.32), tb)
# g4 drowsy: slow detuned pad, then birds
for k, m in enumerate((57, 60, 64)):
    addm(mus, rhodes(mtof(m) * 0.995, 3.0, 0.08), 9.45 + k * 0.05)
for k, m in enumerate((55, 59, 62)):
    addm(mus, rhodes(mtof(m) * 0.995, 2.0, 0.07), 11.2 + k * 0.05)
mus = mus.copy(); L += mus; R += mus

clicks = [0.3 + i * 0.17 for i in range(15)] + [4.0 + i * 0.07 for i in range(28)] + [10.0 + i * 0.3 for i in range(5)] + [13.0 + i * 0.25 for i in range(14)]
for tc in clicks:
    m = int(SR * 0.015); add(bp(rng.uniform(-1, 1, m), 2000, 7000) * np.exp(-np.arange(m) / 90) * 0.25, tc, pan=0.3)
add(tone(110, 0.4, 0.5, 8), 3.4)                                       # thud on defeat
for tb in (10.0, 10.25, 10.4, 10.9, 11.15):                              # bird chirps
    t = tt(0.12); f = np.linspace(3200, 4600, len(t)); add(0.08 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18), tb, pan=0.6)
add(tone(mtof(88), 0.3, 0.15, 6) + tone(mtof(95), 0.3, 0.1, 6), 11.1)   # "!" sting
add(noise_sweep(0.5, 600, 5000, 0.08), 12.3)
t = tt(1.5); ring = 0.15 * np.sign(np.sin(2 * np.pi * 2100 * t)) * (np.sin(2 * np.pi * 14 * t) > 0)
add(lp(ring, 6000), 12.9, pan=-0.4)
add(bp(rng.uniform(-1, 1, int(SR * 0.12)), 400, 4000) * np.exp(-tt(0.12) * 30) * 0.7, 14.4)  # alarm slapped off

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
