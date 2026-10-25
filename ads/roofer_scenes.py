"""Scenes for the Southline roofers 'storm season' ad (navy + gold theme). Built on adkit + volt_scenes helpers.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, pill, fit_size, eo, eio, back, spring, clamp, ring, underline, sprite, shadowed
from volt_scenes import RED, WHITE, DARK, header

_rng = np.random.default_rng(3)
_DROPS = [(_rng.uniform(-200, W + 200), _rng.uniform(0, H), _rng.uniform(40, 90), _rng.uniform(0.6, 1.0)) for _ in range(140)]


def rain(im, t, amount=1.0, speed=2600):
    """diagonal rain streaks over the frame (deterministic, so it loops cleanly)"""
    if amount <= 0: return
    o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    for x, y, ln, a in _DROPS[:int(len(_DROPS) * amount)]:
        yy = (y + t * speed * a) % (H + 200) - 100; xx = x - (yy - y) * 0.18
        d.line((xx, yy, xx - ln * 0.18, yy + ln), fill=(200, 215, 240, int(70 * a)), width=3)
    im.alpha_composite(o)


def flash(im, k, strength=0.55):
    """lightning flash: white wash fading out over k 0->1"""
    if 0 <= k < 1: im.alpha_composite(Image.new("RGBA", (W, H), (235, 240, 255, int(255 * strength * (1 - k) ** 2))))


def bolt(d, cx, cy, s, col):
    d.polygon([(cx + 8 * s, cy - 44 * s), (cx - 24 * s, cy + 6 * s), (cx - 2 * s, cy + 6 * s), (cx - 10 * s, cy + 44 * s),
               (cx + 24 * s, cy - 8 * s), (cx + 2 * s, cy - 8 * s)], fill=col)


# ---------------------------------------------------------------- opener
def scene_storm_calls(word="Roofers,", l1="IF YOUR PHONE ONLY RINGS", l2="AFTER A STORM…", dur=4.0, flash_at=0.5, rise_at=1.2):
    """frame 0: giant gold 'Roofers,' + a 'CALLS PER WEEK' bar chart, flat except one storm spike, both fully on screen
    mid-slam. Lightning hits the spike at flash_at, rain falls, then the line rises in."""
    big = text(word, "bl", fit_size(word, "bl", 260, 940), grad=(A.TH["accent"], A.TH["accent2"], 0))
    s1 = text(l1, "xb", fit_size(l1, "xb", 76, 960)); s2 = text(l2, "xb", fit_size(l2, "xb", 92, 960), A.TH["accent"])
    vals = [1.2, 0.8, 1.0, 0.6, 9.0, 6.5, 1.0, 0.4, 0.7, 0.3]; X0, X1, Y0, Y1 = 150, 930, 760, 1180
    bw = (X1 - X0) / len(vals) * 0.62; lab = text("CALLS PER WEEK", "b", 34, A.TH["muted"])
    storm = shadowed(pill("STORM", 34, A.TH["accent"], w="bl"), blur=14, dy=8, alpha=110, pad=26)
    quiet = pill("QUIET", 28, (90, 30, 30), RED, w="bl")

    def fn(t):
        im = A.bg(); sh = 12 * (1 - t / 0.2) if t < 0.2 else 0
        put(im, big, W / 2, 420, 1, 1.06 - 0.06 * eo(t / 0.28))
        underline(im, big, W / 2, 420 + big.height / 2 + 2, 0.35 + (t - 0.05) / 0.3, h=14)
        d = ImageDraw.Draw(im); put(im, lab, X0 + lab.width / 2, Y0 - 50, 1)
        d.line((X0, Y1, X1, Y1), fill=(70, 84, 110), width=3)
        hit = t >= flash_at; pulse = 1 + (0.06 * math.sin((t - flash_at) * 10) * math.exp(-(t - flash_at) * 1.5) if hit else 0)
        for i, v in enumerate(vals):
            x = X0 + (i + 0.5) * (X1 - X0) / len(vals); h = (Y1 - Y0 - 40) * v / 9 * (pulse if v > 5 else 1)
            col = A.TH["accent"] if v > 5 else (80, 94, 124)
            d.rounded_rectangle((x - bw / 2, Y1 - max(h, 10), x + bw / 2, Y1 - 2), 12, fill=col)
        sx = X0 + 4.5 * (X1 - X0) / len(vals) - (X1 - X0) / len(vals) / 2
        put(im, storm, X0 + 5 * (X1 - X0) / len(vals), Y0 - 6, 1, 1 + (0.3 * (1 - eo((t - flash_at) / 0.3)) if hit else 0))
        put(im, quiet, X0 + 8 * (X1 - X0) / len(vals), Y1 - 70, 1)
        if hit:
            k = (t - flash_at) / 0.25
            if k < 1:
                o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bolt(ImageDraw.Draw(o), sx + 120, Y0 - 140, 3.2, (255, 250, 220, int(255 * (1 - k))))
                im.alpha_composite(o.filter(ImageFilter.GaussianBlur(2)))
        rain(im, t, 0.6)
        flash(im, (t - flash_at) / 0.35)
        if flash_at <= t < flash_at + 0.18: sh = 14 * (1 - (t - flash_at) / 0.18)
        put_rise(im, s1, W / 2, 1330, eo((t - rise_at) / 0.32)); put_rise(im, s2, W / 2, 1440, eo((t - rise_at - 0.5) / 0.32))
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (flash_at, "glitch", 0.8), (flash_at, "hit", 0.9), (rise_at, "whoosh", 0.4)]


# ---------------------------------------------------------------- small wet jobs
def scene_patch_jobs(jobs, drops, dur=3.5, lines=(("UP A LADDER", False), ("IN THE RAIN…", True))):
    """rain + small patch-job cards stacking, each with its tiny price. jobs=[(title, sub, value)]"""
    cards = [A.job_card(a, b, A.money(v), icon="house", value_col=A.TH["muted"]) for a, b, v in jobs]

    def fn(t):
        im = A.bg(); header(im, lines, t, 330, 120)
        sh = A.draw_stack(im, cards, drops, t, 1050, step=70, from_y=1300, rot=6)
        landed = [i for i, d0 in enumerate(drops) if t >= d0]
        if landed:
            fp = (t - drops[landed[-1]] - 0.3) / 0.7
            if 0 < fp < 1: put(im, text(A.money(jobs[landed[-1]][2]), "bl", 90, A.TH["accent"]), W / 2 + 300, 880 - 120 * eo(fp), 1 - fp)
        rain(im, t, 1.0)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5)] + sum([[(d, "swish", 0.4), (d + 0.3, "hit", 0.5), (d + 0.32, "coin", 0.4)] for d in drops], [])


# ---------------------------------------------------------------- big jobs going elsewhere
def big_card(title, sub):
    def dr(d, s):
        d.rounded_rectangle((40 * s, 45 * s, 160 * s, 165 * s), 30 * s, fill=tuple(int(c * 0.3) for c in A.TH["accent"]))
        bx, by = 100 * s, 105 * s
        d.polygon([(bx, by - 42 * s), (bx - 44 * s, by), (bx + 44 * s, by)], fill=A.TH["accent"]); d.rectangle((bx - 32 * s, by - 2 * s, bx + 32 * s, by + 40 * s), fill=A.TH["accent"])
        d.text((196 * s, 48 * s), title, font=A.font("bl", 52 * s), fill=A.TH["card_ink"])
        d.text((196 * s, 122 * s), sub, font=A.font("m", 34 * s), fill=A.TH["muted"])
        f = A.font("bl", 30 * s); tw, th, ox, oy = A.tsize("BIG JOB", f)
        d.rounded_rectangle(((900 - 40) * s - tw - 44 * s, 66 * s, (900 - 40) * s, 118 * s), 26 * s, fill=A.TH["accent"])
        d.text(((900 - 40) * s - tw - 22 * s - ox, 92 * s - th / 2 - oy), "BIG JOB", font=f, fill=DARK)
    return A.card_sprite(900, 210, dr, outline=(60, 78, 110))


def scene_big_jobs_gone(items, appear, gone_at, dur=5.0, lines=(("AND THE", False), ("BIG JOBS…", True)), gone_txt="GOING TO SOMEONE ELSE"):
    """big-ticket job cards slide in on their words, then get swept off to the right at gone_at with a red tag"""
    cards = [big_card(*it) for it in items]; tag = shadowed(pill(gone_txt + " →", 44, RED, WHITE, w="bl"), blur=18, dy=10, alpha=120, pad=30)

    def fn(t):
        im = A.bg(); sh = 0; header(im, lines, t, 330, 130)
        for i, (sp, ta) in enumerate(zip(cards, appear)):
            k = (t - ta) / 0.45
            if k <= 0: continue
            x = W / 2 - 700 * (1 - eo(k)); g = (t - gone_at - i * 0.07) / 0.45
            if g > 0: x += 1500 * eio(g) ** 1.6
            if x - 450 > W: continue
            put(im, sp, x, 760 + i * 250, clamp(k / 0.2), 1, -4 * eo(g) if g > 0 else 0)
        tk = (t - gone_at - 0.15) / 0.35
        if tk > 0:
            put(im, tag, W / 2, 1520, clamp(tk / 0.2), 1.4 - 0.4 * eo(tk), -3)
            if tk < 0.4: sh = 12 * (1 - tk / 0.4)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(a, "swish", 0.5) for a in appear] + [(a + 0.2, "pop", 0.6) for a in appear] + \
        [(gone_at, "whoosh", 1.0), (gone_at + 0.15, "hit", 0.9)]


# ---------------------------------------------------------------- storm week, then nothing
def scene_storm_diary(dur=5.0, clear_at=2.6, drain_at=3.6, A_lines=(("STORM HITS?", False), ("FLAT OUT FOR A WEEK.", True)),
                      B_lines=(("THE WEATHER CLEARS…", False), ("SO DOES YOUR DIARY.", True)), step_a=0.6, step_b=1.0):
    """2-week diary: storm week fills instantly with lightning + rain; weather clears and the jobs fall out of the diary"""
    cw, ch, gap = 180, 230, 15; x0 = (W - (5 * cw + 4 * gap)) / 2; ys = [700, 700 + ch + 70]; days = ("Mon", "Tue", "Wed", "Thu", "Fri")
    jobs = ["Leak", "Slates", "Ridge", "Valley", "Flashing", "Gutter", "Leak", "Slates", "Chimney", "Leak"]

    def cell(day, job):
        def dr(d, s):
            d.text((22 * s, 18 * s), day, font=A.font("sb", 30 * s), fill=A.TH["muted"])
            if job:
                d.rounded_rectangle((14 * s, 70 * s, (cw - 14) * s, 200 * s), 22 * s, fill=A.TH["accent"])
                f = A.font("b", 30 * s); tw, th, ox, oy = A.tsize(job, f); d.text((cw / 2 * s - tw / 2 - ox, 135 * s - th / 2 - oy), job, font=f, fill=DARK)
            else: d.rounded_rectangle((14 * s, 70 * s, (cw - 14) * s, 200 * s), 22 * s, outline=(80, 94, 124), width=2 * s)
        return A.card_sprite(cw, ch, dr, radius=30, shadow=False)
    empty = [cell(days[i % 5], None) for i in range(10)]; chips = [cell(days[i % 5], j) for i, j in enumerate(jobs)]
    fill_t = [0.25 + 0.05 * i for i in range(10)]; order = [9, 4, 7, 2, 8, 0, 5, 3, 6, 1]; fall_t = {c: drain_at + k * 0.11 for k, c in enumerate(order)}
    wk = [text("Storm week", "b", 40, A.TH["accent"]), text("Next week", "b", 40, A.TH["muted"])]

    def fn(t):
        im = A.bg(); sh = 0; b = t >= clear_at
        header(im, B_lines if b else A_lines, t, 330, 104, clear_at if b else 0, step_b if b else step_a)
        for r in range(2):
            put(im, wk[r], x0 + wk[r].width / 2, ys[r] - 40, 1)
            for c in range(5):
                i = r * 5 + c; cx = x0 + c * (cw + gap) + cw / 2; cy = ys[r] + ch / 2
                put(im, empty[i], cx, cy, 1)
                if t >= fill_t[i]:
                    f = (t - fall_t[i]) / 0.6
                    if f < 1: put(im, chips[i], cx, cy + (900 * f * f if f > 0 else 0), 1 - clamp(f), 0.9 + 0.1 * spring((t - fill_t[i]) / 0.3), 25 * f if f > 0 else 0)
        n = sum(1 for i in range(10) if t >= fill_t[i] and t < fall_t[i])
        if t >= fill_t[0]: put(im, pill(f"{n} jobs booked", 40, A.TH["accent"] if n >= 8 else (RED if n <= 2 else (60, 74, 100)), DARK if n >= 8 else WHITE), W / 2, 1500, 1)
        if not b: rain(im, t, 1.0); flash(im, t / 0.3, 0.45)
        if t < 0.18: sh = 12 * (1 - t / 0.18)
        return im, sh
    return dur, fn, [(0.0, "glitch", 0.7), (0.0, "hit", 0.9)] + [(x, "pop", 0.35) for x in fill_t[::2]] + [(clear_at, "shimmer", 0.6)] + \
        [(fall_t[i], "swish", 0.25) for i in order[::2]] + [(fall_t[order[-1]] + 0.3, "hit", 0.7)]


# ---------------------------------------------------------------- the other lad's ad
def scene_feed_steal(dur=6.0, never_at=2.4, tap_at=3.6, lines_a=(("THE HOMEOWNER WHO", False), ("NEEDED A NEW ROOF?", True)),
                     lines_b=(("THEY NEVER", False), ("RANG YOU.", True))):
    """phone feed: a competitor's sponsored roofing post (brand blurred), the homeowner taps 'Get quote', quote requested"""
    k = 0.66; PW, PH = A.PW, A.PH
    def post():
        w, h = 820, 980
        def fn(d, s, im):
            d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 40 * s, fill=(255, 255, 255))
            d.ellipse((30 * s, 30 * s, 110 * s, 110 * s), fill=(150, 160, 175))
            d.rounded_rectangle((130 * s, 40 * s, 400 * s, 70 * s), 12 * s, fill=(190, 196, 206))  # blurred-out brand name
            d.text((130 * s, 78 * s), "Sponsored", font=A.font("m", 26 * s), fill=(120, 126, 136))
            d.text((30 * s, 130 * s), "Full roof replacements across Dublin.", font=A.font("m", 32 * s), fill=(30, 34, 40))
            # illustrated house: sky, roof, walls
            g = A.gradient((w * s, 480 * s), (120, 160, 210), (200, 220, 240), 90); im.paste(g, (0, 190 * s))
            d.polygon([(110 * s, 450 * s), (410 * s, 250 * s), (710 * s, 450 * s)], fill=(60, 64, 76))
            for j in range(6): d.line(((150 + j * 0) * s, (430 - j * 30) * s, (670 - j * 0) * s, (430 - j * 30) * s), fill=(80, 86, 100), width=3 * s)
            d.rectangle((160 * s, 450 * s, 660 * s, 670 * s), fill=(235, 228, 214)); d.rectangle((370 * s, 540 * s, 450 * s, 670 * s), fill=(120, 80, 60))
            d.rectangle((210 * s, 500 * s, 300 * s, 580 * s), fill=(170, 200, 230)); d.rectangle((520 * s, 500 * s, 610 * s, 580 * s), fill=(170, 200, 230))
            d.rectangle((0, 670 * s, w * s, 760 * s), fill=(240, 242, 245))
            d.text((30 * s, 690 * s), "New roof? Free quote this week.", font=A.font("b", 36 * s), fill=(20, 24, 30))
        return sprite(w, h, fn)
    base = post()
    def btn(pressed):
        w, h = 760, 110
        return sprite(w, h, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 24 * s, fill=(30, 100, 220) if not pressed else (20, 70, 170)),
                                              d.text((w * s / 2 - A.tsize("Get quote", A.font("b", 40 * s))[0] / 2, 30 * s), "Get quote", font=A.font("b", 40 * s), fill=WHITE)))
    b0, b1 = btn(False), btn(True); ok = A.toast("Quote requested")
    label = shadowed(pill("THE OTHER LAD'S AD", 40, RED, WHITE, w="bl"), blur=16, dy=8, alpha=120, pad=26)
    screen = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    body = sprite(PW, PH, lambda d, s, im: (d.rounded_rectangle((0, 0, PW * s - 1, PH * s - 1), 130 * s, fill=(20, 20, 20)),
                                            d.rounded_rectangle((16 * s, 16 * s, (PW - 16) * s, (PH - 16) * s), 116 * s, fill=(236, 238, 242))))
    ImageDraw.Draw(body).rounded_rectangle((PW // 2 - 130, 52, PW // 2 + 130, 120), 34, fill=(0, 0, 0))
    ImageDraw.Draw(body).text((90, 60), "23:47", font=A.font("sb", 40), fill=(20, 20, 20))

    def fn(t):
        im = A.bg(); sh = 0; b = t >= never_at
        header(im, lines_b if b else lines_a, t, 300, 104, never_at if b else 0)
        ph = body.copy(); put(ph, base, PW / 2, 200 + 490, 1)
        press = abs(t - tap_at) < 0.1; put(ph, b1 if press else b0, PW / 2, 200 + 980 - 70 + 0, 1, 0.97 if press else 1)
        if t > tap_at + 0.15: put(ph, ok, PW / 2, 1360, clamp((t - tap_at - 0.15) / 0.2), 0.9 + 0.1 * spring((t - tap_at - 0.15) / 0.4))
        cy = 560 + PH * k / 2 + 900 * (1 - spring(t / 0.9, f=1.6, d=6))
        put(im, ph, W / 2, cy, 1, k)
        A.tap(im, W / 2 + 120, cy - PH * k / 2 + (200 + 910) * k, t, tap_at)
        lk = (t - never_at - 0.1) / 0.35
        if lk > 0: put(im, label, W / 2, 560, clamp(lk / 0.2), 1.3 - 0.3 * eo(lk), -3)
        if 0 <= lk < 0.4: sh = 10 * (1 - lk / 0.4)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.6), (never_at, "hit", 0.9), (tap_at, "click", 1.0), (tap_at + 0.15, "ping", 0.7)]
