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

---

```py
cells/src main ? ❯ python
Python 3.14.4 (main, Apr  8 2026, 17:48:49) [GCC 15.2.1 20260209] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from space import Space
>>> import random
>>> rng = random.Random()
>>> s = Space(8, rng)
>>> s
<space.Space object at 0x7fddea859160>
>>> print(s.cells)
[<space.Cell object at 0x7fddea858ad0>, <space.Cell object at 0x7fddea9b6ad0>, <space.Cell object at 0x7fddea9b6490>, <space.Cell object at 0x7fddea87c180>, <space.Cell object at 0x7fddea87c640>, <space.Cell object at 0x7fddeaab2c30>, <space.Cell object at 0x7fddea812360>, <space.Cell object at 0x7fddea812470>]
>>> for cell in s.cells:
...     print(cell.value)
...     
13056112310781561994
8406672687597636777
18052626968141575383
8397496338371894957
17593712058340741861
6798217040340226453
2399385779092594927
3144335035618740979
>>> s.update()
<space.Space object at 0x7fddea859160>
>>> for cell in s.cells:
...     print(cell.value)
...     
-3756143104935873673
-8107183036072985730
-8106971929837311110
-8361322367129490086
-6055101106456367238
-20288330582196358
-2377975396094181604
-2387083759340767363
>>> s.update()
<space.Space object at 0x7fddea859160>
>>> for cell in s.cells:
...     print(cell.value)
...     
8404420887515516041
8107534879793878149
8397491901670626981
8361331163224609445
6073137499762856069
2398259328356188391
2387158552173889763
3828235918250888330
>>> s.update()
<space.Space object at 0x7fddea859160>
>>> for cell in s.cells:
...     print(cell.value)
...     
-8107183036072985730
-8106971929837311110
-8361322367129490086
-6055101106456367238
-20288330582196358
-2377975396094181604
-2387083759340767363
-3756143104935873673
>>>
```
