  // ===== 1 HOOK: the counter spins 0 → 100
  drift("#cam1", 0, 3.2, 0.05);
  tl.fromTo("#hook", { x: -900, filter: "blur(10px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 0.0);
  tl.fromTo("#hmk", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: E.in }, 0.25);
  shake("#cam1", 0.1, 8);
  tl.to("#hook", { y: -30, opacity: 0, duration: 0.15, ease: "power2.in" }, 1.1);
  words("#c1", 0, 0, [1.28, 1.52, 1.92, 2.16, 2.32]); punch("#c1", 2.32);
  tl.fromTo("#odo1", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.25, ease: E.in }, 1.4);
  const steps = [0, 3, 7, 12, 19, 27, 36, 46, 57, 68, 78, 86, 92, 96, 99, 100];
  steps.forEach((v, i) => tl.set("#odo1", { innerText: String(v) }, 1.5 + i * 0.065));
  punch("#odo1", 2.5);

  // ===== 2 "No chance." 100 struck through in orange, the digits crash down
  drift("#cam2", 3.2, 6.5, 0.05);
  words("#c2a", 0, 0, [3.28, 3.52]); under("#u2", 3.52); punch("#c2a", 3.52);
  tl.fromTo("#st2", { scaleX: 0 }, { scaleX: 1, duration: 0.22, ease: E.in }, 3.3);
  shake("#cam2", 3.55, 10);
  [["#d1", -260, -30], ["#d2", 120, 25], ["#d3", 380, -18]].forEach(([d, x, r], i) =>
    tl.to(d, { y: 1100, x: x * 0.3, rotation: r, opacity: 0, duration: 0.6, ease: "power3.in" }, 3.8 + i * 0.07));
  tl.to("#st2", { y: 1100, opacity: 0, duration: 0.6, ease: "power3.in" }, 3.9);
  exit("#c2a", 4.22); tl.to("#u2", { opacity: 0, duration: 0.1 }, 4.22);
  tl.set("#c2b", { opacity: 1 }, 4.28);
  words("#c2b", 0, 0, [4.32, 4.56, 5.28, 5.44, 5.68, 5.92]); punch("#c2b", 5.92);

  // ===== 3 a hundred grey dots; on "a handful of real jobs" most fall away and a handful light up
  drift("#cam3", 6.5, 10.5, 0.05);
  words("#c3a", 0, 0, [6.56, 6.72, 7.12]); under("#u3a", 7.12);
  exit("#c3a", 7.92); tl.to("#u3a", { opacity: 0, duration: 0.1 }, 7.92);
  tl.set("#c3b", { opacity: 1 }, 7.98);
  words("#c3b", 0, 0, [8.16, 8.48, 8.64, 8.84, 9.2, 9.4, 9.6]); under("#u3b", 9.6); punch("#c3b", 9.6);
  tl.fromTo("#gl", { opacity: 0 }, { opacity: 1, duration: 0.2 }, 7.12);
  const grid = document.getElementById("grid"), REAL = [14, 37, 42, 58, 71, 86];
  for (let i = 0; i < 100; i++) {
    const d = document.createElement("div"); d.className = "dot"; d.id = "dt" + i;
    d.style.left = ((i % 10) * 76) + "px"; d.style.top = (Math.floor(i / 10) * 60) + "px"; grid.appendChild(d);
    tl.fromTo("#dt" + i, { scale: 0 }, { scale: 1, duration: 0.18, ease: E.ui }, 6.75 + rnd(i) * 0.6);
    if (REAL.includes(i)) {
      tl.to("#dt" + i, { backgroundColor: "#d7ff3c", scale: 1.5, duration: 0.25, ease: "back.out(2)" }, 9.4 + REAL.indexOf(i) * 0.06);
    } else {
      tl.to("#dt" + i, { y: 700 + rnd(i + 3) * 300, x: (rnd(i + 9) - 0.5) * 200, rotation: (rnd(i + 5) - 0.5) * 120, opacity: 0, duration: 0.6, ease: "power3.in" }, 8.84 + rnd(i + 1) * 0.45);
    }
  }
  tl.to("#gl", { opacity: 0, duration: 0.2 }, 8.84);

  // ===== 4 (cream) the real-enquiry card ticks itself off
  flash(10.5, 0.4);
  drift("#cam4", 10.5, 17.3, 0.04);
  words("#c4", 0, 0, [10.56, 11.04, 11.32, 11.52]); under("#u4", 11.52); punch("#c4", 11.52);
  tl.fromTo("#rc", { y: 260, rotation: 4, opacity: 0, rotationX: 8, transformPerspective: 900 }, { y: 0, rotation: -1, opacity: 1, rotationX: 0, duration: 0.55, ease: E.ui }, 11.7);
  [[1, 12.44, 13.1], [2, 13.44, 15.0], [3, 15.52, 16.75]].forEach(([n, a, c]) => {
    tl.fromTo("#rw" + n + " .tx", { x: 60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: E.in }, a);
    tl.fromTo("#bf" + n, { scale: 0 }, { scale: 1, duration: 0.22, ease: "back.out(2)" }, c);
    tl.fromTo("#ck" + n, { strokeDashoffset: 60 }, { strokeDashoffset: 0, duration: 0.22, ease: "power2.out" }, c + 0.04);
    shake("#rc", c, 6);
  });

  // ===== 5 the card lands on the phone; fewer time-wasters (grey blows away), more jobs (lime pops)
  drift("#cam5", 17.3, 22.0, 0.04);
  words("#c5a", 0, 0, [17.4, 17.72, 17.96, 18.24, 18.48, 18.64, 18.8, 19.04]); under("#u5a", 19.04);
  tl.fromTo("#ph5", { y: 900 }, { y: 0, duration: 0.55, ease: E.ui }, 17.45);
  tl.fromTo("#nt5", { y: -220, opacity: 0, scale: 1.3 }, { y: 0, opacity: 1, scale: 1, duration: 0.4, ease: "back.out(2)" }, 19.04);
  tl.fromTo("#ph5", { x: 0 }, { keyframes: { x: [8, -8, 6, -6, 3, 0] }, duration: 0.3, ease: "none", immediateRender: false }, 19.06);
  exit("#c5a", 19.58); tl.to("#u5a", { opacity: 0, duration: 0.1 }, 19.58);
  tl.set("#c5b", { opacity: 1 }, 19.64);
  words("#c5b", 0, 0, [19.68, 19.92]); under("#u5b", 19.92);
  const fw = document.getElementById("fws");
  for (let i = 0; i < 14; i++) {
    const d = document.createElement("div"); d.className = "fw"; d.id = "fw" + i;
    d.style.left = (90 + (i % 7) * 140) + "px"; d.style.top = (1560 + Math.floor(i / 7) * 80) + "px"; fw.appendChild(d);
    tl.fromTo("#fw" + i, { scale: 0, opacity: 1 }, { scale: 1, duration: 0.15, ease: E.ui }, 19.7 + i * 0.02);
    tl.to("#fw" + i, { x: -1300, rotation: -40, opacity: 0, duration: 0.5, ease: "power3.in" }, 20.3 + i * 0.025);
  }
  exit("#c5b", 20.86); tl.to("#u5b", { opacity: 0, duration: 0.1 }, 20.86);
  tl.set("#c5c", { opacity: 1 }, 20.92);
  words("#c5c", 0, 0, [20.96, 21.2]); under("#u5c", 21.2); punch("#c5c", 21.2);
  const mj = document.getElementById("mjs");
  [["Rewire", "NAAS", 40, 1080, -8], ["Boiler", "LUCAN", 790, 1120, 7], ["Extension", "NAVAN", 20, 1380, 5], ["EV charger", "SWORDS", 770, 1400, -6]].forEach(([t, p, x, y, r], i) => {
    const d = document.createElement("div"); d.className = "mj"; d.id = "mj" + i; d.style.left = x + "px"; d.style.top = y + "px";
    d.innerHTML = "<small>NEW · " + p + "</small>" + t; mj.appendChild(d);
    tl.fromTo("#mj" + i, { scale: 0, rotation: 0, opacity: 0 }, { scale: 1, rotation: r, opacity: 1, duration: 0.35, ease: "back.out(2)" }, 21.2 + i * 0.09);
  });
