"""Southline Reel for CLOTHING BRANDS, 'the question you all ask me' v2: same script and timings as
build_clothing_budget.py (so the same voiceover fits), rebuilt in blue with lots of colours and a different
animation in every scene: bouncing letters, phone chat + camera push, colour word pops + confetti, strike and card
flip, coins into colour jars, a colour loop, a frosted-glass offer over drifting blobs, and a comment CTA with confetti.
python3 build_clothing_budget_blue.py [--stills] [--voice vo.mp3]"""
import sys
from PIL import Image
import adkit as A
import blue_scenes as B
import ember_scenes as E

A.set_theme("ocean", bg=(B.BG_TOP, B.BG_BOT), blobs=B.BLOBS, ink=A.WHITE, muted=(170, 190, 230), accent=B.AMBER, accent2=B.CORAL,
            card=(22, 44, 120), card_ink=A.WHITE, grid=True)
SCENES = [  # (scene, the line said over it) - same lines and lengths as the ember version
    (B.scene_letters(dur=2.6), "Clothing brands… you all ask me this."),
    (B.scene_chat(dur=3.4), "How much should I actually be spending on Meta ads?"),
    (B.scene_pop_words(dur=2.4), "And my answer always surprises them."),
    (B.scene_strike_flip(dur=3.6), "It's not about how much you spend… it's where it goes."),
    (E.scene_jars(dur=6.8, cols=(B.MINT, B.AMBER, B.CORAL), pill_col=B.CYAN), "We split your budget three ways. Test new ads. Scale what's already selling. And remind people who looked."),
    (E.scene_loop(dur=4.0, cols=(B.CYAN, B.MINT, B.CORAL)), "Every week, the winner gets more. The weak ones switch off."),
    (B.scene_glass_offer(dur=4.2), "Want yours? On a free fifteen-minute call, I'll map your split for you."),
    (B.with_confetti(A.scene_cta_comment("Want your split?", "Free, 15 minutes.", "SPLIT", "SOUTHLINE AGENCY", "Meta ads for clothing brands",
                                         after="and I'll send the link.", toast_msg="We'll DM you the link", dur=4.0, logo=A.logo()), at=2.15, y=1160),
     "Comment SPLIT and I'll send you the link."),
]

if "--stills" in sys.argv:   # quick check: two frames per scene on one sheet
    sheet = Image.new("RGB", (4 * 360, 4 * 640)); k = 0
    for (dur, fn, _), _ in SCENES:
        for x in (dur * 0.5, dur - 0.1): sheet.paste(fn(x)[0].convert("RGB").resize((360, 640)), ((k % 4) * 360, (k // 4) * 640)); k += 1
    sheet.save("out/_stills.png"); sys.exit()

VOICE = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else None
v = A.Video(); [v.add(*s) for s, _ in SCENES]
ends, t = [], 0
for (d, _, _), _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.4)
total = v.render("out/southline_clothing_budget_blue.mp4", transition="whip", tr_frames=5, bpm=110, punch=True, drift=0.02, preview_times=ends, voice=VOICE)
print(f"rendered {total:.2f}s")
