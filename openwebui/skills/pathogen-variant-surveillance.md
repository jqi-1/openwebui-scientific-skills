---
name: pathogen-variant-surveillance
description: Query live pathogen genomic surveillance data through the GenSpectrum LAPIS API to find which viral lineages are circulating now, how fast they are growing, and what mutations they carry. Use whenever a question depends on the current state of a pathogen population rather than on remembered facts - which SARS-CoV-2 variant is dominant, whether a Pango lineage is still designated or has been withdrawn, what clade or genotype of H5N1 is in a host or region, whether a PCR primer or assay target still matches circulating sequence, or how a lineage's prevalence has moved week to week. Triggers include "variant surveillance", "genomic surveillance", "what variant is circulating", "dominant variant", "Pango lineage", "lineage prevalence", "growth advantage", "SARS-CoV-2 variant", "XFG", "clade 2.3.4.4b", "H5N1 genotype", "influenza clade", "RSV/mpox/measles/dengue lineage", "CoV-Spectrum", "LAPIS", "Nextclade", "pango-designation", and any request to report what a pathogen population looks like today.
---

# Pathogen Variant Surveillance

## When to use

Any time an answer depends on what a pathogen population looks like **now**: which lineages are
circulating, whether one is growing, what a lineage name currently means, or whether an assay
target still matches.

## The rule

**Never state what is circulating, and never write a lineage name, from memory.**

Three things go wrong at once, and only the first is an ordinary knowledge-cutoff problem:

1. **Names post-date training.** The Pango designation list carries over 6,200 names and grows
   continuously.
2. **The nomenclature is a live data structure, not a convention.** `XFG` is a recombinant that
   only resolves through `alias_key.json`; `PQ.17` unaliases to `XDV.1.5.1.1.8.1.17`. Neither
   expansion is derivable by reasoning — the mapping is a file that changes.
3. **Prior knowledge gets retracted, not just outdated.** 294 names in the current
   `lineage_notes.txt` are withdrawn or redesignated. `PC.2` is now `LF.7.9`; `XFG.20` was
   withdrawn outright. A remembered lineage fact is not merely stale, it can be actively wrong.

Every number this skill reports is a count returned by a live instance, stamped with the data
version it came from.

## Scope

Surveillance data analysis for research. This skill describes sequences that were collected and
submitted; it does not produce clinical interpretations, outbreak-response recommendations, or
public-health guidance, and sequence counts are not case counts.

## Instances

One API shape covers every pathogen. `--instance` names a verified deployment; `--base-url`
reaches any other LAPIS instance.

| Instance | Host | Lineage column | Indexed |
| --- | --- | --- | --- |
| `sars-cov-2` | lapis.cov-spectrum.org (open GenBank data) | `pangoLineage` | yes |
| `h5n1`, `h3n2`, `h1n1pdm`, `influenza-a` | lapis.genspectrum.org | `clade` | no |
| `rsv-a`, `rsv-b`, `mpox`, `measles`, `dengue`, `west-nile`, `hmpv`, `ebola-zaire`, `ebola-sudan`, `cchf` | lapis.pathoplexus.org | varies | varies |

**Field names differ per instance and are never assumed.** Every script reads
`/sample/databaseConfig` at run time and picks the collection-date, submission-date and lineage
columns from what the instance actually declares. `dateFrom=` is correct on SARS-CoV-2 and a hard
400 on H5N1, whose collection date is `sampleCollectionDateRangeLower`.

## Scripts

```bash
cd skills/pathogen-variant-surveillance/scripts
```

| Script | Question answered |
| --- | --- |
| `resolve_lineage.py` | Does this name still exist, what does it expand to, what is it descended from? |
| `lineage_prevalence.py` | What share of sequences is this lineage, week by week, and is it growing? |
| `mutation_profile.py` | What mutations does it carry, and how does it differ from another lineage? |
| `reporting_lag.py` | How far back does the data have to go before it can be trusted? |

All four take `--format table|tsv|json` and print provenance (instance, data version, resolved
field names, filters) to stderr, so `> out.tsv` keeps the data clean and the provenance visible.

### Start from the data, not from a remembered list

```bash
# no names: discover what is actually circulating in the window
python3 lineage_prevalence.py --top 5 --where country=USA --weeks 12
```

> note: discovered the 5 most common pangoLineage values in the window:
> XFG.1.1, XFG.23.1.3, PY.1.1.1, XFJ.3.1.2, PQ.17

This is the right first command for "what is circulating". Naming lineages up front presumes you
already know which ones matter, which is the assumption this skill exists to remove.

### Check a name before using it

```bash
python3 resolve_lineage.py XFG.23.1.3 PQ.17 PC.2 NOTALINEAGE
```

```
query        status     unaliased                        parent    recombinant_of  descendants  sequences  detail
XFG.23.1.3   current    XFG.23.1.3                       XFG.23.1  LF.7+LP.8.1.2   6            317        S:A1174V, on C29137T branch
PQ.17        current    XDV.1.5.1.1.8.1.17               NB.1.8.1                  23           931        Alias of XDV.1.5.1.1.8.1.17
PC.2         withdrawn  B.1.1.529.2.86.1.1.16.1.7.2.1.2  LF.7.2.1                  4            25         now LF.7.9; Redesignated as LF.7.9
NOTALINEAGE  unknown    NOTALINEAGE                                                0            n/a        no such name in the live nomenclature
```

(`detail` abridged; each real row also cites the lineage proposal it came from.)

Exit code is 1 if any name is withdrawn or unknown, so it gates a manuscript's lineage list.
Note `PC.2`: withdrawn upstream, yet 25 sequences still carry the label because the instance's
assignments lag designation. Both facts are true and both matter.

### Prevalence and growth

```bash
python3 lineage_prevalence.py "XFG.1.1*" "XFJ*" --where country=USA --weeks 16 --growth
```

```
lineage   week        n   total  proportion  ci_low  ci_high  coverage
XFG.1.1*  2026-05-04  42  80     0.5250      0.4170  0.6308   ok
XFG.1.1*  2026-06-15  3   49     0.0612      0.0210  0.1652   ok
XFG.1.1*  2026-06-29  1   30     0.0333      0.0059  0.1667   low
XFG.1.1*  2026-07-13  0   0                                   low
```

Proportions carry Wilson intervals because surveillance weeks are small. Weeks whose denominator
has not filled in yet are flagged `low` and excluded from the growth fit unless
`--include-incomplete`.

The window is widened to whole ISO weeks, and says so when it does. A window starting mid-week
would give a first row covering three days and a last row covering four, neither comparable to the
full weeks between them.

`--growth` reports a weighted least-squares slope of log-odds against time. It is **descriptive**:
it absorbs every change in who is sequencing, where, and how fast they report. It is not a fitness
or transmissibility estimate. No slope is printed for a lineage with too few observations — see the
trap table for why that guard exists.

### Mutations, and whether an assay still matches

```bash
python3 mutation_profile.py "XFJ*" --versus "XFG*" --gene S --since 2026-01-01
```

```
mutation  gene  position  verdict  prop_a  prop_b  n_a  n_b
S:L441R   S     441       gained   1.000   0.000   66   0
S:A475V   S     475       gained   1.000   0.000   68   0
S:K444R   S     444       lost     0.000   0.996   0    5031
S:Q493E   S     493       lost     0.000   0.998   0    5359
```

Works the same on a segmented genome — `--instance h5n1 --gene HA` or `--gene seg4`. Use
`--nucleotide` for primer and probe questions, where the codon is not the unit that matters.

### Decide how far back to trust

```bash
python3 reporting_lag.py --where country=USA
```

```
lag_days  mean_complete  min_complete  max_complete  cohorts
14        0.456          0.332         0.557         6
30        0.677          0.580         0.822         6
60        0.868          0.802         0.949         6
90        0.939          0.916         1.000         6
```

> 90% of a cohort has arrived by 90 days. Trust collection dates up to 2026-04-28; treat anything
> later as provisional.

Run this **before** quoting any recent prevalence. The curve differs sharply by pathogen and
country: on H5N1 the same measurement returns 0% complete at 14 days and 15% at 30 days, so a
"current" H5N1 picture is effectively blind for two months.

## Traps that produce silently wrong answers

All verified against the live API on 2026-07-27. These are why this skill ships scripts rather
than a recipe; full detail in `references/lapis-api.md`.

| Trap | Consequence |
| --- | --- |
| A bare lineage name excludes its descendants | `pangoLineage=XFG` returns 4 sequences; `XFG*` returns 640 |
| A trailing `*` needs a lineage index | On H5N1 `clade=2.3.4.4b` returns 62,413 and `clade=2.3.4.4b*` returns **0** — the same syntax, the opposite meaning |
| Field names are per-instance | `dateFrom` is a 400 on H5N1; the collection date is `sampleCollectionDateRangeLower` |
| Only `date`-typed fields take ranges | H5N1 types `sampleCollectionDate` as a string, so it has no `From`/`To` keys at all |
| Recent weeks are not a sample of what circulated | They are a sample of whoever reports fastest; only 29% of a US cohort arrives within 7 days |
| LAPIS roots recombinants | Asking it for `XFG`'s parents returns nothing; only `alias_key.json` records `XFG = LF.7 + LP.8.1.2` |
| Withdrawn names persist in the data | `PC.2` was redesignated `LF.7.9` upstream while sequences still carry `PC.2` |
| An unknown name fails loudly only when indexed | Indexed columns reject a typo with a 400; unindexed columns answer `0` |
| Mutation `proportion` is over `coverage` | Not over all matching sequences — a poorly covered site can show 1.000 on very few reads |
| `/sample/aggregated` rejects `limit`/`orderBy` | The result has no inherent ordering; sort client-side |

## Reporting results

State the instance, the data version, the filters, and the window — a prevalence figure without
them cannot be reproduced, because the underlying database changes daily. Give counts alongside
proportions, quote the interval, and say explicitly when a window is too recent to support an
estimate. "No reliable estimate for the last six weeks" is a legitimate and often correct answer.

## References

- `references/lapis-api.md` — endpoints, filter grammar, per-instance schema differences, the
  instance registry, and every verified trap in full.
- `references/lineage-nomenclature.md` — Pango aliases and recombinants, designation churn,
  Nextstrain clades, WHO labels, influenza clades, H5N1 clades and genotypes, and how the naming
  systems map onto each other.
- `references/surveillance-caveats.md` — reporting lag, sampling and ascertainment bias, choosing
  a denominator, interval and growth interpretation, and the conclusions this data cannot support.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pathogen-variant-surveillance/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/lapis-api.md`

# LAPIS API reference

LAPIS (Lightweight API for Sequences) is the query layer GenSpectrum runs in front of SILO. One
API shape serves every pathogen; what differs between deployments is the **schema**, and almost
every mistake in this area comes from assuming otherwise.

Everything below was verified against the live services on 2026-07-27 (`lapisVersion 0.8.3`,
`siloVersion 0.11.2`).

## Instances

| `--instance` | Base URL | Backing data |
| --- | --- | --- |
| `sars-cov-2` | `https://lapis.cov-spectrum.org/open/v2` | Nextstrain open (GenBank) |
| `influenza-a` | `https://lapis.genspectrum.org/influenza-a` | Loculus |
| `h1n1pdm`, `h3n2`, `h5n1` | `https://lapis.genspectrum.org/<name>` | Loculus |
| `rsv-a`, `rsv-b`, `hmpv`, `measles`, `mpox`, `west-nile`, `dengue`, `ebola-zaire`, `ebola-sudan`, `cchf` | `https://lapis.pathoplexus.org/<name>` | Pathoplexus |

Approximate sizes when checked: SARS-CoV-2 open ~9M, influenza-a 1.07M, h3n2 277k, h1n1pdm 212k,
h5n1 79k, dengue 62k, measles 53k, rsv-a 53k, rsv-b 40k, west-nile 26k, mpox 17k, ebola-zaire 12k,
cchf 8.7k, ebola-sudan 636.

The registry in `scripts/lapis_client.py` is a convenience, not an authority. New organisms appear
and paths move; `--base-url` reaches any deployment, and `/sample/databaseConfig` describes it.

**Point `--base-url` only at deployments you trust.** Field names, lineage labels and error
`detail` strings are printed verbatim, so a hostile instance could put arbitrary text — including
text shaped like instructions — into agent-visible output. Responses are parsed as data and never
executed, but the strings are still read.

The pango-designation fetch is deliberately unpinned. Pinning it to a tag would make lineage
resolution reproducible and *wrong*: withdrawals and redesignations are exactly what the skill
exists to catch, and a frozen copy reintroduces the failure mode.

Auditability comes from recording what was read rather than freezing it. `raw.githubusercontent`
returns the git blob SHA as the `ETag`, so `resolve_lineage.py` prints the exact hash of both files
at no extra request:

```
# source blobs lineage_notes.txt@b63582d49216 alias_key.json@0deb39eeac80
```

Keep that line with `dataVersion`; together they pin the result without staling the source.

**GISAID.** `https://lapis.cov-spectrum.org/gisaid/v2` exists but requires credentials and its own
data-use terms. This skill targets the open instances only. Open GenBank data is a subset of
GISAID, so absolute counts here are lower than GISAID-derived figures — proportions are usually
comparable, absolute counts are not.

## Endpoints

| Path | Use |
| --- | --- |
| `GET /sample/aggregated` | Counts, optionally grouped by `fields` |
| `GET /sample/details` | Per-sequence metadata rows |
| `GET /sample/aminoAcidMutations` | AA substitutions with per-site proportions |
| `GET /sample/nucleotideMutations` | Nucleotide substitutions |
| `GET /sample/aminoAcidInsertions`, `/sample/nucleotideInsertions` | Insertions |
| `GET /sample/databaseConfig` | The schema: every metadata field and its type |
| `GET /sample/referenceGenome` | Segment and gene names for mutation queries |
| `GET /sample/lineageDefinition/{column}` | The lineage tree for an indexed column |
| `GET /sample/info` | `dataVersion` — record it with any result you keep |
| `GET /sample/unalignedNucleotideSequences`, `/sample/alignedNucleotideSequences`, `/sample/alignedAminoAcidSequences/{gene}` | FASTA download |
| `GET /sample/mostRecentCommonAncestor`, `/sample/phyloSubtree` | Tree queries where a phylo field exists |
| `POST /component/*OverTime` | Prebuilt time-series components |

Every endpoint accepts GET and POST. Filters are query parameters; unknown ones are rejected.

## Reading the schema first

`/sample/databaseConfig` returns `schema.metadata[]` with a `name`, a `type`, and
`generateLineageIndex`. Three things follow from it, and all three differ between instances:

**1. Which column holds the lineage.** `schema.metadata[].generateLineageIndex` is true for
`pangoLineage` and `nextcladePangoLineage` on SARS-CoV-2 and for nothing at all on H5N1, whose
lineage-like column is a plain string `clade`.

**2. Which date columns accept ranges.** LAPIS derives `<field>From` / `<field>To` from the
declared type. Only `date`, `int` and `float` get them.

| Instance | Collection date | Type | Range filter |
| --- | --- | --- | --- |
| `sars-cov-2` | `date` | date | `dateFrom` / `dateTo` |
| `h5n1` | `sampleCollectionDate` | **string** | none |
| `h5n1` | `sampleCollectionDateRangeLower` | date | `sampleCollectionDateRangeLowerFrom` / `...To` |

`dateFrom=2025-01-01` against H5N1 is a 400. The error body lists every valid key for that
instance, which is the fastest way to discover a schema by hand.

**3. Which submission date exists.** `dateSubmitted` on SARS-CoV-2; `ncbiReleaseDate` on H5N1
(`submittedDate` and `releasedDate` are there too, but typed string, so they cannot be ranged).

`scripts/lapis_client.py` does this resolution in `describe_instance()`, `pick_date_field()` and
`pick_lineage_field()`, and raises rather than guessing.

## Lineage filters and the wildcard

On a column with a lineage index, a trailing `*` means "this lineage and all descendants":

```
pangoLineage=XFG      ->   4 sequences   (sequences named exactly XFG)
pangoLineage=XFG*     -> 640 sequences   (XFG and every descendant)
```

On a column **without** one, `*` is matched literally and finds nothing:

```
clade=2.3.4.4b        -> 62413 sequences
clade=2.3.4.4b*       ->     0 sequences
```

Same syntax, opposite meaning, no warning either way. `lineage_filter()` refuses to build the
second query.

The index also decides how a bad name fails. On an indexed column an unknown lineage is rejected:

```
{"error":{"status":400,"detail":"Error from SILO: The lineage 'XFG.20' is not a valid lineage
 for column 'pangoLineage'."}}
```

On an unindexed column the same typo returns `0` and looks like a finding. Validate names with
`resolve_lineage.py` before reporting an absence.

### The lineage definition endpoint

`/sample/lineageDefinition/pangoLineage` returns roughly 5,500 entries of the form

```json
{"XFG.1.1": {"parents": ["XFG.1"], "aliases": ["xfg.1.1", ...]},
 "PQ.17":   {"parents": ["NB.1.8.1"], "aliases": ["NB.1.8.1.17", ...]}}
```

**It roots recombinants.** `XFG` has no `parents` key, and no entry in the whole document has more
than one parent. The recombinant parentage `XFG = LF.7 + LP.8.1.2` exists only in
pango-designation's `alias_key.json`, where a recombinant's value is a *list*. Both sources are
needed; neither is sufficient.

Requesting the endpoint for an unindexed column returns 400.

## Mutation queries

`/sample/aminoAcidMutations` rows look like:

```json
{"mutation": "S:L452W", "count": 3793, "coverage": 5211, "proportion": 0.728,
 "sequenceName": "S", "mutationFrom": "L", "mutationTo": "W", "position": 452}
```

`proportion = count / coverage`, and **`coverage` is the number of sequences that resolved that
site**, not the number matching the filter. A site covered by 12 sequences can report
`proportion: 1.000`. Always read `coverage` alongside it.

`minProportion` (default 0.05) prunes the response server-side. For a diff between two lineages,
fetch both at a low threshold and apply the reporting threshold client-side — otherwise a mutation
absent from one side is indistinguishable from one pruned out of it. `mutation_profile.py` does
exactly this.

`sequenceName` is the gene on an unsegmented genome (`S`, `ORF1a`, `N`) and the gene or segment on
a segmented one. Get the valid names from `/sample/referenceGenome`:

- SARS-CoV-2: one sequence `main`; genes `E M N ORF1a ORF1b ORF3a ORF6 ORF7a ORF7b ORF8 ORF9b S`
- H5N1: segments `seg1`–`seg8`; genes `PB2 PB1 PA PAX HA NP NA M1 M2 NS1 NS2`

Nucleotide mutations on a segmented genome must be qualified by segment (`seg4:A123G`).

## Aggregation

`fields` on `/sample/aggregated` is the **group-by**, not a projection:

```
GET /sample/aggregated?fields=pangoLineage&country=USA&dateFrom=2026-04-01
-> [{"count": 286, "pangoLineage": "XFG.1.1"}, ...]
```

`limit`, `offset` and `orderBy` are rejected here — the result has no inherent ordering:

```
"detail": "Offset and limit can only be applied if the output of the operation has some
 ordering. ... Aggregated however produces unordered results."
```

Sort client-side. There is no ISO-week grouping; group by the date field and bin weeks yourself
(`bin_weekly()`). Grouped rows carry nulls for sequences whose date was never reported — count
them separately rather than dropping them silently.

## Errors, versioning, and etiquette

Two error envelopes are in use, both carrying `detail`:

```json
{"error": {"type": "about:blank", "title": "Bad request", "status": 400, "detail": "..."},
 "info":  {"dataVersion": null, "requestId": "...", "lapisVersion": "0.8.3"}}
```

```json
{"type": "about:blank", "title": "Bad Request", "status": 400, "instance": "/open/v2/query/parse"}
```

`_error_detail()` reads both. Always surface `detail` — on a bad filter key it enumerates every
valid key for that instance.

`info.dataVersion` accompanies every successful response and identifies the underlying snapshot.
**Record it with any figure that will be quoted.** The same query returns different numbers on
different days, and without the data version a result cannot be reproduced or audited.

These are free public services with no API key. Ask for aggregates rather than per-sequence rows,
send one query per question instead of paginating through sequences, and retry `429`/`5xx` with
backoff (`MAX_ATTEMPTS = 3`, 1.5 s linear) rather than hammering.

### `references/lineage-nomenclature.md`

# Lineage nomenclature

Naming systems are not interchangeable, are not stable, and several run side by side on the same
instance. Values below were read from the live instances on 2026-07-27 and will have moved by the
time you read this — the point is the *structure*, not the specific names.

## SARS-CoV-2

Four naming systems coexist on the open instance:

| Column | Example values | What it is |
| --- | --- | --- |
| `pangoLineage` | `XFG.1.1`, `PQ.17`, `RE.2` | Pango designation; the fine-grained system |
| `nextcladePangoLineage` | same vocabulary | Nextclade's own call, assigned by a versioned dataset |
| `nextstrainClade` | `25C`, `25B`, `25I`, `recombinant` | Coarse year-plus-letter clades |
| `whoClade` | `Omicron`, mostly null | WHO Greek labels |

Two consequences worth knowing before choosing a column:

- **`nextstrainClade` collapses every recombinant into one bucket.** 627 sequences collected in
  2026 are labelled simply `recombinant`. Since the currently dominant lineages *are*
  recombinants, `nextstrainClade` cannot distinguish XFG from XFJ. Use `pangoLineage` for anything
  lineage-specific.
- **`whoClade` is effectively retired.** It is null for the large majority of 2026 sequences; no
  Greek letter has been assigned beyond Omicron. Do not expect a Greek label for a current lineage,
  and do not invent one.

### How Pango names are built

Names root at `A` or `B` and extend by dots. Once a name would exceed three numeric levels it is
**aliased** to a new letter prefix, and the alias key is the only way back:

```
PQ.17  = XDV.1.5.1.1.8.1.17
RE.2   = BA.3.2.2.2 = B.1.1.529.3.2.2.2
```

`scripts/lapis_client.py:unalias_full()` walks this using the live `alias_key.json`. There is no
way to derive it — the mapping is a file that changes.

### Recombinants

Names beginning `X` are recombinants. Their alias entry is a **list of parents**, not a path:

```json
{"XFG": ["LF.7", "LP.8.1.2"], "XFJ": ["LS.2.1.1", "LF.7.2"]}
```

LAPIS's own lineage definition does **not** carry this — it roots every `X*` lineage, and no entry
in that document has more than one parent. Ask LAPIS for `XFG`'s parents and you get nothing. Both
sources are required: LAPIS for the descendant index that queries use, `alias_key.json` for
parentage.

A recombinant's descendants alias normally (`XFG.1.1` → `XFG.1` → `XFG`), so ancestry *below* the
recombination point behaves like any other lineage.

### Designation churn

`lineage_notes.txt` currently lists ~6,230 names, of which **294 are withdrawn or redesignated**.
Entries are prefixed `*`:

```
*PC.2      Redesignated as LF.7.9, S:L441R, S:H445P, Wales/Scotland
*XFG.20    Withdrawn: C10615T (didn't realize it was a dropout branch of XFG.3)
*MC.34     Withdrawn: Alias of B.1.1.529.2.86.1.1.11.1.3.1.1.34
```

This is what makes a remembered lineage fact actively wrong rather than merely stale. Two
follow-on effects:

- **A withdrawn name can still be attached to sequences.** `PC.2` was redesignated `LF.7.9`
  upstream, yet 25 sequences still carry `PC.2` because the instance's assignment pipeline lags
  designation. Both facts are true; report the redesignation alongside the count.
- **Nextclade calls depend on the dataset version.** The SARS-CoV-2 instance records
  `nextcladeDatasetVersion` per sequence. Two sequences called on different dataset versions can
  carry different lineage labels for identical genomes. Re-fetch the dataset
  (`data.clades.nextstrain.org/v3`) before calling your own sequences, and record the version.

## Influenza

| Instance | Column | Live values |
| --- | --- | --- |
| `h3n2`, `h1n1pdm` | `cladeHA` (also `cladeNA`) | `K` (88.9% of 2025/26 H3N2), `J.2.4`, `J.2.3`, `J.2.2`, `unassigned` |
| `h5n1` | `clade` | `2.3.4.4b` (essentially all of the current US data), `Am-nonGsGD` |
| `influenza-a` | `subtypeHA` / `subtypeNA` | `H3`, `H5`, `H1`, `H9`, `H10` |

Three cautions:

- **HA and NA are called separately** and can disagree; a reassortant is normal, not an error.
  `cladeHA` is the one antigenic and vaccine-strain discussion refers to, which is why the field
  picker prefers it.
- **`unassigned` is a real category**, not a null. Excluding it silently inflates every other
  clade's proportion.
- **H5N1 genotypes are not in this data.** The US genotype calls that dominate reporting — `B3.13`
  (the dairy-cattle genotype) and `D1.1` (the poultry and wild-bird genotype) — describe the
  reassortment pattern across all eight segments. The instance carries `clade` only, so both
  genotypes appear identically as `2.3.4.4b`. Genotype must come from a whole-genome tool such as
  GenoFLU, or from USDA/CDC reporting. Do not infer a genotype from a clade query, and do not
  present `2.3.4.4b` counts as genotype counts. Host is often the more informative axis available
  here: filtering US 2.3.4.4b by `hostNameScientific` separates `Bos taurus` from
  `Gallus gallus` and wild birds directly.

## Other pathogens

| Instance | Columns | Notes |
| --- | --- | --- |
| `mpox` | `clade`, `outbreakLineage`, `lineage` | Two orthogonal systems: `clade` is `Ia`/`Ib`/`IIa`/`IIb`; `outbreakLineage` is `sh2023/A.1`-style. Only `outbreakLineage` is indexed. |
| `rsv-a`, `rsv-b` | `lineage` (indexed), `subtype` | Post-2021 consensus lineage nomenclature (`A.D.5.2`-style) |
| `dengue` | `lineage` (indexed), `serotype` | Serotype and lineage are different questions; pick deliberately |
| `measles` | `genotype` | WHO genotypes (`B3`, `D8`, …), not indexed |
| `west-nile` | `lineage` | Not indexed |
| `cchf` | `lineage_S` | Named after the segment it is called on |
| `hmpv` | `lineage` (indexed) | |
| `ebola-zaire`, `ebola-sudan` | none | No lineage column exists; counts and lag still work |

`resolve_lineage.py` prints the alternatives it did not pick, so run it once against an unfamiliar
instance before committing to a column.

## Choosing a column

1. Prefer an **indexed** column when the question involves descendants — only those support `NAME*`.
2. Prefer the **finest** system that answers the question. Coarse clades hide the distinction you
   are usually asking about (`nextstrainClade` and recombinants being the clearest case).
3. Say which column you used. "XFG.1.1 is 35% of US sequences" is ambiguous until you add
   *`pangoLineage`, exact name, not including descendants* — three separate choices, each of which
   changes the number.

### `references/surveillance-caveats.md`

# Surveillance caveats

Genomic surveillance data is a convenience sample of a convenience sample: someone had to be
tested, the specimen had to be selected for sequencing, the sequence had to pass QC, and a
laboratory had to submit it. Every number below survives that funnel. The caveats here are the
difference between a defensible statement and a confident wrong one.

## Reporting lag is the dominant error

**Recent weeks are not a sample of what was circulating. They are a sample of whoever reports
fastest.** Measured on the open SARS-CoV-2 instance, US sequences, six monthly cohorts:

| Days after collection | Share of the cohort that has arrived |
| --- | --- |
| 7 | 29% |
| 14 | 46% |
| 30 | 68% |
| 60 | 87% |
| 90 | 94% |
| 180 | 100% |

H5N1 is far slower: 0% at 14 days, 15% at 30 days, 85% at 60 days.

Two things follow.

**The denominator for the last several weeks is a fraction of its final size.** A collection week
that will eventually hold 200 sequences may hold 20 today, and those 20 come disproportionately
from the fastest-reporting laboratories — which are geographically and institutionally clustered.
The resulting proportion is not merely noisy, it is *biased*, and no confidence interval accounts
for that bias.

**A "new variant" can be an artifact of who reported first.** A lineage that looks like it appeared
last week may simply be the lineage of the laboratory with the shortest turnaround.

Run `reporting_lag.py` for the instance and country in question — the curve differs sharply
between them — and treat the cutoff it prints as the boundary of interpretable data.
`lineage_prevalence.py` flags weeks whose denominator has not filled in and excludes them from
growth fits by default.

The measured curve is a **lower bound**: it uses each cohort's present-day total as the
denominator, and even year-old cohorts still gain sequences.

## Sampling and ascertainment bias

Sequence counts are not case counts, and nothing in this data corrects for:

- **Which specimens get sequenced.** Programmes variously prioritise travellers, hospitalised
  patients, outbreak investigations, S-gene target failures, or a random subsample. The
  SARS-CoV-2 instance carries a `samplingStrategy` field that is frequently null.
- **Where.** Sequencing capacity is concentrated. A global proportion is close to a weighted
  average of a handful of well-resourced countries. Filter to a geography you can interpret, and
  say which.
- **Who.** Host matters outside human pathogens. For H5N1 the same clade in `Bos taurus`,
  `Gallus gallus`, and wild birds represents entirely different epidemiology; an unfiltered clade
  count silently pools them.
- **QC.** Sequences failing coverage thresholds are absent, and failure is not random with respect
  to lineage — a lineage with a primer-dropout region is under-represented exactly where the
  dropout matters.

None of this is fixable from the API. It is reportable, and the honest form is "X% of *sequenced
specimens meeting these filters*", never "X% of infections".

## Denominators

Decide explicitly, and state it:

- **Exact name vs. including descendants.** `XFG` alone is 4 sequences; `XFG*` is 640. Almost
  every question about a lineage's importance means the second.
- **Geography.** `--where country=USA` and no filter answer different questions.
- **Window.** A 26-week window and a 4-week window can invert the apparent ranking of two lineages.
  Windows are widened to whole ISO weeks so every row covers the same number of days.
- **Undated sequences.** Sequences with no usable collection date are excluded from weekly bins;
  `lineage_prevalence.py` reports how many rather than dropping them silently. Note that they are
  still counted by the descendant check, which is why that check compares two counts of the same
  kind rather than a count against a sum of bins — mixing the two made every lineage with undated
  sequences look as though it had descendants it does not.
- **Unassigned calls.** The most frequent value in a lineage column is sometimes null or
  `unassigned`. Discovery mode skips those, but they stay in the denominator, which is correct:
  they were sequenced, they just were not classified.

## Intervals

Proportions carry **Wilson score intervals**. The normal-approximation (Wald) interval is wrong in
exactly the situations surveillance produces constantly: it leaves the unit interval for small
`n`, and collapses to zero width at `p = 0`, which would report "0.0% (0.0–0.0)" for a lineage seen
zero times in 20 sequences. Wilson gives 0–17% there, which is the honest answer.

The interval covers **binomial sampling error only**. It does not cover reporting bias, geographic
clustering, or lineage-assignment error, all of which are typically larger. Two intervals
overlapping is weak evidence of no difference; two not overlapping is not proof of one.

## Growth estimates

`--growth` fits a weighted least-squares line to the log-odds of the proportion against time,
weighting each week by `n·p·(1−p)` and applying a Haldane–Anscombe 0.5 correction so 0 and 1 stay
finite.

**What it is:** a description of how the log-odds of this lineage among sequenced specimens moved
over this window, in this place.

**What it is not:** a fitness estimate, a transmissibility estimate, or a forecast. A logistic
model assumes two competing populations under constant conditions. Real windows contain changing
sequencing programmes, shifting geography, holidays, and multiple co-circulating lineages.

Two guards keep the interval honest.

**Observation thresholds.** With the continuity correction alone, a lineage observed **zero** times
in every week still produces p = 0.5/(n+1), which drifts purely with the denominator. A shrinking
denominator then manufactures a tight, confident-looking positive slope for a lineage nobody has
seen — this was observed in testing, at +0.105/week with a CI excluding zero, for a lineage with
no observations at all. `logit_slope()` therefore requires at least 5 observations across at least
3 non-empty weeks and returns nothing otherwise. Do not lower those thresholds to get a number.

**Dispersion clamped at 1.** The standard error uses a quasi-binomial dispersion estimated from the
residuals, floored at 1. With inverse-variance weights the model's own scale *is* 1, so an estimate
below it means a short series happened to sit near the line — not that the slope is better
determined than binomial sampling allows. Letting that through would report an interval narrower
than the data supports. Above 1 the estimate is kept, so genuine overdispersion widens the interval
as it should. The reported `dispersion` is worth reading: well above 1 means the weekly points
scatter far more than binomial sampling explains, which usually means the denominator's composition
is changing and the slope is describing that rather than the lineage.

When quoting a slope, give the window, the geography, the number of weeks, and the interval, and
call it descriptive.

## Reproducibility

The database changes daily. A result without `dataVersion`, the instance, the filters, and the
window cannot be reproduced or audited — the same query will simply return different numbers.
Every script prints all four. Keep them with the figure.

Open GenBank-derived instances hold a subset of what GISAID holds. Absolute counts here are lower
than GISAID-derived figures; proportions are usually comparable but not identical. Do not mix the
two in one table.

## What this data cannot support

- **Case counts, incidence, or severity.** Sequences are not cases; there is no denominator of
  infections and no outcome data.
- **Clinical interpretation.** Nothing here speaks to how a patient should be treated.
- **Outbreak-response or public-health recommendations.** Those require case surveillance,
  local context, and authority this data does not carry.
- **Claims about a lineage's biology from its frequency.** A rising proportion is consistent with
  higher transmissibility, immune escape, a founder effect, a single outbreak in one facility, or
  a change in who is being sequenced. Frequency alone does not distinguish them.
- **Absence.** "Zero sequences" means zero *sequenced and submitted* specimens under these
  filters. With H5N1 at 15% completeness after 30 days, recent absence is close to uninformative.
  Check whether the name is even valid first — on an unindexed column, a typo returns 0 rather
  than an error.

### `scripts/lapis_client.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Minimal LAPIS client plus the pure helpers the four CLIs share.

Standard library only. Network access to the GenSpectrum family of LAPIS
instances (cov-spectrum.org, genspectrum.org, pathoplexus.org) is required for
the request functions; every helper below the ``--- pure helpers ---`` mark is
offline and independently testable.

Design notes that matter for correctness (all verified against the live API on
2026-07-27, and the reason this skill ships scripts rather than a recipe):

* **Field names are per-instance, not universal.** ``dateFrom=`` is the
  collection-date filter on the SARS-CoV-2 instance and a hard 400 on H5N1,
  whose collection date is ``sampleCollectionDateRangeLower``. Nothing here
  hardcodes a field name; ``describe_instance()`` reads ``/sample/databaseConfig``
  and the pickers below choose from what the instance actually declares.

* **A trailing ``*`` means opposite things on different instances.** It expands
  to "this lineage and its descendants" only where the field carries a lineage
  index. ``pangoLineage=XFG`` returns 4 sequences and ``pangoLineage=XFG*``
  returns 640; on H5N1, which has no lineage index, ``clade=2.3.4.4b`` returns
  62413 and ``clade=2.3.4.4b*`` returns **0**. Silently wrong in both
  directions, so ``lineage_filter()`` refuses to build the query that lies.

* **Only ``date``-typed fields accept range filters.** H5N1 types
  ``sampleCollectionDate`` as a string, so it has no ``...From``/``...To`` keys
  at all. ``supports_range()`` checks the declared type instead of guessing.

* **LAPIS reports errors in the body, and the body is worth reading.** A 400
  lists every valid filter key for that instance. ``_request()`` surfaces that
  ``detail`` string rather than letting urllib raise a bare HTTPError.
"""
from __future__ import annotations

import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from typing import Any, Iterable, Sequence

# Instances verified reachable on 2026-07-27. The registry is a convenience,
# not an authority: any LAPIS deployment works via --base-url, and every script
# introspects the schema at runtime rather than trusting this table.
INSTANCES: dict[str, str] = {
    "sars-cov-2": "https://lapis.cov-spectrum.org/open/v2",
    "influenza-a": "https://lapis.genspectrum.org/influenza-a",
    "h1n1pdm": "https://lapis.genspectrum.org/h1n1pdm",
    "h3n2": "https://lapis.genspectrum.org/h3n2",
    "h5n1": "https://lapis.genspectrum.org/h5n1",
    "rsv-a": "https://lapis.pathoplexus.org/rsv-a",
    "rsv-b": "https://lapis.pathoplexus.org/rsv-b",
    "hmpv": "https://lapis.pathoplexus.org/hmpv",
    "measles": "https://lapis.pathoplexus.org/measles",
    "mpox": "https://lapis.pathoplexus.org/mpox",
    "west-nile": "https://lapis.pathoplexus.org/west-nile",
    "dengue": "https://lapis.pathoplexus.org/dengue",
    "ebola-zaire": "https://lapis.pathoplexus.org/ebola-zaire",
    "ebola-sudan": "https://lapis.pathoplexus.org/ebola-sudan",
    "cchf": "https://lapis.pathoplexus.org/cchf",
}

# pango-designation is the authority for SARS-CoV-2 lineage names. Fetched at
# run time, never cached in this repository: withdrawals and redesignations
# land continuously and a stale copy is worse than no copy.
PANGO_ALIAS_URL = (
    "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/"
    "pango_designation/alias_key.json"
)
PANGO_NOTES_URL = (
    "https://raw.githubusercontent.com/cov-lineages/pango-designation/master/"
    "lineage_notes.txt"
)

USER_AGENT = "scientific-agent-skills-pathogen-variant-surveillance/1.0"
TIMEOUT = 60
MAX_ATTEMPTS = 3
RETRY_STATUS = {429, 500, 502, 503, 504}

# Collection- and submission-date fields, in the order they should be preferred
# when an instance declares more than one. Anything not listed is still found by
# the substring fallback in pick_date_field().
COLLECTION_DATE_FIELDS = (
    "date",
    "sampleCollectionDateRangeLower",
    "sampleCollectionDate",
    "collectionDate",
    "dateCollected",
)
SUBMISSION_DATE_FIELDS = (
    "dateSubmitted",
    "ncbiReleaseDate",
    "releasedDate",
    "submittedDate",
    "dateReleased",
)
# Lineage-like columns for instances that declare no lineage index at all.
LINEAGE_FIELDS = (
    "pangoLineage",
    "nextcladePangoLineage",
    "lineage",
    "clade",
    "nextstrainClade",
    "subtype",
    "genotype",
    "serotype",
)
RANGE_TYPES = {"date", "int", "float"}

# Two-sided 95% normal quantile, shared by the interval and the slope CI.
Z_95 = 1.959964


class LapisError(RuntimeError):
    """A LAPIS request failed in a way the caller cannot paper over."""


# --- network ----------------------------------------------------------------


def _encode(params: dict[str, Any]) -> str:
    """Encode query parameters, repeating keys for list values."""
    pairs: list[tuple[str, str]] = []
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple, set)):
            pairs.extend((key, str(item)) for item in value if item is not None)
        else:
            pairs.append((key, str(value)))
    return urllib.parse.urlencode(pairs)


def _error_detail(body: bytes) -> str:
    """Pull the human-readable reason out of a LAPIS error body.

    Two envelopes are in use: ``{"error": {...}, "info": {...}}`` and a bare
    RFC 7807 ``{"type": ..., "detail": ...}``. Both carry ``detail``, and on a
    bad filter key that string enumerates every key the instance accepts.
    """
    try:
        payload = json.loads(body.decode("utf-8", "replace"))
    except (ValueError, AttributeError):
        return sanitize(body.decode("utf-8", "replace"), limit=400) if body else ""
    if isinstance(payload, dict):
        inner = payload.get("error") if isinstance(payload.get("error"), dict) else payload
        detail = inner.get("detail") or inner.get("title")
        if detail:
            return sanitize(detail, limit=1200)
    return sanitize(json.dumps(payload), limit=1200)


def request(base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
    """GET a JSON document from a LAPIS instance, retrying transient failures."""
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    if params:
        query = _encode(params)
        if query:
            url = f"{url}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    last: str = ""
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            detail = _error_detail(exc.read())
            last = f"HTTP {exc.code}: {detail}"
            if exc.code not in RETRY_STATUS:
                raise LapisError(f"{url}\n  {last}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last = str(exc)
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(1.5 * (attempt + 1))
    raise LapisError(f"request failed after {MAX_ATTEMPTS} attempts: {url}\n  {last}")


def resolve_base_url(instance: str | None, base_url: str | None) -> str:
    """Turn ``--instance`` / ``--base-url`` into a URL, or explain the options."""
    if base_url:
        return base_url.rstrip("/")
    if not instance:
        raise LapisError("give --instance NAME or --base-url URL")
    try:
        return INSTANCES[instance]
    except KeyError:
        known = ", ".join(sorted(INSTANCES))
        raise LapisError(
            f"unknown instance {instance!r}. Known: {known}. "
            "Any other LAPIS deployment works via --base-url."
        ) from None


_SCHEMA_CACHE: dict[str, dict] = {}


def describe_instance(base_url: str) -> dict:
    """Fetch and cache ``/sample/databaseConfig`` for an instance.

    Returns ``{"name", "openness", "primary_key", "types", "lineage_indexed",
    "features"}`` where ``types`` maps every declared metadata field to its
    declared type. Everything downstream chooses field names from this rather
    than assuming the SARS-CoV-2 vocabulary.
    """
    if base_url in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[base_url]
    schema = request(base_url, "sample/databaseConfig").get("schema", {})
    metadata = schema.get("metadata", [])
    described = {
        "name": schema.get("instanceName", ""),
        "openness": schema.get("opennessLevel", ""),
        "primary_key": schema.get("primaryKey", ""),
        "types": {m["name"]: m.get("type", "string") for m in metadata},
        "lineage_indexed": [m["name"] for m in metadata if m.get("generateLineageIndex")],
        "features": [f.get("name") for f in schema.get("features", [])],
    }
    _SCHEMA_CACHE[base_url] = described
    return described


def data_version(base_url: str) -> str:
    """The instance's current data version, for stamping any result you keep."""
    return str(request(base_url, "sample/info").get("dataVersion", ""))


def aggregated(
    base_url: str, filters: dict[str, Any], fields: Sequence[str] = ()
) -> list[dict]:
    """Grouped counts. ``fields`` is the group-by, not a projection.

    ``limit``/``offset``/``orderBy`` are rejected on this endpoint because the
    result has no inherent ordering; sort client-side.
    """
    params = dict(filters)
    if fields:
        params["fields"] = ",".join(fields)
    return request(base_url, "sample/aggregated", params).get("data", [])


def count(base_url: str, filters: dict[str, Any]) -> int:
    """Total sequences matching a filter."""
    rows = aggregated(base_url, filters)
    return int(rows[0]["count"]) if rows else 0


def mutations(
    base_url: str,
    filters: dict[str, Any],
    *,
    amino_acid: bool = True,
    min_proportion: float = 0.05,
) -> list[dict]:
    """Mutations carried by the matching sequences, with per-site proportions.

    Rows carry ``mutation``, ``count``, ``coverage``, ``proportion``,
    ``sequenceName`` (the gene or segment), ``position``, ``mutationFrom`` and
    ``mutationTo``. ``proportion`` is over ``coverage`` — sequences that
    actually resolved that site — not over every matching sequence.
    """
    endpoint = "sample/aminoAcidMutations" if amino_acid else "sample/nucleotideMutations"
    params = dict(filters)
    params["minProportion"] = min_proportion
    return request(base_url, endpoint, params).get("data", [])


def lineage_definition(base_url: str, column: str) -> dict:
    """The instance's live lineage tree for a column: parents and aliases.

    Only served for columns carrying a lineage index; a 400 means the column
    has none, and there is no ancestry to query.
    """
    return request(base_url, f"sample/lineageDefinition/{column}")


# Blob hashes of the pango-designation files most recently fetched, keyed by
# URL. raw.githubusercontent returns the git blob SHA as the ETag, so exact
# provenance costs no extra request.
PANGO_BLOBS: dict[str, str] = {}


def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            etag = (response.headers.get("ETag") or "").strip('"W/ ')
            if etag:
                PANGO_BLOBS[url] = etag
            return response.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise LapisError(f"could not fetch {url}: {exc}") from exc


def pango_provenance() -> str:
    """Blob hashes of the pango-designation files fetched this run.

    The fetch is deliberately unpinned — freezing it to a tag would make
    lineage resolution reproducible and wrong, since withdrawals and
    redesignations are exactly what this skill exists to catch. Recording the
    hash of what was actually read gives auditability without staleness.
    """
    return " ".join(
        f"{url.rsplit('/', 1)[-1]}@{sha[:12]}" for url, sha in sorted(PANGO_BLOBS.items())
    )


def fetch_pango_aliases() -> dict[str, Any]:
    """The live ``alias_key.json`` from pango-designation.

    Values are a string (the unaliased parent path) for ordinary lineages and a
    **list of parents** for recombinants. LAPIS does not carry the recombinant
    parentage — its lineage tree roots every X* lineage — so this file is the
    only place ``XFG -> [LF.7, LP.8.1.2]`` is recorded.
    """
    return json.loads(_fetch_text(PANGO_ALIAS_URL))


def fetch_lineage_notes() -> dict[str, dict[str, str]]:
    """Parse ``lineage_notes.txt`` into ``{name: {status, note}}``.

    Names prefixed ``*`` have been withdrawn or redesignated. Those entries are
    the reason a model's remembered lineage facts are not merely stale but
    wrong, so they are surfaced rather than filtered out.
    """
    parsed: dict[str, dict[str, str]] = {}
    for line in _fetch_text(PANGO_NOTES_URL).splitlines():
        if not line.strip() or line.startswith("Lineage\t"):
            continue
        name, _, note = line.partition("\t")
        name = name.strip()
        if not name:
            continue
        withdrawn = name.startswith("*")
        parsed[name.lstrip("*")] = {
            "status": "withdrawn" if withdrawn else "designated",
            "note": note.strip(),
        }
    return parsed


# --- pure helpers -----------------------------------------------------------


def supports_range(schema: dict, field: str) -> bool:
    """True when ``<field>From`` / ``<field>To`` exist for this field.

    LAPIS derives range filters from the declared type, so a date recorded as a
    string (H5N1's ``sampleCollectionDate``) has none.
    """
    return schema.get("types", {}).get(field) in RANGE_TYPES


def range_keys(field: str) -> tuple[str, str]:
    """The inclusive lower/upper filter keys for a range-capable field."""
    return f"{field}From", f"{field}To"


def pick_date_field(schema: dict, role: str = "collection", preferred: str | None = None) -> str:
    """Choose a range-capable date field for ``collection`` or ``submission``.

    Raises rather than guessing: a silently wrong date column produces a
    plausible time series of the wrong thing.
    """
    types = schema.get("types", {})
    if preferred:
        if preferred not in types:
            raise LapisError(f"{preferred!r} is not a field on this instance")
        if not supports_range(schema, preferred):
            raise LapisError(
                f"{preferred!r} is typed {types[preferred]!r} on this instance, so LAPIS "
                f"offers no {preferred}From/{preferred}To range filter"
            )
        return preferred

    ordered = COLLECTION_DATE_FIELDS if role == "collection" else SUBMISSION_DATE_FIELDS
    for name in ordered:
        if name in types and supports_range(schema, name):
            return name
    needles = ("collect",) if role == "collection" else ("submit", "release")
    for name, kind in sorted(types.items()):
        low = name.lower()
        if kind == "date" and any(n in low for n in needles) and "_seg" not in low:
            return name
    raise LapisError(
        f"no range-capable {role} date field on this instance; "
        f"date-typed fields are: {sorted(n for n, t in types.items() if t == 'date')}"
    )


def looks_like_lineage(name: str) -> bool:
    """True for field names that plausibly hold a lineage, clade, or genotype.

    Deliberately loose, because the naming is not standardised across
    deployments: seasonal influenza splits the call per segment (``cladeHA``,
    ``cladeNA``), CCHF names it after the segment (``lineage_S``), mpox carries
    both ``clade`` and ``outbreakLineage``. Per-segment quality columns
    (``completeness_seg3``) are excluded.
    """
    low = name.lower()
    # "nextcladeQcOverallScore" contains "clade" and is not a lineage call.
    if any(token in low for token in ("_seg", "qc", "score", "coverage", "version")):
        return False
    return any(
        token in low for token in ("clade", "lineage", "genotype", "serotype", "subtype")
    )


def lineage_field_candidates(schema: dict) -> list[tuple[str, bool]]:
    """Every plausible lineage column as ``(name, indexed)``, best first.

    Indexed columns come first because only they support descendant queries.
    Within a tier, the names this skill knows outrank the ones it guessed, and
    an HA-derived clade outranks NA — for influenza the HA clade is the one
    that antigenic and vaccine-strain discussion refers to.
    """
    types = schema.get("types", {})
    indexed = set(schema.get("lineage_indexed", []))
    known = {name: rank for rank, name in enumerate(LINEAGE_FIELDS)}

    def sort_key(name: str) -> tuple:
        return (
            0 if name in indexed else 1,
            known.get(name, len(LINEAGE_FIELDS)),
            0 if name.upper().endswith("HA") else 1,
            name,
        )

    names = [n for n in types if looks_like_lineage(n)]
    return [(n, n in indexed) for n in sorted(names, key=sort_key)]


def pick_lineage_field(schema: dict, preferred: str | None = None) -> tuple[str, bool]:
    """Choose the lineage/clade column. Returns ``(field, has_lineage_index)``.

    The index flag decides whether a trailing ``*`` expands to descendants or
    matches nothing, so it travels with the field name everywhere.
    """
    types = schema.get("types", {})
    if preferred:
        if preferred not in types:
            raise LapisError(f"{preferred!r} is not a field on this instance")
        return preferred, preferred in set(schema.get("lineage_indexed", []))
    candidates = lineage_field_candidates(schema)
    if not candidates:
        raise LapisError(
            "no lineage-like column on this instance; pass --lineage-field with one of: "
            + ", ".join(sorted(types))
        )
    return candidates[0]


def lineage_filter(value: str, has_index: bool, include_sublineages: bool) -> str:
    """Build the lineage filter value, refusing the query that lies.

    ``XFG*`` on an indexed column means XFG and every descendant. The same
    string on an unindexed column is a literal match against a name no sequence
    carries, and LAPIS answers 0 without complaint.
    """
    stripped = value.rstrip("*")
    wants_children = include_sublineages or value.endswith("*")
    if not wants_children:
        return stripped
    if not has_index:
        raise LapisError(
            f"{value!r} asks for sublineages, but this column carries no lineage index, "
            "so a trailing '*' would match nothing and report 0. Query the exact name, "
            "or enumerate descendants yourself."
        )
    return f"{stripped}*"


def wilson_interval(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Used instead of the normal approximation because surveillance weeks are
    routinely small or zero-count, where Wald intervals leave the unit interval
    and report zero width at p=0.
    """
    if total <= 0:
        return (0.0, 1.0)
    k, n = float(successes), float(total)
    denom = n + z * z
    centre = (k + z * z / 2.0) / denom
    half = (z / denom) * math.sqrt(k * (n - k) / n + z * z / 4.0)
    return (max(0.0, centre - half), min(1.0, centre + half))


def iso_week_start(value: str) -> str | None:
    """Monday of the ISO week containing an ISO date, or None if unparseable.

    LAPIS returns nulls and partial dates for sequences whose collection date
    was never reported; those are counted separately, never silently binned.
    """
    if not value or len(value) < 10:
        return None
    try:
        parsed = date.fromisoformat(value[:10])
    except ValueError:
        return None
    return (parsed - timedelta(days=parsed.weekday())).isoformat()


def bin_weekly(rows: Iterable[dict], date_key: str) -> tuple[dict[str, int], int]:
    """Sum ``count`` into ISO weeks. Returns ``(weeks, undated)``."""
    weeks: dict[str, int] = {}
    undated = 0
    for row in rows:
        week = iso_week_start(str(row.get(date_key) or ""))
        n = int(row.get("count") or 0)
        if week is None:
            undated += n
            continue
        weeks[week] = weeks.get(week, 0) + n
    return weeks, undated


def week_range(start: str, end: str) -> list[str]:
    """Every ISO week start from ``start`` to ``end`` inclusive, gaps included."""
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    out: list[str] = []
    cursor = first - timedelta(days=first.weekday())
    while cursor <= last:
        out.append(cursor.isoformat())
        cursor += timedelta(days=7)
    return out


def flag_low_coverage(weekly_totals: dict[str, int], fraction: float = 0.4) -> dict[str, bool]:
    """Mark weeks whose denominator has not filled in yet.

    A collection week keeps accruing sequences for months: on the SARS-CoV-2
    open instance only 14% of a month's sequences had been submitted by the end
    of that month, and 89% by two months later. Recent weeks therefore look
    thin, and a proportion computed from them is dominated by whichever labs
    report fastest. The reference is the median of the older half of the
    window, which is the settled part of the same series.
    """
    if not weekly_totals:
        return {}
    ordered = sorted(weekly_totals)
    settled = ordered[: max(1, len(ordered) // 2)]
    counts = sorted(weekly_totals[w] for w in settled)
    mid = len(counts) // 2
    median = counts[mid] if len(counts) % 2 else (counts[mid - 1] + counts[mid]) / 2
    threshold = median * fraction
    return {week: weekly_totals[week] < threshold for week in ordered}


def logit_slope(
    points: Sequence[tuple[float, int, int]],
    *,
    min_successes: int = 5,
    min_nonzero_weeks: int = 3,
) -> dict[str, float] | None:
    """Weighted least-squares slope of log-odds against time.

    ``points`` are ``(t_weeks, successes, total)``. Proportions are shifted by
    the Haldane-Anscombe 0.5 so that 0 and 1 remain finite, and each point is
    weighted by the inverse variance of its logit, ``n*p*(1-p)``.

    This is a **descriptive** slope, not a fitness estimate. It absorbs any
    change in who is sequencing, where, and how fast they report, and it
    assumes the composition of the denominator is stable across the window.

    Returns None unless there is something to fit. The success thresholds are
    not decoration: with the continuity correction alone, a lineage observed
    **zero** times in every week still yields p = 0.5/(n+1), which drifts purely
    with the denominator. A shrinking denominator then manufactures a tight,
    confident-looking positive slope for a lineage nobody has seen. Requiring
    real observations is what stops that number from being printed.
    """
    usable = [(t, k, n) for t, k, n in points if n > 0]
    if len(usable) < 3:
        return None
    if sum(k for _, k, _ in usable) < min_successes:
        return None
    if sum(1 for _, k, _ in usable if k > 0) < min_nonzero_weeks:
        return None

    rows = []
    for t, k, n in usable:
        p = (k + 0.5) / (n + 1.0)
        weight = n * p * (1.0 - p)
        if weight <= 0:
            continue
        rows.append((t, math.log(p / (1.0 - p)), weight))
    if len(rows) < 3:
        return None

    sw = sum(w for _, _, w in rows)
    mean_t = sum(w * t for t, _, w in rows) / sw
    mean_y = sum(w * y for _, y, w in rows) / sw
    sxx = sum(w * (t - mean_t) ** 2 for t, _, w in rows)
    if sxx <= 0:
        return None
    sxy = sum(w * (t - mean_t) * (y - mean_y) for t, y, w in rows)
    slope = sxy / sxx
    intercept = mean_y - slope * mean_t

    # Quasi-binomial dispersion, clamped at 1. With inverse-variance weights the
    # model's own scale is 1, so an estimate below 1 is underdispersion -- almost
    # always a short series that happens to sit near the line, not evidence the
    # slope is better determined than binomial sampling allows. Letting it
    # through would report a CI narrower than the data can support. Above 1 it
    # is kept, so real overdispersion widens the interval as it should.
    residual = sum(w * (y - intercept - slope * t) ** 2 for t, y, w in rows)
    dof = len(rows) - 2
    dispersion = max(residual / dof, 1.0) if dof > 0 else 1.0
    stderr = math.sqrt(dispersion / sxx)
    return {
        "slope_per_week": slope,
        "stderr": stderr,
        "dispersion": dispersion,
        "ci_low": slope - Z_95 * stderr,
        "ci_high": slope + Z_95 * stderr,
        "n_weeks": float(len(rows)),
    }


def unalias(name: str, aliases: dict[str, Any]) -> str:
    """Expand a Pango alias to its full dotted path under A or B.

    ``PQ.17`` unaliases to ``XDV.1.5.1.1.8.1.17``; applied repeatedly it walks
    back to ``B.1.1.529...``. Recombinants stop the walk: their alias entry is a
    list of parents, not a path, so ``XFG.1.1`` expands no further.
    """
    head, _, tail = name.partition(".")
    target = aliases.get(head)
    if not isinstance(target, str) or not target:
        return name
    return f"{target}.{tail}" if tail else target


def unalias_full(name: str, aliases: dict[str, Any], limit: int = 20) -> str:
    """Apply :func:`unalias` until it reaches a fixed point."""
    current = name
    for _ in range(limit):
        expanded = unalias(current, aliases)
        if expanded == current:
            return current
        current = expanded
    return current


def recombinant_parents(name: str, aliases: dict[str, Any]) -> list[str]:
    """Parents of a recombinant lineage, or [] for an ordinary one."""
    head = name.partition(".")[0]
    target = aliases.get(head)
    if isinstance(target, list):
        seen: list[str] = []
        for parent in target:
            if parent not in seen:
                seen.append(parent)
        return seen
    return []


def parent_chain(name: str, definition: dict, limit: int = 60) -> list[str]:
    """Walk a LAPIS lineage definition from a lineage up to its root."""
    chain: list[str] = []
    current = name
    for _ in range(limit):
        parents = (definition.get(current) or {}).get("parents") or []
        if not parents:
            break
        current = parents[0]
        if current in chain:
            break
        chain.append(current)
    return chain


def children_map(definition: dict) -> dict[str, list[str]]:
    """Invert a lineage definition into parent -> children.

    Worth building once and passing around: the SARS-CoV-2 definition holds
    ~5,500 entries, so rebuilding it per lineage turns a list of names into
    quadratic work.
    """
    children: dict[str, list[str]] = {}
    for lineage, entry in definition.items():
        for parent in (entry or {}).get("parents") or []:
            children.setdefault(parent, []).append(lineage)
    return children


def descendants(
    name: str, definition: dict, children: dict[str, list[str]] | None = None
) -> list[str]:
    """Every lineage whose parent chain passes through ``name``.

    Pass ``children`` from :func:`children_map` when resolving several names.
    """
    if children is None:
        children = children_map(definition)
    found: set[str] = set()
    stack = list(children.get(name, []))
    while stack:
        node = stack.pop()
        if node in found:
            continue
        found.add(node)
        stack.extend(children.get(node, []))
    return sorted(found)


def top_values(rows: Sequence[dict], field: str, limit: int) -> list[str]:
    """The ``limit`` most frequent non-null values of a grouped-by field.

    Used to discover what is actually circulating before naming anything, so a
    situation report starts from the data rather than from a remembered list.
    """
    ranked = sorted(
        (r for r in rows if r.get(field) not in (None, "")),
        key=lambda r: -int(r.get("count") or 0),
    )
    return [str(r[field]) for r in ranked[:limit]]


# Every C0 and C1 control character, tabs and newlines included -- a single
# newline in a label is enough to forge a row in TSV output.
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]")


def sanitize(value: object, limit: int = 400) -> str:
    """Flatten a value to one printable line for table and TSV rendering.

    Cell values reach here from a remote instance: lineage labels, field names,
    and error ``detail`` strings. Two reasons to flatten them.

    Correctness: a tab or newline inside a label silently corrupts TSV columns.

    Safety: this output is read by an agent, so remote text is untrusted input.
    Stripping control characters and collapsing line breaks stops a hostile or
    malformed instance from forging rows, headers, or anything that reads as
    structure rather than data. It is not a substitute for pointing
    ``--base-url`` only at deployments you trust.

    JSON output deliberately skips this — the encoder escapes control
    characters already, so values stay faithful for machine consumers.
    """
    text = "" if value is None else str(value)
    text = re.sub(r"\s{2,}", " ", _CONTROL_CHARS.sub(" ", text)).strip()
    return text if len(text) <= limit else text[: limit - 3] + "..."


def format_table(rows: Sequence[dict], columns: Sequence[str]) -> str:
    """Render rows as an aligned plain-text table."""
    header = list(columns)
    body = [[sanitize(r.get(c)) for c in header] for r in rows]
    widths = [
        max(len(header[i]), *(len(r[i]) for r in body)) if body else len(header[i])
        for i in range(len(header))
    ]
    lines = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(header)).rstrip()]
    for row in body:
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return "\n".join(lines)


def emit(rows: Sequence[dict], columns: Sequence[str], fmt: str) -> str:
    """Render rows as ``table``, ``tsv``, or ``json``."""
    if fmt == "json":
        return json.dumps([{c: r.get(c) for c in columns} for r in rows], indent=2)
    if fmt == "tsv":
        lines = ["\t".join(columns)]
        lines += ["\t".join(sanitize(r.get(c)) for c in columns) for r in rows]
        return "\n".join(lines)
    return format_table(rows, columns)
```

### `scripts/lineage_prevalence.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Weekly prevalence of one or more lineages, with intervals and a coverage flag.

Answers "what is circulating, and is it growing" from live sequence counts
rather than from memory. Every number is a count returned by the instance at
the data version printed in the provenance block.

    python3 lineage_prevalence.py XFG.1.1 XFJ.3 --instance sars-cov-2 --where country=USA
    python3 lineage_prevalence.py XFG --sublineages --weeks 12 --growth
    python3 lineage_prevalence.py 2.3.4.4b --instance h5n1 --where country=USA --weeks 52

Proportions carry Wilson intervals because surveillance weeks are small, and
recent weeks are flagged ``low`` when their denominator has not filled in yet
-- see reporting_lag.py for the measured filling-in curve.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from lapis_client import (
    LapisError,
    aggregated,
    bin_weekly,
    count,
    data_version,
    describe_instance,
    emit,
    flag_low_coverage,
    lineage_filter,
    logit_slope,
    pick_date_field,
    pick_lineage_field,
    range_keys,
    resolve_base_url,
    top_values,
    week_range,
    wilson_interval,
)

COLUMNS = (
    "lineage",
    "week",
    "n",
    "total",
    "proportion",
    "ci_low",
    "ci_high",
    "coverage",
)


def parse_where(pairs: list[str], schema: dict) -> dict[str, str]:
    """Turn ``KEY=VALUE`` arguments into filters, checking keys against the schema."""
    filters: dict[str, str] = {}
    types = schema.get("types", {})
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise LapisError(f"--where expects KEY=VALUE, got {pair!r}")
        base = key.split(".")[0]
        for suffix in ("From", "To"):
            if base.endswith(suffix) and base[: -len(suffix)] in types:
                base = base[: -len(suffix)]
                break
        if base not in types:
            near = sorted(n for n in types if base.lower() in n.lower())
            hint = f" Did you mean: {', '.join(near[:6])}?" if near else ""
            raise LapisError(f"{key!r} is not a field on this instance.{hint}")
        filters[key] = value
    return filters


def weekly_counts(
    base_url: str, filters: dict, date_field: str, weeks: list[str]
) -> tuple[dict[str, int], int]:
    """Weekly counts over the requested window, zero-filled for empty weeks."""
    rows = aggregated(base_url, filters, [date_field])
    binned, undated = bin_weekly(rows, date_field)
    return {week: binned.get(week, 0) for week in weeks}, undated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Weekly lineage prevalence from a LAPIS instance.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("lineages", nargs="*",
                        help="lineage or clade names; 'NAME*' includes descendants. "
                             "Omit to discover them with --top")
    parser.add_argument("--top", type=int, metavar="N",
                        help="discover the N most common lineages in the window instead of "
                             "naming them (default when no names are given)")
    parser.add_argument("--instance", default="sars-cov-2", help="registry name (default: sars-cov-2)")
    parser.add_argument("--base-url", help="any other LAPIS deployment")
    parser.add_argument("--lineage-field", help="override the auto-detected lineage column")
    parser.add_argument("--date-field", help="override the auto-detected collection-date column")
    parser.add_argument("--where", action="append", default=[], metavar="KEY=VALUE",
                        help="extra filter, repeatable (e.g. --where country=USA)")
    parser.add_argument("--weeks", type=int, default=26, help="window length in weeks (default: 26)")
    parser.add_argument("--since", help="window start, YYYY-MM-DD; overrides --weeks")
    parser.add_argument("--until", help="window end, YYYY-MM-DD (default: today)")
    parser.add_argument("--sublineages", action="store_true", help="include descendant lineages")
    parser.add_argument("--growth", action="store_true",
                        help="also fit a weighted log-odds slope over the trusted weeks")
    parser.add_argument("--include-incomplete", action="store_true",
                        help="let low-coverage weeks into the growth fit")
    parser.add_argument("--coverage-fraction", type=float, default=0.4,
                        help="flag weeks below this fraction of the settled median (default: 0.4)")
    parser.add_argument("--format", choices=("table", "tsv", "json"), default="table")
    parser.add_argument("-o", "--output", help="write to a file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        base_url = resolve_base_url(args.instance, args.base_url)
        schema = describe_instance(base_url)
        lineage_field, has_index = pick_lineage_field(schema, args.lineage_field)
        date_field = pick_date_field(schema, "collection", args.date_field)
        where = parse_where(args.where, schema)
    except LapisError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    requested_until = date.fromisoformat(args.until) if args.until else date.today()
    requested_since = (
        date.fromisoformat(args.since)
        if args.since
        else requested_until - timedelta(weeks=max(1, args.weeks))
    )
    if requested_since > requested_until:
        print("error: --since is after --until", file=sys.stderr)
        return 2
    if args.top is not None and args.top < 1:
        print("error: --top must be at least 1", file=sys.stderr)
        return 2

    # Snap both ends to ISO week boundaries. A window that starts mid-week gives
    # a first row covering three days and a last row covering four, and neither
    # is comparable to the full weeks between them -- exactly the kind of
    # silently uneven denominator this skill exists to prevent. Widening to whole
    # weeks keeps every row meaning the same thing; a still-unfilled final week
    # shows up through the coverage flag rather than as a short bar.
    since = requested_since - timedelta(days=requested_since.weekday())
    until = requested_until + timedelta(days=6 - requested_until.weekday())
    snapped = (since, until) != (requested_since, requested_until)

    from_key, to_key = range_keys(date_field)
    window = {from_key: since.isoformat(), to_key: until.isoformat(), **where}
    weeks = week_range(since.isoformat(), until.isoformat())

    try:
        version = data_version(base_url)
        totals, undated = weekly_counts(base_url, window, date_field, weeks)

        rows: list[dict] = []
        notes: list[str] = []
        fits: dict[str, dict] = {}
        coverage = flag_low_coverage(totals, args.coverage_fraction)

        targets = list(args.lineages)
        if args.top is not None or not targets:
            wanted = args.top or 10
            discovered = top_values(
                aggregated(base_url, window, [lineage_field]), lineage_field, wanted
            )
            if not discovered:
                print(
                    f"error: no sequences in {since} to {until}"
                    + (f" with {where}" if where else "")
                    + ". Widen the window or relax the filters.",
                    file=sys.stderr,
                )
                return 1
            notes.append(
                f"discovered the {len(discovered)} most common {lineage_field} "
                f"value{'s' if len(discovered) != 1 else ''} in the window: "
                f"{', '.join(discovered)}"
            )
            targets = discovered + [t for t in targets if t not in discovered]

        for name in targets:
            value = lineage_filter(name, has_index, args.sublineages)
            counts, _ = weekly_counts(
                base_url, {**window, lineage_field: value}, date_field, weeks
            )

            if has_index and not value.endswith("*"):
                # Both sides must come from the same kind of query. Summing the
                # weekly bins would drop sequences with no usable collection
                # date, making every lineage that has some look as though it had
                # descendants it does not.
                exact = count(base_url, {**window, lineage_field: value})
                inclusive = count(base_url, {**window, lineage_field: f"{value}*"})
                if inclusive > exact:
                    notes.append(
                        f"{value}: {exact} sequences named exactly {value}, "
                        f"{inclusive} including descendants. Pass --sublineages "
                        f"or write '{value}*' for the second number."
                    )

            for week in weeks:
                k, n = counts[week], totals[week]
                low, high = wilson_interval(k, n)
                rows.append(
                    {
                        "lineage": value,
                        "week": week,
                        "n": k,
                        "total": n,
                        "proportion": f"{(k / n):.4f}" if n else "",
                        "ci_low": f"{low:.4f}" if n else "",
                        "ci_high": f"{high:.4f}" if n else "",
                        "coverage": "low" if coverage.get(week) else "ok",
                    }
                )

            if args.growth:
                usable = [
                    (i, counts[w], totals[w])
                    for i, w in enumerate(weeks)
                    if args.include_incomplete or not coverage.get(w)
                ]
                fit = logit_slope([(float(t), k, n) for t, k, n in usable])
                if fit:
                    fits[value] = fit
                else:
                    notes.append(
                        f"{value}: too few observations for a growth estimate "
                        f"({sum(k for _, k, _ in usable)} sequences across "
                        f"{sum(1 for _, k, _ in usable if k > 0)} non-empty weeks). "
                        "No slope is reported rather than a slope driven by the denominator."
                    )
    except LapisError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        import json

        payload = {
            "meta": {
                "instance": schema["name"],
                "base_url": base_url,
                "data_version": version,
                "lineage_field": lineage_field,
                "lineage_index": has_index,
                "date_field": date_field,
                "window": [since.isoformat(), until.isoformat()],
                "filters": where,
                "undated_sequences": undated,
                "notes": notes,
            },
            "rows": rows,
            "growth": fits,
        }
        text = json.dumps(payload, indent=2)
    else:
        text = emit(rows, COLUMNS, args.format)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    else:
        print(text)

    sys.stdout.flush()
    if args.format != "json":
        print(
            f"\n# {schema['name']} via {base_url}"
            f"\n# data version {version} | {lineage_field}"
            f"{' (lineage-indexed)' if has_index else ' (no lineage index)'}"
            f" | dates from {date_field}"
            f"\n# window {since} to {until}"
            + (f" (widened from {requested_since}..{requested_until} to whole ISO weeks)"
               if snapped else "")
            + (f" | filters {where}" if where else "")
            + (f"\n# {undated} matching sequences carry no usable collection date" if undated else ""),
            file=sys.stderr,
        )
        for note in notes:
            print(f"# note: {note}", file=sys.stderr)
        if any(coverage.values()):
            flagged = [w for w, bad in coverage.items() if bad]
            print(
                f"# {len(flagged)} week(s) flagged low: denominator still filling in "
                f"(earliest {min(flagged)}). Treat their proportions as unstable.",
                file=sys.stderr,
            )
        for name, fit in fits.items():
            print(
                f"# growth {name}: log-odds slope {fit['slope_per_week']:+.3f}/week "
                f"(95% CI {fit['ci_low']:+.3f} to {fit['ci_high']:+.3f}, "
                f"{int(fit['n_weeks'])} weeks, dispersion {fit['dispersion']:.1f}). "
                f"Descriptive only -- confounded by sampling and reporting changes.",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/mutation_profile.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Mutations carried by a lineage, or the difference between two lineages.

Use this to answer "what distinguishes this lineage" and "does my assay target
still match" from current sequences, instead of from a lineage's founding
description -- which drifts as sublineages accumulate substitutions.

    python3 mutation_profile.py XFG.1.1 --gene S --min-proportion 0.9
    python3 mutation_profile.py XFG.23.1.3 --versus XFG.1.1 --gene S
    python3 mutation_profile.py 2.3.4.4b --instance h5n1 --gene HA --min-proportion 0.8
    python3 mutation_profile.py XFG --sublineages --nucleotide --since 2026-01-01

``proportion`` is over ``coverage`` -- the sequences that actually resolved that
site -- not over every matching sequence. A site with poor coverage can show a
high proportion on very few reads, so read the coverage column before quoting a
proportion.
"""
from __future__ import annotations

import argparse
import sys

from lapis_client import (
    LapisError,
    count,
    data_version,
    describe_instance,
    emit,
    lineage_filter,
    mutations,
    pick_date_field,
    pick_lineage_field,
    range_keys,
    resolve_base_url,
)

PROFILE_COLUMNS = ("mutation", "gene", "position", "from", "to", "proportion", "count", "coverage")
DIFF_COLUMNS = ("mutation", "gene", "position", "verdict", "prop_a", "prop_b", "n_a", "n_b")


def parse_where(pairs: list[str], schema: dict) -> dict[str, str]:
    """Turn ``KEY=VALUE`` arguments into filters, checking keys against the schema."""
    filters: dict[str, str] = {}
    types = schema.get("types", {})
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep:
            raise LapisError(f"--where expects KEY=VALUE, got {pair!r}")
        if key.split(".")[0] not in types:
            raise LapisError(f"{key!r} is not a field on this instance")
        filters[key] = value
    return filters


def profile(base_url: str, filters: dict, *, amino_acid: bool, min_proportion: float,
            gene: str | None) -> dict[str, dict]:
    """Mutation rows keyed by mutation string, optionally restricted to one gene."""
    rows = mutations(base_url, filters, amino_acid=amino_acid, min_proportion=min_proportion)
    keyed: dict[str, dict] = {}
    for row in rows:
        if gene and str(row.get("sequenceName") or "").upper() != gene.upper():
            continue
        keyed[row["mutation"]] = row
    return keyed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mutation profile of a lineage.")
    parser.add_argument("lineage", help="lineage or clade name; 'NAME*' includes descendants")
    parser.add_argument("--versus", help="second lineage to diff against")
    parser.add_argument("--instance", default="sars-cov-2", help="registry name (default: sars-cov-2)")
    parser.add_argument("--base-url", help="any other LAPIS deployment")
    parser.add_argument("--lineage-field", help="override the auto-detected lineage column")
    parser.add_argument("--date-field", help="override the auto-detected collection-date column")
    parser.add_argument("--gene", help="restrict to one gene or segment (e.g. S, HA, seg4)")
    parser.add_argument("--nucleotide", action="store_true",
                        help="nucleotide instead of amino-acid mutations")
    parser.add_argument("--min-proportion", type=float, default=0.8,
                        help="report mutations at or above this proportion (default: 0.8)")
    parser.add_argument("--sublineages", action="store_true", help="include descendant lineages")
    parser.add_argument("--since", help="restrict to sequences collected on or after YYYY-MM-DD")
    parser.add_argument("--where", action="append", default=[], metavar="KEY=VALUE",
                        help="extra filter, repeatable")
    parser.add_argument("--format", choices=("table", "tsv", "json"), default="table")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        base_url = resolve_base_url(args.instance, args.base_url)
        schema = describe_instance(base_url)
        lineage_field, has_index = pick_lineage_field(schema, args.lineage_field)
        where = parse_where(args.where, schema)
        if args.since:
            date_field = pick_date_field(schema, "collection", args.date_field)
            where[range_keys(date_field)[0]] = args.since

        # A diff must fetch below the reporting threshold on both sides,
        # otherwise a mutation pruned out of one side is indistinguishable from
        # one genuinely absent there and gets misreported as gained or lost.
        # The floor tracks --min-proportion so lowering it stays correct.
        diff_floor = min(0.05, args.min_proportion)

        primary = lineage_filter(args.lineage, has_index, args.sublineages)
        base_filters = {**where, lineage_field: primary}
        n_primary = count(base_url, base_filters)
        if n_primary == 0:
            print(
                f"error: no sequences match {lineage_field}={primary}"
                + (f" with {where}" if where else "")
                + ". Check the name with resolve_lineage.py.",
                file=sys.stderr,
            )
            return 1

        first = profile(
            base_url,
            base_filters,
            amino_acid=not args.nucleotide,
            min_proportion=args.min_proportion if not args.versus else diff_floor,
            gene=args.gene,
        )

        if not args.versus:
            rows = [
                {
                    "mutation": m["mutation"],
                    "gene": m.get("sequenceName", ""),
                    "position": m.get("position", ""),
                    "from": m.get("mutationFrom", ""),
                    "to": m.get("mutationTo", ""),
                    "proportion": f"{m['proportion']:.3f}",
                    "count": m.get("count", ""),
                    "coverage": m.get("coverage", ""),
                }
                for m in sorted(
                    first.values(),
                    key=lambda r: (str(r.get("sequenceName")), int(r.get("position") or 0)),
                )
            ]
            print(emit(rows, PROFILE_COLUMNS, args.format))
            summary = (
                f"\n# {schema['name']} via {base_url} | data version {data_version(base_url)}"
                f"\n# {lineage_field}={primary} | {n_primary} sequences"
                f" | {'nucleotide' if args.nucleotide else 'amino acid'} mutations"
                f" at proportion >= {args.min_proportion}"
                f"\n# proportion is over per-site coverage, not over all {n_primary} sequences"
            )
        else:
            secondary = lineage_filter(args.versus, has_index, args.sublineages)
            n_secondary = count(base_url, {**where, lineage_field: secondary})
            if n_secondary == 0:
                print(f"error: no sequences match {lineage_field}={secondary}", file=sys.stderr)
                return 1
            second = profile(
                base_url,
                {**where, lineage_field: secondary},
                amino_acid=not args.nucleotide,
                min_proportion=diff_floor,
                gene=args.gene,
            )

            rows = []
            for mutation in sorted(set(first) | set(second)):
                a = first.get(mutation, {})
                b = second.get(mutation, {})
                pa = float(a.get("proportion") or 0.0)
                pb = float(b.get("proportion") or 0.0)
                if pa >= args.min_proportion and pb < args.min_proportion:
                    verdict = "gained"
                elif pb >= args.min_proportion and pa < args.min_proportion:
                    verdict = "lost"
                elif pa >= args.min_proportion and pb >= args.min_proportion:
                    verdict = "shared"
                else:
                    continue
                source = a or b
                rows.append(
                    {
                        "mutation": mutation,
                        "gene": source.get("sequenceName", ""),
                        "position": source.get("position", ""),
                        "verdict": verdict,
                        "prop_a": f"{pa:.3f}",
                        "prop_b": f"{pb:.3f}",
                        "n_a": a.get("count", 0),
                        "n_b": b.get("count", 0),
                    }
                )
            rows.sort(key=lambda r: ({"gained": 0, "lost": 1, "shared": 2}[r["verdict"]],
                                     str(r["gene"]), int(r["position"] or 0)))
            print(emit(rows, DIFF_COLUMNS, args.format))
            summary = (
                f"\n# {schema['name']} via {base_url} | data version {data_version(base_url)}"
                f"\n# A = {primary} ({n_primary} sequences), B = {secondary} ({n_secondary})"
                f"\n# verdict is relative to a {args.min_proportion} proportion threshold"
            )
    except LapisError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    sys.stdout.flush()
    if args.format != "json":
        print(summary, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/reporting_lag.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure how long sequences take to appear, and how far back to trust the data.

The single most common way to get variant surveillance wrong is to compute
prevalence over the last few weeks. Those weeks are not a sample of what was
circulating -- they are a sample of whichever laboratories report fastest, and
they keep growing for months. This script measures that filling-in curve from
the instance itself and turns it into a cutoff date.

    python3 reporting_lag.py --instance sars-cov-2 --where country=USA
    python3 reporting_lag.py --instance h5n1 --target 0.8

Method: take monthly collection cohorts old enough to have settled, group each
by submission date, and compute what fraction of the cohort's present-day total
had arrived by each lag. Averaging across cohorts gives the curve.

The curve is a **lower bound** on the true lag: a cohort's denominator is what
has arrived so far, and even old cohorts still gain sequences. Treat the
recommended cutoff as the least conservative one defensible.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from lapis_client import (
    LapisError,
    aggregated,
    data_version,
    describe_instance,
    emit,
    pick_date_field,
    range_keys,
    resolve_base_url,
)

COLUMNS = ("lag_days", "mean_complete", "min_complete", "max_complete", "cohorts")
OFFSETS = (7, 14, 21, 30, 45, 60, 90, 120, 180)


def month_window(anchor: date, months_back: int) -> tuple[date, date]:
    """First and last day of the month ``months_back`` before ``anchor``."""
    total = anchor.year * 12 + (anchor.month - 1) - months_back
    year, month = divmod(total, 12)
    first = date(year, month + 1, 1)
    nxt = date(year + 1, 1, 1) if month == 11 else date(year, month + 2, 1)
    return first, nxt - timedelta(days=1)


def cohort_curve(
    base_url: str,
    filters: dict,
    submission_field: str,
    cohort_end: date,
) -> tuple[dict[int, float], int, int] | None:
    """Cumulative completeness by lag for one collection cohort.

    Returns ``(curve, dated, undated)``. Sequences with no parseable submission
    date are excluded from the denominator rather than counted as never having
    arrived — the question is "of the ones we can date, how fast did they come"
    — but they are returned so the caller can say how many were set aside.
    """
    rows = aggregated(base_url, filters, [submission_field])
    lags: list[tuple[int, int]] = []
    dated = 0
    undated = 0
    for row in rows:
        value = str(row.get(submission_field) or "")
        n = int(row.get("count") or 0)
        try:
            submitted = date.fromisoformat(value[:10])
        except ValueError:
            undated += n
            continue
        lags.append((max(0, (submitted - cohort_end).days), n))
        dated += n
    if dated == 0:
        return None
    lags.sort()
    curve: dict[int, float] = {}
    for offset in OFFSETS:
        arrived = sum(n for lag, n in lags if lag <= offset)
        curve[offset] = arrived / dated
    return curve, dated, undated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Measure sequence reporting lag and recommend a trust cutoff.",
    )
    parser.add_argument("--instance", default="sars-cov-2", help="registry name (default: sars-cov-2)")
    parser.add_argument("--base-url", help="any other LAPIS deployment")
    parser.add_argument("--date-field", help="override the auto-detected collection-date column")
    parser.add_argument("--submission-field", help="override the auto-detected submission-date column")
    parser.add_argument("--where", action="append", default=[], metavar="KEY=VALUE",
                        help="extra filter, repeatable (lag differs sharply by country)")
    parser.add_argument("--cohorts", type=int, default=6, help="monthly cohorts to average (default: 6)")
    parser.add_argument("--skip-months", type=int, default=3,
                        help="most recent months to exclude as unsettled (default: 3)")
    parser.add_argument("--target", type=float, default=0.9,
                        help="completeness the cutoff should reach (default: 0.9)")
    parser.add_argument("--until", help="anchor date, YYYY-MM-DD (default: today)")
    parser.add_argument("--format", choices=("table", "tsv", "json"), default="table")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        base_url = resolve_base_url(args.instance, args.base_url)
        schema = describe_instance(base_url)
        collection_field = pick_date_field(schema, "collection", args.date_field)
        submission_field = pick_date_field(schema, "submission", args.submission_field)
        if collection_field == submission_field:
            raise LapisError(
                f"collection and submission both resolved to {collection_field!r}; "
                "the lag would be identically zero. Set --submission-field explicitly."
            )
        where: dict[str, str] = {}
        for pair in args.where:
            key, sep, value = pair.partition("=")
            if not sep or key.split(".")[0] not in schema["types"]:
                raise LapisError(f"bad --where {pair!r}")
            where[key] = value
    except LapisError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    anchor = date.fromisoformat(args.until) if args.until else date.today()
    from_key, to_key = range_keys(collection_field)

    curves: list[dict[int, float]] = []
    sizes: list[int] = []
    undated_total = 0
    try:
        for back in range(args.skip_months, args.skip_months + max(1, args.cohorts)):
            start, end = month_window(anchor, back)
            result = cohort_curve(
                base_url,
                {from_key: start.isoformat(), to_key: end.isoformat(), **where},
                submission_field,
                end,
            )
            if result:
                curve, dated, undated = result
                curves.append(curve)
                sizes.append(dated)
                undated_total += undated
    except LapisError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not curves:
        print(
            "error: no cohort in the requested range holds any sequence. "
            "Widen --where, raise --cohorts, or lower --skip-months.",
            file=sys.stderr,
        )
        return 1

    rows = []
    for offset in OFFSETS:
        values = [c[offset] for c in curves]
        rows.append(
            {
                "lag_days": offset,
                "mean_complete": f"{sum(values) / len(values):.3f}",
                "min_complete": f"{min(values):.3f}",
                "max_complete": f"{max(values):.3f}",
                "cohorts": len(values),
            }
        )

    reached = [o for o in OFFSETS if sum(c[o] for c in curves) / len(curves) >= args.target]
    print(emit(rows, COLUMNS, args.format))

    sys.stdout.flush()
    if args.format != "json":
        print(
            f"\n# {schema['name']} via {base_url} | data version {data_version(base_url)}"
            f"\n# collection dates from {collection_field}, submission from {submission_field}"
            f"\n# {len(curves)} monthly cohorts, {sum(sizes)} datable sequences"
            + (f" ({undated_total} excluded for having no submission date)"
               if undated_total else "")
            + (f" | filters {where}" if where else ""),
            file=sys.stderr,
        )
        if reached:
            cutoff = anchor - timedelta(days=reached[0])
            print(
                f"# {args.target:.0%} of a cohort has arrived by {reached[0]} days.\n"
                f"# Trust collection dates up to {cutoff.isoformat()}; treat anything "
                f"later as provisional.",
                file=sys.stderr,
            )
        else:
            print(
                f"# no lag up to {OFFSETS[-1]} days reaches {args.target:.0%} completeness "
                f"(best {max(sum(c[o] for c in curves) / len(curves) for o in OFFSETS):.0%}). "
                f"Recent weeks cannot support a prevalence estimate here.",
                file=sys.stderr,
            )
        print(
            "# This curve is a lower bound: cohort denominators are still growing.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/resolve_lineage.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve a lineage name against the live nomenclature before trusting it.

Pango names are not stable identifiers. They are minted continuously, aliased
through a key that must be fetched to be read, and **withdrawn or redesignated
after the fact** -- so a remembered lineage fact is not merely stale, it can be
actively wrong. This script answers, for each name: does it still exist, what
does it expand to, what is it descended from, and how many sequences carry it.

    python3 resolve_lineage.py XFG.23.1.3 PQ.17 PC.2
    python3 resolve_lineage.py XFG --descendants
    python3 resolve_lineage.py 2.3.4.4b --instance h5n1

Exit code is 1 when any name is withdrawn or unknown, so it works as a gate on
a manuscript's lineage list.
"""
from __future__ import annotations

import argparse
import re
import sys

from lapis_client import (
    LapisError,
    children_map,
    count,
    data_version,
    descendants,
    describe_instance,
    emit,
    fetch_lineage_notes,
    fetch_pango_aliases,
    lineage_definition,
    lineage_field_candidates,
    parent_chain,
    pango_provenance,
    pick_lineage_field,
    recombinant_parents,
    resolve_base_url,
    unalias_full,
)

COLUMNS = (
    "query",
    "status",
    "unaliased",
    "parent",
    "recombinant_of",
    "descendants",
    "sequences",
    "detail",
)
PANGO_FIELDS = {"pangoLineage", "nextcladePangoLineage"}
REDESIGNATED = re.compile(r"[Rr]edesignated as ([A-Za-z][A-Za-z0-9.]*)")


def normalise(name: str) -> str:
    """Uppercase the alphabetic head so ``xfg.1`` matches ``XFG.1``."""
    head, sep, tail = name.strip().partition(".")
    return f"{head.upper()}{sep}{tail}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check lineage names against the live nomenclature.",
    )
    parser.add_argument("names", nargs="+", help="lineage or clade names to resolve")
    parser.add_argument("--instance", default="sars-cov-2", help="registry name (default: sars-cov-2)")
    parser.add_argument("--base-url", help="any other LAPIS deployment")
    parser.add_argument("--lineage-field", help="override the auto-detected lineage column")
    parser.add_argument("--descendants", action="store_true",
                        help="list every descendant lineage instead of counting them")
    parser.add_argument("--no-counts", action="store_true",
                        help="skip the sequence counts (one fewer request per name)")
    parser.add_argument("--format", choices=("table", "tsv", "json"), default="table")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        base_url = resolve_base_url(args.instance, args.base_url)
        schema = describe_instance(base_url)
        lineage_field, has_index = pick_lineage_field(schema, args.lineage_field)
        # Fetched here, not inside the provenance f-string: a network failure at
        # print time would raise after the table had already been written.
        version = data_version(base_url)
    except LapisError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    definition: dict = {}
    if has_index:
        try:
            definition = lineage_definition(base_url, lineage_field)
        except LapisError as exc:
            print(f"warning: no lineage definition for {lineage_field}: {exc}", file=sys.stderr)

    aliases: dict = {}
    notes: dict = {}
    if lineage_field in PANGO_FIELDS:
        try:
            aliases = fetch_pango_aliases()
            notes = fetch_lineage_notes()
        except LapisError as exc:
            print(f"warning: pango-designation unreachable: {exc}", file=sys.stderr)

    # Inverted once: the SARS-CoV-2 definition holds ~5,500 entries, so
    # rebuilding it per name makes a list of lineages quadratic.
    children = children_map(definition)

    rows: list[dict] = []
    failures = 0
    for raw in args.names:
        name = normalise(raw)
        note = notes.get(name, {})
        in_definition = name in definition

        if note.get("status") == "withdrawn":
            status = "withdrawn"
        elif note.get("status") == "designated" or in_definition:
            status = "current"
        elif notes or definition:
            status = "unknown"
        else:
            status = "unverified"
        if status in {"withdrawn", "unknown"}:
            failures += 1

        detail = note.get("note", "")
        successor = REDESIGNATED.search(detail)
        if successor:
            detail = f"now {successor.group(1)}; {detail}"
        elif status == "unknown":
            detail = "no such name in the live nomenclature for this instance"

        chain = parent_chain(name, definition) if definition else []
        kids = descendants(name, definition, children) if definition else []

        sequences: object = ""
        if not args.no_counts:
            try:
                query = f"{name}*" if has_index else name
                sequences = count(base_url, {lineage_field: query})
            except LapisError as exc:
                # An indexed column rejects an unknown lineage outright rather
                # than answering 0 -- which is the one place a typo is caught
                # for you. An unindexed column would have returned 0 instead.
                sequences = "n/a" if "not a valid lineage" in str(exc) else "error"

        rows.append(
            {
                "query": raw,
                "status": status,
                "unaliased": unalias_full(name, aliases) if aliases else "",
                "parent": chain[0] if chain else "",
                "recombinant_of": "+".join(recombinant_parents(name, aliases)) if aliases else "",
                "descendants": ", ".join(kids) if args.descendants else len(kids),
                "sequences": sequences,
                "detail": detail,
            }
        )

    print(emit(rows, COLUMNS, args.format))
    sys.stdout.flush()

    if args.format != "json":
        print(
            f"\n# {schema['name']} via {base_url} | data version {version}"
            f"\n# lineage column {lineage_field}"
            f"{' with a lineage index' if has_index else ' with no lineage index'}"
            + (
                f"\n# nomenclature from pango-designation ({len(notes)} names, "
                f"{sum(1 for v in notes.values() if v['status'] == 'withdrawn')} withdrawn)"
                f"\n# source blobs {pango_provenance()}"
                if notes
                else ""
            )
            + ("\n# 'sequences' counts the lineage and its descendants" if has_index else ""),
            file=sys.stderr,
        )
        others = [n for n, _ in lineage_field_candidates(schema) if n != lineage_field]
        if others:
            print(
                f"# other lineage-like columns here: {', '.join(others)} "
                f"(select one with --lineage-field)",
                file=sys.stderr,
            )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
```
