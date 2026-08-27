---
name: matchms
description: Process, clean, compare, and search tandem mass spectra with matchms. Use for MS/MS file I/O, metadata harmonization, peak filtering, spectral similarity, library matching, score matrices, and molecular-similarity networks. Use pyopenms instead for LC-MS feature detection or proteomics pipelines.
---

# Matchms

## Purpose and Scope

Matchms is a Python package for importing, cleaning, processing, and comparing
tandem mass spectra. This skill targets **matchms 0.33.1**, released 2026-06-08,
and corrects several breaking API changes that older tutorials do not reflect.

Use matchms for:

- MS/MS library search and query-versus-reference scoring
- Metadata harmonization, adduct/precursor handling, and peak filtering
- Cosine, modified-cosine, neutral-loss, approximate, and entropy scoring
- Structured score matrices, top-hit extraction, and spectral networks
- MGF, MSP, mzML, mzXML, JSON, mzSpecLib, and metabolomics-USI workflows

Do not use matchms as a replacement for:

- LC-MS feature detection, chromatographic alignment, peptide identification, or
  protein quantification — use pyopenms
- Vendor raw-file conversion — convert to mzML/mzXML first
- A validated compound-identification protocol — similarity is evidence, not
  proof of identity

## Install the Verified Release

Create or activate an environment, then install the release used by this skill:

```bash
uv pip install "matchms==0.33.1"
```

Verify the runtime:

```bash
uv run python -c "import matchms; print(matchms.__version__)"
```

Matchms 0.33.1 supports Python 3.10-3.14 and installs RDKit as a regular
dependency. The old `matchms[chemistry]` extra is not part of the current
package metadata.

## Operating Workflow

1. **Inspect the inputs.** Record format, spectrum count, MS level, precursor
   coverage, ion mode, peak counts, and identifier fields.
2. **Load with metadata harmonization enabled** unless preserving source keys is
   a deliberate requirement.
3. **Apply the same peak-processing steps** to query and reference spectra.
   Keep metadata enrichment separate when reference annotations are richer.
4. **Drop invalid spectra explicitly.** Many `require_*` filters return `None`.
5. **Choose the score from the scientific question**, not from convenience.
   Modified and neutral-loss scores require valid `precursor_mz`.
6. **Estimate `len(references) * len(queries)` before scoring.** A sparse result
   container does not automatically avoid computing every requested pair.
7. **Report score settings and evidence.** Include tolerance, preprocessing,
   score name, number of matched peaks when available, and candidate metadata.
8. **Validate top hits visually and chemically.** Use mirror plots, precursor
   agreement, ion/adduct compatibility, and orthogonal evidence.

## Current API Guardrails

These points prevent the most common failures from pre-0.33 examples:

- Use `ModifiedCosineGreedy` or `ModifiedCosineHungarian`; `ModifiedCosine` was
  removed in 0.32.0.
- Do not call `add_losses()`. It was removed in 0.27.0; use
  `spectrum.losses`, `spectrum.compute_losses(...)`, or
  `NeutralLossesCosine` directly.
- `SpectrumProcessor` is not callable. Use `process_spectrum()` or
  `process_spectra()`.
- `process_spectra()` returns `(processed_spectra, processing_report)`.
- `Scores.scores` is a `StackedSparseArray`, often with separate structured
  fields such as `CosineGreedy_score` and `CosineGreedy_matches`.
- `scores_by_query()` returns `(reference_spectrum, score_record)` pairs, not
  reference indices.
- Prefer `spectra` in parameter names. The legacy spelling `spectrums` is
  deprecated.
- Never load pickle files from an untrusted source; unpickling can execute code.

See `references/migration.md` for a complete old-to-current mapping.

## Quick Start: Clean and Search a Library

```python
from matchms import SpectrumProcessor, calculate_scores
from matchms.filtering import (
    default_filters,
    normalize_intensities,
    require_minimum_number_of_peaks,
    select_by_relative_intensity,
)
from matchms.importing import load_spectra
from matchms.similarity import ModifiedCosineGreedy


def load_and_process(path):
    spectra = [default_filters(spectrum) for spectrum in load_spectra(path)]
    processor = SpectrumProcessor(
        [
            normalize_intensities,
            (select_by_relative_intensity, {"intensity_from": 0.01}),
            (require_minimum_number_of_peaks, {"n_required": 5}),
        ]
    )
    processed, _ = processor.process_spectra(
        spectra,
        progress_bar=False,
        create_report=False,
    )
    return processed


references = load_and_process("library.msp")
queries = load_and_process("queries.mgf")

metric = ModifiedCosineGreedy(tolerance=0.02)
scores = calculate_scores(
    references=references,
    queries=queries,
    similarity_function=metric,
)

score_name = "ModifiedCosineGreedy_score"
matches_name = "ModifiedCosineGreedy_matches"
for query in queries:
    ranked = scores.scores_by_query(query, name=score_name, sort=True)
    for reference, values in ranked[:5]:
        print(
            query.get("spectrum_id", query.get("id")),
            reference.get("compound_name", reference.get("spectrum_id")),
            float(values[score_name]),
            int(values[matches_name]),
        )
```

`SpectrumProcessor` automatically orders built-in filters according to matchms's
filter order. The aggregate `default_filters` callable is not in that registry,
so run it first as above or expand its nine component filters. Inspect
`processor.processing_steps` and preserve it with results.

## Pair Scoring

Similarity classes expose `pair()` for one reference/query pair. Cosine-family
results are structured NumPy scalars:

```python
from matchms.similarity import CosineGreedy

result = CosineGreedy(tolerance=0.02).pair(reference, query)
similarity = float(result["score"])
matched_peaks = int(result["matches"])
```

Use `calculate_scores()` for matrix-oriented methods such as
`FlashSimilarity`; its single-pair path is supported but intentionally not the
optimized path.

## Choose a Similarity Method

- `CosineGreedy` — standard peak cosine with greedy peak assignment.
- `CosineHungarian` — exact assignment; slower, useful for benchmarks.
- `CosineLinear` — current linear-scaling cosine implementation.
- `ModifiedCosineGreedy` — permits precursor-delta-shifted matches; common for
  analog search.
- `ModifiedCosineHungarian` — exact modified-cosine assignment.
- `NeutralLossesCosine` — compares losses computed from precursor and fragments.
- `BlinkCosine` — fast BLINK-style cosine approximation for larger matrices.
- `FlashSimilarity` — optimized matrix scoring using spectral entropy or cosine
  with fragment, neutral-loss, or hybrid matching.
- `BinnedEmbeddingSimilarity` — binned spectral vectors and optional approximate
  nearest-neighbor indexing.
- `PrecursorMzMatch`, `ParentMassMatch`, `MetadataMatch` — candidate masks or
  metadata constraints, not rich spectral scores.
- `FingerprintSimilarity` — molecular-structure similarity; it is not spectral
  similarity and requires fingerprints prepared from valid structures.

Read `references/similarity.md` before choosing a fast method, combining scores,
or interpreting structured outputs.

## Large Comparisons

For all-vs-all scoring of one collection, set `is_symmetric=True`:

```python
scores = calculate_scores(
    references=spectra,
    queries=spectra,
    similarity_function=CosineGreedy(tolerance=0.02),
    array_type="sparse",
    is_symmetric=True,
)
```

For a precursor-gated search, compute and filter `PrecursorMzMatch` first, then
calculate the spectral metric only on retained coordinates through `Pipeline`
or `Scores.calculate(...)`. See `references/workflows.md`.

Do not choose a universal "identification threshold." Score distributions
depend on preprocessing, mass accuracy, collision conditions, library quality,
and metric. At minimum, retain both score and matched-peak count for
cosine-family methods.

## Bundled Library-Search CLI

`scripts/library_search.py` provides a reproducible query-versus-library search
with current score extraction, pair-count limits, preprocessing, and CSV output:

```bash
uv run python scripts/library_search.py \
  queries.mgf library.msp hits.csv \
  --metric modified \
  --tolerance 0.02 \
  --top-k 10 \
  --min-score 0.6 \
  --min-matches 5
```

Run `--help` for fast metrics, preprocessing options, identifier fields,
overwrite control, and the explicit large-matrix override.

## Spectrum Objects and Visualization

```python
import numpy as np
from matchms import Spectrum

spectrum = Spectrum(
    mz=np.array([100.0, 150.0, 200.0]),
    intensities=np.array([0.2, 1.0, 0.4]),
    metadata={"spectrum_id": "query-1", "precursor_mz": 250.5},
)

print(spectrum.peaks.mz)
print(spectrum.get("precursor_mz"))
losses = spectrum.compute_losses(loss_mz_from=5.0, loss_mz_to=200.0)
spectrum.plot()
spectrum.plot_against(reference_spectrum)
```

## References

Read only the reference needed for the task:

- `references/importing_exporting.md` — formats, return types, generic I/O,
  mzSpecLib, score serialization, and pickle safety
- `references/filtering.md` — current filter catalog, clone/`None` semantics,
  default filters, ordering, and `SpectrumProcessor`
- `references/similarity.md` — all current similarity classes, outputs,
  candidate masking, performance, and interpretation
- `references/workflows.md` — library search, sparse gating, `Pipeline`, networks,
  plotting, and provenance
- `references/migration.md` — breaking changes and deprecated APIs
- `references/sources.md` — authoritative docs, release notes, user guides, and
  scientific publications used for this refresh

## Non-Negotiable Checks

- Never compare raw queries against differently processed references.
- Never use modified or neutral-loss scoring without valid precursor metadata.
- Never assume a `Scores` value is a plain float; inspect `score_names`.
- Never treat a high similarity score alone as confirmed identification.
- Never deserialize untrusted pickle data.
- Never launch an unbounded all-pairs comparison without estimating pair count.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/matchms/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/filtering.md`

# Filtering and Spectrum Processing (matchms 0.33.1)

Use this reference when building or debugging metadata-cleaning, peak-processing,
or quality-control pipelines. The authoritative API is the matchms
[`filtering` package](https://matchms.readthedocs.io/en/latest/api/matchms.filtering.html).

## Filter Contract

Most matchms filters:

- accept one `Spectrum` as the first argument;
- return a `Spectrum` or `None`;
- default to `clone=True`, so direct calls usually return a modified copy;
- use `None` to indicate that a `require_*` condition failed; and
- should be assigned back when called directly.

```python
spectrum = normalize_intensities(spectrum)
spectrum = require_minimum_number_of_peaks(spectrum, n_required=5)
if spectrum is None:
    # The spectrum failed a quality requirement.
    ...
```

Do not continue passing `None` through ordinary filters. `SpectrumProcessor`
stops the chain and discards rejected spectra for you.

## Prefer `SpectrumProcessor`

`SpectrumProcessor` accepts:

- a built-in filter name such as `"normalize_intensities"`;
- a callable such as `normalize_intensities`; or
- `(filter, parameter_dict)`, where `filter` can be a name or callable.

Built-in filters are automatically sorted into matchms's required filter order.
Custom filters are appended unless an explicit position is supplied with
`parse_and_add_filter()`.

```python
from matchms import SpectrumProcessor
from matchms.filtering import (
    default_filters,
    normalize_intensities,
    remove_peaks_relative_to_precursor_mz,
    require_minimum_number_of_peaks,
    require_precursor_mz,
    select_by_mz,
    select_by_relative_intensity,
)

# Run the aggregate metadata harmonizer before SpectrumProcessor. If included as
# one callable inside the processor, it is treated as custom and placed last.
spectra = [default_filters(spectrum) for spectrum in spectra]

processor = SpectrumProcessor(
    [
        (require_precursor_mz, {"minimum_accepted_mz": 50.0, "maximum_mz": 1500.0}),
        normalize_intensities,
        (remove_peaks_relative_to_precursor_mz, {"offset_to_precursor": -1.6}),
        (select_by_mz, {"mz_from": 20.0, "mz_to": 1500.0}),
        (select_by_relative_intensity, {"intensity_from": 0.01}),
        (require_minimum_number_of_peaks, {"n_required": 5}),
    ]
)

cleaned, report = processor.process_spectra(
    spectra,
    progress_bar=False,
    create_report=False,
)
print(processor.processing_steps)
```

Important current behavior:

- `SpectrumProcessor` is **not callable**.
- Use `processor.process_spectrum(spectrum)` for one spectrum.
- Use `processor.process_spectra(spectra)` for a list.
- `process_spectra()` returns `(processed_spectra, processing_report)`.
- With `create_report=False`, the processor clones each input once and disables
  per-filter cloning where supported.
- With `create_report=True`, filters are cloned step by step to measure changes.
  The aggregate `default_filters` function is not in the processor's built-in
  order registry and does not expose a `clone` parameter. If passed directly,
  it is placed after registered filters and detailed reporting logs a warning.
  Run it before the processor or expand it into the nine filters below.
- `process_spectrums()` is a deprecated spelling.

## What `default_filters()` Does

In 0.33.1, `default_filters()` applies exactly:

1. `make_charge_int`
2. `add_compound_name`
3. `derive_adduct_from_name`
4. `derive_formula_from_name`
5. `clean_compound_name`
6. `interpret_pepmass`
7. `add_precursor_mz`
8. `derive_ionmode`
9. `correct_charge`

It does **not** normalize peaks, add retention fields, harmonize structural
identifiers, require precursor metadata, or enforce peak-count quality. Add
those steps explicitly.

## Peak Processing

### Normalize and select peaks

- `normalize_intensities(spectrum_in, clone=True, scaling=None)` — normalize to
  maximum intensity 1 by default; pass `scaling=(low, high)` for min-max scaling.
- `select_by_intensity(spectrum_in, intensity_from=10.0, intensity_to=200.0,
  clone=True)` — keep an absolute intensity interval.
- `select_by_relative_intensity(spectrum_in, intensity_from=0.0,
  intensity_to=1.0, clone=True)` — keep a fraction-of-maximum interval.
- `select_by_mz(spectrum_in, mz_from=0.0, mz_to=1000.0, clone=True)` — crop the
  fragment m/z interval.

Normalize before using relative-intensity thresholds.

### Reduce and clean peaks

- `reduce_to_number_of_peaks(spectrum_in, n_required=0, n_max=inf,
  ratio_desired=None, clone=True)` — keep the most intense peaks within count
  constraints.
- `remove_noise_below_frequent_intensities(spectrum_in,
  min_count_of_frequent_intensities=5, noise_level_multiplier=2.0, clone=True)`
  — estimate and remove repeated low-intensity noise.
- `remove_peaks_around_precursor_mz(spectrum_in, mz_tolerance=17, clone=True)`
  — remove peaks within a precursor-centered exclusion window.
- `remove_peaks_relative_to_precursor_mz(spectrum_in,
  offset_to_precursor=-1.6, clone=True)` — remove peaks above a cutoff relative
  to precursor m/z.
- `remove_peaks_outside_top_k(spectrum_in, k=6, mz_window=50, clone=True)` —
  retain peaks that lie near one of the `k` most intense local peaks.
- `remove_profiled_spectra(spectrum_in, mz_window=0.5, clone=True)` — reject
  spectra likely to contain profile-mode rather than centroided data.

These defaults are starting points, not instrument-independent truth. Record
chosen windows and thresholds.

### Peak quality requirements

- `require_minimum_number_of_peaks(spectrum_in, n_required=10,
  ratio_required=None, clone=True)`
- `require_maximum_number_of_peaks(spectrum_in,
  maximum_number_of_fragments=1000, clone=True)`
- `require_minimum_number_of_high_peaks(spectrum_in, no_peaks=5,
  intensity_percent=2.0, clone=True)`

Older examples commonly use invalid
`require_minimum_number_of_high_peaks(n_required=..., intensity_threshold=...)`
arguments. In 0.33.1 the names are `no_peaks` and `intensity_percent`, where the
latter is a percentage rather than a 0-1 fraction.

## Precursor, Adduct, Charge, and Ion Mode

- `interpret_pepmass(spectrum_in, clone=True)`
- `add_precursor_mz(spectrum_in, clone=True)`
- `add_parent_mass(spectrum_in, estimate_from_adduct=True,
  overwrite_existing_entry=False, estimate_from_charge=True, clone=True)`
- `add_precursor_formula(spectrum_in, clone=True)`
- `make_charge_int(spectrum_in, clone=True)`
- `correct_charge(spectrum_in, clone=True)`
- `clean_adduct(spectrum_in, clone=True)`
- `derive_adduct_from_name(spectrum_in, remove_adduct_from_name=True,
  clone=True)`
- `derive_ionmode(spectrum_in, clone=True)`
- `require_correct_ionmode(spectrum_in, ion_mode_to_keep)`
- `require_matching_adduct_and_ionmode(spectrum)`
- `require_matching_adduct_precursor_mz_parent_mass(spectrum, tolerance=0.1)`
- `require_precursor_mz(spectrum_in, minimum_accepted_mz=10.0,
  maximum_mz=None, clone=True)`

`require_precursor_below_mz()` is deprecated. Use
`require_precursor_mz(maximum_mz=...)`.

Modified-cosine and neutral-loss scoring require a valid `precursor_mz`.
Parent-mass matching additionally requires a valid `parent_mass`.

## Compound Names, Formulae, and Structures

### Name and formula processing

- `add_compound_name(spectrum_in, clone=True)`
- `clean_compound_name(spectrum_in, clone=True)`
- `derive_formula_from_name(spectrum_in, remove_formula_from_name=True,
  clone=True)`
- `derive_formula_from_smiles(spectrum_in, overwrite=True, clone=True)`
- `require_compound_name(spectrum)`
- `require_formula(spectrum)`

### SMILES, InChI, and InChIKey

- `derive_inchi_from_smiles(spectrum_in, clone=True)`
- `derive_inchikey_from_inchi(spectrum_in, clone=True)`
- `derive_smiles_from_inchi(spectrum_in, clone=True)`
- `harmonize_undefined_inchi(...)`
- `harmonize_undefined_inchikey(...)`
- `harmonize_undefined_smiles(...)`
- `repair_inchi_inchikey_smiles(spectrum_in, clone=True)`
- `repair_not_matching_annotation(spectrum_in, clone=True)`
- `require_valid_annotation(spectrum)`

`derive_annotation_from_compound_name()` can query PubChem. It introduces
network dependence, name ambiguity, and external-service variability; cache or
export the resulting annotations and retain provenance.

### Structure/mass repair

Current repair helpers include:

- `repair_adduct_and_parent_mass_based_on_smiles`
- `repair_adduct_based_on_parent_mass`
- `repair_parent_mass_from_smiles`
- `repair_parent_mass_is_molar_mass`
- `repair_parent_mass_match_smiles_wrapper`
- `repair_smiles_of_salts`
- `require_parent_mass_match_smiles`

Several require an explicit `mass_tolerance`. Do not silently "repair" library
annotations without preserving original fields and logging the rule used.

## Retention and MS-Level Metadata

- `add_retention_time(spectrum_in, clone=True)`
- `add_retention_index(spectrum_in, clone=True)`
- `require_retention_time(spectrum_in, minimum_rt=None, maximum_rt=None,
  clone=True)`
- `require_retention_index(spectrum_in, clone=True)`
- `require_correct_ms_level(spectrum, required_ms_level=2)`

Retention time and retention index are not interchangeable. Record units and
the chromatographic method before using either as a matching constraint.

## Fingerprints

`add_fingerprint()` still works in 0.33.1, but it is marked for removal in
matchms 1.0. Prefer the top-level `Fingerprints` class:

```python
from matchms import Fingerprints

fingerprints = Fingerprints(
    fingerprint_algorithm="morgan2",
    fingerprint_method="bit",
    nbits=2048,
)
fingerprints.compute_fingerprints(spectra)
```

`Fingerprints` maps valid InChIKeys to fingerprints and needs a valid InChIKey
plus SMILES or InChI. In 0.33.1, `FingerprintSimilarity` still reads a
`"fingerprint"` field from each spectrum, so bridge deliberately when that
legacy similarity class is needed:

```python
for spectrum in spectra:
    fingerprint = fingerprints.get_fingerprint_by_spectrum(spectrum)
    if fingerprint is not None:
        spectrum.set("fingerprint", fingerprint)
```

Do not describe fingerprint similarity as spectral similarity.

## Custom Filters

A custom filter should accept a spectrum first and return a spectrum or `None`:

```python
def require_fragment(spectrum_in, fragment_mz, tolerance=0.02):
    if spectrum_in is None:
        return None
    if any(abs(mz - fragment_mz) <= tolerance for mz in spectrum_in.peaks.mz):
        return spectrum_in
    return None


processor.parse_and_add_filter(
    (require_fragment, {"fragment_mz": 184.0733, "tolerance": 0.01})
)
```

Avoid mutation unless it is intentional and documented. If the custom filter
modifies a spectrum, either implement a `clone` parameter consistently or clone
inside the function.

## Reproducibility Checklist

- Save `processor.processing_steps`.
- Record matchms and Python versions.
- Record whether metadata harmonization was enabled at import.
- Apply identical peak filters to query and reference collections.
- Preserve counts before and after every requirement filter.
- Preserve original metadata before repair/enrichment.
- Record network calls and external annotation sources.
- Test a few spectra with expected pass/fail behavior before batch processing.

### `references/importing_exporting.md`

# Importing and Exporting (matchms 0.33.1)

Use this reference for file-format selection, return types, streaming behavior,
and safe serialization. The authoritative APIs are the matchms
[`importing`](https://matchms.readthedocs.io/en/latest/api/matchms.importing.html)
and
[`exporting`](https://matchms.readthedocs.io/en/latest/api/matchms.exporting.html)
packages.

## Recommended Entry Points

Use extension-based helpers for ordinary local files:

```python
from matchms.importing import load_spectra
from matchms.exporting import save_spectra

spectra = list(load_spectra("library.msp"))
save_spectra(spectra, "cleaned.mgf")
```

`load_spectra()` supports mzML, mzXML, MGF, MSP, JSON, and `.pickle`.
`save_spectra()` supports MGF, MSP, JSON, and `.pickle` in 0.33.1. Use
format-specific functions when you need an MS level, file-like MGF input,
mzSpecLib output, or precise writer options.

`save_spectra()` refuses to overwrite an existing output unless
`append=True`, and append mode is restricted to MGF and MSP. This makes it
safer than direct writers, whose MGF/MSP defaults are append mode.

## Import Matrix

### MGF

```python
from matchms.importing import load_from_mgf

spectra = list(load_from_mgf("queries.mgf"))
```

Signature:

```text
load_from_mgf(filename: str | Path | TextIO,
              metadata_harmonization: bool = True) -> Generator[Spectrum]
```

MGF is a practical interchange format for centroided MS/MS spectra and supports
streaming iteration. It can also read an already-open text handle:

```python
with open("queries.mgf", encoding="utf-8") as handle:
    spectra = list(load_from_mgf(handle))
```

### MSP

```python
from matchms.importing import load_from_msp

library = list(load_from_msp("library.msp"))
```

Signature:

```text
load_from_msp(filename: str,
              metadata_harmonization: bool = True) -> Generator[Spectrum]
```

MSP is common for reference libraries. Matchms 0.29+ includes support for
GOLM-style MSP data, but source metadata still varies substantially by library.

### mzML and mzXML

```python
from matchms.importing import load_from_mzml, load_from_mzxml

ms2 = list(load_from_mzml("sample.mzML", ms_level=2))
ms1 = list(load_from_mzxml("legacy.mzXML", ms_level=1))
```

Signatures:

```text
load_from_mzml(filename: str | Path, ms_level: int = 2,
               metadata_harmonization: bool = True) -> Generator[Spectrum]
load_from_mzxml(filename: str | Path, ms_level: int = 2,
                metadata_harmonization: bool = True) -> Generator[Spectrum]
```

These readers select one MS level. For chromatograms, binary arrays beyond the
Spectrum abstraction, vendor-specific metadata, or more complex raw-data
parsing, use pyteomics, pymzML, or pyopenms.

### JSON

```python
from matchms.importing import load_from_json

spectra = load_from_json("spectra.json")
```

Signature:

```text
load_from_json(filename: str,
               metadata_harmonization: bool = True) -> list[Spectrum]
```

The JSON reader returns a list, not a generator. It supports matchms JSON and
GNPS-style spectral-library JSON and skips spectra with zero peaks.

### Metabolomics USI

```python
from matchms.importing import load_from_usi

spectrum = load_from_usi(
    "mzspec:GNPS:GNPS-LIBRARY:accession:CCMSLIB00000424840"
)
```

Signature:

```text
load_from_usi(
    usi: str,
    server: str = "https://metabolomics-usi.gnps2.org",
    metadata_harmonization: bool = True,
)
```

USI loading makes an external network request. Preserve the USI, resolver URL,
retrieval date, and retrieved metadata with analysis outputs. Handle service
failures and `None`/invalid responses rather than assuming availability.

### Pickle

```python
from matchms.importing import load_from_pickle

spectra = load_from_pickle("trusted-cache.pickle", metadata_harmonization=True)
```

The `metadata_harmonization` argument is required in 0.33.1.

**Security:** Python pickle is executable serialization. Loading an untrusted
pickle can run arbitrary code. Use MGF, MSP, JSON, or mzSpecLib for exchanged or
downloaded data. Restrict pickle to trusted, local, reproducible caches.

## Generator and Memory Semantics

MGF, MSP, mzML, and mzXML readers yield generators. JSON and pickle readers
return lists. Converting a generator with `list(...)` loads all spectra and peak
arrays into memory.

Pairwise scoring requires materialized collections. Before scoring, estimate:

```python
pair_count = len(references) * len(queries)
```

For preprocessing-only MGF/MSP workflows, stream one spectrum at a time:

```python
from pathlib import Path

from matchms.exporting import save_spectra
from matchms.filtering import default_filters, normalize_intensities
from matchms.importing import load_from_mgf

output = Path("cleaned.mgf")
if output.exists():
    raise FileExistsError(output)

first_write = True
for spectrum in load_from_mgf("large.mgf"):
    spectrum = default_filters(spectrum)
    spectrum = normalize_intensities(spectrum)
    if spectrum is None:
        continue
    save_spectra([spectrum], str(output), append=not first_write)
    first_write = False
```

For many spectra, writing larger batches is usually faster than one record per
call.

## Metadata Harmonization

The importers default to `metadata_harmonization=True`. This normalizes source
keys to matchms conventions while constructing each `Spectrum`.

Keep harmonization enabled for cross-source comparisons. Disable it only when:

- exact source keys must be preserved;
- you have a documented custom normalization layer; or
- you are investigating an importer/harmonization issue.

When source fidelity matters, retain the original file and export a metadata
audit before applying repair filters.

## Export Matrix

### Generic writer

```python
from matchms.exporting import save_spectra

save_spectra(spectra, "output.mgf", export_style="matchms")
save_spectra(spectra, "output.msp", export_style="nist")
save_spectra(spectra, "output.json", export_style="gnps")
```

Signature:

```text
save_spectra(spectra, file: str,
             export_style: str = "matchms",
             append: bool = False) -> None
```

Supported export styles are `matchms`, `massbank`, `nist`, `riken`, and `gnps`.
Not every source metadata field has a lossless representation in every target
format. Reopen converted data and compare identifiers, precursor values, peak
counts, and representative peaks.

### Direct MGF writer

```text
save_as_mgf(spectra, filename, export_style="matchms", file_mode="a")
```

The direct writer's default is append mode. Pass `file_mode="w"` when creating a
fresh output, or prefer `save_spectra()` for overwrite protection.

### Direct MSP writer

```text
save_as_msp(spectra, filename, write_peak_comments=True,
            mode="a", style="matchms", peak_sep="\t")
```

The direct writer also defaults to append mode. Peak comments can be retained
when supported by the input and output style.

### JSON writer

```text
save_as_json(spectra, filename, export_style="matchms")
```

JSON is portable and preserves matchms-oriented structured metadata better than
plain text library formats, but it is not a raw-data archive.

### mzSpecLib writer

```python
from matchms.exporting import save_as_mzspeclib

save_as_mzspeclib(spectra, "library.mzspeclib.txt")
```

`save_as_mzspeclib()` exports a list of spectra through psims. Validate the
result with the downstream mzSpecLib consumer because metadata requirements can
be stricter than MGF/MSP.

### Pickled spectra

The generic writer recognizes a `.pickle` extension:

```python
save_spectra(spectra, "trusted-cache.pickle")
```

Use the full `.pickle` suffix; `.pkl` is not recognized by `save_spectra()` in
0.33.1. Pickle is Python-specific, version-sensitive, and unsafe for untrusted
inputs.

## Score Serialization

A `Scores` object has dedicated serializers:

```python
scores.to_json("scores.json")
scores.to_pickle("scores.pickle")
```

Prefer JSON for exchange. Pickled `Scores` objects have the same arbitrary-code
execution risk as pickled spectra.

Load score JSON using matchms's score loader rather than manually reconstructing
the sparse stack. Confirm exact loader names with the installed version because
the importing package exposes both current and compatibility aliases.

## Conversion Pattern

```python
from matchms.exporting import save_spectra
from matchms.importing import load_from_mzml

spectra = list(load_from_mzml("sample.mzML", ms_level=2))
save_spectra(spectra, "sample-ms2.mgf")

roundtrip = list(load_spectra("sample-ms2.mgf"))
assert len(roundtrip) == len(spectra)
for before, after in zip(spectra[:10], roundtrip[:10], strict=True):
    assert len(before.peaks) == len(after.peaks)
```

Do not assume conversion preserves all acquisition metadata. MGF and MSP are
spectral interchange/library formats, not lossless replacements for mzML.

## Output Validation Checklist

- Reopen the output with matchms or the intended downstream consumer.
- Compare spectrum count and non-empty peak count.
- Compare precursor m/z, charge, ion mode, and identifiers.
- Compare m/z and intensity arrays for representative records.
- Confirm the chosen export style and append/overwrite mode.
- Preserve the original source alongside converted data.
- Never load exchanged pickle data.

### `references/migration.md`

# Migration to matchms 0.33.1

Use this guide when adapting code written for older matchms releases or the
official tutorial notebooks last revised in 2024.

## Release Timeline That Affects This Skill

### 0.27.0 (2024-07-10)

- `add_losses()` was removed.
- Neutral losses moved to on-demand computation through `spectrum.losses` and
  `spectrum.compute_losses(...)`.
- public names and parameters began changing from `spectrums` to `spectra`;
  compatibility spellings were deprecated.
- Python support moved to 3.9-3.12 at that release.

### 0.29.x-0.30.x (2025)

- importers gained broader `pathlib.Path`/MGF file-like support and writer
  behavior was revised.
- NumPy 2 became the supported baseline.
- Python 3.13 support was added.

### 0.31.0 (2025-10-06)

- `FlashSimilarity` and `BlinkCosine` were added.
- `normalize_intensities(..., scaling=(low, high))` gained min-max scaling.
- `add_precursor_formula` and
  `remove_peaks_relative_to_precursor_mz` were added.

### 0.32.0 (2026-03-04)

- `ModifiedCosine` was renamed to `ModifiedCosineGreedy`.
- `ModifiedCosineHungarian` was added for exact assignment.

### 0.33.0-0.33.1 (2026-05-12 to 2026-06-08)

- `CosineLinear` was added.
- v1 cleanup/deprecation work began, including migration away from
  `add_fingerprint()`.
- Python 3.14 support was added.

## Required Code Changes

### Modified cosine class

Old:

```python
from matchms.similarity import ModifiedCosine

metric = ModifiedCosine(tolerance=0.02)
```

Current greedy behavior:

```python
from matchms.similarity import ModifiedCosineGreedy

metric = ModifiedCosineGreedy(tolerance=0.02)
```

Current exact assignment:

```python
from matchms.similarity import ModifiedCosineHungarian

metric = ModifiedCosineHungarian(tolerance=0.02)
```

Update score field names too:

```text
ModifiedCosine_score   -> ModifiedCosineGreedy_score
ModifiedCosine_matches -> ModifiedCosineGreedy_matches
```

### Neutral losses

Old:

```python
from matchms.filtering import add_losses

spectrum = add_losses(spectrum)
```

Current:

```python
losses = spectrum.losses
custom_losses = spectrum.compute_losses(
    loss_mz_from=5.0,
    loss_mz_to=200.0,
)
```

`NeutralLossesCosine` computes the needed losses directly; do not pre-add them.

### `SpectrumProcessor`

Old:

```python
processor = SpectrumProcessor(
    [
        normalize_intensities,
        lambda spectrum: select_by_relative_intensity(
            spectrum,
            intensity_from=0.01,
        ),
    ]
)
processed = [processor(spectrum) for spectrum in spectra]
```

Current:

```python
processor = SpectrumProcessor(
    [
        normalize_intensities,
        (select_by_relative_intensity, {"intensity_from": 0.01}),
    ]
)
processed, report = processor.process_spectra(
    spectra,
    progress_bar=False,
    create_report=False,
)
```

For one spectrum, call `processor.process_spectrum(spectrum)`.

The aggregate `default_filters` callable is not registered in
`SpectrumProcessor`'s built-in filter order. Run it before the processor or
expand its nine component filters; otherwise it is treated as custom and moved
after registered filters.

### Score access

Old assumptions:

```python
reference_index, score = scores.scores_by_query(query, sort=True)[0]
reference = references[reference_index]
numeric = scores.scores[j, i]
```

Current:

```python
score_name = "CosineGreedy_score"
reference, value = scores.scores_by_query(
    query,
    name=score_name,
    sort=True,
)[0]

numeric = float(value[score_name])
matches = int(value["CosineGreedy_matches"])
matrix = scores.to_array(score_name)
```

`Scores.scores` is a layered sparse container. Always inspect
`scores.score_names`.

### Metadata matching

Old:

```python
MetadataMatch(field="ionmode", matching_type="exact")
```

Current:

```python
MetadataMatch(field="ionmode", matching_type="equal_match")
```

Current matching types are `equal_match` and `difference`.

### High-peak requirement

Old:

```python
require_minimum_number_of_high_peaks(
    spectrum,
    n_required=5,
    intensity_threshold=0.05,
)
```

Current:

```python
require_minimum_number_of_high_peaks(
    spectrum,
    no_peaks=5,
    intensity_percent=5.0,
)
```

`intensity_percent` is expressed as a percentage.

### Top-k peak filter

Old examples may use a `ratio_desired` argument. Current:

```python
remove_peaks_outside_top_k(
    spectrum,
    k=6,
    mz_window=50,
)
```

For global peak-count reduction, use
`reduce_to_number_of_peaks(n_required=..., n_max=..., ratio_desired=...)`.

### Precursor upper bound

Old:

```python
require_precursor_below_mz(spectrum, maximum_accepted_mz=1000)
```

Current:

```python
require_precursor_mz(
    spectrum,
    minimum_accepted_mz=10.0,
    maximum_mz=1000.0,
)
```

`require_precursor_below_mz()` is deprecated.

### Parent-mass repair names

Older examples may refer to:

```text
repair_parent_mass_is_mol_wt
repair_adduct_based_on_smiles
```

Current public helpers include:

```text
repair_parent_mass_is_molar_mass
repair_adduct_and_parent_mass_based_on_smiles
repair_adduct_based_on_parent_mass
repair_parent_mass_from_smiles
```

Review semantics and supply required `mass_tolerance` arguments rather than
performing a mechanical rename.

### Fingerprints

Old:

```python
spectra = [add_fingerprint(spectrum, fingerprint_type="morgan2")
           for spectrum in spectra]
```

`add_fingerprint()` still works in 0.33.1 but is marked for removal in matchms
1.0. Forward-oriented preparation:

```python
from matchms import Fingerprints

fp_store = Fingerprints(
    fingerprint_algorithm="morgan2",
    fingerprint_method="bit",
    nbits=2048,
)
fp_store.compute_fingerprints(spectra)
```

Current `FingerprintSimilarity` still reads a `"fingerprint"` spectrum field.
When that class is needed in 0.33.1, bridge the store explicitly:

```python
for spectrum in spectra:
    fingerprint = fp_store.get_fingerprint_by_spectrum(spectrum)
    if fingerprint is not None:
        spectrum.set("fingerprint", fingerprint)
```

### Installation

Old:

```bash
uv pip install matchms[chemistry]
```

Current:

```bash
uv pip install "matchms==0.33.1"
```

The 0.33.1 package metadata has no `chemistry` extra and includes RDKit as a
regular dependency.

### Spectrum serialization

Old:

```python
from matchms.exporting import save_as_pickle

save_as_pickle(spectra, "spectra.pkl")
```

Current public pattern:

```python
from matchms.exporting import save_spectra

save_spectra(spectra, "trusted-cache.pickle")
```

`save_as_pickle` is not exported in 0.33.1. The generic writer recognizes
`.pickle`, not `.pkl`. Prefer portable MGF/MSP/JSON for exchanged data, and
never load untrusted pickle.

### Generic I/O and overwrite behavior

Prefer:

```python
from matchms.exporting import save_spectra
from matchms.importing import load_spectra

spectra = list(load_spectra("input.mgf"))
save_spectra(spectra, "output.msp")
```

`save_spectra()` refuses an existing output unless appending MGF/MSP data.
Direct `save_as_mgf()` and `save_as_msp()` default to append mode, so specify
write mode explicitly when bypassing the generic writer.

## Deprecated Compatibility Names

Replace these even if 0.33.1 still accepts some of them:

```text
spectrums             -> spectra
process_spectrums()   -> process_spectra()
import_spectrums()    -> import_spectra()
spectrums_queries     -> spectra_queries
spectrums_references  -> spectra_references
```

Do not suppress deprecation warnings globally; they are migration signals for
the forthcoming 1.0 API.

## Tutorial Caveat

The separate `matchms-docs` user-guide repository was last revised on
2024-06-13. Its pipeline/filtering explanations remain useful, but the tutorial
still contains examples using `ModifiedCosine` and older spelling. Prefer the
current Read the Docs API and release notes for symbol names and signatures.

## Migration Verification

After migration:

1. print `matchms.__version__` and confirm 0.33.1;
2. run imports with deprecation warnings visible;
3. inspect `processor.processing_steps`;
4. compare spectrum counts before/after processing;
5. print `scores.score_names`;
6. test one known spectrum pair and one query/library search;
7. compare old and new result rankings on a representative subset;
8. verify serialized outputs by reopening them; and
9. document any score changes caused by algorithm renaming, filtering, or
   dependency updates.

### `references/similarity.md`

# Similarity and Scores (matchms 0.33.1)

Use this reference to select a similarity class, interpret its output, extract
top hits, or scale a comparison. The authoritative API is
[`matchms.similarity`](https://matchms.readthedocs.io/en/latest/api/matchms.similarity.html).

## Core Calculation

```python
from matchms import calculate_scores
from matchms.similarity import CosineGreedy

metric = CosineGreedy(tolerance=0.02)
scores = calculate_scores(
    references=reference_spectra,
    queries=query_spectra,
    similarity_function=metric,
    array_type="numpy",
    is_symmetric=False,
)
```

Set `is_symmetric=True` only when references and queries are the same collection
in the same order and the metric is symmetric.

## Understand the Output Before Indexing

`Scores.scores` is a `sparsestack.StackedSparseArray`, not a plain two-dimensional
NumPy array. Its shape is `(n_references, n_queries, n_score_fields)`.

Cosine-family methods produce two fields:

```python
print(scores.score_names)
# ('CosineGreedy_score', 'CosineGreedy_matches')

similarities = scores.to_array("CosineGreedy_score")
matched_peaks = scores.to_array("CosineGreedy_matches")
```

Scalar methods such as `FlashSimilarity`, `PrecursorMzMatch`, and
`FingerprintSimilarity` produce one field named after the class.

### Top hits for one query

```python
score_name = "CosineGreedy_score"
matches_name = "CosineGreedy_matches"

ranked = scores.scores_by_query(query_spectrum, name=score_name, sort=True)
for reference, value in ranked[:10]:
    print(
        reference.get("spectrum_id"),
        float(value[score_name]),
        int(value[matches_name]),
    )
```

The first tuple item is the actual reference `Spectrum`, not an integer index.
The second item can be a structured NumPy record containing every score field.

### Iterate stored pairs

```python
for reference, query, values in scores:
    print(reference.get("id"), query.get("id"), values)
```

Iteration covers stored coordinates. After sparse filtering, that may be only a
subset of the Cartesian product.

## Peak-Based Cosine Methods

All cosine classes below use:

```text
tolerance=0.1, mz_power=0.0, intensity_power=1.0
```

unless noted otherwise. Tolerance is in daltons for these classes.

### `CosineGreedy`

Greedily assigns candidate peak pairs within tolerance.

Use for:

- routine spectral-library comparisons;
- a transparent baseline;
- moderate collections where exact assignment is not essential.

Output fields: `CosineGreedy_score`, `CosineGreedy_matches`.

### `CosineHungarian`

Uses optimal assignment rather than greedy assignment.

Use for:

- benchmarking peak-assignment effects;
- smaller datasets;
- cases where greedy ambiguity materially affects results.

It is computationally more expensive than `CosineGreedy`.

### `CosineLinear`

Added in 0.33.0 as a linear-scaling cosine implementation.

Use when:

- cosine is the intended metric;
- matrix size makes assignment cost important; and
- you have benchmarked agreement and runtime on representative spectra.

Output fields: `CosineLinear_score`, `CosineLinear_matches`.

## Modified Cosine

Modified cosine allows unshifted peak matches and matches shifted by the
difference in precursor m/z. Both spectra need valid `precursor_mz`.

### `ModifiedCosineGreedy`

```python
from matchms.similarity import ModifiedCosineGreedy

metric = ModifiedCosineGreedy(tolerance=0.02)
```

This is the current name for the implementation formerly called
`ModifiedCosine`. It uses greedy assignment.

### `ModifiedCosineHungarian`

```python
from matchms.similarity import ModifiedCosineHungarian

metric = ModifiedCosineHungarian(tolerance=0.02)
```

Use for exact modified-cosine assignment in benchmarks or method development.
It is slower than the greedy variant.

Do not infer that a shifted match proves a specific chemical transformation.
Inspect precursor delta, adduct/charge compatibility, shifted peaks, and
orthogonal annotations.

## Neutral-Loss Cosine

```python
from matchms.similarity import NeutralLossesCosine

metric = NeutralLossesCosine(
    tolerance=0.02,
    ignore_peaks_above_precursor=True,
)
```

`NeutralLossesCosine` computes losses from `precursor_mz - fragment_mz`.
Both spectra require precursor m/z. Do not call the removed `add_losses()`
filter; losses are computed on demand in current matchms.

Output fields: `NeutralLossesCosine_score`,
`NeutralLossesCosine_matches`.

## Fast Matrix-Oriented Methods

### `BlinkCosine`

BLINK-style approximate cosine:

```python
from matchms.similarity import BlinkCosine

metric = BlinkCosine(
    tolerance=0.01,
    bin_width=0.001,
    min_relative_intensity=0.01,
    top_k=None,
    batch_size=1024,
    sparse_score_min=0.0,
)
```

Important parameters include peak preprocessing, precursor cropping, batch
size, and sparse score minimum. Output contains a float32 score and matched-peak
count. Validate approximation behavior against `CosineGreedy` on a subset
before changing production workflows.

### `FlashSimilarity`

Fast matrix scoring based on the Flash Entropy approach:

```python
from matchms.similarity import FlashSimilarity

entropy = FlashSimilarity(
    score_type="spectral_entropy",
    matching_mode="fragment",
    tolerance=0.02,
)

fast_modified_cosine = FlashSimilarity(
    score_type="cosine",
    matching_mode="hybrid",
    tolerance=0.02,
)
```

Current choices:

- `score_type`: `spectral_entropy` or `cosine`
- `matching_mode`: `fragment`, `neutral_loss`, or `hybrid`
- optional preprocessing: precursor removal, noise cutoff, peak merging, dtype,
  and identity precursor tolerance

`pair()` exists but emits a warning because it is not the optimized use. Call
`calculate_scores()` so matchms uses the matrix path. Flash output is a scalar
field named `FlashSimilarity`, not a score/matches pair.

### `BinnedEmbeddingSimilarity`

```python
from matchms.similarity import BinnedEmbeddingSimilarity

metric = BinnedEmbeddingSimilarity(
    similarity="cosine",
    max_mz=1005,
    bin_width=1.0,
    intensity_power=1.0,
)
```

This creates fixed-width binned spectral embeddings. Bin width controls both
resolution and dimensionality. The class also supports approximate-neighbor
indexing through the current PyNNDescent backend; use it only after checking
recall against exact neighbors.

## Candidate and Metadata Matches

These methods are useful as gates or additional evidence. They are not
substitutes for peak-pattern similarity.

### `PrecursorMzMatch`

```python
from matchms.similarity import PrecursorMzMatch

absolute = PrecursorMzMatch(tolerance=0.02, tolerance_type="Dalton")
relative = PrecursorMzMatch(tolerance=10, tolerance_type="ppm")
```

Output field: `PrecursorMzMatch` (boolean).

### `ParentMassMatch`

```python
from matchms.similarity import ParentMassMatch

metric = ParentMassMatch(tolerance=0.02)
```

Requires `parent_mass`. Output field: `ParentMassMatch` (boolean). The current
constructor does not expose a ppm mode.

### `MetadataMatch`

```python
from matchms.similarity import MetadataMatch

same_mode = MetadataMatch(field="ionmode", matching_type="equal_match")
near_rt = MetadataMatch(
    field="retention_time",
    matching_type="difference",
    tolerance=0.2,
)
```

Current matching types are `equal_match` and `difference`. Older examples that
use `matching_type="exact"` are invalid.

### `IntersectMz`

`IntersectMz(scaling=1.0)` is a simple m/z-intersection score useful in tests or
specialized workflows. It is not a drop-in replacement for tolerance-aware,
intensity-weighted spectral scoring.

## Molecular Fingerprint Similarity

`FingerprintSimilarity` compares molecular fingerprints derived from known
structures. It therefore measures structure similarity, not spectral
similarity.

```python
from matchms import Fingerprints, calculate_scores
from matchms.similarity import FingerprintSimilarity

fp_store = Fingerprints(
    fingerprint_algorithm="morgan2",
    fingerprint_method="bit",
    nbits=2048,
)
fp_store.compute_fingerprints(spectra)

usable = []
for spectrum in spectra:
    fingerprint = fp_store.get_fingerprint_by_spectrum(spectrum)
    if fingerprint is not None:
        spectrum.set("fingerprint", fingerprint)
        usable.append(spectrum)

scores = calculate_scores(
    usable,
    usable,
    FingerprintSimilarity(similarity_measure="jaccard"),
    is_symmetric=True,
)
```

Similarity measures are `jaccard`, `dice`, and `cosine`.

The old `add_fingerprint()` filter still satisfies the 0.33.1
`FingerprintSimilarity` interface, but it is marked for removal in matchms 1.0.
The `Fingerprints` bridge above avoids calling that deprecated filter while
remaining compatible with the current similarity class.

## Efficient Precursor-Gated Search

Filter score coordinates before calculating an expensive spectral metric:

```python
from matchms import calculate_scores
from matchms.similarity import ModifiedCosineGreedy, PrecursorMzMatch

scores = calculate_scores(
    references,
    queries,
    PrecursorMzMatch(tolerance=10, tolerance_type="ppm"),
    array_type="sparse",
)
scores.filter_by_range(name="PrecursorMzMatch", low=0.5)
scores.calculate(
    ModifiedCosineGreedy(tolerance=0.02),
    array_type="sparse",
    join_type="left",
)
```

After `filter_by_range`, the second calculation can operate on retained
coordinates. Confirm `scores.score_names` and stored-coordinate counts after
each stage. An overly narrow precursor gate can remove valid analogs or
different adducts.

The `Pipeline` class formalizes the same pattern and can persist a YAML
workflow. See `workflows.md`.

## Filtering and Exporting Scores

```python
print(scores.score_names)

scores.filter_by_range(
    name="ModifiedCosineGreedy_score",
    low=0.6,
    above_operator=">=",
)

dense = scores.to_array("ModifiedCosineGreedy_score")
coo = scores.to_coo("ModifiedCosineGreedy_score")
scores.to_json("scores.json")
```

`filter_by_range()` mutates the stored score coordinates. Preserve an unfiltered
copy or serialize first when alternative thresholds must be compared.

Dense arrays require memory proportional to
`n_references * n_queries`. A sparse container is most useful only when a mask
or score threshold leaves relatively few stored pairs.

## Combining Metrics

Do not directly index `scores.scores[j, i]` and assume a scalar. Extract named
layers:

```python
cosine = scores.to_array("CosineGreedy_score")
matches = scores.to_array("CosineGreedy_matches")
```

If combining metrics:

- define whether missing/filtered pairs are zero, missing, or excluded;
- normalize only when score semantics justify it;
- fit or justify weights on an appropriate validation set;
- avoid leaking query identities into tuning;
- retain each component score in the output; and
- report the exact formula and package version.

## Interpretation Checklist

- Was identical preprocessing applied to references and queries?
- Is the tolerance appropriate for the instrument and calibration?
- Are precursor m/z, charge, ion mode, and adduct metadata valid?
- How many peaks matched, and what fraction of each spectrum do they represent?
- Is the hit driven by one dominant/common fragment?
- Are collision energy and acquisition conditions comparable?
- Is the query actually present in the searched library?
- Was the threshold validated on representative positives and negatives?
- Has the top hit been inspected with a mirror plot?

A high score ranks a candidate under a chosen metric. It does not, by itself,
establish compound identity.

### `references/sources.md`

# Sources and Verification Record

This skill was refreshed on **2026-07-23** against matchms **0.33.1**.

## Version and Packaging

- [matchms on PyPI](https://pypi.org/project/matchms/) — 0.33.1, released
  2026-06-08; Python `>=3.10,<3.15`; release history and package metadata.
- [matchms 0.33.1 release](https://github.com/matchms/matchms/releases/tag/0.33.1)
  — Python 3.14 support and maintenance changes.
- [matchms repository](https://github.com/matchms/matchms) — source,
  `pyproject.toml`, tests, examples, and current README.
- [matchms releases](https://github.com/matchms/matchms/releases) — complete
  upstream release history.

The 0.33.1 wheel was installed in an isolated uv environment and its public
objects were inspected with `inspect.signature`. Runnable examples in this skill
were checked against that environment.

## Release Notes Used for Migration

- [0.27.0](https://github.com/matchms/matchms/releases/tag/0.27.0) — on-demand
  losses, removal of `add_losses`, and `spectrums` to `spectra` renaming.
- [0.30.0](https://github.com/matchms/matchms/releases/tag/0.30.0) — NumPy 2
  baseline and Python 3.13 support.
- [0.31.0](https://github.com/matchms/matchms/releases/tag/0.31.0) —
  `FlashSimilarity`, `BlinkCosine`, min-max intensity scaling, and new filters.
- [0.32.0](https://github.com/matchms/matchms/releases/tag/0.32.0) —
  `ModifiedCosineGreedy` rename and `ModifiedCosineHungarian`.
- [0.33.0](https://github.com/matchms/matchms/releases/tag/0.33.0) —
  `CosineLinear` and preparation for the future 1.0 API.
- [0.33.1](https://github.com/matchms/matchms/releases/tag/0.33.1) — current
  verified release.

## Current API Documentation

- [Documentation home](https://matchms.readthedocs.io/)
- [Core package, Pipeline, Spectrum, and Scores](https://matchms.readthedocs.io/en/latest/api/matchms.html)
- [Spectrum](https://matchms.readthedocs.io/en/latest/api/matchms.Spectrum.html)
- [Filtering](https://matchms.readthedocs.io/en/latest/api/matchms.filtering.html)
- [Importing](https://matchms.readthedocs.io/en/latest/api/matchms.importing.html)
- [Exporting](https://matchms.readthedocs.io/en/latest/api/matchms.exporting.html)
- [Similarity](https://matchms.readthedocs.io/en/latest/api/matchms.similarity.html)
- [Networking](https://matchms.readthedocs.io/en/latest/api/matchms.networking.html)

Read the Docs "latest" and the installed 0.33.1 source were treated as
authoritative for class names, signatures, return values, and deprecations.

## User Guides

- [matchms user documentation](https://matchms.github.io/matchms-docs/intro.html)
- [Filtering tutorial](https://matchms.github.io/matchms-docs/notebooks/matchms_filtering_tutorial.html)
- [Building an MS/MS analysis pipeline](https://matchms.github.io/matchms-docs/notebooks/matchms_tutorial_01_building_analysis_pipeline.html)
- [User-guide repository](https://github.com/matchms/matchms-docs)
- [Latest recorded guide revision](https://github.com/matchms/matchms-docs/commit/796f156c58d25adfb7e1528fcb24eb8c40c143a5)
  — 2024-06-13.

The tutorials are useful for workflow concepts but predate releases 0.27-0.33.
In particular, the pipeline tutorial still uses `ModifiedCosine`. Current API
docs and release notes supersede tutorial symbol names.

## Primary Scientific References

- [Huber et al., 2020 — matchms: processing and similarity evaluation of mass
  spectrometry data](https://joss.theoj.org/papers/10.21105/joss.02411),
  *Journal of Open Source Software* 5(52), 2411,
  DOI `10.21105/joss.02411`.
- [Watrous et al., 2012 — Mass spectral molecular networking of living
  microbial colonies](https://www.pnas.org/doi/10.1073/pnas.1203689109),
  *PNAS* 109, E1743-E1752, DOI `10.1073/pnas.1203689109`.
- [Harwood et al., 2023 — BLINK enables ultrafast tandem mass spectrometry
  cosine similarity scoring](https://pmc.ncbi.nlm.nih.gov/articles/PMC10439109),
  *Scientific Reports* 13, 13462, DOI `10.1038/s41598-023-40496-9`.
- [Li & Fiehn, 2023 — Flash entropy search to query all mass spectral libraries
  in real time](https://pubmed.ncbi.nlm.nih.gov/37735567),
  *Nature Methods* 20, 1475-1478,
  DOI `10.1038/s41592-023-02012-9`.
- [Huber et al., 2021 — Spec2Vec: Improved mass spectral similarity scoring
  through learning of structural relationships](https://pmc.ncbi.nlm.nih.gov/articles/PMC7909622/),
  *PLoS Computational Biology* 17, e1008724,
  DOI `10.1371/journal.pcbi.1008724`.

These papers motivate methods and interpretation. The matchms implementation
and its exact defaults remain defined by the 0.33.1 API/source.

## Ecosystem References

The current PyPI project description lists compatible or complementary tools:

- [MS2DeepScore](https://github.com/matchms/ms2deepscore)
- [Spec2Vec](https://github.com/iomega/spec2vec)
- [matchmsextras](https://github.com/matchms/matchmsextras)
- [MS2Query](https://github.com/iomega/ms2query)
- [SimMS](https://github.com/PangeAI/SimMS)
- [matchms organization](https://github.com/matchms)

Check each project's current compatibility matrix before combining environments;
matchms 0.33.1 uses NumPy 2 and Python 3.10-3.14.

## Research Queries

Focused web searches and extracts covered:

- current matchms stable version, Python support, dependencies, and release
  history;
- breaking changes and deprecated/removed APIs since 2023;
- current core, filtering, I/O, similarity, Pipeline, Scores, and networking
  documentation;
- current upstream tutorials and their last revision;
- primary publications for matchms, modified cosine/molecular networking,
  BLINK, Flash Entropy, and Spec2Vec.

No research JSON artifacts were committed to the repository.

### `references/workflows.md`

# Practical Workflows (matchms 0.33.1)

These patterns use the current 0.33.1 API. Adapt tolerances and quality filters
to the instrument, acquisition method, and scientific question.

## 1. Standard Query/Reference Preprocessing

Apply the same peak processing to both collections. Metadata enrichment can
differ when a reference library contains known structures and queries do not.

```python
from matchms import SpectrumProcessor
from matchms.filtering import (
    default_filters,
    normalize_intensities,
    require_minimum_number_of_peaks,
    require_precursor_mz,
    select_by_mz,
    select_by_relative_intensity,
)
from matchms.importing import load_spectra


def preprocess(path):
    raw = [default_filters(spectrum) for spectrum in load_spectra(path)]
    processor = SpectrumProcessor(
        [
            (require_precursor_mz, {"minimum_accepted_mz": 50.0}),
            normalize_intensities,
            (select_by_mz, {"mz_from": 20.0, "mz_to": 1500.0}),
            (select_by_relative_intensity, {"intensity_from": 0.01}),
            (require_minimum_number_of_peaks, {"n_required": 5}),
        ]
    )
    cleaned, _ = processor.process_spectra(
        raw,
        progress_bar=False,
        create_report=False,
    )
    return cleaned, ["default_filters", *processor.processing_steps]


queries, query_steps = preprocess("queries.mgf")
references, reference_steps = preprocess("library.msp")
assert query_steps == reference_steps
```

`SpectrumProcessor` may reorder built-in filters. Persist the final
`processing_steps`, not only the requested list. Run the aggregate
`default_filters` before the processor; if passed as one callable, it is treated
as a custom filter and placed after registered filters.

## 2. Run the Bundled Library Search

The bundled CLI is the fastest route to a reproducible CSV:

```bash
uv run python scripts/library_search.py \
  queries.mgf library.msp hits.csv \
  --metric modified \
  --tolerance 0.02 \
  --top-k 10 \
  --min-score 0.6 \
  --min-matches 5
```

The script:

- applies the same configurable peak filters to both inputs;
- supports cosine, exact/greedy modified cosine, neutral-loss, BLINK, and Flash
  modes;
- handles both scalar and structured matchms score records;
- records identifiers, precursor m/z, rank, score, and matched peaks;
- refuses pickle inputs;
- refuses to overwrite output unless `--force`; and
- stops before an unexpectedly large pairwise matrix unless `--max-pairs` is
  explicitly raised.

Use `--help` before batch use.

## 3. Programmatic Spectral-Library Search

```python
from matchms import calculate_scores
from matchms.similarity import ModifiedCosineGreedy

metric = ModifiedCosineGreedy(tolerance=0.02)
scores = calculate_scores(
    references=references,
    queries=queries,
    similarity_function=metric,
)

score_name = "ModifiedCosineGreedy_score"
matches_name = "ModifiedCosineGreedy_matches"
rows = []

for query_index, query in enumerate(queries):
    ranked = scores.scores_by_query(query, name=score_name, sort=True)
    for rank, (reference, value) in enumerate(ranked[:10], start=1):
        rows.append(
            {
                "query_index": query_index,
                "query_id": query.get("spectrum_id", query.get("id")),
                "reference_id": reference.get(
                    "spectrum_id",
                    reference.get("compound_name"),
                ),
                "rank": rank,
                "score": float(value[score_name]),
                "matches": int(value[matches_name]),
            }
        )
```

Filter on both score and matched peaks only after examining their distributions.
Do not label arbitrary cutoffs as universal high/medium/low confidence.

## 4. Efficient Precursor-Gated Search

For identity-oriented search, a precursor gate can reduce expensive spectral
calculations:

```python
from matchms import calculate_scores
from matchms.similarity import ModifiedCosineGreedy, PrecursorMzMatch

scores = calculate_scores(
    references,
    queries,
    PrecursorMzMatch(tolerance=10, tolerance_type="ppm"),
    array_type="sparse",
)
scores.filter_by_range(
    name="PrecursorMzMatch",
    low=0.5,
    above_operator=">=",
)
scores.calculate(
    ModifiedCosineGreedy(tolerance=0.02),
    array_type="sparse",
    join_type="left",
)
```

This pattern calculates the second metric on retained coordinates. It is
inappropriate when the scientific goal is broad analog discovery across
precursor shifts or adducts.

## 5. Reproducible `Pipeline` Workflow

`Pipeline` combines import, ordered filtering, sparse score gating, and score
calculation. A workflow can also be written to YAML.

```python
from matchms import Pipeline
from matchms.Pipeline import create_workflow

common_filters = [
    "make_charge_int",
    "add_compound_name",
    "derive_adduct_from_name",
    "derive_formula_from_name",
    "clean_compound_name",
    "interpret_pepmass",
    "add_precursor_mz",
    "derive_ionmode",
    "correct_charge",
    ["require_precursor_mz", {"minimum_accepted_mz": 50.0}],
    "normalize_intensities",
    ["select_by_relative_intensity", {"intensity_from": 0.01}],
    ["require_minimum_number_of_peaks", {"n_required": 5}],
]

workflow = create_workflow(
    yaml_file_name=None,
    query_filters=common_filters,
    reference_filters=common_filters,
    score_computations=[
        ["precursormzmatch", {"tolerance": 10, "tolerance_type": "ppm"}],
        ["filter_by_range", {"name": "PrecursorMzMatch", "low": 0.5}],
        ["modifiedcosinegreedy", {"tolerance": 0.02}],
        [
            "filter_by_range",
            {"name": "ModifiedCosineGreedy_score", "low": 0.6},
        ],
    ],
)

pipeline = Pipeline(
    workflow,
    progress_bar=False,
    logging_level="WARNING",
    logging_file="matchms-pipeline.log",
)
pipeline.run(
    query_files="queries.mgf",
    reference_files="library.msp",
    cleaned_query_file="queries-cleaned.mgf",
    cleaned_reference_file="library-cleaned.msp",
    create_report=False,
)
scores = pipeline.scores
```

Notes:

- `create_workflow()` expects matchms filter callables/names and score class
  names lowercased in `score_computations`.
- The first score should establish the coordinate set when later metrics should
  be candidate-gated.
- `filter_by_range` mutates the retained coordinates.
- `Pipeline.run()` stores final scores on `pipeline.scores`.
- Output and YAML paths must not already exist.
- For all-vs-all scoring, omit `reference_files`; Pipeline then sets symmetric
  mode.

To persist and reload a workflow:

```python
from matchms import Pipeline
from matchms.Pipeline import create_workflow
from matchms.yaml_file_functions import load_workflow_from_yaml_file

create_workflow(
    yaml_file_name="workflow.yaml",
    query_filters=common_filters,
    reference_filters=common_filters,
    score_computations=[["cosinegreedy", {"tolerance": 0.02}]],
)

workflow = load_workflow_from_yaml_file("workflow.yaml")
Pipeline(workflow).run("queries.mgf", "library.msp")
```

Treat YAML as configuration, not as a substitute for recording software and
input versions.

## 6. All-vs-All Comparison

```python
from matchms import calculate_scores
from matchms.similarity import CosineGreedy

scores = calculate_scores(
    references=spectra,
    queries=spectra,
    similarity_function=CosineGreedy(tolerance=0.02),
    array_type="sparse",
    is_symmetric=True,
)
```

`is_symmetric=True` avoids redundant calculation for symmetric methods. The
logical pair count still grows quadratically. Estimate size before launching:

```python
n = len(spectra)
unique_pairs_with_diagonal = n * (n + 1) // 2
```

For large collections, consider:

- precursor/metadata candidate masks;
- `BlinkCosine` or matrix-oriented `FlashSimilarity`;
- batched query subsets;
- sparse score thresholds; and
- approximate-neighbor indexing with validated recall.

Do not densify a large result with `to_array()` merely to find top hits.

## 7. Fast Matrix Scoring

### Flash entropy

```python
from matchms import calculate_scores
from matchms.similarity import FlashSimilarity

scores = calculate_scores(
    references,
    queries,
    FlashSimilarity(
        score_type="spectral_entropy",
        matching_mode="fragment",
        tolerance=0.02,
        noise_cutoff=0.01,
    ),
)
```

### Fast modified-cosine-like mode

```python
scores = calculate_scores(
    references,
    queries,
    FlashSimilarity(
        score_type="cosine",
        matching_mode="hybrid",
        tolerance=0.02,
    ),
)
```

Flash outputs a scalar `FlashSimilarity` field without a matched-peak count.
Validate ranking agreement against a transparent baseline on representative
data.

## 8. Mirror-Plot Validation

```python
from pathlib import Path

output = Path("top-hit-mirror.png")
axis = query.plot_against(reference, figsize=(10, 6), dpi=200)
axis.figure.savefig(output, bbox_inches="tight")
```

Inspect:

- unshifted and shifted matched peaks;
- precursor and adduct agreement;
- whether the score is driven by one dominant fragment;
- unexplained high-intensity peaks; and
- collision-energy/acquisition differences.

## 9. Spectral Similarity Network

Networks require an all-vs-all `Scores` object and a unique identifier on each
spectrum:

```python
from matchms import calculate_scores
from matchms.networking import SimilarityNetwork
from matchms.similarity import ModifiedCosineGreedy

scores = calculate_scores(
    spectra,
    spectra,
    ModifiedCosineGreedy(tolerance=0.02),
    array_type="sparse",
    is_symmetric=True,
)

network = SimilarityNetwork(
    identifier_key="spectrum_id",
    top_n=20,
    max_links=10,
    score_cutoff=0.7,
    link_method="mutual",
    keep_unconnected_nodes=True,
)
network.create_network(
    scores,
    score_name="ModifiedCosineGreedy_score",
)
network.export_to_file("spectral-network.graphml", graph_format="graphml")
```

Supported export formats include GraphML, GEXF, GML, Cytoscape JSON, and JSON.
`top_n` must be at least `max_links`. Equal scores near the strict link limit
can make tie selection order-dependent; use deterministic identifiers and
document parameters.

Network components are hypotheses about spectral relatedness, not proof of
shared structure or biosynthetic origin.

## 10. Structure Versus Spectrum Similarity

Use separate labels and outputs:

- spectral similarity compares measured peak patterns;
- fingerprint similarity compares known molecular structures;
- correlation between the two can be analyzed only where reliable structures
  are available.

Do not include a query's true structure in candidate ranking when evaluating a
spectral identification method; that leaks the answer.

## 11. USI-Based Reproducible Pair

```python
from matchms.importing import load_from_usi
from matchms.similarity import CosineGreedy

reference = load_from_usi(
    "mzspec:GNPS:GNPS-LIBRARY:accession:CCMSLIB00000424840"
)
query = load_from_usi(
    "mzspec:MSV000086109:BD5_dil2x_BD5_01_57213:scan:760"
)
result = CosineGreedy(tolerance=0.02).pair(reference, query)
```

Record resolver, retrieval date, and returned metadata. A USI is stable
provenance, but resolver availability and returned annotations can change.

## 12. Provenance Record

At minimum, save:

```python
import json
import platform

import matchms

provenance = {
    "matchms_version": matchms.__version__,
    "python_version": platform.python_version(),
    "query_files": ["queries.mgf"],
    "reference_files": ["library.msp"],
    "metadata_harmonization": True,
    "processing_steps": query_steps,
    "similarity": {
        "class": "ModifiedCosineGreedy",
        "tolerance_da": 0.02,
    },
    "selection": {
        "top_k": 10,
        "minimum_score": 0.6,
        "minimum_matches": 5,
    },
}

with open("provenance.json", "w", encoding="utf-8") as handle:
    json.dump(provenance, handle, indent=2, default=str)
```

Also retain input checksums, library release/date, acquisition information,
code/configuration, and any manual curation decisions.

## Failure Modes

- **No modified-cosine results:** check precursor m/z after harmonization and
  filtering.
- **Unexpected `TypeError` from `SpectrumProcessor`:** call
  `process_spectrum()`/`process_spectra()`; the processor is not callable.
- **Cannot format a score as float:** extract a named field from the structured
  score record.
- **Top-hit value treated as an index:** `scores_by_query()` returns a Spectrum.
- **Huge memory use:** avoid dense conversion; gate candidates and estimate pair
  count.
- **No network edges:** verify identifier fields, score layer name, threshold,
  and that the scores are all-vs-all.
- **Fingerprint warnings:** migrate from `add_fingerprint()` to `Fingerprints`
  and bridge to the current `FingerprintSimilarity` only when required.
- **Output already exists:** matchms intentionally refuses overwrite in generic
  writers and pipeline outputs; choose a new path or remove only after explicit
  confirmation.

### `scripts/library_search.py`

```python
#!/usr/bin/env python3
"""Search query MS/MS spectra against a reference library with matchms.

Examples:
    uv run python library_search.py queries.mgf library.msp hits.csv
    uv run python library_search.py queries.mgf library.msp hits.csv \
        --metric modified --tolerance 0.02 --top-k 10 \
        --min-score 0.6 --min-matches 5
    uv run python library_search.py queries.mgf library.msp hits.csv \
        --metric flash-entropy --max-pairs 20000000

This script targets matchms 0.33.1. It refuses pickle inputs, bounds the
query-reference Cartesian product, applies identical peak processing to both
collections, and handles both scalar and structured matchms score records.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

try:
    from matchms import SpectrumProcessor, calculate_scores
    from matchms.filtering import (
        add_compound_name,
        add_precursor_mz,
        clean_compound_name,
        correct_charge,
        derive_adduct_from_name,
        derive_formula_from_name,
        derive_ionmode,
        interpret_pepmass,
        make_charge_int,
        normalize_intensities,
        reduce_to_number_of_peaks,
        remove_peaks_around_precursor_mz,
        require_minimum_number_of_peaks,
        require_precursor_mz,
        select_by_mz,
        select_by_relative_intensity,
    )
    from matchms.importing import load_spectra
    from matchms.similarity import (
        BlinkCosine,
        CosineGreedy,
        CosineHungarian,
        CosineLinear,
        FlashSimilarity,
        ModifiedCosineGreedy,
        ModifiedCosineHungarian,
        NeutralLossesCosine,
    )
except ImportError as exc:
    raise SystemExit(
        'matchms is required. Install the verified release with: '
        'uv pip install "matchms==0.33.1"'
    ) from exc


TARGET_VERSION = "0.33.1"
UNSAFE_PICKLE_SUFFIXES = {".pickle", ".pkl"}
SUPPORTED_SUFFIXES = {".json", ".mgf", ".msp", ".mzml", ".mzxml"}
STRUCTURED_METRICS = {
    "cosine",
    "cosine-exact",
    "cosine-linear",
    "modified",
    "modified-exact",
    "neutral-loss",
    "blink",
}
PRECURSOR_METRICS = {
    "modified",
    "modified-exact",
    "neutral-loss",
    "flash-modified",
}
DEFAULT_METADATA_FILTERS = (
    make_charge_int,
    add_compound_name,
    derive_adduct_from_name,
    derive_formula_from_name,
    clean_compound_name,
    interpret_pepmass,
    add_precursor_mz,
    derive_ionmode,
    correct_charge,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("queries", type=Path, help="Query spectra: MGF/MSP/mzML/mzXML/JSON")
    parser.add_argument("references", type=Path, help="Reference library: MGF/MSP/mzML/mzXML/JSON")
    parser.add_argument("output", type=Path, help="Output CSV path")
    parser.add_argument(
        "--metric",
        choices=[
            "cosine",
            "cosine-exact",
            "cosine-linear",
            "modified",
            "modified-exact",
            "neutral-loss",
            "blink",
            "flash-entropy",
            "flash-cosine",
            "flash-modified",
        ],
        default="modified",
        help="Similarity method (default: modified)",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.02,
        help="Fragment matching tolerance in daltons (default: 0.02)",
    )
    parser.add_argument("--top-k", type=int, default=10, help="Hits per query (default: 10)")
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Minimum similarity in [0, 1] (default: 0)",
    )
    parser.add_argument(
        "--min-matches",
        type=int,
        default=0,
        help="Minimum matched peaks for metrics that report matches (default: 0)",
    )
    parser.add_argument(
        "--array-type",
        choices=["numpy", "sparse"],
        default="numpy",
        help="matchms calculation array type (default: numpy)",
    )
    parser.add_argument(
        "--max-pairs",
        type=int,
        default=5_000_000,
        help="Refuse comparisons above this reference×query count (default: 5,000,000)",
    )
    parser.add_argument(
        "--relative-intensity",
        type=float,
        default=0.01,
        help="Drop peaks below this fraction of maximum; 0 disables (default: 0.01)",
    )
    parser.add_argument(
        "--min-peaks",
        type=int,
        default=5,
        help="Reject spectra with fewer peaks; 0 disables (default: 5)",
    )
    parser.add_argument(
        "--max-peaks",
        type=int,
        default=None,
        help="Keep at most this many highest-intensity peaks",
    )
    parser.add_argument("--mz-min", type=float, default=None, help="Minimum fragment m/z")
    parser.add_argument("--mz-max", type=float, default=None, help="Maximum fragment m/z")
    parser.add_argument(
        "--remove-precursor-window",
        type=float,
        default=None,
        metavar="DA",
        help="Remove peaks within this precursor-centered window",
    )
    parser.add_argument(
        "--no-default-filters",
        action="store_true",
        help="Skip matchms metadata default_filters",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Skip intensity normalization",
    )
    parser.add_argument(
        "--query-id-field",
        default=None,
        help="Preferred metadata key for query identifiers",
    )
    parser.add_argument(
        "--reference-id-field",
        default=None,
        help="Preferred metadata key for reference identifiers",
    )
    parser.add_argument(
        "--bin-width",
        type=float,
        default=0.001,
        help="BLINK bin width in daltons (default: 0.001)",
    )
    parser.add_argument(
        "--blink-top-k",
        type=int,
        default=None,
        help="Optional number of most intense peaks retained by BLINK",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite an existing CSV")
    parser.add_argument("--quiet", action="store_true", help="Hide processing progress bars")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    for path, label in ((args.queries, "query"), (args.references, "reference")):
        if not path.is_file():
            raise ValueError(f"{label} file does not exist: {path}")
        suffix = path.suffix.lower()
        if suffix in UNSAFE_PICKLE_SUFFIXES:
            raise ValueError(
                f"pickle input is intentionally refused because unpickling can execute code: {path}"
            )
        if suffix not in SUPPORTED_SUFFIXES:
            raise ValueError(
                f"unsupported {label} suffix {suffix!r}; choose MGF, MSP, mzML, mzXML, or JSON"
            )

    if args.output.exists() and not args.force:
        raise ValueError(f"output already exists (pass --force to replace it): {args.output}")
    if not args.output.parent.is_dir():
        raise ValueError(f"output directory does not exist: {args.output.parent}")
    if args.tolerance <= 0:
        raise ValueError("--tolerance must be positive")
    if args.top_k <= 0:
        raise ValueError("--top-k must be positive")
    if not 0.0 <= args.min_score <= 1.0:
        raise ValueError("--min-score must be between 0 and 1")
    if args.min_matches < 0:
        raise ValueError("--min-matches cannot be negative")
    if args.max_pairs <= 0:
        raise ValueError("--max-pairs must be positive")
    if not 0.0 <= args.relative_intensity <= 1.0:
        raise ValueError("--relative-intensity must be between 0 and 1")
    if args.min_peaks < 0:
        raise ValueError("--min-peaks cannot be negative")
    if args.max_peaks is not None and args.max_peaks <= 0:
        raise ValueError("--max-peaks must be positive")
    if args.mz_min is not None and args.mz_max is not None and args.mz_min >= args.mz_max:
        raise ValueError("--mz-min must be smaller than --mz-max")
    if args.remove_precursor_window is not None and args.remove_precursor_window <= 0:
        raise ValueError("--remove-precursor-window must be positive")
    if args.bin_width <= 0:
        raise ValueError("--bin-width must be positive")
    if args.blink_top_k is not None and args.blink_top_k <= 0:
        raise ValueError("--blink-top-k must be positive")
    if args.metric not in STRUCTURED_METRICS and args.min_matches > 0:
        raise ValueError(f"--metric {args.metric!r} does not report matched-peak counts")


def installed_matchms_version() -> str:
    try:
        return version("matchms")
    except PackageNotFoundError:
        return "unknown"


def create_processor(args: argparse.Namespace) -> SpectrumProcessor:
    filters: list[Any] = []
    if not args.no_default_filters:
        # Expand default_filters so SpectrumProcessor can preserve the registered
        # metadata-before-peaks order. The aggregate callable is otherwise
        # treated as a custom filter and moved to the end.
        filters.extend(DEFAULT_METADATA_FILTERS)

    needs_precursor = (
        args.metric in PRECURSOR_METRICS
        or args.remove_precursor_window is not None
    )
    if needs_precursor:
        filters.append((require_precursor_mz, {"minimum_accepted_mz": 0.0}))
    if not args.no_normalize:
        filters.append(normalize_intensities)
    if args.mz_min is not None or args.mz_max is not None:
        filters.append(
            (
                select_by_mz,
                {
                    "mz_from": 0.0 if args.mz_min is None else args.mz_min,
                    "mz_to": float("inf") if args.mz_max is None else args.mz_max,
                },
            )
        )
    if args.remove_precursor_window is not None:
        filters.append(
            (
                remove_peaks_around_precursor_mz,
                {"mz_tolerance": args.remove_precursor_window},
            )
        )
    if args.relative_intensity > 0:
        filters.append(
            (
                select_by_relative_intensity,
                {"intensity_from": args.relative_intensity},
            )
        )
    if args.max_peaks is not None:
        filters.append((reduce_to_number_of_peaks, {"n_max": args.max_peaks}))
    if args.min_peaks > 0:
        filters.append((require_minimum_number_of_peaks, {"n_required": args.min_peaks}))
    return SpectrumProcessor(filters)


def load_and_process(
    path: Path,
    processor: SpectrumProcessor,
    *,
    show_progress: bool,
) -> tuple[list[Any], int]:
    raw = list(load_spectra(str(path)))
    cleaned, _ = processor.process_spectra(
        raw,
        progress_bar=show_progress,
        create_report=False,
    )
    return cleaned, len(raw)


def create_metric(args: argparse.Namespace) -> Any:
    common = {"tolerance": args.tolerance}
    if args.metric == "cosine":
        return CosineGreedy(**common)
    if args.metric == "cosine-exact":
        return CosineHungarian(**common)
    if args.metric == "cosine-linear":
        return CosineLinear(**common)
    if args.metric == "modified":
        return ModifiedCosineGreedy(**common)
    if args.metric == "modified-exact":
        return ModifiedCosineHungarian(**common)
    if args.metric == "neutral-loss":
        return NeutralLossesCosine(**common)
    if args.metric == "blink":
        return BlinkCosine(
            tolerance=args.tolerance,
            bin_width=args.bin_width,
            min_relative_intensity=args.relative_intensity,
            top_k=args.blink_top_k,
            sparse_score_min=args.min_score,
        )
    if args.metric == "flash-entropy":
        return FlashSimilarity(
            score_type="spectral_entropy",
            matching_mode="fragment",
            tolerance=args.tolerance,
        )
    if args.metric == "flash-cosine":
        return FlashSimilarity(
            score_type="cosine",
            matching_mode="fragment",
            tolerance=args.tolerance,
        )
    if args.metric == "flash-modified":
        return FlashSimilarity(
            score_type="cosine",
            matching_mode="hybrid",
            tolerance=args.tolerance,
        )
    raise ValueError(f"unsupported metric: {args.metric}")


def choose_score_fields(score_names: tuple[str, ...]) -> tuple[str, str | None]:
    score_name = next(
        (name for name in score_names if name.endswith("_score")),
        score_names[0],
    )
    matches_name = next(
        (name for name in score_names if name.endswith("_matches")),
        None,
    )
    return score_name, matches_name


def numeric_field(value: Any, name: str) -> float:
    dtype = getattr(value, "dtype", None)
    names = getattr(dtype, "names", None)
    if names and name in names:
        return float(value[name])
    return float(value)


def matched_peaks(value: Any, name: str | None) -> int | None:
    if name is None:
        return None
    dtype = getattr(value, "dtype", None)
    names = getattr(dtype, "names", None)
    if names and name in names:
        return int(value[name])
    return None


def spectrum_id(
    spectrum: Any,
    *,
    preferred: str | None,
    index: int,
    prefix: str,
) -> str:
    keys = [
        preferred,
        "spectrum_id",
        "id",
        "feature_id",
        "scan_number",
        "compound_name",
        "title",
    ]
    for key in keys:
        if key:
            value = spectrum.get(key)
            if value not in (None, ""):
                return str(value)
    return f"{prefix}-{index}"


def metadata_value(spectrum: Any, key: str) -> str:
    value = spectrum.get(key)
    return "" if value is None else str(value)


def write_hits(
    output: Path,
    *,
    scores: Any,
    queries: list[Any],
    references: list[Any],
    args: argparse.Namespace,
) -> int:
    score_name, matches_name = choose_score_fields(scores.score_names)
    reference_indices = {id(spectrum): index for index, spectrum in enumerate(references)}
    fieldnames = [
        "query_index",
        "query_id",
        "query_precursor_mz",
        "reference_index",
        "reference_id",
        "reference_compound_name",
        "reference_inchikey",
        "reference_precursor_mz",
        "rank",
        "metric",
        "score_field",
        "score",
        "matched_peaks",
    ]

    rows_written = 0
    mode = "w"
    with output.open(mode, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for query_index, query in enumerate(queries):
            ranked = scores.scores_by_query(query, name=score_name, sort=True)
            accepted = 0
            for reference, value in ranked:
                score = numeric_field(value, score_name)
                matches = matched_peaks(value, matches_name)
                if not math.isfinite(score) or score < args.min_score:
                    continue
                if matches is not None and matches < args.min_matches:
                    continue

                reference_index = reference_indices.get(id(reference))
                if reference_index is None:
                    raise RuntimeError("a score referenced a spectrum outside the input library")

                accepted += 1
                writer.writerow(
                    {
                        "query_index": query_index,
                        "query_id": spectrum_id(
                            query,
                            preferred=args.query_id_field,
                            index=query_index,
                            prefix="query",
                        ),
                        "query_precursor_mz": metadata_value(query, "precursor_mz"),
                        "reference_index": reference_index,
                        "reference_id": spectrum_id(
                            reference,
                            preferred=args.reference_id_field,
                            index=reference_index,
                            prefix="reference",
                        ),
                        "reference_compound_name": metadata_value(
                            reference,
                            "compound_name",
                        ),
                        "reference_inchikey": metadata_value(reference, "inchikey"),
                        "reference_precursor_mz": metadata_value(
                            reference,
                            "precursor_mz",
                        ),
                        "rank": accepted,
                        "metric": args.metric,
                        "score_field": score_name,
                        "score": format(score, ".12g"),
                        "matched_peaks": "" if matches is None else matches,
                    }
                )
                rows_written += 1
                if accepted >= args.top_k:
                    break
    return rows_written


def run(args: argparse.Namespace) -> int:
    validate_args(args)
    matchms_version = installed_matchms_version()
    if matchms_version != TARGET_VERSION:
        print(
            f"warning: script targets matchms {TARGET_VERSION}; found {matchms_version}",
            file=sys.stderr,
        )

    processor = create_processor(args)
    queries, raw_query_count = load_and_process(
        args.queries,
        processor,
        show_progress=not args.quiet,
    )
    references, raw_reference_count = load_and_process(
        args.references,
        processor,
        show_progress=not args.quiet,
    )
    if not queries:
        raise ValueError("no query spectra remain after processing")
    if not references:
        raise ValueError("no reference spectra remain after processing")

    pair_count = len(queries) * len(references)
    if pair_count > args.max_pairs:
        raise ValueError(
            f"comparison would evaluate {pair_count:,} pairs, above --max-pairs "
            f"{args.max_pairs:,}; raise the limit only after reviewing memory/runtime"
        )

    print(
        f"matchms {matchms_version}; queries {raw_query_count}->{len(queries)}; "
        f"references {raw_reference_count}->{len(references)}; pairs {pair_count:,}",
        file=sys.stderr,
    )
    print(f"processing steps: {processor.processing_steps}", file=sys.stderr)

    metric = create_metric(args)
    scores = calculate_scores(
        references=references,
        queries=queries,
        similarity_function=metric,
        array_type=args.array_type,
        is_symmetric=False,
    )
    rows_written = write_hits(
        args.output,
        scores=scores,
        queries=queries,
        references=references,
        args=args,
    )
    print(
        f"wrote {rows_written} hit rows to {args.output} "
        f"(score fields: {', '.join(scores.score_names)})",
        file=sys.stderr,
    )
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return run(args)
    except (AssertionError, OSError, RuntimeError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```
