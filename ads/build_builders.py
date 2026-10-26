"""Southline BUILDERS ad 'The Gap' (silent, ~35s). Sells the system (show the work, ask first, a pipeline), not an outcome.
8-part structure: Hook (slider sticker), Lead, Body 1 (spot the problem), Open loop, Body 2 (step 1), Open loop,
Body 3 (steps 2+3), CTA. Concrete grey + black + one safety-orange accent; calm pace.
python3 build_builders.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import builder_scenes as B
from stack_scenes import camera

ORANGE = (255, 92, 0)
A.set_theme("cream", accent=ORANGE, accent2=ORANGE, bg=((236, 234, 229), (225, 222, 216)), blobs=[], grid=True,
            ink=(24, 24, 22), muted=(120, 116, 108))
SCENES = [
    B.scene_hook(dur=3.8),            # HOOK      'Builders,' slider 'How full are your next 8 weeks?' dragged 7/8 -> 2/8. 'Be honest.'
    B.scene_lead(dur=3.2),            # LEAD      'When a job finishes with nothing lined up, the wages don't stop.'
    B.scene_gap(dur=5.0),             # BODY 1    spot the problem: 8-week schedule, countdown, THE GAP stamped on weeks 5-8
    B.scene_typed(["So how do some builders", "have the next job lined up", "before this one ends?"], 1, "the next job", dur=3.6),  # OPEN LOOP
    B.scene_show(dur=5.2),            # BODY 2    01 show the work: extension builds brick by brick in a sponsored post
    B.scene_typed(["But how do you sort", "the dreamers from the ones", "ready to build?"], 2, "ready to build?", dur=3.3),  # OPEN LOOP
    B.scene_ask_pipeline(dur=6.6),    # BODY 3    02 ask first (form taps) -> 03 pipeline board, card slides to BOOKED
    camera(A.scene_cta_comment("Want this pipeline", "built for you?", "PIPELINE", "Southline Agency", "Meta ads for Irish builders",
                               after="to see how.", toast_msg="We'll DM you how it works", dur=4.4, logo=A.logo()), [(0.0, 1.2, 540, 600), (0.45, 1.0, 540, 960)]),  # CTA
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.5, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_builders_gap.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="wipe", tr_frames=8, preview_times=ends, punch=False, drift=0.015, bpm=100)
print(f"rendered {total:.2f}s")
