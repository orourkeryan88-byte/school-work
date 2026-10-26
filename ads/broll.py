"""Code-drawn B-roll shots for the trust video (no stock footage). Each shot is fn(ts) -> RGB 1080x1920 PIL image,
moving continuously with ts: desk (monitor showing a kitchen ad), phone_feed (feed of trade posts scrolling),
van_road (a van driving past houses at dusk), map (top-down map panning, pins pulsing), dashboard (ads dashboard,
chart drawing on), site (house going up, crane swinging), planner (wall planner with job blocks, slow pan).
Static layers are drawn once; only the moving parts are drawn per frame."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import adkit as A

W, H = 1080, 1920
ACC = (56, 140, 255)


def vgrad(w, h, top, bottom, stops=None):
    g = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top, np.float32) * (1 - g) + np.array(bottom, np.float32) * g
    return np.repeat(arr, w, axis=1)

def glow(arr, cx, cy, r, col, s):
    h, w = arr.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
    b = np.exp(-(((xx - cx) / r) ** 2 + ((yy - cy) / r) ** 2))[..., None] * s
    return arr * (1 - b) + np.array(col, np.float32) * b

def img(arr): return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ======================================================================= desk
_desk = {}
def desk(ts):
    """dark room, a monitor showing a sponsored kitchen post with a before/after slider, cursor moving"""
    import kitchen_scenes as K
    if not _desk:
        a = vgrad(W, H, (16, 17, 24), (6, 6, 9)); a = glow(a, 540, 820, 620, (50, 80, 150), 0.55)
        a[1330:] = vgrad(W, H - 1330, (36, 32, 30), (14, 12, 11)); a = glow(a, 540, 1360, 420, (70, 90, 140), 0.25)
        base = img(a); d = ImageDraw.Draw(base)
        d.rectangle((0, 400, W, 418), fill=(22, 22, 28))
        for x, y, r in [(60, 300, 60), (140, 380, 70), (40, 460, 55), (210, 330, 50), (120, 520, 48), (250, 450, 40)]:  # ivy, top left
            d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(14, 26, 18))
        d.rounded_rectangle((80, 530, 1000, 1110), 26, fill=(8, 8, 10)); d.polygon([(505, 1110), (575, 1110), (590, 1250), (490, 1250)], fill=(26, 26, 30))
        d.ellipse((390, 1238, 690, 1290), fill=(30, 30, 34))
        d.rounded_rectangle((240, 1420, 840, 1540), 18, fill=(38, 38, 44))
        for r in range(4):
            for c in range(14): d.rounded_rectangle((258 + c * 41, 1434 + r * 26, 292 + c * 41, 1454 + r * 26), 4, fill=(54, 54, 62))
        d.ellipse((900, 1440, 965, 1535), fill=(40, 40, 46)); d.rectangle((100, 1350, 195, 1470), fill=(64, 56, 50)); d.arc((170, 1375, 230, 1440), -90, 90, fill=(64, 56, 50), width=12)
        for x, y, r in [(930, 1080, 50), (990, 1030, 46), (880, 1020, 40), (960, 960, 42), (1030, 1110, 38)]: d.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), fill=(16, 30, 20))
        d.rectangle((920, 1150, 1010, 1330), fill=(40, 36, 34))
        _desk.update(base=base, b=K.kitchen_art(360, 280, False), a=K.kitchen_art(360, 280, True, 1), K=K)
    K = _desk["K"]; im = _desk["base"].copy(); SW_, SH_ = 880, 540
    sc = Image.new("RGB", (SW_, SH_), (244, 245, 248)); d = ImageDraw.Draw(sc)
    d.rectangle((0, 0, SW_, 40), fill=(228, 230, 236)); [d.ellipse((16 + i * 24, 13, 30 + i * 24, 27), fill=c) for i, c in enumerate([(240, 96, 90), (245, 190, 70), (90, 200, 110)])]
    d.rounded_rectangle((40, 62, 440, 520), 18, fill=(255, 255, 255)); d.ellipse((60, 78, 100, 118), fill=ACC)
    d.rounded_rectangle((112, 84, 260, 98), 7, fill=(210, 212, 218)); d.rounded_rectangle((112, 104, 200, 114), 5, fill=(226, 228, 232))
    f = 0.5 + 0.42 * math.sin(ts * 1.4); sc.paste(K.before_after(_desk["b"], _desk["a"], f).convert("RGB"), (60, 130))
    d.rounded_rectangle((60, 430, 420, 480), 12, fill=ACC); d.text((180, 440), "Get a quote", font=A.font("bl", 26), fill=(255, 255, 255))
    d.rounded_rectangle((480, 62, 840, 270), 18, fill=(255, 255, 255))
    pts = [(500 + i * 16, 230 - 90 * (0.5 + 0.5 * math.sin(i * 0.5 + ts * 0.8)) * (i / 20)) for i in range(21)]; d.line(pts, fill=ACC, width=5)
    d.rounded_rectangle((480, 290, 840, 520), 18, fill=(255, 255, 255))
    for i in range(4):
        y = 320 + i * 50; d.ellipse((500, y, 520, y + 20), fill=ACC if i % 2 == 0 else (120, 200, 140)); d.rounded_rectangle((536, y + 3, 700 - i * 20, y + 17), 7, fill=(214, 216, 222))
    cx, cy = 300 + 220 * math.sin(ts * 0.7), 300 + 130 * math.sin(ts * 1.1)
    d.polygon([(cx, cy), (cx, cy + 30), (cx + 8, cy + 23), (cx + 15, cy + 36), (cx + 20, cy + 33), (cx + 13, cy + 21), (cx + 23, cy + 21)], fill=(20, 20, 20), outline=(255, 255, 255))
    im.paste(sc, (100, 550)); return im


# ======================================================================= phone feed
_pf = {}
def phone_feed(ts, speed=150):
    """a phone scrolling a feed of trade posts over warm bokeh"""
    import kitchen_scenes as K
    PW_, PH_, SW_, SH_ = 640, 1300, 600, 1260
    if not _pf:
        a = vgrad(W, H + 600, (14, 12, 20), (5, 5, 9)); rng = np.random.default_rng(3); bk = img(a).convert("RGBA")
        o = Image.new("RGBA", bk.size, (0, 0, 0, 0)); d = ImageDraw.Draw(o)
        for _ in range(26):
            x, y, r = rng.uniform(0, W), rng.uniform(0, H + 600), rng.uniform(40, 140); c = [(255, 170, 90), (90, 140, 255), (255, 220, 160)][rng.integers(3)]
            d.ellipse((x - r, y - r, x + r, y + r), fill=c + (int(rng.uniform(25, 70)),))
        bk.alpha_composite(o.filter(ImageFilter.GaussianBlur(18)))
        posts = []
        for i in range(6):
            p = Image.new("RGB", (SW_, 720), (255, 255, 255)); d = ImageDraw.Draw(p)
            d.ellipse((20, 20, 76, 76), fill=ACC if i % 2 == 0 else (230, 140, 60)); d.rounded_rectangle((92, 30, 300, 46), 8, fill=(210, 212, 218)); d.rounded_rectangle((92, 56, 220, 66), 5, fill=(228, 230, 234))
            pic = K.kitchen_art(560, 500, i % 3 != 1, i).convert("RGB") if i % 2 == 0 else Image.fromarray(vgrad(560, 500, (120, 170, 220), (240, 210, 180)).astype(np.uint8))
            if i % 2 == 1:
                dd = ImageDraw.Draw(pic); dd.rectangle((0, 400, 560, 500), fill=(110, 140, 90)); dd.rectangle((120, 220, 440, 400), fill=(236, 230, 220), outline=(40, 40, 40), width=5)
                dd.polygon([(100, 224), (280, 110), (460, 224)], fill=(150, 70, 60)); dd.rectangle((250, 300, 310, 400), fill=(80, 60, 50)); [dd.rectangle((x, 260, x + 60, 320), fill=(170, 210, 240)) for x in (150, 350)]
            p.paste(pic, (20, 92)); [d.ellipse((24 + j * 56, 612, 60 + j * 56, 648), outline=(40, 40, 40), width=4) for j in range(3)]
            d.rounded_rectangle((24, 666, 400, 680), 7, fill=(214, 216, 222)); posts.append(p)
        strip = Image.new("RGB", (SW_, 720 * 12), (255, 255, 255))
        for i in range(12): strip.paste(posts[i % 6], (0, i * 720))
        shell = A.sprite(PW_, PH_, lambda d, s, im_: d.rounded_rectangle((0, 0, PW_ * s - 1, PH_ * s - 1), 84 * s, fill=(16, 16, 18, 255)))
        mask = A.sprite(SW_, SH_, lambda d, s, im_: d.rounded_rectangle((0, 0, SW_ * s - 1, SH_ * s - 1), 64 * s, fill=(255, 255, 255, 255))).split()[3]
        _pf.update(bk=bk, strip=strip, shell=A.shadowed(shell, blur=40, dy=30, alpha=160, pad=80), mask=mask)
    oy = int(ts * 12) % 600; im = _pf["bk"].crop((0, oy, W, oy + H)).copy()
    off = int(ts * speed) % (720 * 6); scr = _pf["strip"].crop((0, off, SW_, off + SH_))
    sh = _pf["shell"]; im.alpha_composite(sh, (int(W / 2 - sh.width / 2), int(H / 2 - sh.height / 2)))
    im.paste(scr, (int(W / 2 - SW_ / 2), int(H / 2 - SH_ / 2)), _pf["mask"])
    ImageDraw.Draw(im).rounded_rectangle((W / 2 - 90, H / 2 - SH_ / 2 + 18, W / 2 + 90, H / 2 - SH_ / 2 + 58), 20, fill=(10, 10, 12))
    return im.convert("RGB")


# ======================================================================= van on the road at dusk
_vr = {}
def van_road(ts):
    """a white van driving past a row of houses at dusk; hills, houses, lamps and road move at different speeds"""
    LW = W * 3
    if not _vr:
        a = vgrad(W, H, (16, 20, 46), (236, 132, 86)); a[1300:] = vgrad(W, H - 1300, (30, 30, 36), (14, 14, 18)); sky = img(a)
        d = ImageDraw.Draw(sky); rng = np.random.default_rng(8)
        for _ in range(60): x, y = rng.uniform(0, W), rng.uniform(0, 600); d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(220, 225, 255))
        hills = Image.new("RGBA", (LW, H), (0, 0, 0, 0)); d = ImageDraw.Draw(hills)
        d.polygon([(x, 1050 - 90 * math.sin(x / 400) - 50 * math.sin(x / 170)) for x in range(0, LW + 1, 20)] + [(LW, 1310), (0, 1310)], fill=(44, 34, 66))
        houses = Image.new("RGBA", (LW, H), (0, 0, 0, 0)); d = ImageDraw.Draw(houses); x = 0
        while x < LW:
            w = int(rng.uniform(220, 340)); h = int(rng.uniform(220, 330)); top = 1300 - h
            d.rectangle((x, top, x + w, 1300), fill=(20, 18, 30)); d.polygon([(x - 10, top), (x + w / 2, top - 110), (x + w + 10, top)], fill=(20, 18, 30))
            for wx in range(x + 30, x + w - 50, 80):
                for wy in (top + 40, top + 140):
                    if wy + 60 < 1290 and rng.random() < 0.7: d.rectangle((wx, wy, wx + 46, wy + 60), fill=(255, 196, 120) if rng.random() < 0.8 else (120, 140, 200))
            if rng.random() < 0.5:  # street lamp
                lx = x + w + 20; d.rectangle((lx, 1000, lx + 8, 1300), fill=(30, 30, 36)); d.ellipse((lx - 14, 990, lx + 22, 1016), fill=(255, 220, 150))
            x += w + int(rng.uniform(40, 120))
        hg = Image.new("RGBA", (LW, H), (0, 0, 0, 0)); hg.alpha_composite(houses.filter(ImageFilter.GaussianBlur(1)))
        _vr.update(sky=sky, hills=hills, houses=hg)
    im = _vr["sky"].copy().convert("RGBA")
    for layer, sp in ((_vr["hills"], 25), (_vr["houses"], 140)):
        ox = int(ts * sp) % (LW - W); im.alpha_composite(layer.crop((ox, 0, ox + W, H)))
    d = ImageDraw.Draw(im); d.rectangle((0, 1300, W, 1322), fill=(70, 70, 78))
    off = (ts * 700) % 260
    for x in range(-260, W + 260, 260): d.rectangle((x - off, 1690, x - off + 140, 1704), fill=(220, 220, 210))
    bob = 3 * math.sin(ts * 18); vx, vy = 540, 1590 + bob  # van: body, cab, windows, stripe, wheels
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).polygon([(vx + 280, vy - 120), (W + 200, vy - 260), (W + 200, vy + 60)], fill=(255, 240, 200, 70)); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(20)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((vx - 320, vy - 300, vx + 140, vy - 40), 26, fill=(236, 238, 242)); d.polygon([(vx + 130, vy - 300), (vx + 230, vy - 300), (vx + 300, vy - 170), (vx + 300, vy - 40), (vx + 130, vy - 40)], fill=(236, 238, 242))
    d.polygon([(vx + 150, vy - 280), (vx + 222, vy - 280), (vx + 276, vy - 180), (vx + 150, vy - 180)], fill=(40, 60, 90)); d.rectangle((vx - 320, vy - 150, vx + 300, vy - 120), fill=ACC)
    d.rectangle((vx + 290, vy - 110, vx + 304, vy - 80), fill=(255, 240, 200))
    for wx in (vx - 200, vx + 180):
        d.ellipse((wx - 62, vy - 100, wx + 62, vy + 24), fill=(16, 16, 18)); d.ellipse((wx - 30, vy - 68, wx + 30, vy - 8), fill=(150, 150, 156))
        a_ = ts * 14; d.line((wx - 26 * math.cos(a_), vy - 38 - 26 * math.sin(a_), wx + 26 * math.cos(a_), vy - 38 + 26 * math.sin(a_)), fill=(80, 80, 86), width=6)
    return im.convert("RGB")


# ======================================================================= map
_mp = {}
def map_(ts):
    """top-down night map panning slowly; accent pins pulse"""
    MW, MH = 2200, 3600
    if not _mp:
        rng = np.random.default_rng(21); m = Image.new("RGB", (MW, MH), (22, 26, 34)); d = ImageDraw.Draw(m)
        for _ in range(900):
            x, y = rng.uniform(0, MW), rng.uniform(0, MH); w, h = rng.uniform(40, 140), rng.uniform(40, 140); d.rectangle((x, y, x + w, y + h), fill=(30, 35, 46))
        d.line([(x, 1500 + 300 * math.sin(x / 300)) for x in range(0, MW + 1, 20)], fill=(28, 48, 80), width=70)
        for _ in range(40):
            if rng.random() < 0.5: x = rng.uniform(0, MW); d.line([(x + 30 * math.sin(y / 200), y) for y in range(0, MH + 1, 40)], fill=(52, 58, 74), width=int(rng.uniform(10, 24)))
            else: y = rng.uniform(0, MH); d.line([(x, y + 30 * math.sin(x / 260)) for x in range(0, MW + 1, 40)], fill=(52, 58, 74), width=int(rng.uniform(10, 24)))
        for _ in range(4): y = rng.uniform(0, MH); d.line([(x, y + 80 * math.sin(x / 500)) for x in range(0, MW + 1, 40)], fill=(78, 86, 108), width=34)
        _mp.update(m=m, pins=[(rng.uniform(0, MW), rng.uniform(0, MH), rng.uniform(0, 3)) for _ in range(60)])
    ox, oy = int(560 + 300 * math.sin(ts * 0.12)), int(800 + ts * 26) % (MH - H - 10)
    im = _mp["m"].crop((ox, oy, ox + W, oy + H)).convert("RGBA"); o = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(o)
    for x, y, ph in _mp["pins"]:
        x, y = x - ox, y - oy
        if -50 < x < W + 50 and -50 < y < H + 50:
            p = ((ts + ph) % 2.2) / 2.2; r = 14 + 70 * p; d.ellipse((x - r, y - r, x + r, y + r), outline=ACC + (int(200 * (1 - p)),), width=4)
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=ACC + (255,))
    im.alpha_composite(o); return im.convert("RGB")


# ======================================================================= dashboard
_db = {}
def dashboard(ts):
    """dark ads dashboard: sidebar, campaign cards, a line chart drawing on in a loop, bars breathing, ad rows"""
    if not _db:
        b = Image.new("RGB", (W, H), (15, 17, 23)); d = ImageDraw.Draw(b)
        d.rectangle((0, 0, 190, H), fill=(22, 25, 33))
        for i in range(7): d.rounded_rectangle((55, 220 + i * 120, 135, 300 + i * 120), 20, fill=(34, 38, 50) if i else ACC)
        d.text((240, 210), "Campaigns", font=A.font("bl", 64), fill=(240, 242, 248)); d.text((240, 300), "Kitchens · Bathrooms · Extensions", font=A.font("m", 32), fill=(130, 138, 156))
        for i, lab in enumerate(["Enquiries", "Cost per enquiry"]):
            x = 240 + i * 410; d.rounded_rectangle((x, 380, x + 380, 560), 24, fill=(24, 27, 36)); d.text((x + 30, 410), lab, font=A.font("sb", 30), fill=(140, 148, 166))
            d.rounded_rectangle((x + 30, 470, x + 220, 510), 12, fill=(44, 50, 66))
        d.rounded_rectangle((240, 600, 1040, 1120), 24, fill=(24, 27, 36))
        for i in range(5): d.line((280, 680 + i * 95, 1000, 680 + i * 95), fill=(36, 40, 52), width=2)
        d.rounded_rectangle((240, 1160, 1040, 1500), 24, fill=(24, 27, 36)); d.rounded_rectangle((240, 1540, 1040, 1880), 24, fill=(24, 27, 36))
        for i, n in enumerate(["Kitchen refit · Lucan", "Bathroom · Swords", "Extension · Naas"]):
            y = 1590 + i * 100; d.ellipse((280, y + 8, 304, y + 32), fill=(90, 210, 130) if i != 1 else ACC); d.text((330, y), n, font=A.font("sb", 34), fill=(220, 224, 234))
            d.rounded_rectangle((820, y + 8, 990, y + 30), 10, fill=(44, 50, 66))
        _db["b"] = b
    im = _db["b"].copy().convert("RGBA"); p = (ts % 6) / 6
    pts = [(290 + i * 17.7, 1060 - 340 * (0.15 + 0.85 * (i / 40) ** 1.3) - 40 * math.sin(i * 0.7)) for i in range(41)]
    n = max(2, int(41 * min(1, p * 1.4)))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).line(pts[:n], fill=ACC + (255,), width=22, joint="curve"); im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im); d.line(pts[:n], fill=(160, 200, 255), width=7, joint="curve"); x, y = pts[n - 1]; d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(255, 255, 255))
    for i in range(12):
        h = 60 + 180 * (0.5 + 0.5 * math.sin(ts * 1.3 + i * 0.6)) * (0.4 + i / 20); x = 290 + i * 62
        d.rounded_rectangle((x, 1460 - h, x + 38, 1460), 10, fill=ACC if i == 11 else (60, 90, 150))
    return im.convert("RGB")


# ======================================================================= building site
_st = {}
def site(ts):
    """morning sky, a house going up behind scaffolding, a tower crane slowly swinging, birds; slow pan"""
    SWd = 1500
    if not _st:
        a = vgrad(SWd, H, (64, 104, 168), (246, 204, 164)); a[1380:] = vgrad(SWd, H - 1380, (110, 96, 80), (60, 52, 44)); b = img(a); d = ImageDraw.Draw(b)
        d.ellipse((380, 640, 540, 800), fill=(255, 236, 200))
        d.rectangle((300, 900, 1100, 1380), fill=(196, 184, 168))
        for y in range(920, 1380, 36):
            for x in range(300 + (18 if (y // 36) % 2 else 0), 1100, 72): d.rectangle((x, y, x + 66, y + 30), outline=(172, 160, 144), width=2)
        for x in (360, 560, 820, 980): d.rectangle((x, 1000, x + 110, 1130), fill=(60, 70, 86))
        for x in range(260, 1160, 150): d.rectangle((x, 760, x + 12, 1380), fill=(70, 72, 78))
        for y in (900, 1060, 1220): d.rectangle((250, y, 1160, y + 12), fill=(70, 72, 78)); d.rectangle((250, y - 30, 1160, y - 22), fill=(150, 120, 60))
        for x in range(300, 1100, 80): d.line((x, 900, x + 40, 760, x + 80, 900), fill=(120, 96, 70), width=8)
        d.rectangle((1250, 300, 1290, 1380), fill=(240, 180, 40))
        for y in range(320, 1380, 60): d.line((1250, y, 1290, y + 60), fill=(200, 140, 30), width=4)
        _st["b"] = b
    ox = int(140 + 120 * math.sin(ts * 0.25)); im = _st["b"].crop((ox, 0, ox + W, H)).copy(); d = ImageDraw.Draw(im)
    cx, cy = 1270 - ox, 300; ang = 0.25 * math.sin(ts * 0.4); L = 900
    ex, ey = cx - L * math.cos(ang), cy + 120 * math.sin(ang)
    d.line((cx + 200 * math.cos(ang), cy - 30 * math.sin(ang), ex, ey), fill=(240, 180, 40), width=22); d.line((ex + 200, ey, ex + 200, ey + 300), fill=(40, 40, 40), width=4)
    d.rectangle((ex + 160, ey + 300, ex + 240, ey + 350), fill=(130, 110, 90))
    for i in range(5):
        bx = (ts * 90 + i * 230) % (W + 200) - 100; by = 380 + 60 * math.sin(i * 1.7) + 10 * math.sin(ts * 3 + i); w_ = 14 * abs(math.sin(ts * 6 + i)) + 4
        d.line((bx - 18, by - w_, bx, by, bx + 18, by - w_), fill=(40, 40, 50), width=4)
    return im


# ======================================================================= wall planner
_pl = {}
def planner(ts):
    """paper wall planner, months of job blocks in a few colours, slow diagonal pan with a warm light falloff"""
    PW_, PH_ = 1700, 2600
    if not _pl:
        rng = np.random.default_rng(4); a = vgrad(PW_, PH_, (238, 236, 230), (226, 222, 214)); p = img(a); d = ImageDraw.Draw(p)
        cw, ch = 220, 150
        for r in range(17):
            for c in range(7):
                x, y = 60 + c * cw, 80 + r * ch; d.rectangle((x, y, x + cw, y + ch), outline=(200, 196, 188), width=2); d.text((x + 12, y + 8), str((r * 7 + c) % 31 + 1), font=A.font("sb", 26), fill=(140, 136, 128))
            c0 = 0
            while c0 < 7:
                ln = int(rng.integers(1, 4)); col = [ACC, (240, 120, 60), (90, 180, 120), (120, 120, 140)][rng.integers(4)]
                if rng.random() < 0.8: d.rounded_rectangle((60 + c0 * cw + 8, 80 + r * ch + 56, 60 + min(7, c0 + ln) * cw - 8, 80 + r * ch + 120), 14, fill=col)
                c0 += ln
        _pl["p"] = p
    ox, oy = int(200 + 150 * math.sin(ts * 0.2)), int(200 + ts * 20) % (PH_ - H - 10)
    im = _pl["p"].crop((ox, oy, ox + W, oy + H)); a = np.asarray(im, np.float32); yy, xx = np.mgrid[0:H, 0:W]
    fall = 1 - 0.35 * np.clip(np.sqrt(((xx - 300) / 1200.0) ** 2 + ((yy - 400) / 1600.0) ** 2), 0, 1)
    return img(a * fall[..., None])
