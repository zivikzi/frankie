"""Every creature the page and the batch can run, with its colour on screen."""

from life.minds.wanderer import Wanderer
from life.sim import register

register("wanderer", "Wanderer", lambda seed, reserve, boldness: Wanderer(seed, reserve, boldness), "#b9b9b9")
