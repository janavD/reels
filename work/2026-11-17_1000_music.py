"""Soundtrack: bouncy store-muzak lofi in A -> error buzzes -> tense pulse + alarm while frozen -> tap, success chime, deadpan (self checkout)."""
import numpy as np, wave
from scipy.signal import lfilter, butter

SR = 44100; T = 17.4
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
rng = np.random.default_rng(1000)

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
# 0-4.0: bouncy elevator/store muzak in A major, 104 bpm
b = 60 / 104
chords = [[57, 61, 64, 68], [54, 57, 61, 64], [50, 54, 57, 61], [52, 56, 59, 62]]
mel = [76, 0, 73, 76, 78, 0, 76, 73, 74, 0, 73, 71, 69, 0, 71, 73]
t0 = 0.0; n = 0
while t0 < 3.95:
    ch = chords[(n // 4) % 4]
    if n % 4 == 0:
        for m in ch: addm(mus, rhodes(mtof(m), b * 2, 0.05), t0)
        addm(mus, bass(mtof(ch[0] - 24), b * 0.9, 0.24), t0)
    if n % 2 == 0: addm(mus, kick(0.38), t0)
    if n % 4 == 2: addm(mus, snare(0.2), t0)
    addm(mus, hat(0.05), t0 + b / 4)
    if mel[n % 16]: addm(mus, bell(mtof(mel[n % 16]), 0.5, 0.06), t0)
    n += 1; t0 += b / 2
# 4.0-13.2: tense A minor pulse, faster during the freeze
t0 = 4.1; n = 0
while t0 < 13.15:
    b2 = 60 / (120 if t0 < 9.4 else 150)
    m = [45, 45, 48, 45, 44, 45, 50, 48][n % 8]
    addm(mus, saw(mtof(m), b2 / 2, 0.14, cut=650), t0)
    if n % 4 == 0: addm(mus, kick(0.42), t0)
    if n % 2 == 1: addm(mus, hat(0.06), t0)
    if t0 > 9.4 and n % 8 == 0:
        for mm in (69, 72, 76): addm(mus, saw(mtof(mm), b2 * 3, 0.045, cut=1500), t0)
    n += 1; t0 += b2 / 2
# 14.3-17.4: deadpan lofi back in A
t0 = 14.35
for k2, m in enumerate([57, 61, 64, 68]): addm(mus, rhodes(mtof(m), 3.0, 0.07), t0 + k2 * 0.03)
for k in range(6): addm(mus, hat(0.035), t0 + k * 0.5)
addm(mus, bass(mtof(33), 2.5, 0.22), t0)
mus = lp(mus, 5200)
L += mus; R += mus

# SFX
def err(t0):
    for k in range(2): add(saw(mtof(46), 0.22, 0.2, cut=1400), t0 + k * 0.26, pan=0.3)
def ding(t0, fs=(1319, 1760)):
    for k, f in enumerate(fs): add(tone(f, 0.45, 0.17, 6), t0 + k * 0.12, pan=0.3)
add(tone(2400, 0.12, 0.2, 20), 1.2, pan=0.3)              # scanner beep
add(tone(2400, 0.12, 0.2, 20), 1.35, pan=0.3)
add(noise_sweep(0.25, 600, 1800, 0.08), 3.6)               # rustle into bag
err(4.0); add(noise_sweep(0.3, 3000, 300, 0.2), 4.0)
add(noise_sweep(0.25, 600, 1800, 0.08), 6.2)
ding(6.75, (988, 784))                                       # 'please place item'
add(noise_sweep(0.25, 600, 1800, 0.08), 7.4)
err(7.7)
add(noise_sweep(0.4, 300, 2500, 0.2), 8.15)               # rage whoosh
for k in range(3): add(tone(500 + k * 0, 0.15, 0.15, 10), 8.25 + k * 0.17)
for tk in np.arange(9.4, 11.4, 1 / 3): add(tone(880, 0.12, 0.1, 15), tk, pan=0.4)  # help light alarm
for tk in np.arange(11.45, 13.2, 0.42): add(tone(300, 0.05, 0.12, 50), tk, pan=-0.3)  # line foot taps
for tk in np.arange(13.2, 14.0, 0.27): add(hat(0.1, 0.06), tk, pan=0.4)             # employee footsteps
add(tone(1800, 0.05, 0.2, 60), 14.2, pan=0.3)              # tap
ding(14.3, (1046, 1319, 1568))                             # success chime
t = tt(0.5); add(0.1 * np.sin(2 * np.pi * 220 * t * (1 - 0.3 * t)) * np.exp(-t * 3), 15.5)  # deflating sigh tone
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
