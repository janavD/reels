"""Soundtrack v2: lo-fi beat -> tense panic beat -> sad lo-fi outro, plus SFX."""
import numpy as np, wave, sys
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


T = 16.6
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

# ---------- A: struggle, B minor, 66 bpm piano (0 -> 7.55) ----------
b = 60 / 66
prog = [([47, 54, 59, 62], 35), ([43, 50, 55, 59], 31), ([45, 52, 57, 61], 33), ([42, 49, 54, 57], 30)]  # Bm G A F#m
mel = [[74, 73, 71], [71, 69], [69, 71, 73], [66]]
A = np.zeros(len(L)); t0 = 0.0; k = 0
while t0 < 7.5:
    ch, root = prog[k % 4]
    for j, m in enumerate(ch): addm(A, rhodes(mtof(m), 2.6, 0.085), t0 + j * 0.05)
    addm(A, bass(mtof(root), b * 2.6, 0.22), t0)
    for j, m in enumerate(mel[k % 4]): addm(A, bell(mtof(m), 1.6, 0.055), t0 + b * (0.5 + j * 0.9))
    k += 1; t0 += b * 2
A = lp(A, 3200)
env = np.ones(len(L)); env[int(7.5 * SR):] = 0
env[int(5.8 * SR):int(7.5 * SR)] = np.linspace(1, 0.55, int(7.5 * SR) - int(5.8 * SR))
A *= env; L += A; R += A
# rain on day 23
rain = lp(rng.normal(0, 1, int(SR * 1.75)), 2500) * 0.025 * np.minimum(1, tt(1.75) * 4)
add(rain, 5.8)

# SFX
for j in range(4): add(tone(mtof(50 + j), 0.12, 0.04, 20), 0.6 + j * 0.3)       # grunt-ish strain
add(kick(0.9), 1.95); add(tone(90, 0.4, 0.5, 9), 1.95)                           # THUD
add(lp(rng.uniform(-1, 1, int(SR * 0.3)), 1200) * np.exp(-tt(0.3) * 14) * 0.4, 1.95)
for j in range(3): add(tone(mtof(86 - j * 4), 0.22, 0.08, 8), 2.05 + j * 0.13, pan=0.3)  # dizzy
n = int(SR * 0.5); add(np.sin(2 * np.pi * np.cumsum(np.linspace(700, 250, n)) / SR) * np.linspace(0.08, 0, n), 4.9)  # slide down

# ---------- B: decision + grind, D major build (7.55 -> 14.0) ----------
bpm = 112; bb = 60 / bpm
for j in range(3): add(clap(0.28), 7.55 + j * 0.35, pan=0.1)                   # chalk claps
add(noise_sweep(0.5, 400, 2500, 0.08), 7.6)
grid = np.arange(7.55, 14.0, bb / 2)
chords = [[50, 57, 62, 66], [57, 61, 64, 69], [59, 62, 66, 71], [55, 59, 62, 67]]  # D A Bm G
roots = [38, 45, 47, 43]
arp = [0, 2, 1, 3, 2, 1, 3, 2]
for i, tb in enumerate(grid):
    bar = int((tb - 7.55) / (bb * 4)); ch = chords[bar % 4]
    lvl = clamp_k = min(1.0, (tb - 7.55) / 6.4)
    add(saw(mtof(ch[arp[i % 8]] + 12), bb * 0.45, 0.05 + 0.06 * lvl, cut=900 + 2600 * lvl), tb, pan=0.25 * (1 if i % 2 else -1))
    if i % 2 == 0: add(kick(0.45 + 0.35 * lvl), tb)                                # heartbeat -> four on the floor
    if tb > 9.2:
        if i % 4 == 2: add(snare(0.18 + 0.15 * lvl), tb)
        add(hat(0.05 + 0.04 * lvl, 0.03), tb + bb / 4, pan=0.3)
    if i % 8 == 0:
        add(bass(mtof(roots[bar % 4]), bb * 4, 0.25), tb)
        add(pad([mtof(m) for m in ch], bb * 4, 0.012 + 0.02 * lvl, cut=1500 + 2000 * lvl), tb)
# day counter ticks in grind
per = 2.8 / 23
for j in range(23): add(tone(mtof(81 + (j % 4) * 2), 0.05, 0.05, 30), 9.2 + j * per, pan=-0.4)
# effort strain on day 47
add(noise_sweep(1.9, 300, 9000, 0.16), 12.2)
for j in range(10): add(kick(0.5 + j * 0.04), 12.3 + j * 0.17)                  # drum roll build

# ---------- C: chin over the bar, climax (14.25 -> end) ----------
TOP = 14.25
add(kick(1.0), TOP); add(crash(0.3), TOP); add(tone(73, 0.8, 0.5, 4), TOP)
for j, m in enumerate((74, 78, 81, 86, 90)): add(bell(mtof(m), 1.6, 0.11), TOP + j * 0.06, pan=-0.2 + j * 0.1)
C = np.zeros(len(L))
cb = 60 / 120
cprog = [([50, 57, 62, 66, 69], 38), ([55, 59, 62, 67, 71], 43), ([57, 61, 64, 69, 73], 45)]  # D G A
cmel = [78, 81, 83, 81, 86, 85, 81, 78, 81]
for j in range(3):
    ch, root = cprog[j]; ts = TOP + j * cb * 1.5
    addm(C, pad([mtof(m) for m in ch], cb * 1.6 if j < 2 else 2.4, 0.03, cut=3500), ts)
    for m in ch: addm(C, rhodes(mtof(m), 1.6, 0.06), ts)
    addm(C, bass(mtof(root), cb * 1.6 if j < 2 else 2.2, 0.3), ts)
for j, m in enumerate(cmel):
    addm(C, bell(mtof(m), 1.0, 0.09), TOP + 0.75 + j * cb / 2)
i = 0
while TOP + 0.75 + i * cb / 2 < 16.3:
    tb = TOP + 0.75 + i * cb / 2
    if i % 2 == 0: addm(C, kick(0.7), tb)
    if i % 4 == 2: addm(C, snare(0.3), tb)
    addm(C, hat(0.08, 0.04), tb + cb / 4)
    i += 1
add(crash(0.22), TOP + 0.75)
L += C; R += C
# cheers sparkle
for j in range(8): add(bell(mtof(93 + (j % 3) * 2), 0.5, 0.04), 15.1 + j * 0.15, pan=rng.uniform(-0.6, 0.6))

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
