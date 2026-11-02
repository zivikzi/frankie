"""Frankie Lab's E1: since the sealed-test job, E1 lives in the mind package (src/mind/e1.py).

This module keeps the Lab's names. Every Lab run of E1 runs mind.e1's code,
the same code the sandboxed process runs for the kill test. Exploration
settings are passed as birth parameters (the names in mind.e1.NUMBERS and
mind.e1.SWITCHES); with none, E1 runs as frozen (KT-132).
"""

from mind import e1 as frozen

Settings = frozen.Settings
look = frozen.look
version_of = frozen.version_of


def make(config):
    return frozen.make(config)
