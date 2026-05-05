"""
src/main.py
Entry point.

Created: 2026-05-01
 Author: Maxence Morel Dierckx
"""
import sys
import signal
import random
from cells import Graph, DATA_WIDTH
from cellinput import KeyInput
from harness import SwitchHarness
from evolver import SwitchEvolver


NUM_CELLS = 16
SAMPLE_RATE = 12 # Hz
CHAR_ONE = '█'#'1'
CHAR_ZERO = '░'#'0'


def stop(signum, frame):
    sys.exit(0)


def main():
    rng = random.Random(42)
    graph = Graph(NUM_CELLS, rng)
    evolver = SwitchEvolver(graph, rng)
    key_down = KeyInput(graph, 0)
    harness = SwitchHarness(graph, evolver, key_down, NUM_CELLS - 1, "switch", SAMPLE_RATE)
    harness.run()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, stop)
    main()
