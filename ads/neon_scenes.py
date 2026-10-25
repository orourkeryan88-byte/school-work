"""NEON GLASS scenes (style of the user's 'short-form structure' reference): near-black stage with magenta/blue haze,
a moving perspective floor grid, twinkling stars, translucent 3D glass slabs with glowing edges and status dots,
neon-glow type, and a glowing 01/08 section counter. Built for the 8-part structure:
Hook, Lead, Body 1, Open loop, Body 2, Open loop, Body 3, CTA.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite

SEC = {1: (236, 72, 180), 2: (240, 176, 64), 3: (80, 196, 240), 4: (138, 96, 250), 5: (72, 206, 226), 6: (138, 96, 250), 7: (64, 214, 170), 8: (72, 224, 120)}
RED = (255, 76, 96); GREEN = (72, 224, 120); WHITE = (255, 255, 255)
_rng = np.random.default_rng(4)
_STARS = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(1.5, 3.5), _rng.uniform(0, 6.28)) for _ in range(70)]
_BASE = None


def stage(t):
    """dark haze + twinkling stars + perspective floor grid sliding towards the viewer (constant motion)"""
    global _BASE
    if _BASE is None:
        _BASE = A.mesh_bg((16, 10, 34), (4, 4, 12), [(150, 1500, 620, (220, 40, 160), 0.28), (900, 380, 560, (60, 80, 255), 0.22), (540, 1150, 500, (120, 60, 220), 0.12)], grain=1.0)
    im = _BASE.copy(); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    for x, y, r, ph in _STARS:
        a = int(120 + 120 * math.sin(t * 2.2 + ph)); d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 210, 255, max(0, a)))
    vx, vy = W / 2, 1200  # vanishing point; floor below it
    for i in range(-9, 10):
        d.line((vx, vy, vx + i * 260, H + 40), fill=(150, 110, 255, 60), width=2)
    for k in range(12):
        f = ((k + (t * 0.6) % 1) / 12) ** 2.2; y = vy + (H - vy) * f
        d.line((0, y, W, y), fill=(150, 110, 255, int(20 + 70 * f)), width=2)
    im.alpha_composite(o); return im


_gc = {}
def glow_text(s, size, col=WHITE, glow=None, w="bl", blur=16):
    """bright text with a coloured neon glow behind it"""
    k = (s, size, col, glow, w)
    if k in _gc: return _gc[k]
    sp = text(s, w, size, col); pad = 40
    out = Image.new("RGBA", (sp.width + pad * 2, sp.height + pad * 2), (0, 0, 0, 0))
    if glow:
        g = Image.new("RGBA", sp.size, glow + (255,)); g.putalpha(sp.split()[3])
        gl = Image.new("RGBA", out.size, (0, 0, 0, 0)); gl.alpha_composite(g, (pad, pad)); gl = gl.filter(ImageFilter.GaussianBlur(blur))
        out.alpha_composite(gl); out.alpha_composite(gl)
    out.alpha_composite(sp, (pad, pad)); _gc[k] = out; return out


def fit_glow(s, size, col=WHITE, glow=None, maxw=960, w="bl"):
    return glow_text(s, fit_size(s, w, size, maxw), col, glow, w)


_sc = {}
def slab(w, h, col, label="", num="", dot=None, depth=44, lsize=58, lcol=WHITE, sub=""):
    """translucent 3D glass slab: front face + top + right side, glowing edges, gloss, mono number, label, status dot"""
    k = (w, h, col, label, num, dot, depth, lsize, lcol, sub)
    if k in _sc: return _sc[k]
    G = 46; dx, dy = depth * 0.85, -depth * 0.75; S = 2
    cw, ch = int(w + dx + 2 * G), int(h - dy + 2 * G)
    fx0, fy0 = G, G - dy; fx1, fy1 = G + w, G - dy + h
    lite = tuple(int(c + (255 - c) * 0.35) for c in col); dark = tuple(int(c * 0.55) for c in col)

    def fn(d, s, im):
        P = lambda pts: [(x * s, y * s) for x, y in pts]
        top = [(fx0 + 10, fy0), (fx0 + 10 + dx, fy0 + dy), (fx1 + dx - 6, fy0 + dy), (fx1, fy0)]
        side = [(fx1, fy0), (fx1 + dx, fy0 + dy), (fx1 + dx, fy1 + dy), (fx1, fy1)]
        d.polygon(P(side), fill=dark + (130,)); d.polygon(P(top), fill=lite + (120,))
        d.rounded_rectangle((fx0 * s, fy0 * s, fx1 * s, fy1 * s), 18 * s, fill=col + (105,))
        # gloss on the upper half of the front
        g = Image.new("RGBA", (int((fx1 - fx0) * s), int((fy1 - fy0) * s / 2)), (255, 255, 255, 0)); gd = ImageDraw.Draw(g)
        for yy in range(g.height): gd.line((0, yy, g.width, yy), fill=(255, 255, 255, int(46 * (1 - yy / g.height))))
        m = Image.new("L", g.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, g.width - 1, g.height + 40 * s), 18 * s, fill=255); g.putalpha(Image.fromarray(np.minimum(np.asarray(g.split()[3]), np.asarray(m))))
        im.alpha_composite(g, (int(fx0 * s), int(fy0 * s)))
        for poly in (top, side): d.line(P(poly + [poly[0]]), fill=lite + (230,), width=3 * s)
        d.rounded_rectangle((fx0 * s, fy0 * s, fx1 * s, fy1 * s), 18 * s, outline=lite + (240,), width=3 * s)
        d.line(((fx0 + 24) * s, (fy0 + 10) * s, (fx1 - 24) * s, (fy0 + 10) * s), fill=(255, 255, 255, 110), width=2 * s)
        x = fx0 + 34
        if num:
            d.text((x * s, (fy0 + h / 2 - 22) * s), num, font=A.font("monob", 36 * s), fill=(255, 255, 255, 210)); x += 90
        if label:
            f = A.font("bl", lsize * s); tw, th, ox, oy = A.tsize(label, f)
            d.text((x * s - ox, (fy0 + h / 2) * s - th / 2 - oy - (14 * s if sub else 0)), label, font=f, fill=lcol)
            if sub: d.text((x * s, (fy0 + h / 2 + 18) * s), sub, font=A.font("sb", 30 * s), fill=(255, 255, 255, 200))
        if dot:
            cx, cy = fx1 - 56, fy0 + h / 2; d.ellipse(((cx - 14) * s, (cy - 14) * s, (cx + 14) * s, (cy + 14) * s), fill=dot)
    sp = sprite(cw, ch, fn, ss=S)
    # outer glow from the slab's own alpha
    gl = Image.new("RGBA", sp.size, col + (255,)); gl.putalpha(sp.split()[3].point(lambda v: min(255, v * 2)))
    gl = gl.filter(ImageFilter.GaussianBlur(20)); gl.putalpha(gl.split()[3].point(lambda v: v * 6 // 10))
    out = Image.new("RGBA", sp.size, (0, 0, 0, 0)); out.alpha_composite(gl); out.alpha_composite(sp)
    if dot:  # dot glow
        dg = Image.new("RGBA", sp.size, (0, 0, 0, 0)); cx, cy = fx1 - 56, fy0 + h / 2
        ImageDraw.Draw(dg).ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=dot + (200,)); out.alpha_composite(dg.filter(ImageFilter.GaussianBlur(14)))
        ImageDraw.Draw(out).ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=dot)
    _sc[k] = out; return out


def hud(im, n, t, label="KITCHENS  ·  BATHROOMS"):
    """reference-style header: letterspaced mono label left, glowing NN/08 counter right"""
    col = SEC[n]
    put(im, text(label, "monob", 30, (200, 200, 220)), 60 + text(label, "monob", 30).width / 2, 262, 1)
    c = glow_text(f"{n:02d}/08", 76, WHITE, col, "bl", 18); put(im, c, W - 60 - c.width / 2 + 40, 262, 1, 1 + 0.12 * (1 - eo(t / 0.3)))


def neon_rule(im, y, p, col, x0=60, x1=W - 60):
    if p <= 0: return
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o); x = x0 + (x1 - x0) * eo(p)
    d.rounded_rectangle((x0, y - 3, x, y + 3), 3, fill=col + (255,)); im.alpha_composite(o.filter(ImageFilter.GaussianBlur(6))); im.alpha_composite(o)


# ======================================================================= 01 HOOK
def scene_hook(dur=3.6, resolve=(0.55, 0.22), big_at=2.15):
    """frame 0: neon 'Kitchen & bathroom companies,' + a stack of six glass quote slabs (all on screen). Each quote resolves:
    NO REPLY / TOO DEAR / BOOKED / JUST LOOKING / GHOSTED / NO REPLY, then '6 QUOTES. 1 YES.' slams in neon"""
    col = SEC[1]; jobs = ["Kitchen", "Bathroom", "Kitchen", "En-suite", "Kitchen", "Bathroom"]
    res = ["NO REPLY", "TOO DEAR", "BOOKED", "JUST LOOKING", "GHOSTED", "NO REPLY"]
    h1 = fit_glow("Kitchen & bathroom", 104, WHITE, col); h2 = fit_glow("companies,", 130, (255, 180, 235), col)
    b1 = glow_text("6 QUOTES.", 150, WHITE, col); b2 = glow_text("1 YES.", 210, (255, 255, 255), GREEN, blur=24)

    def fn(t):
        im = stage(t); hud(im, 1, t); sh = 12 * (1 - t / 0.18) if t < 0.18 else 0
        put(im, h1, W / 2, 400, 1, 1.05 - 0.05 * eo(t / 0.3)); put(im, h2, W / 2, 520, 1, 1.05 - 0.05 * eo(t / 0.3))
        for i in range(6):
            tr = resolve[0] + i * resolve[1]; done = t >= tr; ok = res[i] == "BOOKED"
            c = (GREEN if ok else RED) if done else col
            sp = slab(820, 104, c, res[i] if done else f"Quote · {jobs[i]}", f"{i + 1:02d}", GREEN if (done and ok) else (RED if done else col), lsize=46)
            y = 690 + i * 132 + 6 * math.sin(t * 2 + i); kk = (t - tr) / 0.25
            put(im, sp, W / 2 + 10 - i * 4, y, 1 if (not done or ok or t < big_at) else 0.55, (1 + 0.06 * (1 - eo(kk))) if done else 1)
            if done and ok: ring(im, W / 2 + 330, y, kk / 1.2, col=GREEN, maxr=200, width=5, r0=30)
        if t >= big_at:
            k = (t - big_at) / 0.3; o = Image.new("RGBA", (W, H), (4, 4, 12, int(170 * clamp(k)))); im.alpha_composite(o)
            put(im, b1, W / 2, 900, clamp(k / 0.25), 1.3 - 0.3 * eo(k)); put(im, b2, W / 2, 1110, clamp((k - 0.55) / 0.25), 1.6 - 0.6 * eo(k - 0.55))
            if 0.55 <= k < 1.0: sh = 14
        return im, sh
    ev = [(0.0, "hit", 1.0)] + [(resolve[0] + i * resolve[1], "ping" if r == "BOOKED" else "tick", 0.6) for i, r in enumerate(res)] + \
         [(big_at, "whoosh", 0.5), (big_at + 0.16, "hit", 1.0)]
    return dur, fn, ev


# ======================================================================= 02 LEAD
def scene_lead(dur=3.4, drops=(0.35, 0.75, 1.15), total_at=1.9):
    col = SEC[2]; items = ["THE DRIVE", "THE MEASURE-UP", "AN EVENING ON THE DESIGN"]
    h = fit_glow("EVERY 'FREE' QUOTE", 92, WHITE, col); h2 = fit_glow("COSTS YOU:", 92, (255, 220, 150), col)
    tot1 = fit_glow("5 DEAD QUOTES", 92, WHITE, col); tot2 = fit_glow("= 15 HOURS UNPAID.", 96, (255, 220, 150), col)

    def fn(t):
        im = stage(t + 10); hud(im, 2, t)
        put_rise(im, h, W / 2, 420, eo(t / 0.25)); put_rise(im, h2, W / 2, 525, eo((t - 0.1) / 0.25))
        for i, (s, d0) in enumerate(zip(items, drops)):
            k = (t - d0) / 0.45
            if k <= 0: continue
            sp = slab(880, 120, col, s, f"{i + 1:02d}", col, lsize=46 if i < 2 else 40)
            put(im, sp, W / 2, 760 + i * 160 - 700 * (1 - spring(k, f=1.6, d=6)), clamp(k / 0.2), 1)
        if t >= total_at:
            k = (t - total_at) / 0.3; put(im, tot1, W / 2, 1320, clamp(k / 0.25), 1.2 - 0.2 * eo(k)); put(im, tot2, W / 2, 1440, clamp((k - 0.4) / 0.25), 1.4 - 0.4 * eo(k - 0.4))
            put(im, text("at ~3 hrs each · example week", "mono", 26, (180, 170, 200)), W / 2, 1540, clamp((k - 0.8) / 0.3))
        return im, (12 if total_at + 0.12 <= t < total_at + 0.26 else 0)
    return dur, fn, [(d0 + 0.25, "hit", 0.7) for d0 in drops] + [(total_at, "whoosh", 0.4), (total_at + 0.12, "hit", 1.0), (total_at + 0.12, "coin", 0.5)]


# ======================================================================= 03 BODY 1
def scene_body1(dur=4.0, scan_from=0.6, win_at=2.9):
    """REASON 1: on the directories they price-shop dozens of companies. A neon grid of listings, a glowing scanner hops
    between them, price tags pop, 'yours' pulses magenta; then 'LOWEST PRICE WINS.'"""
    col = SEC[3]; hdr = fit_glow("REASON 1:", 64, (170, 230, 255), col); h2 = fit_glow("THEY'RE PRICE SHOPPING.", 92, WHITE, col)
    cols, rows = 5, 5; tw, th_ = 168, 128; x0 = W / 2 - (cols - 1) * 190 / 2; y0 = 700; YOU = 12
    tags = ["€", "€€", "€€€"]; hops = [3, 7, 12, 18, 9, 21, 15, 1]
    tile = slab(tw, th_, col, depth=22); you = slab(tw, th_, SEC[1], "YOU", depth=22, lsize=34)
    win = fit_glow("LOWEST PRICE WINS.", 100, WHITE, RED)

    def fn(t):
        im = stage(t + 20); hud(im, 3, t)
        put_rise(im, hdr, W / 2, 400, eo(t / 0.25)); put_rise(im, h2, W / 2, 500, eo((t - 0.1) / 0.25))
        hk = int(clamp((t - scan_from) / 0.28, 0, len(hops) - 1)); cur = hops[hk]
        for i in range(cols * rows):
            r, c = divmod(i, cols); x, y = x0 + c * 190, y0 + r * 150; k = eo((t - 0.1 - i * 0.015) / 0.3)
            put(im, you if i == YOU else tile, x, y, k, 1 + (0.06 * math.sin(t * 8) if i == YOU else 0))
            if t >= scan_from and i in hops[:hk + 1]:
                put(im, text(tags[i % 3], "monob", 34, (255, 230, 140)), x + 20, y - 4, 1)
        if t >= scan_from:  # glowing scanner box on the current listing
            r, c = divmod(cur, cols); x, y = x0 + c * 190, y0 + r * 150
            o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).rounded_rectangle((x - 100, y - 82, x + 120, y + 82), 22, outline=(255, 255, 255, 230), width=5)
            im.alpha_composite(o.filter(ImageFilter.GaussianBlur(4))); im.alpha_composite(o)
        if t >= win_at:
            k = (t - win_at) / 0.3; o = Image.new("RGBA", (W, H), (4, 4, 12, int(150 * clamp(k)))); im.alpha_composite(o)
            put(im, win, W / 2, 1100, clamp(k / 0.25), 1.3 - 0.3 * eo(k))
        return im, (12 if win_at <= t < win_at + 0.15 else 0)
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(scan_from + i * 0.28, "tick", 0.5) for i in range(len(hops))] + [(win_at, "hit", 1.0), (win_at, "glitch", 0.4)]


# ======================================================================= 04 / 06 OPEN LOOPS
def scene_loop(lines, dur=2.6, n=4, key_line=-1, q=True):
    """open loop: lines rise in one by one in neon (key line tinted), a big glowing '?' pulses behind"""
    col = SEC[n]

    def fn(t):
        im = stage(t + 30 + n); hud(im, n, t)
        if q:
            qs = glow_text("?", 700, (60, 40, 120), col, "bl", 40); put(im, qs, W / 2, 1000, 0.5 + 0.2 * math.sin(t * 4), 1 + 0.03 * math.sin(t * 3))
        for j, s in enumerate(lines):
            key = j == (key_line % len(lines))
            sp = fit_glow(s, 108 if key else 88, (220, 200, 255) if key else WHITE, col)
            k = (t - 0.1 - j * 0.32) / 0.3
            if k > 0: put(im, sp, W / 2, 760 + j * 150 + 30 * (1 - eo(k)), clamp(k / 0.3), 1.15 - 0.15 * eo(k))
        neon_rule(im, 760 + len(lines) * 150 - 40, (t - 0.2 - len(lines) * 0.32) / 0.5, col, 200, W - 200)
        return im, 0
    return dur, fn, [(0.1 + j * 0.32, "whoosh" if j < len(lines) - 1 else "hit", 0.45 if j < len(lines) - 1 else 0.8) for j in range(len(lines))]


# ======================================================================= 05 BODY 2
def scene_body2(dur=4.6, like_from=1.0, req_from=1.6):
    """REASON 2: their work is in the feed. A neon glass phone with a before/after makeover playing, hearts floating up,
    a glowing 'Get a quote' button and an example quote-request counter"""
    import kitchen_scenes as K
    col = SEC[5]; hdr = fit_glow("REASON 2:", 64, (170, 240, 250), col); h2 = fit_glow("THEIR WORK IS IN THE FEED.", 88, WHITE, col)
    b, a = K.kitchen_art(600, 560, False), K.kitchen_art(600, 560, True, 1)
    PWn, PHn = 680, 1000
    shell = slab(PWn, PHn, col, depth=30)
    rng = np.random.default_rng(9); hearts = [(rng.uniform(-200, 200), rng.uniform(0, 1.5), rng.uniform(0.7, 1.2)) for _ in range(14)]

    def fn(t):
        im = stage(t + 40); hud(im, 5, t)
        put_rise(im, hdr, W / 2, 400, eo(t / 0.25)); put_rise(im, h2, W / 2, 500, eo((t - 0.1) / 0.25))
        cx, cy = W / 2, 1110; k = eo(t / 0.5)
        put(im, shell, cx, cy + 200 * (1 - k), k)
        f = 0.5 + 0.47 * math.sin(t * 2.6); ba = K.rounded(K.before_after(b, a, f), 24)
        put(im, ba, cx - 14, cy - 110 + 200 * (1 - k), k)
        d = ImageDraw.Draw(im); by = cy + 300 + 200 * (1 - k); pulse = 0.5 + 0.5 * math.sin(t * 6)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(o); od.rounded_rectangle((cx - 270, by - 50, cx + 250, by + 50), 50, fill=col + (255,))
        im.alpha_composite(o.filter(ImageFilter.GaussianBlur(10 + 8 * pulse))); im.alpha_composite(o)
        put(im, text("Get a quote", "bl", 46, (10, 20, 30)), cx - 10, by, k)
        for hx, ht, hs in hearts:  # hearts float up from the post
            p = (t - like_from - ht) / 1.4
            if 0 < p < 1:
                x, y = cx + 260 + hx * 0.4, cy + 100 - 700 * p; r = 26 * hs
                d.ellipse((x - r, y - r, x, y), fill=(255, 80, 150)); d.ellipse((x, y - r, x + r, y), fill=(255, 80, 150)); d.polygon([(x - r, y - r / 2), (x + r, y - r / 2), (x, y + r * 0.9)], fill=(255, 80, 150))
        n = min(7, int(clamp((t - req_from) / 2.2) * 7.99))
        chip = slab(430, 92, col, f"Quote requests  {n:02d}", depth=20, lsize=38); put(im, chip, W / 2, 1640 - 40, eo((t - req_from) / 0.3))
        put(im, text("example", "mono", 24, (170, 190, 200)), W / 2 + 300, 1640 + 10, eo((t - req_from) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4), (like_from, "pop", 0.5)] + [(req_from + i * 0.31, "ping", 0.45) for i in range(7)]


# ======================================================================= 07 BODY 3
def scene_body3(dur=5.0, drops=(0.35, 0.8, 1.25, 1.7), ok_from=2.2, ready_at=3.2, junk_at=0.9):
    """REASON 3: the ad asks first. Four glass question slabs stack like the reference; each dot turns green;
    a 'Just browsing' slab falls away red; READY TO BOOK slab lands"""
    col = SEC[7]; hdr = fit_glow("REASON 3:", 64, (170, 250, 220), col); h2 = fit_glow("THE AD ASKS FIRST.", 100, WHITE, col)
    qa = [("Project", "Kitchen + bathroom"), ("Budget", "€15k+"), ("Start", "Next 3 months"), ("Photos", "Uploaded")]
    ready = slab(820, 130, GREEN, "READY TO BOOK", dot=GREEN, lsize=64)
    junk = slab(600, 96, RED, "Just browsing", dot=RED, lsize=40, depth=24)

    def fn(t):
        im = stage(t + 50); hud(im, 7, t)
        put_rise(im, hdr, W / 2, 400, eo(t / 0.25)); put_rise(im, h2, W / 2, 500, eo((t - 0.1) / 0.25))
        for i, ((q, a), d0) in enumerate(zip(qa, drops)):
            k = (t - d0) / 0.45
            if k <= 0: continue
            ok = t >= ok_from + i * 0.18
            sp = slab(860, 118, col, a, f"{i + 1:02d}", GREEN if ok else (255, 255, 255), lsize=46, sub="")
            y = 720 + i * 150 - 600 * (1 - spring(k, f=1.6, d=6))
            put(im, sp, W / 2 - i * 6, y, clamp(k / 0.2))
            put(im, text(q.upper(), "monob", 26, (190, 255, 230)), W / 2 - 330, y - 44, clamp(k / 0.2))
        if t >= junk_at:  # a tyre-kicker slab drops in and falls away
            k = (t - junk_at) / 1.2; put(im, junk, W / 2 + 220 + 200 * k, 640 + 900 * k * k, clamp(1.4 - k), 1, 20 * k)
        if t >= ready_at:
            k = (t - ready_at) / 0.4; put(im, ready, W / 2, 1400 + 300 * (1 - eo(k)), clamp(k / 0.2), 0.8 + 0.2 * back(k))
            ring(im, W / 2, 1400, k / 1.3, col=GREEN, maxr=520, width=6, r0=200)
            put(im, fit_glow("ONLY BUYERS REACH YOUR PHONE.", 52, WHITE, GREEN), W / 2, 1560, clamp((k - 0.6) / 0.4))
        return im, (12 if ready_at + 0.2 <= t < ready_at + 0.34 else 0)
    return dur, fn, [(d0 + 0.25, "hit", 0.6) for d0 in drops] + [(ok_from + i * 0.18, "ping", 0.45) for i in range(4)] + \
        [(junk_at, "swish", 0.5), (ready_at, "whoosh", 0.5), (ready_at + 0.2, "hit", 1.0), (ready_at + 0.25, "shimmer", 0.6)]


# ======================================================================= 08 CTA
def scene_cta(logo, dur=4.6, keyword="MAKEOVER", type_at=1.0, logo_at=0.4):
    col = SEC[8]; h1 = fit_glow("Want buyers,", 100, WHITE, col); h2 = fit_glow("not browsers?", 112, (200, 255, 220), col)
    lg = logo.resize((220, 220), Image.LANCZOS); m = Image.new("L", lg.size, 0); ImageDraw.Draw(m).ellipse((0, 0, 219, 219), fill=255)
    disc_glow = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); ImageDraw.Draw(disc_glow).ellipse((60, 60, 360, 360), fill=col + (200,)); disc_glow = disc_glow.filter(ImageFilter.GaussianBlur(40))

    def fn(t):
        im = stage(t + 60); hud(im, 8, t)
        put_rise(im, h1, W / 2, 420, eo(t / 0.25)); put_rise(im, h2, W / 2, 535, eo((t - 0.12) / 0.25))
        n = int(clamp((t - type_at) * 11, 0, len(keyword)))
        box = slab(900, 170, col, ("COMMENT  " + keyword[:n]) if n else "COMMENT", lsize=68)
        put(im, box, W / 2, 820, eo((t - 0.3) / 0.35), 0.9 + 0.1 * spring((t - 0.3) / 0.5))
        if t >= logo_at:
            k = (t - logo_at) / 0.4; y = 1160
            put(im, disc_glow, W / 2, y, clamp(k) * (0.7 + 0.3 * math.sin(t * 3)), 1)
            put(im, lg, W / 2, y, clamp(k / 0.2), 0.7 + 0.3 * back(k))
        c = eo((t - logo_at - 0.4) / 0.4)
        put(im, glow_text("SOUTHLINE AGENCY", 58, WHITE, col), W / 2, 1400 + 20 * (1 - c), c)
        put(im, text("Paid ads for kitchen & bathroom companies", "sb", 34, (190, 220, 200)), W / 2, 1480 + 20 * (1 - c), c)
        return im, 0
    return dur, fn, [(0.3, "whoosh", 0.5), (logo_at, "pop", 0.8)] + [(type_at + i / 11, "tick", 0.5) for i in range(len(keyword))] + [(type_at + len(keyword) / 11 + 0.1, "hit", 0.8), (type_at + len(keyword) / 11 + 0.15, "shimmer", 0.7)]
