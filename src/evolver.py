"""
src/evolver.py
TODO: docstring

Created: 2026-05-02
 Author: Maxence Morel Dierckx
"""
import sys
import random
from collections import deque
from cells import Tree, Leaf, Cell, Graph


PRECISION = 1e-9
ALPHA = 0.6


class Sample:
    def __init__(self, start: int, duration: int, error: int, index: int):
        self.start = start
        self.duration = duration
        self.error = error
        self.index = index

    def check(self, now: int) -> bool:
        return now - self.start > self.duration




class Evolver:
    def __init__(self, graph: Graph, rng: random.Random):
        self.graph = graph
        self.rng = rng
        self.samples: set['Sample'] = set()


    # Override
    def prediction(self, error: int, cell: 'Cell') -> int:
        raise NotImplementedError


    # Override
    def mutate(self, cell: 'Cell'):
        raise NotImplementedError


    # Override
    def correction(self, sample: 'Sample', error: int, cell: 'Cell') -> int:
        raise NotImplementedError


    def update(self, harness):
        completed = {s for s in self.samples if s.check(harness.tick)}
        self.samples -= completed

        # Mutate completed sample cells
        for sample in completed:
            error = harness.window_error(sample)
            cell = harness.graph.cells[sample.index]
            mutation = ALPHA * self.correction(sample, error, cell) # TODO: figure out what alpha means and what range correction is in (propose [0, 1])
            if self.rng.random() < mutation:
                self.mutate(cell)

        # Sample currently untracked firing cells
        pending_indices = {s.index for s in self.samples}
        for i in harness.graph.next_indices:
            if i not in pending_indices:
                error = harness.current_error()
                cell = harness.graph.cells[i]
                self.samples.add(Sample(
                    start = harness.tick,
                    duration = self.prediction(error, cell),
                    error = error,
                    index = i,
                ))




class SwitchEvolver(Evolver):
    def __init__(self, graph, rng):
        super().__init__(graph, rng)
        self.count = 0

    def prediction(self, error, cell) -> int:
        return - ( cell.Cc * cell.Dc )


    def correction(self, sample, error, cell) -> float:
        return max(0, error - sample.error)


    def mutate(self, cell):
        mutate_side = self.rng.random() < 0.5
        num_cells = len(self.graph.cells)
        if mutate_side: # Converge
            new_tree = self.swap_random_leaf(cell.C, num_cells)
            cell.replace_C(new_tree)
        else: # Diverge
            new_tree = self.swap_random_leaf(cell.D, num_cells)
            cell.replace_D(new_tree)


    def swap_random_leaf(self, tree: Tree, num_cells: int):
        if isinstance(tree, Leaf):
            sign = self.rng.choice([1, -1])
            self.count += 1
            sys.stdout.flush()
            return Leaf(sign * self.rng.randint(1, num_cells), float('nan'))
        left, right = tree
        if self.rng.random() < 0.5:
            return (self.swap_random_leaf(left, num_cells), right)
        else:
            return (left, self.swap_random_leaf(right, num_cells))



""" class SwitchEvolver(Evolver):
    def __init__(self, rng):
        super().__init__()
        self._Y = 0 """




""" def get_loss(self, harness) -> float:

    for 

    d = time.perf_counter() - self.time
    Y = self.measure()
    dY = (Y - self._Y) / d if d > 0 else 0

    # Predicted uncertainty (time to convergence)
    ddY = 0
    if abs(Y) < PRECISION and abs(dY) < PRECISION:
        ddY = 0.0
    elif abs(dY) < max(PRECISION, ALPHA * abs(Y)):
        ddY = float('inf') # plateau
    else:
        ddY = abs(Y / dY)

    ddY_ = ddY / d # convert to graph units
    pred_ddY_ = harness.measure()
    L = pred_ddY_ - ddY_

    self.time += d

    return L
"""