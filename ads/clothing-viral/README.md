# Southline: three clothing-brand reels, one style

Three 9:16 Instagram/Facebook reels (1080x1920, 30 fps, sound on with captions burned in). They're cut from Ryan's Higgsfield and ElevenLabs clips in `Southline_All_Files`, all in one look: **Southline Clean Cut**.

| File | Length | Hook (on screen from frame 1) | Story |
|---|---|---|---|
| `southline_v1_only_one_sells.mp4` | 26.7 s | "Only one of these sells." | Three presenters say "this is ad one / two / three". Then research, 10–15 ads, different faces, hooks and settings, a test, and Meta picks the winner in days. |
| `southline_v2_still_paying_a_retainer.mp4` | 14.6 s | "Still paying an agency retainer?" | A presenter, lip-synced, says agencies charge a retainer win or lose. Southline makes the creatives, runs the Meta ads and takes a cut when a sale lands; a "New order" pops in. |
| `southline_v3_not_one_pretty_ad.mp4` | 17.1 s | "Stop betting on one ad." | "Not one pretty ad. A test." Then different faces, hooks and settings; Meta tells us in days; kill the losers, scale the winners, new versions every week; "you're not paying us to experiment". |

All three end on the same **Black Friday** end card:
- "BLACK FRIDAY DEAL"
- "50% OFF" slams in, and a red ticker band runs across.
- "comment **SALES** to learn more", voiced by the narrator: "Comment… sales." is spliced from his own take, because ElevenLabs was out of credits for a new line.

## Why it's cut like this
**From Southline's own Instagram insights:**
- People watch Southline's reels for 5–12 s on average.
- The short one-idea reel had the best watch time.

**From research on high-performing reels:**
- Put the claim on screen in frame 1, readable with the sound off.
- Make a visual change every 1–2 s and cut the dead air.
- Use big captions, highlighting the word being said.
- Add punch-in zooms on the key words.
- End on a card that loops back to the start.

The Composio Instagram scraper was out of credits, so the research came from Firecrawl web research instead.

## The style: "Southline Black Cut" (shared by all three, in `template.html`)
- **Captions behind the head.**
  - Each shot with a person is cut out with `npx hyperframes remove-background`, giving `cutouts/*.webm`.
  - The layers go footage, then the captions, then the cut-out of the person. The head covers the lower ~30% of the words.
  - `build.py` tracks the top of the head from the cut-out so the words sit just above it.
  - In tight close-ups there's no room above the head, so the caption goes in front, lower down.
- **Font:** League Gothic (tall condensed caps) for captions, headlines and the end card. Space Mono for labels, Inter for small text.
- **Square corners** everywhere.
- **Colours:** black #0B0B0B, bone #F3EFE6, signal red #FF3D2E, smoke #8C8A85.
  - Footage is graded darker and less saturated.
  - The word being said is red, and so are the progress bar, the chips and the winner frames.
- **Motion:** every shot enters with a zoom blur and the footage drifts slowly. Key words get punch-in zooms, and the graphics pop in.
- **Sound:** the same music bed ducked under the voice, a whoosh on every cut, hits on the end-card slams. Mastered at −14 LUFS.

## Voices
- **V1:** opens with the hook presenter's own voice (lip-synced), then the narrator (Adam) takes over from "Week one".
- **V2:** the talking presenter only, lip-synced throughout.
- **V3:** Adam only.

## Lines left out on purpose (CLAUDE.md offer rules)
- "If our ads don't sell your clothes, you pay us nothing", "No sale, no fee" and "We only get paid when you get sales" all imply the brand pays nothing. They still fund their own ad spend.
- V2 shows "Our fee: tied to your sales" instead.
- The Black Friday 50% off end card is Ryan's offer. Make sure the DM reply says what the 50% applies to.

## Before posting
- Set up a comment-to-DM automation for **SALES**.
- The order toast and the chart on the laptop are illustrative.
- The presenter footage is 480p, upscaled, so it's slightly soft.
- The music bed is an ElevenLabs Music track. Check you're happy with it, or swap in your own licensed track: `--music` in `mkaudio.py`.

## Rebuild
```
python3 build.py            # voice splice, timings, clip tags and beats -> v1/ v2/ v3/
python3 mkaudio.py          # soundtracks
cd v1/hyperframes && npx hyperframes render -q delivery -f 30 -o ../../southline_v1_only_one_sells.mp4
```
- **Sources:** `media/` holds the transcoded clips and `voice/` the voice takes with word timings. `shared/` holds the fonts, GSAP, the stills, the badge and the bed.
- **Edits:** change a reel's lines and beats in `REELS` inside `build.py`. Change the shared look in `template.html`.
