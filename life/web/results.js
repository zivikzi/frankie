// The results view: batch numbers for every creature, with the learning curves.
export async function show(el) {
  const r = await (await fetch("/api/results")).json();
  if (!r.runs) { el.innerHTML = "<h2>Results</h2><p>No batch has been run yet. Run <code>uv run python life/batch.py</code>.</p>"; return; }
}
