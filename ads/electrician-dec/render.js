// Parallel renderer for this composition (the stock HyperFrames capture was ~5 s/frame here with software WebGL).
// Each worker opens index.html, seeks the GSAP timeline frame by frame (clips shown/hidden by data-start/duration,
// exactly as HyperFrames does), screenshots, and pipes JPEGs into its own ffmpeg segment. Then: concat + the mix.
//   NODE_PATH=$(npm root -g) node render.js hyperframes/index.html out.mp4 [workers=4] [fps=30]
const { chromium } = require("playwright"), { spawn, execFileSync } = require("child_process"), fs = require("fs"), path = require("path");
const [, , file, out, W = "4", F = "30"] = process.argv, workers = +W, fps = +F;
const html = fs.readFileSync(file, "utf8"), dur = +html.match(/data-composition-id="main"[^>]*data-duration="([\d.]+)"/)[1];
const total = Math.round(dur * fps), dir = path.dirname(path.resolve(out)), tmp = path.join(dir, ".render_tmp");
fs.mkdirSync(tmp, { recursive: true });
(async () => {
  const t0 = Date.now(), per = Math.ceil(total / workers);
  await Promise.all([...Array(workers).keys()].map(async (w) => {
    const a = w * per, b = Math.min(total, a + per); if (a >= b) return;
    const ff = spawn("ffmpeg", ["-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
      "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", path.join(tmp, `seg${w}.mp4`)]);
    const br = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
    const p = await br.newPage({ viewport: { width: 1080, height: 1920 } });
    p.on("pageerror", (e) => console.log(`[w${w}] page error:`, e.message));
    await p.goto("file://" + path.resolve(file)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
    for (let f = a; f < b; f++) {
      const t = f / fps;
      await p.evaluate((t) => { window.__timelines.main.seek(t, false);
        document.querySelectorAll(".clip").forEach((c) => { const s = +c.dataset.start, d = +c.dataset.duration; c.style.visibility = t >= s && t < s + d ? "visible" : "hidden"; }); }, t);
      const buf = await p.screenshot({ type: "jpeg", quality: 94 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
      if ((f - a) % 60 === 0) console.log(`[w${w}] frame ${f - a}/${b - a}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise((r) => ff.on("close", r)); await br.close();
  }));
  const list = path.join(tmp, "list.txt");
  fs.writeFileSync(list, [...Array(workers).keys()].filter((w) => w * per < total).map((w) => `file 'seg${w}.mp4'`).join("\n"));
  execFileSync("ffmpeg", ["-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", list, "-i", path.join(path.dirname(file), "assets/audio.wav"),
    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]);
  fs.rmSync(tmp, { recursive: true, force: true });
  console.log(`done ${out}: ${total} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
})();
