"""Clean scenes for the clothing '3 questions' Reel, timed to a voiceover: pale sage, deep forest green, one
terracotta. Outlined numbers, skeleton rows, smooth eases, dot animations. No shakes, no stickers.
Meta ads first; email isn't sold here."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, WHITE, clamp, put
import motion as M
from motion import ftext, expo_out, quint_out, cubic_io, back_out

BG, INK, ACC, MUTED, LINE, SOFT = (238, 242, 236), (22, 50, 40), (214, 104, 64), (112, 130, 120), (214, 222, 212), (226, 233, 224)
GREEN = (40, 150, 90)
_BG = None
def bg():
    global _BG
    if _BG is None: _BG = M.flat_bg(BG, grain=1.0)
    return _BG.copy()

def fitT(s, size, col=INK, w="xb", maxw=940):
    while size > 30 and M.ffont(w, size).getlength(s) > maxw: size -= 2
    return ftext(s, w, size, col)

def card(w, h, draw=None, fill=WHITE, r=34, border=None, bw=4):
    def dr(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill, outline=border, width=(bw * s if border else 0))
        if draw: draw(d, s)
    return A.shadowed(A.sprite(w, h, dr), blur=28, dy=14, alpha=22, pad=56)

_on = {}
def outline_num(n, size=220, col=ACC, stroke=4):
    """big outlined number (stroke only), e.g. 01: the stroked mask minus the plain mask"""
    k = (n, size, col)
    if k not in _on:
        f = M.ffont("bl", size * 2); tw = int(f.getlength(n)); hh = int(size * 2.4); sw = stroke * 2
        outer, inner = Image.new("L", (tw + 40, hh), 0), Image.new("L", (tw + 40, hh), 0)
        ImageDraw.Draw(outer).text((20, 10), n, font=f, fill=255, stroke_width=sw, stroke_fill=255); ImageDraw.Draw(inner).text((20, 10), n, font=f, fill=255)
        from PIL import ImageChops
        m = Image.new("RGBA", outer.size, col + (0,)); m.putalpha(ImageChops.subtract(outer, inner))
        _on[k] = m.resize((m.width // 2, m.height // 2), Image.LANCZOS)
    return _on[k]

def num_header(im, t, n, q, q2=None):
    """outlined number draws in (wipe), the question rises under it"""
    N = outline_num(n); M.reveal_lr(im, N, W / 2, 360, expo_out(t / 0.6))
    M.words_rise(im, [fitT(q, 70)], W / 2, 560, t, 0.2)
    if q2: M.words_rise(im, [fitT(q2, 70, ACC)], W / 2, 650, t, 0.35)

def chk(p, col=GREEN, r=64):
    def f(d, s, im):
        d.ellipse((0, 0, r * s, r * s), fill=col); pts = [(0.27, 0.52), (0.44, 0.69), (0.75, 0.34)]; q, q2 = clamp(p * 2), clamp(p * 2 - 1)
        P = [(x * r * s, y * r * s) for x, y in pts]
        d.line((P[0][0], P[0][1], P[0][0] + (P[1][0] - P[0][0]) * q, P[0][1] + (P[1][1] - P[0][1]) * q), fill=WHITE, width=int(r * 0.11 * s))
        if q2 > 0: d.line((P[1][0], P[1][1], P[1][0] + (P[2][0] - P[1][0]) * q2, P[1][1] + (P[2][1] - P[1][1]) * q2), fill=WHITE, width=int(r * 0.11 * s))
    return A.sprite(r, r, f)


# ======================================================================= 1-2. hook: three questions, highlight #3
def _slot(n, hl=False):
    def dr(d, s):
        f = M.ffont("bl", 64 * s); d.text((50 * s, 30 * s), n, font=f, fill=BG, stroke_width=2 * s, stroke_fill=ACC if hl else MUTED)
        d.rounded_rectangle((200 * s, 50 * s, 560 * s, 74 * s), 12 * s, fill=SOFT); d.rounded_rectangle((200 * s, 92 * s, 440 * s, 112 * s), 10 * s, fill=SOFT)
        if hl: d.text((680 * s, 34 * s), "?", font=M.ffont("bl", 80 * s), fill=ACC)
    return card(820, 150, dr, border=ACC if hl else None)

def scene_hook(dur=3.6, l1="3 questions", l2="before you spend another", l3="euro on Meta ads.", slots_at=(1.0, 1.25, 1.5)):
    """the title rises word by word, three skeleton question slots slide up with a soft shimmer"""
    T1 = [ftext("3", "bl", 150, ACC), ftext("questions", "bl", 150, INK)]
    T2, T3 = fitT(l2, 62, INK, "sb"), fitT(l3, 62, INK, "sb"); S = [_slot(f"0{i + 1}") for i in range(3)]
    ys = [1000, 1190, 1380]
    def fn(t):
        im = bg(); M.words_rise(im, T1, W / 2, 440, t, 0.05, stagger=0.12, gap=30)
        M.words_rise(im, [T2], W / 2, 610, t, 0.4); M.words_rise(im, [T3], W / 2, 690, t, 0.5)
        for i, sp in enumerate(S):
            sl = sp
            if t > slots_at[i] + 0.4:   # shimmer sweeping across the skeleton rows
                sl = A.shine(sp, ((t - slots_at[i] - 0.4) % 1.4) / 1.0, width=90, strength=0.35)
            M.slide_put(im, sl, W / 2, ys[i] + 160, W / 2, ys[i], (t - slots_at[i]) / 0.5, expo_out)
        return im, 0
    return dur, fn, [(0.05, "whoosh", 0.4), (0.4, "swish", 0.3)] + [(a, "pop", 0.45) for a in slots_at]

def scene_three(dur=2.4, l1="Most clothing brands", l2="can't answer number 3.", hl_at=0.5):
    """same slots: 01 and 02 dim back, 03 lifts with a terracotta border and a pulsing ?"""
    S = [_slot(f"0{i + 1}") for i in range(3)]; S3 = _slot("03", hl=True); L1, L2 = fitT(l1, 76), fitT(l2, 76, ACC)
    ys = [1000, 1190, 1380]
    def fn(t):
        im = bg(); M.words_rise(im, [L1], W / 2, 520, t, 0.05); M.words_rise(im, [L2], W / 2, 620, t, 0.2)
        k = quint_out((t - hl_at) / 0.5)
        for i in range(2): put(im, S[i], W / 2, ys[i], 1 - 0.6 * k)
        put(im, S3 if k > 0 else S[2], W / 2, ys[2] - 10 * k, 1, 1 + 0.04 * k + 0.008 * math.sin(max(0, t - hl_at - 0.5) * 5))
        return im, 0
    return dur, fn, [(0.05, "swish", 0.3), (hl_at, "pop", 0.6), (hl_at + 0.05, "shimmer", 0.4)]


# ======================================================================= 3. Q1: which ad made the sale?
def scene_q1(dur=4.0, q="Which ad made the sale?", rows=(("Ad 1 · Linen shirt", "1.2k", 0), ("Ad 2 · Heavy hoodie", "310", 14), ("Ad 3 · Straight jeans", "640", 3)),
             track_at=1.9, count=(2.2, 3.1)):
    """an ads table: likes are filled in, sales show '?'. 'Tracking connected' slides in and the sales count up; the
    most-liked ad sells nothing"""
    cw, ch = 920, 520
    def base(d, s):
        d.text((50 * s, 40 * s), "Your ads", font=M.ffont("b", 34 * s), fill=INK)
        for x, lab in ((580, "Likes"), (760, "Sales")): d.text((x * s, 44 * s), lab, font=M.ffont("sb", 28 * s), fill=MUTED)
        for i, (nm, lk, _) in enumerate(rows):
            y = 130 + i * 120; d.line((50 * s, (y - 20) * s, (cw - 50) * s, (y - 20) * s), fill=LINE, width=2 * s)
            d.rounded_rectangle((50 * s, y * s, 120 * s, (y + 70) * s), 14 * s, fill=SOFT); d.text((150 * s, (y + 16) * s), nm, font=M.ffont("sb", 34 * s), fill=INK)
            d.text((580 * s, (y + 14) * s), lk, font=M.ffont("b", 38 * s), fill=INK)
    C = card(cw, ch, base); X0, Y0 = W / 2 - cw / 2 + 56, 1040 - ch / 2 - 56 + 56
    TR = A.sprite(420, 70, lambda d, s, im: (d.rounded_rectangle((0, 0, 420 * s - 1, 70 * s - 1), 35 * s, fill=INK), d.text((70 * s, 16 * s), "Tracking connected", font=M.ffont("b", 30 * s), fill=WHITE),
                                              d.ellipse((24 * s, 24 * s, 46 * s, 46 * s), fill=(110, 220, 150))))
    NOTE = fitT("Most likes. Zero sales.", 52, ACC, "xb"); EX = ftext("example", "m", 24, MUTED)
    def fn(t):
        im = bg(); num_header(im, t, "01", q)
        M.slide_put(im, C, W / 2, 1040 + 200, W / 2, 1040, (t - 0.5) / 0.6, expo_out)
        p = quint_out((t - count[0]) / (count[1] - count[0]))
        for i, (_, _, sales) in enumerate(rows):
            y = Y0 + 130 + i * 120 + 35
            if t < count[0]: put(im, ftext("?", "bl", 44, MUTED), X0 + 790, y, clamp((t - 0.9) / 0.3))
            else:
                v = int(round(sales * p)); put(im, ftext(str(v), "bl", 44, ACC if (i == 0 and p > 0.9) else (GREEN if sales else INK)), X0 + 790, y)
        if t >= track_at: M.slide_put(im, TR, W / 2, 1400, W / 2, 1360, (t - track_at) / 0.4, expo_out)
        if t >= count[1]: M.words_rise(im, [NOTE], W / 2, 1460, t, count[1])
        put(im, EX, W / 2 + 380, 1040 + ch / 2 - 20, clamp((t - 1.0) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4), (0.5, "whoosh", 0.4), (track_at, "pop", 0.6)] + [(count[0] + 0.15 * i, "tick", 0.3) for i in range(6)] + [(count[1], "hit", 0.5)]


# ======================================================================= 4. Q2: new buyers or the same people?
def scene_q2(dur=4.0, q="Who's actually seeing your ads?", q2="New buyers, or the same people?", shift=(1.9, 3.0)):
    """a field of people dots: the left cluster have already bought (filled), the right are new (outlined). A soft
    'your ad' highlight sits on the left cluster, then eases across to the new people, who fill terracotta as it covers them"""
    cols, rows_, gap = 10, 6, 84; X0 = W / 2 - (cols - 1) * gap / 2; Y0 = 900
    pts = [(X0 + c * gap, Y0 + r * gap, c < 5) for r in range(rows_) for c in range(cols)]
    lx, rx = X0 + 2 * gap, X0 + 7 * gap
    LG1, LG2 = ftext("already bought", "sb", 30, INK), ftext("new people", "sb", 30, INK); AD = ftext("Your ads", "b", 30, ACC)
    def fn(t):
        im = bg(); num_header(im, t, "02", q, q2)
        a = clamp((t - 0.6) / 0.4); p = cubic_io((t - shift[0]) / (shift[1] - shift[0])); hx = lx + (rx - lx) * p
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rounded_rectangle((hx - 2.45 * gap, Y0 - 0.8 * gap, hx + 2.45 * gap, Y0 + (rows_ - 0.2) * gap), 50, fill=ACC + (int(38 * a),), outline=ACC + (int(200 * a),), width=4)
        im.alpha_composite(ov); d = ImageDraw.Draw(im)
        for i, (x, y, bought) in enumerate(pts):
            k = clamp((t - 0.5 - i * 0.008) / 0.3)
            if k <= 0: continue
            r = 22 * quint_out(k); covered = abs(x - hx) < 2.5 * gap and not bought and p > 0.05
            if bought: d.ellipse((x - r, y - r, x + r, y + r), fill=(150, 165, 155))
            elif covered: d.ellipse((x - r, y - r, x + r, y + r), fill=ACC)
            else: d.ellipse((x - r, y - r, x + r, y + r), outline=INK, width=4)
        put(im, AD, hx, Y0 - 0.8 * gap - 30, a)
        ly = Y0 + rows_ * gap + 40; la = clamp((t - 1.0) / 0.3)
        d.ellipse((W / 2 - 330, ly - 14, W / 2 - 302, ly + 14), fill=(150, 165, 155)); put(im, LG1, W / 2 - 290 + LG1.width / 2, ly, la)
        d.ellipse((W / 2 + 60, ly - 14, W / 2 + 88, ly + 14), outline=INK, width=4); put(im, LG2, W / 2 + 100 + LG2.width / 2, ly, la)
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4), (0.5, "pop", 0.4), (shift[0], "whoosh", 0.5), (shift[1], "coin", 0.5)]


# ======================================================================= 5. Q3: click, don't buy
def scene_q3(dur=4.8, q="What happens to people", q2="who click and don't buy?", flow=(0.7, 2.4), nothing_at=3.0, n=14):
    """dots stream from the ad into the store; one goes on to checkout, the rest drift down into 'left' and grey
    out. Then 'For most brands: nothing.'"""
    BX = [(200, 1000, "Ad"), (540, 1000, "Store"), (880, 1000, "Checkout")]
    def box(lab):
        return card(220, 110, lambda d, s: d.text(((220 * s - d.textlength(lab, font=M.ffont("b", 38 * s))) / 2, 30 * s), lab, font=M.ffont("b", 38 * s), fill=INK), r=55)
    boxes = [box(lab) for _, _, lab in BX]
    LEFT = ftext("Left the site", "sb", 32, MUTED); NO1, NO2 = fitT("For most brands…", 60, INK, "sb"), fitT("nothing happens.", 84, ACC, "bl")
    import random
    rng = random.Random(4); drift = [(rng.uniform(-200, 200), rng.uniform(0, 80)) for _ in range(n)]
    def fn(t):
        im = bg(); num_header(im, t, "03", q, q2); d = ImageDraw.Draw(im)
        d.line((BX[0][0] + 110, 1000, BX[1][0] - 110, 1000), fill=LINE, width=4); d.line((BX[1][0] + 110, 1000, BX[2][0] - 110, 1000), fill=LINE, width=4)
        for i in range(n):
            t0 = flow[0] + i * (flow[1] - flow[0]) / n; k = (t - t0) / 0.6
            if k <= 0: continue
            if k < 1: x = BX[0][0] + (BX[1][0] - BX[0][0]) * cubic_io(k); y = 1000; col = ACC
            else:
                k2 = (t - t0 - 0.6) / 0.8
                if i == n // 2: x = BX[1][0] + (BX[2][0] - BX[1][0]) * cubic_io(k2); y = 1000; col = GREEN
                else:
                    e = quint_out(k2); x = BX[1][0] + drift[i][0] * e; y = 1000 + (230 + drift[i][1]) * e
                    g = clamp(k2); col = tuple(int(ACC[j] * (1 - g) + 180 * g) for j in range(3))
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=col)
        for (x, y, _), sp in zip(BX, boxes): put(im, sp, x, y, clamp((t - 0.4) / 0.3))   # boxes on top: dots go in and out of them
        put(im, LEFT, BX[1][0], 1370, clamp((t - 1.6) / 0.3)); put(im, ftext("example", "m", 24, MUTED), BX[2][0], 1080, clamp((t - 1.6) / 0.3))
        M.words_rise(im, [NO1], W / 2, 1500, t, nothing_at); M.words_rise(im, [NO2], W / 2, 1590, t, nothing_at + 0.35)
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4), (0.4, "pop", 0.4), (flow[0], "whoosh", 0.3)] + [(flow[0] + 0.6 + (flow[1] - flow[0]) / 2, "ping", 0.5), (nothing_at + 0.35, "hit", 0.5)]


# ======================================================================= 6. the fix
def scene_fix(dur=5.0, title="That's what we fix.", rows=(("01", "Every sale tracked to the ad", "so you know what's working"), ("02", "Every audience tested", "new buyers, not the same faces"),
              ("03", "Everyone who left, reminded", "ads that bring them back")), at=(1.0, 1.9, 2.8)):
    """the three numbers come back as answered rows: outlined number, title, sub, then a green check draws on the right"""
    TT = fitT(title, 96, INK, "bl"); cw, ch = 920, 210
    def rowc(n, a, b):
        def dr(d, s):
            d.text((44 * s, 52 * s), n, font=M.ffont("bl", 70 * s), fill=WHITE, stroke_width=2 * s, stroke_fill=ACC)
            d.text((200 * s, 50 * s), a, font=M.ffont("b", 42 * s), fill=INK); d.text((200 * s, 112 * s), b, font=M.ffont("m", 32 * s), fill=MUTED)
        return card(cw, ch, dr)
    R = [rowc(*r) for r in rows]; ys = [820, 1080, 1340]
    def fn(t):
        im = bg(); M.words_rise(im, [TT], W / 2, 520, t, 0.1); d = ImageDraw.Draw(im); p = quint_out((t - 0.5) / 0.4)
        if p > 0: d.rounded_rectangle((W / 2 - 70 * p, 600, W / 2 + 70 * p, 612), 6, fill=ACC)
        for i, sp in enumerate(R):
            M.slide_put(im, sp, W / 2 + 300, ys[i], W / 2, ys[i], (t - at[i]) / 0.5, expo_out)
            k = (t - at[i] - 0.35) / 0.45
            if k > 0: put(im, chk(quint_out(k)), W / 2 + cw / 2 - 90, ys[i], clamp(k / 0.2))
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.4)] + [(a, "swish", 0.5) for a in at] + [(a + 0.45, "tick", 0.6) for a in at]


# ======================================================================= 7. the offer
def scene_offer(dur=4.4, badge="FREE AD REVIEW", big="15 minutes.", lines=("We look at your Meta ads with you", "and answer all three questions", "for your brand."),
                foot="Southline Agency · Meta ads for clothing brands", chips_at=(1.6, 1.85, 2.1)):
    cw, ch = 920, 860
    def dr(d, s):
        f = M.ffont("bl", 30 * s); bw = d.textlength(badge, font=f) + 60 * s
        d.rounded_rectangle((60 * s, 60 * s, 60 * s + bw, 120 * s), 30 * s, fill=ACC); d.text((90 * s, 72 * s), badge, font=f, fill=WHITE)
        d.text((60 * s, 160 * s), big, font=M.ffont("bl", 110 * s), fill=INK)
        for i, l in enumerate(lines): d.text((60 * s, (320 + i * 56) * s), l, font=M.ffont("m", 42 * s), fill=INK)
        d.line((60 * s, 680 * s, (cw - 60) * s, 680 * s), fill=LINE, width=2 * s); d.text((60 * s, 720 * s), foot, font=M.ffont("sb", 30 * s), fill=MUTED)
    C = card(cw, ch, dr, r=44)
    def chip(n, done):
        def f(d, s, im):
            d.rounded_rectangle((0, 0, 170 * s - 1, 84 * s - 1), 42 * s, fill=GREEN if done else SOFT)
            d.text((34 * s, 16 * s), n, font=M.ffont("bl", 44 * s), fill=WHITE if done else MUTED)
            if done: d.line((112 * s, 44 * s, 124 * s, 56 * s, 144 * s, 30 * s), fill=WHITE, width=6 * s, joint="curve")
        return A.sprite(170, 84, f)
    CH = [(chip(f"0{i + 1}", False), chip(f"0{i + 1}", True)) for i in range(3)]
    def fn(t):
        im = bg(); k = (t - 0.1) / 0.7; M.slide_put(im, C, W / 2, 960 + 500, W / 2, 900, k, expo_out)
        top = 900 - ch / 2
        for i, (a, b) in enumerate(CH):
            x = W / 2 - cw / 2 + 60 + 85 + i * 200; y = top + 560
            put(im, b if t >= chips_at[i] else a, x, y, clamp((t - 0.9) / 0.3), 1 + 0.1 * (1 - quint_out((t - chips_at[i]) / 0.3)) if t >= chips_at[i] else 1)
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.6)] + [(a, "tick", 0.6) for a in chips_at] + [(chips_at[-1] + 0.05, "coin", 0.5)]


# ======================================================================= 8. CTA
def scene_cta(dur=3.0, kw="REVIEW", sub="and I'll send you the link.", kw_at=0.3):
    CM = ftext("Comment", "bl", 96, INK); kt = ftext(kw, "bl", 90, WHITE); pw, ph = kt.width + 90, 150
    KP = A.shadowed(A.sprite(pw, ph, lambda d, s, im: d.rounded_rectangle((0, 0, pw * s - 1, ph * s - 1), ph // 2 * s, fill=ACC)), blur=24, dy=12, alpha=40, pad=40)
    KP.alpha_composite(kt, (40 + 45, 40 + (ph - kt.height) // 2)); SB = fitT(sub, 60, INK, "sb"); lg = A.logo().resize((130, 130), Image.LANCZOS)
    def fn(t):
        im = bg(); k = (t - kw_at) / 0.5; tot = CM.width + 24 + KP.width - 80
        M.words_rise(im, [CM], W / 2 - tot / 2 + CM.width / 2, 820, t, 0.05)
        if k > 0: put(im, KP, W / 2 + tot / 2 - (KP.width - 80) / 2, 820, clamp(k / 0.3), 0.85 + 0.15 * back_out(k) + 0.012 * math.sin(max(0, t - kw_at - 0.6) * 4))
        M.words_rise(im, [SB], W / 2, 980, t, kw_at + 0.35)
        put(im, lg, W / 2, 1250, clamp((t - 1.0) / 0.3), 0.9 + 0.1 * back_out((t - 1.0) / 0.5)); put(im, ftext("Southline Agency", "b", 34, INK), W / 2, 1360, clamp((t - 1.1) / 0.3))
        return im, 0
    return dur, fn, [(0.05, "whoosh", 0.4), (kw_at, "pop", 0.8), (kw_at + 0.05, "ping", 0.4), (1.0, "coin", 0.4)]
