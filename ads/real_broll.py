"""Ryan's own B-roll (footage/ryan_working_*.mp4) as shots for the scene system: shot(n, start, ...) -> fn(ts),
with crops, punch-ins and a slow push so reused footage never looks the same twice; title() = section card on a freeze frame."""
import subprocess
import numpy as np
from PIL import Image
import adkit as A
import trust_scenes as S
from adkit import W, H, eio, clamp


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
