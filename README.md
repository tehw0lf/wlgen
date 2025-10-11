# Description

A recursive wordlist generator written in Python.
For each string position, custom character sets can be defined.

# Prerequisites

Python 3.7 or higher

For NumPy support, Python 3.7+ and NumPy 1.20.0+ are required.

# Installation

From PyPI:

```bash
pip install wlgen
```

For high-performance NumPy implementation:

```bash
pip install wlgen[numpy]
```

From GitHub:

```bash
git clone https://github.com/tehw0lf/wlgen.git
cd wlgen
pip install .
# Or with NumPy support
pip install .[numpy]
```

# Usage

Four implementations are available:

- `gen_wordlist_iter`: **Recommended**. Fast generator using `itertools.product`. No dependencies.
- `gen_wordlist_numpy`: Alternative NumPy-based implementation with similar performance. Requires NumPy.
- `gen_wordlist`: Builds entire list in memory. Fast but memory-intensive (only for small wordlists).
- `gen_words`: Memory-efficient recursive generator. Slower than itertools.

All implementations calculate the n-ary Cartesian product of input character sets.

## Example

```python
import wlgen

# Define character sets for each position
charset = {0: '123', 1: 'ABC', 2: 'xyz'}

# Using itertools implementation (recommended, no dependencies)
for word in wlgen.gen_wordlist_iter(charset):
    print(word)

# Using NumPy implementation (requires numpy, similar performance)
if wlgen.HAS_NUMPY:
    for word in wlgen.gen_wordlist_numpy(charset):
        print(word)
```

## Performance Comparison

Based on benchmarks with various wordlist sizes:
- `gen_wordlist_iter`: ~600-700K combinations/second
- `gen_wordlist_numpy`: ~500-700K combinations/second (similar to itertools)
- `gen_words`: ~260-450K combinations/second
- `gen_wordlist`: Only suitable for small wordlists (<100K combinations)

# Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and development workflow.

## Setup

Install dependencies:
```bash
uv sync --all-extras --group lint --group numpy
```

Or without NumPy (will skip NumPy-related tests):
```bash
uv sync --all-extras --group lint
```

## Testing

Run tests:
```bash
uv run python -m unittest discover
```

## Benchmarking

Run performance benchmarks:
```bash
uv run python wlgen/benchmarks/benchmark.py
```

## Code Quality

Lint code:
```bash
uv run ruff check
```

Auto-fix linting issues:
```bash
uv run ruff check --fix
```

Format code:
```bash
uv run ruff format
```

## Building

Build wheel and source distribution:
```bash
uv build
```
