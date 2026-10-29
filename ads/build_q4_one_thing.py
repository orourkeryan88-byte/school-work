"""Q4 'ONE THING' trust video (out/southline_q4_one_thing_script.md): Q4 can make a clothing brand's year if it tests
its ads early and spends late. No pitch. Animations over Ryan's B-roll, every scene timed to the script read at a
natural pace (so his voiceover drops straight on), on-screen text carries the message on mute, slight music under SFX.
python3 build_q4_one_thing.py [--stills]"""
import sys, os, subprocess
from PIL import Image
import adkit as A
import trust_scenes as S
import pack_scenes as P
import q4_scenes as Q
import build_trust_audio as BA
from real_broll import shot

A.set_theme("midnight", accent=S.ACC, accent2=S.ACC, bg=((8, 10, 14), (4, 5, 8)), blobs=[], grid=False)
P.MIN_DARK = 0.45
OUT = "out/southline_q4_one_thing.mp4"
w = S.with_shot

# (scene over a cut of Ryan's footage, the script line it carries). Footage: clip 1 (20s) side view at the laptop then
# writing; clip 2 (6.6s) front-on typing; clip 3 (5s) front-on writing then looking up.
SCENES = [
    (w(Q.scene_hook(dur=4.0), shot(2, 0.0, 1.05, 0.5, 0.5, dur=4.0, push=0.1)),
     "Q4 can turn a good clothing brand into a million-pound brand… if you do one thing properly."),
    (w(Q.scene_season(dur=6.0), [(0.0, shot(1, 0.0, 1.0, 0.5, 0.5, dur=3.0)), (3.0, shot(1, 3.0, 1.35, 0.4, 0.5, dur=3.0))]),
     "From Black Friday to Christmas, people buy more than at any other time of the year. But ads get more expensive too…"),
    (w(Q.scene_wrong(dur=7.0), [(0.0, shot(3, 0.0, 1.15, 0.5, 0.55, dur=3.5)), (3.5, shot(1, 6.0, 1.0, 0.5, 0.5, dur=3.5))]),
     "Here's where most brands go wrong. They launch their new ads on Black Friday week… with no idea what works."),
    (w(Q.scene_test_now(dur=4.0), shot(2, 2.4, 1.4, 0.5, 0.42, dur=4.0, push=0.12)),
     "The one thing? Test now. Before it gets expensive."),
    (w(P.scene_test(dur=9.0, head_at=0.1, cards_at=(1.0, 1.6, 2.2, 2.8), cap_at=5.6, tag="THE ONE THING", head=("Your best seller.", "4 or 5 different ads."),
                    key="different ads", cap=("Small budget.", "A week or two.")),
       [(0.0, shot(1, 9.5, 1.0, 0.5, 0.5, dur=4.5)), (4.5, shot(3, 0.5, 1.4, 0.45, 0.6, dur=4.5))]),
     "Take your best seller. Make four or five different ads for it… Run them for a week or two on a small budget."),
    (w(P.scene_winner(dur=7.0, bars_at=0.9, win_at=2.8, budget_at=3.8, tag="BY BLACK FRIDAY", head=("You know which", "one sells."), key="sells",
                      cap="A winner, not a guess.", cap_key="not a guess", cap_size=80),
       [(0.0, shot(1, 13.5, 1.2, 0.55, 0.5, dur=3.5)), (3.5, shot(2, 0.0, 1.25, 0.5, 0.5, dur=3.5))]),
     "By Black Friday, you know which one sells. You put the budget behind that one… a winner, not a guess."),
    (w(Q.scene_novdec(dur=5.0), shot(1, 16.5, 1.15, 0.5, 0.5, dur=5.0)),
     "And everyone who looks in November but doesn't buy? Show them that ad again in December, when they're buying gifts."),
    (w(Q.scene_outro(dur=4.0), shot(3, 1.5, 1.0, 0.5, 0.5, dur=4.0, push=0.12)),
     "Test early, spend late. Save this for when you plan your Q4."),
]

if "--stills" in sys.argv:
    cells = []
    for (dur, fn, _), _ in SCENES:
        for x in (dur * 0.45, dur - 0.1): cells.append(fn(x)[0].convert("RGB").resize((216, 384)))
    sheet = Image.new("RGB", (216 * 8, 384 * 2)); [sheet.paste(c, (216 * (j % 8), 384 * (j // 8))) for j, c in enumerate(cells)]
    sheet.save("out/q4_stills.png"); sys.exit()

v = A.Video(); t = 0.0; marks = []; cues = []
for sc, line in SCENES:
    v.add(*sc); cues.append(f"{int(t // 60)}:{t % 60:05.2f}  {line}"); marks.append(t + sc[0] * 0.75); t += sc[0]
RAW = OUT.replace(".mp4", "_sfx_only.mp4")
total = v.render(RAW, transition="whip", music=False, sfx=True, lufs=-20.0, preview_times=marks)
bed = "/tmp/q4_bed.wav"; BA.music_bed(total, bed)  # slight music, about 8 dB under the SFX, then the mix to -16 LUFS
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", RAW, "-i", bed, "-filter_complex",
                "[1:a]volume=-7.5dB,aresample=48000[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", OUT], check=True)
os.remove(RAW); os.replace(RAW.replace(".mp4", "_preview.png"), OUT.replace(".mp4", "_preview.png"))
open(OUT.replace(".mp4", "_cues.txt"), "w").write("\n".join(cues) + "\n")
print(f"wrote {OUT} ({total:.1f}s)")
