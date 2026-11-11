"""Builds the three clothing-brand reels from one template (template.html, the "Southline Clean Cut" style).
For each reel: splices the voice lines (cuts nudged to the quietest spot, 12 ms fades), maps the word timings,
writes vN/timing.json + hyperframes/assets/js/timing.js, the <video> tags and the reel's own beats into
vN/hyperframes/index.html, hard-links the shared assets in, and writes vN/cues.json for the soundtrack.
    python3 build.py            # all three
    python3 build.py v2         # one
Then: python3 mkaudio.py vN, cd vN/hyperframes && npx hyperframes render -q delivery -f 30 -o ../../southline_vN.mp4"""
import json, os, shutil, subprocess, sys
import numpy as np, soundfile as sf

SR, GAP, HOLD = 44100, 0.06, 1.6
HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA_DUR = {"creatives": 7.03, "folding_sweater": 6.13, "hook": 9.03, "jacket_rail": 6.13, "phone_sales_alerts": 6.13,
             "research": 8.03, "sales": 7.03, "talk": 22.03}

# ---- voices: each source loudness-matched once (the hook presenter and the narrator are different reads) ----
os.makedirs(f"{HERE}/voice/lev", exist_ok=True)
VOX, WORDS = {}, {}
for k in ("adam", "hook", "talk"):
    lev = f"{HERE}/voice/lev/{k}.wav"
    if not os.path.exists(lev):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{HERE}/voice/{k}.wav", "-af", "highpass=f=70,loudnorm=I=-16:TP=-2:LRA=7",
                        "-ar", str(SR), "-ac", "1", lev], check=True)
    VOX[k] = sf.read(lev, dtype="float32", always_2d=True)[0].mean(1)
    WORDS[k] = json.load(open(f"{HERE}/voice/{k}_words.json"))

# ---- the three reels ----
# segment: (id, voice, audio in, audio out, visual, join)   visual = ("vid", clip, media start[, rate]) or ("gfx",)
# join=True: no breath before it (same sentence continues over a new shot)
REELS = {
 "v1": dict(
  title="Southline - Only one sells", kicker="For clothing brands", headline="Only one of these <b>sells.</b>",
  keyword="AUDIT", sub="I'll look at your ads. Free.",
  segs=[
   ("hook1", "hook", 0.00, 1.75, ("vid", "hook", 0.00), False),     # the hook presenter reads ad one / two / three on camera
   ("hook2", "hook", 1.95, 3.45, ("vid", "hook", 1.95), False),
   ("hook3", "hook", 3.60, 4.95, ("vid", "hook", 3.60), False),
   ("only", "hook", 5.10, 6.55, ("gfx",), False),
   ("how", "hook", 6.60, 9.03, ("vid", "hook", 6.60), False),
   ("sellers", "adam", 8.80, 10.90, ("vid", "research", 0.20), False),  # the narrator takes over
   ("angles", "adam", 13.00, 14.30, ("vid", "research", 4.77), False),
   ("angles2", "adam", 14.30, 15.95, ("vid", "research", 6.70, 0.75), True),
   ("make", "adam", 16.20, 18.45, ("gfx",), False),
   ("faces", "adam", 18.55, 19.44, ("vid", "creatives", 0.05), False),
   ("hooks", "adam", 19.44, 20.24, ("vid", "creatives", 1.66), True),
   ("settings", "adam", 20.24, 21.20, ("vid", "creatives", 3.12), True),
   ("test", "adam", 21.25, 23.55, ("vid", "creatives", 4.66), False),
   ("meta", "adam", 23.80, 26.10, ("vid", "sales", 0.00), False),
   ("cta", "adam", 35.70, 39.60, ("gfx",), False),
  ],
  hook_out="only",
  beats="""
  hookOut(st("only"));
  // the three ads land on "ad one / two / three"
  ["hook1", "hook2", "hook3"].forEach((id, i) => chip("AD 0" + (i + 1), 70, 1560, st(id) + 0.05, en(id)));
  ["hook1", "hook2", "hook3"].forEach((id) => punch(W(id, -1), 1.08));
  threeUp(st("only"), W("only", -1), en("only"));
  punch(W("how", 0), 1.1);
  // research: the angles
  ["ANGLE 01", "ANGLE 02", "ANGLE 03"].forEach((t, i) => chip(t, 70 + i * 320, 330, W("angles", 2) + i * 0.12, en("angles2")));
  punch(W("sellers", 4), 1.1);
  const g = grid(st("make"), W("make", 4), W("make", 5), en("make"));
  ["faces", "hooks", "settings"].forEach((id, i) => chip(["NEW FACE", "NEW HOOK", "NEW SETTING"][i], 70, 330, st(id) + 0.03, en(id)));
  punch(W("test", 4), 1.14); flash(W("test", 4));
  const d = chip("DAY 1", 70, 330, st("meta") + 0.05, en("meta"));
  tl.set(d, { textContent: "DAY 2" }, W("meta", 3)); tl.set(d, { textContent: "DAY 3 · WINNER FOUND" }, W("meta", 5));
  punch(W("meta", 5), 1.1);
  endCard(st("cta"), W("cta", 1));
""",
  sfx=lambda S, W: [*[(W("hook" + k, -1), "hit", 0.5) for k in "123"], (W("only", -1), "hit", 0.8), (W("only", -1) + 0.02, "shimmer", 0.5),
                    *[(S["make"]["start"] + 0.05 + i * 0.09, "pop", 0.16) for i in range(10)], *[(W("make", 5) + i * 0.06, "pop", 0.18) for i in range(5)],
                    (W("test", 4), "hit", 0.7), (W("meta", 5), "coin", 0.45), *[(W("angles", 2) + i * 0.12, "pop", 0.3) for i in range(3)]],
 ),
 "v2": dict(
  title="Southline - Still paying a retainer", kicker="For clothing brands", headline="Still paying an agency <b>retainer?</b>",
  keyword="ADS", sub="We'll send you how it works",
  segs=[
   ("own", "talk", 0.15, 1.70, ("vid", "talk", 0.15), False),       # lip-synced presenter
   ("retainer", "talk", 7.75, 11.40, ("vid", "talk", 7.75), False),
   ("cr1", "talk", 11.60, 12.30, ("vid", "creatives", 0.05), False),
   ("cr2", "talk", 12.30, 13.05, ("vid", "creatives", 3.12), True),
   ("meta", "talk", 13.05, 14.30, ("vid", "talk", 13.05), False),
   ("cut", "talk", 14.30, 16.85, ("vid", "phone_sales_alerts", 0.00), True),
   ("cta", "talk", 19.35, 22.05, ("vid", "talk", 19.35), False),
  ],
  beats="""
  hookOut(st("retainer"));
  punch(W("own", 2), 1.1);
  // the retainer card: paid every month, sales or not
  const rc = card('<div class="mono" style="font-size:24px;color:#c6ccc8;">Typical agency retainer</div>' +
    '<div class="rr" style="font-size:38px;font-weight:700;margin-top:10px;">Month 1 <span class="pd">paid</span></div>' +
    '<div class="rr" style="font-size:38px;font-weight:700;margin-top:4px;">Month 2 <span class="pd">paid</span></div>' +
    '<div class="rr" style="font-size:38px;font-weight:700;margin-top:4px;">Month 3 <span class="pd">paid</span></div>', 110, 1300, 860, W("retainer", 2), en("retainer"));
  rc.querySelectorAll(".rr").forEach((r, i) => { tl.set(r, { opacity: 0 }, 0); pop(r, W("retainer", 3) + i * 0.18, { x: 80, y: 0 }); });
  const stamp = el('<div class="stamp mono">win or lose</div>'); show(stamp, W("retainer", 5), en("retainer")); pop(stamp, W("retainer", 5), { scale: 2.2, rotation: -20, y: 0 });
  ["NEW FACE", "NEW SETTING"].forEach((t, i) => chip(t, 70, 330, st(["cr1", "cr2"][i]) + 0.03, en(["cr1", "cr2"][i])));
  punch(W("meta", 2), 1.1);
  // a sale lands
  const toast = el('<div class="toast card"><span class="ic">✓</span><span class="tt">New order</span><span class="ts mono">Just now · 1 item</span></div>');
  show(toast, W("cut", -1) - 0.05, en("cut")); pop(toast, W("cut", -1) - 0.05, { y: -120, scale: 0.9 });
  chip("OUR FEE: TIED TO YOUR SALES", 70, 1560, W("cut", 2), en("cut"));
  endCard(W("cta", 2), W("cta", 2) + 0.08);
""",
  sfx=lambda S, W: [(W("own", 2), "hit", 0.6), *[(W("retainer", 3) + i * 0.18, "pop", 0.3) for i in range(3)], (W("retainer", 5), "hit", 0.7),
                    (W("meta", 2), "hit", 0.4), (W("cut", -1) - 0.05, "ping", 0.6), (W("cut", -1) + 0.1, "coin", 0.4)],
 ),
 "v3": dict(
  title="Southline - Not one pretty ad", kicker="For clothing brands", headline="Stop betting on <b>one ad.</b>",
  keyword="AUDIT", sub="I'll look at your ads. Free.",
  segs=[
   ("test", "adam", 21.25, 23.55, ("vid", "creatives", 5.30), False),   # opens on the polaroid wall, already in frame
   ("faces", "adam", 18.55, 19.44, ("vid", "creatives", 0.05), False),
   ("hooks", "adam", 19.44, 20.24, ("vid", "creatives", 1.66), True),
   ("settings", "adam", 20.24, 21.20, ("vid", "creatives", 3.12), True),
   ("meta", "adam", 23.80, 26.10, ("vid", "sales", 0.00), False),
   ("kill", "adam", 26.30, 30.30, ("gfx",), False),
   ("week", "adam", 30.40, 31.20, ("vid", "sales", 4.87), False),
   ("exp", "adam", 31.45, 33.05, ("gfx",), False),
   ("cta", "adam", 35.70, 39.60, ("gfx",), False),
  ],
  skip_caps=["exp"],
  beats="""
  hookOut(st("faces"));
  punch(W("test", 4), 1.14); flash(W("test", 4));
  ["faces", "hooks", "settings"].forEach((id, i) => chip(["NEW FACE", "NEW HOOK", "NEW SETTING"][i], 70, 330, st(id) + 0.03, en(id)));
  const d = chip("DAY 1", 70, 330, st("meta") + 0.05, en("meta"));
  tl.set(d, { textContent: "DAY 2" }, W("meta", 3)); tl.set(d, { textContent: "DAY 3" }, W("meta", 5));
  punch(W("meta", 5), 1.1);
  const g = grid(st("kill"), st("kill") + 0.5, st("kill") + 0.5, en("kill"));
  killScale(g, W("kill", 1), W("kill", 4), W("kill", 9));
  punch(W("week", 1), 1.12);
  big("And you're not paying us to", "<b>experiment.</b>", st("exp"), en("exp"), W("exp", -1) + 0.3);
  endCard(st("cta"), W("cta", 1));
""",
  sfx=lambda S, W: [(W("test", 4), "hit", 0.7), (W("meta", 5), "coin", 0.45), *[(S["kill"]["start"] + i * 0.03, "pop", 0.1) for i in range(15)],
                    (W("kill", 1), "glitch", 0.35), (W("kill", 4), "shimmer", 0.6), *[(W("kill", 9) + n * 0.08, "pop", 0.2) for n in range(6)],
                    (W("exp", -1), "hit", 0.6)],
 ),
}


def quiet(x, t, w=0.08):
    """nudge t to the quietest 10 ms window within ±w s"""
    a, b = max(int((t - w) * SR), 0), int((t + w) * SR); seg = x[a:b]
    if len(seg) < 900: return t
    e = np.convolve(seg ** 2, np.ones(441) / 441, "same"); return (a + int(np.argmin(e))) / SR


def build(name):
    R = REELS[name]; out_dir = f"{HERE}/{name}"; hf = f"{out_dir}/hyperframes"
    os.makedirs(f"{hf}/assets/js", exist_ok=True)
    fade = int(0.012 * SR); out, t, segs, words = [], 0.0, [], []
    for sid, src, ain, aout, vis, join in R["segs"]:
        x = VOX[src]; a2, b2 = quiet(x, ain), quiet(x, aout)
        clip = x[int(a2 * SR):int(b2 * SR)].copy()
        clip[:fade] *= np.linspace(0, 1, fade); clip[-fade:] *= np.linspace(1, 0, fade)
        if out and not join: out.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
        start = t; out.append(clip); t += len(clip) / SR
        for w in WORDS[src]:
            if a2 - 0.13 <= w["start"] < b2 - 0.06: words.append({"seg": sid, "text": w["text"], "start": round(start + max(0, w["start"] - a2), 3)})
        segs.append({"id": sid, "src": src, "ain": round(a2, 3), "start": round(start, 3), "dur": round(b2 - a2, 3), "vis": list(vis)})
    for i, s in enumerate(segs):                 # each shot runs until the next one starts (covers the breath)
        nxt = segs[i + 1]["start"] if i + 1 < len(segs) else s["start"] + s["dur"] + HOLD
        s["vdur"] = round(nxt - s["start"], 3)
    total = round(segs[-1]["start"] + segs[-1]["vdur"], 2)
    sf.write(f"{out_dir}/vo.wav", np.concatenate(out + [np.zeros(int((total - t + 0.1) * SR), np.float32)]), SR)
    T = {"duration": total, "segments": segs, "words": words}
    json.dump(T, open(f"{out_dir}/timing.json", "w"), indent=1)
    open(f"{hf}/assets/js/timing.js", "w").write("window.TIMING = " + json.dumps(T) + ";\n")

    # <video> tags: lip-synced presenter shots start where their audio starts; b-roll may be slowed to fill its line
    tags = []
    for i, s in enumerate(segs):
        v = s["vis"]
        if v[0] != "vid": continue
        clip, m0 = v[1], v[2]; rate = v[3] if len(v) > 3 else 1.0
        if clip in ("talk", "hook") and s["src"] == clip: m0 = s["ain"]      # keep the lips on the words
        room = MEDIA_DUR[clip] - m0 - 0.05
        if s["vdur"] * rate > room and not (clip in ("talk", "hook") and s["src"] == clip):   # lip-sync shots never slow; they hold the last frame
            rate = round(room / s["vdur"], 3); print(f"  {name}/{s['id']}: slowed {clip} to {rate}x to fill the line")
        r = f' data-playback-rate="{rate}"' if rate != 1.0 else ""
        tags.append(f'      <video id="v{i}" class="clip" src="assets/media/{clip}.mp4" muted playsinline data-start="{s["start"]}" data-duration="{s["vdur"]}" '
                    f'data-media-start="{m0}"{r} data-track-index="1" style="position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover;"></video>')
    h = open(f"{HERE}/template.html").read()
    rep = {"__TITLE__": R["title"], "__DUR__": str(total), "__VIDEOS__": "\n".join(tags), "__KICKER__": R["kicker"], "__HEADLINE__": R["headline"],
           "__KEYWORD__": R["keyword"], "__SUB__": R["sub"],
           "__BEATS__": f'  const KW = "{R["keyword"]}";\n  caps({json.dumps(R.get("skip_caps", []))});\n' + R["beats"].strip("\n")}
    for k, v in rep.items(): h = h.replace(k, v)
    open(f"{hf}/index.html", "w").write(h)

    # shared assets (hard links: no extra disk, and the renderer serves only files inside the project)
    for sub in ("fonts", "vendor", "img"):
        shutil.rmtree(f"{hf}/assets/{sub}", ignore_errors=True); shutil.copytree(f"{HERE}/shared/{sub}", f"{hf}/assets/{sub}", copy_function=os.link)
    os.makedirs(f"{hf}/assets/media", exist_ok=True)
    for clip in {s["vis"][1] for s in segs if s["vis"][0] == "vid"}:
        dst = f"{hf}/assets/media/{clip}.mp4"
        if not os.path.exists(dst): os.link(f"{HERE}/media/{clip}.mp4", dst)

    # soundtrack cues: whoosh into every new shot, ticks under the words, riser + drop-out into the end card
    S = {s["id"]: s for s in segs}
    def W(sid, k): a = [w["start"] for w in words if w["seg"] == sid]; return a[max(0, min(k if k >= 0 else len(a) + k, len(a) - 1))]
    ev = [[0.0, "hit", 0.75], [0.02, "shimmer", 0.4]]
    for s in segs[1:]: ev.append([round(s["start"] - 0.1, 3), "whoosh", 0.4])
    for w in words: ev.append([w["start"], "tick", 0.05])
    for at, n, g in R["sfx"](S, W): ev.append([round(at, 3), n, g])
    endc = S["cta"]["start"] if name != "v2" else W("cta", 2)
    ev += [[round(endc - 0.7, 3), "riser", 0.6], [round(endc, 3), "hit", 0.9], [round(total - 0.6, 3), "coin", 0.35]]
    ev.sort(key=lambda e: e[0])
    json.dump({"duration": total, "bpm": 123, "events": ev, "dropouts": [[round(endc - 0.27, 3), round(endc - 0.02, 3)]]}, open(f"{out_dir}/cues.json", "w"), indent=0)

    print(f"{name}: {total}s")
    for s in segs: print(f'  {s["id"]:9s} {s["start"]:6.2f} +{s["vdur"]:5.2f} {s["vis"][0]:4s} ' + " ".join(w["text"] for w in words if w["seg"] == s["id"]))


for n in (sys.argv[1:] or REELS): build(n)
