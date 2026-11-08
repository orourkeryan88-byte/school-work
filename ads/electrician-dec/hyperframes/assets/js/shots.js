/* The 15 scenes as pure functions of time: WORLD.render(T) shows the right set, places Dec and the props, moves the
   camera and lights, then draws. Nothing depends on the previous frame, so the renderer can seek anywhere.
   Word times come from timing.js (the voiceover); w(k) = local time of word k in the current scene. */
(function () {
  const C = K.C, P = DEC.P, kf = K.kf, seg = K.seg, eio = K.eio, eo = K.eo, lerp = K.lerp;
  const WORLD = (window.WORLD = {}), TM = window.TIMING;
  let R, scene, cam, L, dec, sets = {}, extras = {};
  const v = (x, y, z) => new THREE.Vector3(x, y, z);

  WORLD.init = (canvas) => {
    R = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
    R.setPixelRatio(1); R.setSize(1080, 1920, false); R.outputEncoding = THREE.sRGBEncoding;
    R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFShadowMap;
    scene = new THREE.Scene(); cam = new THREE.PerspectiveCamera(40, 1080 / 1920, 0.05, 220);
    L = SETS.lights(scene);
    ["A", "B", "C", "D", "E", "F", "G", "H", "I", "Map", "Flow", "Tower"].forEach((n) => { sets[n] = SETS.get(n); scene.add(sets[n]); });
    dec = DEC.make(); scene.add(dec.root);
    // floating extras: the cards of problem 1, the attic clock, toggle, padlock, dominoes
    extras.cards = ["Brennan Electrical", "JK Sparks", "Lynch Electric", "Doyle & Son", "Kelly Electrical", "Byrne & Co", "rewires.co"].map((n, i) => {
      const g = new THREE.Group(), me = i === 6;
      g.add(K.rbox(1.5, 0.62, 0.05, 0.08, me ? C.gold : C.cloud));
      const t = SETS.cardTex(720, 300, me ? K.hex(C.gold) : K.hex(C.cloud), [{ t: n, f: `700 78px ${SETS.FONT}`, c: K.hex(C.ink), y: 110, x: 40 },
        { t: "Free quotes · any job", f: `500 46px ${SETS.MONO}`, c: K.hex(me ? C.ink : C.graphite), y: 215, x: 40 }], { r: 40 });
      const p = K.plane(1.44, 0.6, t); p.position.z = 0.03; g.add(p); g.userData.p = p; scene.add(g); return g;
    });
    extras.dominos = [1, 2, 3, 4, 5].map((n) => { const pv = new THREE.Group(), d = SETS.domino(n, n === 1); d.rotation.y = -Math.PI / 2; d.position.x = -0.16; pv.add(d); scene.add(pv); return pv; });
    extras.toggle = SETS.toggle(); scene.add(extras.toggle);
    extras.lock = SETS.padlock(); scene.add(extras.lock);
    extras.glow = new THREE.Mesh(new THREE.CircleGeometry(3, 40), new THREE.MeshBasicMaterial({ color: 0xf0b455, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
    scene.add(extras.glow);
    WORLD.cam = cam; WORLD.dec = dec;
  };

  // ---------- helpers ----------
  const hideAll = () => { for (const k in sets) sets[k].visible = false; for (const k in extras) { const e = extras[k]; (Array.isArray(e) ? e : [e]).forEach((o) => (o.visible = false)); }
    dec.root.visible = true; scene.fog = null; };
  const show = (...n) => n.forEach((k) => (sets[k].visible = true));
  const look = (p, t, fov = 40) => {
    if (["I", "Map", "Flow", "Tower", "F"].some((k) => sets[k].visible) && !sets.B.visible) {         // open sets: longer lens = flatter, more 2D
      const f2 = fov * 0.62, k = Math.tan(fov * Math.PI / 360) / Math.tan(f2 * Math.PI / 360); p = t.clone().add(p.clone().sub(t).multiplyScalar(k)); fov = f2; }
    cam.position.copy(p); cam.up.set(0, 1, 0); cam.lookAt(t); if (cam.fov !== fov) { cam.fov = fov; cam.updateProjectionMatrix(); } };
  const lerpV = (a, b, u) => v(lerp(a.x, b.x, u), lerp(a.y, b.y, u), lerp(a.z, b.z, u));
  const pathV = (t, keys, ease = eio) => { const x = K.kfv(t, keys, ease); return v(x[0], x[1], x[2]); };
  /* lights: key [colour, intensity, position, target], hemi [sky, ground, intensity], p1/p2 point lights, bg colour */
  const light = (o) => {
    const k = o.key || [0xffe3b8, 1.2, [5, 9, 6], [0, 0, 0]];
    L.key.color.set(k[0]); L.key.intensity = k[1]; L.key.position.set(...k[2]); L.key.target.position.set(...(k[3] || [0, 0, 0]));
    const s = o.shadow || 9; const sc = L.key.shadow.camera; if (sc.right !== s) { sc.left = -s; sc.right = s; sc.top = s; sc.bottom = -s; sc.updateProjectionMatrix(); }
    const h = o.hemi || [0xcfe0d8, 0x0c2a22, 0.6]; L.hemi.color.set(h[0]); L.hemi.groundColor.set(h[1]); L.hemi.intensity = h[2];
    [["p1", o.p1], ["p2", o.p2]].forEach(([n, p]) => { const l = L[n]; if (!p) { l.intensity = 0; l.visible = false; return; }
      l.visible = true; l.color.set(p[0]); l.intensity = p[1]; l.position.set(...p[2]); l.distance = p[3] || 9; });
    scene.background = new THREE.Color(o.bg === undefined ? C.pine : o.bg);
    if (o.fog) scene.fog = new THREE.Fog(o.fog[0], o.fog[1], o.fog[2]);
  };
  const DARK = { hemi: [0x6f9c8a, 0x0c2a22, 0.45] }, BRIGHT = { hemi: [0xffffff, 0x9fb3aa, 0.85] };
  const FIXL = (o = {}) => Object.assign({ key: [0xffe6c0, 1.3, [-4, 10, 7], [0, 1, 0]], hemi: [0xa9cfc0, 0x0c2a22, 0.7], bg: C.pine }, o);
  /* Dec placement + acting. pose track keys and face keys are in scene-local seconds */
  const act = (lt, pos, ry, poses, faces, o = {}) => {
    dec.root.position.set(...pos); dec.root.rotation.set(0, ry, 0); dec.root.scale.setScalar(o.scale || 1);
    dec.hold(o.hold || null);
    dec.apply(DEC.track(lt, poses, o.blend), DEC.face(lt, faces), lt + (o.seed || 0), o);
  };
  const sitP = (n) => Object.assign({}, P.sit, P[n]);
  const ramp = (lt, slow = 0.6, k = 0.3) => (lt < slow ? lt * k : slow * k + (lt - slow));   // slow-mo speed ramp
  const W = (i) => TM.scenes[i].words.map((x) => x.start - TM.scenes[i].start);

  // ---------- scenes (lt = local time, d = duration, w = word times) ----------
  // Framing note: 9:16 at fov 40 shows only ±0.2·distance sideways, so subjects stay close to the look-at line,
  // and full-body shots aim at y ≈ 1.9 so Dec's head sits just under the caption band.
  const SH = [];

  // 1 THE LAUNCH: low angle, the van rolls in nose-first and bounces; Dec hops out and waves → crane up over the
  //   street and back to the box-room window as night falls → in through the window, over his shoulder, into the screen
  SH[0] = (lt, d, w) => {
    const c1 = 2.55, cut = w[11] - 0.05, night = seg(lt, c1, cut);
    if (lt < cut) {
      show("B"); const B = sets.B.userData; B.night(night); B.vans.forEach((x) => (x.visible = false));
      const bg = new THREE.Color(0xc6ccc8).lerp(new THREE.Color(0x0c2a22), night);
      light({ key: [night > 0.5 ? 0x9fc2b4 : 0xffe3b8, lerp(1.15, 0.25, night), [-8, 12, 14], [3, 0, 6]], hemi: [night > 0.5 ? 0x4f7a6a : 0xdfe9e4, 0x2f4a3c, lerp(0.75, 0.45, night)], bg: bg.getHex(), shadow: 14 });
      const arrive = eo(lt / 1.25), z = lerp(17, 7.6, arrive);
      B.van.position.set(4.5, 0, z); B.van.rotation.y = Math.PI / 2;
      B.van.userData.wheels.forEach((wh) => (wh.rotation.z = -(17 - z) / 0.42));
      const bt = lt - 1.2; B.van.userData.body.position.y = bt > 0 ? -0.07 * Math.exp(-bt * 5) * Math.sin(bt * 22) : 0;
      B.van.userData.body.rotation.x = bt > 0 ? 0.03 * Math.exp(-bt * 5) * Math.sin(bt * 22) : 0;
      const hop = seg(lt, 1.3, 1.7);
      dec.root.visible = lt > 1.25;
      act(lt, [lerp(3.45, 3.0, hop), Math.sin(hop * Math.PI) * 0.35, lerp(7.2, 6.6, hop)], lerp(-1.3, Math.PI - 0.35, eo(seg(lt, 1.55, 1.95))),
        [[0, "idle"], [1.3, { lSz: 0.6, rSz: -0.6, lE: -0.3, rE: -0.3 }], [1.72, "idle"], [1.9, "wave"]], [[0, "happy"], [1.85, "grin"]], { seed: 1 });
      if (lt > 1.9) dec.J.shR.rotation.z += 0.25 * Math.sin((lt - 1.9) * 13);
      if (lt < c1) look(v(lerp(1.35, 1.6, lt / c1), lerp(0.5, 0.62, lt / c1), lerp(3.95, 3.85, lt / c1)), v(3.7, 1.7, 8.5), 46);
      else { const cu = eio(night);
        look(pathV(cu, [[0, [1.6, 0.62, 3.85]], [0.5, [2.0, 7.5, 12.5]], [1, [-1.9, 4.2, 5.2]]], (u) => u), lerpV(v(3.7, 1.7, 8.5), v(-1.9, 4.1, 3.5), eio(seg(cu, 0.25, 1))), 42); }
    } else {
      const lt2 = lt - cut; show("A"); const A = sets.A.userData;
      A.glass.material.map = A.out; A.clock.visible = false;
      light({ key: [0x5f8f80, 0.25, [2, 6, -6], [0, 1, 0]], hemi: [0x3f6f60, 0x0c2a22, 0.35], p1: [0xffc070, 2.2, [-0.5, 2.1, -1.7], 6], p2: [0xe9f2ec, 1.5, [0.45, 1.6, -1.0], 3.2], bg: C.pine });
      rain(A, lt);
      act(lt, [0.15, 0, -0.35], Math.PI, [[0, Object.assign(sitP("type"), { headX: -0.18 })]], [[0, "determined"], [w[19] + 0.1, "grin"]], { seed: 2 });
      typing(lt);
      const swing = eio(seg(lt, w[14] - 0.1, w[16]));
      const p = swing <= 0 ? lerpV(v(0.3, 2.3, -3.7), v(0.35, 1.95, -2.25), eo(seg(lt2, 0, 1.2))) :
        pathV(swing, [[0, [0.35, 1.95, -2.25]], [0.5, [1.5, 2.2, -0.5]], [1, [0.75, 2.0, 0.35]]], (u) => u);
      const tg = swing <= 0 ? v(0.15, 1.6, -0.35) : lerpV(v(0.15, 1.6, -0.35), v(0.45, 1.42, -1.7), swing);
      const push = eio(seg(lt, w[17], d));
      look(lerpV(p, v(0.5, 1.55, -1.15), push * 0.85), tg, lerp(40, 30, push));
    }
  };
  function rain(A, lt) { A.rain.forEach((r) => { const u = ((lt * r.userData.s + r.userData.o) % 2.2); r.position.set(r.userData.x, 0.95 - u, 0.03); r.visible = u < 1.95; }); }
  function typing(lt) { const J = dec.J; J.elL.rotation.x += 0.12 * Math.sin(lt * 31); J.elR.rotation.x += 0.12 * Math.sin(lt * 27 + 1.3); }

  // 2 DAY ONE: morning, clock 8:02. Over the shoulder into the screen (DOM: refresh, 0 enquiries), then his face.
  SH[1] = (lt, d, w) => {
    show("A"); const A = sets.A.userData; A.glass.material.map = A.day; A.cone.visible = false; A.clock.visible = true; A.clock.userData.set(8, 2);
    A.rain.forEach((r) => (r.visible = false));
    light({ key: [0xe9eee9, 0.85, [1, 7, -9], [0, 1, 0]], hemi: [0xdfe9e4, 0x2f4a3c, 0.55], p2: [0xe9f2ec, 0.6, [0.45, 1.6, -1.0], 3], bg: 0x8fa39a });
    const rev = w[4] + 0.3;
    act(lt, [0.15, 0, -0.35], Math.PI, [[0, sitP("type")], [0.5, sitP("leanIn")], [rev + 0.15, Object.assign(sitP("slump"), { headX: 0.12, lean: 0.2 }), 0.5]], [[0, "happy"], [w[3], "knit"], [rev + 0.1, "defeated"]], { seed: 3 });
    if (lt < rev) look(lerpV(v(1.0, 2.1, 0.7), v(0.6, 1.68, -0.75), eio(lt / rev)), v(0.45, 1.42, -1.75), lerp(38, 30, eio(lt / rev)));
    else { const u = eio(seg(lt, rev, d)); look(lerpV(v(2.1, 2.05, -2.0), v(1.95, 2.0, -1.85), u), v(0.2, 1.3, -0.45), 44); }
  };

  // 3 THE ROAD TO BOOKED OUT: five domino tiles topple in slow motion; the last stops at Dec's boots. He shrugs.
  SH[2] = (lt, d, w) => {
    show("I"); sets.I.userData.tone(true); sets.I.userData.strip.visible = true;
    light({ key: [0xffd9a0, 1.0, [-4, 9, 6], [0, 0, 0]], hemi: [0x6f9c8a, 0x0c2a22, 0.5], bg: C.pine });
    const X = [-5.6, -4.2, -2.8, -1.4, 0.0], start = (i) => 0.5 + i * 0.62;
    extras.dominos.forEach((pv, i) => { pv.visible = true; pv.position.set(X[i] + 0.16, 0.06, 0);
      const me = eio(seg(lt, start(i), start(i) + 0.75)), nx = i < 4 ? eio(seg(lt, start(i + 1), start(i + 1) + 0.75)) : 0;
      pv.rotation.z = -(i < 4 ? 0.69 * me + 0.55 * nx : 1.33 * K.back(seg(lt, start(i), start(i) + 0.9), 0.6)); });
    const dx = X[4] + 2.25;
    act(lt, [dx, 0.06, 0.1], -0.55, [[0, "idle"], [start(4) + 0.7, { lSz: 0.12, rSz: -0.12, headX: 0.3, headY: 0.4 }], [w[14] - 0.15, "shrug"]],
      [[0, "neutral"], [start(4) + 0.8, "knit"], [w[14], "happy"]], { seed: 4 });
    const u = eio(seg(lt, 0.2, start(4) + 0.6)), endU = eio(seg(lt, start(4) + 0.7, w[13]));
    look(lerpV(v(lerp(-7.8, -1.4, u), 1.9, 4.6), v(dx - 0.5, 1.75, 4.6), endU), lerpV(v(lerp(-4.6, 0.8, u), 0.8, 0), v(dx - 0.2, 1.35, 0), endU), 40);
  };

  // 4 PROBLEM 1 (van cab): identical free-quote cards fly out of his phone and orbit; his card fades into the pile.
  SH[3] = (lt, d, w) => {
    show("C"); const Cc = sets.C.userData; Cc.timeline.visible = false;
    light({ key: [0xbfd2c8, 0.6, [3, 8, -9], [0, 1, 0]], hemi: [0x86a598, 0x0c2a22, 0.5], p1: [0xe9f2ec, 0.9, [0.45, 2.2, -0.6], 3], bg: 0x3a4a43, fog: [0x5c6e66, 14, 60] });
    scroll(Cc, 40, 0);
    act(lt, [-0.55, 0.3, 0.45], Math.PI, [[0, P.drive], [w[9], Object.assign({}, P.drive, { headY: 0.3, headX: -0.15 })]], [[0, "neutral"], [w[3], "knit"], [w[9], "frustrated"]], { seed: 5 });
    const a = -1.15 + ramp(lt) * 0.46, c = v(-0.55, 2.0, 0.45), r = 3.3;
    look(v(c.x + Math.sin(a) * r, 2.55, c.z - Math.cos(a) * r), v(-0.5, 2.05, 0.45), 42);
    const ph = v(0.45, 1.98, -0.9);
    extras.cards.forEach((g, i) => {
      const me = i === 6, t0 = me ? w[5] - 0.1 : w[7] + i * 0.16;
      const u = eo(seg(lt, t0, t0 + 0.7)); g.visible = lt > t0;
      const ang = i * 0.9 + lt * 0.6, rad = 0.95 + (i % 3) * 0.14, hy = 2.6 + (i % 3) * 0.13;
      const orbit = v(c.x + Math.cos(ang) * rad, hy, c.z + Math.sin(ang) * rad * 0.7);
      const target = me && lt < w[7] ? v(c.x + 0.1, 2.75, -0.3) : orbit;
      g.position.copy(lerpV(ph, target, u)); g.quaternion.copy(cam.quaternion);
      const fade = me ? seg(lt, w[12], w[14]) : 0; g.scale.setScalar(lerp(0.15, 0.44, u) * (1 - fade * 0.3));
      g.userData.p.material.opacity = 1 - fade * 0.6;
    });
  };
  function scroll(Cc, t, speed) {
    Cc.dashes.forEach((dd, i) => (dd.position.z = -((i * 5 - t * speed) % 70 + 70) % 70 + 2));
    Cc.hedges.forEach((h, i) => (h.position.z = -((i * 3 - t * speed) % 78 + 78) % 78 + 3));
  }

  // 5 FIX 1: offer panel on the clean stage (DOM) → hallway mid-rewire, phone buzzing on the ladder, Dec's "O"
  SH[4] = (lt, d, w) => {
    const cut = w[15] - 0.12;
    if (lt < cut) {
      show("I"); sets.I.userData.tone(true);
      light(FIXL());
      act(lt, [-0.7, 0, 0.5], 0.5, [[0, "idle"], [w[1] - 0.1, "point"], [w[9], "idle"], [w[12], "thumbs"]], [[0, "determined"], [w[1], "happy"], [w[12], "grin"]],
        { hold: lt > w[1] - 0.1 && lt < w[9] ? "driver" : null, seed: 6 });
      const u = eio(lt / cut); look(v(lerp(0.15, 0.3, u), 1.95, lerp(6.4, 5.7, u)), v(0.05, 1.85, 0), 40);
    } else {
      const l2 = lt - cut; show("D"); const D = sets.D.userData;
      light({ key: [0xffe8c8, 0.95, [4, 8, 6], [0, 1, -1]], hemi: [0xf2efe6, 0x5a4636, 0.6], bg: 0x2a211a });
      const buzz = lt > w[16] ? Math.sin(lt * 70) * 0.012 : 0; D.phone.position.x = -0.68 + buzz; D.phone.rotation.y = buzz * 3;
      D.phoneScr.material = K.glow(lt > w[16] ? 0xf0b455 : 0x2b4a40);
      const turn = eo(seg(lt, w[17], w[18] + 0.1));
      act(lt, [0.55, 0, -1.3], lerp(Math.PI, 0.3, turn), [[0, P.chase], [w[17], "idle"], [w[18], { lSz: 0.4, rSz: -0.4, lE: -0.6, rE: -0.6, lift: 0.03 }]],
        [[0, "determined"], [w[18], "shocked"]], { hold: lt < w[17] ? "driver" : null, seed: 7 });
      if (lt < w[17]) dec.J.elR.rotation.x += 0.15 * Math.sin(lt * 26);
      const a = 0.75 - l2 * 0.6, r = lerp(5.2, 4.2, eio(l2 / (d - cut)));
      look(v(0.2 + Math.sin(a) * r, lerp(2.5, 2.1, eio(l2 / 2)), -1.0 + Math.cos(a) * r), v(0.15, 1.75, -1.1), 42);
    }
  };

  // 6 PROBLEM 2 (kitchen, night): chat bubbles (DOM); he scratches his head with the screwdriver; JUNK stamp slams down.
  SH[5] = (lt, d, w) => {
    show("H"); const H = sets.H.userData;
    light({ key: [0x9fc2b4, 0.3, [3, 9, 4], [0, 1, 0]], hemi: [0x5f8c7c, 0x0c2a22, 0.4], p1: [0xffc27a, 2.6, [0, 3.8, 0], 9], bg: 0x112620 });
    H.cal.userData.pages.forEach((p) => (p.rotation.x = 0));
    act(lt, [0.75, 0, 1.15], 0.25, [[0, "phoneLook"], [w[5], "scratch"], [w[9] + 0.15, { lSz: 0.5, rSz: -0.5, lE: -0.5, rE: -0.5, lean: -0.08 }]],
      [[0, "knit"], [w[5], "frustrated"], [w[9] + 0.15, "shocked"]], { hold: "driver", seed: 8 });
    if (lt > w[5] && lt < w[9]) dec.J.elR.rotation.x += 0.18 * Math.sin(lt * 22);
    const st = w[9] - 0.05, hit = st + 0.2;
    H.stamp.visible = lt > st - 0.3; H.stamp.position.set(-0.45, lt < hit ? lerp(6, 1.28, (seg(lt, st - 0.3, hit)) ** 2) : 1.28, 0.0);
    H.stamp.scale.set(1, lt > hit ? 1 - 0.25 * Math.exp(-(lt - hit) * 9) : 1, 1); H.stamp.rotation.y = -0.12;
    H.dust.forEach((p, i) => { const u = seg(lt, hit, hit + 0.7); p.visible = u > 0 && u < 1; const a = i / 10 * 6.283;
      p.position.set(-0.45 + Math.cos(a) * (1.0 + u * 0.9), 1.1 + u * 0.3, Math.sin(a) * (0.6 + u * 0.7)); p.scale.setScalar(0.4 + u * 1.2 * (1 - u)); });
    const u = eio(seg(ramp(lt, 0.6, 0.35), 0, 2.4)), a = lerp(-0.9, 0.12, u), r = lerp(1.0, 6.4, u);
    look(v(0.1 + Math.sin(a) * r, lerp(8.8, 2.9, u), 0.3 + Math.cos(a) * r), v(0.1, lerp(1.0, 1.65, u), 0.2), lerp(50, 40, u));
  };

  // 7 FIX 2: tilt-shift Kildare miniature; the ad card (DOM) rises out of it; 24 lead tiles → 19 sink, 5 glow.
  SH[6] = (lt, d, w) => {
    show("I", "Map"); sets.I.userData.tone(true);
    light(FIXL({ shadow: 9 }));
    const M = sets.Map.userData;
    M.tiles.forEach((t, i) => { const up = K.back(seg(lt, w[14] + i * 0.012, w[14] + i * 0.012 + 0.3)), down = t.userData.good ? 0 : eio(seg(lt, w[15], w[15] + 0.5));
      t.visible = up > 0.01; t.position.y = 0.6 + up * 0.14 - down * 0.32; t.scale.setScalar(Math.max(0.01, up));
      t.material = t.userData.good && lt > w[16] ? K.glow(0xf0b455) : K.toon(C.fog); });
    act(lt, [1.3, 0, 4.4], -0.3, [[0, "idle"], [w[1] - 0.1, Object.assign({}, P.point, { rSx: -1.0, headY: -0.3, headX: 0.25 })], [w[8], "idle"], [w[17], "cross"]],
      [[0, "determined"], [w[1], "happy"], [w[17], "grin"]], { hold: lt > w[1] - 0.1 && lt < w[8] ? "driver" : null, seed: 9 });
    const u = eio(seg(lt, 0, d));
    look(v(lerp(1.4, 1.0, u), lerp(9.0, 7.0, u), lerp(11.0, 9.4, u)), v(0.6, lerp(0.4, 0.9, u), 0.6), 40);
  };

  // 8 PROBLEM 3: quote form ("they tap submit just to get a price") (DOM, over the kitchen) → van on the road to Naas (tilt-shift) → empty house, no one home.
  SH[7] = (lt, d, w) => {
    const c1 = w[14] - 0.12, c2 = w[18] - 0.25;
    if (lt < c1) {
      show("H"); const H = sets.H.userData; H.stamp.visible = false; H.dust.forEach((p) => (p.visible = false));
      light({ key: [0x9fc2b4, 0.3, [3, 9, 4], [0, 1, 0]], hemi: [0x5f8c7c, 0x0c2a22, 0.4], p1: [0xffc27a, 2.6, [0, 3.8, 0], 9], bg: 0x112620 });
      act(lt, [0.3, 0, -1.2], 0, [[0, sitP("phoneLook")]], [[0, "neutral"], [w[6], "knit"]], { hold: "phone", seed: 23 });
      const a = 0.5 + ramp(lt, 0.6, 0.3) * 0.16; look(v(Math.sin(a) * 5.4, 3.0, Math.cos(a) * 5.4), v(0.2, 1.4, -0.3), 40);
    } else if (lt < c2) {
      const l2 = lt - c1; show("F"); const F = sets.F.userData; dec.root.visible = false;
      light({ key: [0xe6ece8, 0.95, [-6, 12, 4], [0, 0, -20]], hemi: [0xdfe9e4, 0x3f5c38, 0.6], bg: 0xb9c2bd, shadow: 26, fog: [0xb9c2bd, 30, 75] });
      const u = 0.2 + l2 * 0.09, p = F.curve.getPointAt(u), tg = F.curve.getTangentAt(u);
      F.van.position.copy(p); F.van.rotation.y = Math.atan2(-tg.z, tg.x);
      F.van.userData.wheels.forEach((wh) => (wh.rotation.z = -l2 * 9));
      const sp = F.curve.getPointAt(0.29); F.sign.position.set(sp.x + 1.7, 0, sp.z);
      F.board.rotation.y = lt > w[17] - 0.25 ? -K.eo(seg(lt, w[17] - 0.25, w[17] + 0.3)) * Math.PI * 2 : 0;
      look(v(p.x + 1.2, 5.0, p.z + 6.0), v(p.x, 0.3, p.z - 0.8), 34);
    } else {
      const l3 = lt - c2; show("G"); const G = sets.G.userData;
      light({ key: [0xdfe6e2, 0.85, [-8, 10, 9], [1, 0, 3]], hemi: [0xdfe9e4, 0x3f5c38, 0.55], bg: 0xa9b3ae, shadow: 12 });
      G.leaves.forEach((lf, i) => { const ph = (l3 * (0.9 + K.hash(i) * 0.6) + K.hash(i + 5) * 3) % 3;
        lf.position.set(-0.5 + ph * 2.2 + Math.sin(ph * 4 + i) * 0.3, 0.05 + Math.abs(Math.sin(ph * 5 + i)) * 0.35, 4.6 + K.hash(i + 9) * 1.8); lf.rotation.set(ph * 3, ph * 5, ph * 2); });
      act(lt, [1.5, 0.18, 4.75], lerp(Math.PI, 0.6, eo(seg(lt, w[19] + 0.25, w[19] + 0.75))), [[0, "knock"], [w[19] + 0.2, "slump", 0.5]], [[0, "neutral"], [w[19] + 0.2, "defeated"]], { seed: 10 });
      if (lt < w[19]) dec.J.elR.rotation.x += 0.35 * Math.max(0, Math.sin(lt * 18));
      const u = eio(seg(l3, 0, d - c2)); look(lerpV(v(3.4, 2.1, 10.6), v(2.7, 2.0, 8.6), u), v(1.6, 1.85, 4.5), 38);
    }
  };

  // 9 FIX 3: Ad → Video → Form stacked with glowing cables (camera rides down the cable) → selfie video by the new board.
  SH[8] = (lt, d, w) => {
    const cut = w[7] - 0.15;
    if (lt < cut) {
      show("I", "Flow"); sets.I.userData.tone(true); dec.root.visible = false;
      light(FIXL({ shadow: 10 }));
      const F = sets.Flow.userData; F.play.scale.setScalar(1 + (lt > w[3] ? 0.14 * Math.max(0, Math.sin((lt - w[3]) * 9)) : 0));
      F.sparks.forEach((s, i) => { const u = ((lt * 0.9 + i * 0.5) % 1); s.position.copy(F.cables[i].userData.curve.getPointAt(u)); });
      const u = eio(seg(lt, 0.15, cut)), y = lerp(6.4, 1.6, u);
      look(v(0.9, y + 0.5, 5.4), v(0, y - 0.35, 0), 40);
    } else {
      show("D"); const D = sets.D.userData; D.phoneScr.material = K.glow(0x2b4a40);
      light({ key: [0xffe8c8, 1.0, [4, 8, 6], [1, 1, -1]], hemi: [0xf2efe6, 0x5a4636, 0.65], bg: 0x2a211a });
      act(lt, [2.25, 0, -0.85], -0.25, [[0, "selfie"], [w[19] - 0.1, Object.assign({}, P.selfie, P.thumbs, { headY: 0.1 })]], [[0, "talk"], [w[19], "grin"]], { hold: "phoneL", seed: 11 });
      if (lt < w[19]) dec.J.mouthMat.map = DEC.mouthTex[Math.sin(lt * 34) > 0 ? "open" : "smile"];      // lip flap while he talks to camera
      const u = eio(seg(lt, cut, d)); look(lerpV(v(1.0, 2.2, 2.8), v(1.4, 2.15, 2.2), u), v(2.2, 1.85, -1.1), 40);
    }
  };

  // 10 PROBLEM 4: attic under the swinging work light → crane down through the hatch → phone on the landing, clock to 17:00
  SH[9] = (lt, d, w) => {
    show("E"); const E = sets.E.userData, Y = E.Y;
    const sw = Math.sin(lt * 2.2) * 0.28; E.wl.rotation.z = sw; E.wl.rotation.x = Math.cos(lt * 1.7) * 0.12;
    const bulb = new THREE.Vector3(); E.bulb.getWorldPosition(bulb);
    light({ key: [0xdcd8cc, lt > 1.8 ? 0.6 : 0.12, [4, 9, 6], [0, 0, 0]], hemi: [0x7f8f86, 0x1a1410, lt > 1.8 ? 0.55 : 0.25], p1: [0xffd08a, 3.2, [bulb.x, bulb.y, bulb.z], 8], bg: 0x120e0b });
    const spin = eio(seg(lt, w[12] - 0.1, w[13] + 0.2)), mins = lt < w[11] ? 4 : lt < w[12] - 0.1 ? 6 : lerp(6, 300, spin);
    E.clock.userData.set(12 + Math.floor(mins / 60), mins % 60, spin > 0.98);
    const down = w[14] - 0.1, land = down + 0.45, dropU = seg(lt, down, land), landed = lt > land;
    E.phone.visible = !landed;
    if (lt < down) act(lt, [-1.1, Y - 0.12, -1.0], 0.5, [[0, "work"]], [[0, "determined"]], { hold: "driver", seed: 12 });
    else act(lt, [lerp(0.2, 0.75, dropU), lerp(Y + 0.2, 0, dropU * dropU), lerp(0.6, -0.5, dropU)], 0.4,
      [[0, { lSz: 0.8, rSz: -0.8 }], [land, landed ? "phoneLook" : "idle"], [w[17] - 0.1, Object.assign({}, P.phoneLook, P.slump, { headX: 0.55 }), 0.5]],
      [[0, "shocked"], [land + 0.2, "knit"], [w[17] - 0.1, "defeated"]], { hold: landed ? "phone" : null, seed: 12 });
    if (lt < down) dec.J.elR.rotation.x += 0.2 * Math.sin(lt * 20);
    const cr = eio(seg(lt, 1.3, 2.9));
    if (cr <= 0) { const a = -0.4 + ramp(lt) * 0.25; look(v(-1.1 + Math.sin(a) * 3.4, Y + 1.9, -1.0 + Math.cos(a) * 3.4), v(-1.0, Y + 1.0, -1.0), 42); }
    else { const p = pathV(cr, [[0, [-0.2, Y + 2.0, 1.6]], [0.45, [0.2, Y + 0.6, 0.6]], [1, [0.5, 1.9, 2.4]]], (u) => u);
      look(p, lerpV(v(0.2, Y, 0.6), v(1.1, 1.45, -1.5), eio(seg(cr, 0.3, 1))), 44); }
  };

  // 11 FIX 4: parked between jobs, phone at his ear, smiling → push through the windscreen, fly along the gold timeline.
  SH[10] = (lt, d, w) => {
    show("C"); const Cc = sets.C.userData; Cc.timeline.visible = true;
    light({ key: [0xfff1d8, 1.15, [-4, 10, 4], [0, 0, -8]], hemi: [0xf4f6f4, 0x6d8753, 0.7], bg: 0xdfe5e1, fog: [0xdfe5e1, 30, 80], shadow: 18 });
    scroll(Cc, 0, 0);
    const grow = eio(seg(lt, w[0], w[4] + 0.4)); Cc.tlBar.scale.z = Math.max(0.01, grow); Cc.tlBar.position.z = -1 - 15 * grow;
    Cc.miles.forEach((m, i) => { const t0 = [w[5], w[9], w[12]][i]; m.position.y = lerp(-3, 0.3, K.back(seg(lt, t0 - 0.25, t0 + 0.3))); });
    act(lt, [-0.55, 0.3, 0.45], Math.PI, [[0, Object.assign({}, P.sit, P.phoneEar)]], [[0, "happy"], [w[1], "grin"]], { hold: "phone", seed: 13 });
    const turn = w[4] + 0.05;
    if (lt < turn) { const u = eio(seg(lt, 0, turn)); look(lerpV(v(-0.1, 2.3, -1.75), v(-0.25, 2.2, -1.35), u), v(-0.55, 1.95, 0.45), 42); }
    else { const z = kf(lt, [[turn, -1.2], [w[5] + 0.35, -1.6], [w[9] + 0.35, -8.6], [w[12] + 0.35, -15.6], [d, -17.0]]);
      const tx = kf(lt, [[w[5], -0.35], [w[9], 0.35], [w[12], -0.35]]);
      look(v(tx * 0.5, 2.3, z), v(tx, 1.2, z - 6.4), 42); }
  };

  // 12 PROBLEM 5: busy montage on the beat → giant ADS ON toggle flicked OFF, lights dim → calendar flips to an empty month
  SH[11] = (lt, d, w) => {
    const m1 = w[2] - 0.05, m2 = w[5] - 0.1, c3 = w[11] - 0.1;
    if (lt < m2) {
      show("D"); light({ key: [0xffe8c8, 0.9, [4, 8, 6], [0, 1, -1]], hemi: [0xf2efe6, 0x5a4636, 0.55], bg: 0x2a211a });
      const shot = lt < m1 ? 0 : Math.min(2, Math.floor((lt - m1) / ((m2 - m1) / 3)));
      if (shot === 0) { act(lt, [-1.6, 0, -1.3], Math.PI - 0.5, [[0, P.chase]], [[0, "determined"]], { hold: "driver", seed: 14 }); dec.J.elR.rotation.x += 0.2 * Math.sin(lt * 30);
        const a = ramp(lt, 0.6, 0.3); look(v(0.2 + Math.sin(a) * 0.4, 2.3, 2.6), v(-1.7, 1.75, -1.4), 42); }
      if (shot === 1) { act(lt, [0.2, 0, 0.3], 0.5, [[0, { lSx: -1.2, rSx: -0.6, lE: -0.4, rE: -1.2, lean: 0.3, twist: 0.3 }]], [[0, "frustrated"]], { seed: 15 });
        dec.J.shR.rotation.x += 0.4 * Math.sin(lt * 16); look(v(0.6, 1.9, 4.2), v(0.3, 1.55, 0.3), 40); }
      if (shot === 2) { act(lt, [2.6, 0, -1.25], Math.PI, [[0, P.work]], [[0, "determined"]], { hold: "driver", seed: 16 }); dec.J.elR.rotation.x += 0.15 * Math.sin(lt * 24);
        look(v(1.6, 2.9, 1.2), v(2.6, 2.3, -2.0), 38); }
    } else if (lt < c3) {
      show("I"); sets.I.userData.tone(true); extras.toggle.visible = true;
      const flick = eio(seg(lt, w[10] - 0.15, w[10] + 0.05)), dim = seg(lt, w[10], w[10] + 0.25);
      light({ key: [0xffd9a0, lerp(1.1, 0.25, dim), [-4, 9, 6], [0, 1, 0]], hemi: [0x6f9c8a, 0x0c2a22, lerp(0.55, 0.22, dim)], bg: C.pine });
      extras.toggle.position.set(0.55, 0, -0.4); extras.toggle.userData.set(flick);
      const lean = eo(seg(lt, w[7], w[10]));
      act(lt, [lerp(-1.35, -1.0, lean), 0, 0.55], Math.PI / 2 - 0.2, [[0, "idle"], [w[7], "push"], [w[10] + 0.1, Object.assign({}, P.push, { lean: 0.55 })]], [[0, "determined"], [w[10] + 0.1, "neutral"]], { seed: 17 });
      const u = eio(seg(lt, m2, c3)); look(v(lerp(0.6, 0.3, u), 0.55, lerp(8.0, 7.2, u)), v(-0.05, 2.25, 0), 44);
    } else {
      show("H"); const H = sets.H.userData; H.stamp.visible = false; H.dust.forEach((p) => (p.visible = false));
      light({ key: [0x9fc2b4, 0.25, [3, 9, 4], [0, 1, 0]], hemi: [0x5f8c7c, 0x0c2a22, 0.35], p1: [0xffc27a, 2.2, [0, 3.8, 0], 9], bg: 0x112620 });
      H.cal.userData.pages.forEach((p, i) => { if (i === 3) { p.rotation.x = 0; return; } const t0 = c3 + 0.15 + i * 0.32; p.rotation.x = -eio(seg(lt, t0, t0 + 0.3)) * 2.9; });
      act(lt, [0.3, 0, -1.2], 0, [[0, sitP("idle")], [w[15], Object.assign({}, P.sit, P.slump, { lSx: -0.9, rSx: -0.9, lE: -1.2, rE: -1.2, headX: 0.45 }), 0.5]], [[0, "knit"], [w[15], "defeated"]], { seed: 18 });
      const u = eio(seg(lt, c3, d)); look(lerpV(v(-0.4, 2.7, 1.1), v(0.1, 2.6, 5.4), u), lerpV(v(-0.4, 2.7, -2.35), v(0.0, 1.75, -1.0), u), lerp(36, 40, u));
    }
  };

  // 13 FIX 5: toggle snaps back ON, padlock clicks shut; job cards (DOM); Dec crosses his arms → crane up to three vans.
  SH[12] = (lt, d, w) => {
    const cut = w[14] - 0.25;
    if (lt < cut) {
      show("I"); sets.I.userData.tone(true); extras.toggle.visible = true; extras.lock.visible = true;
      light(FIXL());
      extras.toggle.position.set(0.55, 0, -0.6); extras.toggle.userData.set(1 - eio(seg(lt, w[0] - 0.05, w[0] + 0.12)));
      const ld = seg(lt, w[3], w[4]); extras.lock.position.set(0.55, lerp(6.5, 1.1, ld * ld), 0.5); extras.lock.userData.sh.position.y = lt > w[4] ? 0.37 : 0.55;
      extras.lock.rotation.y = 0.15;
      act(lt, [-1.05, 0, 0.9], 0.45, [[0, "idle"], [w[9], "cross"]], [[0, "determined"], [w[9], "grin"]], { seed: 19 });
      const u = eio(seg(lt, 0, cut)); look(v(lerp(-0.1, -0.4, u), lerp(2.0, 2.3, u), lerp(8.0, 8.6, u)), v(-0.15, 2.2, 0), 40);
    } else {
      const l2 = lt - cut; show("B"); const B = sets.B.userData; B.night(0);
      light({ key: [0xfff1d8, 1.15, [-8, 12, 14], [4, 0, 6]], hemi: [0xdfe9e4, 0x2f4a3c, 0.7], bg: 0xc6ccc8, shadow: 16 });
      B.van.position.set(4.5, 0, 6.6); B.van.rotation.y = Math.PI / 2; B.van.userData.body.position.y = 0; B.van.userData.body.rotation.x = 0;
      B.vans.forEach((x, i) => { x.visible = true; x.position.set(i ? 6.95 : 2.05, 0, 6.6); x.rotation.y = Math.PI / 2; });
      act(lt, [4.4, 0, 9.9], 0.0, [[0, "cross"]], [[0, "grin"]], { seed: 20 });
      const u = eio(seg(l2, 0, d - cut)); look(lerpV(v(4.4, 1.9, 13.6), v(4.4, 10.5, 17.5), u), lerpV(v(4.4, 1.7, 9.0), v(4.4, 0.8, 6.8), u), 44);
    }
  };

  // 14 THE SYSTEM: five extruded blocks stack into a tower; Dec jumps on top, arms up; it glows. 180° orbit.
  SH[13] = (lt, d, w) => {
    show("I", "Tower"); sets.I.userData.tone(true);
    light({ key: [0xffd9a0, 1.1, [-4, 11, 6], [0, 2, 0]], hemi: [0x6f9c8a, 0x0c2a22, 0.55], bg: C.pine, shadow: 10 });
    const T = sets.Tower.userData;
    T.blocks.forEach((b, i) => { const t0 = w[Math.min(i, 4)] - 0.12, u = seg(lt, t0, t0 + 0.32);
      b.visible = lt > t0 - 0.05; b.position.set(0, lerp(10, 0.31 + i * 0.66, u * u), 0); b.rotation.y = (1 - u) * 0.6 + (i % 2) * 0.06;
      b.scale.set(1, lt > t0 + 0.32 ? 1 - 0.18 * Math.exp(-(lt - t0 - 0.32) * 10) : 1, 1); });
    const top = 0.31 + 4 * 0.66 + 0.33, j0 = w[6] - 0.25, j1 = w[6] + 0.35, ju = seg(lt, j0, j1);
    act(lt, [lerp(1.9, 0, ju), lt < j0 ? 0 : lt < j1 ? lerp(0, top, ju) + Math.sin(ju * Math.PI) * 1.6 : top, lerp(0.6, 0.05, ju)], lerp(-0.6, 0.3, ju),
      [[0, "idle"], [j0, { lSz: 0.6, rSz: -0.6, squash: 0.85 }, 0.15], [j0 + 0.2, "cheer", 0.2]], [[0, "happy"], [j0, "celebrate"]], { seed: 21 });
    const gl = seg(lt, w[9] - 0.1, w[9] + 0.3); extras.glow.visible = gl > 0; extras.glow.material.opacity = 0.35 * gl;
    extras.glow.position.set(0, 2.6, -0.8); extras.glow.scale.setScalar(1 + 0.05 * Math.sin(lt * 8));
    const a = kf(lt, [[0, -0.35], [w[4] + 0.4, 0.15], [d, Math.PI - 0.35]]);
    look(v(Math.sin(a) * 10.5, lerp(2.4, 3.6, eio(seg(lt, w[5], d))), Math.cos(a) * 10.5), v(0, lerp(1.9, 3.1, eio(seg(lt, w[3], w[6] + 0.5))), 0), 40);
  };

  // 15 END CARD: pine, the house + van from B as a faint dusk silhouette far back; Dec waves beside the wordmark.
  SH[14] = (lt, d, w) => {
    show("I", "B"); sets.I.userData.tone(true); sets.I.userData.curve.visible = false; sets.I.userData.wall.visible = false;
    const B = sets.B.userData; B.night(1); B.vans.forEach((x) => (x.visible = false)); B.van.position.set(4.5, 0, 6.6);
    sets.B.position.set(-3, -0.02, -34);
    light({ key: [0xffd9a0, 0.9, [-4, 9, 8], [0, 1, 0]], hemi: [0x6f9c8a, 0x0c2a22, 0.5], bg: C.pine, fog: [C.pine, 18, 46], shadow: 8 });
    act(lt, [1.0, 0, 0.6], -0.35, [[0, "idle"], [0.4, "wave"]], [[0, "happy"], [0.4, "grin"]], { seed: 22 });
    if (lt > 0.4) dec.J.shR.rotation.z += 0.25 * Math.sin((lt - 0.4) * 12);
    const u = eio(seg(lt, 0, d)); look(lerpV(v(0.45, 1.75, 6.4), v(0.45, 1.85, 7.6), u), v(0.25, 2.2, 0), 40);
  };

  WORLD.sceneAt = (T) => { const S = TM.scenes; for (let i = S.length - 1; i >= 0; i--) if (T >= S[i].start) return i; return 0; };
  WORLD.render = (T) => {
    const i = WORLD.sceneAt(T), sc = TM.scenes[i], lt = T - sc.start;
    hideAll(); sets.B.position.set(0, 0, 0); sets.I.userData.curve.visible = true; sets.I.userData.wall.visible = true; sets.I.userData.strip.visible = false;
    sets.A.userData.clock.visible = true; sets.A.userData.cone.visible = true;
    SH[i](lt, sc.dur, W(i));
    K.inkUniforms.uTime.value = Math.floor(T * 8) / 8;                 // ink lines "boil" at 8 fps
    R.render(scene, cam);
    WORLD.last = { i, lt };
  };
  /* project a world point to frame pixels (for DOM cards that follow 3D things) */
  WORLD.toScreen = (p) => { const q = p.clone().project(cam); return { x: (q.x + 1) / 2 * 1080, y: (1 - q.y) / 2 * 1920 }; };
})();
