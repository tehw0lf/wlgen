# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**wlgen** is a recursive wordlist generator library written in Python. It calculates the n-ary Cartesian product of input character sets to generate wordlists with custom character sets for each string position.

## Core Architecture

### Wordlist Generation Algorithms

The library provides three distinct implementations with different performance characteristics:

1. **`gen_wordlist(charset)`** (wlgen/core.py:4)
   - Builds the entire wordlist in memory using recursive list comprehensions
   - Fast but memory-intensive
   - Best for small to medium wordlists that fit in memory
   - Returns a complete list of all generated words

2. **`gen_wordlist_iter(charset)`** (wlgen/core.py:25)
   - Uses `itertools.product` for lazy evaluation
   - Memory-efficient generator-based approach
   - Recommended for large wordlists that exceed memory constraints
   - Returns an iterator mapping over product tuples

3. **`gen_words(charset, positions=None, prev_iter=None)`** (wlgen/core.py:33)
   - Pure recursive generator implementation
   - Memory-efficient but slower than `gen_wordlist_iter`
   - Yields words one at a time without building intermediate structures
   - Uses position tracking for recursive state management

### Package Structure

- **wlgen/__init__.py**: Public API exports
- **wlgen/core.py**: Core wordlist generation implementations
- **wlgen/benchmarks/**: Performance benchmarking suite
- **wlgen/tests/**: Unit tests

### Input Format

All functions expect a dictionary where:
- Keys are integer positions (0-indexed)
- Values are strings containing character sets for that position
- Character sets are automatically deduplicated and sorted internally

Example: `{0: '123', 1: 'ABC', 2: '!"§ '}`

## Development Commands

### Environment Setup
```bash
uv sync --all-extras --group lint    # Install all dependencies including linting
```

### Testing
```bash
uv run python -m unittest discover   # Run all unit tests
uv run python -m unittest wlgen.tests  # Run specific test module
```

### Linting
```bash
uv run ruff check                    # Check code quality
uv run ruff check --fix              # Auto-fix linting issues
uv run ruff format                   # Format code
```

### Building & Publishing
```bash
uv build                             # Build wheel and sdist to dist/
uv publish                           # Publish to PyPI (requires UV_TOKEN)
```

### Benchmarking
```bash
uv run python wlgen/benchmarks/benchmark.py    # Run performance benchmarks
```

### Pre-commit Validation
```bash
uv run ruff check && uv run python -m unittest discover && uv build
```

## Performance Benchmarking

Performance benchmarks are located in `wlgen/benchmarks/` and measure:
- Execution time across different problem sizes
- Memory usage (peak RSS)
- Throughput (combinations/second)
- First result latency for generators

**Baseline Results** (1M combinations):
- `gen_wordlist_iter`: ~710K comb/s, minimal memory
- `gen_words`: ~260K comb/s, minimal memory
- `gen_wordlist`: Only suitable for small wordlists (<100K combinations)

See `wlgen/benchmarks/README.md` and `OPTIMIZATION_ANALYSIS.md` for details.

## Testing Strategy

The test suite (wlgen/tests/__init__.py) validates all three generation algorithms produce identical output:
- Tests run against a reference charset with mixed character types
- Output is written to temporary files and compared against platform-specific sample files
- Platform detection handles DOS vs Unix line ending differences
- Reference files: `wlgen/tests/files/sample_mixed_{dos|unix}`

## CI/CD Pipeline

The project uses a reusable workflow from the `tehw0lf/workflows` repository:
- Workflow: `.github/workflows/build.yml`
- Triggers: Push to main branch and all pull requests
- Actions: Install dependencies, lint, test, build, publish to PyPI (on main), create GitHub releases
- Publishing: Conditional on UV_TOKEN secret availability

## Command-Line Interface

The package includes a CLI entry point defined in pyproject.toml:
```bash
wlgen <args>    # Invokes wlgen:main function
```
