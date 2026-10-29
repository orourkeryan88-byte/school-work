"""The animation pack (pack_scenes.py) laid over Ryan's own B-roll of himself working (footage/ryan_working_*.mp4),
cut into a different shot under every animation: real clip times, punch-ins and crops so reused footage never looks
the same twice, section titles on freeze frames. The footage is darkened behind the type so white text reads on the
bright office. Soft SFX only (no music), so his track or voiceover goes on top.
python3 build_pack_over_broll.py [--stills]"""
import sys, subprocess
import numpy as np
from PIL import Image
import adkit as A
import trust_scenes as S
import pack_scenes as P
from adkit import W, H, eio, clamp

A.set_theme("midnight", accent=S.ACC, accent2=S.ACC, bg=((8, 10, 14), (4, 5, 8)), blobs=[], grid=False)
P.MIN_DARK = 0.45
OUT = "out/animation_pack/southline_animations_over_broll.mp4"


_clips = {}
def frames(n):
    """all frames of footage/ryan_working_<n>.mp4 at its own size (cached), as one uint8 array"""
    if n not in _clips:
        path = f"footage/ryan_working_{n}.mp4"
        w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
                                       capture_output=True, text=True, check=True).stdout.strip().split(","))
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-r", str(A.FPS), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        _clips[n] = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    return _clips[n]

def shot(n, start, zoom=1.0, fx=0.5, fy=0.5, push=0.06, dur=5.0):
    """B-roll shot: clip n from `start` seconds, cropped to 9:16 and zoomed into (fx, fy), with a slow push-in of
    `push` over the shot so it never sits still. Holds the last frame if the clip runs out."""
    def fn(ts):
        fr = frames(n); i = int(clamp((start + ts) * A.FPS, 0, len(fr) - 1)); im = Image.fromarray(fr[i])
        z = zoom * (1 + push * eio(ts / dur)); sw, sh = im.size
        cw = min(sw, sh * W / H) / z; ch = cw * H / W
        x0 = clamp(fx * sw - cw / 2, 0, sw - cw); y0 = clamp(fy * sh - ch / 2, 0, sh - ch)
        return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    return fn

def title(num, lines, n, at, zoom=1.15, fx=0.5, fy=0.5, dur=1.7):
    """section card on a blurred freeze frame of clip n at `at` seconds"""
    return S.with_shot(S.scene_title(num, lines, 0.0, 1.0, 0.5, 0.5, dur=dur), shot(n, at, zoom, fx, fy, push=0))

w = S.with_shot
# clip 1 (20s): side view at the laptop, then writing in a notebook. clip 2 (6.6s): front-on, typing.
# clip 3 (5s): front-on, writing then looking up.
SCENES = [
    w(P.scene_who(), shot(2, 0.0, 1.0, 0.5, 0.5, dur=4.2)),                                   # face to camera for "I'm Ryan"
    title("01", ["What I do"], 1, 2.0, 1.3, 0.55, 0.45),
    w(P.scene_what(), shot(1, 0.0, 1.0, 0.5, 0.5, dur=4.6)),                                  # typing at the laptop
    title("02", ["How I help"], 3, 4.6, 1.3, 0.45, 0.55),
    w(P.scene_test(), [(0.0, shot(1, 5.0, 1.35, 0.35, 0.5, dur=2.4)), (2.4, shot(1, 7.4, 1.0, 0.5, 0.5, dur=2.4))]),  # punch-in on the laptop, then wide
    w(P.scene_winner(), shot(3, 0.0, 1.15, 0.5, 0.55, dur=5.0)),                              # writing, then looks up
    w(P.scene_back(), [(0.0, shot(1, 10.0, 1.0, 0.5, 0.5, dur=2.6)), (2.6, shot(2, 3.0, 1.5, 0.45, 0.62, dur=2.6))]),  # wide, then tight on hands
    title("03", ["How I'm paid"], 2, 1.0, 1.4, 0.5, 0.42),
    w(P.scene_fee(), shot(1, 14.6, 1.2, 0.55, 0.5, dur=4.6)),                                 # notebook work, slightly closer
    title("04", ["Who it's for"], 1, 18.5, 1.25, 0.6, 0.4),
    w(P.scene_for(), shot(2, 2.0, 1.3, 0.5, 0.45, dur=4.4)),                                  # tight on face, typing
    w(P.scene_cta(), shot(3, 0.4, 1.0, 0.5, 0.5, dur=4.6, push=0.1)),                          # front-on, slow push for the end card
]

if "--stills" in sys.argv:
    row = []
    for dur, fn, _ in SCENES: row.append(fn(dur * 0.7)[0].convert("RGB").resize((216, 384)))
    sheet = Image.new("RGB", (216 * 6, 384 * 2)); [sheet.paste(r_, (216 * (j % 6), 384 * (j // 6))) for j, r_ in enumerate(row)]
    sheet.save("out/animation_pack/over_broll_stills.png"); sys.exit()

v = A.Video(); [v.add(*sc) for sc in SCENES]; t = 0.0; marks = []
for dur, _, _ in SCENES: marks.append(t + dur * 0.7); t += dur
RAW = OUT.replace(".mp4", "_sfx_only.mp4")
total = v.render(RAW, transition="whip", music=False, sfx=True, lufs=-20.0, preview_times=marks)

# slight background music: the soft synth bed from the trust videos, about 8 dB under the SFX; the mix is then
# brought up to -16 LUFS so it isn't quiet next to other Reels
import os, build_trust_audio as BA
bed = "/tmp/pack_bed.wav"; BA.music_bed(total, bed)  # the bed comes out at about -20.6 LUFS
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", RAW, "-i", bed, "-filter_complex",
                "[1:a]volume=-7.5dB,aresample=48000[m];[0:a][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", OUT], check=True)
os.remove(RAW); os.replace(RAW.replace(".mp4", "_preview.png"), OUT.replace(".mp4", "_preview.png"))
print(f"wrote {OUT} ({total:.1f}s)")
