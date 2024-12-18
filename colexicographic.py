"""
Provides functions generating combinations in colexicographic order.

This module implements alternatives to itertools.combinations and 
itertools.combinations_with_replacement that:
1. Generate combinations in colexicographic order
2. Can handle infinite input iterables
"""

_MAX_NESTED = 20
_INDENT = "    "

def _0_combinations(iterable):
    yield ()

def _1_combinations(iterable):
    for x0 in iterable:
        yield (x0, )

def _2_combinations(stream):
    i1 = 0
    queue = [None] * 2
    for x1 in stream:
        queue[i1] = x1
        i1 += 1
        if i1 == 2:
            yield tuple(queue)
            break
    
    for x1 in stream:
        for x0 in queue:
            yield x0, x1
        queue.append(x1)

def _2_combinations_with_replacement(iterable):
    queue = []
    for x1 in iterable:
        queue.append(x1)
        for x0 in queue:
            yield x0, x1

class _combinations_base:
    """Base class for combinations and combinations_with_replacement"""
    
    def __init__(self, iterable, r):
        self._r = self.indexify(r)
        self._stream = iter(iterable)   # Insure a single pass on the input iterable
        if self._r < 0:
            raise ValueError("r must be non-negative")
        
        if self._r <= _MAX_NESTED and self._r not in self._nested_function_cache:
            self._nested_function_cache[self._r] = self._nested_function(self._r)
    
    @staticmethod
    def indexify(r):
        """Return the integer interpretation of r, using __index__"""
        if not hasattr(r, '__index__'):
            raise TypeError(f"'{type(r).__name__}' object cannot be interpreted as an integer")
        ind = r.__index__()
        if not isinstance(r, int):
            raise TypeError(f"__index__ returned non-int (type {type(ind).__name__})")
        return ind
    
    def __iter__(self):
        if self._r in self._nested_function_cache:
            return self._nested_function_cache[self._r](self._stream)
        return self._unnested(self._stream, self._r)

class combinations(_combinations_base):
    """Return r length subsequences of elements from the input iterable in colexicographic order.

    Args:
        iterable: Input iterable (can be infinite)
        r: Length of combinations to generate

    Returns:
        Iterator yielding r-length subsequences (tuples) of elements from iterable

    Example:
        combinations('ABCD', 2) → AB AC BC AD BD CD
    """
    
    _nested_function_cache = {0: _0_combinations, 1: _1_combinations, 2: _2_combinations}
    
    @staticmethod
    def _nested_function(r):
        """Returns a function yielding sequences of length r from input generator.
        
        Implemented with r nested loops, and r must be >= 3."""
        if r < 3:
            raise ValueError("r must be at least 3")
        
        # Function definition, queue initilization, and outer loop:
        code = [f"def _{r}_combinations(stream):",
                _INDENT + f"i{r-1} = 0",
                _INDENT + f"queue = [None] * {r}",
                _INDENT + f"for x{r-1} in stream:",
                _INDENT * 2 + f"queue[i{r-1}] = x{r-1}",
                _INDENT * 2 + f"i{r-1} += 1",
                _INDENT * 2 + f"if i{r-1} == {r}:",
                _INDENT * 3 + "yield tuple(queue)",
                _INDENT * 3 + "break",
                _INDENT + f"for x{r-1} in stream:"]
        
        # Nested loops:
        for j in range(r - 2):
            code.append(_INDENT * (j+2) + f"for i{r-j-2} in range({r-j-2}, i{r-j-1}):")
            code.append(_INDENT * (j+3) + f"x{r-j-2} = queue[i{r-j-2}]")
        
        # Inner loop and yield statement:
        code.append(_INDENT * r + "for i0 in range(i1):")
        code.append(_INDENT * (r+1) + "yield queue[i0], " + ', '.join(f"x{i}" for i in range(1, r)))
        
        # Append to queue:
        code.append(_INDENT * 2 + f"queue.append(x{r-1})")
        code.append(_INDENT * 2 + f"i{r-1} += 1")
        
        # Execute and return function object
        namespace = {}
        exec('\n'.join(code), namespace)
        return namespace[f"_{r}_combinations"]
    
    @staticmethod
    def _unnested(stream, r):
        """Generate sequences of length r from generator (stream)"""
        indices = [0] * r   # Indices of elements in current sequence
        queue = [None] * r   # All elements from stream so far
        sequence = [None] * r   # Elements in current sequence - always yield tuple(sequence)
        j = 0   # Position (in indices and sequence) that needs to be updated 
        
        # Initialize with first r elements, if they exist:
        for x in stream:
            indices[j] = j
            queue[j] = x
            sequence[j] = x
            if j == r - 1:
                yield tuple(sequence)
                break
            else:
                j += 1
        
        # Sequences from remaining elements, if they exist:
        for x in stream:
            indices[j] += 1   # We always have j=r-1 at this point
            queue.append(x)
            sequence[j] = x
            yield tuple(sequence)
            j -= 1   # Next position to update
            while True:
                indices[j] += 1
                sequence[j] = queue[indices[j]]
                yield tuple(sequence)
                # Update j for next modification, and reset first elements in sequence if needed:
                if j > 0:
                    j -= 1
                else:
                    while j < r - 1 and indices[j] + 1 == indices[j + 1]:
                        indices[j] = j
                        sequence[j] = queue[j]
                        j += 1
                    if j == r - 1: break

class combinations_with_replacement(_combinations_base):
    """Return r length subsequences of elements from the input iterable in colexicographic order, with replacement (elements from iterable may be repeated in a subsequence).

    Args:
        iterable: Input iterable (can be infinite)
        r: Length of combinations to generate

    Returns:
        Iterator yielding r-length subsequences (tuples) of elements from iterable

    Example:
        combinations('ABC', 2) → AA AB BB AC BC CC
    """
    
    _nested_function_cache = {0: _0_combinations, 1: _1_combinations,
                              2: _2_combinations_with_replacement}
    
    @staticmethod
    def _nested_function(r):
        """Returns a function yielding sequences of length r (with replacement) from input generator.
        
        Implemented with r nested loops, and r must be >= 3."""
        if r < 3:
            raise ValueError("r must be at least 3")
            
        # Function definition, queue initilization, and outer loop:
        code = [f"def _{r}_combinations_with_replacement(iterable):",
                _INDENT + f"queue = []",
                _INDENT + f"for x{r-1} in iterable:",
                _INDENT * 2 + f"queue.append(x{r-1})"]

        # 2-nd loop:
        code.append(_INDENT * 2 + f"for i{r-2}, x{r-2} in enumerate(queue):")

        # Nested loops:
        for j in range(r - 3):
            code.append(_INDENT * (j+3) + f"for i{r-j-3} in range(i{r-j-2} + 1):")
            code.append(_INDENT * (j+4) + f"x{r-j-3} = queue[i{r-j-3}]")

        # Inner loop and yield statement:
        code.append(_INDENT * r + "for i0 in range(i1 + 1):")
        code.append(_INDENT * (r+1) + "yield queue[i0], " + ', '.join(f"x{i}" for i in range(1, r)))
        
        # Execute and return function object
        namespace = {}
        exec('\n'.join(code), namespace)
        return namespace[f"_{r}_combinations_with_replacement"]
    
    @staticmethod
    def _unnested(stream, r):
        """Generate sequences of length r with replacement from generator (stream)"""
        
        # Initialize with first element (if it exists):
        try:
            first_item = next(stream)
        except StopIteration:
            return

        indices = [0] * r   # Keeps track of the indices of elements from stream for current sequence
        queue = [first_item]   # All elements from stream so far
        sequence = [first_item] * r   # Elements in current sequence - always yield tuple(sequence)
        yield tuple(sequence)

        j = r - 1   # Position that needs to be updated (in indices and sequence)

        # Use remaining elements, if they exist:
        for x in stream:
            indices[j] += 1   # We always have j=r-1 at this point
            queue.append(x)
            sequence[j] = x
            yield tuple(sequence)
            j -= 1   # Next position to update
            while True:
                indices[j] += 1
                sequence[j] = queue[indices[j]]
                yield tuple(sequence)
                # Update j for next modification, and reset first sequence elements if needed:
                if j > 0:
                    j -= 1
                else:
                    while j < r - 1 and indices[j] == indices[j + 1]:
                        indices[j] = 0
                        sequence[j] = first_item
                        j += 1
                    if j == r - 1: break