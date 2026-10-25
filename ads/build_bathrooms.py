"""Southline BATHROOM ad 'Blueprint' (silent, ~25s): six free quotes, one job; the ad's form filters before you drive.
Navy blueprint, white line drawings, mono annotations, hard cuts. Paid ads for bathroom fitters (agency offer).
python3 build_bathrooms.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import blueprint_scenes as B

A.set_theme("blueprint")
SCENES = [
    B.scene_route(dur=4.4),          # HOOK      route to 6 free quotes, each tagged; 6 FREE QUOTES. 1 JOB.
    B.scene_question(dur=3.6),       # OPEN LOOP what if you knew which one would book BEFORE you got in the van?
    B.scene_form(dur=6.0),           # BODY 1    the ad asks the questions before you drive (project, budget, when, photo) -> READY TO BOOK
    B.scene_sort(dur=4.6),           # BODY 2    only drive to the ready ones: VISIT / SKIP
    B.scene_title_block(A.logo(), dur=4.8),  # CTA  architect's title block with the logo, comment BATHROOM
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_bathrooms_blueprint.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="cut", preview_times=ends, drift=0.02, bpm=110)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
