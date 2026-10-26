"""PLUMBERS 'The Setup' scenes: sells the system (3 steps), not an outcome. Interactive beats: a poll sticker that gets
tapped, a count-along checklist. Simple dark look: near-black, white type, ONE hi-vis yellow accent (TH['accent']);
the highlighter is yellow with dark text, like a real one. Calm pace: one idea per beat, key lines hold ~1s.
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed
from stack_scenes import Line as _Line, camera

INK = (14, 16, 20); WHITE = (255, 255, 255); MUTED = (150, 156, 166); CARD_MUTED = (120, 124, 132); BAR = (236, 237, 240)
def ACC(): return A.TH["accent"]


def Line(s, size, hi=None, w="bl", maxw=960):
    """white words; highlighted words turn dark on the yellow marker"""
    l = _Line(s, size, hi, w, maxw, WHITE); l.wh = [text(x, w, l.size, INK) for x in l.words]; return l


def card(w, h, draw=None, fill=WHITE, r=34):
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), r * s, fill=fill)
        if draw: draw(d, s)
    return shadowed(sprite(w, h, fn), blur=26, dy=14, alpha=120, pad=50)


def ctext(d, s, x, y, txt, f, col):
    """centred text helper for sprite drawing (x, y in 1x units)"""
    tw, th, ox, oy = A.tsize(txt, f); d.text((x * s - tw / 2 - ox, y * s - th / 2 - oy), txt, font=f, fill=col)


def tick(d, s, x, y, r=22, col=INK):
    d.line([((x - r * 0.45) * s, y * s), ((x - r * 0.1) * s, (y + r * 0.35) * s), ((x + r * 0.5) * s, (y - r * 0.4) * s)], fill=col, width=int(6 * s), joint="curve")


# ======================================================================= 01 HOOK  (interactive poll)
def scene_hook(dur=3.9, tap_at=1.05, stats_at=1.55, hl_at=2.15):
    """frame 0: 'Plumbers,' + a poll sticker 'Ever boosted a post?'. A finger taps YES, the bar fills yellow.
    The boosted post's stats slide up: 42 likes, 3 comments, 0 calls -> '0 calls' highlighted, camera zooms in."""
    big = text("Plumbers,", "bl", fit_size("Plumbers,", "bl", 230, 960), ACC())
    PW_, PH_ = 820, 400
    _pc = {}
    def poll(p):
        k = round(p, 2)
        if k in _pc: return _pc[k]
        def dr(d, s):
            ctext(d, s, PW_ / 2, 78, "Ever boosted a post?", A.font("bl", 56 * s), INK)
            for i, (lab, y) in enumerate((("Yes", 150), ("No", 275))):
                d.rounded_rectangle((50 * s, y * s, (PW_ - 50) * s, (y + 96) * s), 48 * s, fill=BAR)
                if i == 0 and k > 0: d.rounded_rectangle((50 * s, y * s, (50 + max(96, (PW_ - 100) * eo(k))) * s, (y + 96) * s), 48 * s, fill=ACC())
                ctext(d, s, PW_ / 2, y + 48, lab, A.font("bl", 44 * s), INK)
                if i == 0 and k >= 1: d.ellipse(((PW_ - 120) * s, (y + 22) * s, (PW_ - 68) * s, (y + 74) * s), fill=INK); tick(d, s, PW_ - 94, y + 48, 18, ACC())
        _pc[k] = card(PW_, PH_, dr, r=44); return _pc[k]
    SW_, SH_ = 820, 230; COLS = [(140, "42", "likes"), (410, "3", "comments"), (680, "0", "calls")]
    def stats(hl):
        def dr(d, s):
            d.text((40 * s, 24 * s), "YOUR BOOSTED POST", font=A.font("monob", 26 * s), fill=CARD_MUTED)
            if hl: d.rounded_rectangle((560 * s, 70 * s, 800 * s, 210 * s), 26 * s, fill=ACC())
            for x, n, lab in COLS:
                ctext(d, s, x, 120, n, A.font("bl", 76 * s), INK); ctext(d, s, x, 178, lab, A.font("sb", 32 * s), INK if lab == "calls" else CARD_MUTED)
        return card(SW_, SH_, dr, r=36)
    S0, S1 = stats(False), stats(True); POLL_Y, STATS_Y = 820, 1230

    def fn(t):
        im = A.bg(); sh = 10 * (1 - t / 0.16) if t < 0.16 else 0
        put(im, big, W / 2, 430, 1, 1.08 - 0.08 * eo(t / 0.3))
        put(im, poll((t - tap_at) / 0.3 if t > tap_at else 0), W / 2, POLL_Y, 1, 0.97 + 0.03 * eo(t / 0.3) - 0.02 * clamp(1 - abs(t - tap_at) / 0.1))
        A.tap(im, W / 2 + 230, POLL_Y - 200 + 198, t, tap_at, t_in=0.5, from_dx=140, from_dy=300)
        if t >= stats_at:
            k = (t - stats_at) / 0.45; put(im, S1 if t >= hl_at else S0, W / 2, STATS_Y + 220 * (1 - eo(k)), clamp(k / 0.25), 0.95 + 0.05 * back(k))
            if hl_at <= t < hl_at + 0.14: sh = 10
        return im, sh
    ev = [(0.0, "hit", 1.0), (tap_at - 0.05, "click", 1.0), (tap_at + 0.05, "pop", 0.6), (stats_at, "swish", 0.6), (hl_at, "hit", 0.9), (hl_at + 0.6, "whoosh", 0.6)]
    zx, zy = W / 2 - SW_ / 2 + 680, STATS_Y + 25
    return camera((dur, fn, ev), [(hl_at + 0.55, 1.0, W / 2, 960), (hl_at + 1.0, 1.5, zx - 60, zy), (dur, 1.55, zx - 60, zy)])


# ======================================================================= 02 LEAD
def scene_lead(dur=3.2, strike_at=0.7, need_at=1.15, hl_at=1.6):
    """'You don't need more posts.' (yellow strike through 'more posts.') -> 'You need a SYSTEM.' highlight + zoom"""
    l1 = Line("You don't need more posts.", 84); l2 = Line("You need a", 110); l3 = Line("system.", 200, hi=(0, 0))
    sx0 = W / 2 + l1.xs[3] - l1.ink[3].width / 2 - 10; sx1 = W / 2 + l1.xs[4] + l1.ink[4].width / 2 + 10
    zx, zy = l3.hi_centre(W / 2, 1180)

    def fn(t):
        im = A.bg(); l1.draw(im, W / 2, 760, t / 0.3)
        p = eo((t - strike_at) / 0.3)
        if p > 0: ImageDraw.Draw(im).rounded_rectangle((sx0, 755, sx0 + (sx1 - sx0) * p, 771), 8, fill=ACC())
        l2.draw(im, W / 2, 960, (t - need_at) / 0.3); l3.draw(im, W / 2, 1180, (t - need_at - 0.2) / 0.3, (t - hl_at) / 0.35)
        return im, (10 if hl_at + 0.1 <= t < hl_at + 0.24 else 0)
    ev = [(0.0, "whoosh", 0.5), (strike_at, "swish", 0.7), (need_at, "swish", 0.4), (need_at + 0.2, "hit", 0.9), (hl_at, "swish", 0.7), (hl_at + 0.45, "whoosh", 0.6)]
    return camera((dur, fn, ev), [(hl_at + 0.45, 1.0, W / 2, 960), (hl_at + 0.9, 1.15, zx, zy - 60), (dur, 1.18, zx, zy - 60)])


# ======================================================================= 03 BODY 1  (interactive count-along)
def scene_body1(dur=4.9, drops=(0.75, 1.4, 2.05, 2.7), ask_at=3.55):
    """'How many have you tried?' Four tactics drop into a stacking list, each box ticks as it lands and a big
    counter climbs 1/4..4/4 so the viewer counts along. Then 'Tried 2 or more? Keep watching.'"""
    items = ["Boosting posts", "Leaflet drops", "Paying lead sites", "Waiting on word of mouth"]
    h1, h2 = Line("Count along.", 92), Line("How many have you tried?", 76, hi=(4, 4))
    def item(s_, on):
        def dr(d, s):
            d.rounded_rectangle((30 * s, 26 * s, 98 * s, 94 * s), 18 * s, fill=ACC() if on else WHITE, outline=None if on else (200, 202, 208), width=4 * s)
            if on: tick(d, s, 64, 60, 26)
            d.text((130 * s, 34 * s), s_, font=A.font("b", 46 * s), fill=INK)
        return card(860, 120, dr, r=30)
    C = [(item(s_, False), item(s_, True)) for s_ in items]
    q1 = text("Tried 2 or more?", "bl", 84); q2 = A.pill("Keep watching.", 46, ACC(), INK, w="bl")

    def fn(t):
        im = A.bg(); sh = 0; h1.draw(im, W / 2, 360, t / 0.3); h2.draw(im, W / 2, 460, (t - 0.2) / 0.3, (t - 0.45) / 0.35)
        n = 0
        for i, d0 in enumerate(drops):
            k = (t - d0) / 0.45
            if k <= 0: continue
            on = t >= d0 + 0.3; n += on
            put(im, C[i][on], W / 2, 640 + i * 150 - 520 * (1 - spring(k, f=1.5, d=6.5)), clamp(k / 0.15), 1, (5 if i % 2 else -5) * (1 - eo(k * 1.3)))
            if 0.3 <= t - d0 < 0.42: sh = 7
        if n and t < ask_at:  # counter: big yellow number / 4, pops on every tick
            lt = drops[n - 1] + 0.3; pop = 1 + 0.25 * (1 - eo((t - lt) / 0.25))
            put(im, text(f"{n}", "bl", 230, ACC()), W / 2 - 70, 1350, 1, pop); put(im, text("/4", "bl", 120, MUTED), W / 2 + 90, 1390)
        if t >= ask_at:
            k = (t - ask_at) / 0.3; put(im, q1, W / 2, 1300, clamp(k / 0.2), 1.15 - 0.15 * eo(k))
            kk = (t - ask_at - 0.45) / 0.35; put(im, q2, W / 2, 1440, clamp(kk / 0.2), 0.7 + 0.3 * back(kk))
        return im, sh
    ev = [(0.0, "whoosh", 0.4), (0.45, "swish", 0.6)] + sum([[(d0 + 0.28, "hit", 0.5), (d0 + 0.3, "pop", 0.7)] for d0 in drops], []) + \
         [(ask_at, "hit", 0.8), (ask_at + 0.45, "pop", 0.8)]
    return dur, fn, ev


# ======================================================================= 04 / 06 OPEN LOOPS (questions)
def scene_question(lines, hi_line, hi, dur=3.0, gap=0.35, mode="rise", zoom=1.5, size=100, word_gap=0.13):
    """question lines come in, the key word gets the yellow highlighter, everything else fades back and the camera
    pushes in on it"""
    n = len(lines); ys = [960 - (n - 1) * 75 + j * 150 for j in range(n)]
    L = [Line(s, size + (16 if j == hi_line else 0), hi=hi if j == hi_line else None) for j, s in enumerate(lines)]
    starts, k = [], 0.05
    for l in L:
        if mode == "pop": starts.append([k + i * word_gap for i in range(len(l.words))]); k += len(l.words) * word_gap
        else: starts.append([k] * len(l.words)); k += gap
    t_hi = k + 0.3; t_z = t_hi + 0.45; zx, zy = L[hi_line].hi_centre(W / 2, ys[hi_line])

    def fn(t):
        im = A.bg()
        for j, l in enumerate(L):
            l.draw(im, W / 2, ys[j], [(t - s0) / 0.3 for s0 in starts[j]], (t - t_hi) / 0.3 if j == hi_line else 0, mode)
        dim = eo((t - t_z) / 0.35)
        if dim > 0: im.alpha_composite(Image.new("RGBA", (W, H), A.TH["bg"][0] + (int(200 * dim),))); L[hi_line].draw_hi(im, W / 2, ys[hi_line])
        return im, 0
    ev = [(s[0], "swish", 0.45) for s in starts] if mode == "rise" else [(s0, "pop", 0.35) for s in starts for s0 in s]
    ev += [(t_hi, "swish", 0.7), (t_z, "whoosh", 0.7), (t_z + 0.4, "hit", 0.6)]
    return camera((dur, fn, ev), [(t_z, 1.0, W / 2, 960), (t_z + 0.5, zoom, zx, zy), (dur, zoom * 1.04, zx, zy)])


def step_chip(n):
    return A.pill(f"STEP {n} OF 3", 34, ACC(), INK, w="bl")


# ======================================================================= 05 BODY 2  (step 1: targeting)
def scene_step1(dur=5.0, ring_at=(1.0, 2.0), line_at=3.1):
    """STEP 1: 'Your ad only shows to homeowners near you.' A dark map with house icons; your pin drops, a radius ring
    sweeps out and every house inside lights up yellow one by one; houses outside stay grey."""
    chip = step_chip(1); h1, h2 = Line("Your ad only shows", 78), Line("to homeowners near you.", 78, hi=(2, 3))
    MX, MY, MW, MH = W / 2, 1090, 940, 860; R = 330
    rng = np.random.default_rng(12); houses = []
    while len(houses) < 90:
        x, y = rng.uniform(MX - MW / 2 + 40, MX + MW / 2 - 40), rng.uniform(MY - MH / 2 + 40, MY + MH / 2 - 40)
        if math.hypot(x - MX, y - MY) > 60: houses.append((x, y, math.hypot(x - MX, y - MY)))
    def t_lit(d):  # when the ring (r = R*eo(p)) reaches distance d
        if d >= R: return None
        return ring_at[0] + (ring_at[1] - ring_at[0]) * (1 - (1 - d / R) ** 0.25)
    LIT = [t_lit(d) for _, _, d in houses]
    def base_map():
        m = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(m)
        d.rounded_rectangle((MX - MW / 2, MY - MH / 2, MX + MW / 2, MY + MH / 2), 40, fill=(22, 26, 33))
        for a, b in (((MX - MW / 2, MY - 120), (MX + MW / 2, MY + 60)), ((MX - 200, MY - MH / 2), (MX + 90, MY + MH / 2)), ((MX - MW / 2, MY + 300), (MX + MW / 2, MY + 250))):
            d.line((a, b), fill=(36, 41, 50), width=18)
        return m
    MAP = base_map(); pin = text("YOU", "bl", 34, INK); patch = text("Not the whole country. Just your patch.", "xb", fit_size("Not the whole country. Just your patch.", "xb", 50, 960))
    km = A.pill("25 km", 34, ACC(), INK, w="bl")

    def house(d, x, y, col, s=1.0):
        r = 13 * s; d.polygon([(x, y - r * 1.5), (x - r * 1.2, y - r * 0.3), (x + r * 1.2, y - r * 0.3)], fill=col); d.rectangle((x - r, y - r * 0.35, x + r, y + r), fill=col)

    def fn(t):
        im = A.bg(); put(im, chip, W / 2, 335, eo(t / 0.25), 0.8 + 0.2 * back(t / 0.35))
        h1.draw(im, W / 2, 440, (t - 0.1) / 0.3); h2.draw(im, W / 2, 535, (t - 0.25) / 0.3, (t - 0.55) / 0.35)
        k = eo((t - 0.3) / 0.4)
        if k > 0:
            mp = MAP.copy(); mp.putalpha(mp.split()[3].point(lambda v: int(v * k))); im.alpha_composite(mp)
        d = ImageDraw.Draw(im)
        rp = (t - ring_at[0]) / (ring_at[1] - ring_at[0])
        if rp > 0:
            r = R * eo(rp); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).ellipse((MX - r, MY - r, MX + r, MY + r), fill=ACC() + (28,), outline=ACC() + (230,), width=5); im.alpha_composite(o)
        d = ImageDraw.Draw(im)
        for (x, y, _), tl in zip(houses, LIT):
            if k <= 0: break
            if tl is not None and t >= tl: house(d, x, y, ACC(), 1 + 0.5 * (1 - eo((t - tl) / 0.25)))
            else: house(d, x, y, (78, 84, 96) if tl is None or t < tl else ACC())
        pk = (t - 0.75) / 0.4  # pin drops in
        if pk > 0:
            py = MY - 260 * (1 - spring(pk, f=1.5, d=6))
            d.ellipse((MX - 46, py - 110, MX + 46, py - 18), fill=ACC()); d.polygon([(MX - 34, py - 50), (MX + 34, py - 50), (MX, py)], fill=ACC())
            put(im, pin, MX, py - 64)
        if rp > 0.8: put(im, km, MX + R * 0.72 + 30, MY - R * 0.72, eo((rp - 0.8) / 0.3), back((rp - 0.8) / 0.4))
        put_rise(im, patch, W / 2, 1590, eo((t - line_at) / 0.35))
        return im, 0
    ev = [(0.0, "pop", 0.7), (0.25, "swish", 0.5), (0.55, "swish", 0.6), (0.85, "hit", 0.6), (ring_at[0], "whoosh", 0.6)] + \
         [(tl, "tick", 0.25) for tl in sorted(x for x in LIT if x is not None)[::3]] + [(ring_at[1], "shimmer", 0.6), (line_at, "swish", 0.5)]
    return dur, fn, ev


# ======================================================================= 07 BODY 3  (steps 2 + 3: questions, then your phone)
def scene_steps23(dur=6.0, drops=(0.75, 1.25, 1.75), swap=2.9, buzz_at=3.65):
    """STEP 2: 'They answer 3 questions first.' answer cards stack in. STEP 3: 'Then it texts your phone.'
    the cards fly up out, a phone rises, the job enquiry drops onto the lock screen with a buzz."""
    qa = [("What's the job?", "Boiler not firing"), ("Where?", "Swords"), ("When?", "This week")]
    c2, c3 = step_chip(2), step_chip(3)
    a1, a2 = Line("They answer", 84), Line("3 questions first.", 84, hi=(0, 1))
    b1, b2 = Line("Then it texts", 84), Line("straight to your phone.", 84, hi=(2, 3))
    def qcard(q, a):
        def dr(d, s):
            d.text((40 * s, 22 * s), q, font=A.font("sb", 30 * s), fill=CARD_MUTED); d.text((40 * s, 62 * s), a, font=A.font("bl", 48 * s), fill=INK)
            d.ellipse((770 * s, 46 * s, 822 * s, 98 * s), fill=ACC()); tick(d, s, 796, 72, 18)
        return card(860, 140, dr, r=30)
    Q = [qcard(q, a) for q, a in qa]
    ph = A.phone("Tuesday 28 October", "10:14", wall=((30, 34, 42), (10, 12, 16), ACC()))
    def note():
        w, h = 860, 210
        def dr(d, s):
            d.rounded_rectangle((32 * s, 40 * s, 120 * s, 128 * s), 24 * s, fill=ACC()); ctext(d, s, 76, 84, "S", A.font("bl", 54 * s), INK)
            d.text((150 * s, 36 * s), "NEW JOB ENQUIRY", font=A.font("sb", 26 * s), fill=CARD_MUTED)
            f = A.font("m", 26 * s); d.text(((w - 40) * s - A.tsize("now", f)[0], 36 * s), "now", font=f, fill=CARD_MUTED)
            d.text((150 * s, 74 * s), "Boiler not firing", font=A.font("bl", 42 * s), fill=INK)
            d.text((150 * s, 130 * s), "Mary · Swords · this week", font=A.font("m", 32 * s), fill=(70, 74, 82))
        return card(w, h, dr, fill=(250, 250, 250), r=46)
    N = note()

    def fn(t):
        im = A.bg(); sh = 0
        if t < swap + 0.35:  # STEP 2 (cards fly up and away during the swap)
            out = eio((t - swap) / 0.35)
            if out < 1:
                put(im, c2, W / 2, 335 - 300 * out, eo(t / 0.25) * (1 - out), 0.8 + 0.2 * back(t / 0.35))
                a1.draw(im, W / 2 - 1200 * out, 445, (t - 0.1) / 0.3); a2.draw(im, W / 2 - 1200 * out, 545, (t - 0.25) / 0.3, (t - 0.55) / 0.35)
                for i, d0 in enumerate(drops):
                    k = (t - d0) / 0.45
                    if k > 0: put(im, Q[i], W / 2, 760 + i * 175 - 520 * (1 - spring(k, f=1.5, d=6.5)) - 1400 * out * out, clamp(k / 0.15) * (1 - out), 1, (5 if i % 2 else -5) * (1 - eo(k * 1.3)))
                    if 0.3 <= t - d0 < 0.42: sh = 7
        if t >= swap:  # STEP 3
            u = t - swap
            put(im, c3, W / 2, 335, eo(u / 0.25), 0.8 + 0.2 * back(u / 0.35))
            b1.draw(im, W / 2, 445, (u - 0.1) / 0.3); b2.draw(im, W / 2, 545, (u - 0.25) / 0.3, (u - 0.55) / 0.35)
            k = eo((u - 0.15) / 0.5); hap = 8 * math.sin((t - buzz_at) * 140) if 0 <= t - buzz_at < 0.25 else 0
            put(im, ph, W / 2 + hap, 1230 + 700 * (1 - k), k, 0.56)
            if t >= buzz_at:
                kk = (t - buzz_at) / 0.45; put(im, N, W / 2 + hap, 1120 - 200 * (1 - spring(kk, f=1.5, d=6)), clamp(kk / 0.15), 0.9 + 0.1 * back(kk))
                ring(im, W / 2, 1120, kk / 1.5, col=ACC(), maxr=460, width=6, r0=200)
        return im, sh
    ev = [(0.0, "pop", 0.7), (0.25, "swish", 0.5), (0.55, "swish", 0.6)] + [(d0 + 0.28, "hit", 0.55) for d0 in drops] + \
         [(swap, "whoosh", 0.7), (swap + 0.3, "pop", 0.7), (swap + 0.55, "swish", 0.6), (buzz_at, "ping", 0.9), (buzz_at + 0.05, "hit", 0.6)]
    return dur, fn, ev
