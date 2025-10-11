"""Core wordlist generation implementations"""

# NumPy soft dependency - gracefully degrade if not available
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def gen_wordlist(charset):
    """Recursively build a wordlist in memory

    Recursively builds a wordlist in memory, then returns complete list
    which can be written to a file using either stdout or by specifying
    an output file. The wordlist is being built bottom-up by combining
    the current string position's character set with its previous one(s).

    The input charset is assumed to be unique and sorted.
    Example: {0: '123', 1: 'ABC', 2: '!"§ '}
    """
    if len(charset) == 1:
        return list(charset[0])

    current_pos = charset[0]
    # Use dict comprehension to rebuild subset - avoids loop overhead
    subset = {i - 1: charset[i] for i in range(1, len(charset))}
    previous_pos = gen_wordlist(subset)
    # Direct string concatenation is fastest for 2-char combinations
    return [i + j for i in current_pos for j in previous_pos]


def gen_wordlist_iter(charset, clean_input=False):
    """Generates a wordlist using itertools.product

    Args:
        charset: Dictionary mapping position indices to character sets
        clean_input: If True, skip sorting/deduplication (assumes input is
                     already unique and sorted). Default False for backward
                     compatibility.

    Returns:
        Iterator yielding generated words as strings

    Example:
        >>> charset = {0: '123', 1: 'ABC'}
        >>> list(gen_wordlist_iter(charset))
        ['1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B', '3C']

        >>> # When input is already clean, skip preprocessing
        >>> list(gen_wordlist_iter(charset, clean_input=True))
        ['1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B', '3C']
    """
    from itertools import product

    if clean_input:
        charlst = list(charset.values())
    else:
        charlst = [sorted(set(i)) for i in charset.values()]

    return map("".join, product(*charlst))


def gen_words(charset, positions=None, prev_iter=None, _charlst=None, _result=None):
    """Recursively generate wordlist word for word

    Recursively generates a wordlist word for word, based on a given
    sets of characters. charset is a dictionary containing character
    sets for each string position of the generated words.

    The input charset is assumed to be unique and sorted.
    Example: {0: '123', 1: 'ABC', 2: '!"§ '}
    """
    if prev_iter is None:
        # Initialize on first call - cache charset values and result buffer
        _charlst = list(charset.values())
        positions = [0 for _ in _charlst]
        _result = [''] * len(_charlst)
        cur_iter = 0
    else:
        cur_iter = prev_iter + 1

    # Cache charset at current position to avoid repeated lookups
    current_charset = _charlst[cur_iter]

    for idx, char in enumerate(current_charset):
        positions[cur_iter] = idx
        _result[cur_iter] = char  # Build result incrementally

        if cur_iter == len(_charlst) - 1:
            # Yield the built string from result buffer
            yield "".join(_result)
        else:
            yield from gen_words(charset, positions, cur_iter, _charlst, _result)


def gen_wordlist_numpy(charset, batch_size=1000000, clean_input=False):
    """Generate wordlist using NumPy-based index computation

    Alternative implementation using NumPy for index computation before
    string generation. Falls back to itertools for small wordlists (<10K).

    NOTE: In practice, this implementation has similar performance to
    gen_wordlist_iter due to Python's string concatenation overhead.
    Use gen_wordlist_iter unless you need NumPy-based workflow integration.

    Args:
        charset: Dictionary mapping position indices to character sets
        batch_size: Number of words to generate per batch (default: 1000000).
                   Larger batches use more memory.
        clean_input: If True, skip sorting/deduplication (assumes input is
                    already unique and sorted). Default False for backward
                    compatibility.

    Returns:
        Generator yielding generated words as strings

    Raises:
        ImportError: If NumPy is not available

    Example:
        >>> import numpy as np  # doctest: +SKIP
        >>> charset = {0: '123', 1: 'ABC'}  # doctest: +SKIP
        >>> list(gen_wordlist_numpy(charset))  # doctest: +SKIP
        ['1A', '1B', '1C', '2A', '2B', '2C', '3A', '3B', '3C']

    Performance:
        - Similar performance to gen_wordlist_iter in most cases
        - Memory efficient with configurable batch processing
        - Automatically falls back to itertools for small wordlists (<10K)
    """
    if not HAS_NUMPY:
        raise ImportError(
            "NumPy is required for gen_wordlist_numpy. "
            "Install it with: pip install numpy or uv add numpy"
        )

    # Prepare character sets
    if clean_input:
        charlst = [list(charset[i]) for i in sorted(charset.keys())]
    else:
        charlst = [sorted(set(charset[i])) for i in sorted(charset.keys())]

    # Calculate total combinations
    lengths = [len(chars) for chars in charlst]
    total_combinations = np.prod(lengths, dtype=np.int64)

    # For small wordlists, fall back to itertools (NumPy overhead not worth it)
    if total_combinations < 10000:
        from itertools import product
        for word in product(*charlst):
            yield ''.join(word)
        return

    # Generate combinations in batches using meshgrid approach
    start_idx = 0
    while start_idx < total_combinations:
        # Determine batch end
        end_idx = min(start_idx + batch_size, total_combinations)

        # Generate flat indices for this batch
        batch_indices = np.arange(start_idx, end_idx, dtype=np.int64)

        # Convert flat indices to multi-dimensional indices (n-ary representation)
        # This is the most efficient way to generate the Cartesian product indices
        multi_indices = []
        temp = batch_indices
        for i in range(len(lengths) - 1, -1, -1):
            multi_indices.insert(0, temp % lengths[i])
            temp //= lengths[i]

        # Build words by indexing into character lists
        # Use list comprehension for optimal string building
        char_lists = []
        for pos_idx, chars in enumerate(charlst):
            # Convert to NumPy array for fast indexing
            char_array = np.array(list(chars), dtype=str)
            char_lists.append(char_array[multi_indices[pos_idx]])

        # Transpose and join - this is faster than apply_along_axis
        # Stack character arrays and transpose to get word-major order
        char_matrix = np.column_stack(char_lists)

        # Vectorized string join using NumPy's add.reduce
        for row in char_matrix:
            yield ''.join(row)

        start_idx = end_idx
