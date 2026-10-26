"""BUILDERS 'The Gap' scenes: sells the system (show the work, ask first, a pipeline you can see weeks ahead).
Interactive beats: an emoji-slider sticker that gets dragged ('How full are your next 8 weeks?'), a 'spot the problem'
8-week schedule with a 3-2-1 countdown, a quiz form that gets tapped.
Simple look: concrete grey, black type, ONE safety-orange accent (TH['accent']). Motion: underline swipes, typewriter
questions, a Gantt playhead, an extension building itself brick by brick, a job card moving across a pipeline board.
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed
from stack_scenes import camera

INK = (24, 24, 22); MUTED = (120, 116, 108); WHITE = (255, 255, 255); LINE = (220, 216, 208); COL = (226, 223, 217)
def ACC(): return A.TH["accent"]


class KLine:
    """one centred line. key = substring that gets an orange underline swipe. Can rise in or be typed out."""
    def __init__(self, s, size, key=None, w="bl", col=INK, maxw=960):
        self.s, self.w, self.col = s, w, col; self.size = size = fit_size(s, w, size, maxw)
        self.sp = text(s, w, size, col); f = A.font(w, size); self.k = None
        if key:
            i = s.index(key); self.k = (f.getlength(s[:i]), f.getlength(s[:i]) + f.getlength(key.rstrip(".,?")))

    def left(self, cx): return cx - self.sp.width / 2 + 2

    def underline(self, im, cx, cy, p):
        if not self.k or p <= 0: return
        x0 = self.left(cx) + self.k[0]; x1 = x0 + (self.k[1] - self.k[0]) * eo(p); y = cy + self.size * 0.40; h = max(8, self.size * 0.1)
        ImageDraw.Draw(im).rounded_rectangle((x0, y, max(x0 + 1, x1), y + h), h / 2, fill=ACC())

    def draw(self, im, cx, cy, p, p_ul=0.0):
        self.underline(im, cx, cy, p_ul); put_rise(im, self.sp, cx, cy, eo(p))

    def type(self, im, cx, cy, n, caret=False, p_ul=0.0):
        """typewriter: first n characters, left-aligned to where the full line sits"""
        self.underline(im, cx, cy, p_ul)
        if n > 0:
            sub = text(self.s[:n], self.w, self.size, self.col); im.alpha_composite(sub, (int(cx - self.sp.width / 2), int(cy - sub.height / 2)))
        if caret:
            x = self.left(cx) + A.font(self.w, self.size).getlength(self.s[:n]) + 6
            ImageDraw.Draw(im).rectangle((x, cy - self.size * 0.42, x + 7, cy + self.size * 0.42), fill=ACC())


def card(w, h, draw=None, fill=WHITE, r=30):
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill)
        if draw: draw(d, s)
    return shadowed(sprite(w, h, fn), blur=24, dy=14, alpha=40, pad=50)


def ctext(d, x, y, s_, f, col):
    tw, th, ox, oy = A.tsize(s_, f); d.text((x - tw / 2 - ox, y - th / 2 - oy), s_, font=f, fill=col)


def stamp(word, size=64):
    """rubber-stamp label: orange outline + orange letters"""
    f = A.font("bl", size * 2); tw, th, ox, oy = A.tsize(word, f); w, h = tw // 2 + 70, int(size * 1.7)
    def fn(d, s, im):
        d.rounded_rectangle((4 * s, 4 * s, (w - 4) * s, (h - 4) * s), 16 * s, outline=ACC(), width=7 * s, fill=(255, 255, 255, 215))
        d.text((w * s / 2 - tw / 2 - ox, h * s / 2 - th / 2 - oy), word, font=f, fill=ACC())
    return sprite(w, h, fn)


def label(s):
    return text(s, "monob", 32, ACC())


# ======================================================================= 01 HOOK  (interactive emoji slider)
def scene_hook(dur=3.8, ask_at=0.5, grab=(1.0, 1.9)):
    """frame 0: 'Builders,' + a slider sticker 'How full are your next 8 weeks?' sitting at 7/8. 'Be honest.'
    A finger grabs the handle and drags it down to 2/8; the bubble counts down."""
    big = text("Builders,", "bl", fit_size("Builders,", "bl", 230, 960), ACC())
    SW_, SH_, TX0, TX1, TY = 880, 420, 90, 790, 300
    base = card(SW_, SH_, lambda d, s: (ctext(d, SW_ * s / 2, 72 * s, "How full are your next", A.font("bl", 50 * s), INK),
                                        ctext(d, SW_ * s / 2, 132 * s, "8 weeks?", A.font("bl", 50 * s), INK),
                                        d.text((TX0 * s, 352 * s), "EMPTY", font=A.font("monob", 24 * s), fill=MUTED),
                                        d.text(((TX1 - 96) * s, 352 * s), "PACKED", font=A.font("monob", 24 * s), fill=MUTED)), r=44)
    honest = text("Be honest.", "bl", 96); CX, CY = W / 2, 900

    def fn(t):
        im = A.bg(); sh = 10 * (1 - t / 0.16) if t < 0.16 else 0
        put(im, big, W / 2, 430, 1, 1.08 - 0.08 * eo(t / 0.3)); put(im, base, CX, CY, 1)
        f = 7 / 8 - (5 / 8) * eio((t - grab[0]) / (grab[1] - grab[0]))  # handle position 0..1
        x0 = CX - SW_ / 2 + TX0; x1 = CX - SW_ / 2 + TX1; ty = CY - SH_ / 2 + TY; hx = x0 + (x1 - x0) * f
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((x0, ty - 10, x1, ty + 10), 10, fill=COL); d.rounded_rectangle((x0, ty - 10, hx, ty + 10), 10, fill=ACC())
        d.ellipse((hx - 40, ty - 40, hx + 40, ty + 40), fill=WHITE, outline=ACC(), width=8)
        n = round(f * 8); bub = A.pill(f"{n}/8 booked", 30, INK, WHITE, w="bl"); put(im, bub, hx, ty - 80, 1, 1 + 0.12 * (1 - eo((t - grab[1]) / 0.25)) if t > grab[1] else 1)
        if grab[0] - 0.35 < t < grab[1] + 0.5:  # finger rides the handle
            al = clamp((t - grab[0] + 0.35) / 0.2) * clamp((grab[1] + 0.5 - t) / 0.2); fy = ty + 38
            o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).ellipse((hx - 34, fy - 34, hx + 34, fy + 34), fill=(255, 255, 255, int(220 * al)), outline=(17, 17, 16, int(130 * al)), width=3); im.alpha_composite(o)
        put_rise(im, honest, W / 2, 1280, eo((t - ask_at) / 0.3))
        if grab[1] <= t < grab[1] + 0.14: sh = 9
        return im, sh
    ev = [(0.0, "hit", 1.0), (ask_at, "swish", 0.6), (grab[0], "click", 0.7)] + [(grab[0] + i * (grab[1] - grab[0]) / 5, "tick", 0.4) for i in range(1, 6)] + [(grab[1], "hit", 0.8)]
    return dur, fn, ev


# ======================================================================= 02 LEAD
def scene_lead(dur=3.2):
    """'When a job finishes / with nothing lined up, / the wages don't stop.' (underline swipe, slow push-in)"""
    l1, l2 = KLine("When a job finishes", 96), KLine("with nothing lined up,", 96); l3 = KLine("the wages don't stop.", 112, key="wages don't stop.")

    def fn(t):
        im = A.bg(); l1.draw(im, W / 2, 800, t / 0.3); l2.draw(im, W / 2, 925, (t - 0.35) / 0.3)
        l3.draw(im, W / 2, 1110, (t - 0.85) / 0.3, (t - 1.25) / 0.4)
        return im, (9 if 0.85 <= t < 0.99 else 0)
    ev = [(0.0, "swish", 0.5), (0.35, "swish", 0.5), (0.85, "hit", 0.9), (1.25, "swish", 0.7)]
    return camera((dur, fn, ev), [(1.3, 1.0, W / 2, 960), (dur, 1.05, W / 2, 1000)])


# ======================================================================= 03 BODY 1  (interactive spot-the-problem)
def scene_gap(dur=5.0, bars_at=0.35, play=(0.7, 2.3), count_at=1.2, reveal=2.9):
    """'Spot the problem.' An 8-week schedule: two jobs end by week 4, a TODAY playhead slides along while a 3-2-1
    countdown runs. Then weeks 5-8 fill with orange hatching, 'THE GAP' is stamped on, the camera pushes in."""
    hd = KLine("Your next 8 weeks.", 96); sp_ = KLine("Spot the problem.", 70, key="problem.")
    PX0, PY0, PX1, PY1 = 60, 760, 1020, 1300; GX0, GX1 = 100, 980; cw = (GX1 - GX0) / 8
    jobs = [("Extension · Lucan", 0, 4, 900), ("Attic · Naas", 0, 3, 1010)]
    gap = (GX0 + 4 * cw + 6, 850, GX1, 1240); st = stamp("THE GAP", 66)
    bottom = KLine("Weeks 5–8: nothing booked.", 66, key="nothing booked.")

    def fn(t):
        im = A.bg(); sh = 0
        hd.draw(im, W / 2, 400, t / 0.3); sp_.draw(im, W / 2, 520, (t - 0.25) / 0.3, (t - 0.55) / 0.35)
        k = eo(t / 0.35); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        d.rounded_rectangle((PX0, PY0 + 40 * (1 - k), PX1, PY1 + 40 * (1 - k)), 34, fill=(255, 255, 255, int(255 * k)))
        im.alpha_composite(o); d = ImageDraw.Draw(im)
        for i in range(8 if k > 0.5 else 0):
            x = GX0 + i * cw; ctext(d, x + cw / 2, 810, f"W{i + 1}", A.font("monob", 26), MUTED)
            d.line((x, 840, x, 1260), fill=LINE, width=2)
        if k > 0.5: d.line((GX1, 840, GX1, 1260), fill=LINE, width=2)
        for j, (name, a, b, y) in enumerate(jobs):  # bars draw on left to right
            p = eo((t - bars_at - j * 0.2) / 0.5)
            if p <= 0: continue
            x0, x1 = GX0 + a * cw + 6, GX0 + a * cw + 6 + ((b - a) * cw - 12) * p
            d.rounded_rectangle((x0, y - 38, x1, y + 38), 18, fill=INK)
            if p > 0.6: d.text((x0 + 24, y - 18), name, font=A.font("b", 32), fill=WHITE)
        if t >= reveal:  # the gap: orange hatching + outline
            r = eo((t - reveal) / 0.4); g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
            gd.rounded_rectangle(gap, 20, fill=ACC() + (int(40 * r),), outline=ACC() + (int(255 * r),), width=6)
            for x in range(int(gap[0]) - 400, int(gap[2]), 34):
                gd.line((x, gap[3], x + (gap[3] - gap[1]), gap[1]), fill=ACC() + (int(90 * r),), width=6)
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle(gap, 20, fill=255)
            g.putalpha(Image.fromarray(__import__("numpy").minimum(__import__("numpy").asarray(g.split()[3]), __import__("numpy").asarray(m))))
            im.alpha_composite(g); d = ImageDraw.Draw(im)
            sk = (t - reveal - 0.35) / 0.3
            if sk > 0: put(im, st, (gap[0] + gap[2]) / 2, (gap[1] + gap[3]) / 2, clamp(sk / 0.15), 1.6 - 0.6 * eo(sk), -8)
            if 0 <= sk < 0.45: sh = 10
        px = GX0 + (4 * cw) * eio((t - play[0]) / (play[1] - play[0]))  # TODAY playhead
        if t > play[0] - 0.2:
            d.line((px, 840, px, 1270), fill=ACC(), width=6); put(im, A.pill("TODAY", 24, ACC(), WHITE, w="bl"), px, 1275)
        if count_at <= t < reveal:  # 3-2-1 countdown, top right of the panel
            c = 3 - int((t - count_at) / ((reveal - count_at) / 3)); ph = ((t - count_at) / ((reveal - count_at) / 3)) % 1
            d.ellipse((PX1 - 110, 610, PX1 - 10, 710), fill=INK); ctext(d, PX1 - 60, 660, str(max(1, c)), A.font("bl", 56), WHITE)
            d.arc((PX1 - 116, 604, PX1 - 4, 716), -90, -90 + 360 * (1 - ph), fill=ACC(), width=8)
        bottom.draw(im, W / 2, 1420, (t - reveal - 0.7) / 0.3, (t - reveal - 1.0) / 0.4)
        return im, sh
    ev = [(0.0, "whoosh", 0.5), (0.25, "swish", 0.5), (bars_at + 0.3, "swish", 0.5), (count_at, "tick", 0.8), (count_at + (reveal - count_at) / 3, "tick", 0.8),
          (count_at + 2 * (reveal - count_at) / 3, "tick", 0.8), (reveal, "whoosh", 0.6), (reveal + 0.35, "hit", 1.0), (reveal + 0.7, "swish", 0.5)]
    cx, cy = (gap[0] + gap[2]) / 2, (gap[1] + gap[3]) / 2 + 60
    return camera((dur, fn, ev), [(reveal + 0.3, 1.0, W / 2, 960), (reveal + 0.9, 1.06, W / 2 + 30, cy), (dur, 1.08, W / 2 + 30, cy)])


# ======================================================================= 04 / 06 OPEN LOOPS (typed questions)
def scene_typed(lines, key_line, key, dur=3.4, cps=34, size=88):
    """open-loop question typed out line by line with an orange caret; the key phrase gets underlined; holds to read"""
    L = [KLine(s, size, key=key if j == key_line else None) for j, s in enumerate(lines)]
    n = len(L); ys = [960 - (n - 1) * 70 + j * 140 for j in range(n)]
    starts, k = [], 0.1
    for l in L: starts.append(k); k += len(l.s) / cps + 0.12
    t_end = k; t_ul = t_end + 0.15

    def fn(t):
        im = A.bg()
        for j, l in enumerate(L):
            nch = int(clamp((t - starts[j]) * cps, 0, len(l.s)))
            typing = starts[j] <= t < starts[j] + len(l.s) / cps + 0.12 or (j == n - 1 and t >= starts[j] and int(t * 3) % 2 == 0)
            l.type(im, W / 2, ys[j], nch, caret=typing, p_ul=(t - t_ul) / 0.4 if j == key_line else 0)
        return im, 0
    ev = [(starts[j] + i / cps, "tick", 0.22) for j, l in enumerate(L) for i in range(0, len(l.s), 2)] + [(t_ul, "swish", 0.7), (t_ul + 0.3, "hit", 0.6)]
    return camera((dur, fn, ev), [(t_ul, 1.0, W / 2, 960), (dur, 1.08, W / 2, ys[key_line])])


# ======================================================================= 05 BODY 2  (step 1: show the work)
def scene_show(dur=5.2, build=(0.9, 3.0), roof_at=3.05, door_at=3.35, btn_at=3.7):
    """01 - SHOW THE WORK: a sponsored post whose picture builds a rear extension brick by brick, roof slab and glazing
    drop on, then 'Get a quote' pulses. Header: 'Your best job, in front of homeowners near you.'"""
    lab = label("01 — SHOW THE WORK"); h1 = KLine("Your best work, in front of", 76); h2 = KLine("homeowners near you.", 76, key="homeowners near you.")
    CW, CH = 860, 900; IX, IY, IW, IH = 40, 120, 780, 560
    def chrome(d, s):
        d.ellipse((40 * s, 34 * s, 100 * s, 94 * s), fill=ACC())
        d.text((118 * s, 34 * s), "Your company", font=A.font("b", 32 * s), fill=INK); d.text((118 * s, 72 * s), "Sponsored", font=A.font("m", 24 * s), fill=MUTED)
        d.text((40 * s, 706 * s), "Rear extension · Swords", font=A.font("b", 34 * s), fill=INK)
    POST = card(CW, CH, chrome, r=36); PAD = 50
    cols, rows, bw, bh = 6, 10, 46, 24; ex0, eb = 470, 500  # extension: left edge, ground y (image coords)
    nb = cols * rows

    def picture(t):
        img = Image.new("RGBA", (IW, IH), (238, 236, 231, 255)); d = ImageDraw.Draw(img)
        d.rectangle((0, eb, IW, IH), fill=(214, 210, 202))
        d.rectangle((90, 260, 470, eb), fill=(250, 249, 246), outline=INK, width=6); d.polygon([(70, 264), (280, 110), (490, 264)], fill=(250, 249, 246), outline=INK)
        d.line([(70, 264), (280, 110), (490, 264)], fill=INK, width=6)
        for wx in (130, 350): d.rectangle((wx, 300, wx + 80, 380), outline=INK, width=5)
        d.rectangle((240, 390, 320, eb), outline=INK, width=5)
        nb_now = int(nb * eio((t - build[0]) / (build[1] - build[0])))
        for i in range(nb_now):  # bricks: bottom row first, staggered bond
            r, c = divmod(i, cols); x = ex0 + c * bw + (bw / 2 if r % 2 else 0); y = eb - (r + 1) * bh
            if x + bw > ex0 + cols * bw + 1: x -= cols * bw
            d.rectangle((x + 2, y + 2, x + bw - 2, y + bh - 2), fill=ACC())
        if t >= roof_at:
            k = eo((t - roof_at) / 0.3); y = eb - rows * bh - 26 - 140 * (1 - k); d.rectangle((ex0 - 10, y, ex0 + cols * bw + 24, y + 26), fill=INK)
        if t >= door_at + 0.03:
            k = max(0.1, eo((t - door_at) / 0.3)); dx0, dx1 = ex0 + 50, ex0 + cols * bw - 50; dy1 = eb - 6; dy0 = dy1 - 170 * k
            d.rectangle((dx0, dy0, dx1, dy1), fill=(250, 249, 246), outline=INK, width=6); d.line(((dx0 + dx1) / 2, dy0, (dx0 + dx1) / 2, dy1), fill=INK, width=5)
        m = Image.new("L", (IW, IH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, IW - 1, IH - 1), 22, fill=255); img.putalpha(m); return img

    def fn(t):
        im = A.bg(); put(im, lab, W / 2, 330, eo(t / 0.25)); h1.draw(im, W / 2, 425, (t - 0.1) / 0.3); h2.draw(im, W / 2, 515, (t - 0.25) / 0.3, (t - 0.55) / 0.4)
        k = eo((t - 0.2) / 0.45); cy = 1110 + 160 * (1 - k)
        post = POST.copy(); post.alpha_composite(picture(t), (PAD + IX, PAD + IY))
        pd = ImageDraw.Draw(post); bx0, by0 = PAD + 40, PAD + 780; pulse = 0.5 + 0.5 * math.sin((t - btn_at) * 7) if t > btn_at else 0
        pd.rounded_rectangle((bx0, by0, bx0 + 780, by0 + 84), 22, fill=ACC()); ctext(pd, bx0 + 390, by0 + 42, "Get a quote", A.font("bl", 38), WHITE)
        put(im, post, W / 2, cy, k, 1 + 0.012 * pulse)
        return im, 0
    ev = [(0.0, "pop", 0.6), (0.25, "swish", 0.5), (0.55, "swish", 0.6)] + [(build[0] + i * (build[1] - build[0]) / 14, "tick", 0.35) for i in range(14)] + \
         [(roof_at + 0.25, "hit", 0.8), (door_at + 0.2, "pop", 0.6), (btn_at, "ping", 0.6)]
    return dur, fn, ev


# ======================================================================= 07 BODY 3  (step 2: ask first, step 3: pipeline)
def scene_ask_pipeline(dur=6.6, taps=(1.25, 1.85, 2.45), verdict_at=2.85, swap=3.45, moves=(3.9, 4.5, 5.1, 5.7)):
    """02 - ASK FIRST: a quick form; a finger taps one answer per row (planning, budget, start) -> 'Ready to build'.
    03 - YOUR PIPELINE: a board (Enquiry / Site visit / Quote / Booked); the new enquiry card slides column to column
    and gets stamped BOOKED."""
    la, lb = label("02 — ASK FIRST"), label("03 — YOUR PIPELINE")
    a1, a2 = KLine("Before they ring you,", 76), KLine("they answer 3 questions.", 76, key="3 questions.")
    b1, b2 = KLine("Every enquiry lands in a pipeline", 64), KLine("you can see weeks ahead.", 76, key="weeks ahead.")
    rows = [("PLANNING?", ["Granted", "Applied", "Not yet"], 0), ("BUDGET?", ["Under €30k", "€30–60k", "€60k+"], 2), ("START?", ["ASAP", "Spring", "Just looking"], 1)]
    FX, FY, FW_, FH = W / 2, 1060, 900, 660; RY = [FY - FH / 2 + 90 + i * 200 for i in range(3)]; SEG_W = 800 / 3
    verdict = shadowed(A.pill("Ready to build  ✓", 50, ACC(), WHITE, w="bl"), blur=18, dy=10, alpha=50, pad=40)
    COLS_ = ["ENQUIRY", "SITE VISIT", "QUOTE", "BOOKED"]; KW, KX0 = 228, 72; KX = [KX0 + i * (KW + 8) + KW / 2 for i in range(4)]
    static = [(0, "Attic", "Naas"), (0, "Porch", "Bray"), (1, "Garage", "Ennis"), (2, "Kitchen ext.", "Lucan"), (3, "Extension", "Lucan")]
    def kcard(a, b, hl=False):
        def dr(d, s):
            d.text((20 * s, 16 * s), a, font=A.font("b", 30 * s), fill=INK); d.text((20 * s, 56 * s), b, font=A.font("m", 24 * s), fill=MUTED)
            if hl: d.rounded_rectangle((2 * s, 2 * s, 206 * s, 94 * s), 18 * s, outline=ACC(), width=5 * s)
        return card(208, 96, dr, r=18)
    SC = [kcard(a, b) for _, a, b in static]; MOVER = kcard("Extension", "Swords", True); bst = stamp("BOOKED", 30)
    form = card(FW_, FH, r=36)

    def fn(t):
        im = A.bg(); sh = 0
        if t < swap + 0.3:  # ---- STEP 2
            out = eio((t - swap) / 0.3); dx = -1200 * out
            put(im, la, W / 2 + dx, 330, eo(t / 0.25)); a1.draw(im, W / 2 + dx, 425, (t - 0.1) / 0.3); a2.draw(im, W / 2 + dx, 515, (t - 0.25) / 0.3, (t - 0.55) / 0.4)
            k = eo((t - 0.2) / 0.45); put(im, form, FX + dx, FY + 140 * (1 - k), k)
            if k > 0.6:
                d = ImageDraw.Draw(im)
                for i, (q, opts, pick) in enumerate(rows):
                    y = RY[i] + 140 * (1 - k); d.text((FX - 400 + dx, y - 50), q, font=A.font("monob", 26), fill=MUTED)
                    for j, o in enumerate(opts):
                        x0 = FX - 400 + j * SEG_W + dx; on = j == pick and t >= taps[i]
                        d.rounded_rectangle((x0 + 4, y - 10, x0 + SEG_W - 4, y + 76), 20, fill=ACC() if on else (244, 242, 238), outline=None if on else LINE, width=2)
                        ctext(d, x0 + SEG_W / 2, y + 33, o, A.font("b", 32), WHITE if on else INK)
                for i, (q, opts, pick) in enumerate(rows): A.tap(im, FX - 400 + pick * SEG_W + SEG_W / 2 + 60 + dx, RY[i] + 50, t, taps[i], t_in=0.4, t_out=0.35, from_dx=120, from_dy=200)
            vk = (t - verdict_at) / 0.35
            if vk > 0: put(im, verdict, W / 2 + dx, 1480, clamp(vk / 0.2), 0.7 + 0.3 * back(vk))
            if verdict_at <= t < verdict_at + 0.14: sh = 8
        if t >= swap:  # ---- STEP 3
            u = t - swap; dx = 1200 * (1 - eio(u / 0.3))
            put(im, lb, W / 2 + dx, 330, 1); b1.draw(im, W / 2 + dx, 425, (u - 0.05) / 0.3); b2.draw(im, W / 2 + dx, 515, (u - 0.2) / 0.3, (u - 0.5) / 0.4)
            d = ImageDraw.Draw(im)
            for i, c in enumerate(COLS_):
                x = KX[i] + dx; d.rounded_rectangle((x - KW / 2, 640, x + KW / 2, 1300), 24, fill=COL)
                ctext(d, x, 690, c, A.font("monob", 24), ACC() if i == 3 else MUTED)
            counts = [0, 0, 0, 0]
            for (ci, a, b), sp in zip(static, SC):
                put(im, sp, KX[ci] + dx, 790 + counts[ci] * 120, 1); counts[ci] += 1
            # mover: enters ENQUIRY, then slides one column per move
            col = sum(1 for m in moves[1:] if t >= m); fx = KX[col]
            if col < 3 and t >= moves[col + 1] - 0.45: pass
            for i in range(1, 4):
                if moves[i] - 0.35 <= t < moves[i]: f = eio((t - moves[i] + 0.35) / 0.35); fx = KX[i - 1] + (KX[i] - KX[i - 1]) * f
            fy = 790 + counts[min(col, 3)] * 120 if t >= moves[0] else 790
            ek = (t - moves[0]) / 0.4
            if ek > 0:
                lift = 1.06 if any(moves[i] - 0.35 <= t < moves[i] for i in range(1, 4)) else 1
                put(im, MOVER, fx + dx, fy - 200 * (1 - eo(ek)), clamp(ek / 0.2), lift)
                if t >= moves[3]:
                    sk = (t - moves[3] - 0.1) / 0.3; put(im, bst, fx + dx, fy + 92, clamp(sk / 0.15), 1.6 - 0.6 * eo(sk), -8)
                    ring(im, fx, fy, (t - moves[3]) / 1.2, col=ACC(), maxr=260, width=5, r0=60)
                    if moves[3] + 0.1 <= t < moves[3] + 0.24: sh = 8
        return im, sh
    ev = [(0.0, "pop", 0.6), (0.25, "swish", 0.5), (0.55, "swish", 0.6)] + [(x, "click", 0.9) for x in taps] + [(verdict_at, "hit", 0.8),
          (swap, "whoosh", 0.7), (swap + 0.5, "swish", 0.6), (moves[0], "pop", 0.7)] + [(m - 0.35, "swish", 0.5) for m in moves[1:]] + [(moves[3] + 0.1, "hit", 1.0), (moves[3] + 0.15, "shimmer", 0.6)]
    return dur, fn, ev
