  drift("#cam1", 0, 4.3, 0.05);
  tl.fromTo("#hook", { x: -900, filter: "blur(10px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 0.0);
  tl.fromTo("#hmk", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: E.in }, 0.25); shake("#cam1", 0.12, 8);
  tl.to("#hook", { y: -30, opacity: 0, duration: 0.15, ease: "power2.in" }, 0.9);
  words("#c1a", 0, 0, [1.03, 1.24, 1.67, 1.88, 2.10, 2.31]); exit("#c1a", 2.55);
  tl.set("#c1b", { opacity: 1 }, 2.62); words("#c1b", 0, 0, [2.69, 2.88, 3.07, 3.26, 3.65, 3.84]); under("#u1", 3.84); punch("#c1b", 3.84);
  // ===== 2 three lanes get the same message; the race to ring back
  drift("#cam2", 4.3, 8.2, 0.04);
  words("#c2a", 0, 0, [4.37, 4.59, 5.02]); under("#u2a", 5.02); exit("#c2a", 5.5); tl.to("#u2a", { opacity: 0, duration: 0.1 }, 5.5);
  [["#ln1", 4.4], ["#ln2", 4.5], ["#ln3", 4.6]].forEach(([l, t]) => tl.fromTo(l, { x: 1100 }, { x: 0, duration: 0.4, ease: E.in }, t));
  [["#ms1", 4.9], ["#ms2", 5.0], ["#ms3", 5.1]].forEach(([m, t]) => tl.fromTo(m, { scale: 0, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }, t));
  tl.set("#c2b", { opacity: 1 }, 5.55); words("#c2b", 0, 0, [5.75, 5.92, 6.43, 6.61, 6.78, 7.46, 7.63, 7.80]); under("#u2b", 7.8); punch("#c2b", 7.8);
  tl.fromTo("#watch", { scale: 0, rotation: -40 }, { scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2)" }, 5.7);
  tl.fromTo("#hand", { rotation: 0 }, { rotation: 720, duration: 2.2, ease: "none" }, 5.8);
  tl.fromTo("#br1", { scaleX: 0 }, { scaleX: 0.55, duration: 1.8, ease: "power1.out" }, 5.9);
  tl.fromTo("#br2", { scaleX: 0 }, { scaleX: 1, duration: 1.5, ease: "power2.in" }, 5.9);
  tl.fromTo("#br3", { scaleX: 0 }, { scaleX: 0.35, duration: 1.8, ease: "power1.out" }, 5.9);
  tl.set("#won", { opacity: 1 }, 7.46); tl.fromTo("#won", { scale: 2, y: 130 }, { scale: 1, y: 130, duration: 0.3, ease: "back.out(2)" }, 7.46);
  // ===== 3 (cream) with us: the enquiry lands the second it comes in, fields fill as she says them
  flash(8.2, 0.4); drift("#cam3", 8.2, 14.7, 0.04);
  words("#c3a", 0, 0, [8.32, 8.57, 8.98, 9.15, 9.63, 9.79, 9.96, 10.12]); exit("#c3a", 10.22);
  tl.set("#c3b", { opacity: 1 }, 10.25); words("#c3b", 0, 0, [10.28, 10.44, 10.77, 10.93, 11.25]); under("#u3", 11.25); punch("#c3b", 11.25);
  tl.fromTo("#nc", { y: -1700, rotation: -6, opacity: 0 }, { y: 0, rotation: -1, opacity: 1, duration: 0.5, ease: "back.out(1.6)" }, 9.63);
  shake("#cam3", 10.1, 7);
  [["#f1", 12.01], ["#f2", 12.61], ["#f3", 14.04]].forEach(([f, t]) => {
    tl.fromTo(f + " span", { x: 80, opacity: 0, filter: "blur(8px)" }, { x: 0, opacity: 1, filter: "blur(0px)", duration: 0.3, ease: E.in }, t);
    tl.fromTo(f + " small", { opacity: 0 }, { opacity: 1, duration: 0.2 }, t - 0.2);
  });
  // ===== 4 your lane rockets to the finish first
  drift("#cam4", 14.7, 17.1, 0.04);
  words("#c4a", 0, 0, [14.80, 15.08, 15.36]); under("#u4a", 15.36); exit("#c4a", 15.85); tl.to("#u4a", { opacity: 0, duration: 0.1 }, 15.85);
  tl.set("#c4b", { opacity: 1 }, 15.92); words("#c4b", 0, 0, [15.99, 16.20, 16.41, 16.62]); under("#u4b", 16.62); punch("#c4b", 16.62);
  tl.fromTo("#bry", { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, 14.85);
  tl.fromTo("#bro1", { scaleX: 0 }, { scaleX: 0.3, duration: 1.2, ease: "power1.out" }, 14.85);
  tl.fromTo("#bro2", { scaleX: 0 }, { scaleX: 0.2, duration: 1.2, ease: "power1.out" }, 14.85);
  shake("#cam4", 15.45, 8);
