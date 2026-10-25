"""WEDDING VENUE ad 'Saved': ivory paper, champagne gold, Playfair Display serif. Soft, elegant motion: drifting petals,
word-by-word fades, a slow camera pull-back, a sponsored post glowing at golden hour, sealed envelopes, an invitation
opening with the SA logo as the wax seal. No shake, no glitch.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed

INK = (46, 38, 34); BLUSH = (226, 160, 150); WHITE = (255, 255, 255)
_r = np.random.default_rng(21)
_PETALS = [(_r.uniform(0, W), _r.uniform(-H, H), _r.uniform(16, 30), _r.uniform(0.35, 1.0), _r.uniform(0, 6.28)) for _ in range(20)]
_PET = {}


def _petal(r, ang):
    """one soft petal sprite, cached by size and 15-degree angle step"""
    k = (int(r), int(ang // 15))
    if k not in _PET:
        sp = sprite(int(r * 2.4), int(r * 2.4), lambda d, s, im: (d.ellipse((r * 0.3 * s, r * 0.7 * s, r * 2.1 * s, r * 1.7 * s), fill=BLUSH + (150,)),
                                                                 d.ellipse((r * 1.1 * s, r * 0.95 * s, r * 2.1 * s, r * 1.45 * s), fill=(244, 196, 186, 120))))
        _PET[k] = sp.rotate(k[1] * 15, resample=Image.BICUBIC, expand=False)
    return _PET[k]


def petals(im, t, amount=1.0):
    """soft blush petals drifting down with a sway"""
    for x, y, r, sp, ph in _PETALS[:int(len(_PETALS) * amount)]:
        yy = (y + t * 150 * sp) % (H + 200) - 100; xx = x + 40 * math.sin(t * 1.3 * sp + ph)
        put(im, _petal(r, (math.degrees(ph) + t * 90 * sp) % 360), xx, yy, 0.45 + 0.5 * sp)


def serif(s, size, w="pf", col=None):
    return text(s, w, fit_size(s, w, size, 960), col or INK)


def words_in(im, line, cx, cy, t, t0, size, w="pf", col=None, step=0.09):
    """fade + rise a line word by word, centred on cx"""
    ws = line.split(" "); sps = [text(x, w, size, col or INK) for x in ws]; gap = size * 0.28
    total = sum(s.width for s in sps) + gap * (len(sps) - 1); x = cx - total / 2
    for i, sp in enumerate(sps):
        k = eo((t - t0 - i * step) / 0.45)
        if k > 0: put(im, sp, x + sp.width / 2, cy + 24 * (1 - k), k)
        x += sp.width + gap


def heart(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r * 0.9, cx, cy + r * 0.1), fill=col); d.ellipse((cx, cy - r * 0.9, cx + r, cy + r * 0.1), fill=col)
    d.polygon([(cx - r * 0.98, cy - r * 0.25), (cx + r * 0.98, cy - r * 0.25), (cx, cy + r)], fill=col)


def venue_art(w, h, kind, sky=((250, 200, 160), (255, 236, 214))):
    """little illustrated venue: golden-hour sky, lawn, and a manor / castle / barn / glasshouse silhouette"""
    def fn(d, s, im):
        g = A.gradient((w * s, h * s), sky[0], sky[1], 90); im.paste(g, (0, 0))
        d.ellipse((w * 0.62 * s, h * 0.12 * s, w * 0.84 * s, h * 0.34 * s), fill=(255, 244, 220))
        d.rectangle((0, h * 0.72 * s, w * s, h * s), fill=(148, 170, 120))
        b = (90, 80, 86); win = (255, 220, 150); X = lambda f: f * w * s; Y = lambda f: f * h * s
        if kind == "manor":
            d.rectangle((X(.18), Y(.42), X(.82), Y(.74)), fill=(238, 228, 214)); d.polygon([(X(.14), Y(.44)), (X(.5), Y(.24)), (X(.86), Y(.44))], fill=b)
            for i in range(5): d.rectangle((X(.24 + i * .11), Y(.5), X(.3 + i * .11), Y(.6)), fill=win)
        elif kind == "castle":
            d.rectangle((X(.25), Y(.38), X(.75), Y(.74)), fill=(180, 170, 160))
            for i in range(6): d.rectangle((X(.25 + i * .09), Y(.33), X(.3 + i * .09), Y(.38)), fill=(180, 170, 160))
            d.rectangle((X(.15), Y(.3), X(.27), Y(.74)), fill=(170, 160, 150)); d.rectangle((X(.73), Y(.3), X(.85), Y(.74)), fill=(170, 160, 150))
            d.rectangle((X(.45), Y(.56), X(.55), Y(.74)), fill=(90, 70, 60))
        elif kind == "barn":
            d.polygon([(X(.25), Y(.5)), (X(.5), Y(.3)), (X(.75), Y(.5)), (X(.75), Y(.74)), (X(.25), Y(.74))], fill=(150, 80, 60))
            d.rectangle((X(.42), Y(.56), X(.58), Y(.74)), fill=win)
            for i in range(12): d.ellipse((X(.08 + i * .075) - 3 * s, Y(.2 + .05 * math.sin(i)) - 3 * s, X(.08 + i * .075) + 3 * s, Y(.2 + .05 * math.sin(i)) + 3 * s), fill=(255, 240, 180))
        else:  # glasshouse
            d.rounded_rectangle((X(.22), Y(.36), X(.78), Y(.74)), 60 * s, fill=(210, 230, 230), outline=(120, 120, 110), width=3 * s)
            for i in range(1, 6): d.line((X(.22 + i * .093), Y(.38), X(.22 + i * .093), Y(.74)), fill=(120, 120, 110), width=2 * s)
    return sprite(w, h, fn)


SKIES = [((250, 200, 160), (255, 236, 214)), ((214, 196, 236), (250, 226, 236)), ((180, 210, 236), (240, 236, 226)), ((246, 180, 170), (255, 226, 200))]
KINDS = ["manor", "castle", "barn", "glass"]


# ---------------------------------------------------------------- HOOK: their saved collection
def scene_saved(word="Wedding venues,", dur=4.4, pops=(0.25, 0.45, 0.65), line1_at=1.7, line2_at=2.9):
    """frame 0: gold italic 'Wedding venues,' + a 'Venue ideas' saved collection already full of hearted venues.
    The last tiles heart-pop in, the grid softens, then 'They saved 9 venues.' / 'Yours wasn't one of them.'"""
    big = text(word, "pfbi", fit_size(word, "pfbi", 150, 980), A.TH["accent"])
    tiles = [venue_art(250, 250, KINDS[i % 4], SKIES[(i * 3) % 4]) for i in range(9)]
    tl = [0.0] * 6 + list(pops)
    hdr = sprite(840, 90, lambda d, s, im: (d.text((0, 10 * s), "Saved", font=A.font("pfb", 54 * s), fill=INK),
                                            d.text((200 * s, 26 * s), "·  Venue ideas", font=A.font("m", 36 * s), fill=(140, 124, 112))))

    def fn(t):
        im = A.bg(); petals(im, t, 0.6)
        put(im, big, W / 2, 300, 1, 1.03 - 0.03 * eo(t / 0.6))
        card = Image.new("RGBA", (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((90, 440, W - 90, 1340), 40, fill=(255, 253, 249)); put(card, hdr, W / 2, 510, 1)
        for i, sp in enumerate(tiles):
            if t < tl[i]: continue
            k = (t - tl[i]) / 0.4 if tl[i] else 1
            x, y = 255 + (i % 3) * 285, 735 + (i // 3) * 285; put(card, sp, x, y, clamp(k / 0.3), 0.85 + 0.15 * spring(k))
            d = ImageDraw.Draw(card); heart(d, x + 92, y - 92, 22 * (0.6 + 0.4 * spring(k)), (232, 70, 90))
            if tl[i] and k < 1.5: ring(card, x + 92, y - 92, k / 1.2, col=(232, 70, 90), maxr=90, width=3, r0=10)
        sh = shadowed(card.crop((60, 410, W - 60, 1370)), blur=30, dy=18, alpha=40)
        soft = clamp((t - line1_at) / 0.6)
        if soft > 0: sh = sh.filter(ImageFilter.GaussianBlur(5 * soft))
        put(im, sh, W / 2, 890, 1 - 0.45 * soft)
        if t >= line1_at: words_in(im, "They saved 9 venues.", W / 2, 1420, t, line1_at, 92, "pfb")
        if t >= line2_at: words_in(im, "Yours wasn't one of them.", W / 2, 1540, t, line2_at, 80, "pfi", A.TH["accent2"])
        return im, 0
    return dur, fn, [(0.0, "shimmer", 0.6)] + [(p, "pop", 0.6) for p in pops] + [(line1_at, "whoosh", 0.3), (line2_at, "ping", 0.5)]


# ---------------------------------------------------------------- OPEN LOOP: the question
def scene_question(dur=3.6):
    """centred serif question appearing word by word; 'fall for?' in gold italic; a gold flourish draws beneath"""
    def fn(t):
        im = A.bg(); petals(im, t + 4, 0.8)
        words_in(im, "So where do couples", W / 2, 720, t, 0.1, 100, "pfb")
        words_in(im, "find the venue", W / 2, 860, t, 0.55, 100, "pfb")
        words_in(im, "they fall for?", W / 2, 1010, t, 0.95, 120, "pfbi", A.TH["accent"])
        p = eio((t - 1.5) / 1.0)
        if p > 0:  # flourish: a gentle S-curve with a dot at each end
            pts = [(W / 2 - 300 + 600 * u, 1150 + 26 * math.sin(u * 2 * math.pi)) for u in [i / 80 * p for i in range(81)]]
            d = ImageDraw.Draw(im); d.line(pts, fill=A.TH["accent"], width=6, joint="curve")
            d.ellipse((pts[0][0] - 9, pts[0][1] - 9, pts[0][0] + 9, pts[0][1] + 9), fill=A.TH["accent"])
            if p >= 1: d.ellipse((pts[-1][0] - 9, pts[-1][1] - 9, pts[-1][0] + 9, pts[-1][1] + 9), fill=A.TH["accent"])
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.3), (0.95, "shimmer", 0.6), (1.5, "swish", 0.3)]


# ---------------------------------------------------------------- BODY 1: one of hundreds
def scene_hundreds(dur=5.0, pull=(0.3, 2.8), line2_at=3.0):
    """camera starts tight on 'your venue' on a directory page, then pulls back and back to reveal hundreds of listings"""
    cols, rows, tw = 14, 20, 120; gw, gh = cols * (tw + 14), rows * (tw + 14)
    grid = Image.new("RGBA", (gw, gh), (0, 0, 0, 0)); YOU = (6, 9)
    for r in range(rows):
        for c in range(cols):
            sp = venue_art(tw, tw, KINDS[(r * 3 + c) % 4], SKIES[(r + c) % 4]); grid.alpha_composite(sp, (c * (tw + 14), r * (tw + 14)))
    d = ImageDraw.Draw(grid); yx, yy = YOU[0] * (tw + 14), YOU[1] * (tw + 14)
    d.rounded_rectangle((yx - 6, yy - 6, yx + tw + 6, yy + tw + 6), 12, outline=A.TH["accent"], width=6)
    gbig = grid.resize((gw * 2, gh * 2), Image.LANCZOS)
    lab = text("Your venue", "pfbi", 44, A.TH["accent"])
    cx0, cy0 = yx + tw / 2, yy + tw / 2

    def fn(t):
        im = A.bg()
        p = eio(clamp((t - pull[0]) / (pull[1] - pull[0])))
        z = 7.0 * (1 - p) + 0.98 * p  # zoom factor: tight on your tile -> whole page
        cx = cx0 * (1 - p) + gw / 2 * p; cy = cy0 * (1 - p) + gh / 2 * p
        vw, vh = W / z, 980 / z  # viewport in grid pixels
        src = gbig.crop((int((cx - vw / 2) * 2), int((cy - vh / 2) * 2), int((cx + vw / 2) * 2), int((cy + vh / 2) * 2))).resize((W, 980), Image.BILINEAR)
        im.alpha_composite(src, (0, 470))
        lx, ly = (cx0 - cx) * z + W / 2, (cy0 - cy) * z + 470 + 490
        put(im, lab, lx, ly + (tw / 2) * z + 40, 1 - clamp((t - 1.6) / 0.6))
        d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 470), fill=A.TH["bg"][0]); d.rectangle((0, 1450, W, H), fill=A.TH["bg"][1])
        words_in(im, "On the directories…", W / 2, 290, t, 0.1, 92, "pfb")
        if t >= line2_at: words_in(im, "you're one of hundreds.", W / 2, 1550, t, line2_at, 84, "pfbi", A.TH["accent2"])
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.3), (pull[0], "swish", 0.5)] + [(pull[0] + i * 0.25, "tick", 0.25) for i in range(9)] + [(line2_at, "ping", 0.4)]


# ---------------------------------------------------------------- BODY 2: alone in their feed
def scene_alone(dur=5.2, line2_at=1.6, heart_at=2.6, tap_at=3.6):
    """one tall sponsored post of your venue at golden hour, fairy lights twinkling, the only thing on screen; they
    heart it, then tap 'Request a viewing' and an envelope floats off"""
    PW, PH = 760, 1240
    art = venue_art(PW - 60, 760, "barn", ((246, 176, 140), (255, 226, 196)))

    def post(t, pressed):
        def fn(d, s, im):
            d.rounded_rectangle((0, 0, PW * s - 1, PH * s - 1), 46 * s, fill=(255, 253, 249))
            d.ellipse((34 * s, 34 * s, 104 * s, 104 * s), fill=A.TH["accent"])
            d.text((124 * s, 36 * s), "Your Venue", font=A.font("b", 36 * s), fill=INK); d.text((124 * s, 80 * s), "Sponsored", font=A.font("m", 26 * s), fill=(140, 124, 112))
            d.text((34 * s, 1000 * s), "Your 2027 wedding, right here.", font=A.font("pfb", 40 * s), fill=INK)
            d.rounded_rectangle((34 * s, 1100 * s, (PW - 34) * s, 1200 * s), 50 * s, fill=(150, 112, 60) if pressed else A.TH["accent"])
            f = A.font("b", 40 * s); tw = A.tsize("Request a viewing", f)[0]; d.text((PW * s / 2 - tw / 2, 1126 * s), "Request a viewing", font=f, fill=WHITE)
        sp = sprite(PW, PH, fn); sp.alpha_composite(art, (30, 140))
        d = ImageDraw.Draw(sp)
        for i in range(16):  # twinkling fairy lights strung across the photo
            x = 60 + i * 42; y = 220 + 40 * math.sin(i * 0.5); a = int(150 + 105 * math.sin(t * 6 + i))
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 236, 170, a))
        return shadowed(sp, blur=34, dy=22, alpha=50)
    env = sprite(150, 100, lambda d, s, im: (d.rectangle((0, 0, 150 * s - 1, 100 * s - 1), fill=(255, 250, 240), outline=A.TH["accent"], width=3 * s),
                                             d.line((0, 0, 75 * s, 55 * s, 150 * s, 0), fill=A.TH["accent"], width=3 * s), d.ellipse((60 * s, 40 * s, 90 * s, 70 * s), fill=(176, 60, 60))))

    def fn(t):
        im = A.bg(); petals(im, t + 8, 0.5)
        words_in(im, "In their feed…", W / 2, 280, t, 0.1, 92, "pfb")
        if t >= line2_at: words_in(im, "you're the only one on screen.", W / 2, 390, t, line2_at, 64, "pfi", A.TH["accent2"])
        pressed = abs(t - tap_at) < 0.1
        put(im, post(t, pressed), W / 2, 1110 + 14 * math.sin(t * 1.2), 1, 0.98 + 0.02 * eio(t / dur))
        if t >= heart_at:
            k = (t - heart_at) / 0.6; d = ImageDraw.Draw(im); heart(d, W / 2, 900, 90 * (0.4 + 0.6 * back(clamp(k / 0.5))), (232, 70, 90, int(255 * clamp(1.6 - k))))
        A.tap(im, W / 2 + 100, 1110 - 620 + 1150, t, tap_at)
        if t > tap_at + 0.1:
            k = eio((t - tap_at - 0.1) / 1.1); put(im, env, W / 2 + 380 * k, 1700 - 1300 * k, 1 - clamp((k - 0.8) / 0.2), 1, -20 * k)
        return im, 0
    return dur, fn, [(0.1, "whoosh", 0.3), (line2_at, "shimmer", 0.4), (heart_at, "pop", 0.8), (tap_at, "click", 0.9), (tap_at + 0.15, "whoosh", 0.5)]


# ---------------------------------------------------------------- the enquiries that follow
def envelope(label1, label2, label3, w=860, h=280):
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 18 * s, fill=(255, 250, 240), outline=(226, 210, 186), width=3 * s)
        d.line((0, 0, w * s / 2, 120 * s, w * s, 0), fill=(226, 210, 186), width=3 * s)
        d.ellipse((w * s / 2 - 34 * s, 86 * s, w * s / 2 + 34 * s, 154 * s), fill=(176, 60, 60))
        d.text((44 * s, 168 * s), label1, font=A.font("b", 28 * s), fill=A.TH["accent"])
        d.text((44 * s, 206 * s), label2, font=A.font("pfb", 44 * s), fill=INK)
        tw = A.tsize(label3, A.font("pfi", 36 * s))[0]; d.text(((w - 44) * s - tw, 212 * s), label3, font=A.font("pfi", 36 * s), fill=(140, 124, 112))
    return shadowed(sprite(w, h, fn), blur=24, dy=14, alpha=40)


def scene_envelopes(dur=4.6, times=(0.9, 1.5, 2.1)):
    envs = [envelope("VIEWING REQUEST", "Aoife & Conor", "June 2027"), envelope("BROCHURE REQUEST", "Ciara & Tom", "Sept 2027"),
            envelope("VIEWING REQUEST", "Niamh & Seán", "May 2028")]

    def fn(t):
        im = A.bg(); petals(im, t + 12, 0.7)
        words_in(im, "That's where", W / 2, 300, t, 0.05, 96, "pfb"); words_in(im, "we put you.", W / 2, 420, t, 0.4, 110, "pfbi", A.TH["accent"])
        for i, (sp, ta) in enumerate(zip(envs, times)):
            k = (t - ta) / 0.9
            if k <= 0: continue
            y = 760 + i * 300; put(im, sp, W / 2 + 30 * math.sin(i * 2), y + 700 * (1 - eo(k)), clamp(k / 0.3), 1, (-2 + 2 * i) * eo(k))
        return im, 0
    return dur, fn, [(0.05, "whoosh", 0.3)] + [(x + 0.4, "ping", 0.6) for x in times]


# ---------------------------------------------------------------- CTA: the invitation
def scene_invitation(logo, dur=5.0, open_at=0.5, rise_at=1.1, seal_at=2.2, keyword="VIEWINGS"):
    """an envelope opens, the invitation card rises out: 'You're invited / to fill your 2027 calendar / Comment VIEWINGS',
    with the SA logo pressed on as the wax seal"""
    ew, eh = 900, 560; ex, ey = W / 2, 1180
    lg = logo.resize((210, 210), Image.LANCZOS)

    def card():
        cw, ch = 800, 900
        def fn(d, s, im):
            d.rectangle((0, 0, cw * s - 1, ch * s - 1), fill=(255, 253, 249)); d.rectangle((20 * s, 20 * s, (cw - 20) * s, (ch - 20) * s), outline=A.TH["accent"], width=3 * s)
            for txt_, f, y, col in (("You're invited", A.font("pfbi", 92 * s), 90, A.TH["accent"]), ("to fill your 2027", A.font("pf", 58 * s), 230, INK),
                                    ("wedding calendar.", A.font("pf", 58 * s), 300, INK), ("Comment", A.font("m", 36 * s), 440, (140, 124, 112)),
                                    (keyword, A.font("pfx", 96 * s), 490, INK)):
                tw = A.tsize(txt_, f)[0]; d.text((cw * s / 2 - tw / 2, y * s), txt_, font=f, fill=col)
            d.line(((cw / 2 - 120) * s, 420 * s, (cw / 2 + 120) * s, 420 * s), fill=A.TH["accent"], width=2 * s)
        return sprite(cw, ch, fn)
    cd = card(); brand = text("Southline Agency", "pfb", 60); sub = text("Paid ads for Irish wedding venues", "m", 34, A.TH["muted"])

    def fn(t):
        im = A.bg(); petals(im, t + 16, 1.0); d = ImageDraw.Draw(im)
        f = eio((t - open_at) / 0.5); tip = ey - eh / 2 + 300 * (1 - 2 * f)  # flap tip: down (closed) -> up (open)
        flap = [(ex - ew / 2, ey - eh / 2), (ex + ew / 2, ey - eh / 2), (ex, tip)]
        d.rectangle((ex - ew / 2, ey - eh / 2, ex + ew / 2, ey + eh / 2), fill=(240, 228, 210))  # envelope back
        if f >= 0.5: d.polygon(flap, fill=(236, 222, 200), outline=(226, 210, 186))  # open flap sits behind the card
        r = eio((t - rise_at) / 1.0)
        put(im, cd, ex, ey + 120 - 640 * r, 1, 0.92 + 0.08 * r)  # card rising out
        d = ImageDraw.Draw(im)  # front pocket: tucks the card's lower edge in
        d.polygon([(ex - ew / 2, ey - eh / 2 + 10), (ex, ey + 80), (ex + ew / 2, ey - eh / 2 + 10), (ex + ew / 2, ey + eh / 2), (ex - ew / 2, ey + eh / 2)], fill=(250, 240, 224), outline=(226, 210, 186))
        if f < 0.5: d.polygon(flap, fill=(236, 222, 200), outline=(226, 210, 186))  # closed flap in front
        if t >= seal_at:  # the SA logo pressed on as the wax seal
            k = (t - seal_at) / 0.35; put(im, lg, ex, ey - 640 + 120 + 380, clamp(k / 0.15), 1.5 - 0.5 * eo(k))
            ring(im, ex, ey - 640 + 120 + 380, k / 1.4, col=A.TH["accent"], maxr=300, width=4, r0=110)
        c = eo((t - seal_at - 0.4) / 0.5); put(im, brand, W / 2, 1530 + 16 * (1 - c), c); put(im, sub, W / 2, 1600 + 16 * (1 - c), c)
        return im, 0
    return dur, fn, [(0.0, "shimmer", 0.4), (open_at, "swish", 0.6), (rise_at, "whoosh", 0.5), (seal_at, "hit", 0.6), (seal_at + 0.05, "coin", 0.5)]
