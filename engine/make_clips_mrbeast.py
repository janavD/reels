"""Cut vertical clips with a hook title and word captions from a horizontal source video."""
import json, subprocess, os, sys

SRC = "src/v.mp4"
WORDS = json.load(open("transcript.json"))["words"]
OUT = "out"; os.makedirs(OUT, exist_ok=True); os.makedirs("tmp", exist_ok=True)

CLIPS = [
    ("b01_intro", [(0.0, 17.5)], "MrBeast recreated the\\NHunger Games in real life\\Nfor $250,000"),
    ("b02_first_out", [(18.0, 50.0)], "The first elimination of\\NMrBeast's Hunger Games"),
    ("b03_called_mom", [(73.0, 98.5)], "He called his MOM\\Nin the middle of a fight"),
    ("b04_corn_alliance", [(194.0, 228.0)], "They named their\\Nalliance \"Corn\""),
    ("b05_fog", [(279.0, 318.0)], "The game master released\\Nfog... touch it and you're OUT"),
    ("b06_ashley", [(337.0, 374.5)], "3 vs 1...\\N\"it's $250,000\""),
    ("b07_standoff", [(402.0, 446.5)], "The standoff at\\Nthe cornucopia"),
    ("b08_big_boy", [(629.0, 675.0)], "\"You want some, big boy?\""),
    ("b09_duel", [(775.0, 831.0)], "1v1 for the cornucopia...\\Nand his mom is watching"),
    ("b10_drones", [(849.0, 889.5)], "MrBeast used 1,500 drones\\Nto reveal who's eliminated"),
    ("b11_angus", [(1038.0, 1079.5)], "He betrayed his own\\Nteammate for $250K"),
    ("b12_revenge_mom", [(1133.0, 1160.0)], "\"You eliminated my mom\"\\Nrevenge arc"),
    ("b13_jimmy_out", [(1162.0, 1205.0)], "MrBeast got eliminated\\Nfrom his OWN Hunger Games"),
    ("b14_control_room", [(1218.0, 1262.0)], "The eliminated players\\Ntook over the control room"),
    ("b15_why_win", [(1328.0, 1352.0)], "Why they need\\Nthe $250,000"),
    ("b16_fan_favorite", [(1422.0, 1441.0)], "Fans voted him\\Ntheir favorite"),
    ("b17_golden_dagger", [(1505.0, 1533.5)], "Golden dagger =\\N$25,000 bounty"),
    ("b18_juan_ambush", [(1604.0, 1637.0)], "They ambushed\\Nthe fan favorite"),
    ("b19_lost_juan", [(1646.0, 1680.0)], "He lost his best friend\\Nin the game..."),
    ("b20_revenge_fail", [(1679.0, 1723.5)], "His revenge arc\\Nlasted 3 seconds"),
    ("b21_peacekeepers", [(1742.0, 1787.0)], "\"Check her shoes.\\NSorry, I don't trust you\""),
    ("b22_ring_of_fire", [(1851.0, 1883.0)], "Final 5 trapped in\\Na ring of fire"),
    ("b23_final_battle", [(1883.0, 1928.5)], "The final battle\\Nfor $250,000"),
    ("b24_best_friends", [(1929.0, 1966.0)], "Best friends...\\Nfinal 2 for $250,000"),
    ("b25_winner", [(1985.0, 2023.5)], "He grew up homeless...\\Nand just won $250,000"),
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
        "[fg]crop=ih*4/3:ih,scale=1080:810[fgs];"
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
