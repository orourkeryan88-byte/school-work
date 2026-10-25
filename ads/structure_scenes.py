"""SIMPLE scenes for the 8-part structure (Hook, Lead, Body 1, Open loop, Body 2, Open loop, Body 3, CTA).
One clean look: warm off-white, black type, ONE accent colour (TH['accent']). Motion carries the attention:
strike-throughs, marker highlights, a zoom-out grid, a scrolling feed, a quiz form filling in.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed, TH

INK = (17, 17, 16); MUTED = (128, 124, 116); WHITE = (255, 255, 255); LINE = (226, 222, 214)
def ACC(): return A.TH["accent"]


def marker(im, s, cx, cy, p, size, w="bl", maxw=960):
    """black text that gets a highlighter swipe in the accent colour (p 0->1); the covered part turns white"""
    size = fit_size(s, w, size, maxw); ink, wh = text(s, w, size, INK), text(s, w, size, WHITE)
    x0, y0 = int(cx - ink.width / 2), int(cy - ink.height / 2)
    if p > 0:
        x1 = x0 - 18 + (ink.width + 36) * eo(p)
        ImageDraw.Draw(im).rounded_rectangle((x0 - 18, y0 + size * 0.08, x1, y0 + ink.height - size * 0.02), 14, fill=ACC())
    im.alpha_composite(ink, (x0, y0))
    if p > 0:
        cw = int(clamp(x1 - x0, 0, wh.width))
        if cw > 0: im.alpha_composite(wh.crop((0, 0, cw, wh.height)), (x0, y0))


def card(w, h, draw=None, fill=WHITE, r=30):
    """flat white card, soft shadow"""
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill)
        if draw: draw(d, s)
    return shadowed(sprite(w, h, fn), blur=22, dy=12, alpha=34, pad=50)


def label(s, col=None):
    return text(s, "monob", 30, col or ACC())


# ======================================================================= 01 HOOK
QUOTES = [("Kitchen quote", "Naas", "No reply"), ("Bathroom quote", "Swords", "Just looking"), ("Kitchen quote", "Lucan", "BOOKED"),
          ("En-suite quote", "Bray", "Went quiet"), ("Kitchen quote", "Ennis", "Ghosted"), ("Bathroom quote", "Malahide", "Still deciding")]

def quote_card(title, area, status, state):
    """state 0 = sent (waiting), 1 = dead (muted status), 2 = booked (accent fill)"""
    w, h = 860, 118; acc = ACC(); fill = acc if state == 2 else WHITE; fg = WHITE if state == 2 else INK
    def dr(d, s):
        d.rounded_rectangle((24 * s, 22 * s, 98 * s, 96 * s), 20 * s, fill=(255, 255, 255, 60) if state == 2 else (240, 237, 231))
        f = A.font("bl", 40 * s); tw, th, ox, oy = A.tsize("Q", f); d.text((61 * s - tw / 2 - ox, 59 * s - th / 2 - oy), "Q", font=f, fill=fg if state == 2 else MUTED)
        d.text((124 * s, 22 * s), title, font=A.font("b", 40 * s), fill=fg)
        d.text((124 * s, 70 * s), area, font=A.font("m", 28 * s), fill=(255, 255, 255, 220) if state == 2 else MUTED)
        st = {0: "Quote sent", 1: status, 2: "BOOKED"}[state]; f2 = A.font("bl" if state == 2 else "sb", 34 * s)
        tw, th, ox, oy = A.tsize(st, f2); x = (w - 40) * s - tw - (60 * s if state == 2 else 0)
        d.text((x - ox, 59 * s - th / 2 - oy), st, font=f2, fill=WHITE if state == 2 else (INK if state == 0 else MUTED))
        if state == 2: A.check(d, s, w - 84, 37, (255, 255, 255)); d.line([((w - 72) * s, 60 * s), ((w - 64) * s, 68 * s), ((w - 50) * s, 51 * s)], fill=acc, width=6 * s)
    return card(w, h, dr, fill)

def scene_hook(dur=3.6, first=0.5, gap=0.2, big_at=2.05):
    """frame 0: 'Kitchen & bathroom companies,' + six quote cards on screen. One by one they get struck out
    (no reply, just looking...), one turns blue: BOOKED. Then '6 quotes. 1 yes.' slams in."""
    h1 = text("Kitchen & bathroom", "bl", fit_size("Kitchen & bathroom", "bl", 110, 960)); h2 = text("companies,", "bl", 136, ACC())
    cards = [[quote_card(t_, a_, s_, st) for st in (0, 1, 2)] for t_, a_, s_ in QUOTES]
    b1, b2 = text("6 quotes.", "bl", 190), text("1 yes.", "bl", 250, ACC())

    def fn(t):
        im = A.bg(); sh = 12 * (1 - t / 0.16) if t < 0.16 else 0
        put(im, h1, W / 2, 390, 1, 1.04 - 0.04 * eo(t / 0.3)); put(im, h2, W / 2, 515, 1, 1.06 - 0.06 * eo(t / 0.3))
        out = eio((t - big_at) / 0.35)  # cards drop away before the big line
        for i, (tt, ar, stt) in enumerate(QUOTES):
            tr = first + i * gap; ok = stt == "BOOKED"; state = (2 if ok else 1) if t >= tr else 0; k = (t - tr) / 0.25
            y = 700 + i * 140 + (200 + i * 60) * out; cx = W / 2 + (0 if t < tr else 14 * math.sin(clamp(k) * math.pi) * (1 if ok else -1))
            put(im, cards[i][state], cx, y, (1 if (ok or state == 0) else 0.55) * (1 - out), (1 + 0.07 * (1 - eo(k))) if (t >= tr and ok) else 1)
            if state == 1 and out < 0.98:  # strike-through wipes across the title (overlay so it fades with the card)
                tw = A.tsize(tt, A.font("b", 40))[0]; x0 = cx - 430 + 124; p = eo(k / 0.8)
                o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).line((x0 - 6, y - 13, x0 - 6 + (tw + 12) * p, y - 13), fill=INK + (int(255 * (1 - out)),), width=5); im.alpha_composite(o)
            if state == 2: ring(im, cx, y, k / 1.4, col=ACC(), maxr=360, width=6, r0=60)
        if t >= big_at:
            k = (t - big_at - 0.15) / 0.3
            put(im, b1, W / 2, 930, clamp(k / 0.2), 1.25 - 0.25 * eo(k))
            put(im, b2, W / 2, 1170, clamp((k - 0.9) / 0.2), 1.5 - 0.5 * eo(k - 0.9))
            if 0.9 <= k < 1.35: sh = 16
        return im, sh
    ev = [(0.0, "hit", 1.0)] + [(first + i * gap, "ping" if q[2] == "BOOKED" else "swish", 0.55) for i, q in enumerate(QUOTES)] + \
         [(big_at, "whoosh", 0.5), (big_at + 0.15, "hit", 0.9), (big_at + 0.42, "hit", 1.0)]
    return dur, fn, ev


# ======================================================================= 02 LEAD
def scene_lead(dur=3.2, rows_at=(0.45, 0.75, 1.05), total_at=1.5):
    """every 'free' quote costs you an evening: three cost rows tick in, then an hours counter rolls to 15"""
    items = [("The drive out", "+1 hr"), ("The measure-up", "+1 hr"), ("The drawings", "+1 hr")]
    s1 = text("Every 'free' quote", "bl", fit_size("Every 'free' quote", "bl", 100, 960))
    def row(a, b):
        def dr(d, s):
            d.ellipse((34 * s, 38 * s, 58 * s, 62 * s), fill=ACC()); d.text((86 * s, 26 * s), a, font=A.font("b", 42 * s), fill=INK)
            f = A.font("bl", 42 * s); tw = A.tsize(b, f)[0]; d.text((800 * s - tw, 26 * s), b, font=f, fill=ACC())
        return card(840, 100, dr)
    rows = [row(a, b) for a, b in items]
    sub = text("on 5 quotes that went nowhere.", "xb", 54); ex = text("3 hrs a quote · example week", "mono", 26, MUTED)

    def fn(t):
        im = A.bg(); put_rise(im, s1, W / 2, 400, eo(t / 0.25))
        if t > 0.15: marker(im, "costs you an evening.", W / 2, 520, (t - 0.25) / 0.35, 96)
        for i, d0 in enumerate(rows_at):
            k = (t - d0) / 0.35
            if k > 0: put(im, rows[i], W / 2 + 500 * (1 - eo(k)), 700 + i * 125, clamp(k / 0.3))
        if t >= total_at:
            n = int(round(15 * eo((t - total_at) / 0.7))); k = (t - total_at) / 0.3
            put(im, text(f"{n} hrs", "bl", 260), W / 2, 1210, clamp(k / 0.2), 1.15 - 0.15 * eo(k))
            put_rise(im, sub, W / 2, 1400, eo((t - total_at - 0.5) / 0.3)); put(im, ex, W / 2, 1480, eo((t - total_at - 0.8) / 0.3))
        return im, (12 if total_at + 0.7 <= t < total_at + 0.84 else 0)
    return dur, fn, [(0.0, "whoosh", 0.4), (0.25, "swish", 0.5)] + [(d0, "click", 0.6) for d0 in rows_at] + \
        [(total_at + i * 0.05, "tick", 0.35) for i in range(14)] + [(total_at + 0.7, "hit", 1.0)]


# ======================================================================= 03 BODY 1
def scene_body1(dur=4.0, zoom=(0.45, 2.1), you_at=2.2, punch_at=2.85):
    """body 1: they found you on a list. Camera starts tight on your listing, zooms out to a wall of 80 identical
    companies: 'You're 1 of 80.' then 'Collecting quotes. Not choosing you.'"""
    cols, rows, tw, th, g = 8, 10, 108, 78, 14
    gw, gh = cols * (tw + g) - g, rows * (th + g) - g; YOU = (4, 4)
    def grid():
        def fn(d, s, im):
            for r in range(rows):
                for c in range(cols):
                    x, y = c * (tw + g), r * (th + g); you = (r, c) == YOU
                    d.rounded_rectangle((x * s, y * s, (x + tw) * s, (y + th) * s), 14 * s, fill=ACC() if you else WHITE, outline=None if you else LINE, width=2 * s)
                    if you:
                        f = A.font("bl", 30 * s); a, b_, ox, oy = A.tsize("YOU", f); d.text(((x + tw / 2) * s - a / 2 - ox, (y + th / 2) * s - b_ / 2 - oy), "YOU", font=f, fill=WHITE)
                    else:
                        d.ellipse(((x + 12) * s, (y + 22) * s, (x + 44) * s, (y + 54) * s), fill=(232, 228, 220))
                        d.rounded_rectangle(((x + 52) * s, (y + 26) * s, (x + 96) * s, (y + 36) * s), 5 * s, fill=(222, 218, 210))
                        d.rounded_rectangle(((x + 52) * s, (y + 44) * s, (x + 84) * s, (y + 52) * s), 4 * s, fill=(232, 228, 220))
        return sprite(gw, gh, fn, ss=3)
    G = grid(); BOX = (60, 620, W - 60, 1460); bw, bh = BOX[2] - BOX[0], BOX[3] - BOX[1]
    ux, uy = YOU[1] * (tw + g) + tw / 2, YOU[0] * (th + g) + th / 2  # you-tile centre in grid px
    lab, h2 = label("HERE'S THE PROBLEM:"), text("They found you on a list.", "bl", fit_size("They found you on a list.", "bl", 88, 960))
    p1, p2 = text("Collecting quotes.", "bl", fit_size("Collecting quotes.", "bl", 120, 940)), text("Not choosing you.", "bl", fit_size("Not choosing you.", "bl", 120, 960), ACC())

    def fn(t):
        im = A.bg(); put(im, lab, W / 2, 380, eo(t / 0.2)); put_rise(im, h2, W / 2, 470, eo((t - 0.08) / 0.25))
        z = 3.4 + (bw / gw * 0.98 - 3.4) * eio((t - zoom[0]) / (zoom[1] - zoom[0]))
        Gs = G.resize((max(1, int(gw * z)), max(1, int(gh * z))), Image.BICUBIC)
        f = eio((t - zoom[0]) / (zoom[1] - zoom[0]))  # camera moves from the YOU tile to the grid centre
        cx, cy = (ux + (gw / 2 - ux) * f) * z, (uy + (gh / 2 - uy) * f) * z
        win = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); win.paste(Gs, (int(bw / 2 - cx), int(bh / 2 - cy)), Gs)
        im.alpha_composite(win, (BOX[0], BOX[1]))
        if t >= you_at:
            k = (t - you_at) / 0.3; put(im, A.pill("You're 1 of 80.", 52, INK, w="bl"), W / 2, 1560, clamp(k / 0.2), 0.8 + 0.2 * back(k))
        if t >= punch_at:
            k = (t - punch_at) / 0.3; o = Image.new("RGBA", (W, H), A.TH["bg"][0] + (int(250 * clamp(k / 0.6)),)); im.alpha_composite(o)
            put(im, p1, W / 2, 900, clamp(k / 0.2), 1.2 - 0.2 * eo(k)); put(im, p2, W / 2, 1060, clamp((k - 0.8) / 0.2), 1.3 - 0.3 * eo(k - 0.8))
        return im, (12 if punch_at + 0.24 <= t < punch_at + 0.38 else 0)
    return dur, fn, [(0.0, "whoosh", 0.4), (zoom[0], "swish", 0.6), (you_at, "pop", 0.8), (punch_at, "hit", 0.8), (punch_at + 0.24, "hit", 1.0)]


# ======================================================================= 04 / 06 OPEN LOOPS (questions)
def scene_question(lines, hi, dur=3.0, gap=0.3, qmark=True, size=96):
    """open-loop question: lines rise in one by one, the key line gets the highlighter, a big accent '?' drops and wobbles"""
    n = len(lines); y0 = 900 - (n - 1) * 70 - (90 if qmark else 0)
    q = text("?", "bl", 300, ACC())

    def fn(t):
        im = A.bg()
        for j, s in enumerate(lines):
            k = (t - 0.05 - j * gap) / 0.28; y = y0 + j * 140
            if k <= 0: continue
            if j == hi: marker(im, s, W / 2, y, (t - 0.15 - j * gap) / 0.35, size + 8)
            else: put_rise(im, text(s, "bl", fit_size(s, "bl", size, 960)), W / 2, y, eo(k))
        if qmark:
            tq = 0.05 + n * gap; k = (t - tq) / 0.5
            if k > 0: put(im, q, W / 2, y0 + n * 140 + 130 - 260 * (1 - spring(k, f=2.0, d=5)), clamp(k / 0.15), 1, 12 * math.sin(t * 5) * (1 - clamp(k / 2)))
        return im, 0
    ev = [(0.05 + j * gap, "swish" if j != hi else "whoosh", 0.45) for j in range(n)]
    if qmark: ev += [(0.05 + n * gap + 0.15, "hit", 0.8)]
    return dur, fn, ev


# ======================================================================= 05 BODY 2
def scene_body2(dur=4.6, scroll=(0.4, 1.2), tap_at=1.75, notes_at=(2.2, 2.65, 3.1)):
    """body 2: their best job lands in the feed. A phone scrolls a feed, the before/after makeover post slides in
    and plays, 'Get a quote' is tapped, quote requests drop in."""
    import kitchen_scenes as K
    PWn, PHn, SW, SH = 600, 940, 560, 900
    before, after = K.kitchen_art(520, 440, False), K.kitchen_art(520, 440, True, 1)
    shell = shadowed(sprite(PWn, PHn, lambda d, s, im: d.rounded_rectangle((0, 0, PWn * s - 1, PHn * s - 1), 70 * s, fill=INK)), blur=30, dy=20, alpha=50, pad=60)
    smask = sprite(SW, SH, lambda d, s, im: d.rounded_rectangle((0, 0, SW * s - 1, SH * s - 1), 54 * s, fill=(255, 255, 255, 255))).split()[3]
    def post_head(name, d, y):
        d.ellipse((20, y, 76, y + 56), fill=ACC() if name else (230, 226, 218))
        d.text((92, y + 2), name or "", font=A.font("b", 28), fill=INK); d.text((92, y + 34), "Sponsored" if name else "", font=A.font("m", 22), fill=MUTED)
        if not name: d.rounded_rectangle((92, y + 10, 260, y + 26), 8, fill=(226, 222, 214)); d.rounded_rectangle((92, y + 36, 200, y + 48), 6, fill=(234, 230, 222))
    lab = label("HERE'S WHAT THE BUSY ONES DO:"); h2 = text("Their best job is in the feed.", "bl", fit_size("Their best job is in the feed.", "bl", 82, 960))
    notes = [("New quote request", "Kitchen · Lucan"), ("New quote request", "Bathroom · Swords"), ("New quote request", "En-suite · Bray")]
    def note(a, b):
        def dr(d, s):
            d.ellipse((28 * s, 30 * s, 58 * s, 60 * s), fill=ACC()); d.text((80 * s, 18 * s), a, font=A.font("b", 34 * s), fill=INK)
            d.text((80 * s, 60 * s), b, font=A.font("m", 28 * s), fill=MUTED)
        return card(640, 110, dr)
    NS = [note(a, b) for a, b in notes]; ex = text("example", "mono", 24, MUTED)

    def screen(t):
        sc = Image.new("RGBA", (SW, SH), (250, 249, 246, 255)); d = ImageDraw.Draw(sc)
        off = 760 * eio((t - scroll[0]) / (scroll[1] - scroll[0]))  # feed scrolls up: placeholder post out, our post in
        y = 70 - off; post_head(None, d, y); d.rounded_rectangle((20, y + 76, SW - 20, y + 520), 18, fill=(232, 228, 220))
        y += 760; post_head("Your company", d, y)
        f = 0.5 + 0.45 * math.sin((t - scroll[1]) * 2.4) if t > scroll[1] else 0.95
        ba = K.rounded(K.before_after(before, after, f), 18); sc.alpha_composite(ba, (20, int(y + 76)))
        by = int(y + 76 + 440 + 22); pressed = abs(t - tap_at) < 0.08
        d.rounded_rectangle((20, by, SW - 20, by + 86), 22, fill=tuple(int(c * (0.85 if pressed else 1)) for c in ACC()))
        fb = A.font("bl", 36); a, b_, ox, oy = A.tsize("Get a quote", fb); d.text((SW / 2 - a / 2 - ox, by + 43 - b_ / 2 - oy), "Get a quote", font=fb, fill=WHITE)
        out = Image.new("RGBA", (SW, SH), (0, 0, 0, 0)); out.paste(sc, (0, 0), smask); return out, by + 43

    def fn(t):
        im = A.bg(); put(im, lab, W / 2, 370, eo(t / 0.2)); put_rise(im, h2, W / 2, 460, eo((t - 0.08) / 0.25))
        k = eo(t / 0.4); cx, cy = W / 2, 1130 + 220 * (1 - k)
        put(im, shell, cx, cy, k); sc, by = screen(t); put(im, sc, cx, cy, k)
        A.tap(im, cx + 205, cy - SH / 2 + by, t, tap_at, t_in=0.45, from_dx=160, from_dy=260)
        for i, n0 in enumerate(notes_at):
            kk = (t - n0) / 0.35
            if kk > 0: put(im, NS[i], W / 2, 640 + i * 130 - 120 * (1 - eo(kk)), clamp(kk / 0.25), 0.9 + 0.1 * back(kk))
        if t >= notes_at[0]: put(im, ex, W / 2, 1630, eo((t - notes_at[0]) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4), (scroll[0], "swish", 0.6), (tap_at, "click", 1.0)] + [(n0, "ping", 0.6) for n0 in notes_at]


# ======================================================================= 07 BODY 3
def scene_body3(dur=4.6, rows_at=(0.4, 0.75, 1.1, 1.45), junk_at=2.0, ready_at=2.65):
    """body 3: the ad asks first. A quiz card fills in answer by answer, then a 'Just browsing' lead is flicked away
    and a 'Ready to book' lead lands."""
    qa = [("Kitchen or bathroom?", "Kitchen"), ("Budget?", "€15k+"), ("When?", "Next 3 months"), ("Photos?", "3 uploaded")]
    lab = label("HERE'S THE TRICK:"); h2 = text("The ad asks first.", "bl", 104)
    form = card(880, 560)
    def chip(s): return A.pill(s, 34, ACC(), w="b")
    chips = [chip(a) for _, a in qa]
    junk = A.pill("Just browsing", 44, (226, 222, 214), INK, w="b"); ready = shadowed(A.pill("Ready to book  ✓", 50, ACC(), w="bl"), blur=20, dy=12, alpha=50, pad=40)
    end = text("Only ready buyers reach your phone.", "xb", fit_size("Only ready buyers reach your phone.", "xb", 56, 960))

    def fn(t):
        im = A.bg(); put(im, lab, W / 2, 370, eo(t / 0.2)); put_rise(im, h2, W / 2, 470, eo((t - 0.08) / 0.25))
        k = eo((t - 0.1) / 0.35); fy = 900 + 120 * (1 - k); put(im, form, W / 2, fy, k)
        d = ImageDraw.Draw(im)
        for i, ((q, a), d0) in enumerate(zip(qa, rows_at)):
            y = fy - 280 + 70 + i * 130
            if k > 0.5: d.text((W / 2 - 400, y - 20), q, font=A.font("b", 38), fill=INK if t >= d0 - 0.2 else MUTED)
            if i and k > 0.5: d.line((W / 2 - 400, y - 55, W / 2 + 400, y - 55), fill=LINE, width=2)
            kk = (t - d0) / 0.3
            if kk > 0: put(im, chips[i], W / 2 + 400 - chips[i].width / 2, y + 2, clamp(kk / 0.2), 0.6 + 0.4 * back(kk))
        if t >= junk_at:  # browser lead slides in, gets flicked off the left with a spin
            kk = (t - junk_at) / 0.9; x = W / 2 + 600 * (1 - eo(kk / 0.3)) - (900 * ((kk - 0.45) / 0.55) ** 2 if kk > 0.45 else 0)
            put(im, junk, x, 1340, clamp(1.6 - kk), 1, -40 * clamp((kk - 0.45) / 0.55))
        if t >= ready_at:
            kk = (t - ready_at) / 0.4; put(im, ready, W / 2, 1340 - 300 * (1 - eo(kk)), clamp(kk / 0.2), 0.85 + 0.15 * back(kk))
            ring(im, W / 2, 1340, kk / 1.4, col=ACC(), maxr=440, width=6, r0=160)
            put_rise(im, end, W / 2, 1500, eo((t - ready_at - 0.5) / 0.3))
        return im, (12 if ready_at + 0.3 <= t < ready_at + 0.44 else 0)
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(d0, "pop", 0.6) for d0 in rows_at] + \
        [(junk_at, "swish", 0.5), (junk_at + 0.45, "swish", 0.7), (ready_at, "whoosh", 0.5), (ready_at + 0.3, "hit", 1.0), (ready_at + 0.35, "shimmer", 0.6)]
