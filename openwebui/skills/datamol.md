---
name: datamol
description: Pythonic wrapper around RDKit with simplified interface and sensible defaults. Preferred for standard drug discovery including SMILES parsing, standardization, descriptors, fingerprints, clustering, 3D conformers, parallel processing. Returns native rdkit.Chem.Mol objects. For advanced control or custom parameters, use rdkit directly.
---

# Datamol Cheminformatics Skill

## Overview

Datamol is a Python library that provides a lightweight, Pythonic abstraction layer over RDKit for molecular cheminformatics. Simplify complex molecular operations with sensible defaults, efficient parallelization, and modern I/O capabilities. All molecular objects are native `rdkit.Chem.Mol` instances, ensuring full compatibility with the RDKit ecosystem.

**Version note:** Examples target **datamol 0.12.x** (PyPI stable: **0.12.5**, June 2024). Since 0.10.0, modules are lazy-loaded by default (set `DATAMOL_DISABLE_LAZY_LOADING=1` to disable). Since 0.12.2, RDKit is a direct PyPI dependency of datamol. Fingerprints use RDKit's `rdFingerprintGenerator` API (0.12.5+).

**Key capabilities**:
- Molecular format conversion (SMILES, SELFIES, InChI)
- Structure standardization and sanitization
- Molecular descriptors and fingerprints
- 3D conformer generation and analysis
- Clustering and diversity selection
- Scaffold and fragment analysis
- Chemical reaction application
- Visualization and alignment
- Batch processing with parallelization
- Cloud storage support via fsspec

## Installation and Setup

Guide users to install datamol:

```bash
uv pip install datamol
```

RDKit is installed automatically with datamol. For remote file paths (S3, GCS, HTTP), install the matching fsspec backend:

```bash
uv pip install s3fs   # AWS S3
uv pip install gcsfs  # Google Cloud Storage
```

**Import convention**:
```python
import datamol as dm
```

## Core Workflows

Ten workflow areas, each with worked code, are documented in
[references/core_workflows.md](references/core_workflows.md):

| # | Area | Covers |
| --- | --- | --- |
| 1 | Basic molecule handling | `to_mol`, batch conversion, error handling, canonical and isomeric SMILES, sanitization and full standardization |
| 2 | Reading and writing files | SDF, SMILES, CSV, Excel with rendered structures, the universal reader/writer, and cloud or HTTPS paths |
| 3 | Descriptors and properties | the standard descriptor set, parallel computation, aromaticity, stereochemistry, flexibility, and filtering |
| 4 | Fingerprints and similarity | ECFP4 and other types, pairwise and cross-set distances, nearest-neighbour lookup (Tanimoto distance = 1 − similarity) |
| 5 | Clustering and diversity | similarity clustering, diverse subset picking, and cluster centroids |
| 6 | Scaffold analysis | Bemis-Murcko scaffolds, grouping and counting, and scaffold-disjoint train/test splits |
| 7 | Fragmentation | fragmenting molecules, finding common fragments across a library, and fragment-based scoring |
| 8 | 3D conformers | generation, access, RMSD clustering, representative selection, and SASA |
| 9 | Visualization | grids, files, publication SVG, substructure alignment, atom and bond highlighting, conformer display |
| 10 | Chemical reactions | reaction SMARTS, applying to a molecule or a whole library |

Three end-to-end pipelines — load/filter/analyze, SAR by scaffold series, and virtual
screening — are in [references/workflow_patterns.md](references/workflow_patterns.md).

## Parallelization

Datamol includes built-in parallelization for many operations. Use `n_jobs` parameter:
- `n_jobs=1`: Sequential (no parallelization)
- `n_jobs=-1`: Use all available CPU cores
- `n_jobs=4`: Use 4 cores

**Functions supporting parallelization**:
- `dm.read_sdf(..., n_jobs=-1)`
- `dm.descriptors.batch_compute_many_descriptors(..., n_jobs=-1)`
- `dm.cluster_mols(..., n_jobs=-1)`
- `dm.pdist(..., n_jobs=-1)`
- `dm.conformers.sasa(..., n_jobs=-1)`

**Progress bars**: Many batch operations support `progress=True` parameter.

## Reference Documentation

For detailed API documentation, consult these reference files:

- **`references/core_api.md`**: Core namespace functions (conversions, standardization, fingerprints, clustering)
- **`references/io_module.md`**: File I/O operations (read/write SDF, CSV, Excel, remote files)
- **`references/conformers_module.md`**: 3D conformer generation, clustering, SASA calculations
- **`references/descriptors_viz.md`**: Molecular descriptors and visualization functions
- **`references/fragments_scaffolds.md`**: Scaffold extraction, BRICS/RECAP fragmentation
- **`references/reactions_data.md`**: Chemical reactions and toy datasets

## Best Practices

1. **Always standardize molecules** from external sources:
   ```python
   mol = dm.standardize_mol(mol, disconnect_metals=True, normalize=True, reionize=True)
   ```

2. **Check for None values** after molecule parsing:
   ```python
   mol = dm.to_mol(smiles)
   if mol is None:
       # Handle invalid SMILES
   ```

3. **Use parallel processing** for large datasets:
   ```python
   result = dm.operation(..., n_jobs=-1, progress=True)
   ```

4. **Use cloud I/O only when requested** — confirm remote write paths; install `s3fs`/`gcsfs` as needed:
   ```python
   df = dm.read_sdf("s3://bucket/compounds.sdf")
   ```

5. **Use appropriate fingerprints** for similarity:
   - ECFP (Morgan): General purpose, structural similarity
   - MACCS: Fast, smaller feature space
   - Atom pairs: Considers atom pairs and distances

6. **Consider scale limitations**:
   - Butina clustering: ~1,000 molecules (full distance matrix)
   - For larger datasets: Use diversity selection or hierarchical methods

7. **Scaffold splitting for ML**: Ensure proper train/test separation by scaffold

8. **Align molecules** when visualizing SAR series

## Error Handling

```python
# Safe molecule creation
def safe_to_mol(smiles):
    try:
        mol = dm.to_mol(smiles)
        if mol is not None:
            mol = dm.standardize_mol(mol)
        return mol
    except Exception as e:
        print(f"Failed to process {smiles}: {e}")
        return None

# Safe batch processing
valid_mols = []
for smiles in smiles_list:
    mol = safe_to_mol(smiles)
    if mol is not None:
        valid_mols.append(mol)
```

## Integration with Machine Learning

Datamol ships with `scipy` and `scikit-learn` as dependencies. Import them as normal PyPI packages — they are not scripts bundled in this skill.

```python
import numpy as np

# Feature generation
X = np.array([dm.to_fp(mol) for mol in mols])

# Or descriptors
desc_df = dm.descriptors.batch_compute_many_descriptors(mols, n_jobs=-1)
X = desc_df.values

# Train model (scikit-learn PyPI package)
from sklearn.ensemble import RandomForestRegressor  # third-party library
model = RandomForestRegressor()
model.fit(X, y_target)

# Predict
predictions = model.predict(X_test)
```

## Troubleshooting

**Issue**: Molecule parsing fails
- **Solution**: Use `dm.standardize_smiles()` first or try `dm.fix_mol()`

**Issue**: Memory errors with clustering
- **Solution**: Use `dm.pick_diverse()` instead of full clustering for large sets

**Issue**: Slow conformer generation
- **Solution**: Reduce `n_confs` or increase `rms_cutoff` to generate fewer conformers

**Issue**: Remote file access fails
- **Solution**: Install the matching fsspec backend (`uv pip install s3fs` or `gcsfs`) and verify only the provider credentials needed for that backend are set (see Remote file support above)

## Additional Resources

- **Datamol Documentation**: https://docs.datamol.io/
- **RDKit Documentation**: https://www.rdkit.org/docs/
- **GitHub Repository**: https://github.com/datamol-io/datamol

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/datamol/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/conformers_module.md`

# Datamol Conformers Module Reference

The `datamol.conformers` module provides tools for generating and analyzing 3D molecular conformations.

## Conformer Generation

### `dm.conformers.generate(mol, n_confs=None, rms_cutoff=None, minimize_energy=True, method='ETKDGv3', add_hs=True, ...)`
Generate 3D molecular conformers.
- **Parameters**:
  - `mol`: Input molecule
  - `n_confs`: Number of conformers to generate (auto-determined based on rotatable bonds if None)
  - `rms_cutoff`: RMS threshold in Ångströms for filtering similar conformers (removes duplicates)
  - `minimize_energy`: Apply UFF energy minimization (default: True)
  - `method`: Embedding method - options:
    - `'ETDG'` - Experimental Torsion Distance Geometry
    - `'ETKDG'` - ETDG with additional basic knowledge
    - `'ETKDGv2'` - Enhanced version 2
    - `'ETKDGv3'` - Enhanced version 3 (default, recommended)
  - `add_hs`: Add hydrogens before embedding (default: True, critical for quality)
  - `random_seed`: Set for reproducibility
- **Returns**: Molecule with embedded conformers
- **Example**:
  ```python
  mol = dm.to_mol("CCO")
  mol_3d = dm.conformers.generate(mol, n_confs=10, rms_cutoff=0.5)
  conformers = mol_3d.GetConformers()  # Access all conformers
  ```

## Conformer Clustering

### `dm.conformers.cluster(mol, rms_cutoff=1.0, already_aligned=False, centroids=False)`
Group conformers by RMS distance.
- **Parameters**:
  - `rms_cutoff`: Clustering threshold in Ångströms (default: 1.0)
  - `already_aligned`: Whether conformers are pre-aligned
  - `centroids`: Return centroid conformers (True) or cluster groups (False)
- **Returns**: Cluster information or centroid conformers
- **Use case**: Identify distinct conformational families

### `dm.conformers.return_centroids(mol, conf_clusters, centroids=True)`
Extract representative conformers from clusters.
- **Parameters**:
  - `conf_clusters`: Sequence of cluster indices from `cluster()`
  - `centroids`: Return single molecule (True) or list of molecules (False)
- **Returns**: Centroid conformer(s)

## Conformer Analysis

### `dm.conformers.rmsd(mol)`
Calculate pairwise RMSD matrix across all conformers.
- **Requirements**: Minimum 2 conformers
- **Returns**: NxN matrix of RMSD values
- **Use case**: Quantify conformer diversity

### `dm.conformers.sasa(mol, n_jobs=1, ...)`
Calculate Solvent Accessible Surface Area (SASA) using FreeSASA.
- **Parameters**:
  - `n_jobs`: Parallelization for multiple conformers
- **Returns**: Array of SASA values (one per conformer)
- **Storage**: Values stored in each conformer as property `'rdkit_free_sasa'`
- **Example**:
  ```python
  sasa_values = dm.conformers.sasa(mol_3d)
  # Or access from conformer properties
  conf = mol_3d.GetConformer(0)
  sasa = conf.GetDoubleProp('rdkit_free_sasa')
  ```

## Low-Level Conformer Manipulation

### `dm.conformers.center_of_mass(mol, conf_id=-1, use_atoms=True, round_coord=None)`
Calculate molecular center.
- **Parameters**:
  - `conf_id`: Conformer index (-1 for first conformer)
  - `use_atoms`: Use atomic masses (True) or geometric center (False)
  - `round_coord`: Decimal precision for rounding
- **Returns**: 3D coordinates of center
- **Use case**: Centering molecules for visualization or alignment

### `dm.conformers.get_coords(mol, conf_id=-1)`
Retrieve atomic coordinates from a conformer.
- **Returns**: Nx3 numpy array of atomic positions
- **Example**:
  ```python
  positions = dm.conformers.get_coords(mol_3d, conf_id=0)
  # positions.shape: (num_atoms, 3)
  ```

### `dm.conformers.translate(mol, conf_id=-1, transform_matrix=None)`
Reposition conformer using transformation matrix.
- **Modification**: Operates in-place
- **Use case**: Aligning or repositioning molecules

## Workflow Example

```python
import datamol as dm

# 1. Create molecule and generate conformers
mol = dm.to_mol("CC(C)CCO")  # Isopentanol
mol_3d = dm.conformers.generate(
    mol,
    n_confs=50,           # Generate 50 initial conformers
    rms_cutoff=0.5,       # Filter similar conformers
    minimize_energy=True   # Minimize energy
)

# 2. Analyze conformers
n_conformers = mol_3d.GetNumConformers()
print(f"Generated {n_conformers} unique conformers")

# 3. Calculate SASA
sasa_values = dm.conformers.sasa(mol_3d)

# 4. Cluster conformers
clusters = dm.conformers.cluster(mol_3d, rms_cutoff=1.0, centroids=False)

# 5. Get representative conformers
centroids = dm.conformers.return_centroids(mol_3d, clusters)

# 6. Access 3D coordinates
coords = dm.conformers.get_coords(mol_3d, conf_id=0)
```

## Key Concepts

- **Distance Geometry**: Method for generating 3D structures from connectivity information
- **ETKDG**: Uses experimental torsion angle preferences and additional chemical knowledge
- **RMS Cutoff**: Lower values = more unique conformers; higher values = fewer, more distinct conformers
- **Energy Minimization**: Relaxes structures to nearest local energy minimum
- **Hydrogens**: Critical for accurate 3D geometry - always include during embedding

### `references/core_api.md`

# Datamol Core API Reference

This document covers the main functions available in the datamol namespace.

## Molecule Creation and Conversion

### `to_mol(mol, ...)`
Convert SMILES string or other molecular representations to RDKit molecule objects.
- **Parameters**: Accepts SMILES strings, InChI, or other molecular formats
- **Returns**: `rdkit.Chem.Mol` object
- **Common usage**: `mol = dm.to_mol("CCO")`

### `from_inchi(inchi)`
Convert InChI string to molecule object.

### `from_smarts(smarts)`
Convert SMARTS pattern to molecule object.

### `from_selfies(selfies)`
Convert SELFIES string to molecule object.

### `copy_mol(mol)`
Create a copy of a molecule object to avoid modifying the original.

## Molecule Export

### `to_smiles(mol, ...)`
Convert molecule object to SMILES string.
- **Common parameters**: `canonical=True`, `isomeric=True`

### `to_inchi(mol, ...)`
Convert molecule to InChI string representation.

### `to_inchikey(mol)`
Convert molecule to InChI key (fixed-length hash).

### `to_smarts(mol)`
Convert molecule to SMARTS pattern.

### `to_selfies(mol)`
Convert molecule to SELFIES (Self-Referencing Embedded Strings) format.

## Sanitization and Standardization

### `sanitize_mol(mol, ...)`
Enhanced version of RDKit's sanitize operation using mol→SMILES→mol conversion and aromatic nitrogen fixing.
- **Purpose**: Fix common molecular structure issues
- **Returns**: Sanitized molecule or None if sanitization fails

### `standardize_mol(mol, disconnect_metals=False, normalize=True, reionize=True, ...)`
Apply comprehensive standardization procedures including:
- Metal disconnection
- Normalization (charge corrections)
- Reionization
- Fragment handling (largest fragment selection)

### `standardize_smiles(smiles, ...)`
Apply SMILES standardization procedures directly to a SMILES string.

### `fix_mol(mol)`
Attempt to fix molecular structure issues automatically.

### `fix_valence(mol)` / `fix_valence_charge(mol, inplace=False)`
Correct valence errors in molecular structures (charge-aware variant available).

### `hash_mol(mol, hash_scheme='all')`
Generate a chemistry-aware hash for deduplication (requires RDKit ≥ 2022.09).
- **`hash_scheme`**: `'all'` (default), `'no_stereo'`, or `'no_tautomers'`

## Molecular Properties

### `reorder_atoms(mol, ...)`
Ensure consistent atom ordering for the same molecule regardless of original SMILES representation.
- **Purpose**: Maintain reproducible feature generation

### `remove_hs(mol, ...)`
Remove hydrogen atoms from molecular structure.

### `add_hs(mol, ...)`
Add explicit hydrogen atoms to molecular structure.

## Fingerprints and Similarity

### `to_fp(mol, fp_type='ecfp', ...)`
Generate molecular fingerprints for similarity calculations.
- **Fingerprint types**:
  - `'ecfp'` / `'fcfp'` - Morgan fingerprints (default radius 3 for ECFP6; pass `radius=2` for ECFP4)
  - `'maccs'` - MACCS keys
  - `'topological'` - Topological fingerprints
  - `'atompair'` - Atom pair fingerprints
  - `'rdkit'` - RDKit topological fingerprint
  - Count variants: `'ecfp-count'`, `'fcfp-count'`, `'atompair-count'`, etc.
- **Implementation**: Uses RDKit `rdFingerprintGenerator` (datamol ≥ 0.12.5)
- **Common parameters**: `n_bits` (default 2048), `radius`
- **Returns**: Numpy array or RDKit fingerprint object

### `pdist(mols, ...)`
Calculate pairwise Tanimoto distances between all molecules in a list.
- **Supports**: Parallel processing via `n_jobs` parameter
- **Returns**: Distance matrix

### `cdist(mols1, mols2, ...)`
Calculate Tanimoto distances between two sets of molecules.

## Clustering and Diversity

### `cluster_mols(mols, cutoff=0.2, feature_fn=None, n_jobs=1)`
Cluster molecules using Butina clustering algorithm.
- **Parameters**:
  - `cutoff`: Distance threshold (default 0.2)
  - `feature_fn`: Custom function for molecular features
  - `n_jobs`: Parallelization (-1 for all cores)
- **Important**: Builds full distance matrix - suitable for ~1000 structures, not for 10,000+
- **Returns**: List of clusters (each cluster is a list of molecule indices)

### `pick_diverse(mols, npick, ...)`
Select diverse subset of molecules based on fingerprint diversity.

### `pick_centroids(mols, npick, ...)`
Select centroid molecules representing clusters.

## Graph Operations

### `to_graph(mol)`
Convert molecule to graph representation for graph-based analysis.

### `get_all_path_between(mol, start, end)`
Find all paths between two atoms in molecular structure.

## DataFrame Integration

### `to_df(mols, smiles_column='smiles', mol_column='mol')`
Convert list of molecules to pandas DataFrame.

### `from_df(df, smiles_column='smiles', mol_column='mol')`
Convert pandas DataFrame to list of molecules.

### `references/core_workflows.md`

# Datamol Core Workflows

The ten workflow areas in full, with worked code: basic molecule handling, reading and
writing molecular files (including cloud and compressed formats), descriptors and
properties, fingerprints and similarity, clustering and diversity selection, scaffold
analysis, fragmentation, 3D conformer generation, visualization, and chemical reactions.

## Core Workflows

### 1. Basic Molecule Handling

**Creating molecules from SMILES**:
```python
import datamol as dm

# Single molecule
mol = dm.to_mol("CCO")  # Ethanol

# From list of SMILES
smiles_list = ["CCO", "c1ccccc1", "CC(=O)O"]
mols = [dm.to_mol(smi) for smi in smiles_list]

# Error handling
mol = dm.to_mol("invalid_smiles")  # Returns None
if mol is None:
    print("Failed to parse SMILES")
```

**Converting molecules to SMILES**:
```python
# Canonical SMILES
smiles = dm.to_smiles(mol)

# Isomeric SMILES (includes stereochemistry)
smiles = dm.to_smiles(mol, isomeric=True)

# Other formats
inchi = dm.to_inchi(mol)
inchikey = dm.to_inchikey(mol)
selfies = dm.to_selfies(mol)
```

**Standardization and sanitization** (always recommend for user-provided molecules):
```python
# Sanitize molecule
mol = dm.sanitize_mol(mol)

# Full standardization (recommended for datasets)
mol = dm.standardize_mol(
    mol,
    disconnect_metals=True,
    normalize=True,
    reionize=True
)

# For SMILES strings directly
clean_smiles = dm.standardize_smiles(smiles)
```

### 2. Reading and Writing Molecular Files

Refer to `references/io_module.md` for comprehensive I/O documentation.

**Reading files**:
```python
# SDF files (most common in chemistry)
df = dm.read_sdf("compounds.sdf", mol_column='mol')

# SMILES files
df = dm.read_smi("molecules.smi", smiles_column='smiles', mol_column='mol')

# CSV with SMILES column
df = dm.read_csv("data.csv", smiles_column="SMILES", mol_column="mol")

# Excel files
df = dm.read_excel("compounds.xlsx", sheet_name=0, mol_column="mol")

# Universal reader/writer (auto-detects format; supports compression)
df = dm.open_df("file.sdf")  # .sdf, .csv, .xlsx, .parquet, .json, .gz, etc.
dm.save_df(df, "output.parquet")
```

**Writing files**:
```python
# Save as SDF
dm.to_sdf(mols, "output.sdf")
# Or from DataFrame
dm.to_sdf(df, "output.sdf", mol_column="mol")

# Save as SMILES file
dm.to_smi(mols, "output.smi")

# Excel with rendered molecule images
dm.to_xlsx(df, "output.xlsx", mol_columns=["mol"])
```

**Remote file support** (S3, GCS, HTTP via fsspec):

Only use cloud paths when the user explicitly requests them. Confirm the destination before writing.

```python
# Read from cloud storage or HTTPS (user-provided URLs only)
df = dm.read_sdf("s3://bucket/compounds.sdf")
df = dm.read_csv("https://example.com/data.csv")

# Write to cloud storage — confirm path with user first
dm.to_sdf(mols, "s3://bucket/output.sdf")
```

Cloud backends read credentials from the standard provider environment (for example `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, or `GOOGLE_APPLICATION_CREDENTIALS`). Datamol passes these to fsspec locally; it does not collect or transmit environment variables to third-party endpoints. Scope credential access to the named provider variables only.

### 3. Molecular Descriptors and Properties

Refer to `references/descriptors_viz.md` for detailed descriptor documentation.

**Computing descriptors for a single molecule**:
```python
# Get standard descriptor set
descriptors = dm.descriptors.compute_many_descriptors(mol)
# Returns: {'mw': 46.07, 'logp': -0.03, 'hbd': 1, 'hba': 1,
#           'tpsa': 20.23, 'n_aromatic_atoms': 0, ...}
```

**Batch descriptor computation** (recommended for datasets):
```python
# Compute for all molecules in parallel
desc_df = dm.descriptors.batch_compute_many_descriptors(
    mols,
    n_jobs=-1,      # Use all CPU cores
    progress=True   # Show progress bar
)
```

**Specific descriptors**:
```python
# Aromaticity
n_aromatic = dm.descriptors.n_aromatic_atoms(mol)
aromatic_ratio = dm.descriptors.n_aromatic_atoms_proportion(mol)

# Stereochemistry
n_stereo = dm.descriptors.n_stereo_centers(mol)
n_unspec = dm.descriptors.n_stereo_centers_unspecified(mol)

# Flexibility
n_rigid = dm.descriptors.n_rigid_bonds(mol)
```

**Drug-likeness filtering (Lipinski's Rule of Five)**:
```python
# Filter compounds
def is_druglike(mol):
    desc = dm.descriptors.compute_many_descriptors(mol)
    return (
        desc['mw'] <= 500 and
        desc['logp'] <= 5 and
        desc['hbd'] <= 5 and
        desc['hba'] <= 10
    )

druglike_mols = [mol for mol in mols if is_druglike(mol)]
```

### 4. Molecular Fingerprints and Similarity

**Generating fingerprints**:

Datamol defaults to ECFP6 (`radius=3`, `n_bits=2048`). Pass `radius=2` explicitly for ECFP4.

```python
# ECFP4 (common in similarity screening)
fp = dm.to_fp(mol, fp_type='ecfp', radius=2, n_bits=2048)

# Other fingerprint types
fp_maccs = dm.to_fp(mol, fp_type='maccs')
fp_topological = dm.to_fp(mol, fp_type='topological')
fp_atompair = dm.to_fp(mol, fp_type='atompair')
fp_rdkit = dm.to_fp(mol, fp_type='rdkit')
```

**Similarity calculations**:
```python
# Pairwise distances within a set
distance_matrix = dm.pdist(mols, n_jobs=-1)

# Distances between two sets
distances = dm.cdist(query_mols, library_mols, n_jobs=-1)

# Find most similar molecules (scipy is a PyPI package, not a file in this skill)
from scipy.spatial.distance import squareform  # third-party library
dist_matrix = squareform(dm.pdist(mols))
# Lower distance = higher similarity (Tanimoto distance = 1 - Tanimoto similarity)
```

### 5. Clustering and Diversity Selection

Refer to `references/core_api.md` for clustering details.

**Butina clustering**:
```python
# Cluster molecules by structural similarity
clusters = dm.cluster_mols(
    mols,
    cutoff=0.2,    # Tanimoto distance threshold (0=identical, 1=completely different)
    n_jobs=-1      # Parallel processing
)

# Each cluster is a list of molecule indices
for i, cluster in enumerate(clusters):
    print(f"Cluster {i}: {len(cluster)} molecules")
    cluster_mols = [mols[idx] for idx in cluster]
```

**Important**: Butina clustering builds a full distance matrix - suitable for ~1000 molecules, not for 10,000+.

**Diversity selection**:
```python
# Pick diverse subset
diverse_mols = dm.pick_diverse(
    mols,
    npick=100  # Select 100 diverse molecules
)

# Pick cluster centroids
centroids = dm.pick_centroids(
    mols,
    npick=50   # Select 50 representative molecules
)
```

### 6. Scaffold Analysis

Refer to `references/fragments_scaffolds.md` for complete scaffold documentation.

**Extracting Murcko scaffolds**:
```python
# Get Bemis-Murcko scaffold (core structure)
scaffold = dm.to_scaffold_murcko(mol)
scaffold_smiles = dm.to_smiles(scaffold)
```

**Scaffold-based analysis**:
```python
# Group compounds by scaffold
from collections import Counter

scaffolds = [dm.to_scaffold_murcko(mol) for mol in mols]
scaffold_smiles = [dm.to_smiles(s) for s in scaffolds]

# Count scaffold frequency
scaffold_counts = Counter(scaffold_smiles)
most_common = scaffold_counts.most_common(10)

# Create scaffold-to-molecules mapping
scaffold_groups = {}
for mol, scaf_smi in zip(mols, scaffold_smiles):
    if scaf_smi not in scaffold_groups:
        scaffold_groups[scaf_smi] = []
    scaffold_groups[scaf_smi].append(mol)
```

**Scaffold-based train/test splitting** (for ML):
```python
# Ensure train and test sets have different scaffolds
scaffold_to_mols = {}
for mol, scaf in zip(mols, scaffold_smiles):
    if scaf not in scaffold_to_mols:
        scaffold_to_mols[scaf] = []
    scaffold_to_mols[scaf].append(mol)

# Split scaffolds into train/test
import random
scaffolds = list(scaffold_to_mols.keys())
random.shuffle(scaffolds)
split_idx = int(0.8 * len(scaffolds))
train_scaffolds = scaffolds[:split_idx]
test_scaffolds = scaffolds[split_idx:]

# Get molecules for each split
train_mols = [mol for scaf in train_scaffolds for mol in scaffold_to_mols[scaf]]
test_mols = [mol for scaf in test_scaffolds for mol in scaffold_to_mols[scaf]]
```

### 7. Molecular Fragmentation

Refer to `references/fragments_scaffolds.md` for fragmentation details.

**BRICS fragmentation** (16 bond types):
```python
# Fragment molecule
fragments = dm.fragment.brics(mol)
# Returns: set of fragment SMILES with attachment points like '[1*]CCN'
```

**RECAP fragmentation** (11 bond types):
```python
fragments = dm.fragment.recap(mol)
```

**Fragment analysis**:
```python
# Find common fragments across compound library
from collections import Counter

all_fragments = []
for mol in mols:
    frags = dm.fragment.brics(mol)
    all_fragments.extend(frags)

fragment_counts = Counter(all_fragments)
common_frags = fragment_counts.most_common(20)

# Fragment-based scoring
def fragment_score(mol, reference_fragments):
    mol_frags = dm.fragment.brics(mol)
    overlap = mol_frags.intersection(reference_fragments)
    return len(overlap) / len(mol_frags) if mol_frags else 0
```

### 8. 3D Conformer Generation

Refer to `references/conformers_module.md` for detailed conformer documentation.

**Generating conformers**:
```python
# Generate 3D conformers
mol_3d = dm.conformers.generate(
    mol,
    n_confs=50,           # Number to generate (auto if None)
    rms_cutoff=0.5,       # Filter similar conformers (Ångströms)
    minimize_energy=True,  # Minimize with UFF force field
    method='ETKDGv3'      # Embedding method (recommended)
)

# Access conformers
n_conformers = mol_3d.GetNumConformers()
conf = mol_3d.GetConformer(0)  # Get first conformer
positions = conf.GetPositions()  # Nx3 array of atom coordinates
```

**Conformer clustering**:
```python
# Cluster conformers by RMSD
clusters = dm.conformers.cluster(
    mol_3d,
    rms_cutoff=1.0,
    centroids=False
)

# Get representative conformers
centroids = dm.conformers.return_centroids(mol_3d, clusters)
```

**SASA calculation**:
```python
# Calculate solvent accessible surface area
sasa_values = dm.conformers.sasa(mol_3d, n_jobs=-1)

# Access SASA from conformer properties
conf = mol_3d.GetConformer(0)
sasa = conf.GetDoubleProp('rdkit_free_sasa')
```

### 9. Visualization

Refer to `references/descriptors_viz.md` for visualization documentation.

**Basic molecule grid**:
```python
# Visualize molecules
dm.viz.to_image(
    mols[:20],
    legends=[dm.to_smiles(m) for m in mols[:20]],
    n_cols=5,
    mol_size=(300, 300)
)

# Save to file
dm.viz.to_image(mols, outfile="molecules.png")

# SVG for publications
dm.viz.to_image(mols, outfile="molecules.svg", use_svg=True)
```

**Aligned visualization** (for SAR analysis):
```python
# Align molecules by common substructure
dm.viz.to_image(
    similar_mols,
    align=True,  # Enable MCS alignment
    legends=activity_labels,
    n_cols=4
)
```

**Highlighting substructures**:
```python
# Highlight specific atoms and bonds
dm.viz.to_image(
    mol,
    highlight_atom=[0, 1, 2, 3],  # Atom indices
    highlight_bond=[0, 1, 2]      # Bond indices
)
```

**Conformer visualization**:
```python
# Display multiple conformers
dm.viz.conformers(
    mol_3d,
    n_confs=10,
    align_conf=True,
    n_cols=3
)
```

### 10. Chemical Reactions

Refer to `references/reactions_data.md` for reactions documentation.

**Applying reactions**:
```python
from rdkit.Chem import rdChemReactions

# Define reaction from SMARTS
rxn_smarts = '[C:1](=[O:2])[OH:3]>>[C:1](=[O:2])[Cl:3]'
rxn = rdChemReactions.ReactionFromSmarts(rxn_smarts)

# Apply to molecule
reactant = dm.to_mol("CC(=O)O")  # Acetic acid
product = dm.reactions.apply_reaction(
    rxn,
    (reactant,),
    sanitize=True
)

# Convert to SMILES
product_smiles = dm.to_smiles(product)
```

**Batch reaction application**:
```python
# Apply reaction to library
products = []
for mol in reactant_mols:
    try:
        prod = dm.reactions.apply_reaction(rxn, (mol,))
        if prod is not None:
            products.append(prod)
    except Exception as e:
        print(f"Reaction failed: {e}")
```

### `references/descriptors_viz.md`

# Datamol Descriptors and Visualization Reference

## Descriptors Module (`datamol.descriptors`)

The descriptors module provides tools for computing molecular properties and descriptors.

### Specialized Descriptor Functions

#### `dm.descriptors.n_aromatic_atoms(mol)`
Calculate the number of aromatic atoms.
- **Returns**: Integer count
- **Use case**: Aromaticity analysis

#### `dm.descriptors.n_aromatic_atoms_proportion(mol)`
Calculate ratio of aromatic atoms to total heavy atoms.
- **Returns**: Float between 0 and 1
- **Use case**: Quantifying aromatic character

#### `dm.descriptors.n_charged_atoms(mol)`
Count atoms with nonzero formal charge.
- **Returns**: Integer count
- **Use case**: Charge distribution analysis

#### `dm.descriptors.n_rigid_bonds(mol)`
Count non-rotatable bonds (neither single bonds nor ring bonds).
- **Returns**: Integer count
- **Use case**: Molecular flexibility assessment

#### `dm.descriptors.n_stereo_centers(mol)`
Count stereogenic centers (chiral centers).
- **Returns**: Integer count
- **Use case**: Stereochemistry analysis

#### `dm.descriptors.n_stereo_centers_unspecified(mol)`
Count stereocenters lacking stereochemical specification.
- **Returns**: Integer count
- **Use case**: Identifying incomplete stereochemistry

### Batch Descriptor Computation

#### `dm.descriptors.compute_many_descriptors(mol, properties_fn=None, add_properties=True)`
Compute multiple molecular properties for a single molecule.
- **Parameters**:
  - `properties_fn`: Custom list of descriptor functions
  - `add_properties`: Include additional computed properties
- **Returns**: Dictionary of descriptor name → value pairs
- **Default descriptors include**:
  - Molecular weight, LogP, number of H-bond donors/acceptors
  - Aromatic atoms, stereocenters, rotatable bonds
  - TPSA (Topological Polar Surface Area)
  - Ring count, heteroatom count
- **Example**:
  ```python
  mol = dm.to_mol("CCO")
  descriptors = dm.descriptors.compute_many_descriptors(mol)
  # Returns: {'mw': 46.07, 'logp': -0.03, 'hbd': 1, 'hba': 1, ...}
  ```

#### `dm.descriptors.batch_compute_many_descriptors(mols, properties_fn=None, add_properties=True, n_jobs=1, batch_size=None, progress=False)`
Compute descriptors for multiple molecules in parallel.
- **Parameters**:
  - `mols`: List of molecules
  - `n_jobs`: Number of parallel jobs (-1 for all cores)
  - `batch_size`: Chunk size for parallel processing
  - `progress`: Show progress bar
- **Returns**: Pandas DataFrame with one row per molecule
- **Example**:
  ```python
  mols = [dm.to_mol(smi) for smi in smiles_list]
  df = dm.descriptors.batch_compute_many_descriptors(
      mols,
      n_jobs=-1,
      progress=True
  )
  ```

### RDKit Descriptor Access

#### `dm.descriptors.any_rdkit_descriptor(name)`
Retrieve any descriptor function from RDKit by name.
- **Parameters**: `name` - Descriptor function name (e.g., 'MolWt', 'TPSA')
- **Returns**: RDKit descriptor function
- **Available descriptors**: From `rdkit.Chem.Descriptors` and `rdkit.Chem.rdMolDescriptors`
- **Example**:
  ```python
  tpsa_fn = dm.descriptors.any_rdkit_descriptor('TPSA')
  tpsa_value = tpsa_fn(mol)
  ```

### Common Use Cases

**Drug-likeness Filtering (Lipinski's Rule of Five)**:
```python
descriptors = dm.descriptors.compute_many_descriptors(mol)
is_druglike = (
    descriptors['mw'] <= 500 and
    descriptors['logp'] <= 5 and
    descriptors['hbd'] <= 5 and
    descriptors['hba'] <= 10
)
```

**ADME Property Analysis**:
```python
df = dm.descriptors.batch_compute_many_descriptors(compound_library)
# Filter by TPSA for blood-brain barrier penetration
bbb_candidates = df[df['tpsa'] < 90]
```

---

## Visualization Module (`datamol.viz`)

The viz module provides tools for rendering molecules and conformers as images.

### Main Visualization Function

#### `dm.viz.to_image(mols, legends=None, n_cols=4, use_svg=False, mol_size=(200, 200), highlight_atom=None, highlight_bond=None, outfile=None, max_mols=None, copy=True, indices=False, ...)`
Generate image grid from molecules.
- **Parameters**:
  - `mols`: Single molecule or list of molecules
  - `legends`: String or list of strings as labels (one per molecule)
  - `n_cols`: Number of molecules per row (default: 4)
  - `use_svg`: Output SVG format (True) or PNG (False, default)
  - `mol_size`: Tuple (width, height) or single int for square images
  - `highlight_atom`: Atom indices to highlight (list or dict)
  - `highlight_bond`: Bond indices to highlight (list or dict)
  - `outfile`: Save path (local or remote, supports fsspec)
  - `max_mols`: Maximum number of molecules to display
  - `indices`: Draw atom indices on structures (default: False)
  - `align`: Align molecules using MCS (Maximum Common Substructure)
- **Returns**: Image object (can be displayed in Jupyter) or saves to file
- **Example**:
  ```python
  # Basic grid
  dm.viz.to_image(mols[:10], legends=[dm.to_smiles(m) for m in mols[:10]])

  # Save to file
  dm.viz.to_image(mols, outfile="molecules.png", n_cols=5)

  # Highlight substructure
  dm.viz.to_image(mol, highlight_atom=[0, 1, 2], highlight_bond=[0, 1])

  # Aligned visualization
  dm.viz.to_image(mols, align=True, legends=activity_labels)
  ```

### Conformer Visualization

#### `dm.viz.conformers(mol, n_confs=None, align_conf=True, n_cols=3, sync_views=True, remove_hs=True, ...)`
Display multiple conformers in grid layout.
- **Parameters**:
  - `mol`: Molecule with embedded conformers
  - `n_confs`: Number or list of conformer indices to display (None = all)
  - `align_conf`: Align conformers for comparison (default: True)
  - `n_cols`: Grid columns (default: 3)
  - `sync_views`: Synchronize 3D views when interactive (default: True)
  - `remove_hs`: Remove hydrogens for clarity (default: True)
- **Returns**: Grid of conformer visualizations
- **Use case**: Comparing conformational diversity
- **Example**:
  ```python
  mol_3d = dm.conformers.generate(mol, n_confs=20)
  dm.viz.conformers(mol_3d, n_confs=10, align_conf=True)
  ```

### Circle Grid Visualization

#### `dm.viz.circle_grid(center_mol, circle_mols, mol_size=200, circle_margin=50, act_mapper=None, ...)`
Create concentric ring visualization with central molecule.
- **Parameters**:
  - `center_mol`: Molecule at center
  - `circle_mols`: List of molecule lists (one list per ring)
  - `mol_size`: Image size per molecule
  - `circle_margin`: Spacing between rings (default: 50)
  - `act_mapper`: Activity mapping dictionary for color-coding
- **Returns**: Circular grid image
- **Use case**: Visualizing molecular neighborhoods, SAR analysis, similarity networks
- **Example**:
  ```python
  # Show a reference molecule surrounded by similar compounds
  dm.viz.circle_grid(
      center_mol=reference,
      circle_mols=[nearest_neighbors, second_tier]
  )
  ```

### Visualization Best Practices

1. **Use legends for clarity**: Always label molecules with SMILES, IDs, or activity values
2. **Align related molecules**: Use `align=True` in `to_image()` for SAR analysis
3. **Adjust grid size**: Set `n_cols` based on molecule count and display width
4. **Use SVG for publications**: Set `use_svg=True` for scalable vector graphics
5. **Highlight substructures**: Use `highlight_atom` and `highlight_bond` to emphasize features
6. **Save large grids**: Use `outfile` parameter to save rather than display in memory

### `references/fragments_scaffolds.md`

# Datamol Fragments and Scaffolds Reference

## Scaffolds Module (`datamol.scaffold`)

Scaffolds represent the core structure of molecules, useful for identifying structural families and analyzing structure-activity relationships (SAR).

### Murcko Scaffolds

#### `dm.to_scaffold_murcko(mol)`
Extract Bemis-Murcko scaffold (molecular framework).
- **Method**: Removes side chains, retaining ring systems and linkers
- **Returns**: Molecule object representing the scaffold
- **Use case**: Identify core structures across compound series
- **Example**:
  ```python
  mol = dm.to_mol("c1ccc(cc1)CCN")  # Phenethylamine
  scaffold = dm.to_scaffold_murcko(mol)
  scaffold_smiles = dm.to_smiles(scaffold)
  # Returns: 'c1ccccc1CC' (benzene ring + ethyl linker)
  ```

**Workflow for scaffold analysis**:
```python
# Extract scaffolds from compound library
scaffolds = [dm.to_scaffold_murcko(mol) for mol in mols]
scaffold_smiles = [dm.to_smiles(s) for s in scaffolds]

# Count scaffold frequency
from collections import Counter
scaffold_counts = Counter(scaffold_smiles)
most_common = scaffold_counts.most_common(10)
```

### Fuzzy Scaffolds

#### `dm.scaffold.fuzzy_scaffolding(mol, ...)`
Generate fuzzy scaffolds with enforceable groups that must appear in the core.
- **Purpose**: More flexible scaffold definition allowing specified functional groups
- **Use case**: Custom scaffold definitions beyond Murcko rules

### Applications

**Scaffold-based splitting** (for ML model validation):
```python
# Group compounds by scaffold
scaffold_to_mols = {}
for mol, scaffold in zip(mols, scaffolds):
    smi = dm.to_smiles(scaffold)
    if smi not in scaffold_to_mols:
        scaffold_to_mols[smi] = []
    scaffold_to_mols[smi].append(mol)

# Ensure train/test sets have different scaffolds
```

**SAR analysis**:
```python
# Group by scaffold and analyze activity
for scaffold_smi, molecules in scaffold_to_mols.items():
    activities = [get_activity(mol) for mol in molecules]
    print(f"Scaffold: {scaffold_smi}, Mean activity: {np.mean(activities)}")
```

---

## Fragments Module (`datamol.fragment`)

Molecular fragmentation breaks molecules into smaller pieces based on chemical rules, useful for fragment-based drug design and substructure analysis.

### BRICS Fragmentation

#### `dm.fragment.brics(mol, ...)`
Fragment molecule using BRICS (Breaking Retrosynthetically Interesting Chemical Substructures).
- **Method**: Dissects based on 16 chemically meaningful bond types
- **Consideration**: Considers chemical environment and surrounding substructures
- **Returns**: Set of fragment SMILES strings
- **Use case**: Retrosynthetic analysis, fragment-based design
- **Example**:
  ```python
  mol = dm.to_mol("c1ccccc1CCN")
  fragments = dm.fragment.brics(mol)
  # Returns fragments like: '[1*]CCN', '[1*]c1ccccc1', etc.
  # [1*] represents attachment points
  ```

### RECAP Fragmentation

#### `dm.fragment.recap(mol, ...)`
Fragment molecule using RECAP (Retrosynthetic Combinatorial Analysis Procedure).
- **Method**: Dissects based on 11 predefined bond types
- **Rules**:
  - Leaves alkyl groups smaller than 5 carbons intact
  - Preserves cyclic bonds
- **Returns**: Set of fragment SMILES strings
- **Use case**: Combinatorial library design
- **Example**:
  ```python
  mol = dm.to_mol("CCCCCc1ccccc1")
  fragments = dm.fragment.recap(mol)
  ```

### MMPA Fragmentation

#### `dm.fragment.mmpa_frag(mol, ...)`
Fragment for Matched Molecular Pair Analysis.
- **Purpose**: Generate fragments suitable for identifying molecular pairs
- **Use case**: Analyzing how small structural changes affect properties
- **Example**:
  ```python
  fragments = dm.fragment.mmpa_frag(mol)
  # Used to find pairs of molecules differing by single transformation
  ```

### Comparison of Methods

| Method | Bond Types | Preserves Cycles | Best For |
|--------|-----------|------------------|----------|
| BRICS  | 16        | Yes              | Retrosynthetic analysis, fragment recombination |
| RECAP  | 11        | Yes              | Combinatorial library design |
| MMPA   | Variable  | Depends          | Structure-activity relationship analysis |

### Fragmentation Workflow

```python
import datamol as dm

# 1. Fragment a molecule
mol = dm.to_mol("CC(=O)Oc1ccccc1C(=O)O")  # Aspirin
brics_frags = dm.fragment.brics(mol)
recap_frags = dm.fragment.recap(mol)

# 2. Analyze fragment frequency across library
all_fragments = []
for mol in molecule_library:
    frags = dm.fragment.brics(mol)
    all_fragments.extend(frags)

# 3. Identify common fragments
from collections import Counter
fragment_counts = Counter(all_fragments)
common_fragments = fragment_counts.most_common(20)

# 4. Convert fragments back to molecules (remove attachment points)
def clean_fragment(frag_smiles):
    # Remove [1*], [2*], etc. attachment point markers
    clean = frag_smiles.replace('[1*]', '[H]')
    return dm.to_mol(clean)
```

### Advanced: Fragment-Based Virtual Screening

```python
# Build fragment library from known actives
active_fragments = set()
for active_mol in active_compounds:
    frags = dm.fragment.brics(active_mol)
    active_fragments.update(frags)

# Screen compounds for presence of active fragments
def score_by_fragments(mol, fragment_set):
    mol_frags = dm.fragment.brics(mol)
    overlap = mol_frags.intersection(fragment_set)
    return len(overlap) / len(mol_frags)

# Score screening library
scores = [score_by_fragments(mol, active_fragments) for mol in screening_lib]
```

### Key Concepts

- **Attachment Points**: Marked with [1*], [2*], etc. in fragment SMILES
- **Retrosynthetic**: Fragmentation mimics synthetic disconnections
- **Chemically Meaningful**: Breaks occur at typical synthetic bonds
- **Recombination**: Fragments can theoretically be recombined into valid molecules

### `references/io_module.md`

# Datamol I/O Module Reference

The `datamol.io` module provides comprehensive file handling for molecular data across multiple formats.

## Reading Molecular Files

### `dm.read_sdf(filename, sanitize=True, remove_hs=True, as_df=True, mol_column='mol', ...)`
Read Structure-Data File (SDF) format.
- **Parameters**:
  - `filename`: Path to SDF file (supports local and remote paths via fsspec)
  - `sanitize`: Apply sanitization to molecules
  - `remove_hs`: Remove explicit hydrogens
  - `as_df`: Return as DataFrame (True) or list of molecules (False)
  - `mol_column`: Name of molecule column in DataFrame
  - `n_jobs`: Enable parallel processing
- **Returns**: DataFrame or list of molecules
- **Example**: `df = dm.read_sdf("compounds.sdf")`

### `dm.read_smi(filename, smiles_column='smiles', mol_column='mol', as_df=True, ...)`
Read SMILES file (space-delimited by default).
- **Common format**: SMILES followed by molecule ID/name
- **Example**: `df = dm.read_smi("molecules.smi")`

### `dm.read_csv(filename, smiles_column='smiles', mol_column=None, ...)`
Read CSV file with optional automatic SMILES-to-molecule conversion.
- **Parameters**:
  - `smiles_column`: Column containing SMILES strings
  - `mol_column`: If specified, creates molecule objects from SMILES column
- **Example**: `df = dm.read_csv("data.csv", smiles_column="SMILES", mol_column="mol")`

### `dm.read_excel(filename, sheet_name=0, smiles_column='smiles', mol_column=None, ...)`
Read Excel files with molecule handling.
- **Parameters**:
  - `sheet_name`: Sheet to read (index or name)
  - Other parameters similar to `read_csv`
- **Example**: `df = dm.read_excel("compounds.xlsx", sheet_name="Sheet1")`

### `dm.read_molblock(molblock, sanitize=True, remove_hs=True)`
Parse MOL block string (molecular structure text representation).

### `dm.read_mol2file(filename, sanitize=True, remove_hs=True, cleanupSubstructures=True)`
Read Mol2 format files.

### `dm.read_pdbfile(filename, sanitize=True, remove_hs=True, proximityBonding=True)`
Read Protein Data Bank (PDB) format files.

### `dm.read_pdbblock(pdbblock, sanitize=True, remove_hs=True, proximityBonding=True)`
Parse PDB block string.

### `dm.open_df(filename, ...)`
Universal DataFrame reader - automatically detects format.
- **Supported formats**: CSV, Excel, Parquet, JSON, SDF (including compressed files such as `.gz`)
- **Example**: `df = dm.open_df("data.csv")` or `df = dm.open_df("molecules.sdf.gz")`

## Writing Molecular Files

### `dm.to_sdf(mols, filename, mol_column=None, ...)`
Write molecules to SDF file.
- **Input types**:
  - List of molecules
  - DataFrame with molecule column
  - Sequence of molecules
- **Parameters**:
  - `mol_column`: Column name if input is DataFrame
- **Example**:
  ```python
  dm.to_sdf(mols, "output.sdf")
  # or from DataFrame
  dm.to_sdf(df, "output.sdf", mol_column="mol")
  ```

### `dm.to_smi(mols, filename, mol_column=None, ...)`
Write molecules to SMILES file with optional validation.
- **Format**: SMILES strings with optional molecule names/IDs

### `dm.to_xlsx(df, filename, mol_columns=None, ...)`
Export DataFrame to Excel with rendered molecular images.
- **Parameters**:
  - `mol_columns`: Columns containing molecules to render as images
- **Special feature**: Automatically renders molecules as images in Excel cells
- **Example**: `dm.to_xlsx(df, "molecules.xlsx", mol_columns=["mol"])`

### `dm.to_molblock(mol, ...)`
Convert molecule to MOL block string.

### `dm.to_pdbblock(mol, ...)`
Convert molecule to PDB block string.

### `dm.save_df(df, filename, ...)`
Save DataFrame in multiple formats (CSV, Excel, Parquet, JSON). Auto-detects format from the file extension; supports compression (added in datamol 0.10.0).

## Remote File Support

All I/O functions support remote file paths through fsspec integration:
- **Supported protocols**: S3 (AWS), GCS (Google Cloud), Azure, HTTP/HTTPS
- **Optional backends**: `uv pip install s3fs` (S3), `uv pip install gcsfs` (GCS)
- **Credentials**: Standard provider environment variables only (`AWS_*`, `GOOGLE_APPLICATION_CREDENTIALS`, etc.). Datamol uses fsspec locally; confirm remote write paths with the user before saving.
- **Example**:
  ```python
  dm.read_sdf("s3://bucket/compounds.sdf")
  dm.read_csv("https://example.com/data.csv")
  dm.save_df(df, "s3://bucket/output.parquet")  # confirm destination first
  ```

## Key Parameters Across Functions

- **`sanitize`**: Apply molecule sanitization (default: True)
- **`remove_hs`**: Remove explicit hydrogens (default: True)
- **`as_df`**: Return DataFrame vs list (default: True for most functions)
- **`n_jobs`**: Enable parallel processing (None = all cores, 1 = sequential)
- **`mol_column`**: Name of molecule column in DataFrames
- **`smiles_column`**: Name of SMILES column in DataFrames

### `references/reactions_data.md`

# Datamol Reactions and Data Modules Reference

## Reactions Module (`datamol.reactions`)

The reactions module enables programmatic application of chemical transformations using SMARTS reaction patterns.

### Applying Chemical Reactions

#### `dm.reactions.apply_reaction(rxn, reactants, as_smiles=False, sanitize=True, single_product_group=True, rm_attach=True, product_index=0)`
Apply a chemical reaction to reactant molecules.
- **Parameters**:
  - `rxn`: Reaction object (from SMARTS pattern)
  - `reactants`: Tuple of reactant molecules
  - `as_smiles`: Return SMILES strings (True) or molecule objects (False)
  - `sanitize`: Sanitize product molecules
  - `single_product_group`: Return single product (True) or all product groups (False)
  - `rm_attach`: Remove attachment point markers
  - `product_index`: Which product to return from reaction
- **Returns**: Product molecule(s) or SMILES
- **Example**:
  ```python
  from rdkit import Chem

  # Define reaction: alcohol + carboxylic acid → ester
  rxn = Chem.rdChemReactions.ReactionFromSmarts(
      '[C:1][OH:2].[C:3](=[O:4])[OH:5]>>[C:1][O:2][C:3](=[O:4])'
  )

  # Apply to reactants
  alcohol = dm.to_mol("CCO")
  acid = dm.to_mol("CC(=O)O")
  product = dm.reactions.apply_reaction(rxn, (alcohol, acid))
  ```

### Creating Reactions

Reactions are typically created from SMARTS patterns using RDKit:
```python
from rdkit.Chem import rdChemReactions

# Reaction pattern: [reactant1].[reactant2]>>[product]
rxn = rdChemReactions.ReactionFromSmarts(
    '[1*][*:1].[1*][*:2]>>[*:1][*:2]'
)
```

### Validation Functions

The module includes functions to:
- **Check if molecule is reactant**: Verify if molecule matches reactant pattern
- **Validate reaction**: Check if reaction is synthetically reasonable
- **Process reaction files**: Load reactions from files or databases

### Common Reaction Patterns

**Amide formation**:
```python
# Amine + carboxylic acid → amide
amide_rxn = rdChemReactions.ReactionFromSmarts(
    '[N:1].[C:2](=[O:3])[OH]>>[N:1][C:2](=[O:3])'
)
```

**Suzuki coupling**:
```python
# Aryl halide + boronic acid → biaryl
suzuki_rxn = rdChemReactions.ReactionFromSmarts(
    '[c:1][Br].[c:2][B]([OH])[OH]>>[c:1][c:2]'
)
```

**Functional group transformations**:
```python
# Alcohol → ester
esterification = rdChemReactions.ReactionFromSmarts(
    '[C:1][OH:2].[C:3](=[O:4])[Cl]>>[C:1][O:2][C:3](=[O:4])'
)
```

### Workflow Example

```python
import datamol as dm
from rdkit.Chem import rdChemReactions

# 1. Define reaction
rxn_smarts = '[C:1](=[O:2])[OH:3]>>[C:1](=[O:2])[Cl:3]'  # Acid → acid chloride
rxn = rdChemReactions.ReactionFromSmarts(rxn_smarts)

# 2. Apply to molecule library
acids = [dm.to_mol(smi) for smi in acid_smiles_list]
acid_chlorides = []

for acid in acids:
    try:
        product = dm.reactions.apply_reaction(
            rxn,
            (acid,),  # Single reactant as tuple
            sanitize=True
        )
        acid_chlorides.append(product)
    except Exception as e:
        print(f"Reaction failed: {e}")

# 3. Validate products
valid_products = [p for p in acid_chlorides if p is not None]
```

### Key Concepts

- **SMARTS**: SMiles ARbitrary Target Specification - pattern language for reactions
- **Atom Mapping**: Numbers like [C:1] preserve atom identity through reaction
- **Attachment Points**: [1*] represents generic connection points
- **Reaction Validation**: Not all SMARTS reactions are chemically reasonable

---

## Data Module (`datamol.data`)

The data module provides convenient access to curated molecular datasets for testing and learning.

### Available Datasets

#### `dm.data.cdk2(as_df=True, mol_column='mol')`
RDKit CDK2 dataset - kinase inhibitor data.
- **Parameters**:
  - `as_df`: Return as DataFrame (True) or list of molecules (False)
  - `mol_column`: Name for molecule column
- **Returns**: Dataset with molecular structures and activity data
- **Use case**: Small dataset for algorithm testing
- **Example**:
  ```python
  cdk2_df = dm.data.cdk2(as_df=True)
  print(cdk2_df.shape)
  print(cdk2_df.columns)
  ```

#### `dm.data.freesolv()`
FreeSolv dataset - experimental and calculated hydration free energies.
- **Contents**: 642 molecules with:
  - IUPAC names
  - SMILES strings
  - Experimental hydration free energy values
  - Calculated values
- **Warning**: "Only meant to be used as a toy dataset for pedagogic and testing purposes"
- **Not suitable for**: Benchmarking or production model training
- **Example**:
  ```python
  freesolv_df = dm.data.freesolv()
  # Columns: iupac, smiles, expt (kcal/mol), calc (kcal/mol)
  ```

#### `dm.data.solubility(as_df=True, mol_column='mol')`
RDKit solubility dataset with train/test splits.
- **Contents**: Aqueous solubility data with pre-defined splits
- **Columns**: Includes 'split' column with 'train' or 'test' values
- **Use case**: Testing ML workflows with proper train/test separation
- **Example**:
  ```python
  sol_df = dm.data.solubility(as_df=True)

  # Split into train/test
  train_df = sol_df[sol_df['split'] == 'train']
  test_df = sol_df[sol_df['split'] == 'test']

  # Use for model development
  X_train = dm.to_fp(train_df[mol_column])
  y_train = train_df['solubility']
  ```

### Usage Guidelines

**For testing and tutorials**:
```python
# Quick dataset for testing code
df = dm.data.cdk2()
mols = df['mol'].tolist()

# Test descriptor calculation
descriptors_df = dm.descriptors.batch_compute_many_descriptors(mols)

# Test clustering
clusters = dm.cluster_mols(mols, cutoff=0.3)
```

**For learning workflows**:
```python
# Complete ML pipeline example
sol_df = dm.data.solubility()

# Preprocessing
train = sol_df[sol_df['split'] == 'train']
test = sol_df[sol_df['split'] == 'test']

# Featurization
X_train = dm.to_fp(train['mol'])
X_test = dm.to_fp(test['mol'])

# Model training (example; scikit-learn is a PyPI dependency, not a bundled skill script)
from sklearn.ensemble import RandomForestRegressor  # third-party library
model = RandomForestRegressor()
model.fit(X_train, train['solubility'])
predictions = model.predict(X_test)
```

### Important Notes

- **Toy Datasets**: Designed for pedagogical purposes, not production use
- **Small Size**: Limited number of compounds suitable for quick tests
- **Pre-processed**: Data already cleaned and formatted
- **Citations**: Check dataset documentation for proper attribution if publishing

### Best Practices

1. **Use for development only**: Don't draw scientific conclusions from toy datasets
2. **Validate on real data**: Always test production code on actual project data
3. **Proper attribution**: Cite original data sources if using in publications
4. **Understand limitations**: Know the scope and quality of each dataset

### `references/workflow_patterns.md`

# Common Workflow Patterns

Three end-to-end pipelines: data loading through filtering to analysis, structure-activity
relationship analysis by scaffold series, and a virtual screening pipeline.

## Common Workflows and Patterns

### Complete Pipeline: Data Loading → Filtering → Analysis

```python
import datamol as dm
import pandas as pd

# 1. Load molecules
df = dm.read_sdf("compounds.sdf")

# 2. Standardize
df['mol'] = df['mol'].apply(lambda m: dm.standardize_mol(m) if m else None)
df = df[df['mol'].notna()]  # Remove failed molecules

# 3. Compute descriptors
desc_df = dm.descriptors.batch_compute_many_descriptors(
    df['mol'].tolist(),
    n_jobs=-1,
    progress=True
)

# 4. Filter by drug-likeness
druglike = (
    (desc_df['mw'] <= 500) &
    (desc_df['logp'] <= 5) &
    (desc_df['hbd'] <= 5) &
    (desc_df['hba'] <= 10)
)
filtered_df = df[druglike]

# 5. Cluster and select diverse subset
diverse_mols = dm.pick_diverse(
    filtered_df['mol'].tolist(),
    npick=100
)

# 6. Visualize results
dm.viz.to_image(
    diverse_mols,
    legends=[dm.to_smiles(m) for m in diverse_mols],
    outfile="diverse_compounds.png",
    n_cols=10
)
```

### Structure-Activity Relationship (SAR) Analysis

```python
# Group by scaffold
scaffolds = [dm.to_scaffold_murcko(mol) for mol in mols]
scaffold_smiles = [dm.to_smiles(s) for s in scaffolds]

# Create DataFrame with activities
sar_df = pd.DataFrame({
    'mol': mols,
    'scaffold': scaffold_smiles,
    'activity': activities  # User-provided activity data
})

# Analyze each scaffold series
for scaffold, group in sar_df.groupby('scaffold'):
    if len(group) >= 3:  # Need multiple examples
        print(f"\nScaffold: {scaffold}")
        print(f"Count: {len(group)}")
        print(f"Activity range: {group['activity'].min():.2f} - {group['activity'].max():.2f}")

        # Visualize with activities as legends
        dm.viz.to_image(
            group['mol'].tolist(),
            legends=[f"Activity: {act:.2f}" for act in group['activity']],
            align=True  # Align by common substructure
        )
```

### Virtual Screening Pipeline

```python
import numpy as np

# 1. Calculate Tanimoto distances between query actives and library
distances = dm.cdist(query_actives, library_mols, n_jobs=-1)

# 3. Find closest matches (min distance to any query)
min_distances = distances.min(axis=0)
similarities = 1 - min_distances  # Convert distance to similarity

# 4. Rank and select top hits
top_indices = np.argsort(similarities)[::-1][:100]  # Top 100
top_hits = [library_mols[i] for i in top_indices]
top_scores = [similarities[i] for i in top_indices]

# 5. Visualize hits
dm.viz.to_image(
    top_hits[:20],
    legends=[f"Sim: {score:.3f}" for score in top_scores[:20]],
    outfile="screening_hits.png"
)
```
