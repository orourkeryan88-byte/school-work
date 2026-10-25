"""Southline KITCHEN & BATHROOM makeover ad (silent, 30s), one combined ad for both.
8-part short-form structure: Hook, Lead, Body 1, Open loop, Body 2, Open loop, Body 3, CTA.
Simple look: off-white, black type, one blue accent. Open loops are questions.
python3 build_makeovers.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import structure_scenes as S

BLUE = (30, 86, 255)
A.set_theme("clean", accent=BLUE, accent2=BLUE, bg=((248, 247, 244), (240, 238, 233)), blobs=[], grid=False)
SCENES = [
    S.scene_hook(dur=3.6),                                                     # HOOK       6 quotes struck out, 1 booked -> '6 quotes. 1 yes.'
    S.scene_lead(dur=3.2),                                                     # LEAD       every 'free' quote costs you an evening -> 15 hrs
    S.scene_body1(dur=4.0),                                                    # BODY 1     they found you on a list: 1 of 80 -> collecting quotes
    S.scene_question(["So how is the company", "down the road", "booked till summer", "without chasing a quote?"], hi=2, dur=3.0, gap=0.28),  # OPEN LOOP
    S.scene_body2(dur=4.6),                                                    # BODY 2     their best job is in the feed -> quote requests
    S.scene_question(["But what stops", "the time-wasters", "ever ringing them?"], hi=1, dur=2.6, gap=0.3),  # OPEN LOOP
    S.scene_body3(dur=4.6),                                                    # BODY 3     the ad asks first -> only ready buyers
    A.scene_cta_comment("Want buyers,", "not browsers?", "MAKEOVER", "Southline Agency", "Paid ads for kitchen & bathroom companies",
                        after="to see how.", toast_msg="We'll DM you the details", dur=4.4, logo=A.logo()),  # CTA
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_makeovers.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="whip", tr_frames=5, preview_times=ends, punch=True, drift=0.025, bpm=120)
print(f"rendered {total:.2f}s")
