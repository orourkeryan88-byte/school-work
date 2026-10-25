"""Scenes for the Southline roofers 'the maths' ad (navy + gold). Built on adkit + volt_scenes/roofer_scenes helpers.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, pill, fit_size, eo, eio, back, spring, clamp, ring, underline, sprite, shadowed
from volt_scenes import RED, WHITE, DARK, header
from roofer_scenes import rain


def house_tile(w, col, roof=None):
    """small flat house icon sprite"""
    def fn(d, s, im):
        h = w; d.polygon([(w * s / 2, 0.08 * h * s), (0.06 * w * s, 0.48 * h * s), (0.94 * w * s, 0.48 * h * s)], fill=roof or col)
        d.rectangle((0.18 * w * s, 0.46 * h * s, 0.82 * w * s, 0.92 * h * s), fill=col)
        d.rectangle((0.42 * w * s, 0.64 * h * s, 0.58 * w * s, 0.92 * h * s), fill=(0, 0, 0, 90))
    return sprite(w, w, fn)


# ---------------------------------------------------------------- opener: the scale
def scene_scale(word="Roofers,", l1="ONE RE-ROOF CAN BEAT", l2="FORTY PATCH JOBS.", dur=4.0, tip_at=1.4, rise_at=1.0):
    """frame 0: giant gold 'Roofers,' + a balance scale, one re-roof card vs a pile of forty slate chips, both fully on
    screen mid-slam. The beam slams down on the re-roof side at tip_at, then the line rises in."""
    big = text(word, "bl", fit_size(word, "bl", 260, 940), grad=(A.TH["accent"], A.TH["accent2"], 0))
    s1 = text(l1, "xb", fit_size(l1, "xb", 76, 960)); s2 = text(l2, "xb", fit_size(l2, "xb", 92, 960), A.TH["accent"])
    CX, PY, BL = W / 2, 700, 340  # pivot and half beam length
    roof = A.card_sprite(260, 230, lambda d, s: (d.text((26 * s, 22 * s), "1", font=A.font("bl", 110 * s), fill=DARK),
                                                 d.text((26 * s, 160 * s), "RE-ROOF", font=A.font("bl", 40 * s), fill=DARK)), fill=A.TH["accent"], radius=34)
    chip = sprite(46, 22, lambda d, s, im: d.rounded_rectangle((0, 0, 46 * s - 1, 22 * s - 1), 5 * s, fill=(110, 124, 150)))
    lab = text("40 PATCH JOBS", "bl", 38, A.TH["muted"])

    def fn(t):
        im = A.bg(); sh = 12 * (1 - t / 0.2) if t < 0.2 else 0
        put(im, big, W / 2, 420, 1, 1.06 - 0.06 * eo(t / 0.28))
        underline(im, big, W / 2, 420 + big.height / 2 + 2, 0.35 + (t - 0.05) / 0.3, h=14)
        # beam angle: wobbles near level, then slams down on the left (re-roof) side
        ang = 4 * math.sin(t * 5) * (1 - clamp(t / tip_at)) if t < tip_at else -14 * spring((t - tip_at) / 0.6, f=1.8, d=5)
        a = math.radians(ang); lx, ly = CX - BL * math.cos(a), PY - BL * math.sin(a); rx, ry = CX + BL * math.cos(a), PY + BL * math.sin(a)
        d = ImageDraw.Draw(im)
        d.polygon([(CX, PY), (CX - 70, PY + 560), (CX + 70, PY + 560)], fill=(40, 56, 88))
        d.line((lx, ly, rx, ry), fill=A.TH["accent"], width=16); d.ellipse((CX - 22, PY - 22, CX + 22, PY + 22), fill=A.TH["accent2"])
        for x, y in ((lx, ly), (rx, ry)):  # pans hang straight down
            d.line((x, y, x - 140, y + 280), fill=(120, 134, 160), width=4); d.line((x, y, x + 140, y + 280), fill=(120, 134, 160), width=4)
            d.rounded_rectangle((x - 160, y + 280, x + 160, y + 302), 10, fill=(120, 134, 160))
        put(im, roof, lx, ly + 280 - 112, 1)
        for i in range(40):  # forty chips piled on the right pan
            r_, c_ = divmod(i, 5); put(im, chip, rx - 110 + c_ * 55 + (r_ % 2) * 10, ry + 266 - r_ * 22, 1)
        put(im, lab, rx, ry + 340, 1)
        if tip_at <= t < tip_at + 0.18: sh = 14 * (1 - (t - tip_at) / 0.18)
        put_rise(im, s1, W / 2, 1420, eo((t - rise_at) / 0.32)); put_rise(im, s2, W / 2, 1520, eo((t - rise_at - 0.25) / 0.32))
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (rise_at, "whoosh", 0.4), (tip_at, "hit", 1.0), (tip_at + 0.05, "coin", 0.5)]


# ---------------------------------------------------------------- price stickers
def scene_prices(items, times, dur=4.0, sticker_times=None):
    """'A slipped slate? €150.' Question line + a tilted price sticker slams in for each small job. items=[(question, price)]"""
    stick = [shadowed(sprite(440, 200, lambda d, s, im, p=p: (d.rounded_rectangle((0, 0, 440 * s - 1, 200 * s - 1), 36 * s, fill=A.TH["accent"]),
                                                                 d.text((220 * s - A.tsize(p, A.font("bl", 120 * s))[0] / 2, 30 * s), p, font=A.font("bl", 120 * s), fill=DARK))),
                      blur=20, dy=12, alpha=120, pad=40) for _, p in items]
    qs = [text(q, "bl", fit_size(q, "bl", 100, 960)) for q, _ in items]

    def fn(t):
        im = A.bg(); sh = 0
        for i, (q, sp, ta) in enumerate(zip(qs, stick, times)):
            if t < ta: continue
            y = 560 + i * 560; k = (t - ta) / 0.3
            put_rise(im, q, W / 2, y, eo(k))
            sk = (t - (sticker_times[i] if sticker_times else ta + 0.45)) / 0.3
            if sk > 0:
                put(im, sp, W / 2 + (-90 if i == 0 else 90), y + 220, clamp(sk / 0.15), 1.5 - 0.5 * eo(sk), -6 if i == 0 else 5)
                if sk < 0.5: sh = 12 * (1 - sk / 0.5)
        rain(im, t, 0.5)
        return im, sh
    st = sticker_times or [ta + 0.45 for ta in times]
    return dur, fn, sum([[(ta, "whoosh", 0.4), (sa, "hit", 0.9), (sa + 0.05, "coin", 0.5)] for ta, sa in zip(times, st)], [])


# ---------------------------------------------------------------- forty of them vs one re-roof
def scene_forty(dur=7.0, fill_from=0.6, fill_to=4.2, match_at=4.6, each=150, big_lbl="€10,000+", big_sub="1 re-roof · 3-bed semi"):
    """header 'YOU'D NEED FORTY'; an 8x5 grid of ladder tiles pops in with a running total, then two bars compare
    forty patch jobs with one re-roof (illustrative figures)"""
    tile = A.card_sprite(104, 104, lambda d, s: (d.line((34 * s, 20 * s, 34 * s, 86 * s), fill=A.TH["muted"], width=5 * s),
                                                 d.line((70 * s, 20 * s, 70 * s, 86 * s), fill=A.TH["muted"], width=5 * s),
                                                 [d.line((34 * s, (28 + j * 14) * s, 70 * s, (28 + j * 14) * s), fill=A.TH["muted"], width=4 * s) for j in range(5)]),
                         radius=20, shadow=False, outline=(60, 78, 110))
    lit = A.card_sprite(104, 104, lambda d, s: (d.line((34 * s, 20 * s, 34 * s, 86 * s), fill=DARK, width=5 * s), d.line((70 * s, 20 * s, 70 * s, 86 * s), fill=DARK, width=5 * s),
                                                [d.line((34 * s, (28 + j * 14) * s, 70 * s, (28 + j * 14) * s), fill=DARK, width=4 * s) for j in range(5)]),
                        fill=A.TH["accent"], radius=20, shadow=False)
    T = [fill_from + (fill_to - fill_from) * (i / 39) ** 0.8 for i in range(40)]
    x0, y0, g = W / 2 - 3.5 * 116, 620, 116

    def fn(t):
        im = A.bg(); sh = 0; m = t >= match_at
        header(im, (("JUST TO MATCH", False), ("ONE RE-ROOF.", True)) if m else (("YOU'D NEED", False), ("FORTY OF THEM.", True)), t, 330, 120, match_at if m else 0)
        n = sum(1 for x in T if t >= x)
        if not m:
            for i in range(40):
                r_, c_ = divmod(i, 8); cx, cy = x0 + c_ * g, y0 + r_ * g
                if t >= T[i]: put(im, lit, cx, cy, 1, 0.85 + 0.15 * spring((t - T[i]) / 0.25))
                else: put(im, tile, cx, cy, 0.5)
            tot = text(f"{n} × €{each} = €{n * each:,}", "bl", 70, A.TH["ink"]); put(im, tot, W / 2, 1300, 1)
        else:  # bars: forty small jobs vs one re-roof
            k = eio((t - match_at) / 0.8); d = ImageDraw.Draw(im); base = 1400
            for x, hgt, col, lbl, sub in ((W / 2 - 200, 360, (90, 104, 132), f"€{40 * each:,}", "40 patch jobs"), (W / 2 + 200, 640, A.TH["accent"], big_lbl, big_sub)):
                hh = hgt * k; d.rounded_rectangle((x - 130, base - hh, x + 130, base), 24, fill=col)
                put(im, text(lbl, "bl", 72, A.TH["ink"]), x, base - hh - 60, clamp(k * 2)); put(im, text(sub, "b", 34, A.TH["muted"]), x, base + 50, clamp(k * 2))
            if 0 <= t - match_at - 0.8 < 0.16: sh = 12
        rain(im, t, 0.4 if not m else 0)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5)] + [(x, "tick", 0.4) for x in T[::2]] + [(match_at, "whoosh", 0.8), (match_at + 0.8, "hit", 1.0), (match_at + 0.85, "coin", 0.7)]


# ---------------------------------------------------------------- the right homeowners
def scene_targeting(dur=6.0, right_at=2.5, planning_at=3.6, lines_a=(("THE BIG JOBS DON'T", False), ("COME FROM LUCK.", True)),
                    lines_b=(("THE RIGHT", False), ("HOMEOWNERS.", True))):
    """a street map of houses; a radar sweep passes, most fade, a few light up gold as 'planning a new roof'"""
    dim, gold = house_tile(70, (70, 84, 112)), house_tile(70, A.TH["accent"], A.TH["accent2"])
    pts = [(170 + c * 105 + (r % 2) * 50, 700 + r * 120) for r in range(6) for c in range(8)]
    pts = [(x, y) for x, y in pts if x < W - 120]
    picks = {5, 14, 22, 31, 37}; tag = shadowed(pill("PLANNING A NEW ROOF", 40, A.TH["accent"], DARK, w="bl"), blur=16, dy=8, alpha=120, pad=26)
    CX, CY = W / 2, 1000

    def fn(t):
        im = A.bg(); b = t >= right_at; sh = 0
        header(im, lines_b if b else lines_a, t, 330, 112, right_at if b else 0)
        d = ImageDraw.Draw(im)
        for i in range(1, 4): r = 160 * i; d.ellipse((CX - r, CY - r, CX + r, CY + r), outline=(40, 58, 92), width=2)
        sw = (t * 160) % 360  # radar sweep
        o = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(o).pieslice((CX - 560, CY - 560, CX + 560, CY + 560), sw - 40, sw, fill=A.TH["accent"] + (40,)); im.alpha_composite(o)
        for i, (x, y) in enumerate(pts):
            sel = i in picks; fade = clamp((t - right_at) / 0.5)
            if sel and t >= planning_at - 0.4:
                k = (t - planning_at + 0.4 - list(sorted(picks)).index(i) * 0.12) / 0.3
                put(im, gold if k > 0 else dim, x, y, 1, (0.8 + 0.4 * spring(k)) if k > 0 else 1)
                if k > 0: ring(im, x, y, k / 1.6, maxr=110, width=4, r0=20)
            else: put(im, dim, x, y, 1 - 0.7 * fade if not sel else 1)
        tk = (t - planning_at - 0.4) / 0.35
        if tk > 0:
            put(im, tag, W / 2, 1520, clamp(tk / 0.2), 1.3 - 0.3 * eo(tk))
            if tk < 0.4: sh = 10 * (1 - tk / 0.4)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5), (right_at, "glitch", 0.5), (right_at, "hit", 0.6)] + \
        [(planning_at - 0.4 + k * 0.12, "ping", 0.5) for k in range(len(picks))] + [(planning_at + 0.4, "hit", 0.9)]


# ---------------------------------------------------------------- name, number, the job
def scene_lead_card(fields, times, tap_at, dur=3.0, title="New lead", job_tag="Full re-roof"):
    """a lead card whose rows fill in on their words, then 'Ring back' is tapped. fields=[(label, value)], times=[t per row]"""
    w, h = 900, 640
    def card(n):
        def dr(d, s):
            d.text((56 * s, 46 * s), title.upper(), font=A.font("b", 32 * s), fill=A.TH["muted"])
            f = A.font("bl", 30 * s); tw, th, ox, oy = A.tsize(job_tag, f)
            d.rounded_rectangle(((w - 56) * s - tw - 44 * s, 40 * s, (w - 56) * s, 88 * s), 24 * s, fill=A.TH["accent"])
            d.text(((w - 56) * s - tw - 22 * s - ox, 64 * s - th / 2 - oy), job_tag, font=f, fill=DARK)
            for i, (lab, val) in enumerate(fields):
                y = 130 + i * 150; d.line((56 * s, (y + 130) * s, (w - 56) * s, (y + 130) * s), fill=(60, 78, 110), width=2 * s)
                d.text((56 * s, y * s), lab, font=A.font("sb", 32 * s), fill=A.TH["muted"])
                if i < n: d.text((56 * s, (y + 44) * s), val, font=A.font("bl", 64 * s), fill=A.TH["card_ink"])
        return A.card_sprite(w, h, dr, outline=(60, 78, 110))
    cards = [card(n) for n in range(len(fields) + 1)]; b0, b1 = A.button("Ring back"), A.button("Ring back", pressed=True)

    def fn(t):
        im = A.bg(); n = sum(1 for x in times if t >= x); k = eo(t / 0.4)
        put(im, cards[n], W / 2, 860 + 140 * (1 - k), clamp(t / 0.2), 0.94 + 0.06 * spring(t / 0.5))
        if n and t - times[n - 1] < 0.25: ring(im, W / 2, 860 - 190 + (n - 1) * 150, (t - times[n - 1]) / 0.6, maxr=300, width=4, r0=60)
        p = (t - times[-1] - 0.2) / 0.4
        if p > 0:
            press = 1 - clamp(abs(t - tap_at - 0.06) / 0.1)
            put(im, b1 if press > 0.5 else b0, W / 2, 1360, clamp(p / 0.3), (0.7 + 0.3 * spring(p)) * (1 - 0.06 * press))
        A.tap(im, W / 2 + 300, 1375, t, tap_at)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.6)] + [(x, "pop", 0.8) for x in times] + [(tap_at, "click", 1.0), (tap_at + 0.02, "ping", 0.6)]
