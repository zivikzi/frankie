"""Every creature the page and the batch can run, with its colour on screen."""

from life.minds.frankie import Frankie, FrankieNoContext, FrankieNoMerge
from life.minds.trial import TrialAndError
from life.minds.wanderer import Wanderer
from life.sim import register

register("frankie", "Frankie", lambda seed, r, b: Frankie(seed, r, b), "#f08a24")
register("trial", "Trial and error", lambda seed, r, b: TrialAndError(seed, r, b), "#3fa7e0")
register("wanderer", "Wanderer", lambda seed, r, b: Wanderer(seed, r, b), "#b9b9b9")
register("frankie-no-merge", "Frankie, no merging", lambda seed, r, b: FrankieNoMerge(seed, r, b), "#c05fd0")
register("frankie-no-context", "Frankie, no context", lambda seed, r, b: FrankieNoContext(seed, r, b), "#e6cf3a")
