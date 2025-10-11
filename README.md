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

## Smart Dispatcher (Recommended)

The `generate_wordlist()` function automatically selects the optimal algorithm based on problem size:

```python
import wlgen

# Auto-select optimal algorithm
charset = {0: '123', 1: 'ABC', 2: 'xyz'}
wordlist = wlgen.generate_wordlist(charset)

# Use the result (list or iterator depending on size)
for word in wordlist if not isinstance(wordlist, list) else wordlist:
    print(word)
```

**Selection Strategy:**
- Tiny (<1K combinations): Uses `gen_wordlist` (fastest, low memory)
- Small (1K-100K): Uses `gen_wordlist` (fast and convenient)
- Medium+ (100K+): Uses `gen_wordlist_iter` (optimal throughput, constant memory)

**Options:**

```python
# Force memory-efficient mode for any size
wordlist = wlgen.generate_wordlist(charset, prefer_memory_efficient=True)

# Manual algorithm selection
wordlist = wlgen.generate_wordlist(charset, method='iter')  # Force iterator
wordlist = wlgen.generate_wordlist(charset, method='list')  # Force list
wordlist = wlgen.generate_wordlist(charset, method='words') # Force gen_words

# Skip input validation for pre-cleaned data (performance optimization)
wordlist = wlgen.generate_wordlist(charset, method='iter', clean_input=True)
```

**Estimate wordlist size before generation:**

```python
size = wlgen.estimate_wordlist_size(charset)
print(f"Will generate {size:,} combinations")
```

## Direct Implementation Access

Three implementations are available for direct use:

- `gen_wordlist_iter`: Fast generator using `itertools.product` (~780-810K comb/s).
- `gen_wordlist`: Builds entire list in memory. Fastest for small lists (~900K-1.6M comb/s).
- `gen_words`: Memory-efficient recursive generator (~210-230K comb/s).

All implementations calculate the n-ary Cartesian product of input character sets.

```python
import wlgen

charset = {0: '123', 1: 'ABC'}

# Use specific implementation
for word in wlgen.gen_wordlist_iter(charset):
    print(word)
```

**Note:** NumPy, CUDA, and multiprocessing were investigated but found to provide no performance benefit for this workload. String operations are fundamentally CPU-bound and too fast for parallelization overhead. See [issues #17](https://github.com/tehw0lf/wlgen/issues/17), [#18](https://github.com/tehw0lf/wlgen/issues/18), [#20](https://github.com/tehw0lf/wlgen/issues/20) for detailed analysis.

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
