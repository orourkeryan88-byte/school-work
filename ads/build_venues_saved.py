"""Southline WEDDING VENUE ad 'Saved' (silent, ~28s): couples saved 9 venues and yours wasn't one; on the directories
you're one of hundreds; in their feed you're the only one. Ivory + champagne gold, Playfair serif, soft dissolves.
Paid ads for wedding venues (agency offer only).  python3 build_venues_saved.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import wedding_scenes as WS

A.set_theme("ivory")
SCENES = [
    WS.scene_saved(dur=4.5),          # HOOK      'Wedding venues,' + their saved collection -> 'Yours wasn't one of them.'
    WS.scene_question(dur=3.4),       # OPEN LOOP So where do couples find the venue they fall for?
    WS.scene_hundreds(dur=5.0),       # BODY 1    on the directories… you're one of hundreds
    WS.scene_alone(dur=5.2),          # BODY 2    in their feed… you're the only one on screen
    WS.scene_envelopes(dur=4.0),      # that's where we put you -> viewing requests arrive
    WS.scene_invitation(A.logo(), dur=5.2),  # CTA: invitation, SA logo as the wax seal, comment VIEWINGS
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_venues_saved.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="fade", tr_frames=9, preview_times=ends, drift=0.03, bpm=96)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
