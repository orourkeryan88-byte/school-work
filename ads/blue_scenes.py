"""Multi-colour scenes on a royal-blue base for the clothing budget Reel (v2): bouncing letters, a phone chat with a
camera push, words popping in different colours with confetti, a strike-and-flip, a glass offer card over drifting
colour blobs, and a confetti wrapper for any scene. Built on adkit + motion."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, WHITE, clamp, put, put_rise, ring, text, pill, back, spring
import motion as M
from motion import expo_out, quint_out, cubic_io, back_out

AMBER, CORAL, MINT, VIOLET, CYAN = (255, 196, 60), (255, 107, 107), (60, 220, 170), (170, 130, 255), (90, 210, 255)
BG_TOP, BG_BOT = (20, 56, 168), (6, 16, 58)
BLOBS = [(250, 500, 520, (40, 120, 255), 0.5), (880, 1400, 560, (120, 60, 230), 0.35), (760, 300, 320, (0, 200, 255), 0.25)]
CONF = [AMBER, CORAL, MINT, VIOLET, CYAN, WHITE]


def wrap(s_, f, maxw):
    """greedy word wrap for a PIL font"""
    out, cur = [], ""
    for w_ in s_.split():
        t = (cur + " " + w_).strip()
        if f.getlength(t) > maxw and cur: out.append(cur); cur = w_
        else: cur = t
    return out + ([cur] if cur else [])


# ======================================================================= confetti (works on any scene)
def confetti(im, dt, x0, y0, n=70, seed=3, spread=900, up=1500):
    """burst of coloured paper pieces with gravity, spin and fade; dt = seconds since the burst"""
    if dt <= 0 or dt > 1.8: return
    rng = random.Random(seed); d = ImageDraw.Draw(im); g = 2600
    for i in range(n):
        vx = rng.uniform(-spread, spread); vy = -rng.uniform(up * 0.4, up); col = CONF[i % len(CONF)]
        w_, h_ = rng.uniform(10, 20), rng.uniform(18, 34); rs = rng.uniform(-12, 12)
        x = x0 + vx * dt * (1 - 0.25 * dt); y = y0 + vy * dt + 0.5 * g * dt * dt; a = rs * dt
        al = int(255 * clamp((1.8 - dt) / 0.5)); sq = abs(math.cos(a * 1.7))
        pts = [(-w_ / 2, -h_ / 2 * sq), (w_ / 2, -h_ / 2 * sq), (w_ / 2, h_ / 2 * sq), (-w_ / 2, h_ / 2 * sq)]
        pts = [(x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a)) for px, py in pts]
        d.polygon(pts, fill=col + (al,))

def with_confetti(scene, at, x=W / 2, y=900, n=70):
    """wrap a scene so a confetti burst fires at `at` seconds"""
    dur, fn, ev = scene
    def f2(t):
        im, sh = fn(t); im = im.copy(); confetti(im, t - at, x, y, n); return im, sh
    return dur, f2, list(ev) + [(at, "pop", 0.7), (at + 0.02, "shimmer", 0.6)]


# ======================================================================= 1. bouncing letters callout
def scene_letters(dur=2.6, words=(("Clothing", WHITE), ("brands,", AMBER)), sub="this is the question you all ask me.", type_at=1.0):
    """each letter drops in on its own spring, staggered left to right; the second word in amber; the subline types
    itself out with a caret; a cyan underline wipes in under it all"""
    full = " ".join(w_ for w_, _ in words); size = A.fit_size(full, "bl", 190, 940); f = A.font("bl", size)
    letters = []; x = W / 2 - A.tsize(full, f)[0] / 2
    for wi, (w_, col) in enumerate(words):
        for ch in w_:
            sp = text(ch, "bl", size, col); adv = f.getlength(ch); letters.append((sp, x + adv / 2, col)); x += adv
        x += f.getlength(" ")
    SB = A.fit_size(sub, "xb", 62, 960); Y = 820
    def fn(t):
        im = A.bg(); d = ImageDraw.Draw(im)
        for i, (sp, cx, col) in enumerate(letters):
            k = (t - 0.04 * i) / 0.55
            if k <= 0: continue
            y = Y - 260 * (1 - spring(k, f=2.2, d=6)); put(im, sp, cx, y, clamp(k / 0.15), 1.0, 0)
        p = quint_out((t - 0.75) / 0.4)
        if p > 0: w_ = A.tsize(full, f)[0]; d.rounded_rectangle((W / 2 - w_ / 2, Y + size * 0.62, W / 2 - w_ / 2 + w_ * p, Y + size * 0.62 + 14), 7, fill=CYAN)
        n = int(clamp((t - type_at) / 0.9) * len(sub))
        if n:
            tsp = text(sub[:n], "xb", SB, WHITE); full_w = text(sub, "xb", SB, WHITE).width
            x0 = W / 2 - full_w / 2; im.alpha_composite(tsp, (int(x0), int(Y + 260 - tsp.height / 2)))
            if n < len(sub) or int(t * 3) % 2: d.rectangle((x0 + tsp.width + 4, Y + 230, x0 + tsp.width + 10, Y + 292), fill=AMBER)
        return im, 0
    ev = [(0.04 * i + 0.3, "tick", 0.25) for i in range(0, len(letters), 2)] + [(0.75, "swish", 0.4)] + [(type_at + i * 0.09, "tick", 0.2) for i in range(10)]
    return dur, fn, ev


# ======================================================================= 2. phone chat, then a camera push into the question
def scene_chat(dur=3.4, msgs=("How much should I spend on ads?", "What's a good daily budget?", "Is €20 a day enough??", "How much do I need for Meta ads?"),
               at=(0.45, 0.8, 1.15, 1.5), push_at=2.0, q=("How much should I", "spend on Meta ads?")):
    """phone slides up; incoming bubbles pop in (each tinted a different colour), then the camera pushes into the last
    bubble and the question fills the screen"""
    ph0 = A.phone(date="Your DMs", clock="9:41", wall=((24, 60, 170), (8, 18, 64), CYAN))
    tints = [(236, 240, 250), (255, 240, 214), (220, 248, 238), (236, 228, 255)]
    def bubble(s_, tint):
        f = A.font("m", 40 * 2); lines = wrap(s_, f, 1300)
        w_ = int(max(f.getlength(l) for l in lines) / 2) + 64; h_ = 54 * len(lines) + 44
        def dr(d, s, im):
            d.rounded_rectangle((0, 0, w_ * s - 1, h_ * s - 1), 34 * s, fill=tint)
            for i, l in enumerate(lines): d.text((32 * s, (20 + i * 54) * s), l, font=A.font("m", 40 * s), fill=(20, 24, 40))
        return A.sprite(w_, h_, dr)
    B = [bubble(m, tints[i % 4]) for i, m in enumerate(msgs)]; ys = [640, 820, 1000, 1180]
    Q1 = text(q[0], "bl", A.fit_size(q[0], "bl", 104), WHITE); Q2 = text(q[1], "bl", A.fit_size(q[1], "bl", 116), grad=(AMBER, CORAL, 0))
    SC = 0.86; PX, PY = W / 2, 1010
    def fn(t):
        im = A.bg(); ph = ph0.copy()
        for i, (b, a) in enumerate(zip(B, at)):
            k = (t - a) / 0.35
            if k > 0: put(ph, b, 60 + b.width / 2 + 20 * (1 - quint_out(k)), ys[i], clamp(k / 0.2), 0.6 + 0.4 * back_out(k))
        M.slide_put(im, ph.resize((int(ph.width * SC), int(ph.height * SC)), Image.LANCZOS), PX, PY + 900, PX, PY, t / 0.55, expo_out)
        if t >= push_at:   # camera push toward the last bubble, crossfading into the question
            k = cubic_io((t - push_at) / 0.6); z = 1 + 2.2 * k
            fx, fy = PX - ph.width * SC / 2 + (60 + B[-1].width / 2) * SC, PY - ph.height * SC / 2 + ys[-1] * SC
            nw, nh = int(W * z), int(H * z); big = im.resize((nw, nh), Image.BILINEAR)
            ox = int(clamp(fx * z - W / 2, 0, nw - W)); oy = int(clamp(fy * z - H / 2, 0, nh - H)); im = big.crop((ox, oy, ox + W, oy + H))
            qa = A.bg(); M.words_rise(qa, [Q1], W / 2, 860, t, push_at + 0.35); M.words_rise(qa, [Q2], W / 2, 1000, t, push_at + 0.5)
            A.underline(qa, Q2, W / 2, 1000 + Q2.height / 2 + 4, (t - push_at - 0.9) / 0.35, CYAN, h=12)
            im = Image.blend(im.convert("RGB"), qa.convert("RGB"), clamp((t - push_at - 0.25) / 0.3)).convert("RGBA")
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.5)] + [(a, "ping", 0.5) for a in at] + [(push_at, "whoosh", 0.7), (push_at + 0.5, "hit", 0.8)]


# ======================================================================= 3. words pop in colours, confetti on 'surprises'
def scene_pop_words(dur=2.4, lines=((("My", WHITE), ("answer", WHITE)), (("always", CYAN),), (("surprises", AMBER), ("them.", CORAL))), at=0.1, gap=0.18, boom=None):
    """each word pops from 0 with an overshoot, one after another, each line its own colour; confetti fires from the
    last line"""
    rows = []; k = 0
    for li, ln in enumerate(lines):
        sz = A.fit_size(" ".join(w_ for w_, _ in ln), "bl", 150 if li != 1 else 96, 900); sps = [text(w_, "bl", sz, c) for w_, c in ln]
        tot = sum(s_.width for s_ in sps) + 30 * (len(sps) - 1); x = W / 2 - tot / 2; row = []
        for s_ in sps: row.append((s_, x + s_.width / 2, at + k * gap)); x += s_.width + 30; k += 1
        rows.append(row)
    ys = [720, 870, 1010]; boom = boom if boom is not None else at + (k - 1) * gap + 0.15
    def fn(t):
        im = A.bg()
        for y, row in zip(ys, rows):
            for s_, x, t0 in row:
                p = (t - t0) / 0.4
                if p > 0: put(im, s_, x, y, clamp(p / 0.15), back_out(p, 2.2), 6 * (1 - quint_out(p)))
        confetti(im, t - boom, W / 2, 1010, 80)
        return im, (8 * (1 - (t - boom) / 0.14) if boom <= t < boom + 0.14 else 0)
    ev = [(at + i * gap, "pop", 0.6) for i in range(k)] + [(boom, "hit", 0.8), (boom + 0.02, "shimmer", 0.5)]
    return dur, fn, ev


# ======================================================================= 4. strike through, flip to the answer
def scene_strike_flip(dur=3.6, l1="It's not", l2="how much.", l3="It's", l4="where it goes.", strike_at=0.8, flip_at=1.6):
    """'how much.' gets a coral strike drawn through it and drops back; a card flips over (squash and stretch) to show
    'where it goes.' on an amber-to-coral card"""
    L1, L2 = text(l1, "xb", 70, (170, 190, 230)), text(l2, "bl", 140, WHITE); L3 = text(l3, "xb", 70, (170, 190, 230))
    cw, ch = 900, 240
    def face(back_):
        def dr(d, s, im):
            if back_:
                g = A.gradient((cw * s, ch * s), AMBER, CORAL, 0); m = Image.new("L", (cw * s, ch * s), 0)
                ImageDraw.Draw(m).rounded_rectangle((0, 0, cw * s - 1, ch * s - 1), 48 * s, fill=255); g.putalpha(m); im.alpha_composite(g)
                f = A.font("bl", A.fit_size(l4, "bl", 120, 820) * s); tw = d.textlength(l4, font=f); d.text(((cw * s - tw) / 2, 50 * s), l4, font=f, fill=(20, 24, 50))
            else:
                d.rounded_rectangle((0, 0, cw * s - 1, ch * s - 1), 48 * s, fill=(255, 255, 255, 30), outline=(255, 255, 255, 90), width=4 * s)
                f = A.font("bl", 120 * s); tw = d.textlength("?", font=f); d.text(((cw * s - tw) / 2, 40 * s), "?", font=f, fill=WHITE)
        return A.shadowed(A.sprite(cw, ch, dr), blur=30, dy=16, alpha=90, pad=50)
    F0, F1 = face(False), face(True)
    def fn(t):
        im = A.bg(); M.words_rise(im, [L1], W / 2, 520, t, 0.05)
        drop = quint_out((t - strike_at - 0.35) / 0.4)
        if t < 0.55: M.words_rise(im, [L2], W / 2, 650, t, 0.12)
        else: put(im, L2, W / 2, 650 + 20 * drop, 1 - 0.35 * drop, 1 - 0.12 * drop)
        p = cubic_io((t - strike_at) / 0.3)
        if p > 0:
            d = ImageDraw.Draw(im); x0 = W / 2 - L2.width / 2 * (1 - 0.12 * drop) - 10; x1 = W / 2 + L2.width / 2 * (1 - 0.12 * drop) + 10
            d.line((x0, 650 + 20 * drop, x0 + (x1 - x0) * p, 650 + 20 * drop - 6), fill=CORAL, width=16)
        M.words_rise(im, [L3], W / 2, 900, t, flip_at - 0.4)
        k = (t - flip_at) / 0.5
        if t > flip_at - 0.5:
            a_ = clamp((t - flip_at + 0.5) / 0.25)
            if k < 0.5: sp = F0; sx = abs(math.cos(clamp(k) * math.pi)) if k > 0 else 1
            else: sp = F1; sx = abs(math.cos(clamp(k) * math.pi))
            sx = max(sx, 0.02); spr = sp.resize((max(1, int(sp.width * sx)), int(sp.height * (1 + 0.06 * (1 - sx)))), Image.BICUBIC)
            put(im, spr, W / 2, 1110, a_)
            if 1 <= k < 1.6: ring(im, W / 2, 1110, (k - 1) / 0.6, col=AMBER, maxr=500, width=6, r0=200)
        return im, 0
    return dur, fn, [(0.05, "swish", 0.4), (0.12, "whoosh", 0.4), (strike_at, "swish", 0.7), (strike_at + 0.35, "click", 0.5), (flip_at, "whoosh", 0.5), (flip_at + 0.5, "hit", 0.8)]


# ======================================================================= 7. glass offer card over drifting colour blobs
def scene_glass_offer(dur=4.2, badge="FREE 15-MIN CALL", big="Your split", lines=("We'll map your budget", "for your brand. Free."),
                      checks=(("Meta ads, run for you", AMBER), ("Your account, your budget", MINT), ("Email: optional add-on", VIOLET)), at=(1.3, 1.65, 2.0)):
    """three colour blobs drift behind a frosted-glass card that rises with motion blur; ticks draw in, each in its own
    colour; a light sweep crosses the card"""
    cw, ch = 900, 900; CX, CY = W / 2, 980
    BD = A.pill(badge, 34, MINT, (10, 30, 40), w="bl"); BG_ = text(big, "bl", 140, WHITE)
    LN = [text(l, "b", 52, WHITE if i == 0 else AMBER) for i, l in enumerate(lines)]
    CK = [(text(c, "sb", 42, WHITE), col) for c, col in checks]
    m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), 56, fill=255)
    rim = A.sprite(cw, ch, lambda d, s, im: d.rounded_rectangle((0, 0, cw * s - 1, ch * s - 1), 56 * s, outline=(255, 255, 255, 110), width=3 * s))
    def tick(p, col):
        def f(d, s, im):
            d.ellipse((0, 0, 64 * s, 64 * s), fill=col); q, q2 = clamp(p * 2), clamp(p * 2 - 1)
            P = [(17, 33), (28, 44), (48, 22)]
            d.line((P[0][0] * s, P[0][1] * s, (P[0][0] + (P[1][0] - P[0][0]) * q) * s, (P[0][1] + (P[1][1] - P[0][1]) * q) * s), fill=(15, 25, 50), width=7 * s)
            if q2 > 0: d.line((P[1][0] * s, P[1][1] * s, (P[1][0] + (P[2][0] - P[1][0]) * q2) * s, (P[1][1] + (P[2][1] - P[1][1]) * q2) * s), fill=(15, 25, 50), width=7 * s)
        return A.sprite(64, 64, f)
    def fn(t):
        bl = [(300 + 120 * math.sin(t * 0.9), 700 + 80 * math.cos(t * 0.7), 300, CORAL, 0.75), (820 + 100 * math.cos(t * 0.8), 1050, 320, MINT, 0.6),
              (520, 1350 + 90 * math.sin(t * 1.1), 300, VIOLET, 0.7)]
        im = A.mesh_bg(BG_TOP, BG_BOT, BLOBS + bl, grain=1.0)
        k = expo_out((t - 0.1) / 0.7); y = CY + 700 * (1 - k)
        x0, y0 = int(CX - cw / 2), int(y - ch / 2)
        region = im.crop((x0, max(0, y0), x0 + cw, min(H, y0 + ch))).filter(ImageFilter.GaussianBlur(30))
        glass = Image.blend(region, Image.new("RGBA", region.size, (255, 255, 255, 255)), 0.12)
        mm = m.crop((0, max(0, -y0), cw, max(0, -y0) + region.height)); im.paste(glass, (x0, max(0, y0)), mm)
        card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); card.alpha_composite(rim)
        put(card, BD, 60 + BD.width / 2, 90, clamp((t - 0.6) / 0.2))
        put(card, BG_, 60 + BG_.width / 2, 230, clamp((t - 0.7) / 0.2))
        for i, l in enumerate(LN): put(card, l, 60 + l.width / 2, 370 + i * 66, clamp((t - 0.85 - i * 0.1) / 0.25))
        ImageDraw.Draw(card).line((60, 500, cw - 60, 500), fill=(255, 255, 255, 60), width=2)
        for i, (c, col) in enumerate(CK):
            p = (t - at[i]) / 0.4
            if p > 0: put(card, tick(quint_out(p), col), 100, 590 + i * 100, clamp(p / 0.2)); put(card, c, 160 + c.width / 2 + 16 * (1 - quint_out(p)), 590 + i * 100, clamp(p / 0.3))
        card = A.shine(card, (t - 2.6) / 0.9, width=90, strength=0.3)
        im.alpha_composite(card, (x0, y0))
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.7), (0.6, "pop", 0.5)] + [(a, "tick", 0.6) for a in at] + [(2.6, "shimmer", 0.5)]
