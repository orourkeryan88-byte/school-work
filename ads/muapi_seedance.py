"""Generate a video with Seedance 2 through MuAPI (the engine behind Open Generative AI), from the command line.

    MUAPI_KEY must be set in the environment (never paste it into a file or the chat).
    python3 muapi_seedance.py prompt.txt out.mp4 [--duration 15] [--aspect 9:16] [--model seedance-2-text-to-video]

Same calls the app makes (packages/studio/src/muapi.js): POST /api/v1/<model> with x-api-key, then poll
/api/v1/predictions/<request_id>/result until it has an output URL, then download it.
Each run spends MuAPI credits."""
import argparse, json, os, sys, time, urllib.request

BASE = "https://api.muapi.ai"


def call(method, url, key, body=None):
    req = urllib.request.Request(url, method=method, headers={"Content-Type": "application/json", "x-api-key": key},
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt_file"); ap.add_argument("out")
    ap.add_argument("--duration", type=int, default=15); ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--model", default="seedance-2-text-to-video")
    a = ap.parse_args()
    key = os.environ.get("MUAPI_KEY")
    if not key: sys.exit("MUAPI_KEY is not set")
    prompt = open(a.prompt_file).read().strip()
    sub = call("POST", f"{BASE}/api/v1/{a.model}", key, {"prompt": prompt, "aspect_ratio": a.aspect, "duration": a.duration})
    rid = sub.get("request_id") or sub.get("id")
    print("submitted", rid, flush=True)
    for _ in range(900):                                  # up to ~30 min, polled every 2 s like the app
        time.sleep(2)
        res = call("GET", f"{BASE}/api/v1/predictions/{rid}/result", key)
        status = str(res.get("status", "")).lower()
        url = (res.get("outputs") or [None])[0] or res.get("url") or (res.get("output") or {}).get("url")
        if url:
            urllib.request.urlretrieve(url, a.out); print("saved", a.out, flush=True); return
        if status in ("failed", "error", "cancelled"):
            sys.exit(f"generation failed: {json.dumps(res)[:400]}")
    sys.exit("timed out waiting for the video")


if __name__ == "__main__":
    main()
