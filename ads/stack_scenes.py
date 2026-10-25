"""STACK + HIGHLIGHT + ZOOM scenes for the 8-part structure (Hook, Lead, Body 1, Open loop, Body 2, Open loop, Body 3, CTA).
Same simple look as structure_scenes (off-white, black type, one accent) but more motion:
  - stacking: cards drop onto a deck / build a tower / notifications push down
  - highlight then zoom: a key word gets the highlighter swipe, then the camera pushes in on it
  - word-by-word pops, zoom-out reveals, punch-ins
camera(scene, keys) wraps any scene with keyframed zooms: keys = [(t, scale, cx, cy), ...]."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed
from structure_scenes import INK, MUTED, WHITE, LINE, ACC, marker, card, label


# ======================================================================= camera + highlighted lines
def _cam(keys, t):
    if t <= keys[0][0]: return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            f = eio((t - a[0]) / max(1e-6, b[0] - a[0])); return tuple(a[i] + (b[i] - a[i]) * f for i in (1, 2, 3))
    return keys[-1][1:]

def zoom_at(im, s, cx, cy):
    """crop a 1/s window around (cx,cy) (kept inside the frame) and scale it back up"""
    w, h = W / s, H / s; x0 = clamp(cx - w / 2, 0, W - w); y0 = clamp(cy - h / 2, 0, H - h)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))

def camera(scene, keys):
    dur, fn, ev = scene
    def f2(t):
        im, sh = fn(t); s, cx, cy = _cam(keys, t)
        return (zoom_at(im, s, cx, cy) if s > 1.002 else im), sh
    return dur, f2, ev


class Line:
    """one centred line laid out word by word, so single words can pop in or get the highlighter.
    hi = (first, last) word index of the highlighted span"""
    def __init__(self, s, size, hi=None, w="bl", maxw=960, col=INK):
        self.size = size = fit_size(s, w, size, maxw); self.words = s.split(" "); self.hi = hi
        self.ink = [text(x, w, size, col) for x in self.words]; self.wh = [text(x, w, size, WHITE) for x in self.words]
        sp = size * 0.26; tot = sum(i.width for i in self.ink) + sp * (len(self.words) - 1); x = -tot / 2; self.xs = []
        for i in self.ink: self.xs.append(x + i.width / 2); x += i.width + sp

    def hi_box(self, cx, cy):
        a, b = self.hi; h = self.ink[0].height
        return (cx + self.xs[a] - self.ink[a].width / 2 - 16, cy - h / 2 + self.size * 0.08, cx + self.xs[b] + self.ink[b].width / 2 + 16, cy + h / 2 - self.size * 0.02)

    def hi_centre(self, cx, cy):
        x0, y0, x1, y1 = self.hi_box(cx, cy); return (x0 + x1) / 2, (y0 + y1) / 2

    def draw_hi(self, im, cx, cy):
        """just the finished highlight (box + white words), for drawing on top of a dimmed frame"""
        ImageDraw.Draw(im).rounded_rectangle(self.hi_box(cx, cy), 14, fill=ACC())
        for i in range(self.hi[0], self.hi[1] + 1): put(im, self.wh[i], cx + self.xs[i], cy)

    def draw(self, im, cx, cy, ps, p_hi=0.0, mode="rise"):
        """ps: per-word reveal progress (one number = all words). mode rise = masked slide up, pop = scale-in"""
        ps = ps if isinstance(ps, (list, tuple)) else [ps] * len(self.words)
        x1 = None
        if self.hi and p_hi > 0:
            x0, y0, xe, y1 = self.hi_box(cx, cy); x1 = x0 + (xe - x0) * eo(p_hi)
            ImageDraw.Draw(im).rounded_rectangle((x0, y0, x1, y1), 14, fill=ACC())
        for i, (ink, wh, x, p) in enumerate(zip(self.ink, self.wh, self.xs, ps)):
            if p <= 0: continue
            if mode == "pop": put(im, ink, cx + x, cy, clamp(p / 0.4), 1.45 - 0.45 * back(p))
            else: put_rise(im, ink, cx + x, cy, eo(p))
            if x1 is not None and self.hi[0] <= i <= self.hi[1]:
                left = int(cx + x - wh.width / 2); cw = int(clamp(x1 - left, 0, wh.width))
                if cw > 0: im.alpha_composite(wh.crop((0, 0, cw, wh.height)), (left, int(cy - wh.height / 2)))


# ======================================================================= 01 HOOK
QUOTES = [("Kitchen quote", "Naas", "No reply"), ("Bathroom quote", "Swords", "Just looking"), ("En-suite quote", "Bray", "Went quiet"),
          ("Kitchen quote", "Ennis", "Ghosted"), ("Bathroom quote", "Malahide", "Still deciding"), ("Kitchen quote", "Lucan", "BOOKED")]

def quote_card(title, area, status, state):
    """state 0 = sent, 1 = dead (title struck through, muted status), 2 = booked (accent fill)"""
    w, h = 860, 118; acc = ACC(); fill = acc if state == 2 else WHITE; fg = WHITE if state == 2 else INK
    def dr(d, s):
        d.rounded_rectangle((24 * s, 22 * s, 98 * s, 96 * s), 20 * s, fill=(255, 255, 255, 60) if state == 2 else (240, 237, 231))
        f = A.font("bl", 40 * s); tw, th, ox, oy = A.tsize("Q", f); d.text((61 * s - tw / 2 - ox, 59 * s - th / 2 - oy), "Q", font=f, fill=fg if state == 2 else MUTED)
        ft = A.font("b", 40 * s); d.text((124 * s, 22 * s), title, font=ft, fill=fg if state != 1 else MUTED)
        if state == 1: d.line((118 * s, 49 * s, 130 * s + A.tsize(title, ft)[0], 49 * s), fill=INK, width=5 * s)
        d.text((124 * s, 70 * s), area, font=A.font("m", 28 * s), fill=(255, 255, 255, 220) if state == 2 else MUTED)
        st = {0: "Quote sent", 1: status, 2: "BOOKED"}[state]; f2 = A.font("bl" if state == 2 else "sb", 34 * s)
        tw, th, ox, oy = A.tsize(st, f2); x = (w - 40) * s - tw - (60 * s if state == 2 else 0)
        d.text((x - ox, 59 * s - th / 2 - oy), st, font=f2, fill=WHITE if state == 2 else (INK if state == 0 else MUTED))
        if state == 2: A.check(d, s, w - 84, 37, (255, 255, 255)); d.line([((w - 72) * s, 60 * s), ((w - 64) * s, 68 * s), ((w - 50) * s, 51 * s)], fill=acc, width=6 * s)
    return card(w, h, dr, fill)

def scene_hook(dur=4.0, drops=(-0.6, 0.45, 0.85, 1.25), big_at=2.05, quotes=None):
    """frame 0: 'Kitchen & bathroom companies,' + a quote card on the deck. Quote cards slam onto the stack one by one,
    each gets struck out (no reply, just looking...), the last one lands BOOKED in blue. The deck falls away,
    '6 quotes. 1 yes.' slams in, '1 yes.' gets highlighted and the camera zooms into it."""
    h1 = text("Kitchen & bathroom", "bl", fit_size("Kitchen & bathroom", "bl", 110, 960)); h2 = text("companies,", "bl", 136, ACC())
    qs = quotes or [QUOTES[0], QUOTES[1], QUOTES[3], QUOTES[5]]  # no reply, just looking, ghosted, BOOKED
    cards = [[quote_card(t_, a_, s_, st) for st in (0, 1, 2)] for t_, a_, s_ in qs]
    b1 = text(f"{len(qs)} quotes.", "bl", 190); YES_Y = 1170

    def fn(t):
        im = A.bg(); sh = 12 * (1 - t / 0.16) if t < 0.16 else 0
        out = eio((t - big_at) / 0.3); ta = 1 - eo((t - big_at - 0.6) / 0.3)  # title fades before the zoom
        put(im, h1, W / 2, 390, ta, 1.04 - 0.04 * eo(t / 0.3)); put(im, h2, W / 2, 515, ta, 1.06 - 0.06 * eo(t / 0.3))
        if out < 1:
            sps = []
            for i, (tt, ar, st) in enumerate(qs):
                ok = st == "BOOKED"; sps.append(cards[i][(2 if ok else 1) if t >= drops[i] + (0.4 if ok else 0.3) else 0])
            deck = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh = max(sh, A.draw_stack(deck, sps, drops, t, 940, step=70, from_y=-1300, rot=-8))
            if out > 0: deck.putalpha(deck.split()[3].point(lambda v: int(v * (1 - out))))
            im.alpha_composite(deck, (0, int(900 * out * out)))
            kk = (t - drops[-1] - 0.4) / 1.2; ring(im, W / 2, 940, kk, col=ACC(), maxr=420, width=6, r0=80)
        if t >= big_at:
            k = (t - big_at - 0.1) / 0.3
            put(im, b1, W / 2, 900, clamp(k / 0.2), 1.25 - 0.25 * eo(k))
            if k > 0.9: marker(im, "1 yes.", W / 2, YES_Y, (t - big_at - 0.65) / 0.3, 240)
            if 0.9 <= k < 1.35: sh = 16
        return im, sh
    ev = [(0.0, "hit", 1.0)] + [(d0 + 0.28, "hit", 0.55) for d0 in drops[1:]] + [(drops[i] + 0.3, "swish", 0.4) for i in range(1, len(drops) - 1)] + \
         [(drops[-1] + 0.4, "ping", 0.8), (big_at, "whoosh", 0.5), (big_at + 0.1, "hit", 0.9), (big_at + 0.37, "hit", 1.0), (big_at + 0.65, "swish", 0.6), (big_at + 1.0, "whoosh", 0.6)]
    sc = (dur, fn, ev)
    return camera(sc, [(big_at + 0.95, 1.0, W / 2, 960), (big_at + 1.45, 1.12, W / 2, 1060), (dur, 1.15, W / 2, 1070)])


# ======================================================================= 02 LEAD
def scene_lead(dur=3.2, swap=1.85, total_at=1.9):
    """'Every free quote costs you AN EVENING.' -> highlight -> zoom into 'evening.', then zoom back out to
    an hours counter rolling to 15 (example week)"""
    l1, l2 = Line("Every 'free' quote", 100), Line("costs you", 100); l3 = Line("an evening.", 150, hi=(1, 1))
    ex_, ey_ = l3.hi_centre(W / 2, 1090)
    sub = text("gone on dead quotes.", "xb", 64); ex = text("example week", "mono", 28, MUTED)

    def fn(t):
        im = A.bg(); sh = 0
        if t < swap:
            l1.draw(im, W / 2, 790, t / 0.3); l2.draw(im, W / 2, 930, (t - 0.25) / 0.3); l3.draw(im, W / 2, 1090, (t - 0.5) / 0.3, (t - 0.85) / 0.35)
        else:
            n = int(round(15 * eo((t - total_at) / 0.5))); k = (t - total_at) / 0.3
            put(im, text(f"{n} hrs", "bl", 280), W / 2, 880, clamp(k / 0.2), 1.15 - 0.15 * eo(k))
            put_rise(im, sub, W / 2, 1080, eo((t - total_at - 0.45) / 0.3)); put(im, ex, W / 2, 1170, eo((t - total_at - 0.6) / 0.3))
            if total_at + 0.5 <= t < total_at + 0.64: sh = 10
        return im, sh
    ev = [(0.0, "whoosh", 0.4), (0.25, "swish", 0.4), (0.5, "swish", 0.4), (0.85, "swish", 0.6), (1.25, "whoosh", 0.6), (swap - 0.05, "whoosh", 0.5)] + \
         [(total_at + i * 0.035, "tick", 0.3) for i in range(14)] + [(total_at + 0.5, "hit", 1.0)]
    return camera((dur, fn, ev), [(1.2, 1.0, W / 2, 960), (1.6, 1.55, ex_, ey_), (swap - 0.05, 1.6, ex_, ey_), (swap + 0.15, 1.0, W / 2, 960)])


# ======================================================================= 03 BODY 1
def scene_body1(dur=3.8, zoom=(0.5, 1.95), you_at=2.0, punch_at=2.65):
    """'They found you on a LIST.' (highlight) - camera starts tight on your listing and pulls back to a wall of 80
    identical companies: 'You're 1 of 80.' -> 'Collecting quotes. NOT CHOOSING YOU.' (highlight + punch-in)"""
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
    G = grid(); BOX = (60, 650, W - 60, 1450); bw, bh = BOX[2] - BOX[0], BOX[3] - BOX[1]
    ux, uy = YOU[1] * (tw + g) + tw / 2, YOU[0] * (th + g) + th / 2
    h1, h2 = Line("They found you", 92), Line("on a list.", 92, hi=(2, 2))
    p1 = text("Collecting quotes.", "bl", fit_size("Collecting quotes.", "bl", 120, 940)); p2 = Line("Not choosing you.", 120, hi=(0, 2))

    def fn(t):
        im = A.bg(); h1.draw(im, W / 2, 410, t / 0.25); h2.draw(im, W / 2, 520, (t - 0.1) / 0.25, (t - 0.35) / 0.3)
        f = eio((t - zoom[0]) / (zoom[1] - zoom[0])); z = 3.4 + (bw / gw * 0.98 - 3.4) * f
        Gs = G.resize((max(1, int(gw * z)), max(1, int(gh * z))), Image.BICUBIC)
        cx, cy = (ux + (gw / 2 - ux) * f) * z, (uy + (gh / 2 - uy) * f) * z
        win = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); win.paste(Gs, (int(bw / 2 - cx), int(bh / 2 - cy)), Gs)
        im.alpha_composite(win, (BOX[0], BOX[1]))
        if t >= you_at:
            k = (t - you_at) / 0.3; put(im, A.pill("You're 1 of 80.", 52, INK, w="bl"), W / 2, 1560, clamp(k / 0.2), 0.8 + 0.2 * back(k))
        if t >= punch_at:
            k = (t - punch_at) / 0.3; o = Image.new("RGBA", (W, H), A.TH["bg"][0] + (int(250 * clamp(k / 0.6)),)); im.alpha_composite(o)
            put(im, p1, W / 2, 880, clamp(k / 0.2), 1.2 - 0.2 * eo(k)); p2.draw(im, W / 2, 1040, (t - punch_at - 0.2) / 0.25, (t - punch_at - 0.5) / 0.3, mode="pop")
        return im, (12 if punch_at + 0.2 <= t < punch_at + 0.34 else 0)
    ev = [(0.0, "whoosh", 0.4), (0.35, "swish", 0.5), (zoom[0], "swish", 0.6), (you_at, "pop", 0.8), (punch_at, "hit", 0.8), (punch_at + 0.2, "hit", 1.0), (punch_at + 0.5, "swish", 0.6)]
    return camera((dur, fn, ev), [(punch_at + 0.75, 1.0, W / 2, 960), (dur, 1.22, W / 2, 1000)])


# ======================================================================= 04 / 06 OPEN LOOPS (questions)
def scene_question(lines, hi_line, hi, dur=3.0, gap=0.26, mode="rise", zoom=1.7, size=96, word_gap=0.08):
    """open-loop question: lines come in (rise, or word-by-word pop), the key word gets the highlighter,
    then the camera zooms right into it and keeps creeping in"""
    n = len(lines); ys = [960 - (n - 1) * 70 + j * 140 for j in range(n)]
    L = [Line(s, size + (14 if j == hi_line else 0), hi=hi if j == hi_line else None) for j, s in enumerate(lines)]
    # word timings: rise = per line; pop = every word in reading order
    starts, k = [], 0.05
    for j, l in enumerate(L):
        if mode == "pop": starts.append([k + i * word_gap for i in range(len(l.words))]); k += len(l.words) * word_gap
        else: starts.append([k] * len(l.words)); k += gap
    t_hi = k + 0.3; t_z = t_hi + 0.45; zx, zy = L[hi_line].hi_centre(W / 2, ys[hi_line])

    def fn(t):
        im = A.bg()
        for j, l in enumerate(L):
            l.draw(im, W / 2, ys[j], [(t - s0) / (0.3 if mode == "pop" else 0.28) for s0 in starts[j]], (t - t_hi) / 0.3 if j == hi_line else 0, mode)
        dim = eo((t - t_z) / 0.35)  # focus: everything but the highlighted word fades back as the camera pushes in
        if dim > 0:
            im.alpha_composite(Image.new("RGBA", (W, H), A.TH["bg"][0] + (int(205 * dim),))); L[hi_line].draw_hi(im, W / 2, ys[hi_line])
        return im, 0
    ev = [(s[0], "swish", 0.45) for s in starts] if mode == "rise" else [(s0, "pop", 0.35) for s in starts for s0 in s]
    ev += [(t_hi, "swish", 0.7), (t_z, "whoosh", 0.7), (t_z + 0.4, "hit", 0.6)]
    return camera((dur, fn, ev), [(t_z, 1.0, W / 2, 960), (t_z + 0.5, zoom, zx, zy), (dur, zoom * 1.04, zx, zy)])


# ======================================================================= 05 BODY 2
def scene_body2(dur=4.4, scroll=(0.4, 1.1), tap_at=1.6, notes_at=(2.15, 2.5, 2.85, 3.2)):
    """'Their best job is in the FEED.' (highlight). A phone scrolls a feed to the before/after makeover post,
    the camera pushes in as 'Get a quote' is tapped, pulls back out, quote requests stack on top of each other."""
    import kitchen_scenes as K
    PWn, PHn, SW, SH = 600, 940, 560, 900; CY = 1150
    before, after = K.kitchen_art(520, 440, False), K.kitchen_art(520, 440, True, 1)
    shell = shadowed(sprite(PWn, PHn, lambda d, s, im: d.rounded_rectangle((0, 0, PWn * s - 1, PHn * s - 1), 70 * s, fill=INK)), blur=30, dy=20, alpha=50, pad=60)
    smask = sprite(SW, SH, lambda d, s, im: d.rounded_rectangle((0, 0, SW * s - 1, SH * s - 1), 54 * s, fill=(255, 255, 255, 255))).split()[3]
    def post_head(name, d, y):
        d.ellipse((20, y, 76, y + 56), fill=ACC() if name else (230, 226, 218))
        if name: d.text((92, y + 2), name, font=A.font("b", 28), fill=INK); d.text((92, y + 34), "Sponsored", font=A.font("m", 22), fill=MUTED)
        else: d.rounded_rectangle((92, y + 10, 260, y + 26), 8, fill=(226, 222, 214)); d.rounded_rectangle((92, y + 36, 200, y + 48), 6, fill=(234, 230, 222))
    h1, h2 = Line("Their best job", 92), Line("is in the feed.", 92, hi=(3, 3))
    notes = [("Kitchen · Lucan", "2 min ago"), ("Bathroom · Swords", "9 min ago"), ("En-suite · Bray", "26 min ago"), ("Kitchen · Naas", "1 hr ago")]
    def note(a, b):
        def dr(d, s):
            d.rounded_rectangle((26 * s, 24 * s, 88 * s, 86 * s), 18 * s, fill=ACC())
            f = A.font("bl", 34 * s); tw_, th_, ox, oy = A.tsize("Q", f); d.text((57 * s - tw_ / 2 - ox, 55 * s - th_ / 2 - oy), "Q", font=f, fill=WHITE)
            d.text((110 * s, 18 * s), "New quote request", font=A.font("b", 34 * s), fill=INK); d.text((110 * s, 60 * s), a, font=A.font("m", 28 * s), fill=MUTED)
            f2 = A.font("m", 24 * s); d.text(((700 - 30) * s - A.tsize(b, f2)[0], 22 * s), b, font=f2, fill=MUTED)
        return card(700, 110, dr)
    NS = [note(a, b) for a, b in notes]; ex = text("example", "mono", 24, MUTED)

    def screen(t):
        sc = Image.new("RGBA", (SW, SH), (250, 249, 246, 255)); d = ImageDraw.Draw(sc)
        off = 760 * eio((t - scroll[0]) / (scroll[1] - scroll[0]))
        y = 70 - off; post_head(None, d, y); d.rounded_rectangle((20, y + 76, SW - 20, y + 520), 18, fill=(232, 228, 220))
        y += 760; post_head("Your company", d, y)
        f = 0.5 + 0.45 * math.sin((t - scroll[1]) * 2.4) if t > scroll[1] else 0.95
        sc.alpha_composite(K.rounded(K.before_after(before, after, f), 18), (20, int(y + 76)))
        by = int(y + 76 + 440 + 22); pressed = abs(t - tap_at) < 0.08
        d.rounded_rectangle((20, by, SW - 20, by + 86), 22, fill=tuple(int(c * (0.85 if pressed else 1)) for c in ACC()))
        fb = A.font("bl", 36); a, b_, ox, oy = A.tsize("Get a quote", fb); d.text((SW / 2 - a / 2 - ox, by + 43 - b_ / 2 - oy), "Get a quote", font=fb, fill=WHITE)
        out = Image.new("RGBA", (SW, SH), (0, 0, 0, 0)); out.paste(sc, (0, 0), smask); return out, by + 43
    BTN_Y = CY - SH / 2 + 70 + 76 + 440 + 22 + 43  # button centre once the feed has scrolled

    def fn(t):
        im = A.bg(); h1.draw(im, W / 2, 400, t / 0.25); h2.draw(im, W / 2, 505, (t - 0.15) / 0.3, (t - 0.5) / 0.35)
        k = eo(t / 0.4); cy = CY + 220 * (1 - k)
        put(im, shell, W / 2, cy, k); sc, by = screen(t); put(im, sc, W / 2, cy, k)
        A.tap(im, W / 2 + 205, cy - SH / 2 + by, t, tap_at, t_in=0.4, from_dx=160, from_dy=260)
        landed = [i for i, n0 in enumerate(notes_at) if t >= n0]
        if landed:  # notification stack: newest drops in on top, older ones get pushed down
            nw = landed[-1]; lp = (t - notes_at[nw]) / 0.4
            for i in landed:
                depth = (nw - i) - ((1 - spring(lp, f=1.4, d=7)) if i != nw else 0)
                y = 690 + 128 * depth if i != nw else 690 - 160 * (1 - eo(lp))
                put(im, NS[i], W / 2, y, clamp(lp / 0.25) if i == nw else 1, (0.9 + 0.1 * back(lp)) if i == nw else 1)
            put(im, ex, W / 2, 1640, eo((t - notes_at[0]) / 0.3))
        return im, 0
    ev = [(0.0, "whoosh", 0.4), (0.35, "swish", 0.5), (scroll[0], "swish", 0.6), (tap_at - 0.35, "whoosh", 0.5), (tap_at, "click", 1.0)] + [(n0, "ping", 0.6) for n0 in notes_at]
    return camera((dur, fn, ev), [(tap_at - 0.45, 1.0, W / 2, 960), (tap_at - 0.1, 1.4, W / 2 + 100, BTN_Y), (tap_at + 0.2, 1.4, W / 2 + 100, BTN_Y), (notes_at[0] + 0.05, 1.0, W / 2, 960)])


# ======================================================================= 07 BODY 3
def scene_body3(dur=4.6, drops=(0.7, 1.2, 1.7), junk_at=2.35, ready_at=3.0, qa=None):
    """'The ad ASKS FIRST.' (highlight). Question cards slam down and build a tower from the bottom up,
    a 'Just browsing' lead is flicked away, a 'Ready to book' lead lands with a ring."""
    qa = qa or [("Budget?", "€15k+"), ("When?", "Next 3 months"), ("Photos?", "3 uploaded")]
    hd = Line("The ad asks first.", 104, hi=(2, 3))
    def qcard(q, a):
        chip = A.pill(a, 36, ACC(), w="b")
        def dr(d, s): d.text((40 * s, 32 * s), q, font=A.font("b", 42 * s), fill=INK)
        c = card(860, 112, dr); c.alpha_composite(chip, (50 + 860 - 30 - chip.width, 50 + 56 - chip.height // 2)); return c
    Q = [qcard(q, a) for q, a in qa]
    junk = A.pill("Just browsing", 46, (226, 222, 214), INK, w="b"); ready = shadowed(A.pill("Ready to book  ✓", 54, ACC(), w="bl"), blur=20, dy=12, alpha=50, pad=40)
    end = text("Only ready buyers reach your phone.", "xb", fit_size("Only ready buyers reach your phone.", "xb", 56, 960))

    def fn(t):
        im = A.bg(); sh = 0; hd.draw(im, W / 2, 440, t / 0.3, (t - 0.35) / 0.35)
        for i, d0 in enumerate(drops):  # tower: first card lands lowest
            k = (t - d0) / 0.45
            if k <= 0: continue
            y = 1150 - i * 140 - 1400 * (1 - spring(k, f=1.5, d=6.5))
            put(im, Q[i], W / 2, y, clamp(k / 0.15), 1, (-6 if i % 2 else 6) * (1 - eo(k * 1.3)))
            if 0.28 <= t - d0 < 0.4: sh = 8
        if t >= junk_at:  # browser slides in and is flicked off the left with a spin
            kk = (t - junk_at) / 0.9; x = W / 2 + 600 * (1 - eo(kk / 0.3)) - (1000 * ((kk - 0.45) / 0.55) ** 2 if kk > 0.45 else 0)
            put(im, junk, x, 1420, clamp(1.6 - kk), 1, -40 * clamp((kk - 0.45) / 0.55))
        if t >= ready_at:
            kk = (t - ready_at) / 0.4; put(im, ready, W / 2, 1420 - 300 * (1 - eo(kk)), clamp(kk / 0.2), 0.85 + 0.15 * back(kk))
            ring(im, W / 2, 1420, kk / 1.4, col=ACC(), maxr=440, width=6, r0=160)
            put_rise(im, end, W / 2, 1565, eo((t - ready_at - 0.5) / 0.3))
            if ready_at + 0.3 <= t < ready_at + 0.44: sh = 12
        return im, sh
    ev = [(0.0, "whoosh", 0.4), (0.25, "swish", 0.6)] + [(d0 + 0.3, "hit", 0.6) for d0 in drops] + \
        [(junk_at, "swish", 0.5), (junk_at + 0.45, "swish", 0.7), (ready_at, "whoosh", 0.5), (ready_at + 0.3, "hit", 1.0), (ready_at + 0.35, "shimmer", 0.6)]
    return camera((dur, fn, ev), [(0.0, 1.14, W / 2, 900), (0.5, 1.0, W / 2, 960)])
