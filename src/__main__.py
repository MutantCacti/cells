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
from single_cell_input import KeyInput


SAMPLE_RATE = 60 # Hz
CHAR_ONE = '█'#'1'
CHAR_ZERO = '░'#'0'


def stop(signum, frame):
    sys.exit(0)


def main():
    rng = random.Random(42)
    graph = Graph(16, rng)
    key_down = KeyInput(graph, 0)

    sys.stdout.write('\033[?1049h') # alternate screen buffer
    last = ''
    try:
        while True:
            key_down.write()
            graph.update()
            #last = '\n'.join([str(cell.value) for cell in graph.cells])
            #last = ''.join('█' if c.value == -1 else '·' for c in graph.cells)
            last = '\n'.join(''.join(CHAR_ONE if c.value & (1<<b) else CHAR_ZERO for b in range(DATA_WIDTH - 1, -1, -1)) for c in graph.cells)
            sys.stdout.write('\033[H' + last)
            sys.stdout.flush()
            time.sleep(1 / SAMPLE_RATE)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write('\033[?1049l')
        print(last)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, stop)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, stop)
    main()
