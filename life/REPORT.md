# Frankie in a 3D world: first results

Written on 2 November 2026 (UTC) for Aitzaz. Every number below comes from **batch 3**: 200 fresh random worlds, with every creature living in the same 200 worlds for up to 3,000 ticks each. The seeds are in `life/results/batch.json` and `life/results/seeds.log`; re-run them with `uv run python life/batch.py --seed-file life/results/batch.json`. Before seeing this batch I said it would be the one reported. Two earlier 50-seed batches (batch 1, batch 2) are logged too, and point the same way; see "Every batch run" below.

## How Frankie is doing

**He learns what is safe to eat, and he learns that the same fruit can be safe in one place and poison in another. He does not yet solve obstacles: with no detour code, he pushes at a fence while he can see the food through it.**

- **His poison share falls as he eats:** 29% over his first 5 eats, 17% over eats 6–10, 16% over eats 11–15, and 8% over eats 16–20. Trial and error falls more slowly (35% → 20%), and the wanderer doesn't improve at all (33% → 41%).
- **He lives longest:** 1,441 ticks on average, against 1,101 for trial and error and 704 for the wanderer. A quarter of his lives reach the 3,000-tick cap, against 9% and 1%. Part of this is his drive rather than his recognition: when fed he rests, which costs half as much as walking. Trial and error has the same drive, so Frankie against trial and error is the fair comparison there.
- **The context rule (Aitzaz's outside-in idea): yes.** The context fruit looks the same everywhere but feeds in one region and poisons in another. 45% of Frankie's first context-fruit eats were in the poison region, and only 13% of his later ones. Trial and error went from 46% to 34%, the wanderer from 53% to 47%.
- **Context is what matters; merging isn't.** Without context (no scene or host traits), Frankie drops to trial-and-error level: 1,117 ticks and 27% poison. Without merging, he does as well as with it (1,505 ticks, 23% poison). On the bench, merging was what made E1 work. In the world it isn't needed, probably because a life holds only 10 to 20 eats and context already keeps the regions apart.
- **His sharp looks matter:** 47% of the looks that came before a decision changed it, usually from "eat" to "leave it".
- **He eats less than the others:** 0.27 meals per 100 ticks, against about 0.30. He refuses more, and he rests when fed.
- **Obstacles: no better than luck.** On his first try at food behind a fence or across the river, he got there 7 times out of 104 (7%), median 869 ticks. The wanderer, walking at random, got there 12 times out of 111 (11%), median 466. His later tries weren't faster in a way that counts: 4 of 51. In 37 of his 145 lives in fence worlds he pushed at a fence 50 or more times (149 bumps on average in those lives).

| Creature | Lifespan mean (median) | Lived to 3,000 | Food per 100 ticks | Poison share | Poison, eats 1–5 / 6–10 / 11–15 / 16–20 | Settled lives | Looks that changed the decision | Context fruit in its poison region: first → later |
|---|---|---|---|---|---|---|---|---|
| **Frankie** | **1441** (1026) | **25%** | 0.27 | **22%** | 29% / 17% / 16% / 8% | 31 of 200 | 47% | **45% → 13%** (137 + 359 eats) |
| Trial and error | 1101 (720) | 9% | 0.30 | 30% | 35% / 28% / 22% / 20% | 10 of 200 | 33% | 46% → 34% (139 + 271 eats) |
| Wanderer | 704 (549) | 1% | 0.31 | 32% | 33% / 28% / 25% / 41% | 2 of 200 | – | 53% → 47% (122 + 204 eats) |
| Frankie, no merging | 1505 (1152) | 26% | 0.33 | 23% | 30% / 21% / 15% / 9% | 30 of 200 | 44% | 46% → 17% (144 + 351 eats) |
| Frankie, no context | 1117 (807) | 8% | 0.19 | 27% | 30% / 19% / 18% / 14% | 12 of 200 | 63% | 44% → 22% (106 + 165 eats) |

- **"Settled"** means his poison share stayed under 10% for good: no poisoning in at least his last 10 eats.
- **Sample sizes:** the eat-number groups get thin late in life. Frankie's eats 1–5 pool 827 eats, 6–10 pool 469, 11–15 pool 272 and 16–20 pool 106; few lives reach 20 eats.
- **The survivor effect:** creatures that keep eating poison die, so late groups lean towards the lucky. That affects every creature alike.
- **Frankie without context still improves on the context fruit** (44% → 22%). A likely reason is his place memory: he walks back to squares that fed him, not to ones that poisoned him. I haven't tested that reason.

### Obstacles

| Creature | First try: got there | Median ticks | Median metres | Later tries: got there | Median ticks | Fence bumps per life | River bumps per life |
|---|---|---|---|---|---|---|---|
| Frankie | 7 of 104 (7%) | 869 | 358 | 4 of 51 (8%) | 322 | 29.7 | 12.5 |
| Trial and error | 7 of 97 (7%) | 614 | 290 | 3 of 36 (8%) | 626 | 49.1 | 13.2 |
| Wanderer (luck) | 12 of 111 (11%) | 466 | 402 | 4 of 71 (6%) | 232 | 1.6 | 2.3 |
| Frankie, no merging | 6 of 104 (6%) | 886 | 426 | 4 of 55 (7%) | 322 | 34.8 | 14.2 |
| Frankie, no context | 4 of 106 (4%) | 1206 | 500 | 3 of 42 (7%) | 1271 | 27.1 | 14.9 |

- **When an episode starts:** the first time the creature sees good food behind a fence (from outside) or across the river (from the other side), while at least 4 m clear of the fence or bank.
- **When it ends:** when the creature gets inside the fence or across the river.
- **"First try"** is the first episode of each life, which is always on a brand-new layout.
- **Layouts:** 145 of the 200 worlds had obstacles and 55 had none.

## What today's Frankie does at an obstacle

Frankie was run against the obstacles with **no detour code at all**: no route-finder, no wall-following, and nothing that reacts to a bump except writing "Bumped into something solid" in his thoughts. What he does:

- **He pushes at the fence.** Fences are see-through, so the food stays in view and stays his target. He steers straight at it, bumps, and steers straight at it again, for hundreds of ticks. Each bump costs a little energy (0.02 on top of the tick).
- **Luck sometimes gets him out.** His only way out is a whim: now and then randomness proposes "walk off somewhere for a while", and his character accepts with a chance tied to his boldness (halved when hungry). If the whim happens to carry him round to the gap, he gets in. This is how his 7 first-try successes happened. It's less than the wanderer's luck, because Frankie keeps returning to the shortest line.
- **He doesn't give up on purpose.** He has no notion of "this isn't working". A bump changes nothing he keeps.
- **His place memory makes walls worse.** When hungry, he walks in a straight line to the square that fed him most. If a wall is in the way, he pushes at the wall until he starves; I watched him die this way in seed 3.
- **The river is the same.** He pushes at the bank towards food on the far side, and crosses only when a whim walks him onto the ford.

## Detour ideas for Aitzaz to choose from (proposed, not built)

Each idea uses only Frankie's own pieces: elimination, the drive, place memory, and "randomness proposes, character decides". None uses a route-finder or a map he didn't build himself.

1. **Bumps rule out directions (untested; elimination applied to moving).**
   - **The idea:** Frankie treats "which way do I walk" like "what is this object". He has a few candidate headings (say 8). The straight line to the food is the first candidate, and the others follow by how far they turn away from it. A bump eliminates the heading he was on, and nearby headings lose a little standing.
   - **How he walks:** randomness proposes one of the surviving headings, and his character decides how far from the food he's willing to turn. A bold Frankie accepts big turns sooner; a careful one tries the near headings first.
   - **What a detour is here:** walking away from the food happens only after the closer headings are eliminated. The eliminations fade after a while, or when the food leaves his view.
   - **Closest known method:** the "bug" algorithms in robotics (follow the obstacle's edge until the straight line is free again), which are conventional. This idea differs by eliminating and choosing at random, not following edges.
   - **Expected effect:** this is the only idea that could beat luck on a **brand-new** layout.
2. **Frustration lowers the target's worth (untested; from the drive).**
   - **The idea:** each bump while chasing a target counts against that target. Its expected worth drops below other options (other food in view, a remembered square, or a whim), and he switches.
   - **What it fixes:** the starve-at-the-wall death. It doesn't find the gap.
   - **Closest known method:** patch-leaving rules in foraging theory (Charnov's marginal value theorem), which are conventional.
3. **Remembering doors (untested; place memory).**
   - **The idea:** when Frankie gets past something he once bumped (through a fence gap, or over the ford), his place memory marks that square as a door, linked to the square of the bump. Next time he bumps in that square, or sees food beyond it, he walks to the remembered door first.
   - **What it gives:** faster later tries, which is "getting faster with experience". It can't help a first try on a new layout.
   - **Closest known method:** landmark and route memories in cognitive-map research, which are conventional ideas. Doing it inside Frankie's coarse place memory is untested.

**My recommendation:** try idea 1 first, because only it can beat the wanderer's luck on a new layout, and it's Aitzaz's elimination applied to moving. Add idea 3 afterwards, to test getting faster.

## What was built

Everything is in `life/` on branch `claude/frankie-mvp`. It runs with `uv run python life/lab.py`.

- **The world (`life/world3d.py`, `terrain.py`, `ecology.py`, `obstacles.py`; conventional).**
  - **Land:** a 128 m square of smooth noise terrain, split by height and a second noise field into meadow, forest, marsh and rocky.
  - **Kinds:** made with the bench's own generator (`src/world`, read-only), keyed by the world's seed.
    - Apple A, with two poison look-alikes.
    - Apple B, with one poison look-alike.
    - Three neutral kinds.
    - The context fruit, which feeds in one region and poisons in another.
  - **Where kinds grow:** each kind favours a region (70% of its patches) and a second region (25%). A look-alike's two favourite regions are its apple's two, swapped, so apples and look-alikes meet.
  - **Objects:** each is the bench's 22 numbers, with scene and host set by the region it grows in. Eaten objects regrow at the same spot after 250–450 ticks, as a fresh draw.
  - **Obstacles:** two thirds of worlds have them; one third have none, for comparison.
    - 1–2 see-through fences, each with one gap, around 7 apples.
    - 0–2 solid walls.
    - Half the obstacle worlds have a river across the map, with one ford or log, and apples on the far side.
- **The body (`life/body.py`).**
  - **The blurry view:** a cone 22 m deep and 120° wide, blocked by hills and walls but not fences. It gives the 6 context and object traits, with noise from 2 noise widths close up, growing by 0.25 per metre.
  - **The sharp look:** one object within 4 m. It gives all 18 traits at 1 noise width and costs 0.25 energy.
  - **Touch and taste:** touch is a bump; taste comes only by eating.
  - **Energy:** start at 60, +15 for nourishing, −20 for poison, 0 for nothing. Each tick costs 0.04, a step 0.04 more, plus 0.08 per metre climbed. The most a creature can hold is 100; it dies at 0. All the numbers are in `life/config.py`.
- **Frankie's mind (`life/minds/frankie.py`, `forager.py`).**
  - **Recognition** is E1's elimination, imported from the frozen `src/mind/e1.py`. His memory writes are copied from it, with one change: stretching ignores traits he never read, since in the world he may eat something seen only blurrily.
  - **Attention:** he takes a sharp look only when the blurry view leaves candidates that disagree, or leaves none and he means to try the thing anyway.
  - **The drive:** spend-or-conserve, with reserve and boldness drawn at birth (the bench's ranges). Randomness proposes; character decides.
  - **Place memory:** 16 m squares, each counting fed, poisoned and nothing.
  - **What he senses:** only what the body senses. A test swaps every object's hidden nature and checks that he acts the same until his first eat.
- **The baselines.**
  - **The wanderer:** walks at random and eats whatever he bumps into.
  - **Trial and error:** remembers every item eaten exactly, and expects the same outcome from anything within 10 noise widths of one of them. It has Frankie's body, drive and place memory, so only recognition differs.
  - **Frankie without merging, and Frankie without context.**
- **The page (`life/web/`, three.js 0.170.0 kept in the repository).**
  - **The 3D world:** terrain coloured by region, fruits drawn from their numbers, fences, walls, the river, each creature with its view cone and trail, and flags for its place memory.
  - **Controls:** play/pause, step, speed, fast forward (with an option to stop drawing), the world's seed (shown and editable), and which creature runs, or two side by side in the same world.
  - **The side panel:** energy against reserve, what he's doing and why in plain words, the kinds he's learned, the places he remembers, the obstacle episodes, and a running chart.
  - **The Results tab:** this batch.
  - **Logs:** go to `life/logs/` (server, events, and errors from the page).
- **Tests:** `tests/test_life.py`, with 27 tests. They cover:
  - fences, walls and the river;
  - energy, eating, regrowth and the context fruit;
  - the view cone, hills, noise, and taste only by eating;
  - that the mind can't reach any world object, and acts the same when hidden natures are swapped;
  - that no mind imports anything world-side or anything named like a route-finder;
  - that the server serves the page.

  They found two bugs: a step aimed exactly at a fence post went through, and context fruit could spill into a third region. Both are fixed.

## The LLM creature (later, optional; every choice untested)

`life/minds/llm.py` is one more opponent, not Frankie: Frankie's mind never uses a language model.

- **Body and senses:** the same as Frankie's. Each decision is put to the LLM as text holding only numbers ("[2] 3.4 m, +12 deg, t1=0.62 …"), its energy and reserve, and its history of eats with their energy changes and tastes.
- **Nothing is named:** there is no "apple", "poison", "forest" or "red", so its training can't hand it this world's rules. A test checks every prompt for such words.
- **Its memory is its prompt:** the last 40 lines of its eating history.
- **When it's asked:** only at decision points.
  - Something in view could be approached and it has no target. It's asked at most every 15 ticks, or at once when its energy crosses its reserve.
  - It reaches its target: look, eat or leave.
  - Its view is empty: wander or rest, every 100 ticks.
  - It has bumped 10 times on the way to its target. Touch is a sense Frankie has too; Frankie just has no code that uses it.

  Simple shared code walks it to what it chose.
- **Plumbing:** the standard library's urllib, the key from `ANTHROPIC_API_KEY`, the model from `--llm-model` or `FRANKIE_LLM_MODEL` (none is written in the code). Every call (prompt, answer, tokens) is saved under `life/results/llm-runs/`, and `ReplayLLM` re-runs a saved race without paying.
- **To race:** `ANTHROPIC_API_KEY=… uv run python life/batch.py --seeds 10 --creatures frankie,trial,llm --llm-model <model>`. The batch reports calls and tokens. The headline measure, how many eats it took before the poison share stayed under 10%, is the "settled" column.
- **Expect** a strong LLM may well beat today's Frankie, and Frankie runs on a laptop CPU while the LLM uses a data centre.

## Labels: conventional or untested

- **Conventional (infrastructure):**
  - the noise terrain and regions;
  - line-segment collision and sight;
  - the view cone;
  - straight-line steering;
  - the random walk;
  - the nearest-item trial-and-error baseline;
  - place memory as a grid of counts.
- **Untested (mind):**
  - E1's elimination with stretch, split and merge;
  - attention driven by elimination;
  - "fed me" share against the bench bar as "believes is good";
  - the spend-or-conserve drive with whims;
  - the context rule as a test of outside-in recognition.
- **Not used anywhere in a mind:** gradient descent, reinforcement learning, neural networks, nearest-neighbour matching (only the baseline uses it), language models, path-finding, or anything that reads a kind's nature or a region's name.

## Departures from the brief

- **Thinking is free in the world.** The bench charges 0.001 per check; with dozens of objects in view every tick, that would cost more than walking. Looks, steps, climbs and bumps are charged.
- **E1's memory writes are copied, with one change** (stretching ignores unread traits). The frozen file is untouched, and so is every other frozen file: `sha256sum -c` passes on all three manifests.
- **"Believes is good"** uses the kind's "fed me" share against the bench's bar (0.9 − 0.3 × boldness), not the bench's "energy stayed above reserve" share.
- **Two creatures side by side share one world and its food.** They aren't in two copies of it.
- **The narration names regions ("in the forest").** Only the page does this, from where the object is. Frankie himself never knows a region's name.
- **The LLM race** (later, optional) is built, but has been run only against a scripted fake LLM. There's no API key on this computer, so no real race has happened. See "The LLM creature" below.

## Every batch run

| Batch | Seeds | What | Frankie lifespan / poison share | Trial and error | Wanderer |
|---|---|---|---|---|---|
| 1 | 50 | first look; obstacle and context measures still being fixed (`batch-01-superseded.json`) | 1472 / 21% | 950 / 34% | 775 / 30% |
| 2 | 50 | measures fixed (`batch-02-50-seeds.json`) | 1264 / 25% | 857 / 34% | 783 / 29% |
| **3** | **200** | **reported (`batch.json`)** | **1441 / 22%** | **1101 / 30%** | **704 / 32%** |

The creatures' minds were the same in all three batches. Only the obstacle and context measures changed, between batches 1 and 2. A development look on 30 seeds came before batch 1. Its seeds are in `seeds.log`, and nothing was tuned from it.
