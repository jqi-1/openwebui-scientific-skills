---
name: deepchem
description: Molecular ML with diverse featurizers and pre-built datasets. Use for property prediction (ADMET, toxicity) with traditional ML or GNNs when you want extensive featurization options and MoleculeNet benchmarks. Best for quick experiments with pre-trained models, diverse molecular representations. For graph-first PyTorch workflows use torchdrug; for benchmark datasets use pytdc.
---

# DeepChem

## Overview

DeepChem is a comprehensive Python library for applying machine learning to chemistry, materials science, and biology. Enable molecular property prediction, drug discovery, materials design, and biomolecule analysis through specialized neural networks, molecular featurization methods, and pretrained models.

**Version note:** Examples target **deepchem 2.8.0** (PyPI stable, Apr 2024). Requires **Python 3.7–3.11** (`<3.12` on PyPI). Core utilities (loaders, featurizers, MoleculeNet) work without a DL backend; GNN and transformer models need the matching extra (`torch`, `tensorflow`, or `jax`). Install the backend framework first when using GPU builds.

## When to Use This Skill

This skill should be used when:
- Loading and processing molecular data (SMILES strings, SDF files, protein sequences)
- Predicting molecular properties (solubility, toxicity, binding affinity, ADMET properties)
- Training models on chemical/biological datasets
- Using MoleculeNet benchmark datasets (Tox21, BBBP, Delaney, etc.)
- Converting molecules to ML-ready features (fingerprints, graph representations, descriptors)
- Implementing graph neural networks for molecules (GCN, GAT, MPNN, AttentiveFP)
- Applying transfer learning with pretrained models (ChemBERTa, GROVER, MolFormer)
- Predicting crystal/materials properties (bandgap, formation energy)
- Analyzing protein or DNA sequences

## Core Capabilities

Eight capability areas, each with worked code, are in
[references/core_capabilities.md](references/core_capabilities.md):

1. **Molecular data loading and processing** — loaders, `NumpyDataset` / `DiskDataset`.
2. **Molecular featurization** — circular fingerprints, graph convolution, and descriptors.
3. **Data splitting** — random, scaffold, stratified, and butina splitters, and why
   scaffold splitting is the honest default for molecules.
4. **Model selection and training** — the model families and how to fit them.
5. **MoleculeNet benchmarks** — loading standard datasets and their published splits.
6. **Transfer learning** — pretraining and fine-tuning.
7. **Model evaluation** — metrics appropriate to regression and classification tasks.
8. **Making predictions** — applying a trained model to new molecules.

Three end-to-end workflows are in
[references/typical_workflows.md](references/typical_workflows.md).

## Example Scripts

This skill includes three production-ready scripts in the `scripts/` directory:

### 1. `predict_solubility.py`
Train and evaluate solubility prediction models. Works with Delaney benchmark or custom CSV data.

```bash
# Use Delaney benchmark
python scripts/predict_solubility.py

# Use custom data
python scripts/predict_solubility.py \
    --data my_data.csv \
    --smiles-col smiles \
    --target-col solubility \
    --predict "CCO" "c1ccccc1"
```

### 2. `graph_neural_network.py`
Train various graph neural network architectures on molecular data.

```bash
# Train GCN on Tox21
python scripts/graph_neural_network.py --model gcn --dataset tox21

# Train AttentiveFP on custom data
python scripts/graph_neural_network.py \
    --model attentivefp \
    --data molecules.csv \
    --task-type regression \
    --targets activity \
    --epochs 100
```

### 3. `transfer_learning.py`
Fine-tune pretrained models (ChemBERTa, GROVER, MolFormer) on molecular property prediction tasks.

```bash
# Fine-tune ChemBERTa on BBBP
python scripts/transfer_learning.py --model chemberta --dataset bbbp

# Fine-tune GROVER on custom data
python scripts/transfer_learning.py \
    --model grover \
    --data small_dataset.csv \
    --target activity \
    --task-type classification \
    --epochs 20
```

## Common Patterns and Best Practices

### Pattern 1: Always Use Scaffold Splitting for Molecules
```python
# GOOD: Prevents data leakage
splitter = dc.splits.ScaffoldSplitter()
train, test = splitter.train_test_split(dataset)

# BAD: Similar molecules in train and test
splitter = dc.splits.RandomSplitter()
train, test = splitter.train_test_split(dataset)
```

### Pattern 2: Normalize Features and Targets
```python
transformers = [
    dc.trans.NormalizationTransformer(
        transform_y=True,  # Also normalize target values
        dataset=train
    )
]
for transformer in transformers:
    train = transformer.transform(train)
    test = transformer.transform(test)
```

### Pattern 3: Start Simple, Then Scale
1. Start with Random Forest + CircularFingerprint (fast baseline)
2. Try XGBoost/LightGBM if RF works well
3. Move to deep learning (MultitaskRegressor) if you have >5K samples
4. Try GNNs if you have >10K samples
5. Use transfer learning for small datasets or novel scaffolds

### Pattern 4: Handle Imbalanced Data
```python
# Option 1: Balancing transformer
transformer = dc.trans.BalancingTransformer(dataset=train)
train = transformer.transform(train)

# Option 2: Use balanced metrics
metric = dc.metrics.Metric(dc.metrics.balanced_accuracy_score)
```

### Pattern 5: Avoid Memory Issues
```python
# Use DiskDataset for large datasets
dataset = dc.data.DiskDataset.from_numpy(X, y, w, ids)

# Use smaller batch sizes
model = dc.models.GCNModel(batch_size=32)  # Instead of 128
```

## Common Pitfalls

### Issue 1: Data Leakage in Drug Discovery
**Problem**: Using random splitting allows similar molecules in train/test sets.
**Solution**: Always use `ScaffoldSplitter` for molecular datasets.

### Issue 2: GNN Underperforming vs Fingerprints
**Problem**: Graph neural networks perform worse than simple fingerprints.
**Solutions**:
- Ensure dataset is large enough (>10K samples typically)
- Increase training epochs (50-100)
- Try different architectures (AttentiveFP, DMPNN instead of GCN)
- Use pretrained models (GROVER)

### Issue 3: Overfitting on Small Datasets
**Problem**: Model memorizes training data.
**Solutions**:
- Use stronger regularization (increase dropout to 0.5)
- Use simpler models (Random Forest instead of deep learning)
- Apply transfer learning (ChemBERTa, GROVER)
- Collect more data

### Issue 4: Import Errors
**Problem**: `No module named 'torch'` / `No module named 'tensorflow'` warnings, or model classes fail to import.
**Solution**: DeepChem loads lazily — install the backend that matches your model, then add the matching extra:
```bash
uv pip install deepchem              # loaders, featurizers, MoleculeNet only
uv pip install 'deepchem[torch]'       # GCN, GAT, AttentiveFP, HuggingFaceModel, GroverModel
uv pip install 'deepchem[tensorflow]'  # legacy Keras models
uv pip install 'deepchem[jax]'         # Haiku/JAX models
```
Install PyTorch or TensorFlow with the correct CUDA build **before** the extra when using GPUs. Quote extras in zsh: `'deepchem[torch]'`.

**Conda + PyTorch users:** If `import deepchem` fails with `undefined symbol: iJIT_NotifyEvent`, pin MKL below 2025 (`conda install "mkl<2025"`) — PyTorch wheels may be incompatible with MKL 2025.0.0.

## Reference Documentation

This skill includes comprehensive reference documentation:

### `references/api_reference.md`
Complete API documentation including:
- All data loaders and their use cases
- Dataset classes and when to use each
- Complete featurizer catalog with selection guide
- Model catalog organized by category (50+ models)
- MoleculeNet dataset descriptions
- Metrics and evaluation functions
- Common code patterns

**When to reference**: Search this file when you need specific API details, parameter names, or want to explore available options.

### `references/workflows.md`
Eight detailed end-to-end workflows:
1. Molecular property prediction from SMILES
2. Using MoleculeNet benchmarks
3. Hyperparameter optimization
4. Transfer learning with pretrained models
5. Molecular generation with GANs
6. Materials property prediction
7. Protein sequence analysis
8. Custom model integration

**When to reference**: Use these workflows as templates for implementing complete solutions.

## Installation

Core package (data loaders, featurizers, MoleculeNet, scikit-learn wrappers):

```bash
uv pip install deepchem
```

Add the extra that matches your model backend (install PyTorch/TensorFlow/JAX first for GPU builds):

```bash
uv pip install 'deepchem[torch]'       # GNNs, TorchModel, HuggingFaceModel, GroverModel
uv pip install 'deepchem[tensorflow]'  # Keras/TensorFlow models
uv pip install 'deepchem[jax]'         # JAX/Haiku models
uv pip install 'deepchem[dqc]'         # Differentiable quantum chemistry (torch + xitorch)
```

Nightly builds: `uv pip install --pre deepchem` (same extras apply with `--pre`).

See [installation guide](https://deepchem.readthedocs.io/en/latest/get_started/installation.html) and [soft requirements](https://deepchem.readthedocs.io/en/latest/requirements.html) for optional dependencies per model class.

## Additional Resources

- Official documentation: https://deepchem.readthedocs.io/
- GitHub repository: https://github.com/deepchem/deepchem
- Tutorials: https://deepchem.readthedocs.io/en/latest/get_started/tutorials.html
- Paper: "MoleculeNet: A Benchmark for Molecular Machine Learning"

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/deepchem/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_reference.md`

# DeepChem API Reference

This document provides a comprehensive reference for DeepChem's core APIs, organized by functionality.

## Data Handling

### Data Loaders

#### File Format Loaders
- **CSVLoader**: Load tabular data from CSV files with customizable feature handling
- **UserCSVLoader**: User-defined CSV loading with flexible column specifications
- **SDFLoader**: Process molecular structure files (SDF format)
- **JsonLoader**: Import JSON-structured datasets
- **ImageLoader**: Load image data for computer vision tasks

#### Biological Data Loaders
- **FASTALoader**: Handle protein/DNA sequences in FASTA format
- **FASTQLoader**: Process FASTQ sequencing data with quality scores
- **SAMLoader/BAMLoader/CRAMLoader**: Support sequence alignment formats

#### Specialized Loaders
- **DFTYamlLoader**: Process density functional theory computational data
- **InMemoryLoader**: Load data directly from Python objects

### Dataset Classes

- **NumpyDataset**: Wrap NumPy arrays for in-memory data manipulation
- **DiskDataset**: Manage larger datasets stored on disk, reducing memory overhead
- **ImageDataset**: Specialized container for image-based ML tasks

### Data Splitters

#### General Splitters
- **RandomSplitter**: Random dataset partitioning
- **IndexSplitter**: Split by specified indices
- **SpecifiedSplitter**: Use pre-defined splits
- **RandomStratifiedSplitter**: Stratified random splitting
- **SingletaskStratifiedSplitter**: Stratified splitting for single tasks
- **TaskSplitter**: Split for multitask scenarios

#### Molecule-Specific Splitters
- **ScaffoldSplitter**: Divide molecules by structural scaffolds (prevents data leakage)
- **ButinaSplitter**: Clustering-based molecular splitting
- **FingerprintSplitter**: Split based on molecular fingerprint similarity
- **MaxMinSplitter**: Maximize diversity between training/test sets
- **MolecularWeightSplitter**: Split by molecular weight properties

**Best Practice**: For drug discovery tasks, use ScaffoldSplitter to prevent overfitting on similar molecular structures.

### Transformers

#### Normalization
- **NormalizationTransformer**: Standard normalization (mean=0, std=1)
- **MinMaxTransformer**: Scale features to [0,1] range
- **LogTransformer**: Apply log transformation
- **PowerTransformer**: Box-Cox and Yeo-Johnson transformations
- **CDFTransformer**: Cumulative distribution function normalization

#### Task-Specific
- **BalancingTransformer**: Address class imbalance
- **FeaturizationTransformer**: Apply dynamic feature engineering
- **CoulombFitTransformer**: Quantum chemistry specific
- **DAGTransformer**: Directed acyclic graph transformations
- **RxnSplitTransformer**: Chemical reaction preprocessing

## Molecular Featurizers

### Graph-Based Featurizers
Use these with graph neural networks (GCNs, MPNNs, etc.):

- **ConvMolFeaturizer**: Graph representations for graph convolutional networks
- **WeaveFeaturizer**: "Weave" graph embeddings
- **MolGraphConvFeaturizer**: Graph convolution-ready representations
- **EquivariantGraphFeaturizer**: Maintains geometric invariance
- **DMPNNFeaturizer**: Directed message-passing neural network inputs
- **GroverFeaturizer**: Pre-trained molecular embeddings

### Fingerprint-Based Featurizers
Use these with traditional ML (Random Forest, SVM, XGBoost):

- **MACCSKeysFingerprint**: 167-bit structural keys
- **CircularFingerprint**: Extended connectivity fingerprints (Morgan fingerprints)
  - Parameters: `radius` (default 2), `size` (default 2048), `useChirality` (default False)
- **PubChemFingerprint**: 881-bit structural descriptors
- **Mol2VecFingerprint**: Learned molecular vector representations

### Descriptor Featurizers
Calculate molecular properties directly:

- **RDKitDescriptors**: ~200 molecular descriptors (MW, LogP, H-donors, H-acceptors, TPSA, etc.)
- **MordredDescriptors**: Comprehensive structural and physicochemical descriptors
- **CoulombMatrix**: Interatomic distance matrices for 3D structures

### Sequence-Based Featurizers
For recurrent networks and transformers:

- **SmilesToSeq**: Convert SMILES strings to sequences
- **SmilesToImage**: Generate 2D image representations from SMILES
- **RawFeaturizer**: Pass through raw molecular data unchanged

### Selection Guide

| Use Case | Recommended Featurizer | Model Type |
|----------|----------------------|------------|
| Graph neural networks | ConvMolFeaturizer, MolGraphConvFeaturizer | GCN, MPNN, GAT |
| Traditional ML | CircularFingerprint, RDKitDescriptors | Random Forest, XGBoost, SVM |
| Deep learning (non-graph) | CircularFingerprint, Mol2VecFingerprint | Dense networks, CNN |
| Sequence models | SmilesToSeq | LSTM, GRU, Transformer |
| 3D molecular structures | CoulombMatrix | Specialized 3D models |
| Quick baseline | RDKitDescriptors | Linear, Ridge, Lasso |

## Models

**Install note (2.8.0):** PyPI extras are `torch`, `tensorflow`, `jax`, and `dqc` — there is no `[all]` extra. Install PyTorch/TensorFlow/JAX before the matching `uv pip install 'deepchem[torch]'` (quote brackets in zsh).

### Scikit-Learn Integration
- **SklearnModel**: Wrapper for any scikit-learn algorithm
  - Usage: `SklearnModel(model=RandomForestRegressor())`

### Gradient Boosting
- **GBDTModel**: Gradient boosting decision trees (XGBoost, LightGBM)

### PyTorch Models

#### Molecular Property Prediction
- **MultitaskRegressor**: Multi-task regression with shared representations
- **MultitaskClassifier**: Multi-task classification
- **MultitaskFitTransformRegressor**: Regression with learned transformations
- **GCNModel**: Graph convolutional networks
- **GATModel**: Graph attention networks
- **AttentiveFPModel**: Attentive fingerprint networks
- **DMPNNModel**: Directed message passing neural networks
- **GroverModel**: GROVER pre-trained transformer
- **MATModel**: Molecule attention transformer

#### Materials Science
- **CGCNNModel**: Crystal graph convolutional networks
- **MEGNetModel**: Materials graph networks
- **LCNNModel**: Lattice CNN for materials

#### Generative Models
- **GANModel**: Generative adversarial networks
- **WGANModel**: Wasserstein GAN
- **BasicMolGANModel**: Molecular GAN
- **LSTMGenerator**: LSTM-based molecule generation
- **SeqToSeqModel**: Sequence-to-sequence models

#### Physics-Informed Models
- **PINNModel**: Physics-informed neural networks
- **HNNModel**: Hamiltonian neural networks
- **LNN**: Lagrangian neural networks
- **FNOModel**: Fourier neural operators

#### Computer Vision
- **CNN**: Convolutional neural networks
- **UNetModel**: U-Net architecture for segmentation
- **InceptionV3Model**: Pre-trained Inception v3
- **MobileNetV2Model**: Lightweight mobile networks

### Hugging Face Models

- **HuggingFaceModel**: General wrapper for HF transformers
- **Chemberta**: Chemical BERT for molecular property prediction
- **MoLFormer**: Molecular transformer architecture
- **ProtBERT**: Protein sequence BERT
- **DeepAbLLM**: Antibody large language models

### Model Selection Guide

| Task | Recommended Model | Featurizer |
|------|------------------|------------|
| Small dataset (<1000 samples) | SklearnModel (Random Forest) | CircularFingerprint |
| Medium dataset (1K-100K) | GBDTModel or MultitaskRegressor | CircularFingerprint or ConvMolFeaturizer |
| Large dataset (>100K) | GCNModel, AttentiveFPModel, or DMPNN | MolGraphConvFeaturizer |
| Transfer learning | GroverModel, Chemberta, MoLFormer | Model-specific |
| Materials properties | CGCNNModel, MEGNetModel | Structure-based |
| Molecule generation | BasicMolGANModel, LSTMGenerator | SmilesToSeq |
| Protein sequences | ProtBERT | Sequence-based |

## MoleculeNet Datasets

Quick access to 30+ benchmark datasets via `dc.molnet.load_*()` functions.

### Classification Datasets
- **load_bace()**: BACE-1 inhibitors (binary classification)
- **load_bbbp()**: Blood-brain barrier penetration
- **load_clintox()**: Clinical toxicity
- **load_hiv()**: HIV inhibition activity
- **load_muv()**: PubChem BioAssay (challenging, sparse)
- **load_pcba()**: PubChem screening data
- **load_sider()**: Adverse drug reactions (multi-label)
- **load_tox21()**: 12 toxicity assays (multi-task)
- **load_toxcast()**: EPA ToxCast screening

### Regression Datasets
- **load_delaney()**: Aqueous solubility (ESOL)
- **load_freesolv()**: Solvation free energy
- **load_lipo()**: Lipophilicity (octanol-water partition)
- **load_qm7/qm8/qm9()**: Quantum mechanical properties
- **load_hopv()**: Organic photovoltaic properties

### Protein-Ligand Binding
- **load_pdbbind()**: Binding affinity data

### Materials Science
- **load_perovskite()**: Perovskite stability
- **load_mp_formation_energy()**: Materials Project formation energy
- **load_mp_metallicity()**: Metal vs. non-metal classification
- **load_bandgap()**: Electronic bandgap prediction

### Chemical Reactions
- **load_uspto()**: USPTO reaction dataset

### Usage Pattern
```python
tasks, datasets, transformers = dc.molnet.load_bbbp(
    featurizer='GraphConv',  # or 'ECFP', 'GraphConv', 'Weave', etc.
    splitter='scaffold',      # or 'random', 'stratified', etc.
    reload=False              # set True to skip caching
)
train, valid, test = datasets
```

## Metrics

Common evaluation metrics available in `dc.metrics`:

### Classification Metrics
- **roc_auc_score**: Area under ROC curve (binary/multi-class)
- **prc_auc_score**: Area under precision-recall curve
- **accuracy_score**: Classification accuracy
- **balanced_accuracy_score**: Balanced accuracy for imbalanced datasets
- **recall_score**: Sensitivity/recall
- **precision_score**: Precision
- **f1_score**: F1 score

### Regression Metrics
- **mean_absolute_error**: MAE
- **mean_squared_error**: MSE
- **root_mean_squared_error**: RMSE
- **r2_score**: R² coefficient of determination
- **pearson_r2_score**: Pearson correlation
- **spearman_correlation**: Spearman rank correlation

### Multi-Task Metrics
Most metrics support multi-task evaluation by averaging over tasks.

## Training Pattern

Standard DeepChem workflow:

```python
# 1. Load data
loader = dc.data.CSVLoader(tasks=['task1'], feature_field='smiles',
                           featurizer=dc.feat.CircularFingerprint())
dataset = loader.create_dataset('data.csv')

# 2. Split data
splitter = dc.splits.ScaffoldSplitter()
train, valid, test = splitter.train_valid_test_split(dataset)

# 3. Transform data (optional)
transformers = [dc.trans.NormalizationTransformer(dataset=train)]
for transformer in transformers:
    train = transformer.transform(train)
    valid = transformer.transform(valid)
    test = transformer.transform(test)

# 4. Create and train model
model = dc.models.MultitaskRegressor(n_tasks=1, n_features=2048, layer_sizes=[1000])
model.fit(train, nb_epoch=50)

# 5. Evaluate
metric = dc.metrics.Metric(dc.metrics.r2_score)
train_score = model.evaluate(train, [metric])
test_score = model.evaluate(test, [metric])
```

## Common Patterns

### Pattern 1: Quick Baseline with MoleculeNet
```python
tasks, datasets, transformers = dc.molnet.load_tox21(featurizer='ECFP')
train, valid, test = datasets
model = dc.models.MultitaskClassifier(n_tasks=len(tasks), n_features=1024)
model.fit(train)
```

### Pattern 2: Custom Data with Graph Networks
```python
featurizer = dc.feat.MolGraphConvFeaturizer()
loader = dc.data.CSVLoader(tasks=['activity'], feature_field='smiles',
                           featurizer=featurizer)
dataset = loader.create_dataset('my_data.csv')
train, test = dc.splits.RandomSplitter().train_test_split(dataset)
model = dc.models.GCNModel(mode='classification', n_tasks=1)
model.fit(train)
```

### Pattern 3: Transfer Learning with Pretrained Models
```python
model = dc.models.GroverModel(task='classification', n_tasks=1)
model.fit(train_dataset)
predictions = model.predict(test_dataset)
```

### `references/core_capabilities.md`

# DeepChem Core Capabilities

Molecular data loading and processing, featurization, data splitting, model selection and
training, MoleculeNet benchmarks, transfer learning, evaluation, and prediction.

## Core Capabilities

### 1. Molecular Data Loading and Processing

DeepChem provides specialized loaders for various chemical data formats:

```python
import deepchem as dc

# Load CSV with SMILES
featurizer = dc.feat.CircularFingerprint(radius=2, size=2048)
loader = dc.data.CSVLoader(
    tasks=['solubility', 'toxicity'],
    feature_field='smiles',
    featurizer=featurizer
)
dataset = loader.create_dataset('molecules.csv')

# Load SDF files
loader = dc.data.SDFLoader(tasks=['activity'], featurizer=featurizer)
dataset = loader.create_dataset('compounds.sdf')

# Load protein sequences
loader = dc.data.FASTALoader()
dataset = loader.create_dataset('proteins.fasta')
```

**Key Loaders**:
- `CSVLoader`: Tabular data with molecular identifiers
- `SDFLoader`: Molecular structure files
- `FASTALoader`: Protein/DNA sequences
- `ImageLoader`: Molecular images
- `JsonLoader`: JSON-formatted datasets

### 2. Molecular Featurization

Convert molecules into numerical representations for ML models.

#### Decision Tree for Featurizer Selection

```
Is the model a graph neural network?
├─ YES → Use graph featurizers
│   ├─ Standard GNN → MolGraphConvFeaturizer
│   ├─ Message passing → DMPNNFeaturizer
│   └─ Pretrained → GroverFeaturizer
│
└─ NO → What type of model?
    ├─ Traditional ML (RF, XGBoost, SVM)
    │   ├─ Fast baseline → CircularFingerprint (ECFP)
    │   ├─ Interpretable → RDKitDescriptors
    │   └─ Maximum coverage → MordredDescriptors
    │
    ├─ Deep learning (non-graph)
    │   ├─ Dense networks → CircularFingerprint
    │   └─ CNN → SmilesToImage
    │
    ├─ Sequence models (LSTM, Transformer)
    │   └─ SmilesToSeq
    │
    └─ 3D structure analysis
        └─ CoulombMatrix
```

#### Example Featurization

```python
# Fingerprints (for traditional ML)
fp = dc.feat.CircularFingerprint(radius=2, size=2048)

# Descriptors (for interpretable models)
desc = dc.feat.RDKitDescriptors()

# Graph features (for GNNs)
graph_feat = dc.feat.MolGraphConvFeaturizer()

# Apply featurization
features = fp.featurize(['CCO', 'c1ccccc1'])
```

**Selection Guide**:
- **Small datasets (<1K)**: CircularFingerprint or RDKitDescriptors
- **Medium datasets (1K-100K)**: CircularFingerprint or graph featurizers
- **Large datasets (>100K)**: Graph featurizers (MolGraphConvFeaturizer, DMPNNFeaturizer)
- **Transfer learning**: Pretrained model featurizers (GroverFeaturizer)

See `references/api_reference.md` for complete featurizer documentation.

### 3. Data Splitting

**Critical**: For drug discovery tasks, use `ScaffoldSplitter` to prevent data leakage from similar molecular structures appearing in both training and test sets.

```python
# Scaffold splitting (recommended for molecules)
splitter = dc.splits.ScaffoldSplitter()
train, valid, test = splitter.train_valid_test_split(
    dataset,
    frac_train=0.8,
    frac_valid=0.1,
    frac_test=0.1
)

# Random splitting (for non-molecular data)
splitter = dc.splits.RandomSplitter()
train, test = splitter.train_test_split(dataset)

# Stratified splitting (for imbalanced classification)
splitter = dc.splits.RandomStratifiedSplitter()
train, test = splitter.train_test_split(dataset)
```

**Available Splitters**:
- `ScaffoldSplitter`: Split by molecular scaffolds (prevents leakage)
- `ButinaSplitter`: Clustering-based molecular splitting
- `MaxMinSplitter`: Maximize diversity between sets
- `RandomSplitter`: Random splitting
- `RandomStratifiedSplitter`: Preserves class distributions

### 4. Model Selection and Training

#### Quick Model Selection Guide

| Dataset Size | Task | Recommended Model | Featurizer |
|-------------|------|-------------------|------------|
| < 1K samples | Any | SklearnModel (RandomForest) | CircularFingerprint |
| 1K-100K | Classification/Regression | GBDTModel or MultitaskRegressor | CircularFingerprint |
| > 100K | Molecular properties | GCNModel, AttentiveFPModel, DMPNNModel | MolGraphConvFeaturizer |
| Any (small preferred) | Transfer learning | ChemBERTa, GROVER, MolFormer | Model-specific |
| Crystal structures | Materials properties | CGCNNModel, MEGNetModel | Structure-based |
| Protein sequences | Protein properties | ProtBERT | Sequence-based |

#### Example: Traditional ML
```python
from sklearn.ensemble import RandomForestRegressor

# Wrap scikit-learn model
sklearn_model = RandomForestRegressor(n_estimators=100)
model = dc.models.SklearnModel(model=sklearn_model)
model.fit(train)
```

#### Example: Deep Learning
```python
# Multitask regressor (for fingerprints)
model = dc.models.MultitaskRegressor(
    n_tasks=2,
    n_features=2048,
    layer_sizes=[1000, 500],
    dropouts=0.25,
    learning_rate=0.001
)
model.fit(train, nb_epoch=50)
```

#### Example: Graph Neural Networks
```python
# Graph Convolutional Network
model = dc.models.GCNModel(
    n_tasks=1,
    mode='regression',
    batch_size=128,
    learning_rate=0.001
)
model.fit(train, nb_epoch=50)

# Graph Attention Network
model = dc.models.GATModel(n_tasks=1, mode='classification')
model.fit(train, nb_epoch=50)

# Attentive Fingerprint
model = dc.models.AttentiveFPModel(n_tasks=1, mode='regression')
model.fit(train, nb_epoch=50)
```

### 5. MoleculeNet Benchmarks

Quick access to 30+ curated benchmark datasets with standardized train/valid/test splits:

```python
# Load benchmark dataset
tasks, datasets, transformers = dc.molnet.load_tox21(
    featurizer='GraphConv',  # or 'ECFP', 'Weave', 'Raw'
    splitter='scaffold',     # or 'random', 'stratified'
    reload=False
)
train, valid, test = datasets

# Train and evaluate
model = dc.models.GCNModel(n_tasks=len(tasks), mode='classification')
model.fit(train, nb_epoch=50)

metric = dc.metrics.Metric(dc.metrics.roc_auc_score)
test_score = model.evaluate(test, [metric])
```

**Common Datasets**:
- **Classification**: `load_tox21()`, `load_bbbp()`, `load_hiv()`, `load_clintox()`
- **Regression**: `load_delaney()`, `load_freesolv()`, `load_lipo()`
- **Quantum properties**: `load_qm7()`, `load_qm8()`, `load_qm9()`
- **Materials**: `load_perovskite()`, `load_bandgap()`, `load_mp_formation_energy()`

See `references/api_reference.md` for complete dataset list.

### 6. Transfer Learning

Leverage pretrained models for improved performance, especially on small datasets:

```python
# ChemBERTa (BERT pretrained on 77M molecules)
model = dc.models.HuggingFaceModel(
    model='seyonec/ChemBERTa-zinc-base-v1',
    task='classification',
    n_tasks=1,
    learning_rate=2e-5  # Lower LR for fine-tuning
)
model.fit(train, nb_epoch=10)

# GROVER (graph transformer pretrained on 10M molecules)
model = dc.models.GroverModel(
    task='regression',
    n_tasks=1
)
model.fit(train, nb_epoch=20)
```

**When to use transfer learning**:
- Small datasets (< 1000 samples)
- Novel molecular scaffolds
- Limited computational resources
- Need for rapid prototyping

Use the `scripts/transfer_learning.py` script for guided transfer learning workflows.

### 7. Model Evaluation

```python
# Define metrics
classification_metrics = [
    dc.metrics.Metric(dc.metrics.roc_auc_score, name='ROC-AUC'),
    dc.metrics.Metric(dc.metrics.accuracy_score, name='Accuracy'),
    dc.metrics.Metric(dc.metrics.f1_score, name='F1')
]

regression_metrics = [
    dc.metrics.Metric(dc.metrics.r2_score, name='R²'),
    dc.metrics.Metric(dc.metrics.mean_absolute_error, name='MAE'),
    dc.metrics.Metric(dc.metrics.root_mean_squared_error, name='RMSE')
]

# Evaluate
train_scores = model.evaluate(train, classification_metrics)
test_scores = model.evaluate(test, classification_metrics)
```

### 8. Making Predictions

```python
# Predict on test set
predictions = model.predict(test)

# Predict on new molecules
new_smiles = ['CCO', 'c1ccccc1', 'CC(C)O']
new_features = featurizer.featurize(new_smiles)
new_dataset = dc.data.NumpyDataset(X=new_features)

# Untransform the output, not the input. A NormalizationTransformer built with
# transform_y=True touches y, and a prediction dataset has no y -- transforming
# it does nothing, and the predictions come back in z-scored space. Passing the
# transformers to predict() untransforms them into the target's real units.
predictions = model.predict(new_dataset, transformers=transformers)
```

### `references/typical_workflows.md`

# Typical Workflows

Three end-to-end workflows: quick benchmark evaluation, prediction on custom data, and
transfer learning on a small dataset.

## Typical Workflows

### Workflow A: Quick Benchmark Evaluation

For evaluating a model on standard benchmarks:

```python
import deepchem as dc

# 1. Load benchmark
tasks, datasets, _ = dc.molnet.load_bbbp(
    featurizer='GraphConv',
    splitter='scaffold'
)
train, valid, test = datasets

# 2. Train model
model = dc.models.GCNModel(n_tasks=len(tasks), mode='classification')
model.fit(train, nb_epoch=50)

# 3. Evaluate
metric = dc.metrics.Metric(dc.metrics.roc_auc_score)
test_score = model.evaluate(test, [metric])
print(f"Test ROC-AUC: {test_score}")
```

### Workflow B: Custom Data Prediction

For training on custom molecular datasets:

```python
import deepchem as dc

# 1. Load and featurize data
featurizer = dc.feat.CircularFingerprint(radius=2, size=2048)
loader = dc.data.CSVLoader(
    tasks=['activity'],
    feature_field='smiles',
    featurizer=featurizer
)
dataset = loader.create_dataset('my_molecules.csv')

# 2. Split data (use ScaffoldSplitter for molecules!)
splitter = dc.splits.ScaffoldSplitter()
train, valid, test = splitter.train_valid_test_split(dataset)

# 3. Normalize (optional but recommended)
transformers = [dc.trans.NormalizationTransformer(
    transform_y=True, dataset=train
)]
for transformer in transformers:
    train = transformer.transform(train)
    valid = transformer.transform(valid)
    test = transformer.transform(test)

# 4. Train model
model = dc.models.MultitaskRegressor(
    n_tasks=1,
    n_features=2048,
    layer_sizes=[1000, 500],
    dropouts=0.25
)
model.fit(train, nb_epoch=50)

# 5. Evaluate
metric = dc.metrics.Metric(dc.metrics.r2_score)
test_score = model.evaluate(test, [metric])
```

### Workflow C: Transfer Learning on Small Dataset

For leveraging pretrained models:

```python
import deepchem as dc

# 1. Load data (pretrained models often need raw SMILES)
loader = dc.data.CSVLoader(
    tasks=['activity'],
    feature_field='smiles',
    featurizer=dc.feat.DummyFeaturizer()  # Model handles featurization
)
dataset = loader.create_dataset('small_dataset.csv')

# 2. Split data
splitter = dc.splits.ScaffoldSplitter()
train, test = splitter.train_test_split(dataset)

# 3. Load pretrained model
model = dc.models.HuggingFaceModel(
    model='seyonec/ChemBERTa-zinc-base-v1',
    task='classification',
    n_tasks=1,
    learning_rate=2e-5
)

# 4. Fine-tune
model.fit(train, nb_epoch=10)

# 5. Evaluate
predictions = model.predict(test)
```

See `references/workflows.md` for 8 detailed workflow examples covering molecular generation, materials science, protein analysis, and more.

### `references/workflows.md`

# DeepChem Workflows

This document provides detailed workflows for common DeepChem use cases.

## Workflow 1: Molecular Property Prediction from SMILES

**Goal**: Predict molecular properties (e.g., solubility, toxicity, activity) from SMILES strings.

### Step-by-Step Process

#### 1. Prepare Your Data
Data should be in CSV format with at minimum:
- A column with SMILES strings
- One or more columns with property values (targets)

Example CSV structure:
```csv
smiles,solubility,toxicity
CCO,-0.77,0
CC(=O)OC1=CC=CC=C1C(=O)O,-1.19,1
```

#### 2. Choose Featurizer
Decision tree:
- **Small dataset (<1K)**: Use `CircularFingerprint` or `RDKitDescriptors`
- **Medium dataset (1K-100K)**: Use `CircularFingerprint` or `MolGraphConvFeaturizer`
- **Large dataset (>100K)**: Use graph-based featurizers (`MolGraphConvFeaturizer`, `DMPNNFeaturizer`)
- **Transfer learning**: Use pretrained model featurizers (`GroverFeaturizer`)

#### 3. Load and Featurize Data
```python
import deepchem as dc

# For fingerprint-based
featurizer = dc.feat.CircularFingerprint(radius=2, size=2048)
# OR for graph-based
featurizer = dc.feat.MolGraphConvFeaturizer()

loader = dc.data.CSVLoader(
    tasks=['solubility', 'toxicity'],  # column names to predict
    feature_field='smiles',             # column with SMILES
    featurizer=featurizer
)
dataset = loader.create_dataset('data.csv')
```

#### 4. Split Data
**Critical**: Use `ScaffoldSplitter` for drug discovery to prevent data leakage.

```python
splitter = dc.splits.ScaffoldSplitter()
train, valid, test = splitter.train_valid_test_split(
    dataset,
    frac_train=0.8,
    frac_valid=0.1,
    frac_test=0.1
)
```

#### 5. Transform Data (Optional but Recommended)
```python
transformers = [
    dc.trans.NormalizationTransformer(
        transform_y=True,
        dataset=train
    )
]

for transformer in transformers:
    train = transformer.transform(train)
    valid = transformer.transform(valid)
    test = transformer.transform(test)
```

#### 6. Select and Train Model
```python
# For fingerprints
model = dc.models.MultitaskRegressor(
    n_tasks=2,                    # number of properties to predict
    n_features=2048,              # fingerprint size
    layer_sizes=[1000, 500],      # hidden layer sizes
    dropouts=0.25,
    learning_rate=0.001
)

# OR for graphs
model = dc.models.GCNModel(
    n_tasks=2,
    mode='regression',
    batch_size=128,
    learning_rate=0.001
)

# Train
model.fit(train, nb_epoch=50)
```

#### 7. Evaluate
```python
metric = dc.metrics.Metric(dc.metrics.r2_score)
train_score = model.evaluate(train, [metric])
valid_score = model.evaluate(valid, [metric])
test_score = model.evaluate(test, [metric])

print(f"Train R²: {train_score}")
print(f"Valid R²: {valid_score}")
print(f"Test R²: {test_score}")
```

#### 8. Make Predictions
```python
# Predict on new molecules
new_smiles = ['CCO', 'CC(C)O', 'c1ccccc1']
new_featurizer = dc.feat.CircularFingerprint(radius=2, size=2048)
new_features = new_featurizer.featurize(new_smiles)
new_dataset = dc.data.NumpyDataset(X=new_features)

# Untransform the output, not the input. A NormalizationTransformer built with
# transform_y=True touches y, and a prediction dataset has no y -- transforming
# it does nothing, and the predictions come back in z-scored space. Passing the
# transformers to predict() untransforms them into the target's real units.
predictions = model.predict(new_dataset, transformers=transformers)
```

---

## Workflow 2: Using MoleculeNet Benchmark Datasets

**Goal**: Quickly train and evaluate models on standard benchmarks.

### Quick Start
```python
import deepchem as dc

# Load benchmark dataset
tasks, datasets, transformers = dc.molnet.load_tox21(
    featurizer='GraphConv',
    splitter='scaffold'
)
train, valid, test = datasets

# Train model
model = dc.models.GCNModel(
    n_tasks=len(tasks),
    mode='classification'
)
model.fit(train, nb_epoch=50)

# Evaluate
metric = dc.metrics.Metric(dc.metrics.roc_auc_score)
test_score = model.evaluate(test, [metric])
print(f"Test ROC-AUC: {test_score}")
```

### Available Featurizer Options
When calling `load_*()` functions:
- `'ECFP'`: Extended-connectivity fingerprints (circular fingerprints)
- `'GraphConv'`: Graph convolution features
- `'Weave'`: Weave features
- `'Raw'`: Raw SMILES strings
- `'smiles2img'`: 2D molecular images

### Available Splitter Options
- `'scaffold'`: Scaffold-based splitting (recommended for drug discovery)
- `'random'`: Random splitting
- `'stratified'`: Stratified splitting (preserves class distributions)
- `'butina'`: Butina clustering-based splitting

---

## Workflow 3: Hyperparameter Optimization

**Goal**: Find optimal model hyperparameters systematically.

### Using GridHyperparamOpt
```python
import deepchem as dc
import numpy as np

# Load data
tasks, datasets, transformers = dc.molnet.load_bbbp(
    featurizer='ECFP',
    splitter='scaffold'
)
train, valid, test = datasets

# Define parameter grid
params_dict = {
    'layer_sizes': [[1000], [1000, 500], [1000, 1000]],
    'dropouts': [0.0, 0.25, 0.5],
    'learning_rate': [0.001, 0.0001]
}

# Define model builder function
def model_builder(model_params, model_dir):
    return dc.models.MultitaskClassifier(
        n_tasks=len(tasks),
        n_features=1024,
        **model_params
    )

# Setup optimizer
metric = dc.metrics.Metric(dc.metrics.roc_auc_score)
optimizer = dc.hyper.GridHyperparamOpt(model_builder)

# Run optimization
best_model, best_params, all_results = optimizer.hyperparam_search(
    params_dict,
    train,
    valid,
    metric,
    transformers=transformers
)

print(f"Best parameters: {best_params}")
print(f"Best validation score: {all_results['best_validation_score']}")
```

---

## Workflow 4: Transfer Learning with Pretrained Models

**Goal**: Leverage pretrained models for improved performance on small datasets.

### Using ChemBERTa
```python
import deepchem as dc
from transformers import AutoTokenizer

# Load your data
loader = dc.data.CSVLoader(
    tasks=['activity'],
    feature_field='smiles',
    featurizer=dc.feat.DummyFeaturizer()  # ChemBERTa handles featurization
)
dataset = loader.create_dataset('data.csv')

# Split data
splitter = dc.splits.ScaffoldSplitter()
train, test = splitter.train_test_split(dataset)

# Load pretrained ChemBERTa
model = dc.models.HuggingFaceModel(
    model='seyonec/ChemBERTa-zinc-base-v1',
    task='regression',
    n_tasks=1
)

# Fine-tune
model.fit(train, nb_epoch=10)

# Evaluate
predictions = model.predict(test)
```

### Using GROVER
```python
# GROVER: pre-trained on molecular graphs
model = dc.models.GroverModel(
    task='classification',
    n_tasks=1,
    model_dir='./grover_model'
)

# Fine-tune on your data
model.fit(train_dataset, nb_epoch=20)
```

---

## Workflow 5: Molecular Generation with GANs

**Goal**: Generate novel molecules with desired properties.

### Basic MolGAN
```python
import deepchem as dc

# Load training data (molecules for the generator to learn from)
tasks, datasets, _ = dc.molnet.load_qm9(
    featurizer='GraphConv',
    splitter='random'
)
train, _, _ = datasets

# Create and train MolGAN
gan = dc.models.BasicMolGANModel(
    learning_rate=0.001,
    vertices=9,  # max atoms in molecule
    edges=5,     # max bonds
    nodes=[128, 256, 512]
)

# Train
gan.fit_gan(
    train,
    nb_epoch=100,
    generator_steps=0.2,
    checkpoint_interval=10
)

# Generate new molecules
generated_molecules = gan.predict_gan_generator(1000)
```

### Conditional Generation
```python
# For property-targeted generation
from deepchem.models.optimizers import ExponentialDecay

gan = dc.models.BasicMolGANModel(
    learning_rate=ExponentialDecay(0.001, 0.9, 1000),
    conditional=True  # enable conditional generation
)

# Train with properties
gan.fit_gan(train, nb_epoch=100)

# Generate molecules with target properties
target_properties = np.array([[5.0, 300.0]])  # e.g., [logP, MW]
molecules = gan.predict_gan_generator(
    1000,
    conditional_inputs=target_properties
)
```

---

## Workflow 6: Materials Property Prediction

**Goal**: Predict properties of crystalline materials.

### Using Crystal Graph Convolutional Networks
```python
import deepchem as dc

# Load materials data (structure files in CIF format)
loader = dc.data.CIFLoader()
dataset = loader.create_dataset('materials.csv')

# Split data
splitter = dc.splits.RandomSplitter()
train, test = splitter.train_test_split(dataset)

# Create CGCNN model
model = dc.models.CGCNNModel(
    n_tasks=1,
    mode='regression',
    batch_size=32,
    learning_rate=0.001
)

# Train
model.fit(train, nb_epoch=100)

# Evaluate
metric = dc.metrics.Metric(dc.metrics.mae_score)
test_score = model.evaluate(test, [metric])
```

---

## Workflow 7: Protein Sequence Analysis

**Goal**: Predict protein properties from sequences.

### Using ProtBERT
```python
import deepchem as dc

# Load protein sequence data
loader = dc.data.FASTALoader()
dataset = loader.create_dataset('proteins.fasta')

# Use ProtBERT
model = dc.models.HuggingFaceModel(
    model='Rostlab/prot_bert',
    task='classification',
    n_tasks=1
)

# Split and train
splitter = dc.splits.RandomSplitter()
train, test = splitter.train_test_split(dataset)
model.fit(train, nb_epoch=5)

# Predict
predictions = model.predict(test)
```

---

## Workflow 8: Custom Model Integration

**Goal**: Use your own PyTorch/scikit-learn models with DeepChem.

### Wrapping Scikit-Learn Models
```python
from sklearn.ensemble import RandomForestRegressor
import deepchem as dc

# Create scikit-learn model
sklearn_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    random_state=42
)

# Wrap in DeepChem
model = dc.models.SklearnModel(model=sklearn_model)

# Use with DeepChem datasets
model.fit(train)
predictions = model.predict(test)

# Evaluate
metric = dc.metrics.Metric(dc.metrics.r2_score)
score = model.evaluate(test, [metric])
```

### Creating Custom PyTorch Models
```python
import torch
import torch.nn as nn
import deepchem as dc

class CustomNetwork(nn.Module):
    def __init__(self, n_features, n_tasks):
        super().__init__()
        self.fc1 = nn.Linear(n_features, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, n_tasks)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        return self.fc3(x)

# Wrap in DeepChem TorchModel
model = dc.models.TorchModel(
    model=CustomNetwork(n_features=2048, n_tasks=1),
    loss=nn.MSELoss(),
    output_types=['prediction']
)

# Train
model.fit(train, nb_epoch=50)
```

---

## Common Pitfalls and Solutions

### Issue 1: Data Leakage in Drug Discovery
**Problem**: Using random splitting allows similar molecules in train and test sets.
**Solution**: Always use `ScaffoldSplitter` for molecular datasets.

### Issue 2: Imbalanced Classification
**Problem**: Poor performance on minority class.
**Solution**: Use `BalancingTransformer` or weighted metrics.
```python
transformer = dc.trans.BalancingTransformer(dataset=train)
train = transformer.transform(train)
```

### Issue 3: Memory Issues with Large Datasets
**Problem**: Dataset doesn't fit in memory.
**Solution**: Use `DiskDataset` instead of `NumpyDataset`.
```python
dataset = dc.data.DiskDataset.from_numpy(X, y, w, ids)
```

### Issue 4: Overfitting on Small Datasets
**Problem**: Model memorizes training data.
**Solutions**:
1. Use stronger regularization (increase dropout)
2. Use simpler models (Random Forest, Ridge)
3. Apply transfer learning (pretrained models)
4. Collect more data

### Issue 5: Poor Graph Neural Network Performance
**Problem**: GNN performs worse than fingerprints.
**Solutions**:
1. Check if dataset is large enough (GNNs need >10K samples typically)
2. Increase training epochs
3. Try different GNN architectures (AttentiveFP, DMPNN)
4. Use pretrained models (GROVER)

### `scripts/graph_neural_network.py`

```python
#!/usr/bin/env python3
"""
Graph Neural Network Training Script

This script demonstrates training Graph Convolutional Networks (GCNs) and other
graph-based models for molecular property prediction.

Usage:
    python graph_neural_network.py --dataset tox21 --model gcn
    python graph_neural_network.py --dataset bbbp --model attentivefp
    python graph_neural_network.py --data custom.csv --task-type regression
"""

import argparse
import deepchem as dc
import sys


AVAILABLE_MODELS = {
    'gcn': 'Graph Convolutional Network',
    'gat': 'Graph Attention Network',
    'attentivefp': 'Attentive Fingerprint',
    'mpnn': 'Message Passing Neural Network',
    'dmpnn': 'Directed Message Passing Neural Network'
}

MOLNET_DATASETS = {
    'tox21': ('classification', 12),
    'bbbp': ('classification', 1),
    'bace': ('classification', 1),
    'hiv': ('classification', 1),
    'delaney': ('regression', 1),
    'freesolv': ('regression', 1),
    'lipo': ('regression', 1)
}

# MoleculeNet loader names that are not simply load_<dataset>. BACE ships as
# separate classification and regression loaders, so dc.molnet.load_bace does
# not exist; the entry above treats it as a classification benchmark.
MOLNET_LOADERS = {
    'bace': 'load_bace_classification'
}


def molnet_loader(dataset_name):
    """Return the dc.molnet loader function for a MoleculeNet dataset name."""
    return getattr(dc.molnet, MOLNET_LOADERS.get(dataset_name, f'load_{dataset_name}'))


def create_model(model_type, n_tasks, mode='classification'):
    """
    Create a graph neural network model.

    Args:
        model_type: Type of model ('gcn', 'gat', 'attentivefp', etc.)
        n_tasks: Number of prediction tasks
        mode: 'classification' or 'regression'

    Returns:
        DeepChem model
    """
    if model_type == 'gcn':
        return dc.models.GCNModel(
            n_tasks=n_tasks,
            mode=mode,
            batch_size=128,
            learning_rate=0.001,
            dropout=0.0
        )
    elif model_type == 'gat':
        return dc.models.GATModel(
            n_tasks=n_tasks,
            mode=mode,
            batch_size=128,
            learning_rate=0.001
        )
    elif model_type == 'attentivefp':
        return dc.models.AttentiveFPModel(
            n_tasks=n_tasks,
            mode=mode,
            batch_size=128,
            learning_rate=0.001
        )
    elif model_type == 'mpnn':
        return dc.models.MPNNModel(
            n_tasks=n_tasks,
            mode=mode,
            batch_size=128,
            learning_rate=0.001
        )
    elif model_type == 'dmpnn':
        return dc.models.DMPNNModel(
            n_tasks=n_tasks,
            mode=mode,
            batch_size=128,
            learning_rate=0.001
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")


def train_on_molnet(dataset_name, model_type, n_epochs=50):
    """
    Train a graph neural network on a MoleculeNet benchmark dataset.

    Args:
        dataset_name: Name of MoleculeNet dataset
        model_type: Type of model to train
        n_epochs: Number of training epochs

    Returns:
        Trained model and test scores
    """
    print("=" * 70)
    print(f"Training {AVAILABLE_MODELS[model_type]} on {dataset_name.upper()}")
    print("=" * 70)

    # Get dataset info
    task_type, n_tasks_default = MOLNET_DATASETS[dataset_name]

    # Load dataset with graph featurization
    print(f"\nLoading {dataset_name} dataset with GraphConv featurizer...")
    load_func = molnet_loader(dataset_name)
    tasks, datasets, transformers = load_func(
        featurizer='GraphConv',
        splitter='scaffold'
    )
    train, valid, test = datasets

    n_tasks = len(tasks)
    print(f"\nDataset Information:")
    print(f"  Task type: {task_type}")
    print(f"  Number of tasks: {n_tasks}")
    print(f"  Training samples: {len(train)}")
    print(f"  Validation samples: {len(valid)}")
    print(f"  Test samples: {len(test)}")

    # Create model
    print(f"\nCreating {AVAILABLE_MODELS[model_type]} model...")
    model = create_model(model_type, n_tasks, mode=task_type)

    # Train
    print(f"\nTraining for {n_epochs} epochs...")
    model.fit(train, nb_epoch=n_epochs)
    print("Training complete!")

    # Evaluate
    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)

    if task_type == 'classification':
        metrics = [
            dc.metrics.Metric(dc.metrics.roc_auc_score, name='ROC-AUC'),
            dc.metrics.Metric(dc.metrics.accuracy_score, name='Accuracy'),
            dc.metrics.Metric(dc.metrics.f1_score, name='F1'),
        ]
    else:
        metrics = [
            dc.metrics.Metric(dc.metrics.r2_score, name='R²'),
            dc.metrics.Metric(dc.metrics.mean_absolute_error, name='MAE'),
            dc.metrics.Metric(dc.metrics.root_mean_squared_error, name='RMSE'),
        ]

    results = {}
    for dataset_name_eval, dataset in [('Train', train), ('Valid', valid), ('Test', test)]:
        print(f"\n{dataset_name_eval} Set:")
        scores = model.evaluate(dataset, metrics)
        results[dataset_name_eval] = scores
        for metric_name, score in scores.items():
            print(f"  {metric_name}: {score:.4f}")

    return model, results


def train_on_custom_data(data_path, model_type, task_type, target_cols, smiles_col='smiles', n_epochs=50):
    """
    Train a graph neural network on custom CSV data.

    Args:
        data_path: Path to CSV file
        model_type: Type of model to train
        task_type: 'classification' or 'regression'
        target_cols: List of target column names
        smiles_col: Name of SMILES column
        n_epochs: Number of training epochs

    Returns:
        Trained model and test dataset
    """
    print("=" * 70)
    print(f"Training {AVAILABLE_MODELS[model_type]} on Custom Data")
    print("=" * 70)

    # Load and featurize data
    print(f"\nLoading data from {data_path}...")
    featurizer = dc.feat.MolGraphConvFeaturizer()
    loader = dc.data.CSVLoader(
        tasks=target_cols,
        feature_field=smiles_col,
        featurizer=featurizer
    )
    dataset = loader.create_dataset(data_path)

    print(f"Loaded {len(dataset)} molecules")

    # Split data
    print("\nSplitting data with scaffold splitter...")
    splitter = dc.splits.ScaffoldSplitter()
    train, valid, test = splitter.train_valid_test_split(
        dataset,
        frac_train=0.8,
        frac_valid=0.1,
        frac_test=0.1
    )

    print(f"  Training: {len(train)}")
    print(f"  Validation: {len(valid)}")
    print(f"  Test: {len(test)}")

    # Create model
    print(f"\nCreating {AVAILABLE_MODELS[model_type]} model...")
    n_tasks = len(target_cols)
    model = create_model(model_type, n_tasks, mode=task_type)

    # Train
    print(f"\nTraining for {n_epochs} epochs...")
    model.fit(train, nb_epoch=n_epochs)
    print("Training complete!")

    # Evaluate
    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)

    if task_type == 'classification':
        metrics = [
            dc.metrics.Metric(dc.metrics.roc_auc_score, name='ROC-AUC'),
            dc.metrics.Metric(dc.metrics.accuracy_score, name='Accuracy'),
        ]
    else:
        metrics = [
            dc.metrics.Metric(dc.metrics.r2_score, name='R²'),
            dc.metrics.Metric(dc.metrics.mean_absolute_error, name='MAE'),
        ]

    for dataset_name, dataset in [('Train', train), ('Valid', valid), ('Test', test)]:
        print(f"\n{dataset_name} Set:")
        scores = model.evaluate(dataset, metrics)
        for metric_name, score in scores.items():
            print(f"  {metric_name}: {score:.4f}")

    return model, test


def main():
    parser = argparse.ArgumentParser(
        description='Train graph neural networks for molecular property prediction'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=list(AVAILABLE_MODELS.keys()),
        default='gcn',
        help='Type of graph neural network model'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        choices=list(MOLNET_DATASETS.keys()),
        default=None,
        help='MoleculeNet dataset to use'
    )
    parser.add_argument(
        '--data',
        type=str,
        default=None,
        help='Path to custom CSV file'
    )
    parser.add_argument(
        '--task-type',
        type=str,
        choices=['classification', 'regression'],
        default='classification',
        help='Type of prediction task (for custom data)'
    )
    parser.add_argument(
        '--targets',
        nargs='+',
        default=['target'],
        help='Names of target columns (for custom data)'
    )
    parser.add_argument(
        '--smiles-col',
        type=str,
        default='smiles',
        help='Name of SMILES column'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='Number of training epochs'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.dataset is None and args.data is None:
        print("Error: Must specify either --dataset (MoleculeNet) or --data (custom CSV)",
              file=sys.stderr)
        return 1

    if args.dataset and args.data:
        print("Error: Cannot specify both --dataset and --data",
              file=sys.stderr)
        return 1

    # Train model
    try:
        if args.dataset:
            model, results = train_on_molnet(
                args.dataset,
                args.model,
                n_epochs=args.epochs
            )
        else:
            model, test_set = train_on_custom_data(
                args.data,
                args.model,
                args.task_type,
                args.targets,
                smiles_col=args.smiles_col,
                n_epochs=args.epochs
            )

        print("\n" + "=" * 70)
        print("Training Complete!")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

### `scripts/predict_solubility.py`

```python
#!/usr/bin/env python3
"""
Molecular Solubility Prediction Script

This script trains a model to predict aqueous solubility from SMILES strings
using the Delaney (ESOL) dataset as an example. Can be adapted for custom datasets.

Usage:
    python predict_solubility.py --data custom_data.csv --smiles-col smiles --target-col solubility
    python predict_solubility.py  # Uses Delaney dataset by default
"""

import argparse
import deepchem as dc
import numpy as np
import sys


def train_solubility_model(data_path=None, smiles_col='smiles', target_col='measured log solubility in mols per litre'):
    """
    Train a solubility prediction model.

    Args:
        data_path: Path to CSV file with SMILES and solubility data. If None, uses Delaney dataset.
        smiles_col: Name of column containing SMILES strings
        target_col: Name of column containing solubility values

    Returns:
        Trained model, test dataset, and transformers
    """
    print("=" * 60)
    print("DeepChem Solubility Prediction")
    print("=" * 60)

    # Load data
    if data_path is None:
        print("\nUsing Delaney (ESOL) benchmark dataset...")
        tasks, datasets, transformers = dc.molnet.load_delaney(
            featurizer='ECFP',
            splitter='scaffold'
        )
        train, valid, test = datasets
    else:
        print(f"\nLoading custom data from {data_path}...")
        featurizer = dc.feat.CircularFingerprint(radius=2, size=2048)
        loader = dc.data.CSVLoader(
            tasks=[target_col],
            feature_field=smiles_col,
            featurizer=featurizer
        )
        dataset = loader.create_dataset(data_path)

        # Split data
        print("Splitting data with scaffold splitter...")
        splitter = dc.splits.ScaffoldSplitter()
        train, valid, test = splitter.train_valid_test_split(
            dataset,
            frac_train=0.8,
            frac_valid=0.1,
            frac_test=0.1
        )

        # Normalize data
        print("Normalizing features and targets...")
        transformers = [
            dc.trans.NormalizationTransformer(
                transform_y=True,
                dataset=train
            )
        ]
        for transformer in transformers:
            train = transformer.transform(train)
            valid = transformer.transform(valid)
            test = transformer.transform(test)

        tasks = [target_col]

    print(f"\nDataset sizes:")
    print(f"  Training:   {len(train)} molecules")
    print(f"  Validation: {len(valid)} molecules")
    print(f"  Test:       {len(test)} molecules")

    # Create model
    print("\nCreating multitask regressor...")
    model = dc.models.MultitaskRegressor(
        n_tasks=len(tasks),
        n_features=2048,  # ECFP fingerprint size
        layer_sizes=[1000, 500],
        dropouts=0.25,
        learning_rate=0.001,
        batch_size=50
    )

    # Train model
    print("\nTraining model...")
    model.fit(train, nb_epoch=50)
    print("Training complete!")

    # Evaluate model
    print("\n" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)

    metrics = [
        dc.metrics.Metric(dc.metrics.r2_score, name='R²'),
        dc.metrics.Metric(dc.metrics.mean_absolute_error, name='MAE'),
        dc.metrics.Metric(dc.metrics.root_mean_squared_error, name='RMSE'),
    ]

    for dataset_name, dataset in [('Train', train), ('Valid', valid), ('Test', test)]:
        print(f"\n{dataset_name} Set:")
        scores = model.evaluate(dataset, metrics)
        for metric_name, score in scores.items():
            print(f"  {metric_name}: {score:.4f}")

    return model, test, transformers


def predict_new_molecules(model, smiles_list, transformers=None):
    """
    Predict solubility for new molecules.

    Args:
        model: Trained DeepChem model
        smiles_list: List of SMILES strings
        transformers: List of data transformers to apply

    Returns:
        Array of predictions
    """
    print("\n" + "=" * 60)
    print("Predicting New Molecules")
    print("=" * 60)

    # Featurize new molecules
    featurizer = dc.feat.CircularFingerprint(radius=2, size=2048)
    features = featurizer.featurize(smiles_list)

    # Create dataset
    new_dataset = dc.data.NumpyDataset(X=features)

    # Both training paths normalize with transform_y=True, so the model learned
    # in z-scored target space. Hand the transformers to predict() so it
    # untransforms the output back to log(mol/L) -- transforming the dataset
    # instead would do nothing (these transformers touch y, not X, and a
    # prediction dataset has no y) and leave the printed numbers z-scored.
    predictions = model.predict(new_dataset, transformers=transformers or [])

    # Display results
    print("\nPredictions:")
    for smiles, pred in zip(smiles_list, predictions):
        print(f"  {smiles:30s} -> {pred[0]:.3f} log(mol/L)")

    return predictions


def main():
    parser = argparse.ArgumentParser(
        description='Train a molecular solubility prediction model'
    )
    parser.add_argument(
        '--data',
        type=str,
        default=None,
        help='Path to CSV file with molecular data'
    )
    parser.add_argument(
        '--smiles-col',
        type=str,
        default='smiles',
        help='Name of column containing SMILES strings'
    )
    parser.add_argument(
        '--target-col',
        type=str,
        default='solubility',
        help='Name of column containing target values'
    )
    parser.add_argument(
        '--predict',
        nargs='+',
        default=None,
        help='SMILES strings to predict after training'
    )

    args = parser.parse_args()

    # Train model
    try:
        model, test_set, transformers = train_solubility_model(
            data_path=args.data,
            smiles_col=args.smiles_col,
            target_col=args.target_col
        )
    except Exception as e:
        print(f"\nError during training: {e}", file=sys.stderr)
        return 1

    # Make predictions on new molecules if provided
    if args.predict:
        try:
            predict_new_molecules(model, args.predict, transformers)
        except Exception as e:
            print(f"\nError during prediction: {e}", file=sys.stderr)
            return 1
    else:
        # Example predictions
        example_smiles = [
            'CCO',                    # Ethanol
            'CC(=O)O',                # Acetic acid
            'c1ccccc1',               # Benzene
            'CN1C=NC2=C1C(=O)N(C(=O)N2C)C',  # Caffeine
        ]
        predict_new_molecules(model, example_smiles, transformers)

    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

### `scripts/transfer_learning.py`

```python
#!/usr/bin/env python3
"""
Transfer Learning Script for DeepChem

Use pretrained models (ChemBERTa, GROVER, MolFormer) for molecular property prediction
with transfer learning. Particularly useful for small datasets.

Usage:
    python transfer_learning.py --model chemberta --data my_data.csv --target activity
    python transfer_learning.py --model grover --dataset bbbp
"""

import argparse
import deepchem as dc
import sys


PRETRAINED_MODELS = {
    'chemberta': {
        'name': 'ChemBERTa',
        'description': 'BERT pretrained on 77M molecules from ZINC15',
        'model_id': 'seyonec/ChemBERTa-zinc-base-v1'
    },
    'grover': {
        'name': 'GROVER',
        'description': 'Graph transformer pretrained on 10M molecules',
        'model_id': None  # GROVER uses its own loading mechanism
    },
    'molformer': {
        'name': 'MolFormer',
        'description': 'Transformer pretrained on molecular structures',
        'model_id': 'ibm/MoLFormer-XL-both-10pct'
    }
}


def train_chemberta(train_dataset, valid_dataset, test_dataset, task_type='classification', n_tasks=1, n_epochs=10):
    """
    Fine-tune ChemBERTa on a dataset.

    Args:
        train_dataset: Training dataset
        valid_dataset: Validation dataset
        test_dataset: Test dataset
        task_type: 'classification' or 'regression'
        n_tasks: Number of prediction tasks
        n_epochs: Number of fine-tuning epochs

    Returns:
        Trained model and evaluation results
    """
    print("=" * 70)
    print("Fine-tuning ChemBERTa")
    print("=" * 70)
    print("\nChemBERTa is a BERT model pretrained on 77M molecules from ZINC15.")
    print("It uses SMILES strings as input and has learned rich molecular")
    print("representations that transfer well to downstream tasks.")

    print(f"\nLoading pretrained ChemBERTa model...")
    model = dc.models.HuggingFaceModel(
        model=PRETRAINED_MODELS['chemberta']['model_id'],
        task=task_type,
        n_tasks=n_tasks,
        batch_size=32,
        learning_rate=2e-5  # Lower LR for fine-tuning
    )

    print(f"\nFine-tuning for {n_epochs} epochs...")
    print("(This may take a while on the first run as the model is downloaded)")
    model.fit(train_dataset, nb_epoch=n_epochs)
    print("Fine-tuning complete!")

    # Evaluate
    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)

    if task_type == 'classification':
        metrics = [
            dc.metrics.Metric(dc.metrics.roc_auc_score, name='ROC-AUC'),
            dc.metrics.Metric(dc.metrics.accuracy_score, name='Accuracy'),
        ]
    else:
        metrics = [
            dc.metrics.Metric(dc.metrics.r2_score, name='R²'),
            dc.metrics.Metric(dc.metrics.mean_absolute_error, name='MAE'),
        ]

    results = {}
    for name, dataset in [('Train', train_dataset), ('Valid', valid_dataset), ('Test', test_dataset)]:
        print(f"\n{name} Set:")
        scores = model.evaluate(dataset, metrics)
        results[name] = scores
        for metric_name, score in scores.items():
            print(f"  {metric_name}: {score:.4f}")

    return model, results


def train_grover(train_dataset, test_dataset, task_type='classification', n_tasks=1, n_epochs=20):
    """
    Fine-tune GROVER on a dataset.

    Args:
        train_dataset: Training dataset
        test_dataset: Test dataset
        task_type: 'classification' or 'regression'
        n_tasks: Number of prediction tasks
        n_epochs: Number of fine-tuning epochs

    Returns:
        Trained model and evaluation results
    """
    print("=" * 70)
    print("Fine-tuning GROVER")
    print("=" * 70)
    print("\nGROVER is a graph transformer pretrained on 10M molecules using")
    print("self-supervised learning. It learns both node and graph-level")
    print("representations through masked atom/bond prediction tasks.")

    print(f"\nCreating GROVER model...")
    model = dc.models.GroverModel(
        task=task_type,
        n_tasks=n_tasks,
        model_dir='./grover_pretrained'
    )

    print(f"\nFine-tuning for {n_epochs} epochs...")
    model.fit(train_dataset, nb_epoch=n_epochs)
    print("Fine-tuning complete!")

    # Evaluate
    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)

    if task_type == 'classification':
        metrics = [
            dc.metrics.Metric(dc.metrics.roc_auc_score, name='ROC-AUC'),
            dc.metrics.Metric(dc.metrics.accuracy_score, name='Accuracy'),
        ]
    else:
        metrics = [
            dc.metrics.Metric(dc.metrics.r2_score, name='R²'),
            dc.metrics.Metric(dc.metrics.mean_absolute_error, name='MAE'),
        ]

    results = {}
    for name, dataset in [('Train', train_dataset), ('Test', test_dataset)]:
        print(f"\n{name} Set:")
        scores = model.evaluate(dataset, metrics)
        results[name] = scores
        for metric_name, score in scores.items():
            print(f"  {metric_name}: {score:.4f}")

    return model, results


def train_molformer(train_dataset, valid_dataset, test_dataset, task_type='classification', n_tasks=1, n_epochs=10):
    """
    Fine-tune MolFormer on a dataset.

    Args:
        train_dataset: Training dataset
        valid_dataset: Validation dataset
        test_dataset: Test dataset
        task_type: 'classification' or 'regression'
        n_tasks: Number of prediction tasks
        n_epochs: Number of fine-tuning epochs

    Returns:
        Trained model and evaluation results
    """
    print("=" * 70)
    print("Fine-tuning MolFormer")
    print("=" * 70)
    print("\nMolFormer is a transformer pretrained on molecular structures.")
    print("It uses SMILES strings as input via HuggingFaceModel.")

    print(f"\nLoading pretrained MolFormer model...")
    model = dc.models.HuggingFaceModel(
        model=PRETRAINED_MODELS['molformer']['model_id'],
        task=task_type,
        n_tasks=n_tasks,
        batch_size=32,
        learning_rate=2e-5
    )

    print(f"\nFine-tuning for {n_epochs} epochs...")
    print("(This may take a while on the first run as the model is downloaded)")
    model.fit(train_dataset, nb_epoch=n_epochs)
    print("Fine-tuning complete!")

    print("\n" + "=" * 70)
    print("Model Evaluation")
    print("=" * 70)

    if task_type == 'classification':
        metrics = [
            dc.metrics.Metric(dc.metrics.roc_auc_score, name='ROC-AUC'),
            dc.metrics.Metric(dc.metrics.accuracy_score, name='Accuracy'),
        ]
    else:
        metrics = [
            dc.metrics.Metric(dc.metrics.r2_score, name='R²'),
            dc.metrics.Metric(dc.metrics.mean_absolute_error, name='MAE'),
        ]

    results = {}
    for name, dataset in [('Train', train_dataset), ('Valid', valid_dataset), ('Test', test_dataset)]:
        print(f"\n{name} Set:")
        scores = model.evaluate(dataset, metrics)
        results[name] = scores
        for metric_name, score in scores.items():
            print(f"  {metric_name}: {score:.4f}")

    return model, results


def load_molnet_dataset(dataset_name, model_type):
    """
    Load a MoleculeNet dataset with appropriate featurization.

    Args:
        dataset_name: Name of MoleculeNet dataset
        model_type: Type of pretrained model being used

    Returns:
        tasks, train/valid/test datasets, transformers
    """
    # Map of MoleculeNet datasets
    molnet_datasets = {
        'tox21': dc.molnet.load_tox21,
        'bbbp': dc.molnet.load_bbbp,
        'bace': dc.molnet.load_bace_classification,
        'hiv': dc.molnet.load_hiv,
        'delaney': dc.molnet.load_delaney,
        'freesolv': dc.molnet.load_freesolv,
        'lipo': dc.molnet.load_lipo
    }

    if dataset_name not in molnet_datasets:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    # ChemBERTa and MolFormer use raw SMILES
    if model_type in ['chemberta', 'molformer']:
        featurizer = 'Raw'
    # GROVER needs graph features
    elif model_type == 'grover':
        featurizer = 'GraphConv'
    else:
        featurizer = 'ECFP'

    print(f"\nLoading {dataset_name} dataset...")
    load_func = molnet_datasets[dataset_name]
    tasks, datasets, transformers = load_func(
        featurizer=featurizer,
        splitter='scaffold'
    )

    return tasks, datasets, transformers


def load_custom_dataset(data_path, target_cols, smiles_col, model_type):
    """
    Load a custom CSV dataset.

    Args:
        data_path: Path to CSV file
        target_cols: List of target column names
        smiles_col: Name of SMILES column
        model_type: Type of pretrained model being used

    Returns:
        train, valid, test datasets
    """
    print(f"\nLoading custom data from {data_path}...")

    # Choose featurizer based on model
    if model_type in ['chemberta', 'molformer']:
        featurizer = dc.feat.DummyFeaturizer()  # Models handle featurization
    elif model_type == 'grover':
        featurizer = dc.feat.MolGraphConvFeaturizer()
    else:
        featurizer = dc.feat.CircularFingerprint()

    loader = dc.data.CSVLoader(
        tasks=target_cols,
        feature_field=smiles_col,
        featurizer=featurizer
    )
    dataset = loader.create_dataset(data_path)

    print(f"Loaded {len(dataset)} molecules")

    # Split data
    print("Splitting data with scaffold splitter...")
    splitter = dc.splits.ScaffoldSplitter()
    train, valid, test = splitter.train_valid_test_split(
        dataset,
        frac_train=0.8,
        frac_valid=0.1,
        frac_test=0.1
    )

    print(f"  Training: {len(train)}")
    print(f"  Validation: {len(valid)}")
    print(f"  Test: {len(test)}")

    return train, valid, test


def main():
    parser = argparse.ArgumentParser(
        description='Transfer learning for molecular property prediction'
    )
    parser.add_argument(
        '--model',
        type=str,
        choices=list(PRETRAINED_MODELS.keys()),
        required=True,
        help='Pretrained model to use'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        choices=['tox21', 'bbbp', 'bace', 'hiv', 'delaney', 'freesolv', 'lipo'],
        default=None,
        help='MoleculeNet dataset to use'
    )
    parser.add_argument(
        '--data',
        type=str,
        default=None,
        help='Path to custom CSV file'
    )
    parser.add_argument(
        '--target',
        nargs='+',
        default=['target'],
        help='Target column name(s) for custom data'
    )
    parser.add_argument(
        '--smiles-col',
        type=str,
        default='smiles',
        help='SMILES column name for custom data'
    )
    parser.add_argument(
        '--task-type',
        type=str,
        choices=['classification', 'regression'],
        default='classification',
        help='Type of prediction task'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=10,
        help='Number of fine-tuning epochs'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.dataset is None and args.data is None:
        print("Error: Must specify either --dataset or --data", file=sys.stderr)
        return 1

    if args.dataset and args.data:
        print("Error: Cannot specify both --dataset and --data", file=sys.stderr)
        return 1

    # Print model info
    model_info = PRETRAINED_MODELS[args.model]
    print("\n" + "=" * 70)
    print(f"Transfer Learning with {model_info['name']}")
    print("=" * 70)
    print(f"\n{model_info['description']}")

    try:
        # Load dataset
        if args.dataset:
            tasks, datasets, transformers = load_molnet_dataset(args.dataset, args.model)
            train, valid, test = datasets
            task_type = 'classification' if args.dataset in ['tox21', 'bbbp', 'bace', 'hiv'] else 'regression'
            n_tasks = len(tasks)
        else:
            train, valid, test = load_custom_dataset(
                args.data,
                args.target,
                args.smiles_col,
                args.model
            )
            task_type = args.task_type
            n_tasks = len(args.target)

        # Train model
        if args.model == 'chemberta':
            model, results = train_chemberta(
                train, valid, test,
                task_type=task_type,
                n_tasks=n_tasks,
                n_epochs=args.epochs
            )
        elif args.model == 'grover':
            model, results = train_grover(
                train, test,
                task_type=task_type,
                n_tasks=n_tasks,
                n_epochs=args.epochs
            )
        elif args.model == 'molformer':
            model, results = train_molformer(
                train, valid, test,
                task_type=task_type,
                n_tasks=n_tasks,
                n_epochs=args.epochs
            )
        else:
            print(f"Error: Model {args.model} not yet implemented", file=sys.stderr)
            return 1

        print("\n" + "=" * 70)
        print("Transfer Learning Complete!")
        print("=" * 70)
        print("\nTip: Pretrained models often work best with:")
        print("  - Small datasets (< 1000 samples)")
        print("  - Lower learning rates (1e-5 to 5e-5)")
        print("  - Fewer epochs (5-20)")
        print("  - Avoiding overfitting through early stopping")

        return 0

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
```
