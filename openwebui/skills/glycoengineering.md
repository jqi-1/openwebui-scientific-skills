---
name: glycoengineering
description: Analyze and engineer protein glycosylation. Scan sequences for N-glycosylation sequons (N-X-S/T), predict O-glycosylation hotspots, and access curated glycoengineering tools (NetOGlyc, GlycoShield, GlycoWorkbench). For glycoprotein engineering, therapeutic antibody optimization, and vaccine design.
---

# Glycoengineering

## Overview

Glycosylation is the most common and complex post-translational modification (PTM) of proteins, affecting over 50% of all human proteins. Glycans regulate protein folding, stability, immune recognition, receptor interactions, and pharmacokinetics of therapeutic proteins. Glycoengineering involves rational modification of glycosylation patterns for improved therapeutic efficacy, stability, or immune evasion.

**Two major glycosylation types:**
- **N-glycosylation**: Attached to asparagine (N) in the sequon N-X-[S/T] where X ≠ Proline; occurs in the ER/Golgi
- **O-glycosylation**: Attached to serine (S) or threonine (T); no strict consensus motif; primarily GalNAc initiation

## When to Use This Skill

Use this skill when:

- **Antibody engineering**: Optimize Fc glycosylation for enhanced ADCC, CDC, or reduced immunogenicity
- **Therapeutic protein design**: Identify glycosylation sites that affect half-life, stability, or immunogenicity
- **Vaccine antigen design**: Engineer glycan shields to focus immune responses on conserved epitopes
- **Biosimilar characterization**: Compare glycan patterns between reference and biosimilar
- **Drug target analysis**: Does glycosylation affect target engagement for a receptor?
- **Protein stability**: N-glycans often stabilize proteins; identify sites for stabilizing mutations

## N-Glycosylation Sequon Analysis

### Scanning for N-Glycosylation Sites

N-glycosylation occurs at the sequon **N-X-[S/T]** where X ≠ Proline.

```python
import re
from typing import List, Tuple

def find_n_glycosylation_sequons(sequence: str) -> List[dict]:
    """
    Scan a protein sequence for canonical N-linked glycosylation sequons.
    Motif: N-X-[S/T], where X ≠ Proline.

    Args:
        sequence: Single-letter amino acid sequence

    Returns:
        List of dicts with position (1-based), motif, and context
    """
    seq = sequence.upper()
    results = []
    i = 0
    while i <= len(seq) - 3:
        triplet = seq[i:i+3]
        if triplet[0] == 'N' and triplet[1] != 'P' and triplet[2] in {'S', 'T'}:
            context = seq[max(0, i-3):i+6]  # ±3 residue context
            results.append({
                'position': i + 1,   # 1-based
                'motif': triplet,
                'context': context,
                'sequon_type': 'NXS' if triplet[2] == 'S' else 'NXT'
            })
            i += 3
        else:
            i += 1
    return results

def summarize_glycosylation_sites(sequence: str, protein_name: str = "") -> str:
    """Generate a research log summary of N-glycosylation sites."""
    sequons = find_n_glycosylation_sequons(sequence)

    lines = [f"# N-Glycosylation Sequon Analysis: {protein_name or 'Protein'}"]
    lines.append(f"Sequence length: {len(sequence)}")
    lines.append(f"Total N-glycosylation sequons: {len(sequons)}")

    if sequons:
        lines.append(f"\nN-X-S sites: {sum(1 for s in sequons if s['sequon_type'] == 'NXS')}")
        lines.append(f"N-X-T sites: {sum(1 for s in sequons if s['sequon_type'] == 'NXT')}")
        lines.append(f"\nSite details:")
        for s in sequons:
            lines.append(f"  Position {s['position']}: {s['motif']} (context: ...{s['context']}...)")
    else:
        lines.append("No canonical N-glycosylation sequons detected.")

    return "\n".join(lines)

# Example: IgG1 Fc region
fc_sequence = "APELLGGPSVFLFPPKPKDTLMISRTPEVTCVVVDVSHEDPEVKFNWYVDGVEVHNAKTKPREEQYNSTYRVVSVLTVLHQDWLNGKEYKCKVSNKALPAPIEKTISKAKGQPREPQVYTLPPSREEMTKNQVSLTCLVKGFYPSDIAVEWESNGQPENNYKTTPPVLDSDGSFFLYSKLTVDKSRWQQGNVFSCSVMHEALHNHYTQKSLSLSPGK"
print(summarize_glycosylation_sites(fc_sequence, "IgG1 Fc"))
```

### Mutating N-Glycosylation Sites

```python
def eliminate_glycosite(sequence: str, position: int, replacement: str = "Q") -> str:
    """
    Eliminate an N-glycosylation site by substituting Asn → Gln (conservative).

    Args:
        sequence: Protein sequence
        position: 1-based position of the Asn to mutate
        replacement: Amino acid to substitute (default Q = Gln; similar size, not glycosylated)

    Returns:
        Mutated sequence
    """
    seq = list(sequence.upper())
    idx = position - 1
    assert seq[idx] == 'N', f"Position {position} is '{seq[idx]}', not 'N'"
    seq[idx] = replacement.upper()
    return ''.join(seq)

def add_glycosite(sequence: str, position: int, flanking_context: str = "S") -> str:
    """
    Introduce an N-glycosylation site by mutating a residue to Asn,
    and ensuring X ≠ Pro and +2 = S/T.

    Args:
        position: 1-based position to introduce Asn
        flanking_context: 'S' or 'T' at position+2 (if modification needed)
    """
    seq = list(sequence.upper())
    idx = position - 1

    # Mutate to Asn
    seq[idx] = 'N'

    # Ensure X+1 != Pro (mutate to Ala if needed)
    if idx + 1 < len(seq) and seq[idx + 1] == 'P':
        seq[idx + 1] = 'A'

    # Ensure X+2 = S or T
    if idx + 2 < len(seq) and seq[idx + 2] not in ('S', 'T'):
        seq[idx + 2] = flanking_context

    return ''.join(seq)
```

## O-Glycosylation Analysis

### Heuristic O-Glycosylation Hotspot Prediction

```python
def predict_o_glycosylation_hotspots(
    sequence: str,
    window: int = 7,
    min_st_fraction: float = 0.4,
    disallow_proline_next: bool = True
) -> List[dict]:
    """
    Heuristic O-glycosylation hotspot scoring based on local S/T density.
    Not a substitute for NetOGlyc; use as fast baseline.

    Rules:
    - O-GalNAc glycosylation clusters on Ser/Thr-rich segments
    - Flag Ser/Thr residues in windows enriched for S/T
    - Avoid S/T immediately followed by Pro (TP/SP motifs inhibit GalNAc-T)

    Args:
        window: Odd window size for local S/T density
        min_st_fraction: Minimum fraction of S/T in window to flag site
    """
    if window % 2 == 0:
        window = 7
    seq = sequence.upper()
    half = window // 2
    candidates = []

    for i, aa in enumerate(seq):
        if aa not in ('S', 'T'):
            continue
        if disallow_proline_next and i + 1 < len(seq) and seq[i+1] == 'P':
            continue

        start = max(0, i - half)
        end = min(len(seq), i + half + 1)
        segment = seq[start:end]
        st_count = sum(1 for c in segment if c in ('S', 'T'))
        frac = st_count / len(segment)

        if frac >= min_st_fraction:
            candidates.append({
                'position': i + 1,
                'residue': aa,
                'st_fraction': round(frac, 3),
                'window': f"{start+1}-{end}",
                'segment': segment
            })

    return candidates
```

## External Glycoengineering Tools

### 1. NetOGlyc 4.0 (O-glycosylation prediction)

Web service for high-accuracy O-GalNAc site prediction:
- **URL**: https://services.healthtech.dtu.dk/services/NetOGlyc-4.0/
- **Input**: FASTA protein sequence
- **Output**: Per-residue O-glycosylation probability scores
- **Method**: Neural network trained on experimentally verified O-GalNAc sites

```python
import requests

def submit_netoglycv4(fasta_sequence: str) -> str:
    """
    Submit sequence to NetOGlyc 4.0 web service.
    Returns the job URL for result retrieval.

    Note: This uses the DTU Health Tech web service. Results take ~1-5 min.
    """
    url = "https://services.healthtech.dtu.dk/cgi-bin/webface2.cgi"
    # NetOGlyc submission (parameters may vary with web service version)
    # Recommend using the web interface directly for most use cases
    print("Submit sequence at: https://services.healthtech.dtu.dk/services/NetOGlyc-4.0/")
    return url

# Also: NetNGlyc for N-glycosylation prediction
# URL: https://services.healthtech.dtu.dk/services/NetNGlyc-1.0/
```

### 2. GlycoSHIELD (Glycan Shielding Analysis)

GlycoSHIELD grafts libraries of pre-simulated glycan conformers onto a static protein structure and
scores how much of the protein surface the glycans shield, without running new MD
(Tsai et al., *Cell* 2024, doi:10.1016/j.cell.2024.01.034):
- **URL**: https://gitlab.mpcdf.mpg.de/dioscuri-biophysics/glycoshield-md/ (web app: https://glycoshield.eu)
- **Use**: Model the glycan shield on a glycoprotein and map per-residue shielding
- **Output**: Glycosylated PDB/XTC ensembles per site, per-residue shielding plot, PDB with shielding in the B-factor column

GlycoSHIELD is **not on PyPI** — `uv pip install glycoshield` fails. It ships as three scripts on top
of a small `glycoshield` package (needs numpy, scipy, matplotlib, MDAnalysis; `GlycoSASA.py` also needs
`gmx` from GROMACS on `PATH`). Install from the checkout:

```bash
# Installation (GPL-3.0). Glycan conformer libraries are downloaded separately —
# see glycan_library_downloader.py and GLYCAN_LIBRARY/ in the repository.
git clone https://gitlab.mpcdf.mpg.de/dioscuri-biophysics/glycoshield-md.git
cd glycoshield-md
uv pip install -e .

# 1. Graft glycan conformers onto each sequon listed in the input file.
#    One line per site: <chain> <res-1,res,res+1> <1,2,3> <glycan.pdb> <glycan.xtc> <out.pdb> <out.xtc>
python GlycoSHIELD.py --protpdb protein.pdb --inputfile sequons_input \
    --threshold 3.5 --mode CG --shuffle-sugar

# 2. Per-residue shielding score across the grafted ensembles (probe radii in nm)
python GlycoSASA.py --pdblist A_463.pdb,A_492.pdb --xtclist A_463.xtc,A_492.xtc \
    --probelist 0.14,0.25 --plottrace
```

Illustrative: the flags come from the scripts' argparse definitions and the upstream tutorial
(N-cadherin EC5 with Man5 glycans); they were not run here. `--mode CG` checks clashes against
Cα atoms only and pairs with `--threshold 3.5`; `--mode All` with `--threshold 0.7` is the all-atom
setting.

### 3. GlycoWorkbench (Glycan Structure Drawing/Analysis)

- **URL**: https://www.eurocarbdb.org/project/glycoworkbench
- **Use**: Draw glycan structures, calculate masses, annotate MS spectra
- **Format**: GlycoCT, IUPAC condensed glycan notation

### 4. GlyConnect (Glycan-Protein Database)

- **URL**: https://glyconnect.expasy.org/
- **Use**: Find experimentally verified glycoproteins and glycosylation sites
- **Query**: By protein (UniProt ID), glycan structure, or tissue

```python
import requests

def query_glyconnect(uniprot_id: str) -> dict:
    """Query GlyConnect for glycosylation data for a protein."""
    url = f"https://glyconnect.expasy.org/api/proteins/uniprot/{uniprot_id}"
    response = requests.get(url, headers={"Accept": "application/json"})
    if response.status_code == 200:
        return response.json()
    return {}

# Example: query EGFR glycosylation
egfr_glyco = query_glyconnect("P00533")
```

### 5. UniCarbKB (Glycan Structure Database)

- **URL**: https://unicarbkb.org/
- **Use**: Browse glycan structures, search by mass or composition
- **Format**: GlycoCT or IUPAC notation

## Key Glycoengineering Strategies

### For Therapeutic Antibodies

| Goal | Strategy | Notes |
|------|----------|-------|
| Enhance ADCC | Defucosylation at Fc Asn297 | Afucosylated IgG1 has ~50× better FcγRIIIa binding |
| Reduce immunogenicity | Remove non-human glycans | Eliminate α-Gal, NGNA epitopes |
| Improve PK half-life | Sialylation | Sialylated glycans extend half-life |
| Reduce inflammation | Hypersialylation | IVIG anti-inflammatory mechanism |
| Create glycan shield | Add N-glycosites to surface | Masks vulnerable epitopes (vaccine design) |

### Common Mutations Used

| Mutation | Effect |
|----------|--------|
| N297A/Q (IgG1) | Removes Fc glycosylation (aglycosyl) |
| N297D (IgG1) | Removes Fc glycosylation |
| S298A/E333A/K334A | Increases FcγRIIIa binding |
| F243L (IgG1) | Increases defucosylation |
| T299A | Removes Fc glycosylation |

## Glycan Notation

### IUPAC Condensed Notation (Monosaccharide abbreviations)

| Symbol | Full Name | Type |
|--------|-----------|------|
| Glc | Glucose | Hexose |
| GlcNAc | N-Acetylglucosamine | HexNAc |
| Man | Mannose | Hexose |
| Gal | Galactose | Hexose |
| Fuc | Fucose | Deoxyhexose |
| Neu5Ac | N-Acetylneuraminic acid (Sialic acid) | Sialic acid |
| GalNAc | N-Acetylgalactosamine | HexNAc |

### Complex N-Glycan Structure

```
Typical complex biantennary N-glycan:
Neu5Ac-Gal-GlcNAc-Man\
                       Man-GlcNAc-GlcNAc-[Asn]
Neu5Ac-Gal-GlcNAc-Man/
(±Core Fuc at innermost GlcNAc)
```

## Best Practices

- **Start with NetNGlyc/NetOGlyc** for computational prediction before experimental validation
- **Verify with mass spectrometry**: Glycoproteomics (Byonic, Mascot) for site-specific glycan profiling
- **Consider site context**: Not all predicted sequons are actually glycosylated (accessibility, cell type, protein conformation)
- **For antibodies**: Fc N297 glycan is critical — always characterize this site first
- **Use GlyConnect** to check if your protein of interest has experimentally verified glycosylation data

## Additional Resources

- **GlyTouCan** (glycan structure repository): https://glytoucan.org/
- **GlyConnect**: https://glyconnect.expasy.org/
- **CFG Functional Glycomics**: http://www.functionalglycomics.org/
- **DTU Health Tech servers** (NetNGlyc, NetOGlyc): https://services.healthtech.dtu.dk/
- **GlycoWorkbench**: https://glycoworkbench.software.informer.com/
- **Review**: Apweiler R et al. (1999) Biochim Biophys Acta. PMID: 10564035
- **Therapeutic glycoengineering review**: Jefferis R (2009) Nature Reviews Drug Discovery. PMID: 19448661

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/glycoengineering/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/glycan_databases.md`

# Glycan Databases and Resources Reference

## Primary Databases

### GlyTouCan
- **URL**: https://glytoucan.org/
- **Content**: Unique accession numbers (GTC IDs) for glycan structures
- **Use**: Standardized glycan identification across databases
- **Format**: GlycoCT, WURCS, IUPAC

```python
import requests

def lookup_glytoucan(glytoucan_id: str) -> dict:
    """Fetch glycan details from GlyTouCan."""
    url = f"https://api.glytoucan.org/glycan/{glytoucan_id}"
    response = requests.get(url, headers={"Accept": "application/json"})
    return response.json() if response.ok else {}
```

### GlyConnect
- **URL**: https://glyconnect.expasy.org/
- **Content**: Protein glycosylation database with site-specific glycan profiles
- **Integration**: Links UniProt proteins to experimentally verified glycosylation
- **Use**: Look up known glycosylation for your target protein

```python
import requests

def get_glycoprotein_info(uniprot_id: str) -> dict:
    """Get glycosylation data for a protein from GlyConnect."""
    base_url = "https://glyconnect.expasy.org/api"
    response = requests.get(f"{base_url}/proteins/uniprot/{uniprot_id}")
    return response.json() if response.ok else {}

def get_glycan_compositions(glyconnect_protein_id: int) -> list:
    """Get all glycan compositions for a GlyConnect protein entry."""
    base_url = "https://glyconnect.expasy.org/api"
    response = requests.get(f"{base_url}/compositions/protein/{glyconnect_protein_id}")
    return response.json().get("data", []) if response.ok else []
```

### UniCarbKB
- **URL**: https://unicarbkb.org/
- **Content**: Curated glycan structures with biological context
- **Features**: Tissue/cell-type specific glycan data, mass spectrometry data

### KEGG Glycan
- **URL**: https://www.genome.jp/kegg/glycan/
- **Content**: Glycan structures in KEGG format, biosynthesis pathways
- **Integration**: Links to KEGG PATHWAY maps for glycan biosynthesis

### CAZy (Carbohydrate-Active Enzymes)
- **URL**: http://www.cazy.org/
- **Content**: Enzymes that build, break, and modify glycans
- **Use**: Identify enzymes for glycoengineering applications

## Prediction Servers

### NetNGlyc 1.0
- **URL**: https://services.healthtech.dtu.dk/services/NetNGlyc-1.0/
- **Method**: Neural network for N-glycosylation site prediction
- **Input**: Protein FASTA sequence
- **Output**: Per-asparagine probability score; threshold ~0.5

### NetOGlyc 4.0
- **URL**: https://services.healthtech.dtu.dk/services/NetOGlyc-4.0/
- **Method**: Neural network for O-GalNAc glycosylation prediction
- **Input**: Protein FASTA sequence
- **Output**: Per-serine/threonine probability; threshold ~0.5

### GlycoMine (Machine Learning)
- Machine learning predictor for N-, O- and C-glycosylation
- Multiple glycan types: N-GlcNAc, O-GalNAc, O-GlcNAc, O-Man, O-Fuc, O-Glc, C-Man

### SymLink (Glycosylation site & sequon predictor)
- Species-specific N-glycosylation prediction
- More specific than simple sequon scanning

## Mass Spectrometry Glycoproteomics Tools

### Byonic (Protein Metrics)
- De novo glycopeptide identification from MS2 spectra
- Comprehensive glycan database
- Site-specific glycoform assignment

### Mascot Glycan Analysis
- Glycan-specific search parameters
- Common for bottom-up glycoproteomics

### GlycoWorkbench
- **URL**: https://www.eurocarbdb.org/project/glycoworkbench
- Glycan structure drawing and mass calculation
- Annotation of MS/MS spectra with glycan fragment ions

### Skyline
- Targeted quantification of glycopeptides
- Integrates with glycan database

## Glycan Nomenclature Systems

### Oxford Notation (For N-glycans)
Codes complex N-glycans as text strings:
```
G0F   = Core-fucosylated, biantennary, no galactose
G1F   = Core-fucosylated, one galactose
G2F   = Core-fucosylated, two galactoses
G2FS1 = Core-fucosylated, two galactoses, one sialic acid
G2FS2 = Core-fucosylated, two galactoses, two sialic acids
M5    = High mannose 5 (Man5GlcNAc2)
M9    = High mannose 9 (Man9GlcNAc2)
```

### Symbol Nomenclature for Glycans (SNFG)
Standard colored symbols for publications:
- Blue circle = Glucose
- Green circle = Mannose
- Yellow circle = Galactose
- Blue square = N-Acetylglucosamine
- Yellow square = N-Acetylgalactosamine
- Purple diamond = N-Acetylneuraminic acid (sialic acid)
- Red triangle = Fucose

## Therapeutic Glycoproteins and Key Glycosylation Sites

| Therapeutic | Target | Key Glycosylation | Function |
|-------------|--------|------------------|---------|
| IgG1 antibody | Various | N297 (Fc) | ADCC/CDC effector function |
| Erythropoietin | EPOR | N24, N38, N83, O-glycans | Pharmacokinetics |
| Etanercept | TNF | N420 (IgG1 Fc) | Half-life |
| tPA (alteplase) | Fibrin | N117, N184, N448 | Fibrin binding |
| Factor VIII | VWF | 25 N-glycosites | Clearance |

## Batch Analysis Example

```python
from glycoengineering_tools import find_n_glycosylation_sequons, predict_o_glycosylation_hotspots
import pandas as pd

def analyze_glycosylation_landscape(sequences_dict: dict) -> pd.DataFrame:
    """
    Batch analysis of glycosylation for multiple proteins.

    Args:
        sequences_dict: {protein_name: sequence}

    Returns:
        DataFrame with glycosylation summary per protein
    """
    results = []
    for name, seq in sequences_dict.items():
        n_sites = find_n_glycosylation_sequons(seq)
        o_sites = predict_o_glycosylation_hotspots(seq)

        results.append({
            'protein': name,
            'length': len(seq),
            'n_glycosites': len(n_sites),
            'o_glyco_hotspots': len(o_sites),
            'n_glyco_density': len(n_sites) / len(seq) * 100,
            'n_glyco_positions': [s['position'] for s in n_sites]
        })

    return pd.DataFrame(results)
```
