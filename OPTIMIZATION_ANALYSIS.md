# Wordlist Generation Optimization Analysis

## Current Implementation Analysis

### 1. `gen_wordlist` (wlgen/core.py:4)

**Issues Identified:**
- **Unnecessary dictionary rebuilding** (lines 17-18): Creates new subset dictionary on each recursive call
- **Inefficient string concatenation** (line 20): Uses `+` operator which creates new string objects
- **Type inconsistency** (line 14): Returns string for base case but list for recursive case
- **Memory intensive**: Builds entire list in memory before returning

**Performance Impact:** Medium - Recursive overhead and dict rebuilding slow it down

### 2. `gen_wordlist_iter` (wlgen/core.py:25)

**Current State:** Already near-optimal

**Minor Optimization Opportunity:**
- Line 28: `sorted(set(i))` is redundant if input is already unique and sorted (as per docs)
- Could add a parameter to skip this step when input is known to be clean

**Performance Impact:** Low - itertools.product is C-optimized

### 3. `gen_words` (wlgen/core.py:33)

**Issues Identified:**
- **Repeated list comprehension** (line 50-52): Rebuilds string from positions on every yield
- **Recursive function overhead**: Python recursion is slower than iterative approaches
- **Position tracking**: Could use pre-allocated numpy array instead of Python list

**Performance Impact:** High - Slowest of the three implementations

## Proposed Optimizations

### Option 1: Optimized Pure Python Implementation

**Target:** Fix `gen_wordlist` issues
- Use list slicing instead of dict rebuilding
- Pre-allocate result list when size is calculable
- Ensure consistent return types

**Expected Speedup:** 1.5-2x faster

### Option 2: NumPy-based Implementation

**Approach:**
- Use NumPy's `meshgrid` or index broadcasting for Cartesian product
- Vectorized operations for character array manipulation
- Batch string conversion using numpy's char array operations

**Advantages:**
- 10-100x faster than pure Python for large charsets
- Memory efficient with lazy evaluation options
- No external dependencies beyond NumPy

**Use Cases:**
- Medium to large wordlists (1K - 10M combinations)
- When NumPy is already in the dependency stack

### Option 3: CUDA/CuPy Implementation

**Approach:**
- GPU-parallel string generation using CuPy
- Kernel-based character combination
- Batch processing to handle memory constraints

**Advantages:**
- 100-1000x faster for extremely large wordlists
- Massive parallelization (thousands of concurrent generations)
- Leverages modern GPU compute power

**Requirements:**
- NVIDIA GPU with CUDA support
- CuPy library
- Additional dependency overhead

**Use Cases:**
- Extremely large wordlists (10M+ combinations)
- Security research / password cracking scenarios
- Batch processing multiple wordlists

### Option 4: Multi-Processing Implementation

**Current Issue:** All implementations are single-threaded due to Python's GIL (Global Interpreter Lock)

**Approach:**
- Use `multiprocessing` to split charset ranges across CPU cores
- Each worker process generates a subset of the wordlist
- Combine results via queue or write directly to output

**Implementation Strategies:**

1. **Chunk-based Parallelization (Best for itertools.product)**
   ```python
   from multiprocessing import Pool
   from itertools import islice

   def gen_wordlist_parallel(charset, workers=None):
       # Split work into chunks
       # Each worker generates subset of combinations
       # Merge results or stream to output
   ```

2. **Range-based Splitting (Best for index-based generation)**
   - Calculate total combinations
   - Divide range by number of workers
   - Each worker generates combinations in its assigned range
   - Works well with NumPy implementation

**Advantages:**
- Linear speedup with CPU cores (2-16x on modern CPUs)
- No GIL contention (true parallelism)
- Works with existing implementations
- Compatible with Python 3.13 (no need to wait for 3.14 free-threading)

**Challenges:**
- Process spawning overhead for small wordlists
- Result ordering (may need to sort if order matters)
- Memory overhead from multiple processes

**Use Cases:**
- Medium to large wordlists where setup overhead < generation time
- Multi-core systems (4+ cores)
- When order doesn't matter or can be post-sorted

**Expected Speedup:** 2-8x on typical 4-8 core systems

### Option 5: Hybrid Approach

**Strategy:**
- Auto-select implementation based on problem size and available hardware
- Small (<1K): Use optimized pure Python (single-threaded)
- Medium (1K-100K): Use multiprocessing with optimized Python
- Large (100K-10M): Use NumPy with multiprocessing
- Extra Large (10M+): Use CUDA if available, fallback to NumPy + multiprocessing

## Implementation Plan

### Phase 1: Benchmarking (PRIORITY)
- [ ] Create benchmark script with various charset sizes
- [ ] Measure current implementation performance
- [ ] Establish baseline metrics (time, memory, throughput)

### Phase 2: Pure Python Optimizations
- [ ] Fix `gen_wordlist` dictionary rebuilding
- [ ] Optimize `gen_wordlist_iter` (remove redundant sorting)
- [ ] Optimize `gen_words` string building

### Phase 3: NumPy Implementation
- [ ] Implement `gen_wordlist_numpy` function
- [ ] Add as optional feature (soft dependency)
- [ ] Benchmark against existing implementations

### Phase 4: Multi-Processing Implementation
- [ ] Implement `gen_wordlist_parallel` using multiprocessing
- [ ] Support chunk-based and range-based splitting strategies
- [ ] Add worker count configuration (default: cpu_count())
- [ ] Benchmark single-core vs multi-core performance
- [ ] Document overhead thresholds for when to use parallelization

### Phase 5: CUDA Implementation (Optional)
- [ ] Implement `gen_wordlist_cuda` function
- [ ] Add as optional feature with graceful fallback
- [ ] Benchmark on GPU hardware
- [ ] Document GPU requirements

### Phase 6: Smart Dispatcher
- [ ] Create auto-selecting wrapper function
- [ ] Size-based algorithm selection
- [ ] Hardware detection (NumPy/CUDA availability, CPU cores)
- [ ] Auto-enable multiprocessing for suitable workloads

## Testing Strategy

### Correctness Testing
- All implementations must produce identical output
- Use existing test suite as validation
- Test edge cases (empty sets, single char, unicode)

### Performance Testing
- Small: charset with 3-5 positions, 5-10 chars each (~1K-10K combinations)
- Medium: charset with 5-8 positions, 10-20 chars each (~100K-1M combinations)
- Large: charset with 8-12 positions, 20+ chars each (~10M+ combinations)

### Metrics to Track
- Execution time (wall clock)
- Memory usage (peak RSS)
- Throughput (combinations/second)
- First result latency (for generators)

## Backward Compatibility

All optimizations must:
- Maintain existing API signatures
- Preserve existing behavior
- Keep current implementations available
- Add new implementations as optional functions

## Dependencies Consideration

### Current: Zero dependencies
### With NumPy: `numpy` (widely used, minimal overhead)
### With CUDA: `cupy` (heavy dependency, GPU required)

**Strategy:** Make both optional with graceful degradation
```python
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import cupy as cp
    HAS_CUDA = True
except ImportError:
    HAS_CUDA = False
```
