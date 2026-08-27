---
name: scikit-learn
description: Machine learning in Python with scikit-learn. Use when working with supervised learning (classification, regression), unsupervised learning (clustering, dimensionality reduction), model evaluation, hyperparameter tuning, preprocessing, or building ML pipelines. Provides comprehensive reference documentation for algorithms, preprocessing techniques, pipelines, and best practices.
---

# Scikit-learn

## Overview

This skill provides comprehensive guidance for machine learning tasks using scikit-learn, the industry-standard Python library for classical machine learning. Use this skill for classification, regression, clustering, dimensionality reduction, preprocessing, model evaluation, and building production-ready ML pipelines.

## Installation

Tested against **scikit-learn 1.8.0** (stable; December 2025). Requires **Python 3.11–3.14** (free-threaded CPython 3.14 wheels available in 1.8+).

Install the PyPI package **`scikit-learn`** (not the deprecated `sklearn` package on PyPI). Import in code as `sklearn`.

```bash
# Install scikit-learn using uv
uv pip install "scikit-learn>=1.7"

# Optional: plotting utilities and bundled script dependencies
uv pip install "scikit-learn[plots]" matplotlib seaborn

# Commonly used with
uv pip install pandas numpy
```

Check your version:

```python
import sklearn
print(sklearn.__version__)
```

## When to Use This Skill

Use the scikit-learn skill when:

- Building classification or regression models
- Performing clustering or dimensionality reduction
- Preprocessing and transforming data for machine learning
- Evaluating model performance with cross-validation
- Tuning hyperparameters with grid or random search
- Creating ML pipelines for production workflows
- Comparing different algorithms for a task
- Working with both structured (tabular) and text data
- Need interpretable, classical machine learning approaches

## Quick Start

### Classification Example

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Preprocess
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))
```

### Complete Pipeline with Mixed Data

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier

# Define feature types
numeric_features = ['age', 'income']
categorical_features = ['gender', 'occupation']

# Create preprocessing pipelines
numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine transformers
preprocessor = ColumnTransformer([
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])

# Full pipeline
model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', GradientBoostingClassifier(random_state=42))
])

# Fit and predict
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

## Core Capabilities

Five capability areas are documented in
[references/core_capabilities.md](references/core_capabilities.md), with per-topic detail
in [references/supervised_learning.md](references/supervised_learning.md),
[references/unsupervised_learning.md](references/unsupervised_learning.md),
[references/model_evaluation.md](references/model_evaluation.md),
[references/preprocessing.md](references/preprocessing.md), and
[references/pipelines_and_composition.md](references/pipelines_and_composition.md):

1. **Supervised learning** — classification and regression estimator families.
2. **Unsupervised learning** — clustering, decomposition, and manifold learning.
3. **Model evaluation and selection** — metrics, cross-validation, and hyperparameter search.
4. **Data preprocessing** — scaling, encoding, imputation, and feature selection.
5. **Pipelines and composition** — `Pipeline` and `ColumnTransformer`.

Always fit preprocessing inside a `Pipeline` so it is refit per cross-validation fold;
scaling or imputing before splitting leaks test information into training.

Two worked workflows are in
[references/common_workflows.md](references/common_workflows.md).

## Example Scripts

### Classification Pipeline

Run a complete classification workflow with preprocessing, model comparison, hyperparameter tuning, and evaluation:

```bash
uv run python scripts/classification_pipeline.py
```

This script demonstrates:
- Handling mixed data types (numeric and categorical)
- Model comparison using cross-validation
- Hyperparameter tuning with GridSearchCV
- Comprehensive evaluation with multiple metrics
- Feature importance analysis

### Clustering Analysis

Perform clustering analysis with algorithm comparison and visualization:

```bash
uv run python scripts/clustering_analysis.py
```

This script demonstrates:
- Finding optimal number of clusters (elbow method, silhouette analysis)
- Comparing multiple clustering algorithms (K-Means, DBSCAN, Agglomerative, Gaussian Mixture)
- Evaluating clustering quality without ground truth
- Visualizing results with PCA projection

## Reference Documentation

This skill includes comprehensive reference files for deep dives into specific topics:

### Quick Reference
**File:** `references/quick_reference.md`
- Common import patterns and installation instructions
- Quick workflow templates for common tasks
- Algorithm selection cheat sheets
- Common patterns and gotchas
- Performance optimization tips

### Supervised Learning
**File:** `references/supervised_learning.md`
- Linear models (regression and classification)
- Support Vector Machines
- Decision Trees and ensemble methods
- K-Nearest Neighbors, Naive Bayes, Neural Networks
- Algorithm selection guide

### Unsupervised Learning
**File:** `references/unsupervised_learning.md`
- All clustering algorithms with parameters and use cases
- Dimensionality reduction techniques
- Outlier and novelty detection
- Gaussian Mixture Models
- Method selection guide

### Model Evaluation
**File:** `references/model_evaluation.md`
- Cross-validation strategies
- Hyperparameter tuning methods
- Classification, regression, and clustering metrics
- Learning and validation curves
- Best practices for model selection

### Preprocessing
**File:** `references/preprocessing.md`
- Feature scaling and normalization
- Encoding categorical variables
- Missing value imputation
- Feature engineering techniques
- Custom transformers

### Pipelines and Composition
**File:** `references/pipelines_and_composition.md`
- Pipeline construction and usage
- ColumnTransformer for mixed data types
- FeatureUnion for parallel transformations
- Complete end-to-end examples
- Best practices

## Best Practices

### Always Use Pipelines
Pipelines prevent data leakage and ensure consistency:
```python
# Good: Preprocessing in pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])

# Bad: Preprocessing outside (can leak information)
X_scaled = StandardScaler().fit_transform(X)
```

### Fit on Training Data Only
Never fit on test data:
```python
# Good
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Only transform

# Bad
scaler = StandardScaler()
X_all_scaled = scaler.fit_transform(np.vstack([X_train, X_test]))
```

### Use Stratified Splitting for Classification
Preserve class distribution:
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

### Set Random State for Reproducibility
```python
model = RandomForestClassifier(n_estimators=100, random_state=42)
```

### Choose Appropriate Metrics
- Balanced data: Accuracy, F1-score
- Imbalanced data: Precision, Recall, ROC AUC, Balanced Accuracy
- Cost-sensitive: Define custom scorer

### Scale Features When Required
Algorithms requiring feature scaling:
- SVM, KNN, Neural Networks
- PCA, Linear/Logistic Regression with regularization
- K-Means clustering

Algorithms not requiring scaling:
- Tree-based models (Decision Trees, Random Forest, Gradient Boosting)
- Naive Bayes

## Troubleshooting Common Issues

### ConvergenceWarning
**Issue:** Model didn't converge
**Solution:** Increase `max_iter` or scale features
```python
model = LogisticRegression(max_iter=1000)
```

### Poor Performance on Test Set
**Issue:** Overfitting
**Solution:** Use regularization, cross-validation, or simpler model
```python
# Add regularization
model = Ridge(alpha=1.0)

# Use cross-validation
scores = cross_val_score(model, X, y, cv=5)
```

### Memory Error with Large Datasets
**Solution:** Use algorithms designed for large data
```python
# Use SGD for large datasets
from sklearn.linear_model import SGDClassifier
model = SGDClassifier()

# Or MiniBatchKMeans for clustering
from sklearn.cluster import MiniBatchKMeans
model = MiniBatchKMeans(n_clusters=8, batch_size=100)
```

## Additional Resources

- Official Documentation: https://scikit-learn.org/stable/
- User Guide: https://scikit-learn.org/stable/user_guide.html
- API Reference: https://scikit-learn.org/stable/api/index.html
- Examples Gallery: https://scikit-learn.org/stable/auto_examples/index.html

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/scikit-learn/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/common_workflows.md`

# Common Workflows

Two worked end-to-end workflows: building a classification model and performing a
clustering analysis.

## Common Workflows

### Building a Classification Model

1. **Load and explore data**
   ```python
   import pandas as pd
   df = pd.read_csv('data.csv')
   X = df.drop('target', axis=1)
   y = df['target']
   ```

2. **Split data with stratification**
   ```python
   from sklearn.model_selection import train_test_split
   X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=0.2, stratify=y, random_state=42
   )
   ```

3. **Create preprocessing pipeline**
   ```python
   from sklearn.pipeline import Pipeline
   from sklearn.preprocessing import StandardScaler
   from sklearn.compose import ColumnTransformer

   # Handle numeric and categorical features separately
   preprocessor = ColumnTransformer([
       ('num', StandardScaler(), numeric_features),
       ('cat', OneHotEncoder(), categorical_features)
   ])
   ```

4. **Build complete pipeline**
   ```python
   model = Pipeline([
       ('preprocessor', preprocessor),
       ('classifier', RandomForestClassifier(random_state=42))
   ])
   ```

5. **Tune hyperparameters**
   ```python
   from sklearn.model_selection import GridSearchCV

   param_grid = {
       'classifier__n_estimators': [100, 200],
       'classifier__max_depth': [10, 20, None]
   }

   grid_search = GridSearchCV(model, param_grid, cv=5)
   grid_search.fit(X_train, y_train)
   ```

6. **Evaluate on test set**
   ```python
   from sklearn.metrics import classification_report

   best_model = grid_search.best_estimator_
   y_pred = best_model.predict(X_test)
   print(classification_report(y_test, y_pred))
   ```

### Performing Clustering Analysis

1. **Preprocess data**
   ```python
   from sklearn.preprocessing import StandardScaler

   scaler = StandardScaler()
   X_scaled = scaler.fit_transform(X)
   ```

2. **Find optimal number of clusters**
   ```python
   from sklearn.cluster import KMeans
   from sklearn.metrics import silhouette_score

   scores = []
   for k in range(2, 11):
       kmeans = KMeans(n_clusters=k, random_state=42)
       labels = kmeans.fit_predict(X_scaled)
       scores.append(silhouette_score(X_scaled, labels))

   optimal_k = range(2, 11)[np.argmax(scores)]
   ```

3. **Apply clustering**
   ```python
   model = KMeans(n_clusters=optimal_k, random_state=42)
   labels = model.fit_predict(X_scaled)
   ```

4. **Visualize with dimensionality reduction**
   ```python
   from sklearn.decomposition import PCA

   pca = PCA(n_components=2)
   X_2d = pca.fit_transform(X_scaled)

   plt.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='viridis')
   ```

### `references/core_capabilities.md`

# Core Capabilities

Supervised learning, unsupervised learning, model evaluation and selection, data
preprocessing, and pipelines and composition. Per-topic detail is in the other reference
files in this directory.

## Core Capabilities

### 1. Supervised Learning

Comprehensive algorithms for classification and regression tasks.

**Key algorithms:**
- **Linear models**: Logistic Regression, Linear Regression, Ridge, Lasso, ElasticNet
- **Tree-based**: Decision Trees, Random Forest, Gradient Boosting
- **Support Vector Machines**: SVC, SVR with various kernels
- **Ensemble methods**: AdaBoost, Voting, Stacking
- **Neural Networks**: MLPClassifier, MLPRegressor
- **Others**: Naive Bayes, K-Nearest Neighbors

**When to use:**
- Classification: Predicting discrete categories (spam detection, image classification, fraud detection)
- Regression: Predicting continuous values (price prediction, demand forecasting)

**See:** `references/supervised_learning.md` for detailed algorithm documentation, parameters, and usage examples.

### 2. Unsupervised Learning

Discover patterns in unlabeled data through clustering and dimensionality reduction.

**Clustering algorithms:**
- **Partition-based**: K-Means, MiniBatchKMeans
- **Density-based**: DBSCAN, HDBSCAN, OPTICS
- **Hierarchical**: AgglomerativeClustering
- **Probabilistic**: Gaussian Mixture Models
- **Others**: MeanShift, SpectralClustering, BIRCH

**Dimensionality reduction:**
- **Linear**: PCA, TruncatedSVD, NMF
- **Manifold learning**: t-SNE, Isomap, LLE, MDS, ClassicalMDS (1.8+)
- **External (install separately)**: UMAP (`umap-learn`)
- **Feature extraction**: FastICA, LatentDirichletAllocation

**When to use:**
- Customer segmentation, anomaly detection, data visualization
- Reducing feature dimensions, exploratory data analysis
- Topic modeling, image compression

**See:** `references/unsupervised_learning.md` for detailed documentation.

### 3. Model Evaluation and Selection

Tools for robust model evaluation, cross-validation, and hyperparameter tuning.

**Cross-validation strategies:**
- KFold, StratifiedKFold (classification)
- TimeSeriesSplit (temporal data)
- GroupKFold (grouped samples)

**Hyperparameter tuning:**
- GridSearchCV (exhaustive search)
- RandomizedSearchCV (random sampling)
- HalvingGridSearchCV (successive halving)

**Metrics:**
- **Classification**: accuracy, precision, recall, F1-score, ROC AUC, confusion matrix
- **Regression**: MSE, RMSE, MAE, R², MAPE
- **Clustering**: silhouette score, Calinski-Harabasz, Davies-Bouldin

**When to use:**
- Comparing model performance objectively
- Finding optimal hyperparameters
- Preventing overfitting through cross-validation
- Understanding model behavior with learning curves

**See:** `references/model_evaluation.md` for comprehensive metrics and tuning strategies.

### 4. Data Preprocessing

Transform raw data into formats suitable for machine learning.

**Scaling and normalization:**
- StandardScaler (zero mean, unit variance)
- MinMaxScaler (bounded range)
- RobustScaler (robust to outliers)
- Normalizer (sample-wise normalization)

**Encoding categorical variables:**
- OneHotEncoder (nominal categories)
- OrdinalEncoder (ordered categories)
- LabelEncoder (target encoding)

**Handling missing values:**
- SimpleImputer (mean, median, most frequent)
- KNNImputer (k-nearest neighbors)
- IterativeImputer (multivariate imputation)

**Feature engineering:**
- PolynomialFeatures (interaction terms)
- KBinsDiscretizer (binning)
- Feature selection (RFE, SelectKBest, SelectFromModel)

**When to use:**
- Before training any algorithm that requires scaled features (SVM, KNN, Neural Networks)
- Converting categorical variables to numeric format
- Handling missing data systematically
- Creating non-linear features for linear models

**See:** `references/preprocessing.md` for detailed preprocessing techniques.

### 5. Pipelines and Composition

Build reproducible, production-ready ML workflows.

**Key components:**
- **Pipeline**: Chain transformers and estimators sequentially
- **ColumnTransformer**: Apply different preprocessing to different columns
- **FeatureUnion**: Combine multiple transformers in parallel
- **TransformedTargetRegressor**: Transform target variable

**Benefits:**
- Prevents data leakage in cross-validation
- Simplifies code and improves maintainability
- Enables joint hyperparameter tuning
- Ensures consistency between training and prediction

**When to use:**
- Always use Pipelines for production workflows
- When mixing numerical and categorical features (use ColumnTransformer)
- When performing cross-validation with preprocessing steps
- When hyperparameter tuning includes preprocessing parameters

**See:** `references/pipelines_and_composition.md` for comprehensive pipeline patterns.

### `references/model_evaluation.md`

# Model Selection and Evaluation Reference

## Overview

Comprehensive guide for evaluating models, tuning hyperparameters, and selecting the best model using scikit-learn's model selection tools.

## Train-Test Split

### Basic Splitting

```python
from sklearn.model_selection import train_test_split

# Basic split (default 75/25)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# With stratification (preserves class distribution)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

# Three-way split (train/val/test)
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
```

## Cross-Validation

### Cross-Validation Strategies

**KFold**
- Standard k-fold cross-validation
- Splits data into k consecutive folds
```python
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, val_idx in kf.split(X):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
```

**StratifiedKFold**
- Preserves class distribution in each fold
- Use for imbalanced classification
```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, val_idx in skf.split(X, y):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
```

**TimeSeriesSplit**
- For time series data
- Respects temporal order
```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_idx, val_idx in tscv.split(X):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
```

**GroupKFold**
- Ensures samples from same group don't appear in both train and validation
- Use when samples are not independent
```python
from sklearn.model_selection import GroupKFold

gkf = GroupKFold(n_splits=5)
for train_idx, val_idx in gkf.split(X, y, groups=group_ids):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
```

**LeaveOneOut (LOO)**
- Each sample used as validation set once
- Use for very small datasets
- Computationally expensive
```python
from sklearn.model_selection import LeaveOneOut

loo = LeaveOneOut()
for train_idx, val_idx in loo.split(X):
    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y[train_idx], y[val_idx]
```

### Cross-Validation Functions

**cross_val_score**
- Evaluate model using cross-validation
- Returns array of scores
```python
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')

print(f"Scores: {scores}")
print(f"Mean: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

**cross_validate**
- More comprehensive than cross_val_score
- Can return multiple metrics and fit times
```python
from sklearn.model_selection import cross_validate

model = RandomForestClassifier(n_estimators=100, random_state=42)
cv_results = cross_validate(
    model, X, y, cv=5,
    scoring=['accuracy', 'precision', 'recall', 'f1'],
    return_train_score=True,
    return_estimator=True  # Returns fitted estimators
)

print(f"Test accuracy: {cv_results['test_accuracy'].mean():.3f}")
print(f"Test precision: {cv_results['test_precision'].mean():.3f}")
print(f"Fit time: {cv_results['fit_time'].mean():.3f}s")
```

**cross_val_predict**
- Get predictions for each sample when it was in validation set
- Useful for analyzing errors
```python
from sklearn.model_selection import cross_val_predict

model = RandomForestClassifier(n_estimators=100, random_state=42)
y_pred = cross_val_predict(model, X, y, cv=5)

# Now can analyze predictions vs actual
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y, y_pred)
```

## Hyperparameter Tuning

### Grid Search

**GridSearchCV**
- Exhaustive search over parameter grid
- Tests all combinations
```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [5, 10, 15, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

model = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(
    model, param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,  # Use all CPU cores
    verbose=1
)

grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best cross-validation score: {grid_search.best_score_:.3f}")
print(f"Test score: {grid_search.score(X_test, y_test):.3f}")

# Access best model
best_model = grid_search.best_estimator_

# View all results
import pandas as pd
results_df = pd.DataFrame(grid_search.cv_results_)
```

### Randomized Search

**RandomizedSearchCV**
- Samples random combinations from parameter distributions
- More efficient for large search spaces
```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint, uniform

param_distributions = {
    'n_estimators': randint(50, 300),
    'max_depth': [5, 10, 15, 20, None],
    'min_samples_split': randint(2, 20),
    'min_samples_leaf': randint(1, 10),
    'max_features': uniform(0.1, 0.9)  # Continuous distribution
}

model = RandomForestClassifier(random_state=42)
random_search = RandomizedSearchCV(
    model, param_distributions,
    n_iter=100,  # Number of parameter settings sampled
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1,
    random_state=42
)

random_search.fit(X_train, y_train)

print(f"Best parameters: {random_search.best_params_}")
print(f"Best score: {random_search.best_score_:.3f}")
```

### Successive Halving

**HalvingGridSearchCV / HalvingRandomSearchCV**
- Iteratively selects best candidates using successive halving
- More efficient than exhaustive search
```python
from sklearn.experimental import enable_halving_search_cv
from sklearn.model_selection import HalvingGridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200, 300],
    'max_depth': [5, 10, 15, 20, None],
    'min_samples_split': [2, 5, 10, 20]
}

model = RandomForestClassifier(random_state=42)
halving_search = HalvingGridSearchCV(
    model, param_grid,
    cv=5,
    factor=3,  # Proportion of candidates eliminated in each iteration
    resource='n_samples',  # Can also use 'n_estimators' for ensembles
    max_resources='auto',
    random_state=42
)

halving_search.fit(X_train, y_train)
print(f"Best parameters: {halving_search.best_params_}")
```

## Classification Metrics

### Basic Metrics

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    balanced_accuracy_score, matthews_corrcoef
)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')  # For multiclass
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')
balanced_acc = balanced_accuracy_score(y_test, y_pred)  # Good for imbalanced data
mcc = matthews_corrcoef(y_test, y_pred)  # Matthews correlation coefficient

print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1-score: {f1:.3f}")
print(f"Balanced Accuracy: {balanced_acc:.3f}")
print(f"MCC: {mcc:.3f}")
```

### Classification Report

```python
from sklearn.metrics import classification_report

print(classification_report(y_test, y_pred, target_names=class_names))
```

### Confusion Matrix

```python
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(cmap='Blues')
plt.show()
```

### ROC and AUC

```python
from sklearn.metrics import roc_auc_score, roc_curve, RocCurveDisplay

# Binary classification
y_proba = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_proba)
print(f"ROC AUC: {auc:.3f}")

# Plot ROC curve
fpr, tpr, thresholds = roc_curve(y_test, y_proba)
RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=auc).plot()

# Multiclass (one-vs-rest)
auc_ovr = roc_auc_score(y_test, y_proba_multi, multi_class='ovr')
```

### Precision-Recall Curve

```python
from sklearn.metrics import precision_recall_curve, PrecisionRecallDisplay
from sklearn.metrics import average_precision_score

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
ap = average_precision_score(y_test, y_proba)

disp = PrecisionRecallDisplay(precision=precision, recall=recall, average_precision=ap)
disp.plot()
```

### Log Loss

```python
from sklearn.metrics import log_loss

y_proba = model.predict_proba(X_test)
logloss = log_loss(y_test, y_proba)
print(f"Log Loss: {logloss:.3f}")
```

## Regression Metrics

```python
from sklearn.metrics import (
    mean_squared_error, root_mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error, median_absolute_error
)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = root_mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mape = mean_absolute_percentage_error(y_test, y_pred)
median_ae = median_absolute_error(y_test, y_pred)

print(f"MSE: {mse:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"MAE: {mae:.3f}")
print(f"R² Score: {r2:.3f}")
print(f"MAPE: {mape:.3f}")
print(f"Median AE: {median_ae:.3f}")
```

## Clustering Metrics

### With Ground Truth Labels

```python
from sklearn.metrics import (
    adjusted_rand_score, normalized_mutual_info_score,
    adjusted_mutual_info_score, fowlkes_mallows_score,
    homogeneity_score, completeness_score, v_measure_score
)

ari = adjusted_rand_score(y_true, y_pred)
nmi = normalized_mutual_info_score(y_true, y_pred)
ami = adjusted_mutual_info_score(y_true, y_pred)
fmi = fowlkes_mallows_score(y_true, y_pred)
homogeneity = homogeneity_score(y_true, y_pred)
completeness = completeness_score(y_true, y_pred)
v_measure = v_measure_score(y_true, y_pred)
```

### Without Ground Truth

```python
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, davies_bouldin_score
)

silhouette = silhouette_score(X, labels)  # [-1, 1], higher better
ch_score = calinski_harabasz_score(X, labels)  # Higher better
db_score = davies_bouldin_score(X, labels)  # Lower better
```

## Custom Scoring

### Using make_scorer

```python
from sklearn.metrics import make_scorer

def custom_metric(y_true, y_pred):
    # Your custom logic
    return score

custom_scorer = make_scorer(custom_metric, greater_is_better=True)

# Use in cross-validation or grid search
scores = cross_val_score(model, X, y, cv=5, scoring=custom_scorer)
```

### Multiple Metrics in Grid Search

```python
from sklearn.model_selection import GridSearchCV

scoring = {
    'accuracy': 'accuracy',
    'precision': 'precision_weighted',
    'recall': 'recall_weighted',
    'f1': 'f1_weighted'
}

grid_search = GridSearchCV(
    model, param_grid,
    cv=5,
    scoring=scoring,
    refit='f1',  # Refit on best f1 score
    return_train_score=True
)

grid_search.fit(X_train, y_train)
```

## Validation Curves

### Learning Curve

```python
from sklearn.model_selection import learning_curve
import matplotlib.pyplot as plt
import numpy as np

train_sizes, train_scores, val_scores = learning_curve(
    model, X, y,
    cv=5,
    train_sizes=np.linspace(0.1, 1.0, 10),
    scoring='accuracy',
    n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
train_std = train_scores.std(axis=1)
val_mean = val_scores.mean(axis=1)
val_std = val_scores.std(axis=1)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, train_mean, label='Training score')
plt.plot(train_sizes, val_mean, label='Validation score')
plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1)
plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1)
plt.xlabel('Training Set Size')
plt.ylabel('Score')
plt.title('Learning Curve')
plt.legend()
plt.grid(True)
```

### Validation Curve

```python
from sklearn.model_selection import validation_curve

param_range = [1, 10, 50, 100, 200, 500]
train_scores, val_scores = validation_curve(
    model, X, y,
    param_name='n_estimators',
    param_range=param_range,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

train_mean = train_scores.mean(axis=1)
val_mean = val_scores.mean(axis=1)

plt.figure(figsize=(10, 6))
plt.plot(param_range, train_mean, label='Training score')
plt.plot(param_range, val_mean, label='Validation score')
plt.xlabel('n_estimators')
plt.ylabel('Score')
plt.title('Validation Curve')
plt.legend()
plt.grid(True)
```

## Model Persistence

### Save and Load Models

```python
import joblib

# Save model
joblib.dump(model, 'model.pkl')

# Load model
loaded_model = joblib.load('model.pkl')

# Also works with pipelines
joblib.dump(pipeline, 'pipeline.pkl')
```

### Using pickle

```python
import pickle

# Save
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Load
with open('model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)
```

## Imbalanced Data Strategies

### Class Weighting

```python
from sklearn.ensemble import RandomForestClassifier

# Automatically balance classes
model = RandomForestClassifier(class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

# Custom weights
class_weights = {0: 1, 1: 10}  # Give class 1 more weight
model = RandomForestClassifier(class_weight=class_weights, random_state=42)
```

### Resampling (using imbalanced-learn)

```python
# Install: uv pip install imbalanced-learn
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline

# SMOTE oversampling
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# Combined approach
pipeline = ImbPipeline([
    ('over', SMOTE(sampling_strategy=0.5)),
    ('under', RandomUnderSampler(sampling_strategy=0.8)),
    ('model', RandomForestClassifier())
])
```

## Best Practices

### Stratified Splitting
Always use stratified splitting for classification:
```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

### Appropriate Metrics
- **Balanced data**: Accuracy, F1-score
- **Imbalanced data**: Precision, Recall, F1-score, ROC AUC, Balanced Accuracy
- **Cost-sensitive**: Define custom scorer with costs
- **Ranking**: ROC AUC, Average Precision

### Cross-Validation
- Use 5 or 10-fold CV for most cases
- Use StratifiedKFold for classification
- Use TimeSeriesSplit for time series
- Use GroupKFold when samples are grouped

### Nested Cross-Validation
For unbiased performance estimates when tuning:
```python
from sklearn.model_selection import cross_val_score, GridSearchCV

# Inner loop: hyperparameter tuning
grid_search = GridSearchCV(model, param_grid, cv=5)

# Outer loop: performance estimation
scores = cross_val_score(grid_search, X, y, cv=5)
print(f"Nested CV score: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

### `references/pipelines_and_composition.md`

# Pipelines and Composite Estimators Reference

## Overview

Pipelines chain multiple processing steps into a single estimator, preventing data leakage and simplifying code. They enable reproducible workflows and seamless integration with cross-validation and hyperparameter tuning.

## Pipeline Basics

### Creating a Pipeline

**Pipeline (`sklearn.pipeline.Pipeline`)**
- Chains transformers with a final estimator
- All intermediate steps must have fit_transform()
- Final step can be any estimator (transformer, classifier, regressor, clusterer)
- Example:
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=10)),
    ('classifier', LogisticRegression())
])

# Fit the entire pipeline
pipeline.fit(X_train, y_train)

# Predict using the pipeline
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)
```

### Using make_pipeline

**make_pipeline**
- Convenient constructor that auto-generates step names
- Example:
```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

pipeline = make_pipeline(
    StandardScaler(),
    PCA(n_components=10),
    SVC(kernel='rbf')
)

pipeline.fit(X_train, y_train)
```

## Accessing Pipeline Components

### Accessing Steps

```python
# By index
scaler = pipeline.steps[0][1]

# By name
scaler = pipeline.named_steps['scaler']
pca = pipeline.named_steps['pca']

# Using indexing syntax
scaler = pipeline['scaler']
pca = pipeline['pca']

# Get all step names
print(pipeline.named_steps.keys())
```

### Setting Parameters

```python
# Set parameters using double underscore notation
pipeline.set_params(
    pca__n_components=15,
    classifier__C=0.1
)

# Or during creation
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=10)),
    ('classifier', LogisticRegression(C=1.0))
])
```

### Accessing Attributes

```python
# Access fitted attributes
pca_components = pipeline.named_steps['pca'].components_
explained_variance = pipeline.named_steps['pca'].explained_variance_ratio_

# Access intermediate transformations
X_scaled = pipeline.named_steps['scaler'].transform(X_test)
X_pca = pipeline.named_steps['pca'].transform(X_scaled)
```

## Hyperparameter Tuning with Pipelines

### Grid Search with Pipeline

```python
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', SVC())
])

param_grid = {
    'classifier__C': [0.1, 1, 10, 100],
    'classifier__gamma': ['scale', 'auto', 0.001, 0.01],
    'classifier__kernel': ['rbf', 'linear']
}

grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1)
grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.3f}")
```

### Tuning Multiple Pipeline Steps

```python
param_grid = {
    # PCA parameters
    'pca__n_components': [5, 10, 20, 50],

    # Classifier parameters
    'classifier__C': [0.1, 1, 10],
    'classifier__kernel': ['rbf', 'linear']
}

grid_search = GridSearchCV(pipeline, param_grid, cv=5)
grid_search.fit(X_train, y_train)
```

## ColumnTransformer

### Basic Usage

**ColumnTransformer (`sklearn.compose.ColumnTransformer`)**
- Apply different preprocessing to different columns
- Prevents data leakage in cross-validation
- Example:
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Define column groups
numeric_features = ['age', 'income', 'hours_per_week']
categorical_features = ['gender', 'occupation', 'native_country']

# Create preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'  # Keep other columns unchanged
)

X_transformed = preprocessor.fit_transform(X)
```

### With Pipeline Steps

```python
from sklearn.pipeline import Pipeline

numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Full pipeline with model
full_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression())
])

full_pipeline.fit(X_train, y_train)
```

### Using make_column_transformer

```python
from sklearn.compose import make_column_transformer

preprocessor = make_column_transformer(
    (StandardScaler(), numeric_features),
    (OneHotEncoder(), categorical_features),
    remainder='passthrough'
)
```

### Column Selection

```python
# By column names (if X is DataFrame)
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), ['age', 'income']),
    ('cat', OneHotEncoder(), ['gender', 'occupation'])
])

# By column indices
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), [0, 1, 2]),
    ('cat', OneHotEncoder(), [3, 4])
])

# By boolean mask
numeric_mask = [True, True, True, False, False]
categorical_mask = [False, False, False, True, True]

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_mask),
    ('cat', OneHotEncoder(), categorical_mask)
])

# By callable
def is_numeric(X):
    return X.select_dtypes(include=['number']).columns.tolist()

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), is_numeric)
])
```

### Getting Feature Names

```python
# Get output feature names
feature_names = preprocessor.get_feature_names_out()

# After fitting
preprocessor.fit(X_train)
output_features = preprocessor.get_feature_names_out()
print(f"Input features: {X_train.columns.tolist()}")
print(f"Output features: {output_features}")
```

### Remainder Handling

```python
# Drop unspecified columns (default)
preprocessor = ColumnTransformer([...], remainder='drop')

# Pass through unchanged
preprocessor = ColumnTransformer([...], remainder='passthrough')

# Apply transformer to remaining columns
preprocessor = ColumnTransformer([...], remainder=StandardScaler())
```

## FeatureUnion

### Basic Usage

**FeatureUnion (`sklearn.pipeline.FeatureUnion`)**
- Concatenates results of multiple transformers
- Transformers are applied in parallel
- Example:
```python
from sklearn.pipeline import FeatureUnion
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest

# Combine PCA and feature selection
feature_union = FeatureUnion([
    ('pca', PCA(n_components=10)),
    ('select_best', SelectKBest(k=20))
])

X_combined = feature_union.fit_transform(X_train, y_train)
print(f"Combined features: {X_combined.shape[1]}")  # 10 + 20 = 30
```

### With Pipeline

```python
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA, TruncatedSVD

# Create feature union
feature_union = FeatureUnion([
    ('pca', PCA(n_components=10)),
    ('svd', TruncatedSVD(n_components=10))
])

# Full pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('features', feature_union),
    ('classifier', LogisticRegression())
])

pipeline.fit(X_train, y_train)
```

### Weighted Feature Union

```python
# Apply weights to transformers
feature_union = FeatureUnion(
    transformer_list=[
        ('pca', PCA(n_components=10)),
        ('select_best', SelectKBest(k=20))
    ],
    transformer_weights={
        'pca': 2.0,  # Give PCA features double weight
        'select_best': 1.0
    }
)
```

## Advanced Pipeline Patterns

### Caching Pipeline Steps

```python
from sklearn.pipeline import Pipeline
from tempfile import mkdtemp
from shutil import rmtree

# Cache intermediate results
cachedir = mkdtemp()
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=50)),
    ('classifier', LogisticRegression())
], memory=cachedir)

pipeline.fit(X_train, y_train)

# Clean up cache
rmtree(cachedir)
```

### Nested Pipelines

```python
from sklearn.pipeline import Pipeline

# Inner pipeline for text processing
text_pipeline = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer())
])

# Outer pipeline combining text and numeric features
full_pipeline = Pipeline([
    ('features', FeatureUnion([
        ('text', text_pipeline),
        ('numeric', StandardScaler())
    ])),
    ('classifier', LogisticRegression())
])
```

### Custom Transformers in Pipelines

```python
from sklearn.base import BaseEstimator, TransformerMixin

class TextLengthExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [[len(text)] for text in X]

pipeline = Pipeline([
    ('length', TextLengthExtractor()),
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression())
])
```

### Slicing Pipelines

```python
# Get sub-pipeline
sub_pipeline = pipeline[:2]  # First two steps

# Get specific range
middle_steps = pipeline[1:3]
```

## TransformedTargetRegressor

### Basic Usage

**TransformedTargetRegressor**
- Transforms target variable before fitting
- Automatically inverse-transforms predictions
- Example:
```python
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import QuantileTransformer
from sklearn.linear_model import LinearRegression

model = TransformedTargetRegressor(
    regressor=LinearRegression(),
    transformer=QuantileTransformer(output_distribution='normal')
)

model.fit(X_train, y_train)
y_pred = model.predict(X_test)  # Automatically inverse-transformed
```

### With Functions

```python
import numpy as np

model = TransformedTargetRegressor(
    regressor=LinearRegression(),
    func=np.log1p,
    inverse_func=np.expm1
)

model.fit(X_train, y_train)
```

## Complete Example: End-to-End Pipeline

```python
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# Define feature types
numeric_features = ['age', 'income', 'hours_per_week']
categorical_features = ['gender', 'occupation', 'education']

# Numeric preprocessing pipeline
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

# Categorical preprocessing pipeline
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

# Combine preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ]
)

# Full pipeline
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('pca', PCA(n_components=0.95)),  # Keep 95% variance
    ('classifier', RandomForestClassifier(random_state=42))
])

# Hyperparameter tuning
param_grid = {
    'preprocessor__num__imputer__strategy': ['mean', 'median'],
    'pca__n_components': [0.90, 0.95, 0.99],
    'classifier__n_estimators': [100, 200],
    'classifier__max_depth': [10, 20, None]
}

grid_search = GridSearchCV(
    pipeline, param_grid,
    cv=5, scoring='accuracy',
    n_jobs=-1, verbose=1
)

grid_search.fit(X_train, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV score: {grid_search.best_score_:.3f}")
print(f"Test score: {grid_search.score(X_test, y_test):.3f}")

# Make predictions
best_pipeline = grid_search.best_estimator_
y_pred = best_pipeline.predict(X_test)
y_proba = best_pipeline.predict_proba(X_test)
```

## Visualization

### Displaying Pipelines

```python
# In Jupyter notebooks, pipelines display as diagrams
from sklearn import set_config
set_config(display='diagram')

pipeline  # Displays visual diagram
```

### Text Representation

```python
# Print pipeline structure
print(pipeline)

# Get detailed parameters
print(pipeline.get_params())
```

## Best Practices

### Always Use Pipelines
- Prevents data leakage
- Ensures consistency between training and prediction
- Makes code more maintainable
- Enables easy hyperparameter tuning

### Proper Pipeline Construction
```python
# Good: Preprocessing inside pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])
pipeline.fit(X_train, y_train)

# Bad: Preprocessing outside pipeline (can cause leakage)
X_train_scaled = StandardScaler().fit_transform(X_train)
model = LogisticRegression()
model.fit(X_train_scaled, y_train)
```

### Use ColumnTransformer for Mixed Data
Always use ColumnTransformer when you have both numerical and categorical features:
```python
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(), categorical_features)
])
```

### Name Your Steps Meaningfully
```python
# Good
pipeline = Pipeline([
    ('imputer', SimpleImputer()),
    ('scaler', StandardScaler()),
    ('pca', PCA(n_components=10)),
    ('rf_classifier', RandomForestClassifier())
])

# Bad
pipeline = Pipeline([
    ('step1', SimpleImputer()),
    ('step2', StandardScaler()),
    ('step3', PCA(n_components=10)),
    ('step4', RandomForestClassifier())
])
```

### Cache Expensive Transformations
For repeated fitting (e.g., during grid search), cache expensive steps:
```python
from tempfile import mkdtemp

cachedir = mkdtemp()
pipeline = Pipeline([
    ('expensive_preprocessing', ExpensiveTransformer()),
    ('classifier', LogisticRegression())
], memory=cachedir)
```

### Test Pipeline Compatibility
Ensure all steps are compatible:
- All intermediate steps must have fit() and transform()
- Final step needs fit() and predict() (or transform())
- Use set_output(transform='pandas') for DataFrame output
```python
pipeline.set_output(transform='pandas')
X_transformed = pipeline.transform(X)  # Returns DataFrame
```

### `references/preprocessing.md`

# Data Preprocessing and Feature Engineering Reference

## Overview

Data preprocessing transforms raw data into a format suitable for machine learning models. This includes scaling, encoding, handling missing values, and feature engineering.

## Feature Scaling and Normalization

### StandardScaler

**StandardScaler (`sklearn.preprocessing.StandardScaler`)**
- Standardizes features to zero mean and unit variance
- Formula: z = (x - mean) / std
- Use when: Features have different scales, algorithm assumes normally distributed data
- Required for: SVM, KNN, Neural Networks, PCA, Linear Regression with regularization
- Example:
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # Use same parameters as training

# Access learned parameters
print(f"Mean: {scaler.mean_}")
print(f"Std: {scaler.scale_}")
```

### MinMaxScaler

**MinMaxScaler (`sklearn.preprocessing.MinMaxScaler`)**
- Scales features to a given range (default [0, 1])
- Formula: X_scaled = (X - X.min) / (X.max - X.min)
- Use when: Need bounded values, data not normally distributed
- Sensitive to outliers
- Example:
```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0, 1))
X_scaled = scaler.fit_transform(X_train)

# Custom range
scaler = MinMaxScaler(feature_range=(-1, 1))
X_scaled = scaler.fit_transform(X_train)
```

### RobustScaler

**RobustScaler (`sklearn.preprocessing.RobustScaler`)**
- Scales using median and interquartile range (IQR)
- Formula: X_scaled = (X - median) / IQR
- Use when: Data contains outliers
- Robust to outliers
- Example:
```python
from sklearn.preprocessing import RobustScaler

scaler = RobustScaler()
X_scaled = scaler.fit_transform(X_train)
```

### Normalizer

**Normalizer (`sklearn.preprocessing.Normalizer`)**
- Normalizes samples individually to unit norm
- Common norms: 'l1', 'l2', 'max'
- Use when: Need to normalize each sample independently (e.g., text features)
- Example:
```python
from sklearn.preprocessing import Normalizer

normalizer = Normalizer(norm='l2')  # Euclidean norm
X_normalized = normalizer.fit_transform(X)
```

### MaxAbsScaler

**MaxAbsScaler (`sklearn.preprocessing.MaxAbsScaler`)**
- Scales by maximum absolute value
- Range: [-1, 1]
- Doesn't shift/center data (preserves sparsity)
- Use when: Data is already centered or sparse
- Example:
```python
from sklearn.preprocessing import MaxAbsScaler

scaler = MaxAbsScaler()
X_scaled = scaler.fit_transform(X_sparse)
```

## Encoding Categorical Variables

### OneHotEncoder

**OneHotEncoder (`sklearn.preprocessing.OneHotEncoder`)**
- Creates binary columns for each category
- Use when: Nominal categories (no order), tree-based models or linear models
- Example:
```python
from sklearn.preprocessing import OneHotEncoder

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = encoder.fit_transform(X_categorical)

# Get feature names
feature_names = encoder.get_feature_names_out(['color', 'size'])

# Handle unknown categories during transform
X_test_encoded = encoder.transform(X_test_categorical)
```

### OrdinalEncoder

**OrdinalEncoder (`sklearn.preprocessing.OrdinalEncoder`)**
- Encodes categories as integers
- Use when: Ordinal categories (ordered), or tree-based models
- Example:
```python
from sklearn.preprocessing import OrdinalEncoder

# Natural ordering
encoder = OrdinalEncoder()
X_encoded = encoder.fit_transform(X_categorical)

# Custom ordering
encoder = OrdinalEncoder(categories=[['small', 'medium', 'large']])
X_encoded = encoder.fit_transform(X_categorical)
```

### LabelEncoder

**LabelEncoder (`sklearn.preprocessing.LabelEncoder`)**
- Encodes target labels (y) as integers
- Use for: Target variable encoding
- Example:
```python
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Decode back
y_decoded = le.inverse_transform(y_encoded)
print(f"Classes: {le.classes_}")
```

### Target Encoding (using category_encoders)

```python
# Install: uv pip install category-encoders
from category_encoders import TargetEncoder

encoder = TargetEncoder()
X_train_encoded = encoder.fit_transform(X_train_categorical, y_train)
X_test_encoded = encoder.transform(X_test_categorical)
```

## Non-linear Transformations

### Power Transforms

**PowerTransformer**
- Makes data more Gaussian-like
- Methods: 'yeo-johnson' (works with negative values), 'box-cox' (positive only)
- Use when: Data is skewed, algorithm assumes normality
- Example:
```python
from sklearn.preprocessing import PowerTransformer

# Yeo-Johnson (handles negative values)
pt = PowerTransformer(method='yeo-johnson', standardize=True)
X_transformed = pt.fit_transform(X)

# Box-Cox (positive values only)
pt = PowerTransformer(method='box-cox', standardize=True)
X_transformed = pt.fit_transform(X)
```

### Quantile Transformation

**QuantileTransformer**
- Transforms features to follow uniform or normal distribution
- Robust to outliers
- Use when: Want to reduce outlier impact
- Example:
```python
from sklearn.preprocessing import QuantileTransformer

# Transform to uniform distribution
qt = QuantileTransformer(output_distribution='uniform', random_state=42)
X_transformed = qt.fit_transform(X)

# Transform to normal distribution
qt = QuantileTransformer(output_distribution='normal', random_state=42)
X_transformed = qt.fit_transform(X)
```

### Log Transform

```python
import numpy as np

# Log1p (log(1 + x)) - handles zeros
X_log = np.log1p(X)

# Or use FunctionTransformer
from sklearn.preprocessing import FunctionTransformer

log_transformer = FunctionTransformer(np.log1p, inverse_func=np.expm1)
X_log = log_transformer.fit_transform(X)
```

## Missing Value Imputation

### SimpleImputer

**SimpleImputer (`sklearn.impute.SimpleImputer`)**
- Basic imputation strategies
- Strategies: 'mean', 'median', 'most_frequent', 'constant'
- Example:
```python
from sklearn.impute import SimpleImputer

# For numerical features
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# For categorical features
imputer = SimpleImputer(strategy='most_frequent')
X_imputed = imputer.fit_transform(X_categorical)

# Fill with constant
imputer = SimpleImputer(strategy='constant', fill_value=0)
X_imputed = imputer.fit_transform(X)
```

### Iterative Imputer

**IterativeImputer**
- Models each feature with missing values as function of other features
- More sophisticated than SimpleImputer
- Example:
```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

imputer = IterativeImputer(max_iter=10, random_state=42)
X_imputed = imputer.fit_transform(X)
```

### KNN Imputer

**KNNImputer**
- Imputes using k-nearest neighbors
- Use when: Features are correlated
- Example:
```python
from sklearn.impute import KNNImputer

imputer = KNNImputer(n_neighbors=5)
X_imputed = imputer.fit_transform(X)
```

## Feature Engineering

### Polynomial Features

**PolynomialFeatures**
- Creates polynomial and interaction features
- Use when: Need non-linear features for linear models
- Example:
```python
from sklearn.preprocessing import PolynomialFeatures

# Degree 2: includes x1, x2, x1^2, x2^2, x1*x2
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

# Get feature names
feature_names = poly.get_feature_names_out(['x1', 'x2'])

# Only interactions (no powers)
poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_interactions = poly.fit_transform(X)
```

### Binning/Discretization

**KBinsDiscretizer**
- Bins continuous features into discrete intervals
- Strategies: 'uniform', 'quantile', 'kmeans'
- Encoding: 'onehot', 'ordinal', 'onehot-dense'
- Example:
```python
from sklearn.preprocessing import KBinsDiscretizer

# Equal-width bins
binner = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='uniform')
X_binned = binner.fit_transform(X)

# Equal-frequency bins (quantile-based)
binner = KBinsDiscretizer(n_bins=5, encode='onehot', strategy='quantile')
X_binned = binner.fit_transform(X)
```

### Binarization

**Binarizer**
- Converts features to binary (0 or 1) based on threshold
- Example:
```python
from sklearn.preprocessing import Binarizer

binarizer = Binarizer(threshold=0.5)
X_binary = binarizer.fit_transform(X)
```

### Spline Features

**SplineTransformer**
- Creates spline basis functions
- Useful for capturing non-linear relationships
- Example:
```python
from sklearn.preprocessing import SplineTransformer

spline = SplineTransformer(n_knots=5, degree=3)
X_splines = spline.fit_transform(X)
```

## Text Feature Extraction

### CountVectorizer

**CountVectorizer (`sklearn.feature_extraction.text.CountVectorizer`)**
- Converts text to token count matrix
- Use for: Bag-of-words representation
- Example:
```python
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(
    max_features=5000,  # Keep top 5000 features
    min_df=2,  # Ignore terms appearing in < 2 documents
    max_df=0.8,  # Ignore terms appearing in > 80% documents
    ngram_range=(1, 2)  # Unigrams and bigrams
)

X_counts = vectorizer.fit_transform(documents)
feature_names = vectorizer.get_feature_names_out()
```

### TfidfVectorizer

**TfidfVectorizer**
- TF-IDF (Term Frequency-Inverse Document Frequency) transformation
- Better than CountVectorizer for most tasks
- Example:
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=5000,
    min_df=2,
    max_df=0.8,
    ngram_range=(1, 2),
    stop_words='english'  # Remove English stop words
)

X_tfidf = vectorizer.fit_transform(documents)
```

### HashingVectorizer

**HashingVectorizer**
- Uses hashing trick for memory efficiency
- No fit needed, can't reverse transform
- Use when: Very large vocabulary, streaming data
- Example:
```python
from sklearn.feature_extraction.text import HashingVectorizer

vectorizer = HashingVectorizer(n_features=2**18)
X_hashed = vectorizer.transform(documents)  # No fit needed
```

## Feature Selection

### Filter Methods

**Variance Threshold**
- Removes low-variance features
- Example:
```python
from sklearn.feature_selection import VarianceThreshold

selector = VarianceThreshold(threshold=0.01)
X_selected = selector.fit_transform(X)
```

**SelectKBest / SelectPercentile**
- Select features based on statistical tests
- Tests: f_classif, chi2, mutual_info_classif
- Example:
```python
from sklearn.feature_selection import SelectKBest, f_classif

# Select top 10 features
selector = SelectKBest(score_func=f_classif, k=10)
X_selected = selector.fit_transform(X_train, y_train)

# Get selected feature indices
selected_indices = selector.get_support(indices=True)
```

### Wrapper Methods

**Recursive Feature Elimination (RFE)**
- Recursively removes features
- Uses model feature importances
- Example:
```python
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
rfe = RFE(estimator=model, n_features_to_select=10, step=1)
X_selected = rfe.fit_transform(X_train, y_train)

# Get selected features
selected_features = rfe.support_
feature_ranking = rfe.ranking_
```

**RFECV (with Cross-Validation)**
- RFE with cross-validation to find optimal number of features
- Example:
```python
from sklearn.feature_selection import RFECV

model = RandomForestClassifier(n_estimators=100, random_state=42)
rfecv = RFECV(estimator=model, cv=5, scoring='accuracy')
X_selected = rfecv.fit_transform(X_train, y_train)

print(f"Optimal number of features: {rfecv.n_features_}")
```

### Embedded Methods

**SelectFromModel**
- Select features based on model coefficients/importances
- Works with: Linear models (L1), Tree-based models
- Example:
```python
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
selector = SelectFromModel(model, threshold='median')
selector.fit(X_train, y_train)
X_selected = selector.transform(X_train)

# Get selected features
selected_features = selector.get_support()
```

**L1-based Feature Selection**
```python
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectFromModel

model = LogisticRegression(l1_ratio=1.0, solver='liblinear', C=0.1)
selector = SelectFromModel(model)
selector.fit(X_train, y_train)
X_selected = selector.transform(X_train)
```

## Handling Outliers

### IQR Method

```python
import numpy as np

Q1 = np.percentile(X, 25, axis=0)
Q3 = np.percentile(X, 75, axis=0)
IQR = Q3 - Q1

# Define outlier boundaries
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Remove outliers
mask = np.all((X >= lower_bound) & (X <= upper_bound), axis=1)
X_no_outliers = X[mask]
```

### Winsorization

```python
from scipy.stats import mstats

# Clip outliers at 5th and 95th percentiles
X_winsorized = mstats.winsorize(X, limits=[0.05, 0.05], axis=0)
```

## Custom Transformers

### Using FunctionTransformer

```python
from sklearn.preprocessing import FunctionTransformer
import numpy as np

def log_transform(X):
    return np.log1p(X)

transformer = FunctionTransformer(log_transform, inverse_func=np.expm1)
X_transformed = transformer.fit_transform(X)
```

### Creating Custom Transformer

```python
from sklearn.base import BaseEstimator, TransformerMixin

class CustomTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, parameter=1):
        self.parameter = parameter

    def fit(self, X, y=None):
        # Learn parameters from X if needed
        return self

    def transform(self, X):
        # Transform X
        return X * self.parameter

transformer = CustomTransformer(parameter=2)
X_transformed = transformer.fit_transform(X)
```

## Best Practices

### Fit on Training Data Only
Always fit transformers on training data only:
```python
# Correct
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Wrong - causes data leakage
scaler = StandardScaler()
X_all_scaled = scaler.fit_transform(np.vstack([X_train, X_test]))
```

### Use Pipelines
Combine preprocessing with models:
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', LogisticRegression())
])

pipeline.fit(X_train, y_train)
```

### Handle Categorical and Numerical Separately
Use ColumnTransformer:
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

numeric_features = ['age', 'income']
categorical_features = ['gender', 'occupation']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
    ]
)

X_transformed = preprocessor.fit_transform(X)
```

### Algorithm-Specific Requirements

**Require Scaling:**
- SVM, KNN, Neural Networks
- PCA, Linear/Logistic Regression with regularization
- K-Means clustering

**Don't Require Scaling:**
- Tree-based models (Decision Trees, Random Forest, Gradient Boosting)
- Naive Bayes

**Encoding Requirements:**
- Linear models, SVM, KNN: One-hot encoding for nominal features
- Tree-based models: Can handle ordinal encoding directly

### `references/quick_reference.md`

# Scikit-learn Quick Reference

## Common Import Patterns

```python
# Core scikit-learn
import sklearn

# Data splitting and cross-validation
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV

# Preprocessing
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Feature selection
from sklearn.feature_selection import SelectKBest, RFE

# Supervised learning
from sklearn.linear_model import LogisticRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.svm import SVC, SVR
from sklearn.tree import DecisionTreeClassifier

# Unsupervised learning
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, NMF

# Metrics
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, root_mean_squared_error, r2_score,
    confusion_matrix, classification_report
)

# Pipeline
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer, make_column_transformer

# Utilities
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

## Installation

Tested against scikit-learn **1.8.0** (Python 3.11–3.14). Install the PyPI package `scikit-learn` (import as `sklearn`).

```bash
# Using uv (recommended)
uv pip install "scikit-learn>=1.7"

# Optional dependencies
uv pip install "scikit-learn[plots]"  # For plotting utilities
uv pip install pandas numpy matplotlib seaborn  # Common companions
```

## Quick Workflow Templates

### Classification Pipeline

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# Preprocess
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
```

### Regression Pipeline

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, root_mean_squared_error, r2_score

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Preprocess and train
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = GradientBoostingRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate
y_pred = model.predict(X_test_scaled)
print(f"RMSE: {root_mean_squared_error(y_test, y_pred):.3f}")
print(f"R² Score: {r2_score(y_test, y_pred):.3f}")
```

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(n_estimators=100, random_state=42)
scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"CV Accuracy: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

### Complete Pipeline with Mixed Data Types

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

# Define feature types
numeric_features = ['age', 'income']
categorical_features = ['gender', 'occupation']

# Create preprocessing pipelines
numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine transformers
preprocessor = ColumnTransformer([
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])

# Full pipeline
model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Fit and predict
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

### Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10]
}

model = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(
    model, param_grid, cv=5, scoring='accuracy', n_jobs=-1
)

grid_search.fit(X_train, y_train)
print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.3f}")

# Use best model
best_model = grid_search.best_estimator_
```

## Common Patterns

### Loading Data

```python
# From scikit-learn datasets
from sklearn.datasets import load_iris, load_digits, make_classification

# Built-in datasets
iris = load_iris()
X, y = iris.data, iris.target

# Synthetic data
X, y = make_classification(
    n_samples=1000, n_features=20, n_classes=2, random_state=42
)

# From pandas
import pandas as pd
df = pd.read_csv('data.csv')
X = df.drop('target', axis=1)
y = df['target']
```

### Handling Imbalanced Data

```python
from sklearn.ensemble import RandomForestClassifier

# Use class_weight parameter
model = RandomForestClassifier(class_weight='balanced', random_state=42)
model.fit(X_train, y_train)

# Or use appropriate metrics
from sklearn.metrics import balanced_accuracy_score, f1_score
print(f"Balanced Accuracy: {balanced_accuracy_score(y_test, y_pred):.3f}")
print(f"F1 Score: {f1_score(y_test, y_pred):.3f}")
```

### Feature Importance

```python
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Get feature importances
importances = pd.DataFrame({
    'feature': feature_names,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(importances.head(10))
```

### Clustering

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Scale data first
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Fit K-Means
kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(X_scaled)

# Evaluate
from sklearn.metrics import silhouette_score
score = silhouette_score(X_scaled, labels)
print(f"Silhouette Score: {score:.3f}")
```

### Dimensionality Reduction

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Fit PCA
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)

# Plot
plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=y, cmap='viridis')
plt.xlabel('PC1')
plt.ylabel('PC2')
plt.title(f'PCA (explained variance: {pca.explained_variance_ratio_.sum():.2%})')
```

### Model Persistence

```python
import joblib

# Save model
joblib.dump(model, 'model.pkl')

# Load model
loaded_model = joblib.load('model.pkl')
predictions = loaded_model.predict(X_new)
```

## Common Gotchas and Solutions

### Data Leakage
```python
# WRONG: Fitting scaler on all data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test = train_test_split(X_scaled)

# RIGHT: Fit on training data only
X_train, X_test = train_test_split(X)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# BEST: Use Pipeline
from sklearn.pipeline import Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])
pipeline.fit(X_train, y_train)  # No leakage!
```

### Stratified Splitting for Classification
```python
# Always use stratify for classification
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

### Random State for Reproducibility
```python
# Set random_state for reproducibility
model = RandomForestClassifier(n_estimators=100, random_state=42)
```

### Handling Unknown Categories
```python
# Use handle_unknown='ignore' for OneHotEncoder
encoder = OneHotEncoder(handle_unknown='ignore')
```

### Feature Names with Pipelines
```python
# Get feature names after transformation
preprocessor.fit(X_train)
feature_names = preprocessor.get_feature_names_out()
```

## Cheat Sheet: Algorithm Selection

### Classification

| Problem | Algorithm | When to Use |
|---------|-----------|-------------|
| Binary/Multiclass | Logistic Regression | Fast baseline, interpretability |
| Binary/Multiclass | Random Forest | Good default, robust |
| Binary/Multiclass | Gradient Boosting | Best accuracy, willing to tune |
| Binary/Multiclass | SVM | Small data, complex boundaries |
| Binary/Multiclass | Naive Bayes | Text classification, fast |
| High dimensions | Linear SVM or Logistic | Text, many features |

### Regression

| Problem | Algorithm | When to Use |
|---------|-----------|-------------|
| Continuous target | Linear Regression | Fast baseline, interpretability |
| Continuous target | Ridge/Lasso | Regularization needed |
| Continuous target | Random Forest | Good default, non-linear |
| Continuous target | Gradient Boosting | Best accuracy |
| Continuous target | SVR | Small data, non-linear |

### Clustering

| Problem | Algorithm | When to Use |
|---------|-----------|-------------|
| Known K, spherical | K-Means | Fast, simple |
| Unknown K, arbitrary shapes | DBSCAN | Noise/outliers present |
| Hierarchical structure | Agglomerative | Need dendrogram |
| Soft clustering | Gaussian Mixture | Probability estimates |

### Dimensionality Reduction

| Problem | Algorithm | When to Use |
|---------|-----------|-------------|
| Linear reduction | PCA | Variance explanation |
| Visualization | t-SNE | 2D/3D plots |
| Non-negative data | NMF | Images, text |
| Sparse data | TruncatedSVD | Text, recommender systems |

## Performance Tips

### Speed Up Training
```python
# Use n_jobs=-1 for parallel processing
model = RandomForestClassifier(n_estimators=100, n_jobs=-1)

# Use warm_start for incremental learning
model = RandomForestClassifier(n_estimators=100, warm_start=True)
model.fit(X, y)
model.n_estimators += 50
model.fit(X, y)  # Adds 50 more trees

# Use partial_fit for online learning
from sklearn.linear_model import SGDClassifier
model = SGDClassifier()
for X_batch, y_batch in batches:
    model.partial_fit(X_batch, y_batch, classes=np.unique(y))
```

### Memory Efficiency
```python
# Use sparse matrices
from scipy.sparse import csr_matrix
X_sparse = csr_matrix(X)

# Use MiniBatchKMeans for large data
from sklearn.cluster import MiniBatchKMeans
model = MiniBatchKMeans(n_clusters=8, batch_size=100)
```

## Version Check

```python
import sklearn
print(f"scikit-learn version: {sklearn.__version__}")
```

## Useful Resources

- Official Documentation: https://scikit-learn.org/stable/
- User Guide: https://scikit-learn.org/stable/user_guide.html
- API Reference: https://scikit-learn.org/stable/api/index.html
- Examples: https://scikit-learn.org/stable/auto_examples/index.html
- Tutorials: https://scikit-learn.org/stable/tutorial/index.html

### `references/supervised_learning.md`

# Supervised Learning Reference

## Overview

Supervised learning algorithms learn from labeled training data to make predictions on new data. Scikit-learn provides comprehensive implementations for both classification and regression tasks.

## Linear Models

### Regression

**Linear Regression (`sklearn.linear_model.LinearRegression`)**
- Ordinary least squares regression
- Fast, interpretable, no hyperparameters
- Use when: Linear relationships, interpretability matters
- Example:
```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

**Ridge Regression (`sklearn.linear_model.Ridge`)**
- L2 regularization to prevent overfitting
- Key parameter: `alpha` (regularization strength, default=1.0)
- Use when: Multicollinearity present, need regularization
- Example:
```python
from sklearn.linear_model import Ridge

model = Ridge(alpha=1.0)
model.fit(X_train, y_train)
```

**Lasso (`sklearn.linear_model.Lasso`)**
- L1 regularization with feature selection
- Key parameter: `alpha` (regularization strength)
- Use when: Want sparse models, feature selection
- Can reduce some coefficients to exactly zero
- Example:
```python
from sklearn.linear_model import Lasso

model = Lasso(alpha=0.1)
model.fit(X_train, y_train)
# Check which features were selected
print(f"Non-zero coefficients: {sum(model.coef_ != 0)}")
```

**ElasticNet (`sklearn.linear_model.ElasticNet`)**
- Combines L1 and L2 regularization
- Key parameters: `alpha`, `l1_ratio` (0=Ridge, 1=Lasso)
- Use when: Need both feature selection and regularization
- Example:
```python
from sklearn.linear_model import ElasticNet

model = ElasticNet(alpha=0.1, l1_ratio=0.5)
model.fit(X_train, y_train)
```

### Classification

**Logistic Regression (`sklearn.linear_model.LogisticRegression`)**
- Binary and multiclass classification
- Key parameters: `C` (inverse regularization), `l1_ratio` (0=L2, 1=L1, between for elastic net)
- Returns probability estimates
- Use when: Need probabilistic predictions, interpretability
- Note: The `penalty` parameter is deprecated since 1.8; use `l1_ratio` instead
- Example:
```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(C=1.0, l1_ratio=0.0, max_iter=1000)
model.fit(X_train, y_train)
probas = model.predict_proba(X_test)
```

**Stochastic Gradient Descent (SGD)**
- `SGDClassifier`, `SGDRegressor`
- Efficient for large-scale learning
- Key parameters: `loss`, `penalty`, `alpha`, `learning_rate`
- Use when: Very large datasets (>10^4 samples)
- Example:
```python
from sklearn.linear_model import SGDClassifier

model = SGDClassifier(loss='log_loss', max_iter=1000, tol=1e-3)
model.fit(X_train, y_train)
```

## Support Vector Machines

**SVC (`sklearn.svm.SVC`)**
- Classification with kernel methods
- Key parameters: `C`, `kernel` ('linear', 'rbf', 'poly'), `gamma`
- Use when: Small to medium datasets, complex decision boundaries
- Note: Does not scale well to large datasets
- Example:
```python
from sklearn.svm import SVC

# Linear kernel for linearly separable data
model_linear = SVC(kernel='linear', C=1.0)

# RBF kernel for non-linear data
model_rbf = SVC(kernel='rbf', C=1.0, gamma='scale')
model_rbf.fit(X_train, y_train)
```

**SVR (`sklearn.svm.SVR`)**
- Regression with kernel methods
- Similar parameters to SVC
- Additional parameter: `epsilon` (tube width)
- Example:
```python
from sklearn.svm import SVR

model = SVR(kernel='rbf', C=1.0, epsilon=0.1)
model.fit(X_train, y_train)
```

## Decision Trees

**DecisionTreeClassifier / DecisionTreeRegressor**
- Non-parametric model learning decision rules
- Key parameters:
  - `max_depth`: Maximum tree depth (prevents overfitting)
  - `min_samples_split`: Minimum samples to split a node
  - `min_samples_leaf`: Minimum samples in leaf
  - `criterion`: 'gini', 'entropy' for classification; 'squared_error', 'absolute_error' for regression
- Use when: Need interpretable model, non-linear relationships, mixed feature types
- Prone to overfitting - use ensembles or pruning
- Example:
```python
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(
    max_depth=5,
    min_samples_split=20,
    min_samples_leaf=10,
    criterion='gini'
)
model.fit(X_train, y_train)

# Visualize the tree
from sklearn.tree import plot_tree
plot_tree(model, feature_names=feature_names, class_names=class_names)
```

## Ensemble Methods

### Random Forests

**RandomForestClassifier / RandomForestRegressor**
- Ensemble of decision trees with bagging
- Key parameters:
  - `n_estimators`: Number of trees (default=100)
  - `max_depth`: Maximum tree depth
  - `max_features`: Features to consider for splits ('sqrt', 'log2', or int)
  - `min_samples_split`, `min_samples_leaf`: Control tree growth
- Use when: High accuracy needed, can afford computation
- Provides feature importance
- Example:
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    max_features='sqrt',
    n_jobs=-1  # Use all CPU cores
)
model.fit(X_train, y_train)

# Feature importance
importances = model.feature_importances_
```

### Gradient Boosting

**GradientBoostingClassifier / GradientBoostingRegressor**
- Sequential ensemble building trees on residuals
- Key parameters:
  - `n_estimators`: Number of boosting stages
  - `learning_rate`: Shrinks contribution of each tree
  - `max_depth`: Depth of individual trees (typically 3-5)
  - `subsample`: Fraction of samples for training each tree
- Use when: Need high accuracy, can afford training time
- Often achieves best performance
- Example:
```python
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    subsample=0.8
)
model.fit(X_train, y_train)
```

**HistGradientBoostingClassifier / HistGradientBoostingRegressor**
- Faster gradient boosting with histogram-based algorithm
- Native support for missing values and categorical features
- Key parameters: Similar to GradientBoosting
- Use when: Large datasets, need faster training
- Example:
```python
from sklearn.ensemble import HistGradientBoostingClassifier

model = HistGradientBoostingClassifier(
    max_iter=100,
    learning_rate=0.1,
    max_depth=None,  # No limit by default
    categorical_features='from_dtype'  # Auto-detect categorical
)
model.fit(X_train, y_train)
```

### Other Ensemble Methods

**AdaBoost**
- Adaptive boosting focusing on misclassified samples
- Key parameters: `n_estimators`, `learning_rate`, `estimator` (base estimator)
- Use when: Simple boosting approach needed
- Example:
```python
from sklearn.ensemble import AdaBoostClassifier

model = AdaBoostClassifier(n_estimators=50, learning_rate=1.0)
model.fit(X_train, y_train)
```

**Voting Classifier / Regressor**
- Combines predictions from multiple models
- Types: 'hard' (majority vote) or 'soft' (average probabilities)
- Use when: Want to ensemble different model types
- Example:
```python
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

model = VotingClassifier(
    estimators=[
        ('lr', LogisticRegression()),
        ('dt', DecisionTreeClassifier()),
        ('svc', SVC(probability=True))
    ],
    voting='soft'
)
model.fit(X_train, y_train)
```

**Stacking Classifier / Regressor**
- Trains a meta-model on predictions from base models
- More sophisticated than voting
- Key parameter: `final_estimator` (meta-learner)
- Example:
```python
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

model = StackingClassifier(
    estimators=[
        ('dt', DecisionTreeClassifier()),
        ('svc', SVC())
    ],
    final_estimator=LogisticRegression()
)
model.fit(X_train, y_train)
```

## K-Nearest Neighbors

**KNeighborsClassifier / KNeighborsRegressor**
- Non-parametric method based on distance
- Key parameters:
  - `n_neighbors`: Number of neighbors (default=5)
  - `weights`: 'uniform' or 'distance'
  - `metric`: Distance metric ('euclidean', 'manhattan', etc.)
- Use when: Small dataset, simple baseline needed
- Slow prediction on large datasets
- Example:
```python
from sklearn.neighbors import KNeighborsClassifier

model = KNeighborsClassifier(n_neighbors=5, weights='distance')
model.fit(X_train, y_train)
```

## Naive Bayes

**GaussianNB, MultinomialNB, BernoulliNB**
- Probabilistic classifiers based on Bayes' theorem
- Fast training and prediction
- GaussianNB: Continuous features (assumes Gaussian distribution)
- MultinomialNB: Count features (text classification)
- BernoulliNB: Binary features
- Use when: Text classification, fast baseline, probabilistic predictions
- Example:
```python
from sklearn.naive_bayes import GaussianNB, MultinomialNB

# For continuous features
model_gaussian = GaussianNB()

# For text/count data
model_multinomial = MultinomialNB(alpha=1.0)  # alpha is smoothing parameter
model_multinomial.fit(X_train, y_train)
```

## Neural Networks

**MLPClassifier / MLPRegressor**
- Multi-layer perceptron (feedforward neural network)
- Key parameters:
  - `hidden_layer_sizes`: Tuple of hidden layer sizes, e.g., (100, 50)
  - `activation`: 'relu', 'tanh', 'logistic'
  - `solver`: 'adam', 'sgd', 'lbfgs'
  - `alpha`: L2 regularization parameter
  - `learning_rate`: 'constant', 'adaptive'
- Use when: Complex non-linear patterns, large datasets
- Requires feature scaling
- Example:
```python
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

# Scale features first
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

model = MLPClassifier(
    hidden_layer_sizes=(100, 50),
    activation='relu',
    solver='adam',
    alpha=0.0001,
    max_iter=1000
)
model.fit(X_train_scaled, y_train)
```

## Algorithm Selection Guide

### Choose based on:

**Dataset size:**
- Small (<1k samples): KNN, SVM, Decision Trees
- Medium (1k-100k): Random Forest, Gradient Boosting, Linear Models
- Large (>100k): SGD, Linear Models, HistGradientBoosting

**Interpretability:**
- High: Linear Models, Decision Trees
- Medium: Random Forest (feature importance)
- Low: SVM with RBF kernel, Neural Networks

**Accuracy vs Speed:**
- Fast training: Naive Bayes, Linear Models, KNN
- High accuracy: Gradient Boosting, Random Forest, Stacking
- Fast prediction: Linear Models, Naive Bayes
- Slow prediction: KNN (on large datasets), SVM

**Feature types:**
- Continuous: Most algorithms work well
- Categorical: Trees, HistGradientBoosting (native support)
- Mixed: Trees, Gradient Boosting
- Text: Naive Bayes, Linear Models with TF-IDF

**Common starting points:**
1. Logistic Regression (classification) / Linear Regression (regression) - fast baseline
2. Random Forest - good default choice
3. Gradient Boosting - optimize for best accuracy

### `references/unsupervised_learning.md`

# Unsupervised Learning Reference

## Overview

Unsupervised learning discovers patterns in unlabeled data through clustering, dimensionality reduction, and density estimation.

## Clustering

### K-Means

**KMeans (`sklearn.cluster.KMeans`)**
- Partition-based clustering into K clusters
- Key parameters:
  - `n_clusters`: Number of clusters to form
  - `init`: Initialization method ('k-means++', 'random')
  - `n_init`: Number of initializations (default=10)
  - `max_iter`: Maximum iterations
- Use when: Know number of clusters, spherical cluster shapes
- Fast and scalable
- Example:
```python
from sklearn.cluster import KMeans

model = KMeans(n_clusters=3, init='k-means++', n_init=10, random_state=42)
labels = model.fit_predict(X)
centers = model.cluster_centers_

# Inertia (sum of squared distances to nearest center)
print(f"Inertia: {model.inertia_}")
```

**MiniBatchKMeans**
- Faster K-Means using mini-batches
- Use when: Large datasets, need faster training
- Slightly less accurate than K-Means
- Example:
```python
from sklearn.cluster import MiniBatchKMeans

model = MiniBatchKMeans(n_clusters=3, batch_size=100, random_state=42)
labels = model.fit_predict(X)
```

### Density-Based Clustering

**DBSCAN (`sklearn.cluster.DBSCAN`)**
- Density-Based Spatial Clustering
- Key parameters:
  - `eps`: Maximum distance between two samples to be neighbors
  - `min_samples`: Minimum samples in neighborhood to form core point
  - `metric`: Distance metric
- Use when: Arbitrary cluster shapes, presence of noise/outliers
- Automatically determines number of clusters
- Labels noise points as -1
- Example:
```python
from sklearn.cluster import DBSCAN

model = DBSCAN(eps=0.5, min_samples=5, metric='euclidean')
labels = model.fit_predict(X)

# Number of clusters (excluding noise)
n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
n_noise = list(labels).count(-1)
print(f"Clusters: {n_clusters}, Noise points: {n_noise}")
```

**HDBSCAN (`sklearn.cluster.HDBSCAN`)**
- Hierarchical DBSCAN with adaptive epsilon (added in scikit-learn 1.3)
- More robust than DBSCAN; prefer this over the separate `hdbscan` PyPI package for new projects
- Key parameter: `min_cluster_size`
- Use when: Varying density clusters
- Example:
```python
from sklearn.cluster import HDBSCAN

model = HDBSCAN(min_cluster_size=10, min_samples=5)
labels = model.fit_predict(X)
```

**OPTICS (`sklearn.cluster.OPTICS`)**
- Ordering points to identify clustering structure
- Similar to DBSCAN but doesn't require eps parameter
- Key parameters: `min_samples`, `max_eps`
- Use when: Varying density, exploratory analysis
- Example:
```python
from sklearn.cluster import OPTICS

model = OPTICS(min_samples=5, max_eps=0.5)
labels = model.fit_predict(X)
```

### Hierarchical Clustering

**AgglomerativeClustering**
- Bottom-up hierarchical clustering
- Key parameters:
  - `n_clusters`: Number of clusters (or use `distance_threshold`)
  - `linkage`: 'ward', 'complete', 'average', 'single'
  - `metric`: Distance metric
- Use when: Need dendrogram, hierarchical structure important
- Example:
```python
from sklearn.cluster import AgglomerativeClustering

model = AgglomerativeClustering(n_clusters=3, linkage='ward')
labels = model.fit_predict(X)

# Create dendrogram using scipy
from scipy.cluster.hierarchy import dendrogram, linkage
Z = linkage(X, method='ward')
dendrogram(Z)
```

### Other Clustering Methods

**MeanShift**
- Finds clusters by shifting points toward mode of density
- Automatically determines number of clusters
- Key parameter: `bandwidth`
- Use when: Don't know number of clusters, arbitrary shapes
- Example:
```python
from sklearn.cluster import MeanShift, estimate_bandwidth

# Estimate bandwidth
bandwidth = estimate_bandwidth(X, quantile=0.2, n_samples=500)
model = MeanShift(bandwidth=bandwidth)
labels = model.fit_predict(X)
```

**SpectralClustering**
- Uses graph-based approach with eigenvalues
- Key parameters: `n_clusters`, `affinity` ('rbf', 'nearest_neighbors')
- Use when: Non-convex clusters, graph structure
- Example:
```python
from sklearn.cluster import SpectralClustering

model = SpectralClustering(n_clusters=3, affinity='rbf', random_state=42)
labels = model.fit_predict(X)
```

**AffinityPropagation**
- Finds exemplars by message passing
- Automatically determines number of clusters
- Key parameters: `damping`, `preference`
- Use when: Don't know number of clusters
- Example:
```python
from sklearn.cluster import AffinityPropagation

model = AffinityPropagation(damping=0.9, random_state=42)
labels = model.fit_predict(X)
n_clusters = len(model.cluster_centers_indices_)
```

**BIRCH**
- Balanced Iterative Reducing and Clustering using Hierarchies
- Memory efficient for large datasets
- Key parameters: `n_clusters`, `threshold`, `branching_factor`
- Use when: Very large datasets
- Example:
```python
from sklearn.cluster import Birch

model = Birch(n_clusters=3, threshold=0.5)
labels = model.fit_predict(X)
```

### Clustering Evaluation

**Metrics when ground truth is known:**
```python
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from sklearn.metrics import adjusted_mutual_info_score, fowlkes_mallows_score

# Compare predicted labels with true labels
ari = adjusted_rand_score(y_true, y_pred)
nmi = normalized_mutual_info_score(y_true, y_pred)
ami = adjusted_mutual_info_score(y_true, y_pred)
fmi = fowlkes_mallows_score(y_true, y_pred)
```

**Metrics without ground truth:**
```python
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics import davies_bouldin_score

# Silhouette: [-1, 1], higher is better
silhouette = silhouette_score(X, labels)

# Calinski-Harabasz: higher is better
ch_score = calinski_harabasz_score(X, labels)

# Davies-Bouldin: lower is better
db_score = davies_bouldin_score(X, labels)
```

**Elbow method for K-Means:**
```python
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

inertias = []
K_range = range(2, 11)
for k in K_range:
    model = KMeans(n_clusters=k, random_state=42)
    model.fit(X)
    inertias.append(model.inertia_)

plt.plot(K_range, inertias, 'bo-')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')
plt.title('Elbow Method')
```

## Dimensionality Reduction

### Principal Component Analysis (PCA)

**PCA (`sklearn.decomposition.PCA`)**
- Linear dimensionality reduction using SVD
- Key parameters:
  - `n_components`: Number of components (int or float for explained variance)
  - `whiten`: Whiten components to unit variance
- Use when: Linear relationships, want to explain variance
- Example:
```python
from sklearn.decomposition import PCA

# Keep components explaining 95% variance
pca = PCA(n_components=0.95)
X_reduced = pca.fit_transform(X)

print(f"Original dimensions: {X.shape[1]}")
print(f"Reduced dimensions: {X_reduced.shape[1]}")
print(f"Explained variance ratio: {pca.explained_variance_ratio_}")
print(f"Total variance explained: {pca.explained_variance_ratio_.sum()}")

# Or specify exact number of components
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X)
```

**IncrementalPCA**
- PCA for large datasets that don't fit in memory
- Processes data in batches
- Key parameter: `n_components`, `batch_size`
- Example:
```python
from sklearn.decomposition import IncrementalPCA

pca = IncrementalPCA(n_components=50, batch_size=100)
X_reduced = pca.fit_transform(X)
```

**KernelPCA**
- Non-linear dimensionality reduction using kernels
- Key parameters: `n_components`, `kernel` ('linear', 'poly', 'rbf', 'sigmoid')
- Use when: Non-linear relationships
- Example:
```python
from sklearn.decomposition import KernelPCA

pca = KernelPCA(n_components=2, kernel='rbf', gamma=0.1)
X_reduced = pca.fit_transform(X)
```

### Manifold Learning

**t-SNE (`sklearn.manifold.TSNE`)**
- t-distributed Stochastic Neighbor Embedding
- Excellent for 2D/3D visualization
- Key parameters:
  - `n_components`: Usually 2 or 3
  - `perplexity`: Balance between local and global structure (5-50)
  - `learning_rate`: Usually 10-1000
  - `max_iter`: Number of iterations (minimum 250; renamed from `n_iter` in 1.5)
- Use when: Visualizing high-dimensional data
- Note: Slow on large datasets, no transform() method
- Example:
```python
from sklearn.manifold import TSNE

tsne = TSNE(n_components=2, perplexity=30, learning_rate=200, max_iter=1000, random_state=42)
X_embedded = tsne.fit_transform(X)

# Visualize
import matplotlib.pyplot as plt
plt.scatter(X_embedded[:, 0], X_embedded[:, 1], c=labels, cmap='viridis')
plt.title('t-SNE visualization')
```

**UMAP (not in scikit-learn, but compatible)**
- Uniform Manifold Approximation and Projection
- Faster than t-SNE, preserves global structure better
- Install: `uv pip install umap-learn`
- Example:
```python
from umap import UMAP

reducer = UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
X_embedded = reducer.fit_transform(X)
```

**Isomap**
- Isometric Mapping
- Preserves geodesic distances
- Key parameters: `n_components`, `n_neighbors`
- Use when: Non-linear manifolds
- Example:
```python
from sklearn.manifold import Isomap

isomap = Isomap(n_components=2, n_neighbors=5)
X_embedded = isomap.fit_transform(X)
```

**Locally Linear Embedding (LLE)**
- Preserves local neighborhood structure
- Key parameters: `n_components`, `n_neighbors`
- Example:
```python
from sklearn.manifold import LocallyLinearEmbedding

lle = LocallyLinearEmbedding(n_components=2, n_neighbors=10)
X_embedded = lle.fit_transform(X)
```

**MDS (Multidimensional Scaling)**
- Preserves pairwise distances
- Key parameters: `n_components`, `metric`, `metric_params`, `init` (e.g. `'classical_mds'` in 1.8+)
- Note: `dissimilarity` is deprecated; the former `metric` boolean was renamed to `metric_mds`
- Example:
```python
from sklearn.manifold import MDS

mds = MDS(n_components=2, metric='euclidean', init='classical_mds', random_state=42)
X_embedded = mds.fit_transform(X)
```

**ClassicalMDS (`sklearn.manifold.ClassicalMDS`)**
- Classical (Torgerson) MDS via eigendecomposition of the double-centered distance matrix
- Added in scikit-learn 1.8; faster initialization path for `MDS`
- Example:
```python
from sklearn.manifold import ClassicalMDS

cmds = ClassicalMDS(n_components=2, random_state=42)
X_embedded = cmds.fit_transform(X)
```

### Matrix Factorization

**NMF (Non-negative Matrix Factorization)**
- Factorizes into non-negative matrices
- Key parameters: `n_components`, `init` ('nndsvd', 'random')
- Use when: Data is non-negative (images, text)
- Interpretable components
- Example:
```python
from sklearn.decomposition import NMF

nmf = NMF(n_components=10, init='nndsvd', random_state=42)
W = nmf.fit_transform(X)  # Document-topic matrix
H = nmf.components_  # Topic-word matrix
```

**TruncatedSVD**
- SVD for sparse matrices
- Similar to PCA but works with sparse data
- Use when: Text data, sparse matrices
- Example:
```python
from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=100, random_state=42)
X_reduced = svd.fit_transform(X_sparse)
print(f"Explained variance: {svd.explained_variance_ratio_.sum()}")
```

**FastICA**
- Independent Component Analysis
- Separates multivariate signal into independent components
- Key parameter: `n_components`
- Use when: Signal separation (e.g., audio, EEG)
- Example:
```python
from sklearn.decomposition import FastICA

ica = FastICA(n_components=10, random_state=42)
S = ica.fit_transform(X)  # Independent sources
A = ica.mixing_  # Mixing matrix
```

**LatentDirichletAllocation (LDA)**
- Topic modeling for text data
- Key parameters: `n_components` (number of topics), `learning_method` ('batch', 'online')
- Use when: Topic modeling, document clustering
- Example:
```python
from sklearn.decomposition import LatentDirichletAllocation

lda = LatentDirichletAllocation(n_components=10, random_state=42)
doc_topics = lda.fit_transform(X_counts)  # Document-topic distribution

# Get top words for each topic
feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    top_words = [feature_names[i] for i in topic.argsort()[-10:]]
    print(f"Topic {topic_idx}: {', '.join(top_words)}")
```

## Outlier and Novelty Detection

### Outlier Detection

**IsolationForest**
- Isolates anomalies using random trees
- Key parameters:
  - `contamination`: Expected proportion of outliers
  - `n_estimators`: Number of trees
- Use when: High-dimensional data, efficiency important
- Example:
```python
from sklearn.ensemble import IsolationForest

model = IsolationForest(contamination=0.1, random_state=42)
predictions = model.fit_predict(X)  # -1 for outliers, 1 for inliers
```

**LocalOutlierFactor**
- Measures local density deviation
- Key parameters: `n_neighbors`, `contamination`
- Use when: Varying density regions
- Example:
```python
from sklearn.neighbors import LocalOutlierFactor

lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
predictions = lof.fit_predict(X)  # -1 for outliers, 1 for inliers
outlier_scores = lof.negative_outlier_factor_
```

**One-Class SVM**
- Learns decision boundary around normal data
- Key parameters: `nu` (upper bound on outliers), `kernel`, `gamma`
- Use when: Small training set of normal data
- Example:
```python
from sklearn.svm import OneClassSVM

model = OneClassSVM(nu=0.1, kernel='rbf', gamma='auto')
model.fit(X_train)
predictions = model.predict(X_test)  # -1 for outliers, 1 for inliers
```

**EllipticEnvelope**
- Assumes Gaussian distribution
- Key parameter: `contamination`
- Use when: Data is Gaussian-distributed
- Example:
```python
from sklearn.covariance import EllipticEnvelope

model = EllipticEnvelope(contamination=0.1, random_state=42)
predictions = model.fit_predict(X)
```

## Gaussian Mixture Models

**GaussianMixture**
- Probabilistic clustering with mixture of Gaussians
- Key parameters:
  - `n_components`: Number of mixture components
  - `covariance_type`: 'full', 'tied', 'diag', 'spherical'
- Use when: Soft clustering, need probability estimates
- Example:
```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(n_components=3, covariance_type='full', random_state=42)
gmm.fit(X)

# Predict cluster labels
labels = gmm.predict(X)

# Get probability of each cluster
probabilities = gmm.predict_proba(X)

# Information criteria for model selection
print(f"BIC: {gmm.bic(X)}")  # Lower is better
print(f"AIC: {gmm.aic(X)}")  # Lower is better
```

## Choosing the Right Method

### Clustering:
- **Know K, spherical clusters**: K-Means
- **Arbitrary shapes, noise**: DBSCAN, HDBSCAN
- **Hierarchical structure**: AgglomerativeClustering
- **Very large data**: MiniBatchKMeans, BIRCH
- **Probabilistic**: GaussianMixture

### Dimensionality Reduction:
- **Linear, variance explanation**: PCA
- **Non-linear, visualization**: t-SNE, UMAP
- **Non-negative data**: NMF
- **Sparse data**: TruncatedSVD
- **Topic modeling**: LatentDirichletAllocation

### Outlier Detection:
- **High-dimensional**: IsolationForest
- **Varying density**: LocalOutlierFactor
- **Gaussian data**: EllipticEnvelope

### `scripts/classification_pipeline.py`

```python
"""
Complete classification pipeline example with preprocessing, model training,
hyperparameter tuning, and evaluation.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    accuracy_score, precision_score, recall_score, f1_score
)
import warnings
warnings.filterwarnings('ignore')


def create_preprocessing_pipeline(numeric_features, categorical_features):
    """
    Create a preprocessing pipeline for mixed data types.

    Parameters:
    -----------
    numeric_features : list
        List of numeric feature column names
    categorical_features : list
        List of categorical feature column names

    Returns:
    --------
    ColumnTransformer
        Preprocessing pipeline
    """
    # Numeric preprocessing
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    # Categorical preprocessing
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # Combine transformers
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    return preprocessor


def train_and_evaluate_model(X, y, numeric_features, categorical_features,
                             test_size=0.2, random_state=42):
    """
    Complete pipeline: preprocess, train, tune, and evaluate a classifier.

    Parameters:
    -----------
    X : DataFrame or array
        Feature matrix
    y : Series or array
        Target variable
    numeric_features : list
        List of numeric feature names
    categorical_features : list
        List of categorical feature names
    test_size : float
        Proportion of data for testing
    random_state : int
        Random seed

    Returns:
    --------
    dict
        Dictionary containing trained model, predictions, and metrics
    """
    # Split data with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )

    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    print(f"Class distribution in training: {pd.Series(y_train).value_counts().to_dict()}")

    # Create preprocessor
    preprocessor = create_preprocessing_pipeline(numeric_features, categorical_features)

    # Define models to compare
    models = {
        'Logistic Regression': Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(max_iter=1000, random_state=random_state))
        ]),
        'Random Forest': Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=100, random_state=random_state))
        ]),
        'Gradient Boosting': Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', GradientBoostingClassifier(n_estimators=100, random_state=random_state))
        ])
    }

    # Compare models using cross-validation
    print("\n" + "="*60)
    print("Model Comparison (5-Fold Cross-Validation)")
    print("="*60)

    cv_results = {}
    for name, model in models.items():
        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        cv_results[name] = scores.mean()
        print(f"{name:20s}: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")

    # Select best model based on CV
    best_model_name = max(cv_results, key=cv_results.get)
    best_model = models[best_model_name]

    print(f"\nBest model: {best_model_name}")

    # Hyperparameter tuning for best model
    if best_model_name == 'Random Forest':
        param_grid = {
            'classifier__n_estimators': [100, 200],
            'classifier__max_depth': [10, 20, None],
            'classifier__min_samples_split': [2, 5]
        }
    elif best_model_name == 'Gradient Boosting':
        param_grid = {
            'classifier__n_estimators': [100, 200],
            'classifier__learning_rate': [0.01, 0.1],
            'classifier__max_depth': [3, 5]
        }
    else:  # Logistic Regression
        param_grid = {
            'classifier__C': [0.1, 1.0, 10.0],
            'classifier__l1_ratio': [0.0]
        }

    print("\n" + "="*60)
    print("Hyperparameter Tuning")
    print("="*60)

    grid_search = GridSearchCV(
        best_model, param_grid, cv=5, scoring='accuracy',
        n_jobs=-1, verbose=0
    )

    grid_search.fit(X_train, y_train)

    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best CV score: {grid_search.best_score_:.4f}")

    # Evaluate on test set
    tuned_model = grid_search.best_estimator_
    y_pred = tuned_model.predict(X_test)
    y_pred_proba = tuned_model.predict_proba(X_test)

    print("\n" + "="*60)
    print("Test Set Evaluation")
    print("="*60)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")

    # ROC AUC (if binary classification)
    if len(np.unique(y)) == 2:
        roc_auc = roc_auc_score(y_test, y_pred_proba[:, 1])
        print(f"ROC AUC:   {roc_auc:.4f}")

    print("\n" + "="*60)
    print("Classification Report")
    print("="*60)
    print(classification_report(y_test, y_pred))

    print("\n" + "="*60)
    print("Confusion Matrix")
    print("="*60)
    print(confusion_matrix(y_test, y_pred))

    # Feature importance (if available)
    if hasattr(tuned_model.named_steps['classifier'], 'feature_importances_'):
        print("\n" + "="*60)
        print("Top 10 Most Important Features")
        print("="*60)

        feature_names = tuned_model.named_steps['preprocessor'].get_feature_names_out()
        importances = tuned_model.named_steps['classifier'].feature_importances_

        feature_importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False).head(10)

        print(feature_importance_df.to_string(index=False))

    return {
        'model': tuned_model,
        'y_test': y_test,
        'y_pred': y_pred,
        'y_pred_proba': y_pred_proba,
        'metrics': {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
    }


# Example usage
if __name__ == "__main__":
    # Load example dataset
    from sklearn.datasets import load_breast_cancer

    # Load data
    data = load_breast_cancer()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target

    # For demonstration, treat all features as numeric
    numeric_features = X.columns.tolist()
    categorical_features = []

    print("="*60)
    print("Classification Pipeline Example")
    print("Dataset: Breast Cancer Wisconsin")
    print("="*60)

    # Run complete pipeline
    results = train_and_evaluate_model(
        X, y, numeric_features, categorical_features,
        test_size=0.2, random_state=42
    )

    print("\n" + "="*60)
    print("Pipeline Complete!")
    print("="*60)
```

### `scripts/clustering_analysis.py`

```python
"""
Clustering analysis example with multiple algorithms, evaluation, and visualization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, davies_bouldin_score
)
import warnings
warnings.filterwarnings('ignore')


def preprocess_for_clustering(X, scale=True, pca_components=None):
    """
    Preprocess data for clustering.

    Parameters:
    -----------
    X : array-like
        Feature matrix
    scale : bool
        Whether to standardize features
    pca_components : int or None
        Number of PCA components (None to skip PCA)

    Returns:
    --------
    array
        Preprocessed data
    """
    X_processed = X.copy()

    if scale:
        scaler = StandardScaler()
        X_processed = scaler.fit_transform(X_processed)

    if pca_components is not None:
        pca = PCA(n_components=pca_components)
        X_processed = pca.fit_transform(X_processed)
        print(f"PCA: Explained variance ratio = {pca.explained_variance_ratio_.sum():.3f}")

    return X_processed


def find_optimal_k_kmeans(X, k_range=range(2, 11)):
    """
    Find optimal K for K-Means using elbow method and silhouette score.

    Parameters:
    -----------
    X : array-like
        Feature matrix (should be scaled)
    k_range : range
        Range of K values to test

    Returns:
    --------
    dict
        Dictionary with inertia and silhouette scores for each K
    """
    inertias = []
    silhouette_scores = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)

        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X, labels))

    # Plot results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    # Elbow plot
    ax1.plot(k_range, inertias, 'bo-')
    ax1.set_xlabel('Number of clusters (K)')
    ax1.set_ylabel('Inertia')
    ax1.set_title('Elbow Method')
    ax1.grid(True)

    # Silhouette plot
    ax2.plot(k_range, silhouette_scores, 'ro-')
    ax2.set_xlabel('Number of clusters (K)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Analysis')
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig('clustering_optimization.png', dpi=300, bbox_inches='tight')
    print("Saved: clustering_optimization.png")
    plt.close()

    # Find best K based on silhouette score
    best_k = k_range[np.argmax(silhouette_scores)]
    print(f"\nRecommended K based on silhouette score: {best_k}")

    return {
        'k_values': list(k_range),
        'inertias': inertias,
        'silhouette_scores': silhouette_scores,
        'best_k': best_k
    }


def compare_clustering_algorithms(X, n_clusters=3):
    """
    Compare different clustering algorithms.

    Parameters:
    -----------
    X : array-like
        Feature matrix (should be scaled)
    n_clusters : int
        Number of clusters

    Returns:
    --------
    dict
        Dictionary with results for each algorithm
    """
    print("="*60)
    print(f"Comparing Clustering Algorithms (n_clusters={n_clusters})")
    print("="*60)

    algorithms = {
        'K-Means': KMeans(n_clusters=n_clusters, random_state=42, n_init=10),
        'Agglomerative': AgglomerativeClustering(n_clusters=n_clusters, linkage='ward'),
        'Gaussian Mixture': GaussianMixture(n_components=n_clusters, random_state=42)
    }

    # DBSCAN doesn't require n_clusters
    # We'll add it separately
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    dbscan_labels = dbscan.fit_predict(X)

    results = {}

    for name, algorithm in algorithms.items():
        labels = algorithm.fit_predict(X)

        # Calculate metrics
        silhouette = silhouette_score(X, labels)
        calinski = calinski_harabasz_score(X, labels)
        davies = davies_bouldin_score(X, labels)

        results[name] = {
            'labels': labels,
            'n_clusters': n_clusters,
            'silhouette': silhouette,
            'calinski_harabasz': calinski,
            'davies_bouldin': davies
        }

        print(f"\n{name}:")
        print(f"  Silhouette Score:       {silhouette:.4f} (higher is better)")
        print(f"  Calinski-Harabasz:      {calinski:.4f} (higher is better)")
        print(f"  Davies-Bouldin:         {davies:.4f} (lower is better)")

    # DBSCAN results
    n_clusters_dbscan = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
    n_noise = list(dbscan_labels).count(-1)

    if n_clusters_dbscan > 1:
        # Only calculate metrics if we have multiple clusters
        mask = dbscan_labels != -1  # Exclude noise
        if mask.sum() > 0:
            silhouette = silhouette_score(X[mask], dbscan_labels[mask])
            calinski = calinski_harabasz_score(X[mask], dbscan_labels[mask])
            davies = davies_bouldin_score(X[mask], dbscan_labels[mask])

            results['DBSCAN'] = {
                'labels': dbscan_labels,
                'n_clusters': n_clusters_dbscan,
                'n_noise': n_noise,
                'silhouette': silhouette,
                'calinski_harabasz': calinski,
                'davies_bouldin': davies
            }

            print(f"\nDBSCAN:")
            print(f"  Clusters found:         {n_clusters_dbscan}")
            print(f"  Noise points:           {n_noise}")
            print(f"  Silhouette Score:       {silhouette:.4f} (higher is better)")
            print(f"  Calinski-Harabasz:      {calinski:.4f} (higher is better)")
            print(f"  Davies-Bouldin:         {davies:.4f} (lower is better)")
    else:
        print(f"\nDBSCAN:")
        print(f"  Clusters found:         {n_clusters_dbscan}")
        print(f"  Noise points:           {n_noise}")
        print("  Note: Insufficient clusters for metric calculation")

    return results


def visualize_clusters(X, results, true_labels=None):
    """
    Visualize clustering results using PCA for 2D projection.

    Parameters:
    -----------
    X : array-like
        Feature matrix
    results : dict
        Dictionary with clustering results
    true_labels : array-like or None
        True labels (if available) for comparison
    """
    # Reduce to 2D using PCA
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)

    # Determine number of subplots
    n_plots = len(results)
    if true_labels is not None:
        n_plots += 1

    n_cols = min(3, n_plots)
    n_rows = (n_plots + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
    if n_plots == 1:
        axes = np.array([axes])
    axes = axes.flatten()

    plot_idx = 0

    # Plot true labels if available
    if true_labels is not None:
        ax = axes[plot_idx]
        scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=true_labels, cmap='viridis', alpha=0.6)
        ax.set_title('True Labels')
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
        plt.colorbar(scatter, ax=ax)
        plot_idx += 1

    # Plot clustering results
    for name, result in results.items():
        ax = axes[plot_idx]
        labels = result['labels']

        scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='viridis', alpha=0.6)

        # Highlight noise points for DBSCAN
        if name == 'DBSCAN' and -1 in labels:
            noise_mask = labels == -1
            ax.scatter(X_2d[noise_mask, 0], X_2d[noise_mask, 1],
                      c='red', marker='x', s=100, label='Noise', alpha=0.8)
            ax.legend()

        title = f"{name} (K={result['n_clusters']})"
        if 'silhouette' in result:
            title += f"\nSilhouette: {result['silhouette']:.3f}"
        ax.set_title(title)
        ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
        ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
        plt.colorbar(scatter, ax=ax)

        plot_idx += 1

    # Hide unused subplots
    for idx in range(plot_idx, len(axes)):
        axes[idx].axis('off')

    plt.tight_layout()
    plt.savefig('clustering_results.png', dpi=300, bbox_inches='tight')
    print("\nSaved: clustering_results.png")
    plt.close()


def complete_clustering_analysis(X, true_labels=None, scale=True,
                                 find_k=True, k_range=range(2, 11), n_clusters=3):
    """
    Complete clustering analysis workflow.

    Parameters:
    -----------
    X : array-like
        Feature matrix
    true_labels : array-like or None
        True labels (for comparison only, not used in clustering)
    scale : bool
        Whether to scale features
    find_k : bool
        Whether to search for optimal K
    k_range : range
        Range of K values to test
    n_clusters : int
        Number of clusters to use in comparison

    Returns:
    --------
    dict
        Dictionary with all analysis results
    """
    print("="*60)
    print("Clustering Analysis")
    print("="*60)
    print(f"Data shape: {X.shape}")

    # Preprocess data
    X_processed = preprocess_for_clustering(X, scale=scale)

    # Find optimal K if requested
    optimization_results = None
    if find_k:
        print("\n" + "="*60)
        print("Finding Optimal Number of Clusters")
        print("="*60)
        optimization_results = find_optimal_k_kmeans(X_processed, k_range=k_range)

        # Use recommended K
        if optimization_results:
            n_clusters = optimization_results['best_k']

    # Compare clustering algorithms
    comparison_results = compare_clustering_algorithms(X_processed, n_clusters=n_clusters)

    # Visualize results
    print("\n" + "="*60)
    print("Visualizing Results")
    print("="*60)
    visualize_clusters(X_processed, comparison_results, true_labels=true_labels)

    return {
        'X_processed': X_processed,
        'optimization': optimization_results,
        'comparison': comparison_results
    }


# Example usage
if __name__ == "__main__":
    from sklearn.datasets import load_iris, make_blobs

    print("="*60)
    print("Example 1: Iris Dataset")
    print("="*60)

    # Load Iris dataset
    iris = load_iris()
    X_iris = iris.data
    y_iris = iris.target

    results_iris = complete_clustering_analysis(
        X_iris,
        true_labels=y_iris,
        scale=True,
        find_k=True,
        k_range=range(2, 8),
        n_clusters=3
    )

    print("\n" + "="*60)
    print("Example 2: Synthetic Dataset with Noise")
    print("="*60)

    # Create synthetic dataset
    X_synth, y_synth = make_blobs(
        n_samples=500, n_features=2, centers=4,
        cluster_std=0.5, random_state=42
    )

    # Add noise points
    noise = np.random.randn(50, 2) * 3
    X_synth = np.vstack([X_synth, noise])
    y_synth_with_noise = np.concatenate([y_synth, np.full(50, -1)])

    results_synth = complete_clustering_analysis(
        X_synth,
        true_labels=y_synth_with_noise,
        scale=True,
        find_k=True,
        k_range=range(2, 8),
        n_clusters=4
    )

    print("\n" + "="*60)
    print("Analysis Complete!")
    print("="*60)
```
