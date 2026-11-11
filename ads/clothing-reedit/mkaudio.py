"""Soundtrack: the separated voice (vo.wav) over an original 124 BPM bed; whoosh on every visual change, sub hit on the
hook, faint ticks on caption words, pops on the grid/list beats, riser + 0.25 s drop-out into the end card. -14 LUFS.
    python3 mkaudio.py"""
import json, subprocess
T = json.load(open("timing.json")); S = {s["id"]: s for s in T["segments"]}
W = lambda sid: [w["start"] for w in T["words"] if w["seg"] == sid]
ev = []; E = lambda t, n, g: ev.append([round(t, 3), n, g])
prev = None
for s in T["segments"]:
    v = s["vis"][0] if s["vis"][0] != "card" else "card" + s["src"]
    if prev and v != prev: E(s["start"] - 0.12, "whoosh", 0.45)
    prev = v
for w in T["words"]: E(w["start"], "tick", 0.06)
for k in ("ad1", "ad2", "ad3"): E(W(k)[-1], "hit", 0.45)
E(W("only")[-1], "hit", 0.8); E(W("only")[-1] + 0.02, "shimmer", 0.5)
E(S["make"]["start"], "swish", 0.4)
for i in range(15): E(S["make"]["start"] + 0.05 + min(i, 9) * 0.07 if i < 10 else S["make_ads"]["start"] - 0.05 + (i - 10) * 0.06, "pop", 0.18)
E(W("kill")[1], "glitch", 0.35); E(W("kill")[4], "shimmer", 0.6)
for n in range(6): E(W("kill")[8] + n * 0.08, "pop", 0.2)
for k in (3, 6, 10): E(W("offer")[k] - 0.08, "pop", 0.4)
E(W("experiment")[5], "hit", 0.6)
cta = S["cta"]["start"]
E(cta - 0.7, "riser", 0.6); E(W("cta")[1], "hit", 0.9); E(W("cta")[-1] + 0.3, "coin", 0.4)
ev.sort(key=lambda e: e[0])
json.dump({"duration": T["duration"], "bpm": 124, "events": ev, "dropouts": [[round(cta - 0.27, 3), round(cta - 0.02, 3)]]}, open("cues.json", "w"), indent=0)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "vo.wav", "-af", "highpass=f=70,loudnorm=I=-12:TP=-1:LRA=7", "-ar", "44100", "-ac", "1", "vo_lev.wav"], check=True)
subprocess.run(["python3", "build_audio.py", "cues.json", "vo_lev.wav", "--bed-db", "-5", "-o", "mix_tmp.wav"], check=True)
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "mix_tmp.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in o.splitlines() if l.strip().startswith("I:")][-1].split()[1])
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "mix_tmp.wav", "-af", f"volume={-14 - I:.2f}dB", "-ar", "44100", "-ac", "2", "hyperframes/assets/audio.wav"], check=True)
subprocess.run(["rm", "-f", "mix_tmp.wav"])
o = subprocess.run(["ffmpeg", "-hide_banner", "-i", "hyperframes/assets/audio.wav", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print([l.strip() for l in o.splitlines() if l.strip().startswith(("I:", "Peak:"))][-2:], len(ev), "events")
