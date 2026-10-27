"""Clean, simple scenes for the clothing 'Why does one sell?' Reel: off-white, navy, one gold, soft shadows, lots of
space. Motion is smooth only: expo/quint eases, motion blur on slides, words rising from masks, bars easing.
No shakes, no stickers. Sells Meta ads; email appears only as the add-on."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, WHITE, clamp, put, ring
import motion as M
from motion import ftext, expo_out, quint_out, cubic_io, back_out
from ecom3_scenes import garment

BG, NAVY, GOLD, MUTED, LINE, GREEN = (249, 249, 247), (16, 30, 58), (201, 160, 72), (122, 130, 146), (226, 229, 235), (30, 158, 92)
_BG = None
def bg():
    global _BG
    if _BG is None: _BG = M.flat_bg(BG, grain=1.0)
    return _BG.copy()

def T(s, size, col=NAVY, w="xb"): return ftext(s, w, size, col)
def fitT(s, size, col=NAVY, w="xb", maxw=960):
    while size > 30 and M.ffont(w, size).getlength(s) > maxw: size -= 2
    return T(s, size, col, w)

def card(w, h, draw=None, fill=WHITE, r=36, border=None):
    def dr(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill, outline=border, width=(4 * s if border else 0))
        if draw: draw(d, s)
    return A.shadowed(A.sprite(w, h, dr), blur=30, dy=16, alpha=28, pad=60)

def tile(kind, col, label, w=200, h=250, border=None):
    """an ad thumbnail: garment on a soft swatch with an angle label underneath"""
    def dr(d, s):
        d.rounded_rectangle((16 * s, 16 * s, (w - 16) * s, (h - 70) * s), 22 * s, fill=(240, 238, 232)); garment(d, s, w / 2 * s, (h - 70) / 2 * s + 8 * s, kind, col, (240, 238, 232))
        f = M.ffont("sb", 28 * s); tw = d.textlength(label, font=f); d.text(((w * s - tw) / 2, (h - 56) * s), label, font=f, fill=NAVY)
    return card(w, h, dr, r=28, border=border)

def header(im, t, n, title, total=4):
    """STEP n OF 4, a 4-segment progress bar that fills, and the step title rising"""
    d = ImageDraw.Draw(im); x0, x1, y = 120, W - 120, 250; seg = (x1 - x0 - 3 * 16) / total
    for i in range(total):
        sx = x0 + i * (seg + 16); d.rounded_rectangle((sx, y, sx + seg, y + 10), 5, fill=LINE)
        f = 1 if i < n - 1 else (quint_out(t / 0.5) if i == n - 1 else 0)
        if f > 0: d.rounded_rectangle((sx, y, sx + seg * f, y + 10), 5, fill=GOLD)
    put(im, ftext(f"STEP {n} OF {total}", "b", 28, GOLD, track=4), W / 2, 320, clamp(t / 0.3))
    M.words_rise(im, [fitT(title, 76)], W / 2, 420, t, 0.1)


# ======================================================================= 1. hook: two brands, same budget
def scene_split(dur=5.2, t1="Two clothing brands.", t2="Same ad budget.", q1="So why does one sell…", q2="…and the other doesn't?",
                orders=(1.7, 2.05, 2.35, 2.7, 3.0), q_at=3.4):
    """two cards slide up side by side; brand B's order counter ticks up with soft pings, brand A sits on 0;
    then the question rises underneath"""
    cw, ch = 430, 560
    def face(name, d, s):
        d.rounded_rectangle((36 * s, 36 * s, 210 * s, 84 * s), 24 * s, fill=(236, 239, 245)); d.text((58 * s, 44 * s), name, font=M.ffont("b", 28 * s), fill=NAVY)
        d.text((36 * s, 130 * s), "Ad spend", font=M.ffont("m", 30 * s), fill=MUTED); d.text((36 * s, 172 * s), "€20/day", font=M.ffont("xb", 60 * s), fill=NAVY)
        d.line((36 * s, 280 * s, (cw - 36) * s, 280 * s), fill=LINE, width=3 * s); d.text((36 * s, 310 * s), "Orders this week", font=M.ffont("m", 30 * s), fill=MUTED)
    CA, CB = card(cw, ch, lambda d, s: face("Brand A", d, s)), card(cw, ch, lambda d, s: face("Brand B", d, s))
    L1, L2 = fitT(t1, 84), fitT(t2, 84, GOLD); Q1, Q2 = fitT(q1, 70), fitT(q2, 70, GOLD); EX = ftext("example", "m", 24, MUTED)
    plus = ftext("+1 order", "b", 30, GREEN)
    XA, XB, Y = W / 2 - 240, W / 2 + 240, 1010
    def fn(t):
        im = bg()
        M.words_rise(im, [L1], W / 2, 400, t, 0.1); M.words_rise(im, [L2], W / 2, 500, t, 0.3)
        for x, C, t0 in ((XA, CA, 0.6), (XB, CB, 0.72)): M.slide_put(im, C, x, Y + 700, x, Y, (t - t0) / 0.6, expo_out)
        n = sum(1 for o in orders if t >= o)
        if t >= 0.9:
            put(im, T("0", 110, (190, 196, 206), "bl"), XA - cw / 2 + 36 + 40, Y - ch / 2 + 440, clamp((t - 0.9) / 0.2))
            k = (t - orders[n - 1]) / 0.25 if n else 1
            put(im, T(str(n), 110, GREEN if n else (190, 196, 206), "bl"), XB - cw / 2 + 36 + (40 if n < 10 else 66), Y - ch / 2 + 440, clamp((t - 0.9) / 0.2), 1 + 0.12 * (1 - quint_out(k)))
        for o in orders:
            k = (t - o) / 0.6
            if 0 < k < 1: put(im, plus, XB + 80, Y + 150 - 90 * quint_out(k), 1 - k ** 2)
        put(im, EX, W / 2, Y + ch / 2 + 10, clamp((t - 1.2) / 0.3))
        M.words_rise(im, [Q1], W / 2, 1460, t, q_at); M.words_rise(im, [Q2], W / 2, 1550, t, q_at + 0.4)
        return im, 0
    ev = [(0.1, "whoosh", 0.4), (0.6, "swish", 0.4)] + [(o, "ping", 0.45) for o in orders] + [(q_at, "whoosh", 0.4), (q_at + 0.4, "pop", 0.5)]
    return dur, fn, ev


# ======================================================================= 2. the turn
def scene_turn(dur=2.8, l1="It's not the product.", l2="It's the system", l3="behind the ads."):
    L1, L2, L3 = fitT(l1, 70, MUTED, "sb"), fitT(l2, 104, NAVY, "bl"), fitT(l3, 104, NAVY, "bl")
    def fn(t):
        im = bg(); M.words_rise(im, [L1], W / 2, 760, t, 0.1); M.words_rise(im, [L2], W / 2, 920, t, 0.6); M.words_rise(im, [L3], W / 2, 1040, t, 0.75)
        d = ImageDraw.Draw(im); p = quint_out((t - 1.15) / 0.5)
        if p > 0: d.rounded_rectangle((W / 2 - L3.width / 2, 1110, W / 2 - L3.width / 2 + L3.width * p, 1124), 7, fill=GOLD)
        return im, 0
    return dur, fn, [(0.1, "swish", 0.3), (0.6, "whoosh", 0.5), (1.15, "shimmer", 0.4)]


ADS = (("tee", (40, 46, 60), "Lifestyle"), ("hoodie", (190, 70, 60), "Close-up"), ("jeans", (50, 80, 130), "Review"), ("tee", (90, 120, 80), "Offer"))


# ======================================================================= 3a. several ads, not one
def scene_step_ads(dur=3.4, title="Launch several ads, not one.", sub="Different angles. Same product.", fan_at=1.0):
    """one ad tile sits in the centre, then fans out into four different angles with motion blur"""
    TL = [tile(*a) for a in ADS]; SB = ftext(sub, "m", 40, MUTED)
    xs = [W / 2 - 345, W / 2 - 115, W / 2 + 115, W / 2 + 345]; Y = 1000
    def fn(t):
        im = bg(); header(im, t, 1, title); M.words_rise(im, [SB], W / 2, 510, t, 0.3)
        p = (t - fan_at) / 0.6
        for i in (1, 2, 3, 0):
            if p <= 0:
                if i == 0: put(im, TL[0], W / 2, Y, clamp((t - 0.4) / 0.3), 0.9 + 0.1 * back_out((t - 0.4) / 0.5))
                continue
            M.slide_put(im, TL[i], W / 2, Y, xs[i], Y, p, expo_out, alpha=1.0 if i == 0 else clamp(p / 0.2))
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4), (0.4, "pop", 0.5), (fan_at, "whoosh", 0.6)] + [(fan_at + 0.05 * i, "tick", 0.4) for i in range(4)]


# ======================================================================= 3b. the data picks the winner
def scene_step_test(dur=3.6, title="Let real buyers pick the winner.", sub="Meta shows each ad. Sales decide.", scores=(0.35, 1.0, 0.5, 0.28), race=(0.6, 2.2), win_at=2.3):
    TL = [tile(*a) for a in ADS]; TW = tile(*ADS[1], border=GOLD); SB = ftext(sub, "m", 40, MUTED)
    win = max(range(4), key=lambda i: scores[i]); WP = ftext("Winner", "b", 30, WHITE)
    xs = [W / 2 - 345, W / 2 - 115, W / 2 + 115, W / 2 + 345]; Y = 820; BY, BH = 1420, 380
    def fn(t):
        im = bg(); header(im, t, 2, title); M.words_rise(im, [SB], W / 2, 510, t, 0.3); d = ImageDraw.Draw(im)
        p = cubic_io((t - race[0]) / (race[1] - race[0])); done = quint_out((t - win_at) / 0.4)
        for i in range(4):
            fade = 1 - 0.6 * done if i != win else 1
            put(im, TW if (i == win and done > 0) else TL[i], xs[i], Y, fade)
            h = BH * scores[i] * p
            col = tuple(int(c * fade + 249 * (1 - fade)) for c in (GOLD if i == win and done > 0 else NAVY))
            if h > 2: d.rounded_rectangle((xs[i] - 50, BY - h, xs[i] + 50, BY), 14, fill=col)
        d.line((W / 2 - 440, BY + 4, W / 2 + 440, BY + 4), fill=LINE, width=4)
        if done > 0:
            pw = WP.width + 50; x = xs[win]; y = Y - 170
            pl = A.sprite(pw, 64, lambda d_, s, im_: d_.rounded_rectangle((0, 0, pw * s - 1, 64 * s - 1), 32 * s, fill=GOLD)); pl.alpha_composite(WP, (25, 14))
            put(im, pl, x, y + 20 * (1 - done), done)
        put(im, ftext("sales per ad · example", "m", 26, MUTED), W / 2, BY + 50, clamp((t - 0.8) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4), (race[0], "swish", 0.3)] + [(race[0] + 0.25 * i, "tick", 0.25) for i in range(6)] + [(win_at, "coin", 0.7), (win_at + 0.05, "shimmer", 0.5)]


# ======================================================================= 3c. budget follows the winner
def scene_step_budget(dur=3.4, title="Move the budget to what sells.", sub="The rest switch off.", shift=(0.9, 2.2)):
    """one rounded budget bar split four ways eases into the winner taking most of it"""
    SB = ftext(sub, "m", 40, MUTED); names = [a[2] for a in ADS]
    before, after = (0.25, 0.25, 0.25, 0.25), (0.07, 0.79, 0.07, 0.07)
    cols = [(178, 186, 202), GOLD, (150, 160, 180), (204, 210, 222)]
    X0, X1, Y, BH = 120, W - 120, 1000, 130
    def fn(t):
        im = bg(); header(im, t, 3, title); M.words_rise(im, [SB], W / 2, 510, t, 0.3); d = ImageDraw.Draw(im)
        p = cubic_io((t - shift[0]) / (shift[1] - shift[0])); a = clamp((t - 0.4) / 0.3)
        put(im, ftext("Your daily ad budget", "sb", 34, NAVY), W / 2, Y - 130, a)
        x = X0; mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rounded_rectangle((X0, Y - BH / 2, X1, Y + BH / 2), BH / 2, fill=int(255 * a))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
        for i in range(4):
            wdt = (X1 - X0) * (before[i] + (after[i] - before[i]) * p); ld.rectangle((x, Y - BH / 2, x + wdt, Y + BH / 2), fill=cols[i] if (i == 1 or p < 0.5) else (222, 225, 232))
            if i < 3: ld.rectangle((x + wdt - 2, Y - BH / 2, x + wdt + 2, Y + BH / 2), fill=WHITE)
            lab = ftext(names[i], "sb", 30, NAVY if (i == 1 or p < 0.6) else MUTED); cx = x + wdt / 2
            if wdt > lab.width + 20: layer.alpha_composite(lab, (int(cx - lab.width / 2), int(Y - lab.height / 2)))
            x += wdt
        layer.putalpha(Image.fromarray((A.np.asarray(layer.split()[3], A.np.float32) * A.np.asarray(mask, A.np.float32) / 255).astype(A.np.uint8))); im.alpha_composite(layer)
        if p > 0.95:
            k = quint_out((t - shift[1]) / 0.4); put(im, ftext("Most of your budget on the ad that sells", "sb", 36, GOLD), W / 2, Y + 150 + 20 * (1 - k), k)
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4), (0.4, "pop", 0.4), (shift[0], "whoosh", 0.5), (shift[1], "coin", 0.6)]


# ======================================================================= 3d. remind anyone who looked
def scene_step_retarget(dur=3.6, title="Remind anyone who looked.", sub="Most people don't buy on the first visit.", at=(0.7, 1.5, 2.3)):
    """three cards stack down a connector that draws itself: viewed → reminder ad → order placed"""
    SB = ftext(sub, "m", 38, MUTED); cw, ch = 760, 170
    def row(icon_col, a, b, tick=False):
        def dr(d, s):
            d.ellipse((40 * s, 45 * s, 120 * s, 125 * s), fill=icon_col)
            if tick: d.line((60 * s, 86 * s, 76 * s, 102 * s, 102 * s, 70 * s), fill=WHITE, width=8 * s, joint="curve")
            d.text((150 * s, 40 * s), a, font=M.ffont("b", 40 * s), fill=NAVY); d.text((150 * s, 98 * s), b, font=M.ffont("m", 30 * s), fill=MUTED)
        return card(cw, ch, dr, r=30)
    R = [row((206, 212, 224), "Viewed: Heavy hoodie", "Left without buying"), row(GOLD, "Sees your ad again", "\"Still thinking about it?\""), row(GREEN, "Order placed", "Heavy hoodie · €68", True)]
    ys = [760, 1030, 1300]
    def fn(t):
        im = bg(); header(im, t, 4, title); M.words_rise(im, [SB], W / 2, 510, t, 0.3); d = ImageDraw.Draw(im)
        for i in range(1, 3):
            p = quint_out((t - at[i] + 0.35) / 0.35)
            if p > 0: d.line((W / 2, ys[i - 1] + ch / 2 - 10, W / 2, ys[i - 1] + ch / 2 - 10 + (ys[i] - ys[i - 1] - ch + 20) * p), fill=LINE, width=6)
        for i, sp in enumerate(R): M.slide_put(im, sp, W / 2, ys[i] + 120, W / 2, ys[i], (t - at[i]) / 0.5, expo_out)
        return im, 0
    return dur, fn, [(0.0, "swish", 0.4)] + [(a, "pop", 0.5) for a in at] + [(at[-1] + 0.1, "coin", 0.7)]


# ======================================================================= 4. payoff: back to the two brands
def scene_payoff(dur=3.2, a=("Brand A", "One ad. Hope."), b=("Brand B", "A system."), line="That's the system we run for you."):
    cw, ch = 430, 300
    def face(nm, txt, good, d, s):
        d.text((40 * s, 40 * s), nm, font=M.ffont("b", 30 * s), fill=MUTED); d.text((40 * s, 110 * s), txt, font=M.ffont("xb", 54 * s), fill=GREEN if good else (170, 176, 188))
    CA, CB = card(cw, ch, lambda d, s: face(*a, False, d, s)), card(cw, ch, lambda d, s: face(*b, True, d, s), border=GOLD)
    LN = fitT(line, 66); XA, XB, Y = W / 2 - 240, W / 2 + 240, 880
    def fn(t):
        im = bg(); M.slide_put(im, CA, -400, Y, XA, Y, (t - 0.1) / 0.5, expo_out); M.slide_put(im, CB, W + 400, Y, XB, Y, (t - 0.2) / 0.5, expo_out)
        M.words_rise(im, [LN], W / 2, 1220, t, 1.2); d = ImageDraw.Draw(im); p = quint_out((t - 1.6) / 0.5)
        if p > 0: d.rounded_rectangle((W / 2 - 60 * p, 1290, W / 2 + 60 * p, 1300), 5, fill=GOLD)
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.4), (0.2, "whoosh", 0.4), (1.2, "pop", 0.5)]


# ======================================================================= 5. the offer
def scene_offer(dur=4.6, rows=(("We build and test your ads", "several angles, real data"), ("We move budget to what sells", "and retarget anyone who looked"),
                ("No retainer", "you pay per new subscriber we bring in"), ("Your ad account", "your budget, you see every number")),
                addon="Email marketing: optional add-on", at=(1.0, 1.4, 1.8, 2.2)):
    """a clean white offer card rises; each row's check draws in; the add-on line fades in last"""
    cw, ch = 920, 1120
    def dr(d, s):
        d.text((60 * s, 60 * s), "SOUTHLINE AGENCY", font=M.ffont("b", 28 * s), fill=GOLD)
        d.text((60 * s, 110 * s), "Meta ads for", font=M.ffont("bl", 76 * s), fill=NAVY); d.text((60 * s, 200 * s), "clothing brands.", font=M.ffont("bl", 76 * s), fill=NAVY)
        d.line((60 * s, 320 * s, (cw - 60) * s, 320 * s), fill=LINE, width=3 * s)
    C = card(cw, ch, dr, r=44)
    R = [(ftext(a_, "b", 44, NAVY), ftext(b_, "m", 32, MUTED)) for a_, b_ in rows]; AD = ftext(addon, "m", 30, MUTED)
    def chk(p):
        def f(d, s, im):
            d.ellipse((0, 0, 64 * s, 64 * s), fill=GOLD)
            pts = [(17, 33), (28, 44), (48, 22)]; q = clamp(p * 2); r = clamp(p * 2 - 1)
            d.line((pts[0][0] * s, pts[0][1] * s, (pts[0][0] + (pts[1][0] - pts[0][0]) * q) * s, (pts[0][1] + (pts[1][1] - pts[0][1]) * q) * s), fill=WHITE, width=7 * s)
            if r > 0: d.line((pts[1][0] * s, pts[1][1] * s, (pts[1][0] + (pts[2][0] - pts[1][0]) * r) * s, (pts[1][1] + (pts[2][1] - pts[1][1]) * r) * s), fill=WHITE, width=7 * s)
        return A.sprite(64, 64, f)
    def fn(t):
        im = bg(); k = expo_out((t - 0.1) / 0.7); cy = 960 + 600 * (1 - k)
        M.mb_put(im, C, W / 2, cy, 0, -600 * (expo_out((t - 0.1) / 0.7) - expo_out((t - 0.14) / 0.7)), clamp((t - 0.1) / 0.15))
        top = cy - ch / 2
        for i, (a_, b_) in enumerate(R):
            p = (t - at[i]) / 0.4
            if p <= 0: continue
            y = top + 450 + i * 160
            put(im, chk(quint_out(p)), W / 2 - cw / 2 + 100, y, clamp(p / 0.2))
            put(im, a_, W / 2 - cw / 2 + 160 + a_.width / 2 + 20 * (1 - quint_out(p)), y - 20, clamp(p / 0.3)); put(im, b_, W / 2 - cw / 2 + 160 + b_.width / 2 + 20 * (1 - quint_out(p)), y + 30, clamp((p - 0.15) / 0.3))
        put(im, AD, W / 2, top + ch - 90, clamp((t - at[-1] - 0.5) / 0.4))
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.6)] + [(a_, "tick", 0.55) for a_ in at] + [(at[-1] + 0.5, "shimmer", 0.4)]


# ======================================================================= 6. CTA
def scene_cta(dur=4.0, l1="Want this system", l2="for your brand?", kw="SYSTEM", sub="Comment it, or DM me SYSTEM.", sub2="I'll send you the full breakdown.", kw_at=1.0):
    L1, L2 = fitT(l1, 92), fitT(l2, 92, GOLD); CM = T("Comment", 84, NAVY, "bl")
    kt = ftext(kw, "bl", 84, WHITE); pw, ph = kt.width + 80, 140
    KP = A.shadowed(A.sprite(pw, ph, lambda d, s, im: d.rounded_rectangle((0, 0, pw * s - 1, ph * s - 1), ph // 2 * s, fill=NAVY)), blur=24, dy=12, alpha=40, pad=40)
    KP.alpha_composite(kt, (40 + 40, 40 + (ph - kt.height) // 2))
    S1, S2 = ftext(sub, "m", 40, MUTED), ftext(sub2, "m", 40, MUTED); lg = A.logo().resize((120, 120), Image.LANCZOS)
    def fn(t):
        im = bg(); M.words_rise(im, [L1], W / 2, 520, t, 0.1); M.words_rise(im, [L2], W / 2, 630, t, 0.3)
        k = (t - kw_at) / 0.5; tot = CM.width + 20 + KP.width - 80
        if k > 0:
            put(im, CM, W / 2 - tot / 2 + CM.width / 2, 900, clamp(k / 0.3))
            put(im, KP, W / 2 + tot / 2 - (KP.width - 80) / 2, 900, clamp(k / 0.3), 0.85 + 0.15 * back_out(k) + 0.015 * math.sin(max(0, t - kw_at - 0.6) * 4))
        M.words_rise(im, [S1], W / 2, 1100, t, kw_at + 0.5); M.words_rise(im, [S2], W / 2, 1160, t, kw_at + 0.6)
        put(im, lg, W / 2, 1400, clamp((t - kw_at - 1.0) / 0.3), 0.9 + 0.1 * back_out((t - kw_at - 1.0) / 0.5))
        put(im, ftext("Southline Agency", "b", 34, NAVY), W / 2, 1500, clamp((t - kw_at - 1.1) / 0.3))
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.4), (kw_at, "pop", 0.8), (kw_at + 0.05, "ping", 0.4), (kw_at + 1.0, "coin", 0.4)]
