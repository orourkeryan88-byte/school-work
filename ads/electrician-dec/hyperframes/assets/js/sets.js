/* The location library (A–I) and props. Each set is a THREE.Group built once; shots.js shows one (or two) at a time.
   Sets keep handles to anything that moves in S.<name>.h. Scale: Dec is ~2.1 units tall. */
(function () {
  const C = K.C, S = (window.SETS = {});
  const FONT = "'Instrument Sans', sans-serif", MONO = "'IBM Plex Mono', monospace", SERIF = "'Instrument Serif', serif";
  S.FONT = FONT; S.MONO = MONO; S.SERIF = SERIF;
  const add = (g, m, x = 0, y = 0, z = 0, ry = 0) => { m.position.set(x, y, z); m.rotation.y = ry; g.add(m); return m; };
  const R = (w, h, d, r, c, o) => K.rbox(w, h, d, r, c, o);

  // ---- textures ----
  const speckle = (base, dots, n = 9000, a = 0.35, size = 2) => K.tex(512, 512, (x, w, h) => {
    x.fillStyle = base; x.fillRect(0, 0, w, h);
    for (let i = 0; i < n; i++) { x.fillStyle = dots[i % dots.length]; x.globalAlpha = a * K.hash(i + 7); x.fillRect(K.hash(i) * w, K.hash(i + 5e4) * h, size, size); }
    x.globalAlpha = 1;
  });
  const pebble = speckle("#d7d8d2", ["#8f948e", "#b9bcb5", "#f2f2ee", "#6d726c"], 14000, 0.55, 3);
  pebble.wrapS = pebble.wrapT = THREE.RepeatWrapping; pebble.repeat.set(3, 2);
  const grain = (base) => { const t = speckle(base, ["#00000022"], 2500, 0.25, 2); t.wrapS = t.wrapT = THREE.RepeatWrapping; return t; };
  /* text card texture: lines = [{t, font, color, y}] on a rounded card */
  S.cardTex = (w, h, bg, lines, o = {}) => K.tex(w, h, (x) => {
    x.fillStyle = bg; x.beginPath(); x.roundRect(0, 0, w, h, o.r || 36); x.fill();
    if (o.rim) { x.strokeStyle = o.rim; x.lineWidth = o.rimW || 14; x.beginPath(); x.roundRect(7, 7, w - 14, h - 14, (o.r || 36) - 6); x.stroke(); }
    lines.forEach((l) => { x.fillStyle = l.c; x.font = l.f; x.textAlign = l.a || "left"; x.textBaseline = "middle"; x.fillText(l.t, l.x === undefined ? 48 : l.x, l.y); });
  });

  // ---- lights shared by all sets (shots.js sets their colour/intensity per shot) ----
  S.lights = (scene) => {
    const key = new THREE.DirectionalLight(0xffe3b8, 1.2); key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0006; key.shadow.normalBias = 0.02;
    const kc = key.shadow.camera; kc.left = -9; kc.right = 9; kc.top = 9; kc.bottom = -9; kc.near = 0.5; kc.far = 60;
    const hemi = new THREE.HemisphereLight(0xcfe0d8, 0x0c2a22, 0.65);
    const p1 = new THREE.PointLight(0xffb85a, 0, 9, 1.6); p1.castShadow = true; p1.shadow.mapSize.set(1024, 1024); p1.shadow.bias = -0.002;
    const p2 = new THREE.PointLight(0xbfe6ff, 0, 6, 2);
    scene.add(key, key.target, hemi, p1, p2);
    return { key, hemi, p1, p2 };
  };

  // ======================================== PROPS ========================================
  S.van = (scale = 1) => {
    const g = new THREE.Group(), body = new THREE.Group(); g.add(body); g.scale.setScalar(scale);
    const side = K.tex(1024, 400, (x, w, h) => {
      x.fillStyle = "#f3f4f2"; x.fillRect(0, 0, w, h);
      x.fillStyle = K.hex(C.gold); x.fillRect(0, 250, w, 46);
      x.fillStyle = K.hex(C.ink); x.font = `700 132px ${FONT}`; x.textBaseline = "alphabetic"; x.fillText("rewires", 70, 190);
      const wd = x.measureText("rewires").width; x.fillStyle = K.hex(C.goldDeep); x.fillText(".co", 70 + wd, 190);
      x.fillStyle = K.hex(C.graphite); x.font = `500 30px ${MONO}`; x.fillText("FULL REWIRES · SAFE ELECTRIC REG.", 76, 352);
    });
    add(body, R(3.3, 1.95, 1.9, 0.32, C.cloud), -0.35, 1.45, 0);                    // box
    add(body, R(1.25, 1.2, 1.86, 0.3, C.cloud), 1.55, 1.05, 0);                      // bonnet / cab front
    const ws = R(0.12, 0.85, 1.6, 0.06, 0x24312d); ws.position.set(1.32, 1.95, 0); ws.rotation.z = -0.42; body.add(ws);   // windscreen
    [-1, 1].forEach((s) => {
      const win = R(0.75, 0.62, 0.06, 0.08, 0x24312d, { ink: 0.6 }); win.position.set(0.95, 2.0, s * 0.94); body.add(win);
      const dec = K.plane(2.7, 1.05, side, { lit: true }); dec.position.set(-0.45, 1.42, s * 0.957); if (s < 0) dec.rotation.y = Math.PI; body.add(dec);
      if (s < 0) { dec.scale.x = 1; }
    });
    add(body, R(0.25, 0.22, 1.95, 0.08, C.graphite), 2.18, 0.62, 0);               // bumper
    add(body, R(0.25, 0.22, 1.95, 0.08, C.graphite), -2.0, 0.62, 0);
    [-1, 1].forEach((s) => { const l = K.sphere(0.13, 0xfff4d6, { ink: 0.6 }); l.scale.set(0.5, 1, 1); l.position.set(2.2, 1.12, s * 0.66); body.add(l); });
    const wheels = [];
    [[1.3, 1], [1.3, -1], [-1.5, 1], [-1.5, -1]].forEach(([x, s]) => {
      const w = new THREE.Group(); w.position.set(x, 0.42, s * 0.88); g.add(w); wheels.push(w);
      const t = K.cyl(0.42, 0.42, 0.34, C.ink, { seg: 24 }); t.rotation.x = Math.PI / 2; w.add(t);
      const hub = K.cyl(0.2, 0.2, 0.36, C.fog, { seg: 18, ink: 0.5 }); hub.rotation.x = Math.PI / 2; w.add(hub);
    });
    g.userData = { body, wheels };
    return g;
  };
  S.laptop = (screenTex) => {
    const g = new THREE.Group();
    add(g, R(0.9, 0.05, 0.62, 0.03, C.graphite), 0, 0.025, 0);
    const lid = new THREE.Group(); lid.position.set(0, 0.05, -0.3); lid.rotation.x = -0.28; g.add(lid);
    add(lid, R(0.9, 0.6, 0.04, 0.03, C.graphite), 0, 0.3, 0);
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.82, 0.52), new THREE.MeshBasicMaterial({ map: screenTex, toneMapped: false }));
    scr.position.set(0, 0.3, 0.022); lid.add(scr);
    g.userData = { lid, scr }; return g;
  };
  S.mug = () => { const g = new THREE.Group(); add(g, K.cyl(0.08, 0.075, 0.18, C.cloud), 0, 0.09, 0);
    const h = K.mesh(new THREE.TorusGeometry(0.05, 0.016, 8, 16), K.toon(C.cloud)); h.position.set(0.09, 0.1, 0); g.add(h);
    add(g, K.cyl(0.07, 0.07, 0.01, 0x7a5236, { ink: 0 }), 0, 0.165, 0); return g; };
  S.papers = (n = 6) => { const g = new THREE.Group();
    for (let i = 0; i < n; i++) { const p = R(0.42, 0.012, 0.56, 0.004, i % 3 ? C.cloud : 0xf2ead8, { ink: 0.5 }); p.position.set((K.hash(i) - 0.5) * 0.06, i * 0.016, (K.hash(i + 3) - 0.5) * 0.06); p.rotation.y = (K.hash(i + 9) - 0.5) * 0.3; g.add(p); }
    return g; };
  S.ladder = () => { const g = new THREE.Group();
    [-1, 1].forEach((s) => { [-0.32, 0.32].forEach((x) => { const r = K.cyl(0.035, 0.035, 2.2, C.graphite, { seg: 8 }); r.position.set(x, 1.05, s * 0.32); r.rotation.x = -s * 0.17; g.add(r); }); });
    for (let i = 0; i < 5; i++) add(g, R(0.66, 0.04, 0.16, 0.015, C.fog), 0, 0.35 + i * 0.38, 0.3 - i * 0.065);
    add(g, R(0.72, 0.06, 0.5, 0.02, C.fog), 0, 2.12, 0); return g; };
  S.consumerUnit = () => { const g = new THREE.Group(); add(g, R(1.0, 0.7, 0.22, 0.05, C.cloud), 0, 0, 0);
    add(g, R(0.86, 0.22, 0.06, 0.02, C.fog), 0, 0.05, 0.12);
    for (let i = 0; i < 10; i++) add(g, R(0.06, 0.16, 0.05, 0.01, i === 0 ? C.goldDeep : C.graphite, { ink: 0.4 }), -0.37 + i * 0.082, 0.05, 0.16);
    return g; };
  S.fuseBoard = () => { const g = new THREE.Group(); add(g, R(0.9, 0.75, 0.08, 0.02, C.wood), 0, 0, 0);
    for (let i = 0; i < 6; i++) { const f = K.cyl(0.05, 0.05, 0.18, 0xf2efe6, { seg: 12 }); f.position.set(-0.3 + (i % 3) * 0.3, 0.15 - Math.floor(i / 3) * 0.3, 0.08); g.add(f); }
    return g; };
  S.drum = (r = 0.45) => { const g = new THREE.Group();
    const a = K.cyl(r, r, 0.07, C.woodL); a.rotation.z = Math.PI / 2; a.position.x = -0.3; g.add(a);
    const b = K.cyl(r, r, 0.07, C.woodL); b.rotation.z = Math.PI / 2; b.position.x = 0.3; g.add(b);
    const c = K.cyl(r * 0.78, r * 0.78, 0.55, C.graphite); c.rotation.z = Math.PI / 2; g.add(c); g.position.y = r; return g; };
  S.clock = () => { const g = new THREE.Group();
    const face = K.tex(256, 256, (x) => { x.fillStyle = "#f3f4f1"; x.beginPath(); x.arc(128, 128, 124, 0, 7); x.fill();
      x.fillStyle = K.hex(C.ink); for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; x.fillRect(128 + Math.sin(a) * 100 - 4, 128 - Math.cos(a) * 100 - 4, 8, 8); } });
    const rim = K.cyl(0.42, 0.42, 0.08, C.ink, { seg: 32 }); rim.rotation.x = Math.PI / 2; g.add(rim);
    const f = new THREE.Mesh(new THREE.CircleGeometry(0.38, 32), K.toon(0xffffff, { map: face })); f.position.z = 0.045; g.add(f);
    const mk = (len, w, c) => { const p = new THREE.Group(); p.position.z = 0.06; const m = R(w, len, 0.02, w / 2.2, c, { ink: 0 }); m.position.y = len / 2 - 0.04; p.add(m); g.add(p); return p; };
    g.userData = { hr: mk(0.22, 0.045, C.ink), mn: mk(0.32, 0.03, C.ink) };
    g.userData.set = (h, m, gold) => { g.userData.hr.rotation.z = -((h % 12) + m / 60) / 12 * 6.283; g.userData.mn.rotation.z = -m / 60 * 6.283;
      [g.userData.hr, g.userData.mn].forEach((p) => p.children[0].material = K.toon(gold ? C.goldDeep : C.ink)); };
    return g; };
  S.domino = (n, gold) => { const g = new THREE.Group();
    const t = K.tex(256, 512, (x, w, h) => { x.fillStyle = K.hex(C.cloud); x.fillRect(0, 0, w, h); x.fillStyle = K.hex(C.graphite); x.fillRect(30, 252, 196, 8);
      x.fillStyle = gold ? K.hex(C.goldDeep) : K.hex(C.ink); x.font = `700 200px ${FONT}`; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText(n, 128, 128);
      x.font = `500 44px ${MONO}`; x.fillText("PROBLEM", 128, 380); });
    const body = R(0.9, 1.7, 0.32, 0.1, gold ? C.gold : C.cloud); body.position.y = 0.85; g.add(body);
    const face = K.plane(0.74, 1.48, t, { lit: true }); face.position.set(0, 0.85, 0.162); g.add(face);
    return g; };
  S.toggle = () => { const g = new THREE.Group();
    add(g, R(2.2, 3.2, 0.5, 0.35, C.cloud), 0, 1.6, 0);
    add(g, R(1.3, 2.1, 0.2, 0.25, C.fog), 0, 1.6, 0.28);
    const lev = new THREE.Group(); lev.position.set(0, 1.6, 0.35); g.add(lev);
    const l = R(0.8, 1.15, 0.6, 0.28, C.gold); l.position.set(0, 0.48, 0.18); lev.add(l);
    const lab = (txt) => K.tex(640, 180, (x) => { x.font = `700 118px ${FONT}`; x.textAlign = "center"; x.textBaseline = "middle"; x.lineJoin = "round";
      x.lineWidth = 16; x.strokeStyle = K.hex(C.ink); x.strokeText(txt, 320, 94); x.fillStyle = K.hex(C.gold); x.fillText(txt, 320, 94); });
    const on = K.plane(1.9, 0.53, lab("ADS ON")); on.position.set(0, 3.6, 0.1); g.add(on);
    const off = K.plane(1.9, 0.53, lab("ADS OFF")); off.position.set(0, 3.6, 0.1); g.add(off);
    g.userData = { lev, on, off, lever: l };
    g.userData.set = (u) => { lev.rotation.x = K.lerp(-0.55, 0.55, u); on.visible = u < 0.5; off.visible = u >= 0.5;
      l.material = K.toon(u < 0.5 ? C.gold : C.graphite); };
    return g; };
  S.padlock = () => { const g = new THREE.Group();
    add(g, R(0.9, 0.75, 0.4, 0.14, C.gold), 0, 0, 0);
    const sh = new THREE.Group(); g.add(sh); sh.position.y = 0.37;
    const arc = K.mesh(new THREE.TorusGeometry(0.28, 0.08, 10, 24, Math.PI), K.toon(C.graphite)); sh.add(arc);
    [-0.28, 0.28].forEach((x) => { const leg = K.cyl(0.08, 0.08, 0.2, C.graphite, { seg: 12 }); leg.position.set(x, -0.1, 0); sh.add(leg); });
    add(g, K.cyl(0.07, 0.07, 0.05, C.ink, { seg: 12 }), 0, -0.05, 0.21).rotation.x = Math.PI / 2;
    g.userData = { sh }; return g; };
  S.block = (word, gold) => { const g = new THREE.Group();
    add(g, R(2.6, 0.62, 0.9, 0.12, gold ? C.gold : C.cloud), 0, 0, 0);
    const t = S.cardTex(1024, 240, "rgba(0,0,0,0)", [{ t: word, f: `700 150px ${FONT}`, c: K.hex(gold ? C.ink : C.ink), a: "center", x: 512, y: 124 }]);
    const p = K.plane(2.3, 0.54, t, { lit: true }); p.position.z = 0.455; g.add(p);
    const p2 = K.plane(2.3, 0.54, t, { lit: true }); p2.position.z = -0.455; p2.rotation.y = Math.PI; g.add(p2);
    return g; };
  S.calendar = () => { const g = new THREE.Group();
    add(g, R(1.3, 1.5, 0.06, 0.04, C.cloud), 0, 0, 0);
    const pages = [];
    const month = (name, full) => K.tex(400, 460, (x) => { x.fillStyle = "#f6f6f3"; x.fillRect(0, 0, 400, 460);
      x.fillStyle = K.hex(C.ink); x.font = `700 46px ${FONT}`; x.fillText(name, 26, 60);
      for (let i = 0; i < 35; i++) { const cx = 26 + (i % 7) * 50, cy = 100 + Math.floor(i / 7) * 66;
        x.strokeStyle = "#c6ccc8"; x.lineWidth = 2; x.strokeRect(cx, cy, 46, 60);
        if (full && K.hash(i + name.length) < full) { x.fillStyle = K.hex(C.goldDeep); x.fillRect(cx + 5, cy + 30, 36, 14); } } });
    [["MARCH", 0.85], ["APRIL", 0.7], ["MAY", 0.4], ["JUNE", 0]].forEach(([n, f], i) => {
      const pv = new THREE.Group(); pv.position.set(0, 0.7, 0.04 + (3 - i) * 0.004); g.add(pv);
      const pg = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 1.38), K.toon(0xffffff, { map: month(n, f), side: THREE.DoubleSide })); pg.position.y = -0.69; pv.add(pg);
      pages.push(pv);
    });
    g.userData = { pages }; return g; };
  S.phoneBig = (tex) => { const g = new THREE.Group();
    add(g, R(0.55, 1.0, 0.09, 0.09, 0x1b2220), 0, 0, 0);
    const s = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.86), K.glow(0x2b4a40)); s.position.z = 0.047; g.add(s);
    g.userData = { scr: s }; return g; };
  S.tree = (s = 1, c = C.hedge) => { const g = new THREE.Group(); add(g, K.cyl(0.08, 0.1, 0.8, C.wood, { seg: 8 }), 0, 0.4, 0);
    add(g, K.sphere(0.5, c), 0, 1.1, 0); add(g, K.sphere(0.36, c), 0.25, 1.35, 0.1); g.scale.setScalar(s); return g; };
  S.cloudPuff = (s = 1) => { const g = new THREE.Group();
    [[0, 0, 0, 1], [0.9, -0.15, 0, 0.75], [-0.9, -0.2, 0.1, 0.7], [0.3, 0.45, -0.1, 0.7]].forEach(([x, y, z, r]) => add(g, K.sphere(r, C.cloud, { ink: 0.6 }), x, y, z));
    g.scale.set(s, s * 0.7, s * 0.8); return g; };

  // house facade (semi-d): pebble-dash, pitched roof, windows with frames; night = glowing windows
  S.house = (o = {}) => {
    const g = new THREE.Group(), wins = [];
    const wallMat = o.render ? K.toon(C.cloud) : K.toon(0xffffff, { map: pebble });
    const wall = K.mesh(K.rboxGeo(8, 5.6, 7, 0.08), wallMat); wall.position.set(0, 2.8, 0); g.add(wall);
    const roofS = new THREE.Shape(); roofS.moveTo(-4.4, 0); roofS.lineTo(4.4, 0); roofS.lineTo(0, 2.6); roofS.closePath();
    const roof = K.mesh(new THREE.ExtrudeGeometry(roofS, { depth: 7.4, bevelEnabled: false }), K.toon(o.roof || C.graphite));
    roof.position.set(0, 5.6, -3.7); g.add(roof);
    const glass = (x, y, w, h) => {
      add(g, R(w + 0.24, h + 0.24, 0.12, 0.05, C.cloud), x, y, 3.53);
      const p = R(w, h, 0.06, 0.03, 0x22302c, { ink: 0 }); p.position.set(x, y, 3.58); g.add(p); wins.push(p);
      if (o.blinds) { const b = R(w - 0.04, h - 0.04, 0.03, 0.01, C.fog, { ink: 0 }); b.position.set(x, y, 3.6); g.add(b); }
      add(g, R(0.06, h, 0.08, 0.02, C.cloud, { ink: 0 }), x, y, 3.62);
    };
    glass(-1.9, 1.6, 1.8, 1.25); glass(-1.9, 4.1, 1.5, 1.1); glass(1.5, 4.1, 1.1, 1.0);
    add(g, R(1.15, 2.2, 0.14, 0.06, o.door || C.pine2), 1.5, 1.1, 3.55);                          // door
    add(g, R(1.9, 0.18, 1.2, 0.05, C.fog), 1.5, 0.09, 4.1);                                        // step
    add(g, R(0.08, 0.08, 0.06, 0.02, C.gold, { ink: 0.4 }), 1.85, 1.15, 3.66);                     // handle
    g.userData = { wins };
    g.userData.night = (u) => wins.forEach((w, i) => w.material = u > 0.5 && i !== 2 ? K.glow(0xf0b455) : K.toon(0x22302c));
    return g;
  };

  // ======================================== SETS ========================================
  const built = {};
  S.get = (name) => built[name] || (built[name] = S["build" + name]());

  /* I: infinite cyc. dark = pine, else cloud. */
  S.buildI = () => {
    const g = new THREE.Group(), sh = new THREE.Shape();
    sh.moveTo(-40, 0); sh.lineTo(-40, 30); sh.lineTo(40, 30); sh.lineTo(40, 0);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(80, 40), K.toon(C.cloud)); floor.rotation.x = -Math.PI / 2; floor.position.z = 4; floor.receiveShadow = true; g.add(floor);
    const curve = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 80, 24, 1, true, Math.PI, Math.PI / 2), K.toon(C.cloud, { side: THREE.BackSide }));
    curve.rotation.z = Math.PI / 2; curve.position.set(0, 6, -10); curve.receiveShadow = true; g.add(curve);
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(80, 40), K.toon(C.cloud)); wall.position.set(0, 26, -16); wall.receiveShadow = true; g.add(wall);
    const strip = new THREE.Group(); g.add(strip);                                              // floorboard strip (scene 3)
    for (let i = 0; i < 18; i++) { const b = R(0.95, 0.06, 2.1, 0.02, i % 2 ? C.wood : 0x7d5f44, { ink: 0.5 }); b.position.set(-8 + i * 0.98, 0.03, 0); strip.add(b); }
    g.userData = { floor, curve, wall, strip, mats: [floor.material, curve.material, wall.material] };
    g.userData.tone = (dark) => { const c = dark ? C.pine : C.cloud; floor.material = K.toon(c); curve.material = K.toon(c, { side: THREE.BackSide }); wall.material = K.toon(c); };
    return g;
  };

  /* A: box room at night (or morning). Desk against the window, laptop, tea, invoices, vest on the chair. */
  S.buildA = () => {
    const g = new THREE.Group(), h = {};
    const floor = R(8, 0.2, 7, 0.02, 0x6b5440, { ink: 0 }); floor.position.set(0, -0.1, 0); floor.material = K.toon(0xffffff, { map: grain("#6b5440") }); g.add(floor);
    const wallC = 0x1f3c33;
    const back = R(8, 5, 0.2, 0.02, wallC, { ink: 0 }); back.position.set(0, 2.5, -2.6); g.add(back);
    const sideW = R(0.2, 5, 7, 0.02, wallC, { ink: 0 }); sideW.position.set(-3.2, 2.5, 0.8); g.add(sideW);
    // window: frame + night outside (neighbours, streetlight) + rain streaks
    const win = new THREE.Group(); win.position.set(0.3, 2.35, -2.48); g.add(win); h.win = win;
    const out = K.tex(512, 400, (x, w, hh) => { const gr = x.createLinearGradient(0, 0, 0, hh); gr.addColorStop(0, "#0a1f19"); gr.addColorStop(1, "#163a30"); x.fillStyle = gr; x.fillRect(0, 0, w, hh);
      x.fillStyle = "#0b1a16"; [[0, 210, 200, 190], [230, 240, 160, 160], [400, 200, 140, 200]].forEach(([a, b, c, d]) => { x.fillRect(a, b, c, d); x.beginPath(); x.moveTo(a - 10, b); x.lineTo(a + c / 2, b - 70); x.lineTo(a + c + 10, b); x.fill(); });
      x.fillStyle = "#f0b455"; [[40, 280], [120, 290], [270, 300], [440, 260], [470, 330]].forEach(([a, b]) => x.fillRect(a, b, 26, 30));
      const sl = x.createRadialGradient(330, 150, 2, 330, 150, 70); sl.addColorStop(0, "rgba(255,210,140,.95)"); sl.addColorStop(1, "rgba(255,210,140,0)"); x.fillStyle = sl; x.fillRect(240, 60, 180, 180);
      x.fillStyle = "#0b1a16"; x.fillRect(326, 150, 8, 250); });
    const day = K.tex(512, 400, (x, w, hh) => { const gr = x.createLinearGradient(0, 0, 0, hh); gr.addColorStop(0, "#c6ccc8"); gr.addColorStop(1, "#e7e9e6"); x.fillStyle = gr; x.fillRect(0, 0, w, hh);
      x.fillStyle = "#9aa39d"; [[0, 210, 200, 190], [230, 240, 160, 160], [400, 200, 140, 200]].forEach(([a, b, c, d]) => { x.fillRect(a, b, c, d); x.beginPath(); x.moveTo(a - 10, b); x.lineTo(a + c / 2, b - 70); x.lineTo(a + c + 10, b); x.fill(); }); });
    const glass = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.9), new THREE.MeshBasicMaterial({ map: out, toneMapped: false })); win.add(glass); h.glass = glass; h.out = out; h.day = day;
    [[0, 1.0, 2.9, 0.16], [0, -1.0, 2.9, 0.16], [-1.37, 0, 0.16, 2.1], [1.37, 0, 0.16, 2.1], [0, 0, 0.08, 1.9]].forEach(([x, y, w, hh]) => add(win, R(w, hh, 0.16, 0.03, C.cloud), x, y, 0.06));
    add(win, R(3.0, 0.12, 0.45, 0.03, C.cloud), 0, -1.1, 0.2);                                     // sill
    const rain = new THREE.Group(); win.add(rain); h.rain = [];
    for (let i = 0; i < 46; i++) { const d = new THREE.Mesh(new THREE.PlaneGeometry(0.012, 0.16 + K.hash(i) * 0.2), new THREE.MeshBasicMaterial({ color: 0xcfe0d8, transparent: true, opacity: 0.35 + K.hash(i + 1) * 0.3 }));
      d.userData = { x: (K.hash(i + 2) - 0.5) * 2.5, s: 1.2 + K.hash(i + 3) * 1.6, o: K.hash(i + 4) * 3 }; d.position.z = 0.03; rain.add(d); h.rain.push(d); }
    // desk + kit
    const desk = new THREE.Group(); desk.position.set(0.3, 0, -1.6); g.add(desk); h.desk = desk;
    add(desk, R(3.0, 0.12, 1.3, 0.04, C.wood), 0, 1.0, 0);
    [[-1.35, -0.5], [1.35, -0.5], [-1.35, 0.5], [1.35, 0.5]].forEach(([x, z]) => add(desk, R(0.1, 0.95, 0.1, 0.03, C.wood), x, 0.47, z));
    h.screenTex = K.tex(820, 520, (x, w, hh) => { x.fillStyle = "#f3f4f1"; x.fillRect(0, 0, w, hh); x.fillStyle = "#d9ddd9"; x.fillRect(0, 0, w, 60);
      x.fillStyle = "#c6ccc8"; for (let i = 0; i < 4; i++) x.fillRect(40, 100 + i * 100, 480, 60); x.fillStyle = "#e9c48a"; x.fillRect(560, 100, 220, 360); });
    const lap = S.laptop(h.screenTex); lap.position.set(0.15, 1.06, 0.1); desk.add(lap); h.lap = lap;
    const mug = S.mug(); mug.position.set(-0.75, 1.06, 0.2); desk.add(mug);
    const pp = S.papers(7); pp.position.set(1.0, 1.06, -0.1); desk.add(pp);
    const pp2 = S.papers(4); pp2.position.set(0.95, 1.17, 0.0); pp2.rotation.y = 0.4; desk.add(pp2);
    // desk lamp: base, arm, head, warm pool
    const lamp = new THREE.Group(); lamp.position.set(-1.15, 1.06, -0.25); desk.add(lamp); h.lamp = lamp;
    add(lamp, K.cyl(0.16, 0.18, 0.05, C.ink), 0, 0.025, 0);
    const a1 = K.cyl(0.025, 0.025, 0.8, C.ink, { seg: 8 }); a1.position.set(0.1, 0.4, 0); a1.rotation.z = -0.25; lamp.add(a1);
    const hd = K.cyl(0.07, 0.2, 0.22, C.ink, { seg: 18 }); hd.position.set(0.32, 0.78, 0.05); hd.rotation.z = 0.9; lamp.add(hd);
    const bulb = K.sphere(0.07, 0xfff0c8, { ink: 0, mat: K.glow(0xfff0c8) }); bulb.position.set(0.38, 0.72, 0.05); lamp.add(bulb);
    const cone = new THREE.Mesh(new THREE.ConeGeometry(0.75, 1.1, 24, 1, true), new THREE.MeshBasicMaterial({ color: 0xf0b455, transparent: true, opacity: 0.09, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
    cone.position.set(0.55, 0.25, 0.05); cone.rotation.z = 0.55; lamp.add(cone); h.cone = cone;
    // chair with the vest on the back
    const chair = new THREE.Group(); chair.position.set(0.15, 0, -0.35); g.add(chair); h.chair = chair;
    add(chair, R(1.0, 0.14, 0.9, 0.06, C.pine2), 0, 0.42, 0);
    add(chair, R(1.0, 1.1, 0.14, 0.08, C.pine2), 0, 1.0, 0.45);
    add(chair, R(0.94, 0.7, 0.18, 0.08, C.gold), 0, 1.05, 0.5);                                      // hi-vis over the back
    add(chair, R(0.96, 0.05, 0.2, 0.02, C.graphite, { ink: 0.5 }), 0, 1.0, 0.5);
    add(chair, K.cyl(0.06, 0.06, 0.38, C.graphite, { seg: 8 }), 0, 0.18, 0);
    // wall clock (morning shot) + a shelf
    const clk = S.clock(); clk.position.set(2.5, 3.6, -2.45); g.add(clk); h.clock = clk; clk.userData.set(8, 2);
    add(g, R(1.6, 0.08, 0.4, 0.02, C.wood), -2.0, 3.2, -2.35);
    const files = [[0.18, 0.5, C.gold], [0.18, 0.46, C.cloud], [0.18, 0.52, C.graphite]];
    files.forEach(([w, hh, c], i) => add(g, R(w, hh, 0.3, 0.02, c, { ink: 0.6 }), -2.5 + i * 0.22, 3.24 + hh / 2, -2.35));
    g.userData = h; return g;
  };

  /* B: driveway / front of house, overcast morning (or dusk). Van, low wall, bin, gate, clouds. */
  S.buildB = () => {
    const g = new THREE.Group(), h = {};
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), K.toon(0x6f8a5c)); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; g.add(ground);
    const drive = R(4.6, 0.06, 10, 0.02, 0x9a9e98, { ink: 0 }); drive.position.set(4.3, 0.03, 4); drive.material = K.toon(0xffffff, { map: grain("#a3a7a1") }); g.add(drive);
    const path = R(1.4, 0.05, 4.5, 0.02, C.fog, { ink: 0 }); path.position.set(1.5, 0.03, 6); g.add(path);
    const road = R(80, 0.04, 6, 0.01, 0x4a504c, { ink: 0 }); road.position.set(0, 0.02, 13); g.add(road);
    const house = S.house(); g.add(house); h.house = house;
    const twin = S.house({ door: C.graphite }); twin.position.x = 8.0; twin.scale.x = -1; g.add(twin); h.twin = twin;
    // low wall with a gap for the drive and the gate
    [[-3.2, 6.4], [9.5, 2.6]].forEach(([x, w]) => add(g, R(w, 0.7, 0.35, 0.06, C.fog), x, 0.35, 9.0));
    const gate = new THREE.Group(); gate.position.set(1.5, 0, 9.0); g.add(gate);
    for (let i = 0; i < 6; i++) add(gate, K.cyl(0.03, 0.03, 0.9, C.graphite, { seg: 6 }), -0.6 + i * 0.24, 0.45, 0);
    add(gate, R(1.4, 0.06, 0.06, 0.02, C.graphite), 0, 0.82, 0);
    const bin = new THREE.Group(); bin.position.set(-0.6, 0, 7.6); g.add(bin);
    add(bin, R(0.75, 1.1, 0.8, 0.08, C.pine2), 0, 0.55, 0); add(bin, R(0.82, 0.1, 0.88, 0.04, C.pine3), 0, 1.15, 0);
    const van = S.van(); van.position.set(4.3, 0, 4.2); van.rotation.y = -Math.PI / 2; g.add(van); h.van = van;
    const vans = [S.van(), S.van()]; vans.forEach((v, i) => { v.position.set(4.3 + (i ? 4.6 : -9.6), 0, 4.2); v.rotation.y = -Math.PI / 2; v.visible = false; g.add(v); }); h.vans = vans;
    h.clouds = [];
    [[-8, 15, -20, 2.6], [6, 17, -24, 3.2], [16, 13, -18, 2.2], [-18, 12, -14, 2.0]].forEach(([x, y, z, s]) => { const c = S.cloudPuff(s); c.position.set(x, y, z); g.add(c); h.clouds.push(c); });
    const lamps = [];
    [[-6, 12], [12, 12]].forEach(([x, z]) => { const p = new THREE.Group(); p.position.set(x, 0, z); g.add(p);
      add(p, K.cyl(0.08, 0.1, 4.5, C.graphite, { seg: 8 }), 0, 2.25, 0); const hd = R(0.5, 0.2, 0.3, 0.05, C.graphite); hd.position.set(0.2, 4.5, 0); p.add(hd);
      const b = K.sphere(0.14, C.gold, { ink: 0 }); b.position.set(0.25, 4.36, 0); p.add(b); lamps.push(b); });
    h.lamps = lamps;
    h.night = (u) => { house.userData.night(u); twin.userData.night(u); lamps.forEach((b) => (b.material = u > 0.5 ? K.glow(0xffd28c) : K.toon(C.fog))); };
    g.userData = h; return g;
  };

  /* C: inside the van cab. Dash, wheel, phone holder, coffee, receipts; wet country road outside. */
  S.buildC = () => {
    const g = new THREE.Group(), h = {};
    add(g, R(3.4, 0.7, 1.2, 0.2, C.graphite), 0, 1.25, -1.3);                                          // dash
    add(g, R(3.4, 0.2, 0.7, 0.1, 0x3d4542), 0, 1.65, -1.55);
    const wheel = K.mesh(new THREE.TorusGeometry(0.42, 0.06, 10, 28), K.toon(C.ink)); wheel.position.set(-0.55, 1.75, -0.75); wheel.rotation.x = -0.9; g.add(wheel); h.wheel = wheel;
    add(g, K.cyl(0.06, 0.06, 0.5, C.ink, { seg: 8 }), -0.55, 1.6, -0.95).rotation.x = -0.9;
    // phone in holder
    const ph = S.phoneBig(); ph.scale.setScalar(0.42); ph.position.set(0.45, 1.98, -0.9); ph.rotation.x = -0.25; g.add(ph); h.phone = ph;
    add(g, R(0.06, 0.25, 0.06, 0.02, C.ink), 0.45, 1.75, -0.95);
    // windscreen pillars + roof edge
    [-1.65, 1.65].forEach((x) => { const p = R(0.16, 1.7, 0.16, 0.05, C.graphite); p.position.set(x, 2.45, -1.55); p.rotation.x = 0.35; g.add(p); });
    add(g, R(3.5, 0.18, 0.5, 0.05, C.graphite), 0, 3.25, -1.25);
    // seats
    [-0.55, 0.85].forEach((x) => { add(g, R(0.95, 0.25, 0.9, 0.12, C.char), x, 0.95, 0.4); add(g, R(0.95, 1.3, 0.25, 0.12, C.char), x, 1.65, 0.85); });
    const cup = K.cyl(0.08, 0.065, 0.2, C.cloud); cup.position.set(0.7, 1.18, 0.3); g.add(cup); add(g, K.cyl(0.085, 0.085, 0.03, C.graphite), 0.7, 1.3, 0.3);
    const rc = S.papers(3); rc.scale.set(0.6, 1, 0.5); rc.position.set(1.0, 1.08, 0.45); g.add(rc);
    // outside: road + verges + hedges scrolling toward camera
    const road = new THREE.Mesh(new THREE.PlaneGeometry(5, 80), K.toon(0x3d4340)); road.rotation.x = -Math.PI / 2; road.position.set(0, 0.3, -40); g.add(road);
    const verge = new THREE.Mesh(new THREE.PlaneGeometry(60, 80), K.toon(C.field)); verge.rotation.x = -Math.PI / 2; verge.position.set(0, 0.28, -40); g.add(verge);
    h.dashes = []; for (let i = 0; i < 14; i++) { const d = R(0.1, 0.02, 1.4, 0.01, C.cloud, { ink: 0 }); d.position.set(0, 0.32, -i * 5); g.add(d); h.dashes.push(d); }
    h.hedges = []; for (let i = 0; i < 26; i++) { const s = i % 2 ? 1 : -1; const b = K.sphere(0.9 + K.hash(i) * 0.4, C.hedge); b.position.set(s * (3.6 + K.hash(i + 1)), 0.9, -i * 3); b.scale.y = 0.8; g.add(b); h.hedges.push(b); }
    h.timeline = new THREE.Group(); g.add(h.timeline); h.timeline.visible = false;                        // gold timeline (fix 4)
    const tl = R(0.22, 0.04, 30, 0.02, C.gold, { ink: 0.6 }); tl.material = K.glow(0xf0b455); tl.position.set(0, 0.35, -16); h.timeline.add(tl); h.tlBar = tl;
    h.miles = [["1 MIN", "Text them"], ["5 MIN", "Call them"], ["DAILY", "Follow up"]].map(([a, b], i) => {
      const m = new THREE.Group(); m.position.set(i % 2 ? 0.35 : -0.35, 0.3, -8 - i * 7); m.scale.setScalar(0.82); h.timeline.add(m);
      add(m, K.cyl(0.06, 0.06, 0.8, C.graphite, { seg: 8 }), i % 2 ? 0.7 : -0.7, 0.4, 0);
      const t = S.cardTex(640, 300, K.hex(C.cloud), [{ t: a, f: `700 120px ${FONT}`, c: K.hex(C.goldDeep), y: 110 }, { t: b, f: `500 64px ${MONO}`, c: K.hex(C.ink), y: 220 }], { rim: K.hex(C.ink), rimW: 8 });
      const bd = R(2.1, 1.0, 0.12, 0.08, C.cloud); bd.position.y = 1.0; m.add(bd);
      const p = K.plane(2.0, 0.94, t, { lit: true }); p.position.set(0, 1.0, 0.065); m.add(p); return m;
    });
    g.userData = h; return g;
  };

  /* D: customer's hallway mid-rewire (1970s): chased walls, new cable runs, boards up, old fuse board + new CU. */
  S.buildD = () => {
    const g = new THREE.Group(), h = {};
    for (let i = 0; i < 14; i++) { if (i === 5 || i === 6 || i === 10) continue;
      const b = R(0.48, 0.1, 6, 0.02, i % 2 ? 0x8a6a4c : 0x7a5d43, { ink: 0.4 }); b.position.set(-3.2 + i * 0.5, -0.05, 0); g.add(b); }
    add(g, R(7, 0.1, 6, 0, 0x2a211a, { ink: 0 }), 0, -0.4, 0);                                      // void under the lifted boards
    for (let i = 0; i < 5; i++) add(g, R(0.12, 0.3, 6, 0.02, C.woodL, { ink: 0.4 }), -0.55 + (i % 2) * 0.5 + (i > 2 ? 2 : 0), -0.25, 0);   // joists
    const wallT = K.tex(512, 512, (x, w, hh) => { x.fillStyle = "#e5ddc8"; x.fillRect(0, 0, w, hh);
      for (let i = 0; i < 40; i++) { x.fillStyle = i % 2 ? "#d7ccb2" : "#efe7d2"; x.fillRect(i * 13, 0, 6, hh); } });   // 70s stripe wallpaper
    const back = new THREE.Mesh(new THREE.PlaneGeometry(9, 4.2), K.toon(0xffffff, { map: wallT })); back.position.set(0, 2.1, -2.2); back.receiveShadow = true; g.add(back);
    const side = new THREE.Mesh(new THREE.PlaneGeometry(6, 4.2), K.toon(0xffffff, { map: wallT })); side.position.set(-3.5, 2.1, 0.8); side.rotation.y = Math.PI / 2; side.receiveShadow = true; g.add(side);
    // chases (raw plaster grooves) with cable runs
    [[-2.2, 2.1, 0.16, 3.6], [0.4, 3.1, 0.16, 2.0], [-0.9, 3.8, 3.2, 0.16]].forEach(([x, y, w, hh]) => {
      add(g, R(w, hh, 0.04, 0.02, 0xa79a83, { ink: 0.4 }), x, y, -2.17);
      const c = R(w > hh ? w : 0.05, w > hh ? 0.05 : hh, 0.05, 0.02, C.cloud, { ink: 0.4 }); c.position.set(x, y, -2.13); g.add(c); });
    const fb = S.fuseBoard(); fb.position.set(1.3, 2.6, -2.12); g.add(fb);
    const cu = S.consumerUnit(); cu.position.set(2.6, 2.6, -2.05); g.add(cu); h.cu = cu;
    const sheet = R(2.2, 0.3, 1.6, 0.14, C.fog); sheet.position.set(-1.6, 0.15, 0.6); sheet.rotation.y = 0.2; g.add(sheet);
    const lad = S.ladder(); lad.position.set(-0.7, 0, -0.9); lad.rotation.y = 0.35; g.add(lad); h.ladder = lad;
    const ph = new THREE.Group(); ph.position.set(-0.68, 2.2, -0.86); g.add(ph); h.phone = ph;
    const pp = S.phoneBig(); pp.scale.setScalar(0.38); pp.rotation.x = -Math.PI / 2; pp.position.y = 0.03; ph.add(pp); h.phoneScr = pp.userData.scr;
    const dr = S.drum(0.4); dr.position.set(2.4, 0, 0.6); g.add(dr);
    g.userData = h; return g;
  };

  /* E: attic (y ≥ 3.4) over a landing (y = 0). Joists, insulation, drums, swinging work light, the hatch. */
  S.buildE = () => {
    const g = new THREE.Group(), h = {};
    const Y = 3.4, hx = 0.2, hz = 0.6;                                                                 // hatch opening centre
    for (let i = 0; i < 11; i++) { const x = -3 + i * 0.6; if (Math.abs(x - hx) < 0.6) {
        [[-1.9, 2.8], [3.1, 3.2]].forEach(([z, L]) => add(g, R(0.14, 0.24, L, 0.03, C.wood), x, Y, z + 0.0 + (z < 0 ? -0.6 : 0.2)));
      } else add(g, R(0.14, 0.24, 7, 0.03, C.wood), x, Y, 0); }
    for (let i = 0; i < 4; i++) { const r = K.cyl(0.32, 0.32, 1.8, 0xd9b77a, { seg: 18 }); r.rotation.z = Math.PI / 2; r.position.set(-2.3 + (i % 2) * 0.1, Y + 0.44, -2 + i * 0.7); if (i === 3) r.position.set(2.4, Y + 0.44, 1.6); g.add(r); }
    const dr = S.drum(0.35); dr.position.set(2.0, Y, -1.4); g.add(dr);
    const roofL = new THREE.Mesh(new THREE.PlaneGeometry(9, 4.4), K.toon(0x2a2119, { side: THREE.DoubleSide })); roofL.position.set(0, Y + 1.7, -1.9); roofL.rotation.x = 0.85; g.add(roofL);
    for (let i = 0; i < 8; i++) { const rf = R(0.12, 0.2, 4.4, 0.03, C.wood); rf.position.set(-3.5 + i, Y + 1.6, -1.8); rf.rotation.x = -0.72; g.add(rf); }
    const backW = new THREE.Mesh(new THREE.PlaneGeometry(9, 4), K.toon(0x2a2119)); backW.position.set(0, Y + 1.5, -3.6); g.add(backW);
    // hatch frame + light coming up
    [[hx, hz - 0.62, 1.2, 0.1], [hx, hz + 0.62, 1.2, 0.1]].forEach(([x, z, w, d]) => add(g, R(w, 0.1, d, 0.02, C.fog), x, Y + 0.05, z));
    const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.85, 3.0, 4, 1, true), new THREE.MeshBasicMaterial({ color: 0xffe2b0, transparent: true, opacity: 0.1, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide }));
    beam.rotation.y = Math.PI / 4; beam.position.set(hx, Y + 1.2, hz); g.add(beam);
    // swinging work light
    const wl = new THREE.Group(); wl.position.set(-0.4, Y + 3.0, -0.4); g.add(wl); h.wl = wl;
    const cord = K.cyl(0.012, 0.012, 1.4, C.ink, { seg: 6, ink: 0 }); cord.position.y = -0.7; wl.add(cord);
    const cage = K.cyl(0.14, 0.2, 0.3, C.goldDeep, { seg: 10 }); cage.position.y = -1.5; wl.add(cage);
    const bulb = K.sphere(0.11, 0xfff3d6, { ink: 0, mat: K.glow(0xfff3d6) }); bulb.position.y = -1.6; wl.add(bulb); h.bulb = bulb;
    // landing below
    add(g, R(7, 0.12, 6, 0.02, 0x5a4636, { ink: 0 }), 0, -0.06, 0);
    const lw = new THREE.Mesh(new THREE.PlaneGeometry(9, 3.4), K.toon(0xd9d3c3)); lw.position.set(0, 1.7, -2.4); lw.receiveShadow = true; g.add(lw);
    add(g, R(7, 0.14, 0.14, 0.04, C.wood), 0, 1.0, 2.2);
    for (let i = 0; i < 12; i++) add(g, R(0.06, 1.0, 0.06, 0.02, C.cloud, { ink: 0.4 }), -3.2 + i * 0.58, 0.5, 2.2);
    const ceil = new THREE.Mesh(new THREE.PlaneGeometry(9, 6), K.toon(0xe8e4d8, { side: THREE.DoubleSide })); ceil.rotation.x = Math.PI / 2; ceil.position.set(0, Y - 0.15, -2.5); ceil.scale.y = 0.6; g.add(ceil);
    const ledge = R(1.1, 0.9, 0.5, 0.05, C.wood); ledge.position.set(1.7, 0.45, -1.9); g.add(ledge);   // hall table
    const ph = S.phoneBig(); ph.scale.setScalar(0.4); ph.position.set(1.7, 0.95, -1.85); ph.rotation.x = -1.2; g.add(ph); h.phone = ph;
    const clk = S.clock(); clk.position.set(0.85, 2.35, -2.35); g.add(clk); h.clock = clk;
    g.userData = h; h.Y = Y; h.hatch = [hx, hz]; return g;
  };

  /* F: country road to Naas, tilt-shift miniature: patchwork fields, hedgerows, winding road, NAAS 38 sign. */
  S.buildF = () => {
    const g = new THREE.Group(), h = {};
    const cols = [C.field, C.field2, 0x6d8753, 0x899e6a, 0x56704a];
    for (let i = 0; i < 6; i++) for (let j = 0; j < 8; j++) {
      const f = R(5.6, 0.2, 5.6, 0.06, cols[(i * 3 + j * 2) % 5], { ink: 0.5 }); f.position.set(-15 + i * 6, -0.1, -40 + j * 6); g.add(f);
      for (let k = 0; k < 7; k++) { const b = K.sphere(0.32, C.hedge, { ink: 0.5 }); b.position.set(-15 + i * 6 - 2.9 + k * 0.95, 0.18, -40 + j * 6 + 2.9); b.scale.y = 0.85; g.add(b); }
      if (K.hash(i * 9 + j) > 0.7) { const t = S.tree(0.9 + K.hash(i + j) * 0.5); t.position.set(-15 + i * 6 + 1.5, 0, -40 + j * 6 - 1.2); g.add(t); }
    }
    const pts = [[2, -42], [-1.5, -32], [3, -22], [-2, -12], [2.5, -2], [0, 8]].map(([x, z]) => new THREE.Vector3(x, 0.08, z));
    const curve = new THREE.CatmullRomCurve3(pts); h.curve = curve;
    const N = 160, pos = [], idx = [];
    for (let i = 0; i <= N; i++) { const p = curve.getPointAt(i / N), tg = curve.getTangentAt(i / N), n = new THREE.Vector3(-tg.z, 0, tg.x).normalize();
      pos.push(p.x + n.x * 1.2, 0.09, p.z + n.z * 1.2, p.x - n.x * 1.2, 0.09, p.z - n.z * 1.2); if (i < N) { const a = i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
    const rg = new THREE.BufferGeometry(); rg.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); rg.setIndex(idx); rg.computeVertexNormals();
    const road = new THREE.Mesh(rg, K.toon(0x474d49, { side: THREE.DoubleSide })); road.receiveShadow = true; g.add(road);
    const van = S.van(0.42); g.add(van); h.van = van;
    const sign = new THREE.Group(); g.add(sign); h.sign = sign;
    const st = S.cardTex(512, 256, K.hex(C.cloud), [{ t: "NAAS 38", f: `700 118px ${FONT}`, c: K.hex(C.ink), a: "center", x: 256, y: 132 }], { rim: K.hex(C.ink), rimW: 12, r: 20 });
    add(sign, K.cyl(0.05, 0.05, 1.6, C.graphite, { seg: 8 }), 0, 0.8, 0);
    const board = new THREE.Group(); board.position.y = 1.6; sign.add(board); h.board = board;
    add(board, R(1.7, 0.85, 0.08, 0.06, C.cloud), 0, 0, 0);
    const sp = K.plane(1.6, 0.8, st, { lit: true }); sp.position.z = 0.045; board.add(sp);
    const sp2 = K.plane(1.6, 0.8, st, { lit: true }); sp2.position.z = -0.045; sp2.rotation.y = Math.PI; board.add(sp2);
    g.userData = h; return g;
  };

  /* G: the empty house in Naas: modern semi-d, rendered walls, blinds down, no car, leaves blowing. */
  S.buildG = () => {
    const g = new THREE.Group(), h = {};
    const ground = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), K.toon(0x6f8a5c)); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; g.add(ground);
    const drive = R(4.6, 0.06, 9, 0.02, 0xa3a7a1, { ink: 0 }); drive.position.set(4.3, 0.03, 4); g.add(drive);
    add(g, R(1.6, 0.05, 4.5, 0.02, C.fog, { ink: 0 }), 1.5, 0.03, 6);
    const house = S.house({ render: true, blinds: true, roof: C.ink, door: C.ink }); g.add(house);
    const twin = S.house({ render: true, blinds: true, roof: C.ink, door: C.graphite }); twin.position.x = 8; twin.scale.x = -1; g.add(twin);
    h.leaves = []; for (let i = 0; i < 14; i++) { const l = R(0.16, 0.02, 0.1, 0.01, i % 3 ? C.goldDeep : C.tan, { ink: 0.4 }); g.add(l); h.leaves.push(l); }
    g.userData = h; return g;
  };

  /* H: kitchen table, evening: paperwork, wall calendar, kettle, radio, phone face down. */
  S.buildH = () => {
    const g = new THREE.Group(), h = {};
    add(g, R(9, 0.1, 7, 0, 0x4f4136, { ink: 0 }), 0, -0.05, 0);
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), K.toon(0x23443a)); wall.position.set(0, 2.5, -2.4); wall.receiveShadow = true; g.add(wall);
    add(g, R(10, 1.0, 0.7, 0.04, C.pine2), 0, 0.5, -2.05);                                            // worktop run
    add(g, R(10, 0.08, 0.75, 0.02, C.woodL), 0, 1.04, -2.05);
    const kettle = new THREE.Group(); kettle.position.set(-2.4, 1.08, -2.0); g.add(kettle);
    add(kettle, K.cyl(0.22, 0.27, 0.45, C.fog), 0, 0.23, 0); add(kettle, R(0.08, 0.3, 0.08, 0.03, C.ink), 0.28, 0.3, 0);
    const radio = new THREE.Group(); radio.position.set(2.1, 1.08, -2.0); g.add(radio);
    add(radio, R(0.8, 0.45, 0.3, 0.08, C.goldDeep), 0, 0.23, 0); add(radio, K.cyl(0.11, 0.11, 0.04, C.ink), -0.18, 0.24, 0.16).rotation.x = Math.PI / 2;
    add(radio, R(0.28, 0.2, 0.04, 0.02, C.fog, { ink: 0.4 }), 0.16, 0.24, 0.16);
    const table = new THREE.Group(); g.add(table); h.table = table;
    add(table, R(3.2, 0.14, 1.9, 0.05, C.wood), 0, 0.95, 0);
    [[-1.45, -0.8], [1.45, -0.8], [-1.45, 0.8], [1.45, 0.8]].forEach(([x, z]) => add(table, R(0.12, 0.9, 0.12, 0.03, C.wood), x, 0.45, z));
    const pp = S.papers(6); pp.position.set(-0.6, 1.02, 0.1); table.add(pp);
    const pp2 = S.papers(3); pp2.position.set(0.5, 1.02, 0.3); pp2.rotation.y = -0.5; table.add(pp2);
    const ph = S.phoneBig(); ph.scale.setScalar(0.32); ph.rotation.x = Math.PI / 2; ph.position.set(0.9, 1.04, -0.25); table.add(ph); h.phone = ph;
    const mug = S.mug(); mug.position.set(-1.2, 1.02, -0.4); table.add(mug);
    const cal = S.calendar(); cal.position.set(-0.4, 2.7, -2.35); g.add(cal); h.cal = cal;
    const chair = new THREE.Group(); chair.position.set(0.3, 0, -1.25); chair.rotation.y = Math.PI; g.add(chair);
    add(chair, R(0.9, 0.12, 0.8, 0.05, C.wood), 0, 0.42, 0); add(chair, R(0.9, 1.0, 0.1, 0.05, C.wood), 0, 0.95, 0.4);
    [[-0.38, -0.33], [0.38, -0.33], [-0.38, 0.33], [0.38, 0.33]].forEach(([x, z]) => add(chair, R(0.08, 0.4, 0.08, 0.02, C.wood), x, 0.2, z));
    const pend = new THREE.Group(); pend.position.set(0, 4.2, 0); g.add(pend);
    add(pend, K.cyl(0.01, 0.01, 1.2, C.ink, { seg: 6, ink: 0 }), 0, 0.6, 0);
    add(pend, K.cyl(0.12, 0.45, 0.35, C.ink, { seg: 20 }), 0, -0.1, 0);
    add(pend, K.sphere(0.1, 0xfff0c8, { ink: 0, mat: K.glow(0xfff0c8) }), 0, -0.25, 0);
    const stamp = new THREE.Group(); g.add(stamp); h.stamp = stamp; stamp.visible = false;
    add(stamp, R(1.7, 0.5, 0.9, 0.12, C.gold), 0, 0, 0);
    const jt = S.cardTex(700, 300, "rgba(0,0,0,0)", [{ t: "JUNK", f: `700 210px ${FONT}`, c: K.hex(C.ink), a: "center", x: 350, y: 160 }]);
    const jp = K.plane(1.5, 0.64, jt, { lit: true }); jp.rotation.x = -Math.PI / 2; jp.position.y = 0.255; stamp.add(jp);
    h.dust = []; for (let i = 0; i < 10; i++) { const d = K.sphere(0.16, C.fog, { ink: 0.5 }); d.visible = false; g.add(d); h.dust.push(d); }
    g.userData = h; return g;
  };

  /* Kildare miniature (fix 2): a round plinth of fields, lanes and toy houses, plus 24 lead tiles. */
  S.buildMap = () => {
    const g = new THREE.Group(), h = {};
    add(g, K.cyl(4.2, 4.3, 0.5, C.cloud, { seg: 48 }), 0, 0.25, 0);
    const cols = [C.field, C.field2, 0x6d8753, 0x899e6a];
    for (let i = 0; i < 26; i++) { const a = K.hash(i) * 6.283, r = Math.sqrt(K.hash(i + 40)) * 3.3;
      const f = R(1.1 + K.hash(i + 2) * 0.6, 0.1, 0.9 + K.hash(i + 3) * 0.6, 0.05, cols[i % 4], { ink: 0.4 }); f.position.set(Math.cos(a) * r, 0.55, Math.sin(a) * r); f.rotation.y = K.hash(i + 5) * 3; g.add(f); }
    for (let i = 0; i < 9; i++) { const a = K.hash(i + 70) * 6.283, r = 0.8 + K.hash(i + 80) * 2.4;
      const hs = new THREE.Group(); hs.position.set(Math.cos(a) * r, 0.6, Math.sin(a) * r); g.add(hs);
      add(hs, R(0.3, 0.24, 0.24, 0.03, C.cloud, { ink: 0.4 }), 0, 0.12, 0); const rf = R(0.34, 0.08, 0.28, 0.02, C.graphite, { ink: 0.4 }); rf.position.y = 0.28; hs.add(rf); }
    h.tiles = []; for (let i = 0; i < 24; i++) { const a = (i / 24) * 6.283 + K.hash(i + 200) * 0.3, r = 1.1 + K.hash(i + 300) * 2.5;
      const t = R(0.32, 0.12, 0.32, 0.04, C.fog, { ink: 0.5 }); t.position.set(Math.cos(a) * r, 0.7, Math.sin(a) * r); t.userData.good = [3, 8, 13, 17, 21].includes(i); g.add(t); h.tiles.push(t); }
    g.userData = h; return g;
  };

  /* Ad → Video → Form tiles with glowing cables (fix 3). */
  S.buildFlow = () => {
    const g = new THREE.Group(), h = {};
    const tile = (txt, y, gold) => { const t = new THREE.Group(); t.position.set(0, y, 0); g.add(t);
      add(t, R(1.9, 1.4, 0.5, 0.2, gold ? C.gold : C.cloud), 0, 0, 0);
      const tx = S.cardTex(512, 380, "rgba(0,0,0,0)", [{ t: txt, f: `700 120px ${FONT}`, c: K.hex(C.ink), a: "center", x: 256, y: gold ? 300 : 196 }]);
      const p = K.plane(1.7, 1.26, tx, { lit: true }); p.position.z = 0.26; t.add(p); return t; };
    h.ad = tile("Ad", 6.2); h.video = tile("Video", 3.7, true); h.form = tile("Form", 1.2);
    const play = new THREE.Shape(); play.moveTo(-0.18, 0.24); play.lineTo(0.26, 0); play.lineTo(-0.18, -0.24); play.closePath();
    h.play = K.extrude(play, 0.08, C.ink, { bevel: 0.02 }); h.play.position.set(0.03, 0.12, 0.3); h.video.add(h.play);
    h.cables = [[5.5, 4.4], [3.0, 1.9]].map(([a, b]) => { const c = new THREE.CatmullRomCurve3([K.v3(0, a, 0), K.v3(0.35, (a + b) / 2, 0.3), K.v3(0, b, 0)]);
      const m = new THREE.Mesh(new THREE.TubeGeometry(c, 30, 0.07, 8), K.glow(0xf0b455)); g.add(m); m.userData.curve = c; return m; });
    h.sparks = [0, 1].map(() => { const s = K.sphere(0.12, 0xfff3d6, { ink: 0, mat: K.glow(0xfff3d6) }); g.add(s); return s; });
    g.userData = h; return g;
  };

  /* The system tower (5 extruded blocks) and the end-card dusk silhouettes. */
  S.buildTower = () => { const g = new THREE.Group(), h = {};
    h.blocks = ["Offer", "Message", "Video", "Speed", "Always on"].map((w, i) => { const b = S.block(w, i === 4); g.add(b); return b; });
    g.userData = h; return g; };
})();
