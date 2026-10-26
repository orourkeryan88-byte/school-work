"""E-COMMERCE 'Three problems' scenes: same engine and look as the trust video (B-roll behind, white type with
shadows) in the brand's navy + gold. Built for retention: an open loop up front (three locked cards, #3 'the
expensive one' leaking money) and a 1 . 2 . 3 progress tracker that unlocks as each problem is revealed.
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, put_rise, text, eo, eio, back, spring, clamp, ring, sprite, shadowed
import trust_scenes as S
from trust_scenes import view, vignette, T, under, pop, rise, ctext, card, finger
import broll as B

GOLD = (226, 178, 92); NAVY = (14, 26, 48); WHITE = (255, 255, 255); INK = (16, 18, 24); MUTED = (120, 126, 138); DIM = (40, 48, 66)
S.ACC = GOLD  # the shared helpers (underlines, titles) pick up the gold accent


def coins(im, x0, y0, t, t0, n=10, spread=120):
    """gold € coins tumbling down from (x0, y0): money leaking"""
    if t < t0: return
    f = A.font("bl", 30)
    for i in range(n):
        p = ((t - t0) * 0.9 + i / n) % 1.0
        if (t - t0) * 0.9 + i / n < 1.0 and p < i / n: continue
        x = x0 + spread * math.sin(i * 2.3) * (0.4 + p); y = y0 + 520 * p * p; a = int(255 * (1 - p))
        o = Image.new("RGBA", (70, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        d.ellipse((5, 5, 65, 65), fill=GOLD + (a,)); tw = f.getlength("€"); d.text((35 - tw / 2, 14), "€", font=f, fill=NAVY + (a,))
        im.alpha_composite(o.rotate(p * 400 + i * 40), (int(x - 35), int(y - 35)))


def lock(d, cx, cy, s=1.0, col=GOLD):
    d.arc((cx - 26 * s, cy - 62 * s, cx + 26 * s, cy - 10 * s), 180, 360, fill=col, width=int(9 * s))
    d.line((cx - 26 * s, cy - 36 * s, cx - 26 * s, cy - 14 * s), fill=col, width=int(9 * s)); d.line((cx + 26 * s, cy - 36 * s, cx + 26 * s, cy - 14 * s), fill=col, width=int(9 * s))
    d.rounded_rectangle((cx - 42 * s, cy - 18 * s, cx + 42 * s, cy + 46 * s), 12 * s, fill=col); d.ellipse((cx - 8 * s, cy + 2 * s, cx + 8 * s, cy + 18 * s), fill=NAVY)


_trk = {}
def tracker(im, active, t):
    """1 . 2 . 3 progress pills at the top: done = white with a tick, current = gold, still locked = dim"""
    labs = ["1  Ads dying", "2  Tracking", "3  The expensive one"]
    def P(i, st):
        k = (i, st)
        if k not in _trk:
            s_ = labs[i] + ("  ✓" if st == "done" else "")
            bg, fg = {"done": (WHITE, INK), "now": (GOLD, NAVY), "lock": (DIM, (150, 158, 176))}[st]
            _trk[k] = A.pill(s_, 28, bg, fg, w="bl")
        return _trk[k]
    sps = [P(i, "done" if i < active else ("now" if i == active else "lock")) for i in range(3)]
    tot = sum(s_.width for s_ in sps) + 14 * 2; x = W / 2 - tot / 2
    for i, s_ in enumerate(sps):
        put(im, s_, x + s_.width / 2, 300, eo(t / 0.25), 1 + (0.15 * (1 - eo(t / 0.4)) if i == active else 0)); x += s_.width + 14


# ======================================================================= hook
def scene_hook(dur=8.4, l2_at=1.2, cards_at=(1.6, 1.95, 2.3), three_at=5.6):
    """frame 0: 'E-commerce brands,' slams over the warehouse; three locked cards drop in ('3 problems in your ad
    account you probably don't know about'); then #3 shakes, glows, and leaks money: 'the expensive one'"""
    h1, h2 = T("E-commerce", 160), T("brands,", 160, GOLD)
    c1, c2 = T("3 problems in your ad account", 74), T("you probably don't know about.", 70)
    c3 = T("And #3 costs you the most.", 76); tag = A.pill("the expensive one", 36, GOLD, NAVY, w="bl")
    def cardn(n):
        def dr(d, s):
            d.rounded_rectangle((3 * s, 3 * s, 257 * s, 337 * s), 30 * s, outline=GOLD, width=4 * s)
            ctext(d, 130 * s, 120 * s, str(n), A.font("bl", 140 * s), GOLD); lock(d, 130 * s, 250 * s, s * 0.9)
        return card(260, 340, dr, fill=(18, 26, 44), r=30, alpha=240)
    C = [cardn(i + 1) for i in range(3)]; X = [W / 2 - 300, W / 2, W / 2 + 300]
    def fn(t):
        z = 1.0 + 0.5 * (1 - eo(t / 0.9)); im = vignette(view(t * 0.9, z, 0.5, 0.6, dark=0.3 + 0.3 * clamp((t - l2_at) / 0.4)))
        sh = 14 if t < 0.14 else 0
        o = eio((t - l2_at + 0.1) / 0.35)  # the callout flies up and out
        if o < 1:
            put(im, h1, W / 2, 560 - 400 * o * o, 1 - o, 1.15 - 0.15 * back(t / 0.3)); put(im, h2, W / 2, 730 - 400 * o * o, 1 - o, 1.15 - 0.15 * back((t - 0.15) / 0.3))
        rise(im, c1, W / 2, 440, t, l2_at + 0.1); rise(im, c2, W / 2, 535, t, l2_at + 0.9)
        under(im, "you probably don't know about.", 70, W / 2, 535, "don't know about", (t - l2_at - 1.4) / 0.4)
        for i, (c_, x, t0) in enumerate(zip(C, X, cards_at)):
            k = (t - t0) / 0.5
            if k <= 0: continue
            shake = 10 * math.sin(t * 38) * clamp((t - three_at) / 0.2) * (1 - clamp((t - three_at - 0.9) / 0.4)) if i == 2 else 0
            put(im, c_, x + shake, 930 - 900 * (1 - spring(k, f=1.5, d=6)), clamp(k / 0.15), 1.12 if (i == 2 and t >= three_at) else 1, (-6, 2, 7)[i] * (1 - eo(k)))
            if 0.28 <= t - t0 < 0.4: sh = max(sh, 7)
        if t >= three_at:
            ring(im, X[2], 930, (t - three_at) / 1.0, col=GOLD, maxr=320, width=6, r0=120)
            coins(im, X[2], 1110, t, three_at + 0.4, n=8, spread=60)
            pop(im, tag, X[2] - 30, 1140, t, three_at + 0.2, 1.4)
            rise(im, c3, W / 2, 1330, t, three_at + 0.1); under(im, "And #3 costs you the most.", 76, W / 2, 1330, "the most", (t - three_at - 0.6) / 0.4)
        return im, sh
    ev = [(0.0, "hit", 1.0), (0.0, "whoosh", 0.4), (l2_at, "whoosh", 0.5), (l2_at + 0.1, "swish", 0.4), (l2_at + 0.9, "swish", 0.4)] + \
         [(t0 + 0.3, "hit", 0.55) for t0 in cards_at] + [(three_at, "glitch", 0.6), (three_at + 0.2, "pop", 0.7), (three_at + 0.4, "coin", 0.6), (three_at + 0.9, "coin", 0.4)]
    return dur, fn, ev


# ======================================================================= who's talking
def scene_ryan(dur=3.0):
    """'I'm Ryan, I run Southline. We run Meta ads.' name card with the logo slides in over the desk"""
    s1, s2 = T("I'm Ryan.", 130), T("We run Meta ads.", 84)
    logo = A.logo().resize((120, 120))
    def lt(d, s): d.text((170 * s, 34 * s), "Ryan", font=A.font("bl", 58 * s), fill=INK); d.text((172 * s, 104 * s), "Founder · Southline Agency", font=A.font("m", 30 * s), fill=MUTED)
    LT = card(700, 170, lt, alpha=245); LT.alpha_composite(logo, (50 + 26, 50 + 25))
    def fn(t):
        im = vignette(view(2.0 + 0.8 * t, 1.15 + 0.08 * eio(t / dur), 0.5, 0.45, dark=0.5))
        pop(im, s1, W / 2, 560, t, 0.1, 1.4); rise(im, s2, W / 2, 720, t, 1.4)
        k = eo((t - 0.6) / 0.45); put(im, LT, -400 + (W / 2 + 400) * k, 1350, k)
        return im, (8 if 0.1 <= t < 0.22 else 0)
    return dur, fn, [(0.1, "hit", 0.7), (0.6, "swish", 0.5), (1.4, "swish", 0.4)]


# ======================================================================= problem 1: ads dying
def scene_dying(dur=10.5, weeks_at=3.0, cost_at=5.5, algo_at=8.2):
    """'1. Your ads are dying faster than you think.' a product ad whose strength bar drains week by week, the card
    fading to grey; 'weeks, not months'; cost per sale ticking up (example); "the algorithm's broken" struck out"""
    h1, h2 = T("1. Your ads are dying", 84), T("faster than you think.", 84)
    def adc(d, s):
        d.ellipse((24 * s, 22 * s, 70 * s, 68 * s), fill=GOLD); d.rounded_rectangle((86 * s, 30 * s, 260 * s, 46 * s), 8 * s, fill=(210, 212, 218))
        d.rounded_rectangle((86 * s, 54 * s, 200 * s, 64 * s), 5 * s, fill=(228, 230, 234)); d.text((86 * s, 74 * s), "Sponsored", font=A.font("m", 20 * s), fill=MUTED)
        d.rectangle((0, 110 * s, 520 * s, 470 * s), fill=(238, 232, 222)); B.product(d, 260 * s, 300 * s, 0.95 * s)
        d.rounded_rectangle((24 * s, 490 * s, 496 * s, 560 * s), 18 * s, fill=NAVY); ctext(d, 260 * s, 525 * s, "Shop now", A.font("bl", 34 * s), WHITE)
    AD = card(520, 580, adc, r=28); AD_G = Image.fromarray(np.asarray(AD.convert("LA").convert("RGBA")))
    wk = [A.pill(f"Week {i + 1}", 30, DIM, (180, 186, 200), w="bl") for i in range(4)]; wk_on = [A.pill(f"Week {i + 1}", 30, GOLD, NAVY, w="bl") for i in range(4)]
    nm = A.pill("Burnt out in weeks, not months", 34, WHITE, INK, w="bl"); algo = A.pill("“The algorithm's broken”", 40, WHITE, INK, w="bl")
    ex = T("example", 24, (170, 176, 190), "mono")
    def fn(t):
        im = view(1.0 + 0.5 * t, 1.15, 0.5, 0.5, blur=8, dark=0.62); tracker(im, 0, t)
        rise(im, h1, W / 2, 430, t, 0.1); rise(im, h2, W / 2, 535, t, 0.4); under(im, "faster than you think.", 84, W / 2, 535, "faster", (t - 0.9) / 0.4)
        health = 1 - 0.85 * eio((t - 1.2) / 6.5); k = spring((t - 0.5) / 0.6, f=1.4, d=6); y = 910 + 600 * (1 - k)
        if t > 0.5:
            ad = Image.blend(AD, AD_G, clamp((1 - health) * 1.1)) if health < 0.99 else AD; put(im, ad, W / 2 - 120, y, clamp((t - 0.5) / 0.15), 0.92)
            d = ImageDraw.Draw(im); bx0, bx1, by = W / 2 - 360, W / 2 + 120, y + 330
            d.text((bx0, by - 46), "AD STRENGTH", font=A.font("monob", 24), fill=(200, 206, 220))
            d.rounded_rectangle((bx0, by, bx1, by + 24), 12, fill=(40, 46, 60)); d.rounded_rectangle((bx0, by, bx0 + (bx1 - bx0) * health, by + 24), 12, fill=GOLD if health > 0.35 else (200, 120, 90))
        if t >= cost_at:  # cost per sale badge, top right of the ad
            c = int(round(18 + 16 * eio((t - cost_at) / 2.4)))
            def cb(d, s): d.text((26 * s, 18 * s), "COST PER SALE", font=A.font("monob", 22 * s), fill=MUTED); d.text((26 * s, 52 * s), f"€{c}", font=A.font("bl", 64 * s), fill=INK)
            put(im, card(270, 140, cb, r=26), W / 2 + 290, y - 170, clamp((t - cost_at) / 0.2), 0.9 + 0.1 * back((t - cost_at) / 0.4)); put(im, ex, W / 2 + 290, y - 70, clamp((t - cost_at) / 0.3))
        if weeks_at <= t < cost_at + 2.4 or t < algo_at - 0.2:
            for i in range(4):
                on = t >= weeks_at + i * 0.4
                if t >= weeks_at: put(im, wk_on[i] if on else wk[i], W / 2 - 330 + i * 220, 1420, eo((t - weeks_at) / 0.3) * (1 - clamp((t - algo_at + 0.4) / 0.25)))
            if t >= weeks_at + 1.4: pop(im, nm, W / 2, 1520, t, weeks_at + 1.4, 1.3) if t < algo_at - 0.4 else put(im, nm, W / 2, 1520, 1 - clamp((t - algo_at + 0.4) / 0.25))
        if t >= algo_at:
            pop(im, algo, W / 2, 1470, t, algo_at, 1.3); p = eo((t - algo_at - 0.5) / 0.3)
            if p > 0: ImageDraw.Draw(im).line((W / 2 - algo.width / 2 + 20, 1475, W / 2 - algo.width / 2 + 20 + (algo.width - 40) * p, 1465), fill=GOLD, width=10)
        return im, 0
    ev = [(0.0, "pop", 0.6), (0.1, "swish", 0.4), (0.4, "swish", 0.4), (0.9, "swish", 0.5), (0.5, "whoosh", 0.4)] + [(weeks_at + i * 0.4, "tick", 0.5) for i in range(4)] + \
         [(weeks_at + 1.4, "pop", 0.6), (cost_at, "pop", 0.6)] + [(cost_at + i * 0.15, "tick", 0.25) for i in range(16)] + [(algo_at, "pop", 0.6), (algo_at + 0.5, "swish", 0.7)]
    return dur, fn, ev


# ======================================================================= problem 2: tracking
def scene_tracking(dur=9.2, neq_at=1.9, dots_at=2.8, toggles_at=5.4):
    """'2. Ads Manager doesn't match your bank.' 38 sales vs 52 orders (example), a gold ≠ slams with a glitch; a row of
    orders with gaps and double counts; then the wrong ad switched off, the wrong one scaled"""
    h1, h2 = T("2. Ads Manager doesn't", 84), T("match your bank.", 84)
    def numcard(lab, n, sub):
        def dr(d, s): ctext(d, 200 * s, 60 * s, lab, A.font("monob", 26 * s), MUTED); ctext(d, 200 * s, 190 * s, n, A.font("bl", 150 * s), INK); ctext(d, 200 * s, 300 * s, sub, A.font("sb", 34 * s), MUTED)
        return card(400, 360, dr, r=32)
    L_, R_ = numcard("ADS MANAGER", "38", "sales"), numcard("YOUR STORE", "52", "orders"); neq = T("≠", 200, GOLD); ex = T("example numbers", 24, (170, 176, 190), "mono")
    miss = A.pill("Missed sales  ·  Counted twice", 32, WHITE, INK, w="bl")
    def row(lab, sub, on):
        def dr(d, s):
            d.text((34 * s, 26 * s), lab, font=A.font("bl", 40 * s), fill=INK); d.text((34 * s, 80 * s), sub, font=A.font("m", 28 * s), fill=MUTED)
        c = card(860, 140, dr, r=28); return c
    RA, RB = row("Ad A", "actually selling", True), row("Ad B", "not really selling", False)
    off_ = A.pill("Switched off", 34, DIM, WHITE, w="bl"); up_ = A.pill("Budget ↑  Scaled", 34, GOLD, NAVY, w="bl"); cap = T("Wrong one off. Wrong one up.", 76)
    def toggle(im, x, y, on):
        d = ImageDraw.Draw(im); d.rounded_rectangle((x - 50, y - 28, x + 50, y + 28), 28, fill=GOLD if on else (190, 194, 204)); cx = x + (22 if on else -22); d.ellipse((cx - 22, y - 22, cx + 22, y + 22), fill=WHITE)
    def fn(t):
        im = view(1.0 + 0.5 * t, 1.1, 0.5, 0.5, blur=6, dark=0.6); tracker(im, 1, t); sh = 0
        rise(im, h1, W / 2, 430, t, 0.1); rise(im, h2, W / 2, 535, t, 0.4); under(im, "match your bank.", 84, W / 2, 535, "your bank", (t - 0.9) / 0.4)
        out = eio((t - toggles_at + 0.3) / 0.3)
        if out < 1:
            g = (8 * math.sin(t * 60)) if neq_at <= t < neq_at + 0.4 else 0
            pop(im, L_, W / 2 - 250 + g - 900 * out, 860, t, 0.6, 1.2); pop(im, R_, W / 2 + 250 + 900 * out, 860, t, 0.9, 1.2)
            if t >= neq_at: put(im, neq, W / 2, 860, clamp((t - neq_at) / 0.12) * (1 - out), 1.6 - 0.6 * back((t - neq_at) / 0.3))
            if neq_at <= t < neq_at + 0.15: sh = 12
            if t >= 0.9: put(im, ex, W / 2, 1060, (1 - out) * clamp((t - 1.0) / 0.3))
            d = ImageDraw.Draw(im)
            for i in range(10):  # orders: gaps (missed) and a double count
                k = (t - dots_at - i * 0.1) / 0.25
                if k <= 0: continue
                x = W / 2 - 405 + i * 90; y = 1200; a = int(255 * clamp(k) * (1 - out))
                if i in (2, 6): d.ellipse((x - 26, y - 26, x + 26, y + 26), outline=(200, 206, 220, a), width=4); ctext(d, x, y, "?", A.font("bl", 30), (200, 206, 220, a))
                else:
                    d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=WHITE + (a,))
                    if i == 8: d.ellipse((x - 14, y - 40, x + 38, y + 12), fill=GOLD + (a,))
            if t >= dots_at + 1.1: put(im, miss, W / 2, 1310, clamp((t - dots_at - 1.1) / 0.2) * (1 - out))
        if t >= toggles_at:
            u = t - toggles_at; pop(im, RA, W / 2, 880, t, toggles_at, 1.2); pop(im, RB, W / 2, 1060, t, toggles_at + 0.2, 1.2)
            toggle(im, W / 2 + 330, 880, t < toggles_at + 0.75); finger(im, W / 2 + 330, 880, t, toggles_at + 0.7)
            if u > 0.8: pop(im, off_, W / 2 + 130, 880, t, toggles_at + 0.8, 1.3)
            if u > 1.5: pop(im, up_, W / 2 + 230, 1060, t, toggles_at + 1.5, 1.3)
            rise(im, cap, W / 2, 1260, t, toggles_at + 2.0); under(im, "Wrong one off. Wrong one up.", 76, W / 2, 1260, "Wrong one", (t - toggles_at - 2.4) / 0.4)
        return im, sh
    ev = [(0.0, "pop", 0.6), (0.1, "swish", 0.4), (0.4, "swish", 0.4), (0.6, "pop", 0.6), (0.9, "pop", 0.6), (neq_at, "glitch", 0.7), (neq_at + 0.05, "hit", 0.9)] + \
         [(dots_at + i * 0.1, "tick", 0.3) for i in range(10)] + [(dots_at + 1.1, "pop", 0.5), (toggles_at, "whoosh", 0.5), (toggles_at + 0.7, "click", 0.9), (toggles_at + 0.8, "pop", 0.5), (toggles_at + 1.5, "pop", 0.6), (toggles_at + 2.0, "swish", 0.5)]
    return dur, fn, ev


# ======================================================================= problem 3: paying for sales you'd get anyway
def scene_expensive(dur=11.0, roas_at=0.9, pie_at=5.2, crack_at=7.4):
    """'3. The expensive one.' a glowing 5.1x ROAS badge ('your best campaign'); it shrinks up and a donut fills:
    mostly people who were already your customers (example); the badge cracks: paying for sales you'd get for free"""
    h1 = T("3. The expensive one.", 92); sub = T("Your best campaign…", 70, (210, 216, 230))
    def rb(d, s): ctext(d, 280 * s, 60 * s, "ROAS", A.font("monob", 30 * s), MUTED); ctext(d, 280 * s, 175 * s, "5.1x", A.font("bl", 150 * s), NAVY)
    BADGE = card(560, 280, rb, r=36)
    chips = [A.pill("Your customers", 34, WHITE, INK, w="bl"), A.pill("Your email list", 34, WHITE, INK, w="bl")]
    lab1, lab2 = A.pill("Already your customers", 30, GOLD, NAVY, w="bl"), A.pill("New", 30, WHITE, INK, w="bl"); ex = T("example", 24, (170, 176, 190), "mono")
    c1, c2 = T("Paying for sales", 84), T("you'd get for free.", 84)
    def fn(t):
        im = view(1.5 + 0.6 * t, 1.12, 0.5, 0.5, blur=6, dark=0.6); tracker(im, 2, t); sh = 0
        rise(im, h1, W / 2, 440, t, 0.1); under(im, "3. The expensive one.", 92, W / 2, 440, "expensive", (t - 0.6) / 0.4)
        up = eio((t - pie_at) / 0.5); by, bs = 900 - 230 * up, 1 - 0.35 * up
        if t >= roas_at:
            put(im, BADGE, W / 2, by, clamp((t - roas_at) / 0.15) * (1 - 0.55 * clamp((t - crack_at) / 0.3)), bs * (0.8 + 0.2 * back((t - roas_at) / 0.4)))
            for j in range(3): ring(im, W / 2, by, ((t - roas_at - 0.2) - j * 0.5) / 1.5 if t < pie_at else 0, col=GOLD, maxr=420, width=5, r0=200)
            if t < pie_at: rise(im, sub, W / 2, 1150, t, roas_at + 0.9)
            if t >= crack_at:  # crack across the badge
                p = eo((t - crack_at) / 0.25); d = ImageDraw.Draw(im); pts = [(W / 2 - 180 * bs, by - 60 * bs), (W / 2 - 60 * bs, by + 10 * bs), (W / 2 + 10 * bs, by - 40 * bs), (W / 2 + 90 * bs, by + 50 * bs), (W / 2 + 180 * bs, by + 20 * bs)]
                n = 1 + int(4 * p); d.line(pts[:n + 1] if n < 5 else pts, fill=GOLD, width=8)
                if crack_at <= t < crack_at + 0.15: sh = 10
        if t >= pie_at:  # donut: mostly people who were already customers
            p = eio((t - pie_at - 0.2) / 1.0); cx, cy, r = W / 2, 1110, 190; d = ImageDraw.Draw(im)
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 48, 66)); d.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * 0.78 * p, fill=GOLD)
            if p > 0.75: d.pieslice((cx - r, cy - r, cx + r, cy + r), -90 + 360 * 0.78, -90 + 360 * 0.78 + 360 * 0.22 * clamp((p - 0.75) / 0.25), fill=WHITE)
            d.ellipse((cx - 100, cy - 100, cx + 100, cy + 100), fill=(18, 24, 38))
            pop(im, lab1, cx - 250, cy + 240, t, pie_at + 0.8, 1.3); pop(im, lab2, cx + 290, cy - 150, t, pie_at + 1.1, 1.3); put(im, ex, cx, cy, clamp((t - pie_at - 1.2) / 0.3))
            for i, c in enumerate(chips): pop(im, c, W / 2 + (-300 if i == 0 else 300), (960 if i == 0 else 1250), t, pie_at + 0.3 + i * 0.6, 1.3) if t < crack_at else None
        if t >= crack_at:
            rise(im, c1, W / 2, 1440, t, crack_at + 0.2); rise(im, c2, W / 2, 1545, t, crack_at + 0.5)
            under(im, "you'd get for free.", 84, W / 2, 1545, "for free", (t - crack_at - 0.9) / 0.4); coins(im, W / 2, 620, t, crack_at + 0.3, n=10, spread=200)
        return im, sh
    ev = [(0.0, "pop", 0.6), (0.1, "swish", 0.4), (0.6, "swish", 0.5), (roas_at, "pop", 0.8), (roas_at + 0.2, "shimmer", 0.6), (roas_at + 0.9, "swish", 0.4),
          (pie_at, "whoosh", 0.5), (pie_at + 0.3, "pop", 0.5), (pie_at + 0.9, "pop", 0.5), (crack_at, "glitch", 0.7), (crack_at + 0.05, "hit", 0.9), (crack_at + 0.3, "coin", 0.6), (crack_at + 0.9, "swish", 0.5)]
    return dur, fn, ev


# ======================================================================= the fix
def scene_fix(dur=9.4, steps_at=(0.2, 3.4, 6.2)):
    """three step cards drop in on their words, each with a little live visual: fresh ads flipping week by week,
    52 = 52 tracking check, new customers flowing in"""
    hd = T("What we do differently:", 74, (210, 216, 230))
    steps = [("Fresh ads every week", "built from what's actually selling"), ("Tracking you can trust", "checked against your real store numbers"), ("New customers", "not just re-selling to the old ones")]
    def sc(i, a, b):
        def dr(d, s):
            d.ellipse((30 * s, 40 * s, 110 * s, 120 * s), fill=GOLD); ctext(d, 70 * s, 80 * s, f"0{i + 1}", A.font("bl", 34 * s), NAVY)
            d.text((136 * s, 40 * s), a, font=A.font("bl", 40 * s), fill=INK); d.text((136 * s, 94 * s), b, font=A.font("m", 27 * s), fill=MUTED)
        return card(900, 170, dr, r=30)
    C = [sc(i, a, b) for i, (a, b) in enumerate(steps)]; Y = [700, 930, 1160]
    def fn(t):
        im = view(3.0 + 0.6 * t, 1.1, 0.5, 0.45, blur=5, dark=0.58); rise(im, hd, W / 2, 470, t, 0.05)
        for i, (c, y, t0) in enumerate(zip(C, Y, steps_at)):
            k = (t - t0) / 0.5
            if k <= 0: continue
            put(im, c, W / 2 + 900 * (1 - eo(k)), y, 1, 1, 0); d = ImageDraw.Draw(im); x = W / 2 + 330
            if i == 0:  # little ad cards flipping, one per week
                n = int((t - t0) * 2.5) % 3
                for j in range(3): d.rounded_rectangle((x - 70 + j * 46, y - 60 + (0 if j == n else 10), x - 34 + j * 46, y + (0 if j == n else 10)), 6, fill=GOLD if j == n else (210, 212, 218))
            elif i == 1 and t > t0 + 0.6:
                ctext(d, x - 10, y - 30, "52 = 52", A.font("bl", 34), NAVY); A.check(d, 1, x + 70, y - 52, GOLD)
            elif i == 2:
                for j in range(5):
                    p = ((t - t0) * 0.8 + j / 5) % 1; d.ellipse((x - 100 + 170 * p - 9, y - 30 - 9, x - 100 + 170 * p + 9, y - 30 + 9), fill=GOLD)
                d.rounded_rectangle((x + 70, y - 60, x + 110, y), 8, outline=NAVY, width=4)
        return im, 0
    return dur, fn, [(0.05, "swish", 0.4)] + [(x, "whoosh", 0.5) for x in steps_at] + [(x + 0.4, "hit", 0.6) for x in steps_at]


# ======================================================================= call to action
def scene_cta(dur=7.2, ask_at=0.2, comment_at=3.6, cps=6):
    """'Spending on ads and working harder for the same sales?' then 'Comment leads': the box types it, Post is tapped,
    'I'll show you where your account's leaking'"""
    q1, q2 = T("Spending on ads,", 84), T("working harder for the same sales?", 70)
    cw = T("Comment", 92); kp = A.pill("leads", 64, GOLD, NAVY, w="bl"); tip = A.pill("I'll show you where it's leaking", 40, WHITE, INK, w="bl")
    kw = "leads"; ty0 = comment_at + 0.7; post_at = ty0 + len(kw) / cps + 0.3
    def fn(t):
        im = view(4.0 + 0.6 * t, 1.1, 0.5, 0.6, blur=6, dark=0.58)
        rise(im, q1, W / 2, 460, t, ask_at); rise(im, q2, W / 2, 565, t, ask_at + 0.5); under(im, "working harder for the same sales?", 70, W / 2, 565, "the same sales", (t - ask_at - 1.2) / 0.4)
        if t >= comment_at:
            k = (t - comment_at) / 0.35; tot = cw.width + kp.width - 40
            put(im, cw, W / 2 - tot / 2 + cw.width / 2, 820, clamp(k / 0.2)); put(im, kp, W / 2 - tot / 2 + cw.width - 40 + kp.width / 2, 820, clamp(k / 0.2), 0.6 + 0.4 * back(k))
            n = int(clamp((t - ty0) * cps, 0, len(kw))); posted = t >= post_at + 0.1
            put(im, A.comment_box("" if posted else kw[:n], (not posted) and int(t * 3) % 2 == 0), W / 2, 1040, clamp((t - comment_at - 0.3) / 0.3))
            finger(im, 915, 1040, t, post_at)
            if t >= post_at + 0.2: pop(im, tip, W / 2, 1230, t, post_at + 0.2, 1.3)
        return im, 0
    return dur, fn, [(ask_at, "swish", 0.4), (ask_at + 0.5, "swish", 0.4), (comment_at, "pop", 0.7)] + [(ty0 + i / cps, "tick", 0.5) for i in range(len(kw))] + [(post_at, "click", 0.9), (post_at + 0.2, "ping", 0.7)]
