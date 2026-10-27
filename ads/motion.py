"""Smoother motion for the newer Reels: extra easings, real motion blur on fast moves, per-word masked reveals,
hard offset shadows and any-font text sprites (Playfair, JetBrains Mono). Works on top of adkit."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import adkit as A
from adkit import W, H, clamp

HERE = A.os.path.dirname(A.os.path.abspath(__file__))
FONTS = {
    "serif": (HERE + "/brand/fonts/PlayfairDisplay.ttf", None), "serif-it": (HERE + "/brand/fonts/PlayfairDisplay-Italic.ttf", None),
    "mono": ("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf", None), "mono-b": ("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf", None),
}


# ---- easings (all clamp to 0..1) ----
def expo_out(x): x = clamp(x); return 1 if x >= 1 else 1 - 2 ** (-10 * x)
def quint_out(x): x = clamp(x); return 1 - (1 - x) ** 5
def cubic_io(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def back_out(x, c=1.3): x = clamp(x); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def snap(x, steps=3):
    """stepped ease: holds then jumps, for a stop-motion / sticker feel"""
    x = clamp(x); return math.floor(x * steps + 1e-6) / steps


# ---- fonts / text ----
_ff = {}
def ffont(name, size, wght=None):
    """any font by key (serif, serif-it, mono, mono-b) or an adkit weight (r, m, sb, b, xb, bl); wght sets a variable weight"""
    k = (name, size, wght)
    if k not in _ff:
        if name in FONTS:
            f = ImageFont.truetype(FONTS[name][0], size)
            if wght: f.set_variation_by_axes([wght])
        else: f = A.font(name, size)
        _ff[k] = f
    return _ff[k]

_tc = {}
def ftext(s, name="serif", size=80, col=(20, 20, 20), wght=None, track=0):
    """crisp text sprite in any font (drawn at 2x then downsampled). track = extra letter spacing in px"""
    k = (s, name, size, col, wght, track)
    if k in _tc: return _tc[k]
    f = ffont(name, size * 2, wght); d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    if track:
        widths = [d0.textlength(ch, font=f) for ch in s]; tw = int(sum(widths) + track * 2 * (len(s) - 1))
    else: tw = int(d0.textlength(s, font=f))
    asc, desc = f.getmetrics(); h = asc + desc + 8
    im = Image.new("RGBA", (tw + 16, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if track:
        x = 8
        for ch, wd in zip(s, widths): d.text((x, 4), ch, font=f, fill=col); x += wd + track * 2
    else: d.text((8, 4), s, font=f, fill=col)
    _tc[k] = im.resize((im.width // 2, im.height // 2), Image.LANCZOS); return _tc[k]


# ---- compositing ----
def mb_put(base, sp, x, y, vx=0.0, vy=0.0, alpha=1.0, scale=1.0, rot=0.0, samples=7):
    """put() with motion blur: averages `samples` copies spread along the velocity (px per frame). Still when slow."""
    if alpha <= 0.003: return
    if abs(rot) > 0.05: sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.002: sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.BICUBIC)
    sp_ = np.asarray(sp, np.float32) / 255.0
    if math.hypot(vx, vy) < 2:
        out = sp_
        pad_x = pad_y = 0
    else:
        pad_x, pad_y = int(abs(vx)) + 2, int(abs(vy)) + 2
        acc = np.zeros((sp.height + 2 * pad_y, sp.width + 2 * pad_x, 4), np.float32)
        prem = sp_.copy(); prem[..., :3] *= prem[..., 3:4]
        for i in range(samples):
            f = (i / (samples - 1) - 0.5); ox, oy = int(round(pad_x + vx * f)), int(round(pad_y + vy * f))
            acc[oy:oy + sp.height, ox:ox + sp.width] += prem
        acc /= samples; a = acc[..., 3:4]; acc[..., :3] = np.where(a > 1e-4, acc[..., :3] / np.maximum(a, 1e-4), 0); out = acc
    out = out.copy(); out[..., 3] *= alpha
    im = Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8), "RGBA")
    base.alpha_composite(im, (int(round(x - im.width / 2)), int(round(y - im.height / 2))))

def slide_put(base, sp, x0, y0, x1, y1, p, ease=quint_out, alpha=None, rot0=0.0):
    """move a sprite from (x0,y0) to (x1,y1) over p 0->1 with ease + motion blur from the real per-frame speed"""
    if p <= 0: return
    e, e2 = ease(p), ease(max(0, p - 0.04))
    x, y = x0 + (x1 - x0) * e, y0 + (y1 - y0) * e; vx, vy = (x1 - x0) * (e - e2), (y1 - y0) * (e - e2)
    mb_put(base, sp, x, y, vx, vy, clamp(p / 0.12) if alpha is None else alpha, 1.0, rot0 * (1 - e))

def hard_shadow(sp, dx=14, dy=14, col=(0, 0, 0)):
    """solid offset shadow (no blur): flat poster / brutalist look"""
    out = Image.new("RGBA", (sp.width + abs(dx), sp.height + abs(dy)), (0, 0, 0, 0))
    sh = Image.new("RGBA", sp.size, col + (255,)); sh.putalpha(sp.split()[3])
    out.alpha_composite(sh, (max(0, dx), max(0, dy))); out.alpha_composite(sp, (max(0, -dx), max(0, -dy))); return out

def reveal_lr(base, sp, x, y, p):
    """left-to-right wipe reveal of a sprite (handwriting / ink line), p 0->1"""
    if p <= 0: return
    w = int(sp.width * clamp(p))
    if w > 0: base.alpha_composite(sp.crop((0, 0, w, sp.height)), (int(x - sp.width / 2), int(y - sp.height / 2)))

def words_rise(base, words, cx, cy, t, t0, stagger=0.07, dur=0.45, gap=18, ease=quint_out):
    """a line built from word sprites; each rises from behind its own mask, staggered. Returns total width."""
    tot = sum(w.width for w in words) + gap * (len(words) - 1); x = cx - tot / 2
    for i, w in enumerate(words):
        p = ease((t - t0 - i * stagger) / dur)
        if p > 0:
            off = int(w.height * (1 - p))
            if off < w.height: base.alpha_composite(w.crop((0, 0, w.width, w.height - off)), (int(x), int(cy - w.height / 2 + off)))
        x += w.width + gap
    return tot

def flat_bg(col, grain=1.2, seed=7):
    """solid paper colour with a whisper of grain, so flat backgrounds don't band in compression"""
    arr = np.zeros((H, W, 3), np.float32) + np.array(col, np.float32)
    arr += np.random.default_rng(seed).standard_normal((H, W, 1)) * grain
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
