"""Soundtrack: bouncy lofi in A (9am call) -> fast triumphant pitch -> record scratch + mute buzzer -> click, call-ended bloop, sad wah (on mute)."""
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 16.6
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(909)

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
# 0-6.0 bouncy lofi in A major, 104 bpm
b = 60 / 104
chords = [[57, 61, 64, 68], [54, 57, 61, 64], [50, 54, 57, 61], [52, 56, 59, 62]]
mel = [76, 0, 73, 76, 78, 0, 76, 73, 74, 0, 73, 71, 69, 0, 71, 73]
t0 = 0.0; n = 0
while t0 < 5.95:
    ch = chords[(n // 4) % 4]
    if n % 4 == 0:
        for m in ch: addm(mus, rhodes(mtof(m), b * 2, 0.05), t0)
        addm(mus, bass(mtof(ch[0] - 24), b * 0.9, 0.24), t0)
    if n % 2 == 0: addm(mus, kick(0.4), t0)
    if n % 4 == 2: addm(mus, snare(0.22), t0)
    addm(mus, hat(0.05), t0 + b / 4)
    if mel[n % 16]: addm(mus, pluck(mtof(mel[n % 16]), 0.3, 0.09), t0)
    n += 1; t0 += b / 2
# 6.0-9.85 fast triumphant pitch music, D major 140 bpm, building
b2 = 60 / 140; t0 = 6.0; n = 0
prog = [[62, 66, 69], [67, 71, 74], [69, 73, 76], [66, 69, 74]]
while t0 < 9.8:
    ch = prog[(n // 4) % 4]
    if n % 4 == 0:
        for m in ch: addm(mus, saw(mtof(m), b2 * 2, 0.05, cut=2200), t0)
        addm(mus, bass(mtof(ch[0] - 24), b2 * 1.8, 0.26), t0)
    addm(mus, kick(0.45) if n % 2 == 0 else snare(0.2), t0)
    addm(mus, hat(0.06), t0 + b2 / 2)
    addm(mus, pluck(mtof(ch[n % 3] + 12), 0.2, 0.08), t0 + b2 / 2)
    n += 1; t0 += b2
# 11.0-12.8 tense low drone
t = tt(1.8); addm(mus, 0.12 * np.sin(2 * np.pi * 55 * t) * np.minimum(1, t * 3) * (1 + 0.3 * np.sin(2 * np.pi * 7 * t)), 11.0)
# 15.0-16.6 deadpan
for k2, m in enumerate([57, 60, 64, 67]): addm(mus, rhodes(mtof(m), 1.6, 0.06), 15.0 + k2 * 0.03)
mus = lp(mus, 6000)
L += mus; R += mus

# SFX
add(noise_sweep(0.3, 800, 4000, 0.15), 0.3)                                    # hair swoosh
add(tone(1568, 0.25, 0.12, 10), 1.45); add(tone(2093, 0.4, 0.12, 8), 1.55)    # thumbs-up sparkle
for k in range(6): add(tone(rng.uniform(300, 420), 0.07, 0.07, 30), 3.2 + k * 0.15, pan=-0.3)  # boss talking blips
add(tone(880, 0.2, 0.15, 10), 4.3); add(tone(1320, 0.3, 0.15, 8), 4.38)       # ME!! pop
for k in range(22): add(tone(rng.uniform(380, 640), 0.08, 0.07, 25), 6.15 + k * 0.16, pan=0.2)  # pitch babble
add(noise_sweep(0.35, 4000, 400, 0.28), 9.6)                                  # record scratch
add(tone(660, 0.3, 0.14, 8), 9.9)                                             # bubble ding
add(saw(mtof(34), 0.7, 0.3, cut=900) + saw(mtof(35), 0.7, 0.2, cut=900), 11.0)  # MUTED buzzer
add(kick(0.5), 11.0)
add(hat(0.3, 0.06), 13.1); add(tone(2400, 0.05, 0.2, 60), 13.1)              # click
for k, f in enumerate((784, 659, 523)): add(tone(f, 0.3, 0.15, 8), 14.7 + k * 0.14)  # call-ended bloop
for k, m in enumerate((58, 57, 56, 55)):                                      # sad wah-wah
    d = 0.3 if k < 3 else 0.9
    add(saw(mtof(m), d, 0.12, cut=1200) * (1 + 0.3 * np.sin(2 * np.pi * 6 * tt(d))), 15.2 + k * 0.3)
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
