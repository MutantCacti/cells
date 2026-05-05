"""
src/graph.py
A graph of Turing-complete cells with mutable programs.
Cells converge graph input to transform data and diverge that data as output into other cells.

Created: 2026-05-01
 Author: Maxence Morel Dierckx
"""
import random
from collections import defaultdict


DATA_WIDTH = 64 # torch.int64


# Everything is a tree
type Tree = int | tuple[Tree, Tree]


def count_leaves(tree: Tree) -> int:
    if isinstance(tree, int):
        return 1
    left, right = tree
    return count_leaves(left) + count_leaves(right)




class Cell:
    def __init__(self, converge: Tree, diverge: Tree, value: int = 0):
        self.C: Tree = converge  # leaves are upstream cell indices
        self.D: Tree = diverge    # leaves are downstream cell indices
        self.value: int = value


    # TODO: compile to post-order tensor schedule for ~size speedup
    def converge(self, cells: list['Cell']) -> int:
        """Converge by NAND folding upstream cell values into a new value"""
        def nand(tree: Tree) -> int:
            if isinstance(tree, int):
                value = cells[abs(tree) - 1].value
                # Negative indices are "inhibited" by bitwise NOT
                return ~value if tree < 0 else value
            left, right = tree
            return ~(nand(left) & nand(right))
        return nand(self.C)


    # TODO: compile to post-order tensor schedule for ~size speedup
    def diverge(self, rng: random.Random) -> list[int]:
        """Diverge by bit pachinko on self.value through tree to target cell indices"""
        def distribute(signal: int, tree: Tree, targets: list[int], rng: random.Random) -> list[int]:
            if signal == 0:
                return targets
            if isinstance(tree, int):
                return targets + [tree]
            left, right = tree
            mask = rng.getrandbits(DATA_WIDTH)
            targets = distribute(signal & mask,  left,  targets, rng)
            targets = distribute(signal & ~mask, right, targets, rng)
            return targets
        return distribute(self.value, self.D, [], rng)


    def replace_C(self, tree: Tree):
        self.C = tree


    def replace_D(self, tree: Tree):
        self.D = tree


    @property
    def Cc(self) -> int:
        return count_leaves(self.C)


    @property
    def Dc(self) -> int:
        return count_leaves(self.D)




class Graph:
    def __init__(self, size: int, rng: random.Random):
        self.rng = rng
        self.cells: list[Cell] = [
            Cell(
                converge=(i + 1, (i % size) + 1),
                diverge=(i + 1, (i % size) + 1),
                value=rng.getrandbits(DATA_WIDTH),
            )
            for i in range(size)
        ]
        self.next_indices: set[int] = set(range(size))


    def update(self) -> 'Graph':
        # Collect activations from all cells over their converging inputs
        active = sorted(self.next_indices)
        activations = [self.cells[i].converge(self.cells) for i in active]

        # Write snapshots back to cells (simultaneous displacement)
        for i, value in zip(active, activations):
            self.cells[i].value = value

        # Collect cell divergence routing data based on new value for next update
        # Negatively signed indices correspond to inhibitory signals;
        # signal is tallied across cells, only cells >0 are active next update
        tally: dict[int, int] = defaultdict(int)
        for i in active:
            for signed in self.cells[i].diverge(self.rng):
                tally[abs(signed) - 1] += 1 if signed > 0 else -1 # strictly GT; excitation has to win
        self.next_indices = {k for k, v in tally.items() if v > 0} # +1 offset 
        return self
