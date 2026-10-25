"""Southline KITCHEN & BATHROOM makeover ad (silent, 30s), one combined ad for both.
8-part short-form structure: Hook, Lead, Body 1, Open loop, Body 2, Open loop, Body 3, CTA.
Simple look: off-white, black type, one blue accent. Open loops are questions. Stacking cards, highlight-then-zoom on key words.
python3 build_makeovers.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import stack_scenes as S

BLUE = (30, 86, 255)
A.set_theme("clean", accent=BLUE, accent2=BLUE, bg=((248, 247, 244), (240, 238, 233)), blobs=[], grid=False)
SCENES = [  # paced so every line gets read: one idea per beat, ~1s hold on each key line
    S.scene_hook(dur=4.0),    # HOOK       4 quotes stack + get struck out, last one BOOKED -> '4 quotes. 1 yes.' highlight + zoom
    S.scene_lead(dur=3.2),    # LEAD       'costs you an evening.' highlight + zoom -> 15 hrs
    S.scene_body1(dur=4.2, zoom=(0.9, 2.2), you_at=2.35, punch_at=3.0),  # BODY 1 'on a list.' -> pull back to 1 of 80 -> 'Not choosing you.'
    S.scene_question(["So how is the company", "down the road", "booked till summer?"], 2, (2, 2), dur=3.0, gap=0.35),  # OPEN LOOP, zoom on 'summer?'
    S.scene_body2(dur=4.6, scroll=(0.7, 1.4), tap_at=2.0, notes_at=(2.7, 3.2, 3.7)),  # BODY 2 'in the feed.' -> tap -> requests stack
    S.scene_question(["So what stops", "the time-wasters?"], 1, (1, 1), dur=2.8, mode="pop", zoom=1.25, size=110, word_gap=0.13),  # OPEN LOOP
    S.scene_body3(dur=4.6),   # BODY 3     'asks first.' -> 3 question cards build a tower -> ready to book
    S.camera(A.scene_cta_comment("Want buyers,", "not browsers?", "MAKEOVER", "Southline Agency", "Paid ads for kitchen & bathroom companies",
                                 after="to see how.", toast_msg="We'll DM you the details", dur=3.8, logo=A.logo()), [(0.0, 1.2, 540, 600), (0.45, 1.0, 540, 960)]),  # CTA
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
total = v.render(out, transition="whip", tr_frames=5, preview_times=ends, punch=False, drift=0.02, bpm=120)
print(f"rendered {total:.2f}s")
