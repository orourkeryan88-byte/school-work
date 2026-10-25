"""Southline WEDDING VENUE silent ad (~29s): 'they enquired with 6 venues; the first to reply wins'.
Hook -> open loop -> body 1 -> flip (reply first, every time) -> CTA with the SA logo. Plum + champagne theme.
python3 build_venues.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import volt_scenes as V
import niche_scenes as N

A.set_theme("plum")
SCENES = [
    # HOOK  frame 0: 'Wedding venues,' + a couple's enquiry card -> fans out to 6 venues
    N.scene_six_venues(dur=3.9),
    # OPEN LOOP
    V.scene_slam([("WHICH ONE|DO THEY BOOK?", "d"), ("IT'S NOT THE|PRETTIEST.", "dh")], dur=2.5, cuts=[0.0, 1.15], stagger=0.07),
    # BODY 1  the reply race: clock fast-forwards overnight; the 4-minute reply gets the viewing
    N.scene_reply_race(dur=5.6),
    V.scene_slam([("THEY ENQUIRED|AT 11PM.", "d"), ("YOU REPLIED|NEXT MORNING.", "dh")], dur=2.5, cuts=[0.0, 1.1], lock_last=True, stagger=0.07),
    # FLIP
    V.scene_slam([("WHAT IF YOU", "d"), ("REPLIED|FIRST?", "y")], dur=1.7, cuts=[0.0, 0.6], stagger=0.07),
    N.scene_instant_reply(dur=6.0),
    V.scene_slam([("MORE ENQUIRIES IN.", "d"), ("REPLIED TO|FIRST.", "dh")], dur=2.4, cuts=[0.0, 1.0], lock_last=True, stagger=0.07),
    # CTA  (logo only here)
    A.scene_cta_comment("Want this for", "your venue?", "VIEWINGS", "SOUTHLINE AGENCY", "Ads + instant replies for Irish venues",
                        after="for the details.", toast_msg="I'll send you the details", dur=4.0, comment_at=0.4, logo=A.logo()),
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_venues_first_reply.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="whip", preview_times=ends, punch=True, drift=0.035)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
