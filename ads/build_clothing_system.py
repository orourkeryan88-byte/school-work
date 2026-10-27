"""Southline Reel for CLOTHING BRANDS, angle: 'Same budget. Why does one sell?' Opens on an open question (two
brands, same ad budget, only one gets orders), answers it with the four-step system we run (several ads, let buyers
pick the winner, move budget to it, retarget anyone who looked), then the offer and a comment CTA.
Clean and simple: off-white, navy, one gold, smooth motion only. Meta ads first; email is the add-on.
~30s, 9:16, no voice baked in.  python3 build_clothing_system.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import clean_scenes as C

A.set_theme("clean", bg=(C.BG, C.BG), blobs=[], grid=False, ink=C.NAVY, muted=C.MUTED, accent=C.GOLD, accent2=C.GOLD)
SCENES = [C.scene_split(dur=4.8, q_at=3.2), C.scene_turn(dur=2.4), C.scene_step_ads(dur=3.0, fan_at=0.9), C.scene_step_test(dur=3.2, race=(0.5, 2.0), win_at=2.1),
          C.scene_step_budget(dur=2.9, shift=(0.8, 1.9)), C.scene_step_retarget(dur=3.1, at=(0.6, 1.2, 1.8)), C.scene_payoff(dur=2.6),
          C.scene_offer(dur=4.2), C.scene_cta(dur=3.8)]

if "--stills" in sys.argv:   # quick check: two frames per scene on one sheet
    sheet = Image.new("RGB", (6 * 300, 3 * 534)); k = 0
    for dur, fn, _ in SCENES:
        for x in (dur * 0.5, dur - 0.1): sheet.paste(fn(x)[0].convert("RGB").resize((300, 534)), ((k % 6) * 300, (k // 6) * 534)); k += 1
    sheet.save("out/_stills.png"); sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
ends, t = [], 0
for d, _, _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.15)
total = v.render("out/southline_clothing_system.mp4", transition="fade", tr_frames=5, bpm=100, punch=False, drift=0.0, preview_times=ends)
print(f"rendered {total:.2f}s")
