---
name: bioservices
description: Email for NCBI service identification.
---

# BioServices

## Overview

BioServices is a Python package providing programmatic access to approximately 40 bioinformatics web services and databases. Retrieve biological data, perform cross-database queries, map identifiers, analyze sequences, and integrate multiple biological resources in Python workflows. The package handles both REST and SOAP/WSDL protocols transparently.

**Version note:** Examples target **bioservices 1.16.0** (PyPI, Mar 2026). Requires **Python 3.9–3.12**. UniProt REST changes in mid-2022 (bioservices ≥1.10) mainly affect tabular `columns` names — see upstream `_legacy_names` if parsing breaks. ChEMBL wrappers changed at 1.6.0 (2018 API); use `get_similarity`, `get_substructure`, `get_molecule` instead of pre-1.6 method names.

## When to Use This Skill

This skill should be used when:
- Retrieving protein sequences, annotations, or structures from UniProt, PDB, Pfam
- Analyzing metabolic pathways and gene functions via KEGG or Reactome
- Searching compound databases (ChEBI, ChEMBL, PubChem) for chemical information
- Converting identifiers between different biological databases (KEGG↔UniProt, compound IDs)
- Running sequence similarity searches (BLAST, MUSCLE alignment)
- Querying gene ontology terms (QuickGO, GO annotations)
- Accessing protein-protein interaction data (PSICQUIC, IntactComplex)
- Mining genomic data (BioMart, ArrayExpress, ENA)
- Integrating data from multiple bioinformatics resources in a single workflow

## Core Capabilities

### 1. Protein Analysis

Retrieve protein information, sequences, and functional annotations:

```python
from bioservices import UniProt

u = UniProt(verbose=False)

# Search for protein by name
results = u.search("ZAP70_HUMAN", frmt="tab", columns="id,genes,organism")

# Retrieve FASTA sequence
sequence = u.retrieve("P43403", "fasta")

# Map identifiers between databases
kegg_ids = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query="P43403")
```

**Key methods:**
- `search()`: Query UniProt with flexible search terms
- `retrieve()`: Get protein entries in various formats (FASTA, XML, tab)
- `mapping()`: Convert identifiers between databases

Reference: `references/services_reference.md` for complete UniProt API details.

### 2. Pathway Discovery and Analysis

Access KEGG pathway information for genes and organisms:

```python
from bioservices import KEGG

k = KEGG()
k.organism = "hsa"  # Set to human

# Search for organisms
k.lookfor_organism("droso")  # Find Drosophila species

# Find pathways by name
k.lookfor_pathway("B cell")  # Returns matching pathway IDs

# Get pathways containing specific genes
pathways = k.get_pathway_by_gene("7535", "hsa")  # ZAP70 gene

# Retrieve and parse pathway data
data = k.get("hsa04660")
parsed = k.parse(data)

# Extract pathway interactions
interactions = k.parse_kgml_pathway("hsa04660")
relations = interactions['relations']  # Protein-protein interactions

# Convert to Simple Interaction Format
sif_data = k.pathway2sif("hsa04660")
```

**Key methods:**
- `lookfor_organism()`, `lookfor_pathway()`: Search by name
- `get_pathway_by_gene()`: Find pathways containing genes
- `parse_kgml_pathway()`: Extract structured pathway data
- `pathway2sif()`: Get protein interaction networks

Reference: `references/workflow_patterns.md` for complete pathway analysis workflows.

### 3. Compound Database Searches

Search and cross-reference compounds across multiple databases:

```python
from bioservices import KEGG, UniChem

k = KEGG()

# Search compounds by name
results = k.find("compound", "Geldanamycin")  # Returns cpd:C11222

# Get compound information with database links
compound_info = k.get("cpd:C11222")  # Includes ChEBI links

# Cross-reference KEGG → ChEMBL using UniChem
u = UniChem()
chembl_id = u.get_compound_id_from_kegg("C11222")  # Returns CHEMBL278315
```

**Version caveat:** the per-source `get_compound_id_from_*` helpers are gone from
bioservices 1.16.0 — check `hasattr(u, "get_compound_id_from_kegg")` first, and
otherwise use the current UniChem API (`u.get_compounds(compound, source_type)`
and read `res["compounds"][0]["sources"]`). ChEMBL lookups follow the same rule:
`get_molecule`, not the pre-1.6 `get_compound_by_chemblId`.

**Common workflow:**
1. Search compound by name in KEGG
2. Extract KEGG compound ID
3. Use UniChem for KEGG → ChEMBL mapping
4. ChEBI IDs are often provided in KEGG entries

Reference: `references/identifier_mapping.md` for complete cross-database mapping guide.

### 4. Sequence Analysis

Run BLAST searches and sequence alignments. NCBI requires a contact email — prefer the `NCBI_EMAIL` environment variable (same convention as BioPython Entrez and other repo skills):

```python
import os
from bioservices import NCBIblast

s = NCBIblast(verbose=False)
email = os.environ["NCBI_EMAIL"]  # set before running: export NCBI_EMAIL=you@lab.org

# Run BLASTP against UniProtKB
jobid = s.run(
    program="blastp",
    sequence=protein_sequence,
    stype="protein",
    database="uniprotkb",
    email=email,
)

# Check job status and retrieve results
s.getStatus(jobid)
results = s.getResult(jobid, "out")
```

**Note:** BLAST jobs are asynchronous. Check status before retrieving results.

### 5. Identifier Mapping

Convert identifiers between different biological databases:

```python
from bioservices import UniProt, KEGG

# UniProt mapping (many database pairs supported)
u = UniProt()
results = u.mapping(
    fr="UniProtKB_AC-ID",  # Source database
    to="KEGG",              # Target database
    query="P43403"          # Identifier(s) to convert
)

# KEGG gene ID → UniProt
kegg_to_uniprot = u.mapping(fr="KEGG", to="UniProtKB_AC-ID", query="hsa:7535")

# For compounds, use UniChem
from bioservices import UniChem
u = UniChem()
chembl_from_kegg = u.get_compound_id_from_kegg("C11222")
```

**Supported mappings (UniProt):**
- UniProtKB ↔ KEGG
- UniProtKB ↔ Ensembl
- UniProtKB ↔ PDB
- UniProtKB ↔ RefSeq
- And many more (see `references/identifier_mapping.md`)

### 6. Gene Ontology Queries

Access GO terms and annotations:

```python
from bioservices import QuickGO

g = QuickGO(verbose=False)

# Retrieve GO term information
term_info = g.Term("GO:0003824", frmt="obo")

# Search annotations
annotations = g.Annotation(protein="P43403", format="tsv")
```

### 7. Protein-Protein Interactions

Query interaction databases via PSICQUIC. **PSICQUIC is not shipped by every
release — it is absent from 1.16.0** — so import it defensively and fall back to
`IntactComplex`, `OmniPath`, or `STRING` when it is missing:

```python
from bioservices import PSICQUIC

s = PSICQUIC(verbose=False)

# Query specific database (e.g., MINT)
interactions = s.query("mint", "ZAP70 AND species:9606")

# List available interaction databases
databases = s.activeDBs
```

**Available databases:** MINT, IntAct, BioGRID, DIP, and 30+ others.

## Multi-Service Integration Workflows

BioServices excels at combining multiple services for comprehensive analysis. Common integration patterns:

### Complete Protein Analysis Pipeline

Execute a full protein characterization workflow:

```bash
export NCBI_EMAIL=your.email@example.com
python scripts/protein_analysis_workflow.py ZAP70_HUMAN
# Or pass email as optional second argument if NCBI_EMAIL is unset
python scripts/protein_analysis_workflow.py ZAP70_HUMAN your.email@example.com
```

This script demonstrates:
1. UniProt search for protein entry
2. FASTA sequence retrieval
3. BLAST similarity search
4. KEGG pathway discovery
5. PSICQUIC interaction mapping

### Pathway Network Analysis

Analyze all pathways for an organism:

```bash
python scripts/pathway_analysis.py hsa output_directory/
```

Extracts and analyzes:
- All pathway IDs for organism
- Protein-protein interactions per pathway
- Interaction type distributions
- Exports to CSV/SIF formats

### Cross-Database Compound Search

Map compound identifiers across databases:

```bash
python scripts/compound_cross_reference.py Geldanamycin
```

Retrieves:
- KEGG compound ID
- ChEBI identifier
- ChEMBL identifier
- Basic compound properties

### Batch Identifier Conversion

Convert multiple identifiers at once:

```bash
python scripts/batch_id_converter.py input_ids.txt --from UniProtKB_AC-ID --to KEGG
```

## Best Practices

### Output Format Handling

Different services return data in various formats:
- **XML**: Parse using BeautifulSoup (most SOAP services)
- **Tab-separated (TSV)**: Pandas DataFrames for tabular data
- **Dictionary/JSON**: Direct Python manipulation
- **FASTA**: BioPython integration for sequence analysis

### Rate Limiting and Verbosity

Control API request behavior:

```python
from bioservices import KEGG

k = KEGG(verbose=False)  # Suppress HTTP request details
k.TIMEOUT = 30  # Adjust timeout for slow connections
```

### Error Handling

Wrap service calls in try-except blocks:

```python
try:
    results = u.search("ambiguous_query")
    if results:
        # Process results
        pass
except Exception as e:
    print(f"Search failed: {e}")
```

### Organism Codes

Use standard organism abbreviations:
- `hsa`: Homo sapiens (human)
- `mmu`: Mus musculus (mouse)
- `dme`: Drosophila melanogaster
- `sce`: Saccharomyces cerevisiae (yeast)

List all organisms: `k.list("organism")` or `k.organismIds`

### Integration with Other Tools

BioServices works well with:
- **BioPython**: Sequence analysis on retrieved FASTA data
- **Pandas**: Tabular data manipulation
- **PyMOL**: 3D structure visualization (retrieve PDB IDs)
- **NetworkX**: Network analysis of pathway interactions
- **Galaxy**: Custom tool wrappers for workflow platforms

## Resources

### scripts/

Executable Python scripts demonstrating complete workflows:

- `protein_analysis_workflow.py`: End-to-end protein characterization
- `pathway_analysis.py`: KEGG pathway discovery and network extraction
- `compound_cross_reference.py`: Multi-database compound searching
- `batch_id_converter.py`: Bulk identifier mapping utility

Scripts can be executed directly or adapted for specific use cases.

### references/

Detailed documentation loaded as needed:

- `services_reference.md`: Comprehensive list of all 40+ services with methods
- `workflow_patterns.md`: Detailed multi-step analysis workflows
- `identifier_mapping.md`: Complete guide to cross-database ID conversion

Load references when working with specific services or complex integration tasks.

## Installation

```bash
uv pip install "bioservices==1.16.0"
```

Dependencies are installed automatically. Upstream CI tests Python 3.9–3.12 ([PyPI](https://pypi.org/project/bioservices/), [docs](https://bioservices.readthedocs.io/)).

## Credentials

Most services need no API key. Exceptions:

| Service | Requirement |
|---------|-------------|
| NCBI BLAST | Contact email via `NCBI_EMAIL` or `email=` in `NCBIblast.run()` |
| Some EBI services | Optional; check service docs if rate-limited |

Set once per shell session:

```bash
export NCBI_EMAIL=your.email@example.com
```

Use a real institutional or lab address — NCBI may contact you about heavy BLAST usage.

## Additional Information

For detailed API documentation and advanced features, refer to:
- Official documentation: https://bioservices.readthedocs.io/
- Source code: https://github.com/cokelaer/bioservices
- Service-specific references in `references/services_reference.md`

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/bioservices/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/identifier_mapping.md`

# BioServices: Identifier Mapping Guide

This document provides comprehensive information about converting identifiers between different biological databases using BioServices.

## Table of Contents

1. [Overview](#overview)
2. [UniProt Mapping Service](#uniprot-mapping-service)
3. [UniChem Compound Mapping](#unichem-compound-mapping)
4. [KEGG Identifier Conversions](#kegg-identifier-conversions)
5. [Common Mapping Patterns](#common-mapping-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Overview

Biological databases use different identifier systems. Cross-referencing requires mapping between these systems. BioServices provides multiple approaches:

1. **UniProt Mapping**: Comprehensive protein/gene ID conversion
2. **UniChem**: Chemical compound ID mapping
3. **KEGG**: Built-in cross-references in entries
4. **PICR**: Protein identifier cross-reference service

---

## UniProt Mapping Service

The UniProt mapping service is the most comprehensive tool for protein and gene identifier conversion.

### Basic Usage

```python
from bioservices import UniProt

u = UniProt()

# Map single ID
result = u.mapping(
    fr="UniProtKB_AC-ID",    # Source database
    to="KEGG",                # Target database
    query="P43403"            # Identifier to convert
)

print(result)
# Output: {'P43403': ['hsa:7535']}
```

### Batch Mapping

```python
# Map multiple IDs (comma-separated)
ids = ["P43403", "P04637", "P53779"]
result = u.mapping(
    fr="UniProtKB_AC-ID",
    to="KEGG",
    query=",".join(ids)
)

for uniprot_id, kegg_ids in result.items():
    print(f"{uniprot_id} → {kegg_ids}")
```

### Supported Database Pairs

UniProt supports mapping between 100+ database pairs. Key ones include:

#### Protein/Gene Databases

| Source Format | Code | Target Format | Code |
|---------------|------|---------------|------|
| UniProtKB AC/ID | `UniProtKB_AC-ID` | KEGG | `KEGG` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | Ensembl | `Ensembl` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | Ensembl Protein | `Ensembl_Protein` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | Ensembl Transcript | `Ensembl_Transcript` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | RefSeq Protein | `RefSeq_Protein` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | RefSeq Nucleotide | `RefSeq_Nucleotide` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | GeneID (Entrez) | `GeneID` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | HGNC | `HGNC` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | MGI | `MGI` |
| KEGG | `KEGG` | UniProtKB | `UniProtKB` |
| Ensembl | `Ensembl` | UniProtKB | `UniProtKB` |
| GeneID | `GeneID` | UniProtKB | `UniProtKB` |

#### Structural Databases

| Source | Code | Target | Code |
|--------|------|--------|------|
| UniProtKB AC/ID | `UniProtKB_AC-ID` | PDB | `PDB` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | Pfam | `Pfam` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | InterPro | `InterPro` |
| PDB | `PDB` | UniProtKB | `UniProtKB` |

#### Expression & Proteomics

| Source | Code | Target | Code |
|--------|------|--------|------|
| UniProtKB AC/ID | `UniProtKB_AC-ID` | PRIDE | `PRIDE` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | ProteomicsDB | `ProteomicsDB` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | PaxDb | `PaxDb` |

#### Organism-Specific

| Source | Code | Target | Code |
|--------|------|--------|------|
| UniProtKB AC/ID | `UniProtKB_AC-ID` | FlyBase | `FlyBase` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | WormBase | `WormBase` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | SGD | `SGD` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | ZFIN | `ZFIN` |

#### Other Useful Mappings

| Source | Code | Target | Code |
|--------|------|--------|------|
| UniProtKB AC/ID | `UniProtKB_AC-ID` | GO | `GO` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | Reactome | `Reactome` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | STRING | `STRING` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | BioGRID | `BioGRID` |
| UniProtKB AC/ID | `UniProtKB_AC-ID` | OMA | `OMA` |

### Complete List of Database Codes

To get the complete, up-to-date list:

```python
from bioservices import UniProt

u = UniProt()

# This information is in the UniProt REST API documentation
# Common patterns:
# - Source databases typically end in source database name
# - UniProtKB uses "UniProtKB_AC-ID" or "UniProtKB"
# - Most other databases use their standard abbreviation
```

### Common Database Codes Reference

**Gene/Protein Identifiers:**
- `UniProtKB_AC-ID`: UniProt accession/ID
- `UniProtKB`: UniProt accession
- `KEGG`: KEGG gene IDs (e.g., hsa:7535)
- `GeneID`: NCBI Gene (Entrez) IDs
- `Ensembl`: Ensembl gene IDs
- `Ensembl_Protein`: Ensembl protein IDs
- `Ensembl_Transcript`: Ensembl transcript IDs
- `RefSeq_Protein`: RefSeq protein IDs (NP_)
- `RefSeq_Nucleotide`: RefSeq nucleotide IDs (NM_)

**Gene Nomenclature:**
- `HGNC`: Human Gene Nomenclature Committee
- `MGI`: Mouse Genome Informatics
- `RGD`: Rat Genome Database
- `SGD`: Saccharomyces Genome Database
- `FlyBase`: Drosophila database
- `WormBase`: C. elegans database
- `ZFIN`: Zebrafish database

**Structure:**
- `PDB`: Protein Data Bank
- `Pfam`: Protein families
- `InterPro`: Protein domains
- `SUPFAM`: Superfamily
- `PROSITE`: Protein motifs

**Pathways & Networks:**
- `Reactome`: Reactome pathways
- `BioCyc`: BioCyc pathways
- `PathwayCommons`: Pathway Commons
- `STRING`: Protein-protein networks
- `BioGRID`: Interaction database

### Mapping Examples

#### UniProt → KEGG

```python
from bioservices import UniProt

u = UniProt()

# Single mapping
result = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query="P43403")
print(result)  # {'P43403': ['hsa:7535']}
```

#### KEGG → UniProt

```python
# Reverse mapping
result = u.mapping(fr="KEGG", to="UniProtKB", query="hsa:7535")
print(result)  # {'hsa:7535': ['P43403']}
```

#### UniProt → Ensembl

```python
# To Ensembl gene IDs
result = u.mapping(fr="UniProtKB_AC-ID", to="Ensembl", query="P43403")
print(result)  # {'P43403': ['ENSG00000115085']}

# To Ensembl protein IDs
result = u.mapping(fr="UniProtKB_AC-ID", to="Ensembl_Protein", query="P43403")
print(result)  # {'P43403': ['ENSP00000381359']}
```

#### UniProt → PDB

```python
# Find 3D structures
result = u.mapping(fr="UniProtKB_AC-ID", to="PDB", query="P04637")
print(result)  # {'P04637': ['1A1U', '1AIE', '1C26', ...]}
```

#### UniProt → RefSeq

```python
# Get RefSeq protein IDs
result = u.mapping(fr="UniProtKB_AC-ID", to="RefSeq_Protein", query="P43403")
print(result)  # {'P43403': ['NP_001070.2']}
```

#### Gene Name → UniProt (via search, then mapping)

```python
# First search for gene
search_result = u.search("gene:ZAP70 AND organism:9606", frmt="tab", columns="id")
lines = search_result.strip().split("\n")
if len(lines) > 1:
    uniprot_id = lines[1].split("\t")[0]

    # Then map to other databases
    kegg_id = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=uniprot_id)
    print(kegg_id)
```

---

## UniChem Compound Mapping

UniChem specializes in mapping chemical compound identifiers across databases.

### Source Database IDs

| Source ID | Database |
|-----------|----------|
| 1 | ChEMBL |
| 2 | DrugBank |
| 3 | PDB |
| 4 | IUPHAR/BPS Guide to Pharmacology |
| 5 | PubChem |
| 6 | KEGG |
| 7 | ChEBI |
| 8 | NIH Clinical Collection |
| 14 | FDA/SRS |
| 22 | PubChem |

### Basic Usage

```python
from bioservices import UniChem

u = UniChem()

# Get ChEMBL ID from KEGG compound ID
chembl_id = u.get_compound_id_from_kegg("C11222")
print(chembl_id)  # CHEMBL278315
```

### All Compound IDs

```python
# Get all identifiers for a compound
# src_compound_id: compound ID, src_id: source database ID
all_ids = u.get_all_compound_ids("CHEMBL278315", src_id=1)  # 1 = ChEMBL

for mapping in all_ids:
    src_name = mapping['src_name']
    src_compound_id = mapping['src_compound_id']
    print(f"{src_name}: {src_compound_id}")
```

### Specific Database Conversion

```python
# Convert between specific databases
# from_src_id=6 (KEGG), to_src_id=1 (ChEMBL)
result = u.get_src_compound_ids("C11222", from_src_id=6, to_src_id=1)
print(result)
```

### Common Compound Mappings

#### KEGG → ChEMBL

```python
u = UniChem()
chembl_id = u.get_compound_id_from_kegg("C00031")  # D-Glucose
print(f"ChEMBL: {chembl_id}")
```

#### ChEMBL → PubChem

```python
result = u.get_src_compound_ids("CHEMBL278315", from_src_id=1, to_src_id=22)
if result:
    pubchem_id = result[0]['src_compound_id']
    print(f"PubChem: {pubchem_id}")
```

#### ChEBI → DrugBank

```python
result = u.get_src_compound_ids("5292", from_src_id=7, to_src_id=2)
if result:
    drugbank_id = result[0]['src_compound_id']
    print(f"DrugBank: {drugbank_id}")
```

---

## KEGG Identifier Conversions

KEGG entries contain cross-references that can be extracted by parsing.

### Extract Database Links from KEGG Entry

```python
from bioservices import KEGG

k = KEGG()

# Get compound entry
entry = k.get("cpd:C11222")

# Parse for specific database
chebi_id = None
uniprot_ids = []

for line in entry.split("\n"):
    if "ChEBI:" in line:
        # Extract ChEBI ID
        parts = line.split("ChEBI:")
        if len(parts) > 1:
            chebi_id = parts[1].strip().split()[0]

# For genes/proteins
gene_entry = k.get("hsa:7535")
for line in gene_entry.split("\n"):
    if line.startswith("            "):  # Database links section
        if "UniProt:" in line:
            parts = line.split("UniProt:")
            if len(parts) > 1:
                uniprot_id = parts[1].strip()
                uniprot_ids.append(uniprot_id)
```

### KEGG Gene ID Components

KEGG gene IDs have format `organism:gene_id`:

```python
kegg_id = "hsa:7535"
organism, gene_id = kegg_id.split(":")

print(f"Organism: {organism}")  # hsa (human)
print(f"Gene ID: {gene_id}")    # 7535
```

### KEGG Pathway to Genes

```python
k = KEGG()

# Get pathway entry
pathway = k.get("path:hsa04660")

# Parse for gene list
genes = []
in_gene_section = False

for line in pathway.split("\n"):
    if line.startswith("GENE"):
        in_gene_section = True

    if in_gene_section:
        if line.startswith(" " * 12):  # Gene line
            parts = line.strip().split()
            if parts:
                gene_id = parts[0]
                genes.append(f"hsa:{gene_id}")
        elif not line.startswith(" "):
            break

print(f"Found {len(genes)} genes")
```

---

## Common Mapping Patterns

### Pattern 1: Gene Symbol → Multiple Database IDs

```python
from bioservices import UniProt

def gene_symbol_to_ids(gene_symbol, organism="9606"):
    """Convert gene symbol to multiple database IDs."""
    u = UniProt()

    # Search for gene
    query = f"gene:{gene_symbol} AND organism:{organism}"
    result = u.search(query, frmt="tab", columns="id")

    lines = result.strip().split("\n")
    if len(lines) < 2:
        return None

    uniprot_id = lines[1].split("\t")[0]

    # Map to multiple databases
    ids = {
        'uniprot': uniprot_id,
        'kegg': u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=uniprot_id),
        'ensembl': u.mapping(fr="UniProtKB_AC-ID", to="Ensembl", query=uniprot_id),
        'refseq': u.mapping(fr="UniProtKB_AC-ID", to="RefSeq_Protein", query=uniprot_id),
        'pdb': u.mapping(fr="UniProtKB_AC-ID", to="PDB", query=uniprot_id)
    }

    return ids

# Usage
ids = gene_symbol_to_ids("ZAP70")
print(ids)
```

### Pattern 2: Compound Name → All Database IDs

```python
from bioservices import KEGG, UniChem, ChEBI

def compound_name_to_ids(compound_name):
    """Search compound and get all database IDs."""
    k = KEGG()

    # Search KEGG
    results = k.find("compound", compound_name)
    if not results:
        return None

    # Extract KEGG ID
    kegg_id = results.strip().split("\n")[0].split("\t")[0].replace("cpd:", "")

    # Get KEGG entry for ChEBI
    entry = k.get(f"cpd:{kegg_id}")
    chebi_id = None
    for line in entry.split("\n"):
        if "ChEBI:" in line:
            parts = line.split("ChEBI:")
            if len(parts) > 1:
                chebi_id = parts[1].strip().split()[0]
                break

    # Get ChEMBL from UniChem
    u = UniChem()
    try:
        chembl_id = u.get_compound_id_from_kegg(kegg_id)
    except:
        chembl_id = None

    return {
        'kegg': kegg_id,
        'chebi': chebi_id,
        'chembl': chembl_id
    }

# Usage
ids = compound_name_to_ids("Geldanamycin")
print(ids)
```

### Pattern 3: Batch ID Conversion with Error Handling

```python
from bioservices import UniProt

def safe_batch_mapping(ids, from_db, to_db, chunk_size=100):
    """Safely map IDs with error handling and chunking."""
    u = UniProt()
    all_results = {}

    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i+chunk_size]
        query = ",".join(chunk)

        try:
            results = u.mapping(fr=from_db, to=to_db, query=query)
            all_results.update(results)
            print(f"✓ Processed {min(i+chunk_size, len(ids))}/{len(ids)}")

        except Exception as e:
            print(f"✗ Error at chunk {i}: {e}")

            # Try individual IDs in failed chunk
            for single_id in chunk:
                try:
                    result = u.mapping(fr=from_db, to=to_db, query=single_id)
                    all_results.update(result)
                except:
                    all_results[single_id] = None

    return all_results

# Usage
uniprot_ids = ["P43403", "P04637", "P53779", "INVALID123"]
mapping = safe_batch_mapping(uniprot_ids, "UniProtKB_AC-ID", "KEGG")
```

### Pattern 4: Multi-Hop Mapping

Sometimes you need to map through intermediate databases:

```python
from bioservices import UniProt

def multi_hop_mapping(gene_symbol, organism="9606"):
    """Gene symbol → UniProt → KEGG → Pathways."""
    u = UniProt()
    k = KEGG()

    # Step 1: Gene symbol → UniProt
    query = f"gene:{gene_symbol} AND organism:{organism}"
    result = u.search(query, frmt="tab", columns="id")

    lines = result.strip().split("\n")
    if len(lines) < 2:
        return None

    uniprot_id = lines[1].split("\t")[0]

    # Step 2: UniProt → KEGG
    kegg_mapping = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=uniprot_id)
    if not kegg_mapping or uniprot_id not in kegg_mapping:
        return None

    kegg_id = kegg_mapping[uniprot_id][0]

    # Step 3: KEGG → Pathways
    organism_code, gene_id = kegg_id.split(":")
    pathways = k.get_pathway_by_gene(gene_id, organism_code)

    return {
        'gene': gene_symbol,
        'uniprot': uniprot_id,
        'kegg': kegg_id,
        'pathways': pathways
    }

# Usage
result = multi_hop_mapping("TP53")
print(result)
```

---

## Troubleshooting

### Issue 1: No Mapping Found

**Symptom:** Mapping returns empty or None

**Solutions:**
1. Verify source ID exists in source database
2. Check database code spelling
3. Try reverse mapping
4. Some IDs may not have mappings in all databases

```python
result = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query="P43403")

if not result or 'P43403' not in result:
    print("No mapping found. Try:")
    print("1. Verify ID exists: u.search('P43403')")
    print("2. Check if protein has KEGG annotation")
```

### Issue 2: Too Many IDs in Batch

**Symptom:** Batch mapping fails or times out

**Solution:** Split into smaller chunks

```python
def chunked_mapping(ids, from_db, to_db, chunk_size=50):
    all_results = {}

    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i+chunk_size]
        result = u.mapping(fr=from_db, to=to_db, query=",".join(chunk))
        all_results.update(result)

    return all_results
```

### Issue 3: Multiple Target IDs

**Symptom:** One source ID maps to multiple target IDs

**Solution:** Handle as list

```python
result = u.mapping(fr="UniProtKB_AC-ID", to="PDB", query="P04637")
# Result: {'P04637': ['1A1U', '1AIE', '1C26', ...]}

pdb_ids = result['P04637']
print(f"Found {len(pdb_ids)} PDB structures")

for pdb_id in pdb_ids:
    print(f"  {pdb_id}")
```

### Issue 4: Organism Ambiguity

**Symptom:** Gene symbol maps to multiple organisms

**Solution:** Always specify organism in searches

```python
# Bad: Ambiguous
result = u.search("gene:TP53")  # Many organisms have TP53

# Good: Specific
result = u.search("gene:TP53 AND organism:9606")  # Human only
```

### Issue 5: Deprecated IDs

**Symptom:** Old database IDs don't map

**Solution:** Update to current IDs first

```python
# Check if ID is current
entry = u.retrieve("P43403", frmt="txt")

# Look for secondary accessions
for line in entry.split("\n"):
    if line.startswith("AC"):
        print(line)  # Shows primary and secondary accessions
```

---

## Best Practices

1. **Always validate inputs** before batch processing
2. **Handle None/empty results** gracefully
3. **Use chunking** for large ID lists (50-100 per chunk)
4. **Cache results** for repeated queries
5. **Specify organism** when possible to avoid ambiguity
6. **Log failures** in batch processing for later retry
7. **Add delays** between large batches to respect API limits

```python
import time

def polite_batch_mapping(ids, from_db, to_db):
    """Batch mapping with rate limiting."""
    results = {}

    for i in range(0, len(ids), 50):
        chunk = ids[i:i+50]
        result = u.mapping(fr=from_db, to=to_db, query=",".join(chunk))
        results.update(result)

        time.sleep(0.5)  # Be nice to the API

    return results
```

---

For complete working examples, see:
- `scripts/batch_id_converter.py`: Command-line batch conversion tool
- `workflow_patterns.md`: Integration into larger workflows

### `references/services_reference.md`

# BioServices: Complete Services Reference

This document provides a comprehensive reference for all major services available in BioServices, including key methods, parameters, and use cases. Targets **bioservices 1.16.0** ([Read the Docs](https://bioservices.readthedocs.io/), [GitHub](https://github.com/cokelaer/bioservices)).

## Protein & Gene Resources

### UniProt

Protein sequence and functional information database.

**Initialization:**
```python
from bioservices import UniProt
u = UniProt(verbose=False)
```

**Key Methods:**

- `search(query, frmt="tab", columns=None, limit=None, sort=None, compress=False, include=False, **kwargs)`
  - Search UniProt with flexible query syntax
  - `frmt`: "tab", "fasta", "xml", "rdf", "gff", "txt"
  - `columns`: Comma-separated list (e.g., "id,genes,organism,length")
  - Returns: String in requested format

- `retrieve(uniprot_id, frmt="txt")`
  - Retrieve specific UniProt entry
  - `frmt`: "txt", "fasta", "xml", "rdf", "gff"
  - Returns: Entry data in requested format

- `mapping(fr="UniProtKB_AC-ID", to="KEGG", query="P43403")`
  - Convert identifiers between databases
  - `fr`/`to`: Database identifiers (see identifier_mapping.md)
  - `query`: Single ID or comma-separated list
  - Returns: Dictionary mapping input to output IDs

- `searchUniProtId(pattern, columns="entry name,length,organism", limit=100)`
  - Convenience method for ID-based searches
  - Returns: Tab-separated values

**Common columns:** id, entry name, genes, organism, protein names, length, sequence, go-id, ec, pathway, interactor

**UniProt API note (≥1.10):** UniProt updated its REST API in June 2022. User-facing methods are largely unchanged, but tabular `columns` names may differ from older examples. If column parsing fails, check upstream `_legacy_names` in the UniProt module docs.

**Use cases:**
- Protein sequence retrieval for BLAST
- Functional annotation lookup
- Cross-database identifier mapping
- Batch protein information retrieval

---

### KEGG (Kyoto Encyclopedia of Genes and Genomes)

Metabolic pathways, genes, and organisms database.

**Initialization:**
```python
from bioservices import KEGG
k = KEGG()
k.organism = "hsa"  # Set default organism
```

**Key Methods:**

- `list(database)`
  - List entries in KEGG database
  - `database`: "organism", "pathway", "module", "disease", "drug", "compound"
  - Returns: Multi-line string with entries

- `find(database, query)`
  - Search database by keywords
  - Returns: List of matching entries with IDs

- `get(entry_id)`
  - Retrieve entry by ID
  - Supports genes, pathways, compounds, etc.
  - Returns: Raw entry text

- `parse(data)`
  - Parse KEGG entry into dictionary
  - Returns: Dict with structured data

- `lookfor_organism(name)`
  - Search organisms by name pattern
  - Returns: List of matching organism codes

- `lookfor_pathway(name)`
  - Search pathways by name
  - Returns: List of pathway IDs

- `get_pathway_by_gene(gene_id, organism)`
  - Find pathways containing gene
  - Returns: List of pathway IDs

- `parse_kgml_pathway(pathway_id)`
  - Parse pathway KGML for interactions
  - Returns: Dict with "entries" and "relations"

- `pathway2sif(pathway_id)`
  - Extract Simple Interaction Format data
  - Filters for activation/inhibition
  - Returns: List of interaction tuples

**Organism codes:**
- hsa: Homo sapiens
- mmu: Mus musculus
- dme: Drosophila melanogaster
- sce: Saccharomyces cerevisiae
- eco: Escherichia coli

**Use cases:**
- Pathway analysis and visualization
- Gene function annotation
- Metabolic network reconstruction
- Protein-protein interaction extraction

---

### HGNC (Human Gene Nomenclature Committee)

Official human gene naming authority.

**Initialization:**
```python
from bioservices import HGNC
h = HGNC()
```

**Key Methods:**
- `search(query)`: Search gene symbols/names
- `fetch(format, query)`: Retrieve gene information

**Use cases:**
- Standardizing human gene names
- Looking up official gene symbols

---

### MyGeneInfo

Gene annotation and query service.

**Initialization:**
```python
from bioservices import MyGeneInfo
m = MyGeneInfo()
```

**Key Methods:**
- `querymany(ids, scopes, fields, species)`: Batch gene queries
- `getgene(geneid)`: Get gene annotation

**Use cases:**
- Batch gene annotation retrieval
- Gene ID conversion

---

## Chemical Compound Resources

### ChEBI (Chemical Entities of Biological Interest)

Dictionary of molecular entities.

**Initialization:**
```python
from bioservices import ChEBI
c = ChEBI()
```

**Key Methods:**
- `getCompleteEntity(chebi_id)`: Full compound information
- `getLiteEntity(chebi_id)`: Basic information
- `getCompleteEntityByList(chebi_ids)`: Batch retrieval

**Use cases:**
- Small molecule information
- Chemical structure data
- Compound property lookup

---

### ChEMBL

Bioactive drug-like compound database.

**Initialization:**
```python
from bioservices import ChEMBL
c = ChEMBL()
```

**Key Methods:**
- `get_molecule_form(chembl_id)`: Compound details
- `get_target(chembl_id)`: Target information
- `get_similarity(chembl_id)`: Get similar compounds for given 
- `get_assays()`: Bioassay data

**Use cases:**
- Drug discovery data
- Find similar compounds  
- Bioactivity information
- Target-compound relationships

---

### UniChem

Chemical identifier mapping service.

**Initialization:**
```python
from bioservices import UniChem
u = UniChem()
```

**Key Methods:**
- `get_compound_id_from_kegg(kegg_id)`: KEGG → ChEMBL
- `get_all_compound_ids(src_compound_id, src_id)`: Get all IDs
- `get_src_compound_ids(src_compound_id, from_src_id, to_src_id)`: Convert IDs

**Source IDs:**
- 1: ChEMBL
- 2: DrugBank
- 3: PDB
- 6: KEGG
- 7: ChEBI
- 22: PubChem

**Use cases:**
- Cross-database compound ID mapping
- Linking chemical databases

---

### PubChem

Chemical compound database from NIH.

**Initialization:**
```python
from bioservices import PubChem
p = PubChem()
```

**Key Methods:**
- `get_compounds(identifier, namespace)`: Retrieve compounds
- `get_properties(properties, identifier, namespace)`: Get properties

**Use cases:**
- Chemical structure retrieval
- Compound property information

---

## Sequence Analysis Tools

### NCBIblast

Sequence similarity searching.

**Initialization:**
```python
from bioservices import NCBIblast
s = NCBIblast(verbose=False)
```

**Key Methods:**
- `run(program, sequence, stype, database, email, **params)`
  - Submit BLAST job
  - `program`: "blastp", "blastn", "blastx", "tblastn", "tblastx"
  - `stype`: "protein" or "dna"
  - `database`: "uniprotkb", "pdb", "refseq_protein", etc.
  - `email`: Required by NCBI — set `NCBI_EMAIL` in the environment or pass explicitly
  - Returns: Job ID

- `getStatus(jobid)`
  - Check job status
  - Returns: "RUNNING", "FINISHED", "ERROR"

- `getResult(jobid, result_type)`
  - Retrieve results
  - `result_type`: "out" (default), "ids", "xml"

**Important:** BLAST jobs are asynchronous. Always check status before retrieving results.

**Use cases:**
- Protein homology searches
- Sequence similarity analysis
- Functional annotation by homology

---

## Pathway & Interaction Resources

### Reactome

Pathway database.

**Initialization:**
```python
from bioservices import Reactome
r = Reactome()
```

**Key Methods:**
- `get_pathway_by_id(pathway_id)`: Pathway details
- `search_pathway(query)`: Search pathways

**Use cases:**
- Human pathway analysis
- Biological process annotation

---

### PSICQUIC

Protein interaction query service (federates 30+ databases).

**Initialization:**
```python
from bioservices import PSICQUIC
s = PSICQUIC()
```

**Key Methods:**
- `query(database, query_string)`
  - Query specific interaction database
  - Returns: PSI-MI TAB format

- `activeDBs`
  - Property listing available databases
  - Returns: List of database names

**Available databases:** MINT, IntAct, BioGRID, DIP, InnateDB, MatrixDB, MPIDB, UniProt, and 30+ more

**Query syntax:** Supports AND, OR, species filters
- Example: "ZAP70 AND species:9606"

**Use cases:**
- Protein-protein interaction discovery
- Network analysis
- Interactome mapping

---

### IntactComplex

Protein complex database.

**Initialization:**
```python
from bioservices import IntactComplex
i = IntactComplex()
```

**Key Methods:**
- `search(query)`: Search complexes
- `details(complex_ac)`: Complex details

**Use cases:**
- Protein complex composition
- Multi-protein assembly analysis

---

### OmniPath

Integrated signaling pathway database.

**Initialization:**
```python
from bioservices import OmniPath
o = OmniPath()
```

**Key Methods:**
- `interactions(datasets, organisms)`: Get interactions
- `ptms(datasets, organisms)`: Post-translational modifications

**Use cases:**
- Cell signaling analysis
- Regulatory network mapping

---

## Gene Ontology

### QuickGO

Gene Ontology annotation service.

**Initialization:**
```python
from bioservices import QuickGO
g = QuickGO()
```

**Key Methods:**
- `Term(go_id, frmt="obo")`
  - Retrieve GO term information
  - Returns: Term definition and metadata

- `Annotation(protein=None, goid=None, format="tsv")`
  - Get GO annotations
  - Returns: Annotations in requested format

**GO categories:**
- Biological Process (BP)
- Molecular Function (MF)
- Cellular Component (CC)

**Use cases:**
- Functional annotation
- Enrichment analysis
- GO term lookup

---

## Genomic Resources

### BioMart

Data mining tool for genomic data.

**Initialization:**
```python
from bioservices import BioMart
b = BioMart()
```

**Key Methods:**
- `datasets(dataset)`: List available datasets
- `attributes(dataset)`: List attributes
- `query(query_xml)`: Execute BioMart query

**Use cases:**
- Bulk genomic data retrieval
- Custom genome annotations
- SNP information

---

### ArrayExpress

Gene expression database.

**Initialization:**
```python
from bioservices import ArrayExpress
a = ArrayExpress()
```

**Key Methods:**
- `queryExperiments(keywords)`: Search experiments
- `retrieveExperiment(accession)`: Get experiment data

**Use cases:**
- Gene expression data
- Microarray analysis
- RNA-seq data retrieval

---

### ENA (European Nucleotide Archive)

Nucleotide sequence database.

**Initialization:**
```python
from bioservices import ENA
e = ENA()
```

**Key Methods:**
- `search_data(query)`: Search sequences
- `retrieve_data(accession)`: Retrieve sequences

**Use cases:**
- Nucleotide sequence retrieval
- Genome assembly access

---

## Structural Biology

### PDB (Protein Data Bank)

3D protein structure database.

**Initialization:**
```python
from bioservices import PDB
p = PDB()
```

**Key Methods:**
- `get_file(pdb_id, file_format)`: Download structure files
- `search(query)`: Search structures

**File formats:** pdb, cif, xml

**Use cases:**
- 3D structure retrieval
- Structure-based analysis
- PyMOL visualization

---

### Pfam

Protein family database.

**Initialization:**
```python
from bioservices import Pfam
p = Pfam()
```

**Key Methods:**
- `searchSequence(sequence)`: Find domains in sequence
- `getPfamEntry(pfam_id)`: Domain information

**Use cases:**
- Protein domain identification
- Family classification
- Functional motif discovery

---

## Specialized Resources

### BioModels

Systems biology model repository.

**Initialization:**
```python
from bioservices import BioModels
b = BioModels()
```

**Key Methods:**
- `get_model_by_id(model_id)`: Retrieve SBML model

**Use cases:**
- Systems biology modeling
- SBML model retrieval

---

### COG (Clusters of Orthologous Genes)

Orthologous gene classification.

**Initialization:**
```python
from bioservices import COG
c = COG()
```

**Use cases:**
- Orthology analysis
- Functional classification

---

### BiGG Models

Metabolic network models.

**Initialization:**
```python
from bioservices import BiGG
b = BiGG()
```

**Key Methods:**
- `list_models()`: Available models
- `get_model(model_id)`: Model details

**Use cases:**
- Metabolic network analysis
- Flux balance analysis

---

## General Patterns

### Error Handling

All services may throw exceptions. Wrap calls in try-except:

```python
try:
    result = service.method(params)
    if result:
        # Process result
        pass
except Exception as e:
    print(f"Error: {e}")
```

### Verbosity Control

Most services support `verbose` parameter:
```python
service = Service(verbose=False)  # Suppress HTTP logs
```

### Rate Limiting

Services have timeouts and rate limits:
```python
service.TIMEOUT = 30  # Adjust timeout
service.DELAY = 1     # Delay between requests (if supported)
```

### Output Formats

Common format parameters:
- `frmt`: "xml", "json", "tab", "txt", "fasta"
- `format`: Service-specific variants

### Caching

Some services cache results:
```python
service.CACHE = True  # Enable caching
service.clear_cache()  # Clear cache
```

## Additional Resources

For detailed API documentation:
- Official docs: https://bioservices.readthedocs.io/
- Individual service docs linked from main page
- Source code: https://github.com/cokelaer/bioservices

### `references/workflow_patterns.md`

# BioServices: Common Workflow Patterns

This document describes detailed multi-step workflows for common bioinformatics tasks using BioServices.

## Table of Contents

1. [Complete Protein Analysis Pipeline](#complete-protein-analysis-pipeline)
2. [Pathway Discovery and Network Analysis](#pathway-discovery-and-network-analysis)
3. [Compound Multi-Database Search](#compound-multi-database-search)
4. [Batch Identifier Conversion](#batch-identifier-conversion)
5. [Gene Functional Annotation](#gene-functional-annotation)
6. [Protein Interaction Network Construction](#protein-interaction-network-construction)
7. [Multi-Organism Comparative Analysis](#multi-organism-comparative-analysis)

---

## Complete Protein Analysis Pipeline

**Goal:** Given a protein name, retrieve sequence, find homologs, identify pathways, and discover interactions.

**Example:** Analyzing human ZAP70 protein

### Step 1: UniProt Search and Identifier Retrieval

```python
from bioservices import UniProt

u = UniProt(verbose=False)

# Search for protein by name
query = "ZAP70_HUMAN"
results = u.search(query, frmt="tab", columns="id,genes,organism,length")

# Parse results
lines = results.strip().split("\n")
if len(lines) > 1:
    header = lines[0]
    data = lines[1].split("\t")
    uniprot_id = data[0]  # e.g., P43403
    gene_names = data[1]   # e.g., ZAP70

print(f"UniProt ID: {uniprot_id}")
print(f"Gene names: {gene_names}")
```

**Output:**
- UniProt accession: P43403
- Gene name: ZAP70

### Step 2: Sequence Retrieval

```python
# Retrieve FASTA sequence
sequence = u.retrieve(uniprot_id, frmt="fasta")
print(sequence)

# Extract just the sequence string (remove header)
seq_lines = sequence.split("\n")
sequence_only = "".join(seq_lines[1:])  # Skip FASTA header
```

**Output:** Complete protein sequence in FASTA format

### Step 3: BLAST Similarity Search

```python
import os
import time
from bioservices import NCBIblast

s = NCBIblast(verbose=False)
email = os.environ["NCBI_EMAIL"]  # export NCBI_EMAIL=you@lab.org

# Submit BLAST job
jobid = s.run(
    program="blastp",
    sequence=sequence_only,
    stype="protein",
    database="uniprotkb",
    email=email,
)

print(f"BLAST Job ID: {jobid}")

# Wait for completion
while True:
    status = s.getStatus(jobid)
    print(f"Status: {status}")
    if status == "FINISHED":
        break
    elif status == "ERROR":
        print("BLAST job failed")
        break
    time.sleep(5)

# Retrieve results
if status == "FINISHED":
    blast_results = s.getResult(jobid, "out")
    print(blast_results[:500])  # Print first 500 characters
```

**Output:** BLAST alignment results showing similar proteins

### Step 4: KEGG Pathway Discovery

```python
from bioservices import KEGG

k = KEGG()

# Get KEGG gene ID from UniProt mapping
kegg_mapping = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=uniprot_id)
print(f"KEGG mapping: {kegg_mapping}")

# Extract KEGG gene ID (e.g., hsa:7535)
if kegg_mapping:
    kegg_gene_id = kegg_mapping[uniprot_id][0] if uniprot_id in kegg_mapping else None

    if kegg_gene_id:
        # Find pathways containing this gene
        organism = kegg_gene_id.split(":")[0]  # e.g., "hsa"
        gene_id = kegg_gene_id.split(":")[1]   # e.g., "7535"

        pathways = k.get_pathway_by_gene(gene_id, organism)
        print(f"Found {len(pathways)} pathways:")

        # Get pathway names
        for pathway_id in pathways:
            pathway_info = k.get(pathway_id)
            # Parse NAME line
            for line in pathway_info.split("\n"):
                if line.startswith("NAME"):
                    pathway_name = line.replace("NAME", "").strip()
                    print(f"  {pathway_id}: {pathway_name}")
                    break
```

**Output:**
- path:hsa04064 - NF-kappa B signaling pathway
- path:hsa04650 - Natural killer cell mediated cytotoxicity
- path:hsa04660 - T cell receptor signaling pathway
- path:hsa04662 - B cell receptor signaling pathway

### Step 5: Protein-Protein Interactions

```python
from bioservices import PSICQUIC

p = PSICQUIC()

# Query MINT database for human (taxid:9606) interactions
query = f"ZAP70 AND species:9606"
interactions = p.query("mint", query)

# Parse PSI-MI TAB format results
if interactions:
    interaction_lines = interactions.strip().split("\n")
    print(f"Found {len(interaction_lines)} interactions")

    # Print first few interactions
    for line in interaction_lines[:5]:
        fields = line.split("\t")
        protein_a = fields[0]
        protein_b = fields[1]
        interaction_type = fields[11]
        print(f"  {protein_a} - {protein_b}: {interaction_type}")
```

**Output:** List of proteins that interact with ZAP70

### Step 6: Gene Ontology Annotation

```python
from bioservices import QuickGO

g = QuickGO()

# Get GO annotations for protein
annotations = g.Annotation(protein=uniprot_id, format="tsv")

if annotations:
    # Parse TSV results
    lines = annotations.strip().split("\n")
    print(f"Found {len(lines)-1} GO annotations")

    # Display first few annotations
    for line in lines[1:6]:  # Skip header
        fields = line.split("\t")
        go_id = fields[6]
        go_term = fields[7]
        go_aspect = fields[8]
        print(f"  {go_id}: {go_term} [{go_aspect}]")
```

**Output:** GO terms annotating ZAP70 function, process, and location

### Complete Pipeline Summary

**Inputs:** Protein name (e.g., "ZAP70_HUMAN")

**Outputs:**
1. UniProt accession and gene name
2. Protein sequence (FASTA)
3. Similar proteins (BLAST results)
4. Biological pathways (KEGG)
5. Interaction partners (PSICQUIC)
6. Functional annotations (GO terms)

**Script:** `scripts/protein_analysis_workflow.py` automates this entire pipeline.

---

## Pathway Discovery and Network Analysis

**Goal:** Analyze all pathways for an organism and extract protein interaction networks.

**Example:** Human (hsa) pathway analysis

### Step 1: Get All Pathways for Organism

```python
from bioservices import KEGG

k = KEGG()
k.organism = "hsa"

# Get all pathway IDs
pathway_ids = k.pathwayIds
print(f"Found {len(pathway_ids)} pathways for {k.organism}")

# Display first few
for pid in pathway_ids[:10]:
    print(f"  {pid}")
```

**Output:** List of ~300 human pathways

### Step 2: Parse Pathway for Interactions

```python
# Analyze specific pathway
pathway_id = "hsa04660"  # T cell receptor signaling

# Get KGML data
kgml_data = k.parse_kgml_pathway(pathway_id)

# Extract entries (genes/proteins)
entries = kgml_data['entries']
print(f"Pathway contains {len(entries)} entries")

# Extract relations (interactions)
relations = kgml_data['relations']
print(f"Found {len(relations)} relations")

# Analyze relation types
relation_types = {}
for rel in relations:
    rel_type = rel.get('name', 'unknown')
    relation_types[rel_type] = relation_types.get(rel_type, 0) + 1

print("\nRelation type distribution:")
for rel_type, count in sorted(relation_types.items()):
    print(f"  {rel_type}: {count}")
```

**Output:**
- Entry count (genes/proteins in pathway)
- Relation count (interactions)
- Distribution of interaction types (activation, inhibition, binding, etc.)

### Step 3: Extract Protein-Protein Interactions

```python
# Filter for specific interaction types
pprel_interactions = [
    rel for rel in relations
    if rel.get('link') == 'PPrel'  # Protein-protein relation
]

print(f"Found {len(pprel_interactions)} protein-protein interactions")

# Extract interaction details
for rel in pprel_interactions[:10]:
    entry1 = rel['entry1']
    entry2 = rel['entry2']
    interaction_type = rel.get('name', 'unknown')

    print(f"  {entry1} -> {entry2}: {interaction_type}")
```

**Output:** Directed protein-protein interactions with types

### Step 4: Convert to Network Format (SIF)

```python
# Get Simple Interaction Format (filters for key interactions)
sif_data = k.pathway2sif(pathway_id)

# SIF format: source, interaction_type, target
print("\nSimple Interaction Format:")
for interaction in sif_data[:10]:
    print(f"  {interaction}")
```

**Output:** Network edges suitable for Cytoscape or NetworkX

### Step 5: Batch Analysis of All Pathways

```python
import pandas as pd

# Analyze all pathways (this takes time!)
all_results = []

for pathway_id in pathway_ids[:50]:  # Limit for example
    try:
        kgml = k.parse_kgml_pathway(pathway_id)

        result = {
            'pathway_id': pathway_id,
            'num_entries': len(kgml.get('entries', [])),
            'num_relations': len(kgml.get('relations', []))
        }

        all_results.append(result)

    except Exception as e:
        print(f"Error parsing {pathway_id}: {e}")

# Create DataFrame
df = pd.DataFrame(all_results)
print(df.describe())

# Find largest pathways
print("\nLargest pathways:")
print(df.nlargest(10, 'num_entries')[['pathway_id', 'num_entries', 'num_relations']])
```

**Output:** Statistical summary of pathway sizes and interaction densities

**Script:** `scripts/pathway_analysis.py` implements this workflow with export options.

---

## Compound Multi-Database Search

**Goal:** Search for compound by name and retrieve identifiers across KEGG, ChEBI, and ChEMBL.

**Example:** Geldanamycin (antibiotic)

### Step 1: Search KEGG Compound Database

```python
from bioservices import KEGG

k = KEGG()

# Search by compound name
compound_name = "Geldanamycin"
results = k.find("compound", compound_name)

print(f"KEGG search results for '{compound_name}':")
print(results)

# Extract compound ID
if results:
    lines = results.strip().split("\n")
    if lines:
        kegg_id = lines[0].split("\t")[0]  # e.g., cpd:C11222
        kegg_id_clean = kegg_id.replace("cpd:", "")  # C11222
        print(f"\nKEGG Compound ID: {kegg_id_clean}")
```

**Output:** KEGG ID (e.g., C11222)

### Step 2: Get KEGG Entry with Database Links

```python
# Retrieve compound entry
compound_entry = k.get(kegg_id)

# Parse entry for database links
chebi_id = None
for line in compound_entry.split("\n"):
    if "ChEBI:" in line:
        # Extract ChEBI ID
        parts = line.split("ChEBI:")
        if len(parts) > 1:
            chebi_id = parts[1].strip().split()[0]
            print(f"ChEBI ID: {chebi_id}")
            break

# Display entry snippet
print("\nKEGG Entry (first 500 chars):")
print(compound_entry[:500])
```

**Output:** ChEBI ID (e.g., 5292) and compound information

### Step 3: Cross-Reference to ChEMBL via UniChem

```python
from bioservices import UniChem

u = UniChem()

# Convert KEGG → ChEMBL
try:
    chembl_id = u.get_compound_id_from_kegg(kegg_id_clean)
    print(f"ChEMBL ID: {chembl_id}")
except Exception as e:
    print(f"UniChem lookup failed: {e}")
    chembl_id = None
```

**Output:** ChEMBL ID (e.g., CHEMBL278315)

### Step 4: Retrieve Detailed Information

```python
# Get ChEBI information
if chebi_id:
    from bioservices import ChEBI
    c = ChEBI()

    try:
        chebi_entity = c.getCompleteEntity(f"CHEBI:{chebi_id}")
        print(f"\nChEBI Formula: {chebi_entity.Formulae}")
        print(f"ChEBI Name: {chebi_entity.chebiAsciiName}")
    except Exception as e:
        print(f"ChEBI lookup failed: {e}")

# Get ChEMBL information
if chembl_id:
    from bioservices import ChEMBL
    chembl = ChEMBL()

    try:
        chembl_compound = chembl.get_compound_by_chemblId(chembl_id)
        print(f"\nChEMBL Molecular Weight: {chembl_compound['molecule_properties']['full_mwt']}")
        print(f"ChEMBL SMILES: {chembl_compound['molecule_structures']['canonical_smiles']}")
    except Exception as e:
        print(f"ChEMBL lookup failed: {e}")
```

**Output:** Chemical properties from multiple databases

### Complete Compound Workflow Summary

**Input:** Compound name (e.g., "Geldanamycin")

**Output:**
- KEGG ID: C11222
- ChEBI ID: 5292
- ChEMBL ID: CHEMBL278315
- Chemical formula
- Molecular weight
- SMILES structure

**Script:** `scripts/compound_cross_reference.py` automates this workflow.

---

## Batch Identifier Conversion

**Goal:** Convert multiple identifiers between databases efficiently.

### Batch UniProt → KEGG Mapping

```python
from bioservices import UniProt

u = UniProt()

# List of UniProt IDs
uniprot_ids = ["P43403", "P04637", "P53779", "Q9Y6K9"]

# Batch mapping (comma-separated)
query_string = ",".join(uniprot_ids)
results = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=query_string)

print("UniProt → KEGG mapping:")
for uniprot_id, kegg_ids in results.items():
    print(f"  {uniprot_id} → {kegg_ids}")
```

**Output:** Dictionary mapping each UniProt ID to KEGG gene IDs

### Batch File Processing

```python
import csv

# Read identifiers from file
def read_ids_from_file(filename):
    with open(filename, 'r') as f:
        ids = [line.strip() for line in f if line.strip()]
    return ids

# Process in chunks (API limits)
def batch_convert(ids, from_db, to_db, chunk_size=100):
    u = UniProt()
    all_results = {}

    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i+chunk_size]
        query = ",".join(chunk)

        try:
            results = u.mapping(fr=from_db, to=to_db, query=query)
            all_results.update(results)
            print(f"Processed {min(i+chunk_size, len(ids))}/{len(ids)}")
        except Exception as e:
            print(f"Error processing chunk {i}: {e}")

    return all_results

# Write results to CSV
def write_mapping_to_csv(mapping, output_file):
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Source_ID', 'Target_IDs'])

        for source_id, target_ids in mapping.items():
            target_str = ";".join(target_ids) if target_ids else "No mapping"
            writer.writerow([source_id, target_str])

# Example usage
input_ids = read_ids_from_file("uniprot_ids.txt")
mapping = batch_convert(input_ids, "UniProtKB_AC-ID", "KEGG", chunk_size=50)
write_mapping_to_csv(mapping, "uniprot_to_kegg_mapping.csv")
```

**Script:** `scripts/batch_id_converter.py` provides command-line batch conversion.

---

## Gene Functional Annotation

**Goal:** Retrieve comprehensive functional information for a gene.

### Workflow

```python
from bioservices import UniProt, KEGG, QuickGO

# Gene of interest
gene_symbol = "TP53"

# 1. Find UniProt entry
u = UniProt()
search_results = u.search(f"gene:{gene_symbol} AND organism:9606",
                          frmt="tab",
                          columns="id,genes,protein names")

# Extract UniProt ID
lines = search_results.strip().split("\n")
if len(lines) > 1:
    uniprot_id = lines[1].split("\t")[0]
    protein_name = lines[1].split("\t")[2]
    print(f"Protein: {protein_name}")
    print(f"UniProt ID: {uniprot_id}")

# 2. Get KEGG pathways
kegg_mapping = u.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=uniprot_id)
if uniprot_id in kegg_mapping:
    kegg_id = kegg_mapping[uniprot_id][0]

    k = KEGG()
    organism, gene_id = kegg_id.split(":")
    pathways = k.get_pathway_by_gene(gene_id, organism)

    print(f"\nPathways ({len(pathways)}):")
    for pathway_id in pathways[:5]:
        print(f"  {pathway_id}")

# 3. Get GO annotations
g = QuickGO()
go_annotations = g.Annotation(protein=uniprot_id, format="tsv")

if go_annotations:
    lines = go_annotations.strip().split("\n")
    print(f"\nGO Annotations ({len(lines)-1} total):")

    # Group by aspect
    aspects = {"P": [], "F": [], "C": []}
    for line in lines[1:]:
        fields = line.split("\t")
        go_aspect = fields[8]  # P, F, or C
        go_term = fields[7]
        aspects[go_aspect].append(go_term)

    print(f"  Biological Process: {len(aspects['P'])} terms")
    print(f"  Molecular Function: {len(aspects['F'])} terms")
    print(f"  Cellular Component: {len(aspects['C'])} terms")

# 4. Get protein sequence features
full_entry = u.retrieve(uniprot_id, frmt="txt")
print("\nProtein Features:")
for line in full_entry.split("\n"):
    if line.startswith("FT   DOMAIN"):
        print(f"  {line}")
```

**Output:** Comprehensive annotation including name, pathways, GO terms, and features.

---

## Protein Interaction Network Construction

**Goal:** Build a protein-protein interaction network for a set of proteins.

### Workflow

```python
from bioservices import PSICQUIC
import networkx as nx

# Proteins of interest
proteins = ["ZAP70", "LCK", "LAT", "SLP76", "PLCg1"]

# Initialize PSICQUIC
p = PSICQUIC()

# Build network
G = nx.Graph()

for protein in proteins:
    # Query for human interactions
    query = f"{protein} AND species:9606"

    try:
        results = p.query("intact", query)

        if results:
            lines = results.strip().split("\n")

            for line in lines:
                fields = line.split("\t")
                # Extract protein names (simplified)
                protein_a = fields[4].split(":")[1] if ":" in fields[4] else fields[4]
                protein_b = fields[5].split(":")[1] if ":" in fields[5] else fields[5]

                # Add edge
                G.add_edge(protein_a, protein_b)

    except Exception as e:
        print(f"Error querying {protein}: {e}")

print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Analyze network
print("\nNode degrees:")
for node in proteins:
    if node in G:
        print(f"  {node}: {G.degree(node)} interactions")

# Export for visualization
nx.write_gml(G, "protein_network.gml")
print("\nNetwork exported to protein_network.gml")
```

**Output:** NetworkX graph exported in GML format for Cytoscape visualization.

---

## Multi-Organism Comparative Analysis

**Goal:** Compare pathway or gene presence across multiple organisms.

### Workflow

```python
from bioservices import KEGG

k = KEGG()

# Organisms to compare
organisms = ["hsa", "mmu", "dme", "sce"]  # Human, mouse, fly, yeast
organism_names = {
    "hsa": "Human",
    "mmu": "Mouse",
    "dme": "Fly",
    "sce": "Yeast"
}

# Pathway of interest
pathway_name = "cell cycle"

print(f"Searching for '{pathway_name}' pathway across organisms:\n")

for org in organisms:
    k.organism = org

    # Search pathways
    results = k.lookfor_pathway(pathway_name)

    print(f"{organism_names[org]} ({org}):")
    if results:
        for pathway in results[:3]:  # Show first 3
            print(f"  {pathway}")
    else:
        print("  No matches found")
    print()
```

**Output:** Pathway presence/absence across organisms.

---

## Best Practices for Workflows

### 1. Error Handling

Always wrap service calls:
```python
try:
    result = service.method(params)
    if result:
        # Process
        pass
except Exception as e:
    print(f"Error: {e}")
```

### 2. Rate Limiting

Add delays for batch processing:
```python
import time

for item in items:
    result = service.query(item)
    time.sleep(0.5)  # 500ms delay
```

### 3. Result Validation

Check for empty or unexpected results:
```python
if result and len(result) > 0:
    # Process
    pass
else:
    print("No results returned")
```

### 4. Progress Reporting

For long workflows:
```python
total = len(items)
for i, item in enumerate(items):
    # Process item
    if (i + 1) % 10 == 0:
        print(f"Processed {i+1}/{total}")
```

### 5. Data Export

Save intermediate results:
```python
import json

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## Integration with Other Tools

### BioPython Integration

```python
from bioservices import UniProt
from Bio import SeqIO
from io import StringIO

u = UniProt()
fasta_data = u.retrieve("P43403", "fasta")

# Parse with BioPython
fasta_io = StringIO(fasta_data)
record = SeqIO.read(fasta_io, "fasta")

print(f"Sequence length: {len(record.seq)}")
print(f"Description: {record.description}")
```

### Pandas Integration

```python
from bioservices import UniProt
import pandas as pd
from io import StringIO

u = UniProt()
results = u.search("zap70", frmt="tab", columns="id,genes,length,organism")

# Load into DataFrame
df = pd.read_csv(StringIO(results), sep="\t")
print(df.head())
print(df.describe())
```

### NetworkX Integration

See Protein Interaction Network Construction above.

---

For complete working examples, see the scripts in `scripts/` directory.

### `scripts/batch_id_converter.py`

```python
#!/usr/bin/env python3
"""
Batch Identifier Converter

This script converts multiple identifiers between biological databases
using UniProt's mapping service. Supports batch processing with
automatic chunking and error handling.

Usage:
    python batch_id_converter.py INPUT_FILE --from DB1 --to DB2 [options]

Examples:
    python batch_id_converter.py uniprot_ids.txt --from UniProtKB_AC-ID --to KEGG
    python batch_id_converter.py gene_ids.txt --from GeneID --to UniProtKB --output mapping.csv
    python batch_id_converter.py ids.txt --from UniProtKB_AC-ID --to Ensembl --chunk-size 50

Input file format:
    One identifier per line (plain text)

Common database codes:
    UniProtKB_AC-ID  - UniProt accession/ID
    KEGG             - KEGG gene IDs
    GeneID           - NCBI Gene (Entrez) IDs
    Ensembl          - Ensembl gene IDs
    Ensembl_Protein  - Ensembl protein IDs
    RefSeq_Protein   - RefSeq protein IDs
    PDB              - Protein Data Bank IDs
    HGNC             - Human gene symbols
    GO               - Gene Ontology IDs
"""

import sys
import argparse
import csv
import time
from bioservices import UniProt


# Common database code mappings
DATABASE_CODES = {
    'uniprot': 'UniProtKB_AC-ID',
    'uniprotkb': 'UniProtKB_AC-ID',
    'kegg': 'KEGG',
    'geneid': 'GeneID',
    'entrez': 'GeneID',
    'ensembl': 'Ensembl',
    'ensembl_protein': 'Ensembl_Protein',
    'ensembl_transcript': 'Ensembl_Transcript',
    'refseq': 'RefSeq_Protein',
    'refseq_protein': 'RefSeq_Protein',
    'pdb': 'PDB',
    'hgnc': 'HGNC',
    'mgi': 'MGI',
    'go': 'GO',
    'pfam': 'Pfam',
    'interpro': 'InterPro',
    'reactome': 'Reactome',
    'string': 'STRING',
    'biogrid': 'BioGRID'
}


def normalize_database_code(code):
    """Normalize database code to official format."""
    # Try exact match first
    if code in DATABASE_CODES.values():
        return code

    # Try lowercase lookup
    lowercase = code.lower()
    if lowercase in DATABASE_CODES:
        return DATABASE_CODES[lowercase]

    # Return as-is if not found (may still be valid)
    return code


def read_ids_from_file(filename):
    """Read identifiers from file (one per line)."""
    print(f"Reading identifiers from {filename}...")

    ids = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                ids.append(line)

    print(f"✓ Read {len(ids)} identifier(s)")

    return ids


def batch_convert(ids, from_db, to_db, chunk_size=100, delay=0.5):
    """Convert IDs with automatic chunking and error handling."""
    print(f"\nConverting {len(ids)} IDs:")
    print(f"  From: {from_db}")
    print(f"  To: {to_db}")
    print(f"  Chunk size: {chunk_size}")
    print()

    u = UniProt(verbose=False)
    all_results = {}
    failed_ids = []

    total_chunks = (len(ids) + chunk_size - 1) // chunk_size

    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i+chunk_size]
        chunk_num = (i // chunk_size) + 1

        query = ",".join(chunk)

        try:
            print(f"  [{chunk_num}/{total_chunks}] Processing {len(chunk)} IDs...", end=" ")

            results = u.mapping(fr=from_db, to=to_db, query=query)

            if results:
                all_results.update(results)
                mapped_count = len([v for v in results.values() if v])
                print(f"✓ Mapped: {mapped_count}/{len(chunk)}")
            else:
                print(f"✗ No mappings returned")
                failed_ids.extend(chunk)

            # Rate limiting
            if delay > 0 and i + chunk_size < len(ids):
                time.sleep(delay)

        except Exception as e:
            print(f"✗ Error: {e}")

            # Try individual IDs in failed chunk
            print(f"    Retrying individual IDs...")
            for single_id in chunk:
                try:
                    result = u.mapping(fr=from_db, to=to_db, query=single_id)
                    if result:
                        all_results.update(result)
                        print(f"      ✓ {single_id}")
                    else:
                        failed_ids.append(single_id)
                        print(f"      ✗ {single_id} - no mapping")
                except Exception as e2:
                    failed_ids.append(single_id)
                    print(f"      ✗ {single_id} - {e2}")

                time.sleep(0.2)

    # Add missing IDs to results (mark as failed)
    for id_ in ids:
        if id_ not in all_results:
            all_results[id_] = None

    print(f"\n✓ Conversion complete:")
    print(f"  Total: {len(ids)}")
    print(f"  Mapped: {len([v for v in all_results.values() if v])}")
    print(f"  Failed: {len(failed_ids)}")

    return all_results, failed_ids


def save_mapping_csv(mapping, output_file, from_db, to_db):
    """Save mapping results to CSV."""
    print(f"\nSaving results to {output_file}...")

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(['Source_ID', 'Source_DB', 'Target_IDs', 'Target_DB', 'Mapping_Status'])

        # Data
        for source_id, target_ids in sorted(mapping.items()):
            if target_ids:
                target_str = ";".join(target_ids)
                status = "Success"
            else:
                target_str = ""
                status = "Failed"

            writer.writerow([source_id, from_db, target_str, to_db, status])

    print(f"✓ Results saved")


def save_failed_ids(failed_ids, output_file):
    """Save failed IDs to file."""
    if not failed_ids:
        return

    print(f"\nSaving failed IDs to {output_file}...")

    with open(output_file, 'w') as f:
        for id_ in failed_ids:
            f.write(f"{id_}\n")

    print(f"✓ Saved {len(failed_ids)} failed ID(s)")


def print_mapping_summary(mapping, from_db, to_db):
    """Print summary of mapping results."""
    print(f"\n{'='*70}")
    print("MAPPING SUMMARY")
    print(f"{'='*70}")

    total = len(mapping)
    mapped = len([v for v in mapping.values() if v])
    failed = total - mapped

    print(f"\nSource database: {from_db}")
    print(f"Target database: {to_db}")
    print(f"\nTotal identifiers: {total}")
    print(f"Successfully mapped: {mapped} ({mapped/total*100:.1f}%)")
    print(f"Failed to map: {failed} ({failed/total*100:.1f}%)")

    # Show some examples
    if mapped > 0:
        print(f"\nExample mappings (first 5):")
        count = 0
        for source_id, target_ids in mapping.items():
            if target_ids:
                target_str = ", ".join(target_ids[:3])
                if len(target_ids) > 3:
                    target_str += f" ... +{len(target_ids)-3} more"
                print(f"  {source_id} → {target_str}")
                count += 1
                if count >= 5:
                    break

    # Show multiple mapping statistics
    multiple_mappings = [v for v in mapping.values() if v and len(v) > 1]
    if multiple_mappings:
        print(f"\nMultiple target mappings: {len(multiple_mappings)} ID(s)")
        print(f"  (These source IDs map to multiple target IDs)")

    print(f"{'='*70}")


def list_common_databases():
    """Print list of common database codes."""
    print("\nCommon Database Codes:")
    print("-" * 70)
    print(f"{'Alias':<20} {'Official Code':<30}")
    print("-" * 70)

    for alias, code in sorted(DATABASE_CODES.items()):
        if alias != code.lower():
            print(f"{alias:<20} {code:<30}")

    print("-" * 70)
    print("\nNote: Many other database codes are supported.")
    print("See UniProt documentation for complete list.")


def main():
    """Main conversion workflow."""
    parser = argparse.ArgumentParser(
        description="Batch convert biological identifiers between databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_id_converter.py uniprot_ids.txt --from UniProtKB_AC-ID --to KEGG
  python batch_id_converter.py ids.txt --from GeneID --to UniProtKB -o mapping.csv
  python batch_id_converter.py ids.txt --from uniprot --to ensembl --chunk-size 50

Common database codes:
  UniProtKB_AC-ID, KEGG, GeneID, Ensembl, Ensembl_Protein,
  RefSeq_Protein, PDB, HGNC, GO, Pfam, InterPro, Reactome

Use --list-databases to see all supported aliases.
        """
    )
    parser.add_argument("input_file", help="Input file with IDs (one per line)")
    parser.add_argument("--from", dest="from_db", required=True,
                       help="Source database code")
    parser.add_argument("--to", dest="to_db", required=True,
                       help="Target database code")
    parser.add_argument("-o", "--output", default=None,
                       help="Output CSV file (default: mapping_results.csv)")
    parser.add_argument("--chunk-size", type=int, default=100,
                       help="Number of IDs per batch (default: 100)")
    parser.add_argument("--delay", type=float, default=0.5,
                       help="Delay between batches in seconds (default: 0.5)")
    parser.add_argument("--save-failed", action="store_true",
                       help="Save failed IDs to separate file")
    parser.add_argument("--list-databases", action="store_true",
                       help="List common database codes and exit")

    args = parser.parse_args()

    # List databases and exit
    if args.list_databases:
        list_common_databases()
        sys.exit(0)

    print("=" * 70)
    print("BIOSERVICES: Batch Identifier Converter")
    print("=" * 70)

    # Normalize database codes
    from_db = normalize_database_code(args.from_db)
    to_db = normalize_database_code(args.to_db)

    if from_db != args.from_db:
        print(f"\nNote: Normalized '{args.from_db}' → '{from_db}'")
    if to_db != args.to_db:
        print(f"Note: Normalized '{args.to_db}' → '{to_db}'")

    # Read input IDs
    try:
        ids = read_ids_from_file(args.input_file)
    except Exception as e:
        print(f"\n✗ Error reading input file: {e}")
        sys.exit(1)

    if not ids:
        print("\n✗ No IDs found in input file")
        sys.exit(1)

    # Perform conversion
    mapping, failed_ids = batch_convert(
        ids,
        from_db,
        to_db,
        chunk_size=args.chunk_size,
        delay=args.delay
    )

    # Print summary
    print_mapping_summary(mapping, from_db, to_db)

    # Save results
    output_file = args.output or "mapping_results.csv"
    save_mapping_csv(mapping, output_file, from_db, to_db)

    # Save failed IDs if requested
    if args.save_failed and failed_ids:
        failed_file = output_file.replace(".csv", "_failed.txt")
        save_failed_ids(failed_ids, failed_file)

    print(f"\n✓ Done!")


if __name__ == "__main__":
    main()
```

### `scripts/compound_cross_reference.py`

```python
#!/usr/bin/env python3
"""
Compound Cross-Database Search

This script searches for a compound by name and retrieves identifiers
from multiple databases:
- KEGG Compound
- ChEBI
- ChEMBL (via UniChem)
- Basic compound properties

Usage:
    python compound_cross_reference.py COMPOUND_NAME [--output FILE]

Examples:
    python compound_cross_reference.py Geldanamycin
    python compound_cross_reference.py "Adenosine triphosphate"
    python compound_cross_reference.py Aspirin --output aspirin_info.txt
"""

import sys
import argparse
from bioservices import KEGG, UniChem, ChEBI, ChEMBL


def search_kegg_compound(compound_name):
    """Search KEGG for compound by name."""
    print(f"\n{'='*70}")
    print("STEP 1: KEGG Compound Search")
    print(f"{'='*70}")

    k = KEGG()

    print(f"Searching KEGG for: {compound_name}")

    try:
        results = k.find("compound", compound_name)

        if not results or not results.strip():
            print(f"✗ No results found in KEGG")
            return k, None

        # Parse results
        lines = results.strip().split("\n")
        print(f"✓ Found {len(lines)} result(s):\n")

        for i, line in enumerate(lines[:5], 1):
            parts = line.split("\t")
            kegg_id = parts[0]
            description = parts[1] if len(parts) > 1 else "No description"
            print(f"  {i}. {kegg_id}: {description}")

        # Use first result
        first_result = lines[0].split("\t")
        kegg_id = first_result[0].replace("cpd:", "")

        print(f"\nUsing: {kegg_id}")

        return k, kegg_id

    except Exception as e:
        print(f"✗ Error: {e}")
        return k, None


def get_kegg_info(kegg, kegg_id):
    """Retrieve detailed KEGG compound information."""
    print(f"\n{'='*70}")
    print("STEP 2: KEGG Compound Details")
    print(f"{'='*70}")

    try:
        print(f"Retrieving KEGG entry for {kegg_id}...")

        entry = kegg.get(f"cpd:{kegg_id}")

        if not entry:
            print("✗ Failed to retrieve entry")
            return None

        # Parse entry
        compound_info = {
            'kegg_id': kegg_id,
            'name': None,
            'formula': None,
            'exact_mass': None,
            'mol_weight': None,
            'chebi_id': None,
            'pathways': []
        }

        current_section = None

        for line in entry.split("\n"):
            # KEGG field names start in column 1 and their continuation lines are
            # indented. A new field therefore ends any multi-line section --
            # without this reset, the indented DBLINKS lines that follow PATHWAY
            # would be collected as pathways.
            if line and not line.startswith(" "):
                current_section = None

            if line.startswith("NAME"):
                compound_info['name'] = line.replace("NAME", "").strip().rstrip(";")

            elif line.startswith("FORMULA"):
                compound_info['formula'] = line.replace("FORMULA", "").strip()

            elif line.startswith("EXACT_MASS"):
                compound_info['exact_mass'] = line.replace("EXACT_MASS", "").strip()

            elif line.startswith("MOL_WEIGHT"):
                compound_info['mol_weight'] = line.replace("MOL_WEIGHT", "").strip()

            elif "ChEBI:" in line:
                parts = line.split("ChEBI:")
                if len(parts) > 1:
                    compound_info['chebi_id'] = parts[1].strip().split()[0]

            elif line.startswith("PATHWAY"):
                current_section = "pathway"
                pathway = line.replace("PATHWAY", "").strip()
                if pathway:
                    compound_info['pathways'].append(pathway)

            elif current_section == "pathway" and line.startswith("            "):
                pathway = line.strip()
                if pathway:
                    compound_info['pathways'].append(pathway)

            elif line.startswith(" ") and not line.startswith("            "):
                current_section = None

        # Display information
        print(f"\n✓ KEGG Compound Information:")
        print(f"  ID: {compound_info['kegg_id']}")
        print(f"  Name: {compound_info['name']}")
        print(f"  Formula: {compound_info['formula']}")
        print(f"  Exact Mass: {compound_info['exact_mass']}")
        print(f"  Molecular Weight: {compound_info['mol_weight']}")

        if compound_info['chebi_id']:
            print(f"  ChEBI ID: {compound_info['chebi_id']}")

        if compound_info['pathways']:
            print(f"  Pathways: {len(compound_info['pathways'])} found")

        return compound_info

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def get_chembl_id(kegg_id):
    """Map KEGG ID to ChEMBL via UniChem."""
    print(f"\n{'='*70}")
    print("STEP 3: ChEMBL Mapping (via UniChem)")
    print(f"{'='*70}")

    try:
        u = UniChem()

        print(f"Mapping KEGG:{kegg_id} to ChEMBL...")

        chembl_id = u.get_compound_id_from_kegg(kegg_id)

        if chembl_id:
            print(f"✓ ChEMBL ID: {chembl_id}")
            return chembl_id
        else:
            print("✗ No ChEMBL mapping found")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def get_chebi_info(chebi_id):
    """Retrieve ChEBI compound information."""
    print(f"\n{'='*70}")
    print("STEP 4: ChEBI Details")
    print(f"{'='*70}")

    if not chebi_id:
        print("⊘ No ChEBI ID available")
        return None

    try:
        c = ChEBI()

        print(f"Retrieving ChEBI entry for {chebi_id}...")

        # Ensure proper format
        if not chebi_id.startswith("CHEBI:"):
            chebi_id = f"CHEBI:{chebi_id}"

        entity = c.getCompleteEntity(chebi_id)

        if entity:
            print(f"\n✓ ChEBI Information:")
            print(f"  ID: {entity.chebiId}")
            print(f"  Name: {entity.chebiAsciiName}")

            if hasattr(entity, 'Formulae') and entity.Formulae:
                print(f"  Formula: {entity.Formulae}")

            if hasattr(entity, 'mass') and entity.mass:
                print(f"  Mass: {entity.mass}")

            if hasattr(entity, 'charge') and entity.charge:
                print(f"  Charge: {entity.charge}")

            return {
                'chebi_id': entity.chebiId,
                'name': entity.chebiAsciiName,
                'formula': entity.Formulae if hasattr(entity, 'Formulae') else None,
                'mass': entity.mass if hasattr(entity, 'mass') else None
            }
        else:
            print("✗ Failed to retrieve ChEBI entry")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def get_chembl_info(chembl_id):
    """Retrieve ChEMBL compound information."""
    print(f"\n{'='*70}")
    print("STEP 5: ChEMBL Details")
    print(f"{'='*70}")

    if not chembl_id:
        print("⊘ No ChEMBL ID available")
        return None

    try:
        c = ChEMBL()

        print(f"Retrieving ChEMBL entry for {chembl_id}...")

        # `get_compound_by_chemblId` was a pre-1.6 name; current releases expose
        # the same lookup as `get_molecule`.
        compound = c.get_molecule(chembl_id)

        if compound:
            print(f"\n✓ ChEMBL Information:")
            print(f"  ID: {chembl_id}")

            if 'pref_name' in compound and compound['pref_name']:
                print(f"  Preferred Name: {compound['pref_name']}")

            if 'molecule_properties' in compound:
                props = compound['molecule_properties']

                if 'full_mwt' in props:
                    print(f"  Molecular Weight: {props['full_mwt']}")

                if 'alogp' in props:
                    print(f"  LogP: {props['alogp']}")

                if 'hba' in props:
                    print(f"  H-Bond Acceptors: {props['hba']}")

                if 'hbd' in props:
                    print(f"  H-Bond Donors: {props['hbd']}")

            if 'molecule_structures' in compound:
                structs = compound['molecule_structures']

                if 'canonical_smiles' in structs:
                    smiles = structs['canonical_smiles']
                    print(f"  SMILES: {smiles[:60]}{'...' if len(smiles) > 60 else ''}")

            return compound
        else:
            print("✗ Failed to retrieve ChEMBL entry")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def save_results(compound_name, kegg_info, chembl_id, output_file):
    """Save results to file."""
    print(f"\n{'='*70}")
    print(f"Saving results to {output_file}")
    print(f"{'='*70}")

    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write(f"Compound Cross-Reference Report: {compound_name}\n")
        f.write("=" * 70 + "\n\n")

        # KEGG information
        if kegg_info:
            f.write("KEGG Compound\n")
            f.write("-" * 70 + "\n")
            f.write(f"ID: {kegg_info['kegg_id']}\n")
            f.write(f"Name: {kegg_info['name']}\n")
            f.write(f"Formula: {kegg_info['formula']}\n")
            f.write(f"Exact Mass: {kegg_info['exact_mass']}\n")
            f.write(f"Molecular Weight: {kegg_info['mol_weight']}\n")
            f.write(f"Pathways: {len(kegg_info['pathways'])} found\n")
            f.write("\n")

        # Database IDs
        f.write("Cross-Database Identifiers\n")
        f.write("-" * 70 + "\n")
        if kegg_info:
            f.write(f"KEGG: {kegg_info['kegg_id']}\n")
            if kegg_info['chebi_id']:
                f.write(f"ChEBI: {kegg_info['chebi_id']}\n")
        if chembl_id:
            f.write(f"ChEMBL: {chembl_id}\n")
        f.write("\n")

    print(f"✓ Results saved")


def main():
    """Main workflow."""
    parser = argparse.ArgumentParser(
        description="Search compound across multiple databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compound_cross_reference.py Geldanamycin
  python compound_cross_reference.py "Adenosine triphosphate"
  python compound_cross_reference.py Aspirin --output aspirin_info.txt
        """
    )
    parser.add_argument("compound", help="Compound name to search")
    parser.add_argument("--output", default=None,
                       help="Output file for results (optional)")

    args = parser.parse_args()

    print("=" * 70)
    print("BIOSERVICES: Compound Cross-Database Search")
    print("=" * 70)

    # Step 1: Search KEGG
    kegg, kegg_id = search_kegg_compound(args.compound)
    if not kegg_id:
        print("\n✗ Failed to find compound. Exiting.")
        sys.exit(1)

    # Step 2: Get KEGG details
    kegg_info = get_kegg_info(kegg, kegg_id)

    # Step 3: Map to ChEMBL
    chembl_id = get_chembl_id(kegg_id)

    # Step 4: Get ChEBI details
    chebi_info = None
    if kegg_info and kegg_info['chebi_id']:
        chebi_info = get_chebi_info(kegg_info['chebi_id'])

    # Step 5: Get ChEMBL details
    chembl_info = None
    if chembl_id:
        chembl_info = get_chembl_info(chembl_id)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"  Compound: {args.compound}")
    if kegg_info:
        print(f"  KEGG ID: {kegg_info['kegg_id']}")
        if kegg_info['chebi_id']:
            print(f"  ChEBI ID: {kegg_info['chebi_id']}")
    if chembl_id:
        print(f"  ChEMBL ID: {chembl_id}")
    print(f"{'='*70}")

    # Save to file if requested
    if args.output:
        save_results(args.compound, kegg_info, chembl_id, args.output)


if __name__ == "__main__":
    main()
```

### `scripts/pathway_analysis.py`

```python
#!/usr/bin/env python3
"""
KEGG Pathway Network Analysis

This script analyzes all pathways for an organism and extracts:
- Pathway sizes (number of genes)
- Protein-protein interactions
- Interaction type distributions
- Network data in various formats (CSV, SIF)

Usage:
    python pathway_analysis.py ORGANISM OUTPUT_DIR [--limit N]

Examples:
    python pathway_analysis.py hsa ./human_pathways
    python pathway_analysis.py mmu ./mouse_pathways --limit 50

Organism codes:
    hsa = Homo sapiens (human)
    mmu = Mus musculus (mouse)
    dme = Drosophila melanogaster
    sce = Saccharomyces cerevisiae (yeast)
    eco = Escherichia coli
"""

import sys
import os
import argparse
import csv
from collections import Counter
from bioservices import KEGG


def get_all_pathways(kegg, organism):
    """Get all pathway IDs for organism."""
    print(f"\nRetrieving pathways for {organism}...")

    kegg.organism = organism
    pathway_ids = kegg.pathwayIds

    print(f"✓ Found {len(pathway_ids)} pathways")

    return pathway_ids


def analyze_pathway(kegg, pathway_id):
    """Analyze single pathway for size and interactions."""
    try:
        # Parse KGML pathway
        kgml = kegg.parse_kgml_pathway(pathway_id)

        entries = kgml.get('entries', [])
        relations = kgml.get('relations', [])

        # Count relation types
        relation_types = Counter()
        for rel in relations:
            rel_type = rel.get('name', 'unknown')
            relation_types[rel_type] += 1

        # Get pathway name
        try:
            entry = kegg.get(pathway_id)
            pathway_name = "Unknown"
            for line in entry.split("\n"):
                if line.startswith("NAME"):
                    pathway_name = line.replace("NAME", "").strip()
                    break
        except:
            pathway_name = "Unknown"

        result = {
            'pathway_id': pathway_id,
            'pathway_name': pathway_name,
            'num_entries': len(entries),
            'num_relations': len(relations),
            'relation_types': dict(relation_types),
            'entries': entries,
            'relations': relations
        }

        return result

    except Exception as e:
        print(f"  ✗ Error analyzing {pathway_id}: {e}")
        return None


def analyze_all_pathways(kegg, pathway_ids, limit=None):
    """Analyze all pathways."""
    if limit:
        pathway_ids = pathway_ids[:limit]
        print(f"\n⚠ Limiting analysis to first {limit} pathways")

    print(f"\nAnalyzing {len(pathway_ids)} pathways...")

    results = []
    for i, pathway_id in enumerate(pathway_ids, 1):
        print(f"  [{i}/{len(pathway_ids)}] {pathway_id}", end="\r")

        result = analyze_pathway(kegg, pathway_id)
        if result:
            results.append(result)

    print(f"\n✓ Successfully analyzed {len(results)}/{len(pathway_ids)} pathways")

    return results


def save_pathway_summary(results, output_file):
    """Save pathway summary to CSV."""
    print(f"\nSaving pathway summary to {output_file}...")

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Pathway_ID',
            'Pathway_Name',
            'Num_Genes',
            'Num_Interactions',
            'Activation',
            'Inhibition',
            'Phosphorylation',
            'Binding',
            'Other'
        ])

        # Data
        for result in results:
            rel_types = result['relation_types']

            writer.writerow([
                result['pathway_id'],
                result['pathway_name'],
                result['num_entries'],
                result['num_relations'],
                rel_types.get('activation', 0),
                rel_types.get('inhibition', 0),
                rel_types.get('phosphorylation', 0),
                rel_types.get('binding/association', 0),
                sum(v for k, v in rel_types.items()
                    if k not in ['activation', 'inhibition', 'phosphorylation', 'binding/association'])
            ])

    print(f"✓ Summary saved")


def save_interactions_sif(results, output_file):
    """Save all interactions in SIF format."""
    print(f"\nSaving interactions to {output_file}...")

    with open(output_file, 'w') as f:
        for result in results:
            pathway_id = result['pathway_id']

            for rel in result['relations']:
                entry1 = rel.get('entry1', '')
                entry2 = rel.get('entry2', '')
                interaction_type = rel.get('name', 'interaction')

                # Write SIF format: source\tinteraction\ttarget
                f.write(f"{entry1}\t{interaction_type}\t{entry2}\n")

    print(f"✓ Interactions saved")


def save_detailed_pathway_info(results, output_dir):
    """Save detailed information for each pathway."""
    print(f"\nSaving detailed pathway files to {output_dir}/pathways/...")

    pathway_dir = os.path.join(output_dir, "pathways")
    os.makedirs(pathway_dir, exist_ok=True)

    for result in results:
        pathway_id = result['pathway_id'].replace(":", "_")
        filename = os.path.join(pathway_dir, f"{pathway_id}_interactions.csv")

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Source', 'Target', 'Interaction_Type', 'Link_Type'])

            for rel in result['relations']:
                writer.writerow([
                    rel.get('entry1', ''),
                    rel.get('entry2', ''),
                    rel.get('name', 'unknown'),
                    rel.get('link', 'unknown')
                ])

    print(f"✓ Detailed files saved for {len(results)} pathways")


def print_statistics(results):
    """Print analysis statistics."""
    print(f"\n{'='*70}")
    print("PATHWAY ANALYSIS STATISTICS")
    print(f"{'='*70}")

    # Total stats
    total_pathways = len(results)
    total_interactions = sum(r['num_relations'] for r in results)
    total_genes = sum(r['num_entries'] for r in results)

    print(f"\nOverall:")
    print(f"  Total pathways: {total_pathways}")
    print(f"  Total genes/proteins: {total_genes}")
    print(f"  Total interactions: {total_interactions}")

    # Largest pathways
    print(f"\nLargest pathways (by gene count):")
    sorted_by_size = sorted(results, key=lambda x: x['num_entries'], reverse=True)
    for i, result in enumerate(sorted_by_size[:10], 1):
        print(f"  {i}. {result['pathway_id']}: {result['num_entries']} genes")
        print(f"     {result['pathway_name']}")

    # Most connected pathways
    print(f"\nMost connected pathways (by interactions):")
    sorted_by_connections = sorted(results, key=lambda x: x['num_relations'], reverse=True)
    for i, result in enumerate(sorted_by_connections[:10], 1):
        print(f"  {i}. {result['pathway_id']}: {result['num_relations']} interactions")
        print(f"     {result['pathway_name']}")

    # Interaction type distribution
    print(f"\nInteraction type distribution:")
    all_types = Counter()
    for result in results:
        for rel_type, count in result['relation_types'].items():
            all_types[rel_type] += count

    for rel_type, count in all_types.most_common():
        percentage = (count / total_interactions) * 100 if total_interactions > 0 else 0
        print(f"  {rel_type}: {count} ({percentage:.1f}%)")


def main():
    """Main analysis workflow."""
    parser = argparse.ArgumentParser(
        description="Analyze KEGG pathways for an organism",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pathway_analysis.py hsa ./human_pathways
  python pathway_analysis.py mmu ./mouse_pathways --limit 50

Organism codes:
  hsa = Homo sapiens (human)
  mmu = Mus musculus (mouse)
  dme = Drosophila melanogaster
  sce = Saccharomyces cerevisiae (yeast)
  eco = Escherichia coli
        """
    )
    parser.add_argument("organism", help="KEGG organism code (e.g., hsa, mmu)")
    parser.add_argument("output_dir", help="Output directory for results")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit analysis to first N pathways")

    args = parser.parse_args()

    print("=" * 70)
    print("BIOSERVICES: KEGG Pathway Network Analysis")
    print("=" * 70)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize KEGG
    kegg = KEGG()

    # Get all pathways
    pathway_ids = get_all_pathways(kegg, args.organism)

    if not pathway_ids:
        print(f"\n✗ No pathways found for {args.organism}")
        sys.exit(1)

    # Analyze pathways
    results = analyze_all_pathways(kegg, pathway_ids, args.limit)

    if not results:
        print("\n✗ No pathways successfully analyzed")
        sys.exit(1)

    # Print statistics
    print_statistics(results)

    # Save results
    summary_file = os.path.join(args.output_dir, "pathway_summary.csv")
    save_pathway_summary(results, summary_file)

    sif_file = os.path.join(args.output_dir, "all_interactions.sif")
    save_interactions_sif(results, sif_file)

    save_detailed_pathway_info(results, args.output_dir)

    # Final summary
    print(f"\n{'='*70}")
    print("OUTPUT FILES")
    print(f"{'='*70}")
    print(f"  Summary: {summary_file}")
    print(f"  Interactions: {sif_file}")
    print(f"  Detailed: {args.output_dir}/pathways/")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
```

### `scripts/protein_analysis_workflow.py`

```python
#!/usr/bin/env python3
"""
Complete Protein Analysis Workflow

This script performs a comprehensive protein analysis pipeline:
1. UniProt search and identifier retrieval
2. FASTA sequence retrieval
3. BLAST similarity search
4. KEGG pathway discovery
5. PSICQUIC interaction mapping
6. GO annotation retrieval

Usage:
    export NCBI_EMAIL=you@lab.org
    python protein_analysis_workflow.py PROTEIN_NAME [EMAIL] [--skip-blast]

Examples:
    python protein_analysis_workflow.py ZAP70_HUMAN
    python protein_analysis_workflow.py P43403 user@example.com --skip-blast

Note: BLAST searches can take several minutes. Use --skip-blast to skip this step.
Email is read from NCBI_EMAIL when the optional EMAIL argument is omitted.
"""

import os
import re
import sys
import time
import argparse
from bioservices import UniProt, KEGG, NCBIblast, QuickGO

try:
    # PSICQUIC is not shipped by every bioservices release (it is absent from
    # 1.16.0). Importing it unconditionally would take the whole workflow down
    # over one optional step, so degrade instead.
    from bioservices import PSICQUIC
except ImportError:  # pragma: no cover - depends on the installed release
    PSICQUIC = None

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def resolve_ncbi_email(cli_email=None):
    """Return a validated NCBI contact email from CLI or NCBI_EMAIL."""
    email = (cli_email or os.environ.get("NCBI_EMAIL", "")).strip()
    if email and _EMAIL_RE.match(email):
        return email
    return None


def search_protein(query):
    """Search UniProt for protein and retrieve basic information."""
    print(f"\n{'='*70}")
    print("STEP 1: UniProt Search")
    print(f"{'='*70}")

    u = UniProt(verbose=False)

    print(f"Searching for: {query}")

    # Try direct retrieval first (if query looks like accession)
    if len(query) == 6 and query[0] in "OPQ":
        try:
            entry = u.retrieve(query, frmt="tab")
            if entry:
                uniprot_id = query
                print(f"✓ Found UniProt entry: {uniprot_id}")
                return u, uniprot_id
        except:
            pass

    # Otherwise search
    results = u.search(query, frmt="tab", columns="id,genes,organism,length,protein names", limit=5)

    if not results:
        print("✗ No results found")
        return u, None

    lines = results.strip().split("\n")
    if len(lines) < 2:
        print("✗ No entries found")
        return u, None

    # Display results
    print(f"\n✓ Found {len(lines)-1} result(s):")
    for i, line in enumerate(lines[1:], 1):
        fields = line.split("\t")
        print(f"  {i}. {fields[0]} - {fields[1]} ({fields[2]})")

    # Use first result
    first_entry = lines[1].split("\t")
    uniprot_id = first_entry[0]
    gene_names = first_entry[1] if len(first_entry) > 1 else "N/A"
    organism = first_entry[2] if len(first_entry) > 2 else "N/A"
    length = first_entry[3] if len(first_entry) > 3 else "N/A"
    protein_name = first_entry[4] if len(first_entry) > 4 else "N/A"

    print(f"\nUsing first result:")
    print(f"  UniProt ID: {uniprot_id}")
    print(f"  Gene names: {gene_names}")
    print(f"  Organism: {organism}")
    print(f"  Length: {length} aa")
    print(f"  Protein: {protein_name}")

    return u, uniprot_id


def retrieve_sequence(uniprot, uniprot_id):
    """Retrieve FASTA sequence for protein."""
    print(f"\n{'='*70}")
    print("STEP 2: FASTA Sequence Retrieval")
    print(f"{'='*70}")

    try:
        sequence = uniprot.retrieve(uniprot_id, frmt="fasta")

        if sequence:
            # Extract sequence only (remove header)
            lines = sequence.strip().split("\n")
            header = lines[0]
            seq_only = "".join(lines[1:])

            print(f"✓ Retrieved sequence:")
            print(f"  Header: {header}")
            print(f"  Length: {len(seq_only)} residues")
            print(f"  First 60 residues: {seq_only[:60]}...")

            return seq_only
        else:
            print("✗ Failed to retrieve sequence")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def run_blast(sequence, email, skip=False):
    """Run BLAST similarity search."""
    print(f"\n{'='*70}")
    print("STEP 3: BLAST Similarity Search")
    print(f"{'='*70}")

    if skip:
        print("⊘ Skipped (--skip-blast flag)")
        return None

    if not email:
        print("⊘ Skipped (set NCBI_EMAIL or pass email for BLAST)")
        return None

    try:
        print(f"Submitting BLASTP job...")
        print(f"  Database: uniprotkb")
        print(f"  Sequence length: {len(sequence)} aa")

        s = NCBIblast(verbose=False)

        jobid = s.run(
            program="blastp",
            sequence=sequence,
            stype="protein",
            database="uniprotkb",
            email=email
        )

        print(f"✓ Job submitted: {jobid}")
        print(f"  Waiting for completion...")

        # Poll for completion
        max_wait = 300  # 5 minutes
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status = s.getStatus(jobid)
            elapsed = int(time.time() - start_time)
            print(f"  Status: {status} (elapsed: {elapsed}s)", end="\r")

            if status == "FINISHED":
                print(f"\n✓ BLAST completed in {elapsed}s")

                # Retrieve results
                results = s.getResult(jobid, "out")

                # Parse and display summary
                lines = results.split("\n")
                print(f"\n  Results preview:")
                for line in lines[:20]:
                    if line.strip():
                        print(f"    {line}")

                return results

            elif status == "ERROR":
                print(f"\n✗ BLAST job failed")
                return None

            time.sleep(5)

        print(f"\n✗ Timeout after {max_wait}s")
        return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def discover_pathways(uniprot, kegg, uniprot_id):
    """Discover KEGG pathways for protein."""
    print(f"\n{'='*70}")
    print("STEP 4: KEGG Pathway Discovery")
    print(f"{'='*70}")

    try:
        # Map UniProt → KEGG
        print(f"Mapping {uniprot_id} to KEGG...")
        kegg_mapping = uniprot.mapping(fr="UniProtKB_AC-ID", to="KEGG", query=uniprot_id)

        if not kegg_mapping or uniprot_id not in kegg_mapping:
            print("✗ No KEGG mapping found")
            return []

        kegg_ids = kegg_mapping[uniprot_id]
        print(f"✓ KEGG ID(s): {kegg_ids}")

        # Get pathways for first KEGG ID
        kegg_id = kegg_ids[0]
        organism, gene_id = kegg_id.split(":")

        print(f"\nSearching pathways for {kegg_id}...")
        pathways = kegg.get_pathway_by_gene(gene_id, organism)

        if not pathways:
            print("✗ No pathways found")
            return []

        print(f"✓ Found {len(pathways)} pathway(s):\n")

        # Get pathway names
        pathway_info = []
        for pathway_id in pathways:
            try:
                entry = kegg.get(pathway_id)

                # Extract pathway name
                pathway_name = "Unknown"
                for line in entry.split("\n"):
                    if line.startswith("NAME"):
                        pathway_name = line.replace("NAME", "").strip()
                        break

                pathway_info.append((pathway_id, pathway_name))
                print(f"  • {pathway_id}: {pathway_name}")

            except Exception as e:
                print(f"  • {pathway_id}: [Error retrieving name]")

        return pathway_info

    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def find_interactions(protein_query):
    """Find protein-protein interactions via PSICQUIC."""
    print(f"\n{'='*70}")
    print("STEP 5: Protein-Protein Interactions")
    print(f"{'='*70}")

    if PSICQUIC is None:
        print("⊘ Skipped (this bioservices release does not ship PSICQUIC)")
        return []

    try:
        p = PSICQUIC()

        # Try querying MINT database
        query = f"{protein_query} AND species:9606"
        print(f"Querying MINT database...")
        print(f"  Query: {query}")

        results = p.query("mint", query)

        if not results:
            print("✗ No interactions found in MINT")
            return []

        # Parse PSI-MI TAB format
        lines = results.strip().split("\n")
        print(f"✓ Found {len(lines)} interaction(s):\n")

        # Display first 10 interactions
        interactions = []
        for i, line in enumerate(lines[:10], 1):
            fields = line.split("\t")
            if len(fields) >= 12:
                protein_a = fields[4].split(":")[1] if ":" in fields[4] else fields[4]
                protein_b = fields[5].split(":")[1] if ":" in fields[5] else fields[5]
                interaction_type = fields[11]

                interactions.append((protein_a, protein_b, interaction_type))
                print(f"  {i}. {protein_a} ↔ {protein_b}")

        if len(lines) > 10:
            print(f"  ... and {len(lines)-10} more")

        return interactions

    except Exception as e:
        print(f"✗ Error: {e}")
        return []


def get_go_annotations(uniprot_id):
    """Retrieve GO annotations."""
    print(f"\n{'='*70}")
    print("STEP 6: Gene Ontology Annotations")
    print(f"{'='*70}")

    try:
        g = QuickGO()

        print(f"Retrieving GO annotations for {uniprot_id}...")
        annotations = g.Annotation(protein=uniprot_id, format="tsv")

        if not annotations:
            print("✗ No GO annotations found")
            return []

        lines = annotations.strip().split("\n")
        print(f"✓ Found {len(lines)-1} annotation(s)\n")

        # Group by aspect
        aspects = {"P": [], "F": [], "C": []}
        for line in lines[1:]:
            fields = line.split("\t")
            if len(fields) >= 9:
                go_id = fields[6]
                go_term = fields[7]
                go_aspect = fields[8]

                if go_aspect in aspects:
                    aspects[go_aspect].append((go_id, go_term))

        # Display summary
        print(f"  Biological Process (P): {len(aspects['P'])} terms")
        for go_id, go_term in aspects['P'][:5]:
            print(f"    • {go_id}: {go_term}")
        if len(aspects['P']) > 5:
            print(f"    ... and {len(aspects['P'])-5} more")

        print(f"\n  Molecular Function (F): {len(aspects['F'])} terms")
        for go_id, go_term in aspects['F'][:5]:
            print(f"    • {go_id}: {go_term}")
        if len(aspects['F']) > 5:
            print(f"    ... and {len(aspects['F'])-5} more")

        print(f"\n  Cellular Component (C): {len(aspects['C'])} terms")
        for go_id, go_term in aspects['C'][:5]:
            print(f"    • {go_id}: {go_term}")
        if len(aspects['C']) > 5:
            print(f"    ... and {len(aspects['C'])-5} more")

        return aspects

    except Exception as e:
        print(f"✗ Error: {e}")
        return {}


def main():
    """Main workflow."""
    parser = argparse.ArgumentParser(
        description="Complete protein analysis workflow using BioServices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  export NCBI_EMAIL=you@lab.org
  python protein_analysis_workflow.py ZAP70_HUMAN
  python protein_analysis_workflow.py P43403 user@example.com --skip-blast
        """
    )
    parser.add_argument("protein", help="Protein name or UniProt ID")
    parser.add_argument(
        "email",
        nargs="?",
        default=None,
        help="NCBI contact email (optional if NCBI_EMAIL is set)",
    )
    parser.add_argument("--skip-blast", action="store_true",
                       help="Skip BLAST search (faster)")

    args = parser.parse_args()

    print("=" * 70)
    print("BIOSERVICES: Complete Protein Analysis Workflow")
    print("=" * 70)

    # Step 1: Search protein
    uniprot, uniprot_id = search_protein(args.protein)
    if not uniprot_id:
        print("\n✗ Failed to find protein. Exiting.")
        sys.exit(1)

    # Step 2: Retrieve sequence
    sequence = retrieve_sequence(uniprot, uniprot_id)
    if not sequence:
        print("\n⚠ Warning: Could not retrieve sequence")

    # Step 3: BLAST search
    ncbi_email = resolve_ncbi_email(args.email)
    if sequence:
        blast_results = run_blast(sequence, ncbi_email, args.skip_blast)

    # Step 4: Pathway discovery
    kegg = KEGG()
    pathways = discover_pathways(uniprot, kegg, uniprot_id)

    # Step 5: Interaction mapping
    interactions = find_interactions(args.protein)

    # Step 6: GO annotations
    go_terms = get_go_annotations(uniprot_id)

    # Summary
    print(f"\n{'='*70}")
    print("WORKFLOW SUMMARY")
    print(f"{'='*70}")
    print(f"  Protein: {args.protein}")
    print(f"  UniProt ID: {uniprot_id}")
    print(f"  Sequence: {'✓' if sequence else '✗'}")
    print(f"  BLAST: {'✓' if not args.skip_blast and sequence else '⊘'}")
    print(f"  Pathways: {len(pathways)} found")
    print(f"  Interactions: {len(interactions)} found")
    print(f"  GO annotations: {sum(len(v) for v in go_terms.values())} found")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
```
