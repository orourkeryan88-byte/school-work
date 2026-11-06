# Southline: "Leads already looking for you" (tradesmen, map)

Meta ad (Reels / Facebook / Instagram), 9:16 1080×1920, 21.7 s, 30 fps, voiceover + music + SFX, captions word-timed.
CTA: comment **MAP**. Output: `southline_tradesmen_map_leads.mp4`.

## Voiceover (ElevenLabs "Sean – Laid Back & Friendly", Irish male, eleven_v4, take 1 of 2 → `vo_sean.mp3`)
> Tradesmen. You've got leads already looking for you. People near you, searching for a sparky, a plumber, a builder…
> right now. You just can't get to them. So we do it for you. We run Facebook and Instagram ads for your business, and
> the enquiries come straight to your phone. Again. And again. Comment MAP and we'll show you how.

Word timings (Scribe): `vo_words_sean.json`. Every caption word and cut is placed on them.

## Scenes
| Time | On screen |
|---|---|
| 0–3.1 | Street map (unbranded, map-app tones), close on one stick man holding his phone up, lime location dot pulsing. "Tradesmen," slams in. *you've got leads already / looking for you.* |
| 3.1–8.0 | Zoom out over the whole town: dozens of stick men pop up with location dots. Chips land on the words: "needs a sparky", "needs a plumber", "needs a builder". *people near you, / searching right now.* |
| 8.0–9.65 | A glass pane drops between you and them, the town blurs out of reach. *you just / can't get to them.* (orange underline) |
| 9.65–11.05 | Hard cut to black. *so we do it / for you.* |
| 11.05–18.4 | Phone rises; a "Facebook + Instagram ads" card pops up on the screen (logo slot). *we run Facebook + Instagram ads.* Then NEW ENQUIRY notifications buzz in and stack (Full rewire · Naas, Boiler swap · Lucan, Bathroom refit · Bray, EV charger · Swords, Kitchen extension · Navan, Leak under sink · Douglas). *straight to your phone. / again. and again.* |
| 18.4–21.7 | End card: *we'll show you how* / **comment MAP** / Southline wordmark. |

## Before you run it
- **Meta logo:** the phone card has a logo slot (`#logoSlot`, the lime "ADS" square). It was not drawn by hand because
  a recreated trademark gets ads rejected. Drop the official file from Meta's brand resources into `hyperframes/assets/`
  and it can go in that square, used as Meta's brand guidelines allow.
- **Comment MAP** needs a comment-to-DM automation (ManyChat, or GHL's Facebook/Instagram comment trigger).
- The enquiries and towns on the phone are illustrations, not client results.

## Re-render
```
python3 ../make_cues.py . 21.7 accents.json
ffmpeg -i vo_sean.mp3 -af "highpass=f=70,loudnorm=I=-12:TP=-1:LRA=7" -ar 44100 -ac 1 vo.wav
python3 build_audio.py cues.json vo.wav --bed-db -3 -o hyperframes/assets/audio.wav    # then +0.4 dB → -14 LUFS
cd hyperframes && npx --yes hyperframes check && npx --yes hyperframes render -q delivery -f 30 -o ../southline_tradesmen_map_leads.mp4
```
