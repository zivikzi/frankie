"""The stub mind's registry entry, for tests only (section 7, step 5)."""

import pathlib

from harness.agents import OS07, AgentSpec

STUB_DIR = pathlib.Path(__file__).resolve().parent / "stub_package" / "mind"
SPIKE_NANO = 100_000          # must match the stub's own SPIKE_NANO (stub_package/mind/entry.py)


def stub_spec(variant="taste-blind", label=None, host="subprocess", **params):
    """A tower-shaped stub configuration. In-process hosting is for fast harness tests only."""
    entry = "mind" if host == "subprocess" else "test_fixtures.stub_inprocess:make"
    return AgentSpec(agent_type="stub", label=label or f"stub({variant})", mind_class="tower", entry=entry,
                     host=host, pays_look=True, thinking_unit="spike", unit_nano=SPIKE_NANO,
                     unit_row="stub fixture", version=(OS07,), params=dict(params, variant=variant),
                     test_only=True)
