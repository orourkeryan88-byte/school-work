"""Re-time the ad to a real voiceover.
    python3 retime.py [transcript_words.json]
The composition is authored once, in index.template.html, on the script's estimated word times (vo_words.json).
Given the transcription of a real read (per-word start/end seconds), this lines up its words with the script, builds a
time warp (estimated -> real), and writes hyperframes/index.html (scene cuts warped, WARP table filled in) and
cues.json (SFX, word ticks and the music drop-out warped). With no transcript it writes the estimated version.
The end card holds HOLD seconds after the last word."""
import difflib, json, re, subprocess, sys

HOLD, EST_DUR, EST_LAST_END = 1.62, 21.7, 20.08
_e = json.load(open("vo_words_sean.json")); _e = _e.get("words", _e)
est = [{"word": w["text"], "start": w["start"]} for w in _e if not w["text"].startswith("[") and not w["text"].endswith("]")]

def norm(w):
    w = w.lower().replace("’", "'")
    w = re.sub(r"[^a-z0-9']", "", w)
    return {"qfour": "q4", "q": "q4"}.get(w, w)

anchors = [(0.0, 0.0)]
if len(sys.argv) > 1:
    raw = json.load(open(sys.argv[1]))
    raw = raw.get("words", raw) if isinstance(raw, dict) else raw
    real = [w for w in raw if (w.get("type", "word") == "word") and (w.get("text") or w.get("word", "")).strip()
            and not (w.get("text") or w.get("word", "")).strip().startswith("[")]
    rt = [norm(w.get("text") or w.get("word")) for w in real]
    et = [norm(w["word"]) for w in est]
    sm = difflib.SequenceMatcher(a=et, b=rt, autojunk=False)
    matched = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): matched[blk.a + k] = real[blk.b + k]
    print(f"matched {len(matched)}/{len(est)} script words")
    for i, w in enumerate(est):
        if i in matched: anchors.append((w["start"], float(matched[i]["start"])))
    last = matched.get(len(est) - 1) or real[-1]
    end_real = float(last.get("end", last["start"] + 0.3))
    anchors += [(EST_LAST_END, end_real), (EST_DUR, end_real + HOLD)]
else:
    anchors.append((EST_DUR, EST_DUR))
# keep it strictly increasing on both axes
clean = [anchors[0]]
for a, b in anchors[1:]:
    if a > clean[-1][0] + 1e-6 and b > clean[-1][1] + 1e-6: clean.append((a, b))
anchors = clean

def W(t):
    if t <= anchors[0][0]: return t
    for (a0, b0), (a1, b1) in zip(anchors, anchors[1:]):
        if t <= a1: return b0 + (t - a0) * (b1 - b0) / (a1 - a0)
    a, b = anchors[-1]; return b + (t - a)

DUR = round(W(EST_DUR), 3)
import os
html = open(os.environ.get("TEMPLATE", "index.template.html")).read()
html = html.replace("const WARP = [[0, 0], [21.7, 21.7]]; // @warp",
                    "const WARP = " + json.dumps([[round(a, 3), round(b, 3)] for a, b in anchors]) + "; // @warp")
def clip(m):
    s0, d0 = float(m.group(2)), float(m.group(3))
    return f'{m.group(1)}data-start="{round(W(s0), 3)}" data-duration="{round(W(s0 + d0) - W(s0), 3)}"'
html = re.sub(r'(<section [^>]*?)data-start="([\d.]+)" data-duration="([\d.]+)"', clip, html)
html = html.replace('data-duration="21.7"', f'data-duration="{DUR}"')   # root + audio
open("hyperframes/index.html", "w").write(html)

subprocess.run([sys.executable, "../make_cues.py", ".", str(EST_DUR), "accents.json"], check=True, cwd=".", capture_output=True)
cues = json.load(open("cues.json"))
cues["duration"] = DUR
cues["events"] = [[round(W(t), 3), n, g] for t, n, g in cues["events"]]
cues["dropouts"] = [[round(W(a), 3), round(W(b), 3)] for a, b in cues.get("dropouts", [])]
json.dump(cues, open("cues.json", "w"), indent=1)
print(f"duration {EST_DUR} -> {DUR}; scenes:", [round(W(t), 2) for t in (2.95, 4.9, 8.08, 9.65, 11.05, 16.0, 18.4)])
