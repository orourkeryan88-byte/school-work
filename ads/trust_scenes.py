"""TRUST video scenes ('Ryan explains Southline'): code-drawn B-roll (broll.py) behind every line, shot in many ways
(push-ins, freeze frames, a floating framed shot, blurred backgrounds, a fly-in to the ad on the monitor),
with a different animation on every line of the voiceover script. White type with soft shadows, one blue accent.
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed

ACC = (56, 140, 255); WHITE = (255, 255, 255); INK = (16, 18, 24); MUTED = (120, 126, 138)


# ======================================================================= B-roll
SHOT = None  # the B-roll shot currently behind the animations: fn(ts) -> RGB 1080x1920 (see broll.py)

def with_shot(scene, shots):
    """run a scene over B-roll. shots = fn, or [(t_from, fn), ...] to cut between shots inside the scene"""
    dur, fn, ev = scene; shots = shots if isinstance(shots, list) else [(0.0, shots)]
    def f2(t):
        global SHOT
        SHOT = [s_ for t0, s_ in shots if t >= t0][-1]; return fn(t)
    return dur, f2, ev

def frame(ts):
    return SHOT(ts)

def view(ts, zoom=1.0, fx=0.5, fy=0.5, blur=0, dark=0.0):
    """full-screen B-roll at time ts: zoom into (fx, fy), optional blur (done small = cheap and soft) / darken"""
    im = frame(ts); k = 1.0
    if blur: im = im.resize((360, 640), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur * 0.75)); k = 360 / W
    cw, ch = W / zoom, H / zoom; x0 = clamp(fx * W - cw / 2, 0, W - cw); y0 = clamp(fy * H - ch / 2, 0, H - ch)
    out = im.resize((W, H), Image.BICUBIC, box=(x0 * k, y0 * k, (x0 + cw) * k, (y0 + ch) * k)).convert("RGBA")
    if dark > 0: out.alpha_composite(Image.new("RGBA", (W, H), (6, 8, 12, int(255 * clamp(dark)))))
    return out

MON = (0.5, 0.427)   # the ad on the B-roll monitor (broll.desk)
FACE = (0.5, 0.5)    # centre of frame

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
def scene_intro(dur=4.8, places_at=(0.55, 0.85), clear_at=2.1, ryan_at=2.3, line_at=3.1, logo_at=3.6):
    """hook: fast pull-out from the van; 'TRADESMEN' slams on frame 0, 'Ireland' & 'the UK' pins pop in; the callout
    flies up and away, 'I'm Ryan.' slams with a pen circle drawn round 'Ryan', 'I run a marketing agency,' rises,
    the logo flips in like a coin with 'Southline Agency'"""
    big = T("Tradesmen", 200); inn = T("in", 70, (200, 210, 230))
    def place(s_):
        f = A.font("bl", 88); tw = f.getlength(s_); w_, h_ = int(tw + 150), 140
        def dr(d, s, im_):
            d.rounded_rectangle((0, 0, w_ * s - 1, h_ * s - 1), 70 * s, fill=WHITE)
            d.ellipse((34 * s, 40 * s, 94 * s, 100 * s), fill=ACC); d.ellipse((54 * s, 60 * s, 74 * s, 80 * s), fill=WHITE)
            d.text((112 * s, 26 * s), s_, font=A.font("bl", 88 * s), fill=INK)
        return shadowed(sprite(w_, h_, dr), blur=20, dy=10, alpha=150, pad=40)
    IRL, UK = place("Ireland"), place("the UK"); amp = T("&", 90, ACC)
    im_, ryan = T("I'm", 150), T("Ryan.", 150); l2 = T("I run a marketing agency,", 76)
    gap = A.font("bl", 150).getlength(" ") * 0.5; rw = im_.width + ryan.width - 72 + gap - 36
    lg = A.logo().resize((150, 150), Image.LANCZOS); brand = A.pill("Southline Agency", 44, WHITE, INK, w="bl")

    def fn(t):
        z = 1.0 + 0.6 * (1 - eo(t / 0.8)); im = vignette(view(0.2 + t * 0.9, z, 0.5, 0.62, dark=0.2 + 0.25 * clamp((t - clear_at) / 0.4)))
        sh = 14 if t < 0.14 else 0
        out = eio((t - clear_at) / 0.35); a_ = 1 - out; dy = -500 * out * out  # callout flies up and away
        if a_ > 0:
            put(im, big, W / 2, 560 + dy, a_, 1.12 - 0.12 * back(t / 0.3))
            if t >= places_at[0]:
                put(im, inn, W / 2, 735 + dy, a_ * clamp((t - places_at[0]) / 0.15))
                pop(im, IRL, W / 2, 880 + dy, t, places_at[0]) if out == 0 else put(im, IRL, W / 2, 880 + dy, a_)
            if t >= places_at[1]:
                put(im, amp, W / 2, 1010 + dy, a_ * clamp((t - places_at[1]) / 0.15))
                pop(im, UK, W / 2, 1140 + dy, t, places_at[1] + 0.1) if out == 0 else put(im, UK, W / 2, 1140 + dy, a_)
            for i, t0 in enumerate(places_at): ring(im, W / 2, 880 + 260 * i, (t - t0) / 1.0, col=ACC, maxr=300, width=5, r0=60)
        if t >= ryan_at:
            k = (t - ryan_at) / 0.3; x0 = W / 2 - rw / 2; s_ = 1.4 - 0.4 * back(k); y2 = 640
            put(im, im_, x0 + (im_.width - 36) / 2, y2, clamp(k / 0.15), s_)
            rx = x0 + im_.width - 36 + gap + (ryan.width - 36) / 2; put(im, ryan, rx, y2, clamp(k / 0.15), s_)
            if ryan_at <= t < ryan_at + 0.14: sh = 12
            p = eo((t - ryan_at - 0.35) / 0.45)  # pen circle round 'Ryan'
            if p > 0:
                ew, eh = (ryan.width - 40) * 0.62, 105
                ImageDraw.Draw(im).arc((rx - ew, y2 - eh, rx + ew, y2 + eh), 200, 200 + 350 * p, fill=ACC, width=10)
        if t >= line_at: rise(im, l2, W / 2, 830, t, line_at)
        if t >= logo_at:  # coin flip
            k = (t - logo_at) / 0.6; ang = (1 - eo(k)) * math.pi * 3; sx = abs(math.cos(ang))
            if sx > 0.04: put(im, lg.resize((max(1, int(150 * sx)), 150), Image.LANCZOS), W / 2 - brand.width / 2 - 20, 1060, clamp(k / 0.15))
            pk = (t - logo_at - 0.35) / 0.35
            if pk > 0: put(im, brand, W / 2 + 85, 1060, clamp(pk / 0.2), 0.7 + 0.3 * back(pk))
        return im, sh
    ev = [(0.0, "hit", 1.0), (0.0, "whoosh", 0.4), (places_at[0], "pop", 0.7), (places_at[1] + 0.1, "pop", 0.7), (clear_at, "whoosh", 0.6),
          (ryan_at, "hit", 0.9), (ryan_at + 0.35, "swish", 0.6), (line_at, "swish", 0.4), (logo_at, "swish", 0.6), (logo_at + 0.35, "pop", 0.7)]
    return dur, fn, ev


def scene_common(dur=3.0):
    """blurred backdrop + the clip floating in a rounded frame; 'and the biggest question I get asked is…'"""
    FW_, FH_ = 600, 1068
    mask = sprite(FW_, FH_, lambda d, s, im: d.rounded_rectangle((0, 0, FW_ * s - 1, FH_ * s - 1), 44 * s, fill=(255, 255, 255, 255))).split()[3]
    shadow = shadowed(Image.new("RGBA", (FW_ + 16, FH_ + 16), (255, 255, 255, 255)), blur=30, dy=20, alpha=150, pad=60)
    h1, h2 = T("And the biggest", 84), T("question I get asked is…", 84)
    def fn(t):
        ts = 3.5 + t; im = view(ts, 1.2, 0.5, 0.5, blur=8, dark=0.55)
        fr = frame(ts).resize((FW_, FH_), Image.BICUBIC).convert("RGBA"); fr.putalpha(mask)
        k = spring(t / 0.8, f=1.4, d=6); rot = -4 + 2 * math.sin(t * 1.6) + 10 * (1 - eo(t / 0.6))
        sh = shadow.copy(); sh.alpha_composite(fr, (68, 68)); put(im, sh, W / 2, 1180 + 600 * (1 - k), 1, 0.92 + 0.02 * math.sin(t * 2), rot)
        rise(im, h1, W / 2, 380, t, 0.15); rise(im, h2, W / 2, 490, t, 0.4); under(im, "question I get asked is…", 84, W / 2, 490, "question", (t - 0.8) / 0.4)
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


def scene_short(dur=7.9, s1_at=0.2, yeah_at=1.3, props_at=1.75, post_at=3.6, comments_at=(4.3, 4.8, 5.3), calls_at=5.6, cap_at=(5.9, 6.7)):
    """'Short answer? YEAH. when they're done properly.' then a job post goes up on your page: hearts and 'Great job!'
    comments pile on while the calls counter stays at 0, gets circled: 'Posting and hoping / isn't the same thing.'"""
    s1, s2, s3 = T("Short answer?", 84), T("Yeah.", 230, ACC), T("when they're done properly.", 70)
    c1, c2 = T("Posting and hoping", 84), T("isn't the same thing.", 84)
    import kitchen_scenes as K
    pic = K.rounded(K.kitchen_art(680, 400, True, 2), 18)
    def pb(d, s):
        d.ellipse((30 * s, 26 * s, 90 * s, 86 * s), fill=ACC); d.text((110 * s, 30 * s), "Your page", font=A.font("bl", 34 * s), fill=INK)
        d.text((110 * s, 70 * s), "Just finished this one!", font=A.font("m", 26 * s), fill=MUTED)
    POST = card(760, 640, pb, r=30); POST.alpha_composite(pic, (50 + 40, 50 + 116))
    coms = [A.pill(c, 38, WHITE, INK, w="b") for c in ("Great job!", "Lovely work", "Fair play!")]

    def fn(t):
        dk = 0.5 + 0.2 * clamp((t - post_at + 0.3) / 0.3)
        im = vignette(view(7.0 + 0.55 * t, 1.3 + 0.12 * eio(t / dur), *FACE, dark=dk)); sh = 0
        fo = post_at - 0.15; a_ = 1 - clamp((t - fo) / 0.25)
        if a_ > 0:
            rise(im, s1, W / 2, 520, t, s1_at, fo)
            if t >= yeah_at: put(im, s2, W / 2, 760, a_ * clamp((t - yeah_at) / 0.15), 1.6 - 0.6 * back((t - yeah_at) / 0.35))
            rise(im, s3, W / 2, 960, t, props_at, fo)
            if t < fo: under(im, "when they're done properly.", 70, W / 2, 960, "done properly", (t - props_at - 0.5) / 0.4)
            if yeah_at <= t < yeah_at + 0.15: sh = 10
        if t >= post_at:
            k = spring((t - post_at) / 0.6, f=1.4, d=6); py = 900 + 700 * (1 - k); put(im, POST, W / 2, py, clamp((t - post_at) / 0.15))
            d = ImageDraw.Draw(im); ry = py + 320 - 70
            likes = int(round(47 * eo((t - post_at - 0.3) / 1.8))) if t > post_at + 0.3 else 0
            hx = W / 2 - 330; d.ellipse((hx, ry - 14, hx + 22, ry + 8), fill=(240, 70, 100)); d.ellipse((hx + 16, ry - 14, hx + 38, ry + 8), fill=(240, 70, 100))
            d.polygon([(hx + 1, ry), (hx + 37, ry), (hx + 19, ry + 22)], fill=(240, 70, 100)); d.text((hx + 52, ry - 20), f"{likes}", font=A.font("bl", 36), fill=INK)
            d.text((hx + 140, ry - 20), f"{sum(t >= c for c in comments_at)} comments", font=A.font("sb", 32), fill=MUTED)
            calls = A.pill("0 calls", 36, INK, WHITE, w="bl"); cx = W / 2 + 240
            put(im, calls, cx, ry, 1, 1 + 0.12 * math.sin(max(0, t - calls_at) * 9) * (1 - clamp((t - calls_at) / 0.8)) if t >= calls_at else 1)
            if t >= calls_at:  # circle the 0 calls
                p = eo((t - calls_at) / 0.4); d = ImageDraw.Draw(im)
                d.arc((cx - 130, ry - 62, cx + 130, ry + 62), 200, 200 + 355 * p, fill=ACC, width=8)
            for i, (c, ct) in enumerate(zip(coms, comments_at)):
                pop(im, c, W / 2 + (-200 if i % 2 == 0 else 200), 300 + i * 80, t, ct, 1.3)
            rise(im, c1, W / 2, 1380, t, cap_at[0]); rise(im, c2, W / 2, 1490, t, cap_at[1])
        return im, sh
    ev = [(s1_at, "swish", 0.4), (yeah_at, "hit", 0.8), (props_at, "swish", 0.4), (props_at + 0.5, "swish", 0.5), (post_at, "whoosh", 0.6)] + \
         [(post_at + 0.3 + i * 0.15, "tick", 0.25) for i in range(10)] + [(c, "pop", 0.5) for c in comments_at] + [(calls_at, "swish", 0.6), (cap_at[0], "swish", 0.4), (cap_at[1], "hit", 0.6)]
    return dur, fn, ev


def scene_title(num, lines, src, zoom, fx, fy, dur=2.3, chips=None, hi_chip=None):
    """section card: freeze frame, darkened; big accent number slams, the question pops in word by word.
    chips = optional rows of labels that pop in underneath (hi_chip is drawn in the accent colour)"""
    nsp = T(num, 150, ACC, "monob"); words = [[T(w_, 92) for w_ in l.split(" ")] for l in lines]
    CH_ = [[A.pill(c, 44, ACC if c == hi_chip else WHITE, WHITE if c == hi_chip else INK, w="bl") for c in row] for row in (chips or [])]
    sp = A.font("bl", 92).getlength(" ")
    def fn(t):
        im = view(src, zoom + 0.08 * eio(t / dur), fx, fy, blur=3, dark=0.62)
        pop(im, nsp, W / 2, 720, t, 0.0, 1.8); k = 0.3
        for j, ws in enumerate(words):
            tot = sum(w_.width - 72 for w_ in ws) + sp * (len(ws) - 1); x = W / 2 - tot / 2
            for w_ in ws:
                pop(im, w_, x + (w_.width - 72) / 2, 930 + j * 120, t, k, 1.5); x += w_.width - 72 + sp; k += 0.1
        for r, row in enumerate(CH_):
            tot = sum(c.width for c in row) + 20 * (len(row) - 1); x = W / 2 - tot / 2
            for c in row: pop(im, c, x + c.width / 2, 1250 + r * 110, t, k, 1.4); x += c.width + 20; k += 0.12
        return im, (12 if t < 0.12 else 0)
    n = sum(len(l.split(" ")) for l in lines)
    return dur, fn, [(0.0, "hit", 1.0)] + [(0.3 + i * 0.1, "pop", 0.3) for i in range(n)]


def scene_what(dur=4.6, s0_at=0.1, pills_at=(0.45, 0.75), s1_at=1.4, pin_at=2.6, s3_at=2.9):
    """fly into the monitors; 'We run' + Facebook / Instagram pills + 'ads for trades & local businesses' + pin 'in Ireland & the UK'"""
    s0 = T("We run", 84); s1 = T("ads for trades across", 84); s3 = T("Ireland & the UK.", 84)
    pf, pi = A.pill("Facebook", 50, WHITE, INK, w="bl"), A.pill("Instagram", 50, WHITE, INK, w="bl"); plus = T("+", 80, ACC)
    def fn(t):
        im = vignette(view(0.5 + 0.8 * t, 1.5 + 0.35 * eio(t / dur), *MON, dark=0.4))
        rise(im, s0, W / 2, 470, t, s0_at)
        pop(im, pf, W / 2 - 220, 630, t, pills_at[0]); pop(im, plus, W / 2 + 10, 630, t, pills_at[0] + 0.15); pop(im, pi, W / 2 + 240, 630, t, pills_at[1])
        rise(im, s1, W / 2, 880, t, s1_at)
        k = (t - pin_at) / 0.45
        if k > 0:  # location pin drops in
            py = 1150 - 220 * (1 - spring(k, f=1.5, d=6)); d = ImageDraw.Draw(im)
            d.ellipse((W / 2 - 44, py - 104, W / 2 + 44, py - 16), fill=ACC); d.polygon([(W / 2 - 34, py - 48), (W / 2 + 34, py - 48), (W / 2, py + 4)], fill=ACC)
            d.ellipse((W / 2 - 16, py - 76, W / 2 + 16, py - 44), fill=WHITE); ring(im, W / 2, 1150, (t - pin_at - 0.3) / 1.0, col=ACC, maxr=260, width=5, r0=30)
        rise(im, s3, W / 2, 1290, t, s3_at)
        return im, 0
    return dur, fn, [(s0_at, "swish", 0.4), (pills_at[0], "pop", 0.6), (pills_at[1], "pop", 0.6), (s1_at, "swish", 0.4), (pin_at, "pop", 0.7), (s3_at, "swish", 0.4)]


def scene_trades(dur=3.6, times=(0.15, 0.65, 1.15, 1.65, 2.15)):
    """trade chips slide in from alternating sides and stack; the newest one is blue"""
    names = ["Plumbers", "Builders", "Electricians", "Kitchen fitters", "Bathroom fitters"]
    W0 = [A.pill(n, 56, WHITE, INK, w="bl") for n in names]; W1 = [A.pill(n, 56, ACC, WHITE, w="bl") for n in names]
    def fn(t):
        im = view(4.2 + 0.5 * t, 1.15, 0.5, 0.5, blur=9, dark=0.55)
        last = sum(t >= x for x in times) - 1
        for i in range(len(names)):
            k = (t - times[i]) / 0.4
            if k <= 0: continue
            side = -1 if i % 2 == 0 else 1
            put(im, W1[i] if i == last else W0[i], W / 2 + side * 700 * (1 - eo(k)), 620 + i * 170, 1, 1, side * 6 * (1 - eo(k)))
        return im, 0
    return dur, fn, [(x, "click", 0.7) for x in times]


def scene_aim(dur=4.4, ring_at=0.9, pings_at=1.7, lines_at=(0.05, 0.25, 0.45)):
    """'The goal's simple: people near you asking for a quote.' radius map with quote pings"""
    h0 = T("The goal's simple:", 64, (200, 210, 230)); h1, h2 = T("people near you", 84), T("asking for a quote.", 84)
    MX, MY, R = W / 2, 1180, 300
    rng = np.random.default_rng(5); houses = [(MX + rng.uniform(-420, 420), MY + rng.uniform(-330, 330)) for _ in range(70)]
    inside = [h for h in houses if math.hypot(h[0] - MX, h[1] - MY) < R - 20]; pings = inside[:5]
    bub = A.pill("Quote request", 26, WHITE, INK, w="bl")
    def fn(t):
        im = view(1.0 + 0.6 * t, 1.1, 0.5, 0.5, blur=9, dark=0.62)
        rise(im, h0, W / 2, 400, t, lines_at[0]); rise(im, h1, W / 2, 500, t, lines_at[1]); rise(im, h2, W / 2, 605, t, lines_at[2])
        under(im, "asking for a quote.", 84, W / 2, 605, "asking for a quote", (t - lines_at[2] - 0.35) / 0.5)
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
    return dur, fn, [(lines_at[0], "swish", 0.4), (lines_at[1], "swish", 0.4), (lines_at[2] + 0.35, "swish", 0.5), (ring_at, "whoosh", 0.5)] + [(pings_at + i * 0.35, "ping", 0.45) for i in range(5)]


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
        im = vignette(view(3.6 + 0.35 * u, z, *MON, dark=0.4))
        if u < 0.12: im.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(160 * (1 - u / 0.12)))))
        for j in range(3): ring(im, W / 2, 900, ((u - 0.9) - j * 0.45) % 1.35 / 1.35 if u > 0.9 else 0, col=ACC, maxr=500, width=5, r0=60)
        rise(im, hB1, W / 2, 1380, t, fly_at + 0.6); rise(im, hB2, W / 2, 1490, t, fly_at + 0.85)
        under(im, "in the area you cover.", 84, W / 2, 1490, "the area you cover", (u - 1.3) / 0.5)
        return im, 0
    return dur, fn, [(0.1, "swish", 0.4)] + [(0.4 + i * 0.45 + 0.3, "hit", 0.45) for i in range(3)] + [(2.3, "swish", 0.5), (2.6, "pop", 0.6),
                     (fly_at - 0.1, "whoosh", 0.7), (fly_at + 0.6, "swish", 0.4), (fly_at + 0.85, "swish", 0.4), (fly_at + 1.3, "swish", 0.5)]


def scene_questions(dur=4.6, rows_at=(0.8, 1.4, 2.0), h2_at=0.3, know_at=None):
    """'Before anyone gets in touch, a few quick questions.' form card; each answer chip pops in with a tick"""
    h1, h2 = T("Before anyone gets in touch,", 74), T("a few quick questions.", 84)
    qa = [("WHAT'S THE JOB?", "Kitchen refit"), ("WHERE?", "Lucan"), ("WHEN?", "Next month")]
    FORM = card(880, 600); chips = [A.pill(a + "  ✓", 40, ACC, WHITE, w="bl") for _, a in qa]; know = A.pill("You know the job before you ring", 42, WHITE, INK, w="bl")
    def fn(t):
        im = view(6.0 + 0.5 * t, 1.1, 0.5, 0.5, blur=9, dark=0.6)
        rise(im, h1, W / 2, 420, t, 0.05); rise(im, h2, W / 2, 530, t, h2_at); under(im, "a few quick questions.", 84, W / 2, 530, "quick questions", (t - h2_at - 0.3) / 0.4)
        k = spring((t - 0.3) / 0.6, f=1.4, d=6); fy = 1050 + 500 * (1 - k); put(im, FORM, W / 2, fy, clamp((t - 0.3) / 0.15))
        if t > 0.5:
            d = ImageDraw.Draw(im)
            for i, (q, _) in enumerate(qa):
                y = fy - 300 + 110 + i * 180; d.text((W / 2 - 380, y - 30), q, font=A.font("monob", 28), fill=MUTED)
                if i: d.line((W / 2 - 380, y - 70, W / 2 + 380, y - 70), fill=(228, 230, 234), width=2)
                ck = (t - rows_at[i]) / 0.35
                if ck > 0: put(im, chips[i], W / 2 + 380 - chips[i].width / 2, y + 45, clamp(ck / 0.2), 0.6 + 0.4 * back(ck))
                else: d.rounded_rectangle((W / 2 - 380, y + 15, W / 2 + 380, y + 75), 20, outline=(220, 222, 228), width=3)
        if know_at is not None: pop(im, know, W / 2, 1490, t, know_at, 1.3)
        return im, 0
    return dur, fn, [(0.05, "swish", 0.4), (0.3, "whoosh", 0.4), (h2_at, "swish", 0.5)] + [(r, "pop", 0.6) for r in rows_at] + ([(know_at, "hit", 0.6)] if know_at else [])


def scene_phone(dur=3.8, note_at=0.9, call_at=2.0, tap_at=2.5, quote_at=None, book_at=None, tools_at=None):
    """'Straight to your phone.' a phone rises, the enquiry drops in with a buzz, 'Call back' is tapped, rings pulse.
    Then the phone slides left and the steps tick in on the right: Quote sent -> Booked -> Back to the tools."""
    h = T("Straight to your phone.", 84); h2 = T("Back to what you do best.", 80); ph = A.phone("Monday 3 November", "09:41", wall=((28, 34, 46), (8, 10, 14), ACC))
    def nd(d, s):
        d.rounded_rectangle((30 * s, 36 * s, 118 * s, 124 * s), 24 * s, fill=ACC); ctext(d, 74 * s, 80 * s, "S", A.font("bl", 54 * s), WHITE)
        d.text((146 * s, 32 * s), "NEW ENQUIRY", font=A.font("sb", 26 * s), fill=MUTED); d.text((146 * s, 70 * s), "Kitchen refit · Lucan", font=A.font("bl", 40 * s), fill=INK)
        d.text((146 * s, 124 * s), "Mary · next month", font=A.font("m", 30 * s), fill=(70, 74, 82))
    NOTE = card(840, 180, nd, fill=(250, 250, 252), r=44)
    CALL = A.pill("Call back", 54, ACC, WHITE, w="bl"); CALLING = A.pill("Calling Mary…", 54, WHITE, INK, w="bl")
    steps = [(quote_at, A.pill("Quote sent  ✓", 46, WHITE, INK, w="bl")), (book_at, A.pill("Booked in  ✓", 46, WHITE, INK, w="bl")), (tools_at, A.pill("Back to the tools", 46, ACC, WHITE, w="bl"))]
    def fn(t):
        im = view(8.0 + 0.4 * t, 1.1, 0.5, 0.5, blur=9, dark=0.6)
        sw = eio((t - quote_at) / 0.5) if quote_at else 0; px, ps = W / 2 - 240 * sw, 0.55 - 0.1 * sw  # phone slides left for the steps
        if tools_at and t >= tools_at - 0.1:
            o = clamp((t - tools_at + 0.1) / 0.25); put(im, h, W / 2, 400 - 40 * o, 1 - o); rise(im, h2, W / 2, 400, t, tools_at)
        else: rise(im, h, W / 2, 400, t, 0.05)
        k = eo(t / 0.5); buzz = 8 * math.sin((t - note_at) * 140) if 0 <= t - note_at < 0.25 else 0
        put(im, ph, px + buzz, 1150 + 700 * (1 - k), k, ps)
        nk = (t - note_at) / 0.45
        if nk > 0: put(im, NOTE, px + buzz, 960 - 180 * (1 - spring(nk, f=1.5, d=6)), clamp(nk / 0.15) * (1 - sw), (0.9 + 0.1 * back(nk)) * (1 - 0.3 * sw))
        if t >= call_at:
            pop(im, CALLING if t >= tap_at + 0.1 else CALL, px, 1420, t, call_at, 1.3) if sw < 0.5 else put(im, CALLING, px, 1420, 2 * (1 - sw))
            finger(im, W / 2 + 140, 1420, t, tap_at)
            if t >= tap_at and sw == 0:
                for j in range(3): ring(im, W / 2, 1150, ((t - tap_at) - j * 0.4) / 1.2, col=ACC, maxr=420, width=5, r0=120)
        for i, (st, sp) in enumerate(steps):
            if st is not None and t >= st:
                kk = (t - st) / 0.4; put(im, sp, W / 2 + 230 + 300 * (1 - eo(kk)), 900 + i * 190, clamp(kk / 0.2), 0.8 + 0.2 * back(kk))
        return im, 0
    ev = [(0.05, "swish", 0.4), (0.1, "whoosh", 0.5), (note_at, "ping", 0.8), (call_at, "pop", 0.6), (tap_at, "click", 0.8), (tap_at + 0.1, "shimmer", 0.4)]
    ev += [(x, "pop", 0.7) for x in (quote_at, book_at) if x] + ([(quote_at - 0.05, "whoosh", 0.4)] if quote_at else []) + ([(tools_at, "hit", 0.8), (tools_at, "swish", 0.4)] if tools_at else [])
    return dur, fn, ev


def scene_wom(dur=6.2, bubbles_at=(0.7, 1.3, 1.9), dry_at=2.5, swap=3.0, ul_at=3.6, help_at=4.8):
    """'Tradesmen still relying on word of mouth…' - referral speech bubbles pop in left/right, then go grey and drift
    up and away (it dries up). '…and struggling to get booked out?' - a two-week calendar, nearly empty, the empty days
    pulsing. 'That's who we help.'"""
    a1, a2 = T("Tradesmen still relying", 76), T("on word of mouth…", 84)
    b1, b2 = T("Good at the job, but", 84), T("struggling to stay booked out.", 84); hp = T("That's who we help.", 96)
    says = [("Know a good plumber?", -1), ("Ask Mick, he's sound.", 1), ("Grand, I'll get his number.", -1)]
    def bubble(s_, side, grey=False):
        f = A.font("b", 46); w_, h_ = int(f.getlength(s_) + 80), 120
        def dr(d, s, im_):
            fill = (210, 212, 218) if grey else WHITE
            d.rounded_rectangle((0, 0, w_ * s - 1, (h_ - 24) * s), 40 * s, fill=fill)
            tx = 60 if side < 0 else w_ - 60; d.polygon([((tx - 20) * s, (h_ - 30) * s), ((tx + 20) * s, (h_ - 30) * s), ((tx - 30 * side) * s, h_ * s - 1)], fill=fill)
            d.text((40 * s, 22 * s), s_, font=A.font("b", 46 * s), fill=MUTED if grey else INK)
        return shadowed(sprite(w_, h_, dr), blur=18, dy=10, alpha=140, pad=40)
    BB = [(bubble(s_, sd), bubble(s_, sd, True)) for s_, sd in says]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]; booked = {1: "Leak fix", 7: "Quote"}
    def cell(i):
        def dr(d, s, im_):
            ctext(d, 75 * s, 30 * s, days[i % 5], A.font("sb", 26 * s), (170, 178, 194))
            if i in booked:
                d.rounded_rectangle((12 * s, 58 * s, 138 * s, 128 * s), 18 * s, fill=ACC); ctext(d, 75 * s, 93 * s, booked[i], A.font("bl", 24 * s), WHITE)
            else: d.rounded_rectangle((12 * s, 58 * s, 138 * s, 128 * s), 18 * s, outline=(110, 118, 136), width=3 * s)
        return sprite(150, 140, dr)
    CELLS = [cell(i) for i in range(10)]; wk = [T("Week 1", 34, (170, 178, 194), "b"), T("Week 2", 34, (170, 178, 194), "b")]

    def fn(t):
        im = view(1.5 + 0.6 * t, 1.15, 0.6, 0.5, blur=6, dark=0.62)
        if t < swap + 0.3:
            o = eio((t - swap) / 0.3); dx = -1100 * o
            rise(im, a1, W / 2 + dx, 410, t, 0.05); rise(im, a2, W / 2 + dx, 515, t, 0.3)
            under(im, "on word of mouth…", 84, W / 2 + dx, 515, "word of mouth", (t - 0.7) / 0.4)
            dry = eio((t - dry_at) / 0.6)
            for i, ((sp0, sp1), (_, sd)) in enumerate(zip(BB, says)):
                k = (t - bubbles_at[i]) / 0.4
                if k <= 0: continue
                x = W / 2 + sd * 90 + dx; y = 780 + i * 200 - 160 * dry
                put(im, sp1 if dry > 0.3 else sp0, x, y, clamp(k / 0.15) * (1 - 0.75 * dry), (0.6 + 0.4 * back(k)) * (1 - 0.15 * dry))
        if t >= swap:
            u = t - swap; dx = 1100 * (1 - eio(u / 0.3))
            rise(im, b1, W / 2 + dx, 420, t, swap + 0.05); rise(im, b2, W / 2 + dx, 525, t, swap + 0.25)
            under(im, "struggling to stay booked out.", 84, W / 2 + dx, 525, "booked out", (t - ul_at) / 0.4)
            for r in range(2):
                put(im, wk[r], W / 2 - 330 + dx, 700 + r * 230, eo((u - 0.2) / 0.3))
                for c in range(5):
                    i = r * 5 + c; x = W / 2 + (c - 2) * 162 + dx; y = 800 + r * 230
                    pulse = 1 + (0.03 * math.sin(t * 5 + i) if i not in booked else 0)
                    put(im, CELLS[i], x, y, eo((u - 0.3 - i * 0.04) / 0.3), pulse)
            pop(im, hp, W / 2, 1400, t, help_at, 1.4); under(im, "That's who we help.", 96, W / 2, 1400, "who we help", (t - help_at - 0.35) / 0.4)
        return im, 0
    ev = [(0.05, "swish", 0.4), (0.3, "swish", 0.4), (0.7, "swish", 0.5)] + [(b_, "pop", 0.5) for b_ in bubbles_at] + [(dry_at, "whoosh", 0.4),
          (swap, "whoosh", 0.6), (swap + 0.25, "swish", 0.4), (ul_at, "swish", 0.5), (help_at, "hit", 0.8), (help_at + 0.35, "swish", 0.5)]
    return dur, fn, ev


def scene_end(dur=4.4, card_at=2.5, lines_at=(0.05, 0.7, 1.35)):
    """'That's it. No magic. Just ads done properly.' over a slow push; then the logo end card"""
    s1, s2, s3 = T("That's it.", 100), T("No magic.", 100), T("Just ads done properly.", 84)
    lg = A.logo().resize((220, 220), Image.LANCZOS); b1, b2 = T("Southline Agency", 70), T("Meta ads for trades in Ireland & the UK", 38, (190, 198, 212), "m")
    def fn(t):
        out = clamp((t - card_at) / 0.35)
        im = vignette(view(6.5 + 0.8 * t, 1.0 + 0.12 * eio(t / dur), 0.7, 0.5, dark=0.25 + 0.5 * out))
        a = 1 - out
        for sp, y, t0 in zip((s1, s2, s3), (620, 760, 910), lines_at):
            if t >= t0: put(im, sp, W / 2, y - 60 * out, a * clamp((t - t0) / 0.15), 1.25 - 0.25 * back((t - t0) / 0.35))
        if a > 0: under(im, "Just ads done properly.", 84, W / 2, 910 - 60 * out, "done properly", (t - lines_at[2] - 0.45) / 0.4)
        if t >= card_at:
            k = (t - card_at) / 0.5; put(im, lg, W / 2, 900, clamp(k / 0.2), 0.6 + 0.4 * back(k)); ring(im, W / 2, 900, k / 1.6, col=ACC, maxr=360, width=5, r0=110)
            rise(im, b1, W / 2, 1110, t, card_at + 0.3); rise(im, b2, W / 2, 1190, t, card_at + 0.5)
        return im, 0
    return dur, fn, [(lines_at[0], "hit", 0.6), (lines_at[1], "hit", 0.6), (lines_at[2], "hit", 0.7), (lines_at[2] + 0.45, "swish", 0.5), (card_at, "whoosh", 0.5), (card_at + 0.1, "pop", 0.8), (card_at + 0.2, "shimmer", 0.6)]


def thumb_frame(path):
    """square brand card placed in the middle of a 9:16 frame; the navy above and below is extended from its own
    top/bottom edge colours and blended in, so it reads as one clean full-screen image (Instagram cover / thumbnail)"""
    sq = Image.open(path).convert("RGB").resize((W, W), Image.LANCZOS); a = np.asarray(sq).astype(np.float32)
    top, bot = a[:20].reshape(-1, 3).mean(0), a[-20:].reshape(-1, 3).mean(0)
    g = np.linspace(0, 1, H)[:, None, None]; bg = top * (1 - g) + bot * g; bg = np.repeat(bg, W, axis=1)
    y0 = (H - W) // 2; F = 170  # feather the square's top and bottom edges into the extension
    m = np.ones((W, 1, 1), np.float32); ramp = np.linspace(0, 1, F)[:, None, None]; m[:F] = ramp; m[-F:] = ramp[::-1]
    bg[y0:y0 + W] = bg[y0:y0 + W] * (1 - m) + a * m
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")


def scene_thumb(path, dur=2.5):
    """clean end card held still: settles in over 0.4s, then not a single pixel moves (pick any frame as the cover)"""
    card_ = thumb_frame(path)
    def fn(t):
        s = 1.04 - 0.04 * eo(t / 0.4)
        if s <= 1.0005: return card_.copy(), 0
        im = card_.resize((int(W * s), int(H * s)), Image.BICUBIC); x, y = (im.width - W) // 2, (im.height - H) // 2
        return im.crop((x, y, x + W, y + H)), 0
    return dur, fn, [(0.0, "shimmer", 0.5)]
