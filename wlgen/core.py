"""Core wordlist generation implementations"""


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
