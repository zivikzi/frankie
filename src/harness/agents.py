"""The frozen agent registry: who runs, where, and what each pays (section 4, KT-46, KT-93).

The harness charges every cost from this registry, never from a mind's own
description of itself. Each entry fixes:

- agent_type, from the glossary's list (a bare "B1n" is not allowed, X03);
- its class: "bot" (chooses by a baseline rule, never reads energy), "drive"
  (B1n-mind: Frankie's drive over a nearest-item memory) or "tower" (K-F, its
  off-switch versions and its twins);
- where it runs: frozen bench code in the harness's process, or a mind package
  in a process of its own (host.py);
- whether it pays the sharp look (B13) and what its thinking costs (B14,
  KT-27), in nano-units per check or spike (KT-92);
- whether it tastes the warm-up (K-F-NOWARM does not);
- its version record (KT-49, FORBIDDEN 26): every user of the drive runs
  with habits off (OS07, lifetime); OS01 and OS10 add their own switch;
- its birth parameters. B2e alone is handed H's 4 core traits (X03).

K-F and its versions live in packages that do not exist yet (Week 3). Their
entries are fixed now, so the harness and the analysis script need no change
when they arrive: the mind package's `mind/entry.py` and the twins package's
`twins/entry.py` each provide make(config).
"""

from dataclasses import dataclass, field

from . import constants as C

OS07 = {"switch": "OS07", "setting": "habits off", "scope": "lifetime"}    # (section 5, KT-49)
# Grid of acceptance radii, in noise widths; None is "unlimited" (KT-05)
RADIUS_GRID = (2, 4, 6, 8, 12, 16, 24, None)


@dataclass(frozen=True)
class AgentSpec:
    agent_type: str
    label: str                       # unique name of this configuration in a set's run
    mind_class: str                  # "bot" | "drive" | "tower"
    entry: str                       # "module:factory" in-process, or a package name ("mind", "twins")
    host: str                        # "in-process" | "subprocess"
    pays_look: bool
    thinking_unit: str               # "none" | "check" | "spike"
    unit_nano: int | None = None     # nano-units per check or spike; spikes take KT-27 from the tuned values
    unit_row: str = ""               # the row the unit cost comes from
    warmup: bool = True
    version: tuple = ()
    params: dict = field(default_factory=dict)
    oracle_core: bool = False        # B2e only: is handed H's core traits (X03)
    test_only: bool = False          # the stub and its variants; never run on a set
    after: str = ""                  # label of the configuration that must run first on each run key (KT-67)

    def __post_init__(self):
        if self.mind_class not in ("bot", "drive", "tower"):
            raise ValueError(f"unknown mind class {self.mind_class}")
        if self.mind_class == "bot" and (self.pays_look or self.thinking_unit != "none"):
            raise ValueError("bots pay nothing (KT-46)")
        if self.mind_class != "bot" and not self.pays_look:
            raise ValueError("every tower mind and B1n-mind pay the sharp look (KT-46)")
        if self.oracle_core and self.agent_type != "B2e":
            raise ValueError("only B2e is handed H's core traits (X03)")


def radius_label(r) -> str:
    return "unlimited" if r is None else str(r)


def _bot(agent_type, cls, label=None, **params):
    return AgentSpec(agent_type=agent_type, label=label or agent_type, mind_class="bot",
                     entry=f"baselines.bots:{cls}", host="in-process", pays_look=False,
                     thinking_unit="none", params=params, oracle_core=(agent_type == "B2e"))


def b1n_bot_r(r):
    return _bot("B1n-bot-r", "B1nBotR", f"B1n-bot-r(r={radius_label(r)})", radius=r)


def g16(r):
    return _bot("G16", "G16", f"G16(r={radius_label(r)})", radius=r)


def g18(r):
    return _bot("G18", "G18", f"G18(r={radius_label(r)})", radius=r)


def b1n_mind(r):
    return AgentSpec(agent_type="B1n-mind", label=f"B1n-mind(r={radius_label(r)})", mind_class="drive",
                     entry="baselines.b1n_mind:B1nMind", host="in-process", pays_look=True,
                     thinking_unit="check", unit_nano=C.CHECK_NANO, unit_row="B14, KT-45, KT-46",
                     version=(OS07,), params={"radius": r})


# The bots whose choices need no radius (section 4).
PLAIN_BOTS = {
    "B1n-bot": "B1nBot", "B1t": "B1t", "B2": "B2", "B2e": "B2e", "G01": "G01", "G04": "G04",
    "G05": "G05", "G06": "G06", "G07": "G07", "G08": "G08", "G09": "G09", "G17": "G17",
}

# Rule 6's must-fail list (section 9) and the bots that are only reported.
MUST_FAIL = ("B1t", "B2", "G01", "G04", "G05", "G06", "G07", "G09", "G16", "G17", "G18")
REPORTED_BOTS = ("B1n-bot", "G08")


def plain_bot(agent_type):
    return _bot(agent_type, PLAIN_BOTS[agent_type])


# The radii chosen on the tuning set and registered before any K-F code (section 4, KT-101):
# each maximises its mind's mean D_learn (D_beh) on the 30 tuning families; equal means go to the smaller radius.
RADIUS_B1N_BOT_R = None      # unlimited: 0.2445, against 0.2435 at 24 (KT-101)
RADIUS_B1N_MIND = 24         # 0.2430, against 0.2403 unlimited (KT-101)
RADIUS_G16 = 24              # 0.0634, equal to unlimited, so the smaller (KT-101); G18 uses it too


def bench_minds():
    """The registered non-tower minds, in the order they run on every set (section 3)."""
    return non_tower_minds(RADIUS_B1N_BOT_R, RADIUS_B1N_MIND, RADIUS_G16)


def non_tower_minds(r_bot, r_mind, r16):
    """Every mind that runs before any tower mind on a set (section 3), with the registered radii."""
    out = [plain_bot(t) for t in ("B1n-bot", "B1t", "B2", "B2e", "G01", "G04", "G05", "G06", "G07",
                                  "G08", "G09", "G17")]
    return [b1n_bot_r(r_bot), b1n_mind(r_mind)] + out + [g16(r16), g18(r16)]


def _tower(agent_type, label, package, unit, unit_nano, unit_row, version, warmup=True, params=None,
           after=""):
    return AgentSpec(agent_type=agent_type, label=label, mind_class="tower", entry=package,
                     host="subprocess", pays_look=True, thinking_unit=unit, unit_nano=unit_nano,
                     unit_row=unit_row, warmup=warmup, version=version, params=params or {},
                     after=after)


def tower_minds(spike_nano):
    """K-F and the minds built from its code (sections 4 and 7). spike_nano is KT-27, set in Week 4."""
    spike = ("spike", spike_nano, "KT-27, KT-46")
    check = ("check", C.CHECK_NANO, "B14, KT-45, KT-46")
    return [
        _tower("K-F", "K-F", "mind", *spike, (OS07,)),
        _tower("K-F", "OS01-cap", "mind", *check,
               (OS07, {"switch": "OS01", "setting": "cap", "scope": "lifetime"}),
               params={"OS01": "cap"}, after="K-F"),
        _tower("K-F", "OS01-free", "mind", "none", 0, "KT-46",
               (OS07, {"switch": "OS01", "setting": "free", "scope": "lifetime"}),
               params={"OS01": "free"}),
        _tower("K-F", "OS10", "mind", *spike, (OS07, {"switch": "OS10", "setting": None, "scope": "lifetime"}),
               params={"OS10": True}),
        _tower("K-F-NOWARM", "K-F-NOWARM", "mind", *spike, (OS07,), warmup=False),
        _tower("TW2", "TW2", "twins", *spike, (OS07,), params={"twin": "TW2"}),
        _tower("TW7", "TW7", "twins", *check, (OS07,), params={"twin": "TW7"}),
    ]
