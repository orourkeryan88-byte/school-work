"""Scene timing from ONE full voiceover take (instead of per-line reads): uses take_words.json from align_take.py.
Each scene starts 0.22 s before its first word; the end card holds 1.6 s after "Book a call."
Writes vo.wav (the take, padded 0.35 s at the start), timing.json, hyperframes/assets/js/timing.js, and syncs index.html.
    python3 align_take.py vo_liam.mp3 && python3 timing_take.py vo_liam.mp3 && python3 mkaudio.py"""
import json, sys, subprocess
PAD, LEAD = 0.35, 0.22
take = sys.argv[1]; W = json.load(open("take_words.json")); ids = [k for k, _ in json.load(open("lines.json"))]
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", take, "-af", f"adelay={int(PAD*1000)}", "-ac", "1", "-ar", "44100", "vo.wav"], check=True)
first = {k: min(w["start"] for w in W if w["scene"] == k) + PAD for k in ids}
scenes = []
for i, k in enumerate(ids):
    st = 0.0 if i == 0 else round(first[k] - LEAD, 3)
    ws = [{"text": w["text"], "start": round(w["start"] + PAD, 3), "end": round(w["end"] + PAD, 3)} for w in W if w["scene"] == k]
    scenes.append({"id": k, "start": st, "vo_at": ws[0]["start"], "words": ws})
for i, sc in enumerate(scenes):
    sc["dur"] = round((scenes[i + 1]["start"] if i + 1 < len(scenes) else sc["words"][-1]["end"] + 1.6) - sc["start"], 2)
t = scenes[-1]["start"] + scenes[-1]["dur"]
json.dump({"duration": round(t, 2), "scenes": scenes}, open("timing.json", "w"), indent=1)
open("hyperframes/assets/js/timing.js", "w").write("window.TIMING = " + json.dumps({"duration": round(t, 2), "scenes": scenes}) + ";\n")
for s_ in scenes: print(s_["id"], s_["start"], s_["dur"])
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
