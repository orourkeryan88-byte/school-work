"""Edit decision list for the clothing-brand re-edit: one story cut from clips 4 + 5 (voice) over clips 2-5 (picture).
- Voice comes from the separated vocal stems (stems/vox4.wav, stems/vox5.wav), so the old music beds don't jump at cuts.
- Each cut point is nudged to the quietest spot within ±0.1 s of the word boundary, with 12 ms fades.
- Writes: vo.wav, timing.json, hyperframes/assets/js/timing.js, ad-tile stills in hyperframes/assets/img/, and the
  <video> clip tags into hyperframes/index.html (between the EDL markers).
    python3 build_edl.py"""
import json, subprocess, numpy as np, soundfile as sf

SR = 44100
GAP = 0.05                                   # breath between spliced lines (tight, reel pace)
VOX = {k: sf.read(f"stems/vox{k}.wav", dtype="float32", always_2d=True)[0].mean(1) for k in ("4", "5")}
WORDS = {k: json.load(open(f"stems/words{k}.json")) for k in ("4", "5")}

# id, voice source, audio in, audio out, visual
#   card  = talking head cropped into the presenter window (source clip, media start = audio in)
#   full  = full-bleed b-roll (clip, media start, playback rate)
#   gfx   = graphics only
SEG = [
    ("callout",   "5", 0.10, 1.52, ("card", "5", 0, 520, 1080)),   # below the old "owners." headline
    ("ad1",       "4", 0.18, 1.45, ("card", "4")),
    ("ad2",       "4", 1.94, 3.28, ("card", "4")),
    ("ad3",       "4", 3.62, 4.66, ("card", "4")),
    ("only",      "4", 5.06, 6.52, ("gfx",)),
    ("how",       "4", 6.58, 9.16, ("card", "4")),
    ("sellers",   "4", 9.30, 11.38, ("full", "3", 0.0, 1.0)),
    ("angles",    "4", 13.56, 14.80, ("full", "3", 4.78, 1.0)),
    ("angles2",   "4", 14.80, 16.76, ("full", "3", 6.70, 0.55)),
    ("make",      "4", 16.82, 18.22, ("gfx",)),
    ("make_ads",  "4", 18.58, 19.06, ("gfx",)),
    ("faces",     "4", 19.06, 19.98, ("full", "2", 0.05, 1.0)),
    ("hooks",     "4", 19.98, 20.78, ("full", "2", 1.66, 1.0)),
    ("settings",  "4", 20.78, 21.78, ("full", "2", 3.12, 1.0)),
    ("test",      "4", 21.78, 24.08, ("full", "2", 4.66, 1.0)),
    ("meta",      "4", 24.16, 26.88, ("gfx",)),
    ("kill",      "4", 26.90, 31.90, ("gfx",)),
    ("retainer",  "5", 6.16, 9.72, ("card", "5", 108, 392, 864)),   # between "retainer," and "win or lose"
    ("offer",     "5", 9.80, 14.76, ("gfx",)),
    ("experiment", "4", 31.93, 33.68, ("gfx",)),
    ("cta",       "4", 35.92, 40.50, ("gfx",)),
]
# no gap inside a line that was split for picture (same sentence continues)
JOIN = {"angles2", "make_ads", "hooks", "settings"}

def quiet(x, t, w=0.1):
    """nudge t to the quietest 10 ms window within ±w s"""
    a, b = int((t - w) * SR), int((t + w) * SR); a = max(a, 0); seg = x[a:b]
    if len(seg) < 900: return t
    e = np.convolve(seg ** 2, np.ones(441) / 441, "same"); return (a + int(np.argmin(e))) / SR

out, t, segs, words = [], 0.0, [], []
fade = int(0.012 * SR)
for sid, src, ain, aout, vis in SEG:
    x = VOX[src]; ain2, aout2 = quiet(x, ain), quiet(x, aout)
    clip = x[int(ain2 * SR):int(aout2 * SR)].copy()
    clip[:fade] *= np.linspace(0, 1, fade); clip[-fade:] *= np.linspace(1, 0, fade)
    if out and sid not in JOIN: out.append(np.zeros(int(GAP * SR), np.float32)); t += GAP
    start = t; out.append(clip); t += len(clip) / SR
    ws = [w for w in WORDS[src] if ain2 - 0.02 <= w["start"] < aout2 - 0.05]
    if sid == "cta": words.append({"seg": sid, "text": "Comment", "start": round(start + 0.06, 3)})   # said, but missed by the recogniser
    for w in ws: words.append({"seg": sid, "text": w["text"], "start": round(start + w["start"] - ain2, 3)})
    segs.append({"id": sid, "src": src, "ain": round(ain2, 3), "aout": round(aout2, 3), "start": round(start, 3),
                 "dur": round(aout2 - ain2, 3), "vis": list(vis)})
# visuals run until the next segment starts (gaps are covered by the earlier shot)
for i, s in enumerate(segs):
    nxt = segs[i + 1]["start"] if i + 1 < len(segs) else s["start"] + s["dur"] + 1.5   # end card hold
    s["vdur"] = round(nxt - s["start"], 3)
total = round(segs[-1]["start"] + segs[-1]["vdur"], 2)
vo = np.concatenate(out + [np.zeros(int((total - t + 0.1) * SR), np.float32)])
sf.write("vo.wav", vo, SR)
T = {"duration": total, "segments": segs, "words": words}
json.dump(T, open("timing.json", "w"), indent=1)
open("hyperframes/assets/js/timing.js", "w").write("window.TIMING = " + json.dumps(T) + ";\n")

# ---- ad-tile stills (the "10 to 15 ads" grid): clean frames from the b-roll + the three faces from clip 4 ----
STILLS = [("2", 0.8), ("2", 2.3), ("2", 3.8), ("3", 1.5), ("2", 5.6), ("4", 0.9), ("4", 2.6), ("4", 4.3), ("3", 3.8), ("3", 5.6),
          ("2", 6.6), ("4", 7.5), ("3", 7.4), ("2", 1.2), ("2", 4.2)]
for i, (c, tt) in enumerate(STILLS):
    crop = "crop=iw:iw*4/3:0:ih*0.16" if c in ("4", "5") else "crop=iw:iw*4/3:0:(ih-iw*4/3)/2"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(tt), "-i", f"source/clip{c}.mp4", "-frames:v", "1",
                    "-vf", f"{crop},scale=300:400,eq=saturation=0.85:contrast=1.06", f"hyperframes/assets/img/ad{i + 1:02d}.jpg"], check=True)

# ---- the <video> tags (static, so the renderer can pre-extract their frames) ----
CW, CX, CY = 960, 60, 700                    # presenter window: 960 x 810 at (60, 700)
# default source face region: x 108-972, y 350-1079 (the old captions sit below / above it); a segment may override
tags_card, tags_full = [], []
for i, s in enumerate(segs):
    v = s["vis"]
    if v[0] == "card":
        x0, y0, cw = (v[2], v[3], v[4]) if len(v) > 2 else (108, 350, 864); S = CW / cw
        tags_card.append(f'      <video id="v{i}" class="clip" src="assets/footage/c{v[1]}.mp4" muted playsinline data-start="{s["start"]}" '
                         f'data-duration="{s["vdur"]}" data-media-start="{s["ain"]}" data-track-index="1" '
                         f'style="position:absolute; left:{-x0 * S:.1f}px; top:{-y0 * S:.1f}px; width:{1080 * S:.1f}px; height:{1920 * S:.1f}px;"></video>')
    if v[0] == "full":
        rate = f' data-playback-rate="{v[3]}"' if v[3] != 1.0 else ""
        tags_full.append(f'      <video id="v{i}" class="clip" src="assets/footage/c{v[1]}.mp4" muted playsinline data-start="{s["start"]}" '
                         f'data-duration="{s["vdur"]}" data-media-start="{v[2]}"{rate} data-track-index="2" '
                         f'style="position:absolute; left:0; top:0; width:1080px; height:1920px; object-fit:cover;"></video>')
h = open("hyperframes/index.html").read()
a, b = h.index("<!-- EDL:card -->"), h.index("<!-- /EDL:card -->")
h = h[:a] + "<!-- EDL:card -->\n" + "\n".join(tags_card) + "\n      " + h[b:]
a, b = h.index("<!-- EDL:full -->"), h.index("<!-- /EDL:full -->")
h = h[:a] + "<!-- EDL:full -->\n" + "\n".join(tags_full) + "\n      " + h[b:]
import re
h = re.sub(r'(data-composition-id="main" data-width="1080" data-height="1920" data-duration=")[\d.]+', rf"\g<1>{total}", h)
h = re.sub(r'(id="score"[^>]*data-duration=")[\d.]+', rf"\g<1>{total}", h)
open("hyperframes/index.html", "w").write(h)
for s in segs: print(f'{s["id"]:11s} {s["start"]:6.2f} +{s["vdur"]:5.2f}  {s["vis"][0]:5s} ' + " ".join(w["text"] for w in words if w["seg"] == s["id"]))
print("total", total)
