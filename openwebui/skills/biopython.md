---
name: biopython
description: NCBI API key to raise Entrez rate limits.
---

# Biopython: Computational Molecular Biology in Python

## Overview

Biopython is a comprehensive set of freely available Python tools for biological computation. It provides functionality for sequence manipulation, file I/O, database access, structural bioinformatics, phylogenetics, and many other bioinformatics tasks. The current version is **Biopython 1.87** (released 30 March 2026). It supports **Python 3.10-3.14** and PyPy3.10, and requires NumPy. Biopython 1.87 also addresses **CVE-2025-68463** in `Bio.Entrez.Parser` when parsing untrusted files, so prefer 1.87+ for workflows that parse externally supplied Entrez XML.

## When to Use This Skill

Use this skill when:

- Working with biological sequences (DNA, RNA, or protein)
- Reading, writing, or converting biological file formats (FASTA, GenBank, FASTQ, PDB, mmCIF, etc.)
- Accessing NCBI databases (GenBank, PubMed, Protein, Gene, etc.) via Entrez
- Running BLAST searches or parsing BLAST results
- Performing sequence alignments (pairwise or multiple sequence alignments)
- Analyzing protein structures from PDB files
- Creating, manipulating, or visualizing phylogenetic trees
- Finding sequence motifs or analyzing motif patterns
- Calculating sequence statistics (GC content, molecular weight, melting temperature, etc.)
- Performing structural bioinformatics tasks
- Working with population genetics data
- Any other computational molecular biology task

## Core Capabilities

Biopython is organized into modular sub-packages, each addressing specific bioinformatics domains:

1. **Sequence Handling** - Bio.Seq and Bio.SeqIO for sequence manipulation and file I/O
2. **Alignment Analysis** - Bio.Align and Bio.AlignIO for pairwise and multiple sequence alignments
3. **Database Access** - Bio.Entrez for programmatic access to NCBI databases
4. **BLAST Operations** - Bio.Blast for running and parsing BLAST searches
5. **Structural Bioinformatics** - Bio.PDB for working with 3D protein structures
6. **Phylogenetics** - Bio.Phylo for phylogenetic tree manipulation and visualization
7. **Advanced Features** - Motifs, population genetics, sequence utilities, and more

## Installation and Setup

Install the current stable Biopython release with an explicit version pin for reproducibility:

```bash
uv pip install "biopython==1.87"
```

For NCBI database access, always set your email address (required by NCBI). For reusable software, set a stable `Entrez.tool` value and register the tool/email with NCBI. For higher rate limits (10 req/s instead of 3 req/s), read only `NCBI_API_KEY` from the environment — do not hardcode keys or load unrelated environment variables:

```python
import os
from Bio import Entrez

Entrez.email = "your.email@example.com"  # required — use your real email
Entrez.tool = "your_tool_name"  # optional but recommended for reusable software

# Optional: register at https://www.ncbi.nlm.nih.gov/account/settings/
if api_key := os.environ.get("NCBI_API_KEY"):
    Entrez.api_key = api_key
```

## Using This Skill

This skill provides comprehensive documentation organized by functionality area. When working on a task, consult the relevant reference documentation:

### 1. Sequence Handling (Bio.Seq & Bio.SeqIO)

**Reference:** `references/sequence_io.md`

Use for:
- Creating and manipulating biological sequences
- Reading and writing sequence files (FASTA, GenBank, FASTQ, etc.)
- Converting between file formats
- Extracting sequences from large files
- Sequence translation, transcription, and reverse complement
- Working with SeqRecord objects

**Quick example:**
```python
from Bio import SeqIO

# Read sequences from FASTA file
for record in SeqIO.parse("sequences.fasta", "fasta"):
    print(f"{record.id}: {len(record.seq)} bp")

# Convert GenBank to FASTA
SeqIO.convert("input.gb", "genbank", "output.fasta", "fasta")
```

### 2. Alignment Analysis (Bio.Align & Bio.AlignIO)

**Reference:** `references/alignment.md`

Use for:
- Pairwise sequence alignment (global and local)
- Reading and writing multiple sequence alignments
- Using substitution matrices (BLOSUM, PAM)
- Calculating alignment statistics
- Customizing alignment parameters

**Quick example:**
```python
from Bio import Align

# Pairwise alignment
aligner = Align.PairwiseAligner()
aligner.mode = 'global'
alignments = aligner.align("ACCGGT", "ACGGT")
print(alignments[0])
```

### 3. Database Access (Bio.Entrez)

**Reference:** `references/databases.md`

Use for:
- Searching NCBI databases (PubMed, GenBank, Protein, Gene, etc.)
- Downloading sequences and records
- Fetching publication information
- Finding related records across databases
- Batch downloading with proper rate limiting

**Quick example:**
```python
from Bio import Entrez
Entrez.email = "your.email@example.com"

# Search PubMed
handle = Entrez.esearch(db="pubmed", term="biopython", retmax=10)
results = Entrez.read(handle)
handle.close()
print(f"Found {results['Count']} results")
```

### 4. BLAST Operations (Bio.Blast)

**Reference:** `references/blast.md`

Use for:
- Running BLAST searches via NCBI web services
- Running local BLAST searches
- Parsing BLAST XML output
- Filtering results by E-value or identity
- Extracting hit sequences

**Quick example:**
```python
from Bio.Blast import NCBIWWW, NCBIXML

# Run BLAST search
result_handle = NCBIWWW.qblast("blastn", "nt", "ATCGATCGATCG")
blast_record = NCBIXML.read(result_handle)

# Display top hits
for alignment in blast_record.alignments[:5]:
    print(f"{alignment.title}: E-value={alignment.hsps[0].expect}")
```

### 5. Structural Bioinformatics (Bio.PDB)

**Reference:** `references/structure.md`

Use for:
- Parsing PDB and mmCIF structure files
- Navigating protein structure hierarchy (SMCRA: Structure/Model/Chain/Residue/Atom)
- Calculating distances, angles, and dihedrals
- Secondary structure assignment (DSSP)
- Structure superimposition and RMSD calculation
- Extracting sequences from structures

**Quick example:**
```python
from Bio.PDB import PDBParser

# Parse structure
parser = PDBParser(QUIET=True)
structure = parser.get_structure("1crn", "1crn.pdb")

# Calculate distance between alpha carbons
chain = structure[0]["A"]
distance = chain[10]["CA"] - chain[20]["CA"]
print(f"Distance: {distance:.2f} Å")
```

### 6. Phylogenetics (Bio.Phylo)

**Reference:** `references/phylogenetics.md`

Use for:
- Reading and writing phylogenetic trees (Newick, NEXUS, phyloXML)
- Building trees from distance matrices or alignments
- Tree manipulation (pruning, rerooting, ladderizing)
- Calculating phylogenetic distances
- Creating consensus trees
- Visualizing trees

**Quick example:**
```python
from Bio import Phylo

# Read and visualize tree
tree = Phylo.read("tree.nwk", "newick")
Phylo.draw_ascii(tree)

# Calculate distance
distance = tree.distance("Species_A", "Species_B")
print(f"Distance: {distance:.3f}")
```

### 7. Advanced Features

**Reference:** `references/advanced.md`

Use for:
- **Sequence motifs** (Bio.motifs) - Finding and analyzing motif patterns
- **Population genetics** (Bio.PopGen) - GenePop files, Fst calculations, Hardy-Weinberg tests
- **Sequence utilities** (Bio.SeqUtils) - GC content, melting temperature, molecular weight, protein analysis
- **Restriction analysis** (Bio.Restriction) - Finding restriction enzyme sites
- **Clustering** (Bio.Cluster) - K-means and hierarchical clustering
- **Genome diagrams** (GenomeDiagram) - Visualizing genomic features

**Quick example:**
```python
from Bio.SeqUtils import gc_fraction, molecular_weight
from Bio.Seq import Seq

seq = Seq("ATCGATCGATCG")
print(f"GC content: {gc_fraction(seq):.2%}")
print(f"Molecular weight: {molecular_weight(seq, seq_type='DNA'):.2f} g/mol")
```

## General Workflow Guidelines

### Reading Documentation

When a user asks about a specific Biopython task:

1. **Identify the relevant module** based on the task description
2. **Read the appropriate reference file** using the Read tool
3. **Extract relevant code patterns** and adapt them to the user's specific needs
4. **Combine multiple modules** when the task requires it

Example search patterns for reference files:
```bash
# Find information about specific functions
rg -n "SeqIO.parse" references/sequence_io.md

# Find examples of specific tasks
rg -n "BLAST" references/blast.md

# Find information about specific concepts
rg -n "alignment" references/alignment.md
```

### Writing Biopython Code

Follow these principles when writing Biopython code:

1. **Import modules explicitly**
   ```python
   from Bio import SeqIO, Entrez
   from Bio.Seq import Seq
   ```

2. **Set Entrez email** when using NCBI databases; load only `NCBI_API_KEY` from the environment if present
   ```python
   import os
   from Bio import Entrez

   Entrez.email = "your.email@example.com"
   Entrez.tool = "your_tool_name"
   if api_key := os.environ.get("NCBI_API_KEY"):
       Entrez.api_key = api_key
   ```

3. **Use appropriate file formats** - Check which format best suits the task
   ```python
   # Common formats: "fasta", "genbank", "fastq", "clustal", "phylip"
   ```

4. **Handle files properly** - Close handles after use or use context managers
   ```python
   with open("file.fasta") as handle:
       records = SeqIO.parse(handle, "fasta")
   ```

5. **Use iterators for large files** - Avoid loading everything into memory
   ```python
   for record in SeqIO.parse("large_file.fasta", "fasta"):
       # Process one record at a time
   ```

6. **Handle errors gracefully** - Network operations and file parsing can fail
   ```python
   from urllib.error import HTTPError

   try:
       handle = Entrez.efetch(db="nucleotide", id=accession)
   except HTTPError as e:
       print(f"Error: {e}")
   ```

## Common Patterns

### Pattern 1: Fetch Sequence from GenBank

```python
from Bio import Entrez, SeqIO

Entrez.email = "your.email@example.com"

# Fetch sequence
handle = Entrez.efetch(db="nucleotide", id="EU490707", rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")
handle.close()

print(f"Description: {record.description}")
print(f"Sequence length: {len(record.seq)}")
```

### Pattern 2: Sequence Analysis Pipeline

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction

for record in SeqIO.parse("sequences.fasta", "fasta"):
    # Calculate statistics
    gc = gc_fraction(record.seq)
    length = len(record.seq)

    # Find ORFs, translate, etc.
    protein = record.seq.translate()

    print(f"{record.id}: {length} bp, GC={gc:.2%}")
```

### Pattern 3: BLAST and Fetch Top Hits

```python
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import Entrez, SeqIO

Entrez.email = "your.email@example.com"

# Run BLAST
result_handle = NCBIWWW.qblast("blastn", "nt", sequence)
blast_record = NCBIXML.read(result_handle)

# Get top hit accessions
accessions = [aln.accession for aln in blast_record.alignments[:5]]

# Fetch sequences
for acc in accessions:
    handle = Entrez.efetch(db="nucleotide", id=acc, rettype="fasta", retmode="text")
    record = SeqIO.read(handle, "fasta")
    handle.close()
    print(f">{record.description}")
```

### Pattern 4: Build Phylogenetic Tree from Sequences

```python
from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

# Read alignment
alignment = AlignIO.read("alignment.fasta", "fasta")

# Calculate distances
calculator = DistanceCalculator("identity")
dm = calculator.get_distance(alignment)

# Build tree
constructor = DistanceTreeConstructor()
tree = constructor.nj(dm)

# Visualize
Phylo.draw_ascii(tree)
```

## Best Practices

1. **Always read relevant reference documentation** before writing code
2. **Use grep to search reference files** for specific functions or examples
3. **Validate file formats** before parsing
4. **Handle missing data gracefully** - Not all records have all fields
5. **Cache downloaded data** - Don't repeatedly download the same sequences
6. **Respect NCBI rate limits** - Use API keys, registered tool/email values for reusable software, and Entrez history/batching for large jobs
7. **Test with small datasets** before processing large files
8. **Keep Biopython updated** to get latest features and bug fixes
9. **Use appropriate genetic code tables** for translation
10. **Document analysis parameters** for reproducibility

## Troubleshooting Common Issues

### Issue: "No handlers could be found for logger 'Bio.Entrez'"
**Solution:** This is just a warning. Set Entrez.email to suppress it.

### Issue: "HTTP Error 400" from NCBI
**Solution:** Check that IDs/accessions are valid and properly formatted.

### Issue: "ValueError: EOF" when parsing files
**Solution:** Verify file format matches the specified format string.

### Issue: Alignment fails with "sequences are not the same length"
**Solution:** Ensure sequences are aligned before using AlignIO or MultipleSeqAlignment.

### Issue: BLAST searches are slow
**Solution:** Use local BLAST for large-scale searches, or cache results.

### Issue: PDB parser warnings
**Solution:** Use `PDBParser(QUIET=True)` to suppress warnings, or investigate structure quality.

### Issue: ImportError for Bio.HMM, Bio.MarkovModel, or Bio.Application
**Solution:** These modules were removed in Biopython 1.86. Use [hmmlearn](https://pypi.org/project/hmmlearn/) for HMMs and the standard library `subprocess` module instead of `Bio.Application` CLI wrappers.

### Issue: PairwiseAligner returns fewer alignments after upgrading to 1.86+
**Solution:** The default gap score changed from 0 to -1 in 1.86, eliminating trivial tie alignments. Set `aligner.gap_score = 0` to restore the old behavior if needed (see `references/alignment.md`).

## Additional Resources

- **Official Documentation**: https://biopython.org/docs/latest/
- **Tutorial**: https://biopython.org/docs/latest/Tutorial/
- **Cookbook**: https://biopython.org/docs/latest/Tutorial/ (advanced examples)
- **GitHub**: https://github.com/biopython/biopython
- **Release notes**: https://github.com/biopython/biopython/blob/master/NEWS.rst
- **Deprecated APIs**: https://github.com/biopython/biopython/blob/master/DEPRECATED.rst
- **Mailing List**: biopython@biopython.org

## Quick Reference

To locate information in reference files, use these search patterns:

```bash
# Search for specific functions
rg -n "function_name" references/*.md

# Find examples of specific tasks
rg -n "example" references/sequence_io.md

# Find all occurrences of a module
rg -n "Bio.Seq" references/*.md
```

## Summary

Biopython provides comprehensive tools for computational molecular biology. When using this skill:

1. **Identify the task domain** (sequences, alignments, databases, BLAST, structures, phylogenetics, or advanced)
2. **Consult the appropriate reference file** in the `references/` directory
3. **Adapt code examples** to the specific use case
4. **Combine multiple modules** when needed for complex workflows
5. **Follow best practices** for file handling, error checking, and data management

The modular reference documentation ensures detailed, searchable information for every major Biopython capability.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/biopython/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/advanced.md`

# Advanced Biopython Features

## Sequence Motifs with Bio.motifs

### Creating Motifs

```python
from Bio import motifs
from Bio.Seq import Seq

# Create motif from instances
instances = [
    Seq("TACAA"),
    Seq("TACGC"),
    Seq("TACAC"),
    Seq("TACCC"),
    Seq("AACCC"),
    Seq("AATGC"),
    Seq("AATGC"),
]

motif = motifs.create(instances)
```

### Motif Consensus and Degenerate Sequences

```python
# Get consensus sequence
print(motif.counts.consensus)

# Get degenerate consensus (IUPAC ambiguity codes)
print(motif.counts.degenerate_consensus)

# Access counts matrix
print(motif.counts)
```

### Position Weight Matrix (PWM)

```python
# Create position weight matrix
pwm = motif.counts.normalize(pseudocounts=0.5)
print(pwm)

# Calculate information content
ic = sum(motif.relative_entropy)
print(f"Information content: {ic:.2f} bits")
```

### Searching for Motifs

```python
from Bio.Seq import Seq

# Search sequence for motif
test_seq = Seq("ATACAGGACAGACATACGCATACAACATTACAC")

# Get Position Specific Scoring Matrix (PSSM)
pssm = pwm.log_odds()

# Search sequence
for position, score in pssm.search(test_seq, threshold=5.0):
    print(f"Position {position}: score = {score:.2f}")
```

### Reading Motifs from Files

```python
# Read motif from JASPAR format
with open("motif.jaspar") as handle:
    motif = motifs.read(handle, "jaspar")

# Read multiple motifs
with open("motifs.jaspar") as handle:
    for m in motifs.parse(handle, "jaspar"):
        print(m.name)

# Supported formats: jaspar, meme, transfac, pfm
```

### Writing Motifs

```python
# Write motif in JASPAR format
with open("output.jaspar", "w") as handle:
    handle.write(motif.format("jaspar"))
```

## Population Genetics with Bio.PopGen

### Working with GenePop Files

```python
from Bio.PopGen import GenePop

# Read GenePop file
with open("data.gen") as handle:
    record = GenePop.read(handle)

# Access populations
print(f"Number of populations: {len(record.populations)}")
print(f"Loci: {record.loci_list}")

# Iterate through populations
for pop_idx, pop in enumerate(record.populations):
    print(f"\nPopulation {pop_idx + 1}:")
    for individual in pop:
        print(f"  {individual[0]}: {individual[1]}")
```

### Calculating Population Statistics

```python
from Bio.PopGen.GenePop.Controller import GenePopController

# Create controller
ctrl = GenePopController()

# Calculate basic statistics
result = ctrl.calc_allele_genotype_freqs("data.gen")

# Calculate Fst
fst_result = ctrl.calc_fst_all("data.gen")
print(f"Fst: {fst_result}")

# Test Hardy-Weinberg equilibrium
hw_result = ctrl.test_hw_pop("data.gen", "probability")
```

## Sequence Utilities with Bio.SeqUtils

### GC Content

```python
from Bio.SeqUtils import gc_fraction
from Bio.Seq import Seq

seq = Seq("ATCGATCGATCG")
gc = gc_fraction(seq)
print(f"GC content: {gc:.2%}")
```

### Molecular Weight

```python
from Bio.SeqUtils import molecular_weight

# DNA molecular weight
dna_seq = Seq("ATCG")
mw = molecular_weight(dna_seq, seq_type="DNA")
print(f"DNA MW: {mw:.2f} g/mol")

# Protein molecular weight
protein_seq = Seq("ACDEFGHIKLMNPQRSTVWY")
mw = molecular_weight(protein_seq, seq_type="protein")
print(f"Protein MW: {mw:.2f} Da")
```

### Melting Temperature

```python
from Bio.SeqUtils import MeltingTemp as mt

# Calculate Tm using nearest-neighbor method
seq = Seq("ATCGATCGATCG")
tm = mt.Tm_NN(seq)
print(f"Tm: {tm:.1f}°C")

# Use different salt concentration
tm = mt.Tm_NN(seq, Na=50, Mg=1.5)  # 50 mM Na+, 1.5 mM Mg2+

# Wallace rule (for primers)
tm_wallace = mt.Tm_Wallace(seq)
```

### GC Skew

```python
from Bio.SeqUtils import gc_skew

# Calculate GC skew
seq = Seq("ATCGATCGGGCCCAAATTT")
skew = gc_skew(seq, window=100)
print(f"GC skew: {skew}")
```

### ProtParam - Protein Analysis

```python
from Bio.SeqUtils.ProtParam import ProteinAnalysis

protein_seq = "ACDEFGHIKLMNPQRSTVWY"
analyzed_seq = ProteinAnalysis(protein_seq)

# Molecular weight
print(f"MW: {analyzed_seq.molecular_weight():.2f} Da")

# Isoelectric point
print(f"pI: {analyzed_seq.isoelectric_point():.2f}")

# Amino acid composition
print(f"Composition: {analyzed_seq.get_amino_acids_percent()}")

# Instability index
print(f"Instability: {analyzed_seq.instability_index():.2f}")

# Aromaticity
print(f"Aromaticity: {analyzed_seq.aromaticity():.2f}")

# Secondary structure fraction
ss = analyzed_seq.secondary_structure_fraction()
print(f"Helix: {ss[0]:.2%}, Turn: {ss[1]:.2%}, Sheet: {ss[2]:.2%}")

# Extinction coefficient (assumes Cys reduced, no disulfide bonds)
print(f"Extinction coefficient: {analyzed_seq.molar_extinction_coefficient()}")

# Gravy (grand average of hydropathy)
print(f"GRAVY: {analyzed_seq.gravy():.3f}")
```

## Restriction Analysis with Bio.Restriction

```python
from Bio import Restriction
from Bio.Seq import Seq

# Analyze sequence for restriction sites
seq = Seq("GAATTCATCGATCGATGAATTC")

# Use specific enzyme
ecori = Restriction.EcoRI
sites = ecori.search(seq)
print(f"EcoRI sites at: {sites}")

# Use multiple enzymes
rb = Restriction.RestrictionBatch(["EcoRI", "BamHI", "PstI"])
results = rb.search(seq)
for enzyme, sites in results.items():
    if sites:
        print(f"{enzyme}: {sites}")

# Get all enzymes that cut sequence
all_enzymes = Restriction.Analysis(rb, seq)
print(f"Cutting enzymes: {all_enzymes.with_sites()}")
```

## Sequence Translation Tables

```python
from Bio.Data import CodonTable

# Standard genetic code
standard_table = CodonTable.unambiguous_dna_by_id[1]
print(standard_table)

# Mitochondrial code
mito_table = CodonTable.unambiguous_dna_by_id[2]

# Get specific codon
print(f"ATG codes for: {standard_table.forward_table['ATG']}")

# Get stop codons
print(f"Stop codons: {standard_table.stop_codons}")

# Get start codons
print(f"Start codons: {standard_table.start_codons}")
```

## Cluster Analysis with Bio.Cluster

```python
from Bio.Cluster import kcluster
import numpy as np

# Sample data matrix (genes x conditions)
data = np.array([
    [1.2, 0.8, 0.5, 1.5],
    [0.9, 1.1, 0.7, 1.3],
    [0.2, 0.3, 2.1, 2.5],
    [0.1, 0.4, 2.3, 2.2],
])

# Perform k-means clustering
clusterid, error, nfound = kcluster(data, nclusters=2)
print(f"Cluster assignments: {clusterid}")
print(f"Error: {error}")
```

## Genome Diagrams with GenomeDiagram

```python
from Bio.Graphics import GenomeDiagram
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio import SeqIO
from reportlab.lib import colors

# Read GenBank file
record = SeqIO.read("sequence.gb", "genbank")

# Create diagram
gd_diagram = GenomeDiagram.Diagram("Genome Diagram")
gd_track = gd_diagram.new_track(1, greytrack=True)
gd_feature_set = gd_track.new_set()

# Add features
for feature in record.features:
    if feature.type == "CDS":
        color = colors.blue
    elif feature.type == "gene":
        color = colors.lightblue
    else:
        color = colors.grey

    gd_feature_set.add_feature(
        feature,
        color=color,
        label=True,
        label_size=6,
        label_angle=45
    )

# Draw and save
gd_diagram.draw(format="linear", pagesize="A4", fragments=1)
gd_diagram.write("genome_diagram.pdf", "PDF")
```

## Sequence Comparison with PairwiseAligner

`Bio.pairwise2` is deprecated (since Biopython 1.80). Use `Bio.Align.PairwiseAligner` for new pairwise alignment code (see `alignment.md`). For HMM workflows, `Bio.HMM` and `Bio.MarkovModel` were removed in Biopython 1.86; use [hmmlearn](https://pypi.org/project/hmmlearn/) instead.

```python
from Bio.Align import PairwiseAligner

aligner = PairwiseAligner()
aligner.mode = "global"
aligner.match_score = 1
aligner.mismatch_score = 0
aligner.gap_score = 0  # Optional: mimic the old globalxx scoring style

alignments = aligner.align("ACCGT", "ACGT")

for alignment in alignments[:3]:
    print(alignment)
    print(f"Score: {alignment.score}")
```

Avoid importing `Bio.pairwise2` in new code. It remains a legacy migration concern only.

## Working with PubChem

```python
from Bio import Entrez

Entrez.email = "your.email@example.com"

# Search PubChem
handle = Entrez.esearch(db="pccompound", term="aspirin")
result = Entrez.read(handle)
handle.close()

compound_id = result["IdList"][0]

# Get compound information
handle = Entrez.efetch(db="pccompound", id=compound_id, retmode="xml")
compound_data = handle.read()
handle.close()
```

## Sequence Features with Bio.SeqFeature

```python
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Create a feature
feature = SeqFeature(
    location=FeatureLocation(start=10, end=50),
    type="CDS",
    strand=1,
    qualifiers={"gene": ["ABC1"], "product": ["ABC protein"]}
)

# Add feature to record
record = SeqRecord(Seq("ATCG" * 20), id="seq1")
record.features.append(feature)

# Extract feature sequence
feature_seq = feature.extract(record.seq)
print(feature_seq)
```

## Sequence Ambiguity

```python
from Bio.Data import IUPACData

# DNA ambiguity codes
print(IUPACData.ambiguous_dna_letters)

# Protein ambiguity codes
print(IUPACData.ambiguous_protein_letters)

# Resolve ambiguous bases
print(IUPACData.ambiguous_dna_values["N"])  # Any base
print(IUPACData.ambiguous_dna_values["R"])  # A or G
```

## Quality Scores (FASTQ)

```python
from Bio import SeqIO

# Read FASTQ with quality scores
for record in SeqIO.parse("reads.fastq", "fastq"):
    print(f"ID: {record.id}")
    print(f"Sequence: {record.seq}")
    print(f"Quality: {record.letter_annotations['phred_quality']}")

    # Calculate average quality
    avg_quality = sum(record.letter_annotations['phred_quality']) / len(record)
    print(f"Average quality: {avg_quality:.2f}")

    # Filter by quality
    min_quality = min(record.letter_annotations['phred_quality'])
    if min_quality >= 20:
        print("High quality read")
```

## Best Practices

1. **Use appropriate modules** - Choose the right tool for your analysis
2. **Handle pseudocounts** - Important for motif analysis
3. **Validate input data** - Check file formats and data quality
4. **Consider performance** - Some operations can be computationally intensive
5. **Cache results** - Store intermediate results for large analyses
6. **Use proper genetic codes** - Select appropriate translation tables
7. **Document parameters** - Record thresholds and settings used
8. **Validate statistical results** - Understand limitations of tests
9. **Handle edge cases** - Check for empty results or invalid input
10. **Combine modules** - Leverage multiple Biopython tools together

## Common Use Cases

### Find ORFs

```python
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction

def find_orfs(seq, min_length=100):
    """Find all ORFs in sequence."""
    orfs = []

    for strand, nuc in [(+1, seq), (-1, seq.reverse_complement())]:
        for frame in range(3):
            trans = nuc[frame:].translate()
            trans_len = len(trans)

            aa_start = 0
            while aa_start < trans_len:
                aa_end = trans.find("*", aa_start)
                if aa_end == -1:
                    aa_end = trans_len

                if aa_end - aa_start >= min_length // 3:
                    start = frame + aa_start * 3
                    end = frame + aa_end * 3
                    orfs.append({
                        'start': start,
                        'end': end,
                        'strand': strand,
                        'frame': frame,
                        'length': end - start,
                        'sequence': nuc[start:end]
                    })

                aa_start = aa_end + 1

    return orfs

# Use it
record = SeqIO.read("sequence.fasta", "fasta")
orfs = find_orfs(record.seq, min_length=300)
for orf in orfs:
    print(f"ORF: {orf['start']}-{orf['end']}, strand={orf['strand']}, length={orf['length']}")
```

### Analyze Codon Usage

```python
from Bio import SeqIO

def analyze_codon_usage(fasta_file):
    """Analyze codon usage in coding sequences."""
    codon_counts = {}

    for record in SeqIO.parse(fasta_file, "fasta"):
        # Ensure sequence is multiple of 3
        seq = record.seq[:len(record.seq) - len(record.seq) % 3]

        # Count codons
        for i in range(0, len(seq), 3):
            codon = str(seq[i:i+3])
            codon_counts[codon] = codon_counts.get(codon, 0) + 1

    # Calculate frequencies
    total = sum(codon_counts.values())
    codon_freq = {k: v/total for k, v in codon_counts.items()}

    return codon_freq
```

### Calculate Sequence Complexity

```python
def sequence_complexity(seq, k=2):
    """Calculate k-mer complexity (Shannon entropy)."""
    import math
    from collections import Counter

    # Generate k-mers
    kmers = [str(seq[i:i+k]) for i in range(len(seq) - k + 1)]

    # Count k-mers
    counts = Counter(kmers)
    total = len(kmers)

    # Calculate entropy
    entropy = 0
    for count in counts.values():
        freq = count / total
        entropy -= freq * math.log2(freq)

    # Normalize by maximum possible entropy
    max_entropy = math.log2(4 ** k)  # For DNA

    return entropy / max_entropy if max_entropy > 0 else 0

# Use it
from Bio.Seq import Seq
seq = Seq("ATCGATCGATCGATCG")
complexity = sequence_complexity(seq, k=2)
print(f"Sequence complexity: {complexity:.3f}")
```

### Extract Promoter Regions

```python
def extract_promoters(genbank_file, upstream=500):
    """Extract promoter regions upstream of genes."""
    from Bio import SeqIO

    record = SeqIO.read(genbank_file, "genbank")
    promoters = []

    for feature in record.features:
        if feature.type == "gene":
            if feature.strand == 1:
                # Forward strand
                start = max(0, feature.location.start - upstream)
                end = feature.location.start
            else:
                # Reverse strand
                start = feature.location.end
                end = min(len(record.seq), feature.location.end + upstream)

            promoter_seq = record.seq[start:end]
            if feature.strand == -1:
                promoter_seq = promoter_seq.reverse_complement()

            promoters.append({
                'gene': feature.qualifiers.get('gene', ['Unknown'])[0],
                'sequence': promoter_seq,
                'start': start,
                'end': end
            })

    return promoters
```

### `references/alignment.md`

# Sequence Alignments with Bio.Align and Bio.AlignIO

## Overview

Bio.Align provides tools for pairwise sequence alignment using various algorithms, while Bio.AlignIO handles reading and writing multiple sequence alignment files in various formats.

## Pairwise Alignment with Bio.Align

### The PairwiseAligner Class

The `PairwiseAligner` class performs pairwise sequence alignments using Needleman-Wunsch (global), Smith-Waterman (local), Gotoh (three-state), and Waterman-Smith-Beyer algorithms. The appropriate algorithm is automatically selected based on gap score parameters.

### Creating an Aligner

```python
from Bio import Align

# Create aligner with default parameters
aligner = Align.PairwiseAligner()

# Default scores (as of Biopython 1.86+):
# - Match score: +1.0
# - Mismatch score: 0.0
# - All gap scores: -1.0  (changed from 0 in 1.86 to avoid trivial tie alignments)
```

**Note (1.86+):** The default gap score changed from 0 to -1. Previously, mismatches and gap combinations could score 0, producing many logically equivalent alignments. To restore pre-1.86 behavior:

```python
aligner.gap_score = 0
```

### Customizing Alignment Parameters

```python
# Set scoring parameters
aligner.match_score = 2.0
aligner.mismatch_score = -1.0
aligner.gap_score = -0.5

# Or use separate gap opening/extension penalties
aligner.open_gap_score = -2.0
aligner.extend_gap_score = -0.5

# Set internal gap scores separately
aligner.internal_open_gap_score = -2.0
aligner.internal_extend_gap_score = -0.5

# Set end gap scores (for semi-global alignment)
aligner.left_open_gap_score = 0.0
aligner.left_extend_gap_score = 0.0
aligner.right_open_gap_score = 0.0
aligner.right_extend_gap_score = 0.0
```

### Alignment Modes

```python
# Global alignment (default)
aligner.mode = 'global'

# Local alignment
aligner.mode = 'local'
```

### Performing Alignments

```python
from Bio.Seq import Seq

seq1 = Seq("ACCGGT")
seq2 = Seq("ACGGT")

# Get all optimal alignments
alignments = aligner.align(seq1, seq2)

# Iterate through alignments
for alignment in alignments:
    print(alignment)
    print(f"Score: {alignment.score}")

# Get just the score
score = aligner.score(seq1, seq2)
```

### Using Substitution Matrices

```python
from Bio.Align import substitution_matrices

# Load a substitution matrix
matrix = substitution_matrices.load("BLOSUM62")
aligner.substitution_matrix = matrix

# Align protein sequences
protein1 = Seq("KEVLA")
protein2 = Seq("KSVLA")
alignments = aligner.align(protein1, protein2)
```

### Available Substitution Matrices

Common matrices include:
- **BLOSUM** series (BLOSUM45, BLOSUM50, BLOSUM62, BLOSUM80, BLOSUM90)
- **PAM** series (PAM30, PAM70, PAM250)
- **MATCH** - Simple match/mismatch matrix

```python
# List available matrices
available = substitution_matrices.load()
print(available)
```

## Multiple Sequence Alignments with Bio.AlignIO

### Reading Alignments

Bio.AlignIO provides similar API to Bio.SeqIO but for alignment files:

```python
from Bio import AlignIO

# Read a single alignment
alignment = AlignIO.read("alignment.aln", "clustal")

# Parse multiple alignments from a file
for alignment in AlignIO.parse("alignments.aln", "clustal"):
    print(f"Alignment with {len(alignment)} sequences")
    print(f"Alignment length: {alignment.get_alignment_length()}")
```

### Supported Alignment Formats

Common formats include:
- **clustal** - Clustal format
- **phylip** - PHYLIP format
- **phylip-relaxed** - Relaxed PHYLIP (longer names)
- **stockholm** - Stockholm format
- **fasta** - FASTA format (aligned)
- **nexus** - NEXUS format
- **emboss** - EMBOSS alignment format
- **msf** - MSF format
- **maf** - Multiple Alignment Format

### Writing Alignments

```python
# Write alignment to file
AlignIO.write(alignment, "output.aln", "clustal")

# Convert between formats
count = AlignIO.convert("input.aln", "clustal", "output.phy", "phylip")
```

### Working with Alignment Objects

```python
from Bio import AlignIO

alignment = AlignIO.read("alignment.aln", "clustal")

# Get alignment properties
print(f"Number of sequences: {len(alignment)}")
print(f"Alignment length: {alignment.get_alignment_length()}")

# Access individual sequences
for record in alignment:
    print(f"{record.id}: {record.seq}")

# Get alignment column
column = alignment[:, 0]  # First column

# Get alignment slice
sub_alignment = alignment[:, 10:20]  # Positions 10-20

# Get specific sequence
seq_record = alignment[0]  # First sequence
```

### Alignment Analysis

```python
# Calculate alignment statistics with current Biopython APIs.
# Avoid Bio.AlignInfo.SummaryInfo: it is deprecated in 1.86 and several
# methods were removed in 1.85/1.86.
from Bio import AlignIO
from Bio.motifs import Motif

msa = AlignIO.read("alignment.aln", "clustal")
alignment = msa.alignment  # New-style Bio.Align.Alignment

# Build a motif from a DNA alignment to inspect per-column counts
motif = Motif("ACGT", alignment)
counts = motif.counts
consensus = counts.consensus

# Information content replacement for deprecated SummaryInfo methods
information_content = sum(motif.relative_entropy)

# Replacement dictionary from the new-style Alignment object
substitutions = alignment.substitutions
```

## Creating Alignments Programmatically

### From SeqRecord Objects

```python
from Bio.Align import MultipleSeqAlignment
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

# Create records
records = [
    SeqRecord(Seq("ACTGCTAGCTAG"), id="seq1"),
    SeqRecord(Seq("ACT-CTAGCTAG"), id="seq2"),
    SeqRecord(Seq("ACTGCTA-CTAG"), id="seq3"),
]

# Create alignment
alignment = MultipleSeqAlignment(records)
```

### Adding Sequences to Alignments

```python
# Start with empty alignment
alignment = MultipleSeqAlignment([])

# Add sequences (must have same length)
alignment.append(SeqRecord(Seq("ACTG"), id="seq1"))
alignment.append(SeqRecord(Seq("ACTG"), id="seq2"))

# Extend with another alignment
alignment.extend(other_alignment)
```

## Advanced Alignment Operations

### Removing Gaps

```python
# Remove all gap-only columns
no_gaps = []
for i in range(alignment.get_alignment_length()):
    column = alignment[:, i]
    if set(column) != {'-'}:  # Not all gaps
        no_gaps.append(column)
```

### Alignment Sorting

```python
# Sort by sequence ID
sorted_alignment = sorted(alignment, key=lambda x: x.id)
alignment = MultipleSeqAlignment(sorted_alignment)
```

### Computing Pairwise Identities

```python
def pairwise_identity(seq1, seq2):
    """Calculate percent identity between two sequences."""
    matches = sum(a == b for a, b in zip(seq1, seq2) if a != '-' and b != '-')
    length = sum(1 for a, b in zip(seq1, seq2) if a != '-' and b != '-')
    return matches / length if length > 0 else 0

# Calculate all pairwise identities
for i, record1 in enumerate(alignment):
    for record2 in alignment[i+1:]:
        identity = pairwise_identity(record1.seq, record2.seq)
        print(f"{record1.id} vs {record2.id}: {identity:.2%}")
```

## Running External Alignment Tools

Biopython 1.86 removed `Bio.Application` and all command-line wrapper modules, including `Bio.Align.Applications`. Use Python's standard `subprocess` module with argument lists. Keep executable names and flags explicit, and do not construct command arguments from unsanitized user input.

### Clustal Omega (via subprocess)

```python
import subprocess
from Bio import AlignIO

cmd = [
    "clustalo",
    "-i", "sequences.fasta",
    "-o", "alignment.aln",
    "--outfmt", "clu",
    "--force",
    "--auto",
]

subprocess.run(cmd, check=True)

# Read result
alignment = AlignIO.read("alignment.aln", "clustal")
```

### MUSCLE (via subprocess)

```python
import subprocess
from Bio import AlignIO

cmd = [
    "muscle",
    "-align", "sequences.fasta",
    "-output", "alignment.fasta",
]

subprocess.run(cmd, check=True)
alignment = AlignIO.read("alignment.fasta", "fasta")
```

## Best Practices

1. **Choose appropriate scoring schemes** - Use BLOSUM62 for proteins, custom scores for DNA
2. **Consider alignment mode** - Global for similar-length sequences, local for finding conserved regions
3. **Set gap penalties carefully** - Higher penalties create fewer, longer gaps
4. **Use appropriate formats** - FASTA for simple alignments, Stockholm for rich annotation
5. **Validate alignment quality** - Check for conserved regions and percent identity
6. **Handle large alignments carefully** - Use slicing and iteration for memory efficiency
7. **Preserve metadata** - Maintain SeqRecord IDs and annotations through alignment operations

## Common Use Cases

### Find Best Local Alignment

```python
from Bio.Align import PairwiseAligner
from Bio.Seq import Seq

aligner = PairwiseAligner()
aligner.mode = 'local'
aligner.match_score = 2
aligner.mismatch_score = -1

seq1 = Seq("AGCTTAGCTAGCTAGC")
seq2 = Seq("CTAGCTAGC")

alignments = aligner.align(seq1, seq2)
print(alignments[0])
```

### Protein Sequence Alignment

```python
from Bio.Align import PairwiseAligner, substitution_matrices

aligner = PairwiseAligner()
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
aligner.open_gap_score = -10
aligner.extend_gap_score = -0.5

protein1 = Seq("KEVLA")
protein2 = Seq("KEVLAEQP")
alignments = aligner.align(protein1, protein2)
```

### Extract Conserved Regions

```python
from Bio import AlignIO

alignment = AlignIO.read("alignment.aln", "clustal")

# Find columns with >80% identity
conserved_positions = []
for i in range(alignment.get_alignment_length()):
    column = alignment[:, i]
    most_common = max(set(column), key=column.count)
    if column.count(most_common) / len(column) > 0.8:
        conserved_positions.append(i)

print(f"Conserved positions: {conserved_positions}")
```

### `references/blast.md`

# BLAST Operations with Bio.Blast

## Overview

Bio.Blast provides tools for running BLAST searches (both locally and via NCBI web services) and parsing BLAST results in various formats. The module handles the complexity of submitting queries and parsing outputs.

## Running BLAST via NCBI Web Services

### Bio.Blast.NCBIWWW

The `qblast()` function submits sequences to NCBI's online BLAST service:

```python
from Bio.Blast import NCBIWWW
from Bio import SeqIO

# Read sequence from file
record = SeqIO.read("sequence.fasta", "fasta")

# Run BLAST search
result_handle = NCBIWWW.qblast(
    program="blastn",           # BLAST program
    database="nt",              # Database to search
    sequence=str(record.seq)    # Query sequence
)

# Save results
with open("blast_results.xml", "w") as out_file:
    out_file.write(result_handle.read())
result_handle.close()
```

### BLAST Programs Available

- **blastn** - Nucleotide vs nucleotide
- **blastp** - Protein vs protein
- **blastx** - Translated nucleotide vs protein
- **tblastn** - Protein vs translated nucleotide
- **tblastx** - Translated nucleotide vs translated nucleotide

### Common Databases

**Nucleotide databases:**
- `nt` - All GenBank+EMBL+DDBJ+PDB sequences
- `refseq_rna` - RefSeq RNA sequences

**Protein databases:**
- `nr` - All non-redundant GenBank CDS translations
- `refseq_protein` - RefSeq protein sequences
- `pdb` - Protein Data Bank sequences
- `swissprot` - Curated UniProtKB/Swiss-Prot

### Advanced qblast Parameters

```python
result_handle = NCBIWWW.qblast(
    program="blastn",
    database="nt",
    sequence=str(record.seq),
    expect=0.001,              # E-value threshold
    hitlist_size=50,           # Number of hits to return
    alignments=25,             # Number of alignments to show
    word_size=11,              # Word size for initial match
    gapcosts="5 2",            # Gap costs (open extend)
    format_type="XML"          # Output format (default)
)
```

### Using Sequence Files or IDs

```python
# Use FASTA format string
fasta_string = open("sequence.fasta").read()
result_handle = NCBIWWW.qblast("blastn", "nt", fasta_string)

# Use GenBank ID
result_handle = NCBIWWW.qblast("blastn", "nt", "EU490707")

# Use GI number
result_handle = NCBIWWW.qblast("blastn", "nt", "160418")
```

## Parsing BLAST Results

### Bio.Blast.NCBIXML

NCBIXML provides parsers for BLAST XML output (the recommended format):

```python
from Bio.Blast import NCBIXML

# Parse single BLAST result
with open("blast_results.xml") as result_handle:
    blast_record = NCBIXML.read(result_handle)
```

### Accessing BLAST Record Data

```python
# Query information
print(f"Query: {blast_record.query}")
print(f"Query length: {blast_record.query_length}")
print(f"Database: {blast_record.database}")
print(f"Number of sequences in database: {blast_record.database_sequences}")

# Iterate through alignments (hits)
for alignment in blast_record.alignments:
    print(f"\nHit: {alignment.title}")
    print(f"Length: {alignment.length}")
    print(f"Accession: {alignment.accession}")

    # Each alignment can have multiple HSPs (high-scoring pairs)
    for hsp in alignment.hsps:
        print(f"  E-value: {hsp.expect}")
        print(f"  Score: {hsp.score}")
        print(f"  Bits: {hsp.bits}")
        print(f"  Identities: {hsp.identities}/{hsp.align_length}")
        print(f"  Gaps: {hsp.gaps}")
        print(f"  Query: {hsp.query}")
        print(f"  Match: {hsp.match}")
        print(f"  Subject: {hsp.sbjct}")
```

### Filtering Results

```python
# Only show hits with E-value < 0.001
E_VALUE_THRESH = 0.001

for alignment in blast_record.alignments:
    for hsp in alignment.hsps:
        if hsp.expect < E_VALUE_THRESH:
            print(f"Hit: {alignment.title}")
            print(f"E-value: {hsp.expect}")
            print(f"Identities: {hsp.identities}/{hsp.align_length}")
            print()
```

### Multiple BLAST Results

For files containing multiple BLAST results (e.g., from batch searches):

```python
from Bio.Blast import NCBIXML

with open("batch_blast_results.xml") as result_handle:
    blast_records = NCBIXML.parse(result_handle)

    for blast_record in blast_records:
        print(f"\nQuery: {blast_record.query}")
        print(f"Hits: {len(blast_record.alignments)}")

        if blast_record.alignments:
            # Get best hit
            best_alignment = blast_record.alignments[0]
            best_hsp = best_alignment.hsps[0]
            print(f"Best hit: {best_alignment.title}")
            print(f"E-value: {best_hsp.expect}")
```

## Running Local BLAST

### Prerequisites

Local BLAST requires:
1. BLAST+ command-line tools installed
2. BLAST databases downloaded locally

### Running BLAST+ via subprocess

Biopython 1.86 removed `Bio.Application` and the BLAST command-line wrappers in `Bio.Blast.Applications`. Use the standard library `subprocess` module with explicit argument lists. Keep command names and flags fixed, validate file paths before running, and do not interpolate unsanitized user input into shell commands.

```python
import subprocess
from Bio.Blast import NCBIXML

cmd = [
    "blastn",
    "-query", "input.fasta",
    "-db", "local_database",
    "-evalue", "0.001",
    "-outfmt", "5",  # XML format for NCBIXML
    "-out", "results.xml",
]
subprocess.run(cmd, check=True)

# Parse results
with open("results.xml") as result_handle:
    blast_record = NCBIXML.read(result_handle)
```

### Common BLAST+ commands

- `blastn` - nucleotide vs nucleotide
- `blastp` - protein vs protein
- `blastx` - translated nucleotide vs protein
- `tblastn` - protein vs translated nucleotide
- `tblastx` - translated nucleotide vs translated nucleotide
- `makeblastdb` - create local BLAST databases

### Creating BLAST Databases

```python
import subprocess

cmd = [
    "makeblastdb",
    "-in", "sequences.fasta",
    "-dbtype", "nucl",
    "-out", "my_database",
]
subprocess.run(cmd, check=True)
```

## Analyzing BLAST Results

### Extract Best Hits

```python
def get_best_hits(blast_record, num_hits=10, e_value_thresh=0.001):
    """Extract best hits from BLAST record."""
    hits = []
    for alignment in blast_record.alignments[:num_hits]:
        for hsp in alignment.hsps:
            if hsp.expect < e_value_thresh:
                hits.append({
                    'title': alignment.title,
                    'accession': alignment.accession,
                    'length': alignment.length,
                    'e_value': hsp.expect,
                    'score': hsp.score,
                    'identities': hsp.identities,
                    'align_length': hsp.align_length,
                    'query_start': hsp.query_start,
                    'query_end': hsp.query_end,
                    'sbjct_start': hsp.sbjct_start,
                    'sbjct_end': hsp.sbjct_end
                })
                break  # Only take best HSP per alignment
    return hits
```

### Calculate Percent Identity

```python
def calculate_percent_identity(hsp):
    """Calculate percent identity for an HSP."""
    return (hsp.identities / hsp.align_length) * 100

# Use it
for alignment in blast_record.alignments:
    for hsp in alignment.hsps:
        if hsp.expect < 0.001:
            identity = calculate_percent_identity(hsp)
            print(f"{alignment.title}: {identity:.2f}% identity")
```

### Extract Hit Sequences

```python
from Bio import Entrez, SeqIO

Entrez.email = "your.email@example.com"

def fetch_hit_sequences(blast_record, num_sequences=5):
    """Fetch sequences for top BLAST hits."""
    sequences = []

    for alignment in blast_record.alignments[:num_sequences]:
        accession = alignment.accession

        # Fetch sequence from GenBank
        handle = Entrez.efetch(
            db="nucleotide",
            id=accession,
            rettype="fasta",
            retmode="text"
        )
        record = SeqIO.read(handle, "fasta")
        handle.close()

        sequences.append(record)

    return sequences
```

## Parsing Other BLAST Formats

### Tab-Delimited Output (outfmt 6/7)

```python
import subprocess

cmd = [
    "blastn",
    "-query", "input.fasta",
    "-db", "database",
    "-outfmt", "6",
    "-out", "results.txt",
]
subprocess.run(cmd, check=True)

# Parse tabular results
with open("results.txt") as f:
    for line in f:
        fields = line.strip().split('\t')
        query_id = fields[0]
        subject_id = fields[1]
        percent_identity = float(fields[2])
        align_length = int(fields[3])
        e_value = float(fields[10])
        bit_score = float(fields[11])

        print(f"{query_id} -> {subject_id}: {percent_identity}% identity, E={e_value}")
```

### Custom Output Formats

```python
import subprocess

# Specify custom columns (outfmt 6 with custom fields)
cmd = [
    "blastn",
    "-query", "input.fasta",
    "-db", "database",
    "-outfmt", "6 qseqid sseqid pident length evalue bitscore qseq sseq",
    "-out", "results.txt",
]
subprocess.run(cmd, check=True)
```

## Best Practices

1. **Use XML format** for parsing (outfmt 5) - most reliable and complete
2. **Save BLAST results** - Don't re-run searches unnecessarily
3. **Set appropriate E-value thresholds** - Default is 10, but 0.001-0.01 is often better
4. **Handle rate limits** - NCBI limits request frequency
5. **Use local BLAST** for large-scale searches or repeated queries
6. **Cache results** - Save parsed data to avoid re-parsing
7. **Check for empty results** - Handle cases with no hits gracefully
8. **Consider alternatives** - For large datasets, consider DIAMOND or other fast aligners
9. **Batch searches** - Submit multiple sequences together when possible
10. **Filter by identity** - E-value alone may not be sufficient

## Common Use Cases

### Basic BLAST Search and Parse

```python
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import SeqIO

# Read query sequence
record = SeqIO.read("query.fasta", "fasta")

# Run BLAST
print("Running BLAST search...")
result_handle = NCBIWWW.qblast("blastn", "nt", str(record.seq))

# Parse results
blast_record = NCBIXML.read(result_handle)

# Display top 5 hits
print(f"\nTop 5 hits for {blast_record.query}:")
for i, alignment in enumerate(blast_record.alignments[:5], 1):
    hsp = alignment.hsps[0]
    identity = (hsp.identities / hsp.align_length) * 100
    print(f"{i}. {alignment.title}")
    print(f"   E-value: {hsp.expect}, Identity: {identity:.1f}%")
```

### Find Orthologs

```python
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import Entrez, SeqIO

Entrez.email = "your.email@example.com"

# Query gene sequence
query_record = SeqIO.read("gene.fasta", "fasta")

# BLAST against specific organism
result_handle = NCBIWWW.qblast(
    "blastn",
    "nt",
    str(query_record.seq),
    entrez_query="Mus musculus[Organism]"  # Restrict to mouse
)

blast_record = NCBIXML.read(result_handle)

# Find best hit
if blast_record.alignments:
    best_hit = blast_record.alignments[0]
    print(f"Potential ortholog: {best_hit.title}")
    print(f"Accession: {best_hit.accession}")
```

### Batch BLAST Multiple Sequences

```python
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import SeqIO

# Read multiple sequences
sequences = list(SeqIO.parse("queries.fasta", "fasta"))

# Create batch results file
with open("batch_results.xml", "w") as out_file:
    for seq_record in sequences:
        print(f"Searching for {seq_record.id}...")

        result_handle = NCBIWWW.qblast("blastn", "nt", str(seq_record.seq))
        out_file.write(result_handle.read())
        result_handle.close()

# Parse batch results
with open("batch_results.xml") as result_handle:
    for blast_record in NCBIXML.parse(result_handle):
        print(f"\n{blast_record.query}: {len(blast_record.alignments)} hits")
```

### Reciprocal Best Hits

```python
def reciprocal_best_hit(seq1_id, seq2_id, database="nr", program="blastp"):
    """Check if two sequences are reciprocal best hits."""
    from Bio.Blast import NCBIWWW, NCBIXML
    from Bio import Entrez

    Entrez.email = "your.email@example.com"

    # Forward BLAST
    result1 = NCBIWWW.qblast(program, database, seq1_id)
    record1 = NCBIXML.read(result1)
    best_hit1 = record1.alignments[0].accession if record1.alignments else None

    # Reverse BLAST
    result2 = NCBIWWW.qblast(program, database, seq2_id)
    record2 = NCBIXML.read(result2)
    best_hit2 = record2.alignments[0].accession if record2.alignments else None

    # Check reciprocity
    return best_hit1 == seq2_id and best_hit2 == seq1_id
```

## Error Handling

```python
from Bio.Blast import NCBIWWW, NCBIXML
from urllib.error import HTTPError

try:
    result_handle = NCBIWWW.qblast("blastn", "nt", "ATCGATCGATCG")
    blast_record = NCBIXML.read(result_handle)
    result_handle.close()
except HTTPError as e:
    print(f"HTTP Error: {e.code}")
except Exception as e:
    print(f"Error running BLAST: {e}")
```

### `references/databases.md`

# Database Access with Bio.Entrez

## Overview

Bio.Entrez provides programmatic access to NCBI's Entrez databases, including PubMed, GenBank, Gene, Protein, Nucleotide, and many others. It handles all the complexity of API calls, rate limiting, and data parsing.

## Setup and Configuration

### Email Address (Required)

NCBI requires an email address to track usage and contact users if issues arise:

```python
from Bio import Entrez

# Always set your email
Entrez.email = "your.email@example.com"

# For reusable software, set a stable tool name and register
# the tool/email pair with NCBI.
Entrez.tool = "your_tool_name"
```

### API Key (Recommended)

Using an API key increases E-utilities rate limits from 3 to 10 requests per second. Register at https://www.ncbi.nlm.nih.gov/account/settings/ and read only `NCBI_API_KEY` from the environment — do not hardcode it and do not load unrelated environment variables:

```python
import os

# Check NCBI_API_KEY from the environment (or export it before running)
if api_key := os.environ.get("NCBI_API_KEY"):
    Entrez.api_key = api_key
```

### Rate Limiting

Biopython automatically respects NCBI rate limits:
- **Without API key**: 3 requests per second
- **With API key**: 10 requests per second

The module handles ordinary request pacing automatically and retries transient HTTP 5XX failures. For large jobs, use Entrez history (`usehistory="y"` / `WebEnv` / `query_key`) and batch requests rather than making one request per record. NCBI also recommends scheduling large jobs for weekends or between 9:00 PM and 5:00 AM Eastern time.

## Core Entrez Functions

### EInfo - Database Information

Get information about available databases and their statistics:

```python
# List all databases
handle = Entrez.einfo()
result = Entrez.read(handle)
print(result["DbList"])

# Get information about a specific database
handle = Entrez.einfo(db="pubmed")
result = Entrez.read(handle)
print(result["DbInfo"]["Description"])
print(result["DbInfo"]["Count"])  # Number of records
```

### ESearch - Search Databases

Search for records and retrieve their IDs:

```python
# Search PubMed
handle = Entrez.esearch(db="pubmed", term="biopython")
result = Entrez.read(handle)
handle.close()

id_list = result["IdList"]
count = result["Count"]
print(f"Found {count} results")
print(f"Retrieved IDs: {id_list}")
```

### Advanced ESearch Parameters

```python
# Search with additional parameters
handle = Entrez.esearch(
    db="pubmed",
    term="biopython[Title]",
    retmax=100,           # Return up to 100 IDs
    sort="relevance",     # Sort by relevance
    reldate=365,          # Only results from last year
    datetype="pdat"       # Use publication date
)
result = Entrez.read(handle)
handle.close()
```

### ESummary - Get Record Summaries

Retrieve summary information for a list of IDs:

```python
# Get summaries for multiple records
handle = Entrez.esummary(db="pubmed", id="19304878,18606172")
results = Entrez.read(handle)
handle.close()

for record in results:
    print(f"Title: {record['Title']}")
    print(f"Authors: {record['AuthorList']}")
    print(f"Journal: {record['Source']}")
    print()
```

### EFetch - Retrieve Full Records

Fetch complete records in various formats:

```python
# Fetch a GenBank record
handle = Entrez.efetch(db="nucleotide", id="EU490707", rettype="gb", retmode="text")
record_text = handle.read()
handle.close()

# Parse with SeqIO
from Bio import SeqIO
handle = Entrez.efetch(db="nucleotide", id="EU490707", rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")
handle.close()
print(record.description)
```

### EFetch Return Types

Different databases support different return types:

**Nucleotide/Protein:**
- `rettype="fasta"` - FASTA format
- `rettype="gb"` or `"genbank"` - GenBank format
- `rettype="gp"` - GenPept format (proteins)

**PubMed:**
- `rettype="medline"` - MEDLINE format
- `rettype="abstract"` - Abstract text

**Common modes:**
- `retmode="text"` - Plain text
- `retmode="xml"` - XML format

### ELink - Find Related Records

Find links between records in different databases:

```python
# Find protein records linked to a nucleotide record
handle = Entrez.elink(dbfrom="nucleotide", db="protein", id="EU490707")
result = Entrez.read(handle)
handle.close()

# Extract linked IDs
for linkset in result[0]["LinkSetDb"]:
    if linkset["LinkName"] == "nucleotide_protein":
        protein_ids = [link["Id"] for link in linkset["Link"]]
        print(f"Linked protein IDs: {protein_ids}")
```

### EPost - Upload ID Lists

Upload large lists of IDs to the server for later use:

```python
# Post IDs to server
id_list = ["19304878", "18606172", "16403221"]
handle = Entrez.epost(db="pubmed", id=",".join(id_list))
result = Entrez.read(handle)
handle.close()

# Get query_key and WebEnv for later use
query_key = result["QueryKey"]
webenv = result["WebEnv"]

# Use in subsequent queries
handle = Entrez.efetch(
    db="pubmed",
    query_key=query_key,
    WebEnv=webenv,
    rettype="medline",
    retmode="text"
)
```

### EGQuery - Global Query

Search across all Entrez databases at once:

```python
handle = Entrez.egquery(term="biopython")
result = Entrez.read(handle)
handle.close()

for row in result["eGQueryResult"]:
    print(f"{row['DbName']}: {row['Count']} results")
```

### ESpell - Spelling Suggestions

Get spelling suggestions for search terms:

```python
handle = Entrez.espell(db="pubmed", term="biopythn")
result = Entrez.read(handle)
handle.close()

print(f"Original: {result['Query']}")
print(f"Suggestion: {result['CorrectedQuery']}")
```

## Working with Different Databases

### PubMed

```python
# Search for articles
handle = Entrez.esearch(db="pubmed", term="cancer genomics", retmax=10)
result = Entrez.read(handle)
handle.close()

# Fetch abstracts
handle = Entrez.efetch(
    db="pubmed",
    id=result["IdList"],
    rettype="medline",
    retmode="text"
)
records = handle.read()
handle.close()
print(records)
```

### GenBank / Nucleotide

```python
# Search for sequences
handle = Entrez.esearch(db="nucleotide", term="Cypripedioideae[Orgn] AND matK[Gene]")
result = Entrez.read(handle)
handle.close()

# Fetch sequences
if result["IdList"]:
    handle = Entrez.efetch(
        db="nucleotide",
        id=result["IdList"][:5],
        rettype="fasta",
        retmode="text"
    )
    sequences = handle.read()
    handle.close()
```

### Protein

```python
# Search for protein sequences
handle = Entrez.esearch(db="protein", term="human insulin")
result = Entrez.read(handle)
handle.close()

# Fetch protein records
from Bio import SeqIO
handle = Entrez.efetch(
    db="protein",
    id=result["IdList"][:5],
    rettype="gp",
    retmode="text"
)
records = SeqIO.parse(handle, "genbank")
for record in records:
    print(f"{record.id}: {record.description}")
handle.close()
```

### Gene

```python
# Search for gene records
handle = Entrez.esearch(db="gene", term="BRCA1[Gene] AND human[Organism]")
result = Entrez.read(handle)
handle.close()

# Get gene information
handle = Entrez.efetch(db="gene", id=result["IdList"][0], retmode="xml")
record = Entrez.read(handle)
handle.close()
```

### Taxonomy

```python
# Search for organism
handle = Entrez.esearch(db="taxonomy", term="Homo sapiens")
result = Entrez.read(handle)
handle.close()

# Fetch taxonomic information
handle = Entrez.efetch(db="taxonomy", id=result["IdList"][0], retmode="xml")
records = Entrez.read(handle)
handle.close()

for record in records:
    print(f"TaxID: {record['TaxId']}")
    print(f"Scientific Name: {record['ScientificName']}")
    print(f"Lineage: {record['Lineage']}")
```

## Parsing Entrez Results

### Reading XML Results

```python
# Most results can be parsed with Entrez.read()
handle = Entrez.efetch(db="pubmed", id="19304878", retmode="xml")
records = Entrez.read(handle)
handle.close()

# Access parsed data
article = records['PubmedArticle'][0]['MedlineCitation']['Article']
print(article['ArticleTitle'])
```

### Handling Large Result Sets

```python
# Batch processing for large searches
search_term = "cancer[Title]"
handle = Entrez.esearch(db="pubmed", term=search_term, retmax=0)
result = Entrez.read(handle)
handle.close()

total_count = int(result["Count"])
batch_size = 500

for start in range(0, total_count, batch_size):
    # Fetch batch
    handle = Entrez.esearch(
        db="pubmed",
        term=search_term,
        retstart=start,
        retmax=batch_size
    )
    result = Entrez.read(handle)
    handle.close()

    # Process IDs
    id_list = result["IdList"]
    print(f"Processing IDs {start} to {start + len(id_list)}")
```

## Advanced Patterns

### Search History with WebEnv

```python
# Perform search and store on server
handle = Entrez.esearch(
    db="pubmed",
    term="biopython",
    usehistory="y"
)
result = Entrez.read(handle)
handle.close()

webenv = result["WebEnv"]
query_key = result["QueryKey"]
count = int(result["Count"])

# Fetch results in batches using history
batch_size = 100
for start in range(0, count, batch_size):
    handle = Entrez.efetch(
        db="pubmed",
        retstart=start,
        retmax=batch_size,
        rettype="medline",
        retmode="text",
        webenv=webenv,
        query_key=query_key
    )
    data = handle.read()
    handle.close()
    # Process data
```

### Combining Searches

```python
# Use boolean operators
complex_search = "(cancer[Title]) AND (genomics[Title]) AND 2020:2025[PDAT]"
handle = Entrez.esearch(db="pubmed", term=complex_search, retmax=100)
result = Entrez.read(handle)
handle.close()
```

## Best Practices

1. **Always set Entrez.email** - Required by NCBI
2. **Set Entrez.tool** for reusable software and register the tool/email pair with NCBI
3. **Use `NCBI_API_KEY` from the environment** for higher rate limits (10 req/s vs 3 req/s); never hardcode keys
4. **Close handles** after reading to free resources
5. **Batch large requests** - Use retstart and retmax for pagination
6. **Use WebEnv for large downloads** - Store results on server
7. **Cache locally** - Download once and save to avoid repeated requests
8. **Handle errors gracefully** - Network issues and API limits can occur
9. **Respect NCBI guidelines** - Don't overwhelm the service
10. **Use appropriate rettype** - Choose format that matches your needs
11. **Parse XML carefully** - Structure varies by database and record type

## Error Handling

```python
from urllib.error import HTTPError
from Bio import Entrez

Entrez.email = "your.email@example.com"

try:
    handle = Entrez.efetch(db="nucleotide", id="invalid_id", rettype="gb")
    record = handle.read()
    handle.close()
except HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except Exception as e:
    print(f"Error: {e}")
```

## Common Use Cases

### Download GenBank Records

```python
from Bio import Entrez, SeqIO

Entrez.email = "your.email@example.com"

# List of accession numbers
accessions = ["EU490707", "EU490708", "EU490709"]

for acc in accessions:
    handle = Entrez.efetch(db="nucleotide", id=acc, rettype="gb", retmode="text")
    record = SeqIO.read(handle, "genbank")
    handle.close()

    # Save to file
    SeqIO.write(record, f"{acc}.gb", "genbank")
```

### Search and Download Papers

```python
# Search PubMed
handle = Entrez.esearch(db="pubmed", term="machine learning bioinformatics", retmax=20)
result = Entrez.read(handle)
handle.close()

# Get details
handle = Entrez.efetch(db="pubmed", id=result["IdList"], retmode="xml")
papers = Entrez.read(handle)
handle.close()

# Extract information
for paper in papers['PubmedArticle']:
    article = paper['MedlineCitation']['Article']
    print(f"Title: {article['ArticleTitle']}")
    print(f"Journal: {article['Journal']['Title']}")
    print()
```

### Find Related Sequences

```python
# Start with one sequence
handle = Entrez.efetch(db="nucleotide", id="EU490707", rettype="gb", retmode="text")
record = SeqIO.read(handle, "genbank")
handle.close()

# Find similar sequences
handle = Entrez.elink(dbfrom="nucleotide", db="nucleotide", id="EU490707")
result = Entrez.read(handle)
handle.close()

# Get related IDs
related_ids = []
for linkset in result[0]["LinkSetDb"]:
    for link in linkset["Link"]:
        related_ids.append(link["Id"])
```

### `references/phylogenetics.md`

# Phylogenetics with Bio.Phylo

## Overview

Bio.Phylo provides a unified toolkit for reading, writing, analyzing, and visualizing phylogenetic trees. It supports multiple file formats including Newick, NEXUS, phyloXML, NeXML, and CDAO.

## Supported File Formats

- **Newick** - Simple tree representation (most common)
- **NEXUS** - Extended format with additional data
- **phyloXML** - XML-based format with rich annotations
- **NeXML** - Modern XML format
- **CDAO** - Comparative Data Analysis Ontology

## Reading and Writing Trees

### Reading Trees

```python
from Bio import Phylo

# Read a tree from file
tree = Phylo.read("tree.nwk", "newick")

# Parse multiple trees from a file
trees = list(Phylo.parse("trees.nwk", "newick"))
print(f"Found {len(trees)} trees")
```

### Writing Trees

```python
# Write tree to file
Phylo.write(tree, "output.nwk", "newick")

# Write multiple trees
Phylo.write(trees, "output.nex", "nexus")
```

### Format Conversion

```python
# Convert between formats
count = Phylo.convert("input.nwk", "newick", "output.xml", "phyloxml")
print(f"Converted {count} trees")
```

## Tree Structure and Navigation

### Basic Tree Components

Trees consist of:
- **Clade** - A node (internal or terminal) in the tree
- **Terminal clades** - Leaves/tips (taxa)
- **Internal clades** - Internal nodes
- **Branch length** - Evolutionary distance

### Accessing Tree Properties

```python
# Tree root
root = tree.root

# Terminal nodes (leaves)
terminals = tree.get_terminals()
print(f"Number of taxa: {len(terminals)}")

# Non-terminal nodes
nonterminals = tree.get_nonterminals()
print(f"Number of internal nodes: {len(nonterminals)}")

# All clades
all_clades = list(tree.find_clades())
print(f"Total clades: {len(all_clades)}")
```

### Traversing Trees

```python
# Iterate through all clades
for clade in tree.find_clades():
    if clade.name:
        print(f"Clade: {clade.name}, Branch length: {clade.branch_length}")

# Iterate through terminals only
for terminal in tree.get_terminals():
    print(f"Taxon: {terminal.name}")

# Depth-first traversal
for clade in tree.find_clades(order="preorder"):
    print(clade.name)

# Level-order (breadth-first) traversal
for clade in tree.find_clades(order="level"):
    print(clade.name)
```

### Finding Specific Clades

```python
# Find clade by name
clade = tree.find_any(name="Species_A")

# Find all clades matching criteria
def is_long_branch(clade):
    return clade.branch_length and clade.branch_length > 0.5

long_branches = tree.find_clades(is_long_branch)
```

## Tree Analysis

### Tree Statistics

```python
# Total branch length
total_length = tree.total_branch_length()
print(f"Total tree length: {total_length:.3f}")

# Tree depth (root to furthest leaf)
depths = tree.depths()
max_depth = max(depths.values())
print(f"Maximum depth: {max_depth:.3f}")

# Terminal count
terminal_count = tree.count_terminals()
print(f"Number of taxa: {terminal_count}")
```

### Distance Calculations

```python
# Distance between two taxa
distance = tree.distance("Species_A", "Species_B")
print(f"Distance: {distance:.3f}")

# Create distance matrix
from Bio import Phylo

terminals = tree.get_terminals()
taxa_names = [t.name for t in terminals]

print("Distance Matrix:")
for taxon1 in taxa_names:
    row = []
    for taxon2 in taxa_names:
        if taxon1 == taxon2:
            row.append(0)
        else:
            dist = tree.distance(taxon1, taxon2)
            row.append(dist)
    print(f"{taxon1}: {row}")
```

### Common Ancestors

```python
# Find common ancestor of two clades
clade1 = tree.find_any(name="Species_A")
clade2 = tree.find_any(name="Species_B")
ancestor = tree.common_ancestor(clade1, clade2)
print(f"Common ancestor: {ancestor.name}")

# Find common ancestor of multiple clades
clades = [tree.find_any(name=n) for n in ["Species_A", "Species_B", "Species_C"]]
ancestor = tree.common_ancestor(*clades)
```

### Tree Comparison

```python
# Compare tree topologies
def compare_trees(tree1, tree2):
    """Compare two trees."""
    # Get terminal names
    taxa1 = set(t.name for t in tree1.get_terminals())
    taxa2 = set(t.name for t in tree2.get_terminals())

    # Check if they have same taxa
    if taxa1 != taxa2:
        return False, "Different taxa"

    # Compare distances
    differences = []
    for taxon1 in taxa1:
        for taxon2 in taxa1:
            if taxon1 < taxon2:
                dist1 = tree1.distance(taxon1, taxon2)
                dist2 = tree2.distance(taxon1, taxon2)
                if abs(dist1 - dist2) > 0.01:
                    differences.append((taxon1, taxon2, dist1, dist2))

    return len(differences) == 0, differences
```

## Tree Manipulation

### Pruning Trees

```python
# Prune (remove) specific taxa
tree_copy = tree.copy()
tree_copy.prune("Species_A")

# Keep only specific taxa
taxa_to_keep = ["Species_B", "Species_C", "Species_D"]
terminals = tree_copy.get_terminals()
for terminal in terminals:
    if terminal.name not in taxa_to_keep:
        tree_copy.prune(terminal)
```

### Collapsing Short Branches

```python
# Collapse branches shorter than threshold
def collapse_short_branches(tree, threshold=0.01):
    """Collapse branches shorter than threshold."""
    for clade in tree.find_clades():
        if clade.branch_length and clade.branch_length < threshold:
            clade.branch_length = 0
    return tree
```

### Ladderizing Trees

```python
# Ladderize tree (sort branches by size)
tree.ladderize()  # ascending order
tree.ladderize(reverse=True)  # descending order
```

### Rerooting Trees

```python
# Reroot at midpoint
tree.root_at_midpoint()

# Reroot with outgroup
outgroup = tree.find_any(name="Outgroup_Species")
tree.root_with_outgroup(outgroup)

# Reroot at internal node
internal = tree.get_nonterminals()[0]
tree.root_with_outgroup(internal)
```

## Tree Visualization

### Basic ASCII Drawing

```python
# Draw tree to console
Phylo.draw_ascii(tree)

# Draw with custom format
Phylo.draw_ascii(tree, column_width=80)
```

### Matplotlib Visualization

```python
import matplotlib.pyplot as plt
from Bio import Phylo

# Simple plot
fig = plt.figure(figsize=(10, 8))
axes = fig.add_subplot(1, 1, 1)
Phylo.draw(tree, axes=axes)
plt.show()

# Customize plot
fig = plt.figure(figsize=(10, 8))
axes = fig.add_subplot(1, 1, 1)
Phylo.draw(tree, axes=axes, do_show=False)
axes.set_title("Phylogenetic Tree")
plt.tight_layout()
plt.savefig("tree.png", dpi=300)
```

### Advanced Visualization Options

```python
# Radial (circular) tree
Phylo.draw(tree, branch_labels=lambda c: c.branch_length)

# Show branch support values
Phylo.draw(tree, label_func=lambda n: str(n.confidence) if n.confidence else "")

# Color branches
def color_by_length(clade):
    if clade.branch_length:
        if clade.branch_length > 0.5:
            return "red"
        elif clade.branch_length > 0.2:
            return "orange"
    return "black"

# Note: Direct branch coloring requires custom matplotlib code
```

## Building Trees

### From Distance Matrix

```python
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor, DistanceMatrix

# Create distance matrix
dm = DistanceMatrix(
    names=["Alpha", "Beta", "Gamma", "Delta"],
    matrix=[
        [],
        [0.23],
        [0.45, 0.34],
        [0.67, 0.58, 0.29]
    ]
)

# Build tree using UPGMA
constructor = DistanceTreeConstructor()
tree = constructor.upgma(dm)
Phylo.draw_ascii(tree)

# Build tree using Neighbor-Joining
tree = constructor.nj(dm)
```

### From Multiple Sequence Alignment

```python
from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

# Read alignment
alignment = AlignIO.read("alignment.fasta", "fasta")

# Calculate distance matrix
calculator = DistanceCalculator("identity")
distance_matrix = calculator.get_distance(alignment)

# Build tree
constructor = DistanceTreeConstructor()
tree = constructor.upgma(distance_matrix)

# Write tree
Phylo.write(tree, "output_tree.nwk", "newick")
```

### Distance Models

Available distance calculation models:
- **identity** - Simple identity
- **blastn** - BLASTN identity
- **trans** - Transition/transversion ratio
- **blosum62** - BLOSUM62 matrix
- **pam250** - PAM250 matrix

```python
# Use different model
calculator = DistanceCalculator("blosum62")
dm = calculator.get_distance(alignment)
```

## Consensus Trees

```python
from Bio.Phylo.Consensus import majority_consensus, strict_consensus

# Read multiple trees
trees = list(Phylo.parse("bootstrap_trees.nwk", "newick"))

# Majority-rule consensus
consensus = majority_consensus(trees, cutoff=0.5)

# Strict consensus
strict_cons = strict_consensus(trees)

# Write consensus tree
Phylo.write(consensus, "consensus.nwk", "newick")
```

## PhyloXML Features

PhyloXML format supports rich annotations:

```python
from Bio.Phylo.PhyloXML import Phylogeny, Clade

# Create PhyloXML tree
tree = Phylogeny(rooted=True)
tree.name = "Example Tree"
tree.description = "A sample phylogenetic tree"

# Add clades with rich annotations
clade = Clade(branch_length=0.5)
clade.name = "Species_A"
clade.color = "red"
clade.width = 2.0

# Add taxonomy information
from Bio.Phylo.PhyloXML import Taxonomy
taxonomy = Taxonomy(scientific_name="Homo sapiens", common_name="Human")
clade.taxonomies.append(taxonomy)
```

## Bootstrap Support

```python
# Add bootstrap support values to tree
def add_bootstrap_support(tree, support_values):
    """Add bootstrap support to internal nodes."""
    internal_nodes = tree.get_nonterminals()
    for node, support in zip(internal_nodes, support_values):
        node.confidence = support
    return tree

# Example
support_values = [95, 87, 76, 92]
tree_with_support = add_bootstrap_support(tree, support_values)
```

## Best Practices

1. **Choose appropriate file format** - Newick for simple trees, phyloXML for annotations
2. **Validate tree topology** - Check for polytomies and negative branch lengths
3. **Root trees appropriately** - Use midpoint or outgroup rooting
4. **Handle bootstrap values** - Store as clade confidence
5. **Consider tree size** - Large trees may need special handling
6. **Use tree copies** - Call `.copy()` before modifications
7. **Export publication-ready figures** - Use matplotlib for high-quality output
8. **Document tree construction** - Record alignment and parameters used
9. **Compare multiple trees** - Use consensus methods for bootstrap trees
10. **Validate taxon names** - Ensure consistent naming across files

## Common Use Cases

### Build Tree from Sequences

```python
from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

# Read aligned sequences
alignment = AlignIO.read("sequences.aln", "clustal")

# Calculate distances
calculator = DistanceCalculator("identity")
dm = calculator.get_distance(alignment)

# Build neighbor-joining tree
constructor = DistanceTreeConstructor()
tree = constructor.nj(dm)

# Root at midpoint
tree.root_at_midpoint()

# Save tree
Phylo.write(tree, "tree.nwk", "newick")

# Visualize
import matplotlib.pyplot as plt
fig = plt.figure(figsize=(10, 8))
Phylo.draw(tree)
plt.show()
```

### Extract Subtree

```python
def extract_subtree(tree, taxa_list):
    """Extract subtree containing specific taxa."""
    # Create a copy
    subtree = tree.copy()

    # Get all terminals
    all_terminals = subtree.get_terminals()

    # Prune taxa not in list
    for terminal in all_terminals:
        if terminal.name not in taxa_list:
            subtree.prune(terminal)

    return subtree

# Use it
subtree = extract_subtree(tree, ["Species_A", "Species_B", "Species_C"])
Phylo.write(subtree, "subtree.nwk", "newick")
```

### Calculate Phylogenetic Diversity

```python
def phylogenetic_diversity(tree, taxa_subset=None):
    """Calculate phylogenetic diversity (sum of branch lengths)."""
    if taxa_subset:
        # Prune to subset
        tree = extract_subtree(tree, taxa_subset)

    # Sum all branch lengths
    total = 0
    for clade in tree.find_clades():
        if clade.branch_length:
            total += clade.branch_length

    return total

# Calculate PD for all taxa
pd_all = phylogenetic_diversity(tree)
print(f"Total phylogenetic diversity: {pd_all:.3f}")

# Calculate PD for subset
pd_subset = phylogenetic_diversity(tree, ["Species_A", "Species_B"])
print(f"Subset phylogenetic diversity: {pd_subset:.3f}")
```

### Annotate Tree with External Data

```python
def annotate_tree_from_csv(tree, csv_file):
    """Annotate tree leaves with data from CSV."""
    import csv

    # Read annotation data
    annotations = {}
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            annotations[row["species"]] = row

    # Annotate tree
    for terminal in tree.get_terminals():
        if terminal.name in annotations:
            # Add custom attributes
            for key, value in annotations[terminal.name].items():
                setattr(terminal, key, value)

    return tree
```

### Compare Tree Topologies

```python
def robinson_foulds_distance(tree1, tree2):
    """Calculate Robinson-Foulds distance between two trees."""
    # Get bipartitions for each tree
    def get_bipartitions(tree):
        bipartitions = set()
        for clade in tree.get_nonterminals():
            terminals = frozenset(t.name for t in clade.get_terminals())
            bipartitions.add(terminals)
        return bipartitions

    bp1 = get_bipartitions(tree1)
    bp2 = get_bipartitions(tree2)

    # Symmetric difference
    diff = len(bp1.symmetric_difference(bp2))
    return diff

# Use it
tree1 = Phylo.read("tree1.nwk", "newick")
tree2 = Phylo.read("tree2.nwk", "newick")
rf_dist = robinson_foulds_distance(tree1, tree2)
print(f"Robinson-Foulds distance: {rf_dist}")
```

### `references/sequence_io.md`

# Sequence Handling with Bio.Seq and Bio.SeqIO

## Overview

Bio.Seq provides the `Seq` object for biological sequences with specialized methods, while Bio.SeqIO offers a unified interface for reading, writing, and converting sequence files across multiple formats.

## The Seq Object

### Creating Sequences

```python
from Bio.Seq import Seq

# Create a basic sequence
my_seq = Seq("AGTACACTGGT")

# Sequences support string-like operations
print(len(my_seq))  # Length
print(my_seq[0:5])  # Slicing
```

### Core Sequence Operations

```python
# Complement and reverse complement
complement = my_seq.complement()
rev_comp = my_seq.reverse_complement()

# Transcription (DNA to RNA)
rna = my_seq.transcribe()

# Translation (to protein)
protein = my_seq.translate()

# Back-transcription (RNA to DNA)
dna = rna_seq.back_transcribe()
```

### Sequence Methods

- `complement()` - Returns complementary strand
- `reverse_complement()` - Returns reverse complement
- `transcribe()` - DNA to RNA transcription
- `back_transcribe()` - RNA to DNA conversion
- `translate()` - Translate to protein sequence
- `translate(table=N)` - Use specific genetic code table
- `translate(to_stop=True)` - Stop at first stop codon

## Bio.SeqIO: Sequence File I/O

### Core Functions

**Bio.SeqIO.parse()**: The primary workhorse for reading sequence files as an iterator of `SeqRecord` objects.

```python
from Bio import SeqIO

# Parse a FASTA file
for record in SeqIO.parse("sequences.fasta", "fasta"):
    print(record.id)
    print(record.seq)
    print(len(record))
```

**Bio.SeqIO.read()**: For single-record files (validates exactly one record exists).

```python
record = SeqIO.read("single.fasta", "fasta")
```

**Bio.SeqIO.write()**: Output SeqRecord objects to files.

```python
# Write records to file
count = SeqIO.write(seq_records, "output.fasta", "fasta")
print(f"Wrote {count} records")
```

**Bio.SeqIO.convert()**: Streamlined format conversion.

```python
# Convert between formats
count = SeqIO.convert("input.gbk", "genbank", "output.fasta", "fasta")
```

### Supported File Formats

Common formats include:
- **fasta** - FASTA format
- **fastq** - FASTQ format (with quality scores)
- **genbank** or **gb** - GenBank format
- **embl** - EMBL format
- **swiss** - SwissProt format
- **fasta-2line** - FASTA with sequence on one line
- **fasta-pearson** - Pearson FASTA with comment lines before the first record
- **fasta-blast** - BLAST-style FASTA where `#`, `;`, or `!` comment lines are ignored
- **tab** - Simple tab-separated format

**Biopython 1.87 note:** `format="fasta"` no longer accepts comment lines before the first `>` record. If you need to parse FASTA files with leading comments, use `format="fasta-pearson"` or `format="fasta-blast"` depending on the source convention.

### The SeqRecord Object

`SeqRecord` objects combine sequence data with annotations:

```python
record.id          # Primary identifier
record.name        # Short name
record.description # Description line
record.seq         # The actual sequence (Seq object)
record.annotations # Dictionary of additional info
record.features    # List of SeqFeature objects
record.letter_annotations  # Per-letter annotations (e.g., quality scores)
```

### Modifying Records

```python
# Modify record attributes
record.id = "new_id"
record.description = "New description"

# Extract subsequences
sub_record = record[10:30]  # Slicing preserves annotations

# Modify sequence
record.seq = record.seq.reverse_complement()
```

## Working with Large Files

### Memory-Efficient Parsing

Use iterators to avoid loading entire files into memory:

```python
# Good for large files
for record in SeqIO.parse("large_file.fasta", "fasta"):
    if len(record.seq) > 1000:
        print(record.id)
```

### Dictionary-Based Access

Three approaches for random access:

**1. Bio.SeqIO.to_dict()** - Loads all records into memory:

```python
seq_dict = SeqIO.to_dict(SeqIO.parse("sequences.fasta", "fasta"))
record = seq_dict["sequence_id"]
```

**2. Bio.SeqIO.index()** - Lazy-loaded dictionary (memory efficient):

```python
seq_index = SeqIO.index("sequences.fasta", "fasta")
record = seq_index["sequence_id"]
seq_index.close()
```

**3. Bio.SeqIO.index_db()** - SQLite-based index for very large files:

```python
seq_index = SeqIO.index_db("index.idx", "sequences.fasta", "fasta")
record = seq_index["sequence_id"]
seq_index.close()
```

### Low-Level Parsers for High Performance

For high-throughput sequencing data, use low-level parsers that return tuples instead of objects:

```python
from Bio.SeqIO.FastaIO import SimpleFastaParser

with open("sequences.fasta") as handle:
    for title, sequence in SimpleFastaParser(handle):
        print(title, len(sequence))

from Bio.SeqIO.QualityIO import FastqGeneralIterator

with open("reads.fastq") as handle:
    for title, sequence, quality in FastqGeneralIterator(handle):
        print(title)
```

## Compressed Files

Bio.SeqIO automatically handles compressed files:

```python
# Works with gzip compression
for record in SeqIO.parse("sequences.fasta.gz", "fasta"):
    print(record.id)

# BGZF format for random access
from Bio import bgzf
with bgzf.open("sequences.fasta.bgz", "r") as handle:
    records = SeqIO.parse(handle, "fasta")
```

## Data Extraction Patterns

### Extract Specific Information

```python
# Get all IDs
ids = [record.id for record in SeqIO.parse("file.fasta", "fasta")]

# Get sequences above length threshold
long_seqs = [record for record in SeqIO.parse("file.fasta", "fasta")
             if len(record.seq) > 500]

# Extract organism from GenBank
for record in SeqIO.parse("file.gbk", "genbank"):
    organism = record.annotations.get("organism", "Unknown")
    print(f"{record.id}: {organism}")
```

### Filter and Write

```python
# Filter sequences by criteria
long_sequences = (record for record in SeqIO.parse("input.fasta", "fasta")
                  if len(record) > 500)
SeqIO.write(long_sequences, "filtered.fasta", "fasta")
```

## Best Practices

1. **Use iterators** for large files rather than loading everything into memory
2. **Prefer index()** for repeated random access to large files
3. **Use index_db()** for millions of records or multi-file scenarios
4. **Use low-level parsers** for high-throughput data when speed is critical
5. **Download once, reuse locally** rather than repeated network access
6. **Close indexed files** explicitly or use context managers
7. **Validate input** before writing with SeqIO.write()
8. **Use appropriate format strings** - always lowercase (e.g., "fasta", not "FASTA")

## Common Use Cases

### Format Conversion

```python
# GenBank to FASTA
SeqIO.convert("input.gbk", "genbank", "output.fasta", "fasta")

# Multiple format conversion
for fmt in ["fasta", "genbank", "embl"]:
    SeqIO.convert("input.fasta", "fasta", f"output.{fmt}", fmt)
```

### Quality Filtering (FASTQ)

```python
from Bio import SeqIO

good_reads = (record for record in SeqIO.parse("reads.fastq", "fastq")
              if min(record.letter_annotations["phred_quality"]) >= 20)
count = SeqIO.write(good_reads, "filtered.fastq", "fastq")
```

### Sequence Statistics

```python
from Bio.SeqUtils import gc_fraction

for record in SeqIO.parse("sequences.fasta", "fasta"):
    gc = gc_fraction(record.seq)
    print(f"{record.id}: GC={gc:.2%}, Length={len(record)}")
```

### Creating Records Programmatically

```python
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# Create a new record
new_record = SeqRecord(
    Seq("ATGCGATCGATCG"),
    id="seq001",
    name="MySequence",
    description="Test sequence"
)

# Write to file
SeqIO.write([new_record], "new.fasta", "fasta")
```

### `references/structure.md`

# Structural Bioinformatics with Bio.PDB

## Overview

Bio.PDB provides tools for working with macromolecular 3D structures from PDB and mmCIF files. The module uses the SMCRA (Structure/Model/Chain/Residue/Atom) architecture to represent protein structures hierarchically.

## SMCRA Architecture

The Bio.PDB module organizes structures hierarchically:

```
Structure
  └── Model       (multiple models for NMR structures)
      └── Chain   (e.g., chain A, B, C)
          └── Residue  (amino acids, nucleotides, heteroatoms)
              └── Atom (individual atoms)
```

## Parsing Structure Files

### PDB Format

```python
from Bio.PDB import PDBParser

# Create parser
parser = PDBParser(QUIET=True)  # QUIET=True suppresses warnings

# Parse structure
structure = parser.get_structure("1crn", "1crn.pdb")

# Access basic information
print(f"Structure ID: {structure.id}")
print(f"Number of models: {len(structure)}")
```

### mmCIF Format

mmCIF format is more modern and handles large structures better:

```python
from Bio.PDB import MMCIFParser

# Create parser
parser = MMCIFParser(QUIET=True)

# Parse structure
structure = parser.get_structure("1crn", "1crn.cif")
```

### Download from PDB

```python
from Bio.PDB import PDBList

# Create PDB list object
pdbl = PDBList()

# Download PDB file
pdbl.retrieve_pdb_file("1CRN", file_format="pdb", pdir="structures/")

# Download mmCIF file
pdbl.retrieve_pdb_file("1CRN", file_format="mmCif", pdir="structures/")

# Download obsolete structure
pdbl.retrieve_pdb_file("1CRN", obsolete=True, pdir="structures/")
```

## Navigating Structure Hierarchy

### Access Models

```python
# Get first model
model = structure[0]

# Iterate through all models
for model in structure:
    print(f"Model {model.id}")
```

### Access Chains

```python
# Get specific chain
chain = model["A"]

# Iterate through all chains
for chain in model:
    print(f"Chain {chain.id}")
```

### Access Residues

```python
# Iterate through residues in a chain
for residue in chain:
    print(f"Residue: {residue.resname} {residue.id[1]}")

# Get specific residue by ID
# Residue ID is tuple: (hetfield, sequence_id, insertion_code)
residue = chain[(" ", 10, " ")]  # Standard amino acid at position 10
```

### Access Atoms

```python
# Iterate through atoms in a residue
for atom in residue:
    print(f"Atom: {atom.name}, Coordinates: {atom.coord}")

# Get specific atom
ca_atom = residue["CA"]  # Alpha carbon
print(f"CA coordinates: {ca_atom.coord}")
```

### Alternative Access Patterns

```python
# Direct access through hierarchy
atom = structure[0]["A"][10]["CA"]

# Get all atoms
atoms = list(structure.get_atoms())
print(f"Total atoms: {len(atoms)}")

# Get all residues
residues = list(structure.get_residues())

# Get all chains
chains = list(structure.get_chains())
```

## Working with Atom Coordinates

### Accessing Coordinates

```python
# Get atom coordinates
coord = atom.coord
print(f"X: {coord[0]}, Y: {coord[1]}, Z: {coord[2]}")

# Get B-factor (temperature factor)
b_factor = atom.bfactor

# Get occupancy
occupancy = atom.occupancy

# Get element
element = atom.element
```

### Calculate Distances

```python
from Bio.PDB import Vector

# Calculate distance between two atoms
atom1 = residue1["CA"]
atom2 = residue2["CA"]

distance = atom1 - atom2  # Returns distance in Angstroms
print(f"Distance: {distance:.2f} Å")
```

### Calculate Angles

```python
from Bio.PDB.vectors import calc_angle

# Calculate angle between three atoms
angle = calc_angle(
    atom1.get_vector(),
    atom2.get_vector(),
    atom3.get_vector()
)
print(f"Angle: {angle:.2f} radians")
```

### Calculate Dihedrals

```python
from Bio.PDB.vectors import calc_dihedral

# Calculate dihedral angle between four atoms
dihedral = calc_dihedral(
    atom1.get_vector(),
    atom2.get_vector(),
    atom3.get_vector(),
    atom4.get_vector()
)
print(f"Dihedral: {dihedral:.2f} radians")
```

## Structure Analysis

### Secondary Structure (DSSP)

DSSP assigns secondary structure to protein structures:

```python
from Bio.PDB import DSSP, PDBParser

# Parse structure
parser = PDBParser()
structure = parser.get_structure("1crn", "1crn.pdb")

# Run DSSP (requires DSSP executable installed)
model = structure[0]
dssp = DSSP(model, "1crn.pdb")

# Access results
for residue_key in dssp:
    dssp_data = dssp[residue_key]
    residue_id = residue_key[1]
    ss = dssp_data[2]  # Secondary structure code
    phi = dssp_data[4]  # Phi angle
    psi = dssp_data[5]  # Psi angle
    print(f"Residue {residue_id}: {ss}, φ={phi:.1f}°, ψ={psi:.1f}°")
```

Secondary structure codes:
- `H` - Alpha helix
- `B` - Beta bridge
- `E` - Strand
- `G` - 3-10 helix
- `I` - Pi helix
- `T` - Turn
- `S` - Bend
- `-` - Coil/loop

### Solvent Accessibility (DSSP)

```python
# Get relative solvent accessibility
for residue_key in dssp:
    acc = dssp[residue_key][3]  # Relative accessibility
    print(f"Residue {residue_key[1]}: {acc:.2f} relative accessibility")
```

### Neighbor Search

Find nearby atoms efficiently:

```python
from Bio.PDB import NeighborSearch

# Get all atoms
atoms = list(structure.get_atoms())

# Create neighbor search object
ns = NeighborSearch(atoms)

# Find atoms within radius
center_atom = structure[0]["A"][10]["CA"]
nearby_atoms = ns.search(center_atom.coord, 5.0)  # 5 Å radius
print(f"Found {len(nearby_atoms)} atoms within 5 Å")

# Find residues within radius
nearby_residues = ns.search(center_atom.coord, 5.0, level="R")

# Find chains within radius
nearby_chains = ns.search(center_atom.coord, 10.0, level="C")
```

### Contact Map

```python
def calculate_contact_map(chain, distance_threshold=8.0):
    """Calculate residue-residue contact map."""
    residues = list(chain.get_residues())
    n = len(residues)
    contact_map = [[0] * n for _ in range(n)]

    for i, res1 in enumerate(residues):
        for j, res2 in enumerate(residues):
            if i < j:
                # Get CA atoms
                if res1.has_id("CA") and res2.has_id("CA"):
                    dist = res1["CA"] - res2["CA"]
                    if dist < distance_threshold:
                        contact_map[i][j] = 1
                        contact_map[j][i] = 1

    return contact_map
```

## Structure Quality Assessment

### Ramachandran Plot Data

```python
from Bio.PDB import Polypeptide

def get_phi_psi(structure):
    """Extract phi and psi angles for Ramachandran plot."""
    phi_psi = []

    for model in structure:
        for chain in model:
            polypeptides = Polypeptide.PPBuilder().build_peptides(chain)
            for poly in polypeptides:
                angles = poly.get_phi_psi_list()
                for residue, (phi, psi) in zip(poly, angles):
                    if phi and psi:  # Skip None values
                        phi_psi.append((residue.resname, phi, psi))

    return phi_psi
```

### Check for Missing Atoms

```python
def check_missing_atoms(structure):
    """Identify residues with missing atoms."""
    missing = []

    for residue in structure.get_residues():
        if residue.id[0] == " ":  # Standard amino acid
            resname = residue.resname

            # Expected backbone atoms
            expected = ["N", "CA", "C", "O"]

            for atom_name in expected:
                if not residue.has_id(atom_name):
                    missing.append((residue.full_id, atom_name))

    return missing
```

## Structure Manipulation

### Select Specific Atoms

```python
from Bio.PDB import Select

class CASelect(Select):
    """Select only CA atoms."""
    def accept_atom(self, atom):
        return atom.name == "CA"

class ChainASelect(Select):
    """Select only chain A."""
    def accept_chain(self, chain):
        return chain.id == "A"

# Use with PDBIO
from Bio.PDB import PDBIO

io = PDBIO()
io.set_structure(structure)
io.save("ca_only.pdb", CASelect())
io.save("chain_a.pdb", ChainASelect())
```

### Transform Structures

```python
import numpy as np

# Rotate structure
from Bio.PDB.vectors import rotaxis

# Define rotation axis and angle
axis = Vector(1, 0, 0)  # X-axis
angle = np.pi / 4  # 45 degrees

# Create rotation matrix
rotation = rotaxis(angle, axis)

# Apply rotation to all atoms
for atom in structure.get_atoms():
    atom.transform(rotation, Vector(0, 0, 0))
```

### Superimpose Structures

```python
from Bio.PDB import Superimposer, PDBParser

# Parse two structures
parser = PDBParser()
structure1 = parser.get_structure("ref", "reference.pdb")
structure2 = parser.get_structure("mov", "mobile.pdb")

# Get CA atoms from both structures
ref_atoms = [atom for atom in structure1.get_atoms() if atom.name == "CA"]
mov_atoms = [atom for atom in structure2.get_atoms() if atom.name == "CA"]

# Superimpose
super_imposer = Superimposer()
super_imposer.set_atoms(ref_atoms, mov_atoms)

# Apply transformation
super_imposer.apply(structure2.get_atoms())

# Get RMSD
rmsd = super_imposer.rms
print(f"RMSD: {rmsd:.2f} Å")

# Save superimposed structure
from Bio.PDB import PDBIO
io = PDBIO()
io.set_structure(structure2)
io.save("superimposed.pdb")
```

## Writing Structure Files

### Save PDB Files

```python
from Bio.PDB import PDBIO

io = PDBIO()
io.set_structure(structure)
io.save("output.pdb")
```

### Save mmCIF Files

```python
from Bio.PDB import MMCIFIO

io = MMCIFIO()
io.set_structure(structure)
io.save("output.cif")
```

## Sequence from Structure

### Extract Sequence

```python
from Bio.PDB import Polypeptide

# Get polypeptides from structure
ppb = Polypeptide.PPBuilder()

for model in structure:
    for chain in model:
        for pp in ppb.build_peptides(chain):
            sequence = pp.get_sequence()
            print(f"Chain {chain.id}: {sequence}")
```

### Map to FASTA

```python
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

# Extract sequences and create FASTA
records = []
ppb = Polypeptide.PPBuilder()

for model in structure:
    for chain in model:
        for pp in ppb.build_peptides(chain):
            seq_record = SeqRecord(
                pp.get_sequence(),
                id=f"{structure.id}_{chain.id}",
                description=f"Chain {chain.id}"
            )
            records.append(seq_record)

SeqIO.write(records, "structure_sequences.fasta", "fasta")
```

## Best Practices

1. **Use mmCIF** for large structures and modern data
2. **Set QUIET=True** to suppress parser warnings
3. **Check for missing atoms** before analysis
4. **Use NeighborSearch** for efficient spatial queries
5. **Validate structure quality** with DSSP or Ramachandran analysis
6. **Handle multiple models** appropriately (NMR structures)
7. **Be aware of heteroatoms** - they have different residue IDs
8. **Use Select classes** for targeted structure output
9. **Cache downloaded structures** locally
10. **Consider alternative conformations** - some residues have multiple positions

## Common Use Cases

### Calculate RMSD Between Structures

```python
from Bio.PDB import PDBParser, Superimposer

parser = PDBParser()
structure1 = parser.get_structure("s1", "structure1.pdb")
structure2 = parser.get_structure("s2", "structure2.pdb")

# Get CA atoms
atoms1 = [atom for atom in structure1[0]["A"].get_atoms() if atom.name == "CA"]
atoms2 = [atom for atom in structure2[0]["A"].get_atoms() if atom.name == "CA"]

# Ensure same number of atoms
min_len = min(len(atoms1), len(atoms2))
atoms1 = atoms1[:min_len]
atoms2 = atoms2[:min_len]

# Calculate RMSD
sup = Superimposer()
sup.set_atoms(atoms1, atoms2)
print(f"RMSD: {sup.rms:.3f} Å")
```

### Find Binding Site Residues

```python
def find_binding_site(structure, ligand_chain, ligand_res_id, distance=5.0):
    """Find residues near a ligand."""
    from Bio.PDB import NeighborSearch

    # Get ligand atoms
    ligand = structure[0][ligand_chain][ligand_res_id]
    ligand_atoms = list(ligand.get_atoms())

    # Get all protein atoms
    protein_atoms = []
    for chain in structure[0]:
        if chain.id != ligand_chain:
            for residue in chain:
                if residue.id[0] == " ":  # Standard residue
                    protein_atoms.extend(residue.get_atoms())

    # Find nearby atoms
    ns = NeighborSearch(protein_atoms)
    binding_site = set()

    for ligand_atom in ligand_atoms:
        nearby = ns.search(ligand_atom.coord, distance, level="R")
        binding_site.update(nearby)

    return list(binding_site)
```

### Calculate Center of Mass

```python
import numpy as np

def center_of_mass(entity):
    """Calculate center of mass for structure entity."""
    masses = []
    coords = []

    # Atomic masses (simplified)
    mass_dict = {"C": 12.0, "N": 14.0, "O": 16.0, "S": 32.0}

    for atom in entity.get_atoms():
        mass = mass_dict.get(atom.element, 12.0)
        masses.append(mass)
        coords.append(atom.coord)

    masses = np.array(masses)
    coords = np.array(coords)

    com = np.sum(coords * masses[:, np.newaxis], axis=0) / np.sum(masses)
    return com
```
