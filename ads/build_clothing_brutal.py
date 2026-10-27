"""Southline Reel for CLOTHING BRANDS, angle: boosting isn't advertising. Brutalist poster look: flat yellow, black,
white, one red; heavy uppercase type, thick borders, hard shadows, hard cuts, motion-blurred slams, sticker slaps.
Sells Meta ads first; email shows up only as the optional add-on.
Hook: BOOSTING POSTS ISN'T RUNNING ADS. Offer: we run your Meta ads, no retainer, pay per new subscriber we bring in.
CTA: comment ADS.  ~27s, 9:16, no voice baked in.  python3 build_clothing_brutal.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import brutal_scenes as B

A.set_theme("lime", bg=(B.YEL, B.YEL), blobs=[], grid=False, ink=B.INK, muted=B.GREY, accent=B.RED, accent2=B.RED, light=True)
SCENES = [B.scene_hook(), B.scene_boost(), B.scene_system(), B.scene_race(), B.scene_deal(), B.scene_cta()]

if "--stills" in sys.argv:   # quick check: two frames per scene on one sheet
    sheet = Image.new("RGB", (4 * 360, 3 * 640)); k = 0
    for dur, fn, _ in SCENES:
        for x in (dur * 0.5, dur - 0.1): sheet.paste(fn(x)[0].convert("RGB").resize((360, 640)), ((k % 4) * 360, (k // 4) * 640)); k += 1
    sheet.save("out/_stills.png"); sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]
total = v.render("out/southline_clothing_brutal.mp4", transition="cut", bpm=128, punch=True, drift=0.0,
                 preview_times=[3.7, 7.6, 12.6, 17.7, 22.7, 26.9])
print(f"rendered {total:.2f}s")
