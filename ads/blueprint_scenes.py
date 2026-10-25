"""BATHROOM ad 'Blueprint': navy blueprint grid, white technical line drawings, cyan + amber, monospaced annotations.
Motion: routes and lines drawing on, typewriter text, a quote form filling itself, leads sorted into VISIT / SKIP.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
from PIL import Image, ImageDraw, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, fit_size, eo, eio, back, spring, clamp, ring, sprite, shadowed

LINE = (220, 238, 255); FAINT = (255, 255, 255, 26); MAJOR = (255, 255, 255, 46)
_BP = None


def bp_bg():
    """blueprint paper: navy gradient + fine and major grid lines"""
    global _BP
    if _BP is None:
        im = A.bg(); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        for x in range(0, W, 36): d.line((x, 0, x, H), fill=MAJOR if x % 180 == 0 else FAINT, width=2 if x % 180 == 0 else 1)
        for y in range(0, H, 36): d.line((0, y, W, y), fill=MAJOR if y % 180 == 0 else FAINT, width=2 if y % 180 == 0 else 1)
        im.alpha_composite(o); _BP = im
    return _BP.copy()


def amber(): return A.TH["accent2"]
def cyan(): return A.TH["accent"]


def mono(s, size, col=None, w="monob"): return text(s, w, size, col or LINE)


def typed(im, s, x, y, t, t0, size, col=None, cps=26, w="monob", cursor=True):
    """typewriter: characters appear at cps, left-aligned at x; blinking block cursor while typing"""
    n = int(clamp((t - t0) * cps, 0, len(s)))
    if n <= 0: return
    sp = text(s[:n], w, size, col or LINE); im.alpha_composite(sp, (int(x), int(y - sp.height / 2)))
    if cursor and (n < len(s) or int(t * 3) % 2 == 0):
        ImageDraw.Draw(im).rectangle((x + sp.width + 6, y - size * 0.45, x + sp.width + 6 + size * 0.5, y + size * 0.45), fill=cyan())


def house_icon(d, cx, cy, s, col, width=4):
    d.line([(cx - 26 * s, cy - 4 * s), (cx, cy - 28 * s), (cx + 26 * s, cy - 4 * s)], fill=col, width=width)
    d.rectangle((cx - 20 * s, cy - 6 * s, cx + 20 * s, cy + 24 * s), outline=col, width=width)


def van_icon(d, cx, cy, col):
    d.rounded_rectangle((cx - 40, cy - 22, cx + 30, cy + 16), 6, fill=col); d.polygon([(cx + 30, cy - 12), (cx + 46, cy - 2), (cx + 46, cy + 16), (cx + 30, cy + 16)], fill=col)
    for wx in (cx - 22, cx + 28): d.ellipse((wx - 10, cy + 8, wx + 10, cy + 28), fill=(10, 32, 66), outline=col, width=4)


# ---------------------------------------------------------------- HOOK: the quote route
PINS = [(230, 640, "NO REPLY"), (520, 560, "JUST GETTING PRICES"), (840, 700, "TOO DEAR"), (760, 980, "BOOKED"), (400, 1060, "MAYBE NEXT YEAR"), (220, 1270, "NO REPLY")]


def scene_route(word="Bathroom fitters,", dur=4.4, drive=(0.0, 2.6), start_p=0.18, result_at=2.9):
    """frame 0: 'Bathroom fitters,' + a blueprint map: the van's route to six free-quote visits is already drawing.
    Each pin gets its outcome tag as the van passes, km counter climbs, then '6 FREE QUOTES.' / '1 JOB.'"""
    big = text(word, "bl", fit_size(word, "bl", 140, 980), A.TH["ink"])
    start = (120, 470)
    pts = [start] + [(x, y) for x, y, _ in PINS]
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]; total = sum(seg)
    def at(p):  # point along the route at fraction p
        dd = p * total
        for (a, b), L in zip(zip(pts, pts[1:]), seg):
            if dd <= L: f = dd / L; return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
            dd -= L
        return pts[-1]
    reach = [sum(seg[:i + 1]) / total for i in range(len(PINS))]
    r1 = text("6 FREE QUOTES.", "bl", 120); r2 = text("1 JOB.", "bl", 170, amber())

    def fn(t):
        im = bp_bg(); d = ImageDraw.Draw(im)
        put(im, big, 60 + big.width / 2, 300, 1)
        p = start_p + (1 - start_p) * eio(clamp((t - drive[0]) / (drive[1] - drive[0])))
        # dashed route drawn so far
        n = 140; prev = at(0)
        for i in range(1, int(n * p) + 1):
            q = at(i / n)
            if i % 2: d.line((prev, q), fill=cyan(), width=6)
            prev = q
        for i, ((x, y, lab), rp) in enumerate(zip(PINS, reach)):
            hit = p >= rp; booked = lab == "BOOKED"
            house_icon(d, x, y, 1.3, amber() if hit and booked else LINE, 5)
            if hit:
                k = clamp((p - rp) * 8); tag = mono(lab, 34, (10, 32, 66))
                bw = tag.width + 36; tx = min(max(x, bw / 2 + 20), W - bw / 2 - 20)
                d.rounded_rectangle((tx - bw / 2, y + 48, tx + bw / 2, y + 100), 10, fill=amber() if booked else (150, 186, 220))
                put(im, tag, tx, y + 74, k)
                if booked: ring(im, x, y, k, col=amber(), maxr=160, width=5, r0=30)
        vx, vy = at(p); van_icon(d, vx, vy - 40, LINE)
        km = int(214 * p); put(im, mono(f"KM DRIVEN  {km:03d}", 38, amber()), W - 260, 470, 1)
        if t >= result_at:
            k = (t - result_at) / 0.3
            o = Image.new("RGBA", (W, H), (10, 32, 66, int(190 * clamp(k)))); im.alpha_composite(o)
            put(im, r1, W / 2, 820, clamp(k / 0.3), 1.15 - 0.15 * eo(k)); put(im, r2, W / 2, 1000, clamp((k - 0.6) / 0.3), 1.6 - 0.6 * eo(k - 0.6))
        return im, (10 * (1 - (t - result_at - 0.18) / 0.15) if 0.18 <= t - result_at < 0.33 else 0)
    ev = [(0.0, "hit", 0.9)] + [(drive[0] + (rp - start_p) / (1 - start_p) * (drive[1] - drive[0]) * 0.75, "tick", 0.5) for rp in reach if rp > start_p] + \
         [(result_at, "whoosh", 0.4), (result_at + 0.18, "hit", 1.0)]
    return dur, fn, ev


# ---------------------------------------------------------------- OPEN LOOP: typewriter question
def scene_question(dur=3.6):
    lines = ["What if you knew", "which one would book", "BEFORE you got", "in the van?"]

    def fn(t):
        im = bp_bg(); y0 = 700
        t0 = 0.1
        for j, l in enumerate(lines):
            typed(im, l, 70, y0 + j * 140, t, t0, 84, amber() if j >= 2 else None, cps=34, cursor=j == len(lines) - 1 or t < t0 + len(l) / 34)
            t0 += len(l) / 34 + 0.08
        # dimension line under the question, drawing on
        p = eio((t - 2.4) / 0.6); d = ImageDraw.Draw(im); y = y0 + 4 * 140 + 10
        if p > 0:
            d.line((70, y, 70 + 940 * p, y), fill=cyan(), width=3); d.line((70, y - 20, 70, y + 20), fill=cyan(), width=3)
            if p >= 1: d.line((1010, y - 20, 1010, y + 20), fill=cyan(), width=3); put(im, mono("1 JOB = 1 VISIT", 30, cyan(), "mono"), W / 2, y + 44, 1)
        return im, 0
    return dur, fn, [(0.1 + i * 0.12, "tick", 0.3) for i in range(22)] + [(2.4, "swish", 0.4)]


# ---------------------------------------------------------------- BODY 1: the form does the filtering
def plan_drawing(w, h):
    """white line drawing of a bathroom in plan view: bath, toilet, basin, door swing"""
    def fn(d, s, im):
        d.rectangle((6 * s, 6 * s, (w - 6) * s, (h - 6) * s), outline=LINE, width=4 * s)
        d.rounded_rectangle((20 * s, 20 * s, (w * 0.55) * s, (h * 0.42) * s), 30 * s, outline=LINE, width=3 * s)  # bath
        d.ellipse(((w * 0.72) * s, 24 * s, (w * 0.9) * s, (h * 0.3) * s), outline=LINE, width=3 * s)  # toilet
        d.rectangle(((w * 0.7) * s, 14 * s, (w * 0.92) * s, 34 * s), outline=LINE, width=3 * s)
        d.rounded_rectangle((20 * s, (h * 0.62) * s, (w * 0.3) * s, (h - 20) * s), 14 * s, outline=LINE, width=3 * s)  # basin
        d.arc(((w * 0.55) * s, (h * 0.55) * s, (w * 1.05) * s, (h * 1.05) * s), 180, 270, fill=LINE, width=3 * s)  # door swing
    return sprite(w, h, fn)


def scene_form(dur=6.0, q_times=(0.5, 1.6, 2.6, 3.5), stamp_at=4.5):
    """blueprint quote-request form; each question appears and its answer chip gets selected; a plan drawing of their
    bathroom drops in as the photo; READY TO BOOK stamp"""
    Q = [("WHAT ARE YOU PLANNING?", ["Full refit", "Wet room", "Just a tap"], 0), ("BUDGET?", ["Under €5k", "€10–15k", "€15k+"], 1),
         ("WHEN?", ["Next 3 months", "Next year", "Just looking"], 0)]
    plan = plan_drawing(360, 260)
    stamp = text("READY TO BOOK", "monob", 64, (10, 32, 66))

    def fn(t):
        im = bp_bg(); d = ImageDraw.Draw(im)
        put_rise(im, text("THE AD ASKS THE QUESTIONS", "bl", fit_size("THE AD ASKS THE QUESTIONS", "bl", 84, 980)), W / 2, 300, eo(t / 0.25))
        put_rise(im, text("BEFORE YOU DRIVE.", "bl", 96, amber()), W / 2, 395, eo((t - 0.12) / 0.25))
        x0, y0 = 70, 520; d.rectangle((x0, y0, W - 70, 1560), outline=LINE, width=3)
        d.rectangle((x0, y0, W - 70, y0 + 70), fill=(255, 255, 255, 20)); put(im, mono("QUOTE REQUEST // BATHROOM", 32, cyan()), W / 2, y0 + 35, 1)
        for i, (q, opts, pick) in enumerate(Q):
            if t < q_times[i]: continue
            y = y0 + 130 + i * 200; k = eo((t - q_times[i]) / 0.3)
            put(im, mono(q, 34, LINE, "mono"), x0 + 40 + mono(q, 34, LINE, "mono").width / 2, y, k)
            x = x0 + 40
            for j, o in enumerate(opts):
                sp = mono(o, 32, (10, 32, 66) if (j == pick and t >= q_times[i] + 0.6) else LINE, "mono"); bw = sp.width + 40
                sel = j == pick and t >= q_times[i] + 0.6
                d.rounded_rectangle((x, y + 50, x + bw, y + 120), 12, fill=amber() if sel else None, outline=amber() if sel else (150, 186, 220), width=3)
                put(im, sp, x + bw / 2, y + 85, k); x += bw + 22
        if t >= q_times[3]:
            k = eo((t - q_times[3]) / 0.4); y = y0 + 130 + 3 * 200
            put(im, mono("PHOTO OF YOUR BATHROOM", 34, LINE, "mono"), x0 + 40 + mono("PHOTO OF YOUR BATHROOM", 34, LINE, "mono").width / 2, y - 20, k)
            put(im, plan, x0 + 40 + 180, y + 170 + 40 * (1 - k), k)
            put(im, mono("UPLOADED", 30, cyan(), "mono"), x0 + 520, y + 90, clamp((t - q_times[3] - 0.5) / 0.2))
        if t >= stamp_at:
            k = (t - stamp_at) / 0.3; sp = Image.new("RGBA", (stamp.width + 60, stamp.height + 40), amber() + (255,)); sp.alpha_composite(stamp, (30, 20))
            put(im, sp, W / 2 + 190, 1430, clamp(k / 0.15), 1.6 - 0.6 * eo(k), -8)
        return im, (12 * (1 - (t - stamp_at) / 0.15) if 0 <= t - stamp_at < 0.15 else 0)
    ev = [(0.0, "whoosh", 0.4)] + sum([[(q, "pop", 0.5), (q + 0.6, "click", 0.8)] for q in q_times[:3]], []) + [(q_times[3], "pop", 0.5), (q_times[3] + 0.5, "ping", 0.5), (stamp_at, "hit", 1.0)]
    return dur, fn, ev


# ---------------------------------------------------------------- BODY 2: sort into VISIT / SKIP
LEADS = [("Full refit · €10–15k · 3 months", True), ("Just getting prices", False), ("Wet room · €12k · spring", True),
         ("Leaky tap, how much?", False), ("En-suite refit · this year", True), ("No budget yet", False)]


def scene_sort(dur=4.6, start=0.4, gap=0.42):
    """lead slips drop from the top and slide left into VISIT (amber) or right into SKIP (grey); counters tick"""
    slips = [mono(s, 34, (10, 32, 66) if ok else LINE, "monob") for s, ok in LEADS]

    def fn(t):
        im = bp_bg(); d = ImageDraw.Draw(im)
        put_rise(im, text("ONLY DRIVE TO", "bl", 96), W / 2, 300, eo(t / 0.25)); put_rise(im, text("THE READY ONES.", "bl", 104, amber()), W / 2, 405, eo((t - 0.12) / 0.25))
        d.line((W / 2, 560, W / 2, 1560), fill=(150, 186, 220), width=3)
        put(im, mono("VISIT", 52, amber()), W / 4, 600, 1); put(im, mono("SKIP", 52, (150, 186, 220)), W * 3 / 4, 600, 1)
        nv = ns = 0
        for i, ((s, ok), sp) in enumerate(zip(LEADS, slips)):
            ta = start + i * gap
            if t < ta: continue
            k = eio((t - ta) / 0.4); slot = (nv if ok else ns)
            tx, ty = (W / 4 if ok else W * 3 / 4), 720 + slot * 150
            x = W / 2 + (tx - W / 2) * k; y = 470 + (ty - 470) * eo((t - ta) / 0.4)
            bw = min(sp.width + 40, 470); sc = min(1, 430 / sp.width)
            d.rounded_rectangle((x - bw / 2, y - 45, x + bw / 2, y + 45), 10, fill=amber() if ok else (16, 46, 88), outline=amber() if ok else (150, 186, 220), width=3)
            put(im, sp, x, y, 1, sc)
            if ok: nv += 1
            else: ns += 1
        return im, 0
    return dur, fn, [(0.0, "whoosh", 0.4)] + [(start + i * gap + 0.3, "click" if ok else "tick", 0.7) for i, (_, ok) in enumerate(LEADS)]


# ---------------------------------------------------------------- CTA: architect's title block with the logo
def scene_title_block(logo, dur=4.6, keyword="BATHROOM", type_at=1.0, logo_at=0.5):
    lg = logo.resize((190, 190), Image.LANCZOS)

    def fn(t):
        im = bp_bg(); d = ImageDraw.Draw(im)
        p = eio(t / 0.6)
        if p > 0: d.rectangle((50, 230, 50 + (W - 100) * p, 1640), outline=LINE, width=4)  # drawing frame draws on
        put_rise(im, text("Want ads that filter", "bl", 78), W / 2, 400, eo((t - 0.2) / 0.25))
        put_rise(im, text("before you drive?", "bl", 96, amber()), W / 2, 500, eo((t - 0.32) / 0.25))
        put(im, mono("COMMENT", 40, (150, 186, 220), "mono"), W / 2, 700, eo((t - 0.6) / 0.3))
        sp_full = text(keyword, "monob", 130, cyan()); n = int(clamp((t - type_at) * 12, 0, len(keyword)))
        if n:
            sp = text(keyword[:n], "monob", 130, cyan()); im.alpha_composite(sp, (int(W / 2 - sp_full.width / 2), int(840 - sp.height / 2)))
        y0 = 1180; d.rectangle((50, y0, W - 50, 1640), outline=LINE, width=4); d.line((380, y0, 380, 1640), fill=LINE, width=3)
        d.line((380, y0 + 230, W - 50, y0 + 230), fill=LINE, width=3)
        if t >= logo_at:
            k = (t - logo_at) / 0.3; put(im, lg, 215, y0 + 230, clamp(k / 0.15), 1.4 - 0.4 * eo(k))
        typed(im, "SOUTHLINE AGENCY", 410, y0 + 80, t, logo_at + 0.2, 52, LINE, cps=40, cursor=False)
        typed(im, "Paid ads, bathroom fitters", 410, y0 + 160, t, logo_at + 0.7, 30, (150, 186, 220), cps=60, w="mono", cursor=False)
        typed(im, "DWG NO. 001   SCALE 1:1", 410, y0 + 310, t, logo_at + 1.2, 30, (150, 186, 220), cps=60, w="mono", cursor=False)
        typed(im, "CHECKED: READY TO BOOK", 410, y0 + 380, t, logo_at + 1.6, 30, amber(), cps=60, w="mono", cursor=False)
        return im, 0
    return dur, fn, [(0.0, "swish", 0.5), (logo_at, "hit", 0.7)] + [(type_at + i / 12, "tick", 0.5) for i in range(len(keyword))] + [(type_at + 1.0, "ping", 0.6)]
