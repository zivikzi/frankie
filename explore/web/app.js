// Frankie Lab: the page. Plain JavaScript and SVG; no libraries.
"use strict";

const $ = (id) => document.getElementById(id);
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") n.className = v; else if (k === "html") n.innerHTML = v; else n.setAttribute(k, v);
  }
  for (const k of kids) n.append(k);
  return n;
};
const NS = "http://www.w3.org/2000/svg";
const svg = (tag, attrs = {}) => {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  return n;
};
const svgText = (parent, attrs, text) => { const t = svg("text", attrs); t.textContent = text; parent.append(t); return t; };
const fmt = (x, d = 2) => (x === null || x === undefined || Number.isNaN(x)) ? "—" : Number(x).toFixed(d);
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));

const NICE = {
  scene: "scene", host: "what it sits on", coarse_hue: "colour (coarse)", size: "size", roundness: "roundness",
  lobes: "lobes", stem: "stem", leaves: "leaves", spots: "spots", thorns: "thorns", sticker_mark: "sticker",
  exact_hue: "colour (exact)", sheen: "sheen", texture: "texture", smell_1: "smell 1", smell_2: "smell 2",
  smell_3: "smell 3", smell_4: "smell 4", sweet: "sweet", sour: "sour", bitter: "bitter", salty: "salty",
};
const LAYER_NAMES = ["context", "object", "parts", "details"];

let META = null, TRACE = null, VIEW = [], POS = 0, TIMER = null;

// ------------------------------------------------------------------ tabs

document.querySelectorAll(".tab").forEach((b) => b.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("on", x === b));
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("on", v.id === b.dataset.tab));
  if (b.dataset.tab === "score") loadBoard();
  if (b.dataset.tab === "variants") loadVariants();
}));

async function api(path, opts) {
  const r = await fetch(path, opts);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error || r.statusText);
  return j;
}

// ------------------------------------------------------------------ start

async function start() {
  META = await api("/api/meta");
  for (const m of META.minds) { $("mind").append(el("option", { value: m }, m)); $("bmind").append(el("option", { value: m }, m)); }
  $("mind").value = META.minds.includes("E1") ? "E1" : META.minds[0];
  for (const f of META.families) $("family").append(el("option", { value: f.n }, `${f.n} (${f.half})`));
  for (const r of META.runs) $("run").append(el("option", { value: r }, r));
  $("load").addEventListener("click", load);
  $("first").addEventListener("click", () => go(0));
  $("prev").addEventListener("click", () => go(POS - 1));
  $("next").addEventListener("click", () => go(POS + 1));
  $("last").addEventListener("click", () => go(VIEW.length - 1));
  $("play").addEventListener("click", togglePlay);
  $("slider").addEventListener("input", (e) => go(+e.target.value));
  $("showchecks").addEventListener("change", () => { const n = VIEW[POS]; filter(); go(Math.max(0, VIEW.indexOf(n))); });
  $("reveal").addEventListener("change", () => draw());
  $("half").addEventListener("change", loadBoard);
  $("brun").addEventListener("click", startBatch);
  document.addEventListener("keydown", (e) => {
    if (e.target.tagName === "SELECT" || e.target.tagName === "INPUT" && e.target.type !== "range" && e.target.type !== "checkbox") return;
    if (e.key === "ArrowRight") { go(POS + 1); e.preventDefault(); }
    if (e.key === "ArrowLeft") { go(POS - 1); e.preventDefault(); }
    if (e.key === " ") { togglePlay(); e.preventDefault(); }
  });
  load();
}

async function load() {
  stopPlay();
  $("status").textContent = "working it out…";
  $("status").className = "muted";
  try {
    TRACE = await api(`/api/trace?mind=${encodeURIComponent($("mind").value)}&family=${$("family").value}&run=${$("run").value}`);
    $("status").textContent = `${TRACE.mind}, family ${TRACE.family} (${TRACE.half} half), run ${TRACE.run}: ` +
      `reserve R = ${fmt(TRACE.reserve / 1000, 1)}, boldness b = ${fmt(TRACE.boldness)}`;
    filter();
    const firstTeach = VIEW.findIndex((i) => TRACE.steps[i].phase === "teaching");
    go(Math.max(0, firstTeach));
  } catch (e) {
    $("status").textContent = "Could not load: " + e.message;
    $("status").className = "err";
  }
}

function filter() {
  VIEW = TRACE.steps.map((s, i) => i).filter((i) => $("showchecks").checked || !TRACE.steps[i].phase.startsWith("check"));
  $("slider").max = Math.max(0, VIEW.length - 1);
}

function go(p) {
  if (!TRACE || !VIEW.length) return;
  POS = clamp(p, 0, VIEW.length - 1);
  $("slider").value = POS;
  draw();
}

function togglePlay() { if (TIMER) stopPlay(); else { TIMER = setInterval(() => { if (POS >= VIEW.length - 1) stopPlay(); else go(POS + 1); }, 900); $("play").textContent = "⏸ Pause"; } }
function stopPlay() { if (TIMER) clearInterval(TIMER); TIMER = null; $("play").textContent = "▶ Play"; }

// ------------------------------------------------------------------ one step

function draw() {
  const s = TRACE.steps[VIEW[POS]];
  const reveal = $("reveal").checked;
  $("stepinfo").textContent = `decision ${s.n} of ${TRACE.steps.length} · ${s.item}`;
  $("phase").textContent = s.phase;
  drawObject(s);
  $("role").textContent = reveal ? `It really is: ${s.role}` : "Tick “reveal what it really is” to see. Try guessing first!";
  $("role").classList.toggle("hidden", !reveal);
  drawSenses(s);
  drawNumbers(s);
  drawThinking(s, reveal);
  drawChoice(s, reveal);
  drawEnergy(s);
  drawMemory(s, reveal);
}

function val(s, name) {
  const i = TRACE.traits.indexOf(name);
  if (i < 18) return s.visible[i];
  return s.taste ? s.taste[i - 18] : null;
}

// The object as a picture. Every feature is one of its numbers (0 to 1).
function drawObject(s) {
  const g = $("pic");
  g.replaceChildren();
  const v = (n) => val(s, n);
  const sceneHue = v("scene") * 360, hostHue = v("host") * 360;
  g.append(svg("rect", { x: 0, y: 0, width: 320, height: 260, fill: `hsl(${sceneHue},45%,86%)` }));
  g.append(svg("rect", { x: 0, y: 170, width: 320, height: 90, fill: `hsl(${sceneHue},30%,72%)` }));
  // what it sits on
  const h = v("host");
  if (h < 0.34) g.append(svg("ellipse", { cx: 160, cy: 214, rx: 120, ry: 18, fill: `hsl(${hostHue},25%,92%)`, stroke: `hsl(${hostHue},20%,55%)` }));
  else if (h < 0.67) g.append(svg("rect", { x: 20, y: 206, width: 280, height: 14, rx: 7, fill: `hsl(${hostHue},40%,35%)` }));
  else for (let k = 0; k < 24; k++) g.append(svg("line", { x1: 20 + k * 12, y1: 222, x2: 24 + k * 12, y2: 200 + (k % 3) * 4, stroke: `hsl(${hostHue},45%,38%)`, "stroke-width": 3 }));
  // body: colour from the exact hue, size, roundness, lobes
  const hue = (v("exact_hue") ?? v("coarse_hue")) * 360;
  const r = 34 + 50 * v("size");
  const ry = r * (0.55 + 0.45 * v("roundness"));
  const cx = 160, cy = 208 - ry;
  const lobes = 2 + Math.round(5 * v("lobes"));
  const depth = 0.04 + 0.12 * v("lobes");
  let d = "";
  for (let k = 0; k <= 96; k++) {
    const t = (k / 96) * Math.PI * 2;
    const m = 1 + depth * Math.cos(lobes * t);
    const x = cx + r * m * Math.sin(t), y = cy - ry * m * Math.cos(t);
    d += (k ? "L" : "M") + x.toFixed(1) + "," + y.toFixed(1);
  }
  const defs = svg("defs");
  const grad = svg("radialGradient", { id: "shine", cx: "35%", cy: "30%", r: "70%" });
  grad.append(svg("stop", { offset: "0%", "stop-color": `hsl(${hue},70%,${62 + 20 * v("sheen")}%)` }));
  grad.append(svg("stop", { offset: "100%", "stop-color": `hsl(${hue},65%,${38 - 8 * v("texture")}%)` }));
  defs.append(grad);
  const pat = svg("pattern", { id: "tex", width: 7, height: 7, patternUnits: "userSpaceOnUse" });
  pat.append(svg("circle", { cx: 2, cy: 2, r: 1.1, fill: "#000", opacity: (0.35 * v("texture")).toFixed(2) }));
  defs.append(pat);
  g.append(defs);
  // stem and leaves
  const stem = 4 + 36 * v("stem");
  g.append(svg("path", { d: `M${cx},${cy - ry + 4} q 6,${-stem / 2} 2,${-stem}`, stroke: "#5c3d1e", "stroke-width": 5, fill: "none", "stroke-linecap": "round" }));
  const nLeaves = Math.round(3 * v("leaves"));
  for (let k = 0; k < nLeaves; k++) {
    const side = k % 2 ? -1 : 1;
    g.append(svg("ellipse", { cx: cx + side * (14 + 6 * k), cy: cy - ry - stem * 0.6 + 6 * k, rx: 16, ry: 7, fill: "hsl(120,45%,38%)", transform: `rotate(${side * -25} ${cx + side * (14 + 6 * k)} ${cy - ry - stem * 0.6 + 6 * k})` }));
  }
  g.append(svg("path", { d, fill: "url(#shine)", stroke: `hsl(${hue},55%,25%)`, "stroke-width": 1.5 }));
  g.append(svg("path", { d, fill: "url(#tex)" }));
  // spots, thorns, sticker, sheen
  const nSpots = Math.round(12 * v("spots"));
  for (let k = 0; k < nSpots; k++) {
    const a = k * 2.399, rr = 0.25 + 0.55 * ((k * 37) % 11) / 11;
    g.append(svg("circle", { cx: cx + r * rr * Math.cos(a), cy: cy + ry * rr * Math.sin(a), r: 2.5 + (k % 3), fill: `hsl(${hue},50%,22%)`, opacity: 0.7 }));
  }
  const nThorns = Math.round(10 * v("thorns"));
  for (let k = 0; k < nThorns; k++) {
    const t = (k / Math.max(1, nThorns)) * Math.PI * 2 + 0.3;
    const x = cx + r * Math.sin(t), y = cy - ry * Math.cos(t);
    const ox = 10 * Math.sin(t), oy = -10 * Math.cos(t);
    g.append(svg("path", { d: `M${x - oy * 0.3},${y + ox * 0.3} L${x + ox},${y + oy} L${x + oy * 0.3},${y - ox * 0.3}Z`, fill: "#4a3b2a" }));
  }
  if (v("sticker_mark") > 0.15) {
    g.append(svg("ellipse", { cx: cx + r * 0.35, cy: cy + ry * 0.15, rx: 13, ry: 9, fill: "#fff", stroke: "#888", opacity: clamp(v("sticker_mark") * 1.2) }));
    svgText(g, { x: cx + r * 0.35, y: cy + ry * 0.15 + 4, "text-anchor": "middle", "font-size": 9, fill: "#c00", opacity: clamp(v("sticker_mark") * 1.2) }, "★");
  }
  g.append(svg("ellipse", { cx: cx - r * 0.35, cy: cy - ry * 0.4, rx: r * 0.22, ry: ry * 0.12, fill: "#fff", opacity: (0.6 * v("sheen")).toFixed(2), transform: `rotate(-25 ${cx - r * 0.35} ${cy - ry * 0.4})` }));
}

function barRow(label, x, extra = "") {
  return el("div", { class: "bar" }, el("span", {}, label),
    el("div", { class: "track", html: x === null ? "" : `<div class="fill" style="width:${(100 * clamp(x)).toFixed(1)}%"></div>${extra}` }),
    el("span", { class: "num" }, x === null ? "?" : fmt(x)));
}

function drawSenses(s) {
  const box = $("senses");
  box.replaceChildren();
  const smell = el("div", { class: "layer" }, el("h3", {}, "smell (seen before eating)"));
  for (let k = 1; k <= 4; k++) smell.append(barRow(`smell ${k}`, val(s, `smell_${k}`)));
  const taste = el("div", { class: "layer" }, el("h3", {}, s.taste ? "taste (known only after eating)" : "taste: not eaten, so unknown"));
  if (s.taste) for (const n of ["sweet", "sour", "bitter", "salty"]) taste.append(barRow(n, val(s, n)));
  box.append(smell, taste);
}

function drawNumbers(s) {
  const box = $("numbers");
  box.replaceChildren();
  TRACE.layers.slice(0, 4).forEach(([name, a, b], li) => {
    const L = el("div", { class: "layer" }, el("h3", {}, `${li + 1}. ${name}`));
    for (let t = a; t < b; t++) L.append(barRow(NICE[TRACE.traits[t]] || TRACE.traits[t], s.visible[t]));
    box.append(L);
  });
}

function kindName(slot, mem) {
  const k = (mem || []).find((x) => x.slot === slot);
  return `kind #${slot}` + (k && k.lid ? ` (${k.lid})` : "");
}

function memAt(i) { return i === null || i === undefined ? [] : TRACE.memories[i] || []; }

function drawThinking(s, reveal) {
  const box = $("thinking");
  box.replaceChildren();
  const before = memAt(s.memory_before);
  const lg = s.log || {};
  if (TRACE.mind_class !== "tower") {
    box.append(el("p", {}, "This mind keeps no kinds. Trial and error: it compares the object with every item it has eaten and copies what happened to the nearest one."));
    if (lg && Object.keys(lg).length) box.append(el("pre", { class: "muted" }, JSON.stringify(lg).slice(0, 400)));
    return;
  }
  if (!before.length) { box.append(el("p", {}, "Memory is empty, so there is nothing to compare with: the verdict is “I don't know this”.")); return; }
  const cols = lg.layers ? lg.layers.map((l) => l.layer) : LAYER_NAMES;
  const rows = new Map(before.map((k) => [k.slot, { k, cells: {}, out: null, total: null }]));
  if (lg.layers) {                                          // E1: elimination layer by layer
    for (const L of lg.layers) {
      for (const [slot, total, missed] of L.out) { const r = rows.get(slot); if (r) { r.cells[L.layer] = { out: true, total, missed }; r.out = L.layer; } }
      for (const [slot, total] of L.kept) { const r = rows.get(slot); if (r) r.cells[L.layer] = { out: false, total }; }
    }
  } else {                                                  // K-F: dropped at the layer handovers, or objected to
    const stepLayer = { 1: "context", 2: "object", 3: "parts" };
    for (const [step, slot] of lg.eliminated || []) { const r = rows.get(slot); if (r && !r.out) { r.out = stepLayer[step] || `step ${step}`; r.cells[r.out] = { out: true, why: `trailing the leader at step ${step}` }; } }
    for (const [step, slot, layers, what] of lg.objections || []) { const r = rows.get(slot); if (r) { const lay = layers[layers.length - 1]; r.cells[lay] = { out: what === "removed", why: `${layers.join("+")} objected at step ${step} (${what})` }; if (what === "removed") r.out = lay; } }
    for (const r of rows.values()) for (const c of cols) if (!r.cells[c] && !r.out) r.cells[c] = { out: false };
    const win = lg.within_margin || [];
    box.append(el("p", { class: "muted" }, `K-F's spiking race: at its last step the leader was ${lg.last_leader === "unknown" ? "“unknown”" : kindName(lg.last_leader, before)}` +
      (win.length ? `, with ${win.length} other group(s) within the winning margin (a near-tie).` : ".") + (lg.unsettled_why ? ` Unsettled because ${lg.unsettled_why}.` : "")));
  }
  const order = [...rows.values()].sort((a, b) => (a.out ? cols.indexOf(a.out) : 99) < (b.out ? cols.indexOf(b.out) : 99) ? 1 : -1);
  const showAll = box.dataset.all === "1";
  const shown = showAll ? order : order.slice(0, 18);
  const tbl = el("table");
  const head = el("tr", {}, el("th", {}, "kind (outcome so far)"));
  for (const c of cols) head.append(el("th", {}, c));
  tbl.append(head);
  for (const r of shown) {
    const named = r.k.slot === s.verdict;
    const rec = (r.k.record || []);
    const outc = rec.length ? (rec[0] > 0 ? "nourish" : rec[0] < 0 ? "poison" : "nothing") : `${r.k.eats} eats`;
    const label = el("td", { class: "kind" }, el("span", { class: (r.out ? "out" : named ? "winner" : "kept") }, kindName(r.k.slot, before)), ` · ${outc}` + (reveal && r.k.in_h ? " · an apple kind" : ""));
    const tr = el("tr", {}, label);
    let dead = false;
    for (const c of cols) {
      const cell = r.cells[c];
      if (dead || !cell) { tr.append(el("td", { class: "muted" }, dead ? "" : "")); continue; }
      if (cell.out) {
        dead = true;
        const why = cell.missed ? `ruled out: misses on ${cell.missed.map((t) => NICE[TRACE.traits[t]]).join(", ")}` : cell.why;
        tr.append(el("td", { class: "out", title: why }, "✗ " + (why || "ruled out")));
      } else tr.append(el("td", { class: "kept" }, cell.total !== undefined ? `✓ ${fmt(cell.total, 1)} weighted misses` : (cell.why ? "↺ " + cell.why : "✓")));
    }
    tbl.append(tr);
  }
  box.append(el("div", { class: "scroll" }, tbl));
  if (order.length > 18) {
    const b = el("button", {}, showAll ? "show fewer" : `show all ${order.length} kinds`);
    b.addEventListener("click", () => { box.dataset.all = showAll ? "0" : "1"; drawThinking(s, reveal); });
    box.append(b);
  }
}

function verdictText(s, mem) {
  if (TRACE.mind_class !== "tower") return "no kinds: trial and error";
  if (s.verdict === "unknown") return "“I don't know this”";
  if (s.verdict === "unsettled") return "couldn't decide (unsettled)";
  return `it's ${kindName(s.verdict, mem)}`;
}

function drawChoice(s, reveal) {
  const box = $("choice");
  box.replaceChildren();
  const mem = memAt(s.memory_before);
  box.append(el("div", { class: "verdict" }, verdictText(s, mem)));
  const act = el("div", { class: "verdict " + (s.action === "eat" ? "eat" : "skip") }, s.action === "eat" ? "→ EAT" : "→ skip");
  box.append(act);
  if (s.phase.startsWith("check")) box.append(el("p", { class: "muted" }, "A check: a throwaway copy of the mind is asked, so nothing is really eaten and nothing is learned."));
  else if (s.forced && s.action === "skip") box.append(el("p", { class: "muted" }, "It chose to skip, but this taste is forced (every mind gets the same lessons), so it ate anyway."));
  if (s.outcome !== null && s.outcome !== undefined) {
    const o = s.outcome > 0 ? "nourishing (+15)" : s.outcome < 0 ? "poison (−20)" : "nothing (0)";
    box.append(el("p", {}, `Outcome: ${o}`));
  }
  if (s.landing !== null && s.landing !== undefined && TRACE.mind_class === "tower")
    box.append(el("p", { class: "muted" }, `After tasting, it thought: ${s.landing === "unknown" ? "“I don't know this”" : s.landing === "unsettled" ? "unsettled" : kindName(s.landing, mem)}`));
  if (reveal && s.names_h !== null && s.names_h !== undefined)
    box.append(el("p", {}, s.names_h ? "✓ It named one of its apple kinds." : "It did not name an apple kind."));
  if (s.events && s.events.length) {
    const p = el("p", {}, "Memory: ");
    for (const e of s.events) {
      const merged = (s.merges || []).find((m) => m[0] === e.slot);
      const t = e.type === "forget" && merged ? "merge" : e.type;
      p.append(el("span", { class: `tag ${t}` }, t === "merge" ? `#${e.slot} merged into #${merged[1]}` : `${t} #${e.slot}`));
    }
    box.append(p);
  }
}

function drawEnergy(s) {
  const g = $("energy");
  g.replaceChildren();
  const max = 90000, X = (m) => 10 + 300 * clamp(m / max);
  g.append(svg("rect", { x: 10, y: 20, width: 300, height: 18, rx: 4, fill: "none", stroke: "currentColor", opacity: 0.3 }));
  const now = s.energy_after ?? s.energy_choice ?? s.energy_set;
  g.append(svg("rect", { x: 10, y: 20, width: X(now) - 10, height: 18, rx: 4, fill: s.outcome < 0 ? "#e8590c" : "#2f9e44", opacity: 0.8 }));
  g.append(svg("line", { x1: X(TRACE.reserve), x2: X(TRACE.reserve), y1: 12, y2: 46, stroke: "#c2255c", "stroke-width": 2 }));
  svgText(g, { x: X(TRACE.reserve), y: 10, "text-anchor": "middle", "font-size": 10, fill: "#c2255c" }, "reserve R");
  svgText(g, { x: 10, y: 62, "font-size": 11, fill: "currentColor" },
    `energy: set to ${fmt(s.energy_set / 1000, 1)} → ${fmt(s.energy_choice / 1000, 2)} after looking and thinking` + (s.energy_after != null ? ` → ${fmt(s.energy_after / 1000, 1)} after eating` : ""));
}

function rangeChart(k) {
  const W = 154, H = 44, n = 22, cw = W / n;
  const g = svg("svg", { viewBox: `0 0 ${W} ${H + 2}`, width: "100%" });
  for (let t = 0; t < n; t++) {
    if (t === 2 || t === 6 || t === 11 || t === 18) g.append(svg("line", { x1: t * cw, x2: t * cw, y1: 0, y2: H, stroke: "currentColor", opacity: 0.25 }));
    const r = k.ranges[t];
    if (!r) continue;
    const lo = clamp(r[0]), hi = clamp(r[1]);
    const w = k.weights[t] === null ? 0.3 : 0.15 + 0.85 * (k.weights[t] / 10);
    g.append(svg("rect", { x: t * cw + 1, y: H * (1 - hi), width: cw - 2, height: Math.max(1.5, H * (hi - lo)), fill: t >= 18 ? "#c2255c" : "#3b5bdb", opacity: w.toFixed(2) }));
  }
  return g;
}

function drawMemory(s, reveal) {
  const box = $("memory");
  box.replaceChildren();
  const mem = memAt(s.memory);
  $("memnote").textContent = mem.length ? `${mem.length} kinds · each chart shows a kind's ranges on the 22 traits (context | object | parts | details | taste), darker = more relevant` : "";
  if (TRACE.mind_class !== "tower") { box.append(el("p", { class: "muted" }, "Bots keep a plain list of eaten items, not kinds.")); return; }
  if (!mem.length) { box.append(el("p", { class: "muted" }, "Empty.")); return; }
  const touched = new Map();
  for (const e of s.events || []) if (e.type !== "forget") touched.set(e.slot, e.type);
  for (const [gone, keep] of s.merges || []) touched.set(keep, "merge");
  const grid = el("div", { class: "mem" });
  const sorted = [...mem].sort((a, b) => (touched.has(b.slot) - touched.has(a.slot)) || a.slot - b.slot);
  for (const k of sorted) {
    const rec = k.record || [];
    const n = (c) => rec.filter((x) => x === c).length;
    const ev = touched.get(k.slot);
    const card = el("div", { class: "kcard" + (ev ? ` ev-${ev}` : "") + (k.slot === s.verdict ? " named" : "") });
    const head = el("div", {}, el("b", {}, `#${k.slot}`), ` ${k.lid || ""} `);
    if (ev) head.append(el("span", { class: `tag ${ev}` }, ev));
    if (reveal && k.in_h) head.append(el("span", { class: "tag h" }, "apple kind"));
    card.append(head, el("div", { class: "muted" }, rec.length ? `nourish ${n(1)} · poison ${n(-1)} · nothing ${n(0)}` : `${k.eats} eats`), rangeChart(k));
    grid.append(card);
  }
  for (const [gone, keep] of s.merges || []) grid.append(el("div", { class: "kcard" }, el("span", { class: "tag merge" }, "merged"), ` #${gone} was absorbed into #${keep}`));
  box.append(grid);
}

// ------------------------------------------------------------------ scoreboard

const MARKS = [
  ["settle_rate", "decisions that settle", (v) => v >= 0.95, "≥ 0.95"],
  ["copy_accept", "copies of h1 eaten", (v) => v >= 0.80, "≥ 0.80"],
  ["d_learn", "D_learn", null, "≥ floor + 0.15, and ≥ 0.25"],
  ["fmn", "apples vs strangers", (v) => v >= 0.15, "≥ 0.15"],
  ["lr_h1", "look-alikes refused (h1 half)", (v) => v >= 0.60, "≥ 0.60"],
  ["lr_far", "look-alikes refused (far half)", (v) => v >= 0.60, "≥ 0.60"],
  ["dq_sour", "Q after the sour apple", (v) => v >= 0.25, "≥ 0.25"],
  ["sour_drop", "sour drop", (v) => v <= 0.15, "≤ 0.15"],
];
const COLOURS = ["#3b5bdb", "#e8590c", "#2f9e44", "#c2255c", "#7048e8", "#0c8599", "#e67700", "#495057", "#a61e4d", "#5c940d"];

async function loadBoard() {
  const b = await api("/api/scoreboard");
  const half = b.halves && b.halves[$("half").value];
  const box = $("board");
  box.replaceChildren();
  if (!half) { box.append(el("p", {}, "No results for these families yet. Use “Run a batch” below.")); $("curve").replaceChildren(); return; }
  const floor = half.floor;
  const dTarget = Math.max(floor + 0.15, 0.25);
  const names = Object.keys(half).filter((k) => k !== "floor");
  const order = ["B2e", "B1n-bot-r", "B1n-mind", "K-F"];
  names.sort((a, b) => (order.indexOf(a) === -1 ? 9 : order.indexOf(a)) - (order.indexOf(b) === -1 ? 9 : order.indexOf(b)) || a.localeCompare(b));
  const tbl = el("table");
  const head = el("tr", {}, el("th", {}, "mind"));
  for (const [, label, , mark] of MARKS) head.append(el("th", { title: mark }, el("div", {}, label), el("div", { class: "muted" }, mark)));
  tbl.append(head);
  for (const n of names) {
    const m = half[n];
    const tr = el("tr", {}, el("td", {}, el("b", {}, n), el("div", { class: "muted" }, `${m.runs} runs`)));
    for (const [key, , test] of MARKS) {
      const v = m[key];
      if (v === undefined) { tr.append(el("td", { class: "muted" }, "—")); continue; }
      const ok = key === "d_learn" ? v >= dTarget : test(v);
      tr.append(el("td", { class: ok ? "ok" : "no" }, fmt(v)));
    }
    tbl.append(tr);
  }
  box.append(el("div", { class: "card scroll" }, el("p", {}, `Trial and error's floor here: ${fmt(floor, 3)} (the better of B1n-bot-r and B1n-mind). To pass, D_learn needs ${fmt(dTarget, 3)}. B2e reads the hidden answer, so it shows the best possible score.`), tbl));
  drawCurve(half, names, floor, dTarget);
}

function drawCurve(half, names, floor, dTarget) {
  const g = $("curve");
  g.replaceChildren();
  const L = 50, R = 700, T = 15, B = 290, xs = [1, 2, 4, 6, 8];
  const X = (c) => L + (R - L) * (xs.indexOf(c) / (xs.length - 1));
  const Y = (v) => T + (B - T) * (1 - (v + 1) / 2);
  for (let v = -1; v <= 1.001; v += 0.25) {
    g.append(svg("line", { x1: L, x2: R, y1: Y(v), y2: Y(v), stroke: "currentColor", opacity: v === 0 ? 0.4 : 0.1 }));
    svgText(g, { x: L - 6, y: Y(v) + 4, "text-anchor": "end", "font-size": 11, fill: "currentColor" }, v.toFixed(2));
  }
  for (const c of xs) svgText(g, { x: X(c), y: B + 18, "text-anchor": "middle", "font-size": 11, fill: "currentColor" }, `after ${c}`);
  g.append(svg("line", { x1: L, x2: R, y1: Y(dTarget), y2: Y(dTarget), stroke: "#2f9e44", "stroke-dasharray": "6 4", "stroke-width": 2 }));
  svgText(g, { x: R, y: Y(dTarget) - 5, "text-anchor": "end", "font-size": 11, fill: "#2f9e44" }, `pass mark ${fmt(dTarget)}`);
  g.append(svg("line", { x1: L, x2: R, y1: Y(floor), y2: Y(floor), stroke: "#b42318", "stroke-dasharray": "2 4", "stroke-width": 2 }));
  svgText(g, { x: R, y: Y(floor) + 14, "text-anchor": "end", "font-size": 11, fill: "#b42318" }, `trial and error ${fmt(floor)}`);
  const leg = $("legend");
  leg.replaceChildren();
  leg.className = "legend";
  names.forEach((n, i) => {
    const m = half[n];
    if (m.d_1 === undefined) return;
    const col = COLOURS[i % COLOURS.length];
    const pts = xs.map((c) => `${X(c)},${Y(m["d_" + c])}`).join(" ");
    g.append(svg("polyline", { points: pts, fill: "none", stroke: col, "stroke-width": 2.5 }));
    for (const c of xs) g.append(svg("circle", { cx: X(c), cy: Y(m["d_" + c]), r: 3.5, fill: col }));
    leg.append(el("span", {}, el("i", { style: `background:${col}` }), n));
  });
}

async function startBatch() {
  try {
    await api(`/api/batch?mind=${encodeURIComponent($("bmind").value)}&half=${$("bhalf").value}`, { method: "POST" });
    pollBatch();
  } catch (e) { $("bstatus").textContent = e.message; }
}

async function pollBatch() {
  const b = await api("/api/batch");
  $("bprog").max = Math.max(1, b.total);
  $("bprog").value = b.done;
  $("bstatus").textContent = b.error ? `error: ${b.error}` : b.running ? `${b.mind}: ${b.done} of ${b.total} runs` : (b.finished_at ? `done at ${b.finished_at}` : "");
  if (b.running) setTimeout(pollBatch, 1000); else if (b.finished_at) loadBoard();
}

// ------------------------------------------------------------------ variants

async function loadVariants() {
  const rows = await api("/api/variants");
  const box = $("vtable");
  box.replaceChildren();
  if (!rows.length) { box.append(el("p", {}, "No variants logged yet.")); return; }
  const tbl = el("table");
  tbl.append(el("tr", {}, ...["#", "variant", "settings", "families", "settle", "copies", "D_learn", "apples vs strangers", "LookReject h1/far", "Q sour"].map((h) => el("th", {}, h))));
  rows.forEach((r, i) => {
    const s = r.summary;
    tbl.append(el("tr", {}, el("td", {}, i + 1), el("td", {}, r.variant), el("td", { class: "muted" }, JSON.stringify(r.params)), el("td", {}, r.half),
      el("td", {}, fmt(s.settle_rate)), el("td", {}, fmt(s.copy_accept)), el("td", {}, el("b", {}, fmt(s.d_learn))), el("td", {}, fmt(s.fmn)),
      el("td", {}, `${fmt(s.lr_h1)} / ${fmt(s.lr_far)}`), el("td", {}, fmt(s.dq_sour))));
  });
  box.append(el("div", { class: "card scroll" }, tbl));
}

start().catch((e) => { $("status").textContent = "The Lab could not start: " + e.message; $("status").className = "err"; });
