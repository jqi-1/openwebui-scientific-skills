---
name: zarr-python
description: Chunked N-D arrays for cloud storage (Zarr-Python 3). Compressed arrays, parallel I/O, S3/GCS via fsspec, NumPy/Dask/Xarray compatible, for large-scale scientific computing pipelines.
---

# Zarr Python

## Overview

Zarr is a Python library for storing large N-dimensional arrays with chunking and compression. Apply this skill for efficient parallel I/O, cloud-native workflows, and seamless integration with NumPy, Dask, and Xarray.

**Current upstream:** zarr **3.2.1** (released 2026-05-05). Docs: [zarr.readthedocs.io](https://zarr.readthedocs.io/en/stable/). New arrays default to **Zarr format 3**; set `zarr_format=2` for legacy interop. Zarr 3.2 adds rectilinear chunks and continues to refine the v3 codec pipeline. This skill is a **community guide** maintained by K-Dense Inc., not an official zarr-developers package.

## Quick Start

### Installation

```bash
uv pip install "zarr==3.2.1"
```

Requires **Python 3.12+** and NumPy 2.0+ for current stable Zarr-Python. For remote stores (S3, GCS, HTTP), pin the optional extras/backends in your project lockfile:

```bash
uv pip install "zarr[remote]==3.2.1" "s3fs==2026.4.0" "gcsfs==2026.5.0"
```

Use a version range such as `zarr>=3,<4` only when your project has a committed lockfile and compatibility tests. For Zarr-Python 2 / Python 3.10–3.11 workflows, choose an exact `zarr==2.x.y` patch version from the support-v2 release notes and commit the resulting lockfile.

### Basic Array Creation

```python
import zarr
import numpy as np

# Create a 2D array with chunking and compression
z = zarr.create_array(
    store="data/my_array.zarr",
    shape=(10000, 10000),
    chunks=(1000, 1000),
    dtype="f4"
)

# Write data using NumPy-style indexing
z[:, :] = np.random.random((10000, 10000))

# Read data
data = z[0:100, 0:100]  # Returns NumPy array
```

## Core Operations

### Creating Arrays

Zarr provides multiple convenience functions for array creation:

```python
# Create empty array
z = zarr.zeros(shape=(10000, 10000), chunks=(1000, 1000), dtype='f4',
               store='data.zarr')

# Create filled arrays
z = zarr.ones((5000, 5000), chunks=(500, 500))
z = zarr.full((1000, 1000), fill_value=42, chunks=(100, 100))

# Create from existing data
data = np.arange(10000).reshape(100, 100)
z = zarr.array(data, chunks=(10, 10), store='data.zarr')

# Create like another array
z2 = zarr.zeros_like(z)  # Matches shape, chunks, dtype of z
```

### Opening Existing Arrays

```python
# Open array (read/write mode by default)
z = zarr.open_array('data.zarr', mode='r+')

# Read-only mode
z = zarr.open_array('data.zarr', mode='r')

# The open() function auto-detects arrays vs groups
z = zarr.open('data.zarr')  # Returns Array or Group
```

### Reading and Writing Data

Zarr arrays support NumPy-like indexing:

```python
# Write entire array
z[:] = 42

# Write slices
z[0, :] = np.arange(100)
z[10:20, 50:60] = np.random.random((10, 10))

# Read data (returns NumPy array)
data = z[0:100, 0:100]
row = z[5, :]

# Advanced indexing
z.vindex[[0, 5, 10], [2, 8, 15]]  # Coordinate indexing
z.oindex[0:10, [5, 10, 15]]       # Orthogonal indexing
z.blocks[0, 0]                     # Block/chunk indexing
```

### Resizing and Appending

```python
# Resize array (v3: pass shape as a tuple)
z.resize((15000, 15000))

# Append data along an axis
z.append(np.random.random((1000, 10000)), axis=0)  # Adds rows
```

## Groups and Hierarchies

Groups organize multiple arrays hierarchically, similar to directories or HDF5 groups.

### Creating and Using Groups

```python
# Create root group
root = zarr.group(store='data/hierarchy.zarr')

# Create sub-groups
temperature = root.create_group('temperature')
precipitation = root.create_group('precipitation')

# Create arrays within groups
temp_array = temperature.create_array(
    name='t2m',
    shape=(365, 720, 1440),
    chunks=(1, 720, 1440),
    dtype='f4'
)

precip_array = precipitation.create_array(
    name='prcp',
    shape=(365, 720, 1440),
    chunks=(1, 720, 1440),
    dtype='f4'
)

# Access using paths
array = root['temperature/t2m']

# Visualize hierarchy
print(root.tree())
# Output:
# /
#  ├── temperature
#  │   └── t2m (365, 720, 1440) f4
#  └── precipitation
#      └── prcp (365, 720, 1440) f4
```

### Group API (v3)

Use `create_array` / `require_array` (h5py-style `create_dataset` / `require_dataset` were removed in v3):

```python
root = zarr.group('data.zarr')
arr = root.create_array('my_data', shape=(1000, 1000), chunks=(100, 100), dtype='f4')

grp = root.require_group('subgroup')
arr2 = grp.require_array('array', shape=(500, 500), chunks=(50, 50), dtype='i4')
```

## Attributes and Metadata

Attach custom metadata to arrays and groups using attributes:

```python
# Add attributes to array
z = zarr.zeros((1000, 1000), chunks=(100, 100))
z.attrs['description'] = 'Temperature data in Kelvin'
z.attrs['units'] = 'K'
z.attrs['created'] = '2024-01-15'
z.attrs['processing_version'] = 2.1

# Attributes are stored as JSON
print(z.attrs['units'])  # Output: K

# Add attributes to groups
root = zarr.group('data.zarr')
root.attrs['project'] = 'Climate Analysis'
root.attrs['institution'] = 'Research Institute'

# Attributes persist with the array/group
z2 = zarr.open('data.zarr')
print(z2.attrs['description'])
```

**Important**: Attributes must be JSON-serializable (strings, numbers, lists, dicts, booleans, null).

## Chunking, Compression, Storage, and Performance

- [references/chunking_and_compression.md](references/chunking_and_compression.md):
  sizing chunks to the access pattern (aim for ~1 MB, 5-100 MB on cloud), sharding, and
  codec choice.
- [references/storage_backends.md](references/storage_backends.md): local, memory, ZIP,
  and fsspec remote stores (S3, GCS), with credential guidance — prefer IAM roles or
  workload identity, and never print credential values.
- [references/integration.md](references/integration.md): NumPy, Dask, and Xarray
  integration, thread safety, and consolidated metadata.
- [references/performance_and_patterns.md](references/performance_and_patterns.md):
  optimization, appendable time-series and large-matrix patterns, format conversion, and
  troubleshooting.
- [references/api_reference.md](references/api_reference.md) and
  [references/v3_migration.md](references/v3_migration.md): full API and the v2-to-v3
  migration notes.

## Additional Resources

### Bundled references

| File | Contents |
|------|----------|
| `references/api_reference.md` | Function signatures, stores, codecs, indexing |
| `references/v3_migration.md` | Zarr-Python 2→3 breaking changes and WIP features |

### Official upstream

- **Documentation**: https://zarr.readthedocs.io/en/stable/
- **3.0 migration guide**: https://zarr.readthedocs.io/en/stable/user-guide/v3_migration/
- **Storage backends**: https://zarr.readthedocs.io/en/stable/user-guide/storage/
- **Zarr specifications**: https://zarr-specs.readthedocs.io/
- **GitHub**: https://github.com/zarr-developers/zarr-python
- **Developer chat**: https://ossci.zulipchat.com/#narrow/channel/423692-Zarr-Python

**Related libraries:** [Xarray](https://docs.xarray.dev/), [Dask](https://docs.dask.org/), [NumCodecs](https://numcodecs.readthedocs.io/)

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/zarr-python/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_reference.md`

# Zarr Python Quick Reference

Concise reference for **zarr 3.2.x**. See `references/v3_migration.md` for Zarr-Python 2→3 changes.

## Array Creation

### `zarr.zeros()` / `zarr.ones()` / `zarr.empty()` / `zarr.full()`
```python
zarr.zeros(shape, *, chunks=None, dtype='f8', store=None, compressors='default',
           fill_value=0, zarr_format=3)
```

### `zarr.create_array()`
```python
zarr.create_array(store, *, shape, chunks, dtype='f8', compressors='default',
                  filters=None, fill_value=0, zarr_format=3, storage_options=None,
                  overwrite=False)
```

`chunks` may be a regular tuple (for example `(100, 100)`) or, in Zarr 3.2+, a rectilinear nested sequence (for example `([10, 20, 30], [50, 50])`).

### `zarr.array()`
```python
zarr.array(data, *, chunks=None, dtype=None, store=None, compressors='default')
```

### `zarr.open_array()` / `zarr.open()`
```python
zarr.open_array(store, mode='a', *, shape=None, chunks=None, dtype=None)
zarr.open(store, mode='r')  # auto-detects Array or Group
```

**Mode:** `'r'`, `'r+'`, `'a'` (default create-if-missing), `'w'` (overwrite), `'w-'` (create only).

## Storage (zarr.storage)

Built-in stores in v3: `LocalStore`, `MemoryStore`, `ZipStore`, `FsspecStore`, `ObjectStore`.

```python
from zarr.storage import LocalStore, MemoryStore, ZipStore, FsspecStore

# Local directory (default when passing a path string)
store = LocalStore('path/to/data.zarr')

# In-memory
store = MemoryStore()

# ZIP archive
store = ZipStore('data.zip', mode='w')  # close when done writing

# Cloud via fsspec URI (install pinned zarr[remote] + pinned backend)
store = FsspecStore.from_url('s3://bucket/path.zarr', storage_options={'anon': False})
group = zarr.open_group(store=store, mode='r')

# Shorthand — pass URI directly to open/create
zarr.open_group('s3://bucket/data.zarr', mode='r', storage_options={'anon': True})
```

**Removed in v3:** `DirectoryStore`, `FSStore`, `S3Map`, `GCSMap`, `DBMStore`, `LMDBStore`, `SQLiteStore`, `RedisStore`, `MongoDBStore`, `N5Store`.

## Compression (zarr.codecs)

```python
from zarr.codecs import BloscCodec, BloscShuffle, GzipCodec, ZstdCodec

# Default Blosc (zstd) is applied when compressors='default'
codec = BloscCodec(cname='zstd', clevel=5, shuffle=BloscShuffle.bitshuffle)
z = zarr.create_array('data.zarr', shape=(1000, 1000), chunks=(100, 100),
                      dtype='f4', compressors=codec)

# No compression
z = zarr.create_array('data.zarr', shape=(1000, 1000), chunks=(100, 100),
                      dtype='f4', compressors=None)
```

For **Zarr format 2** arrays, import codecs from `numcodecs` instead of `zarr.codecs`.

## Indexing

### Basic (NumPy-style)
```python
z[0:100, 0:100]
z[10:20, 50:60] = np.random.random((10, 10))
```

### Advanced (v3)
```python
z.vindex[[0, 5, 10], [2, 8, 15]]           # coordinate (convenience)
z.get_coordinate_selection([0, 5, 10])     # explicit API

z.oindex[0:10, [5, 10, 15]]                # orthogonal
z.get_orthogonal_selection((slice(0, 10), [5, 10, 15]))

z.blocks[0, 0]                             # chunk/block access
```

## Groups

```python
root = zarr.group('data.zarr')
grp = root.create_group('temperature')
arr = grp.create_array('t2m', shape=(365, 720, 1440), chunks=(1, 720, 1440), dtype='f4')
sub = root['temperature/t2m']

# v3 only — no create_dataset / require_dataset
arr2 = root.require_array('precip', shape=(100, 100), chunks=(10, 10), dtype='f4')
```

## Array properties and methods

```python
z.shape, z.chunks, z.dtype, z.size
z.nbytes          # uncompressed logical size
z.nbytes_stored   # stored (compressed) size
z.info            # summary string
z.resize((1500, 1500))   # tuple shape, not separate args
z.append(new_data, axis=0)
```

## Metadata consolidation

```python
zarr.consolidate_metadata('data.zarr')
root = zarr.open_consolidated('data.zarr')  # pass storage_options for cloud URIs
```

## Integration

```python
import dask.array as da
dask_arr = da.from_zarr('data.zarr')
da.to_zarr(dask_arr, 'output.zarr')

import xarray as xr
ds = xr.open_zarr('data.zarr')
ds.to_zarr('output.zarr')
```

## Thread / process safety (v3)

- Reads: safe without coordination.
- Writes: safe across workers when chunks do not overlap.
- `synchronizer=` / `ThreadSynchronizer` / `ProcessSynchronizer`: **not available in v3** (see migration reference).
- Tune Zarr's internal concurrency with `zarr.config.set({"async.concurrency": 8, "threading.max_workers": 8})`, especially when combining Zarr with Dask.

## Format versions

```python
z = zarr.create_array(..., zarr_format=3)  # default
z = zarr.create_array(..., zarr_format=2)  # legacy interop
```

## Common dtypes

`'f4'`, `'f8'`, `'i4'`, `'i8'`, `'u4'`, `'u8'`, `'bool'`, `'c8'`, `'c16'`

## Errors

```python
import zarr.errors
# PathNotFoundError, ReadOnlyError, GroupNotFoundError — see zarr.errors module
```

### `references/chunking_and_compression.md`

# Chunking and Compression

How to size chunks for an access pattern, sharding, the available codecs and Blosc
compressors, and recommended settings for numeric scientific data, for speed, and for
compression ratio.

## Chunking Strategies

Chunking is critical for performance. Choose chunk sizes and shapes based on access patterns.

### Chunk Size Guidelines

- **Minimum chunk size**: 1 MB recommended for optimal performance
- **Balance**: Larger chunks = fewer metadata operations; smaller chunks = better parallel access
- **Memory consideration**: Entire chunks must fit in memory during compression

```python
# Configure chunk size (aim for ~1MB per chunk)
# For float32 data: 1MB = 262,144 elements = 512×512 array
z = zarr.zeros(
    shape=(10000, 10000),
    chunks=(512, 512),  # ~1MB chunks
    dtype='f4'
)
```

### Aligning Chunks with Access Patterns

**Critical**: Chunk shape dramatically affects performance based on how data is accessed.

```python
# If accessing rows frequently (first dimension)
z = zarr.zeros((10000, 10000), chunks=(10, 10000))  # Chunk spans columns

# If accessing columns frequently (second dimension)
z = zarr.zeros((10000, 10000), chunks=(10000, 10))  # Chunk spans rows

# For mixed access patterns (balanced approach)
z = zarr.zeros((10000, 10000), chunks=(1000, 1000))  # Square chunks
```

**Performance example**: For a (200, 200, 200) array, reading along the first dimension:
- Using chunks (1, 200, 200): ~107ms
- Using chunks (200, 200, 1): ~1.65ms (65× faster!)

### Rectilinear Chunks and Sharding

Zarr 3.2 supports **rectilinear chunks** for uneven grids. Pass nested chunk lengths when a dimension has variable tile sizes:

```python
z = zarr.create_array(
    store="rectilinear.zarr",
    shape=(60, 100),
    chunks=([10, 20, 30], [50, 50]),
    dtype="f4",
)
```

When arrays have millions of small chunks, use **sharding** to group chunks into larger storage objects:

```python
# Create array with sharding
z = zarr.create_array(
    store='data.zarr',
    shape=(100000, 100000),
    chunks=(100, 100),  # Small chunks for access
    shards=(1000, 1000),  # Groups 100 chunks per shard
    dtype='f4'
)
```

**Benefits**:
- Reduces file system overhead from millions of small files
- Improves cloud storage performance (fewer object requests)
- Prevents filesystem block size waste

**Important**: Entire shards must fit in memory before writing.

## Compression

Zarr applies compression per chunk to reduce storage while maintaining fast access.

### Configuring Compression

```python
from zarr.codecs import BloscCodec, BloscShuffle, GzipCodec

# Default: Blosc with Zstandard
z = zarr.zeros((1000, 1000), chunks=(100, 100))  # Uses default compression

# Configure Blosc compression
z = zarr.create_array(
    store='data.zarr',
    shape=(1000, 1000),
    chunks=(100, 100),
    dtype='f4',
    compressors=BloscCodec(cname='zstd', clevel=5, shuffle=BloscShuffle.bitshuffle)
)

# Available Blosc compressors: 'blosclz', 'lz4', 'lz4hc', 'snappy', 'zlib', 'zstd'

# Use Gzip compression
z = zarr.create_array(
    store='data.zarr',
    shape=(1000, 1000),
    chunks=(100, 100),
    dtype='f4',
    compressors=GzipCodec(level=6)
)

# Disable compression
z = zarr.create_array(
    store='data.zarr',
    shape=(1000, 1000),
    chunks=(100, 100),
    dtype='f4',
    compressors=None
)
```

### Compression Performance Tips

- **Blosc** (default): Fast compression/decompression, good for interactive workloads
- **Zstandard**: Better compression ratios, slightly slower than LZ4
- **Gzip**: Maximum compression, slower performance
- **LZ4**: Fastest compression, lower ratios
- **Shuffle**: Enable shuffle filter for better compression on numeric data

```python
# Optimal for numeric scientific data
compressors=BloscCodec(cname='zstd', clevel=5, shuffle=BloscShuffle.bitshuffle)

# Optimal for speed
compressors=BloscCodec(cname='lz4', clevel=1)

# Optimal for compression ratio
compressors=GzipCodec(level=9)
```

### `references/integration.md`

# Integration, Parallelism, and Consolidated Metadata

Using Zarr with NumPy, Dask, and Xarray; thread safety and concurrency settings; and
consolidating metadata for fast opens on cloud storage.

## Integration with NumPy, Dask, and Xarray

### NumPy Integration

Zarr arrays implement the NumPy array interface:

```python
import numpy as np
import zarr

z = zarr.zeros((1000, 1000), chunks=(100, 100))

# Use NumPy functions directly
result = np.sum(z, axis=0)  # NumPy operates on Zarr array
mean = np.mean(z[:100, :100])

# Convert to NumPy array
numpy_array = z[:]  # Loads entire array into memory
```

### Dask Integration

Dask provides lazy, parallel computation on Zarr arrays:

```python
import dask.array as da
import zarr

# Create large Zarr array
z = zarr.open('data.zarr', mode='w', shape=(100000, 100000),
              chunks=(1000, 1000), dtype='f4')

# Load as Dask array (lazy, no data loaded)
dask_array = da.from_zarr('data.zarr')

# Perform computations (parallel, out-of-core)
result = dask_array.mean(axis=0).compute()  # Parallel computation

# Write Dask array to Zarr
large_array = da.random.random((100000, 100000), chunks=(1000, 1000))
da.to_zarr(large_array, 'output.zarr')
```

**Benefits**:
- Process datasets larger than memory
- Automatic parallel computation across chunks
- Efficient I/O with chunked storage

### Xarray Integration

Xarray provides labeled, multidimensional arrays with Zarr backend:

```python
import xarray as xr
import zarr

# Open Zarr store as Xarray Dataset (lazy loading)
ds = xr.open_zarr('data.zarr')

# Dataset includes coordinates and metadata
print(ds)

# Access variables
temperature = ds['temperature']

# Perform labeled operations
subset = ds.sel(time='2024-01', lat=slice(30, 60))

# Write Xarray Dataset to Zarr
ds.to_zarr('output.zarr')

# Create from scratch with coordinates
ds = xr.Dataset(
    {
        'temperature': (['time', 'lat', 'lon'], data),
        'precipitation': (['time', 'lat', 'lon'], data2)
    },
    coords={
        'time': pd.date_range('2024-01-01', periods=365),
        'lat': np.arange(-90, 91, 1),
        'lon': np.arange(-180, 180, 1)
    }
)
ds.to_zarr('climate_data.zarr')
```

**Benefits**:
- Named dimensions and coordinates
- Label-based indexing and selection
- Integration with pandas for time series
- NetCDF-like interface familiar to climate/geospatial scientists

## Parallel Computing and Thread Safety

Zarr uses async I/O internally. Tune concurrency for remote storage or Dask-heavy workloads:

```python
import zarr

# Higher values can improve remote throughput; lower values reduce pressure
# when Dask already supplies many worker threads.
zarr.config.set({
    "async.concurrency": 8,
    "threading.max_workers": 8,
})
```

The old `synchronizer` argument (`ThreadSynchronizer`, `ProcessSynchronizer`) is **not available in Zarr-Python 3**. Use these patterns instead:

- **Reads:** always safe across threads/processes.
- **Writes:** safe when each worker writes to **non-overlapping chunks**; most stores support atomic chunk writes.
- **Overlapping writes:** coordinate externally (file locks, workflow design) until synchronizers return.

For Dask-heavy workloads, estimate total concurrent I/O as roughly `dask_threads × async.concurrency` and lower Zarr's concurrency settings if the store or memory becomes saturated.

## Consolidated Metadata

For hierarchical stores with many arrays, consolidate metadata into a single file to reduce I/O operations:

```python
import zarr

# After creating arrays/groups
root = zarr.group('data.zarr')
# ... create multiple arrays/groups ...

# Consolidate metadata
zarr.consolidate_metadata('data.zarr')

# Open with consolidated metadata (faster, especially on cloud storage)
root = zarr.open_consolidated('data.zarr')
```

**Benefits**:
- Reduces metadata read operations from N (one per array) to 1
- Critical for cloud storage (reduces latency)
- Speeds up `tree()` operations and group traversal

**Cautions**:
- Metadata can become stale if arrays update without re-consolidation
- Not suitable for frequently-updated datasets
- Multi-writer scenarios may have inconsistent reads

### `references/performance_and_patterns.md`

# Performance, Patterns, and Troubleshooting

Performance optimization, array introspection and storage sizing, common patterns
(appendable time series, large matrices, format conversion), and common issues with
their fixes.

## Performance Optimization

### Checklist for Optimal Performance

1. **Chunk Size**: Aim for 1-10 MB per chunk
   ```python
   # For float32: 1MB = 262,144 elements
   chunks = (512, 512)  # 512×512×4 bytes = ~1MB
   ```

2. **Chunk Shape**: Align with access patterns
   ```python
   # Row-wise access → chunk spans columns: (small, large)
   # Column-wise access → chunk spans rows: (large, small)
   # Random access → balanced: (medium, medium)
   ```

3. **Compression**: Choose based on workload
   ```python
   # Interactive/fast: BloscCodec(cname='lz4')
   # Balanced: BloscCodec(cname='zstd', clevel=5)
   # Maximum compression: GzipCodec(level=9)
   ```

4. **Storage Backend**: Match to environment
   ```python
   # Local: LocalStore (default)
   # Cloud: fsspec URIs or FsspecStore + consolidated metadata
   # Temporary: MemoryStore
   ```

5. **Sharding**: Use for large-scale datasets
   ```python
   # When you have millions of small chunks
   shards=(10*chunk_size, 10*chunk_size)
   ```

6. **Parallel I/O**: Use Dask for large operations
   ```python
   import dask.array as da
   dask_array = da.from_zarr('data.zarr')
   result = dask_array.compute(scheduler='threads', num_workers=8)
   ```

### Profiling and Debugging

```python
# Print detailed array information
print(z.info)

# Output includes:
# - Type, shape, chunks, dtype
# - Serializer and compressors
# - Storage size (compressed vs uncompressed)
# - Storage location

# Check storage size
print(f"Compressed size: {z.nbytes_stored / 1e6:.2f} MB")
print(f"Uncompressed size: {z.nbytes / 1e6:.2f} MB")
print(f"Compression ratio: {z.nbytes / z.nbytes_stored:.2f}x")
```

## Common Patterns and Best Practices

### Pattern: Time Series Data

```python
# Store time series with time as first dimension
# This allows efficient appending of new time steps
z = zarr.open('timeseries.zarr', mode='a',
              shape=(0, 720, 1440),  # Start with 0 time steps
              chunks=(1, 720, 1440),  # One time step per chunk
              dtype='f4')

# Append new time steps
new_data = np.random.random((1, 720, 1440))
z.append(new_data, axis=0)
```

### Pattern: Large Matrix Operations

```python
import dask.array as da

# Create large matrix in Zarr
z = zarr.open('matrix.zarr', mode='w',
              shape=(100000, 100000),
              chunks=(1000, 1000),
              dtype='f8')

# Use Dask for parallel computation
dask_z = da.from_zarr('matrix.zarr')
result = (dask_z @ dask_z.T).compute()  # Parallel matrix multiply
```

### Pattern: Cloud-Native Workflow

```python
import zarr

path = "s3://my-bucket/data.zarr"
z = zarr.create_array(
    store=path,
    shape=(10000, 10000),
    chunks=(500, 500),
    dtype="f4",
    storage_options={"anon": False},
)
z[:] = data

zarr.consolidate_metadata(path)
z_read = zarr.open_consolidated(path, storage_options={"anon": False})
subset = z_read[0:100, 0:100]
```

### Pattern: Format Conversion

```python
# HDF5 to Zarr
import h5py
import zarr

with h5py.File('data.h5', 'r') as h5:
    dataset = h5['dataset_name']
    z = zarr.array(dataset[:],
                   chunks=(1000, 1000),
                   store='data.zarr')

# NumPy to Zarr
import numpy as np
data = np.load('data.npy')
z = zarr.array(data, chunks='auto', store='data.zarr')

# Zarr to NetCDF (via Xarray)
import xarray as xr
ds = xr.open_zarr('data.zarr')
ds.to_netcdf('data.nc')
```

## Common Issues and Solutions

### Issue: Slow Performance

**Diagnosis**: Check chunk size and alignment
```python
print(z.chunks)  # Are chunks appropriate size?
print(z.info)    # Check compression ratio
```

**Solutions**:
- Increase chunk size to 1-10 MB
- Align chunks with access pattern
- Try different compression codecs
- Use Dask for parallel operations

### Issue: High Memory Usage

**Cause**: Loading entire array or large chunks into memory

**Solutions**:
```python
# Don't load entire array
# Bad: data = z[:]
# Good: Process in chunks
for i in range(0, z.shape[0], 1000):
    chunk = z[i:i+1000, :]
    process(chunk)

# Or use Dask for automatic chunking
import dask.array as da
dask_z = da.from_zarr('data.zarr')
result = dask_z.mean().compute()  # Processes in chunks
```

### Issue: Cloud Storage Latency

**Solutions**:
```python
# 1. Consolidate metadata
zarr.consolidate_metadata(store)
z = zarr.open_consolidated(store)

# 2. Use appropriate chunk sizes (5-100 MB for cloud)
chunks = (2000, 2000)  # Larger chunks for cloud

# 3. Enable sharding
shards = (10000, 10000)  # Groups many chunks
```

### Issue: Concurrent Write Conflicts

**Solution**: Design workflows so each process/thread writes to separate chunks. Zarr-Python 3 does not yet support `ThreadSynchronizer` / `ProcessSynchronizer`; see `references/v3_migration.md`.

### `references/storage_backends.md`

# Storage Backends

LocalStore, MemoryStore, ZipStore, and fsspec-backed remote stores (S3, GCS), including
credential handling guidance.

## Storage Backends

Zarr supports multiple storage backends through a flexible storage interface.

### Local Filesystem (Default)

```python
from zarr.storage import LocalStore

# Explicit store creation
store = LocalStore('data/my_array.zarr')
z = zarr.open_array(store=store, mode='w', shape=(1000, 1000), chunks=(100, 100))

# Or use string path (creates LocalStore automatically)
z = zarr.open_array('data/my_array.zarr', mode='w', shape=(1000, 1000),
                    chunks=(100, 100))
```

### In-Memory Storage

```python
from zarr.storage import MemoryStore

# Create in-memory store
store = MemoryStore()
z = zarr.open_array(store=store, mode='w', shape=(1000, 1000), chunks=(100, 100))

# Data exists only in memory, not persisted
```

### ZIP File Storage

```python
from zarr.storage import ZipStore

# Write to ZIP file
store = ZipStore('data.zip', mode='w')
z = zarr.open_array(store=store, mode='w', shape=(1000, 1000), chunks=(100, 100))
z[:] = np.random.random((1000, 1000))
store.close()  # IMPORTANT: Must close ZipStore

# Read from ZIP file
store = ZipStore('data.zip', mode='r')
z = zarr.open_array(store=store)
data = z[:]
store.close()
```

### Cloud Storage (S3, GCS)

Zarr 3 uses **fsspec** backends via URI strings or `FsspecStore` (preferred over legacy `S3Map`/`GCSMap`).

```python
import zarr

# S3 — prefer IAM roles/profiles; fsspec handles provider credential discovery.
# Never print, log, or copy credential values into prompts or notebooks.
z = zarr.create_array(
    store="s3://my-bucket/path/to/array.zarr",
    shape=(1000, 1000),
    chunks=(100, 100),
    dtype="f4",
    storage_options={"anon": False},
)
z[:] = data

# GCS — prefer workload identity or gcloud application-default credentials.
z = zarr.open_array(
    "gs://my-bucket/path/to/array.zarr",
    mode="r",
    storage_options={"project": "my-project"},
)

# Explicit store (any fsspec filesystem)
from zarr.storage import FsspecStore
store = FsspecStore.from_url("s3://my-bucket/data.zarr", storage_options={"anon": False})
root = zarr.open_group(store=store, mode="r+")
```

Cloud backends read credentials through the provider SDK/fsspec backend. Do not inspect broad `.env` files; if a user explicitly needs help debugging auth, ask for redacted configuration and read only the named provider variables they approve. Treat all `import zarr`, `import dask`, `import h5py`, and `import xarray` examples as third-party package imports, not bundled script files.

**Cloud Storage Best Practices**:
- Use consolidated metadata to reduce latency: `zarr.consolidate_metadata(store)`
- Align chunk sizes with cloud object sizing (typically 5-100 MB optimal)
- Enable parallel writes using Dask for large-scale data
- Consider sharding to reduce number of objects

### `references/v3_migration.md`

# Zarr-Python 3 Migration Quick Reference

Targets **zarr 3.2.x** (current stable: **3.2.1**, released 2026-05-05). Official guide: [3.0 Migration Guide](https://zarr.readthedocs.io/en/stable/user-guide/v3_migration/).

## Version and format defaults

| Topic | Zarr-Python 2 | Zarr-Python 3 |
|-------|---------------|---------------|
| Pin while migrating downstream | `zarr>=2,<3` | `zarr>=3,<4` |
| Default on-disk format | Zarr v2 | Zarr v3 (`zarr_format=3`) |
| Write v2-compatible data | default | `zarr_format=2` on create/open |
| Python requirement | 3.9–3.11 (late 2.x) | **3.12+** (3.2.1 on PyPI) |

```python
# Keep writing Zarr format 2 arrays (interop with older tools)
z = zarr.create_array(store="data.zarr", shape=(1000, 1000), chunks=(100, 100),
                      dtype="f4", zarr_format=2)
```

## Store imports and backends

```python
# v3 — stores live under zarr.storage
from zarr.storage import LocalStore, MemoryStore, ZipStore, FsspecStore
```

| v2 | v3 |
|----|-----|
| `DirectoryStore` | `LocalStore` |
| `FSStore` | `FsspecStore` |
| `TempStore` | `tempfile.TemporaryDirectory` + `LocalStore` |
| `S3Map` / `GCSMap` (s3fs/gcsfs) | Prefer `FsspecStore` or URI strings (see below) |
| `DBMStore`, `LMDBStore`, `SQLiteStore`, `RedisStore`, `MongoDBStore` | Removed — use `FsspecStore` or custom store |

### Cloud storage (recommended v3 pattern)

```python
import zarr

# URI + storage_options (requires s3fs for S3)
root = zarr.open_group(
    store="s3://my-bucket/path/data.zarr",
    mode="r",
    storage_options={"anon": False},  # provider credentials are handled by fsspec
)

# Explicit FsspecStore
from zarr.storage import FsspecStore
store = FsspecStore.from_url("s3://my-bucket/path/data.zarr", storage_options={"anon": False})
root = zarr.open_group(store=store, mode="r")
```

Install remote I/O extras with pinned versions in production projects, for example: `uv pip install "zarr[remote]==3.2.1" "s3fs==2026.4.0" "gcsfs==2026.5.0"`. Zarr's `remote` extra pulls fsspec; add the protocol backend needed by the target store.

## Codecs and compression

- Zarr v3 arrays: use `zarr.codecs.*` (e.g. `BloscCodec`, `GzipCodec`) via `compressors=` on `create_array`.
- Zarr v2 arrays: `numcodecs` codecs still work; import from `numcodecs`, not `zarr.*`.
- `compressor=` kwarg on creation functions → use `compressors=` in v3.
- Disable compression with `compressors=None`; `BytesCodec` is the serializer, not the "no compression" setting.

```python
from zarr.codecs import BloscCodec, BloscShuffle

z = zarr.create_array(
    store="data.zarr", shape=(1000, 1000), chunks=(100, 100), dtype="f4",
    compressors=BloscCodec(cname="zstd", clevel=5, shuffle=BloscShuffle.bitshuffle),
)
```

## Groups and h5py-style API

| v2 (removed in v3) | v3 replacement |
|--------------------|----------------|
| `group.create_dataset(...)` | `group.create_array(...)` |
| `group.require_dataset(...)` | `group.require_array(...)` |
| `group.foo` attribute access | `group["foo"]` only |
| `zarr.storage.init_group(...)` | `zarr.open_group(...)` or `zarr.create_group(...)` |

## Array operations

```python
# resize — pass a shape tuple, not separate dimension args
z.resize((15000, 15000))  # not z.resize(15000, 15000)
```

Advanced indexing: `vindex`, `oindex`, and `blocks` remain as convenience properties; equivalent methods are `get_coordinate_selection`, `get_orthogonal_selection`, etc.

### Rectilinear chunks (3.2+)

Zarr 3.2 adds support for rectilinear chunk grids. Existing regular chunk tuples still work, but you can now pass nested chunk lengths when chunk boundaries vary by dimension:

```python
z = zarr.create_array(
    store="rectilinear.zarr",
    shape=(60, 100),
    chunks=([10, 20, 30], [50, 50]),
    dtype="f4",
)
```

### Metadata migration CLI (3.1.3+)

For v2 stores that need v3 metadata, use the Zarr CLI non-destructively first:

```bash
zarr migrate v3 path/to/input.zarr path/to/output.zarr
zarr migrate v3 path/to/input.zarr --dry-run
```

Only remove v2 metadata after downstream readers have been tested:

```bash
zarr remove-metadata v2 path/to/input.zarr
```

## Not yet ported to v3 (avoid or expect errors)

From the [migration guide WIP list](https://zarr.readthedocs.io/en/stable/user-guide/v3_migration/#work-in-progress):

- `synchronizer` argument (`ThreadSynchronizer`, `ProcessSynchronizer`) — use separate chunks per writer or external coordination; see [performance guide — thread safety](https://zarr.readthedocs.io/en/stable/user-guide/performance/).
- `zarr.copy`, `zarr.copy_all`, `zarr.copy_store`, `Group.move`
- Object dtypes, ragged arrays, `cache_attrs`, `cache_metadata`, `chunk_store`

## Zarr-Python 2 support

For legacy workflows, choose an exact `zarr==2.x.y` release from the support-v2 release notes and commit a lockfile. Maintenance lives on the `support/v2` branch (security fixes for ~6 months after 3.0).
