"""K-F's constants. Each is one number, shared by every trait and every layer (section 7, FORBIDDEN 28).

Every line cites the row its number comes from. The tuned numbers (KT-19 to
KT-27) hold the start values Aitzaz agreed for tuning on 1 Nov 2026. Only
the logged search in Week 4 may change them, and until then every run uses
these start values.
"""

# ------------------------------------------------------------------ the trait schema (KT-01)

N_TRAITS = 22                # traits per object, in schema order (KT-01)
N_VISIBLE = 18               # context, object, parts and details; taste comes only after an eat (KT-01, FORBIDDEN 29)
OBJECT_FROM = 2              # context is traits 0 and 1, scene and host (KT-01)
PARTS_FROM = 6               # the object layer is traits 2 to 5 (KT-01)
DETAILS_FROM = 11            # the parts layer is traits 6 to 10 (KT-01)
TASTE_FROM = 18              # visible details are traits 11 to 17, taste is 18 to 21 (KT-01, KT-55)
NOISE_WIDTH = 0.01           # one noise width, as a share of each trait's 0-to-1 range (PLACEHOLDER-45, KT-34)

# ------------------------------------------------------------------ detectors (M18, KT-53)

DETECTORS = 16               # detectors per trait (M18, KT-53)
DETECTOR_OFFSET = 0.5        # detector k is centred at (k + 0.5)/16 of the range (KT-53)

# ------------------------------------------------------------------ the time base and settling (section 6)

SUBSTEPS = 10                # 1 ms substeps per settling step (KT-09)
TRACE_MS = 10                # the activation trace's smoothing time constant, in ms (KT-09, KT-62)
TRACE_DECAY = 0.9048374180359595   # e^(-1/10): the trace's decay per substep, written out so every machine uses the same double (KT-62, I05)
CONTEXT_STEP = 1             # the step each layer switches on at (KT-51)
OBJECT_STEP = 2              # (KT-51)
PARTS_STEP = 3               # (KT-51)
DETAILS_STEP = 4             # (KT-51); elimination runs at the ends of the steps before this one (KT-52)
WIN_STEPS = 2                # a win needs a lead by the margin at steps s - 1 and s (PLACEHOLDER-12, KT-10)
HOLD_STEPS = 4               # a win settles if the winner stays the leader through step s + 4 (KT-10, KT-63)
LAST_WIN_STEP = 30           # no winner by step 30: the step-30 rule (KT-10, X29, KT-64)
OBJECTION_STEPS = 2          # a mismatch must hold at the ends of 2 steps in a row to object (M08, KT-56)
RESETS = 2                   # the 1st and 2nd objection reset the race; later ones remove the leader (PLACEHOLDER-13, KT-57)
ATTENTION_TRAITS = 3         # traits parts and details each check (PLACEHOLDER-14, KT-54)
GROUP_NEURONS = 8            # neurons per candidate group, spiking only (D12, section 6, KT-61)
SHARE_STEP = 2               # neuron k of a group gets (2k + 1)/8 of the group's input (KT-61)

# ------------------------------------------------------------------ memory (section 6, PLACEHOLDER-02 to -08)

SLOTS = 48                   # kinds memory holds, plus "unknown" (PLACEHOLDER-08)
TENTHS = 10                  # weights are kept in whole tenths (PLACEHOLDER-02, KT-94)
WEIGHT_START = 5             # every weight starts at 0.5 (M20, KT-10, section 6)
WEIGHT_UP = 2                # +0.2 on a blamed layer's differing traits (PLACEHOLDER-02, KT-72)
WEIGHT_DOWN = 1              # -0.1 on a trait that varied in a right guess (PLACEHOLDER-02, M14, KT-71)
TWENTIETHS = 20              # reliability is kept in whole twentieths, 0 to 20 (PLACEHOLDER-05)
RELIABILITY_UP = 1           # +0.05 per right guess (PLACEHOLDER-05)
RELIABILITY_DOWN = 5         # -0.25 per unexplained mistake (PLACEHOLDER-05, M13)

# ------------------------------------------------------------------ the drive (section 5, KT-08, KT-44 to KT-50)

BAR_TOP = 0.9                # the bar is 0.9 - 0.3 x b (PLACEHOLDER-27, KT-08)
BAR_SLOPE = 0.3              # (PLACEHOLDER-27, KT-08)
WRONG_FACTOR_TOP = 2.0       # the chance of being wrong is multiplied by (2 - reliability) (PLACEHOLDER-05)
NANO_PER_MILLI = 1_000_000   # costs are whole nano-units, energy whole milli-units (KT-92)
MILLI_PER_UNIT = 1000        # one unit of energy (KT-92)
HALF_MILLI_NANO = 500_000    # half a milli-unit: a cost rounds halves up (KT-48, KT-92)
CHECK_NANO = 1_000_000       # one check costs 0.001 (B14, KT-45, KT-46, KT-92)

# ------------------------------------------------------------------ the tuned list (section 7), at the agreed start values

LEAK = 0.1                   # share of charge that fades per ms (KT-19, start value)
THRESHOLD = 2.5              # charge at which a neuron fires (KT-20, start value)
REFRACTORY_MS = 2            # rest after a spike, in ms (KT-21, start value)
INHIBITION = 0.3125          # charge each spike takes off every neuron of every other group (KT-22, start value)
DETECTOR_WIDTH_NW = 4        # detector width, in noise widths (KT-23, start value)
COMMIT_MARGIN = 2            # the lead a winner needs, in activation (KT-24, start value)
OBJECTION_THRESHOLD = 0.5    # mismatch, in weight, at which a layer objects (KT-25, start value)
NEW_KIND_THRESHOLD = 0.5     # "unknown"'s steady input (KT-26, start value)
SPIKE_NANO = None            # per-spike cost, in nano-units: set by KT-47's rule after the search (KT-27, KT-92)

OS07 = {"switch": "OS07", "setting": "habits off", "scope": "lifetime"}     # every bench run (section 5, KT-49)


class Settings:
    """The tuned numbers one tower runs with (KT-19 to KT-26).

    Every run uses the values above. Tests may make other settings to check
    the logic on hand-made cases, and the logged search of section 7 hands
    each setting it tries to the mind as its own settings at birth (KT-97,
    KT-126); nothing else may change them.
    """

    def __init__(self, leak=LEAK, threshold=THRESHOLD, refractory_ms=REFRACTORY_MS, inhibition=INHIBITION,
                 detector_width_nw=DETECTOR_WIDTH_NW, commit_margin=COMMIT_MARGIN,
                 objection_threshold=OBJECTION_THRESHOLD, new_kind_threshold=NEW_KIND_THRESHOLD):
        self.leak = leak
        self.threshold = threshold
        self.refractory_ms = refractory_ms
        self.inhibition = inhibition
        self.detector_width_nw = detector_width_nw
        self.detector_width = detector_width_nw * NOISE_WIDTH        # as a share of range (KT-23)
        self.commit_margin = commit_margin
        self.objection_threshold = objection_threshold
        self.new_kind_threshold = new_kind_threshold

    @classmethod
    def from_params(cls, given):
        """A setting the logged search tries, from the mind's birth parameters (KT-126).

        Only the closed list's own names are taken, each as one number; any
        other name stops the mind, so nothing outside the list can be set.
        """
        if not isinstance(given, dict) or not set(given) <= set(TUNED_NAMES):
            raise ValueError(f"a setting may name only the closed list: {sorted(TUNED_NAMES)} (section 7)")
        for name, value in given.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{name} must be one number (section 7)")
        return cls(**given)

    def table(self):
        """The constants table info() reports: [value, row] (FORBIDDEN 28)."""
        return {"leak": [self.leak, "KT-19"], "threshold": [self.threshold, "KT-20"],
                "refractory_ms": [self.refractory_ms, "KT-21"], "inhibition": [self.inhibition, "KT-22"],
                "detector_width_nw": [self.detector_width_nw, "KT-23"],
                "commit_margin": [self.commit_margin, "KT-24"],
                "objection_threshold": [self.objection_threshold, "KT-25"],
                "new_kind_threshold": [self.new_kind_threshold, "KT-26"]}


# The closed list's own names, in KT-19 to KT-26's order (section 7)
TUNED_NAMES = ("leak", "threshold", "refractory_ms", "inhibition", "detector_width_nw", "commit_margin",
               "objection_threshold", "new_kind_threshold")
