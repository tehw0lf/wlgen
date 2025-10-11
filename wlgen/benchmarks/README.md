# Wordlist Generation Benchmarks

Performance benchmark suite for wlgen implementations.

## Running Benchmarks

### Basic Usage

```bash
uv run python -m wlgen.benchmarks.benchmark
```

### From Project Root

```bash
uv run python wlgen/benchmarks/benchmark.py
```

## Test Cases

### Small Tests (All Implementations)
- **small_1**: 3 positions, 5 chars each (~125 combinations)
- **small_2**: 4 positions, 7 chars each (~2,401 combinations)
- **small_3**: 5 positions, 8 chars each (~32,768 combinations)

### Medium Tests (Generators Only, Limited to 10M)
- **medium_1**: 5 positions, 10 chars each (~100K combinations)
- **medium_2**: 6 positions, 12 chars each (~2.9M combinations)
- **medium_3**: 7 positions, 13 chars each (~62.7M combinations, sampled at 10M)

### Large Tests (Generators Only, Sampled)
- **large_1**: 7 positions, 15 chars each (~170M combinations, sampled at 1M)
- **large_2**: 8 positions, 16 chars each (~4.3B combinations, sampled at 1M)
- **large_3**: 9 positions, 20 chars each (~512B combinations, sampled at 1M)

### Extra Large Tests (Reserved for CUDA)
- **xlarge_1**: 10 positions, 25 chars each (~9.5 quadrillion combinations)
- **xlarge_2**: 12 positions, 30 chars each (astronomical, sampled at 1M)
- Run with `--xlarge` flag or `include_xlarge=True`

## Metrics Tracked

- **Execution Time**: Total wall-clock time to complete generation
- **Memory Usage**: Peak RSS memory consumption
- **Throughput**: Combinations generated per second
- **First Result Latency**: Time to generate first result (generators only)

## Output

Results are saved to `baseline_results.txt` in this directory and include:
- Detailed per-test results
- Summary comparison table
- System information

## Implementation Notes

### Small Tests
All three implementations (`gen_wordlist`, `gen_wordlist_iter`, `gen_words`) are tested since the output fits comfortably in memory.

### Medium/Large Tests
Only generator-based implementations (`gen_wordlist_iter`, `gen_words`) are tested to avoid memory exhaustion. In-memory `gen_wordlist` is skipped.

### Large Test Limits
Large tests are capped at 1M combinations to keep benchmark runtime reasonable while still measuring throughput accurately.
