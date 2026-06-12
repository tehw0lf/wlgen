"""wlgen - A recursive wordlist generator

This package provides multiple implementations for generating wordlists
by calculating the n-ary Cartesian product of input character sets.
"""

from importlib.metadata import version

from wlgen.core import (
    estimate_wordlist_size,
    gen_wordlist,
    gen_wordlist_iter,
    gen_words,
    generate_wordlist,
)

__all__ = [
    "gen_wordlist",
    "gen_wordlist_iter",
    "gen_words",
    "generate_wordlist",
    "estimate_wordlist_size",
]
__version__ = version("wlgen")
