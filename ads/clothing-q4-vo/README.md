# Southline: "Q4 problems you didn't know you had" (voiceover cut, clothing brand owners)

Meta ad (Reels / Facebook / Instagram), 9:16 1080×1920, 34.3 s, 30 fps. Captions are word-timed to the script; the
voiceover is Ryan's own recording (not in yet). CTA: comment **Q4**.

Outputs:
- `southline_clothing_q4_vo_colour.mp4`: the current version, a bold colour cut (what `hyperframes/index.html` builds now).
- `southline_clothing_q4_vo.mp4`: the first cut in the green Southline house colours (source in git history).

## Colour cut
Black `#0D0D0F` and cream `#F3EFE6` bases, with each pop colour doing one job so the eye knows where to look:
- **Hot orange `#FF5B1F` = problems:** underlines on the pain lines, the rising cost bar, the falling sales line, the strike-throughs.
- **Electric lime `#D7FF3C` = fixes and the CTA:** "nobody", the gold-line wipe, marker highlights on "system" and the fix list, the block behind the hoodie, "Q4".
- **Lilac `#B6A3FF` = product and brand:** phone-feed posts, the repeating ad, the cart thumbnail, the email card, the hoodie, a faint haze.
- In the POV opener the role stickers are lilac / orange / lime.

Angle: Q4 is when DIY ads break (every brand fighting for the same feeds, the same ad getting scrolled past, cart
buyers lost with no retargeting or emails). It's not a product problem, it's a system problem. Southline runs the
Facebook and Instagram ads (main offer) and sets up the emails that bring buyers back (add-on, once, near the end).

## Voiceover script (101 words) and where each line sits

| Shot | Time | Line | On screen |
|---|---|---|---|
| 1 Viral opener | 0.0–3.15 | This is what Q4 looks like when you run your clothing brand's ads yourself. | Handheld POV of a stockroom desk at night: mailers landing, laptop, tee stacks, phone buzzing NEW ORDER. Native stickers "POV: it's Q4 / and you're the… designer · packer · ads guy" |
| 2 Freeze + rewind | 3.15–5.0 | And here's what nobody tells you. | Freeze, desaturate, REWIND scrub with a glitch (parcels fly back up), hard cut to Pine. "nobody" bursts out of a crop-corner box, bigger than the frame, slides left. *tells you.* |
| 3 Pain 1 | 5.0–10.0 | Every brand is fighting for the same feeds right now, so your ads cost more. | 01 — Q4 COMPETITION. Identical phone feeds crowd in from every edge, "every brand" slides through oversized. *every brand is / fighting for feeds.* then *so your ads / cost more.* as a gold bar rises (no numbers) |
| 4 Pain 2 | 10.0–14.0 | Same ad for weeks? People scroll past it. Sales slow down mid-rush. | Whip. 02 — AD FATIGUE. The same card repeats faster and faster, the feed scrolls past it in a blur. *same ad for weeks? / scroll past it.* (gold on "past"), then a sales line rises and flattens: *sales slow down / mid-rush.* |
| 5 Pain 3 | 14.0–19.0 | And everyone who added to cart and left? No retargeting, no emails, they're gone. | Whip. 03 — LOST BUYERS. Cart card tilts in, the hoodie drifts out of it and out of frame. *added to cart… / and left?* Then "retargeting", "cart email", "welcome flow" get struck through and fly out of frame on "gone" |
| 6 The turn | 19.0–22.0 | That's not a product problem. It's a system problem. | *that's not a / product problem.* wiped away by the gold line → Cloud, *it's a / system problem.* builds word by word, ghost "system" behind |
| 7 Solution | 22.0–29.0 | Southline runs your Facebook and Instagram ads. Fresh creatives, proper tracking, retargeting. Plus the emails that bring buyers back. | 04 — THE FIX. "Southline", *runs your Facebook and Instagram ads.*, build-on list with gold bars, then the "+ email flows / that bring buyers back" card tilts in, envelope and returning-cart icons draw on |
| 8 Payoff | 29.0–31.0 | You focus on the clothes. | Music drops out 28.75–29.0. Hoodie pulled down, *you focus on the* … "clothes." sits behind it, then pops in front on the beat |
| 9 CTA | 31.0–34.3 | Comment Q4 and we'll show you how. | End card on Pine: *comment* + oversized gold "Q4" bleeding off the right edge, *we'll show you how*, Southline wordmark. Holds 1.5 s, loops to frame 1 |

`vo_words.json` holds the estimated time of every spoken word (`vo_timing.py` makes it from the line windows above).

### Changes from the brief
- **34.3 s instead of 34.0.** "Comment Q4 and we'll show you how" needs about 1.7 s to say, so the end card would only
  hold about 1.2 s inside 34 s. The extra 0.3 s gives it the 1.5 s hold the brief asks for.
- **The freeze lands at 3.15 s, not 3.0.** The opening line is 17 syllables, which is quick in 3 s, so it gets a
  touch longer. The rest of the shot boundaries are exactly the brief's.
- Captions follow the brief's lead/key lines. Where the VO runs on (e.g. "so your ads cost more", "sales slow
  down mid-rush") the next caption replaces the last one, so there are never two captions at once.

## Recording the voiceover
- Read it conversationally, like telling a mate. The pace these captions were built for is about 3 words a second
  (lines 1 and 7 are the quick ones).
- Phone close to your mouth, quiet room with soft furnishings, no music. Leave half a second of silence at the start.
- Send the file (m4a, mp3 or wav) and the cuts and every caption word get re-timed to your actual read, and it gets
  mixed with your track: music ducked about 9 dB under your voice, the 250 ms drop-out before "you focus on the
  clothes", riser into the end card, -14 LUFS / -1 dBTP.

## Music
The current mix uses a temporary synth bed plus SFX, standing in for your track. To use yours:
```
python3 build_audio.py cues.json vo.m4a --music your_track.mp3 -o hyperframes/assets/audio.wav
```
`--music` swaps your track in for the synth bed; the drop-out, ducking and loudness targets still apply.
Use a track you have the licence for.

## Footage slots
Shot 1 (founder packing at night) and shot 8 (hoodie being pulled on) are illustrated stand-ins built in HTML.
Swap in your own phone footage when it's filmed: handheld, natural light, 9:16.

## Before you run it
- **Comment Q4** needs a comment-to-DM automation (ManyChat, or GHL's Facebook/Instagram comment trigger) that DMs
  everyone who comments Q4.
- No figures, results or guarantees are on screen. The gold bar and the sales line are illustrations with no
  numbers. No platform logos or UI.

## Re-render
```
cd .. && python3 make_cues.py clothing-q4-vo 34.3 clothing-q4-vo/accents.json && cd clothing-q4-vo   # if timings change
python3 build_audio.py cues.json [vo.m4a] [--music track.mp3] -o hyperframes/assets/audio.wav    # then +1 dB to land on -14 LUFS
cd hyperframes && npx --yes hyperframes check && npx --yes hyperframes render -q delivery -f 30 -o ../southline_clothing_q4_vo_colour.mp4
```
Delivered mix: -13.8 LUFS, -2.4 dBFS peak (temporary bed, no VO yet). After the render the soundtrack was muxed in
with ffmpeg so the MP4 carries exactly `assets/audio.wav`.
