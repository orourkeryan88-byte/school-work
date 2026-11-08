"""Lay the 15 per-scene VO lines on one track and fix every scene's start/duration.
Each scene lasts at least its line + 0.55 s, and roughly the brief's window; the end card holds 1.5 s after "Book a call."
Writes vo.wav (22.05 kHz mono), hyperframes/assets/js/timing.js and timing.json {scenes:[{id,start,dur,vo_at,words:[{text,start,end}]}], duration}."""
import json, wave, numpy as np
WIN = [7, 3, 6, 5, 8, 4, 7, 7, 8, 7, 6, 7, 6, 4, 5]          # brief windows (s)
LEAD = 0.25                                                   # line starts this long after the cut
SR = 22050
lines = json.load(open("lines.json")); scenes, tracks, t = [], [], 0.0
for (k, _), win in zip(lines, WIN):
    w = wave.open(f"vo/{k}.wav"); x = np.frombuffer(w.readframes(w.getnframes()), np.int16)
    words = json.load(open(f"vo/{k}_words.json"))["words"]; vo_len = words[-1]["end"]
    lead = 0.45 if k == "s01" else LEAD
    dur = round(max(lead + vo_len + 0.5, win - 0.6), 2) if k != "s15" else round(lead + vo_len + 1.6, 2)
    scenes.append({"id": k, "start": round(t, 3), "dur": dur, "vo_at": round(t + lead, 3),
                   "words": [{"text": d["text"], "start": round(t + lead + d["start"], 3), "end": round(t + lead + d["end"], 3)} for d in words]})
    tracks.append((t + lead, x)); t += dur
N = int((t + 0.5) * SR); y = np.zeros(N, np.float32)
for at, x in tracks:
    s = int(at * SR); y[s:s + len(x)] += x[:N - s].astype(np.float32)
with wave.open("vo.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes(np.clip(y, -32767, 32767).astype(np.int16).tobytes())
json.dump({"duration": round(t, 2), "scenes": scenes}, open("timing.json", "w"), indent=1)
open("hyperframes/assets/js/timing.js", "w").write("window.TIMING = " + json.dumps({"duration": round(t, 2), "scenes": scenes}) + ";\n")   # the 3D scenes and UI read this
for s in scenes: print(s["id"], s["start"], s["dur"])
print("total", round(t, 2))

# keep index.html's clip windows in step with the scenes (overlay sections, HUD, captions, audio, total length)
import re
H = "hyperframes/index.html"; h = open(H).read(); D = round(t, 2); sc = {s["id"]: s for s in scenes}
win = {"u1": "s01", "u2": "s02", "u4": "s04", "u11": "s11", "u5": "s05", "u6": "s06", "u7": "s07", "u8": "s08", "u9": "s09", "u10": "s10", "u13": "s13", "ec": "s15"}
def setclip(h, cid, start, dur):
    return re.sub(r'(id="%s"[^>]*?data-start=")[\d.]+(" data-duration=")[\d.]+' % cid, r"\g<1>%s\g<2>%s" % (round(start, 2), round(dur, 2)), h)
for cid, sid in win.items(): h = setclip(h, cid, sc[sid]["start"], sc[sid]["dur"])
h = setclip(h, "hudc", sc["s03"]["start"], sc["s15"]["start"] - sc["s03"]["start"])
for cid in ("world", "caps", "score"): h = setclip(h, cid, 0, D)
h = re.sub(r'(data-composition-id="main" data-width="1080" data-height="1920" data-duration=")[\d.]+', r"\g<1>%s" % D, h)
h = re.sub(r"const DUR = [\d.]+", "const DUR = %s" % D, h)
open(H, "w").write(h)
