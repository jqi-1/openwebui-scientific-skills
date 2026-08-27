---
name: deeptools
description: NGS analysis toolkit. BAM to bigWig conversion, QC (correlation, PCA, fingerprints), heatmaps/profiles (TSS, peaks), for ChIP-seq, RNA-seq, ATAC-seq visualization.
---

# deepTools: NGS Data Analysis Toolkit

## Overview

deepTools is a comprehensive suite of Python command-line tools designed for processing and analyzing high-throughput sequencing data. Use deepTools to perform quality control, normalize data, compare samples, and generate publication-quality visualizations for ChIP-seq, RNA-seq, ATAC-seq, MNase-seq, and other NGS experiments.

**Core capabilities:**
- Convert BAM alignments to normalized coverage tracks (bigWig/bedGraph)
- Quality control assessment (fingerprint, correlation, coverage)
- Sample comparison and correlation analysis
- Heatmap and profile plot generation around genomic features
- Enrichment analysis and peak region visualization

## When to Use This Skill

This skill should be used when:

- **File conversion**: "Convert BAM to bigWig", "generate coverage tracks", "normalize ChIP-seq data"
- **Quality control**: "check ChIP quality", "compare replicates", "assess sequencing depth", "QC analysis"
- **Visualization**: "create heatmap around TSS", "plot ChIP signal", "visualize enrichment", "generate profile plot"
- **Sample comparison**: "compare treatment vs control", "correlate samples", "PCA analysis"
- **Analysis workflows**: "analyze ChIP-seq data", "RNA-seq coverage", "ATAC-seq analysis", "complete workflow"
- **Working with specific file types**: BAM files, bigWig files, BED region files in genomics context

## Quick Start

For users new to deepTools, start with file validation and common workflows:

### 1. Validate Input Files

Before running any analysis, validate BAM, bigWig, and BED files using the validation script:

```bash
python scripts/validate_files.py --bam sample1.bam sample2.bam --bed regions.bed
```

This checks file existence, BAM indices, and format correctness.

### 2. Generate Workflow Template

For standard analyses, use the workflow generator to create customized scripts:

```bash
# List available workflows
python scripts/workflow_generator.py --list

# Generate ChIP-seq QC workflow
python scripts/workflow_generator.py chipseq_qc -o qc_workflow.sh \
    --input-bam Input.bam --chip-bams "ChIP1.bam ChIP2.bam" \
    --genome-size 2913022398

# Make executable and run
chmod +x qc_workflow.sh
./qc_workflow.sh
```

### 3. Most Common Operations

See `assets/quick_reference.md` for frequently used commands and parameters.

## Installation

```bash
uv pip install deepTools==3.5.6
```

Upstream recommends conda/bioconda for full dependency resolution, especially on shared HPC systems:

```bash
conda install -c conda-forge -c bioconda deeptools
```

On Apple Silicon, upstream documents either the PyPI route above or an `osx-64` conda environment when native conda packages are unavailable.

## Core Workflows and Tool Categories

Complete command sequences for ChIP-seq QC, full ChIP-seq analysis, RNA-seq coverage, and
ATAC-seq analysis — plus the BAM/bigWig processing, quality control, and visualization
tool categories — are in [references/core_workflows.md](references/core_workflows.md) and
[references/workflows.md](references/workflows.md). Per-tool options are in
[references/tools_reference.md](references/tools_reference.md).

## Normalization Methods

Choosing the correct normalization is critical for valid comparisons. Consult `references/normalization_methods.md` for comprehensive guidance.

**Quick selection guide:**

- **ChIP-seq coverage**: Use RPGC or CPM
- **ChIP-seq comparison**: Use bamCompare with log2 and readCount
- **RNA-seq bins**: Use CPM
- **RNA-seq genes**: Use RPKM (accounts for gene length)
- **ATAC-seq**: Use RPGC or CPM

**Normalization methods:**
- **RPGC**: 1× genome coverage (requires --effectiveGenomeSize)
- **CPM**: Counts per million mapped reads
- **RPKM**: Reads per kb per million (per-bin length and library-size scaling)
- **BPM**: Bins per million, analogous to TPM-style scaling over binned signal
- **None**: Raw counts (not recommended for comparisons)

Full explanation: `references/normalization_methods.md`

## Effective Genome Sizes

RPGC normalization requires effective genome size. Common values:

| Organism | Assembly | Size | Usage |
|----------|----------|------|-------|
| Human | GRCh38/hg38 | 2,913,022,398 | `--effectiveGenomeSize 2913022398` |
| Human | T2T/CHM13CAT_v2 | 3,117,292,070 | `--effectiveGenomeSize 3117292070` |
| Mouse | GRCm39/mm39 | 2,654,621,783 | `--effectiveGenomeSize 2654621783` |
| Mouse | GRCm38/mm10 | 2,652,783,500 | `--effectiveGenomeSize 2652783500` |
| Zebrafish | GRCz11 | 1,368,780,147 | `--effectiveGenomeSize 1368780147` |
| *Drosophila* | dm6 | 142,573,017 | `--effectiveGenomeSize 142573017` |
| *C. elegans* | ce10/ce11 | 100,286,401 | `--effectiveGenomeSize 100286401` |

Complete table with read-length-specific values: `references/effective_genome_sizes.md`

## Common Parameters Across Tools

Many deepTools commands share these options:

**Performance:**
- `--numberOfProcessors, -p`: Enable parallel processing (always use available cores)
- `max` / `max/2`: Supported values for `--numberOfProcessors`; useful under schedulers because recent deepTools releases detect CPU affinity more carefully
- `--region`: Process specific regions for testing (e.g., `chr1:1-1000000`)

**Read Filtering:**
- `--ignoreDuplicates`: Remove PCR duplicates (recommended for most analyses)
- `--minMappingQuality`: Filter by alignment quality (e.g., `--minMappingQuality 10`)
- `--minFragmentLength` / `--maxFragmentLength`: Fragment length bounds
- `--samFlagInclude` / `--samFlagExclude`: SAM flag filtering

**Read Processing:**
- `--extendReads`: Extend to fragment length (ChIP-seq: YES, RNA-seq: NO)
- `--centerReads`: Center at fragment midpoint for sharper signals

## Best Practices

### File Validation
**Always validate files first** using `scripts/validate_files.py` to check:
- File existence and readability
- BAM indices present (.bai files)
- BED format correctness
- File sizes reasonable

### Analysis Strategy

1. **Start with QC**: Run correlation, coverage, and fingerprint analysis before proceeding
2. **Test on small regions**: Use `--region chr1:1-10000000` for parameter testing
3. **Document commands**: Save full command lines for reproducibility
4. **Use consistent normalization**: Apply same method across samples in comparisons
5. **Verify genome assembly**: Ensure BAM and BED files use matching genome builds

### ChIP-seq Specific

- **Always extend reads** for ChIP-seq: `--extendReads 200`
- **Remove duplicates**: Use `--ignoreDuplicates` in most cases
- **Check enrichment first**: Run plotFingerprint before detailed analysis
- **GC correction**: Only apply if significant bias detected; never use `--ignoreDuplicates` after GC correction

### RNA-seq Specific

- **Never extend reads** for RNA-seq (would span splice junctions)
- **Strand-specific**: Use `--filterRNAstrand forward/reverse` for common dUTP-style stranded libraries; confirm library orientation before interpreting strand labels
- **Normalization**: CPM for bins, RPKM for genes

### ATAC-seq Specific

- **Apply Tn5 correction**: Use alignmentSieve with `--ATACshift`
- **Use only proper pairs for shifting**: `--ATACshift` is equivalent to `--shift 4 -5 5 -4` and filters to properly paired fragments
- **Fragment filtering**: Set appropriate min/max fragment lengths
- **Check nucleosome pattern**: Fragment size plot should show ladder pattern

### Performance Optimization

1. **Use multiple processors**: `--numberOfProcessors 8` (or available cores)
2. **Increase bin size** for faster processing and smaller files
3. **Process chromosomes separately** for memory-limited systems
4. **Pre-filter BAM files** using alignmentSieve to create reusable filtered files
5. **Use bigWig over bedGraph**: Compressed and faster to process

## Troubleshooting

### Common Issues

**BAM index missing:**
```bash
samtools index input.bam
```

**Out of memory:**
Process chromosomes individually using `--region`:
```bash
bamCoverage --bam input.bam -o chr1.bw --region chr1
```

**Slow processing:**
Increase `--numberOfProcessors` and/or increase `--binSize`

**bigWig files too large:**
Increase bin size: `--binSize 50` or larger

### Validation Errors

Run validation script to identify issues:
```bash
python scripts/validate_files.py --bam *.bam --bed regions.bed
```

Common errors and solutions explained in script output.

## Reference Documentation

This skill includes comprehensive reference documentation:

### references/tools_reference.md
Complete documentation of all deepTools commands organized by category:
- BAM and bigWig processing tools (9 tools)
- Quality control tools (6 tools)
- Visualization tools (3 tools)
- Miscellaneous tools (3 tools, including `bigwigAverage`)

Each tool includes:
- Purpose and overview
- Key parameters with explanations
- Usage examples
- Important notes and best practices

**Use this reference when:** Users ask about specific tools, parameters, or detailed usage.

### references/workflows.md
Complete workflow examples for common analyses:
- ChIP-seq quality control workflow
- ChIP-seq complete analysis workflow
- RNA-seq coverage workflow
- ATAC-seq analysis workflow
- Multi-sample comparison workflow
- Peak region analysis workflow
- Troubleshooting and performance tips

**Use this reference when:** Users need complete analysis pipelines or workflow examples.

### references/normalization_methods.md
Comprehensive guide to normalization methods:
- Detailed explanation of each method (RPGC, CPM, RPKM, BPM, etc.)
- When to use each method
- Formulas and interpretation
- Selection guide by experiment type
- Common pitfalls and solutions
- Quick reference table

**Use this reference when:** Users ask about normalization, comparing samples, or which method to use.

### references/effective_genome_sizes.md
Effective genome size values and usage:
- Common organism values (human, mouse, fly, worm, zebrafish)
- Read-length-specific values
- Calculation methods
- When and how to use in commands
- Custom genome calculation instructions

**Use this reference when:** Users need genome size for RPGC normalization or GC bias correction.

## Helper Scripts

### scripts/validate_files.py

Validates BAM, bigWig, and BED files for deepTools analysis. Checks file existence, indices, and format.

**Usage:**
```bash
python scripts/validate_files.py --bam sample1.bam sample2.bam \
    --bed peaks.bed --bigwig signal.bw
```

**When to use:** Before starting any analysis, or when troubleshooting errors.

### scripts/workflow_generator.py

Generates customizable bash script templates for common deepTools workflows.

**Available workflows:**
- `chipseq_qc`: ChIP-seq quality control
- `chipseq_analysis`: Complete ChIP-seq analysis
- `rnaseq_coverage`: Strand-specific RNA-seq coverage
- `atacseq`: ATAC-seq with Tn5 correction

**Usage:**
```bash
# List workflows
python scripts/workflow_generator.py --list

# Generate workflow
python scripts/workflow_generator.py chipseq_qc -o qc.sh \
    --input-bam Input.bam --chip-bams "ChIP1.bam ChIP2.bam" \
    --genome-size 2913022398 --threads 8

# Run generated workflow
chmod +x qc.sh
./qc.sh
```

**When to use:** Users request standard workflows or need template scripts to customize.

## Assets

### assets/quick_reference.md

Quick reference card with most common commands, effective genome sizes, and typical workflow pattern.

**When to use:** Users need quick command examples without detailed documentation.

## Handling User Requests

### For New Users

1. Start with installation verification
2. Validate input files using `scripts/validate_files.py`
3. Recommend appropriate workflow based on experiment type
4. Generate workflow template using `scripts/workflow_generator.py`
5. Guide through customization and execution

### For Experienced Users

1. Provide specific tool commands for requested operations
2. Reference appropriate sections in `references/tools_reference.md`
3. Suggest optimizations and best practices
4. Offer troubleshooting for issues

### For Specific Tasks

**"Convert BAM to bigWig":**
- Use bamCoverage with appropriate normalization
- Recommend RPGC or CPM based on use case
- Provide effective genome size for organism
- Suggest relevant parameters (extendReads, ignoreDuplicates, binSize)

**"Check ChIP quality":**
- Run full QC workflow or use plotFingerprint specifically
- Explain interpretation of results
- Suggest follow-up actions based on results

**"Create heatmap":**
- Guide through two-step process: computeMatrix → plotHeatmap
- Help choose appropriate matrix mode (reference-point vs scale-regions)
- Suggest visualization parameters and clustering options

**"Compare samples":**
- Recommend bamCompare for two-sample comparison
- Suggest multiBamSummary + plotCorrelation for multiple samples
- Guide normalization method selection

### Referencing Documentation

When users need detailed information:
- **Tool details**: Direct to specific sections in `references/tools_reference.md`
- **Workflows**: Use `references/workflows.md` for complete analysis pipelines
- **Normalization**: Consult `references/normalization_methods.md` for method selection
- **Genome sizes**: Reference `references/effective_genome_sizes.md`

## Example Interactions

**User: "I need to analyze my ChIP-seq data"**

Response approach:
1. Ask about files available (BAM files, peaks, genes)
2. Validate files using validation script
3. Generate chipseq_analysis workflow template
4. Customize for their specific files and organism
5. Explain each step as script runs

**User: "Which normalization should I use?"**

Response approach:
1. Ask about experiment type (ChIP-seq, RNA-seq, etc.)
2. Ask about comparison goal (within-sample or between-sample)
3. Consult `references/normalization_methods.md` selection guide
4. Recommend appropriate method with justification
5. Provide command example with parameters

**User: "Create a heatmap around TSS"**

Response approach:
1. Verify bigWig and gene BED files available
2. Use computeMatrix with reference-point mode at TSS
3. Generate plotHeatmap with appropriate visualization parameters
4. Suggest clustering if dataset is large
5. Offer profile plot as complement

## Key Reminders

- **File validation first**: Always validate input files before analysis
- **Normalization matters**: Choose appropriate method for comparison type
- **Extend reads carefully**: YES for ChIP-seq, NO for RNA-seq
- **Use all cores**: Set `--numberOfProcessors` to available cores
- **Test on regions**: Use `--region` for parameter testing
- **Check QC first**: Run quality control before detailed analysis
- **Document everything**: Save commands for reproducibility
- **Reference documentation**: Use comprehensive references for detailed guidance

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/deeptools/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/core_workflows.md`

# Core Workflows and Tool Categories

Complete command sequences for ChIP-seq quality control, full ChIP-seq analysis, RNA-seq
coverage, and ATAC-seq analysis, then the tool categories: BAM/bigWig processing, quality
control, and visualization.

## Core Workflows

deepTools workflows typically follow this pattern: **QC → Normalization → Comparison/Visualization**

### ChIP-seq Quality Control Workflow

When users request ChIP-seq QC or quality assessment:

1. **Generate workflow script** using `scripts/workflow_generator.py chipseq_qc`
2. **Key QC steps**:
   - Sample correlation (multiBamSummary + plotCorrelation)
   - PCA analysis (plotPCA)
   - Coverage assessment (plotCoverage)
   - Fragment size validation (bamPEFragmentSize)
   - ChIP enrichment strength (plotFingerprint)

**Interpreting results:**
- **Correlation**: Replicates should cluster together with high correlation (>0.9)
- **Fingerprint**: Strong ChIP shows steep rise; flat diagonal indicates poor enrichment
- **Coverage**: Assess if sequencing depth is adequate for analysis

Full workflow details in `references/workflows.md` → "ChIP-seq Quality Control Workflow"

### ChIP-seq Complete Analysis Workflow

For full ChIP-seq analysis from BAM to visualizations:

1. **Generate coverage tracks** with normalization (bamCoverage)
2. **Create comparison tracks** (bamCompare for log2 ratio)
3. **Compute signal matrices** around features (computeMatrix)
4. **Generate visualizations** (plotHeatmap, plotProfile)
5. **Enrichment analysis** at peaks (plotEnrichment)

Use `scripts/workflow_generator.py chipseq_analysis` to generate template.

Complete command sequences in `references/workflows.md` → "ChIP-seq Analysis Workflow"

### RNA-seq Coverage Workflow

For strand-specific RNA-seq coverage tracks:

Use bamCoverage with `--filterRNAstrand` to separate forward and reverse strands.

**Important:** NEVER use `--extendReads` for RNA-seq (would extend over splice junctions).

**Strand note:** `--filterRNAstrand` assumes common dUTP/NSR/NNSR reverse-stranded library preparation. For libraries where read 1 follows the RNA strand, forward/reverse output is inverted; use SAM flag filters when library chemistry differs.

Use normalization: CPM for fixed bins, RPKM for gene-level analysis.

Template available: `scripts/workflow_generator.py rnaseq_coverage`

Details in `references/workflows.md` → "RNA-seq Coverage Workflow"

### ATAC-seq Analysis Workflow

ATAC-seq requires Tn5 offset correction:

1. **Shift reads** using alignmentSieve with `--ATACshift`
2. **Generate coverage** with bamCoverage
3. **Analyze fragment sizes** (expect nucleosome ladder pattern)
4. **Visualize at peaks** if available

Template: `scripts/workflow_generator.py atacseq`

Full workflow in `references/workflows.md` → "ATAC-seq Workflow"

## Tool Categories and Common Tasks

### BAM/bigWig Processing

**Convert BAM to normalized coverage:**
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC --effectiveGenomeSize 2913022398 \
    --binSize 10 --numberOfProcessors 8
```

**Compare two samples (log2 ratio):**
```bash
bamCompare -b1 treatment.bam -b2 control.bam -o ratio.bw \
    --operation log2 --scaleFactorsMethod readCount
```

**Key tools:** bamCoverage, bamCompare, multiBamSummary, multiBigwigSummary, correctGCBias, alignmentSieve

Complete reference: `references/tools_reference.md` → "BAM and bigWig File Processing Tools"

### Quality Control

**Check ChIP enrichment:**
```bash
plotFingerprint -b input.bam chip.bam -o fingerprint.png \
    --extendReads 200 --ignoreDuplicates
```

**Sample correlation:**
```bash
multiBamSummary bins --bamfiles *.bam -o counts.npz
plotCorrelation -in counts.npz --corMethod pearson \
    --whatToShow heatmap -o correlation.png
```

**Key tools:** plotFingerprint, plotCoverage, plotCorrelation, plotPCA, bamPEFragmentSize

Complete reference: `references/tools_reference.md` → "Quality Control Tools"

### Visualization

**Create heatmap around TSS:**
```bash
# Compute matrix
computeMatrix reference-point -S signal.bw -R genes.bed \
    -b 3000 -a 3000 --referencePoint TSS -o matrix.gz

# Generate heatmap
plotHeatmap -m matrix.gz -o heatmap.png \
    --colorMap RdBu --kmeans 3
```

**Create profile plot:**
```bash
plotProfile -m matrix.gz -o profile.png \
    --plotType lines --colors blue red
```

**Key tools:** computeMatrix, plotHeatmap, plotProfile, plotEnrichment

Complete reference: `references/tools_reference.md` → "Visualization Tools"

### `references/effective_genome_sizes.md`

# Effective Genome Sizes

## Definition

Effective genome size refers to the length of the "mappable" genome - regions that can be uniquely mapped by sequencing reads. This metric is crucial for proper normalization in many deepTools commands.

## Why It Matters

- Required for RPGC normalization (`--normalizeUsing RPGC`)
- Affects accuracy of coverage calculations
- Must match your data processing approach (filtered vs unfiltered reads)

## Calculation Methods

1. **Non-N bases**: Count of non-N nucleotides in genome sequence
2. **Unique mappability**: Regions of specific size that can be uniquely mapped (may consider edit distance)

## Common Organism Values

### Using Non-N Bases Method

| Organism | Assembly | Effective Size | Full Command |
|----------|----------|----------------|--------------|
| Human | GRCh38/hg38 | 2,913,022,398 | `--effectiveGenomeSize 2913022398` |
| Human | GRCh37/hg19 | 2,864,785,220 | `--effectiveGenomeSize 2864785220` |
| Human | T2T/CHM13CAT_v2 | 3,117,292,070 | `--effectiveGenomeSize 3117292070` |
| Mouse | GRCm39/mm39 | 2,654,621,783 | `--effectiveGenomeSize 2654621783` |
| Mouse | GRCm38/mm10 | 2,652,783,500 | `--effectiveGenomeSize 2652783500` |
| Zebrafish | GRCz11 | 1,368,780,147 | `--effectiveGenomeSize 1368780147` |
| *Drosophila* | dm6 | 142,573,017 | `--effectiveGenomeSize 142573017` |
| *C. elegans* | WBcel235/ce11 | 100,286,401 | `--effectiveGenomeSize 100286401` |
| *C. elegans* | ce10 | 100,258,171 | `--effectiveGenomeSize 100258171` |
| *Arabidopsis thaliana* | TAIR10 | 119,482,012 | `--effectiveGenomeSize 119482012` |

### Human (GRCh38) by Read Length

For quality-filtered reads, values vary by read length:

| Read Length | Effective Size |
|-------------|----------------|
| 50bp | ~2.7 billion |
| 75bp | ~2.8 billion |
| 100bp | ~2.8 billion |
| 150bp | ~2.9 billion |
| 250bp | ~2.9 billion |

### Mouse (GRCm38) by Read Length

| Read Length | Effective Size |
|-------------|----------------|
| 50bp | ~2.3 billion |
| 75bp | ~2.5 billion |
| 100bp | ~2.6 billion |

## Usage in deepTools

The effective genome size is most commonly used with:

### bamCoverage with RPGC normalization
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398
```

### bamCompare with RPGC normalization
```bash
bamCompare -b1 treatment.bam -b2 control.bam \
    --outFileName comparison.bw \
    --scaleFactorsMethod RPGC \
    --effectiveGenomeSize 2913022398
```

### computeGCBias / correctGCBias
```bash
computeGCBias --bamfile input.bam \
    --effectiveGenomeSize 2913022398 \
    --genome genome.2bit \
    --fragmentLength 200 \
    --biasPlot bias.png
```

## Choosing the Right Value

**For most analyses with multimapping reads retained:** Use the non-N bases method value for your reference genome

**For filtered data:** If you apply MAPQ filters or remove multimapping reads, consider read-length-specific mappability values

**When unsure:** Use the conservative non-N bases value - it's more widely applicable

## Common Shortcuts

deepTools also accepts these shorthand values in some contexts:

- `hs` or `GRCh38`: 2913022398
- `mm` or `GRCm38`: 2652783500
- `dm` or `dm6`: 142573017
- `ce` or `ce10`: 100286401

Check your specific deepTools version documentation for supported shortcuts.

## Calculating Custom Values

For custom genomes or assemblies, calculate the non-N bases count:

```bash
# Using faCount (UCSC tools)
faCount genome.fa | grep "total" | awk '{print $2-$7}'

# Using seqtk
seqtk comp genome.fa | awk '{x+=$2}END{print x}'
```

## References

For the most up-to-date effective genome sizes and detailed calculation methods, see:
- deepTools documentation: https://deeptools.readthedocs.io/en/latest/content/feature/effectiveGenomeSize.html
- ENCODE documentation for reference genome details

### `references/normalization_methods.md`

# deepTools Normalization Methods

This document explains the various normalization methods available in deepTools and when to use each one.

## Why Normalize?

Normalization is essential for:
1. **Comparing samples with different sequencing depths**
2. **Accounting for library size differences**
3. **Making coverage values interpretable across experiments**
4. **Enabling fair comparisons between conditions**

Without normalization, a sample with 100 million reads will appear to have higher coverage than a sample with 50 million reads, even if the true biological signal is identical.

---

## Available Normalization Methods

### 1. RPKM (Reads Per Kilobase per Million mapped reads)

**Formula:** `(Number of reads) / (Length of region in kb × Total mapped reads in millions)`

**When to use:**
- Comparing different genomic regions within the same sample
- Adjusting for both sequencing depth AND region length
- RNA-seq gene expression analysis

**Available in:** `bamCoverage`

**Example:**
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPKM
```

**Interpretation:** RPKM of 10 means 10 reads per kilobase of feature per million mapped reads.

**Pros:**
- Accounts for both region length and library size
- Widely used and understood in genomics

**Cons:**
- Not ideal for comparing between samples if total RNA content differs
- Can be misleading when comparing samples with very different compositions

---

### 2. CPM (Counts Per Million mapped reads)

**Formula:** `(Number of reads) / (Total mapped reads in millions)`

**Also known as:** RPM (Reads Per Million)

**When to use:**
- Comparing the same genomic regions across different samples
- When region length is constant or not relevant
- ChIP-seq, ATAC-seq, DNase-seq analyses

**Available in:** `bamCoverage`, `bamCompare`

**Example:**
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing CPM
```

**Interpretation:** CPM of 5 means 5 reads per million mapped reads in that bin.

**Pros:**
- Simple and intuitive
- Good for comparing samples with different sequencing depths
- Appropriate when comparing fixed-size bins

**Cons:**
- Does not account for region length
- Affected by highly abundant regions (e.g., rRNA in RNA-seq)

---

### 3. BPM (Bins Per Million mapped reads)

**Formula:** `(Number of reads in bin) / (Sum of all reads in bins in millions)`

**Key difference from CPM:** deepTools scales by the sum of reads across all bins, analogous to TPM-style scaling for RNA-seq signal tracks.

**When to use:**
- Similar to CPM, but when you want to exclude reads outside analyzed regions
- Comparing specific genomic regions while ignoring background

**Available in:** `bamCoverage`, `bamCompare`

**Example:**
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing BPM
```

**Interpretation:** BPM accounts only for reads in the binned regions.

**Pros:**
- Focuses normalization on analyzed regions
- Less affected by reads in unanalyzed areas

**Cons:**
- Less commonly used, may be harder to compare with published data

---

### 4. RPGC (Reads Per Genomic Content)

**Formula:** `(Number of reads per bin) / scaling factor for 1× average genomic coverage`

**Scaling factor:** deepTools estimates sequencing depth as `(total mapped reads × fragment length) / effective genome size`, then applies the inverse to match 1× average coverage.

**When to use:**
- Want comparable coverage values across samples
- Need interpretable absolute coverage values
- Comparing samples with very different total read counts
- ChIP-seq with spike-in normalization context

**Available in:** `bamCoverage`, `bamCompare`

**Requires:** `--effectiveGenomeSize` parameter

**Example:**
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398
```

**Interpretation:** Signal value approximates the coverage depth (e.g., value of 2 ≈ 2× coverage).

**Pros:**
- Produces 1× normalized coverage
- Interpretable in terms of genomic coverage
- Good for comparing samples with different sequencing depths

**Cons:**
- Requires knowing effective genome size
- Effective genome size should change if blacklists, MAPQ filters, or multimapper removal substantially change the mappable space
- Assumes uniform coverage (not true for ChIP-seq with peaks)

---

### 5. None (No Normalization)

**Formula:** Raw read counts

**When to use:**
- Preliminary analysis
- When samples have identical library sizes (rare)
- When downstream tool will perform normalization
- Debugging or quality control

**Available in:** All tools (usually default)

**Example:**
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing None
```

**Interpretation:** Raw read counts per bin.

**Pros:**
- No assumptions made
- Useful for seeing raw data
- Fastest computation

**Cons:**
- Cannot fairly compare samples with different sequencing depths
- Not suitable for publication figures

---

### 6. SES (Selective Enrichment Statistics)

**Method:** Signal Extraction Scaling - more sophisticated method for comparing ChIP to control

**When to use:**
- ChIP-seq analysis with bamCompare
- Want sophisticated background correction
- Alternative to simple readCount scaling

**Available in:** `bamCompare` only

**Example:**
```bash
bamCompare -b1 chip.bam -b2 input.bam -o output.bw \
    --scaleFactorsMethod SES
```

**Note:** SES is specifically designed for ChIP-seq data and may work better than simple read count scaling for noisy data.

---

### 7. readCount (Read Count Scaling)

**Method:** Scale by ratio of total read counts between samples

**When to use:**
- Default for `bamCompare`
- Compensating for sequencing depth differences in comparisons
- When you trust that total read counts reflect library size

**Available in:** `bamCompare`

**Example:**
```bash
bamCompare -b1 treatment.bam -b2 control.bam -o output.bw \
    --scaleFactorsMethod readCount
```

**How it works:** If sample1 has 100M reads and sample2 has 50M reads, sample2 is scaled by 2× before comparison.

---

## Normalization Method Selection Guide

### For ChIP-seq Coverage Tracks

**Recommended:** RPGC or CPM

```bash
bamCoverage --bam chip.bam --outFileName chip.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --extendReads 200 \
    --ignoreDuplicates
```

**Reasoning:** Accounts for sequencing depth differences; RPGC provides interpretable coverage values.

---

### For ChIP-seq Comparisons (Treatment vs Control)

**Recommended:** log2 ratio with readCount or SES scaling

```bash
bamCompare -b1 chip.bam -b2 input.bam -o ratio.bw \
    --operation log2 \
    --scaleFactorsMethod readCount \
    --extendReads 200 \
    --ignoreDuplicates
```

**Reasoning:** Log2 ratio shows enrichment (positive) and depletion (negative); readCount adjusts for depth.

---

### For RNA-seq Coverage Tracks

**Recommended:** CPM or RPKM

```bash
# Strand-specific forward
bamCoverage --bam rnaseq.bam --outFileName forward.bw \
    --normalizeUsing CPM \
    --filterRNAstrand forward

# For gene-level: RPKM accounts for gene length
bamCoverage --bam rnaseq.bam --outFileName output.bw \
    --normalizeUsing RPKM
```

**Reasoning:** CPM for comparing fixed-width bins; RPKM for genes (accounts for length).

---

### For ATAC-seq

**Recommended:** RPGC or CPM

```bash
bamCoverage --bam atac_shifted.bam --outFileName atac.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398
```

**Reasoning:** Similar to ChIP-seq; want comparable coverage across samples.

---

### For Sample Correlation Analysis

**Recommended:** CPM or RPGC

```bash
multiBamSummary bins \
    --bamfiles sample1.bam sample2.bam sample3.bam \
    -o readCounts.npz

plotCorrelation -in readCounts.npz \
    --corMethod pearson \
    --whatToShow heatmap \
    -o correlation.png
```

**Note:** `multiBamSummary` doesn't explicitly normalize, but correlation analysis is robust to scaling. For very different library sizes, consider normalizing BAM files first or using CPM-normalized bigWig files with `multiBigwigSummary`.

---

## Advanced Normalization Considerations

### Spike-in Normalization

For experiments with spike-in controls (e.g., *Drosophila* chromatin spike-in for ChIP-seq):

1. Calculate scaling factors from spike-in reads
2. Apply custom scaling factors using `--scaleFactor` parameter

```bash
# Calculate spike-in factor (example: 0.8)
SCALE_FACTOR=0.8

bamCoverage --bam chip.bam --outFileName chip_spikenorm.bw \
    --scaleFactor ${SCALE_FACTOR} \
    --extendReads 200
```

---

### Manual Scaling Factors

You can apply custom scaling factors:

```bash
# Apply 2× scaling
bamCoverage --bam input.bam --outFileName output.bw \
    --scaleFactor 2.0
```

---

### Chromosome Exclusion

Exclude specific chromosomes from normalization calculations:

```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --ignoreForNormalization chrX chrY chrM
```

**When to use:** Sex chromosomes in mixed-sex samples, mitochondrial DNA, or chromosomes with unusual coverage.

### Exact Scaling

By default, deepTools can sample reads to estimate scaling factors after filtering. Use `--exactScaling` when rare filtered regions are expected to make sampling inaccurate.

```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --exactScaling
```

**Tradeoff:** More accurate scaling for unusual filtering patterns, but slower because all reads are processed for scaling.

---

## Common Pitfalls

### 1. Using RPKM for bin-based data
**Problem:** RPKM accounts for region length, but all bins are the same size
**Solution:** Use CPM or RPGC instead

### 2. Comparing unnormalized samples
**Problem:** Sample with 2× sequencing depth appears to have 2× signal
**Solution:** Always normalize when comparing samples

### 3. Wrong effective genome size
**Problem:** Using hg19 genome size for hg38 data
**Solution:** Double-check genome assembly and use correct size

### 4. Ignoring duplicates after GC correction
**Problem:** Can introduce bias
**Solution:** Never use `--ignoreDuplicates` after `correctGCBias`

### 5. Using RPGC without effective genome size
**Problem:** Command fails
**Solution:** Always specify `--effectiveGenomeSize` with RPGC

---

## Normalization for Different Comparisons

### Within-sample comparisons (different regions)
**Use:** RPKM (accounts for region length)

### Between-sample comparisons (same regions)
**Use:** CPM, RPGC, or BPM (accounts for library size)

### Treatment vs Control
**Use:** bamCompare with log2 ratio and readCount/SES scaling

### Multiple samples correlation
**Use:** CPM or RPGC normalized bigWig files, then multiBigwigSummary

---

## Quick Reference Table

| Method | Accounts for Depth | Accounts for Length | Best For | Command |
|--------|-------------------|---------------------|----------|---------|
| RPKM | ✓ | ✓ | RNA-seq genes | `--normalizeUsing RPKM` |
| CPM | ✓ | ✗ | Fixed-size bins | `--normalizeUsing CPM` |
| BPM | ✓ | ✗ | Specific regions | `--normalizeUsing BPM` |
| RPGC | ✓ | ✗ | Interpretable coverage | `--normalizeUsing RPGC --effectiveGenomeSize X` |
| None | ✗ | ✗ | Raw data | `--normalizeUsing None` |
| SES | ✓ | ✗ | ChIP comparisons | `bamCompare --scaleFactorsMethod SES` |
| readCount | ✓ | ✗ | ChIP comparisons | `bamCompare --scaleFactorsMethod readCount` |

---

## Further Reading

For more details on normalization theory and best practices:
- deepTools documentation: https://deeptools.readthedocs.io/
- ENCODE guidelines for ChIP-seq analysis
- RNA-seq normalization papers (DESeq2, TMM methods)

### `references/tools_reference.md`

# deepTools Complete Tool Reference

This document provides a comprehensive reference for all deepTools command-line utilities organized by category.

## BAM and bigWig File Processing Tools

### multiBamSummary

Computes read coverages for genomic regions across multiple BAM files, outputting compressed numpy arrays for downstream correlation and PCA analysis.

**Modes:**
- **bins**: Genome-wide analysis using consecutive equal-sized windows (default 10kb)
- **BED-file**: Restricts analysis to user-specified genomic regions

**Key Parameters:**
- `--bamfiles, -b`: Indexed BAM files (space-separated, required)
- `--outFileName, -o`: Output coverage matrix file (required)
- `--BED`: Region specification file (BED-file mode only)
- `--binSize`: Window size in bases (default: 10,000)
- `--labels`: Custom sample identifiers
- `--minMappingQuality`: Quality threshold for read inclusion
- `--numberOfProcessors, -p`: Parallel processing cores
- `--extendReads`: Fragment size extension
- `--ignoreDuplicates`: Remove PCR duplicates
- `--outRawCounts`: Export tab-delimited file with coordinate columns and per-sample counts

**Output:** Compressed numpy array (.npz) for plotCorrelation and plotPCA

**Common Usage:**
```bash
# Genome-wide comparison
multiBamSummary bins --bamfiles sample1.bam sample2.bam -o results.npz

# Peak region comparison
multiBamSummary BED-file --BED peaks.bed --bamfiles sample1.bam sample2.bam -o results.npz
```

---

### multiBigwigSummary

Similar to multiBamSummary but operates on bigWig files instead of BAM files. Used for comparing coverage tracks across samples.

**Modes:**
- **bins**: Genome-wide analysis
- **BED-file**: Region-specific analysis

**Key Parameters:** Similar to multiBamSummary but accepts bigWig files

---

### bamCoverage

Converts BAM alignment files into normalized coverage tracks in bigWig or bedGraph formats. Calculates coverage as number of reads per bin.

**Key Parameters:**
- `--bam, -b`: Input BAM file (required)
- `--outFileName, -o`: Output filename (required)
- `--outFileFormat, -of`: Output type (bigwig or bedgraph)
- `--normalizeUsing`: Normalization method
  - **RPKM**: Reads Per Kilobase per Million mapped reads
  - **CPM**: Counts Per Million mapped reads
  - **BPM**: Bins Per Million mapped reads
  - **RPGC**: Reads per genomic content (requires --effectiveGenomeSize)
  - **None**: No normalization (default)
- `--effectiveGenomeSize`: Mappable genome size (required for RPGC)
- `--binSize`: Resolution in base pairs (default: 50)
- `--extendReads, -e`: Extend reads to fragment length (recommended for ChIP-seq, NOT for RNA-seq)
- `--centerReads`: Center reads at fragment length for sharper signals
- `--ignoreDuplicates`: Count identical reads only once
- `--minMappingQuality`: Filter reads below quality threshold
- `--minFragmentLength / --maxFragmentLength`: Fragment length filtering
- `--smoothLength`: Window averaging for noise reduction
- `--MNase`: Analyze MNase-seq data for nucleosome positioning
- `--Offset`: Position-specific offsets (useful for RiboSeq, GROseq)
- `--filterRNAstrand`: Separate forward/reverse strand reads
- `--ignoreForNormalization`: Exclude chromosomes from normalization (e.g., sex chromosomes)
- `--exactScaling`: Process all reads when sampling-based scaling may be inaccurate
- `--numberOfProcessors, -p`: Parallel processing

**Important Notes:**
- For RNA-seq: Do NOT use --extendReads (would extend over splice junctions)
- `--filterRNAstrand` assumes common dUTP/NSR/NNSR reverse-stranded libraries; verify library orientation before interpreting forward/reverse tracks
- For ChIP-seq: Use --extendReads with smaller bin sizes
- Never apply --ignoreDuplicates after GC bias correction

**Common Usage:**
```bash
# Basic coverage with RPKM normalization
bamCoverage --bam input.bam --outFileName coverage.bw --normalizeUsing RPKM

# ChIP-seq with extension
bamCoverage --bam chip.bam --outFileName chip_coverage.bw \
    --binSize 10 --extendReads 200 --ignoreDuplicates

# Strand-specific RNA-seq
bamCoverage --bam rnaseq.bam --outFileName forward.bw \
    --filterRNAstrand forward
```

---

### bamCompare

Compares two BAM files by generating bigWig or bedGraph files, normalizing for sequencing depth differences. Processes genome in equal-sized bins and performs per-bin calculations.

**Comparison Methods:**
- **log2** (default): Log2 ratio of samples
- **ratio**: Direct ratio calculation
- **subtract**: Difference between files
- **add**: Sum of samples
- **mean**: Average across samples
- **reciprocal_ratio**: Negative inverse for ratios < 0
- **first/second**: Output scaled signal from single file

**Normalization Methods:**
- **readCount** (default): Compensates for sequencing depth
- **SES**: Selective enrichment statistics
- **RPKM**: Reads per kilobase per million
- **CPM**: Counts per million
- **BPM**: Bins per million
- **RPGC**: Reads per genomic content (requires --effectiveGenomeSize)

**Key Parameters:**
- `--bamfile1, -b1`: First BAM file (required)
- `--bamfile2, -b2`: Second BAM file (required)
- `--outFileName, -o`: Output filename (required)
- `--outFileFormat`: bigwig or bedgraph
- `--operation`: Comparison method (see above)
- `--scaleFactorsMethod`: Normalization method (see above)
- `--binSize`: Bin width for output (default: 50bp)
- `--pseudocount`: Avoid division by zero (default: 1)
- `--extendReads`: Extend reads to fragment length
- `--ignoreDuplicates`: Count identical reads once
- `--minMappingQuality`: Quality threshold
- `--numberOfProcessors, -p`: Parallelization

**Common Usage:**
```bash
# Log2 ratio of treatment vs control
bamCompare -b1 treatment.bam -b2 control.bam -o log2ratio.bw

# Subtract control from treatment
bamCompare -b1 treatment.bam -b2 control.bam -o difference.bw \
    --operation subtract --scaleFactorsMethod readCount
```

---

### correctGCBias / computeGCBias

**computeGCBias:** Identifies GC-content bias from sequencing and PCR amplification.

**correctGCBias:** Corrects BAM files for GC bias detected by computeGCBias.

**Key Parameters (computeGCBias):**
- `--bamfile, -b`: Input BAM file
- `--effectiveGenomeSize`: Mappable genome size
- `--genome, -g`: Reference genome in 2bit format
- `--fragmentLength, -l`: Fragment length (for single-end)
- `--biasPlot`: Output diagnostic plot

**Key Parameters (correctGCBias):**
- `--bamfile, -b`: Input BAM file
- `--effectiveGenomeSize`: Mappable genome size
- `--genome, -g`: Reference genome in 2bit format
- `--GCbiasFrequenciesFile`: Frequencies from computeGCBias
- `--correctedFile, -o`: Output corrected BAM

**Important:** Never use --ignoreDuplicates after GC bias correction

---

### alignmentSieve

Filters BAM files by various quality metrics on-the-fly. Useful for creating filtered BAM files for specific analyses.

**Key Parameters:**
- `--bam, -b`: Input BAM file
- `--outFile, -o`: Output BAM file
- `--minMappingQuality`: Minimum mapping quality
- `--ignoreDuplicates`: Remove duplicates
- `--minFragmentLength / --maxFragmentLength`: Fragment length filters
- `--samFlagInclude / --samFlagExclude`: SAM flag filtering
- `--shift`: Shift reads (e.g., for ATACseq Tn5 correction)
- `--ATACshift`: Automatically shift for ATAC-seq data; equivalent to `--shift 4 -5 5 -4`
- `--BED`: Write BEDPE output instead of BAM/CRAM
- `--filterMetrics`: Save counts before/after filtering

**Important Notes:**
- `--shift` and `--ATACshift` use only properly paired reads.
- Adjust effective genome size if blacklisted regions are excluded before RPGC normalization.

---

### computeMatrix

Calculates scores per genomic region and prepares matrices for plotHeatmap and plotProfile. Processes bigWig score files and BED/GTF region files.

**Modes:**
- **reference-point**: Signal distribution relative to specific position (TSS, TES, or center)
- **scale-regions**: Signal across regions standardized to uniform lengths

**Key Parameters:**
- `-R`: Region file(s) in BED/GTF format (required)
- `-S`: BigWig score file(s) (required)
- `-o`: Output matrix file (required)
- `-b`: Upstream distance from reference point
- `-a`: Downstream distance from reference point
- `-m`: Region body length (scale-regions only)
- `-bs, --binSize`: Bin size for averaging scores
- `--skipZeros`: Skip regions with all zeros
- `--minThreshold / --maxThreshold`: Filter by signal intensity
- `--sortRegions`: ascend, descend, keep, no
- `--sortUsing`: mean, median, max, min, sum, region_length
- `--sortUsingSamples`: Limit sorting to selected sample columns
- `-p, --numberOfProcessors`: Parallel processing
- `--averageTypeBins`: Statistical method (mean, median, min, max, sum, std)

**Output Options:**
- `--outFileNameMatrix`: Export tab-delimited data
- `--outFileSortedRegions`: Save filtered/sorted BED file

**Important Notes:**
- Use `--sortRegions keep` if output order must match the input BED/GTF order.
- Matrices from deepTools 3.x include labels and are not backward compatible with pre-3.0 plotting tools.

**Common Usage:**
```bash
# TSS analysis
computeMatrix reference-point -S signal.bw -R genes.bed \
    -o matrix.gz -b 2000 -a 2000 --referencePoint TSS

# Scaled gene body
computeMatrix scale-regions -S signal.bw -R genes.bed \
    -o matrix.gz -b 1000 -a 1000 -m 3000
```

---

## Quality Control Tools

### plotFingerprint

Quality control tool primarily for ChIP-seq experiments. Assesses whether antibody enrichment was successful. Generates cumulative read coverage profiles to distinguish signal from noise.

**Key Parameters:**
- `--bamfiles, -b`: Indexed BAM files (required)
- `--plotFile, -plot, -o`: Output image filename (required)
- `--extendReads, -e`: Extend reads to fragment length
- `--ignoreDuplicates`: Count identical reads once
- `--minMappingQuality`: Mapping quality filter
- `--centerReads`: Center reads at fragment length
- `--minFragmentLength / --maxFragmentLength`: Fragment filters
- `--outRawCounts`: Save per-bin read counts
- `--outQualityMetrics`: Output QC metrics (Jensen-Shannon distance)
- `--labels`: Custom sample names
- `--numberOfProcessors, -p`: Parallel processing

**Interpretation:**
- Ideal control: Straight diagonal line
- Strong ChIP: Steep rise towards highest rank (concentrated reads in few bins)
- Weak enrichment: Flatter curve approaching diagonal

**Common Usage:**
```bash
plotFingerprint -b input.bam chip1.bam chip2.bam \
    --labels Input ChIP1 ChIP2 -o fingerprint.png \
    --extendReads 200 --ignoreDuplicates
```

---

### plotCoverage

Visualizes average read distribution across the genome. Shows genome coverage and helps determine if sequencing depth is adequate.

**Key Parameters:**
- `--bamfiles, -b`: BAM files to analyze (required)
- `--plotFile, -o`: Output plot filename (required)
- `--ignoreDuplicates`: Remove PCR duplicates
- `--minMappingQuality`: Quality threshold
- `--outRawCounts`: Save underlying data
- `--labels`: Sample names
- `--numberOfSamples`: Number of positions to sample (default: 1,000,000)

---

### bamPEFragmentSize

Determines fragment length distribution for paired-end sequencing data. Essential QC to verify expected fragment sizes from library preparation.

**Key Parameters:**
- `--bamfiles, -b`: BAM files (required)
- `--histogram, -hist`: Output histogram filename (required)
- `--plotTitle, -T`: Plot title
- `--maxFragmentLength`: Maximum length to consider (default: 1000)
- `--logScale`: Use logarithmic Y-axis
- `--outRawFragmentLengths`: Save raw fragment lengths

---

### plotCorrelation

Analyzes sample correlations from multiBamSummary or multiBigwigSummary outputs. Shows how similar different samples are.

**Correlation Methods:**
- **Pearson**: Measures metric differences; sensitive to outliers; appropriate for normally distributed data
- **Spearman**: Rank-based; less influenced by outliers; better for non-normal distributions

**Visualization Options:**
- **heatmap**: Color intensity with hierarchical clustering (complete linkage)
- **scatterplot**: Pairwise scatter plots with correlation coefficients

**Key Parameters:**
- `--corData, -in`: Input matrix from multiBamSummary/multiBigwigSummary (required)
- `--corMethod`: pearson or spearman (required)
- `--whatToShow`: heatmap or scatterplot (required)
- `--plotFile, -o`: Output filename (required)
- `--skipZeros`: Exclude zero-value regions
- `--removeOutliers`: Use median absolute deviation (MAD) filtering
- `--outFileCorMatrix`: Export correlation matrix
- `--labels`: Custom sample names
- `--plotTitle`: Plot title
- `--colorMap`: Color scheme (50+ options)
- `--plotNumbers`: Display correlation values on heatmap

**Common Usage:**
```bash
# Heatmap with Pearson correlation
plotCorrelation -in readCounts.npz --corMethod pearson \
    --whatToShow heatmap -o correlation_heatmap.png --plotNumbers

# Scatterplot with Spearman correlation
plotCorrelation -in readCounts.npz --corMethod spearman \
    --whatToShow scatterplot -o correlation_scatter.png
```

---

### plotPCA

Generates principal component analysis plots from multiBamSummary or multiBigwigSummary output. Displays sample relationships in reduced dimensionality.

**Key Parameters:**
- `--corData, -in`: Coverage file from multiBamSummary/multiBigwigSummary (required)
- `--plotFile, -o`: Output image (png, eps, pdf, svg) (required)
- `--outFileNameData`: Export PCA data (loadings/rotation and eigenvalues)
- `--labels, -l`: Custom sample labels
- `--plotTitle, -T`: Plot title
- `--plotHeight / --plotWidth`: Dimensions in centimeters
- `--colors`: Custom symbol colors
- `--markers`: Symbol shapes
- `--transpose`: Perform PCA on transposed matrix (rows=samples)
- `--ntop`: Use top N variable rows (default: 1000)
- `--PCs`: Components to plot (default: 1 2)
- `--log2`: Log2-transform data before analysis
- `--rowCenter`: Center each row at 0

**Common Usage:**
```bash
plotPCA -in readCounts.npz -o PCA_plot.png \
    -T "PCA of read counts" --transpose
```

---

## Visualization Tools

### plotHeatmap

Creates genomic region heatmaps from computeMatrix output. Generates publication-quality visualizations.

**Key Parameters:**
- `--matrixFile, -m`: Matrix from computeMatrix (required)
- `--outFileName, -o`: Output image (png, eps, pdf, svg) (required)
- `--outFileSortedRegions`: Save regions after filtering
- `--outFileNameMatrix`: Export matrix values
- `--interpolationMethod`: auto, nearest, bilinear, bicubic, gaussian
  - Default: nearest (≤1000 columns), bilinear (>1000 columns)
- `--dpi`: Figure resolution

**Clustering:**
- `--kmeans`: k-means clustering
- `--hclust`: Hierarchical clustering (slower for >1000 regions)
- `--silhouette`: Calculate cluster quality metrics

**Visual Customization:**
- `--heatmapHeight / --heatmapWidth`: Dimensions (3-100 cm)
- `--whatToShow`: plot, heatmap, colorbar (combinations)
- `--alpha`: Transparency (0-1)
- `--colorMap`: 50+ color schemes
- `--colorList`: Custom gradient colors
- `--zMin / --zMax`: Intensity scale limits
- `--boxAroundHeatmaps`: yes/no (default: yes)

**Labels:**
- `--xAxisLabel / --yAxisLabel`: Axis labels
- `--regionsLabel`: Region set identifiers
- `--samplesLabel`: Sample names
- `--refPointLabel`: Reference point label
- `--startLabel / --endLabel`: Region boundary labels

**Common Usage:**
```bash
# Basic heatmap
plotHeatmap -m matrix.gz -o heatmap.png

# With clustering and custom colors
plotHeatmap -m matrix.gz -o heatmap.png \
    --kmeans 3 --colorMap RdBu --zMin -3 --zMax 3
```

---

### plotProfile

Generates profile plots showing scores across genomic regions using computeMatrix output.

**Key Parameters:**
- `--matrixFile, -m`: Matrix from computeMatrix (required)
- `--outFileName, -o`: Output image (png, eps, pdf, svg) (required)
- `--plotType`: lines, fill, se, std, overlapped_lines, heatmap
- `--colors`: Color palette (names or hex codes)
- `--plotHeight / --plotWidth`: Dimensions in centimeters
- `--yMin / --yMax`: Y-axis range
- `--averageType`: mean, median, min, max, std, sum

**Clustering:**
- `--kmeans`: k-means clustering
- `--hclust`: Hierarchical clustering
- `--silhouette`: Cluster quality metrics

**Labels:**
- `--plotTitle`: Main heading
- `--regionsLabel`: Region set identifiers
- `--samplesLabel`: Sample names
- `--startLabel / --endLabel`: Region boundary labels (scale-regions mode)

**Output Options:**
- `--outFileNameData`: Export data as tab-separated values
- `--outFileSortedRegions`: Save filtered/sorted regions as BED

**Common Usage:**
```bash
# Line plot
plotProfile -m matrix.gz -o profile.png --plotType lines

# With standard error shading
plotProfile -m matrix.gz -o profile.png --plotType se \
    --colors blue red green
```

---

### plotEnrichment

Calculates and visualizes signal enrichment across genomic regions. Measures percentage of alignments overlapping region groups. Useful for FRiP (Fragment in Peaks) scores.

**Key Parameters:**
- `--bamfiles, -b`: Indexed BAM files (required)
- `--BED`: Region files in BED/GTF format (required)
- `--plotFile, -o`: Output visualization (png, pdf, eps, svg)
- `--labels, -l`: Custom sample identifiers
- `--outRawCounts`: Export numerical data
- `--perSample`: Group by sample instead of feature (default)
- `--regionLabels`: Custom region names

**Read Processing:**
- `--minFragmentLength / --maxFragmentLength`: Fragment filters
- `--minMappingQuality`: Quality threshold
- `--samFlagInclude / --samFlagExclude`: SAM flag filters
- `--ignoreDuplicates`: Remove duplicates
- `--centerReads`: Center reads for sharper signal

**Common Usage:**
```bash
plotEnrichment -b Input.bam H3K4me3.bam \
    --BED peaks_up.bed peaks_down.bed \
    --regionLabels "Up regulated" "Down regulated" \
    -o enrichment.png
```

---

## Miscellaneous Tools

### bigwigAverage

Averages multiple bigWig tracks by partitioning the genome into equal-sized bins, optionally applying scale factors before averaging.

**Key Parameters:**
- `--bigwigs, -b`: Input bigWig files
- `--outFileName, -o`: Output file name
- `--outFileFormat, -of`: bigwig or bedgraph
- `--scaleFactors`: Colon-separated scale factors, such as `0.7:1`
- `--skipNonCoveredRegions, --skipNAs`: Skip missing regions instead of treating them as zero
- `--binSize, -bs`: Bin size for averaging
- `--region, -r`: Limit processing to a test region
- `--blackListFileName, -bl`: Exclude blacklisted regions
- `--numberOfProcessors, -p`: Parallel processing

**Common Usage:**
```bash
bigwigAverage -b rep1.bw rep2.bw -o average.bw \
    --scaleFactors 1:0.9 --binSize 50
```

---

### computeMatrixOperations

Advanced matrix manipulation tool for combining or subsetting matrices from computeMatrix. Enables complex multi-sample, multi-region analyses.

**Operations:**
- `cbind`: Combine matrices column-wise
- `rbind`: Combine matrices row-wise
- `subset`: Extract specific samples or regions
- `filterStrand`: Keep only regions on specific strand
- `filterValues`: Apply signal intensity filters
- `sort`: Order regions by various criteria
- `dataRange`: Report min/max values

**Common Usage:**
```bash
# Combine matrices
computeMatrixOperations cbind -m matrix1.gz matrix2.gz -o combined.gz

# Extract specific samples
computeMatrixOperations subset -m matrix.gz --samples 0 2 -o subset.gz
```

---

### estimateReadFiltering

Predicts the impact of various filtering parameters without actually filtering. Helps optimize filtering strategies before running full analyses.

**Key Parameters:**
- `--bamfiles, -b`: BAM files to analyze
- `--sampleSize`: Number of reads to sample (default: 100,000)
- `--binSize`: Bin size for analysis
- `--distanceBetweenBins`: Spacing between sampled bins

**Filtration Options to Test:**
- `--minMappingQuality`: Test quality thresholds
- `--ignoreDuplicates`: Assess duplicate impact
- `--minFragmentLength / --maxFragmentLength`: Test fragment filters

---

## Common Parameters Across Tools

Many deepTools commands share these filtering and performance options:

**Read Filtering:**
- `--ignoreDuplicates`: Remove PCR duplicates
- `--minMappingQuality`: Filter by alignment confidence
- `--samFlagInclude / --samFlagExclude`: SAM format filtering
- `--minFragmentLength / --maxFragmentLength`: Fragment length bounds

**Performance:**
- `--numberOfProcessors, -p`: Enable parallel processing
- `--region`: Process specific genomic regions (chr:start-end)

**Read Processing:**
- `--extendReads`: Extend to fragment length
- `--centerReads`: Center at fragment midpoint
- `--ignoreDuplicates`: Count unique reads only

### `references/workflows.md`

# deepTools Common Workflows

This document provides complete workflow examples for common deepTools analyses.

## ChIP-seq Quality Control Workflow

Complete quality control assessment for ChIP-seq experiments.

### Step 1: Initial Correlation Assessment

Compare replicates and samples to verify experimental quality:

```bash
# Generate coverage matrix across genome
multiBamSummary bins \
    --bamfiles Input1.bam Input2.bam ChIP1.bam ChIP2.bam \
    --labels Input_rep1 Input_rep2 ChIP_rep1 ChIP_rep2 \
    -o readCounts.npz \
    --numberOfProcessors 8

# Create correlation heatmap
plotCorrelation \
    -in readCounts.npz \
    --corMethod pearson \
    --whatToShow heatmap \
    --plotFile correlation_heatmap.png \
    --plotNumbers

# Generate PCA plot
plotPCA \
    -in readCounts.npz \
    -o PCA_plot.png \
    -T "PCA of ChIP-seq samples"
```

**Expected Results:**
- Replicates should cluster together
- Input samples should be distinct from ChIP samples

---

### Step 2: Coverage and Depth Assessment

```bash
# Check sequencing depth and coverage
plotCoverage \
    --bamfiles Input1.bam ChIP1.bam ChIP2.bam \
    --labels Input ChIP_rep1 ChIP_rep2 \
    --plotFile coverage.png \
    --ignoreDuplicates \
    --numberOfProcessors 8
```

**Interpretation:** Assess whether sequencing depth is adequate for downstream analysis.

---

### Step 3: Fragment Size Validation (Paired-end)

```bash
# Verify expected fragment sizes
bamPEFragmentSize \
    --bamfiles Input1.bam ChIP1.bam ChIP2.bam \
    --histogram fragmentSizes.png \
    --plotTitle "Fragment Size Distribution"
```

**Expected Results:** Fragment sizes should match library preparation protocols (typically 200-600bp for ChIP-seq).

---

### Step 4: GC Bias Detection and Correction

```bash
# Compute GC bias
computeGCBias \
    --bamfile ChIP1.bam \
    --effectiveGenomeSize 2913022398 \
    --genome genome.2bit \
    --fragmentLength 200 \
    --biasPlot GCbias.png \
    --frequenciesFile freq.txt

# If bias detected, correct it
correctGCBias \
    --bamfile ChIP1.bam \
    --effectiveGenomeSize 2913022398 \
    --genome genome.2bit \
    --GCbiasFrequenciesFile freq.txt \
    --correctedFile ChIP1_GCcorrected.bam
```

**Note:** Only correct if significant bias is observed. Do NOT use `--ignoreDuplicates` with GC-corrected files.

---

### Step 5: ChIP Signal Strength Assessment

```bash
# Evaluate ChIP enrichment quality
plotFingerprint \
    --bamfiles Input1.bam ChIP1.bam ChIP2.bam \
    --labels Input ChIP_rep1 ChIP_rep2 \
    --plotFile fingerprint.png \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8 \
    --outQualityMetrics fingerprint_metrics.txt
```

**Interpretation:**
- Strong ChIP: Steep rise in cumulative curve
- Weak enrichment: Curve close to diagonal (input-like)

---

## ChIP-seq Analysis Workflow

Complete workflow from BAM files to publication-quality visualizations.

### Step 1: Generate Normalized Coverage Tracks

```bash
# Input control
bamCoverage \
    --bam Input.bam \
    --outFileName Input_coverage.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --binSize 10 \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8

# ChIP sample
bamCoverage \
    --bam ChIP.bam \
    --outFileName ChIP_coverage.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --binSize 10 \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8
```

---

### Step 2: Create Log2 Ratio Track

```bash
# Compare ChIP to Input
bamCompare \
    --bamfile1 ChIP.bam \
    --bamfile2 Input.bam \
    --outFileName ChIP_vs_Input_log2ratio.bw \
    --operation log2 \
    --scaleFactorsMethod readCount \
    --binSize 10 \
    --extendReads 200 \
    --ignoreDuplicates \
    --numberOfProcessors 8
```

**Result:** Log2 ratio track showing enrichment (positive values) and depletion (negative values).

---

### Step 3: Compute Matrix Around TSS

```bash
# Prepare data for heatmap/profile around transcription start sites
computeMatrix reference-point \
    --referencePoint TSS \
    --scoreFileName ChIP_coverage.bw \
    --regionsFileName genes.bed \
    --beforeRegionStartLength 3000 \
    --afterRegionStartLength 3000 \
    --binSize 10 \
    --sortRegions descend \
    --sortUsing mean \
    --outFileName matrix_TSS.gz \
    --outFileNameMatrix matrix_TSS.tab \
    --numberOfProcessors 8
```

---

### Step 4: Generate Heatmap

```bash
# Create heatmap around TSS
plotHeatmap \
    --matrixFile matrix_TSS.gz \
    --outFileName heatmap_TSS.png \
    --colorMap RdBu \
    --whatToShow 'plot, heatmap and colorbar' \
    --zMin -3 --zMax 3 \
    --yAxisLabel "Genes" \
    --xAxisLabel "Distance from TSS (bp)" \
    --refPointLabel "TSS" \
    --heatmapHeight 15 \
    --kmeans 3
```

---

### Step 5: Generate Profile Plot

```bash
# Create meta-profile around TSS
plotProfile \
    --matrixFile matrix_TSS.gz \
    --outFileName profile_TSS.png \
    --plotType lines \
    --perGroup \
    --colors blue \
    --plotTitle "ChIP-seq signal around TSS" \
    --yAxisLabel "Average signal" \
    --xAxisLabel "Distance from TSS (bp)" \
    --refPointLabel "TSS"
```

---

### Step 6: Enrichment at Peaks

```bash
# Calculate enrichment in peak regions
plotEnrichment \
    --bamfiles Input.bam ChIP.bam \
    --BED peaks.bed \
    --labels Input ChIP \
    --plotFile enrichment.png \
    --outRawCounts enrichment_counts.tab \
    --extendReads 200 \
    --ignoreDuplicates
```

---

## RNA-seq Coverage Workflow

Generate strand-specific coverage tracks for RNA-seq data.

### Forward Strand

```bash
bamCoverage \
    --bam rnaseq.bam \
    --outFileName forward_coverage.bw \
    --filterRNAstrand forward \
    --normalizeUsing CPM \
    --binSize 1 \
    --numberOfProcessors 8
```

### Reverse Strand

```bash
bamCoverage \
    --bam rnaseq.bam \
    --outFileName reverse_coverage.bw \
    --filterRNAstrand reverse \
    --normalizeUsing CPM \
    --binSize 1 \
    --numberOfProcessors 8
```

**Important:** Do NOT use `--extendReads` for RNA-seq (would extend over splice junctions). `--filterRNAstrand` assumes common dUTP/NSR/NNSR reverse-stranded library prep; for other chemistries, confirm orientation or use SAM flag filters.

---

## Multi-Sample Comparison Workflow

Compare multiple ChIP-seq samples (e.g., different conditions or time points).

### Step 1: Generate Coverage Files

```bash
# For each sample
for sample in Control_ChIP Treated_ChIP; do
    bamCoverage \
        --bam ${sample}.bam \
        --outFileName ${sample}.bw \
        --normalizeUsing RPGC \
        --effectiveGenomeSize 2913022398 \
        --binSize 10 \
        --extendReads 200 \
        --ignoreDuplicates \
        --numberOfProcessors 8
done
```

---

### Step 2: Compute Multi-Sample Matrix

```bash
computeMatrix scale-regions \
    --scoreFileName Control_ChIP.bw Treated_ChIP.bw \
    --regionsFileName genes.bed \
    --beforeRegionStartLength 1000 \
    --afterRegionStartLength 1000 \
    --regionBodyLength 3000 \
    --binSize 10 \
    --sortRegions descend \
    --sortUsing mean \
    --outFileName matrix_multi.gz \
    --numberOfProcessors 8
```

---

### Step 3: Multi-Sample Heatmap

```bash
plotHeatmap \
    --matrixFile matrix_multi.gz \
    --outFileName heatmap_comparison.png \
    --colorMap Blues \
    --whatToShow 'plot, heatmap and colorbar' \
    --samplesLabel Control Treated \
    --yAxisLabel "Genes" \
    --heatmapHeight 15 \
    --kmeans 4
```

---

### Step 4: Multi-Sample Profile

```bash
plotProfile \
    --matrixFile matrix_multi.gz \
    --outFileName profile_comparison.png \
    --plotType lines \
    --perGroup \
    --colors blue red \
    --samplesLabel Control Treated \
    --plotTitle "ChIP-seq signal comparison" \
    --startLabel "TSS" \
    --endLabel "TES"
```

---

## ATAC-seq Workflow

Specialized workflow for ATAC-seq data with Tn5 offset correction.

### Step 1: Shift Reads for Tn5 Correction

```bash
alignmentSieve \
    --bam atacseq.bam \
    --outFile atacseq_shifted.bam \
    --ATACshift \
    --minFragmentLength 38 \
    --maxFragmentLength 2000 \
    --ignoreDuplicates
```

**Note:** `--ATACshift` is equivalent to `--shift 4 -5 5 -4` and uses only properly paired fragments.

---

### Step 2: Generate Coverage Track

```bash
bamCoverage \
    --bam atacseq_shifted.bam \
    --outFileName atacseq_coverage.bw \
    --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 \
    --binSize 1 \
    --numberOfProcessors 8
```

---

### Step 3: Fragment Size Analysis

```bash
bamPEFragmentSize \
    --bamfiles atacseq.bam \
    --histogram fragmentSizes_atac.png \
    --maxFragmentLength 1000
```

**Expected Pattern:** Nucleosome ladder with peaks at ~50bp (nucleosome-free), ~200bp (mono-nucleosome), ~400bp (di-nucleosome).

---

## Peak Region Analysis Workflow

Analyze ChIP-seq signal specifically at peak regions.

### Step 1: Matrix at Peaks

```bash
computeMatrix reference-point \
    --referencePoint center \
    --scoreFileName ChIP_coverage.bw \
    --regionsFileName peaks.bed \
    --beforeRegionStartLength 2000 \
    --afterRegionStartLength 2000 \
    --binSize 10 \
    --outFileName matrix_peaks.gz \
    --numberOfProcessors 8
```

---

### Step 2: Heatmap at Peaks

```bash
plotHeatmap \
    --matrixFile matrix_peaks.gz \
    --outFileName heatmap_peaks.png \
    --colorMap YlOrRd \
    --refPointLabel "Peak Center" \
    --heatmapHeight 15 \
    --sortUsing max
```

---

## Troubleshooting Common Issues

### Issue: Out of Memory
**Solution:** Use `--region` parameter to process chromosomes individually:
```bash
bamCoverage --bam input.bam -o chr1.bw --region chr1
```

### Issue: BAM Index Missing
**Solution:** Index BAM files before running deepTools:
```bash
samtools index input.bam
```

### Issue: Slow Processing
**Solution:** Increase `--numberOfProcessors`:
```bash
# Use 8 cores instead of default
--numberOfProcessors 8
```

### Issue: bigWig Files Too Large
**Solution:** Increase bin size:
```bash
--binSize 50  # or larger (default is 10-50)
```

---

## Performance Tips

1. **Use multiple processors:** Always set `--numberOfProcessors` to available cores
2. **Process regions:** Use `--region` for testing or memory-limited environments
3. **Adjust bin size:** Larger bins = faster processing and smaller files
4. **Pre-filter BAM files:** Use `alignmentSieve` to create filtered BAM files once, then reuse
5. **Use bigWig over bedGraph:** bigWig format is compressed and faster to process

---

## Best Practices

1. **Always check QC first:** Run correlation, coverage, and fingerprint analysis before proceeding
2. **Document parameters:** Save command lines for reproducibility
3. **Use consistent normalization:** Apply same normalization method across samples in a comparison
4. **Verify reference genome match:** Ensure BAM files and region files use same genome build
5. **Check strand orientation:** For RNA-seq, verify correct strand orientation
6. **Test on small regions first:** Use `--region chr1:1-1000000` for testing parameters
7. **Keep intermediate files:** Save matrices for regenerating plots with different settings

### `scripts/validate_files.py`

```python
#!/usr/bin/env python3
"""
deepTools File Validation Script

Validates BAM, bigWig, and BED files for deepTools analysis.
Checks for file existence, proper indexing, and basic format requirements.
"""

import os
import sys
import argparse
from pathlib import Path


def check_file_exists(filepath):
    """Check if file exists and is readable."""
    if not os.path.exists(filepath):
        return False, f"File not found: {filepath}"
    if not os.access(filepath, os.R_OK):
        return False, f"File not readable: {filepath}"
    return True, f"✓ File exists: {filepath}"


def check_bam_index(bam_file):
    """Check if BAM file has an index (.bai or .bam.bai)."""
    bai_file1 = bam_file + ".bai"
    bai_file2 = bam_file.replace(".bam", ".bai")

    if os.path.exists(bai_file1):
        return True, f"✓ BAM index found: {bai_file1}"
    elif os.path.exists(bai_file2):
        return True, f"✓ BAM index found: {bai_file2}"
    else:
        return False, f"✗ BAM index missing for: {bam_file}\n  Run: samtools index {bam_file}"


def check_bigwig_file(bw_file):
    """Basic check for bigWig file."""
    # Check file size (bigWig files should have reasonable size)
    file_size = os.path.getsize(bw_file)
    if file_size < 100:
        return False, f"✗ bigWig file suspiciously small: {bw_file} ({file_size} bytes)"
    return True, f"✓ bigWig file appears valid: {bw_file} ({file_size} bytes)"


def check_bed_file(bed_file):
    """Basic validation of BED file format."""
    try:
        with open(bed_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        if len(lines) == 0:
            return False, f"✗ BED file is empty: {bed_file}"

        # Check first few lines for basic format
        for i, line in enumerate(lines[:10], 1):
            fields = line.split('\t')
            if len(fields) < 3:
                return False, f"✗ BED file format error at line {i}: expected at least 3 columns\n  Line: {line}"

            # Check if start and end are integers
            try:
                start = int(fields[1])
                end = int(fields[2])
                if start >= end:
                    return False, f"✗ BED file error at line {i}: start >= end ({start} >= {end})"
            except ValueError:
                return False, f"✗ BED file format error at line {i}: start and end must be integers\n  Line: {line}"

        return True, f"✓ BED file format appears valid: {bed_file} ({len(lines)} regions)"

    except Exception as e:
        return False, f"✗ Error reading BED file: {bed_file}\n  Error: {str(e)}"


def validate_files(bam_files=None, bigwig_files=None, bed_files=None):
    """
    Validate all provided files.

    Args:
        bam_files: List of BAM file paths
        bigwig_files: List of bigWig file paths
        bed_files: List of BED file paths

    Returns:
        Tuple of (success: bool, messages: list)
    """
    all_success = True
    messages = []

    # Validate BAM files
    if bam_files:
        messages.append("\n=== Validating BAM Files ===")
        for bam_file in bam_files:
            # Check existence
            success, msg = check_file_exists(bam_file)
            messages.append(msg)
            if not success:
                all_success = False
                continue

            # Check index
            success, msg = check_bam_index(bam_file)
            messages.append(msg)
            if not success:
                all_success = False

    # Validate bigWig files
    if bigwig_files:
        messages.append("\n=== Validating bigWig Files ===")
        for bw_file in bigwig_files:
            # Check existence
            success, msg = check_file_exists(bw_file)
            messages.append(msg)
            if not success:
                all_success = False
                continue

            # Basic bigWig check
            success, msg = check_bigwig_file(bw_file)
            messages.append(msg)
            if not success:
                all_success = False

    # Validate BED files
    if bed_files:
        messages.append("\n=== Validating BED Files ===")
        for bed_file in bed_files:
            # Check existence
            success, msg = check_file_exists(bed_file)
            messages.append(msg)
            if not success:
                all_success = False
                continue

            # Check BED format
            success, msg = check_bed_file(bed_file)
            messages.append(msg)
            if not success:
                all_success = False

    return all_success, messages


def main():
    parser = argparse.ArgumentParser(
        description="Validate files for deepTools analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate BAM files
  python validate_files.py --bam sample1.bam sample2.bam

  # Validate all file types
  python validate_files.py --bam input.bam chip.bam --bed peaks.bed --bigwig signal.bw

  # Validate from a directory
  python validate_files.py --bam *.bam --bed *.bed
        """
    )

    parser.add_argument('--bam', nargs='+', help='BAM files to validate')
    parser.add_argument('--bigwig', '--bw', nargs='+', help='bigWig files to validate')
    parser.add_argument('--bed', nargs='+', help='BED files to validate')

    args = parser.parse_args()

    # Check if any files were provided
    if not any([args.bam, args.bigwig, args.bed]):
        parser.print_help()
        sys.exit(1)

    # Run validation
    success, messages = validate_files(
        bam_files=args.bam,
        bigwig_files=args.bigwig,
        bed_files=args.bed
    )

    # Print results
    for msg in messages:
        print(msg)

    # Summary
    print("\n" + "="*50)
    if success:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print("✗ Some validations failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### `scripts/workflow_generator.py`

```python
#!/usr/bin/env python3
"""
deepTools Workflow Generator

Generates bash script templates for common deepTools workflows.
"""

import argparse
import re
import shlex
import sys


SAFE_PATH_PATTERN = re.compile(r"^[A-Za-z0-9._/-]+$")


WORKFLOWS = {
    'chipseq_qc': {
        'name': 'ChIP-seq Quality Control',
        'description': 'Complete QC workflow for ChIP-seq experiments',
    },
    'chipseq_analysis': {
        'name': 'ChIP-seq Complete Analysis',
        'description': 'Full ChIP-seq analysis from BAM to heatmaps',
    },
    'rnaseq_coverage': {
        'name': 'RNA-seq Coverage Tracks',
        'description': 'Generate strand-specific RNA-seq coverage',
    },
    'atacseq': {
        'name': 'ATAC-seq Analysis',
        'description': 'ATAC-seq workflow with Tn5 correction',
    },
}


def sanitize_path(value, default, label):
    """Return a shell-safe path-like value for generated workflow scripts."""
    value = default if value in (None, "") else str(value)
    if not SAFE_PATH_PATTERN.fullmatch(value):
        raise ValueError(
            f"{label} contains unsupported characters. Use letters, numbers, '/', '.', '_' or '-'."
        )
    if any(part == ".." for part in value.split("/")):
        raise ValueError(f"{label} must not contain '..' path segments.")
    return value


def sanitize_path_list(value, default, label):
    """Parse and validate a space-separated list of path-like values."""
    raw_values = default if value in (None, "") else shlex.split(str(value))
    if not raw_values:
        raise ValueError(f"{label} must contain at least one file path.")
    return [sanitize_path(item, item, label) for item in raw_values]


def sanitize_positive_int(value, label):
    """Validate numeric workflow settings before script interpolation."""
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be an integer.") from exc
    if parsed < 1:
        raise ValueError(f"{label} must be >= 1.")
    return parsed


def shell_literal(value):
    """Quote a sanitized value for use in a generated bash assignment."""
    return shlex.quote(str(value))


def shell_array(values):
    """Render sanitized values as a bash array literal."""
    return " ".join(shell_literal(value) for value in values)


def runnable_script_path(output_file):
    """Return a quoted path suitable for the generated run hint."""
    if output_file.startswith("/"):
        return shell_literal(output_file)
    return f"./{shell_literal(output_file)}"


def generate_chipseq_qc_workflow(output_file, params):
    """Generate ChIP-seq QC workflow script."""

    script = f"""#!/bin/bash
set -euo pipefail

# deepTools ChIP-seq Quality Control Workflow
# Generated by deepTools workflow generator

# Configuration
INPUT_BAM={shell_literal(params['input_bam'])}
CHIP_BAM=({shell_array(params['chip_bams'])})
GENOME_SIZE={params.get('genome_size', '2913022398')}
THREADS={params.get('threads', '8')}
OUTPUT_DIR={shell_literal(params['output_dir'])}

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=== Starting ChIP-seq QC workflow ==="

# Step 1: Correlation analysis
echo "Step 1: Computing correlation matrix..."
multiBamSummary bins \\
    --bamfiles "$INPUT_BAM" "${{CHIP_BAM[@]}}" \\
    -o "$OUTPUT_DIR/readCounts.npz" \\
    --numberOfProcessors "$THREADS"

echo "Step 2: Generating correlation heatmap..."
plotCorrelation \\
    -in "$OUTPUT_DIR/readCounts.npz" \\
    --corMethod pearson \\
    --whatToShow heatmap \\
    --plotFile "$OUTPUT_DIR/correlation_heatmap.png" \\
    --plotNumbers

echo "Step 3: Generating PCA plot..."
plotPCA \\
    -in "$OUTPUT_DIR/readCounts.npz" \\
    -o "$OUTPUT_DIR/PCA_plot.png" \\
    -T "PCA of ChIP-seq samples"

# Step 2: Coverage assessment
echo "Step 4: Assessing coverage..."
plotCoverage \\
    --bamfiles "$INPUT_BAM" "${{CHIP_BAM[@]}}" \\
    --plotFile "$OUTPUT_DIR/coverage.png" \\
    --ignoreDuplicates \\
    --numberOfProcessors "$THREADS"

# Step 3: Fragment size (for paired-end data)
echo "Step 5: Analyzing fragment sizes..."
bamPEFragmentSize \\
    --bamfiles "$INPUT_BAM" "${{CHIP_BAM[@]}}" \\
    --histogram "$OUTPUT_DIR/fragmentSizes.png" \\
    --plotTitle "Fragment Size Distribution"

# Step 4: ChIP signal strength
echo "Step 6: Evaluating ChIP enrichment..."
plotFingerprint \\
    --bamfiles "$INPUT_BAM" "${{CHIP_BAM[@]}}" \\
    --plotFile "$OUTPUT_DIR/fingerprint.png" \\
    --extendReads 200 \\
    --ignoreDuplicates \\
    --numberOfProcessors "$THREADS" \\
    --outQualityMetrics "$OUTPUT_DIR/fingerprint_metrics.txt"

echo "=== ChIP-seq QC workflow complete ==="
echo "Results are in: $OUTPUT_DIR"
"""

    with open(output_file, 'w') as f:
        f.write(script)

    return f"✓ Generated ChIP-seq QC workflow: {output_file}"


def generate_chipseq_analysis_workflow(output_file, params):
    """Generate complete ChIP-seq analysis workflow script."""

    script = f"""#!/bin/bash
set -euo pipefail

# deepTools ChIP-seq Complete Analysis Workflow
# Generated by deepTools workflow generator

# Configuration
INPUT_BAM={shell_literal(params['input_bam'])}
CHIP_BAM={shell_literal(params['chip_bam'])}
GENES_BED={shell_literal(params['genes_bed'])}
PEAKS_BED={shell_literal(params['peaks_bed'])}
GENOME_SIZE={params.get('genome_size', '2913022398')}
THREADS={params.get('threads', '8')}
OUTPUT_DIR={shell_literal(params['output_dir'])}

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=== Starting ChIP-seq analysis workflow ==="

# Step 1: Generate normalized coverage tracks
echo "Step 1: Generating coverage tracks..."

bamCoverage \\
    --bam "$INPUT_BAM" \\
    --outFileName "$OUTPUT_DIR/Input_coverage.bw" \\
    --normalizeUsing RPGC \\
    --effectiveGenomeSize "$GENOME_SIZE" \\
    --binSize 10 \\
    --extendReads 200 \\
    --ignoreDuplicates \\
    --numberOfProcessors "$THREADS"

bamCoverage \\
    --bam "$CHIP_BAM" \\
    --outFileName "$OUTPUT_DIR/ChIP_coverage.bw" \\
    --normalizeUsing RPGC \\
    --effectiveGenomeSize "$GENOME_SIZE" \\
    --binSize 10 \\
    --extendReads 200 \\
    --ignoreDuplicates \\
    --numberOfProcessors "$THREADS"

# Step 2: Create log2 ratio track
echo "Step 2: Creating log2 ratio track..."
bamCompare \\
    --bamfile1 "$CHIP_BAM" \\
    --bamfile2 "$INPUT_BAM" \\
    --outFileName "$OUTPUT_DIR/ChIP_vs_Input_log2ratio.bw" \\
    --operation log2 \\
    --scaleFactorsMethod readCount \\
    --binSize 10 \\
    --extendReads 200 \\
    --ignoreDuplicates \\
    --numberOfProcessors "$THREADS"

# Step 3: Compute matrix around TSS
echo "Step 3: Computing matrix around TSS..."
computeMatrix reference-point \\
    --referencePoint TSS \\
    --scoreFileName "$OUTPUT_DIR/ChIP_coverage.bw" \\
    --regionsFileName "$GENES_BED" \\
    --beforeRegionStartLength 3000 \\
    --afterRegionStartLength 3000 \\
    --binSize 10 \\
    --sortRegions descend \\
    --sortUsing mean \\
    --outFileName "$OUTPUT_DIR/matrix_TSS.gz" \\
    --numberOfProcessors "$THREADS"

# Step 4: Generate heatmap
echo "Step 4: Generating heatmap..."
plotHeatmap \\
    --matrixFile "$OUTPUT_DIR/matrix_TSS.gz" \\
    --outFileName "$OUTPUT_DIR/heatmap_TSS.png" \\
    --colorMap RdBu \\
    --whatToShow 'plot, heatmap and colorbar' \\
    --yAxisLabel "Genes" \\
    --xAxisLabel "Distance from TSS (bp)" \\
    --refPointLabel "TSS" \\
    --heatmapHeight 15 \\
    --kmeans 3

# Step 5: Generate profile plot
echo "Step 5: Generating profile plot..."
plotProfile \\
    --matrixFile "$OUTPUT_DIR/matrix_TSS.gz" \\
    --outFileName "$OUTPUT_DIR/profile_TSS.png" \\
    --plotType lines \\
    --perGroup \\
    --colors blue \\
    --plotTitle "ChIP-seq signal around TSS" \\
    --yAxisLabel "Average signal" \\
    --refPointLabel "TSS"

# Step 6: Enrichment at peaks (if peaks provided)
if [ -f "$PEAKS_BED" ]; then
    echo "Step 6: Calculating enrichment at peaks..."
    plotEnrichment \\
        --bamfiles "$INPUT_BAM" "$CHIP_BAM" \\
        --BED "$PEAKS_BED" \\
        --labels Input ChIP \\
        --plotFile "$OUTPUT_DIR/enrichment.png" \\
        --outRawCounts "$OUTPUT_DIR/enrichment_counts.tab" \\
        --extendReads 200 \\
        --ignoreDuplicates
fi

echo "=== ChIP-seq analysis complete ==="
echo "Results are in: $OUTPUT_DIR"
"""

    with open(output_file, 'w') as f:
        f.write(script)

    return f"✓ Generated ChIP-seq analysis workflow: {output_file}"


def generate_rnaseq_coverage_workflow(output_file, params):
    """Generate RNA-seq coverage workflow script."""

    script = f"""#!/bin/bash
set -euo pipefail

# deepTools RNA-seq Coverage Workflow
# Generated by deepTools workflow generator

# Configuration
RNASEQ_BAM={shell_literal(params['rnaseq_bam'])}
THREADS={params.get('threads', '8')}
OUTPUT_DIR={shell_literal(params['output_dir'])}

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=== Starting RNA-seq coverage workflow ==="

# Generate strand-specific coverage tracks
echo "Step 1: Generating forward strand coverage..."
bamCoverage \\
    --bam "$RNASEQ_BAM" \\
    --outFileName "$OUTPUT_DIR/forward_coverage.bw" \\
    --filterRNAstrand forward \\
    --normalizeUsing CPM \\
    --binSize 1 \\
    --numberOfProcessors "$THREADS"

echo "Step 2: Generating reverse strand coverage..."
bamCoverage \\
    --bam "$RNASEQ_BAM" \\
    --outFileName "$OUTPUT_DIR/reverse_coverage.bw" \\
    --filterRNAstrand reverse \\
    --normalizeUsing CPM \\
    --binSize 1 \\
    --numberOfProcessors "$THREADS"

echo "=== RNA-seq coverage workflow complete ==="
echo "Results are in: $OUTPUT_DIR"
echo ""
echo "Note: These bigWig files can be loaded into genome browsers"
echo "for strand-specific visualization of RNA-seq data."
"""

    with open(output_file, 'w') as f:
        f.write(script)

    return f"✓ Generated RNA-seq coverage workflow: {output_file}"


def generate_atacseq_workflow(output_file, params):
    """Generate ATAC-seq workflow script."""

    script = f"""#!/bin/bash
set -euo pipefail

# deepTools ATAC-seq Analysis Workflow
# Generated by deepTools workflow generator

# Configuration
ATAC_BAM={shell_literal(params['atac_bam'])}
PEAKS_BED={shell_literal(params['peaks_bed'])}
GENOME_SIZE={params.get('genome_size', '2913022398')}
THREADS={params.get('threads', '8')}
OUTPUT_DIR={shell_literal(params['output_dir'])}

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=== Starting ATAC-seq analysis workflow ==="

# Step 1: Shift reads for Tn5 correction
echo "Step 1: Applying Tn5 offset correction..."
alignmentSieve \\
    --bam "$ATAC_BAM" \\
    --outFile "$OUTPUT_DIR/atacseq_shifted.bam" \\
    --ATACshift \\
    --minFragmentLength 38 \\
    --maxFragmentLength 2000 \\
    --ignoreDuplicates

# Index the shifted BAM
samtools index "$OUTPUT_DIR/atacseq_shifted.bam"

# Step 2: Generate coverage track
echo "Step 2: Generating coverage track..."
bamCoverage \\
    --bam "$OUTPUT_DIR/atacseq_shifted.bam" \\
    --outFileName "$OUTPUT_DIR/atacseq_coverage.bw" \\
    --normalizeUsing RPGC \\
    --effectiveGenomeSize "$GENOME_SIZE" \\
    --binSize 1 \\
    --numberOfProcessors "$THREADS"

# Step 3: Fragment size analysis
echo "Step 3: Analyzing fragment sizes..."
bamPEFragmentSize \\
    --bamfiles "$ATAC_BAM" \\
    --histogram "$OUTPUT_DIR/fragmentSizes.png" \\
    --maxFragmentLength 1000

# Step 4: Compute matrix at peaks (if peaks provided)
if [ -f "$PEAKS_BED" ]; then
    echo "Step 4: Computing matrix at peaks..."
    computeMatrix reference-point \\
        --referencePoint center \\
        --scoreFileName "$OUTPUT_DIR/atacseq_coverage.bw" \\
        --regionsFileName "$PEAKS_BED" \\
        --beforeRegionStartLength 2000 \\
        --afterRegionStartLength 2000 \\
        --binSize 10 \\
        --outFileName "$OUTPUT_DIR/matrix_peaks.gz" \\
        --numberOfProcessors "$THREADS"

    echo "Step 5: Generating heatmap..."
    plotHeatmap \\
        --matrixFile "$OUTPUT_DIR/matrix_peaks.gz" \\
        --outFileName "$OUTPUT_DIR/heatmap_peaks.png" \\
        --colorMap YlOrRd \\
        --refPointLabel "Peak Center" \\
        --heatmapHeight 15
fi

echo "=== ATAC-seq analysis complete ==="
echo "Results are in: $OUTPUT_DIR"
echo ""
echo "Expected fragment size pattern:"
echo "  ~50bp: nucleosome-free regions"
echo "  ~200bp: mono-nucleosome"
echo "  ~400bp: di-nucleosome"
"""

    with open(output_file, 'w') as f:
        f.write(script)

    return f"✓ Generated ATAC-seq workflow: {output_file}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate deepTools workflow scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available workflows:
{chr(10).join(f"  {key}: {value['name']}" for key, value in WORKFLOWS.items())}

Examples:
  # Generate ChIP-seq QC workflow
  python workflow_generator.py chipseq_qc -o chipseq_qc.sh

  # Generate ChIP-seq analysis with custom parameters
  python workflow_generator.py chipseq_analysis -o analysis.sh \\
      --chip-bam H3K4me3.bam --input-bam Input.bam

  # List all available workflows
  python workflow_generator.py --list
        """
    )

    parser.add_argument('workflow', nargs='?', choices=list(WORKFLOWS.keys()),
                        help='Workflow type to generate')
    parser.add_argument('-o', '--output', default='deeptools_workflow.sh',
                        help='Output script filename (default: deeptools_workflow.sh)')
    parser.add_argument('--list', action='store_true',
                        help='List all available workflows')

    # Common parameters
    parser.add_argument('--threads', type=int, default=8,
                        help='Number of threads (default: 8)')
    parser.add_argument('--genome-size', type=int, default=2913022398,
                        help='Effective genome size (default: 2913022398 for hg38)')
    parser.add_argument('--output-dir', default=None,
                        help='Output directory for results')

    # Workflow-specific parameters
    parser.add_argument('--input-bam', help='Input/control BAM file')
    parser.add_argument('--chip-bam', help='ChIP BAM file')
    parser.add_argument('--chip-bams', help='Multiple ChIP BAM files (space-separated)')
    parser.add_argument('--rnaseq-bam', help='RNA-seq BAM file')
    parser.add_argument('--atac-bam', help='ATAC-seq BAM file')
    parser.add_argument('--genes-bed', help='Genes BED file')
    parser.add_argument('--peaks-bed', help='Peaks BED file')

    args = parser.parse_args()

    # List workflows
    if args.list:
        print("\nAvailable deepTools workflows:\n")
        for key, value in WORKFLOWS.items():
            print(f"  {key}")
            print(f"    {value['name']}")
            print(f"    {value['description']}\n")
        sys.exit(0)

    # Check if workflow was specified
    if not args.workflow:
        parser.print_help()
        sys.exit(1)

    # Prepare parameters. Values are validated before they are interpolated
    # into generated bash so filenames cannot smuggle shell metacharacters.
    try:
        output_file = sanitize_path(args.output, 'deeptools_workflow.sh', 'output script')
        params = {
            'threads': sanitize_positive_int(args.threads, 'threads'),
            'genome_size': sanitize_positive_int(args.genome_size, 'genome size'),
            'output_dir': sanitize_path(args.output_dir, f"{args.workflow}_output", 'output directory'),
            'input_bam': sanitize_path(args.input_bam, 'Input.bam', 'input BAM'),
            'chip_bam': sanitize_path(args.chip_bam, 'ChIP.bam', 'ChIP BAM'),
            'chip_bams': sanitize_path_list(args.chip_bams, ['ChIP1.bam', 'ChIP2.bam'], 'ChIP BAMs'),
            'rnaseq_bam': sanitize_path(args.rnaseq_bam, 'rnaseq.bam', 'RNA-seq BAM'),
            'atac_bam': sanitize_path(args.atac_bam, 'atacseq.bam', 'ATAC-seq BAM'),
            'genes_bed': sanitize_path(args.genes_bed, 'genes.bed', 'genes BED'),
            'peaks_bed': sanitize_path(args.peaks_bed, 'peaks.bed', 'peaks BED'),
        }
    except ValueError as exc:
        parser.error(str(exc))

    # Generate workflow
    if args.workflow == 'chipseq_qc':
        message = generate_chipseq_qc_workflow(output_file, params)
    elif args.workflow == 'chipseq_analysis':
        message = generate_chipseq_analysis_workflow(output_file, params)
    elif args.workflow == 'rnaseq_coverage':
        message = generate_rnaseq_coverage_workflow(output_file, params)
    elif args.workflow == 'atacseq':
        message = generate_atacseq_workflow(output_file, params)

    print(message)
    print(f"\nTo run the workflow:")
    print(f"  chmod +x {shell_literal(output_file)}")
    print(f"  {runnable_script_path(output_file)}")
    print(f"\nNote: Edit the script to customize file paths and parameters.")


if __name__ == "__main__":
    main()
```

### `assets/quick_reference.md`

# deepTools Quick Reference

## Most Common Commands

### BAM to bigWig (normalized)
```bash
bamCoverage --bam input.bam --outFileName output.bw \
    --normalizeUsing RPGC --effectiveGenomeSize 2913022398 \
    --binSize 10 --numberOfProcessors 8
```

### Compare two BAM files
```bash
bamCompare -b1 treatment.bam -b2 control.bam -o ratio.bw \
    --operation log2 --scaleFactorsMethod readCount
```

### Correlation heatmap
```bash
multiBamSummary bins --bamfiles *.bam -o counts.npz
plotCorrelation -in counts.npz --corMethod pearson \
    --whatToShow heatmap -o correlation.png
```

### Heatmap around TSS
```bash
computeMatrix reference-point -S signal.bw -R genes.bed \
    -b 3000 -a 3000 --referencePoint TSS -o matrix.gz

plotHeatmap -m matrix.gz -o heatmap.png
```

### ChIP enrichment check
```bash
plotFingerprint -b input.bam chip.bam -o fingerprint.png \
    --extendReads 200 --ignoreDuplicates
```

## Effective Genome Sizes

| Organism | Assembly | Size |
|----------|----------|------|
| Human | hg38 | 2913022398 |
| Human | T2T/CHM13CAT_v2 | 3117292070 |
| Mouse | mm39 | 2654621783 |
| Mouse | mm10 | 2652783500 |
| Fly | dm6 | 142573017 |

## Common Normalization Methods

- **RPGC**: 1× genome coverage (requires --effectiveGenomeSize)
- **CPM**: Counts per million (for fixed bins)
- **RPKM**: Reads per kb per million (for genes)

## Notes

- `--filterRNAstrand` assumes common dUTP-style reverse-stranded RNA-seq libraries.
- `--ATACshift` uses only properly paired fragments and is equivalent to `--shift 4 -5 5 -4`.

## Typical Workflow

1. **QC**: plotFingerprint, plotCorrelation
2. **Coverage**: bamCoverage with normalization
3. **Comparison**: bamCompare for treatment vs control
4. **Visualization**: computeMatrix → plotHeatmap/plotProfile
