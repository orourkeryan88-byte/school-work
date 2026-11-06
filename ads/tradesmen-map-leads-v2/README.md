# Southline: "Leads already looking for you" v2 (tradesmen, map), more engaging lead pop-ups

Same voiceover (ElevenLabs Sean, `vo_sean.mp3`), map opener and end card as `../tradesmen-map-leads/`; the phone
section (11.05–18.4 s) is rebuilt so the leads land harder. 21.7 s, comment **MAP**. Output: `southline_tradesmen_map_leads_v2.mp4`.

## What's new in the lead section
- The phone sits over a **dark version of the same town** (stick men still there), with a vignette.
- **"…and the enquiries come…"**: five lime ENQUIRY chips launch off people on the map (a ring pulses where each one
  starts) and arc into the phone.
- **"…straight to your phone. Again. And again."**: four enquiries **slam** onto the screen one per beat: they come
  in oversized and tilted, snap into place with a bounce, the phone buzzes and rocks, the screen flashes lime, a
  phone-shaped pulse ripples out, and a counter badge ticks 1, 2, 3, 4. Each card has a job icon (bolt / drop / house).
- **Final "again."**: eight more lead cards spring out around the phone, the badge rolls up to 12, and the camera
  punches in to the end card.
- Sounds: whoosh per flying lead, ding + buzz + thump per slam, rapid pops for the burst.

The jobs and towns are illustrations, not client results. The phone card's lime "ADS" square is the slot for the
official Meta logo file if you want it there. "Comment MAP" needs a comment-to-DM automation.

## Re-render
```
python3 ../make_cues.py . 21.7 accents.json
ffmpeg -i vo_sean.mp3 -af "highpass=f=70,loudnorm=I=-12:TP=-1:LRA=7" -ar 44100 -ac 1 vo.wav
python3 build_audio.py cues.json vo.wav --bed-db -3 -o hyperframes/assets/audio.wav    # then +0.4 dB → -14 LUFS
cd hyperframes && npx --yes hyperframes check && npx --yes hyperframes render -q delivery -f 30 -o ../southline_tradesmen_map_leads_v2.mp4
```

## Soft female voiceover version
`southline_tradesmen_map_leads_v2_female.mp4` (22.2 s): ElevenLabs **Sinéad** (soft, warm Irish female), `eleven_v4`,
same script with `[softly]` on the problem and `[warmly]` from "So we do it for you" → `vo_sinead.mp3`,
word timings `vo_words_sinead.json`. `index.template.html` holds the composition on the Sean timings;
`python3 retime.py vo_words_sinead.json` moves every cut, caption word and SFX onto her read (writes
`hyperframes/index.html` + `cues.json`). `python3 retime.py vo_words_sean.json` goes back to the male timing.
Mix: VO `loudnorm I=-12`, `--bed-db -3`, +0.2 dB → -14 LUFS.

## Laura voiceover version (replaces Sinéad, which sounded off)
`southline_tradesmen_map_leads_v2_laura.mp4` (23.4 s): ElevenLabs **Laura | Warm, Natural Irish Voice**, `eleven_v4`,
take 2 of 2 → `vo_laura.mp3`, one `[warmly]` tag only (no `[softly]`, which can sound breathy). Timings:
`vo_words_laura.json`; `python3 retime.py vo_words_laura.json` (current `hyperframes/index.html`). Mix +0.9 dB → -14.1 LUFS.

## Guarantee version (current `hyperframes/index.html`)
`southline_tradesmen_map_leads_guarantee.mp4` (27.4 s, Laura): adds a lime guarantee beat after "again and again":
a big **10** counts up, "qualified leads / in 30 days," builds word by word, then an **"or your money back"** stamp
slams down. VO line added: "Ten qualified leads in thirty days, or your money back." (`vo_laura_guarantee.mp3`,
`vo_words_laura_guarantee.json`). The end card moved 3 s later in the template (`vo_words_est.json` = the template's
timing incl. the new line); `python3 retime.py vo_words_laura_guarantee.json`. Mix +0.9 dB → -14.1 LUFS.

Before running it: the guarantee was asked for by the owner. Write down what counts as a "qualified lead" (e.g. a
real person, in the service area, asking for a job the business does, contactable) in the client contract and the
comment-DM reply, when the 30 days start (e.g. from the day ads go live), and exactly what is refunded if it's missed
(the management fee; ad spend is paid to Meta and isn't refundable by Southline).
