"""Cut vertical clips with a hook title and word captions from a horizontal source video."""
import json, subprocess, os, sys

SRC = "src/vlog.mp4"
WORDS = json.load(open("transcript.json"))["words"]
OUT = "out"; os.makedirs(OUT, exist_ok=True); os.makedirs("tmp", exist_ok=True)

CLIPS = [
    ("01_indonesian_speech", [(43.0, 52.2), (318.5, 358.0)],
     "Speed promised a speech in\\NIndonesian if he won...\\Nand he actually did it"),
    ("02_fit_check", [(56.0, 76.5)],
     "Speed's fit for the\\NStreamer Awards"),
    ("03_best_irl", [(180.0, 206.0), (220.0, 242.0)],
     "Speed wins Best IRL Streamer\\Nand thanks his whole team"),
    ("04_three_peat", [(297.0, 330.0), (370.5, 381.0)],
     "Streamer of the Year...\\N3 TIMES IN A ROW"),
    ("05_selfie", [(381.0, 398.0)],
     "Fan asks Speed for a selfie\\Nright after he wins"),
    ("06_proud", [(403.0, 423.0)],
     "\"I'm genuinely proud\\Nof you bro\""),
    ("07_advice", [(437.0, 455.0)],
     "Speed's advice to anyone\\Nchasing a dream"),
    ("08_fans", [(475.0, 502.5)],
     "Speed to his fans:\\N\"Y'all actually keep me going\""),
]

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def captions(segs):
    """Group words into 1-3 word chunks, mapped onto the clip's own timeline."""
    out, offset = [], 0.0
    for (a, b) in segs:
        ws = [w for w in WORDS if a <= w["start_ms"] / 1000 < b]
        chunk = []
        def flush():
            if chunk:
                st = chunk[0]["start_ms"] / 1000 - a + offset
                en = min(chunk[-1]["end_ms"] / 1000, b) - a + offset
                out.append((st, max(en, st + 0.35), " ".join(w["text"] for w in chunk).upper()))
                chunk.clear()
        for w in ws:
            if chunk and (w["start_ms"] - chunk[-1]["end_ms"] > 450 or len(chunk) >= 3):
                flush()
            chunk.append(w)
            if w["text"].endswith((".", "?", "!", ",")): flush()
        flush()
        offset += b - a
    # stop each caption when the next starts
    for i in range(len(out) - 1):
        st, en, tx = out[i]
        out[i] = (st, min(en + 0.25, out[i + 1][0]), tx)
    return out

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Poppins,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,6,0,5,60,60,0,1
Style: Cap,Poppins,74,&H0000E5FF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1
Style: Tag,Poppins,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def build(name, segs, hook):
    dur = sum(b - a for a, b in segs)
    ass = HEADER
    ass += f"Dialogue: 0,{ts(0)},{ts(dur)},Hook,,0,0,0,,{{\\pos(540,300)}}{hook}\n"
    ass += f"Dialogue: 0,{ts(0)},{ts(dur)},Tag,,0,0,0,,{{\\pos(540,1640)\\alpha&H40&}}@typeshi707\n"
    for st, en, tx in captions(segs):
        ass += f"Dialogue: 1,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\pos(540,1440)\\fscx80\\fscy80\\t(0,90,\\fscx100\\fscy100)}}{tx}\n"
    open(f"tmp/{name}.ass", "w").write(ass)
    # trim + join segments, then lay out: blurred full-frame background, 4:3 centre crop on top
    inputs, parts = [], []
    for i, (a, b) in enumerate(segs):
        inputs += ["-ss", str(a), "-t", str(b - a), "-i", SRC]
        parts.append(f"[{i}:v]setpts=PTS-STARTPTS[v{i}];[{i}:a]asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.05,afade=t=out:st={b - a - 0.08}:d=0.08[a{i}]")
    n = len(segs)
    cat = "".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    fc = ";".join(parts) + ";" + cat + ";" + (
        "[v]split[bg][fg];"
        "[bg]scale=-2:1920,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.25[bgb];"
        "[fg]crop=1440:1080,scale=1080:810[fgs];"
        "[bgb][fgs]overlay=0:555,"
        f"ass=tmp/{name}.ass:fontsdir=/usr/share/fonts/truetype/google-fonts,format=yuv420p[vo]")
    tmp, final = f"{OUT}/{name}.tmp.mp4", f"{OUT}/{name}.mp4"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc,
                        "-map", "[vo]", "-map", "[a]", "-r", "30", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", tmp])
    if r.returncode == 0: os.replace(tmp, final); print("ok", name, round(dur, 1))

if __name__ == "__main__":
    only = sys.argv[1:]
    for name, segs, hook in CLIPS:
        if not only or name in only: build(name, segs, hook)
