---
name: umap-learn
description: Use UMAP-learn for nonlinear dimensionality reduction, 2D/3D embeddings, clustering preprocessing, supervised or semi-supervised UMAP, DensMAP, AlignedUMAP, and Parametric UMAP workflows.
---

# UMAP-Learn

## Overview

UMAP (Uniform Manifold Approximation and Projection) is a dimensionality reduction technique for visualization and general non-linear dimensionality reduction. Apply this skill for fast, scalable embeddings that preserve local and global structure, supervised learning, and clustering preprocessing.

## Quick Start

### Installation

Current stable release: **umap-learn 0.5.12** (released April 2026). Requires Python 3.9+ and depends on `scikit-learn>=1.6`, `numba`, `pynndescent`, `numpy`, and `scipy`. Pin to a verified release:

```bash
uv pip install umap-learn==0.5.12
```

### Basic Usage

UMAP follows scikit-learn conventions and can be used as a drop-in replacement for t-SNE or PCA.

```python
import umap
from sklearn.preprocessing import StandardScaler

# Prepare data (standardization is essential)
scaled_data = StandardScaler().fit_transform(data)

# Method 1: Single step (fit and transform)
embedding = umap.UMAP().fit_transform(scaled_data)

# Method 2: Separate steps (for reusing trained model)
reducer = umap.UMAP(random_state=42)
reducer.fit(scaled_data)
embedding = reducer.embedding_  # Access the trained embedding
```

**Preprocessing requirement:** Match preprocessing to the metric. For numeric Euclidean-style metrics, scale features before fitting so high-variance columns do not dominate. For cosine, binary, precomputed-distance, or mixed-feature workflows, choose preprocessing that matches the metric instead of blindly standardizing every column.

### Typical Workflow

```python
import umap
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# 1. Preprocess data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(raw_data)

# 2. Create and fit UMAP
reducer = umap.UMAP(
    n_neighbors=15,
    min_dist=0.1,
    n_components=2,
    metric='euclidean',
    random_state=42
)
embedding = reducer.fit_transform(scaled_data)

# 3. Visualize
plt.scatter(embedding[:, 0], embedding[:, 1], c=labels, cmap='Spectral', s=5)
plt.colorbar()
plt.title('UMAP Embedding')
plt.show()
```

## Parameter Tuning Guide

UMAP has four primary parameters that control the embedding behavior. Understanding these is crucial for effective usage.

### n_neighbors (default: 15)

**Purpose:** Balances local versus global structure in the embedding.

**How it works:** Controls the size of the local neighborhood UMAP examines when learning manifold structure.

**Effects by value:**
- **Low values (2-5):** Emphasizes fine local detail but may fragment data into disconnected components
- **Medium values (15-20):** Balanced view of both local structure and global relationships (recommended starting point)
- **High values (50-200):** Prioritizes broad topological structure at the expense of fine-grained details

**Recommendation:** Start with 15 and adjust based on results. Increase for more global structure, decrease for more local detail.

### min_dist (default: 0.1)

**Purpose:** Controls how tightly points cluster in the low-dimensional space.

**How it works:** Sets the minimum distance apart that points are allowed to be in the output representation.

**Effects by value:**
- **Low values (0.0-0.1):** Creates clumped embeddings useful for clustering; reveals fine topological details
- **High values (0.5-0.99):** Prevents tight packing; emphasizes broad topological preservation over local structure

**Recommendation:** Use 0.0 for clustering applications, 0.1-0.3 for visualization, 0.5+ for loose structure.

### n_components (default: 2)

**Purpose:** Determines the dimensionality of the embedded output space.

**Key feature:** Unlike t-SNE, UMAP scales well in the embedding dimension, enabling use beyond visualization.

**Common uses:**
- **2-3 dimensions:** Visualization
- **5-10 dimensions:** Clustering preprocessing (better preserves density than 2D)
- **10-50 dimensions:** Feature engineering for downstream ML models

**Recommendation:** Use 2 for visualization, 5-10 for clustering, higher for ML pipelines.

### metric (default: 'euclidean')

**Purpose:** Specifies how distance is calculated between input data points.

**Supported metrics:**
- **Minkowski variants:** euclidean, manhattan, chebyshev
- **Spatial metrics:** canberra, braycurtis, haversine
- **Correlation metrics:** cosine, correlation (good for text/document embeddings)
- **Binary data metrics:** hamming, jaccard, dice, russellrao, kulsinski, rogerstanimoto, sokalmichener, sokalsneath, yule
- **Custom metrics:** User-defined distance functions via Numba

**Recommendation:** Use euclidean for numeric data, cosine for text/document vectors, hamming for binary data.

### Parameter Tuning Example

```python
# For visualization with emphasis on local structure
umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, metric='euclidean')

# For clustering preprocessing
umap.UMAP(n_neighbors=30, min_dist=0.0, n_components=10, metric='euclidean')

# For document embeddings
umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, metric='cosine')

# For preserving global structure
umap.UMAP(n_neighbors=100, min_dist=0.5, n_components=2, metric='euclidean')
```

## Supervised and Semi-Supervised Dimension Reduction

UMAP supports incorporating label information to guide the embedding process, enabling class separation while preserving internal structure.

### Supervised UMAP

Pass target labels via the `y` parameter when fitting:

```python
# Supervised dimension reduction
embedding = umap.UMAP().fit_transform(data, y=labels)
```

**Key benefits:**
- Achieves cleanly separated classes
- Preserves internal structure within each class
- Maintains global relationships between classes

### Semi-Supervised UMAP

For partial labels, mark unlabeled points with `-1` following scikit-learn convention:

```python
# Create semi-supervised labels
semi_labels = labels.copy()
semi_labels[unlabeled_indices] = -1

# Fit with partial labels
embedding = umap.UMAP().fit_transform(data, y=semi_labels)
```

**When to use:** When labeling is expensive or you have more data than labels available.

## UMAP for Clustering

UMAP serves as effective preprocessing for density-based clustering algorithms like HDBSCAN, overcoming the curse of dimensionality.

### Best Practices for Clustering

**Key principle:** Configure UMAP differently for clustering than for visualization.

**Recommended parameters:**
- **n_neighbors:** Increase to ~30 (default 15 is too local and can create artificial fine-grained clusters)
- **min_dist:** Set to 0.0 (pack points densely within clusters for clearer boundaries)
- **n_components:** Use 5-10 dimensions (maintains performance while improving density preservation vs. 2D)

### Clustering Workflow

Install HDBSCAN separately for density-based clustering:

```bash
uv pip install hdbscan
```

```python
import umap
import hdbscan
from sklearn.preprocessing import StandardScaler

# 1. Preprocess data
scaled_data = StandardScaler().fit_transform(data)

# 2. UMAP with clustering-optimized parameters
reducer = umap.UMAP(
    n_neighbors=30,
    min_dist=0.0,
    n_components=10,  # Higher than 2 for better density preservation
    metric='euclidean',
    random_state=42
)
embedding = reducer.fit_transform(scaled_data)

# 3. Apply HDBSCAN clustering
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=15,
    min_samples=5,
    metric='euclidean'
)
labels = clusterer.fit_predict(embedding)

# 4. Evaluate
from sklearn.metrics import adjusted_rand_score
score = adjusted_rand_score(true_labels, labels)
print(f"Adjusted Rand Score: {score:.3f}")
print(f"Number of clusters: {len(set(labels)) - (1 if -1 in labels else 0)}")
print(f"Noise points: {sum(labels == -1)}")
```

### Visualization After Clustering

```python
# Create 2D embedding for visualization (separate from clustering)
vis_reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, n_components=2, random_state=42)
vis_embedding = vis_reducer.fit_transform(scaled_data)

# Plot with cluster labels
import matplotlib.pyplot as plt
plt.scatter(vis_embedding[:, 0], vis_embedding[:, 1], c=labels, cmap='Spectral', s=5)
plt.colorbar()
plt.title('UMAP Visualization with HDBSCAN Clusters')
plt.show()
```

**Important caveat:** UMAP does not completely preserve density and can create artificial cluster divisions. Always validate and explore resulting clusters.

## Transforming New Data

UMAP enables preprocessing of new data through its `transform()` method, allowing trained models to project unseen data into the learned embedding space.

### Basic Transform Usage

```python
# Train on training data
trans = umap.UMAP(n_neighbors=15, random_state=42).fit(X_train)

# Transform test data
test_embedding = trans.transform(X_test)
```

### Integration with Machine Learning Pipelines

```python
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import umap

# Split data
X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2)

# Preprocess
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train UMAP
reducer = umap.UMAP(n_components=10, random_state=42)
X_train_embedded = reducer.fit_transform(X_train_scaled)
X_test_embedded = reducer.transform(X_test_scaled)

# Train classifier on embeddings
clf = SVC()
clf.fit(X_train_embedded, y_train)
accuracy = clf.score(X_test_embedded, y_test)
print(f"Test accuracy: {accuracy:.3f}")
```

### Important Considerations

**Data consistency:** The transform method assumes the overall distribution in the higher-dimensional space is consistent between training and test data. When this assumption fails, consider using Parametric UMAP instead.

**Performance:** Transform operations are efficient (typically <1 second), though initial calls may be slower due to Numba JIT compilation.

**Scikit-learn compatibility:** UMAP follows standard sklearn conventions and works in pipelines. Recent 0.5.x releases also improved feature-name support and compatibility with current scikit-learn validation APIs:

```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('umap', umap.UMAP(n_components=10)),
    ('classifier', SVC())
])

pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
feature_names = pipeline.named_steps['umap'].get_feature_names_out()
```

## Advanced Features

### Parametric UMAP

Parametric UMAP replaces direct embedding optimization with a learned neural network mapping function.

**Key differences from standard UMAP:**
- Uses TensorFlow/Keras to train encoder networks
- Enables efficient transformation of new data
- Supports reconstruction via decoder networks (inverse transform)
- Allows custom architectures (CNNs for images, RNNs for sequences)

**Installation:**
```bash
uv pip install "umap-learn[parametric-umap]==0.5.12"
# Installs the TensorFlow-backed Parametric UMAP extra.
```

**Basic usage:**
```python
from umap.parametric_umap import ParametricUMAP

# Default architecture (3-layer 100-neuron fully-connected network)
embedder = ParametricUMAP()
embedding = embedder.fit_transform(data)

# Transform new data efficiently
new_embedding = embedder.transform(new_data)
```

**Custom architecture:**
```python
import tensorflow as tf

# Define custom encoder
encoder = tf.keras.Sequential([
    tf.keras.layers.InputLayer(shape=(input_dim,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(2)  # Output dimension
])

embedder = ParametricUMAP(encoder=encoder, dims=(input_dim,))
embedding = embedder.fit_transform(data)
```

**Persistence:** Save Parametric UMAP with its built-in Keras-aware methods rather than plain pickle:

```python
embedder.save("parametric_umap_model", exclude_raw_data=True)

from umap.parametric_umap import load_ParametricUMAP
loaded = load_ParametricUMAP("parametric_umap_model")
new_embedding = loaded.transform(new_data)
```

Recent 0.5.12 fixes include Parametric UMAP retraining stability improvements and metric-gradient fixes, so prefer the pinned current release for neural-network workflows.

**When to use Parametric UMAP:**
- Need efficient transformation of new data after training
- Require reconstruction capabilities (inverse transforms)
- Want to combine UMAP with autoencoders
- Working with complex data types (images, sequences) benefiting from specialized architectures

### Inverse Transforms

Inverse transforms enable reconstruction of high-dimensional data from low-dimensional embeddings.

**Basic usage:**
```python
reducer = umap.UMAP()
embedding = reducer.fit_transform(data)

# Reconstruct high-dimensional data from embedding coordinates
reconstructed = reducer.inverse_transform(embedding)
```

**Important limitations:**
- Computationally expensive operation
- Works poorly outside the convex hull of the embedding
- Accuracy decreases in regions with gaps between clusters

**Example: Exploring embedding space:**
```python
import numpy as np

# Create grid of points in embedding space
x = np.linspace(embedding[:, 0].min(), embedding[:, 0].max(), 10)
y = np.linspace(embedding[:, 1].min(), embedding[:, 1].max(), 10)
xx, yy = np.meshgrid(x, y)
grid_points = np.c_[xx.ravel(), yy.ravel()]

# Reconstruct samples from grid
reconstructed_samples = reducer.inverse_transform(grid_points)
```

### AlignedUMAP

For analyzing temporal or related datasets (e.g., time-series experiments, batch data):

```python
from umap import AlignedUMAP

# List of related datasets
datasets = [day1_data, day2_data, day3_data]

# Relations map matching sample indices between consecutive datasets.
relations = [
    {day1_idx: day2_idx for day1_idx, day2_idx in matched_day1_to_day2},
    {day2_idx: day3_idx for day2_idx, day3_idx in matched_day2_to_day3},
]

# Create aligned embeddings
mapper = AlignedUMAP().fit(datasets, relations=relations)
aligned_embeddings = mapper.embeddings_  # List of embeddings
```

**When to use:** Comparing embeddings across related datasets while maintaining consistent coordinate systems. `relations` is required for meaningful alignment; each dictionary describes how samples in one dataset correspond to samples in the next.

## Reproducibility

To ensure reproducible results, always set the `random_state` parameter:

```python
reducer = umap.UMAP(random_state=42)
```

UMAP uses stochastic optimization, so results will vary slightly between runs without a fixed random state.

Setting `random_state` prioritizes deterministic output. Leave it unset when throughput matters more than exact repeatability, because UMAP can use more parallelism without a fixed seed.

## Common Issues and Solutions

**Issue:** Disconnected components or fragmented clusters
- **Solution:** Increase `n_neighbors` to emphasize more global structure

**Issue:** Clusters too spread out or not well separated
- **Solution:** Decrease `min_dist` to allow tighter packing

**Issue:** Poor clustering results
- **Solution:** Use clustering-specific parameters (n_neighbors=30, min_dist=0.0, n_components=5-10)

**Issue:** Transform results differ significantly from training
- **Solution:** Ensure test data distribution matches training, or use Parametric UMAP

**Issue:** Slow performance on large datasets
- **Solution:** Set `low_memory=True` (default), or consider dimensionality reduction with PCA first

**Issue:** NaN or inf values in input data
- **Solution:** Impute or drop invalid rows before fitting. Current UMAP uses scikit-learn-style finite-value checks (`ensure_all_finite`) in `fit()` and `update()`, so clean numeric input is the safest default

**Issue:** All points collapsed to single cluster
- **Solution:** Check data preprocessing (ensure proper scaling), increase `min_dist`

**Issue:** Imports resolve to a local file instead of the real package
- **Solution:** Do not keep project files named `umap.py`, `sklearn.py`, `hdbscan.py`, or `tensorflow.py` beside notebooks or scripts. Those names can shadow installed packages and break or poison examples.

## Resources

### Official documentation

- [UMAP user guide](https://umap-learn.readthedocs.io/en/latest/)
- [Release notes](https://umap-learn.readthedocs.io/en/latest/release_notes.html)
- [PyPI package](https://pypi.org/project/umap-learn/) (current stable: 0.5.12)
- [GitHub repository](https://github.com/lmcinnes/umap)

### references/

Contains detailed API documentation:
- `api_reference.md`: Complete UMAP class parameters and methods

Load these references when detailed parameter information or advanced method usage is needed.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/umap-learn/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_reference.md`

# UMAP API Reference

Reference for **umap-learn 0.5.12** (Python >=3.9; `scikit-learn>=1.6`). See [official API guide](https://umap-learn.readthedocs.io/en/latest/api.html) and the 0.5.12 GitHub tag for the full upstream reference.

## UMAP Class

`umap.UMAP(n_neighbors=15, n_components=2, metric='euclidean', metric_kwds=None, output_metric='euclidean', output_metric_kwds=None, n_epochs=None, learning_rate=1.0, init='spectral', min_dist=0.1, spread=1.0, low_memory=True, n_jobs=-1, set_op_mix_ratio=1.0, local_connectivity=1.0, repulsion_strength=1.0, negative_sample_rate=5, transform_queue_size=4.0, a=None, b=None, random_state=None, angular_rp_forest=False, target_n_neighbors=-1, target_metric='categorical', target_metric_kwds=None, target_weight=0.5, transform_seed=42, transform_mode='embedding', force_approximation_algorithm=False, verbose=False, tqdm_kwds=None, unique=False, densmap=False, dens_lambda=2.0, dens_frac=0.3, dens_var_shift=0.1, output_dens=False, disconnection_distance=None, precomputed_knn=(None, None, None))`

Find low-dimensional embedding that approximates the underlying manifold of the data.

### Core Parameters

#### n_neighbors (int, default: 15)
Size of the local neighborhood used for manifold approximation. Larger values result in more global views of the manifold, while smaller values preserve more local structure. Generally in the range 2 to 100.

**Tuning guidance:**
- Use 2-5 for very local structure
- Use 10-20 for balanced local/global structure (typical)
- Use 50-200 for emphasizing global structure

#### n_components (int, default: 2)
Dimension of the embedding space. Unlike t-SNE, UMAP scales well with increasing embedding dimensions.

**Common values:**
- 2-3: Visualization
- 5-10: Clustering preprocessing
- 10-100: Feature engineering for downstream ML

#### metric (str or callable, default: 'euclidean')
Distance metric to use. Accepts:
- Any metric from scipy.spatial.distance
- Any metric from sklearn.metrics
- Custom callable distance functions (must be compiled with Numba)

**Common metrics:**
- `'euclidean'`: Standard Euclidean distance (default)
- `'manhattan'`: L1 distance
- `'cosine'`: Cosine distance (good for text/document vectors)
- `'correlation'`: Correlation distance
- `'hamming'`: Hamming distance (for binary data)
- `'jaccard'`: Jaccard distance (for binary/set data)
- `'dice'`: Dice distance
- `'canberra'`: Canberra distance
- `'braycurtis'`: Bray-Curtis distance
- `'chebyshev'`: Chebyshev distance
- `'minkowski'`: Minkowski distance (specify p with metric_kwds)
- `'precomputed'`: Use precomputed distance matrix

#### output_metric (str or callable, default: 'euclidean')
Distance metric for the embedding space. Most workflows should keep the Euclidean default; advanced workflows can use a supported output metric with `output_metric_kwds`.

#### min_dist (float, default: 0.1)
Effective minimum distance between embedded points. Controls how tightly points are packed together. Smaller values result in clumpier embeddings.

**Tuning guidance:**
- Use 0.0 for clustering applications
- Use 0.1-0.3 for visualization (balanced)
- Use 0.5-0.99 for loose structure preservation

#### spread (float, default: 1.0)
Effective scale of embedded points. Combined with `min_dist` to control clumped vs. spread-out embeddings. Determines how spread out the clusters are in the embedding space.

### Training Parameters

#### n_epochs (int, default: None)
Number of training epochs. If None, automatically determined based on dataset size (typically 200-500 epochs).

**Manual tuning:**
- Smaller datasets may need 500+ epochs
- Larger datasets may converge with 200 epochs
- More epochs = better optimization but slower training

#### learning_rate (float, default: 1.0)
Initial learning rate for the SGD optimizer. Higher values lead to faster convergence but may overshoot optimal solutions.

#### init (str or np.ndarray, default: 'spectral')
Initialization method for the embedding:
- `'spectral'`: Use spectral embedding (default, usually best)
- `'random'`: Random initialization
- `'pca'`: Initialize with PCA
- numpy array: Custom initialization (shape: (n_samples, n_components))

### Advanced Structural Parameters

#### local_connectivity (int, default: 1.0)
Number of nearest neighbors assumed to be locally connected. Higher values give more connected manifolds.

#### set_op_mix_ratio (float, default: 1.0)
Interpolation between union and intersection when constructing fuzzy set unions. Value of 1.0 uses pure union, 0.0 uses pure intersection.

#### repulsion_strength (float, default: 1.0)
Weighting applied to negative samples in low-dimensional embedding optimization. Higher values push embedded points further apart.

#### negative_sample_rate (int, default: 5)
Number of negative samples to select per positive sample. Higher values lead to greater repulsion between points and more spread-out embeddings but increase computational cost.

### Supervised Learning Parameters

#### target_n_neighbors (int, default: -1)
Number of nearest neighbors to use when constructing target simplicial set. If -1, uses n_neighbors value.

#### target_metric (str, default: 'categorical')
Distance metric for target values (labels):
- `'categorical'`: For classification tasks
- Any other metric for regression tasks

#### target_weight (float, default: 0.5)
Weight applied to target information vs. data structure. Range 0.0 to 1.0:
- 0.0: Pure unsupervised embedding (ignores labels)
- 0.5: Balanced (default)
- 1.0: Pure supervised embedding (only considers labels)

### Transform Parameters

#### transform_queue_size (float, default: 4.0)
Size of the nearest neighbor search queue for transform operations. Larger values improve transform accuracy but increase memory usage and computation time.

#### transform_seed (int, default: 42)
Random seed for transform operations. Ensures reproducibility of transform results.

#### transform_mode (str, default: 'embedding')
Method for transforming new data:
- `'embedding'`: Standard approach (default)
- `'graph'`: Use nearest neighbor graph

### Performance Parameters

#### low_memory (bool, default: True)
Whether to use a memory-efficient implementation. Set to False only if memory is not a constraint and you want faster performance.

#### n_jobs (int, default: -1)
Number of parallel jobs to use where supported. `-1` uses all available processors. Setting `random_state` can limit parallel optimization in favor of reproducibility.

#### verbose (bool, default: False)
Whether to print progress messages during fitting.

#### tqdm_kwds (dict, default: None)
Keyword arguments passed to the tqdm progress bar when progress reporting is enabled.

#### unique (bool, default: False)
Whether to consider only unique data points. Set to True if you know your data contains many duplicates to improve performance.

#### force_approximation_algorithm (bool, default: False)
Force use of approximate nearest neighbor search even for small datasets. Can improve performance on large datasets.

#### angular_rp_forest (bool, default: False)
Whether to use angular random projection forest for nearest neighbor search. Can improve performance for normalized data in high dimensions.

### DensMAP Parameters

DensMAP is a variant that preserves local density information.

#### densmap (bool, default: False)
Whether to use the DensMAP algorithm instead of standard UMAP. Preserves local density in addition to topological structure.

#### dens_lambda (float, default: 2.0)
Weight of density preservation term in DensMAP optimization. Higher values emphasize density preservation.

#### dens_frac (float, default: 0.3)
Fraction of dataset used for density estimation in DensMAP.

#### dens_var_shift (float, default: 0.1)
Regularization parameter for density estimation in DensMAP.

#### output_dens (bool, default: False)
Whether to output local density estimates in addition to the embedding. When enabled, `fit_transform()` returns `(embedding, original_local_radii, embedded_local_radii)` and fitted objects expose density-related attributes such as `rad_orig_` and `rad_emb_`.

### Other Parameters

#### a (float, default: None)
Parameter controlling embedding. If None, determined automatically from min_dist and spread.

#### b (float, default: None)
Parameter controlling embedding. If None, determined automatically from min_dist and spread.

#### random_state (int, RandomState instance, or None, default: None)
Random state for reproducibility. Set to an integer for reproducible results.

#### metric_kwds (dict, default: None)
Additional keyword arguments for the distance metric.

#### disconnection_distance (float, default: None)
Distance threshold for considering points disconnected. If None, uses max distance in the graph.

#### precomputed_knn (tuple, default: (None, None, None))
Precomputed k-nearest neighbors as (knn_indices, knn_dists, knn_search_index). Useful for reusing expensive computations.

## Methods

### fit(X, y=None, ensure_all_finite=True, **kwargs)
Fit the UMAP model to the data.

**Parameters:**
- `X`: array-like, shape (n_samples, n_features) - Training data
- `y`: array-like, shape (n_samples,), optional - Target values for supervised dimension reduction
- `ensure_all_finite`: bool or sklearn-compatible option - Controls finite-value validation during fitting

**Returns:**
- `self`: Fitted UMAP object

**Attributes set:**
- `embedding_`: The embedded representation of training data
- `graph_`: Fuzzy simplicial set approximation to the manifold
- `_raw_data`: Copy of the training data
- `_small_data`: Whether the dataset is considered small
- `_metric_kwds`: Processed metric keyword arguments
- `_n_neighbors`: Actual n_neighbors used
- `_initial_alpha`: Initial learning rate
- `_a`, `_b`: Curve parameters

### fit_transform(X, y=None)
Fit the model and return the embedded representation.

**Parameters:**
- `X`: array-like, shape (n_samples, n_features) - Training data
- `y`: array-like, shape (n_samples,), optional - Target values for supervised dimension reduction

**Returns:**
- `X_new`: array, shape (n_samples, n_components) - Embedded data

### transform(X)
Transform new data into the existing embedded space.

**Parameters:**
- `X`: array-like, shape (n_samples, n_features) - New data to transform

**Returns:**
- `X_new`: array, shape (n_samples, n_components) - Embedded representation of new data

**Important notes:**
- The model must be fitted before calling transform
- Transform quality depends on similarity between training and test distributions
- For significantly different data distributions, consider Parametric UMAP

### inverse_transform(X)
Transform data from the embedded space back to the original data space.

**Parameters:**
- `X`: array-like, shape (n_samples, n_components) - Embedded data points

**Returns:**
- `X_new`: array, shape (n_samples, n_features) - Reconstructed data in original space

**Important notes:**
- Computationally expensive operation
- Works poorly outside the convex hull of the training embedding
- Reconstruction quality varies by region

### update(X, ensure_all_finite=True)
Update the model with new data. Allows incremental fitting.

**Parameters:**
- `X`: array-like, shape (n_samples, n_features) - New data to incorporate
- `ensure_all_finite`: bool or sklearn-compatible option - Controls finite-value validation during update

**Returns:**
- `self`: Updated UMAP object

**Note:** Experimental feature, may not preserve all properties of batch training.

### get_feature_names_out(input_features=None)
Return output feature names for sklearn pipeline compatibility (added in 0.5.x).

**Parameters:**
- `input_features`: array-like of str, optional - Ignored; present for sklearn API compatibility

**Returns:**
- `ndarray` of shape `(n_components,)` with names like `umap0`, `umap1`, ...

## Attributes

### embedding_
array, shape (n_samples, n_components) - The embedded representation of the training data.

### graph_
scipy.sparse.csr_matrix - The weighted adjacency matrix of the fuzzy simplicial set approximation to the manifold.

### _raw_data
array - Copy of the raw training data.

### _sparse_data
bool - Whether the training data was sparse.

### _small_data
bool - Whether the dataset was considered small (uses different algorithm for small datasets).

### _input_hash
str - Hash of the input data for caching purposes.

### _knn_indices
array - Indices of k-nearest neighbors for each training point.

### _knn_dists
array - Distances to k-nearest neighbors for each training point.

### _rp_forest
list - Random projection forest used for approximate nearest neighbor search.

## ParametricUMAP Class

`umap.parametric_umap.ParametricUMAP(batch_size=None, dims=None, encoder=None, decoder=None, parametric_reconstruction=False, parametric_reconstruction_loss_fcn=None, parametric_reconstruction_loss_weight=1.0, autoencoder_loss=False, reconstruction_validation=None, global_correlation_loss_weight=0, landmark_loss_fn=None, landmark_loss_weight=1.0, keras_fit_kwargs={}, **kwargs)`

Install with `uv pip install "umap-learn[parametric-umap]==0.5.12"`. Parametric UMAP uses neural networks to learn the embedding function.

### Additional Parameters (beyond UMAP)

#### encoder (tensorflow.keras.Model, default: None)
Keras model for encoding data to embeddings. If None, uses default 3-layer architecture with 100 neurons per layer.

#### decoder (tensorflow.keras.Model, default: None)
Keras model for decoding embeddings back to data space. Only used if parametric_reconstruction=True.

#### parametric_reconstruction (bool, default: False)
Whether to use parametric reconstruction. Requires decoder model.

#### parametric_reconstruction_loss_fcn (callable, default: None)
Custom reconstruction loss function for decoder training.

#### parametric_reconstruction_loss_weight (float, default: 1.0)
Weight applied to the parametric reconstruction loss.

#### autoencoder_loss (bool, default: False)
Whether to include reconstruction loss in the optimization. Requires decoder model.

#### global_correlation_loss_weight (float, default: 0)
Weight for global correlation loss, used to encourage preservation of broad distance relationships.

#### reconstruction_validation (tuple, default: None)
Validation data (X_val, y_val) for monitoring reconstruction loss during training.

#### dims (tuple, default: None)
Input dimensions for the encoder network. Required if providing custom encoder.

#### batch_size (int, default: None)
Batch size for neural network training. If None, determined automatically.

#### landmark_loss_fn (callable, default: None)
Loss function used when retraining with landmark positions.

#### landmark_loss_weight (float, default: 1.0)
Weight applied to landmark loss relative to the UMAP loss.

#### keras_fit_kwargs (dict, default: {})
Additional keyword arguments passed to the Keras fit() method.

#### Training epoch attributes
`ParametricUMAP` initializes `n_training_epochs=1` and `loss_report_frequency=10` internally. Set these attributes after construction when you need longer neural-network training.

### Methods

Same as UMAP class, but transform() and inverse_transform() use learned neural networks for faster inference.

#### fit(X, y=None, precomputed_distances=None, landmark_positions=None)
Fit the parametric model. `landmark_positions` can be used for landmarked retraining workflows.

#### save(save_location, verbose=True, exclude_raw_data=False)
Save the Parametric UMAP object and Keras networks. Use `load_ParametricUMAP(save_location)` to load it again; plain pickle is not sufficient for models that contain Keras networks.

## Utility Functions

### umap.nearest_neighbors(X, n_neighbors, metric, metric_kwds={}, angular=False, random_state=None)
Compute k-nearest neighbors for the data.

**Returns:** (knn_indices, knn_dists, rp_forest)

### umap.fuzzy_simplicial_set(X, n_neighbors, random_state, metric, metric_kwds={}, knn_indices=None, knn_dists=None, angular=False, set_op_mix_ratio=1.0, local_connectivity=1.0, apply_set_operations=True, verbose=False, return_dists=None)
Construct fuzzy simplicial set representation of the data.

**Returns:** Fuzzy simplicial set as sparse matrix

### umap.simplicial_set_embedding(data, graph, n_components, initial_alpha, a, b, gamma, negative_sample_rate, n_epochs, init, random_state, metric, metric_kwds, densmap, densmap_kwds, output_dens, output_metric, output_metric_kwds, euclidean_output, parallel=False, verbose=False)
Perform the optimization to find a low-dimensional embedding.

**Returns:** Embedding array

### umap.find_ab_params(spread, min_dist)
Fit a, b params for the UMAP curve from spread and min_dist.

**Returns:** (a, b) tuple

## AlignedUMAP Class

`umap.AlignedUMAP(n_neighbors=15, n_components=2, metric='euclidean', metric_kwds=None, n_epochs=None, learning_rate=1.0, init='spectral', alignment_regularisation=0.01, alignment_window_size=3, min_dist=0.1, spread=1.0, low_memory=False, set_op_mix_ratio=1.0, local_connectivity=1.0, repulsion_strength=1.0, negative_sample_rate=5, transform_queue_size=4.0, a=None, b=None, random_state=None, angular_rp_forest=False, target_n_neighbors=-1, target_metric='categorical', target_metric_kwds=None, target_weight=0.5, transform_seed=42, force_approximation_algorithm=False, verbose=False, unique=False)`

UMAP variant for aligning multiple related datasets.

### Additional Parameters

#### alignment_regularisation (float, default: 1e-2)
Strength of alignment regularization between datasets.

#### alignment_window_size (int, default: 3)
Number of adjacent datasets to align.

### Methods

#### fit(X, relations=..., y=None)
Fit model to multiple datasets.

**Parameters:**
- `X`: list of arrays - List of datasets to align
- `relations`: list of dictionaries - Mappings between sample indices in consecutive datasets; required for meaningful alignment

#### update(X, relations=..., y=None)
Append a new dataset to an existing aligned model. Use backward-looking relation mappings from the new dataset to the prior window.

**Returns:**
- `self`: Fitted model

### Attributes

#### embeddings_
list of arrays - List of aligned embeddings, one per input dataset.

## Usage Examples

### Basic Usage with All Common Parameters

```python
import umap

# Standard 2D visualization embedding
reducer = umap.UMAP(
    n_neighbors=15,          # Balance local/global structure
    n_components=2,          # Output dimensions
    metric='euclidean',      # Distance metric
    min_dist=0.1,           # Minimum distance between points
    spread=1.0,             # Scale of embedded points
    random_state=42,        # Reproducibility
    n_epochs=200,           # Training iterations (None = auto)
    learning_rate=1.0,      # SGD learning rate
    init='spectral',        # Initialization method
    low_memory=True,        # Memory-efficient mode
    verbose=True            # Print progress
)

embedding = reducer.fit_transform(data)
```

### Supervised Learning

```python
# Train with labels for class separation
reducer = umap.UMAP(
    n_neighbors=15,
    target_weight=0.5,           # Balance data structure vs labels
    target_metric='categorical',  # Metric for labels
    random_state=42
)

embedding = reducer.fit_transform(data, y=labels)
```

### Clustering Preprocessing

```python
# Optimized for clustering
reducer = umap.UMAP(
    n_neighbors=30,      # More global structure
    min_dist=0.0,        # Allow tight packing
    n_components=10,     # Higher dimensions for density
    metric='euclidean',
    random_state=42
)

embedding = reducer.fit_transform(data)
```

### Custom Distance Metric

```python
from numba import njit

@njit()
def custom_distance(x, y):
    """Custom distance function (must be Numba-compatible)"""
    result = 0.0
    for i in range(x.shape[0]):
        result += abs(x[i] - y[i])
    return result

reducer = umap.UMAP(metric=custom_distance)
embedding = reducer.fit_transform(data)
```

### Parametric UMAP with Custom Architecture

```python
import tensorflow as tf
from umap.parametric_umap import ParametricUMAP

# Define custom encoder
encoder = tf.keras.Sequential([
    tf.keras.layers.InputLayer(shape=(input_dim,)),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(2)  # Output dimension
])

# Define decoder for reconstruction
decoder = tf.keras.Sequential([
    tf.keras.layers.InputLayer(shape=(2,)),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(input_dim)
])

# Train parametric UMAP with autoencoder
embedder = ParametricUMAP(
    encoder=encoder,
    decoder=decoder,
    dims=(input_dim,),
    parametric_reconstruction=True,
    autoencoder_loss=True,
    batch_size=128,
    n_neighbors=15,
    min_dist=0.1,
    random_state=42
)
embedder.n_training_epochs = 10

embedding = embedder.fit_transform(data)
new_embedding = embedder.transform(new_data)
reconstructed = embedder.inverse_transform(embedding)
```

### DensMAP for Density Preservation

```python
# Preserve local density information
reducer = umap.UMAP(
    densmap=True,           # Enable DensMAP
    dens_lambda=2.0,       # Weight of density preservation
    dens_frac=0.3,         # Fraction for density estimation
    output_dens=True,      # Output density estimates
    n_neighbors=15,
    min_dist=0.1,
    random_state=42
)

embedding, original_density, embedded_density = reducer.fit_transform(data)
```

### Aligned UMAP for Time Series

```python
from umap import AlignedUMAP

# Multiple related datasets (e.g., different time points)
datasets = [day1_data, day2_data, day3_data, day4_data]
relations = [
    {day1_idx: day2_idx for day1_idx, day2_idx in matched_day1_to_day2},
    {day2_idx: day3_idx for day2_idx, day3_idx in matched_day2_to_day3},
    {day3_idx: day4_idx for day3_idx, day4_idx in matched_day3_to_day4},
]

# Align embeddings
mapper = AlignedUMAP(
    n_neighbors=15,
    alignment_regularisation=1e-2,  # Alignment strength
    alignment_window_size=2,        # Align with adjacent datasets
    n_components=2,
    random_state=42
)

mapper.fit(datasets, relations=relations)

# Access aligned embeddings
aligned_embeddings = mapper.embeddings_
# aligned_embeddings[0] is day1 embedding
# aligned_embeddings[1] is day2 embedding, etc.
```
