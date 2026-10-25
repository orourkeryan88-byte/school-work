"""DENTAL ad 'The Report': clinical white, teal, monospaced numbers. Precise, mechanical motion: counters, highlighter
swipes, a red pen circle, a funnel that gets cut off, then counts all the way to the chair. No glitch, no shake.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, pill, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed

RED = (226, 54, 54); HL = (255, 230, 90)
NAVY = lambda: A.TH["ink"]


def headline(im, lines, t, y0, size=96, t0=0.0, step=0.12):
    """left-aligned clinical headline; second line teal. masked rise"""
    for j, (s, teal) in enumerate(lines):
        sp = text(s, "bl", fit_size(s, "bl", size, 960), A.TH["accent"] if teal else None)
        put_rise(im, sp, 60 + sp.width / 2, y0 + j * size * 1.1, eo((t - t0 - j * step) / 0.25))


def ruled_card(w, h, rows, title, sub, counts, hl=(), pen=None, done=None, example=False):
    """report document: title, rows of (label, value) with mono numbers; hl = row indexes with highlighter (0..1 progress),
    pen = (row, progress) red ellipse; done = {row: progress} teal ticks"""
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 26 * s, fill=WHITE_, outline=(214, 222, 228), width=2 * s)
        d.rectangle((0, 0, w * s, 14 * s), fill=A.TH["accent"])
        d.text((50 * s, 50 * s), title, font=A.font("b", 30 * s), fill=(110, 128, 140))
        d.text((50 * s, 92 * s), sub, font=A.font("bl", 46 * s), fill=A.TH["ink"])
        if example:
            f = A.font("b", 24 * s); tw = A.tsize("EXAMPLE", f)[0]
            d.rounded_rectangle(((w - 50) * s - tw - 40 * s, 52 * s, (w - 50) * s, 92 * s), 20 * s, fill=(232, 240, 242)); d.text(((w - 50) * s - tw - 20 * s, 58 * s), "EXAMPLE", font=f, fill=(110, 128, 140))
        for i, (lab, val) in enumerate(rows):
            y = 190 + i * 110
            hp = dict(hl).get(i, 0)
            if hp > 0: d.rounded_rectangle((36 * s, (y - 8) * s, (36 + (w - 72) * hp) * s, (y + 72) * s), 12 * s, fill=HL + (170,))
            d.text((50 * s, (y + 12) * s), lab, font=A.font("sb", 40 * s), fill=A.TH["ink"])
            v = counts.get(i, val) if counts else val
            f = A.font("monob", 46 * s); tw = A.tsize(v, f)[0]; d.text(((w - 50) * s - tw, (y + 8) * s), v, font=f, fill=RED if v in ("—", "?") else A.TH["ink"])
            if done and done.get(i, 0) > 0:
                k = done[i]; cx, cy = (w - 50 - tw / s - 60), y + 34
                d.ellipse(((cx - 24 * k) * s, (cy - 24 * k) * s, (cx + 24 * k) * s, (cy + 24 * k) * s), fill=A.TH["accent"])
                if k > 0.8: d.line(((cx - 10) * s, cy * s, (cx - 2) * s, (cy + 9) * s, (cx + 12) * s, (cy - 9) * s), fill=(255, 255, 255), width=5 * s)
            d.line((50 * s, (y + 90) * s, (w - 50) * s, (y + 90) * s), fill=(230, 236, 240), width=2 * s)
        if pen:
            row, p = pen; y = 190 + row * 110 + 34; cx, rx, ry = w - 200, 190, 70
            pts = [(cx + rx * math.cos(a) * 1.02 ** (a), y + ry * math.sin(a)) for a in [-0.4 + 6.9 * p * j / 60 for j in range(61)]]
            if len(pts) > 1: d.line([(x * s, yy * s) for x, yy in pts], fill=RED, width=7 * s, joint="curve")
    return shadowed(sprite(w, h, fn), blur=30, dy=18, alpha=40)

WHITE_ = (255, 255, 255)


def tooth(d, cx, cy, sc, col):
    """simple tooth glyph"""
    d.rounded_rectangle((cx - 60 * sc, cy - 60 * sc, cx + 60 * sc, cy + 10 * sc), 40 * sc, fill=col)
    d.polygon([(cx - 56 * sc, cy), (cx - 40 * sc, cy + 70 * sc), (cx - 14 * sc, cy + 70 * sc), (cx, cy + 20 * sc), (cx + 14 * sc, cy + 70 * sc),
               (cx + 40 * sc, cy + 70 * sc), (cx + 56 * sc, cy)], fill=col)


# ---------------------------------------------------------------- HOOK
def scene_report_hook(word="Dentists,", dur=3.6, hl_at=0.75, pen_at=1.75, q_at=2.3):
    """frame 0: 'Dentists,' + the agency's monthly report with big vanity numbers already rolling.
    Highlighter swipes the vanity rows, a red pen circles the empty 'New patients booked' row, then the question lands."""
    big = text(word, "bl", fit_size(word, "bl", 210, 960))
    rows = [("Impressions", "48,213"), ("Reach", "21,904"), ("Link clicks", "1,206"), ("Post likes", "312"), ("New patients booked", "—")]
    targets = [48213, 21904, 1206, 312]; cache = {}
    q1 = text("HOW MANY OF THESE", "bl", 76); q2 = text("BOOKED A CONSULT?", "bl", 92, A.TH["accent"])

    def fn(t):
        im = A.bg()
        put(im, big, 60 + big.width / 2, 345, 1, 1.0)
        ImageDraw.Draw(im).rectangle((60, 425, 60 + big.width * eo(0.5 + t / 0.4), 437), fill=A.TH["accent"])
        roll = eo(0.55 + t / 0.7)  # numbers already well underway on frame 0
        counts = {i: f"{int(v * roll):,}" for i, v in enumerate(targets)}
        hl = tuple((i, clamp((t - hl_at - i * 0.18) / 0.22)) for i in range(4))
        pen = (4, clamp((t - pen_at) / 0.45)) if t >= pen_at else None
        key = (tuple(counts.values()), tuple(round(h, 2) for _, h in hl), pen and round(pen[1], 2))
        if key not in cache: cache.clear(); cache[key] = ruled_card(940, 760, rows, "MONTHLY MARKETING REPORT", "October results", counts, hl, pen)
        put(im, cache[key], W / 2, 900, 1, 1, -1.5)
        if t >= q_at:
            put_rise(im, q1, 60 + q1.width / 2, 1390, eo((t - q_at) / 0.25)); put_rise(im, q2, 60 + q2.width / 2, 1490, eo((t - q_at - 0.15) / 0.25))
        return im, 0
    return dur, fn, [(0.0, "hit", 0.9)] + [(i * 0.07, "tick", 0.35) for i in range(9)] + [(hl_at + i * 0.18, "swish", 0.35) for i in range(4)] + \
        [(pen_at, "swish", 0.6), (pen_at + 0.45, "pop", 0.7), (q_at, "whoosh", 0.4), (q_at + 0.15, "hit", 0.7)]


# ---------------------------------------------------------------- OPEN LOOP: the magnifier
def scene_magnifier(dur=3.2, swap_at=1.6):
    """the report blurs back; a magnifying lens glides to the blank row and shows NOT TRACKED inside;
    headline asks what the report is hiding"""
    rows = [("Impressions", "48,213"), ("Reach", "21,904"), ("Link clicks", "1,206"), ("Post likes", "312"), ("New patients booked", "—")]
    card = ruled_card(940, 760, rows, "MONTHLY MARKETING REPORT", "October results", None)
    base = A.bg(); put(base, card, W / 2, 1000, 1, 1, -1.5); blur = base.filter(ImageFilter.GaussianBlur(8))
    big = base.resize((W * 2, H * 2), Image.LANCZOS)
    nt = text("NOT TRACKED", "monob", 54, RED)

    def fn(t):
        im = blur.copy()
        headline(im, (("IF YOUR REPORT", False), ("CAN'T ANSWER THAT…", True)) if t < swap_at else (("HERE'S WHAT", False), ("IT'S HIDING.", True)),
                 t, 300, 92, 0 if t < swap_at else swap_at)
        p = eio(t / 1.1); lx = 300 + (880 - 300) * p; ly = 760 + (1284 - 760) * p  # glide onto the blank 'New patients booked' value
        r = 210; m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse((lx - r, ly - r, lx + r, ly + r), fill=255)
        z = big.crop((int(lx * 2 - lx), int(ly * 2 - ly), int(lx * 2 - lx) + W, int(ly * 2 - ly) + H))  # 2x zoom centred on the lens
        im.paste(z, (0, 0), m)
        d = ImageDraw.Draw(im); d.ellipse((lx - r, ly - r, lx + r, ly + r), outline=A.TH["ink"], width=14)
        d.line((lx + r * 0.7, ly + r * 0.7, lx + r * 1.35, ly + r * 1.35), fill=A.TH["ink"], width=26)
        if t > 1.2: put(im, nt, lx, ly + r + 70, clamp((t - 1.2) / 0.2), 1.3 - 0.3 * eo((t - 1.2) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.5), (1.15, "pop", 0.8), (1.2, "hit", 0.6), (swap_at, "swish", 0.4)]


# ---------------------------------------------------------------- BODY 1: the funnel that stops counting
STAGES = [("Saw the ad", 48213), ("Clicked", 1206), ("Filled in the form", 64), ("Booked a consult", 31), ("Started treatment", 12)]


def funnel(im, t, on_at, reveal_from):
    """horizontal funnel bars drawing in from reveal_from; stage i shows teal + counts up from on_at[i] (None = grey '?')"""
    d = ImageDraw.Draw(im); maxw = 900
    for i, (lab, v) in enumerate(STAGES):
        y = 640 + i * 175; wv = (900, 830, 760, 700, 650)[i]; k = eo((t - reveal_from - i * 0.14) / 0.4)
        if k <= 0: continue
        on = on_at[i] is not None and t >= on_at[i]; col = A.TH["accent"] if on else (214, 222, 228)
        x0 = W / 2 - wv / 2; d.rounded_rectangle((x0, y - 60, x0 + wv * k, y + 60), 30, fill=col)
        put(im, text(lab, "b", 40, (255, 255, 255) if on else (120, 134, 146)), x0 + 40 + text(lab, "b", 40).width / 2, y, clamp(k * 2))
        val = f"{int(v * eo((t - on_at[i]) / 0.7)):,}" if on else "?"
        sp = text(val, "monob", 50, (255, 255, 255) if on else RED); put(im, sp, x0 + wv - 40 - sp.width / 2, y, clamp(k * 2))
        if on and i >= 2: ring(im, x0 + wv - 80, y, (t - on_at[i]) / 0.8, maxr=160, width=4, r0=30)


def scene_funnel_cut(dur=5.4, reveal_from=0.25, cut_at=1.9, swap_at=3.3):
    """funnel draws stage by stage; a red dashed scissor line slices under 'Clicked': MOST REPORTS STOP HERE;
    the lower stages grey out with '?'; headline lands: LIKES DON'T FILL CHAIRS."""
    tag = pill("MOST REPORTS STOP HERE", 34, RED, (255, 255, 255), w="bl")

    def fn(t):
        im = A.bg()
        headline(im, (("WHERE MOST AGENCIES", False), ("STOP COUNTING.", True)) if t < swap_at else (("LIKES DON'T", False), ("FILL CHAIRS.", True)),
                 t, 300, 96, 0 if t < swap_at else swap_at)
        funnel(im, t, [reveal_from, reveal_from + 0.14, None, None, None], reveal_from)
        if t >= cut_at:
            k = eo((t - cut_at) / 0.35); y = 640 + 175 + 88; d = ImageDraw.Draw(im)
            for x in range(40, int(40 + (W - 80) * k), 46): d.line((x, y, x + 26, y), fill=RED, width=8)
            put(im, tag, W / 2, y + 2, clamp((t - cut_at - 0.2) / 0.2), 1.2 - 0.2 * eo((t - cut_at - 0.2) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(reveal_from + i * 0.14, "pop", 0.45) for i in range(5)] + \
        [(cut_at, "swish", 0.9), (cut_at + 0.2, "hit", 0.8), (swap_at, "whoosh", 0.4)]


def scene_count_to_chair(dur=5.0, light_at=0.5):
    """same funnel, now every stage counted in teal down to 'Started treatment', with a tooth glowing at the end"""
    def fn(t):
        im = A.bg()
        headline(im, (("WE COUNT ALL THE", False), ("WAY TO THE CHAIR.", True)), t, 300, 96)
        funnel(im, t, [-9, -9, light_at, light_at + 0.35, light_at + 0.7], -9)  # bars already drawn; lower stages light up in turn
        g = clamp((t - light_at - 1.1) / 0.4)
        if g > 0:
            d = ImageDraw.Draw(im); tooth(d, W / 2, 1560, 0.8 + 0.2 * spring(g), A.TH["accent"])
        put(im, pill("EXAMPLE NUMBERS", 26, (232, 240, 242), (110, 128, 140), w="b"), W - 190, 560, eo(t / 0.3))
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(light_at + i * 0.35, "ping", 0.6) for i in range(3)] + [(light_at + 1.1, "shimmer", 0.7), (light_at + 1.1, "hit", 0.6)]


# ---------------------------------------------------------------- the report it should be
def scene_better_report(dur=3.8):
    rows = [("Consult requests", "64"), ("Consults booked", "31"), ("Treatments started", "12"), ("Cost per booked consult", "tracked"), ("Revenue from ads", "tracked")]
    T = [0.6 + i * 0.32 for i in range(5)]; cache = {}

    def fn(t):
        im = A.bg()
        headline(im, (("YOUR REPORT,", False), ("THE WAY IT SHOULD BE.", True)), t, 300, 92)
        done = {i: clamp((t - T[i]) / 0.25) for i in range(5)}
        key = tuple(round(v, 2) for v in done.values())
        if key not in cache: cache.clear(); cache[key] = ruled_card(940, 760, rows, "SOUTHLINE MONTHLY REPORT", "Patients, not likes", None, done=done, example=True)
        k = eo(t / 0.45); put(im, cache[key], W / 2 + 500 * (1 - k), 1020, 1, 1, 1.5 * k)
        return im, 0
    return dur, fn, [(0.0, "swish", 0.7)] + [(x, "pop", 0.6) for x in T] + [(T[-1] + 0.25, "coin", 0.6)]


# ---------------------------------------------------------------- CTA: logo stamped like a seal
def scene_report_cta(logo, dur=4.2, stamp_at=0.9, type_at=1.6, keyword="REPORT"):
    big1 = text("Want a report that", "bl", 76); big2 = text("counts patients,", "bl", 92, A.TH["accent"]); big3 = text("not likes?", "bl", 92)
    lg = logo.resize((260, 260), Image.LANCZOS)
    brand = text("SOUTHLINE AGENCY", "bl", 52); sub = text("Paid ads for Irish dental clinics", "m", 34, A.TH["muted"])
    TY = type_at; CH = 0.09

    def fn(t):
        im = A.bg()
        put_rise(im, big1, 60 + big1.width / 2, 340, eo(t / 0.25)); put_rise(im, big2, 60 + big2.width / 2, 440, eo((t - 0.12) / 0.25)); put_rise(im, big3, 60 + big3.width / 2, 545, eo((t - 0.24) / 0.25))
        # the comment field
        d = ImageDraw.Draw(im); y = 780; n = int(clamp((t - TY) / CH, 0, len(keyword)))
        d.rounded_rectangle((60, y - 80, W - 60, y + 80), 28, fill=(255, 255, 255), outline=A.TH["accent"] if t >= TY else (214, 222, 228), width=5)
        d.text((100, y - 60), "Comment", font=A.font("sb", 30), fill=(110, 128, 140))
        d.text((100, y - 22), keyword[:n], font=A.font("monob", 64), fill=A.TH["ink"])
        if int(t * 3) % 2 == 0 or TY <= t < TY + 0.9: cx = 100 + A.tsize(keyword[:n], A.font("monob", 64))[0] + 14 if n else 100; d.rectangle((cx, y - 18, cx + 6, y + 50), fill=A.TH["accent"])
        # logo stamped like a seal
        if t >= stamp_at:
            k = (t - stamp_at) / 0.3; put(im, lg, W / 2, 1190, clamp(k / 0.15), 1.6 - 0.6 * eo(k), -8 * (1 - eo(k)))
            ring(im, W / 2, 1190, k / 1.4, maxr=420, width=6, r0=130)
        c = eo((t - stamp_at - 0.3) / 0.4); put(im, brand, W / 2, 1400 + 20 * (1 - c), c); put(im, sub, W / 2, 1470 + 20 * (1 - c), c)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4), (stamp_at, "hit", 1.0), (stamp_at + 0.05, "coin", 0.6)] + [(TY + i * CH, "tick", 0.5) for i in range(len(keyword))] + [(TY + len(keyword) * CH + 0.2, "ping", 0.7)]
