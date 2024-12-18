# Colexicographic Combinations

A Python module providing a variation on `itertools.combinations` and `itertools.combinations_with_replacement` that generate combinations in colexicographic order and can handle infinite input iterables.

## Installation

```bash
# Clone the repository
git clone https://github.com/moshejw/colexicographic.git

# Copy colexicographic.py to your project directory
```

## Usage

Basic usage:
```python
from colexicographic import combinations, combinations_with_replacement
for tup in combinations('ABCD', 2):
    print(tup)  # Outputs: ('A', 'B') ('A', 'C') ('B', 'C') ('A', 'D'), ('B', 'D'), ('C', 'D')
```

With infinite iterables:
```python
from itertools import count
for tup in combinations(count(), 2):
    if tup[1] > 3: break
    print(tup)  # Outputs: (0,1) (0,2) (1,2) (0,3) (1,3) (2,3)
```

## When to Use

- When colexicographic order is more natural for your use case (as in sometimes the case in combinatorics)
- When working with infinite iterables (lexicographic order would never finish generating combinations that start with the first element, and itertools tries to create all elements from iterable in memory)
- Interface is identical to itertools versions for smooth transition
