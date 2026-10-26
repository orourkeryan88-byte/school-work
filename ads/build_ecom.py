"""Southline E-COMMERCE video 'Three leaks' (~57s): same format as the trust video (code-drawn B-roll, an animation on
every line) aimed at e-commerce brands, in the brand's navy + gold. Sells the two things Southline does: Meta ads and
email marketing. Timed to the script read at a brisk natural pace; Ryan records the voiceover over it (then it gets
re-timed to the recording, like the trust video). Music bed (--music <file>, else a soft synth bed) + quiet SFX,
mastered low (-22 LUFS) so the voiceover sits on top.  python3 build_ecom.py [--stills] [--music song.mp4]"""
import sys, os, subprocess
from PIL import Image
import adkit as A
import trust_scenes as S
import ecom2_scenes as E
import broll as B
import build_trust_audio as BA

A.set_theme("midnight", accent=E.GOLD, accent2=E.GOLD, bg=((10, 18, 34), (4, 8, 16)), blobs=[], grid=False)
THUMB = "brand/southline_thumb_square.webp"; w = S.with_shot

SCENES = [  # (scene over its B-roll, the line(s) said over it)
    (w(E.scene_hook(dur=6.0), B.parcels), "E-commerce brands. Your store has three leaks. And you're probably paying for all of them."),
    (w(E.scene_ryan(dur=4.5), B.parcels), "I'm Ryan, I run Southline. Meta ads and email marketing, for online brands."),
    (w(E.scene_burnout(dur=8.0), B.phone_feed), "Leak one: your ads burn out. Most die in weeks, and if nobody's testing new ones, your cost per sale just keeps climbing."),
    (w(E.scene_carts(dur=7.6), B.checkout), "Leak two: abandoned carts. People add to basket, leave, and never hear from you again. No reminder. No email. Gone."),
    (w(E.scene_meter(dur=8.6), B.dashboard), "And leak three, the expensive one: you're paying Meta to sell to people who already bought from you. When an email would reach them for free."),
    (w(E.scene_fix(dur=12.8), B.desk), "So here's how we fix it. Meta ads that keep testing, to find new customers. And email that brings them back: abandoned carts, second orders, all of it. Ads to get them. Email to keep them."),
    (w(E.scene_cta(dur=5.2), B.checkout), "If your store's leaking, comment 'leads', and I'll send you how we'd plug it."),
    (S.scene_thumb(THUMB, dur=2.5), "(end card / thumbnail, no voice)"),
]

if "--stills" in sys.argv:
    for i, ((dur, fn, _), _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (dur * 0.25, dur * 0.6, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()

MUSIC = sys.argv[sys.argv.index("--music") + 1] if "--music" in sys.argv else None
v = A.Video(); [v.add(*s) for s, _ in SCENES]
raw, out, bed = "out/_ecom_raw.mp4", "out/southline_ecom_three_leaks.mp4", "out/_ecom_music.wav"
ends, t = [], 0
for (d, _, _), _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.4)
total = v.render(raw, transition="whip", tr_frames=4, preview_times=ends, music=False, lufs=None, punch=False, drift=0.0)
BA.song_bed(total, MUSIC, bed) if MUSIC else BA.music_bed(total, bed)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-i", bed, "-filter_complex",
                "[0:a]volume=0.4[s];[1:a]volume=1.0[m];[s][m]amix=inputs=2:normalize=0,lowpass=f=15000,loudnorm=I=-22:TP=-3:LRA=11,aresample=48000[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
os.remove(bed); os.replace(raw.replace(".mp4", "_preview.png"), out.replace(".mp4", "_preview.png")); os.remove(raw)
S.thumb_frame(THUMB).convert("RGB").save("out/southline_ecom_cover.png")
cue, t = [], 0.0
for (d, _, _), line in SCENES: cue.append(f"{int(t // 60)}:{t % 60:05.2f}  {line}"); t += round(d * A.FPS) / A.FPS
open("out/southline_ecom_cues.txt", "w").write("\n".join(cue) + "\n"); print(f"rendered {total:.2f}s"); print("\n".join(cue))
