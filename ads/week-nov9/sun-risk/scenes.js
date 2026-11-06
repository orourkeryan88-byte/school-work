  drift("#cam1", 0, 4.0, 0.05);
  tl.fromTo("#hook", { x: -900, filter: "blur(10px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 0.0);
  tl.fromTo("#hmk", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: E.in }, 0.25); shake("#cam1", 0.12, 8);
  tl.to("#hook", { y: -30, opacity: 0, duration: 0.15, ease: "power2.in" }, 0.9);
  words("#c1a", 0, 0, [1.02, 1.20, 1.37, 1.89, 2.24, 2.42, 2.59]); under("#u1", 2.59); exit("#c1a", 3.15); tl.to("#u1", { opacity: 0, duration: 0.1 }, 3.15);
  tl.fromTo("#inv", { y: 400, rotation: 4, opacity: 0 }, { y: 0, rotation: -2, opacity: 1, duration: 0.45, ease: E.ui }, 1.3);
  tl.fromTo("#burn", { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.in" }, 2.59);
  tl.to("#inv", { y: 900, rotation: 18, duration: 0.6, ease: "power3.in" }, 3.3);
  tl.set("#c1b", { opacity: 1 }, 3.2); words("#c1b", 0, 0, [3.28, 3.44]); punch("#c1b", 3.44);
  // ===== 2 (cream) the deal builds as she says it
  flash(4.0, 0.4); drift("#cam2", 4.0, 8.8, 0.04);
  words("#c2", 0, 0, [4.12, 4.31, 4.70, 4.90]); under("#u2", 4.9); punch("#c2", 4.9);
  tl.fromTo("#deal", { y: 300, rotationX: 8, opacity: 0, transformPerspective: 900 }, { y: 0, rotationX: 0, opacity: 1, duration: 0.5, ease: E.ui }, 4.9);
  tl.fromTo("#d10", { scale: 0.3, opacity: 0, transformOrigin: "0% 60%" }, { scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2)" }, 5.43);
  tl.fromTo("#dq", { x: 60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: E.in }, 5.67);
  tl.fromTo("#d30", { x: 60, opacity: 0 }, { x: 0, opacity: 1, duration: 0.3, ease: E.in }, 6.61);
  tl.fromTo("#dst", { scale: 2.4, opacity: 0, rotation: -14 }, { scale: 1, opacity: 1, rotation: -3, duration: 0.26, ease: "power4.in" }, 7.78);
  shake("#cam2", 8.04, 10);
  // ===== 3 the scale tips: the risk moves off you and onto us
  drift("#cam3", 8.8, 10.7, 0.05);
  words("#c3", 0, 0, [8.86, 9.06, 9.25, 9.44, 9.63, 9.98, 10.21]); under("#u3", 10.21); punch("#c3", 10.21);
  tl.set("#beam", { rotation: -9 }, 8.8); tl.set("#pl", { y: 55 }, 8.8); tl.set("#pr", { y: -55 }, 8.8); tl.set("#rk", { y: 55 }, 8.8);
  tl.to("#rk", { x: 660, y: -160, duration: 0.3, ease: "power2.out" }, 9.44); tl.to("#rk", { y: -55, duration: 0.2, ease: "power2.in" }, 9.74);
  tl.to("#beam", { rotation: 9, duration: 0.45, ease: "back.out(2)" }, 9.63);
  tl.to("#pl", { y: -55, duration: 0.45, ease: "back.out(2)" }, 9.63); tl.to("#pr", { y: 55, duration: 0.45, ease: "back.out(2)" }, 9.63);
  tl.to("#rk", { y: 55, duration: 0.45, ease: "back.out(2)" }, 9.95);
  shake("#cam3", 9.95, 7);
  // ===== 4 (lilac) the qualified-leads meter fills as the enquiries come
  flash(10.7, 0.4); drift("#cam4", 10.7, 16.3, 0.04);
  words("#c4a", 0, 0, [10.79, 10.99, 11.20, 11.83, 12.04, 12.66]); exit("#c4a", 13.9);
  tl.set("#c4b", { opacity: 1 }, 13.98); words("#c4b", 0, 0, [14.08, 14.27, 14.47, 15.06, 15.26, 15.46, 15.66, 15.85]); punch("#c4b", 15.85);
  tl.fromTo("#ml", { opacity: 0 }, { opacity: 0.7, duration: 0.2 }, 11.2);
  const mt = document.getElementById("meter");
  for (let i = 0; i < 10; i++) { const s = document.createElement("div"); s.className = "sg"; s.style.left = (i * 91) + "px"; s.innerHTML = '<i id="sg' + i + '"></i>'; mt.appendChild(s);
    tl.fromTo("#sg" + i, { scaleY: 0 }, { scaleY: 1, duration: 0.22, ease: "back.out(2)" }, [11.25, 11.7, 12.15, 12.6, 13.05, 13.5, 14.47, 15.06, 15.46, 15.85][i]); }
  tl.to("#meter .sg i", { backgroundColor: "#d7ff3c", duration: 0.2, stagger: 0.02 }, 15.85);
