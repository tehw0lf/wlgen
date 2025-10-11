"""Core wordlist generation implementations"""


def estimate_wordlist_size(charset):
    """Estimate the total number of combinations in a wordlist

    Calculates the n-ary Cartesian product size without generating the wordlist.
    This is used for algorithm selection in the smart dispatcher.

    Args:
        charset: Dictionary mapping position indices to character sets

    Returns:
        int: Estimated number of combinations

    Example:
        >>> estimate_wordlist_size({0: '123', 1: 'AB'})
        6
        >>> estimate_wordlist_size({0: 'abc', 1: 'xyz', 2: '123'})
        27
    """
    if not charset:
        return 0

    size = 1
    for chars in charset.values():
        # Handle both string and iterable character sets
        char_count = len(set(chars)) if isinstance(chars, str) else len(chars)
        size *= char_count

    return size


def generate_wordlist(charset, method='auto', prefer_memory_efficient=False, clean_input=False):
    """Smart dispatcher for wordlist generation

    Automatically selects the optimal wordlist generation algorithm based on
    problem size and user preferences. This is the recommended entry point
    for most use cases.

    Args:
        charset: Dictionary mapping position indices to character sets
                 Example: {0: '123', 1: 'ABC', 2: '!"§ '}
        method: Algorithm selection strategy (default: 'auto')
                - 'auto': Automatically select based on problem size
                - 'list': Use gen_wordlist (in-memory, fast for small lists)
                - 'iter': Use gen_wordlist_iter (memory-efficient, optimal throughput)
                - 'words': Use gen_words (memory-efficient generator)
        prefer_memory_efficient: If True, always prefer generator-based approaches
                                regardless of problem size (default: False)
        clean_input: If True, skip sorting/deduplication for pre-validated input.
                    Only applies to 'iter' method. (default: False)

    Returns:
        Iterator or list depending on selected method:
        - 'list': Returns complete list of generated words
        - 'iter'/'words': Returns iterator yielding words

    Selection Strategy (method='auto'):
        - Tiny (<1,000 combinations): gen_wordlist (fastest, low memory)
        - Small (1,000-100,000): gen_wordlist if not prefer_memory_efficient
        - Medium+ (100,000+): gen_wordlist_iter (optimal throughput)
        - Memory constrained (prefer_memory_efficient=True): Always gen_wordlist_iter

    Performance Characteristics:
        - gen_wordlist: ~900K-1.6M comb/s, builds complete list in memory
        - gen_wordlist_iter: ~780-810K comb/s, constant memory usage
        - gen_words: ~210-230K comb/s, constant memory usage

    Examples:
        >>> # Auto-select optimal algorithm
        >>> wordlist = generate_wordlist({0: '123', 1: 'AB'})
        >>> list(wordlist) if hasattr(wordlist, '__iter__') and not isinstance(wordlist, list) else wordlist
        ['1A', '1B', '2A', '2B', '3A', '3B']

        >>> # Force memory-efficient mode
        >>> for word in generate_wordlist({0: 'abc', 1: 'xyz'}, prefer_memory_efficient=True):
        ...     print(word)

        >>> # Manual algorithm selection
        >>> wordlist = generate_wordlist({0: '123'}, method='list')
        >>> # Returns: ['1', '2', '3']

    Note:
        NumPy, CUDA, and multiprocessing were investigated but found to provide
        no performance benefit for this workload. String operations are
        fundamentally CPU-bound and too fast for parallelization overhead.
        See issues #17, #18, #20 for detailed analysis.
    """
    if method == 'auto':
        # Estimate problem size
        size = estimate_wordlist_size(charset)

        # Always prefer memory-efficient if requested
        if prefer_memory_efficient:
            method = 'iter'
        # Tiny problems (<1K): gen_wordlist is fastest
        elif size < 1000:
            method = 'list'
        # Small problems (1K-100K): gen_wordlist is still fast and convenient
        elif size < 100000:
            method = 'list'
        # Medium+ problems (100K+): gen_wordlist_iter is optimal
        else:
            method = 'iter'

    # Dispatch to appropriate implementation
    if method == 'list':
        return gen_wordlist(charset)
    elif method == 'iter':
        return gen_wordlist_iter(charset, clean_input=clean_input)
    elif method == 'words':
        return gen_words(charset)
    else:
        raise ValueError(f"Invalid method '{method}'. Choose from: 'auto', 'list', 'iter', 'words'")


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
