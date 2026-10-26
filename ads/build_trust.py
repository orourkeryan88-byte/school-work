"""Southline TRUST video: code-drawn B-roll (broll.py) under every line + animations, timed to the voiceover script
(read at a natural pace, ~64s). No voice baked in: Ryan records the VO over it. Music bed (--music <file>, else a soft
synth bed) + quiet SFX, mastered low (-22 LUFS) so a voiceover sits on top.
python3 build_trust.py [--stills] [--music song.mp4] [--remix = audio only, onto the existing video]"""
import sys, os, subprocess, wave
import numpy as np
from PIL import Image
import adkit as A
import trust_scenes as S
import broll as B

A.set_theme("midnight", accent=S.ACC, accent2=S.ACC, bg=((8, 10, 14), (4, 5, 8)), blobs=[], grid=False)

# (scene, script line it carries) - durations = the line read at a relaxed pace + a breath
SPEED = 1.1  # everything runs 10% quicker than the relaxed read (Ryan asked for a touch faster)

def w(scene, shots):
    """scene over its B-roll shot, sped up by SPEED: shorter duration, animations and SFX times compressed evenly"""
    dur, fn, ev = S.with_shot(scene, shots)
    return dur / SPEED, (lambda t: fn(t * SPEED)), [(a_ / SPEED, n_, g_) for a_, n_, g_ in ev]
# (scene over its B-roll shot, script line it carries) - durations = the line read at a relaxed pace + a breath
SCENES = [
    (w(S.scene_intro(dur=4.8), B.van_road), "Tradesmen in Ireland and the UK. I'm Ryan. I run a marketing agency,"),
    (w(S.scene_common(dur=3.0), B.van_road), "and the biggest question I get asked is…"),
    (w(S.scene_question(dur=3.3), B.desk), "'Do Facebook ads actually work for tradesmen?'"),
    (w(S.scene_short(dur=5.2), B.phone_feed), "Short answer? Yeah, when they're done properly. Boosting a post isn't the same thing."),
    (w(S.scene_title("01", ["So what do we", "actually do?"], 9.0, 1.3, 0.6, 0.6, dur=2.3), B.van_road), "So what do we actually do?"),
    (w(S.scene_what(dur=4.6), B.dashboard), "We run Facebook and Instagram ads for trades and local businesses in Ireland and the UK."),
    (w(S.scene_trades(dur=3.6), B.van_road), "Plumbers, builders, electricians, kitchen and bathroom fitters."),
    (w(S.scene_aim(dur=4.4), B.map_), "The aim's simple: get people in your area asking you for a quote."),
    (w(S.scene_title("02", ["So how do we", "actually do it?"], 5.0, 1.3, 0.5, 0.45, dur=2.3), B.dashboard), "So how do we actually do it?"),
    (w(S.scene_how(dur=7.0), [(0.0, B.site), (3.5, B.desk)]), "We take your real work, your photos and your before-and-afters, and show it to homeowners in the area you cover."),
    (w(S.scene_questions(dur=4.6), B.phone_feed), "Before anyone gets in touch, they answer a few quick questions about the job."),
    (w(S.scene_phone(dur=3.8), B.desk), "Then it lands straight on your phone, and you ring them back."),
    (w(S.scene_title("03", ["And who's", "it for?"], 2.0, 1.2, 0.5, 0.5, dur=1.8, chips=[["Plumbers", "Electricians", "Builders"], ["Kitchen & bathroom fitters"]], hi_chip="Electricians"), B.map_), "And who's it for?"),
    (w(S.scene_wom(dur=6.2), B.site), "Tradesmen still relying on word of mouth, and struggling to get booked out. That's who we help."),
    (w(S.scene_end(dur=4.4), B.van_road), "That's it. No magic, just ads done properly."),
]

if "--stills" in sys.argv:
    for i, ((dur, fn, _), _) in enumerate(SCENES):
        row = [fn(x)[0].convert("RGB").resize((270, 480)) for x in (0.0, dur * 0.5, dur - 0.2)]
        sheet = Image.new("RGB", (270 * 3, 480)); [sheet.paste(r_, (270 * j, 0)) for j, r_ in enumerate(row)]
        sheet.save(f"out/still_{i + 1:02d}.png")
    sys.exit()


def music_bed(dur, path, bpm=84):
    """soft background music: warm pad chords (Cmaj7 Am7 Fmaj7 G6) + a quiet plucked arpeggio + a light kick on 1 and 3"""
    sr = A.SR; n = int(dur * sr); t = np.arange(n) / sr; out = np.zeros(n, np.float32); beat = 60 / bpm; bar = beat * 4
    chords = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 329.6]]
    for b in range(int(dur / bar) + 1):
        ch = chords[b % 4]; s0 = int(b * bar * sr); s1 = min(n, int((b + 1) * bar * sr) + int(0.5 * sr))
        if s0 >= n: break
        tt = np.arange(s1 - s0) / sr; env = np.minimum(tt / 0.6, 1) * np.exp(-np.maximum(tt - bar, 0) * 6)
        for f in ch:
            out[s0:s1] += (np.sin(2 * np.pi * f / 2 * tt) * 0.5 + np.sin(2 * np.pi * f * tt + 0.3) * 0.25) * env * 0.05
        for k in range(8):  # pluck arpeggio on eighths
            p0 = s0 + int(k * beat / 2 * sr); f = ch[[0, 1, 2, 3, 2, 1, 2, 3][k]] * 2
            if p0 >= n: break
            pt = np.arange(min(int(0.6 * sr), n - p0)) / sr; out[p0:p0 + len(pt)] += np.sin(2 * np.pi * f * pt) * np.exp(-pt * 7) * 0.035
        for k in (0, 2):  # soft kick
            p0 = s0 + int(k * beat * sr)
            if p0 >= n: break
            pt = np.arange(min(int(0.3 * sr), n - p0)) / sr; out[p0:p0 + len(pt)] += np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-pt * 30)) / sr) * np.exp(-pt * 12) * 0.18
    out *= np.minimum(t / 1.5, 1) * np.clip((dur - t) / 2.0, 0, 1)  # fade in / out
    out /= np.abs(out).max() / 0.7
    with wave.open(path, "wb") as wf: wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((out * 32767).astype(np.int16).tobytes())


def song_bed(total, src, path, start=1.5, end=40.5, xf=4.0):
    """background song from a file: the clean stretch [start, end] looped once with a long crossfade, cut to the
    video length, faded in and out"""
    seg = f"atrim={start}:{end},asetpts=PTS-STARTPTS"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", src, "-filter_complex",
                    f"[0:a]{seg}[a];[1:a]{seg}[b];[a][b]acrossfade=d={xf}:c1=tri:c2=tri,atrim=0:{total},afade=t=in:d=1.2,afade=t=out:st={total - 3}:d=3,aformat=channel_layouts=mono[m]",
                    "-map", "[m]", "-ar", str(A.SR), path], check=True)


def mix_onto(video_in, sfx_in, bed, out):
    """music under, SFX quieter on top; the whole bed is mastered low so Ryan's voiceover sits clearly above it"""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video_in, "-i", sfx_in, "-i", bed, "-filter_complex",
                    "[1:a]volume=0.4[s];[2:a]volume=1.0[m];[s][m]amix=inputs=2:normalize=0,lowpass=f=15000,loudnorm=I=-22:TP=-3:LRA=11,aresample=48000[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)


# --music <file>: use that song as the bed (e.g. the clean audio from a screen recording); default = the synth bed
MUSIC = sys.argv[sys.argv.index("--music") + 1] if "--music" in sys.argv else None
v = A.Video(); [v.add(*s) for s, _ in SCENES]
out = "out/southline_trust_ryan.mp4"; bed = "out/_trust_music.wav"
if "--remix" in sys.argv:  # audio only: rebuild the SFX + music and swap them onto the existing video (no frame render)
    total = v.render("out/_trust_sfx.m4a", music=False, lufs=None, audio_only=True)
    song_bed(total, MUSIC, bed) if MUSIC else music_bed(total, bed)
    tmp = out.replace(".mp4", "_tmp.mp4"); mix_onto(out, "out/_trust_sfx.m4a", bed, tmp); os.replace(tmp, out)
    os.remove("out/_trust_sfx.m4a"); os.remove(bed); print(f"remixed {total:.2f}s"); sys.exit()
raw = "out/_trust_raw.mp4"
ends, t = [], 0
for (d, _, _), _ in SCENES: t += round(d * A.FPS) / A.FPS; ends.append(t - 0.4)
total = v.render(raw, transition="whip", tr_frames=4, preview_times=ends, music=False, lufs=None, punch=False, drift=0.0)
song_bed(total, MUSIC, bed) if MUSIC else music_bed(total, bed)
mix_onto(raw, raw, bed, out); os.remove(bed)
os.replace(raw.replace(".mp4", "_preview.png"), out.replace(".mp4", "_preview.png")); os.remove(raw)
print(f"rendered {total:.2f}s")
cue, t = [], 0.0
for (d, _, _), line in SCENES: cue.append(f"{int(t // 60)}:{t % 60:05.2f}  {line}"); t += round(d * A.FPS) / A.FPS
open("out/southline_trust_ryan_cues.txt", "w").write("\n".join(cue) + "\n"); print("\n".join(cue))
