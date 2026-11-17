"""Soundtrack v2: lo-fi beat -> tense panic beat -> sad lo-fi outro, plus SFX."""
import numpy as np, wave, sys
from scipy.signal import lfilter, butter

SR = 44100; T = 67.0
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(7)

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
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
def addm(buf, sig, t):
    i = int(t * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i + n] += sig[:n]
def pad(freqs, d, amp=0.05, cut=2200):
    t = tt(d); env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.5)
    s = sum(saw(f * dt, d, 1.0, cut=cut) * 0 + (2 * ((f * dt * t) % 1) - 1) for f in freqs for dt in (0.997, 1.003))
    return lp(s, cut) * env * amp
def crash(amp=0.25):
    t = tt(2.0); return amp * hp(rng.uniform(-1, 1, len(t)), 5000) * np.exp(-t * 2.2)
def clap(amp=0.3):
    t = tt(0.12); return amp * bp(rng.uniform(-1, 1, len(t)), 900, 5000) * np.exp(-t * 35)

def pluck(f, d=1.6, amp=0.22, bright=0.5, detune=0.0):
    """Karplus-Strong acoustic guitar string."""
    f = f * (1 + detune); n = int(SR / f); g = 0.996
    x = np.zeros(int(SR * d)); x[:n] = lp(rng.uniform(-1, 1, n), 1500 + 5000 * bright)
    a = np.zeros(n + 2); a[0] = 1; a[n] = -g / 2; a[n + 1] = -g / 2
    y = lfilter([1], a, x)
    return amp * y / (np.abs(y).max() + 1e-9) * np.minimum(1, (d - tt(d)) * 8)

def strum(t0, notes, amp=0.16, sour=0.0, down=True, d=1.6, pan=0.0):
    seq = notes if down else notes[::-1]
    for i, m in enumerate(seq):
        det = rng.uniform(-sour, sour)
        add(pluck(mtof(m), d, amp, detune=det), t0 + i * 0.014, pan=pan)

def ping(t0):
    t = tt(1.2); f = 1800 * np.exp(-t * 0.6)
    add(0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4), t0)
    add(noise_sweep(0.3, 6000, 2000, 0.15), t0)

def heartbeat(t0):
    add(kick(0.5), t0); add(kick(0.35), t0 + 0.22)

Am, F, Cc, G, Em, Dm = [45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [48, 52, 55, 60, 64], [43, 47, 50, 55, 59], [40, 47, 52, 55, 59], [50, 57, 62, 65]

# ---------- g1 0-9: day 1, awkward. sparse lo-fi rhodes, sour strums ----------
bpm = 84; b = 60 / bpm
for i, ch in enumerate([[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]] * 2):
    for m in ch: add(rhodes(mtof(m), b * 4, 0.05), i * b * 4 * 0.5 if False else i * 2.2, pan=-0.2)
for k in range(0, 4): add(bass(mtof(33 + [0, -4, -2, -5][k % 4]), 2.0, 0.18), k * 2.2)
for t0 in (0.1, 0.45, 0.8, 1.1): strum(t0, Am, 0.14, sour=0.05)
add(saw(mtof(40), 0.5, 0.12, cut=500), 0.5)  # CLUNK
for t0 in (2.45, 2.8, 3.2): strum(t0, F, 0.14, sour=0.08)
t = tt(1.2); add(0.18 * np.sin(2 * np.pi * np.cumsum(110 * (1 - 0.3 * t)) / SR) * np.exp(-t * 2), 2.6)  # BWOOONG bend
add(tone(mtof(76), 0.15, 0.1), 4.3); add(tone(mtof(71), 0.2, 0.1), 4.45)  # cat 'nope'
for j in range(3): add(tone(mtof(84 - j * 2), 0.12, 0.08, 10), 5.7 + j * 0.25)  # ow ow ow

# ---------- g2 9-17: tuning tension -> PING ----------
for j in range(14):
    tj = 9.4 + j * 0.22 * (1 - j / 30)
    add(pluck(mtof(64) * (1 + j * 0.035), 0.3, 0.12), tj)
add(noise_sweep(1.0, 800, 6000, 0.12), 11.6)
ping(12.6); add(crash(0.18), 12.6)
for k in range(3): add(rhodes(mtof([57, 53, 52][k]), 1.6, 0.06), 13.5 + k * 1.2)
add(bass(mtof(33), 3.0, 0.15), 14.0)

# ---------- g3 17-26: playing for mom, wobbly little tune ----------
melody = [64, 67, 69, 67, 64, 62, 60, 62, 64, 64, 62, 60]
for j, m in enumerate(melody):
    add(pluck(mtof(m), 0.6, 0.18, detune=rng.uniform(-0.03, 0.03) if j % 3 == 0 else 0), 17.4 + j * 0.4)
for k in range(5): strum(17.2 + k * 1.0, [Cc, G, Am, F, Cc][k], 0.08, sour=0.02)
add(noise_sweep(0.5, 300, 900, 0.06), 18.6)  # door creak
for j in range(4): add(bell(mtof([72, 76, 79, 84][j]), 0.5, 0.05), 19.6 + j * 0.1)  # sweetie sparkle
add(noise_sweep(0.4, 900, 300, 0.06), 22.2)  # door closes
add(tone(mtof(50), 0.6, 0.14, 3), 22.6); add(tone(mtof(46), 0.9, 0.14, 2), 23.2)  # sad 'womp'

# ---------- g4 26-37: night doubt -> calluses -> decision ----------
for k, ch in enumerate([[45, 57, 60, 64], [41, 53, 57, 60], [43, 55, 59, 62]]):
    add(pad([mtof(m) for m in ch], 3.4, 0.022, cut=1400), 26 + k * 2.6)
for j, m in enumerate([69, 67, 64, 62, 60, 64]):
    add(rhodes(mtof(m), 1.6, 0.06), 26.3 + j * 0.65)
for j in range(6): add(bell(mtof([72, 76, 79, 84, 88, 91][j]), 1.0, 0.05), 31.4 + j * 0.12)  # calluses shimmer
add(pad([mtof(m) for m in (48, 55, 60, 64, 67)], 3.5, 0.03, cut=2400), 31.5)
add(noise_sweep(1.6, 400, 5000, 0.1), 32.4)
strum(34.1, Cc, 0.2, d=2.4)  # ok. again.

# ---------- g5 37-49: grind montage, building groove, cleaner + faster ----------
prog = [Am, F, Cc, G]
bpm = 96; b = 60 / bpm; t0 = 37.0; bar = 0
while t0 < 49.0:
    k = (t0 - 37) / 12
    ch = prog[bar % 4]
    for s in range(8):
        ts = t0 + s * b / 2
        if ts >= 49: break
        add(pluck(mtof(ch[[0, 2, 3, 4, 3, 2, 1, 2][s] % len(ch)] + 12), 0.8, 0.12 + 0.05 * k,
                  detune=rng.uniform(-0.02, 0.02) * (1 - k)), ts, pan=0.2)
        add(hat(0.05 + 0.05 * k), ts, pan=-0.3)
        add(tone(1500, 0.03, 0.05 * (1 - k), 60), ts)  # metronome
    for q in range(4):
        tq = t0 + q * b
        if tq >= 49: break
        if k > 0.15 and q % 2 == 0: add(kick(0.55), tq)
        if k > 0.45 and q % 2 == 1: add(snare(0.22), tq)
    add(bass(mtof(ch[0] - 12 + (12 if ch[0] < 40 else 0)), b * 4, 0.16 + 0.06 * k), t0)
    t0 += b * 4; bar += 1
add(noise_sweep(1.2, 500, 9000, 0.12), 47.8)

# ---------- g6 49-60: open mic. heartbeat -> full song -> applause ----------
for j in range(4): heartbeat(49.2 + j * 0.7)
add(pad([mtof(m) for m in (45, 52, 57)], 3.0, 0.02, cut=900), 49.0)
bpm = 100; b = 60 / bpm; t0 = 52.0; bar = 0
song = [Cc, G, Am, F]
mel = [76, 74, 72, 74, 76, 79, 76, 74, 72, 69, 72, 74, 76, 76, 79, 81]
mi = 0
while t0 < 60.0:
    ch = song[bar % 4]
    for s, dn in enumerate([True, True, False, True, False, True, True, False]):
        ts = t0 + s * b / 2
        if ts >= 60: break
        strum(ts, ch, 0.09 if dn else 0.06, down=dn, d=0.9, pan=0.15)
    for q in range(4):
        tq = t0 + q * b
        if tq >= 60: break
        add(kick(0.6), tq) if q % 2 == 0 else add(snare(0.25), tq)
        add(hat(0.06), tq + b / 2)
        if mi < len(mel): add(rhodes(mtof(mel[mi]), b * 1.5, 0.07), tq, pan=-0.2); mi += 1
    add(bass(mtof(ch[0] - 12 if ch[0] > 44 else ch[0]), b * 4, 0.2), t0)
    t0 += b * 4; bar += 1
add(crash(0.3), 56.4)
for j in range(140):  # applause
    add(clap(rng.uniform(0.05, 0.14)), 56.4 + rng.uniform(0, 3.6), pan=rng.uniform(-0.8, 0.8))
for j in range(8): add(bell(mtof(84 + (j % 4) * 3), 0.6, 0.04), 56.5 + j * 0.18, pan=rng.uniform(-0.6, 0.6))

# ---------- g7 60-67: warm resolve, strumming for the cat ----------
for k, ch in enumerate([F, G, Cc, Cc]):
    for s in range(4): strum(60.1 + k * 1.7 + s * 0.42, ch, 0.11, down=s % 2 == 0, d=1.2)
add(pad([mtof(m) for m in (48, 55, 60, 64, 67)], 6.8, 0.025, cut=2000), 60.1)
for j in range(5): add(bell(mtof([79, 84, 88, 91, 96][j]), 1.4, 0.04), 64.6 + j * 0.15)
def verb(x):
    y = x.copy()
    for dly, g in ((0.031, 0.3), (0.047, 0.26), (0.073, 0.21), (0.117, 0.16), (0.171, 0.1)):
        n = int(dly * SR); y[n:] += x[:-n] * g
    return y
L, R = verb(L), verb(R)
end = np.ones(len(L)); end[-int(SR * 0.6):] = np.linspace(1, 0, int(SR * 0.6))
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.3) * 0.89 * end, np.tanh(R / peak * 1.3) * 0.89 * end
st = np.empty(len(L) * 2); st[0::2] = L; st[1::2] = R
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
