"""wlgen - A recursive wordlist generator

This package provides multiple implementations for generating wordlists
by calculating the n-ary Cartesian product of input character sets.
"""

from wlgen.core import gen_wordlist, gen_wordlist_iter, gen_words

__all__ = ["gen_wordlist", "gen_wordlist_iter", "gen_words"]
__version__ = "1.3.3"
