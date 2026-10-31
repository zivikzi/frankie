"""Drive-class minds that each break one rule of the interface, for the harness's tests (KT-93, KT-95)."""

from harness.agents import OS07


class Liar:
    """Says "unknown" and skips, except for the one rule params["break"] names."""

    def __init__(self, config):
        self.brk = config["params"]["break"]

    def decide(self, visible, energy_milli):
        tr = {"eat_chance": None, "skip_chance": 1.0, "bar": 0.8, "pick": "skip", "options_considered": [],
              "no_safe_option": False, "untried_tally": None}
        d = {"action": "skip", "verdict": "unknown", "settle_step": None,
             "thinking": {"unit": "check", "count": 3, "cost_milli": 3}, "drive": tr, "provenance": "bench"}
        if self.brk == "eat-unknown":
            d["action"] = tr["pick"] = "eat"
        elif self.brk == "cost":
            d["thinking"]["cost_milli"] = 2
        elif self.brk == "extra-field":
            d["kind"] = "apple"
        elif self.brk == "fallback-cleared":
            d["verdict"] = 0
            tr.update(eat_chance=0.95, no_safe_option=True, pick="eat",
                      options_considered=[{"order": 1, "source": "bench", "option": "eat",
                                           "predicted_p_above_R": 0.95, "cleared_bar": True},
                                          {"order": 2, "source": "bench", "option": "skip",
                                           "predicted_p_above_R": 1.0, "cleared_bar": True}])
            d["action"], d["provenance"] = "eat", "no-safe-option-fallback"
        elif self.brk == "nan":
            tr["skip_chance"] = float("nan")
        return d

    def land(self, delta, after, taste):
        return {"verdict": None, "settle_step": None}

    def write(self):
        return {"events": []}

    def dump(self):
        return {}

    def info(self):
        chooser = "maximising" if self.brk == "chooser" else "satisficing"
        return {"version": [dict(OS07)], "constants": {}, "chooser": chooser, "neuron": None}


SEEN = []


class Grabber(Liar):
    """Keeps every packet it is handed, so a test can look at them."""

    def decide(self, visible, energy_milli):
        SEEN.append(visible)
        return super().decide(visible, energy_milli)
