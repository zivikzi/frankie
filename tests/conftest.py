import sys
from pathlib import Path

# Lets the tests import philox_reference.py from this folder.
sys.path.insert(0, str(Path(__file__).parent))
