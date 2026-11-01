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

BODY = [  # everything after the hook is the same in every version, so a test only measures the hook
    Hs.scene_pains(dur=5.4),
    Hs.scene_fix(dur=5.6),
    Hs.scene_offer(OFFER_BIG, OFFER_SUB, OFFER_CHECKS, dur=4.6),
    Hs.scene_form(FORM, dur=6.0),
]
# (output, hook). Hook formulas: 'I'm looking for 5 (avatar) who want (outcome)' / 'Did you know that X% of (avatar)
# are still struggling with (problem)' (2 in 3 = 65.6% over budget, Renno UK homeowner survey 2026, n=300) /
# 'If you're (avatar) and tired of struggling with (problems)'
VERSIONS = [
    ("out/builder_homeowner_extension_ad.mp4", Hs.scene_hook(dur=3.6)),
    ("out/builder_homeowner_hook1_looking_for_5.mp4", Hs.scene_hook_looking(dur=4.2)),
    ("out/builder_homeowner_hook2_did_you_know.mp4", Hs.scene_hook_stat(dur=4.6)),
    ("out/builder_homeowner_hook3_tired_of.mp4", Hs.scene_hook_tired(dur=4.6)),
]
only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None

if "--stills" in sys.argv:
    hooks = [h for o, h in VERSIONS[1:]]
    cells = [fn(x)[0].convert("RGB").resize((270, 480)) for dur, fn, _ in hooks for x in (dur * 0.35, dur - 0.1)]
    sheet = Image.new("RGB", (270 * 6, 480))
    for j, c in enumerate(cells): sheet.paste(c, (270 * j, 0))
    sheet.save("out/builder_hook_stills.png"); sys.exit()

for out, hook in VERSIONS:
    if only and only not in out: continue
    scenes = [hook] + BODY; v = A.Video(); [v.add(*s) for s in scenes]; t = 0.0; marks = []
    for d, _, _ in scenes: marks.append(t + d * 0.8); t += d
    total = v.render(out, transition="whip", music=True, sfx=True, preview_times=marks)
    print(f"wrote {out} ({total:.1f}s)")
