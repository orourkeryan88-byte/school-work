  // ===== 1 HOOK
  drift("#cam1", 0, 2.4, 0.05);
  tl.fromTo("#hook", { x: -900, filter: "blur(10px)" }, { x: 0, filter: "blur(0px)", duration: 0.35, ease: "expo.out" }, 0.0);
  tl.fromTo("#hmk", { scaleX: 0 }, { scaleX: 1, duration: 0.25, ease: E.in }, 0.25);
  shake("#cam1", 0.1, 8);
  tl.to("#hook", { y: -30, opacity: 0, duration: 0.15, ease: "power2.in" }, 0.9);
  words("#c1", 0, 0, [1.04, 1.36, 1.52, 1.76]); under("#u1", 1.76); punch("#c1", 1.76);

  // ===== 2 "Answer three questions."
  flash(2.4, 0.4);
  drift("#cam2", 2.4, 4.3, 0.05);
  tl.fromTo("#q3big", { x: 500, rotation: 12, opacity: 0 }, { x: 0, rotation: 0, opacity: 1, duration: 0.5, ease: E.in }, 2.85);
  words("#c2", 0, 0, [2.48, 2.88, 3.2]); under("#u2", 3.2); punch("#c2", 3.2);

  // ===== 3 THE CHECK: cards slide in on "One / Two / Three", words land as she asks, ticks slam on the end of each question
  drift("#cam3", 4.3, 15.5, 0.04);
  const Q = [[1, 4.32, [5.36, 6.32, 6.56, 6.72], 7.42], [2, 7.76, [9.04, 9.44, 9.76, 9.92, 10.16], 10.95], [3, 11.28, [12.52, 12.84, 12.96, 13.6, 13.96, 14.16, 14.4], 15.12]];
  Q.forEach(([n, tin, ws, ttk]) => {
    tl.fromTo("#qc" + n, { x: 1150, rotation: 7, opacity: 1 }, { x: 0, rotation: 0, duration: 0.5, ease: E.ui }, tin);
    tl.fromTo("#qc" + n + " .num", { scale: 0.3, rotation: -20 }, { scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2.2)" }, tin + 0.15);
    words("#qt" + n, 0, 0, ws);
    tl.fromTo("#fl" + n, { scale: 0 }, { scale: 1, duration: 0.22, ease: "back.out(2)" }, ttk);
    tl.fromTo("#tk" + n, { strokeDashoffset: 120 }, { strokeDashoffset: 0, duration: 0.25, ease: "power2.out" }, ttk + 0.05);
    tl.fromTo("#qc" + n + " .box", { scale: 1.35 }, { scale: 1, duration: 0.35, ease: "back.out(2.4)", immediateRender: false }, ttk);
    tl.set("#ys" + n, { opacity: 1 }, ttk + 0.1);
    shake("#qc" + n, ttk, 9);
    if (n > 1) tl.to("#qc" + (n - 1), { opacity: 0.6, scale: 0.97, duration: 0.3 }, tin);
  });

  // ===== 4 "Said yes to any of them?" (lime): the three ticks stamp down in a row
  flash(15.5, 0.5);
  drift("#cam4", 15.5, 17.05, 0.05);
  words("#c4", 0, 0, [15.6, 15.84, 16.08, 16.24, 16.4, 16.56]); punch("#c4", 16.56);
  [["#mn1", 15.62], ["#mn2", 15.86], ["#mn3", 16.1]].forEach(([m, t]) => tl.fromTo(m, { scale: 2.2, opacity: 0, rotation: -12 }, { scale: 1, opacity: 1, rotation: 0, duration: 0.25, ease: "power4.in" }, t));
  shake("#cam4", 16.12, 8);

  // ===== 5 "You don't need to work harder." struck through, "You need to be found." with pulses
  drift("#cam5", 17.05, 20.75, 0.05);
  words("#c5a", 0, 0, [17.12, 17.36, 17.68, 17.84, 18.04, 18.28]);
  tl.fromTo("#st5", { scaleX: 0 }, { scaleX: 1, duration: 0.28, ease: E.in }, 18.62);
  exit("#c5a", 18.92);
  tl.set("#c5b", { opacity: 1 }, 18.96);
  words("#c5b", 0, 0, [19.0, 19.2, 19.4, 19.52, 19.76]); under("#u5", 19.76); punch("#c5b", 19.76);
  const sq = document.getElementById("sqs");
  for (let i = 0; i < 4; i++) {
    const d = document.createElement("div"); d.className = "sq"; d.id = "sq" + i; sq.appendChild(d);
    tl.fromTo("#sq" + i, { scale: 0.4, opacity: 0.9, rotation: 0 }, { scale: 3.2, opacity: 0, rotation: 12, duration: 1.0, ease: "power2.out", immediateRender: false }, 19.8 + i * 0.22);
  }

  // ===== 6 (lilac) the enquiries stack up
  flash(20.75, 0.4);
  drift("#cam6", 20.75, 25.2, 0.04);
  words("#c6a", 0, 0, [20.8, 21.0, 21.2, 21.64, 21.76, 22.32]); under("#u6", 22.32);
  exit("#c6a", 22.52); tl.to("#u6", { opacity: 0, duration: 0.1 }, 22.52);
  tl.set("#c6b", { opacity: 1 }, 22.6);
  words("#c6b", 0, 0, [22.64, 22.8, 23.04, 23.84, 24.12, 24.24, 24.4]); punch("#c6b", 24.4);
  const EQ = [["Full rewire", "Naas · this week", 23.04], ["Boiler swap", "Lucan · tomorrow", 23.84], ["Bathroom refit", "Bray · this month", 24.4]];
  const enqs = document.getElementById("enqs");
  EQ.forEach(([t, s, at], i) => {
    const e = document.createElement("div"); e.className = "enq"; e.id = "eq" + i; e.style.top = (1000 + i * 40) + "px";
    e.innerHTML = '<div class="k">NEW ENQUIRY · NOW</div><div class="t">' + t + '</div><div class="s">' + s + '</div>'; enqs.appendChild(e);
    tl.fromTo("#eq" + i, { y: 900, rotation: (i % 2 ? 9 : -9), opacity: 0 }, { y: i * 150, rotation: (i % 2 ? 2 : -2), opacity: 1, duration: 0.45, ease: E.ui }, at);
    shake("#cam6", at + 0.3, 5);
  });
