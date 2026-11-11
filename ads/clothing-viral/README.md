# Southline: three clothing-brand reels, one style

Three 9:16 Instagram/Facebook reels (1080x1920, 30 fps, sound on with captions burned in). They're cut from Ryan's Higgsfield and ElevenLabs clips in `Southline_All_Files`, all in one look: **Southline Clean Cut**.

| File | Length | Hook (on screen from frame 1) | Story | CTA |
|---|---|---|---|---|
| `southline_v1_only_one_sells.mp4` | 28.6 s | "Only one of these sells." | Three presenters say "this is ad one / two / three". Then: research, 10–15 ads, different faces, hooks and settings, a test, and Meta picks the winner in days. | Comment **AUDIT** |
| `southline_v2_still_paying_a_retainer.mp4` | 15.4 s | "Still paying an agency retainer?" | A presenter, lip-synced, says agencies charge a retainer win or lose. Southline makes the creatives, runs the Meta ads and takes a cut when a sale lands; a "New order" pops in. | Comment **ADS** |
| `southline_v3_not_one_pretty_ad.mp4` | 19.0 s | "Stop betting on one ad." | "Not one pretty ad. A test." Then different faces, hooks and settings; Meta tells us in days; kill the losers, scale the winners, new versions every week; "you're not paying us to experiment". | Comment **AUDIT** |

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

## The style (shared by all three, in `template.html`)
- **Footage:** full-bleed and graded towards Pine, with grain and a vignette. Every shot enters with a zoom blur and then drifts slowly.
- **Top of frame:** a gold progress bar. A gold kicker sits over a two-line headline, and the key word turns gold.
- **Captions:** 1–3 words at a time in the centre; the word being said is gold.
- **Graphics:** Pine glass cards with the gold accent:
  - the three ads
  - the 15-ad grid that kills the losers, scales the winners and adds new versions
  - DAY 1→3 chips
  - the retainer card
  - the "New order" toast
  - big text
- **End card:** the same in all three: Southline badge, "comment KEYWORD" and a gold rule.
- **Sound:**
  - the same music bed, ducked under the voice
  - a whoosh on every cut, pops and hits on the graphics
  - a riser and a short drop-out into the end card
  - mastered at −14 LUFS

## Voices
- **V1:** opens with the hook presenter's own voice (lip-synced), then the narrator (Adam) takes over from "Week one".
- **V2:** the talking presenter only, lip-synced throughout.
- **V3:** Adam only.

## Lines left out on purpose (CLAUDE.md offer rules)
- "If our ads don't sell your clothes, you pay us nothing", "No sale, no fee" and "We only get paid when you get sales" all imply the brand pays nothing. They still fund their own ad spend.
- V2 shows "Our fee: tied to your sales" instead.
- The old reels' end card ("Guaranteed", "Black Friday 50% off", pay per sale) isn't used: it's unconfirmed and against the rules.

## Before posting
- Set up comment-to-DM automations for **AUDIT** and **ADS**.
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
