# Southline: "Nobody's seen them twice" (clothing brand owners)

Meta ad (Reels / Facebook / Instagram), 9:16 1080×1920, 33.6 s, 30 fps. Music + SFX, readable on mute.
CTA: comment **LOOK**. Output: `southline_clothing_second_look.mp4`.

Angle: your ads aren't failing, nobody's seen them twice. Most people don't buy the first time they see a brand
(scroll, save, forget). Southline runs the Meta ads as a full journey: fresh creatives to get seen, then retargeting
so everyone who looked sees you again. Fee tied to the sales the ads bring in; emails that bring past customers back
as the one add-on mention near the end.

## Voiceover script (ElevenLabs)

Paste as one block. The timings below were built for about 2.8 words a second.

> Clothing brands: your ads aren't failing. Nobody's seen them twice.
> So why do people look at your stuff… and leave?
> Most people don't buy the first time they see a brand.
> They scroll. Save. Forget.
> Show them once, and that sale's gone.
> Southline runs your Meta ads as a full journey: fresh creatives to get you seen, then retargeting, so everyone who looked sees you again.
> Our fee's tied to the sales our ads bring in. Plus, emails that bring past customers back.
> Comment LOOK and we'll map out your Q4.

## Scenes

| Time | Beat | On screen |
|---|---|---|
| 0.0–3.6 | Hook | "Clothing brands," slams in; product card tagged SEEN 1×. *your ads aren't failing. nobody's seen them twice.* |
| 3.6–7.2 | Open loop | Someone taps the card… then swipes it away. *so why do people look… and leave?* |
| 7.2–11.2 | Problem | Journey rail: LOOK 1 lights up, BUY is way down the line. *most people don't buy the first time.* |
| 11.2–13.3 | Problem | One word per beat over a scrolling feed: *scroll. save. forget.* (bookmark appears, then fades) |
| 13.3–15.9 | Problem | The card drops off the rail, the buy never happens. *show them once, sale's gone.* |
| 15.9–19.4 | Solution | Gold wipe to light; the full journey draws on in gold. *Southline runs your Meta ads* |
| 19.4–24.8 | Solution | NEW CREATIVE · SEES YOU AGAIN; the card travels look → look → look → BOUGHT ✓. *fresh creatives, then retargeting. everyone who looked sees you again.* |
| 24.8–30.2 | End | *our fee's tied to the sales.* Cards: Tied to the sales our ads bring in. · Plus: emails that bring past customers back. |
| 30.2–33.6 | CTA | *we'll map your Q4.* comment **LOOK** · Southline |

## Before you run it
- **Comment LOOK** needs a comment-to-DM automation (ManyChat, or GHL's Facebook/Instagram comment trigger).
- Wording follows the house rules: fee "tied to the sales our ads bring in", never "only pay per sale"; ad spend is
  explained on the call, not in the ad; emails are mentioned once, near the end, as an extra.
- The hoodie card is an illustration, not a client's product.

## Re-render
```
cd .. && python3 make_cues.py clothing-second-look 33.6 clothing-second-look/accents.json && cd clothing-second-look   # only if timings change
python3 build_audio.py cues.json -o hyperframes/assets/audio.wav   # then +1 dB to land on about -14 LUFS
cd hyperframes && npx --yes hyperframes check && npx --yes hyperframes render -q delivery -f 30 -o ../southline_clothing_second_look.mp4
```
Delivered mix: -13.9 LUFS, -2.5 dBFS peak. Render one project at a time (two renders in parallel mixed up the audio).
