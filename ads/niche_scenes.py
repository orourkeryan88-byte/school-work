"""Scenes for the Southline dental ('missed calls') and wedding venue ('first to reply') silent ads.
Every factory returns (duration, fn, events) like the adkit scenes. fn(t) -> (RGBA image, shake_px)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import adkit as A
from adkit import W, H, put, put_rise, text, pill, fit_size, eo, eio, back, spring, clamp, ring, underline, sprite, shadowed
from volt_scenes import RED, WHITE, DARK, header
from hook_scenes import stamp
from ghost_scenes import phone_shell, ticks

PW, PH = A.PW, A.PH
GREEN = (52, 199, 89)


def screen_put(ph, layer, scr):
    """composite a screen layer into a phone body, clipped to the screen shape"""
    layer.putalpha(ImageChops.multiply(layer.split()[3], scr)); ph.alpha_composite(layer)


def status(ph, clock, dark=True):
    d = ImageDraw.Draw(ph); d.rectangle((22, 22, PW - 22, 140), fill=(16, 18, 22) if dark else (242, 244, 247))
    d.rounded_rectangle((PW // 2 - 130, 52, PW // 2 + 130, 120), 34, fill=(0, 0, 0))
    d.text((96, 58), clock, font=A.font("sb", 44), fill=(235, 235, 240) if dark else (20, 20, 20))


def missed_notif(time, who="Unknown caller"):
    """iOS-style missed-call notification"""
    w = 820
    def fn(d, s, im):
        d.rounded_rectangle((0, 0, w * s - 1, 150 * s - 1), 40 * s, fill=(255, 255, 255, 245))
        d.rounded_rectangle((26 * s, 30 * s, 116 * s, 120 * s), 22 * s, fill=GREEN)
        # handset glyph
        d.arc((44 * s, 48 * s, 98 * s, 102 * s), 120, 330, fill=WHITE, width=10 * s)
        d.text((140 * s, 26 * s), "Missed call", font=A.font("b", 40 * s), fill=(17, 17, 16))
        d.text((140 * s, 80 * s), who, font=A.font("m", 32 * s), fill=(110, 110, 110))
        tw = A.tsize(time, A.font("m", 30 * s))[0]; d.text(((w - 36) * s - tw, 30 * s), time, font=A.font("m", 30 * s), fill=(130, 130, 130))
    return shadowed(sprite(w, 150, fn), blur=18, dy=10, alpha=60, pad=30)


# ======================================================================= DENTAL
def scene_missed_calls(word="Dentists,", dur=3.6, times=("13:02", "13:04", "13:07", "13:09", "13:13", "13:18"),
                       stack_from=0.35, gap=0.22, reveal_at=2.2):
    """frame 0: giant 'Dentists,' + a lunchtime lock screen with missed calls already stacked; more pile in with a
    red counter, then the top one is stamped NEW PATIENT. and 'THAT WAS A NEW PATIENT.' rises in"""
    big = text(word, "bl", fit_size(word, "bl", 240, 940), grad=(A.TH["accent"], A.TH["accent2"], 0))
    body, scr = phone_shell(bg=(30, 60, 70), clock="13:18"); k_ = 0.62
    wall = A.gradient((PW, PH), (40, 110, 120), (10, 30, 40), 90)
    nots = [missed_notif(tm, "Unknown caller" if i % 2 else "087 ••• ••" + str(10 + i * 7)) for i, tm in enumerate(times)]
    T = [0.0, 0.0] + [stack_from + i * gap for i in range(len(times) - 2)]  # two already there on frame 0
    clock = text("13:18", "sb", 200, WHITE); dt = text("Tuesday · lunch", "sb", 40, (220, 235, 235))
    np_ = shadowed(stamp("NEW PATIENT.", RED, 70), blur=10, dy=6, alpha=90, pad=30)
    l1 = text("THAT WAS A", "bl", 96, A.TH["ink"]); l2 = text("NEW PATIENT.", "bl", 130, grad=(A.TH["accent"], A.TH["accent2"], 0))

    def fn(t):
        im = A.bg(); sh = 14 * (1 - t / 0.2) if t < 0.2 else 0
        put(im, big, W / 2, 300, 1, 1.08 - 0.08 * eo(t / 0.25))
        ph = body.copy(); lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); lay.alpha_composite(wall)
        put(lay, dt, PW / 2, 230, 1); put(lay, clock, PW / 2, 370, 1)
        arrived = [i for i in range(len(nots)) if t >= T[i]]
        for rank, i in enumerate(reversed(arrived)):
            kk = (t - T[i]) / 0.35 if T[i] > 0 else 1
            y = 640 + rank * 178 - 120 * (1 - spring(kk)) * (rank == 0)
            if y < PH - 80: put(lay, nots[i], PW / 2, y, clamp(kk / 0.15) if rank == 0 else 1, (0.92 + 0.08 * spring(kk)) if rank == 0 else 1)
        screen_put(ph, lay, scr)
        n = len(arrived); last = T[arrived[-1]] if arrived else 0
        hap = 8 * math.sin((t - last) * 140) if 0 < t - last < 0.15 and last > 0 else 0
        put(im, ph, W / 2 + hap, 1080, 1, k_)
        cnt = pill(f"{n} MISSED CALLS", 44, RED, WHITE, w="bl"); put(im, cnt, W / 2, 560, 1, 1 + 0.2 * (1 - eo((t - last) / 0.25)) if last > 0 else 1)
        if t >= reveal_at:
            k = (t - reveal_at) / 0.3
            put(im, np_, W / 2 + 120, 1080 - PH * k_ / 2 + 640 * k_, clamp(k / 0.15), 1.8 - 0.8 * eo(k), -8)
            o = Image.new("RGBA", (W, H), (0, 0, 0, int(150 * clamp((k - 0.8) / 0.5)))); im.alpha_composite(o)
            put(im, l1, W / 2, 1180, clamp((k - 1.0) / 0.4), 1.2 - 0.2 * eo(k - 1.0)); put(im, l2, W / 2, 1320, clamp((k - 1.6) / 0.4), 1.5 - 0.5 * eo(k - 1.6))
            if k < 0.5: sh = 14 * (1 - k / 0.5)
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0)] + [(x, "ping", 0.6) for x in T[2:]] + [(reveal_at, "hit", 1.0), (reveal_at + 0.3, "whoosh", 0.4), (reveal_at + 0.48, "hit", 0.8)]


def scene_next_practice(dur=5.0, vm_at=0.3, hang_at=1.3, search_at=1.7, tap_at=3.0, booked_at=3.6,
                        lines_a=(("MOST DON'T LEAVE", False), ("A MESSAGE…", True)), lines_b=(("THEY RING THE", False), ("NEXT PRACTICE.", True))):
    """call screen goes to voicemail, they hang up, search for a dentist, tap Call on another practice, booked"""
    body, scr = phone_shell(bg=(18, 20, 26), clock="13:05"); k_ = 0.64
    hang = sprite(150, 150, lambda d, s, im: (d.ellipse((0, 0, 150 * s - 1, 150 * s - 1), fill=(255, 59, 48)),
                                              d.arc((38 * s, 52 * s, 112 * s, 126 * s), 200, 340, fill=WHITE, width=12 * s)))
    def result(name_blur, rating, you=False):
        w = 760
        def fn(d, s, im):
            d.rounded_rectangle((0, 0, w * s - 1, 170 * s - 1), 26 * s, fill=(255, 240, 240) if you else WHITE, outline=(255, 59, 48) if you else None, width=4 * s)
            if you: d.text((30 * s, 26 * s), "Your practice", font=A.font("b", 38 * s), fill=(17, 17, 16))
            else: d.rounded_rectangle((30 * s, 34 * s, (30 + name_blur) * s, 62 * s), 12 * s, fill=(196, 200, 208))
            d.text((30 * s, 86 * s), "★★★★★"[:5] if False else rating, font=A.font("sb", 30 * s), fill=(230, 160, 20))
            d.rounded_rectangle(((w - 180) * s, 50 * s, (w - 30) * s, 120 * s), 35 * s, fill=(200, 200, 200) if you else (30, 120, 230))
            d.text(((w - 140) * s, 64 * s), "Call", font=A.font("b", 34 * s), fill=WHITE)
            if you: d.text((300 * s, 90 * s), "No answer", font=A.font("b", 28 * s), fill=(220, 40, 40))
        return sprite(w, 170, fn)
    res = [result(330, "4.8 · 0.6 km"), result(270, "4.9 · 1.1 km"), result(0, "4.7 · 0.4 km", you=True)]
    bar = sprite(760, 100, lambda d, s, im: (d.rounded_rectangle((0, 0, 760 * s - 1, 100 * s - 1), 50 * s, fill=WHITE),
                                             d.ellipse((30 * s, 28 * s, 74 * s, 72 * s), outline=(120, 120, 120), width=5 * s),
                                             d.line((66 * s, 64 * s, 82 * s, 80 * s), fill=(120, 120, 120), width=5 * s)))
    booked = A.card_sprite(640, 200, lambda d, s: (d.ellipse((30 * s, 50 * s, 130 * s, 150 * s), fill=GREEN),
                                                   d.line((56 * s, 102 * s, 76 * s, 122 * s), fill=WHITE, width=10 * s), d.line((76 * s, 122 * s, 108 * s, 78 * s), fill=WHITE, width=10 * s),
                                                   d.text((160 * s, 44 * s), "Booked", font=A.font("bl", 52 * s), fill=(17, 17, 16)),
                                                   d.text((160 * s, 112 * s), "Tue 9:30 · another practice", font=A.font("m", 32 * s), fill=(90, 90, 90))), fill=WHITE, radius=36)
    query = "dentist near me"

    def fn(t):
        im = A.bg(); sh = 0; b = t >= search_at + 0.6
        header(im, lines_b if b else lines_a, t, 300, 104, search_at + 0.6 if b else 0)
        ph = body.copy(); lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if t < search_at:  # call screen
            d.rectangle((0, 0, PW, PH), fill=(28, 30, 36))
            put(lay, text("Your practice", "sb", 64, WHITE), PW / 2, 360, 1)
            put(lay, text("Voicemail…" if t >= vm_at else "Calling…", "m", 44, (190, 190, 200)), PW / 2, 450, 1)
            if t >= vm_at:  # voicemail waveform
                for i in range(18):
                    hgt = 20 + 60 * abs(math.sin(t * 9 + i * 0.7)); x = PW / 2 - 340 + i * 40
                    d.rounded_rectangle((x, 700 - hgt, x + 22, 700 + hgt), 10, fill=(120, 130, 150))
            pr = 1 - clamp(abs(t - hang_at) / 0.1) * 0.1
            put(lay, hang, PW / 2, 1300, 1, pr)
        else:  # search results
            d.rectangle((0, 0, PW, PH), fill=(242, 244, 247))
            put(lay, bar, PW / 2, 260, 1); n = int(clamp((t - search_at) / 0.5) * len(query))
            d.text((PW / 2 - 300, 236), query[:n], font=A.font("m", 40), fill=(20, 20, 20))
            for i, sp in enumerate(res):
                k = (t - search_at - 0.55 - i * 0.12) / 0.3
                if k > 0: put(lay, sp, PW / 2, 470 + i * 200, clamp(k / 0.3), 0.92 + 0.08 * spring(k))
            if t >= booked_at:
                k = (t - booked_at) / 0.35; put(lay, booked, PW / 2, 1260, clamp(k / 0.2), 0.7 + 0.3 * back(k))
        status(lay, "13:05", dark=t < search_at)
        screen_put(ph, lay, scr)
        cy = 1100; put(im, ph, W / 2, cy, 1, k_)
        if t < search_at: A.tap(im, W / 2, cy - PH * k_ / 2 + 1300 * k_, t, hang_at)
        else: A.tap(im, W / 2 + (PW / 2 - 105) * k_, cy - PH * k_ / 2 + 470 * k_, t, tap_at)
        if hang_at <= t < hang_at + 0.15: sh = 8
        if booked_at <= t < booked_at + 0.16: sh = 12
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5), (vm_at, "tick", 0.5), (hang_at, "click", 0.9), (search_at, "swish", 0.5)] + \
        [(search_at + i * 0.04, "tick", 0.25) for i in range(12)] + [(tap_at, "click", 1.0), (booked_at, "hit", 0.9), (booked_at + 0.05, "ping", 0.6)]


def scene_ai_answer(dur=5.2, ring_at=0.2, answer_at=0.8, msgs_from=1.3, msg_gap=0.66, booked_at=4.0):
    """incoming call answered instantly by the AI receptionist: waveform, transcript bubbles, consult booked card"""
    body, scr = phone_shell(bg=(14, 22, 26), clock="13:05"); k_ = 0.64
    msgs = [("ai", "Hi! How can I help?"), ("pt", "Asking about Invisalign."), ("ai", "I can book you in Thu 4:15?"), ("pt", "Perfect, thanks!")]
    def bub(who, s_):
        f = A.font("sb", 48); tw = A.tsize(s_, f)[0]; w = tw + 70; ai = who == "ai"
        return sprite(w, 110, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, 110 * s - 1), 40 * s, fill=A.TH["accent"] if ai else (60, 66, 80)),
                                                d.text((35 * s, 26 * s), s_, font=A.font("sb", 48 * s), fill=DARK if ai else WHITE)))
    bubs = [bub(w_, s_) for w_, s_ in msgs]
    badge = pill("ANSWERED BY YOUR AI RECEPTIONIST", 30, A.TH["accent"], DARK, w="bl")
    card = A.card_sprite(700, 230, lambda d, s: (d.text((40 * s, 30 * s), "NEW PATIENT · CONSULT", font=A.font("b", 30 * s), fill=(80, 90, 96)),
                                                 d.text((40 * s, 80 * s), "Thu 4:15", font=A.font("bl", 76 * s), fill=(17, 17, 16)),
                                                 d.text((40 * s, 172 * s), "Booked at 13:06, while you worked", font=A.font("m", 30 * s), fill=(90, 90, 90))), fill=WHITE, radius=40)

    def fn(t):
        im = A.bg(); sh = 0
        header(im, (("EVERY CALL.", False), ("ANSWERED.", True)), t, 300, 120)
        ph = body.copy(); lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rectangle((0, 0, PW, PH), fill=(14, 22, 26))
        if t < answer_at:  # incoming call pulse
            put(lay, text("Incoming call", "sb", 56, WHITE), PW / 2, 380, 1); ring(lay, PW / 2, 700, ((t - ring_at) % 0.6) / 0.6, maxr=260, width=8, r0=60)
            d.ellipse((PW / 2 - 70, 630, PW / 2 + 70, 770), fill=GREEN)
        else:
            put(lay, badge, PW / 2, 210, clamp((t - answer_at) / 0.2), 0.8 + 0.2 * spring((t - answer_at) / 0.4))
            for i in range(16):  # live waveform
                hgt = 10 + 40 * abs(math.sin(t * 11 + i * 0.6)); x = PW / 2 - 300 + i * 38
                d.rounded_rectangle((x, 320 - hgt, x + 20, 320 + hgt), 9, fill=A.TH["accent"])
            n = sum(1 for i in range(len(bubs)) if t >= msgs_from + i * msg_gap); y = 440
            for i in range(n):
                sp = bubs[i]; ai = msgs[i][0] == "ai"; kk = (t - msgs_from - i * msg_gap) / 0.25
                x = 60 + sp.width / 2 if ai else PW - 60 - sp.width / 2
                put(lay, sp, x, y + 30 * (1 - eo(kk)), clamp(kk / 0.3)); y += 145
        status(lay, "13:05")
        screen_put(ph, lay, scr)
        put(im, ph, W / 2, 1110, 1, k_)
        if t >= booked_at:
            k = (t - booked_at) / 0.35; put(im, card, W / 2, 1460, clamp(k / 0.2), 0.7 + 0.3 * back(k), -2)
            ring(im, W / 2, 1460, k / 1.4, maxr=520, width=6, r0=160)
            if k < 0.45: sh = 12 * (1 - k / 0.45)
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5), (ring_at, "ping", 0.7), (answer_at, "click", 0.9)] + [(msgs_from + i * msg_gap, "pop", 0.5) for i in range(len(msgs))] + \
        [(booked_at, "hit", 1.0), (booked_at + 0.05, "coin", 0.7)]


# ======================================================================= WEDDING VENUES
def enquiry_card(w=900):
    def dr(d, s):
        d.text((48 * s, 36 * s), "NEW WEDDING ENQUIRY", font=A.font("b", 30 * s), fill=(150, 120, 110))
        d.text((48 * s, 84 * s), "Aoife & Conor", font=A.font("bl", 70 * s), fill=(40, 20, 30))
        for i, (a, b) in enumerate((("Date", "Fri 11 June 2027"), ("Guests", "140"), ("Sent", "23:12"))):
            x = (48, 430, 660)[i]; d.text((x * s, 196 * s), a, font=A.font("sb", 28 * s), fill=(150, 130, 130)); d.text((x * s, 234 * s), b, font=A.font("b", 36 * s), fill=(40, 20, 30))
    return A.card_sprite(w, 310, dr, fill=(255, 250, 244), radius=44)


def scene_six_venues(word="Wedding venues,", dur=3.8, fan_at=1.0, you_at=1.9, rise_at=2.3):
    """frame 0: giant 'Wedding venues,' + a couple's enquiry card mid-slam; it fans out into six copies (sent to six
    venues), yours highlighted, then 'THEY SENT IT TO 6 VENUES.' rises in"""
    big = text(word, "bl", fit_size(word, "bl", 200, 960), grad=(A.TH["accent"], A.TH["accent2"], 0))
    card = enquiry_card(); mini = card.resize((card.width * 42 // 100, card.height * 42 // 100), Image.LANCZOS)
    you = shadowed(pill("YOU", 34, A.TH["accent"], DARK, w="bl"), blur=12, dy=6, alpha=120, pad=20)
    pos = [(W / 2 - 250 + (i % 2) * 500, 760 + (i // 2) * 220) for i in range(6)]
    l1 = text("THEY SENT IT TO", "bl", 92); l2 = text("6 VENUES.", "bl", 150, grad=(A.TH["accent"], A.TH["accent2"], 0))

    def fn(t):
        im = A.bg(); sh = 14 * (1 - t / 0.2) if t < 0.2 else 0
        put(im, big, W / 2, 330, 1, 1.08 - 0.08 * eo(t / 0.25))
        f = eio((t - fan_at) / 0.6)
        if f <= 0: put(im, card, W / 2, 900, 1, 1.06 - 0.06 * eo(t / 0.3))
        else:
            for i, (x, y) in enumerate(pos):
                ki = clamp(f * 1.2 - i * 0.04)
                put(im, mini, W / 2 + (x - W / 2) * ki, 900 + (y - 900) * ki, 1, 2.38 - 1.38 * ki, (i - 2.5) * 3 * (1 - ki))
            if f >= 1 and t >= you_at:
                k = (t - you_at) / 0.3; x, y = pos[4]
                put(im, you, x - 150, y - 70, clamp(k / 0.2), 1.4 - 0.4 * eo(k)); ring(im, x, y, k / 1.2, maxr=260, width=5, r0=80)
        if fan_at <= t < fan_at + 0.15: sh = 10
        if t >= rise_at:
            k = (t - rise_at) / 0.3; o = Image.new("RGBA", (W, H), (0, 0, 0, int(140 * clamp(k)))); im.alpha_composite(o)
            put(im, l1, W / 2, 1180, clamp(k / 0.3), 1.2 - 0.2 * eo(k)); put(im, l2, W / 2, 1330, clamp((k - 0.4) / 0.3), 1.5 - 0.5 * eo(k - 0.4))
            if 0.4 <= k < 0.9: sh = 12
        return im, sh
    return dur, fn, [(0.0, "hit", 1.0), (fan_at, "whoosh", 0.8)] + [(fan_at + 0.08 * i, "pop", 0.4) for i in range(6)] + \
        [(you_at, "ping", 0.6), (rise_at, "whoosh", 0.4), (rise_at + 0.12, "hit", 0.9)]


def scene_reply_race(dur=5.6, start=0.4, end=3.6, verdict_at=4.0):
    """six venue lanes race: a clock fast-forwards from 23:12 to next morning, replies land; venue 3 replies in
    4 minutes and gets VIEWING BOOKED, 'You' replies at 10:42 next day and gets 'booked elsewhere'"""
    lanes = [("Venue A", 9 * 60 + 20), ("Venue B", 14 * 60), ("Venue C", 4), ("Venue D", 22 * 60), ("You", 11 * 60 + 30), ("Venue F", 7 * 60)]
    total = 23 * 60
    def clock(m):
        tm = 23 * 60 + 12 + int(m); return f"{(tm // 60) % 24:02d}:{tm % 60:02d}" + (" · next day" if tm >= 24 * 60 else "")
    win = pill("VIEWING BOOKED", 28, A.TH["accent"], DARK, w="bl"); lost = pill("BOOKED ELSEWHERE", 28, RED, WHITE, w="bl")
    note = text("Survey of couples: 50-66% book the first supplier to reply (Easy Weddings)", "m", 24, A.TH["muted"])

    def fn(t):
        im = A.bg(); sh = 0
        header(im, (("THE FIRST VENUE", False), ("TO REPLY WINS.", True)) if t >= verdict_at else (("WHO REPLIES", False), ("FIRST?", True)), t, 300, 120, verdict_at if t >= verdict_at else 0)
        m = total * eio(clamp((t - start) / (end - start))) ** 2.2
        put(im, pill(clock(m), 36, (60, 30, 54), A.TH["ink"], w="b"), W / 2, 585, 1)
        d = ImageDraw.Draw(im)
        for i, (name, rep) in enumerate(lanes):
            y = 710 + i * 140; you = name == "You"
            d.rounded_rectangle((80, y - 55, W - 80, y + 55), 30, fill=(70, 34, 60) if you else A.TH["card"], outline=A.TH["accent"] if you else None, width=4)
            put(im, text(name, "bl", 40, A.TH["accent"] if you else A.TH["ink"]), 220, y, 1)
            frac = clamp(m / max(rep, 1)); x1 = 330 + (W - 520 - 330) * frac
            d.rounded_rectangle((330, y - 10, W - 300, y + 10), 10, fill=(80, 50, 70)); d.rounded_rectangle((330, y - 10, x1, y + 10), 10, fill=A.TH["accent"] if rep < 10 else (150, 120, 140))
            if m >= rep:
                tag = win if rep < 10 else (lost if you and t >= verdict_at else text(clock(rep).replace(" · next day", "+1"), "sb", 30, A.TH["muted"]))
                put(im, tag, W - 205, y, 1, 1.15 - 0.15 * eo((t - start) / 0.4) if rep < 10 else 1)
        if t >= verdict_at:
            k = (t - verdict_at) / 0.3; ring(im, W - 200, 710 + 2 * 140, k / 1.2, maxr=400, width=6, r0=60)
            if k < 0.45: sh = 12 * (1 - k / 0.45)
        put(im, note, W / 2, 1600, eo((t - verdict_at) / 0.4))
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5)] + [(start + i * 0.18, "tick", 0.35) for i in range(int((end - start) / 0.18))] + \
        [(start + 0.12, "ping", 0.7), (verdict_at, "hit", 1.0), (verdict_at + 0.05, "glitch", 0.4)]


def scene_instant_reply(dur=5.6, arrive_at=0.3, reply_at=1.0, couple_at=2.4, booked_at=3.3, fill_at=3.9):
    """the enquiry lands at 23:12 and the reply goes out the same minute; the couple says yes; viewing booked;
    then a 2027 Friday calendar fills up"""
    body, scr = phone_shell(bg=(250, 246, 242), clock="23:12"); k_ = 0.68
    def bub(lines, mine):
        w = 740; h = 44 + 62 * len(lines)
        return sprite(w, h, lambda d, s, im: (d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), 34 * s, fill=A.TH["accent"] if mine else (232, 226, 222)),
                                              [d.text((30 * s, (22 + i * 62) * s), l, font=A.font("sb", 44 * s), fill=DARK) for i, l in enumerate(lines)]))

    q = bub(["Hi! Is Fri 11 June 2027", "free for 140 guests?"], False)
    a = bub(["Hi Aoife & Conor! Yes, that", "date is free. Would you like", "to come for a viewing?"], True)
    c = bub(["Yes!! Saturday?"], False)
    sent = sprite(300, 40, lambda d, s, im: (ticks(d, 0, 6, (90, 170, 255), s), d.text((50 * s, 0), "Sent 23:12", font=A.font("m", 30 * s), fill=(120, 110, 110))))
    card = A.card_sprite(700, 200, lambda d, s: (d.text((40 * s, 28 * s), "VIEWING BOOKED", font=A.font("b", 30 * s), fill=(150, 120, 110)),
                                                 d.text((40 * s, 76 * s), "Sat 11:00", font=A.font("bl", 76 * s), fill=(40, 20, 30))), fill=(255, 250, 244), radius=40)
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    def fn(t):
        im = A.bg(); sh = 0; cal = t >= fill_at
        header(im, (("FILL YOUR", False), ("FRIDAYS.", True)) if cal else (("REPLY FIRST.", False), ("EVERY TIME.", True)), t, 300, 120, fill_at if cal else 0)
        if not cal:
            ph = body.copy(); lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
            if t >= arrive_at: put(lay, q, 50 + q.width / 2, 420, clamp((t - arrive_at) / 0.2))
            if t >= reply_at:
                k = (t - reply_at) / 0.3; put(lay, a, PW - 50 - a.width / 2, 700 + 30 * (1 - eo(k)), clamp(k / 0.3)); put(lay, sent, PW - 50 - 150, 870, clamp(k / 0.3))
            if t >= couple_at: put(lay, c, 50 + c.width / 2, 1010, clamp((t - couple_at) / 0.2))
            status(lay, "23:12", dark=False); screen_put(ph, lay, scr)
            put(im, ph, W / 2, 1100, 1, k_)
            if t >= booked_at:
                k = (t - booked_at) / 0.35; put(im, card, W / 2, 1470, clamp(k / 0.2), 0.7 + 0.3 * back(k), -2)
                if k < 0.45: sh = 12 * (1 - k / 0.45)
        else:  # 2027 calendar: every month's Fridays light up in a wave
            d = ImageDraw.Draw(im); kk = t - fill_at
            for mi, mn in enumerate(months):
                cx, cy = 175 + (mi % 3) * 345, 620 + (mi // 3) * 230
                put(im, text(mn, "bl", 34, A.TH["muted"]), cx + 30, cy - 60, 1)
                for wk in range(4):
                    x = cx - 90 + wk * 64; lit = kk >= 0.08 * mi + 0.05 * wk
                    d.rounded_rectangle((x, cy - 25, x + 50, cy + 55), 14, fill=A.TH["accent"] if lit else (70, 40, 62))
            put(im, pill("YOUR 2027 FRIDAYS", 42, A.TH["accent"], DARK, w="bl"), W / 2, 1580, eo(kk / 0.3))
        return im, sh
    return dur, fn, [(0.0, "whoosh", 0.5), (arrive_at, "ping", 0.6), (reply_at, "pop", 0.8), (couple_at, "ping", 0.6), (booked_at, "hit", 1.0)] + \
        [(fill_at + 0.08 * i, "pop", 0.35) for i in range(12)] + [(fill_at + 1.2, "shimmer", 0.7)]
