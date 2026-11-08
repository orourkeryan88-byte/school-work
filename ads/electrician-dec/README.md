# Southline: "Dec's five problems" (Irish electricians, full rewires)

Meta ad (Facebook + Instagram). 9:16, 1080×1920, 30 fps, **92.9 s**, sound on, burned-in captions.
CTA: **Book a call.**

Output: `southline_electricians_dec_5_problems.mp4`. Character sheet: `character_sheet.png`.

## How it's made
- **3D/2D hybrid, built entirely in code.** The world is real-time 3D (Three.js inside HyperFrames):
  - toon shading in two cel tones
  - a thick, slightly wobbly ink outline on every mesh, which "boils" at 8 fps
  - rounded, bevelled toy shapes
  - shadows, warm gold key lights and pine fill
  - additive light cones for the desk lamp and the attic hatch
  - paper grain and risograph dots over every frame
- **UI is flat 2D in perspective:** cards, chat bubbles, captions, the HUD and the end card. Each one tilts toward camera on arrival and casts a shadow. AI video was not used, so every word on screen is crisp.
- **Dec** (original design) is one rig used in every shot:
  - Body: stocky, gold hi-vis vest with two grey bands over a pine long-sleeve, charcoal trousers with knee-pad pockets, tan boots.
  - Kit: tool belt (screwdriver and voltage tester), pencil behind his ear, pine cap with a white lightning-bolt patch.
  - Expressions: six faces (happy, shocked, frustrated, defeated, determined, celebrating), driven by his brows and mouth shapes, plus idle sway, blinks and a tool-belt jiggle.
  - `character_sheet.png` shows front, 3/4, side and back views plus the six expressions.
- **Files:**
  - `hyperframes/assets/js/kit3d.js`: the look.
  - `dec.js`: the character.
  - `sets.js`: locations A–I and the props.
  - `shots.js`: the 15 scenes, written as pure functions of time.
  - `hyperframes/index.html`: UI, HUD, captions and timeline.

## Scenes (times from the voiceover)
| # | Time | Line | On screen |
|---|---|---|---|
| 1 | 0.0–6.6 | You're a spark… post your first Facebook ads. | Low angle: the rewires.co van rolls in and bounces; Dec hops out and waves. The camera cranes up as night falls, back to the box-room window, in through the rain, over his shoulder, into the laptop. The "Publish ad" card gets clicked, then "Ad is live" bursts out. |
| 2 | 6.6–10.0 | You hit refresh. And… nothing. | Morning, wall clock 8:02. A refresh icon spins, "0 ENQUIRIES" shakes, and a reverse shot shows Dec slumping. |
| 3 | 10.0–15.4 | Five problems… every fix brings the next one. | Pine stage: five domino tiles (tile 1 in gold) topple in slow motion and the last stops at his boots. He shrugs. The HUD drops in. |
| 4 | 15.4–21.0 | Problem one: free quotes. | Van cab, slow-mo orbit: identical "Free quotes · any job" cards fly out of his phone and circle him; his card fades into the pile. |
| 5 | 21.0–28.7 | Fix: sell the result… | Offer panel "Full rewire in five days." with two ticks. Cut to the hallway mid-rewire: the phone buzzes on the ladder, enquiries stack in the air, Dec gives his "O". HUD 31 / 1. |
| 6 | 28.7–33.2 | Problem two: junk leads. | Kitchen at night, top-down to eye level: chat bubbles float up, he scratches his head with the screwdriver, and a gold JUNK stamp slams down. |
| 7 | 33.2–41.8 | Fix: who it's for + the price. | Tilt-shift miniature of Kildare. The ad card rises and types "3-bed rewires · Kildare / From €9,000 · certified". 24 lead tiles pop up, 19 sink and 5 glow. HUD 43 / 4. |
| 8 | 41.8–48.6 | Problem three: the form's too easy. | Quote form with taps on Submit, then the van on the road with the NAAS 38 sign flipping, then the empty house: knock, leaves blowing, "No one home." |
| 9 | 48.6–57.1 | Fix: a short video before the form. | Ad → Video → Form tiles joined by glowing cables (the camera rides down). Dec films a selfie by the new consumer unit; a checklist pops; thumbs up. HUD 52 / 9. |
| 10 | 57.1–63.9 | Problem four: too slow. | Attic under a swinging work light. The camera cranes down through the hatch to the landing: "New enquiry" on the phone flips to "Missed call · 12:06", the clock spins to 17:00 in gold, and "Thanks, went with someone else." |
| 11 | 63.9–70.1 | Fix: speed is the system. | Parked between jobs with the phone at his ear. The camera pushes through the windscreen along a gold timeline: 1 MIN, 5 MIN, DAILY. HUD 64 / 15. |
| 12 | 70.1–76.8 | Problem five: switching the ads off. | Busy montage on the beat. He leans on the giant ADS ON toggle to flick it OFF, clunk, and the lights dim. Calendar pages flip to an empty June. |
| 13 | 76.8–82.5 | Fix: never switch them off. | The toggle snaps back ON and a padlock clicks shut. The job cards come in and "Full rewire · Malahide" gets the gold border. Crane up to three rewires.co vans. HUD 70 / 21. |
| 14 | 82.5–88.4 | Offer. Message. Video. Speed. Always on. | Five blocks stack into a tower ("Always on" in gold). Dec jumps on top and the tower glows; the camera orbits. |
| 15 | 88.4–92.9 | Want this built for your business? Book a call. | Pine end card: gold line wipe, extruded "Southline", "META ADS FOR ELECTRICIANS", the "Book a call." pill on the final hit, and the logo row. Dec waves; the house and van sit faintly behind at dusk. Holds 1.5 s. |

## Voice
- **Not the Higgsfield "Cillian" voice:** the Higgsfield account has 0 credits, so it couldn't be generated. ElevenLabs is also out of credits for the month.
- **Current read:** the free Piper TTS voice "en_GB VCTK", speaker **p245** (Irish male, Dublin), generated one line per scene (`lines.json`, `vo/`).
  - The VCTK recordings are CC BY 4.0. Credit if needed: "Voice: Piper TTS, VCTK corpus (CC BY 4.0)".
  - **Caution:** this Piper voice was fine-tuned from Piper's "lessac" voice, whose source recordings are licensed for non-commercial research only. For a paid ad, swap in Cillian (or another paid voice) once there are credits. The scenes re-time from the new lines automatically:
    ```
    python3 timing.py; python3 mkaudio.py   # after replacing vo/sNN.wav + vo/sNN_words.json
    ```
- "craic" and "Naas" are spelled phonetically for the voice ("crack", "Nace"). The captions show the real spelling.

## Changes from the brief
- **92.9 s instead of 85–90 s.** The 15 lines read at about 3 words a second take 80 s on their own.
- **Meta logo:** not drawn. There is a gold "ADS" logo slot in scene 1's card, the ad card in scene 7 and the end card (`#logoSlot`, `#logoSlot2`). Drop the official Meta logo file in there if you want it.
- **Depth of field:** no true depth of field. Depth comes from fog, tilt-shift blur bands (scenes 7 and 8) and light cones.
- **Attic clock:** the 3D clock is on the landing wall, so it's in frame when the camera arrives.
- **Phone call in the van:** Dec makes the call **parked** between jobs (the brief says between jobs), so the ad doesn't show him on the phone while driving.
- **Music:** an original 124 BPM minimal tech-house bed (kick, clap, hats, warm sub bass, no vocals), ducked about 9 dB under the voice, out for 0.25 s before "Book a call.". The final mix is −14.0 LUFS with peaks below −1 dBTP. To use a licensed track instead: `python3 build_audio.py cues.json vo_lev.wav --music track.mp3 -o hyperframes/assets/audio.wav`.

## Before it runs
- **"ILLUSTRATIVE" on screen:** the job names, towns, prices and HUD numbers are illustrative, and the tag stays on screen the whole time the HUD is up. The competitor names on the free-quote cards are made up but could match real firms; swap them if one is local to you.
- **No Southline claims:** there are no Southline prices, guarantees or client results in it.
- **CTA button:** use **Book now** (or Learn more) and point it at your booking page.

## Re-render
```
python3 timing.py && python3 mkaudio.py        # timings (also writes hyperframes/assets/js/timing.js) + soundtrack
NODE_PATH=$(npm root -g) node render.js hyperframes/index.html southline_electricians_dec_5_problems.mp4 4 30
```
`render.js` renders in parallel: each worker seeks the timeline frame by frame, takes a screenshot and pipes it into its own ffmpeg segment. The segments are then joined and the exact mix in `assets/audio.wav` is added. The stock `npx hyperframes render` also works but takes about 5 s a frame here, because WebGL runs in software. If the total length changes, update `data-duration` and the scene `data-start` values in `index.html`.
