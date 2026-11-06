  drift("#cam1", 0, 2.3, 0.05);
  tl.fromTo("#hook", { x: -900, filter: "blur(10px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 0.0);
  tl.fromTo("#hmk", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: E.in }, 0.25); shake("#cam1", 0.12, 8);
  tl.to("#hook", { y: -30, opacity: 0, duration: 0.15, ease: "power2.in" }, 0.88);
  words("#c1", 0, 0, [1.01, 1.21, 1.41, 1.62, 1.82]); under("#u1", 1.82); punch("#c1", 1.82);
  // ===== 2 the word-of-mouth staircase: a step per job, then a quiet month drags it down
  drift("#cam2", 2.3, 9.8, 0.04);
  words("#c2a", 0, 0, [2.82, 3.27, 3.49, 3.72, 3.94, 4.17, 4.39, 4.62]); punch("#c2a", 4.62); exit("#c2a", 5.05);
  tl.fromTo("#g1", { strokeDashoffset: 400 }, { strokeDashoffset: 0, duration: 1.4, ease: "power1.inOut" }, 3.3);
  tl.set("#l1", { opacity: 1 }, 4.62);
  tl.set("#c2b", { opacity: 1 }, 5.1); words("#c2b", 0, 0, [5.18, 5.52, 5.69, 6.02, 6.51, 6.67]); punch("#c2b", 6.67); exit("#c2b", 7.3);
  tl.fromTo("#g2", { strokeDashoffset: 300 }, { strokeDashoffset: 0, duration: 0.6, ease: "power1.inOut" }, 5.2); tl.set("#l2", { opacity: 1 }, 5.69);
  tl.fromTo("#g3", { strokeDashoffset: 300 }, { strokeDashoffset: 0, duration: 0.6, ease: "power1.inOut" }, 6.2); tl.set("#l3", { opacity: 1 }, 6.67);
  tl.set("#c2c", { opacity: 1 }, 7.42); words("#c2c", 0, 0, [7.51, 7.69, 7.88, 8.07, 8.64, 8.87, 9.10, 9.32]); under("#u2", 9.32); punch("#c2c", 9.32);
  tl.fromTo("#g4", { strokeDashoffset: 500 }, { strokeDashoffset: 0, duration: 1.8, ease: "power1.inOut" }, 7.6); tl.set("#l4", { opacity: 1 }, 8.07);
  // ===== 3 (cream) every single day, a column of people for each day; then way more
  flash(9.8, 0.4); drift("#cam3", 9.8, 17.95, 0.04);
  words("#c3a", 0, 0, [9.89, 10.13, 10.37, 10.61, 10.85, 11.09, 11.32]); under("#u3", 11.32); punch("#c3a", 11.32); exit("#c3a", 11.75); tl.to("#u3", { opacity: 0, duration: 0.1 }, 11.75);
  tl.set("#c3b", { opacity: 1 }, 11.82); words("#c3b", 0, 0, [12.42, 12.59, 12.76, 12.93, 13.27, 13.44, 13.77, 14.31, 14.67]); exit("#c3b", 15.05);
  tl.set("#c3c", { opacity: 1 }, 15.1); words("#c3c", 0, 0, [15.19, 15.47, 15.75, 16.36, 16.58, 16.80, 17.24, 17.46]); punch("#c3c", 17.46);
  const wk = document.getElementById("week"), D = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"];
  D.forEach((n, c) => {
    const x = 70 + c * 136, lab = document.createElement("div"); lab.className = "day"; lab.id = "dy" + c; lab.style.left = x + "px"; lab.innerText = n; wk.appendChild(lab);
    tl.fromTo("#dy" + c, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.2 }, 12.3 + c * 0.05);
    for (let r = 0; r < 9; r++) {
      const p = document.createElement("div"); p.className = "pp" + (r >= 4 ? " v" : ""); p.id = "p" + c + "_" + r; p.style.left = (x + 7) + "px"; p.style.top = (1410 - r * 44) + "px"; wk.appendChild(p);
      tl.fromTo("#p" + c + "_" + r, { scaleX: 0, opacity: 0 }, { scaleX: 1, opacity: 1, duration: 0.18, ease: E.ui, immediateRender: true }, (r < 4 ? 13.77 + c * 0.13 + r * 0.04 : 16.36 + c * 0.1 + (r - 4) * 0.05));
    }
  });
