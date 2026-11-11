# Southline: "Only one of them sells" (clothing brands): re-edit of five supplied clips

One Instagram reel cut from Ryan's five clips. 9:16, 1080×1920, 30 fps, about 47 s.
CTA: **Comment AUDIT** (free review of their current ads).

Output: `southline_clothing_one_sells.mp4`.

## What the five clips were
| Clip | What it is | Used for |
|---|---|---|
| 1 (33.5 s) | The "Only one of them sells" test-method ad, blue style, music baked in | **Not used.** Same script as clip 4, so using both would repeat it. |
| 2 (7 s, silent) | B-roll: ring-light creator, man in coat, older woman in snow, polaroid wall | "Different faces / hooks / settings", "a test" |
| 3 (8 s, silent) | B-roll: hoodie, phone reviews, laptop of ads, sticky notes | Research beat ("best sellers", "three angles… care about") |
| 4 (40.6 s) | The same test-method ad, Southline green and gold, the longer version | Most of the voice + the AD 01/02/03 and presenter shots |
| 5 (21 s) | A different pitch: "if our ads don't sell your clothes, you pay us nothing… no sale, no fee" | "Clothing brand owners", "Most agencies charge a retainer. Win or lose.", "We make the creatives, run your Meta ads and only take a cut when a sale lands." |

## The story (one ad, in order)
1. **Callout:** "Clothing brand owners." (clip 5)
2. **Hook:** "This is ad one. This is ad two. Ad three. Only one of them sells." (clip 4). The three ads appear; two grey out and one goes gold.
3. **Open loop:** "Here's how we find out which in under a week."
4. **Research:** "Week one: we pull your best sellers… and find the three angles your buyers actually care about." Clean b-roll from clip 3.
5. **Create:** "Then we make 10 to 15 ads." The grid fills to 15. "Different faces, different hooks, different settings. Not one pretty ad. A test." (clip 2 b-roll)
6. **Test:** "Meta tells us within days which ones sell. We kill the losers, scale the winners, and make new versions of what works. Every week." Losers struck through, winners gold, new versions take the dead slots.
7. **Contrast:** "Most agencies charge a retainer. Win or lose." (clip 5)
8. **Offer (Cloud):** "We make the creatives, run your Meta ads and only take a cut when a sale lands." The list reads 01 creatives, 02 Meta ads, 03 "Our fee: tied to your sales".
9. **Reassurance:** "And you're not paying us to experiment."
10. **CTA:** "Comment audit and I'll look at your current ads and tell you what I'd change. Free." End card with the SA badge.

## How it's made
- **Voice:** separated from the music baked into clips 4 and 5 (Spleeter 2-stem via sherpa-onnx). That way the spliced lines don't make the old music jump, and one new 124 BPM bed runs under the whole reel (ducked about 9 dB, −14 LUFS).
- **Word timings and cuts:** words were found with an offline recogniser (Parakeet via sherpa-onnx). Cut points are nudged to the quietest 10 ms near each boundary, with 12 ms fades.
- **Talking heads:** the old edits had captions burned into the picture, so each talking head is cropped into a presenter window that sits clear of the old text. Clip 5 gets its own crops, below "owners." and between "retainer," and "win or lose".
- **Captions:** new captions in the Southline house style: serif-italic lead, bold key line, gold underline.
- **Files:**
  - `build_edl.py`: the edit list. It writes the voice track, the timings, the ad-tile stills and the `<video>` clip tags.
  - `mkaudio.py`: the soundtrack.
  - `hyperframes/index.html`: the composition.

## Wording kept out on purpose (CLAUDE.md offer rules for clothing brands)
- Not used: "You pay us nothing", "No sale, no fee", "Paid on sales only" and "We only get paid when you get sales". These imply the brand pays nothing unless it sells, but they still fund their own ad spend.
- Kept: "only take a cut when a sale lands", which is about Southline's fee. On screen it reads "Our fee: tied to your sales".

## Rebuild
```
python3 build_edl.py && python3 mkaudio.py
for i in 2 3 4 5; do ffmpeg -i source/clip$i.mp4 -an -c:v libx264 -crf 17 -g 15 -pix_fmt yuv420p hyperframes/assets/footage/c$i.mp4; done
cd hyperframes && npx hyperframes render -q delivery -f 30 -o ../southline_clothing_one_sells.mp4
```
