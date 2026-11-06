# Southline: ad week of Mon 9 – Sun 15 Nov 2026

## What's performing (Meta Ad Library, IE + GB, active ads, 6 Nov 2026)
Long-running ads (advertisers keep paying for what works) in the trades-leads space:
- **"Looking for more work?"** (MyJobQuote, running since Jun 2026): a plain question to the audience.
- **"Website + Leads For £197/Month"** (UK Trade Leads, since Feb 2026): price/value framing.
- **"Fill Your Diary, Or Your Money Back!"** (The Brand Angle, since Oct 2026): guarantee / risk reversal.
- **"New Here? Start with £25 FREE"** (Workalat, since Oct 2026): first-step offer.
- Newer, many variants (testing hard): **"100 LEADS A DAY? BULLSH*T!"** (myth-busting), "Why Your Facebook Leads Are
  Junk", "Booked Rewires, Not Random Leads", "£11 a Lead for Jobs Worth Thousands", "Who picks up?".
Recreated as *formats*, not copied: plain-question hook, myth-buster, risk reversal, speed-to-lead, timely urgency.
Prices/results in those ads are theirs; Southline's ads use no invented prices or results.

## Sounds
Firecrawl → Pixabay's licensed catalogue: the most-used styles right now are bright, energetic, medium-fast tech house
and darker "restless" deep house. Pixabay only releases files through its in-browser download, so the week's beds are
original instrumentals generated in those styles with ElevenLabs Music (commercial use on the paid plan):
A bright tech house · B dark restless minimal · C warm deep house.

## The week (all new angles; none repeat `angles-log.md`)
| Day | Audience | Angle | Hook | Keyword | Visual system | Bed |
|---|---|---|---|---|---|---|
| Mon | Trades | Self-check: 3 questions | "Looking for more work? Answer three questions." | WORK | Giant checkboxes thump in, scorecard | A |
| Tue | Trades | Myth-buster: 100 leads a day | "A hundred leads a day? No chance." | REAL | Odometer spins to 100, crashes, 10 real cards remain | B |
| Wed | Clothing | Boosting posts vs real campaigns | "Still pressing boost?" | BOOST | One boost arrow vs a branching campaign tree | C |
| Thu | Trades | The callback race | "The first one to ring back gets the job." | FIRST | Race lanes + stopwatch, your phone wins | B |
| Fri | Clothing | Black Friday run-in | "Black Friday's less than three weeks away." | FRIDAY | Countdown calendar flips, audience warms up | C |
| Sat | Trades | Referral ceiling | "Word of mouth only grows as fast as your last job." | GROW | Stair-step graph that stalls vs a rising stream | A |
| Sun | Trades | Risk reversal | "What if it doesn't work? Then you don't pay." | RISK | Balance scale: the risk moves off you | A |

## Status (6 Nov)
- **Mon · WORK** `mon-work/mon_work_looking_for_more_work.mp4` (29 s) and **Tue · REAL** `tue-real/tue_real_hundred_leads.mp4`
  (25.5 s): done. Laura VO (ElevenLabs), bed A (ElevenLabs Music, bright tech house ~123 BPM, `music/`), -14 LUFS.
- **Wed–Sun: blocked.** The ElevenLabs account hit its monthly quota (10,000 credits) partway through: the music
  generations (four variations per style) used most of what was left. Five voiceovers and beds B/C didn't generate.
  The scripts below are final; once credits are topped up (or the quota resets) each one takes one VO + one build.
- Bed A was generated with ElevenLabs' "instrumental" switch off (prompt says no vocals). Give it a listen before the
  ads run; the vocal check couldn't run without credits.

## Scripts still to voice (Laura, `[warmly]`)
- **Wed · BOOST (clothing):** Clothing brands. Still pressing boost? Boosting shows one post to whoever's around, and
  that's it. No testing, no retargeting, no idea what actually sold. We run your Meta ads properly: fresh creatives
  tested every week, the winners pushed harder, and everyone who looked, brought back. And our fee's tied to the sales
  our ads bring in. Comment BOOST and we'll show you the difference.
- **Thu · FIRST:** Tradesmen. When someone needs a job done, they don't ring one of ye. They message three. And the
  first one to ring back usually gets the job. With us, the enquiry lands on your phone the second it comes in, with
  the job, the area, and when they want it done. You ring first. You win the job. Comment FIRST and we'll show you how.
- **Fri · FRIDAY (clothing):** Clothing brands. Black Friday's less than three weeks away. The brands that win it don't
  start on the day. They're testing creatives now, warming up their audience now, so when the sale drops, people
  already know them. Start on the Friday, and you're showing up cold to the busiest feed of the year. We'll get your
  Meta ads ready for the run-in. Comment FRIDAY and we'll map it out.
- **Sat · GROW:** Tradesmen. Word of mouth is great. But it only grows as fast as your last job. Finish a job, maybe you
  get a referral. Have a quiet month, and so does your phone. Ads don't wait for your last job. They put you in front
  of people near you, every single day. Same great work. Way more people seeing it. Comment GROW and we'll show you how.
- **Sun · RISK:** Tradesmen. Tried an agency before and got burned? Fair enough. So here's the deal. Ten qualified
  leads in thirty days, or your money back. The risk is on us, not you. We run Facebook and Instagram ads for your
  business, and the enquiries come straight to your phone. Comment RISK and we'll show you how.

## Build
`python3 kit.py <day-dir>` writes `<day-dir>/hyperframes/index.html` from `scenes.html/.css/.js` + `meta.json`
(shared look, captions, CTA end card). Audio: `python3 ../../make_cues.py . <dur> accents.json`, then
`python3 ../build_audio.py cues.json vo.wav --music ../music/bed_a_bright_techhouse.mp3 --bed-db -4 -o hyperframes/assets/audio.wav`
(VO pre-levelled with `loudnorm I=-12`), then `hyperframes check` + `render`.

## Update: Wed–Sun built with a local voice (no ElevenLabs credits)
Ryan: "Use your own voice." Claude has no voice of its own, so Wed–Sun use **Piper** (open-source neural TTS run in
the session) with the **LibriTTS-high** model, speaker 675 (female; picked by pitch and pace across 60 speakers).
- Licence: LibriTTS is **CC BY 4.0** (commercial use allowed with credit). Credit line for the ad copy or page:
  "Voice: Piper TTS, LibriTTS (CC BY 4.0)". The nicer-sounding Piper "lessac" voice was ruled out: its dataset licence
  is research-only and forbids commercial use.
- Accent is American (no free Irish voice). "one of ye" was changed to "one of you" for this voice.
- `local_vo.py` reads each phrase, trims it, joins with natural pauses, and writes word timings (phrase timing exact,
  words spread by syllables). VO files: `vo/*.wav` + `vo/*_words.json`.
- Outputs: `wed-boost/wed_boost_still_pressing_boost.mp4` (23.3 s), `thu-first/thu_first_ring_back.mp4` (20.3 s),
  `fri-friday/fri_friday_black_friday.mp4` (22.6 s), `sat-grow/sat_grow_word_of_mouth.mp4` (21.4 s),
  `sun-risk/sun_risk_money_back.mp4` (19.5 s). All on bed A, -14 LUFS.
- When ElevenLabs credits are back, any of these can be re-voiced with Laura: generate, transcribe, rebuild (the
  scenes are timed per word, so re-timing is a small edit).
