"""UI-native scenes for the clothing-brand 'Black Friday build' Reel: everything looks like a phone screen (a note
being typed, an inbox filling up, a flow builder, a receipt printing, a chat). Light theme, flat, no gradients.
Research basis: native / screen-looking creative beats polished motion graphics on Meta in 2026, and the live agency
ads in the Ad Library lead with a direct callout, a Black Friday build offer and risk reversal."""
import math
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, WHITE, GREEN, clamp, eo, eio, back, spring, put, put_rise, ring, pill, text, sprite, font, tsize

INK, MUTED, LINE, PAPER = (20, 22, 28), (120, 126, 140), (226, 228, 234), (255, 255, 255)
BLUE, RED, GREY_BUBBLE = (0, 110, 255), (255, 59, 48), (233, 234, 239)


def wrap(s, f, maxw):
    """greedy word wrap for a PIL font"""
    out, cur = [], ""
    for w_ in s.split():
        t = (cur + " " + w_).strip()
        if tsize(t, f)[0] > maxw and cur: out.append(cur); cur = w_
        else: cur = t
    return out + ([cur] if cur else [])


def statusbar(d, s, w, y=0, clock="9:41"):
    d.text((36 * s, (y + 18) * s), clock, font=font("sb", 30 * s), fill=INK)
    d.rounded_rectangle(((w - 86) * s, (y + 22) * s, (w - 40) * s, (y + 44) * s), 6 * s, outline=INK, width=2 * s); d.rounded_rectangle(((w - 83) * s, (y + 25) * s, (w - 50) * s, (y + 41) * s), 4 * s, fill=INK)


def phone_frame(w=960, h=1500):
    """flat white 'screen' with a status bar; everything else is drawn on top per frame"""
    def dr(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 56 * s, fill=PAPER); statusbar(d, s, w)
    return A.shadowed(sprite(w, h, dr), blur=40, dy=24, alpha=50, pad=70)


# ======================================================================= 1. the note being typed
def scene_note(lines=(("Clothing brands,", "bl", 92, INK), ("your Black Friday emails", "sb", 68, INK), ("aren't built yet,", "sb", 68, INK), ("are they?", "bl", 92, RED)),
               dur=3.8, start=0.35, cps=22, title="Notes", sub_at=None):
    """a Notes-app page: the hook types itself out with a blinking caret and key ticks. cps = characters per second"""
    frame = phone_frame(); total = sum(len(l[0]) for l in lines)
    ends = []; acc = 0
    for l in lines: acc += len(l[0]); ends.append(acc)
    def fn(t):
        im = A.bg(); put(im, frame, W / 2, 960 + 80 * (1 - eo(t / 0.5)), clamp(t / 0.25)); d = ImageDraw.Draw(im)
        x0, y0 = (W - 960) / 2, 960 - 750
        d.text((x0 + 48, y0 + 90), title, font=font("b", 40), fill=MUTED); d.text((x0 + 48, y0 + 140), "Today", font=font("m", 28), fill=MUTED)
        n = int(max(0, t - start) * cps); y = y0 + 260; shown = 0
        for i, (s_, w_, sz, col) in enumerate(lines):
            f = font(w_, sz); k = clamp(n - (ends[i] - len(s_)), 0, len(s_)); seg = s_[:int(k)]
            if seg: d.text((x0 + 48, y), seg, font=f, fill=col)
            if 0 < k < len(s_) or (k == len(s_) and i == len(lines) - 1 and n >= total) or (k == len(s_) and i < len(lines) - 1 and n == ends[i]):
                if int(t * 2.5) % 2 == 0 or k < len(s_):
                    cx = x0 + 48 + tsize(seg, f)[0] + 6 if seg else x0 + 48; d.rectangle((cx, y + 4, cx + 5, y + sz * 1.05), fill=BLUE)
            if k > 0: y += int(sz * 1.3)
            if k < len(s_): break
        return im, 0
    ev = [(0.0, "whoosh", 0.4)] + [(start + i / cps, "tick", 0.18) for i in range(0, total, 2)]
    return dur, fn, ev


# ======================================================================= 2. their inbox on Black Friday
def scene_inbox(rows=(("N", "Nova Apparel", "BLACK FRIDAY: 40% off everything", "9:02", (255, 149, 0)), ("H", "Hollow Studio", "Early access starts now", "9:07", (88, 86, 214)),
                      ("F", "Form & Thread", "Free shipping all weekend", "9:11", (52, 199, 89)), ("K", "Kinfolk Wear", "Your size is back in stock", "9:15", (0, 122, 255)),
                      ("A", "Arlo Basics", "Last chance: ends midnight", "9:20", (175, 82, 222))),
                title="Their inbox, Black Friday morning:", you="Your brand", you_sub="No email sent", line="Everyone shows up but you.",
                dur=4.4, at=(0.5, 0.9, 1.3, 1.7, 2.1), you_at=2.7, line_at=3.3):
    """an inbox fills from the top: competitor emails drop in one after another, pushing the list down. Then a greyed,
    dashed 'Your brand · No email sent' row pops in with a shake and the line lands."""
    frame = phone_frame(); RH = 150
    def row(ini, sender, subj, when, col, ghost=False):
        def dr(d, s, im):
            if ghost:
                d.rounded_rectangle((20 * s, 10 * s, 880 * s, 140 * s), 24 * s, outline=(200, 204, 214), width=3 * s)
                d.ellipse((44 * s, 35 * s, 124 * s, 115 * s), outline=(200, 204, 214), width=3 * s); d.text((70 * s, 52 * s), "?", font=font("b", 40 * s), fill=(200, 204, 214))
                d.text((150 * s, 36 * s), sender, font=font("b", 36 * s), fill=(160, 166, 180)); d.text((150 * s, 84 * s), subj, font=font("m", 32 * s), fill=RED)
            else:
                d.ellipse((44 * s, 35 * s, 124 * s, 115 * s), fill=col); f = font("b", 40 * s); tw, th, ox, oy = tsize(ini, f); d.text((84 * s - tw / 2 - ox, 75 * s - th / 2 - oy), ini, font=f, fill=WHITE)
                d.text((150 * s, 36 * s), sender, font=font("b", 36 * s), fill=INK); d.text((150 * s, 84 * s), subj, font=font("m", 32 * s), fill=MUTED)
                f2 = font("m", 26 * s); d.text((870 * s - f2.getlength(when), 40 * s), when, font=f2, fill=MUTED)
                d.line((150 * s, 148 * s, 880 * s, 148 * s), fill=LINE, width=2 * s)
        return sprite(900, RH, dr)
    sps = [row(*r) for r in rows]; ghost = row("?", you, you_sub, "", None, ghost=True)
    tsp = text(title, "xb", A.fit_size(title, "xb", 60, 900)); ln = text(line, "bl", A.fit_size(line, "bl", 84, 960), RED)
    def fn(t):
        im = A.bg(); put(im, frame, W / 2, 960, 1); sh = 0
        put_rise(im, tsp, W / 2, 330, eo(t / 0.35))
        top = 960 - 750 + 230; arrived = [i for i, a in enumerate(at) if t >= a]
        for rank, i in enumerate(reversed(arrived)):
            if rank == 0: k = (t - at[i]) / 0.4; y = top - 90 * (1 - spring(k)); al = clamp(k / 0.15)
            else: nk = eo((t - at[arrived[-1]]) / 0.35); y = top + (rank - 1) * RH + RH * nk; al = 1
            put(im, sps[i], W / 2, y + RH / 2, al)
        if t >= you_at:
            k = (t - you_at) / 0.4; y = top + len(rows) * RH + 20
            put(im, ghost, W / 2 + (8 * math.sin(t * 80) if k < 0.3 else 0), y + RH / 2, clamp(k / 0.15), 0.9 + 0.1 * spring(k))
            if you_at <= t < you_at + 0.14: sh = 8
        put_rise(im, ln, W / 2, 1470, eo((t - line_at) / 0.35))
        return im, sh
    ev = [(0.0, "whoosh", 0.4)] + [(a, "ping", 0.45) for a in at] + [(you_at, "glitch", 0.6), (you_at, "hit", 0.7), (line_at, "whoosh", 0.5)]
    return dur, fn, ev


# ======================================================================= 3. the flow builder
def scene_flow(nodes=(("trigger", "Trigger: added to basket"), ("wait", "Wait 1 hour"), ("email", "Email 1 · Still thinking?"), ("wait", "Wait 1 day"),
                      ("email", "Email 2 · Your size is almost gone"), ("wait", "Wait 2 days"), ("email", "Email 3 · Free shipping ends tonight")),
               title="We build this for you:", live="Flow live", dur=5.0, start=0.6, gap=0.42):
    """a flow-builder canvas: nodes drop in one after another down a connector that draws itself, then a toggle flips to
    'Flow live' in green. The thing we actually sell, shown being built."""
    frame = phone_frame()
    def node(kind, label):
        h = 60 if kind == "wait" else 110; w_ = 640 if kind == "wait" else 820
        def dr(d, s, im):
            if kind == "wait":
                d.rounded_rectangle((0, 0, w_ * s - 1, h * s - 1), 30 * s, fill=(240, 242, 247)); f = font("m", 28 * s); tw, th, ox, oy = tsize(label, f)
                d.text((w_ * s / 2 - tw / 2 - ox, h * s / 2 - th / 2 - oy), label, font=f, fill=MUTED)
            else:
                col = BLUE if kind == "email" else (255, 149, 0)
                d.rounded_rectangle((0, 0, w_ * s - 1, h * s - 1), 26 * s, fill=PAPER, outline=LINE, width=3 * s)
                d.rounded_rectangle((26 * s, 27 * s, 82 * s, 83 * s), 16 * s, fill=col)
                if kind == "email": d.rectangle((38 * s, 44 * s, 70 * s, 68 * s), fill=WHITE); d.line((38 * s, 44 * s, 54 * s, 58 * s, 70 * s, 44 * s), fill=col, width=3 * s)
                else: d.polygon([(58 * s, 38 * s), (44 * s, 58 * s), (56 * s, 58 * s), (50 * s, 74 * s), (66 * s, 52 * s), (54 * s, 52 * s)], fill=WHITE)
                f = font("b", 34 * s); d.text((110 * s, h * s / 2 - 20 * s), label, font=f, fill=INK)
        sp = sprite(w_, h, dr); return A.shadowed(sp, blur=18, dy=8, alpha=35, pad=30) if kind != "wait" else sp
    sps = [node(k, l) for k, l in nodes]; ys = []; y = 960 - 750 + 250
    for k, _ in nodes: h = 60 if k == "wait" else 110; ys.append(y + h / 2); y += h + 34
    AT = [start + i * gap for i in range(len(nodes))]; tsp = text(title, "xb", A.fit_size(title, "xb", 60, 900))
    tog_off = pill("Draft", 34, (200, 204, 214), WHITE, w="b"); tog_on = pill(live, 34, GREEN, WHITE, w="b")
    def fn(t):
        im = A.bg(); put(im, frame, W / 2, 960, 1); d = ImageDraw.Draw(im); put_rise(im, tsp, W / 2, 330, eo(t / 0.35))
        landed = [i for i, a in enumerate(AT) if t >= a]
        if landed:
            n = landed[-1]; lp = eo((t - AT[n]) / 0.35); y_end = ys[n - 1] + (ys[n] - ys[n - 1]) * lp if n > 0 else ys[0]
            d.line((W / 2, ys[0], W / 2, y_end), fill=(200, 204, 214), width=5)
        for i in landed:
            k = (t - AT[i]) / 0.45; put(im, sps[i], W / 2, ys[i] - 40 * (1 - eo(k)), clamp(k / 0.25), 0.9 + 0.1 * spring(k))
        done = t >= AT[-1] + 0.6; k2 = (t - AT[-1] - 0.6) / 0.35
        put(im, tog_on if done else tog_off, W / 2, 1500, eo((t - 0.3) / 0.3), (1 + 0.15 * (1 - eo(k2))) if done else 1)
        if done: ring(im, W / 2, 1500, k2 / 1.4, col=GREEN, maxr=260, width=4, r0=60)
        return im, 0
    ev = [(0.0, "whoosh", 0.4)] + [(a, "pop", 0.5) for a in AT] + [(AT[-1] + 0.6, "coin", 0.8), (AT[-1] + 0.65, "shimmer", 0.5)]
    return dur, fn, ev


# ======================================================================= 4. the offer card
def scene_offer_card(badge="BLACK FRIDAY BUILD", big="Live before Nov 27.", items=("Abandoned-basket flow", "Welcome flow", "Black Friday campaign emails", "Meta ads to grow the list"),
                     foot=("No retainer.", "Paid per new subscriber."), brand="Southline Agency", dur=4.0, at=(0.9, 1.2, 1.5, 1.8), foot_at=2.3):
    """a flat white offer card slides up; the ticks land one by one; the price line slams under them"""
    cw, ch = 920, 1000
    def dr(d, s, im):
        d.rounded_rectangle((0, 0, cw * s - 1, ch * s - 1), 48 * s, fill=PAPER)
        d.text((60 * s, 56 * s), brand, font=font("b", 30 * s), fill=MUTED)
        bw = font("bl", 30 * s).getlength(badge) + 60 * s; d.rounded_rectangle((60 * s, 110 * s, 60 * s + bw, 166 * s), 28 * s, fill=INK); d.text((90 * s, 121 * s), badge, font=font("bl", 30 * s), fill=WHITE)
        d.text((60 * s, 200 * s), big, font=font("bl", A.fit_size(big, "bl", 84, 800) * s), fill=INK)
        for i, it in enumerate(items): d.text((140 * s, (360 + i * 100) * s), it, font=font("sb", 42 * s), fill=INK)
    card = A.shadowed(sprite(cw, ch, dr), blur=40, dy=24, alpha=55, pad=70)
    ticks = [sprite(70, 70, lambda d, s, im: (d.ellipse((5 * s, 5 * s, 65 * s, 65 * s), fill=GREEN), d.line((22 * s, 36 * s, 31 * s, 46 * s, 49 * s, 26 * s), fill=WHITE, width=6 * s, joint="curve"))) for _ in items]
    f1, f2 = text(foot[0], "bl", 64, INK), text(foot[1], "bl", A.fit_size(foot[1], "bl", 64, 800), BLUE)
    def fn(t):
        im = A.bg(); k = spring(t / 0.8, f=1.6, d=6); cy = 960 + 1000 * (1 - k)
        put(im, A.shine(card, (t - 2.2) / 0.9) if t > 2.2 else card, W / 2, cy, clamp(t / 0.2)); x0, y0 = W / 2 - cw / 2, cy - ch / 2
        for i, tk in enumerate(ticks):
            k2 = (t - at[i]) / 0.35
            if k2 > 0: put(im, tk, x0 + 95, y0 + 390 + i * 100, clamp(k2 / 0.2), 0.5 + 0.5 * back(k2))
        put_rise(im, f1, x0 + 60 + f1.width / 2, y0 + 820, eo((t - foot_at) / 0.3)); put_rise(im, f2, x0 + 60 + f2.width / 2, y0 + 900, eo((t - foot_at - 0.2) / 0.3))
        return im, (8 * (1 - (t - foot_at - 0.2) / 0.14) if foot_at + 0.2 <= t < foot_at + 0.34 else 0)
    return dur, fn, [(0.0, "whoosh", 0.7), (0.3, "hit", 0.6)] + [(a, "tick", 0.6) for a in at] + [(foot_at, "whoosh", 0.4), (foot_at + 0.2, "hit", 0.9), (2.2, "shimmer", 0.5)]


# ======================================================================= 5. the receipt
def scene_receipt(lines=(("Setup fee", "€0"), ("Monthly retainer", "€0"), ("Ad spend", "your account"), ("Per new subscriber", "our fee"), ("Your email list", "yours, always")),
                  head="SOUTHLINE AGENCY", title="How you pay", stamp="NOTHING UPFRONT", dur=3.8, start=0.5, gap=0.42, stamp_at=3.0):
    """a till receipt prints downwards line by line (tick per line), zigzag edge, then a stamp slams on"""
    pw = 700; ph = 200 + len(lines) * 90 + 60
    def dr(d, s, im):
        d.rectangle((0, 0, pw * s - 1, (ph - 20) * s), fill=(252, 251, 247))
        for x in range(0, pw, 28): d.polygon([(x * s, (ph - 20) * s), ((x + 14) * s, ph * s), ((x + 28) * s, (ph - 20) * s)], fill=(252, 251, 247))
        f = font("b", 30 * s); tw = f.getlength(head); d.text((pw * s / 2 - tw / 2, 44 * s), head, font=f, fill=INK)
        f = font("m", 26 * s); tw = f.getlength(title); d.text((pw * s / 2 - tw / 2, 92 * s), title, font=f, fill=MUTED)
        d.line((40 * s, 150 * s, (pw - 40) * s, 150 * s), fill=(210, 208, 200), width=2 * s)
        for i, (a, b) in enumerate(lines):
            y = (190 + i * 90) * s; d.text((50 * s, y), a, font=font("m", 34 * s), fill=INK)
            f = font("b", 34 * s); tw = f.getlength(b); d.text(((pw - 50) * s - tw, y), b, font=f, fill=GREEN if b in ("€0", "yours, always") else INK)
            d.line((50 * s, y + 62 * s, (pw - 50) * s, y + 62 * s), fill=(230, 228, 220), width=2 * s)
    paper = A.shadowed(sprite(pw, ph, dr), blur=30, dy=18, alpha=50, pad=60)
    st = text(stamp, "bl", 70, RED); tsp = text("Nothing to lose. Nothing upfront.", "xb", A.fit_size("Nothing to lose. Nothing upfront.", "xb", 60, 960))
    def fn(t):
        im = A.bg(); d = ImageDraw.Draw(im)
        d.rounded_rectangle((W / 2 - 400, 430, W / 2 + 400, 520), 20, fill=(60, 62, 70))   # printer slot
        reveal = clamp((t - start) / (gap * len(lines) + 0.8)); hpx = int((paper.height - 120) * (0.22 + 0.78 * reveal)) + 60
        crop = paper.crop((0, 0, paper.width, min(paper.height, hpx)))
        im.alpha_composite(crop, (int(W / 2 - paper.width / 2), 480 - 60))
        d.rounded_rectangle((W / 2 - 400, 430, W / 2 + 400, 520), 20, fill=(60, 62, 70)); d.rectangle((W / 2 - 360, 470, W / 2 + 360, 478), fill=(30, 31, 36))
        if t >= stamp_at:
            k = (t - stamp_at) / 0.3; put(im, st, W / 2, 1300, clamp(k / 0.15), 1.6 - 0.6 * eo(k), -10)
        put_rise(im, tsp, W / 2, 1450, eo((t - stamp_at - 0.3) / 0.35))
        return im, (10 * (1 - (t - stamp_at) / 0.14) if stamp_at <= t < stamp_at + 0.14 else 0)
    ev = [(0.0, "click", 0.5)] + [(start + 0.3 + i * gap, "tick", 0.5) for i in range(len(lines))] + [(stamp_at, "hit", 1.0), (stamp_at + 0.3, "whoosh", 0.4)]
    return dur, fn, ev


# ======================================================================= 6. the chat CTA
def scene_chat(header="Ryan · Southline Agency", msgs=(("in", "Saw your Reel. Can you build ours before Black Friday?"), ("out", "Yep. DM me READY and I'll send the plan + price today.")),
               foot=("DM 'READY'", "or comment READY · link in bio"), dur=4.0, at=(0.5, 1.9), foot_at=3.0):
    """an iMessage-style thread: typing dots, then the bubble pops in; the reply from Ryan is the CTA"""
    frame = phone_frame()
    def bubble(kind, s_):
        f = font("m", 36); ls = wrap(s_, f, 600); bw = max(tsize(l, f)[0] for l in ls) + 64; bh = len(ls) * 46 + 40
        def dr(d, s, im):
            d.rounded_rectangle((0, 0, bw * s - 1, bh * s - 1), 34 * s, fill=BLUE if kind == "out" else GREY_BUBBLE)
            for i, l in enumerate(ls): d.text((32 * s, (20 + i * 46) * s), l, font=font("m", 36 * s), fill=WHITE if kind == "out" else INK)
        return sprite(bw, bh, dr)
    def dots(kind):
        def dr(d, s, im):
            d.rounded_rectangle((0, 0, 130 * s - 1, 70 * s - 1), 34 * s, fill=BLUE if kind == "out" else GREY_BUBBLE)
        return sprite(130, 70, dr)
    sps = [bubble(k, m) for k, m in msgs]; dt = {k: dots(k) for k in ("in", "out")}
    hd = text(header, "b", 34, INK); f1, f2 = text(foot[0], "bl", 96, INK), text(foot[1], "sb", 40, MUTED)
    def fn(t):
        im = A.bg(); put(im, frame, W / 2, 960, 1); d = ImageDraw.Draw(im); x0, y0 = (W - 960) / 2, 960 - 750
        d.ellipse((x0 + 420, y0 + 80, x0 + 540, y0 + 200), fill=(230, 232, 238)); d.text((x0 + 455, y0 + 105), "R", font=font("b", 56), fill=INK)
        put(im, hd, W / 2, y0 + 250); d.line((x0 + 40, y0 + 290, x0 + 920, y0 + 290), fill=LINE, width=2)
        y = y0 + 360
        for i, (kind, _) in enumerate(msgs):
            if t < at[i] - 0.6: break
            x = x0 + 60 if kind == "in" else x0 + 900
            if t < at[i]:   # typing dots
                dsp = dt[kind]; put(im, dsp, x + (dsp.width / 2 if kind == "in" else -dsp.width / 2), y + 35, clamp((t - at[i] + 0.6) / 0.2))
                for j in range(3): r = 8 + 4 * max(0, math.sin((t * 6 - j * 0.8))); cx = x + (30 + j * 35 if kind == "in" else -(30 + j * 35)); d.ellipse((cx - r, y + 35 - r, cx + r, y + 35 + r), fill=WHITE if kind == "out" else MUTED)
                break
            sp = sps[i]; k = (t - at[i]) / 0.4
            put(im, sp, x + (sp.width / 2 if kind == "in" else -sp.width / 2), y + sp.height / 2, clamp(k / 0.15), 0.7 + 0.3 * back(k)); y += sp.height + 30
        put_rise(im, f1, W / 2, 1420, eo((t - foot_at) / 0.3)); put_rise(im, f2, W / 2, 1510, eo((t - foot_at - 0.15) / 0.3))
        return im, (8 * (1 - (t - foot_at) / 0.14) if foot_at <= t < foot_at + 0.14 else 0)
    ev = [(0.0, "whoosh", 0.4)] + [(a - 0.6, "tick", 0.3) for a in at] + [(a, "pop", 0.7) for a in at] + [(at[-1], "ping", 0.6), (foot_at, "hit", 0.8)]
    return dur, fn, ev
