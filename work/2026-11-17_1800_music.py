"""Soundtrack v2: lo-fi beat -> tense panic beat -> sad lo-fi outro, plus SFX."""
import numpy as np, wave
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


import sys
T = 19.4
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
def addm(buf, sig, t):
    i = int(t * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i + n] += sig[:n]

def alarm(t, d=0.9, amp=0.13):  # beeping digital alarm
    k = 0
    while k * 0.16 < d:
        add(tone(2100, 0.08, amp, dec=4) + tone(4200, 0.08, amp * 0.3, dec=6), t + k * 0.16, pan=-0.4); k += 1
def slap(t, amp=0.5):
    n = int(SR * 0.09); add(lp(rng.uniform(-1, 1, n), 3000) * np.exp(-tt(0.09) * 40) * amp + kick(0.4)[:n], t, pan=-0.3)
def scratch(t):
    n = int(SR * 0.4); s = np.sin(2 * np.pi * np.cumsum(np.linspace(1500, 100, n)) / SR) * rng.uniform(0.5, 1, n)
    add(lp(s, 3500) * np.linspace(0.6, 0, n), t)

# ---------- sleepy lo-fi in A, 0 -> 8.4 ----------
bpm = 78; b = 60 / bpm; sw = b * 0.6
chords = [[57, 61, 64, 68], [54, 57, 61, 64], [50, 54, 57, 61], [52, 56, 59, 62]]  # Amaj7 F#m7 Dmaj7 E7
roots = [45, 42, 38, 40]
mels = [[76, 73], [73, 69, 71], [69, 66], [68, 71, 74]]
lofi = np.zeros(len(L)); bar = 0; t0 = 0.0
while t0 < 8.4:
    ch = chords[bar % 4]
    for st in (0, b * 2 + sw):
        for k, m in enumerate(ch): addm(lofi, rhodes(mtof(m), 1.8, 0.1), t0 + st + k * 0.015)
    addm(lofi, bass(mtof(roots[bar % 4]), b * 2.5), t0); addm(lofi, bass(mtof(roots[bar % 4] + 7), b * 1.2), t0 + b * 2.5)
    for beat in range(4):
        tb = t0 + beat * b
        if beat in (0, 2): addm(lofi, kick(0.6), tb)
        if beat in (1, 3): addm(lofi, snare(0.22), tb)
        addm(lofi, hat(0.08), tb); addm(lofi, hat(0.05), tb + sw)
    for j, m in enumerate(mels[bar % 4]): addm(lofi, bell(mtof(m), 1.4, 0.07), t0 + b * (0.5 + j * 1.3))
    bar += 1; t0 += 4 * b
lofi = lp(lofi, 3800)
env = np.ones(len(L)); env[int(5.6 * SR):int(8.4 * SR)] = 0.75
env[int(8.4 * SR):] = 0; env[int(8.2 * SR):int(8.4 * SR)] = np.linspace(0.75, 0, int(0.2 * SR) + 1)[:int(8.4 * SR) - int(8.2 * SR)]
lofi *= env; L += lofi; R += lofi

# alarms + slaps
alarm(0.05, 1.3); slap(1.4)
alarm(3.2, 0.85); slap(4.1)
per = 2.8 / 9
for k in range(9):
    alarm(5.6 + per * k, per * 0.55, 0.1); slap(5.6 + per * (k + 0.6), 0.35)
# snore
for st in (2.0, 4.6, 7.0):
    n = int(SR * 0.6); s = lp(rng.uniform(-1, 1, n), 350) * np.sin(np.linspace(0, np.pi, n)) * 0.5
    add(s, st)

# ---------- wake up: silence, eye creak, then STING 9.5 ----------
add(tone(mtof(74), 0.6, 0.07, dec=3), 8.6); add(tone(mtof(75), 0.6, 0.07, dec=3), 9.0)
scratch(9.45)
pb = 60 / 172; s16 = pb / 4
for j, m in enumerate((45, 46, 45, 46)): add(saw(mtof(m), 0.3, 0.2, cut=1200), 9.5 + j * 0.45)
add(noise_sweep(1.6, 300, 6000, 0.12), 9.8)
for k in range(8): add(kick(0.7), 9.5 + k * 0.23)

# ---------- speedrun 11.4 -> 14.8 : A minor, 172 bpm ----------
i = 0; ost = [45, 57, 45, 52, 45, 55, 45, 60]
while 11.4 + i * s16 < 14.8:
    tb = 11.4 + i * s16; kk = (tb - 11.4) / 3.4
    add(saw(mtof(ost[i % 8]), s16 * 0.9, 0.14, cut=900 + 2500 * kk), tb)
    if i % 4 == 0: add(kick(0.8), tb)
    if i % 8 == 4: add(snare(0.36), tb)
    add(hat(0.08, 0.03), tb, pan=0.3)
    if i % 16 == 0: add(saw(mtof(69 + (i // 16) % 3 * 2), pb * 1.5, 0.12, cut=2500), tb)
    i += 1
for k in range(12):  # toothbrush scrub
    n = int(SR * 0.07); add(bp(rng.uniform(-1, 1, n), 3000, 9000) * 0.1, 11.5 + k * 0.14, pan=0.2)
add(noise_sweep(0.6, 500, 7000, 0.12), 14.2)

# ---------- saturday reveal 14.8 ----------
add(tone(mtof(88), 0.2, 0.12, dec=8), 14.85)  # phone tap
scratch(15.3)
for j in range(3): add(tone(mtof(76 - j * 2), 0.18, 0.12, dec=9), 16.1 + j * 0.25)  # ...
add(tone(2000, 0.02, 0.1, 50), 16.0); add(tone(2000, 0.02, 0.1, 50), 16.35)  # crickets
# flop + dreamy outro
add(kick(0.7), 17.2); add(noise_sweep(0.4, 800, 200, 0.12), 17.15)
out = np.zeros(len(L))
for j, m in enumerate((69, 73, 76, 81, 80, 76)): addm(out, bell(mtof(m), 1.6, 0.09), 17.3 + j * 0.2)
for k, m in enumerate((57, 61, 64, 68, 71)): addm(out, rhodes(mtof(m), 2.4, 0.08), 17.3 + k * 0.03)
addm(out, bass(mtof(33), 2.0), 17.3)
L += out; R += out

def verb(x):
    y = x.copy()
    for dly, g in ((0.029, 0.3), (0.043, 0.25), (0.067, 0.2), (0.109, 0.15)):
        n = int(dly * SR); y[n:] += x[:-n] * g
    return y
L, R = verb(L), verb(R)
end = np.ones(len(L)); end[-int(SR * 0.4):] = np.linspace(1, 0, int(SR * 0.4))
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.3) * 0.89 * end, np.tanh(R / peak * 1.3) * 0.89 * end
st = np.empty(len(L) * 2); st[0::2] = L; st[1::2] = R
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
