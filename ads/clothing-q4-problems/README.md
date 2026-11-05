# Southline: "Q4 problems you didn't know you had" (clothing brand owners)

Meta ad (Reels / Facebook), 9:16 1080×1920, 28.1 s, no voiceover: on-screen kinetic type carries the message, cut to a
124 BPM grid. CTA: comment **Q4**. Output: `southline_clothing_q4_problems.mp4`.

Angle: Q4 breaks DIY ads (competition for the feed, ad fatigue, cart-abandoners lost with no retargeting or emails).
It's not the clothes, it's the system. Southline runs the Meta ads (main offer) + emails that bring buyers back (add-on).

## Re-render
```
cd hyperframes
python3 ../build_audio.py ../cues.json -o assets/audio.wav    # then +1 dB (see below) to land on -14 LUFS
npx --yes hyperframes check            # lint, runtime, layout, motion, contrast, craft, audio: 0 errors
npx --yes hyperframes render -q delivery -f 30 -o ../southline_clothing_q4_problems.mp4
```
The synth score normalises to about -15 LUFS here; the delivered mix was lifted 1 dB to -13.9 LUFS / -1.8 dBTP.
To swap in a licensed track: replace `assets/audio.wav` (cut points are on b(n) = n × 60/124 s; music drop-out
22.98–23.23 s before the payoff, riser into the end card, resolved hit on "Q4" at 25.89 s).

## Footage slots
Shot 1 (POV founder packing at night, 0–3.4 s) and shot 8 (hoodie being pulled on, 23.2–25.6 s) are illustrated
stand-ins built in HTML: no original footage was available. Replace with the brand owner's own phone footage when filmed.
