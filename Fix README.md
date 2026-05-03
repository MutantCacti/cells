# cells

A cell is an integer value with a convergence tree and a divergence tree.

```py
Tree: int | tuple[Tree, Tree]
```

## convergence

We do `~(int & int)` on leaves recursively. In later versions, this can be a tensorised schedule of sequential NAND operations executed in parallel streams.
Leaves are signed. Converging integers are ~ NOT ed when negative.
Convergence writes cell.value and is the **forward pass**, taking previous input and writing new.

## divergence

Let bits = 011001.
Take some tree:
```
 |
/ \
```
and flip it.
```
\ /
 |
```
generate random bits 001001
NAND it with bits:
```
011001 001001
    001001
```
--> goes left
and XOR the same
```
011001 001001
    010000
```
--> goes right

This can be run on the whole tree by threading random values to the GPU.
We think of it as a distribution, because the structure will dictate where chance goes.

## graph

Holds an array of cells and routes them.

`Graph` holds a set of indices to the next cells to update. Its main function is `Graph.update()`, which runs the convergence schedule to update cell.values, then parses the divergence schedule for `next_indices`.

## sample

```py
class Sample:
    def __init__(self, start: float y_pred: float, prev_y: float, index: int):
    self.time = time.perf_counter()
    self.duration = self.index # literally nanoseconds
    ...
    def sample(self):
        return ( time.perf_counter() - self.time ) > self.duration
```

A sample is effectively a timer and measures whether error has improved over a short window when it is compared to a CellInput.

## cellinput

CellInput base class for writing to arbitrary indices. Example: 

`KeyInput` which accepts any key as a non-blocking signal.

It writes, for example, to index i of n cells.

## evolver

An `Evolver` holds a number of Samples written by cells. Because each sample has an index, it can find y_pred and prev_y for a specific cell value and compare how the prediction has changed.

We call predicted difference in error, or change in error the *innovation* of a cell.

We compare it to a measured value from the input. Note that the Sample never saves the past input; instead, the cell is expected to have predicted what we are reading now, which it did not know then.

## harness

A `Harness` holds a Graph, a CellInput and an Evolver.

It, updates the graph, retrieving cell values,

Then reads the input, sampling reality,

And updates the evolver.

These correspond to Fetch, Decode, Execute and are the CPU cycle of the logical stream.



## main

```sh
./run [N] [D] # Optional cell count and DATA_WIDTH
```

