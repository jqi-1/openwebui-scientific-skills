---
name: scikit-bio
description: Biological data toolkit. Sequence analysis, alignments, phylogenetic trees, diversity metrics (alpha/beta, UniFrac), ordination (PCoA), PERMANOVA, FASTA/Newick I/O, for microbiome analysis.
---

# scikit-bio

## Overview

scikit-bio is a comprehensive Python library for working with biological data. Apply this skill for bioinformatics analyses spanning sequence manipulation, alignment, phylogenetics, microbial ecology, and multivariate statistics.

## When to Use This Skill

This skill should be used when the user:
- Works with biological sequences (DNA, RNA, protein)
- Needs to read/write biological file formats (FASTA, FASTQ, GenBank, Newick, BIOM, etc.)
- Performs sequence alignments or searches for motifs
- Constructs or analyzes phylogenetic trees
- Calculates diversity metrics (alpha/beta diversity, UniFrac distances)
- Performs ordination analysis (PCoA, CCA, RDA)
- Runs statistical tests on biological/ecological data (PERMANOVA, ANOSIM, Mantel)
- Analyzes microbiome or community ecology data
- Works with protein embeddings from language models
- Needs to manipulate biological data tables

## Core Capabilities

### 1. Sequence Manipulation

Work with biological sequences using specialized classes for DNA, RNA, and protein data.

**Key operations:**
- Read/write sequences from FASTA, FASTQ, GenBank, EMBL formats
- Sequence slicing, concatenation, and searching
- Reverse complement, transcription (DNA→RNA), and translation (RNA→protein)
- Find motifs and patterns using regex
- Calculate distances (Hamming, k-mer based)
- Handle sequence quality scores and metadata

**Common patterns:**
```python
import skbio

# Read sequences from file
seq = skbio.DNA.read('input.fasta')

# Sequence operations
rc = seq.reverse_complement()
rna = seq.transcribe()
protein = rna.translate()

# Find motifs
motif_positions = seq.find_with_regex('ATG[ACGT]{3}')

# Check for properties
has_degens = seq.has_degenerates()
seq_no_gaps = seq.degap()
```

**Important notes:**
- Use `DNA`, `RNA`, `Protein` classes for grammared sequences with validation
- Use `Sequence` class for generic sequences without alphabet restrictions
- Quality scores automatically loaded from FASTQ files into positional metadata
- Metadata types: sequence-level (ID, description), positional (per-base), interval (regions/features)

### 2. Sequence Alignment

Perform pairwise and multiple sequence alignments using the `pair_align` engine (introduced in scikit-bio 0.7.0), a versatile and efficient dynamic-programming aligner.

**Key capabilities:**
- Global, local, and semi-global alignment (free ends configurable) in one function
- Convenience wrappers `pair_align_nucl` (BLASTN-like) and `pair_align_prot` (BLASTP-like)
- Configurable scoring: match/mismatch tuple or named substitution matrix; linear or affine gap penalties
- `PairAlignPath` results carry CIGAR strings and convert to aligned sequences
- Multiple sequence alignment storage and manipulation with `TabularMSA`

**Common patterns:**
```python
from skbio import DNA, Protein
from skbio.alignment import pair_align_nucl, pair_align_prot, pair_align, TabularMSA

# Nucleotide alignment with BLASTN-like defaults
seq1, seq2 = DNA('ACTACCAGATTACTTACGGATCAGG'), DNA('CGAAACTACTAGATTACGGATCTTA')
aln = pair_align_nucl(seq1, seq2)
aln.score                                  # alignment score (float)
path = aln.paths[0]                        # PairAlignPath (repr shows CIGAR)
aligned_seqs = path.to_aligned((seq1, seq2))  # list of gapped strings

# Build a TabularMSA from the alignment path + original sequences
msa = TabularMSA.from_path_seqs(path, (seq1, seq2))

# Customize the algorithm via pair_align (default mode='global')
aln = pair_align(seq1, seq2, mode='local')                       # Smith-Waterman
aln = pair_align(seq1, seq2, sub_score=(2, -3), gap_cost=(5, 2)) # affine gaps
aln = pair_align(seq1, seq2, sub_score='NUC.4.4', gap_cost=3)    # substitution matrix, linear gap

# Protein alignment (BLASTP-like, BLOSUM62)
aln = pair_align_prot(Protein('HEAGAWGHEE'), Protein('PAWHEAE'))

# Read a multiple alignment from file and summarize
msa = TabularMSA.read('alignment.fasta', constructor=DNA)
consensus = msa.consensus()
```

**Important notes:**
- `pair_align` replaces the removed SSW wrapper (`local_pairwise_align_ssw`, `StripedSmithWaterman`) and the deprecated pure-Python aligners (`global_pairwise_align`, `local_pairwise_align_nucleotide`, etc.)
- The result is a `PairAlignResult` that also unpacks as `score, paths, matrices` (use `keep_matrices=True` to retain the DP matrix)
- `sub_score` accepts a `(match, mismatch)` tuple or a matrix name (e.g., `'NUC.4.4'`, `'BLOSUM62'`); `gap_cost` accepts a single number (linear) or `(open, extend)` tuple (affine)
- Parse external CIGAR strings with `PairAlignPath.from_cigar('1I8M2D5M2I')`; score an existing alignment with `align_score(...)` and build a distance matrix from an MSA with `align_dists(...)`

### 3. Phylogenetic Trees

Construct, manipulate, and analyze phylogenetic trees representing evolutionary relationships.

**Key capabilities:**
- Tree construction from distance matrices (UPGMA/WPGMA, Neighbor Joining, GME, BME)
- Tree rearrangement with nearest neighbor interchange (`nni`)
- Tree manipulation (pruning, rerooting, traversal)
- Distance calculations (patristic via `cophenet`, Robinson-Foulds via `compare_rfd`)
- ASCII visualization
- Newick format I/O

**Common patterns:**
```python
from skbio import TreeNode
from skbio.tree import nj, upgma, gme, bme, rf_dists

# Read tree from file
tree = TreeNode.read('tree.nwk')

# Construct tree from distance matrix
tree = nj(distance_matrix)

# Tree operations
subtree = tree.shear(['taxon1', 'taxon2', 'taxon3'])
tips = [node for node in tree.tips()]
lca = tree.lca(['taxon1', 'taxon2'])

# Calculate distances
patristic_dist = tree.find('taxon1').distance(tree.find('taxon2'))
cophenetic_dm = tree.cophenet()           # patristic distance matrix among tips

# Compare two trees (Robinson-Foulds)
rf_distance = tree.compare_rfd(other_tree)
# Pairwise RF distances among many trees -> DistanceMatrix
rf_dm = rf_dists([tree, other_tree, third_tree])
```

**Important notes:**
- Use `nj()` for neighbor joining (classic phylogenetic method)
- Use `upgma()` for UPGMA/WPGMA (assumes molecular clock)
- GME and BME are highly scalable for large trees; refine topology with `nni()`
- `cophenet()` (formerly `tip_tip_distances`) returns the patristic distance matrix; `compare_rfd()` is the Robinson-Foulds method (`compare_wrfd`/`compare_cophenet` for weighted/cophenetic variants)
- `lca()` is the lowest common ancestor; `lowest_common_ancestor` remains as an alias
- Trees can be rooted or unrooted; some metrics require specific rooting

### 4. Diversity Analysis

Calculate alpha and beta diversity metrics for microbial ecology and community analysis.

**Key capabilities:**
- Alpha diversity: richness (`sobs`, `observed_features`, `chao1`, `ace`), Shannon, Simpson, Hill numbers (`hill`), Faith's PD (`faith_pd`), generalized PD (`phydiv`), Pielou's evenness
- Beta diversity: Bray-Curtis, Jaccard, weighted/unweighted UniFrac, Euclidean distances
- Phylogenetic diversity metrics (require tree input)
- Rarefaction and subsampling
- Integration with ordination and statistical tests

**Common patterns:**
```python
from skbio.diversity import alpha_diversity, beta_diversity

# Alpha diversity (phylogenetic metrics take taxa= for tip-name mapping)
alpha = alpha_diversity('shannon', counts_matrix, ids=sample_ids)
faith_pd = alpha_diversity('faith_pd', counts_matrix, ids=sample_ids,
                           tree=tree, taxa=feature_ids)

# Beta diversity
bc_dm = beta_diversity('braycurtis', counts_matrix, ids=sample_ids)
unifrac_dm = beta_diversity('unweighted_unifrac', counts_matrix,
                            ids=sample_ids, tree=tree, taxa=feature_ids)

# Get available metrics
from skbio.diversity import get_alpha_diversity_metrics
print(get_alpha_diversity_metrics())
```

**Important notes:**
- Counts must be integers representing abundances, not relative frequencies
- The phylogenetic-metric argument is `taxa=` (renamed from `otu_ids` in 0.6.0; the old name is a deprecated alias); `observed_otus` is now `observed_features` (or `sobs`)
- `counts_matrix` may be any table-like input (NumPy array, pandas/polars DataFrame, BIOM `Table`, or AnnData) via the dispatch system
- Phylogenetic metrics (Faith's PD, UniFrac) require tree and taxa-to-tip mapping
- Use `partial_beta_diversity()` for specific sample pairs, or `block_beta_diversity()` for large block-decomposed calculations
- Alpha diversity returns a `pandas.Series`, beta diversity returns a `DistanceMatrix`

### 5. Ordination Methods

Reduce high-dimensional biological data to visualizable lower-dimensional spaces.

**Key capabilities:**
- PCoA (Principal Coordinate Analysis) from distance matrices
- CA (Correspondence Analysis) for contingency tables
- CCA (Canonical Correspondence Analysis) with environmental constraints
- RDA (Redundancy Analysis) for linear relationships
- Biplot projection for feature interpretation

**Common patterns:**
```python
from skbio.stats.ordination import pcoa, cca
import skbio

# PCoA from distance matrix (limit dimensions for large matrices)
pcoa_results = pcoa(distance_matrix, dimensions=3)
pc1 = pcoa_results.samples['PC1']
pc2 = pcoa_results.samples['PC2']

# Built-in scatter plot colored by a metadata column
fig = pcoa_results.plot(sample_metadata, column='bodysite')

# CCA with environmental variables
cca_results = cca(species_matrix, environmental_matrix)

# Save/load ordination results
pcoa_results.write('ordination.txt')
results = skbio.OrdinationResults.read('ordination.txt')
```

**Important notes:**
- PCoA works with any distance/dissimilarity matrix; pass `dimensions` as an int (count) or a float in (0, 1] (fraction of cumulative variance to retain)
- `OrdinationResults` exposes pandas-based attributes: `samples`, `features`, `eigvals`, `proportion_explained`, `biplot_scores`, `sample_constraints`
- CCA reveals environmental drivers of community composition
- `OrdinationResults.plot()` produces a matplotlib figure; results also integrate with seaborn/plotly

### 6. Statistical Testing

Perform hypothesis tests specific to ecological and biological data.

**Key capabilities:**
- PERMANOVA: test group differences using distance matrices
- ANOSIM: alternative test for group differences
- PERMDISP: test homogeneity of group dispersions
- Mantel test: correlation between distance matrices
- Bioenv: find environmental variables correlated with distances
- Differential abundance: `ancom`, `dirmult_ttest`, and `dirmult_lme` (longitudinal mixed-effects) in `skbio.stats.composition`

**Common patterns:**
```python
from skbio.stats.distance import permanova, anosim, mantel

# Test if groups differ significantly
permanova_results = permanova(distance_matrix, grouping, permutations=999)
print(f"p-value: {permanova_results['p-value']}")

# ANOSIM test
anosim_results = anosim(distance_matrix, grouping, permutations=999)

# Mantel test between two distance matrices
mantel_results = mantel(dm1, dm2, method='pearson', permutations=999)
print(f"Correlation: {mantel_results[0]}, p-value: {mantel_results[1]}")

# Differential abundance on a feature table (raw counts recommended)
from skbio.stats.composition import dirmult_ttest
da = dirmult_ttest(counts_table, grouping, treatment='caseA', reference='control')
```

**Important notes:**
- Permutation tests provide non-parametric significance testing
- Use 999+ permutations for robust p-values
- PERMANOVA sensitive to dispersion differences; pair with PERMDISP
- Mantel tests assess matrix correlation (e.g., geographic vs genetic distance)
- Supply differential-abundance tests with raw counts, not pre-normalized proportions, to preserve magnitude information

### 7. File I/O and Format Conversion

Read and write 19+ biological file formats with automatic format detection.

**Supported formats:**
- Sequences: FASTA, FASTQ, GenBank, EMBL, QSeq
- Alignments: Clustal, PHYLIP, Stockholm
- Trees: Newick
- Tables: BIOM (HDF5 and JSON)
- Distances: delimited square matrices
- Analysis: BLAST+6/7, GFF3, Ordination results
- Metadata: TSV/CSV with validation

**Common patterns:**
```python
import skbio

# Read with automatic format detection
seq = skbio.DNA.read('file.fasta', format='fasta')
tree = skbio.TreeNode.read('tree.nwk')

# Write to file
seq.write('output.fasta', format='fasta')

# Generator for large files (memory efficient)
for seq in skbio.io.read('large.fasta', format='fasta', constructor=skbio.DNA):
    process(seq)

# Convert formats
seqs = list(skbio.io.read('input.fastq', format='fastq', constructor=skbio.DNA))
skbio.io.write(seqs, format='fasta', into='output.fasta')
```

**Important notes:**
- Use generators for large files to avoid memory issues
- Format can be auto-detected when `into` parameter specified
- Some objects can be written to multiple formats
- Support for stdin/stdout piping with `verify=False`

### 8. Distance Matrices

Create and manipulate distance/dissimilarity matrices with statistical methods.

**Key capabilities:**
- Store symmetric (`DistanceMatrix`, hollow diagonal) or general pairwise (`PairwiseMatrix`) data
- ID-based indexing and slicing
- Integration with diversity, ordination, and statistical tests
- Read/write delimited text format

**Common patterns:**
```python
from skbio import DistanceMatrix
import numpy as np

# Create from array
data = np.array([[0, 1, 2], [1, 0, 3], [2, 3, 0]])
dm = DistanceMatrix(data, ids=['A', 'B', 'C'])

# Access distances
dist_ab = dm['A', 'B']
row_a = dm['A']

# Read from file
dm = DistanceMatrix.read('distances.txt')

# Use in downstream analyses
pcoa_results = pcoa(dm)
permanova_results = permanova(dm, grouping)
```

**Important notes:**
- `DistanceMatrix` enforces symmetry and a zero (hollow) diagonal; it is a subclass of `SymmetricMatrix`
- `PairwiseMatrix` (renamed from `DissimilarityMatrix`, which is kept as a deprecated alias) allows general/asymmetric values
- IDs enable integration with metadata and biological knowledge
- Compatible with pandas, numpy, and scikit-learn

### 9. Biological Tables

Work with feature tables (OTU/ASV tables) common in microbiome research.

**Key capabilities:**
- BIOM format I/O (HDF5 and JSON) via the native `Table` class
- Table dispatch system (0.7.0+): functions accept any `table_like` input — BIOM `Table`, pandas/polars DataFrame, NumPy array, or AnnData — without explicit conversion
- Data augmentation techniques (`phylomix`, `mixup`, `aitchison_mixup`, `compos_cutmix`)
- Sample/feature filtering and normalization
- Metadata integration

**Common patterns:**
```python
from skbio import Table
from skbio.diversity import beta_diversity

# Read BIOM table
table = Table.read('table.biom')

# Access data
sample_ids = table.ids(axis='sample')
feature_ids = table.ids(axis='observation')
counts = table.matrix_data

# Filter
filtered = table.filter(sample_ids_to_keep, axis='sample')

# Pass table-like objects directly to scikit-bio drivers (dispatch system)
import pandas as pd
df = pd.read_table('data.tsv', index_col=0)   # samples x features
bdiv = beta_diversity('braycurtis', df)         # no manual conversion needed
```

**Important notes:**
- BIOM tables are standard in QIIME 2 workflows
- Rows typically represent samples, columns represent features (OTUs/ASVs)
- Supports sparse and dense representations
- With the dispatch system, functions return the same format as their input, or a user-specified output format

### 10. Protein Embeddings

Work with protein language model embeddings for downstream analysis.

**Key capabilities:**
- Store embeddings from protein language models (ESM, ProtTrans, etc.)
- Convert embeddings to distance matrices
- Generate ordination objects for visualization
- Export to numpy/pandas for ML workflows

**Common patterns:**
```python
from skbio.embedding import ProteinEmbedding, ProteinVector

# Create embedding from array
embedding = ProteinEmbedding(embedding_array, sequence_ids)

# Convert to distance matrix for analysis
dm = embedding.to_distances(metric='euclidean')

# PCoA visualization of embedding space
pcoa_results = embedding.to_ordination(metric='euclidean', method='pcoa')

# Export for machine learning
array = embedding.to_array()
df = embedding.to_dataframe()
```

**Important notes:**
- Embeddings bridge protein language models with traditional bioinformatics
- Compatible with scikit-bio's distance/ordination/statistics ecosystem
- SequenceEmbedding and ProteinEmbedding provide specialized functionality
- Useful for sequence clustering, classification, and visualization

## Best Practices

### Installation
```bash
uv pip install scikit-bio
```
Requires Python 3.10+ and NumPy 2.0+. Pre-compiled wheels are published for each release since 0.7.0, so most platforms install without a compiler. Conda users can instead run `conda install -c conda-forge scikit-bio`.

### Performance Considerations
- Use generators for large sequence files to minimize memory usage
- For massive phylogenetic trees, prefer GME or BME over NJ
- Beta diversity calculations can be parallelized with `partial_beta_diversity()`
- BIOM format (HDF5) more efficient than JSON for large tables

### Integration with Ecosystem
- Sequences interoperate with Biopython via standard formats
- Tables integrate with pandas, polars, and AnnData
- Distance matrices compatible with scikit-learn
- Ordination results visualizable with matplotlib/seaborn/plotly
- Works seamlessly with QIIME 2 artifacts (BIOM, trees, distance matrices)

### Common Workflows
1. **Microbiome diversity analysis**: Read BIOM table → Calculate alpha/beta diversity → Ordination (PCoA) → Statistical testing (PERMANOVA)
2. **Phylogenetic analysis**: Read sequences → Align → Build distance matrix → Construct tree → Calculate phylogenetic distances
3. **Sequence processing**: Read FASTQ → Quality filter → Trim/clean → Find motifs → Translate → Write FASTA
4. **Comparative genomics**: Read sequences → Pairwise alignment → Calculate distances → Build tree → Analyze clades

## Reference Documentation

For detailed API information, parameter specifications, and advanced usage examples, refer to `references/api_reference.md` which contains comprehensive documentation on:
- Complete method signatures and parameters for all capabilities
- Extended code examples for complex workflows
- Troubleshooting common issues
- Performance optimization tips
- Integration patterns with other libraries

## Additional Resources

- Official documentation: https://scikit.bio/docs/latest/
- GitHub repository: https://github.com/scikit-bio/scikit-bio
- Changelog: https://github.com/scikit-bio/scikit-bio/blob/main/CHANGELOG.md
- Reference paper: "scikit-bio: a fundamental Python library for biological omic data," *Nature Methods* (2025), https://www.nature.com/articles/s41592-025-02981-z
- Forum support: https://forum.qiime2.org (scikit-bio is part of QIIME 2 ecosystem)

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/scikit-bio/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_reference.md`

# scikit-bio API Reference

This document provides detailed API information, advanced examples, and troubleshooting guidance for working with scikit-bio.

## Table of Contents
1. [Sequence Classes](#sequence-classes)
2. [Alignment Methods](#alignment-methods)
3. [Phylogenetic Trees](#phylogenetic-trees)
4. [Diversity Metrics](#diversity-metrics)
5. [Ordination](#ordination)
6. [Statistical Tests](#statistical-tests)
7. [Distance Matrices](#distance-matrices)
8. [File I/O](#file-io)
9. [Troubleshooting](#troubleshooting)

## Sequence Classes

### DNA, RNA, and Protein Classes

```python
from skbio import DNA, RNA, Protein, Sequence

# Creating sequences
dna = DNA('ATCGATCG', metadata={'id': 'seq1', 'description': 'Example'})
rna = RNA('AUCGAUCG')
protein = Protein('ACDEFGHIKLMNPQRSTVWY')

# Sequence operations
dna_rc = dna.reverse_complement()  # Reverse complement
rna = dna.transcribe()  # DNA -> RNA
protein = rna.translate()  # RNA -> Protein

# Using genetic code tables
protein = rna.translate(genetic_code=11)  # Bacterial code
```

### Sequence Searching and Pattern Matching

```python
# Find motifs using regex
dna = DNA('ATGCGATCGATGCATCG')
motif_locs = dna.find_with_regex('ATG.{3}')  # Start codons

# Find all positions
import re
for match in re.finditer('ATG', str(dna)):
    print(f"ATG found at position {match.start()}")

# k-mer counting
from skbio.sequence import _motifs
kmers = dna.kmer_frequencies(k=3)
```

### Handling Sequence Metadata

```python
# Sequence-level metadata
dna = DNA('ATCG', metadata={'id': 'seq1', 'source': 'E. coli'})
print(dna.metadata['id'])

# Positional metadata (per-base quality scores from FASTQ)
from skbio import DNA
seqs = DNA.read('reads.fastq', format='fastq', phred_offset=33)
quality_scores = seqs.positional_metadata['quality']

# Interval metadata (features/annotations)
dna.interval_metadata.add([(5, 15)], metadata={'type': 'gene', 'name': 'geneA'})
```

### Distance Calculations

```python
from skbio import DNA

seq1 = DNA('ATCGATCG')
seq2 = DNA('ATCG--CG')

# Hamming distance (default)
dist = seq1.distance(seq2)

# Custom distance function
from skbio.sequence.distance import kmer_distance
dist = seq1.distance(seq2, metric=kmer_distance)
```

## Alignment Methods

### Pairwise Alignment

scikit-bio 0.7.0 introduced `pair_align`, a single fast engine for global, local, and semi-global alignment. The convenience wrappers `pair_align_nucl` and `pair_align_prot` ship with BLASTN/BLASTP-like scoring. The old SSW wrapper (`local_pairwise_align_ssw`, `StripedSmithWaterman`) was removed, and the pure-Python `global_pairwise_align`/`local_pairwise_align_*` functions are deprecated.

```python
from skbio import DNA, Protein
from skbio.alignment import pair_align_nucl, pair_align_prot, pair_align, align_score

# Nucleotide alignment with BLASTN-like defaults
seq1 = DNA('ATCGATCGATCG')
seq2 = DNA('ATCGGGGATCG')
aln = pair_align_nucl(seq1, seq2)

# Inspect the result (PairAlignResult: score + paths [+ matrices])
print(f"Score: {aln.score}")
path = aln.paths[0]                       # PairAlignPath; repr shows the CIGAR
aligned_seqs = path.to_aligned((seq1, seq2))   # list of gapped strings

# Global alignment with custom affine scoring via pair_align
aln = pair_align(
    seq1, seq2,
    mode='global',          # 'global' (default), 'local', or semi-global via free_ends
    sub_score=(2, -3),      # (match, mismatch)
    gap_cost=(5, 2),        # (open, extend) -> affine; a single number -> linear
)

# Use a named substitution matrix instead of match/mismatch scores
aln = pair_align(seq1, seq2, mode='global', sub_score='NUC.4.4', gap_cost=3)

# Protein alignment with BLASTP-like defaults (BLOSUM62)
protein_query = Protein('ACDEFGHIKLMNPQRSTVWY')
protein_target = Protein('ACDEFMNPQRSTVWY')
aln = pair_align_prot(protein_query, protein_target)

# Re-score an existing alignment with the same parameters
score = align_score((aln.paths[0], (protein_query, protein_target)),
                    sub_score='BLOSUM62', gap_cost=(11, 1))

# PairAlignResult also unpacks as a tuple
score, (path,), _ = pair_align_nucl(seq1, seq2)
```

### Multiple Sequence Alignment

```python
from skbio.alignment import TabularMSA, pair_align_nucl
from skbio import DNA

# Read MSA from file
msa = TabularMSA.read('alignment.fasta', constructor=DNA)

# Build a TabularMSA from a pairwise alignment path + original sequences
score, (path,), _ = pair_align_nucl(DNA('ATCGATCG'), DNA('ATCGGGGATCG'))
msa = TabularMSA.from_path_seqs(path, (DNA('ATCGATCG'), DNA('ATCGGGGATCG')))

# Create MSA manually
seqs = [
    DNA('ATCG--'),
    DNA('ATGG--'),
    DNA('ATCGAT')
]
msa = TabularMSA(seqs)

# MSA operations
consensus = msa.consensus()
majority_consensus = msa.majority_consensus()

# Calculate conservation
conservation = msa.conservation()

# Access sequences
first_seq = msa[0]
column = msa[:, 2]  # Third column

# Filter gaps
degapped_msa = msa.omit_gap_positions(maximum_gap_frequency=0.5)

# Calculate position-specific scores
position_entropies = msa.position_entropies()
```

### CIGAR Strings and Alignment Paths

```python
from skbio.alignment import PairAlignPath, AlignPath, pair_align_nucl
from skbio import DNA

# Parse a CIGAR string into a pairwise alignment path
path = PairAlignPath.from_cigar('10M2I5M3D10M')
print(repr(path))   # <PairAlignPath, ..., CIGAR: '10M2I5M3D10M'>

# A path produced by pair_align already carries its CIGAR
aln = pair_align_nucl(DNA('ATCGATCG'), DNA('ATCGGGGATCG'))
cigar_string = aln.paths[0].cigar

# AlignPath generalizes to >2 sequences (e.g., from aligned strings)
path3 = AlignPath.from_aligned(['CGTCGTGC', 'CA--GT-C', 'CGTCGT-T'])

# Parse CIGAR output from external tools such as parasail
# path = PairAlignPath.from_cigar(res.cigar.decode)
```

## Phylogenetic Trees

### Tree Construction

```python
from skbio import TreeNode, DistanceMatrix
from skbio.tree import nj, upgma

# Distance matrix
dm = DistanceMatrix([[0, 5, 9, 9],
                     [5, 0, 10, 10],
                     [9, 10, 0, 8],
                     [9, 10, 8, 0]],
                    ids=['A', 'B', 'C', 'D'])

# Neighbor joining
nj_tree = nj(dm)

# UPGMA (assumes molecular clock)
upgma_tree = upgma(dm)

# Balanced Minimum Evolution (scalable for large trees)
from skbio.tree import bme
bme_tree = bme(dm)
```

### Tree Manipulation

```python
from skbio import TreeNode

# Read tree
tree = TreeNode.read('tree.nwk', format='newick')

# Traversal
for node in tree.traverse():
    print(node.name)

# Preorder, postorder, levelorder
for node in tree.preorder():
    print(node.name)

# Get tips only
tips = list(tree.tips())

# Find specific node
node = tree.find('taxon_name')

# Root tree at midpoint
rooted_tree = tree.root_at_midpoint()

# Prune tree to specific taxa
pruned = tree.shear(['taxon1', 'taxon2', 'taxon3'])

# Get subtree
lca = tree.lowest_common_ancestor(['taxon1', 'taxon2'])
subtree = lca.copy()

# Add/remove nodes
parent = tree.find('parent_name')
child = TreeNode(name='new_child', length=0.5)
parent.append(child)

# Remove node
node_to_remove = tree.find('taxon_to_remove')
node_to_remove.parent.remove(node_to_remove)
```

### Tree Distances and Comparisons

```python
# Patristic distance (branch-length distance) between two nodes
node1 = tree.find('taxon1')
node2 = tree.find('taxon2')
patristic = node1.distance(node2)

# Cophenetic (patristic) distance matrix among all tips
# cophenet() replaces the former tip_tip_distances()
cophenetic_dm = tree.cophenet()

# Robinson-Foulds distance between two trees (compare_rfd, added in 0.6.3)
rf_dist = tree.compare_rfd(other_tree)              # count (float)
rf_prop = tree.compare_rfd(other_tree, proportion=True)  # normalized to [0, 1]

# Weighted Robinson-Foulds and cophenetic-correlation comparisons
wrf = tree.compare_wrfd(other_tree)
coph = tree.compare_cophenet(other_tree)

# Pairwise RF distances among many trees -> DistanceMatrix
from skbio.tree import rf_dists
rf_dm = rf_dists([tree, other_tree, third_tree])
```

### Tree Visualization

```python
# ASCII art visualization
print(tree.ascii_art())

# For advanced visualization, export to external tools
tree.write('tree.nwk', format='newick')

# Then use ete3, toytree, or ggtree for publication-quality figures
```

## Diversity Metrics

### Alpha Diversity

```python
from skbio.diversity import alpha_diversity, get_alpha_diversity_metrics
import numpy as np

# Sample count data (samples x features)
counts = np.array([
    [10, 5, 0, 3],
    [2, 0, 8, 4],
    [5, 5, 5, 5]
])
sample_ids = ['Sample1', 'Sample2', 'Sample3']

# List available metrics
print(get_alpha_diversity_metrics())

# Calculate various alpha diversity metrics
shannon = alpha_diversity('shannon', counts, ids=sample_ids)
simpson = alpha_diversity('simpson', counts, ids=sample_ids)
observed = alpha_diversity('observed_features', counts, ids=sample_ids)  # was 'observed_otus'
chao1 = alpha_diversity('chao1', counts, ids=sample_ids)
hill_q2 = alpha_diversity('hill', counts, ids=sample_ids)  # effective number of species

# Phylogenetic alpha diversity (requires tree). Note: taxa= replaces otu_ids=
from skbio import TreeNode

tree = TreeNode.read('tree.nwk')
feature_ids = ['OTU1', 'OTU2', 'OTU3', 'OTU4']

faith_pd = alpha_diversity('faith_pd', counts, ids=sample_ids,
                           tree=tree, taxa=feature_ids)
```

### Beta Diversity

```python
from skbio.diversity import beta_diversity, partial_beta_diversity

# Beta diversity (all pairwise comparisons)
bc_dm = beta_diversity('braycurtis', counts, ids=sample_ids)

# Jaccard (presence/absence)
jaccard_dm = beta_diversity('jaccard', counts, ids=sample_ids)

# Phylogenetic beta diversity (taxa= replaces the deprecated otu_ids=)
unifrac_dm = beta_diversity('unweighted_unifrac', counts,
                            ids=sample_ids,
                            tree=tree,
                            taxa=feature_ids)

weighted_unifrac_dm = beta_diversity('weighted_unifrac', counts,
                                     ids=sample_ids,
                                     tree=tree,
                                     taxa=feature_ids)

# Compute only specific pairs (more efficient)
pairs = [('Sample1', 'Sample2'), ('Sample1', 'Sample3')]
partial_dm = partial_beta_diversity('braycurtis', counts,
                                   ids=sample_ids,
                                   id_pairs=pairs)
```

### Rarefaction and Subsampling

```python
from skbio.diversity import subsample_counts

# Rarefy to minimum depth
min_depth = counts.min(axis=1).max()
rarefied = [subsample_counts(row, n=min_depth) for row in counts]

# Multiple rarefactions for confidence intervals
import numpy as np
rarefactions = []
for i in range(100):
    rarefied_counts = np.array([subsample_counts(row, n=1000) for row in counts])
    shannon_rare = alpha_diversity('shannon', rarefied_counts)
    rarefactions.append(shannon_rare)

# Calculate mean and std
mean_shannon = np.mean(rarefactions, axis=0)
std_shannon = np.std(rarefactions, axis=0)
```

## Ordination

### Principal Coordinate Analysis (PCoA)

```python
from skbio.stats.ordination import pcoa
from skbio import DistanceMatrix
import numpy as np

# PCoA from distance matrix
dm = DistanceMatrix(...)
pcoa_results = pcoa(dm)

# Access coordinates
pc1 = pcoa_results.samples['PC1']
pc2 = pcoa_results.samples['PC2']

# Proportion explained
prop_explained = pcoa_results.proportion_explained

# Eigenvalues
eigenvalues = pcoa_results.eigvals

# Save results
pcoa_results.write('pcoa_results.txt')

# Plot with matplotlib
import matplotlib.pyplot as plt
plt.scatter(pc1, pc2)
plt.xlabel(f'PC1 ({prop_explained[0]*100:.1f}%)')
plt.ylabel(f'PC2 ({prop_explained[1]*100:.1f}%)')
```

### Canonical Correspondence Analysis (CCA)

```python
from skbio.stats.ordination import cca
import pandas as pd
import numpy as np

# Species abundance matrix (samples x species)
species = np.array([
    [10, 5, 3],
    [2, 8, 4],
    [5, 5, 5]
])

# Environmental variables (samples x variables)
env = pd.DataFrame({
    'pH': [6.5, 7.0, 6.8],
    'temperature': [20, 25, 22],
    'depth': [10, 15, 12]
})

# CCA
cca_results = cca(species, env,
                 sample_ids=['Site1', 'Site2', 'Site3'],
                 species_ids=['SpeciesA', 'SpeciesB', 'SpeciesC'])

# Access constrained axes
cca1 = cca_results.samples['CCA1']
cca2 = cca_results.samples['CCA2']

# Biplot scores for environmental variables
env_scores = cca_results.biplot_scores
```

### Redundancy Analysis (RDA)

```python
from skbio.stats.ordination import rda

# Similar to CCA but for linear relationships
rda_results = rda(species, env,
                 sample_ids=['Site1', 'Site2', 'Site3'],
                 species_ids=['SpeciesA', 'SpeciesB', 'SpeciesC'])
```

## Statistical Tests

### PERMANOVA

```python
from skbio.stats.distance import permanova
from skbio import DistanceMatrix
import numpy as np

# Distance matrix
dm = DistanceMatrix(...)

# Grouping variable
grouping = ['Group1', 'Group1', 'Group2', 'Group2', 'Group3', 'Group3']

# Run PERMANOVA
results = permanova(dm, grouping, permutations=999)

print(f"Test statistic: {results['test statistic']}")
print(f"p-value: {results['p-value']}")
print(f"Sample size: {results['sample size']}")
print(f"Number of groups: {results['number of groups']}")
```

### ANOSIM

```python
from skbio.stats.distance import anosim

# ANOSIM test
results = anosim(dm, grouping, permutations=999)

print(f"R statistic: {results['test statistic']}")
print(f"p-value: {results['p-value']}")
```

### PERMDISP

```python
from skbio.stats.distance import permdisp

# Test homogeneity of dispersions
results = permdisp(dm, grouping, permutations=999)

print(f"F statistic: {results['test statistic']}")
print(f"p-value: {results['p-value']}")
```

### Mantel Test

```python
from skbio.stats.distance import mantel
from skbio import DistanceMatrix

# Two distance matrices to compare
dm1 = DistanceMatrix(...)  # e.g., genetic distance
dm2 = DistanceMatrix(...)  # e.g., geographic distance

# Mantel test
r, p_value, n = mantel(dm1, dm2, method='pearson', permutations=999)

print(f"Correlation: {r}")
print(f"p-value: {p_value}")
print(f"Sample size: {n}")

# Spearman correlation
r_spearman, p, n = mantel(dm1, dm2, method='spearman', permutations=999)
```

### Partial Mantel Test

```python
from skbio.stats.distance import mantel

# Control for a third matrix
dm3 = DistanceMatrix(...)  # controlling variable

r_partial, p_value, n = mantel(dm1, dm2, method='pearson',
                               permutations=999, alternative='two-sided')
```

## Distance Matrices

### Creating and Manipulating Distance Matrices

```python
from skbio import DistanceMatrix
from skbio.stats.distance import PairwiseMatrix
import numpy as np

# Create from array
data = np.array([[0, 1, 2],
                 [1, 0, 3],
                 [2, 3, 0]])
dm = DistanceMatrix(data, ids=['A', 'B', 'C'])

# Access elements
dist_ab = dm['A', 'B']
row_a = dm['A']

# Slicing
subset_dm = dm.filter(['A', 'C'])

# General/asymmetric matrix: PairwiseMatrix (renamed from DissimilarityMatrix,
# which is kept as a deprecated alias)
asym_data = np.array([[0, 1, 2],
                      [3, 0, 4],
                      [5, 6, 0]])
pwm = PairwiseMatrix(asym_data, ids=['X', 'Y', 'Z'])

# Read/write
dm.write('distances.txt')
dm2 = DistanceMatrix.read('distances.txt')

# Convert to condensed form (for scipy)
condensed = dm.condensed_form()

# Convert to dataframe
df = dm.to_data_frame()
```

## File I/O

### Reading Sequences

```python
import skbio

# Read single sequence
dna = skbio.DNA.read('sequence.fasta', format='fasta')

# Read multiple sequences (generator)
for seq in skbio.io.read('sequences.fasta', format='fasta', constructor=skbio.DNA):
    print(seq.metadata['id'], len(seq))

# Read into list
sequences = list(skbio.io.read('sequences.fasta', format='fasta',
                               constructor=skbio.DNA))

# Read FASTQ with quality scores
for seq in skbio.io.read('reads.fastq', format='fastq', constructor=skbio.DNA):
    quality = seq.positional_metadata['quality']
    print(f"Mean quality: {quality.mean()}")
```

### Writing Sequences

```python
# Write single sequence
dna.write('output.fasta', format='fasta')

# Write multiple sequences
sequences = [dna1, dna2, dna3]
skbio.io.write(sequences, format='fasta', into='output.fasta')

# Write with custom line wrapping
dna.write('output.fasta', format='fasta', max_width=60)
```

### BIOM Tables

```python
from skbio import Table

# Read BIOM table
table = Table.read('table.biom', format='hdf5')

# Access data
sample_ids = table.ids(axis='sample')
feature_ids = table.ids(axis='observation')
matrix = table.matrix_data.toarray()  # if sparse

# Filter samples
abundant_samples = table.filter(lambda row, id_, md: row.sum() > 1000, axis='sample')

# Filter features (OTUs/ASVs)
prevalent_features = table.filter(lambda col, id_, md: (col > 0).sum() >= 3,
                                 axis='observation')

# Normalize
relative_abundance = table.norm(axis='sample', inplace=False)

# Write
table.write('filtered_table.biom', format='hdf5')
```

### Format Conversion

```python
# FASTQ to FASTA
seqs = skbio.io.read('input.fastq', format='fastq', constructor=skbio.DNA)
skbio.io.write(seqs, format='fasta', into='output.fasta')

# GenBank to FASTA
seqs = skbio.io.read('genes.gb', format='genbank', constructor=skbio.DNA)
skbio.io.write(seqs, format='fasta', into='genes.fasta')
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: "ValueError: Ids must be unique"
```python
# Problem: Duplicate sequence IDs
# Solution: Make IDs unique or filter duplicates
seen = set()
unique_seqs = []
for seq in sequences:
    if seq.metadata['id'] not in seen:
        unique_seqs.append(seq)
        seen.add(seq.metadata['id'])
```

#### Issue: "ValueError: Counts must be integers"
```python
# Problem: Relative abundances instead of counts
# Solution: Convert to integer counts or use appropriate metrics
counts_int = (abundance_table * 1000).astype(int)
```

#### Issue: Memory error with large files
```python
# Problem: Loading entire file into memory
# Solution: Use generators
for seq in skbio.io.read('huge.fasta', format='fasta', constructor=skbio.DNA):
    # Process one at a time
    process(seq)
```

#### Issue: Tree tips don't match OTU IDs
```python
# Problem: Mismatch between tree tip names and feature IDs
# Solution: Verify and align IDs
tree_tips = {tip.name for tip in tree.tips()}
feature_ids = set(feature_ids)
missing_in_tree = feature_ids - tree_tips
missing_in_table = tree_tips - feature_ids

# Prune tree to match table
tree_pruned = tree.shear(feature_ids)
```

#### Issue: Alignment fails with sequences of different lengths
```python
# Problem: Trying to align pre-aligned sequences
# Solution: Degap sequences first or ensure sequences are unaligned
seq1_degapped = seq1.degap()
seq2_degapped = seq2.degap()
alignment = pair_align_nucl(seq1_degapped, seq2_degapped)
```

### Performance Tips

1. **Use appropriate data structures**: BIOM HDF5 for large tables, generators for large sequence files
2. **Parallel processing**: Use `partial_beta_diversity()` for subset calculations that can be parallelized
3. **Subsample large datasets**: For exploratory analysis, work with subsampled data first
4. **Cache results**: Save distance matrices and ordination results to avoid recomputation

### Integration Examples

#### With pandas
```python
import pandas as pd
from skbio import DistanceMatrix

# Distance matrix to DataFrame
dm = DistanceMatrix(...)
df = dm.to_data_frame()

# Alpha diversity to DataFrame
alpha = alpha_diversity('shannon', counts, ids=sample_ids)
alpha_df = pd.DataFrame({'shannon': alpha})
```

#### With matplotlib/seaborn
```python
import matplotlib.pyplot as plt
import seaborn as sns

# PCoA plot
fig, ax = plt.subplots()
scatter = ax.scatter(pc1, pc2, c=grouping, cmap='viridis')
ax.set_xlabel(f'PC1 ({prop_explained[0]*100:.1f}%)')
ax.set_ylabel(f'PC2 ({prop_explained[1]*100:.1f}%)')
plt.colorbar(scatter)

# Heatmap of distance matrix
sns.heatmap(dm.to_data_frame(), cmap='viridis')
```

#### With QIIME 2
```python
# scikit-bio objects are compatible with QIIME 2
# Export from QIIME 2
# qiime tools export --input-path table.qza --output-path exported/

# Read in scikit-bio
table = Table.read('exported/feature-table.biom')

# Process with scikit-bio
# ...

# Import back to QIIME 2 if needed
table.write('processed-table.biom')
# qiime tools import --input-path processed-table.biom --output-path processed.qza
```
