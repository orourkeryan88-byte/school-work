"""Soundtrack for the Dec film: cues (SFX on cuts, problems, fixes, phone, stamp, toggle...) + the 124 BPM bed,
ducked ~9 dB under the voiceover, music out for 0.25 s before "Book a call.", final mix -14 LUFS / -1 dBTP.
    python3 mkaudio.py      (reads timing.json + vo.wav, writes cues.json + hyperframes/assets/audio.wav)"""
import json, subprocess
T = json.load(open("timing.json")); S = T["scenes"]
st = lambda i: S[i]["start"]; wt = lambda i, k: S[i]["words"][k]["start"]
ev = []
E = lambda t, n, g: ev.append([round(t, 3), n, g])
inner = [[0, 11, -0.05], [4, 15, -0.12], [7, 14, -0.12], [7, 18, -0.25], [8, 7, -0.15], [11, 5, -0.1], [11, 11, -0.1], [12, 14, -0.25]]
for i in range(1, 15): E(st(i) - 0.15, "whoosh", 0.55)
for i, k, o in inner: E(wt(i, k) + o - 0.15, "whoosh", 0.5)
for i in [3, 5, 7, 9, 11]: E(wt(i, 0), "kick", 1.0); E(wt(i, 0), "hit", 0.3)          # sub thump on each "Problem"
for i in [4, 6, 8, 10, 12]: E(wt(i, 0), "shimmer", 0.9)                                 # shimmer on each "Fix"
for i, k in [(4, 19), (6, 16), (8, 21), (10, 15), (12, 15)]: E(wt(i, k), "coin", 0.35)   # HUD counters roll
# 1 launch: suspension bump, click on publish, ping when live; rain + lamp hum in the office
E(1.2, "knock", 0.5); E(1.45, "pop", 0.3); E(wt(0, 17), "click", 0.9); E(wt(0, 18), "ping", 0.6)
E(wt(0, 11) - 0.05, "rain", 0.8); E(wt(0, 11) - 0.05, "hum", 1.0)
# 2 refresh click, the zero lands
E(wt(1, 2), "click", 0.8); E(wt(1, 4), "pop", 0.5)
# 3 dominoes tap down one by one, HUD swishes in
for i in range(5): E(st(2) + 0.5 + i * 0.62 + 0.55, "knock", 0.55)
E(wt(2, 10), "swish", 0.5)
# 4 cards fly out of the phone
E(wt(3, 5), "swish", 0.4); E(wt(3, 7), "swish", 0.5)
# 5 ticks, then the phone won't stop
E(wt(4, 9), "pop", 0.45); E(wt(4, 13), "pop", 0.45)
for k in (16, 17, 18, 19): E(wt(4, k), "buzz", 0.8); E(wt(4, k) + 0.05, "ping", 0.35)
# 6 messages ping, JUNK stamp slams
for k in (2, 5, 7): E(wt(5, k), "ping", 0.4)
E(wt(5, 9) + 0.15, "hit", 1.0); E(wt(5, 9) + 0.15, "clunk", 0.5)
# 7 ad card rises, tiles pop, the good five glow
E(wt(6, 8) - 0.25, "swish", 0.45); E(wt(6, 12), "pop", 0.4); E(wt(6, 14), "pop", 0.4); E(wt(6, 15), "swish", 0.35); E(wt(6, 16), "shimmer", 0.6)
# 8 taps on submit, sign flips, knocks at the door
E(wt(7, 8), "click", 0.8); E(wt(7, 13), "click", 0.8); E(wt(7, 17) - 0.25, "swish", 0.5)
for k in range(3): E(wt(7, 18) - 0.2 + k * 0.35, "knock", 0.8)
# 9 play pulse, checklist pops, thumbs up
E(wt(8, 3), "pop", 0.4)
for k in (7, 10, 14): E(wt(8, k), "pop", 0.5)
# 10 phone buzzes on the landing, missed call, clock spins, he lands, the text
E(wt(9, 4), "buzz", 0.7); E(wt(9, 4) + 0.45, "buzz", 0.6); E(wt(9, 11), "glitch", 0.4); E(wt(9, 12) - 0.1, "riser", 0.35)
E(wt(9, 14) + 0.35, "hit", 0.5); E(wt(9, 14) + 0.45, "ping", 0.45)
# 11 milestones rise
for k in (5, 9, 12): E(wt(10, k), "pop", 0.5)
# 12 toggle clunk OFF, calendar pages flip
E(wt(11, 10), "clunk", 1.0)
for i in range(3): E(wt(11, 11) + 0.05 + i * 0.32, "swish", 0.4)
# 13 toggle ON, padlock clicks shut, job cards, best job
E(wt(12, 0), "clunk", 0.7); E(wt(12, 4), "click", 1.0); E(wt(12, 4), "hit", 0.4)
for k in (5, 6, 7): E(wt(12, k) - 0.05, "pop", 0.45)
E(wt(12, 12), "shimmer", 0.5)
# 14 blocks thud onto the tower, jump, glow
for k in range(5): E(wt(13, k) + 0.2, "hit", 0.45)
E(wt(13, 6) - 0.25, "swish", 0.5); E(wt(13, 9), "shimmer", 0.7)
# 15 riser into the end card, one clean final hit on "Book"
E(st(14) - 0.6, "riser", 0.7); E(wt(14, 6) - 0.05, "hit", 1.0)
ev.sort(key=lambda e: e[0])
json.dump({"duration": T["duration"], "bpm": 124, "events": ev, "dropouts": [[round(wt(14, 6) - 0.25, 3), round(wt(14, 6), 3)]]}, open("cues.json", "w"), indent=0)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "vo.wav", "-af", "highpass=f=70,loudnorm=I=-12:TP=-1:LRA=7", "-ar", "44100", "-ac", "1", "vo_lev.wav"], check=True)
subprocess.run(["python3", "build_audio.py", "cues.json", "vo_lev.wav", "--bed-db", "-4", "-o", "hyperframes/assets/audio.wav"], check=True)
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", "hyperframes/assets/audio.wav", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in out.splitlines() if l.strip().startswith("I:")][-1].split()[1])
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", "hyperframes/assets/audio.wav", "-af", f"volume={-14 - I:.2f}dB", "-ar", "44100", "-ac", "2", "audio_tmp.wav"], check=True)
subprocess.run(["mv", "audio_tmp.wav", "hyperframes/assets/audio.wav"], check=True)
out = subprocess.run(["ffmpeg", "-hide_banner", "-i", "hyperframes/assets/audio.wav", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
print([l.strip() for l in out.splitlines() if l.strip().startswith(("I:", "Peak:"))][-2:], len(ev), "events")
