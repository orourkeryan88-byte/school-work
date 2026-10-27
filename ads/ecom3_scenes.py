"""Custom scenes for the clothing-brand Reels: an abandoned basket, the email rescue timeline, and a stream of store
visitors who mostly leave. Flat garment icons drawn with PIL, nothing to license."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, WHITE, GREEN, clamp, eo, eio, back, spring, put, put_rise, ring, pill, text, sprite, font, tsize

RED = (226, 68, 68); INK = (24, 26, 32)


def garment(d, s, cx, cy, kind, col, bgc):
    """flat clothing icon at 2x scale: tee | hoodie | jeans"""
    if kind in ("tee", "hoodie"):
        d.rectangle((cx - 42 * s, cy - 40 * s, cx + 42 * s, cy + 58 * s), fill=col)
        d.polygon([(cx - 42 * s, cy - 40 * s), (cx - 78 * s, cy - 22 * s), (cx - 66 * s, cy + 6 * s), (cx - 42 * s, cy - 4 * s)], fill=col)
        d.polygon([(cx + 42 * s, cy - 40 * s), (cx + 78 * s, cy - 22 * s), (cx + 66 * s, cy + 6 * s), (cx + 42 * s, cy - 4 * s)], fill=col)
        if kind == "tee": d.ellipse((cx - 20 * s, cy - 52 * s, cx + 20 * s, cy - 30 * s), fill=bgc)
        else:
            d.ellipse((cx - 30 * s, cy - 72 * s, cx + 30 * s, cy - 24 * s), fill=col); d.ellipse((cx - 16 * s, cy - 60 * s, cx + 16 * s, cy - 34 * s), fill=bgc)
            d.rounded_rectangle((cx - 28 * s, cy + 18 * s, cx + 28 * s, cy + 48 * s), 6 * s, fill=bgc)
    else:
        d.rectangle((cx - 40 * s, cy - 58 * s, cx + 40 * s, cy - 40 * s), fill=col)
        d.polygon([(cx - 40 * s, cy - 40 * s), (cx - 4 * s, cy - 40 * s), (cx - 10 * s, cy + 66 * s), (cx - 46 * s, cy + 66 * s)], fill=col)
        d.polygon([(cx + 4 * s, cy - 40 * s), (cx + 40 * s, cy - 40 * s), (cx + 46 * s, cy + 66 * s), (cx + 10 * s, cy + 66 * s)], fill=col)


def product_card(name, price, kind, col):
    """small shop tile: garment icon, name, price"""
    def dr(d, s):
        d.rounded_rectangle((20 * s, 20 * s, 240 * s, 200 * s), 22 * s, fill=(240, 236, 230)); garment(d, s, 130 * s, 110 * s, kind, col, (240, 236, 230))
        d.text((24 * s, 216 * s), name, font=font("b", 30 * s), fill=A.TH["card_ink"]); d.text((24 * s, 256 * s), price, font=font("xb", 34 * s), fill=A.TH["accent"])
    return A.card_sprite(260, 310, dr, radius=30)


def basket_icon(col, s_=1.0):
    def dr(d, s, im):
        d.line((20 * s, 30 * s, 60 * s, 30 * s, 100 * s, 170 * s, 230 * s, 170 * s, 260 * s, 80 * s, 80 * s, 80 * s), fill=col, width=14 * s, joint="curve")
        d.ellipse((110 * s, 190 * s, 150 * s, 230 * s), fill=col); d.ellipse((190 * s, 190 * s, 230 * s, 230 * s), fill=col)
    return sprite(280, 250, dr)


def scene_basket(dur=5.6, items=(("Oversized tee", "€34", "tee", (60, 70, 90)), ("Heavy hoodie", "€68", "hoodie", (190, 70, 60)), ("Straight jeans", "€59", "jeans", (50, 80, 130))),
                 total=161, hook=("Clothing brands,", "Black Friday is weeks away."), add_at=(0.9, 1.5, 2.1), checkout_at=2.7, leave_at=3.5, line_at=4.3,
                 line="7 in 10 baskets end like this."):
    """three product tiles fly into a basket, the total counts up, a Checkout button appears, the cursor drifts away,
    a red LEFT AT CHECKOUT stamp slams on and the total goes grey. Then the stat line rises."""
    tiles = [product_card(n, p, k, c) for n, p, k, c in items]; bk = basket_icon(A.TH["ink"]); bk_grey = basket_icon(A.TH["muted"])
    h1 = text(hook[0], "bl", A.fit_size(hook[0], "bl", 120, 980), grad=(A.TH["accent"], A.TH["accent2"], 0)); h2 = text(hook[1], "xb", A.fit_size(hook[1], "xb", 70, 960))
    btn, btn_grey = A.button("Checkout", w=560, h=130), A.button("Checkout", w=560, h=130, pressed=True)
    stamp = text("LEFT AT CHECKOUT", "bl", A.fit_size("LEFT AT CHECKOUT", "bl", 84, 900), RED); ln = text(line, "xb", A.fit_size(line, "xb", 72, 960), A.TH["accent2"])
    prices = [int(p.strip("€")) for _, p, _, _ in items]
    def fn(t):
        im = A.bg(); sh = 10 * (1 - t / 0.18) if t < 0.18 else 0
        put(im, h1, W / 2, 400, clamp(t / 0.1), 1.12 - 0.12 * eo(t / 0.3)); put_rise(im, h2, W / 2, 520, eo((t - 0.3) / 0.3))
        left = t >= leave_at
        put(im, bk_grey if left else bk, 300, 1000, eo((t - 0.4) / 0.3), 0.9 + 0.1 * spring((t - 0.4) / 0.6))
        n = 0
        for i, tile in enumerate(tiles):
            k = (t - add_at[i]) / 0.55
            if k <= 0: continue
            if k < 1:
                p = eio(k); x = 900 + (300 - 900) * p; y = 760 + (1000 - 760) * p - 220 * math.sin(math.pi * p)
                put(im, tile, x, y, 1, 1 - 0.55 * p, -18 * p)
            else: n += 1
            if 0.95 < k < 1.6: ring(im, 300, 1000, (k - 0.95) / 0.65, maxr=160, width=4, r0=40)
        tot = sum(prices[:n])
        if n:
            lbl = pill(f"Basket: €{tot}", 40, A.TH["muted"] if left else A.TH["accent"], w="bl")
            put(im, lbl, 300, 1200, 1, 1 + 0.15 * (1 - eo((t - add_at[n - 1] - 0.55) / 0.25)))
        if t >= checkout_at:
            k = (t - checkout_at) / 0.4; put(im, btn_grey if left else btn, 760, 1000, clamp(k / 0.3), 0.7 + 0.3 * back(k))
            # cursor glides in towards the button, hovers, then at leave_at drifts off and fades: never taps
            g = eo((t - checkout_at - 0.2) / 0.6); cx_, cy_ = 820 + 200 * (1 - g), 1010 + 360 * (1 - g); al = clamp((t - checkout_at - 0.2) / 0.2)
            if left: lv = eo((t - leave_at) / 0.7); cx_ += 420 * lv; cy_ += 380 * lv; al *= 1 - lv
            if al > 0:
                o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).ellipse((cx_ - 30, cy_ - 30, cx_ + 30, cy_ + 30), fill=(255, 255, 255, int(210 * al)), outline=(17, 17, 16, int(120 * al)), width=3)
                im.alpha_composite(o)
        if left:
            k = (t - leave_at) / 0.3; put(im, stamp, W / 2, 1310, clamp(k / 0.15), 1.6 - 0.6 * eo(k), -6)
            if leave_at <= t < leave_at + 0.14: sh = 12
        put_rise(im, ln, W / 2, 1480, eo((t - line_at) / 0.35))
        return im, sh
    ev = [(0.0, "hit", 1.0), (0.3, "whoosh", 0.4)] + [(a + 0.5, "pop", 0.7) for a in add_at] + [(a + 0.55, "coin", 0.5) for a in add_at] + \
         [(checkout_at, "pop", 0.6), (leave_at, "hit", 1.0), (leave_at + 0.05, "glitch", 0.5), (line_at, "whoosh", 0.5)]
    return dur, fn, ev


def email_card(subject, preview, when):
    def dr(d, s):
        d.rounded_rectangle((36 * s, 50 * s, 116 * s, 130 * s), 20 * s, fill=A.TH["accent"])
        d.rectangle((54 * s, 72 * s, 98 * s, 108 * s), fill=WHITE); d.line((54 * s, 72 * s, 76 * s, 92 * s, 98 * s, 72 * s), fill=A.TH["accent"], width=4 * s)
        d.text((150 * s, 44 * s), subject, font=font("b", 36 * s), fill=A.TH["card_ink"]); d.text((150 * s, 100 * s), preview, font=font("m", 30 * s), fill=A.TH["muted"])
        f = font("sb", 28 * s); tw = f.getlength(when); d.text((820 * s - tw, 44 * s), when, font=f, fill=A.TH["muted"])
    return A.card_sprite(860, 180, dr, radius=32)


def scene_email_rescue(dur=5.2, title="What we do about it", emails=(("Still thinking about the hoodie?", "Your size is still in stock.", "1 hour"),
                       ("Your size is almost gone", "Only a few left in M.", "1 day"), ("Free shipping ends tonight", "Complete your order →", "3 days")),
                       at=(0.6, 1.4, 2.2), back_at=3.6, order=("Order #1043 · €161", "Basket recovered")):
    """three follow-up emails slide in down a timeline, then the order comes back as a green card with a coin"""
    cards = [email_card(*e) for e in emails]; tsp = text(title, "xb", 84)
    def ok(d, s):
        d.ellipse((40 * s, 50 * s, 120 * s, 130 * s), fill=GREEN); A.check(d, s, 56, 66, WHITE)
        d.text((150 * s, 44 * s), order[0], font=font("xb", 40 * s), fill=GREEN); d.text((150 * s, 102 * s), order[1], font=font("m", 30 * s), fill=A.TH["muted"])
    okc = A.card_sprite(860, 180, ok, radius=32)
    def fn(t):
        im = A.bg(); put_rise(im, tsp, W / 2, 430, eo(t / 0.35)); d = ImageDraw.Draw(im)
        lp = eio((t - at[0]) / max(0.5, at[-1] - at[0]))
        if lp > 0: d.line((W / 2 - 430 + 40, 640, W / 2 - 430 + 40, 640 + 230 * 2 * lp), fill=A.TH["muted"], width=6)
        for i, sp in enumerate(cards):
            k = (t - at[i]) / 0.5
            if k > 0: put(im, sp, W / 2 + 160 * (1 - eo(k)), 640 + i * 230, clamp(k / 0.3), 0.92 + 0.08 * spring(k))
        k = (t - back_at) / 0.5
        if k > 0:
            put(im, okc, W / 2, 1360 - 300 * (1 - spring(k, f=1.6, d=6)), clamp(k / 0.15), 1, 6 * (1 - eo(k)))
            ring(im, W / 2, 1360, k / 1.4, col=GREEN, maxr=320, width=5, r0=80)
        return im, (8 * (1 - (t - back_at - 0.25) / 0.12) if back_at + 0.25 <= t < back_at + 0.37 else 0)
    return dur, fn, [(0.0, "whoosh", 0.6)] + [(a, "swish", 0.6) for a in at] + [(a + 0.3, "ping", 0.4) for a in at] + [(back_at, "whoosh", 0.6), (back_at + 0.25, "coin", 0.9), (back_at + 0.3, "shimmer", 0.6)]


def scene_visitors(dur=5.2, n=12, buyers=(5,), hook=("Clothing brands,", "most visitors leave without buying."), hook_at=2.9,
                   counter=("100 visitors", "2 orders"), tag="typical store"):
    """a stream of shoppers walks past the store; nearly all turn grey with an x, one turns green with a bag. A counter
    pill at the top keeps score, then the hook lands."""
    shop = pill("YOUR STORE", 34, A.TH["accent"], w="bl"); tg = pill(tag, 26, (30, 34, 40), (190, 196, 206), w="b")
    def person(col, mark):
        def dr(d, s, im):
            d.ellipse((50 * s, 10 * s, 110 * s, 70 * s), fill=col); d.pieslice((20 * s, 80 * s, 140 * s, 220 * s), 180, 360, fill=col)
            if mark == "x":
                d.line((100 * s, 0, 150 * s, 50 * s), fill=RED, width=9 * s); d.line((150 * s, 0, 100 * s, 50 * s), fill=RED, width=9 * s)
            elif mark == "bag":
                d.rounded_rectangle((104 * s, 20 * s, 158 * s, 80 * s), 8 * s, fill=GREEN); d.arc((116 * s, 0, 146 * s, 40 * s), 180, 360, fill=GREEN, width=6 * s)
        return sprite(170, 160, dr)
    plain, gone, bought = person(A.TH["muted"], None), person((70, 76, 86), "x"), person(GREEN, "bag")
    h1 = text(hook[0], "bl", A.fit_size(hook[0], "bl", 120, 980), grad=(A.TH["accent"], A.TH["accent2"], 0)); h2 = text(hook[1], "xb", A.fit_size(hook[1], "xb", 66, 960))
    ST = [0.3 + i * 0.22 for i in range(n)]   # when each shopper starts walking
    def fn(t):
        im = A.bg(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((90, 700, 990, 1120), 40, fill=A.TH["card"]); d.rounded_rectangle((90, 700, 990, 790), 40, fill=A.TH["card"])
        put(im, shop, W / 2, 745, eo(t / 0.3))
        for i in range(n):
            k = (t - ST[i]) / 1.6
            if k <= 0: continue
            p = clamp(k); x = -100 + 1300 * p; y = 960
            if p < 0.45: sp = plain
            else: sp = bought if i in buyers else gone
            if p >= 1: continue
            put(im, sp, x, y + 6 * math.sin(t * 14 + i), 1 if p < 0.85 else (1 - (p - 0.85) / 0.15))
        seen = sum(1 for s_ in ST if t >= s_ + 0.72); b = sum(1 for i in buyers if t >= ST[i] + 0.72)
        if seen:
            lab = pill(f"{counter[0]} · {counter[1]}" if t >= ST[-1] + 0.72 else f"{seen} visitor{'s' if seen != 1 else ''} · {b} order{'s' if b != 1 else ''}", 40, (17, 17, 16) if A.TH["light"] else A.TH["ink"], A.TH["bg"][0], w="bl")
            put(im, lab, W / 2, 1210, 1); put(im, tg, W / 2, 1290, eo((t - ST[-1] - 0.72) / 0.3))
        put(im, h1, W / 2, 400, clamp((t - hook_at) / 0.1), 1.12 - 0.12 * eo((t - hook_at) / 0.3)); put_rise(im, h2, W / 2, 520, eo((t - hook_at - 0.3) / 0.3))
        return im, (10 * (1 - (t - hook_at) / 0.18) if hook_at <= t < hook_at + 0.18 else 0)
    ev = [(0.0, "whoosh", 0.5)] + [(s_ + 0.72, "coin" if i in buyers else "tick", 0.7 if i in buyers else 0.35) for i, s_ in enumerate(ST)] + [(hook_at, "hit", 1.0), (hook_at + 0.3, "whoosh", 0.4)]
    return dur, fn, ev
