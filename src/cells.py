"""
src/graph.py
A graph of Turing-complete cells with mutable programs.
Cells converge graph input to transform data and diverge that data as output into other cells.

Created: 2026-05-01
 Author: Maxence Morel Dierckx
"""
import random
from collections import defaultdict
from typing import NamedTuple


DATA_WIDTH = 64 # torch.int64


# Everything is a tree
class Leaf(NamedTuple):
    index: int       # signed cell 1-index (negative means inhibitory)
    ema: float = float('nan')
type Tree = Leaf | tuple[Tree, Tree]
type Mask = bool | tuple[Mask, Mask] # used to track tree traversals


def count_leaves(tree: Tree) -> int:
    if isinstance(tree, Leaf):
        return 1
    left, right = tree
    return count_leaves(left) + count_leaves(right)




class Cell:
    def __init__(self, converge: Tree, diverge: Tree, value: int = 0):
        self.C: Tree = converge     # leaves are upstream cell indices
        self.D: Tree = diverge      # leaves are downstream cell indices
        self.value: int = value

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


    # TODO: compile to post-order tensor schedule for ~size speedup
    def converge(self, cells: list['Cell']) -> int:
        """Converge by NAND folding upstream cell values into a new value"""
        def nand(tree: Tree) -> int:
            if isinstance(tree, Leaf):
                value = cells[abs(tree.index) - 1].value
                # Negative indices are inhibited by bitwise NOT
                return ~value if tree.index < 0 else value
            left, right = tree
            return ~(nand(left) & nand(right))
        return nand(self.C)


    # TODO: compile to post-order tensor schedule for ~size speedup
    def diverge(self, rng: random.Random) -> Mask:
        """Diverge by bit pachinko on self.value through tree to target mask"""
        def distribute(signal: int, tree: Tree, rng: random.Random) -> Mask:
            if signal == 0:
                return False
            if isinstance(tree, Leaf):
                return True
            left, right = tree
            pivot = rng.getrandbits(DATA_WIDTH)
            return (distribute(signal & pivot,  left,  rng),
                    distribute(signal & ~pivot, right, rng))
        return distribute(self.value, self.D, rng)





class Graph:
    def __init__(self, size: int, rng: random.Random):
        self.size = size
        self.rng = rng
        self.cells: list[Cell] = [
            Cell(
                converge=(Leaf(i + 1), Leaf(((i + 1) % size) + 1)),
                diverge=(Leaf(i + 1), Leaf(((i + 1) % size) + 1)),
                value=rng.getrandbits(DATA_WIDTH),
            )
            for i in range(size)
        ]
        self.next_indices: set[int] = set(range(size))
        self.masks: dict[int, Mask] = {i: False for i in range(size)}


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
        self.masks: dict[int, Mask] = {}
        tally: dict[int, int] = defaultdict(int)

        def update_tally(tree: Tree, mask: Mask):
            if mask is False:
                return
            if isinstance(tree, Leaf):
                i = tree.index
                tally[(i if i > 0 else -i) - 1] += 1 if i > 0 else -1 # index strictly GT; excitation has to win
            else:
                left_tree, right_tree = tree
                left_mask, right_mask = mask
                update_tally(left_tree, left_mask)
                update_tally(right_tree, right_mask)


        for i in active:
            cell = self.cells[i]
            mask: Mask = cell.diverge(self.rng)
            update_tally(cell.D, mask)
            self.masks[i] = mask

        self.next_indices = {k for k, v in tally.items() if v > 0} # +1 offset
        return self
