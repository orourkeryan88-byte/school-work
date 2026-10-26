"""E-COMMERCE v2 'Three leaks' scenes: sells the two things Southline does, Meta ads + email marketing.
The store is a shopping bag leaking € coins from three holes; each problem is one leak, and the solution plugs them
(ads to get customers, email to keep them). New animation set (none reused from the earlier e-com cut): per-letter
bounce, leaking bag, flatlining heartbeat monitor, flip-digit counter, carts rolling away, taxi meter, boomerang
envelopes, patch-the-holes, letters dropping into a comment bubble. Navy + gold. fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, put_rise, text, eo, eio, back, spring, clamp, ring, sprite, shadowed
import trust_scenes as S
from trust_scenes import view, vignette, T, under, pop, rise, ctext, card

GOLD = (226, 178, 92); NAVY = (14, 26, 48); WHITE = (255, 255, 255); INK = (16, 18, 24); MUTED = (120, 126, 138); DIM = (52, 60, 80)
S.ACC = GOLD


# ======================================================================= shared pieces
_coin = {}
def coin(r=20):
    if r not in _coin:
        def dr(d, s, im_):
            d.ellipse((0, 0, 2 * r * s - 1, 2 * r * s - 1), fill=GOLD); d.ellipse((4 * s, 4 * s, (2 * r - 4) * s, (2 * r - 4) * s), outline=(250, 214, 140), width=2 * s)
            f = A.font("bl", int(r * 1.3) * s); tw, th, ox, oy = A.tsize("€", f); d.text((r * s - tw / 2 - ox, r * s - th / 2 - oy), "€", font=f, fill=NAVY)
        _coin[r] = sprite(2 * r, 2 * r, dr)
    return _coin[r]

HOLES = [(-90, 70), (0, 120), (90, 70)]  # leak positions on the bag front (from bag centre)

def bag(im, cx, cy, s=1.0, t=0.0, open_=(1, 1, 1), plugged=(0, 0, 0), fill=0.25, pour=True, leak_from=0.0):
    """the store as a shopping bag: coins pour in the top; open holes leak coins; plugged holes show a gold patch.
    fill = 0..1 how full it looks"""
    d = ImageDraw.Draw(im); w, h = 360 * s, 380 * s; x0, y0 = cx - w / 2, cy - h / 2
    for hx in (-70, 70): d.arc((cx + hx * s - 50 * s, y0 - 90 * s, cx + hx * s + 50 * s, y0 + 20 * s), 180, 360, fill=GOLD, width=int(12 * s))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 30 * s, fill=(20, 32, 58), outline=GOLD, width=int(8 * s))
    lvl = y0 + h - (h - 30 * s) * clamp(fill)  # coin level inside (a lighter band)
    d.rounded_rectangle((x0 + 10 * s, lvl, x0 + w - 10 * s, y0 + h - 10 * s), 22 * s, fill=(60, 52, 40))
    ctext(d, cx, y0 + 80 * s, "YOUR STORE", A.font("monob", int(30 * s)), GOLD)
    for i, (hx, hy) in enumerate(HOLES):
        x, y = cx + hx * s, cy + hy * s
        if plugged[i] > 0:
            r = 34 * s * (0.6 + 0.4 * back(plugged[i])); d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD)
            if plugged[i] > 0.6: d.line([(x - 13 * s, y), (x - 3 * s, y + 10 * s), (x + 15 * s, y - 10 * s)], fill=NAVY, width=int(7 * s), joint="curve")
        else:
            d.ellipse((x - 24 * s, y - 24 * s, x + 24 * s, y + 24 * s), fill=(6, 10, 18), outline=(90, 100, 124), width=int(3 * s))
            ctext(d, x, y, str(i + 1), A.font("bl", int(24 * s)), (150, 160, 184))
    c = coin(int(18 * s))
    if pour:  # coins dropping into the bag
        for j in range(6):
            p = ((t * 1.3) + j / 6) % 1; put(im, c, cx + 40 * s * math.sin(j * 2.1), y0 - 420 * s + 400 * s * p * p, clamp((1 - p) * 4) * clamp(p * 6), 1, p * 300)
    for i, (hx, hy) in enumerate(HOLES):  # leaks
        if open_[i] and plugged[i] == 0 and t >= leak_from:
            for j in range(4):
                p = ((t - leak_from) * 1.1 + j / 4 + i * 0.13) % 1
                put(im, c, cx + hx * s + (hx * 0.5 * s) * p, cy + hy * s + 30 * s + 520 * s * p * p, 1 - p, 0.9, p * 200)


_trk = {}
def leaks(im, now, t, plugged=()):
    """top tracker: LEAK 1 2 3 as drops; the current one gold and dripping, plugged ones white with a tick"""
    d = ImageDraw.Draw(im); a = eo(t / 0.25); x0 = W / 2 - 170
    ctext(d, x0 - 30, 300, "LEAK", A.font("monob", 30), (200, 206, 220, int(255 * a)))
    for i in range(3):
        x = x0 + 70 + i * 100; y = 300; col = WHITE if i in plugged else (GOLD if i == now else DIM)
        sc = 1 + (0.2 * (1 - eo(t / 0.4)) if i == now else 0); r = 26 * sc
        d.ellipse((x - r, y - r * 0.8, x + r, y + r * 1.2), fill=col); d.polygon([(x - r * 0.8, y - r * 0.2), (x + r * 0.8, y - r * 0.2), (x, y - r * 1.6)], fill=col)
        ctext(d, x, y + 4, "✓" if i in plugged else str(i + 1), A.font("bl", int(26 * sc)), NAVY if col != DIM else (150, 160, 184))
        if i == now and i not in plugged:
            p = (t * 1.2) % 1; d.ellipse((x - 7, y + 40 + 50 * p * p - 9, x + 7, y + 40 + 50 * p * p + 9), fill=GOLD + (int(255 * (1 - p)),))


def letters_bounce(im, s, size, cx, cy, t, t0=0.0, col=WHITE, stagger=0.05, frame0=True):
    """word with a per-letter bounce: readable from the first frame, each letter hops in sequence"""
    f = A.font("bl", size); x = cx - f.getlength(s) / 2
    for i, ch in enumerate(s):
        wch = f.getlength(ch)
        if ch != " ":
            k = (t - t0 - i * stagger) / 0.35; hop = -40 * math.sin(math.pi * clamp(k)) if k < 1 else 0
            if frame0 or k > 0: put(im, T(ch, size, col), x + wch / 2, cy + hop, 1 if frame0 else clamp(k * 3), 1 + 0.15 * math.sin(math.pi * clamp(k)))
        x += wch


# ======================================================================= hook: your store has 3 leaks
def scene_hook(dur=6.0, bag_at=1.3, pay_at=3.3):
    """frame 0: 'E-commerce brands,' with a per-letter bounce; it lifts away and the store-bag drops in, coins pouring
    in the top and leaking out of three holes: 'Your store has 3 leaks.' '…and you're paying for all of them.'"""
    c1 = T("Your store has 3 leaks.", 90); c2, c3 = T("And you're probably", 72), T("paying for all of them.", 72)
    def fn(t):
        im = vignette(view(t * 0.8, 1.0 + 0.4 * (1 - eo(t / 0.9)), 0.5, 0.5, dark=0.35 + 0.25 * clamp((t - bag_at) / 0.4)))
        sh = 14 if t < 0.14 else 0; o = eio((t - bag_at + 0.15) / 0.35)
        if o < 1:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            letters_bounce(lay, "E-commerce", 150, W / 2, 600, t); letters_bounce(lay, "brands,", 150, W / 2, 780, t, 0.3, GOLD)
            if o > 0: lay.putalpha(lay.split()[3].point(lambda v: int(v * (1 - o))))
            im.alpha_composite(lay, (0, int(-500 * o * o)))
        if t >= bag_at:
            k = spring((t - bag_at) / 0.7, f=1.4, d=6); bag(im, W / 2, 1000 + 700 * (1 - k), 1.05, t, fill=0.25, leak_from=bag_at + 0.5)
            if bag_at + 0.4 <= t < bag_at + 0.55: sh = 9
        rise(im, c1, W / 2, 440, t, bag_at + 0.1); under(im, "Your store has 3 leaks.", 90, W / 2, 440, "3 leaks", (t - bag_at - 0.6) / 0.4)
        rise(im, c2, W / 2, 1480, t, pay_at); rise(im, c3, W / 2, 1575, t, pay_at + 0.4); under(im, "paying for all of them.", 72, W / 2, 1575, "paying", (t - pay_at - 0.9) / 0.4)
        return im, sh
    ev = [(0.0, "hit", 1.0)] + [(i * 0.05, "tick", 0.3) for i in range(0, 17, 2)] + [(bag_at - 0.15, "whoosh", 0.5), (bag_at + 0.45, "hit", 0.8), (bag_at + 0.5, "coin", 0.5),
          (bag_at + 1.2, "coin", 0.4), (pay_at, "swish", 0.4), (pay_at + 0.4, "swish", 0.4), (pay_at + 0.9, "coin", 0.5)]
    return dur, fn, ev


# ======================================================================= who / what
def scene_ryan(dur=4.5, chips_at=(1.2, 1.6), sub_at=2.4):
    """'I'm Ryan, I run Southline.' the two services flip in like cards: Meta ads, Email marketing; 'for online brands'
    types out; the logo stamps in"""
    s1 = T("I'm Ryan.", 130); sub = "for online brands."
    def chip(lab):
        def dr(d, s): ctext(d, 200 * s, 60 * s, lab, A.font("bl", 46 * s), NAVY)
        return card(400, 120, dr, fill=GOLD, r=60)
    C = [chip("Meta ads"), chip("Email marketing")]; lg = A.logo().resize((150, 150))
    def fn(t):
        im = vignette(view(2.0 + 0.7 * t, 1.12, 0.5, 0.45, dark=0.5)); sh = 0
        pop(im, s1, W / 2, 560, t, 0.1, 1.4)
        for i, (c, t0) in enumerate(zip(C, chips_at)):  # card flip: x-scale through 0
            k = clamp((t - t0) / 0.45)
            if k <= 0: continue
            sx = abs(math.cos((1 - eo(k)) * math.pi)); sp = c.resize((max(1, int(c.width * sx)), c.height)) if sx < 0.99 else c
            put(im, sp, W / 2 + (-215 if i == 0 else 215), 760, clamp(k * 4))
        n = int(clamp((t - sub_at) * 18, 0, len(sub)))
        if n: put(im, T(sub[:n], 66, (210, 216, 230)), W / 2, 920)
        k = (t - sub_at - 1.0) / 0.3
        if k > 0: put(im, lg, W / 2, 1200, clamp(k / 0.2), 1.6 - 0.6 * eo(k)); sh = 8 if k < 0.5 else 0
        return im, sh
    return dur, fn, [(0.1, "hit", 0.7)] + [(x, "swish", 0.6) for x in chips_at] + [(sub_at + i / 18, "tick", 0.2) for i in range(0, len(sub), 2)] + [(sub_at + 1.0, "hit", 0.8)]


# ======================================================================= leak 1: ads burn out
def scene_burnout(dur=8.0, flat_at=3.6, meter_at=4.2, test_at=5.6):
    """heartbeat monitor of your ad: beats shrink week by week and flatline (beep); a flip-digit 'cost per sale'
    counter climbs (example); 'if nobody's testing new ones'"""
    h1, h2 = T("Leak 1:", 70, GOLD), T("your ads burn out.", 92)
    MX0, MY0, MX1, MY1 = 90, 640, 990, 1080
    pill = A.pill("…and nobody's testing new ones", 40, WHITE, INK, w="bl"); ex = T("example", 24, (170, 176, 190), "mono")
    def digit(ch, sq=1.0):
        sp = T(ch, 110, NAVY); return sp if sq > 0.98 else sp.resize((sp.width, max(1, int(sp.height * sq))))
    def fn(t):
        im = view(1.0 + 0.5 * t, 1.12, 0.5, 0.5, blur=8, dark=0.62); leaks(im, 0, t)
        rise(im, h1, W / 2, 410, t, 0.05); rise(im, h2, W / 2, 500, t, 0.3); under(im, "your ads burn out.", 92, W / 2, 500, "burn out", (t - 0.8) / 0.4)
        k = eo((t - 0.4) / 0.4); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        d.rounded_rectangle((MX0, MY0 + 60 * (1 - k), MX1, MY1 + 60 * (1 - k)), 30, fill=(8, 14, 24, int(235 * k)), outline=GOLD + (int(255 * k),), width=3)
        for gx in range(MX0 + 30, MX1, 60): d.line((gx, MY0 + 60, gx, MY1 - 30), fill=(30, 44, 64, int(255 * k)), width=1)
        d.text((MX0 + 30, MY0 + 22), "AD PERFORMANCE", font=A.font("monob", 26), fill=(150, 160, 184, int(255 * k)))
        for i in range(4): ctext(d, MX0 + 150 + i * 210, MY1 - 22, f"W{i + 1}", A.font("monob", 24), (150, 160, 184, int(255 * k)))
        im.alpha_composite(o); d = ImageDraw.Draw(im)
        if k > 0.5:  # ECG trace: drawn left to right, beats shrink, then flat
            head = clamp((t - 0.6) / 3.0); n = int(300 * head); pts = []; base = (MY0 + MY1) / 2 + 20
            for j in range(n):
                x = MX0 + 30 + (MX1 - MX0 - 60) * j / 300; ph = (j % 50) / 50; amp = 170 * max(0, 1 - j / 260)
                y = base - (amp if 0.42 < ph < 0.46 else (-amp * 0.4 if 0.46 <= ph < 0.5 else 0))
                pts.append((x, y))
            if len(pts) > 1:
                gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(pts, fill=GOLD + (255,), width=14); im.alpha_composite(gl.filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(8)))
                d = ImageDraw.Draw(im); d.line(pts, fill=(255, 230, 170), width=5); d.ellipse((pts[-1][0] - 9, pts[-1][1] - 9, pts[-1][0] + 9, pts[-1][1] + 9), fill=WHITE)
            if t >= flat_at: ctext(d, (MX0 + MX1) / 2, MY0 + 120, "FLATLINE", A.font("monob", 34), GOLD if int(t * 4) % 2 == 0 else (120, 100, 70))
        if t >= meter_at:  # flip-digit cost per sale
            v = int(round(18 + 16 * eio((t - meter_at) / 2.2))); s_ = f"{v}"; prev = f"{max(18, v - 1)}"
            def cb(d_, sc): d_.text((26 * sc, 18 * sc), "COST PER SALE", font=A.font("monob", 24 * sc), fill=MUTED)
            cc = card(420, 210, cb, r=28); kk = eo((t - meter_at) / 0.3); put(im, cc, W / 2, 1240, kk)
            put(im, T("€", 90, NAVY), W / 2 - 120, 1270, kk); flip = ((t - meter_at) * 7.3) % 1
            for i, ch in enumerate(s_):
                sq = abs(math.cos(math.pi * min(1, flip * 4))) if ch != prev[i] and t < meter_at + 2.2 else 1
                put(im, digit(ch, sq), W / 2 - 20 + i * 80, 1272, kk)
            put(im, ex, W / 2 + 150, 1180, kk)
        if t >= test_at: pop(im, pill, W / 2, 1460, t, test_at, 1.3)
        return im, 0
    ev = [(0.05, "swish", 0.4), (0.3, "swish", 0.4), (0.8, "swish", 0.5)] + [(0.6 + 3.0 * j / 6, "ping", 0.35 * (1 - j / 6)) for j in range(6)] + \
         [(flat_at, "glitch", 0.5), (meter_at, "pop", 0.6)] + [(meter_at + i * 0.137, "tick", 0.3) for i in range(16)] + [(test_at, "pop", 0.7)]
    return dur, fn, ev


# ======================================================================= leak 2: abandoned carts
def scene_carts(dur=7.6, carts_at=(0.9, 1.4, 1.9), leave_at=3.0, inbox_at=4.6, gone_at=6.2):
    """three full carts roll in, sit, then roll off one by one ('left'); an inbox slides up: 'Emails sent to them: 0';
    'GONE.' stamps down"""
    h1, h2 = T("Leak 2:", 70, GOLD), T("abandoned carts.", 92)
    def cart(d, x, y, s=1.0, items=((226, 178, 92), (240, 240, 240), (120, 170, 230))):
        d.line((x - 120 * s, y - 120 * s, x - 90 * s, y - 120 * s, x - 60 * s, y + 20 * s, x + 100 * s, y + 20 * s), fill=WHITE, width=int(10 * s), joint="curve")
        d.polygon([(x - 80 * s, y - 90 * s), (x + 130 * s, y - 90 * s), (x + 105 * s, y), (x - 62 * s, y)], fill=(30, 40, 62), outline=WHITE)
        for j, c in enumerate(items): d.rounded_rectangle((x - 60 * s + j * 58 * s, y - 140 * s + (j % 2) * 20 * s, x - 12 * s + j * 58 * s, y - 88 * s), 8 * s, fill=c)
        for wx in (-40, 80): d.ellipse((x + (wx - 16) * s, y + 30 * s, x + (wx + 16) * s, y + 62 * s), fill=WHITE)
    left = A.pill("left", 30, DIM, WHITE, w="bl")
    def ib(d, s):
        d.text((34 * s, 26 * s), "EMAILS SENT TO THEM", font=A.font("monob", 26 * s), fill=MUTED); d.text((34 * s, 70 * s), "0", font=A.font("bl", 120 * s), fill=INK)
        d.text((150 * s, 120 * s), "no reminder · no offer · nothing", font=A.font("m", 28 * s), fill=MUTED)
    INBOX = card(700, 230, ib, r=30); gone = T("GONE.", 150, GOLD)
    def fn(t):
        im = view(1.5 + 0.5 * t, 1.12, 0.5, 0.5, blur=6, dark=0.62); leaks(im, 1, t, plugged=()); sh = 0
        rise(im, h1, W / 2, 410, t, 0.05); rise(im, h2, W / 2, 500, t, 0.3); under(im, "abandoned carts.", 92, W / 2, 500, "abandoned", (t - 0.8) / 0.4)
        up = eio((t - inbox_at) / 0.4); d = ImageDraw.Draw(im)
        for i, t0 in enumerate(carts_at):
            k = eo((t - t0) / 0.5)
            if k <= 0: continue
            tl = leave_at + i * 0.45; out = eio((t - tl) / 0.7); x = -300 + (W / 2 + (i - 1) * 300 + 300) * k + 900 * out
            y = 820 + i * 0 - 140 * up; bob = 4 * math.sin(t * 20 + i) if (k < 1 or out > 0) else 0
            o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cart(ImageDraw.Draw(o), x, y + bob, 0.8)
            if out > 0: o.putalpha(o.split()[3].point(lambda v: int(v * (1 - out))))
            im.alpha_composite(o)
            if t >= tl: put(im, left, x, y + 110, clamp((t - tl) / 0.2) * (1 - out))
        if t >= inbox_at: put(im, INBOX, W / 2, 1180 + 300 * (1 - up), up)
        if t >= gone_at:
            k = (t - gone_at) / 0.3; put(im, gone, W / 2, 1460, clamp(k / 0.15), 1.8 - 0.8 * eo(k), -6)
            if gone_at <= t < gone_at + 0.15: sh = 12
        return im, sh
    ev = [(0.05, "swish", 0.4), (0.3, "swish", 0.4), (0.8, "swish", 0.5)] + [(x, "whoosh", 0.4) for x in carts_at] + [(leave_at + i * 0.45, "swish", 0.5) for i in range(3)] + \
         [(inbox_at, "whoosh", 0.5), (inbox_at + 0.3, "pop", 0.6), (gone_at, "hit", 1.0)]
    return dur, fn, ev


# ======================================================================= leak 3: paying Meta to reach your own customers
def scene_meter(dur=8.6, faces_at=1.2, meter_at=2.4, email_at=5.4, free_at=6.4):
    """a crowd of 'already bought from you' customers; a taxi meter 'You pay Meta' runs up while targeting them; an
    envelope 'Email: €0' slams in beside it and the meter freezes: 'for free'"""
    h1, h2 = T("Leak 3: the expensive one.", 74, GOLD), T("Paying Meta to reach", 84)
    h3 = T("people who already bought.", 84)
    rng = np.random.default_rng(3); faces = [(W / 2 + (c - 3) * 120 + rng.uniform(-10, 10), 760 + r * 120 + rng.uniform(-8, 8)) for r in range(2) for c in range(7)]
    tag = A.pill("Already bought from you", 32, GOLD, NAVY, w="bl"); ex = T("example", 24, (170, 176, 190), "mono")
    def env_(d, s):
        d.rectangle((40 * s, 40 * s, 260 * s, 180 * s), fill=WHITE); d.line((40 * s, 40 * s, 150 * s, 120 * s, 260 * s, 40 * s), fill=GOLD, width=8 * s, joint="curve")
    ENV = sprite(300, 220, lambda d, s, im_: env_(d, s)); free = T("Email: €0", 70, WHITE)
    def fn(t):
        im = view(2.0 + 0.5 * t, 1.12, 0.5, 0.45, blur=6, dark=0.62); leaks(im, 2, t); sh = 0
        rise(im, h1, W / 2, 410, t, 0.05); rise(im, h2, W / 2, 510, t, 0.4); rise(im, h3, W / 2, 610, t, 0.8)
        d = ImageDraw.Draw(im)
        for i, (x, y) in enumerate(faces):  # customers: head + shoulders, heart badge
            k = eo((t - faces_at - i * 0.04) / 0.3)
            if k <= 0: continue
            a = int(255 * k); d.ellipse((x - 24, y - 50, x + 24, y - 2), fill=(200, 206, 220, a)); d.pieslice((x - 44, y - 4, x + 44, y + 80), 180, 360, fill=(200, 206, 220, a))
            d.ellipse((x + 14, y - 56, x + 36, y - 34), fill=GOLD + (a,))
        if t >= faces_at + 0.6: put(im, tag, W / 2, 1010, clamp((t - faces_at - 0.6) / 0.2))
        if t >= meter_at:  # taxi meter
            frozen = t >= email_at + 0.3; tt = min(t, email_at + 0.3); v = (tt - meter_at) * 37.3
            def mb(d_, sc):
                d_.text((30 * sc, 22 * sc), "YOU PAY META", font=A.font("monob", 26 * sc), fill=(150, 160, 184))
                d_.rounded_rectangle((26 * sc, 64 * sc, 394 * sc, 170 * sc), 14 * sc, fill=(4, 8, 14))
                ctext(d_, 210 * sc, 117 * sc, f"€{v:,.2f}", A.font("monob", 64 * sc), GOLD if not frozen or int(t * 3) % 2 else (150, 120, 70))
            put(im, card(420, 200, mb, fill=(22, 30, 46), r=28), W / 2 - (190 if t >= email_at else 0), 1250, eo((t - meter_at) / 0.3)); put(im, ex, W / 2 - (190 if t >= email_at else 0), 1380, clamp((t - meter_at) / 0.3))
        if t >= email_at:
            k = (t - email_at) / 0.35; put(im, ENV, W / 2 + 250, 1230 - 500 * (1 - eo(k)), clamp(k / 0.15), 0.9, 25 * (1 - eo(k)))
            if email_at + 0.3 <= t < email_at + 0.45: sh = 10
            rise(im, free, W / 2 + 250, 1400, t, email_at + 0.4)
        if t >= free_at:
            pf = T("…for free.", 90, GOLD); pop(im, pf, W / 2, 1530, t, free_at, 1.4)
        return im, sh
    ev = [(0.05, "swish", 0.4), (0.4, "swish", 0.4), (0.8, "swish", 0.4), (faces_at, "pop", 0.5), (meter_at, "click", 0.7)] + [(meter_at + i * 0.25, "tick", 0.3) for i in range(12)] + \
         [(email_at, "whoosh", 0.6), (email_at + 0.3, "hit", 0.9), (free_at, "ping", 0.7)]
    return dur, fn, ev


# ======================================================================= the fix: ads to get them, email to keep them
def scene_fix(dur=12.8, split_at=0.9, keep_at=8.0, plug_at=(9.4, 9.9, 10.4)):
    """'Here's how we fix it.' split screen: META ADS - new customers stream into the store; EMAIL - envelopes
    boomerang out to customers and come back with coins (carts recovered, second orders). 'Ads to get them. Email to
    keep them.' Then the bag returns and its three holes get patched, the coin level rising"""
    hd = T("Here's how we fix it.", 84); l1, l2 = A.pill("META ADS", 40, GOLD, NAVY, w="bl"), A.pill("EMAIL", 40, WHITE, INK, w="bl")
    s1, s2 = T("find new customers", 46, (210, 216, 230), "b"), T("carts · second orders", 46, (210, 216, 230), "b")
    k1, k2 = T("Ads to get them.", 92), T("Email to keep them.", 92, GOLD)
    def fn(t):
        im = view(1.0 + 0.5 * t, 1.12, 0.5, 0.5, blur=6, dark=0.62); sh = 0
        out = eio((t - keep_at + 0.3) / 0.3); dx = 1100 * out
        rise(im, hd, W / 2, 420, t, 0.05) if out < 1 else None
        if out < 1:
            d = ImageDraw.Draw(im); k = eo((t - split_at) / 0.4)
            for side, (lab, sub, cx) in enumerate(((l1, s1, W / 4), (l2, s2, 3 * W / 4))):
                x = cx + (-dx if side == 0 else dx); put(im, lab, x, 600, k); put(im, sub, x, 1430, k)
                d.rounded_rectangle((x - 230, 660, x + 230, 1360), 30, fill=(10, 16, 28, 0), outline=(60, 72, 96), width=3)
                d.rounded_rectangle((x - 60, 1150, x + 60, 1260), 16, fill=(20, 32, 58), outline=GOLD, width=5)  # mini store
                d.arc((x - 35, 1115, x + 35, 1175), 180, 360, fill=GOLD, width=6)
            if t >= split_at + 0.4:
                for j in range(8):  # ads: new customers stream down into the store
                    p = ((t - split_at) * 0.7 + j / 8) % 1; x = W / 4 - dx + 150 * math.sin(j * 1.9) * (1 - p); y = 720 + 430 * p
                    d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=WHITE); d.ellipse((x - 5, y - 26, x + 5, y - 16), fill=WHITE)
                for j in range(3):  # email: envelopes fly out to a customer and come back with a coin
                    p = ((t - split_at - 0.6) * 0.45 + j / 3) % 1; ang = p * 2 * math.pi; x = 3 * W / 4 + dx + 150 * math.sin(ang); y = 940 - 190 * math.sin(ang / 2) + 120 * math.cos(ang)
                    d.rectangle((x - 30, y - 20, x + 30, y + 20), fill=WHITE); d.line((x - 30, y - 20, x, y + 2, x + 30, y - 20), fill=GOLD, width=4)
                    if p > 0.5: put(im, coin(14), x + 34, y - 18, 1)
                    d = ImageDraw.Draw(im)
                cx3 = 3 * W / 4 + dx; d.ellipse((cx3 - 20, 760, cx3 + 20, 800), fill=(200, 206, 220)); d.pieslice((cx3 - 36, 796, cx3 + 36, 860), 180, 360, fill=(200, 206, 220))
        if t >= keep_at:
            rise(im, k1, W / 2, 470, t, keep_at); rise(im, k2, W / 2, 575, t, keep_at + 0.6)
            pl = tuple(clamp((t - p0) / 0.35) for p0 in plug_at); fl = 0.25 + 0.6 * eio((t - plug_at[0]) / 2.6)
            kb = spring((t - keep_at - 0.2) / 0.7, f=1.4, d=6); bag(im, W / 2, 1120 + 700 * (1 - kb), 1.05, t, plugged=pl, fill=fl, leak_from=keep_at)
            for p0 in plug_at:
                if p0 <= t < p0 + 0.12: sh = 8
        return im, sh
    ev = [(0.05, "swish", 0.4), (split_at, "whoosh", 0.6), (split_at + 0.3, "pop", 0.5), (split_at + 2.0, "ping", 0.4), (split_at + 4.2, "coin", 0.4), (split_at + 6.4, "coin", 0.4),
          (keep_at - 0.2, "whoosh", 0.6), (keep_at, "swish", 0.5), (keep_at + 0.6, "hit", 0.7)] + [(p0, "pop", 0.8) for p0 in plug_at] + [(plug_at[-1] + 0.3, "shimmer", 0.8)]
    return dur, fn, ev


# ======================================================================= CTA: letters drop into a comment bubble
def scene_cta(dur=5.2, ask_at=0.1, drop_at=1.0):
    """'Is your store leaking?' 'LEADS' - each letter drops into a big gold comment bubble; 'Comment it, and I'll send
    you how we'd plug it.'"""
    q = T("Store leaking?", 100); cap1, cap2 = T("Comment it, and I'll send you", 64), T("how we'd plug it.", 64)
    BW, BH = 760, 300
    def bb(d, s, im_):
        d.rounded_rectangle((0, 0, BW * s - 1, (BH - 50) * s), 60 * s, fill=GOLD)
        d.polygon([(120 * s, (BH - 52) * s), (200 * s, (BH - 52) * s), (110 * s, BH * s - 1)], fill=GOLD)
    BUB = shadowed(sprite(BW, BH, bb), blur=26, dy=16, alpha=140, pad=50)
    word = "LEADS"; f = A.font("bl", 150)
    def fn(t):
        im = view(1.0 + 0.6 * t, 1.12, 0.5, 0.5, blur=6, dark=0.6); sh = 0
        pop(im, q, W / 2, 460, t, ask_at, 1.4)
        k = spring((t - drop_at + 0.4) / 0.6, f=1.4, d=6); put(im, BUB, W / 2, 900 + 700 * (1 - k), clamp((t - drop_at + 0.4) / 0.15))
        x = W / 2 - f.getlength(word) / 2
        for i, ch in enumerate(word):
            wch = f.getlength(ch); t0 = drop_at + 0.2 + i * 0.16; kk = (t - t0) / 0.4
            if kk > 0: put(im, T(ch, 150, NAVY), x + wch / 2, 860 - 600 * (1 - spring(kk, f=1.6, d=6)), clamp(kk / 0.1), 1, 15 * (1 - eo(kk)) * (1 if i % 2 else -1))
            x += wch
            if t0 + 0.3 <= t < t0 + 0.38: sh = 6
        rise(im, cap1, W / 2, 1230, t, drop_at + 1.4); rise(im, cap2, W / 2, 1320, t, drop_at + 1.7); under(im, "how we'd plug it.", 64, W / 2, 1320, "plug it", (t - drop_at - 2.2) / 0.4)
        return im, sh
    return dur, fn, [(ask_at, "hit", 0.7), (drop_at - 0.4, "whoosh", 0.5)] + [(drop_at + 0.5 + i * 0.16, "hit", 0.5) for i in range(5)] + [(drop_at + 1.4, "swish", 0.4), (drop_at + 2.2, "swish", 0.5)]
