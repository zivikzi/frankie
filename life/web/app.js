// Frankie's world: the 3D view, the controls and the side panel.
// The simulation runs in Python (life/lab.py); this page polls its state and draws it.
// Rendering is conventional three.js (pinned 0.170.0, kept in ./vendor so it works offline).
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

// ------------------------------------------------------------------ reporting to the server's client.log
function report(level, msg, extra = {}) {
  try {
    fetch("/api/log", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ level, msg, ...extra, at: new Date().toISOString() }) });
  } catch (_) { /* nothing more we can do */ }
}
window.addEventListener("error", (e) => report("error", e.message, { src: e.filename, line: e.lineno, col: e.colno, stack: e.error && e.error.stack }));
window.addEventListener("unhandledrejection", (e) => report("error", "unhandled rejection: " + (e.reason && (e.reason.stack || e.reason.message) || e.reason)));

const $ = (id) => document.getElementById(id);
const REGION_COLOURS = { meadow: 0x9cc76a, forest: 0x3f7a3d, marsh: 0x6f8f86, rocky: 0x9b9286 };
const TRAITS = ["scene", "host", "coarse_hue", "size", "roundness", "lobes", "stem", "leaves", "spots", "thorns",
  "sticker_mark", "exact_hue", "sheen", "texture", "smell_1", "smell_2", "smell_3", "smell_4"];
const T = Object.fromEntries(TRAITS.map((n, i) => [n, i]));

// ------------------------------------------------------------------ scene
const canvas = $("three");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xa9c8de);
scene.fog = new THREE.Fog(0xa9c8de, 110, 260);
const camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI * 0.48;
controls.minDistance = 4;
controls.maxDistance = 220;
scene.add(new THREE.HemisphereLight(0xdfefff, 0x4a3f2c, 1.15));
const sun = new THREE.DirectionalLight(0xfff2dc, 1.6);
sun.position.set(80, 120, 40);
scene.add(sun);

let world = null;          // static world from /api/world
let heights = null;
let worldGroup = null;     // terrain, water, fences, walls
const objectMeshes = new Map();
let objectsVersion = -1;
const creatures = new Map(); // id -> {group, cone, trail, lookLine, target{x,z,y,h}, shown{...}}
let lastState = null;
let live = null;
let placeGroup = null;

function heightAt(x, z) {
  if (!world) return 0;
  const n = world.grid, c = world.size / (n - 1);
  const gx = Math.min(Math.max(x / c, 0), n - 1.000001), gz = Math.min(Math.max(z / c, 0), n - 1.000001);
  const i = Math.floor(gx), j = Math.floor(gz), fx = gx - i, fz = gz - j;
  const h = (a, b) => heights[b * n + a];
  return (h(i, j) * (1 - fx) + h(i + 1, j) * fx) * (1 - fz) + (h(i, j + 1) * (1 - fx) + h(i + 1, j + 1) * fx) * fz;
}

function buildWorld(w) {
  if (worldGroup) { scene.remove(worldGroup); disposeTree(worldGroup); }
  for (const m of objectMeshes.values()) { scene.remove(m); m.geometry.dispose(); }
  objectMeshes.clear();
  objectsVersion = -1;
  for (const c of creatures.values()) { scene.remove(c.group); scene.remove(c.trail); scene.remove(c.lookLine); }
  creatures.clear();
  world = w;
  heights = Float32Array.from(w.height);
  worldGroup = new THREE.Group();
  const n = w.grid, size = w.size;
  // terrain
  const g = new THREE.PlaneGeometry(size, size, n - 1, n - 1);
  g.rotateX(-Math.PI / 2);
  g.translate(size / 2, 0, size / 2);
  const pos = g.attributes.position;
  const col = new Float32Array(pos.count * 3);
  const tmp = new THREE.Color();
  for (let k = 0; k < pos.count; k++) {
    const h = heights[k];
    pos.setY(k, h);
    tmp.setHex(REGION_COLOURS[w.regions[w.region[k]]]);
    const shade = 0.82 + 0.3 * (h / 14) + 0.05 * Math.sin(k * 12.9898);
    col[3 * k] = tmp.r * shade; col[3 * k + 1] = tmp.g * shade; col[3 * k + 2] = tmp.b * shade;
  }
  g.setAttribute("color", new THREE.BufferAttribute(col, 3));
  g.computeVertexNormals();
  const terrain = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ vertexColors: true }));
  worldGroup.add(terrain);
  // obstacles
  for (const o of w.obstacles) {
    if (o.type === "fence") worldGroup.add(fenceMesh(o));
    if (o.type === "wall") worldGroup.add(wallMesh(o));
    if (o.type === "river") worldGroup.add(riverMesh(o));
  }
  scene.add(worldGroup);
  placeGroup = new THREE.Group();
  scene.add(placeGroup);
  // legend
  $("hud-legend").innerHTML = w.regions.map((r) => `<i style="background:#${REGION_COLOURS[r].toString(16).padStart(6, "0")}"></i>${r}`).join("")
    + (w.obstacles.length ? " · obstacles: " + w.obstacles.map((o) => o.type).join(", ") : " · no obstacles");
  // camera
  const [sx, sz] = w.spawn;
  controls.target.set(sx, heightAt(sx, sz), sz);
  camera.position.set(sx - 22, heightAt(sx, sz) + 22, sz + 26);
  controls.update();
}

function disposeTree(o) {
  o.traverse((m) => { if (m.geometry) m.geometry.dispose(); if (m.material) [].concat(m.material).forEach((x) => x.dispose()); });
}

function fenceMesh(f) {
  const grp = new THREE.Group();
  const post = new THREE.CylinderGeometry(0.07, 0.07, 1.3, 6);
  const postMat = new THREE.MeshLambertMaterial({ color: 0x7a5a36 });
  const netMat = new THREE.MeshBasicMaterial({ color: 0xd8d2c4, wireframe: true, transparent: true, opacity: 0.55 });
  const c = f.corners;
  for (let k = 0; k < c.length - 1; k++) {
    const [ax, az] = c[k], [bx, bz] = c[k + 1];
    const ha = heightAt(ax, az), hb = heightAt(bx, bz);
    const p = new THREE.Mesh(post, postMat); p.position.set(ax, ha + 0.65, az); grp.add(p);
    if (k === f.gap_index) continue;
    const len = Math.hypot(bx - ax, bz - az);
    const net = new THREE.Mesh(new THREE.PlaneGeometry(len, 1.2, 6, 3), netMat);
    net.position.set((ax + bx) / 2, (ha + hb) / 2 + 0.6, (az + bz) / 2);
    net.rotation.y = -Math.atan2(bz - az, bx - ax);
    grp.add(net);
  }
  return grp;
}

function wallMesh(w) {
  const [ax, az] = w.a, [bx, bz] = w.b;
  const len = Math.hypot(bx - ax, bz - az);
  const m = new THREE.Mesh(new THREE.BoxGeometry(len, 2.6, 0.5), new THREE.MeshLambertMaterial({ color: 0x8a8a90 }));
  const mx = (ax + bx) / 2, mz = (az + bz) / 2;
  m.position.set(mx, Math.min(heightAt(ax, az), heightAt(bx, bz), heightAt(mx, mz)) + 1.1, mz);
  m.rotation.y = -Math.atan2(bz - az, bx - ax);
  return m;
}

function riverMesh(r) {
  const grp = new THREE.Group();
  const pts = r.centre, hw = r.half_width;
  const verts = [], idx = [];
  for (let k = 0; k < pts.length; k++) {
    const [x, z] = pts[k];
    // the band runs across v: for a north-south river v is x, else z
    const L = r.vertical ? [x - hw, z] : [x, z - hw];
    const R = r.vertical ? [x + hw, z] : [x, z + hw];
    const y = Math.max(heightAt(...L), heightAt(...R), heightAt(x, z)) + 0.12;
    verts.push(L[0], y, L[1], R[0], y, R[1]);
    if (k > 0) { const a = 2 * (k - 1); idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(verts, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  grp.add(new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: 0x3b7fc4, transparent: true, opacity: 0.82, side: THREE.DoubleSide })));
  const [fx, fz] = r.ford;
  const fy = heightAt(fx, fz) + 0.22;
  if (r.crossing === "log") {
    const log = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 2 * hw + 3, 10), new THREE.MeshLambertMaterial({ color: 0x6b4a2b }));
    log.position.set(fx, fy + 0.3, fz);
    log.rotation.set(r.vertical ? 0 : Math.PI / 2, 0, r.vertical ? Math.PI / 2 : 0);
    grp.add(log);
  } else {
    const w = 2 * r.ford_half_width, l = 2 * hw + 1.5;
    const ford = new THREE.Mesh(new THREE.BoxGeometry(r.vertical ? l : w, 0.2, r.vertical ? w : l), new THREE.MeshLambertMaterial({ color: 0xc9b98f }));
    ford.position.set(fx, fy, fz);
    grp.add(ford);
  }
  return grp;
}

// ------------------------------------------------------------------ fruit: colour, size and shape come from its numbers
function mergeParts(parts) {
  let count = 0;
  const geos = parts.map(([geo, colour]) => {
    const g = geo.index ? geo.toNonIndexed() : geo;
    count += g.attributes.position.count;
    return [g, colour];
  });
  const pos = new Float32Array(count * 3), nor = new Float32Array(count * 3), col = new Float32Array(count * 3);
  let o = 0;
  for (const [g, c] of geos) {
    pos.set(g.attributes.position.array, o * 3);
    nor.set(g.attributes.normal.array, o * 3);
    for (let k = 0; k < g.attributes.position.count; k++) { col[(o + k) * 3] = c.r; col[(o + k) * 3 + 1] = c.g; col[(o + k) * 3 + 2] = c.b; }
    o += g.attributes.position.count;
    g.dispose();
  }
  const out = new THREE.BufferGeometry();
  out.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  out.setAttribute("normal", new THREE.BufferAttribute(nor, 3));
  out.setAttribute("color", new THREE.BufferAttribute(col, 3));
  return out;
}

const fruitMat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.55, metalness: 0.0 });
function fruitMesh(o) {
  const v = (n) => o.v[T[n]];
  const r = 0.16 + 0.26 * v("size");
  const squash = 0.6 + 0.45 * v("roundness");
  const lobes = 2 + Math.round(5 * v("lobes")), depth = 0.04 + 0.14 * v("lobes");
  const body = new THREE.SphereGeometry(r, 18, 12);
  const p = body.attributes.position;
  for (let k = 0; k < p.count; k++) {
    const x = p.getX(k), y = p.getY(k), z = p.getZ(k);
    const m = 1 + depth * Math.cos(lobes * Math.atan2(z, x));
    p.setXYZ(k, x * m, y * squash, z * m);
  }
  body.computeVertexNormals();
  const hue = v("exact_hue");
  const bodyCol = new THREE.Color().setHSL(hue, 0.72, 0.36 + 0.2 * v("sheen"));
  const parts = [[body, bodyCol]];
  const top = r * squash;
  const stemLen = 0.03 + 0.22 * v("stem");
  const stem = new THREE.CylinderGeometry(0.018, 0.024, stemLen, 5); stem.translate(0, top + stemLen / 2, 0);
  parts.push([stem, new THREE.Color(0x5c3d1e)]);
  const nLeaves = Math.round(3 * v("leaves"));
  for (let k = 0; k < nLeaves; k++) {
    const leaf = new THREE.SphereGeometry(0.07, 6, 4); leaf.scale(1.6, 0.25, 0.7);
    leaf.translate(0.09, 0, 0); leaf.rotateY(k * 2.1); leaf.translate(0, top + stemLen * 0.7, 0);
    parts.push([leaf, new THREE.Color().setHSL(0.3, 0.6, 0.32)]);
  }
  const nThorns = Math.round(8 * v("thorns"));
  for (let k = 0; k < nThorns; k++) {
    const th = new THREE.ConeGeometry(0.02, 0.09, 4); th.translate(0, r + 0.03, 0);
    th.rotateZ(Math.PI / 2 * (0.4 + 0.8 * ((k * 0.618) % 1))); th.rotateY(k * 2.4);
    parts.push([th, new THREE.Color(0x3b2a1a)]);
  }
  const nSpots = Math.round(6 * v("spots"));
  for (let k = 0; k < nSpots; k++) {
    const s = new THREE.SphereGeometry(0.035, 5, 4); s.scale(1, 0.5, 1); s.translate(0, r * 0.98, 0);
    s.rotateZ(0.6 + 1.2 * ((k * 0.381) % 1)); s.rotateY(k * 1.9);
    parts.push([s, new THREE.Color().setHSL(hue, 0.5, 0.18)]);
  }
  const mesh = new THREE.Mesh(mergeParts(parts), fruitMat);
  mesh.position.set(o.x, o.y + r * squash * 0.9, o.z);
  mesh.rotation.y = (o.id * 1.37) % (2 * Math.PI);
  mesh.userData.id = o.id;
  return mesh;
}

function syncObjects(list) {
  const keep = new Set(list.map((o) => o.id));
  for (const [id, m] of objectMeshes) if (!keep.has(id)) { scene.remove(m); m.geometry.dispose(); objectMeshes.delete(id); }
  for (const o of list) if (!objectMeshes.has(o.id)) { const m = fruitMesh(o); objectMeshes.set(o.id, m); scene.add(m); }
}

// ------------------------------------------------------------------ creatures
function creatureMesh(c) {
  const grp = new THREE.Group();
  const col = new THREE.Color(c.colour);
  const body = new THREE.Mesh(new THREE.SphereGeometry(0.42, 18, 12), new THREE.MeshStandardMaterial({ color: col, roughness: 0.6 }));
  body.scale.set(1.35, 0.85, 1.0); body.position.y = 0.45; grp.add(body);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.27, 16, 10), new THREE.MeshStandardMaterial({ color: col, roughness: 0.6 }));
  head.position.set(0.55, 0.8, 0); grp.add(head);
  const eyeM = new THREE.MeshBasicMaterial({ color: 0xffffff }), pupM = new THREE.MeshBasicMaterial({ color: 0x111111 });
  for (const s of [-1, 1]) {
    const e = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 6), eyeM); e.position.set(0.76, 0.88, 0.11 * s); grp.add(e);
    const pu = new THREE.Mesh(new THREE.SphereGeometry(0.04, 6, 4), pupM); pu.position.set(0.83, 0.88, 0.11 * s); grp.add(pu);
  }
  for (const [dx, dz] of [[0.3, 0.25], [0.3, -0.25], [-0.3, 0.25], [-0.3, -0.25]]) {
    const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.05, 0.3, 6), new THREE.MeshStandardMaterial({ color: col.clone().multiplyScalar(0.6) }));
    leg.position.set(dx, 0.12, dz); grp.add(leg);
  }
  const half = THREE.MathUtils.degToRad(world.view ? world.view.half_angle_deg : 60);
  const range = world.view ? world.view.range : 22;
  const coneG = new THREE.CircleGeometry(range, 32, -half, 2 * half); coneG.rotateX(-Math.PI / 2);
  const cone = new THREE.Mesh(coneG, new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.1, depthWrite: false, side: THREE.DoubleSide }));
  cone.position.y = 0.9; grp.add(cone);
  const trailG = new THREE.BufferGeometry();
  trailG.setAttribute("position", new THREE.BufferAttribute(new Float32Array(400 * 3), 3));
  const trail = new THREE.Line(trailG, new THREE.LineBasicMaterial({ color: col }));
  trail.frustumCulled = false;
  const lookG = new THREE.BufferGeometry();
  lookG.setAttribute("position", new THREE.BufferAttribute(new Float32Array(6), 3));
  const lookLine = new THREE.Line(lookG, new THREE.LineDashedMaterial({ color: 0xffffff, dashSize: 0.25, gapSize: 0.15 }));
  lookLine.visible = false; lookLine.frustumCulled = false;
  scene.add(grp); scene.add(trail); scene.add(lookLine);
  return { group: grp, cone, trail, lookLine, body, shown: null, target: null };
}

function updateCreatures(list) {
  for (const c of list) {
    let e = creatures.get(c.id);
    if (!e) { e = creatureMesh(c); creatures.set(c.id, e); }
    e.target = { x: c.x, z: c.z, y: c.y, h: c.heading };
    if (!e.shown) e.shown = { ...e.target };
    e.cone.visible = c.alive;
    e.group.rotation.z = c.alive ? 0 : Math.PI / 2 * 0.9;
    // trail
    const arr = e.trail.geometry.attributes.position.array;
    const tr = c.trail;
    for (let k = 0; k < tr.length; k++) { arr[3 * k] = tr[k][0]; arr[3 * k + 1] = heightAt(tr[k][0], tr[k][1]) + 0.12; arr[3 * k + 2] = tr[k][1]; }
    e.trail.geometry.setDrawRange(0, tr.length);
    e.trail.geometry.attributes.position.needsUpdate = true;
    // the sharp look
    const lt = c.look_target != null ? objectMeshes.get(c.look_target) : null;
    if (lt && c.action === "look") {
      const a = e.lookLine.geometry.attributes.position.array;
      a.set([c.x, c.y + 0.9, c.z, lt.position.x, lt.position.y, lt.position.z]);
      e.lookLine.geometry.attributes.position.needsUpdate = true;
      e.lookLine.computeLineDistances();
      e.lookLine.visible = true;
    } else e.lookLine.visible = false;
  }
}

function angleLerp(a, b, t) { const d = ((b - a + Math.PI * 3) % (Math.PI * 2)) - Math.PI; return a + d * t; }

// ------------------------------------------------------------------ place memory on the map
// A flag at the middle of each remembered square: green where he was fed more than poisoned, red where
// poisoned more, yellow where even. Taller flags mean more memories there.
const poleGeo = new THREE.CylinderGeometry(0.05, 0.05, 1, 6);
const flagGeo = new THREE.BoxGeometry(0.9, 0.55, 0.04);
const poleMat = new THREE.MeshLambertMaterial({ color: 0xeeeeee });
const flagMats = { good: new THREE.MeshLambertMaterial({ color: 0x3fcf55 }), bad: new THREE.MeshLambertMaterial({ color: 0xe4574c }), even: new THREE.MeshLambertMaterial({ color: 0xe0c83a }) };
let placesKey = "";
function drawPlaces(list) {
  if (!placeGroup) return;
  const on = $("places").checked;
  const key = on ? JSON.stringify(list.map((c) => (c.memory && c.memory.places || []).map((p) => [p.x, p.z, p.fed, p.poisoned]))) : "off";
  if (key === placesKey) return;
  placesKey = key;
  placeGroup.clear();
  if (!on) return;
  list.forEach((c, ci) => {
    for (const p of (c.memory && c.memory.places) || []) {
      if (!p.fed && !p.poisoned) continue;
      const net = p.fed - p.poisoned;
      const h = 1.6 + 0.35 * Math.min(p.fed + p.poisoned, 10);
      const x = p.x + ci * 0.8, z = p.z, y = heightAt(x, z);
      const pole = new THREE.Mesh(poleGeo, poleMat); pole.scale.y = h; pole.position.set(x, y + h / 2, z);
      const flag = new THREE.Mesh(flagGeo, net > 0 ? flagMats.good : net < 0 ? flagMats.bad : flagMats.even);
      flag.position.set(x + 0.45, y + h - 0.3, z);
      placeGroup.add(pole, flag);
    }
  });
}

// ------------------------------------------------------------------ the side panel
const CREATURE_NAMES = {};
function esc(s) { return String(s ?? "").replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch])); }

function panelHTML(c) {
  const em = world ? world.energy_max : 100;
  const st = c.stats;
  const mem = c.memory || {};
  const kinds = (mem.kinds || []).map((k) => `<tr><td>${esc(k.name)}</td><td class="${k.outcome === "fed me" ? "good" : k.outcome === "poisoned me" ? "bad" : "none"}">${esc(k.outcome)}</td><td>${k.eats}</td><td class="muted">${esc(k.note || "")}</td></tr>`).join("");
  const places = (mem.places || []).filter((p) => p.fed || p.poisoned).slice(0, 8)
    .map((p) => `<tr><td>${esc(p.name)}</td><td class="good">${p.fed}</td><td class="bad">${p.poisoned}</td></tr>`).join("");
  const eps = (c.episodes || []).map((e) => `<tr><td>${e.obstacle}${e.obstacle === "fence" ? " " + e.id : ""}</td><td>${e.start}</td><td>${e.reached ? e.ticks + " ticks, " + e.metres + " m" : "not yet"}</td></tr>`).join("");
  return `<div class="card" data-id="${c.id}">
    <h3><span class="sw" style="background:${c.colour}"></span>${esc(c.label)} ${c.alive ? "" : '<span class="dead">died at tick ' + c.age + "</span>"}</h3>
    <div class="energy"><div class="fill" style="width:${(100 * c.energy / em).toFixed(1)}%"></div>${c.reserve != null ? `<div class="res" style="left:${(100 * c.reserve / em).toFixed(1)}%" title="reserve"></div>` : ""}</div>
    <div class="energy-row"><span>energy <b>${c.energy.toFixed(1)}</b></span><span>reserve ${c.reserve} · boldness ${c.boldness}</span><span>age ${c.age}</span></div>
    <div class="thought">${esc(c.thought)}</div>
    <div class="stats">
      <div><b class="good">${st.food}</b><span>fed</span></div><div><b style="color:var(--bad)">${st.poison}</b><span>poisoned</span></div>
      <div><b>${st.nothing}</b><span>nothing</span></div><div><b>${st.looks}</b><span>sharp looks</span></div>
    </div>
    <h4>Energy and poison share</h4><canvas class="chart" width="700" height="220"></canvas>
    ${kinds ? `<h4>Kinds he has learned</h4><table><tr><th>kind</th><th>outcome</th><th>eats</th><th></th></tr>${kinds}</table>` : ""}
    ${places ? `<h4>Places he remembers</h4><table><tr><th>place</th><th>fed</th><th>poisoned</th></tr>${places}</table>` : ""}
    ${eps ? `<h4>Food behind obstacles</h4><table><tr><th>obstacle</th><th>saw it at</th><th>got there</th></tr>${eps}</table>` : ""}
    <div class="muted" style="margin-top:6px">bumps: fence ${st.bumps.fence}, wall ${st.bumps.wall}, river ${st.bumps.river}, edge ${st.bumps.edge} · walked ${st.walked} m</div>
  </div>`;
}

function drawChart(cv, c) {
  const ctx = cv.getContext("2d"), W = cv.width, H = cv.height;
  ctx.clearRect(0, 0, W, H);
  const em = world ? world.energy_max : 100;
  // poison share per 50-tick window, as bars
  const win = c.windows || [];
  const bw = W / Math.max(win.length, 20);
  win.forEach(([n, p], k) => {
    if (!n) return;
    ctx.fillStyle = `rgba(228,87,76,${0.25 + 0.5 * p / n})`;
    const h = (H - 20) * p / n;
    ctx.fillRect(k * bw + 1, H - h, Math.max(bw - 2, 1), h);
    ctx.fillStyle = "rgba(92,195,106,.35)";
    ctx.fillRect(k * bw + 1, H - 4, Math.max(bw - 2, 1), 4);
  });
  // reserve
  if (c.reserve != null) {
    ctx.strokeStyle = "rgba(255,255,255,.35)"; ctx.setLineDash([6, 6]); ctx.beginPath();
    const y = H - (H - 10) * c.reserve / em; ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); ctx.setLineDash([]);
  }
  // energy line
  const es = c.energy_series || [];
  if (es.length > 1) {
    ctx.strokeStyle = c.colour; ctx.lineWidth = 3; ctx.beginPath();
    const n = es.length;
    es.forEach((e, k) => { const x = (W * k) / Math.max(n - 1, 1), y = H - (H - 10) * e / em; k ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
    ctx.stroke(); ctx.lineWidth = 1;
  }
  ctx.fillStyle = "#95a3b1"; ctx.font = "20px system-ui";
  ctx.fillText("energy (line) · poison share per 50 ticks (red bars)", 8, 22);
}

function renderPanel(state) {
  const aside = $("panel");
  aside.innerHTML = state.creatures.map(panelHTML).join("") + `<div class="card muted">Running: ${state.live.creatures_running.map((n) => CREATURE_NAMES[n] || n).join(" vs ")} · life ${state.live.lives} in this session.<br>Logs are written to life/logs/ for debugging.</div>`;
  aside.querySelectorAll(".card[data-id]").forEach((card) => {
    const c = state.creatures.find((x) => String(x.id) === card.dataset.id);
    drawChart(card.querySelector("canvas.chart"), c);
  });
}

function renderTicker(state) {
  const lines = state.events.slice(-5).reverse().map((e) => {
    const who = CREATURE_NAMES[e.name] || e.name;
    if (e.died) return `tick ${e.tick}: ${who} died.`;
    const what = e.nature === "nourish" ? "was fed (+15)" : e.nature === "poison" ? "was poisoned (−20)" : "ate something that did nothing";
    return `tick ${e.tick}: ${who} ate a ${e.label} in the ${world.regions[e.region]} and ${what}${e.behind ? " — food behind a " + e.behind[0] + "!" : ""}`;
  });
  $("ticker").innerHTML = lines.map((l) => `<div>${esc(l)}</div>`).join("");
}

// ------------------------------------------------------------------ polling
let worldSeed = null;
let panelTimer = 0;
async function poll() {
  let wait = 100;
  try {
    const r = await fetch(`/api/state?objects=${objectsVersion}`);
    const s = await r.json();
    if (s.error) throw new Error(s.error);
    if (s.seed !== worldSeed) {
      const w = await (await fetch("/api/world")).json();
      buildWorld(w);
      worldSeed = w.seed;
      $("seed").placeholder = String(w.seed);
      report("info", "world loaded", { seed: w.seed, obstacles: w.obstacles.length });
      objectsVersion = -1;
      setTimeout(poll, 0);
      return;
    }
    if (s.objects) { syncObjects(s.objects); objectsVersion = s.objects_version; }
    lastState = s; live = s.live;
    updateCreatures(s.creatures);
    $("hud-seed").textContent = s.seed;
    $("hud-tick").textContent = s.tick;
    $("hud-status").textContent = live.error ? "stopped by an error" : live.playing ? (live.fast ? "fast forward" : `playing at ${live.speed}/s`) : "paused";
    $("play").textContent = live.playing ? "Pause" : "Play";
    $("fast").checked = live.fast;
    $("auto").checked = live.auto;
    if (document.activeElement !== $("c1") && document.activeElement !== $("c2")) {
      $("c1").value = live.creatures_running[0];
      $("c2").value = live.creatures_running[1] || "";
    }
    if (document.activeElement !== $("speed")) $("speed").value = String(live.speed);
    $("error").hidden = !live.error;
    $("error").textContent = live.error ? "The simulation stopped: " + live.error + " (details in life/logs/server.log)" : "";
    const now = performance.now();
    if (now - panelTimer > (live.fast ? 600 : 250)) { renderPanel(s); renderTicker(s); drawPlaces(s.creatures); panelTimer = now; }
    wait = live.fast ? 250 : live.playing ? Math.max(50, Math.min(150, 1000 / live.speed)) : 300;
  } catch (e) {
    $("hud-status").textContent = "can't reach the server — is life/lab.py still running?";
    wait = 1500;
  }
  setTimeout(poll, wait);
}

async function control(cmd) {
  const r = await fetch("/api/control", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cmd) });
  const out = await r.json();
  if (out.error) { $("error").hidden = false; $("error").textContent = out.error; report("warn", "control failed", { cmd, out }); }
  return out;
}

// ------------------------------------------------------------------ controls
$("play").onclick = () => control({ cmd: live && live.playing ? "pause" : "play" });
$("step").onclick = () => control({ cmd: "step" });
$("speed").onchange = (e) => control({ cmd: "speed", value: Number(e.target.value) });
$("fast").onchange = (e) => control({ cmd: "fast", value: e.target.checked });
$("auto").onchange = (e) => control({ cmd: "auto", value: e.target.checked });
$("new").onclick = () => {
  const cs = [$("c1").value, $("c2").value].filter(Boolean);
  control({ cmd: "new", seed: $("seed").value.trim(), creatures: cs });
  $("seed").value = "";
};
// Picking a creature restarts this same world (same seed) with the creatures picked.
for (const id of ["c1", "c2"]) $(id).onchange = () => {
  const cs = [$("c1").value, $("c2").value].filter(Boolean);
  control({ cmd: "new", seed: worldSeed, creatures: cs });
};
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;
  if (e.code === "Space") { e.preventDefault(); $("play").click(); }
  if (e.key === ".") $("step").click();
});
document.querySelectorAll(".tab").forEach((b) => b.onclick = () => {
  document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === b));
  $("world-view").hidden = b.dataset.view !== "world";
  $("results-view").hidden = b.dataset.view !== "results";
  if (b.dataset.view === "results") import("./results.js").then((m) => m.show($("results"))).catch((e) => report("error", "results view: " + e));
  else resize();
});

async function loadCreatures() {
  const cs = await (await fetch("/api/creatures")).json();
  for (const [name, v] of Object.entries(cs)) {
    CREATURE_NAMES[name] = v.label;
    $("c1").add(new Option(v.label, name));
    $("c2").add(new Option(v.label, name));
  }
  const st = await (await fetch("/api/state?objects=-2")).json();
  const running = st.live.creatures_running;
  $("c1").value = running[0];
  $("c2").value = running[1] || "";
  $("speed").value = String(st.live.speed);
}

// ------------------------------------------------------------------ the render loop
function resize() {
  const st = $("stage");
  const w = st.clientWidth, h = st.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);

let lastFrame = performance.now(), frames = 0, fpsT = performance.now();
function frame() {
  requestAnimationFrame(frame);
  const now = performance.now();
  const dt = Math.min((now - lastFrame) / 1000, 0.1);
  lastFrame = now;
  if (live && live.fast && $("nodraw").checked) return;
  const k = Math.min(1, dt * 10);
  let followed = null;
  for (const e of creatures.values()) {
    if (!e.target) continue;
    const s = e.shown;
    const jump = Math.hypot(e.target.x - s.x, e.target.z - s.z) > 6;
    s.x = jump ? e.target.x : s.x + (e.target.x - s.x) * k;
    s.z = jump ? e.target.z : s.z + (e.target.z - s.z) * k;
    s.h = jump ? e.target.h : angleLerp(s.h, e.target.h, k);
    s.y = heightAt(s.x, s.z);
    e.group.position.set(s.x, s.y, s.z);
    e.group.rotation.y = -s.h;
    if (!followed) followed = s;
  }
  if ($("follow").checked && followed) {
    const tgt = new THREE.Vector3(followed.x, followed.y, followed.z);
    const delta = tgt.clone().sub(controls.target).multiplyScalar(Math.min(1, dt * 3));
    controls.target.add(delta);
    camera.position.add(delta);
  }
  controls.update();
  renderer.render(scene, camera);
  frames++;
  if (now - fpsT > 60000) { report("info", "fps", { fps: Math.round(frames * 1000 / (now - fpsT)), objects: objectMeshes.size }); frames = 0; fpsT = now; }
}

resize();
loadCreatures().then(() => { poll(); frame(); }).catch((e) => { report("error", "start-up failed: " + e.stack); $("hud-status").textContent = "start-up failed: " + e; });
report("info", "page opened", { ua: navigator.userAgent, gl: renderer.getContext().getParameter(renderer.getContext().VERSION) });
