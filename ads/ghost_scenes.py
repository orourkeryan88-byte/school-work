"""Scenes for the Southline roofers 'ghosted after the quote' silent ad. Built on adkit + helpers.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops
import adkit as A
from adkit import W, H, put, put_rise, text, pill, fit_size, eo, eio, back, spring, clamp, ring, underline, sprite, shadowed
from volt_scenes import RED, WHITE, DARK
from hook_scenes import stamp

CHAT_BG, THEM, META = (16, 18, 22), (38, 42, 50), (140, 146, 158)


def phone_shell(bg=CHAT_BG, clock="21:04"):
    """dark phone body + screen mask; returns (body, screen_mask)"""
    PW, PH = A.PW, A.PH
    body = sprite(PW, PH, lambda d, s, im: (d.rounded_rectangle((0, 0, PW * s - 1, PH * s - 1), 130 * s, fill=(28, 28, 30)),
                                            d.rounded_rectangle((16 * s, 16 * s, (PW - 16) * s, (PH - 16) * s), 116 * s, fill=bg)))
    d = ImageDraw.Draw(body); d.rounded_rectangle((PW // 2 - 130, 52, PW // 2 + 130, 120), 34, fill=(0, 0, 0))
    d.text((96, 58), clock, font=A.font("sb", 44), fill=(235, 235, 240))
    m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((22, 22, PW - 22, PH - 22), 110, fill=255)
    return body, m


def bubble(txt_lines, mine=True, w=640):
    """chat bubble sprite with wrapped lines"""
    f = A.font("m", 42); lh = 56; h = 40 + lh * len(txt_lines)
    col = A.TH["accent"] if mine else THEM; fg = WHITE
    return sprite(w, h, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 34 * s, fill=col),
                                          [d.text((30 * s, (20 + i * lh) * s), l, font=A.font("m", 42 * s), fill=fg) for i, l in enumerate(txt_lines)]))


def ticks(d, x, y, col, s=1):
    for dx in (0, 14):
        d.line(((x + dx) * s, (y + 12) * s, (x + dx + 9) * s, (y + 21) * s), fill=col, width=4 * s)
        d.line(((x + dx + 9) * s, (y + 21) * s, (x + dx + 26) * s, (y + 2) * s), fill=col, width=4 * s)


# ---------------------------------------------------------------- HOOK: quote sent, seen, nothing
def scene_ghosted(word="Roofers,", dur=3.6, seen_at=0.55, typing=(1.15, 1.75), days_from=1.9, nothing_at=2.5):
    """frame 0: giant 'Roofers,' + a chat where your quote is sent and 'Seen 21:04' is already showing, mid-slam.
    A SEEN. stamp hits, a 'typing…' bubble teases and vanishes, Tue/Wed/Thu dividers tick past with no reply,
    then '…AND THEN NOTHING.' rises in. Reads with the sound off."""
    big = text(word, "bl", fit_size(word, "bl", 240, 940), grad=(A.TH["accent"], A.TH["accent2"], 0))
    PW, PH = A.PW, A.PH; k_ = 0.7; body, scr = phone_shell()
    hdr = sprite(PW - 44, 150, lambda d, s, im: (d.rectangle((0, 0, (PW - 44) * s, 150 * s), fill=(26, 28, 34)),
                                                 d.ellipse((40 * s, 30 * s, 130 * s, 120 * s), fill=(90, 110, 140)),
                                                 d.text((70 * s, 52 * s), "S", font=A.font("b", 44 * s), fill=WHITE),
                                                 d.text((160 * s, 34 * s), "Sarah (new roof)", font=A.font("b", 44 * s), fill=WHITE),
                                                 d.text((160 * s, 90 * s), "last seen recently", font=A.font("m", 30 * s), fill=META)))
    b1 = bubble(["Hi Sarah, here's the quote", "for the roof. Any questions", "just give me a shout."])
    pdf = sprite(640, 130, lambda d, s, im: (d.rounded_rectangle((0, 0, 640 * s - 1, 130 * s - 1), 30 * s, fill=tuple(int(c * 0.8) for c in A.TH["accent"])),
                                             d.rounded_rectangle((26 * s, 22 * s, 96 * s, 108 * s), 10 * s, fill=WHITE),
                                             d.text((40 * s, 48 * s), "PDF", font=A.font("bl", 22 * s), fill=RED),
                                             d.text((120 * s, 30 * s), "Quote_Full_ReRoof.pdf", font=A.font("b", 36 * s), fill=WHITE),
                                             d.text((120 * s, 76 * s), "2 pages", font=A.font("m", 28 * s), fill=(255, 225, 200))))
    seen = sprite(300, 40, lambda d, s, im: (ticks(d, 0, 6, (90, 170, 255), s), d.text((50 * s, 0), "Seen 21:04", font=A.font("m", 32 * s), fill=META)))
    typ = sprite(200, 90, lambda d, s, im: (d.rounded_rectangle((0, 0, 200 * s - 1, 90 * s - 1), 45 * s, fill=THEM),
                                            [d.ellipse(((48 + i * 40) * s, 34 * s, (70 + i * 40) * s, 56 * s), fill=META) for i in range(3)]))
    days = ["Tuesday", "Wednesday", "Thursday", "Friday"]
    divs = [pill(d_, 30, (40, 44, 52), META, w="sb") for d_ in days]
    sst = shadowed(stamp("SEEN.", A.TH["accent"], 110), blur=10, dy=6, alpha=100, pad=30)
    n1 = text("…AND THEN", "bl", 96, A.TH["muted"]); n2 = text("NOTHING.", "bl", 150, A.TH["accent"])

    def fn(t):
        im = A.bg(); sh = 14 * (1 - t / 0.2) if t < 0.2 else 0
        put(im, big, W / 2, 330, 1, 1.08 - 0.08 * eo(t / 0.25))
        ph = body.copy(); scrn = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        nd = sum(1 for i in range(len(days)) if t >= days_from + i * 0.16)
        push = 110 * nd  # each new day divider pushes the chat up
        y0 = 560 - push
        put(scrn, b1, PW - 50 - b1.width / 2, y0, 1); put(scrn, pdf, PW - 50 - 320, y0 + b1.height / 2 + 90, 1)
        put(scrn, seen, PW - 50 - 150, y0 + b1.height / 2 + 190, 1)
        ty = y0 + b1.height / 2 + 300
        if typing[0] <= t < typing[1]:
            bob = 4 * math.sin(t * 20); put(scrn, typ, 50 + 100, ty + bob, clamp((t - typing[0]) / 0.1))
        for i in range(nd):
            put(scrn, divs[i], PW / 2, ty + 120 + i * 110, 1, 1 + 0.2 * (1 - eo((t - days_from - i * 0.16) / 0.15)))
        put(scrn, hdr, PW / 2, 22 + 75 + 150, 1)  # header on top so the chat scrolls under it
        scrn.putalpha(ImageChops.multiply(scrn.split()[3], scr)); ph.alpha_composite(scrn)
        put(im, ph, W / 2, 1050, 1, k_)
        if seen_at <= t < nothing_at:
            k = (t - seen_at) / 0.3; put(im, sst, W / 2 + 190, 1010, clamp(k / 0.15), 2.0 - 1.0 * eo(k), -10)
            if k < 0.5: sh = 14 * (1 - k / 0.5)
        if t >= nothing_at:
            k = (t - nothing_at) / 0.3
            o = Image.new("RGBA", (W, H), (0, 0, 0, int(150 * clamp(k)))); im.alpha_composite(o)  # dim the phone for the line
            put(im, n1, W / 2, 900, clamp(k / 0.3), 1.2 - 0.2 * eo(k)); put(im, n2, W / 2, 1060, clamp((k - 0.4) / 0.3), 1.5 - 0.5 * eo(k - 0.4))
            if 0.4 <= k < 0.9: sh = 12
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (seen_at, "hit", 0.9), (typing[0], "tick", 0.5), (typing[1], "glitch", 0.4)] + \
        [(days_from + i * 0.16, "tick", 0.5) for i in range(len(days))] + [(nothing_at, "whoosh", 0.5), (nothing_at + 0.12, "hit", 1.0)]


# ---------------------------------------------------------------- BODY: the group post flood
def scene_group_post(dur=4.8, flood=(1.0, 2.8), yours_at=0.35, bury_to=47, label_at=3.0):
    """a local community-group post 'Can anyone recommend a roofer?'; comments flood in, a counter races to 47,
    your reply (highlighted) is pushed down and out of sight, then 'YOU WERE 1 OF 47.' slams"""
    PW, PH = A.PW, A.PH; k_ = 0.64; body, scr = phone_shell(bg=(240, 242, 245), clock="19:42")
    post = sprite(PW - 80, 400, lambda d, s, im: (d.rounded_rectangle((0, 0, (PW - 80) * s - 1, 400 * s - 1), 30 * s, fill=WHITE),
                                                  d.text((30 * s, 24 * s), "Local Community Noticeboard", font=A.font("b", 30 * s), fill=(90, 96, 110)),
                                                  d.ellipse((30 * s, 80 * s, 110 * s, 160 * s), fill=(200, 160, 170)),
                                                  d.text((130 * s, 86 * s), "Aoife M.", font=A.font("b", 38 * s), fill=(20, 22, 28)),
                                                  d.text((130 * s, 130 * s), "2 hrs", font=A.font("m", 28 * s), fill=(130, 136, 146)),
                                                  d.text((30 * s, 200 * s), "Can anyone recommend a good", font=A.font("sb", 46 * s), fill=(20, 22, 28)),
                                                  d.text((30 * s, 260 * s), "roofer? Need a full re-roof.", font=A.font("sb", 46 * s), fill=(20, 22, 28))))
    rng = np.random.default_rng(11); cw = PW - 120
    def comment(i, you=False):
        nl = int(rng.integers(150, 300)); tl = int(rng.integers(260, 520))
        def fn(d, s, im):
            d.ellipse((0, 10 * s, 70 * s, 80 * s), fill=A.TH["accent"] if you else tuple(int(x) for x in rng.integers(120, 210, 3)))
            d.rounded_rectangle((90 * s, 0, cw * s, 120 * s), 28 * s, fill=(255, 240, 230) if you else (232, 234, 238), outline=A.TH["accent"] if you else None, width=5 * s)
            if you:
                d.text((116 * s, 16 * s), "You", font=A.font("bl", 34 * s), fill=(20, 22, 28)); d.text((116 * s, 62 * s), "Can do, PM me", font=A.font("m", 32 * s), fill=(40, 44, 52))
            else:
                d.rounded_rectangle((116 * s, 22 * s, (116 + nl) * s, 48 * s), 10 * s, fill=(190, 194, 202))
                d.rounded_rectangle((116 * s, 70 * s, (116 + tl) * s, 92 * s), 10 * s, fill=(208, 212, 218))
        return sprite(cw, 120, fn)
    YOU_I = 0; comments = [comment(i, i == YOU_I) for i in range(26)]
    tag = shadowed(pill("YOU", 34, A.TH["accent"], WHITE, w="bl"), blur=12, dy=6, alpha=120, pad=20)
    big1 = text("YOU WERE", "bl", 120); big2 = text("1 OF 47.", "bl", 200, grad=(A.TH["accent"], A.TH["accent2"], 0))

    def fn(t):
        im = A.bg(); sh = 0
        n = (1 if t >= yours_at else 0) + (int(clamp((t - flood[0]) / (flood[1] - flood[0])) ** 1.6 * (len(comments) - 1)) if t >= flood[0] else 0)
        cnt = (1 if t >= yours_at else 0) + int(round((bury_to - 1) * clamp((t - flood[0]) / (flood[1] - flood[0])) ** 1.3))
        put(im, text("THEY ASKED A", "bl", 88), W / 2, 300, eo(t / 0.25)); put(im, text("LOCAL GROUP.", "bl", 88, A.TH["accent"]), W / 2, 395, eo((t - 0.1) / 0.25))
        ph = body.copy(); scrn = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(scrn)
        scroll = max(0, (n - 4) * 135)
        put(scrn, post, PW / 2, 190 + 200 - min(scroll, 260), 1)
        d.text((60, 620 - min(scroll, 260)), f"{cnt} comments", font=A.font("b", 36), fill=(90, 96, 110))
        you_y = None
        for i in range(n):
            y = 720 + i * 135 - scroll + 0 * 1
            if -150 < y < PH + 150: put(scrn, comments[i], PW / 2 + 20, y, 1, 0.9 + 0.1 * spring((t - flood[0] - i * 0.08) / 0.2))
            if i == YOU_I: you_y = y
        scrn.putalpha(ImageChops.multiply(scrn.split()[3], scr)); ph.alpha_composite(scrn)
        cy = 1060; put(im, ph, W / 2, cy, 1, k_)
        if you_y is not None and you_y > 120:  # tag your comment while it is still visible
            put(im, tag, W / 2 - PW * k_ / 2 - 20, cy - PH * k_ / 2 + you_y * k_, 1, 1 + 0.25 * (1 - eo((t - yours_at) / 0.3)))
        if t >= label_at:
            k = (t - label_at) / 0.3
            o = Image.new("RGBA", (W, H), (0, 0, 0, int(170 * clamp(k)))); im.alpha_composite(o)
            put(im, big1, W / 2, 860, clamp(k / 0.3), 1.2 - 0.2 * eo(k)); put(im, big2, W / 2, 1060, clamp((k - 0.3) / 0.3), 1.6 - 0.6 * eo(k - 0.3))
            if 0.3 <= k < 0.8: sh = 14
        return im, sh
    ev = [(0.0, "whoosh", 0.5)] + [(flood[0] + i * (flood[1] - flood[0]) / 18, "pop", 0.35) for i in range(18)] + [(yours_at, "ping", 0.6), (label_at, "whoosh", 0.4), (label_at + 0.12, "hit", 1.0)]
    return dur, fn, ev
