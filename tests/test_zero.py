"""
tests/test_zero.py
Test the absorbing zero state of the graph.

Starting with all cells at value 0, the graph oscillates 0 -> -1 -> 0 over two
ticks, then permanently absorbs because routing on signal=0 emits no targets,
which empties next_indices.
"""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from graph import Graph


def bits(x: int) -> int:
    """Unsigned 64-bit view of a Python int (for readable assertions)."""
    return x & ((1 << 64) - 1)


def test_zero_absorbs():
    rng = random.Random(0)
    g = Graph(size=4, rng=rng)

    # Force all-zeros initial state.
    for cell in g.cells:
        cell.value = 0

    # Tick 1: NAND(0, 0) = -1 for every cell. Routing on all-bits-set fires both leaves.
    g.update()
    assert all(bits(c.value) == 0xFFFFFFFFFFFFFFFF for c in g.cells), \
        f'after tick 1: {[hex(bits(c.value)) for c in g.cells]}'
    assert g.next_indices == {0, 1, 2, 3}, f'next: {g.next_indices}'

    # Tick 2: NAND(-1, -1) = 0 for every cell. Routing on signal=0 emits nothing.
    g.update()
    assert all(bits(c.value) == 0 for c in g.cells), \
        f'after tick 2: {[hex(bits(c.value)) for c in g.cells]}'
    assert g.next_indices == set(), f'next: {g.next_indices}'

    # Tick 3+: graph is permanently dead.
    for _ in range(5):
        g.update()
        assert all(bits(c.value) == 0 for c in g.cells)
        assert g.next_indices == set()


if __name__ == '__main__':
    test_zero_absorbs()
    print('PASSED: zero state absorbs the graph in 2 ticks')
