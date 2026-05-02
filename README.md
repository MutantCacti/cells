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

`Graph` holds a set of indices to the next cells to update. Its main function is `Graph.update()`, which runs the convergence schedule to update cell.value l, then parsing the divergence schedule for `next_indices`.

## cellinput

CellInput base class for writing to arbitrary indices. Example: `SwitchHarness` which accepts any key as a non-blocking active signal.

## harness

## evolver

## main

```sh
./run [N] [D] # Optional cell count and DATA_WIDTH
```

