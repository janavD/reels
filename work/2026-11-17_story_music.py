"""Soundtrack for the breakfast-in-bed story reel: bouncy morning lo-fi (A major, 96bpm) -> tense smoke-alarm
section -> awkward silence + crickets -> warm wholesome outro; SFX synced; narration on top with music ducked to ~35%."""
import numpy as np, wave, sys
from scipy.signal import lfilter, butter, resample_poly

SR = 44100; T = 67.0
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

def pluck(f, d=0.5, amp=0.1):
    t = tt(d); env = np.minimum(1, t * 400) * np.exp(-t * 9)
    return amp * env * (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 14) + 0.25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 20))

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

def gliss(f0, f1, d, amp=0.15):
    t = tt(d); f = np.geomspace(f0, f1, len(t)); ph = 2 * np.pi * np.cumsum(f) / SR
    return amp * np.sin(ph) * np.minimum(1, t * 50) * np.minimum(1, (d - t) * 20)

music = np.zeros(len(L))
def addm(sig, t, gain=1.0):
    i = int(t * SR); n = min(len(sig), len(music) - i)
    if n > 0: music[i:i + n] += sig[:n] * gain

# ---------- section A: bouncy morning, 0 -> 24.5 (A major, 96 bpm) ----------
bpm = 96; b = 60 / bpm; sw = b * 0.56
chA = [[57, 61, 64, 68], [54, 57, 61, 64], [50, 54, 57, 61], [52, 56, 59, 62]]   # Amaj7 F#m7 Dmaj7 E7
rtA = [45, 42, 38, 40]
melA = [[76, 73, 71, 73], [69, 71, 73], [74, 73, 69, 66], [68, 71, 74]]
bar = 0; t0 = 0.0
while t0 < 24.3:
    ch = chA[bar % 4]
    for st in (0, b * 1 + sw, b * 2 + sw):
        for k, m in enumerate(ch): addm(rhodes(mtof(m), 1.2, 0.09), t0 + st + k * 0.01)
    addm(bass(mtof(rtA[bar % 4]), b * 1.4), t0); addm(bass(mtof(rtA[bar % 4] + 7), b * 0.8), t0 + b * 1.5)
    addm(bass(mtof(rtA[bar % 4] + 12), b * 0.8), t0 + b * 2.5); addm(bass(mtof(rtA[bar % 4] + 7), b * 0.8), t0 + b * 3.5)
    for beat in range(4):
        tb = t0 + beat * b
        if beat in (0, 2): addm(kick(0.6), tb)
        if beat in (1, 3): addm(snare(0.25), tb)
        addm(hat(0.08), tb); addm(hat(0.05), tb + sw)
    for j, m in enumerate(melA[bar % 4]): addm(pluck(mtof(m), 0.5, 0.1), t0 + b * (0.5 + j * 0.9))
    bar += 1; t0 += 4 * b
fa = np.ones(len(music)); i0, i1 = int(24.0 * SR), int(24.6 * SR); fa[i0:i1] = np.linspace(1, 0, i1 - i0); fa[i1:] = 0
music *= fa

# ---------- section B: tense alarm, 24.5 -> 30.6 ----------
pb = 60 / 150; s16 = pb / 4
tb0 = 24.5; i = 0
ost = [45, 45, 57, 45, 48, 45, 56, 45]
B = np.zeros(len(music))
def addB(sig, t):
    j = int(t * SR); n = min(len(sig), len(B) - j)
    if n > 0: B[j:j + n] += sig[:n]
while tb0 + i * s16 < 30.55:
    tb = tb0 + i * s16; k = (tb - 24.5) / 6.0
    addB(saw(mtof(ost[i % 8] + int(k * 3)), s16 * 0.9, 0.13, cut=600 + 2200 * k), tb)
    if i % 4 == 0: addB(kick(0.75), tb)
    if i % 8 == 4: addB(snare(0.32), tb)
    addB(hat(0.05, 0.03), tb)
    i += 1
music += B

# ---------- section C: awkward, 30.6 -> 46 (sparse) ----------
for j, m in enumerate((69, 0, 68, 0, 66, 0, 64)):
    if m: addm(pluck(mtof(m), 0.6, 0.06), 31.6 + j * 0.55)
for j, m in enumerate((64, 63)):
    addm(rhodes(mtof(m - 12), 2.0, 0.05), 32.5 + j * 2.0)
# warm pad under mom's line only lightly
for j, ch in enumerate(([57, 60, 64], [56, 60, 63])):
    for m in ch: addm(rhodes(mtof(m), 2.5, 0.04), 37.0 + j * 2.4)

# ---------- section D: laughter + wholesome outro, 46 -> 67 (D major, 88 bpm) ----------
bpm2 = 88; b2 = 60 / bpm2; sw2 = b2 * 0.56
chD = [[50, 54, 57, 61], [55, 59, 62, 66], [47, 50, 54, 57], [52, 55, 59, 62]]  # Dmaj7 Gmaj7 Bm7 Em7
rtD = [38, 43, 35, 40]
melD = [[78, 76, 74], [74, 76, 78, 81], [78, 74, 71], [73, 74, 76]]
bar = 0; t0 = 46.2
while t0 < 64.4:
    ch = chD[bar % 4]
    full = t0 > 52.0
    for st in (0, b2 + sw2) if full else (0,):
        for k, m in enumerate(ch): addm(rhodes(mtof(m), 1.8, 0.1), t0 + st + k * 0.015)
    addm(bass(mtof(rtD[bar % 4]), b2 * 2.2, 0.24), t0); addm(bass(mtof(rtD[bar % 4] + 7), b2 * 1.2, 0.2), t0 + b2 * 2.5)
    if full:
        for beat in range(4):
            tb = t0 + beat * b2
            if beat in (0, 2): addm(kick(0.5), tb)
            if beat in (1, 3): addm(snare(0.2), tb)
            addm(hat(0.06), tb); addm(hat(0.04), tb + sw2)
        for j, m in enumerate(melD[bar % 4]): addm(bell(mtof(m), 1.0, 0.08), t0 + b2 * (0.5 + j * 1.1))
    bar += 1; t0 += 4 * b2
fd = np.ones(len(music)); i0, i1 = int(64.3 * SR), int(64.9 * SR); fd[i0:i1] = np.linspace(1, 0.0, i1 - i0); fd[i1:] = 0
music *= fd
# final chord after the plop
for k, m in enumerate((62, 66, 69, 73, 74)): addm(rhodes(mtof(m), 2.0, 0.09), 65.5 + k * 0.03)
addm(bell(mtof(86), 1.4, 0.08), 65.6)

crackle = np.zeros(len(music)); idx = rng.integers(0, len(music), 900); crackle[idx] = rng.uniform(-0.2, 0.2, 900)
music = lp(music, 5000) + lp(crackle, 5000) * 0.6

# ---------- SFX ----------
for k in range(18):  # whisking
    add(bp(rng.uniform(-1, 1, int(SR * 0.08)), 2000, 7000) * np.exp(-tt(0.08) * 30) * 0.12, 0.4 + k * 0.17, pan=-0.4)
add(bell(mtof(93), 0.8, 0.1) + bell(mtof(100), 0.8, 0.06), 3.9, pan=0.3)                    # sparkle
add(lp(rng.uniform(-1, 1, int(SR * 1.6)), 1200) * 0.05, 7.4, pan=0.3)                      # sizzle
add(noise_sweep(0.5, 600, 5000, 0.18), 9.2)                                                 # flip whoosh
add(gliss(300, 1400, 0.5, 0.08), 9.2)
add(tone(140, 0.25, 0.6, 18), 9.8); add(bp(rng.uniform(-1, 1, int(SR * 0.25)), 200, 1800) * np.exp(-tt(0.25) * 22) * 0.6, 9.8)   # SPLAT
for k in range(6): add(tone(mtof(60 - k), 0.12, 0.04, 20), 11.0 + k * 0.6)                  # drip blips
add(lp(rng.uniform(-1, 1, int(SR * 1.0)), 1500) * np.linspace(0, 0.08, int(SR * 1.0)), 13.0)  # pour
add(lp(rng.uniform(-1, 1, int(SR * 2.0)), 1500) * 0.05, 16.0, pan=0.3)                     # sizzle 2
add(noise_sweep(0.5, 300, 2500, 0.3), 18.5)                                                 # fire ignite
add(lp(rng.uniform(-1, 1, int(SR * 1.8)), 900) * 0.08 * (1 + 0.5 * np.sin(2 * np.pi * 7 * tt(1.8))), 18.9)  # crackle
add(lp(rng.uniform(-1, 1, int(SR * 0.6)), 2500) * np.hanning(int(SR * 0.6)) * 0.3, 20.3)     # blow
for j, m in enumerate((72, 76, 79)): add(bell(mtof(m), 0.6, 0.08), 21.0 + j * 0.1)          # phew ding
add(noise_sweep(0.6, 200, 4000, 0.45), 21.7); add(tone(80, 0.5, 0.5, 6), 21.7)               # FWOOSH relight
add(lp(rng.uniform(-1, 1, int(SR * 2.6)), 900) * 0.08, 22.2)
# smoke alarm: 3 fast chirps repeating, 24.6 -> 35
ta = 24.6
while ta < 35.0:
    for q in range(3):
        add(0.12 * np.sign(np.sin(2 * np.pi * 3200 * tt(0.11))) * np.minimum(1, tt(0.11) * 200), ta + q * 0.18, pan=-0.4)
    ta += 0.9
for k in range(14): add(noise_sweep(0.12, 800, 3000, 0.08), 26.0 + k * 0.17)                # fanning
add(lp(rng.uniform(-1, 1, int(SR * 0.6)), 3000) * np.exp(-tt(0.6) * 6) * 0.8, 30.6); add(kick(0.9), 30.6)   # POOF
for k in range(4): add(bp(rng.uniform(-1, 1, int(SR * 0.12)), 500, 2500) * np.exp(-tt(0.12) * 25) * 0.3, 32.0 + k * 0.7)  # coughs
t_c = np.arange(int(SR * 2.4)) / SR
creak = 0.07 * np.sin(2 * np.pi * np.cumsum(220 + 60 * np.sin(2 * np.pi * 1.3 * t_c)) / SR) * np.minimum(1, t_c * 5) * np.minimum(1, (0.9 - t_c).clip(0) * 6)
add(lp(creak, 2000), 36.8, pan=-0.6)                                                        # door creak
for k in range(10):                                                                         # crickets in the silence
    tc = 41.4 + k * 0.42
    add(0.035 * np.sin(2 * np.pi * 4300 * tt(0.12)) * (np.sin(2 * np.pi * 40 * tt(0.12)) > 0), tc, pan=0.5)
add(tone(mtof(72), 0.15, 0.08, 14), 44.9); add(tone(mtof(76), 0.15, 0.08, 14), 45.05)        # smile twitch
for k in range(9): add(tone(700 + (k % 3) * 120, 0.08, 0.05, 25), 46.4 + k * 0.22)            # laugh blips
add(noise_sweep(0.4, 1500, 300, 0.12), 47.3); add(tone(110, 0.2, 0.4, 16), 48.2)             # slide down + bump
for k in range(10): add(bp(rng.uniform(-1, 1, int(SR * 0.04)), 2500, 7000) * 0.06, 52.8 + k * 0.85, pan=0.2)  # crunchy spoons
add(gliss(1800, 250, 0.55, 0.14), 64.55)                                                    # falling slide whistle
add(tone(120, 0.3, 0.7, 14), 65.1); add(bp(rng.uniform(-1, 1, int(SR * 0.3)), 200, 1600) * np.exp(-tt(0.3) * 20) * 0.7, 65.1)  # PLOP
for k in range(6): add(tone(750 + (k % 2) * 150, 0.08, 0.05, 25), 65.5 + k * 0.2)

# ---------- reverb-ish on music, then voice + duck ----------
def verb(x):
    y = x.copy()
    for dly, g in ((0.031, 0.3), (0.047, 0.25), (0.071, 0.2), (0.113, 0.14)):
        n = int(dly * SR); y[n:] += x[:-n] * g
    return y
music = verb(music)
L += music; R += music

VO = [(1, 0.5), (2, 7.6), (3, 16.6), (4, 25.0), (5, 37.0), (6, 46.3), (7, 53.0), (8, 61.8)]
voice = np.zeros(len(L))
for n, t0 in VO:
    w = wave.open(f"work/vo/l{n}.wav"); sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
    if w.getnchannels() == 2: x = x[::2]
    x = resample_poly(x, SR, sr)
    j = int(t0 * SR); m = min(len(x), len(voice) - j); voice[j:j + m] += x[:m]
# duck envelope
active = np.zeros(len(L))
for n, t0 in VO:
    w = wave.open(f"work/vo/l{n}.wav"); d = w.getnframes() / w.getframerate()
    active[int((t0 - 0.15) * SR):int((t0 + d + 0.2) * SR)] = 1
k = int(0.15 * SR); env = np.convolve(active, np.ones(k) / k, mode="same")
duck = 1 - 0.65 * env
L *= duck; R *= duck
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.2) * 0.42, np.tanh(R / peak * 1.2) * 0.42
vp = np.abs(voice).max(); voice = voice / vp * 0.85
L += voice; R += voice
end = np.ones(len(L)); end[-int(SR * 0.5):] = np.linspace(1, 0, int(SR * 0.5))
pk = max(np.abs(L).max(), np.abs(R).max(), 1.0)
L, R = L / pk * 0.95 * end, R / pk * 0.95 * end
st = np.empty(len(L) * 2); st[0::2] = L; st[1::2] = R
out = sys.argv[1] if len(sys.argv) > 1 else "final_audio.wav"
w = wave.open(out, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
