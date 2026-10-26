"""TRUST video scenes ('Ryan explains Southline'): the owner's 10.7s desk clip, cut into many different shots
(push-ins, slow-mo, freeze frames, a floating framed clip, blurred backgrounds, a fly-in to the real ad on the monitor),
with a different animation on every line of the voiceover script. White type with soft shadows, one blue accent.
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed

ACC = (56, 140, 255); WHITE = (255, 255, 255); INK = (16, 18, 24); MUTED = (120, 126, 138)
CW, CH, CFPS = 480, 854, 30
_F = None


# ======================================================================= the clip
def load_clip(path):
    """decode the clip once (480x854), lift the shadows a little - it was filmed in a dark room"""
    global _F
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, CH, CW, 3).astype(np.float32) / 255
    _F = np.clip((f ** 0.78) * 1.06 * 255, 0, 255).astype(np.uint8)
    return len(_F) / CFPS

def src_time(ts):
    """ping-pong inside the clip so any source time is valid"""
    L = (len(_F) - 1) / CFPS; ts = ts % (2 * L)
    return ts if ts <= L else 2 * L - ts

def frame(ts):
    return Image.fromarray(_F[int(round(src_time(ts) * CFPS))])

def view(ts, zoom=1.0, fx=0.5, fy=0.5, blur=0, dark=0.0):
    """full-screen shot of the clip at source time ts: zoom into (fx, fy), optional blur / darken"""
    im = frame(ts)
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))  # blur at low res = cheap and soft
    cw, ch = CW / zoom, CH / zoom; x0 = clamp(fx * CW - cw / 2, 0, CW - cw); y0 = clamp(fy * CH - ch / 2, 0, CH - ch)
    out = im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
    if dark > 0: out.alpha_composite(Image.new("RGBA", (W, H), (6, 8, 12, int(255 * clamp(dark)))))
    return out

MON = (0.28, 0.57)   # the ad on the left monitor
FACE = (0.84, 0.47)  # Ryan

_VIG = None
def vignette(im):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        a = (np.clip((r - 0.55) / 0.6, 0, 1) ** 1.6 * 200).astype(np.uint8); _VIG = Image.new("RGBA", (W, H), (0, 0, 0, 0)); _VIG.putalpha(Image.fromarray(a))
    im.alpha_composite(_VIG); return im


# ======================================================================= type helpers
_tc = {}
def T(s, size, col=WHITE, w="bl", maxw=960):
    """white text with a soft drop shadow so it reads on video"""
    k = (s, size, col, w, maxw)
    if k not in _tc: _tc[k] = shadowed(text(s, w, fit_size(s, w, size, maxw), col), blur=14, dy=5, alpha=180, pad=36)
    return _tc[k]

def under(im, s, size, cx, cy, key, p, w="bl", maxw=960):
    """accent underline under `key` inside line s (drawn centred at cx, cy), wiping in with p"""
    if p <= 0: return
    size = fit_size(s, w, size, maxw); f = A.font(w, size); full = f.getlength(s); i = s.index(key)
    x0 = cx - full / 2 + f.getlength(s[:i]); x1 = x0 + f.getlength(key.rstrip(".,?…")) * eo(p); y = cy + size * 0.42; h = max(8, size * 0.1)
    ImageDraw.Draw(im).rounded_rectangle((x0, y, max(x0 + 1, x1), y + h), h / 2, fill=ACC)

def pop(im, sp, x, y, t, t0, big=1.4):
    k = (t - t0) / 0.35
    if k > 0: put(im, sp, x, y, clamp(k / 0.15), big - (big - 1) * back(k))

def rise(im, sp, x, y, t, t0, fade_out=None):
    if t < t0: return
    a = 1.0 if fade_out is None else 1 - clamp((t - fade_out) / 0.25)
    if a >= 1: put_rise(im, sp, x, y, eo((t - t0) / 0.3))
    else: put(im, sp, x, y - 40 * (1 - a), a)

def ctext(d, x, y, s, f, col):
    tw, th, ox, oy = A.tsize(s, f); d.text((x - tw / 2 - ox, y - th / 2 - oy), s, font=f, fill=col)

def card(w, h, draw=None, fill=WHITE, r=34, alpha=255):
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill + (alpha,))
        if draw: draw(d, s)
    return shadowed(sprite(w, h, fn), blur=26, dy=14, alpha=150, pad=50)

def finger(im, x, y, t, t_tap):
    A.tap(im, x, y, t, t_tap, t_in=0.45, t_out=0.45, from_dx=140, from_dy=260)


# ======================================================================= scenes
def scene_intro(dur=4.2):
    """push-in on the desk; 'Hey, I'm Ryan.' pops; lower-third name card slides in with the logo"""
    logo = A.logo().resize((120, 120), Image.LANCZOS)
    def lt(d, s): d.text((170 * s, 34 * s), "Ryan", font=A.font("bl", 58 * s), fill=INK); d.text((172 * s, 104 * s), "Founder · Southline Agency", font=A.font("m", 30 * s), fill=MUTED)
    LT = card(700, 170, lt, alpha=240); LT.alpha_composite(logo, (50 + 26, 50 + 25))
    h1, h2 = T("Hey, I'm Ryan.", 120), T("I run a marketing agency.", 70)
    def fn(t):
        im = vignette(view(0.2 + t * 0.9, 1.0 + 0.1 * eio(t / dur), 0.62, 0.5))
        pop(im, h1, W / 2, 520, t, 0.1); rise(im, h2, W / 2, 660, t, 1.5)
        k = eo((t - 0.7) / 0.5); put(im, LT, -400 + (W / 2 + 400) * k, 1440, k)
        return im, 0
    return dur, fn, [(0.1, "pop", 0.6), (0.7, "swish", 0.5), (1.5, "swish", 0.4)]


def scene_common(dur=3.4):
    """blurred backdrop + the clip floating in a rounded frame; 'The most common question I get asked…'"""
    FW_, FH_ = 600, 1068
    mask = sprite(FW_, FH_, lambda d, s, im: d.rounded_rectangle((0, 0, FW_ * s - 1, FH_ * s - 1), 44 * s, fill=(255, 255, 255, 255))).split()[3]
    shadow = shadowed(Image.new("RGBA", (FW_ + 16, FH_ + 16), (255, 255, 255, 255)), blur=30, dy=20, alpha=150, pad=60)
    h1, h2 = T("The most common", 84), T("question I get asked…", 84)
    def fn(t):
        ts = 3.5 + t; im = view(ts, 1.2, 0.5, 0.5, blur=8, dark=0.55)
        fr = frame(ts).resize((FW_, FH_), Image.BICUBIC).convert("RGBA"); fr.putalpha(mask)
        k = spring(t / 0.8, f=1.4, d=6); rot = -4 + 2 * math.sin(t * 1.6) + 10 * (1 - eo(t / 0.6))
        sh = shadow.copy(); sh.alpha_composite(fr, (68, 68)); put(im, sh, W / 2, 1180 + 600 * (1 - k), 1, 0.92 + 0.02 * math.sin(t * 2), rot)
        rise(im, h1, W / 2, 380, t, 0.15); rise(im, h2, W / 2, 490, t, 0.4); under(im, "question I get asked…", 84, W / 2, 490, "question", (t - 0.8) / 0.4)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.5), (0.15, "swish", 0.4), (0.4, "swish", 0.4), (0.8, "swish", 0.5)]


def scene_question(dur=3.3, type_from=0.45, cps=30):
    """the question as an 'ask me anything' sticker, typed out, over a blurred push into the monitor"""
    q = ["Do Facebook ads actually", "work for tradesmen?"]; n_all = sum(len(x) for x in q)
    CWd, CHd = 900, 420
    def base(d, s):
        d.rounded_rectangle((0, 0, CWd * s - 1, 110 * s), 34 * s, fill=ACC); d.rectangle((0, 70 * s, CWd * s, 110 * s), fill=ACC)
        ctext(d, CWd * s / 2, 56 * s, "THE QUESTION", A.font("monob", 34 * s), WHITE)
    C = card(CWd, CHd, base); f = A.font("bl", 64)
    def fn(t):
        im = view(5.5 + 0.5 * t, 1.6 + 0.3 * eio(t / dur), *MON, blur=5, dark=0.45)
        k = spring(t / 0.6, f=1.5, d=6); c = C.copy(); d = ImageDraw.Draw(c); n = int(clamp((t - type_from) * cps, 0, n_all))
        for j, line in enumerate(q):
            shown = line[:max(0, n - sum(len(x) for x in q[:j]))]
            if shown: d.text((50 + 60, 50 + 160 + j * 100), shown, font=f, fill=INK)
            if 0 < len(shown) < len(line) or (j == 1 and len(shown) == len(line) and int(t * 3) % 2 == 0):
                x = 50 + 60 + f.getlength(shown) + 6; d.rectangle((x, 50 + 165 + j * 100, x + 7, 50 + 235 + j * 100), fill=ACC)
        put(im, c, W / 2, 960, clamp(t / 0.15), 0.8 + 0.2 * k, -2 * (1 - eo(t / 0.5)))
        return im, 0
    return dur, fn, [(0.0, "pop", 0.8)] + [(type_from + i / cps, "tick", 0.22) for i in range(0, n_all, 2)]


def scene_short(dur=5.2, boost_at=2.8, tap_at=3.25):
    """slow-mo push on Ryan: 'Short answer? YEAH. when they're done properly.' then a 'Boost post' button gets tapped
    and struck out: 'isn't the same thing.'"""
    s1, s2, s3, s4 = T("Short answer?", 84), T("Yeah.", 230, ACC), T("when they're done properly.", 70), T("isn't the same thing.", 76)
    def bb(d, s): ctext(d, 280 * s, 70 * s, "Boost post", A.font("bl", 58 * s), INK)
    BOOST = card(560, 140, bb, fill=(232, 234, 238), r=70)
    def fn(t):
        dk = 0.25 + 0.35 * clamp((t - boost_at) / 0.3)
        im = vignette(view(7.0 + 0.55 * t, 1.3 + 0.12 * eio(t / dur), *FACE, dark=dk)); sh = 0
        fo = boost_at
        rise(im, s1, W / 2, 520, t, 0.1, fo); pop(im, s2, W / 2, 760, t, 0.75, 1.6) if t < fo else None
        if t >= fo and t < fo + 0.25: put(im, s2, W / 2, 760, 1 - (t - fo) / 0.25)
        rise(im, s3, W / 2, 960, t, 1.4, fo)
        if t < fo: under(im, "when they're done properly.", 70, W / 2, 960, "done properly", (t - 1.8) / 0.4)
        if 0.75 <= t < 0.9: sh = 10
        if t >= boost_at:
            pop(im, BOOST, W / 2, 900, t, boost_at + 0.1, 1.3); finger(im, W / 2 + 160, 900, t, tap_at)
            p = eo((t - tap_at - 0.25) / 0.3)
            if p > 0: ImageDraw.Draw(im).line((W / 2 - 300, 960, W / 2 - 300 + 600 * p, 840), fill=ACC, width=16)
            rise(im, s4, W / 2, 1120, t, tap_at + 0.5)
        return im, sh
    return dur, fn, [(0.1, "swish", 0.4), (0.75, "hit", 0.8), (1.4, "swish", 0.4), (1.8, "swish", 0.5), (boost_at + 0.1, "pop", 0.6),
                     (tap_at, "click", 0.8), (tap_at + 0.25, "swish", 0.7), (tap_at + 0.5, "swish", 0.4)]


def scene_title(num, lines, src, zoom, fx, fy, dur=2.3):
    """section card: freeze frame, darkened; big accent number slams, the question pops in word by word"""
    nsp = T(num, 150, ACC, "monob"); words = [[T(w_, 92) for w_ in l.split(" ")] for l in lines]
    sp = A.font("bl", 92).getlength(" ")
    def fn(t):
        im = view(src, zoom + 0.08 * eio(t / dur), fx, fy, blur=3, dark=0.62)
        pop(im, nsp, W / 2, 720, t, 0.0, 1.8); k = 0.3
        for j, ws in enumerate(words):
            tot = sum(w_.width - 72 for w_ in ws) + sp * (len(ws) - 1); x = W / 2 - tot / 2
            for w_ in ws:
                pop(im, w_, x + (w_.width - 72) / 2, 930 + j * 120, t, k, 1.5); x += w_.width - 72 + sp; k += 0.1
        return im, (12 if t < 0.12 else 0)
    n = sum(len(l.split(" ")) for l in lines)
    return dur, fn, [(0.0, "hit", 1.0)] + [(0.3 + i * 0.1, "pop", 0.3) for i in range(n)]


def scene_what(dur=4.6):
    """fly into the monitors; 'We run' + Facebook / Instagram pills + 'ads for trades & local businesses' + pin 'around Ireland'"""
    s0 = T("We run", 84); s1, s2 = T("ads for trades &", 84), T("local businesses", 84); s3 = T("around Ireland.", 84)
    pf, pi = A.pill("Facebook", 50, WHITE, INK, w="bl"), A.pill("Instagram", 50, WHITE, INK, w="bl"); plus = T("+", 80, ACC)
    def fn(t):
        im = vignette(view(0.5 + 0.8 * t, 1.5 + 0.35 * eio(t / dur), *MON, dark=0.4))
        rise(im, s0, W / 2, 470, t, 0.1)
        pop(im, pf, W / 2 - 220, 630, t, 0.45); pop(im, plus, W / 2 + 10, 630, t, 0.62); pop(im, pi, W / 2 + 240, 630, t, 0.75)
        rise(im, s1, W / 2, 840, t, 1.4); rise(im, s2, W / 2, 950, t, 1.6)
        k = (t - 2.6) / 0.45
        if k > 0:  # location pin drops in
            py = 1150 - 220 * (1 - spring(k, f=1.5, d=6)); d = ImageDraw.Draw(im)
            d.ellipse((W / 2 - 44, py - 104, W / 2 + 44, py - 16), fill=ACC); d.polygon([(W / 2 - 34, py - 48), (W / 2 + 34, py - 48), (W / 2, py + 4)], fill=ACC)
            d.ellipse((W / 2 - 16, py - 76, W / 2 + 16, py - 44), fill=WHITE); ring(im, W / 2, 1150, (t - 2.9) / 1.0, col=ACC, maxr=260, width=5, r0=30)
        rise(im, s3, W / 2, 1290, t, 2.9)
        return im, 0
    return dur, fn, [(0.1, "swish", 0.4), (0.45, "pop", 0.6), (0.75, "pop", 0.6), (1.4, "swish", 0.4), (1.6, "swish", 0.4), (2.6, "pop", 0.7), (2.9, "swish", 0.4)]


def scene_trades(dur=3.6, gap=0.5):
    """trade chips slide in from alternating sides and stack; the newest one is blue"""
    names = ["Plumbers", "Builders", "Electricians", "Kitchen fitters", "Bathroom fitters"]
    W0 = [A.pill(n, 56, WHITE, INK, w="bl") for n in names]; W1 = [A.pill(n, 56, ACC, WHITE, w="bl") for n in names]
    def fn(t):
        im = view(4.2 + 0.5 * t, 1.15, 0.5, 0.5, blur=9, dark=0.55)
        last = int(clamp((t - 0.15) / gap, -1, len(names) - 1)) if t >= 0.15 else -1
        for i in range(len(names)):
            k = (t - 0.15 - i * gap) / 0.4
            if k <= 0: continue
            side = -1 if i % 2 == 0 else 1
            put(im, W1[i] if i == last else W0[i], W / 2 + side * 700 * (1 - eo(k)), 620 + i * 170, 1, 1, side * 6 * (1 - eo(k)))
        return im, 0
    return dur, fn, [(0.15 + i * gap, "click", 0.7) for i in range(5)]


def scene_aim(dur=4.4, ring_at=0.9, pings_at=1.7):
    """'The aim's simple: people in your area asking you for a quote.' radius map with quote pings"""
    h0 = T("The aim's simple:", 64, (200, 210, 230)); h1, h2 = T("people in your area", 84), T("asking you for a quote.", 84)
    MX, MY, R = W / 2, 1180, 300
    rng = np.random.default_rng(5); houses = [(MX + rng.uniform(-420, 420), MY + rng.uniform(-330, 330)) for _ in range(70)]
    inside = [h for h in houses if math.hypot(h[0] - MX, h[1] - MY) < R - 20]; pings = inside[:5]
    bub = A.pill("Quote request", 26, WHITE, INK, w="bl")
    def fn(t):
        im = view(1.0 + 0.6 * t, 1.1, 0.5, 0.5, blur=9, dark=0.62)
        rise(im, h0, W / 2, 400, t, 0.05); rise(im, h1, W / 2, 500, t, 0.25); rise(im, h2, W / 2, 605, t, 0.45)
        under(im, "asking you for a quote.", 84, W / 2, 605, "asking you for a quote", (t - 0.8) / 0.5)
        k = eo((t - 0.3) / 0.4); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        d.rounded_rectangle((MX - 460, MY - 370, MX + 460, MY + 370), 40, fill=(20, 24, 32, int(230 * k)))
        r = R * eo((t - ring_at) / 0.7)
        if r > 1: d.ellipse((MX - r, MY - r, MX + r, MY + r), fill=ACC + (40,), outline=ACC + (230,), width=5)
        for x, y in houses:
            lit = math.hypot(x - MX, y - MY) < r; c = (ACC if lit else (90, 96, 110)) + (int(255 * k),)
            d.polygon([(x, y - 18), (x - 15, y - 4), (x + 15, y - 4)], fill=c); d.rectangle((x - 11, y - 4, x + 11, y + 12), fill=c)
        d.ellipse((MX - 26, MY - 26, MX + 26, MY + 26), fill=WHITE + (int(255 * k),)); im.alpha_composite(o)
        for i, (x, y) in enumerate(pings):
            pk = (t - pings_at - i * 0.35) / 0.35
            if pk > 0: put(im, bub, x, y - 50, clamp(pk / 0.2), 0.6 + 0.4 * back(pk)); ring(im, x, y, pk / 1.6, col=ACC, maxr=80, width=4, r0=10)
        return im, 0
    return dur, fn, [(0.05, "swish", 0.4), (0.25, "swish", 0.4), (0.8, "swish", 0.5), (ring_at, "whoosh", 0.5)] + [(pings_at + i * 0.35, "ping", 0.45) for i in range(5)]


def scene_how(dur=7.0, fly_at=3.5):
    """phase A: 'Your real work' - three photo prints fly in and fan out, then slide together: 'turned into ads'.
    phase B: the camera flies into the real ad on the monitor: 'shown to homeowners in the area you cover.'"""
    import kitchen_scenes as K
    b, a = K.kitchen_art(380, 320, False), K.kitchen_art(380, 320, True, 1); a2 = K.kitchen_art(380, 320, True, 3)
    def print_(img, cap):
        def dr(d, s): ctext(d, 210 * s, 400 * s, cap, A.font("b", 32 * s), INK)
        c = card(420, 450, dr, r=18); c.alpha_composite(img.convert("RGBA"), (50 + 20, 50 + 20)); return c
    P = [print_(a, "Your photos"), print_(K.before_after(b, a, 0.5), "Before & afters"), print_(a2, "Finished jobs")]
    hA = T("Your real work.", 96); tag = A.pill("→ turned into ads", 46, ACC, WHITE, w="bl")
    hB1, hB2 = T("Shown to homeowners", 84), T("in the area you cover.", 84)
    fan = [(-300, -8), (0, 2), (300, 9)]
    def fn(t):
        if t < fly_at:
            im = view(2.0 + 0.5 * t, 1.1, 0.5, 0.5, blur=9, dark=0.55); rise(im, hA, W / 2, 430, t, 0.1)
            together = eio((t - 2.3) / 0.5)
            for i, (dx, rot) in enumerate(fan):
                k = (t - 0.4 - i * 0.45) / 0.55
                if k <= 0: continue
                x = W / 2 + dx * (1 - 0.85 * together); y = 1000 + 900 * (1 - spring(k, f=1.4, d=6)) - i * 10 * together
                put(im, P[i], x, y, 1, 0.95, rot * (1 - 0.6 * together) + 25 * (1 - eo(k)))
            pop(im, tag, W / 2, 1420, t, 2.6)
            return im, 0
        u = t - fly_at; z = 1.0 + 1.4 * eio(u / 0.7)  # fly into the monitor
        im = vignette(view(3.6 + 0.35 * u, z, *MON, dark=0.15))
        if u < 0.12: im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - u / 0.12)))))
        for j in range(3): ring(im, W / 2, 900, ((u - 0.9) - j * 0.45) % 1.35 / 1.35 if u > 0.9 else 0, col=ACC, maxr=500, width=5, r0=60)
        rise(im, hB1, W / 2, 1380, t, fly_at + 0.6); rise(im, hB2, W / 2, 1490, t, fly_at + 0.85)
        under(im, "in the area you cover.", 84, W / 2, 1490, "the area you cover", (u - 1.3) / 0.5)
        return im, 0
    return dur, fn, [(0.1, "swish", 0.4)] + [(0.4 + i * 0.45 + 0.3, "hit", 0.45) for i in range(3)] + [(2.3, "swish", 0.5), (2.6, "pop", 0.6),
                     (fly_at - 0.1, "whoosh", 0.7), (fly_at + 0.6, "swish", 0.4), (fly_at + 0.85, "swish", 0.4), (fly_at + 1.3, "swish", 0.5)]


def scene_questions(dur=4.6, rows_at=(0.8, 1.4, 2.0)):
    """'Before anyone gets in touch, a few quick questions.' form card; each answer chip pops in with a tick"""
    h1, h2 = T("Before anyone gets in touch,", 74), T("a few quick questions.", 84)
    qa = [("WHAT'S THE JOB?", "Kitchen refit"), ("WHERE?", "Lucan"), ("WHEN?", "Next month")]
    FORM = card(880, 600); chips = [A.pill(a + "  ✓", 40, ACC, WHITE, w="bl") for _, a in qa]
    def fn(t):
        im = view(6.0 + 0.5 * t, 1.1, 0.5, 0.5, blur=9, dark=0.6)
        rise(im, h1, W / 2, 420, t, 0.05); rise(im, h2, W / 2, 530, t, 0.3); under(im, "a few quick questions.", 84, W / 2, 530, "quick questions", (t - 0.6) / 0.4)
        k = spring((t - 0.3) / 0.6, f=1.4, d=6); fy = 1050 + 500 * (1 - k); put(im, FORM, W / 2, fy, clamp((t - 0.3) / 0.15))
        if t > 0.5:
            d = ImageDraw.Draw(im)
            for i, (q, _) in enumerate(qa):
                y = fy - 300 + 110 + i * 180; d.text((W / 2 - 380, y - 30), q, font=A.font("monob", 28), fill=MUTED)
                if i: d.line((W / 2 - 380, y - 70, W / 2 + 380, y - 70), fill=(228, 230, 234), width=2)
                ck = (t - rows_at[i]) / 0.35
                if ck > 0: put(im, chips[i], W / 2 + 380 - chips[i].width / 2, y + 45, clamp(ck / 0.2), 0.6 + 0.4 * back(ck))
                else: d.rounded_rectangle((W / 2 - 380, y + 15, W / 2 + 380, y + 75), 20, outline=(220, 222, 228), width=3)
        return im, 0
    return dur, fn, [(0.05, "swish", 0.4), (0.3, "whoosh", 0.4), (0.6, "swish", 0.5)] + [(r, "pop", 0.6) for r in rows_at]


def scene_phone(dur=3.8, note_at=0.9, call_at=2.0, tap_at=2.5):
    """'Straight to your phone.' a phone rises, the enquiry drops in with a buzz, 'Call back' is tapped, rings pulse"""
    h = T("Straight to your phone.", 84); ph = A.phone("Monday 3 November", "09:41", wall=((28, 34, 46), (8, 10, 14), ACC))
    def nd(d, s):
        d.rounded_rectangle((30 * s, 36 * s, 118 * s, 124 * s), 24 * s, fill=ACC); ctext(d, 74 * s, 80 * s, "S", A.font("bl", 54 * s), WHITE)
        d.text((146 * s, 32 * s), "NEW ENQUIRY", font=A.font("sb", 26 * s), fill=MUTED); d.text((146 * s, 70 * s), "Kitchen refit · Lucan", font=A.font("bl", 40 * s), fill=INK)
        d.text((146 * s, 124 * s), "Mary · next month", font=A.font("m", 30 * s), fill=(70, 74, 82))
    NOTE = card(840, 180, nd, fill=(250, 250, 252), r=44)
    CALL = A.pill("Call back", 54, ACC, WHITE, w="bl"); CALLING = A.pill("Calling Mary…", 54, WHITE, INK, w="bl")
    def fn(t):
        im = view(8.0 + 0.4 * t, 1.1, 0.5, 0.5, blur=9, dark=0.6); rise(im, h, W / 2, 400, t, 0.05)
        k = eo(t / 0.5); buzz = 8 * math.sin((t - note_at) * 140) if 0 <= t - note_at < 0.25 else 0
        put(im, ph, W / 2 + buzz, 1150 + 700 * (1 - k), k, 0.55)
        nk = (t - note_at) / 0.45
        if nk > 0: put(im, NOTE, W / 2 + buzz, 960 - 180 * (1 - spring(nk, f=1.5, d=6)), clamp(nk / 0.15), 0.9 + 0.1 * back(nk))
        if t >= call_at:
            pop(im, CALLING if t >= tap_at + 0.1 else CALL, W / 2, 1420, t, call_at, 1.3); finger(im, W / 2 + 140, 1420, t, tap_at)
            if t >= tap_at:
                for j in range(3): ring(im, W / 2, 1150, ((t - tap_at) - j * 0.4) / 1.2, col=ACC, maxr=420, width=5, r0=120)
        return im, 0
    return dur, fn, [(0.05, "swish", 0.4), (0.1, "whoosh", 0.5), (note_at, "ping", 0.8), (call_at, "pop", 0.6), (tap_at, "click", 0.8), (tap_at + 0.1, "shimmer", 0.4)]


def scene_waves(dur=5.4, draw=(0.5, 2.6), help_at=3.3):
    """'If work comes in waves…' a busy/quiet wave draws across the year with a glow; '…that's who we help.'"""
    h1 = T("If work comes in waves…", 84); h2 = T("…that's who we help.", 84)
    X0, X1, Y0, Y1 = 110, 970, 820, 1220; months = "JFMAMJJASOND"
    pts = [(X0 + (X1 - X0) * i / 200, (Y0 + Y1) / 2 - 150 * math.sin(i / 200 * 2 * math.pi * 2.5 + 0.4)) for i in range(201)]
    busy, quiet = A.pill("Busy", 34, WHITE, INK, w="bl"), A.pill("Quiet", 34, (60, 66, 80), WHITE, w="bl")
    peaks = [(i, p) for i, p in enumerate(pts[1:-1], 1) if (p[1] < pts[i - 1][1] and p[1] <= pts[i + 1][1]) or (p[1] > pts[i - 1][1] and p[1] >= pts[i + 1][1])]
    def fn(t):
        im = view(1.5 + 0.6 * t, 1.15, 0.6, 0.5, blur=4, dark=0.62); rise(im, h1, W / 2, 470, t, 0.05)
        d = ImageDraw.Draw(im)
        for i, m in enumerate(months): ctext(d, X0 + (X1 - X0) * (i + 0.5) / 12, 1320, m, A.font("monob", 30), (170, 176, 190))
        n = int(200 * eio((t - draw[0]) / (draw[1] - draw[0])))
        if n > 1:
            gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(pts[:n + 1], fill=ACC + (255,), width=24, joint="curve")
            im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(im); d.line(pts[:n + 1], fill=WHITE, width=9, joint="curve")
            x, y = pts[n]; d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=WHITE)
        for i, (x, y) in peaks:
            if i <= n: lab = busy if y < (Y0 + Y1) / 2 else quiet; pop(im, lab, x, y + (-70 if lab is busy else 70), t, draw[0] + (draw[1] - draw[0]) * i / 200, 1.4)
        rise(im, h2, W / 2, 1490, t, help_at); under(im, "…that's who we help.", 84, W / 2, 1490, "who we help", (t - help_at - 0.35) / 0.4)
        return im, 0
    ev = [(0.05, "swish", 0.4), (draw[0], "whoosh", 0.5)] + [(draw[0] + (draw[1] - draw[0]) * i / 200, "pop", 0.35) for i, _ in peaks] + [(help_at, "swish", 0.5), (help_at + 0.35, "swish", 0.5)]
    return dur, fn, ev


def scene_solid(dur=3.6, fill=(0.4, 1.5), honest_at=1.9):
    """'Booked solid all year?' twelve month tiles fill up, then the honest line: 'You probably don't need us.'"""
    h = T("Booked solid all year?", 84); hn = T("You probably don't need us.", 74)
    MO = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    def tile(m, full):
        def dr(d, s):
            ctext(d, 100 * s, 50 * s, m, A.font("bl", 40 * s), WHITE if full else INK)
            ctext(d, 100 * s, 100 * s, "FULL" if full else "", A.font("monob", 24 * s), WHITE)
        return card(200, 140, dr, fill=ACC if full else (238, 240, 244), r=22)
    T0 = [tile(m, False) for m in MO]; T1 = [tile(m, True) for m in MO]
    def fn(t):
        im = view(9.0 + 0.3 * t, 1.1, 0.5, 0.5, blur=9, dark=0.62); rise(im, h, W / 2, 430, t, 0.05)
        for i in range(12):
            r, c = divmod(i, 4); x, y = W / 2 + (c - 1.5) * 230, 720 + r * 170; ft = fill[0] + (fill[1] - fill[0]) * i / 11
            put(im, T1[i] if t >= ft else T0[i], x, y, eo((t - 0.1 - i * 0.02) / 0.3), 1 + 0.12 * (1 - eo((t - ft) / 0.25)) if t >= ft else 1)
        pop(im, hn, W / 2, 1310, t, honest_at, 1.25)
        return im, 0
    return dur, fn, [(0.05, "swish", 0.4)] + [(fill[0] + (fill[1] - fill[0]) * i / 11, "tick", 0.4) for i in range(12)] + [(honest_at, "hit", 0.7)]


def scene_end(dur=4.4, card_at=2.5):
    """'That's it. No magic. Just ads done properly.' over a slow push; then the logo end card"""
    s1, s2, s3 = T("That's it.", 100), T("No magic.", 100), T("Just ads done properly.", 84)
    lg = A.logo().resize((220, 220), Image.LANCZOS); b1, b2 = T("Southline Agency", 70), T("Meta ads for Irish trades", 38, (190, 198, 212), "m")
    def fn(t):
        out = clamp((t - card_at) / 0.35)
        im = vignette(view(6.5 + 0.8 * t, 1.0 + 0.12 * eio(t / dur), 0.7, 0.5, dark=0.25 + 0.5 * out))
        a = 1 - out
        for sp, y, t0 in ((s1, 620, 0.05), (s2, 760, 0.7), (s3, 910, 1.35)):
            if t >= t0: put(im, sp, W / 2, y - 60 * out, a * clamp((t - t0) / 0.15), 1.25 - 0.25 * back((t - t0) / 0.35))
        if a > 0: under(im, "Just ads done properly.", 84, W / 2, 910 - 60 * out, "done properly", (t - 1.8) / 0.4)
        if t >= card_at:
            k = (t - card_at) / 0.5; put(im, lg, W / 2, 900, clamp(k / 0.2), 0.6 + 0.4 * back(k)); ring(im, W / 2, 900, k / 1.6, col=ACC, maxr=360, width=5, r0=110)
            rise(im, b1, W / 2, 1110, t, card_at + 0.3); rise(im, b2, W / 2, 1190, t, card_at + 0.5)
        return im, 0
    return dur, fn, [(0.05, "hit", 0.6), (0.7, "hit", 0.6), (1.35, "hit", 0.7), (1.8, "swish", 0.5), (card_at, "whoosh", 0.5), (card_at + 0.1, "pop", 0.8), (card_at + 0.2, "shimmer", 0.6)]
