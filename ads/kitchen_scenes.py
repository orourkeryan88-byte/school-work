"""KITCHEN ad 'Before / After': deep sage + oak, cream type, warm and editorial. Motion: before/after slider wipes,
a like counter that stalls, months stamped BOOKED, a camera roll lifting a photo into the feed, comments popping,
a polaroid stack fanning out. Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed

CREAM = (246, 240, 228); DARK = (24, 30, 26); WHITE = (255, 255, 255)


def kitchen_art(w, h, after=True, seed=0):
    """illustrated kitchen. before: dated beige units, brown worktop, busy tiles, strip light.
    after: sage shaker units, white quartz worktop, brass handles, oak floor, pendant lights."""
    def fn(d, s, im):
        X = lambda f: f * w * s; Y = lambda f: f * h * s
        if after:
            d.rectangle((0, 0, X(1), Y(1)), fill=(242, 238, 230)); d.rectangle((0, Y(.78), X(1), Y(1)), fill=(196, 150, 104))
            for i in range(9): d.line((X(i / 8), Y(.78), X(i / 8 - .08), Y(1)), fill=(176, 132, 90), width=2 * s)
            unit = [(120, 150, 128), (100, 140, 140), (60, 70, 80)][seed % 3]
            d.rectangle((X(.05), Y(.12), X(.62), Y(.36)), fill=unit)                       # wall units
            for i in range(3): d.line((X(.05 + i * .19), Y(.12), X(.05 + i * .19), Y(.36)), fill=(255, 255, 255, 60), width=2 * s)
            d.rectangle((X(.05), Y(.36), X(.95), Y(.52)), fill=(250, 250, 248))           # splashback
            d.rectangle((X(.03), Y(.52), X(.97), Y(.56)), fill=(255, 255, 255))           # quartz worktop
            d.rectangle((X(.05), Y(.56), X(.95), Y(.78)), fill=unit)                       # base units
            for i in range(5):
                x = X(.05 + i * .18 + .09); d.line((x - 18 * s, Y(.6), x + 18 * s, Y(.6)), fill=(206, 170, 90), width=5 * s)  # brass handles
            for x in (.3, .5, .7):  # pendants
                d.line((X(x), 0, X(x), Y(.16)), fill=(60, 60, 60), width=2 * s); d.pieslice((X(x) - 28 * s, Y(.14), X(x) + 28 * s, Y(.22)), 180, 360, fill=(206, 170, 90))
                d.ellipse((X(x) - 18 * s, Y(.2), X(x) + 18 * s, Y(.25)), fill=(255, 236, 180))
            d.rectangle((X(.7), Y(.14), X(.92), Y(.34)), fill=(200, 226, 240)); d.line((X(.81), Y(.14), X(.81), Y(.34)), fill=WHITE, width=3 * s)  # window
        else:
            d.rectangle((0, 0, X(1), Y(1)), fill=(214, 200, 170)); d.rectangle((0, Y(.78), X(1), Y(1)), fill=(150, 120, 96))
            for i in range(20):
                for j in range(4): d.rectangle((X(.05 + i * .045), Y(.36 + j * .04), X(.05 + i * .045 + .04), Y(.36 + j * .04 + .035)), fill=(196, 176, 130) if (i + j) % 2 else (226, 206, 160))
            d.rectangle((X(.05), Y(.1), X(.62), Y(.36)), fill=(200, 170, 120)); d.rectangle((X(.05), Y(.56), X(.95), Y(.78)), fill=(200, 170, 120))
            for i in range(4): d.rectangle((X(.07 + i * .14), Y(.13), X(.19 + i * .14), Y(.33)), outline=(160, 130, 90), width=3 * s)
            d.rectangle((X(.03), Y(.52), X(.97), Y(.56)), fill=(120, 80, 50))
            d.rectangle((X(.3), Y(.03), X(.7), Y(.06)), fill=(250, 250, 230))  # strip light
    return sprite(w, h, fn)


def label(s, col=DARK, bg=CREAM):
    f = A.font("bl", 30); tw = A.tsize(s, f)[0]
    return sprite(tw + 40, 54, lambda d, sc, im: (d.rounded_rectangle((0, 0, (tw + 40) * sc - 1, 54 * sc - 1), 27 * sc, fill=bg),
                                                  d.text((20 * sc, 10 * sc), s, font=A.font("bl", 30 * sc), fill=col)))


def before_after(before, after, frac, handle=True):
    """composite: left part = after up to frac, right = before; white divider with a round handle"""
    out = before.copy(); x = int(before.width * frac)
    if x > 0: out.paste(after.crop((0, 0, x, after.height)), (0, 0))
    if handle:
        d = ImageDraw.Draw(out); d.rectangle((x - 3, 0, x + 3, out.height), fill=WHITE); cy = out.height / 2
        d.ellipse((x - 34, cy - 34, x + 34, cy + 34), fill=WHITE)
        d.polygon([(x - 8, cy - 12), (x - 22, cy), (x - 8, cy + 12)], fill=DARK); d.polygon([(x + 8, cy - 12), (x + 22, cy), (x + 8, cy + 12)], fill=DARK)
    return out


def rounded(img, r=36):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), r, fill=255)
    o = img.copy(); o.putalpha(m); return o


# ---------------------------------------------------------------- HOOK: before / after, then 11 likes
def scene_ba_hook(word="Kitchen fitters,", dur=4.3, sweep=(0.0, 1.5), start=0.35, likes_at=2.2):
    """frame 0: 'Kitchen fitters,' + a big before/after with the slider mid-drag (both halves visible). The slider sweeps
    to reveal the finished kitchen, then the like counter crawls to 11 and stalls: 'This got 11 likes.'"""
    big = text(word, "bl", fit_size(word, "bl", 150, 980), A.TH["accent"])
    b, a = kitchen_art(960, 820, False), kitchen_art(960, 820, True)
    lb, la = label("BEFORE"), label("AFTER", CREAM, DARK)
    l1 = text("This got 11 likes.", "bl", fit_size("This got 11 likes.", "bl", 104, 980)); l2 = text("on your page.", "bl", 80, A.TH["accent"])

    def fn(t):
        im = A.bg()
        put(im, big, W / 2, 290, 1)
        f = start + (0.97 - start) * eio(clamp((t - sweep[0]) / (sweep[1] - sweep[0])))
        f = f - 0.06 * math.sin(clamp((t - sweep[1]) / 0.5) * math.pi)  # little settle-back like a real drag
        ba = rounded(before_after(b, a, f, handle=t < likes_at)); put(im, shadowed(ba, blur=30, dy=18, alpha=90), W / 2, 860, 1)
        put(im, la, W / 2 - 480 + 90, 500, 1); put(im, lb, W / 2 + 480 - 100, 500, 1 - clamp((f - 0.85) / 0.1))
        if t >= likes_at:
            k = (t - likes_at) / 0.4; n = min(11, int(11 * eo((t - likes_at) / 1.0)))
            d = ImageDraw.Draw(im); hx, hy = 150, 1350
            d.ellipse((hx - 34, hy - 30, hx, hy + 4), fill=(230, 80, 90)); d.ellipse((hx, hy - 30, hx + 34, hy + 4), fill=(230, 80, 90)); d.polygon([(hx - 33, hy - 10), (hx + 33, hy - 10), (hx, hy + 32)], fill=(230, 80, 90))
            put(im, text(f"{n} likes", "bl", 60), hx + 60 + text(f"{n} likes", "bl", 60).width / 2, hy, clamp(k / 0.3))
            put_rise(im, l1, W / 2, 1480, eo((t - likes_at - 0.6) / 0.3)); put_rise(im, l2, W / 2, 1590, eo((t - likes_at - 0.9) / 0.3))
        return im, 0
    return dur, fn, [(0.0, "swish", 0.7), (sweep[1] - 0.2, "shimmer", 0.6)] + [(likes_at + i * 0.09, "tick", 0.35) for i in range(11)] + [(likes_at + 0.6, "whoosh", 0.4)]


# ---------------------------------------------------------------- OPEN LOOP: down the road, booked till spring
def scene_booked_till_spring(dur=3.6, months=("NOV", "DEC", "JAN", "FEB", "MAR", "APR"), flip_from=1.1, gap=0.3):
    q1 = text("So why is the fitter", "bl", 78); q2 = text("down the road", "bl", 78); q3 = text("booked until spring?", "bl", 92, A.TH["accent"])

    def fn(t):
        im = A.bg()
        put_rise(im, q1, W / 2, 380, eo(t / 0.25)); put_rise(im, q2, W / 2, 470, eo((t - 0.12) / 0.25)); put_rise(im, q3, W / 2, 575, eo((t - 0.24) / 0.25))
        d = ImageDraw.Draw(im)
        for i, m in enumerate(months):
            x = 190 + (i % 3) * 350; y = 860 + (i // 3) * 360
            k = eo((t - 0.5 - i * 0.06) / 0.3)
            if k <= 0: continue
            d.rounded_rectangle((x - 140, y - 150, x + 140, y + 150), 24, fill=CREAM)
            d.rectangle((x - 140, y - 150, x + 140, y - 90), fill=A.TH["accent"])
            put(im, text(m, "bl", 40, DARK), x, y - 120, k); put(im, text("31", "bl", 110, (150, 150, 140)), x, y + 20, k)
            sk = (t - flip_from - i * gap) / 0.25
            if sk > 0:
                st = Image.new("RGBA", (300, 90), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.rounded_rectangle((0, 0, 299, 89), 12, outline=(200, 60, 50), width=8)
                tx = text("BOOKED", "bl", 54, (200, 60, 50)); st.alpha_composite(tx, (150 - tx.width // 2, 45 - tx.height // 2))
                put(im, st, x, y + 30, clamp(sk / 0.3), 1.6 - 0.6 * eo(sk), -12)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(flip_from + i * gap, "hit", 0.55) for i in range(len(months))]


# ---------------------------------------------------------------- BODY 1: camera roll -> the feed
def scene_camera_roll(dur=5.6, lift_at=2.0, swap_at=3.6):
    """a phone camera roll full of finished kitchens; one lifts out and flies into a sponsored post in the feed,
    where its before/after slider plays. Header: YOUR BEST WORK… IS IN YOUR CAMERA ROLL -> THEIRS IS IN THE FEED."""
    thumbs = [kitchen_art(230, 230, True, i) for i in range(3)] + [kitchen_art(230, 230, False)]
    b, a = kitchen_art(760, 640, False), kitchen_art(760, 640, True, 0)

    def post(f):
        card = Image.new("RGBA", (820, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, 819, 899), 40, fill=CREAM)
        d.ellipse((30, 30, 100, 100), fill=A.TH["accent"]); put(card, text("Your Kitchens", "b", 36, DARK), 220, 52, 1); put(card, text("Sponsored", "m", 26, (120, 120, 110)), 185, 88, 1)
        card.alpha_composite(rounded(before_after(b, a, f), 20), (30, 130))
        d.rounded_rectangle((30, 800, 790, 880), 40, fill=A.TH["accent"]); put(card, text("Get a quote", "b", 40, DARK), 410, 840, 1)
        return card

    def fn(t):
        im = A.bg(); swap = t >= swap_at
        if not swap:
            put_rise(im, text("YOUR BEST WORK…", "bl", 92), W / 2, 300, eo(t / 0.25)); put_rise(im, text("IS IN YOUR CAMERA ROLL.", "bl", fit_size("IS IN YOUR CAMERA ROLL.", "bl", 80, 980), A.TH["accent"]), W / 2, 400, eo((t - 0.6) / 0.25))
        else:
            put_rise(im, text("THEIRS IS", "bl", 92), W / 2, 300, eo((t - swap_at) / 0.25)); put_rise(im, text("IN THE FEED.", "bl", 104, A.TH["accent"]), W / 2, 405, eo((t - swap_at - 0.12) / 0.25))
        lk = eio((t - lift_at) / 0.9)
        if lk < 1:  # camera roll grid
            g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
            gd.rounded_rectangle((90, 520, W - 90, 1600), 40, fill=(20, 26, 22)); put(g, text("Recents", "b", 40, CREAM), 230, 580, 1); put(g, text("2,431", "m", 32, (150, 160, 150)), W - 200, 580, 1)
            for i in range(12):
                x, y = 220 + (i % 3) * 320, 760 + (i // 3) * 240
                if i != 4: put(g, thumbs[i % 4].resize((230, 230)), x, y, 1, 1)
            g.putalpha(g.split()[3].point(lambda v: int(v * (1 - lk))))
            im.alpha_composite(g)
        # the lifted photo flies into the feed post
        x0, y0, s0 = 220 + 320, 760 + 240, 230 / 760
        if t >= lift_at:
            f = 0.5 + 0.45 * math.sin(max(0, t - lift_at - 0.9) * 2.4) if t > lift_at + 0.9 else 0.98
            p = post(f); sc = s0 + (1 - s0) * lk
            put(im, shadowed(p, blur=30, dy=18, alpha=90), x0 + (W / 2 - x0) * lk, y0 + (1080 - y0) * lk, 1, sc * 1.0 if lk >= 1 else sc)
        else: put(im, thumbs[0].resize((230, 230)), x0, y0, 1, 1 + 0.08 * spring((t - lift_at + 0.3) / 0.3) if t > lift_at - 0.3 else 1)
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4), (lift_at, "swish", 0.7), (lift_at + 0.9, "pop", 0.7), (swap_at, "hit", 0.6)]


# ---------------------------------------------------------------- BODY 2: the comments roll in
def scene_comments(dur=4.6, start=0.6, gap=0.5):
    b, a = kitchen_art(760, 560, False), kitchen_art(760, 560, True, 1)
    C = [("Niamh K.", "Could you do ours??"), ("David O.", "How soon could you start?"), ("Sinéad M.", "Sent you a message!"), ("Aidan R.", "Love the green. Price for a 4-bed?")]

    def bubble(n, c):
        f = A.font("m", 34); tw = max(A.tsize(c, f)[0], A.tsize(n, A.font("b", 30))[0]) + 140
        return sprite(tw, 130, lambda d, s, im: (d.ellipse((0, 20 * s, 80 * s, 100 * s), fill=(180, 190, 176)), d.rounded_rectangle((96 * s, 0, tw * s - 1, 130 * s - 1), 34 * s, fill=CREAM),
                                                 d.text((126 * s, 18 * s), n, font=A.font("b", 30 * s), fill=DARK), d.text((126 * s, 62 * s), c, font=A.font("m", 34 * s), fill=(60, 60, 56))))
    bubs = [bubble(*c) for c in C]

    def fn(t):
        im = A.bg()
        put_rise(im, text("WE TURN YOUR", "bl", 84), W / 2, 290, eo(t / 0.25)); put_rise(im, text("BEFORE & AFTERS", "bl", 96, A.TH["accent"]), W / 2, 385, eo((t - 0.1) / 0.25))
        put_rise(im, text("INTO ENQUIRIES.", "bl", 84), W / 2, 480, eo((t - 0.2) / 0.25))
        f = 0.5 + 0.45 * math.sin(t * 2.4); ba = rounded(before_after(b, a, f), 30)
        put(im, shadowed(ba, blur=24, dy=14, alpha=80), W / 2, 870, 1, 0.98 + 0.02 * eio(t / dur))
        n = sum(1 for i in range(len(C)) if t >= start + i * gap)
        for i in range(n):
            k = (t - start - i * gap) / 0.35
            put(im, bubs[i], 120 + bubs[i].width / 2 + (20 if i % 2 else 0), 1230 + i * 100, clamp(k / 0.3), 0.85 + 0.15 * spring(k))
        put(im, text("EXAMPLE COMMENTS", "b", 24, (150, 160, 150)), W - 190, 1650, eo(t / 0.4))
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(start + i * gap, "pop", 0.65) for i in range(len(C))]


# ---------------------------------------------------------------- CTA: polaroid stack + logo sticker
def scene_polaroids(logo, dur=4.8, keyword="KITCHEN", drop=(0.2, 0.45, 0.7), logo_at=1.6, type_at=1.2):
    shots = [kitchen_art(560, 520, True, i) for i in range(3)]
    def polaroid(img):
        p = Image.new("RGBA", (640, 760), CREAM + (255,)); p.alpha_composite(img, (40, 40)); return p
    pols = [polaroid(s_) for s_ in shots]
    lg = logo.resize((200, 200), Image.LANCZOS); rot = [-9, 7, -2]; pos = [(W / 2 - 120, 900), (W / 2 + 130, 880), (W / 2, 930)]

    def fn(t):
        im = A.bg()
        put_rise(im, text("Want your kitchens", "bl", 78), W / 2, 300, eo(t / 0.25)); put_rise(im, text("in the feed?", "bl", 100, A.TH["accent"]), W / 2, 405, eo((t - 0.12) / 0.25))
        for i, (p, r, (x, y)) in enumerate(zip(pols, rot, pos)):
            k = (t - drop[i]) / 0.5
            if k <= 0: continue
            put(im, shadowed(p, blur=24, dy=16, alpha=110), x, y - 900 * (1 - eo(k)), 1, 1, r * (1 - 0.3 * eo(k)) + (1 - eo(k)) * 20)
        # handwritten caption on the top polaroid
        top_x, top_y = pos[2]; n = int(clamp((t - type_at) * 10, 0, len("Comment " + keyword)))
        cap = ("Comment " + keyword)[:n]
        if cap: sp = text(cap, "pfbi", 58, DARK); put(im, sp, top_x, top_y + 300, 1, 1, -2)
        if t >= logo_at:
            k = (t - logo_at) / 0.3; put(im, lg, top_x + 250, top_y - 330, clamp(k / 0.15), 1.5 - 0.5 * eo(k), 10)
        c = eo((t - logo_at - 0.3) / 0.4)
        put(im, text("Southline Agency", "bl", 54), W / 2, 1480 + 16 * (1 - c), c); put(im, text("Paid ads for Irish kitchen companies", "m", 32, A.TH["muted"]), W / 2, 1545 + 16 * (1 - c), c)
        return im, 0
    return dur, fn, [(d0 + 0.3, "hit", 0.6) for d0 in drop] + [(type_at + i / 10, "tick", 0.4) for i in range(len("Comment " + keyword))] + [(logo_at, "pop", 0.9)]
