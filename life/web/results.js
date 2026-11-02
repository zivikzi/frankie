// The results view: the batch numbers for every creature, with the learning curves.
// Reads life/results/batch.json through /api/results (made by `uv run python life/batch.py`).

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
const pct = (x) => (x == null ? "–" : (100 * x).toFixed(0) + "%");
const num = (x, d = 0) => (x == null ? "–" : Number(x).toFixed(d));

function lineChart(canvas, series, opts) {
  const ctx = canvas.getContext("2d");
  const W = (canvas.width = canvas.clientWidth * 2), H = (canvas.height = canvas.clientHeight * 2);
  const L = 70, R = 20, Tp = 20, B = 50;
  ctx.clearRect(0, 0, W, H);
  ctx.font = "22px system-ui"; ctx.fillStyle = "#95a3b1"; ctx.strokeStyle = "#2f3a46"; ctx.lineWidth = 1;
  const xmax = opts.xmax, ymax = opts.ymax;
  const X = (x) => L + (W - L - R) * x / xmax, Y = (y) => H - B - (H - B - Tp) * y / ymax;
  for (let k = 0; k <= 4; k++) {
    const y = (ymax * k) / 4;
    ctx.beginPath(); ctx.moveTo(L, Y(y)); ctx.lineTo(W - R, Y(y)); ctx.stroke();
    ctx.fillText(opts.yfmt(y), 6, Y(y) + 7);
  }
  (opts.xticks || []).forEach(([x, label]) => ctx.fillText(label, X(x) - 12, H - B + 30));
  ctx.fillText(opts.xlabel, L, H - 6);
  for (const s of series) {
    ctx.strokeStyle = s.colour; ctx.lineWidth = s.width || 4; ctx.beginPath();
    let started = false;
    for (const [x, y] of s.points) {
      if (y == null) { started = false; continue; }
      started ? ctx.lineTo(X(x), Y(y)) : ctx.moveTo(X(x), Y(y));
      started = true;
    }
    ctx.stroke();
  }
}

export async function show(el) {
  const [r, cs] = await Promise.all([fetch("/api/results").then((x) => x.json()), fetch("/api/creatures").then((x) => x.json())]);
  if (!r.runs) {
    el.innerHTML = "<h2>Results</h2><p>No batch has been run yet. Run <code>uv run python life/batch.py</code> and come back.</p>";
    return;
  }
  const S = r.summary;
  const names = Object.keys(S);
  const label = (n) => (cs[n] ? cs[n].label : n);
  const colour = (n) => (cs[n] ? cs[n].colour : "#888");
  const f = S.frankie, t = S.trial, w = S.wanderer;
  const head = f && t && w
    ? `Frankie lived ${num(f.lifespan_mean)} ticks on average, against trial and error's ${num(t.lifespan_mean)} and the wanderer's ${num(w.lifespan_mean)}. ` +
      `His poison share fell from ${pct(f.by_eat[0] && f.by_eat[0].poison_share)} over his first 5 eats to ${pct(f.by_eat[2] && f.by_eat[2].poison_share)} over eats 11–15 ` +
      `(trial and error: ${pct(t.by_eat[0] && t.by_eat[0].poison_share)} to ${pct(t.by_eat[2] && t.by_eat[2].poison_share)}).`
    : "";
  const byEat = (s, k) => (s.by_eat[k] ? pct(s.by_eat[k].poison_share) + `<span class="muted"> (${s.by_eat[k].n})</span>` : "–");
  const rows = names.map((n) => {
    const s = S[n];
    return `<tr><td><span style="color:${colour(n)}">●</span> ${esc(label(n))}</td>
      <td class="num">${num(s.lifespan_mean)}</td><td class="num">${num(s.lifespan_median)}</td><td class="num">${pct(s.survived_share)}</td>
      <td class="num">${num(s.food_per_100, 2)}</td><td class="num">${pct(s.poison_share_all)}</td>
      <td class="num">${byEat(s, 0)}</td><td class="num">${byEat(s, 1)}</td><td class="num">${byEat(s, 2)}</td><td class="num">${byEat(s, 3)}</td>
      <td class="num">${s.settled_runs} <span class="muted">(${num(s.settled_median_eats, 0)})</span></td>
      <td class="num">${num(s.looks_per_life, 1)}</td><td class="num">${pct(s.looks_changed_share)}</td>
      <td class="num">${pct(s.ctx_bad_share_early)} → ${pct(s.ctx_bad_share_late)} <span class="muted">(${s.ctx_eats})</span></td></tr>`;
  }).join("");
  const ep = (e) => `${e.reached}/${e.n} (${pct(e.reached_share)})`;
  const obsRows = names.map((n) => {
    const s = S[n];
    return `<tr><td><span style="color:${colour(n)}">●</span> ${esc(label(n))}</td>
      <td class="num">${ep(s.episodes_first)}</td><td class="num">${num(s.episodes_first.median_ticks)}</td><td class="num">${num(s.episodes_first.median_metres)}</td>
      <td class="num">${ep(s.episodes_later)}</td><td class="num">${num(s.episodes_later.median_ticks)}</td>
      <td class="num">${num(s.bumps_fence_mean, 1)}</td><td class="num">${num(s.bumps_wall_mean, 1)}</td><td class="num">${num(s.bumps_river_mean, 1)}</td>
      <td class="num">${num(s.lifespan_obstacle_worlds)} / ${num(s.lifespan_plain_worlds)}</td></tr>`;
  }).join("");
  el.innerHTML = `
    <h2>Results: ${r.seeds.length} fresh random worlds per creature</h2>
    <p><b>${esc(head)}</b></p>
    <p>Batch started ${esc(r.started.replace('T', ' ').replace('Z', ''))} UTC${r.label ? " (" + esc(r.label) + ")" : ""}; every creature lived in the same ${r.seeds.length} worlds, each up to ${r.ticks} ticks. Seeds are listed at the bottom and in life/results/seeds.log.</p>
    <table><tr><th>creature</th><th class="num">lifespan<br>mean</th><th class="num">median</th><th class="num">lived to<br>${r.ticks}</th>
      <th class="num">food per<br>100 ticks</th><th class="num">poison<br>share</th>
      <th class="num">poison<br>eats 1–5</th><th class="num">6–10</th><th class="num">11–15</th><th class="num">16–20</th>
      <th class="num">settled<br>(eats)</th><th class="num">sharp<br>looks</th><th class="num">looks that<br>changed it</th>
      <th class="num">context fruit eaten where it poisons:<br>first one → later ones</th></tr>${rows}</table>
    <p>“Settled” counts lives whose poison share stayed under 10% for good (no poisoning in at least the last 10 eats); in brackets, the median number of eats it took.
    The context column: the context fruit looks the same everywhere but feeds in one region and poisons in another. It shows the share of context-fruit eats made in the region where it poisons, for each life's first one, and for all later ones (pooled; in brackets, how many eats in all). Learning the rule means the later share falls well below the first.</p>
    <div class="charts">
      <div class="card"><h3>Poison share by eat number</h3><canvas id="ch-eat"></canvas><div class="key" id="key1"></div></div>
      <div class="card"><h3>Poison share over time (50-tick windows, pooled in fives)</h3><canvas id="ch-win"></canvas><div class="key" id="key2"></div></div>
      <div class="card"><h3>Still alive, by tick</h3><canvas id="ch-alive"></canvas><div class="key" id="key3"></div></div>
    </div>
    <h2>Obstacles: food behind a fence or across the river</h2>
    <p>An episode starts when the creature first sees food behind a fence (from outside) or across the river (from the other side) and ends when it gets inside the fence or across.
    The first episode in each life is its first try on a brand-new layout. The wanderer gives the luck level.</p>
    <table><tr><th>creature</th><th class="num">first try:<br>reached</th><th class="num">median<br>ticks</th><th class="num">median<br>metres</th>
      <th class="num">later tries:<br>reached</th><th class="num">median<br>ticks</th>
      <th class="num">fence bumps<br>per life</th><th class="num">wall</th><th class="num">river</th><th class="num">lifespan: obstacle<br>worlds / none</th></tr>${obsRows}</table>
    <h2>Seeds</h2><p class="muted" style="word-break:break-all">${r.seeds.join(" ")}</p>`;
  const keyHTML = names.map((n) => `<span><i style="background:${colour(n)}"></i>${esc(label(n))}</span>`).join("");
  ["key1", "key2", "key3"].forEach((k) => (el.querySelector("#" + k).innerHTML = keyHTML));
  const maxEat = Math.max(...names.map((n) => S[n].by_eat.length));
  lineChart(el.querySelector("#ch-eat"), names.map((n) => ({ colour: colour(n), points: S[n].by_eat.filter((b) => b.n >= 10).map((b, k) => [k, b.poison_share]) })),
    { xmax: Math.max(maxEat - 1, 1), ymax: 0.6, yfmt: (y) => pct(y), xlabel: "eats (groups of 5)", xticks: S[names[0]].by_eat.map((b, k) => [k, String(k * 5 + 1)]) });
  const maxW = Math.max(...names.map((n) => S[n].curve.length));
  const pooled = (curve) => { const out = []; for (let k = 0; k < curve.length; k += 5) { const seg = curve.slice(k, k + 5); const e = seg.reduce((a, c) => a + c.eats, 0), p = seg.reduce((a, c) => a + c.poison, 0); out.push([k + 2.5, e >= 15 ? p / e : null]); } return out; };
  lineChart(el.querySelector("#ch-win"), names.map((n) => ({ colour: colour(n), points: pooled(S[n].curve) })),
    { xmax: maxW, ymax: 0.6, yfmt: (y) => pct(y), xlabel: "tick", xticks: [0, 10, 20, 30, 40, 50, 60].filter((k) => k <= maxW).map((k) => [k, String(k * 50)]) });
  lineChart(el.querySelector("#ch-alive"), names.map((n) => ({ colour: colour(n), points: S[n].curve.map((c) => [c.window, c.alive / S[n].runs]) })),
    { xmax: maxW, ymax: 1, yfmt: (y) => pct(y), xlabel: "tick", xticks: [0, 10, 20, 30, 40, 50, 60].filter((k) => k <= maxW).map((k) => [k, String(k * 50)]) });
}
