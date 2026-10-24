"""adkit: 9:16 motion-graphic ad engine (PIL + numpy + ffmpeg). Effects, gradient themes, synthesized SFX/beat.
Usage:  import adkit as A; A.set_theme("cream"); v = A.Video(); v.add(*A.scene_kinetic([...])); ...; v.render("out.mp4")
Every scene factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px). events: [(t, sfx_name, gain)]."""
import subprocess, math, wave, os, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SR = 1080, 1920, 30, 44100

# ======================= THEMES / GRADIENTS =======================
THEMES = {
    # name: bg top, bg bottom, blobs [(x,y,radius,rgb,strength)], ink, muted, accent, accent2 (gradient end), card, card_ink, dark_scene
    "cream":    dict(bg=((246, 244, 239), (238, 234, 226)), blobs=[(540, 820, 700, (255, 200, 150), 0.10)], ink=(17, 17, 16), muted=(120, 116, 108),
                     accent=(232, 93, 42), accent2=(255, 150, 60), card=(255, 255, 255), card_ink=(17, 17, 16), grid=True, light=True),
    "midnight": dict(bg=((18, 16, 30), (6, 6, 12)), blobs=[(250, 600, 520, (110, 70, 255), 0.55), (880, 1350, 560, (40, 120, 255), 0.45)],
                     ink=(245, 245, 250), muted=(150, 150, 170), accent=(124, 92, 255), accent2=(56, 189, 248), card=(28, 27, 40), card_ink=(245, 245, 250), grid=True, light=False),
    "ember":    dict(bg=((36, 26, 22), (10, 10, 10)), blobs=[(800, 500, 480, (232, 93, 42), 0.55), (200, 1500, 420, (255, 170, 60), 0.25)],
                     ink=(245, 240, 232), muted=(170, 160, 148), accent=(232, 93, 42), accent2=(255, 190, 70), card=(30, 26, 24), card_ink=(245, 240, 232), grid=False, light=False),
    "ocean":    dict(bg=((8, 26, 44), (3, 10, 20)), blobs=[(300, 500, 520, (0, 190, 255), 0.45), (850, 1400, 520, (0, 255, 190), 0.30)],
                     ink=(240, 250, 255), muted=(140, 170, 190), accent=(0, 190, 255), accent2=(0, 255, 190), card=(14, 34, 52), card_ink=(240, 250, 255), grid=True, light=False),
    "lime":     dict(bg=((16, 18, 14), (8, 9, 7)), blobs=[(540, 700, 600, (170, 255, 60), 0.25)], ink=(240, 245, 235), muted=(150, 160, 140),
                     accent=(170, 240, 40), accent2=(40, 220, 140), card=(26, 30, 22), card_ink=(240, 245, 235), grid=True, light=False),
    "sunset":   dict(bg=((255, 120, 70), (200, 40, 110)), blobs=[(800, 400, 600, (255, 210, 90), 0.6), (200, 1500, 600, (120, 40, 200), 0.5)],
                     ink=(255, 255, 255), muted=(255, 225, 215), accent=(255, 255, 255), accent2=(255, 220, 120), card=(255, 255, 255), card_ink=(30, 20, 30), grid=False, light=False),
    "clean":    dict(bg=((255, 255, 255), (244, 245, 248)), blobs=[(540, 700, 700, (120, 140, 255), 0.06)], ink=(12, 14, 20), muted=(110, 115, 130),
                     accent=(37, 99, 235), accent2=(124, 58, 237), card=(255, 255, 255), card_ink=(12, 14, 20), grid=True, light=True),
    "volt":     dict(bg=((16, 17, 12), (5, 5, 4)), blobs=[(540, 760, 640, (212, 255, 0), 0.10), (900, 1500, 420, (255, 226, 0), 0.06)], ink=(245, 247, 240), muted=(160, 165, 150),
                     accent=(212, 255, 0), accent2=(255, 226, 0), card=(26, 28, 22), card_ink=(245, 247, 240), grid=True, light=False),
}
GREEN = (34, 170, 92); WHITE = (255, 255, 255); BLACK = (0, 0, 0)
TH = dict(THEMES["cream"]); _BG = None

def set_theme(name, **override):
    """pick a theme (or override any key, e.g. accent=(255,0,80)); rebuilds the background"""
    global TH, _BG
    TH = dict(THEMES[name]); TH.update(override); _BG = None

def gradient(size, c1, c2, angle=90, c3=None):
    """linear gradient RGBA image. angle 90 = top->bottom, 0 = left->right. optional middle stop c3."""
    w, h = size; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = math.radians(angle); d = xx * math.cos(a) + yy * math.sin(a); d = (d - d.min()) / max(1e-6, d.max() - d.min())
    c1, c2 = np.array(c1, np.float32), np.array(c2, np.float32)
    if c3 is None: arr = c1 * (1 - d[..., None]) + c2 * d[..., None]
    else:
        c3 = np.array(c3, np.float32); m = d[..., None]
        arr = np.where(m < 0.5, c1 * (1 - m * 2) + c3 * (m * 2), c3 * (1 - (m - 0.5) * 2) + c2 * ((m - 0.5) * 2))
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

def mesh_bg(top, bottom, blobs, grain=1.6, grid=False):
    """full-frame background: vertical gradient + soft colour blobs (mesh-gradient look) + grain + optional dot grid"""
    yy, xx = np.mgrid[0:H, 0:W]; g = (yy / H)[..., None].astype(np.float32)
    arr = np.array(top, np.float32) * (1 - g) + np.array(bottom, np.float32) * g
    for cx, cy, r, col, s in blobs:
        b = np.exp(-(((xx - cx) / r) ** 2 + ((yy - cy) / r) ** 2))[..., None]
        arr = arr * (1 - b * s) + np.array(col, np.float32) * b * s
    arr += np.random.default_rng(1).standard_normal((H, W, 1)) * grain
    if grid: arr += ((((xx % 54) == 27) & ((yy % 54) == 27))[..., None] * (-14 if TH["light"] else 18)).astype(np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

def bg():
    global _BG
    if _BG is None: _BG = mesh_bg(*TH["bg"], TH["blobs"], grid=TH["grid"])
    return _BG.copy()
def dark_bg(): return mesh_bg((22, 20, 19), (8, 8, 8), [(540, 900, 600, TH["accent"], 0.18)])

# ======================= PRIMITIVES =======================
FD = "/usr/share/fonts/opentype/inter/"
FW = {"r": "Inter-Regular.otf", "m": "Inter-Medium.otf", "sb": "Inter-SemiBold.otf", "b": "Inter-Bold.otf", "xb": "Inter-ExtraBold.otf", "bl": "Inter-Black.otf"}
_fc = {}
def font(w, s):
    if (w, s) not in _fc:
        for name in (FW.get(w, w), FW["xb"]):
            for path in (FD + name, name):
                try: _fc[(w, s)] = ImageFont.truetype(path, s); break
                except OSError: pass
            if (w, s) in _fc: break
        else: _fc[(w, s)] = ImageFont.truetype("DejaVuSans-Bold.ttf", s)
    return _fc[(w, s)]
def tsize(s, f):
    b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), s, font=f); return b[2] - b[0], b[3] - b[1], b[0], b[1]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 4                       # ease-out
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)                    # ease-in-out
def back(x, c=1.6): x = clamp(x); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2   # overshoot
def spring(x, f=3.2, d=5.0): x = max(0.0, x); return 1 - math.exp(-d * x) * math.cos(f * math.pi * x)

def sprite(w, h, fn, ss=2):
    """draw at 2x then downsample = crisp antialiased UI. fn(draw, scale, image)"""
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0)); fn(ImageDraw.Draw(im), ss, im); return im.resize((w, h), Image.LANCZOS)
def shadowed(sp, blur=30, dy=18, alpha=60, pad=60, color=(0, 0, 0)):
    out = Image.new("RGBA", (sp.width + pad * 2, sp.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", sp.size, color + (255,)); sh.putalpha(sp.split()[3].point(lambda v: v * alpha // 255))
    out.alpha_composite(sh, (pad, pad + dy)); out = out.filter(ImageFilter.GaussianBlur(blur)); out.alpha_composite(sp, (pad, pad)); return out
def put(base, sp, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    """composite sprite centred at (cx,cy) with alpha/scale/rotation"""
    if alpha <= 0.003 or scale <= 0.01: return
    if abs(rot) > 0.05: sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.002: sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))), Image.BICUBIC)
    if alpha < 0.997: sp = sp.copy(); sp.putalpha(sp.split()[3].point(lambda v: int(v * alpha)))
    base.alpha_composite(sp, (int(round(cx - sp.width / 2)), int(round(cy - sp.height / 2))))
def put_rise(base, sp, cx, cy, p):
    """masked reveal: sprite slides up from behind an invisible line (p 0->1)"""
    if p <= 0: return
    off = int(sp.height * (1 - clamp(p)))
    if off < sp.height: base.alpha_composite(sp.crop((0, 0, sp.width, sp.height - off)), (int(cx - sp.width / 2), int(cy - sp.height / 2 + off)))

_ts = {}
def text(s, w="xb", size=80, col=None, grad=None):
    """text sprite. grad=(c1,c2[,angle]) fills the text with a gradient"""
    col = col or TH["ink"]; k = (s, w, size, col, grad)
    if k in _ts: return _ts[k]
    f = font(w, size * 2); tw, th, ox, oy = tsize(s, f)
    m = Image.new("L", (tw + 8, int(size * 2 * 1.25)), 0); ImageDraw.Draw(m).text((4 - ox, int(size * 2 * 0.12)), s, font=f, fill=255)
    if grad: fill = gradient(m.size, grad[0], grad[1], grad[2] if len(grad) > 2 else 0)
    else: fill = Image.new("RGBA", m.size, col + (255,))
    fill.putalpha(m); _ts[k] = fill.resize((m.width // 2, m.height // 2), Image.LANCZOS); return _ts[k]
def fit_size(s, w, start, maxw=980):
    size = start
    while size > 30 and tsize(s, font(w, size))[0] > maxw: size -= 4
    return size

_pc = {}
def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
def pill(s, size=40, bg=None, fg=None, grad=None, w="b"):
    """rounded label. grad=(c1,c2) for gradient fill. fg auto-contrasts with bg"""
    bg = bg or ((17, 17, 16) if TH["light"] else TH["accent"]); fg = fg or ((17, 17, 16) if lum(grad[0] if grad else bg) > 170 else WHITE); k = (s, size, bg, fg, grad, w)
    if k in _pc: return _pc[k]
    f = font(w, size * 2); tw, th, ox, oy = tsize(s, f); pw, ph = tw // 2 + 60, int(size * 2.0)
    shape = sprite(pw, ph, lambda d, ss, im: d.rounded_rectangle((0, 0, pw * ss - 1, ph * ss - 1), ph * ss // 2, fill=(255, 255, 255, 255)))
    body = gradient(shape.size, *grad) if grad else Image.new("RGBA", shape.size, bg + (255,)); body.putalpha(shape.split()[3])
    t = sprite(pw, ph, lambda d, ss, im: d.text((pw * ss / 2 - tw / 2 - ox, ph * ss / 2 - th / 2 - oy), s, font=f, fill=fg))
    body.alpha_composite(t); _pc[k] = body; return body

def ring(im, cx, cy, p, col=None, maxr=620, width=6, r0=120):
    """expanding pulse ring (p 0->1)"""
    if not (0 < p < 1): return
    col = col or TH["accent"]; r = r0 + maxr * eo(p); a = int(150 * (1 - p))
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).ellipse((cx - r, cy - r, cx + r, cy + r), outline=col + (a,), width=width); im.alpha_composite(o)
def underline(im, sp, cx, y, p, col=None, h=12):
    """wipe-in underline under a text sprite"""
    if p <= 0: return
    x0 = cx - sp.width / 2; ImageDraw.Draw(im).rounded_rectangle((x0, y, x0 + sp.width * eo(p), y + h), h // 2, fill=col or TH["accent"])
def shine(sp, p, width=70, strength=0.25):
    """diagonal light sweep across a sprite, clipped to its alpha (p 0->1)"""
    if not (0 < p < 1): return sp
    out = sp.copy(); h, w = sp.height, sp.width; yv, xv = np.mgrid[0:h, 0:w]
    pos = -400 + (w + 800) * eio(p); band = np.exp(-(((xv + yv * 0.45) - pos) / width) ** 2) * strength
    a = (band * np.asarray(sp.split()[3], np.float32)).astype(np.uint8)
    hl = Image.new("RGBA", sp.size, (255, 255, 255, 0)); hl.putalpha(Image.fromarray(a)); out.alpha_composite(hl); return out
def tap(im, cx, cy, t, t_tap, t_in=0.6, t_out=0.6, from_dx=200, from_dy=350):
    """fake finger: glides in, presses at t_tap, ripple"""
    if not (t_tap - t_in < t < t_tap + t_out): return
    k = eo((t - (t_tap - t_in)) / (t_in * 0.8)); x = cx + from_dx * (1 - k); y = cy + from_dy * (1 - k); al = clamp((t_tap + t_out - t) / 0.25)
    r = 34 - 8 * (1 - clamp(abs(t - t_tap) / 0.1))
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(o).ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, int(210 * al)), outline=(17, 17, 16, int(120 * al)), width=3)
    im.alpha_composite(o); ring(im, cx, cy, (t - t_tap) / 0.6, maxr=220, width=5, r0=30)
def count(v, t, t0, dur, step=100):
    """rolling number value"""
    return int(round(v * eo((t - t0) / dur) / step) * step)
def money(v, cur="€", plus=False): return ("+" if plus else "") + f"{cur}{v:,}"

# ======================= UI COMPONENTS =======================
def card_sprite(w, h, draw, fill=None, radius=44, outline=None, grad=None, shadow=True):
    """generic rounded card: draw(d, s) adds content at 2x scale"""
    def fn(d, s, im):
        if grad:
            g = gradient((w * s, h * s), *grad); m = Image.new("L", (w * s, h * s), 0)
            ImageDraw.Draw(m).rounded_rectangle((0, 0, w * s - 1, h * s - 1), radius * s, fill=255); g.putalpha(m); im.alpha_composite(g)
        else: d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), radius * s, fill=fill or TH["card"])
        if outline: d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), radius * s, outline=outline, width=2 * s)
        draw(d, s)
    sp = sprite(w, h, fn); return shadowed(sp, blur=26, dy=16, alpha=45 if TH["light"] else 110) if shadow else sp

def check(d, s, x, y, col=GREEN):
    d.ellipse((x * s, y * s, (x + 44) * s, (y + 44) * s), fill=col)
    d.line([((x + 12) * s, (y + 23) * s), ((x + 20) * s, (y + 31) * s), ((x + 34) * s, (y + 14) * s)], fill=WHITE, width=6 * s, joint="curve")

def notif(app, title, body, time, icon="S"):
    """iOS-style lock-screen notification"""
    w = 820
    def dr(d, s):
        d.rounded_rectangle((30 * s, 36 * s, 114 * s, 120 * s), 22 * s, fill=TH["accent"])
        f = font("bl", 52 * s); tw, th, ox, oy = tsize(icon, f); d.text((72 * s - tw / 2 - ox, 78 * s - th / 2 - oy), icon, font=f, fill=WHITE)
        d.text((140 * s, 34 * s), app.upper(), font=font("sb", 24 * s), fill=(120, 116, 108))
        d.text(((w - 40) * s - tsize(time, font("m", 24 * s))[0], 34 * s), time, font=font("m", 24 * s), fill=(120, 116, 108))
        d.text((140 * s, 72 * s), title, font=font("b", 36 * s), fill=(17, 17, 16))
        d.text((140 * s, 120 * s), body, font=font("m", 30 * s), fill=(80, 78, 72))
    sp = sprite(w, 186, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, 186 * s - 1), 44 * s, fill=(255, 255, 255, 250)), dr(d, s)))
    return shadowed(sp, blur=22, dy=14, alpha=45, pad=40)

PW, PH = 900, 1640
def phone(date="Friday 24 October", clock="9:41", wall=None):
    """phone mockup with gradient wallpaper. wall=(top,bottom,glow) colours"""
    top, bot, glow = wall or ((40, 34, 31), (12, 12, 14), TH["accent"])
    body = sprite(PW, PH, lambda d, s, im: (d.rounded_rectangle((0, 0, PW * s - 1, PH * s - 1), 130 * s, fill=(20, 20, 20)),
                                            d.rounded_rectangle((16 * s, 16 * s, (PW - 16) * s, (PH - 16) * s), 116 * s, fill=(0, 0, 0))))
    sw, sh = PW - 44, PH - 44; y2, x2 = np.mgrid[0:sh, 0:sw]; g = (y2 / sh)[..., None]
    arr = np.array(top, np.float32) * (1 - g) + np.array(bot, np.float32) * g
    arr += np.exp(-(((x2 - sw * 0.7) / 380.0) ** 2 + ((y2 - 300) / 380.0) ** 2))[..., None] * np.array(glow, np.float32) * 0.6
    wl = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    m = sprite(sw, sh, lambda d, s, im: d.rounded_rectangle((0, 0, sw * s - 1, sh * s - 1), 108 * s, fill=(255, 255, 255, 255)))
    body.paste(wl, (22, 22), m.split()[3]); d = ImageDraw.Draw(body)
    d.rounded_rectangle((PW // 2 - 130, 52, PW // 2 + 130, 120), 34, fill=(0, 0, 0))
    for s_, f, y in ((date, font("sb", 38), 210), (clock, font("sb", 220), 270)):
        tw, th, ox, oy = tsize(s_, f); d.text((PW / 2 - tw / 2 - ox, y - oy), s_, font=f, fill=(255, 255, 255, 235))
    return body

def job_card(title, sub, value, icon="bolt", value_col=GREEN, w=940):
    """stack card: icon tile, title, sub, +value. icon: bolt|drop|house|dot"""
    def dr(d, s):
        d.rounded_rectangle((40 * s, 50 * s, 160 * s, 170 * s), 30 * s, fill=tuple(int(c * 0.15 + 255 * 0.85) for c in TH["accent"]) if TH["light"] else tuple(int(c * 0.3) for c in TH["accent"]))
        bx, by, a = 100 * s, 110 * s, TH["accent"]
        if icon == "bolt": d.polygon([(bx + 8 * s, by - 44 * s), (bx - 24 * s, by + 6 * s), (bx - 2 * s, by + 6 * s), (bx - 10 * s, by + 44 * s), (bx + 24 * s, by - 8 * s), (bx + 2 * s, by - 8 * s)], fill=a)
        elif icon == "drop": d.polygon([(bx, by - 44 * s), (bx - 30 * s, by + 4 * s), (bx + 30 * s, by + 4 * s)], fill=a); d.ellipse((bx - 30 * s, by - 26 * s, bx + 30 * s, by + 34 * s), fill=a)
        elif icon == "house": d.polygon([(bx, by - 40 * s), (bx - 38 * s, by - 4 * s), (bx + 38 * s, by - 4 * s)], fill=a); d.rectangle((bx - 28 * s, by - 6 * s, bx + 28 * s, by + 36 * s), fill=a)
        else: d.ellipse((bx - 26 * s, by - 26 * s, bx + 26 * s, by + 26 * s), fill=a)
        d.text((196 * s, 56 * s), title, font=font("b", 40 * s), fill=TH["card_ink"])
        d.text((196 * s, 124 * s), sub, font=font("m", 32 * s), fill=TH["muted"])
        f = font("xb", 50 * s); tw, th, ox, oy = tsize(value, f); d.text(((w - 44) * s - tw - ox, 110 * s - th / 2 - oy), value, font=f, fill=value_col)
    return card_sprite(w, 220, dr, outline=(232, 228, 220) if TH["light"] else None)

def step_card(n, title, sub, highlight=False):
    w = 880
    def dr(d, s):
        d.ellipse((44 * s, 55 * s, 164 * s, 175 * s), fill=TH["accent"] if highlight else TH["card_ink"])
        f = font("xb", 56 * s); tw, th, ox, oy = tsize(str(n), f)
        d.text((104 * s - tw / 2 - ox, 115 * s - th / 2 - oy), str(n), font=f, fill=WHITE if highlight or TH["light"] else TH["card"])
        d.text((200 * s, 58 * s), title, font=font("b", 46 * s), fill=TH["card_ink"]); d.text((200 * s, 128 * s), sub, font=font("m", 34 * s), fill=TH["muted"])
    return card_sprite(w, 230, dr)

def offer_card(badge, big, line1, line2, checks, grad=None):
    """big dark offer card. grad=(c1,c2,angle) for a gradient card body"""
    w, h = 920, 540 + 80 * len(checks) + 30
    def dr(d, s):
        f = font("b", 28 * s); tw, th, ox, oy = tsize(badge, f); bw = tw / s + 80
        d.rounded_rectangle((60 * s, 60 * s, (60 + bw) * s, 116 * s), 28 * s, fill=TH["accent"]); d.text(((60 + bw / 2) * s - tw / 2 - ox, 88 * s - th / 2 - oy), badge, font=f, fill=(17, 17, 16) if lum(TH["accent"]) > 170 else WHITE)
        d.text((56 * s, 150 * s), big, font=font("bl", fit_size(big, "bl", 160, 800) * s), fill=WHITE)
        d.text((60 * s, 340 * s), line1, font=font("b", 60 * s), fill=(235, 232, 225))
        d.text((60 * s, 412 * s), line2, font=font("b", 60 * s), fill=TH["accent2"] if TH["accent"] == WHITE else TH["accent"])
        d.line((60 * s, 540 * s, (w - 60) * s, 540 * s), fill=(255, 255, 255, 40), width=2 * s)
        for i, c in enumerate(checks):
            y = 590 + i * 80; check(d, s, 60, y); d.text((130 * s, (y + 2) * s), c, font=font("sb", 40 * s), fill=(235, 232, 225))
    sp = sprite(w, h, lambda d, s, im: (_card_body(d, s, im, w, h, grad), dr(d, s)))
    return shadowed(sp, blur=40, dy=30, alpha=110, pad=80)
def _card_body(d, s, im, w, h, grad):
    if grad:
        g = gradient((w * s, h * s), *grad); m = Image.new("L", (w * s, h * s), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w * s - 1, h * s - 1), 56 * s, fill=255); g.putalpha(m); im.alpha_composite(g)
    else: d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 56 * s, fill=(17, 17, 16))

def button(label, w=880, h=160, pressed=False, grad=None):
    """CTA button with glow + arrow. grad=(c1,c2) for gradient fill"""
    c1 = TH["accent"]; c2 = TH["accent2"]
    body = gradient((w * 2, h * 2), *(grad or (c1, c2)), 0) if grad or TH.get("grad_buttons") else Image.new("RGBA", (w * 2, h * 2), c1 + (255,))
    if pressed: body = Image.blend(body, Image.new("RGBA", body.size, (0, 0, 0, 255)), 0.12)
    m = Image.new("L", body.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), h, fill=255); body.putalpha(m)
    d = ImageDraw.Draw(body); f = font("xb", 104); tw, th, ox, oy = tsize(label, f)
    fg = (17, 17, 16) if c1 == WHITE else WHITE
    d.text((w - tw / 2 - ox - 48, h - th / 2 - oy), label, font=f, fill=fg)
    ax = w + tw / 2 + 8; d.line([(ax, h), (ax + 88, h)], fill=fg, width=16); d.line([(ax + 48, h - 40), (ax + 92, h), (ax + 48, h + 40)], fill=fg, width=16, joint="curve")
    sp = body.resize((w, h), Image.LANCZOS); out = Image.new("RGBA", (w + 160, h + 160), (0, 0, 0, 0))
    gl = Image.new("RGBA", sp.size, c1 + (0,)); gl.putalpha(sp.split()[3].point(lambda v: v * 120 // 255))
    out.alpha_composite(gl, (80, 100)); out = out.filter(ImageFilter.GaussianBlur(28)); out.alpha_composite(sp, (80, 80)); return out

def comment_box(typed, caret, placeholder="Add a comment…"):
    w, h = 900, 150; acc = (17, 17, 16) if lum(TH["accent"]) > 170 else TH["accent"]
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 75 * s, fill=WHITE, outline=(225, 221, 212), width=3 * s)
        d.ellipse((24 * s, 25 * s, 124 * s, 125 * s), fill=(230, 226, 218))
        d.ellipse((56 * s, 44 * s, 92 * s, 80 * s), fill=(190, 185, 175)); d.chord((38 * s, 82 * s, 110 * s, 150 * s), 180, 360, fill=(190, 185, 175))
        f = font("b", 52 * s)
        if typed: d.text((160 * s, 46 * s), typed, font=f, fill=(17, 17, 16))
        else: d.text((160 * s, 50 * s), placeholder, font=font("m", 44 * s), fill=(160, 156, 148))
        if caret:
            x = 160 * s + (tsize(typed, f)[0] + tsize(typed, f)[2] + 8 * s if typed else 0); d.rectangle((x, 44 * s, x + 5 * s, 108 * s), fill=acc)
        f2 = font("xb", 46 * s); tw, th, ox, oy = tsize("Post", f2)
        d.text(((w - 50) * s - tw - ox, h * s / 2 - th / 2 - oy), "Post", font=f2, fill=acc if typed else (200, 196, 190))
    return shadowed(sprite(w, h, fn), blur=26, dy=14, alpha=40)

def toast(msg, ok=True):
    f = font("b", 76); tw, th, ox, oy = tsize(msg, f); w, h = tw // 2 + 130, 92
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), h * s // 2, fill=(17, 17, 16))
        if ok: check(d, s, 28, 24)
        d.text((92 * s - ox, h * s / 2 - th / 2 - oy), msg, font=f, fill=WHITE)
    return sprite(w, h, fn)

# ======================= SCENES =======================
def scene_kinetic(lines, dur=2.4, y0=740, gap=None, stagger=0.32, shake=True, underline_line=None):
    """masked word-rise hook. lines = [(text, weight, size, colour|None|'accent'|'grad'), ...]. first lines slam with shake."""
    sps = []
    for s, w, size, c in lines:
        size = fit_size(s, w, size)
        sps.append(text(s, w, size, grad=(TH["accent"], TH["accent2"], 0)) if c == "grad" else text(s, w, size, TH["accent"] if c == "accent" else c))
    ys = []; y = y0
    for sp in sps: ys.append(y); y += gap or sp.height * 1.05
    def fn(t):
        im = bg(); sh = 0
        for i, (sp, yy) in enumerate(zip(sps, ys)):
            k0 = i * stagger; put_rise(im, sp, W / 2, yy, eo((t - k0) / 0.3))
            if shake and i < 2 and 0 <= t - k0 < 0.18: sh = 10 * (1 - (t - k0) / 0.18)
        if underline_line is not None:
            sp = sps[underline_line]; underline(im, sp, W / 2, ys[underline_line] + sp.height / 2 + 6, (t - underline_line * stagger - 0.3) / 0.35)
        return im, sh
    ev = [(i * stagger, "hit" if i < 2 else "whoosh", 0.9 if i < 2 else 0.4) for i in range(len(lines))]
    return dur, fn, ev

def scene_counter_hook(top, value, bottom, sub=None, cur="€", plus=True, dur=2.9, pill_text=None):
    """'Electricians, this is how we made a client' -> rolling +€60,000 -> 'in extra revenue.'"""
    def fn(t):
        im = bg(); sh = 0
        if pill_text: put(im, pill(pill_text, 34), W / 2, 430, eo(t / 0.25), 0.8 + 0.2 * spring(t / 0.4))
        for i, (s, w, sz) in enumerate(top):
            sp = text(s, w, fit_size(s, w, sz)); put_rise(im, sp, W / 2, 560 + i * 160, eo((t - i * 0.35) / 0.28))
        if t < 0.16: sh = 10 * (1 - t / 0.16)
        land = t >= 1.6; v = count(value, t, 0.7, 0.9)
        if t > 0.65:
            sp = text(money(v, cur, plus), "bl", fit_size(money(value, cur, plus), "bl", 168), grad=(TH["accent"], TH["accent2"], 0) if land else None)
            put(im, sp, W / 2, 880, clamp((t - 0.65) / 0.12), 1 + (0.12 * (1 - eo((t - 1.6) / 0.3)) if land else 0))
        if 1.6 <= t < 1.78: sh = 12 * (1 - (t - 1.6) / 0.18)
        bsp = text(bottom, "xb", fit_size(bottom, "xb", 66)); put_rise(im, bsp, W / 2, 1050, eo((t - 1.7) / 0.3))
        underline(im, bsp, W / 2, 1095, (t - 1.9) / 0.35)
        if sub: put_rise(im, text(sub, "xb", 56, TH["muted"]), W / 2, 1180, eo((t - 2.1) / 0.3))
        return im, sh
    ev = [(0.0, "hit", 0.9), (0.35, "swish", 0.5)] + [(0.7 + i * 0.075, "tick", 0.35) for i in range(12)] + [(1.6, "hit", 1.0), (1.6, "coin", 0.7), (1.9, "swish", 0.4)]
    return dur, fn, ev

def scene_phone_leads(leads, app="Southline Leads", counter="{n} new enquir{ies}", dur=5.6, interval=0.42, ages=None):
    """phone springs in; notifications drop & stack (newest on top), haptic buzz, pulse rings, counter pill. leads=[(title, body)]"""
    ages = ages or ["now", "1h", "4h", "Yesterday", "Tue", "Mon", "Sun", "Sat", "Fri", "Thu", "Wed", "Tue"]
    ph0 = phone(); cache = {}
    def N(i, r):
        if (i, r) not in cache: cache[(i, r)] = notif(app, *leads[i], ages[min(r, len(ages) - 1)])
        return cache[(i, r)]
    LT = [0.55 + i * interval for i in range(len(leads))]
    def fn(t):
        im = bg(); arrived = [i for i, lt in enumerate(LT) if t >= lt]
        for i in arrived: ring(im, W / 2, 1060, (t - LT[i]) / 0.9)
        ph = ph0.copy(); nk = eo((t - LT[arrived[-1]]) / 0.38) if arrived else 0
        for rank, i in enumerate(reversed(arrived)):
            if rank == 0: k = (t - LT[i]) / 0.42; cy = 640 - 140 * (1 - spring(k)); al = clamp(k / 0.15); sc = 0.9 + 0.1 * spring(k)
            else: cy = 640 + (rank - 1) * 198 + 198 * nk; al = clamp((PH - 130 - cy) / 120); sc = 1
            if cy > PH - 110: continue
            put(ph, N(i, rank), PW / 2, cy, al, sc)
        hap = 7 * math.sin((t - LT[arrived[-1]]) * 140) if arrived and t - LT[arrived[-1]] < 0.14 else 0
        put(im, ph, W / 2 + hap, 1060 + 1100 * (1 - spring(t / 0.9, f=1.6, d=6)), 1, 0.9 + 0.02 * eio(t / 6), 8 * (1 - eo(t / 0.7)))
        n = len(arrived); bump = 1 + 0.18 * (1 - eo((t - LT[arrived[-1]]) / 0.25)) if arrived else 1
        lbl = counter.replace("{n}", str(n)).replace("{ies}", "ies" if n != 1 else "y").replace("{s}", "s" if n != 1 else "")
        put(im, pill(lbl, 40, TH["accent"] if n == len(leads) else (17, 17, 16)), W / 2, 150, eo(t / 0.4), bump)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.7)] + [(lt, "ping", 0.8) for lt in LT] + [(LT[-1] + 0.05, "hit", 0.6)]

def draw_stack(im, sprites, drops, t, base_y, step=62, max_depth=3.6, from_y=-1500, rot=-7):
    """card-deck stacking: newest drops in with spring + rotation, older cards push back (up, smaller, dimmer). returns shake"""
    landed = [i for i, d0 in enumerate(drops) if t >= d0]
    if not landed: return 0
    nw = landed[-1]; lp = (t - drops[nw]) / 0.45
    for i in landed[:-1]:
        depth = (nw - i) - (1 - spring(lp, f=1.4, d=7))
        if depth > max_depth: continue
        sp = sprites[i]
        if depth > 0.05:
            sp = sp.copy(); ov = Image.new("RGBA", sp.size, TH["bg"][0] + (0,)); ov.putalpha(sp.split()[3].point(lambda v: int(v * min(0.55, 0.16 * depth)))); sp.alpha_composite(ov)
        put(im, sp, W / 2, base_y - step * depth, 1, 1 - 0.05 * depth)
    put(im, sprites[nw], W / 2, base_y + from_y * (1 - spring(lp, f=1.6, d=6.5)), 1, 1.0, rot * (1 - eo(lp * 1.4)))
    return 7 * (1 - (t - drops[nw] - 0.28) / 0.14) if 0.28 <= t - drops[nw] < 0.42 else 0

def scene_stack_total(jobs, header="{n} jobs from Meta ad leads", done_line="extra revenue. One client.", cur="€", icon="bolt", dur=5.6, interval=0.6):
    """running-total header + stacking job cards with +€ float-ups. jobs=[(title, sub, value)]"""
    cards = [job_card(a, b, money(v, cur, True), icon) for a, b, v in jobs]; DR = [0.4 + i * interval for i in range(len(jobs))]
    def fn(t):
        im = bg(); landed = [i for i, d0 in enumerate(DR) if t >= d0]
        tot = sum(jobs[i][2] for i in landed if t >= DR[i] + 0.3); done = len(landed) == len(jobs) and t >= DR[-1] + 0.3
        n = len(landed); put(im, pill(header.replace("{n}", str(n)).replace("jobs", "job" if n == 1 else "jobs"), 36), W / 2, 330, eo(t / 0.3))
        nb = 1 + 0.1 * (1 - eo((t - DR[landed[-1]] - 0.3) / 0.25)) if landed and t >= DR[landed[-1]] + 0.3 else 1
        put(im, text(money(tot, cur), "bl", 170, GREEN if done else None), W / 2, 520, eo(t / 0.3), nb)
        if done: put_rise(im, text(done_line, "xb", fit_size(done_line, "xb", 60), TH["muted"]), W / 2, 660, eo((t - DR[-1] - 0.45) / 0.3))
        sh = draw_stack(im, cards, DR, t, 1240)
        if landed:
            fp = (t - DR[landed[-1]] - 0.3) / 0.6
            if 0 < fp < 1: put(im, text(money(jobs[landed[-1]][2], cur, True), "xb", 64, GREEN), W / 2 + 300, 1070 - 120 * eo(fp), 1 - fp)
        return im, sh
    ev = [(0.0, "whoosh", 0.6)] + sum([[(d, "swish", 0.4), (d + 0.3, "hit", 0.5), (d + 0.32, "coin", 0.6)] for d in DR], []) + [(DR[-1] + 0.45, "shimmer", 0.8)]
    return dur, fn, ev

def scene_steps(steps, title="How it works", mode="stack", dur=2.8):
    """steps=[(title, sub)]; mode 'stack' (deck) or 'slide' (cards slide in with a connector line drawing)"""
    sps = [step_card(i + 1, a, b, i == len(steps) - 1) for i, (a, b) in enumerate(steps)]
    DR = [0.35 + i * 0.6 for i in range(len(steps))] if mode == "stack" else [0.35 + i * 0.45 for i in range(len(steps))]
    tsp = text(title, "xb", 84)
    def fn(t):
        im = bg(); sh = 0
        if mode == "stack":
            put_rise(im, tsp, W / 2, 520, eo(t / 0.35)); sh = draw_stack(im, sps, DR, t, 1120, step=70, from_y=1400, rot=6)
        else:
            put_rise(im, tsp, W / 2, 430, eo(t / 0.35)); lp = eio((t - 0.45) / 1.2)
            if lp > 0: ImageDraw.Draw(im).line((W / 2 - 336, 700, W / 2 - 336, 700 + 270 * (len(steps) - 1) * lp), fill=TH["muted"], width=6)
            for i, sp in enumerate(sps):
                k = (t - DR[i]) / 0.5
                if k > 0: put(im, sp, W / 2 + 140 * (1 - eo(k)), 700 + i * 270, clamp(k / 0.3), 0.92 + 0.08 * spring(k))
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.6)] + [(d + (0.3 if mode == "stack" else 0), "pop", 0.7) for d in DR]

def scene_offer(badge, big, line1, line2, checks, dur=3.2, dark=True, grad=None):
    """offer card punches in on a dark stage, then a light sweep"""
    card = offer_card(badge, big, line1, line2, checks, grad); stage = dark_bg() if dark else None
    def fn(t):
        im = stage.copy() if dark else bg()
        put(im, shine(card, (t - 0.9) / 0.9), W / 2, 940 + 260 * (1 - eo(t / 0.5)), clamp(t / 0.2), 0.85 + 0.15 * spring(t / 0.6, f=1.8, d=5.5))
        return im, (12 * (1 - t / 0.2) if t < 0.2 else 0)
    return dur, fn, [(0.0, "whoosh", 0.8), (0.12, "hit", 1.0), (0.9, "shimmer", 0.6)]

def scene_cta_button(l1, l2, label, brand, brand_sub, dur=3.6, t_tap=1.9):
    b0, b1 = button(label), button(label, pressed=True); s1, s2 = text(l1, "xb", fit_size(l1, "xb", 84)), text(l2, "xb", fit_size(l2, "xb", 84), TH["accent"])
    def fn(t):
        im = bg(); put_rise(im, s1, W / 2, 700, eo(t / 0.32)); put_rise(im, s2, W / 2, 800, eo((t - 0.15) / 0.32))
        p = (t - 0.55) / 0.5
        if p > 0:
            press = 1 - clamp(abs(t - t_tap - 0.06) / 0.1)
            put(im, b1 if press > 0.5 else b0, W / 2, 1060, clamp(p / 0.3), (0.6 + 0.4 * spring(p)) * (1 - 0.06 * press) * (1 + 0.02 * math.sin(max(0, t - 2.3) * 5)))
        tap(im, W / 2 + 330, 1075, t, t_tap)
        c = eo((t - 0.9) / 0.4); put(im, text(brand, "bl", 64), W / 2, 1290 + 20 * (1 - c), c); put(im, text(brand_sub, "m", 38, TH["muted"]), W / 2, 1360 + 20 * (1 - c), c)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.6), (0.55, "pop", 0.8), (t_tap, "click", 1.0), (t_tap + 0.02, "ping", 0.5)]

def scene_cta_comment(l1, l2, keyword, brand, brand_sub, after="to get started.", toast_msg="We'll DM you the details", dur=3.8, comment_at=0.4):
    """'Comment KEYWORD to get started': keyword pill, comment box types it, Post tapped, toast. comment_at: when 'Comment' lands"""
    sh_ = comment_at - 0.4  # shifts the comment part so it lands on the word
    kp = shadowed(pill(keyword, 64, TH["accent"], w="bl"), blur=22, dy=14, alpha=60, pad=40); cw = text("Comment", "xb", 92)
    s1, s2, s3 = text(l1, "xb", fit_size(l1, "xb", 84)), text(l2, "xb", fit_size(l2, "xb", 84), TH["accent"]), text(after, "xb", 92)
    TY = 1.15 + sh_; CH = 0.1; PT = TY + len(keyword) * CH + 0.35; ts = toast(toast_msg); cb = {}
    def CB(ty, c):
        if (ty, c) not in cb: cb[(ty, c)] = comment_box(ty, c)
        return cb[(ty, c)]
    def fn(t):
        im = bg(); put_rise(im, s1, W / 2, 440, eo(t / 0.32)); put_rise(im, s2, W / 2, 540, eo((t - 0.12) / 0.32))
        a = (t - 0.4 - sh_) / 0.4; tot = cw.width + 26 + kp.width - 80
        if a > 0:
            put(im, cw, W / 2 - tot / 2 + cw.width / 2, 780, eo(a))
            put(im, kp, W / 2 - tot / 2 + cw.width + 26 + (kp.width - 80) / 2, 780, clamp(a / 0.5), (0.6 + 0.4 * spring(a * 0.8)) * (1 + 0.03 * math.sin(max(0, t - 1.0 - sh_) * 6)))
        put_rise(im, s3, W / 2, 900, eo((t - 0.6 - sh_) / 0.35))
        b = (t - 0.8 - sh_) / 0.4
        if b > 0:
            n = int(clamp((t - TY) / CH, 0, len(keyword))); posted = t >= PT + 0.08
            caret = (not posted) and (int(t * 3) % 2 == 0 or TY <= t < TY + 0.6)
            put(im, CB("" if posted else keyword[:n], caret), W / 2, 1160 + 60 * (1 - eo(b)), clamp(b / 0.4), 1 - 0.03 * (1 - clamp(abs(t - PT - 0.04) / 0.08)))
        tp = (t - PT - 0.12) / 0.4
        if tp > 0: put(im, ts, W / 2, 1330 + 40 * (1 - eo(tp)), clamp(tp / 0.4), 0.9 + 0.1 * spring(tp))
        tap(im, 915, 1160, t, PT, t_in=0.5, from_dx=120, from_dy=330)
        c = eo((t - 1.0) / 0.4); put(im, text(brand, "bl", 64), W / 2, 1560 + 20 * (1 - c), c); put(im, text(brand_sub, "m", 38, TH["muted"]), W / 2, 1630 + 20 * (1 - c), c)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.6), (comment_at, "pop", 0.8)] + [(TY + i * CH, "tick", 0.5) for i in range(len(keyword))] + [(PT, "click", 1.0), (PT + 0.15, "ping", 0.6)]

def scene_callout(word, sub="you need to watch this.", dur=1.7):
    """BIG ICP callout opener: 'Electricians,' fills the width in gradient text, slam + shake + underline, then the subline rises in"""
    big = text(word, "bl", fit_size(word, "bl", 260, 1000), grad=(TH["accent"], TH["accent2"], 0))
    sb = text(sub, "xb", fit_size(sub, "xb", 84, 940))
    def fn(t):
        im = bg(); sh = 10 * (1 - t / 0.18) if t < 0.18 else 0
        put(im, big, W / 2, 860, clamp(t / 0.08), 1.12 - 0.12 * eo(t / 0.3))
        underline(im, big, W / 2, 860 + big.height / 2 + 4, (t - 0.25) / 0.35, h=14)
        put_rise(im, sb, W / 2, 1095, eo((t - 0.35) / 0.3))
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (0.25, "swish", 0.5), (0.35, "whoosh", 0.4)]

def scene_diary(jobs, title="Your next 2 weeks", days=("Mon", "Tue", "Wed", "Thu", "Fri"), done_label="{n} jobs in the diary", dur=4.9):
    """two-week diary grid (10 cells); job chips pop into days in a scattered order with rings, counter pill turns green when full. jobs = 10 short labels"""
    cw, ch, gap = 180, 290, 15; x0 = (W - (5 * cw + 4 * gap)) / 2; ys = [640, 640 + ch + 70]
    def cell(day, job):
        def dr(d, s):
            d.text((22 * s, 20 * s), day, font=font("sb", 30 * s), fill=TH["muted"])
            if job:
                acc = TH["accent"]; fg = (8, 22, 34) if lum(acc) > 130 else WHITE
                d.rounded_rectangle((14 * s, 80 * s, (cw - 14) * s, 200 * s), 22 * s, fill=acc)
                fs = 30
                while fs > 16 and tsize(job, font("b", fs))[0] > cw - 64: fs -= 1
                f = font("b", fs * s); tw, th, ox, oy = tsize(job, f)
                d.text((cw / 2 * s - tw / 2 - ox, 140 * s - th / 2 - oy), job, font=f, fill=fg)
                check(d, s, cw / 2 - 22, 220, GREEN)
            else: d.rounded_rectangle((14 * s, 80 * s, (cw - 14) * s, 200 * s), 22 * s, outline=TH["muted"], width=2 * s)
        return card_sprite(cw, ch, dr, radius=30, shadow=False)
    empty = [cell(days[i % 5], None) for i in range(10)]; full = [cell(days[i % 5], j) for i, j in enumerate(jobs[:10])]
    order = [0, 3, 1, 6, 4, 8, 2, 9, 5, 7]; DT = {c: 0.75 + k * 0.33 for k, c in enumerate(order)}; last = max(DT.values())
    tsp = text(title, "xb", 84); wk = [text("Week 1", "b", 40, TH["muted"]), text("Week 2", "b", 40, TH["muted"])]
    def fn(t):
        im = bg(); put_rise(im, tsp, W / 2, 400, eo(t / 0.35))
        for r in range(2):
            put(im, wk[r], x0 + wk[r].width / 2, ys[r] - 40, eo((t - 0.2) / 0.3))
            for c in range(5):
                i = r * 5 + c; cx = x0 + c * (cw + gap) + cw / 2; cy = ys[r] + ch / 2
                if t >= DT[i]: k = (t - DT[i]) / 0.4; put(im, full[i], cx, cy, 1, 0.85 + 0.15 * spring(k)); ring(im, cx, cy, k / 1.6, maxr=140, width=4, r0=40)
                else: put(im, empty[i], cx, cy, eo((t - 0.15 - i * 0.03) / 0.3))
        n = sum(1 for i in range(10) if t >= DT[i])
        if n:
            lbl = done_label.replace("{n}", str(n)).replace("jobs", "job" if n == 1 else "jobs")
            put(im, pill(lbl, 40, GREEN if n == 10 else None), W / 2, 1450, 1, 1 + 0.15 * (1 - eo((t - last) / 0.25)) if n == 10 else 1)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.6)] + [(DT[i], "pop", 0.7) for i in range(10)] + [(last + 0.1, "coin", 0.8), (last + 0.15, "shimmer", 0.6)]

# ---- reel-style effects (from the "Effect of the Day" reel) ----
_yy, _xx = np.mgrid[0:H, 0:W]
_DOTS = (((_xx % 11) - 5.5) ** 2 + ((_yy % 11) - 5.5) ** 2 <= (11 * 0.42) ** 2).astype(np.float32)
_SCAN = (0.85 + 0.15 * (np.sin(_yy * 0.9) > 0)).astype(np.float32)
def scene_dot_matrix(lines, dur=1.4, color=None, sub=None, size=None):
    """screen-push-digital: LED dot-matrix text, push-in scale, flicker, glow, chromatic fringe"""
    color = color or (235, 232, 225); m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    size = size or min(fit_size(l, "bl", 230) for l in lines); f = font("bl", size); y = H // 2 - len(lines) * size // 2 - 40
    for l in lines:
        tw, th, ox, oy = tsize(l, f); d.text(((W - tw) // 2 - ox, y - oy + (size - th) // 2), l, font=f, fill=255); y += int(size * 1.02)
    base_mask = m.filter(ImageFilter.GaussianBlur(1.5)); glow0 = np.asarray(base_mask.filter(ImageFilter.GaussianBlur(18)), np.float32) / 255
    def fn(t):
        s = 1.18 - 0.18 * eo(t / 0.35); img = base_mask
        if s > 1.001: nw, nh = int(W * s), int(H * s); img = img.resize((nw, nh), Image.BILINEAR).crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))
        mm = np.asarray(img, np.float32) / 255; fl = 1.0 if t > 0.3 else 0.4 + 0.6 * (int(t * 40) % 2); a = mm * _DOTS * _SCAN * fl; col = np.array(color, np.float32)
        out = np.zeros((H, W, 3), np.float32) + 12 + glow0[..., None] * col * 0.18 + a[..., None] * col * 0.95
        out[..., 0] += np.roll(a, 3, axis=1) * 40; out[..., 2] += np.roll(a, -3, axis=1) * 40
        im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
        if sub: put_rise(im, text(sub, "sb", 46, TH["accent"]), W / 2, 1340, eo((t - 0.25) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "glitch", 0.7)]

def scene_match_cut(word, para, sub=None, dur=2.8):
    """match-cut: blurred paragraph drifting/zooming, highlighted pill word pops in centre"""
    big = Image.new("RGB", (int(W * 1.5), int(H * 1.5)), (240, 237, 230)); d = ImageDraw.Draw(big); f = font("sb", 118)
    words, lines, cur = (para + " ") * 3, [], ""
    for w_ in words.split():
        if tsize(cur + " " + w_, f)[0] > big.width + 300 and cur: lines.append(cur); cur = w_
        else: cur = (cur + " " + w_).strip()
    y = -30
    for l in lines:
        d.text((-140, y), l, font=f, fill=(60, 58, 54)); y += 132
        if y > big.height: break
    blur = big.filter(ImageFilter.GaussianBlur(13)); pl = shadowed(pill(word, 66, TH["accent"], w="xb"), blur=22, dy=14, alpha=80, pad=40)
    def fn(t):
        s = 1.0 + 0.12 * (1 - eo(t / 2.6)); bw, bh = int(W * 1.25 * s), int(H * 1.25 * s); b = blur.resize((bw, bh), Image.BILINEAR)
        ox = (bw - W) // 2 + int(40 * t); oy = (bh - H) // 2; im = b.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
        put(im, pl, W / 2, H / 2 - 60, eo((t - 0.15) / 0.35), 0.6 + 0.4 * back((t - 0.15) / 0.4))
        if sub: put(im, pill(sub, 30, (20, 20, 19)), W / 2, 1200, eo((t - 0.7) / 0.4))
        return im, 0
    return dur, fn, [(0.15, "pop", 0.9), (0.7, "swish", 0.4)]

def scene_float_cards(title, cards, dur=3.6):
    """floating tilted stat cards bobbing. cards=[(label, big, small, accent_bool)]"""
    sps = []
    for lab, big, small, acc in cards:
        def dr(d, s, lab=lab, big=big, small=small, acc=acc):
            lite = acc and lum(TH["accent"]) > 170; tc = (17, 17, 16) if (not acc or lite) else WHITE
            d.text((45 * s, 45 * s), lab, font=font("b", 34 * s), fill=(130, 126, 118) if (not acc or lite) else (255, 225, 205))
            d.text((40 * s, 90 * s), big, font=font("xb", fit_size(big, "xb", 120, 540) * s), fill=tc); d.text((45 * s, 250 * s), small, font=font("sb", 40 * s), fill=tc)
        sps.append(card_sprite(620, 330, dr, fill=None if not acc else (TH["accent2"] if lum(TH["accent"]) > 170 else TH["accent"]), radius=34) if acc else card_sprite(620, 330, dr, fill=(248, 246, 241), radius=34))
    pos = [(W / 2 - 150, 640, -4), (W / 2 + 150, 1030, 3), (W / 2 - 120, 1420, -2)]; tsp = text(title, "xb", 76, WHITE if TH["light"] else None)
    def fn(t):
        im = dark_bg() if TH["light"] else bg(); put_rise(im, tsp, W / 2, 300, eo(t / 0.4))
        for i, (sp, (x, y, ang)) in enumerate(zip(sps, pos)):
            k = t - 0.35 - i * 0.55
            if k <= 0: continue
            p = back(k / 0.5); put(im, sp, x + (1 - p) * (200 if i % 2 else -200), y + math.sin((t + i) * 2.2) * 8, clamp(k / 0.25), 0.7 + 0.3 * p, ang * (1 + (1 - p) * 3))
        return im, 0
    return dur, fn, [(0.35 + i * 0.55, "pop", 0.7) for i in range(len(cards))]

def scene_glass_graph(label, points, big_suffix="", badge="GUARANTEED", dur=3.4):
    """liquid-glass panel over gradient blobs, line chart draws on with glow + area fill, counter, badge pop. points=[(x 0..30, y)]"""
    gb = mesh_bg((16, 16, 16), (10, 10, 12), [(260, 640, 380, TH["accent"], 0.9), (860, 1180, 420, (120, 70, 200), 0.9), (700, 520, 260, TH["accent2"], 0.9)], grain=0.8)
    blur = gb.filter(ImageFilter.GaussianBlur(40)); X0, Y0, X1, Y1 = 80, 520, 1000, 1360
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((X0, Y0, X1, Y1), 48, fill=255)
    stage = gb.copy(); stage.paste(Image.blend(blur, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.14), (0, 0), m)
    ImageDraw.Draw(stage).rounded_rectangle((X0, Y0, X1, Y1), 48, outline=(255, 255, 255, 90), width=3)
    ymax = max(p[1] for p in points) * 1.04; xmax = max(p[0] for p in points); bp = shadowed(pill(badge, 34, TH["accent"]), blur=16, dy=10, alpha=80, pad=30) if badge else None
    def fn(t):
        im = stage.copy(); d = ImageDraw.Draw(im); d.text((X0 + 60, Y0 + 55), label, font=font("b", 34), fill=(255, 255, 255, 190))
        gx0, gy0, gx1, gy1 = X0 + 70, Y0 + 190, X1 - 70, Y1 - 110
        for i in range(6): y = gy1 - (gy1 - gy0) * i / 5; d.line((gx0, y, gx1, y), fill=(255, 255, 255, 35), width=2)
        pr = eio(t / 2.2) * xmax; xy = [(gx0 + (gx1 - gx0) * x / xmax, gy1 - (gy1 - gy0) * y / ymax) for x, y in points]; seg = []
        for (a, b), (xa, _), (xb, _) in zip(zip(xy, xy[1:]), points, points[1:]):
            if pr <= xa: break
            f = clamp((pr - xa) / (xb - xa)); seg += [a, (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)]
        if len(seg) >= 2:
            fl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(fl).polygon(seg + [(seg[-1][0], gy1), (gx0, gy1)], fill=TH["accent"] + (70,)); im.alpha_composite(fl)
            gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(seg, fill=TH["accent2"] + (255,), width=22, joint="curve"); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14)))
            d = ImageDraw.Draw(im); d.line(seg, fill=(255, 245, 235, 255), width=8, joint="curve"); ex, ey = seg[-1]; d.ellipse((ex - 16, ey - 16, ex + 16, ey + 16), fill=WHITE)
        n = int(round(points[-1][1] * eio(t / 2.2))); d = ImageDraw.Draw(im); d.text((X0 + 60, Y0 + 95), f"{n}", font=font("xb", 96), fill=WHITE)
        d.text((X0 + 80 + tsize(str(n), font("xb", 96))[0], Y0 + 140), big_suffix, font=font("sb", 38), fill=(255, 255, 255, 200))
        if bp: put(im, bp, X1 - bp.width / 2 + 40, Y0, eo((t - 2.3) / 0.35), back((t - 2.3) / 0.4))
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.6), (2.3, "pop", 0.8)]

# ======================= TRANSITIONS =======================
def vblur(img, amt):
    if amt < 1: return img
    a = np.asarray(img, np.float32); acc = np.zeros_like(a)
    for j in range(6): acc += np.roll(a, int((j - 3) * amt / 6), axis=0)
    return Image.fromarray((acc / 6).astype(np.uint8))
def zoom(img, s):
    if abs(s - 1) < 0.002: return img
    nw, nh = int(W * s), int(H * s); r = img.resize((nw, nh), Image.BILINEAR); l, tp = (nw - W) // 2, (nh - H) // 2; return r.crop((l, tp, l + W, tp + H))

# ======================= AUDIO =======================
def _synth():
    rng = np.random.default_rng(7); tt = lambda d: np.arange(int(d * SR)) / SR; S = {}
    def kick(d=0.35):
        t = tt(d); f = 45 + 110 * np.exp(-t * 28); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    def lpf(x, a):
        y = np.empty_like(x); acc = 0.0
        for i in range(len(x)): acc += (a[i] if hasattr(a, "__len__") else a) * (x[i] - acc); y[i] = acc
        return y
    t = tt(0.5); S["ping"] = (np.sin(2 * np.pi * 1568 * t) * np.exp(-t * 9) + 0.6 * np.sin(2 * np.pi * 2349 * t) * np.exp(-t * 12) * (t > 0.07)) * 0.35
    t = tt(0.18); S["pop"] = np.sin(2 * np.pi * np.cumsum(300 + 900 * np.exp(-t * 40)) / SR) * np.exp(-t * 30) * 0.5
    t = tt(0.05); S["click"] = np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120) * 0.6 + rng.standard_normal(len(t)) * np.exp(-t * 200) * 0.2
    t = tt(0.03); S["tick"] = np.sin(2 * np.pi * 3000 * t) * np.exp(-t * 250) * 0.4
    t = tt(0.35); S["coin"] = (np.sin(2 * np.pi * 1975 * t) * np.exp(-t * 14) * (t < 0.08) + np.sin(2 * np.pi * 2637 * t) * np.exp(-(t - 0.08).clip(0) * 7) * (t >= 0.08)) * 0.32
    nz = rng.standard_normal(int(0.45 * SR)).astype(np.float32); S["whoosh"] = lpf(nz, np.linspace(0.02, 0.35, len(nz)) ** 1.2) * np.sin(np.linspace(0, np.pi, len(nz))) ** 2 * 0.9
    S["swish"] = S["whoosh"][::2] * 0.7
    t = tt(0.6); S["hit"] = kick(0.6) * 0.9 + lpf(rng.standard_normal(len(t)).astype(np.float32), 0.25) * np.exp(-t * 14) * 0.35
    t = tt(0.9); S["shimmer"] = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 4) for f in (2093, 2637, 3136)) * np.minimum(t / 0.05, 1) * 0.08
    t = tt(0.25); S["glitch"] = np.sign(np.sin(2 * np.pi * 180 * t)) * (rng.random(len(t)) > 0.4) * np.exp(-t * 10) * 0.18
    S["kick"] = kick(); hn = rng.standard_normal(int(0.06 * SR)); hn = hn - np.concatenate([[0], hn[:-1]]); S["hat"] = hn * np.exp(-np.arange(len(hn)) / SR / 0.015) * 0.25
    return S

# ======================= RENDER =======================
class Video:
    def __init__(self): self.scenes = []
    def add(self, dur, fn, events=()): self.scenes.append((dur, fn, list(events))); return self
    def render(self, out, transition="whip", tr_frames=5, bpm=120, music=True, sfx=True, preview_times=None, lufs=-14.0, tp=-1.0,
               voice=None, voice_at=0.0, duck_db=18.0, pause_db=8.0, sfx_duck_db=6.0, audio_only=False):
        """transition: whip | fade | flash | cut. preview_times=[sec,...] writes a contact sheet <out>_preview.png
        lufs/tp: master loudness with a two-pass ffmpeg loudnorm (None = skip)
        voice: voiceover file, placed at voice_at seconds. Music sits duck_db under the voice while words are spoken
        and pause_db under it in the gaps; SFX dip sfx_duck_db under speech. The voice itself is never limited.
        audio_only: skip the frames and write just the mastered soundtrack to out (fast audio checks)"""
        tmp = tempfile.mkdtemp(); vpath, apath = os.path.join(tmp, "v.mp4"), os.path.join(tmp, "a.wav")
        p = None if audio_only else subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-vf", "setsar=1", vpath], stdin=subprocess.PIPE)
        t0 = 0.0; events = []; cuts = []; prev = None
        for si, (dur, fn, ev) in enumerate(self.scenes):
            events += [(t0 + a, k, g) for a, k, g in ev]; n = int(round(dur * FPS))
            for i in range(0 if audio_only else n):
                im, sh = fn(i / FPS); im = im.convert("RGB")
                if sh: im = im.transform(im.size, Image.AFFINE, (1, 0, -sh * math.sin(i * 2.7), 0, 1, -sh * math.cos(i * 3.1)), fillcolor=TH["bg"][0])
                last, first = si < len(self.scenes) - 1 and i >= n - tr_frames, si > 0 and i < tr_frames
                if transition == "whip":
                    if last: q = (i - (n - tr_frames) + 1) / tr_frames; im = vblur(zoom(im, 1 + 0.18 * q * q), 90 * q)
                    if first: q = 1 - (i + 1) / (tr_frames + 1); im = vblur(zoom(im, 1 + 0.14 * q), 90 * q)
                elif transition == "fade" and first and prev is not None: im = Image.blend(prev, im, eio((i + 1) / (tr_frames + 1)))
                elif transition == "flash" and first: im = Image.blend(im, Image.new("RGB", im.size, WHITE), 0.4 * (tr_frames - i) / tr_frames)
                p.stdin.write(im.tobytes())
                if i == n - 1: prev = im
            t0 += n / FPS; cuts.append(t0)
        if p: p.stdin.close(); p.wait()
        total = t0
        N = int(total * SR); S = _synth(); mus = np.zeros(N + SR, np.float32); fx = np.zeros(N + SR, np.float32)
        def add(buf, sig, at, g):
            s = int(at * SR); e = min(len(buf), s + len(sig)); buf[s:e] += sig[:e - s] * g
        if music:
            beat = 60 / bpm; b = 0.0
            while b < total - 0.2:
                if b >= 0.45: add(mus, S["kick"], b, 0.32)
                add(mus, S["hat"], b + beat / 2, 0.5); b += beat
            pt = np.arange(len(mus)) / SR; mus += (np.sin(2 * np.pi * 55 * pt) + 0.5 * np.sin(2 * np.pi * 82.4 * pt)) * 0.05 * np.minimum(pt, 1) * np.clip((total - pt) / 0.8, 0, 1)
        if sfx:
            for at, k, g in events: add(fx, S[k], at, g)
            if transition != "cut":
                for c in cuts[:-1]: add(fx, S["whoosh"], c - 0.25, 0.5)
        mus, fx = mus[:N], fx[:N]
        if voice is None:
            mix = mus + fx; mix = np.tanh(mix * 1.2) / np.tanh(1.2); mix /= max(1e-6, np.abs(mix).max()) / 0.89; bed_limit = 0.35
        else:
            vo = load_audio(voice, N, voice_at)
            talk = speech_gain(vo)                                   # 1 while words are spoken, 0 in gaps (smoothed)
            v_rms = rms(vo[talk > 0.5])
            k = v_rms * 10 ** (-pause_db / 20) / max(1e-6, rms(mus))  # music level in the gaps
            duck = 10 ** (-(duck_db - pause_db) / 20)
            mg = np.minimum(1 - talk * (1 - duck), follow_gain(vo, mus * k, talk, duck_db + 2))  # also track soft words
            bed = (mus * k) * mg + (fx * k) * (1 - talk * (1 - 10 ** (-sfx_duck_db / 20)))
            ceil = np.abs(vo).max() * 0.6; bed = np.tanh(bed / ceil) * ceil  # soft-clip SFX/beat peaks only
            words = speech_gain(vo, hold=0.0, pre=0.0, attack=0.005, release=0.005)  # raw word activity, no hold
            self.duck_report = duck_check(vo, mus * k * mg, words)
            mix = vo + bed; mix /= max(1.0, np.abs(mix).max() / 0.99); bed_limit = None   # plain gain, no limiter on the voice
        with wave.open(apath, "wb") as wf: wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((mix * 32767).astype(np.int16).tobytes())
        if lufs is not None: apath = master(apath, lufs, tp, bed_limit, peak_catch=voice is not None)
        if audio_only:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", apath, "-c:a", "aac", "-b:a", "256k", "-ar", "48000", out], check=True); return total
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vpath, "-i", apath, "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], check=True)
        if preview_times: contact_sheet(out, preview_times)
        return total

def rms(x): return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if len(x) else 0.0

def load_audio(path, n, at=0.0, offset=0.0):
    """decode a file to mono float32 at SR, starting offset seconds in, placed at `at` seconds, padded/cut to n samples"""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(offset), "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32); out = np.zeros(n, np.float32); s = int(at * SR)
    if s < 0: a, s = a[-s:], 0
    m = min(len(a), n - s)
    if m > 0: out[s:s + m] = a[:m]
    return out

def speech_gain(vo, thresh_db=-35.0, hold=0.12, pre=0.06, attack=0.03, release=0.25, hop=0.01):
    """0..1 curve: 1 while the voice is talking. thresh relative to the loudest 10ms; held across short gaps,
    opens `pre` seconds early so the duck lands before the word, smoothed with attack/release"""
    h = int(hop * SR); n = len(vo) // h + 1
    env = np.sqrt(np.convolve(np.square(vo), np.ones(h) / h, "same")[::h])[:n]
    on = env > env.max() * 10 ** (thresh_db / 20)
    k = int((hold + pre) / hop); idx = np.flatnonzero(on); g = np.zeros(len(env))
    for i in idx: g[max(0, i - int(pre / hop)):i + int(hold / hop) + 1] = 1
    a, r = 1 - math.exp(-hop / attack), 1 - math.exp(-hop / release); sm = np.zeros_like(g); y = 0.0
    for i, x in enumerate(g): y += (a if x > y else r) * (x - y); sm[i] = y
    return np.interp(np.arange(len(vo)) / h, np.arange(len(sm)), sm).astype(np.float32)

def follow_gain(vo, music, talk, under_db, win=0.3, hop=0.01, release=0.3):
    """music gain that keeps the music under_db below the voice's own local level while it talks (soft words duck harder)"""
    h = int(hop * SR); w = max(1, int(win / hop))
    env = lambda x: np.sqrt(np.convolve(np.convolve(np.square(x), np.ones(h) / h, "same")[::h], np.ones(w) / w, "same")) + 1e-9
    v, m, tk = env(vo), env(music), talk[::h][:len(env(vo))]
    req = np.where(tk > 0.05, np.minimum(1.0, v * 10 ** (-under_db / 20) / m), 1.0)
    r = 1 - math.exp(-hop / release); sm = np.empty_like(req); y = 1.0
    for i, x in enumerate(req): y = x if x < y else y + r * (x - y); sm[i] = y   # instant attack, smooth release
    sm = np.minimum(sm, np.concatenate([sm[int(0.06 / hop):], np.ones(int(0.06 / hop))]))  # open the duck 60ms early
    return np.interp(np.arange(len(vo)) / h, np.arange(len(sm)), sm).astype(np.float32)

def duck_check(vo, music, talk, win=0.4):
    """voice-minus-music level (dB) over each window that is words (not pauses). returns (min, median) for the report"""
    w = int(win * SR); d = []
    for s in range(0, len(vo) - w, w):
        if talk[s:s + w].mean() > 0.8: d.append(20 * math.log10(max(1e-9, rms(vo[s:s + w])) / max(1e-9, rms(music[s:s + w]))))
    return (min(d), float(np.median(d))) if d else (None, None)

def loudness(path, lufs=-14.0, tp=-1.0, extra=""):
    """measure with loudnorm (print_format=json) -> dict of input_i / input_tp / ..."""
    import json
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", f"loudnorm=I={lufs}:TP={tp}:LRA=11{extra}:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    return json.loads(r.stderr[r.stderr.rindex("{"):])

def master(wav, lufs=-14.0, tp=-1.0, bed_limit=0.35, peak_catch=False):
    """two-pass loudnorm to lufs / tp (aims 0.2 dB under tp; check the encoded file). returns the new wav path.
    bed_limit: first tame the synthesized SFX/beat transients (fast alimiter, linear ceiling) so loudnorm can stay
    linear. Only for beds with no voice in them; pass None to skip.
    peak_catch: for voice mixes. Gain to lufs, then a 1ms-attack catch on just the peaks over the ceiling (a dB or two on
    well under 1% of samples) instead of loudnorm's dynamic mode, which would ride the whole voice."""
    if bed_limit:
        pre = os.path.splitext(wav)[0] + "_pre.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", f"alimiter=limit={bed_limit}:attack=2:release=60:level=false", "-ar", "48000", pre], check=True); wav = pre
    if peak_catch:  # plain gain to the target, then a fast catch on only the peaks above the ceiling (no compression)
        m = loudness(wav, lufs, tp); out = os.path.splitext(wav)[0] + "_master.wav"; ceil = 10 ** ((tp - 0.6) / 20)
        gain = lufs - float(m["input_i"])
        for _ in range(4):  # the catch takes a little loudness off, so nudge the gain until the output lands on lufs
            af = f"volume={gain:.2f}dB,alimiter=limit={ceil:.4f}:attack=1:release=15:level=false"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", af, "-ar", "48000", out], check=True)
            got = float(loudness(out, lufs, tp)["input_i"])
            if abs(got - lufs) < 0.15: break
            gain += lufs - got
        master.info = dict(gain_db=round(gain, 2), catch_db=round(gain - (lufs - float(m["input_i"])), 2)); return out
    m = loudness(wav, lufs, tp - 0.2); out = os.path.splitext(wav)[0] + "_master.wav"
    af = (f"loudnorm=I={lufs}:TP={tp - 0.2}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", af, "-ar", "48000", out], check=True); return out

def reframe_4x5(src, out, top=200, bottom=1700):
    """Instagram/Facebook feed version (1080x1350, 4:5) of a 9:16 render. Keeps the y=top..bottom band where all the
    content lives, scales it to 1350 tall and fills the thin side strips with a blurred copy of the frame."""
    h = bottom - top; fw = int(round(W * 1350 / h / 2) * 2)
    fc = (f"[0:v]split[a][b];[a]scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350,gblur=sigma=40[bg];"
          f"[b]crop={W}:{h}:0:{top},scale={fw}:1350[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "0:a?",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", out], check=True)
    return out

def contact_sheet(video, times, width=260):
    """grab frames at times -> <video>_preview.png for visual QA"""
    tmp = tempfile.mkdtemp(); ins = []
    for i, s in enumerate(times):
        f = os.path.join(tmp, f"{i}.png"); subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(s), "-i", video, "-frames:v", "1", "-vf", f"scale={width}:-1", f], check=True); ins += ["-i", f]
    out = os.path.splitext(video)[0] + "_preview.png"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", f"hstack={len(times)}" if len(times) > 1 else "null", out], check=True); return out
