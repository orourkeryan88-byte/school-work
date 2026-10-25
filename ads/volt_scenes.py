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


def draw_lines(im, sps, cy, gap=0.98, scale=1.0, k=None, stagger=0.0):
    """centre a stack of line sprites on cy. k (seconds into the cut) + stagger pop the lines in one after another"""
    h = sum(sp.height * gap for sp in sps); y = cy - h / 2
    for j, sp in enumerate(sps):
        if k is None or not stagger: put(im, sp, W / 2, y + sp.height * gap / 2, 1, scale)
        else:
            q = (k - j * stagger) / 0.14
            if q > 0: put(im, sp, W / 2, y + sp.height * gap / 2, clamp(q * 3), 1.25 - 0.25 * eo(q))
        y += sp.height * gap


# ---------------------------------------------------------------- opener
def scene_one_builder(word="Plumbers,", l1="IF ONE BUILDER GIVES YOU", l2="MOST OF YOUR WORK…", dur=3.2, pop_at=0.55, rise_at=0.75):
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
        # donut: builder slice punches out at pop_ats, then throbs
        pop = 0 if t < pop_at else 26 * spring((t - pop_at) / 0.5) + 6 * math.sin((t - pop_at) * 9) * clamp((t - 0.9) / 0.3)
        key = round(pop)
        if key not in cache:
            dn = donut(key); gl = dn.filter(ImageFilter.GaussianBlur(30)); gl.putalpha(gl.split()[3].point(lambda v: v * 6 // 10))
            cache[key] = (dn, gl)
        dn, gl = cache[key]
        if t > pop_at: im.alpha_composite(gl)
        im.alpha_composite(dn)
        for i, sp in enumerate(centre): put(im, sp, CX, CY - 36 + i * 72, 1, 1.06 - 0.06 * eo(t / 0.3))
        ring(im, CX, CY, (t - pop_at) / 0.9, maxr=420, r0=R)
        put(im, tag, CX - 270, CY - R - 10, 1, (1 + 0.25 * (1 - eo((t - pop_at) / 0.3))) if t > pop_at else 1, -6)
        put(im, other, CX + 300, CY - R + 40, clamp((t - 0.2) / 0.2), 1, 5)
        if pop_at <= t < 0.7: sh = 8 * (1 - (t - pop_at) / 0.15)
        put_rise(im, s1, W / 2, 1330, eo((t - rise_at) / 0.32))
        put_rise(im, s2, W / 2, 1430, eo((t - rise_at - 0.2) / 0.32))
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (pop_at, "hit", 0.6), (pop_at, "pop", 0.6), (rise_at, "whoosh", 0.4)]


# ---------------------------------------------------------------- fast-cut slams
def scene_slam(parts, dur=2.4, lock_last=False, last_share=1.7, cuts=None, stagger=0.0):
    """giant fast-cut type. parts=[(text with | breaks, style d|y|dh)]. each part is a hard cut with a slam + hit.
    lock_last: the final card holds, then an underline locks it in with a click. cuts: explicit cut times (e.g. on the words)"""
    cards = [big_lines(s, st) for s, st in parts]
    wts = [len(s.replace("|", "")) + 6 for s, _ in parts]; wts[-1] *= last_share
    tot = sum(wts); cuts_in, cuts = cuts, [0.0]
    for w_ in wts[:-1]: cuts.append(cuts[-1] + dur * w_ / tot)
    cuts = list(cuts_in) if cuts_in else cuts

    def fn(t):
        i = max(k for k, c in enumerate(cuts) if t >= c); k = t - cuts[i]
        im = volt_bg() if parts[i][1] == "dh" else A.bg()
        sps, size = cards[i]
        draw_lines(im, sps, H / 2 - 40, scale=1.12 - 0.12 * eo(k / 0.14), k=k, stagger=stagger)
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
def scene_linked(dur=4.4, flip=2.1, lag=0.45, A_lines=(("WHEN HE'S BUSY,", False), ("YOU'RE BUSY.", True)),
                 B_lines=(("WHEN HE GOES QUIET…", False), ("SO DO YOU.", True)), step_a=0.12, step_b=0.12):
    """two calendar meters chained together. his drains at flip, yours follows lag later. header swaps from busy to quiet"""
    BW, BH, TOP = 300, 680, 760; XS = (W / 2 - 220, W / 2 + 220)
    labs = [text("HIS CALENDAR", "xb", 40, A.TH["muted"]), text("YOUR CALENDAR", "xb", 40, A.TH["muted"])]

    def meter(im, x, level, t):
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((x - BW / 2, TOP, x + BW / 2, TOP + BH), 40, fill=A.TH["card"], outline=(60, 62, 52), width=3)
        col = A.TH["accent"] if level > 0.45 else (RED if level < 0.25 else (255, 170, 40))
        fh = (BH - 40) * level
        if fh > 4: d.rounded_rectangle((x - BW / 2 + 20, TOP + BH - 20 - fh, x + BW / 2 - 20, TOP + BH - 20), 26, fill=col)
        # day ticks so it reads like a calendar
        for k in range(1, 5): d.line((x - BW / 2 + 20, TOP + 20 + k * (BH - 40) / 5, x + BW / 2 - 20, TOP + 20 + k * (BH - 40) / 5), fill=(0, 0, 0, 70), width=3)
        word = "FULL" if level > 0.45 else "EMPTY"; st = text(word, "bl", 64, DARK if level > 0.45 else A.TH["ink"])
        put(im, st, x, TOP + BH - 90 if level < 0.45 else TOP + BH - 20 - fh + 60, 1)

    def fn(t):
        im = A.bg(); sh = 0
        phase_b = t >= flip
        header(im, B_lines if phase_b else A_lines, t, 330, 104, flip if phase_b else 0, step_b if phase_b else step_a)
        lv_him = 0.92 - 0.82 * eio((t - flip) / 0.7); lv_you = 0.92 - 0.82 * eio((t - flip - lag) / 0.7)
        bob = 0 if t > flip else math.sin(t * 6) * 0.02
        for x, lv, lab in zip(XS, (lv_him + bob, lv_you + bob), labs):
            meter(im, x, lv, t); put(im, lab, x, TOP + BH + 60, eo((t - 0.2) / 0.3))
        # chain between the meters
        d = ImageDraw.Draw(im); cy = TOP + BH / 2
        for k in range(4):
            cx = XS[0] + BW / 2 + 22 + k * 30; d.ellipse((cx - 20, cy - 13, cx + 20, cy + 13), outline=A.TH["accent"] if not phase_b else RED, width=7)
        if flip + lag <= t < flip + lag + 0.15: sh = 9
        if flip <= t < flip + 0.16: sh = 12 * (1 - (t - flip) / 0.16)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.6), (0.05, "pop", 0.6), (flip, "hit", 0.9), (flip + lag, "hit", 0.7), (flip + 0.2, "glitch", 0.4)]


# ---------------------------------------------------------------- his price
def scene_his_price(dur=4.2, your="€6,500", his="€4,800", job="Bathroom refit · 3-bed semi", strike_at=1.1, stamp_at=1.45,
                    sub_txt="Because he knows you can't say no.", sub_at=2.0, lines=(("YOU WORK AT", False), ("HIS PRICE.", True))):
    """your quote card gets struck through and HIS PRICE is stamped on it (illustrative numbers)"""
    def card_fn(d, s):
        d.text((56 * s, 50 * s), "YOUR QUOTE", font=A.font("b", 34 * s), fill=A.TH["muted"])
        d.text((56 * s, 100 * s), job, font=A.font("sb", 40 * s), fill=A.TH["card_ink"])
        d.text((56 * s, 180 * s), your, font=A.font("bl", 150 * s), fill=A.TH["card_ink"])
    card = A.card_sprite(900, 400, card_fn, outline=(60, 62, 52))
    stamp = sprite(560, 190, lambda d, s, im: (d.rounded_rectangle((0, 0, 560 * s - 1, 190 * s - 1), 26 * s, outline=RED, width=10 * s),
                                                d.text((40 * s, 22 * s), "HIS PRICE", font=A.font("bl", 46 * s), fill=RED),
                                                d.text((40 * s, 74 * s), his, font=A.font("bl", 96 * s), fill=RED)))
    sub = text(sub_txt, "xb", fit_size(sub_txt, "xb", 64, 960))

    def fn(t):
        im = A.bg(); sh = 0
        header(im, lines, t, 330, 120)
        k = (t - 0.3) / 0.5; put(im, card, W / 2, 900 + 120 * (1 - eo(k)), clamp(k / 0.3), 0.92 + 0.08 * spring(k))
        sp = clamp((t - strike_at) / 0.25)
        if sp > 0: ImageDraw.Draw(im).line((W / 2 - 400, 990, W / 2 - 400 + 640 * eo(sp), 970), fill=RED, width=14)
        st = (t - stamp_at) / 0.3
        if st > 0: put(im, stamp, W / 2 + 140, 1150, clamp(st / 0.15), 1.5 - 0.5 * eo(st), -8)
        if stamp_at <= t < stamp_at + 0.17: sh = 14 * (1 - (t - stamp_at) / 0.17)
        put_rise(im, sub, W / 2, 1420, eo((t - sub_at) / 0.32))
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5), (0.3, "pop", 0.7), (strike_at, "swish", 0.6), (stamp_at, "hit", 1.0), (sub_at, "whoosh", 0.3)]


# ---------------------------------------------------------------- paid when he gets paid
def scene_invoice(dur=4.4, amount="€3,600", keys=((0.7, 0), (2.6, 67)), sub_txt="If he's slow paying, so are you.", sub_at=2.75,
                  van=None, van_at=None, lines=(("YOU GET PAID WHEN", False), ("HE GETS PAID.", True))):
    """invoice card: days-waiting counter rolls up, status flips to OVERDUE in red, progress bar fills red"""
    def base_fn(d, s):
        d.text((56 * s, 50 * s), "INVOICE #0418", font=A.font("b", 34 * s), fill=A.TH["muted"])
        d.text((56 * s, 100 * s), "Kitchen + 2 bathrooms · first fix", font=A.font("sb", 38 * s), fill=A.TH["card_ink"])
        d.text((56 * s, 170 * s), amount, font=A.font("bl", 130 * s), fill=A.TH["card_ink"])
        d.text((56 * s, 352 * s), "DAYS WAITING", font=A.font("b", 32 * s), fill=A.TH["muted"])
    card = A.card_sprite(900, 560, base_fn, outline=(60, 62, 52))
    sub = text(sub_txt, "xb", fit_size(sub_txt, "xb", 64, 960))
    T0, T1 = keys[0][0], keys[-1][0]; vanp = shadowed(pill(van, 40, RED, WHITE, w="bl"), blur=18, dy=10, alpha=120, pad=30) if van else None

    def days_at(t):  # eased roll between keyframes (t, value)
        for (ta, va), (tb, vb) in zip(keys, keys[1:]):
            if t < tb: return va + (vb - va) * eio((t - ta) / (tb - ta))
        return keys[-1][1]
    over_at = next((ta + (tb - ta) * 0.5 for (ta, va), (tb, vb) in zip(keys, keys[1:]) if vb >= 45), T1)

    def fn(t):
        im = A.bg(); sh = 0
        header(im, lines, t, 330, 104)
        k = (t - 0.25) / 0.5; cy = 960 + 120 * (1 - eo(k)); put(im, card, W / 2, cy, clamp(k / 0.3), 0.92 + 0.08 * spring(k))
        if k > 0.3:
            n = int(round(days_at(t))); over = n >= 45
            x0, y0 = W / 2 - 450 + 56, cy - 280 + 400
            d = ImageDraw.Draw(im)
            num = text(str(n), "bl", 96, RED if over else A.TH["ink"]); put(im, num, x0 + num.width / 2, y0 + 30)
            chip = pill("OVERDUE" if over else ("AWAITING PAYMENT" if n > 0 else "SENT"), 30, RED if over else (60, 62, 52), WHITE)
            put(im, chip, W / 2 + 450 - 56 - chip.width / 2, y0 + 30, 1, 1 + 0.25 * (1 - eo((t - over_at) / 0.25)) if over else 1)
            bx0, bx1, by = x0, W / 2 + 450 - 56, y0 + 110
            d.rounded_rectangle((bx0, by, bx1, by + 22), 11, fill=(50, 52, 44))
            d.rounded_rectangle((bx0, by, bx0 + max(22, (bx1 - bx0) * min(1, n / max(60, keys[-1][1]))), by + 22), 11, fill=RED if over else A.TH["accent"])
        put_rise(im, sub, W / 2, 1420, eo((t - sub_at) / 0.32))
        if vanp and t >= van_at:
            vk = (t - van_at) / 0.35; put(im, vanp, W / 2, 1540, clamp(vk / 0.2), 1.4 - 0.4 * eo(vk), -3)
            if vk < 0.45: sh = 12 * (1 - vk / 0.45)
        return im, sh
    ev = [(0.0, "whoosh", 0.5), (0.25, "pop", 0.7)] + [(T0 + i * 0.12, "tick", 0.35) for i in range(int((T1 - T0) / 0.12))] + [(over_at, "glitch", 0.6), (over_at, "hit", 0.6), (sub_at, "whoosh", 0.3)]
    if van: ev.append((van_at, "hit", 1.0))
    return dur, fn, ev


# ---------------------------------------------------------------- own homeowners
def notif_v(title, body, age, icon="drop"):
    """lock-screen enquiry notification with a water-drop or house tile (no brand logo before the CTA)"""
    w = 820
    def dr(d, s):
        d.rounded_rectangle((30 * s, 36 * s, 114 * s, 120 * s), 22 * s, fill=A.TH["accent"])
        bx, by = 72 * s, 80 * s
        if icon == "house": d.polygon([(bx, by - 30 * s), (bx - 28 * s, by - 4 * s), (bx + 28 * s, by - 4 * s)], fill=DARK); d.rectangle((bx - 20 * s, by - 6 * s, bx + 20 * s, by + 24 * s), fill=DARK)
        else: d.polygon([(bx, by - 30 * s), (bx - 20 * s, by + 2 * s), (bx + 20 * s, by + 2 * s)], fill=DARK); d.ellipse((bx - 20 * s, by - 16 * s, bx + 20 * s, by + 24 * s), fill=DARK)
        d.text((140 * s, 34 * s), "NEW ENQUIRY", font=A.font("sb", 24 * s), fill=(120, 116, 108))
        d.text(((w - 40) * s - A.tsize(age, A.font("m", 24 * s))[0], 34 * s), age, font=A.font("m", 24 * s), fill=(120, 116, 108))
        d.text((140 * s, 72 * s), title, font=A.font("b", 38 * s), fill=(17, 17, 16))
        d.text((140 * s, 122 * s), body, font=A.font("m", 31 * s), fill=(80, 78, 72))
    sp = sprite(w, 186, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, 186 * s - 1), 44 * s, fill=(255, 255, 255, 250)), dr(d, s)))
    return shadowed(sp, blur=22, dy=14, alpha=45, pad=40)


def scene_own_leads(leads, dur=5.6, interval=0.5, k=0.74, top=640, crop=1610, lt=None, tag_at=0.3, price_at=None,
                    price_txt="AT YOUR PRICE.", lines=(("YOUR OWN", False), ("HOMEOWNERS.", True)),
                    tag="BOILER SWAPS · BATHROOM REFITS", icon="drop"):
    """header + phone rising from the bottom (cropped with a fade), enquiries drop and stack, 'AT YOUR PRICE.' pops at the end"""
    ph0 = A.phone(date="Monday 26 October", wall=((34, 36, 24), (8, 8, 6), A.TH["accent"]))
    ages = ["now", "4m", "22m", "1h", "3h", "5h"]; cache = {}
    def N(i, r):
        if (i, r) not in cache: cache[(i, r)] = notif_v(*leads[i], ages[min(r, len(ages) - 1)], icon)
        return cache[(i, r)]
    LT = list(lt) if lt else [0.65 + i * interval for i in range(len(leads))]; END = price_at if price_at is not None else LT[-1] + 0.55
    tagp = pill(tag, 34, tuple(int(c * 0.25) for c in A.TH["accent"]), A.TH["accent"], w="b")
    price = shadowed(pill(price_txt, 62, A.TH["accent"], w="bl"), blur=24, dy=14, alpha=120, pad=40)
    mask = Image.new("L", (W, H), 255); md = ImageDraw.Draw(mask)
    for y in range(crop - 160, H): md.line((0, y, W, y), fill=int(255 * clamp((crop - y) / 160)))

    def fn(t):
        im = A.bg(); arrived = [i for i, lt in enumerate(LT) if t >= lt]
        header(im, lines, t, 300, 112)
        put(im, tagp, W / 2, 548, eo((t - tag_at) / 0.3), 0.9 + 0.1 * spring((t - tag_at) / 0.4))
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


# ---------------------------------------------------------------- "if you're relying on…"
def warn_card(title, sub):
    """stack card with a red warning tile"""
    def dr(d, s):
        d.rounded_rectangle((40 * s, 45 * s, 160 * s, 165 * s), 30 * s, fill=(70, 24, 24))
        d.polygon([(100 * s, 70 * s), (140 * s, 140 * s), (60 * s, 140 * s)], fill=RED)
        d.rectangle((96 * s, 92 * s, 104 * s, 120 * s), fill=(70, 24, 24)); d.ellipse((95 * s, 126 * s, 105 * s, 136 * s), fill=(70, 24, 24))
        d.text((196 * s, 50 * s), title, font=A.font("bl", 50 * s), fill=A.TH["card_ink"])
        d.text((196 * s, 122 * s), sub, font=A.font("m", 34 * s), fill=A.TH["muted"])
    return A.card_sprite(940, 210, dr, outline=(60, 62, 52))


def scene_relying(items, drops, dur=4.0, title=("IF YOU'RE", "RELYING ON…"), count_lbl="{n} THING{s} YOU CAN'T CONTROL"):
    """giant 'IF YOU'RE RELYING ON…' header, then each crutch drops onto a card stack on its word. items=[(title, sub)], drops=[t]"""
    cards = [warn_card(*it) for it in items]
    big = [text(title[0], "bl", fit_size(title[0], "bl", 150, 900)), text(title[1], "bl", fit_size(title[1], "bl", 150, 900), A.TH["accent"])]

    def fn(t):
        im = A.bg()
        for j, sp in enumerate(big): put_rise(im, sp, W / 2, 400 + j * 160, eo((t - j * 0.1) / 0.25))
        sh = A.draw_stack(im, cards, drops, t, 1150, step=78, from_y=1300, rot=5)
        n = sum(1 for d in drops if t >= d)
        if n and count_lbl: put(im, pill(count_lbl.replace("{n}", str(n)).replace("{s}", "S" if n > 1 else ""), 34, RED, WHITE), W / 2, 1450, 1, 1 + 0.15 * (1 - eo((t - drops[n - 1] - 0.3) / 0.25)))
        return im, sh
    return dur, fn, [(0.0, "hit", 0.9)] + sum([[(d, "swish", 0.4), (d + 0.3, "hit", 0.8)] for d in drops], [])
