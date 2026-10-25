"""Southline DENTAL silent ad (~27s): 'missed calls at lunch = new patients booking elsewhere'.
Hook -> open loop -> body 1 -> flip (AI receptionist answers every call) -> CTA with the SA logo. Mint theme.
python3 build_dental.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import volt_scenes as V
import niche_scenes as N

A.set_theme("mint")
SCENES = [
    # HOOK  frame 0: 'Dentists,' + lunchtime lock screen of missed calls -> NEW PATIENT.
    N.scene_missed_calls(dur=3.9),
    # OPEN LOOP
    V.scene_slam([("SO WHERE|DO THEY GO?", "d"), ("NOT YOUR|VOICEMAIL.", "dh")], dur=2.4, cuts=[0.0, 1.1], stagger=0.07),
    # BODY 1  voicemail -> hang up -> 'dentist near me' -> another practice -> booked  (most callers don't leave a message)
    N.scene_next_practice(dur=5.0),
    V.scene_slam([("YOUR NEW|PATIENT", "d"), ("JUST BOOKED|SOMEWHERE ELSE.", "dh")], dur=2.5, cuts=[0.0, 0.9], lock_last=True, stagger=0.07),
    # FLIP
    V.scene_slam([("WHAT IF EVERY|CALL GOT", "d"), ("ANSWERED?", "y")], dur=1.8, cuts=[0.0, 0.75], stagger=0.07),
    N.scene_ai_answer(dur=5.3),
    V.scene_slam([("MORE NEW PATIENTS IN.", "d"), ("EVERY CALL|ANSWERED.", "dh")], dur=2.4, cuts=[0.0, 1.0], lock_last=True, stagger=0.07),
    # CTA  (logo only here)
    A.scene_cta_comment("Want this for", "your practice?", "PATIENTS", "SOUTHLINE AGENCY", "Ads + AI receptionists for Irish dentists",
                        after="for the details.", toast_msg="I'll send you the details", dur=4.0, comment_at=0.4, logo=A.logo()),
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_dental_missed_calls.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="whip", preview_times=ends, punch=True, drift=0.035)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
