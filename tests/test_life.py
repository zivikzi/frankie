"""Frankie's 3D world (life/): the world's rules, the mind's blindness to hidden truth, and the page's server."""

import ast
import json
import math
import pathlib
import sys
import threading
import urllib.request

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from life import body as B  # noqa: E402
from life import config as C  # noqa: E402
from life.ecology import LifeKind, LifeObject  # noqa: E402
from life.obstacles import Fence, Obstacles, River, Wall  # noqa: E402
from life.sim import Session  # noqa: E402
from life.world3d import World  # noqa: E402

MINDS = ("frankie", "trial", "wanderer", "frankie-no-merge", "frankie-no-context")


def flat_world(seed=5):
    """A real world with the ground flattened and every obstacle removed, for hand-made cases."""
    w = World(seed)
    w.terrain.height[:] = 1.0
    w.obstacles.fences.clear()
    w.obstacles.walls.clear()
    w.obstacles.river = None
    w.obstacles._rebuild()
    return w


def place(w, obj, x, z):
    obj.x, obj.z, obj.y = x, z, w.terrain.height_at(x, z)


# ------------------------------------------------------------------ obstacles


def test_fence_blocks_walking_but_not_its_gap_and_not_sight():
    obs = Obstacles()
    f = Fence(1, 50.0, 50.0, 7.0, gap_index=0)
    obs.add_fence(f)
    # straight in from the west (through segment 6, which is closed)
    assert obs.blocks_move(42.5, 50.0, 43.5, 50.0) == "fence"
    # through the gap (segment 0 spans angles 0 to 30 degrees)
    gx, gz = f.gap
    ux, uz = (gx - 50) / math.hypot(gx - 50, gz - 50), (gz - 50) / math.hypot(gx - 50, gz - 50)
    assert obs.blocks_move(gx + 0.5 * ux, gz + 0.5 * uz, gx - 0.5 * ux, gz - 0.5 * uz) is None
    # see-through
    assert obs.blocks_sight(40.0, 50.0, 50.0, 50.0) is False


def test_wall_blocks_walking_and_sight():
    obs = Obstacles()
    obs.add_wall(Wall(1, 50.0, 40.0, 50.0, 60.0))
    assert obs.blocks_move(49.5, 50.0, 50.5, 50.0) == "wall"
    assert obs.blocks_sight(45.0, 50.0, 55.0, 50.0) is True
    assert obs.blocks_sight(45.0, 30.0, 55.0, 30.0) is False


def test_river_blocks_except_at_its_crossing_and_never_blocks_sight():
    obs = Obstacles()
    obs.river = River(0, True, 64.0, 0.0, 128.0, 0.0, ford_u=30.0, crossing="ford")
    assert obs.blocks_move(61.0, 80.0, 62.0, 80.0) == "river"          # stepping into the water
    assert obs.blocks_move(61.0, 30.0, 62.0, 30.0) is None              # the ford
    assert obs.river.side(60, 80) != obs.river.side(68, 80)
    assert obs.blocks_sight(60, 80, 68, 80) is False


def test_a_creature_walking_into_a_fence_stays_outside_and_feels_it():
    w = flat_world()
    w.obstacles.add_fence(Fence(1, 50.0, 50.0, 7.0, gap_index=0))
    b = w.new_body(0, 1)
    b.x, b.z, b.heading = 40.0, 50.0, 0.0                                # facing east, at the fence's west side
    for _ in range(10):
        w.apply(b, {"do": "step"})
    assert math.hypot(b.x - 50, b.z - 50) > 7.0 - C.CREATURE_RADIUS
    assert b.pending.get("touch") == "solid"


# ------------------------------------------------------------------ energy, eating, regrowth


def test_energy_bookkeeping_for_rest_step_look_and_eat():
    w = flat_world()
    b = w.new_body(0, 1)
    b.x, b.z, b.heading = 30.0, 30.0, 0.0
    e = b.energy
    w.apply(b, {"do": "rest"})
    assert b.energy == pytest.approx(e - C.TICK_COST)
    e = b.energy
    w.apply(b, {"do": "step"})
    assert b.energy == pytest.approx(e - C.TICK_COST - C.STEP_COST)     # flat ground: no climb
    e = b.energy
    w.apply(b, {"do": "look", "ref": -1})
    assert b.energy == pytest.approx(e - C.TICK_COST - C.LOOK_COST)
    obj = next(iter(w.ecology.alive()))
    place(w, obj, b.x + 1.0, b.z)
    obj.nature = "poison"
    e = b.energy
    w.apply(b, {"do": "eat", "ref": obj.ident})
    assert b.energy == pytest.approx(e - C.TICK_COST + C.POISON_LOSS)
    assert b.pending["ate"]["delta"] == C.POISON_LOSS


def test_eating_needs_to_be_close_and_energy_is_capped_and_death_at_zero():
    w = flat_world()
    b = w.new_body(0, 1)
    b.x, b.z = 30.0, 30.0
    obj = next(iter(w.ecology.alive()))
    place(w, obj, 35.0, 30.0)
    w.apply(b, {"do": "eat", "ref": obj.ident})
    assert obj.alive and b.pending.get("failed") == "eat"
    place(w, obj, 31.0, 30.0)
    obj.nature = "nourish"
    b.energy = C.ENERGY_MAX - 1
    w.apply(b, {"do": "eat", "ref": obj.ident})
    assert b.energy == C.ENERGY_MAX
    b.energy = 0.03
    w.apply(b, {"do": "rest"})
    assert not b.alive and b.energy == 0


def test_eaten_objects_regrow_at_the_same_spot_as_a_fresh_draw():
    w = flat_world()
    obj = next(iter(w.ecology.alive()))
    spot = (obj.x, obj.z)
    w.ecology.eat(obj.ident, tick=0)
    assert not obj.alive
    grown = w.ecology.regrow(C.REGROW_TICKS_HI + 1)
    new = [o for o in grown if o.spot == obj.spot]
    assert len(new) == 1 and new[0].alive and (new[0].x, new[0].z) == spot
    assert new[0].ident != obj.ident and new[0].kind is obj.kind


def test_context_fruit_feeds_in_one_region_and_poisons_in_another():
    w = World(11)
    ctx = next(k for k in w.ecology.kinds if k.role == "context")
    assert sorted(ctx.natures.values()) == ["nourish", "poison"]
    for o in w.ecology.objects.values():
        if o.kind is ctx:
            assert o.nature == ctx.natures[o.region]


# ------------------------------------------------------------------ the senses


def test_view_cone_range_and_angle():
    w = flat_world()
    b = w.new_body(0, 1)
    b.x, b.z, b.heading = 60.0, 60.0, 0.0
    objs = list(w.ecology.alive())
    for o in objs:
        place(w, o, 5.0, 5.0)                                           # far away
    ahead, behind, far, side = objs[:4]
    place(w, ahead, 70.0, 60.0)
    place(w, behind, 50.0, 60.0)
    place(w, far, 60.0 + C.VIEW_RANGE + 2, 60.0)
    place(w, side, 60.0, 70.0)                                          # 90 degrees off the heading
    seen = {s["ref"] for s in B.blurry_view(b, w)}
    assert ahead.ident in seen
    assert behind.ident not in seen and far.ident not in seen and side.ident not in seen


def test_hills_block_the_view():
    w = flat_world()
    b = w.new_body(0, 1)
    b.x, b.z, b.heading = 60.0, 60.0, 0.0
    obj = next(iter(w.ecology.alive()))
    place(w, obj, 70.0, 60.0)
    assert obj.ident in {s["ref"] for s in B.blurry_view(b, w)}
    w.terrain.height[55:66, 64:67] = 9.0                               # a ridge between them
    obj.y = w.terrain.height_at(obj.x, obj.z)
    assert obj.ident not in {s["ref"] for s in B.blurry_view(b, w)}


def test_blurry_view_gives_six_traits_sharp_look_eighteen_and_taste_only_by_eating():
    w = flat_world()
    b = w.new_body(0, 1)
    b.x, b.z, b.heading = 60.0, 60.0, 0.0
    obj = next(iter(w.ecology.alive()))
    place(w, obj, 61.0, 60.0)                                           # within eating range
    p = B.percept(b, w, 0)
    s = next(s for s in p["seen"] if s["ref"] == obj.ident)
    assert len(s["traits"]) == 6 and p["ate"] is None and p["sharp"] is None
    assert set(p) == {"tick", "energy", "x", "z", "heading", "seen", "touch", "sharp", "ate", "failed"}
    assert set(s) == {"ref", "dist", "bearing", "x", "z", "traits"}
    w.apply(b, {"do": "look", "ref": obj.ident})
    p = B.percept(b, w, 1)
    assert len(p["sharp"]["traits"]) == 18 and p["ate"] is None
    w.apply(b, {"do": "eat", "ref": obj.ident})
    p = B.percept(b, w, 2)
    assert len(p["ate"]["taste"]) == 4 and set(p["ate"]) == {"ref", "delta", "energy_after", "taste"}
    assert all(isinstance(v, float) for v in p["ate"]["taste"])


def test_blurry_noise_grows_with_distance():
    w = flat_world()
    b = w.new_body(0, 1)
    b.x, b.z, b.heading = 30.0, 60.0, 0.0
    near, far = list(w.ecology.alive())[:2]
    errs = {"near": [], "far": []}
    for _ in range(200):
        place(w, near, 32.0, 60.0)
        place(w, far, 50.0, 60.0)
        for s in B.blurry_view(b, w):
            o = near if s["ref"] == near.ident else far if s["ref"] == far.ident else None
            if o is not None:
                errs["near" if o is near else "far"].append(np.mean(np.abs(np.array(s["traits"]) - o.values[:6])))
    assert np.mean(errs["far"]) > 2 * np.mean(errs["near"])


# ------------------------------------------------------------------ the mind never sees hidden truth

FORBIDDEN_TYPES = (LifeObject, LifeKind, World, B.Body)


def _walk(obj, seen, path, out):
    if id(obj) in seen or len(out) > 0:
        return
    seen.add(id(obj))
    from world.kinds import Kind as WorldKind
    if isinstance(obj, FORBIDDEN_TYPES + (WorldKind,)):
        out.append(path)
        return
    if isinstance(obj, (str, bytes, int, float, bool, type(None), np.ndarray, np.generic)):
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk(k, seen, path + "[key]", out)
            _walk(v, seen, f"{path}[{k!r}]", out)
        return
    if isinstance(obj, (list, tuple, set, frozenset)):
        for i, v in enumerate(obj):
            _walk(v, seen, f"{path}[{i}]", out)
        return
    if isinstance(obj, np.random.Generator):
        return
    if hasattr(obj, "__dict__"):
        for k, v in vars(obj).items():
            _walk(v, seen, f"{path}.{k}", out)


@pytest.mark.parametrize("name", MINDS)
def test_the_mind_holds_no_world_object_after_living(name):
    s = Session(21, [name])
    for _ in range(600):
        s.step()
    found = []
    _walk(s.creatures[0].mind, set(), name, found)
    assert not found, f"the mind can reach a world-side object at {found}"


@pytest.mark.parametrize("name", MINDS)
def test_hidden_natures_do_not_change_what_the_mind_does_before_it_eats(name):
    """Swap every object's hidden nature and kind label: until the first eat, every action must be the same."""
    def actions(swap):
        s = Session(33, [name])
        if swap:
            for o in s.world.ecology.objects.values():
                o.nature = {"nourish": "poison", "poison": "nourish", "nothing": "nothing"}[o.nature]
        out = []
        c = s.creatures[0]
        while s.tick < 3000 and c.body.alive:
            s.step()
            out.append(json.dumps(c.body.last_action, sort_keys=True))
            if c.body.last_action.get("do") == "eat" and c.rec.eats:
                break
        return out
    assert actions(False) == actions(True)


def test_mind_modules_import_nothing_world_side():
    allowed = {"numpy", "math", "mind", "life.config", "life.minds", "life.sim",
               "json", "os", "pathlib", "time", "urllib"}                   # the last five: the LLM creature's plumbing
    for path in (ROOT / "life" / "minds").glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""] if node.module not in ("life", "mind") else \
                    [f"{node.module}.{a.name}" for a in node.names]
            for n in names:
                assert any(n == a or n.startswith(a + ".") for a in allowed), f"{path.name} imports {n}"
                assert not n.startswith(("life.world3d", "life.ecology", "life.terrain", "life.obstacles", "world")), n


def test_no_route_finder_in_any_mind():
    """No code in a mind is named like a path-finder or imports one (docstrings may say there is none)."""
    words = ("astar", "a_star", "dijkstra", "heapq", "navmesh", "flow_field", "breadth_first", "bfs", "pathfind",
             "shortest_path", "networkx", "scipy")
    for path in (ROOT / "life" / "minds").glob("*.py"):
        names = set()
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                names.add(node.attr)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                names.add(node.name)
            elif isinstance(node, ast.Import):
                names.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add(node.module or "")
        for n in names:
            assert not any(w in n.lower() for w in words), f"{path.name} has {n}"


# ------------------------------------------------------------------ batch measures


def test_settled_after_counts_eats_until_poison_share_stays_low():
    from life.batch import settled_after
    assert settled_after(list("pp" + "f" * 20)) == 2
    assert settled_after(list("f" * 20)) == 0
    assert settled_after(list("fpfpfpfp")) is None


def test_every_creature_lives_and_reports_its_measures():
    for name in MINDS:
        r = Session(4, [name]).run(400)[0]
        assert r["lifespan"] >= 1 and r["eats"] == r["food"] + r["poison"] + r["nothing"]
        assert len(r["windows"]) == math.ceil(r["lifespan"] / C.WINDOW_TICKS)


# ------------------------------------------------------------------ the page's server


def test_the_server_starts_and_serves_the_page_and_the_world(tmp_path):
    from life import lab
    lab.setup_logging(tmp_path)
    lab.LIVE = lab.Live(seed=7, creatures=("wanderer",))
    lab.LIVE.playing = False
    server = lab.serve(port=18770)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        page = urllib.request.urlopen(base + "/").read().decode()
        assert "Frankie's World" in page and "three.module.min.js" in page
        assert urllib.request.urlopen(base + "/vendor/three-0.170.0/three.module.min.js").status == 200
        world = json.loads(urllib.request.urlopen(base + "/api/world").read())
        assert world["seed"] == 7 and len(world["height"]) == C.GRID * C.GRID
        req = urllib.request.Request(base + "/api/control", data=json.dumps({"cmd": "step", "n": 5}).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        assert json.loads(urllib.request.urlopen(req).read())["playing"] is False
        state = json.loads(urllib.request.urlopen(base + "/api/state?objects=-1").read())
        assert state["tick"] == 5 and state["objects"] and state["creatures"][0]["name"] == "wanderer"
        assert "nature" not in json.dumps(state["objects"])        # the page draws looks, never natures
        log = urllib.request.Request(base + "/api/log", data=b'{"level":"info","msg":"test"}',
                                     headers={"Content-Type": "application/json"}, method="POST")
        assert json.loads(urllib.request.urlopen(log).read())["ok"]
    finally:
        server.shutdown()
        server.server_close()
    assert "new world seed=7" in (tmp_path / "server.log").read_text()


# ------------------------------------------------------------------ the LLM creature (later, optional; fake LLM only)

FORBIDDEN_WORDS = ("apple", "poison", "nourish", "fruit", "food", "forest", "meadow", "marsh", "rocky", "look-alike",
                   "lookalike", "neutral", "context", "region", "fence", "river", "wall", " red", "green", "blue")


def _llm_session(tmp_path, seed=8, ticks=500):
    from life import sim
    from life.minds import llm
    s = Session(seed, ["wanderer"])                      # a real world; swap in the LLM creature's mind
    c = s.creatures[0]
    c.mind = llm.LLMCreature(seed, c.reserve, c.boldness, llm=llm.FakeLLM(), log_path=tmp_path / "run.jsonl")
    c.name = "llm"
    for _ in range(ticks):
        if not c.body.alive:
            break
        s.step()
    return s, c


def test_llm_creature_runs_on_the_fake_and_saves_every_call(tmp_path):
    s, c = _llm_session(tmp_path)
    cost = c.mind.cost()
    calls = [json.loads(l) for l in (tmp_path / "run.jsonl").read_text().splitlines()]
    assert cost["calls"] == len(calls) > 0 and cost["model"] == "fake"
    assert any(json.loads(x["answer"]["text"])["do"] == "approach" for x in calls)


def test_llm_prompts_hold_only_neutral_numbers(tmp_path):
    _llm_session(tmp_path)
    for line in (tmp_path / "run.jsonl").read_text().splitlines():
        prompt = json.loads(line)["prompt"].lower()
        for w in FORBIDDEN_WORDS:
            assert w not in prompt, f"the LLM was told {w!r}"
    from life.minds.llm import SYSTEM
    for w in FORBIDDEN_WORDS:
        assert w not in SYSTEM.lower()


def test_a_saved_llm_run_replays_identically_without_calling_anyone(tmp_path):
    from life.minds import llm
    s1, c1 = _llm_session(tmp_path, seed=9, ticks=400)
    s2 = Session(9, ["wanderer"])
    c2 = s2.creatures[0]
    c2.mind = llm.LLMCreature(9, c2.reserve, c2.boldness, llm=llm.ReplayLLM(tmp_path / "run.jsonl"))
    for _ in range(400):
        if not c2.body.alive:
            break
        s2.step()
    assert (c2.body.x, c2.body.z, c2.body.energy) == (c1.body.x, c1.body.z, c1.body.energy)


def test_llm_request_is_built_from_the_environment_and_parsed(monkeypatch):
    from life.minds import llm
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("FRANKIE_LLM_MODEL", "model-from-env")
    client = llm.AnthropicLLM()
    req = client.request("hello")
    body = json.loads(req.data)
    assert req.full_url == llm.API_URL and req.get_header("X-api-key") == "test-key"
    assert req.get_header("Anthropic-version") == llm.API_VERSION and body["model"] == "model-from-env"

    class Fake:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return json.dumps({"content": [{"type": "thinking", "thinking": ""},
                                           {"type": "text", "text": '{"do": "rest"}'}],
                               "stop_reason": "end_turn", "usage": {"input_tokens": 10, "output_tokens": 3}}).encode()

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=None: Fake())
    ans = client("hello")
    assert ans["text"] == '{"do": "rest"}' and ans["input_tokens"] == 10 and llm.parse(ans["text"]) == {"do": "rest"}


def test_llm_creature_is_unavailable_without_a_key(monkeypatch):
    from life.minds import llm
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("FRANKIE_LLM_FAKE", raising=False)
    assert not llm.available()
    with pytest.raises(llm.LLMError):
        llm.AnthropicLLM()
    from life import sim
    sim._load_minds()
    assert not sim.CREATURES["llm"]["available"]()
