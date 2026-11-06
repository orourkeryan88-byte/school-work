"""Accents (SFX) from a compact spec, then cues + mix. python3 mkaudio.py <dir> <vo.wav> '<json spec>'
spec: {"dur": D, "drop": [[a,b]], "ev": [[t, name, gain], ...]}"""
import json, subprocess, sys
d, vo, spec = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
json.dump({"bpm": 123, "dropouts": spec.get("drop", []), "events": spec["ev"]}, open(f"{d}/accents.json", "w"))
subprocess.run([sys.executable, "../../make_cues.py", ".", str(spec["dur"]), "accents.json"], cwd=d, check=True, capture_output=True)
SP = "/tmp/claude-0/-home-user-school-work/3ca0b593-da17-54e1-bf3a-5ab3178f80dc/scratchpad"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vo, "-af", "highpass=f=70,loudnorm=I=-12:TP=-1:LRA=7", "-ar", "44100", "-ac", "1", f"{SP}/vo/{d}.wav"], check=True)
subprocess.run([sys.executable, "../build_audio.py", "cues.json", f"{SP}/vo/{d}.wav", "--music", "../music/bed_a_bright_techhouse.mp3", "--bed-db", "-4", "-o", f"{SP}/{d}_raw.wav"], cwd=d, check=True, capture_output=True)
out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f"{SP}/{d}_raw.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float([l for l in out.splitlines() if l.strip().startswith("I:")][-1].split()[1])
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{SP}/{d}_raw.wav", "-af", f"volume={-14 - I:.1f}dB", f"{d}/hyperframes/assets/audio.wav"], check=True)
print(d, "mix", I, "LUFS -> lifted", round(-14 - I, 1), "dB")
