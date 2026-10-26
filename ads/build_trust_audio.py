"""music beds shared by the trust + e-commerce videos: a soft synth bed, or a song looped to length"""
import subprocess, wave
import numpy as np
import adkit as A


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
    """background song from a file: the clean stretch [start, end] looped with a long crossfade, cut to the video
    length, faded in and out"""
    seg = f"atrim={start}:{end},asetpts=PTS-STARTPTS"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", src, "-filter_complex",
                    f"[0:a]{seg}[a];[1:a]{seg}[b];[a][b]acrossfade=d={xf}:c1=tri:c2=tri,atrim=0:{total},afade=t=in:d=1.2,afade=t=out:st={total - 3}:d=3,aformat=channel_layouts=mono[m]",
                    "-map", "[m]", "-ar", str(A.SR), path], check=True)
