"""Editorial / fashion-magazine scenes for the clothing 'Repeat Issue' Reel: cream paper, Playfair serif, black ink,
one red. Motion is calm and precise: rules draw, words rise from masks, pages slide with motion blur, ink writes."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, clamp, put, ring
import motion as M
from motion import ftext, expo_out, quint_out, cubic_io, back_out

PAPER, INK, RED, MUTED, RULE = (244, 239, 230), (22, 20, 18), (196, 38, 30), (128, 120, 108), (200, 192, 178)
_BG = None
def paper():
    global _BG
    if _BG is None: _BG = M.flat_bg(PAPER, grain=1.6)
    return _BG.copy()

def rule(d, x0, y, x1, p, col=INK, w=3):
    """a hairline that draws from the left"""
    if p > 0: d.line((x0, y, x0 + (x1 - x0) * quint_out(p), y), fill=col, width=w)

MAST = ["THE AD ISSUE", "Nº 01 · FOR CLOTHING BRANDS"]   # masthead text, set per video
def masthead(im, t, label=None, issue=None):
    label, issue = label or MAST[0], issue or MAST[1]; d = ImageDraw.Draw(im); rule(d, 80, 230, W - 80, t / 0.6); rule(d, 80, 238, W - 80, (t - 0.08) / 0.6, w=1)
    a = ftext(label, "b", 30, INK, track=6); b = ftext(issue, "m", 24, MUTED, track=3)
    M.reveal_lr(im, a, 80 + a.width / 2, 200, (t - 0.2) / 0.5); M.reveal_lr(im, b, W - 80 - b.width / 2, 200, (t - 0.3) / 0.5)


# ======================================================================= 1. hook
def scene_hook(dur=4.6, l1=("You", "paid", "€38"), l2=("to", "meet", "her."), l3=("Then", "you", "never"), l4=("wrote", "back."),
               note="example: cost to win one new customer with ads", at=(0.35, 0.75, 1.9, 2.25), note_at=1.25):
    """serif headline built word by word from masks; the price in red; the last two lines in italic red; a small
    footnote keeps the €38 honest"""
    S = lambda w_, it=False, col=INK: ftext(w_, "serif-it" if it else "serif", 132, col, wght=900 if not it else 700)
    L1 = [S(w_, col=RED if "€" in w_ else INK) for w_ in l1]; L2 = [S(w_) for w_ in l2]
    L3 = [S(w_, True, RED) for w_ in l3]; L4 = [S(w_, True, RED) for w_ in l4]
    nt = ftext(note, "m", 26, MUTED); star = ftext("*", "serif", 90, RED, wght=900)
    def fn(t):
        im = paper(); masthead(im, t)
        M.words_rise(im, L1, W / 2, 520, t, at[0], stagger=0.09); M.words_rise(im, L2, W / 2, 680, t, at[1], stagger=0.09)
        M.words_rise(im, L3, W / 2, 940, t, at[2], stagger=0.08); M.words_rise(im, L4, W / 2, 1100, t, at[3], stagger=0.08)
        if t >= note_at:
            M.reveal_lr(im, nt, W / 2, 1420, (t - note_at) / 0.6); put(im, ftext("*", "serif", 60, RED, wght=900), W / 2 - nt.width / 2 - 26, 1412, clamp((t - note_at) / 0.2))
        d = ImageDraw.Draw(im); rule(d, W / 2 - 240, 1240, W / 2 + 240, (t - at[3] - 0.35) / 0.5, RED, 4)
        return im, 0
    ev = [(0.0, "swish", 0.35), (at[0], "pop", 0.5), (at[0] + 0.18, "coin", 0.5), (at[1], "pop", 0.4), (at[2], "whoosh", 0.4), (at[3], "hit", 0.7)]
    return dur, fn, ev


# ======================================================================= 2. 90 days of silence
def scene_silence(dur=4.8, order=("ORDER Nº 2081", "Linen shirt · size M", "€64"), marks=(("Day 1", 0.0, "no email"), ("Day 30", 0.33, "no email"), ("Day 60", 0.66, "no email"), ("Day 90", 1.0, "no email")),
                  line_at=1.0, line_dur=2.0, big_at=3.1, big=("90 days.", "Not one email."), tag="Her first order", sub_col=None):
    """her order slip slides in with motion blur, then a timeline rule runs across the page; each day mark drops a grey
    'no email' tick; the pull line lands"""
    sw, sh = 760, 250
    def slip(d, s, im):
        d.rectangle((0, 0, sw * s - 1, sh * s - 1), fill=(252, 249, 243)); d.rectangle((0, 0, sw * s - 1, sh * s - 1), outline=INK, width=3 * s)
        d.text((40 * s, 34 * s), order[0], font=M.ffont("b", 28 * s), fill=MUTED)
        d.text((40 * s, 86 * s), order[1], font=M.ffont("serif", 56 * s, 700), fill=INK)
        f = M.ffont("serif", 64 * s, 900); tw = d.textlength(order[2], font=f); d.text(((sw - 40) * s - tw, 150 * s), order[2], font=f, fill=INK)
        d.text((40 * s, 170 * s), tag, font=M.ffont("serif-it", 34 * s, 400), fill=RED)
    SL = A.shadowed(A.sprite(sw, sh, slip), blur=24, dy=14, alpha=40, pad=50)
    X0, X1, Y = 140, W - 140, 1080
    lab = [ftext(m, "b", 30, INK) for m, _, _ in marks]; subs = [ftext(sb, "serif-it", 34, sub_col[i] if sub_col else MUTED) for i, (_, _, sb) in enumerate(marks)]
    B1, B2 = ftext(big[0], "serif", 150, INK, wght=900), ftext(big[1], "serif-it", 96, RED, wght=700)
    def inv(f):  # time at which cubic_io(progress) reaches f
        lo, hi = 0.0, 1.0
        for _ in range(30): mid = (lo + hi) / 2; lo, hi = (mid, hi) if cubic_io(mid) < f else (lo, mid)
        return line_at + line_dur * hi
    reach = [inv(f) for _, f, _ in marks]
    def fn(t):
        im = paper(); masthead(im, 9); d = ImageDraw.Draw(im)
        M.slide_put(im, SL, -500, 600, W / 2, 600, (t - 0.1) / 0.7, expo_out, rot0=-4)
        p = (t - line_at) / line_dur
        if p > 0:
            xe = X0 + (X1 - X0) * cubic_io(p); d.line((X0, Y, xe, Y), fill=INK, width=4); d.ellipse((xe - 10, Y - 10, xe + 10, Y + 10), fill=INK)
            for (m, f, _), lb, no, tr in zip(marks, lab, subs, reach):
                k = (t - tr) / 0.35   # each mark lands when the line reaches it
                if k > 0:
                    x = X0 + (X1 - X0) * f; d.line((x, Y - 24, x, Y + 24), fill=INK, width=4)
                    M.reveal_lr(im, lb, x, Y - 64, k)
                    put(im, no, x, Y + 70 + 12 * (1 - quint_out(k)), clamp(k), 1.0)
        if t >= big_at:
            M.words_rise(im, [B1], W / 2, 1380, t, big_at); M.words_rise(im, [B2], W / 2, 1530, t, big_at + 0.25)
        return im, 0
    ev = [(0.1, "whoosh", 0.6), (0.45, "click", 0.5), (line_at, "swish", 0.4)] + [(r_, "tick", 0.5) for r_ in reach] + [(big_at, "hit", 0.6), (big_at + 0.25, "whoosh", 0.3)]
    return dur, fn, ev


# ======================================================================= 3. pull quote
def scene_quote(dur=3.0, lines=("She already loves", "the fit."), sub="Selling to her again is easier", sub2="than finding someone new.", size=112):
    """giant red quote marks draw in, the quote rises, the attribution rule draws"""
    q = ftext("“", "serif", 420, RED, wght=900); L = [ftext(l, "serif-it", size, INK, wght=600) for l in lines]
    s1, s2 = ftext(sub, "m", 40, MUTED), ftext(sub2, "m", 40, MUTED)
    def fn(t):
        im = paper(); masthead(im, 9)
        k = back_out((t - 0.05) / 0.5); put(im, q, W / 2, 560 + 30 * (1 - k), clamp((t - 0.05) / 0.2), 0.7 + 0.3 * k)
        for i, l in enumerate(L): M.words_rise(im, [l], W / 2, 860 + i * 140, t, 0.35 + i * 0.15)
        d = ImageDraw.Draw(im); rule(d, W / 2 - 60, 1170, W / 2 + 60, (t - 0.9) / 0.4, RED, 4)
        M.words_rise(im, [s1], W / 2, 1260, t, 1.1); M.words_rise(im, [s2], W / 2, 1320, t, 1.2)
        return im, 0
    return dur, fn, [(0.05, "pop", 0.6), (0.35, "whoosh", 0.4), (1.1, "swish", 0.3)]


# ======================================================================= 4. contents page = the flow we build
def scene_contents(dur=5.4, head="In this issue:", head2="her next five emails.", rows=(("01", "Thank you + fit guide", "Day 1"), ("02", "How to style it", "Day 7"),
                   ("03", "Leave a review", "Day 14"), ("04", "New in, picked for her", "Day 30"), ("05", "We miss you", "Day 60")),
                   by="Written, designed and set live by Southline.", start=0.9, gap=0.45, by_at=3.6):
    """a magazine contents list: numbers slide in, dotted leaders run across, the day lands at the right edge"""
    H1, H2 = ftext(head, "serif", 96, INK, wght=900), ftext(head2, "serif-it", 84, RED, wght=600)
    NUM = [ftext(n, "serif", 64, RED, wght=900) for n, _, _ in rows]; TI = [ftext(ti, "serif", 50, INK, wght=600) for _, ti, _ in rows]
    DAY = [ftext(dd, "b", 32, INK) for _, _, dd in rows]; BY = ftext(by, "serif-it", 40, MUTED)
    X0, X1, Y0, RH = 110, W - 110, 720, 150
    def fn(t):
        im = paper(); masthead(im, 9); d = ImageDraw.Draw(im)
        M.words_rise(im, [H1], W / 2, 420, t, 0.15); M.words_rise(im, [H2], W / 2, 540, t, 0.35)
        for i in range(len(rows)):
            t0 = start + i * gap; p = (t - t0) / 0.5
            if p <= 0: continue
            y = Y0 + i * RH
            M.slide_put(im, NUM[i], X0 - 120, y, X0 + NUM[i].width / 2, y, p, expo_out)
            put(im, TI[i], X0 + 110 + TI[i].width / 2 + 30 * (1 - quint_out(p)), y, clamp(p / 0.3))
            lx0 = X0 + 130 + TI[i].width; lx1 = X1 - DAY[i].width - 20; lp = quint_out((t - t0 - 0.2) / 0.5)
            x = lx0
            while x < lx0 + (lx1 - lx0) * lp: d.ellipse((x - 3, y + 14, x + 3, y + 20), fill=RULE); x += 16
            if lp > 0.95: put(im, DAY[i], X1 - DAY[i].width / 2, y + 4, clamp((t - t0 - 0.65) / 0.2))
            rule(d, X0, y + RH / 2, X1, (t - t0 - 0.1) / 0.6, RULE, 2)
        M.reveal_lr(im, BY, W / 2, Y0 + len(rows) * RH + 70, (t - by_at) / 0.8)
        return im, 0
    ev = [(0.15, "whoosh", 0.4)] + [(start + i * gap, "swish", 0.45) for i in range(len(rows))] + [(start + i * gap + 0.7, "tick", 0.5) for i in range(len(rows))] + [(by_at, "swish", 0.3)]
    return dur, fn, ev


# ======================================================================= 5. subscription coupon = the offer
def scene_coupon(dur=4.8, head="THE OFFER", title=("Meta ads + email,", "done for clothing brands."), stamp_lines=("NOTHING", "UPFRONT", "· FREE CALL ·"), foot=None, lines=(("We run your Meta ads", "to bring in new customers"), ("We build the emails", "that bring them back"),
                 ("No retainer", "paid per new subscriber")), cut_at=0.35, rows_at=(1.0, 1.45, 1.9), stamp_at=2.9):
    """a magazine subscription coupon: scissors cut along the dashed line, the card lifts, the three lines tick in,
    then a round red stamp presses on"""
    cw, ch = 920, 1160; X0, Y0 = (W - cw) / 2, 360
    def card(d, s, im):
        d.rectangle((0, 0, cw * s - 1, ch * s - 1), fill=(252, 249, 243))
        d.text((60 * s, 60 * s), head, font=M.ffont("b", 30 * s), fill=RED)
        d.text((60 * s, 110 * s), title[0], font=M.ffont("serif", 80 * s, 900), fill=INK)
        d.text((60 * s, 205 * s), title[1], font=M.ffont("serif-it", 66 * s, 600), fill=INK)
        d.line((60 * s, 320 * s, (cw - 60) * s, 320 * s), fill=INK, width=2 * s)
    C = A.sprite(cw, ch, card)
    R = [(ftext(a, "serif", 58, INK, wght=800), ftext(b, "serif-it", 44, MUTED, wght=400)) for a, b in lines]
    box = A.sprite(64, 64, lambda d, s, im: d.rectangle((3 * s, 3 * s, 61 * s, 61 * s), outline=INK, width=4 * s))
    tick = A.sprite(64, 64, lambda d, s, im: d.line((14 * s, 34 * s, 28 * s, 48 * s, 54 * s, 14 * s), fill=RED, width=8 * s, joint="curve"))
    def stamp():
        def dr(d, s, im):
            d.ellipse((6 * s, 6 * s, 294 * s, 294 * s), outline=RED, width=8 * s); d.ellipse((24 * s, 24 * s, 276 * s, 276 * s), outline=RED, width=3 * s)
            for txt, y, sz in ((stamp_lines[0], 92, 38), (stamp_lines[1], 140, 38), (stamp_lines[2], 196, 26)):
                f = M.ffont("b", sz * s); tw = d.textlength(txt, font=f); d.text((150 * s - tw / 2, y * s), txt, font=f, fill=RED)
        return A.sprite(300, 300, dr)
    ST = stamp(); FT = ftext(foot, "serif-it", 36, MUTED, wght=400) if foot else None
    def fn(t):
        im = paper(); d = ImageDraw.Draw(im)
        lift = quint_out((t - cut_at - 0.55) / 0.5)
        x, y = X0 - 16 * lift, Y0 - 16 * lift
        if lift > 0: d.rectangle((X0 + 10, Y0 + 14, X0 + cw + 10, Y0 + ch + 14), fill=(222, 214, 200))
        im.alpha_composite(C, (int(x), int(y)))
        # dashed cut line around the card, consumed by the scissors
        per = 2 * (cw + ch); cp = cubic_io((t - cut_at) / 0.7) * per
        pts = [(X0 - 20, Y0 - 20), (X0 + cw + 20, Y0 - 20), (X0 + cw + 20, Y0 + ch + 20), (X0 - 20, Y0 + ch + 20), (X0 - 20, Y0 - 20)]
        dist = 0
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay); n = int(L // 22)
            for j in range(n):
                dd = dist + j * 22
                if dd < cp or lift >= 1: continue
                fx, fy = ax + (bx - ax) * j / n, ay + (by - ay) * j / n; d.line((fx, fy, fx + (bx - ax) / n * 0.5, fy + (by - ay) / n * 0.5), fill=MUTED, width=3)
            dist += L
        for i, (a, b) in enumerate(R):
            k = (t - rows_at[i]) / 0.5
            if k <= 0: continue
            ry = y + 420 + i * 170
            put(im, box, x + 100, ry, clamp(k / 0.2)); M.reveal_lr(im, tick, x + 100, ry, (k - 0.2) / 0.4)
            put(im, a, x + 160 + a.width / 2 + 24 * (1 - quint_out(k)), ry - 18, clamp(k / 0.3)); put(im, b, x + 160 + b.width / 2 + 24 * (1 - quint_out(k)), ry + 46, clamp((k - 0.15) / 0.3))
        if foot and t >= rows_at[-1] + 0.4: M.reveal_lr(im, FT, x + 60 + FT.width / 2, y + ch - 90, (t - rows_at[-1] - 0.4) / 0.6)
        if t >= stamp_at:
            k = (t - stamp_at) / 0.25; put(im, ST, x + cw - 190, y + ch - 170, clamp(k / 0.3), 1.35 - 0.35 * quint_out(k), -12)
        return im, (6 * (1 - (t - stamp_at - 0.12) / 0.12) if stamp_at + 0.12 <= t < stamp_at + 0.24 else 0)
    ev = [(cut_at, "swish", 0.5), (cut_at + 0.35, "swish", 0.4), (cut_at + 0.6, "click", 0.5)] + [(a, "tick", 0.6) for a in rows_at] + [(stamp_at + 0.12, "hit", 0.9)]
    return dur, fn, ev


# ======================================================================= 6. RSVP card = book a call
def scene_rsvp(dur=4.4, kicker="R.S.V.P.", l1="A free 15-minute call.", l2="We'll map your next five emails", l3="with you, live.",
               sign="Ryan", by="Southline Agency", cta="Book it · link in bio", sign_at=1.6, cta_at=2.7):
    """an invitation card: thin double border draws round, the lines rise, a signature writes itself in ink, the
    booking line underlines"""
    K = ftext(kicker, "serif", 64, RED, wght=900); L1 = ftext(l1, "serif", 76, INK, wght=800)
    L2, L3 = ftext(l2, "serif-it", 54, INK, wght=500), ftext(l3, "serif-it", 54, INK, wght=500)
    SG = ftext(sign, "serif-it", 150, INK, wght=400); BY = ftext(by, "b", 30, MUTED)
    CT = ftext(cta, "serif", 66, INK, wght=900)
    lg = A.logo().resize((130, 130), Image.LANCZOS)
    def fn(t):
        im = paper(); d = ImageDraw.Draw(im)
        bx0, by0, bx1, by1 = 90, 260, W - 90, 1660; per = cubic_io(t / 0.9)
        for inset, wdt in ((0, 4), (14, 1)):
            x0, y0, x1, y1 = bx0 + inset, by0 + inset, bx1 - inset, by1 - inset
            segs = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
            for i, ((ax, ay), (bx, by)) in enumerate(segs):
                q = clamp(per * 4 - i)
                if q > 0: d.line((ax, ay, ax + (bx - ax) * q, ay + (by - ay) * q), fill=INK, width=wdt)
        M.words_rise(im, [K], W / 2, 420, t, 0.3); M.words_rise(im, [L1], W / 2, 580, t, 0.5)
        M.words_rise(im, [L2], W / 2, 700, t, 0.7); M.words_rise(im, [L3], W / 2, 770, t, 0.8)
        M.reveal_lr(im, SG, W / 2, 1000, quint_out((t - sign_at) / 0.9))
        rule(d, W / 2 - 260, 1080, W / 2 + 260, (t - sign_at - 0.4) / 0.5, INK, 2); M.reveal_lr(im, BY, W / 2, 1120, (t - sign_at - 0.6) / 0.5)
        if t >= cta_at:
            M.words_rise(im, [CT], W / 2, 1320, t, cta_at); rule(d, W / 2 - CT.width / 2, 1372, W / 2 + CT.width / 2, (t - cta_at - 0.3) / 0.5, RED, 6)
        put(im, lg, W / 2, 1530, clamp((t - cta_at - 0.4) / 0.3), 0.85 + 0.15 * back_out((t - cta_at - 0.4) / 0.5))
        return im, 0
    ev = [(0.0, "swish", 0.4), (0.3, "pop", 0.5), (0.5, "whoosh", 0.3), (sign_at, "swish", 0.5), (cta_at, "hit", 0.7), (cta_at + 0.4, "coin", 0.5)]
    return dur, fn, ev
