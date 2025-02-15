# Description

A recursive wordlist generator written in Python.
For each string position, custom character sets can be defined.

# Prerequisites

Python 3.x (developed on Python 3.7)

# Instructions

## Installation

To install from GitHub:

```
git clone https://github.com/tehw0lf/wlgen.git
cd wlgen
python setup.py test (optional unit tests to ensure functionality)
pip install .
```

To install from PyPI:

```
pip install wlgen
```

## Which function should I use?

Currently there are three implementations to generate a wordlist.
`gen_wordlist` builds the whole list in memory before writing it, `gen_words` is a generator that is memory efficient but slower.
`gen_wordlist_iter` uses `itertools.product` to generate the wordlist, which is recommended for lists that are too large to be built by `gen_wordlist`.
Both algorithms calculate the n-ary cartesian product of the input character sets.
