---
name: ontology-term-resolution
description: Resolve free-text scientific labels to ontology term IDs and validate existing CURIEs against the EBI Ontology Lookup Service (OLS4). Use whenever an ontology identifier must be produced or checked - annotating tissue, cell type, disease, phenotype, assay, chemical, organism, sex, or developmental stage fields; preparing metadata for GEO, ENA, BioSamples, CELLxGENE, HCA, or ISA-Tab submission; auditing a metadata table of term IDs; checking whether a term is obsolete and what replaced it; or mapping between ontologies. Triggers include "ontology term", "ontology ID", "CURIE", "controlled vocabulary", "UBERON", "CL:", "MONDO", "HPO", "EFO", "ChEBI", "NCBITaxon", "GO term", "PATO", "annotate this tissue/cell type/disease", and any request to emit or verify an identifier shaped like PREFIX:0001234.
---

# Ontology Term Resolution

## When to use

Any time an ontology identifier is about to be written down or trusted: annotating a metadata
column, filling a submission template, auditing a table someone else produced, or checking whether
an ID in an old file is still current.

## The rule

**Never write an ontology ID from memory, and never accept one without checking it.**

Ontology IDs are memorable in form and arbitrary in detail. A plausible-looking `UBERON:0002108`
is a real term (small intestine) that is not the liver, and nothing downstream will catch the
substitution — the ID is well-formed, the ontology is right, and the metadata is silently wrong.
Reviewers cannot spot it either, which is why these errors persist into published datasets.

Every ID this skill emits comes from a live OLS lookup. Every ID it is handed gets verified.

## Two directions

| Direction | Script | Question answered |
| --- | --- | --- |
| text → ID | `scripts/resolve_terms.py` | What is the term for "left ventricle"? |
| ID → verdict | `scripts/validate_terms.py` | Is `EFO:0001067` real, current, and labelled what this file claims? |

Both take single values or files, emit TSV or JSON, and need no packages beyond the standard
library.

## Resolve text to terms

```bash
cd skills/ontology-term-resolution/scripts

# one string, constrained to the ontology that should define it
python3 resolve_terms.py "liver" --ontology uberon
```

```
query   rank  curie           label  ontology  match_type   strategy  defining_ontology
liver   1     UBERON:0002107  liver  uberon    exact_label  exact     true
```

```bash
# a column of tissue names; anything not an exact hit is reported, not guessed
python3 resolve_terms.py --input tissues.txt --ontology uberon \
    --exact-only --format tsv -o resolved.tsv

# accept fuzzy fallbacks, then review the partial hits by hand
python3 resolve_terms.py "left ventrical of heart" --ontology uberon --top 3
```

The search escalates `exact` (label and synonym) → `token` → `fulltext` and stops at the first
strategy that returns anything, reporting which one fired. `--exact-only` disables the ladder.
`--branch UBERON:0000465` restricts candidates to descendants of a term.

**Read `match_type` before using a result.** `exact_label` and `exact_synonym` are safe;
`partial` means OLS returned its best guess for a string that does not exist as written, and
needs a human decision. `unresolved` is a legitimate output — see `references/curation-rules.md`
for the normalisations worth retrying first.

## Validate existing IDs

```bash
python3 validate_terms.py UBERON:0002107 EFO:0001067 UBERON:9999999
```

```
id              status     actual_label                  ontology  replacement     detail
UBERON:0002107  ok         liver                         uberon
EFO:0001067     obsolete   obsolete_parasitic infection  efo       MONDO:0005135   obsolete; replaced by MONDO:0005135
UBERON:9999999  not_found                                                          no such term in the ontology this prefix names
```

Exit code is 1 if anything failed, 0 otherwise, 2 on usage or network trouble — so it works as a
CI gate on a metadata file:

```bash
# id + label columns; catches IDs that exist but are labelled as something else
python3 validate_terms.py --input metadata.tsv --strict

# a tissue column must hold UBERON anatomical entities and nothing else
python3 validate_terms.py --input tissue_ids.tsv \
    --branch UBERON:0000465 --expect-ontology uberon
```

| Status | Meaning | Verdict |
| --- | --- | --- |
| `ok` | Exists, current, consistent with everything asserted | pass |
| `matched_synonym` | Claimed label is a synonym; primary label differs | warn |
| `imported_only` | Home ontology no longer asserts this ID | warn |
| `not_a_class` | Term is a property or individual | warn |
| `not_found` | No such term | fail |
| `obsolete` | Obsoleted; `replacement` gives the successor when one exists | fail |
| `label_mismatch` | ID and claimed label describe different things | fail |
| `wrong_ontology` | Right kind of ID, wrong ontology for this column | fail |
| `wrong_branch` | Not a descendant of the required root | fail |
| `malformed_curie` | Not of the form `PREFIX:local` | fail |

`--strict` promotes warnings to failures.

## API behaviour that will mislead you

These are verified against the live service and are the reason this skill ships scripts rather
than a recipe. Full detail in `references/ols4-api.md`.

| Trap | Consequence |
| --- | --- |
| `exact=true` is exact **token** matching | `liver` returns 161 hits in UBERON; adding `queryFields=label` returns 1 |
| `/search` never returns `is_obsolete` or `term_replaced_by` | Named in `fieldList` they are dropped silently; only term detail can answer "is this ID still current" |
| `ontology=efo` returns MONDO and CL hits | Ontologies import each other; filter on the CURIE prefix yourself |
| The same term appears once per importing ontology | Deduplicate on `obo_id`, keep `is_defining_ontology: true` |
| The `obo_id` index has holes | `MONDO:0000001` is live but unindexed by `obo_id`; an IRI fallback is required to avoid a false `not_found` |
| IRIs are not all OBO PURLs | EFO and Orphanet use their own namespaces — resolve IRIs, do not template them |
| OxO is retired | Returns HTML with HTTP 200; use term cross-references or SSSOM instead |
| A branch check does not exclude cell types from anatomy | CARO puts `cell` under `anatomical structure`; constrain the prefix too |

## Choosing the ontology

MONDO for disease, HP for phenotype, UBERON for tissue, CL for cell type, EFO for assay, ChEBI for
compounds, NCBITaxon for organism, PATO for sex and for `normal`. Prefix-to-OLS-id mappings (`HP`
is served as `hp`, `Orphanet` as `ordo`), branch roots for `--branch`, and the overlapping-ontology
judgement calls are in `references/ontology-registry.md`.

## Reporting results

Give the ID **and** the label, and say how each was matched. A table of bare IDs cannot be
reviewed. State unresolved terms explicitly rather than filling them with the nearest hit.

## References

- `references/ols4-api.md` — endpoints, parameters, response fields, and every verified trap.
- `references/ontology-registry.md` — prefix/ontology-id table, branch roots, which ontology owns
  which concept.
- `references/curation-rules.md` — candidate-selection procedure, normalisations to retry,
  auditing an existing table, obsolete terms, cross-ontology mapping.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/ontology-term-resolution/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/curation-rules.md`

# Curation rules

How to choose among candidates, and what to do when the honest answer is "no term".

## The decision procedure

Run it per string. Stop at the first step that gives a defensible answer.

1. **Exact label match in the expected ontology, from its defining ontology.** Accept.
2. **Exact synonym match.** Accept, but record the primary label, not the synonym. Metadata files
   should carry the ontology's own label so they diff cleanly against the ontology release.
3. **Exact match, wrong ontology.** Usually a category error in the source column, not a naming
   problem — `hepatocyte` in a tissue field means the column mixes tissue and cell type. Fix the
   column, do not force a match.
4. **Partial match only.** Do not accept silently. Either:
   - normalise the input and retry (see below), or
   - present the top candidates with their labels and let a human choose, or
   - mark it unresolved.
5. **Nothing.** Mark unresolved and say so. An unresolved row is a correct output.

`resolve_terms.py` implements steps 1–4's search side and labels every hit `exact_label`,
`exact_synonym`, or `partial`. The judgement about whether a `partial` is acceptable is yours;
the tool will not make it for you.

## Normalisations worth retrying

Cheap rewrites that convert a `partial` into an `exact_label`, in rough order of yield:

- Drop qualifiers the source added: `liver (donor)`, `Liver - left lobe [FFPE]`.
- Expand lab shorthand: `PBMC` → `peripheral blood mononuclear cell`, `WT` → the actual genotype,
  `M`/`F` → `male`/`female`.
- Reverse an inverted phrase: `ventricle, left` → `left ventricle`, `cortex, kidney` → `kidney
  cortex`.
- Singularise: `hepatocytes` → `hepatocyte`. Ontology labels are singular.
- Anglicise or Americanise: ontology labels vary; try both `oesophagus` and `esophagus`.
- Strip species prefixes: `human liver` → `liver` (species belongs in a separate NCBITaxon field).

Do **not** normalise away hyphens, Greek letters, digits, or capitalised gene symbols — `CD4-positive`
and `alpha-beta T cell` mean what they say, and `normalize_label()` deliberately folds only case and
whitespace.

When plain search keeps failing on lab shorthand, try ZOOMA with an ontology filter
(`ols4-api.md`). It matches against how curators previously mapped that exact string, which is a
different and often better signal than lexical search.

## What "unresolved" should look like

Never invent an ID to fill a cell. An unresolved row carries the original string, an empty ID, and
the reason. Downstream that is a visible gap; an invented `UBERON:0002108` is a silent error that
survives review because it looks exactly like a real ID.

If a concept genuinely has no term and the project depends on it, the route is a new-term request
to the ontology (GitHub issue on the ontology's tracker, with a definition and a reference), not a
locally minted identifier.

## Auditing an existing metadata table

The high-yield checks, in order:

1. **Every ID exists.** `validate_terms.py --input table.tsv`.
2. **No obsolete IDs.** Obsolete terms carry `term_replaced_by` often enough that the fix is
   mechanical — but apply replacements deliberately, since a replacement can be broader or
   narrower than the original.
3. **Labels match IDs.** Supply the label column. Mismatches are where copy-paste drift and
   hallucinated IDs surface: the ID is real, the label is real, and they describe different things.
4. **Right ontology per column.** `--expect-ontology`.
5. **Right branch per column.** `--branch`, remembering it does not exclude cell types from
   anatomy (`ontology-registry.md`).

`--strict` turns warnings into failures, which is the right setting for a CI gate. Warnings are
`matched_synonym` (label is a synonym rather than the primary label), `imported_only` (the home
ontology no longer asserts this ID), and `not_a_class`.

## Obsolete terms

Obsoletion is not deletion — the ID keeps resolving, and its label is usually prefixed
`obsolete_`. That prefix is a useful smell in any metadata file:

```
EFO:0001067  obsolete_parasitic infection  ->  replaced by MONDO:0005135
```

Some obsolete terms have no replacement, only a `consider` annotation or nothing at all. Then the
term must be re-curated by hand; there is no automatic answer.

## Cross-ontology mapping

OxO is retired and returns HTML with HTTP 200. Two workable routes:

- **Term cross-references.** `term_detail(curie)["annotation"]["database_cross_reference"]` lists
  equivalents — `UBERON:0002107` carries `MESH:D008099`, `NCIT:C12392`, `FMA:7197`, `UMLS:C0023884`,
  and more.
- **SSSOM mapping sets** published by Monarch and the OBO community, when provenance and mapping
  predicates (`skos:exactMatch` vs `closeMatch`) matter.

Cross-references are asserted by curators at varying confidence and are not all `exactMatch`.
Treat a single xref as a lead, not a proof, when the mapping drives analysis rather than display.

```python
from ols_client import term_detail
xrefs = (term_detail("UBERON:0002107") or {}).get("annotation", {}).get(
    "database_cross_reference", []
)
```

## Reporting

When you hand back resolved terms, give the ID *and* the label, and say how each was matched. A
table of bare IDs cannot be reviewed — no reader can tell `UBERON:0002107` from `UBERON:0002108`
by eye, which is precisely why invented IDs survive review.

### `references/ols4-api.md`

# EBI OLS4 API reference

Base URL: `https://www.ebi.ac.uk/ols4/api`. No API key, no registration. Be polite: send a
descriptive `User-Agent`, keep concurrency low, and back off on HTTP 429.

Every behaviour recorded here was checked against the live service in July 2026. OLS4 changed
several defaults from OLS3, and the traps below are the ones that silently produce wrong answers
rather than errors.

## `/search` — text to candidate terms

| Parameter | Effect |
| --- | --- |
| `q` | The query string. |
| `ontology` | Comma-separated OLS **ontology ids** (`uberon`, not `UBERON`). Filters by ontology *document*, not by CURIE prefix — see trap 3. |
| `queryFields` | Which fields to match. Default is every indexed field. Use `label` or `label,synonym`. |
| `exact` | `true` restricts to whole-token matches — **not** to exact labels. See trap 1. |
| `obsoletes` | `true` includes obsolete terms. Default excludes them. |
| `allChildrenOf` | URL-encoded **IRI**; restricts hits to descendants of that term. |
| `childrenOf` | As above but direct children only. |
| `rows`, `start` | Paging. |
| `fieldList` | Fields to return. See trap 2 for what it will not give you. |

Response shape: `{"response": {"numFound": N, "docs": [...]}}`. Useful doc fields are `obo_id`,
`label`, `synonym`, `ontology_name`, `is_defining_ontology`, `short_form`, `iri`, `type`.

### Trap 1 — `exact=true` is exact *token*, not exact *label*

```
q=liver&ontology=uberon&exact=true                    -> numFound 161
q=liver&ontology=uberon&exact=true&queryFields=label  -> numFound 1
```

With `exact=true` alone, `caudate lobe of liver` matches because the token `liver` appears in its
label. `zzzquux` still returns 0, so the flag does something — just not what its name promises.
Restrict `queryFields` to `label` or `label,synonym`, and re-check exactness client-side anyway.
`resolve_terms.py` classifies every hit as `exact_label`, `exact_synonym`, or `partial` for
exactly this reason.

### Trap 2 — `/search` never reports obsolescence

`is_obsolete` and `term_replaced_by` are **not returned by `/search`**, even when named explicitly
in `fieldList` — the fields are dropped from the response without error. Only the term-detail
endpoint carries them. Search does exclude obsolete terms by default, so search results are safe;
but you cannot use search to check whether an ID *you already have* is still current.

### Trap 3 — `ontology=` does not mean "this prefix"

Ontologies import each other, so a filtered search returns foreign prefixes:

```
q=parasitic infection&ontology=efo  -> includes MONDO:0016472, CL:0001069
q=hepatocyte&ontology=uberon        -> CL:0000182, is_defining_ontology=false
```

Filter on the CURIE prefix yourself if the target field requires one ontology.

### Trap 4 — the same term appears once per importing ontology

A search for `liver` returns `UBERON:0002107` under `uberon` (`is_defining_ontology: true`) and
again under `cl` and `hra` (`false`). Deduplicate on `obo_id` and keep the defining copy.

## `/ontologies/{ontology}/terms?obo_id={CURIE}` — term detail

The authoritative per-term lookup, and the only one that reports obsolescence.

```
GET /ontologies/efo/terms?obo_id=EFO:0001067
  is_obsolete       true
  term_replaced_by  "http://purl.obolibrary.org/obo/MONDO_0005135"
```

`term_replaced_by` is a **full IRI**, not a CURIE. Convert by splitting on the final underscore
(`iri_to_curie` in `ols_client.py`), which also handles multi-underscore prefixes such as
`APOLLO_SV_00000001`.

A missing term returns HTTP **404** with a JSON body, so 404 is a normal answer to check for, not
an exception to crash on.

### Trap 5 — the `obo_id` index has holes

`MONDO:0000001` is defined by MONDO and imported by eleven other ontologies, yet
`?obo_id=MONDO:0000001` returns zero results — OLS never indexed its `obo_id`. Treating that as
"ID does not exist" is a false failure on a live term.

Fall back to `/terms?iri={encoded IRI}`, which returns one copy per ontology; prefer the copy whose
`ontology_name` matches the home ontology and has `is_defining_ontology: true`. `term_detail()` in
`ols_client.py` does this automatically and tags the result with `_resolved_via`.

## `/terms?iri={encoded IRI}` — cross-ontology copies

Returns every ontology's copy of one IRI. Useful for the fallback above and for seeing which
ontologies import a term. `UBERON:0002107` has 42 copies.

## Hierarchy

`_links.hierarchicalAncestors.href` on a term detail gives the transitive ancestors, paged
(`?size=500`, follow `_links.next`). Use it to check that a term sits in the branch a metadata
field requires.

Beware that CARO makes `cell` a descendant of `anatomical structure`, so `CL:0000182` (hepatocyte)
genuinely *is* under `UBERON:0000061`. A branch check alone will not keep cell types out of a
tissue column — constrain the CURIE prefix too.

`/ontologies/{id}/terms/roots` is unreliable for merged ontologies: MONDO's roots list returns bare
numeric ids and unrelated BFO/CHEBI/FOODON entries. Do not build logic on it.

## IRI patterns

Do not template IRIs when you can resolve them. The OBO PURL pattern is not universal:

| Prefix | IRI |
| --- | --- |
| most OBO prefixes | `http://purl.obolibrary.org/obo/{PREFIX}_{local}` |
| `EFO` | `http://www.ebi.ac.uk/efo/EFO_{local}` |
| `Orphanet` | `http://www.orpha.net/ORDO/Orphanet_{local}` |

## Related services

**ZOOMA** (`https://www.ebi.ac.uk/spot/zooma/v2/api/services/annotate`) maps free text to terms
using curated annotation history. Unfiltered it is unusable — `propertyValue=liver` returns
`https://w3id.org/gold.vocab/Liver`. Always pass a filter:

```
?propertyValue=liver&propertyType=organism+part&filter=required:[none],ontologies:[uberon]
```

which returns `UBERON:0002107` and related terms with `confidence: HIGH|GOOD` and
`evidence: ZOOMA_INFERRED_FROM_CURATED`. Worth trying when OLS search fails on lab shorthand,
because it has seen how curators mapped that exact string before.

**OxO** (`https://www.ebi.ac.uk/spot/oxo/api/...`) is **retired**. It returns an HTML upgrade
notice with HTTP **200**, so a naive `curl | jq` fails confusingly rather than cleanly. For
cross-ontology mappings use the `annotation.database_cross_reference` list on the term detail
(`UBERON:0002107` carries MESH, NCIT, FMA, UMLS, EFO, and others) or a published SSSOM mapping set.

### `references/ontology-registry.md`

# Ontology registry

Which ontology owns which kind of term, what OLS calls it, and a branch root to constrain against.
Every ontology id and branch label below was resolved against OLS in July 2026.

## Prefix to OLS ontology id

The OLS ontology id is almost always the lowercased CURIE prefix. Note the exceptions.

| CURIE prefix | OLS id | Covers |
| --- | --- | --- |
| `UBERON` | `uberon` | Anatomy, tissues, organs, body fluids (cross-species) |
| `CL` | `cl` | Cell types |
| `CLO` | `clo` | Cell lines |
| `MONDO` | `mondo` | Diseases (the merged disease ontology; prefer over DOID/NCIT) |
| `DOID` | `doid` | Human Disease Ontology (largely subsumed by MONDO) |
| `HP` | `hp` | Human phenotypic abnormalities — **id is `hp`, not `hpo`** |
| `EFO` | `efo` | Experimental factors, assays, platforms, cell lines |
| `CHEBI` | `chebi` | Chemical entities, drugs, metabolites |
| `NCBITaxon` | `ncbitaxon` | Organisms |
| `GO` | `go` | Biological process, molecular function, cellular component |
| `OBI` | `obi` | Assays, devices, protocols, study design |
| `PATO` | `pato` | Qualities — sex, colour, magnitude, `normal` |
| `SO` | `so` | Sequence features |
| `HsapDv` | `hsapdv` | Human developmental stages |
| `MmusDv` | `mmusdv` | Mouse developmental stages |
| `ENVO` | `envo` | Environmental materials and biomes |
| `FOODON` | `foodon` | Food |
| `NCIT` | `ncit` | NCI Thesaurus (clinical/oncology breadth) |
| `MS` | `ms` | Mass spectrometry instruments and methods |
| `BAO` | `bao` | BioAssay descriptions |
| `Orphanet` | **`ordo`** | Rare diseases — id is `ordo`, prefix in CURIEs is `Orphanet`, and OLS reports `preferredPrefix: ORDO` |

Not in OLS at all: **Cellosaurus** (cell line identity, RRID `CVCL_*`) — query
`https://api.cellosaurus.org` instead. Vendor and instrument vocabularies generally are not there
either.

## Branch roots for constraint checks

Pass these to `--branch` to assert a term is the right *kind* of thing.

| Root | Label | Use for |
| --- | --- | --- |
| `UBERON:0001062` | anatomical entity | any anatomy |
| `UBERON:0000465` | material anatomical entity | tissues and organs |
| `CL:0000000` | cell | cell types |
| `MONDO:0700096` | human disease | human disease fields |
| `HP:0000118` | Phenotypic abnormality | phenotype fields |
| `CHEBI:24431` | chemical entity | compounds |
| `NCBITaxon:1` | root | organisms |
| `OBI:0000070` | assay | assay fields |
| `PATO:0000001` | quality | qualities including sex |
| `GO:0008150` | biological_process | GO BP only |
| `GO:0003674` | molecular_function | GO MF only |
| `GO:0005575` | cellular_component | GO CC only |
| `EFO:0000001` | experimental factor | EFO breadth |
| `SO:0000110` | sequence_feature | sequence features |
| `HsapDv:0000001` | life cycle | human developmental stage |
| `MmusDv:0000001` | life cycle | mouse developmental stage |
| `ENVO:00010483` | environmental material | environmental samples |
| `CLO:0000031` | cell line | cell lines |
| `NCIT:C7057` | Disease, Disorder or Finding | NCIT disease subtree |
| `DOID:4` | disease | DOID subtree |

`MONDO:0000001` resolves (label `disease`) but only through the IRI fallback described in
`ols4-api.md`; prefer `MONDO:0700096` as a human-disease root.

A branch check does not substitute for a prefix check. CARO places `cell` under
`anatomical structure`, so cell types pass an anatomy branch test. Constrain both.

## Choosing between overlapping ontologies

- **Disease: MONDO.** It is the merge target for DOID, Orphanet, OMIM, and NCIT disease terms, and
  it carries cross-references back to all of them. Use DOID or NCIT only when a downstream
  consumer demands that namespace.
- **Disease vs phenotype.** MONDO for the diagnosis (`asthma`), HP for the observed abnormality
  (`Wheezing`). Metadata fields usually want one or the other, not either.
- **Tissue vs cell type.** UBERON for the sample's anatomical origin, CL for what the cells are.
  `liver` is UBERON, `hepatocyte` is CL — even though a search for `hepatocyte` restricted to
  `uberon` will return the CL term as an imported copy.
- **Assay: EFO first, OBI second.** Genomics platforms and library strategies are richer in EFO;
  OBI is better for general laboratory assay classes.
- **Chemicals: ChEBI** for anything with a structure. Drug products by trade name belong in
  a drug vocabulary (RxNorm, DrugBank), not ChEBI.
- **Sex: PATO** (`PATO:0000384` male, `PATO:0000383` female). Not NCIT, not free text.
- **"Normal" / healthy control:** `PATO:0000461` (`normal`) is the conventional filler for a
  disease field with no disease, and is what several submission schemas require.

## Common metadata fields and their expected ontology

Field names differ per archive, but the ontology behind each concept is stable:

| Concept | Ontology |
| --- | --- |
| tissue / organ / anatomical site | UBERON |
| cell type | CL |
| cell line | CLO, or Cellosaurus for identity and contamination status |
| disease | MONDO (`PATO:0000461` when none) |
| phenotype | HP |
| organism | NCBITaxon |
| assay / platform | EFO |
| developmental stage | HsapDv, MmusDv |
| sex | PATO |
| chemical / treatment compound | ChEBI |
| environmental material | ENVO |

Submission schemas — CELLxGENE, HCA, ENA/BioSamples checklists, ISA-Tab configurations — pin both
the field names and the permitted ontologies, and they revise them. Read the schema version the
submission targets rather than relying on this table or on memory; the ontology choices above are
the stable part, the field names are not.

### `scripts/ols_client.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Minimal EBI OLS4 client plus the pure helpers the two CLIs share.

Standard library only. Network access to https://www.ebi.ac.uk/ols4 is required
for the request functions; every helper below the ``--- pure helpers ---`` mark
is offline and independently testable.

Design notes that matter for correctness (all verified against the live API):

* ``/search`` with ``exact=true`` is exact *token* matching, not exact label
  matching. Restricting ``queryFields`` to ``label`` (or ``label,synonym``) is
  what makes a match exact. See ``references/ols4-api.md``.
* ``/search`` never returns ``is_obsolete`` or ``term_replaced_by``, even when
  they are named in ``fieldList``. Only the term-detail endpoint carries them.
* IRIs are never constructed here. ``http://purl.obolibrary.org/obo/{PREFIX}_{id}``
  is wrong for EFO and Orphanet, so ``iri_for()`` asks the API instead.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Iterable

OLS_BASE = "https://www.ebi.ac.uk/ols4/api"
USER_AGENT = "scientific-agent-skills-ontology-term-resolution/1.0"
TIMEOUT = 30
MAX_ATTEMPTS = 3
RETRY_STATUS = {429, 500, 502, 503, 504}

# Fields worth asking for on /search. `synonym` is the only synonym field name
# `fieldList` honours -- `exact_synonym` is silently dropped.
SEARCH_FIELDS = "obo_id,label,synonym,ontology_name,is_defining_ontology,type,short_form"

# OLS ontology ids that are not simply the lowercased CURIE prefix.
ONTOLOGY_ID_OVERRIDES = {
    "orphanet": "ordo",
}

# IRI templates for prefixes that do not live under the OBO PURL namespace.
# Only used by the term-detail fallback below, never to mint an IRI we then
# trust: a wrong guess simply resolves to nothing.
IRI_TEMPLATES = {
    "efo": "http://www.ebi.ac.uk/efo/EFO_{local}",
    "orphanet": "http://www.orpha.net/ORDO/Orphanet_{local}",
}
DEFAULT_IRI_TEMPLATE = "http://purl.obolibrary.org/obo/{prefix}_{local}"


class OlsError(RuntimeError):
    """A request to OLS failed in a way the caller cannot paper over."""


def _request(path: str, params: dict[str, Any] | None = None) -> dict:
    """GET a JSON document from OLS, retrying transient failures."""
    url = f"{OLS_BASE}/{path.lstrip('/')}"
    if params:
        clean = {k: v for k, v in params.items() if v is not None}
        url = f"{url}?{urllib.parse.urlencode(clean)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    last: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise
            last = exc
            if exc.code not in RETRY_STATUS:
                break
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = exc
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(1.5 * (attempt + 1))
    raise OlsError(f"OLS request failed after {MAX_ATTEMPTS} attempts: {url} ({last})")


def search(
    text: str,
    *,
    ontology: str | None = None,
    query_fields: str | None = "label,synonym",
    exact: bool = True,
    subtree_iri: str | None = None,
    rows: int = 10,
    include_obsolete: bool = False,
) -> list[dict]:
    """Search OLS and return the raw ``response.docs`` list.

    ``query_fields=None`` widens the search to every indexed field, which is how
    a fuzzy fallback is spelled. Obsolete terms are excluded unless asked for.
    """
    docs = _request(
        "search",
        {
            "q": text,
            "ontology": ontology,
            "queryFields": query_fields,
            "exact": "true" if exact else None,
            "allChildrenOf": subtree_iri,
            "rows": rows,
            "obsoletes": "true" if include_obsolete else None,
            "fieldList": SEARCH_FIELDS,
        },
    )
    return docs.get("response", {}).get("docs", [])


def candidate_iris(curie: str) -> list[str]:
    """IRIs a CURIE might correspond to, for the term-detail fallback."""
    match = CURIE_RE.match(curie.strip())
    if not match:
        return []
    prefix, local = match.group(1), match.group(2)
    template = IRI_TEMPLATES.get(prefix.lower())
    if template:
        return [template.format(prefix=prefix, local=local)]
    return [DEFAULT_IRI_TEMPLATE.format(prefix=prefix, local=local)]


def _terms_by_iri(iri: str) -> list[dict]:
    """Every copy of a term across ontologies, looked up by IRI."""
    try:
        payload = _request("terms", {"iri": iri, "size": 100})
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise OlsError(f"OLS returned HTTP {exc.code} for {iri}") from exc
    return payload.get("_embedded", {}).get("terms", [])


def term_detail(curie: str) -> dict | None:
    """Fetch the authoritative copy of a term by CURIE, or None if unknown.

    This is the only endpoint that reports ``is_obsolete`` and
    ``term_replaced_by``, so validation must come through here.

    Two lookups are needed. The ``obo_id`` index is preferred, but it has holes:
    ``MONDO:0000001`` is defined by MONDO and imported by eleven other
    ontologies, yet no document indexes its ``obo_id``, so the direct query
    returns nothing. Falling back to an IRI lookup turns that false ``not_found``
    into a correct answer. The returned dict carries ``_resolved_via`` and
    ``_home_ontology`` so callers can tell the two paths apart.
    """
    ontology = curie_to_ontology_id(curie)
    if not ontology:
        return None

    try:
        payload = _request(f"ontologies/{ontology}/terms", {"obo_id": curie})
        terms = payload.get("_embedded", {}).get("terms", [])
        if terms:
            found = dict(terms[0])
            found["_resolved_via"] = "obo_id"
            found["_home_ontology"] = ontology
            return found
    except urllib.error.HTTPError as exc:
        if exc.code != 404:
            raise OlsError(f"OLS returned HTTP {exc.code} for {curie}") from exc

    copies: list[dict] = []
    for iri in candidate_iris(curie):
        copies.extend(_terms_by_iri(iri))
    if not copies:
        return None

    home = [c for c in copies if c.get("ontology_name") == ontology]
    defining = [c for c in copies if c.get("is_defining_ontology")]
    best = (
        next((c for c in home if c.get("is_defining_ontology")), None)
        or (home[0] if home else None)
        or (defining[0] if defining else None)
        or copies[0]
    )
    found = dict(best)
    found["_resolved_via"] = "iri"
    found["_home_ontology"] = ontology
    return found


def iri_for(curie: str) -> str | None:
    """Resolve a CURIE to its IRI via the API rather than by string templating."""
    term = term_detail(curie)
    return term.get("iri") if term else None


def ancestor_curies(curie: str) -> set[str]:
    """Return every hierarchical ancestor of a term as a set of CURIEs."""
    term = term_detail(curie)
    if not term:
        return set()
    href = (
        term.get("_links", {})
        .get("hierarchicalAncestors", {})
        .get("href")
    )
    if not href:
        return set()
    found: set[str] = set()
    url = f"{href}{'&' if '?' in href else '?'}size=500"
    while url:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                payload = json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                break
            raise OlsError(f"ancestor lookup failed for {curie}: HTTP {exc.code}") from exc
        for entry in payload.get("_embedded", {}).get("terms", []):
            if entry.get("obo_id"):
                found.add(entry["obo_id"])
        url = payload.get("_links", {}).get("next", {}).get("href")
    return found


# --- pure helpers -----------------------------------------------------------

CURIE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_.]*):([A-Za-z0-9_.\-]+)$")


def is_curie(value: str) -> bool:
    """True for ``PREFIX:local`` strings, false for IRIs, labels, and junk."""
    return bool(CURIE_RE.match(value.strip()))


def curie_to_ontology_id(curie: str) -> str | None:
    """Map a CURIE to the OLS ontology id that defines it.

    Lowercasing the prefix is right for almost every ontology; the exceptions
    live in ``ONTOLOGY_ID_OVERRIDES`` (``Orphanet:558`` is served by ``ordo``).
    """
    match = CURIE_RE.match(curie.strip())
    if not match:
        return None
    prefix = match.group(1).lower()
    return ONTOLOGY_ID_OVERRIDES.get(prefix, prefix)


def iri_to_curie(iri: str) -> str | None:
    """Convert a term IRI to a CURIE by splitting on the final underscore.

    Handles the three IRI shapes in use -- OBO PURLs, EFO's own namespace, and
    Orphanet's -- plus multi-underscore prefixes such as ``APOLLO_SV_00000001``.
    """
    if not iri:
        return None
    tail = iri.rstrip("/").rsplit("/", 1)[-1]
    if "#" in tail:
        tail = tail.rsplit("#", 1)[-1]
    if "_" not in tail:
        return None
    prefix, local = tail.rsplit("_", 1)
    if not prefix or not local:
        return None
    return f"{prefix}:{local}"


def normalize_label(text: str) -> str:
    """Fold case and whitespace for label comparison, changing nothing else.

    Deliberately conservative: hyphens, Greek letters, and digits carry meaning
    in ontology labels, so only case and spacing are normalised.
    """
    return re.sub(r"\s+", " ", text.strip()).casefold()


def synonyms_of(doc: dict) -> list[str]:
    """Collect synonyms from a search doc or a term-detail doc.

    ``/search`` returns them under ``synonym`` when requested via ``fieldList``
    and under ``exact_synonyms`` / ``related_synonyms`` otherwise; term detail
    uses ``synonyms``.
    """
    collected: list[str] = []
    for key in ("synonym", "synonyms", "exact_synonyms", "related_synonyms"):
        value = doc.get(key)
        if isinstance(value, str):
            collected.append(value)
        elif isinstance(value, Iterable):
            collected.extend(str(item) for item in value)
    return collected


def match_type(query: str, doc: dict) -> str:
    """Classify how a hit matched: exact_label, exact_synonym, or partial.

    OLS ranks partial hits alongside exact ones, so the caller -- not the
    server -- decides whether a match is exact.
    """
    target = normalize_label(query)
    if normalize_label(doc.get("label") or "") == target:
        return "exact_label"
    if any(normalize_label(s) == target for s in synonyms_of(doc)):
        return "exact_synonym"
    return "partial"


def dedupe_candidates(docs: list[dict]) -> list[dict]:
    """Collapse repeats of the same term, keeping the defining ontology's copy.

    A search for ``liver`` returns ``UBERON:0002107`` once per ontology that
    imports it. Only the copy with ``is_defining_ontology`` is canonical.
    """
    best: dict[str, dict] = {}
    order: list[str] = []
    for doc in docs:
        key = doc.get("obo_id") or doc.get("iri") or doc.get("short_form")
        if not key:
            continue
        if key not in best:
            best[key] = doc
            order.append(key)
        elif doc.get("is_defining_ontology") and not best[key].get("is_defining_ontology"):
            best[key] = doc
    return [best[key] for key in order]


def rank_candidates(query: str, docs: list[dict]) -> list[dict]:
    """Annotate hits with ``match_type`` and sort exact matches to the front.

    Within a match tier the server's relevance order is preserved, and terms
    from their defining ontology outrank imported copies.
    """
    tier = {"exact_label": 0, "exact_synonym": 1, "partial": 2}
    annotated = []
    for position, doc in enumerate(dedupe_candidates(docs)):
        enriched = dict(doc)
        enriched["match_type"] = match_type(query, doc)
        annotated.append((tier[enriched["match_type"]], 0 if doc.get("is_defining_ontology") else 1, position, enriched))
    annotated.sort(key=lambda row: row[:3])
    return [row[3] for row in annotated]
```

### `scripts/resolve_terms.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve free-text labels to ontology terms via EBI OLS4.

Never emit an ontology ID from memory -- run this instead. Each input string is
searched with an escalating strategy and every returned candidate is labelled
with how it actually matched, so a partial hit can never be mistaken for an
exact one.

Strategies, tried in order until one returns candidates:

    exact       exact=true restricted to label and synonym fields
    token       exact=true across all indexed fields (whole-word match)
    fulltext    unrestricted relevance search

Examples:
    # single term, constrained to the ontology that should define it
    uv run resolve_terms.py "liver" --ontology uberon

    # a column of tissue names, requiring anatomical entities only
    uv run resolve_terms.py --input tissues.txt \\
        --ontology uberon --branch UBERON:0000465 --format tsv -o resolved.tsv

    # accept exact matches only; unresolved rows are reported, not guessed
    uv run resolve_terms.py "kidney cortex" "left ventrical" --exact-only
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ols_client import (  # noqa: E402
    OlsError,
    iri_for,
    is_curie,
    rank_candidates,
    search,
)

STRATEGIES = (
    ("exact", {"exact": True, "query_fields": "label,synonym"}),
    ("token", {"exact": True, "query_fields": None}),
    ("fulltext", {"exact": False, "query_fields": None}),
)

TSV_COLUMNS = (
    "query",
    "rank",
    "curie",
    "label",
    "ontology",
    "match_type",
    "strategy",
    "defining_ontology",
)


def read_inputs(args: argparse.Namespace) -> list[str]:
    """Collect query strings from positional args, a file, or stdin."""
    values: list[str] = list(args.text)
    if args.input:
        raw = (
            sys.stdin.read()
            if args.input == "-"
            else Path(args.input).read_text(encoding="utf-8")
        )
        for line in raw.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                values.append(line)
    if not values and not sys.stdin.isatty():
        for line in sys.stdin.read().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                values.append(line)
    # Preserve order, drop duplicates.
    seen: set[str] = set()
    unique = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def resolve_one(
    text: str,
    *,
    ontology: str | None,
    subtree_iri: str | None,
    rows: int,
    exact_only: bool,
) -> dict:
    """Run the strategy ladder for one string and return ranked candidates."""
    strategies = STRATEGIES[:1] if exact_only else STRATEGIES
    for name, options in strategies:
        docs = search(
            text,
            ontology=ontology,
            subtree_iri=subtree_iri,
            rows=rows,
            **options,
        )
        ranked = rank_candidates(text, docs)
        if ranked:
            return {"query": text, "strategy": name, "candidates": ranked[:rows]}
    return {"query": text, "strategy": strategies[-1][0], "candidates": []}


def to_rows(results: list[dict]) -> list[dict]:
    """Flatten results into one row per candidate, or one row if unresolved."""
    rows: list[dict] = []
    for result in results:
        if not result["candidates"]:
            rows.append(
                {
                    "query": result["query"],
                    "rank": 1,
                    "curie": "",
                    "label": "",
                    "ontology": "",
                    "match_type": "unresolved",
                    "strategy": result["strategy"],
                    "defining_ontology": "",
                }
            )
            continue
        for position, candidate in enumerate(result["candidates"], start=1):
            rows.append(
                {
                    "query": result["query"],
                    "rank": position,
                    "curie": candidate.get("obo_id", ""),
                    "label": candidate.get("label", ""),
                    "ontology": candidate.get("ontology_name", ""),
                    "match_type": candidate["match_type"],
                    "strategy": result["strategy"],
                    "defining_ontology": str(
                        bool(candidate.get("is_defining_ontology"))
                    ).lower(),
                }
            )
    return rows


def write_output(results: list[dict], fmt: str, output: str | None) -> None:
    """Emit TSV or JSON to a path or stdout."""
    stream = open(output, "w", encoding="utf-8", newline="") if output else sys.stdout
    try:
        if fmt == "json":
            json.dump(results, stream, indent=2)
            stream.write("\n")
        else:
            writer = csv.DictWriter(
                stream, fieldnames=TSV_COLUMNS, delimiter="\t", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(to_rows(results))
    finally:
        if output:
            stream.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve free-text labels to ontology terms via EBI OLS4.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", nargs="*", help="strings to resolve")
    parser.add_argument(
        "--input",
        help="file with one string per line ('-' for stdin); # lines are comments",
    )
    parser.add_argument(
        "--ontology",
        help="restrict to OLS ontology ids, comma separated (e.g. uberon,cl)",
    )
    parser.add_argument(
        "--branch",
        help="require candidates to be descendants of this CURIE (e.g. UBERON:0000465)",
    )
    parser.add_argument(
        "--top", type=int, default=5, help="candidates to report per query (default 5)"
    )
    parser.add_argument(
        "--exact-only",
        action="store_true",
        help="only exact label/synonym matches; report anything else as unresolved",
    )
    parser.add_argument(
        "--format", choices=("tsv", "json"), default="tsv", help="output format"
    )
    parser.add_argument("-o", "--output", help="write here instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    queries = read_inputs(args)
    if not queries:
        print("No input strings given. See --help.", file=sys.stderr)
        return 2

    subtree_iri = None
    if args.branch:
        if not is_curie(args.branch):
            print(f"--branch expects a CURIE, got {args.branch!r}", file=sys.stderr)
            return 2
        try:
            subtree_iri = iri_for(args.branch)
        except OlsError as exc:
            print(f"Could not resolve --branch {args.branch}: {exc}", file=sys.stderr)
            return 2
        if not subtree_iri:
            print(f"--branch term not found in OLS: {args.branch}", file=sys.stderr)
            return 2

    results = []
    for query in queries:
        try:
            results.append(
                resolve_one(
                    query,
                    ontology=args.ontology,
                    subtree_iri=subtree_iri,
                    rows=args.top,
                    exact_only=args.exact_only,
                )
            )
        except OlsError as exc:
            print(f"OLS lookup failed for {query!r}: {exc}", file=sys.stderr)
            return 2

    write_output(results, args.format, args.output)

    unresolved = [r["query"] for r in results if not r["candidates"]]
    if unresolved:
        print(
            f"{len(unresolved)}/{len(results)} unresolved: "
            + ", ".join(repr(q) for q in unresolved[:10]),
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_terms.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate ontology CURIEs against EBI OLS4 before they leave the machine.

This is the gate that catches invented IDs. For each term it reports whether the
ID exists at all, whether it has been obsoleted (and what replaced it), whether a
claimed label actually belongs to it, and optionally whether it sits in the
branch and ontology the metadata field requires.

Statuses: ``ok`` and ``matched_synonym`` pass, ``not_found``, ``obsolete``,
``label_mismatch``, ``wrong_branch``, ``wrong_ontology`` fail, and
``not_a_class`` warns. Exit code is 1 if anything failed, 0 otherwise, 2 on
usage or network trouble. ``--strict`` promotes warnings to failures.

Examples:
    # spot-check three IDs
    uv run validate_terms.py UBERON:0002107 CL:0000182 UBERON:9999999

    # verify id/label pairs a pipeline wrote, as a CI gate
    uv run validate_terms.py --input metadata.tsv --strict

    # a tissue column must hold anatomical entities from UBERON
    uv run validate_terms.py --input tissue_ids.tsv \\
        --branch UBERON:0000465 --expect-ontology uberon
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ols_client import (  # noqa: E402
    OlsError,
    ancestor_curies,
    is_curie,
    iri_to_curie,
    normalize_label,
    synonyms_of,
    term_detail,
)

FAIL_STATUSES = {
    "not_found",
    "obsolete",
    "label_mismatch",
    "wrong_branch",
    "wrong_ontology",
    "malformed_curie",
}
WARN_STATUSES = {"not_a_class", "matched_synonym", "imported_only"}

TSV_COLUMNS = ("id", "status", "actual_label", "ontology", "replacement", "detail")

ID_HEADERS = {"id", "curie", "term_id", "ontology_term_id", "obo_id"}
LABEL_HEADERS = {"label", "term_label", "name", "ontology_term_label"}


def read_pairs(args: argparse.Namespace) -> list[tuple[str, str | None]]:
    """Collect (curie, expected_label) pairs from positional args or a file."""
    pairs: list[tuple[str, str | None]] = [(value, None) for value in args.term]
    if not args.input:
        return pairs

    raw = (
        sys.stdin.read()
        if args.input == "-"
        else Path(args.input).read_text(encoding="utf-8")
    )
    lines = [line for line in raw.splitlines() if line.strip()]
    if not lines:
        return pairs

    delimiter = "\t" if "\t" in lines[0] else ","
    rows = list(csv.reader(lines, delimiter=delimiter))
    header = [cell.strip().lower() for cell in rows[0]]
    id_index, label_index = 0, 1

    if any(cell in ID_HEADERS for cell in header):
        id_index = next(i for i, cell in enumerate(header) if cell in ID_HEADERS)
        label_index = next(
            (i for i, cell in enumerate(header) if cell in LABEL_HEADERS), None
        )
        rows = rows[1:]

    for row in rows:
        if not row or not row[id_index].strip():
            continue
        curie = row[id_index].strip()
        if curie.startswith("#"):
            continue
        label = None
        if label_index is not None and len(row) > label_index:
            label = row[label_index].strip() or None
        pairs.append((curie, label))
    return pairs


def check_term(
    curie: str,
    expected_label: str | None,
    *,
    branch: str | None,
    expect_ontologies: set[str] | None,
) -> dict:
    """Validate one CURIE and return a result record."""
    result = {
        "id": curie,
        "status": "ok",
        "actual_label": "",
        "ontology": "",
        "replacement": "",
        "detail": "",
    }

    if not is_curie(curie):
        result["status"] = "malformed_curie"
        result["detail"] = "not of the form PREFIX:local"
        return result

    term = term_detail(curie)
    if term is None:
        result["status"] = "not_found"
        result["detail"] = "no such term in the ontology this prefix names"
        return result

    result["actual_label"] = term.get("label") or ""
    result["ontology"] = term.get("ontology_name") or ""

    if term.get("is_obsolete"):
        replacement = iri_to_curie(term.get("term_replaced_by") or "") or ""
        result["status"] = "obsolete"
        result["replacement"] = replacement
        result["detail"] = (
            f"obsolete; replaced by {replacement}"
            if replacement
            else "obsolete with no stated replacement"
        )
        return result

    if expect_ontologies and result["ontology"] not in expect_ontologies:
        result["status"] = "wrong_ontology"
        result["detail"] = (
            f"defined by {result['ontology']!r}, expected one of "
            + ",".join(sorted(expect_ontologies))
        )
        return result

    warnings: list[tuple[str, str]] = []

    if expected_label is not None:
        wanted = normalize_label(expected_label)
        if normalize_label(result["actual_label"]) != wanted:
            if any(normalize_label(s) == wanted for s in synonyms_of(term)):
                warnings.append(
                    (
                        "matched_synonym",
                        f"{expected_label!r} is a synonym; primary label is "
                        f"{result['actual_label']!r}",
                    )
                )
            else:
                result["status"] = "label_mismatch"
                result["detail"] = (
                    f"claimed {expected_label!r}, actual {result['actual_label']!r}"
                )
                return result

    if branch:
        ancestors = ancestor_curies(curie)
        if branch not in ancestors and branch != curie:
            result["status"] = "wrong_branch"
            result["detail"] = f"not a descendant of {branch}"
            return result

    # An ID no ontology asserts, surviving only as a copy inside importers, is
    # stale even though it resolves. Curators reject these.
    home = term.get("_home_ontology")
    if not term.get("is_defining_ontology") and result["ontology"] != home:
        warnings.append(
            (
                "imported_only",
                f"{home} does not define this term; found only as a copy in "
                f"{result['ontology']!r}",
            )
        )

    if term.get("type") not in (None, "class"):
        warnings.append(
            ("not_a_class", f"term type is {term.get('type')!r}, not a class")
        )

    if warnings:
        order = {"imported_only": 0, "not_a_class": 1, "matched_synonym": 2}
        warnings.sort(key=lambda item: order[item[0]])
        result["status"] = warnings[0][0]
        result["detail"] = "; ".join(detail for _, detail in warnings)

    return result


def write_output(results: list[dict], fmt: str, output: str | None) -> None:
    """Emit TSV or JSON to a path or stdout."""
    stream = open(output, "w", encoding="utf-8", newline="") if output else sys.stdout
    try:
        if fmt == "json":
            json.dump(results, stream, indent=2)
            stream.write("\n")
        else:
            writer = csv.DictWriter(
                stream, fieldnames=TSV_COLUMNS, delimiter="\t", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(results)
    finally:
        if output:
            stream.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate ontology CURIEs against EBI OLS4.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("term", nargs="*", help="CURIEs to validate")
    parser.add_argument(
        "--input",
        help="TSV/CSV with an id column and an optional label column ('-' for stdin)",
    )
    parser.add_argument(
        "--branch", help="require every term to be a descendant of this CURIE"
    )
    parser.add_argument(
        "--expect-ontology",
        help="comma-separated OLS ontology ids every term must come from",
    )
    parser.add_argument(
        "--strict", action="store_true", help="treat warnings as failures"
    )
    parser.add_argument(
        "--format", choices=("tsv", "json"), default="tsv", help="output format"
    )
    parser.add_argument("-o", "--output", help="write here instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pairs = read_pairs(args)
    if not pairs:
        print("No terms given. See --help.", file=sys.stderr)
        return 2

    if args.branch and not is_curie(args.branch):
        print(f"--branch expects a CURIE, got {args.branch!r}", file=sys.stderr)
        return 2

    expect_ontologies = (
        {value.strip().lower() for value in args.expect_ontology.split(",") if value.strip()}
        if args.expect_ontology
        else None
    )

    results = []
    for curie, label in pairs:
        try:
            results.append(
                check_term(
                    curie,
                    label,
                    branch=args.branch,
                    expect_ontologies=expect_ontologies,
                )
            )
        except OlsError as exc:
            print(f"OLS lookup failed for {curie}: {exc}", file=sys.stderr)
            return 2

    write_output(results, args.format, args.output)

    failed = [r for r in results if r["status"] in FAIL_STATUSES]
    warned = [r for r in results if r["status"] in WARN_STATUSES]
    summary = f"{len(results)} checked, {len(failed)} failed, {len(warned)} warned"
    print(summary, file=sys.stderr)
    if failed or (args.strict and warned):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
