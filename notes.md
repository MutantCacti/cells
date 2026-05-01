```py
def inverse_or(c: int, width: int = 64) -> tuple[int, int]:
    r = random.getrandbits(2 * width)
    # Interpret r as width independent values in [0, 4); reject 3, retry per-bit
    # Simpler: draw r1, r2 such that (r1, r2) is uniform over
    (0,1),(1,0),(1,1) at each bit
    # Trick: generate r1, r2, then at positions where both are 0, force one to 1
    r1 = random.getrandbits(width)
    r2 = random.getrandbits(width)
    both_zero = ~r1 & ~r2 & ((1 << width) - 1)
    # At both_zero positions, flip a coin to set either r1 or r2
    coin = random.getrandbits(width)
    r1 |= both_zero & coin
    r2 |= both_zero & ~coin
    a = c & r1
    b = c & r2
    return a, b
```

versus

```py
def random_or(tree: Tree, signal: int, edges: list[int]) -> list[int]:
    if signal == 0:
        return edges
    if isinstance(tree, int):
        return edges + [tree]
    left, right = tree
    mask = random.getrandbits(BITSTRING_WIDTH)
    edges = random_or(left,  signal & mask,  edges)
    edges = random_or(right, signal & ~mask, edges)
    return edges
```

---

Hypothesis: src/graph.py can do "anything" given: 1. error signal from a human, 2. a parser and compiler, 3."anything"-sized space.
Null hypothesis: There are things src/graph.py cannot do given all three of these elements.
Alternate Hypothesis: src/graph.py can do "anything" given: 1. a parser and compiler and 3."anything"-sized space (where "space" also means "energy" in the real world).
Alternate Null Hypothesis: src/graph.py requires human in the loop.

PoC extension:

- Compilation to post-order schedules of trees for tensor acceleration ~N times speedup
- Context division error
