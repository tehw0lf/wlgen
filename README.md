# Description

A recursive wordlist generator written in Python.
For each string position, custom character sets can be defined.

# Prerequisites

Python 3.0 or higher

# Installation

From PyPI:

```bash
pip install wlgen
```

From GitHub:

```bash
git clone https://github.com/tehw0lf/wlgen.git
cd wlgen
pip install .
```

# Usage

Three implementations are available:

- `gen_wordlist_iter`: Recommended for most use cases. Fast generator using `itertools.product`.
- `gen_wordlist`: Builds entire list in memory. Fast but memory-intensive.
- `gen_words`: Memory-efficient generator. Slower than `gen_wordlist_iter`.

All implementations calculate the n-ary Cartesian product of input character sets.

# Development

Run tests:
```bash
python -m unittest discover
```

Run benchmarks:
```bash
python wlgen/benchmarks/benchmark.py
```
