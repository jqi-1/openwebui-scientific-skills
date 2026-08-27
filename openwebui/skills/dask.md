---
name: dask
description: Distributed computing for larger-than-RAM pandas/NumPy workflows. Use when you need to scale existing pandas/NumPy code beyond memory or across clusters. Best for parallel file processing, distributed ML, integration with existing pandas code. For out-of-core analytics on single machine use vaex; for in-memory speed use polars.
---

# Dask

## Overview

Dask is a Python library for parallel and distributed computing that enables three critical capabilities:
- **Larger-than-memory execution** on single machines for data exceeding available RAM
- **Parallel processing** for improved computational speed across multiple cores
- **Distributed computation** supporting terabyte-scale datasets across multiple machines

Dask scales from laptops (processing ~100 GiB) to clusters (processing ~100 TiB) while maintaining familiar Python APIs.

**Current upstream:** dask **2026.3.0** (PyPI, March 2026). Docs: [docs.dask.org](https://docs.dask.org/en/stable/). Since **2025.1.0**, the expression-based DataFrame API with query planning is the only implementation — do not install `dask-expr` separately or set `dataframe.query-planning: False`.

## Quick Start

### Installation

```bash
uv pip install "dask>=2025.1"
```

For a typical pandas/NumPy workflow with the distributed scheduler and dashboard:

```bash
uv pip install "dask[complete]"
```

Remote object storage (S3, GCS, Azure):

```bash
uv pip install s3fs    # s3:// paths
uv pip install gcsfs   # gs:// paths
```

Requires **Python 3.10+** (3.9 support dropped in 2024.12). DataFrame I/O requires **PyArrow 16+** (as of dask 2026.1.2).

## When to Use This Skill

This skill should be used when:
- Process datasets that exceed available RAM
- Scale pandas or NumPy operations to larger datasets
- Parallelize computations for performance improvements
- Process multiple files efficiently (CSVs, Parquet, JSON, text logs)
- Build custom parallel workflows with task dependencies
- Distribute workloads across multiple cores or machines

## Core Capabilities

Dask provides five main components, each suited to different use cases:

### 1. DataFrames - Parallel Pandas Operations

**Purpose**: Scale pandas operations to larger datasets through parallel processing.

**When to Use**:
- Tabular data exceeds available RAM
- Need to process multiple CSV/Parquet files together
- Pandas operations are slow and need parallelization
- Scaling from pandas prototype to production

**Reference Documentation**: For comprehensive guidance on Dask DataFrames, refer to `references/dataframes.md` which includes:
- Reading data (single files, multiple files, glob patterns)
- Common operations (filtering, groupby, joins, aggregations)
- Custom operations with `map_partitions`
- Performance optimization tips
- Common patterns (ETL, time series, multi-file processing)

**Quick Example**:
```python
import dask.dataframe as dd

# Read multiple files as single DataFrame
ddf = dd.read_csv('data/2024-*.csv')

# Operations are lazy until compute()
filtered = ddf[ddf['value'] > 100]
result = filtered.groupby('category').mean().compute()
```

**Key Points**:
- Operations are lazy (build task graph) until `.compute()` called
- Use `map_partitions` for efficient custom operations
- Convert to DataFrame early when working with structured data from other sources

### 2. Arrays - Parallel NumPy Operations

**Purpose**: Extend NumPy capabilities to datasets larger than memory using blocked algorithms.

**When to Use**:
- Arrays exceed available RAM
- NumPy operations need parallelization
- Working with scientific datasets (HDF5, Zarr, NetCDF)
- Need parallel linear algebra or array operations

**Reference Documentation**: For comprehensive guidance on Dask Arrays, refer to `references/arrays.md` which includes:
- Creating arrays (from NumPy, random, from disk)
- Chunking strategies and optimization
- Common operations (arithmetic, reductions, linear algebra)
- Custom operations with `map_blocks`
- Integration with HDF5, Zarr, and XArray

**Quick Example**:
```python
import dask.array as da

# Create large array with chunks
x = da.random.random((100000, 100000), chunks=(10000, 10000))

# Operations are lazy
y = x + 100
z = y.mean(axis=0)

# Compute result
result = z.compute()
```

**Key Points**:
- Chunk size is critical (aim for ~100 MB per chunk)
- Operations work on chunks in parallel
- Rechunk data when needed for efficient operations
- Use `map_blocks` for operations not available in Dask

### 3. Bags - Parallel Processing of Unstructured Data

**Purpose**: Process unstructured or semi-structured data (text, JSON, logs) with functional operations.

**When to Use**:
- Processing text files, logs, or JSON records
- Data cleaning and ETL before structured analysis
- Working with Python objects that don't fit array/dataframe formats
- Need memory-efficient streaming processing

**Reference Documentation**: For comprehensive guidance on Dask Bags, refer to `references/bags.md` which includes:
- Reading text and JSON files
- Functional operations (map, filter, fold, groupby)
- Converting to DataFrames
- Common patterns (log analysis, JSON processing, text processing)
- Performance considerations

**Quick Example**:
```python
import dask.bag as db
import json

# Read and parse JSON files
bag = db.read_text('logs/*.json').map(json.loads)

# Filter and transform
valid = bag.filter(lambda x: x['status'] == 'valid')
processed = valid.map(lambda x: {'id': x['id'], 'value': x['value']})

# Convert to DataFrame for analysis
ddf = processed.to_dataframe()
```

**Key Points**:
- Use for initial data cleaning, then convert to DataFrame/Array
- Use `foldby` instead of `groupby` for better performance
- Operations are streaming and memory-efficient
- Convert to structured formats (DataFrame) for complex operations

### 4. Futures - Task-Based Parallelization

**Purpose**: Build custom parallel workflows with fine-grained control over task execution and dependencies.

**When to Use**:
- Building dynamic, evolving workflows
- Need immediate task execution (not lazy)
- Computations depend on runtime conditions
- Implementing custom parallel algorithms
- Need stateful computations

**Reference Documentation**: For comprehensive guidance on Dask Futures, refer to `references/futures.md` which includes:
- Setting up distributed client
- Submitting tasks and working with futures
- Task dependencies and data movement
- Advanced coordination (queues, locks, events, actors)
- Common patterns (parameter sweeps, dynamic tasks, iterative algorithms)

**Quick Example**:
```python
from dask.distributed import Client

client = Client()  # Create local cluster

# Submit tasks (executes immediately)
def process(x):
    return x ** 2

futures = client.map(process, range(100))

# Gather results
results = client.gather(futures)

client.close()
```

**Key Points**:
- Requires distributed client (even for single machine)
- Tasks execute immediately when submitted
- Pre-scatter large data to avoid repeated transfers
- ~1ms overhead per task (not suitable for millions of tiny tasks)
- Use actors for stateful workflows

### 5. Schedulers - Execution Backends

**Purpose**: Control how and where Dask tasks execute (threads, processes, distributed).

**When to Choose Scheduler**:
- **Threads** (default): NumPy/Pandas operations, GIL-releasing libraries, shared memory benefit
- **Processes**: Pure Python code, text processing, GIL-bound operations
- **Synchronous**: Debugging with pdb, profiling, understanding errors
- **Distributed**: Need dashboard, multi-machine clusters, advanced features

**Reference Documentation**: For comprehensive guidance on Dask Schedulers, refer to `references/schedulers.md` which includes:
- Detailed scheduler descriptions and characteristics
- Configuration methods (global, context manager, per-compute)
- Performance considerations and overhead
- Common patterns and troubleshooting
- Thread configuration for optimal performance

**Quick Example**:
```python
import dask
import dask.dataframe as dd

# Use threads for DataFrame (default, good for numeric)
ddf = dd.read_csv('data.csv')
result1 = ddf.mean().compute()  # Uses threads

# Use processes for Python-heavy work
import dask.bag as db
bag = db.read_text('logs/*.txt')
result2 = bag.map(python_function).compute(scheduler='processes')

# Use synchronous for debugging
dask.config.set(scheduler='synchronous')
result3 = problematic_computation.compute()  # Can use pdb

# Use distributed for monitoring and scaling
from dask.distributed import Client
client = Client()
result4 = computation.compute()  # Uses distributed with dashboard
```

**Key Points**:
- Threads: Lowest overhead (~10 µs/task), best for numeric work
- Processes: Avoids GIL (~10 ms/task), best for Python work
- Distributed: Monitoring dashboard (~1 ms/task), scales to clusters
- Can switch schedulers per computation or globally

## Best Practices

For comprehensive performance optimization guidance, memory management strategies, and common pitfalls to avoid, refer to `references/best-practices.md`. Key principles include:

### Start with Simpler Solutions
Before using Dask, explore:
- Better algorithms
- Efficient file formats (Parquet instead of CSV)
- Compiled code (Numba, Cython)
- Data sampling

### Critical Performance Rules

**1. Don't Load Data Locally Then Hand to Dask**
```python
# Wrong: Loads all data in memory first
import pandas as pd
df = pd.read_csv('large.csv')
ddf = dd.from_pandas(df, npartitions=10)

# Correct: Let Dask handle loading
import dask.dataframe as dd
ddf = dd.read_csv('large.csv')
```

**2. Avoid Repeated compute() Calls**
```python
# Wrong: Each compute is separate
for item in items:
    result = dask_computation(item).compute()

# Correct: Single compute for all
computations = [dask_computation(item) for item in items]
results = dask.compute(*computations)
```

**3. Don't Build Excessively Large Task Graphs**
- Increase chunk sizes if millions of tasks
- Use `map_partitions`/`map_blocks` to fuse operations
- Check task graph size: `len(ddf.__dask_graph__())`

**4. Choose Appropriate Chunk Sizes**
- Target: ~100 MB per chunk (or 10 chunks per core in worker memory)
- Too large: Memory overflow
- Too small: Scheduling overhead

**5. Use the Dashboard**
```python
from dask.distributed import Client
client = Client()
print(client.dashboard_link)  # Monitor performance, identify bottlenecks
```

## Common Workflow Patterns

### ETL Pipeline
```python
import dask.dataframe as dd

# Extract: Read data
ddf = dd.read_csv('raw_data/*.csv')

# Transform: Clean and process
ddf = ddf[ddf['status'] == 'valid']
ddf['amount'] = ddf['amount'].astype('float64')
ddf = ddf.dropna(subset=['important_col'])

# Load: Aggregate and save
summary = ddf.groupby('category').agg({'amount': ['sum', 'mean']})
summary.to_parquet('output/summary.parquet')
```

### Unstructured to Structured Pipeline
```python
import dask.bag as db
import json

# Start with Bag for unstructured data
bag = db.read_text('logs/*.json').map(json.loads)
bag = bag.filter(lambda x: x['status'] == 'valid')

# Convert to DataFrame for structured analysis
ddf = bag.to_dataframe()
result = ddf.groupby('category').mean().compute()
```

### Large-Scale Array Computation
```python
import dask.array as da

# Load or create large array
x = da.from_zarr('large_dataset.zarr')

# Process in chunks
normalized = (x - x.mean()) / x.std()

# Save result (use mode= for overwrite; zarr_array_kwargs for compression)
da.to_zarr(normalized, 'normalized.zarr', mode='w')
```

### Custom Parallel Workflow
```python
from dask.distributed import Client

client = Client()

# Scatter large dataset once
data = client.scatter(large_dataset)

# Process in parallel with dependencies
futures = []
for param in parameters:
    future = client.submit(process, data, param)
    futures.append(future)

# Gather results
results = client.gather(futures)
```

## Selecting the Right Component

Use this decision guide to choose the appropriate Dask component:

**Data Type**:
- Tabular data → **DataFrames**
- Numeric arrays → **Arrays**
- Text/JSON/logs → **Bags** (then convert to DataFrame)
- Custom Python objects → **Bags** or **Futures**

**Operation Type**:
- Standard pandas operations → **DataFrames**
- Standard NumPy operations → **Arrays**
- Custom parallel tasks → **Futures**
- Text processing/ETL → **Bags**

**Control Level**:
- High-level, automatic → **DataFrames/Arrays**
- Low-level, manual → **Futures**

**Workflow Type**:
- Static computation graph → **DataFrames/Arrays/Bags**
- Dynamic, evolving → **Futures**

## Integration Considerations

### File Formats
- **Efficient**: Parquet, HDF5, Zarr (columnar, compressed, parallel-friendly)
- **Compatible but slower**: CSV (use for initial ingestion only)
- **For Arrays**: HDF5, Zarr, NetCDF

### Conversion Between Collections
```python
# Bag → DataFrame
ddf = bag.to_dataframe()

# DataFrame → Array (for numeric data)
arr = ddf.to_dask_array(lengths=True)

# Array → DataFrame
ddf = dd.from_dask_array(arr, columns=['col1', 'col2'])
```

### With Other Libraries
- **XArray**: Wraps Dask arrays with labeled dimensions (geospatial, imaging)
- **Dask-ML**: Machine learning with scikit-learn compatible APIs
- **Distributed**: Advanced cluster management and monitoring

## Debugging and Development

### Iterative Development Workflow

1. **Test on small data with synchronous scheduler**:
```python
dask.config.set(scheduler='synchronous')
result = computation.compute()  # Can use pdb, easy debugging
```

2. **Validate with threads on sample**:
```python
sample = ddf.head(1000)  # Small sample
# Test logic, then scale to full dataset
```

3. **Scale with distributed for monitoring**:
```python
from dask.distributed import Client
client = Client()
print(client.dashboard_link)  # Monitor performance
result = computation.compute()
```

### Common Issues

**Memory Errors**:
- Decrease chunk sizes
- Use `persist()` strategically and delete when done
- Check for memory leaks in custom functions

**Slow Start**:
- Task graph too large (increase chunk sizes)
- Use `map_partitions` or `map_blocks` to reduce tasks

**Poor Parallelization**:
- Chunks too large (increase number of partitions)
- Using threads with Python code (switch to processes)
- Data dependencies preventing parallelism

## Reference Files

All reference documentation files can be read as needed for detailed information:

- `references/dataframes.md` - Complete Dask DataFrame guide
- `references/arrays.md` - Complete Dask Array guide
- `references/bags.md` - Complete Dask Bag guide
- `references/futures.md` - Complete Dask Futures and distributed computing guide
- `references/schedulers.md` - Complete scheduler selection and configuration guide
- `references/best-practices.md` - Comprehensive performance optimization and troubleshooting

Load these files when users need detailed information about specific Dask components, operations, or patterns beyond the quick guidance provided here.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/dask/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/arrays.md`

# Dask Arrays

## Overview

Dask Array implements NumPy's ndarray interface using blocked algorithms. It coordinates many NumPy arrays arranged into a grid to enable computation on datasets larger than available memory, utilizing parallelism across multiple cores.

## Core Concept

A Dask Array is divided into chunks (blocks):
- Each chunk is a regular NumPy array
- Operations are applied to each chunk in parallel
- Results are combined automatically
- Enables out-of-core computation (data larger than RAM)

## Key Capabilities

### What Dask Arrays Support

**Mathematical Operations**:
- Arithmetic operations (+, -, *, /)
- Scalar functions (exponentials, logarithms, trigonometric)
- Element-wise operations

**Reductions**:
- `sum()`, `mean()`, `std()`, `var()`
- Reductions along specified axes
- `min()`, `max()`, `argmin()`, `argmax()`

**Linear Algebra**:
- Tensor contractions
- Dot products and matrix multiplication
- Some decompositions (SVD, QR)

**Data Manipulation**:
- Transposition
- Slicing (standard and fancy indexing)
- Reshaping
- Concatenation and stacking

**Array Protocols**:
- Universal functions (ufuncs)
- NumPy protocols for interoperability

## When to Use Dask Arrays

**Use Dask Arrays When**:
- Arrays exceed available RAM
- Computation can be parallelized across chunks
- Working with NumPy-style numerical operations
- Need to scale NumPy code to larger datasets

**Stick with NumPy When**:
- Arrays fit comfortably in memory
- Operations require global views of data
- Using specialized functions not available in Dask
- Performance is adequate with NumPy alone

## Important Limitations

Dask Arrays intentionally don't implement certain NumPy features:

**Not Implemented**:
- Most `np.linalg` functions (only basic operations available)
- Operations difficult to parallelize (like full sorting)
- Memory-inefficient operations (converting to lists, iterating via loops)
- Many specialized functions (driven by community needs)

**Workarounds**: For unsupported operations, consider using `map_blocks` with custom NumPy code.

## Creating Dask Arrays

### From NumPy Arrays
```python
import dask.array as da
import numpy as np

# Create from NumPy array with specified chunks
x = np.arange(10000)
dx = da.from_array(x, chunks=1000)  # Creates 10 chunks of 1000 elements each
```

### Random Arrays
```python
# Create random array with specified chunks
x = da.random.random((10000, 10000), chunks=(1000, 1000))

# Other random functions
x = da.random.normal(10, 0.1, size=(10000, 10000), chunks=(1000, 1000))
```

### Zeros, Ones, and Empty
```python
# Create arrays filled with constants
zeros = da.zeros((10000, 10000), chunks=(1000, 1000))
ones = da.ones((10000, 10000), chunks=(1000, 1000))
empty = da.empty((10000, 10000), chunks=(1000, 1000))
```

### From Functions
```python
# Create array from function
def create_block(block_id):
    return np.random.random((1000, 1000)) * block_id[0]

x = da.from_delayed(
    [[dask.delayed(create_block)((i, j)) for j in range(10)] for i in range(10)],
    shape=(10000, 10000),
    dtype=float
)
```

### From Disk
```python
# Load from HDF5
import h5py
f = h5py.File('myfile.hdf5', mode='r')
x = da.from_array(f['/data'], chunks=(1000, 1000))

# Load from Zarr
import zarr
z = zarr.open('myfile.zarr', mode='r')
x = da.from_array(z, chunks=(1000, 1000))
```

## Common Operations

### Arithmetic Operations
```python
import dask.array as da

x = da.random.random((10000, 10000), chunks=(1000, 1000))
y = da.random.random((10000, 10000), chunks=(1000, 1000))

# Element-wise operations (lazy)
z = x + y
z = x * y
z = da.exp(x)
z = da.log(y)

# Compute result
result = z.compute()
```

### Reductions
```python
# Reductions along axes
total = x.sum().compute()
mean = x.mean().compute()
std = x.std().compute()

# Reduction along specific axis
row_means = x.mean(axis=1).compute()
col_sums = x.sum(axis=0).compute()
```

### Slicing and Indexing
```python
# Standard slicing (returns Dask Array)
subset = x[1000:5000, 2000:8000]

# Fancy indexing
indices = [0, 5, 10, 15]
selected = x[indices, :]

# Boolean indexing
mask = x > 0.5
filtered = x[mask]
```

### Matrix Operations
```python
# Matrix multiplication
A = da.random.random((10000, 5000), chunks=(1000, 1000))
B = da.random.random((5000, 8000), chunks=(1000, 1000))
C = da.matmul(A, B)
result = C.compute()

# Dot product
dot_product = da.dot(A, B)

# Transpose
AT = A.T
```

### Linear Algebra
```python
# SVD (Singular Value Decomposition)
U, s, Vt = da.linalg.svd(A)
U_computed, s_computed, Vt_computed = dask.compute(U, s, Vt)

# QR decomposition
Q, R = da.linalg.qr(A)
Q_computed, R_computed = dask.compute(Q, R)

# Note: Only some linalg operations are available
```

### Reshaping and Manipulation
```python
# Reshape
x = da.random.random((10000, 10000), chunks=(1000, 1000))
reshaped = x.reshape(5000, 20000)

# Transpose
transposed = x.T

# Concatenate
x1 = da.random.random((5000, 10000), chunks=(1000, 1000))
x2 = da.random.random((5000, 10000), chunks=(1000, 1000))
combined = da.concatenate([x1, x2], axis=0)

# Stack
stacked = da.stack([x1, x2], axis=0)
```

## Chunking Strategy

Chunking is critical for Dask Array performance.

### Chunk Size Guidelines

**Good Chunk Sizes**:
- Each chunk: ~10-100 MB (compressed)
- ~1 million elements per chunk for numeric data
- Balance between parallelism and overhead

**Example Calculation**:
```python
# For float64 data (8 bytes per element)
# Target 100 MB chunks: 100 MB / 8 bytes = 12.5M elements

# For 2D array (10000, 10000):
x = da.random.random((10000, 10000), chunks=(1000, 1000))  # ~8 MB per chunk
```

### Viewing Chunk Structure
```python
# Check chunks
print(x.chunks)  # ((1000, 1000, ...), (1000, 1000, ...))

# Number of chunks
print(x.npartitions)

# Chunk sizes in bytes
print(x.nbytes / x.npartitions)
```

### Rechunking
```python
# Change chunk sizes
x = da.random.random((10000, 10000), chunks=(500, 500))
x_rechunked = x.rechunk((2000, 2000))

# Rechunk specific dimension
x_rechunked = x.rechunk({0: 2000, 1: 'auto'})
```

## Custom Operations with map_blocks

For operations not available in Dask, use `map_blocks`:

```python
import dask.array as da
import numpy as np

def custom_function(block):
    # Apply custom NumPy operation
    return np.fft.fft2(block)

x = da.random.random((10000, 10000), chunks=(1000, 1000))
result = da.map_blocks(custom_function, x, dtype=x.dtype)

# Compute
output = result.compute()
```

### map_blocks with Different Output Shape
```python
def reduction_function(block):
    # Returns scalar for each block
    return np.array([block.mean()])

result = da.map_blocks(
    reduction_function,
    x,
    dtype='float64',
    drop_axis=[0, 1],  # Output has no axes from input
    new_axis=0,        # Output has new axis
    chunks=(1,)        # One element per block
)
```

## Lazy Evaluation and Computation

### Lazy Operations
```python
# All operations are lazy (instant, no computation)
x = da.random.random((10000, 10000), chunks=(1000, 1000))
y = x + 100
z = y.mean(axis=0)
result = z * 2

# Nothing computed yet, just task graph built
```

### Triggering Computation
```python
# Compute single result
final = result.compute()

# Compute multiple results efficiently
result1, result2 = dask.compute(operation1, operation2)
```

### Persist in Memory
```python
# Keep intermediate results in memory
x_cached = x.persist()

# Reuse cached results
y1 = (x_cached + 10).compute()
y2 = (x_cached * 2).compute()
```

## Saving Results

### To NumPy
```python
# Convert to NumPy (loads all in memory)
numpy_array = dask_array.compute()
```

### To Disk
```python
# Save to Zarr (dask 2026.1+: use mode= and zarr_array_kwargs= for zarr-python 3)
da.to_zarr(x, 'output.zarr', mode='w')

# Save to HDF5
import h5py
with h5py.File('output.hdf5', mode='w') as f:
    dset = f.create_dataset('/data', shape=x.shape, dtype=x.dtype)
    da.store(x, dset)
```

## Performance Considerations

### Efficient Operations
- Element-wise operations: Very efficient
- Reductions with parallelizable operations: Efficient
- Slicing along chunk boundaries: Efficient
- Matrix operations with good chunk alignment: Efficient

### Expensive Operations
- Slicing across many chunks: Requires data movement
- Operations requiring global sorting: Not well supported
- Extremely irregular access patterns: Poor performance
- Operations with poor chunk alignment: Requires rechunking

### Optimization Tips

**1. Choose Good Chunk Sizes**
```python
# Aim for balanced chunks
# Good: ~100 MB per chunk
x = da.random.random((100000, 10000), chunks=(10000, 10000))
```

**2. Align Chunks for Operations**
```python
# Make sure chunks align for operations
x = da.random.random((10000, 10000), chunks=(1000, 1000))
y = da.random.random((10000, 10000), chunks=(1000, 1000))  # Aligned
z = x + y  # Efficient
```

**3. Use Appropriate Scheduler**
```python
# Arrays work well with threaded scheduler (default)
# Shared memory access is efficient
result = x.compute()  # Uses threads by default
```

**4. Minimize Data Transfer**
```python
# Better: Compute on each chunk, then transfer results
means = x.mean(axis=1).compute()  # Transfers less data

# Worse: Transfer all data then compute
x_numpy = x.compute()
means = x_numpy.mean(axis=1)  # Transfers more data
```

## Common Patterns

### Image Processing
```python
import dask.array as da

# Load large image stack
images = da.from_zarr('images.zarr')

# Apply filtering
def apply_gaussian(block):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(block, sigma=2)

filtered = da.map_blocks(apply_gaussian, images, dtype=images.dtype)

# Compute statistics
mean_intensity = filtered.mean().compute()
```

### Scientific Computing
```python
# Large-scale numerical simulation
x = da.random.random((100000, 100000), chunks=(10000, 10000))

# Apply iterative computation
for i in range(num_iterations):
    x = da.exp(-x) * da.sin(x)
    x = x.persist()  # Keep in memory for next iteration

# Final result
result = x.compute()
```

### Data Analysis
```python
# Load large dataset
data = da.from_zarr('measurements.zarr')

# Compute statistics
mean = data.mean(axis=0)
std = data.std(axis=0)
normalized = (data - mean) / std

# Save normalized data
da.to_zarr(normalized, 'normalized.zarr')
```

## Integration with Other Tools

### XArray
```python
import xarray as xr
import dask.array as da

# XArray wraps Dask arrays with labeled dimensions
data = da.random.random((1000, 2000, 3000), chunks=(100, 200, 300))
dataset = xr.DataArray(
    data,
    dims=['time', 'y', 'x'],
    coords={'time': range(1000), 'y': range(2000), 'x': range(3000)}
)
```

### Scikit-learn (via Dask-ML)
```python
# Some scikit-learn compatible operations
from dask_ml.preprocessing import StandardScaler

X = da.random.random((10000, 100), chunks=(1000, 100))
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

## Debugging Tips

### Visualize Task Graph
```python
# Visualize computation graph (for small arrays)
x = da.random.random((100, 100), chunks=(10, 10))
y = x + 1
y.visualize(filename='graph.png')
```

### Check Array Properties
```python
# Inspect before computing
print(f"Shape: {x.shape}")
print(f"Dtype: {x.dtype}")
print(f"Chunks: {x.chunks}")
print(f"Number of tasks: {len(x.__dask_graph__())}")
```

### Test on Small Arrays First
```python
# Test logic on small array
small_x = da.random.random((100, 100), chunks=(50, 50))
result_small = computation(small_x).compute()

# Validate, then scale
large_x = da.random.random((100000, 100000), chunks=(10000, 10000))
result_large = computation(large_x).compute()
```

### `references/bags.md`

# Dask Bags

## Overview

Dask Bag implements functional operations including `map`, `filter`, `fold`, and `groupby` on generic Python objects. It processes data in parallel while maintaining a small memory footprint through Python iterators. Bags function as "a parallel version of PyToolz or a Pythonic version of the PySpark RDD."

## Core Concept

A Dask Bag is a collection of Python objects distributed across partitions:
- Each partition contains generic Python objects
- Operations use functional programming patterns
- Processing uses streaming/iterators for memory efficiency
- Ideal for unstructured or semi-structured data

## Key Capabilities

### Functional Operations
- `map`: Transform each element
- `filter`: Select elements based on condition
- `fold`: Reduce elements with combining function
- `groupby`: Group elements by key
- `pluck`: Extract fields from records
- `flatten`: Flatten nested structures

### Use Cases
- Text processing and log analysis
- JSON record processing
- ETL on unstructured data
- Data cleaning before structured analysis

## When to Use Dask Bags

**Use Bags When**:
- Working with general Python objects requiring flexible computation
- Data doesn't fit structured array or tabular formats
- Processing text, JSON, or custom Python objects
- Initial data cleaning and ETL is needed
- Memory-efficient streaming is important

**Use Other Collections When**:
- Data is structured (use DataFrames instead)
- Numeric computing (use Arrays instead)
- Operations require complex groupby or shuffles (use DataFrames)

**Key Recommendation**: Use Bag to clean and process data, then transform it into an array or DataFrame before embarking on more complex operations that require shuffle steps.

## Important Limitations

Bags sacrifice performance for generality:
- Rely on multiprocessing scheduling (not threads)
- Remain immutable (create new bags for changes)
- Operate slower than array/DataFrame equivalents
- Handle `groupby` inefficiently (use `foldby` when possible)
- Operations requiring substantial inter-worker communication are slow

## Creating Bags

### From Sequences
```python
import dask.bag as db

# From Python list
bag = db.from_sequence([1, 2, 3, 4, 5], partition_size=2)

# From range
bag = db.from_sequence(range(10000), partition_size=1000)
```

### From Text Files
```python
# Single file
bag = db.read_text('data.txt')

# Multiple files with glob
bag = db.read_text('data/*.txt')

# With encoding
bag = db.read_text('data/*.txt', encoding='utf-8')

# Custom line processing
bag = db.read_text('logs/*.log', blocksize='64MB')
```

### From Delayed Objects
```python
import dask

@dask.delayed
def load_data(filename):
    with open(filename) as f:
        return [line.strip() for line in f]

files = ['file1.txt', 'file2.txt', 'file3.txt']
partitions = [load_data(f) for f in files]
bag = db.from_delayed(partitions)
```

### From Custom Sources
```python
# From any iterable-producing function
def read_json_files():
    import json
    for filename in glob.glob('data/*.json'):
        with open(filename) as f:
            yield json.load(f)

# Create bag from generator
bag = db.from_sequence(read_json_files(), partition_size=10)
```

## Common Operations

### Map (Transform)
```python
import dask.bag as db

bag = db.read_text('data/*.json')

# Parse JSON
import json
parsed = bag.map(json.loads)

# Extract field
values = parsed.map(lambda x: x['value'])

# Complex transformation
def process_record(record):
    return {
        'id': record['id'],
        'value': record['value'] * 2,
        'category': record.get('category', 'unknown')
    }

processed = parsed.map(process_record)
```

### Filter
```python
# Filter by condition
valid = parsed.filter(lambda x: x['status'] == 'valid')

# Multiple conditions
filtered = parsed.filter(lambda x: x['value'] > 100 and x['year'] == 2024)

# Filter with custom function
def is_valid_record(record):
    return record.get('status') == 'valid' and record.get('value') is not None

valid_records = parsed.filter(is_valid_record)
```

### Pluck (Extract Fields)
```python
# Extract single field
ids = parsed.pluck('id')

# Extract multiple fields (creates tuples)
key_pairs = parsed.pluck(['id', 'value'])
```

### Flatten
```python
# Flatten nested lists
nested = db.from_sequence([[1, 2], [3, 4], [5, 6]])
flat = nested.flatten()  # [1, 2, 3, 4, 5, 6]

# Flatten after map
bag = db.read_text('data/*.txt')
words = bag.map(str.split).flatten()  # All words from all files
```

### GroupBy (Expensive)
```python
# Group by key (requires shuffle)
grouped = parsed.groupby(lambda x: x['category'])

# Aggregate after grouping
counts = grouped.map(lambda key_items: (key_items[0], len(list(key_items[1]))))
result = counts.compute()
```

### FoldBy (Preferred for Aggregations)
```python
# FoldBy is more efficient than groupby for aggregations
def add(acc, item):
    return acc + item['value']

def combine(acc1, acc2):
    return acc1 + acc2

# Sum values by category
sums = parsed.foldby(
    key='category',
    binop=add,
    initial=0,
    combine=combine
)

result = sums.compute()
```

### Reductions
```python
# Count elements
count = bag.count().compute()

# Get all distinct values (requires memory)
distinct = bag.distinct().compute()

# Take first n elements
first_ten = bag.take(10)

# Fold/reduce
total = bag.fold(
    lambda acc, x: acc + x['value'],
    initial=0,
    combine=lambda a, b: a + b
).compute()
```

## Converting to Other Collections

### To DataFrame
```python
import dask.bag as db
import dask.dataframe as dd

# Bag of dictionaries
bag = db.read_text('data/*.json').map(json.loads)

# Convert to DataFrame
ddf = bag.to_dataframe()

# With explicit columns
ddf = bag.to_dataframe(meta={'id': int, 'value': float, 'category': str})
```

### To List/Compute
```python
# Compute to Python list (loads all in memory)
result = bag.compute()

# Take sample
sample = bag.take(100)
```

## Common Patterns

### JSON Processing
```python
import dask.bag as db
import json

# Read and parse JSON files
bag = db.read_text('logs/*.json')
parsed = bag.map(json.loads)

# Filter valid records
valid = parsed.filter(lambda x: x.get('status') == 'success')

# Extract relevant fields
processed = valid.map(lambda x: {
    'user_id': x['user']['id'],
    'timestamp': x['timestamp'],
    'value': x['metrics']['value']
})

# Convert to DataFrame for analysis
ddf = processed.to_dataframe()

# Analyze
summary = ddf.groupby('user_id')['value'].mean().compute()
```

### Log Analysis
```python
# Read log files
logs = db.read_text('logs/*.log')

# Parse log lines
def parse_log_line(line):
    parts = line.split(' ')
    return {
        'timestamp': parts[0],
        'level': parts[1],
        'message': ' '.join(parts[2:])
    }

parsed_logs = logs.map(parse_log_line)

# Filter errors
errors = parsed_logs.filter(lambda x: x['level'] == 'ERROR')

# Count by message pattern
error_counts = errors.foldby(
    key='message',
    binop=lambda acc, x: acc + 1,
    initial=0,
    combine=lambda a, b: a + b
)

result = error_counts.compute()
```

### Text Processing
```python
# Read text files
text = db.read_text('documents/*.txt')

# Split into words
words = text.map(str.lower).map(str.split).flatten()

# Count word frequencies
def increment(acc, word):
    return acc + 1

def combine_counts(a, b):
    return a + b

word_counts = words.foldby(
    key=lambda word: word,
    binop=increment,
    initial=0,
    combine=combine_counts
)

# Get top words
top_words = word_counts.compute()
sorted_words = sorted(top_words, key=lambda x: x[1], reverse=True)[:100]
```

### Data Cleaning Pipeline
```python
import dask.bag as db
import json

# Read raw data
raw = db.read_text('raw_data/*.json').map(json.loads)

# Validation function
def is_valid(record):
    required_fields = ['id', 'timestamp', 'value']
    return all(field in record for field in required_fields)

# Cleaning function
def clean_record(record):
    return {
        'id': int(record['id']),
        'timestamp': record['timestamp'],
        'value': float(record['value']),
        'category': record.get('category', 'unknown'),
        'tags': record.get('tags', [])
    }

# Pipeline
cleaned = (raw
    .filter(is_valid)
    .map(clean_record)
    .filter(lambda x: x['value'] > 0)
)

# Convert to DataFrame
ddf = cleaned.to_dataframe()

# Save cleaned data
ddf.to_parquet('cleaned_data/')
```

## Performance Considerations

### Efficient Operations
- Map, filter, pluck: Very efficient (streaming)
- Flatten: Efficient
- FoldBy with good key distribution: Reasonable
- Take and head: Efficient (only processes needed partitions)

### Expensive Operations
- GroupBy: Requires shuffle, can be slow
- Distinct: Requires collecting all unique values
- Operations requiring full data materialization

### Optimization Tips

**1. Use FoldBy Instead of GroupBy**
```python
# Better: Use foldby for aggregations
result = bag.foldby(key='category', binop=add, initial=0, combine=sum)

# Worse: GroupBy then reduce
result = bag.groupby('category').map(lambda x: (x[0], sum(x[1])))
```

**2. Convert to DataFrame Early**
```python
# For structured operations, convert to DataFrame
bag = db.read_text('data/*.json').map(json.loads)
bag = bag.filter(lambda x: x['status'] == 'valid')
ddf = bag.to_dataframe()  # Now use efficient DataFrame operations
```

**3. Control Partition Size**
```python
# Balance between too many and too few partitions
bag = db.read_text('data/*.txt', blocksize='64MB')  # Reasonable partition size
```

**4. Use Lazy Evaluation**
```python
# Chain operations before computing
result = (bag
    .map(process1)
    .filter(condition)
    .map(process2)
    .compute()  # Single compute at the end
)
```

## Debugging Tips

### Inspect Partitions
```python
# Get number of partitions
print(bag.npartitions)

# Take sample
sample = bag.take(10)
print(sample)
```

### Validate on Small Data
```python
# Test logic on small subset
small_bag = db.from_sequence(sample_data, partition_size=10)
result = process_pipeline(small_bag).compute()
# Validate results, then scale
```

### Check Intermediate Results
```python
# Compute intermediate steps to debug
step1 = bag.map(parse).take(5)
print("After parsing:", step1)

step2 = bag.map(parse).filter(validate).take(5)
print("After filtering:", step2)
```

## Memory Management

Bags are designed for memory-efficient processing:

```python
# Streaming processing - doesn't load all in memory
bag = db.read_text('huge_file.txt')  # Lazy
processed = bag.map(process_line)     # Still lazy
result = processed.compute()          # Processes in chunks
```

For very large results, avoid computing to memory:

```python
# Don't compute huge results to memory
# result = bag.compute()  # Could overflow memory

# Instead, convert and save to disk
ddf = bag.to_dataframe()
ddf.to_parquet('output/')
```

### `references/best-practices.md`

# Dask Best Practices

## Performance Optimization Principles

### Start with Simpler Solutions First

Before implementing parallel computing with Dask, explore these alternatives:
- Better algorithms for the specific problem
- Efficient file formats (Parquet, HDF5, Zarr instead of CSV)
- Compiled code via Numba or Cython
- Data sampling for development and testing

These alternatives often provide better returns than distributed systems and should be exhausted before scaling to parallel computing.

### Chunk Size Strategy

**Critical Rule**: Chunks should be small enough that many fit in a worker's available memory at once.

**Recommended Target**: Size chunks so workers can hold 10 chunks per core without exceeding available memory.

**Why It Matters**:
- Too large chunks: Memory overflow and inefficient parallelization
- Too small chunks: Excessive scheduling overhead

**Example Calculation**:
- 8 cores with 32 GB RAM
- Target: ~400 MB per chunk (32 GB / 8 cores / 10 chunks)

### Monitor with the Dashboard

The Dask dashboard provides essential visibility into:
- Worker states and resource utilization
- Task progress and bottlenecks
- Memory usage patterns
- Performance characteristics

Access the dashboard to understand what's actually slow in parallel workloads rather than guessing at optimizations.

## Critical Pitfalls to Avoid

### 1. Don't Create Large Objects Locally Before Dask

**Wrong Approach**:
```python
import pandas as pd
import dask.dataframe as dd

# Loads entire dataset into memory first
df = pd.read_csv('large_file.csv')
ddf = dd.from_pandas(df, npartitions=10)
```

**Correct Approach**:
```python
import dask.dataframe as dd

# Let Dask handle the loading
ddf = dd.read_csv('large_file.csv')
```

**Why**: Loading data with pandas or NumPy first forces the scheduler to serialize and embed those objects in task graphs, defeating the purpose of parallel computing.

**Key Principle**: Use Dask methods to load data and use Dask to control the results.

### 2. Avoid Repeated compute() Calls

**Wrong Approach**:
```python
results = []
for item in items:
    result = dask_computation(item).compute()  # Each compute is separate
    results.append(result)
```

**Correct Approach**:
```python
computations = [dask_computation(item) for item in items]
results = dask.compute(*computations)  # Single compute for all
```

**Why**: Calling compute in loops prevents Dask from:
- Parallelizing different computations
- Sharing intermediate results
- Optimizing the overall task graph

### 3. Don't Build Excessively Large Task Graphs

**Symptoms**:
- Millions of tasks in a single computation
- Severe scheduling overhead
- Long delays before computation starts

**Solutions**:
- Increase chunk sizes to reduce number of tasks
- Use `map_partitions` or `map_blocks` to fuse operations
- Break computations into smaller pieces with intermediate persists
- Consider whether the problem truly requires distributed computing

**Example Using map_partitions**:
```python
# Instead of applying function to each row
ddf['result'] = ddf.apply(complex_function, axis=1)  # Many tasks

# Apply to entire partitions at once
ddf = ddf.map_partitions(lambda df: df.assign(result=complex_function(df)))
```

## Infrastructure Considerations

### Scheduler Selection

**Use Threads For**:
- Numeric work with GIL-releasing libraries (NumPy, Pandas, scikit-learn)
- Operations that benefit from shared memory
- Single-machine workloads with array/dataframe operations

**Use Processes For**:
- Text processing and Python collection operations
- Pure Python code that's GIL-bound
- Operations that need process isolation

**Use Distributed Scheduler For**:
- Multi-machine clusters
- Need for diagnostic dashboard
- Asynchronous APIs
- Better data locality handling

### Thread Configuration

**Recommendation**: Aim for roughly 4 threads per process on numeric workloads.

**Rationale**:
- Balance between parallelism and overhead
- Allows efficient use of CPU cores
- Reduces context switching costs

### Memory Management

**Persist Strategically**:
```python
# Persist intermediate results that are reused
intermediate = expensive_computation(data).persist()
result1 = intermediate.operation1().compute()
result2 = intermediate.operation2().compute()
```

**Clear Memory When Done**:
```python
# Explicitly delete large objects
del intermediate
```

## Data Loading Best Practices

### Use Appropriate File Formats

**For Tabular Data**:
- Parquet: Columnar, compressed, fast filtering
- CSV: Only for small data or initial ingestion

**For Array Data**:
- HDF5: Good for numeric arrays
- Zarr: Cloud-native, parallel-friendly
- NetCDF: Scientific data with metadata

### Optimize Data Ingestion

**Read Multiple Files Efficiently**:
```python
# Use glob patterns to read multiple files in parallel
ddf = dd.read_parquet('data/year=2024/month=*/day=*.parquet')
```

**Specify Useful Columns Early**:
```python
# Only read needed columns
ddf = dd.read_parquet('data.parquet', columns=['col1', 'col2', 'col3'])
```

## Common Patterns and Solutions

### Pattern: Embarrassingly Parallel Problems

For independent computations, use Futures:
```python
from dask.distributed import Client

client = Client()
futures = [client.submit(func, arg) for arg in args]
results = client.gather(futures)
```

### Pattern: Data Preprocessing Pipeline

Use Bags for initial ETL, then convert to structured formats:
```python
import dask.bag as db

# Process raw JSON
bag = db.read_text('logs/*.json').map(json.loads)
bag = bag.filter(lambda x: x['status'] == 'success')

# Convert to DataFrame for analysis
ddf = bag.to_dataframe()
```

### Pattern: Iterative Algorithms

Persist data between iterations:
```python
data = dd.read_parquet('data.parquet')
data = data.persist()  # Keep in memory across iterations

for iteration in range(num_iterations):
    data = update_function(data)
    data = data.persist()  # Persist updated version
```

## Debugging Tips

### Use Single-Threaded Scheduler

For debugging with pdb or detailed error inspection:
```python
import dask

dask.config.set(scheduler='synchronous')
result = computation.compute()  # Runs in single thread for debugging
```

### Check Task Graph Size

Before computing, check the number of tasks:
```python
print(len(ddf.__dask_graph__()))  # Should be reasonable, not millions
```

### Validate on Small Data First

Test logic on small subset before scaling:
```python
# Test on first partition
sample = ddf.head(1000)
# Validate results
# Then scale to full dataset
```

## Performance Troubleshooting

### Symptom: Slow Computation Start

**Likely Cause**: Task graph is too large
**Solution**: Increase chunk sizes or use map_partitions

### Symptom: Memory Errors

**Likely Causes**:
- Chunks too large
- Too many intermediate results
- Memory leaks in user functions

**Solutions**:
- Decrease chunk sizes
- Use persist() strategically and delete when done
- Profile user functions for memory issues

### Symptom: Poor Parallelization

**Likely Causes**:
- Data dependencies preventing parallelism
- Chunks too large (not enough tasks)
- GIL contention with threads on Python code

**Solutions**:
- Restructure computation to reduce dependencies
- Increase number of partitions
- Switch to multiprocessing scheduler for Python code

### `references/dataframes.md`

# Dask DataFrames

## Overview

Dask DataFrames enable parallel processing of large tabular data by distributing work across multiple pandas DataFrames. As described in the documentation, "Dask DataFrames are a collection of many pandas DataFrames" with identical APIs, making the transition from pandas straightforward.

Since **dask 2025.1.0**, the expression-based implementation with logical query planning is the only DataFrame backend. Import from `dask.dataframe` only — avoid legacy submodule paths. DataFrame I/O requires **PyArrow 16+** (dask 2026.1.2+).

## Core Concept

A Dask DataFrame is divided into multiple pandas DataFrames (partitions) along the index:
- Each partition is a regular pandas DataFrame
- Operations are applied to each partition in parallel
- Results are combined automatically

## Key Capabilities

### Scale
- Process 100 GiB on a laptop
- Process 100 TiB on a cluster
- Handle datasets exceeding available RAM

### Compatibility
- Implements most of the pandas API
- Easy transition from pandas code
- Works with familiar operations

## When to Use Dask DataFrames

**Use Dask When**:
- Dataset exceeds available RAM
- Computations require significant time and pandas optimization hasn't helped
- Need to scale from prototype (pandas) to production (larger data)
- Working with multiple files that should be processed together

**Stick with Pandas When**:
- Data fits comfortably in memory
- Computations complete in subseconds
- Simple operations without custom `.apply()` functions
- Iterative development and exploration

## Reading Data

Dask mirrors pandas reading syntax with added support for multiple files:

### Single File
```python
import dask.dataframe as dd

# Read single file
ddf = dd.read_csv('data.csv')
ddf = dd.read_parquet('data.parquet')
```

### Multiple Files
```python
# Read multiple files using glob patterns
ddf = dd.read_csv('data/*.csv')
ddf = dd.read_parquet('data/year=*/month=*/day=*.parquet')

# Remote Parquet (requires s3fs: uv pip install s3fs)
ddf = dd.read_parquet('s3://mybucket/data/*.parquet', storage_options={'anon': False})
```

### Optimizations
```python
# Specify columns to read (reduces memory)
ddf = dd.read_parquet('data.parquet', columns=['col1', 'col2'])

# Control partitioning
ddf = dd.read_csv('data.csv', blocksize='64MB')  # Creates 64MB partitions
```

## Common Operations

All operations are lazy until `.compute()` is called.

### Filtering
```python
# Same as pandas
filtered = ddf[ddf['column'] > 100]
filtered = ddf.query('column > 100')
```

### Column Operations
```python
# Add columns
ddf['new_column'] = ddf['col1'] + ddf['col2']

# Select columns
subset = ddf[['col1', 'col2', 'col3']]

# Drop columns
ddf = ddf.drop(columns=['unnecessary_col'])
```

### Aggregations
```python
# Standard aggregations work as expected
mean = ddf['column'].mean().compute()
sum_total = ddf['column'].sum().compute()
counts = ddf['category'].value_counts().compute()
```

### GroupBy
```python
# GroupBy operations (may require shuffle)
grouped = ddf.groupby('category')['value'].mean().compute()

# Multiple aggregations
agg_result = ddf.groupby('category').agg({
    'value': ['mean', 'sum', 'count'],
    'amount': 'sum'
}).compute()
```

### Joins and Merges
```python
# Merge DataFrames
merged = dd.merge(ddf1, ddf2, on='key', how='left')

# Join on index
joined = ddf1.join(ddf2, on='key')
```

### Sorting
```python
# Sorting (expensive operation, requires data movement)
sorted_ddf = ddf.sort_values('column')
result = sorted_ddf.compute()
```

## Custom Operations

### Apply Functions

**To Partitions (Efficient)**:
```python
# Apply function to entire partitions
def custom_partition_function(partition_df):
    # partition_df is a pandas DataFrame
    return partition_df.assign(new_col=partition_df['col1'] * 2)

ddf = ddf.map_partitions(custom_partition_function)
```

**To Rows (Less Efficient)**:
```python
# Apply to each row (creates many tasks)
ddf['result'] = ddf.apply(lambda row: custom_function(row), axis=1, meta=('result', 'float'))
```

**Note**: Always prefer `map_partitions` over row-wise `apply` for better performance.

### Meta Parameter

When Dask can't infer output structure, specify the `meta` parameter:
```python
# For apply operations
ddf['new'] = ddf.apply(func, axis=1, meta=('new', 'float64'))

# For map_partitions
ddf = ddf.map_partitions(func, meta=pd.DataFrame({
    'col1': pd.Series(dtype='float64'),
    'col2': pd.Series(dtype='int64')
}))
```

## Lazy Evaluation and Computation

### Lazy Operations
```python
# These operations are lazy (instant, no computation)
filtered = ddf[ddf['value'] > 100]
aggregated = filtered.groupby('category').mean()
final = aggregated[aggregated['value'] < 500]

# Nothing has computed yet
```

### Triggering Computation
```python
# Compute single result
result = final.compute()

# Compute multiple results efficiently
result1, result2, result3 = dask.compute(
    operation1,
    operation2,
    operation3
)
```

### Persist in Memory
```python
# Keep results in distributed memory for reuse
ddf_cached = ddf.persist()

# Now multiple operations on ddf_cached won't recompute
result1 = ddf_cached.mean().compute()
result2 = ddf_cached.sum().compute()
```

## Index Management

### Setting Index
```python
# Set index (required for efficient joins and certain operations)
ddf = ddf.set_index('timestamp', sorted=True)
```

### Index Properties
- Sorted index enables efficient filtering and joins
- Index determines partitioning
- Some operations perform better with appropriate index

## Writing Results

### To Files
```python
# Write to multiple files (one per partition)
ddf.to_parquet('output/data.parquet')
ddf.to_csv('output/data-*.csv')

# Write to single file (forces computation and concatenation)
ddf.compute().to_csv('output/single_file.csv')
```

### To Memory (Pandas)
```python
# Convert to pandas (loads all data in memory)
pdf = ddf.compute()
```

## Performance Considerations

### Efficient Operations
- Column selection and filtering: Very efficient
- Simple aggregations (sum, mean, count): Efficient
- Row-wise operations on partitions: Efficient with `map_partitions`

### Expensive Operations
- Sorting: Requires data shuffle across workers
- GroupBy with many groups: May require shuffle
- Complex joins: Depends on data distribution
- Row-wise apply: Creates many tasks

### Optimization Tips

**1. Select Columns Early**
```python
# Better: Read only needed columns
ddf = dd.read_parquet('data.parquet', columns=['col1', 'col2'])
```

**2. Filter Before GroupBy**
```python
# Better: Reduce data before expensive operations
result = ddf[ddf['year'] == 2024].groupby('category').sum().compute()
```

**3. Use Efficient File Formats**
```python
# Use Parquet instead of CSV for better performance
ddf.to_parquet('data.parquet')  # Faster, smaller, columnar
```

**4. Repartition Appropriately**
```python
# If partitions are too small
ddf = ddf.repartition(npartitions=10)

# If partitions are too large
ddf = ddf.repartition(partition_size='100MB')
```

## Common Patterns

### ETL Pipeline
```python
import dask.dataframe as dd

# Read data
ddf = dd.read_csv('raw_data/*.csv')

# Transform
ddf = ddf[ddf['status'] == 'valid']
ddf['amount'] = ddf['amount'].astype('float64')
ddf = ddf.dropna(subset=['important_col'])

# Aggregate
summary = ddf.groupby('category').agg({
    'amount': ['sum', 'mean'],
    'quantity': 'count'
})

# Write results
summary.to_parquet('output/summary.parquet')
```

### Time Series Analysis
```python
# Read time series data
ddf = dd.read_parquet('timeseries/*.parquet')

# Set timestamp index
ddf = ddf.set_index('timestamp', sorted=True)

# Resample time series (requires sorted datetime index)
hourly = ddf.resample('1h').mean()

# Compute statistics
result = hourly.compute()
```

### Combining Multiple Files
```python
# Read multiple files as single DataFrame
ddf = dd.read_csv('data/2024-*.csv')

# Process combined data
result = ddf.groupby('category')['value'].sum().compute()
```

## Limitations and Differences from Pandas

### Not All Pandas Features Available
Some pandas operations are not implemented in Dask:
- Some string methods
- Certain window functions
- Some specialized statistical functions

### Partitioning Matters
- Operations within partitions are efficient
- Cross-partition operations may be expensive
- Index-based operations benefit from sorted index

### Lazy Evaluation
- Operations don't execute until `.compute()`
- Need to be aware of computation triggers
- Can't inspect intermediate results without computing

## Debugging Tips

### Inspect Partitions
```python
# Get number of partitions
print(ddf.npartitions)

# Compute single partition
first_partition = ddf.get_partition(0).compute()

# View first few rows (computes first partition)
print(ddf.head())
```

### Validate Operations on Small Data
```python
# Test on small sample first
sample = ddf.head(1000)
# Validate logic works
# Then scale to full dataset
result = ddf.compute()
```

### Check Dtypes
```python
# Verify data types are correct
print(ddf.dtypes)
```

### `references/futures.md`

# Dask Futures

## Overview

Dask futures extend Python's `concurrent.futures` interface, enabling immediate (non-lazy) task execution. Unlike delayed computations (used in DataFrames, Arrays, and Bags), futures provide more flexibility in situations where computations may evolve over time or require dynamic workflow construction.

## Core Concept

Futures represent real-time task execution:
- Tasks execute immediately when submitted (not lazy)
- Each future represents a remote computation result
- Automatic dependency tracking between futures
- Enables dynamic, evolving workflows
- Direct control over task scheduling and data placement

## Key Capabilities

### Real-Time Execution
- Tasks run immediately when submitted
- No need for explicit `.compute()` call
- Get results with `.result()` method

### Automatic Dependency Management
When you submit tasks with future inputs, Dask automatically handles dependency tracking. Once all input futures have completed, they will be moved onto a single worker for efficient computation.

### Dynamic Workflows
Build computations that evolve based on intermediate results:
- Submit new tasks based on previous results
- Conditional execution paths
- Iterative algorithms with varying structure

## When to Use Futures

**Use Futures When**:
- Building dynamic, evolving workflows
- Need immediate task execution (not lazy)
- Computations depend on runtime conditions
- Require fine control over task placement
- Implementing custom parallel algorithms
- Need stateful computations (with actors)

**Use Other Collections When**:
- Static, predefined computation graphs (use delayed, DataFrames, Arrays)
- Simple data parallelism on large collections (use Bags, DataFrames)
- Standard array/dataframe operations suffice

## Setting Up Client

Futures require a distributed client:

```python
from dask.distributed import Client

# Local cluster (on single machine)
client = Client()

# Or specify resources
client = Client(n_workers=4, threads_per_worker=2)

# Or connect to existing cluster
client = Client('scheduler-address:8786')
```

## Submitting Tasks

### Basic Submit
```python
from dask.distributed import Client

client = Client()

# Submit single task
def add(x, y):
    return x + y

future = client.submit(add, 1, 2)

# Get result
result = future.result()  # Blocks until complete
print(result)  # 3
```

### Multiple Tasks
```python
# Submit multiple independent tasks
futures = []
for i in range(10):
    future = client.submit(add, i, i)
    futures.append(future)

# Gather results
results = client.gather(futures)  # Efficient parallel gathering
```

### Map Over Inputs
```python
# Apply function to multiple inputs
def square(x):
    return x ** 2

# Submit batch of tasks
futures = client.map(square, range(100))

# Gather results
results = client.gather(futures)
```

**Note**: Each task carries ~1ms overhead, making `map` less suitable for millions of tiny tasks. For massive datasets, use Bags or DataFrames instead.

## Working with Futures

### Check Status
```python
future = client.submit(expensive_function, arg)

# Check if complete
print(future.done())  # False or True

# Check status
print(future.status)  # 'pending', 'running', 'finished', or 'error'
```

### Non-Blocking Result Retrieval
```python
# Non-blocking check
if future.done():
    result = future.result()
else:
    print("Still computing...")

# Or use callbacks
def handle_result(future):
    print(f"Result: {future.result()}")

future.add_done_callback(handle_result)
```

### Error Handling
```python
def might_fail(x):
    if x < 0:
        raise ValueError("Negative value")
    return x ** 2

future = client.submit(might_fail, -5)

try:
    result = future.result()
except ValueError as e:
    print(f"Task failed: {e}")
```

## Task Dependencies

### Automatic Dependency Tracking
```python
# Submit task
future1 = client.submit(add, 1, 2)

# Use future as input (creates dependency)
future2 = client.submit(add, future1, 10)  # Depends on future1

# Chain dependencies
future3 = client.submit(add, future2, 100)  # Depends on future2

# Get final result
result = future3.result()  # 113
```

### Complex Dependencies
```python
# Multiple dependencies
a = client.submit(func1, x)
b = client.submit(func2, y)
c = client.submit(func3, a, b)  # Depends on both a and b

result = c.result()
```

## Data Movement Optimization

### Scatter Data
Pre-scatter important data to avoid repeated transfers:

```python
# Upload data to cluster once
large_dataset = client.scatter(big_data)  # Returns future

# Use scattered data in multiple tasks
futures = [client.submit(process, large_dataset, i) for i in range(100)]

# Each task uses the same scattered data without re-transfer
results = client.gather(futures)
```

### Efficient Gathering
Use `client.gather()` for concurrent result collection:

```python
# Better: Gather all at once (parallel)
results = client.gather(futures)

# Worse: Sequential result retrieval
results = [f.result() for f in futures]
```

## Fire-and-Forget

For side-effect tasks without needing the result:

```python
from dask.distributed import fire_and_forget

def log_to_database(data):
    # Write to database, no return value needed
    database.write(data)

# Submit without keeping reference
future = client.submit(log_to_database, data)
fire_and_forget(future)

# Dask won't abandon this computation even without active future reference
```

## Performance Characteristics

### Task Overhead
- ~1ms overhead per task
- Good for: Thousands of tasks
- Not suitable for: Millions of tiny tasks

### Worker-to-Worker Communication
- Direct worker-to-worker data transfer
- Roundtrip latency: ~1ms
- Efficient for task dependencies

### Memory Management
Dask tracks active futures locally. When a future is garbage collected by your local Python session, Dask will feel free to delete that data.

**Keep References**:
```python
# Keep reference to prevent deletion
important_result = client.submit(expensive_calc, data)

# Use result multiple times
future1 = client.submit(process1, important_result)
future2 = client.submit(process2, important_result)
```

## Advanced Coordination

### Distributed Primitives

**Queues**:
```python
from dask.distributed import Queue

queue = Queue()

def producer():
    for i in range(10):
        queue.put(i)

def consumer():
    results = []
    for _ in range(10):
        results.append(queue.get())
    return results

# Submit tasks
client.submit(producer)
result_future = client.submit(consumer)
results = result_future.result()
```

**Locks**:
```python
from dask.distributed import Lock

lock = Lock()

def critical_section():
    with lock:
        # Only one task executes this at a time
        shared_resource.update()
```

**Events**:
```python
from dask.distributed import Event

event = Event()

def waiter():
    event.wait()  # Blocks until event is set
    return "Event occurred"

def setter():
    time.sleep(5)
    event.set()

# Start both tasks
wait_future = client.submit(waiter)
set_future = client.submit(setter)

result = wait_future.result()  # Waits for setter to complete
```

**Variables**:
```python
from dask.distributed import Variable

var = Variable('my-var')

# Set value
var.set(42)

# Get value from tasks
def reader():
    return var.get()

future = client.submit(reader)
print(future.result())  # 42
```

## Actors

For stateful, rapidly-changing workflows, actors enable worker-to-worker roundtrip latency around 1ms while bypassing scheduler coordination.

### Creating Actors
```python
from dask.distributed import Client

client = Client()

class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count

    def get_count(self):
        return self.count

# Create actor on worker
counter = client.submit(Counter, actor=True).result()

# Call methods
future1 = counter.increment()
future2 = counter.increment()
result = counter.get_count().result()
print(result)  # 2
```

### Actor Use Cases
- Stateful services (databases, caches)
- Rapidly changing state
- Complex coordination patterns
- Real-time streaming applications

## Common Patterns

### Embarrassingly Parallel Tasks
```python
from dask.distributed import Client

client = Client()

def process_item(item):
    # Independent computation
    return expensive_computation(item)

# Process many items in parallel
items = range(1000)
futures = client.map(process_item, items)

# Gather all results
results = client.gather(futures)
```

### Dynamic Task Submission
```python
def recursive_compute(data, depth):
    if depth == 0:
        return process(data)

    # Split and recurse
    left, right = split(data)
    left_future = client.submit(recursive_compute, left, depth - 1)
    right_future = client.submit(recursive_compute, right, depth - 1)

    # Combine results
    return combine(left_future.result(), right_future.result())

# Start computation
result_future = client.submit(recursive_compute, initial_data, 5)
result = result_future.result()
```

### Parameter Sweep
```python
from itertools import product

def run_simulation(param1, param2, param3):
    # Run simulation with parameters
    return simulate(param1, param2, param3)

# Generate parameter combinations
params = product(range(10), range(10), range(10))

# Submit all combinations
futures = [client.submit(run_simulation, p1, p2, p3) for p1, p2, p3 in params]

# Gather results as they complete
from dask.distributed import as_completed

for future in as_completed(futures):
    result = future.result()
    process_result(result)
```

### Pipeline with Dependencies
```python
# Stage 1: Load data
load_futures = [client.submit(load_data, file) for file in files]

# Stage 2: Process (depends on stage 1)
process_futures = [client.submit(process, f) for f in load_futures]

# Stage 3: Aggregate (depends on stage 2)
agg_future = client.submit(aggregate, process_futures)

# Get final result
result = agg_future.result()
```

### Iterative Algorithm
```python
# Initialize
state = client.scatter(initial_state)

# Iterate
for iteration in range(num_iterations):
    # Compute update based on current state
    state = client.submit(update_function, state)

    # Check convergence
    converged = client.submit(check_convergence, state)
    if converged.result():
        break

# Get final state
final_state = state.result()
```

## Best Practices

### 1. Pre-scatter Large Data
```python
# Upload once, use many times
large_data = client.scatter(big_dataset)
futures = [client.submit(process, large_data, i) for i in range(100)]
```

### 2. Use Gather for Bulk Retrieval
```python
# Efficient: Parallel gathering
results = client.gather(futures)

# Inefficient: Sequential
results = [f.result() for f in futures]
```

### 3. Manage Memory with References
```python
# Keep important futures
important = client.submit(expensive_calc, data)

# Use multiple times
f1 = client.submit(use_result, important)
f2 = client.submit(use_result, important)

# Clean up when done
del important
```

### 4. Handle Errors Appropriately
```python
futures = client.map(might_fail, inputs)

# Check for errors
results = []
errors = []
for future in as_completed(futures):
    try:
        results.append(future.result())
    except Exception as e:
        errors.append(e)
```

### 5. Use as_completed for Progressive Processing
```python
from dask.distributed import as_completed

futures = client.map(process, items)

# Process results as they arrive
for future in as_completed(futures):
    result = future.result()
    handle_result(result)
```

## Debugging Tips

### Monitor Dashboard
View the Dask dashboard to see:
- Task progress
- Worker utilization
- Memory usage
- Task dependencies

### Check Task Status
```python
# Inspect future
print(future.status)
print(future.done())

# Get traceback on error
try:
    future.result()
except Exception:
    print(future.traceback())
```

### Profile Tasks
```python
# Get performance data
client.profile(filename='profile.html')
```

### `references/schedulers.md`

# Dask Schedulers

## Overview

Dask provides multiple task schedulers, each suited to different workloads. The scheduler determines how tasks are executed: sequentially, in parallel threads, in parallel processes, or distributed across a cluster.

## Scheduler Types

### Single-Machine Schedulers

#### 1. Local Threads (Default)

**Description**: The threaded scheduler executes computations with a local `concurrent.futures.ThreadPoolExecutor`.

**When to Use**:
- Numeric computations in NumPy, Pandas, scikit-learn
- Libraries that release the GIL (Global Interpreter Lock)
- Operations benefit from shared memory access
- Default for Dask Arrays and DataFrames

**Characteristics**:
- Low overhead
- Shared memory between threads
- Best for GIL-releasing operations
- Poor for pure Python code (GIL contention)

**Example**:
```python
import dask.array as da

# Uses threads by default
x = da.random.random((10000, 10000), chunks=(1000, 1000))
result = x.mean().compute()  # Computed with threads
```

**Explicit Configuration**:
```python
import dask

# Set globally
dask.config.set(scheduler='threads')

# Or per-compute
result = x.mean().compute(scheduler='threads')
```

#### 2. Local Processes

**Description**: Multiprocessing scheduler that uses `concurrent.futures.ProcessPoolExecutor`.

**When to Use**:
- Pure Python code with GIL contention
- Text processing and Python collections
- Operations that benefit from process isolation
- CPU-bound Python code

**Characteristics**:
- Bypasses GIL limitations
- Incurs data transfer costs between processes
- Higher overhead than threads
- Ideal for linear workflows with small inputs/outputs

**Example**:
```python
import dask.bag as db

# Good for Python object processing
bag = db.read_text('data/*.txt')
result = bag.map(complex_python_function).compute(scheduler='processes')
```

**Explicit Configuration**:
```python
import dask

# Set globally
dask.config.set(scheduler='processes')

# Or per-compute
result = computation.compute(scheduler='processes')
```

**Limitations**:
- Data must be serializable (pickle)
- Overhead from process creation
- Memory overhead from data copying

#### 3. Single Thread (Synchronous)

**Description**: The single-threaded synchronous scheduler executes all computations in the local thread with no parallelism at all.

**When to Use**:
- Debugging with pdb
- Profiling with standard Python tools
- Understanding errors in detail
- Development and testing

**Characteristics**:
- No parallelism
- Easy debugging
- No overhead
- Deterministic execution

**Example**:
```python
import dask

# Enable for debugging
dask.config.set(scheduler='synchronous')

# Now can use pdb
result = computation.compute()  # Runs in single thread
```

**Debugging with IPython**:
```python
# In IPython/Jupyter
%pdb on

dask.config.set(scheduler='synchronous')
result = problematic_computation.compute()  # Drops into debugger on error
```

### Distributed Schedulers

#### 4. Local Distributed

**Description**: Despite its name, this scheduler runs effectively on personal machines using the distributed scheduler infrastructure.

**When to Use**:
- Need diagnostic dashboard
- Asynchronous APIs
- Better data locality handling than multiprocessing
- Development before scaling to cluster
- Want distributed features on single machine

**Characteristics**:
- Provides dashboard for monitoring
- Better memory management
- More overhead than threads/processes
- Can scale to cluster later

**Example**:
```python
from dask.distributed import Client
import dask.dataframe as dd

# Create local cluster
client = Client()  # Automatically uses all cores

# Use distributed scheduler
ddf = dd.read_csv('data.csv')
result = ddf.groupby('category').mean().compute()

# View dashboard
print(client.dashboard_link)

# Clean up
client.close()
```

**Configuration Options**:
```python
# Control resources
client = Client(
    n_workers=4,
    threads_per_worker=2,
    memory_limit='4GB'
)
```

#### 5. Cluster Distributed

**Description**: For scaling across multiple machines using the distributed scheduler.

**When to Use**:
- Data exceeds single machine capacity
- Need computational power beyond one machine
- Production deployments
- Cluster computing environments (HPC, cloud)

**Characteristics**:
- Scales to hundreds of machines
- Requires cluster setup
- Network communication overhead
- Advanced features (adaptive scaling, task prioritization)

**Example with Dask-Jobqueue (HPC)**:
```python
from dask_jobqueue import SLURMCluster
from dask.distributed import Client

# Create cluster on HPC with SLURM
cluster = SLURMCluster(
    cores=24,
    memory='100GB',
    walltime='02:00:00',
    queue='regular'
)

# Scale to 10 jobs
cluster.scale(jobs=10)

# Connect client
client = Client(cluster)

# Run computation
result = computation.compute()

client.close()
```

**Example with Dask on Kubernetes**:
```python
from dask_kubernetes import KubeCluster
from dask.distributed import Client

cluster = KubeCluster()
cluster.scale(20)  # 20 workers

client = Client(cluster)
result = computation.compute()

client.close()
```

## Scheduler Configuration

### Global Configuration

```python
import dask

# Set scheduler globally for session
dask.config.set(scheduler='threads')
dask.config.set(scheduler='processes')
dask.config.set(scheduler='synchronous')
```

### Context Manager

```python
import dask

# Temporarily use different scheduler
with dask.config.set(scheduler='processes'):
    result = computation.compute()

# Back to default scheduler
result2 = computation2.compute()
```

### Per-Compute

```python
# Specify scheduler per compute call
result = computation.compute(scheduler='threads')
result = computation.compute(scheduler='processes')
result = computation.compute(scheduler='synchronous')
```

### Distributed Client

```python
from dask.distributed import Client

# Using client automatically sets distributed scheduler
client = Client()

# All computations use distributed scheduler
result = computation.compute()

client.close()
```

## Choosing the Right Scheduler

### Decision Matrix

| Workload Type | Recommended Scheduler | Rationale |
|--------------|----------------------|-----------|
| NumPy/Pandas operations | Threads (default) | GIL-releasing, shared memory |
| Pure Python objects | Processes | Avoids GIL contention |
| Text/log processing | Processes | Python-heavy operations |
| Debugging | Synchronous | Easy debugging, deterministic |
| Need dashboard | Local Distributed | Monitoring and diagnostics |
| Multi-machine | Cluster Distributed | Exceeds single machine capacity |
| Small data, quick tasks | Threads | Lowest overhead |
| Large data, single machine | Local Distributed | Better memory management |

### Performance Considerations

**Threads**:
- Overhead: ~10 µs per task
- Best for: Numeric operations
- Memory: Shared
- GIL: Affected by GIL

**Processes**:
- Overhead: ~10 ms per task
- Best for: Python operations
- Memory: Copied between processes
- GIL: Not affected

**Synchronous**:
- Overhead: ~1 µs per task
- Best for: Debugging
- Memory: No parallelism
- GIL: Not relevant

**Distributed**:
- Overhead: ~1 ms per task
- Best for: Complex workflows, monitoring
- Memory: Managed by scheduler
- GIL: Workers can use threads or processes

## Thread Configuration for Distributed Scheduler

### Setting Thread Count

```python
from dask.distributed import Client

# Control thread/worker configuration
client = Client(
    n_workers=4,           # Number of worker processes
    threads_per_worker=2   # Threads per worker process
)
```

### Recommended Configuration

**For Numeric Workloads**:
- Aim for roughly 4 threads per process
- Balance between parallelism and overhead
- Example: 8 cores → 2 workers with 4 threads each

**For Python Workloads**:
- Use more workers with fewer threads
- Example: 8 cores → 8 workers with 1 thread each

### Configuration via dask.config

Prefer `dask.config` over shell environment variables so worker settings stay explicit in code:

```python
import dask

dask.config.set({
    "distributed.worker.memory.target": 0.60,
    "distributed.worker.memory.spill": 0.70,
})
```

When creating a `Client`, pass resource limits directly:

```python
from dask.distributed import Client

client = Client(n_workers=4, threads_per_worker=2, memory_limit='4GB')
```

Upstream also supports `DASK_*` environment variables (for example `DASK_SCHEDULER_ADDRESS` when connecting to an existing cluster). Set only the specific variables documented for your deployment — do not copy entire `.env` files into the environment.

## Common Patterns

### Development to Production

```python
# Development: Use local distributed for testing
from dask.distributed import Client
client = Client(processes=False)  # In-process for debugging

# Production: Scale to cluster
from dask.distributed import Client
client = Client('scheduler-address:8786')
```

### Mixed Workloads

```python
import dask
import dask.dataframe as dd

# Use threads for DataFrame operations
ddf = dd.read_parquet('data.parquet')
result1 = ddf.mean().compute(scheduler='threads')

# Use processes for Python code
import dask.bag as db
bag = db.read_text('logs/*.txt')
result2 = bag.map(parse_log).compute(scheduler='processes')
```

### Debugging Workflow

```python
import dask

# Step 1: Debug with synchronous scheduler
dask.config.set(scheduler='synchronous')
result = problematic_computation.compute()

# Step 2: Test with threads
dask.config.set(scheduler='threads')
result = computation.compute()

# Step 3: Scale with distributed
from dask.distributed import Client
client = Client()
result = computation.compute()
```

## Monitoring and Diagnostics

### Dashboard Access (Distributed Only)

```python
from dask.distributed import Client

client = Client()

# Get dashboard URL
print(client.dashboard_link)
# Opens dashboard in browser showing:
# - Task progress
# - Worker status
# - Memory usage
# - Task stream
# - Resource utilization
```

### Performance Profiling

```python
# Profile computation
from dask.distributed import Client

client = Client()
result = computation.compute()

# Get performance report
client.profile(filename='profile.html')
```

### Resource Monitoring

```python
# Check worker info
client.scheduler_info()

# Get current tasks
client.who_has()

# Memory usage
client.run(lambda: psutil.virtual_memory().percent)
```

## Advanced Configuration

### Custom Executors

```python
from concurrent.futures import ThreadPoolExecutor
import dask

# Use custom thread pool
with ThreadPoolExecutor(max_workers=4) as executor:
    dask.config.set(pool=executor)
    result = computation.compute(scheduler='threads')
```

### Adaptive Scaling (Distributed)

```python
from dask.distributed import Client

client = Client()

# Enable adaptive scaling
client.cluster.adapt(minimum=2, maximum=10)

# Cluster scales based on workload
result = computation.compute()
```

### Worker Plugins

```python
from dask.distributed import Client, WorkerPlugin

class CustomPlugin(WorkerPlugin):
    def setup(self, worker):
        # Initialize worker-specific resources
        worker.custom_resource = initialize_resource()

client = Client()
client.register_worker_plugin(CustomPlugin())
```

## Troubleshooting

### Slow Performance with Threads
**Problem**: Pure Python code slow with threaded scheduler
**Solution**: Switch to processes or distributed scheduler

### Memory Errors with Processes
**Problem**: Data too large to pickle/copy between processes
**Solution**: Use threaded or distributed scheduler

### Debugging Difficult
**Problem**: Can't use pdb with parallel schedulers
**Solution**: Use synchronous scheduler for debugging

### Task Overhead High
**Problem**: Many tiny tasks causing overhead
**Solution**: Use threaded scheduler (lowest overhead) or increase chunk sizes
