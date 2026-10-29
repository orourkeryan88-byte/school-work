"""Q4 'ONE THING' trust video scenes (no pitch): Q4 can make a clothing brand's year if it tests ads early, before
Black Friday, then spends late. Same look as the animation pack (pack_scenes.py): white type with soft shadows, one
blue accent, over Ryan's B-roll. Charts are illustrative only: no numbers, no results claimed.
Every factory returns (duration, fn, events). fn(t) -> (RGBA image, shake_px)."""
import math, calendar
from PIL import Image, ImageDraw
import adkit as A
from adkit import W, H, put, eo, eio, back, spring, clamp, ring, sprite, shadowed
from trust_scenes import T, rise, pop, under, card, ctext, ACC, WHITE, INK, MUTED
from pack_scenes import back_view, tee, RED

GREY = (150, 158, 176); SOFT = (210, 216, 228)


def scene_hook(dur=4.0, q4_at=0.0, l1_at=0.6, l2_at=1.1, l3_at=2.3, one_at=2.6):
    """'Q4' slams huge; 'can turn a good clothing brand / into a million-pound brand… / if you do ONE thing properly.'"""
    q4 = T("Q4", 380, ACC); l1 = T("can turn a good clothing brand", 70, SOFT, "b"); l2 = T("into a million-pound brand…", 84)
    l3 = T("if you do", 70, SOFT, "b"); l4 = T("ONE thing properly.", 104)
    def fn(t):
        im = back_view(t); sh = 16 if q4_at <= t < q4_at + 0.15 else (10 if one_at <= t < one_at + 0.12 else 0)
        if t >= q4_at: put(im, q4, W / 2, 560, clamp((t - q4_at) / 0.1), 1.5 - 0.5 * back((t - q4_at) / 0.35)); ring(im, W / 2, 560, (t - q4_at) / 1.1, col=ACC, maxr=520, width=6, r0=160)
        rise(im, l1, W / 2, 880, t, l1_at); rise(im, l2, W / 2, 990, t, l2_at)
        under(im, "into a million-pound brand…", 84, W / 2, 990, "million-pound brand", (t - l2_at - 0.45) / 0.45)
        rise(im, l3, W / 2, 1180, t, l3_at)
        if t >= one_at: put(im, l4, W / 2, 1300, clamp((t - one_at) / 0.12), 1.35 - 0.35 * back((t - one_at) / 0.35))
        return im, sh
    return dur, fn, [(q4_at, "hit", 1.0), (q4_at, "whoosh", 0.4), (l1_at, "swish", 0.4), (l2_at, "swish", 0.4), (l2_at + 0.45, "swish", 0.5), (l3_at, "swish", 0.35), (one_at, "hit", 0.8)]


def _chart_card(w=900, h=620):
    def dr(d, s):
        d.text((50 * s, 40 * s), "OCT → DEC", font=A.font("monob", 30 * s), fill=MUTED)
        for i, m in enumerate(("Oct", "Nov", "Dec")):
            x = (90 + i * 330) * s; ctext(d, x + 60 * s, (h - 60) * s, m, A.font("b", 32 * s), MUTED)
        d.line((60 * s, (h - 110) * s, (w - 50) * s, (h - 110) * s), fill=(214, 218, 228), width=3 * s)
        bx = int(60 + (330 * 1.62)); d.rounded_rectangle((bx * s, 110 * s, (bx + 150) * s, (h - 112) * s), 16 * s, fill=(234, 240, 252))
        ctext(d, (bx + 75) * s, 140 * s, "BF", A.font("monob", 26 * s), ACC)
    return card(w, h, dr, r=30)

def _curve(x0, y0, w, h, k, steep):
    """points of a rising curve inside the chart, drawn up to fraction k; steep = how hard it climbs at the end"""
    n = max(2, int(60 * k)); pts = []
    for i in range(n):
        u = i / 59; pts.append((x0 + u * w, y0 + h - h * (0.12 + 0.88 * u ** steep)))
    return pts

def scene_season(dur=6.0, h_at=0.1, h2_at=0.5, sales_at=0.9, cost_at=3.0, cap_at=3.4):
    """'Black Friday → Christmas / People buy the most.' an illustrative chart: the sales line climbs into December,
    then a red 'Ad costs' line climbs with it: '…and ads cost the most.'"""
    h1 = T("Black Friday → Christmas", 84); h2 = T("People buy the most.", 72, SOFT, "b"); cap = T("…and ads cost the most.", 78)
    CH = _chart_card(); cx, cy = W / 2, 1010; lab_s = A.pill("Sales", 30, ACC, WHITE, w="bl"); lab_c = A.pill("Ad costs", 30, RED, WHITE, w="bl")
    def fn(t):
        im = back_view(t, 0.3)
        rise(im, h1, W / 2, 370, t, h_at); rise(im, h2, W / 2, 470, t, h2_at)
        if t >= 0.4:
            k = spring((t - 0.4) / 0.6, f=1.4, d=6); y = cy + 600 * (1 - k); put(im, CH, cx, y, clamp((t - 0.4) / 0.15))
            x0, y0 = cx - 450 + 50 + 70, y - 310 + 50 + 110; d = ImageDraw.Draw(im)
            ps = eio((t - sales_at) / 1.8)
            if ps > 0:
                pts = _curve(x0, y0, 720, 360, ps, 2.6); d.line(pts, fill=ACC, width=12, joint="curve"); ex, ey = pts[-1]
                d.ellipse((ex - 14, ey - 14, ex + 14, ey + 14), fill=ACC); put(im, lab_s, min(ex + 10, x0 + 640), ey - 50, clamp(ps * 3))
            pc = eio((t - cost_at) / 1.4)
            if pc > 0:
                pts = _curve(x0, y0 + 60, 720, 300, pc, 3.4); d.line(pts, fill=RED, width=10, joint="curve"); ex, ey = pts[-1]
                d.ellipse((ex - 12, ey - 12, ex + 12, ey + 12), fill=RED); put(im, lab_c, min(ex + 10, x0 + 620), ey + 48, clamp(pc * 3))
        rise(im, cap, W / 2, 1450, t, cap_at); under(im, "…and ads cost the most.", 78, W / 2, 1450, "cost the most", (t - cap_at - 0.4) / 0.45)
        return im, 0
    return dur, fn, [(h_at, "swish", 0.4), (h2_at, "swish", 0.35), (0.4, "whoosh", 0.5), (sales_at, "swish", 0.5), (cost_at, "swish", 0.6), (cap_at, "swish", 0.4), (cap_at + 0.4, "swish", 0.5)]


def scene_wrong(dur=7.0, h_at=0.1, cal_at=0.6, row_at=1.4, pill_at=1.9, x_at=3.3, l1_at=3.6, l2_at=5.0):
    """'Where most brands go wrong': a November calendar, Black Friday week lights up, 'New ads launched' lands on it,
    a red ✗ stamps it: 'Testing at the most expensive / time of the year… / with no idea what works.'"""
    h1 = T("Where most brands go wrong.", 80); l1, l2 = T("Testing at the most", 72), T("expensive time of the year…", 72)
    l3 = T("with no idea what works.", 66, SOFT, "b"); tag = A.pill("New ads launched", 34, RED, WHITE, w="bl")
    weeks = calendar.Calendar(0).monthdayscalendar(2026, 11); BFW = next(i for i, wk in enumerate(weeks) if 27 in wk)
    CW_, CH_ = 860, 140 + len(weeks) * 96
    def dr(d, s):
        d.text((44 * s, 34 * s), "NOVEMBER", font=A.font("monob", 34 * s), fill=INK)
        for j, dn in enumerate("MTWTFSS"): ctext(d, (80 + j * 110) * s, 110 * s, dn, A.font("b", 26 * s), MUTED)
        for i, wk in enumerate(weeks):
            for j, day in enumerate(wk):
                if day: ctext(d, (80 + j * 110) * s, (180 + i * 96) * s, str(day), A.font("b", 34 * s), INK)
    CAL = card(CW_, CH_, dr, r=30)
    def fn(t):
        im = back_view(t, 0.3)
        rise(im, h1, W / 2, 370, t, h_at); under(im, "Where most brands go wrong.", 80, W / 2, 370, "wrong", (t - h_at - 0.5) / 0.4)
        cx, cy = W / 2, 860
        if t >= cal_at:
            k = spring((t - cal_at) / 0.6, f=1.4, d=6); y = cy + 600 * (1 - k); put(im, CAL, cx, y, clamp((t - cal_at) / 0.15))
            ry = y - CH_ / 2 + 180 + BFW * 96; x0 = cx - CW_ / 2 + 25
            p = eo((t - row_at) / 0.35)
            if p > 0:  # Black Friday week highlight + the day itself circled
                o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(o)
                od.rounded_rectangle((x0, ry - 40, x0 + 770 * p, ry + 40), 24, fill=ACC + (70,), outline=ACC + (255,), width=4); im.alpha_composite(o)
                bx = x0 + 55 + 4 * 110 - 25 + 25; ImageDraw.Draw(im).ellipse((bx - 40, ry - 40, bx + 40, ry + 40), outline=ACC, width=6)
            pop(im, tag, cx, ry + 96, t, pill_at, 1.5)
            if t >= x_at:  # red X stamped on Black Friday itself
                k2 = (t - x_at) / 0.3; s_ = 1.6 - 0.6 * back(k2); dd = ImageDraw.Draw(im); r = 48 * s_; bx = cx + 90
                if k2 > 0:
                    dd.line((bx - r, ry - r, bx + r, ry + r), fill=RED, width=16); dd.line((bx - r, ry + r, bx + r, ry - r), fill=RED, width=16)
        rise(im, l1, W / 2, 1400, t, l1_at); rise(im, l2, W / 2, 1490, t, l1_at + 0.25); rise(im, l3, W / 2, 1590, t, l2_at)
        under(im, "expensive time of the year…", 72, W / 2, 1490, "expensive", (t - l1_at - 0.7) / 0.4)
        return im, (12 if x_at <= t < x_at + 0.14 else 0)
    return dur, fn, [(h_at, "swish", 0.4), (cal_at, "whoosh", 0.5), (row_at, "swish", 0.5), (pill_at, "pop", 0.7), (x_at, "hit", 0.9),
                     (l1_at, "swish", 0.4), (l1_at + 0.25, "swish", 0.4), (l2_at, "swish", 0.35)]


def scene_test_now(dur=4.0, q_at=0.1, big_at=0.8, sub_at=1.7, chip_at=2.4):
    """'The one thing?' then 'TEST NOW.' slams; 'Before it gets expensive.'; a 'Black Friday · 27 Nov' chip"""
    q = T("The one thing?", 80, SOFT); big = T("TEST NOW.", 200, ACC); sub = T("Before it gets expensive.", 72)
    chip = A.pill("Black Friday  ·  27 Nov", 40, WHITE, INK, w="bl")
    def fn(t):
        im = back_view(t, 0.35)
        rise(im, q, W / 2, 620, t, q_at)
        if t >= big_at: put(im, big, W / 2, 840, clamp((t - big_at) / 0.1), 1.45 - 0.45 * back((t - big_at) / 0.35)); ring(im, W / 2, 840, (t - big_at) / 1.0, col=ACC, maxr=560, width=6, r0=200)
        rise(im, sub, W / 2, 1060, t, sub_at); under(im, "Before it gets expensive.", 72, W / 2, 1060, "expensive", (t - sub_at - 0.4) / 0.4)
        pop(im, chip, W / 2, 1240, t, chip_at, 1.4)
        return im, (14 if big_at <= t < big_at + 0.15 else 0)
    return dur, fn, [(q_at, "swish", 0.4), (big_at, "hit", 1.0), (sub_at, "swish", 0.4), (sub_at + 0.4, "swish", 0.5), (chip_at, "pop", 0.7)]


def scene_novdec(dur=5.0, h_at=0.1, nov_at=0.6, arrow_at=1.3, dec_at=1.7, order_at=2.7, cap_at=3.1):
    """'Looked in November?' NOV card (an eye: looked, didn't buy) → arrow → DEC card (the ad again, a gift) →
    'Order placed' toast; 'Show them again in December, / when they're buying gifts.'"""
    h1 = T("Looked in November?", 84); c1, c2 = T("Show them again in December,", 68), T("when they're buying gifts.", 68, SOFT, "b")
    def nov(d, s):
        d.rounded_rectangle((0, 0, 380 * s, 90 * s), 30 * s, fill=(70, 78, 98)); d.rectangle((0, 60 * s, 380 * s, 90 * s), fill=(70, 78, 98))
        ctext(d, 190 * s, 46 * s, "NOV", A.font("monob", 38 * s), WHITE)
        d.ellipse((110 * s, 150 * s, 270 * s, 250 * s), outline=INK, width=8 * s); d.ellipse((160 * s, 170 * s, 220 * s, 230 * s), fill=INK)
        ctext(d, 190 * s, 300 * s, "Looked", A.font("bl", 40 * s), INK); ctext(d, 190 * s, 350 * s, "didn't buy", A.font("m", 30 * s), MUTED)
    def dec(d, s):
        d.rounded_rectangle((0, 0, 380 * s, 90 * s), 30 * s, fill=ACC); d.rectangle((0, 60 * s, 380 * s, 90 * s), fill=ACC)
        ctext(d, 190 * s, 46 * s, "DEC", A.font("monob", 38 * s), WHITE)
        d.rectangle((130 * s, 170 * s, 250 * s, 250 * s), fill=RED); d.rectangle((120 * s, 145 * s, 260 * s, 175 * s), fill=(210, 56, 66))
        d.rectangle((182 * s, 145 * s, 198 * s, 250 * s), fill=(255, 210, 90)); d.ellipse((150 * s, 120 * s, 188 * s, 150 * s), outline=(255, 210, 90), width=7 * s)
        d.ellipse((192 * s, 120 * s, 230 * s, 150 * s), outline=(255, 210, 90), width=7 * s)
        ctext(d, 190 * s, 300 * s, "Saw your ad", A.font("bl", 40 * s), INK); ctext(d, 190 * s, 350 * s, "again", A.font("m", 30 * s), MUTED)
    NOV, DEC = card(380, 400, nov, r=30), card(380, 400, dec, r=30); toast_ = A.toast("Order placed")
    def fn(t):
        im = back_view(t, 0.3)
        rise(im, h1, W / 2, 380, t, h_at)
        y = 900; pop(im, NOV, W / 2 - 245, y, t, nov_at, 1.3)
        p = eo((t - arrow_at) / 0.4)
        if p > 0:
            d = ImageDraw.Draw(im); x0, x1 = W / 2 - 40, W / 2 - 40 + 80 * p; d.line((x0, y, x1, y), fill=WHITE, width=12)
            if p > 0.6: d.polygon([(x1 + 4, y), (x1 - 26, y - 24), (x1 - 26, y + 24)], fill=WHITE)
        pop(im, DEC, W / 2 + 245, y, t, dec_at, 1.3)
        if t >= order_at:
            k = (t - order_at) / 0.4; put(im, toast_, W / 2 + 245, y + 290, clamp(k / 0.2), 0.7 + 0.3 * back(k))
        rise(im, c1, W / 2, 1420, t, cap_at); rise(im, c2, W / 2, 1515, t, cap_at + 0.3)
        under(im, "when they're buying gifts.", 68, W / 2, 1515, "buying gifts", (t - cap_at - 0.7) / 0.4)
        return im, 0
    return dur, fn, [(h_at, "swish", 0.4), (nov_at, "pop", 0.7), (arrow_at, "swish", 0.5), (dec_at, "pop", 0.7), (order_at, "ping", 0.6), (cap_at, "swish", 0.4), (cap_at + 0.3, "swish", 0.4)]


def scene_outro(dur=4.0, a_at=0.1, b_at=0.75, save_at=1.7):
    """'Test early.' / 'Spend late.' slam one after the other; a 'Save this' pill with a bookmark pops in"""
    a, b = T("Test early.", 150), T("Spend late.", 150, ACC)
    f = A.font("bl", 46); tw = f.getlength("Save this for your Q4 plan"); pw, ph = int(tw + 150), 110
    def sv(d, s, im_):
        d.rounded_rectangle((0, 0, pw * s - 1, ph * s - 1), 55 * s, fill=WHITE)
        d.polygon([(40 * s, 28 * s), (78 * s, 28 * s), (78 * s, 84 * s), (59 * s, 70 * s), (40 * s, 84 * s)], fill=ACC)
        d.text((100 * s, 28 * s), "Save this for your Q4 plan", font=A.font("bl", 46 * s), fill=INK)
    SAVE = shadowed(sprite(pw, ph, sv), blur=20, dy=10, alpha=150, pad=40)
    def fn(t):
        im = back_view(t, 0.35); sh = 0
        for sp, y, t0 in ((a, 760, a_at), (b, 940, b_at)):
            if t >= t0: put(im, sp, W / 2, y, clamp((t - t0) / 0.1), 1.4 - 0.4 * back((t - t0) / 0.35))
            if t0 <= t < t0 + 0.13: sh = 12
        pop(im, SAVE, W / 2, 1200, t, save_at, 1.4); ring(im, W / 2, 1200, (t - save_at) / 1.0, col=ACC, maxr=360, width=5, r0=80)
        return im, sh
    return dur, fn, [(a_at, "hit", 0.9), (b_at, "hit", 0.9), (save_at, "pop", 0.8), (save_at + 0.1, "shimmer", 0.6)]
