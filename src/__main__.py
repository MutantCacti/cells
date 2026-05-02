"""
src/__main__.py
Temporary entry point.

Created: 2026-05-01
 Author: Maxence Morel Dierckx
"""
import sys
import time
import signal
import random
from cells import Graph, DATA_WIDTH
from cell_input import KeyInput
from harness import SwitchHarness


NUM_CELLS = 16
SAMPLE_RATE = 12 # Hz
CHAR_ONE = '█'#'1'
CHAR_ZERO = '░'#'0'


def stop(signum, frame):
    sys.exit(0)


def main():
    rng = random.Random(42)
    graph = Graph(NUM_CELLS, rng)
    key_down = KeyInput(graph, 0)
    harness = SwitchHarness(graph, key_down, NUM_CELLS - 1, "switch", SAMPLE_RATE)
    harness.run()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, stop)
    main()
