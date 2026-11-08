/* kit3d: the look of the whole film in one place.
   Toon (2-tone cel) materials, a wobbly ink outline on every mesh (inverted hull pushed out in view space, so the line
   keeps the same width on screen), rounded/bevelled shapes, canvas-text textures and small easing helpers.
   Everything is deterministic: no Math.random, so any frame can be rendered on its own. */
(function () {
  const K = (window.K = {});
  THREE.ColorManagement.legacyMode = false;          // hex colours are sRGB; renderer outputs sRGB
  K.C = { pine: 0x0c2a22, pine2: 0x163d31, pine3: 0x1e4a3c, cloud: 0xeceeed, ink: 0x0e1412, graphite: 0x56605b,
          fog: 0xc6ccc8, gold: 0xf0b455, goldDeep: 0xc9821f, skin: 0xe9b68f, skinS: 0xc98e6c, tan: 0xb98a55,
          char: 0x2e3431, wood: 0x8c6c4e, woodL: 0xb89572, field: 0x5f7a4c, field2: 0x7d9460, hedge: 0x3f5c38 };

  // 2-tone ramp: shadow side ~55% of the colour, lit side full. Nearest filter = hard cel edge.
  const ramp = new THREE.DataTexture(new Uint8Array([140, 140, 140, 255, 255, 255, 255, 255]), 2, 1);
  ramp.minFilter = ramp.magFilter = THREE.NearestFilter; ramp.needsUpdate = true;
  const mats = {};
  K.toon = (color, o = {}) => {
    const key = color + JSON.stringify(o);
    if (!o.map && mats[key]) return mats[key];
    const m = new THREE.MeshToonMaterial(Object.assign({ color, gradientMap: ramp }, o));
    if (!o.map) mats[key] = m;
    return m;
  };
  K.flat = (color, o = {}) => new THREE.MeshBasicMaterial(Object.assign({ color }, o));
  K.glow = (color, o = {}) => new THREE.MeshBasicMaterial(Object.assign({ color, toneMapped: false }, o));

  // ---- ink outline -------------------------------------------------------------------------------------------
  K.inkUniforms = { uTime: { value: 0 }, uInk: { value: new THREE.Color(K.C.ink) } };
  const hullMat = (w) => new THREE.ShaderMaterial({
    uniforms: Object.assign({ uW: { value: w } }, K.inkUniforms), side: THREE.BackSide,
    vertexShader: `attribute vec3 snormal; uniform float uW; uniform float uTime;
      void main(){ vec4 mv = modelViewMatrix * vec4(position,1.0);
        vec3 n = normalize(normalMatrix * snormal);
        float wob = 1.0 + 0.28*sin(position.x*9.0 + position.y*7.0 + uTime*5.0) + 0.18*sin(position.z*11.0 - uTime*3.0);
        mv.xyz += n * uW * wob * max(0.6, -mv.z) * 0.0042;
        gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform vec3 uInk; void main(){ gl_FragColor = vec4(uInk,1.0); }` });
  const hulls = {};
  K.hull = (w) => hulls[w] || (hulls[w] = hullMat(w));

  // smoothed normals keyed by position, so the hull never splits open at hard edges
  K.smooth = (geo) => {
    if (geo.attributes.snormal) return geo;
    geo.computeVertexNormals();
    const p = geo.attributes.position, n = geo.attributes.normal, acc = new Map(), keys = [];
    for (let i = 0; i < p.count; i++) {
      const k = Math.round(p.getX(i) * 1e3) + "," + Math.round(p.getY(i) * 1e3) + "," + Math.round(p.getZ(i) * 1e3);
      keys.push(k); const a = acc.get(k) || [0, 0, 0]; a[0] += n.getX(i); a[1] += n.getY(i); a[2] += n.getZ(i); acc.set(k, a);
    }
    const s = new Float32Array(p.count * 3);
    keys.forEach((k, i) => { const a = acc.get(k), l = Math.hypot(a[0], a[1], a[2]) || 1; s[i * 3] = a[0] / l; s[i * 3 + 1] = a[1] / l; s[i * 3 + 2] = a[2] / l; });
    geo.setAttribute("snormal", new THREE.BufferAttribute(s, 3));
    return geo;
  };

  /* mesh(geo, mat, {ink, shadow}) → a mesh with its ink hull as a child. ink = line weight (0 = none). */
  K.mesh = (geo, mat, o = {}) => {
    const m = new THREE.Mesh(geo, mat);
    m.castShadow = o.cast !== false; m.receiveShadow = o.receive !== false;
    const ink = o.ink === undefined ? 1 : o.ink;
    if (ink > 0) { K.smooth(geo); const h = new THREE.Mesh(geo, K.hull(ink)); h.castShadow = false; h.receiveShadow = false; m.add(h); m.userData.hull = h; }
    return m;
  };

  // ---- shapes ------------------------------------------------------------------------------------------------
  const geos = {};
  /* rounded box: a segmented box whose vertices are pulled onto a rounded shell; normals are exact */
  K.rboxGeo = (w, h, d, r = 0.05, seg = 3) => {
    const key = [w, h, d, r, seg].join("_"); if (geos[key]) return geos[key];
    r = Math.min(r, w / 2 - 1e-4, h / 2 - 1e-4, d / 2 - 1e-4);
    const g = new THREE.BoxGeometry(w, h, d, seg * 2 + 1, seg * 2 + 1, seg * 2 + 1);
    const p = g.attributes.position, n = g.attributes.normal, ix = w / 2 - r, iy = h / 2 - r, iz = d / 2 - r;
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      const cx = Math.max(-ix, Math.min(ix, x)), cy = Math.max(-iy, Math.min(iy, y)), cz = Math.max(-iz, Math.min(iz, z));
      let dx = x - cx, dy = y - cy, dz = z - cz; const l = Math.hypot(dx, dy, dz) || 1; dx /= l; dy /= l; dz /= l;
      p.setXYZ(i, cx + dx * r, cy + dy * r, cz + dz * r); n.setXYZ(i, dx, dy, dz);
    }
    const s = new Float32Array(n.array); g.setAttribute("snormal", new THREE.BufferAttribute(s, 3));
    return (geos[key] = g);
  };
  K.rbox = (w, h, d, r, color, o = {}) => K.mesh(K.rboxGeo(w, h, d, r, o.seg || 3), o.mat || K.toon(color), o);
  K.sphere = (r, color, o = {}) => K.mesh(geos["s" + r] || (geos["s" + r] = new THREE.SphereGeometry(r, 28, 20)), o.mat || K.toon(color), o);
  K.capsule = (r, len, color, o = {}) => K.mesh(new THREE.CapsuleGeometry(r, len, 6, 16), o.mat || K.toon(color), o);
  K.cyl = (rt, rb, h, color, o = {}) => K.mesh(new THREE.CylinderGeometry(rt, rb, h, o.seg || 28, 1, !!o.open), o.mat || K.toon(color), o);
  /* extruded 2D shape with a soft bevel (tiles, blocks, bolt patch, padlock body) */
  K.extrude = (shape, depth, color, o = {}) => {
    const g = new THREE.ExtrudeGeometry(shape, { depth, bevelEnabled: true, bevelThickness: o.bevel || depth * 0.18,
      bevelSize: o.bevel || depth * 0.18, bevelSegments: 3, curveSegments: 10 });
    g.center(); return K.mesh(g, o.mat || K.toon(color), o);
  };
  K.roundRect = (w, h, r) => {
    const s = new THREE.Shape(), x = -w / 2, y = -h / 2;
    s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r);
    s.quadraticCurveTo(x + w, y + h, x + w - r, y + h); s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
    s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); return s;
  };
  K.bolt = (s = 1) => {
    const p = [[0.1, 0.5], [-0.22, -0.02], [0.0, -0.02], [-0.1, -0.5], [0.24, 0.06], [0.02, 0.06], [0.14, 0.5]];
    const sh = new THREE.Shape(); sh.moveTo(p[0][0] * s, p[0][1] * s); p.slice(1).forEach(([x, y]) => sh.lineTo(x * s, y * s)); return sh;
  };

  // ---- canvas text / decal textures -------------------------------------------------------------------------
  /* tex(w, h, draw(ctx)) → CanvasTexture. Drawn again once the web fonts have loaded (K.refreshText). */
  const texs = [];
  K.tex = (w, h, draw) => {
    const c = document.createElement("canvas"); c.width = w; c.height = h;
    const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; t.anisotropy = 4;
    const redraw = () => { const x = c.getContext("2d"); x.clearRect(0, 0, w, h); draw(x, w, h); t.needsUpdate = true; };
    redraw(); texs.push(redraw); return t;
  };
  K.refreshText = () => texs.forEach((f) => f());
  K.hex = (c) => "#" + new THREE.Color(c).getHexString();
  /* a flat textured card (decals, signs, screens) */
  K.plane = (w, h, tex, o = {}) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
      o.lit ? K.toon(0xffffff, { map: tex, transparent: true }) : new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false }));
    m.receiveShadow = !!o.lit; return m;
  };

  // ---- maths -------------------------------------------------------------------------------------------------
  K.clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  K.lerp = (a, b, u) => a + (b - a) * u;
  K.seg = (t, a, b) => K.clamp((t - a) / (b - a));                      // 0→1 between a and b
  K.eio = (u) => (u = K.clamp(u), u * u * (3 - 2 * u));                  // ease in-out
  K.eo = (u) => 1 - Math.pow(1 - K.clamp(u), 4);                         // ease out
  K.expo = (u) => (u = K.clamp(u), u >= 1 ? 1 : 1 - Math.pow(2, -10 * u));
  K.back = (u, c = 1.7) => { u = K.clamp(u); return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
  K.spring = (u, f = 3, d = 5) => (u <= 0 ? 0 : 1 - Math.exp(-d * u) * Math.cos(f * Math.PI * u));
  K.hash = (i) => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };   // seeded 0..1
  K.v3 = (x, y, z) => new THREE.Vector3(x, y, z);
  /* keyframed number: kf(t, [[t0,v0],[t1,v1],...], ease) */
  K.kf = (t, keys, ease = K.eio) => {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) if (t <= keys[i][0]) {
      const [a, va] = keys[i - 1], [b, vb] = keys[i]; return K.lerp(va, vb, ease((t - a) / (b - a)));
    }
    return keys[keys.length - 1][1];
  };
  K.kfv = (t, keys, ease = K.eio) => [0, 1, 2].map((j) => K.kf(t, keys.map((k) => [k[0], k[1][j]]), ease));
})();
