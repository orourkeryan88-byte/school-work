"""Estimate when each voiceover word is spoken, so captions can be built before the real recording exists.
Each line gets a window (start, end); words share it by syllable count, with short pauses after , ? and .
When the real VO arrives, replace vo_words.json with the transcription's word times and re-time the captions.
    python3 vo_timing.py   -> writes vo_words.json and prints the table"""
import json, re

LINES = [  # (start, end, text): windows follow the brief's shot timings
    (0.10, 3.10, "This is what Q4 looks like when you run your clothing brand's ads yourself."),
    (3.25, 4.85, "And here's what nobody tells you."),
    (5.05, 9.35, "Every brand is fighting for the same feeds right now, so your ads cost more."),
    (10.05, 13.75, "Same ad for weeks? People scroll past it. Sales slow down mid-rush."),
    (14.05, 18.80, "And everyone who added to cart and left? No retargeting, no emails, they're gone."),
    (19.05, 21.80, "That's not a product problem. It's a system problem."),
    (22.05, 28.70, "Southline runs your Facebook and Instagram ads. Fresh creatives, proper tracking, retargeting. Plus the emails that bring buyers back."),
    (29.15, 30.45, "You focus on the clothes."),
    (31.05, 32.75, "Comment Q4 and we'll show you how."),
]
SYL = {"q4": 2, "everyone": 3, "every": 2, "instagram": 3, "facebook": 2, "southline": 2, "retargeting": 4,
       "creatives": 3, "emails": 2, "nobody": 3, "yourself": 2, "clothes": 1, "here's": 1, "they're": 1, "that's": 1}

def syl(w):
    k = re.sub(r"[^a-z0-9']", "", w.lower())
    if k in SYL: return SYL[k]
    n = len(re.findall(r"[aeiouy]+", k)) - (1 if k.endswith("e") and not k.endswith("le") and len(k) > 3 else 0)
    return max(1, n)

out = []
for li, (t0, t1, text) in enumerate(LINES):
    ws = text.split()
    pause = [0.28 if w.endswith((".", "?")) and i < len(ws) - 1 else 0.16 if w.endswith(",") else 0 for i, w in enumerate(ws)]
    unit = (t1 - t0 - sum(pause)) / sum(syl(w) for w in ws)
    t = t0
    for w, p in zip(ws, pause):
        out.append({"line": li + 1, "word": w, "start": round(t, 2)}); t += syl(w) * unit + p
    print(f"L{li+1} {t0:5.2f}-{t1:5.2f}  {sum(syl(w) for w in ws)} syl  {sum(syl(w) for w in ws)/(t1-t0-sum(pause)):.1f} syl/s  {len(ws)} words")
json.dump(out, open("vo_words.json", "w"), indent=0)
print(sum(len(l[2].split()) for l in LINES), "words")
for li in range(1, 10): print(li, " ".join(f"{o['word']}@{o['start']}" for o in out if o["line"] == li))
