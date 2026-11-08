/* Dec, the rewires.co sparky. Original design, built from toon-shaded primitives with the ink outline.
   Stocky, short-legged, ~3.2 heads tall. Gold hi-vis vest with two grey reflective bands over a pine long-sleeve,
   charcoal work trousers with knee-pad pockets, tan boots, tool belt (screwdriver + voltage tester), pencil behind
   the right ear, pine cap with a cloud-white lightning-bolt patch. The brows do most of the acting.
   Feet at y = 0, facing +z.  dec.apply(pose, face, t) sets every joint; DEC.P / DEC.F are the pose and face library. */
(function () {
  const C = K.C, D = (window.DEC = {});

  // ---- mouth shapes (canvas, drawn once) ----
  const mouthTex = {};
  const MW = 256, MH = 128, inkC = K.hex(C.ink), lip = "#7a3b2a";
  const shapes = {
    flat: (x) => { x.lineCap = "round"; x.lineWidth = 14; x.strokeStyle = inkC; x.beginPath(); x.moveTo(78, 64); x.lineTo(178, 62); x.stroke(); },
    smile: (x) => { x.lineCap = "round"; x.lineWidth = 14; x.strokeStyle = inkC; x.beginPath(); x.moveTo(62, 46); x.quadraticCurveTo(128, 104, 194, 46); x.stroke(); },
    frown: (x) => { x.lineCap = "round"; x.lineWidth = 14; x.strokeStyle = inkC; x.beginPath(); x.moveTo(78, 84); x.quadraticCurveTo(128, 44, 178, 84); x.stroke(); },
    grin: (x) => { x.fillStyle = inkC; x.beginPath(); x.moveTo(40, 34); x.quadraticCurveTo(128, 150, 216, 34); x.closePath(); x.fill();
      x.fillStyle = "#f4f1ea"; x.beginPath(); x.moveTo(56, 42); x.quadraticCurveTo(128, 70, 200, 42); x.lineTo(196, 52); x.quadraticCurveTo(128, 76, 60, 52); x.fill();
      x.fillStyle = lip; x.beginPath(); x.ellipse(128, 92, 40, 12, 0, 0, Math.PI * 2); x.fill(); },
    O: (x) => { x.fillStyle = inkC; x.beginPath(); x.ellipse(128, 64, 30, 40, 0, 0, Math.PI * 2); x.fill();
      x.fillStyle = lip; x.beginPath(); x.ellipse(128, 86, 18, 10, 0, 0, Math.PI * 2); x.fill(); },
    grimace: (x) => { x.fillStyle = inkC; x.beginPath(); x.roundRect(44, 34, 168, 60, 26); x.fill();
      x.fillStyle = "#f4f1ea"; x.beginPath(); x.roundRect(56, 44, 144, 40, 14); x.fill();
      x.strokeStyle = inkC; x.lineWidth = 6; x.beginPath(); x.moveTo(56, 64); x.lineTo(200, 64);
      for (let i = 1; i < 6; i++) { x.moveTo(56 + i * 24, 44); x.lineTo(56 + i * 24, 84); } x.stroke(); },
    open: (x) => { x.fillStyle = inkC; x.beginPath(); x.moveTo(66, 40); x.quadraticCurveTo(128, 130, 190, 40); x.quadraticCurveTo(128, 56, 66, 40); x.fill(); },
  };
  for (const k in shapes) mouthTex[k] = K.tex(MW, MH, (x) => shapes[k](x));
  D.mouthTex = mouthTex;

  // ---- head skin texture: skin, cropped dark hair at the back/sides, fine stubble on the lower face ----
  const headTex = K.tex(512, 256, (x, w, h) => {
    x.fillStyle = K.hex(C.skin); x.fillRect(0, 0, w, h);
    x.fillStyle = "#2a231e";                                                          // tight crop: back + sides only
    x.beginPath(); x.ellipse(w * 0.75, h * 0.22, w * 0.27, h * 0.3, 0, 0, Math.PI * 2); x.fill();
    x.fillRect(w * 0.42, 0, w * 0.66, h * 0.2); x.fillRect(0, 0, w * 0.08, h * 0.2);
    [0.075, 0.425].forEach((u) => x.fillRect(w * (u - 0.03), h * 0.2, w * 0.06, h * 0.22));       // sideburns
    const sg = x.createRadialGradient(w * 0.25, h * 0.76, 4, w * 0.25, h * 0.76, w * 0.15);      // soft stubble shadow
    sg.addColorStop(0, "rgba(86,96,91,0.22)"); sg.addColorStop(0.75, "rgba(86,96,91,0.16)"); sg.addColorStop(1, "rgba(86,96,91,0)");
    x.fillStyle = sg; x.fillRect(0, h * 0.55, w * 0.5, h * 0.45);
    for (let i = 0; i < 5200; i++) {                                                  // fine-grain stubble dots
      const u = 0.1 + K.hash(i) * 0.3, v = 0.58 + K.hash(i + 9e3) * 0.32;
      const du = (u - 0.25) / 0.15, dv = (v - 0.76) / 0.15; if (du * du + dv * dv > 1) continue;
      x.fillStyle = `rgba(48,40,36,${0.1 + K.hash(i + 3e3) * 0.16})`; x.fillRect(u * w, v * h, 1.4, 1.4);
    }
  });

  D.make = function () {
    const root = new THREE.Group(), body = new THREE.Group(), hips = new THREE.Group(), spine = new THREE.Group();
    root.add(body); body.add(hips); hips.position.y = 0.64; hips.add(spine); spine.position.y = 0.1;
    const J = { root, body, hips, spine };

    // legs (no knees: a chunky toy read), boots, knee-pad pockets
    ["L", "R"].forEach((s, i) => {
      const leg = new THREE.Group(); leg.position.set(i ? -0.13 : 0.13, 0, 0); hips.add(leg); J["leg" + s] = leg;
      const l = K.capsule(0.12, 0.3, C.char); l.position.y = -0.3; leg.add(l);
      const pad = K.rbox(0.13, 0.12, 0.05, 0.03, C.graphite); pad.position.set(0, -0.3, 0.11); leg.add(pad);
      const boot = K.rbox(0.22, 0.15, 0.34, 0.07, C.tan); boot.position.set(0, -0.565, 0.05); leg.add(boot);
      const sole = K.rbox(0.23, 0.04, 0.35, 0.02, C.ink, { ink: 0 }); sole.position.set(0, -0.625, 0.05); leg.add(sole);
    });
    const pelvis = K.rbox(0.5, 0.22, 0.34, 0.09, C.char); pelvis.position.y = 0.0; hips.add(pelvis);
    const belt = new THREE.Group(); hips.add(belt); belt.position.y = 0.09; J.belt = belt;
    belt.add(K.rbox(0.54, 0.09, 0.38, 0.04, C.tan));
    const buckle = K.rbox(0.08, 0.07, 0.03, 0.015, C.fog); buckle.position.z = 0.19; belt.add(buckle);
    const pouch = K.rbox(0.12, 0.16, 0.1, 0.03, C.tan); pouch.position.set(-0.27, -0.06, 0.06); belt.add(pouch);
    const tester = new THREE.Group(); tester.position.set(-0.3, 0.02, 0.07); belt.add(tester);
    tester.add(K.rbox(0.04, 0.12, 0.03, 0.012, C.fog)); const tip = K.cyl(0.006, 0.006, 0.07, C.ink); tip.position.y = 0.09; tester.add(tip);
    const beltDriver = D.screwdriver(); beltDriver.position.set(0.27, -0.02, 0.07); beltDriver.rotation.z = Math.PI; belt.add(beltDriver); J.beltDriver = beltDriver;

    // torso: pine long-sleeve, gold vest, two reflective bands, pine placket where the vest is open
    const torso = K.rbox(0.58, 0.6, 0.38, 0.15, C.pine3); torso.position.y = 0.3; spine.add(torso);
    const vest = K.rbox(0.62, 0.5, 0.42, 0.15, C.gold); vest.position.y = 0.27; spine.add(vest);
    [0.16, 0.3].forEach((y) => { const b = K.rbox(0.635, 0.045, 0.435, 0.13, C.graphite, { ink: 0.6 }); b.position.y = y; spine.add(b); });
    const plk = K.rbox(0.07, 0.5, 0.03, 0.015, C.pine3, { ink: 0.6 }); plk.position.set(0, 0.28, 0.205); spine.add(plk);
    const collar = K.rbox(0.3, 0.06, 0.26, 0.03, C.pine3); collar.position.y = 0.6; spine.add(collar);
    const neck = K.cyl(0.09, 0.1, 0.12, C.skin); neck.position.y = 0.62; spine.add(neck);

    // arms: shoulder → elbow → hand. Hands are mittens; a thumb pops out for thumbs-up / grip.
    ["L", "R"].forEach((s, i) => {
      const sh = new THREE.Group(); sh.position.set(i ? -0.33 : 0.33, 0.5, 0); spine.add(sh); J["sh" + s] = sh;
      const up = K.capsule(0.088, 0.16, C.pine3); up.position.y = -0.14; sh.add(up);
      const el = new THREE.Group(); el.position.y = -0.29; sh.add(el); J["el" + s] = el;
      const fo = K.capsule(0.082, 0.14, C.pine3); fo.position.y = -0.11; el.add(fo);
      const cuff = K.cyl(0.085, 0.085, 0.04, C.pine2); cuff.position.y = -0.22; el.add(cuff);
      const hand = new THREE.Group(); hand.position.y = -0.3; el.add(hand); J["hand" + s] = hand;
      const palm = K.sphere(0.085, C.skin); palm.scale.set(1, 1.1, 0.85); hand.add(palm);
      const th = K.capsule(0.03, 0.06, C.skin); th.position.set(i ? 0.02 : -0.02, 0.07, 0.05); th.rotation.x = -0.3; th.visible = false; hand.add(th); J["thumb" + s] = th;
      const grip = new THREE.Group(); grip.position.set(0, -0.04, 0.06); hand.add(grip); J["grip" + s] = grip;   // props attach here
    });

    // head: oval, wider at the jaw; ears stick out; small oval eyes; thick brows; button nose
    const neckJ = new THREE.Group(); neckJ.position.y = 0.66; spine.add(neckJ); J.neck = neckJ;
    const head = new THREE.Group(); head.position.y = 0.3; neckJ.add(head); J.head = head;
    const hg = new THREE.SphereGeometry(0.3, 40, 28); const hp = hg.attributes.position;
    for (let i = 0; i < hp.count; i++) {
      let x = hp.getX(i), y = hp.getY(i), z = hp.getZ(i);
      const jaw = y < 0 ? 1 + 0.12 * Math.min(1, -y / 0.22) : 1;
      hp.setXYZ(i, x * jaw, y * 1.1, z * 0.95 * (y < 0 ? 1 + 0.04 * Math.min(1, -y / 0.25) : 1));
    }
    hg.computeVertexNormals();
    const skull = K.mesh(hg, K.toon(0xffffff, { map: headTex })); head.add(skull);
    const front = (x, y) => { const yy = y / 1.1 / 0.3; return 0.3 * 0.95 * Math.sqrt(Math.max(0, 1 - yy * yy - (x / 0.31) ** 2)) * (y < 0 ? 1.03 : 1); };
    [1, -1].forEach((s, i) => {
      const ear = K.sphere(0.075, C.skin); ear.scale.set(0.5, 1, 0.75); ear.position.set(s * 0.315, -0.01, -0.01); ear.rotation.y = s * 0.3; head.add(ear);
      const eye = new THREE.Group(); eye.position.set(s * 0.1, 0.0, front(0.1, 0.0) - 0.01); head.add(eye); J["eye" + (i ? "R" : "L")] = eye;
      const e = K.sphere(0.036, C.ink, { ink: 0 }); e.scale.set(0.82, 1.18, 0.5); eye.add(e);
      const gl = K.sphere(0.009, 0xffffff, { ink: 0, mat: K.flat(0xffffff) }); gl.position.set(s * -0.008 + 0.006, 0.014, 0.017); eye.add(gl);
      const brow = K.rbox(0.135, 0.046, 0.05, 0.02, 0x1a1512, { ink: 0.5 }); brow.position.set(s * 0.1, 0.08, front(0.1, 0.08) + 0.006); head.add(brow);
      J["brow" + (i ? "R" : "L")] = brow; brow.userData.y0 = 0.08;
    });
    const nose = K.sphere(0.044, C.skin); nose.scale.set(1.05, 0.9, 0.85); nose.position.set(0, -0.07, front(0, -0.07) + 0.008); head.add(nose);
    // mouth: a curved strip hugging the face, mapped with the current mouth shape
    const mg = new THREE.CylinderGeometry(0.29, 0.29, 0.13, 20, 1, true, -0.42, 0.84);
    const mouthMat = new THREE.MeshBasicMaterial({ map: mouthTex.smile, transparent: true, depthWrite: false, side: THREE.FrontSide });
    const mouth = new THREE.Mesh(mg, mouthMat); mouth.position.set(0, -0.165, front(0, -0.165) - 0.29 + 0.006); head.add(mouth);
    J.mouth = mouth; J.mouthMat = mouthMat;
    // cap: pine dome, brim forward, cloud-white bolt patch
    const cap = new THREE.Group(); head.add(cap); J.cap = cap;
    const dome = K.mesh(new THREE.SphereGeometry(0.318, 36, 14, 0, Math.PI * 2, 0, Math.PI * 0.43), K.toon(C.pine2));
    dome.scale.set(1.0, 1.08, 0.98); dome.position.y = 0.075; cap.add(dome);
    const button = K.sphere(0.03, C.pine2); button.position.y = 0.415; cap.add(button);
    const brimS = new THREE.Shape(); brimS.absellipse(0, 0, 0.25, 0.2, 0, Math.PI, false);
    const brim = K.extrude(brimS, 0.02, C.pine2, { bevel: 0.008 }); brim.rotation.x = Math.PI / 2 + 0.08; brim.position.set(0, 0.165, 0.29); cap.add(brim);
    const patch = K.extrude(K.bolt(0.17), 0.014, C.cloud, { bevel: 0.004, ink: 0.5 }); patch.position.set(0, 0.255, 0.272); patch.rotation.x = -0.62; cap.add(patch);
    const pencil = K.cyl(0.011, 0.011, 0.2, C.goldDeep); pencil.position.set(-0.3, 0.05, 0.02); pencil.rotation.set(0.15, 0, 1.25); head.add(pencil);
    const lead = K.cyl(0.0, 0.011, 0.03, C.woodL, { ink: 0.4 }); lead.position.y = -0.115; lead.rotation.x = Math.PI; pencil.add(lead);

    const dec = { root, J, holding: null, props: {} };
    dec.props.driver = D.screwdriver(); dec.props.driver.rotation.x = Math.PI / 2; J.gripR.add(dec.props.driver);
    dec.props.phone = D.phone(); dec.props.phone.rotation.x = -0.2; J.gripR.add(dec.props.phone);
    dec.props.phoneL = D.phone(); dec.props.phoneL.rotation.x = -0.2; J.gripL.add(dec.props.phoneL);
    dec.hold = (what) => {                                 // 'driver' | 'phone' | 'phoneL' | null
      for (const k in dec.props) dec.props[k].visible = k === what;
      J.beltDriver.visible = what !== "driver";
    };
    dec.hold(null);
    dec.apply = (p, f, t = 0, o = {}) => D.apply(dec, p, f, t, o);
    return dec;
  };

  D.screwdriver = () => {
    const g = new THREE.Group();
    const h = K.rbox(0.05, 0.13, 0.05, 0.02, C.graphite); g.add(h);
    const ring = K.cyl(0.028, 0.028, 0.02, C.fog, { ink: 0.5 }); ring.position.y = -0.065; g.add(ring);
    const shaft = K.cyl(0.009, 0.009, 0.17, C.fog, { ink: 0.5 }); shaft.position.y = -0.15; g.add(shaft);
    return g;
  };
  D.phone = (screenTex) => {
    const g = new THREE.Group();
    g.add(K.rbox(0.11, 0.2, 0.026, 0.02, 0x1b2220));                 // rugged dark case
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.085, 0.165), K.glow(0x2b4a40)); scr.position.z = 0.0135; g.add(scr);
    g.userData.screen = scr; return g;
  };

  // ---- pose & face library (radians / units). Missing keys = 0. -----------------------------------------------
  const P = (D.P = {
    idle:   { lSz: 0.12, rSz: -0.12, lE: -0.15, rE: -0.15 },
    wave:   { lSz: 0.12, lE: -0.15, rSz: -2.5, rE: -0.6, headZ: -0.08 },
    type:   { lSx: -1.1, rSx: -1.1, lE: -0.7, rE: -0.7, lSz: 0.12, rSz: -0.12, lean: 0.12 },
    leanIn: { lSx: -1.2, rSx: -1.2, lE: -0.6, rE: -0.6, lean: 0.32, headX: 0.12 },
    slump:  { lean: 0.38, headX: 0.38, lSx: 0.15, rSx: 0.15, lSz: 0.04, rSz: -0.04, squash: 0.93, drop: -0.04 },
    shrug:  { lSz: 0.55, rSz: -0.55, lE: -1.5, rE: -1.5, lSx: -0.2, rSx: -0.2, headZ: 0.14, lift: 0.04 },
    point:  { lSz: 0.12, lE: -0.15, rSx: -1.45, rSz: 0.1, rE: -0.12, lean: 0.06, headY: -0.15 },
    scratch:{ lSz: 0.12, lE: -0.15, rSx: -2.5, rSz: -0.7, rE: -2.0, headZ: 0.12, headX: -0.05 },
    thumbs: { lSz: 0.12, lE: -0.15, rSx: -0.9, rSz: -0.25, rE: -1.5, thumb: 1 },
    phoneEar:{ lSz: 0.12, lE: -0.15, rSx: -0.5, rSz: -0.62, rE: -2.55, headZ: -0.12 },
    phoneLook:{ rSx: -0.9, rSz: 0.15, rE: -1.25, lSz: 0.12, lE: -0.2, headX: 0.32, lean: 0.06 },
    cross:  { lSx: -0.55, rSx: -0.55, lE: -1.95, rE: -1.95, lSz: -0.32, rSz: 0.32, lean: -0.06, headX: -0.05 },
    cheer:  { lSz: 2.6, rSz: -2.6, lE: -0.2, rE: -0.2, headX: -0.2, lift: 0.03 },
    selfie: { lSx: -1.45, lSz: 0.38, lE: -0.25, rSz: -0.12, rE: -0.15, headY: 0.25, headZ: 0.06 },
    push:   { lSx: -1.9, rSx: -1.9, lE: -0.3, rE: -0.3, lean: 0.38, lSz: 0.15, rSz: -0.15 },
    knock:  { lSz: 0.12, lE: -0.15, rSx: -1.25, rSz: 0.05, rE: -1.25, lean: 0.05 },
    work:   { lSx: -1.7, rSx: -1.9, lE: -0.7, rE: -0.9, lSz: 0.2, rSz: -0.15, headX: -0.25 },
    chase:  { lSx: -1.3, rSx: -1.35, lE: -0.5, rE: -0.45, lean: 0.18 },
    sit:    { legL: -1.35, legR: -1.35, sink: -0.12, lSz: 0.1, rSz: -0.1, lE: -0.4, rE: -0.4 },
    drive:  { legL: -1.35, legR: -1.35, sink: -0.12, lSx: -1.0, rSx: -1.0, lE: -0.55, rE: -0.55 },
  });
  const F = (D.F = {
    neutral:    { by: 0, ba: 0.04, m: "smile", eye: 1 },
    happy:      { by: 0.01, ba: 0.06, m: "smile", eye: 1 },
    grin:       { by: 0.02, ba: 0.08, m: "grin", eye: 1 },
    shocked:    { by: 0.042, ba: 0.16, m: "O", eye: 1.32 },
    frustrated: { by: -0.018, ba: -0.36, m: "grimace", eye: 0.92 },
    knit:       { by: -0.012, ba: -0.3, m: "flat", eye: 0.95 },
    defeated:   { by: -0.006, ba: 0.42, m: "frown", eye: 0.7 },
    determined: { by: -0.01, ba: -0.24, m: "flat", eye: 1 },
    celebrate:  { by: 0.035, ba: 0.12, m: "grin", eye: 1.1 },
    talk:       { by: 0.015, ba: 0.05, m: "open", eye: 1 },
  });
  /* mix two poses: u = 0 → a, 1 → b */
  D.mix = (a, b, u) => { const o = {}; const ks = new Set([...Object.keys(a), ...Object.keys(b)]);
    ks.forEach((k) => (o[k] = K.lerp(a[k] || 0, b[k] || 0, u))); return o; };
  /* pose track: [[t, poseName|obj], ...] → pose at time t (each change eases over `blend` s, back-out for snap) */
  D.track = (t, keys, blend = 0.32) => {
    const get = (k) => (typeof k === "string" ? P[k] : k);
    let cur = get(keys[0][1]);
    for (let i = 1; i < keys.length; i++) {
      if (t < keys[i][0]) break;
      const u = (t - keys[i][0]) / (keys[i][2] || blend);
      cur = D.mix(cur, get(keys[i][1]), u >= 1 ? 1 : K.back(u, 1.2));
    }
    return cur;
  };
  D.face = (t, keys) => {                               // [[t, faceName], ...] → face (mouth switches at 40% of blend)
    let cur = F[keys[0][1]];
    for (let i = 1; i < keys.length; i++) {
      if (t < keys[i][0]) break;
      const n = F[keys[i][1]], u = K.eo((t - keys[i][0]) / 0.18);
      cur = { by: K.lerp(cur.by, n.by, u), ba: K.lerp(cur.ba, n.ba, u), eye: K.lerp(cur.eye, n.eye, u), m: u > 0.4 ? n.m : cur.m };
    }
    return cur;
  };

  D.apply = (dec, p, f, t, o) => {
    const J = dec.J, g = (k) => p[k] || 0;
    // idle life: 2–4° sway, breathing, belt jiggle, a blink every ~3.5 s
    const sway = o.still ? 0 : 0.045 * Math.sin(t * 1.25 + (o.seed || 0)) + 0.012 * Math.sin(t * 2.9);
    J.body.rotation.z = sway; J.body.position.y = g("lift") + g("sink") + (o.still ? 0 : 0.006 * Math.sin(t * 2.4));
    const sq = p.squash || 1; J.body.scale.set(1 / Math.sqrt(sq), sq, 1 / Math.sqrt(sq));
    J.spine.rotation.set(g("lean"), g("twist"), g("tilt")); J.spine.position.y = 0.1 + g("drop");
    J.neck.rotation.set(g("headX"), g("headY"), g("headZ"));
    J.shL.rotation.set(g("lSx"), 0, g("lSz")); J.shR.rotation.set(g("rSx"), 0, g("rSz"));
    J.elL.rotation.x = g("lE"); J.elR.rotation.x = g("rE");
    J.legL.rotation.x = g("legL"); J.legR.rotation.x = g("legR");
    J.thumbR.visible = g("thumb") > 0.5;
    J.belt.position.y = 0.09 + 0.004 * Math.sin(t * 9.5);
    // face
    const blink = o.noBlink ? 1 : ((t + (o.seed || 0) * 1.7) % 3.6) < 0.13 ? 0.12 : 1;
    [["L", 1], ["R", -1]].forEach(([s, sgn]) => {
      const b = J["brow" + s]; b.position.y = b.userData.y0 + f.by; b.rotation.z = -sgn * f.ba;
      const e = J["eye" + s]; e.scale.set(f.eye, f.eye * blink * (f.eye < 0.8 ? 0.75 : 1), 1);
    });
    J.mouthMat.map = mouthTex[f.m] || mouthTex.smile;
  };
})();
