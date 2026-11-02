# Frankie's world

Watch Frankie live in a 3D world in your browser. He wanders hills, meadows, forests, marshes and rocks, decides what to eat, learns which fruit feeds him and which poisons him, and runs into fences, walls and a river. Simple baselines can live in the same worlds, for comparison.

**First results:** [REPORT.md](REPORT.md). In short, Frankie learns what is safe to eat, and that the same-looking fruit can be safe in one region and poison in another, better than trial and error. But he doesn't yet get round obstacles any better than luck.

Everything runs on your computer. Nothing is sent anywhere.

## Run it

1. **Get the code.** Download https://github.com/zivikzi/frankie/archive/refs/heads/claude/frankie-mvp.zip and unzip it.
2. **Install `uv`, once.** `uv` fetches the right Python (3.12) and NumPy.
   - **macOS or Linux:** paste `curl -LsSf https://astral.sh/uv/install.sh | sh` into a terminal.
   - **Windows:** paste `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` into PowerShell.

   Then close the window and open a new one.
3. **Start the world.** In a terminal, go into the unzipped folder and run:
   ```
   uv run python life/lab.py
   ```
   Your browser opens at http://127.0.0.1:8770/. Leave the terminal open while you watch, and press Ctrl+C there to stop.

The world plays until you press **Pause** (or the space bar). When every creature has died, a fresh random world starts after a few seconds. To stop that, untick **Keep going**.

## What you see

- **The land** is coloured by region: light green for meadow, dark green for forest, grey-green for marsh and grey-brown for rocky ground.
- **Each fruit** is drawn from its own 22 numbers: colour, size, roundness, lobes, stem, leaves, spots and thorns. Look-alikes really do look alike.
- **Obstacles:** fences are see-through mesh rings with one gap; walls are grey; the river is blue, with a sandy ford or a log across it.
- **Frankie** is the orange creature, with a pale cone showing what he can see and a trail showing where he's been. A dashed white line means he's taking a sharp look. Flags show his place memory: green where he was fed, red where he was poisoned.
- **The side panel** shows:
  - his energy, with a white mark at his reserve;
  - what he's doing and why, in plain words;
  - what he's eaten and his sharp looks;
  - a chart of his energy, with red bars for his poison share per 50 ticks;
  - the kinds he has learned and the places he remembers;
  - any food he has seen behind an obstacle.
- **The Results tab** shows the batch numbers for every creature, with the learning curves.

## Controls

- **Play/Pause, Step:** the space bar and `.` work too.
- **Speed:** ticks per second.
- **Fast forward:** runs as fast as the computer can. Tick **Skip drawing** to save the graphics work.
- **Creature, vs:** pick who lives in the world, and optionally a second creature in the same world. Changing either restarts the same world.
- **Seed and New world:** every world comes from a random seed, shown at the top left. Type a seed to see that world again, or leave it blank for a fresh one.
- **Follow:** the camera follows the creature. Untick it to fly around: drag to orbit, scroll to zoom, right-drag to pan.

Start options: `--seed N`, `--creature trial` (repeat it for two creatures), `--paused`, `--port 8770` and `--no-browser`.

## The creatures

- **Frankie:** E1's elimination (from `src/mind/e1.py`), a sharp look only when it could change his mind, a spend-or-conserve drive, and place memory.
- **Trial and error:** remembers every item he ate exactly. He has the same body, drive and place memory as Frankie.
- **The wanderer:** walks at random and eats anything he bumps into. He shows the luck level.
- **Frankie, no merging** and **Frankie, no context:** Frankie with one of Aitzaz's ideas switched off.

## The batch (the numbers in REPORT.md)

```
uv run python life/batch.py --seeds 200
```

This runs every creature in the same fresh random worlds (about a minute on a laptop). It writes `life/results/batch.json` and appends every seed to `life/results/seeds.log`. Use `--seed-file life/results/batch.json` to re-run the same worlds.

## Logs, for debugging

`life/logs/` holds:

- `server.log`: start-up, every control pressed, every new world with its seed, and any error;
- `events.jsonl`: every eat and death, with seed and tick;
- `client.log`: anything the page itself reports, such as errors and the frame rate.

If the simulation hits an error, it pauses, and the page shows the error in red.

## Tests

`uv run pytest tests/test_life.py` checks:

- the world's rules;
- the senses;
- that no mind can reach hidden truth;
- that no mind contains a route-finder;
- that the server serves the page.

## Files

| File | What |
|---|---|
| `config.py` | every number, in one place |
| `terrain.py`, `obstacles.py`, `ecology.py`, `world3d.py` | the world |
| `body.py` | the body and its senses: the only door between world and mind |
| `minds/` | Frankie, the baselines, and the shared drive, attention and place memory |
| `sim.py`, `metrics.py`, `batch.py` | running lives and measuring them |
| `lab.py`, `web/` | the live page |
