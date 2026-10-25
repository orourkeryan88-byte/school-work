"""Southline DENTAL ad 'The Report' (silent, ~25s): your agency report counts likes, not patients.
Clinical white + teal, monospaced numbers, white flash cuts. Paid ads for dental clinics (agency offer only).
python3 build_dental_report.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import report_scenes as R

A.set_theme("clinic")
SCENES = [
    R.scene_report_hook(dur=3.7),        # HOOK      'Dentists,' + an agency report: impressions, reach, likes... new patients booked: —
    R.scene_magnifier(dur=3.2),          # OPEN LOOP if your report can't answer that… here's what it's hiding
    R.scene_funnel_cut(dur=5.4),         # BODY 1    where most agencies stop counting -> likes don't fill chairs
    R.scene_count_to_chair(dur=4.6),     # BODY 2    we count all the way to the chair (example numbers)
    R.scene_better_report(dur=3.9),      # the report it should be
    R.scene_report_cta(A.logo(), dur=4.4),  # CTA: logo stamped like a seal, comment REPORT
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_dental_report.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="flash", tr_frames=4, preview_times=ends, drift=0.015)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
