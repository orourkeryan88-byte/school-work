"""Volt scenes for the Southline plumbers "one builder" ad. Built on adkit primitives.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageChops, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, pill, fit_size, eo, eio, back, spring, clamp, ring, underline, sprite, shadowed

RED = (255, 72, 72); WHITE = A.WHITE
DARK = (12, 12, 9)
_volt_bg = None


def volt_bg():
    """full-screen volt gradient (used for 'dh' slam cards)"""
    global _volt_bg
    if _volt_bg is None:
        _volt_bg = A.gradient((W, H), A.TH["accent"], A.TH["accent2"], 90)
    return _volt_bg.copy()


def big_lines(s, style, maxw=900, start=300, max_h=980):
    """giant stacked type. s uses '|' for line breaks. style: d (white), y (volt gradient), dh (dark on volt)"""
    lines = s.split("|")
    size = min(fit_size(l, "bl", start, maxw) for l in lines)
    while size > 60 and len(lines) * size * 1.02 > max_h: size -= 6
    grad = (A.TH["accent"], A.TH["accent2"], 0) if style == "y" else None
    col = DARK if style == "dh" else A.TH["ink"]
    return [text(l, "bl", size, col, grad) for l in lines], size


def draw_lines(im, sps, cy, gap=0.98, scale=1.0):
    """centre a stack of line sprites on cy"""
    h = sum(sp.height * gap for sp in sps); y = cy - h / 2
    for sp in sps:
        put(im, sp, W / 2, y + sp.height * gap / 2, 1, scale); y += sp.height * gap


# ---------------------------------------------------------------- opener
def scene_one_builder(word="Plumbers,", l1="IF ONE BUILDER GIVES YOU", l2="MOST OF YOUR WORK…", dur=3.2):
    """frame 0: giant gradient trade word + a 'YOUR WORK' donut that's mostly one builder, both fully on screen mid-slam.
    The builder slice punches out and throbs, then the line rises in."""
    big = text(word, "bl", fit_size(word, "bl", 260, 940), grad=(A.TH["accent"], A.TH["accent2"], 0))
    s1 = text(l1, "xb", fit_size(l1, "xb", 76, 960)); s2 = text(l2, "xb", fit_size(l2, "xb", 76, 960), A.TH["accent"])
    CX, CY, R, RW = W / 2, 930, 250, 96
    frac = 0.84  # 'most of your work' (illustrative share, no number shown)
    centre = [text("YOUR", "bl", 64), text("WORK", "bl", 64)]
    tag = shadowed(pill("ONE BUILDER", 38, A.TH["accent"], w="bl"), blur=16, dy=10, alpha=90, pad=30)
    other = pill("EVERYONE ELSE", 26, (44, 46, 38), w="b")

    def ring_slice(a, b, ox=0, oy=0):
        """mask for a donut slice from angle a to b (pie slice minus the inner circle; wide PIL arcs draw unevenly)"""
        ss = 2; m = Image.new("L", (W * ss, H * ss), 0); d = ImageDraw.Draw(m); x, y = (CX + ox) * ss, (CY + oy) * ss
        d.pieslice((x - R * ss, y - R * ss, x + R * ss, y + R * ss), a, b, fill=255)
        r = (R - RW) * ss; d.ellipse((x - r, y - r, x + r, y + r), fill=0); return m

    def donut(pop):
        ss = 2; im = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
        a0 = -90 + 360 * frac  # the builder slice runs from 12 o'clock to a0, everyone else from a0 round to 12
        grey = Image.new("RGBA", im.size, (60, 62, 52, 255)); grey.putalpha(ring_slice(a0 + 2, 268)); im.alpha_composite(grey)
        mid = math.radians(-90 + 180 * frac); ox, oy = math.cos(mid) * pop, math.sin(mid) * pop
        g = A.gradient(im.size, A.TH["accent"], A.TH["accent2"], 0); g.putalpha(ring_slice(-90, a0 - 2, ox, oy))
        im.alpha_composite(g); return im.resize((W, H), Image.LANCZOS)
    cache = {}

    def fn(t):
        im = A.bg(); sh = 12 * (1 - t / 0.2) if t < 0.2 else 0
        # trade word: fully opaque on frame 0, settling from a slam
        put(im, big, W / 2, 420, 1, 1.06 - 0.06 * eo(t / 0.28))
        underline(im, big, W / 2, 420 + big.height / 2 + 2, 0.35 + (t - 0.05) / 0.3, h=14)
        # donut: builder slice punches out at 0.55s, then throbs
        pop = 0 if t < 0.55 else 26 * spring((t - 0.55) / 0.5) + 6 * math.sin((t - 0.55) * 9) * clamp((t - 0.9) / 0.3)
        key = round(pop)
        if key not in cache:
            dn = donut(key); gl = dn.filter(ImageFilter.GaussianBlur(30)); gl.putalpha(gl.split()[3].point(lambda v: v * 6 // 10))
            cache[key] = (dn, gl)
        dn, gl = cache[key]
        if t > 0.55: im.alpha_composite(gl)
        im.alpha_composite(dn)
        for i, sp in enumerate(centre): put(im, sp, CX, CY - 36 + i * 72, 1, 1.06 - 0.06 * eo(t / 0.3))
        ring(im, CX, CY, (t - 0.55) / 0.9, maxr=420, r0=R)
        put(im, tag, CX - 270, CY - R - 10, 1, (1 + 0.25 * (1 - eo((t - 0.55) / 0.3))) if t > 0.55 else 1, -6)
        put(im, other, CX + 300, CY - R + 40, clamp((t - 0.2) / 0.2), 1, 5)
        if 0.55 <= t < 0.7: sh = 8 * (1 - (t - 0.55) / 0.15)
        put_rise(im, s1, W / 2, 1330, eo((t - 0.75) / 0.32))
        put_rise(im, s2, W / 2, 1430, eo((t - 0.95) / 0.32))
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (0.55, "hit", 0.6), (0.55, "pop", 0.6), (0.75, "whoosh", 0.4)]


# ---------------------------------------------------------------- fast-cut slams
def scene_slam(parts, dur=2.4, lock_last=False, last_share=1.7):
    """giant fast-cut type. parts=[(text with | breaks, style d|y|dh)]. each part is a hard cut with a slam + hit.
    lock_last: the final card holds, then an underline locks it in with a click."""
    cards = [big_lines(s, st) for s, st in parts]
    wts = [len(s.replace("|", "")) + 6 for s, _ in parts]; wts[-1] *= last_share
    tot = sum(wts); cuts = [0.0]
    for w_ in wts[:-1]: cuts.append(cuts[-1] + dur * w_ / tot)

    def fn(t):
        i = max(k for k, c in enumerate(cuts) if t >= c); k = t - cuts[i]
        im = volt_bg() if parts[i][1] == "dh" else A.bg()
        sps, size = cards[i]
        draw_lines(im, sps, H / 2 - 40, scale=1.12 - 0.12 * eo(k / 0.14))
        if lock_last and i == len(parts) - 1:
            ref = max(sps, key=lambda s: s.width); h = sum(s.height * 0.98 for s in sps)
            underline(im, ref, W / 2, H / 2 - 40 + h / 2 + 10, (k - 0.3) / 0.25, DARK if parts[i][1] == "dh" else A.TH["accent"], h=18)
        sh = 14 * (1 - k / 0.16) if k < 0.16 else 0
        return im, sh
    ev = [(c, "hit", 1.0 if j == 0 else 0.75) for j, c in enumerate(cuts)] + [(c, "swish", 0.35) for c in cuts[1:]]
    if lock_last: ev.append((cuts[-1] + 0.3, "click", 0.9))
    return dur, fn, ev


def header(im, lines, t, y0=300, size=104, t0=0.0, step=0.12):
    """two-line reason header: first line white, second volt. masked rise"""
    for j, (s, col) in enumerate(lines):
        sp = text(s, "bl", fit_size(s, "bl", size, 980), A.TH["accent"] if col else None)
        put_rise(im, sp, W / 2, y0 + j * size * 1.08, eo((t - t0 - j * step) / 0.28))


# ---------------------------------------------------------------- he's busy / he's quiet
def scene_linked(dur=4.4, flip=2.1):
    """two diary meters chained together. his drains, yours follows. header swaps from busy to quiet"""
    A_lines = [("WHEN HE'S BUSY,", False), ("YOU'RE BUSY.", True)]
    B_lines = [("WHEN HE GOES QUIET…", False), ("SO DO YOU.", True)]
    BW, BH, TOP = 300, 680, 760; XS = (W / 2 - 220, W / 2 + 220)
    labs = [text("HIS DIARY", "xb", 40, A.TH["muted"]), text("YOUR DIARY", "xb", 40, A.TH["muted"])]

    def meter(im, x, level, t):
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((x - BW / 2, TOP, x + BW / 2, TOP + BH), 40, fill=A.TH["card"], outline=(60, 62, 52), width=3)
        col = A.TH["accent"] if level > 0.45 else (RED if level < 0.25 else (255, 170, 40))
        fh = (BH - 40) * level
        if fh > 4: d.rounded_rectangle((x - BW / 2 + 20, TOP + BH - 20 - fh, x + BW / 2 - 20, TOP + BH - 20), 26, fill=col)
        # day ticks so it reads like a diary
        for k in range(1, 5): d.line((x - BW / 2 + 20, TOP + 20 + k * (BH - 40) / 5, x + BW / 2 - 20, TOP + 20 + k * (BH - 40) / 5), fill=(0, 0, 0, 70), width=3)
        word = "FULL" if level > 0.45 else "EMPTY"; st = text(word, "bl", 64, DARK if level > 0.45 else A.TH["ink"])
        put(im, st, x, TOP + BH - 90 if level < 0.45 else TOP + BH - 20 - fh + 60, 1)

    def fn(t):
        im = A.bg(); sh = 0
        phase_b = t >= flip
        header(im, B_lines if phase_b else A_lines, t, 330, 104, flip if phase_b else 0)
        lv_him = 0.92 - 0.82 * eio((t - flip) / 0.7); lv_you = 0.92 - 0.82 * eio((t - flip - 0.45) / 0.7)
        bob = 0 if t > flip else math.sin(t * 6) * 0.02
        for x, lv, lab in zip(XS, (lv_him + bob, lv_you + bob), labs):
            meter(im, x, lv, t); put(im, lab, x, TOP + BH + 60, eo((t - 0.2) / 0.3))
        # chain between the meters
        d = ImageDraw.Draw(im); cy = TOP + BH / 2
        for k in range(4):
            cx = XS[0] + BW / 2 + 22 + k * 30; d.ellipse((cx - 20, cy - 13, cx + 20, cy + 13), outline=A.TH["accent"] if not phase_b else RED, width=7)
        if flip + 0.45 <= t < flip + 0.6: sh = 9
        if flip <= t < flip + 0.16: sh = 12 * (1 - (t - flip) / 0.16)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.6), (0.05, "pop", 0.6), (flip, "hit", 0.9), (flip + 0.45, "hit", 0.7), (flip + 0.2, "glitch", 0.4)]


# ---------------------------------------------------------------- his price
def scene_his_price(dur=4.2, your="€6,500", his="€4,800", job="Bathroom refit · 3-bed semi"):
    """your quote card gets struck through and HIS PRICE is stamped on it (illustrative numbers)"""
    def card_fn(d, s):
        d.text((56 * s, 50 * s), "YOUR QUOTE", font=A.font("b", 34 * s), fill=A.TH["muted"])
        d.text((56 * s, 100 * s), job, font=A.font("sb", 40 * s), fill=A.TH["card_ink"])
        d.text((56 * s, 180 * s), your, font=A.font("bl", 150 * s), fill=A.TH["card_ink"])
    card = A.card_sprite(900, 400, card_fn, outline=(60, 62, 52))
    stamp = sprite(560, 190, lambda d, s, im: (d.rounded_rectangle((0, 0, 560 * s - 1, 190 * s - 1), 26 * s, outline=RED, width=10 * s),
                                                d.text((40 * s, 22 * s), "HIS PRICE", font=A.font("bl", 46 * s), fill=RED),
                                                d.text((40 * s, 74 * s), his, font=A.font("bl", 96 * s), fill=RED)))
    sub = text("Because he knows you can't say no.", "xb", fit_size("Because he knows you can't say no.", "xb", 60, 960), A.TH["muted"])

    def fn(t):
        im = A.bg(); sh = 0
        header(im, [("YOU WORK AT", False), ("HIS PRICE.", True)], t, 330, 120)
        k = (t - 0.3) / 0.5; put(im, card, W / 2, 900 + 120 * (1 - eo(k)), clamp(k / 0.3), 0.92 + 0.08 * spring(k))
        sp = clamp((t - 1.1) / 0.25)
        if sp > 0: ImageDraw.Draw(im).line((W / 2 - 400, 990, W / 2 - 400 + 640 * eo(sp), 970), fill=RED, width=14)
        st = (t - 1.45) / 0.3
        if st > 0: put(im, stamp, W / 2 + 140, 1150, clamp(st / 0.15), 1.5 - 0.5 * eo(st), -8)
        if 1.45 <= t < 1.62: sh = 14 * (1 - (t - 1.45) / 0.17)
        put_rise(im, sub, W / 2, 1420, eo((t - 2.0) / 0.32))
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5), (0.3, "pop", 0.7), (1.1, "swish", 0.6), (1.45, "hit", 1.0), (2.0, "whoosh", 0.3)]


# ---------------------------------------------------------------- paid when he gets paid
def scene_invoice(dur=4.4, amount="€3,600", days=67):
    """invoice card: days-waiting counter rolls up, status flips to OVERDUE in red, progress bar fills red"""
    def base_fn(d, s):
        d.text((56 * s, 50 * s), "INVOICE #0418", font=A.font("b", 34 * s), fill=A.TH["muted"])
        d.text((56 * s, 100 * s), "Kitchen + 2 bathrooms · first fix", font=A.font("sb", 38 * s), fill=A.TH["card_ink"])
        d.text((56 * s, 170 * s), amount, font=A.font("bl", 130 * s), fill=A.TH["card_ink"])
        d.text((56 * s, 352 * s), "DAYS WAITING", font=A.font("b", 32 * s), fill=A.TH["muted"])
    card = A.card_sprite(900, 560, base_fn, outline=(60, 62, 52))
    sub = text("If he's slow paying, so are you.", "xb", fit_size("If he's slow paying, so are you.", "xb", 64, 960), A.TH["muted"])
    T0, T1 = 0.7, 2.6

    def fn(t):
        im = A.bg(); sh = 0
        header(im, [("YOU GET PAID WHEN", False), ("HE GETS PAID.", True)], t, 330, 104)
        k = (t - 0.25) / 0.5; cy = 960 + 120 * (1 - eo(k)); put(im, card, W / 2, cy, clamp(k / 0.3), 0.92 + 0.08 * spring(k))
        if k > 0.3:
            n = int(round(days * eio((t - T0) / (T1 - T0)))); over = n >= 45
            x0, y0 = W / 2 - 450 + 56, cy - 280 + 400
            d = ImageDraw.Draw(im)
            num = text(str(n), "bl", 96, RED if over else A.TH["ink"]); put(im, num, x0 + num.width / 2, y0 + 30)
            chip = pill("OVERDUE" if over else ("AWAITING PAYMENT" if n > 0 else "SENT"), 30, RED if over else (60, 62, 52), WHITE)
            put(im, chip, W / 2 + 450 - 56 - chip.width / 2, y0 + 30, 1, 1 + 0.25 * (1 - eo((t - (T0 + (T1 - T0) * 0.62)) / 0.25)) if over else 1)
            bx0, bx1, by = x0, W / 2 + 450 - 56, y0 + 110
            d.rounded_rectangle((bx0, by, bx1, by + 22), 11, fill=(50, 52, 44))
            d.rounded_rectangle((bx0, by, bx0 + max(22, (bx1 - bx0) * min(1, n / 60)), by + 22), 11, fill=RED if over else A.TH["accent"])
        put_rise(im, sub, W / 2, 1420, eo((t - 2.75) / 0.32))
        return im, sh
    ev = [(0.0, "whoosh", 0.5), (0.25, "pop", 0.7)] + [(T0 + i * 0.12, "tick", 0.35) for i in range(15)] + [(T0 + (T1 - T0) * 0.62, "glitch", 0.6), (T0 + (T1 - T0) * 0.62, "hit", 0.6), (2.75, "whoosh", 0.3)]
    return dur, fn, ev


# ---------------------------------------------------------------- own homeowners
def notif_v(title, body, age):
    """lock-screen enquiry notification with a water-drop tile (no brand logo before the CTA)"""
    w = 820
    def dr(d, s):
        d.rounded_rectangle((30 * s, 36 * s, 114 * s, 120 * s), 22 * s, fill=A.TH["accent"])
        bx, by = 72 * s, 80 * s
        d.polygon([(bx, by - 30 * s), (bx - 20 * s, by + 2 * s), (bx + 20 * s, by + 2 * s)], fill=DARK); d.ellipse((bx - 20 * s, by - 16 * s, bx + 20 * s, by + 24 * s), fill=DARK)
        d.text((140 * s, 34 * s), "NEW ENQUIRY", font=A.font("sb", 24 * s), fill=(120, 116, 108))
        d.text(((w - 40) * s - A.tsize(age, A.font("m", 24 * s))[0], 34 * s), age, font=A.font("m", 24 * s), fill=(120, 116, 108))
        d.text((140 * s, 72 * s), title, font=A.font("b", 38 * s), fill=(17, 17, 16))
        d.text((140 * s, 122 * s), body, font=A.font("m", 31 * s), fill=(80, 78, 72))
    sp = sprite(w, 186, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, 186 * s - 1), 44 * s, fill=(255, 255, 255, 250)), dr(d, s)))
    return shadowed(sp, blur=22, dy=14, alpha=45, pad=40)


def scene_own_leads(leads, dur=5.6, interval=0.5, k=0.74, top=640, crop=1610):
    """header + phone rising from the bottom (cropped with a fade), enquiries drop and stack, 'AT YOUR PRICE.' pops at the end"""
    ph0 = A.phone(date="Monday 26 October", wall=((34, 36, 24), (8, 8, 6), A.TH["accent"]))
    ages = ["now", "4m", "22m", "1h", "3h", "5h"]; cache = {}
    def N(i, r):
        if (i, r) not in cache: cache[(i, r)] = notif_v(*leads[i], ages[min(r, len(ages) - 1)])
        return cache[(i, r)]
    LT = [0.65 + i * interval for i in range(len(leads))]; END = LT[-1] + 0.55
    tagp = pill("BOILER SWAPS · BATHROOM REFITS", 34, (44, 46, 38), A.TH["accent"], w="b")
    price = shadowed(pill("AT YOUR PRICE.", 62, A.TH["accent"], w="bl"), blur=24, dy=14, alpha=120, pad=40)
    mask = Image.new("L", (W, H), 255); md = ImageDraw.Draw(mask)
    for y in range(crop - 160, H): md.line((0, y, W, y), fill=int(255 * clamp((crop - y) / 160)))

    def fn(t):
        im = A.bg(); arrived = [i for i, lt in enumerate(LT) if t >= lt]
        header(im, [("YOUR OWN", False), ("HOMEOWNERS.", True)], t, 300, 112)
        put(im, tagp, W / 2, 548, eo((t - 0.3) / 0.3), 0.9 + 0.1 * spring((t - 0.3) / 0.4))
        ph = ph0.copy(); nk = eo((t - LT[arrived[-1]]) / 0.38) if arrived else 0
        for rank, i in enumerate(reversed(arrived)):
            if rank == 0: kk = (t - LT[i]) / 0.42; cy = 640 - 140 * (1 - spring(kk)); al = clamp(kk / 0.15); sc = 0.9 + 0.1 * spring(kk)
            else: cy = 640 + (rank - 1) * 198 + 198 * nk; al = 1; sc = 1
            if cy > A.PH - 110: continue
            put(ph, N(i, rank), A.PW / 2, cy, al, sc)
        hap = 7 * math.sin((t - LT[arrived[-1]]) * 140) if arrived and t - LT[arrived[-1]] < 0.14 else 0
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        put(layer, ph, W / 2 + hap, top + A.PH * k / 2 + 900 * (1 - spring(t / 0.9, f=1.6, d=6)), 1, k)
        layer.putalpha(ImageChops.multiply(layer.split()[3], mask))
        im.alpha_composite(layer)
        for i in arrived: ring(im, W / 2, top + 560, (t - LT[i]) / 0.9, maxr=520, r0=200)
        pk = (t - END) / 0.4
        if pk > 0: put(im, price, W / 2, 1440, clamp(pk / 0.2), 0.6 + 0.4 * back(pk))
        sh = 12 * (1 - (t - END) / 0.16) if 0 <= t - END < 0.16 else 0
        return im, sh
    ev = [(0.0, "whoosh", 0.7)] + [(lt, "ping", 0.8) for lt in LT] + [(END, "hit", 1.0), (END + 0.05, "coin", 0.6)]
    return dur, fn, ev
