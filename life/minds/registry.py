"""Every creature the page and the batch can run, with its colour on screen."""

from life.minds.frankie import Frankie, FrankieNoContext, FrankieNoMerge
from life.minds.trial import TrialAndError
from life.minds import llm
from life.minds.wanderer import Wanderer
from life.sim import register

register("frankie", "Frankie", lambda seed, r, b: Frankie(seed, r, b), "#f08a24")
register("trial", "Trial and error", lambda seed, r, b: TrialAndError(seed, r, b), "#3fa7e0")
register("wanderer", "Wanderer", lambda seed, r, b: Wanderer(seed, r, b), "#b9b9b9")
register("frankie-no-merge", "Frankie, no merging", lambda seed, r, b: FrankieNoMerge(seed, r, b), "#c05fd0")
register("frankie-no-context", "Frankie, no context", lambda seed, r, b: FrankieNoContext(seed, r, b), "#e6cf3a")


def _llm(seed, r, b):
    """The LLM creature (later, optional): needs ANTHROPIC_API_KEY and FRANKIE_LLM_MODEL; FRANKIE_LLM_FAKE=1 uses the
    scripted fake. Every call is saved under life/results/llm-runs/ for replay."""
    import os
    import pathlib
    import time
    fake = os.environ.get("FRANKIE_LLM_FAKE") == "1"
    client = llm.FakeLLM() if fake else llm.AnthropicLLM()
    runs = pathlib.Path(__file__).resolve().parents[1] / "results" / "llm-runs"
    tag = "fake" if fake else "real"
    path = runs / f"{tag}-{seed}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.jsonl"
    return llm.LLMCreature(seed, r, b, llm=client, log_path=path)


register("llm", "LLM creature", _llm, "#2fd3b5",
         available=lambda: llm.available() or __import__("os").environ.get("FRANKIE_LLM_FAKE") == "1")
