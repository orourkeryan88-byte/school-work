"""Southline video for ONLINE STORES 'Three leaks' (~64s): same format as the trust videos (Ryan's voiceover, B-roll
behind, an animation on every line, the brand end card) but its own script and its own animation set (ecom2_scenes):
who it's for + what we do up front, the store as a leaking shopping bag, three leaks, the fix (Meta ads + email only).
Navy + gold. Timed to the script read at a brisk natural pace; Ryan records the voiceover, then it gets re-timed.
python3 build_ecom.py [--stills] [--music song.mp4]"""
import sys, os, subprocess
from PIL import Image
import adkit as A
import trust_scenes as S
import ecom2_scenes as E
import broll as B
import build_trust_audio as BA

B.KIND = "ecom"
A.set_theme("midnight", accent=E.GOLD, accent2=E.GOLD, bg=((10, 18, 34), (4, 8, 16)), blobs=[], grid=False)
THUMB = "brand/southline_thumb_square.webp"; w = S.with_shot

SCENES = [  # (scene over its B-roll, the line said over it)
    (w(E.scene_callout(dur=3.4, you_at=1.5), B.checkout), "If you run an online store, this one's for you."),
    (w(E.scene_ryan(dur=5.6, chips_at=(4.1, 4.8), sub_at=1.9, sub="for e-commerce brands:"), B.parcels),
     "I'm Ryan from Southline. We do two things for e-commerce brands: Meta ads, and email marketing."),
    (w(E.scene_hook(dur=5.8, bag_at=0.2, pay_at=3.3, intro=False, cap=("Most stores have 3 leaks.", "3 leaks")), B.parcels),
     "Here's the problem. Most online stores have three leaks, and they're paying for all of them."),
    (w(E.scene_burnout(dur=7.2, flat_at=3.0, meter_at=4.4, test_at=2.4, pill_text="Worked last month. Not this month."), B.phone_feed),
     "One: your ads burn out. An ad that worked last month stops working, and your cost per sale keeps going up."),
    (w(E.scene_carts(dur=5.6, carts_at=(0.7, 1.0, 1.3), leave_at=2.2, inbox_at=3.4, gone_at=4.6), B.checkout),
     "Two: abandoned carts. People add to basket, leave, and never hear from you again."),
    (w(E.scene_meter(dur=7.6, faces_at=1.0, meter_at=2.0, email_at=4.6, free_at=5.6), B.dashboard),
     "Three: you're paying for ads to reach people who already bought from you, when an email would reach them for free."),
    (w(E.scene_fix(dur=14.5, split_at=1.4, keep_at=10.6, plug_at=(11.8, 12.3, 12.8)), B.desk),
     "So here's what we do. We run your Meta ads to bring in new customers, and we keep testing so they don't burn out. Then we set up your emails to bring them back: abandoned carts, second orders, all of it. Ads to get them. Email to keep them."),
    (w(E.scene_who(dur=7.2, rows_at=(1.4, 3.9), help_at=5.6), B.parcels),
     "If you're spending on ads but sales feel flat, or you've got no emails going out, that's who we help."),
    (w(E.scene_cta(dur=4.8, drop_at=0.6, ask="Sound like you?", caps=("Comment it, and I'll send you", "how we'd do it for your store.", "your store")), B.checkout),
     "Comment 'leads', and I'll send you how we'd do it for your store."),
    (S.scene_thumb(THUMB, dur=2.5), "(end card / thumbnail, no voice)"),
]

if "--stills" in sys.argv:
    for i, ((dur, fn, _), _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (dur * 0.3, dur * 0.65, dur - 0.2)]
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
cue, t = [], 0.0
for (d, _, _), line in SCENES: cue.append(f"{int(t // 60)}:{t % 60:05.2f}  {line}"); t += round(d * A.FPS) / A.FPS
open("out/southline_ecom_three_leaks_cues.txt", "w").write("\n".join(cue) + "\n"); print(f"rendered {total:.2f}s"); print("\n".join(cue))
