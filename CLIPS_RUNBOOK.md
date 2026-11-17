# Clip slot runbook (@typeshi707)

Clip slots (Vancouver time): 10:30am, 1:30pm, 4:30pm, 7:30pm, 11pm. Each run posts ONE clip.

1. Read `clips/queue.json`. Take the FIRST entry with `"posted": false`.
2. If there is none (queue empty): follow RUNBOOK.md and make + post a FUNNY animation reel instead,
   and say in the final summary that the clip queue is empty and the user needs to send new footage.
3. Otherwise post it with the Windsor.ai connector: `execute_action` connector `instagram`,
   account `17841442538868018`, action `create_video_post`, params
   `{"video_url": "https://cdn.jsdelivr.net/gh/janavD/reels@<HEAD commit sha>/<file>",
     "caption": <the entry's caption>, "share_to_feed": true}`.
   Use the full SHA from `git rev-parse HEAD` (the file must exist at that commit).
   If it fails, wait 1 minute and retry once with
   `https://raw.githubusercontent.com/janavD/reels/<sha>/<file>`.
4. Set that entry's `posted` to true, `media_id` to the returned id and `posted_at` to the
   current time, commit and push (`git -c push.negotiate=true push origin HEAD:main`; if rejected,
   `git fetch --depth=5 origin main`, `git rebase origin/main`, push again).
4b. Captions: hook line, one keyword sentence (creator name + what happens), then EXACTLY 5 hashtags
   (creator tag, creator-nickname tag, event/topic tag, #clips, 1 broad tag). Never more than 5.
5. Final message: which clip, caption, media id (or what failed), and how many unposted clips are left.
   If 3 or fewer are left, say the user should send new footage soon.

jsDelivr only serves files up to 20 MB, so every clip in the queue must be under 19 MB
(re-encode with a lower video bitrate if needed).

Making new clips (done in a chat with the user, not by the scheduled runs): see engine/make_clips.py.
Format: 1080x1920, blurred background, 4:3 centre crop at y=555, hook title at the top,
yellow word captions underneath from a word-timestamp transcript, @typeshi707 tag.
