# Daily reel runbook (@typeshi707)

Each scheduled run makes ONE new reel and posts it. Follow every step.

## Style (keep consistent)
- 2D cartoon in the style of jevon_animations: stick-figure guy with a big round cream head
  (SKIN), thick black outlines, cozy illustrated room backgrounds.
- 1080x1920, 30 fps, 12-25 s, white caption bar at the top with the setup line
  (`me: "..."` / `me when ...` / `POV: ...`), big outlined labels near the bottom.
- Lots of motion: jointed arms/legs with `limb()`/`ik()`, hands, head tilt/bob, blinking,
  expression changes, camera push-ins (`punch()`), pop-in text (`back()`), shake for panic.
- Each reel: a setup, 3-6 short beats that escalate, and a punchline at the end.

## Slot types (ONE animation reel every hour, 24 a day, Vancouver time)
Use the current Vancouver hour (TZ=America/Vancouver date +%H) to pick the type:
- 07, 13, 21: MOTIVATIONAL (struggle, keep going, win) - 62-75 seconds.
- 11, 15, 19: STORY WITH AI VOICEOVER (tiny funny or wholesome story) - 62-75 seconds.
- every other hour: FUNNY + RELATABLE, 12-25 seconds. Late night (23-05) favour late-night
  topics (3am thoughts, can't sleep, night snacks, gaming till sunrise).
Clips are NOT posted to Instagram any more (they are TikTok-only now).
No two reels on the same topic; check topics.md. With 24 a day, vary settings (bedroom, kitchen,
classroom, gym, bus, store, office, park, beach) and side characters so the feed stays fresh.

## Monetization rules (apply to EVERY reel)
Goal: grow followers fast and qualify for TikTok Creator Rewards (10K followers, 100K views/30 days,
ORIGINAL videos over 1 minute) and Instagram monetization + brand deals.
- Hook in the first 1 second: the caption bar line must create curiosity or instant relatability.
  No slow intros. Something moves on screen in frame 1.
- Retention: a new beat every 2-3 seconds; escalate; payoff at the end. End on a frame that loops
  cleanly back into the start when possible (rewatches boost reach).
- LENGTH: the story and motivational reels must be 62-75 seconds (over 1 minute so they
  earn on TikTok Creator Rewards). Funny reels stay 12-25 s (short = more shares/rewatches).
- Series: when a topic works, make it a numbered series ("part 2", "day 1 vs day 47") - series
  drive follows. Caption ends with a soft CTA: "follow for part 2", "send this to your friend who..."
  or "save this for later".
- Brand-safe: no swearing, no violence beyond cartoon slapstick, no politics, no real brands or
  logos (sponsors pay more for clean accounts and we must not show unpaid brands).
- Leave natural product moments in stories (phone, snacks, energy drink, headphones, app on a
  laptop) drawn as GENERIC items - these are the slots a sponsor can buy later.
- Captions: hook line + 1 emoji, then 5-8 hashtags mixing broad (#relatable #funny) and niche
  (#studentlife #gymmotivation). Never more than 10.


## Budget rules (must last at least a month)
Voiceover credit (Speko) must last 30+ days:
- Before any voiceover, check the balance with the Speko credits balance tool. If it is under $1.50,
  skip the voiceover and use on-screen text instead.
- Narration max ~900 characters (about 60-70 s). Use intent {"language":"en-US","optimizeFor":"cost"}.
  Synthesize ONCE per reel - never re-generate the same narration.
Keep each run light on usage:
- One contact sheet of stills (max 6 frames, small), at most ONE round of fixes, then ONE full render.
- Reuse before you draw: check engine/library/ for scenes and props made by earlier runs and import
  them. After posting, save any new reusable scene/prop functions to engine/library/<topic>.py.
- Do not read whole large files; never re-render a finished reel unless it is broken.
- Funny reels: 12-20 s, 3-5 scenes. Long reels: reuse library scenes heavily.

## Steps
1. Read `topics.md`. Pick a fresh topic that fits the slot and was never used.
2. Write `work/<date>_<slot>.py`: `import sys; sys.path.insert(0, 'engine'); import rig` and reuse
   everything from `engine/rig.py` (C, head, limb, ik, hand, room/bed/desk/window/lamp/etc,
   caption/label/sub/bubble, easing, render). Set `rig.CAP = [...]` (max ~22 characters per
   line, 1-3 lines). Write new scene functions `f(t) -> PIL image` and a SCENES list.
   Add new props/sets as needed in the same drawing style.
3. Draw a contact sheet of stills at the busiest moments of each scene and LOOK at it.
   Fix overlaps (labels over faces, text off screen, limbs crossing badly) before rendering.
4. Render each scene with `rig.render(name, dur, fn, outdir)`, concat with the ffmpeg concat
   demuxer `-c copy`.
5. Soundtrack: copy `engine/music_example.py` and adapt it (keep the synth helpers: rhodes,
   bell, kick, snare, hat, bass, saw, tone, noise_sweep). Match the music and sound effects
   to the scene timings. Vary key, tempo and melody each reel. Funny = lo-fi / bouncy;
   panic = tense; motivational = slow build to an uplifting climax.
6. Voiceover (story slots only, see Budget rules): use the Speko connector `audio.synthesize` with
   `{"text": ..., "intent": {"language": "en-US", "optimizeFor": "cost"}}` (a natural, expressive voice). Decode the
   base64 audio, place it over the video, duck the music to ~35% under the voice, and make
   the scenes long enough for the narration. If Speko fails or credits run out, skip the voice
   and use on-screen text instead.
7. Mux video + audio (`-c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart`).
   Check: duration 10-30 s, 1080x1920, has audio.
8. Save to `videos/<YYYY-MM-DD>_<HHMM>_<slug>.mp4`, commit, and push to main with
   `git -c push.negotiate=true push origin HEAD:main`.
9. Post with the Windsor.ai connector: `execute_action` connector `instagram`, account
   `17841442538868018`, action `create_video_post`, params
   `{"video_url": "https://cdn.jsdelivr.net/gh/janavD/reels@<commit-sha>/videos/<file>.mp4",
     "caption": "<hook line + emoji>\n\n<8-12 relevant hashtags>", "share_to_feed": true}`.
   Use the full commit SHA of the commit that added the file. If it fails, wait 1 minute and
   retry once with `https://raw.githubusercontent.com/janavD/reels/<sha>/videos/<file>.mp4`.
10. Append a line to `topics.md` (date | slot | type | topic | file | media id), commit, push.
11. Final message: topic, caption, and whether it posted (with media id) or what failed.

If a push is rejected because another run pushed first: `git fetch --depth=5 origin main`,
`git rebase origin/main` (for topics.md conflicts keep both lines), then push again.

Never post anything hateful, sexual, about real people, or using copyrighted characters/music.
