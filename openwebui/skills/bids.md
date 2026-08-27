---
name: bids
description: >
---

# Brain Imaging Data Structure (BIDS)

## Overview

The Brain Imaging Data Structure (BIDS) is a community standard for organizing and describing neuroscience and biomedical research datasets. It defines a consistent file naming convention, directory hierarchy, and metadata schema so that datasets are immediately understandable by humans and software tools alike. BIDS is governed by the BIDS Specification (currently v1.11.x) and is maintained by the community via the BIDS-Standard GitHub organization.

While BIDS originated for MRI, it has grown well beyond neuroimaging. The specification now covers 11 modalities spanning imaging, electrophysiology, and behavioral data:

- **Imaging**: MRI (structural, functional, diffusion, fieldmaps, perfusion/ASL), PET, microscopy
- **Electrophysiology**: EEG, MEG, iEEG (intracranial EEG), EMG
- **Other**: NIRS (near-infrared spectroscopy), motion capture, behavioral data (without imaging), MR spectroscopy

Active BEPs are extending BIDS further — notably BEP032 (microelectrode electrophysiology) will add support for extracellular recordings including Neuropixels probes, bringing BIDS to a prevalent methodology in animal neuroscience research (see also the neuropixels-analysis skill).

Adoption is required or strongly encouraged by major data repositories (OpenNeuro, DANDI), leading journals (NeuroImage, Human Brain Mapping, Scientific Data), and funding agencies (NIH, ERC).

The Python ecosystem for BIDS centers on **PyBIDS** (`pybids`) for querying and indexing BIDS datasets, and the **bids-validator** (Deno-based, available as PyPI package `bids-validator-deno` or via Deno directly) for compliance checking. Conversion from DICOM is typically done with **HeuDiConv**, **dcm2bids**, or **BIDScoin**.

## When to Use This Skill

Apply this skill when:
- Organizing raw neuroscience data (imaging, electrophysiology, behavioral) into BIDS-compliant directory structures
- Querying an existing BIDS dataset to find specific files by subject, session, task, run, or modality
- Validating a dataset against the BIDS specification before sharing or submission
- Converting DICOM data from scanners into BIDS format
- Writing or editing JSON sidecar metadata files
- Creating BIDS-compliant derivatives (preprocessed data, analysis outputs)
- Setting up a `dataset_description.json` for a new dataset
- Working with BIDS entities (subject, session, task, acquisition, run, etc.)
- Configuring `.bidsignore` to exclude files from validation
- Preparing data for upload to OpenNeuro, DANDI, or other BIDS-aware repositories

## Installation

```bash
# Core BIDS querying library
uv pip install pybids

# BIDS validator (Deno-based, installed via PyPI wrapper)
uv pip install bids-validator-deno
# Alternative: install directly via Deno
# deno install -g -A npm:bids-validator

# DICOM-to-BIDS converters (install as needed)
uv pip install heudiconv       # HeuDiConv - heuristic-based DICOM conversion
uv pip install dcm2bids        # dcm2bids - config-file-based conversion
# BIDScoin: uv pip install bidscoin

# Useful companions
uv pip install nibabel          # NIfTI/other neuroimaging file I/O
uv pip install pydicom          # DICOM file reading (used by converters)
```

## Core Workflows

Twelve workflow areas, each with worked code, are documented in
[references/core_workflows.md](references/core_workflows.md):

1. **BIDS directory structure** — the required layout and where each modality belongs.
2. **`dataset_description.json`** — the required fields and how to generate it.
3. **Querying with PyBIDS** — `BIDSLayout`, entity filters, sidecar metadata with
   automatic inheritance, and building paths from entities.
4. **Validation** — `bids-validator` via the PyPI wrapper (recommended), via Deno
   directly, the legacy Node validator, and using `.bidsignore` to exclude files.
5. **Entities and file naming** — the entity order and naming grammar.
6. **DICOM to BIDS conversion** — HeuDiConv (including the turnkey ReproIn path and the
   reconnaissance → heuristic → convert sequence) and dcm2bids (config-file based).
7. **Metadata sidecars** — required and recommended JSON fields per modality.
8. **Events files** — task fMRI event timing and column conventions.
9. **Participants file** — `participants.tsv` and its data dictionary.
10. **Derivatives** — the derivatives layout and its `dataset_description.json`.
11. **Advanced PyBIDS** — index caching, including derivatives, confound regressors, and
    DataFrame output.
12. **BIDS-Apps** — the standard invocation pattern, and fMRIPrep, MRIQC, and QSIPrep.

Validate early and often: PyBIDS validates structure when it indexes a dataset, so an
indexing failure usually means a naming or metadata problem rather than a code bug.

## Reference Materials

This skill includes detailed reference documentation:

- **bids_schema.json**: Machine-readable BIDS schema (from https://bids-specification.readthedocs.io/en/stable/schema.json). This is the authoritative source for entity definitions, ordering rules, filename templates, allowed suffixes per datatype, and metadata field requirements. BEP-specific schemas are at https://github.com/bids-standard/bids-schema/tree/main/BEPs.
- **beps.yml**: Current list of all BIDS Extension Proposals with titles, leads, status, and links (from [bids-website](https://github.com/bids-standard/bids-website/blob/main/data/beps/beps.yml))
- **bids_specification.md**: Human-readable summary of the entity table, datatype reference, directory structure rules, template spaces, and specification changelog
- **metadata_fields.md**: Required and recommended JSON sidecar fields for every BIDS modality (anat, func, dwi, fmap, eeg, meg, pet, etc.)
- **conversion_tools.md**: Detailed workflows for HeuDiConv, dcm2bids, and BIDScoin including heuristic/config examples and troubleshooting

Update schema and BEPs with: `python scripts/update_schema.py`

## Common Issues and Solutions

### 1. Validator reports "Not a BIDS dataset"
**Cause**: Missing `dataset_description.json` at the root.
**Fix**: Create the file with at minimum `{"Name": "...", "BIDSVersion": "1.10.0"}`.

### 2. Inconsistent subjects warning
**Cause**: Not all subjects have the same set of files (some missing sessions, runs, etc.).
**Fix**: This is a warning, not an error. Use `--ignoreSubjectConsistency` if intentional. Document missing data in `participants.tsv` or a `scans.tsv`.

### 3. Missing SliceTiming
**Cause**: `dcm2niix` couldn't extract slice timing from DICOM headers.
**Fix**: Determine slice order from the scan protocol and add manually to the JSON sidecar. Common patterns: ascending, descending, interleaved (odd-first or even-first).

### 4. Phase encoding direction confusion
**Cause**: Axis labels (i/j/k vs x/y/z vs LR/AP/SI) are confusing.
**Fix**: In BIDS, use NIfTI image axes: `i`=first axis, `j`=second, `k`=third. `-` means negative direction. For standard axial acquisitions: `j` is typically anterior-posterior. Verify with the acquisition protocol.

### 5. PyBIDS is slow on large datasets
**Cause**: Full filesystem indexing on every `BIDSLayout()` call.
**Fix**: Use `database_path` to cache the index to an SQLite file:
```python
layout = BIDSLayout("/data", database_path="/data/.pybids_cache.db")
```

### 6. Derivatives not found by PyBIDS
**Cause**: Derivatives directory missing its own `dataset_description.json`.
**Fix**: Every derivatives directory must have `dataset_description.json` with `"DatasetType": "derivative"`.

### 7. Events file timing is off
**Cause**: `onset` times are relative to the wrong reference (e.g., trigger time vs first volume).
**Fix**: Onsets must be in seconds relative to the first volume of that run's acquisition. Account for dummy scans if they were discarded.

### 8. TSV files fail validation
**Cause**: Encoding or delimiter issues (spaces instead of tabs, BOM characters, Windows line endings).
**Fix**: Ensure tab-separated values with UTF-8 encoding and Unix line endings (`\n`). Use `n/a` (not `NA`, `NaN`, or empty) for missing values.

## Best Practices

1. **Validate early and often** - Run the BIDS validator after every conversion or modification. Fix errors before they compound.

2. **Use metadata inheritance** - Place shared metadata (e.g., `TaskName`, scanner parameters) in top-level sidecar files rather than duplicating in every subject's directory.

3. **Keep sourcedata** - Store the original DICOM (or other raw) data under `sourcedata/` so conversions are reproducible. Add `sourcedata/` to `.bidsignore`.

4. **Use consistent naming from the start** - Define your BIDS naming scheme before data collection. Use the ReproIn naming convention for scan protocols to enable automatic conversion.

5. **Document your dataset** - Write a thorough `README` describing the study design, acquisition parameters, known issues, and any deviations from BIDS.

6. **Use scans.tsv for run-level metadata** - Record per-run acquisition times and quality notes:
   ```
   filename	acq_time	quality
   func/sub-01_task-rest_bold.nii.gz	2025-01-15T10:30:00	good
   ```

7. **Version your dataset** - Use `CHANGES` to document dataset modifications. Consider DataLad for full version control of large datasets.

8. **Deface anatomical images** - Remove facial features from T1w/T2w images before sharing (e.g., using `pydeface`, `mri_deface`, or `afni_refacer`). Store defaced versions as the primary data or use `_defacemask` files.

9. **Use BIDS URIs for provenance** - In derivatives, reference source files using BIDS URIs: `bids::sub-01/anat/sub-01_T1w.nii.gz`.

10. **Prefer community tools** - Use established BIDS-Apps (fMRIPrep, MRIQC, QSIPrep) rather than custom pipelines when possible. They handle BIDS I/O correctly and produce BIDS-compliant derivatives.

11. **Study bids-examples** - The [bids-examples](https://github.com/bids-standard/bids-examples) repository is the canonical collection of prototypical BIDS datasets covering different modalities and use cases (MRI, fMRI, DWI, EEG, MEG, iEEG, PET, ASL, genetics, derivatives, and more). Use it as a reference when structuring your own dataset, as test data for BIDS tools, or to understand how a specific modality should be organized. Each example passes the BIDS validator.

## BIDS Extension Proposals (BEPs)

BEPs are community-driven proposals to extend BIDS to new modalities, derivatives, or metadata. The full list with status, leads, and links is in `references/beps.yml` (fetched from the [bids-website](https://github.com/bids-standard/bids-website/blob/main/data/beps/beps.yml)). BEP-specific schema previews are rendered at https://github.com/bids-standard/bids-schema/tree/main/BEPs.

**Current BEPs** (as of schema update):

| BEP | Title | Content | Status |
|-----|-------|---------|--------|
| 004 | Susceptibility Weighted Imaging | raw | Seeking new leader |
| 011 | Structural preprocessing derivatives | derivative | Has PR (#518) |
| 012 | Functional preprocessing derivatives | derivative | Has PR (#519), schema implemented |
| 014 | Affine transforms and nonlinear field warps | derivative | X5 format development |
| 016 | Diffusion weighted imaging derivatives | derivative | Has PR (#2211) |
| 017 | Generic BIDS connectivity data schema | derivative | In development |
| 021 | Common Electrophysiological Derivatives | derivative | In development |
| 023 | PET Preprocessing derivatives | derivative | In development |
| 024 | Computed Tomography scan | raw | Seeking contributors |
| 026 | Microelectrode Recordings | raw | Seeking new leader |
| 028 | Provenance | metadata | Has PR (#2099) |
| 032 | Microelectrode electrophysiology | raw | Has PR (#2307), preview available — covers Neuropixels and other extracellular probes; relates to neuropixels-analysis skill |
| 033 | Advanced Diffusion Weighted Imaging | raw | Seeking contributors |
| 034 | Computational modeling | derivative | Has PR (#967) |
| 035 | Mega-analyses with non-compliant derivatives | derivative | In development |
| 036 | Phenotypic Data Guidelines | raw | Community review |
| 037 | Non-Invasive Brain Stimulation | raw | In development |
| 039 | Dimensionality reduction-based networks | raw | In development |
| 040 | Functional Ultrasound | raw | In development |
| 041 | Statistical Model Derivatives | derivative | Collecting feedback |
| 043 | BIDS Term Mapping | metadata | Collecting feedback |
| 044 | Stimuli | raw | Has PR (#2022), community review |
| 045 | Peripheral Physiological Recordings | raw | Has PR (#2267) |
| 046 | Diffusion Tractography | derivative | In development |
| 047 | Audio/video recordings for behavioral experiments | raw | Has PR (#2231) |

**Related standards:**
- **BIDS-Stats Models**: JSON specification for defining GLM-based neuroimaging analyses
- **BIDS-Derivatives** (BEP003): Standard for preprocessed/analysis outputs (partially merged into spec)

## Related Tools Ecosystem

| Tool | Purpose |
|------|---------|
| **fMRIPrep** | fMRI preprocessing (produces BIDS derivatives) |
| **MRIQC** | MRI quality control (produces BIDS derivatives) |
| **QSIPrep** | Diffusion MRI preprocessing |
| **TemplateFlow** | Neuroimaging templates and atlases with BIDS-like naming |
| **Fitlins** | BIDS Stats Models implementation |
| **DataLad** | Version control for large datasets, integrates with BIDS |
| **OpenNeuro** | Free BIDS dataset repository |
| **DANDI** | Neurophysiology data archive (uses BIDS for some modalities) |
| **HeuDiConv** | DICOM-to-BIDS with heuristic Python files |
| **dcm2bids** | DICOM-to-BIDS with JSON config |
| **BIDScoin** | DICOM-to-BIDS with GUI and YAML config |
| **nwb2bids** | Convert NWB (Neurodata Without Borders) files to BIDS |
| **CuBIDS** | BIDS dataset curation and harmonization |
| **bids2table** | Efficient tabular indexing of BIDS datasets |
| **bids-examples** | Canonical collection of prototypical BIDS datasets for all modalities |

## Documentation

- **BIDS Specification**: https://bids-specification.readthedocs.io/
- **BIDS Website**: https://bids.neuroimaging.io/
- **PyBIDS Documentation**: https://bids-standard.github.io/pybids/
- **BIDS Validator**: https://github.com/bids-standard/bids-validator
- **BIDS Starter Kit**: https://bids-standard.github.io/bids-starter-kit/
- **BIDS Examples**: https://github.com/bids-standard/bids-examples — canonical reference datasets for every BIDS modality; use as templates and test data
- **HeuDiConv Docs**: https://heudiconv.readthedocs.io/
- **Original BIDS paper**: Gorgolewski et al. (2016) Scientific Data, doi:10.1038/sdata.2016.44

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/bids/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

> Excluded (not usable as inline text — binary assets, vendored schemas, or bulk data): references/bids_schema.json

### `references/beps.yml`

```yaml
---
# template
# - number:
#   title:
#   display:
#   google_doc:
#   pull_request:
#   html_preview:
#   leads:
#   # MUST match given-names and family-names from the bids specification citation.cff
#   -   given-names: ' '
#       family-names: ' '
#   bids_maintainers:
#   -   given-names: ' '
#       family-names: ' '
#   status:
#   blocking:
#   communication_channel:
#   pull_request_created:
#   pull_request_merged:

-   number: '004'
    title: Susceptibility Weighted Imaging
    google_doc: https://docs.google.com/document/d/1kyw9mGgacNqeMbp4xZet3RnDhcMmf4_BmRgKaOkO2Sc/
    content:
    -   raw
    leads:
    -   given-names: ' '
        family-names: ' '
    bids_maintainers:
    status:
    blocking:
    -   Looking for a new leader.
    google_doc_created: 2017-04
    pull_request_created:
    pull_request_merged:

-   number: '011'
    title: Structural preprocessing derivatives
    google_doc: https://docs.google.com/document/d/1YG2g4UkEio4t_STIBOqYOwneLEs1emHIXbGKynx7V0Y/
    pull_request: https://github.com/bids-standard/bids-specification/pull/518
    html_preview: https://bids-specification--518.org.readthedocs.build/en/518/05-derivatives/04-structural-derivatives.html
    content:
    -   derivative
    leads:
    -   given-names: Viviana
        family-names: Siless
    bids_maintainers:
    -   given-names: Christopher J.
        family-names: Markiewicz
    status:
    -   Stability! (We haven't touched it in a bit.)
    blocking:
    -   Staleness! (We haven't touched it in a bit.)
    -   Mostly just need to regroup with other BEPs and make sure we're being consistent.
    google_doc_created: 2017-08
    pull_request_created: 2020-06
    pull_request_merged:

-   number: '012'
    title: Functional preprocessing derivatives
    google_doc:
    pull_request: https://github.com/bids-standard/bids-specification/pull/519
    html_preview: https://bids-specification--519.org.readthedocs.build/en/519/derivatives/functional-derivatives.html
    content:
    -   derivative
    leads:
    -   given-names: Christopher J.
        family-names: Markiewicz
    bids_maintainers:
    -   given-names: Christopher J.
        family-names: Markiewicz
    status:
    -   Moderate reworking, post-BEP23 meeting. "boldmap" suffix.
    -   Schema implemented; waiting on full schema validation to merge.
    blocking:
    -   Overlap with BEP 39 (decompositions).
    -   Probably just needs dropping from BEP 12, but need to make sure BEP 39 meets the needs served there.
    google_doc_created: 2018-10
    pull_request_created: 2020-06
    pull_request_merged:

-   number: '014'
    title: Affine transformations and nonlinear field warps
    google_doc: https://docs.google.com/document/d/11gCzXOPUbYyuQx8fErtMO9tnOKC3kTWiL9axWkkILNE/
    content:
    -   derivative
    leads:
    -   given-names: Oscar
        family-names: Esteban
    bids_maintainers:
    -   given-names: Christopher J.
        family-names: Markiewicz
    status:
    -   After the kick-off meeting (2019), progress locked on developing a prototype of a new HDF5-based format (X5)
    -   Minor bug fixes and features to support more transforms
    -   'Perspectives: The current draft seems sufficient for storing transforms'
    -   'Perspectives: X5 has high promises to enable effortless spatial transforms'
    blocking:
    -   Bandwidth to finalize development
    -   'Current blockers: surface transforms & X5 storing'
    google_doc_created: 2017-08
    pull_request_created:
    pull_request_merged:

-   number: '016'
    title: Diffusion weighted imaging derivatives
    pull_request: https://github.com/bids-standard/bids-specification/pull/2211
    content:
    -   derivative
    leads:
    -   given-names: Franco
        family-names: Pestilli
    -   given-names: Oscar
        family-names: Esteban
    bids_maintainers:
    status:
    -   adapted general spatial derivatives proposal, meaning using <modality>map, like `dwimap`
    -   decided on using `params-` to denote different file types, for example `param-md` or `param-fa`
    -   updated meta-data
    blocking:
    google_doc_created:
    pull_request_created:
    pull_request_merged:

-   number: '017'
    title: Generic BIDS connectivity data schema
    display: Connectivity schema
    google_doc: https://docs.google.com/document/d/1ugBdUF6dhElXdj3u9vw0iWjE6f_Bibsro3ah7sRV0GA/
    content:
    -   derivative
    leads:
    -   given-names: Eugene P.
        family-names: Duff
    bids_maintainers:
    status:
    -   specified different formats for dense and sparse matrices
    -   'proposed arrays in h5 or zarr to cover multi-dimensional matrices (for example: dynamic connectivity)'
    blocking:
    google_doc_created: 2017-05
    pull_request_created:
    pull_request_merged:

-   number: '021'
    title: Common Electrophysiological Derivatives
    google_doc: https://docs.google.com/document/d/1PmcVs7vg7Th-cGC-UrX8rAhKUHIzOI-uIOh69_mvdlw/
    content:
    -   derivative
    leads:
    -   given-names: Arnaud
        family-names: Delorme
    -   given-names: Dora
        family-names: Hermes
    -   given-names: Mainak
        family-names: Jas
    -   given-names: Guiomar
        family-names: Niso
    -   given-names: Robert
        family-names: Oostenveld
    -   given-names: Cyril
        family-names: Pernet
    -   given-names: Christine
        family-names: Rogers
    status:
    -   'Focus on raw-ish data: channels by time: epoching, filtering, interpolation...'
    -   'All provenance tracking: outsourced to BEP028 (“provenance”)'
    -   Reusing existing (raw) data formats where applicable
    -   'No additional entities or suffixes: focus on “desc” entity'
    -   Create new “descriptions.tsv” file to accompany and document the “desc” entity
    -   Working on examples on GitHub
    -   'Perspectives: Derivatives beyond channels by time data will be discussed at a later point'
    blocking:
    google_doc_created: 2018-05
    pull_request_created:
    pull_request_merged:

-   number: '023'
    title: PET Preprocessing derivatives
    google_doc: https://docs.google.com/document/d/1yzsd1J9GT-aA0DWhdlgNr5LCu6_gvbjLyfvYq2FuxlY/
    content:
    -   derivative
    leads:
    -   given-names: Martin
        family-names: Noergaard
    -   given-names: Graham
        family-names: Searle
    -   given-names: Melanie
        family-names: Ganz-Benjaminsen
    bids_maintainers:
    -   given-names: Anthony
        family-names: Galassi
    status:
    -   Defined all the necessary components to be included in the specification
    -   Alignment with other modalities obtained at Copenhagen BIDS derivatives meeting
    -   Example PET derivatives datasets available on github
    -   'Perspectives: 3rd joint meeting between all PET collaborators in August 2023'
    -   'Perspectives:  Aim is to finish the specification during the fall of 2023'
    blocking:
    -   Need more example datasets (fore example different tracers) with different preprocessing choices to capture as most of the PET community as possible
    -   Need to finish alignment with other modalities
    -   Still need to agree on the level of information going into corresponding json files
    google_doc_created: 2018-08
    pull_request_created:
    pull_request_merged:

-   number: '024'
    title: Computed Tomography scan
    google_doc: https://docs.google.com/document/d/1fqnJZ18x5LJC8jiJ8yvPHUGFzNBZ6gW2kywYrUKWtuo/
    content:
    -   raw
    leads:
    -   given-names: Hugo
        family-names: Boniface
    bids_maintainers:
    status:
    -   Lead seeking more contributors and experts.
    blocking:
    google_doc_created: 2018-11
    pull_request_created:
    pull_request_merged:

-   number: '026'
    title: Microelectrode Recordings
    google_doc: https://docs.google.com/document/d/14KC1d5-Lx-7ZSMtwS7pVAAvz-2WR_uoo5FvsNirzqJw/
    content:
    -   raw
    leads:
    -   given-names: ' '
        family-names: ' '
    bids_maintainers:
    status:
    -   BEP is open to new leadership, see also [BEP032 (animal electrophys)](https://docs.google.com/document/d/1oG-C8T-dWPqfVzL2W8HO3elWK8NIh2cOCPssRGv23n0/)
    blocking:
    -   Searching for a new leader.
    google_doc_created: 2018-04
    pull_request_created:
    pull_request_merged:

-   number: '028'
    title: Provenance
    google_doc: https://docs.google.com/document/d/1vw3VNDof5cecv2PkFp7Lw_pNUTUo8-m8V4SIdtGJVKs/
    content:
    -   metadata
    leads:
    -   given-names: Satrajit S.
        family-names: Ghosh
    -   given-names: Camille
        family-names: Maumet
    -   given-names: Yaroslav O.
        family-names: Halchenko
    bids_maintainers:
    status:
    -   '[Specification](https://bids.neuroimaging.io/bep028)'
    -   '[Set of examples](https://github.com/bids-standard/BEP028_BIDSprov)'
    -   'Perspectives: Opening up to BIDS community for feedback'
    -   'Perspectives: Engaging with software developers (in progress w/ SPM, AFNI)'
    blocking:
    google_doc_created: 2018-08
    pull_request: https://github.com/bids-standard/bids-specification/pull/2099
    pull_request_created: 2025-04
    pull_request_merged:

-   number: '032'
    title: Microelectrode electrophysiology
    google_doc: https://docs.google.com/document/d/1oG-C8T-dWPqfVzL2W8HO3elWK8NIh2cOCPssRGv23n0/
    pull_request: https://github.com/bids-standard/bids-specification/pull/2307
    html_preview: https://bids-specification--2307.org.readthedocs.build/en/2307/modality-specific-files/microelectrode-electrophysiology.html
    content:
    -   raw
    leads:
    -   given-names: Sylvain
        family-names: Takerkart
    -   given-names: Benjamin
        family-names: Dichter
    -   given-names: Yaroslav O.
        family-names: Halchenko
    -   given-names: Lyuba
        family-names: Zehl
    -   given-names: Andrew
        family-names: Davison
    bids_maintainers:
    -   given-names: Rémi
        family-names: Gau
    status:
    -   Decided on the new name (not just "Animal" but "Microelectrode"), modalities, datatypes
    -   Nearly finalized added metadata
    -   PR compiles green, preview is available
    -   'Target: finalize & merge PR into the BIDS specs in 2025'
    blocking:
    -   Need to prepare example datasets
    -   Need to start thinking about derived data (spike sorted)
    google_doc_created: 2020-12
    pull_request_created: 2022-11
    pull_request_merged:

-   number: '033'
    title: Advanced Diffusion Weighted Imaging
    google_doc: https://docs.google.com/document/d/1en4ByORlPqwDfZwNOOBTj0GwpYBcS0_2peqreTOvwDU/
    content:
    -   raw
    leads:
    -   given-names: James
        family-names: Gholam
    -   given-names: Leandro
        family-names: Beltrachini
    -   given-names: Filip
        family-names: Szczepankiewicz
    bids_maintainers:
    status:
    -   'New BEP, seeking contributors and collecting community feedback relating to: priority sequences to support, best supported binary structured formats
        (e.g. CBOR? HDF5? MsgPack?).'
    -   Comments may be submitted directly on the document.
    -   Generating example datasets [here](https://github.com/JAgho/MISP_plot/tree/main) and determining best practice with vendors to record data in-sequence
    blocking:
    google_doc_created: 2021-04
    pull_request_created:
    pull_request_merged:

-   number: '034'
    title: Computational modeling
    pull_request: https://github.com/bids-standard/bids-specification/pull/967
    html_preview: https://bids-specification--967.org.readthedocs.build/en/967/modality-specific-files/computational-models.html
    content:
    -   derivative
    -   metadata
    leads:
    -   given-names: Michael
        family-names: Schirner
    -   given-names: Petra
        family-names: Ritter
    bids_maintainers:
    status:
    -   sim2bids app created
    -   easier to bring neural simulation data (especially in The Virtual Brain format) into the proposed BIDS Comp Model format
    -   'Perspectives: A roadmap that coordinates efforts across BEPs would be appreciated.'
    blocking:
    -   BEPs have overlapping concerns (Comp Models, Spaces and mappings, Generic BIDS connectivity schema, time series, Provenance, Atlases)
    -   need to separate concerns & provide a roadmap for each BEP
    google_doc_created: 2021-02
    pull_request_created: 2021-08
    pull_request_merged:

-   number: '035'
    title: Modular extensions for individual participant data mega-analyses with non-compliant derivatives
    display: Mega-analyses
    google_doc: https://docs.google.com/document/d/1tFRNumQyIgjXBNC3brFDLO9FaikjL84noxK6Om-Ctik/
    content:
    -   derivative
    leads:
    -   given-names: Giuseppe
        family-names: Gallitto
    -   given-names: Balint
        family-names: Kincses
    -   given-names: Tamas
        family-names: Spisak
    bids_maintainers:
    -   given-names: Rémi
        family-names: Gau
    status:
    -   Meta-data harmonization with a term-mapper goes to BEP043
    -   'Persperctive: Repeated community review of the simplified proposal'
    blocking:
    -   Term-mapping is a general feature => complex, modular proposal
    google_doc_created: 2021-12
    pull_request_created:
    pull_request_merged:

-   number: '036'
    title: Phenotypic Data Guidelines
    google_doc: https://docs.google.com/document/d/1WTkfES8L0vItZVyyR68fc-9cO03jS-kCnMnw6602pbc/
    content:
    -   raw
    leads:
    -   given-names: Eric
        family-names: Earl
    -   given-names: Samuel
        family-names: Guay
    -   given-names: Sebastian
        family-names: Urchs
    -   given-names: Arshitha
        family-names: Basavaraj
    bids_maintainers:
    -   given-names: Chris
        family-names: Markiewicz
    -   given-names: Ross
        family-names: Blair
    status:
    -   BEP entering community review period shortly.
    -   BIDS specification PR 2123.
    -   BIDS examples PR 465.
    blocking:
    -   A successful community review.
    google_doc_created: 2021-10
    pull_request_created: 2025-05
    pull_request_merged:

-   number: '037'
    title: Non-Invasive Brain Stimulation
    google_doc: https://docs.google.com/document/d/1drYd7kaNbHTcYPR3T_CRDsPcEbFSV7JbJUmhMPeWMqY/
    current_repository: https://github.com/nigelrogasch/nibs-bids/tree/master/nibs-bids-v6/
    current_preprint_editable: https://docs.google.com/document/d/1xfetyFkXh8kqObfCViUvku69pk4ZZw8BC5GL8_Cq9TI/edit?tab=t.0
    current_preprint:
    author_list: https://docs.google.com/spreadsheets/d/1oMImk-HXsyLZtTj3yIa1uY9LX3hVpsCiAGZP3oSV0Eo/edit?gid=0#gid=0
    content:
    -   raw
    leads:
    -   given-names: Giacomo
        family-names: Bertazzoli
    -   given-names: Vittorio
        family-names: Iacovella
    -   given-names: Peter J.
        family-names: Fried
    -   given-names: Marta
        family-names: Bortoletto
    -   given-names: Nigel
        family-names: Rogasch
    past leads (inactive):
    -   given-names: Carlo
        family-names: Miniussi
    bids_maintainers:
    -   given-names: Rémi
        family-names: Gau
    status:
    -   v1.0 2020-11-09 Initial work on specification with vittorio.iacovella@unitn.it carlo.miniussi@unitn.it marta.bortoletto@cognitiveneuroscience.it
    -   v1.0 2021-04 First example of a NIBS-BIDS dataset https://gin.g-node.org/CIMeC/TMS-EEG_brain_connectivity_BIDS
    -   V1.0 2021-11 Brainhack @Donosti with eleonora.marcantoni@cognitiveneuroscience.it martinabulgari3@gmail.com and g.guidali@campus.unimib.it
    -   V1.0 2022-02 First international NIBS-BIDS meeting
    -   V1.0 2022-11 First update of the BEP
    -   V2.0 2023-08 BEP 2.0 available with the new NIBS-BIDS logic for describing NIBS experiments
    -   V3.0 2024-07 BEP 3.0 available with a draft of the final BIDS structure.
    -   V4.0 2024-11 BEP 4.0 updated with a new, more comprehensive structure. Added int files for offline stimulation. Harmonized parameters with SimNIBS.
        Use of events and scans files for online stimulation.
    -   V4.1 2024-12 BEP 4.1 Comments form December 9th, 2024 5th general meeting implemented, added FAQ section. Met with the BIDS maintenance team in
        January 2025. Agreed on closing the open discussions, lock the google doc and start the PR.
    -   V6.2 2026-03 BEP 6.2 Comments form December 12th, 2025 6th general meeting implemented. Met with the BIDS steering team in March 2026. Agreed on
        NSF FAIROS application on NIBS-BIDS implementation https://www.nsf.gov/funding/opportunities/fairos-findable-accessible-interoperable-reusable-open-science.
        Agreed on creating a preprint version of the BEP037 (to bi cited as a work-in-progress).
    blocking:
    google_doc_created: 2022-09
    pull_request_created:
    pull_request_merged:

-   number: '039'
    title: Dimensionality reduction-based networks
    google_doc: https://docs.google.com/document/d/1GTWsj0MFQedXjOaNk6H0or6IDVFyMAysrJ9I4Zmpz2E/
    content:
    -   raw
    leads:
    -   given-names: Arianna
        family-names: Sala
    -   given-names: Anibal
        family-names: Sólon
    -   given-names: Cyrus
        family-names: Eierud
    -   given-names: Franco
        family-names: Pestilli
    -   given-names: Peer
        family-names: Herholz
    bids_maintainers:
    status:
    -   adapted general spatial derivatives proposal, meaning using `<modality>map`, for example `eegmap` and `boldmap` for spatial components
    -   decided on `model-` and `items-` as keys to denote the utilized model and component number, if files are 3D, respectively
    -   updated meta-data and examples
    blocking:
    google_doc_created: 2021-10
    pull_request_created:
    pull_request_merged:

-   number: '040'
    title: Functional Ultrasound
    google_doc: https://docs.google.com/document/d/1W3z01mf1E8cfg_OY7ZGqeUeOKv659jCHQBXavtmT-T8/
    content:
    -   raw
    leads:
    -   given-names: Jean-Charles
        family-names: Mariani
    -   given-names: Samuel
        family-names: Le Meur-Diebolt
    -   given-names: Thomas
        family-names: Deffieux
    bids_maintainers:
    -   given-names: Rémi
        family-names: Gau
    status:
    -   All issues raised on the original BEP have been resolved.
    -   Regular meetings with contributors scheduled.
    -   Scanner coordinate system has been proposed to harmonize affine transformations with moving probes.
    -   'Perspectives: Starting to bidsify existing datasets to stress test the BEP.'
    -   'Perspectives: timing metadata has been copied from the fMRI-BIDS specification, but evolutions could be discussed to handle non-stable sampling
        frequencies.'
    blocking:
    google_doc_created: 2023-03
    pull_request_created:
    pull_request_merged:

-   number: '041'
    title: Statistical Model Derivatives
    google_doc: https://docs.google.com/document/d/1KHzp-yk8KXvkUIhtN71WU0m4P4kKT9C1yvI-i9_kNeY/
    content:
    -   derivative
    leads:
    -   given-names: Taylor
        family-names: Salo
    bids_maintainers:
    -   given-names: Taylor
        family-names: Salo
    status:
    -   New BEP, collecting community comments and feedback.
    -   All collaborators are welcome.
    blocking:
    google_doc_created: 2022-08
    pull_request_created:
    pull_request_merged:

-   number: '043'
    title: BIDS Term Mapping
    google_doc: https://docs.google.com/document/d/1LACjc5hFXDpa2l_QddBPR41Vce_gglGv9WeuBB7LsBU/
    content:
    -   metadata
    leads:
    -   given-names: Christopher J.
        family-names: Markiewicz
    -   given-names: Eric A.
        family-names: Earl
    bids_maintainers:
    -   given-names: Christopher J.
        family-names: Markiewicz
    -   given-names: Eric A.
        family-names: Earl
    status:
    -   For being able to map non-BIDS data as BIDS-compatible.
    -   Now collecting community comments and feedback.
    -   All collaborators are welcome.
    blocking:
    google_doc_created: 2024-03
    pull_request_created:
    pull_request_merged:

-   number: '044'
    title: Stimuli
    pull_request: https://github.com/bids-standard/bids-specification/pull/2022
    html_preview: https://bids-specification--2022.org.readthedocs.build/en/2022/modality-specific-files/stimuli.html
    leads:
    -   given-names: Seyed Yahya
        family-names: Shirazi
    -   given-names: Dora
        family-names: Hermes
    -   given-names: Yaroslav O.
        family-names: Halchenko
    -   given-names: Kay
        family-names: Robbins
    -   given-names: Scott
        family-names: Makeig
    bids_maintainers:
    -   given-names: Rémi
        family-names: Gau
    status:
    -   Community comments and feedback are being collected (January 2025)
    -   To harmonize and make more reusable stimuli content under stimuli/
    -   Collecting community comments and feedback. All collaborators are welcome.
    -   'Original issue: [#153](https://github.com/bids-standard/bids-specification/issues/153)'
    content:
    -   raw
    blocking:
    google_doc_created: 2023-09
    pull_request_created: 2024-12
    pull_request_merged:

-   number: '045'
    title: Peripheral Physiological Recordings
    display: Physio
    pull_request: https://github.com/bids-standard/bids-specification/pull/2267
    html_preview: https://bids-specification--2267.org.readthedocs.build/en/2267/modality-specific-files/physiological-recordings.html
    google_doc: https://docs.google.com/document/d/1oTfjzY5ZnLIYd0kPPWhR81sBmMuy_jC5YYIaqj6OhSA/edit
    leads:
    -   given-names: Mary
        family-names: Miedema
    -   given-names: Stefano
        family-names: Moia
    -   given-names: Sourav
        family-names: Kulkarni
    bids_maintainers:
    -   given-names: Seyed Yahya
        family-names: Shirazi
    status:
    -   No longer developed in google doc, moved to <https://github.com/physiopy/bids-specification-physio>.
    -   To update standards for physiological data for improved clarity and a broader range of use cases.
    -   Now collecting community comments and feedback. All collaborators are welcome.
    -   'Original issue: [#1675](https://github.com/bids-standard/bids-specification/issues/1675).'
    content:
    -   raw
    blocking:
    google_doc_created: 2024-08
    pull_request_created: 2025-11
    pull_request_merged:

-   number: '046'
    title: Diffusion Tractography
    display: Tractography
    google_doc: https://docs.google.com/document/d/1ubDQ2RhgjnfGqoeukzEkPV9YEHhfYMERrj7-3b0c2HI/edit
    leads:
    -   given-names: Robert E.
        family-names: Smith
    -   given-names: Ariel
        family-names: Rokem
    -   given-names: Franco
        family-names: Pestilli
    status:
    -   Porting comprehensive description of streamline tractography mechanisms into specification - 10.1016/B978-0-12-817057-1.00023-8
    -   Determine appropriate resolution with TRX development - https://tee-ar-ex.github.io/trx-python/
    -   Decide on scope of BEP; e.g. whether to include tractometry, complex tract delineation
    content:
    -   derivative
    blocking:
    google_doc_created: 2022-02
    pull_request_created:
    pull_request_merged:

-   number: '047'
    title: Audio/video recordings for behavioral experiments
    display: Behavioral audio/video recordings
    pull_request: https://github.com/bids-standard/bids-specification/pull/2231
    html_preview: https://bids-specification--2231.org.readthedocs.build/en/2231/modality-specific-files/behavioral-experiments.html
    content:
    -   raw
    leads:
    -   given-names: Benjamin
        family-names: Dichter
    bids_maintainers:
    -   given-names: Seyed Yahya
        family-names: Shirazi
    status:
    -   Adds support for storing audio and video behavioral recordings (new `_audio` and `_video` suffixes) in the `beh/` directory.
    blocking:
    google_doc_created:
    pull_request_created: 2025-10
    pull_request_merged:
```

### `references/bids_specification.md`

# BIDS Specification Reference

> **Note**: The canonical, machine-readable source of truth is `bids_schema.json` (in this directory), exported from the [BIDS Schema](https://github.com/bids-standard/bids-specification/tree/master/src/schema). The tables below are a human-readable summary. When the two disagree, trust the schema.

## Entity Table

Complete list of BIDS entities, their keys, and where they apply. **Rows are listed in the required filename ordering** — entities must appear in this order in BIDS filenames. This order is defined in the schema at `rules.entities` (see `bids_schema.json`).

| # | Entity | Key | Format | Applies to |
|---|--------|-----|--------|------------|
| 1 | Subject | `sub-` | `<label>` (alphanumeric) | All files (required) |
| 2 | Template | `tpl-` | `<label>` | derivatives (template-based) |
| 3 | Session | `ses-` | `<label>` | All datatypes |
| 4 | Cohort | `cohort-` | `<label>` | derivatives (template cohorts) |
| 5 | Sample | `sample-` | `<label>` | microscopy |
| 6 | Task | `task-` | `<label>` | func, eeg, meg, ieeg, beh, pet, nirs, motion |
| 7 | Tracking system | `tracksys-` | `<label>` | motion |
| 8 | Acquisition | `acq-` | `<label>` | All datatypes |
| 9 | Nucleus | `nuc-` | `<label>` | MR spectroscopy |
| 10 | Volume | `voi-` | `<label>` | MR spectroscopy |
| 11 | Contrast enhancing agent | `ce-` | `<label>` | anat |
| 12 | Tracer | `trc-` | `<label>` | pet |
| 13 | Stain | `stain-` | `<label>` | microscopy |
| 14 | Reconstruction | `rec-` | `<label>` | anat, func, pet |
| 15 | Direction | `dir-` | `<label>` | fmap, dwi, perf, func |
| 16 | Run | `run-` | `<index>` (integer) | All datatypes |
| 17 | Modality | `mod-` | `<label>` | fieldmaps |
| 18 | Echo | `echo-` | `<index>` | func, fmap |
| 19 | Flip | `flip-` | `<index>` | anat (quantitative MRI) |
| 20 | Inversion | `inv-` | `<index>` | anat (quantitative MRI) |
| 21 | Magnetization transfer | `mt-` | `on`/`off` | anat (quantitative MRI) |
| 22 | Part | `part-` | `mag`/`phase`/`real`/`imag` | anat, func |
| 23 | Processing | `proc-` | `<label>` | eeg, meg, ieeg |
| 24 | Hemisphere | `hemi-` | `L`/`R` | derivatives (surface data) |
| 25 | Space | `space-` | `<label>` | derivatives |
| 26 | Split | `split-` | `<index>` | func, dwi, eeg, meg, ieeg |
| 27 | Recording | `recording-` | `<label>` | physio, stim, eeg, meg |
| 28 | Chunk | `chunk-` | `<index>` | large files split across chunks |
| 29 | Atlas | `atlas-` | `<label>` | derivatives (atlas-based) |
| 30 | Segmentation | `seg-` | `<label>` | derivatives |
| 31 | Scale | `scale-` | `<label>` | derivatives |
| 32 | Resolution | `res-` | `<label>` | derivatives |
| 33 | Density | `den-` | `<label>` | derivatives (surface meshes) |
| 34 | Label | `label-` | `<label>` | derivatives (segmentation labels) |
| 35 | Description | `desc-` | `<label>` | derivatives only |

## Datatypes (Top-Level Directories)

| Datatype | Description | Common Suffixes |
|----------|-------------|-----------------|
| `anat` | Structural MRI | `T1w`, `T2w`, `FLAIR`, `T2star`, `inplaneT1`, `inplaneT2`, `PDw`, `T1map`, `T2map`, `T1rho`, `UNIT1`, `MP2RAGE`, `MTR`, `MTS` |
| `func` | Functional MRI | `bold`, `cbv`, `sbref` |
| `dwi` | Diffusion-weighted imaging | `dwi`, `sbref` |
| `fmap` | Fieldmaps | `phasediff`, `phase1`, `phase2`, `magnitude1`, `magnitude2`, `fieldmap`, `epi` |
| `perf` | Perfusion imaging (ASL) | `asl`, `m0scan`, `aslcontext` |
| `eeg` | Electroencephalography | `eeg`, `channels`, `electrodes`, `events`, `coordsystem` |
| `meg` | Magnetoencephalography | `meg`, `channels`, `coordsystem`, `events`, `headshape` |
| `ieeg` | Intracranial EEG | `ieeg`, `channels`, `electrodes`, `events`, `coordsystem` |
| `pet` | Positron Emission Tomography | `pet`, `blood` |
| `micr` | Microscopy | `2PE`, `BF`, `CARS`, `CONF`, `DIC`, `DF`, `FLUO`, `MPE`, `NLO`, `OCT`, `PC`, `PLI`, `SRS`, `TL` |
| `beh` | Behavioral data (no imaging) | `events`, `beh`, `physio`, `stim` |
| `motion` | Motion capture | `motion`, `channels`, `events` |
| `nirs` | Near-infrared spectroscopy | `nirs`, `channels`, `optodes`, `coordsystem`, `events` |

## File Extensions

| Extension | Description |
|-----------|-------------|
| `.nii.gz` | Compressed NIfTI (standard for MRI/fMRI/DWI) |
| `.nii` | Uncompressed NIfTI |
| `.json` | JSON sidecar metadata |
| `.tsv` | Tab-separated values (events, participants, etc.) |
| `.bvec` | b-vectors (DWI gradient directions) |
| `.bval` | b-values (DWI gradient strengths) |
| `.edf` | European Data Format (EEG) |
| `.bdf` | BioSemi Data Format (EEG) |
| `.vhdr`/`.vmrk`/`.eeg` | BrainVision format (EEG) |
| `.set` | EEGLAB format (EEG) |
| `.fif` | Elekta/MEGIN format (MEG) |
| `.ds` | CTF dataset (MEG) |
| `.sqd`/`.con` | KIT/Yokogawa (MEG) |

## Required Files

### Dataset-level (always required)
- `dataset_description.json`

### Dataset-level (recommended)
- `README` or `README.md`
- `CHANGES`
- `participants.tsv` + `participants.json`
- `LICENSE`

### Run-level (recommended)
- `sub-<label>/[ses-<label>/]sub-<label>[_ses-<label>]_scans.tsv` - per-run acquisition metadata

### Modality-specific required files
- **func/bold**: corresponding `_events.tsv` for task data; `TaskName` in JSON sidecar
- **dwi**: `.bvec` and `.bval` files
- **eeg/meg/ieeg**: `_channels.tsv`, `_events.tsv`
- **perf/asl**: `_aslcontext.tsv`

## Directory Structure Rules

1. Subject directories are named `sub-<label>` and sit at dataset root
2. Session directories `ses-<label>` are optional; if used, must be used for ALL subjects
3. Datatype directories (`anat/`, `func/`, etc.) sit inside subject (or session) directories
4. `sourcedata/` stores raw unprocessed data (DICOM, etc.) - not validated
5. `derivatives/` stores processed outputs - each pipeline in its own subdirectory
6. `code/` stores analysis scripts
7. `stimuli/` stores stimulus files used during acquisition
8. `phenotype/` stores questionnaire/behavioral data not tied to specific imaging

## Metadata Inheritance

JSON metadata cascades from higher to lower directories. If the same key appears at multiple levels, the most specific (closest to the data file) wins.

**Resolution order** (highest priority first):
1. File-level sidecar: `sub-01/func/sub-01_task-rest_bold.json`
2. Subject-level sidecar: `sub-01/sub-01_task-rest_bold.json`
3. Dataset-level sidecar: `task-rest_bold.json`

This avoids duplicating metadata that is constant across subjects (e.g., `RepetitionTime`, `TaskName`).

## Standard Template Spaces

Common `space-` values used in derivatives:

| Space Label | Description |
|-------------|-------------|
| `MNI152NLin2009cAsym` | MNI 2009c nonlinear asymmetric (fMRIPrep default) |
| `MNI152NLin6Asym` | MNI 6th-generation nonlinear asymmetric (FSL default) |
| `MNI152Lin` | MNI linear registration |
| `MNIPediatricAsym` | Pediatric MNI templates |
| `T1w` | Individual subject's T1w native space |
| `fsnative` | FreeSurfer individual surface space |
| `fsaverage` | FreeSurfer average surface (164k vertices) |
| `fsaverage5` | FreeSurfer average surface (10k vertices) |
| `fsaverage6` | FreeSurfer average surface (40k vertices) |
| `fsLR` | HCP fs_LR surface space |
| `OASIS30ANTs` | OASIS-30 ANTs template |
| `UNCInfant` | UNC infant templates |

Full list managed by TemplateFlow: https://www.templateflow.org/

## Specification Changelog (Selected)

| Version | Key Changes |
|---------|-------------|
| 1.10.0 | Motion capture modality; refined derivative entity rules |
| 1.9.0 | NIRS modality; Python-based validator reference implementation |
| 1.8.0 | Microscopy modality; `chunk-` entity for large files |
| 1.7.0 | PET modality fully specified |
| 1.6.0 | EEG/MEG/iEEG matured; `_coordsystem.json` |
| 1.5.0 | Genetic descriptors; ASL perfusion |
| 1.4.0 | `dataset_description.json` expanded; derivatives framework |
| 1.0.0 | Initial release: MRI only (anat, func, dwi, fmap) |

## Entity Label Rules

- **Labels** (`<label>`): alphanumeric only, no special characters, no leading zeros (except `run-`)
- **Indices** (`<index>`): non-negative integers, zero-padded to equal width within a dataset (e.g., `run-01`, `run-02`)
- Subject labels: typically numeric (`01`, `02`) but can be alphanumeric (`CON01`, `PAT01`)
- Session labels: descriptive (`pre`, `post`, `baseline`, `followup`) or numeric
- Task labels: brief, descriptive, no spaces (`rest`, `nback`, `faces`, `gonogo`)

### `references/conversion_tools.md`

# BIDS Conversion Tools Reference

This reference covers detailed workflows for converting DICOM and other raw data formats to BIDS using the three main conversion tools.

## HeuDiConv

HeuDiConv is the most flexible DICOM-to-BIDS converter. It supports three usage modes — from fully automatic turnkey conversion to fully custom heuristics — and handles duplicates, provenance tracking, and sourcedata archiving out of the box.

**Repository**: https://github.com/nipy/heudiconv
**Docs**: https://heudiconv.readthedocs.io/
**Tutorials**: https://heudiconv.readthedocs.io/en/latest/tutorials.html

### Installation

```bash
uv pip install heudiconv

# HeuDiConv wraps dcm2niix for the actual conversion
# dcm2niix is usually installed as a dependency, but can also be installed via:
# conda install -c conda-forge dcm2niix
# or: apt-get install dcm2niix
```

### Mode 1: ReproIn (Turnkey Conversion — Recommended for New Studies)

If scanner protocol names follow the [ReproIn naming convention](https://github.com/repronim/reproin), conversion is fully automatic with no heuristic file to write. ReproIn is a setup for automatic generation of sharable, version-controlled BIDS datasets directly from MR scanners.

```bash
# Turnkey conversion — just point at DICOMs, HeuDiConv does the rest
heudiconv --files dicom/001 -o data -f reproin --bids --minmeta
```

#### ReproIn Protocol Naming Rules

Protocol names encode BIDS entities directly. Format: `<seqtype>[-<suffix>][_<entity>-<label>]...`

| Protocol name at scanner | BIDS output |
|--------------------------|-------------|
| `anat-T1w` or just `anat` | `sub-XX/anat/sub-XX_T1w.nii.gz` |
| `func-bold_task-rest` or `func_task-rest` | `sub-XX/func/sub-XX_task-rest_bold.nii.gz` |
| `dwi_dir-AP` | `sub-XX/dwi/sub-XX_dir-AP_dwi.nii.gz` |
| `fmap_dir-PA` or `fmap-epi_dir-PA` | `sub-XX/fmap/sub-XX_dir-PA_epi.nii.gz` |
| `fmap_acq-4mm` | `sub-XX/fmap/sub-XX_acq-4mm_epi.nii.gz` |

**Key features:**
- **Default suffixes**: `anat` defaults to `T1w`, `func` to `bold`, `fmap` to `epi` — so they can be omitted
- **Subject ID**: extracted automatically from DICOM metadata (Patient ID)
- **Session**: set once on any sequence (e.g., `anat-scout_ses-pre`) and ReproIn propagates it to all sequences in that scanner Program/Patient
- **Duplicate runs**: automatically numbered (`run-01`, `run-02`, ...) when the same protocol is run multiple times
- **Locator hierarchy**: output is nested under Region/Exam from the scanner's Study Description (customizable with `--locator`)
- **sourcedata**: original DICOMs are archived as `.tgz` files under `sourcedata/` for reproducibility
- **Dashes in names**: scanners may strip dashes from protocol names during DICOM export — ReproIn handles this gracefully

#### ReproIn Overview

See also:
- [ReproIn Walkthrough](https://github.com/repronim/reproin#walkthrough) for scanner setup
- [ReproNim Webinar slides and recording](https://github.com/repronim/reproin#presentations) on HeuDiConv + ReproIn

### Mode 2: Custom Heuristic Mapping into ReproIn (For Existing Data)

If you already have collected data with non-ReproIn protocol names (or cannot control scanner naming), you can write a thin heuristic that maps your protocol names into ReproIn conventions. This gives you all ReproIn benefits (automatic entity handling, duplicate management, sourcedata archiving) while accommodating arbitrary scanner naming.

See https://github.com/repronim/reproin/issues/18 for a brief HOWTO on this approach.

The idea is to write a heuristic whose `infotodict` returns keys that follow ReproIn naming patterns, so the ReproIn machinery handles the rest.

### Mode 3: Custom Heuristic (Full Flexibility)

For studies with complex mappings or non-standard requirements, write a full Python heuristic file. This is the most common workflow for retrospective conversion of existing datasets.

#### Step 1: Reconnaissance — Discover DICOM series

```bash
# -f convertall: built-in heuristic that lists all series without converting
# -c none: don't convert, just generate dicominfo.tsv
heudiconv \
    --files dicom/219/itbs/*/*.dcm \
    -s 219 \
    -f convertall \
    -c none \
    -o Nifti/
```

This creates `.heudiconv/219/info/dicominfo.tsv` containing one row per DICOM series with columns:
- `series_id`, `sequence_name`, `protocol_name`, `series_description`
- `dim1`-`dim4` (image dimensions), `TR`, `TE`, `image_type`
- `is_derived`, `is_motion_corrected` — important for filtering

Review this TSV (open in a spreadsheet) to understand what was acquired and plan the mapping to BIDS names. Step 1 only needs to be done once per project.

#### Step 2: Write a heuristic file

```python
"""HeuDiConv heuristic for a typical fMRI study.

Study design:
- T1w MPRAGE anatomical
- Resting-state BOLD
- Task BOLD (n-back working memory)
- DWI with two phase-encoding directions
- Fieldmap (phase-difference)
"""

def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where.

    Parameters
    ----------
    seqinfo : list of namedtuples
        Each namedtuple has fields: .series_id, .sequence_name,
        .protocol_name, .series_description, .dim1, .dim2, .dim3, .dim4,
        .TR, .TE, .is_derived, .is_motion_corrected, .image_type, etc.

    Returns
    -------
    info : dict
        Keys are tuples from create_key(), values are lists of series_id
    """
    # Define BIDS output templates
    t1w = create_key(
        'sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w'
    )
    rest_bold = create_key(
        'sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_bold'
    )
    # {item:02d} auto-numbers runs when the same protocol is run multiple times
    nback_bold = create_key(
        'sub-{subject}/{session}/func/sub-{subject}_{session}_task-nback_run-{item:02d}_bold'
    )
    dwi_AP = create_key(
        'sub-{subject}/{session}/dwi/sub-{subject}_{session}_dir-AP_dwi'
    )
    dwi_PA = create_key(
        'sub-{subject}/{session}/dwi/sub-{subject}_{session}_dir-PA_dwi'
    )
    fmap_phasediff = create_key(
        'sub-{subject}/{session}/fmap/sub-{subject}_{session}_phasediff'
    )
    fmap_mag1 = create_key(
        'sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude1'
    )
    fmap_mag2 = create_key(
        'sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude2'
    )

    info = {
        t1w: [], rest_bold: [], nback_bold: [],
        dwi_AP: [], dwi_PA: [],
        fmap_phasediff: [], fmap_mag1: [], fmap_mag2: [],
    }

    for s in seqinfo:
        protocol = s.protocol_name.lower()
        series_desc = s.series_description.lower() if s.series_description else ''

        # Anatomical — filter by dim3 to exclude localizers
        if ('mprage' in protocol or 't1w' in protocol) and s.dim3 > 100:
            info[t1w].append(s.series_id)

        # Functional — filter by dim4 and exclude MOCO series
        elif 'rest' in protocol and s.dim4 > 10 and not s.is_motion_corrected:
            info[rest_bold].append(s.series_id)
        elif 'nback' in protocol and s.dim4 > 10 and not s.is_motion_corrected:
            info[nback_bold].append(s.series_id)

        # Diffusion
        elif ('dti' in protocol or 'dwi' in protocol) and s.dim4 > 1:
            if 'ap' in protocol or 'ap' in series_desc:
                info[dwi_AP].append(s.series_id)
            elif 'pa' in protocol or 'pa' in series_desc:
                info[dwi_PA].append(s.series_id)

        # Fieldmaps
        elif 'field' in protocol or 'fmap' in protocol:
            if 'ph' in s.image_type_text.lower():
                info[fmap_phasediff].append(s.series_id)
            elif s.series_description and 'e1' in s.series_description.lower():
                info[fmap_mag1].append(s.series_id)
            elif s.series_description and 'e2' in s.series_description.lower():
                info[fmap_mag2].append(s.series_id)

    return info
```

#### Step 3: Convert

```bash
# Convert with custom heuristic
heudiconv \
    --files dicom/219/itbs/*/*.dcm \
    -s 219 \
    -ss itbs \
    -f Nifti/code/heuristic.py \
    -c dcm2niix \
    --bids \
    --minmeta \
    -o Nifti/

# Or using -d template for batch conversion of multiple subjects
heudiconv \
    -d /path/to/dicoms/{subject}/*/*/*.dcm \
    -s 01 02 03 04 05 \
    -f my_heuristic.py \
    -c dcm2niix \
    --bids \
    --minmeta \
    -o /path/to/bids_output

# Key flags:
# --files : point to specific DICOM files/directories
# -d : DICOM path template ({subject}, {session} are replaced)
# -s : subject label(s)
# -ss : session label
# -f : heuristic file path, or built-in name (reproin, convertall)
# -c : converter (dcm2niix, none)
# --bids / -b : output BIDS structure (creates JSON sidecars, etc.)
# --minmeta : prevent excess DICOM metadata from overflowing JSON sidecars
# -o : output directory
# --overwrite : re-run conversion overwriting existing files
```

### The .heudiconv Directory

Every conversion creates/updates a `.heudiconv/` hidden directory alongside the output:
- `.heudiconv/<subject>/info/dicominfo.tsv` — DICOM series metadata
- `.heudiconv/<subject>/info/<heuristic>.py` — copy of the heuristic used
- Conversion records for each subject/session

**Important**: If you re-run conversion for a subject/session that was already processed, HeuDiConv silently reuses cached conversion info from `.heudiconv/`. If troubleshooting, delete the subject's entry from `.heudiconv/` (or the whole directory) and re-run.

Keep `.heudiconv/` with your data — together with `code/` it provides valuable provenance information.

### HeuDiConv Tips

1. **Always use `--minmeta`** to prevent excess DICOM metadata from overflowing JSON sidecars — fMRIPrep and MRIQC may crash on bloated JSON files
2. **Use `{item:02d}` in templates** for auto-numbering runs: if multiple series match, they get `run-01`, `run-02`, etc. Without this, later runs silently overwrite earlier ones
3. **Filter by `dim3`/`dim4`** to exclude localizers (small `dim3`) and single-volume scouts (`dim4 == 1`)
4. **Check `s.is_motion_corrected`** to exclude scanner-generated MOCO series (e.g., `if not s.is_motion_corrected`)
5. **Check `s.is_derived`** to skip other derived/processed series
6. **Store heuristic with dataset** under `code/` for reproducibility
7. **Use `--files`** when DICOM organization doesn't follow a clean `{subject}` template pattern
8. **For new studies**: prefer ReproIn protocol naming from the start — it eliminates the need for custom heuristics entirely
9. **For existing data with arbitrary names**: consider the "map into reproin" approach rather than writing a fully custom heuristic — you get duplicate handling, session propagation, and other ReproIn features for free

## dcm2bids (Configuration-File-Based)

dcm2bids uses JSON configuration files instead of Python heuristics. Simpler for straightforward datasets.

**Repository**: https://github.com/UNFmontreal/Dcm2Bids
**Docs**: https://unfmontreal.github.io/Dcm2Bids/

### Installation

```bash
uv pip install dcm2bids
# Also installs dcm2niix
```

### Workflow

#### Step 1: Scaffold a BIDS directory

```bash
dcm2bids_scaffold -o /path/to/bids_output
```

Creates the basic BIDS structure with `dataset_description.json`, `README`, `.bidsignore`, etc.

#### Step 2: Run helper to inspect DICOM metadata

```bash
dcm2bids_helper -d /path/to/dicom_dir -o /path/to/bids_output
```

Creates `tmp_dcm2bids/helper/` with converted NIfTI files and JSON sidecars. Review the JSON files to find distinguishing metadata fields.

#### Step 3: Write configuration file

```json
{
    "descriptions": [
        {
            "id": "id_t1w",
            "datatype": "anat",
            "suffix": "T1w",
            "criteria": {
                "SeriesDescription": "*MPRAGE*",
                "ImageType": ["ORIGINAL", "PRIMARY", "M", "ND", "NORM"]
            }
        },
        {
            "id": "id_bold_rest",
            "datatype": "func",
            "suffix": "bold",
            "custom_entities": "task-rest",
            "criteria": {
                "SeriesDescription": "*REST*BOLD*",
                "ImageType": ["ORIGINAL", "PRIMARY", "M", "ND", "MOSAIC"]
            },
            "sidecar_changes": {
                "TaskName": "rest"
            }
        },
        {
            "id": "id_bold_nback",
            "datatype": "func",
            "suffix": "bold",
            "custom_entities": "task-nback",
            "criteria": {
                "SeriesDescription": "*NBACK*",
                "EchoTime": 0.03
            },
            "sidecar_changes": {
                "TaskName": "nback"
            }
        },
        {
            "id": "id_dwi",
            "datatype": "dwi",
            "suffix": "dwi",
            "custom_entities": "dir-AP",
            "criteria": {
                "SeriesDescription": "*DTI*AP*"
            }
        },
        {
            "id": "id_fmap_phasediff",
            "datatype": "fmap",
            "suffix": "phasediff",
            "criteria": {
                "SeriesDescription": "*field*map*",
                "EchoTime1": 0.00492,
                "EchoTime2": 0.00738
            },
            "sidecar_changes": {
                "IntendedFor": [
                    "bids::sub-{subject}/func/sub-{subject}_task-rest_bold.nii.gz",
                    "bids::sub-{subject}/func/sub-{subject}_task-nback_bold.nii.gz"
                ]
            }
        }
    ]
}
```

**Configuration file fields:**
- `datatype`: BIDS datatype (`anat`, `func`, `dwi`, `fmap`, etc.)
- `suffix`: BIDS suffix (`T1w`, `bold`, `dwi`, etc.)
- `custom_entities`: additional BIDS entities (`task-rest`, `dir-AP`, `acq-highres`, etc.)
- `criteria`: dictionary of DICOM/JSON metadata fields to match (supports wildcards `*`)
- `sidecar_changes`: fields to add/modify in the output JSON sidecar
- `id`: arbitrary identifier for the description (for logging)

#### Step 4: Convert

```bash
# Single subject
dcm2bids -d /path/to/dicom_dir -p 01 -c dcm2bids_config.json -o /path/to/bids_output

# With session
dcm2bids -d /path/to/dicom_dir -p 01 -s pre -c dcm2bids_config.json -o /path/to/bids_output

# Flags:
# -d : DICOM source directory
# -p : participant label
# -s : session label (optional)
# -c : configuration file
# -o : output BIDS directory
# --auto_extract_entities : auto-detect run numbers from DICOM
# --force_dcm2bids : overwrite existing conversions
```

### dcm2bids Tips

1. **Use `dcm2bids_helper` first** to see exactly what metadata dcm2niix extracts
2. **Criteria matching uses wildcards** (`*`) and is case-sensitive
3. **Multiple criteria** are ANDed together; use the most specific combination
4. **`sidecar_changes`** can inject any BIDS metadata (useful for `TaskName`, `IntendedFor`)
5. **Store config file** under `code/dcm2bids_config.json` for reproducibility

## BIDScoin (GUI + YAML Configuration)

BIDScoin provides a graphical interface and YAML-based configuration. Good for users who prefer visual mapping.

**Repository**: https://github.com/Donders-Institute/bidscoin
**Docs**: https://bidscoin.readthedocs.io/

### Installation

```bash
uv pip install bidscoin
# Optional: install with all plugin dependencies
uv pip install "bidscoin[all]"
```

### Workflow

```bash
# Step 1: Create a bidsmap template by scanning DICOMs
bidsmapper /path/to/raw /path/to/bids

# Step 2: Edit the bidsmap (launches GUI)
bidseditor /path/to/bids

# Step 3: Convert using the finalized bidsmap
bidscoiner /path/to/raw /path/to/bids
```

### BIDScoin Tips

1. **GUI-based editing** is BIDScoin's strength - the `bidseditor` shows DICOM metadata alongside BIDS mapping
2. **YAML bidsmap** can be edited manually if preferred
3. **Plugin architecture** supports custom conversion backends beyond dcm2niix
4. **Good for multi-site studies** where protocol names vary - visual mapping makes differences obvious

## Comparison

| Feature | HeuDiConv | dcm2bids | BIDScoin |
|---------|-----------|----------|----------|
| Configuration | Python heuristic | JSON config | YAML + GUI |
| Flexibility | Highest (full Python) | Medium (criteria matching) | Medium (plugin system) |
| Learning curve | Steeper (Python) | Moderate | Gentlest (GUI) |
| Batch processing | Excellent | Good | Good |
| ReproIn support | Built-in | No | No |
| DataLad integration | Built-in | No | No |
| Best for | Complex studies, automation | Simple-to-moderate studies | Visual learners, multi-site |
| Active development | Yes | Yes | Yes |

## Post-Conversion Checklist

After converting DICOM to BIDS with any tool:

1. **Run the BIDS validator**: `bids-validator /path/to/bids_output`
2. **Check JSON sidecars** for critical fields (`RepetitionTime`, `TaskName`, `SliceTiming`, `PhaseEncodingDirection`)
3. **Verify NIfTI headers** match expectations (dimensions, voxel sizes, orientation)
4. **Add missing metadata** that dcm2niix couldn't extract from DICOM
5. **Create `participants.tsv`** with demographic data
6. **Write events files** for task fMRI
7. **Write `README`** describing the dataset
8. **Deface anatomical images** if sharing data
9. **Run `bids-validator` again** after any manual modifications

## Common DICOM-to-BIDS Pitfalls

### Multiband/SMS sequences
- dcm2niix may split slices incorrectly for multiband data
- Check `dim4` (number of volumes) matches expectations
- Verify `SliceTiming` is correct for the multiband factor

### Dual-echo fieldmaps
- Siemens stores both echoes in one series; dcm2niix splits them
- GE/Philips may store them as separate series
- Verify `EchoTime1` < `EchoTime2` in the phasediff sidecar

### Phase encoding direction
- DICOM `InPlanePhaseEncodingDirection` → BIDS `PhaseEncodingDirection`
- Mapping depends on acquisition orientation and NIfTI axis conventions
- **Always verify** by checking the actual distortion pattern in the images

### Multi-run numbering
- Ensure runs are numbered sequentially (`run-01`, `run-02`)
- HeuDiConv: use `{item:02d}` placeholder
- dcm2bids: use `--auto_extract_entities` or manually specify runs

### Derived/processed series
- Scanners may export inline-processed data (e.g., motion-corrected, distortion-corrected)
- These should NOT be converted to BIDS raw data
- Filter by `ImageType` containing `DERIVED` or `is_derived` flag in HeuDiConv

### `references/core_workflows.md`

# BIDS Core Workflows

The twelve workflow areas in full, with worked code and commands: directory structure,
`dataset_description.json`, querying with PyBIDS, validation (PyPI wrapper, Deno, legacy
Node, and `.bidsignore`), entities and file naming, DICOM-to-BIDS conversion with
HeuDiConv and dcm2bids, metadata sidecars, events files, the participants file,
derivatives, advanced PyBIDS usage, and running BIDS-Apps.

## Core Workflows

### 1. BIDS Directory Structure

A minimal BIDS dataset follows this layout:

```
my_dataset/
  dataset_description.json      # Required: name, BIDSVersion, etc.
  participants.tsv              # Recommended: subject-level phenotypic data
  participants.json             # Recommended: column descriptions
  README                        # Recommended: dataset documentation
  CHANGES                       # Recommended: version history
  .bidsignore                   # Optional: patterns to exclude from validation
  sub-01/
    anat/
      sub-01_T1w.nii.gz
      sub-01_T1w.json           # Sidecar metadata
    func/
      sub-01_task-rest_bold.nii.gz
      sub-01_task-rest_bold.json
      sub-01_task-rest_events.tsv     # Event timing for task fMRI
      sub-01_task-rest_events.json
    dwi/
      sub-01_dwi.nii.gz
      sub-01_dwi.json
      sub-01_dwi.bvec
      sub-01_dwi.bval
    fmap/
      sub-01_phasediff.nii.gz
      sub-01_phasediff.json
      sub-01_magnitude1.nii.gz
    perf/
      sub-01_asl.nii.gz
      sub-01_asl.json
  sub-01/
    ses-pre/
      anat/
        sub-01_ses-pre_T1w.nii.gz
      func/
        sub-01_ses-pre_task-nback_bold.nii.gz
    ses-post/
      ...
```

**Key points:**
- Every NIfTI file should have a corresponding `.json` sidecar
- File names encode entities: `sub-<label>[_ses-<label>][_task-<label>][_acq-<label>][_run-<index>]_<suffix>.<extension>`
- Entity order in filenames is fixed by the specification
- Only `dataset_description.json` is strictly required at the root level

### 2. Creating dataset_description.json

```python
import json

dataset_description = {
    "Name": "My Neuroimaging Study",
    "BIDSVersion": "1.10.0",
    "DatasetType": "raw",
    "License": "CC0",
    "Authors": ["First Author", "Second Author"],
    "Acknowledgements": "Funded by NIH R01-MH123456",
    "HowToAcknowledge": "Please cite: Author et al. (2025) Journal Name.",
    "Funding": ["NIH R01-MH123456", "NSF BCS-7654321"],
    "ReferencesAndLinks": ["https://doi.org/10.xxxx/xxxxx"],
    "DatasetDOI": "10.18112/openneuro.ds000001.v1.0.0",
    "GeneratedBy": [
        {
            "Name": "HeuDiConv",
            "Version": "1.3.1",
            "CodeURL": "https://github.com/nipy/heudiconv"
        }
    ]
}

with open("dataset_description.json", "w") as f:
    json.dump(dataset_description, f, indent=4)
```

For **derivatives**, set `"DatasetType": "derivative"` and add `"GeneratedBy"` listing the pipeline:

```python
deriv_description = {
    "Name": "fMRIPrep - fMRI PREProcessing",
    "BIDSVersion": "1.10.0",
    "DatasetType": "derivative",
    "GeneratedBy": [
        {
            "Name": "fMRIPrep",
            "Version": "24.1.0",
            "CodeURL": "https://github.com/nipreps/fmriprep"
        }
    ]
}
```

### 3. Querying BIDS Datasets with PyBIDS

```python
from bids import BIDSLayout

# Index a BIDS dataset (validates structure on load)
layout = BIDSLayout("/path/to/bids_dataset")

# Basic queries
subjects = layout.get_subjects()          # ['01', '02', '03', ...]
sessions = layout.get_sessions()          # ['pre', 'post'] or []
tasks = layout.get_tasks()                # ['rest', 'nback']
runs = layout.get_runs()                  # [1, 2] or []

# Find specific files
bold_files = layout.get(
    suffix="bold",
    extension=".nii.gz",
    return_type="filename"
)

# Filter by subject, task, session
nback_sub01 = layout.get(
    subject="01",
    task="nback",
    suffix="bold",
    extension=".nii.gz",
    return_type="filename"
)

# Get metadata from JSON sidecars (automatic inheritance)
metadata = layout.get_metadata("/path/to/sub-01/func/sub-01_task-rest_bold.nii.gz")
tr = metadata["RepetitionTime"]

# Get all entities for a file
entities = layout.get_entities()

# Build a path from entities using BIDSLayout
bids_file = layout.get(subject="01", suffix="T1w", extension=".nii.gz")[0]
print(bids_file.path)
print(bids_file.get_entities())
```

**Key points:**
- `BIDSLayout` indexes the entire dataset on initialization; for large datasets use `database_path` to cache the index
- Metadata inheritance: a JSON sidecar at a higher level (e.g., root or subject) is inherited by all files below unless overridden
- Use `return_type="filename"` for paths, `return_type="object"` (default) for `BIDSFile` objects

### 4. Validating BIDS Datasets

#### Using bids-validator via PyPI (recommended)

The `bids-validator-deno` PyPI package bundles the Deno-based validator as a standalone CLI:

```bash
# Install
uv pip install bids-validator-deno

# Validate a dataset
bids-validator /path/to/bids_dataset

# Ignore specific warnings/errors
bids-validator /path/to/bids_dataset --ignoreNiftiHeaders --ignoreSubjectConsistency
```

#### Using bids-validator via Deno directly

If Deno is already available, you can install or run the validator without PyPI:

```bash
# Install globally via Deno
deno install -g -A npm:bids-validator

# Or run without installing
deno run -A npm:bids-validator /path/to/bids_dataset
```

#### Legacy Node.js validator

The older Node.js-based validator (`npm install -g bids-validator`) is deprecated in favor of the Deno-based version. The Deno version is the reference implementation for BIDS Specification v1.9+.

#### Using .bidsignore

Create `.bidsignore` at the dataset root to exclude files from validation (gitignore syntax):

```
# Exclude sourcedata and extra files
sourcedata/
extra_data/
*.log
*_sbref.nii.gz
**/.DS_Store
```

### 5. BIDS Entities and File Naming

The authoritative, machine-readable source of truth for entities, their ordering, allowed suffixes, and all filename rules is the **BIDS Schema** — a structured YAML/JSON representation of the specification. A JSON export is shipped with this skill at `references/bids_schema.json`. The schema is defined in the [bids-specification `src/schema/`](https://github.com/bids-standard/bids-specification/tree/master/src/schema) directory and published at https://bids-specification.readthedocs.io/en/stable/schema.json. BEP-specific schema previews are available at https://github.com/bids-standard/bids-schema/tree/main/BEPs.

Run `scripts/update_schema.py` to refresh the schema and BEPs list from upstream (no dependencies beyond stdlib).

The tables below are a convenient summary; when in doubt, consult the schema.

BIDS filenames are built from ordered key-value entity pairs:

| Entity | Key | Example | Required for |
|--------|-----|---------|--------------|
| Subject | `sub-` | `sub-01` | All files |
| Session | `ses-` | `ses-pre` | Multi-session studies |
| Task | `task-` | `task-rest` | func (bold, cbv, phase), eeg, meg |
| Acquisition | `acq-` | `acq-highres` | Distinguishing acquisition parameters |
| Contrast enhancing agent | `ce-` | `ce-gadolinium` | Contrast-enhanced images |
| Reconstruction | `rec-` | `rec-magnitude` | Reconstruction variants |
| Direction | `dir-` | `dir-AP` | Fieldmaps, DWI, phase-encoding |
| Run | `run-` | `run-01` | Multiple identical acquisitions |
| Echo | `echo-` | `echo-1` | Multi-echo sequences |
| Part | `part-` | `part-mag` | Magnitude/phase splits |
| Space | `space-` | `space-MNI152NLin2009cAsym` | Derivatives in template space |
| Description | `desc-` | `desc-preproc` | Derivatives only |

**Entity ordering in filenames** is fixed by the spec (defined in `rules.entities` in `bids_schema.json`). See `references/bids_specification.md` for the complete numbered ordering table. A common subset:
`sub-<label>[_ses-<label>][_task-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_dir-<label>][_run-<index>][_echo-<index>][_part-<label>][_space-<label>][_desc-<label>]_<suffix>.<extension>`

**Common suffixes by datatype:**

| Datatype | Suffixes |
|----------|----------|
| anat | `T1w`, `T2w`, `FLAIR`, `T2star`, `T1map`, `T2map`, `defacemask` |
| func | `bold`, `cbv`, `sbref`, `events`, `physio`, `stim` |
| dwi | `dwi`, `sbref` |
| fmap | `phasediff`, `phase1`, `phase2`, `magnitude1`, `magnitude2`, `fieldmap`, `epi` |
| perf | `asl`, `m0scan`, `aslcontext` |
| eeg | `eeg`, `channels`, `electrodes`, `events` |
| meg | `meg`, `channels`, `coordsystem`, `events` |
| ieeg | `ieeg`, `channels`, `electrodes`, `coordsystem`, `events` |
| pet | `pet`, `blood` |

### 6. DICOM to BIDS Conversion

#### HeuDiConv

HeuDiConv is the most flexible DICOM-to-BIDS converter. It supports three usage modes — from fully automatic to fully custom — and handles duplicates, provenance tracking, and sourcedata archiving out of the box.

**Mode 1: ReproIn (turnkey, recommended for new studies)**

If scanner protocol names follow the [ReproIn naming convention](https://github.com/repronim/reproin), conversion is fully automatic — no heuristic file to write:

```bash
# Turnkey conversion: HeuDiConv maps ReproIn protocol names to BIDS automatically
heudiconv --files dicom/001 -o /path/to/bids -f reproin --bids --minmeta
```

ReproIn protocol names encode BIDS entities directly:
- `anat-T1w` → `sub-XX/anat/sub-XX_T1w.nii.gz`
- `func-bold_task-rest` → `sub-XX/func/sub-XX_task-rest_bold.nii.gz`
- `dwi_dir-AP` → `sub-XX/dwi/sub-XX_dir-AP_dwi.nii.gz`
- `fmap_dir-PA` → `sub-XX/fmap/sub-XX_dir-PA_epi.nii.gz`

Session can be set once on the localizer (e.g., `anat-scout_ses-pre`) and ReproIn propagates it to all sequences in that Program. Subject ID is extracted from DICOM metadata. Duplicate runs are numbered automatically.

**Mode 2: Custom heuristic mapping into ReproIn (for existing data)**

If you already have data with non-ReproIn protocol names, you can write a thin heuristic that maps your names into ReproIn conventions, gaining all ReproIn benefits (automatic entity handling, duplicate management, etc.). See https://github.com/repronim/reproin/issues/18 for a HOWTO.

**Mode 3: Custom heuristic (full flexibility)**

For complex mappings, write a Python heuristic file:

```bash
# Step 1: Reconnaissance — discover DICOM series
heudiconv --files dicom/219/itbs/*/*.dcm -o Nifti/ -f convertall -s 219 -c none

# This creates .heudiconv/219/info/dicominfo.tsv — inspect it to understand
# what was acquired and map series to BIDS names.

# Step 2: Write a heuristic file (see references/conversion_tools.md)

# Step 3: Convert
heudiconv --files dicom/219/itbs/*/*.dcm -s 219 -ss itbs \
  -f Nifti/code/heuristic.py -c dcm2niix --bids --minmeta -o Nifti/
```

See `references/conversion_tools.md` for complete heuristic file examples.

**Key points:**
- HeuDiConv wraps `dcm2niix` for the actual DICOM-to-NIfTI conversion
- **`--minmeta`**: always use this flag to prevent excess DICOM metadata from overflowing JSON sidecars (can crash fMRIPrep/MRIQC)
- **Duplicate handling**: use `{item:03d}` in templates for auto-numbering when the same protocol is run multiple times; without it, later runs overwrite earlier ones
- **`.heudiconv/` directory**: created alongside output, stores provenance (heuristic used, dicominfo.tsv, conversion records). Keep it with your data for reproducibility
- **`sourcedata/`**: HeuDiConv archives original DICOMs as `.tgz` files under `sourcedata/` for reproducibility
- **`is_motion_corrected` filter**: use in heuristics to exclude scanner-generated MOCO series (e.g., `if not s.is_motion_corrected`)
- Both `--files` (explicit paths) and `-d` (template with `{subject}`, `{session}` placeholders) are supported for specifying DICOM input

#### dcm2bids (Configuration-file-based)

```bash
# Step 1: Generate helper output to inspect series
dcm2bids_helper -d /path/to/dicom

# Step 2: Create config file (dcm2bids_config.json)
# Step 3: Convert
dcm2bids -d /path/to/dicom -p 01 -c dcm2bids_config.json -o /path/to/bids_output
```

See `references/conversion_tools.md` for detailed configuration examples.

### 7. Metadata Sidecars

Every BIDS data file should have a JSON sidecar with acquisition parameters. Metadata fields follow the inheritance principle: a sidecar at a higher directory level applies to all matching files below.

**Inheritance example:**
```
my_dataset/
  task-rest_bold.json           # Applies to ALL rest BOLD files
  sub-01/
    func/
      sub-01_task-rest_bold.json  # Overrides/extends for sub-01 only
```

**Critical metadata fields by modality:**

For **func (BOLD)**:
```json
{
    "RepetitionTime": 2.0,
    "TaskName": "rest",
    "PhaseEncodingDirection": "j-",
    "TotalReadoutTime": 0.05,
    "SliceTiming": [0, 0.5, 1.0, 1.5],
    "EffectiveEchoSpacing": 0.00058,
    "EchoTime": 0.03
}
```

For **anat**:
```json
{
    "MagneticFieldStrength": 3,
    "Manufacturer": "Siemens",
    "ManufacturersModelName": "Prisma",
    "RepetitionTime": 2.3,
    "EchoTime": 0.00293,
    "FlipAngle": 8
}
```

For **DWI**:
```json
{
    "PhaseEncodingDirection": "j-",
    "TotalReadoutTime": 0.05,
    "EchoTime": 0.089,
    "RepetitionTime": 3.4,
    "MultipartID": "dwi_1"
}
```

**Key points:**
- `dcm2niix` auto-generates most sidecar fields from DICOM headers
- `RepetitionTime` and `TaskName` are required for BOLD
- `SliceTiming` is essential for slice-timing correction in fMRI preprocessing
- `PhaseEncodingDirection` and `TotalReadoutTime` (or `EffectiveEchoSpacing`) are needed for distortion correction
- See `references/metadata_fields.md` for comprehensive field reference

### 8. Events Files for Task fMRI

Task-based fMRI requires `_events.tsv` files:

```
onset	duration	trial_type	response_time
0.0	0.5	face	0.435
2.5	0.5	house	0.367
5.0	0.5	face	0.512
7.5	0.5	scrambled	0.298
```

**Required columns:**
- `onset` - onset time in seconds relative to the start of the acquisition
- `duration` - duration in seconds (use `n/a` for instantaneous events)

**Recommended columns:**
- `trial_type` - categorical label for condition
- `response_time` - RT in seconds
- Custom columns as needed (with descriptions in corresponding `.json` sidecar)

### 9. Participants File

```
participant_id	age	sex	group	handedness
sub-01	25	M	control	right
sub-02	30	F	patient	left
sub-03	28	M	control	right
```

The `participants.json` sidecar describes columns:

```json
{
    "age": {
        "Description": "Age of the participant at time of scanning",
        "Units": "years"
    },
    "sex": {
        "Description": "Biological sex",
        "Levels": {
            "M": "male",
            "F": "female"
        }
    },
    "group": {
        "Description": "Experimental group",
        "Levels": {
            "control": "Healthy control",
            "patient": "Patient group"
        }
    },
    "handedness": {
        "Description": "Dominant hand",
        "Levels": {
            "right": "Right-handed",
            "left": "Left-handed",
            "ambidextrous": "Ambidextrous"
        }
    }
}
```

### 10. BIDS Derivatives

Processed outputs go under a `derivatives/` directory:

```
my_dataset/
  derivatives/
    fmriprep-24.1.0/
      dataset_description.json      # DatasetType: "derivative"
      sub-01/
        anat/
          sub-01_space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz
          sub-01_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz
        func/
          sub-01_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
          sub-01_task-rest_desc-confounds_timeseries.tsv
    mriqc-24.0.0/
      dataset_description.json
      sub-01/
        anat/
          sub-01_T1w.html
        func/
          sub-01_task-rest_bold.html
      group_T1w.tsv
      group_bold.tsv
```

**Derivative conventions:**
- `space-<label>` - template/reference space (e.g., `MNI152NLin2009cAsym`, `T1w`)
- `desc-<label>` - description of processing (e.g., `preproc`, `brain`, `smoothed`)
- `res-<label>` - resolution (e.g., `2` for 2mm isotropic)
- Each pipeline gets its own directory under `derivatives/`
- Must have its own `dataset_description.json` with `GeneratedBy`

### 11. PyBIDS: Advanced Usage

```python
from bids import BIDSLayout
from bids.layout import BIDSLayoutIndexer

# Cache the layout index for faster repeated access
layout = BIDSLayout("/path/to/dataset", database_path="/path/to/cache.db")

# Include derivatives
layout = BIDSLayout(
    "/path/to/dataset",
    derivatives=["/path/to/dataset/derivatives/fmriprep-24.1.0"]
)

# Get derivative files
preproc = layout.get(
    subject="01",
    task="rest",
    desc="preproc",
    suffix="bold",
    space="MNI152NLin2009cAsym",
    extension=".nii.gz",
    return_type="filename"
)

# Get confound regressors
confounds = layout.get(
    subject="01",
    task="rest",
    desc="confounds",
    suffix="timeseries",
    extension=".tsv",
    return_type="filename"
)

# Build BIDS path from entities
from bids import BIDSLayout
layout = BIDSLayout("/path/to/dataset")
path = layout.build_path(
    {
        "subject": "01",
        "session": "pre",
        "task": "rest",
        "suffix": "bold",
        "extension": ".nii.gz",
        "datatype": "func"
    },
    validate=True
)

# Get all files for a subject as a DataFrame
import pandas as pd
files_df = layout.to_df()
sub01_df = files_df[files_df["subject"] == "01"]
```

### 12. BIDS-Apps

BIDS-Apps are containerized analysis pipelines that accept BIDS datasets as input:

```bash
# General BIDS-App invocation pattern
docker run -v /path/to/bids:/data:ro -v /path/to/output:/out \
    <bids-app-image> /data /out participant --participant_label 01

# Common BIDS-Apps:
# fMRIPrep - fMRI preprocessing
docker run nipreps/fmriprep /data /out participant \
    --participant-label 01 --fs-license-file /license.txt

# MRIQC - MRI quality control
docker run nipreps/mriqc /data /out participant \
    --participant-label 01

# QSIPrep - diffusion MRI preprocessing
docker run pennbbl/qsiprep /data /out participant \
    --participant-label 01
```

**BIDS-App interface convention:**
```
bids-app input_dataset output_dir {participant|group} [options]
```

- `participant` level: runs per-subject
- `group` level: runs across all subjects (aggregation/group stats)

### `references/metadata_fields.md`

# BIDS Metadata Fields Reference

This reference lists the required and recommended JSON sidecar fields for each BIDS modality.

**Legend:**
- **R** = Required
- **REC** = Recommended
- **OPT** = Optional

## Common MRI Fields (All MRI Modalities)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `MagneticFieldStrength` | REC | number | Field strength in Tesla |
| `Manufacturer` | REC | string | Scanner manufacturer |
| `ManufacturersModelName` | REC | string | Scanner model |
| `DeviceSerialNumber` | REC | string | Scanner serial number |
| `StationName` | REC | string | Scanner station name |
| `SoftwareVersions` | REC | string | Scanner software version |
| `InstitutionName` | REC | string | Name of institution |
| `InstitutionAddress` | REC | string | Address of institution |
| `InstitutionalDepartmentName` | REC | string | Department name |

## Anatomical MRI (anat/)

### T1w, T2w, FLAIR, T2star, PDw

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `RepetitionTime` | REC | number | TR in seconds |
| `EchoTime` | REC | number | TE in seconds |
| `InversionTime` | REC | number | TI in seconds (if applicable) |
| `FlipAngle` | REC | number | Flip angle in degrees |
| `SequenceName` | REC | string | Pulse sequence name |
| `SequenceVariant` | REC | string | Variant of the sequence |
| `ScanningSequence` | REC | string | General description |
| `PulseSequenceType` | REC | string | Type of pulse sequence |
| `NonlinearGradientCorrection` | REC | boolean | Whether applied |
| `ParallelReductionFactorInPlane` | REC | number | iPAT/GRAPPA factor |
| `ContrastBolusIngredient` | REC | string | Active contrast ingredient |

### Quantitative MRI (T1map, T2map, etc.)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `RepetitionTimeExcitation` | R | number | Excitation TR in seconds |
| `RepetitionTimePrepration` | R | number | Preparation TR in seconds |
| `FlipAngle` | R | number/array | Flip angle(s) in degrees |
| `MTState` | R | boolean | Magnetization transfer on/off |
| `SpoilingState` | REC | boolean | Whether RF spoiling applied |
| `SpoilingType` | REC | string | `RF`, `GRADIENT`, or `COMBINED` |
| `SpoilingRFPhaseIncrement` | REC | number | Phase increment in degrees |

## Functional MRI (func/)

### BOLD

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `RepetitionTime` | R | number | TR in seconds (volume acquisition time) |
| `TaskName` | R | string | Name of the task (must match `task-<label>`) |
| `SliceTiming` | REC | array | Time each slice was acquired, in seconds |
| `EchoTime` | REC | number | TE in seconds |
| `FlipAngle` | REC | number | Flip angle in degrees |
| `PhaseEncodingDirection` | REC | string | `i`, `i-`, `j`, `j-`, `k`, `k-` |
| `EffectiveEchoSpacing` | REC | number | Effective echo spacing in seconds |
| `TotalReadoutTime` | REC | number | Total readout time in seconds |
| `MultibandAccelerationFactor` | REC | number | Multiband/SMS factor |
| `NumberOfVolumesDiscardedByScanner` | REC | integer | Dummy scans removed |
| `NumberOfVolumesDiscardedByUser` | REC | integer | Volumes removed post-hoc |
| `TaskDescription` | REC | string | Longer description of the task |
| `CogAtlasID` | REC | string | Cognitive Atlas ID for the task |
| `CogPOID` | REC | string | Cognitive Paradigm Ontology ID |
| `Instructions` | REC | string | Instructions given to participants |

### Multi-echo BOLD

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `EchoTime` | R | number | TE for this echo (each echo in separate file) |
| `EchoTime1`, `EchoTime2` | - | - | NOT used; use `echo-<index>` entity |

### BOLD Timing Details

**SliceTiming** - Array of times (in seconds) at which each slice was acquired relative to the start of volume acquisition. Length must equal the number of slices.

Example for ascending sequential (3 slices, TR=2s):
```json
{"SliceTiming": [0.0, 0.667, 1.333]}
```

Example for interleaved (odd-first, 6 slices, TR=2s):
```json
{"SliceTiming": [0.0, 0.667, 1.333, 0.333, 1.0, 1.667]}
```

**PhaseEncodingDirection** values:
- `i` / `i-` : along first image axis (typically left-right)
- `j` / `j-` : along second image axis (typically anterior-posterior)
- `k` / `k-` : along third image axis (typically inferior-superior)
- The `-` suffix indicates the negative direction along that axis

## Diffusion-Weighted Imaging (dwi/)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `PhaseEncodingDirection` | R | string | Phase encoding direction |
| `TotalReadoutTime` | R | number | Total readout time in seconds |
| `EchoTime` | REC | number | TE in seconds |
| `RepetitionTime` | REC | number | TR in seconds |
| `FlipAngle` | REC | number | Flip angle in degrees |
| `EffectiveEchoSpacing` | REC | number | Effective echo spacing in seconds |
| `MultibandAccelerationFactor` | REC | number | SMS/multiband factor |
| `SliceTiming` | REC | array | Slice timing |

### DWI Gradient Files

`.bvec` file (3 rows x N columns, N = number of volumes):
```
0 0.707 -0.707 0 0.577
0 0.707 0.707 0 0.577
0 0 0 1 0.577
```

`.bval` file (1 row x N columns):
```
0 1000 1000 1000 2000
```

- b=0 volumes have zero-vectors in `.bvec`
- Gradient directions are in the image coordinate system
- Values are space-separated (not tab-separated)
- Number of columns must match number of volumes in the NIfTI

## Fieldmaps (fmap/)

### Case 1: Phase-difference map (`_phasediff`)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `EchoTime1` | R | number | TE of the first echo (shorter) |
| `EchoTime2` | R | number | TE of the second echo (longer) |
| `IntendedFor` | R | string/array | BIDS URI(s) of files to correct |
| `B0FieldIdentifier` | REC | string | Identifier for this B0 field |

### Case 2: Two phase maps (`_phase1`, `_phase2`)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `EchoTime` | R | number | TE for this phase image |
| `IntendedFor` | R | string/array | Files to correct |

### Case 3: Direct fieldmap (`_fieldmap`)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `Units` | R | string | Must be `Hz` or `rad/s` |
| `IntendedFor` | R | string/array | Files to correct |

### Case 4: "Pepolar" fieldmaps (`_epi`)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `PhaseEncodingDirection` | R | string | PE direction for this image |
| `TotalReadoutTime` | R | number | Total readout time |
| `IntendedFor` | R | string/array | Files to correct |
| `B0FieldIdentifier` | REC | string | Identifier for this B0 field |
| `B0FieldSource` | REC | string | Which B0 field to use |

### IntendedFor Syntax

**BIDS URI format** (recommended, v1.7+):
```json
{
    "IntendedFor": [
        "bids::sub-01/func/sub-01_task-rest_bold.nii.gz",
        "bids::sub-01/dwi/sub-01_dwi.nii.gz"
    ]
}
```

**Relative path format** (legacy):
```json
{
    "IntendedFor": [
        "func/sub-01_task-rest_bold.nii.gz",
        "dwi/sub-01_dwi.nii.gz"
    ]
}
```

**B0FieldIdentifier/B0FieldSource** (preferred in v1.9+):
```json
// In the fieldmap sidecar
{"B0FieldIdentifier": "pepolar_fmap0"}

// In the BOLD sidecar
{"B0FieldSource": "pepolar_fmap0"}
```

## Perfusion Imaging (perf/)

### ASL

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `ArterialSpinLabelingType` | R | string | `CASL`, `PCASL`, or `PASL` |
| `PostLabelingDelay` | R | number/array | PLD in seconds |
| `BackgroundSuppression` | R | boolean | Whether applied |
| `MagneticFieldStrength` | R | number | In Tesla |
| `M0Type` | R | string | `Separate`, `Included`, `Estimate`, `Absent` |
| `RepetitionTimePreparation` | R | number | Time between ASL pulses |
| `LabelingDuration` | R | number | Duration of labeling pulse |
| `BackgroundSuppressionNumberPulses` | REC | integer | Number of suppression pulses |
| `BackgroundSuppressionPulseTime` | REC | array | Timing of suppression pulses |
| `VascularCrushing` | REC | boolean | Whether applied |
| `LabelingOrientation` | REC | string | Orientation of labeling plane |
| `LabelingDistance` | REC | number | Distance from isocenter (mm) |
| `BolusCutOffFlag` | R (PASL) | boolean | Whether QUIPSS applied |
| `BolusCutOffTimingSequence` | R (PASL) | string | QUIPSS sequence type |
| `BolusCutOffDelayTime` | R (PASL) | number | QUIPSS delay time |

### aslcontext.tsv

Required file listing the order of volumes (label/control/m0scan):
```
volume_type
control
label
control
label
m0scan
```

## EEG (eeg/)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `TaskName` | R | string | Name of the task |
| `SamplingFrequency` | R | number | In Hz |
| `EEGReference` | R | string | Reference electrode(s) |
| `PowerLineFrequency` | R | number | 50 or 60 Hz (or `n/a`) |
| `SoftwareFilters` | R | object | Online filters applied |
| `EEGPlacementScheme` | REC | string | e.g., `10-20`, `10-10` |
| `CapManufacturer` | REC | string | Cap manufacturer |
| `CapManufacturersModelName` | REC | string | Cap model |
| `EEGChannelCount` | REC | integer | Number of EEG channels |
| `EOGChannelCount` | REC | integer | Number of EOG channels |
| `ECGChannelCount` | REC | integer | Number of ECG channels |
| `EMGChannelCount` | REC | integer | Number of EMG channels |
| `MiscChannelCount` | REC | integer | Number of misc channels |
| `TriggerChannelCount` | REC | integer | Number of trigger channels |
| `RecordingDuration` | REC | number | In seconds |
| `RecordingType` | REC | string | `continuous`, `epoched`, `discontinuous` |

### channels.tsv (EEG)

| Column | Status | Description |
|--------|--------|-------------|
| `name` | R | Channel name |
| `type` | R | `EEG`, `EOG`, `ECG`, `EMG`, `MISC`, `TRIG`, etc. |
| `units` | R | `V`, `mV`, `uV` |
| `sampling_frequency` | OPT | Per-channel if different |
| `low_cutoff` | REC | High-pass filter frequency (Hz) |
| `high_cutoff` | REC | Low-pass filter frequency (Hz) |
| `notch` | REC | Notch filter frequency (Hz) |
| `reference` | REC | Reference electrode name |
| `status` | REC | `good` or `bad` |
| `status_description` | OPT | Reason for bad status |

### electrodes.tsv (EEG)

| Column | Status | Description |
|--------|--------|-------------|
| `name` | R | Electrode name |
| `x` | R | X coordinate |
| `y` | R | Y coordinate |
| `z` | R | Z coordinate |
| `type` | OPT | Electrode type |
| `material` | OPT | Electrode material |
| `impedance` | OPT | Impedance in kOhm |

## MEG (meg/)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `TaskName` | R | string | Name of the task |
| `SamplingFrequency` | R | number | In Hz |
| `PowerLineFrequency` | R | number | 50 or 60 Hz |
| `DewarPosition` | R | string | Position of the dewar |
| `SoftwareFilters` | R | object | Online filters |
| `DigitizedLandmarks` | R | boolean | Fiducials digitized |
| `DigitizedHeadPoints` | R | boolean | Head shape digitized |
| `MEGChannelCount` | REC | integer | Number of MEG channels |
| `MEGREFChannelCount` | REC | integer | Reference channels |
| `ContinuousHeadLocalization` | REC | boolean | HPI on |
| `HeadCoilFrequency` | REC | array | HPI coil frequencies |
| `InstitutionName` | REC | string | Institution name |

## PET (pet/)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `TracerName` | R | string | Name of the radiotracer |
| `TracerRadionuclide` | R | string | e.g., `C11`, `F18`, `O15` |
| `InjectedRadioactivity` | R | number | In MBq |
| `InjectedRadioactivityUnits` | R | string | Must be `MBq` |
| `InjectedMass` | R | number | Mass of tracer injected |
| `InjectedMassUnits` | R | string | e.g., `ug` |
| `ModeOfAdministration` | R | string | `bolus`, `infusion`, `bolus-infusion` |
| `TimeZero` | R | string | Time of injection (HH:MM:SS) |
| `ScanStart` | R | number | Start time relative to TimeZero |
| `InjectionStart` | R | number | Injection time relative to TimeZero |
| `FrameTimesStart` | R | array | Frame start times in seconds |
| `FrameDuration` | R | array | Frame durations in seconds |
| `Units` | R | string | Unit of voxel values (e.g., `Bq/mL`) |
| `TracerRadLex` | REC | string | RadLex ID for tracer |
| `BodyWeight` | REC | number | In kg |
| `BodyPart` | REC | string | Imaged body part |
| `AttenuationCorrection` | REC | string | Method description |
| `ReconMethodName` | REC | string | Reconstruction method |
| `ReconMethodParameterLabels` | REC | array | Parameter names |
| `ReconMethodParameterValues` | REC | array | Parameter values |
| `ReconFilterType` | REC | string | Post-recon filter type |
| `ReconFilterSize` | REC | number | Filter FWHM in mm |

## Microscopy (micr/)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `Manufacturer` | R | string | Microscope manufacturer |
| `ManufacturersModelName` | R | string | Microscope model |
| `PixelSize` | R | array | [X, Y] or [X, Y, Z] in micrometers |
| `PixelSizeUnits` | R | string | `um` (micrometers) |
| `Magnification` | REC | number | Objective magnification |
| `SampleEnvironment` | R | string | `in vivo`, `ex vivo`, `in vitro` |
| `SampleFixation` | REC | string | Fixation method |
| `SampleStaining` | REC | string | Staining protocol |
| `SliceThickness` | REC | number | In micrometers |
| `TissueDeformationScaling` | REC | number | Scaling factor |

## NIRS (nirs/)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `TaskName` | R | string | Name of the task |
| `SamplingFrequency` | R | number | In Hz |
| `NIRSSourceOptodeCount` | R | integer | Number of sources |
| `NIRSDetectorOptodeCount` | R | integer | Number of detectors |
| `ACCELChannelCount` | REC | integer | Accelerometer channels |
| `NIRSPlacementScheme` | REC | string | e.g., `10-20` |

## Motion (motion/)

| Field | Status | Type | Description |
|-------|--------|------|-------------|
| `TaskName` | R | string | Name of the task |
| `SamplingFrequency` | R | number | In Hz |
| `TrackingSystemName` | R | string | Name of tracking system |
| `ACCELChannelCount` | REC | integer | Accelerometer channels |
| `GYROChannelCount` | REC | integer | Gyroscope channels |
| `MAGNChannelCount` | REC | integer | Magnetometer channels |
| `RotationOrder` | REC | string | e.g., `XYZ` |
| `RotationRule` | REC | string | `left-hand` or `right-hand` |
| `SpatialAxes` | REC | string | e.g., `ALS` |

### `scripts/update_schema.py`

```python
#!/usr/bin/env python3
"""Update BIDS schema JSON and BEPs list from upstream sources.

Downloads:
  - bids_schema.json from bids-specification ReadTheDocs (stable release)
  - beps.yml from bids-standard/bids-website (current BEP listing)

Usage:
    python scripts/update_schema.py

    # Fetch schema for a specific spec version or PR preview:
    python scripts/update_schema.py --schema-url https://bids-specification.readthedocs.io/en/v1.11.0/schema.json

    # Fetch a BEP-specific schema from bids-standard/bids-schema:
    python scripts/update_schema.py --schema-url https://raw.githubusercontent.com/bids-standard/bids-schema/main/BEPs/BEP032/schema.json

No external dependencies beyond the Python standard library.
"""

import argparse
import json
import urllib.request
from pathlib import Path

REFERENCES_DIR = Path(__file__).resolve().parent.parent / "references"

SCHEMA_URL = "https://bids-specification.readthedocs.io/en/stable/schema.json"
BEPS_URL = "https://raw.githubusercontent.com/bids-standard/bids-website/main/data/beps/beps.yml"


def fetch(url):
    """Fetch URL content as bytes."""
    print(f"Fetching {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "bids-skill-updater/1.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def update_schema(url):
    """Download schema.json and report version info."""
    data = fetch(url)
    output = REFERENCES_DIR / "bids_schema.json"

    # Validate it's proper JSON and extract version
    d = json.loads(data)
    # Re-serialize with consistent formatting
    with open(output, "w") as f:
        json.dump(d, f, indent=2)
        f.write("\n")

    sv = d.get("schema_version", "?")
    bv = d.get("bids_version", "?")
    print(f"  -> {output.name}: schema {sv} / BIDS {bv}")


def update_beps():
    """Download beps.yml."""
    data = fetch(BEPS_URL)
    output = REFERENCES_DIR / "beps.yml"
    output.write_bytes(data)

    # Count entries
    count = data.count(b"\n-   number:")
    print(f"  -> {output.name}: {count} BEPs")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--schema-url",
        default=SCHEMA_URL,
        help=f"URL for schema.json (default: {SCHEMA_URL})",
    )
    parser.add_argument(
        "--skip-beps",
        action="store_true",
        help="Skip fetching beps.yml",
    )
    args = parser.parse_args()

    update_schema(args.schema_url)
    if not args.skip_beps:
        update_beps()

    print("Done.")


if __name__ == "__main__":
    main()
```
