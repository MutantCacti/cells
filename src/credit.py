"""
src/credit.py
An abstraction for a unit of credit in the graph.

Created: 2026-05-06
Authors: Maxence Morel Dierckx, Claude Code Opus 4.7
"""
from cells import Leaf, Tree, Mask, Cell, Graph
from evolver import ALPHA




class Credit:
    def __init__(self, harness: 'Harness', cell: 'Cell'):
        self.harness = harness
        self.cell = cell


    def update_cell(self, Y_t: float, mask: Mask):
        def update_ema(ema: float) -> float:
            return Y_t if math.isnan(ema) else (1 - ALPHA) * ema + ALPHA * Y_t

        def update_leaves(tree: Tree) -> Tree:
            if isinstance(tree, Leaf):
                new_ema = update_ema(tree.ema)
                return Leaf(tree.index, new_ema)
            left, right = tree
            return (update_leaves(left), update_leaves(right))

        def update_masked(tree: Tree, mask: Mask) -> Tree:
            if mask is False:
                return tree
            if isinstance(tree, Leaf):
                new_ema = update_ema(tree.ema)
                return Leaf(tree.index, new_ema)
            left_tree, right_tree = tree
            left_mask, right_mask = mask
            return (update_masked(left_tree,  left_mask),
                    update_masked(right_tree, right_mask))

        self.cell.C = update_leaves(self.cell.C)
        self.cell.D = update_masked(self.cell.D, mask)


    def update(self, harness: 'Harness', mask: Mask):
        """ TODO: cardinality orders
        t = harness.tick
        Y_t = harness.current_error()
        dY_t = Y_t / t # error per time """

        if harness.input.read() != 0: # only learn input
            self.update_cell(harness.current_error(), mask)

