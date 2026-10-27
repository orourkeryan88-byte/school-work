"""Custom scenes for the clothing 'How much should I spend?' Reel (ember theme: near-black, warm orange glow, amber):
a DM inbox that keeps asking the same question, three glass jars filling as the budget splits, and a weekly loop
with an arrow running round it. Built on adkit + motion (motion blur, masked word rises)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, WHITE, clamp, put, put_rise, ring, text, pill, eo, back, spring
import motion as M
from motion import expo_out, quint_out, cubic_io, back_out

def T(s, w="xb", size=80, col=None, maxw=960):
    return text(s, w, A.fit_size(s, w, size, maxw), col)


# ======================================================================= 1. DMs all asking the same thing
def scene_dms(dur=3.4, rows=(("S", "Streetwear brand", "How much should I spend on ads?"), ("A", "Activewear brand", "What's a good daily budget?"),
                             ("L", "Linen label", "Is €20 a day enough?"), ("K", "Kidswear brand", "How much do I need for Meta ads?")),
              at=(0.25, 0.6, 0.95, 1.3), q_at=1.9, q=("How much should I", "spend on Meta ads?")):
    """message rows drop into an inbox one after another (newest on top, older ones slide down), each with a small
    orange unread dot; then the inbox dims and the question itself rises big over it"""
    cw, ch = 900, 150
    def row(ini, who, msg):
        def dr(d, s):
            d.ellipse((30 * s, 30 * s, 120 * s, 120 * s), fill=(58, 46, 40)); f = A.font("bl", 44 * s); tw, th, ox, oy = A.tsize(ini, f)
            d.text((75 * s - tw / 2 - ox, 75 * s - th / 2 - oy), ini, font=f, fill=A.TH["accent2"])
            d.text((150 * s, 30 * s), who, font=A.font("b", 34 * s), fill=A.TH["ink"]); d.text((150 * s, 82 * s), msg, font=A.font("m", 32 * s), fill=A.TH["muted"])
            d.ellipse(((cw - 50) * s, 62 * s, (cw - 26) * s, 86 * s), fill=A.TH["accent"])
        return A.card_sprite(cw, ch, dr, radius=34)
    R = [row(*r) for r in rows]; HD = A.pill("Your DMs this week", 32); EX = text("example", "m", 24, A.TH["muted"])
    Q1, Q2 = T(q[0], "bl", 100), text(q[1], "bl", A.fit_size(q[1], "bl", 112), grad=(A.TH["accent"], A.TH["accent2"], 0))
    TOP = 560; RH = ch + 30
    def fn(t):
        im = A.bg(); dim = quint_out((t - q_at) / 0.4)
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        put(layer, HD, W / 2, 400, clamp(t / 0.25))
        arrived = [i for i, a in enumerate(at) if t >= a]
        for rank, i in enumerate(reversed(arrived)):
            if rank == 0: k = (t - at[i]) / 0.45; y = TOP - 120 * (1 - spring(k, f=1.6, d=6)); al = clamp(k / 0.15)
            else: nk = expo_out((t - at[arrived[-1]]) / 0.4); y = TOP + (rank - 1) * RH + RH * nk; al = 1
            put(layer, R[i], W / 2, y, al)
        put(layer, EX, W / 2 + 380, TOP + 4 * RH - 40, clamp((t - 1.0) / 0.3))
        if dim > 0: layer.putalpha(layer.split()[3].point(lambda v: int(v * (1 - 0.94 * dim))))
        im.alpha_composite(layer)
        if t >= q_at:
            M.words_rise(im, [Q1], W / 2, 860, t, q_at + 0.1); M.words_rise(im, [Q2], W / 2, 990, t, q_at + 0.3)
            A.underline(im, Q2, W / 2, 990 + Q2.height / 2 + 4, (t - q_at - 0.7) / 0.35, h=12)
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4)] + [(a, "ping", 0.55) for a in at] + [(q_at + 0.1, "whoosh", 0.5), (q_at + 0.3, "hit", 0.7)]


# ======================================================================= 2. the budget splits into three jars
def scene_jars(dur=6.8, budget="€30/day", parts=(("TEST", "new ads", 0.2), ("SCALE", "the winners", 0.6), ("REMIND", "past visitors", 0.2)),
               pour=(1.1, 4.4), n_coins=30, label_at=(1.4, 2.3, 3.6), done_at=4.9, cols=None, pill_col=None):
    """a budget pill at the top pours coins down curved paths into three glass jars; each jar fills with glowing liquid
    to its share and its percentage counts up; the middle (scale) jar takes most of it"""
    xs = [W / 2 - 320, W / 2, W / 2 + 320]; JW, JH, JY = 230, 420, 1180   # jar centre y
    cols = list(cols or [A.TH["accent2"], A.TH["accent"], (255, 140, 90)])
    BP = A.shadowed(pill(budget, 56, pill_col or A.TH["accent"], w="bl"), blur=24, dy=12, alpha=90, pad=40); EX = text("example split", "m", 26, A.TH["muted"])
    TT = T("We split it three ways.", "xb", 72)
    lab = [(text(a, "bl", 46, cols[i]), text(b, "sb", 28, A.TH["muted"])) for i, (a, b, _) in enumerate(parts)]
    coin = A.sprite(54, 54, lambda d, s, im: (d.ellipse((0, 0, 54 * s, 54 * s), fill=A.TH["accent2"]), d.ellipse((6 * s, 6 * s, 48 * s, 48 * s), outline=(200, 120, 40), width=3 * s),
                                              d.text((16 * s, 6 * s), "€", font=A.font("bl", 34 * s), fill=(90, 50, 20))))
    # which jar each coin goes to, in proportion to the split, spread over the pour window
    plan = []
    for i in range(n_coins):
        f = (i + 0.5) / n_coins; j = 0 if f < parts[0][2] else (1 if f < parts[0][2] + parts[1][2] else 2)
        plan.append(j)
    order = sorted(range(n_coins), key=lambda i: (i * 7) % n_coins)   # interleave jars so they fill together
    TC = {c: pour[0] + k * (pour[1] - pour[0]) / n_coins for k, c in enumerate(order)}
    def jar_glass():
        def f(d, s, im):
            d.rounded_rectangle((0, 30 * s, JW * s - 1, JH * s - 1), 46 * s, outline=(255, 255, 255, 90), width=5 * s, fill=(255, 255, 255, 14))
            d.rounded_rectangle((30 * s, 0, (JW - 30) * s, 40 * s), 14 * s, fill=(255, 255, 255, 40))
            d.line((30 * s, 90 * s, 30 * s, (JH - 80) * s), fill=(255, 255, 255, 60), width=8 * s)   # highlight
        return A.sprite(JW, JH, f)
    GL = jar_glass()
    def fn(t):
        im = A.bg(); M.words_rise(im, [TT], W / 2, 330, t, 0.05)
        put(im, BP, W / 2, 500, clamp((t - 0.4) / 0.2), 0.8 + 0.2 * back_out((t - 0.4) / 0.4)); put(im, EX, W / 2, 580, clamp((t - 0.6) / 0.3))
        landed = [0, 0, 0]
        for i in range(n_coins):
            k = (t - TC[i]) / 0.55; j = plan[i]
            if k >= 1: landed[j] += 1; continue
            if k <= 0: continue
            e = cubic_io(k); x0, y0, x1, y1 = W / 2, 520, xs[j], JY - 60
            x = x0 + (x1 - x0) * e; y = y0 + (y1 - y0) * e - 160 * math.sin(math.pi * e)
            e2 = cubic_io(max(0, k - 0.06)); px = x0 + (x1 - x0) * e2; py = y0 + (y1 - y0) * e2 - 160 * math.sin(math.pi * e2)
            M.mb_put(im, coin, x, y, x - px, y - py, clamp(k / 0.1), 1.0 - 0.2 * e, 200 * e)
        tot = [sum(1 for p in plan if p == j) for j in range(3)]
        for j in range(3):
            put(im, GL, xs[j], JY, clamp((t - 0.7 - j * 0.1) / 0.3))
            fill = landed[j] / max(1, n_coins) / max(p[2] for p in parts) * 0.82   # biggest share fills to 82%
            fill_s = fill
            if fill_s > 0:
                h = (JH - 80) * fill_s; x0 = xs[j] - JW / 2 + 10; y1 = JY + JH / 2 - 10
                liq = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(liq)
                wave = [(x0 + u, y1 - h + 6 * math.sin(t * 5 + u / 30 + j)) for u in range(0, JW - 19, 10)] + [(x0 + JW - 20, y1), (x0, y1)]
                ld.polygon(wave, fill=cols[j] + (230,)); im.alpha_composite(liq.filter(ImageFilter.GaussianBlur(1)))
                gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((xs[j] - 140, y1 - h - 60, xs[j] + 140, y1 + 40), fill=cols[j] + (40,))
                im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(40)))
            pct = int(round(parts[j][2] * 100 * landed[j] / max(1, tot[j])))
            put(im, text(f"{pct}%", "bl", 64, WHITE), xs[j], JY - JH / 2 - 10, clamp((t - pour[0]) / 0.3))
            a, b = lab[j]; k = (t - label_at[j]) / 0.4
            if k > 0: put_rise(im, a, xs[j], JY + JH / 2 + 60, quint_out(k)); put_rise(im, b, xs[j], JY + JH / 2 + 110, quint_out(k - 0.2))
        if t >= done_at:
            k = (t - done_at) / 0.35; ring(im, xs[1], JY, k / 1.5, maxr=320, width=5, r0=100)
        return im, 0
    ev = [(0.05, "whoosh", 0.4), (0.4, "pop", 0.7)] + [(TC[i] + 0.55, "coin", 0.18) for i in range(n_coins)] + [(a, "swish", 0.4) for a in label_at] + [(done_at, "shimmer", 0.6)]
    return dur, fn, ev


# ======================================================================= 3. the weekly loop
def scene_loop(dur=4.0, centre=("Every", "week"), nodes=(("New ads tested", "TEST"), ("Winner gets the budget", "SCALE"), ("Weak ads switched off", "CUT")),
               spin=(0.4, 3.3), cols=None):
    """three node cards on a circle; a glowing arc arrow runs round once, and each card lights up as it passes"""
    R_, CX, CY = 330, W / 2, 1000; angs = [-90, 30, 150]
    cols = list(cols or [A.TH["accent"]] * 3)
    def node(a, b, on, c):
        w_, h_ = 400, 150
        def dr(d, s):
            d.text((34 * s, 26 * s), b, font=A.font("bl", 30 * s), fill=c if on else A.TH["muted"])
            d.text((34 * s, 72 * s), a, font=A.font("b", A.fit_size(a, "b", 36, 330) * s), fill=A.TH["ink"] if on else A.TH["muted"])
        return A.card_sprite(w_, h_, dr, radius=30, outline=c if on else None)
    N0 = [node(a, b, False, cols[i]) for i, (a, b) in enumerate(nodes)]; N1 = [node(a, b, True, cols[i]) for i, (a, b) in enumerate(nodes)]
    C1, C2 = text(centre[0], "sb", 44, A.TH["muted"]), text(centre[1], "bl", 96, A.TH["ink"])
    TT = T("Then it repeats.", "xb", 72)
    def fn(t):
        im = A.bg(); M.words_rise(im, [TT], W / 2, 330, t, 0.05)
        p = cubic_io((t - spin[0]) / (spin[1] - spin[0])); a_end = -90 + 360 * p
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.ellipse((CX - R_, CY - R_, CX + R_, CY + R_), outline=(255, 255, 255, 30), width=6)
        if p > 0:
            od.arc((CX - R_, CY - R_, CX + R_, CY + R_), -90, a_end, fill=A.TH["accent"] + (255,), width=10)
            gl = ov.filter(ImageFilter.GaussianBlur(12)); im.alpha_composite(gl)
            ar = math.radians(a_end); hx, hy = CX + R_ * math.cos(ar), CY + R_ * math.sin(ar)
            od.ellipse((hx - 16, hy - 16, hx + 16, hy + 16), fill=A.TH["accent2"] + (255,))
        im.alpha_composite(ov)
        put(im, C1, CX, CY - 50, clamp((t - 0.2) / 0.3)); put(im, C2, CX, CY + 30, clamp((t - 0.3) / 0.3), 0.9 + 0.1 * back_out((t - 0.3) / 0.5))
        for i, ang in enumerate(angs):
            x, y = CX + R_ * math.cos(math.radians(ang)), CY + R_ * math.sin(math.radians(ang))
            reached = (ang - (-90)) % 360 <= 360 * p + 0.5 and p > 0
            k = quint_out((t - 0.2 - i * 0.1) / 0.4)
            if i == 0: y -= 40
            put(im, N1[i] if reached else N0[i], min(max(x, 250), W - 250), y, k, 0.92 + 0.08 * k)
        return im, 0
    hits = [spin[0] + (spin[1] - spin[0]) * f for f in (0.02, 0.36, 0.69)]
    return dur, fn, [(0.05, "whoosh", 0.4), (spin[0], "swish", 0.5)] + [(h, "pop", 0.6) for h in hits] + [(spin[1], "shimmer", 0.5)]
