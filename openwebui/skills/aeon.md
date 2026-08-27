---
name: aeon
description: This skill should be used for time series machine learning tasks including classification, regression, clustering, forecasting, anomaly detection, segmentation, and similarity search. Use when working with temporal data, sequential patterns, or time-indexed observations requiring specialized algorithms beyond standard ML approaches. Particularly suited for univariate and multivariate time series analysis with scikit-learn compatible APIs.
---

# Aeon Time Series Machine Learning

## Overview

Aeon is a scikit-learn compatible Python toolkit for time series machine learning ([aeon-toolkit.org](https://www.aeon-toolkit.org/)). It provides algorithms across classification, regression, clustering, forecasting, anomaly detection, segmentation, similarity search, distances, transformations, benchmarking, and visualization — with a consistent estimator API.

**Version note:** Examples target **aeon 1.x** (stable docs: v1.4.0, March 2026). The v1.0 release reworked forecasting and transformations; import paths differ from aeon 0.x/sktime-era code.

## When to Use This Skill

Apply this skill when:
- Classifying or predicting from time series data
- Detecting anomalies or change points in temporal sequences
- Clustering similar time series patterns
- Forecasting future values
- Finding repeated patterns (motifs) or unusual subsequences (discords)
- Comparing time series with specialized distance metrics
- Extracting features from temporal data

## Installation

Requires **Python 3.10+** (3.11+ recommended). Pin a 1.x release for reproducibility:

```bash
uv pip install "aeon>=1.4,<2"
```

For deep learning forecasters/classifiers and other optional estimators:

```bash
uv pip install "aeon[all_extras]>=1.4,<2"
```

On zsh, quote the extras: `uv pip install "aeon[all_extras]>=1.4,<2"`.

### Experimental modules

Upstream treats **forecasting**, **anomaly_detection**, **segmentation**, **similarity_search**, and **visualisation** as experimental — interfaces may change between minor releases. Prefer stable modules (classification, regression, clustering, distances, transformations) for production pipelines unless you need these tasks.

## Core Capabilities

### 1. Time Series Classification

Categorize time series into predefined classes. See `references/classification.md` for complete algorithm catalog.

**Quick Start:**
```python
from aeon.classification.convolution_based import RocketClassifier
from aeon.datasets import load_classification

# Load data
X_train, y_train = load_classification("GunPoint", split="train")
X_test, y_test = load_classification("GunPoint", split="test")

# Train classifier
clf = RocketClassifier(n_kernels=10000)
clf.fit(X_train, y_train)
accuracy = clf.score(X_test, y_test)
```

**Algorithm Selection:**
- **Speed + Performance**: `MiniRocketClassifier`, `Arsenal`
- **Maximum Accuracy**: `HIVECOTEV2`, `InceptionTimeClassifier`
- **Interpretability**: `ShapeletTransformClassifier`, `Catch22Classifier`
- **Small Datasets**: `KNeighborsTimeSeriesClassifier` with DTW distance

### 2. Time Series Regression

Predict continuous values from time series. See `references/regression.md` for algorithms.

**Quick Start:**
```python
from aeon.regression.convolution_based import RocketRegressor
from aeon.datasets import load_regression

X_train, y_train = load_regression("Covid3Month", split="train")
X_test, y_test = load_regression("Covid3Month", split="test")

reg = RocketRegressor()
reg.fit(X_train, y_train)
predictions = reg.predict(X_test)
```

### 3. Time Series Clustering

Group similar time series without labels. See `references/clustering.md` for methods.

**Quick Start:**
```python
from aeon.clustering import TimeSeriesKMeans

clusterer = TimeSeriesKMeans(
    n_clusters=3,
    distance="dtw",
    averaging_method="ba"
)
labels = clusterer.fit_predict(X_train)
centers = clusterer.cluster_centers_
```

### 4. Forecasting

Predict future time series values (experimental module in aeon 1.x). See `references/forecasting.md` for forecasters.

**Quick Start:**
```python
import numpy as np
from aeon.forecasting import NaiveForecaster
from aeon.forecasting.stats import ARIMA

y_train = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

# Set horizon in the constructor; predict passes the series to forecast from
naive = NaiveForecaster(strategy="last", horizon=5)
naive.fit(y_train)
y_pred = naive.predict(y_train)

# ARIMA uses p/d/q (not order=); multi-step via iterative_forecast
arima = ARIMA(p=1, d=1, q=1)
arima.fit(y_train)
y_pred = arima.iterative_forecast(y_train, prediction_horizon=5)
```

### 5. Anomaly Detection

Identify unusual patterns or outliers. See `references/anomaly_detection.md` for detectors.

**Quick Start:**
```python
from aeon.anomaly_detection import STOMP

detector = STOMP(window_size=50)
anomaly_scores = detector.fit_predict(y)

# Higher scores indicate anomalies
threshold = np.percentile(anomaly_scores, 95)
anomalies = anomaly_scores > threshold
```

### 6. Segmentation

Partition time series into regions with change points. See `references/segmentation.md`.

**Quick Start:**
```python
from aeon.segmentation import ClaSPSegmenter

segmenter = ClaSPSegmenter()
change_points = segmenter.fit_predict(y)
```

### 7. Similarity Search

Find similar patterns within or across time series. See `references/similarity_search.md`.

**Quick Start:**
```python
from aeon.similarity_search import StompMotif

# Find recurring patterns
motif_finder = StompMotif(window_size=50, k=3)
motifs = motif_finder.fit_predict(y)
```

## Feature Extraction and Transformations

Transform time series for feature engineering. See `references/transformations.md`.

**ROCKET Features:**
```python
from aeon.transformations.collection.convolution_based import RocketTransformer

rocket = RocketTransformer()
X_features = rocket.fit_transform(X_train)

# Use features with any sklearn classifier
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(X_features, y_train)
```

**Statistical Features:**
```python
from aeon.transformations.collection.feature_based import Catch22

catch22 = Catch22()
X_features = catch22.fit_transform(X_train)
```

**Preprocessing:**
```python
from aeon.transformations.collection import MinMaxScaler, Normalizer

scaler = Normalizer()  # Z-normalization
X_normalized = scaler.fit_transform(X_train)
```

## Distance Metrics

Specialized temporal distance measures. See `references/distances.md` for complete catalog.

**Usage:**
```python
from aeon.distances import dtw_distance, dtw_pairwise_distance

# Single distance
distance = dtw_distance(x, y, window=0.1)

# Pairwise distances
distance_matrix = dtw_pairwise_distance(X_train)

# Use with classifiers
from aeon.classification.distance_based import KNeighborsTimeSeriesClassifier

clf = KNeighborsTimeSeriesClassifier(
    n_neighbors=5,
    distance="dtw",
    distance_params={"window": 0.2}
)
```

**Available Distances:**
- **Elastic**: DTW, DDTW, WDTW, ERP, EDR, LCSS, TWE, MSM
- **Lock-step**: Euclidean, Manhattan, Minkowski
- **Shape-based**: Shape DTW, SBD

## Deep Learning Networks

Neural architectures for time series. See `references/networks.md`.

**Architectures:**
- Convolutional: `FCNClassifier`, `ResNetClassifier`, `InceptionTimeClassifier`
- Recurrent: `RecurrentNetwork`, `TCNNetwork`
- Autoencoders: `AEFCNClusterer`, `AEResNetClusterer`

**Usage:**
```python
from aeon.classification.deep_learning import InceptionTimeClassifier

clf = InceptionTimeClassifier(n_epochs=100, batch_size=32)
clf.fit(X_train, y_train)
predictions = clf.predict(X_test)
```

## Datasets and Benchmarking

Load standard benchmarks and evaluate performance. See `references/datasets_benchmarking.md`.

**Load Datasets:**
```python
from aeon.datasets import load_classification, load_gunpoint, load_regression

# Classification (generic loader or dataset-specific helper)
X_train, y_train = load_classification("GunPoint", split="train")
X_train, y_train = load_gunpoint(split="train")  # same UCR dataset

# Regression
X_train, y_train = load_regression("Covid3Month", split="train")
```

**Benchmarking:**
```python
from aeon.benchmarking import get_estimator_results

# Compare with published results
published = get_estimator_results("ROCKET", "GunPoint")
```

## Common Workflows

### Classification Pipeline

```python
from aeon.transformations.collection import Normalizer
from aeon.classification.convolution_based import RocketClassifier
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('normalize', Normalizer()),
    ('classify', RocketClassifier())
])

pipeline.fit(X_train, y_train)
accuracy = pipeline.score(X_test, y_test)
```

### Feature Extraction + Traditional ML

```python
from aeon.transformations.collection import RocketTransformer
from sklearn.ensemble import GradientBoostingClassifier

# Extract features
rocket = RocketTransformer()
X_train_features = rocket.fit_transform(X_train)
X_test_features = rocket.transform(X_test)

# Train traditional ML
clf = GradientBoostingClassifier()
clf.fit(X_train_features, y_train)
predictions = clf.predict(X_test_features)
```

### Anomaly Detection with Visualization

```python
from aeon.anomaly_detection import STOMP
import matplotlib.pyplot as plt

detector = STOMP(window_size=50)
scores = detector.fit_predict(y)

plt.figure(figsize=(15, 5))
plt.subplot(2, 1, 1)
plt.plot(y, label='Time Series')
plt.subplot(2, 1, 2)
plt.plot(scores, label='Anomaly Scores', color='red')
plt.axhline(np.percentile(scores, 95), color='k', linestyle='--')
plt.show()
```

## Best Practices

### Data Preparation

1. **Normalize**: Most algorithms benefit from z-normalization
   ```python
   from aeon.transformations.collection import Normalizer
   normalizer = Normalizer()
   X_train = normalizer.fit_transform(X_train)
   X_test = normalizer.transform(X_test)
   ```

2. **Handle Missing Values**: Impute before analysis
   ```python
   from aeon.transformations.collection import SimpleImputer
   imputer = SimpleImputer(strategy='mean')
   X_train = imputer.fit_transform(X_train)
   ```

3. **Check Data Format**: Collections use `(n_cases, n_channels, n_timepoints)`; single series use `(n_channels, n_timepoints)` (see [data format](https://www.aeon-toolkit.org/en/stable/api_reference/data_format.html))

### Model Selection

1. **Start Simple**: Begin with ROCKET variants before deep learning
2. **Use Validation**: Split training data for hyperparameter tuning
3. **Compare Baselines**: Test against simple methods (1-NN Euclidean, Naive)
4. **Consider Resources**: ROCKET for speed, deep learning if GPU available

### Algorithm Selection Guide

**For Fast Prototyping:**
- Classification: `MiniRocketClassifier`
- Regression: `MiniRocketRegressor`
- Clustering: `TimeSeriesKMeans` with Euclidean

**For Maximum Accuracy:**
- Classification: `HIVECOTEV2`, `InceptionTimeClassifier`
- Regression: `InceptionTimeRegressor`
- Forecasting: `AutoARIMA`, `AutoETS`, `TCNForecaster` (requires `[all_extras]` for deep learning)

**For Interpretability:**
- Classification: `ShapeletTransformClassifier`, `Catch22Classifier`
- Features: `Catch22`, `TSFresh`

**For Small Datasets:**
- Distance-based: `KNeighborsTimeSeriesClassifier` with DTW
- Avoid: Deep learning (requires large data)

## Reference Documentation

Detailed information available in `references/`:
- `classification.md` - All classification algorithms
- `regression.md` - Regression methods
- `clustering.md` - Clustering algorithms
- `forecasting.md` - Forecasting approaches
- `anomaly_detection.md` - Anomaly detection methods
- `segmentation.md` - Segmentation algorithms
- `similarity_search.md` - Pattern matching and motif discovery
- `transformations.md` - Feature extraction and preprocessing
- `distances.md` - Time series distance metrics
- `networks.md` - Deep learning architectures
- `datasets_benchmarking.md` - Data loading and evaluation tools

## Additional Resources

- Documentation: https://www.aeon-toolkit.org/
- GitHub: https://github.com/aeon-toolkit/aeon
- Examples: https://www.aeon-toolkit.org/en/stable/examples.html
- API Reference: https://www.aeon-toolkit.org/en/stable/api_reference.html

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/aeon/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/anomaly_detection.md`

# Anomaly Detection

Aeon provides anomaly detection methods for identifying unusual patterns in time series at both series and collection levels.

## Collection Anomaly Detectors

Detect anomalous time series within a collection:

- `ClassificationAdapter` - Adapts classifiers for anomaly detection
  - Train on normal data, flag outliers during prediction
  - **Use when**: Have labeled normal data, want classification-based approach

- `OutlierDetectionAdapter` - Wraps sklearn outlier detectors
  - Works with IsolationForest, LOF, OneClassSVM
  - **Use when**: Want to use sklearn anomaly detectors on collections

## Series Anomaly Detectors

Detect anomalous points or subsequences within a single time series.

### Distance-Based Methods

Use similarity metrics to identify anomalies:

- `CBLOF` - Cluster-Based Local Outlier Factor
  - Clusters data, identifies outliers based on cluster properties
  - **Use when**: Anomalies form sparse clusters

- `KMeansAD` - K-means based anomaly detection
  - Distance to nearest cluster center indicates anomaly
  - **Use when**: Normal patterns cluster well

- `LeftSTAMPi` - Left STAMP incremental
  - Matrix profile for online anomaly detection
  - **Use when**: Streaming data, need online detection

- `STOMP` - Scalable Time series Ordered-search Matrix Profile
  - Computes matrix profile for subsequence anomalies
  - **Use when**: Discord discovery, motif detection

- `MERLIN` - Matrix profile-based method
  - Efficient matrix profile computation
  - **Use when**: Large time series, need scalability

- `LOF` - Local Outlier Factor adapted for time series
  - Density-based outlier detection
  - **Use when**: Anomalies in low-density regions

- `ROCKAD` - ROCKET-based semi-supervised detection
  - Uses ROCKET features for anomaly identification
  - **Use when**: Have some labeled data, want feature-based approach

### Distribution-Based Methods

Analyze statistical distributions:

- `COPOD` - Copula-Based Outlier Detection
  - Models marginal and joint distributions
  - **Use when**: Multi-dimensional time series, complex dependencies

- `DWT_MLEAD` - Discrete Wavelet Transform Multi-Level Anomaly Detection
  - Decomposes series into frequency bands
  - **Use when**: Anomalies at specific frequencies

### Isolation-Based Methods

Use isolation principles:

- `IsolationForest` - Random forest-based isolation
  - Anomalies easier to isolate than normal points
  - **Use when**: High-dimensional data, no assumptions about distribution

- `OneClassSVM` - Support vector machine for novelty detection
  - Learns boundary around normal data
  - **Use when**: Well-defined normal region, need robust boundary

- `STRAY` - Streaming Robust Anomaly Detection
  - Robust to data distribution changes
  - **Use when**: Streaming data, distribution shifts

### External Library Integration

- `PyODAdapter` - Bridges PyOD library to aeon
  - Access 40+ PyOD anomaly detectors
  - **Use when**: Need specific PyOD algorithm

## Quick Start

```python
from aeon.anomaly_detection import STOMP
import numpy as np

# Create time series with anomaly
y = np.concatenate([
    np.sin(np.linspace(0, 10, 100)),
    [5.0],  # Anomaly spike
    np.sin(np.linspace(10, 20, 100))
])

# Detect anomalies
detector = STOMP(window_size=10)
anomaly_scores = detector.fit_predict(y)

# Higher scores indicate more anomalous points
threshold = np.percentile(anomaly_scores, 95)
anomalies = anomaly_scores > threshold
```

## Point vs Subsequence Anomalies

- **Point anomalies**: Single unusual values
  - Use: COPOD, DWT_MLEAD, IsolationForest

- **Subsequence anomalies** (discords): Unusual patterns
  - Use: STOMP, LeftSTAMPi, MERLIN

- **Collective anomalies**: Groups of points forming unusual pattern
  - Use: Matrix profile methods, clustering-based

## Evaluation Metrics

Specialized metrics for anomaly detection:

```python
from aeon.benchmarking.metrics.anomaly_detection import (
    range_precision,
    range_recall,
    range_f_score,
    roc_auc_score
)

# Range-based metrics account for window detection
precision = range_precision(y_true, y_pred, alpha=0.5)
recall = range_recall(y_true, y_pred, alpha=0.5)
f1 = range_f_score(y_true, y_pred, alpha=0.5)
```

## Algorithm Selection

- **Speed priority**: KMeansAD, IsolationForest
- **Accuracy priority**: STOMP, COPOD
- **Streaming data**: LeftSTAMPi, STRAY
- **Discord discovery**: STOMP, MERLIN
- **Multi-dimensional**: COPOD, PyODAdapter
- **Semi-supervised**: ROCKAD, OneClassSVM
- **No training data**: IsolationForest, STOMP

## Best Practices

1. **Normalize data**: Many methods sensitive to scale
2. **Choose window size**: For matrix profile methods, window size critical
3. **Set threshold**: Use percentile-based or domain-specific thresholds
4. **Validate results**: Visualize detections to verify meaningfulness
5. **Handle seasonality**: Detrend/deseasonalize before detection

### `references/classification.md`

# Time Series Classification

Aeon provides 13 categories of time series classifiers with scikit-learn compatible APIs.

## Convolution-Based Classifiers

Apply random convolutional transformations for efficient feature extraction:

- `Arsenal` - Ensemble of ROCKET classifiers with varied kernels
- `HydraClassifier` - Multi-resolution convolution with dilation
- `RocketClassifier` - Random convolution kernels with ridge regression
- `MiniRocketClassifier` - Simplified ROCKET variant for speed
- `MultiRocketClassifier` - Combines multiple ROCKET variants

**Use when**: Need fast, scalable classification with strong performance across diverse datasets.

## Deep Learning Classifiers

Neural network architectures optimized for temporal sequences:

- `FCNClassifier` - Fully convolutional network
- `ResNetClassifier` - Residual networks with skip connections
- `InceptionTimeClassifier` - Multi-scale inception modules
- `TimeCNNClassifier` - Standard CNN for time series
- `MLPClassifier` - Multi-layer perceptron baseline
- `EncoderClassifier` - Generic encoder wrapper
- `DisjointCNNClassifier` - Shapelet-focused architecture

**Use when**: Large datasets available, need end-to-end learning, or complex temporal patterns.

## Dictionary-Based Classifiers

Transform time series into symbolic representations:

- `BOSSEnsemble` - Bag-of-SFA-Symbols with ensemble voting
- `TemporalDictionaryEnsemble` - Multiple dictionary methods combined
- `WEASEL` - Word ExtrAction for time SEries cLassification
- `MrSEQLClassifier` - Multiple symbolic sequence learning

**Use when**: Need interpretable models, sparse patterns, or symbolic reasoning.

## Distance-Based Classifiers

Leverage specialized time series distance metrics:

- `KNeighborsTimeSeriesClassifier` - k-NN with temporal distances (DTW, LCSS, ERP, etc.)
- `ElasticEnsemble` - Combines multiple elastic distance measures
- `ProximityForest` - Tree ensemble using distance-based splits

**Use when**: Small datasets, need similarity-based classification, or interpretable decisions.

## Feature-Based Classifiers

Extract statistical and signature features before classification:

- `Catch22Classifier` - 22 canonical time-series characteristics
- `TSFreshClassifier` - Automated feature extraction via tsfresh
- `SignatureClassifier` - Path signature transformations
- `SummaryClassifier` - Summary statistics extraction
- `FreshPRINCEClassifier` - Combines multiple feature extractors

**Use when**: Need interpretable features, domain expertise available, or feature engineering approach.

## Interval-Based Classifiers

Extract features from random or supervised intervals:

- `CanonicalIntervalForestClassifier` - Random interval features with decision trees
- `DrCIFClassifier` - Diverse Representation CIF with catch22 features
- `TimeSeriesForestClassifier` - Random intervals with summary statistics
- `RandomIntervalClassifier` - Simple interval-based approach
- `RandomIntervalSpectralEnsembleClassifier` - Spectral features from intervals
- `SupervisedTimeSeriesForest` - Supervised interval selection

**Use when**: Discriminative patterns occur in specific time windows.

## Shapelet-Based Classifiers

Identify discriminative subsequences (shapelets):

- `ShapeletTransformClassifier` - Discovers and uses discriminative shapelets
- `LearningShapeletClassifier` - Learns shapelets via gradient descent
- `SASTClassifier` - Scalable approximate shapelet transform
- `RDSTClassifier` - Random dilated shapelet transform

**Use when**: Need interpretable discriminative patterns or phase-invariant features.

## Hybrid Classifiers

Combine multiple classification paradigms:

- `HIVECOTEV1` - Hierarchical Vote Collective of Transformation-based Ensembles (version 1)
- `HIVECOTEV2` - Enhanced version with updated components

**Use when**: Maximum accuracy required, computational resources available.

## Early Classification

Make predictions before observing entire time series:

- `TEASER` - Two-tier Early and Accurate Series Classifier
- `ProbabilityThresholdEarlyClassifier` - Prediction when confidence exceeds threshold

**Use when**: Real-time decisions needed, or observations have cost.

## Ordinal Classification

Handle ordered class labels:

- `OrdinalTDE` - Temporal dictionary ensemble for ordinal outputs

**Use when**: Classes have natural ordering (e.g., severity levels).

## Composition Tools

Build custom pipelines and ensembles:

- `ClassifierPipeline` - Chain transformers with classifiers
- `WeightedEnsembleClassifier` - Weighted combination of classifiers
- `SklearnClassifierWrapper` - Adapt sklearn classifiers for time series

## Quick Start

```python
from aeon.classification.convolution_based import RocketClassifier
from aeon.datasets import load_classification

# Load data
X_train, y_train = load_classification("GunPoint", split="train")
X_test, y_test = load_classification("GunPoint", split="test")

# Train and predict
clf = RocketClassifier()
clf.fit(X_train, y_train)
accuracy = clf.score(X_test, y_test)
```

## Algorithm Selection

- **Speed priority**: MiniRocketClassifier, Arsenal
- **Accuracy priority**: HIVECOTEV2, InceptionTimeClassifier
- **Interpretability**: ShapeletTransformClassifier, Catch22Classifier
- **Small data**: KNeighborsTimeSeriesClassifier, Distance-based methods
- **Large data**: Deep learning classifiers, ROCKET variants

### `references/clustering.md`

# Time Series Clustering

Aeon provides clustering algorithms adapted for temporal data with specialized distance metrics and averaging methods.

## Partitioning Algorithms

Standard k-means/k-medoids adapted for time series:

- `TimeSeriesKMeans` - K-means with temporal distance metrics (DTW, Euclidean, etc.)
- `TimeSeriesKMedoids` - Uses actual time series as cluster centers
- `TimeSeriesKShape` - Shape-based clustering algorithm
- `TimeSeriesKernelKMeans` - Kernel-based variant for nonlinear patterns

**Use when**: Known number of clusters, spherical cluster shapes expected.

## Large Dataset Methods

Efficient clustering for large collections:

- `TimeSeriesCLARA` - Clustering Large Applications with sampling
- `TimeSeriesCLARANS` - Randomized search variant of CLARA

**Use when**: Dataset too large for standard k-medoids, need scalability.

## Elastic Distance Clustering

Specialized for alignment-based similarity:

- `KASBA` - K-means with shift-invariant elastic averaging
- `ElasticSOM` - Self-organizing map using elastic distances

**Use when**: Time series have temporal shifts or warping.

## Spectral Methods

Graph-based clustering:

- `KSpectralCentroid` - Spectral clustering with centroid computation

**Use when**: Non-convex cluster shapes, need graph-based approach.

## Deep Learning Clustering

Neural network-based clustering with auto-encoders:

- `AEFCNClusterer` - Fully convolutional auto-encoder
- `AEResNetClusterer` - Residual network auto-encoder
- `AEDCNNClusterer` - Dilated CNN auto-encoder
- `AEDRNNClusterer` - Dilated RNN auto-encoder
- `AEBiGRUClusterer` - Bidirectional GRU auto-encoder
- `AEAttentionBiGRUClusterer` - Attention-enhanced BiGRU auto-encoder

**Use when**: Large datasets, need learned representations, or complex patterns.

## Feature-Based Clustering

Transform to feature space before clustering:

- `Catch22Clusterer` - Clusters on 22 canonical features
- `SummaryClusterer` - Uses summary statistics
- `TSFreshClusterer` - Automated tsfresh features

**Use when**: Raw time series not informative, need interpretable features.

## Composition

Build custom clustering pipelines:

- `ClustererPipeline` - Chain transformers with clusterers

## Averaging Methods

Compute cluster centers for time series:

- `mean_average` - Arithmetic mean
- `ba_average` - Barycentric averaging with DTW
- `kasba_average` - Shift-invariant averaging
- `shift_invariant_average` - General shift-invariant method

**Use when**: Need representative cluster centers for visualization or initialization.

## Quick Start

```python
from aeon.clustering import TimeSeriesKMeans
from aeon.datasets import load_classification

# Load data (using classification data for clustering)
X_train, _ = load_classification("GunPoint", split="train")

# Cluster time series
clusterer = TimeSeriesKMeans(
    n_clusters=3,
    distance="dtw",  # Use DTW distance
    averaging_method="ba"  # Barycentric averaging
)
labels = clusterer.fit_predict(X_train)
centers = clusterer.cluster_centers_
```

## Algorithm Selection

- **Speed priority**: TimeSeriesKMeans with Euclidean distance
- **Temporal alignment**: KASBA, TimeSeriesKMeans with DTW
- **Large datasets**: TimeSeriesCLARA, TimeSeriesCLARANS
- **Complex patterns**: Deep learning clusterers
- **Interpretability**: Catch22Clusterer, SummaryClusterer
- **Non-convex clusters**: KSpectralCentroid

## Distance Metrics

Compatible distance metrics include:
- Euclidean, Manhattan, Minkowski (lock-step)
- DTW, DDTW, WDTW (elastic with alignment)
- ERP, EDR, LCSS (edit-based)
- MSM, TWE (specialized elastic)

## Evaluation

Use clustering metrics from sklearn or aeon benchmarking:
- Silhouette score
- Davies-Bouldin index
- Calinski-Harabasz index

### `references/datasets_benchmarking.md`

# Datasets and Benchmarking

Aeon provides comprehensive tools for loading datasets and benchmarking time series algorithms.

From **aeon 1.4** onward, most classification and regression archives are hosted on **Zenodo** (including the relaunched Multiverse multivariate classification archive). Loaders download on first use; cache location follows aeon defaults.

## Dataset Loading

### Task-Specific Loaders

**Classification Datasets**:
```python
from aeon.datasets import load_classification

# Load train/test split (or use load_gunpoint for this benchmark)
from aeon.datasets import load_gunpoint

X_train, y_train = load_classification("GunPoint", split="train")
X_test, y_test = load_classification("GunPoint", split="test")
# X_train, y_train = load_gunpoint(split="train")

# Load entire dataset
X, y = load_classification("GunPoint")
```

**Regression Datasets**:
```python
from aeon.datasets import load_regression

X_train, y_train = load_regression("Covid3Month", split="train")
X_test, y_test = load_regression("Covid3Month", split="test")

# Bulk download
from aeon.datasets import download_all_regression
download_all_regression()  # Downloads Monash TSER archive
```

**Forecasting Datasets**:
```python
from aeon.datasets import load_forecasting

# Load from forecastingdata.org
y, X = load_forecasting("airline", return_X_y=True)
```

**Anomaly Detection Datasets**:
```python
from aeon.datasets import load_anomaly_detection

X, y = load_anomaly_detection("NAB_realKnownCause")
```

### File Format Loaders

**Load from .ts files**:
```python
from aeon.datasets import load_from_ts_file

X, y = load_from_ts_file("path/to/data.ts")
```

**Load from .tsf files**:
```python
from aeon.datasets import load_from_tsf_file

df, metadata = load_from_tsf_file("path/to/data.tsf")
```

**Load from ARFF files**:
```python
from aeon.datasets import load_from_arff_file

X, y = load_from_arff_file("path/to/data.arff")
```

**Load from TSV files**:
```python
from aeon.datasets import load_from_tsv_file

data = load_from_tsv_file("path/to/data.tsv")
```

**Load TimeEval CSV**:
```python
from aeon.datasets import load_from_timeeval_csv_file

X, y = load_from_timeeval_csv_file("path/to/timeeval.csv")
```

### Writing Datasets

**Write to .ts format**:
```python
from aeon.datasets import write_to_ts_file

write_to_ts_file(X, "output.ts", y=y, problem_name="MyDataset")
```

**Write to ARFF format**:
```python
from aeon.datasets import write_to_arff_file

write_to_arff_file(X, "output.arff", y=y)
```

## Built-in Datasets

Aeon includes several benchmark datasets for quick testing:

### Classification
- `ArrowHead` - Shape classification
- `GunPoint` - Gesture recognition
- `ItalyPowerDemand` - Energy demand
- `BasicMotions` - Motion classification
- And 100+ more from UCR/UEA archives

### Regression
- `Covid3Month` - COVID forecasting
- Various datasets from Monash TSER archive

### Segmentation
- Time series segmentation datasets
- Human activity data
- Sensor data collections

### Special Collections
- `RehabPile` - Rehabilitation data (classification & regression)

## Dataset Metadata

Get information about datasets:

```python
from aeon.datasets import get_dataset_meta_data

metadata = get_dataset_meta_data("GunPoint")
print(metadata)
# {'n_train': 50, 'n_test': 150, 'length': 150, 'n_classes': 2, ...}
```

## Benchmarking Tools

### Loading Published Results

Access pre-computed benchmark results:

```python
from aeon.benchmarking import get_estimator_results

# Get results for specific algorithm on dataset
results = get_estimator_results(
    estimator_name="ROCKET",
    dataset_name="GunPoint"
)

# Get all available estimators for a dataset
estimators = get_available_estimators("GunPoint")
```

### Resampling Strategies

Create reproducible train/test splits:

```python
from aeon.benchmarking import stratified_resample

# Stratified resampling maintaining class distribution
X_train, X_test, y_train, y_test = stratified_resample(
    X, y,
    random_state=42,
    test_size=0.3
)
```

### Performance Metrics

Specialized metrics for time series tasks:

**Anomaly Detection Metrics**:
```python
from aeon.benchmarking.metrics.anomaly_detection import (
    range_precision,
    range_recall,
    range_f_score,
    range_roc_auc_score
)

# Range-based metrics for window detection
precision = range_precision(y_true, y_pred, alpha=0.5)
recall = range_recall(y_true, y_pred, alpha=0.5)
f1 = range_f_score(y_true, y_pred, alpha=0.5)
auc = range_roc_auc_score(y_true, y_scores)
```

**Clustering Metrics**:
```python
from aeon.benchmarking.metrics.clustering import clustering_accuracy

# Clustering accuracy with label matching
accuracy = clustering_accuracy(y_true, y_pred)
```

**Segmentation Metrics**:
```python
from aeon.benchmarking.metrics.segmentation import (
    count_error,
    hausdorff_error
)

# Number of change points difference
count_err = count_error(y_true, y_pred)

# Maximum distance between predicted and true change points
hausdorff_err = hausdorff_error(y_true, y_pred)
```

### Statistical Testing

Post-hoc analysis for algorithm comparison:

```python
from aeon.benchmarking import (
    nemenyi_test,
    wilcoxon_test
)

# Nemenyi test for multiple algorithms
results = nemenyi_test(scores_matrix, alpha=0.05)

# Pairwise Wilcoxon signed-rank test
stat, p_value = wilcoxon_test(scores_alg1, scores_alg2)
```

## Benchmark Collections

### UCR/UEA Time Series Archives

Access to comprehensive benchmark repositories:

```python
# Classification: 112 univariate + 30 multivariate datasets
X_train, y_train = load_classification("Chinatown", split="train")

# Automatically downloads from timeseriesclassification.com
```

### Monash Forecasting Archive

```python
# Load forecasting datasets
y = load_forecasting("nn5_daily", return_X_y=False)
```

### Published Benchmark Results

Pre-computed results from major competitions:

- 2017 Univariate Bake-off
- 2021 Multivariate Classification
- 2023 Univariate Bake-off

## Workflow Example

Complete benchmarking workflow:

```python
from aeon.datasets import load_classification
from aeon.classification.convolution_based import RocketClassifier
from aeon.benchmarking import get_estimator_results
from sklearn.metrics import accuracy_score
import numpy as np

# Load dataset
dataset_name = "GunPoint"
X_train, y_train = load_classification(dataset_name, split="train")
X_test, y_test = load_classification(dataset_name, split="test")

# Train model
clf = RocketClassifier(n_kernels=10000, random_state=42)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Compare with published results
published = get_estimator_results("ROCKET", dataset_name)
print(f"Published ROCKET accuracy: {published['accuracy']:.4f}")
```

## Best Practices

### 1. Use Standard Splits

For reproducibility, use provided train/test splits:

```python
# Good: Use standard splits
X_train, y_train = load_classification("GunPoint", split="train")
X_test, y_test = load_classification("GunPoint", split="test")

# Avoid: Creating custom splits
X, y = load_classification("GunPoint")
X_train, X_test, y_train, y_test = train_test_split(X, y)
```

### 2. Set Random Seeds

Ensure reproducibility:

```python
clf = RocketClassifier(random_state=42)
results = stratified_resample(X, y, random_state=42)
```

### 3. Report Multiple Metrics

Don't rely on single metric:

```python
from sklearn.metrics import accuracy_score, f1_score, precision_score

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')
precision = precision_score(y_test, y_pred, average='weighted')
```

### 4. Cross-Validation

For robust evaluation on small datasets:

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(
    clf, X_train, y_train,
    cv=5,
    scoring='accuracy'
)
print(f"CV Accuracy: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### 5. Compare Against Baselines

Always compare with simple baselines:

```python
from aeon.classification.distance_based import KNeighborsTimeSeriesClassifier

# Simple baseline: 1-NN with Euclidean distance
baseline = KNeighborsTimeSeriesClassifier(n_neighbors=1, distance="euclidean")
baseline.fit(X_train, y_train)
baseline_acc = baseline.score(X_test, y_test)

print(f"Baseline: {baseline_acc:.4f}")
print(f"Your model: {accuracy:.4f}")
```

### 6. Statistical Significance

Test if improvements are statistically significant:

```python
from aeon.benchmarking import wilcoxon_test

# Run on multiple datasets
accuracies_alg1 = [0.85, 0.92, 0.78, 0.88]
accuracies_alg2 = [0.83, 0.90, 0.76, 0.86]

stat, p_value = wilcoxon_test(accuracies_alg1, accuracies_alg2)
if p_value < 0.05:
    print("Difference is statistically significant")
```

## Dataset Discovery

Find datasets matching criteria:

```python
# List all available classification datasets
from aeon.datasets import get_available_datasets

datasets = get_available_datasets("classification")
print(f"Found {len(datasets)} classification datasets")

# Filter by properties
univariate_datasets = [
    d for d in datasets
    if get_dataset_meta_data(d)['n_channels'] == 1
]
```

### `references/distances.md`

# Distance Metrics

Aeon provides specialized distance functions for measuring similarity between time series, compatible with both aeon and scikit-learn estimators.

## Distance Categories

### Elastic Distances

Allow flexible temporal alignment between series:

**Dynamic Time Warping Family:**
- `dtw` - Classic Dynamic Time Warping
- `ddtw` - Derivative DTW (compares derivatives)
- `wdtw` - Weighted DTW (penalizes warping by location)
- `wddtw` - Weighted Derivative DTW
- `shape_dtw` - Shape-based DTW

**Edit-Based:**
- `erp` - Edit distance with Real Penalty
- `edr` - Edit Distance on Real sequences
- `lcss` - Longest Common SubSequence
- `twe` - Time Warp Edit distance

**Specialized:**
- `msm` - Move-Split-Merge distance
- `adtw` - Amerced DTW
- `sbd` - Shape-Based Distance

**Use when**: Time series may have temporal shifts, speed variations, or phase differences.

### Lock-Step Distances

Compare time series point-by-point without alignment:

- `euclidean` - Euclidean distance (L2 norm)
- `manhattan` - Manhattan distance (L1 norm)
- `minkowski` - Generalized Minkowski distance (Lp norm)
- `squared` - Squared Euclidean distance

**Use when**: Series already aligned, need computational speed, or no temporal warping expected.

## Usage Patterns

### Computing Single Distance

```python
from aeon.distances import dtw_distance

# Distance between two time series
distance = dtw_distance(x, y)

# With window constraint (Sakoe-Chiba band)
distance = dtw_distance(x, y, window=0.1)
```

### Pairwise Distance Matrix

```python
from aeon.distances import dtw_pairwise_distance

# All pairwise distances in collection
X = [series1, series2, series3, series4]
distance_matrix = dtw_pairwise_distance(X)

# Cross-collection distances
distance_matrix = dtw_pairwise_distance(X_train, X_test)
```

### Cost Matrix and Alignment Path

```python
from aeon.distances import dtw_cost_matrix, dtw_alignment_path

# Get full cost matrix
cost_matrix = dtw_cost_matrix(x, y)

# Get optimal alignment path
path = dtw_alignment_path(x, y)
# Returns indices: [(0,0), (1,1), (2,1), (2,2), ...]
```

### Using with Estimators

```python
from aeon.classification.distance_based import KNeighborsTimeSeriesClassifier

# Use DTW distance in classifier
clf = KNeighborsTimeSeriesClassifier(
    n_neighbors=5,
    distance="dtw",
    distance_params={"window": 0.2}
)
clf.fit(X_train, y_train)
```

## Distance Parameters

### Window Constraints

Limit warping path deviation (improves speed and prevents pathological warping):

```python
# Sakoe-Chiba band: window as fraction of series length
dtw_distance(x, y, window=0.1)  # Allow 10% deviation

# Itakura parallelogram: slopes constrain path
dtw_distance(x, y, itakura_max_slope=2.0)
```

### Normalization

Control whether to z-normalize series before distance computation:

```python
# Most elastic distances support normalization
distance = dtw_distance(x, y, normalize=True)
```

### Distance-Specific Parameters

```python
# ERP: penalty for gaps
distance = erp_distance(x, y, g=0.5)

# TWE: stiffness and penalty parameters
distance = twe_distance(x, y, nu=0.001, lmbda=1.0)

# LCSS: epsilon threshold for matching
distance = lcss_distance(x, y, epsilon=0.5)
```

## Algorithm Selection

### By Use Case:

**Temporal misalignment**: DTW, DDTW, WDTW
**Speed variations**: DTW with window constraint
**Shape similarity**: Shape DTW, SBD
**Edit operations**: ERP, EDR, LCSS
**Derivative matching**: DDTW
**Computational speed**: Euclidean, Manhattan
**Outlier robustness**: Manhattan, LCSS

### By Computational Cost:

**Fastest**: Euclidean (O(n))
**Fast**: Constrained DTW (O(nw) where w is window)
**Medium**: Full DTW (O(n²))
**Slower**: Complex elastic distances (ERP, TWE, MSM)

## Quick Reference Table

| Distance | Alignment | Speed | Robustness | Interpretability |
|----------|-----------|-------|------------|------------------|
| Euclidean | Lock-step | Very Fast | Low | High |
| DTW | Elastic | Medium | Medium | Medium |
| DDTW | Elastic | Medium | High | Medium |
| WDTW | Elastic | Medium | Medium | Medium |
| ERP | Edit-based | Slow | High | Low |
| LCSS | Edit-based | Slow | Very High | Low |
| Shape DTW | Elastic | Medium | Medium | High |

## Best Practices

### 1. Normalization

Most distances sensitive to scale; normalize when appropriate:

```python
from aeon.transformations.collection import Normalizer

normalizer = Normalizer()
X_normalized = normalizer.fit_transform(X)
```

### 2. Window Constraints

For DTW variants, use window constraints for speed and better generalization:

```python
# Start with 10-20% window
distance = dtw_distance(x, y, window=0.1)
```

### 3. Series Length

- Equal-length required: Most lock-step distances
- Unequal-length supported: Elastic distances (DTW, ERP, etc.)

### 4. Multivariate Series

Most distances support multivariate time series:

```python
# x.shape = (n_channels, n_timepoints)
distance = dtw_distance(x_multivariate, y_multivariate)
```

### 5. Performance Optimization

- Use numba-compiled implementations (default in aeon)
- Consider lock-step distances if alignment not needed
- Use windowed DTW instead of full DTW
- Precompute distance matrices for repeated use

### 6. Choosing the Right Distance

```python
# Quick decision tree:
if series_aligned:
    use_distance = "euclidean"
elif need_speed:
    use_distance = "dtw"  # with window constraint
elif temporal_shifts_expected:
    use_distance = "dtw" or "shape_dtw"
elif outliers_present:
    use_distance = "lcss" or "manhattan"
elif derivatives_matter:
    use_distance = "ddtw" or "wddtw"
```

## Integration with scikit-learn

Aeon distances work with sklearn estimators:

```python
from sklearn.neighbors import KNeighborsClassifier
from aeon.distances import dtw_pairwise_distance

# Precompute distance matrix
X_train_distances = dtw_pairwise_distance(X_train)

# Use with sklearn
clf = KNeighborsClassifier(metric='precomputed')
clf.fit(X_train_distances, y_train)
```

## Available Distance Functions

Get list of all available distances:

```python
from aeon.distances import get_distance_function_names

print(get_distance_function_names())
# ['dtw', 'ddtw', 'wdtw', 'euclidean', 'erp', 'edr', ...]
```

Retrieve specific distance function:

```python
from aeon.distances import get_distance_function

distance_func = get_distance_function("dtw")
result = distance_func(x, y, window=0.1)
```

### `references/forecasting.md`

# Time Series Forecasting

The `aeon.forecasting` module provides forecasters for univariate and multivariate series. In aeon **1.x**, forecasting was rebuilt on array-native `BaseForecaster` estimators (replacing the old sktime-style `fh` API). The module is marked **experimental** — expect API evolution between releases.

Import paths (aeon 1.4+):

- `from aeon.forecasting import NaiveForecaster, RegressionForecaster`
- `from aeon.forecasting.stats import ARIMA, AutoARIMA, ETS, AutoETS, Theta, TAR, AutoTAR, TVP`
- `from aeon.forecasting.deep_learning import TCNForecaster, DeepARForecaster`

List all forecasters: `aeon.utils.discovery.all_estimators(type_filter="forecaster")`.

## Naive and Baseline Methods

- `NaiveForecaster` — `strategy` in `"last"`, `"mean"`, `"seasonal_last"`; set `horizon` and `seasonal_period` in the constructor
  - **Use when**: Establishing baselines or simple patterns

## Statistical Models

- `ARIMA` / `AutoARIMA` — `p`, `d`, `q` orders (not `order=(p,d,q)`); supports exogenous variables via `exog`
- `ETS` / `AutoETS` — exponential smoothing (native implementations in aeon 1.4+)
- `Theta` — classical Theta method
- `TAR` / `AutoTAR` — threshold autoregressive models for regime switching
- `TVP` — time-varying parameter (Kalman-style) models

## Deep Learning Forecasters

Requires `aeon[all_extras]` (PyTorch stack):

- `TCNForecaster` — temporal convolutional network
- `DeepARForecaster` — probabilistic RNN forecaster (replaces legacy `DeepARNetwork` naming)

## Regression-Based Forecasting

- `RegressionForecaster` — sliding `window` over history, `horizon` steps ahead, any sklearn/aeon regressor

## Quick Start

```python
import numpy as np
from aeon.forecasting import NaiveForecaster
from aeon.forecasting.stats import ARIMA, AutoETS

y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])

# Naive — horizon is a constructor argument; predict(y) forecasts from series y
naive = NaiveForecaster(strategy="last", horizon=3)
naive.fit(y)
pred_naive = naive.predict(y)

# ARIMA — one-step by default; multi-step via iterative_forecast
arima = ARIMA(p=1, d=1, q=1)
arima.fit(y)
pred_arima = arima.iterative_forecast(y, prediction_horizon=3)

# Auto model selection
auto_ets = AutoETS(horizon=3)
auto_ets.fit(y)
pred_ets = auto_ets.predict(y)
```

## Forecasting Horizon

In aeon 1.x, set `horizon` on the estimator (number of steps ahead). `predict(y)` returns the forecast `horizon` steps beyond the end of `y`.

Multi-step strategies:

- **`iterative_forecast(y, prediction_horizon)`** — reuse one fitted model, feed predictions back (ARIMA, many stats models)
- **`direct_forecast(y, prediction_horizon)`** — refit per horizon (requires `capability:horizon` tag; e.g. `RegressionForecaster`)
- **`NaiveForecaster`** — set `horizon>1` directly when `strategy` supports it

There is no `ForecastingHorizon` / `fh=[1,2,3]` API in aeon 1.x.

## Model Selection

- **Baseline**: `NaiveForecaster(strategy="seasonal_last", seasonal_period=12, horizon=h)`
- **Linear / stationary**: `ARIMA`, `AutoARIMA`
- **Trend + seasonality**: `ETS`, `AutoETS`
- **Regime changes**: `TAR`, `AutoTAR`
- **Complex patterns**: `TCNForecaster`, `RegressionForecaster` with aeon regressors
- **Probabilistic**: `DeepARForecaster`

## Evaluation Metrics

Use scikit-learn or standard numpy metrics on hold-out forecasts:

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(y_true, y_pred)
mse = mean_squared_error(y_true, y_pred)
```

## Exogenous Variables

Pass aligned exogenous arrays as `exog` (not `X`):

```python
forecaster.fit(y_train, exog=exog_train)
y_pred = forecaster.predict(y_test, exog=exog_test)
```

## Base Classes

- `BaseForecaster` — `horizon`, `axis`, `fit`, `predict`, `forecast`
- `DirectForecastingMixin` / `IterativeForecastingMixin` — multi-step helpers
- `BaseDeepForecaster` — deep learning forecasters

Extend `BaseForecaster` for custom forecasters.

### `references/networks.md`

# Deep Learning Networks

Aeon provides neural network architectures specifically designed for time series tasks. These networks serve as building blocks for classification, regression, clustering, and forecasting.

## Core Network Architectures

### Convolutional Networks

**FCNNetwork** - Fully Convolutional Network
- Three convolutional blocks with batch normalization
- Global average pooling for dimensionality reduction
- **Use when**: Need simple yet effective CNN baseline

**ResNetNetwork** - Residual Network
- Residual blocks with skip connections
- Prevents vanishing gradients in deep networks
- **Use when**: Deep networks needed, training stability important

**InceptionNetwork** - Inception Modules
- Multi-scale feature extraction with parallel convolutions
- Different kernel sizes capture patterns at various scales
- **Use when**: Patterns exist at multiple temporal scales

**TimeCNNNetwork** - Standard CNN
- Basic convolutional architecture
- **Use when**: Simple CNN sufficient, interpretability valued

**DisjointCNNNetwork** - Separate Pathways
- Disjoint convolutional pathways
- **Use when**: Different feature extraction strategies needed

**DCNNNetwork** - Dilated CNN
- Dilated convolutions for large receptive fields
- **Use when**: Long-range dependencies without many layers

### Recurrent Networks

**RecurrentNetwork** - RNN/LSTM/GRU
- Configurable cell type (RNN, LSTM, GRU)
- Sequential modeling of temporal dependencies
- **Use when**: Sequential dependencies critical, variable-length series

### Temporal Convolutional Network

**TCNNetwork** - Temporal Convolutional Network
- Dilated causal convolutions
- Large receptive field without recurrence
- **Use when**: Long sequences, need parallelizable architecture

### Multi-Layer Perceptron

**MLPNetwork** - Basic Feedforward
- Simple fully-connected layers
- Flattens time series before processing
- **Use when**: Baseline needed, computational limits, or simple patterns

## Encoder-Based Architectures

Networks designed for representation learning and clustering.

### Autoencoder Variants

**EncoderNetwork** - Generic Encoder
- Flexible encoder structure
- **Use when**: Custom encoding needed

**AEFCNNetwork** - FCN-based Autoencoder
- Fully convolutional encoder-decoder
- **Use when**: Need convolutional representation learning

**AEResNetNetwork** - ResNet Autoencoder
- Residual blocks in encoder-decoder
- **Use when**: Deep autoencoding with skip connections

**AEDCNNNetwork** - Dilated CNN Autoencoder
- Dilated convolutions for compression
- **Use when**: Need large receptive field in autoencoder

**AEDRNNNetwork** - Dilated RNN Autoencoder
- Dilated recurrent connections
- **Use when**: Sequential patterns with long-range dependencies

**AEBiGRUNetwork** - Bidirectional GRU
- Bidirectional recurrent encoding
- **Use when**: Context from both directions helpful

**AEAttentionBiGRUNetwork** - Attention + BiGRU
- Attention mechanism on BiGRU outputs
- **Use when**: Need to focus on important time steps

## Specialized Architectures

**LITENetwork** - Lightweight Inception Time Ensemble
- Efficient inception-based architecture
- LITEMV variant for multivariate series
- **Use when**: Need efficiency with strong performance

**DeepARForecaster** - Probabilistic forecasting (use via `aeon.forecasting.deep_learning`)
- Autoregressive RNN for forecasting
- Produces probabilistic predictions
- **Use when**: Need forecast uncertainty quantification

## Usage with Estimators

Networks are typically used within estimators, not directly:

```python
from aeon.classification.deep_learning import FCNClassifier
from aeon.regression.deep_learning import ResNetRegressor
from aeon.clustering.deep_learning import AEFCNClusterer

# Classification with FCN
clf = FCNClassifier(n_epochs=100, batch_size=16)
clf.fit(X_train, y_train)

# Regression with ResNet
reg = ResNetRegressor(n_epochs=100)
reg.fit(X_train, y_train)

# Clustering with autoencoder
clusterer = AEFCNClusterer(n_clusters=3, n_epochs=100)
labels = clusterer.fit_predict(X_train)
```

## Custom Network Configuration

Many networks accept configuration parameters:

```python
# Configure FCN layers
clf = FCNClassifier(
    n_epochs=200,
    batch_size=32,
    kernel_size=[7, 5, 3],  # Kernel sizes for each layer
    n_filters=[128, 256, 128],  # Filters per layer
    learning_rate=0.001
)
```

## Base Classes

- `BaseDeepLearningNetwork` - Abstract base for all networks
- `BaseDeepRegressor` - Base for deep regression
- `BaseDeepClassifier` - Base for deep classification
- `BaseDeepForecaster` - Base for deep forecasting

Extend these to implement custom architectures.

## Training Considerations

### Hyperparameters

Key hyperparameters to tune:

- `n_epochs` - Training iterations (50-200 typical)
- `batch_size` - Samples per batch (16-64 typical)
- `learning_rate` - Step size (0.0001-0.01)
- Network-specific: layers, filters, kernel sizes

### Callbacks

Many networks support callbacks for training monitoring:

```python
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

clf = FCNClassifier(
    n_epochs=200,
    callbacks=[
        EarlyStopping(patience=20, restore_best_weights=True),
        ReduceLROnPlateau(patience=10, factor=0.5)
    ]
)
```

### GPU Acceleration

Deep learning networks benefit from GPU:

```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Use first GPU

# Networks automatically use GPU if available
clf = InceptionTimeClassifier(n_epochs=100)
clf.fit(X_train, y_train)
```

## Architecture Selection

### By Task:

**Classification**: InceptionNetwork, ResNetNetwork, FCNNetwork
**Regression**: InceptionNetwork, ResNetNetwork, TCNNetwork
**Forecasting**: TCNForecaster, DeepARForecaster, RecurrentNetwork
**Clustering**: AEFCNNetwork, AEResNetNetwork, AEAttentionBiGRUNetwork

### By Data Characteristics:

**Long sequences**: TCNNetwork, DCNNNetwork (dilated convolutions)
**Short sequences**: MLPNetwork, FCNNetwork
**Multivariate**: InceptionNetwork, FCNNetwork, LITENetwork
**Variable length**: RecurrentNetwork with masking
**Multi-scale patterns**: InceptionNetwork

### By Computational Resources:

**Limited compute**: MLPNetwork, LITENetwork
**Moderate compute**: FCNNetwork, TimeCNNNetwork
**High compute available**: InceptionNetwork, ResNetNetwork
**GPU available**: Any deep network (major speedup)

## Best Practices

### 1. Data Preparation

Normalize input data:

```python
from aeon.transformations.collection import Normalizer

normalizer = Normalizer()
X_train_norm = normalizer.fit_transform(X_train)
X_test_norm = normalizer.transform(X_test)
```

### 2. Training/Validation Split

Use validation set for early stopping:

```python
from sklearn.model_selection import train_test_split

X_train_fit, X_val, y_train_fit, y_val = train_test_split(
    X_train, y_train, test_size=0.2, stratify=y_train
)

clf = FCNClassifier(n_epochs=200)
clf.fit(X_train_fit, y_train_fit, validation_data=(X_val, y_val))
```

### 3. Start Simple

Begin with simpler architectures before complex ones:

1. Try MLPNetwork or FCNNetwork first
2. If insufficient, try ResNetNetwork or InceptionNetwork
3. Consider ensembles if single models insufficient

### 4. Hyperparameter Tuning

Use grid search or random search:

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_epochs': [100, 200],
    'batch_size': [16, 32],
    'learning_rate': [0.001, 0.0001]
}

clf = FCNClassifier()
grid = GridSearchCV(clf, param_grid, cv=3)
grid.fit(X_train, y_train)
```

### 5. Regularization

Prevent overfitting:
- Use dropout (if network supports)
- Early stopping
- Data augmentation (if available)
- Reduce model complexity

### 6. Reproducibility

Set random seeds:

```python
import numpy as np
import random
import tensorflow as tf

seed = 42
np.random.seed(seed)
random.seed(seed)
tf.random.set_seed(seed)
```

### `references/regression.md`

# Time Series Regression

Aeon provides time series regressors across 9 categories for predicting continuous values from temporal sequences.

## Convolution-Based Regressors

Apply convolutional kernels for feature extraction:

- `HydraRegressor` - Multi-resolution dilated convolutions
- `RocketRegressor` - Random convolutional kernels
- `MiniRocketRegressor` - Simplified ROCKET for speed
- `MultiRocketRegressor` - Combined ROCKET variants
- `MultiRocketHydraRegressor` - Merges ROCKET and Hydra approaches

**Use when**: Need fast regression with strong baseline performance.

## Deep Learning Regressors

Neural architectures for end-to-end temporal regression:

- `FCNRegressor` - Fully convolutional network
- `ResNetRegressor` - Residual blocks with skip connections
- `InceptionTimeRegressor` - Multi-scale inception modules
- `TimeCNNRegressor` - Standard CNN architecture
- `RecurrentRegressor` - RNN/LSTM/GRU variants
- `MLPRegressor` - Multi-layer perceptron
- `EncoderRegressor` - Generic encoder wrapper
- `LITERegressor` - Lightweight inception time ensemble
- `DisjointCNNRegressor` - Specialized CNN architecture

**Use when**: Large datasets, complex patterns, or need feature learning.

## Distance-Based Regressors

k-nearest neighbors with temporal distance metrics:

- `KNeighborsTimeSeriesRegressor` - k-NN with DTW, LCSS, ERP, or other distances

**Use when**: Small datasets, local similarity patterns, or interpretable predictions.

## Feature-Based Regressors

Extract statistical features before regression:

- `Catch22Regressor` - 22 canonical time-series characteristics
- `FreshPRINCERegressor` - Pipeline combining multiple feature extractors
- `SummaryRegressor` - Summary statistics features
- `TSFreshRegressor` - Automated tsfresh feature extraction

**Use when**: Need interpretable features or domain-specific feature engineering.

## Hybrid Regressors

Combine multiple approaches:

- `RISTRegressor` - Randomized Interval-Shapelet Transformation

**Use when**: Benefit from combining interval and shapelet methods.

## Interval-Based Regressors

Extract features from time intervals:

- `CanonicalIntervalForestRegressor` - Random intervals with decision trees
- `DrCIFRegressor` - Diverse Representation CIF
- `TimeSeriesForestRegressor` - Random interval ensemble
- `RandomIntervalRegressor` - Simple interval-based approach
- `RandomIntervalSpectralEnsembleRegressor` - Spectral interval features
- `QUANTRegressor` - Quantile-based interval features

**Use when**: Predictive patterns occur in specific time windows.

## Shapelet-Based Regressors

Use discriminative subsequences for prediction:

- `RDSTRegressor` - Random Dilated Shapelet Transform

**Use when**: Need phase-invariant discriminative patterns.

## Composition Tools

Build custom regression pipelines:

- `RegressorPipeline` - Chain transformers with regressors
- `RegressorEnsemble` - Weighted ensemble with learnable weights
- `SklearnRegressorWrapper` - Adapt sklearn regressors for time series

## Utilities

- `DummyRegressor` - Baseline strategies (mean, median)
- `BaseRegressor` - Abstract base for custom regressors
- `BaseDeepRegressor` - Base for deep learning regressors

## Quick Start

```python
from aeon.regression.convolution_based import RocketRegressor
from aeon.datasets import load_regression

# Load data
X_train, y_train = load_regression("Covid3Month", split="train")
X_test, y_test = load_regression("Covid3Month", split="test")

# Train and predict
reg = RocketRegressor()
reg.fit(X_train, y_train)
predictions = reg.predict(X_test)
```

## Algorithm Selection

- **Speed priority**: MiniRocketRegressor
- **Accuracy priority**: InceptionTimeRegressor, MultiRocketHydraRegressor
- **Interpretability**: Catch22Regressor, SummaryRegressor
- **Small data**: KNeighborsTimeSeriesRegressor
- **Large data**: Deep learning regressors, ROCKET variants
- **Interval patterns**: DrCIFRegressor, CanonicalIntervalForestRegressor

### `references/segmentation.md`

# Time Series Segmentation

Aeon provides algorithms to partition time series into regions with distinct characteristics, identifying change points and boundaries.

## Segmentation Algorithms

### Binary Segmentation
- `BinSegmenter` - Recursive binary segmentation
  - Iteratively splits series at most significant change points
  - Parameters: `n_segments`, `cost_function`
  - **Use when**: Known number of segments, hierarchical structure

### Classification-Based
- `ClaSPSegmenter` - Classification Score Profile
  - Uses classification performance to identify boundaries
  - Discovers segments where classification distinguishes neighbors
  - **Use when**: Segments have different temporal patterns

### Fast Pattern-Based
- `FLUSSSegmenter` - Fast Low-cost Unipotent Semantic Segmentation
  - Efficient semantic segmentation using arc crossings
  - Based on matrix profile
  - **Use when**: Large time series, need speed and pattern discovery

### Information Theory
- `InformationGainSegmenter` - Information gain maximization
  - Finds boundaries maximizing information gain
  - **Use when**: Statistical differences between segments

### Gaussian Modeling
- `GreedyGaussianSegmenter` - Greedy Gaussian approximation
  - Models segments as Gaussian distributions
  - Incrementally adds change points
  - **Use when**: Segments follow Gaussian distributions

### Hierarchical Agglomerative
- `EAggloSegmenter` - Bottom-up merging approach
  - Estimates change points via agglomeration
  - **Use when**: Want hierarchical segmentation structure

### Hidden Markov Models
- `HMMSegmenter` - HMM with Viterbi decoding
  - Probabilistic state-based segmentation
  - **Use when**: Segments represent hidden states

### Dimensionality-Based
- `HidalgoSegmenter` - Heterogeneous Intrinsic Dimensionality Algorithm
  - Detects changes in local dimensionality
  - **Use when**: Dimensionality shifts between segments

### Baseline
- `RandomSegmenter` - Random change point generation
  - **Use when**: Need null hypothesis baseline

## Quick Start

```python
from aeon.segmentation import ClaSPSegmenter
import numpy as np

# Create time series with regime changes
y = np.concatenate([
    np.sin(np.linspace(0, 10, 100)),      # Segment 1
    np.cos(np.linspace(0, 10, 100)),      # Segment 2
    np.sin(2 * np.linspace(0, 10, 100))   # Segment 3
])

# Segment the series
segmenter = ClaSPSegmenter()
change_points = segmenter.fit_predict(y)

print(f"Detected change points: {change_points}")
```

## Output Format

Segmenters return change point indices:

```python
# change_points = [100, 200]  # Boundaries between segments
# This divides series into: [0:100], [100:200], [200:end]
```

## Algorithm Selection

- **Speed priority**: FLUSSSegmenter, BinSegmenter
- **Accuracy priority**: ClaSPSegmenter, HMMSegmenter
- **Known segment count**: BinSegmenter with n_segments parameter
- **Unknown segment count**: ClaSPSegmenter, InformationGainSegmenter
- **Pattern changes**: FLUSSSegmenter, ClaSPSegmenter
- **Statistical changes**: InformationGainSegmenter, GreedyGaussianSegmenter
- **State transitions**: HMMSegmenter

## Common Use Cases

### Regime Change Detection
Identify when time series behavior fundamentally changes:

```python
from aeon.segmentation import InformationGainSegmenter

segmenter = InformationGainSegmenter(k=3)  # Up to 3 change points
change_points = segmenter.fit_predict(stock_prices)
```

### Activity Segmentation
Segment sensor data into activities:

```python
from aeon.segmentation import ClaSPSegmenter

segmenter = ClaSPSegmenter()
boundaries = segmenter.fit_predict(accelerometer_data)
```

### Seasonal Boundary Detection
Find season transitions in time series:

```python
from aeon.segmentation import HMMSegmenter

segmenter = HMMSegmenter(n_states=4)  # 4 seasons
segments = segmenter.fit_predict(temperature_data)
```

## Evaluation Metrics

Use segmentation quality metrics:

```python
from aeon.benchmarking.metrics.segmentation import (
    count_error,
    hausdorff_error
)

# Count error: difference in number of change points
count_err = count_error(y_true, y_pred)

# Hausdorff: maximum distance between predicted and true points
hausdorff_err = hausdorff_error(y_true, y_pred)
```

## Best Practices

1. **Normalize data**: Ensures change detection not dominated by scale
2. **Choose appropriate metric**: Different algorithms optimize different criteria
3. **Validate segments**: Visualize to verify meaningful boundaries
4. **Handle noise**: Consider smoothing before segmentation
5. **Domain knowledge**: Use expected segment count if known
6. **Parameter tuning**: Adjust sensitivity parameters (thresholds, penalties)

## Visualization

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))
plt.plot(y, label='Time Series')
for cp in change_points:
    plt.axvline(cp, color='r', linestyle='--', label='Change Point')
plt.legend()
plt.show()
```

### `references/similarity_search.md`

# Similarity Search

Aeon provides tools for finding similar patterns within and across time series, including subsequence search, motif discovery, and approximate nearest neighbors.

## Subsequence Nearest Neighbors (SNN)

Find most similar subsequences within a time series.

### MASS Algorithm
- `MassSNN` - Mueen's Algorithm for Similarity Search
  - Fast normalized cross-correlation for similarity
  - Computes distance profile efficiently
  - **Use when**: Need exact nearest neighbor distances, large series

### STOMP-Based Motif Discovery
- `StompMotif` - Discovers recurring patterns (motifs)
  - Finds top-k most similar subsequence pairs
  - Based on matrix profile computation
  - **Use when**: Want to discover repeated patterns

### Brute Force Baseline
- `DummySNN` - Exhaustive distance computation
  - Computes all pairwise distances
  - **Use when**: Small series, need exact baseline

## Collection-Level Search

Find similar time series across collections.

### Approximate Nearest Neighbors (ANN)
- `RandomProjectionIndexANN` - Locality-sensitive hashing
  - Uses random projections with cosine similarity
  - Builds index for fast approximate search
  - **Use when**: Large collection, speed more important than exactness

## Quick Start: Motif Discovery

```python
from aeon.similarity_search import StompMotif
import numpy as np

# Create time series with repeated patterns
pattern = np.sin(np.linspace(0, 2*np.pi, 50))
y = np.concatenate([
    pattern + np.random.normal(0, 0.1, 50),
    np.random.normal(0, 1, 100),
    pattern + np.random.normal(0, 0.1, 50),
    np.random.normal(0, 1, 100)
])

# Find top-3 motifs
motif_finder = StompMotif(window_size=50, k=3)
motifs = motif_finder.fit_predict(y)

# motifs contains indices of motif occurrences
for i, (idx1, idx2) in enumerate(motifs):
    print(f"Motif {i+1} at positions {idx1} and {idx2}")
```

## Quick Start: Subsequence Search

```python
from aeon.similarity_search import MassSNN
import numpy as np

# Time series to search within
y = np.sin(np.linspace(0, 20, 500))

# Query subsequence
query = np.sin(np.linspace(0, 2, 50))

# Find nearest subsequences
searcher = MassSNN()
distances = searcher.fit_transform(y, query)

# Find best match
best_match_idx = np.argmin(distances)
print(f"Best match at index {best_match_idx}")
```

## Quick Start: Approximate NN on Collections

```python
from aeon.similarity_search import RandomProjectionIndexANN
from aeon.datasets import load_classification

# Load time series collection
X_train, _ = load_classification("GunPoint", split="train")

# Build index
ann = RandomProjectionIndexANN(n_projections=8, n_bits=4)
ann.fit(X_train)

# Find approximate nearest neighbors
query = X_train[0]
neighbors, distances = ann.kneighbors(query, k=5)
```

## Matrix Profile

The matrix profile is a fundamental data structure for many similarity search tasks:

- **Distance Profile**: Distances from a query to all subsequences
- **Matrix Profile**: Minimum distance for each subsequence to any other
- **Motif**: Pair of subsequences with minimum distance
- **Discord**: Subsequence with maximum minimum distance (anomaly)

```python
from aeon.similarity_search import StompMotif

# Compute matrix profile and find motifs/discords
mp = StompMotif(window_size=50)
mp.fit(y)

# Access matrix profile
profile = mp.matrix_profile_
profile_indices = mp.matrix_profile_index_

# Find discords (anomalies)
discord_idx = np.argmax(profile)
```

## Algorithm Selection

- **Exact subsequence search**: MassSNN
- **Motif discovery**: StompMotif
- **Anomaly detection**: Matrix profile (see anomaly_detection.md)
- **Fast approximate search**: RandomProjectionIndexANN
- **Small data**: DummySNN for exact results

## Use Cases

### Pattern Matching
Find where a pattern occurs in a long series:

```python
# Find heartbeat pattern in ECG data
searcher = MassSNN()
distances = searcher.fit_transform(ecg_data, heartbeat_pattern)
occurrences = np.where(distances < threshold)[0]
```

### Motif Discovery
Identify recurring patterns:

```python
# Find repeated behavioral patterns
motif_finder = StompMotif(window_size=100, k=5)
motifs = motif_finder.fit_predict(activity_data)
```

### Time Series Retrieval
Find similar time series in database:

```python
# Build searchable index
ann = RandomProjectionIndexANN()
ann.fit(time_series_database)

# Query for similar series
neighbors = ann.kneighbors(query_series, k=10)
```

## Best Practices

1. **Window size**: Critical parameter for subsequence methods
   - Too small: Captures noise
   - Too large: Misses fine-grained patterns
   - Rule of thumb: 10-20% of series length

2. **Normalization**: Most methods assume z-normalized subsequences
   - Handles amplitude variations
   - Focus on shape similarity

3. **Distance metrics**: Different metrics for different needs
   - Euclidean: Fast, shape-based
   - DTW: Handles temporal warping
   - Cosine: Scale-invariant

4. **Exclusion zone**: For motif discovery, exclude trivial matches
   - Typically set to 0.5-1.0 × window_size
   - Prevents finding overlapping occurrences

5. **Performance**:
   - MASS is O(n log n) vs O(n²) brute force
   - ANN trades accuracy for speed
   - GPU acceleration available for some methods

### `references/transformations.md`

# Transformations

Aeon provides extensive transformation capabilities for preprocessing, feature extraction, and representation learning from time series data.

## Transformation Types

Aeon distinguishes between:
- **CollectionTransformers**: Transform multiple time series (collections)
- **SeriesTransformers**: Transform individual time series

## Collection Transformers

### Convolution-Based Feature Extraction

Fast, scalable feature generation using random kernels:

- `RocketTransformer` - Random convolutional kernels
- `MiniRocketTransformer` - Simplified ROCKET for speed
- `MultiRocketTransformer` - Enhanced ROCKET variant
- `HydraTransformer` - Multi-resolution dilated convolutions
- `MultiRocketHydraTransformer` - Combines ROCKET and Hydra
- `ROCKETGPU` - GPU-accelerated variant

**Use when**: Need fast, scalable features for any ML algorithm, strong baseline performance.

### Statistical Feature Extraction

Domain-agnostic features based on time series characteristics:

- `Catch22` - 22 canonical time-series characteristics
- `TSFresh` - Comprehensive automated feature extraction (100+ features)
- `TSFreshRelevant` - Feature extraction with relevance filtering
- `SevenNumberSummary` - Descriptive statistics (mean, std, quantiles)

**Use when**: Need interpretable features, domain-agnostic approach, or feeding traditional ML.

### Dictionary-Based Representations

Symbolic approximations for discrete representations:

- `SAX` - Symbolic Aggregate approXimation
- `PAA` - Piecewise Aggregate Approximation
- `SFA` - Symbolic Fourier Approximation
- `SFAFast` - Optimized SFA
- `SFAWhole` - SFA on entire series (no windowing)
- `BORF` - Bag-of-Receptive-Fields

**Use when**: Need discrete/symbolic representation, dimensionality reduction, interpretability.

### Shapelet-Based Features

Discriminative subsequence extraction:

- `RandomShapeletTransform` - Random discriminative shapelets
- `RandomDilatedShapeletTransform` - Dilated shapelets for multi-scale
- `SAST` - Scalable And Accurate Subsequence Transform
- `RSAST` - Randomized SAST

**Use when**: Need interpretable discriminative patterns, phase-invariant features.

### Interval-Based Features

Statistical summaries from time intervals:

- `RandomIntervals` - Features from random intervals
- `SupervisedIntervals` - Supervised interval selection
- `QUANTTransformer` - Quantile-based interval features

**Use when**: Predictive patterns localized to specific windows.

### Preprocessing Transformations

Data preparation and normalization:

- `MinMaxScaler` - Scale to [0, 1] range
- `Normalizer` - Z-normalization (zero mean, unit variance)
- `Centerer` - Center to zero mean
- `SimpleImputer` - Fill missing values
- `DownsampleTransformer` - Reduce temporal resolution
- `Tabularizer` - Convert time series to tabular format

**Use when**: Need standardization, missing value handling, format conversion.

### Specialized Transformations

Advanced analysis methods:

- `MatrixProfile` - Computes distance profiles for pattern discovery
- `DWTTransformer` - Discrete Wavelet Transform
- `AutocorrelationFunctionTransformer` - ACF computation
- `Dobin` - Distance-based Outlier BasIs using Neighbors
- `SignatureTransformer` - Path signature methods
- `PLATransformer` - Piecewise Linear Approximation

### Class Imbalance Handling

- `ADASYN` - Adaptive Synthetic Sampling
- `SMOTE` - Synthetic Minority Over-sampling
- `OHIT` - Over-sampling with Highly Imbalanced Time series

**Use when**: Classification with imbalanced classes.

### Pipeline Composition

- `CollectionTransformerPipeline` - Chain multiple transformers

## Series Transformers

Transform individual time series (e.g., for preprocessing in forecasting).

### Statistical Analysis

- `AutoCorrelationSeriesTransformer` - Autocorrelation
- `StatsModelsACF` - ACF using statsmodels
- `StatsModelsPACF` - Partial autocorrelation

### Smoothing and Filtering

- `ExponentialSmoothing` - Exponentially weighted moving average
- `MovingAverage` - Simple or weighted moving average
- `SavitzkyGolayFilter` - Polynomial smoothing
- `GaussianFilter` - Gaussian kernel smoothing
- `BKFilter` - Baxter-King bandpass filter
- `DiscreteFourierApproximation` - Fourier-based filtering

**Use when**: Need noise reduction, trend extraction, or frequency filtering.

### Dimensionality Reduction

- `PCASeriesTransformer` - Principal component analysis
- `PlASeriesTransformer` - Piecewise Linear Approximation

### Transformations

- `BoxCoxTransformer` - Variance stabilization
- `LogTransformer` - Logarithmic scaling
- `ClaSPTransformer` - Classification Score Profile

### Pipeline Composition

- `SeriesTransformerPipeline` - Chain series transformers

## Quick Start: Feature Extraction

```python
from aeon.transformations.collection.convolution_based import RocketTransformer
from aeon.classification.sklearn import RotationForest
from aeon.datasets import load_classification

# Load data
X_train, y_train = load_classification("GunPoint", split="train")
X_test, y_test = load_classification("GunPoint", split="test")

# Extract ROCKET features
rocket = RocketTransformer()
X_train_features = rocket.fit_transform(X_train)
X_test_features = rocket.transform(X_test)

# Use with any sklearn classifier
clf = RotationForest()
clf.fit(X_train_features, y_train)
accuracy = clf.score(X_test_features, y_test)
```

## Quick Start: Preprocessing Pipeline

```python
from aeon.transformations.collection import (
    MinMaxScaler,
    SimpleImputer,
    CollectionTransformerPipeline
)

# Build preprocessing pipeline
pipeline = CollectionTransformerPipeline([
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', MinMaxScaler())
])

X_transformed = pipeline.fit_transform(X_train)
```

## Quick Start: Series Smoothing

```python
from aeon.transformations.series import MovingAverage

# Smooth individual time series
smoother = MovingAverage(window_size=5)
y_smoothed = smoother.fit_transform(y)
```

## Algorithm Selection

### For Feature Extraction:
- **Speed + Performance**: MiniRocketTransformer
- **Interpretability**: Catch22, TSFresh
- **Dimensionality reduction**: PAA, SAX, PCA
- **Discriminative patterns**: Shapelet transforms
- **Comprehensive features**: TSFresh (with longer runtime)

### For Preprocessing:
- **Normalization**: Normalizer, MinMaxScaler
- **Smoothing**: MovingAverage, SavitzkyGolayFilter
- **Missing values**: SimpleImputer
- **Frequency analysis**: DWTTransformer, Fourier methods

### For Symbolic Representation:
- **Fast approximation**: PAA
- **Alphabet-based**: SAX
- **Frequency-based**: SFA, SFAFast

## Best Practices

1. **Fit on training data only**: Avoid data leakage
   ```python
   transformer.fit(X_train)
   X_train_tf = transformer.transform(X_train)
   X_test_tf = transformer.transform(X_test)
   ```

2. **Pipeline composition**: Chain transformers for complex workflows
   ```python
   pipeline = CollectionTransformerPipeline([
       ('imputer', SimpleImputer()),
       ('scaler', Normalizer()),
       ('features', RocketTransformer())
   ])
   ```

3. **Feature selection**: TSFresh can generate many features; consider selection
   ```python
   from sklearn.feature_selection import SelectKBest
   selector = SelectKBest(k=100)
   X_selected = selector.fit_transform(X_features, y)
   ```

4. **Memory considerations**: Some transformers memory-intensive on large datasets
   - Use MiniRocket instead of ROCKET for speed
   - Consider downsampling for very long series
   - Use ROCKETGPU for GPU acceleration

5. **Domain knowledge**: Choose transformations matching domain:
   - Periodic data: Fourier-based methods
   - Noisy data: Smoothing filters
   - Spike detection: Wavelet transforms
