# Southline: "Your name's on the van" (tradesmen)

Meta ad (Reels / Facebook / Instagram), 9:16 1080×1920, 32.6 s, 30 fps. Music + SFX, readable on mute.
CTA: comment **FEED**. Output: `southline_tradesmen_van_feed.mp4`.

Angle: your name on the van vs your name in their feed. People don't find tradesmen on the road any more; they find
them on their phone at night, and whoever shows up there gets the call. Southline runs the Facebook + Instagram ads,
locals answer a few questions, and the enquiry goes straight to your phone (from your own ads, not shared).

## Voiceover script (ElevenLabs)

Paste as one block. The timings below were built for about 2.8 words a second (a calm, confident Irish voice).

> Tradesmen in Ireland: your name's on the van.
> So why isn't your phone ringing with the big jobs?
> People don't find tradesmen on the road anymore. They find them on their phone, late at night.
> Whoever shows up there gets the call.
> Southline runs Facebook and Instagram ads for your business.
> Locals answer a few quick questions, and the enquiry comes straight to your phone. Not shared with five other lads.
> Same van. Same work. More of the right jobs.
> Comment FEED and I'll show you how.

## Scenes

| Time | Beat | On screen |
|---|---|---|
| 0.0–2.9 | Hook | "Tradesmen," slams through; van with YOUR NAME drives in. *your name's on the van.* |
| 2.9–6.5 | Open loop | A phone that isn't ringing. *so why isn't your phone ringing?* |
| 6.5–9.2 | Problem | Van drives past houses, every window lit by a phone. *people don't find you on the road.* |
| 9.2–12.2 | Problem | Phone at night, a feed of trade posts scrolling. *they find you on their phone.* |
| 12.2–14.9 | Problem | The other lad's post is the one they tap; yours scrolls past. *whoever shows up gets the call.* |
| 14.9–18.6 | Solution | Gold wipe to light. Your post lands top of the feed. *Southline runs your ads.* Facebook · Instagram |
| 18.6–21.6 | Solution | Question card fills itself in: job, where, when. *locals answer a few questions.* |
| 21.6–26.0 | Solution | NEW ENQUIRY lands on your phone; five other phones fade out. *straight to your phone. not shared with five other lads.* |
| 26.0–29.3 | End | Van back, enquiry chips pop above it. *same van. same work. more of the right jobs.* |
| 29.3–32.6 | CTA | *I'll show you how.* comment **FEED** · Southline |

## Before you run it
- **Comment FEED** needs a comment-to-DM automation (ManyChat, or GHL's Facebook/Instagram comment trigger) that DMs
  everyone who comments FEED.
- The example enquiry (Full rewire · Naas · this month) and the chips are illustrations, not a client result.

## Re-render
```
cd .. && python3 make_cues.py tradesmen-van-feed 32.6 tradesmen-van-feed/accents.json && cd tradesmen-van-feed   # only if timings change (word ticks are read from index.html)
python3 build_audio.py cues.json -o hyperframes/assets/audio.wav   # then +1 dB to land on about -14 LUFS
cd hyperframes && npx --yes hyperframes check && npx --yes hyperframes render -q delivery -f 30 -o ../southline_tradesmen_van_feed.mp4
```
Delivered mix: -13.9 LUFS, -2.5 dBFS peak. Render one project at a time (two renders in parallel mixed up the
audio), or remux the soundtrack afterwards with ffmpeg as was done for this delivery.
To add the voiceover, drop the ElevenLabs file in and the music ducks under it (`build_audio.py` has a VO input).
