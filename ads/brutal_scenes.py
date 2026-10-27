"""Brutalist poster scenes for the clothing 'Boosting isn't advertising' Reel: flat yellow, black, white, one red.
Heavy uppercase type, thick borders, hard offset shadows (no blur), snappy cuts, motion-blurred slides, sticker
slaps. Sells Meta ads first; email shows up only as the add-on."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, WHITE, clamp, put, ring
import motion as M
from motion import ftext, expo_out, quint_out, cubic_io, back_out, hard_shadow

YEL, INK, RED, GREY = (255, 214, 0), (12, 12, 12), (255, 59, 48), (150, 140, 90)
_BG = {}
def yellow(col=YEL):
    if col not in _BG: _BG[col] = M.flat_bg(col, grain=1.4)
    return _BG[col].copy()

def block(label, sub=None, w=920, fill=WHITE, ink=INK, size=64, sub_size=30, pad=34, num=None):
    """a thick-bordered box with a heavy label (and optional mono sub-line), hard shadow"""
    fl = M.ffont("bl", size * 2); fs = M.ffont("mono", sub_size * 2); h = pad * 2 + size + (sub_size + 18 if sub else 0)
    def dr(d, s, im):
        d.rectangle((0, 0, w * s - 1, h * s - 1), fill=fill); d.rectangle((0, 0, w * s - 1, h * s - 1), outline=INK, width=7 * s)
        x = pad * s
        if num:
            d.rectangle((x, pad * s, x + (size + 10) * s, (pad + size + 10) * s), fill=INK); f = M.ffont("mono-b", size * s)
            tw = d.textlength(num, font=f); d.text((x + ((size + 10) * s - tw) / 2, (pad - 4) * s), num, font=f, fill=YEL); x += (size + 40) * s
        d.text((x, (pad - 6) * s), label, font=M.ffont("bl", size * s), fill=ink)
        if sub: d.text((x, (pad + size + 14) * s), sub, font=M.ffont("mono", sub_size * s), fill=ink if fill != INK else (210, 200, 150))
    return hard_shadow(A.sprite(w, h, dr), 14, 14, INK)

def sticker(txt, fill=RED, ink=WHITE, size=70, rot=-8):
    f = M.ffont("bl", size * 2); tw = int(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(txt, font=f) / 2)
    w, h = tw + 70, size + 50
    sp = A.sprite(w, h, lambda d, s, im: (d.rectangle((0, 0, w * s - 1, h * s - 1), fill=fill), d.rectangle((0, 0, w * s - 1, h * s - 1), outline=INK, width=6 * s),
                                           d.text((35 * s, 14 * s), txt, font=M.ffont("bl", size * s), fill=ink)))
    return hard_shadow(sp, 10, 10, INK).rotate(rot, resample=Image.BICUBIC, expand=True)

def slap(im, sp, x, y, t, t0, dur=0.22):
    """sticker slap: drops from 1.6x scale to 1.0 with a tiny overshoot"""
    k = (t - t0) / dur
    if k > 0: put(im, sp, x, y, clamp(k / 0.25), 1 + 0.6 * (1 - quint_out(k)) - 0.04 * math.sin(clamp(k) * math.pi))


# ======================================================================= 1. hook: one word per beat, then the stack
def scene_hook(words=("BOOSTING", "POSTS", "ISN'T", "RUNNING", "ADS."), beat=0.3, start=0.25, stack_at=None, sorry_at=None, dur=3.8,
               callout="CLOTHING BRANDS ↓"):
    """each word fills the screen for one beat (hard cut, inverted every other word), then all of them fly into a
    tight stack with motion blur and a red SORRY sticker slaps on"""
    stack_at = stack_at or start + beat * len(words); sorry_at = sorry_at or stack_at + 0.55
    big = []
    for i, w_ in enumerate(words):
        sz = 400
        while sz > 60 and M.ffont("bl", sz).getlength(w_) > 980: sz -= 10
        big.append((ftext(w_, "bl", sz, INK), ftext(w_, "bl", sz, YEL)))
    small = []
    for w_ in words:
        sz = 230
        while sz > 60 and M.ffont("bl", sz).getlength(w_) > 940: sz -= 6
        small.append(ftext(w_, "bl", sz, INK))
    ys = []; y = 560
    for sp in small: ys.append(y + sp.height / 2); y += sp.height * 0.86
    CO = hard_shadow(block(callout, w=560, size=44, pad=20, fill=INK, ink=YEL), 0, 0); SO = sticker("SORRY.", size=96, rot=-9)
    def fn(t):
        i = int((t - start) // beat) if start <= t < stack_at else -1
        if 0 <= i < len(words):
            inv = i % 2 == 1; im = yellow(INK if inv else YEL); put(im, big[i][1 if inv else 0], W / 2, H / 2 - 40)
            put(im, CO, W / 2, 330, 1); return im, 0
        im = yellow()
        if t < start: put(im, CO, W / 2, 330, clamp(t / 0.1), 1 + 0.3 * (1 - quint_out(t / 0.2))); return im, 0
        put(im, CO, W / 2, 330)
        for j, sp in enumerate(small):
            p = (t - stack_at - j * 0.05) / 0.35
            M.slide_put(im, sp, W / 2 + (900 if j % 2 else -900), ys[j], W / 2, ys[j], p, expo_out)
        slap(im, SO, W / 2 + 230, ys[-1] + 210, t, sorry_at)
        return im, 0
    ev = [(0.0, "hit", 0.6)] + [(start + i * beat, "hit", 1.0 if i in (0, len(words) - 1) else 0.75) for i in range(len(words))] + \
         [(stack_at + j * 0.05, "swish", 0.35) for j in range(len(words))] + [(sorry_at, "pop", 1.0), (sorry_at + 0.02, "hit", 0.6)]
    return dur, fn, ev


# ======================================================================= 2. the boost button gets crossed out
def scene_boost(dur=4.2, tap_at=0.9, x_at=1.7, l_at=2.5, lines=("MORE LIKES", "≠ MORE SALES.")):
    """a chunky 'Boost post' button springs in, a cursor presses it, then two thick black marker strokes cross it out
    and the line lands"""
    bw, bh = 780, 200
    def btn(pressed):
        def dr(d, s, im):
            d.rectangle((0, 0, bw * s - 1, bh * s - 1), fill=(60, 120, 255) if not pressed else (40, 90, 210)); d.rectangle((0, 0, bw * s - 1, bh * s - 1), outline=INK, width=8 * s)
            f = M.ffont("bl", 84 * s); tw = d.textlength("Boost post", font=f); d.text(((bw * s - tw) / 2, 50 * s), "Boost post", font=f, fill=WHITE)
        return A.sprite(bw, bh, dr)
    B0, B1 = hard_shadow(btn(False), 16, 16), hard_shadow(btn(True), 6, 6)
    T = ftext("WHAT MOST BRANDS DO:", "mono-b", 46, INK); L1, L2 = ftext(lines[0], "bl", 120, INK), ftext(lines[1], "bl", 120, RED)
    EX = ftext("€50 · 2 days · 140 likes · 0 sales", "mono", 34, INK); ex2 = ftext("(example)", "mono", 26, GREY)
    def fn(t):
        im = yellow(); M.reveal_lr(im, T, W / 2, 400, (t - 0.05) / 0.35)
        pressed = tap_at <= t < tap_at + 0.14; k = back_out((t - 0.2) / 0.45)
        put(im, B1 if pressed else B0, W / 2 + (10 if pressed else 0), 760 + (10 if pressed else 0), clamp((t - 0.2) / 0.1), 0.6 + 0.4 * k)
        if t < tap_at + 0.5: A.tap(im, W / 2 + 200, 790, t, tap_at, t_in=0.55, from_dx=220, from_dy=420)
        d = ImageDraw.Draw(im)
        for j, (a, b) in enumerate((((W / 2 - 430, 640), (W / 2 + 430, 880)), ((W / 2 + 430, 640), (W / 2 - 430, 880)))):
            p = cubic_io((t - x_at - j * 0.18) / 0.22)
            if p > 0: d.line((a[0], a[1], a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p), fill=RED, width=20)
        M.reveal_lr(im, EX, W / 2, 990, (t - tap_at - 0.25) / 0.5); put(im, ex2, W / 2, 1040, clamp((t - tap_at - 0.6) / 0.2))
        if t >= l_at:
            M.slide_put(im, L1, -700, 1260, W / 2, 1260, (t - l_at) / 0.35, expo_out); M.slide_put(im, L2, W + 700, 1400, W / 2, 1400, (t - l_at - 0.12) / 0.35, expo_out)
        return im, (12 * (1 - (t - x_at) / 0.15) if x_at <= t < x_at + 0.15 else 0)
    ev = [(0.05, "click", 0.5), (0.2, "pop", 0.8), (tap_at, "click", 1.0), (tap_at + 0.3, "tick", 0.4), (x_at, "swish", 0.8), (x_at + 0.18, "swish", 0.8), (x_at + 0.05, "hit", 0.9),
          (l_at, "whoosh", 0.6), (l_at + 0.12, "hit", 0.8)]
    return dur, fn, ev


# ======================================================================= 3. what running ads actually is
def scene_system(dur=5.0, title="WHAT WE RUN INSTEAD:", rows=(("FIND NEW BUYERS", "people like your best customers"), ("BRING BACK BROWSERS", "they looked at the hoodie. remind them."),
                 ("TEST, THEN SCALE", "5 ads in, the winner gets the budget")), at=(0.5, 1.2, 1.9)):
    """three bordered blocks slam in from alternating sides with motion blur and hard shadows; each lands with a
    1-frame white flash and a hit"""
    T = ftext(title, "mono-b", 50, INK); BL = [block(a, b, num=f"{i + 1}", size=60) for i, (a, b) in enumerate(rows)]
    ys = [700, 1000, 1300]
    def fn(t):
        im = yellow(); M.reveal_lr(im, T, W / 2, 420, (t - 0.05) / 0.4); sh = 0
        for i, sp in enumerate(BL):
            p = (t - at[i]) / 0.32; x0 = -700 if i % 2 == 0 else W + 700
            M.slide_put(im, sp, x0, ys[i], W / 2, ys[i], p, expo_out)
            if 0.32 <= t - at[i] < 0.42: sh = 9
        return im, sh
    ev = [(0.05, "click", 0.5)] + [(a, "whoosh", 0.6) for a in at] + [(a + 0.3, "hit", 0.85) for a in at]
    return dur, fn, ev


# ======================================================================= 4. the creative test: a bar race
def scene_race(dur=5.0, ads=(("A", "tee", (40, 40, 40)), ("B", "hoodie", (200, 60, 50)), ("C", "jeans", (40, 70, 130)), ("D", "tee", (90, 120, 80)), ("E", "hoodie", (120, 90, 160))),
               scores=(0.38, 1.0, 0.52, 0.27, 0.44), race=(0.6, 3.0), win_at=3.2, head="5 ADS. 1 WINNER.", label="sales from each ad (example)"):
    """five ad tiles on the left, black bars race to the right with a ticking count; when the race ends the losers
    grey out with OFF and the winner gets a red 'BUDGET →' sticker"""
    from ecom3_scenes import garment
    def tile(letter, kind, col, grey=False):
        def dr(d, s, im):
            d.rectangle((0, 0, 150 * s - 1, 150 * s - 1), fill=(236, 230, 214) if not grey else (205, 200, 180)); d.rectangle((0, 0, 150 * s - 1, 150 * s - 1), outline=INK, width=6 * s)
            garment(d, s, 75 * s, 82 * s, kind, col if not grey else (150, 146, 130), (236, 230, 214) if not grey else (205, 200, 180))
            d.rectangle((0, 0, 44 * s, 44 * s), fill=INK); d.text((11 * s, 2 * s), letter, font=M.ffont("mono-b", 34 * s), fill=YEL)
        return A.sprite(150, 150, dr)
    TL = [tile(*a) for a in ads]; TG = [tile(*a, grey=True) for a in ads]
    HD = ftext(head, "bl", 104, INK); LB = ftext(label, "mono", 28, INK)
    OFF = sticker("OFF", fill=INK, ink=WHITE, size=40, rot=6); WIN = sticker("BUDGET →", size=52, rot=-5)
    X0, X1, Y0, RH = 230, 990, 560, 200; win = max(range(len(scores)), key=lambda i: scores[i])
    def fn(t):
        im = yellow(); d = ImageDraw.Draw(im); sh = 0
        M.words_rise(im, [HD], W / 2, 360, t, 0.0, dur=0.35); M.reveal_lr(im, LB, W / 2, 460, (t - 0.3) / 0.4)
        p = cubic_io((t - race[0]) / (race[1] - race[0])); done = t >= win_at
        for i, sc in enumerate(scores):
            y = Y0 + i * RH + 75; k = quint_out((t - 0.15 - i * 0.07) / 0.35)
            if k <= 0: continue
            grey = done and i != win
            put(im, (TG if grey else TL)[i], 140 - 60 * (1 - k), y, clamp(k / 0.3))
            bw = (X1 - X0) * sc * p
            if bw > 2:
                col = (120, 112, 70) if grey else (RED if i == win and done else INK)
                d.rectangle((X0, y - 34, X0 + bw, y + 34), fill=col)
                n = int(round(sc * 46 * p)); nt = ftext(str(n), "mono-b", 40, INK if bw < 120 else YEL)
                put(im, nt, X0 + max(bw - 50, 50) if bw >= 120 else X0 + bw + 50, y)
            if grey: put(im, OFF, X0 + bw + 120, y, clamp((t - win_at - i * 0.05) / 0.1), 1 + 0.4 * (1 - quint_out((t - win_at - i * 0.05) / 0.2)))
        if done:
            y = Y0 + win * RH + 75; slap(im, WIN, X0 + 260, y, t, win_at + 0.35)
            if win_at + 0.35 <= t < win_at + 0.47: sh = 10
        return im, sh
    ev = [(0.0, "hit", 0.7), (0.3, "click", 0.4)] + [(race[0] + i * 0.2, "tick", 0.25) for i in range(int((race[1] - race[0]) / 0.2))] + \
         [(win_at + i * 0.05, "click", 0.5) for i in range(4)] + [(win_at + 0.35, "hit", 1.0), (win_at + 0.4, "coin", 0.8)]
    return dur, fn, ev


# ======================================================================= 5. the deal, inverted poster
def scene_deal(dur=5.0, rows=(("WE RUN YOUR META ADS.", YEL), ("NO RETAINER.", WHITE), ("YOU PAY PER NEW", WHITE), ("SUBSCRIBER WE BRING IN.", WHITE),
                              ("AD SPEND: YOUR ACCOUNT.", YEL)), at=(0.45, 0.85, 1.25, 1.4, 1.85), addon="+ EMAIL FLOWS: OPTIONAL ADD-ON", addon_at=2.5,
               stamp="PAY PER RESULT", stamp_at=3.0):
    """black poster: THE DEAL header, each line cuts in with a 2-frame yellow bar wipe ahead of it, the add-on line
    types in mono, then a big red PAY PER RESULT sticker slaps across"""
    HD = ftext("THE DEAL", "bl", 150, YEL)
    RS = []
    for s_, c in rows:
        sz = 92
        while sz > 40 and M.ffont("bl", sz).getlength(s_) > 960: sz -= 4
        RS.append(ftext(s_, "bl", sz, c))
    AD = ftext(addon, "mono-b", 34, (210, 200, 150)); ST = sticker(stamp, size=92, rot=-7)
    ys = [640, 790, 920, 1030, 1180]
    def fn(t):
        im = yellow(INK); d = ImageDraw.Draw(im); sh = 0
        k = (t - 0.05) / 0.3; put(im, HD, W / 2, 420, clamp(k / 0.2), 1 + 0.25 * (1 - quint_out(k)))
        for i, sp in enumerate(RS):
            p = (t - at[i]) / 0.18
            if p <= 0: continue
            if p < 1:   # a yellow bar wipes across, revealing the line behind it
                xr = 60 + (W - 120) * quint_out(p); d.rectangle((60, ys[i] - sp.height / 2 + 6, xr, ys[i] + sp.height / 2 - 6), fill=YEL)
                M.reveal_lr(im, sp, W / 2, ys[i], quint_out(p) * 0.9)
            else: put(im, sp, W / 2, ys[i])
        n = int(clamp((t - addon_at) / 0.6) * len(addon));
        if n: M.reveal_lr(im, AD, W / 2, 1330, n / len(addon))
        slap(im, ST, W / 2, 1520, t, stamp_at, dur=0.25)
        if stamp_at + 0.2 <= t < stamp_at + 0.32: sh = 12
        return im, sh
    ev = [(0.05, "hit", 0.9)] + [(a, "swish", 0.55) for a in at] + [(addon_at + i * 0.08, "tick", 0.25) for i in range(7)] + [(stamp_at, "pop", 1.0), (stamp_at + 0.2, "hit", 0.9)]
    return dur, fn, ev


# ======================================================================= 6. CTA: comment ADS, with a ticker tape
def scene_cta(dur=4.2, kw="ADS", l1="WANT US TO", l2="RUN YOURS?", type_at=1.3, toast_at=2.3, ticker="SOUTHLINE AGENCY • META ADS FOR CLOTHING BRANDS • "):
    """big two-line ask, COMMENT + keyword box with hard shadow, a mono comment field types it and posts, a toast
    pops, and a black ticker tape scrolls along the bottom the whole time"""
    L1, L2 = ftext(l1, "bl", 130, INK), ftext(l2, "bl", 130, INK)
    CM = ftext("COMMENT", "bl", 110, INK); KB = block(kw, w=int(M.ffont("bl", 110).getlength(kw)) + 90, size=110, pad=22, fill=RED, ink=WHITE)
    TS = block("✓ WE'LL DM YOU HOW IT WORKS", w=760, size=38, pad=24, fill=WHITE)
    TK = ftext(ticker * 4, "mono-b", 40, YEL); period = M.ffont("mono-b", 80).getlength(ticker) / 2; fw, fh = 900, 120
    def field(typed, caret, posted):
        def dr(d, s, im):
            d.rectangle((0, 0, fw * s - 1, fh * s - 1), fill=WHITE); d.rectangle((0, 0, fw * s - 1, fh * s - 1), outline=INK, width=6 * s)
            f = M.ffont("mono-b", 44 * s); d.text((36 * s, 30 * s), typed or ("Add a comment…" if not posted else ""), font=f if typed else M.ffont("mono", 40 * s), fill=INK if typed else GREY)
            if caret: x = 36 * s + d.textlength(typed, font=f); d.rectangle((x + 4 * s, 28 * s, x + 10 * s, 92 * s), fill=INK)
            d.rectangle(((fw - 190) * s, 18 * s, (fw - 18) * s, (fh - 18) * s), fill=INK); f2 = M.ffont("bl", 36 * s); d.text(((fw - 166) * s, 36 * s), "POST", font=f2, fill=YEL)
        return hard_shadow(A.sprite(fw, fh, dr), 10, 10)
    cache = {}
    def F(*k):
        if k not in cache: cache[k] = field(*k)
        return cache[k]
    PT = type_at + len(kw) * 0.12 + 0.25
    def fn(t):
        im = yellow(); sh = 0
        M.slide_put(im, L1, -800, 380, W / 2, 380, t / 0.35, expo_out); M.slide_put(im, L2, W + 800, 510, W / 2, 510, (t - 0.1) / 0.35, expo_out)
        k = (t - 0.6) / 0.3; tot = CM.width + 30 + KB.width
        if k > 0:
            put(im, CM, W / 2 - tot / 2 + CM.width / 2, 760, clamp(k / 0.3)); put(im, KB, W / 2 + tot / 2 - KB.width / 2, 760, clamp(k / 0.3), 1 + 0.5 * (1 - quint_out((t - 0.75) / 0.25)))
            if 0.75 <= t < 0.87: sh = 10
        n = int(clamp((t - type_at) / (len(kw) * 0.12)) * len(kw)); posted = t >= PT
        put(im, F("" if posted else kw[:n], (not posted) and int(t * 3) % 2 == 0, posted), W / 2, 1040, clamp((t - 0.9) / 0.2), 1 - 0.03 * (1 - clamp(abs(t - PT) / 0.08)))
        if t >= toast_at: put(im, TS, W / 2, 1230, clamp((t - toast_at) / 0.12), 0.8 + 0.2 * back_out((t - toast_at) / 0.3))
        d = ImageDraw.Draw(im); d.rectangle((0, 1440, W, 1540), fill=INK); off = 8 + (t * 260) % period
        im.alpha_composite(TK.crop((int(off), 0, int(off) + W, TK.height)), (0, int(1490 - TK.height / 2)))
        return im, sh
    ev = [(0.0, "whoosh", 0.5), (0.1, "whoosh", 0.4), (0.75, "hit", 1.0)] + [(type_at + i * 0.12, "tick", 0.6) for i in range(len(kw))] + [(PT, "click", 1.0), (toast_at, "pop", 0.8), (toast_at + 0.05, "ping", 0.5)]
    return dur, fn, ev
