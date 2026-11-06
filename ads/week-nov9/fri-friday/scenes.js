  drift("#cam1", 0, 3.6, 0.05);
  tl.fromTo("#hook", { x: -900, filter: "blur(10px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 0.0);
  tl.fromTo("#hmk", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: E.in }, 0.25); shake("#cam1", 0.12, 8);
  tl.to("#hook", { y: -30, opacity: 0, duration: 0.15, ease: "power2.in" }, 1.15);
  words("#c1", 0, 0, [1.35, 1.59, 2.06, 2.29, 2.53, 2.76, 3.00]); under("#u1", 3.0); punch("#c1", 3.0);
  tl.fromTo("#tile", { rotationX: -90, opacity: 0, transformPerspective: 900, transformOrigin: "50% 0%" }, { rotationX: 0, opacity: 1, duration: 0.55, ease: "back.out(1.6)" }, 1.4);
  // ===== 2 the run-in: a rail from now to Black Friday, the winners' bar starts now, the audience warms
  flash(3.6, 0.4); drift("#cam2", 3.6, 12.4, 0.04);
  tl.fromTo("#rail", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "power2.out" }, 3.9);
  const tk = document.getElementById("ticks");
  for (let i = 0; i <= 18; i++) { const d = document.createElement("div"); d.className = "tk"; d.id = "tk" + i; d.style.left = (90 + i * 50) + "px"; tk.appendChild(d);
    tl.fromTo("#tk" + i, { scaleY: 0 }, { scaleY: 1, duration: 0.15, ease: E.in }, 3.95 + i * 0.03); }
  words("#c2a", 0, 0, [3.80, 4.05, 4.29, 4.54, 4.79, 5.03, 5.28, 5.53, 5.77, 6.02]); exit("#c2a", 6.45);
  tl.set("#c2b", { opacity: 1 }, 6.52); words("#c2b", 0, 0, [6.60, 6.80, 7.20, 7.79]); exit("#c2b", 8.05);
  tl.fromTo("#bar", { scaleX: 0 }, { scaleX: 1, duration: 3.6, ease: "power1.inOut" }, 6.8);
  tl.fromTo("#p1", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }, 6.8);
  tl.fromTo("#p2", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }, 8.15);
  tl.fromTo("#p3", { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }, 10.3);
  tl.set("#c2c", { opacity: 1 }, 8.1); words("#c2c", 0, 0, [8.15, 8.55, 8.75, 8.95, 9.35]); exit("#c2c", 9.62);
  const au = document.getElementById("auds");
  for (let i = 0; i < 12; i++) { const d = document.createElement("div"); d.className = "au"; d.id = "au" + i; d.style.left = (100 + i * 74) + "px"; au.appendChild(d);
    tl.fromTo("#au" + i, { scale: 0 }, { scale: 1, duration: 0.15, ease: E.ui }, 8.2 + i * 0.03);
    tl.to("#au" + i, { backgroundColor: "#b6a3ff", duration: 0.2 }, 8.95 + i * 0.03);
    tl.to("#au" + i, { backgroundColor: "#d7ff3c", y: -12, duration: 0.25, ease: "back.out(2)" }, 11.05 + i * 0.04); }
  tl.set("#c2d", { opacity: 1 }, 9.66); words("#c2d", 0, 0, [9.70, 9.90, 10.10, 10.30, 10.69, 11.05, 11.38, 11.88, 12.05]); under("#u2", 12.05); punch("#c2d", 12.05);
  // ===== 3 start on the day: cold, in the busiest feed of the year
  drift("#cam3", 12.4, 16.8, 0.05);
  words("#c3a", 0, 0, [12.55, 12.78, 13.00, 13.23]); exit("#c3a", 13.75);
  tl.set("#c3b", { opacity: 1 }, 13.8); words("#c3b", 0, 0, [13.84, 14.03, 14.22, 14.60, 14.79]); under("#u3", 14.79); punch("#c3b", 14.79);
  tl.fromTo("#you", { scale: 0.5, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: E.ui }, 14.79);
  const cr = document.getElementById("crowd");
  for (let i = 0; i < 22; i++) { const d = document.createElement("div"); d.className = "fc"; d.id = "fc" + i;
    const x = 20 + (i % 6) * 175 + (rnd(i) - 0.5) * 60, y = 930 + Math.floor(i / 6) * 160 + (rnd(i + 4) - 0.5) * 60;
    d.style.left = x + "px"; d.style.top = y + "px"; d.innerHTML = "<i></i>"; cr.appendChild(d);
    tl.fromTo("#fc" + i, { x: (i % 2 ? 1 : -1) * 900, rotation: (rnd(i + 7) - 0.5) * 30, opacity: 0 }, { x: 0, opacity: 1, rotation: (rnd(i + 7) - 0.5) * 14, duration: 0.45, ease: E.in }, 15.17 + i * 0.03); }
  shake("#cam3", 15.8, 8);
  // ===== 4 (lilac) ready for the run-in
  flash(16.8, 0.4); drift("#cam4", 16.8, 18.9, 0.05);
  words("#c4", 0, 0, [16.85, 17.00, 17.14, 17.29, 17.59, 17.73, 18.03, 18.18, 18.32]); punch("#c4", 18.32);
  [["#o1", 17.7], ["#o2", 17.95], ["#o3", 18.2]].forEach(([o, t]) => tl.fromTo(o, { x: -700, opacity: 0 }, { x: 0, opacity: 1, duration: 0.35, ease: E.ui }, t));
