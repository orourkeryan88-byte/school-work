"""Local voiceover (no ElevenLabs credits): Piper neural TTS, any Piper voice (model + speaker given).
    python local_vo.py <piper_bin> <model.onnx> <speaker> "<script>" <out_prefix>
Reads the script phrase by phrase (split on . ? , :), trims each phrase's silence, joins them with natural pauses,
and writes <out_prefix>.wav plus <out_prefix>_words.json with a start/end per word (phrase timing is exact; words
inside a phrase are spread by syllable count)."""
import json, re, subprocess, sys, wave, tempfile, os
import numpy as np
piper, model, spk, text, out = sys.argv[1:6]
SR = 22050
phrases = [p.strip() for p in re.findall(r"[^.?,:!…]+[.?,:!…]*", text) if p.strip()]
def syl(w):
    k = re.sub(r"[^a-z']", "", w.lower()); n = len(re.findall(r"[aeiouy]+", k)) - (1 if k.endswith("e") and len(k) > 3 and not k.endswith("le") else 0)
    return max(1, n)
audio, words, t = [np.zeros(int(0.15 * SR), np.float32)], [], 0.15
for i, ph in enumerate(phrases):
    fn = tempfile.mktemp(suffix=".wav")
    subprocess.run([piper, "-m", model, "-s", str(spk), "--length-scale", "0.97", "-f", fn], input=ph.encode(), capture_output=True, check=True)
    w = wave.open(fn); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; os.remove(fn)
    env = np.convolve(np.abs(x), np.ones(441) / 441, "same"); on = np.where(env > 0.01)[0]
    x = x[max(0, on[0] - 220):min(len(x), on[-1] + 660)]
    dur = len(x) / SR; ws = ph.split(); tot = sum(syl(v) for v in ws); u = t
    for v in ws:
        d = dur * syl(v) / tot; words.append({"text": v, "start": round(u, 3), "end": round(u + d, 3)}); u += d
    audio.append(x); t += dur
    gap = 0.34 if ph.endswith((".", "?", "!", "…")) else 0.16 if ph.endswith((",", ":")) else 0.08
    if i < len(phrases) - 1: audio.append(np.zeros(int(gap * SR), np.float32)); t += gap
y = np.concatenate(audio + [np.zeros(int(0.2 * SR), np.float32)])
with wave.open(out + ".wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump({"voice": f"Piper {os.path.basename(model)} speaker {spk}", "words": words}, open(out + "_words.json", "w"), indent=0)
print(out, round(t, 2), "s,", len(words), "words")
