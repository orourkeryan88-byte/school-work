"""Build cues.json (SFX timing) for a HyperFrames ad: one soft tick per caption word, read straight from the
words() calls in index.html, plus the hand-placed accents passed in (whooshes, hits, pops, risers).
    python3 make_cues.py <project dir> <duration> accents.json"""
import json, re, sys
from html.parser import HTMLParser

proj, dur, acc = sys.argv[1], float(sys.argv[2]), json.load(open(sys.argv[3]))
html = open(f"{proj}/hyperframes/index.html").read()


class Counter(HTMLParser):
    """count the .w word spans inside each caption id"""
    def __init__(self):
        super().__init__(); self.stack = []; self.counts = {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cid = a.get("id"); self.stack.append(cid)
        if "w" in (a.get("class") or "").split():
            for c in self.stack:
                if c and re.fullmatch(r"c\d+[a-z]?", c): self.counts[c] = self.counts.get(c, 0) + 1
    def handle_endtag(self, tag):
        if self.stack: self.stack.pop()


cnt = Counter(); cnt.feed(html)
events = []
for m in re.finditer(r'words\("#(c\w+)",\s*([\d.]+)(?:,\s*([\d.]+))?(?:,\s*\[([^\]]*)\])?\)', html):
    cid, t0, step, times = m.group(1), float(m.group(2)), float(m.group(3) or 0.3), m.group(4)
    ts = [float(x) for x in times.split(",")] if times else [t0 + i * step for i in range(cnt.counts.get(cid, 0))]
    events += [[round(t, 3), "tick", 0.07] for t in ts]
events += acc["events"]
events.sort(key=lambda e: e[0])
json.dump({"duration": dur, "bpm": acc.get("bpm", 124), "dropouts": acc.get("dropouts", []), "events": events},
          open(f"{proj}/cues.json", "w"), indent=1)
print(proj, len(events), "events")
