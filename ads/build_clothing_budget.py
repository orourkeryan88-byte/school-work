"""Southline Reel for CLOTHING BRANDS, angle: 'the question you all ask me' (how much should I spend on Meta ads?).
Open loop: my answer surprises them. Answer: it's not how much, it's where it goes, shown as a three-way budget split
(test / scale / remind) and a weekly loop. Offer: a free 15-minute call to map their split. CTA: comment SPLIT.
Ember theme (near-black, orange glow, amber). Meta ads first; email only as the add-on.
Scene lengths are timed to the voiceover in out/southline_clothing_budget_script.md (Ryan records it).
python3 build_clothing_budget.py [--stills] [--voice vo.mp3]"""
import sys
from PIL import Image
import adkit as A
import ember_scenes as E

A.set_theme("ember")
SCENES = [  # (scene, the line said over it)
    (A.scene_callout("Clothing brands,", sub="this is the question you all ask me.", dur=2.6), "Clothing brands… you all ask me this."),
    (E.scene_dms(dur=3.4), "'How much should I actually be spending on Meta ads?'"),
    (A.scene_kinetic([("My answer", "bl", 140, None), ("always", "xb", 90, None), ("surprises them.", "bl", 120, "grad")], underline_line=2, dur=2.4, y0=760, stagger=0.28),
     "And my answer always surprises them."),
    (A.scene_kinetic([("It's not", "xb", 90, (170, 160, 148)), ("how much.", "bl", 130, None), ("It's where", "xb", 90, (170, 160, 148)), ("it goes.", "bl", 150, "grad")],
                     underline_line=3, dur=3.6, y0=640, stagger=0.45), "It's not about how much you spend… it's where it goes."),
    (E.scene_jars(dur=6.8), "We split your budget three ways. Test new ads. Scale what's already selling. And remind people who looked."),
    (E.scene_loop(dur=4.0), "Every week, the winner gets more. The weak ones switch off."),
    (A.scene_offer("FREE 15-MIN CALL", "Your split", "We'll map your budget", "for your brand. Free.", ["Meta ads, run for you", "Your account, your budget", "Email: optional add-on"], dur=4.2),
     "Want yours? On a free fifteen-minute call, I'll map your split for you."),
    (A.scene_cta_comment("Want your split?", "Free, 15 minutes.", "SPLIT", "SOUTHLINE AGENCY", "Meta ads for clothing brands", after="and I'll send the link.",
                         toast_msg="We'll DM you the link", dur=4.0, logo=A.logo()), "Comment SPLIT and I'll send you the link."),
]

if "--stills" in sys.argv:   # quick check: two frames per scene on one sheet
    sheet = Image.new("RGB", (4 * 360, 4 * 640)); k = 0
    for (dur, fn, _), _ in SCENES:
        for x in (dur * 0.55, dur - 0.1): sheet.paste(fn(x)[0].convert("RGB").resize((360, 640)), ((k % 4) * 360, (k // 4) * 640)); k += 1
    sheet.save("out/_stills.png"); sys.exit()

VOICE = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else None
v = A.Video(); [v.add(*s) for s, _ in SCENES]
ends, t = [], 0
for (d, _, _), _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.4)
total = v.render("out/southline_clothing_budget.mp4", transition="whip", tr_frames=5, bpm=110, punch=True, drift=0.02, preview_times=ends, voice=VOICE)
print(f"rendered {total:.2f}s")
