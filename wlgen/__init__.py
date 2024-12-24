def gen_wordlist(charset):
    """Recursively build a wordlist in memory

    Recursively builds a wordlist in memory, then returns complete list
    which can be written to a file using either stdout or by specifying
    an output file. The wordlist is being built bottom-up by combining
    the current string position's character set with its previous one(s).

    The input charset is assumed to be unique and sorted.
    Example: {0: '123', 1: 'ABC', 2: '!"§ '}
    """
    subset = {}
    if len(charset) == 1:
        return charset[0]
    else:
        current_pos = charset[0]
        for str_pos in range(1, len(charset)):
            subset[str_pos - 1] = charset[str_pos]
        previous_pos = gen_wordlist(subset)
        wlist = [(i + j) for i in current_pos for j in previous_pos]
        return wlist


def gen_wordlist_iter(charset):
    """Generates a wordlist using itertools.product"""
    from itertools import product

    charlst = [sorted(set(i)) for i in charset.values()]
    return map("".join, product(*charlst))


def gen_words(charset, positions=None, prev_iter=None):
    """Recursively generate wordlist word for word

    Recursively generates a wordlist word for word, based on a given
    sets of characters. charset is a dictionary containing character
    sets for each string position of the generated words.

    The input charset is assumed to be unique and sorted.
    Example: {0: '123', 1: 'ABC', 2: '!"§ '}
    """
    if prev_iter is None:
        positions = [0 for i in charset]
        cur_iter = 0
    else:
        cur_iter = prev_iter + 1
    for idx, _ in enumerate(charset[cur_iter]):
        positions[cur_iter] = idx
        if cur_iter == len(charset) - 1:
            yield "".join(
                [charset[idx][val] for idx, val in enumerate(positions)]
            )
        else:
            yield from gen_words(charset, positions, cur_iter)
