"""HOMEOWNER ad for a builder client (Ryan hands this to the builder to run): extensions, aimed at homeowners who've
outgrown the house. Hook (outgrown it, can't face moving), pains (no call-backs, quotes that grow, jobs that drag),
the fix (the extension builds itself onto the house), the offer card, then a lead form being filled + 'Fill out the
form below' with an arrow pointing at the Meta form button. Navy + amber, no business name (the Page name shows).
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed

WHITE = (255, 255, 255); RED = (235, 80, 80)
def ACC(): return A.TH["accent"]
def INK(): return A.TH["ink"]

def T(s, size, col=None, w="bl", maxw=960):
    return text(s, w, fit_size(s, w, size, maxw), col or INK())

def card(w, h, draw=None, fill=WHITE, r=30):
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill)
        if draw: draw(d, s)
    return shadowed(sprite(w, h, fn), blur=26, dy=14, alpha=140, pad=50)

def ctext(d, x, y, s_, f, col):
    tw, th, ox, oy = A.tsize(s_, f); d.text((x - tw / 2 - ox, y - th / 2 - oy), s_, font=f, fill=col)

def rise(im, sp, x, y, t, t0):
    if t >= t0: put_rise(im, sp, x, y, eo((t - t0) / 0.3))

def pop(im, sp, x, y, t, t0, big=1.4):
    k = (t - t0) / 0.35
    if k > 0: put(im, sp, x, y, clamp(k / 0.15), big - (big - 1) * back(k))

def swipe(im, s_, size, cx, cy, p, w="bl"):
    """highlighter swipe behind a line of text (drawn before the text)"""
    if p <= 0: return
    f = A.font(w, fit_size(s_, w, size)); tw = f.getlength(s_); x0 = cx - tw / 2 - 14
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).rounded_rectangle((x0, cy - size * 0.36, x0 + (tw + 28) * eo(p), cy + size * 0.5), 12, fill=ACC() + (110,))
    im.alpha_composite(o)


# ======================================================================= house drawing
def house(d, cx, base, s=1.0, ext=0.0, people=0, col=(236, 228, 214), roof=(70, 78, 98)):
    """semi-d house standing on y=base; ext 0..1 builds a single-storey rear/side extension out to the right,
    brick course by course; people = how many little figures squeezed inside the window"""
    w, h = 360 * s, 300 * s; x0 = cx - w / 2
    d.rectangle((x0, base - h, x0 + w, base), fill=col)
    d.polygon([(x0 - 20 * s, base - h), (cx, base - h - 170 * s), (x0 + w + 20 * s, base - h)], fill=roof)
    d.rectangle((cx - 40 * s, base - 120 * s, cx + 40 * s, base), fill=(120, 86, 60))           # door
    for wx in (x0 + 40 * s, x0 + w - 130 * s):
        d.rectangle((wx, base - h + 40 * s, wx + 90 * s, base - h + 120 * s), fill=(170, 200, 230))
    if people:  # the family outside the front door, spilling past the walls as more arrive
        fam = [(1.0, (60, 110, 190)), (0.95, (220, 90, 90)), (0.6, (90, 170, 110)), (0.55, (240, 180, 60)), (0.45, (150, 100, 190)), (0.8, (70, 160, 170))]
        for i in range(people):
            hgt, shirt = fam[i]; off = ((i + 1) // 2) * (1 if i % 2 else -1) * 78 * s
            px = cx + off; top = base - 150 * s * hgt
            d.ellipse((px - 17 * s * hgt, top - 34 * s * hgt, px + 17 * s * hgt, top), fill=(232, 188, 150))
            d.rounded_rectangle((px - 22 * s * hgt, top + 2 * s, px + 22 * s * hgt, base - 50 * s * hgt), int(10 * s), fill=shirt)
            d.rectangle((px - 16 * s * hgt, base - 52 * s * hgt, px + 16 * s * hgt, base), fill=(50, 56, 80))
    if ext > 0:  # extension: walls rise in courses, then the flat roof + glass doors land
        ew, eh = 300 * s, 190 * s; ex0 = x0 + w; courses = 12
        n = int(courses * clamp(ext / 0.75))
        for i in range(n):
            y1 = base - (i + 1) * eh / courses; y0 = base - i * eh / courses
            d.rectangle((ex0, y1, ex0 + ew, y0), fill=(214, 120, 84) if i % 2 == 0 else (200, 110, 76))
            for bx in range(int(6 if i % 2 == 0 else 5)):
                xx = ex0 + (bx + (0.5 if i % 2 else 0)) * ew / 6; d.line((xx, y1, xx, y0), fill=(170, 92, 64), width=max(1, int(2 * s)))
        if ext > 0.8:
            k = clamp((ext - 0.8) / 0.2); d.rectangle((ex0 - 6 * s, base - eh - 22 * s, ex0 + ew + 14 * s, base - eh), fill=(60, 66, 84))
            gw = (ew - 80 * s) * k; d.rectangle((ex0 + 40 * s, base - eh + 40 * s, ex0 + 40 * s + gw, base - 4 * s), fill=(170, 210, 240))
            for j in range(3):
                xx = ex0 + 40 * s + j * (ew - 80 * s) / 3
                if xx < ex0 + 40 * s + gw: d.line((xx, base - eh + 40 * s, xx, base - 4 * s), fill=(60, 66, 84), width=max(2, int(4 * s)))
    d.rectangle((cx - 600, base, cx + 600, base + 14 * s), fill=(110, 140, 90))                     # grass line


# ======================================================================= scenes
def scene_hook(dur=3.6, l1_at=0.15, house_at=0.2, squeeze=(0.6, 1.4), l2_at=1.6):
    """'Outgrown your house…' slams; the family gathers outside a little house, spilling past its walls;
    '…but can't face moving?' rises with a highlighter swipe"""
    l1 = T("Outgrown your house…", 96, WHITE); l2 = T("…but can't face moving?", 84, WHITE)
    def fn(t):
        im = A.bg(); sh = 12 if l1_at <= t < l1_at + 0.13 else 0
        if t >= l1_at: put(im, l1, W / 2, 470, clamp((t - l1_at) / 0.1), 1.35 - 0.35 * back((t - l1_at) / 0.35))
        if t >= house_at:
            k = spring((t - house_at) / 0.6, f=1.4, d=6); n = 1 + int(5 * clamp((t - squeeze[0]) / (squeeze[1] - squeeze[0])))
            o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o); wob = 4 * math.sin(t * 22) * clamp((t - squeeze[0]) / 0.3) * (n >= 4)
            house(d, W / 2 + wob, 1250 + 500 * (1 - k), 1.25, people=n); im.alpha_composite(o)
        if t >= l2_at: swipe(im, "…but can't face moving?", 84, W / 2, 1460, (t - l2_at - 0.3) / 0.4)
        rise(im, l2, W / 2, 1460, t, l2_at)
        return im, sh
    return dur, fn, [(l1_at, "hit", 0.9), (house_at, "whoosh", 0.4)] + [(squeeze[0] + i * 0.2, "pop", 0.45) for i in range(4)] + [(l2_at, "swish", 0.5), (l2_at + 0.3, "swish", 0.4)]


def scene_pains(dur=5.4, h_at=0.1, rows_at=(0.8, 1.6, 2.4), strike=(1.25, 2.05, 2.85), tag_at=3.7):
    """'Most people put it off because of…' then three pain rows drop in, each with a little shake:
    builders who don't call back / quotes that keep growing / jobs that drag on for months"""
    h1, h2 = T("Most people put it off", 78, WHITE), T("because of…", 78, WHITE)
    pains = [("☎", "Builders who don't call back"), ("€", "Quotes that keep growing"), ("clock", "Jobs that drag on for months")]
    def row(icon, s_):
        def dr(d, s):
            d.ellipse((26 * s, 22 * s, 106 * s, 102 * s), fill=(250, 232, 228))
            if icon == "clock":
                d.ellipse((44 * s, 40 * s, 88 * s, 84 * s), outline=RED, width=6 * s); d.line((66 * s, 62 * s, 66 * s, 48 * s), fill=RED, width=5 * s); d.line((66 * s, 62 * s, 78 * s, 66 * s), fill=RED, width=5 * s)
            else: ctext(d, 66 * s, 62 * s, icon, A.font("DejaVuSans-Bold.ttf", 44 * s), RED)
            d.text((132 * s, 38 * s), s_, font=A.font("bl", 44 * s), fill=(24, 26, 34))
        return card(900, 124, dr, r=28)
    rows = [row(*p) for p in pains]; tag = T("Sound familiar?", 72, ACC())
    def fn(t):
        im = A.bg(); rise(im, h1, W / 2, 380, t, h_at); rise(im, h2, W / 2, 475, t, h_at + 0.2)
        for i, (r_, t0, ts) in enumerate(zip(rows, rows_at, strike)):
            k = (t - t0) / 0.5
            if k <= 0: continue
            y = 720 + i * 210
            if ts <= t < ts + 0.25: y += 6 * math.sin((t - ts) * 60)  # a little shake as each one lands
            put(im, r_, W / 2, y - 260 * (1 - spring(k, f=1.4, d=6)), clamp(k / 0.2))
        rise(im, tag, W / 2, 1420, t, tag_at)
        return im, 0
    return dur, fn, [(h_at, "swish", 0.4), (h_at + 0.2, "swish", 0.4)] + [(x, "whoosh", 0.4) for x in rows_at] + [(x, "click", 0.4) for x in strike] + [(tag_at, "pop", 0.7)]


def scene_fix(dur=5.6, h_at=0.1, build=(0.6, 3.0), lines_at=(3.1, 3.5, 3.9)):
    """'So extend instead.' the extension builds itself course by course onto the house, roof and glass doors land;
    three promises tick in: one builder start to finish / a written quote / we answer the phone"""
    h1 = T("So extend instead.", 92, WHITE)
    checks = ["One builder, start to finish", "A clear, written quote", "We pick up the phone"]
    def chk(s_):
        f = A.font("bl", 44); tw = f.getlength(s_); w_, h_ = int(tw + 140), 96
        def dr(d, s, im_):
            d.rounded_rectangle((0, 0, w_ * s - 1, h_ * s - 1), 48 * s, fill=WHITE); d.ellipse((22 * s, 20 * s, 76 * s, 74 * s), fill=ACC())
            d.line([(36 * s, 48 * s), (46 * s, 60 * s), (64 * s, 36 * s)], fill=WHITE, width=7 * s, joint="curve"); d.text((96 * s, 22 * s), s_, font=f.font_variant(size=44 * s), fill=(24, 26, 34))
        return shadowed(sprite(w_, h_, dr), blur=18, dy=8, alpha=120, pad=36)
    C = [chk(c) for c in checks]
    def fn(t):
        im = A.bg(); rise(im, h1, W / 2, 360, t, h_at)
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        house(d, W / 2 - 150, 1000, 1.05, ext=eio((t - build[0]) / (build[1] - build[0]))); im.alpha_composite(o)
        if build[1] - 0.05 <= t: ring(im, W / 2 + 230, 900, (t - build[1]) / 1.0, col=ACC(), maxr=300, width=5, r0=60)
        for i, (c, t0) in enumerate(zip(C, lines_at)): pop(im, c, W / 2, 1200 + i * 125, t, t0, 1.3)
        return im, 0
    n = 12; ev = [(h_at, "swish", 0.4)] + [(build[0] + i * (build[1] - build[0]) * 0.75 / n, "tick", 0.3) for i in range(n)] + [(build[1] - 0.4, "hit", 0.6), (build[1], "shimmer", 0.5)]
    return dur, fn, ev + [(x, "pop", 0.6) for x in lines_at]


def scene_offer(offer_big, offer_sub, checks, dur=4.6, card_at=0.25, checks_at=(1.3, 1.65, 2.0)):
    """the offer card punches in with a shine: badge FREE, big line, sub line, three ticks"""
    def dr(d, s):
        d.rounded_rectangle((300 * s, 40 * s, 600 * s, 110 * s), 35 * s, fill=ACC()); ctext(d, 450 * s, 75 * s, "FREE", A.font("bl", 44 * s), (24, 26, 34))
        ctext(d, 450 * s, 200 * s, offer_big[0], A.font("bl", 76 * s), (24, 26, 34)); ctext(d, 450 * s, 290 * s, offer_big[1], A.font("bl", 76 * s), (24, 26, 34))
        ctext(d, 450 * s, 380 * s, offer_sub, A.font("m", 36 * s), (110, 116, 130))
    CARD = card(900, 700, dr, r=40)
    def fn(t):
        im = A.bg(); k = (t - card_at) / 0.45
        if k > 0:
            c = CARD.copy(); d = ImageDraw.Draw(c)
            for i, (s_, t0) in enumerate(zip(checks, checks_at)):
                if t >= t0:
                    a = clamp((t - t0) / 0.2); y = 50 + 470 + i * 70; x = 50 + 110
                    d.ellipse((x, y, x + 44, y + 44), fill=(34, 170, 92)); d.line([(x + 11, y + 23), (x + 19, y + 32), (x + 33, y + 14)], fill=WHITE, width=5)
                    d.text((x + 64, y + 2), s_, font=A.font("b", 36), fill=(24, 26, 34, int(255 * a)))
            if 0.3 < k < 1.8: c = A.shine(c, (k - 0.3) / 1.5)
            put(im, c, W / 2, 880, clamp(k / 0.2), 0.7 + 0.3 * back(k))
        return im, (10 if card_at <= t < card_at + 0.12 else 0)
    return dur, fn, [(card_at, "hit", 0.8), (card_at + 0.4, "shimmer", 0.5)] + [(x, "pop", 0.5) for x in checks_at]


def scene_form(answers, dur=6.0, form_at=0.2, ans_at=(1.0, 1.7, 2.4), cta_at=3.2, arrow_at=3.6):
    """a lead form slides up and fills itself in (what / where / when), then 'Fill out the form below' with a
    bouncing arrow pointing down at the Meta form button"""
    qs = [q for q, _ in answers]
    FW_, FH_ = 860, 640
    def base(d, s):
        d.rounded_rectangle((0, 0, FW_ * s, 100 * s), 30 * s, fill=ACC()); d.rectangle((0, 70 * s, FW_ * s, 100 * s), fill=ACC())
        ctext(d, FW_ / 2 * s, 52 * s, "Get your free quote", A.font("bl", 42 * s), (24, 26, 34))
        for i, q in enumerate(qs):
            y = (140 + i * 160) * s; d.text((50 * s, y), q, font=A.font("b", 32 * s), fill=(110, 116, 130))
            d.rounded_rectangle((50 * s, y + 48 * s, (FW_ - 50) * s, y + 118 * s), 18 * s, outline=(214, 218, 228), width=3 * s, fill=(248, 249, 252))
    FORM = card(FW_, FH_, base, r=30); l1, l2 = T("Fill out the", 88, WHITE), T("form below", 104, ACC())
    def fn(t):
        im = A.bg(); k = (t - form_at) / 0.6
        if k > 0:
            f = FORM.copy(); d = ImageDraw.Draw(f)
            for i, ((q, a), t0) in enumerate(zip(answers, ans_at)):
                n = int(clamp((t - t0) * 30, 0, len(a)))
                if n: d.text((50 + 80, 50 + 140 + i * 160 + 60), a[:n], font=A.font("bl", 38), fill=(24, 26, 34))
                if n == len(a): d.ellipse((50 + FW_ - 130, 50 + 140 + i * 160 + 62, 50 + FW_ - 90, 50 + 140 + i * 160 + 102), fill=(34, 170, 92))
            put(im, f, W / 2, 720 + 700 * (1 - spring(k, f=1.4, d=6)), clamp(k / 0.2), 0.92)
        rise(im, l1, W / 2, 1180, t, cta_at); rise(im, l2, W / 2, 1300, t, cta_at + 0.2)
        if t >= arrow_at:  # arrow bouncing down at the form button under the ad
            a = clamp((t - arrow_at) / 0.2); y = 1470 + 30 * abs(math.sin((t - arrow_at) * 5)); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
            d.rectangle((W / 2 - 14, y - 60, W / 2 + 14, y + 20), fill=ACC() + (int(255 * a),)); d.polygon([(W / 2 - 50, y + 10), (W / 2 + 50, y + 10), (W / 2, y + 70)], fill=ACC() + (int(255 * a),))
            im.alpha_composite(o)
        return im, 0
    ev = [(form_at, "whoosh", 0.5)] + [(t0 + j / 30, "tick", 0.18) for (q, a), t0 in zip(answers, ans_at) for j in range(0, len(a), 2)]
    return dur, fn, ev + [(t0 + len(a) / 30, "pop", 0.5) for (q, a), t0 in zip(answers, ans_at)] + [(cta_at, "swish", 0.5), (cta_at + 0.2, "hit", 0.7), (arrow_at, "pop", 0.6)]
