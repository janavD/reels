"""Extra reel 2 soundtrack: 3am cringe memory. Music-box lullaby -> record scratch -> frantic beat -> lullaby -> alarm + bouncy outro."""
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
T = 16.8
L = np.zeros(int(SR * T)); R = np.zeros(int(SR * T))
def addm(buf, sig, t):
    i = int(t * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i + n] += sig[:n]

# ---------- lullaby (A major, music box, 72 bpm): 0 -> 4.75 and 9.4 -> 13.0 ----------
def lullaby(buf, a, b, tr=0):
    bpm = 72; bt = 60 / bpm
    mel = [76, 73, 69, 73, 76, 81, 80, 76, 78, 74, 71, 74, 76, 73, 69, 68]
    prog = [(57, [69, 73, 76]), (54, [66, 69, 73]), (50, [66, 69, 74]), (52, [68, 71, 76])]
    t0 = a; i = 0
    while t0 < b:
        if i % 4 == 0:
            r, ch = prog[(i // 4) % 4]
            addm(buf, bass(mtof(r + tr), bt * 3.5, 0.16), t0)
            for k, m in enumerate(ch): addm(buf, rhodes(mtof(m + tr - 12), 2.4, 0.05), t0 + k * 0.03)
        addm(buf, bell(mtof(mel[i % len(mel)] + tr + 12), 1.3, 0.07), t0)
        if i % 2: addm(buf, bell(mtof(mel[i % len(mel)] + tr + 7), 0.8, 0.025), t0 + bt * 0.5)
        t0 += bt; i += 1

mus = np.zeros(len(L))
lullaby(mus, 0.0, 4.75)
seg2 = np.zeros(len(L)); lullaby(seg2, 9.4, 13.0, tr=-1)   # slightly "off" second time
fade = np.ones(len(L)); i0, i1 = int(11.3 * SR), int(13.0 * SR); fade[i0:i1] = np.linspace(1, 0.3, i1 - i0)
mus += seg2 * fade
cut = np.ones(len(L)); cut[int(4.75 * SR):int(9.4 * SR)] = 0; cut[int(13.0 * SR):] = 0
mus *= lp(cut, 40)

# ---------- frantic cringe beat (D minor, 160 bpm): 4.9 -> 9.4 ----------
bpm = 160; b = 60 / bpm; t0 = 4.9; n = 0
riff = [62, 65, 62, 69, 68, 65, 62, 61]
while t0 < 9.35:
    if n % 2 == 0: addm(mus, kick(0.7), t0)
    else: addm(mus, snare(0.3), t0)
    addm(mus, hat(0.08), t0); addm(mus, hat(0.05), t0 + b / 2)
    addm(mus, bass(mtof(riff[n % 8] - 24), b * 0.9, 0.26), t0)
    addm(mus, saw(mtof(riff[n % 8]), b * 0.8, 0.09, cut=1600), t0)
    t0 += b; n += 1

# ---------- bouncy outro (G major, 100 bpm): 14.3 -> end ----------
bpm = 100; b = 60 / bpm; t0 = 14.3; n = 0
for (r, ch) in [(43, [59, 62, 67]), (40, [59, 64, 67]), (48, [60, 64, 67]), (50, [62, 66, 69])]:
    for k, m in enumerate(ch): addm(mus, rhodes(mtof(m), 1.4, 0.07), t0 + k * 0.012)
    addm(mus, bass(mtof(r), b * 1.6, 0.22), t0); addm(mus, kick(0.5), t0); addm(mus, snare(0.18), t0 + b)
    addm(mus, hat(0.06), t0 + b / 2); addm(mus, hat(0.06), t0 + b * 1.5)
    addm(mus, bell(mtof(ch[-1] + 12), 0.9, 0.06), t0 + b * 0.5)
    t0 += 2 * b
mus = lp(mus, 5000)
L += mus; R += mus

# ---------- SFX ----------
def pop(t, f=880): add(tone(f, 0.12, 0.12, dec=18), t); add(tone(f * 2, 0.08, 0.04, dec=30), t)
def scratch(t):
    d = 0.35; x = tt(d); f = 300 + 900 * np.abs(np.sin(2 * np.pi * 5 * x))
    add(0.35 * bp(rng.uniform(-1, 1, len(x)), 500, 4000) * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 5), t)
def boing(t):
    d = 0.5; x = tt(d); f = 180 + 120 * np.sin(2 * np.pi * 9 * x) * np.exp(-x * 4)
    add(0.3 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 5), t)

pop(3.0, 660)                                           # cloud appears
for k in range(5): add(tone(mtof(84 + k), 0.06, 0.05, dec=30), 3.4 + k * 0.05, pan=-0.3)   # waiter line
add(tone(mtof(91), 0.15, 0.12, dec=10), 4.0, pan=0.3)  # "you too!"
add(saw(mtof(50), 0.6, 0.12, cut=700), 4.15)           # cringe low note
scratch(4.75); boing(4.78)                              # eyes snap open
for k in range(3): pop(6.55 + k * 0.25, 520 + k * 120)  # AAA pops
add(noise_sweep(0.8, 3000, 300, 0.06), 8.6)
pop(9.55, 700)                                          # second cloud
for k in range(4): add(tone(mtof(86 - k), 0.06, 0.05, dec=30), 9.9 + k * 0.05)   # heyyy
add(bell(mtof(88), 0.5, 0.06), 10.3)                    # wave back
for j, m in enumerate((58, 57, 56, 55)):                # sad trombone on "not at me"
    d = 0.28 if j < 3 else 0.7
    add(saw(mtof(m), d, 0.14, cut=1100) * (1 + 0.3 * np.sin(2 * np.pi * 6 * tt(d))), 10.85 + j * 0.27)
add(lp(rng.uniform(-1, 1, int(SR * 0.4)), 1200) * np.linspace(0.15, 0, int(SR * 0.4)), 11.3)   # blanket rustle
# alarm 13.2 -> 15.4
t0 = 13.2
while t0 < 15.35:
    for k in range(4): add(tone(2000, 0.06, 0.13, dec=8) + tone(4000, 0.06, 0.03, dec=8), t0 + k * 0.09, pan=-0.5)
    t0 += 0.55
pop(14.0, 760)
for j, m in enumerate((79, 83, 86)): add(bell(mtof(m), 0.8, 0.07), 14.35 + j * 0.1)   # goodnight :)

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
