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

## Slot types
- 9am, 12pm, 6pm: funny + relatable (school, work, sleep, phone, food, gym, money, friends,
  texting, weekends, family, gaming...). No two reels on the same topic; check topics.md.
- 3pm: short story reel WITH AI voiceover (narrator tells a tiny funny or wholesome story).
- 9pm: motivational (character struggles, keeps going, wins) - uplifting, not cheesy.

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
6. Voiceover (3pm slot only): use the Speko connector `audio.synthesize` with
   `{"text": ..., "intent": {"language": "en-US"}}` (a natural, expressive voice). Decode the
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

Never post anything hateful, sexual, about real people, or using copyrighted characters/music.
