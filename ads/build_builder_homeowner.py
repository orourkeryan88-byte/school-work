"""Meta ad for a BUILDER client (Ryan gives it to the builder to run), aimed at homeowners who've outgrown the house.
Brief, avatar, pains and copy: out/builder_homeowner_ad_brief.md. Silent-friendly (all on screen), ~25s, music + SFX.
The offer and the 'spring 2027' line must be confirmed with the builder before it runs.
python3 build_builder_homeowner.py [--stills]"""
import sys
from PIL import Image
import adkit as A
import homeowner_scenes as Hs

A.set_theme("navy")
OFFER_BIG = ("Site visit &", "written quote")
OFFER_SUB = "for your extension"
OFFER_CHECKS = ["No obligation", "Itemised, in writing", "Now booking spring 2027"]
FORM = [("What are you planning?", "Kitchen extension"), ("Where's the house?", "Your area"), ("When would you like to start?", "Spring 2027")]

SCENES = [
    Hs.scene_hook(dur=3.6),
    Hs.scene_pains(dur=5.4),
    Hs.scene_fix(dur=5.6),
    Hs.scene_offer(OFFER_BIG, OFFER_SUB, OFFER_CHECKS, dur=4.6),
    Hs.scene_form(FORM, dur=6.0),
]
OUT = "out/builder_homeowner_extension_ad.mp4"

if "--stills" in sys.argv:
    cells = [fn(x)[0].convert("RGB").resize((270, 480)) for dur, fn, _ in SCENES for x in (dur * 0.4, dur - 0.1)]
    sheet = Image.new("RGB", (270 * 5, 480 * 2))
    for j, c in enumerate(cells): sheet.paste(c, (270 * (j // 2), 480 * (j % 2)))
    sheet.save("out/builder_stills.png"); sys.exit()

v = A.Video(); [v.add(*s) for s in SCENES]; t = 0.0; marks = []
for d, _, _ in SCENES: marks.append(t + d * 0.8); t += d
total = v.render(OUT, transition="whip", music=True, sfx=True, preview_times=marks)
print(f"wrote {OUT} ({total:.1f}s)")
