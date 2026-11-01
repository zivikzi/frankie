"""K-F's entry point: make(config) (B21, KT-93).

K-F runs on spiking units (D12), which are Week 4's work. Until they exist,
make() refuses, so nothing can run K-F by mistake on TW7's rate units. The
tower, the memory rule and the drive it will use are in this package now
(mind.tower, mind.memory, mind.drive and mind.interface).
"""


def make(config):
    raise ValueError("K-F's spiking units are built in Week 4; until then only TW7 (twins package) can run")
