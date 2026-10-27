"""Southline Reel for CLOTHING BRANDS, angle: '3 questions before you spend another euro on Meta ads' (open loop:
most brands can't answer number 3). Each question gets a simple visual (which ad made the sale, who sees the ads,
what happens to people who click and leave), then the fix, a free 15-minute ad review offer and a comment CTA.
Pale sage, forest green, one terracotta. Scene lengths are timed to the voiceover script in
out/southline_clothing_questions_script.md (read at a natural pace). ~31s, 9:16.
python3 build_clothing_questions.py [--stills] [--voice vo.mp3] [--music song.mp4 --out file.mp4]"""
import sys
from PIL import Image
import adkit as A
import sage_scenes as S

A.set_theme("clean", bg=(S.BG, S.BG), blobs=[], grid=False, ink=S.INK, muted=S.MUTED, accent=S.ACC, accent2=S.ACC)
SCENES = [  # (scene, the line said over it)
    (S.scene_hook(dur=3.6), "Three questions before you spend another euro on Meta ads."),
    (S.scene_three(dur=2.4), "Most clothing brands can't answer number three."),
    (S.scene_q1(dur=4.0), "One: which ad actually made the sale? Not likes. Sales."),
    (S.scene_q2(dur=4.0), "Two: who's seeing your ads? New buyers, or the same people?"),
    (S.scene_q3(dur=4.8), "Three: what happens to people who click and don't buy? For most brands… nothing."),
    (S.scene_fix(dur=5.0), "That's what we fix. Every sale tracked. Every audience tested. Everyone who left, reminded."),
    (S.scene_offer(dur=4.4), "Free fifteen-minute ad review. We'll answer all three for your brand."),
    (S.scene_cta(dur=3.0), "Comment REVIEW and I'll send you the link."),
]
if "--music" in sys.argv:   # no-voiceover cut: a callout opener, an extra beat before the fix, slightly tighter reads
    SCENES = [(S.scene_intro(), ""), (S.scene_hook(dur=3.2), ""), (S.scene_three(dur=2.2), ""), (S.scene_q1(dur=4.0), ""), (S.scene_q2(dur=4.0), ""),
              (S.scene_q3(dur=4.4, nothing_at=2.8), ""), (S.scene_couldnt(), ""), (S.scene_fix(dur=4.2, at=(0.8, 1.5, 2.2)), ""),
              (S.scene_offer(dur=4.0), ""), (S.scene_cta(dur=2.8), "")]

if "--stills" in sys.argv:   # quick check: two frames per scene on one sheet
    sheet = Image.new("RGB", (4 * 360, 4 * 640)); k = 0
    for (dur, fn, _), _ in SCENES:
        for x in (dur * 0.55, dur - 0.1): sheet.paste(fn(x)[0].convert("RGB").resize((360, 640)), ((k % 4) * 360, (k // 4) * 640)); k += 1
    sheet.save("out/_stills.png"); sys.exit()

VOICE = sys.argv[sys.argv.index("--voice") + 1] if "--voice" in sys.argv else None
MUSIC = sys.argv[sys.argv.index("--music") + 1] if "--music" in sys.argv else None   # e.g. a song (or a screen recording of one)
v = A.Video(); [v.add(*s) for s, _ in SCENES]
ends, t = [], 0
for (d, _, _), _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.4)
if not MUSIC:
    total = v.render("out/southline_clothing_questions.mp4", transition="fade", tr_frames=5, bpm=100, punch=False, drift=0.0, preview_times=ends, voice=VOICE)
else:
    import os, subprocess
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "out/southline_clothing_questions_music.mp4"
    raw = out.replace(".mp4", "_raw.mp4")
    total = v.render(raw, transition="fade", tr_frames=5, music=False, lufs=None, punch=False, drift=0.012, preview_times=ends)
    start = float(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 1.7   # skip the silence at the top of the recording
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ss", str(start), "-i", MUSIC, "-filter_complex",
                    f"[1:a]atrim=0:{total},asetpts=PTS-STARTPTS,afade=t=in:d=0.4,afade=t=out:st={total - 2.5}:d=2.5,aresample=48000[m];"
                    "[0:a]volume=0.35,aresample=48000[s];[m][s]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    os.replace(raw.replace(".mp4", "_preview.png"), out.replace(".mp4", "_preview.png")); os.remove(raw)
print(f"rendered {total:.2f}s")
