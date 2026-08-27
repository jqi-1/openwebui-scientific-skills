---
name: phylogenetics
description: Build and analyze phylogenetic trees using MAFFT (multiple alignment), IQ-TREE 2 (maximum likelihood), and FastTree (fast NJ/ML). Visualize with ETE3 or FigTree. For evolutionary analysis, microbial genomics, viral phylodynamics, protein family analysis, and molecular clock studies.
---

# Phylogenetics

## Overview

Phylogenetic analysis reconstructs the evolutionary history of biological sequences (genes, proteins, genomes) by inferring the branching pattern of descent. This skill covers the standard pipeline:

1. **MAFFT** — Multiple sequence alignment
2. **IQ-TREE 2** — Maximum likelihood tree inference with model selection
3. **FastTree** — Fast approximate maximum likelihood (for large datasets)
4. **ETE3** — Python library for tree manipulation and visualization

**Installation:**
```bash
# Conda (recommended for CLI tools)
conda install -c bioconda mafft iqtree fasttree
uv pip install ete3

# ete3's TreeStyle/NodeStyle rendering lives in its Qt backend, so image output
# needs PyQt5 as well; tree parsing and statistics work without it.
uv pip install PyQt5
```

## When to Use This Skill

Use phylogenetics when:

- **Evolutionary relationships**: Which organism/gene is most closely related to my sequence?
- **Viral phylodynamics**: Trace outbreak spread and estimate transmission dates
- **Protein family analysis**: Infer evolutionary relationships within a gene family
- **Horizontal gene transfer detection**: Identify genes with discordant species/gene trees
- **Ancestral sequence reconstruction**: Infer ancestral protein sequences
- **Molecular clock analysis**: Estimate divergence dates using temporal sampling
- **GWAS companion**: Place variants in evolutionary context (e.g., SARS-CoV-2 variants)
- **Microbiology**: Species phylogeny from 16S rRNA or core genome phylogeny

## Standard Workflow

### 1. Multiple Sequence Alignment with MAFFT

```python
import subprocess
import os

def run_mafft(input_fasta: str, output_fasta: str, method: str = "auto",
               n_threads: int = 4) -> str:
    """
    Align sequences with MAFFT.

    Args:
        input_fasta: Path to unaligned FASTA file
        output_fasta: Path for aligned output
        method: 'auto' (auto-select), 'einsi' (accurate), 'linsi' (accurate, slow),
                'fftnsi' (medium), 'fftns' (fast), 'retree2' (fast)
        n_threads: Number of CPU threads

    Returns:
        Path to aligned FASTA file
    """
    methods = {
        "auto": ["mafft", "--auto"],
        "einsi": ["mafft", "--genafpair", "--maxiterate", "1000"],
        "linsi": ["mafft", "--localpair", "--maxiterate", "1000"],
        "fftnsi": ["mafft", "--fftnsi"],
        "fftns": ["mafft", "--fftns"],
        "retree2": ["mafft", "--retree", "2"],
    }

    cmd = methods.get(method, methods["auto"])
    cmd += ["--thread", str(n_threads), "--inputorder", input_fasta]

    with open(output_fasta, 'w') as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"MAFFT failed:\n{result.stderr}")

    # Count aligned sequences
    with open(output_fasta) as f:
        n_seqs = sum(1 for line in f if line.startswith('>'))
    print(f"MAFFT: aligned {n_seqs} sequences → {output_fasta}")

    return output_fasta

# MAFFT method selection guide:
# Few sequences (<200), accurate: linsi or einsi
# Many sequences (<1000), moderate: fftnsi
# Large datasets (>1000): fftns or auto
# Ultra-fast (>10000): mafft --retree 1
```

### 2. Trim Alignment (Optional but Recommended)

```python
def trim_alignment_trimal(aligned_fasta: str, output_fasta: str,
                            method: str = "automated1") -> str:
    """
    Trim poorly aligned columns with TrimAl.

    Methods:
    - 'automated1': Automatic heuristic (recommended)
    - 'gappyout': Remove gappy columns
    - 'strict': Strict gap threshold
    """
    cmd = ["trimal", f"-{method}", "-in", aligned_fasta, "-out", output_fasta, "-fasta"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"TrimAl warning: {result.stderr}")
        # Fall back to using the untrimmed alignment
        import shutil
        shutil.copy(aligned_fasta, output_fasta)
    return output_fasta
```

### 3. IQ-TREE 2 — Maximum Likelihood Tree

```python
def run_iqtree(aligned_fasta: str, output_prefix: str,
                model: str = "TEST", bootstrap: int = 1000,
                n_threads: int = 4, extra_args: list = None) -> dict:
    """
    Build a maximum likelihood tree with IQ-TREE 2.

    Args:
        aligned_fasta: Aligned FASTA file
        output_prefix: Prefix for output files
        model: 'TEST' for automatic model selection, or specify (e.g., 'GTR+G' for DNA,
               'LG+G4' for proteins, 'JTT+G' for proteins)
        bootstrap: Number of ultrafast bootstrap replicates (1000 recommended)
        n_threads: Number of threads ('AUTO' to auto-detect)
        extra_args: Additional IQ-TREE arguments

    Returns:
        Dict with paths to output files
    """
    cmd = [
        "iqtree2",
        "-s", aligned_fasta,
        "--prefix", output_prefix,
        "-m", model,
        "-B", str(bootstrap),   # Ultrafast bootstrap
        "-T", str(n_threads),
        "--redo"                # Overwrite existing results
    ]

    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"IQ-TREE failed:\n{result.stderr}")

    # Print model selection result
    log_file = f"{output_prefix}.log"
    if os.path.exists(log_file):
        with open(log_file) as f:
            for line in f:
                if "Best-fit model" in line:
                    print(f"IQ-TREE: {line.strip()}")

    output_files = {
        "tree": f"{output_prefix}.treefile",
        "log": f"{output_prefix}.log",
        "iqtree": f"{output_prefix}.iqtree",  # Full report
        "model": f"{output_prefix}.model.gz",
    }

    print(f"IQ-TREE: Tree saved to {output_files['tree']}")
    return output_files

# IQ-TREE model selection guide:
# DNA:     TEST → GTR+G, HKY+G, TrN+G
# Protein: TEST → LG+G4, WAG+G, JTT+G, Q.pfam+G
# Codon:   TEST → MG+F3X4

# For temporal (molecular clock) analysis, add:
# extra_args = ["--date", "dates.txt", "--clock-test", "--date-CI", "95"]
```

### 4. FastTree — Fast Approximate ML

For large datasets (>1000 sequences) where IQ-TREE is too slow:

```python
def run_fasttree(aligned_fasta: str, output_tree: str,
                  sequence_type: str = "nt", model: str = "gtr",
                  n_threads: int = 4) -> str:
    """
    Build a fast approximate ML tree with FastTree.

    Args:
        sequence_type: 'nt' for nucleotide or 'aa' for amino acid
        model: For nt: 'gtr' (recommended) or 'jc'; for aa: 'lg', 'wag', 'jtt'
    """
    if sequence_type == "nt":
        cmd = ["FastTree", "-nt", "-gtr"]
    else:
        cmd = ["FastTree", f"-{model}"]

    cmd += [aligned_fasta]

    with open(output_tree, 'w') as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FastTree failed:\n{result.stderr}")

    print(f"FastTree: Tree saved to {output_tree}")
    return output_tree
```

### 5. Tree Analysis and Visualization with ETE3

```python
from ete3 import Tree, TreeStyle, NodeStyle, TextFace, PhyloTree
import matplotlib.pyplot as plt

def load_tree(tree_file: str) -> Tree:
    """Load a Newick tree file."""
    t = Tree(tree_file)
    print(f"Tree: {len(t)} leaves, {len(list(t.traverse()))} nodes")
    return t

def basic_tree_stats(t: Tree) -> dict:
    """Compute basic tree statistics."""
    leaves = t.get_leaves()
    distances = [t.get_distance(l1, l2) for l1 in leaves[:min(50, len(leaves))]
                 for l2 in leaves[:min(50, len(leaves))] if l1 != l2]

    stats = {
        "n_leaves": len(leaves),
        "n_internal_nodes": len(t) - len(leaves),
        "total_branch_length": sum(n.dist for n in t.traverse()),
        "max_leaf_distance": max(distances) if distances else 0,
        "mean_leaf_distance": sum(distances)/len(distances) if distances else 0,
    }
    return stats

def find_mrca(t: Tree, leaf_names: list) -> Tree:
    """Find the most recent common ancestor of a set of leaves."""
    return t.get_common_ancestor(*leaf_names)

def visualize_tree(t: Tree, output_file: str = "tree.png",
                    show_branch_support: bool = True,
                    color_groups: dict = None,
                    width: int = 800) -> None:
    """
    Render phylogenetic tree to image.

    Args:
        t: ETE3 Tree object
        color_groups: Dict mapping leaf_name → color (for coloring taxa)
        show_branch_support: Show bootstrap values
    """
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_branch_support = show_branch_support
    ts.mode = "r"  # 'r' = rectangular, 'c' = circular

    if color_groups:
        for node in t.traverse():
            if node.is_leaf() and node.name in color_groups:
                nstyle = NodeStyle()
                nstyle["fgcolor"] = color_groups[node.name]
                nstyle["size"] = 8
                node.set_style(nstyle)

    t.render(output_file, tree_style=ts, w=width, units="px")
    print(f"Tree saved to: {output_file}")

def midpoint_root(t: Tree) -> Tree:
    """Root tree at midpoint (use when outgroup unknown)."""
    t.set_outgroup(t.get_midpoint_outgroup())
    return t

def prune_tree(t: Tree, keep_leaves: list) -> Tree:
    """Prune tree to keep only specified leaves."""
    t.prune(keep_leaves, preserve_branch_length=True)
    return t
```

### 6. Complete Analysis Script

```python
import subprocess, os
from ete3 import Tree

def full_phylogenetic_analysis(
    input_fasta: str,
    output_dir: str = "phylo_results",
    sequence_type: str = "nt",
    n_threads: int = 4,
    bootstrap: int = 1000,
    use_fasttree: bool = False
) -> dict:
    """
    Complete phylogenetic pipeline: align → trim → tree → visualize.

    Args:
        input_fasta: Unaligned FASTA
        sequence_type: 'nt' (nucleotide) or 'aa' (amino acid/protein)
        use_fasttree: Use FastTree instead of IQ-TREE (faster for large datasets)
    """
    os.makedirs(output_dir, exist_ok=True)
    prefix = os.path.join(output_dir, "phylo")

    print("=" * 50)
    print("Step 1: Multiple Sequence Alignment (MAFFT)")
    aligned = run_mafft(input_fasta, f"{prefix}_aligned.fasta",
                         method="auto", n_threads=n_threads)

    print("\nStep 2: Tree Inference")
    if use_fasttree:
        tree_file = run_fasttree(
            aligned, f"{prefix}.tree",
            sequence_type=sequence_type,
            model="gtr" if sequence_type == "nt" else "lg"
        )
    else:
        model = "TEST" if sequence_type == "nt" else "TEST"
        iqtree_files = run_iqtree(
            aligned, prefix,
            model=model,
            bootstrap=bootstrap,
            n_threads=n_threads
        )
        tree_file = iqtree_files["tree"]

    print("\nStep 3: Tree Analysis")
    t = Tree(tree_file)
    t = midpoint_root(t)

    stats = basic_tree_stats(t)
    print(f"Tree statistics: {stats}")

    print("\nStep 4: Visualization")
    visualize_tree(t, f"{prefix}_tree.png", show_branch_support=True)

    # Save rooted tree
    rooted_tree_file = f"{prefix}_rooted.nwk"
    t.write(format=1, outfile=rooted_tree_file)

    results = {
        "aligned_fasta": aligned,
        "tree_file": tree_file,
        "rooted_tree": rooted_tree_file,
        "visualization": f"{prefix}_tree.png",
        "stats": stats
    }

    print("\n" + "=" * 50)
    print("Phylogenetic analysis complete!")
    print(f"Results in: {output_dir}/")
    return results
```

## IQ-TREE Model Guide

### DNA Models

| Model | Description | Use case |
|-------|-------------|---------|
| `GTR+G4` | General Time Reversible + Gamma | Most flexible DNA model |
| `HKY+G4` | Hasegawa-Kishino-Yano + Gamma | Two-rate model (common) |
| `TrN+G4` | Tamura-Nei | Unequal transitions |
| `JC` | Jukes-Cantor | Simplest; all rates equal |

### Protein Models

| Model | Description | Use case |
|-------|-------------|---------|
| `LG+G4` | Le-Gascuel + Gamma | Best average protein model |
| `WAG+G4` | Whelan-Goldman | Widely used |
| `JTT+G4` | Jones-Taylor-Thornton | Classical model |
| `Q.pfam+G4` | pfam-trained | For Pfam-like protein families |
| `Q.bird+G4` | Bird-specific | Vertebrate proteins |

**Tip:** Use `-m TEST` to let IQ-TREE automatically select the best model.

## Best Practices

- **Alignment quality first**: Poor alignment → unreliable trees; check alignment manually
- **Use `linsi` for small (<200 seq), `fftns` or `auto` for large alignments**
- **Model selection**: Always use `-m TEST` for IQ-TREE unless you have a specific reason
- **Bootstrap**: Use ≥1000 ultrafast bootstraps (`-B 1000`) for branch support
- **Root the tree**: Unrooted trees can be misleading; use outgroup or midpoint rooting
- **FastTree for >5000 sequences**: IQ-TREE becomes slow; FastTree is 10–100× faster
- **Trim long alignments**: TrimAl removes unreliable columns; improves tree accuracy
- **Check for recombination** in viral/bacterial sequences before building trees (`RDP4`, `GARD`)

## Additional Resources

- **MAFFT**: https://mafft.cbrc.jp/alignment/software/
- **IQ-TREE 2**: http://www.iqtree.org/ | Tutorial: https://www.iqtree.org/workshop/molevol2022
- **FastTree**: http://www.microbesonline.org/fasttree/
- **ETE3**: http://etetoolkit.org/
- **FigTree** (GUI visualization): https://tree.bio.ed.ac.uk/software/figtree/
- **iTOL** (web visualization): https://itol.embl.de/
- **MUSCLE** (alternative aligner): https://www.drive5.com/muscle/
- **TrimAl** (alignment trimming): https://vicfero.github.io/trimal/

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/phylogenetics/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/iqtree_inference.md`

# IQ-TREE 2 Phylogenetic Inference Reference

## Basic Command Syntax

```bash
iqtree2 -s alignment.fasta --prefix output -m TEST -B 1000 -T AUTO --redo
```

## Key Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `-s` | Input alignment file | Required |
| `--prefix` | Output file prefix | alignment name |
| `-m` | Substitution model (or TEST) | GTR+G |
| `-B` | Ultrafast bootstrap replicates | Off |
| `-b` | Standard bootstrap replicates (slow) | Off |
| `-T` | Number of threads (or AUTO) | 1 |
| `-o` | Outgroup taxa name(s) | None (unrooted) |
| `--redo` | Overwrite existing results | Off |
| `-alrt` | SH-aLRT test replicates | Off |

## Model Selection

```bash
# Full model testing (automatically selects best model)
iqtree2 -s alignment.fasta -m TEST --prefix test_run -B 1000 -T 4

# Specify model explicitly
iqtree2 -s alignment.fasta -m GTR+G4 --prefix gtr_run -B 1000

# Protein sequences
iqtree2 -s protein.fasta -m TEST --prefix prot_tree -B 1000

# Codon-based analysis
iqtree2 -s codon.fasta -m GY --prefix codon_tree -B 1000
```

## Bootstrapping Methods

### Ultrafast Bootstrap (UFBoot, recommended)
```bash
iqtree2 -s alignment.fasta -B 1000  # 1000 replicates
# Values ≥95 are reliable
# ~10× faster than standard bootstrap
```

### Standard Bootstrap
```bash
iqtree2 -s alignment.fasta -b 100  # 100 replicates (very slow)
```

### SH-aLRT Test (fast alternative)
```bash
iqtree2 -s alignment.fasta -alrt 1000 -B 1000  # Both SH-aLRT and UFBoot
# SH-aLRT ≥80 AND UFBoot ≥95 = well-supported branch
```

## Branch Support Interpretation

| Bootstrap Value | Interpretation |
|----------------|----------------|
| ≥ 95 | Well-supported (strongly supported) |
| 70–94 | Moderately supported |
| 50–69 | Weakly supported |
| < 50 | Unreliable (not supported) |

## Output Files

| File | Description |
|------|-------------|
| `{prefix}.treefile` | Best ML tree in Newick format |
| `{prefix}.iqtree` | Full analysis report |
| `{prefix}.log` | Computation log |
| `{prefix}.contree` | Consensus tree from bootstrap |
| `{prefix}.splits.nex` | Network splits |
| `{prefix}.bionj` | BioNJ starting tree |
| `{prefix}.model.gz` | Saved model parameters |

## Advanced Analyses

### Molecular Clock (Dating)

```bash
# Temporal analysis with sampling dates
iqtree2 -s alignment.fasta -m GTR+G \
        --date dates.tsv \           # Tab-separated: taxon_name  YYYY-MM-DD
        --clock-test \               # Test for clock-like evolution
        --date-CI 95 \              # 95% CI for node dates
        --prefix dated_tree
```

### Concordance Factors

```bash
# Gene concordance factor (gCF) - requires multiple gene alignments
iqtree2 --gcf gene_trees.nwk \
        --tree main_tree.treefile \
        --cf-verbose \
        --prefix cf_analysis
```

### Ancestral Sequence Reconstruction

```bash
iqtree2 -s alignment.fasta -m LG+G4 \
        -asr \                      # Marginal ancestral state reconstruction
        --prefix anc_tree
# Output: {prefix}.state (ancestral sequences per node)
```

### Partition Model (Multi-Gene)

```bash
# Create partition file (partitions.txt):
# DNA, gene1 = 1-500
# DNA, gene2 = 501-1000

iqtree2 -s concat_alignment.fasta \
        -p partitions.txt \
        -m TEST \
        -B 1000 \
        --prefix partition_tree
```

## IQ-TREE Log Parsing

```python
def parse_iqtree_log(log_file: str) -> dict:
    """Extract key results from IQ-TREE log file."""
    results = {}
    with open(log_file) as f:
        for line in f:
            if "Best-fit model" in line:
                results["best_model"] = line.split(":")[1].strip()
            elif "Log-likelihood of the tree:" in line:
                results["log_likelihood"] = float(line.split(":")[1].strip())
            elif "Number of free parameters" in line:
                results["free_params"] = int(line.split(":")[1].strip())
            elif "Akaike information criterion" in line:
                results["AIC"] = float(line.split(":")[1].strip())
            elif "Bayesian information criterion" in line:
                results["BIC"] = float(line.split(":")[1].strip())
            elif "Total CPU time used" in line:
                results["cpu_time"] = line.split(":")[1].strip()
    return results

# Example:
# results = parse_iqtree_log("output.log")
# print(f"Best model: {results['best_model']}")
# print(f"Log-likelihood: {results['log_likelihood']:.2f}")
```

## Common Issues and Solutions

| Issue | Likely Cause | Solution |
|-------|-------------|---------|
| All bootstrap values = 0 | Too few taxa | Need ≥4 taxa for bootstrap |
| Very long branches | Alignment artifacts | Re-trim alignment; check for outliers |
| Memory error | Too many sequences | Use FastTree; or reduce `-T` to 1 |
| Poor model fit | Wrong alphabet | Check nucleotide vs. protein specification |
| Identical sequences | Duplicate sequences | Remove duplicates before alignment |

## MAFFT Alignment Guide

```bash
# Accurate (< 200 sequences)
mafft --localpair --maxiterate 1000 input.fasta > aligned.fasta

# Medium (200-1000 sequences)
mafft --auto input.fasta > aligned.fasta

# Fast (> 1000 sequences)
mafft --fftns input.fasta > aligned.fasta

# Very large (> 10000 sequences)
mafft --retree 1 input.fasta > aligned.fasta

# Using multiple threads
mafft --thread 8 --auto input.fasta > aligned.fasta
```

### `scripts/phylogenetic_analysis.py`

```python
"""
Phylogenetic Analysis Pipeline
===============================
Complete workflow: MAFFT alignment → IQ-TREE tree → ETE3 visualization.

Requirements:
    conda install -c bioconda mafft iqtree
    uv pip install ete3

Usage:
    python phylogenetic_analysis.py sequences.fasta --type nt --threads 4
    python phylogenetic_analysis.py proteins.fasta --type aa --fasttree
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Check that required tools are installed."""
    tools = {
        "mafft": "conda install -c bioconda mafft",
        "iqtree2": "conda install -c bioconda iqtree",
    }
    missing = []
    for tool, install_cmd in tools.items():
        result = subprocess.run(["which", tool], capture_output=True)
        if result.returncode != 0:
            missing.append(f"  {tool}: {install_cmd}")

    if missing:
        print("Missing dependencies:")
        for m in missing:
            print(m)
        sys.exit(1)
    print("All dependencies found.")


def count_sequences(fasta_file: str) -> int:
    """Count sequences in a FASTA file."""
    with open(fasta_file) as f:
        return sum(1 for line in f if line.startswith('>'))


def run_mafft(input_fasta: str, output_fasta: str, n_threads: int = 4,
               method: str = "auto") -> str:
    """Run MAFFT multiple sequence alignment."""
    n_seqs = count_sequences(input_fasta)
    print(f"MAFFT: Aligning {n_seqs} sequences...")

    # Auto-select method based on dataset size
    if method == "auto":
        if n_seqs <= 200:
            cmd = ["mafft", "--localpair", "--maxiterate", "1000",
                   "--thread", str(n_threads), "--inputorder", input_fasta]
        elif n_seqs <= 1000:
            cmd = ["mafft", "--auto", "--thread", str(n_threads),
                   "--inputorder", input_fasta]
        else:
            cmd = ["mafft", "--fftns", "--thread", str(n_threads),
                   "--inputorder", input_fasta]
    else:
        cmd = ["mafft", f"--{method}", "--thread", str(n_threads),
               "--inputorder", input_fasta]

    with open(output_fasta, 'w') as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"MAFFT failed:\n{result.stderr[:500]}")

    print(f"  Alignment complete → {output_fasta}")
    return output_fasta


def run_iqtree(aligned_fasta: str, prefix: str, seq_type: str = "nt",
                bootstrap: int = 1000, n_threads: int = 4,
                outgroup: str = None) -> str:
    """Run IQ-TREE 2 phylogenetic inference."""
    print(f"IQ-TREE 2: Building maximum likelihood tree...")

    cmd = [
        "iqtree2",
        "-s", aligned_fasta,
        "--prefix", prefix,
        "-m", "TEST",           # Auto model selection
        "-B", str(bootstrap),   # Ultrafast bootstrap
        "-T", str(n_threads),
        "--redo",
        "-alrt", "1000",        # SH-aLRT test
    ]

    if outgroup:
        cmd += ["-o", outgroup]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"IQ-TREE failed:\n{result.stderr[:500]}")

    tree_file = f"{prefix}.treefile"

    # Extract best model from log
    log_file = f"{prefix}.log"
    if os.path.exists(log_file):
        with open(log_file) as f:
            for line in f:
                if "Best-fit model" in line:
                    print(f"  {line.strip()}")

    print(f"  Tree saved → {tree_file}")
    return tree_file


def run_fasttree(aligned_fasta: str, output_tree: str, seq_type: str = "nt") -> str:
    """Run FastTree (faster alternative for large datasets)."""
    print("FastTree: Building approximate ML tree (faster)...")

    if seq_type == "nt":
        cmd = ["FastTree", "-nt", "-gtr", "-gamma", aligned_fasta]
    else:
        cmd = ["FastTree", "-lg", "-gamma", aligned_fasta]

    with open(output_tree, 'w') as out:
        result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"FastTree failed:\n{result.stderr[:500]}")

    print(f"  Tree saved → {output_tree}")
    return output_tree


def visualize_tree(tree_file: str, output_png: str, outgroup: str = None) -> None:
    """Visualize the phylogenetic tree with ETE3."""
    try:
        from ete3 import Tree, TreeStyle, NodeStyle
    except ImportError as exc:
        # TreeStyle and NodeStyle live in ete3's Qt-backed treeview module, so
        # this also fires when ete3 itself imported fine but PyQt5 is missing.
        print(f"ETE3 rendering unavailable ({exc}). Skipping visualization.")
        print("  Install: uv pip install ete3 PyQt5")
        return

    t = Tree(tree_file)

    # Root the tree
    if outgroup and outgroup in [leaf.name for leaf in t.get_leaves()]:
        t.set_outgroup(outgroup)
        print(f"  Rooted at outgroup: {outgroup}")
    else:
        # Midpoint rooting
        t.set_outgroup(t.get_midpoint_outgroup())
        print("  Applied midpoint rooting")

    # Style
    ts = TreeStyle()
    ts.show_leaf_name = True
    ts.show_branch_support = True
    ts.mode = "r"  # rectangular

    try:
        t.render(output_png, tree_style=ts, w=800, units="px")
        print(f"  Visualization saved → {output_png}")
    except Exception as e:
        print(f"  Visualization failed (display issue?): {e}")
        # Save tree in Newick format as fallback
        rooted_nwk = output_png.replace(".png", "_rooted.nwk")
        t.write(format=1, outfile=rooted_nwk)
        print(f"  Rooted tree saved → {rooted_nwk}")


def tree_summary(tree_file: str) -> dict:
    """Print summary statistics for the tree."""
    try:
        from ete3 import Tree
        t = Tree(tree_file)
        t.set_outgroup(t.get_midpoint_outgroup())

        leaves = t.get_leaves()
        branch_lengths = [n.dist for n in t.traverse() if n.dist > 0]

        stats = {
            "n_taxa": len(leaves),
            "total_branch_length": sum(branch_lengths),
            "mean_branch_length": sum(branch_lengths) / len(branch_lengths) if branch_lengths else 0,
            "max_branch_length": max(branch_lengths) if branch_lengths else 0,
        }

        print("\nTree Summary:")
        for k, v in stats.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.6f}")
            else:
                print(f"  {k}: {v}")

        return stats
    except Exception as e:
        print(f"Could not compute tree stats: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description="Phylogenetic analysis pipeline")
    parser.add_argument("input", help="Input FASTA file (unaligned)")
    parser.add_argument("--type", choices=["nt", "aa"], default="nt",
                        help="Sequence type: nt (nucleotide) or aa (amino acid)")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads")
    parser.add_argument("--bootstrap", type=int, default=1000,
                        help="Bootstrap replicates for IQ-TREE")
    parser.add_argument("--fasttree", action="store_true",
                        help="Use FastTree instead of IQ-TREE (faster, less accurate)")
    parser.add_argument("--outgroup", help="Outgroup taxon name for rooting")
    parser.add_argument("--mafft-method", default="auto",
                        choices=["auto", "linsi", "einsi", "fftnsi", "fftns"],
                        help="MAFFT alignment method")
    parser.add_argument("--output-dir", default="phylo_results",
                        help="Output directory")

    args = parser.parse_args()

    # Setup
    os.makedirs(args.output_dir, exist_ok=True)
    prefix = os.path.join(args.output_dir, Path(args.input).stem)

    print("=" * 60)
    print("Phylogenetic Analysis Pipeline")
    print("=" * 60)
    print(f"Input: {args.input}")
    print(f"Sequence type: {args.type}")
    print(f"Output dir: {args.output_dir}")

    # Step 1: Multiple Sequence Alignment
    print("\n[Step 1/3] Multiple Sequence Alignment (MAFFT)")
    aligned = run_mafft(
        args.input,
        f"{prefix}_aligned.fasta",
        n_threads=args.threads,
        method=args.mafft_method
    )

    # Step 2: Tree Inference
    print("\n[Step 2/3] Tree Inference")
    if args.fasttree:
        tree_file = run_fasttree(aligned, f"{prefix}.tree", seq_type=args.type)
    else:
        tree_file = run_iqtree(
            aligned, prefix,
            seq_type=args.type,
            bootstrap=args.bootstrap,
            n_threads=args.threads,
            outgroup=args.outgroup
        )

    # Step 3: Visualization
    print("\n[Step 3/3] Visualization (ETE3)")
    visualize_tree(tree_file, f"{prefix}_tree.png", outgroup=args.outgroup)
    tree_summary(tree_file)

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print(f"Key outputs:")
    print(f"  Aligned sequences: {aligned}")
    print(f"  Tree file: {tree_file}")
    print(f"  Visualization: {prefix}_tree.png")


if __name__ == "__main__":
    main()
```
