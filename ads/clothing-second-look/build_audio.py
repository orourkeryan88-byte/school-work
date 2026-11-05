#!/usr/bin/env python3
"""Score builder for Southline video ads (Southline Edit Style §7).

    python3 build_audio.py cues.json [vo.mp3] -o out.wav

cues.json:
    {"duration": 25.6, "bpm": 124, "dropouts": [[19.19, 19.44]],
     "events": [[0.24, "hit", 0.6], [4.1, "whoosh", 0.55], [1.2, "tick", 0.07], ...]}

Voices: ping pop click tick coin whoosh swish hit shimmer glitch riser.
Bed: kick on beats, offbeat hats, a short sub-bass line (A F C G, one note per bar), soft pad.
With a VO the music ducks ~9 dB under speech (20 ms attack / 150 ms release).
Output is loudness-normalised to -14 LUFS integrated, -1 dBTP, stereo 44.1 kHz.
Needs numpy and ffmpeg.
"""
import argparse, json, subprocess, tempfile, wave
import numpy as np

SR = 44100


def synth():
    rng = np.random.default_rng(7)
    tt = lambda d: np.arange(int(d * SR)) / SR
    S = {}

    def lpf(x, a):
        y = np.empty_like(x); acc = 0.0
        for i in range(len(x)):
            acc += (a[i] if hasattr(a, "__len__") else a) * (x[i] - acc); y[i] = acc
        return y

    def kick(d=0.35):
        t = tt(d); f = 45 + 110 * np.exp(-t * 28)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

    t = tt(0.5); S["ping"] = (np.sin(2 * np.pi * 1568 * t) * np.exp(-t * 9) + 0.6 * np.sin(2 * np.pi * 2349 * t) * np.exp(-t * 12) * (t > 0.07)) * 0.35
    t = tt(0.18); S["pop"] = np.sin(2 * np.pi * np.cumsum(300 + 900 * np.exp(-t * 40)) / SR) * np.exp(-t * 30) * 0.5
    t = tt(0.05); S["click"] = np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120) * 0.6 + rng.standard_normal(len(t)) * np.exp(-t * 200) * 0.2
    t = tt(0.03); S["tick"] = np.sin(2 * np.pi * 3000 * t) * np.exp(-t * 250) * 0.4
    t = tt(0.35); S["coin"] = (np.sin(2 * np.pi * 1975 * t) * np.exp(-t * 14) * (t < 0.08) + np.sin(2 * np.pi * 2637 * t) * np.exp(-(t - 0.08).clip(0) * 7) * (t >= 0.08)) * 0.32
    nz = rng.standard_normal(int(0.45 * SR)).astype(np.float32)
    S["whoosh"] = lpf(nz, np.linspace(0.02, 0.35, len(nz)) ** 1.2) * np.sin(np.linspace(0, np.pi, len(nz))) ** 2 * 0.9
    S["swish"] = S["whoosh"][::2] * 0.7
    t = tt(0.6); S["hit"] = kick(0.6) * 0.9 + lpf(rng.standard_normal(len(t)).astype(np.float32), 0.25) * np.exp(-t * 14) * 0.35
    t = tt(0.9); S["shimmer"] = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 4) for f in (2093, 2637, 3136)) * np.minimum(t / 0.05, 1) * 0.08
    t = tt(0.25); S["glitch"] = np.sign(np.sin(2 * np.pi * 180 * t)) * (rng.random(len(t)) > 0.4) * np.exp(-t * 10) * 0.18
    rn = rng.standard_normal(int(0.6 * SR)).astype(np.float32)
    S["riser"] = np.convolve(rn, np.ones(30) / 30, "same") * np.linspace(0, 1, len(rn)) ** 2 * 0.5
    S["kick"] = kick()
    hn = rng.standard_normal(int(0.06 * SR)); hn = hn - np.concatenate([[0], hn[:-1]])
    S["hat"] = hn * np.exp(-np.arange(len(hn)) / SR / 0.015) * 0.25
    return S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cues"); ap.add_argument("vo", nargs="?"); ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    cue = json.load(open(a.cues))
    D = float(cue["duration"]); bpm = float(cue.get("bpm", 124)); B = 60 / bpm
    N = int(D * SR); t = np.arange(N) / SR; V = synth()
    music = np.zeros(N + SR, np.float32); sfx = np.zeros(N + SR, np.float32); vo = np.zeros(N + SR, np.float32)

    def add(buf, sig, at, g):
        s = int(at * SR); e = min(len(buf), s + len(sig))
        if e > s: buf[s:e] += sig[:e - s] * g

    roots = [55.0, 43.65, 65.41, 49.0]
    b, i = 0.0, 0
    while b < D - 0.3:
        add(music, V["kick"], b, 0.42); add(music, V["hat"], b + B / 2, 0.38)
        if i % 2 == 0:
            f = roots[(i // 4) % 4]; n = int(B * 0.95 * SR); x = np.arange(n) / SR
            add(music, (np.sin(2 * np.pi * f * x) + 0.25 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 2.2) * 0.32, b, 1.0)
        b += B; i += 1
    music[:N] += sum(np.sin(2 * np.pi * f * t) for f in (220.0, 261.63, 329.63)) * 0.012 * np.clip(t / 2, 0, 1) * np.clip((D - t) / 1.5, 0, 1)
    for d0, d1 in cue.get("dropouts", []):
        music[int(d0 * SR):int(d1 * SR)] *= 0.05
    for at, name, g in cue.get("events", []):
        add(sfx, V[name], float(at), float(g))

    if a.vo:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.vo, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        v = np.frombuffer(raw, np.float32); vo[:min(len(v), len(vo))] = v[:len(vo)]
        w = int(0.03 * SR); env = np.sqrt(np.convolve(vo ** 2, np.ones(w) / w, "same"))
        talk = (env > 0.02).astype(np.float32); g = np.zeros_like(talk)
        ac, rc = np.exp(-1 / (0.02 * SR)), np.exp(-1 / (0.15 * SR)); prev = 0.0
        for k in range(len(talk)):
            c = ac if talk[k] > prev else rc; prev = c * prev + (1 - c) * talk[k]; g[k] = prev
        music *= 10 ** (-9 * g / 20)

    mix = (music + sfx * 0.9 + vo)[:N]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    tmp = tempfile.mktemp(suffix=".wav")
    with wave.open(tmp, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(mix / max(1e-6, np.abs(mix).max()) * 0.9, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1:LRA=9", "-ar", str(SR), "-ac", "2", a.out], check=True)
    print(f"wrote {a.out} ({D}s, VO: {'yes' if a.vo else 'no'})")


if __name__ == "__main__":
    main()
