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

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and development workflow.

## Setup

Install dependencies:
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
