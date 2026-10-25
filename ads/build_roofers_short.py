"""Southline roofers SHORT silent ad (~19s, no voiceover): 'your big job went to the lad down the road'.
Black + safety-orange 'hazard' theme, SA logo on the CTA only. On-screen type carries the whole message.
python3 build_roofers_short.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import volt_scenes as V
import maths_scenes as M
import hook_scenes as K

A.set_theme("hazard")
LOGO = Image.open("brand/southline_logo_badge.png").convert("RGBA")
LEADS = [("Full re-roof", "Rathfarnham · 1960s semi"), ("Flat roof", "Clontarf · kitchen extension"),
         ("Fascias + soffits", "Lucan · 4-bed detached"), ("Full re-roof", "Malahide · bungalow")]

SCENES = [
    # 1 HOOK (frame 0 = 'Roofers,' + a €12,400 re-roof card, then GONE.)  illustrative job + price
    K.scene_job_gone(dur=3.0),
    # 2 TWIST  fast-cut giant type
    V.scene_slam([("HE'S NOT A|BETTER ROOFER.", "d"), ("HE JUST|SHOWED UP|FIRST.", "dh")], dur=2.3, cuts=[0.0, 1.0], lock_last=True),
    # 3 PROOF  11pm feed: the first roofer's ad gets the tap
    K.scene_feed_scroll(dur=3.6, land_at=1.1, tap_at=1.9, win_at=2.4,
                        lines_a=(("11PM.", False), ("THEY'RE ON FACEBOOK…", True)),
                        lines_b=(("FIRST ROOFER THEY SEE", False), ("GETS THE CALL.", True))),
    # 4 SOLUTION
    V.scene_slam([("WE MAKE YOU", "d"), ("THE ONE|THEY SEE.", "dh")], dur=1.7, cuts=[0.0, 0.6], lock_last=True),
    # 5 OUTCOME  big-job enquiries stacking on the lock screen (example leads)
    V.scene_own_leads(LEADS, dur=3.4, lines=(("BIG JOBS.", False), ("STRAIGHT TO YOU.", True)), icon="house",
                      tag="RE-ROOFS · FLAT ROOFS · FASCIAS", tag_at=0.25, lt=[0.45, 0.85, 1.25, 1.65],
                      price_at=2.2, price_txt="NAME. NUMBER. JOB."),
    # 6 OFFER
    A.scene_offer("14-DAY TEST DRIVE", "€0 fee", "Just €300 ad spend.", "See every lead yourself.",
                  ["Re-roofs, flat roofs, fascias", "Leads straight to your phone"], dur=3.0),
    # 7 CTA  (logo appears here only)
    A.scene_cta_comment("Only taking on 2", "roofers this month.", "LEADS", "SOUTHLINE AGENCY", "Meta ads for Irish roofers",
                        after="for the details.", toast_msg="I'll send you the details", dur=3.6, comment_at=0.4, logo=LOGO),
]

if "--stills" in sys.argv:  # quick layout QA: a few frames per scene, no encode
    for i, (dur, fn, _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.45, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

v = A.Video()
for s in SCENES: v.add(*s)
out = "out/southline_roofers_short.mp4"
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.3)
total = v.render(out, transition="whip", preview_times=ends, punch=True)
A.reframe_4x5(out, out.replace(".mp4", "_4x5.mp4"))
print(f"rendered {total:.2f}s")
