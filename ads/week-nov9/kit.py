"""Week kit: builds one HyperFrames composition per ad from a scenes file, in the house look
(ink/cream bases, lime = fixes + CTA, orange = problems, lilac = product pops; Instrument Sans/Serif + Plex Mono).
    python3 kit.py <ad_dir>        (ad_dir has scenes.html, scenes.css, scenes.js, meta.json)
Writes <ad_dir>/hyperframes/index.html and copies fonts + GSAP. Word times come from the VO transcript, so captions
are written as words("#cap", [times]) using the real spoken times."""
import json, os, shutil, sys
ad = sys.argv[1]; meta = json.load(open(os.path.join(ad, "meta.json")))
read = lambda f: open(os.path.join(ad, f)).read() if os.path.exists(os.path.join(ad, f)) else ""
DUR = meta["duration"]; KW = meta["keyword"]; CTA0 = meta["cta_start"]; W = meta["cta_words"]   # [comment, kw, then one time per lead word]
LEAD = meta.get("cta_lead", ["we'll", "show", "you", "how"])
lead_html = " ".join('<span class="w">%s</span>' % w for w in LEAD)
lead_times = ", ".join(str(t) for t in W[2:2 + len(LEAD)])
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>Southline: %(title)s</title>
<script src="assets/vendor/gsap.min.js"></script>
<style>
  @font-face { font-family: "Instrument Sans"; src: url(assets/fonts/is-500.woff2) format("woff2"); font-weight: 500; }
  @font-face { font-family: "Instrument Sans"; src: url(assets/fonts/is-700.woff2) format("woff2"); font-weight: 700; }
  @font-face { font-family: "Instrument Serif"; src: url(assets/fonts/iserif-italic.woff2) format("woff2"); font-style: italic; font-weight: 400; }
  @font-face { font-family: "IBM Plex Mono"; src: url(assets/fonts/plex-500.woff2) format("woff2"); font-weight: 500; }
  :root { --cream: #f3efe6; --ink: #0d0d0f; --ink2: #18181c; --ink3: #25252b; --muted: #8c8a93; --mutedl: #6b6873;
          --volt: #d7ff3c; --blaze: #ff5b1f; --lilac: #b6a3ff; --lilacd: #8f78f0; }
  html, body { margin: 0; background: var(--ink); }
  body { font-family: "Instrument Sans", sans-serif; -webkit-font-smoothing: antialiased; }
  #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
  .full { position: absolute; inset: 0; }
  #bg { z-index: 0; background: var(--ink); }
  #grain { z-index: 90; opacity: .06; mix-blend-mode: overlay; inset: -200px;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/></filter><rect width='300' height='300' filter='url(%%23n)'/></svg>"); }
  .scene { position: absolute; inset: 0; z-index: 10; overflow: hidden; }
  .cam { position: absolute; inset: 0; transform-origin: 50%% 40%%; }
  .light { color: var(--ink); } .dark { color: var(--cream); }
  .cap { position: absolute; left: 72px; width: 936px; top: 560px; transform-origin: 0%% 50%%; z-index: 20; }
  .cap .ld { font-family: "Instrument Serif", serif; font-style: italic; font-size: 72px; line-height: 1.05; opacity: .85; display: block; margin-bottom: 14px; }
  .cap .kw { font-weight: 700; font-size: var(--k, 150px); letter-spacing: -0.04em; line-height: .95; display: block; }
  .cap .w { display: inline-block; position: relative; }
  .ul { position: absolute; left: 0; right: 0; bottom: -8px; height: 12px; border-radius: 3px; transform-origin: 0 50%%; display: block; }
  .dark .ul { background: var(--volt); } .ul.bad { background: var(--blaze) !important; }
  .light .ul { background: var(--volt); left: -8px; right: -8px; bottom: 4px; height: 42%%; border-radius: 4px; z-index: -1; }
  .label { position: absolute; left: 72px; top: 470px; font: 500 28px "IBM Plex Mono", monospace; letter-spacing: .12em; text-transform: uppercase; z-index: 20; }
  .light .label { color: var(--mutedl); } .dark .label { color: var(--muted); }
  .hook { position: absolute; left: 72px; top: 590px; z-index: 20; font-weight: 700; font-size: 176px; letter-spacing: -0.045em; line-height: 1; white-space: nowrap; }
  .hook .mk { position: absolute; left: -10px; right: -10px; bottom: 18px; height: 60px; border-radius: 6px; background: var(--volt); z-index: -1; transform-origin: 0 50%%; }
  #ctaKw { position: absolute; left: 60px; top: 880px; font-weight: 700; font-size: %(kwsize)dpx; letter-spacing: -0.06em; line-height: .8; color: var(--volt); white-space: nowrap; }
  #brand { position: absolute; left: 72px; top: 1380px; }
  #brand .b1 { font-weight: 700; font-size: 76px; letter-spacing: -0.03em; color: var(--cream); }
  #brand .b2 { font: 500 28px "IBM Plex Mono", monospace; letter-spacing: .14em; color: var(--muted); margin-top: 6px; }
  #flash { position: absolute; inset: 0; z-index: 60; background: var(--cream); opacity: 0; }
%(css)s
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-duration="%(dur)s">
  <div id="bg" class="full" data-layout-ignore></div>
%(html)s
  <!-- CTA %(cta0)s–%(dur)s -->
  <section id="sCTA" class="clip scene dark" data-start="%(cta0)s" data-duration="%(ctad)s" data-track-index="1">
    <div class="cam" id="camCTA">
      <div id="ctaKw" data-layout-ignore>%(kw)s</div>
      <div class="cap" id="cCTA" style="top:600px"><span class="ld">%(lead)s</span>
        <span class="kw" style="--k:160px"><span class="w">comment</span></span></div>
      <div id="brand"><div class="b1">Southline</div><div class="b2">%(tag)s</div></div>
    </div>
  </section>
  <div id="flash" data-layout-ignore></div>
  <div id="grain" class="full" data-layout-ignore></div>
  <audio id="score" src="assets/audio.wav" data-start="0" data-duration="%(dur)s" data-track-index="10" data-volume="1"></audio>
</div>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });
  const DUR = %(dur)s;
  const E = { in: "expo.out", cam: "sine.inOut", ui: "back.out(1.4)" };
  const rnd = i => { const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return x - Math.floor(x); };
  function words(capSel, t0, step, times) {
    const ws = document.querySelectorAll(capSel + " .w");
    ws.forEach((w, i) => tl.fromTo(w, { y: 24, opacity: 0, filter: "blur(8px)" }, { y: 0, opacity: 1, filter: "blur(0px)", duration: 0.18, ease: E.in }, times ? times[i] : t0 + i * step));
  }
  const under = (sel, t) => tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: 0.22, ease: E.in }, t);
  const exit = (sel, t) => tl.to(sel, { opacity: 0, y: -12, duration: 0.12, ease: "power2.in" }, t);
  const drift = (sel, t0, t1, amt = 0.05) => tl.fromTo(sel, { scale: 1 }, { scale: 1 + amt, duration: t1 - t0, ease: E.cam }, t0);
  const punch = (sel, t) => tl.fromTo(sel, { scale: 1.12 }, { scale: 1, duration: 0.3, ease: "expo.out", immediateRender: false }, t);
  const shake = (sel, t, px = 8) => tl.fromTo(sel, { x: 0, y: 0 }, { keyframes: { x: [px, -px * .8, px * .5, -px * .3, 0], y: [-px * .6, px * .5, -px * .3, px * .2, 0] }, duration: 0.2, ease: "none", immediateRender: false }, t);
  const flash = (t, o = 0.5) => { tl.set("#flash", { opacity: o }, t); tl.to("#flash", { opacity: 0, duration: 0.2 }, t + 0.01); };

%(js)s

  // ===== CTA: "comment KEYWORD", keyword slams in, wordmark; holds
  drift("#camCTA", %(cta0)s, DUR, 0.04);
  words("#cCTA", 0, 0, [%(leadt)s, %(w0)s]);
  tl.fromTo("#ctaKw", { x: 700, filter: "blur(12px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, %(w1)s);
  shake("#camCTA", %(w1)s + 0.06, 7);
  tl.fromTo("#brand", { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: E.in }, %(w1)s + 0.4);

  window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
out = HEAD % dict(title=meta["title"], dur=DUR, cta0=CTA0, ctad=round(DUR - CTA0, 3), kw=KW, tag=meta["tag"],
                  kwsize=meta.get("kw_size", 400), css=read("scenes.css"), html=read("scenes.html"), js=read("scenes.js"),
                  w0=W[0], w1=W[1], lead=lead_html, leadt=lead_times)
hf = os.path.join(ad, "hyperframes"); os.makedirs(os.path.join(hf, "assets"), exist_ok=True)
open(os.path.join(hf, "index.html"), "w").write(out)
src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tradesmen-map-leads", "hyperframes", "assets")
for d in ("fonts", "vendor"):
    if not os.path.exists(os.path.join(hf, "assets", d)): shutil.copytree(os.path.join(src, d), os.path.join(hf, "assets", d))
print("wrote", os.path.join(hf, "index.html"))
