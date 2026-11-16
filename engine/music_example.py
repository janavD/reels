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

# ---------- section 1: lo-fi, 0 -> 11.2 s ----------
bpm = 84; b = 60 / bpm; sw = b * 0.58  # swung 8th
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm7 Cmaj7
roots = [41, 40, 38, 36]
lofi = np.zeros(len(L))
def addm(buf, sig, t):
    i = int(t * SR); n = min(len(sig), len(buf) - i)
    if n > 0: buf[i:i + n] += sig[:n]
bar = 0; t0 = 0.0
while t0 < 11.2:
    ch = chords[bar % 4]
    for st in (0, b * 1 + sw):
        for k, m in enumerate(ch): addm(lofi, rhodes(mtof(m), 1.6), t0 + st + k * 0.012)
    addm(lofi, bass(mtof(roots[bar % 4]), b * 2.2), t0); addm(lofi, bass(mtof(roots[bar % 4] + 7), b * 1.2), t0 + b * 2.5)
    for beat in range(4):
        tb = t0 + beat * b
        if beat in (0, 2): addm(lofi, kick(), tb)
        if beat == 1: addm(lofi, kick(0.45), tb + sw)
        if beat in (1, 3): addm(lofi, snare(), tb)
        addm(lofi, hat(), tb); addm(lofi, hat(0.07), tb + sw)
    mel = [[72, 76, 79], [74, 71], [69, 72, 74], [67, 64, 67]][bar % 4]
    for j, m in enumerate(mel): addm(lofi, bell(mtof(m)), t0 + b * (0.5 + j * 1.15))
    bar += 1; t0 += 4 * b
lofi = lp(lofi, 4200)
crackle = np.zeros(len(L)); idx = rng.integers(0, int(11.2 * SR), 260); crackle[idx] = rng.uniform(-0.25, 0.25, 260)
lofi += lp(crackle, 5000) + lp(rng.normal(0, 0.006, len(L)), 3000)
fade = np.ones(len(L)); e = int(11.15 * SR); fade[e:] = 0
lofi *= fade
L += lofi; R += lofi

# ---------- SFX in section 1 ----------
add(bell(mtof(88), 0.8, 0.12) + bell(mtof(95), 0.8, 0.08), 1.2, pan=0.4)                # wink sparkle
for i in range(5): add(tone(900 + i * 150, 0.05, 0.05), 3.4 + i * 0.09)                  # laugh-ish blips
add(noise_sweep(0.25, 3000, 600, 0.12), 7.05)                                          # phone slipping
add(tone(160, 0.3, 0.6, dec=14), 7.25); add(bp(rng.uniform(-1, 1, int(SR * 0.3)), 300, 2500) * np.exp(-tt(0.3) * 25) * 0.4, 7.25)  # BONK
for i in range(3): add(tone(mtof(84 - i * 5), 0.25, 0.12, dec=8), 7.33 + i * 0.12)       # dizzy stars
# alarm 8.9 -> 9.9 then slap
t = tt(1.0); ring = 0.18 * np.sign(np.sin(2 * np.pi * 2100 * t)) * (np.sin(2 * np.pi * 14 * t) > 0)
add(lp(ring, 6000), 8.9, pan=-0.5)
add(bp(rng.uniform(-1, 1, int(SR * 0.15)), 400, 4000) * np.exp(-tt(0.15) * 30) * 0.9, 9.9); add(tone(120, 0.15, 0.5, 20), 9.9)
# record scratch into panic
n = int(SR * 0.35); scr = np.sin(2 * np.pi * np.cumsum(np.linspace(1400, 120, n)) / SR) * rng.uniform(0.5, 1, n)
add(lp(scr, 3500) * np.linspace(0.5, 0, n), 11.0)

# ---------- section 2: panic, 11.2 -> 16.75 ----------
pb = 60 / 160; s16 = pb / 4
t0 = 11.2; i = 0
ost = [38, 38, 50, 38, 41, 38, 49, 38]  # D minor driving 16ths
while t0 + i * s16 < 16.7:
    tb = t0 + i * s16; k = (tb - 11.2) / 5.5
    lift = int(k * 4)  # rises a semitone per ~1.4s
    add(saw(mtof(ost[i % 8] + lift), s16 * 0.9, 0.16, cut=500 + 2500 * k), tb)
    if i % 4 == 0: add(kick(0.8), tb)
    if i % 8 == 4: add(snare(0.38), tb)
    add(hat(0.06 + 0.05 * (i % 2 == 0), 0.03), tb, pan=0.3)
    if i % 16 == 0:
        for m in (62, 65, 69): add(saw(mtof(m + lift), pb * 3.5, 0.06, cut=1800), tb, pan=-0.2)
    i += 1
tk = 11.3
while tk < 16.6:
    add(tone(2400, 0.02, 0.22, dec=60), tk, pan=0.6); tk += max(0.12, 0.42 - (tk - 11.3) * 0.055)   # clock ticks speeding up
for _ in range(140):
    tb = rng.uniform(11.3, 16.6); m = int(SR * 0.02)
    add(bp(rng.uniform(-1, 1, m), 1500, 6000) * np.exp(-np.arange(m) / 140) * 0.35, tb, pan=rng.uniform(-0.5, 0.5))  # typing
for hb in np.arange(11.4, 16.6, 0.55): add(tone(58, 0.18, 0.55, 12), hb); add(tone(52, 0.18, 0.4, 12), hb + 0.16)
add(noise_sweep(1.6, 400, 9000, 0.18), 15.15)                                          # riser

# ---------- slam + success + sad outro ----------
add(kick(1.0), 16.75); add(tone(70, 0.6, 0.6, 5), 16.75); add(lp(rng.uniform(-1, 1, int(SR * 0.4)), 1500) * np.exp(-tt(0.4) * 10) * 0.5, 16.75)
for j, m in enumerate((84, 88, 91, 96)): add(bell(mtof(m), 1.4, 0.13), 16.82 + j * 0.07, pan=0.2)
add(noise_sweep(1.2, 600, 3000, 0.08), 17.5)                                            # soul whoosh
sad = [[50, 53, 57, 60], [46, 50, 53, 57]]  # Dm7 -> Bbmaj7
out = np.zeros(len(L))
for j, ch in enumerate(sad):
    for k2, m in enumerate(ch): addm(out, rhodes(mtof(m - 12 + 12), 2.4, 0.1), 17.45 + j * 1.25 + k2 * 0.03)
    addm(out, bass(mtof(ch[0] - 12), 1.3, 0.25), 17.45 + j * 1.25)
for j, (f0, f1) in enumerate(((330, 320), (311, 300), (294, 282), (277, 240))):        # bwomp bwomp bwomp bwooomp
    d = 0.42 if j < 3 else 1.1; t = tt(d); f = np.linspace(f0, f1, len(t)) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    sig = sum(np.sin(ph * h) / h ** 1.3 for h in range(1, 7)) * np.minimum(1, t * 25) * np.minimum(1, (d - t) * 12) * 0.13
    addm(out, lp(sig, 1800), 17.55 + j * 0.45)
out = lp(out, 3500)
L += out; R += out

# ---------- reverb-ish, master ----------
def verb(x):
    y = x.copy()
    for dly, g in ((0.031, 0.32), (0.047, 0.27), (0.071, 0.22), (0.113, 0.16)):
        n = int(dly * SR); y[n:] += x[:-n] * g
    return y
L, R = verb(L), verb(R)
end = np.ones(len(L)); end[-int(SR * 0.4):] = np.linspace(1, 0, int(SR * 0.4))
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.3) * 0.89 * end, np.tanh(R / peak * 1.3) * 0.89 * end
st = np.empty(len(L) * 2); st[0::2] = L; st[1::2] = R
w = wave.open("music_v2.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
