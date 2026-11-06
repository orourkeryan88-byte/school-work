  // ===== 1 hook + the boost button pressed over and over
  drift("#cam1", 0, 2.7, 0.05);
  tl.fromTo("#hook", { x: -900, filter: "blur(10px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 0.0);
  tl.fromTo("#hmk", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: E.in }, 0.25); shake("#cam1", 0.12, 8);
  tl.to("#hook", { y: -30, opacity: 0, duration: 0.15, ease: "power2.in" }, 1.2);
  words("#c1", 0, 0, [1.44, 1.69, 2.19]); under("#u1", 2.19); punch("#c1", 2.19);
  tl.fromTo("#btn", { y: 500, opacity: 0 }, { y: 0, opacity: 1, duration: 0.4, ease: E.ui }, 1.3);
  [1.75, 2.05, 2.35].forEach(t => {
    tl.set("#tap", { opacity: 1, scale: 0.6 }, t); tl.to("#tap", { scale: 1.6, opacity: 0, duration: 0.25, ease: "power2.out" }, t + 0.01);
    tl.fromTo("#btn", { y: 0 }, { keyframes: { y: [20, 0] }, duration: 0.16, ease: "none", immediateRender: false }, t);
  });
  // ===== 2 one post, one arrow, whoever's around … and that's it; then what's missing gets crossed out
  drift("#cam2", 2.7, 9.9, 0.04);
  words("#c2a", 0, 0, [2.78, 3.19, 3.40, 3.82]); exit("#c2a", 5.05);
  tl.fromTo("#post", { scale: 0.4, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.35, ease: E.ui }, 3.4);
  tl.fromTo("#arrow", { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.out" }, 4.02);
  const cw = document.getElementById("crowd");
  for (let i = 0; i < 24; i++) { const d = document.createElement("div"); d.className = "crowd"; d.id = "cw" + i; d.style.left = (820 + (i % 4) * 54 - 10) + "px"; d.style.top = (1000 + Math.floor(i / 4) * 54) + "px"; cw.appendChild(d);
    tl.fromTo("#cw" + i, { scale: 0 }, { scale: 1, duration: 0.15, ease: E.ui }, 4.23 + rnd(i) * 0.4); }
  tl.set("#c2b", { opacity: 1 }, 5.15);
  words("#c2b", 0, 0, [5.22, 5.41, 5.60]); under("#u2", 5.6); punch("#c2b", 5.6);
  tl.to("#arrow", { scaleX: 0.15, duration: 0.3, ease: "power3.in" }, 5.62); shake("#cam2", 5.65, 8);
  exit("#c2b", 6.0);
  tl.to("#post, #arrow, #crowd", { opacity: 0.25, duration: 0.3 }, 6.0);
  [["#x1", 6.13], ["#x2", 7.0], ["#x3", 8.01]].forEach(([x, t]) => {
    tl.fromTo(x, { x: -200, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: E.in }, t);
    tl.fromTo(x + " b", { scale: 2, rotation: -30 }, { scale: 1, rotation: 0, duration: 0.3, ease: "back.out(2)" }, t + 0.1);
  });
  // ===== 3 (cream) properly: creatives tested, a winner pushed, everyone who looked looped back
  flash(9.9, 0.4);
  drift("#cam3", 9.9, 17.2, 0.04);
  words("#c3a", 0, 0, [9.98, 10.16, 10.33, 10.51, 10.87, 11.05]); under("#u3", 11.05); punch("#c3a", 11.05);
  exit("#c3a", 11.6); tl.to("#u3", { opacity: 0, duration: 0.1 }, 11.6);
  tl.set("#c3b", { opacity: 1 }, 11.66); words("#c3b", 0, 0, [11.74, 11.93, 12.48, 12.85, 13.41]); exit("#c3b", 13.68);
  [["#cr1", 11.74], ["#cr2", 11.86], ["#cr3", 11.98]].forEach(([c, t]) => tl.fromTo(c, { y: 400, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: E.ui }, t));
  [["#m1", 12.5], ["#m2", 12.6], ["#m3", 12.7]].forEach(([m, t]) => tl.fromTo(m, { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "power2.out" }, t));
  tl.set("#c3c", { opacity: 1 }, 13.72); words("#c3c", 0, 0, [13.75, 13.93, 14.27, 14.62]); exit("#c3c", 15.05);
  tl.to("#cr1, #cr3", { opacity: 0.3, scale: 0.92, duration: 0.3 }, 13.93);
  tl.to("#cr2", { scale: 1.15, duration: 0.35, ease: E.ui }, 13.93);
  tl.set("#win", { opacity: 1 }, 13.95); tl.fromTo("#win", { scale: 2 }, { scale: 1, duration: 0.25, ease: "back.out(2)" }, 13.95);
  tl.fromTo("#up", { scaleY: 0 }, { scaleY: 1, duration: 0.45, ease: "back.out(1.6)" }, 14.27);
  tl.set("#c3d", { opacity: 1 }, 15.1); words("#c3d", 0, 0, [15.28, 15.76, 15.91, 16.39, 16.68]);
  const au = document.getElementById("auds");
  for (let i = 0; i < 14; i++) { const d = document.createElement("div"); d.className = "aud"; d.id = "au" + i; d.style.left = (110 + i * 62) + "px"; au.appendChild(d);
    tl.fromTo("#au" + i, { scale: 0 }, { scale: 1, duration: 0.15, ease: E.ui }, 15.3 + i * 0.03); }
  tl.fromTo("#lp", { strokeDashoffset: 700 }, { strokeDashoffset: 0, duration: 0.6, ease: "power2.inOut" }, 16.3);
  tl.fromTo("#lp2", { strokeDashoffset: 700 }, { strokeDashoffset: 0, duration: 0.6, ease: "power2.inOut" }, 16.35);
  punch("#cr2", 16.7);
  // ===== 4 fee tied to the sales
  drift("#cam4", 17.2, 19.8, 0.05);
  words("#c4", 0, 0, [17.49, 17.67, 17.85, 18.04, 18.22, 18.40]); under("#u4", 18.4); punch("#c4", 18.4);
  tl.fromTo("#fee", { x: -500, opacity: 0 }, { x: 0, opacity: 1, duration: 0.4, ease: E.ui }, 17.6);
  tl.fromTo("#feeline", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: E.in }, 18.2);
  [["#sl1", 18.4], ["#sl2", 18.77], ["#sl3", 19.14]].forEach(([s, t]) => tl.fromTo(s, { scale: 0.3, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.3, ease: "back.out(2)" }, t));
