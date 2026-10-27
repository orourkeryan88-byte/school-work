"""Custom scenes for the coaches pay-per-result Reel (v2): an opener where a coach rings prospect after prospect and
nobody picks up. Flat, stylised figures drawn with PIL so there's nothing to license."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, WHITE, clamp, eo, back, spring, put, put_rise, ring, pill, text, sprite, font, tsize

SKIN, HAIR, SHIRT = (242, 206, 172), (46, 34, 30), (38, 128, 140)
GREY, GREY2, RED = (108, 118, 128), (78, 86, 96), (226, 68, 68)


def man(sad=False):
    """head-and-shoulders coach holding a phone to his ear. sad: slanted brows + frown"""
    def dr(d, s, im):
        cx, cy = 210 * s, 190 * s; r = 92 * s
        d.pieslice((cx - 190 * s, cy + 70 * s, cx + 190 * s, cy + 430 * s), 180, 360, fill=SHIRT)           # shoulders
        d.rectangle((cx - 34 * s, cy + 60 * s, cx + 34 * s, cy + 120 * s), fill=SKIN)                       # neck
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=SKIN)                                              # head
        d.chord((cx - r, cy - r, cx + r, cy + r), 190, 350, fill=HAIR)                                      # hair
        d.rectangle((cx - r, cy - 40 * s, cx - r + 26 * s, cy + 10 * s), fill=HAIR)                         # sideburn
        ey = cy - 6 * s
        for ex in (cx - 34 * s, cx + 30 * s): d.ellipse((ex - 8 * s, ey - 8 * s, ex + 8 * s, ey + 8 * s), fill=HAIR)  # eyes
        if sad:
            d.line((cx - 52 * s, ey - 40 * s, cx - 16 * s, ey - 28 * s), fill=HAIR, width=7 * s)
            d.line((cx + 12 * s, ey - 28 * s, cx + 48 * s, ey - 40 * s), fill=HAIR, width=7 * s)
            d.arc((cx - 30 * s, cy + 34 * s, cx + 30 * s, cy + 74 * s), 200, 340, fill=HAIR, width=7 * s)   # frown
        else:
            d.line((cx - 52 * s, ey - 34 * s, cx - 16 * s, ey - 34 * s), fill=HAIR, width=7 * s)
            d.line((cx + 12 * s, ey - 34 * s, cx + 48 * s, ey - 34 * s), fill=HAIR, width=7 * s)
            d.line((cx - 22 * s, cy + 48 * s, cx + 22 * s, cy + 48 * s), fill=HAIR, width=7 * s)           # flat mouth
        # phone held to the right ear, hand around it
        px = cx + r - 10 * s
        d.rounded_rectangle((px - 26 * s, cy - 70 * s, px + 30 * s, cy + 60 * s), 14 * s, fill=(24, 26, 30), outline=(70, 74, 80), width=3 * s)
        d.rounded_rectangle((px - 16 * s, cy - 58 * s, px + 20 * s, cy + 48 * s), 8 * s, fill=(52, 200, 170) if not sad else (90, 96, 104))
        d.ellipse((px - 42 * s, cy + 10 * s, px + 46 * s, cy + 92 * s), fill=SKIN)                         # hand
    return sprite(420, 620, dr)


def client():
    """faceless grey prospect: head + shoulders"""
    def dr(d, s, im):
        d.pieslice((20 * s, 130 * s, 200 * s, 330 * s), 180, 360, fill=GREY2)
        d.ellipse((66 * s, 30 * s, 154 * s, 118 * s), fill=GREY)
    return sprite(220, 240, dr)


def scene_unreachable(dur=5.6, calls=((0.8, "No answer"), (1.9, "Voicemail"), (3.0, "Left on seen")), sad_at=3.55,
                      hook=("Chasing people who", "never pick up?"), hook_at=3.75, tag="COACHES & COURSE CREATORS"):
    """the coach rings three prospects in turn; a 'Calling…' chip flies to each, bounces off with a red tag, and his
    face drops. Then the hook line slams in at the top."""
    calm, sad, cl = man(False), man(True), client()
    MX, MY = 330, 1060; PX, PY = MX + 100, MY - 70                       # man centre, phone position
    CY = [700, 980, 1260]; CX = 820                                      # the three prospects
    tags = [pill(txt, 30, RED, WHITE, w="bl") for _, txt in calls]
    calling = pill("Calling…", 26, (52, 200, 170), (6, 20, 24), w="bl")
    tg = pill(tag, 28, A.TH["accent"], w="bl")
    h1 = text(hook[0], "xb", A.fit_size(hook[0], "xb", 88, 960)); h2 = text(hook[1], "bl", A.fit_size(hook[1], "bl", 104, 960), grad=(A.TH["accent"], A.TH["accent2"], 0))
    q = text("?", "bl", 110, A.TH["accent2"])
    def fn(t):
        im = A.bg(); sh = 0
        put(im, tg, W / 2, 300, eo((t - 0.2) / 0.3), 0.8 + 0.2 * back((t - 0.2) / 0.4))
        # the man slides in from the left with a spring, bobbing slightly after
        k = spring(t / 0.7, f=1.6, d=6); put(im, sad if t >= sad_at else calm, MX - 500 * (1 - k), MY + 4 * math.sin(t * 2.4), clamp(t / 0.2), 1, 6 * (1 - eo(t / 0.6)))
        for i, (t0, _) in enumerate(calls):
            cy = CY[i]; fail = t0 + 0.55
            jitter = 8 * math.sin(t * 80) if fail <= t < fail + 0.25 else 0
            put(im, cl, CX + jitter, cy, eo((t - 0.3 - i * 0.12) / 0.3))
            if t0 <= t < fail:                                            # the call chip flies over
                p = eo((t - t0) / 0.55); x = PX + (CX - 60 - PX) * p; y = PY + (cy - PY) * p - 60 * math.sin(math.pi * p)
                put(im, calling, x, y, clamp((t - t0) / 0.1), 0.8 + 0.2 * p)
                ring(im, PX, PY, (t - t0) / 0.6, maxr=120, width=4, r0=20)
            if t >= fail:                                                 # bounce: red tag pops beside the prospect
                k2 = (t - fail) / 0.35
                put(im, tags[i], CX, cy + 150, clamp(k2 / 0.2), 0.7 + 0.3 * back(k2))
                ring(im, CX, cy, k2 / 1.4, col=RED, maxr=150, width=4, r0=60)
            if fail <= t < fail + 0.12 and i == len(calls) - 1: sh = 8
        if t >= sad_at: put(im, q, MX - 10, MY - 300 - 20 * eo((t - sad_at) / 0.4), eo((t - sad_at) / 0.3), 0.6 + 0.4 * back((t - sad_at) / 0.4))
        put_rise(im, h1, W / 2, 440, eo((t - hook_at) / 0.3)); put_rise(im, h2, W / 2, 545, eo((t - hook_at - 0.2) / 0.3))
        if hook_at + 0.2 <= t < hook_at + 0.36: sh = 10 * (1 - (t - hook_at - 0.2) / 0.16)
        A.underline(im, h2, W / 2, 545 + h2.height / 2 + 4, (t - hook_at - 0.5) / 0.35, h=12)
        return im, sh
    ev = [(0.0, "whoosh", 0.6), (0.2, "pop", 0.6)]
    for t0, _ in calls: ev += [(t0, "ping", 0.5), (t0 + 0.55, "click", 0.9), (t0 + 0.6, "glitch", 0.35)]
    ev += [(sad_at, "swish", 0.5), (hook_at, "whoosh", 0.5), (hook_at + 0.2, "hit", 1.0)]
    return dur, fn, ev
