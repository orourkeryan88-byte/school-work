"""Word timings for a single full voiceover take (e.g. a TTS read of the whole script) without a transcription service:
the local per-line Piper reads in vo/ already have word times, so they are concatenated into a reference read and
aligned to the take with DTW on MFCCs; every reference word time is mapped through the path.
    python3 align_take.py vo_liam.mp3      → take_words.json  [{scene, text, start, end}]"""
import json, sys, numpy as np, librosa
take = sys.argv[1]; SR, HOP = 16000, 320
lines = json.load(open("lines.json"))
ref, words, t = [], [], 0.0
for k, _ in lines:
    y, _ = librosa.load(f"vo/{k}.wav", sr=SR); ws = json.load(open(f"vo/{k}_words.json"))["words"]
    words += [{"scene": k, "text": w["text"], "rs": t + w["start"], "re": t + w["end"]} for w in ws]
    ref.append(y); ref.append(np.zeros(int(0.25 * SR), np.float32)); t += len(y) / SR + 0.25
ref = np.concatenate(ref); tk, _ = librosa.load(take, sr=SR)
def feats(y):
    m = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=1024)[1:]
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
A, B = feats(ref), feats(tk)
D, wp = librosa.sequence.dtw(X=A, Y=B, metric="cosine", step_sizes_sigma=np.array([[1, 1], [0, 1], [1, 0]]), weights_mul=np.array([1, 1.2, 1.2]))
wp = wp[::-1]; fr = HOP / SR
ra, ta = wp[:, 0] * fr, wp[:, 1] * fr
m = lambda x: float(np.interp(x, ra, ta))
out = [{"scene": w["scene"], "text": w["text"], "start": round(m(w["rs"]), 3), "end": round(m(w["re"]), 3)} for w in words]
json.dump(out, open("take_words.json", "w"), indent=0)
for k, _ in lines:
    ws = [w for w in out if w["scene"] == k]; print(k, ws[0]["start"], "→", ws[-1]["end"], " ".join(w["text"] for w in ws[:4]))
