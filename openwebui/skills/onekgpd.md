---
name: onekgpd
description: >
---

# OneKGPd: Individual-Level Queries over the 1000 Genomes Project

## Scope

This skill queries the 1000 Genomes Project dataset — the extended high-coverage cohort
of 3,202 whole-genome-sequenced individuals, on the GRCh38 assembly. All results
are drawn from this cohort, and sample names returned by the skill (for example
`HG00096` or `NA21130`) identify its participants.

Queries resolve against the cohort's per-individual genotype data. This supports
two complementary classes of question: selecting **variants** carried within a
region (across the whole cohort or within a specified set of individuals), and
selecting the **individuals** who carry variants matching given criteria.
Variant selection can be filtered by allele frequency, predicted consequence,
clinical significance, AlphaMissense classification, and the other annotation
axes listed below. Relatedness between two named individuals is also available.

The genotype state in which a variant is carried — heterozygous or homozygous —
is a criterion that queries may specify; results are returned as variants or as
sample names, not as raw genotypes.

## When to Use

**Use this skill when you need to:**

-   Find **variants** carried in a region or set of regions matching some criteria
    across the whole cohort (`select-variants`).
-   Find **variants** carried in a region or set of regions matching some criteria
    in specific set of individuals (`select-variants-in-samples`).
-   Find **which 1000 Genomes individuals** carry variants matching some criteria
    in a region or set of regions (`select-samples`).
-   Count how many individuals carry specific variants (`count-samples`).
-   Restrict any variant query to **heterozygous-only or homozygous-only**
    carriage, or query both together (default).
-   Identify which individuals are **homozygous reference** at a single position
    (`select-samples-hom-ref`).
-   Determine the **relatedness** between two named 1000 Genomes individuals —
    both the degree (twin / 1st / 2nd / 3rd / unrelated) and the KING kinship
    coefficient (`kinship`).
-   Get **dataset totals** — sample count, sex split, variant count, assembly
    (`dataset-info`).
-   Variant selection can be specified by KGP allele frequency, gnomAD 4.1 exome and
    gnomAD 4.1 genome allele frequency, AlphaMissense Score and AlphaMissense Class,
    ClinVar significance (202502), and VEP annotations (impact, biotype, feature type,
    variant class, consequences).

**Do NOT use this skill for:**

-   Resolving a gene symbol, rsID, or transcript to coordinates, or fetching
    reference sequence. Resolve coordinates first (see Coordinate Provenance
    below), then query this skill with the resolved GRCh38 region.
-   Any cohort other than the 1000 Genomes Project — this skill serves only that
    dataset.

## Prerequisites

1.  **`uv`**: This skill's script is run with `uv run`, which reads the script's
    inline dependency metadata and provisions an ephemeral environment. Ensure
    `uv` is installed and on PATH (https://docs.astral.sh/uv/).
2.  **Data use terms**: The 1000 Genomes Project data is open; users should be
    aware of the 1000 Genomes Project / IGSR data-use terms
    (https://www.internationalgenome.org/data).
3.  **Access constraints**: There is no API key, no `.env` file, and no
    rate-limit token to configure.
4.  **No credentials required**

## Core Rules

-   **Use the Wrappers**: ALWAYS execute the provided helper scripts rather than
    constructing your own client calls or network requests. Use
    `scripts/onekgpd_api.py` for variant/sample/kinship queries (it handles the
    connection, streaming, pagination, and JSON serialization), and
    `scripts/onekgpd_meta.py` for sample/population metadata (offline, see
    [Sample & population metadata](#sample--population-metadata-offline)).
-   **Coordinates MUST be resolved against an authoritative source first** — see
    [Coordinate Provenance](#coordinate-provenance-mandatory-first-step). This
    is mandatory, not advisory.
-   **Count before you select**: every variant and sample selection has a paired
    counting command. Call the count command FIRST to size the result set, then
    select only if the count is manageable.
-   **Zygosity defaults to both**: selection and counting commands include both
    heterozygous and homozygous carriage by default. Narrow with `--het-only`
    or `--hom-only` when the question is specifically about one state. (You do
    not need to pass anything to get both.)
-   **Output**: scripts write full JSON to a file (`--output`, default under
    `/tmp/`) and print a concise summary to stdout. Do not read large JSON files
    into context — use `jq` or a small disposable `uv run python` snippet to
    extract fields.

## Coordinate Provenance (MANDATORY FIRST STEP)

Before any region-based query, resolve the gene or feature to **GRCh38**
coordinates against an authoritative source (for example Ensembl), and query
with those resolved coordinates. The assembly must be explicit, and a gene-range
must be resolved to precise positions before use. This is structural, not
advisory: there is no source-side guardrail that would catch a misplaced region,
so an unverified coordinate produces results for an unintended location with no
error.

```bash
# Resolve gene symbol -> GRCh38 region with an authoritative source FIRST,
# then pass the verified coordinates to the OneKGPd query below.
```

> [!CAUTION]
> The dataset is GRCh38. A GRCh37 coordinate, or any region that does not
> correctly correspond to the intended feature on GRCh38, will return
> results for an unintended location without raising an error. Verify the
> assembly and the resolved coordinates before querying.

## Command Selection Guide

Match the question to the command. Counting commands are cheap and should
precede their selection counterpart.

-   Which individuals carry matching variants in a region → `count-samples`
    then `select-samples`
-   Which variants are carried in a region, cohort-wide → `count-variants`
    then `select-variants`
-   Which variants are carried in a region, within a named set of individuals →
    `count-variants-in-samples` then `select-variants-in-samples`
-   Who is homozygous-reference at a single position → `count-samples-hom-ref`
    then `select-samples-hom-ref`
-   Relatedness (degree + coefficient) between two named individuals →
    `kinship`
-   Dataset totals (sample count, sex split, variant total, assembly) →
    `dataset-info`

## Annotation filters (shared across variant and sample selection/counting)

All variant- and sample-selection commands (`count-variants`,
`select-variants`, their `-in-samples` forms, `count-samples`, `select-samples`)
accept the same annotation filters. Different filter fields are combined with
**AND**; multiple values within one field are combined with **OR**. Enum values
are case-insensitive (e.g. `missense_variant` or `MISSENSE_VARIANT`).

These are selection criteria applied on the server. The fields returned on a
selected variant are listed under
[Variant-returning commands](#variant-returning-commands); a criterion used for
filtering is not necessarily echoed back on the returned variant.

-   `--af-lt` / `--af-gt`: 1000 Genomes dataset allele frequency bounds
-   `--gnomad-exomes-af-lt` / `--gnomad-exomes-af-gt`: gnomAD v4.1 exome AF bounds
-   `--gnomad-genomes-af-lt` / `--gnomad-genomes-af-gt`: gnomAD v4.1 genome AF bounds
-   `--clin-significance`: ClinVar significance terms, CSV (e.g. `PATHOGENIC,LIKELY_PATHOGENIC`)
-   `--consequence`: Sequence Ontology consequence terms, CSV (e.g. `MISSENSE_VARIANT,STOP_GAINED`)
-   `--impact`: VEP impact, CSV (`HIGH,MODERATE,LOW,MODIFIER`)
-   `--variant-type`, `--feature-type`, `--bio-type`: SO variant class / VEP feature / VEP biotype, CSV
-   `--alpha-missense-class`: `AM_LIKELY_BENIGN,AM_LIKELY_PATHOGENIC,AM_AMBIGUOUS` (CSV)
-   `--alpha-missense-score-lt` / `--alpha-missense-score-gt`: AlphaMissense score bounds
-   `--biallelic-only` / `--multiallelic-only`
-   `--exclude-males` / `--exclude-females`
-   `--min-len-bp` / `--max-len-bp`: alternate-allele length bounds (bp)

> [!NOTE]
> `--alpha-missense-class` and `--alpha-missense-score-*` are mutually exclusive
> (the engine ignores the class when a score bound is set). `--biallelic-only`
> and `--multiallelic-only` are mutually exclusive. `--exclude-males` and
> `--exclude-females` are mutually exclusive. Setting a `*-gt` bound greater than
> or equal to its matching `*-lt` bound defines an empty range and will return
> nothing.

> [!NOTE]
> Allele-frequency fields use `0.0` to mean "not present in that source." So
> `--gnomad-exomes-af-gt 0` selects variants that *are* in gnomAD exomes; a
> returned `gnomad_exomes_af` of `0.0` means the variant is absent from gnomAD
> exomes. The same convention for gnomAD genomes AF.
> Conversely, `--gnomad-exomes-af-lt` / `--gnomad-genomes-af-lt` bounds **include**
unannotated variants: "AF < X in gnomAD" includes variants with gnomAD AF = 0,
i.e. unannotated; pair it with `--gnomad-*-af-gt 0` to require presence in gnomAD.

> [!NOTE]
> `am_score` of `0.0` means not scored or not annotated by AlphaMissense - it does not mean `benign`.
> A real AlphaMissense score is always greater than 0.

## Quick Start

```bash
# Step 1. Resolve coordinates against an authoritative source — see Coordinate Provenance.
#    example: BRCA1: chr17:43044292-43170245
# Step 2. Size the result set: how many individuals carry predicted likely-pathogenic
#    missense variants in this region?
uv run scripts/onekgpd_api.py count-samples \
  --chrom chr17 --start 43044292 --end 43170245 \
  --consequence MISSENSE_VARIANT \
  --alpha-missense-class AM_LIKELY_PATHOGENIC \
  --output /tmp/count.json
# Step 3. If the count is manageable, list those individuals.
uv run scripts/onekgpd_api.py select-samples \
  --chrom chr17 --start 43044292 --end 43170245 \
  --consequence MISSENSE_VARIANT \
  --alpha-missense-class AM_LIKELY_PATHOGENIC \
  --output /tmp/samples.json
# Step 4: For that set of individuals, see the actual variants they carry.
uv run scripts/onekgpd_api.py select-variants-in-samples \
  --chrom chr17 --start 43044292 --end 43170245 \
  --samples HG03169,NA20506 \
  --consequence MISSENSE_VARIANT --alpha-missense-class AM_LIKELY_PATHOGENIC \
  --output /tmp/variants.json
```

## Commands

Each command writes full JSON to a file (`--output PATH`, default a temp file)
and prints a concise stdout summary. All region/sample commands share: the
region input (`--chrom`/`--start`/`--end` with optional `--ref`/`--alt`, or one
or more repeated `--region CHR:START-END`), the zygosity flags
(`--het-only`/`--hom-only`, default both), and the annotation filters above.
The full per-flag tables live in
[references/onekgpd_commands.md](references/onekgpd_commands.md).

### Variant-returning commands

`select-*` return matching variants; `count-*` return an integer count.

-   `count-variants` — count variants in a region, cohort-wide.
-   `select-variants` — select variants in a region, cohort-wide. Use `--limit N`
    (hard cap, default 200) **or** `--page-size N` (retrieve the full set in
    pages); the two are mutually exclusive. The summary flags `truncated` when
    the cap is reached.
-   `count-variants-in-samples` — as `count-variants`, restricted to
    `--samples NAME1,NAME2,...` (required).
-   `select-variants-in-samples` — as `select-variants`, restricted to
    `--samples NAME1,NAME2,...` (required).

Each returned variant carries these 22 keys: `chr`, `start`, `end`, `ref`,
`alt`, `af`, `ac`, `an`, `hom_samples`, `het_samples`, `mis_samples`,
`hom_samples_fx`, `het_samples_fx`, `mis_samples_fx`, `hom_samples_mxy`,
`het_samples_mxy`, `mis_samples_mxy`, `gnomad_exomes_af`, `gnomad_genomes_af`,
`am_score`, `amino_acids`, `biallelic`.
ClinVar significance and VEP consequence are filter criteria only and are not
returned. Full schema:
[references/onekgpd_commands.md](references/onekgpd_commands.md).

### Sample-returning commands

-   `count-samples` — count individuals carrying a matching variant in a region.
-   `select-samples` — list the names of individuals carrying a matching variant.
    Supports `--skip N` and `--limit N`. Returns names only; to see which
    variants qualified an individual, feed the names into
    `select-variants-in-samples`.

### Homozygous-reference commands

Single position via `--chrom` + `--position` (not a region).

-   `count-samples-hom-ref` — count individuals with a 0/0 call at the position.
    The count is a sentinel: `-1` = no variant exists at that position at all;
    `0` = a variant exists but no individual is homozygous reference; `>0` = the
    number of homozygous-reference individuals. The summary states which case.
-   `select-samples-hom-ref` — list the individuals with a 0/0 call at the position.

### Relatedness command

-   `kinship --sample1 NAME --sample2 NAME` — relatedness between two named
    individuals: the degree (`TWINS_MONOZYGOTIC` / `FIRST_DEGREE` /
    `SECOND_DEGREE` / `THIRD_DEGREE` / `UNRELATED`) and the KING kinship
    coefficient (`phi_bwf`).

### Dataset metadata command

-   `dataset-info` — dataset totals: `samples_total` (3,202), female/male split,
    `variants_total`, `assembly` (GRCh38), and the cohort breakdown. No region
    required; doubles as a connectivity check.

## Sample & population metadata (offline)

Population, sex, pedigree, and superpopulation questions are answered by a second
script, `scripts/onekgpd_meta.py`, from a data file bundled in the skill — **no
network, no credentials, no coordinates**. The sample IDs are the same names the
variant commands use, so the two layers compose (e.g. pick a cohort by population,
then query its variants). Run `uv run scripts/onekgpd_meta.py <command>`.

The cohort has 5 superpopulations (`AFR`, `AMR`, `EAS`, `EUR`, `SAS`) and 26
populations. Population/superpopulation values match **case-insensitively** by
short code or full name; **sample IDs are case-sensitive**.

-   `sample-metadata --samples NA19240,HG00096` — family, gender, parents,
    children, population, superpopulation, and phase3 status for the given samples.
-   `list-populations` — all 26 populations with superpopulation and sample count
    (use to discover valid values).
-   `list-superpopulations` — the 5 superpopulations with sample count and
    constituent populations.
-   `population-stats --populations YRI [--populations CHS …]` — per-population sex
    split, phase3 count, and trio membership. Repeat `--populations` for multiple
    values (full names contain commas, so they are not comma-separated).
-   `superpopulation-summary --superpopulations EAS [--superpopulations EUR …]` —
    per-superpopulation totals with a per-population breakdown.
-   `select-samples-by-population --population YRI` and/or `--superpopulation AFR`,
    with optional `--skip`/`--limit` (default 0 / 50, max 3202) — the sample IDs in
    a population and/or superpopulation; both given intersects. Feed the names into
    `select-variants-in-samples` to see their variants.

See [references/onekgpd_commands.md](references/onekgpd_commands.md) for full
argument tables and JSON output schemas.

## Typical Workflows

### Which individuals, then which variants they carry

```bash
# Step 1: resolve gene -> verified GRCh38 region (authoritative source).
# Step 2: count individuals carrying a qualifying variant in the region.
uv run scripts/onekgpd_api.py count-samples \
  --chrom <chr> --start <start> --end <end> \
  --consequence MISSENSE_VARIANT --alpha-missense-class AM_LIKELY_PATHOGENIC \
  --output /tmp/n.json
# Step 3: list those individuals.
uv run scripts/onekgpd_api.py select-samples \
  --chrom <chr> --start <start> --end <end> \
  --consequence MISSENSE_VARIANT --alpha-missense-class AM_LIKELY_PATHOGENIC \
  --output /tmp/who.json
# Step 4: for that set of individuals, see the actual variants they carry.
uv run scripts/onekgpd_api.py select-variants-in-samples \
  --chrom <chr> --start <start> --end <end> \
  --samples <name1,name2,...> \
  --consequence MISSENSE_VARIANT --alpha-missense-class AM_LIKELY_PATHOGENIC \
  --output /tmp/variants.json
```

### Homozygous-reference carriers at a position of interest

```bash
# After identifying a position of interest (verified coordinate):
uv run scripts/onekgpd_api.py count-samples-hom-ref \
  --chrom <chr> --position <pos> --output /tmp/homref_n.json
uv run scripts/onekgpd_api.py select-samples-hom-ref \
  --chrom <chr> --position <pos> --output /tmp/homref.json
```

## Common Mistakes

-   **Mistake:** Querying with an unverified coordinate.
    **Fix:** Always resolve gene/feature → GRCh38 against an authoritative
    source first.
    A misplaced region returns results for an unintended location without error.
-   **Mistake:** Calling a selection command before its counting command.
    **Fix:** Count first; selection result sets can be large.
-   **Mistake:** Assuming a GRCh37 coordinate will work.
    **Fix:** The dataset is GRCh38 only.

## References

-   [references/onekgpd_commands.md](references/onekgpd_commands.md) — full
    per-command argument tables and the returned-variant output schema.
-   [references/annotation_vocabularies.md](references/annotation_vocabularies.md)
    — the controlled-vocabulary terms accepted by the CSV filter flags
    (consequence, impact, biotype, feature type, ClinVar significance,
    AlphaMissense class, variant class).
-   1000 Genomes Project / IGSR: https://www.internationalgenome.org/
-   1000 Genomes Project dataset online: https://dnaerys.org/online/

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/onekgpd/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

> Excluded (not usable as inline text — binary assets, vendored schemas, or bulk data): assets/kgpe.json

### `references/annotation_vocabularies.md`

# OneKGPd annotation vocabularies
Controlled-vocabulary terms accepted by the CSV annotation-filter flags of
`onekgpd_api.py`. Values are **case-insensitive** and resolved by exact member
name; pass them as comma-separated lists (e.g.
`--consequence MISSENSE_VARIANT,STOP_GAINED`). Multiple values within one flag
are combined with **OR**; different flags combine with **AND**.
> These lists are the complete set of valid tokens for each flag. A value not
> in the relevant list is rejected with an error listing the valid values.

## Consequence (SO consequence terms) — `--consequence`
41 terms:
- `TRANSCRIPT_ABLATION`
- `SPLICE_ACCEPTOR_VARIANT`
- `SPLICE_DONOR_VARIANT`
- `STOP_GAINED`
- `FRAMESHIFT_VARIANT`
- `STOP_LOST`
- `START_LOST`
- `TRANSCRIPT_AMPLIFICATION`
- `INFRAME_INSERTION`
- `INFRAME_DELETION`
- `MISSENSE_VARIANT`
- `PROTEIN_ALTERING_VARIANT`
- `SPLICE_REGION_VARIANT`
- `INCOMPLETE_TERMINAL_CODON_VARIANT`
- `START_RETAINED_VARIANT`
- `STOP_RETAINED_VARIANT`
- `SYNONYMOUS_VARIANT`
- `CODING_SEQUENCE_VARIANT`
- `MATURE_MIRNA_VARIANT`
- `FIVE_PRIME_UTR_VARIANT`
- `THREE_PRIME_UTR_VARIANT`
- `NON_CODING_TRANSCRIPT_EXON_VARIANT`
- `INTRON_VARIANT`
- `NMD_TRANSCRIPT_VARIANT`
- `NON_CODING_TRANSCRIPT_VARIANT`
- `UPSTREAM_GENE_VARIANT`
- `DOWNSTREAM_GENE_VARIANT`
- `TFBS_ABLATION`
- `TFBS_AMPLIFICATION`
- `TF_BINDING_SITE_VARIANT`
- `REGULATORY_REGION_ABLATION`
- `REGULATORY_REGION_AMPLIFICATION`
- `FEATURE_ELONGATION`
- `REGULATORY_REGION_VARIANT`
- `FEATURE_TRUNCATION`
- `INTERGENIC_VARIANT`
- `SPLICE_POLYPYRIMIDINE_TRACT_VARIANT`
- `SPLICE_DONOR_5TH_BASE_VARIANT`
- `SPLICE_DONOR_REGION_VARIANT`
- `CODING_TRANSCRIPT_VARIANT`
- `SEQUENCE_VARIANT`

## Impact (VEP impact) — `--impact`
4 terms:
- `HIGH`
- `MODERATE`
- `LOW`
- `MODIFIER`

## VariantType (SO variant class) — `--variant-type`
34 terms:
- `SNV`
- `INSERTION`
- `DELETION`
- `INDEL`
- `SUBSTITUTION`
- `INVERSION`
- `TRANSLOCATION`
- `DUPLICATION`
- `ALU_INSERTION`
- `COMPLEX_STRUCTURAL_ALTERATION`
- `COMPLEX_SUBSTITUTION`
- `COPY_NUMBER_GAIN`
- `COPY_NUMBER_LOSS`
- `COPY_NUMBER_VARIATION`
- `INTERCHROMOSOMAL_BREAKPOINT`
- `INTERCHROMOSOMAL_TRANSLOCATION`
- `INTRACHROMOSOMAL_BREAKPOINT`
- `INTRACHROMOSOMAL_TRANSLOCATION`
- `LOSS_OF_HETEROZYGOSITY`
- `MOBILE_ELEMENT_DELETION`
- `MOBILE_ELEMENT_INSERTION`
- `NOVEL_SEQUENCE_INSERTION`
- `SHORT_TANDEM_REPEAT_VARIATION`
- `TANDEM_DUPLICATION`
- `PROBE`
- `ALU_DELETION`
- `HERV_DELETION`
- `HERV_INSERTION`
- `LINE1_DELETION`
- `LINE1_INSERTION`
- `SVA_DELETION`
- `SVA_INSERTION`
- `COMPLEX_CHROMOSOMAL_REARRANGEMENT`
- `SEQUENCE_ALTERATION`

## FeatureType (VEP feature type) — `--feature-type`
3 terms:
- `TRANSCRIPT`
- `REGULATORYFEATURE`
- `MOTIFFEATURE`

## BioType (VEP biotype) — `--bio-type`
47 terms:
- `PROCESSED_TRANSCRIPT`
- `LNCRNA`
- `ANTISENSE`
- `MACRO_LNCRNA`
- `NON_CODING`
- `RETAINED_INTRON`
- `SENSE_INTRONIC`
- `SENSE_OVERLAPPING`
- `LINCRNA`
- `NCRNA`
- `MIRNA`
- `MISCRNA`
- `PIRNA`
- `RRNA`
- `SIRNA`
- `SNRNA`
- `SNORNA`
- `TRNA`
- `VAULTRNA`
- `PROTEIN_CODING`
- `PSEUDOGENE`
- `IG_PSEUDOGENE`
- `POLYMORPHIC_PSEUDOGENE`
- `PROCESSED_PSEUDOGENE`
- `TRANSCRIBED_PSEUDOGENE`
- `TRANSLATED_PSEUDOGENE`
- `UNITARY_PSEUDOGENE`
- `UNPROCESSED_PSEUDOGENE`
- `READTHROUGH`
- `STOP_CODON_READTHROUGH`
- `TEC`
- `TR_GENE`
- `TR_C_GENE`
- `TR_D_GENE`
- `TR_J_GENE`
- `TR_V_GENE`
- `IG_GENE`
- `IG_C_GENE`
- `IG_D_GENE`
- `IG_J_GENE`
- `IG_V_GENE`
- `NONSENSE_MEDIATED_DECAY`
- `PROMOTER`
- `PROMOTER_FLANKING_REGION`
- `ENHANCER`
- `CTCF_BINDING_SITE`
- `OPEN_CHROMATIN_REGION`

## ClinSignificance (ClinVar significance) — `--clin-significance`
19 terms:
- `CLNSIG_BENIGN`
- `LIKELY_BENIGN`
- `UNCERTAIN_SIGNIFICANCE`
- `LIKELY_PATHOGENIC`
- `PATHOGENIC`
- `DRUG_RESPONSE`
- `ASSOCIATION`
- `RISK_FACTOR`
- `PROTECTIVE`
- `AFFECTS`
- `CONFERS_SENSITIVITY`
- `CONFLICTING_INTERPRETATIONS`
- `NOT_PROVIDED`
- `OTHER`
- `LIKELY_PATHOGENIC_LOW_PENETRANCE`
- `PATHOGENIC_LOW_PENETRANCE`
- `UNCERTAIN_RISK_ALLELE`
- `LIKELY_RISK_ALLELE`
- `ESTABLISHED_RISK_ALLELE`

## AlphaMissense (class) — `--alpha-missense-class`
3 terms:
- `AM_LIKELY_BENIGN`
- `AM_LIKELY_PATHOGENIC`
- `AM_AMBIGUOUS`

## Notes

- ClinVar "benign" is the token `CLNSIG_BENIGN` (note the `CLNSIG_` prefix);
  all other ClinSignificance tokens are the bare term.
- AlphaMissense class is mutually exclusive with the AlphaMissense score bounds
  (`--alpha-missense-score-lt`/`-gt`): set one or the other, not both.

### `references/onekgpd_commands.md`

# OneKGPd command reference

Full argument tables for every `onekgpd_api.py` subcommand and the schema of a
returned variant. Run with `uv run scripts/onekgpd_api.py <command> [flags]`.

Coordinates are **GRCh38, 1-based inclusive**. Resolve a gene/feature to
coordinates against an authoritative source before querying. Every command
writes full JSON to a file (`--output PATH`, default a temp file) and prints a
short summary to stdout.

## Shared flags

### Connection / output (all commands)

| flag | type | required | default | description |
| --- | --- | --- | --- | --- |
| `--output` | path | no | temp file | Write full JSON here; otherwise a `onekgpd_<cmd>_*.json` temp file is created and its path printed. |

There is no endpoint, credential, assembly, or timeout flag: the skill targets
the public 1000 Genomes instance on GRCh38 only.

### Region input (count/select variants and samples)

Provide **either** a single region **or** one-or-more `--region`, not both.

| flag | type | required | default | description |
| --- | --- | --- | --- | --- |
| `--chrom` | str | single-region mode | – | Chromosome: `chr17`, `17`, `X`, `MT` (case-insensitive). |
| `--start` | int | with `--chrom` | – | 1-based inclusive start. |
| `--end` | int | with `--chrom` | – | 1-based inclusive end (≥ start). |
| `--ref` | str | no | – | Narrow to one reference allele (single-region only). |
| `--alt` | str | no | – | Narrow to one alternate allele (single-region only). |
| `--region` | `CHR:START-END` | multi-region mode | – | A region; repeat the flag for multiple regions. |
| `--min-len-bp` | int | no | – | Minimum alternate-allele length (bp). |
| `--max-len-bp` | int | no | – | Maximum alternate-allele length (bp). |

### Zygosity (count/select variants and samples)

| flag | type | required | default | description |
| --- | --- | --- | --- | --- |
| `--het-only` | switch | no | both | Include HETEROZYGOUS variants ONLY (0/1 genotypes). |
| `--hom-only` | switch | no | both | Include HOMOZYGOUS variants ONLY (1/1 genotypes). |

With no zygosity flag, both HETEROZYGOUS (0/1) and HOMOZYGOUS (1/1) carriage are
queried — use the default when you need homozygous OR heterozygous variants, or
when uncertain. `--het-only` and `--hom-only` are mutually exclusive.

### Annotation filters (count/select variants and samples)

See `annotation_vocabularies.md` for the valid CSV terms. Different filter fields
combine with **AND**; multiple CSV values within one field combine with **OR**.

| flag | type | maps to |
| --- | --- | --- |
| `--af-lt` / `--af-gt` | float | 1000 Genomes dataset AF bounds |
| `--gnomad-exomes-af-lt` / `--gnomad-exomes-af-gt` | float | gnomAD v4.1 exomes AF bounds |
| `--gnomad-genomes-af-lt` / `--gnomad-genomes-af-gt` | float | gnomAD v4.1 genomes AF bounds |
| `--clin-significance` | CSV | ClinVar significance terms |
| `--consequence` | CSV | SO consequence terms |
| `--impact` | CSV | VEP impact (HIGH,MODERATE,LOW,MODIFIER) |
| `--variant-type` | CSV | SO variant class terms |
| `--feature-type` | CSV | VEP feature types |
| `--bio-type` | CSV | VEP biotypes |
| `--alpha-missense-class` | CSV | AM_LIKELY_BENIGN,AM_LIKELY_PATHOGENIC,AM_AMBIGUOUS |
| `--alpha-missense-score-lt` / `--alpha-missense-score-gt` | float | AlphaMissense score bounds |
| `--biallelic-only` / `--multiallelic-only` | switch | site multiplicity (mutually exclusive) |
| `--exclude-males` / `--exclude-females` | switch | sex exclusion (mutually exclusive) |

Mutual exclusions enforced: `--biallelic-only`/`--multiallelic-only`,
`--exclude-males`/`--exclude-females`, and `--alpha-missense-class` vs the
AlphaMissense score bounds. Setting a `*-gt` ≥ its matching `*-lt` defines an
empty range and returns nothing.

The `--gnomad-exomes-af-lt` / `--gnomad-genomes-af-lt` bounds **include** unannotated
variants: "AF < X in gnomAD" includes variants with gnomAD AF = 0, i.e. unannotated;
pair it with `--gnomad-*-af-gt 0` to require presence in gnomAD.

---

## Commands

### `dataset-info`

No flags beyond `--output`. Returns dataset totals (sample count, sex split,
variant total, assembly) and the cohort breakdown. Doubles as a connectivity
check.

JSON: `{command, samples_total, females_total, males_total, variants_total,
assembly, cohorts:[{cohort_name, samples_count, female_count, male_count,
synthetic}]}`.

### `count-variants`

Region + zygosity + annotation flags. Counts variants in the region(s),
cohort-wide. JSON: `{command, count, request, result_incomplete}`.

### `select-variants`

SELECT variants which exist in ANY genomic region provided.

Region + zygosity + annotation flags, plus pagination:

| flag | type | required | default | description |
| --- | --- | --- | --- | --- |
| `--limit` | int | no | 200 | Hard cap on returned variants (mutually exclusive with `--page-size`). |
| `--page-size` | int | no | – | Retrieve ALL matching variants in pages of this size (full walk). |

JSON: `{command, count_returned, truncated, request, result_incomplete,
variants:[…]}`. `truncated` is true when the count hit `--limit` (more may
exist; raise `--limit` or use `--page-size`). Empty `variants` array if no
matches.

### `count-variants-in-samples`

As `count-variants`, plus `--samples CSV` (required) — counts variants carried
by the named individuals.

### `select-variants-in-samples`

As `select-variants`, plus `--samples CSV` (required) — selects variants carried
by the named individuals.

### `count-samples`

Region + zygosity + annotation flags. Counts how many individuals carry a
matching variant. JSON: `{command, count, request, result_incomplete}`.

### `select-samples`

Region + zygosity + annotation flags, plus pagination:

| flag | type | required | default | description |
| --- | --- | --- | --- | --- |
| `--skip` | int | no | – | Skip the first N individuals. |
| `--limit` | int | no | – | Return at most N individuals. |

Returns the **names** of individuals carrying a matching variant. To see which
variants qualified them, feed the names into `select-variants-in-samples`. JSON:
`{command, count, samples:[…], request, result_incomplete}`. Empty `samples` array
if no matches.

### `count-samples-hom-ref`

| flag | type | required | description |
| --- | --- | --- | --- |
| `--chrom` | str | yes | Chromosome. |
| `--position` | int | yes | 1-based position. |

Counts individuals with a homozygous-reference (0/0) call at the position. JSON:
`{command, count, variant_present, request}`. The count is a **sentinel**:

- `-1` → no variant exists at the position at all (`variant_present=false`).
- `0` → a variant exists, but no individual is homozygous reference.
- `>0` → number of homozygous-reference individuals.

### `select-samples-hom-ref`

Same `--chrom`/`--position` as above. Lists the individuals with a homozygous-
reference call at the position. JSON: `{command, count, samples:[…], request}`.

### `kinship`

| flag | type | required | description |
| --- | --- | --- | --- |
| `--sample1` | str | yes | First sample name. |
| `--sample2` | str | yes | Second sample name. |

Returns the relatedness degree and the KING kinship coefficient between the two
named individuals. JSON: `{command, sample1, sample2, degree, phi_bwf,
result_incomplete}`. `degree` ∈ `{TWINS_MONOZYGOTIC, FIRST_DEGREE,
SECOND_DEGREE, THIRD_DEGREE, UNRELATED}`; `phi_bwf` is the KING between-family
robust coefficient (≈ 0.5 monozygotic, 0.25 first-degree, 0.125 second-degree,
0.0625 third-degree).

---

## Returned-variant output schema

`select-variants` and `select-variants-in-samples` return a `variants` array;
each element has these keys (filter-only criteria such as ClinVar significance
and VEP consequence are **not** echoed back on a returned variant):

| key | type | meaning |
| --- | --- | --- |
| `chr` | str | Chromosome, e.g. `chr17`. |
| `start` | int | 1-based inclusive start. |
| `end` | int | 1-based inclusive end. |
| `ref` | str | Reference allele. |
| `alt` | str | Alternate allele. |
| `af` | float | Dataset allele frequency. |
| `ac` | float | Dataset allele count (0.5 for male non-PAR het calls on on X and Y chromosomes). |
| `an` | int | Dataset allele number. |
| `hom_samples` | int | Number of all samples with a homozygous genotype. |
| `het_samples` | int | Number of all samples with a heterozygous genotype. |
| `mis_samples` | int | Number of all samples with a missing (no-call) genotype. |
| `hom_samples_fx` | int | Number of female samples with a homozygous genotype, X chromosome only (0 outside X). |
| `het_samples_fx` | int | Number of female samples with a heterozygous genotype, X chromosome only (0 outside X). |
| `mis_samples_fx` | int | Number of female samples with a missing (no-call) genotype, X chromosome only (0 outside X). |
| `hom_samples_mxy` | int | Number of male samples with a homozygous genotype, X & Y chromosomes only (0 outside X and Y). |
| `het_samples_mxy` | int | Number of male samples with a heterozygous genotype, X & Y chromosomes only (0 outside X and Y). |
| `mis_samples_mxy` | int | Number of male samples with a missing (no-call) genotype, X & Y chromosomes only (0 outside X and Y). |
| `gnomad_exomes_af` | float | gnomAD v4.1 exomes AF. `0.0` = absent from gnomAD exomes. |
| `gnomad_genomes_af` | float | gnomAD v4.1 genomes AF. `0.0` = absent from gnomAD genomes. |
| `am_score` | float | AlphaMissense score. `0.0` = not annotated. |
| `amino_acids` | str | HGVSp Amino-acid substitution. |
| `biallelic` | bool | Whether the site was biallelic in the input VCFs. |

---

# Sample & population metadata commands (offline)

A second script, `scripts/onekgpd_meta.py`, answers population/pedigree questions
from a data file bundled in the skill (`assets/kgpe.json`) — **no network, no
credentials, no dependencies**. Run with
`uv run scripts/onekgpd_meta.py <command> [flags]`. The sample identifier is the
same name used by the variant/kinship commands (e.g. `NA19240`), so the two
layers compose (e.g. `select-samples-by-population` → `select-variants-in-samples`).

The 1000 Genomes cohort has **5 superpopulations** (`AFR` Africa, `AMR` America,
`EAS` East Asia, `EUR` Europe, `SAS` South Asia) and **26 populations**. Use
`list-populations` / `list-superpopulations` to discover valid codes and full
names. Population/superpopulation values are matched **case-insensitively**
against either the short code or the full name; **sample IDs are case-sensitive**.

All six commands write JSON to `--output` (or a temp file) and print a summary.

## `sample-metadata`

| flag | type | required | description |
| --- | --- | --- | --- |
| `--samples` | CSV | yes | Comma-separated sample IDs (case-sensitive), e.g. `NA19240,HG00096`. |

JSON: `{command, samples:[{...}]}` ordered by `sample_id`. Each sample object:

| key | type | meaning |
| --- | --- | --- |
| `sample_id` | str | Sample identifier (`externalIDs`). |
| `family_id` | str\|null | Family/pedigree ID; `null` if absent. |
| `gender` | str | `male` / `female`. |
| `paternal_id` | str\|null | Father's `sample_id`; `null` if not in the dataset. |
| `maternal_id` | str\|null | Mother's `sample_id`; `null` if not in the dataset. |
| `relationship` | str\|null | `mother` / `father` / `child` / `null`. |
| `children` | list[str] | Sorted children whose **both** parents are recorded; `[]` if none. |
| `population_code` | str | e.g. `YRI`. |
| `population` | str | e.g. `Yoruba in Ibadan, Nigeria`. |
| `superpopulation_code` | str | e.g. `AFR`. |
| `superpopulation` | str | e.g. `Africa`. |
| `phase3` | str | `"TRUE"` / `"FALSE"` (phase-3 inclusion flag). |

## `list-populations`

No flags. JSON: `{command, populations:[{population_code, population,
superpopulation_code, superpopulation, sample_count}]}`, ordered by
(superpopulation, population). 26 entries.

## `list-superpopulations`

No flags. JSON: `{command, superpopulations:[{superpopulation_code,
superpopulation, sample_count, populations:[codes]}]}`, ordered by
superpopulation. 5 entries.

## `population-stats`

| flag | type | required | description |
| --- | --- | --- | --- |
| `--populations` | repeatable | yes | One population code or full name per flag; repeat for multiple. Repeated (not CSV) because full names contain commas. Case-insensitive. |

JSON: `{command, populations:[{population_code, population, superpopulation_code,
superpopulation, sample_count, male_count, female_count, phase3_count,
trio_count}]}`, ordered by population. `trio_count` = samples that are offspring
with **both** parents in the dataset (not the `relationship` label).

## `superpopulation-summary`

| flag | type | required | description |
| --- | --- | --- | --- |
| `--superpopulations` | repeatable | yes | One superpopulation code or full name per flag; repeat for multiple. Case-insensitive. |

JSON: `{command, superpopulations:[{superpopulation_code, superpopulation,
sample_count, male_count, female_count, phase3_count, trio_count, populations:[
<population-stats object>]}]}`. The per-superpopulation counts are sums over the
nested per-population breakdown.

## `select-samples-by-population`

| flag | type | required | default | description |
| --- | --- | --- | --- | --- |
| `--population` | str | one of the two | – | Population code or full name (case-insensitive). |
| `--superpopulation` | str | one of the two | – | Superpopulation code or full name (case-insensitive). |
| `--skip` | int | no | 0 | Number of results to skip (≥ 0). |
| `--limit` | int | no | 50 | Max results to return (1–3202). |

At least one of `--population` / `--superpopulation` is required; when both are
given the results are intersected (AND). JSON: `{command, count, samples:[ids],
request:{population, superpopulation, skip, limit}}`, sample IDs ordered
ascending then paginated by `skip`/`limit`.

### `scripts/onekgpd_api.py`

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["dnaerys>=0.2.1,<0.3.0"]
# ///
"""OneKGPd — individual-level queries over the 1000 Genomes Project.

A single command-line wrapper exposing ten subcommands over the 1000 Genomes
Project cohort (3,202 whole-genome-sequenced individuals, GRCh38): selecting and
counting variants in a region (cohort-wide or within named individuals),
selecting and counting the individuals who carry matching variants, homozygous-
reference queries at a single position, pairwise relatedness, and dataset totals.

Every command writes full JSON to a file (``--output``, or a temp file by
default) and prints a concise human-readable summary to stdout. Coordinates are
GRCh38, 1-based inclusive; resolve a gene/feature to coordinates against an
authoritative source BEFORE querying.

Examples
--------
    uv run scripts/onekgpd_api.py dataset-info
    uv run scripts/onekgpd_api.py count-samples --chrom chr17 --start 43044292 --end 43170245 \
        --consequence MISSENSE_VARIANT --alpha-missense-class AM_LIKELY_PATHOGENIC
    uv run scripts/onekgpd_api.py kinship --sample1 NA19238 --sample2 NA19240

MIT License. Author: Dnaerys.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import warnings
from typing import Any, NoReturn

from dnaerys import (
    AnnotationFilter,
    DnaerysError,
    DnaerysIncompleteResultWarning,
    DnaerysClient,
    Region,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_ENDPOINT = "db.dnaerys.org:443"   # public 1000 Genomes instance (fixed)
DEFAULT_VARIANT_LIMIT = 200               # hard cap when neither --limit nor --page-size given
MAX_RETRIES = 3                           # bounded retry attempts on retryable errors
RETRY_BASE_DELAY = 1.0                    # seconds; exponential backoff: 1, 2, ...
PREVIEW_ROWS = 10                         # rows shown in a stdout summary preview

INCOMPLETE_NOTE = "[!] Result may be incomplete: some data was unreachable."


# ---------------------------------------------------------------------------
# Small generic helpers
# ---------------------------------------------------------------------------


def _fail(msg: str) -> NoReturn:
    """Print a clean one-line message to stderr and exit non-zero."""
    print(msg, file=sys.stderr)
    sys.exit(1)


def _split_csv(s: str) -> list[str]:
    """Split a comma-separated value into a list of non-empty trimmed tokens."""
    return [part.strip() for part in s.split(",") if part.strip()]


def _save_json(data: Any, prefix: str, output_path: str | None = None) -> str:
    """Write *data* as indented JSON to *output_path* or a temp file; return path."""
    if output_path:
        path = output_path
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
    else:
        fd, path = tempfile.mkstemp(prefix=f"onekgpd_{prefix}_", suffix=".json", text=True)
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
    return path


def _emit(data: Any, prefix: str, summary_lines: list[str], output: str | None) -> None:
    """Save full JSON to a file and print the summary + saved-path line to stdout."""
    path = _save_json(data, prefix, output)
    for line in summary_lines:
        print(line)
    print(f"[*] Full JSON saved to {path}")


def _call_with_retry(fn):
    """Run *fn*; on a retryable ``DnaerysError`` retry with bounded backoff.

    The whole fetch-and-materialize closure is retried (a fresh client per
    attempt), so streaming errors that surface during iteration are covered.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return fn()
        except DnaerysError as e:
            if e.is_retryable and attempt < MAX_RETRIES:
                time.sleep(RETRY_BASE_DELAY * (2 ** (attempt - 1)))
                continue
            raise


# ---------------------------------------------------------------------------
# Input builders
# ---------------------------------------------------------------------------


def _parse_region_str(s: str) -> Region:
    """Parse ``CHR:START-END`` into a ``Region`` (coordinate validation deferred)."""
    try:
        chrom, span = s.split(":", 1)
        start_s, end_s = span.split("-", 1)
        start, end = int(start_s), int(end_s)
    except ValueError:
        raise ValueError(
            f"invalid --region {s!r}; expected CHR:START-END, "
            "e.g. chr17:43044292-43170245"
        )
    return Region(chrom, start, end)


def _build_regions(args) -> tuple[Region | None, list[Region] | None]:
    """Return exactly one of (single Region, None) or (None, list[Region])."""
    has_single = args.chrom is not None
    has_multi = bool(args.region)
    if has_single and has_multi:
        raise ValueError("use either --chrom/--start/--end or --region, not both")
    if not has_single and not has_multi:
        raise ValueError(
            "a region is required: pass --chrom/--start/--end or "
            "one or more --region CHR:START-END"
        )
    if has_multi:
        if args.ref or args.alt:
            raise ValueError(
                "--ref/--alt apply only to a single --chrom/--start/--end region"
            )
        return None, [_parse_region_str(r) for r in args.region]
    if args.start is None or args.end is None:
        raise ValueError("--chrom requires --start and --end")
    return Region(args.chrom, args.start, args.end, ref=args.ref, alt=args.alt), None


def _zygosity(args) -> tuple[bool, bool]:
    """Return (hom, het); default both True, narrowed by --het-only/--hom-only."""
    if getattr(args, "het_only", False):
        return (False, True)
    if getattr(args, "hom_only", False):
        return (True, False)
    return (True, True)


_CSV_FIELDS = [
    ("clin_significance", "clin_significance"),
    ("consequence", "consequence"),
    ("impact", "impact"),
    ("variant_type", "variant_type"),
    ("feature_type", "feature_type"),
    ("bio_type", "bio_type"),
    ("alpha_missense_class", "am_class"),
]
_FLOAT_FIELDS = [
    ("af_lt", "af_lt"),
    ("af_gt", "af_gt"),
    ("gnomad_exomes_af_lt", "gnomad_exomes_af_lt"),
    ("gnomad_exomes_af_gt", "gnomad_exomes_af_gt"),
    ("gnomad_genomes_af_lt", "gnomad_genomes_af_lt"),
    ("gnomad_genomes_af_gt", "gnomad_genomes_af_gt"),
    ("alpha_missense_score_lt", "am_score_lt"),
    ("alpha_missense_score_gt", "am_score_gt"),
]
_BOOL_FIELDS = [
    ("biallelic_only", "biallelic_only"),
    ("multiallelic_only", "multiallelic_only"),
    ("exclude_males", "exclude_males"),
    ("exclude_females", "exclude_females"),
]


def _build_annotation_filter(args) -> AnnotationFilter | None:
    """Map the shared annotation flags to an ``AnnotationFilter`` (or None).

    Note: ``--min-len-bp``/``--max-len-bp`` are NOT filter fields; they are passed
    as the client method's ``variant_min_length``/``variant_max_length`` kwargs.
    """
    kwargs: dict[str, Any] = {}
    for arg_name, field in _CSV_FIELDS:
        raw = getattr(args, arg_name, None)
        if raw:
            kwargs[field] = _split_csv(raw)
    for arg_name, field in _FLOAT_FIELDS:
        val = getattr(args, arg_name, None)
        if val is not None:
            kwargs[field] = val
    for arg_name, field in _BOOL_FIELDS:
        if getattr(args, arg_name, False):
            kwargs[field] = True

    # am-class vs am-score cannot be one argparse group (am-score is a range pair).
    if kwargs.get("am_class") and ("am_score_lt" in kwargs or "am_score_gt" in kwargs):
        _fail(
            "Error: --alpha-missense-class cannot be combined with "
            "--alpha-missense-score-lt/--alpha-missense-score-gt"
        )

    if not kwargs:
        return None
    return AnnotationFilter(**kwargs)


# ---------------------------------------------------------------------------
# Display / serialization helpers
# ---------------------------------------------------------------------------


def _chr_to_str(chrom) -> str:
    """Render a ``Chromosome`` enum as ``chr17`` / ``chrX`` / ``chrMT``."""
    return "chr" + chrom.name[len("CHR"):]


def _region_one_label(r: Region) -> str:
    return f"{_chr_to_str(r.chr)}:{r.start}-{r.end}"


def _region_label(region: Region | None, regions: list[Region] | None) -> str:
    if region is not None:
        return _region_one_label(region)
    return ", ".join(_region_one_label(r) for r in regions or [])


def _zyg_label(hom: bool, het: bool) -> str:
    if hom and het:
        return "hom+het"
    if het:
        return "het only"
    return "hom only"


def _variant_to_dict(v) -> dict:
    """Serialize a ``Variant`` to its in-scope output keys (enum rendered as text)."""
    return {
        "chr": _chr_to_str(v.chr),
        "start": v.start,
        "end": v.end,
        "ref": v.ref,
        "alt": v.alt,
        "af": v.af,
        "ac": v.ac,
        "an": v.an,
        "hom_samples": v.hom_samples,
        "het_samples": v.het_samples,
        "mis_samples": v.mis_samples,
        "hom_samples_fx": v.hom_samples_fx,
        "het_samples_fx": v.het_samples_fx,
        "mis_samples_fx": v.mis_samples_fx,
        "hom_samples_mxy": v.hom_samples_mxy,
        "het_samples_mxy": v.het_samples_mxy,
        "mis_samples_mxy": v.mis_samples_mxy,
        "gnomad_exomes_af": v.gnomad_exomes_af,
        "gnomad_genomes_af": v.gnomad_genomes_af,
        "am_score": v.am_score,
        "amino_acids": v.amino_acids,
        "biallelic": v.biallelic,
    }


def _filters_echo(args) -> dict:
    """Echo the annotation/length flags that were actually set (for provenance)."""
    out: dict[str, Any] = {}
    for arg_name, _ in _FLOAT_FIELDS:
        val = getattr(args, arg_name, None)
        if val is not None:
            out[arg_name] = val
    for arg_name, _ in _CSV_FIELDS:
        raw = getattr(args, arg_name, None)
        if raw:
            out[arg_name] = _split_csv(raw)
    for arg_name, _ in _BOOL_FIELDS:
        if getattr(args, arg_name, False):
            out[arg_name] = True
    if getattr(args, "min_len_bp", None) is not None:
        out["variant_min_length"] = args.min_len_bp
    if getattr(args, "max_len_bp", None) is not None:
        out["variant_max_length"] = args.max_len_bp
    return out


def _request_echo(args, *, samples, region, regions, hom, het) -> dict:
    """Build the request-provenance block included in every region-command JSON."""
    req: dict[str, Any] = {}
    if region is not None:
        req["region"] = _region_one_label(region)
        if region.ref:
            req["ref"] = region.ref
        if region.alt:
            req["alt"] = region.alt
    if regions is not None:
        req["regions"] = [_region_one_label(r) for r in regions]
    if samples is not None:
        req["samples"] = samples
    req["zygosity"] = _zyg_label(hom, het)
    filt = _filters_echo(args)
    if filt:
        req["filters"] = filt
    return req


# ---------------------------------------------------------------------------
# Command workers / handlers
# ---------------------------------------------------------------------------


def _run_count_variants(args, samples: list[str] | None) -> None:
    region, regions = _build_regions(args)
    hom, het = _zygosity(args)
    ann = _build_annotation_filter(args)

    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            return client.count_variants(
                region=region,
                regions=regions,
                samples=samples,
                hom=hom,
                het=het,
                annotations=ann,
                variant_min_length=args.min_len_bp,
                variant_max_length=args.max_len_bp,
            )

    result = _call_with_retry(fetch)
    incomplete = result.metadata.affected
    data = {
        "command": args.command,
        "count": result.count,
        "request": _request_echo(
            args, samples=samples, region=region, regions=regions, hom=hom, het=het
        ),
        "result_incomplete": incomplete,
    }
    summary = [
        f"{result.count:,} variants match in {_region_label(region, regions)} "
        f"({_zyg_label(hom, het)})"
    ]
    if incomplete:
        summary.append(INCOMPLETE_NOTE)
    _emit(data, args.command.replace("-", "_"), summary, args.output)


def _run_select_variants(args, samples: list[str] | None) -> None:
    region, regions = _build_regions(args)
    hom, het = _zygosity(args)
    ann = _build_annotation_filter(args)
    page_size = args.page_size
    limit = args.limit

    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            if page_size is not None:
                pq = client.paginate_variants(
                    page_size=page_size,
                    region=region,
                    regions=regions,
                    samples=samples,
                    hom=hom,
                    het=het,
                    annotations=ann,
                    variant_min_length=args.min_len_bp,
                    variant_max_length=args.max_len_bp,
                )
                collected = []
                for page in pq:
                    collected.extend(page.variants)
                return collected, pq.metadata, False
            stream = client.select_variants(
                region=region,
                regions=regions,
                samples=samples,
                hom=hom,
                het=het,
                annotations=ann,
                variant_min_length=args.min_len_bp,
                variant_max_length=args.max_len_bp,
                limit=limit,
            )
            collected = stream.to_list()
            truncated = limit is not None and len(collected) >= limit
            return collected, stream.metadata, truncated

    variants, meta, truncated = _call_with_retry(fetch)
    incomplete = meta.affected
    request = _request_echo(
        args, samples=samples, region=region, regions=regions, hom=hom, het=het
    )
    if page_size is not None:
        request["page_size"] = page_size
    else:
        request["limit"] = limit
    data = {
        "command": args.command,
        "count_returned": len(variants),
        "truncated": truncated,
        "request": request,
        "result_incomplete": incomplete,
        "variants": [_variant_to_dict(v) for v in variants],
    }
    summary = [
        f"Returned {len(variants)} variants in {_region_label(region, regions)} "
        f"({_zyg_label(hom, het)})"
    ]
    for v in variants[:PREVIEW_ROWS]:
        summary.append(
            f"  {_chr_to_str(v.chr)}:{v.start} {v.ref}>{v.alt}  "
            f"af={v.af:.6g}  am_score={v.am_score:.6g}  aa={v.amino_acids or '-'}"
        )
    if not variants:
        summary.append("  (no variants matched)")
    if truncated:
        summary.append(
            f"[!] Truncated at --limit {limit}; raise --limit or use "
            "--page-size to retrieve the full set."
        )
    if incomplete:
        summary.append(INCOMPLETE_NOTE)
    _emit(data, args.command.replace("-", "_"), summary, args.output)


def cmd_count_variants(args) -> None:
    _run_count_variants(args, samples=None)


def cmd_count_variants_in_samples(args) -> None:
    _run_count_variants(args, samples=_split_csv(args.samples))


def cmd_select_variants(args) -> None:
    _run_select_variants(args, samples=None)


def cmd_select_variants_in_samples(args) -> None:
    _run_select_variants(args, samples=_split_csv(args.samples))


def cmd_count_samples(args) -> None:
    region, regions = _build_regions(args)
    hom, het = _zygosity(args)
    ann = _build_annotation_filter(args)

    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            return client.count_samples(
                region=region,
                regions=regions,
                hom=hom,
                het=het,
                annotations=ann,
                variant_min_length=args.min_len_bp,
                variant_max_length=args.max_len_bp,
            )

    result = _call_with_retry(fetch)
    incomplete = result.metadata.affected
    data = {
        "command": args.command,
        "count": result.count,
        "request": _request_echo(
            args, samples=None, region=region, regions=regions, hom=hom, het=het
        ),
        "result_incomplete": incomplete,
    }
    summary = [
        f"{result.count:,} individuals carry a matching variant in "
        f"{_region_label(region, regions)} ({_zyg_label(hom, het)})"
    ]
    if incomplete:
        summary.append(INCOMPLETE_NOTE)
    _emit(data, "count_samples", summary, args.output)


def cmd_select_samples(args) -> None:
    region, regions = _build_regions(args)
    hom, het = _zygosity(args)
    ann = _build_annotation_filter(args)

    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            return client.select_samples(
                region=region,
                regions=regions,
                hom=hom,
                het=het,
                annotations=ann,
                variant_min_length=args.min_len_bp,
                variant_max_length=args.max_len_bp,
                skip=args.skip,
                limit=args.limit,
            )

    result = _call_with_retry(fetch)
    names = list(result.samples)
    incomplete = result.metadata.affected
    request = _request_echo(
        args, samples=None, region=region, regions=regions, hom=hom, het=het
    )
    if args.skip is not None:
        request["skip"] = args.skip
    if args.limit is not None:
        request["limit"] = args.limit
    data = {
        "command": args.command,
        "count": len(names),
        "samples": names,
        "request": request,
        "result_incomplete": incomplete,
    }
    summary = [
        f"{len(names)} individuals carry a matching variant in "
        f"{_region_label(region, regions)} ({_zyg_label(hom, het)})"
    ]
    for name in names[:PREVIEW_ROWS]:
        summary.append(f"  {name}")
    if not names:
        summary.append("  (none)")
    if incomplete:
        summary.append(INCOMPLETE_NOTE)
    _emit(data, "select_samples", summary, args.output)


def cmd_count_samples_hom_ref(args) -> None:
    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            return client.count_samples_hom_ref(chr=args.chrom, position=args.position)

    result = _call_with_retry(fetch)
    count = result.count
    present = count != -1
    pos = f"{args.chrom}:{args.position}"
    data = {
        "command": args.command,
        "count": count,
        "variant_present": present,
        "request": {"chrom": args.chrom, "position": args.position},
    }
    if count == -1:
        summary = [
            f"No variant exists at {pos} in the dataset; "
            "homozygous-reference count is undefined here."
        ]
    elif count == 0:
        summary = [
            f"A variant exists at {pos}, but no individual is homozygous reference."
        ]
    else:
        summary = [f"{count:,} individuals are homozygous reference at {pos}."]
    _emit(data, "count_samples_hom_ref", summary, args.output)


def cmd_select_samples_hom_ref(args) -> None:
    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            return client.select_samples_hom_ref(chr=args.chrom, position=args.position)

    result = _call_with_retry(fetch)
    names = list(result.samples)
    pos = f"{args.chrom}:{args.position}"
    data = {
        "command": args.command,
        "count": len(names),
        "samples": names,
        "request": {"chrom": args.chrom, "position": args.position},
    }
    summary = [f"{len(names)} individuals are homozygous reference at {pos}"]
    for name in names[:PREVIEW_ROWS]:
        summary.append(f"  {name}")
    if not names:
        summary.append("  (none)")
    _emit(data, "select_samples_hom_ref", summary, args.output)


def cmd_kinship(args) -> None:
    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            return client.kinship_duo(sample1=args.sample1, sample2=args.sample2)

    result = _call_with_retry(fetch)
    if not result.pairs:
        _fail(f"Error: no relatedness result returned for {args.sample1}, {args.sample2}")
    pair = result.pairs[0]
    degree = pair.degree.name
    phi = pair.phi_bwf
    incomplete = result.metadata.affected
    data = {
        "command": "kinship",
        "sample1": pair.sample1,
        "sample2": pair.sample2,
        "degree": degree,
        "phi_bwf": phi,
        "result_incomplete": incomplete,
    }
    summary = [
        f"{pair.sample1} <-> {pair.sample2}: {degree} "
        f"(KING kinship coefficient phi = {phi:.4f})"
    ]
    if incomplete:
        summary.append(INCOMPLETE_NOTE)
    _emit(data, "kinship", summary, args.output)


def cmd_dataset_info(args) -> None:
    def fetch():
        with DnaerysClient(DEFAULT_ENDPOINT) as client:
            return client.dataset_info()

    info = _call_with_retry(fetch)
    data = {
        "command": "dataset-info",
        "samples_total": info.samples_total,
        "females_total": info.females_total,
        "males_total": info.males_total,
        "variants_total": info.variants_total,
        "assembly": info.assembly.name,
        "cohorts": [
            {
                "cohort_name": c.cohort_name,
                "samples_count": c.samples_count,
                "female_count": c.female_count,
                "male_count": c.male_count,
                "synthetic": c.synthetic,
            }
            for c in info.cohorts
        ],
    }
    summary = [
        f"1000 Genomes Project - {info.samples_total:,} individuals "
        f"(F: {info.females_total:,}, M: {info.males_total:,}); "
        f"{info.variants_total:,} variants; {info.assembly.name}"
    ]
    for c in info.cohorts:
        summary.append(
            f"  {c.cohort_name}: {c.samples_count:,} "
            f"(F {c.female_count:,} / M {c.male_count:,})"
        )
    _emit(data, "dataset_info", summary, args.output)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _add_annotation_flags(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("annotation filters (different fields AND; CSV within a field OR)")
    g.add_argument("--af-lt", type=float, help="Keep variants with 1000 Genomes AF < this value.")
    g.add_argument("--af-gt", type=float, help="Keep variants with 1000 Genomes AF > this value.")
    g.add_argument("--gnomad-exomes-af-lt", type=float, help="gnomAD v4.1 exomes AF < this value.")
    g.add_argument("--gnomad-exomes-af-gt", type=float, help="gnomAD v4.1 exomes AF > this value.")
    g.add_argument("--gnomad-genomes-af-lt", type=float, help="gnomAD v4.1 genomes AF < this value.")
    g.add_argument("--gnomad-genomes-af-gt", type=float, help="gnomAD v4.1 genomes AF > this value.")
    g.add_argument("--clin-significance", metavar="CSV", help="ClinVar significance terms (CSV). See references/annotation_vocabularies.md.")
    g.add_argument("--consequence", metavar="CSV", help="Sequence Ontology consequence terms (CSV).")
    g.add_argument("--impact", metavar="CSV", help="VEP impact (CSV: HIGH,MODERATE,LOW,MODIFIER).")
    g.add_argument("--variant-type", metavar="CSV", help="SO variant class terms (CSV).")
    g.add_argument("--feature-type", metavar="CSV", help="VEP feature types (CSV).")
    g.add_argument("--bio-type", metavar="CSV", help="VEP biotypes (CSV).")
    g.add_argument("--alpha-missense-class", metavar="CSV", help="AM_LIKELY_BENIGN,AM_LIKELY_PATHOGENIC,AM_AMBIGUOUS (CSV).")
    g.add_argument("--alpha-missense-score-lt", type=float, help="AlphaMissense score < this value.")
    g.add_argument("--alpha-missense-score-gt", type=float, help="AlphaMissense score > this value.")

    bm = p.add_mutually_exclusive_group()
    bm.add_argument("--biallelic-only", action="store_true", help="Keep only biallelic sites.")
    bm.add_argument("--multiallelic-only", action="store_true", help="Keep only multiallelic sites.")

    ef = p.add_mutually_exclusive_group()
    ef.add_argument("--exclude-males", action="store_true", help="Exclude male samples.")
    ef.add_argument("--exclude-females", action="store_true", help="Exclude female samples.")

    z = p.add_mutually_exclusive_group()
    z.add_argument("--het-only", action="store_true", help="Heterozygous carriage only (default: both).")
    z.add_argument("--hom-only", action="store_true", help="Homozygous carriage only (default: both).")


def build_parser() -> argparse.ArgumentParser:
    conn_parser = argparse.ArgumentParser(add_help=False)
    conn_parser.add_argument(
        "--output",
        help="Write full JSON to this path (default: a temp file in the system temp dir).",
    )

    region_parser = argparse.ArgumentParser(add_help=False)
    region_parser.add_argument("--chrom", help="Chromosome, e.g. chr17, 17, X, MT (single-region mode).")
    region_parser.add_argument("--start", type=int, help="1-based inclusive start (with --chrom).")
    region_parser.add_argument("--end", type=int, help="1-based inclusive end (with --chrom).")
    region_parser.add_argument("--ref", help="Reference allele to narrow to one allele (single-region only).")
    region_parser.add_argument("--alt", help="Alternate allele to narrow to one allele (single-region only).")
    region_parser.add_argument(
        "--region", action="append", metavar="CHR:START-END",
        help="A region as CHR:START-END; repeat for multiple regions (multi-region mode).",
    )
    region_parser.add_argument("--min-len-bp", type=int, help="Minimum alternate-allele length (bp).")
    region_parser.add_argument("--max-len-bp", type=int, help="Maximum alternate-allele length (bp).")

    annot_parser = argparse.ArgumentParser(add_help=False)
    _add_annotation_flags(annot_parser)

    parser = argparse.ArgumentParser(
        prog="onekgpd_api.py",
        description="Individual-level queries over the 1000 Genomes Project "
        "(3,202 WGS individuals, GRCh38).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    region_parents = [conn_parser, region_parser, annot_parser]

    # dataset-info
    p = sub.add_parser("dataset-info", parents=[conn_parser], help="Dataset totals (samples, sex split, variants, assembly).")
    p.set_defaults(func=cmd_dataset_info)

    # count-variants
    p = sub.add_parser("count-variants", parents=region_parents, help="Count variants in a region, cohort-wide.")
    p.set_defaults(func=cmd_count_variants)

    # select-variants
    p = sub.add_parser("select-variants", parents=region_parents, help="Select variants in a region, cohort-wide.")
    lp = p.add_mutually_exclusive_group()
    lp.add_argument("--limit", type=int, default=DEFAULT_VARIANT_LIMIT, help=f"Hard cap on returned variants (default {DEFAULT_VARIANT_LIMIT}).")
    lp.add_argument("--page-size", type=int, help="Retrieve ALL matching variants in pages of this size (full walk).")
    p.set_defaults(func=cmd_select_variants)

    # count-variants-in-samples
    p = sub.add_parser("count-variants-in-samples", parents=region_parents, help="Count variants in a region within named individuals.")
    p.add_argument("--samples", required=True, metavar="CSV", help="Comma-separated sample names.")
    p.set_defaults(func=cmd_count_variants_in_samples)

    # select-variants-in-samples
    p = sub.add_parser("select-variants-in-samples", parents=region_parents, help="Select variants in a region within named individuals.")
    p.add_argument("--samples", required=True, metavar="CSV", help="Comma-separated sample names.")
    lp = p.add_mutually_exclusive_group()
    lp.add_argument("--limit", type=int, default=DEFAULT_VARIANT_LIMIT, help=f"Hard cap on returned variants (default {DEFAULT_VARIANT_LIMIT}).")
    lp.add_argument("--page-size", type=int, help="Retrieve ALL matching variants in pages of this size (full walk).")
    p.set_defaults(func=cmd_select_variants_in_samples)

    # count-samples
    p = sub.add_parser("count-samples", parents=region_parents, help="Count individuals carrying a matching variant in a region.")
    p.set_defaults(func=cmd_count_samples)

    # select-samples
    p = sub.add_parser("select-samples", parents=region_parents, help="List individuals carrying a matching variant in a region.")
    p.add_argument("--skip", type=int, help="Skip the first N individuals.")
    p.add_argument("--limit", type=int, help="Return at most N individuals.")
    p.set_defaults(func=cmd_select_samples)

    # count-samples-hom-ref
    p = sub.add_parser("count-samples-hom-ref", parents=[conn_parser], help="Count individuals homozygous reference at a single position.")
    p.add_argument("--chrom", required=True, help="Chromosome, e.g. chr17, 17, X, MT.")
    p.add_argument("--position", type=int, required=True, help="1-based position.")
    p.set_defaults(func=cmd_count_samples_hom_ref)

    # select-samples-hom-ref
    p = sub.add_parser("select-samples-hom-ref", parents=[conn_parser], help="List individuals homozygous reference at a single position.")
    p.add_argument("--chrom", required=True, help="Chromosome, e.g. chr17, 17, X, MT.")
    p.add_argument("--position", type=int, required=True, help="1-based position.")
    p.set_defaults(func=cmd_select_samples_hom_ref)

    # kinship
    p = sub.add_parser("kinship", parents=[conn_parser], help="Relatedness (degree + KING coefficient) between two individuals.")
    p.add_argument("--sample1", required=True, help="First sample name.")
    p.add_argument("--sample2", required=True, help="Second sample name.")
    p.set_defaults(func=cmd_kinship)

    return parser


def main(argv: list[str] | None = None) -> None:
    # Incompleteness is surfaced via result metadata and the summary, not warnings.
    warnings.simplefilter("ignore", DnaerysIncompleteResultWarning)
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (DnaerysError, ValueError) as e:
        _fail(f"Error: {e}")


if __name__ == "__main__":
    main()
```

### `scripts/onekgpd_meta.py`

```python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""OneKGPd — sample & population metadata (offline) over the 1000 Genomes Project.

Six commands answering population/pedigree questions from a data file bundled in
the skill (``onekgpd/assets/kgpe.json``): no network, no credentials, and no
third-party dependencies. The sample identifier is the same name used by the
variant/kinship commands (e.g. ``NA19240``), so the two layers compose.

Every command writes full JSON to a file (``--output``, or a temp file by
default) and prints a concise summary to stdout.

Examples
--------
    uv run scripts/onekgpd_meta.py list-superpopulations
    uv run scripts/onekgpd_meta.py sample-metadata --samples NA19240,HG00096
    uv run scripts/onekgpd_meta.py population-stats --populations YRI --populations CHS
    uv run scripts/onekgpd_meta.py select-samples-by-population --population YRI --limit 20

MIT License. Author: Dnaerys.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, NoReturn

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ASSETS = Path(__file__).resolve().parent.parent / "assets"
# Prefer the plain-text asset (inspectable, scanner-clean); fall back to a
# gzipped copy if that is the only form present. Both hold identical JSON.
DATA_PATH = _ASSETS / "kgpe.json"
if not DATA_PATH.exists():
    DATA_PATH = _ASSETS / "kgpe.json.gz"
DEFAULT_LIMIT = 50      # MetaClient.java:48
MAX_LIMIT = 3202        # MetaClient.java:49
PREVIEW_ROWS = 10       # rows shown in a stdout summary preview

_ABSENT = (None, "", "0")   # pid/mid "absent" sentinel values


# ---------------------------------------------------------------------------
# Small generic helpers (mirrors onekgpd_api.py; kept local to stay dnaerys-free)
# ---------------------------------------------------------------------------


def _fail(msg: str) -> NoReturn:
    """Print a clean one-line message to stderr and exit non-zero."""
    print(msg, file=sys.stderr)
    sys.exit(1)


def _split_csv(s: str) -> list[str]:
    """Split a comma-separated value into a list of non-empty trimmed tokens."""
    return [part.strip() for part in s.split(",") if part.strip()]


def _save_json(data: Any, prefix: str, output_path: str | None = None) -> str:
    """Write *data* as indented JSON to *output_path* or a temp file; return path."""
    if output_path:
        path = output_path
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
    else:
        fd, path = tempfile.mkstemp(prefix=f"onekgpd_{prefix}_", suffix=".json", text=True)
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
    return path


def _emit(data: Any, prefix: str, summary_lines: list[str], output: str | None) -> None:
    """Save full JSON to a file and print the summary + saved-path line to stdout."""
    path = _save_json(data, prefix, output)
    for line in summary_lines:
        print(line)
    print(f"[*] Full JSON saved to {path}")


# ---------------------------------------------------------------------------
# Data loading / indexing
# ---------------------------------------------------------------------------

_RECORDS: list[dict] | None = None


def _load_records() -> list[dict]:
    """Load and cache the bundled pedigree records (once per process)."""
    global _RECORDS
    if _RECORDS is None:
        opener = gzip.open if DATA_PATH.suffix == ".gz" else open
        with opener(DATA_PATH, "rt", encoding="utf-8") as fh:
            _RECORDS = json.load(fh)
    return _RECORDS


def _present(x: str | None) -> bool:
    """True if a pid/mid value names a real parent (not absent/'0'/empty)."""
    return x not in _ABSENT


def _none_if_empty(x: str | None) -> str | None:
    """Java nullIfEmpty: None for empty/None (MetaClient.java:537-539)."""
    return None if x in (None, "") else x


def _none_if_absent(x: str | None) -> str | None:
    """Java nullIfAbsent: None for None/empty/'0' (MetaClient.java:533-535)."""
    return None if x in _ABSENT else x


def _children_index(records: list[dict]) -> dict[str, list[str]]:
    """Map parent externalID -> child externalIDs.

    Replicates the LEFT JOIN ``(c.pid = s OR c.mid = s) AND c.pid != '0' AND
    c.mid != '0'`` (MetaClient.java:155-156): a child counts only when BOTH of
    its parents are recorded.
    """
    idx: dict[str, list[str]] = {}
    for c in records:
        if _present(c["pid"]) and _present(c["mid"]):
            cid = c["externalIDs"]
            idx.setdefault(c["pid"], []).append(cid)
            idx.setdefault(c["mid"], []).append(cid)
    return idx


def _valid_pop_lower(records: list[dict]) -> set[str]:
    """Lowercased set of all valid population codes and full names."""
    s: set[str] = set()
    for r in records:
        s.add(r["pop"].lower())
        s.add(r["Population"].lower())
    return s


def _valid_reg_lower(records: list[dict]) -> set[str]:
    """Lowercased set of all valid superpopulation codes and full names."""
    s: set[str] = set()
    for r in records:
        s.add(r["reg"].lower())
        s.add(r["region"].lower())
    return s


# ---------------------------------------------------------------------------
# Stats aggregation (shared by population-stats and superpopulation-summary)
# ---------------------------------------------------------------------------


def _population_stats(records_subset: list[dict]) -> dict[tuple, dict]:
    """Group a subset by (pop, Population, reg, region) -> count aggregates.

    Mirrors the COUNT(CASE WHEN …) columns in MetaClient.java:292-298.
    """
    groups: dict[tuple, dict] = {}
    for r in records_subset:
        key = (r["pop"], r["Population"], r["reg"], r["region"])
        g = groups.setdefault(key, {"n": 0, "m": 0, "f": 0, "p3": 0, "trio": 0})
        g["n"] += 1
        if r["gender"] == "male":
            g["m"] += 1
        elif r["gender"] == "female":
            g["f"] += 1
        if r["phase3"] == "TRUE":
            g["p3"] += 1
        if _present(r["pid"]) and _present(r["mid"]):
            g["trio"] += 1
    return groups


def _stats_obj(key: tuple, g: dict) -> dict:
    return {
        "population_code": key[0],
        "population": key[1],
        "superpopulation_code": key[2],
        "superpopulation": key[3],
        "sample_count": g["n"],
        "male_count": g["m"],
        "female_count": g["f"],
        "phase3_count": g["p3"],
        "trio_count": g["trio"],
    }


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def cmd_sample_metadata(args) -> None:
    ids = _split_csv(args.samples)
    if not ids:
        _fail("Error: Parameter 'sampleIds' must not be null or empty")
    records = _load_records()
    by_id = {r["externalIDs"]: r for r in records}
    unknown = [i for i in ids if i not in by_id]   # case-sensitive sample IDs
    if unknown:
        _fail(f"Error: Unknown sample IDs: [{', '.join(unknown)}]")

    children = _children_index(records)
    samples = []
    for sid in sorted(set(ids)):   # ORDER BY externalIDs, distinct
        r = by_id[sid]
        kids = sorted(set(children.get(sid, [])))
        samples.append({
            "sample_id": r["externalIDs"],
            "family_id": _none_if_empty(r["familyId"]),
            "gender": r["gender"],
            "paternal_id": _none_if_absent(r["pid"]),
            "maternal_id": _none_if_absent(r["mid"]),
            "relationship": _none_if_empty(r["Relationship"]),
            "children": kids,
            "population_code": r["pop"],
            "population": r["Population"],
            "superpopulation_code": r["reg"],
            "superpopulation": r["region"],
            "phase3": r["phase3"],
        })

    data = {"command": "sample-metadata", "samples": samples}
    summary = [f"Metadata for {len(samples)} sample(s)"]
    for s in samples[:PREVIEW_ROWS]:
        kids = ", ".join(s["children"]) if s["children"] else "-"
        summary.append(
            f"  {s['sample_id']}  {s['population_code']}/{s['superpopulation_code']}  "
            f"{s['gender']}  {s['relationship'] or '-'}  "
            f"family {s['family_id'] or '-'}  children: {kids}"
        )
    _emit(data, "sample_metadata", summary, args.output)


def cmd_list_populations(args) -> None:
    records = _load_records()
    counts: dict[tuple, int] = {}
    for r in records:
        key = (r["pop"], r["Population"], r["reg"], r["region"])
        counts[key] = counts.get(key, 0) + 1
    # ORDER BY reg, pop (MetaClient.java:220)
    rows = sorted(counts.items(), key=lambda kv: (kv[0][2], kv[0][0]))
    populations = [{
        "population_code": k[0],
        "population": k[1],
        "superpopulation_code": k[2],
        "superpopulation": k[3],
        "sample_count": cnt,
    } for k, cnt in rows]

    data = {"command": "list-populations", "populations": populations}
    n_super = len({k[2] for k in counts})
    summary = [f"{len(populations)} populations across {n_super} superpopulations"]
    for p in populations[:PREVIEW_ROWS]:
        summary.append(
            f"  {p['population_code']}  {p['population']}  "
            f"{p['superpopulation_code']}  {p['sample_count']}"
        )
    if len(populations) > PREVIEW_ROWS:
        summary.append(f"  … {len(populations) - PREVIEW_ROWS} more (see file)")
    _emit(data, "list_populations", summary, args.output)


def cmd_list_superpopulations(args) -> None:
    records = _load_records()
    groups: dict[str, dict] = {}
    for r in records:
        reg = r["reg"]
        g = groups.setdefault(reg, {"region": r["region"], "count": 0, "pops": set()})
        g["count"] += 1
        g["pops"].add(r["pop"])
    # ORDER BY reg (MetaClient.java:250)
    rows = sorted(groups.items(), key=lambda kv: kv[0])
    superpopulations = [{
        "superpopulation_code": reg,
        "superpopulation": g["region"],
        "sample_count": g["count"],
        "populations": sorted(g["pops"]),
    } for reg, g in rows]

    data = {"command": "list-superpopulations", "superpopulations": superpopulations}
    summary = [f"{len(superpopulations)} superpopulations"]
    for sp in superpopulations:
        summary.append(
            f"  {sp['superpopulation_code']}  {sp['superpopulation']}  "
            f"n={sp['sample_count']}  pops={len(sp['populations'])}"
        )
    _emit(data, "list_superpopulations", summary, args.output)


def cmd_population_stats(args) -> None:
    vals = [v.strip() for v in args.populations if v.strip()]
    if not vals:
        _fail("Error: Parameter 'populations' must not be null or empty")
    records = _load_records()
    valid = _valid_pop_lower(records)
    unknown = [v for v in vals if v.lower() not in valid]
    if unknown:
        _fail(f"Error: Unrecognised population values: [{', '.join(unknown)}]")

    wanted = {v.lower() for v in vals}
    subset = [r for r in records
              if r["pop"].lower() in wanted or r["Population"].lower() in wanted]
    groups = _population_stats(subset)
    # ORDER BY pop (MetaClient.java:302)
    rows = sorted(groups.items(), key=lambda kv: kv[0][0])
    populations = [_stats_obj(k, g) for k, g in rows]

    data = {"command": "population-stats", "populations": populations}
    summary = [f"Stats for {len(populations)} population(s)"]
    for p in populations:
        summary.append(
            f"  {p['population_code']}  {p['population']}  n={p['sample_count']}  "
            f"M={p['male_count']} F={p['female_count']}  "
            f"phase3={p['phase3_count']}  trios={p['trio_count']}"
        )
    _emit(data, "population_stats", summary, args.output)


def cmd_superpopulation_summary(args) -> None:
    vals = [v.strip() for v in args.superpopulations if v.strip()]
    if not vals:
        _fail("Error: Parameter 'superpopulations' must not be null or empty")
    records = _load_records()
    valid = _valid_reg_lower(records)
    unknown = [v for v in vals if v.lower() not in valid]
    if unknown:
        _fail(f"Error: Unrecognised superpopulation values: [{', '.join(unknown)}]")

    wanted = {v.lower() for v in vals}
    subset = [r for r in records
              if r["reg"].lower() in wanted or r["region"].lower() in wanted]
    groups = _population_stats(subset)
    # Per-population rows ordered by (reg, pop); group by reg preserving order.
    pop_rows = sorted(groups.items(), key=lambda kv: (kv[0][2], kv[0][0]))
    by_super: dict[str, dict] = {}
    for key, g in pop_rows:
        reg, region = key[2], key[3]
        sg = by_super.setdefault(reg, {"region": region, "pops": []})
        sg["pops"].append(_stats_obj(key, g))

    superpopulations = []
    for reg, sg in by_super.items():
        pops = sg["pops"]
        superpopulations.append({
            "superpopulation_code": reg,
            "superpopulation": sg["region"],
            "sample_count": sum(p["sample_count"] for p in pops),
            "male_count": sum(p["male_count"] for p in pops),
            "female_count": sum(p["female_count"] for p in pops),
            "phase3_count": sum(p["phase3_count"] for p in pops),
            "trio_count": sum(p["trio_count"] for p in pops),
            "populations": pops,
        })

    data = {"command": "superpopulation-summary", "superpopulations": superpopulations}
    summary = [f"Summary for {len(superpopulations)} superpopulation(s)"]
    for sp in superpopulations:
        summary.append(
            f"  {sp['superpopulation_code']}  {sp['superpopulation']}  "
            f"n={sp['sample_count']}  M={sp['male_count']} F={sp['female_count']}  "
            f"phase3={sp['phase3_count']}  trios={sp['trio_count']}  "
            f"({len(sp['populations'])} populations)"
        )
    _emit(data, "superpopulation_summary", summary, args.output)


def cmd_select_samples_by_population(args) -> None:
    pop = args.population.strip() if args.population and args.population.strip() else None
    sup = args.superpopulation.strip() if args.superpopulation and args.superpopulation.strip() else None
    if pop is None and sup is None:
        _fail("Error: At least one parameter ('population' or 'superpopulation') must be provided")

    skip = args.skip if args.skip is not None else 0
    limit = args.limit if args.limit is not None else DEFAULT_LIMIT
    if skip < 0:
        _fail(f"Error: Invalid parameter: 'skip' must be >= 0, actual: {skip}")
    if limit < 1 or limit > MAX_LIMIT:
        _fail(f"Error: Invalid parameter: 'limit' must be between 1 and {MAX_LIMIT}, actual: {limit}")

    records = _load_records()
    if pop is not None and pop.lower() not in _valid_pop_lower(records):
        _fail(f"Error: Unrecognised population: '{pop}'")
    if sup is not None and sup.lower() not in _valid_reg_lower(records):
        _fail(f"Error: Unrecognised superpopulation: '{sup}'")

    pop_l = pop.lower() if pop is not None else None
    sup_l = sup.lower() if sup is not None else None

    def match(r: dict) -> bool:
        if pop_l is not None and pop_l not in (r["pop"].lower(), r["Population"].lower()):
            return False
        if sup_l is not None and sup_l not in (r["reg"].lower(), r["region"].lower()):
            return False
        return True

    matched = sorted(r["externalIDs"] for r in records if match(r))  # ORDER BY externalIDs
    page = matched[skip:skip + limit]

    data = {
        "command": "select-samples-by-population",
        "count": len(page),
        "samples": page,
        "request": {"population": pop, "superpopulation": sup, "skip": skip, "limit": limit},
    }
    parts = []
    if pop is not None:
        parts.append(f"population {pop}")
    if sup is not None:
        parts.append(f"superpopulation {sup}")
    label = " & ".join(parts)
    summary = [f"{len(page)} samples in {label} (rows {skip}..{skip + len(page)} of {len(matched)} total)"]
    for s in page[:PREVIEW_ROWS]:
        summary.append(f"  {s}")
    _emit(data, "select_samples_by_population", summary, args.output)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    conn = argparse.ArgumentParser(add_help=False)
    conn.add_argument(
        "--output",
        help="Write full JSON to this path (default: a temp file in the system temp dir).",
    )

    parser = argparse.ArgumentParser(
        prog="onekgpd_meta.py",
        description="Sample & population metadata for the 1000 Genomes Project "
        "(offline; reads a bundled data file, no network).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("sample-metadata", parents=[conn], help="Pedigree/population metadata for given sample IDs.")
    p.add_argument("--samples", required=True, metavar="CSV", help="Comma-separated sample IDs (case-sensitive).")
    p.set_defaults(func=cmd_sample_metadata)

    p = sub.add_parser("list-populations", parents=[conn], help="List all populations with superpopulation and sample count.")
    p.set_defaults(func=cmd_list_populations)

    p = sub.add_parser("list-superpopulations", parents=[conn], help="List all superpopulations with sample count and constituent populations.")
    p.set_defaults(func=cmd_list_superpopulations)

    p = sub.add_parser("population-stats", parents=[conn], help="Per-population stats: sex split, phase3, trio membership.")
    p.add_argument("--populations", required=True, action="append", metavar="VALUE",
                   help="Population code or full name; repeat for multiple (case-insensitive). "
                        "Repeated rather than comma-separated because full names contain commas.")
    p.set_defaults(func=cmd_population_stats)

    p = sub.add_parser("superpopulation-summary", parents=[conn], help="Per-superpopulation summary with per-population breakdown.")
    p.add_argument("--superpopulations", required=True, action="append", metavar="VALUE",
                   help="Superpopulation code or full name; repeat for multiple (case-insensitive).")
    p.set_defaults(func=cmd_superpopulation_summary)

    p = sub.add_parser("select-samples-by-population", parents=[conn], help="Select sample IDs by population and/or superpopulation.")
    p.add_argument("--population", metavar="P", help="Population code or full name (case-insensitive).")
    p.add_argument("--superpopulation", metavar="R", help="Superpopulation code or full name (case-insensitive).")
    p.add_argument("--skip", type=int, help="Number of results to skip (default 0).")
    p.add_argument("--limit", type=int, help=f"Max results to return (default {DEFAULT_LIMIT}, max {MAX_LIMIT}).")
    p.set_defaults(func=cmd_select_samples_by_population)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (ValueError, OSError) as e:
        _fail(f"Error: {e}")


if __name__ == "__main__":
    main()
```
