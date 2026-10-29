"""Southline ANIMATION PACK for clothing brands: one short animation per beat, each its own MP4, for Ryan to cut
between B-roll clips of himself working (who I am, what I do, how I help, how I'm paid, who it's for, CTA).
Each clip is 9:16, 30fps, soft SFX only (no music, so it sits under his own track or voiceover).
Also writes the full sequence back to back (whip transitions) as a preview, plus a contact sheet.
python3 build_animation_pack.py [--stills] [--only 03]"""
import sys, os
from PIL import Image
import adkit as A
import trust_scenes as S
import pack_scenes as P

A.set_theme("midnight", accent=S.ACC, accent2=S.ACC, bg=((8, 10, 14), (4, 5, 8)), blobs=[], grid=False)
OUT = "out/animation_pack"; os.makedirs(OUT, exist_ok=True)
title = lambda num, lines, dur=1.7: P.on_bg(S.scene_title(num, lines, 0.0, 1.0, 0.5, 0.5, dur=dur))

# (file name, scene): the order they'd usually go in, with B-roll of Ryan between them
CLIPS = [
    ("01_who_i_am", P.on_bg(P.scene_who())),
    ("02_title_what_i_do", title("01", ["What I do"])),
    ("03_what_i_do", P.on_bg(P.scene_what())),
    ("04_title_how_i_help", title("02", ["How I help"])),
    ("05_step1_test_ads", P.on_bg(P.scene_test())),
    ("06_step2_pick_the_winner", P.on_bg(P.scene_winner())),
    ("07_step3_bring_them_back", P.on_bg(P.scene_back())),
    ("08_title_how_im_paid", title("03", ["How I'm paid"])),
    ("09_fee", P.on_bg(P.scene_fee())),
    ("10_title_who_its_for", title("04", ["Who it's for"])),
    ("11_who_its_for", P.on_bg(P.scene_for())),
    ("12_cta_book_a_call", P.on_bg(P.scene_cta())),
]

only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
clips = [c for c in CLIPS if only is None or c[0].startswith(only)]

if "--stills" in sys.argv:
    for name, (dur, fn, _) in clips:
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (dur * 0.35, dur * 0.7, dur - 0.05)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"{OUT}/still_{name}.png")
    sys.exit()

for name, sc in clips:
    A.Video().add(*sc).render(f"{OUT}/{name}.mp4", transition="cut", music=False, sfx=True, lufs=-20.0)
    print("wrote", name)

if only is None:  # whole pack back to back, for checking the flow
    v = A.Video(); [v.add(*sc) for _, sc in CLIPS]; t = 0.0; marks = []
    for _, (dur, _, _) in CLIPS: marks.append(t + dur * 0.75); t += dur
    v.render(f"{OUT}/00_full_sequence_preview.mp4", transition="whip", music=False, sfx=True, lufs=-20.0, preview_times=marks)
