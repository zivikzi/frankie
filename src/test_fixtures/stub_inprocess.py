"""The stub mind loaded in this process, for fast harness tests (the kill test always uses its own process)."""

import importlib.util

from .stub import STUB_DIR

_spec = importlib.util.spec_from_file_location("test_fixtures._stub_entry", STUB_DIR / "entry.py")
_entry = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_entry)
make = _entry.make
