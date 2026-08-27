---
name: optimize-for-gpu
description: GPU-accelerates scientific Python on NVIDIA hardware and verifies that the result is correct and faster. Use for CUDA/GPU optimization; CPU-bound NumPy, SciPy, pandas, scikit-learn, NetworkX, scikit-image, vector-search, image-processing, graph, simulation, or file-I/O workloads; CuPy, cuDF, cuML, cuGraph, cuVS, cuCIM, KvikIO, Warp, Newton, Numba-CUDA, or RAFT questions; and profiling, memory-transfer, kernel, or multi-GPU bottlenecks. Also use when large data-parallel Python code is slow and GPU acceleration is a plausible option, even if the user does not name CUDA.
---

# GPU Optimization for Python with NVIDIA

Treat GPU acceleration as an evidence-driven optimization, not an automatic rewrite. Preserve the
user's numerical and algorithmic contract, measure with representative data, and keep the GPU
version only when synchronized end-to-end benchmarks show a useful improvement.

## When This Skill Applies

- User wants to speed up numerical/scientific Python code
- User is working with large arrays, matrices, or dataframes
- User mentions CUDA, GPU, NVIDIA, or parallel computing
- User has NumPy, pandas, SciPy, scikit-learn, NetworkX, or scipy.sparse.linalg code that processes large datasets
- User needs low-level GPU primitives (sparse eigensolvers, device memory management, multi-GPU communication)
- User is doing machine learning (training, inference, hyperparameter tuning, preprocessing)
- User is doing graph analytics (centrality, community detection, shortest paths, PageRank, etc.)
- User is doing vector search, nearest neighbor search, similarity search, or building a RAG pipeline
- User has Faiss, Annoy, ScaNN, or sklearn NearestNeighbors code that could be GPU-accelerated
- User wants GPU-accelerated interactive dashboards, cross-filtering, or exploratory data analysis on large datasets
- User is doing geospatial analysis (point-in-polygon, spatial joins, trajectory analysis, distance calculations) with GeoPandas or shapely
- User is doing image processing, computer vision, or medical imaging (filtering, segmentation, morphology, feature detection) with scikit-image or OpenCV
- User is working with whole-slide images (WSI), digital pathology, microscopy, or remote sensing imagery
- User is loading large binary data files into GPU memory (numpy.fromfile → cupy, or Python open() → GPU array)
- User needs to read files from S3, HTTP, or WebHDFS directly into GPU memory
- User mentions GPUDirect Storage (GDS) or wants to bypass CPU-memory staging for file IO
- User is doing physics simulation (particles, cloth, fluids, rigid bodies) or differentiable simulation
- User needs mesh operations (ray casting, closest-point queries, signed distance fields) or geometry processing on GPU
- User is doing robotics (kinematics, dynamics, control) with transforms and quaternions
- User has Python simulation loops that could be JIT-compiled to GPU kernels
- User mentions NVIDIA Warp or wants differentiable GPU simulation integrated with PyTorch/JAX
- User is doing simulations, signal processing, financial modeling, bioinformatics, physics, or any compute-intensive work
- User wants to optimize existing code and GPU acceleration is the right answer

## Choose the Smallest Suitable Layer

Prefer a maintained library implementation over a custom kernel:

| Existing workload | Preferred path | Use for |
| --- | --- | --- |
| NumPy / SciPy | **CuPy** | arrays, sparse matrices, linear algebra, FFTs, signal processing |
| pandas | **cudf.pandas**, then **cuDF** | accelerator mode first; native API for more control |
| scikit-learn | **cuml.accel**, then **cuML** | accelerator mode first; native estimators as needed |
| NetworkX | **nx-cugraph**, then **cuGraph** | backend dispatch first; native graph API at scale |
| scikit-image | **cuCIM** | GPU image processing and whole-slide imaging |
| Faiss / Annoy / k-NN | **cuVS** | exact and approximate vector search |
| Raw or remote file I/O | **KvikIO** | GPU buffers and GPUDirect Storage |
| Custom array kernels | **Numba-CUDA-MLIR** for new work; **Numba-CUDA** for existing code | explicit SIMT kernels and shared memory |
| Spatial or differentiable kernels | **Warp** | geometry, simulation kernels, robotics, autodiff |
| High-level physics simulation | **Newton** | maintained engine that succeeds the removed `warp.sim` module |
| Low-level RAPIDS primitives | **RAFT** (`pylibraft`) | sparse eigensolvers, resources, multi-GPU building blocks |

Do not move code out of PyTorch, JAX, TensorFlow, or another GPU-native framework merely to use
one of these libraries. First remove CPU round trips and use the framework's compiler, profiler,
mixed-precision, and batching facilities.

Treat these as legacy-only:

| Project | Status | Guidance |
| --- | --- | --- |
| **cuxfilter** | Final release 26.06 | Maintain existing dashboards only. For new work, combine cuDF with HoloViews/hvPlot/Datashader and serve with Panel, Dash, Streamlit, or Bokeh. |
| **cuSpatial** | Archived at 25.04 | Use only in an isolated legacy environment. For new work, keep geometry in GeoPandas/Shapely and accelerate compatible tabular stages with cuDF. |

Full per-library guidance, including when each is the *wrong* choice and how to combine
them, is in [references/decision_framework.md](references/decision_framework.md).
Install commands and CUDA version selection are in
[references/installation.md](references/installation.md). Before/after conversions for
every library are in
[references/code_transformation_patterns.md](references/code_transformation_patterns.md).

## Optimization Workflow

### 1. Define the contract and baseline

- Capture a representative input, expected output, and acceptable numerical tolerance.
- Measure the current end-to-end path, including input, transfers, compute, and output.
- Profile before changing code. Use CPU profilers for CPU code and identify whether the real limit
  is compute, memory bandwidth, allocation, transfer, synchronization, or storage.
- Record hardware, package versions, dtypes, shapes, batch size, and warm-up policy with results.

### 2. Check suitability before porting

GPU execution is promising when the hot path exposes substantial independent work, runs often
enough to amortize initialization and transfer, and has a working set that fits available device
memory with room for temporaries. Keep a CPU path when the workload is small, mostly sequential,
dominated by unsupported operations, or requires frequent host-device round trips.

Do not use fixed row-count thresholds as proof. Benchmark the user's actual shapes and hardware.
For out-of-core data, estimate peak working memory and choose chunking, Dask, or a streaming design
before allocating.

### 3. Try the least disruptive implementation

1. If the code already uses a GPU-native framework, optimize within that framework.
2. Try accelerator or backend modes (`cudf.pandas`, `cuml.accel`, `nx-cugraph`).
3. Move to a native GPU API only where accelerator coverage or performance is insufficient.
4. Write a custom kernel only when profiling shows an operation without a suitable library
   implementation.

Read the relevant library reference before writing code; compatible names can still differ in
defaults, dtypes, output types, and supported arguments.

### 4. Keep a coherent GPU data path

- Transfer inputs once and keep intermediates device-resident.
- Reuse allocations and prefer `out=` or in-place forms when semantics allow.
- Batch small operations; fuse elementwise work when it removes intermediate arrays.
- Use pinned host memory and non-default streams only after profiling shows transfer overlap matters.
- Choose `float32`, mixed precision, or reduced-precision storage only when the contract permits it.

### 5. Validate semantics before speed

- Compare CPU and GPU outputs on small deterministic fixtures and representative data.
- Use explicit tolerances for floating-point results and test edge cases, NaNs, ordering, and dtypes.
- For approximate nearest-neighbor indexes, report recall@k against exact search; do not compare an
  exact CPU algorithm with an approximate GPU algorithm as if they were equivalent.
- Check accelerator warnings and logs for CPU fallback.

### 6. Benchmark GPU code correctly

GPU work is asynchronous, so a CPU timer around an unsynchronized call measures enqueue time.
Warm up context creation and JIT compilation, then use CUDA events or a library-aware timer:

```python
from cupyx.profiler import benchmark

print(benchmark(gpu_function, (arg1, arg2), n_warmup=10, n_repeat=100))
```

Use `%gpu_timeit` in notebooks, Nsight Systems (`nsys`) for end-to-end timelines, and Nsight
Compute (`ncu`) for kernel analysis. Report both synchronized kernel/region time and realistic
end-to-end latency; include transfer and conversion costs when production pays them.

### 7. Keep, revise, or reject the port

Retain the GPU path only when it passes correctness checks and improves the metric the user cares
about on representative data. If it does not, explain whether the limiting factor is problem size,
transfers, unsupported fallback, memory pressure, launch granularity, or the algorithm itself.

## Important Notes

- Provide a CPU fallback when the application requires portability; otherwise fail early with a
  clear hardware and dependency error.
- Test numerical correctness against CPU results (GPU floating point may differ slightly due to operation ordering)
- GPU memory is limited — for datasets larger than GPU memory, consider chunking or using RAPIDS Dask for multi-GPU
- Prefer the CUDA Array Interface or DLPack for supported zero-copy interchange, but verify device,
  dtype, contiguity, ownership, and stream semantics rather than assuming every conversion is free.

## Reference Files

Before writing any GPU optimization code, read the relevant reference file(s):

| File | When to Read |
|------|-------------|
| `references/cupy.md` | User has NumPy/SciPy code, or needs array operations on GPU |
| `references/numba.md` | User has existing Numba-CUDA code or needs explicit SIMT kernels; note the migration path to Numba-CUDA-MLIR |
| `references/cudf.md` | User has pandas code, or needs dataframe operations on GPU |
| `references/cuml.md` | User has scikit-learn code, or needs ML training/inference/preprocessing on GPU |
| `references/cugraph.md` | User has NetworkX code, or needs graph analytics on GPU |
| `references/warp.md` | User needs GPU kernels for simulation, spatial computing, mesh/volume queries, differentiable programming, or robotics; use Newton for a high-level physics engine |
| `references/kvikio.md` | User needs high-performance file IO to/from GPU, GPUDirect Storage, reading S3/HTTP to GPU, or Zarr on GPU |
| `references/cuxfilter.md` | User maintains or explicitly requests cuxfilter (sunset — 26.06 is the final release) |
| `references/cucim.md` | User has scikit-image code, or needs image processing, digital pathology, or WSI reading on GPU |
| `references/cuvs.md` | User needs vector search, nearest neighbors, similarity search, or RAG retrieval on GPU |
| `references/cuspatial.md` | User maintains or explicitly requests cuSpatial (archived — frozen at 25.04 and isolated from current RAPIDS) |
| `references/raft.md` | User needs sparse eigensolvers, device memory management, or multi-GPU primitives |

Read the specific reference before writing code — they contain detailed API patterns, optimization techniques, and pitfalls specific to each library.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/optimize-for-gpu/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/code_transformation_patterns.md`

# Code Transformation Patterns

Before/after conversions: NumPy to CuPy, pandas to cuDF, a custom loop to a Numba CUDA
kernel, NetworkX to cuGraph, scikit-learn to cuML, a simulation loop to a Warp kernel,
file IO to KvikIO, maintained GPU-backed dashboards, scikit-image to cuCIM, legacy
GeoPandas-to-cuSpatial point-in-polygon, exact Faiss to exact cuVS search, and
`scipy.sparse.linalg` to RAFT.

When converting existing CPU code, apply these patterns:

### NumPy to CuPy
```python
# Before (CPU)
import numpy as np
a = np.random.rand(10_000_000)
b = np.fft.fft(a)
c = np.sort(b.real)

# After (GPU) — often just change the import
import cupy as cp
a = cp.random.rand(10_000_000)
b = cp.fft.fft(a)
c = cp.sort(b.real)
```

### pandas to cuDF
```python
# Before (CPU)
import pandas as pd
df = pd.read_parquet("large_data.parquet")
result = df.groupby("category")["value"].mean()

# After (GPU) — change the import
import cudf
df = cudf.read_parquet("large_data.parquet")
result = df.groupby("category")["value"].mean()

# Or zero-code-change: python -m cudf.pandas your_script.py
```

### Custom loop to Numba CUDA kernel
```python
# Before (CPU) — slow Python loop
def process(data, out):
    for i in range(len(data)):
        out[i] = math.sin(data[i]) * math.exp(-data[i])

# After (GPU) — Numba kernel
from numba import cuda
import math

@cuda.jit
def process(data, out):
    i = cuda.grid(1)
    if i < data.size:
        out[i] = math.sin(data[i]) * math.exp(-data[i])

d_data = cuda.to_device(data)
d_out = cuda.device_array(d_data.shape, dtype=d_data.dtype)
threads = 256
blocks = (len(data) + threads - 1) // threads
process[blocks, threads](d_data, d_out)
out = d_out.copy_to_host()
```

### NetworkX to cuGraph
```python
# Before (CPU)
import networkx as nx
G = nx.read_edgelist("edges.csv", delimiter=",", nodetype=int)
pr = nx.pagerank(G)
bc = nx.betweenness_centrality(G)

# After (GPU) — direct cuGraph API
import cugraph
import cudf
edges = cudf.read_csv("edges.csv", names=["src", "dst"], dtype=["int32", "int32"])
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="src", destination="dst")
pr = cugraph.pagerank(G)
bc = cugraph.betweenness_centrality(G)

# Or zero-code-change: NX_CUGRAPH_AUTOCONFIG=True python your_script.py
```

### scikit-learn to cuML
```python
# Before (CPU)
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# After (GPU) — change the imports
from cuml.ensemble import RandomForestClassifier
from cuml.preprocessing import StandardScaler
from cuml.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Or zero-code-change: python -m cuml.accel your_script.py
```

### Simulation loop to Warp kernel
```python
# Before (CPU) — slow Python loop over particles
import numpy as np

def integrate(positions, velocities, forces, dt):
    for i in range(len(positions)):
        velocities[i] += forces[i] * dt
        positions[i] += velocities[i] * dt

# After (GPU) — Warp kernel, JIT-compiled to CUDA
import warp as wp

@wp.kernel
def integrate(positions: wp.array(dtype=wp.vec3),
              velocities: wp.array(dtype=wp.vec3),
              forces: wp.array(dtype=wp.vec3),
              dt: float):
    tid = wp.tid()
    velocities[tid] = velocities[tid] + forces[tid] * dt
    positions[tid] = positions[tid] + velocities[tid] * dt

wp.launch(integrate, dim=num_particles,
          inputs=[positions, velocities, forces, 0.01], device="cuda")
```

### File IO to GPU with KvikIO
```python
# Before — CPU staging (disk → CPU → GPU)
import numpy as np
import cupy as cp

data = np.fromfile("data.bin", dtype=np.float32)
gpu_data = cp.asarray(data)  # Extra copy through CPU memory

# After — direct to GPU (disk → GPU via GDS)
import cupy as cp
import kvikio

gpu_data = cp.empty(1_000_000, dtype=cp.float32)
with kvikio.CuFile("data.bin", "r") as f:
    f.read(gpu_data)  # Bypasses CPU memory with GPUDirect Storage

# Reading from S3 directly to GPU
with kvikio.RemoteFile.open_s3_url("s3://bucket/data.bin") as f:
    buf = cp.empty(f.nbytes() // 4, dtype=cp.float32)
    f.read(buf)
```

### GPU-backed dashboard with maintained libraries

cuxfilter ended with RAPIDS 26.06. Do not start a new application with it. Keep large
transformations and aggregations in cuDF, then transfer only the compact display data at an
explicit visualization boundary:

```python
# Before — static matplotlib/seaborn plots, no interactivity
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet("large_dataset.parquet")
fig, axes = plt.subplots(1, 2)
df.plot.scatter(x="feature1", y="feature2", ax=axes[0])
df["category"].value_counts().plot.bar(ax=axes[1])
plt.show()

# After — GPU data preparation plus a maintained dashboard stack
import cudf
import hvplot.pandas  # Registers .hvplot on pandas objects
import panel as pn

gpu_df = cudf.read_parquet("large_dataset.parquet")
gpu_summary = (
    gpu_df.groupby("category", as_index=False)
    .agg({"value_col": "mean"})
)
display_summary = gpu_summary.to_pandas()  # Transfer only the reduced result
dashboard = pn.Column(
    "# Interactive Explorer",
    display_summary.hvplot.bar(x="category", y="value_col"),
)
dashboard.servable()
```

For linked selections over detailed points, use HoloViews/hvPlot with Datashader and Panel.
Keep filter/aggregation callbacks on the GPU where practical, and document every conversion to
pandas. Read the cuxfilter reference only when maintaining an existing 26.06 application.

### scikit-image to cuCIM
```python
# Before (CPU)
from skimage.filters import gaussian, sobel, threshold_otsu
from skimage.morphology import binary_opening, disk
from skimage.measure import label, regionprops_table
import numpy as np

blurred = gaussian(image, sigma=3)
binary = blurred > threshold_otsu(blurred)
cleaned = binary_opening(binary, footprint=disk(3))
labels = label(cleaned)
props = regionprops_table(labels, image, properties=['area', 'centroid'])

# After (GPU) — change imports, wrap input with cp.asarray
from cucim.skimage.filters import gaussian, sobel, threshold_otsu
from cucim.skimage.morphology import binary_opening, disk
from cucim.skimage.measure import label, regionprops_table
import cupy as cp

image_gpu = cp.asarray(image)  # Transfer once
blurred = gaussian(image_gpu, sigma=3)
binary = blurred > threshold_otsu(blurred)
cleaned = binary_opening(binary, footprint=disk(3))
labels = label(cleaned)
props = regionprops_table(labels, image_gpu, properties=['area', 'centroid'])
```

### GeoPandas point-in-polygon to cuSpatial (legacy 25.04 only)

cuSpatial is archived and incompatible with current RAPIDS packages. Use this only in an isolated
environment pinned to 25.04. `point_in_polygon` returns a boolean membership matrix; it is not a
drop-in replacement for `geopandas.sjoin`.

```python
# Before (CPU)
import geopandas as gpd
import numpy as np
from shapely.geometry import Point

points = gpd.GeoSeries([Point(x, y) for x, y in coords], crs="EPSG:4326")
polygons = gpd.read_file("regions.geojson").geometry.iloc[:31]
membership_cpu = np.column_stack(
    [points.within(polygon).to_numpy() for polygon in polygons]
)

# After (GPU, legacy) — same point-by-polygon membership semantics
import cuspatial

points_gpu = cuspatial.from_geopandas(points)
polygons_gpu = cuspatial.from_geopandas(polygons)
membership_gpu = cuspatial.point_in_polygon(points_gpu, polygons_gpu)
```

### Exact Faiss search to exact cuVS search

Match algorithmic semantics before benchmarking. Use cuVS brute force for an exact Faiss
`IndexFlatL2` baseline; use CAGRA only when approximate results are acceptable and report recall@k
against this exact ground truth.

```python
# Before (CPU) — Faiss
import faiss
import numpy as np

rng = np.random.default_rng(42)
embeddings = rng.random((1_000_000, 128), dtype=np.float32)
queries = rng.random((1_000, 128), dtype=np.float32)
index = faiss.IndexFlatL2(128)
index.add(embeddings)
distances, neighbors = index.search(queries, k=10)

# After (GPU) — cuVS exact brute-force search
import cupy as cp
from cuvs.neighbors import brute_force

embeddings_gpu = cp.asarray(embeddings)
queries_gpu = cp.asarray(queries)
index_gpu = brute_force.build(embeddings_gpu, metric="sqeuclidean")
distances_gpu, neighbors_gpu = brute_force.search(index_gpu, queries_gpu, k=10)
```

### scipy.sparse.linalg to RAFT
```python
# Before (CPU)
import numpy as np
from scipy.sparse import random as sparse_random
from scipy.sparse.linalg import eigsh

A = sparse_random(10000, 10000, density=0.01, format="csr", dtype=np.float32)
A = A + A.T  # Make symmetric
eigenvalues, eigenvectors = eigsh(A, k=10, which="LM")

# After (GPU) — RAFT sparse eigensolver
import cupy as cp
import cupyx.scipy.sparse as sp_gpu
from pylibraft.sparse.linalg import eigsh as gpu_eigsh

A_gpu = sp_gpu.csr_matrix(A)  # Transfer to GPU
eigenvalues, eigenvectors = gpu_eigsh(A_gpu, k=10, which="LM")
```

### `references/cucim.md`

# cuCIM Reference

cuCIM (CUDA Clara IMage) is NVIDIA's GPU-accelerated computer vision and image processing library
within the RAPIDS ecosystem. Its `cucim.skimage` module mirrors a substantial part of scikit-image
on CuPy arrays, and `cucim.CuImage` reads tiled whole-slide images. Verify function coverage and
benchmark the actual image sizes, storage path, and processing chain.

> **Full documentation:** https://docs.rapids.ai/api/cucim/stable/
> **GitHub:** https://github.com/rapidsai/cucim

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Core Concept: CuPy Arrays](#core-concept-cupy-arrays)
3. [cucim.skimage — GPU scikit-image](#cucimskimage)
4. [Color Operations](#color-operations)
5. [Exposure and Histogram](#exposure-and-histogram)
6. [Feature Detection](#feature-detection)
7. [Filters](#filters)
8. [Measure and Region Properties](#measure-and-region-properties)
9. [Morphology](#morphology)
10. [Segmentation](#segmentation)
11. [Registration](#registration)
12. [Restoration](#restoration)
13. [Transform](#transform)
14. [Metrics](#metrics)
15. [Utility Functions](#utility-functions)
16. [cucim.core.operations — NVIDIA-Specific](#cucimcoreoperations)
17. [Whole-Slide Image Reading (cucim.clara)](#whole-slide-image-reading)
18. [Performance Characteristics](#performance-characteristics)
19. [Interoperability](#interoperability)
20. [Known Limitations vs scikit-image](#known-limitations-vs-scikit-image)
21. [Common Migration Patterns](#common-migration-patterns)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add --extra-index-url=https://pypi.nvidia.com "cucim-cu12==26.6.*"    # For CUDA 12.x
uv add --extra-index-url=https://pypi.nvidia.com "cucim-cu13==26.6.*"    # For CUDA 13.x
```

cuCIM wheels are also published directly to PyPI, so the extra index is optional.

**Platform:** Linux only (x86-64 and aarch64) — no Windows or macOS GPU support.
**Requires:** NVIDIA GPU with CUDA 12.x or 13.x, Python 3.11+, CuPy, NumPy, SciPy, scikit-image.

Verify:
```python
import cucim
print(cucim.__version__)

import cupy as cp
from cucim.skimage.filters import gaussian
img = cp.random.rand(512, 512).astype(cp.float32)
result = gaussian(img, sigma=3)
print(f"Filtered image shape: {result.shape}")  # Should work on GPU
```

---

## Core Concept: CuPy Arrays

cuCIM operates natively on **CuPy arrays**. All `cucim.skimage` functions accept CuPy arrays as input and return CuPy arrays as output — zero-copy, all on GPU.

```python
import cupy as cp
import numpy as np
from cucim.skimage.filters import gaussian

# Transfer image to GPU once
image_gpu = cp.asarray(numpy_image)

# All processing stays on GPU — zero-copy between cuCIM calls
blurred = gaussian(image_gpu, sigma=3)
# ... more processing on GPU ...

# Transfer back to CPU only when needed (for display, save, etc.)
result_cpu = cp.asnumpy(blurred)
```

**Best practice:** Move data to GPU once at the start, chain all cuCIM operations on GPU, then transfer back to CPU only at the end.

---

## cucim.skimage

The `cucim.skimage` module mirrors scikit-image's module structure. In most cases, replace `from skimage` with `from cucim.skimage` and pass CuPy arrays instead of NumPy arrays.

```python
# Before (CPU — scikit-image)
from skimage.filters import gaussian
import numpy as np
result = gaussian(numpy_image, sigma=3)

# After (GPU — cuCIM)
from cucim.skimage.filters import gaussian
import cupy as cp
result = gaussian(cp.asarray(numpy_image), sigma=3)
```

---

## Color Operations

`cucim.skimage.color` — 42 GPU-accelerated color space conversion functions.

```python
from cucim.skimage.color import rgb2gray, rgb2hsv, rgb2lab, label2rgb
from cucim.skimage.color import separate_stains, combine_stains

# Color space conversions
gray = rgb2gray(rgb_image_gpu)
hsv = rgb2hsv(rgb_image_gpu)
lab = rgb2lab(rgb_image_gpu)

# Stain separation (for H&E histology)
stains = separate_stains(rgb_image_gpu, stain_matrix)
```

**Available conversions:** `rgb2gray`, `rgb2hsv`, `hsv2rgb`, `rgb2lab`, `lab2rgb`, `rgb2xyz`, `xyz2rgb`, `rgb2luv`, `luv2rgb`, `rgb2ycbcr`, `ycbcr2rgb`, `rgb2yuv`, `yuv2rgb`, `rgb2yiq`, `yiq2rgb`, `rgb2hed`, `hed2rgb`, `rgb2rgbcie`, `rgbcie2rgb`, `gray2rgb`, `gray2rgba`, `rgba2rgb`, `convert_colorspace`, `label2rgb`

**Color difference:** `deltaE_cie76`, `deltaE_ciede94`, `deltaE_ciede2000`, `deltaE_cmc`

---

## Exposure and Histogram

`cucim.skimage.exposure` — histogram equalization, contrast adjustment.

```python
from cucim.skimage.exposure import (
    equalize_hist, equalize_adapthist,
    rescale_intensity, adjust_gamma, adjust_log, adjust_sigmoid,
    histogram, match_histograms, is_low_contrast
)

# CLAHE (Contrast Limited Adaptive Histogram Equalization)
enhanced = equalize_adapthist(image_gpu, clip_limit=0.03)

# Gamma correction
brightened = adjust_gamma(image_gpu, gamma=0.5)

# Rescale intensity to [0, 1]
normalized = rescale_intensity(image_gpu)

# Histogram matching between two images
matched = match_histograms(source_gpu, reference_gpu)
```

---

## Feature Detection

`cucim.skimage.feature` — edge, corner, and blob detection.

```python
from cucim.skimage.feature import (
    canny, corner_harris, corner_peaks,
    blob_dog, blob_doh, blob_log,
    structure_tensor, hessian_matrix, hessian_matrix_det,
    match_template, peak_local_max, daisy, multiscale_basic_features
)

# Canny edge detection
edges = canny(gray_image_gpu, sigma=2.0)

# Harris corner detection
corners = corner_harris(gray_image_gpu)
corner_coords = corner_peaks(corners, min_distance=5)

# Blob detection (Difference of Gaussian)
blobs = blob_dog(gray_image_gpu, max_sigma=30, threshold=0.1)

# Template matching
result = match_template(image_gpu, template_gpu)
```

---

## Filters

`cucim.skimage.filters` — 47 GPU-accelerated filter functions. This is one of the most commonly used modules.

```python
from cucim.skimage.filters import (
    gaussian, median, sobel, laplace, unsharp_mask,
    frangi, hessian, meijering, sato,
    threshold_otsu, threshold_multiotsu, threshold_sauvola,
    gabor, difference_of_gaussians, butterworth
)

# Gaussian blur
blurred = gaussian(image_gpu, sigma=3)

# Sobel edge detection
edges = sobel(gray_image_gpu)

# Unsharp mask (sharpening)
sharpened = unsharp_mask(image_gpu, radius=5, amount=2.0)

# Vessel/ridge detection (for medical imaging)
vessels = frangi(gray_image_gpu, sigmas=range(1, 10))

# Otsu thresholding
threshold = threshold_otsu(gray_image_gpu)
binary = gray_image_gpu > threshold

# Multi-level Otsu
thresholds = threshold_multiotsu(gray_image_gpu, classes=3)
```

**Edge detection:** `sobel`, `scharr`, `prewitt`, `roberts`, `farid`, `laplace` (plus `_h`/`_v` variants)

**Smoothing:** `gaussian`, `median`, `unsharp_mask`

**Ridge/vessel detection:** `frangi`, `hessian`, `meijering`, `sato`

**Thresholding (10 methods):** `threshold_otsu`, `threshold_isodata`, `threshold_li`, `threshold_mean`, `threshold_minimum`, `threshold_multiotsu`, `threshold_niblack`, `threshold_sauvola`, `threshold_triangle`, `threshold_yen`

**Frequency domain:** `butterworth`, `wiener`

---

## Measure and Region Properties

`cucim.skimage.measure` — labeling, region properties, and shape metrics.

```python
from cucim.skimage.measure import label, regionprops, regionprops_table
from cucim.skimage.measure import moments, moments_central, moments_hu
from cucim.skimage.measure import block_reduce, shannon_entropy

# Connected component labeling
labels = label(binary_image_gpu)

# Region properties (area, centroid, bounding box, etc.)
props = regionprops(labels)
table = regionprops_table(labels, intensity_image=gray_gpu,
                          properties=['area', 'centroid', 'mean_intensity'])

# Block reduce (downsampling)
downsampled = block_reduce(image_gpu, block_size=(2, 2), func=cp.mean)
```

**Colocalization metrics** (for microscopy): `manders_coloc_coeff`, `manders_overlap_coeff`, `pearson_corr_coeff`, `intersection_coeff`

---

## Morphology

`cucim.skimage.morphology` — 30 GPU-accelerated morphological operations.

```python
from cucim.skimage.morphology import (
    binary_erosion, binary_dilation, binary_opening, binary_closing,
    erosion, dilation, opening, closing,
    white_tophat, black_tophat,
    disk, diamond, ball, star,
    remove_small_objects, remove_small_holes,
    reconstruction, medial_axis, thin
)

# Create structuring element
selem = disk(5)

# Binary morphological operations
cleaned = binary_opening(binary_image_gpu, footprint=selem)
cleaned = binary_closing(cleaned, footprint=selem)

# Remove small objects/holes
cleaned = remove_small_objects(labels_gpu, min_size=100)
filled = remove_small_holes(binary_gpu, area_threshold=50)

# Grayscale morphology
tophat = white_tophat(gray_image_gpu, footprint=disk(10))
```

**Structuring elements:** `disk`, `diamond`, `ball`, `octagon`, `octahedron`, `star`, `ellipse`, `footprint_rectangle`

**Isotropic operations:** `isotropic_erosion`, `isotropic_dilation`, `isotropic_opening`, `isotropic_closing`

**Extrema (added in 26.06):** `h_maxima`, `h_minima`, `local_maxima`, `local_minima`

---

## Segmentation

`cucim.skimage.segmentation` — level-set methods, boundary detection, label operations.

```python
from cucim.skimage.segmentation import (
    chan_vese, morphological_chan_vese, morphological_geodesic_active_contour,
    find_boundaries, mark_boundaries, clear_border,
    expand_labels, relabel_sequential, random_walker
)

# Chan-Vese segmentation
segmented = chan_vese(gray_image_gpu, mu=0.25, max_num_iter=200)

# Active contours (geodesic)
gimage = inverse_gaussian_gradient(gray_image_gpu)
init_ls = checkerboard_level_set(gray_image_gpu.shape)
seg = morphological_geodesic_active_contour(gimage, num_iter=200, init_level_set=init_ls)

# Find and mark boundaries
boundaries = find_boundaries(labels_gpu, mode='thick')
```

---

## Registration

`cucim.skimage.registration` — image alignment.

```python
from cucim.skimage.registration import (
    phase_cross_correlation,
    optical_flow_tvl1,
    optical_flow_ilk
)

# Subpixel image registration
shift, error, diffphase = phase_cross_correlation(reference_gpu, moving_gpu)

# Optical flow
flow = optical_flow_tvl1(frame1_gpu, frame2_gpu)
```

---

## Restoration

`cucim.skimage.restoration` — denoising and deconvolution.

```python
from cucim.skimage.restoration import (
    denoise_tv_chambolle,
    richardson_lucy,
    wiener, unsupervised_wiener,
    rolling_ball
)

# Total variation denoising
denoised = denoise_tv_chambolle(noisy_image_gpu, weight=0.1)

# Richardson-Lucy deconvolution
restored = richardson_lucy(blurred_image_gpu, psf_gpu, num_iter=30)

# Rolling-ball background subtraction (added in 26.04)
background = rolling_ball(image_gpu, radius=100)
```

---

## Transform

`cucim.skimage.transform` — geometric transforms, resizing, pyramids.

```python
from cucim.skimage.transform import (
    resize, rescale, rotate, warp, swirl, warp_polar,
    pyramid_gaussian, pyramid_laplacian,
    downscale_local_mean, integral_image,
    AffineTransform, EuclideanTransform, SimilarityTransform
)

# Resize
resized = resize(image_gpu, (256, 256))

# Rescale
half = rescale(image_gpu, 0.5)

# Rotate
rotated = rotate(image_gpu, angle=45, resize=True)

# Gaussian pyramid
pyramid = list(pyramid_gaussian(image_gpu, max_layer=4, downscale=2))

# Affine transform
tform = AffineTransform(rotation=0.3, translation=(50, 50))
warped = warp(image_gpu, tform.inverse)
```

---

## Metrics

`cucim.skimage.metrics` — image quality assessment.

```python
from cucim.skimage.metrics import (
    mean_squared_error,
    peak_signal_noise_ratio,
    structural_similarity,
    normalized_root_mse
)

mse = mean_squared_error(original_gpu, processed_gpu)
psnr = peak_signal_noise_ratio(original_gpu, processed_gpu)
ssim = structural_similarity(original_gpu, processed_gpu)
```

---

## Utility Functions

`cucim.skimage.util` — type conversion, array manipulation.

```python
from cucim.skimage.util import (
    img_as_float, img_as_float32, img_as_ubyte,
    invert, crop, random_noise, montage
)

# Convert to float32 [0, 1]
float_img = img_as_float32(uint8_image_gpu)

# Add noise for testing
noisy = random_noise(image_gpu, mode='gaussian', var=0.01)
```

---

## cucim.core.operations

NVIDIA-specific operations not found in scikit-image. Especially useful for digital pathology.

### Pathology-Specific

```python
from cucim.core.operations.color import (
    color_jitter,
    image_to_absorbance,
    stain_extraction_pca,
    normalize_colors_pca
)

# H&E stain normalization (digital pathology)
normalized = normalize_colors_pca(he_image_gpu)

# Color augmentation
augmented = color_jitter(image_gpu, brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1)
```

### Intensity Operations

```python
from cucim.core.operations.intensity import normalize_data, scale_intensity_range, zoom

normalized = normalize_data(image_gpu)
scaled = scale_intensity_range(image_gpu, a_min=0, a_max=255, b_min=0.0, b_max=1.0)
```

### Spatial Augmentation

```python
from cucim.core.operations.spatial import image_flip, image_rotate_90, rand_image_flip

flipped = image_flip(image_gpu, spatial_axis=1)
rotated = image_rotate_90(image_gpu, k=1)  # 90 degrees
randomly_flipped = rand_image_flip(image_gpu, prob=0.5)
```

### Distance Transform

```python
from cucim.core.operations.morphology import distance_transform_edt

# Exact Euclidean distance transform (faster than scipy.ndimage on GPU)
distances = distance_transform_edt(binary_image_gpu)
```

---

## Whole-Slide Image Reading

`cucim.CuImage` is the public whole-slide image reader:

```python
from cucim import CuImage

# Open a whole-slide image
img = CuImage("slide.svs")

# Inspect metadata
print(f"Dimensions: {img.shape}")
print(f"Resolution levels: {img.resolutions}")
print(f"Spacing: {img.spacing}")

# Read a region (returns a CuImage object)
region = img.read_region(location=(1000, 2000), size=(256, 256), level=0)

# Convert to CuPy array for processing
import cupy as cp
tile_gpu = cp.asarray(region)

# Process with cucim.skimage
from cucim.skimage.color import rgb2gray
gray_tile = rgb2gray(tile_gpu)
```

**Supported formats:** Aperio SVS, Philips TIFF, generic tiled multi-resolution RGB TIFF (JPEG, JPEG2000, LZW, Deflate compression).

### Tile Caching

```python
from cucim.clara.cache import ImageCache

# Configure tile cache for repeated access patterns
cache = ImageCache(memory_capacity=2 * 1024**3)  # 2 GB cache
```

### GPUDirect Storage

GPUDirect Storage can reduce CPU staging on a supported Linux, driver, filesystem, storage, and
container configuration. Treat it as a deployment capability, not an automatic size-based
optimization. Confirm that GDS is active and compare end-to-end tile throughput; otherwise use
cuCIM's normal reader path. Use KvikIO for explicit raw-buffer I/O rather than depending on
cuCIM-internal filesystem classes.

---

## Performance Characteristics

Benchmark each operation and the complete pipeline. Image dimensions alone do not predict a
speedup: kernel type, footprint size, channels, dtype, storage, tiling, transfer, and downstream
reuse all matter.

1. Warm the CUDA context and lazy kernels before timed repetitions.
2. Compare equivalent border modes, interpolation, connectivity, dtype, and output semantics.
3. Report decode/read, host-device transfer, processing, and end-to-end times separately.
4. For WSI workloads, record tile size, level, compression, access pattern, worker count, cache
   state, storage device, and whether GDS was active.
5. Transfer an image to the GPU once, chain compatible operations, and transfer only the result
   required by the next CPU consumer.

---

## Interoperability

- **CuPy:** Native array format. All cucim.skimage functions accept and return CuPy arrays.
- **NumPy:** Convert with `cp.asarray()` / `cp.asnumpy()`.
- **PyTorch/TensorFlow:** Zero-copy via DLPack protocol: `torch.as_tensor(cupy_array)` or `torch.from_dlpack(cupy_array)`.
- **MONAI:** Medical imaging framework with direct cuCIM integration for pathology transforms.
- **Albumentations:** Can use cuCIM as GPU backend for augmentations.
- **NVIDIA DALI:** Data loading pipeline integration.
- **Numba CUDA:** CuPy arrays interoperable with Numba GPU kernels.
- **cuDF:** Use for tabular operations on `regionprops_table` output.

### CPU/GPU Agnostic Code

```python
# Switch between CPU and GPU by changing the array module
import cupy as cp  # or: import numpy as cp
from cucim.skimage.filters import gaussian  # or: from skimage.filters import gaussian

result = gaussian(cp.asarray(image), sigma=5)
```

---

## Known Limitations vs scikit-image

1. **Incomplete API coverage:** ~50-66% of scikit-image functions are implemented. Notable gaps include some graph-based segmentation (watershed, SLIC superpixels), some feature descriptors (ORB, BRIEF, HOG), and some restoration methods.

2. **Linux only.** No Windows or macOS GPU support.

3. **NVIDIA GPU required.** No AMD/Intel GPU support.

4. **Data must be explicitly moved to GPU.** cuCIM does not auto-transfer; you must call `cp.asarray()`.

5. **Small image penalty.** Small or one-shot operations may not amortize context, launch, and
transfer overhead. Benchmark the real tile size and batching strategy.

6. **GPU memory constraints.** Very large images must be tiled. GPU memory is typically smaller than system RAM.

7. **WSI format support is limited.** Supports TIFF/SVS/Philips TIFF only. DICOM, NIFTI, Zarr not yet in stable release.

8. **JIT compilation overhead** on first call per session (cached thereafter).

---

## Common Migration Patterns

### Pattern 1: Direct scikit-image Replacement

```python
# Before (CPU)
from skimage.filters import gaussian, sobel, threshold_otsu
from skimage.morphology import binary_opening, disk
from skimage.measure import label, regionprops_table
import numpy as np

image = np.array(...)  # Load image
blurred = gaussian(image, sigma=3)
edges = sobel(blurred)
binary = blurred > threshold_otsu(blurred)
cleaned = binary_opening(binary, footprint=disk(3))
labels = label(cleaned)
props = regionprops_table(labels, image, properties=['area', 'centroid'])

# After (GPU) — change imports, wrap input with cp.asarray
from cucim.skimage.filters import gaussian, sobel, threshold_otsu
from cucim.skimage.morphology import binary_opening, disk
from cucim.skimage.measure import label, regionprops_table
import cupy as cp

image_gpu = cp.asarray(image)  # Transfer once
blurred = gaussian(image_gpu, sigma=3)
edges = sobel(blurred)
binary = blurred > threshold_otsu(blurred)
cleaned = binary_opening(binary, footprint=disk(3))
labels = label(cleaned)
props = regionprops_table(labels, image_gpu, properties=['area', 'centroid'])
```

### Pattern 2: Digital Pathology Pipeline

```python
from cucim import CuImage
from cucim.skimage.color import rgb2gray, separate_stains
from cucim.skimage.filters import threshold_otsu
from cucim.skimage.morphology import binary_opening, remove_small_objects, disk
from cucim.skimage.measure import label, regionprops_table
from cucim.core.operations.color import normalize_colors_pca
import cupy as cp

# Read whole-slide image tile
slide = CuImage("tissue.svs")
tile = cp.asarray(slide.read_region(location=(1000, 2000), size=(512, 512), level=0))

# Normalize staining
normalized = normalize_colors_pca(tile)

# Segment nuclei
gray = rgb2gray(normalized)
binary = gray < threshold_otsu(gray)
cleaned = binary_opening(binary, footprint=disk(2))
cleaned = remove_small_objects(label(cleaned), min_size=50)
labels = label(cleaned)

# Extract properties
props = regionprops_table(labels, gray, properties=['area', 'centroid', 'mean_intensity'])
```

### Pattern 3: Deep Learning Preprocessing Pipeline

```python
import cupy as cp
from cucim.skimage.transform import resize
from cucim.skimage.exposure import equalize_adapthist
from cucim.skimage.util import img_as_float32
from cucim.core.operations.spatial import rand_image_flip
from cucim.core.operations.color import color_jitter
import torch

# Load batch of images to GPU
images_gpu = cp.asarray(numpy_batch)  # (N, H, W, C)

# Process each image on GPU
processed = []
for img in images_gpu:
    img = img_as_float32(img)
    img = resize(img, (224, 224))
    img = equalize_adapthist(img)
    img = rand_image_flip(img, prob=0.5)
    img = color_jitter(img, brightness=0.2, contrast=0.2)
    processed.append(img)

batch_gpu = cp.stack(processed)

# Zero-copy to PyTorch for model inference
batch_torch = torch.as_tensor(batch_gpu).permute(0, 3, 1, 2)  # NHWC → NCHW
```

### `references/cudf.md`

# cuDF Reference

cuDF is a GPU DataFrame library that provides a pandas-like API for loading, joining, aggregating, filtering, and manipulating tabular data entirely on the GPU. It's part of the NVIDIA RAPIDS ecosystem and is built on the Apache Arrow columnar memory format.

> **Full documentation:** https://docs.rapids.ai/api/cudf/stable/

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Two Usage Modes](#two-usage-modes)
3. [cudf.pandas Accelerator Mode](#cudfpandas-accelerator-mode)
4. [Core API: DataFrame and Series](#core-api)
5. [IO Operations](#io-operations)
6. [GroupBy Operations](#groupby-operations)
7. [String Operations](#string-operations)
8. [User Defined Functions (UDFs)](#user-defined-functions)
9. [Missing Data Handling](#missing-data-handling)
10. [Data Types](#data-types)
11. [Memory Management](#memory-management)
12. [Interoperability](#interoperability)
13. [Multi-GPU with Dask-cuDF](#multi-gpu-with-dask-cudf)
14. [Performance Optimization](#performance-optimization)
15. [Key Differences from pandas](#key-differences-from-pandas)
16. [Common Migration Patterns](#common-migration-patterns)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add "cudf-cu12==26.6.*"    # For CUDA 12.x
uv add "cudf-cu13==26.6.*"    # For CUDA 13.x
```

cuDF wheels are now published directly to PyPI — the `--extra-index-url=https://pypi.nvidia.com` extra index is no longer required. Requires Python >= 3.11.

Verify:
```python
import cudf
print(cudf.Series([1, 2, 3]))  # Should print a GPU series
```

---

## Two Usage Modes

cuDF offers two ways to accelerate pandas code:

### 1. cudf.pandas (Zero-Code-Change)
Drop-in replacement that automatically accelerates pandas. Falls back to CPU for unsupported operations. Best for: quick acceleration of existing code, mixed codebases, prototyping.

### 2. Direct cuDF API
Replace `import pandas` with `import cudf`. Maximum performance, no proxy overhead, but requires adapting code to cuDF's API (which has some behavioral differences from pandas). Best for: production pipelines, maximum performance, new GPU-first code.

---

## cudf.pandas Accelerator Mode

The fastest path from pandas to GPU — no code changes required.

### Activation

```python
# Jupyter/IPython (MUST be before any pandas import)
%load_ext cudf.pandas
import pandas as pd  # Now GPU-accelerated

# Command line
# python -m cudf.pandas your_script.py
# python -m cudf.pandas --profile your_script.py  # With profiling

# Programmatic
import cudf.pandas
cudf.pandas.install()
import pandas as pd  # Now GPU-accelerated
```

**Critical:** If pandas was already imported in the session, you must restart the kernel/process.

### How It Works

- `import pandas` returns a proxy module that wraps cuDF and pandas.
- Every operation is first attempted on GPU (cuDF). If it fails, it automatically falls back to CPU (pandas).
- Data transfers between GPU and CPU happen only when necessary.
- Uses managed memory by default — can process datasets larger than GPU memory.
- Currently passes **93% of pandas' 187,000+ unit tests**.

### Profiling GPU vs CPU Execution

```python
%%cudf.pandas.profile        # Shows GPU vs CPU operation breakdown per cell
%%cudf.pandas.line_profile   # Per-line GPU/CPU timing
```

### Accessing Underlying Objects

```python
proxy_df.as_gpu_object()  # Get the cuDF DataFrame directly
proxy_df.as_cpu_object()  # Get the pandas DataFrame directly
```

Note: automatic fallback stops working after you extract the underlying object.

### Compatible Third-Party Libraries
cuGraph, cuML, Hvplot, Holoview, Ibis, NumPy, Matplotlib, Plotly, PyTorch, Seaborn, Scikit-Learn, SciPy, TensorFlow, XGBoost.

**Not compatible:** Joblib. For distributed work, use Dask-cuDF instead.

### Limitations

- Join operations don't guarantee pandas' row ordering (for performance).
- Cannot use `import cudf` alongside cudf.pandas in the same session.
- Pickled objects are not interchangeable between regular pandas and cudf.pandas.
- Proxy arrays subclass `numpy.ndarray`, which can cause eager device-to-host transfers.
- To force CPU-only: set `CUDF_PANDAS_FALLBACK_MODE=1`.

---

## Core API

### Creating DataFrames and Series

```python
import cudf

# From dict
df = cudf.DataFrame({"a": [1, 2, 3], "b": [4.0, 5.0, 6.0], "c": ["x", "y", "z"]})

# From pandas
import pandas as pd
gdf = cudf.DataFrame.from_pandas(pd.DataFrame({"a": [1, 2, 3]}))
# or
gdf = cudf.DataFrame(pandas_df)

# Series
s = cudf.Series([1, 2, 3, None, 5])

# Back to pandas
pdf = gdf.to_pandas()
```

### Common Operations (Same as pandas)

```python
df.head(10)
df.tail(5)
df.describe()
df.info()
df.dtypes
df.columns
df.shape

# Selection
df["a"]                     # Column → Series
df[["a", "b"]]             # Multiple columns → DataFrame
df.loc[2:5, ["a", "b"]]   # Label-based indexing
df.iloc[0:3]               # Integer-based indexing

# Filtering
df[df["a"] > 2]
df.query("a > 2 and b < 6")  # Supports @var for local variables

# Sorting
df.sort_values("a", ascending=False)
df.sort_index()

# Missing data
df.fillna(0)
df.dropna()
df.isna()

# Aggregations
df["a"].sum()
df["a"].mean()
df["a"].std()
df["a"].value_counts()

# Transforms
df["a"].clip(lower=1, upper=5)
df["a"].apply(lambda x: x * 2)  # JIT-compiled

# Combining
cudf.concat([df1, df2])
df1.merge(df2, on="key")
df1.merge(df2, on="key", how="left")  # left, right, inner, outer

# Arrow interop (zero-copy)
arrow_table = df.to_arrow()
df = cudf.DataFrame.from_arrow(arrow_table)
```

---

## IO Operations

GPU-accelerated file reading and writing — often dramatically faster than pandas for large files.

### Parquet (Recommended for Performance)

```python
# Read
df = cudf.read_parquet("data.parquet")
df = cudf.read_parquet("data.parquet", columns=["a", "b"])  # Read only specific columns

# Write
df.to_parquet("output.parquet")

# Metadata inspection (without loading data)
cudf.io.parquet.read_parquet_metadata("data.parquet")

# Incremental writing
writer = cudf.io.parquet.ParquetDatasetWriter("output_dir/", partition_cols=["year"])
writer.write_table(df)
writer.close()
```

### CSV

```python
df = cudf.read_csv("data.csv")
df = cudf.read_csv("data.csv", usecols=["a", "b"], dtype={"a": "int32"})
df.to_csv("output.csv", index=False)
```

### JSON

```python
df = cudf.read_json("data.json")
df = cudf.read_json("data.json", lines=True)  # JSON Lines format
df.to_json("output.json")
```

### ORC

```python
df = cudf.read_orc("data.orc")
df.to_orc("output.orc")
```

### Other Formats

| Format | Read | Write | GPU-Accelerated |
|--------|------|-------|-----------------|
| Avro | `cudf.read_avro()` | N/A | Yes (read only) |
| Text | `cudf.read_text()` | N/A | Yes (read only) |
| HDF5 | `cudf.read_hdf()` | `df.to_hdf()` | No (uses pandas) |
| Feather | `cudf.read_feather()` | `df.to_feather()` | No (uses pandas) |

**Prefer Parquet over CSV** — columnar format reads faster on GPU, supports predicate pushdown, and compresses well.

---

## GroupBy Operations

### Basic GroupBy

```python
df.groupby("category").sum()
df.groupby(["category", "subcategory"]).mean()
df.groupby("category").agg({"value": "sum", "count": "max"})
df.groupby("category").agg({"value": ["sum", "min", "max"], "count": "mean"})
```

### Supported Aggregations

**Universal:** `count`, `size`, `nunique`, `nth`, `collect`, `unique`
**Numeric:** `sum`, `mean`, `var`, `std`, `median`, `idxmin`, `idxmax`, `min`, `max`, `quantile`
**Specialized:** `corr`, `cov`

### GroupBy Transform

```python
df.groupby("category").transform("max")  # Broadcasts result to match group size
```

### GroupBy Apply

```python
df.groupby("category").apply(lambda x: x.max() - x.min())
```

**Warning:** Apply runs the function sequentially per group — can be slow with many small groups. Use vectorized aggregations whenever possible.

### JIT-Compiled GroupBy (User-Defined Aggregation)

```python
def custom_agg(df):
    return df["value"].max() - df["value"].min() / 2

result = df.groupby("category").apply(custom_agg, engine="jit")
```

JIT restrictions: no nulls, only int32/64 and float32/64, cannot return new columns.

### Important: Sort Behavior

cuDF uses `sort=False` by default (unlike pandas which sorts by default). To match pandas:
```python
df.groupby("category", sort=True).sum()
# Or globally:
cudf.set_option("mode.pandas_compatible", True)
```

---

## String Operations

cuDF provides GPU-accelerated string operations via the `.str` accessor — identical API to pandas.

```python
s = cudf.Series(["Hello World", "foo bar", "RAPIDS GPU", None])

# Case
s.str.lower()
s.str.upper()
s.str.title()
s.str.capitalize()

# Pattern matching
s.str.contains("World")
s.str.startswith("Hello")
s.str.endswith("GPU")
s.str.match(r"^[A-Z]")

# Extraction and replacement
s.str.extract(r"(\w+)\s(\w+)")
s.str.replace("World", "GPU")
s.str.slice(0, 5)

# Splitting and joining
s.str.split(" ")
s.str.cat(sep=", ")

# Info
s.str.len()
s.str.isalpha()
s.str.isdigit()

# cuDF-exclusive operations (not in pandas)
s.str.normalize_spaces()   # Collapse whitespace
s.str.tokenize()           # Tokenize strings
s.str.ngrams(2)            # Generate n-grams
s.str.edit_distance(other) # Levenshtein distance
s.str.url_encode()
s.str.url_decode()
```

---

## User Defined Functions

### Series.apply() — JIT-Compiled

```python
s = cudf.Series([1, 2, 3, 4, 5])

def square_plus_one(x):
    return x ** 2 + 1

s.apply(square_plus_one)  # Compiled to GPU kernel via Numba
```

With arguments:
```python
def add_constant(x, c):
    return x + c

s.apply(add_constant, args=(42,))
```

### DataFrame.apply() — Row-wise (axis=1)

```python
def row_func(row):
    return row["a"] + row["b"] * 2

df.apply(row_func, axis=1)  # Access columns by name via dict-like syntax
```

### Null Handling in UDFs

Nulls propagate automatically:
```python
s = cudf.Series([1, cudf.NA, 3])
def f(x):
    return x + 1
s.apply(f)  # Returns [2, <NA>, 4]
```

Explicit null checks:
```python
def f(x):
    if x is cudf.NA:
        return 0
    return x + 1
```

### String UDFs

String operations inside UDFs support: `==`, `!=`, `>=`, `<=`, `startswith()`, `endswith()`, `find()`, `rfind()`, `count()`, `in`, `strip/lstrip/rstrip()`, `upper/lower()`, `replace()`, `+` (concatenation), `len()`, boolean checks.

For string UDFs creating intermediate strings, allocate heap:
```python
from cudf.core.udf.utils import set_malloc_heap_size
set_malloc_heap_size(int(2e9))  # 2 GB
```

### Rolling Window UDFs

```python
import math

s = cudf.Series([16, 25, 36, 49, 64, 81], dtype="float64")

def max_sqrt(window):
    result = 0
    for val in window:
        result = max(result, math.sqrt(val))
    return result

s.rolling(window=3, min_periods=3).apply(max_sqrt)
```

**Limitation:** Rolling UDFs do NOT support null values.

### Custom Numba CUDA Kernels on cuDF Columns

For maximum control, write CUDA kernels that operate directly on cuDF columns:

```python
from numba import cuda

@cuda.jit
def gpu_multiply(in_col, out_col, multiplier):
    i = cuda.grid(1)
    if i < in_col.size:
        out_col[i] = in_col[i] * multiplier

df["result"] = 0.0
gpu_multiply.forall(len(df))(df["a"], df["result"], 10.0)
```

### UDF Limitations

- Only numeric non-decimal types have full support; strings have partial support.
- `**kwargs` not supported.
- Bitwise operations not implemented in UDFs.
- GroupBy JIT: no nulls, only int32/64 and float32/64, cannot return new columns.
- Rolling UDFs: no null support.

---

## Missing Data Handling

- Missing values are `<NA>` (not NaN) — cuDF uses a separate null mask, not NaN sentinels.
- All dtypes are nullable (including integers — no float coercion for missing ints).
- `np.nan` inserted into integer columns becomes `<NA>` without casting to float.

```python
s = cudf.Series([1, None, 3, None, 5])

s.isna()                # Boolean mask
s.notna()
s.fillna(0)             # Fill with scalar
s.fillna({"a": 0, "b": 1})  # Fill with dict (per-column)
s.dropna()

# Aggregations skip NA by default
s.sum()                 # skipna=True (default)
s.sum(skipna=False)     # Propagates NA

# GroupBy excludes NA groups by default
df.groupby("a", dropna=False).sum()  # Include NA groups
```

---

## Data Types

| Category | Types |
|----------|-------|
| Integer | `int8`, `int16`, `int32`, `int64`, `uint32`, `uint64` |
| Float | `float32`, `float64` |
| Datetime | `datetime64[s/ms/us/ns]` |
| Timedelta | `timedelta[s/ms/us/ns]` |
| Categorical | `CategoricalDtype` |
| String | `object` / `string` |
| Decimal | `Decimal32Dtype`, `Decimal64Dtype`, `Decimal128Dtype` |
| List | `ListDtype` (nested lists) |
| Struct | `StructDtype` (dict-like) |

All types are nullable. List columns have a `.list` accessor (`get()`, `len()`, `contains()`, `sort_values()`, `unique()`, `concat()`). Struct columns have a `.struct` accessor (`field()`, `explode()`).

**No `object` dtype for arbitrary Python objects** — `object` dtype only stores strings.

---

## Memory Management

### RMM (RAPIDS Memory Manager)

cuDF uses RMM for GPU memory allocation. Configure it for your workload:

```python
import rmm

# Pool allocator (recommended for production — avoids per-allocation cudaMalloc overhead)
pool = rmm.mr.PoolMemoryResource(
    rmm.mr.CudaMemoryResource(),
    initial_pool_size="1GiB",
    maximum_pool_size="4GiB"
)
rmm.mr.set_current_device_resource(pool)

# Managed memory (allows datasets larger than GPU memory)
rmm.mr.set_current_device_resource(rmm.mr.ManagedMemoryResource())

# Managed + pool (best of both)
pool = rmm.mr.PoolMemoryResource(
    rmm.mr.ManagedMemoryResource(),
    initial_pool_size="1GiB"
)
rmm.mr.set_current_device_resource(pool)
```

### Aligning CuPy and Numba with RMM

When using cuDF with CuPy or Numba, align all libraries on the same allocator to avoid memory fragmentation:

```python
# CuPy
from rmm.allocators.cupy import rmm_cupy_allocator
import cupy
cupy.cuda.set_allocator(rmm_cupy_allocator)

# Numba
from rmm.allocators.numba import RMMNumbaManager
from numba import cuda
cuda.set_memory_manager(RMMNumbaManager)
```

### Copy-on-Write

```python
cudf.set_option("copy_on_write", True)
# or: export CUDF_COPY_ON_WRITE=1
```

Slices, `.head()`, shallow copies, and view-generating methods share memory until one is modified. Reduces memory usage significantly for workflows with many derived DataFrames.

### Memory Profiling

```python
rmm.statistics.enable_statistics()
stats = rmm.statistics.get_statistics()
# Returns: current_bytes, current_count, peak_bytes, peak_count, total_bytes, total_count
```

---

## Interoperability

### CuPy (Zero-Copy)

```python
import cupy as cp

# cuDF → CuPy
arr = df.to_cupy()             # DataFrame → 2D CuPy array
arr = cp.asarray(df["col"])    # Series → 1D CuPy array
arr = df["col"].values         # Series → 1D CuPy array

# CuPy → cuDF
df = cudf.DataFrame(cupy_2d_array)
s = cudf.Series(cupy_1d_array)

# Via DLPack
df = cudf.from_dlpack(cupy_array.__dlpack__())
```

### Arrow (Zero-Copy)

```python
arrow_table = df.to_arrow()
df = cudf.DataFrame.from_arrow(arrow_table)
```

### RAPIDS Ecosystem

- **cuML:** Accepts cuDF DataFrames directly for ML pipelines.
- **cuGraph:** Accepts cuDF DataFrames for graph analytics.
- **Dask-cuDF:** Distributed GPU DataFrames (see below).

### CUDA Array Interface

cuDF Series exposes `__cuda_array_interface__` for zero-copy sharing with any compatible library (CuPy, Numba, PyTorch, etc.).

---

## Multi-GPU with Dask-cuDF

For datasets larger than a single GPU's memory, or for multi-GPU parallelism:

```python
import dask_cudf
from dask.distributed import Client
from dask_cuda import LocalCUDACluster

# One worker per GPU
cluster = LocalCUDACluster()
client = Client(cluster)

# From files
ddf = dask_cudf.read_csv("path/*.csv")
ddf = dask_cudf.read_parquet("path/")

# From cuDF DataFrame
ddf = dask_cudf.from_cudf(df, npartitions=16)

# Operations (lazy — call .compute() to execute)
result = ddf.groupby("a").sum().compute()

# Persist in GPU memory for repeated access
ddf = ddf.persist()
```

Key differences from cuDF: `.iloc` not supported, must call `.compute()` to materialize, transpose not implemented.

---

## Performance Optimization

1. **Start with cudf.pandas** for easiest adoption — zero code changes, automatic GPU/CPU fallback.

2. **Switch to direct cuDF API for max performance** — avoids proxy overhead and fallback copying costs.

3. **Prefer Parquet over CSV** — columnar format, faster GPU reads, predicate pushdown, better compression.

4. **Use pool allocators** via RMM — avoids per-allocation `cudaMalloc` overhead.

5. **Enable copy-on-write** — `cudf.set_option("copy_on_write", True)` reduces memory from slices and views.

6. **Reshape data to be long** (more rows, fewer columns) — GPUs parallelize over rows.

7. **Never iterate** — use vectorized operations exclusively. `for row in df.iterrows()` defeats the purpose of GPU acceleration.

8. **Minimum dataset size:** GPUs shine with **10,000-100,000+ rows**. Smaller datasets may be faster on CPU.

9. **Use vectorized string ops** (`.str.` accessor) instead of row-wise string UDFs.

10. **Use CuPy for row-wise math** that cuDF doesn't support natively.

11. **Use Numba CUDA kernels** for complex element-wise operations.

12. **Align all RAPIDS libraries on the same RMM allocator** to avoid memory fragmentation.

13. **For distributed workloads**, use Dask-cuDF with `persist()` to keep data on GPU memory.

---

## Key Differences from pandas

1. **Result ordering is non-deterministic** by default (groupby, joins, etc.). Use `sort=True` or `cudf.set_option("mode.pandas_compatible", True)`.

2. **All types are nullable.** Missing values are `<NA>`, not NaN. Integer columns with missing values stay integer (no float coercion).

3. **No iteration.** `for val in series` is not supported. Convert to pandas first if you must iterate.

4. **Unique column names required.** No duplicate column names.

5. **No arbitrary Python objects.** The `object` dtype only stores strings.

6. **`.apply()` uses Numba JIT.** Only a subset of Python is supported inside UDFs — no arbitrary Python objects, no external library calls.

7. **Floating-point results may differ slightly** due to GPU parallel operation ordering. Use tolerance-based comparisons.

8. **GroupBy defaults to `sort=False`** (pandas defaults to `sort=True`).

9. **No ExtensionDtype support** from pandas.

---

## Common Migration Patterns

### Pattern 1: Zero-Effort (cudf.pandas)
```python
%load_ext cudf.pandas
import pandas as pd
# Everything else stays exactly the same
```

### Pattern 2: Direct Import Swap
```python
# Before
import pandas as pd
df = pd.read_csv("data.csv")
result = df.groupby("col").mean()

# After
import cudf
df = cudf.read_csv("data.csv")
result = df.groupby("col").mean()
```

### Pattern 3: Replace Iteration with Vectorized Ops
```python
# Before (pandas — slow even on CPU)
for idx, row in df.iterrows():
    df.at[idx, "c"] = row["a"] + row["b"]

# After (cuDF)
df["c"] = df["a"] + df["b"]
```

### Pattern 4: Replace apply() with Vectorized
```python
# Before
df["result"] = df.apply(lambda row: row["a"] ** 2 + row["b"], axis=1)

# After (vectorized — much faster)
df["result"] = df["a"] ** 2 + df["b"]
```

### Pattern 5: GPU Processing, CPU at Boundaries
```python
# Load and process on GPU
gdf = cudf.read_parquet("data.parquet")
result = gdf.groupby("key").agg({"val": "sum"})

# Convert to pandas only when needed (plotting, export, etc.)
pdf = result.to_pandas()
pdf.plot()
```

### Pattern 6: CuPy for Unsupported Math
```python
import cupy as cp

# Convert to CuPy for operations cuDF doesn't support
arr = df[["x", "y", "z"]].to_cupy()
norms = cp.linalg.norm(arr, axis=1)
df["norm"] = cudf.Series(norms)
```

---

## Configuration

```python
cudf.set_option("copy_on_write", True)            # Enable copy-on-write
cudf.set_option("mode.pandas_compatible", True)    # Match pandas behavior
cudf.describe_option()                             # List all options
```

| Environment Variable | Purpose |
|---------------------|---------|
| `CUDF_COPY_ON_WRITE=1` | Enable copy-on-write |
| `CUDF_PANDAS_RMM_MODE` | Control memory allocator for cudf.pandas |
| `CUDF_PANDAS_FALLBACK_MODE=1` | Force CPU-only execution in cudf.pandas |

### `references/cugraph.md`

# cuGraph Reference

cuGraph is NVIDIA's GPU-accelerated graph analytics library within the RAPIDS ecosystem. It
supports both a direct Python API and an **nx-cugraph** NetworkX backend. Performance depends on
algorithm, graph topology and size, graph-construction cost, fallback behavior, and GPU hardware,
so benchmark the complete workload instead of promising a fixed speedup.

> **Full documentation:** https://docs.rapids.ai/api/cugraph/stable/
> **Version (stable):** 26.06.00
> **Repository:** https://github.com/rapidsai/cugraph

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Two Usage Modes](#two-usage-modes)
3. [nx-cugraph: Zero-Code-Change NetworkX Backend](#nx-cugraph-zero-code-change-networkx-backend)
4. [Direct cuGraph API](#direct-cugraph-api)
5. [Graph Creation and Data Loading](#graph-creation-and-data-loading)
6. [Supported Graph Types](#supported-graph-types)
7. [Algorithm Catalog](#algorithm-catalog)
8. [Multi-GPU Support with Dask](#multi-gpu-support-with-dask)
9. [GNN Support (cugraph-pyg and WholeGraph)](#gnn-support)
10. [Performance Characteristics and Benchmarks](#performance-characteristics-and-benchmarks)
11. [Memory Management](#memory-management)
12. [Interoperability](#interoperability)
13. [Known Limitations vs NetworkX](#known-limitations-vs-networkx)
14. [Common Migration Patterns](#common-migration-patterns)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add --extra-index-url=https://pypi.nvidia.com "cugraph-cu12==26.6.*"    # Core cuGraph for CUDA 12.x
uv add --extra-index-url=https://pypi.nvidia.com "nx-cugraph-cu12==26.6.*" # NetworkX backend
# For CUDA 13.x, use the -cu13 packages: cugraph-cu13, nx-cugraph-cu13
```

Unlike cuDF/cuML (whose wheels are now on PyPI directly), the cugraph and nx-cugraph packages on PyPI are stub sdists — keep the `pypi.nvidia.com` extra index for these.

**Platform:** Linux and WSL2 only (no native macOS or Windows).
**Requires:** Python >= 3.11, NVIDIA GPU with CUDA 12.x or 13.x support, NetworkX >= 3.2 (>= 3.5 recommended for optimal nx-cugraph).

Verify:
```python
import cugraph
print(cugraph.__version__)

# Quick test with built-in dataset
from cugraph.datasets import karate
G = karate.get_graph()
result = cugraph.degree_centrality(G)
print(result.head())
```

---

## Two Usage Modes

### Mode 1: nx-cugraph Backend (Zero Code Change)
Accelerate existing NetworkX code by setting one environment variable. No code changes required.

```bash
NX_CUGRAPH_AUTOCONFIG=True python my_networkx_script.py
```

### Mode 2: Direct cuGraph API
Use cuGraph's native API for maximum control, working directly with cuDF DataFrames and cuGraph graph objects.

```python
import cugraph
import cudf

edges = cudf.DataFrame({
    "src": [0, 1, 2, 0],
    "dst": [1, 2, 3, 3],
    "weight": [1.0, 2.0, 1.5, 3.0]
})
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="src", destination="dst", edge_attr="weight")
result = cugraph.pagerank(G)
```

**When to use which:**
- **nx-cugraph**: Existing NetworkX codebases, rapid prototyping, when you want zero migration effort
- **Direct API**: Maximum performance, multi-GPU workflows, integration with cuDF/cuML pipelines, GNN training

---

## nx-cugraph: Zero-Code-Change NetworkX Backend

nx-cugraph is a NetworkX backend that transparently redirects supported algorithm calls to GPU-accelerated cuGraph implementations.

### How It Works

NetworkX >= 3.2 has a backend dispatch system. When nx-cugraph is installed and enabled, NetworkX automatically redirects supported function calls to GPU implementations. Unsupported calls fall back to default NetworkX.

### Three Ways to Enable

**1. Environment Variable (recommended for zero code change):**
```bash
export NX_CUGRAPH_AUTOCONFIG=True
python my_script.py
# OR inline:
NX_CUGRAPH_AUTOCONFIG=True python my_script.py
```

**2. Keyword Argument (explicit per-call):**
```python
import networkx as nx
result = nx.betweenness_centrality(G, k=10, backend="cugraph")
```

**3. Type-Based Dispatch (explicit graph conversion):**
```python
import networkx as nx
import nx_cugraph as nxcg

G_nx = nx.karate_club_graph()
G_gpu = nxcg.from_networkx(G_nx)  # Convert once, reuse for multiple algorithms
result = nx.pagerank(G_gpu)       # Automatically dispatched to GPU
```

Since 26.04, GPU-backed graphs can also be constructed directly, e.g. `nx.Graph(backend="cugraph")`.

### Supported Algorithms in nx-cugraph

**Centrality:**
- `betweenness_centrality`, `edge_betweenness_centrality`
- `degree_centrality`, `in_degree_centrality`, `out_degree_centrality`
- `eigenvector_centrality`, `katz_centrality`

**Community:**
- `louvain_communities`, `leiden_communities`

**Components:**
- `connected_components`, `is_connected`, `number_connected_components`
- `node_connected_component`
- `weakly_connected_components`, `is_weakly_connected`, `number_weakly_connected_components`

**Clustering:**
- `average_clustering`, `clustering`, `transitivity`, `triangles`

**Core:**
- `core_number`, `k_truss`

**Link Analysis:**
- `pagerank`, `hits`

**Link Prediction:**
- `jaccard_coefficient`

**Shortest Paths (23+ functions):**
- `shortest_path`, `shortest_path_length`
- `has_path`, `all_pairs_shortest_path`, `all_pairs_shortest_path_length`
- `dijkstra_path`, `dijkstra_path_length`, `all_pairs_dijkstra`, `all_pairs_dijkstra_path_length`
- `bellman_ford_path`, `bellman_ford_path_length`, `all_pairs_bellman_ford_path_length`
- `single_source_shortest_path`, `single_source_shortest_path_length`
- `single_source_dijkstra`, `single_source_dijkstra_path`, `single_source_dijkstra_path_length`
- `single_source_bellman_ford`, `single_source_bellman_ford_path`, `single_source_bellman_ford_path_length`
- `single_target_shortest_path_length`

**Traversal:**
- `bfs_edges`, `bfs_layers`, `bfs_predecessors`, `bfs_successors`, `bfs_tree`
- `generic_bfs_edges`, `descendants_at_distance`

**DAG:**
- `ancestors`, `descendants`

**Bipartite:**
- `betweenness_centrality` (bipartite), `biadjacency_matrix`
- `complete_bipartite_graph`, `from_biadjacency_matrix`

**Tree:**
- `is_arborescence`, `is_branching`, `is_forest`, `is_tree`

**Operators:**
- `complement`, `reverse`

**Reciprocity:**
- `overall_reciprocity`, `reciprocity`

**Isolate:**
- `is_isolate`, `isolates`, `number_of_isolates`

**Lowest Common Ancestors:**
- `lowest_common_ancestor`

**Layout:**
- `forceatlas2_layout`

**Graph Generators:** Various generators are also supported for creating graphs directly on GPU.

---

## Direct cuGraph API

### Quick Example

```python
import cugraph
import cudf

# Load edges from cuDF DataFrame
edges = cudf.DataFrame({
    "source": [0, 1, 2, 3, 0, 2],
    "destination": [1, 2, 3, 4, 4, 1],
    "weight": [1.0, 2.0, 1.0, 3.0, 0.5, 1.5]
})

G = cugraph.Graph(directed=True)
G.from_cudf_edgelist(edges, source="source", destination="destination", edge_attr="weight")

# Run algorithms
pr = cugraph.pagerank(G)
bc = cugraph.betweenness_centrality(G)
components = cugraph.weakly_connected_components(G)
```

---

## Graph Creation and Data Loading

### From cuDF DataFrame (Primary Method)
```python
import cudf, cugraph

df = cudf.DataFrame({"src": [0, 1, 2], "dst": [1, 2, 3], "wt": [1.0, 2.0, 3.0]})

# Unweighted
G = cugraph.Graph()
G.from_cudf_edgelist(df, source="src", destination="dst")

# Weighted
G = cugraph.Graph()
G.from_cudf_edgelist(df, source="src", destination="dst", edge_attr="wt")

# Directed
G = cugraph.Graph(directed=True)
G.from_cudf_edgelist(df, source="src", destination="dst")
```

### From Pandas DataFrame
```python
import pandas as pd, cugraph

df = pd.DataFrame({"src": [0, 1, 2], "dst": [1, 2, 3]})
G = cugraph.Graph()
G.from_pandas_edgelist(df, source="src", destination="dst")
```

### From cuDF Adjacency List
```python
G = cugraph.Graph()
G.from_cudf_adjlist(offsets, indices, values)  # CSR format
```

### From NumPy Array
```python
import numpy as np
adj_matrix = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
G = cugraph.Graph()
G.from_numpy_array(adj_matrix)
```

### From Pandas Adjacency Matrix
```python
G = cugraph.Graph()
G.from_pandas_adjacency(adj_df)
```

### From Dask-cuDF (Multi-GPU)
```python
G = cugraph.Graph()
G.from_dask_cudf_edgelist(dask_cudf_df, source="src", destination="dst")
```

### From Built-in Datasets
```python
from cugraph.datasets import karate, dolphins, polbooks, netscience
G = karate.get_graph()
```

### Symmetrization (Undirected Graphs)
```python
# Ensure all edges are bidirectional
sym_df = cugraph.symmetrize_df(df, "src", "dst")

# Or symmetrize a graph directly
sym_df = cugraph.symmetrize(source_col, dest_col, weight_col)
```

### Vertex Renumbering
cuGraph internally renumbers vertices to contiguous integers starting from 0. Use `unrenumber()` to map back to original IDs:
```python
result = cugraph.pagerank(G)
result = G.unrenumber(result, "vertex")  # Map internal IDs back to original
```

---

## Supported Graph Types

| Graph Type | cuGraph Class | Notes |
|---|---|---|
| **Undirected** | `cugraph.Graph()` | Default; edges are bidirectional |
| **Directed** | `cugraph.Graph(directed=True)` | Directed edges; some algorithms require directed/undirected |
| **Weighted** | Set `edge_attr` in `from_cudf_edgelist` | Edge weights used by SSSP, PageRank, Louvain, etc. |
| **MultiGraph** | `cugraph.MultiGraph()` | Multiple edges between same vertex pairs |
| **Bipartite** | Supported via standard Graph with bipartite structure | No dedicated class; algorithms in `cugraph.bipartite` |

**Important:** cuGraph uses a CSR (Compressed Sparse Row) internal representation. Graphs are immutable after creation -- you cannot dynamically add/remove individual edges after calling `from_cudf_edgelist()`. To modify a graph, reconstruct it from a new DataFrame.

---

## Algorithm Catalog

### Centrality

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| Betweenness Centrality | `cugraph.betweenness_centrality(G)` | `cugraph.dask.centrality.betweenness_centrality()` | `nx.betweenness_centrality()` |
| Edge Betweenness | `cugraph.edge_betweenness_centrality(G)` | `cugraph.dask.centrality.edge_betweenness_centrality()` | `nx.edge_betweenness_centrality()` |
| Degree Centrality | `cugraph.degree_centrality(G)` | -- | `nx.degree_centrality()` |
| Eigenvector Centrality | `cugraph.eigenvector_centrality(G)` | `cugraph.dask.centrality.eigenvector_centrality()` | `nx.eigenvector_centrality()` |
| Katz Centrality | `cugraph.katz_centrality(G)` | `cugraph.dask.centrality.katz_centrality()` | `nx.katz_centrality()` |

### Community Detection

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| Louvain | `cugraph.louvain(G, max_level=, max_iter=, resolution=)` | `cugraph.dask.community.louvain.louvain()` | `nx.community.louvain_communities()` |
| Leiden | `cugraph.leiden(G, max_iter=, resolution=)` | `cugraph.dask.community.leiden.leiden()` | `nx.community.leiden_communities()` |
| ECG | `cugraph.ecg(G, min_weight=)` | `cugraph.dask.community.ecg.ecg()` | -- |
| Spectral Balanced Cut | `cugraph.spectralBalancedCutClustering(G, num_clusters)` | -- | -- |
| Spectral Modularity | `cugraph.spectralModularityMaximizationClustering(G, num_clusters)` | -- | -- |
| Triangle Counting | `cugraph.triangle_count(G)` | `cugraph.dask.community.triangle_count()` | `nx.triangles()` |
| K-Truss | `cugraph.k_truss(G, k)` or `cugraph.ktruss_subgraph(G, k)` | `cugraph.dask.community.ktruss_subgraph()` | `nx.k_truss()` |
| EgoNet | `cugraph.ego_graph(G, n, radius=)` | `cugraph.dask.community.egonet()` | `nx.ego_graph()` |
| Induced Subgraph | `cugraph.induced_subgraph(G, vertices)` | `cugraph.dask.community.induced_subgraph()` | `G.subgraph(vertices)` |

**Clustering Analysis:**
- `cugraph.analyzeClustering_edge_cut(G, n_clusters, clustering)`
- `cugraph.analyzeClustering_modularity(G, n_clusters, clustering)`
- `cugraph.analyzeClustering_ratio_cut(G, n_clusters, clustering)`

### Traversal

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| BFS | `cugraph.bfs(G, start=, depth_limit=)` | `cugraph.dask.traversal.bfs.bfs()` | `nx.bfs_edges()` |
| BFS Edges | `cugraph.bfs_edges(G, source)` | -- | `nx.bfs_edges()` |
| SSSP | `cugraph.sssp(G, source=)` | `cugraph.dask.traversal.sssp.sssp()` | `nx.single_source_dijkstra()` |
| Shortest Path | `cugraph.shortest_path(G, source=)` | -- | `nx.shortest_path()` |
| Shortest Path Length | `cugraph.shortest_path_length(G, source, target=)` | -- | `nx.shortest_path_length()` |
| Filter Unreachable | `cugraph.filter_unreachable(df)` | -- | -- |

### Link Analysis

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| PageRank | `cugraph.pagerank(G, alpha=)` | `cugraph.dask.link_analysis.pagerank()` | `nx.pagerank()` |
| HITS | `cugraph.hits(G, max_iter=, tol=)` | `cugraph.dask.link_analysis.hits()` | `nx.hits()` |

### Link Prediction / Similarity

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| Jaccard | `cugraph.jaccard(G, vertex_pair=)` | -- | `nx.jaccard_coefficient()` |
| Cosine Similarity | `cugraph.cosine(G, vertex_pair=)` | -- | -- |
| Overlap | `cugraph.overlap(G, vertex_pair=)` | `cugraph.dask.link_prediction.overlap()` | -- |
| Sorensen | `cugraph.sorensen(G, vertex_pair=)` | `cugraph.dask.link_prediction.sorensen()` | -- |

**NetworkX-compatible wrappers:** `cugraph.jaccard_coefficient(G, ebunch)`, `cugraph.overlap_coefficient(G, ebunch)`, `cugraph.sorensen_coefficient(G, ebunch)`

### Components

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| Connected Components | `cugraph.connected_components(G)` | -- | `nx.connected_components()` |
| Weakly Connected | `cugraph.weakly_connected_components(G)` | `cugraph.dask.components.weakly_connected_components()` | `nx.weakly_connected_components()` |
| Strongly Connected | `cugraph.strongly_connected_components(G)` | -- | `nx.strongly_connected_components()` |

### Cores

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| Core Number | `cugraph.core_number(G, degree_type=)` | `cugraph.dask.cores.core_number()` | `nx.core_number()` |
| K-Core | `cugraph.k_core(G, k=, core_number=)` | `cugraph.dask.cores.k_core()` | `nx.k_core()` |

### Sampling

| Algorithm | Single-GPU | Multi-GPU | Notes |
|---|---|---|---|
| Biased Random Walks | `cugraph.biased_random_walks(G, start_vertices)` | `cugraph.dask.sampling.biased_random_walks()` | Weighted/biased traversal |
| Uniform Random Walks | -- | `cugraph.dask.sampling.uniform_random_walks()` | Padded result with max path length |
| Random Walks | -- | `cugraph.dask.sampling.random_walks()` | General random walk |
| Node2Vec | -- | `cugraph.dask.sampling.node2vec_random_walks()` | Node2Vec sampling framework |
| Homogeneous Neighbor Sample | `cugraph.homogeneous_neighbor_sample(G, start_vertices, fanout)` | -- | Configurable fan-out per hop |
| Heterogeneous Neighbor Sample | `cugraph.heterogeneous_neighbor_sample(G, ...)` | -- | Multi-type node/edge graphs |

### Layout

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| Force Atlas 2 | `cugraph.force_atlas2(G)` | -- | `nx.forceatlas2_layout()` (via nx-cugraph) |

### Tree

| Algorithm | Single-GPU | Multi-GPU | NetworkX Equivalent |
|---|---|---|---|
| Minimum Spanning Tree | `cugraph.minimum_spanning_tree(G)` | -- | `nx.minimum_spanning_tree()` |
| Maximum Spanning Tree | `cugraph.maximum_spanning_tree(G)` | -- | `nx.maximum_spanning_tree()` |

### Linear Assignment

| Algorithm | Single-GPU | Multi-GPU |
|---|---|---|
| Hungarian | `cugraph.hungarian(G, workers, cost)` | -- |

### Utilities

| Function | Purpose |
|---|---|
| `cugraph.symmetrize(src, dst, val)` | Make edges bidirectional (for undirected graphs) |
| `cugraph.symmetrize_df(df, src, dst)` | Symmetrize a DataFrame |
| `cugraph.symmetrize_ddf(ddf, src, dst)` | Symmetrize a Dask DataFrame |
| `cugraph.NumberMap` | Map external vertex IDs to contiguous internal IDs |
| `G.unrenumber(df, col)` | Map internal vertex IDs back to original |

---

## Multi-GPU Support with Dask

cuGraph supports multi-GPU computation through Dask for graphs that exceed single-GPU memory or need faster processing.

### Setup
```python
from dask.distributed import Client
from dask_cuda import LocalCUDACluster
import cugraph
import cugraph.dask as dask_cugraph
import dask_cudf

# Initialize multi-GPU cluster
cluster = LocalCUDACluster()
client = Client(cluster)

# Load distributed edge list
ddf = dask_cudf.read_csv("large_graph.csv", names=["src", "dst", "weight"])

# Create distributed graph
G = cugraph.Graph(directed=True)
G.from_dask_cudf_edgelist(ddf, source="src", destination="dst", edge_attr="weight")

# Run multi-GPU algorithms
pr = dask_cugraph.pagerank(G)
components = dask_cugraph.weakly_connected_components(G)
```

### Algorithms with Multi-GPU Support

The following algorithms have Dask-based multi-GPU implementations:
- **Centrality:** Betweenness, Edge Betweenness, Eigenvector, Katz
- **Community:** Louvain, Leiden, ECG, K-Truss, Triangle Counting, EgoNet, Induced Subgraph
- **Components:** Weakly Connected Components
- **Cores:** Core Number, K-Core
- **Link Analysis:** PageRank, HITS
- **Link Prediction:** Overlap, Sorensen
- **Sampling:** Random Walks, Biased Random Walks, Uniform Random Walks, Node2Vec, Neighborhood Sampling
- **Traversal:** BFS, SSSP
- **Utilities:** Renumbering, Symmetrize, Path Extraction, Two-Hop Neighbors, RMAT Generator

---

## GNN Support

### cugraph-pyg (PyTorch Geometric Integration)

As of release 25.06, **cugraph-pyg is the recommended GNN framework integration** (cuGraph-DGL has been removed).

cugraph-pyg provides native GPU-accelerated implementations of PyG's core interfaces:

- **GraphStore**: GPU-accelerated graph storage using cuGraph's CSR representation
- **FeatureStore**: GPU-resident feature storage for node/edge features
- **Sampler/Loader**: GPU-accelerated neighborhood sampling with configurable fan-out

```bash
uv add --extra-index-url=https://pypi.nvidia.com "cugraph-pyg-cu12==26.6.*"
```

**Key capabilities:**
- Heterogeneous graph sampling (multiple node/edge types)
- Multi-GPU distributed sampling
- Direct integration with PyG's `NeighborLoader` and training loops
- GPU-accelerated centrality, community detection, and other analytics within PyG workflows

**Repository:** https://github.com/rapidsai/cugraph-gnn

### WholeGraph (Distributed GPU Memory for GNNs)

WholeGraph provides distributed GPU memory management for large-scale GNN training through its **WholeMemory** abstraction.

```bash
uv add --extra-index-url=https://pypi.nvidia.com "pylibwholegraph-cu12==26.6.*"
```

**Core concepts:**

- **WholeMemory**: A unified view of GPU memory distributed across multiple GPUs. Each GPU sees the entire memory space through a single abstraction, even though data is physically distributed.
- **WholeMemory Communicator**: Defines the set of GPUs that collaborate, with one process per GPU.
- **WholeMemory Tensor**: Like PyTorch tensors but distributed; supports 1D and 2D data with first dimension partitioned across GPUs.
- **WholeMemory Embedding**: 2D tensor variant with built-in cache policies and sparse optimizers (SGD, Adam, RMSProp, AdaGrad).

**Memory modes:**
| Mode | Description | Use Case |
|---|---|---|
| **Continuous** | Single continuous address space via hardware peer-to-peer | NVLink systems (DGX) |
| **Chunked** | Per-GPU chunks with direct multi-pointer access | Multi-GPU with some NVLink |
| **Distributed** | Explicit communication required for remote access | Multi-node clusters |

**Storage locations:** Host memory (pinned) or device/GPU memory.

**Graph storage:** CSR format with ROW_INDEX and COL_INDEX as WholeMemory Tensors for efficient distributed graph management.

**Cache policies:** Device-cached host memory, local-cached global memory -- critical for handling graphs larger than GPU memory.

**Target hardware:** NVLink systems like DGX A100/H100 servers for optimal performance.

### cuGraph-DGL (DEPRECATED)

**cuGraph-DGL has been removed as of release 25.06.** Users should migrate to cugraph-pyg. The cuGraph team is not planning further work in the DGL ecosystem.

---

## Performance Characteristics and Benchmarks

Benchmark with the user's actual topology and algorithm:

1. Check that the requested NetworkX algorithm dispatches to nx-cugraph rather than falling back
   to CPU.
2. Measure graph construction and conversion separately from repeated algorithm calls, then report
   both warm algorithm time and end-to-end time.
3. Warm the CUDA context before collecting timed repetitions.
4. Verify output semantics, convergence tolerance, sampled-algorithm parameters, and floating-point
   tolerance against the CPU implementation.
5. Record vertices, edges, directedness, weight dtype, GPU model, CPU baseline, software versions,
   and whether the graph was already device-resident.
6. Use multi-GPU only after estimating graph and temporary-memory requirements and measuring the
   communication cost.

Small or one-shot graphs can lose to NetworkX after setup and transfer. Large device-resident
graphs with supported algorithms are better candidates, but graph size alone does not establish a
speedup.

---

## Memory Management

### GPU Memory Considerations

- cuGraph stores graphs in CSR format on GPU memory
- Memory usage is approximately: `(num_edges * 2 * 4 bytes) + (num_vertices * 4 bytes)` for unweighted, plus `(num_edges * 8 bytes)` for weighted (float64 weights)
- A graph with 100M edges requires roughly ~1.6 GB unweighted or ~2.4 GB weighted
- Algorithm working memory varies; some algorithms (like betweenness centrality) need additional O(V) or O(E) temporary space

### Strategies for Large Graphs

1. **Use multi-GPU** via Dask for graphs exceeding single GPU memory
2. **Use WholeGraph** for GNN workloads that need distributed feature/graph storage
3. **Use `rmm`** (RAPIDS Memory Manager) for fine-grained GPU memory control:
   ```python
   import rmm
   rmm.reinitialize(pool_allocator=True, initial_pool_size=2**30)  # 1 GB pool
   ```
4. **Monitor memory** with `nvidia-smi` or `rmm.get_memory_info()`
5. **Delete intermediate results** explicitly: `del result; import gc; gc.collect()`

---

## Interoperability

### With cuDF
cuGraph natively consumes and produces cuDF DataFrames. Algorithm results are returned as cuDF DataFrames with vertex/edge columns.

```python
import cudf, cugraph
# Create graph from cuDF
edges = cudf.read_csv("edges.csv")
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="src", destination="dst")

# Results come back as cuDF DataFrames
pr = cugraph.pagerank(G)  # cuDF DataFrame with 'vertex' and 'pagerank' columns
```

### With cuML
Pipe graph analytics results into cuML for downstream ML:
```python
import cuml
# Use graph embeddings (e.g., from Node2Vec) as features for cuML
# Or use community labels as features for classification
louvain_result = cugraph.louvain(G)
# Feed partition labels into cuML models
```

### With CuPy / SciPy
```python
# cuGraph can work with CuPy and SciPy sparse matrices as input data
import cupy, scipy
```

### With NetworkX
```python
import networkx as nx
import nx_cugraph as nxcg

# Convert once when repeated algorithms justify keeping the graph on GPU.
G_nx = nx.karate_club_graph()
G_gpu = nxcg.from_networkx(G_nx)
result = nx.pagerank(G_gpu)
```

### With PyTorch Geometric
```python
# Via cugraph-pyg (see GNN Support section)
from cugraph_pyg.data import CuGraphStore
from cugraph_pyg.loader import CuGraphNeighborLoader
```

### With Pandas
```python
import pandas as pd
df = pd.DataFrame({"src": [0, 1, 2], "dst": [1, 2, 3]})
G = cugraph.Graph()
G.from_pandas_edgelist(df, source="src", destination="dst")
```

---

## Known Limitations vs NetworkX

1. **Immutable graphs:** Cannot add/remove individual edges after graph creation. Must reconstruct from DataFrame.
2. **No node/edge attributes on Graph object:** cuGraph stores structure only. Node/edge properties must be maintained separately (e.g., in cuDF DataFrames). The nx-cugraph backend handles attribute mapping transparently.
3. **Vertex types:** Vertices must be integers (or will be renumbered to integers internally). String vertex IDs are renumbered automatically.
4. **Not all NetworkX algorithms supported:** Check the nx-cugraph supported algorithms list. Unsupported calls fall back to CPU NetworkX.
5. **Numerical precision:** GPU floating-point results may differ slightly from CPU results due to parallel reduction ordering.
6. **No dynamic graphs:** cuGraph is designed for static graph analytics, not streaming/dynamic graph updates.
7. **Strongly Connected Components:** Single-GPU only (no multi-GPU Dask variant).
8. **Spectral Clustering:** Single-GPU only.
9. **Minimum/Maximum Spanning Tree:** Single-GPU only.
10. **Force Atlas 2 layout:** Single-GPU only.
11. **Compatibility doc:** The official list of NetworkX APIs accelerated by nx-cugraph is maintained at https://docs.rapids.ai/api/cugraph/stable/nx_cugraph/supported-algorithms/ (~80 algorithms plus generators and utilities).

---

## Common Migration Patterns

### NetworkX to nx-cugraph (Zero Effort)
```python
# Before (CPU):
import networkx as nx
G = nx.from_pandas_edgelist(df, "src", "dst")
pr = nx.pagerank(G)

# After (GPU, no code changes):
# Just set: NX_CUGRAPH_AUTOCONFIG=True
# Same code runs on GPU automatically
```

### NetworkX to Direct cuGraph API
```python
# Before (NetworkX):
import networkx as nx
G = nx.from_pandas_edgelist(df, "src", "dst")
pr = nx.pagerank(G, alpha=0.85)
bc = nx.betweenness_centrality(G, k=100)
communities = nx.community.louvain_communities(G, resolution=1.0)

# After (cuGraph):
import cudf, cugraph
edges = cudf.from_pandas(df)
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="src", destination="dst")
pr = cugraph.pagerank(G, alpha=0.85)
bc = cugraph.betweenness_centrality(G)
parts, modularity = cugraph.louvain(G, resolution=1.0)
```

### Pandas to cuDF + cuGraph Pipeline
```python
# Before:
import pandas as pd
import networkx as nx
df = pd.read_csv("edges.csv")
G = nx.from_pandas_edgelist(df, "source", "target", "weight")
result = nx.pagerank(G)

# After:
import cudf
import cugraph
df = cudf.read_csv("edges.csv")
G = cugraph.Graph()
G.from_cudf_edgelist(df, source="source", destination="target", edge_attr="weight")
result = cugraph.pagerank(G)
```

### Adding Multi-GPU to Existing cuGraph Code
```python
# Before (single-GPU):
import cugraph
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="src", destination="dst")
result = cugraph.pagerank(G)

# After (multi-GPU):
from dask.distributed import Client
from dask_cuda import LocalCUDACluster
import cugraph, cugraph.dask as dcg
import dask_cudf

cluster = LocalCUDACluster()
client = Client(cluster)

ddf = dask_cudf.from_cudf(edges, npartitions=len(cluster.workers))
G = cugraph.Graph()
G.from_dask_cudf_edgelist(ddf, source="src", destination="dst")
result = dcg.pagerank(G)
result_local = result.compute()  # Collect to single GPU
```

### `references/cuml.md`

# cuML Reference

cuML is NVIDIA's GPU-accelerated machine learning library within the RAPIDS ecosystem. It
provides scikit-learn-compatible APIs for classification, regression, clustering, dimensionality
reduction, preprocessing, and model selection. Performance depends on algorithm, shape, dtype,
fallback behavior, and transfer cost; benchmark the complete pipeline on representative data.

> **Full documentation:** https://docs.rapids.ai/api/cuml/stable/

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Two Usage Modes](#two-usage-modes)
3. [cuml.accel Accelerator Mode](#cumlaccel-accelerator-mode)
4. [Direct cuML API](#direct-cuml-api)
5. [Algorithm Catalog](#algorithm-catalog)
6. [Input/Output Type Handling](#inputoutput-type-handling)
7. [Preprocessing](#preprocessing)
8. [Feature Extraction](#feature-extraction)
9. [Model Selection and Tuning](#model-selection-and-tuning)
10. [Forest Inference Library (FIL)](#forest-inference-library)
11. [Multi-GPU with Dask](#multi-gpu-with-dask)
12. [Model Serialization](#model-serialization)
13. [Memory Management](#memory-management)
14. [Performance Optimization](#performance-optimization)
15. [Interoperability](#interoperability)
16. [Key Differences from sklearn](#key-differences-from-sklearn)
17. [Common Migration Patterns](#common-migration-patterns)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add "cuml-cu12==26.6.*"    # For CUDA 12.x
uv add "cuml-cu13==26.6.*"    # For CUDA 13.x
```

cuML wheels are published directly to PyPI (since RAPIDS 25.10) — the `--extra-index-url=https://pypi.nvidia.com` extra index is no longer required.

**Platform:** Linux and WSL2 only (no native macOS or Windows).
**Requires:** Python >= 3.11, scikit-learn >= 1.5, NVIDIA GPU with CUDA 12.x or 13.x support.

Verify:
```python
import cuml
print(cuml.__version__)

from cuml.datasets import make_blobs
X, y = make_blobs(n_samples=1000, n_features=10)
print(f"Generated {X.shape[0]} samples on GPU")
```

---

## Two Usage Modes

### 1. cuml.accel (Zero-Code-Change)
Transparently intercepts sklearn, umap-learn, and hdbscan calls and routes them to GPU. Falls back to CPU for unsupported operations. Best for: quick acceleration of existing sklearn code, mixed codebases, prototyping.

### 2. Direct cuML API
Replace `from sklearn` with `from cuml`. Maximum performance, explicit control over GPU execution. Best for: production pipelines, maximum performance, new GPU-first code.

---

## cuml.accel Accelerator Mode

The fastest path from sklearn to GPU — no code changes required. Similar to `cudf.pandas` for pandas.

### Activation

```python
# Jupyter/IPython (MUST be the first cell, before any sklearn import)
%load_ext cuml.accel

import sklearn  # Now GPU-accelerated
from sklearn.cluster import KMeans  # Runs on GPU transparently
```

```bash
# Command line
python -m cuml.accel script.py
python -m cuml.accel -v script.py     # With info logging
python -m cuml.accel -vv script.py    # With debug logging
```

```python
# Programmatic (call BEFORE importing sklearn)
import cuml
cuml.accel.install()

from sklearn.cluster import KMeans  # Now GPU-accelerated
```

```bash
# Environment variable
CUML_ACCEL_ENABLED=1 python script.py
```

### How It Works

- Intercepts sklearn/umap-learn/hdbscan imports and replaces estimators with GPU versions.
- If an operation isn't supported on GPU, it silently falls back to CPU sklearn.
- Uses managed memory by default — host RAM augments GPU VRAM.
- Models pickled under cuml.accel load as standard sklearn objects in non-GPU environments.
- Accelerates 30+ algorithms across sklearn, umap-learn, and hdbscan. Recent releases (26.04-26.06) expanded coverage to preprocessing estimators (StandardScaler, MinMaxScaler, MaxAbsScaler, PolynomialFeatures, LabelEncoder) and SpectralClustering.
- Compatible with scikit-learn versions 1.5-1.8 (some estimators require >= 1.8, which enables GPU acceleration via scikit-learn's experimental array-api support).

### Known Fallback Triggers (Runs on CPU Instead)

- Sparse input data (most algorithms)
- Callable parameters (e.g., callable `init` for KMeans)
- Certain parameter values: `n_components="mle"` for PCA, `positive=True` for linear models, warm starts
- Unsupported distance metrics for neighbors algorithms
- Multi-output targets for Random Forest
- String/object dtypes — must pre-encode with LabelEncoder first

### Numerical Precision

GPU results are numerically equivalent but may differ at floating-point precision level due to parallel reduction order. Compare model quality via scores (accuracy, R2, etc.), not raw coefficient values.

---

## Direct cuML API

Replace sklearn imports with cuml imports. The API is identical — fit/predict/transform.

```python
from cuml.cluster import DBSCAN
from cuml.datasets import make_blobs

# Create data directly on GPU
X, y = make_blobs(n_samples=100_000, centers=5, n_features=10, random_state=42)

# Fit — runs on GPU
model = DBSCAN(eps=1.0, min_samples=5)
model.fit(X)
print(model.labels_)
```

```python
from cuml import LinearRegression
from cuml.datasets import make_regression
from cuml.model_selection import train_test_split

X, y = make_regression(n_samples=100_000, n_features=50, noise=0.1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
score = model.score(X_test, y_test)
print(f"R2 score: {score:.4f}")
```

---

## Algorithm Catalog

### Clustering

| cuML | sklearn Equivalent | Multi-GPU |
|------|-------------------|-----------|
| `cuml.KMeans` | `sklearn.cluster.KMeans` | Yes |
| `cuml.DBSCAN` | `sklearn.cluster.DBSCAN` | Yes |
| `cuml.AgglomerativeClustering` | `sklearn.cluster.AgglomerativeClustering` | No |
| `cuml.cluster.hdbscan.HDBSCAN` | `hdbscan.HDBSCAN` | No |
| `cuml.cluster.SpectralClustering` | `sklearn.cluster.SpectralClustering` | No |

### Regression

| cuML | sklearn Equivalent | Multi-GPU |
|------|-------------------|-----------|
| `cuml.LinearRegression` | `sklearn.linear_model.LinearRegression` | Yes |
| `cuml.Ridge` | `sklearn.linear_model.Ridge` | Yes |
| `cuml.Lasso` | `sklearn.linear_model.Lasso` | Yes |
| `cuml.ElasticNet` | `sklearn.linear_model.ElasticNet` | Yes |
| `cuml.SVR` | `sklearn.svm.SVR` | No |
| `cuml.KernelRidge` | `sklearn.kernel_ridge.KernelRidge` | No |
| `cuml.ensemble.RandomForestRegressor` | `sklearn.ensemble.RandomForestRegressor` | Yes |
| `cuml.MBSGDRegressor` | `sklearn.linear_model.SGDRegressor` | No |

### Classification

| cuML | sklearn Equivalent | Multi-GPU |
|------|-------------------|-----------|
| `cuml.LogisticRegression` | `sklearn.linear_model.LogisticRegression` | No |
| `cuml.ensemble.RandomForestClassifier` | `sklearn.ensemble.RandomForestClassifier` | Yes |
| `cuml.svm.SVC` | `sklearn.svm.SVC` | No |
| `cuml.svm.LinearSVC` | `sklearn.svm.LinearSVC` | No |
| `cuml.naive_bayes.GaussianNB` | `sklearn.naive_bayes.GaussianNB` | No |
| `cuml.naive_bayes.MultinomialNB` | `sklearn.naive_bayes.MultinomialNB` | Yes |
| `cuml.naive_bayes.BernoulliNB` | `sklearn.naive_bayes.BernoulliNB` | No |
| `cuml.naive_bayes.CategoricalNB` | `sklearn.naive_bayes.CategoricalNB` | No |
| `cuml.naive_bayes.ComplementNB` | `sklearn.naive_bayes.ComplementNB` | No |
| `cuml.neighbors.KNeighborsClassifier` | `sklearn.neighbors.KNeighborsClassifier` | Yes |
| `cuml.neighbors.KNeighborsRegressor` | `sklearn.neighbors.KNeighborsRegressor` | Yes |
| `cuml.MBSGDClassifier` | `sklearn.linear_model.SGDClassifier` | No |
| `cuml.multiclass.OneVsOneClassifier` | `sklearn.multiclass.OneVsOneClassifier` | No |
| `cuml.multiclass.OneVsRestClassifier` | `sklearn.multiclass.OneVsRestClassifier` | No |

### Dimensionality Reduction and Manifold Learning

| cuML | sklearn/Library Equivalent | Multi-GPU |
|------|---------------------------|-----------|
| `cuml.PCA` | `sklearn.decomposition.PCA` | Yes |
| `cuml.IncrementalPCA` | `sklearn.decomposition.IncrementalPCA` | No |
| `cuml.TruncatedSVD` | `sklearn.decomposition.TruncatedSVD` | Yes |
| `cuml.UMAP` | `umap.UMAP` | Yes (inference) |
| `cuml.TSNE` | `sklearn.manifold.TSNE` | No |
| `cuml.random_projection.GaussianRandomProjection` | `sklearn.random_projection.GaussianRandomProjection` | No |
| `cuml.random_projection.SparseRandomProjection` | `sklearn.random_projection.SparseRandomProjection` | No |

### Nearest Neighbors

| cuML | sklearn Equivalent | Multi-GPU |
|------|-------------------|-----------|
| `cuml.neighbors.NearestNeighbors` | `sklearn.neighbors.NearestNeighbors` | Yes |
| `cuml.neighbors.KNeighborsClassifier` | `sklearn.neighbors.KNeighborsClassifier` | Yes |
| `cuml.neighbors.KNeighborsRegressor` | `sklearn.neighbors.KNeighborsRegressor` | Yes |
| `cuml.neighbors.KernelDensity` | `sklearn.neighbors.KernelDensity` | No |

### Time Series

| cuML | Description |
|------|-------------|
| `cuml.ExponentialSmoothing` | Holt-Winters exponential smoothing |
| `cuml.tsa.ARIMA` | ARIMA/SARIMA models (batched — fits multiple series simultaneously) |
| `cuml.tsa.auto_arima.AutoARIMA` | Automatic ARIMA order selection |

### Metrics (GPU-Accelerated)

**Regression:** `r2_score`, `mean_squared_error`, `mean_absolute_error`, `mean_squared_log_error`, `median_absolute_error`

**Classification:** `accuracy_score`, `log_loss`, `roc_auc_score`, `precision_recall_curve`, `confusion_matrix`

**Clustering:** `adjusted_rand_score`, `silhouette_score`, `silhouette_samples`, `homogeneity_score`, `completeness_score`, `v_measure_score`, `mutual_info_score`

**Other:** `trustworthiness`, `pairwise_distances`, `pairwise_kernels`

### Model Explainability

| cuML | Description |
|------|-------------|
| `cuml.explainer.KernelExplainer` | SHAP Kernel Explainer |
| `cuml.explainer.PermutationExplainer` | SHAP Permutation Explainer |
| `cuml.explainer.TreeExplainer` | SHAP Tree Explainer |

---

## Input/Output Type Handling

### Supported Input Types

cuML accepts: NumPy arrays, CuPy arrays, cuDF DataFrames/Series, pandas DataFrames/Series, Numba device arrays, PyTorch tensors (via `__cuda_array_interface__`).

NumPy and pandas inputs are automatically transferred to GPU. For best performance, pass CuPy arrays or cuDF DataFrames to avoid transfers.

### Controlling Output Type

```python
import cuml

# Global setting
cuml.set_global_output_type('cupy')  # Options: 'input', 'cupy', 'numpy', 'cudf', 'pandas'

# Context manager
with cuml.using_output_type('cudf'):
    result = model.predict(X)  # Returns cudf Series

# Per-estimator
model = cuml.KMeans(output_type='cupy')
```

**Performance ranking** (fastest to slowest output type):
1. `cupy` — no host transfers, most efficient
2. `cudf` — slight overhead for some shapes
3. `numpy` / `pandas` — device-to-host transfer cost

**Best practice:** Use `cupy` or `cudf` for intermediate results. Only convert to `numpy`/`pandas` at the end for visualization or export.

---

## Preprocessing

cuML provides GPU-accelerated versions of all common sklearn preprocessors.

### Scalers and Transformers

```python
from cuml.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from cuml.preprocessing import Normalizer, PowerTransformer, QuantileTransformer
from cuml.preprocessing import Binarizer, PolynomialFeatures, KBinsDiscretizer

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### Encoders

```python
from cuml.preprocessing import LabelEncoder, OneHotEncoder, LabelBinarizer, TargetEncoder

le = LabelEncoder()
y_encoded = le.fit_transform(y)

ohe = OneHotEncoder(sparse_output=False)
X_encoded = ohe.fit_transform(X_categorical)
```

### Imputers

```python
from cuml.preprocessing import SimpleImputer, MissingIndicator

imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)
```

### Pipeline and Composition

```python
from cuml.compose import ColumnTransformer, make_column_transformer
from cuml.preprocessing import StandardScaler, OneHotEncoder

preprocessor = make_column_transformer(
    (StandardScaler(), ['age', 'income']),
    (OneHotEncoder(), ['category', 'region']),
)
X_processed = preprocessor.fit_transform(df)
```

### Preprocessing Functions

`scale()`, `minmax_scale()`, `maxabs_scale()`, `robust_scale()`, `normalize()`, `binarize()`, `add_dummy_feature()`, `label_binarize()`

---

## Feature Extraction

```python
from cuml.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer

tfidf = TfidfVectorizer(max_features=10000)
X_tfidf = tfidf.fit_transform(corpus)
```

---

## Model Selection and Tuning

### Train/Test Split

```python
from cuml.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
```

### Cross-Validation

```python
from cuml.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, test_idx in kf.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    # ...
```

### Hyperparameter Tuning

For GPU-efficient hyperparameter search, use dask-ml's GridSearchCV/RandomizedSearchCV rather than sklearn's — sklearn's version causes excessive CPU-GPU data transfers per fold.

```python
from dask_ml.model_selection import RandomizedSearchCV
from cuml.ensemble import RandomForestClassifier

param_distributions = {
    'max_depth': [8, 12, 16, 20],
    'n_estimators': [100, 200, 500],
    'max_features': [0.5, 0.75, 1.0],
}

search = RandomizedSearchCV(
    RandomForestClassifier(),
    param_distributions,
    n_iter=25,
    cv=5,
    random_state=42,
)
search.fit(X_train, y_train)
print(f"Best score: {search.best_score_:.4f}")
print(f"Best params: {search.best_params_}")
```

### Dataset Generators

```python
from cuml.datasets import make_blobs, make_classification, make_regression

X, y = make_blobs(n_samples=100_000, centers=5, n_features=20, random_state=42)
X, y = make_classification(n_samples=100_000, n_features=50, n_informative=25)
X, y = make_regression(n_samples=100_000, n_features=50, noise=0.1)
```

---

## Forest Inference Library

FIL provides GPU inference for supported tree-based models trained in other frameworks. Its value
depends on model structure and inference batch size, so compare warm and end-to-end latency with
the deployment baseline.

```python
from cuml.fil import ForestInference

# Load from XGBoost, LightGBM, or sklearn saved models
fil_model = ForestInference.load("xgboost_model.ubj", is_classifier=True)

# Optional: optimize for specific batch size
fil_model.optimize()

# Predict on GPU
predictions = fil_model.predict(X_test)
probas = fil_model.predict_proba(X_test)
```

**Supports:** XGBoost, LightGBM, sklearn Random Forests, any Treelite-compatible model.

This is especially valuable when you have a model already trained on CPU and want to speed up inference without retraining.

---

## Multi-GPU with Dask

For datasets too large for a single GPU or when you want to use multiple GPUs.

```python
from dask.distributed import Client
from dask_cuda import LocalCUDACluster

# One Dask worker per GPU
cluster = LocalCUDACluster(
    rmm_pool_size="12GB",
    enable_cudf_spill=True,
)
client = Client(cluster)

# Create distributed data
from cuml.dask.datasets import make_blobs
X, y = make_blobs(
    n_samples=1_000_000,
    n_features=20,
    centers=5,
    n_parts=len(client.scheduler_info()['workers']) * 2,  # 2 partitions per worker
)

# Use Dask estimator
from cuml.dask.cluster import KMeans
kmeans = KMeans(n_clusters=5)
kmeans.fit(X)
labels = kmeans.predict(X)

# Convert to single-GPU model for serialization
single_model = kmeans.get_combined_model()

client.close()
cluster.close()
```

### Available Multi-GPU Estimators (`cuml.dask`)

- **Clustering:** KMeans, DBSCAN
- **Linear models:** LinearRegression, Ridge, Lasso, ElasticNet
- **Ensemble:** RandomForestClassifier, RandomForestRegressor
- **Decomposition:** PCA, TruncatedSVD
- **Manifold:** UMAP (inference only)
- **Neighbors:** NearestNeighbors, KNeighborsClassifier, KNeighborsRegressor
- **Naive Bayes:** MultinomialNB
- **Preprocessing:** LabelEncoder, LabelBinarizer, OneHotEncoder

---

## Model Serialization

```python
import pickle

# Save cuML model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f, protocol=5)

# Load cuML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)
```

- Models trained under cuml.accel can be pickled and loaded as standard sklearn objects in non-GPU environments.
- Dask distributed models must be converted first: `single_model = dask_model.get_combined_model()`.
- joblib also works for serialization.

---

## Memory Management

### RMM (RAPIDS Memory Manager)

```python
import rmm

# Pre-allocate a memory pool for faster allocation
rmm.reinitialize(pool_allocator=True, initial_pool_size=2**32)  # 4 GB pool
```

### Aligning with cuDF and CuPy

When using cuML alongside cuDF and CuPy, align all libraries on the same RMM allocator:

```python
import rmm
from rmm.allocators.cupy import rmm_cupy_allocator
import cupy
cupy.cuda.set_allocator(rmm_cupy_allocator)
```

### cuml.accel Memory

cuml.accel uses managed memory by default (host RAM augments GPU VRAM). Disable with `--disable-uvm` flag if experiencing slowdowns. Managed memory does NOT work on WSL2 or when RMM is externally configured.

### Best Practices

- Use float32 instead of float64 when precision allows — halves memory, doubles throughput.
- Keep data on GPU throughout the pipeline — avoid NumPy/pandas round-trips.
- For datasets larger than GPU memory: use Dask multi-GPU or chunk processing.
- Pre-allocate RMM pools to avoid fragmentation.

---

## Performance Optimization

### Benchmarking

1. Verify whether `cuml.accel` used a GPU implementation or fell back to scikit-learn.
2. Compare the same estimator parameters, train/test split, random seed, and output semantics.
3. Warm the CUDA context and any lazy compilation before timed repetitions.
4. Report fit, transform/predict, and end-to-end times separately, including conversion and
   transfer costs paid by the application.
5. Record rows, features, sparsity, dtype, estimator parameters, CPU/GPU models, and software
   versions.
6. For stochastic or approximate algorithms, compare quality metrics as well as time.

### Key Optimization Tips

1. **Use float32 when the model's accuracy and stability permit it.** Validate metrics after
changing precision; architecture-specific throughput ratios are not a correctness argument.

2. **Keep data on GPU.** Pass CuPy arrays or cuDF DataFrames. Every NumPy/pandas conversion triggers a device-host transfer.

3. **Use enough work to amortize setup and transfer.** Do not rely on a fixed row threshold;
features, sparsity, estimator, batch size, and reuse all matter.

4. **Benchmark the actual feature shape.** Width affects compute, memory traffic, and temporary
storage differently for each estimator.

5. **First call has JIT overhead.** Benchmark on subsequent calls, not the first.

6. **Use RMM pools when allocation overhead or fragmentation is visible in profiling.** Pools
amortize allocator costs but reserve device memory and should be sized deliberately.

7. **Use dask-ml for hyperparameter tuning,** not sklearn's GridSearchCV — it avoids excessive CPU-GPU transfers.

8. **Evaluate FIL for supported tree-model inference.** Benchmark the target model and production
batch sizes against the existing serving path.

---

## Interoperability

- **cuDF:** Zero-copy input. cuDF DataFrames accepted directly by all estimators.
- **CuPy:** Zero-copy via `__cuda_array_interface__`. Most efficient intermediate format.
- **NumPy/pandas:** Accepted as input (auto-transferred to GPU). Output type configurable.
- **PyTorch:** Tensors accepted via array interface.
- **sklearn:** API-compatible. Models interconvertible. cuml.accel for transparent acceleration.
- **XGBoost/LightGBM:** FIL provides GPU inference for externally-trained tree models.
- **Dask:** Native distributed support via `cuml.dask` module.

### End-to-End RAPIDS Pipeline

```python
import cudf
import cuml
from cuml.preprocessing import StandardScaler
from cuml.ensemble import RandomForestClassifier
from cuml.model_selection import train_test_split

# Load data on GPU
df = cudf.read_parquet("data.parquet")
X = df.drop("target", axis=1)
y = df["target"]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Preprocess
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train
model = RandomForestClassifier(n_estimators=100, max_depth=16)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Accuracy: {score:.4f}")
```

All of this runs entirely on GPU — from Parquet read to model evaluation — with zero CPU-GPU transfers.

---

## Key Differences from sklearn

1. **Platform:** Linux and WSL2 only. No native macOS or Windows.

2. **Sparse data:** Most cuML algorithms do not support sparse matrices (Lasso and ElasticNet gained sparse input support in 26.06). Under cuml.accel, sparse inputs fall back to CPU.

3. **String data:** Must be pre-encoded to numeric. No native string column support in estimators.

4. **Multi-output:** Not supported for Random Forest.

5. **Warm starts:** Not supported for most algorithms.

6. **Some sklearn parameters ignored:** `n_jobs` (GPU handles parallelism), `positive=True`, specific solver choices.

7. **Numerical precision:** Results equivalent in quality but may differ at floating-point level. Compare scores, not raw coefficients.

8. **Memory:** Limited by GPU VRAM (typically 8-80 GB). Use managed memory or Dask for larger datasets.

9. **Missing fitted attributes:** Some sklearn attributes not computed under cuml.accel (e.g., HDBSCAN `exemplars_`, LinearRegression `rank_`).

---

## Common Migration Patterns

### Pattern 1: Zero-Effort (cuml.accel)

```python
# Add one line at top of notebook:
%load_ext cuml.accel

from sklearn.cluster import KMeans  # Now GPU-accelerated
from sklearn.decomposition import PCA  # Now GPU-accelerated
# Everything else stays exactly the same
```

### Pattern 2: Direct Import Swap

```python
# Before
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# After
from cuml.ensemble import RandomForestClassifier
from cuml.preprocessing import StandardScaler
from cuml.model_selection import train_test_split
```

### Pattern 3: Full RAPIDS Pipeline (cuDF + cuML)

```python
import cudf
from cuml.preprocessing import StandardScaler, LabelEncoder
from cuml.ensemble import RandomForestClassifier
from cuml.model_selection import train_test_split

# Load and preprocess entirely on GPU
df = cudf.read_parquet("data.parquet")
le = LabelEncoder()
df["category_encoded"] = le.fit_transform(df["category"])

X = df[["feature1", "feature2", "category_encoded"]].to_cupy()
y = df["target"].to_cupy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200, max_depth=16)
model.fit(X_train, y_train)
print(f"Accuracy: {model.score(X_test, y_test):.4f}")
```

### Pattern 4: GPU Inference for CPU-Trained Models

```python
from cuml.fil import ForestInference

# Load a supported XGBoost/LightGBM/sklearn model for GPU inference
fil_model = ForestInference.load("my_xgboost_model.ubj", is_classifier=True)
predictions = fil_model.predict(X_test)
```

### `references/cupy.md`

# CuPy Reference

CuPy is a NumPy/SciPy-compatible array library for GPU-accelerated computing. It wraps NVIDIA's optimized libraries (cuBLAS, cuFFT, cuSOLVER, cuSPARSE, cuRAND) so standard array operations are already highly tuned. Most NumPy code works by simply changing the import.

> **Full documentation:** https://docs.cupy.dev/en/stable/

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [The Drop-In Replacement Pattern](#the-drop-in-replacement-pattern)
3. [Core API: cupy.ndarray](#core-api)
4. [Supported Operations](#supported-operations)
5. [Custom Kernels](#custom-kernels)
6. [Kernel Fusion](#kernel-fusion)
7. [Memory Management](#memory-management)
8. [Streams and Async Operations](#streams-and-async-operations)
9. [Multi-GPU](#multi-gpu)
10. [Performance Optimization](#performance-optimization)
11. [Interoperability](#interoperability)
12. [Key Differences from NumPy](#key-differences-from-numpy)
13. [Common Pitfalls](#common-pitfalls)
14. [Environment Variables](#environment-variables)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add "cupy-cuda12x==14.1.*"    # For CUDA 12.x
uv add "cupy-cuda13x==14.1.*"    # For CUDA 13.x
```

CuPy v14 (current) requires CUDA >= 12.0, Python >= 3.10, and NumPy >= 2.0 (it follows NumPy 2 type-promotion rules, NEP 50), and supports free-threaded Python. The `[ctk]` extra (e.g. `cupy-cuda13x[ctk]`) pulls the required CUDA runtime components from PyPI, so only the NVIDIA driver needs to be pre-installed.

Verify:
```python
import cupy as cp
print(cp.cuda.runtime.getDeviceCount())  # >= 1 means GPU is available
print(cp.show_config())                  # Full environment info
```

---

## The Drop-In Replacement Pattern

The fastest way to GPU-accelerate NumPy code: change the import.

```python
# Before (CPU)
import numpy as np
a = np.random.rand(10_000_000)
b = np.fft.fft(a)
c = np.sort(b.real)

# After (GPU)
import cupy as cp
a = cp.random.rand(10_000_000)
b = cp.fft.fft(a)
c = cp.sort(b.real)
```

### Data Transfer Between CPU and GPU

```python
# NumPy → CuPy (CPU → GPU)
gpu_array = cp.asarray(numpy_array)     # Zero-copy if already on current device
gpu_array = cp.array(numpy_array)       # Always copies

# CuPy → NumPy (GPU → CPU)
cpu_array = cp.asnumpy(gpu_array)       # Copy to CPU
cpu_array = gpu_array.get()             # Same thing
```

### Writing CPU/GPU Agnostic Code

```python
def normalize(x):
    xp = cp.get_array_module(x)  # Returns cupy or numpy depending on input
    return x / xp.linalg.norm(x)

# Works with both NumPy and CuPy arrays
normalize(numpy_array)   # Runs on CPU
normalize(cupy_array)    # Runs on GPU
```

CuPy arrays implement `__array_ufunc__` and `__array_function__`, so NumPy functions can dispatch to CuPy automatically when given CuPy arrays (NumPy >= 1.17).

---

## Core API

`cupy.ndarray` mirrors `numpy.ndarray` — same attributes (`shape`, `dtype`, `ndim`, `size`, `strides`, `T`), plus `device` (which GPU the array lives on).

**Important:** `cupy.ndarray` and `numpy.ndarray` are NOT implicitly convertible. Every conversion incurs a host-device data transfer.

### Array Creation

```python
cp.empty((1000, 1000), dtype=cp.float32)
cp.zeros((1000,), dtype=cp.float64)
cp.ones((512, 512), dtype=cp.float32)
cp.full((100,), fill_value=3.14, dtype=cp.float32)
cp.arange(0, 100, 0.1)
cp.linspace(0, 1, 1000)
cp.eye(100)
cp.random.rand(1000, 1000)                    # Uniform [0, 1)
cp.random.randn(1000, 1000)                   # Standard normal
cp.random.default_rng(42).normal(0, 1, 1000)  # Generator API
```

CuPy's random supports a `dtype` argument (float32/float64) — unlike NumPy which always returns float64. Use `dtype=cp.float32` when you don't need double precision.

---

## Supported Operations

CuPy implements most of NumPy and large parts of SciPy. All are GPU-accelerated.

### Array Math and Element-wise Operations
`sin`, `cos`, `tan`, `exp`, `log`, `log2`, `log10`, `sqrt`, `square`, `abs`, `power`, `add`, `subtract`, `multiply`, `divide`, `mod`, `clip`, `sign`, `ceil`, `floor`, `round`, `maximum`, `minimum`

### Reductions
`sum`, `prod`, `mean`, `std`, `var`, `min`, `max`, `argmin`, `argmax`, `cumsum`, `cumprod`, `any`, `all`, `nansum`, `nanmean`, `nanstd`, `nanvar`

### Linear Algebra (`cupy.linalg` — powered by cuBLAS/cuSOLVER)
`dot`, `matmul`, `@` operator, `tensordot`, `einsum`, `inner`, `outer`, `cholesky`, `qr`, `svd`, `eig`, `eigh`, `eigvalsh`, `norm`, `solve`, `inv`, `pinv`, `lstsq`, `det`, `slogdet`, `matrix_rank`, `matrix_power`

### FFT (`cupy.fft` — powered by cuFFT)
`fft`, `ifft`, `fft2`, `ifft2`, `fftn`, `ifftn`, `rfft`, `irfft`, `rfft2`, `irfft2`, `rfftn`, `irfftn`, `fftfreq`, `rfftfreq`, `fftshift`, `ifftshift`

### Sorting and Searching
`sort`, `argsort`, `partition`, `argpartition`, `argmin`, `argmax`, `where`, `nonzero`, `unique`, `searchsorted`

### Array Manipulation
`reshape`, `ravel`, `flatten`, `transpose`, `swapaxes`, `concatenate`, `stack`, `vstack`, `hstack`, `dstack`, `split`, `hsplit`, `vsplit`, `tile`, `repeat`, `pad`, `flip`, `fliplr`, `flipud`, `roll`, `rot90`, `broadcast_to`, `expand_dims`, `squeeze`

### Sparse Matrices (`cupyx.scipy.sparse`)
CSR, CSC, COO formats. Matrix-vector multiply, matrix-matrix multiply, conversions between formats. Powered by cuSPARSE. CuPy v14 adds support for large sparse matrices with 64-bit dimensions and nonzero counts.

### Signal Processing (`cupyx.scipy.signal`)
Convolution, correlation, filtering, window functions.

### Special Functions (`cupyx.scipy.special`)
Bessel functions, error functions, gamma functions, and more.

### Statistics
`mean`, `median`, `std`, `var`, `percentile`, `quantile`, `corrcoef`, `cov`, `histogram`, `bincount`, `digitize`

---

## Custom Kernels

When built-in operations aren't enough, CuPy offers several ways to write custom GPU code, ordered from simplest to most powerful.

### ElementwiseKernel — Custom Element-wise Operations

CuPy handles indexing and broadcasting automatically. You just write the per-element logic in C++.

```python
squared_diff = cp.ElementwiseKernel(
    'float32 x, float32 y',   # Input params
    'float32 z',               # Output params
    'z = (x - y) * (x - y)',  # Per-element operation (C++ code)
    'squared_diff'             # Kernel name
)

result = squared_diff(a, b)  # Broadcasting works automatically
```

**Type-generic kernels:** Use single-letter type placeholders. Same letter = same type, resolved from arguments at call time.

```python
generic_squared_diff = cp.ElementwiseKernel(
    'T x, T y', 'T z',
    'z = (x - y) * (x - y)',
    'generic_squared_diff'
)
# Works with float32, float64, etc. — type inferred from inputs
```

**Raw indexing:** Prefix with `raw` to disable automatic indexing. Use `i` for loop index.

```python
# Access neighbors — raw disables auto-indexing so you can index manually
stencil = cp.ElementwiseKernel(
    'raw T x', 'T y',
    'y = (x[i > 0 ? i-1 : 0] + x[i] + x[i < _ind.size()-1 ? i+1 : _ind.size()-1]) / 3',
    'stencil_1d'
)
```

### ReductionKernel — Custom Reductions

Four-part reduction: map each element, reduce pairs, post-process the result.

```python
l2norm = cp.ReductionKernel(
    'T x',           # Input
    'T y',           # Output
    'x * x',         # Map: square each element
    'a + b',         # Reduce: sum pairs (a, b are the binary operands)
    'y = sqrt(a)',   # Post-map: sqrt of final sum
    '0',             # Identity element
    'l2norm'         # Kernel name
)

norm = l2norm(array)        # Full reduction → scalar
norms = l2norm(matrix, axis=1)  # Reduce along axis → vector
```

### RawKernel — Full CUDA C/C++

For complete control over grid, blocks, shared memory — write raw CUDA.

```python
kernel_code = r'''
extern "C" __global__
void vector_add(const float* a, const float* b, float* c, int n) {
    int tid = blockDim.x * blockIdx.x + threadIdx.x;
    if (tid < n) {
        c[tid] = a[tid] + b[tid];
    }
}
'''
vector_add = cp.RawKernel(kernel_code, 'vector_add')

n = 1_000_000
a = cp.random.rand(n, dtype=cp.float32)
b = cp.random.rand(n, dtype=cp.float32)
c = cp.zeros(n, dtype=cp.float32)

threads = 256
blocks = (n + threads - 1) // threads
vector_add((blocks,), (threads,), (a, b, c, n))  # (grid, block, args)
```

**Important RawKernel caveats:**
- Ignores array views/strides — `matrix.T` is treated as `matrix`. Handle strides yourself.
- Use `extern "C"` to prevent C++ name mangling.
- For complex numbers, include `<cupy/complex.cuh>`.
- Compiled binaries cached in `~/.cupy/kernel_cache`.

**CuPy dtype to CUDA type mapping:**

| CuPy dtype | CUDA type |
|-----------|-----------|
| `float16` | `half` |
| `float32` | `float` |
| `float64` | `double` |
| `int32` | `int` |
| `int64` | `long long` |
| `complex64` | `complex<float>` |
| `complex128` | `complex<double>` |

### RawModule — Large CUDA Codebases

For multi-kernel CUDA files or precompiled binaries:

```python
module = cp.RawModule(code=cuda_source)       # From source string
module = cp.RawModule(path='kernels.cu')      # From file
module = cp.RawModule(path='kernels.cubin')   # From precompiled

kernel = module.get_function('my_kernel')
kernel((blocks,), (threads,), (args...))
```

### JIT Kernel (cupyx.jit.rawkernel) — CUDA Kernels in Python Syntax

Write CUDA-style kernels using Python syntax instead of C++.

```python
@cupyx.jit.rawkernel()
def my_kernel(x, y, size):
    tid = cupyx.jit.grid(1)
    if tid < size:
        y[tid] = x[tid] * 2.0

my_kernel[blocks, threads](x, y, n)
```

Available JIT primitives:
- `cupyx.jit.threadIdx`, `blockIdx`, `blockDim`, `gridDim`
- `cupyx.jit.grid(ndim)`, `gridsize(ndim)`
- `cupyx.jit.syncthreads()`, `syncwarp()`
- `cupyx.jit.shared_memory(dtype, size)`
- `cupyx.jit.atomic_add/min/max/and/or/xor(array, index, value)`
- Warp shuffles: `shfl_sync`, `shfl_up_sync`, `shfl_down_sync`, `shfl_xor_sync`

**Limitation:** Does not work in Python REPL (needs source code access). Use from .py files.

---

## Kernel Fusion

Combine multiple element-wise operations into a single kernel launch — eliminates intermediate arrays and reduces kernel launch overhead.

```python
@cp.fuse()
def fused_op(x, y):
    return cp.sqrt((x - y) ** 2 + 1.0)

# This compiles into ONE kernel instead of multiple
result = fused_op(a, b)
```

**Limitation:** Only fuses elementwise and simple reduction operations. Does not support `matmul`, `reshape`, indexing, etc.

---

## Memory Management

### Memory Pools (Default Behavior)

CuPy uses memory pools by default — this is critical for performance. The pool caches freed GPU memory for reuse, avoiding expensive `cudaMalloc`/`cudaFree` calls and implicit synchronization.

**Key insight:** Memory is NOT freed to the OS when arrays go out of scope — it's returned to the pool. This is expected behavior (shows up in `nvidia-smi` as still-allocated).

```python
mempool = cp.get_default_memory_pool()
mempool.used_bytes()        # Currently allocated by CuPy arrays
mempool.total_bytes()       # Total held by pool (including free blocks)
mempool.free_all_blocks()   # Release all unused memory back to OS

pinned_mempool = cp.get_default_pinned_memory_pool()
pinned_mempool.free_all_blocks()
```

### Limiting GPU Memory

```python
mempool = cp.get_default_memory_pool()
with cp.cuda.Device(0):
    mempool.set_limit(size=4 * 1024**3)  # 4 GiB limit for GPU 0
```

Or via environment variable (set before `import cupy`):
```bash
export CUPY_GPU_MEMORY_LIMIT="50%"     # Percentage of total GPU memory
export CUPY_GPU_MEMORY_LIMIT="4294967296"  # Bytes
```

### Managed (Unified) Memory

Data auto-migrates between CPU and GPU. Useful when data doesn't fit in GPU memory.

```python
cp.cuda.set_allocator(cp.cuda.MemoryPool(cp.cuda.malloc_managed).malloc)
```

### Pinned Memory for Fast Transfers

```python
# High-level API
pinned_array = cupyx.empty_pinned((1000,), dtype=np.float32)
pinned_array = cupyx.zeros_pinned((1000,), dtype=np.float32)

# These are NumPy arrays backed by page-locked memory — transfers to GPU are faster
```

### Disabling Pools

```python
cp.cuda.set_allocator(None)                    # Disable device pool
cp.cuda.set_pinned_memory_allocator(None)      # Disable pinned pool
```

Must be done before any CuPy operations.

### Using RMM (RAPIDS Memory Manager)

When using CuPy alongside cuDF/RAPIDS, align on a single allocator:

```python
import rmm
from rmm.allocators.cupy import rmm_cupy_allocator

rmm.reinitialize(pool_allocator=True)
cp.cuda.set_allocator(rmm_cupy_allocator)
```

---

## Streams and Async Operations

Streams enable overlapping computation with data transfer and running multiple operations concurrently.

```python
stream = cp.cuda.Stream()

# Context manager style
with stream:
    d_data = cp.asarray(host_data)     # H→D transfer on this stream
    result = cp.sum(d_data)            # Kernel on this stream
# Operations enqueued but may not be complete here

stream.synchronize()  # Wait for all operations on this stream
```

### Multiple Streams for Overlap

```python
s1 = cp.cuda.Stream()
s2 = cp.cuda.Stream()

with s1:
    d_a = cp.asarray(data_a)
    result_a = cp.fft.fft(d_a)

with s2:
    d_b = cp.asarray(data_b)  # Overlaps with s1's FFT
    result_b = cp.fft.fft(d_b)

cp.cuda.Device().synchronize()  # Wait for all streams
```

### Events for Timing

```python
start = cp.cuda.Event()
end = cp.cuda.Event()

start.record()
# ... GPU operations ...
end.record()
end.synchronize()

elapsed_ms = cp.cuda.get_elapsed_time(start, end)
```

### Per-Thread Default Stream

```bash
export CUPY_CUDA_PER_THREAD_DEFAULT_STREAM=1
```

Enables per-thread default streams for better concurrency in multi-threaded applications.

---

## Multi-GPU

```python
# Set current device
cp.cuda.Device(0).use()

# Context manager
with cp.cuda.Device(1):
    x = cp.array([1, 2, 3])  # Allocated on GPU 1

# Check which device an array is on
print(x.device)  # Device 1
```

Cross-device operations may work via P2P (peer-to-peer) memory access if the GPU topology supports it. Use `cp.asarray()` to explicitly transfer arrays between devices.

### Per-Device Memory Limits

```python
mempool = cp.get_default_memory_pool()
with cp.cuda.Device(0):
    mempool.set_limit(size=4 * 1024**3)
with cp.cuda.Device(1):
    mempool.set_limit(size=4 * 1024**3)
```

---

## Performance Optimization

### Benchmarking (Critical First Step)

**Never use `time.perf_counter()` or `%timeit` for GPU code** — they measure only CPU time, not GPU execution time. CuPy operations are asynchronous.

```python
from cupyx.profiler import benchmark

result = benchmark(my_function, (arg1, arg2), n_repeat=100, n_warmup=10)
print(result)  # Shows CPU and GPU elapsed times with statistics
```

In IPython/Jupyter:
```python
%load_ext cupyx.profiler
%gpu_timeit my_function(args)
```

### One-Time Overheads

- **Context initialization:** First CuPy call may take 1-5 seconds (CUDA context creation). This is one-time.
- **Kernel JIT compilation:** First call to any operation triggers on-the-fly kernel compilation. Cached in `~/.cupy/kernel_cache`. Persist this directory across CI/CD runs.

### CUB and cuTENSOR Acceleration

```bash
# CuPy v11+ uses CUB by default
export CUPY_ACCELERATORS=cub          # CUB only (default)
export CUPY_ACCELERATORS=cub,cutensor # Both (requires cuTENSOR installed)
```

CUB accelerates reductions (`sum`, `prod`, `amin`, `amax`, `argmin`, `argmax`),
inclusive scans (`cumsum`), histograms, sparse matrix-vector multiply, and `ReductionKernel`.
The benefit depends on dtype, shape, axis, and hardware; benchmark the target operation.

cuTENSOR accelerates: binary elementwise ufuncs, reduction, tensor contraction.

### Key Optimization Strategies

1. **Prefer float32 over float64 when the numerical contract allows it.** Throughput differences
depend on GPU architecture; validate accuracy and benchmark the target device.

2. **Minimize CPU-GPU transfers.** Every `cp.asnumpy()` / `.get()` triggers synchronization and PCI-e transfer. Keep data on GPU as long as possible.

3. **Use kernel fusion.** `@cp.fuse()` combines multiple elementwise operations into one kernel, eliminating intermediate arrays.

4. **Batch operations.** Fewer large operations usually beat many small ones. Measure launch
overhead on the target system rather than relying on a fixed latency.

5. **Pre-allocate output arrays.** Use `out=` parameter in ufuncs to avoid repeated allocation:
   ```python
   cp.add(a, b, out=result)  # Writes into existing array
   ```

6. **Use in-place operations.** `a += b` avoids allocating a new array.

7. **Use streams** to overlap computation and data transfer.

8. **Profile with NVTX markers** for Nsight Systems analysis:
   ```python
   with cupyx.profiler.time_range('my_operation', color_id=0):
       result = heavy_computation()
   ```

### Decision Tree: Which Kernel Approach?

1. **Can be expressed as NumPy ops?** → Use built-in CuPy functions (fastest development, often best performance)
2. **Multiple chained elementwise ops?** → Use `@cp.fuse()`
3. **Custom elementwise with broadcasting?** → Use `ElementwiseKernel`
4. **Custom reduction?** → Use `ReductionKernel`
5. **Need full grid/block/shared memory control?** → Use `RawKernel` or `cupyx.jit.rawkernel`
6. **Large CUDA codebase?** → Use `RawModule`

---

## Interoperability

CuPy interoperates with other GPU libraries via the CUDA Array Interface and DLPack protocol — both enable zero-copy data sharing.

### NumPy

```python
# NumPy functions auto-dispatch to CuPy (NumPy >= 1.17)
import numpy as np
result = np.sum(cupy_array)  # Dispatches to CuPy, returns CuPy array
```

### Numba

```python
from numba import cuda

@cuda.jit
def numba_kernel(x, y):
    i = cuda.grid(1)
    if i < x.shape[0]:
        y[i] = x[i] * 2

# CuPy arrays pass directly to Numba kernels — zero copy
a = cp.arange(1000, dtype=cp.float32)
b = cp.zeros_like(a)
numba_kernel[4, 256](a, b)
```

### PyTorch

```python
import torch

# CuPy → PyTorch (zero copy via CUDA Array Interface)
cupy_array = cp.array([1.0, 2.0, 3.0], dtype=cp.float32)
torch_tensor = torch.as_tensor(cupy_array, device='cuda')

# PyTorch → CuPy (zero copy)
cupy_array = cp.asarray(torch_tensor)

# Via DLPack (also zero copy)
cupy_array = cp.from_dlpack(torch_tensor)
torch_tensor = torch.from_dlpack(cupy_array)
```

### cuDF

```python
import cudf

# cuDF → CuPy
arr = df.to_cupy()
arr = cp.asarray(df['column'])

# CuPy → cuDF
df = cudf.DataFrame(cupy_array)
s = cudf.Series(cupy_array)
```

### Raw Pointer Interop

```python
# Export pointer
ptr = cupy_array.data.ptr  # Raw device pointer as int

# Import foreign pointer
mem = cp.cuda.UnownedMemory(ptr, size_bytes, owner=owner_obj)
memptr = cp.cuda.MemoryPointer(mem, offset=0)
arr = cp.ndarray(shape, dtype, memptr=memptr)
```

---

## Key Differences from NumPy

These are the behavioral differences that can cause bugs if you're not aware of them.

1. **Reductions return 0-d arrays, not scalars.** `cp.sum(a)` returns a 0-d `cupy.ndarray`, not a Python float. This avoids implicit GPU-CPU synchronization. Use `.item()` if you need a scalar.

2. **Out-of-bounds indexing wraps silently.** NumPy raises `IndexError`; CuPy wraps around without error.

3. **Duplicate indices in assignment are undefined.** `a[[0, 0]] = [1, 2]` — NumPy stores the last value; CuPy stores an undefined value (GPU race condition).

4. **Float-to-integer casts differ at edges.** Casting negative float to unsigned int or infinity to int gives different results than NumPy.

5. **No string/object dtypes.** CuPy only supports numeric types. No structured arrays with string fields.

6. **CuPy ufuncs require CuPy arrays.** Unlike NumPy ufuncs, CuPy ufuncs don't accept lists or NumPy arrays — convert first.

7. **Random seed arrays are hashed.** Array seeds produce less entropy than NumPy's approach.

---

## Common Pitfalls

1. **Measuring with CPU timers.** GPU operations are async. `time.perf_counter()` measures only the time to *enqueue* operations, not execute them. Always use `cupyx.profiler.benchmark()`.

2. **Unnecessary round-trips.** Every `cp.asnumpy()` / `.get()` syncs the GPU and copies data across PCI-e. Restructure code to keep data on GPU.

3. **"Memory leak" from pools.** The memory pool caches freed blocks. `nvidia-smi` shows them as allocated. Use `mempool.free_all_blocks()` to release.

4. **First-call latency.** CUDA context init + kernel JIT compilation. Warm up before benchmarking.

5. **Mixing devices.** Using an array from GPU 0 on GPU 1 without explicit transfer can fail or be slow.

6. **RawKernel ignoring views.** Transposed or sliced arrays passed to RawKernel are treated as the original contiguous layout. You must handle strides manually.

7. **Forgetting `synchronize()` before reading results.** If you pass data back to CPU or use it in non-CuPy code, ensure the GPU is done first.

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `CUPY_ACCELERATORS` | Backend list: `cub`, `cutensor` (default: `cub` for v11+) |
| `CUPY_CACHE_DIR` | Kernel cache directory (default: `~/.cupy/kernel_cache`) |
| `CUPY_GPU_MEMORY_LIMIT` | GPU memory limit (bytes or `"50%"`) |
| `CUPY_CACHE_SAVE_CUDA_SOURCE` | Set `1` to dump kernel source for profiling |
| `CUPY_CUDA_PER_THREAD_DEFAULT_STREAM` | Set `1` for per-thread default streams |

### `references/cuspatial.md`

# cuSpatial Reference

cuSpatial is a GPU-accelerated GIS library that provides spatial indexing, spatial joins, distance calculations, trajectory analysis, and GeoPandas-compatible geometry types. It integrates with cuDF for tabular data and GeoPandas for geometry interoperability, enabling you to accelerate geospatial workflows by moving the compute-heavy parts to GPU.

> **Full documentation:** https://docs.rapids.ai/api/cuspatial/stable/

> **⚠️ Project status: archived.** cuSpatial development is paused and the GitHub repository was archived (read-only) on July 28, 2025. The **final release is v25.04** — no packages are published for RAPIDS v25.06 or later (see [RSN 45](https://docs.rapids.ai/notices/rsn0045/)). The package still installs and works, but it pins RAPIDS 25.04-era dependencies (e.g., `cudf-cu12==25.4.*`), so it cannot be combined with current RAPIDS releases in the same environment. RAPIDS names no official successor; for actively maintained geospatial work use GeoPandas/Shapely (CPU), and reserve cuSpatial for existing pipelines that can stay on the 25.04 dependency stack.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [GeoPandas Interoperability](#geopandas-interoperability)
3. [GeoSeries and GeoDataFrame](#geoseries-and-geodataframe)
4. [Spatial Joins — Point in Polygon](#spatial-joins--point-in-polygon)
5. [Spatial Indexing — Quadtree](#spatial-indexing--quadtree)
6. [Distance Functions](#distance-functions)
7. [Nearest Points](#nearest-points)
8. [Bounding Boxes](#bounding-boxes)
9. [Projections](#projections)
10. [Spatial Filtering](#spatial-filtering)
11. [Trajectory Analysis](#trajectory-analysis)
12. [Binary Predicates](#binary-predicates)
13. [Performance Tips](#performance-tips)
14. [Common Pitfalls](#common-pitfalls)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add --extra-index-url=https://pypi.nvidia.com "cuspatial-cu12==25.4.*"   # Final 25.04 release
```

The `--extra-index-url=https://pypi.nvidia.com` index is **required** here — the `cuspatial-cu12` entry on PyPI itself is only a stub sdist; the real wheels live on pypi.nvidia.com. There are no CUDA 13 (`-cu13`) packages — the project was archived before CUDA 13 wheels were introduced. Installing cuSpatial pulls in `cudf-cu12==25.4.*` and related 25.04 pins.

Verify:
```python
import cuspatial
from shapely.geometry import Point
gs = cuspatial.GeoSeries([Point(0, 0), Point(1, 1)])
print(gs)
```

---

## GeoPandas Interoperability

cuSpatial's primary on-ramp is converting from GeoPandas. Any `GeoSeries` or `GeoDataFrame` can be moved to GPU:

```python
import geopandas as gpd
import cuspatial

# GeoPandas -> cuSpatial (CPU -> GPU)
gdf = gpd.read_file("my_shapefile.shp")
cu_gdf = cuspatial.from_geopandas(gdf)

# cuSpatial -> GeoPandas (GPU -> CPU)
gdf_back = cu_gdf.to_geopandas()
```

You can also construct a `GeoDataFrame` directly:
```python
cu_gdf = cuspatial.GeoDataFrame(geopandas_dataframe)
```

---

## GeoSeries and GeoDataFrame

`cuspatial.GeoSeries` is a GPU-backed series that holds shapely-compatible geometry objects (Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon).

### Creating GeoSeries from Shapely objects

```python
from shapely.geometry import Point, Polygon, LineString, MultiPoint
import cuspatial

points = cuspatial.GeoSeries([Point(0, 0), Point(1, 1), Point(2, 2)])
polys = cuspatial.GeoSeries([
    Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
    Polygon([(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)])
])
```

### Creating GeoSeries from coordinate arrays (faster for large data)

```python
import cudf

# Points from interleaved xy coordinates
xy = cudf.Series([0.0, 0.0, 1.0, 1.0, 2.0, 2.0])  # x0, y0, x1, y1, ...
points = cuspatial.GeoSeries.from_points_xy(xy)

# MultiPoints from interleaved xy + geometry offsets
multipoints = cuspatial.GeoSeries.from_multipoints_xy(
    multipoints_xy=cudf.Series([0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0]),
    geometry_offset=cudf.Series([0, 2, 4])  # 2 multipoints, each with 2 points
)
```

### GeoSeries properties

```python
gs = cuspatial.GeoSeries([Point(0, 0), Point(1, 1)])
gs.points.xy        # Access raw interleaved coordinates
gs.sizes             # Number of points per geometry
gs.iloc[0]           # Access single geometry
```

### GeoDataFrame

```python
cu_gdf = cuspatial.GeoDataFrame({
    "geometry": cuspatial.GeoSeries([Point(0, 0), Point(1, 1)]),
    "value": cudf.Series([10, 20])
})
```

---

## Spatial Joins — Point in Polygon

The most common operation: test which points are inside which polygons.

### Simple point-in-polygon

```python
from shapely.geometry import Point, Polygon
import cuspatial

points = cuspatial.GeoSeries([Point(0, 0), Point(-8, -8), Point(6, 6)])
polygons = cuspatial.GeoSeries([
    Polygon([(-10, -10), (5, -10), (5, 5), (-10, 5), (-10, -10)]),
    Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
])

result = cuspatial.point_in_polygon(points, polygons)
# Returns a DataFrame of booleans: rows=points, columns=polygons
#   polygon_0  polygon_1
# 0     True      True     <- (0,0) is in both
# 1     True     False     <- (-8,-8) is in first only
# 2    False      True     <- (6,6) is in second only
```

### Quadtree-accelerated point-in-polygon (for large datasets)

For millions of points, use the quadtree pipeline — it dramatically reduces the number of point-polygon tests:

```python
import cuspatial
import cudf

# 1. Build quadtree on points
key_to_point, quadtree = cuspatial.quadtree_on_points(
    points,              # GeoSeries of points
    x_min, x_max,        # Bounding box
    y_min, y_max,
    scale=scale,         # Usually (max_extent) / (2^max_depth)
    max_depth=7,         # Max tree depth (< 16)
    max_size=125         # Max points per leaf before splitting
)

# 2. Compute polygon bounding boxes
poly_bboxes = cuspatial.polygon_bounding_boxes(polygons)

# 3. Join quadtree with bounding boxes
intersections = cuspatial.join_quadtree_and_bounding_boxes(
    quadtree, poly_bboxes, x_min, x_max, y_min, y_max, scale, max_depth
)

# 4. Test point-in-polygon only for relevant quadrants
result = cuspatial.quadtree_point_in_polygon(
    intersections, quadtree, key_to_point, points, polygons
)
# Returns DataFrame with polygon_index and point_index columns
```

---

## Spatial Indexing — Quadtree

Build a quadtree spatial index on a set of points. This is the foundation for scalable spatial joins.

```python
key_to_point, quadtree = cuspatial.quadtree_on_points(
    points,            # GeoSeries of points
    x_min, x_max,      # Area of interest bounding box
    y_min, y_max,
    scale,             # Grid resolution
    max_depth,         # Maximum tree depth (must be < 16)
    max_size           # Max points per node before splitting
)

# quadtree is a DataFrame with columns:
#   key, level, is_internal_node, length, offset
# key_to_point maps sorted quadtree indices back to original point indices
```

**Choosing scale:** `scale = max(x_max - x_min, y_max - y_min) / (2 ** max_depth)`

---

## Distance Functions

### Haversine distance (great-circle, for lat/lon coordinates)

```python
p1 = cuspatial.GeoSeries([Point(lon1, lat1), Point(lon2, lat2)])
p2 = cuspatial.GeoSeries([Point(lon3, lat3), Point(lon4, lat4)])

distances_km = cuspatial.haversine_distance(p1, p2)
# Returns cudf.Series of distances in kilometers
```

### Pairwise point distance (Euclidean)

```python
from shapely.geometry import Point, MultiPoint

p1 = cuspatial.GeoSeries([Point(0, 0), Point(1, 0)])
p2 = cuspatial.GeoSeries([Point(3, 4), Point(4, 3)])
dists = cuspatial.pairwise_point_distance(p1, p2)  # [5.0, 4.243]
```

### Pairwise linestring distance

```python
from shapely.geometry import LineString

ls1 = cuspatial.GeoSeries([LineString([(0, 0), (1, 1)])])
ls2 = cuspatial.GeoSeries([LineString([(2, 0), (3, 1)])])
dists = cuspatial.pairwise_linestring_distance(ls1, ls2)
```

### Point-to-linestring distance

```python
pts = cuspatial.GeoSeries([Point(0, 0)])
lines = cuspatial.GeoSeries([LineString([(1, 0), (0, 1)])])
dists = cuspatial.pairwise_point_linestring_distance(pts, lines)
```

### Directed Hausdorff distance

```python
from shapely.geometry import MultiPoint

spaces = cuspatial.GeoSeries([
    MultiPoint([(0, 0), (1, 0)]),
    MultiPoint([(0, 1), (0, 2)])
])
hausdorff = cuspatial.directed_hausdorff_distance(spaces)
# Returns DataFrame: hausdorff[i][j] = directed Hausdorff from space i to j
```

---

## Nearest Points

Find the nearest point on a linestring to each point:

```python
result = cuspatial.pairwise_point_linestring_nearest_points(points, linestrings)
# Returns GeoDataFrame with:
#   point_geometry_id, linestring_geometry_id, segment_id, geometry (nearest point)
```

For quadtree-accelerated nearest linestring lookup:

```python
result = cuspatial.quadtree_point_to_nearest_linestring(
    linestring_quad_pairs, quadtree, key_to_point, points, linestrings
)
# Returns DataFrame with: point_index, linestring_index, distance
```

---

## Bounding Boxes

```python
# Polygon bounding boxes
poly_bboxes = cuspatial.polygon_bounding_boxes(polygons)
# Returns DataFrame: minx, miny, maxx, maxy

# Linestring bounding boxes (with expansion radius)
line_bboxes = cuspatial.linestring_bounding_boxes(linestrings, expansion_radius=0.5)
```

---

## Projections

### Sinusoidal projection (lon/lat to Cartesian km)

For approximately converting geographic coordinates to Cartesian coordinates when all points are near a reference origin:

```python
origin_lon, origin_lat = -73.9857, 40.7484  # e.g., NYC
lonlat_points = cuspatial.GeoSeries([Point(-73.98, 40.75), Point(-73.99, 40.74)])

xy_km = cuspatial.sinusoidal_projection(origin_lon, origin_lat, lonlat_points)
# Returns GeoSeries of projected (x, y) points in kilometers
```

---

## Spatial Filtering

Filter points within a rectangular window:

```python
filtered = cuspatial.points_in_spatial_window(
    points,
    min_x=-10, max_x=10,
    min_y=-10, max_y=10
)
# Returns GeoSeries of only the points inside the window
```

---

## Trajectory Analysis

Identify, reconstruct, and analyze trajectories from timestamped point data (e.g., vehicle GPS traces).

### Derive trajectories

```python
objects, traj_offsets = cuspatial.derive_trajectories(
    object_ids=[0, 1, 0, 1],     # e.g., vehicle IDs
    points=cuspatial.GeoSeries([Point(0,0), Point(0,0), Point(1,1), Point(1,1)]),
    timestamps=[0, 0, 10000, 10000]
)
# objects: DataFrame sorted by (object_id, timestamp) with x, y, timestamp
# traj_offsets: Series of offsets marking each trajectory's start
```

### Distances and speeds

```python
dist_speed = cuspatial.trajectory_distances_and_speeds(
    len(traj_offsets),
    objects['object_id'],
    objects_points,        # GeoSeries
    objects['timestamp']
)
# Returns DataFrame with 'distance' (km) and 'speed' (m/s) per trajectory
```

### Trajectory bounding boxes

```python
traj_bboxes = cuspatial.trajectory_bounding_boxes(
    len(traj_offsets),
    objects['object_id'],
    objects_points
)
# Returns DataFrame: x_min, y_min, x_max, y_max per trajectory
```

---

## Binary Predicates

`GeoSeries` supports GeoPandas-compatible binary spatial predicates — all GPU-accelerated:

```python
# All return cudf.Series of booleans
polys.contains(points)            # Is each point inside the polygon?
polys.contains_properly(points)   # Strictly interior (not on boundary)?
geom_a.covers(geom_b)            # Does A cover B?
geom_a.crosses(geom_b)           # Do geometries cross?
geom_a.disjoint(geom_b)          # Are they disjoint?
geom_a.distance(geom_b)          # Pairwise distances
geom_a.geom_equals(geom_b)       # Are they geometrically equal?
geom_a.intersects(geom_b)        # Do they intersect?
geom_a.overlaps(geom_b)          # Do they overlap?
geom_a.touches(geom_b)           # Do they touch?
geom_a.within(geom_b)            # Is A within B?
```

The `contains` and `contains_properly` methods support an `allpairs=True` mode that returns all point-polygon containment pairs (useful when you have M points and N polygons and want all matches):

```python
result = polygons.contains(points, allpairs=True)
# Returns DataFrame with point_indices and polygon_indices columns
```

---

## Performance Tips

1. **Use the quadtree pipeline for large datasets.** Brute-force `point_in_polygon` tests every point against every polygon. The quadtree pipeline (`quadtree_on_points` + `join_quadtree_and_bounding_boxes` + `quadtree_point_in_polygon`) pre-filters using spatial indexing and can be orders of magnitude faster for millions of points/polygons.

2. **Build GeoSeries from coordinate arrays, not shapely objects.** `GeoSeries.from_points_xy()` with cuDF Series is much faster than constructing from a list of shapely Point objects, which requires serializing each geometry.

3. **Keep data on GPU.** cuSpatial integrates with cuDF — load data with `cudf.read_csv()` or `cudf.read_parquet()`, then construct GeoSeries from the coordinate columns. Avoid round-tripping through GeoPandas for large datasets.

4. **Use `allpairs=True` for many-to-many spatial joins.** If you need to find all point-polygon pairs (not just row-wise), use `contains(points, allpairs=True)` instead of expanding the data yourself.

5. **Combine with cuDF for full pipelines.** cuSpatial returns cuDF DataFrames/Series, so you can chain spatial operations with cuDF filtering, groupby, and joins without leaving the GPU.

---

## Common Pitfalls

- **Polygons must be closed.** The first and last coordinate of each polygon ring must be identical. Shapely handles this automatically, but if constructing from raw coordinates, ensure closure.

- **GeoSeries must be single-type for some operations.** Functions like `pairwise_point_distance` require the series to contain only points or only multipoints — you can't mix types in the same series.

- **Quadtree max_depth < 16.** Morton codes are represented as uint32, so max_depth must be less than 16.

- **Haversine expects lon/lat, not lat/lon.** cuSpatial follows the (longitude, latitude) convention, matching shapely/GeoJSON — not the (lat, lon) convention used by some mapping APIs.

- **No CRS transformations.** cuSpatial doesn't handle coordinate reference system conversions. Project your data to the correct CRS using GeoPandas/pyproj before moving to GPU.

### `references/cuvs.md`

# cuVS Reference

cuVS is NVIDIA's GPU-accelerated library for exact and approximate nearest-neighbor search, part
of the RAPIDS ecosystem. It provides CAGRA, IVF-Flat, IVF-PQ, brute-force, and CPU-serving
interoperability. Compare equal metrics and exactness requirements, validate ANN recall, and
benchmark build, search, transfer, and serialization costs separately.

> **Full documentation:** https://docs.rapids.ai/api/cuvs/stable/

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [When to Use cuVS](#when-to-use-cuvs)
3. [Index Selection Guide](#index-selection-guide)
4. [CAGRA — Graph-Based Index](#cagra)
5. [IVF-Flat — Inverted File Index](#ivf-flat)
6. [IVF-PQ — Compressed Inverted File Index](#ivf-pq)
7. [Brute Force — Exact Search](#brute-force)
8. [HNSW — CPU Search from GPU Index](#hnsw)
9. [Distance Metrics](#distance-metrics)
10. [Filtering](#filtering)
11. [Multi-GPU](#multi-gpu)
12. [Memory and Performance](#memory-and-performance)
13. [Interoperability](#interoperability)
14. [Common Patterns](#common-patterns)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add --extra-index-url=https://pypi.nvidia.com "cuvs-cu12==26.6.*"   # For CUDA 12.x
uv add --extra-index-url=https://pypi.nvidia.com "cuvs-cu13==26.6.*"   # For CUDA 13.x
```

cuVS wheels (including the companion `libcuvs` wheel) are also published directly to PyPI, so the extra index is optional — but the official cuVS docs still show it and it does no harm.

**Platform:** Linux and WSL2 only (no native macOS or Windows).
**Requires:** NVIDIA GPU with CUDA 12.x or 13.x support, Python 3.11+, CuPy recommended for GPU arrays.

Verify:
```python
from cuvs.neighbors import cagra
import cupy as cp

dataset = cp.random.rand(1000, 128, dtype=cp.float32)
index = cagra.build(cagra.IndexParams(), dataset)
print("cuVS working — built CAGRA index")
```

---

## When to Use cuVS

cuVS is the right tool when the user needs:
- **Nearest neighbor search** on high-dimensional vectors (embeddings)
- **Similarity search** for RAG, recommender systems, image/text/audio retrieval
- **k-NN graph construction** for clustering or visualization pipelines
- **Vector database backends** — cuVS powers search in Milvus, Lucene, Kinetica, and Faiss GPU
- **Replacing Faiss, Annoy, ScaNN, or sklearn NearestNeighbors** with GPU acceleration

cuVS is NOT the right tool for:
- General machine learning (use cuML instead)
- Small or low-dimensional datasets where build, transfer, or launch overhead dominates in a
  representative benchmark
- CPU-only environments with no GPU available

---

## Index Selection Guide

| Index | Best For | Build Speed | Search Speed | Memory | Accuracy |
|-------|----------|-------------|--------------|--------|----------|
| **CAGRA** | Strong first ANN candidate | Fast | Fast | Medium | Tunable |
| **IVF-Flat** | High-recall ANN without vector compression | Medium | Fast | High (stores full vectors) | Tunable |
| **IVF-PQ** | Large datasets that don't fit in GPU memory | Medium | Fast | Low (compressed) | Good |
| **Brute Force** | Small datasets or ground truth | N/A | Slow at scale | High | Exact |
| **HNSW** | CPU-side serving from GPU-built index | Slow | Fast (CPU) | Medium | High |

Benchmark CAGRA as the first ANN candidate, then compare IVF-PQ when memory is tight and IVF-Flat
when avoiding vector compression matters. Use brute force for exact search and recall ground truth.
Choose build and search parameters from measured latency, throughput, memory, and recall targets.

---

## CAGRA

CAGRA (CUDA Accelerated Graph-based) is a graph-based ANN index optimized for GPU. It's the fastest option for most workloads.

### Build

```python
import cupy as cp
from cuvs.neighbors import cagra

n_samples = 1_000_000
n_features = 128
dataset = cp.random.rand(n_samples, n_features, dtype=cp.float32)

# Default parameters work well for most cases
index_params = cagra.IndexParams(
    metric="sqeuclidean",             # "sqeuclidean", "inner_product", "cosine"
    intermediate_graph_degree=128,     # Higher = better quality, slower build
    graph_degree=64,                   # Final graph degree (lower = less memory)
    build_algo="ivf_pq",              # "ivf_pq", "nn_descent", "iterative_cagra_search", or "ace"
)

index = cagra.build(index_params, dataset)
```

### Search

```python
from cuvs.common import Resources

queries = cp.random.rand(1000, n_features, dtype=cp.float32)

search_params = cagra.SearchParams(
    itopk_size=64,       # Intermediate top-k (higher = more accurate, slower)
    search_width=1,      # Starting nodes per iteration
    max_iterations=0,    # 0 = auto
    algo="auto",         # "auto", "single_cta", "multi_cta", "multi_kernel"
)

resources = Resources()
distances, neighbors = cagra.search(
    search_params, index, queries, k=10, resources=resources
)
resources.sync()

# distances: shape (1000, 10) — squared Euclidean distances
# neighbors: shape (1000, 10) — indices into original dataset
```

### Save / Load

```python
cagra.save("my_index.cagra", index)
loaded_index = cagra.load("my_index.cagra")
```

### Extend

```python
new_data = cp.random.rand(10_000, n_features, dtype=cp.float32)
extended_index = cagra.extend(cagra.ExtendParams(), index, new_data)
```

### With Compression (for large datasets)

```python
from cuvs.neighbors.cagra import CompressionParams

index_params = cagra.IndexParams(
    compression=CompressionParams(
        pq_bits=8,
        pq_dim=64,
    )
)
index = cagra.build(index_params, dataset)
```

---

## IVF-Flat

IVF-Flat partitions the dataset into clusters (inverted file) and stores full vectors. Higher accuracy than IVF-PQ but uses more memory.

### Build

```python
from cuvs.neighbors import ivf_flat

build_params = ivf_flat.IndexParams(
    n_lists=1024,                    # Number of clusters (sqrt(n_samples) is a good start)
    metric="sqeuclidean",            # "sqeuclidean", "euclidean", "inner_product", "cosine"
    kmeans_trainset_fraction=0.5,    # Fraction of data used for k-means training
    kmeans_n_iters=20,               # K-means iterations
    add_data_on_build=True,          # Add vectors during build (vs. extend later)
)

index = ivf_flat.build(build_params, dataset)
```

### Search

```python
search_params = ivf_flat.SearchParams(
    n_probes=50,    # Clusters to search (higher = more accurate, slower)
)

distances, neighbors = ivf_flat.search(
    search_params, index, queries, k=10
)
```

### Save / Load / Extend

```python
ivf_flat.save("my_index.ivf_flat", index)
loaded_index = ivf_flat.load("my_index.ivf_flat")

# Extend with new data
import numpy as np
new_vectors = cp.random.rand(5000, n_features, dtype=cp.float32)
new_indices = cp.arange(n_samples, n_samples + 5000, dtype=cp.int64)
ivf_flat.extend(index, new_vectors, new_indices)
```

---

## IVF-PQ

IVF-PQ compresses vectors using product quantization, dramatically reducing memory usage. Best for large datasets that don't fit in GPU memory with full vectors.

### Build

```python
from cuvs.neighbors import ivf_pq

build_params = ivf_pq.IndexParams(
    n_lists=1024,                # Number of clusters
    metric="sqeuclidean",        # "sqeuclidean", "inner_product"
    pq_bits=8,                   # Bits per subquantizer (4 or 8)
    pq_dim=0,                    # PQ dimensions (0 = auto, typically dim/4)
    codebook_kind="subspace",    # "subspace" or "cluster"
    kmeans_n_iters=20,
    add_data_on_build=True,
)

index = ivf_pq.build(build_params, dataset)
```

### Search

```python
search_params = ivf_pq.SearchParams(
    n_probes=50,                     # Clusters to search
    lut_dtype="float32",             # Look-up table precision
    internal_distance_dtype="float32",
)

distances, neighbors = ivf_pq.search(
    search_params, index, queries, k=10
)
```

### Save / Load / Extend

```python
ivf_pq.save("my_index.ivf_pq", index)
loaded_index = ivf_pq.load("my_index.ivf_pq")

# Extend
new_vectors = cp.random.rand(5000, n_features, dtype=cp.float32)
new_indices = cp.arange(n_samples, n_samples + 5000, dtype=cp.int64)
ivf_pq.extend(index, new_vectors, new_indices)
```

---

## Brute Force

Exact k-NN search — computes all distances. Use for small datasets (< 50K vectors) or generating ground truth to evaluate approximate indexes.

```python
from cuvs.neighbors import brute_force

# Build (just stores the dataset)
index = brute_force.build(dataset, metric="sqeuclidean")

# Search
distances, neighbors = brute_force.search(index, queries, k=10)

# Save / Load
brute_force.save("bf_index.bin", index)
loaded = brute_force.load("bf_index.bin")
```

---

## HNSW

cuVS provides an HNSW implementation for CPU-side search. The typical workflow is: build a CAGRA index on GPU, convert it to HNSW for CPU serving. This lets you leverage GPU speed for building while serving from CPU (useful when GPU isn't available at query time).

```python
from cuvs.neighbors import cagra, hnsw
import numpy as np

# Build CAGRA on GPU
dataset_gpu = cp.random.rand(100_000, 128, dtype=cp.float32)
cagra_index = cagra.build(cagra.IndexParams(), dataset_gpu)

# Convert to HNSW for CPU search
hnsw_index = hnsw.from_cagra(hnsw.IndexParams(), cagra_index)

# Search on CPU with numpy queries
queries_cpu = np.random.rand(100, 128).astype(np.float32)
search_params = hnsw.SearchParams(
    ef=200,           # Search depth (higher = more accurate, slower)
    num_threads=0,    # 0 = auto (uses all available threads)
)
distances, neighbors = hnsw.search(search_params, hnsw_index, queries_cpu, k=10)

# Save / Load
hnsw.save("my_index.hnsw", hnsw_index)
loaded = hnsw.load(hnsw.IndexParams(), "my_index.hnsw", dim=128,
                    dtype=np.float32, metric="sqeuclidean")
```

### Extendable HNSW

To add vectors after building, use `hierarchy="cpu"`:

```python
hnsw_index = hnsw.from_cagra(hnsw.IndexParams(hierarchy="cpu"), cagra_index)

new_data = np.random.rand(5000, 128).astype(np.float32)
hnsw.extend(hnsw.ExtendParams(), hnsw_index, new_data)
```

---

## Distance Metrics

| Metric | String | Notes |
|--------|--------|-------|
| Squared Euclidean | `"sqeuclidean"` | Default. Fastest — avoids sqrt. |
| Euclidean | `"euclidean"` | L2 distance |
| Inner Product | `"inner_product"` | For normalized embeddings (cosine similarity via dot product) |
| Cosine | `"cosine"` | Supported by CAGRA and IVF-Flat |

For cosine similarity with IVF-PQ, normalize vectors to unit length and use `"inner_product"`.

---

## Filtering

cuVS supports pre-filtering search results using bitmaps or bitsets to exclude specific vectors.

```python
from cuvs.neighbors import brute_force
import cupy as cp

# Bitset filter: exclude specific indices from ALL queries
# 1 = excluded, 0 = included
n_samples = 100_000
bitset = cp.zeros(n_samples, dtype=cp.uint8)
bitset[0:1000] = 1  # Exclude first 1000 vectors

distances, neighbors = brute_force.search(
    index, queries, k=10, prefilter=bitset
)
```

CAGRA also supports filtering via the `filter` parameter in `cagra.search()`.

---

## Multi-GPU

For datasets too large for a single GPU, use the multi-GPU API:

```python
from cuvs.neighbors.mg import cagra as mg_cagra

# Build across all available GPUs
build_params = mg_cagra.IndexParams(
    intermediate_graph_degree=64,
    graph_degree=32,
)
index = mg_cagra.build(build_params, dataset)

# Search across GPUs
search_params = mg_cagra.SearchParams()
distances, neighbors = mg_cagra.search(search_params, index, queries, k=10)
```

Multi-GPU is also available for IVF-Flat and IVF-PQ via `cuvs.neighbors.mg`.

---

## Memory and Performance

### Supported Data Types

All index types support: `float32`, `float16`, `int8`, `uint8`.

Using `float16` halves memory and can speed up both build and search when full float32 precision isn't needed (common for embeddings).

### Performance Tips

1. **Use CuPy arrays as input.** NumPy arrays work but trigger a CPU-to-GPU transfer. If your vectors are already on GPU (from a model or pipeline), pass them directly.

2. **Tune search parameters, not just build parameters.** The biggest accuracy/speed tradeoff is at search time:
   - CAGRA: increase `itopk_size` (default 64)
   - IVF-Flat/IVF-PQ: increase `n_probes` (default 20)
   - HNSW: increase `ef` (default 200)

3. **Evaluate reduced precision, do not assume it is free.** If the chosen index supports float16,
compare recall/ranking metrics and end-to-end performance with float32 before changing storage.

4. **n_lists tuning for IVF indexes.** A good starting point is `sqrt(n_samples)`. Too few lists = slow search, too many = poor recall.

5. **Batch queries.** GPU throughput scales with batch size. Searching 1000 queries at once is far more efficient than 1000 individual searches.

6. **Reuse the Resources handle.** Create one `Resources()` object and pass it to all build/search calls — it manages CUDA streams and memory.

### Memory Estimates

- **Brute force:** `n_samples * dim * dtype_size` (full dataset)
- **IVF-Flat:** Similar to brute force + cluster overhead
- **IVF-PQ:** `n_samples * pq_dim * pq_bits / 8` (heavily compressed)
- **CAGRA:** `n_samples * (dim * dtype_size + graph_degree * 4)` (dataset + graph)

---

## Interoperability

- **CuPy:** Native input — zero-copy via `__cuda_array_interface__`
- **NumPy:** Accepted as input (auto-transferred to GPU for GPU indexes, used directly for HNSW)
- **PyTorch / TensorFlow:** Tensors accepted via CUDA array interface — no copy needed
- **cuDF:** Convert columns to CuPy with `.values` before passing to cuVS
- **Faiss:** cuVS powers Faiss GPU under the hood; for direct use, cuVS gives more control
- **Vector databases:** cuVS is integrated into Milvus, Lucene, and Kinetica

### End-to-End RAG Pipeline Example

```python
import cupy as cp
from cuvs.neighbors import cagra

# Assume embeddings come from a model (e.g., sentence-transformers on GPU)
document_embeddings = cp.array(embeddings, dtype=cp.float32)  # (n_docs, 768)

# Build index
index_params = cagra.IndexParams(metric="inner_product")
index = cagra.build(index_params, document_embeddings)
cagra.save("doc_index.cagra", index)

# At query time
query_embedding = cp.array(encode("user question"), dtype=cp.float32).reshape(1, -1)
search_params = cagra.SearchParams(itopk_size=128)
distances, neighbors = cagra.search(search_params, index, query_embedding, k=20)

# neighbors[0] contains the indices of the top-20 most similar documents
top_doc_ids = neighbors[0].get()  # Transfer to CPU
```

---

## Common Patterns

### Pattern 1: Quick ANN Search (CAGRA)

```python
import cupy as cp
from cuvs.neighbors import cagra

dataset = cp.random.rand(500_000, 128, dtype=cp.float32)
queries = cp.random.rand(1000, 128, dtype=cp.float32)

index = cagra.build(cagra.IndexParams(), dataset)
distances, neighbors = cagra.search(cagra.SearchParams(), index, queries, k=10)
```

### Pattern 2: Memory-Efficient Search (IVF-PQ)

```python
import cupy as cp
from cuvs.neighbors import ivf_pq

dataset = cp.random.rand(10_000_000, 256, dtype=cp.float32)

# PQ compresses vectors — uses ~32x less memory than brute force
params = ivf_pq.IndexParams(n_lists=4096, pq_bits=8, pq_dim=64)
index = ivf_pq.build(params, dataset)

search_params = ivf_pq.SearchParams(n_probes=100)
distances, neighbors = ivf_pq.search(search_params, index, queries, k=10)
```

### Pattern 3: GPU Build, CPU Serve (CAGRA → HNSW)

```python
import cupy as cp
import numpy as np
from cuvs.neighbors import cagra, hnsw

# Build on GPU (fast)
dataset = cp.random.rand(1_000_000, 128, dtype=cp.float32)
gpu_index = cagra.build(cagra.IndexParams(), dataset)

# Convert to HNSW for CPU serving
cpu_index = hnsw.from_cagra(hnsw.IndexParams(), gpu_index)
hnsw.save("serving_index.hnsw", cpu_index)

# At serving time (no GPU needed)
loaded = hnsw.load(hnsw.IndexParams(), "serving_index.hnsw",
                    dim=128, dtype=np.float32)
queries = np.random.rand(100, 128).astype(np.float32)
distances, neighbors = hnsw.search(
    hnsw.SearchParams(ef=200), loaded, queries, k=10
)
```

### Pattern 4: Validate with Brute Force

```python
from cuvs.neighbors import brute_force, cagra

# Ground truth
bf_index = brute_force.build(dataset)
gt_distances, gt_neighbors = brute_force.search(bf_index, queries, k=10)

# Approximate
cagra_index = cagra.build(cagra.IndexParams(), dataset)
approx_distances, approx_neighbors = cagra.search(
    cagra.SearchParams(), cagra_index, queries, k=10
)

# Compute recall
recall = sum(
    len(set(gt_neighbors[i].get()) & set(approx_neighbors[i].get())) / 10
    for i in range(len(queries))
) / len(queries)
print(f"Recall@10: {recall:.4f}")
```

### Pattern 5: Cosine Similarity Search

```python
import cupy as cp
from cuvs.neighbors import cagra

# Normalize embeddings to unit length
embeddings = cp.random.rand(100_000, 768, dtype=cp.float32)
norms = cp.linalg.norm(embeddings, axis=1, keepdims=True)
embeddings_normalized = embeddings / norms

# Use inner_product on normalized vectors = cosine similarity
index = cagra.build(
    cagra.IndexParams(metric="inner_product"),
    embeddings_normalized,
)

query = cp.random.rand(1, 768, dtype=cp.float32)
query_normalized = query / cp.linalg.norm(query)

distances, neighbors = cagra.search(
    cagra.SearchParams(), index, query_normalized, k=10
)
```

---

## Beyond Neighbors: Clustering, Distance, and Preprocessing

cuVS also provides GPU-accelerated clustering, pairwise distance, and quantization — useful building blocks in vector search pipelines.

### K-Means Clustering

```python
import cupy as cp
from cuvs.cluster.kmeans import fit, predict, KMeansParams

X = cp.random.rand(100_000, 128, dtype=cp.float32)

params = KMeansParams(
    n_clusters=256,
    init_method="KMeansPlusPlus",   # or "Random", "Array"
    max_iter=300,
    tol=1e-4,
)
centroids, inertia, n_iter = fit(params, X)
labels, inertia = predict(params, X, centroids)
```

For datasets larger than GPU memory, pass NumPy arrays with `streaming_batch_size`:

```python
import numpy as np
from cuvs.cluster.kmeans import fit, KMeansParams

X_host = np.random.rand(10_000_000, 128).astype(np.float32)
params = KMeansParams(n_clusters=1000, streaming_batch_size=1_000_000)
centroids, inertia, n_iter = fit(params, X_host)
```

### Pairwise Distance

```python
from cuvs.distance import pairwise_distance

# Supports: euclidean, l2, l1, inner_product, cosine, chebyshev,
# canberra, hellinger, jensenshannon, kl_divergence, correlation, minkowski
output = pairwise_distance(X, Y, metric="euclidean")
```

### Quantization (Preprocessing)

Quantization compresses vectors before indexing, reducing memory and often improving search throughput.

**Scalar quantization** (float32 → int8):
```python
from cuvs.preprocessing.quantize import scalar

params = scalar.QuantizerParams(quantile=0.99)
quantizer = scalar.train(params, dataset)
transformed = scalar.transform(quantizer, dataset)       # int8
reconstructed = scalar.inverse_transform(quantizer, transformed)
```

**Binary quantization** (float32 → uint8 bitpacked):
```python
from cuvs.preprocessing.quantize import binary

transformed = binary.transform(dataset)  # uint8
# Use with metric="bitwise_hamming"
```

**Product quantization**:
```python
from cuvs.preprocessing.quantize import pq

params = pq.QuantizerParams(pq_bits=8, pq_dim=16)
quantizer = pq.build(params, dataset)
transformed, _ = pq.transform(quantizer, dataset)        # uint8
reconstructed = pq.inverse_transform(quantizer, transformed)
```

### PCA (Preprocessing)

GPU-accelerated PCA for dimensionality reduction before indexing (added in 26.06):

```python
import cupy as cp
from cuvs.preprocessing import pca

X = cp.random.random_sample((500, 32), dtype=cp.float32)
params = pca.Params(n_components=8, copy=True)
result = pca.fit(params, X)
transformed = pca.transform(params, X, result.components,
                            result.singular_vals, result.mu)
reconstructed = pca.inverse_transform(
    params, transformed, result.components,
    result.singular_vals, result.mu)
```

### NN-Descent (k-NN Graph Construction)

Builds an all-neighbors k-NN graph — useful as input to UMAP, t-SNE, or graph-based clustering.

```python
import cupy as cp
from cuvs.neighbors import nn_descent

dataset = cp.random.rand(100_000, 128, dtype=cp.float32)

build_params = nn_descent.IndexParams(
    metric="sqeuclidean",
    graph_degree=64,
    intermediate_graph_degree=96,   # >= 1.5 * graph_degree
    max_iterations=20,
)
index = nn_descent.build(build_params, dataset)
graph = index.graph  # (n_samples, graph_degree) — the k-NN graph
```

### `references/cuxfilter.md`

# cuxfilter Reference

cuxfilter is a GPU-accelerated cross-filtering dashboard library from the NVIDIA RAPIDS ecosystem. It enables interactive, multi-chart exploratory data analysis dashboards from Jupyter notebooks in just a few lines of Python. All filtering, groupby, and aggregation operations happen on the GPU via cuDF, with only the visualization results sent to the browser.

> **Full documentation:** https://docs.rapids.ai/api/cuxfilter/stable/
> **Version (stable):** 26.06.00 (final release)
> **Repository:** https://github.com/rapidsai/cuxfilter

> **⚠️ Project status: sunset.** cuxfilter has been sunset — **v26.06 is the final release** and no packages will be published for later RAPIDS releases (see [RSN 60](https://docs.rapids.ai/notices/rsn0060/)). Everything below still works with the 26.06 packages, but for new projects RAPIDS recommends composing dashboards directly from maintained libraries instead: **cuDF** for GPU data loading/aggregation plus **HoloViews / hvPlot / Datashader** for linked cross-filtering visualizations, served with **Panel**, Plotly Dash, Streamlit, or Bokeh.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Core Concepts](#core-concepts)
3. [DataFrame: Loading Data](#dataframe-loading-data)
4. [Charts](#charts)
5. [Widgets](#widgets)
6. [Dashboard Creation](#dashboard-creation)
7. [Layouts](#layouts)
8. [Themes](#themes)
9. [Dashboard Display and Export](#dashboard-display-and-export)
10. [Graph Visualization](#graph-visualization)
11. [Multi-GPU with Dask-cuDF](#multi-gpu-with-dask-cudf)
12. [Interoperability](#interoperability)
13. [Performance Tips](#performance-tips)
14. [Common Patterns](#common-patterns)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add --extra-index-url=https://pypi.nvidia.com "cuxfilter-cu12==26.6.*"   # For CUDA 12.x
uv add --extra-index-url=https://pypi.nvidia.com "cuxfilter-cu13==26.6.*"   # For CUDA 13.x
```

Both install the final 26.06 release — no further updates will be published. cuxfilter wheels are also on PyPI directly, so the extra index is optional. cuxfilter depends on cuDF, so `cudf-cu12` (or `cudf-cu13`) will be pulled in automatically.

**Platform:** Linux and WSL2 only (no native macOS or Windows).
**Requires:** NVIDIA GPU with CUDA 12.x or 13.x support, Python 3.11+.

Verify:
```python
import cuxfilter
import cudf

df = cudf.DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
cux_df = cuxfilter.DataFrame.from_dataframe(df)
print(cux_df.data.head())  # Should print GPU dataframe
```

---

## Core Concepts

cuxfilter has five main modules:

1. **`cuxfilter.DataFrame`** — Wraps a cuDF DataFrame for dashboard use. Entry point for creating dashboards.
2. **`cuxfilter.DashBoard`** — The interactive dashboard object. Created from a DataFrame with charts.
3. **`cuxfilter.charts`** — Chart factory functions (bar, scatter, line, heatmap, choropleth, graph, widgets).
4. **`cuxfilter.layouts`** — Preset and custom layout configurations for chart arrangement.
5. **`cuxfilter.themes`** — Visual themes for dashboards (default, dark, rapids, rapids_dark).

The workflow is always: **Load data → Create charts → Build dashboard → Display**.

---

## DataFrame: Loading Data

The `cuxfilter.DataFrame` is the starting point. It wraps a cuDF or dask_cudf DataFrame.

### From a cuDF DataFrame (most common)
```python
import cudf
import cuxfilter

cudf_df = cudf.DataFrame({
    "x": [0, 1, 2, 3, 4],
    "y": [10.0, 11.0, 12.0, 13.0, 14.0],
    "category": ["A", "B", "A", "B", "A"]
})
cux_df = cuxfilter.DataFrame.from_dataframe(cudf_df)
```

### From an Arrow file on disk
```python
cux_df = cuxfilter.DataFrame.from_arrow("data/my_dataset.arrow")
```

### From a graph (nodes + edges)
```python
import cugraph

edges = cudf.DataFrame({"source": [0, 1, 2], "target": [1, 2, 3], "weight": [1.0, 2.0, 3.0]})
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="source", destination="target", edge_attr="weight")
cux_df = cuxfilter.DataFrame.load_graph((G.nodes(), G.edges()))
```

Or directly from cuDF DataFrames:
```python
nodes = cudf.DataFrame({"vertex": [0, 1, 2, 3], "x": [0, 1, 2, 3], "y": [4, 4, 2, 6], "attr": [0, 1, 1, 1]})
edges = cudf.DataFrame({"source": [0, 1, 2], "target": [1, 2, 3], "weight": [1.0, 2.0, 3.0]})
cux_df = cuxfilter.DataFrame.load_graph((nodes, edges))
```

### Accessing the underlying data
```python
cux_df.data  # The cuDF DataFrame
cux_df.data["new_col"] = cux_df.data["x"] * 2  # Add columns before creating dashboard
```

---

## Charts

All chart functions are accessed via `cuxfilter.charts`. They use the top-level shorthand — you do NOT need to import submodules like `cuxfilter.charts.bokeh` or `cuxfilter.charts.datashader` directly.

### Bar Chart (Bokeh)
```python
chart = cuxfilter.charts.bar(
    x="column_name",           # Required: x-axis column
    y=None,                    # Optional: y-axis column (defaults to count)
    data_points=None,          # Number of bins (None = nunique)
    add_interaction=True,      # Enable cross-filtering interaction
    aggregate_fn="count",      # 'count' or 'mean'
    step_size=None,            # Step size for range slider
    title="",                  # Chart title
    autoscaling=True,          # Auto-scale y-axis on data update
)
```

### Line Chart (Bokeh)
```python
chart = cuxfilter.charts.line(
    x="x_col",
    y="y_col",
    data_points=100,
    add_interaction=True,
)
```

### Scatter Plot (Datashader — handles millions of points)
```python
chart = cuxfilter.charts.scatter(
    x="x_col",
    y="y_col",
    aggregate_col=None,              # Column for color aggregation
    aggregate_fn="count",            # 'count', 'mean', 'max', 'min'
    color_palette=None,              # Bokeh palette or list of hex colors
    point_size=15,
    pixel_shade_type="eq_hist",      # 'eq_hist', 'linear', 'log', 'cbrt'
    pixel_density=0.5,               # [0, 1], higher = denser
    pixel_spread="dynspread",        # 'dynspread' or 'spread'
    tile_provider=None,              # Map tile (e.g., "CartoLight" for geo data)
    title="",
    unselected_alpha=0.2,            # Transparency of unselected points
)
```

### Heatmap (Datashader)
```python
chart = cuxfilter.charts.heatmap(
    x="x_col",
    y="y_col",
    aggregate_col="value_col",
    aggregate_fn="mean",             # 'count', 'mean', 'max', 'min'
    color_palette=None,
    point_size=10,
    point_shape="rect_vertical",     # 'circle', 'square', 'rect_vertical', 'rect_horizontal'
    title="",
)
```

### Stacked Lines (Datashader)
```python
chart = cuxfilter.charts.stacked_lines(
    x="time_col",
    y=["series_a", "series_b", "series_c"],   # List of y columns
    colors=["red", "green", "blue"],
)
```

### Choropleth (Deck.gl — 2D and 3D maps)
```python
chart = cuxfilter.charts.choropleth(
    x="zip_code",
    color_column="metric_col",
    color_aggregate_fn="mean",         # 'count', 'mean', 'sum', 'min', 'max', 'std'
    elevation_column="value_col",      # Set for 3D choropleth, omit for 2D
    elevation_factor=0.00001,
    elevation_aggregate_fn="sum",
    geoJSONSource="https://url/to/geojson",
    geo_color_palette=None,            # Default: Inferno256
    nan_color="#d3d3d3",
    tooltip=True,
    tooltip_include_cols=["zip_code", "metric_col"],
    title="",
)
```

### Graph (Datashader — node-link diagrams)
```python
chart = cuxfilter.charts.datashader.graph(
    node_x="x",                  # Default "x"
    node_y="y",                  # Default "y"
    node_id="vertex",            # Default "vertex"
    edge_source="source",        # Default "source"
    edge_target="target",        # Default "target"
    node_aggregate_col=None,
    node_color_palette=None,
    edge_color_palette=["#000000"],
    node_point_size=15,
    node_pixel_shade_type="eq_hist",
    edge_render_type="direct",   # 'direct' or 'curved' (curved is experimental)
    edge_transparency=0,         # [0, 1]
    tile_provider=None,
    title="",
    unselected_alpha=0.2,
)
```

---

## Widgets

Widgets provide interactive filtering controls, typically placed in the sidebar.

### Range Slider
```python
widget = cuxfilter.charts.range_slider("numeric_col", step_size=1)
```

### Date Range Slider
```python
widget = cuxfilter.charts.date_range_slider("datetime_col")
```

### Float Slider
```python
widget = cuxfilter.charts.float_slider("float_col", step_size=0.5)
```

### Int Slider
```python
widget = cuxfilter.charts.int_slider("int_col", step_size=1)
```

### Dropdown
```python
widget = cuxfilter.charts.drop_down("category_col")
```

### Multi-Select
```python
widget = cuxfilter.charts.multi_select("category_col")
```

### Number (KPI indicator)
```python
widget = cuxfilter.charts.number(
    expression="column_name",                # Or a computed expression like "(x + y) / 2"
    aggregate_fn="mean",                     # 'count', 'mean', 'min', 'max', 'sum', 'std'
    title="Average Value",
    format="{value:.2f}",                    # Python format string
    colors=[(33, "green"), (66, "gold"), (100, "red")],  # Threshold coloring
    font_size="18pt",
)
```

### Card (Markdown content)
```python
import panel as pn
widget = cuxfilter.charts.card(pn.pane.Markdown("## My Dashboard\nSome description text"))
```

---

## Dashboard Creation

Create a dashboard by calling `.dashboard()` on a cuxfilter DataFrame:

```python
# Define charts and widgets
chart1 = cuxfilter.charts.scatter(x="x_col", y="y_col")
chart2 = cuxfilter.charts.bar("category_col")
sidebar_widget = cuxfilter.charts.range_slider("value_col")
number_widget = cuxfilter.charts.number(expression="value_col", aggregate_fn="mean", title="Mean Value")

# Build dashboard
d = cux_df.dashboard(
    charts=[chart1, chart2],               # Main area charts
    sidebar=[sidebar_widget, number_widget],  # Sidebar widgets
    layout=cuxfilter.layouts.feature_and_base,
    theme=cuxfilter.themes.rapids_dark,
    title="My Dashboard",
    data_size_widget=True,                 # Show current data count
)
```

### Adding charts after creation
```python
new_chart = cuxfilter.charts.line("x_col", "y_col")
d.add_charts(charts=[new_chart])
# or
d.add_charts(sidebar=[cuxfilter.charts.card(pn.pane.Markdown("# Note"))])
```

---

## Layouts

### Preset Layouts

| Layout | Description | Charts |
|--------|-------------|--------|
| `layouts.single_feature` | One chart fills the page | 1 |
| `layouts.feature_and_base` | Large chart on top, smaller below (66/33 split) | 2 |
| `layouts.double_feature` | Two charts side-by-side | 2 |
| `layouts.left_feature_right_double` | One large left, two stacked right | 3 |
| `layouts.triple_feature` | Three charts in a row | 3 |
| `layouts.feature_and_double_base` | One large top, two below | 3 |
| `layouts.two_by_two` | 2x2 grid | 4 |
| `layouts.feature_and_triple_base` | One large top, three below | 4 |
| `layouts.feature_and_quad_base` | One large top, four below | 5 |
| `layouts.feature_and_five_edge` | One large center, five around | 6 |
| `layouts.two_by_three` | 2x3 grid | 6 |
| `layouts.double_feature_quad_base` | Two large top, four below | 6 |
| `layouts.three_by_three` | 3x3 grid | 9 |

### Custom Layouts with `layout_array`

Use `layout_array` for full control. It's a list-of-lists where each inner list is a row, and numbers refer to chart indices (1-based):

```python
# Chart 1 takes top-left 2x2 area, charts 2 and 3 on the right
d = cux_df.dashboard(
    charts_list,
    layout_array=[[1, 1, 2, 2], [1, 1, 3, 4]],
    theme=cuxfilter.themes.rapids_dark,
)
```

Rules:
- Each number maps to a chart (1 = first chart, 2 = second, etc.)
- Repeating a number across cells makes that chart span those cells
- The array is auto-scaled to fit the screen

---

## Themes

Four built-in themes:

| Theme | Description |
|-------|-------------|
| `cuxfilter.themes.default` | Light theme (default) |
| `cuxfilter.themes.dark` | Dark theme |
| `cuxfilter.themes.rapids` | RAPIDS-branded light theme |
| `cuxfilter.themes.rapids_dark` | RAPIDS-branded dark theme |

```python
d = cux_df.dashboard(charts, theme=cuxfilter.themes.rapids_dark)
```

---

## Dashboard Display and Export

### Display inline in a notebook
```python
d.app(sidebar_width=280, width=1200, height=800)
```

### Display as a separate web app (opens new browser tab)
```python
d.show()
# or with custom URL/port
d.show(notebook_url="http://localhost:8888", port=8050)
```

### JupyterHub deployment
```python
d.show(service_proxy="jupyterhub")
```

### Stop the server
```python
d.stop()
```

### Export filtered data
After interacting with the dashboard (selecting ranges, filtering), export the current filtered DataFrame:

```python
filtered_df = d.export()  # Returns cuDF DataFrame matching current filter state
# Also prints the query string, e.g.: "2 <= key <= 4"
```

### Access dashboard charts
```python
d.charts  # Dictionary of chart objects
```

---

## Graph Visualization

cuxfilter integrates with cuGraph for interactive graph visualization:

```python
import cuxfilter
import cudf
import cugraph

# Create graph
edges = cudf.DataFrame({
    "source": [0, 0, 1, 1, 2],
    "target": [1, 2, 2, 3, 3]
})
G = cugraph.Graph()
G.from_cudf_edgelist(edges, source="source", destination="target")

# Load into cuxfilter (needs node positions — use force_atlas2 or similar layout)
positions = cugraph.force_atlas2(G)
nodes = positions.rename(columns={"vertex": "vertex", "x": "x", "y": "y"})

cux_df = cuxfilter.DataFrame.load_graph((nodes, G.edges()))

# Create graph chart
chart = cuxfilter.charts.datashader.graph(
    node_pixel_shade_type="linear",
    unselected_alpha=0.2,
)

d = cux_df.dashboard([chart], layout=cuxfilter.layouts.single_feature)
d.app()
```

---

## Multi-GPU with Dask-cuDF

cuxfilter works seamlessly with `dask_cudf.DataFrame` — just pass it in place of a cuDF DataFrame:

```python
import dask_cudf

ddf = dask_cudf.read_parquet("large_dataset/*.parquet")
cux_df = cuxfilter.DataFrame.from_dataframe(ddf)

# Everything else is the same
chart = cuxfilter.charts.scatter(x="x", y="y")
d = cux_df.dashboard([chart])
d.app()
```

Use dask_cudf when:
- Data doesn't fit in a single GPU's memory
- You want to distribute across multiple GPUs
- Processing many files at once

**Supported chart types with dask_cudf:**
- bokeh: bar, line
- datashader: scatter, line, stacked_lines, heatmap, graph (limited edge rendering)
- panel_widgets: all widgets
- deckgl: choropleth (2D and 3D)

---

## Interoperability

cuxfilter sits at the visualization layer of the RAPIDS ecosystem:

- **cuDF** — The data layer. cuxfilter.DataFrame wraps cuDF DataFrames.
- **cuGraph** — Graph analytics. Use `cuxfilter.DataFrame.load_graph()` to visualize cuGraph results.
- **cuML** — Run cuML, then visualize results (e.g., UMAP embeddings, cluster assignments) with cuxfilter.
- **HoloViz ecosystem** — Built on Panel, Bokeh, Datashader, and HoloViews.
- **Deck.gl** — WebGL-powered choropleth maps.

### Typical RAPIDS + cuxfilter pipeline
```python
import cudf
import cuml
import cuxfilter

# Load and preprocess with cuDF
df = cudf.read_parquet("data.parquet")
df = df.dropna().reset_index(drop=True)

# Run ML with cuML (e.g., UMAP for dimensionality reduction)
from cuml.manifold import UMAP
umap = UMAP(n_components=2)
embedding = umap.fit_transform(df[["feature1", "feature2", "feature3"]])
df["umap_x"] = embedding[:, 0]
df["umap_y"] = embedding[:, 1]

# Visualize with cuxfilter
cux_df = cuxfilter.DataFrame.from_dataframe(df)
scatter = cuxfilter.charts.scatter(
    x="umap_x", y="umap_y",
    aggregate_col="cluster_label",
    aggregate_fn="mean",
    pixel_shade_type="linear",
)
bar = cuxfilter.charts.bar("cluster_label")
d = cux_df.dashboard([scatter, bar], layout=cuxfilter.layouts.feature_and_base)
d.app()
```

---

## Performance Tips

1. **Keep data on GPU.** Load with `cudf.read_parquet()` or `cudf.read_csv()`, then wrap with `cuxfilter.DataFrame.from_dataframe()`. Avoid converting to/from pandas.

2. **Use appropriate chart types for data size:**
   - < 10K points: Bokeh charts (bar, line) work well
   - 10K–100M+ points: Datashader charts (scatter, heatmap) handle large datasets efficiently via server-side rasterization

3. **Limit data_points for bar charts.** For columns with many unique values, set `data_points` to bin them (e.g., `bar("col", data_points=50)`).

4. **Use `float32` when possible.** GPU operations are faster with 32-bit floats. Cast before loading: `df["col"] = df["col"].astype("float32")`.

5. **Pre-compute derived columns** before creating the dashboard, not inside chart callbacks.

6. **Use `layout_array`** for complex dashboards to control exactly where each chart appears.

7. **Increase `timeout`** for datashader charts if zooming feels laggy on very large datasets.

---

## Common Patterns

### Exploratory data analysis dashboard
```python
import cudf
import cuxfilter

df = cudf.read_parquet("dataset.parquet")
cux_df = cuxfilter.DataFrame.from_dataframe(df)

# Overview charts
scatter = cuxfilter.charts.scatter(x="feature1", y="feature2", pixel_shade_type="linear")
hist1 = cuxfilter.charts.bar("feature1", data_points=50)
hist2 = cuxfilter.charts.bar("category")

# Sidebar filters
slider = cuxfilter.charts.range_slider("value_col")
dropdown = cuxfilter.charts.drop_down("category")
kpi = cuxfilter.charts.number(expression="value_col", aggregate_fn="mean", title="Mean Value")

d = cux_df.dashboard(
    [scatter, hist1, hist2],
    sidebar=[slider, dropdown, kpi],
    layout=cuxfilter.layouts.feature_and_double_base,
    theme=cuxfilter.themes.rapids_dark,
    title="Data Explorer",
)
d.app()
```

### Geospatial dashboard with scatter on map tiles
```python
chart = cuxfilter.charts.scatter(
    x="longitude",
    y="latitude",
    aggregate_col="value",
    aggregate_fn="mean",
    color_palette=["#3182bd", "#6baed6", "#ff0068"],
    tile_provider="CartoLight",
    pixel_shade_type="linear",
    title="Geo Scatter",
)
```

### Time series dashboard
```python
line_chart = cuxfilter.charts.line("timestamp", "metric")
bar_chart = cuxfilter.charts.bar("hour_of_day")
date_slider = cuxfilter.charts.date_range_slider("timestamp")

d = cux_df.dashboard(
    [line_chart, bar_chart],
    sidebar=[date_slider],
    layout=cuxfilter.layouts.feature_and_base,
)
```

### Export filtered subset for further analysis
```python
# After user interacts with dashboard, export current selection
d.app()
# ... user filters data in the dashboard ...
filtered = d.export()  # cuDF DataFrame of currently visible/selected data
# Continue analysis with cuDF, cuML, etc.
```

### `references/decision_framework.md`

# Decision Framework: Which Library to Use

Each RAPIDS/GPU library, the CPU library it replaces, what it is good at, and when it is
the wrong choice — CuPy, Numba CUDA, Warp, cuDF, cuML, cuGraph, KvikIO, cuxfilter, cuCIM,
cuVS, cuSpatial, and RAFT — plus guidance on combining them.

Choose the right tool based on what the user's code actually does. Read the appropriate reference file(s) before writing any GPU code.

First decide whether a port is justified: establish an end-to-end baseline, estimate peak device
memory including temporaries, and identify transfer and fallback boundaries. Prefer an accelerator
or backend mode before a native rewrite, and prefer a maintained library operation before a custom
kernel. Validate output semantics and use synchronized GPU timing on representative data.

### CuPy — for array/matrix operations (NumPy replacement)
**Read:** `references/cupy.md`

Use CuPy when the user's code is primarily:
- NumPy array operations (element-wise math, linear algebra, FFT, sorting, reductions)
- SciPy operations (sparse matrices, signal processing, image filtering, special functions)
- Any code that chains NumPy calls — CuPy is a drop-in replacement

CuPy wraps NVIDIA's optimized libraries (cuBLAS, cuFFT, cuSOLVER, cuSPARSE, cuRAND) so standard operations are already tuned. Most NumPy code works by changing `import numpy as np` to `import cupy as cp`.

**Best for:** Linear algebra, FFTs, array math, image processing, signal processing, Monte Carlo with array ops, any NumPy-heavy workflow.

### Numba-CUDA-MLIR / Numba-CUDA — for custom GPU kernels
**Read:** `references/numba.md`

Use this path when the user needs:
- Custom algorithms that don't map to standard array operations
- Fine-grained control over GPU threads, blocks, and shared memory
- Reduction operations with custom logic
- Stencil computations or neighbor-dependent calculations
- Anything requiring the CUDA programming model directly

For new projects, evaluate **Numba-CUDA-MLIR**, where NVIDIA is doing new feature development.
Use the established `numba-cuda` package for existing `numba.cuda` code, compatibility, or features
not yet available in the MLIR implementation; it is in maintenance mode through the CUDA 13
lifetime. Do not invest in custom kernels until profiling rules out CuPy or another tuned library.

**Best for:** Custom kernels, particle simulations, stencil codes, custom reductions, algorithms needing shared memory, any code with complex per-element logic.

### Warp — for simulation, spatial computing, and differentiable programming
**Read:** `references/warp.md`

Use Warp when the user's code is primarily:
- Physics simulation (particles, cloth, fluids, rigid bodies, DEM, SPH)
- Geometry processing (mesh operations, ray casting, signed distance fields, marching cubes)
- Robotics (kinematics, dynamics, control with transforms and quaternions)
- Differentiable simulation for ML training (integrates with PyTorch/JAX autograd)
- Any Python simulation loop that needs to be JIT-compiled to GPU
- Spatial computing with meshes, volumes (NanoVDB), hash grids, or BVH queries

Warp JIT-compiles `@wp.kernel` Python functions to CUDA, with built-in types for spatial computing
(vec3, mat33, quat, transform) and primitives for geometry queries (Mesh, Volume, HashGrid, BVH).
Warp can generate adjoint kernels for differentiable programs. The higher-level `warp.sim` module
was removed in Warp 1.10; use the separate **Newton** engine for maintained high-level rigid-body,
robotics, and simulation-environment APIs, and use Warp for custom kernels and domain primitives.

**Best for:** Physics simulation, mesh ray casting, particle systems, differentiable rendering, robotics kinematics, SDF operations, any workload combining spatial data structures with GPU compute.

**Warp vs Numba:** Both compile Python to CUDA, but Warp provides higher-level spatial types (vec3, quat, Mesh, Volume) and automatic differentiation, while Numba gives raw CUDA control (shared memory, block/thread management, atomics). Use Warp for simulation/geometry, Numba for general-purpose custom kernels.

### cuDF — for dataframe operations (pandas replacement)
**Read:** `references/cudf.md`

Use cuDF when the user's code is primarily:
- pandas DataFrame operations (filtering, groupby, joins, aggregations)
- CSV/Parquet/JSON reading and processing
- ETL pipelines or data wrangling on large datasets
- Any pandas-heavy workflow on datasets that fit in GPU memory

cuDF's `cudf.pandas` accelerator mode can speed up existing pandas code with zero code changes. For maximum performance, use the native cuDF API.

**Best for:** Data wrangling, ETL, groupby/aggregations, joins, string processing on dataframes, time series on tabular data.

### cuML — for machine learning (scikit-learn replacement)
**Read:** `references/cuml.md`

Use cuML when the user's code is primarily:
- scikit-learn estimators (classification, regression, clustering, dimensionality reduction)
- ML preprocessing (scaling, encoding, imputation, feature extraction)
- Hyperparameter tuning or cross-validation
- Tree model inference (XGBoost, LightGBM, sklearn Random Forest via FIL)
- UMAP, t-SNE, HDBSCAN, or KNN on large datasets

Start with cuML's `cuml.accel` accelerator mode when compatibility permits. Move to the native
cuML API for unsupported estimators, explicit output control, or a measured performance reason.
Benchmark the user's estimator, dimensions, and end-to-end pipeline rather than relying on headline
speedup ranges.

**Best for:** Classification, regression, clustering, dimensionality reduction, preprocessing pipelines, model inference, any scikit-learn-heavy workflow.

### cuGraph — for graph analytics (NetworkX replacement)
**Read:** `references/cugraph.md`

Use cuGraph when the user's code is primarily:
- NetworkX graph algorithms (centrality, community detection, shortest paths, PageRank)
- Graph construction and analysis on large networks
- Social network analysis, knowledge graphs, or recommendation systems
- Any graph algorithm on networks with 10K+ edges

Start with the `nx-cugraph` backend and inspect fallback behavior. Move to the native cuGraph API
with cuDF edge lists for unsupported operations or a measured performance reason. Include graph
construction and host-device conversion in end-to-end benchmarks.

**Best for:** PageRank, betweenness centrality, community detection (Louvain, Leiden), BFS/SSSP, connected components, link prediction, graph neural network sampling, any NetworkX-heavy workflow.

### KvikIO — for high-performance GPU file IO
**Read:** `references/kvikio.md`

Use KvikIO when the user's code is primarily:
- Loading large binary data files directly into GPU memory
- Writing GPU arrays to disk without copying to host first
- Reading data from remote storage (S3, HTTP, WebHDFS) into GPU memory
- Working with Zarr arrays on GPU (GDSStore backend)
- Any pipeline where file IO is the bottleneck between storage and GPU

KvikIO provides Python bindings to NVIDIA cuFile, enabling GPUDirect Storage (GDS) — data flows directly between NVMe storage and GPU memory, bypassing CPU memory entirely. When GDS isn't available, it falls back to POSIX IO transparently. It handles both host and device data seamlessly.

**Best for:** Loading binary data to GPU, saving GPU arrays to disk, reading from S3/HTTP directly to GPU, Zarr arrays on GPU, replacing `numpy.fromfile()` → `cupy` patterns, any IO-heavy GPU pipeline where data staging through CPU memory is a bottleneck.

**Note:** For tabular formats (CSV, Parquet, JSON), use cuDF's built-in readers instead — they're optimized for those formats. KvikIO is for raw binary data and remote file access.

### cuxfilter — legacy dashboards only
**Read:** `references/cuxfilter.md`

**Project status: sunset.** RAPIDS 26.06 was cuxfilter's final release (RSN 60). Reach
for cuxfilter only when the user already uses it or explicitly requests it. For new dashboards,
prefer cuDF for GPU data prep combined with HoloViews/hvPlot/Datashader linked selections, served
with Panel, Plotly Dash, Streamlit, or Bokeh.

Maintain cuxfilter when an existing application needs:
- Interactive cross-filtering dashboards on large datasets (millions of rows)
- Exploratory data analysis with linked charts that filter each other
- GPU-accelerated visualization with scatter plots, bar charts, heatmaps, choropleths, or graph visualizations
- Dashboard prototyping from Jupyter notebooks with minimal code
- Visualizing results from cuDF, cuML, or cuGraph pipelines

cuxfilter leverages cuDF for all data operations on the GPU — filtering, groupby, and aggregation happen entirely on the GPU, with only rendering results sent to the browser. It integrates Bokeh, Datashader (for millions of points), Deck.gl (for maps), and Panel widgets.

**Best for:** Existing 26.06 applications that cannot yet migrate. Do not start a new dependency on
an unmaintained dashboard framework.

### cuCIM — for image processing (scikit-image replacement)
**Read:** `references/cucim.md`

Use cuCIM when the user's code is primarily:
- scikit-image operations (filtering, morphology, segmentation, feature detection, color conversion)
- Image preprocessing pipelines for deep learning (resize, normalize, augment)
- Digital pathology (whole-slide image reading, H&E stain normalization, cell counting)
- Microscopy, remote sensing, or medical imaging workflows
- Any scikit-image-heavy pipeline processing images at 512x512 or larger

cuCIM's `cucim.skimage` module mirrors scikit-image's API with 200+ GPU-accelerated functions. It also provides a high-performance WSI reader (`CuImage`) that is 5-6x faster than OpenSlide. All functions work on CuPy arrays — zero-copy, all on GPU.

**Best for:** Filtering (Gaussian, Sobel, Frangi), morphology, thresholding, connected component labeling, region properties, color space conversion, image registration, denoising, whole-slide image processing, DL preprocessing pipelines.

### cuVS — for vector search (Faiss/Annoy replacement)
**Read:** `references/cuvs.md`

Use cuVS when the user's code is primarily:
- Approximate nearest neighbor (ANN) search on high-dimensional vectors
- Similarity search for RAG, recommender systems, or semantic retrieval
- k-NN graph construction for clustering or visualization
- Any Faiss, Annoy, ScaNN, or sklearn NearestNeighbors workload on large embedding datasets

cuVS provides GPU-accelerated ANN index types (CAGRA, IVF-Flat, IVF-PQ, brute force) plus HNSW for CPU serving from GPU-built indexes. It powers the GPU backends of Faiss, Milvus, and Lucene. Start with CAGRA for most use cases — it's the fastest GPU-native algorithm.

**Best for:** Embedding search, RAG retrieval, recommender systems, image/text/audio similarity search, k-NN graph construction, any nearest-neighbor workload on 10K+ vectors.

### cuSpatial — archived geospatial pipelines only
**Read:** `references/cuspatial.md`

**Project status: archived.** The cuSpatial repository has been read-only since July 2025; the final release is 25.04, which pins `cudf-cu12==25.4.*` and therefore conflicts with current RAPIDS releases in the same environment. No official successor exists. Recommend it only in a dedicated legacy environment; otherwise keep geometry operations on GeoPandas/Shapely (CPU) and accelerate the tabular parts of the workflow with cuDF.

Maintain cuSpatial when an isolated 25.04 environment already uses:
- GeoPandas spatial operations (point-in-polygon, spatial joins, distance calculations)
- Trajectory analysis (grouping GPS traces, computing speeds/distances)
- Spatial indexing (quadtree) for large-scale spatial joins
- Haversine distance calculations on lat/lon coordinates
- Any GeoPandas/shapely-heavy workflow on large geospatial datasets

cuSpatial provides GPU-accelerated `GeoSeries` and `GeoDataFrame` types compatible with GeoPandas, plus spatial join, distance, and trajectory functions. Convert from GeoPandas with `cuspatial.from_geopandas()`.

**Best for:** Existing pipelines pinned to the 25.04 stack. Do not present it as a current
GeoPandas replacement or combine it with current RAPIDS packages.

### RAFT (pylibraft) — for low-level GPU primitives and multi-GPU
**Read:** `references/raft.md`

Use RAFT when the user needs:
- GPU-accelerated sparse eigenvalue problems (`scipy.sparse.linalg.eigsh` replacement)
- Low-level GPU device memory management (`device_ndarray`)
- Random graph generation (R-MAT model for benchmarking)
- Multi-node multi-GPU communication infrastructure (via `raft-dask`)
- Building blocks that underlie higher-level RAPIDS libraries

RAFT provides the foundational primitives that cuML and cuGraph are built on. Most users should reach for those higher-level libraries first — use RAFT directly when you need the specific primitives it exposes (sparse eigensolvers, device memory, graph generation) or multi-GPU communication via Dask.

**Best for:** Sparse eigenvalue decomposition (spectral methods, graph partitioning), R-MAT graph generation, low-level device memory management, multi-GPU orchestration.

**Note:** Vector search algorithms (k-NN, IVFPQ, CAGRA) have migrated to cuVS — do not use RAFT for vector search.

### Combining Libraries

Many real workloads benefit from using multiple libraries together. They interoperate via the CUDA Array Interface — zero-copy data sharing between CuPy, Numba, Warp, cuDF, cuML, cuGraph, cuVS, cuCIM, cuSpatial, KvikIO, PyTorch, JAX, and other GPU libraries.

Common combinations:
- **cuDF + cuML**: Load and preprocess data with cuDF, train/predict with cuML — the full RAPIDS pipeline
- **cuDF + cuGraph**: Build graphs from cuDF edge lists, run graph analytics with cuGraph
- **cuGraph + cuML**: Extract graph features with cuGraph, feed into cuML for ML
- **cuML + cuVS**: Train an embedding model with cuML, index and search embeddings with cuVS
- **cuDF + CuPy**: Load and filter data with cuDF, then do numerical analysis with CuPy
- **CuPy + cuVS**: Generate embeddings with CuPy operations, build a cuVS search index — zero-copy
- **Warp + PyTorch**: Differentiable simulation in Warp, backpropagate gradients into PyTorch training loop
- **Warp + CuPy**: Use CuPy for array math, Warp for spatial queries (mesh, volume) — zero-copy via CUDA Array Interface
- **Warp + JAX**: Warp kernels as JAX primitives inside jitted functions
- **CuPy + Numba**: Use CuPy for standard ops, drop into Numba for custom kernels
- **cuDF + Numba**: Process dataframes with cuDF, apply custom GPU functions via Numba UDFs
- **cuML + CuPy**: Train with cuML, do custom post-processing with CuPy
- **cuDF + cuxfilter (legacy 26.06 only)**: Maintain an existing cross-filtering dashboard
- **cuML + cuxfilter (legacy 26.06 only)**: Maintain an existing ML visualization workflow
- **cuGraph + cuxfilter (legacy 26.06 only)**: Maintain an existing graph visualization
- **cuCIM + CuPy**: cuCIM operates on CuPy arrays natively — chain image processing with array math
- **cuCIM + PyTorch**: Preprocess images with cuCIM, pass directly to PyTorch via DLPack — zero-copy
- **cuCIM + cuML**: Extract image features with cuCIM (regionprops), train classifiers with cuML
- **KvikIO + CuPy**: Load raw binary data directly into CuPy arrays via GDS, bypassing CPU memory
- **KvikIO + Numba**: Read data directly to GPU with KvikIO, process with custom Numba CUDA kernels
- **KvikIO + Zarr**: Use GDSStore backend to read/write chunked N-dimensional arrays directly on GPU
- **cuSpatial + cuDF (legacy 25.04 only)**: Keep both packages on the compatible frozen stack
- **cuSpatial + cuML (legacy 25.04 only)**: Keep the full environment pinned and isolated
- **RAFT + CuPy**: Use RAFT's eigsh() on sparse matrices built with CuPy/cupyx.scipy.sparse
- **RAFT + raft-dask**: Scale GPU workloads across multiple GPUs/nodes via Dask

### `references/installation.md`

# Installation

Per-library install commands, CUDA version selection, and environment setup.

Use `uv add` in standalone examples to match this repository's convention. If the user's project
already uses another package manager, follow that project rather than rewriting its tooling.

RAPIDS packages below track RAPIDS 26.06 (June 2026): they require Python >= 3.11 and CUDA 12.x or 13.x. Every maintained RAPIDS package ships `-cu12` and `-cu13` wheel variants; the examples use `-cu12`, so substitute `-cu13` for CUDA 13 systems. Use the [RAPIDS release selector](https://docs.rapids.ai/install/) to confirm driver, Python, CUDA, and package compatibility. The NVIDIA extra index is included consistently because package availability differs; many packages are also mirrored directly on PyPI.

```bash
# CuPy (choose the right CUDA version; CuPy 14+ supports CUDA 12/13 only)
uv add "cupy-cuda12x==14.1.*"          # For CUDA 12.x
uv add "cupy-cuda13x==14.1.*"          # For CUDA 13.x

# Numba-CUDA compatibility path (maintenance mode; installs numba automatically)
uv add "numba-cuda[cu12]==0.30.*"      # use [cu13] for CUDA 13
# For new kernel projects, evaluate Numba-CUDA-MLIR and its migration guide first.

# Warp (simulation, spatial computing, differentiable programming)
uv add "warp-lang==1.15.*"              # CUDA 12 runtime included; CUDA 13 builds are on GitHub Releases only

# cuDF (RAPIDS)
uv add --extra-index-url=https://pypi.nvidia.com "cudf-cu12==26.6.*"
# For cudf.pandas accelerator mode, that's all you need
# Load it with: python -m cudf.pandas your_script.py

# cuML (RAPIDS machine learning)
uv add --extra-index-url=https://pypi.nvidia.com "cuml-cu12==26.6.*"
# For cuml.accel accelerator mode (zero-change sklearn acceleration):
# Load it with: python -m cuml.accel your_script.py

# cuGraph (RAPIDS graph analytics) — NVIDIA index still required (PyPI has only stub packages)
uv add --extra-index-url=https://pypi.nvidia.com "cugraph-cu12==26.6.*"    # Core cuGraph
uv add --extra-index-url=https://pypi.nvidia.com "nx-cugraph-cu12==26.6.*" # NetworkX backend
# For nx-cugraph zero-change NetworkX acceleration:
# NX_CUGRAPH_AUTOCONFIG=True python your_script.py

# KvikIO (high-performance GPU file IO)
uv add --extra-index-url=https://pypi.nvidia.com "kvikio-cu12==26.6.*"
# Optional: uv add "zarr==3.*"   # For Zarr GPU backend support

# cuxfilter (interactive dashboards) — SUNSET: 26.06 is the final release
uv add --extra-index-url=https://pypi.nvidia.com "cuxfilter-cu12==26.6.*"
# Depends on cuDF — installs it automatically

# cuCIM (RAPIDS image processing — scikit-image on GPU)
uv add --extra-index-url=https://pypi.nvidia.com "cucim-cu12==26.6.*"

# cuVS (RAPIDS vector search)
uv add --extra-index-url=https://pypi.nvidia.com "cuvs-cu12==26.6.*"

# cuSpatial (geospatial) — ARCHIVED: frozen at 25.04, pins cudf-cu12==25.4.*
# Install only in a dedicated environment; NVIDIA index required
uv add --extra-index-url=https://pypi.nvidia.com "cuspatial-cu12==25.4.*"

# RAFT (low-level GPU primitives)
uv add --extra-index-url=https://pypi.nvidia.com "pylibraft-cu12==26.6.*"   # Core primitives
uv add --extra-index-url=https://pypi.nvidia.com "raft-dask-cu12==26.6.*"   # Multi-GPU support (optional)
```

To check CUDA availability after installation:

```python
# CuPy
import cupy as cp
print(cp.cuda.runtime.getDeviceCount())  # Should be >= 1

# Numba
from numba import cuda
print(cuda.is_available())               # Should be True
print(cuda.detect())                     # Shows GPU details

# cuDF
import cudf
print(cudf.Series([1, 2, 3]))           # Should print a GPU series

# cuML
import cuml
print(cuml.__version__)                  # Should print version

# cuGraph
import cugraph
print(cugraph.__version__)               # Should print version

# Warp
import warp as wp
wp.init()                                # Should print device info

# KvikIO
import kvikio
import kvikio.cufile_driver
print(kvikio.cufile_driver.get("is_gds_available"))  # True if GDS is set up

# cuxfilter
import cuxfilter
print(cuxfilter.__version__)             # Should print version

# cuCIM
from cucim.skimage.filters import gaussian
import cupy as cp
print(gaussian(cp.zeros((8, 8), dtype=cp.float32), sigma=1).shape)

# cuVS
from cuvs.neighbors import cagra
import cupy as cp
dataset = cp.random.rand(1000, 128, dtype=cp.float32)
index = cagra.build(cagra.IndexParams(), dataset)
print("cuVS working")                    # Should print confirmation

# cuSpatial
import cuspatial
from shapely.geometry import Point
gs = cuspatial.GeoSeries([Point(0, 0)])
print("cuSpatial working")              # Should print confirmation

# RAFT (pylibraft)
from pylibraft.common import DeviceResources
handle = DeviceResources()
handle.sync()
print("pylibraft is working")
```

### `references/kvikio.md`

# KvikIO Reference — High-Performance GPU File IO

KvikIO is a Python and C++ library for high-performance file IO. It provides bindings to NVIDIA cuFile, enabling GPUDirect Storage (GDS) — reading and writing data directly between storage and GPU memory, bypassing CPU memory entirely. When GDS isn't available, KvikIO falls back gracefully to POSIX IO while still handling both host and device data seamlessly.

KvikIO is part of the RAPIDS ecosystem and interoperates with CuPy, cuDF, Numba, and other GPU libraries.

## Table of Contents

1. [Installation](#installation)
2. [When to Use KvikIO](#when-to-use-kvikio)
3. [CuFile — Local File IO](#cufile--local-file-io)
4. [RemoteFile — S3, HTTP, WebHDFS](#remotefile--s3-http-webhdfs)
5. [Zarr Integration](#zarr-integration)
6. [Memory-Mapped Files](#memory-mapped-files)
7. [Runtime Settings](#runtime-settings)
8. [Performance Optimization](#performance-optimization)
9. [Interoperability](#interoperability)
10. [Common Patterns](#common-patterns)
11. [Common Pitfalls](#common-pitfalls)

---

## Installation

```bash
# CUDA 12.x
uv add "kvikio-cu12==26.6.*"

# CUDA 13.x
uv add "kvikio-cu13==26.6.*"

# For Zarr support (optional)
uv add "zarr==3.*"
```

Verify installation:

```python
import kvikio
# Check if GDS is available
import kvikio.cufile_driver
print(kvikio.cufile_driver.get("is_gds_available"))  # True if GDS is set up
```

---

## When to Use KvikIO

Use KvikIO when:
- **Loading large binary data directly to GPU** — avoids the CPU-memory copy that standard `open()` or NumPy's `fromfile()` would require
- **Writing GPU arrays to disk** — saves directly from device memory without copying to host first
- **Reading from remote storage (S3, HTTP, WebHDFS) into GPU memory** — skips the host-memory staging step
- **Working with Zarr arrays on GPU** — the GDSStore backend reads chunks directly into CuPy arrays
- **IO is the bottleneck** — GDS can achieve close to raw NVMe bandwidth (6-7 GB/s per drive) vs standard IO that tops out at CPU-memory bandwidth
- **Overlapping IO and compute** — non-blocking reads/writes let you pipeline data loading with GPU computation

KvikIO is a poor fit when:
- Data is small (< 1 MB) — kernel launch and GDS overhead dominate
- You're reading structured formats (CSV, Parquet, JSON) — use cuDF instead, which has its own optimized readers
- You only need host memory — standard Python IO is simpler

---

## CuFile — Local File IO

`kvikio.CuFile` is the primary interface for local file IO. It replaces Python's `open()` for GPU workloads.

### Basic Usage

```python
import cupy as cp
import kvikio

# Write a GPU array to disk
a = cp.arange(1_000_000, dtype=cp.float32)
with kvikio.CuFile("data.bin", "w") as f:
    f.write(a)

# Read it back
b = cp.empty(1_000_000, dtype=cp.float32)
with kvikio.CuFile("data.bin", "r") as f:
    f.read(b)

assert cp.all(a == b)
```

### API Methods

| Method | Blocking | Description |
|--------|----------|-------------|
| `read(buf, size, file_offset)` | Yes | Read into device or host buffer |
| `write(buf, size, file_offset)` | Yes | Write from device or host buffer |
| `pread(buf, size, file_offset)` | No | Non-blocking parallel read, returns `IOFuture` |
| `pwrite(buf, size, file_offset)` | No | Non-blocking parallel write, returns `IOFuture` |
| `raw_read(buf, size, file_offset)` | Yes | Low-level single-thread read (device only) |
| `raw_write(buf, size, file_offset)` | Yes | Low-level single-thread write (device only) |
| `raw_read_async(buf, stream, size, file_offset)` | No | CUDA-stream async read (device only) |
| `raw_write_async(buf, stream, size, file_offset)` | No | CUDA-stream async write (device only) |

File modes: `"r"` (read), `"w"` (write/truncate), `"a"` (append), `"+"` (read+write).

### Non-Blocking IO with Futures

`pread` and `pwrite` split the operation into tasks executed in a thread pool and return an `IOFuture`:

```python
import cupy as cp
import kvikio

data = cp.empty(10_000_000, dtype=cp.float32)

with kvikio.CuFile("data.bin", "r") as f:
    # Launch two non-blocking reads for different sections
    future1 = f.pread(data[:5_000_000])
    future2 = f.pread(data[5_000_000:], file_offset=5_000_000 * 4)

    # Do other work while IO happens...

    # Wait for completion
    bytes_read1 = future1.get()
    bytes_read2 = future2.get()
```

### Partial Reads and Writes

```python
import cupy as cp
import kvikio

# Read only a portion of a file
buf = cp.empty(1000, dtype=cp.float32)
with kvikio.CuFile("data.bin", "r") as f:
    # Read 1000 floats starting at byte offset 4000
    f.read(buf, size=4000, file_offset=4000)
```

### Host Memory Support

KvikIO handles host memory transparently — no special API needed:

```python
import numpy as np
import kvikio

# Write from host memory
a = np.arange(1_000_000, dtype=np.float32)
with kvikio.CuFile("data.bin", "w") as f:
    f.write(a)

# Read into host memory
b = np.empty_like(a)
with kvikio.CuFile("data.bin", "r") as f:
    f.read(b)
```

### GDS Alignment

GDS works best with page-aligned IO. The GPU page size is 4 KiB (4096 bytes):
- **File offset**: should be a multiple of 4096
- **Transfer size**: should be a multiple of 4096

KvikIO handles unaligned IO correctly but splits it into aligned and unaligned parts, so aligned IO will be faster.

---

## RemoteFile — S3, HTTP, WebHDFS

`kvikio.RemoteFile` reads remote files directly into GPU or host memory.

### HTTP/HTTPS

```python
import cupy as cp
import kvikio

buf = cp.empty(1_000_000, dtype=cp.float32)
with kvikio.RemoteFile.open_http("https://example.com/data.bin") as f:
    print(f.nbytes())  # File size
    f.read(buf)
```

### AWS S3

```python
import cupy as cp
import kvikio

# Using bucket + object name (requires AWS env vars or explicit credentials)
with kvikio.RemoteFile.open_s3("my-bucket", "data/file.bin") as f:
    buf = cp.empty(f.nbytes(), dtype=cp.uint8)
    f.read(buf)

# Using S3 URL
with kvikio.RemoteFile.open_s3_url("s3://my-bucket/data/file.bin") as f:
    buf = cp.empty(f.nbytes(), dtype=cp.uint8)
    f.read(buf)

# Public S3 (no credentials needed)
with kvikio.RemoteFile.open_s3_public("s3://public-bucket/data.bin") as f:
    buf = cp.empty(f.nbytes(), dtype=cp.uint8)
    f.read(buf)

# Presigned URL
with kvikio.RemoteFile.open_s3_presigned_url(presigned_url) as f:
    buf = cp.empty(f.nbytes(), dtype=cp.uint8)
    f.read(buf)
```

AWS credentials come from environment variables (`AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) or can be passed as keyword arguments.

### Auto-Detect Endpoint Type

```python
import kvikio

# KvikIO figures out the protocol from the URL
with kvikio.RemoteFile.open("s3://bucket/object") as f:
    ...

with kvikio.RemoteFile.open("https://example.com/file.bin") as f:
    ...
```

### WebHDFS

```python
import kvikio

with kvikio.RemoteFile.open_webhdfs("http://namenode:9870/path/to/file") as f:
    buf = cp.empty(f.nbytes(), dtype=cp.uint8)
    f.read(buf)
```

### Host Memory with RemoteFile

RemoteFile reads into host memory just as easily:

```python
import numpy as np
import kvikio

with kvikio.RemoteFile.open_http("https://example.com/data.bin") as f:
    buf = np.empty(f.nbytes(), dtype=np.uint8)
    f.read(buf)
```

---

## Zarr Integration

KvikIO provides a GPU store backend for Zarr (version 3.x). This enables reading and writing chunked N-dimensional arrays directly in GPU memory via GDS.

```python
import zarr
from kvikio.zarr import GDSStore

# Enable GPU support in Zarr
zarr.config.enable_gpu()

# Create a GDS-backed store
store = GDSStore(root="data.zarr")

# Create and write a Zarr array (data stays on GPU)
z = zarr.create_array(
    store=store,
    shape=(1000, 1000),
    chunks=(100, 100),
    dtype="float32",
    overwrite=True,
)

# Reading returns CuPy arrays
chunk = z[:100, :100]  # Returns cupy.ndarray
```

Zarr + KvikIO is useful for:
- Climate/weather data (large multi-dimensional arrays)
- Bioinformatics (genomic arrays)
- Any workload using chunked arrays that need GPU processing

Requires: `uv add "zarr==3.*"` in addition to KvikIO 26.06.

---

## Memory-Mapped Files

`kvikio.mmap.Mmap` provides memory-mapped file access with support for both host and device destinations:

```python
from kvikio.mmap import Mmap
import cupy as cp

# Map a file for reading
with Mmap("data.bin", flags="r") as m:
    print(m.file_size())

    # Sequential read into device memory
    buf = cp.empty(1000, dtype=cp.float32)
    m.read(buf, size=4000, offset=0)

    # Parallel read (returns IOFuture)
    future = m.pread(buf, size=4000, offset=0)
    future.get()
```

---

## Runtime Settings

KvikIO behavior is controlled via environment variables or the `kvikio.defaults` API.

### Key Settings

| Setting | Env Variable | Default | Description |
|---------|-------------|---------|-------------|
| Compatibility mode | `KVIKIO_COMPAT_MODE` | `AUTO` | `ON`: POSIX only, `OFF`: GDS only, `AUTO`: try GDS, fall back |
| Thread pool size | `KVIKIO_NTHREADS` | 1 | Number of IO threads for `pread`/`pwrite` |
| Task size | `KVIKIO_TASK_SIZE` | 4 MiB | Max size per parallel IO task |
| GDS threshold | `KVIKIO_GDS_THRESHOLD` | 16 KiB | Min size to use GDS (smaller uses POSIX) |
| Bounce buffer size | `KVIKIO_BOUNCE_BUFFER_SIZE` | 16 MiB | Size of intermediate host buffers per thread |
| Direct IO read | `KVIKIO_AUTO_DIRECT_IO_READ` | off | Opportunistic O_DIRECT for reads |
| Direct IO write | `KVIKIO_AUTO_DIRECT_IO_WRITE` | on | Opportunistic O_DIRECT for writes |

### Programmatic Configuration

```python
import kvikio.defaults

# Query settings
print(kvikio.defaults.get("compat_mode"))
print(kvikio.defaults.get("num_threads"))

# Modify settings at runtime
kvikio.defaults.set({"num_threads": 16, "task_size": 8 * 1024 * 1024})

# Enable direct IO for reads
kvikio.defaults.set({"auto_direct_io_read": True})
```

### Compatibility Mode

When GDS isn't available (missing `libcufile.so`, running in WSL, Docker without `/run/udev`), `AUTO` mode falls back to POSIX IO automatically. This means KvikIO code works everywhere — it just runs faster when GDS is available.

```python
import kvikio.cufile_driver

# Check if GDS is actually being used
print(kvikio.cufile_driver.get("is_gds_available"))
```

### cuFile Driver Configuration

```python
import kvikio.cufile_driver

# Query driver properties
print(kvikio.cufile_driver.get("is_gds_available"))
print(kvikio.cufile_driver.get("major_version"))

# Configure settable properties
kvikio.cufile_driver.set("max_device_cache_size", 1024)

# Use as context manager (auto-reverts on exit)
with kvikio.cufile_driver.set({"poll_mode": True}):
    # poll mode active here
    ...
# poll mode reverted
```

---

## Performance Optimization

### 1. Increase Thread Pool Size

The default of 1 thread is conservative. For large files, increase it:

```python
import kvikio.defaults
kvikio.defaults.set({"num_threads": 16})
```

### 2. Use Non-Blocking IO for Pipelining

Overlap IO with compute by using `pread`/`pwrite`:

```python
import cupy as cp
import kvikio

# Pipeline: read chunk N while processing chunk N-1
chunk_size = 10_000_000
buf_a = cp.empty(chunk_size, dtype=cp.float32)
buf_b = cp.empty(chunk_size, dtype=cp.float32)

with kvikio.CuFile("large_data.bin", "r") as f:
    # Start first read
    future = f.pread(buf_a)
    future.get()

    for offset in range(chunk_size * 4, file_size, chunk_size * 4):
        # Start next read while processing current
        next_future = f.pread(buf_b, file_offset=offset)

        # Process buf_a on GPU (overlaps with IO)
        result = cp.fft.fft(buf_a)

        next_future.get()
        buf_a, buf_b = buf_b, buf_a  # Swap buffers
```

### 3. Align IO to Page Boundaries

GDS performs best with 4 KiB-aligned offsets and sizes:

```python
# Good: aligned offset and size
f.read(buf, size=4096 * 1000, file_offset=4096 * 10)

# Slower: unaligned (KvikIO handles it, but splits into aligned + unaligned parts)
f.read(buf, size=5000, file_offset=100)
```

### 4. Enable Direct IO

For sequential writes and cold reads, Direct IO (bypassing OS page cache) can help:

```python
import kvikio.defaults
kvikio.defaults.set({
    "auto_direct_io_read": True,
    "auto_direct_io_write": True,
})
```

### 5. Tune Task and Bounce Buffer Sizes

For very large files, increase task and bounce buffer sizes:

```python
import kvikio.defaults
kvikio.defaults.set({
    "task_size": 16 * 1024 * 1024,       # 16 MiB per task
    "bounce_buffer_size": 64 * 1024 * 1024,  # 64 MiB bounce buffer
})
```

### 6. Page Cache Utilities

For benchmarking, clear the page cache to measure cold-read performance:

```python
import kvikio

# Check page cache residency
pages_cached, total_pages = kvikio.get_page_cache_info("data.bin")
print(f"{pages_cached}/{total_pages} pages in cache")

# Drop the page cache for a single file (no elevated privileges needed; added in 26.04)
kvikio.drop_file_page_cache("data.bin")

# Drop the system-wide page cache (requires elevated permissions)
kvikio.drop_system_page_cache()
```

`kvikio.clear_page_cache()` is deprecated since 26.04 — use `drop_system_page_cache()` (or the per-file `drop_file_page_cache()`) instead.

---

## Interoperability

### With CuPy

KvikIO reads directly into CuPy arrays — this is the most common usage:

```python
import cupy as cp
import kvikio

data = cp.empty(1_000_000, dtype=cp.float64)
with kvikio.CuFile("data.bin", "r") as f:
    f.read(data)
# data is now a CuPy array, ready for GPU computation
```

### With Numba CUDA

KvikIO works with any buffer supporting the CUDA Array Interface:

```python
from numba import cuda
import kvikio

d_arr = cuda.device_array(1_000_000, dtype="float32")
with kvikio.CuFile("data.bin", "r") as f:
    f.read(d_arr)
```

### With cuDF

For raw binary data that isn't in a tabular format, use KvikIO to load, then convert:

```python
import cupy as cp
import cudf
import kvikio

# Load raw float array, wrap as cuDF Series
buf = cp.empty(1_000_000, dtype=cp.float32)
with kvikio.CuFile("signal.bin", "r") as f:
    f.read(buf)
signal = cudf.Series(buf)
```

For tabular formats (CSV, Parquet, JSON, ORC), use cuDF's own readers — they're optimized for those formats.

### With NumPy (Host Memory)

KvikIO seamlessly handles host memory:

```python
import numpy as np
import kvikio

arr = np.empty(1_000_000, dtype=np.float32)
with kvikio.CuFile("data.bin", "r") as f:
    f.read(arr)
```

---

## Common Patterns

### Save and Load GPU Model Checkpoints

```python
import cupy as cp
import kvikio

def save_checkpoint(arrays: dict[str, cp.ndarray], path: str):
    """Save multiple GPU arrays to a single file."""
    with kvikio.CuFile(path, "w") as f:
        offset = 0
        for arr in arrays.values():
            f.write(arr, file_offset=offset)
            offset += arr.nbytes

def load_checkpoint(shapes_dtypes: dict, path: str) -> dict[str, cp.ndarray]:
    """Load GPU arrays from a checkpoint file."""
    arrays = {}
    with kvikio.CuFile(path, "r") as f:
        offset = 0
        for name, (shape, dtype) in shapes_dtypes.items():
            arr = cp.empty(shape, dtype=dtype)
            f.read(arr, file_offset=offset)
            offset += arr.nbytes
            arrays[name] = arr
    return arrays
```

### Stream Data from S3 into GPU for Processing

```python
import cupy as cp
import kvikio

with kvikio.RemoteFile.open_s3("my-bucket", "large-dataset.bin") as f:
    total_bytes = f.nbytes()
    chunk_size = 100 * 1024 * 1024  # 100 MB chunks
    buf = cp.empty(chunk_size // 4, dtype=cp.float32)

    for offset in range(0, total_bytes, chunk_size):
        size = min(chunk_size, total_bytes - offset)
        f.read(buf[:size // 4], size=size, file_offset=offset)
        # Process chunk on GPU
        result = cp.mean(buf[:size // 4])
```

### Replace Python open() for GPU Workloads

```python
# Before: CPU-bound file IO
import numpy as np
data = np.fromfile("data.bin", dtype=np.float32)
import cupy as cp
gpu_data = cp.asarray(data)  # Extra copy: disk → CPU → GPU

# After: Direct to GPU
import cupy as cp
import kvikio
gpu_data = cp.empty(1_000_000, dtype=cp.float32)
with kvikio.CuFile("data.bin", "r") as f:
    f.read(gpu_data)  # disk → GPU directly (with GDS)
```

---

## Common Pitfalls

1. **Forgetting to set thread pool size** — The default is 1 thread. For large files, `kvikio.defaults.set({"num_threads": 16})` can dramatically improve throughput.

2. **Using KvikIO for structured formats** — Don't use KvikIO to read CSV/Parquet/JSON. Use `cudf.read_csv()`, `cudf.read_parquet()`, etc. KvikIO is for raw binary data.

3. **Not checking GDS availability** — Code works fine without GDS (falls back to POSIX), but won't get the full bandwidth benefit. Check with `kvikio.cufile_driver.get("is_gds_available")`.

4. **Misaligned IO in performance-critical paths** — Use 4 KiB-aligned offsets and sizes for best GDS performance.

5. **Not using context managers** — Always use `with kvikio.CuFile(...)` to ensure files are properly closed and deregistered.

6. **Expecting RemoteFile writes** — `RemoteFile` is read-only. To write to remote storage, write locally first, then upload via the appropriate SDK (boto3 for S3, etc.).

7. **Docker without GDS setup** — In Docker, mount `/run/udev` read-only (`--volume /run/udev:/run/udev:ro`) for GDS to work. Otherwise, KvikIO silently falls back to POSIX.

### `references/numba.md`

# Numba CUDA Reference

The established Numba-CUDA target compiles Python into CUDA kernels with explicit control over
threads, blocks, shared memory, and synchronization. It is now in maintenance mode. For new kernel
projects, evaluate Numba-CUDA-MLIR first; use this reference for existing `numba.cuda` code,
compatibility work, or features not yet available in the MLIR implementation.

> **Full documentation:** https://nvidia.github.io/numba-cuda/
> **New-development path:** https://nvidia.github.io/numba-cuda-mlir/

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Core Concepts: Kernels, Threads, Blocks, Grids](#core-concepts)
3. [Writing CUDA Kernels](#writing-cuda-kernels)
4. [Thread Positioning](#thread-positioning)
5. [Memory Management](#memory-management)
6. [Shared Memory](#shared-memory)
7. [Device Functions](#device-functions)
8. [Atomic Operations](#atomic-operations)
9. [GPU Ufuncs: @vectorize and @guvectorize](#gpu-ufuncs)
10. [GPU Reductions](#gpu-reductions)
11. [Streams and Async Operations](#streams)
12. [Random Number Generation](#random-number-generation)
13. [Cooperative Groups](#cooperative-groups)
14. [Common Patterns for Scientific Computing](#common-patterns)
15. [Performance Optimization](#performance-optimization)
16. [Debugging](#debugging)
17. [Interoperability](#interoperability)
18. [Common Pitfalls](#common-pitfalls)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
uv add "numba-cuda[cu12]==0.30.*"    # For CUDA 12.x (pulls in numba and CUDA components)
uv add "numba-cuda[cu13]==0.30.*"    # For CUDA 13.x
```

The NVIDIA `numba-cuda` package is the out-of-tree implementation of the established
`numba.cuda` target (Numba's built-in target is deprecated). It keeps the `numba.cuda` namespace
and depends on `numba`, so a single install command suffices. NVIDIA limits this implementation to
security and critical fixes through the CUDA 13 lifetime; new feature development targets the
separate `numba-cuda-mlir` package. Follow its migration guide before choosing a compiler for new
code because feature coverage continues to evolve.

**Requirements:** CUDA Toolkit 12 or 13. GPU with Compute Capability >= 5.0 (Maxwell or newer) on CUDA 12, or >= 7.5 (Turing or newer) on CUDA 13.

```python
from numba import cuda

# Verify GPU is available
print(cuda.is_available())   # True if CUDA works
cuda.detect()                # Prints GPU details
```

---

## Core Concepts

CUDA organizes parallel execution in a hierarchy:

```
Grid (of blocks) → Blocks (of threads) → Threads
```

- **Thread**: The smallest unit of execution. Each runs your kernel function.
- **Block**: A group of threads that can share fast on-chip memory and synchronize with each other. Max 1024 threads per block.
- **Grid**: The collection of all blocks for a kernel launch.

A **kernel** is a function that runs on the GPU, launched from the CPU. A **device function** runs on the GPU but is called from other GPU code (not from CPU).

---

## Writing CUDA Kernels

### The @cuda.jit Decorator

```python
from numba import cuda

@cuda.jit
def my_kernel(input_array, output_array):
    i = cuda.grid(1)                    # Get this thread's global index
    if i < input_array.size:            # Bounds check — ALWAYS do this
        output_array[i] = input_array[i] * 2.0
```

**Key parameters for @cuda.jit:**

| Parameter | Purpose |
|-----------|---------|
| `device=True` | Makes this a device function (callable from GPU only, can return values) |
| `fastmath=True` | Enables fast math (fast sqrt, division, FMA, trig/exp/log approximations on float32). Use when IEEE-754 strictness isn't required |
| `max_registers=N` | Limits registers per thread to increase occupancy |
| `cache=True` | Caches compiled kernel to disk |
| `debug=True` | Enables exception checking (slow — for debugging only, pair with `opt=False`) |
| `lineinfo=True` | Source line info for profiling without full debug overhead |

### Launching Kernels

```python
import numpy as np
from numba import cuda

data = np.random.rand(1_000_000).astype(np.float32)
out = np.zeros_like(data)

# Transfer to GPU
d_data = cuda.to_device(data)
d_out = cuda.device_array_like(out)

# Calculate launch configuration
threads_per_block = 256
blocks_per_grid = (data.size + threads_per_block - 1) // threads_per_block

# Launch
my_kernel[blocks_per_grid, threads_per_block](d_data, d_out)

# Get results back
result = d_out.copy_to_host()
```

**Launch syntax:** `kernel[grid_dim, block_dim, stream, dynamic_shared_mem_bytes](...args)`

The 3rd and 4th parameters are optional (stream and dynamic shared memory size in bytes).

### 2D Launch Configuration

```python
@cuda.jit
def kernel_2d(matrix, output):
    x, y = cuda.grid(2)
    if x < matrix.shape[0] and y < matrix.shape[1]:
        output[x, y] = matrix[x, y] * 2.0

threads = (16, 16)
blocks = (
    (matrix.shape[0] + threads[0] - 1) // threads[0],
    (matrix.shape[1] + threads[1] - 1) // threads[1],
)
kernel_2d[blocks, threads](d_matrix, d_output)
```

### Convenience: .forall() for 1D

```python
# Automatically computes grid dimensions for 1D
my_kernel.forall(len(data))(d_data, d_out)
```

### Critical Rules for Kernels

1. **Kernels CANNOT return values.** All output must be written to arrays passed as arguments.
2. **Always check array bounds.** If grid_size > array_size, out-of-bounds threads corrupt memory silently.
3. **Kernel launches are asynchronous.** Use `cuda.synchronize()` before reading results on the CPU.

---

## Thread Positioning

### Intrinsics

| Intrinsic | Description |
|-----------|-------------|
| `cuda.threadIdx.x/y/z` | Thread index within its block |
| `cuda.blockIdx.x/y/z` | Block index within the grid |
| `cuda.blockDim.x/y/z` | Threads per block |
| `cuda.gridDim.x/y/z` | Blocks in the grid |
| `cuda.grid(ndim)` | Absolute position in entire grid (1D → int, 2D/3D → tuple) |
| `cuda.gridsize(ndim)` | Total number of threads in entire grid |

### Grid-Stride Loop Pattern

For processing data larger than the grid, use a grid-stride loop. This decouples grid size from problem size and is essential for reusing RNG states.

```python
@cuda.jit
def process_large(data, out):
    start = cuda.grid(1)
    stride = cuda.gridsize(1)
    for i in range(start, data.shape[0], stride):
        out[i] = data[i] * 2.0
```

---

## Memory Management

### Data Transfer

```python
# Host → Device
d_array = cuda.to_device(numpy_array)                    # Synchronous copy
d_array = cuda.to_device(numpy_array, stream=stream)     # Async copy

# Allocate on device (no copy)
d_array = cuda.device_array(shape=(1000,), dtype=np.float32)
d_array = cuda.device_array_like(numpy_array)

# Device → Host
host_array = d_array.copy_to_host()                      # New array
d_array.copy_to_host(existing_array)                     # Into pre-allocated
d_array.copy_to_host(stream=stream)                      # Async
```

### Memory Types

| Type | API | Use Case |
|------|-----|----------|
| **Device** | `cuda.device_array()`, `cuda.to_device()` | Standard GPU memory |
| **Pinned** | `cuda.pinned_array()`, `cuda.pinned()` context manager | Page-locked host memory — faster transfers |
| **Mapped** | `cuda.mapped_array()` | Accessible from both host and device |
| **Managed** | `cuda.managed_array()` | Unified memory — auto-migrates between host/device (Linux/x86 recommended) |
| **Constant** | `cuda.const.array_like(arr)` | Read-only, cached, set from host |

### Pinned Memory for Fast Transfers

```python
# Allocate pinned host memory (page-locked — faster PCI-e transfers)
with cuda.pinned(host_array):
    d_array = cuda.to_device(host_array, stream=stream)
    # Transfer is faster because the OS can't page this memory out

# Or allocate directly
pinned = cuda.pinned_array(shape=(1000,), dtype=np.float32)
```

### Deallocation Control

```python
with cuda.defer_cleanup():
    # All GPU deallocation deferred here — avoids implicit synchronization
    # Use this in performance-critical sections
    run_many_kernels()
# Cleanup happens here
```

---

## Shared Memory

Shared memory is fast on-chip memory (tens of TB/s bandwidth) shared within a block. It's the key to high-performance kernels — use it to cache data that multiple threads in a block will access.

### Static Shared Memory (size known at compile time)

```python
from numba import cuda, float32

@cuda.jit
def kernel_with_shared(data, output):
    # Allocate shared memory — visible to all threads in this block
    shared = cuda.shared.array(256, dtype=float32)

    tid = cuda.threadIdx.x
    i = cuda.grid(1)

    # Each thread loads one element into shared memory
    if i < data.size:
        shared[tid] = data[i]

    # BARRIER: wait for ALL threads in block to finish loading
    cuda.syncthreads()

    # Now safe to read any element in shared[]
    if i < data.size and tid > 0:
        output[i] = shared[tid] + shared[tid - 1]
```

### Dynamic Shared Memory (size set at launch)

```python
@cuda.jit
def kernel_dynamic_shared(data):
    # size=0 means "use dynamic shared memory"
    dyn = cuda.shared.array(0, dtype=float32)
    tid = cuda.threadIdx.x
    dyn[tid] = data[cuda.grid(1)]
    cuda.syncthreads()
    # ...

# Specify size at launch (4th parameter = bytes)
kernel_dynamic_shared[blocks, threads, stream, 1024](data)  # 1024 bytes of shared mem
```

**Important:** All `cuda.shared.array(0, ...)` calls in the same kernel alias the same memory region. To use multiple dynamic shared arrays, take disjoint slices manually.

### Local Memory (per-thread scratchpad)

```python
@cuda.jit
def kernel_with_local(data):
    # Each thread gets its own private array
    local_buf = cuda.local.array(10, dtype=float32)
    i = cuda.grid(1)
    for j in range(10):
        local_buf[j] = data[i * 10 + j]
    # Process local_buf...
```

---

## Device Functions

Device functions run on the GPU and are called from kernels or other device functions. Unlike kernels, they **can return values**.

```python
@cuda.jit(device=True)
def compute_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

@cuda.jit
def kernel(points, distances):
    i = cuda.grid(1)
    if i < points.shape[0] - 1:
        distances[i] = compute_distance(
            points[i, 0], points[i, 1],
            points[i+1, 0], points[i+1, 1]
        )
```

CPU `@numba.jit` dispatchers are not CUDA device functions. If CPU and GPU paths need the same
formula, keep a small undecorated source function and create explicit CPU (`@njit`) and GPU
(`@cuda.jit(device=True)`) implementations or wrappers; test them against the same fixtures.

---

## Atomic Operations

Atomics ensure thread-safe updates to shared data. All return the **old** value.

```python
cuda.atomic.add(array, index, value)       # +=   (int32, float32, float64)
cuda.atomic.sub(array, index, value)       # -=   (int32, float32, float64)
cuda.atomic.max(array, index, value)       # max  (int/uint 32/64, float 32/64)
cuda.atomic.min(array, index, value)       # min  (same types)
cuda.atomic.nanmax(array, index, value)    # max ignoring NaN
cuda.atomic.nanmin(array, index, value)    # min ignoring NaN
cuda.atomic.and_(array, index, value)      # &=   (int/uint 32/64)
cuda.atomic.or_(array, index, value)       # |=   (int/uint 32/64)
cuda.atomic.xor(array, index, value)       # ^=   (int/uint 32/64)
cuda.atomic.exch(array, index, value)      # exchange
cuda.atomic.cas(array, index, old, value)  # compare-and-swap
```

Multi-dimensional indexing works via tuples: `cuda.atomic.add(result, (row, col), value)`

### Example: Histogram

```python
@cuda.jit
def histogram(data, bins, min_value, max_value):
    i = cuda.grid(1)
    if i < data.size:
        value = data[i]
        n_bins = bins.size
        if min_value <= value <= max_value:
            bin_idx = int((value - min_value) * n_bins / (max_value - min_value))
            if bin_idx == n_bins:  # Include the rightmost edge.
                bin_idx = n_bins - 1
            cuda.atomic.add(bins, bin_idx, 1)
```

Validate `max_value > min_value` on the host before launch. For production histograms, prefer
CuPy/CUB unless a custom binning rule is required.

---

## GPU Ufuncs

### @vectorize — Element-wise Operations on GPU

The simplest way to run element-wise operations on GPU. Write a scalar function, Numba broadcasts it over arrays automatically.

```python
from numba import vectorize, float32, float64
import math

@vectorize([float32(float32, float32),
            float64(float64, float64)],
           target='cuda')
def gpu_hypot(x, y):
    return math.sqrt(x**2 + y**2)

# Usage — just call it like a NumPy ufunc
result = gpu_hypot(array_x, array_y)

# Pass device arrays to avoid transfers
d_x = cuda.to_device(x)
d_y = cuda.to_device(y)
d_result = gpu_hypot(d_x, d_y)
```

### @guvectorize — Generalized Ufuncs

For operations on sub-arrays (not just scalars). Uses NumPy's generalized ufunc signature.

```python
from numba import guvectorize, float32

@guvectorize([float32[:,:], float32[:,:], float32[:,:]],
             '(m,n),(n,p)->(m,p)', target='cuda')
def gpu_matmul(A, B, C):
    for i in range(A.shape[0]):
        for j in range(B.shape[1]):
            total = 0.0
            for k in range(A.shape[1]):
                total += A[i, k] * B[k, j]
            C[i, j] = total
```

---

## GPU Reductions

```python
from numba import cuda

# Define reduction operation
sum_reduce = cuda.reduce(lambda a, b: a + b)

# Use it
result = sum_reduce(array)                    # Full reduction
result = sum_reduce(array, init=0)            # With initial value
sum_reduce(array, res=device_result)          # Write to device array (no D→H copy)
sum_reduce(array, stream=stream)              # Async
```

Custom reduction:

```python
@cuda.reduce
def max_reduce(a, b):
    return a if a > b else b

maximum = max_reduce(data_array)
```

---

## Streams

Streams enable overlapping computation with data transfer and running multiple kernels concurrently.

```python
stream = cuda.stream()

# Async transfer → kernel → transfer back
d_data = cuda.to_device(host_data, stream=stream)
my_kernel[blocks, threads, stream](d_data, d_out)
result = d_out.copy_to_host(stream=stream)
stream.synchronize()  # Wait for everything on this stream

# Context manager that auto-synchronizes
with stream.auto_synchronize():
    d_data = cuda.to_device(host_data, stream=stream)
    my_kernel[blocks, threads, stream](d_data, d_out)
    result = d_out.copy_to_host(stream=stream)
# Synchronizes here automatically
```

### Pipeline Pattern (overlap transfer and compute)

```python
stream1 = cuda.stream()
stream2 = cuda.stream()

# Chunk 1: transfer on stream1
d_chunk1 = cuda.to_device(data[:half], stream=stream1)
# Chunk 2: transfer on stream2 (overlaps with stream1 transfer)
d_chunk2 = cuda.to_device(data[half:], stream=stream2)

# Process chunk1 on stream1
kernel[blocks, threads, stream1](d_chunk1, d_out1)
# Process chunk2 on stream2 (overlaps with stream1 compute)
kernel[blocks, threads, stream2](d_chunk2, d_out2)

cuda.synchronize()  # Wait for all streams
```

---

## Random Number Generation

Numba provides GPU-native random number generation using the xoroshiro128+ algorithm.

```python
from numba import cuda
from numba.cuda.random import (
    create_xoroshiro128p_states,
    xoroshiro128p_uniform_float32,
    xoroshiro128p_uniform_float64,
    xoroshiro128p_normal_float32,
    xoroshiro128p_normal_float64,
)

# Create RNG states — one per thread
n_threads = 256 * 128
rng_states = create_xoroshiro128p_states(n_threads, seed=42)

@cuda.jit
def monte_carlo_pi(rng_states, iterations, out):
    gid = cuda.grid(1)
    if gid < out.size:
        inside = 0
        for _ in range(iterations):
            x = xoroshiro128p_uniform_float32(rng_states, gid)
            y = xoroshiro128p_uniform_float32(rng_states, gid)
            if x**2 + y**2 <= 1.0:
                inside += 1
        out[gid] = inside / iterations * 4.0

monte_carlo_pi[128, 256](rng_states, 10000, d_out)
```

**Tip:** RNG states consume memory proportional to thread count. Use grid-stride loops to limit the number of states needed for large problems.

---

## Cooperative Groups

For algorithms requiring synchronization across ALL blocks in a grid (not just within a single block).

```python
@cuda.jit
def iterative_kernel(M):
    col = cuda.grid(1)
    g = cuda.cg.this_grid()  # Get grid group

    for row in range(1, M.shape[0]):
        M[row, col] = M[row - 1, col] + 1
        g.sync()  # Global barrier — all blocks wait here

# Query max grid size for cooperative launch
overload = iterative_kernel.overloads[signature]
max_blocks = overload.max_cooperative_grid_blocks(block_dim)
```

Cooperative launches are triggered automatically when `g.sync()` is detected. The grid must not exceed `max_cooperative_grid_blocks()`.

---

## Common Patterns

### Tiled Matrix Multiplication with Shared Memory

This is the canonical example of shared memory optimization — tiles of A and B are loaded into fast shared memory to reduce slow global memory accesses.

```python
from numba import cuda, float32
import numpy as np

TPB = 16  # Tile/block size

@cuda.jit
def matmul_shared(A, B, C):
    sA = cuda.shared.array((TPB, TPB), dtype=float32)
    sB = cuda.shared.array((TPB, TPB), dtype=float32)

    x, y = cuda.grid(2)
    tx, ty = cuda.threadIdx.x, cuda.threadIdx.y

    tmp = float32(0.0)
    n_tiles = (A.shape[1] + TPB - 1) // TPB
    for tile in range(n_tiles):
        # Load tile into shared memory (with bounds check)
        col = tx + tile * TPB
        row = ty + tile * TPB
        sA[ty, tx] = A[y, col] if (y < A.shape[0] and col < A.shape[1]) else 0
        sB[ty, tx] = B[row, x] if (x < B.shape[1] and row < B.shape[0]) else 0
        cuda.syncthreads()

        # Compute partial dot product from this tile
        for k in range(TPB):
            tmp += sA[ty, k] * sB[k, tx]
        cuda.syncthreads()

    if y < C.shape[0] and x < C.shape[1]:
        C[y, x] = tmp
```

### Block-Local Inclusive Prefix Sum

```python
@cuda.jit
def block_inclusive_scan(data, output):
    shared = cuda.shared.array(256, dtype=float32)
    tid = cuda.threadIdx.x
    i = cuda.grid(1)

    shared[tid] = data[i] if i < data.size else 0
    cuda.syncthreads()

    # Hillis-Steele scan within one block. Two barriers prevent read/write races.
    offset = 1
    while offset < cuda.blockDim.x:
        addend = float32(0.0)
        if tid >= offset:
            addend = shared[tid - offset]
        cuda.syncthreads()
        if tid >= offset:
            shared[tid] += addend
        cuda.syncthreads()
        offset *= 2

    if i < data.size:
        output[i] = shared[tid]
```

This computes an independent scan per block, not a whole-array scan. A complete multi-block scan
also scans block totals and adds block offsets. Prefer `cupy.cumsum()`/CUB unless a custom scan
operator is required.

### Shared Memory Reduction

```python
@cuda.jit
def block_reduce_sum(data, partial_sums):
    shared = cuda.shared.array(256, dtype=float32)
    tid = cuda.threadIdx.x
    i = cuda.grid(1)

    shared[tid] = data[i] if i < data.size else 0.0
    cuda.syncthreads()

    # Tree reduction in shared memory
    s = cuda.blockDim.x // 2
    while s > 0:
        if tid < s:
            shared[tid] += shared[tid + s]
        s //= 2
        cuda.syncthreads()

    # Thread 0 of each block writes the block's sum
    if tid == 0:
        partial_sums[cuda.blockIdx.x] = shared[0]
```

### Stencil / Neighbor Access Pattern

```python
@cuda.jit
def stencil_1d(data, output, radius):
    shared = cuda.shared.array(288, dtype=float32)  # blockDim + 2*radius
    tid = cuda.threadIdx.x
    i = cuda.grid(1)

    # Load center + halo into shared memory
    shared[tid + radius] = data[i] if i < data.size else 0
    if tid < radius:
        shared[tid] = data[i - radius] if i >= radius else 0
        shared[tid + cuda.blockDim.x + radius] = (
            data[i + cuda.blockDim.x] if i + cuda.blockDim.x < data.size else 0
        )
    cuda.syncthreads()

    if i < data.size:
        total = float32(0.0)
        for j in range(-radius, radius + 1):
            total += shared[tid + radius + j]
        output[i] = total / (2 * radius + 1)
```

---

## Performance Optimization

### GPU-Specific Tips

1. **Minimize host-device transfers.** Use `cuda.to_device()` and keep data on GPU across multiple
kernel calls. Measure on the target system; interconnect and device-memory bandwidth vary widely.

2. **Use shared memory** for data reused across threads in a block when profiling shows global
memory traffic is limiting performance. Shared memory is finite and can reduce occupancy.

3. **Coalesce memory accesses.** Adjacent threads (consecutive `threadIdx.x`) should access adjacent memory locations. This lets the hardware combine accesses into fewer wide transactions.

4. **Choose block size for occupancy.** 128-256 threads/block for 1D, (16,16) or (32,32) for 2D. Too few threads underutilizes the GPU; too many may limit registers/shared memory per thread.

5. **Use `fastmath=True`** when IEEE-754 strictness isn't required. Enables FMA, fast sqrt/division, and faster trig/exp/log for float32.

6. **Prefer float32 over float64** when precision and stability requirements allow. The throughput
ratio is architecture-specific, so benchmark the target GPU.

7. **Use streams** to overlap data transfer with computation.

8. **Use `cuda.defer_cleanup()`** in performance-critical sections to prevent implicit synchronization from memory deallocation.

9. **Limit register usage** with `max_registers` parameter when occupancy is the bottleneck.

10. **Use grid-stride loops** to decouple grid size from problem size and improve flexibility.

### What Not To Do

- Don't use Python objects, strings, or dynamic memory allocation inside kernels — Numba CUDA supports a restricted Python subset.
- Don't put `syncthreads()` inside divergent branches — if threads in a block take different paths through a barrier, behavior is undefined (deadlock or corruption).
- Don't forget `cuda.synchronize()` before reading results on CPU — kernel launches are async.
- Don't assume a custom kernel helps small arrays. Measure launch and transfer overhead on the
  target system and batch or fuse work when overhead dominates.

---

## Debugging

### CUDA Simulator

Run CUDA code on CPU for debugging — supports `print()` and `pdb` inside kernels.

```bash
export NUMBA_ENABLE_CUDASIM=1
python your_script.py
```

The simulator runs kernels one block at a time, spawning one thread per CUDA thread. Supports shared/local/constant memory, atomics, and `syncthreads()`.

### Debug a Specific Thread

```python
@cuda.jit
def debug_kernel(data, out):
    i = cuda.grid(1)
    if cuda.threadIdx.x == 0 and cuda.blockIdx.x == 0:
        # Only thread (0,0) hits the debugger
        from pdb import set_trace; set_trace()
    if i < data.size:
        out[i] = data[i] * 2
```

### On-Device Debug Mode

```python
@cuda.jit(debug=True, opt=False)
def kernel_debug(data):
    # Enables CUDA exception checking — much slower but catches errors
    ...
```

---

## Interoperability

Numba supports the **CUDA Array Interface** (version 3) — any object exposing `__cuda_array_interface__` can be passed directly to Numba kernels with zero copy.

### With CuPy

```python
import cupy as cp
from numba import cuda

@cuda.jit
def add_kernel(x, y, out):
    i = cuda.grid(1)
    if i < x.shape[0]:
        out[i] = x[i] + y[i]

# CuPy arrays work directly — zero copy
a = cp.arange(1000, dtype=cp.float32)
b = cp.ones(1000, dtype=cp.float32)
out = cp.zeros(1000, dtype=cp.float32)
add_kernel[4, 256](a, b, out)
```

### With PyTorch

```python
import torch
from numba import cuda

t = torch.cuda.FloatTensor([1, 2, 3])
d_array = cuda.as_cuda_array(t)  # Zero-copy Numba view of PyTorch tensor
```

### Checking GPU Arrays

```python
cuda.is_cuda_array(obj)       # True if obj has __cuda_array_interface__
cuda.as_cuda_array(obj)       # Wrap as Numba device array (zero copy)
```

**Compatible libraries:** CuPy, PyTorch, JAX, PyCUDA, RAPIDS (cuDF, cuML), PyArrow, mpi4py, NVIDIA DALI.

---

## Common Pitfalls

1. **Forgetting bounds checks.** If `blocks * threads > array_size`, out-of-bounds threads corrupt memory silently. Always: `if i < array.size`.

2. **Trying to return values from kernels.** Kernels cannot return — write to output arrays instead. Return values are silently discarded.

3. **Implicit synchronous transfers.** Passing host (NumPy) arrays directly to kernels triggers synchronous copy-back. Use explicit `cuda.to_device()` / `copy_to_host()`.

4. **Shared memory size must be a compile-time constant** for static allocation. Use dynamic shared memory (size=0) for runtime-determined sizes.

5. **Dynamic shared memory aliasing.** All `cuda.shared.array(0, ...)` in the same kernel share the same memory. Slice manually for multiple arrays.

6. **`syncthreads()` in divergent branches.** All threads in a block must reach the same `syncthreads()` call. Divergent paths → undefined behavior.

7. **Atomic operation type restrictions.** `atomic.add` supports int32, float32, float64. Bitwise atomics only work on integer types.

8. **Forgetting `cuda.synchronize()`.** Kernel launches are async. Reading host-side results before sync gives stale/incomplete data.

9. **Unsupported Python features in kernels.** No dynamic allocation, no Python objects, no string operations, no exceptions (unless debug mode). Stick to numeric types and math.

10. **Using float64 on consumer GPUs.** Consumer NVIDIA GPUs (GeForce) have heavily throttled float64 throughput (often 1/32 of float32). Use float32 unless you need the precision.

### `references/raft.md`

# RAFT (pylibraft) Reference

RAFT (Reusable Accelerated Functions and Tools) is a RAPIDS library of GPU-accelerated building blocks for machine learning and information retrieval. It provides low-level primitives — sparse eigensolvers, device memory management, random graph generation, and multi-GPU communication — that higher-level libraries like cuML and cuGraph are built on. Use `pylibraft` directly when you need these primitives without the overhead of a full ML framework.

> **Full documentation:** https://docs.rapids.ai/api/raft/stable/
> **Note:** Vector search and clustering algorithms have been migrated to [cuVS](https://github.com/rapidsai/cuvs). Use cuVS for nearest neighbor search, not RAFT.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Core Concepts](#core-concepts)
3. [Device Memory Management](#device-memory-management)
4. [Sparse Eigenvalue Problems](#sparse-eigenvalue-problems)
5. [Random Graph Generation](#random-graph-generation)
6. [Multi-Node Multi-GPU with raft-dask](#multi-node-multi-gpu-with-raft-dask)
7. [Interoperability](#interoperability)
8. [Performance Tips](#performance-tips)
9. [Common Pitfalls](#common-pitfalls)

---

## Installation and Setup

Use `uv add` in standalone examples; follow the user's existing project package manager when one
is already configured.

```bash
# pylibraft (core library)
uv add --extra-index-url=https://pypi.nvidia.com "pylibraft-cu12==26.6.*"   # For CUDA 12.x
uv add --extra-index-url=https://pypi.nvidia.com "pylibraft-cu13==26.6.*"   # For CUDA 13.x

# raft-dask (multi-node multi-GPU support, optional)
uv add --extra-index-url=https://pypi.nvidia.com "raft-dask-cu12==26.6.*"   # For CUDA 12.x
uv add --extra-index-url=https://pypi.nvidia.com "raft-dask-cu13==26.6.*"   # For CUDA 13.x
```

pylibraft and raft-dask wheels (including the companion `libraft` wheel) are also published directly to PyPI, so the extra index is optional.

Verify:
```python
import pylibraft
from pylibraft.common import DeviceResources
handle = DeviceResources()
handle.sync()
print("pylibraft is working")
```

---

## Core Concepts

### DeviceResources (CUDA Resource Handle)

`DeviceResources` manages expensive CUDA resources (streams, stream pools, library handles for cuBLAS/cuSOLVER). Create one and reuse it across multiple RAFT calls to avoid repeated allocation overhead.

```python
from pylibraft.common import DeviceResources, Stream

# Default stream
handle = DeviceResources()

# Custom stream
stream = Stream()
handle = DeviceResources(stream)

# With a CuPy stream
import cupy
cupy_stream = cupy.cuda.Stream()
handle = DeviceResources(stream=cupy_stream.ptr)

# Always sync before reading results
handle.sync()
```

RAFT functions are asynchronous by default — they return immediately and work continues on the GPU. You must call `handle.sync()` before accessing output data on the CPU. If you don't pass a `handle`, RAFT allocates temporary resources internally and synchronizes before returning (convenient but slower for repeated calls).

### Stream

A thin wrapper around `cudaStream_t` for ordering GPU operations:

```python
from pylibraft.common import Stream

stream = Stream()
stream.sync()                  # Synchronize all work on this stream
ptr = stream.get_ptr()         # Get the raw cudaStream_t pointer (uintptr_t)
```

---

## Device Memory Management

### device_ndarray

`device_ndarray` is RAFT's lightweight GPU array type. It implements `__cuda_array_interface__`, making it interoperable with CuPy, Numba, PyTorch, and other GPU libraries.

```python
from pylibraft.common import device_ndarray
import numpy as np

# Allocate empty GPU array
gpu_arr = device_ndarray.empty((1000, 50), dtype=np.float32)

# From a NumPy array (copies data to GPU)
cpu_data = np.random.rand(1000, 50).astype(np.float32)
gpu_arr = device_ndarray(cpu_data)

# Back to NumPy (copies data to CPU)
result = gpu_arr.copy_to_host()

# Properties
print(gpu_arr.shape)          # (1000, 50)
print(gpu_arr.dtype)          # float32
print(gpu_arr.c_contiguous)   # True (row-major)
print(gpu_arr.f_contiguous)   # False
```

### Configuring Output Types

You can configure all RAFT compute APIs to return CuPy arrays or PyTorch tensors instead of `device_ndarray`:

```python
import pylibraft.config

pylibraft.config.set_output_as("cupy")    # All APIs return cupy arrays
pylibraft.config.set_output_as("torch")   # All APIs return torch tensors

# Custom conversion
pylibraft.config.set_output_as(lambda arr: arr.copy_to_host())  # Return numpy
```

---

## Sparse Eigenvalue Problems

### eigsh — Sparse Symmetric Eigenvalue Decomposition

GPU-accelerated Lanczos method for finding eigenvalues/eigenvectors of large sparse symmetric matrices. Drop-in replacement for `scipy.sparse.linalg.eigsh`.

```python
import cupy as cp
import cupyx.scipy.sparse as sp
from pylibraft.sparse.linalg import eigsh
from pylibraft.common import DeviceResources

# Create a sparse symmetric matrix (CSR format)
n = 10000
density = 0.01
A = sp.random(n, n, density=density, dtype=cp.float32, format='csr')
A = A + A.T  # Make symmetric

# Find 6 largest eigenvalues
handle = DeviceResources()
eigenvalues, eigenvectors = eigsh(A, k=6, which='LM', handle=handle)
handle.sync()

print(f"Eigenvalues shape: {eigenvalues.shape}")      # (6,)
print(f"Eigenvectors shape: {eigenvectors.shape}")     # (10000, 6)
```

**Parameters:**
- `A` — Sparse symmetric CSR matrix (`cupyx.scipy.sparse.csr_matrix`)
- `k` — Number of eigenvalues to compute (default: 6). Must be `1 <= k < n`
- `which` — Which eigenvalues:
  - `'LM'`: largest in magnitude (default)
  - `'LA'`: largest algebraic
  - `'SA'`: smallest algebraic
  - `'SM'`: smallest in magnitude
- `v0` — Starting vector (optional, random if None)
- `ncv` — Number of Lanczos vectors. Must be `k + 1 < ncv < n`
- `maxiter` — Maximum iterations
- `tol` — Convergence tolerance (0 = machine precision)
- `seed` — Random seed for reproducibility
- `handle` — Optional `DeviceResources` handle

**When to use:** Spectral methods (spectral clustering, graph partitioning, PageRank-like computations), dimensionality reduction on sparse data, physics simulations with large sparse Hamiltonians, structural analysis (vibration modes).

---

## Random Graph Generation

### rmat — R-MAT Graph Generation

Generates random graphs using the Recursive Matrix (R-MAT) model, commonly used for benchmarking graph algorithms with realistic structure (power-law degree distribution, community structure).

```python
import cupy as cp
from pylibraft.random import rmat
from pylibraft.common import DeviceResources

n_edges = 100000
r_scale = 16          # log2 of source node count (2^16 = 65536 nodes)
c_scale = 16          # log2 of destination node count
theta_len = max(r_scale, c_scale) * 4

# Output: edge list as (src, dst) pairs
out = cp.empty((n_edges, 2), dtype=cp.int32)
# Probability distribution at each R-MAT level
theta = cp.random.random_sample(theta_len, dtype=cp.float32)

handle = DeviceResources()
rmat(out, theta, r_scale, c_scale, seed=42, handle=handle)
handle.sync()

print(f"Generated {n_edges} edges")
print(f"Edge list shape: {out.shape}")       # (100000, 2)
print(f"Sample edges:\n{out[:5].get()}")     # First 5 edges on CPU
```

**When to use:** Benchmarking graph algorithms, generating synthetic social/web graphs, testing graph processing pipelines at scale.

---

## Multi-Node Multi-GPU with raft-dask

`raft-dask` provides a `Comms` class for managing NCCL and UCX communication across workers in a Dask cluster. This is the foundation for distributed GPU computing in RAPIDS.

```python
from dask_cuda import LocalCUDACluster
from dask.distributed import Client
from raft_dask.common import Comms, local_handle

# Set up a local multi-GPU Dask cluster
cluster = LocalCUDACluster()
client = Client(cluster)

def run_on_gpu(sessionId):
    handle = local_handle(sessionId)
    # Use handle with RAFT or cuML algorithms
    return "done"

# Initialize multi-GPU communication
comms = Comms(client=client)
comms.init()

# Submit work to each GPU worker
futures = [
    client.submit(run_on_gpu, comms.sessionId, workers=[w], pure=False)
    for w in comms.worker_addresses
]

# Wait for results
from dask.distributed import wait
wait(futures, timeout=60)

# Clean up
comms.destroy()
client.close()
cluster.close()
```

**Comms parameters:**
- `comms_p2p` (bool) — Enable UCX peer-to-peer communication (default: False). Enable for algorithms that need direct GPU-to-GPU transfers.
- `client` — Dask distributed client
- `verbose` (bool) — Enable verbose logging
- `streams_per_handle` (int) — Number of CUDA streams per handle

---

## Interoperability

RAFT's `device_ndarray` implements `__cuda_array_interface__`, enabling zero-copy sharing with other GPU libraries:

```python
import cupy as cp
import torch
from pylibraft.common import device_ndarray

# pylibraft -> CuPy (zero-copy)
raft_arr = device_ndarray(np.random.rand(100).astype(np.float32))
cupy_arr = cp.asarray(raft_arr)

# pylibraft -> PyTorch (zero-copy)
torch_tensor = torch.as_tensor(raft_arr, device='cuda')

# CuPy -> pylibraft (pass directly — RAFT APIs accept __cuda_array_interface__)
cupy_data = cp.random.rand(100, 50, dtype=cp.float32)
# Can pass cupy_data directly to pylibraft functions like eigsh()

# pylibraft -> NumPy (copy)
numpy_arr = raft_arr.copy_to_host()
```

RAFT functions accept any object implementing `__cuda_array_interface__` as input — you don't need to convert to `device_ndarray` first. This means CuPy arrays, Numba device arrays, PyTorch CUDA tensors, and cuDF columns all work directly.

---

## Performance Tips

1. **Reuse DeviceResources.** Creating a `DeviceResources` allocates CUDA library handles (cuBLAS, cuSOLVER). Create once, pass to all calls.

2. **Batch your syncs.** RAFT calls are asynchronous. Queue multiple operations before calling `handle.sync()` rather than syncing after each one.

3. **Use float32.** GPU throughput for float32 is 2x-32x higher than float64. Only use float64 when precision demands it.

4. **Pre-allocate outputs.** Many RAFT functions accept an `out` parameter. Pre-allocating avoids repeated GPU memory allocation.

5. **Keep data on GPU.** RAFT interoperates with CuPy, cuDF, and cuML via `__cuda_array_interface__`. Pass GPU arrays directly between libraries instead of round-tripping through CPU.

---

## Common Pitfalls

- **Forgetting to sync.** RAFT operations are asynchronous. Reading results without calling `handle.sync()` gives undefined/stale data. If you omit the `handle` parameter, RAFT syncs internally (safe but slower).

- **Using RAFT for vector search.** Vector search (k-NN, IVFPQ, CAGRA, etc.) has been migrated to [cuVS](https://github.com/rapidsai/cuvs). RAFT no longer maintains these algorithms.

- **Wrong sparse format.** `eigsh()` requires `cupyx.scipy.sparse.csr_matrix`. Other sparse formats (COO, CSC) must be converted first.

- **Non-symmetric matrix with eigsh.** `eigsh` is for real symmetric / Hermitian matrices only. For general eigenvalue problems, you'll need a different solver.

- **dtype mismatch.** RAFT functions are picky about dtypes. Use `float32` or `float64` explicitly — don't rely on implicit conversion.

### `references/warp.md`

# NVIDIA Warp Reference — GPU Simulation & Spatial Computing

NVIDIA Warp is a Python framework for writing high-performance simulation and graphics code. It JIT-compiles Python functions decorated with `@wp.kernel` into efficient C++/CUDA code that runs on CPU or GPU. Warp is designed specifically for spatial computing — physics simulation, robotics, geometry processing, and differentiable programming — with rich built-in types (vectors, matrices, quaternions, transforms) and spatial primitives (meshes, volumes, hash grids, BVH).

Unlike Numba CUDA (which gives you raw thread/block control) or CuPy (which replaces NumPy ops), Warp provides a higher-level programming model with built-in support for differentiable simulation, spatial queries, and tile-based cooperative operations.

## Table of Contents

1. [Installation](#installation)
2. [When to Use Warp vs Other Libraries](#when-to-use-warp-vs-other-libraries)
3. [Kernels and Launch](#kernels-and-launch)
4. [Arrays](#arrays)
5. [Data Types](#data-types)
6. [Spatial Computing Primitives](#spatial-computing-primitives)
7. [Tile-Based Programming](#tile-based-programming)
8. [Differentiability](#differentiability)
9. [Streams, Events, and CUDA Graphs](#streams-events-and-cuda-graphs)
10. [Random Number Generation](#random-number-generation)
11. [Interoperability](#interoperability)
12. [Performance Optimization](#performance-optimization)
13. [Common Patterns](#common-patterns)
14. [Common Pitfalls](#common-pitfalls)

---

## Installation

```bash
uv add "warp-lang==1.15.*"              # PyPI wheels built with the CUDA 12.9 runtime
# uv add "warp-lang[examples]==1.15.*"  # Includes USD and example dependencies
```

Requires Python >= 3.10 and an NVIDIA driver >= 525 for the CUDA 12 wheels. CUDA 13.0 builds (driver >= 580) are published on the project's GitHub Releases page rather than PyPI.

Verify installation:

```python
import warp as wp
wp.init()
# Prints device info, CUDA version, kernel cache location
```

---

## When to Use Warp vs Other Libraries

| Use Case | Best Choice | Why |
|----------|------------|-----|
| High-level rigid-body / robotics simulation | **Newton** | Maintained engine built on Warp; successor to removed `warp.sim` |
| Custom physics kernels (particles, cloth, fluids) | **Warp** | Spatial primitives, autodiff, and explicit kernels |
| Geometry processing (meshes, ray casting, SDFs) | **Warp** | Native mesh/volume/BVH types, spatial queries |
| Differentiable simulation for ML training | **Warp** | Automatic forward/backward AD, PyTorch/JAX integration |
| Robotics (kinematics, dynamics, control) | **Warp** | Transforms, quaternions, spatial vectors built-in |
| NumPy array math (FFT, linear algebra, sorting) | **CuPy** | Drop-in NumPy replacement, wraps cuBLAS/cuFFT |
| General custom CUDA kernels with explicit SIMT control | **Numba-CUDA-MLIR** or **Numba-CUDA** | Direct CUDA programming model and shared memory |
| Data wrangling / ETL on tabular data | **cuDF** | pandas API on GPU |
| ML training (sklearn-style) | **cuML** | scikit-learn API on GPU |

Warp and Numba both compile Python to CUDA, but serve different niches:
- **Warp** excels at simulation/spatial workloads with its rich type system (vec3, quat, transform, mesh, volume) and automatic differentiation
- **Numba** excels at raw CUDA programming where you need explicit thread/block control, shared memory management, and atomic operations on arbitrary data

Warp's former ready-made physics engine module `warp.sim` was removed in Warp 1.10. Use the
separate Newton library, built on Warp, for maintained high-level simulation APIs. Warp itself
remains the tool for writing custom kernels and domain primitives.

---

## Kernels and Launch

### Defining Kernels

```python
import warp as wp

@wp.kernel
def compute_forces(positions: wp.array(dtype=wp.vec3),
                   velocities: wp.array(dtype=wp.vec3),
                   forces: wp.array(dtype=wp.vec3),
                   dt: float):
    tid = wp.tid()

    pos = positions[tid]
    vel = velocities[tid]

    # Gravity
    force = wp.vec3(0.0, -9.81, 0.0)

    forces[tid] = force
```

### Launching Kernels

```python
# 1D launch
wp.launch(kernel=compute_forces,
          dim=num_particles,
          inputs=[positions, velocities, forces, 0.01],
          device="cuda")

# 2D launch (e.g., image processing)
wp.launch(kernel=compute_image, dim=(1024, 1024), inputs=[img], device="cuda")

# 3D launch
wp.launch(kernel=compute_field, dim=(nx, ny, nz), inputs=[field], device="cuda")
```

Inside 2D/3D kernels, retrieve indices with:

```python
i, j = wp.tid()       # 2D
i, j, k = wp.tid()    # 3D
```

### User Functions

```python
@wp.func
def spring_force(x0: wp.vec3, x1: wp.vec3, rest_length: float, stiffness: float):
    delta = x1 - x0
    length = wp.length(delta)
    direction = delta / length
    return stiffness * (length - rest_length) * direction
```

Functions can be called from kernels, support overloading, and can return multiple values.

### User Structs

```python
@wp.struct
class Particle:
    pos: wp.vec3
    vel: wp.vec3
    mass: float
    active: int
```

---

## Arrays

Warp arrays are typed, device-aware containers (1D to 4D):

```python
# Allocate
positions = wp.zeros(n, dtype=wp.vec3, device="cuda")
grid = wp.empty(shape=(nx, ny, nz), dtype=float, device="cuda")

# From NumPy
import numpy as np
data = np.random.rand(1000, 3).astype(np.float32)
wp_data = wp.from_numpy(data, dtype=wp.vec3, device="cuda")

# Back to NumPy (synchronizes GPU automatically)
np_data = wp_data.numpy()

# Array math operators
c = 2.0 * a + b   # Element-wise, GPU-accelerated
c *= 10.0          # In-place
```

Type aliases for kernel signatures: `wp.array2d`, `wp.array3d`, `wp.array4d`.

---

## Data Types

### Scalars
`bool`, `int8`, `uint8`, `int16`, `uint16`, `int32` (alias: `int`), `uint32`, `int64`, `uint64`, `float16`, `float32` (alias: `float`), `float64`

### Vectors
`vec2`, `vec3`, `vec4` — float32 by default. Variants for every scalar type: `vec3f`, `vec3d`, `vec3h`, `vec3i`, etc.

```python
v = wp.vec3(1.0, 2.0, 3.0)
length = wp.length(v)
normalized = wp.normalize(v)
d = wp.dot(a, b)
c = wp.cross(a, b)
```

### Matrices
`mat22`, `mat33`, `mat44` — row-major. Variants: `mat33f`, `mat33d`, `mat33h`.

```python
m = wp.mat33(1.0, 0.0, 0.0,
             0.0, 1.0, 0.0,
             0.0, 0.0, 1.0)
inv = wp.inverse(m)
det = wp.determinant(m)
result = m * v  # Matrix-vector multiply
```

### Quaternions
`quat` (i, j, k, w layout where w is real part)

```python
q = wp.quat_from_axis_angle(wp.vec3(0.0, 1.0, 0.0), 3.14159 / 2.0)
rotated = wp.quat_rotate(q, wp.vec3(1.0, 0.0, 0.0))
q_combined = wp.mul(q1, q2)  # Compose rotations
```

### Transforms
`transform` — 7D (position vec3 + quaternion)

```python
t = wp.transform(wp.vec3(1.0, 2.0, 3.0), wp.quat_identity())
world_point = wp.transform_point(t, local_point)
world_dir = wp.transform_vector(t, local_dir)
```

### Spatial Vectors and Matrices
`spatial_vector` (6D), `spatial_matrix` (6x6) — for rigid body dynamics.

---

## Spatial Computing Primitives

### Meshes (`wp.Mesh`)

Triangle mesh with BVH for fast ray casting and closest-point queries:

```python
# Create mesh from vertices and triangle indices
mesh = wp.Mesh(points=vertices,     # wp.array(dtype=wp.vec3)
               indices=triangles)   # wp.array(dtype=int), flattened (v0,v1,v2,...)

# Query in kernel
@wp.kernel
def raycast(mesh_id: wp.uint64, origins: wp.array(dtype=wp.vec3),
            directions: wp.array(dtype=wp.vec3), hits: wp.array(dtype=float)):
    tid = wp.tid()
    query = wp.mesh_query_ray(mesh_id, origins[tid], directions[tid], 1000.0)
    if query.result:
        hits[tid] = query.t  # Hit distance

wp.launch(raycast, dim=n, inputs=[mesh.id, origins, dirs, hits])

# Update vertex positions (topology stays fixed)
mesh.points = new_positions
mesh.refit()  # Rebuild BVH
```

### Hash Grids (`wp.HashGrid`)

Spatial hashing for particle neighbor queries (DEM, SPH):

```python
grid = wp.HashGrid(dim_x=128, dim_y=128, dim_z=128, device="cuda")
grid.build(points=particle_positions, radius=search_radius)

@wp.kernel
def find_neighbors(grid_id: wp.uint64, positions: wp.array(dtype=wp.vec3)):
    tid = wp.tid()
    pos = positions[tid]

    query = wp.hash_grid_query(grid_id, pos, search_radius)
    index = int(0)
    while wp.hash_grid_query_next(query, index):
        neighbor_pos = positions[index]
        dist = wp.length(pos - neighbor_pos)
        if dist < search_radius:
            # Process neighbor
            ...
```

### Volumes (`wp.Volume`)

Sparse volumetric grids based on NanoVDB (SDFs, velocity fields, smoke):

```python
# Load from NanoVDB file
volume = wp.Volume.load_from_nvdb("field.nvdb")

# Create from NumPy (dense → sparse)
volume = wp.Volume.load_from_numpy(numpy_3d_array, bg_value=0.0)

# Sample in kernel
@wp.kernel
def sample_sdf(volume_id: wp.uint64, points: wp.array(dtype=wp.vec3),
               distances: wp.array(dtype=float)):
    tid = wp.tid()
    # Trilinear interpolation in world space
    uvw = wp.volume_world_to_index(volume_id, points[tid])
    distances[tid] = wp.volume_sample(volume_id, uvw, wp.Volume.LINEAR)
```

### BVH (`wp.Bvh`)

Bounding volume hierarchy for ray and AABB intersection queries:

```python
bvh = wp.Bvh(lowers=box_mins, uppers=box_maxs)

# Ray query
query = wp.bvh_query_ray(bvh.id, ray_origin, ray_dir)
# AABB overlap query
query = wp.bvh_query_aabb(bvh.id, aabb_min, aabb_max)
```

### Marching Cubes

Isosurface extraction from 3D scalar fields:

```python
mc = wp.MarchingCubes(nx=128, ny=128, nz=128, device="cuda")
mc.surface(field=sdf_array, threshold=0.0)

vertices = mc.verts    # wp.array(dtype=wp.vec3)
triangles = mc.indices # wp.array(dtype=int)
```

---

## Tile-Based Programming

Warp's tile API enables cooperative block-level operations (similar to Triton), using shared memory and Tensor Cores:

```python
TILE_M = wp.constant(16)
TILE_N = wp.constant(16)
TILE_K = wp.constant(16)
TILE_THREADS = 64

@wp.kernel
def tile_gemm(A: wp.array2d(dtype=float), B: wp.array2d(dtype=float),
              C: wp.array2d(dtype=float)):
    i, j = wp.tid()

    sum = wp.tile_zeros(shape=(TILE_M, TILE_N), dtype=wp.float32)
    count = int(A.shape[1] / TILE_K)

    for k in range(count):
        a = wp.tile_load(A, shape=(TILE_M, TILE_K), offset=(i * TILE_M, k * TILE_K))
        b = wp.tile_load(B, shape=(TILE_K, TILE_N), offset=(k * TILE_K, j * TILE_N))
        wp.tile_matmul(a, b, sum)

    wp.tile_store(C, sum, offset=(i * TILE_M, j * TILE_N))

wp.launch_tiled(tile_gemm, dim=(M // TILE_M, N // TILE_N),
                inputs=[A, B, C], block_dim=TILE_THREADS)
```

Key tile operations:
- **Construction**: `tile_zeros`, `tile_ones`, `tile_load`, `tile_from_thread`
- **Math**: `tile_matmul`, `tile_fft`, `tile_ifft`, `tile_cholesky`, `tile_cholesky_solve`
- **Reductions**: `tile_sum`, `tile_min`, `tile_max`, `tile_reduce`
- **IO**: `tile_load`, `tile_store`, `tile_atomic_add`
- **Arithmetic**: `+`, `-`, `*`, `/` operators on tiles
- **Spatial queries**: `tile_bvh_query_aabb`, `tile_mesh_query_aabb`

SIMT↔Tile bridging: `wp.tile(scalar_value)` creates a tile from per-thread values; `wp.untile(tile)` extracts per-thread values back.

---

## Differentiability

Warp generates forward and backward (adjoint) kernels automatically, enabling gradient-based optimization and ML integration:

```python
# Arrays participating in gradients need requires_grad=True
a = wp.zeros(1024, dtype=wp.vec3, device="cuda", requires_grad=True)

# Record forward pass
tape = wp.Tape()
with tape:
    wp.launch(kernel=compute1, inputs=[a, b], device="cuda")
    wp.launch(kernel=compute2, inputs=[c, d], device="cuda")
    wp.launch(kernel=loss_fn, inputs=[d, loss], device="cuda")

# Backward pass
tape.backward(loss)

# Access gradients
grad_a = tape.gradients[a]
```

Key features:
- Automatic adjoint code generation for all kernels
- `wp.Tape` records and replays computation graphs
- Integrates with PyTorch autograd and JAX JIT
- Custom gradient functions via `@wp.func_grad`
- Jacobian computation support

---

## Streams, Events, and CUDA Graphs

```python
# Streams for concurrent execution
stream1 = wp.Stream("cuda:0")
stream2 = wp.Stream("cuda:0")
wp.launch(kernel1, ..., stream=stream1)
wp.launch(kernel2, ..., stream=stream2)

# CUDA Graph capture (eliminates Python launch overhead)
with wp.ScopedCapture() as capture:
    wp.launch(kernel1, ...)
    wp.launch(kernel2, ...)
    wp.launch(kernel3, ...)

# Replay graph many times with near-zero CPU overhead
for _ in range(1000):
    wp.capture_launch(capture.graph)
```

---

## Random Number Generation

Uses PCG (Permuted Congruential Generator) — initialize per-thread:

```python
@wp.kernel
def monte_carlo(samples: wp.array(dtype=wp.vec3), seed: int):
    tid = wp.tid()
    rng = wp.rand_init(seed, tid)  # Unique sequence per thread

    x = wp.randf(rng)  # [0, 1)
    y = wp.randf(rng)
    z = wp.randf(rng)
    samples[tid] = wp.vec3(x, y, z)
```

Use different seeds between launches to avoid correlated sequences.

---

## Interoperability

### NumPy (zero-copy on CPU)
```python
np_array = warp_array.numpy()          # GPU → CPU copy, CPU → zero-copy view
wp_array = wp.from_numpy(np_array, dtype=wp.vec3, device="cuda")
```

### PyTorch (zero-copy, autograd support)
```python
torch_tensor = wp.to_torch(warp_array)      # Zero-copy
warp_array = wp.from_torch(torch_tensor)     # Zero-copy
# Gradient arrays are converted between Warp tape and PyTorch autograd
```

### CuPy/Numba (zero-copy via CUDA Array Interface)
```python
# CuPy arrays can be passed directly to Warp kernels
# Warp arrays expose __cuda_array_interface__
cupy_arr = cp.asarray(warp_array)  # Zero-copy
```

### JAX (zero-copy via DLPack)
```python
jax_array = wp.to_jax(warp_array)
warp_array = wp.from_jax(jax_array)
# wp.jax_kernel() / wp.jax_callable() wrap Warp kernels for use inside JAX
# (the old warp.jax_experimental module is deprecated since Warp 1.14)
```

### DLPack (universal zero-copy)
```python
# Import from any DLPack framework
warp_array = wp.from_dlpack(external_array)
# Export
external = framework.from_dlpack(warp_array)
```

---

## Performance Optimization

### 1. Use CUDA Graphs for Repeated Launches

If you launch the same sequence of kernels many times (simulation loop), CUDA graph capture eliminates Python overhead:

```python
with wp.ScopedCapture() as capture:
    for _ in range(substeps):
        wp.launch(integrate, ...)
        wp.launch(collide, ...)

for frame in range(num_frames):
    wp.capture_launch(capture.graph)
```

### 2. Minimize Host-Device Transfers

Keep data on GPU. Use `wp.array` on device, avoid `.numpy()` in inner loops.

### 3. Use Tile Operations for Reductions and GEMM

Tile operations can reduce global traffic and atomic contention, but they also change resource use.
Compare `wp.tile()` / `wp.tile_sum()` designs with the simpler atomic implementation on the target
shape and GPU.

### 4. Prefer float32 Over float64

Use float32 only when the numerical contract permits it. The float32/float64 throughput ratio is
architecture-specific; validate accuracy and benchmark the target GPU.

### 5. Kernel Caching

Warp caches compiled kernels between runs. Exclude first-use compilation from steady-state kernel
timing, but include it when one-shot application latency matters.

### 6. Object Lifetime

Keep Python references to spatial primitives (Mesh, HashGrid, Volume, BVH) alive while their `.id` is in use. Garbage collection of the Python object while a kernel holds the ID causes undefined behavior.

---

## Common Patterns

### Particle Simulation

```python
@wp.kernel
def integrate_particles(positions: wp.array(dtype=wp.vec3),
                        velocities: wp.array(dtype=wp.vec3),
                        forces: wp.array(dtype=wp.vec3),
                        dt: float):
    tid = wp.tid()
    vel = velocities[tid] + forces[tid] * dt
    pos = positions[tid] + vel * dt

    velocities[tid] = vel
    positions[tid] = pos
```

### Mesh Ray Casting

```python
@wp.kernel
def cast_rays(mesh_id: wp.uint64,
              ray_origins: wp.array(dtype=wp.vec3),
              ray_dirs: wp.array(dtype=wp.vec3),
              hit_points: wp.array(dtype=wp.vec3)):
    tid = wp.tid()
    query = wp.mesh_query_ray(mesh_id, ray_origins[tid], ray_dirs[tid], 1e6)
    if query.result:
        hit_points[tid] = ray_origins[tid] + ray_dirs[tid] * query.t
```

### Differentiable Simulation with PyTorch

```python
import torch
import warp as wp

# Warp kernel for simulation
@wp.kernel
def simulate(state: wp.array(dtype=wp.vec3), params: wp.array(dtype=float),
             output: wp.array(dtype=wp.vec3)):
    tid = wp.tid()
    # ... physics computation ...

# PyTorch training loop
optimizer = torch.optim.Adam([torch_params], lr=1e-3)

for epoch in range(100):
    wp_params = wp.from_torch(torch_params)
    tape = wp.Tape()
    with tape:
        wp.launch(simulate, dim=n, inputs=[state, wp_params, output])
        wp.launch(loss_kernel, dim=1, inputs=[output, target, loss])

    tape.backward(loss)
    grad = wp.to_torch(tape.gradients[wp_params])
    torch_params.grad = grad
    optimizer.step()
```

### SPH Fluid with Hash Grid

```python
grid = wp.HashGrid(128, 128, 128, device="cuda")

@wp.kernel
def compute_density(grid_id: wp.uint64, positions: wp.array(dtype=wp.vec3),
                    densities: wp.array(dtype=float), radius: float):
    tid = wp.tid()
    pos = positions[tid]
    density = float(0.0)

    query = wp.hash_grid_query(grid_id, pos, radius)
    index = int(0)
    while wp.hash_grid_query_next(query, index):
        dist = wp.length(pos - positions[index])
        if dist < radius:
            # SPH kernel
            q = dist / radius
            density += (1.0 - q) * (1.0 - q) * (1.0 - q)

    densities[tid] = density

# Each timestep:
grid.build(points=positions, radius=h)
wp.launch(compute_density, dim=n, inputs=[grid.id, positions, densities, h])
```

---

## Common Pitfalls

1. **Forgetting type annotations** — All kernel parameters must be typed. Warp infers types from annotations, not runtime values.

2. **Using Python data structures in kernels** — No lists, dicts, or sets. Use `wp.array`, `wp.vec3`, `@wp.struct`.

3. **Calling `wp.tid()` in user functions** — `wp.tid()` only works in kernels. Pass the thread index as a parameter to `@wp.func` functions.

4. **Object lifetime issues** — Spatial primitives (Mesh, HashGrid, Volume, BVH) must stay alive (referenced in Python) while their `.id` is used in kernels. Letting the Python object get garbage-collected causes crashes.

5. **Expecting in-place ops to be differentiable** — Warp's autodiff doesn't support in-place array modifications. Write to separate output arrays for gradient computation.

6. **Not using `requires_grad=True`** — Arrays participating in gradient computation must be created with `requires_grad=True`.

7. **Launching with wrong device** — Arrays and kernel launch must be on the same device. Use `device="cuda"` consistently.

8. **First-launch compilation time** — The first kernel launch triggers JIT compilation (can take seconds). Subsequent runs use the cache. Don't benchmark the first run.

9. **Using tuples instead of Warp types** — `(1.0, 2.0, 3.0)` is invalid in kernel scope. Use `wp.vec3(1.0, 2.0, 3.0)`.

10. **Block size on CPU** — Tile operations on CPU use `block_dim=1`, which changes behavior. Design cross-device kernels to be independent of block size.
