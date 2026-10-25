"""Southline KITCHEN & BATHROOM makeover ad 'Neon Structure' (silent, 30s), one combined ad for both.
Built on the 8-part short-form structure (Hook, Lead, Body 1, Open loop, Body 2, Open loop, Body 3, CTA),
in the neon-glass style of the reference: glowing glass slabs, floor grid, 01/08 counter.
python3 build_makeovers.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import neon_scenes as N

A.set_theme("midnight")
SCENES = [
    N.scene_hook(dur=3.6),                                                     # 01 HOOK      6 quotes resolve -> 6 QUOTES. 1 YES.
    N.scene_lead(dur=3.4),                                                     # 02 LEAD      every 'free' quote costs you the drive, measure-up, design
    N.scene_body1(dur=4.0),                                                    # 03 BODY 1    reason 1: they're price shopping the directories
    N.scene_loop(["So how are the busy ones", "booked till summer", "with buyers, not browsers?"], dur=2.6, n=4),          # 04 OPEN LOOP
    N.scene_body2(dur=4.6),                                                    # 05 BODY 2    reason 2: their work is in the feed
    N.scene_loop(["But this next bit", "kills the", "tyre-kickers."], dur=2.4, n=6),  # 06 OPEN LOOP
    N.scene_body3(dur=5.0),                                                    # 07 BODY 3    reason 3: the ad asks first -> READY TO BOOK
    N.scene_cta(A.logo(), dur=4.4),                                            # 08 CTA       comment MAKEOVER + logo
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_makeovers_neon.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="whip", tr_frames=5, preview_times=ends, punch=True, drift=0.03, bpm=124)
print(f"rendered {total:.2f}s")
