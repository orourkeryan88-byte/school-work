"""Southline KITCHEN ad 'Before / After' (silent, ~25s): your best work gets 11 likes on your page; theirs is in the feed.
Deep sage + oak, cream type, slider-wipe transitions. Paid ads for kitchen companies (agency offer).
python3 build_kitchens.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import kitchen_scenes as K

A.set_theme("sage")
SCENES = [
    K.scene_ba_hook(dur=4.4),             # HOOK      before/after slider sweep -> 'This got 11 likes. on your page.'
    K.scene_booked_till_spring(dur=3.7),  # OPEN LOOP so why is the fitter down the road booked until spring?
    K.scene_camera_roll(dur=5.6),         # BODY 1    your best work is in your camera roll -> theirs is in the feed
    K.scene_comments(dur=4.6),            # BODY 2    we turn your before & afters into enquiries (example comments)
    K.scene_polaroids(A.logo(), dur=4.8), # CTA       polaroid stack, logo sticker, comment KITCHEN
]

if "--stills" in sys.argv:
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
out = "out/southline_kitchens_before_after.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="wipe", tr_frames=10, preview_times=ends, drift=0.03, bpm=100)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
