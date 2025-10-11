#!/usr/bin/env python3
"""
Benchmark suite for wlgen wordlist generation implementations.

Measures performance across different problem sizes:
- Small: 3-5 positions, 5-8 chars each (~125-33K combinations)
- Medium: 5-7 positions, 10-13 chars each (~100K-63M combinations)
- Large: 7-9 positions, 15-20 chars each (~170M-512B combinations, sampled at 1M)
- XLarge: 10-12 positions, 25-30 chars each (reserved for CUDA benchmarks)

Metrics tracked:
- Execution time (wall clock)
- Memory usage (peak RSS)
- Throughput (combinations/second)
- First result latency (for generators)
"""

import sys
import time
import tracemalloc
from typing import Callable, Dict

import wlgen


class BenchmarkResult:
    """Store benchmark results for a single test"""

    def __init__(self, name: str, impl_name: str, charset_size: str):
        self.name = name
        self.impl_name = impl_name
        self.charset_size = charset_size
        self.execution_time = 0.0
        self.memory_peak = 0
        self.combinations_generated = 0
        self.first_result_latency = 0.0
        self.throughput = 0.0
        self.error = None

    def __repr__(self):
        if self.error:
            return f"{self.name} [{self.charset_size}] - ERROR: {self.error}"
        return (
            f"{self.name} [{self.charset_size}]:\n"
            f"  Time: {self.execution_time:.4f}s\n"
            f"  Memory: {self.memory_peak / 1024 / 1024:.2f} MB\n"
            f"  Combinations: {self.combinations_generated:,}\n"
            f"  Throughput: {self.throughput:,.0f} comb/s\n"
            f"  First result: {self.first_result_latency * 1000:.2f}ms"
        )


def estimate_combinations(charset: Dict[int, str]) -> int:
    """Estimate total number of combinations"""
    result = 1
    for chars in charset.values():
        result *= len(set(chars))
    return result


def benchmark_function(
    func: Callable,
    charset: Dict[int, str],
    is_generator: bool = False,
    max_items: int = None,
) -> BenchmarkResult:
    """
    Benchmark a wordlist generation function

    Args:
        func: Function to benchmark
        charset: Input charset dictionary
        is_generator: True if function returns a generator
        max_items: Maximum items to generate (for large tests)
    """
    result = BenchmarkResult(
        func.__name__, func.__module__, f"{len(charset)} positions"
    )

    try:
        # Start memory tracking
        tracemalloc.start()

        # Start timing
        start_time = time.perf_counter()

        # Execute function
        output = func(charset)

        # Measure first result latency for generators
        if is_generator:
            first_result_time = time.perf_counter()
            iterator = iter(output)
            _ = next(iterator)  # Consume first item to measure latency
            result.first_result_latency = (
                time.perf_counter() - first_result_time
            )
            result.combinations_generated = 1

            # Consume remaining items
            count = 1
            for item in iterator:
                count += 1
                if max_items and count >= max_items:
                    break
            result.combinations_generated = count
        else:
            # For non-generators, convert to list and count
            if isinstance(output, (list, tuple)):
                result.combinations_generated = len(output)
            else:
                # Convert to list
                items = list(output)
                result.combinations_generated = len(items)

        # End timing
        result.execution_time = time.perf_counter() - start_time

        # Get peak memory usage
        current, peak = tracemalloc.get_traced_memory()
        result.memory_peak = peak
        tracemalloc.stop()

        # Calculate throughput
        if result.execution_time > 0:
            result.throughput = (
                result.combinations_generated / result.execution_time
            )

    except Exception as e:
        result.error = str(e)
        tracemalloc.stop()

    return result


def create_charset(
    positions: int, chars_per_position: int, base: str = None
) -> Dict[int, str]:
    """
    Create a test charset

    Args:
        positions: Number of positions in the wordlist
        chars_per_position: Number of characters per position
        base: Base character set to use (default: alphanumeric)
    """
    if base is None:
        base = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    charset = {}
    for i in range(positions):
        start_idx = (i * chars_per_position) % len(base)
        charset[i] = base[start_idx : start_idx + chars_per_position]
        if len(charset[i]) < chars_per_position:
            # Wrap around if needed
            charset[i] += base[: chars_per_position - len(charset[i])]

    return charset


def run_benchmarks(verbose: bool = True, include_xlarge: bool = False):
    """Run all benchmarks

    Args:
        verbose: Print detailed progress
        include_xlarge: Include extra-large tests (reserved for future CUDA benchmarks)
    """

    # Define test cases
    test_cases = [
        # Small tests - all implementations
        ("small_1", create_charset(3, 5), "small"),
        ("small_2", create_charset(4, 7), "small"),
        ("small_3", create_charset(5, 8), "small"),
        # Medium tests - generators only due to memory
        ("medium_1", create_charset(5, 10), "medium"),
        ("medium_2", create_charset(6, 12), "medium"),
        ("medium_3", create_charset(7, 13), "medium"),
        # Large tests - generators only, limited sampling
        ("large_1", create_charset(7, 15), "large"),
        ("large_2", create_charset(8, 16), "large"),
        ("large_3", create_charset(9, 20), "large"),
    ]

    # Extra large tests - only run with flag (for CUDA benchmarks)
    if include_xlarge:
        test_cases.extend([
            ("xlarge_1", create_charset(10, 25), "xlarge"),
            ("xlarge_2", create_charset(12, 30), "xlarge"),
        ])

    # Functions to benchmark
    implementations = [
        (
            "gen_wordlist",
            wlgen.gen_wordlist,
            False,
            ["small"],
        ),  # name, func, is_generator, allowed_sizes
        ("gen_wordlist_iter", wlgen.gen_wordlist_iter, True, ["small", "medium", "large"]),
        ("gen_words", wlgen.gen_words, True, ["small", "medium", "large"]),
    ]

    all_results = []

    for test_name, charset, test_size in test_cases:
        estimated = estimate_combinations(charset)

        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Test: {test_name} ({test_size})")
            print(f"Charset: {len(charset)} positions")
            print(f"Estimated combinations: {estimated:,}")
            print(f"{'=' * 60}\n")

        for impl_name, func, is_gen, allowed_sizes in implementations:
            # Skip implementations not allowed for this test size
            if test_size not in allowed_sizes:
                if verbose:
                    reason = "memory-intensive" if test_size in ["medium", "large", "xlarge"] else "not applicable"
                    print(f"⏭️  Skipping {impl_name} ({reason} for {test_size})")
                continue

            # Set max items based on test size to keep runtime reasonable
            max_items_map = {
                "small": None,  # Run to completion
                "medium": 10_000_000,  # Limit to 10M for reasonable runtime
                "large": 1_000_000,  # Sample 1M
                "xlarge": 1_000_000,  # Sample 1M (reserved for CUDA)
            }
            max_items = max_items_map.get(test_size)

            if verbose:
                print(f"Running {impl_name}...", end=" ", flush=True)

            result = benchmark_function(func, charset, is_gen, max_items)
            all_results.append(result)

            if verbose:
                if result.error:
                    print("❌ ERROR")
                    print(f"  {result.error}")
                else:
                    print(f"✅ {result.execution_time:.4f}s")
                    print(
                        f"  Memory: {result.memory_peak / 1024 / 1024:.2f} MB"
                    )
                    print(f"  Throughput: {result.throughput:,.0f} comb/s")

    return all_results


def print_summary(results):
    """Print summary comparison table"""
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)

    # Group by test name
    tests = {}
    for r in results:
        if r.name not in tests:
            tests[r.name] = []
        tests[r.name].append(r)

    for test_name, test_results in tests.items():
        print(f"\n{test_name}:")
        print(
            f"{'Implementation':<25} {'Time (s)':<12} {'Memory (MB)':<15} {'Throughput (c/s)':<20}"
        )
        print("-" * 80)

        for r in sorted(
            test_results,
            key=lambda x: x.execution_time if not x.error else float("inf"),
        ):
            if r.error:
                print(f"{r.impl_name:<25} ERROR: {r.error}")
            else:
                print(
                    f"{r.impl_name:<25} "
                    f"{r.execution_time:<12.4f} "
                    f"{r.memory_peak / 1024 / 1024:<15.2f} "
                    f"{r.throughput:<20,.0f}"
                )


def save_results(results, filename: str = "benchmark_results.txt"):
    """Save benchmark results to file"""
    from datetime import datetime

    with open(filename, "w") as f:
        f.write("WLGEN BENCHMARK RESULTS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Run date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")

        for r in results:
            f.write(str(r) + "\n\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("System Information:\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Platform: {sys.platform}\n")


if __name__ == "__main__":
    from datetime import datetime

    print("WLGEN Performance Benchmark Suite")
    print("=" * 80)

    results = run_benchmarks(verbose=True)
    print_summary(results)

    # Save results with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"wlgen/benchmarks/results_{timestamp}.txt"
    save_results(results, output_file)

    # Also save as latest
    latest_file = "wlgen/benchmarks/latest_results.txt"
    save_results(results, latest_file)

    print(f"\n📊 Results saved to: {output_file}")
    print(f"📊 Latest results: {latest_file}")
