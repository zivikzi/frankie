# Frankie Lab

Frankie Lab lets you watch a mind think, one decision at a time, in your own browser. You can also compare the minds:

- **E1**, the new, plain elimination mind that can merge kinds;
- **K-F**, the Week 4 spiking tower;
- **trial and error** (B1n-bot-r and B1n-mind);
- **the answer-key control** (B2e).

Everything runs on your computer. Nothing is sent anywhere.

**Tonight's results** are in [RESULTS.md](RESULTS.md). In short, E1 beat trial and error on families it was never tuned on (D_learn 0.45 against 0.24), and merging kinds is what made the difference.

## Run it

You need an internet connection only the first time.

### 1. Download the Lab

Go to https://github.com/zivikzi/frankie/archive/refs/heads/claude/frankie-lab.zip. Your browser downloads a zip file. Unzip it, which gives you a folder called `frankie-claude-frankie-lab`.

### 2. Install `uv`, once

`uv` is a small, free tool that fetches the right Python and the two packages the Lab needs (NumPy and Numba). It doesn't change anything else on your computer.

- **Windows.** Open **PowerShell** (press the Start key, type `powershell`, press Enter) and paste:
  ```
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  Then close PowerShell and open it again.
- **macOS.** Open **Terminal** (press Cmd+Space, type `terminal`, press Enter) and paste:
  ```
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  Then close Terminal and open it again.
- **Linux.** Open a terminal and paste the same line as on macOS.

### 3. Start the Lab

In the same window, go into the unzipped folder. The easiest way is to type `cd ` (with a space after it), drag the folder onto the window, and press Enter. Then type:

```
uv run python explore/lab.py
```

The first time, it takes a few minutes to download Python and the packages. After that it starts in seconds. Your browser then opens the Lab on its own. If it doesn't, the window shows an address such as `http://127.0.0.1:8765/`; copy it into your browser.

Leave the window open while you use the Lab. Press Ctrl+C in it to stop.

## What you'll see

### Watch a run

Pick a mind, a family and a run, then click **Load**. Step through with ◀ ▶, or the arrow keys, or press ▶ Play.

- **The object** is drawn from its numbers:
  - colour from its hue;
  - shape from its size, roundness and lobes;
  - stem, leaves, spots, thorns and a sticker from its parts traits;
  - shine and texture from its details;
  - the background and what it sits on from the scene.

  Smell and taste are shown as bars. Taste is known only after eating.
- **Its numbers** are listed outside in: context, then object, then parts, then details.
- **Verdict and choice** shows what the mind thought the object was, and whether it ate or skipped. It also shows the outcome (nourishing +15, poison −20, nothing 0) and the energy bar, where the red line is the mind's reserve.
- **Thinking** lists every kind the mind remembers, and where each was ruled out. A crossed-out kind was eliminated at that layer; hover over it to see which traits didn't fit. For E1 this is exactly how it decides. For K-F it shows which kinds were dropped at the handovers between layers, and any objections. The bots keep no kinds.
- **Memory** shows each kind the mind holds:
  - its ranges, as small bar charts over the 22 traits, darker where the trait matters more;
  - its record: how many times it nourished, poisoned or did nothing.

  New, split, stretched and merged kinds are highlighted at the moment they happen.
- **Reveal what it really is** shows the object's true role: the first apple h1, a teaching apple, a far apple, a look-alike, a neutral, or h2, the sour apple. It also marks the mind's apple kinds. Leave it off to test your own eye first.

Untick **show the checks** to step through only the lessons: the 40 warm-up tastes, the 8 teaching tastes and the sour test. The checks are the throwaway copies the test quizzes after tastes 1, 2, 4, 6 and 8.

### Scoreboard

The scoreboard shows every mind's key measures against the kill test's pass marks, in green or red. It covers the **search half** (odd families, where E1 was developed) and the **check half** (even families, never tuned on). It also has the learning curve: how D grows over the 8 tastes, with the pass mark and trial and error drawn on it.

**Run a batch** re-runs one mind on 15 families × 10 runs and updates the scoreboard. It takes seconds for the bots and E1, and a few minutes for K-F.

### Variants tried

This tab lists every version of E1 tried while exploring, with its numbers.

## The files

| File | What |
|---|---|
| `lab.py` | The local web server: starts the Lab and opens your browser |
| `e1.py` | E1, the elimination mind with merging; every piece is labelled conventional or untested |
| `minds.py` | The minds compared, run through the frozen kill-test harness |
| `runtrace.py` | Records one run step by step for "Watch a run" |
| `batch.py` | Runs minds over a half of the tuning set and writes `results/scoreboard.json` |
| `web/` | The page (plain HTML, CSS and JavaScript; no outside libraries) |
| `results/scoreboard.json` | The precomputed scoreboard, so the Lab opens instantly |
| `results/variants.jsonl` | Every E1 variant tried, with its numbers |
| `results/traces/` | Saved runs; any other run is worked out when you ask for it |

To re-run everything yourself (about 10 minutes):

```
uv run python explore/batch.py --half both
```
