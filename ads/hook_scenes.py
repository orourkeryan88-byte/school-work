"""Hook / open-question / body-1 scenes for the Southline roofers 'easy to find' ad (navy + gold).
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import adkit as A
from adkit import W, H, put, put_rise, text, pill, fit_size, eo, eio, back, spring, clamp, ring, underline, sprite, shadowed
from volt_scenes import RED, WHITE, DARK, header, big_lines, draw_lines
from roofer_scenes import rain, flash
from maths_scenes import house_tile

GREY = (110, 124, 150)


def stamp(txt, col=RED, size=70, w=None):
    """rubber-stamp style label: outlined box + heavy text"""
    f = A.font("bl", size * 2); tw, th, ox, oy = A.tsize(txt, f); bw, bh = tw // 2 + 70, int(size * 1.6)
    return sprite(bw, bh, lambda d, s, im: (d.rounded_rectangle((0, 0, bw * s - 1, bh * s - 1), 22 * s, outline=col, width=9 * s),
                                            d.text((bw * s / 2 - tw / 2 - ox, bh * s / 2 - th / 2 - oy), txt, font=f, fill=col)))


# ---------------------------------------------------------------- HOOK: 40 patch jobs vs 1 re-roof
def scene_hook_scale(word="Roofers,", dur=3.6, t40=0.9, t1=1.9, same_at=2.6):
    """frame 0: giant gold 'Roofers,' + a loaded balance scale, both fully on screen mid-slam with a camera punch.
    '40' slams over the patch-job pile, '1' over the re-roof as the beam crashes down (slates fly off),
    then a SAME MONEY. stamp with a flash."""
    big = text(word, "bl", fit_size(word, "bl", 260, 940), grad=(A.TH["accent"], A.TH["accent2"], 0))
    CX, PY, BL = W / 2, 760, 340
    roof = A.card_sprite(250, 210, lambda d, s: (d.polygon([(125 * s, 30 * s), (30 * s, 110 * s), (220 * s, 110 * s)], fill=DARK),
                                                 d.rectangle((55 * s, 108 * s, 195 * s, 180 * s), fill=DARK)), fill=A.TH["accent"], radius=34)
    chip = sprite(46, 22, lambda d, s, im: d.rounded_rectangle((0, 0, 46 * s - 1, 22 * s - 1), 5 * s, fill=GREY))
    n40 = text("40", "bl", 200, A.TH["ink"]); n1 = text("1", "bl", 200, grad=(A.TH["accent"], A.TH["accent2"], 0))
    l40 = text("PATCH JOBS", "bl", 44, A.TH["muted"]); l1 = text("RE-ROOF", "bl", 44, A.TH["accent"])
    same = shadowed(pill("SAME MONEY.", 70, A.TH["accent"], DARK, w="bl"), blur=24, dy=14, alpha=140, pad=40)
    rng = np.random.default_rng(5)
    bits = [(rng.uniform(-1, 1) * 520, -rng.uniform(500, 1100), rng.uniform(-400, 400), rng.uniform(0, 40)) for _ in range(16)]

    def fn(t):
        im = A.bg(); sh = 14 * (1 - t / 0.2) if t < 0.2 else 0
        put(im, big, W / 2, 380, 1, 1.08 - 0.08 * eo(t / 0.25))
        underline(im, big, W / 2, 380 + big.height / 2 + 2, 0.4 + (t - 0.05) / 0.3, h=14)
        ang = 5 * math.sin(t * 6) * (1 - clamp(t / t1)) if t < t1 else -15 * spring((t - t1) / 0.6, f=1.8, d=5)
        a = math.radians(ang); lx, ly = CX - BL * math.cos(a), PY - BL * math.sin(a); rx, ry = CX + BL * math.cos(a), PY + BL * math.sin(a)
        d = ImageDraw.Draw(im)
        d.polygon([(CX, PY), (CX - 70, PY + 600), (CX + 70, PY + 600)], fill=(40, 56, 88))
        d.line((lx, ly, rx, ry), fill=A.TH["accent"], width=16); d.ellipse((CX - 22, PY - 22, CX + 22, PY + 22), fill=A.TH["accent2"])
        for x, y in ((lx, ly), (rx, ry)):
            d.line((x, y, x - 140, y + 280), fill=(120, 134, 160), width=4); d.line((x, y, x + 140, y + 280), fill=(120, 134, 160), width=4)
            d.rounded_rectangle((x - 160, y + 280, x + 160, y + 302), 10, fill=(120, 134, 160))
        put(im, roof, lx, ly + 280 - 102, 1, 1 + (0.15 * (1 - eo((t - t1) / 0.3)) if t >= t1 else 0))
        for i in range(40):
            r_, c_ = divmod(i, 5); put(im, chip, rx - 110 + c_ * 55 + (r_ % 2) * 10, ry + 266 - r_ * 22, 1)
        if t >= t1:  # loose slates fly off the pile as the beam drops
            k = t - t1
            for vx, vy, spin, d0 in bits:
                x = rx + vx * k; y = ry + 150 + vy * k + 1700 * k * k
                if y < H + 50: put(im, chip, x, y, 1, 1, spin * k + d0)
            ring(im, lx, ly + 200, k / 0.8, maxr=520, width=8, r0=80)
        if t >= t40:  # the numbers slam in on their words
            k = (t - t40) / 0.25; put(im, n40, rx, ry + 470, clamp(k / 0.3), 1.5 - 0.5 * eo(k)); put(im, l40, rx, ry + 590, clamp(k / 0.3))
        if t >= t1:
            k = (t - t1) / 0.25; put(im, n1, lx, ly + 470, clamp(k / 0.3), 1.5 - 0.5 * eo(k)); put(im, l1, lx, ly + 590, clamp(k / 0.3))
        if t >= same_at:
            k = (t - same_at) / 0.3; put(im, same, W / 2, 1600, clamp(k / 0.2), 1.6 - 0.6 * eo(k), -4)
        flash(im, (t - same_at) / 0.3, 0.35)
        for h_ in (t40, t1, same_at):
            if h_ <= t < h_ + 0.16: sh = 12 * (1 - (t - h_) / 0.16)
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (t40, "hit", 0.85), (t1, "hit", 1.0), (t1 + 0.02, "swish", 0.6), (same_at, "hit", 0.9), (same_at + 0.05, "coin", 0.8)]


# ---------------------------------------------------------------- OPEN QUESTION: their week vs your week
def scene_split_weeks(dur=5.0, left_at=1.0, right_at=2.6):
    """top: SOME ROOFERS, a week of gold RE-ROOF chips popping in. bottom: YOU, one €150 job up a ladder in the rain"""
    days = ("Mon", "Tue", "Wed", "Thu", "Fri"); cw, gap = 170, 16; x0 = (W - (5 * cw + 4 * gap)) / 2 + cw / 2
    chip = A.card_sprite(cw, 150, lambda d, s: (d.text((20 * s, 18 * s), "RE-ROOF", font=A.font("bl", 28 * s), fill=DARK),
                                               d.polygon([(85 * s, 70 * s), (40 * s, 110 * s), (130 * s, 110 * s)], fill=DARK),
                                               d.rectangle((55 * s, 108 * s, 115 * s, 135 * s), fill=DARK)), fill=A.TH["accent"], radius=24, shadow=False)
    slot = A.card_sprite(cw, 150, lambda d, s: None, fill=(26, 40, 68), radius=24, shadow=False, outline=(60, 78, 110))
    dl = [text(x, "sb", 28, A.TH["muted"]) for x in days]
    top_l = pill("SOME ROOFERS", 40, A.TH["accent"], DARK, w="bl"); bot_l = pill("YOU", 40, (60, 74, 100), WHITE, w="bl")
    sticker = shadowed(sprite(380, 170, lambda d, s, im: (d.rounded_rectangle((0, 0, 380 * s - 1, 170 * s - 1), 30 * s, fill=(150, 160, 180)),
                                                          d.text((190 * s - A.tsize("€150", A.font("bl", 110 * s))[0] / 2, 20 * s), "€150", font=A.font("bl", 110 * s), fill=DARK))),
                       blur=18, dy=10, alpha=120, pad=34)
    ladder = sprite(200, 420, lambda d, s, im: ([d.line(((40 + 120 * j) * s, 0, (40 + 120 * j) * s, 420 * s), fill=GREY, width=12 * s) for j in range(2)],
                                                [d.line((40 * s, (30 + 60 * j) * s, 160 * s, (30 + 60 * j) * s), fill=GREY, width=10 * s) for j in range(7)]))
    T = [left_at + 0.16 * i for i in range(5)]; mid = 1060
    clip = Image.new("L", (W, H), 0); ImageDraw.Draw(clip).rectangle((0, mid, W, H), fill=255)

    def fn(t):
        im = A.bg(); sh = 0
        d = ImageDraw.Draw(im); d.rectangle((0, mid, W, H), fill=(10, 18, 34))
        put(im, top_l, W / 2, 360, eo(t / 0.25), 0.8 + 0.2 * spring(t / 0.4))
        for i in range(5):
            x = x0 + i * (cw + gap); put(im, dl[i], x, 470, 1); put(im, slot, x, 600, 1)
            if t >= T[i]: k = (t - T[i]) / 0.3; put(im, chip, x, 600 - 60 * (1 - spring(k)), clamp(k / 0.2), 0.8 + 0.2 * spring(k))
        n = sum(1 for x in T if t >= x)
        if n: put(im, text(f"{n} re-roof{'s' if n > 1 else ''} this week", "bl", 54, A.TH["accent"]), W / 2, 780, 1, 1 + 0.12 * (1 - eo((t - T[n - 1]) / 0.25)))
        if t >= right_at:
            k = (t - right_at) / 0.35
            put(im, bot_l, W / 2, mid + 110, clamp(k / 0.3), 0.8 + 0.2 * spring(k))
            put(im, ladder, W / 2 - 230, mid + 470 + 200 * (1 - eo(k)), clamp(k / 0.3), 1, 8)
            put(im, sticker, W / 2 + 150, mid + 420, clamp(k / 0.3), 1.5 - 0.5 * eo(k), -6)
            if k < 0.5: sh = 10 * (1 - k / 0.5)
            r = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rain(r, t, 1.0); r.putalpha(ImageChops.multiply(r.split()[3], clip)); im.alpha_composite(r)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5)] + [(x, "pop", 0.6) for x in T] + [(T[-1] + 0.1, "coin", 0.6), (right_at, "hit", 0.8), (right_at + 0.05, "swish", 0.4)]


# ---------------------------------------------------------------- BODY 1a: it's not X, not Y, not Z
def scene_crossouts(items, times, dur=3.6, strike_lag=0.35):
    """each word appears big on its beat, then a red strike wipes through it and an ✗ stamps beside it"""
    sps = [text(s, "bl", fit_size(s, "bl", 130, 820)) for s in items]; ys = [700 + i * 260 for i in range(len(items))]
    x_mark = sprite(110, 110, lambda d, s, im: (d.line((15 * s, 15 * s, 95 * s, 95 * s), fill=RED, width=18 * s), d.line((95 * s, 15 * s, 15 * s, 95 * s), fill=RED, width=18 * s)))
    lab = text("IT'S NOT…", "bl", 80, A.TH["muted"])

    def fn(t):
        im = A.bg(); sh = 0; put_rise(im, lab, W / 2, 420, eo(t / 0.3))
        for sp, y, ta in zip(sps, ys, times):
            if t < ta: continue
            k = (t - ta) / 0.25; put(im, sp, W / 2 - 50, y, clamp(k / 0.3), 1.25 - 0.25 * eo(k))
            s_ = clamp((t - ta - strike_lag) / 0.18)
            if s_ > 0:
                x0 = W / 2 - 50 - sp.width / 2 - 20; ImageDraw.Draw(im).line((x0, y + 4, x0 + (sp.width + 40) * eo(s_), y - 4), fill=RED, width=16)
                put(im, x_mark, W / 2 - 50 + sp.width / 2 + 90, y, s_, 1.6 - 0.6 * eo(s_))
            if ta + strike_lag <= t < ta + strike_lag + 0.14: sh = 10
        return im, sh
    return dur, fn, sum([[(ta, "pop", 0.7), (ta + strike_lag, "hit", 0.8)] for ta in times], [])


# ---------------------------------------------------------------- BODY 1b: 11pm, scrolling, first ad wins
def scene_feed_scroll(dur=8.0, land_at=2.8, tap_at=4.5, win_at=5.6, clock="23:04",
                      lines_a=(("THEY'RE ON THEIR PHONE", False), ("AT 11 AT NIGHT…", True)),
                      lines_b=(("THE FIRST ROOFER THEY SEE", False), ("USUALLY GETS THE JOB.", True))):
    """phone at night: the feed flicks past other posts, decelerates onto a roofer's sponsored post (brand blurred),
    'Get quote' is tapped, quote requested, header switches to the payoff line"""
    k_, PW, PH = 0.64, A.PW, A.PH
    def filler(i):
        w, h = 820, 620; tone = [(205, 214, 226), (226, 210, 196), (200, 222, 206), (214, 204, 228)][i % 4]
        return sprite(w, h, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 36 * s, fill=WHITE), d.ellipse((30 * s, 30 * s, 100 * s, 100 * s), fill=(180, 186, 196)),
                                              d.rounded_rectangle((120 * s, 44 * s, 380 * s, 70 * s), 10 * s, fill=(210, 214, 222)), d.rectangle((0, 130 * s, w * s, 520 * s), fill=tone),
                                              d.rounded_rectangle((30 * s, 545 * s, 600 * s, 575 * s), 10 * s, fill=(214, 218, 226))))
    def ad(pressed):
        w, h = 820, 1000
        def fn(d, s, im):
            d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 36 * s, fill=WHITE); d.ellipse((30 * s, 30 * s, 100 * s, 100 * s), fill=(60, 70, 90))
            d.rounded_rectangle((120 * s, 40 * s, 390 * s, 68 * s), 12 * s, fill=(190, 196, 206)); d.text((120 * s, 76 * s), "Sponsored", font=A.font("m", 26 * s), fill=(120, 126, 136))
            d.text((30 * s, 130 * s), "Re-roofs across Dublin. Free quotes.", font=A.font("m", 32 * s), fill=(30, 34, 40))
            g = A.gradient((w * s, 470 * s), (40, 60, 100), (120, 150, 200), 90); im.paste(g, (0, 190 * s))
            d.polygon([(110 * s, 450 * s), (410 * s, 250 * s), (710 * s, 450 * s)], fill=(50, 54, 66))
            for j in range(6): d.line((150 * s, (430 - j * 30) * s, 670 * s, (430 - j * 30) * s), fill=(76, 82, 98), width=3 * s)
            d.rectangle((160 * s, 450 * s, 660 * s, 660 * s), fill=(235, 228, 214)); d.rectangle((370 * s, 540 * s, 450 * s, 660 * s), fill=(120, 80, 60))
            d.rectangle((210 * s, 500 * s, 300 * s, 580 * s), fill=(255, 220, 140)); d.rectangle((520 * s, 500 * s, 610 * s, 580 * s), fill=(255, 220, 140))
            d.text((30 * s, 690 * s), "Need a new roof? Get a quote today.", font=A.font("b", 36 * s), fill=(20, 24, 30))
            d.rounded_rectangle((30 * s, 790 * s, (w - 30) * s, 900 * s), 24 * s, fill=(20, 70, 170) if pressed else (30, 100, 220))
            f = A.font("b", 42 * s); tw = A.tsize("Get quote", f)[0]; d.text((w * s / 2 - tw / 2, 818 * s), "Get quote", font=f, fill=WHITE)
        return sprite(w, h, fn)
    fill = [filler(i) for i in range(5)]; a0, a1 = ad(False), ad(True); ok = A.toast("Quote requested")
    body = sprite(PW, PH, lambda d, s, im: (d.rounded_rectangle((0, 0, PW * s - 1, PH * s - 1), 130 * s, fill=(20, 20, 20)),
                                            d.rounded_rectangle((16 * s, 16 * s, (PW - 16) * s, (PH - 16) * s), 116 * s, fill=(236, 238, 242))))
    scr = Image.new("L", (PW, PH), 0); ImageDraw.Draw(scr).rounded_rectangle((22, 22, PW - 22, PH - 22), 110, fill=255)
    lab = shadowed(pill("FIRST AD THEY SEE", 40, A.TH["accent"], DARK, w="bl"), blur=16, dy=8, alpha=120, pad=26)
    moon = sprite(90, 90, lambda d, s, im: (d.ellipse((0, 0, 90 * s, 90 * s), fill=(255, 230, 160)), d.ellipse((26 * s, -6 * s, 110 * s, 78 * s), fill=(0, 0, 0, 0))))

    def fn(t):
        im = A.bg(); sh = 0; b = t >= win_at
        im.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 20, 70)))  # night tint
        header(im, lines_b if b else lines_a, t, 290, 100, win_at if b else 0)
        ph = body.copy(); feed = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        off = 3600 * (1 - eo(clamp((t - 0.2) / (land_at - 0.2)))) if t < land_at else 0  # flick, then settle on the ad
        y = 230 - off
        for i, f in enumerate(fill):
            put(feed, f, PW / 2, y - (len(fill) - i) * 660 + 310, 1)
        press = abs(t - tap_at) < 0.1; put(feed, a1 if press else a0, PW / 2, y + 500, 1, 0.985 if press else 1)
        if 0 < off: feed = feed.filter(ImageFilter.BoxBlur(min(6, off / 300)))
        if t > tap_at + 0.15: put(feed, ok, PW / 2, 1430, clamp((t - tap_at - 0.15) / 0.2), 0.9 + 0.1 * spring((t - tap_at - 0.15) / 0.4))
        feed.putalpha(ImageChops.multiply(feed.split()[3], scr)); ph.alpha_composite(feed)
        dd = ImageDraw.Draw(ph); dd.rectangle((22, 22, PW - 22, 150), fill=(236, 238, 242)); dd.rounded_rectangle((PW // 2 - 130, 52, PW // 2 + 130, 120), 34, fill=(0, 0, 0))
        dd.text((96, 58), clock, font=A.font("sb", 44), fill=(20, 20, 20))
        cy = 580 + PH * k_ / 2 + 800 * (1 - spring(t / 0.8, f=1.6, d=6))
        put(im, ph, W / 2, cy, 1, k_)
        put(im, moon, W - 140, 520, eo(t / 0.4))
        A.tap(im, W / 2 + 120, cy - PH * k_ / 2 + (230 + 500 + 345) * k_, t, tap_at)
        lk = (t - land_at) / 0.3
        if lk > 0: put(im, lab, W / 2, 560, clamp(lk / 0.2), 1.3 - 0.3 * eo(lk), -3)
        if 0 <= lk < 0.4: sh = 8 * (1 - lk / 0.4)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.6), (0.25, "swish", 0.6), (land_at, "hit", 0.8), (tap_at, "click", 1.0), (tap_at + 0.15, "ping", 0.7), (win_at, "hit", 0.8)]


# ---------------------------------------------------------------- BODY 1c: good at roofing loses to easy to find
def scene_versus(dur=4.0, loses_at=1.4, easy_at=2.4):
    """GOOD AT ROOFING card gets knocked down and greyed with a LOSES stamp; EASY TO FIND card punches up gold with a ring"""
    def card(title, sub, gold):
        return A.card_sprite(900, 300, lambda d, s: (d.text((56 * s, 60 * s), title, font=A.font("bl", fit_size(title, "bl", 96, 790) * s), fill=DARK if gold else A.TH["card_ink"]),
                                                     d.text((60 * s, 200 * s), sub, font=A.font("sb", 38 * s), fill=(60, 50, 20) if gold else A.TH["muted"])),
                             fill=A.TH["accent"] if gold else None, radius=44, outline=None if gold else (60, 78, 110))
    good = card("GOOD AT ROOFING", "The lad with the best work", False); easy = card("EASY TO FIND", "The lad they see first", True)
    loses = stamp("LOSES TO", RED, 64)

    def fn(t):
        im = A.bg(); sh = 0
        k = eo(t / 0.35); gk = (t - loses_at) / 0.5
        gy = 700 + 40 * (1 - k) + (60 * eo(gk) if gk > 0 else 0); grot = -5 * eo(gk) if gk > 0 else 0
        g = good
        if gk > 0:  # knocked: dim it
            g = good.copy(); ov = Image.new("RGBA", g.size, (10, 16, 30, 0)); ov.putalpha(g.split()[3].point(lambda v: int(v * 0.5 * clamp(gk)))); g.alpha_composite(ov)
        put(im, g, W / 2, gy, clamp(t / 0.2), 1 - 0.06 * eo(gk) if gk > 0 else 1, grot)
        if gk > 0: put(im, loses, W / 2 + 40, 1010, clamp(gk / 0.3), 1.6 - 0.6 * eo(gk), -6)
        ek = (t - easy_at) / 0.4
        if ek > 0:
            put(im, easy, W / 2, 1330, clamp(ek / 0.2), 0.7 + 0.3 * back(ek)); ring(im, W / 2, 1330, ek / 1.4, maxr=600, width=8, r0=200)
        for h_ in (loses_at, easy_at):
            if h_ <= t < h_ + 0.16: sh = 12 * (1 - (t - h_) / 0.16)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5), (loses_at, "hit", 0.9), (easy_at, "hit", 1.0), (easy_at + 0.05, "shimmer", 0.7)]
