"""Southline PLUMBERS ad 'The Setup' (silent, ~32s). Sells the system, not an outcome.
8-part structure: Hook (poll tap), Lead, Body 1 (count-along), Open loop, Body 2 (step 1), Open loop, Body 3 (steps 2+3), CTA.
Simple dark look with one hi-vis yellow accent; calm pace, key lines hold ~1s.
python3 build_plumbers_setup.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import plumber_scenes as P

YELLOW = (255, 204, 0)
A.set_theme("navy", accent=YELLOW, accent2=YELLOW, bg=((17, 20, 26), (7, 9, 12)), blobs=[(540, 900, 700, YELLOW, 0.03)], grid=True,
            ink=(250, 250, 248), muted=(150, 156, 166))
SCENES = [
    P.scene_hook(dur=3.9),     # HOOK       'Plumbers,' poll 'Ever boosted a post?' -> tap YES -> 42 likes, 3 comments, 0 calls (zoom)
    P.scene_lead(dur=3.2),     # LEAD       'You don't need more posts.' (struck) 'You need a SYSTEM.' (zoom)
    P.scene_body1(dur=4.9),    # BODY 1     count-along: boosting posts, leaflets, lead sites, word of mouth -> 'Tried 2 or more? Keep watching.'
    P.scene_question(["So what does", "a proper system", "actually look like?"], 1, (2, 2), dur=3.0),  # OPEN LOOP
    P.scene_step1(dur=5.0),    # BODY 2     step 1: ad only shows to homeowners near you (map + radius)
    P.scene_question(["But how do you know", "they're serious", "before you ring?"], 1, (1, 1), dur=3.0, mode="pop", zoom=1.45, size=96, word_gap=0.11),  # OPEN LOOP
    P.scene_steps23(dur=6.0),  # BODY 3     step 2: 3 questions first. step 3: texts straight to your phone
    P.camera(A.scene_cta_comment("Want this set up", "for your business?", "SETUP", "Southline Agency", "Meta ads for Irish plumbers",
                                 after="to see how.", toast_msg="We'll DM you the setup", dur=4.3, logo=A.logo()), [(0.0, 1.2, 540, 600), (0.45, 1.0, 540, 960)]),  # CTA
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_plumbers_setup.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="whip", tr_frames=5, preview_times=ends, punch=False, drift=0.02, bpm=110)
print(f"rendered {total:.2f}s")
