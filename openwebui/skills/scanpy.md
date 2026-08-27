---
name: scanpy
description: Standard single-cell RNA-seq analysis pipeline. Use for QC, normalization, dimensionality reduction (PCA/UMAP/t-SNE), clustering, differential expression, visualization, and converting R-friendly single-cell formats such as Seurat or SingleCellExperiment RDS files into h5ad for Scanpy. Best for exploratory scRNA-seq analysis with established workflows. For deep learning models use scvi-tools; for data format questions use anndata.
---

# Scanpy: Single-Cell Analysis

## Overview

Scanpy is a scalable Python toolkit for analyzing single-cell RNA-seq data, built on AnnData. Apply this skill for complete single-cell workflows including quality control, normalization, dimensionality reduction, clustering, marker gene identification, visualization, and trajectory analysis. Current stable release: **scanpy 1.12.x** (January 2026).

## Installation

Requires Python **3.12+** (scanpy 1.12 dropped Python ≤3.11) and anndata **≥0.10**.

```bash
uv pip install "scanpy[leiden]"
```

The `[leiden]` extra installs `python-igraph` and `leidenalg`, required for Leiden clustering. For reproducible environments, pin a version: `uv pip install "scanpy[leiden]==1.12.1"`.

For large or out-of-core datasets, many functions support [Dask](https://docs.dask.org/) arrays (experimental):

```bash
uv pip install "scanpy[leiden]" dask
```

See the [Using dask with Scanpy](https://scanpy.scverse.org/en/stable/tutorials/experimental/dask.html) tutorial. For GPU-accelerated scanpy-like operations, use [rapids-singlecell](https://rapids-singlecell.readthedocs.io/) as a separate package.

If the input is an R-native single-cell object (`.rds`, `.RData`, Seurat, or SingleCellExperiment), first convert it to `.h5ad` with R tooling, then load it with Scanpy. Read `references/r_interop.md` for agent-run installation and conversion instructions across macOS, Linux, and Windows.

For AnnData structure and I/O details, use the **anndata** skill. For probabilistic models and batch correction, use **scvi-tools**.

## When to Use This Skill

This skill should be used when:
- Analyzing single-cell RNA-seq data (.h5ad, 10X, CSV formats)
- Working with R-friendly single-cell datasets (`.rds`, `.RData`, Seurat, SingleCellExperiment) that need conversion to `.h5ad`
- Performing quality control on scRNA-seq datasets
- Creating UMAP, t-SNE, or PCA visualizations
- Identifying cell clusters and finding marker genes
- Annotating cell types based on gene expression
- Conducting trajectory inference or pseudotime analysis
- Generating publication-quality single-cell plots

## Script Toolkit (prefer these over writing code from scratch)

This skill bundles ready-to-run CLI scripts in `scripts/` for every common step. **Run these instead of hand-writing scanpy code** — they handle file loading by extension, figure setup, sensible defaults, raw-count preservation, and progress logging. Each reads and writes `.h5ad`, so they chain together, and each has its own `--help`. Only drop down to writing scanpy code when a task isn't covered by a script or needs unusual customization.

All scripts use a shared `scripts/_common.py` helper (loading, saving, figure config) — keep it alongside the others. Run from the skill directory or pass full paths; figures default to `./figures/`.

| Script | Purpose | Typical call |
|--------|---------|--------------|
| `run_pipeline.py` | **Full workflow in one command**: load → QC → normalize → HVG → PCA → (batch) → UMAP → Leiden → markers | `python scripts/run_pipeline.py raw.h5ad -o processed.h5ad` |
| `inspect_data.py` | Summarize an unknown dataset (shape, obs/var, layers, what's already computed, raw vs normalized) | `python scripts/inspect_data.py data.h5ad` |
| `convert.py` | Load any format (10x dir/.h5, csv, loom, mtx) and write `.h5ad` | `python scripts/convert.py 10x_dir/ -o data.h5ad` |
| `qc_analysis.py` | QC metrics, before/after plots, filtering, optional Scrublet doublets | `python scripts/qc_analysis.py raw.h5ad -o qc.h5ad --scrublet` |
| `preprocess.py` | Normalize, log1p, HVG, optional scale/regress (keeps `counts` layer + `raw`) | `python scripts/preprocess.py qc.h5ad -o norm.h5ad` |
| `reduce_dimensions.py` | PCA + variance plot, neighbors, UMAP, optional t-SNE | `python scripts/reduce_dimensions.py norm.h5ad -o red.h5ad` |
| `batch_correct.py` | Integration: harmony / bbknn / combat | `python scripts/batch_correct.py red.h5ad -o int.h5ad --method harmony --batch-key sample` |
| `cluster.py` | Leiden (or louvain) at one or many resolutions | `python scripts/cluster.py red.h5ad -o clu.h5ad --resolution 0.3 0.6 1.0` |
| `find_markers.py` | `rank_genes_groups` + per-group CSVs + marker plots | `python scripts/find_markers.py clu.h5ad --groupby leiden -o clu.h5ad` |
| `annotate.py` | Map clusters → cell types from JSON/CSV; optional marker reference dotplot | `python scripts/annotate.py clu.h5ad -o ann.h5ad --mapping map.json` |
| `score_genes.py` | Score gene signatures (JSON) and/or cell-cycle phase | `python scripts/score_genes.py ann.h5ad -o scored.h5ad --gene-sets sigs.json` |
| `pseudobulk.py` | Aggregate counts by sample × cell type → matrix for pydeseq2 | `python scripts/pseudobulk.py ann.h5ad --by sample cell_type --out-prefix pb` |
| `subset.py` | Subset by obs values or gene list (optionally clear stale embeddings) | `python scripts/subset.py ann.h5ad -o tcells.h5ad --obs cell_type --keep "T cells"` |
| `plot.py` | Generate umap/tsne/pca/violin/dotplot/heatmap/etc. from a processed object | `python scripts/plot.py ann.h5ad --kind dotplot --genes CD3D CD14 --groupby cell_type` |

### One-shot end-to-end run

```bash
# Counts → clustered, marker-annotated object + figures + marker CSVs
python scripts/run_pipeline.py raw.h5ad -o processed.h5ad \
    --resolution 0.5 --n-top-genes 2000 --scrublet
# With multi-sample integration:
python scripts/run_pipeline.py raw.h5ad -o processed.h5ad --batch-key sample --batch-method harmony
# Reproducible parameters via JSON (keys mirror flag names with underscores):
python scripts/run_pipeline.py raw.h5ad -o processed.h5ad --config params.json
```

### Step-by-step chain (when you need to inspect/iterate between stages)

```bash
python scripts/qc_analysis.py        raw.h5ad  -o qc.h5ad   --scrublet
python scripts/preprocess.py         qc.h5ad   -o norm.h5ad --n-top-genes 2000
python scripts/reduce_dimensions.py  norm.h5ad -o red.h5ad  --n-pcs 40
python scripts/cluster.py            red.h5ad  -o clu.h5ad  --resolution 0.3 0.5 0.8
python scripts/find_markers.py       clu.h5ad  -o clu.h5ad  --groupby leiden --use-raw
# inspect results/markers/*.csv, decide labels, write a mapping JSON, then:
python scripts/annotate.py           clu.h5ad  -o ann.h5ad  --mapping celltypes.json
```

The sections below document the underlying scanpy calls each script performs — read them when customizing beyond the script flags.

## Quick Start

### Basic Import and Setup

```python
import scanpy as sc
import pandas as pd
import numpy as np

# Configure settings
sc.settings.verbosity = 3
sc.settings.set_figure_params(dpi=80, facecolor='white')
sc.settings.figdir = './figures/'
sc.settings.autosave = True  # Preferred over per-plot save= (deprecated in scanpy 1.12)
```

### Loading Data

```python
# From 10X Genomics
adata = sc.read_10x_mtx('path/to/data/')
adata = sc.read_10x_h5('path/to/data.h5')

# From h5ad (AnnData format)
adata = sc.read_h5ad('path/to/data.h5ad')

# From CSV
adata = sc.read_csv('path/to/data.csv')
```

For R-native files, do not try to parse Seurat `.rds` directly in Python. Convert first:

```bash
# See references/r_interop.md for installing R and conversion packages.
Rscript convert_rds_to_h5ad.R input.rds output.h5ad
```

```python
adata = sc.read_h5ad('output.h5ad')
```

### Understanding AnnData Structure

The AnnData object is the core data structure in scanpy:

```python
adata.X          # Expression matrix (cells × genes)
adata.obs        # Cell metadata (DataFrame)
adata.var        # Gene metadata (DataFrame)
adata.uns        # Unstructured annotations (dict)
adata.obsm       # Multi-dimensional cell data (PCA, UMAP)
adata.raw        # Raw data backup

# Access cell and gene names
adata.obs_names  # Cell barcodes
adata.var_names  # Gene names
```

## Standard Analysis Workflow

The seven steps, with code and the parameters that matter at each, are in
[references/analysis_workflow.md](references/analysis_workflow.md):

1. **Quality control** — filter cells and genes; inspect mitochondrial fraction and counts
   before choosing thresholds rather than copying defaults.
2. **Normalization and preprocessing** — normalize, log-transform, select highly variable
   genes, and keep `.raw` for later plotting.
3. **Dimensionality reduction** — PCA, then the neighbour graph, then UMAP.
4. **Clustering** — Leiden at a resolution chosen for the question, not the default.
5. **Marker gene identification** — ranked genes per cluster.
6. **Cell type annotation** — mapping clusters to types from markers.
7. **Save results** — writing the annotated `AnnData`.

Common follow-on tasks — publication plots, trajectory inference, pseudobulk differential
expression between conditions, gene set scoring, and batch correction — are in the same
file. See also [references/standard_workflow.md](references/standard_workflow.md) and
[references/plotting_guide.md](references/plotting_guide.md).

## Key Parameters to Adjust

### Quality Control
- `min_genes`: Minimum genes per cell (typically 200-500)
- `min_cells`: Minimum cells per gene (typically 3-10)
- `pct_counts_mt`: Mitochondrial threshold (typically 5-20%)

### Normalization
- `target_sum`: Target counts per cell (default 1e4)

### Feature Selection
- `n_top_genes`: Number of HVGs (typically 2000-3000)
- `min_mean`, `max_mean`, `min_disp`: HVG selection parameters

### Dimensionality Reduction
- `n_pcs`: Number of principal components (check variance ratio plot)
- `n_neighbors`: Number of neighbors (typically 10-30)

### Clustering
- `resolution`: Clustering granularity (0.4-1.2, higher = more clusters)

## Common Pitfalls and Best Practices

1. **Always save raw counts**: `adata.raw = adata` before filtering genes
2. **Check QC plots carefully**: Adjust thresholds based on dataset quality
3. **Use Leiden clustering**: `sc.tl.louvain` is deprecated in scanpy 1.12
4. **Try multiple clustering resolutions**: Find optimal granularity
5. **Validate cell type annotations**: Use multiple marker genes
6. **Use `use_raw=True` for gene expression plots**: Shows normalized counts from `.raw`
7. **Check PCA variance ratio**: Determine optimal number of PCs
8. **Save intermediate results**: Long workflows can fail partway through
9. **Pseudobulk for DE**: Do not treat `rank_genes_groups` p-values as rigorous DE between conditions
10. **Save plots via settings**: Use `sc.settings.autosave` instead of deprecated `save=` on plot functions
11. **Convert R objects before Scanpy**: Use R packages to convert Seurat or SingleCellExperiment `.rds` files to `.h5ad`, preserving counts, metadata, and gene identifiers

## Bundled Resources

### scripts/ (CLI toolkit)
A composable set of `.h5ad`-in/`.h5ad`-out scripts covering the whole workflow plus a one-command end-to-end pipeline. See the **Script Toolkit** section above for the full table and chaining examples. Each script has `--help`. Files:

- `_common.py` — shared loading/saving/figure helpers imported by the others (not a CLI)
- `run_pipeline.py` — full pipeline in one command (flags or `--config` JSON)
- `inspect_data.py`, `convert.py` — explore and load/convert any input format
- `qc_analysis.py`, `preprocess.py`, `reduce_dimensions.py`, `batch_correct.py`, `cluster.py` — pipeline steps
- `find_markers.py`, `annotate.py`, `score_genes.py`, `pseudobulk.py` — markers, annotation, scoring, DE prep
- `subset.py`, `plot.py` — subset by metadata/genes; generate any standard plot

**Default to these scripts before writing scanpy code from scratch.**

### references/standard_workflow.md
Complete step-by-step workflow with detailed explanations and code examples for:
- Data loading and setup
- Quality control with visualization
- Normalization and scaling
- Feature selection
- Dimensionality reduction (PCA, UMAP, t-SNE)
- Clustering (Leiden)
- Doublet detection (scrublet) and pseudobulk aggregation
- Marker gene identification
- Cell type annotation
- Trajectory inference
- Differential expression

Read this reference when performing a complete analysis from scratch.

### references/api_reference.md
Quick reference guide for scanpy functions organized by module:
- Reading/writing data (`sc.read_*`, `adata.write_*`)
- Preprocessing (`sc.pp.*`)
- Tools (`sc.tl.*`)
- Plotting (`sc.pl.*`)
- AnnData structure and manipulation
- Settings and utilities

Use this for quick lookup of function signatures and common parameters.

### references/plotting_guide.md
Comprehensive visualization guide including:
- Quality control plots
- Dimensionality reduction visualizations
- Clustering visualizations
- Marker gene plots (heatmaps, dot plots, violin plots)
- Trajectory and pseudotime plots
- Publication-quality customization
- Multi-panel figures
- Color palettes and styling

Consult this when creating publication-ready figures.

### references/r_interop.md
Agent runbook for installing R on macOS, Linux, and Windows, installing CRAN/Bioconductor conversion packages, inspecting `.rds`/`.RData` inputs, converting Seurat or SingleCellExperiment objects to `.h5ad`, and validating the result in Scanpy.

### assets/analysis_template.py
Complete analysis template providing a full workflow from data loading through cell type annotation. Copy and customize this template for new analyses:

```bash
cp assets/analysis_template.py my_analysis.py
# Edit parameters and run
python my_analysis.py
```

The template includes all standard steps with configurable parameters and helpful comments.

### assets/ JSON templates
Edit-and-pass templates so you don't author config/mappings from scratch:
- `assets/pipeline_config.json` — parameter set for `run_pipeline.py --config`
- `assets/celltype_mapping.json` — cluster → cell-type map for `annotate.py --mapping`
- `assets/gene_signatures.json` — gene-set signatures for `score_genes.py --gene-sets`

## Additional Resources

- **Official scanpy documentation**: https://scanpy.scverse.org/en/stable/
- **Scanpy tutorials**: https://scanpy.scverse.org/en/stable/tutorials/index.html
- **Release notes**: https://scanpy.scverse.org/en/stable/release-notes/index.html
- **scverse ecosystem**: https://scverse.org/ (related tools: squidpy, scvi-tools, cellrank)
- **R interoperability**: https://www.bioconductor.org/packages/release/bioc/html/zellkonverter.html and https://mojaveazure.github.io/seurat-disk/
- **Best practices**: Luecken & Theis (2019) "Current best practices in single-cell RNA-seq"

## Tips for Effective Analysis

1. **Start with the template**: Use `assets/analysis_template.py` as a starting point
2. **Run QC script first**: Use `scripts/qc_analysis.py` for initial filtering
3. **Consult references as needed**: Load workflow and API references into context
4. **Iterate on clustering**: Try multiple resolutions and visualization methods
5. **Validate biologically**: Check marker genes match expected cell types
6. **Document parameters**: Record QC thresholds and analysis settings
7. **Save checkpoints**: Write intermediate results at key steps

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/scanpy/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/analysis_workflow.md`

# Standard Analysis Workflow and Common Tasks

The seven workflow steps in full — quality control, normalization and preprocessing,
dimensionality reduction, clustering, marker gene identification, cell type annotation,
and saving results — followed by common tasks: publication-quality plots, trajectory
inference, pseudobulk differential expression between conditions, gene set scoring, and
batch correction.

## Standard Analysis Workflow

### 1. Quality Control

Identify and filter low-quality cells and genes:

```python
# Identify mitochondrial genes
adata.var['mt'] = adata.var_names.str.startswith('MT-')

# Calculate QC metrics
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# Visualize QC metrics
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True)

# Filter cells and genes
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.pct_counts_mt < 5, :]  # Remove high MT% cells
```

**Doublet detection (optional, on raw counts before normalization):**

```python
sc.pp.scrublet(adata)  # Core API since scanpy 1.10 (was scanpy.external.pp)
adata = adata[~adata.obs['predicted_doublet'], :].copy()
```

**Use the QC script for automated analysis** (run from the skill directory or pass the full path):

```bash
python skills/scanpy/scripts/qc_analysis.py input_file.h5ad --output filtered.h5ad
```

### 2. Normalization and Preprocessing

```python
# Normalize to 10,000 counts per cell
sc.pp.normalize_total(adata, target_sum=1e4)

# Log-transform
sc.pp.log1p(adata)

# Save raw counts for later
adata.raw = adata

# Identify highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pl.highly_variable_genes(adata)

# Subset to highly variable genes
adata = adata[:, adata.var.highly_variable]

# Regress out unwanted variation
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])

# Scale data
sc.pp.scale(adata, max_value=10)
```

### 3. Dimensionality Reduction

```python
# PCA
sc.tl.pca(adata, svd_solver='arpack')
sc.pl.pca_variance_ratio(adata, log=True)  # Check elbow plot

# Compute neighborhood graph
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)

# UMAP for visualization
sc.tl.umap(adata)
sc.pl.umap(adata, color='leiden')

# Alternative: t-SNE
sc.tl.tsne(adata)
```

### 4. Clustering

```python
# Leiden clustering (recommended)
sc.tl.leiden(adata, resolution=0.5)
sc.pl.umap(adata, color='leiden', legend_loc='on data')

# Try multiple resolutions to find optimal granularity
for res in [0.3, 0.5, 0.8, 1.0]:
    sc.tl.leiden(adata, resolution=res, key_added=f'leiden_{res}')
```

### 5. Marker Gene Identification

Use `rank_genes_groups` for **exploratory cluster markers** only. Per-cell statistical tests inflate p-values because cells are not independent observations. For rigorous differential expression between conditions or samples, pseudobulk first (see below) and use **pydeseq2** or similar tools.

```python
# Find marker genes for each cluster (exploratory)
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')

# Visualize results
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False)
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10)
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5)

# Get results as DataFrame
markers = sc.get.rank_genes_groups_df(adata, group='0')
```

### 6. Cell Type Annotation

```python
# Define marker genes for known cell types
marker_genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7', 'FCGR3A']

# Visualize markers
sc.pl.umap(adata, color=marker_genes, use_raw=True)
sc.pl.dotplot(adata, var_names=marker_genes, groupby='leiden')

# Manual annotation
cluster_to_celltype = {
    '0': 'CD4 T cells',
    '1': 'CD14+ Monocytes',
    '2': 'B cells',
    '3': 'CD8 T cells',
}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_to_celltype)

# Visualize annotated types
sc.pl.umap(adata, color='cell_type', legend_loc='on data')
```

### 7. Save Results

```python
# Save processed data
adata.write('results/processed_data.h5ad')

# Export metadata
adata.obs.to_csv('results/cell_metadata.csv')
adata.var.to_csv('results/gene_metadata.csv')
```

## Common Tasks

### Creating Publication-Quality Plots

Prefer `sc.settings.autosave` and `sc.settings.figdir` for saving figures. The per-plot `save=` parameter is deprecated in scanpy 1.12.

```python
# Set high-quality defaults
sc.settings.set_figure_params(dpi=300, frameon=False, figsize=(5, 5))
sc.settings.file_format_figs = 'pdf'
sc.settings.figdir = './figures/'
sc.settings.autosave = True

# UMAP with custom styling (saved as figures/umap.pdf via autosave)
sc.pl.umap(adata, color='cell_type',
           palette='Set2',
           legend_loc='on data',
           legend_fontsize=12,
           legend_fontoutline=2,
           frameon=False)

# Heatmap of marker genes
sc.pl.heatmap(adata, var_names=genes, groupby='cell_type',
              swap_axes=True, show_gene_labels=True)

# Dot plot
sc.pl.dotplot(adata, var_names=genes, groupby='cell_type')
```

Refer to `references/plotting_guide.md` for comprehensive visualization examples.

### Trajectory Inference

```python
# PAGA (Partition-based graph abstraction)
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color='leiden')

# Diffusion pseudotime
adata.uns['iroot'] = np.flatnonzero(adata.obs['leiden'] == '0')[0]
sc.tl.dpt(adata)
sc.pl.umap(adata, color='dpt_pseudotime')
```

### Pseudobulk and Differential Expression Between Conditions

Pseudobulk by sample and cell type, then run proper DE (e.g., pydeseq2) rather than per-cell `rank_genes_groups`:

```python
# Aggregate counts by sample and cell type (dask-compatible in scanpy 1.12)
pb = sc.get.aggregate(
    adata,
    by=['sample', 'cell_type'],
    func='sum',
    layer='counts',  # Use raw counts layer if available
)
# Downstream: export pb and use pydeseq2 for condition comparisons
```

For quick exploratory comparisons within a cluster, `rank_genes_groups` is acceptable but interpret p-values cautiously:

```python
adata_subset = adata[adata.obs['cell_type'] == 'T cells']
sc.tl.rank_genes_groups(adata_subset, groupby='condition',
                         groups=['treated'], reference='control')
sc.pl.rank_genes_groups(adata_subset, groups=['treated'])
```

### Gene Set Scoring

```python
# Score cells for gene set expression
gene_set = ['CD3D', 'CD3E', 'CD3G']
sc.tl.score_genes(adata, gene_set, score_name='T_cell_score')
sc.pl.umap(adata, color='T_cell_score')
```

### Batch Correction

```python
# ComBat batch correction
sc.pp.combat(adata, key='batch')

# Alternative: use Harmony or scVI (separate packages)
```

### `references/api_reference.md`

# Scanpy API Quick Reference

Quick reference for commonly used scanpy functions organized by module.

## Import Convention

```python
import scanpy as sc
```

## Reading and Writing Data (sc.read_*)

### Reading Functions

```python
sc.read_10x_h5(filename)                    # Read 10X HDF5 file
sc.read_10x_mtx(path)                       # Read 10X mtx directory
sc.read_h5ad(filename)                      # Read h5ad (AnnData) file
sc.read_csv(filename)                       # Read CSV file
sc.read_excel(filename)                     # Read Excel file
sc.read_loom(filename)                      # Read loom file
sc.read_text(filename)                      # Read text file
sc.read_visium(path)                        # Read Visium spatial data
```

### Writing Functions

```python
adata.write_h5ad(filename)                  # Write to h5ad format
adata.write_csvs(dirname)                   # Write to CSV files
adata.write_loom(filename)                  # Write to loom format
adata.write_zarr(filename)                  # Write to zarr format
```

## Preprocessing (sc.pp.*)

### Quality Control

```python
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.scrublet(adata)                              # Doublet detection (core since 1.10)
sc.pp.scrublet_simulate_doublets(adata)            # Simulate doublets for benchmarking
```

### Normalization and Transformation

```python
sc.pp.normalize_total(adata, target_sum=1e4)    # Normalize to target sum
sc.pp.log1p(adata)                               # Log(x + 1) transformation
sc.pp.sqrt(adata)                                # Square root transformation
```

### Feature Selection

```python
sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
sc.pp.highly_variable_genes(adata, flavor='seurat_v3', n_top_genes=2000)
# seurat, cell_ranger, seurat_v3 flavors support dask arrays (scanpy 1.10+)
```

### Scaling and Regression

```python
sc.pp.scale(adata, max_value=10)                      # Scale to unit variance
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])  # Regress out unwanted variation
```

### Dimensionality Reduction (Preprocessing)

```python
sc.pp.pca(adata, n_comps=50)                     # Principal component analysis
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40) # Compute neighborhood graph
sc.pp.neighbors(adata, method='jaccard')         # Jaccard connectivities (scanpy 1.12)
```

### Batch Correction

```python
sc.pp.combat(adata, key='batch')                 # ComBat batch correction
```

## Tools (sc.tl.*)

### Dimensionality Reduction

```python
sc.tl.pca(adata, svd_solver='arpack')            # PCA
sc.tl.umap(adata)                                 # UMAP embedding
sc.tl.tsne(adata)                                 # t-SNE embedding
sc.tl.diffmap(adata)                              # Diffusion map
sc.tl.draw_graph(adata, layout='fa')             # Force-directed graph
```

### Clustering

```python
sc.tl.leiden(adata, resolution=0.5)              # Leiden clustering (recommended)
# sc.tl.louvain(adata, resolution=0.5)           # Deprecated in scanpy 1.12 — use leiden
sc.tl.kmeans(adata, n_clusters=10)               # K-means clustering
```

### Marker Genes and Differential Expression

```python
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')
sc.tl.rank_genes_groups(adata, groupby='leiden', method='t-test')
sc.tl.rank_genes_groups(adata, groupby='leiden', method='logreg')

# Get results as dataframe
sc.get.rank_genes_groups_df(adata, group='0')
# Exploratory only — per-cell tests inflate p-values; pseudobulk for rigorous DE
```

### Aggregation (Pseudobulk)

```python
sc.get.aggregate(adata, by='cell_type', func='sum', layer='counts')
sc.get.aggregate(adata, by=['sample', 'cell_type'], func=['sum', 'mean'])
# Dask-compatible for sum/mean/count (scanpy 1.12); use pydeseq2 for DE on pseudobulk
```

### Trajectory Inference

```python
sc.tl.paga(adata, groups='leiden')               # PAGA trajectory
sc.tl.dpt(adata)                                  # Diffusion pseudotime
```

### Gene Scoring

```python
sc.tl.score_genes(adata, gene_list, score_name='score')
sc.tl.score_genes_cell_cycle(adata, s_genes, g2m_genes)
```

### Embeddings and Projections

```python
sc.tl.ingest(adata, adata_ref)                   # Map to reference
sc.tl.embedding_density(adata, basis='umap', groupby='leiden')
```

## Plotting (sc.pl.*)

### Basic Embeddings

```python
sc.pl.umap(adata, color='leiden')                # UMAP plot
sc.pl.tsne(adata, color='gene_name')             # t-SNE plot
sc.pl.pca(adata, color='leiden')                 # PCA plot
sc.pl.diffmap(adata, color='leiden')             # Diffusion map plot
```

### Heatmaps and Dot Plots

```python
sc.pl.heatmap(adata, var_names=genes, groupby='leiden')
sc.pl.dotplot(adata, var_names=genes, groupby='leiden')
sc.pl.matrixplot(adata, var_names=genes, groupby='leiden')
sc.pl.stacked_violin(adata, var_names=genes, groupby='leiden')
```

### Violin and Scatter Plots

```python
sc.pl.violin(adata, keys=['gene1', 'gene2'], groupby='leiden')
sc.pl.scatter(adata, x='gene1', y='gene2', color='leiden')
```

### Marker Gene Visualization

```python
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False)
sc.pl.rank_genes_groups_violin(adata, groups='0')
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10)
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5)
```

### Trajectory Visualization

```python
sc.pl.paga(adata, color='leiden')                # PAGA graph
sc.pl.dpt_timeseries(adata)                      # DPT timeseries
```

### QC Plots

```python
sc.pl.highest_expr_genes(adata, n_top=20)
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'])
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

### Advanced Plots

```python
sc.pl.dendrogram(adata, groupby='leiden')
sc.pl.correlation_matrix(adata, groupby='leiden')
sc.pl.tracksplot(adata, var_names=genes, groupby='leiden')
```

## Common Parameters

### Color Parameters
- `color`: Variable(s) to color by (gene name, obs column)
- `use_raw`: Use `.raw` attribute of adata
- `palette`: Color palette to use
- `vmin`, `vmax`: Color scale limits

### Layout Parameters
- `basis`: Embedding basis ('umap', 'tsne', 'pca', etc.)
- `legend_loc`: Legend location ('on data', 'right margin', etc.)
- `size`: Point size
- `alpha`: Point transparency

### Saving Parameters
- `show`: Whether to show plot
- Prefer `sc.settings.autosave` + `sc.settings.figdir` over deprecated `save=`

## AnnData Structure

```python
adata.X                    # Expression matrix (cells × genes)
adata.obs                  # Cell annotations (DataFrame)
adata.var                  # Gene annotations (DataFrame)
adata.uns                  # Unstructured annotations (dict)
adata.obsm                 # Multi-dimensional cell annotations (e.g., PCA, UMAP)
adata.varm                 # Multi-dimensional gene annotations
adata.layers               # Additional data layers
adata.raw                  # Raw data backup

# Access
adata.obs_names            # Cell barcodes
adata.var_names            # Gene names
adata.shape                # (n_cells, n_genes)

# Slicing
adata[cell_indices, gene_indices]
adata[:, adata.var_names.isin(gene_list)]
adata[adata.obs['leiden'] == '0', :]
```

## Settings

```python
sc.settings.verbosity = 3              # 0=error, 1=warning, 2=info, 3=hint
sc.settings.set_figure_params(dpi=80, facecolor='white')
sc.settings.autoshow = False           # Don't show plots automatically
sc.settings.autosave = True            # Save figures to figdir (preferred over save=)
sc.settings.figdir = './figures/'      # Figure directory
sc.settings.file_format_figs = 'pdf'   # Output format when autosave is True
sc.settings.cachedir = './cache/'      # Cache directory
sc.settings.n_jobs = 8                 # Number of parallel jobs
```

Note: the `save=` parameter on individual `sc.pl.*` functions is deprecated in scanpy 1.12. Use `sc.settings.autosave` and `sc.settings.figdir` instead.

## Useful Utilities

```python
sc.logging.print_versions()            # Print version information
sc.logging.print_memory_usage()        # Print memory usage
adata.copy()                           # Create a copy of AnnData object
adata.concatenate([adata1, adata2])    # Concatenate AnnData objects
```

### `references/plotting_guide.md`

# Scanpy Plotting Guide

Comprehensive guide for creating publication-quality visualizations with scanpy.

## General Plotting Principles

All scanpy plotting functions follow consistent patterns:
- Functions in `sc.pl.*` mirror analysis functions in `sc.tl.*`
- Most accept `color` parameter for gene names or metadata columns
- Prefer `sc.settings.autosave = True` and `sc.settings.figdir` for saving (the per-plot `save=` parameter is deprecated in scanpy 1.12)
- Multiple plots can be generated in a single call

```python
sc.settings.figdir = './figures/'
sc.settings.autosave = True
sc.settings.file_format_figs = 'pdf'
```

## Essential Quality Control Plots

### Visualize QC Metrics

```python
# Violin plots for QC metrics
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True, save='_qc_violin.pdf')

# Scatter plots to identify outliers
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt', save='_qc_mt.pdf')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts', save='_qc_genes.pdf')

# Highest expressing genes
sc.pl.highest_expr_genes(adata, n_top=20, save='_highest_expr.pdf')
```

### Post-filtering QC

```python
# Compare before and after filtering
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts'],
             groupby='sample', save='_post_filter.pdf')
```

## Dimensionality Reduction Visualizations

### PCA Plots

```python
# Basic PCA
sc.pl.pca(adata, color='leiden', save='_pca.pdf')

# PCA colored by gene expression
sc.pl.pca(adata, color=['gene1', 'gene2', 'gene3'], save='_pca_genes.pdf')

# Variance ratio plot (elbow plot)
sc.pl.pca_variance_ratio(adata, log=True, n_pcs=50, save='_variance.pdf')

# PCA loadings
sc.pl.pca_loadings(adata, components=[1, 2, 3], save='_loadings.pdf')
```

### UMAP Plots

```python
# Basic UMAP with clusters
sc.pl.umap(adata, color='leiden', legend_loc='on data', save='_umap_leiden.pdf')

# UMAP colored by multiple variables
sc.pl.umap(adata, color=['leiden', 'cell_type', 'batch'],
           save='_umap_multi.pdf')

# UMAP with gene expression
sc.pl.umap(adata, color=['CD3D', 'CD14', 'MS4A1'],
           use_raw=False, save='_umap_genes.pdf')

# Customize appearance
sc.pl.umap(adata, color='leiden',
           palette='Set2',
           size=50,
           alpha=0.8,
           frameon=False,
           title='Cell Types',
           save='_umap_custom.pdf')
```

### t-SNE Plots

```python
# t-SNE with clusters
sc.pl.tsne(adata, color='leiden', legend_loc='right margin', save='_tsne.pdf')

# Multiple t-SNE perplexities (if computed)
sc.pl.tsne(adata, color='leiden', save='_tsne_default.pdf')
```

## Clustering Visualizations

### Basic Cluster Plots

```python
# UMAP with cluster annotations
sc.pl.umap(adata, color='leiden', add_outline=True,
           legend_loc='on data', legend_fontsize=12,
           legend_fontoutline=2, frameon=False,
           save='_clusters.pdf')

# Show cluster proportions
sc.pl.umap(adata, color='leiden', size=50, edges=True,
           edges_width=0.1, save='_clusters_edges.pdf')
```

### Cluster Comparison

```python
# Compare clustering resolutions
sc.pl.umap(adata, color=['leiden_0.3', 'leiden_0.5', 'leiden_0.8'],
           save='_cluster_comparison.pdf')

# Cluster dendrogram
sc.tl.dendrogram(adata, groupby='leiden')
sc.pl.dendrogram(adata, groupby='leiden', save='_dendrogram.pdf')
```

## Marker Gene Visualizations

### Ranked Marker Genes

```python
# Overview of top markers per cluster
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False,
                        save='_marker_overview.pdf')

# Heatmap of top markers
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10, groupby='leiden',
                                 show_gene_labels=True,
                                 save='_marker_heatmap.pdf')

# Dot plot of markers
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5,
                                 save='_marker_dotplot.pdf')

# Stacked violin plots
sc.pl.rank_genes_groups_stacked_violin(adata, n_genes=5,
                                        save='_marker_violin.pdf')

# Matrix plot
sc.pl.rank_genes_groups_matrixplot(adata, n_genes=5,
                                    save='_marker_matrix.pdf')
```

### Specific Gene Expression

```python
# Violin plots for specific genes
marker_genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7', 'FCGR3A']
sc.pl.violin(adata, keys=marker_genes, groupby='leiden',
             save='_markers_violin.pdf')

# Dot plot for curated markers
sc.pl.dotplot(adata, var_names=marker_genes, groupby='leiden',
              save='_markers_dotplot.pdf')

# Heatmap for specific genes
sc.pl.heatmap(adata, var_names=marker_genes, groupby='leiden',
              swap_axes=True, save='_markers_heatmap.pdf')

# Stacked violin for gene sets
sc.pl.stacked_violin(adata, var_names=marker_genes, groupby='leiden',
                     save='_markers_stacked.pdf')
```

### Gene Expression on Embeddings

```python
# Multiple genes on UMAP
genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7']
sc.pl.umap(adata, color=genes, cmap='viridis',
           save='_umap_markers.pdf')

# Gene expression with custom colormap
sc.pl.umap(adata, color='CD3D', cmap='Reds',
           vmin=0, vmax=3, save='_umap_cd3d.pdf')
```

## Trajectory and Pseudotime Visualizations

### PAGA Plots

```python
# PAGA graph
sc.pl.paga(adata, color='leiden', save='_paga.pdf')

# PAGA with gene expression
sc.pl.paga(adata, color=['leiden', 'dpt_pseudotime'],
           save='_paga_pseudotime.pdf')

# PAGA overlaid on UMAP
sc.pl.umap(adata, color='leiden', save='_umap_with_paga.pdf',
           edges=True, edges_color='gray')
```

### Pseudotime Plots

```python
# DPT pseudotime on UMAP
sc.pl.umap(adata, color='dpt_pseudotime', save='_umap_dpt.pdf')

# Gene expression along pseudotime
sc.pl.dpt_timeseries(adata, save='_dpt_timeseries.pdf')

# Heatmap ordered by pseudotime
sc.pl.heatmap(adata, var_names=genes, groupby='leiden',
              use_raw=False, show_gene_labels=True,
              save='_pseudotime_heatmap.pdf')
```

## Advanced Visualizations

### Tracks Plot (Gene Expression Trends)

```python
# Show gene expression across cell types
sc.pl.tracksplot(adata, var_names=marker_genes, groupby='leiden',
                 save='_tracks.pdf')
```

### Correlation Matrix

```python
# Correlation between clusters
sc.pl.correlation_matrix(adata, groupby='leiden',
                         save='_correlation.pdf')
```

### Embedding Density

```python
# Cell density on UMAP
sc.tl.embedding_density(adata, basis='umap', groupby='cell_type')
sc.pl.embedding_density(adata, basis='umap', key='umap_density_cell_type',
                        save='_density.pdf')
```

## Multi-Panel Figures

### Creating Panel Figures

```python
import matplotlib.pyplot as plt

# Create multi-panel figure
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

# Plot on specific axes
sc.pl.umap(adata, color='leiden', ax=axes[0, 0], show=False)
sc.pl.umap(adata, color='CD3D', ax=axes[0, 1], show=False)
sc.pl.umap(adata, color='CD14', ax=axes[1, 0], show=False)
sc.pl.umap(adata, color='MS4A1', ax=axes[1, 1], show=False)

plt.tight_layout()
plt.savefig('figures/multi_panel.pdf')
plt.show()
```

## Publication-Quality Customization

### High-Quality Settings

```python
# Set publication-quality defaults
sc.settings.set_figure_params(dpi=300, frameon=False, figsize=(5, 5),
                               facecolor='white')

# Vector graphics output
sc.settings.figdir = './figures/'
sc.settings.file_format_figs = 'pdf'  # or 'svg'
```

### Custom Color Palettes

```python
# Use custom colors
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
sc.pl.umap(adata, color='leiden', palette=custom_colors,
           save='_custom_colors.pdf')

# Continuous color maps
sc.pl.umap(adata, color='CD3D', cmap='viridis', save='_viridis.pdf')
sc.pl.umap(adata, color='CD3D', cmap='RdBu_r', save='_rdbu.pdf')
```

### Remove Axes and Frames

```python
# Clean plot without axes
sc.pl.umap(adata, color='leiden', frameon=False,
           save='_clean.pdf')

# No legend
sc.pl.umap(adata, color='leiden', legend_loc=None,
           save='_no_legend.pdf')
```

## Exporting Plots

### Save via Settings (recommended)

```python
sc.settings.figdir = './figures/'
sc.settings.autosave = True
sc.settings.file_format_figs = 'pdf'

sc.pl.umap(adata, color='leiden')  # Saves to figures/umap.pdf
```

The per-plot `save=` parameter still works but is deprecated in scanpy 1.12.

### Manual Saving

```python
import matplotlib.pyplot as plt
fig = sc.pl.umap(adata, color='leiden', show=False, return_fig=True)
fig.savefig('figures/my_umap.pdf', dpi=300, bbox_inches='tight')
```

### Batch Export

```python
genes = ['CD3D', 'CD14', 'MS4A1']
for gene in genes:
    sc.pl.umap(adata, color=gene)  # Each saved via autosave
```

## Common Customization Parameters

### Layout Parameters
- `figsize`: Figure size (width, height)
- `frameon`: Show frame around plot
- `title`: Plot title
- `legend_loc`: 'right margin', 'on data', 'best', or None
- `legend_fontsize`: Font size for legend
- `size`: Point size

### Color Parameters
- `color`: Variable(s) to color by
- `palette`: Color palette (e.g., 'Set1', 'viridis')
- `cmap`: Colormap for continuous variables
- `vmin`, `vmax`: Color scale limits
- `use_raw`: Use raw counts for gene expression

### Saving Parameters
- `show`: Whether to display plot
- `dpi`: Resolution for raster formats
- Use `sc.settings.autosave` + `sc.settings.figdir` instead of deprecated `save=`

## Tips for Publication Figures

1. **Use vector formats**: PDF or SVG for scalable graphics
2. **High DPI**: Set dpi=300 or higher for raster images
3. **Consistent styling**: Use the same color palette across figures
4. **Clear labels**: Ensure gene names and cell types are readable
5. **White background**: Use `facecolor='white'` for publications
6. **Remove clutter**: Set `frameon=False` for cleaner appearance
7. **Legend placement**: Use 'on data' for compact figures
8. **Color blind friendly**: Consider palettes like 'colorblind' or 'Set2'

### `references/r_interop.md`

# R Interoperability for Scanpy

Many single-cell datasets arrive as R objects (`.rds`, `.RData`, Seurat, or SingleCellExperiment) even when the downstream analysis should happen in Scanpy. Agents should convert these inputs to AnnData `.h5ad` first, then continue with normal Scanpy workflows.

## Operating Principles

1. **Do not parse Seurat `.rds` directly in Python.** Use R to deserialize R objects and write `.h5ad`.
2. **Prefer `.h5ad` as the Python handoff format.** After conversion, all QC, clustering, plotting, and exports should use Scanpy/AnnData.
3. **Inspect before converting.** Determine whether the R object is Seurat, SingleCellExperiment, or a list/container; do not assume from the filename.
4. **Preserve raw counts and metadata.** Keep cell metadata (`obs`), gene metadata (`var`), raw counts/layers, and dimensional reductions when available.
5. **Use noninteractive commands.** Agents should use `Rscript -e` or script files, set CRAN repos explicitly, and pass `ask = FALSE`, `update = FALSE` for Bioconductor installs.

## Detect R and the Platform

Use these checks before installing anything:

```bash
uname -s 2>/dev/null || true
command -v Rscript || command -v R || true
Rscript --version 2>/dev/null || R --version 2>/dev/null || true
```

On Windows from PowerShell:

```powershell
Get-Command Rscript -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
Get-Command R -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
```

If Git Bash cannot find R on Windows, query PowerShell or common install paths:

```powershell
Get-ChildItem "C:\Program Files\R" -Filter Rscript.exe -Recurse -ErrorAction SilentlyContinue |
  Select-Object -First 1 -ExpandProperty FullName
```

Then call the discovered executable with quotes, for example:

```bash
"/c/Program Files/R/R-4.6.0/bin/Rscript.exe" --version
```

## Install R by OS

Prefer existing system package managers. If installation requires GUI approval, admin credentials, or an unavailable package manager, stop and report the blocker.

### macOS

Use Homebrew when available:

```bash
brew install --cask r
```

For packages with compiled code, install command-line build tools if the system asks for compilers:

```bash
xcode-select --install
```

Some R packages with Fortran code may require the CRAN macOS toolchain from `https://mac.R-project.org/tools/`. Prefer CRAN binary packages where possible to avoid compiler work.

### Linux

Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y \
  r-base r-base-dev build-essential gfortran \
  libcurl4-openssl-dev libssl-dev libxml2-dev libhdf5-dev \
  libharfbuzz-dev libfribidi-dev libfontconfig1-dev libfreetype6-dev \
  libpng-dev libtiff5-dev libjpeg-dev
```

Fedora/RHEL-like systems:

```bash
sudo dnf install -y \
  R R-devel gcc gcc-c++ gcc-gfortran make \
  libcurl-devel openssl-devel libxml2-devel hdf5-devel \
  harfbuzz-devel fribidi-devel fontconfig-devel freetype-devel \
  libpng-devel libtiff-devel libjpeg-turbo-devel
```

If `sudo` is unavailable, use a managed environment such as Conda/Mamba if already present:

```bash
conda install -c conda-forge r-base r-essentials
```

### Windows

Use `winget` from PowerShell when available:

```powershell
winget install --id RProject.R -e
```

Install Rtools only if packages need compilation:

```powershell
winget install --id RProject.Rtools -e
```

After installation, open a new shell or locate `Rscript.exe` under `C:\Program Files\R\R-*\bin\`. In Git Bash, call Windows executables through quoted paths or PowerShell; do not assume `/usr/bin/R` exists.

## Install Conversion Packages

Create a project-local R library when you do not want to alter the user's global R library:

```bash
mkdir -p .r-lib
export R_LIBS_USER="$PWD/.r-lib"
```

Install the core conversion stack:

```bash
Rscript -e 'options(repos = c(CRAN = "https://cloud.r-project.org")); install.packages(c("BiocManager", "remotes"), Ncpus = max(1, parallel::detectCores() - 1)); BiocManager::install(c("SingleCellExperiment", "zellkonverter"), ask = FALSE, update = FALSE)'
```

Install Seurat support only when the input is a Seurat object:

```bash
Rscript -e 'options(repos = c(CRAN = "https://cloud.r-project.org")); install.packages(c("Seurat", "SeuratObject"), Ncpus = max(1, parallel::detectCores() - 1))'
```

Optional SeuratDisk fallback for h5Seurat-to-h5ad conversion:

```bash
Rscript -e 'options(repos = c(CRAN = "https://cloud.r-project.org")); if (!requireNamespace("remotes", quietly = TRUE)) install.packages("remotes"); remotes::install_github("mojaveazure/seurat-disk", upgrade = "never")'
```

Avoid `sceasy` as the first choice. It can work, but it depends on `reticulate`/Python environment coupling and has more version-specific failure modes. Use it only after `zellkonverter` and SeuratDisk paths fail.

## Inspect R Inputs

For `.rds` files:

```bash
Rscript -e 'obj <- readRDS("input.rds"); print(class(obj)); if (is.list(obj) && !is.data.frame(obj)) print(names(obj))'
```

For `.RData`/`.rda` files:

```bash
Rscript -e 'e <- new.env(parent = emptyenv()); load("input.RData", envir = e); print(ls(e)); print(lapply(as.list(e), class))'
```

If multiple objects are present, choose the object with class `Seurat`, `SingleCellExperiment`, or `SummarizedExperiment`. If there is ambiguity, ask the user which object to convert.

## Convert `.rds` to `.h5ad`

Use this script as the default conversion path. It handles SingleCellExperiment directly and converts Seurat objects through SingleCellExperiment before writing `.h5ad`.

```r
#!/usr/bin/env Rscript

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("Usage: Rscript convert_rds_to_h5ad.R input.rds output.h5ad [assay]", call. = FALSE)
}

input <- normalizePath(args[[1]], mustWork = TRUE)
output <- args[[2]]
assay <- if (length(args) >= 3) args[[3]] else NULL

options(repos = c(CRAN = "https://cloud.r-project.org"))

ensure_pkg <- function(pkg, bioc = FALSE) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    if (bioc) {
      if (!requireNamespace("BiocManager", quietly = TRUE)) {
        install.packages("BiocManager")
      }
      BiocManager::install(pkg, ask = FALSE, update = FALSE)
    } else {
      install.packages(pkg)
    }
  }
}

ensure_pkg("SingleCellExperiment", bioc = TRUE)
ensure_pkg("SummarizedExperiment", bioc = TRUE)
ensure_pkg("zellkonverter", bioc = TRUE)

obj <- readRDS(input)
message("Input classes: ", paste(class(obj), collapse = ", "))

if (inherits(obj, "SingleCellExperiment")) {
  sce <- obj
} else if (inherits(obj, "Seurat")) {
  ensure_pkg("Seurat")
  ensure_pkg("SeuratObject")

  obj <- Seurat::UpdateSeuratObject(obj, verbose = FALSE)
  if (is.null(assay)) {
    assay <- SeuratObject::DefaultAssay(obj)
  }

  if ("JoinLayers" %in% getNamespaceExports("SeuratObject")) {
    obj <- tryCatch(SeuratObject::JoinLayers(obj, assay = assay), error = function(e) obj)
  }

  sce <- Seurat::as.SingleCellExperiment(obj, assay = assay)
} else {
  stop("Unsupported RDS class: ", paste(class(obj), collapse = ", "), call. = FALSE)
}

x_name <- if ("counts" %in% SummarizedExperiment::assayNames(sce)) "counts" else NULL
zellkonverter::writeH5AD(sce, output, X_name = x_name)
message("Wrote: ", normalizePath(output, mustWork = FALSE))
```

Run it:

```bash
Rscript convert_rds_to_h5ad.R input.rds output.h5ad
```

If the Seurat object has multiple assays and the user specified one, pass it explicitly:

```bash
Rscript convert_rds_to_h5ad.R input.rds output.h5ad RNA
```

## SeuratDisk Fallback

If Seurat-to-SingleCellExperiment conversion fails, try SeuratDisk:

```r
library(Seurat)
library(SeuratDisk)

obj <- readRDS("input.rds")
obj <- UpdateSeuratObject(obj)
DefaultAssay(obj) <- "RNA"
SaveH5Seurat(obj, filename = "output.h5Seurat", overwrite = TRUE)
Convert("output.h5Seurat", dest = "h5ad", overwrite = TRUE)
```

Be aware that SeuratDisk chooses which assay/layer becomes AnnData `.X` based on the available Seurat slots. If raw counts are essential, validate where counts landed after conversion and copy them into `adata.layers["counts"]` if needed.

## Validate in Python

After conversion, always validate with Scanpy before continuing:

```python
import scanpy as sc

adata = sc.read_h5ad("output.h5ad")
adata.var_names_make_unique()

print(adata)
print(adata.obs.head())
print(adata.var.head())
print("layers:", list(adata.layers.keys()))
print("obsm:", list(adata.obsm.keys()))

adata.write_h5ad("output.validated.h5ad", compression="gzip")
```

If the user requested metadata and expression exports:

```python
import scipy.io as sio

adata.obs.to_csv("cell_metadata.csv")
adata.var.to_csv("gene_metadata.csv")
sio.mmwrite("expression_matrix.mtx", adata.X)
```

For very large datasets, avoid dense CSV expression exports unless the user explicitly asks. Prefer `.h5ad`, Matrix Market (`.mtx`), or sparse-aware downstream analysis.

## Troubleshooting

- **`Rscript: command not found`**: R is not installed or not on PATH. Use the OS-specific install steps above, then reopen the shell or call the full `Rscript` path.
- **Windows Git Bash cannot find R**: Use PowerShell to locate `Rscript.exe` and invoke the quoted path from Git Bash.
- **Package compilation fails**: Install system build dependencies (`r-base-dev`, compilers, HDF5/libcurl/OpenSSL/XML headers, Rtools on Windows, or macOS command-line tools).
- **Bioconductor version mismatch**: Upgrade R when possible. Bioconductor packages are tied to compatible R releases; avoid forcing incompatible versions.
- **Seurat v5 layer issues**: Try `SeuratObject::JoinLayers()` before conversion, pass the assay explicitly, or use SeuratDisk fallback.
- **Counts missing or normalized data in `.X`**: Inspect `adata.layers`, `adata.raw`, and value ranges. Keep raw counts in `adata.layers["counts"]` before normalization if available.
- **Memory pressure**: Convert on a machine with enough RAM, avoid dense exports, and write compressed `.h5ad` checkpoints after successful conversion.

## Sources Checked

- R Project and CRAN installation pages: `https://www.r-project.org/`, `https://cran.r-project.org/bin/macosx`, `https://cran.r-project.org/bin/windows/base/rw-FAQ.html`
- Bioconductor install guidance and BiocManager documentation: `https://www.bioconductor.org/install/`, `https://cran.r-project.org/web/packages/BiocManager/vignettes/BiocManager.html`
- zellkonverter project and package documentation: `https://www.bioconductor.org/packages/release/bioc/html/zellkonverter.html`, `https://github.com/theislab/zellkonverter`
- SeuratDisk documentation and repository: `https://mojaveazure.github.io/seurat-disk/`, `https://github.com/mojaveazure/seurat-disk`
- sceasy repository for fallback context: `https://github.com/cellgeni/sceasy`

### `references/standard_workflow.md`

# Standard Scanpy Workflow for Single-Cell Analysis

This document outlines the standard workflow for analyzing single-cell RNA-seq data using scanpy.

## Complete Analysis Pipeline

### 1. Data Loading and Initial Setup

```python
import scanpy as sc
import pandas as pd
import numpy as np

# Configure scanpy settings
sc.settings.verbosity = 3  # verbosity: errors (0), warnings (1), info (2), hints (3)
sc.settings.set_figure_params(dpi=80, facecolor='white')

# Load data (various formats)
adata = sc.read_10x_mtx('path/to/data/')  # For 10X data
# adata = sc.read_h5ad('path/to/data.h5ad')  # For h5ad format
# adata = sc.read_csv('path/to/data.csv')  # For CSV format
```

### 2. Quality Control (QC)

```python
# Calculate QC metrics
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Common filtering thresholds (adjust based on dataset)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# Remove cells with high mitochondrial content
adata = adata[adata.obs.pct_counts_mt < 5, :]

# Optional: doublet detection (run on raw counts before normalization)
# sc.pp.scrublet(adata)
# adata = adata[~adata.obs['predicted_doublet'], :].copy()

# Visualize QC metrics
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

### 3. Normalization

```python
# Normalize to 10,000 counts per cell
sc.pp.normalize_total(adata, target_sum=1e4)

# Log-transform the data
sc.pp.log1p(adata)

# Store normalized data in raw for later use
adata.raw = adata
```

### 4. Feature Selection

```python
# Identify highly variable genes
sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)

# Visualize highly variable genes
sc.pl.highly_variable_genes(adata)

# Subset to highly variable genes
adata = adata[:, adata.var.highly_variable]
```

### 5. Scaling and Regression

```python
# Regress out effects of total counts per cell and percent mitochondrial genes
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])

# Scale data to unit variance and zero mean
sc.pp.scale(adata, max_value=10)
```

### 6. Dimensionality Reduction

```python
# Principal Component Analysis (PCA)
sc.tl.pca(adata, svd_solver='arpack')

# Visualize PCA results
sc.pl.pca(adata, color='CST3')
sc.pl.pca_variance_ratio(adata, log=True)

# Computing neighborhood graph
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)

# UMAP for visualization
sc.tl.umap(adata)

# t-SNE (alternative to UMAP)
# sc.tl.tsne(adata)
```

### 7. Clustering

```python
# Leiden clustering
sc.tl.leiden(adata, resolution=0.5)

# Visualize clustering results
sc.pl.umap(adata, color=['leiden'], legend_loc='on data')
```

### 8. Marker Gene Identification

`rank_genes_groups` is appropriate for exploratory cluster markers. Per-cell tests produce inflated p-values; for rigorous DE between conditions, pseudobulk with `sc.get.aggregate()` and use pydeseq2.

```python
# Find marker genes for each cluster (exploratory)
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')

# Visualize top marker genes
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False)

# Get marker gene dataframe
marker_genes = sc.get.rank_genes_groups_df(adata, group='0')

# Visualize specific markers
sc.pl.umap(adata, color=['leiden', 'CST3', 'NKG7'])
```

### 9. Cell Type Annotation

```python
# Manual annotation based on marker genes
cluster_annotations = {
    '0': 'CD4 T cells',
    '1': 'CD14+ Monocytes',
    '2': 'B cells',
    '3': 'CD8 T cells',
    # ... add more annotations
}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_annotations)

# Visualize annotated cell types
sc.pl.umap(adata, color='cell_type', legend_loc='on data')
```

### 10. Saving Results

```python
# Save the processed AnnData object
adata.write('results/processed_data.h5ad')

# Export results to CSV
adata.obs.to_csv('results/cell_metadata.csv')
adata.var.to_csv('results/gene_metadata.csv')
```

## Additional Analysis Options

### Trajectory Inference

```python
# PAGA (Partition-based graph abstraction)
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color=['leiden'])

# Diffusion pseudotime (DPT)
adata.uns['iroot'] = np.flatnonzero(adata.obs['leiden'] == '0')[0]
sc.tl.dpt(adata)
sc.pl.umap(adata, color=['dpt_pseudotime'])
```

### Differential Expression Between Conditions

Pseudobulk by sample and cell type, then run proper DE (e.g., pydeseq2):

```python
pb = sc.get.aggregate(
    adata,
    by=['sample', 'cell_type'],
    func='sum',
    layer='counts',
)
# Export pb and use pydeseq2 for condition comparisons
```

For quick exploratory comparisons only:

```python
sc.tl.rank_genes_groups(adata, groupby='condition', groups=['treated'],
                         reference='control', method='wilcoxon')
sc.pl.rank_genes_groups(adata, groups=['treated'])
```

### Gene Set Scoring

```python
# Score cells for gene set expression
gene_set = ['CD3D', 'CD3E', 'CD3G']
sc.tl.score_genes(adata, gene_set, score_name='T_cell_score')
sc.pl.umap(adata, color='T_cell_score')
```

## Common Parameters to Adjust

- **QC thresholds**: `min_genes`, `min_cells`, `pct_counts_mt` - depends on dataset quality
- **Normalization target**: Usually 1e4, but can be adjusted
- **HVG parameters**: Affects feature selection stringency
- **PCA components**: Check variance ratio plot to determine optimal number
- **Clustering resolution**: Higher values give more clusters (typically 0.4-1.2)
- **n_neighbors**: Affects granularity of UMAP and clustering (typically 10-30)

## Best Practices

1. Always visualize QC metrics before filtering
2. Save raw counts before normalization (`adata.raw = adata`)
3. Use Leiden clustering (`sc.tl.louvain` deprecated in scanpy 1.12)
4. Try multiple clustering resolutions to find optimal granularity
5. Validate cell type annotations with known marker genes
6. Pseudobulk for rigorous DE; treat `rank_genes_groups` p-values as exploratory
7. Save intermediate results at key steps

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""
Shared helpers for the scanpy script toolkit.

Every CLI script in this directory imports from this module so that data
loading, saving, figure configuration, and logging behave consistently.
This file is NOT a CLI itself; import it:

    from _common import load_anndata, save_anndata, configure_scanpy, info
"""

import os
import sys


def info(msg):
    """Print a progress message to stderr-friendly stdout with a marker."""
    print(f"[scanpy] {msg}", flush=True)


def die(msg, code=1):
    """Print an error and exit."""
    print(f"Error: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def _import_scanpy():
    try:
        import scanpy as sc  # noqa: F401
        return sc
    except ImportError:
        die('scanpy not installed. Install with: uv pip install "scanpy[leiden]"')


def configure_scanpy(figdir="figures", dpi=120, verbosity=1, autosave=False,
                     file_format="png"):
    """Apply consistent scanpy settings and return the scanpy module.

    Note: autosave is left off by default because the toolkit scripts pass
    explicit ``save=`` suffixes to plotting calls for predictable filenames.
    """
    sc = _import_scanpy()
    sc.settings.verbosity = verbosity
    sc.settings.set_figure_params(dpi=dpi, facecolor="white")
    sc.settings.figdir = figdir
    sc.settings.file_format_figs = file_format
    if autosave:
        sc.settings.autosave = True
    os.makedirs(figdir, exist_ok=True)
    return sc


def load_anndata(path, var_names="gene_symbols"):
    """Load an AnnData object, dispatching on the file extension / layout.

    Supported inputs:
      * ``.h5ad``                  -> sc.read_h5ad
      * ``.h5`` (10x CellRanger)   -> sc.read_10x_h5
      * ``.csv`` / ``.tsv`` / ``.txt`` -> sc.read_csv / read_text
      * ``.loom``                  -> sc.read_loom
      * ``.mtx``                   -> sc.read (matrix market)
      * a directory                -> sc.read_10x_mtx (10x mtx folder)
    """
    sc = _import_scanpy()
    if not os.path.exists(path):
        die(f"input not found: {path}")

    lower = path.lower()
    if os.path.isdir(path):
        info(f"Reading 10x mtx directory: {path}")
        return sc.read_10x_mtx(path, var_names=var_names)
    if lower.endswith(".h5ad"):
        return sc.read_h5ad(path)
    if lower.endswith(".h5"):
        info("Reading 10x HDF5 (.h5)")
        return sc.read_10x_h5(path)
    if lower.endswith(".loom"):
        return sc.read_loom(path)
    if lower.endswith(".csv"):
        return sc.read_csv(path)
    if lower.endswith((".tsv", ".txt")):
        return sc.read_text(path)
    if lower.endswith(".mtx") or lower.endswith(".mtx.gz"):
        return sc.read(path)
    die(f"unrecognized input format: {path}")


def save_anndata(adata, path):
    """Write an AnnData object to .h5ad, creating parent dirs as needed."""
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    adata.write_h5ad(path)
    info(f"Wrote {path}  ({adata.n_obs} cells x {adata.n_vars} genes)")


def add_io_args(parser, default_output=None):
    """Attach the standard input/output/figdir arguments to an argparse parser."""
    parser.add_argument("input", help="Input file (.h5ad, .h5, .csv, .loom, or 10x mtx dir)")
    parser.add_argument("-o", "--output", default=default_output,
                        help="Output .h5ad path" +
                             (f" (default: {default_output})" if default_output else ""))
    parser.add_argument("--figdir", default="figures",
                        help="Directory for saved figures (default: figures)")
    return parser


def _named_keys(mapping):
    """Named keys of an AnnData mapping, in order.

    anndata >= 0.13 reports an unnamed `None` key on `.layers` standing for X
    itself. Joining that into a string raises TypeError, so filter it out.
    """
    return [key for key in mapping.keys() if isinstance(key, str)]


def summarize(adata):
    """Return a short human-readable summary string of an AnnData object."""
    lines = [f"{adata.n_obs} cells x {adata.n_vars} genes"]
    if len(adata.obs.columns):
        lines.append("obs: " + ", ".join(adata.obs.columns[:20]))
    obsm = _named_keys(adata.obsm)
    if obsm:
        lines.append("obsm: " + ", ".join(obsm))
    layers = _named_keys(adata.layers)
    if layers:
        lines.append("layers: " + ", ".join(layers))
    return "\n".join(lines)
```

### `scripts/annotate.py`

```python
#!/usr/bin/env python3
"""
Annotate clusters with cell-type labels from a mapping file.

Maps a cluster column (e.g. leiden) to cell-type names using a JSON or CSV
mapping, writes the labels into a new obs column, and saves a UMAP and dotplot.

The mapping file is one of:
  * JSON  : {"0": "CD4 T cells", "1": "B cells", ...}
  * CSV    : two columns ``cluster,cell_type``

Optionally provide a marker-gene JSON to draw a reference dotplot that helps
decide the mapping:
  {"T cells": ["CD3D","CD3E"], "B cells": ["MS4A1","CD79A"]}

Examples:
    python annotate.py clustered.h5ad -o annotated.h5ad --mapping celltypes.json
    python annotate.py clustered.h5ad -o annotated.h5ad --mapping map.csv --cluster-key leiden
    python annotate.py clustered.h5ad --markers markers.json --cluster-key leiden   # dotplot only
"""

import argparse
import json
import os

from _common import add_io_args, configure_scanpy, die, info, load_anndata, save_anndata


def load_mapping(path):
    if path.lower().endswith(".json"):
        with open(path) as fh:
            return {str(k): v for k, v in json.load(fh).items()}
    import pandas as pd
    df = pd.read_csv(path)
    if df.shape[1] < 2:
        die("CSV mapping needs at least two columns: cluster,cell_type")
    return {str(k): v for k, v in zip(df.iloc[:, 0], df.iloc[:, 1])}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="annotated.h5ad")
    p.add_argument("--cluster-key", default="leiden", help="obs column with clusters (default leiden)")
    p.add_argument("--mapping", default=None, help="JSON or CSV cluster->cell_type mapping")
    p.add_argument("--label-key", default="cell_type", help="New obs column name (default cell_type)")
    p.add_argument("--markers", default=None,
                   help="JSON of {cell_type: [genes]} to draw a reference dotplot")
    p.add_argument("--no-plots", action="store_true", help="Skip plots")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    if args.cluster_key not in adata.obs.columns:
        die(f"cluster key '{args.cluster_key}' not in obs: {list(adata.obs.columns)}")

    if args.markers:
        with open(args.markers) as fh:
            marker_dict = json.load(fh)
        present = {ct: [g for g in genes if g in (adata.raw.var_names if adata.raw is not None else adata.var_names)]
                   for ct, genes in marker_dict.items()}
        present = {ct: g for ct, g in present.items() if g}
        if present and not args.no_plots:
            sc.pl.dotplot(adata, present, groupby=args.cluster_key,
                          use_raw=adata.raw is not None, show=False, save="_marker_reference.png")
            info("Wrote marker reference dotplot")

    if args.mapping:
        mapping = load_mapping(args.mapping)
        adata.obs[args.label_key] = (
            adata.obs[args.cluster_key].astype(str).map(mapping).fillna("Unknown").astype("category")
        )
        info(f"Annotated '{args.label_key}': "
             + ", ".join(f"{k}={v}" for k, v in adata.obs[args.label_key].value_counts().items()))
        if not args.no_plots:
            sc.pl.umap(adata, color=args.label_key, legend_loc="on data",
                       show=False, save="_celltypes.png")
        save_anndata(adata, args.output)
    elif not args.markers:
        die("provide --mapping (to annotate) and/or --markers (for a reference dotplot)")


if __name__ == "__main__":
    main()
```

### `scripts/batch_correct.py`

```python
#!/usr/bin/env python3
"""
Batch correction / integration across samples.

Supports three methods:
  * harmony  : corrects the PCA embedding -> writes obsm['X_pca_harmony'].
               Fast, recommended default. Needs harmonypy (uv pip install harmonypy).
               Follow with: reduce_dimensions.py --use-rep X_pca_harmony
  * bbknn     : batch-balanced kNN graph (replaces sc.pp.neighbors). Then cluster directly.
               Needs bbknn (uv pip install bbknn).
  * combat    : corrects the expression matrix in place (sc.pp.combat). Built into scanpy.

Run on a normalized object that already has PCA (harmony/bbknn) computed.

Examples:
    python batch_correct.py reduced.h5ad -o integrated.h5ad --method harmony --batch-key sample
    python batch_correct.py reduced.h5ad -o integrated.h5ad --method bbknn --batch-key sample
    python batch_correct.py normalized.h5ad -o integrated.h5ad --method combat --batch-key batch
"""

import argparse

from _common import add_io_args, configure_scanpy, die, info, load_anndata, save_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="integrated.h5ad")
    p.add_argument("--method", default="harmony", choices=["harmony", "bbknn", "combat"])
    p.add_argument("--batch-key", required=True, help="obs column identifying batches")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    if args.batch_key not in adata.obs.columns:
        die(f"batch key '{args.batch_key}' not in obs: {list(adata.obs.columns)}")

    if args.method == "harmony":
        if "X_pca" not in adata.obsm:
            sc.tl.pca(adata, svd_solver="arpack")
        try:
            sc.external.pp.harmony_integrate(adata, args.batch_key)
        except ImportError:
            die("harmonypy not installed. Install with: uv pip install harmonypy")
        info("Wrote obsm['X_pca_harmony']. Next: "
             "reduce_dimensions.py --use-rep X_pca_harmony")
    elif args.method == "bbknn":
        if "X_pca" not in adata.obsm:
            sc.tl.pca(adata, svd_solver="arpack")
        try:
            sc.external.pp.bbknn(adata, batch_key=args.batch_key)
        except ImportError:
            die("bbknn not installed. Install with: uv pip install bbknn")
        sc.tl.umap(adata)
        info("Built batch-balanced graph + UMAP. Next: cluster.py")
    elif args.method == "combat":
        sc.pp.combat(adata, key=args.batch_key)
        info("Corrected expression matrix with ComBat. Re-run reduce_dimensions.py.")

    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/cluster.py`

```python
#!/usr/bin/env python3
"""
Leiden clustering on a precomputed neighborhood graph.

Runs Leiden at one or more resolutions and writes a UMAP colored by each
clustering. Requires that ``sc.pp.neighbors`` has already been run
(use reduce_dimensions.py first).

Examples:
    python cluster.py reduced.h5ad -o clustered.h5ad --resolution 0.5
    python cluster.py reduced.h5ad -o clustered.h5ad --resolution 0.3 0.5 0.8 1.0
    python cluster.py reduced.h5ad -o clustered.h5ad --algorithm louvain
"""

import argparse

from _common import add_io_args, configure_scanpy, die, info, load_anndata, save_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="clustered.h5ad")
    p.add_argument("--resolution", type=float, nargs="+", default=[0.5],
                   help="One or more resolutions (default 0.5). Higher = more clusters")
    p.add_argument("--algorithm", default="leiden", choices=["leiden", "louvain"],
                   help="Clustering algorithm (default leiden)")
    p.add_argument("--key", default=None,
                   help="obs key for the result (single resolution only; "
                        "default '<algorithm>'). Multiple resolutions use '<algorithm>_<res>'")
    p.add_argument("--no-plots", action="store_true", help="Skip UMAP plots")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    if "neighbors" not in adata.uns:
        die("no neighborhood graph found. Run reduce_dimensions.py first.")

    cluster_fn = sc.tl.leiden if args.algorithm == "leiden" else sc.tl.louvain
    keys = []
    for res in args.resolution:
        if len(args.resolution) == 1:
            key = args.key or args.algorithm
        else:
            key = f"{args.algorithm}_{res}"
        # flavor='igraph' is the scanpy 1.12 default-recommended Leiden backend.
        kwargs = {"resolution": res, "key_added": key}
        if args.algorithm == "leiden":
            kwargs.update(flavor="igraph", n_iterations=2, directed=False)
        cluster_fn(adata, **kwargs)
        n = adata.obs[key].nunique()
        info(f"{key}: {n} clusters at resolution {res}")
        keys.append(key)

    if not args.no_plots:
        sc.pl.umap(adata, color=keys, legend_loc="on data",
                   show=False, save="_clusters.png")

    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/convert.py`

```python
#!/usr/bin/env python3
"""
Load any supported single-cell format and write it as .h5ad.

Convenience wrapper to get 10x mtx folders, 10x .h5, CSV/TSV, loom, or mtx
files into AnnData .h5ad once, so later steps all read a single fast format.
For R-native files (.rds / Seurat / SingleCellExperiment), see
references/r_interop.md — those must be converted with R first.

Examples:
    python convert.py filtered_feature_bc_matrix/ -o data.h5ad
    python convert.py raw_counts.csv -o data.h5ad --transpose
    python convert.py matrix.h5 -o data.h5ad
"""

import argparse

from _common import add_io_args, configure_scanpy, info, load_anndata, save_anndata, summarize


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="data.h5ad")
    p.add_argument("--transpose", action="store_true",
                   help="Transpose after loading (use if matrix is genes x cells)")
    p.add_argument("--make-unique", action="store_true",
                   help="Make var (gene) names unique")
    args = p.parse_args()

    configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    if args.transpose:
        adata = adata.T
        info(f"Transposed -> {adata.n_obs} cells x {adata.n_vars} genes")
    if args.make_unique:
        adata.var_names_make_unique()
    print(summarize(adata))
    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/find_markers.py`

```python
#!/usr/bin/env python3
"""
Rank marker genes per group and export tables + plots.

Runs ``sc.tl.rank_genes_groups`` for a grouping (e.g. leiden clusters), writes
a combined CSV of the top markers per group, per-group CSVs, and the standard
marker plots (rank panel, heatmap, dotplot).

NOTE: per-cell tests inflate significance because cells are not independent.
Use this for EXPLORATORY cluster markers. For rigorous DE between conditions,
use pseudobulk.py + pydeseq2.

Examples:
    python find_markers.py clustered.h5ad -o markers.h5ad
    python find_markers.py clustered.h5ad --groupby leiden --method wilcoxon --n-genes 50
    python find_markers.py clustered.h5ad --csv-dir results/markers --top 10
"""

import argparse
import os

from _common import add_io_args, configure_scanpy, die, info, load_anndata, save_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output=None)
    p.add_argument("--groupby", default="leiden", help="obs column to group by (default leiden)")
    p.add_argument("--method", default="wilcoxon",
                   choices=["wilcoxon", "t-test", "t-test_overestim_var", "logreg"],
                   help="Test method (default wilcoxon)")
    p.add_argument("--n-genes", type=int, default=25, help="Genes shown in plots (default 25)")
    p.add_argument("--top", type=int, default=25, help="Top markers per group in CSV (default 25)")
    p.add_argument("--use-raw", action="store_true",
                   help="Rank on adata.raw (normalized log values) instead of X")
    p.add_argument("--csv-dir", default="results/markers", help="Directory for marker CSVs")
    p.add_argument("--no-plots", action="store_true", help="Skip marker plots")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    if args.groupby not in adata.obs.columns:
        die(f"groupby column '{args.groupby}' not found in obs: {list(adata.obs.columns)}")

    sc.tl.rank_genes_groups(adata, args.groupby, method=args.method,
                            use_raw=args.use_raw if adata.raw is not None else False)

    os.makedirs(args.csv_dir, exist_ok=True)
    groups = list(adata.obs[args.groupby].cat.categories) \
        if hasattr(adata.obs[args.groupby], "cat") else sorted(adata.obs[args.groupby].unique())
    combined = []
    for g in groups:
        df = sc.get.rank_genes_groups_df(adata, group=str(g)).head(args.top)
        df.insert(0, "group", g)
        df.to_csv(os.path.join(args.csv_dir, f"markers_{args.groupby}_{g}.csv"), index=False)
        combined.append(df)
    if combined:
        import pandas as pd
        all_path = os.path.join(args.csv_dir, f"markers_{args.groupby}_all.csv")
        pd.concat(combined, ignore_index=True).to_csv(all_path, index=False)
        info(f"Wrote marker tables to {args.csv_dir}/ ({len(groups)} groups)")

    if not args.no_plots:
        sc.pl.rank_genes_groups(adata, n_genes=args.n_genes, sharey=False,
                                show=False, save="_markers.png")
        sc.pl.rank_genes_groups_dotplot(adata, n_genes=5, show=False, save="_markers_dotplot.png")
        sc.pl.rank_genes_groups_heatmap(adata, n_genes=10, show=False, save="_markers_heatmap.png")

    if args.output:
        save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/inspect_data.py`

```python
#!/usr/bin/env python3
"""
Inspect an AnnData / single-cell file and print a structured summary.

Reports shape, obs/var columns (with dtypes and category counts), layers,
obsm/varm/uns keys, X dtype and value range, and whether the data looks like
raw counts or normalized values. Use this before analysis to understand an
unfamiliar dataset and decide which pipeline steps still need to run.

Examples:
    python inspect_data.py data.h5ad
    python inspect_data.py 10x_dir/
"""

import argparse

import numpy as np

from _common import configure_scanpy, info, load_anndata


def _is_integer_matrix(X, n=10000):
    sub = X[:50] if X.shape[0] > 50 else X
    arr = sub.toarray() if hasattr(sub, "toarray") else np.asarray(sub)
    arr = arr.ravel()[:n]
    if arr.size == 0:
        return False
    return bool(np.all(np.equal(np.mod(arr, 1), 0)))


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Input file (.h5ad, .h5, .csv, .loom, or 10x mtx dir)")
    p.add_argument("--max-cols", type=int, default=40, help="Max obs/var columns to list")
    args = p.parse_args()

    configure_scanpy()
    adata = load_anndata(args.input)

    print("=" * 70)
    print(f"AnnData: {adata.n_obs} cells x {adata.n_vars} genes")
    print("=" * 70)

    X = adata.X
    looks_int = _is_integer_matrix(X)
    xmax = X.max() if not hasattr(X, "toarray") else X.max()
    print(f"\nX dtype={X.dtype}  max={float(xmax):.2f}  "
          f"=> {'raw counts (likely)' if looks_int else 'normalized/log (likely)'}")

    print(f"\nobs columns ({len(adata.obs.columns)}):")
    for c in adata.obs.columns[:args.max_cols]:
        col = adata.obs[c]
        if str(col.dtype) in ("category", "object"):
            nuniq = col.nunique()
            extra = f"  {nuniq} categories" + (f": {list(col.unique()[:8])}" if nuniq <= 8 else "")
        else:
            extra = f"  range=[{col.min():.2f}, {col.max():.2f}]"
        print(f"  - {c} ({col.dtype}){extra}")

    print(f"\nvar columns ({len(adata.var.columns)}): {list(adata.var.columns[:args.max_cols])}")
    print(f"\nlayers: {list(adata.layers.keys())}")
    print(f"obsm: {list(adata.obsm.keys())}")
    print(f"varm: {list(adata.varm.keys())}")
    print(f"uns:  {list(adata.uns.keys())}")
    print(f"raw:  {'present' if adata.raw is not None else 'none'}")

    done = []
    if any(k in adata.obsm for k in ("X_pca",)):
        done.append("PCA")
    if "neighbors" in adata.uns:
        done.append("neighbors")
    if "X_umap" in adata.obsm:
        done.append("UMAP")
    if any(k in adata.obs.columns for k in ("leiden", "louvain")):
        done.append("clustering")
    print("\nPipeline steps already present: " + (", ".join(done) if done else "none"))


if __name__ == "__main__":
    main()
```

### `scripts/plot.py`

```python
#!/usr/bin/env python3
"""
Generate common single-cell plots from a processed AnnData object.

A flexible plotting front-end so the agent doesn't hand-write matplotlib /
scanpy plotting calls. Pick a plot type and the keys/genes to show.

Plot types:
  umap / tsne / pca   : embedding colored by --color obs columns and/or --genes
  violin               : --genes (or QC metrics) split by --groupby
  dotplot / matrixplot / heatmap / tracksplot / stacked_violin : --genes by --groupby

Examples:
    python plot.py annotated.h5ad --kind umap --color leiden cell_type
    python plot.py annotated.h5ad --kind umap --genes CD3D MS4A1 NKG7 --use-raw
    python plot.py annotated.h5ad --kind dotplot --genes CD3D CD14 MS4A1 --groupby cell_type
    python plot.py annotated.h5ad --kind violin --genes CD3D --groupby leiden
"""

import argparse

from _common import configure_scanpy, die, info, load_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Input .h5ad")
    p.add_argument("--kind", required=True,
                   choices=["umap", "tsne", "pca", "violin", "dotplot",
                            "matrixplot", "heatmap", "tracksplot", "stacked_violin"])
    p.add_argument("--color", nargs="+", default=None, help="obs columns to color by")
    p.add_argument("--genes", nargs="+", default=None, help="genes to display")
    p.add_argument("--groupby", default=None, help="obs column to group by (violin/dotplot/...)")
    p.add_argument("--use-raw", action="store_true", help="Use adata.raw (normalized log values)")
    p.add_argument("--figdir", default="figures", help="Figure output directory")
    p.add_argument("--save", default=None, help="Filename suffix (default derived from --kind)")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    # scanpy prepends the plot-function name, so ".png" yields e.g. "umap.png".
    save = args.save or ".png"
    use_raw = args.use_raw and adata.raw is not None

    var_names = adata.raw.var_names if use_raw else adata.var_names
    genes = [g for g in (args.genes or []) if g in var_names]
    if args.genes and len(genes) < len(args.genes):
        missing = set(args.genes) - set(genes)
        info(f"Genes not found (skipped): {sorted(missing)}")

    if args.kind in ("umap", "tsne", "pca"):
        color = (args.color or []) + genes
        if not color:
            die("provide --color and/or --genes for embedding plots")
        fn = {"umap": sc.pl.umap, "tsne": sc.pl.tsne, "pca": sc.pl.pca}[args.kind]
        fn(adata, color=color, use_raw=use_raw, show=False, save=save)
    elif args.kind == "violin":
        keys = genes or [c for c in (args.color or []) if c in adata.obs.columns]
        if not keys:
            die("provide --genes (or obs keys via --color) for violin")
        sc.pl.violin(adata, keys, groupby=args.groupby, use_raw=use_raw,
                     show=False, save=save)
    else:
        if not genes or not args.groupby:
            die(f"{args.kind} requires --genes and --groupby")
        fn = {
            "dotplot": sc.pl.dotplot, "matrixplot": sc.pl.matrixplot,
            "heatmap": sc.pl.heatmap, "tracksplot": sc.pl.tracksplot,
            "stacked_violin": sc.pl.stacked_violin,
        }[args.kind]
        fn(adata, genes, groupby=args.groupby, use_raw=use_raw, show=False, save=save)

    info(f"Saved {args.figdir}/{args.kind}{save}")


if __name__ == "__main__":
    main()
```

### `scripts/preprocess.py`

```python
#!/usr/bin/env python3
"""
Normalize, log-transform, select highly variable genes, and optionally scale.

Takes QC-filtered raw counts and produces a normalized, log1p-transformed
object ready for dimensionality reduction. A copy of the raw counts is kept in
``adata.layers['counts']`` and the normalized log values in ``adata.raw`` so
downstream marker/expression plots can use ``use_raw=True``.

Examples:
    python preprocess.py filtered.h5ad -o normalized.h5ad
    python preprocess.py filtered.h5ad -o normalized.h5ad --n-top-genes 3000 --scale
    python preprocess.py filtered.h5ad -o normalized.h5ad --flavor seurat_v3 --batch-key sample
    python preprocess.py filtered.h5ad -o normalized.h5ad --regress-out total_counts pct_counts_mt
"""

import argparse

from _common import add_io_args, configure_scanpy, info, load_anndata, save_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="normalized.h5ad")
    p.add_argument("--target-sum", type=float, default=1e4,
                   help="Counts per cell after normalization (default 1e4)")
    p.add_argument("--n-top-genes", type=int, default=2000,
                   help="Number of highly variable genes (default 2000)")
    p.add_argument("--flavor", default="seurat",
                   choices=["seurat", "cell_ranger", "seurat_v3"],
                   help="HVG flavor. seurat_v3 expects raw counts (default seurat)")
    p.add_argument("--batch-key", default=None,
                   help="obs column for batch-aware HVG selection")
    p.add_argument("--subset-hvg", action="store_true",
                   help="Subset the matrix to HVGs (smaller, but drops other genes from X)")
    p.add_argument("--regress-out", nargs="+", default=None,
                   help="obs columns to regress out (e.g. total_counts pct_counts_mt)")
    p.add_argument("--scale", action="store_true",
                   help="Scale to unit variance and zero mean (max_value=10)")
    p.add_argument("--no-plots", action="store_true", help="Skip HVG plot")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    info(f"Loaded {adata.n_obs} cells x {adata.n_vars} genes")

    # Preserve raw counts in a dedicated layer for pseudobulk / DE later.
    adata.layers["counts"] = adata.X.copy()

    if args.flavor == "seurat_v3":
        # seurat_v3 selects HVGs on raw counts, before normalization.
        sc.pp.highly_variable_genes(adata, n_top_genes=args.n_top_genes,
                                    flavor="seurat_v3", batch_key=args.batch_key)
        sc.pp.normalize_total(adata, target_sum=args.target_sum)
        sc.pp.log1p(adata)
    else:
        sc.pp.normalize_total(adata, target_sum=args.target_sum)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=args.n_top_genes,
                                    flavor=args.flavor, batch_key=args.batch_key)

    n_hvg = int(adata.var["highly_variable"].sum())
    info(f"Selected {n_hvg} highly variable genes")

    # Stash the full normalized log matrix so plots can use_raw=True.
    adata.raw = adata

    if not args.no_plots:
        sc.pl.highly_variable_genes(adata, show=False, save="_hvg.png")

    if args.subset_hvg:
        adata = adata[:, adata.var["highly_variable"]].copy()
        info(f"Subset to {adata.n_vars} HVGs")

    if args.regress_out:
        info(f"Regressing out: {', '.join(args.regress_out)}")
        sc.pp.regress_out(adata, args.regress_out)

    if args.scale:
        info("Scaling (max_value=10)")
        sc.pp.scale(adata, max_value=10)

    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/pseudobulk.py`

```python
#!/usr/bin/env python3
"""
Aggregate single cells into pseudobulk profiles for rigorous DE.

Sums raw counts within each combination of grouping columns (e.g. sample x
cell_type) using ``sc.get.aggregate`` and exports a genes x pseudobulk-sample
count matrix plus a sample-metadata table. Feed these into pydeseq2 / edgeR /
limma for condition comparisons — this is the statistically correct route,
unlike per-cell rank_genes_groups.

Examples:
    python pseudobulk.py annotated.h5ad --by sample cell_type --out-prefix results/pb
    python pseudobulk.py annotated.h5ad --by sample cell_type --layer counts --out-prefix pb
"""

import argparse
import os

from _common import configure_scanpy, die, info, load_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Input .h5ad")
    p.add_argument("--by", nargs="+", required=True,
                   help="obs columns to aggregate by (e.g. sample cell_type)")
    p.add_argument("--layer", default="counts",
                   help="Layer with raw counts to sum (default 'counts'; falls back to X)")
    p.add_argument("--func", default="sum", choices=["sum", "mean", "count_nonzero"],
                   help="Aggregation function (default sum)")
    p.add_argument("--out-prefix", default="pseudobulk",
                   help="Output prefix; writes <prefix>_counts.csv and <prefix>_samples.csv")
    args = p.parse_args()

    sc = configure_scanpy()
    adata = load_anndata(args.input)
    for col in args.by:
        if col not in adata.obs.columns:
            die(f"grouping column '{col}' not in obs: {list(adata.obs.columns)}")

    layer = args.layer if args.layer in adata.layers else None
    if args.layer and layer is None:
        info(f"Layer '{args.layer}' not found; aggregating adata.X instead")

    pb = sc.get.aggregate(adata, by=args.by, func=args.func, layer=layer)
    # aggregate stores the result in a layer named after func.
    mat = pb.layers[args.func]

    import pandas as pd
    sample_ids = ["_".join(str(pb.obs.iloc[i][c]) for c in args.by) for i in range(pb.n_obs)]
    counts_df = pd.DataFrame(
        mat.T.toarray() if hasattr(mat, "toarray") else mat.T,
        index=pb.var_names, columns=sample_ids,
    )

    parent = os.path.dirname(os.path.abspath(args.out_prefix))
    if parent:
        os.makedirs(parent, exist_ok=True)
    counts_path = f"{args.out_prefix}_counts.csv"
    samples_path = f"{args.out_prefix}_samples.csv"
    counts_df.to_csv(counts_path)
    meta = pb.obs[args.by].copy()
    meta.index = sample_ids
    meta.to_csv(samples_path)

    info(f"Wrote {counts_df.shape[0]} genes x {counts_df.shape[1]} pseudobulk samples")
    info(f"  counts:  {counts_path}")
    info(f"  samples: {samples_path}")
    info("Next: load these into pydeseq2 for differential expression.")


if __name__ == "__main__":
    main()
```

### `scripts/qc_analysis.py`

```python
#!/usr/bin/env python3
"""
Quality control and filtering for single-cell RNA-seq data.

Calculates QC metrics (genes/counts per cell, mitochondrial / ribosomal /
hemoglobin fractions), writes before/after QC plots, optionally runs Scrublet
doublet detection, and filters cells and genes by the given thresholds.

Run this FIRST on raw counts, before normalization.

Examples:
    python qc_analysis.py raw.h5ad -o filtered.h5ad
    python qc_analysis.py raw.h5ad -o filtered.h5ad --mt-threshold 10 --min-genes 500
    python qc_analysis.py 10x_dir/ -o filtered.h5ad --max-genes 6000 --scrublet
"""

import argparse

from _common import add_io_args, configure_scanpy, info, load_anndata, save_anndata


def annotate_gene_classes(adata):
    """Flag mitochondrial, ribosomal, and hemoglobin genes (human or mouse names)."""
    names = adata.var_names
    adata.var["mt"] = names.str.startswith(("MT-", "mt-", "Mt-"))
    adata.var["ribo"] = names.str.startswith(("RPS", "RPL", "Rps", "Rpl"))
    adata.var["hb"] = names.str.contains(r"^HB[^P]|^Hb[^p]", regex=True)
    return [v for v in ["mt", "ribo", "hb"] if adata.var[v].any()]


def make_qc_plots(sc, adata, prefix):
    qc_keys = ["n_genes_by_counts", "total_counts", "pct_counts_mt"]
    qc_keys = [k for k in qc_keys if k in adata.obs.columns]
    sc.pl.violin(adata, qc_keys, jitter=0.4, multi_panel=True,
                 show=False, save=f"_{prefix}_violin.png")
    if "pct_counts_mt" in adata.obs.columns:
        sc.pl.scatter(adata, x="total_counts", y="pct_counts_mt",
                      show=False, save=f"_{prefix}_mt.png")
    sc.pl.scatter(adata, x="total_counts", y="n_genes_by_counts",
                  show=False, save=f"_{prefix}_counts.png")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="qc_filtered.h5ad")
    p.add_argument("--min-genes", type=int, default=200, help="Min genes per cell (default 200)")
    p.add_argument("--max-genes", type=int, default=None, help="Max genes per cell (upper outliers)")
    p.add_argument("--min-counts", type=int, default=None, help="Min total counts per cell")
    p.add_argument("--max-counts", type=int, default=None, help="Max total counts per cell")
    p.add_argument("--min-cells", type=int, default=3, help="Min cells per gene (default 3)")
    p.add_argument("--mt-threshold", type=float, default=5, help="Max pct mitochondrial counts (default 5)")
    p.add_argument("--scrublet", action="store_true", help="Run Scrublet doublet detection and drop doublets")
    p.add_argument("--no-plots", action="store_true", help="Skip QC plots")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    adata.var_names_make_unique()
    info(f"Loaded {adata.n_obs} cells x {adata.n_vars} genes")

    qc_vars = annotate_gene_classes(adata)
    sc.pp.calculate_qc_metrics(adata, qc_vars=qc_vars, percent_top=None,
                               log1p=False, inplace=True)
    info(f"Mean genes/cell={adata.obs['n_genes_by_counts'].mean():.0f}  "
         f"mean counts/cell={adata.obs['total_counts'].mean():.0f}  "
         f"mean pct_mt={adata.obs.get('pct_counts_mt', 0).mean():.1f}")

    if not args.no_plots:
        make_qc_plots(sc, adata, "qc_before")

    n0, g0 = adata.n_obs, adata.n_vars
    sc.pp.filter_cells(adata, min_genes=args.min_genes)
    if args.min_counts:
        sc.pp.filter_cells(adata, min_counts=args.min_counts)
    if args.max_genes:
        adata = adata[adata.obs["n_genes_by_counts"] < args.max_genes, :].copy()
    if args.max_counts:
        adata = adata[adata.obs["total_counts"] < args.max_counts, :].copy()
    if "pct_counts_mt" in adata.obs.columns:
        adata = adata[adata.obs["pct_counts_mt"] < args.mt_threshold, :].copy()
    sc.pp.filter_genes(adata, min_cells=args.min_cells)

    if args.scrublet:
        info("Running Scrublet doublet detection...")
        try:
            sc.pp.scrublet(adata)
        except (ImportError, ValueError) as e:
            die(f"Scrublet failed ({e}). Install with: uv pip install scikit-image")
        n_dbl = int(adata.obs["predicted_doublet"].sum())
        adata = adata[~adata.obs["predicted_doublet"], :].copy()
        info(f"Removed {n_dbl} predicted doublets")

    info(f"Cells {n0} -> {adata.n_obs} ({adata.n_obs / n0 * 100:.1f}% kept)  "
         f"Genes {g0} -> {adata.n_vars}")

    if not args.no_plots:
        make_qc_plots(sc, adata, "qc_after")

    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/reduce_dimensions.py`

```python
#!/usr/bin/env python3
"""
PCA, neighborhood graph, and UMAP / t-SNE embeddings.

Takes a normalized object (optionally HVG-subset / scaled) and computes PCA,
the kNN graph, and a UMAP (and optionally t-SNE) embedding. Writes a PCA
variance-ratio elbow plot to help choose ``--n-pcs``.

Examples:
    python reduce_dimensions.py normalized.h5ad -o reduced.h5ad
    python reduce_dimensions.py normalized.h5ad -o reduced.h5ad --n-pcs 50 --n-neighbors 15
    python reduce_dimensions.py normalized.h5ad -o reduced.h5ad --tsne --use-rep X_pca_harmony
"""

import argparse

from _common import add_io_args, configure_scanpy, info, load_anndata, save_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="reduced.h5ad")
    p.add_argument("--n-comps", type=int, default=50, help="PCs to compute (default 50)")
    p.add_argument("--n-pcs", type=int, default=40, help="PCs used for the kNN graph (default 40)")
    p.add_argument("--n-neighbors", type=int, default=15, help="Neighbors for the graph (default 15)")
    p.add_argument("--use-rep", default=None,
                   help="obsm key to build the graph from instead of PCA "
                        "(e.g. X_pca_harmony from batch_correct.py)")
    p.add_argument("--tsne", action="store_true", help="Also compute t-SNE")
    p.add_argument("--color", nargs="+", default=None,
                   help="obs/var keys to color the UMAP by (e.g. sample n_genes_by_counts)")
    p.add_argument("--no-plots", action="store_true", help="Skip plots")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    info(f"Loaded {adata.n_obs} cells x {adata.n_vars} genes")

    n_comps = min(args.n_comps, adata.n_vars - 1, adata.n_obs - 1)
    sc.tl.pca(adata, n_comps=n_comps, svd_solver="arpack")
    if not args.no_plots:
        sc.pl.pca_variance_ratio(adata, n_pcs=n_comps, log=True,
                                 show=False, save="_variance.png")

    sc.pp.neighbors(adata, n_neighbors=args.n_neighbors, n_pcs=args.n_pcs,
                    use_rep=args.use_rep)
    info("Computing UMAP...")
    sc.tl.umap(adata)

    if args.tsne:
        info("Computing t-SNE...")
        sc.tl.tsne(adata, use_rep=args.use_rep or "X_pca")

    if not args.no_plots and args.color:
        color = [c for c in args.color if c in adata.obs.columns or c in adata.var_names]
        if color:
            sc.pl.umap(adata, color=color, show=False, save="_colored.png")

    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/run_pipeline.py`

```python
#!/usr/bin/env python3
"""
End-to-end standard scRNA-seq pipeline in one command.

Runs the full exploratory workflow on raw counts:
    load -> QC + filter -> (optional doublets) -> normalize + log1p -> HVG
    -> (optional scale/regress) -> PCA -> (optional batch correction)
    -> neighbors -> UMAP -> Leiden -> marker genes -> save.

Produces a processed .h5ad, marker CSVs, and figures. Tune the common knobs via
flags, or pass a JSON config with ``--config`` (keys mirror the flag names with
underscores). This is the fastest path from counts to a clustered, annotated-
ready object; use the individual step scripts when you need to iterate on one stage.

Examples:
    python run_pipeline.py raw.h5ad -o processed.h5ad
    python run_pipeline.py raw.h5ad -o processed.h5ad --resolution 0.8 --n-top-genes 3000
    python run_pipeline.py raw.h5ad -o processed.h5ad --batch-key sample --batch-method harmony
    python run_pipeline.py raw.h5ad -o processed.h5ad --config params.json
"""

import argparse
import json
import os

from _common import configure_scanpy, info, load_anndata, save_anndata


def build_parser():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input", help="Input raw-counts file (.h5ad, .h5, .csv, 10x dir, ...)")
    p.add_argument("-o", "--output", default="processed.h5ad", help="Output .h5ad")
    p.add_argument("--figdir", default="figures", help="Figure directory")
    p.add_argument("--marker-dir", default="results/markers", help="Marker CSV directory")
    p.add_argument("--config", default=None, help="JSON file overriding any of the options below")
    # QC
    p.add_argument("--min-genes", type=int, default=200)
    p.add_argument("--max-genes", type=int, default=None)
    p.add_argument("--min-cells", type=int, default=3)
    p.add_argument("--mt-threshold", type=float, default=5)
    p.add_argument("--scrublet", action="store_true")
    # normalization / HVG
    p.add_argument("--target-sum", type=float, default=1e4)
    p.add_argument("--n-top-genes", type=int, default=2000)
    p.add_argument("--hvg-flavor", default="seurat", choices=["seurat", "cell_ranger", "seurat_v3"])
    p.add_argument("--scale", action="store_true")
    p.add_argument("--regress-out", nargs="+", default=None)
    # dim reduction / clustering
    p.add_argument("--n-pcs", type=int, default=40)
    p.add_argument("--n-neighbors", type=int, default=15)
    p.add_argument("--resolution", type=float, default=0.5)
    # batch correction
    p.add_argument("--batch-key", default=None)
    p.add_argument("--batch-method", default="harmony", choices=["harmony", "combat"])
    # markers
    p.add_argument("--marker-method", default="wilcoxon")
    p.add_argument("--skip-markers", action="store_true")
    return p


def apply_config(args):
    if args.config:
        with open(args.config) as fh:
            cfg = json.load(fh)
        for k, v in cfg.items():
            setattr(args, k.replace("-", "_"), v)
    return args


def main():
    args = apply_config(build_parser().parse_args())
    sc = configure_scanpy(figdir=args.figdir)

    info("[1/8] Loading data")
    adata = load_anndata(args.input)
    adata.var_names_make_unique()
    info(f"      {adata.n_obs} cells x {adata.n_vars} genes")

    info("[2/8] QC + filtering")
    adata.var["mt"] = adata.var_names.str.startswith(("MT-", "mt-", "Mt-"))
    qc_vars = ["mt"] if adata.var["mt"].any() else []
    sc.pp.calculate_qc_metrics(adata, qc_vars=qc_vars, percent_top=None, log1p=False, inplace=True)
    sc.pl.violin(adata, [k for k in ["n_genes_by_counts", "total_counts", "pct_counts_mt"]
                         if k in adata.obs.columns],
                 jitter=0.4, multi_panel=True, show=False, save="_qc.png")
    n0 = adata.n_obs
    sc.pp.filter_cells(adata, min_genes=args.min_genes)
    sc.pp.filter_genes(adata, min_cells=args.min_cells)
    if args.max_genes:
        adata = adata[adata.obs["n_genes_by_counts"] < args.max_genes, :].copy()
    if qc_vars and "pct_counts_mt" in adata.obs.columns:
        adata = adata[adata.obs["pct_counts_mt"] < args.mt_threshold, :].copy()
    if args.scrublet:
        try:
            sc.pp.scrublet(adata)
            adata = adata[~adata.obs["predicted_doublet"], :].copy()
        except (ImportError, ValueError) as e:
            info(f"      Scrublet skipped ({e}); install scikit-image to enable")
    info(f"      {n0} -> {adata.n_obs} cells, {adata.n_vars} genes")

    info("[3/8] Normalize + log1p + HVG")
    adata.layers["counts"] = adata.X.copy()
    if args.hvg_flavor == "seurat_v3":
        sc.pp.highly_variable_genes(adata, n_top_genes=args.n_top_genes,
                                    flavor="seurat_v3", batch_key=args.batch_key)
        sc.pp.normalize_total(adata, target_sum=args.target_sum)
        sc.pp.log1p(adata)
    else:
        sc.pp.normalize_total(adata, target_sum=args.target_sum)
        sc.pp.log1p(adata)
        sc.pp.highly_variable_genes(adata, n_top_genes=args.n_top_genes,
                                    flavor=args.hvg_flavor, batch_key=args.batch_key)
    adata.raw = adata
    info(f"      {int(adata.var['highly_variable'].sum())} HVGs")

    info("[4/8] Scale / regress (optional)")
    work = adata[:, adata.var["highly_variable"]].copy()
    if args.regress_out:
        sc.pp.regress_out(work, args.regress_out)
    if args.scale:
        sc.pp.scale(work, max_value=10)

    info("[5/8] PCA" + (f" + {args.batch_method} batch correction" if args.batch_key else ""))
    sc.tl.pca(work, svd_solver="arpack")
    sc.pl.pca_variance_ratio(work, log=True, show=False, save="_variance.png")
    use_rep = "X_pca"
    if args.batch_key:
        if args.batch_method == "harmony":
            try:
                sc.external.pp.harmony_integrate(work, args.batch_key)
                use_rep = "X_pca_harmony"
            except ImportError:
                info("      harmonypy not installed; skipping (uv pip install harmonypy)")
        else:
            sc.pp.combat(work, key=args.batch_key)
            sc.tl.pca(work, svd_solver="arpack")

    info("[6/8] Neighbors + UMAP")
    sc.pp.neighbors(work, n_neighbors=args.n_neighbors, n_pcs=args.n_pcs, use_rep=use_rep)
    sc.tl.umap(work)

    info("[7/8] Leiden clustering")
    sc.tl.leiden(work, resolution=args.resolution, flavor="igraph",
                 n_iterations=2, directed=False)
    n_clusters = work.obs["leiden"].nunique()
    color = ["leiden"] + ([args.batch_key] if args.batch_key else [])
    sc.pl.umap(work, color=color, legend_loc="on data", show=False, save="_leiden.png")
    info(f"      {n_clusters} clusters at resolution {args.resolution}")

    # Carry embeddings/clusters back onto the full-gene object so markers use all genes.
    adata.obs["leiden"] = work.obs["leiden"].values
    adata.obsm["X_pca"] = work.obsm["X_pca"]
    adata.obsm["X_umap"] = work.obsm["X_umap"]
    if use_rep in work.obsm:
        adata.obsm[use_rep] = work.obsm[use_rep]
    adata.uns["neighbors"] = work.uns["neighbors"]
    adata.obsp = work.obsp

    if not args.skip_markers:
        info("[8/8] Marker genes")
        sc.tl.rank_genes_groups(adata, "leiden", method=args.marker_method, use_raw=True)
        sc.pl.rank_genes_groups_dotplot(adata, n_genes=5, show=False, save="_markers_dotplot.png")
        os.makedirs(args.marker_dir, exist_ok=True)
        import pandas as pd
        frames = []
        for g in adata.obs["leiden"].cat.categories:
            df = sc.get.rank_genes_groups_df(adata, group=g).head(25)
            df.insert(0, "cluster", g)
            frames.append(df)
        pd.concat(frames, ignore_index=True).to_csv(
            os.path.join(args.marker_dir, "markers_all.csv"), index=False)
        info(f"      marker tables in {args.marker_dir}/")
    else:
        info("[8/8] Skipping markers")

    save_anndata(adata, args.output)
    info("Pipeline complete. Next: inspect markers, then annotate.py with a cluster->cell_type mapping.")


if __name__ == "__main__":
    main()
```

### `scripts/score_genes.py`

```python
#!/usr/bin/env python3
"""
Score cells for one or more gene signatures.

Computes ``sc.tl.score_genes`` for each named gene set in a JSON file and adds
one obs column per signature (``<name>_score``). Also supports the built-in
cell-cycle scoring with ``--cell-cycle``. Writes UMAPs colored by each score.

Gene-set JSON format:
  {"T_cell": ["CD3D","CD3E","CD3G"], "cytotoxic": ["GZMB","PRF1","NKG7"]}

Examples:
    python score_genes.py annotated.h5ad -o scored.h5ad --gene-sets signatures.json
    python score_genes.py annotated.h5ad -o scored.h5ad --cell-cycle
"""

import argparse
import json

from _common import add_io_args, configure_scanpy, info, load_anndata, save_anndata

# Tirosh et al. (2016) cell-cycle genes (human). Lowercase/title for mouse if needed.
S_GENES = ["MCM5", "PCNA", "TYMS", "FEN1", "MCM2", "MCM4", "RRM1", "UNG", "GINS2",
           "MCM6", "CDCA7", "DTL", "PRIM1", "UHRF1", "MLF1IP", "HELLS", "RFC2",
           "RPA2", "NASP", "RAD51AP1", "GMNN", "WDR76", "SLBP", "CCNE2", "UBR7",
           "POLD3", "MSH2", "ATAD2", "RAD51", "RRM2", "CDC45", "CDC6", "EXO1",
           "TIPIN", "DSCC1", "BLM", "CASP8AP2", "USP1", "CLSPN", "POLA1", "CHAF1B",
           "BRIP1", "E2F8"]
G2M_GENES = ["HMGB2", "CDK1", "NUSAP1", "UBE2C", "BIRC5", "TPX2", "TOP2A", "NDC80",
             "CKS2", "NUF2", "CKS1B", "MKI67", "TMPO", "CENPF", "TACC3", "FAM64A",
             "SMC4", "CCNB2", "CKAP2L", "CKAP2", "AURKB", "BUB1", "KIF11", "ANP32E",
             "TUBB4B", "GTSE1", "KIF20B", "HJURP", "CDCA3", "HN1", "CDC20", "TTK",
             "CDC25C", "KIF2C", "RANGAP1", "NCAPD2", "DLGAP5", "CDCA2", "CDCA8",
             "ECT2", "KIF23", "HMMR", "AURKA", "PSRC1", "ANLN", "LBR", "CKAP5",
             "CENPE", "CTCF", "NEK2", "G2E3", "GAS2L3", "CBX5", "CENPA"]


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="scored.h5ad")
    p.add_argument("--gene-sets", default=None, help="JSON of {name: [genes]}")
    p.add_argument("--cell-cycle", action="store_true",
                   help="Add S_score, G2M_score, and phase (Tirosh 2016 human genes)")
    p.add_argument("--no-plots", action="store_true", help="Skip plots")
    args = p.parse_args()

    sc = configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    var_names = adata.raw.var_names if adata.raw is not None else adata.var_names
    plot_keys = []

    if args.gene_sets:
        with open(args.gene_sets) as fh:
            sets = json.load(fh)
        for name, genes in sets.items():
            present = [g for g in genes if g in var_names]
            if not present:
                info(f"Skipping '{name}': no genes present")
                continue
            sc.tl.score_genes(adata, present, score_name=f"{name}_score",
                              use_raw=adata.raw is not None)
            plot_keys.append(f"{name}_score")
            info(f"Scored '{name}' ({len(present)}/{len(genes)} genes)")

    if args.cell_cycle:
        s = [g for g in S_GENES if g in var_names]
        g2m = [g for g in G2M_GENES if g in var_names]
        sc.tl.score_genes_cell_cycle(adata, s_genes=s, g2m_genes=g2m,
                                     use_raw=adata.raw is not None)
        plot_keys += ["phase"]
        info(f"Cell-cycle scored (S={len(s)}, G2M={len(g2m)} genes); phases: "
             + ", ".join(f"{k}={v}" for k, v in adata.obs['phase'].value_counts().items()))

    if not args.no_plots and plot_keys and "X_umap" in adata.obsm:
        sc.pl.umap(adata, color=plot_keys, show=False, save="_scores.png")

    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/subset.py`

```python
#!/usr/bin/env python3
"""
Subset an AnnData object by cell metadata or genes.

Filter cells by obs-column values (keep or drop), or restrict to a gene list.
Useful for isolating a cell type / condition for focused re-analysis.

Examples:
    python subset.py annotated.h5ad -o tcells.h5ad --obs cell_type --keep "CD4 T cells" "CD8 T cells"
    python subset.py annotated.h5ad -o no_doublets.h5ad --obs predicted_doublet --drop True
    python subset.py data.h5ad -o panel.h5ad --genes CD3D CD14 MS4A1 NKG7
"""

import argparse

from _common import add_io_args, configure_scanpy, die, info, load_anndata, save_anndata


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    add_io_args(p, default_output="subset.h5ad")
    p.add_argument("--obs", default=None, help="obs column to filter on")
    p.add_argument("--keep", nargs="+", default=None, help="Values of --obs to keep")
    p.add_argument("--drop", nargs="+", default=None, help="Values of --obs to drop")
    p.add_argument("--genes", nargs="+", default=None, help="Restrict to these genes")
    p.add_argument("--recompute-hvg", action="store_true",
                   help="After subsetting, drop stale embeddings so the next steps recompute cleanly")
    args = p.parse_args()

    configure_scanpy(figdir=args.figdir)
    adata = load_anndata(args.input)
    n0 = adata.n_obs

    if args.obs:
        if args.obs not in adata.obs.columns:
            die(f"obs column '{args.obs}' not found: {list(adata.obs.columns)}")
        vals = adata.obs[args.obs].astype(str)
        if args.keep:
            adata = adata[vals.isin([str(v) for v in args.keep]), :].copy()
        elif args.drop:
            adata = adata[~vals.isin([str(v) for v in args.drop]), :].copy()
        else:
            die("provide --keep or --drop with --obs")
        info(f"Cells {n0} -> {adata.n_obs}")

    if args.genes:
        present = [g for g in args.genes if g in adata.var_names]
        if not present:
            die("none of the requested genes are present")
        adata = adata[:, present].copy()
        info(f"Restricted to {adata.n_vars} genes")

    if args.recompute_hvg:
        for k in ("X_pca", "X_umap", "X_tsne"):
            adata.obsm.pop(k, None)
        adata.uns.pop("neighbors", None)
        info("Cleared PCA/UMAP/neighbors; re-run preprocess/reduce_dimensions on the subset")

    save_anndata(adata, args.output)


if __name__ == "__main__":
    main()
```

### `assets/analysis_template.py`

```python
#!/usr/bin/env python3
"""
Complete Single-Cell Analysis Template

This template provides a complete workflow for single-cell RNA-seq analysis
using scanpy, from data loading through clustering and cell type annotation.

Customize the parameters and sections as needed for your specific dataset.
"""

import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# CONFIGURATION
# ============================================================================

# File paths
INPUT_FILE = 'data/raw_counts.h5ad'  # Change to your input file
OUTPUT_DIR = 'results/'
FIGURES_DIR = 'figures/'

# QC parameters
MIN_GENES = 200          # Minimum genes per cell
MIN_CELLS = 3            # Minimum cells per gene
MT_THRESHOLD = 5         # Maximum mitochondrial percentage

# Analysis parameters
N_TOP_GENES = 2000       # Number of highly variable genes
N_PCS = 40               # Number of principal components
N_NEIGHBORS = 10         # Number of neighbors for graph
LEIDEN_RESOLUTION = 0.5  # Clustering resolution

# Scanpy settings
sc.settings.verbosity = 3
sc.settings.set_figure_params(dpi=80, facecolor='white')
sc.settings.figdir = FIGURES_DIR
sc.settings.autosave = True

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("=" * 80)
print("LOADING DATA")
print("=" * 80)

# Load data (adjust based on your file format)
adata = sc.read_h5ad(INPUT_FILE)
# adata = sc.read_10x_mtx('data/filtered_gene_bc_matrices/')  # For 10X data
# adata = sc.read_csv('data/counts.csv')  # For CSV data

print(f"Loaded: {adata.n_obs} cells x {adata.n_vars} genes")

# ============================================================================
# 2. QUALITY CONTROL
# ============================================================================

print("\n" + "=" * 80)
print("QUALITY CONTROL")
print("=" * 80)

# Identify mitochondrial genes
adata.var['mt'] = adata.var_names.str.startswith('MT-')

# Calculate QC metrics
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None,
                            log1p=False, inplace=True)

# Visualize QC metrics before filtering
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True, save='_qc_before_filtering')

sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt', save='_qc_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts', save='_qc_genes')

# Filter cells and genes
print(f"\nBefore filtering: {adata.n_obs} cells, {adata.n_vars} genes")

sc.pp.filter_cells(adata, min_genes=MIN_GENES)
sc.pp.filter_genes(adata, min_cells=MIN_CELLS)
adata = adata[adata.obs.pct_counts_mt < MT_THRESHOLD, :]

print(f"After filtering: {adata.n_obs} cells, {adata.n_vars} genes")

# Optional: doublet detection (uncomment; run before normalization)
# sc.pp.scrublet(adata)
# adata = adata[~adata.obs['predicted_doublet'], :].copy()
# print(f"After doublet removal: {adata.n_obs} cells")

# ============================================================================
# 3. NORMALIZATION
# ============================================================================

print("\n" + "=" * 80)
print("NORMALIZATION")
print("=" * 80)

# Normalize to 10,000 counts per cell
sc.pp.normalize_total(adata, target_sum=1e4)

# Log-transform
sc.pp.log1p(adata)

# Store normalized data
adata.raw = adata

# ============================================================================
# 4. FEATURE SELECTION
# ============================================================================

print("\n" + "=" * 80)
print("FEATURE SELECTION")
print("=" * 80)

# Identify highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=N_TOP_GENES)

# Visualize
sc.pl.highly_variable_genes(adata, save='_hvg')

print(f"Selected {sum(adata.var.highly_variable)} highly variable genes")

# Subset to highly variable genes
adata = adata[:, adata.var.highly_variable]

# ============================================================================
# 5. SCALING AND REGRESSION
# ============================================================================

print("\n" + "=" * 80)
print("SCALING AND REGRESSION")
print("=" * 80)

# Regress out unwanted sources of variation
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])

# Scale data
sc.pp.scale(adata, max_value=10)

# ============================================================================
# 6. DIMENSIONALITY REDUCTION
# ============================================================================

print("\n" + "=" * 80)
print("DIMENSIONALITY REDUCTION")
print("=" * 80)

# PCA
sc.tl.pca(adata, svd_solver='arpack')
sc.pl.pca_variance_ratio(adata, log=True, save='_pca_variance')

# Compute neighborhood graph
sc.pp.neighbors(adata, n_neighbors=N_NEIGHBORS, n_pcs=N_PCS)

# UMAP
sc.tl.umap(adata)

# ============================================================================
# 7. CLUSTERING
# ============================================================================

print("\n" + "=" * 80)
print("CLUSTERING")
print("=" * 80)

# Leiden clustering
sc.tl.leiden(adata, resolution=LEIDEN_RESOLUTION)

# Visualize
sc.pl.umap(adata, color='leiden', legend_loc='on data', save='_leiden')

print(f"Identified {len(adata.obs['leiden'].unique())} clusters")

# ============================================================================
# 8. MARKER GENE IDENTIFICATION
# ============================================================================

print("\n" + "=" * 80)
print("MARKER GENE IDENTIFICATION")
print("=" * 80)

# Find marker genes (exploratory — pseudobulk + pydeseq2 for rigorous DE)
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')

# Visualize top markers
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False, save='_markers')
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10, save='_markers_heatmap')
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5, save='_markers_dotplot')

# Get top markers for each cluster
for cluster in adata.obs['leiden'].unique():
    print(f"\nCluster {cluster} top markers:")
    markers = sc.get.rank_genes_groups_df(adata, group=cluster).head(10)
    print(markers[['names', 'scores', 'pvals_adj']].to_string(index=False))

# ============================================================================
# 9. CELL TYPE ANNOTATION (CUSTOMIZE THIS SECTION)
# ============================================================================

print("\n" + "=" * 80)
print("CELL TYPE ANNOTATION")
print("=" * 80)

# Example marker genes for common cell types (customize for your data)
marker_genes = {
    'T cells': ['CD3D', 'CD3E', 'CD3G'],
    'B cells': ['MS4A1', 'CD79A', 'CD79B'],
    'Monocytes': ['CD14', 'LYZ', 'S100A8'],
    'NK cells': ['NKG7', 'GNLY', 'KLRD1'],
    'Dendritic cells': ['FCER1A', 'CST3'],
}

# Visualize marker genes
for cell_type, genes in marker_genes.items():
    available_genes = [g for g in genes if g in adata.raw.var_names]
    if available_genes:
        sc.pl.umap(adata, color=available_genes, use_raw=True,
                   save=f'_{cell_type.replace(" ", "_")}')

# Manual annotation based on marker expression (customize this mapping)
cluster_to_celltype = {
    '0': 'CD4 T cells',
    '1': 'CD14+ Monocytes',
    '2': 'B cells',
    '3': 'CD8 T cells',
    '4': 'NK cells',
    # Add more mappings based on your marker analysis
}

# Apply annotations
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_to_celltype)
adata.obs['cell_type'] = adata.obs['cell_type'].fillna('Unknown')

# Visualize annotated cell types
sc.pl.umap(adata, color='cell_type', legend_loc='on data', save='_celltypes')

# ============================================================================
# 10. ADDITIONAL ANALYSES (OPTIONAL)
# ============================================================================

print("\n" + "=" * 80)
print("ADDITIONAL ANALYSES")
print("=" * 80)

# PAGA trajectory analysis (optional)
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color='leiden', save='_paga')

# Gene set scoring (optional)
# example_gene_set = ['CD3D', 'CD3E', 'CD3G']
# sc.tl.score_genes(adata, example_gene_set, score_name='T_cell_score')
# sc.pl.umap(adata, color='T_cell_score', save='_gene_set_score')

# ============================================================================
# 11. SAVE RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

import os
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Save processed AnnData object
adata.write(f'{OUTPUT_DIR}/processed_data.h5ad')
print(f"Saved processed data to {OUTPUT_DIR}/processed_data.h5ad")

# Export metadata
adata.obs.to_csv(f'{OUTPUT_DIR}/cell_metadata.csv')
adata.var.to_csv(f'{OUTPUT_DIR}/gene_metadata.csv')
print(f"Saved metadata to {OUTPUT_DIR}/")

# Export marker genes
for cluster in adata.obs['leiden'].unique():
    markers = sc.get.rank_genes_groups_df(adata, group=cluster)
    markers.to_csv(f'{OUTPUT_DIR}/markers_cluster_{cluster}.csv', index=False)
print(f"Saved marker genes to {OUTPUT_DIR}/")

# ============================================================================
# 12. SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)

print(f"\nFinal dataset:")
print(f"  Cells: {adata.n_obs}")
print(f"  Genes: {adata.n_vars}")
print(f"  Clusters: {len(adata.obs['leiden'].unique())}")

print(f"\nCell type distribution:")
print(adata.obs['cell_type'].value_counts())

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
```

### `assets/celltype_mapping.json`

```json
{
  "0": "CD4 T cells",
  "1": "CD14+ Monocytes",
  "2": "B cells",
  "3": "CD8 T cells",
  "4": "NK cells",
  "5": "FCGR3A+ Monocytes",
  "6": "Dendritic cells",
  "7": "Platelets"
}
```

### `assets/gene_signatures.json`

```json
{
  "T_cell": ["CD3D", "CD3E", "CD3G", "CD2"],
  "B_cell": ["MS4A1", "CD79A", "CD79B", "CD19"],
  "monocyte": ["CD14", "LYZ", "S100A8", "S100A9"],
  "NK_cell": ["NKG7", "GNLY", "KLRD1", "NCAM1"],
  "cytotoxic": ["GZMB", "GZMK", "PRF1", "NKG7"],
  "dendritic": ["FCER1A", "CST3", "CLEC10A"],
  "exhaustion": ["PDCD1", "HAVCR2", "LAG3", "TIGIT", "CTLA4"]
}
```

### `assets/pipeline_config.json`

```json
{
  "min_genes": 200,
  "max_genes": 6000,
  "min_cells": 3,
  "mt_threshold": 10,
  "scrublet": true,
  "target_sum": 10000,
  "n_top_genes": 2000,
  "hvg_flavor": "seurat",
  "scale": false,
  "regress_out": null,
  "n_pcs": 40,
  "n_neighbors": 15,
  "resolution": 0.5,
  "batch_key": null,
  "batch_method": "harmony",
  "marker_method": "wilcoxon",
  "skip_markers": false
}
```
