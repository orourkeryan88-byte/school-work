"""ANIMATION PACK scenes: short stand-alone animations Ryan cuts between B-roll of himself working, for clothing brands.
Same look as the trust video (trust_scenes.py): white type with soft shadows, one blue accent, on a dark moving
background instead of B-roll. Sells Meta ads only; the fee line follows the clothing-brand wording rule
("our fee is tied to the sales our ads bring in"). No logo before the CTA.
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, eo, eio, back, spring, clamp, ring, sprite, shadowed
import trust_scenes as S
from trust_scenes import T, rise, pop, under, card, ctext, ACC, WHITE, INK, MUTED

RED = (235, 70, 80)


# ======================================================================= background
_BG = {}
def bg_shot(ts):
    """dark navy gradient with two soft blue glows drifting slowly, so the frame never sits dead still"""
    if not _BG:
        g = np.linspace(0, 1, H)[:, None, None]
        _BG["base"] = np.repeat(np.array((12, 15, 24), np.float32) * (1 - g) + np.array((4, 5, 9), np.float32) * g, W, axis=1)
        yy, xx = np.mgrid[0:H // 4, 0:W // 4]; _BG["grid"] = (yy * 4, xx * 4)
    yy, xx = _BG["grid"]; small = _BG["base"][::4, ::4].copy()
    for cx, cy, r, s, ph in ((300, 650, 560, 0.30, 0.0), (820, 1350, 620, 0.22, 2.0)):
        x = cx + 90 * math.sin(ts * 0.35 + ph); y = cy + 70 * math.cos(ts * 0.3 + ph)
        b = np.exp(-(((xx - x) / r) ** 2 + ((yy - y) / r) ** 2))[..., None] * s
        small = small * (1 - b) + np.array(ACC, np.float32) * b
    return Image.fromarray(np.clip(small, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)

def on_bg(scene):
    return S.with_shot(scene, bg_shot)

MIN_DARK = 0.0  # raise when the background is real, bright footage, so white type still reads

def back_view(t, dark=0.25):
    return S.vignette(S.view(t, 1.0, dark=max(dark, MIN_DARK)))


# ======================================================================= drawings
def tee(d, cx, cy, s, col, trim=None):
    """simple t-shirt silhouette centred at (cx, cy), s = width in px"""
    k = s / 100
    pts = [(-22, -40), (-8, -44), (0, -36), (8, -44), (22, -40), (48, -24), (38, -6), (26, -12), (26, 44), (-26, 44), (-26, -12), (-38, -6), (-48, -24)]
    d.polygon([(cx + x * k, cy + y * k) for x, y in pts], fill=col)
    d.arc((cx - 9 * k, cy - 50 * k, cx + 9 * k, cy - 34 * k), 0, 180, fill=trim or tuple(max(0, c - 40) for c in col), width=max(2, int(3 * k)))

def stars(d, x, y, r, n=5, col=(255, 196, 0)):
    for i in range(n):
        cx = x + i * r * 2.3; pts = []
        for j in range(10):
            a = -math.pi / 2 + j * math.pi / 5; rr = r if j % 2 == 0 else r * 0.45
            pts.append((cx + rr * math.cos(a), y + rr * math.sin(a)))
        d.polygon(pts, fill=col)

AD_KINDS = [  # (label, backdrop, shirt colour) for the four test ads
    ("Close-up", (236, 228, 218), (60, 72, 110)),
    ("Try-on", (220, 232, 242), (230, 120, 90)),
    ("Review", (244, 240, 232), (60, 72, 110)),
    ("Gift idea", (236, 222, 226), (90, 140, 110)),
]

def ad_card(label, back_, shirt, w=300, h=470, big=False):
    """a little sponsored post: brand row, product picture, label pill. big = shirt fills the frame (close-up)"""
    def dr(d, s):
        d.ellipse((22 * s, 22 * s, 62 * s, 62 * s), fill=INK); d.text((74 * s, 24 * s), "Your brand", font=A.font("bl", 24 * s), fill=INK)
        d.text((74 * s, 50 * s), "Sponsored", font=A.font("m", 18 * s), fill=MUTED)
        d.rounded_rectangle((18 * s, 84 * s, (w - 18) * s, (h - 96) * s), 18 * s, fill=back_)
        mid = (84 + h - 96) / 2
        if label == "Close-up": tee(d, w / 2 * s, mid * s, 250 * s, shirt)
        elif label == "Try-on":
            d.ellipse(((w / 2 - 26) * s, (mid - 118) * s, (w / 2 + 26) * s, (mid - 66) * s), fill=(214, 170, 140)); tee(d, w / 2 * s, (mid + 8) * s, 170 * s, shirt)
            d.rectangle(((w / 2 - 38) * s, (mid + 82) * s, (w / 2 - 8) * s, (mid + 140) * s), fill=(50, 56, 80)); d.rectangle(((w / 2 + 8) * s, (mid + 82) * s, (w / 2 + 38) * s, (mid + 140) * s), fill=(50, 56, 80))
        elif label == "Review":
            tee(d, w / 2 * s, (mid - 40) * s, 150 * s, shirt); stars(d, (w / 2 - 92) * s, (mid + 60) * s, 16 * s)
            d.text(((w / 2 - 100) * s, (mid + 92) * s), "“Best fit I own”", font=A.font("b", 22 * s), fill=INK)
        else:
            tee(d, w / 2 * s, (mid + 10) * s, 150 * s, shirt)
            d.rectangle(((w / 2 - 7) * s, (mid - 30) * s, (w / 2 + 7) * s, (mid + 54) * s), fill=RED)  # ribbon down the shirt + a bow
            d.ellipse(((w / 2 - 40) * s, (mid - 52) * s, (w / 2 - 2) * s, (mid - 22) * s), outline=RED, width=int(8 * s)); d.ellipse(((w / 2 + 2) * s, (mid - 52) * s, (w / 2 + 40) * s, (mid - 22) * s), outline=RED, width=int(8 * s))
        f = A.font("bl", 30 * s); tw = f.getlength(label); d.rounded_rectangle(((w / 2) * s - tw / 2 - 26 * s, (h - 74) * s, (w / 2) * s + tw / 2 + 26 * s, (h - 24) * s), 25 * s, fill=ACC)
        ctext(d, w / 2 * s, (h - 49) * s, label, f, WHITE)
    return card(w, h, dr, r=26)


# ======================================================================= scenes
def scene_who(dur=4.2, ryan_at=0.15, line_at=1.0, sub_at=1.7, pills_at=2.4):
    """'I'm Ryan.' slams with a pen circle round 'Ryan', 'I run Southline,' rises, then 'Meta ads for clothing brands'
    and the pills of the brands it's for"""
    im_, ryan = T("I'm", 170), T("Ryan.", 170); l2 = T("I run Southline,", 84); l3 = T("Meta ads for", 84); l4 = T("clothing brands.", 96, ACC)
    gap = A.font("bl", 170).getlength(" ") * 0.5; rw = im_.width + ryan.width - 72 + gap - 36
    def fn(t):
        im = back_view(t); sh = 14 if ryan_at <= t < ryan_at + 0.14 else 0
        k = (t - ryan_at) / 0.3
        if k > 0:
            x0 = W / 2 - rw / 2; s_ = 1.4 - 0.4 * back(k); y2 = 820
            put(im, im_, x0 + (im_.width - 36) / 2, y2, clamp(k / 0.15), s_)
            rx = x0 + im_.width - 36 + gap + (ryan.width - 36) / 2; put(im, ryan, rx, y2, clamp(k / 0.15), s_)
            p = eo((t - ryan_at - 0.35) / 0.45)
            if p > 0:
                ew, eh = (ryan.width - 40) * 0.57, 118
                ImageDraw.Draw(im).arc((rx - ew, y2 - eh, rx + ew, y2 + eh), 200, 200 + 350 * p, fill=ACC, width=11)
        rise(im, l2, W / 2, 1040, t, line_at); rise(im, l3, W / 2, 1240, t, sub_at); rise(im, l4, W / 2, 1355, t, sub_at + 0.25)
        under(im, "clothing brands.", 96, W / 2, 1355, "clothing brands", (t - pills_at) / 0.45)
        return im, sh
    return dur, fn, [(ryan_at, "hit", 0.9), (ryan_at + 0.35, "swish", 0.6), (line_at, "swish", 0.45), (sub_at, "swish", 0.4), (sub_at + 0.25, "pop", 0.6), (pills_at, "swish", 0.5)]


def scene_what(dur=4.6, s0_at=0.1, pills_at=(0.45, 0.75), s1_at=1.4, acct_at=2.2, eye_at=3.0):
    """'We run' + Facebook / Instagram pills + 'ads for clothing brands,' then an 'Your ad account' card slides up:
    'In your own ad account. You see every number.'"""
    s0 = T("We run", 84); s1 = T("ads for clothing brands.", 84)
    pf, pi = A.pill("Facebook", 50, WHITE, INK, w="bl"), A.pill("Instagram", 50, WHITE, INK, w="bl"); plus = T("+", 80, ACC)
    def ac(d, s):
        d.rounded_rectangle((0, 0, 820 * s, 96 * s), 30 * s, fill=ACC); d.rectangle((0, 60 * s, 820 * s, 96 * s), fill=ACC)
        ctext(d, 410 * s, 48 * s, "YOUR AD ACCOUNT", A.font("monob", 34 * s), WHITE)
        for i, lab in enumerate(("Ad spend", "Sales", "Cost per sale")):
            y = (150 + i * 92) * s; d.text((50 * s, y), lab, font=A.font("b", 40 * s), fill=INK)
            d.rounded_rectangle((470 * s, y + 6 * s, 770 * s, y + 46 * s), 20 * s, fill=(232, 236, 244))
    ACCT = card(820, 430, ac); cap1, cap2 = T("Your own ad account.", 76), T("You see every number.", 76)
    def fn(t):
        im = back_view(t, 0.3)
        rise(im, s0, W / 2, 380, t, s0_at)
        pop(im, pf, W / 2 - 220, 530, t, pills_at[0]); pop(im, plus, W / 2 + 10, 530, t, pills_at[0] + 0.15); pop(im, pi, W / 2 + 240, 530, t, pills_at[1])
        rise(im, s1, W / 2, 690, t, s1_at)
        if t >= acct_at:
            k = spring((t - acct_at) / 0.6, f=1.4, d=6); put(im, ACCT, W / 2, 1060 + 600 * (1 - k), clamp((t - acct_at) / 0.15))
            d = ImageDraw.Draw(im)
            for i in range(3):  # each value bar fills in as the account "opens up"
                p = eo((t - eye_at - i * 0.15) / 0.4)
                if p > 0: y = 1060 - 215 + 50 + 150 + i * 92 + 6; d.rounded_rectangle((W / 2 - 410 + 470 + 50, y, W / 2 - 410 + 470 + 50 + 300 * p, y + 40), 20, fill=ACC)
        rise(im, cap1, W / 2, 1400, t, acct_at + 0.4); rise(im, cap2, W / 2, 1500, t, eye_at)
        under(im, "You see every number.", 76, W / 2, 1500, "every number", (t - eye_at - 0.4) / 0.4)
        return im, 0
    return dur, fn, [(s0_at, "swish", 0.4), (pills_at[0], "pop", 0.6), (pills_at[1], "pop", 0.6), (s1_at, "swish", 0.4), (acct_at, "whoosh", 0.5),
                     (acct_at + 0.4, "swish", 0.4)] + [(eye_at + i * 0.15, "tick", 0.35) for i in range(3)] + [(eye_at + 0.4, "swish", 0.5)]


def scene_test(dur=4.8, head_at=0.1, cards_at=(0.7, 1.0, 1.3, 1.6), cap_at=2.4):
    """step 1: 'Several ads for your best seller' - four different ads (close-up, try-on, review, gift) fan in"""
    n1 = T("STEP 1", 44, ACC, "monob"); h1, h2 = T("Several ads for", 84), T("your best seller.", 84)
    cards = [ad_card(*k) for k in AD_KINDS]; c1, c2 = T("Each one from a", 70, (210, 216, 228), "b"), T("different angle.", 70, (210, 216, 228), "b")
    slots = [(W / 2 - 230, 830, -8), (W / 2 + 230, 830, 7), (W / 2 - 230, 1190, 6), (W / 2 + 230, 1190, -6)]
    def fn(t):
        im = back_view(t, 0.3)
        rise(im, n1, W / 2, 260, t, head_at); rise(im, h1, W / 2, 360, t, head_at + 0.1); rise(im, h2, W / 2, 465, t, head_at + 0.3)
        under(im, "your best seller.", 84, W / 2, 465, "best seller", (t - head_at - 0.7) / 0.4)
        for c, (x, y, r), t0 in zip(cards, slots, cards_at):
            k = (t - t0) / 0.55
            if k > 0:
                kk = spring(k, f=1.4, d=6); put(im, c, W / 2 + (x - W / 2) * kk, 1900 - (1900 - y) * kk, clamp(k / 0.2), 0.74, r * kk + math.sin(t * 1.4 + x) * 1.2)
        if t >= cap_at:
            a = clamp((t - cap_at) / 0.25); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(o).rounded_rectangle((90, 1420, W - 90, 1610), 40, fill=(8, 10, 16, int(215 * a))); im.alpha_composite(o)
            rise(im, c1, W / 2, 1475, t, cap_at); rise(im, c2, W / 2, 1558, t, cap_at + 0.2)
        return im, 0
    return dur, fn, [(head_at, "swish", 0.4), (head_at + 0.3, "swish", 0.4)] + [(x, "pop", 0.6) for x in cards_at] + [(cap_at, "swish", 0.4)]


def scene_winner(dur=5.0, head_at=0.1, bars_at=0.7, win_at=2.3, budget_at=3.0):
    """step 2: the four ads race as bars of sales; one pulls ahead, turns blue, gets a WINNER tag;
    'The budget goes behind it' - coins slide off the other bars onto the winner"""
    n1 = T("STEP 2", 44, ACC, "monob"); h1, h2 = T("Real buyers pick", 84), T("the winner.", 84)
    labels = [k[0] for k in AD_KINDS]; final = [0.42, 0.92, 0.55, 0.36]; WI = 1
    lab_sp = [T(l, 46, WHITE, "b") for l in labels]; tag = A.pill("WINNER", 34, ACC, WHITE, w="bl")
    cap = T("The budget goes behind it.", 72); X0, X1, Y0, DY = 150, 930, 760, 190
    def fn(t):
        im = back_view(t, 0.3); d = ImageDraw.Draw(im)
        rise(im, n1, W / 2, 260, t, head_at); rise(im, h1, W / 2, 360, t, head_at + 0.1); rise(im, h2, W / 2, 465, t, head_at + 0.3)
        under(im, "the winner.", 84, W / 2, 465, "winner", (t - win_at) / 0.4)
        grow = eio((t - bars_at) / 1.5); shift = eo((t - budget_at) / 0.9)
        for i, sp in enumerate(lab_sp):
            y = Y0 + i * DY; put(im, sp, X0 + sp.width / 2 - 36, y - 52, clamp((t - bars_at + 0.2) / 0.3))
            v = final[i] * grow + (math.sin(t * 6 + i) * 0.03 * (1 - grow))  # wobble while racing
            if i == WI: v = max(v, 0) * (1 + 0.08 * shift)
            else: v = max(0.0, v * (1 - 0.35 * shift))
            won = t >= win_at
            col = ACC if (won and i == WI) else ((90, 98, 118) if won else (170, 178, 196))
            d.rounded_rectangle((X0, y, X0 + 40, y + 70), 22, fill=(30, 34, 46)); d.rounded_rectangle((X0, y, X0 + 40 + (X1 - X0 - 40) * min(1, max(0, v)), y + 70), 22, fill=col)
            d.rounded_rectangle((X0, y, X1, y + 70), 22, outline=(60, 66, 84), width=3)
        if t >= win_at:
            pop(im, tag, X1 - 90, Y0 + WI * DY - 40, t, win_at, 1.6); ring(im, X1 - 90, Y0 + WI * DY + 35, (t - win_at) / 0.9, col=ACC, maxr=200, width=5, r0=40)
        if t >= budget_at:  # coins travel from the losing bars to the winner
            for i in (0, 2, 3):
                for j in range(3):
                    p = clamp((t - budget_at - 0.15 * j - 0.05 * i) / 0.7)
                    if 0 < p < 1:
                        sx, sy = X0 + 220, Y0 + i * DY + 35; ex, ey = X0 + 600, Y0 + WI * DY + 35
                        x = sx + (ex - sx) * eio(p); y = sy + (ey - sy) * eio(p) - 120 * math.sin(math.pi * p)
                        d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=(255, 200, 70), outline=(200, 140, 30), width=4)
            rise(im, cap, W / 2, 1600, t, budget_at + 0.3)
            under(im, "The budget goes behind it.", 72, W / 2, 1600, "behind it", (t - budget_at - 0.8) / 0.4)
        return im, (10 if win_at <= t < win_at + 0.12 else 0)
    return dur, fn, [(head_at, "swish", 0.4), (head_at + 0.3, "swish", 0.4), (bars_at, "whoosh", 0.4)] + [(bars_at + 0.2 * i, "tick", 0.3) for i in range(7)] + \
        [(win_at, "hit", 0.8), (win_at + 0.05, "pop", 0.7)] + [(budget_at + 0.35 + 0.12 * i, "coin", 0.35) for i in range(5)] + [(budget_at + 0.3, "swish", 0.4)]


def scene_back(dur=5.2, head_at=0.1, phone_at=0.6, ad_at=1.6, tap_at=2.6, order_at=3.0, cap_at=3.4):
    """step 3: a basket left with 1 item; next day the ad pops up in their feed ('Still thinking about it?'),
    a finger taps Shop now, 'Order placed' toast"""
    n1 = T("STEP 3", 44, ACC, "monob"); h1, h2 = T("Looked, but", 84), T("didn't buy?", 84)
    PW, PH = 560, 900
    def ph(d, s):
        d.rounded_rectangle((0, 0, PW * s - 1, PH * s - 1), 70 * s, fill=(18, 20, 28)); d.rounded_rectangle((18 * s, 18 * s, (PW - 18) * s, (PH - 18) * s), 56 * s, fill=(246, 247, 250))
        d.rounded_rectangle(((PW / 2 - 70) * s, 34 * s, (PW / 2 + 70) * s, 62 * s), 14 * s, fill=(18, 20, 28))
        d.text((60 * s, 110 * s), "Your basket", font=A.font("bl", 40 * s), fill=INK)
        d.rounded_rectangle((50 * s, 180 * s, (PW - 50) * s, 330 * s), 24 * s, fill=WHITE)
        d.rounded_rectangle((70 * s, 198 * s, 184 * s, 312 * s), 18 * s, fill=(236, 228, 218)); tee(d, 127 * s, 255 * s, 90 * s, (60, 72, 110))
        d.text((204 * s, 214 * s), "Everyday tee", font=A.font("b", 32 * s), fill=INK); d.text((204 * s, 262 * s), "1 item  ·  left in basket", font=A.font("m", 24 * s), fill=MUTED)
    PHONE = shadowed(sprite(PW, PH, lambda d, s, im: ph(d, s)), blur=30, dy=18, alpha=170, pad=60)
    def ad(d, s):
        d.ellipse((24 * s, 22 * s, 64 * s, 62 * s), fill=INK); d.text((78 * s, 22 * s), "Your brand", font=A.font("bl", 26 * s), fill=INK)
        d.text((78 * s, 52 * s), "Sponsored", font=A.font("m", 20 * s), fill=MUTED)
        d.text((24 * s, 92 * s), "Still thinking about it?", font=A.font("bl", 34 * s), fill=INK)
        d.rounded_rectangle((24 * s, 146 * s, 456 * s, 330 * s), 18 * s, fill=(236, 228, 218)); tee(d, 240 * s, 238 * s, 150 * s, (60, 72, 110))
        d.rounded_rectangle((24 * s, 348 * s, 456 * s, 412 * s), 32 * s, fill=ACC); ctext(d, 240 * s, 380 * s, "Shop now", A.font("bl", 32 * s), WHITE)
    AD = card(480, 436, ad, r=28); toast_ = A.toast("Order placed"); cap1 = T("They see you again.", 80)
    def fn(t):
        im = back_view(t, 0.3)
        rise(im, n1, W / 2, 260, t, head_at); rise(im, h1, W / 2, 360, t, head_at + 0.1); rise(im, h2, W / 2, 465, t, head_at + 0.3)
        py = 1080
        if t >= phone_at:
            k = spring((t - phone_at) / 0.6, f=1.4, d=6); put(im, PHONE, W / 2, py + 700 * (1 - k), clamp((t - phone_at) / 0.15), 0.95, 3 * (1 - k))
        if t >= ad_at:
            k = (t - ad_at) / 0.45; pressed = abs(t - tap_at) < 0.1
            put(im, AD, W / 2, py + 120, clamp(k / 0.2), (0.6 + 0.4 * back(k)) * (0.97 if pressed else 1))
            A.tap(im, W / 2 + 40, py + 120 + 160, t, tap_at, t_in=0.45, t_out=0.45, from_dx=140, from_dy=260)
        if t >= order_at:
            k = (t - order_at) / 0.4; put(im, toast_, W / 2, 760, clamp(k / 0.2), 0.7 + 0.3 * back(k))
        rise(im, cap1, W / 2, 1610, t, cap_at); under(im, "They see you again.", 80, W / 2, 1610, "see you again", (t - cap_at - 0.35) / 0.4)
        return im, 0
    return dur, fn, [(head_at, "swish", 0.4), (head_at + 0.3, "swish", 0.4), (phone_at, "whoosh", 0.5), (ad_at, "pop", 0.8), (tap_at, "click", 0.8),
                     (order_at, "ping", 0.6), (cap_at, "swish", 0.4), (cap_at + 0.35, "swish", 0.5)]


def scene_fee(dur=4.6, pill_at=0.2, strike_at=0.8, no_at=1.3, l1_at=2.1, l2_at=2.4):
    """'Monthly retainer' pill gets struck through and drops away; 'No monthly retainer.' then
    'Our fee is tied to the / sales our ads bring in.' (clothing-brand wording rule)"""
    pl = A.pill("Monthly retainer", 64, WHITE, INK, w="bl"); no = T("No monthly retainer.", 96)
    l1, l2 = T("Our fee is tied to the", 78), T("sales our ads bring in.", 78)
    def fn(t):
        im = back_view(t, 0.3); fall = eio((t - no_at + 0.2) / 0.5)
        if t >= pill_at and fall < 1:
            k = (t - pill_at) / 0.35; x, y = W / 2, 780 + 700 * fall * fall
            put(im, pl, x, y, (1 - fall) * clamp(k / 0.15), 0.6 + 0.4 * back(k), 10 * fall)
            p = eo((t - strike_at) / 0.25)
            if p > 0 and fall < 0.25: ImageDraw.Draw(im).line((x - pl.width / 2 + 10, y + 6, x - pl.width / 2 + 10 + (pl.width - 20) * p, y - 6), fill=RED, width=12)
        if t >= no_at: put(im, no, W / 2, 780, clamp((t - no_at) / 0.15), 1.3 - 0.3 * back((t - no_at) / 0.35))
        rise(im, l1, W / 2, 1060, t, l1_at); rise(im, l2, W / 2, 1165, t, l2_at)
        under(im, "sales our ads bring in.", 78, W / 2, 1165, "sales", (t - l2_at - 0.4) / 0.4)
        return im, (12 if no_at <= t < no_at + 0.14 else 0)
    return dur, fn, [(pill_at, "pop", 0.7), (strike_at, "swish", 0.7), (no_at - 0.2, "whoosh", 0.4), (no_at, "hit", 0.9), (l1_at, "swish", 0.4), (l2_at, "swish", 0.4), (l2_at + 0.4, "swish", 0.5)]


def scene_for(dur=4.4, head_at=0.15, times=(0.8, 1.1, 1.4, 1.7, 2.0), foot_at=2.7):
    """'Clothing brands' + niche chips sliding in from alternating sides; 'already selling online, ready to grow.'"""
    h1 = T("For clothing brands", 92); names = ["Womenswear", "Menswear", "Activewear", "Swimwear", "Kidswear"]
    W0 = [A.pill(n, 56, WHITE, INK, w="bl") for n in names]; W1 = [A.pill(n, 56, ACC, WHITE, w="bl") for n in names]
    f1, f2 = T("already selling online,", 72, (210, 216, 228), "b"), T("ready to grow.", 84)
    def fn(t):
        im = back_view(t, 0.3)
        if t >= head_at: put(im, h1, W / 2, 420, clamp((t - head_at) / 0.15), 1.3 - 0.3 * back((t - head_at) / 0.35))
        under(im, "For clothing brands", 92, W / 2, 420, "clothing brands", (t - head_at - 0.4) / 0.4)
        last = sum(t >= x for x in times) - 1
        for i in range(len(names)):
            k = (t - times[i]) / 0.4
            if k <= 0: continue
            side = -1 if i % 2 == 0 else 1
            put(im, W1[i] if i == last else W0[i], W / 2 + side * 700 * (1 - eo(k)), 650 + i * 150, 1, 1, side * 6 * (1 - eo(k)))
        rise(im, f1, W / 2, 1500, t, foot_at); rise(im, f2, W / 2, 1600, t, foot_at + 0.25)
        under(im, "ready to grow.", 84, W / 2, 1600, "grow", (t - foot_at - 0.6) / 0.4)
        return im, (10 if head_at <= t < head_at + 0.12 else 0)
    return dur, fn, [(head_at, "hit", 0.8), (head_at + 0.4, "swish", 0.5)] + [(x, "click", 0.7) for x in times] + [(foot_at, "swish", 0.4), (foot_at + 0.25, "swish", 0.4)]


def scene_cta(dur=4.6, logo_at=0.15, name_at=0.55, btn_at=1.2, tap_at=2.3):
    """end card: the Southline badge pops with a ring, 'Southline Agency', a 'Book a 15-min call' button gets tapped"""
    lg = A.logo().resize((240, 240), Image.LANCZOS); b1 = T("Southline Agency", 76); b2 = T("Meta ads for clothing brands", 40, (190, 198, 212), "m")
    up, dn = A.button("Book a 15-min call", w=860, h=150), A.button("Book a 15-min call", w=860, h=150, pressed=True)
    def fn(t):
        im = back_view(t, 0.3)
        k = (t - logo_at) / 0.5
        if k > 0: put(im, lg, W / 2, 720, clamp(k / 0.2), 0.6 + 0.4 * back(k)); ring(im, W / 2, 720, k / 1.6, col=ACC, maxr=380, width=5, r0=120)
        rise(im, b1, W / 2, 950, t, name_at); rise(im, b2, W / 2, 1030, t, name_at + 0.2)
        kb = (t - btn_at) / 0.45
        if kb > 0:
            pressed = abs(t - tap_at) < 0.12
            put(im, dn if pressed else up, W / 2, 1330, clamp(kb / 0.2), (0.6 + 0.4 * back(kb)) * (0.96 if pressed else 1))
            A.tap(im, W / 2 + 180, 1330, t, tap_at, t_in=0.5, t_out=0.6, from_dx=160, from_dy=300)
        return im, 0
    return dur, fn, [(logo_at, "pop", 0.8), (logo_at + 0.1, "shimmer", 0.6), (name_at, "swish", 0.4), (btn_at, "pop", 0.7), (tap_at, "click", 0.9)]
