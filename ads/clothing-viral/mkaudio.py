"""Soundtrack for one reel: its spliced voice (vN/vo.wav) over the shared music bed (shared/bed.mp3), ducked ~9 dB under
the voice, plus the SFX in vN/cues.json (whoosh into every shot, ticks under words, pops/hits on graphics, riser into the
end card). Mastered to -14 LUFS.      python3 mkaudio.py v1 [v2 v3]"""
import subprocess, sys
for n in sys.argv[1:] or ("v1", "v2", "v3"):
    run = lambda *a: subprocess.run(a, check=True)
    run("ffmpeg", "-loglevel", "error", "-y", "-i", f"{n}/vo.wav", "-af", "loudnorm=I=-12:TP=-1:LRA=7", "-ar", "44100", "-ac", "1", f"{n}/vo_lev.wav")
    run("python3", "build_audio.py", f"{n}/cues.json", f"{n}/vo_lev.wav", "--music", "shared/bed.mp3", "--bed-db", "-4", "-o", f"{n}/mix_tmp.wav")
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{n}/mix_tmp.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float([l for l in o.splitlines() if l.strip().startswith("I:")][-1].split()[1])
    run("ffmpeg", "-loglevel", "error", "-y", "-i", f"{n}/mix_tmp.wav", "-af", f"volume={-15 - I:.2f}dB,alimiter=limit=0.89", "-ar", "44100", "-ac", "2", f"{n}/hyperframes/assets/audio.wav")
    run("rm", "-f", f"{n}/mix_tmp.wav")
    o = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{n}/hyperframes/assets/audio.wav", "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    print(n, [l.strip() for l in o.splitlines() if l.strip().startswith(("I:", "Peak:"))][-2:])
