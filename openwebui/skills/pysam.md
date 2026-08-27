---
name: pysam
description: Python/HTSlib workflows for genomic files. Use when reading, querying, filtering, or writing SAM/BAM/CRAM, VCF/BCF, FASTA/FASTQ, or tabix data with pysam, including pileup, coverage, indexing, and CRAM references.
---

# pysam

## Overview

Use pysam for low-level, streaming access to HTSlib-supported genomic formats:

- `AlignmentFile` and `AlignedSegment` for SAM/BAM/CRAM
- `VariantFile`, `VariantHeader`, and `VariantRecord` for VCF/BCF
- `FastaFile` for indexed FASTA and `FastxFile` for sequential FASTA/FASTQ
- `TabixFile` for BGZF-compressed, tabix-indexed BED/GFF/GTF/custom tables
- `pysam.samtools` and `pysam.bcftools` for wrapped command dispatchers

Current upstream baseline: **pysam 0.24.0** (27 April 2026), wrapping
HTSlib/samtools/bcftools 1.23.1. Read `references/sources.md` before updating
version-specific guidance.

## Installation

Use the pinned release for reproducible work:

```bash
uv pip install "pysam==0.24.0"
```

Confirm the runtime:

```python
import pysam

print(pysam.__version__)           # 0.24.0
print(pysam.__samtools_version__)  # 1.23.1
```

Prebuilt wheels are available for supported macOS and Linux platforms. A
source build needs a C compiler and HTSlib build dependencies; read the
official installation guide linked from `references/sources.md`.

## First Decide

Before writing code:

1. Identify the real format, compression, sort order, and available index.
2. Decide whether coordinates are numeric Python coordinates or a region
   string. Do not mix them.
3. For CRAM, identify the exact reference assembly and FASTA.
4. Prefer indexed region access; use sequential iteration only when intended.
5. Preserve headers when writing and write to a new path by default.
6. State filtering semantics: mapping/base quality, flags, overlap handling,
   duplicate handling, and pileup depth cap.

For unfamiliar files, start with the bundled read-only inspector:

```bash
python scripts/inspect_hts.py sample.bam
python scripts/inspect_hts.py cohort.vcf.gz
python scripts/inspect_hts.py reference.fa
```

## Bundled Scripts

| Script | Purpose | Typical call |
|---|---|---|
| `scripts/inspect_hts.py` | Metadata-only inspection for alignment, variant, FASTA, FASTQ, and tabix files | `python scripts/inspect_hts.py sample.cram --reference ref.fa` |
| `scripts/alignment_qc.py` | Streaming aggregate read/QC counts as JSON | `python scripts/alignment_qc.py sample.bam --max-records 100000` |
| `scripts/variant_summary.py` | Streaming variant, FILTER, and genotype summary as JSON | `python scripts/variant_summary.py cohort.vcf.gz --region chr1:1-1000000` |
| `scripts/filter_alignments.py` | Filter SAM/BAM/CRAM without changing record order | `python scripts/filter_alignments.py input.bam output.bam --exclude-secondary` |

All scripts refuse to overwrite existing outputs. Run each with `--help` for
coordinate, index, and privacy notes.

## Coordinate Contract

**Numeric coordinates accepted by pysam APIs are 0-based, half-open.** This
includes numeric `AlignmentFile.fetch()`, `VariantFile.fetch()`,
`FastaFile.fetch()`, `TabixFile.fetch()`, and `pileup()` arguments.

**Region strings are samtools-style: 1-based and inclusive.**

```python
# The same 100 bases:
bam.fetch("chr1", 99, 199)          # [99, 199)
bam.fetch(region="chr1:100-199")    # 1-based inclusive
```

VCF text uses 1-based `POS`, while record properties expose both systems:

```python
record.pos    # 1-based
record.start  # 0-based inclusive
record.stop   # 0-based exclusive
```

Read `references/coordinates_and_indexing.md` for format conversions, overlap
semantics, index choices, and contig-name checks.

## Alignment Files

Use context managers and explicit modes:

```python
import pysam

with pysam.AlignmentFile("sample.bam", "rb", threads=4) as bam:
    for read in bam.fetch("chr1", 1_000, 2_000):
        if (
            not read.is_unmapped
            and not read.is_secondary
            and not read.is_supplementary
            and read.mapping_quality >= 30
        ):
            print(read.query_name, read.reference_start, read.cigarstring)
```

Use `fetch(until_eof=True)` to stream every record in file order, including
unplaced unmapped reads, without requiring an index:

```python
with pysam.AlignmentFile("sample.bam", "rb") as bam:
    for read in bam.fetch(until_eof=True):
        ...
```

Important distinctions:

- `fetch()` returns alignment records overlapping a region.
- `count()` counts records and defaults to `read_callback="nofilter"`.
- `count_coverage()` returns A/C/G/T base counts and defaults to base quality
  15 plus `read_callback="all"`.
- `pileup()` exposes per-column reads and has its own filtering, base-quality,
  overlap, orphan, and `max_depth=8000` defaults.

For exact-region pileups, set `truncate=True` and explicit filters:

```python
with pysam.FastaFile("reference.fa") as fasta, pysam.AlignmentFile(
    "sample.bam", "rb"
) as bam:
    for column in bam.pileup(
        "chr1",
        1_000,
        2_000,
        truncate=True,
        stepper="samtools",
        fastafile=fasta,
        min_mapping_quality=20,
        min_base_quality=20,
        max_depth=100_000,
    ):
        print(column.reference_pos, column.get_num_aligned())
```

Read `references/alignment_files.md` for flags, CIGAR operations, tags,
modified bases, writing records, pileup details, and iterator lifetime.

## Variant Files

Input format is auto-detected. Numeric fetch coordinates remain 0-based:

```python
import pysam

with pysam.VariantFile("cohort.vcf.gz", threads=4) as variants:
    for record in variants.fetch("chr1", 999_999, 2_000_000):
        print(record.contig, record.pos, record.ref, record.alts)
        for sample_name, call in record.samples.items():
            print(sample_name, call.get("GT"))
```

Subset samples **before retrieving records**:

```python
with pysam.VariantFile("cohort.bcf") as variants:
    variants.subset_samples(["sample_A", "sample_B"])
    for record in variants:
        ...
```

When changing a header, copy each record and translate it to the destination
header before assigning newly declared INFO/FORMAT/FILTER fields. Do not
manually clear and rebuild `header.samples`.

Read `references/variant_files.md` for safe headers, writing, sample
subsetting, missing genotypes, symbolic alleles, filtering, translation, and
indexing.

## FASTA, FASTQ, and Tabix

Indexed FASTA uses numeric 0-based coordinates:

```python
with pysam.FastaFile("reference.fa") as fasta:
    sequence = fasta.fetch("chr1", 999, 1_099)
```

`FastxFile` is sequential. `persist=False` is faster but yielded records become
invalid after iteration advances:

```python
with pysam.FastxFile("reads.fastq.gz", persist=False) as reads:
    for read in reads:
        qualities = read.get_quality_array()
        ...
```

Tabix input must be coordinate-sorted and BGZF-compressed, not ordinary gzip.
Use a non-destructive two-step workflow:

```python
pysam.tabix_compress("regions.bed", "regions.bed.gz")
pysam.tabix_index("regions.bed.gz", preset="bed")

with pysam.TabixFile("regions.bed.gz", parser=pysam.asBed()) as tbx:
    for interval in tbx.fetch("chr1", 1_000, 2_000):
        print(interval.contig, interval.start, interval.end)
```

Read `references/sequence_files.md` for FASTA/FASTQ records and safe tabix
creation.

## CRAM, Remote I/O, and Threads

pysam 0.24 changed inherited HTSlib behavior:

- Newly written CRAM defaults to CRAM 3.1, not 3.0.
- HTSlib no longer contacts the EBI reference server by default.
- Prefer `reference_filename="reference.fa"` for deterministic local reads and
  writes.

```python
with pysam.AlignmentFile(
    "sample.cram",
    "rc",
    reference_filename="reference.fa",
    threads=4,
) as cram:
    for read in cram.fetch("chr1", 1_000, 2_000):
        ...
```

Only configure `REF_PATH`/`REF_CACHE` when reference-by-MD5 lookup is
intentional. Do not assume a CRAM is self-contained. `threads=` accelerates
compression/decompression; it does not parallelize Python analysis.

Read `references/cram_and_performance.md` before CRAM conversion, remote access,
or concurrent iteration.

## Wrapped samtools and bcftools

Import command modules explicitly. Pass each command-line token as a separate
string:

```python
import pysam.samtools
import pysam.bcftools

pysam.samtools.sort(
    "-@", "4", "-o", "sorted.bam", "input.bam", catch_stdout=False
)
pysam.samtools.index("-@", "4", "sorted.bam", catch_stdout=False)

pysam.bcftools.index("--csi", "variants.vcf.gz", catch_stdout=False)
```

Dispatchers capture stdout by default. For large or binary output, use the
tool's `-o` option with `catch_stdout=False`, or `save_stdout=...`, rather than
returning the complete output in memory.

```python
try:
    pysam.samtools.quickcheck("-v", "sample.bam")
except pysam.SamtoolsError as error:
    messages = pysam.samtools.quickcheck.get_messages()
    raise RuntimeError(messages or str(error)) from error
```

Use the Python API for record-level logic and dispatchers for mature bulk
operations such as sort, index, merge, view, and normalization. Never compose
dispatcher arguments by splitting an untrusted shell command.

## Writing Rules

- Copy or construct a valid header before opening output.
- Write to a new path; do not use `force=True` unless replacement is explicit.
- Preserve sort order if the output will be indexed.
- Set `query_sequence` before `query_qualities`.
- Prefer `pysam.CIGAR_OPS` enum members; top-level constants such as
  `pysam.CMATCH` are compatibility aliases slated for future removal.
- Validate outputs with `pysam.samtools.quickcheck()` for alignments and reopen
  variant/sequence outputs before downstream use.
- Use CSI rather than BAI/TBI when references or coordinates exceed legacy
  index limits.

## Reference Map

| Need | Read |
|---|---|
| Alignment API, flags, CIGAR, pileup, modified bases | `references/alignment_files.md` |
| VCF/BCF headers, records, samples, writing | `references/variant_files.md` |
| FASTA/FASTQ and tabix-indexed tables | `references/sequence_files.md` |
| Coordinate conversion and index selection | `references/coordinates_and_indexing.md` |
| CRAM references, remote I/O, threads, performance | `references/cram_and_performance.md` |
| Correct integrated analysis patterns | `references/common_workflows.md` |
| Compact current API signatures and defaults | `references/api_reference.md` |
| Upgrade notes for existing environments | `references/migration_to_0_24.md` |
| Official docs, specifications, and release sources | `references/sources.md` |

## Common Failure Modes

- Treating numeric `VariantFile.fetch()` coordinates as 1-based
- Using ordinary gzip where BGZF plus tabix/CSI is required
- Calling region fetch without an index
- Assuming `fetch()` includes unplaced unmapped alignments
- Forgetting `truncate=True` for an exact pileup interval
- Ignoring pileup defaults such as base quality 13 and depth cap 8000
- Sharing one file handle across active iterators or threads
- Decoding CRAM without its exact reference
- Assigning a new VCF field before declaring it in the output header
- Capturing large samtools/bcftools output in memory
- Using a SNP base-counting method for indels or symbolic alleles

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pysam/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/alignment_files.md`

# Alignment Files: SAM, BAM, and CRAM

This reference targets pysam 0.24.0. All numeric coordinates shown here are
0-based, half-open.

## Open Modes and Handles

| Format | Read | Write |
|---|---:|---:|
| SAM text | `r` | `w` |
| BAM | `rb` | `wb` |
| CRAM | `rc` | `wc` |

```python
import pysam

with pysam.AlignmentFile("input.bam", "rb", threads=4) as alignments:
    print(alignments.references)
```

For CRAM, supply the exact reference where possible:

```python
with pysam.AlignmentFile(
    "input.cram",
    "rc",
    reference_filename="GRCh38.fa",
    threads=4,
) as alignments:
    ...
```

`AlignmentFile` can use a path or a real file object that exposes `fileno()`.
In-memory objects such as `io.BytesIO` are not supported by HTSlib. Use `"-"`
for stdin/stdout. When an existing file object is accepted,
`duplicate_filehandle=True` (the default) prevents pysam from closing the
caller's descriptor.

Useful constructor options:

- `index_filename=`: nonstandard, remote, or separately named index
- `require_index=True`: fail early if random access is required
- `reference_filename=`: CRAM reference FASTA
- `threads=`: compression/decompression threads
- `format_options=["key=value"]`: HTSlib format options
- `ignore_truncation=True`: downgrade a missing BGZF EOF marker to a warning;
  do not combine with `threads > 1`

## Headers and Index State

`AlignmentFile.header` is an `AlignmentHeader`, not a plain dictionary.

```python
with pysam.AlignmentFile("input.bam", "rb") as bam:
    header_dict = bam.header.to_dict()
    header_text = str(bam.header)
    contigs = dict(zip(bam.references, bam.lengths))
    has_index = bam.has_index()
```

Use `check_index()` when a missing index should be an error. It raises for SAM,
closed files, or unusable indexes. `get_index_statistics()` exposes per-contig
mapped/unmapped counts recorded in an available index; these are index
statistics, not a fresh scan of every record.

## Iteration Choices

### Indexed region query

```python
with pysam.AlignmentFile("input.bam", "rb") as bam:
    for read in bam.fetch("chr1", 1_000, 2_000):
        ...
```

- Requires BAI/CSI for BAM or CRAI for CRAM.
- Returns reads overlapping the interval, including reads that start before it
  or end after it.
- Records are returned in coordinate/index order.
- `fetch()` with no region still requires an index and returns mapped records.

### Sequential scan

```python
with pysam.AlignmentFile("input.bam", "rb") as bam:
    for read in bam.fetch(until_eof=True):
        ...
```

- Does not require an index.
- Starts at the current file position.
- Preserves file order.
- Includes unplaced unmapped records.

`fetch("*")` requests only unplaced unmapped records at the end of a
coordinate-sorted alignment file.

### Multiple active iterators

`multiple_iterators` belongs to `fetch()`, not the `AlignmentFile`
constructor:

```python
with pysam.AlignmentFile("input.bam", "rb") as bam:
    chr1_reads = bam.fetch("chr1", multiple_iterators=True)
    chr2_reads = bam.fetch("chr2", multiple_iterators=True)
```

Each such iterator reopens the file and has overhead. Prefer one ordered pass
when possible.

## `AlignedSegment` Essentials

### Identity and sequence

- `query_name`
- `query_sequence`
- `query_qualities`: numeric Phred scores, or `None`
- `query_length`
- `query_alignment_sequence`: query bases participating in the alignment
- `query_alignment_qualities`
- `get_forward_sequence()` / `get_forward_qualities()`: original sequencer
  orientation

Assigning `query_sequence` invalidates `query_qualities`. Save and reassign
qualities after changing sequence.

### Reference placement

- `reference_name`
- `reference_id`
- `reference_start`: 0-based inclusive
- `reference_end`: 0-based exclusive; derived from CIGAR
- `mapping_quality`
- `next_reference_name`, `next_reference_start`
- `template_length`

Many placement-derived properties are `None` or sentinel values for unmapped
or CIGAR-less records. Check `is_unmapped` before using them.

### Flags

Common boolean properties:

- pairing: `is_paired`, `is_proper_pair`, `is_read1`, `is_read2`
- orientation: `is_reverse`, `mate_is_reverse`
- mapping: `is_unmapped`, `mate_is_unmapped`
- status: `is_secondary`, `is_supplementary`, `is_qcfail`, `is_duplicate`

For a typical primary mapped-read filter:

```python
def keep_primary(read: pysam.AlignedSegment) -> bool:
    return (
        not read.is_unmapped
        and not read.is_secondary
        and not read.is_supplementary
        and not read.is_qcfail
        and not read.is_duplicate
        and read.mapping_quality >= 20
    )
```

State whether supplementary alignments and duplicates are intentionally
excluded; there is no universal filter for every analysis.

## CIGAR Operations and Alignment Geometry

`cigartuples` stores `(operation, length)`, the reverse of textual SAM CIGAR
notation.

| Enum | Code | SAM op | Consumes query | Consumes reference |
|---|---:|---:|---:|---:|
| `CIGAR_OPS.CMATCH` | 0 | `M` | yes | yes |
| `CIGAR_OPS.CINS` | 1 | `I` | yes | no |
| `CIGAR_OPS.CDEL` | 2 | `D` | no | yes |
| `CIGAR_OPS.CREF_SKIP` | 3 | `N` | no | yes |
| `CIGAR_OPS.CSOFT_CLIP` | 4 | `S` | yes | no |
| `CIGAR_OPS.CHARD_CLIP` | 5 | `H` | no | no |
| `CIGAR_OPS.CPAD` | 6 | `P` | no | no |
| `CIGAR_OPS.CEQUAL` | 7 | `=` | yes | yes |
| `CIGAR_OPS.CDIFF` | 8 | `X` | yes | yes |
| `CIGAR_OPS.CBACK` | 9 | `B` | legacy | legacy |

Prefer enum members in new code. Top-level aliases such as `pysam.CMATCH`
remain in 0.24 for compatibility but are expected to be removed in a future
release.

Useful geometry methods:

```python
blocks = read.get_blocks()  # aligned reference blocks; gaps at D/N
pairs = read.get_aligned_pairs(matches_only=False, with_cigar=True)
reference_positions = read.get_reference_positions(full_length=True)
```

`get_aligned_pairs(with_seq=True)` needs an MD tag and returns reference bases
derived from that tag. It does not consult a separately opened FASTA.

## Optional Tags and Modified Bases

```python
if read.has_tag("NM"):
    edit_distance = read.get_tag("NM")

read.set_tag("XX", 7, value_type="i")
all_tags = read.get_tags(with_value_type=True)
```

Use standard tags according to the SAM tags specification. Avoid changing
alignment-derived tags such as NM/MD without recomputing them.

For base modifications encoded by MM/ML:

```python
for (canonical_base, strand, modification), calls in (
    read.modified_bases or {}
).items():
    for query_position, quality in calls:
        probability = None if quality < 0 else quality / 256.0
```

The key is `(canonical base, strand, modification)`, where strand is `0`
forward or `1` reverse. pysam 0.24 removed the earlier five-modification-type
limit and fixed crashes on degenerate empty MM calls.

## Counting and Coverage

### Record count

```python
with pysam.AlignmentFile("input.bam", "rb") as bam:
    raw_overlap_count = bam.count("chr1", 1_000, 2_000)
    filtered_count = bam.count(
        "chr1",
        1_000,
        2_000,
        read_callback="all",
    )
```

`count()` defaults to `read_callback="nofilter"`. `"all"` excludes reads with
unmapped, secondary, QC-fail, or duplicate flags. It does not accept a
`quality=` argument. Use a callback for custom record filtering:

```python
count = bam.count(
    "chr1",
    1_000,
    2_000,
    read_callback=lambda read: keep_primary(read),
)
```

### A/C/G/T base coverage

```python
a, c, g, t = bam.count_coverage(
    "chr1",
    1_000,
    2_000,
    quality_threshold=20,
    read_callback="all",
)
depth = [sum(values) for values in zip(a, c, g, t)]
```

The result has exactly `stop - start` positions and therefore represents zero
coverage. Only A/C/G/T bases are counted; ambiguous query bases do not
contribute.

## Pileup Semantics

```python
with pysam.FastaFile("reference.fa") as fasta, pysam.AlignmentFile(
    "input.bam", "rb"
) as bam:
    iterator = bam.pileup(
        "chr1",
        1_000,
        2_000,
        truncate=True,
        stepper="samtools",
        fastafile=fasta,
        min_mapping_quality=20,
        min_base_quality=20,
        max_depth=100_000,
        ignore_overlaps=True,
        ignore_orphans=True,
    )
    for column in iterator:
        for pileup_read in column.pileups:
            if pileup_read.is_del or pileup_read.is_refskip:
                continue
            query_position = pileup_read.query_position
            base = pileup_read.alignment.query_sequence[query_position]
```

Key defaults and behaviors:

- Without `truncate=True`, columns outside the requested interval can appear
  when overlapping reads extend beyond the interval.
- `stepper="all"` filters unmapped, secondary, QC-fail, and duplicate reads.
- `stepper="nofilter"` disables read filtering.
- `stepper="samtools"` applies samtools-style processing; provide `fastafile`
  for full BAQ/reference behavior.
- Default `min_base_quality` is 13.
- Default `max_depth` is 8000.
- Paired overlap detection and orphan filtering are enabled by default.
- `nsegments` counts reads in the pileup column before base-level exclusions;
  `get_num_aligned()` is often the clearer aligned-base depth.

`PileupColumn` and `PileupRead` proxy objects are valid only while their
iterator remains alive. Do not retain a column after iteration ends.

For SNP support, inspect base and quality. For insertions/deletions, use
`PileupRead.indel`, deletion/refskip state, CIGAR, and normalized alleles.
Single-base counting is not an indel caller.

## Writing Alignments

### Preserve an input header

```python
with pysam.AlignmentFile("input.bam", "rb") as source, pysam.AlignmentFile(
    "filtered.bam", "wb", template=source, threads=4
) as destination:
    for read in source.fetch(until_eof=True):
        if keep_primary(read):
            destination.write(read)
```

The output retains input order. Only index it if that order is coordinate
sorted and unmapped records remain in a valid location.

### Construct a new record

```python
header = pysam.AlignmentHeader.from_dict(
    {
        "HD": {"VN": "1.6", "SO": "coordinate"},
        "SQ": [{"SN": "chr1", "LN": 248_956_422}],
    }
)

with pysam.AlignmentFile("new.bam", "wb", header=header) as output:
    read = pysam.AlignedSegment(output.header)
    read.query_name = "read001"
    read.query_sequence = "ACGTACGTAA"
    read.flag = 0
    read.reference_id = output.get_tid("chr1")
    read.reference_start = 100
    read.mapping_quality = 60
    read.cigartuples = [(pysam.CIGAR_OPS.CMATCH, 10)]
    read.query_qualities = pysam.qualitystring_to_array("IIIIIIIIII")
    output.write(read)
```

Construct records against the destination header so numeric reference IDs map
correctly. Sequence length, qualities, and query-consuming CIGAR operations
must agree.

## Validation

For BAM/CRAM:

```python
pysam.samtools.quickcheck("-v", "filtered.bam")
pysam.samtools.index("filtered.bam", catch_stdout=False)
```

`quickcheck` checks basic headers and EOF markers, not biological correctness.
Reopen the file, verify header/reference compatibility, and inspect expected
regions. Read `cram_and_performance.md` for CRAM-specific validation.

### `references/api_reference.md`

# Pysam 0.24 API Quick Reference

This is a compact navigation aid, not a replacement for the official API
documentation. Signatures and defaults below are for pysam 0.24.0.

## Alignment Files

### Constructor

```python
pysam.AlignmentFile(
    filepath_or_object,
    mode=None,
    template=None,
    reference_names=None,
    reference_lengths=None,
    text=None,
    header=None,
    add_sq_text=True,
    add_sam_header=True,
    check_header=True,
    check_sq=True,
    reference_filename=None,
    filename=None,
    index_filename=None,
    filepath_index=None,
    require_index=False,
    duplicate_filehandle=True,
    ignore_truncation=False,
    format_options=None,
    threads=1,
)
```

Core methods:

```python
AlignmentFile.fetch(
    contig=None,
    start=None,
    stop=None,
    region=None,
    tid=None,
    until_eof=False,
    multiple_iterators=False,
    reference=None,  # compatibility alias
    end=None,        # compatibility alias
)

AlignmentFile.count(
    contig=None,
    start=None,
    stop=None,
    region=None,
    until_eof=False,
    read_callback="nofilter",
    reference=None,
    end=None,
)

AlignmentFile.count_coverage(
    contig,
    start=None,
    stop=None,
    region=None,
    quality_threshold=15,
    read_callback="all",
    reference=None,
    end=None,
)

AlignmentFile.pileup(
    contig=None,
    start=None,
    stop=None,
    region=None,
    reference=None,
    end=None,
    **kwargs,
)
```

Important pileup kwargs/defaults:

| Option | Default | Meaning |
|---|---:|---|
| `truncate` | `False` | limit columns to exact query interval |
| `max_depth` | `8000` | maximum depth |
| `stepper` | `"samtools"` in current implementation/docs context | read filtering/processing mode |
| `fastafile` | `None` | reference for BAQ/samtools behavior |
| `ignore_overlaps` | `True` | collapse overlapping paired bases |
| `ignore_orphans` | `True` | exclude improper paired orphans |
| `flag_filter` | unmapped, secondary, QC-fail, duplicate | excluded flags |
| `flag_require` | `0` | required flags |
| `min_base_quality` | `13` | base-quality threshold |
| `min_mapping_quality` | `0` | mapping-quality threshold |
| `compute_baq` | `True` | compute BAQ when reference is available |
| `redo_baq` | `False` | recompute existing BAQ |

Always pass important pileup semantics explicitly rather than depending on
defaults.

Other useful methods/properties:

- `write(read)`
- `has_index()` / `check_index()`
- `get_index_statistics()`
- `get_reference_name(tid)` / `get_tid(name)`
- `get_reference_length(name)`
- `find_introns(read_iterator)`
- `head(n, multiple_iterators=True)`
- `references`, `lengths`, `nreferences`
- `mapped`, `unmapped`, `nocoordinate` when index statistics support them

## `AlignedSegment`

Construction:

```python
read = pysam.AlignedSegment(header=None)
```

Prefer passing the destination `AlignmentHeader`.

Frequently used attributes:

- identity: `query_name`, `query_sequence`, `query_qualities`
- query spans: `query_length`, `query_alignment_start`,
  `query_alignment_end`, `query_alignment_length`
- reference: `reference_id`, `reference_name`, `reference_start`,
  `reference_end`, `reference_length`
- mapping: `mapping_quality`, `cigarstring`, `cigartuples`
- mate: `next_reference_id`, `next_reference_name`,
  `next_reference_start`, `template_length`
- flags: `flag` and `is_*` boolean properties

Methods:

- `get_tag(tag, with_value_type=False)`
- `set_tag(tag, value, value_type=None, replace=True)`
- `has_tag(tag)`
- `get_tags(with_value_type=False)`
- `set_tags(tags)`
- `get_aligned_pairs(matches_only=False, with_seq=False, with_cigar=False)`
- `get_blocks()`
- `get_reference_positions(full_length=False)`
- `get_reference_sequence()` (requires MD)
- `get_forward_sequence()` / `get_forward_qualities()`
- `infer_query_length()` / `infer_read_length()`

Modified-base properties:

- `modified_bases`
- `modified_bases_forward`

They return mappings from `(canonical_base, strand, modification)` to
`(query_position, quality)` calls.

## Pileup Objects

`PileupColumn`:

- `reference_id`, `reference_name`, `reference_pos`
- `nsegments`
- `pileups`
- `get_num_aligned()`
- `get_query_sequences(...)`
- `get_query_qualities()`
- `get_mapping_qualities()`

`PileupRead`:

- `alignment`
- `query_position`
- `query_position_or_next`
- `is_del`
- `is_refskip`
- `indel`
- `level`

Proxy objects are valid only while their iterator remains alive.

## Variant Files

### Constructor

```python
pysam.VariantFile(
    filename,
    mode=None,
    index_filename=None,
    header=None,
    drop_samples=False,
    duplicate_filehandle=True,
    ignore_truncation=False,
    threads=1,
)
```

Core methods:

```python
VariantFile.fetch(
    contig=None,
    start=None,
    stop=None,
    region=None,
    reopen=False,
    end=None,
    reference=None,
)

VariantFile.subset_samples(include_samples)
VariantFile.new_record(*args, **kwargs)
VariantFile.write(record)
```

Numeric fetch coordinates are 0-based, half-open. `reopen=True` supports
multiple simultaneous iterators.

`VariantHeader`:

```python
header.copy()
header.add_meta(key, value=None, items=None)
header.add_line(line)
header.add_sample(sample)
header.new_record(
    contig=None,
    start=0,
    stop=0,
    alleles=None,
    id=None,
    qual=None,
    filter=None,
    info=None,
    samples=None,
    **kwargs,
)
```

Metadata collections:

- `contigs`
- `samples`
- `filters`
- `info`
- `formats`
- `records`

`VariantRecord`:

- location: `contig`, `chrom`, `pos`, `start`, `stop`, `rlen`
- alleles: `ref`, `alts`, `alleles`, `alleles_variant_types`
- metadata: `id`, `qual`, `filter`, `info`
- samples: `samples`
- methods: `copy()`, `translate(destination_header)`

## FASTA and FASTX

```python
pysam.FastaFile(
    filename,
    filepath_index=None,
    filepath_index_compressed=None,
)

FastaFile.fetch(
    reference=None,
    start=None,
    end=None,
    region=None,
)

FastaFile.get_reference_length(reference)
```

Properties: `references`, `lengths`, `nreferences`.

```python
pysam.FastxFile(filename, persist=True)
```

Yielded records expose:

- `name`
- `comment`
- `sequence`
- `quality`
- `get_quality_array()`

`persist=False` is faster but returns temporary read-only proxies.

## Tabix

```python
pysam.TabixFile(
    filename,
    index=None,
    mode="r",
    parser=None,
    encoding="ascii",
    threads=1,
)

TabixFile.fetch(
    reference=None,
    start=None,
    end=None,
    region=None,
    parser=None,
    multiple_iterators=False,
)
```

Properties: `contigs`, `header`, `filename`, `index_filename`.

Compression and indexing:

```python
pysam.tabix_compress(
    filename_in,
    filename_out,
    force=False,
)

pysam.tabix_index(
    filename,
    force=False,
    seq_col=None,
    start_col=None,
    end_col=None,
    preset=None,
    meta_char="#",
    line_skip=0,
    zerobased=False,
    min_shift=-1,
    index=None,
    keep_original=False,
    csi=False,
)
```

Parsers:

- `pysam.asTuple()`
- `pysam.asBed()`
- `pysam.asGTF()`
- `pysam.asVCF()`

## Wrapped Commands

Explicit imports:

```python
import pysam.samtools
import pysam.bcftools
```

Each dispatcher has:

```python
command(
    *args: str,
    catch_stdout=True,
    save_stdout=None,
    split_lines=False,
)

command.get_messages()
command.usage()
```

- command-line tokens are separate strings
- stdout is returned by default
- `save_stdout=path` writes captured stdout to a file
- `catch_stdout=False` discards stdout and avoids overriding a command's `-o`
- stderr is captured and available from `get_messages()`
- a nonzero exit raises `pysam.SamtoolsError`

Top-level samtools aliases such as `pysam.sort` exist, but explicit module
imports make provenance clearer. Bcftools should be explicitly imported as
`pysam.bcftools`.

## Convenience Functions

- `pysam.qualitystring_to_array(text)`
- `pysam.array_to_qualitystring(values)`
- `pysam.index(*samtools_args, **dispatcher_kwargs)`
- `pysam.faidx(*samtools_args, **dispatcher_kwargs)`
- `pysam.tabix_compress(...)`
- `pysam.tabix_index(...)`
- `pysam.set_verbosity(level)`

Pysam 0.24 substantially optimized `array_to_qualitystring()`.

## Exceptions

Expect and handle narrowly:

- `ValueError`: invalid coordinates, header/record errors, unusable index
- `OSError` / `IOError`: file, compression, and HTSlib I/O problems
- `IndexError`: out-of-range FASTA coordinates and sequence access
- `KeyError`: missing headers, samples, tags, or fields when accessed directly
- `pysam.SamtoolsError`: wrapped command failure

Do not use `ignore_truncation=True` as general error suppression.

## Compatibility Names to Avoid in New Code

Prefer:

- `AlignmentFile`, not `Samfile`
- `AlignedSegment`, not `AlignedRead`
- `FastxFile`, not `FastqFile`
- `get_tag()` / `set_tag()`, not `opt()` / `setTag()`
- `get_reference_name()` / `get_tid()`, not old PEP8-incompatible names
- `pysam.CIGAR_OPS.CMATCH` and related enum members, not top-level aliases

Compatibility aliases can remain in 0.24 but are poor foundations for new
work.

### `references/common_workflows.md`

# Correct Pysam Workflow Patterns

These patterns target pysam 0.24.0 and make filtering and coordinate semantics
explicit. Adapt thresholds to the assay rather than treating them as universal
defaults.

## Preflight an Analysis

Before combining files, verify:

1. Reference assembly and contig naming agree (`chr1` versus `1`).
2. Numeric coordinates use 0-based, half-open intervals.
3. Alignment and variant inputs are sorted as expected.
4. Random-access inputs have valid indexes.
5. CRAM has the exact reference FASTA available.
6. Read-group/sample metadata identifies the intended samples.
7. Duplicate, secondary, supplementary, QC-fail, and quality policies are
   stated.

Use the bundled inspectors:

```bash
python scripts/inspect_hts.py sample.bam
python scripts/inspect_hts.py cohort.vcf.gz
python scripts/inspect_hts.py reference.fa
```

## Streaming Alignment QC

The bundled script scans in file order and does not require an index:

```bash
python scripts/alignment_qc.py sample.bam --output sample.qc.json
python scripts/alignment_qc.py sample.cram \
  --reference reference.fa \
  --max-records 100000
```

The report counts alignment records, not unique templates or fragments.
Secondary and supplementary records are reported separately. Use
`--max-records` for a sampling pass; omit it for a complete scan.

For index-level counts without reading every record:

```python
import pysam

with pysam.AlignmentFile("sample.bam", "rb", require_index=True) as bam:
    for stats in bam.get_index_statistics():
        print(stats.contig, stats.mapped, stats.unmapped, stats.total)
```

Index statistics are fast but cannot replace custom record-level QC.

## Zero-Aware Coverage

`pileup()` omits positions with no columns. Use `count_coverage()` when zeros
must be represented:

```python
import pysam


def base_depth(
    bam: pysam.AlignmentFile,
    contig: str,
    start: int,
    stop: int,
    *,
    min_base_quality: int = 20,
) -> list[int]:
    a, c, g, t = bam.count_coverage(
        contig,
        start,
        stop,
        quality_threshold=min_base_quality,
        read_callback="all",
    )
    return [sum(counts) for counts in zip(a, c, g, t)]


with pysam.AlignmentFile("sample.bam", "rb") as bam:
    depth = base_depth(bam, "chr1", 1_000, 2_000)
```

`read_callback="all"` excludes unmapped, secondary, QC-fail, and duplicate
records, but not supplementary records. Use a custom callback when
supplementary or low-MAPQ reads must also be excluded:

```python
def usable_read(read: pysam.AlignedSegment) -> bool:
    return (
        not read.is_unmapped
        and not read.is_secondary
        and not read.is_supplementary
        and not read.is_qcfail
        and not read.is_duplicate
        and read.mapping_quality >= 20
    )


a, c, g, t = bam.count_coverage(
    "chr1",
    1_000,
    2_000,
    quality_threshold=20,
    read_callback=usable_read,
)
```

Only A/C/G/T query bases contribute.

### Convert low-depth bases into intervals

```python
def below_threshold_intervals(
    depths: list[int],
    start: int,
    threshold: int,
):
    interval_start = None

    for offset, value in enumerate(depths):
        position = start + offset
        if value < threshold and interval_start is None:
            interval_start = position
        elif value >= threshold and interval_start is not None:
            yield interval_start, position
            interval_start = None

    if interval_start is not None:
        yield interval_start, start + len(depths)
```

The yielded intervals remain 0-based, half-open and correctly include regions
with no aligned columns.

## Exact Pileup at a Position

Use explicit pileup options and retain the iterator:

```python
def aligned_depth_at(
    bam: pysam.AlignmentFile,
    fasta: pysam.FastaFile,
    contig: str,
    position: int,
) -> int:
    iterator = bam.pileup(
        contig,
        position,
        position + 1,
        truncate=True,
        stepper="samtools",
        fastafile=fasta,
        min_mapping_quality=20,
        min_base_quality=20,
        max_depth=100_000,
        ignore_overlaps=True,
        ignore_orphans=True,
    )
    for column in iterator:
        if column.reference_pos == position:
            return column.get_num_aligned()
    return 0
```

This definition is not identical to VCF `INFO/DP` from a caller. Name custom
annotations so their provenance and filters remain clear.

## SNP Base Support

This helper is deliberately limited to single-nucleotide REF/ALT alleles:

```python
from collections import Counter


def snp_base_counts(
    bam: pysam.AlignmentFile,
    fasta: pysam.FastaFile,
    record: pysam.VariantRecord,
) -> Counter[str]:
    if (
        len(record.ref) != 1
        or not record.alts
        or any(len(alt) != 1 for alt in record.alts)
    ):
        raise ValueError("snp_base_counts only supports simple SNP records")

    counts: Counter[str] = Counter()
    iterator = bam.pileup(
        record.contig,
        record.start,
        record.start + 1,
        truncate=True,
        stepper="samtools",
        fastafile=fasta,
        min_mapping_quality=20,
        min_base_quality=20,
        max_depth=100_000,
        ignore_overlaps=True,
        ignore_orphans=True,
    )

    for column in iterator:
        for pileup_read in column.pileups:
            if pileup_read.is_del or pileup_read.is_refskip:
                continue
            query_position = pileup_read.query_position
            if query_position is None:
                continue
            base = pileup_read.alignment.query_sequence[query_position]
            counts[base.upper()] += 1
    return counts
```

For indels, inspect `PileupRead.indel`, CIGAR, and normalized alleles or use a
dedicated variant caller. This SNP method must not be generalized to symbolic
or breakend alleles.

## Annotate a VCF with BAM-Derived Depth

Copy the header, declare a new field, translate copied records, and use
`record.start` directly:

```python
import pysam


def annotate_depth(
    input_vcf: str,
    input_bam: str,
    reference_fasta: str,
    output_vcf: str,
) -> None:
    with pysam.FastaFile(reference_fasta) as fasta, pysam.AlignmentFile(
        input_bam,
        "rb",
        reference_filename=reference_fasta,
    ) as bam, pysam.VariantFile(input_vcf) as source:
        header = source.header.copy()
        if "BAM_BASE_DP" in header.info:
            raise ValueError("BAM_BASE_DP already exists in input header")
        header.info.add(
            "BAM_BASE_DP",
            number=1,
            type="Integer",
            description=(
                "Aligned base depth at POS; MAPQ>=20, baseQ>=20, "
                "samtools pileup filters, paired overlaps collapsed"
            ),
        )

        with pysam.VariantFile(output_vcf, "w", header=header) as output:
            for source_record in source:
                record = source_record.copy()
                record.translate(header)
                record.info["BAM_BASE_DP"] = aligned_depth_at(
                    bam,
                    fasta,
                    record.contig,
                    record.start,
                )
                output.write(record)
```

For CRAM input, `reference_filename` is essential. For a large unindexed VCF,
this pattern can issue many BAM seeks; process by contig or sorted windows to
improve locality.

## Validate VCF REF Alleles Against FASTA

```python
def reference_matches(
    record: pysam.VariantRecord,
    fasta: pysam.FastaFile,
) -> bool:
    observed = fasta.fetch(
        record.contig,
        record.start,
        record.start + len(record.ref),
    )
    return observed.upper() == record.ref.upper()


with pysam.FastaFile("reference.fa") as fasta, pysam.VariantFile(
    "variants.vcf.gz"
) as variants:
    mismatches = [
        (record.contig, record.pos, record.ref)
        for record in variants
        if not reference_matches(record, fasta)
    ]
```

Do not "fix" mismatches automatically. Investigate assembly version, contig
aliases, left normalization, and strand/representation errors.

## Filter an Alignment File

Use the bundled script for common primary-read filtering:

```bash
python scripts/alignment_qc.py input.bam --max-records 10000
python scripts/filter_alignments.py input.bam filtered.bam \
  --min-mapq 20 --exclude-duplicates --exclude-supplementary --index
```

If implementing custom filtering, preserve the source header and stream
records:

```python
with pysam.AlignmentFile("input.bam", "rb") as source, pysam.AlignmentFile(
    "filtered.bam", "wb", template=source
) as output:
    for read in source.fetch(until_eof=True):
        if usable_read(read):
            output.write(read)
```

Filtering preserves input order; it does not sort. Index only coordinate-sorted
output. If the header's sort-order declaration is wrong, fix the workflow
rather than trusting it.

## Extract Strand-Aware BED Sequences

```python
IUPAC_COMPLEMENT = str.maketrans(
    "ACGTRYMKBDHVNacgtrymkbdhvn",
    "TGCAYRKMVHDBNtgcayrkmvhdbn",
)


with pysam.TabixFile(
    "genes.bed.gz", parser=pysam.asBed()
) as genes, pysam.FastaFile("reference.fa") as fasta, open(
    "genes.fa", "x", encoding="utf-8"
) as output:
    for gene in genes.fetch():
        sequence = fasta.fetch(gene.contig, gene.start, gene.end)
        if gene.strand == "-":
            sequence = sequence.translate(IUPAC_COMPLEMENT)[::-1]
        output.write(f">{gene.name}\n{sequence}\n")
```

BED parser coordinates are already 0-based. Sanitize or encode record names if
they will be consumed by strict downstream FASTA parsers.

## Count RNA Splice Junctions

`find_introns()` counts `N` CIGAR operations:

```python
with pysam.AlignmentFile("rna.bam", "rb") as bam:
    primary_reads = (
        read
        for read in bam.fetch("chr1")
        if not read.is_secondary
        and not read.is_supplementary
        and not read.is_duplicate
        and read.mapping_quality >= 20
    )
    junction_counts = bam.find_introns(primary_reads)
```

Keys are `(start, stop)` 0-based splice intervals. Filter strand and library
orientation according to the assay.

## Bulk Operations via Wrapped Tools

For sort/index and normalization, mature command implementations are usually
preferable to Python record loops:

```python
import pysam.samtools
import pysam.bcftools

pysam.samtools.sort(
    "-@", "4",
    "-o", "sorted.bam",
    "input.bam",
    catch_stdout=False,
)
pysam.samtools.index(
    "-@", "4",
    "sorted.bam",
    catch_stdout=False,
)

pysam.bcftools.norm(
    "-f", "reference.fa",
    "-m", "-any",
    "-Oz",
    "-o", "normalized.vcf.gz",
    "input.vcf.gz",
    catch_stdout=False,
)
pysam.bcftools.index(
    "--csi",
    "normalized.vcf.gz",
    catch_stdout=False,
)
```

Pass each argument as its own string. Do not split or evaluate an untrusted
shell command. Use `catch_stdout=False` when `-o` writes large or binary data.

## Do Not Hand-Roll Complex VCF Merges

Combining records by `(contig, pos, ref, alts)` is insufficient because inputs
can differ in:

- allele normalization and multiallelic decomposition
- contig order and metadata
- INFO/FORMAT Number and Type definitions
- FILTER definitions
- sample names and ploidy
- duplicate positions and phasing

Normalize and validate inputs, then use `bcftools merge` for samples or
`bcftools concat` for disjoint genomic partitions as appropriate.

## Output Validation

Alignment output:

```python
pysam.samtools.quickcheck("-v", "filtered.bam")
```

Variant output:

```python
with pysam.VariantFile("annotated.vcf.gz") as variants:
    assert "BAM_BASE_DP" in variants.header.info
```

Then index final sorted output and fetch known intervals at contig starts,
interval boundaries, and high-coordinate regions. Format validity does not
prove biological validity; compare counts and selected records to an
independent tool when results matter.

### `references/coordinates_and_indexing.md`

# Coordinates and Indexing

Coordinate mistakes and stale indexes are the most common causes of plausible
but wrong genomic results. This reference targets pysam 0.24.0.

## The Pysam Rule

For Python API numeric arguments and properties, pysam uses **0-based,
half-open** intervals:

```text
[start, stop)
```

The first base is `0`; `start` is included and `stop` is excluded. Interval
length is `stop - start`.

The main exception is a textual samtools-style region string, which is
**1-based, inclusive**:

```text
chr1:100-199
```

These refer to the same 100 bases:

```python
file.fetch("chr1", 99, 199)
file.fetch(region="chr1:100-199")
```

This rule applies to:

- `AlignmentFile.fetch()`, `count()`, `count_coverage()`, and `pileup()`
- `VariantFile.fetch()`
- `FastaFile.fetch()`
- `TabixFile.fetch()`

Do not treat numeric `VariantFile.fetch()` arguments as VCF text coordinates.

## Format Conversion Table

| Source representation | Source convention | Convert to pysam numeric |
|---|---|---|
| BED `chromStart`, `chromEnd` | 0-based, half-open | use unchanged |
| VCF `POS` and REF | 1-based position | `start = POS - 1`; `stop = start + len(REF)` unless record semantics provide another end |
| `VariantRecord.start`, `.stop` | 0-based, half-open | use unchanged |
| GFF/GTF start/end columns | 1-based, inclusive | `start = start_text - 1`; `stop = end_text` |
| SAM `POS` | 1-based leftmost base | use `AlignedSegment.reference_start` |
| samtools region string | 1-based, inclusive | pass as `region=...`, or convert both endpoints |

For VCF structural variants, symbolic alleles, breakends, and records with
`INFO/END`, use `VariantRecord.start` and `VariantRecord.stop` rather than
reconstructing the interval from `len(REF)`.

## Single Positions

A 1-based position `p` becomes the one-base Python interval:

```python
start = p - 1
stop = p
```

For a VCF record:

```python
assert record.start == record.pos - 1
base = fasta.fetch(record.contig, record.start, record.start + 1)
```

## Overlap Versus Containment

Region fetches are overlap queries. An alignment or variant can begin before
the requested interval and still overlap it.

To require complete containment:

```python
def fully_contained(read, start: int, stop: int) -> bool:
    return (
        read.reference_start is not None
        and read.reference_end is not None
        and read.reference_start >= start
        and read.reference_end <= stop
    )
```

For point-based logic, define exactly what "overlap" means for deletions,
reference skips, symbolic alleles, and breakends.

`pileup()` has an additional trap: without `truncate=True`, it can emit columns
outside the requested interval because reads overlap the interval.

## Parser Coordinates

Pysam parser objects normalize coordinates:

- `asBed().start` / `.end`: 0-based, half-open
- `asGTF().start` / `.end`: exposed in Python coordinate convention
- `asVCF().pos`: parser-specific lightweight field; use `VariantFile` for full
  VCF record semantics

When creating a custom tabix index:

- `seq_col`, `start_col`, and `end_col` are 0-based **column indices**
- file coordinates default to 1-based unless `zerobased=True`
- later `TabixFile.fetch()` numeric query coordinates are still 0-based

These are three distinct concepts: Python column index, coordinate encoding in
the stored table, and coordinate encoding in the query.

## Contig Identity

Coordinate conversion does not solve contig mismatches. Check:

- `chr1` versus `1`
- mitochondrial names (`chrM`, `MT`, `M`)
- alternate loci and decoys
- assembly version (for example GRCh37 versus GRCh38)
- contig order and lengths

```python
alignment_contigs = dict(zip(bam.references, bam.lengths))
fasta_contigs = dict(zip(fasta.references, fasta.lengths))

shared = alignment_contigs.keys() & fasta_contigs.keys()
length_mismatches = {
    name: (alignment_contigs[name], fasta_contigs[name])
    for name in shared
    if alignment_contigs[name] != fasta_contigs[name]
}
```

Do not silently strip or add `chr` across arbitrary assemblies. Use an explicit
reviewed mapping.

## Index Matrix

| Data | Random-access index | Sort requirement |
|---|---|---|
| BAM | `.bai` or `.csi` | coordinate order |
| CRAM | `.crai` | coordinate order |
| BGZF VCF | `.tbi` or `.csi` | contig/position order |
| BCF | `.csi` | contig/position order |
| FASTA | `.fai`; BGZF FASTA also `.gzi` | FASTA layout, not coordinate sort |
| BED/GFF/GTF/custom BGZF table | `.tbi` or `.csi` | contig/start order |
| SAM / ordinary VCF / FASTQ | no random-access index through these APIs | sequential only |

An index is a view of a specific file. If the data file changes, rebuild the
index. A stale index may fail loudly or return wrong/incomplete regions.

## BAI/TBI Versus CSI

Legacy BAI and standard TBI indexes have a maximum coordinate near `2^29`
(512 Mi bases). This is insufficient for some plant, animal, and synthetic
references. CSI is parameterized and supports larger coordinates.

Create a BAM CSI:

```python
import pysam

pysam.index("-c", "large-reference.bam", catch_stdout=False)
```

Create a tabix CSI:

```python
pysam.tabix_index(
    "large-reference.bed.gz",
    preset="bed",
    csi=True,
    min_shift=14,
)
```

Create a VCF/BCF CSI:

```python
import pysam.bcftools

pysam.bcftools.index(
    "--csi",
    "variants.vcf.gz",
    catch_stdout=False,
)
```

Prefer CSI when reference sizes are unknown or potentially large. Confirm
downstream tools support it.

## Sort Before Indexing

Indexing does not sort records.

BAM:

```python
import pysam.samtools

pysam.samtools.sort(
    "-@", "4",
    "-o", "sorted.bam",
    "input.bam",
    catch_stdout=False,
)
pysam.samtools.index(
    "-@", "4",
    "sorted.bam",
    catch_stdout=False,
)
```

VCF:

```python
import pysam.bcftools

pysam.bcftools.sort(
    "-Oz",
    "-o", "sorted.vcf.gz",
    "input.vcf",
    catch_stdout=False,
)
pysam.bcftools.index(
    "--csi",
    "sorted.vcf.gz",
    catch_stdout=False,
)
```

Tabix tables must be sorted before `tabix_index()`. The Python function does
not verify sort order.

## Safe Tabix Creation

Prefer separate compression and indexing:

```python
pysam.tabix_compress("regions.bed", "regions.bed.gz")
pysam.tabix_index("regions.bed.gz", preset="bed")
```

Calling `tabix_index("regions.bed")` can automatically create
`regions.bed.gz` and remove the original. Use `keep_original=True` if relying
on that one-step path.

Do not pass `force=True` by default. Existing output should trigger review,
not silent replacement.

## Nonstandard and Remote Index Locations

Pass an explicit index:

```python
with pysam.AlignmentFile(
    "sample.bam",
    "rb",
    index_filename="indexes/sample.csi",
) as bam:
    ...

with pysam.VariantFile(
    "cohort.vcf.gz",
    index_filename="indexes/cohort.vcf.gz.csi",
) as variants:
    ...
```

Remote random access additionally depends on:

- an HTSlib build with the relevant network/plugin support
- a reachable index
- server range requests
- stable data and index URLs

Pass `index_filename` explicitly when automatic URL derivation is unreliable.
Read `cram_and_performance.md` before remote or CRAM access.

## Index Checks

Alignment:

```python
with pysam.AlignmentFile("sample.bam", "rb") as bam:
    if not bam.has_index():
        raise ValueError("random access requires a BAM/CRAM index")
    bam.check_index()
```

Variant and tabix constructors open a discovered index automatically; a region
fetch fails when none is available. Reopen output and test known regions rather
than checking only that an index filename exists.

## Boundary Tests

For important pipelines, test:

- first base of a contig
- exact interval start and stop
- a record spanning the query boundary
- a zero-length or invalid interval
- contig end
- a high coordinate beyond 512 Mi bases when CSI is expected
- missing and aliased contigs
- region string and numeric equivalents

One useful invariant:

```python
numeric = list(file.fetch(contig, start, stop))
region = f"{contig}:{start + 1}-{stop}"
textual = list(file.fetch(region=region))
```

For the same indexed file and valid nonempty interval, these queries should
select equivalent records.

### `references/cram_and_performance.md`

# CRAM, Remote I/O, Threads, and Performance

This reference targets pysam 0.24.0, which embeds HTSlib/samtools/bcftools
1.23.1.

## Pysam 0.24 CRAM Changes

Pysam 0.24 is the first pysam release to wrap HTSlib 1.22 or later. Two
inherited operational changes matter:

1. New CRAM output defaults to CRAM **3.1**, not 3.0.
2. HTSlib no longer contacts the EBI CRAM reference server by default.

For compatibility with a consumer that cannot read CRAM 3.1:

```python
with pysam.AlignmentFile(
    "output.cram",
    "wc",
    header=header,
    reference_filename="reference.fa",
    format_options=["version=3.0"],
) as output:
    ...
```

In pysam 0.24, `format_options` accepts a list of Python `str` values as
documented.

## Why the Reference Matters

CRAM commonly stores differences from a reference rather than complete read
sequences. A matching reference can therefore be required to decode or encode
records.

Reference identity is represented by `M5` MD5 values and often `UR` fields in
`@SQ` header lines. Contig names alone are not sufficient.

Treat the reference as part of the data provenance:

- preserve the exact FASTA used to create the CRAM
- preserve its `.fai`
- record assembly/version and checksum
- back up reference cache content when it is the only decoding source
- verify contig lengths and M5 tags

Some CRAM files embed all or part of their reference, but do not assume that
every CRAM is self-contained.

## Deterministic Local CRAM Access

Prefer an explicit local FASTA:

```python
import pysam

pysam.faidx("reference.fa")

with pysam.AlignmentFile(
    "sample.cram",
    "rc",
    reference_filename="reference.fa",
    require_index=True,
    threads=4,
) as cram:
    for read in cram.fetch("chr1", 1_000, 2_000):
        ...
```

Use the same reference when writing:

```python
with pysam.AlignmentFile("input.bam", "rb") as source, pysam.AlignmentFile(
    "output.cram",
    "wc",
    template=source,
    reference_filename="reference.fa",
    threads=4,
) as destination:
    for read in source.fetch(until_eof=True):
        destination.write(read)
```

Then create a CRAI and read the output back with the same FASTA.

## `REF_PATH` and `REF_CACHE`

Use these HTSlib environment variables only when reference-by-MD5 lookup is
intentional:

- `REF_PATH`: colon-separated local paths and optionally URLs used to find a
  sequence by its M5 checksum
- `REF_CACHE`: location where retrieved references are cached

A local cache layout commonly uses:

```text
/reference-cache/%2s/%2s/%s
```

Do not add a remote endpoint merely to make an error disappear. Network
reference lookup changes reproducibility, privacy, availability, and cache
behavior. Pysam 0.24 intentionally inherits HTSlib's removal of implicit EBI
fetching.

When remote lookup is required:

- configure a controlled institutional proxy/cache where possible
- place a local cache before remote sources
- ensure downloads are checksum-validated
- document network and retention behavior
- avoid credentials in URLs and logs

An explicit `reference_filename=` is usually clearer for a single known
assembly.

## Convert BAM to CRAM with Wrapped Samtools

For bulk conversion:

```python
import pysam.samtools

pysam.samtools.view(
    "-@",
    "4",
    "-C",
    "-T",
    "reference.fa",
    "-o",
    "output.cram",
    "input.bam",
    catch_stdout=False,
)
pysam.samtools.index(
    "-@",
    "4",
    "output.cram",
    catch_stdout=False,
)
```

Using `-o` plus `catch_stdout=False` avoids capturing binary CRAM output in
Python memory.

Validate:

```python
pysam.samtools.quickcheck("-v", "output.cram")

with pysam.AlignmentFile(
    "output.cram",
    "rc",
    reference_filename="reference.fa",
) as cram:
    first = next(cram.fetch(until_eof=True), None)
```

`quickcheck` is structural, not a full decode or biological validation.
Compare record counts and selected records to the source.

## CRAM Failure Diagnosis

When CRAM open/fetch fails, check in this order:

1. Confirm the FASTA assembly and contig names.
2. Confirm `.fai` exists and lengths match the alignment header.
3. Inspect `@SQ` `M5` and `UR` fields.
4. Pass `reference_filename=` explicitly.
5. Confirm CRAI matches the current CRAM.
6. Try a sequential read to separate index from reference problems.
7. Capture HTSlib/samtools error messages.

Do not disable validation or substitute a similarly named assembly.

## Remote HTSlib I/O

Depending on how the wheel/build was configured, HTSlib can read HTTP(S) and
other plugin-backed URLs. Random access also needs a reachable index and range
request support.

```python
with pysam.AlignmentFile(
    "https://example.org/data/sample.bam",
    "rb",
    index_filename="https://example.org/data/sample.bam.bai",
) as bam:
    for read in bam.fetch("chr1", 1_000, 2_000):
        ...
```

Remote support is build- and protocol-dependent. Before large analysis:

- issue one small known region query
- verify the exact index URL
- check content versioning/immutability
- confirm retries, timeout behavior, and credentials outside logs
- estimate request count from the access pattern

Many tiny random queries can be slower and more expensive than downloading or
staging a file once. Never put bearer tokens or secrets directly in committed
URLs.

## Threads

`threads=` on `AlignmentFile`, `VariantFile`, and `TabixFile` controls HTSlib
compression/decompression threads:

```python
with pysam.AlignmentFile("sample.bam", "rb", threads=4) as bam:
    ...
```

It does **not** parallelize Python filtering, pileup interpretation, or
statistical analysis. More threads can increase memory and I/O contention, and
returns diminish when storage or network is the bottleneck.

`threads > 1` cannot be combined with `ignore_truncation=True`.

## Python Thread Safety

Pysam releases the GIL for many I/O-intensive operations, but not every code
path has been comprehensively validated for thread safety.

Avoid sharing one active file handle across threads. Prefer:

- one independently opened handle per worker, or
- independent `fetch(..., multiple_iterators=True)` iterators when the
  overhead is acceptable

Variant iterators use `fetch(..., reopen=True)`; Tabix and alignment iterators
use `multiple_iterators=True`.

Reopening a remote file for every small iterator can be especially expensive.

## Multiprocessing

Partition work by independent contigs or nonoverlapping windows, but reopen
files inside each process:

```python
def process_region(bam_path: str, contig: str, start: int, stop: int):
    with pysam.AlignmentFile(bam_path, "rb", threads=1) as bam:
        return bam.count(contig, start, stop, read_callback="all")
```

Do not pass live pysam handles or proxy records between processes. Balance
process count and HTSlib `threads`; multiplying both can oversubscribe CPUs.

When partitioning pileup or coverage, include any necessary boundary context
and trim results back to the target windows. Reads overlap partition
boundaries.

## Access-Pattern Guidance

### Prefer sequential scans when

- every record is needed
- the file is unindexed
- remote request overhead dominates
- aggregate QC is being calculated

Use `fetch(until_eof=True)` for alignments and normal iteration for variants.

### Prefer indexed queries when

- only a small fraction of the genome is needed
- regions are grouped and ordered
- an index is available and current

Sort region requests by contig/start to improve locality. Merge heavily
overlapping windows when duplicate processing is not desired.

### Prefer native bulk commands when

- sorting, merging, indexing, or format conversion
- normalizing VCF
- producing standard command outputs

The wrapped samtools/bcftools implementations are usually faster and more
tested than equivalent Python loops.

## Pileup and Coverage Performance

- `count()` is appropriate for overlap-record counts.
- `count_coverage()` efficiently returns dense A/C/G/T arrays for an interval.
- `pileup()` is needed for base/read-level state but has more Python overhead.
- The default pileup depth cap is 8000; changing it can materially affect
  memory and results.
- Avoid one pileup call per nearby variant; group variants into windows or
  traverse columns once.
- Do not materialize all reads or pileup proxies into a list.

## File-Handle and Proxy Lifetimes

Pysam exposes proxy objects backed by HTSlib memory. Keep the owning file and
iterator alive while using:

- `PileupColumn`
- `PileupRead`
- `persist=False` FASTX records

Copy primitive values if data must outlive iteration.

## Reproducibility Checklist

- pin pysam (`pysam==0.24.0`)
- record `pysam.__version__` and `pysam.__samtools_version__`
- record reference FASTA checksum and assembly
- record CRAM output version
- record command arguments and filtering thresholds
- write outputs and indexes atomically or to new paths
- validate representative regions after writing
- avoid hidden network reference dependencies

### `references/migration_to_0_24.md`

# Migration to Pysam 0.24

Use this checklist when moving an existing environment or pipeline to
pysam 0.24.0.

## Runtime Baseline

- Pysam 0.24.0 was released 27 April 2026.
- It was tested with Python 3.8–3.14.
- It wraps HTSlib/samtools/bcftools 1.23.1.
- It requires Cython 3 when building/extending from source.
- The release notes expect 0.24 to be the final line supporting Python 3.8.

For a reproducible environment:

```bash
uv pip install "pysam==0.24.0"
```

If maintaining Python/Cython extensions that cimport pysam declarations,
rebuild them against 0.24. Do not reuse binaries built against a different
pysam ABI without verification.

## CRAM Behavior

### Output version

New CRAM output defaults to CRAM 3.1. If downstream software only supports
3.0:

```python
pysam.AlignmentFile(
    "output.cram",
    "wc",
    header=header,
    reference_filename="reference.fa",
    format_options=["version=3.0"],
)
```

Upgrade downstream tooling instead of forcing 3.0 when possible.

### Reference lookup

Implicit EBI reference fetching is no longer enabled by default. Existing
pipelines that relied on hidden network retrieval can now fail.

Preferred fix:

```python
pysam.AlignmentFile(
    "input.cram",
    "rc",
    reference_filename="reference.fa",
)
```

Only configure `REF_PATH` and `REF_CACHE` when managed checksum-based lookup is
intentional. Do not restore remote fetching without documenting network,
cache, and provenance behavior.

## `format_options`

Pysam 0.24 fixes Python 3 handling so `AlignmentFile(format_options=...)` and
`HTSFile.add_hts_options()` accept documented `str` values rather than
requiring bytes:

```python
format_options=["version=3.0"]
```

Remove workarounds that encode these strings to bytes.

## CIGAR Constants

Pysam 0.23.2 restored top-level aliases such as `pysam.CMATCH` after a Cython
behavior change, but the release notes warn that a future release will remove
them.

Migrate new and maintained code:

```python
# Compatibility alias
pysam.CMATCH

# Preferred
pysam.CIGAR_OPS.CMATCH
```

Audit all CIGAR operators, not only `CMATCH`.

## Modified Bases

Pysam 0.24:

- removes the prior five-modification-type limit in
  `AlignedSegment.modified_bases`
- fixes a crash for degenerate MM fields that describe no modified bases

Retest MM/ML parsing with:

- multiple modification codes
- empty/degenerate MM tags
- missing ML tags
- forward and reverse alignments
- `modified_bases_forward`

## Quality Conversion

`pysam.array_to_qualitystring()` was optimized substantially in 0.24. Remove
custom micro-optimizations only after confirming identical handling of missing
or invalid values.

## Coverage and Python 3.13+

The 0.24 release fixes coverage functionality for Python 3.13 and later.
Re-run `count_coverage()` regression cases when upgrading both Python and
pysam:

- zero-depth positions
- base-quality threshold boundaries
- duplicate/secondary/supplementary filtering
- ambiguous query bases
- contig boundaries

## Variant Documentation and Errors

Pysam 0.24 adds documentation for many `VariantHeader` and `VariantRecord`
internal field wrappers. Prefer documented public mappings and methods over
introspection into Cython implementation details.

Recent 0.23.x releases also improved `AlignmentFile` and `VariantFile` I/O
exception handling. Catch specific `OSError`/`ValueError` conditions and do
not depend on old message text.

## Avoid Pysam 0.23.1 for Cython Extensions

Pysam 0.23.1 was yanked because it broke binary compatibility for Cython
projects by changing `AlignedSegment` size. Pysam 0.23.2 restored
compatibility. Pure Python users were not affected in the same way.

When migrating from 0.23:

- skip 0.23.1
- rebuild extension modules
- test Cython cimports against the 0.24 declarations

## Dispatcher Output

Keep wrapped command output out of memory for bulk or binary operations:

```python
import pysam.samtools

pysam.samtools.sort(
    "-o",
    "sorted.bam",
    "input.bam",
    catch_stdout=False,
)
```

This is not new to 0.24, but it is important when updating older examples that
omit `catch_stdout=False`.

## Regression Checklist

1. Print and record `pysam.__version__` and `pysam.__samtools_version__`.
2. Open representative BAM, CRAM, VCF.gz, BCF, FASTA, FASTQ, and tabix files.
3. Compare numeric queries with equivalent region strings.
4. Decode CRAM with no network and an explicit reference.
5. Write/read CRAM 3.1; test 3.0 only if required.
6. Rebuild all Cython extensions.
7. Exercise pileup and `count_coverage()` thresholds.
8. Test modified-base MM/ML edge cases.
9. Run sort/index/normalization dispatchers with file output.
10. Recreate indexes and compare known regions and aggregate counts.

### `references/sequence_files.md`

# FASTA, FASTQ, and Tabix-Indexed Files

This reference targets pysam 0.24.0.

## Indexed FASTA

`FastaFile` provides random access through a faidx index.

```python
import pysam

pysam.faidx("reference.fa")

with pysam.FastaFile("reference.fa") as fasta:
    print(fasta.references)
    print(fasta.lengths)
    print(fasta.get_reference_length("chr1"))
```

An uncompressed FASTA needs `<name>.fai`. A BGZF-compressed FASTA also needs a
`.gzi` compressed-offset index. Ordinary gzip is not suitable for indexed
random access.

The constructor can use nonstandard index paths:

```python
fasta = pysam.FastaFile(
    "reference.fa.gz",
    filepath_index="indexes/reference.fa.gz.fai",
    filepath_index_compressed="indexes/reference.fa.gz.gzi",
)
```

### Numeric and string coordinates

```python
with pysam.FastaFile("reference.fa") as fasta:
    # Numeric: 0-based, half-open
    sequence = fasta.fetch("chr1", 999, 1_099)

    # Region string: 1-based, inclusive
    same_sequence = fasta.fetch(region="chr1:1000-1099")
```

If start or end is omitted, pysam uses the sequence boundary. Invalid regions
raise `ValueError` or `IndexError`; do not silently clip unless that is the
documented workflow.

### Fetch variant context

```python
def variant_context(
    fasta: pysam.FastaFile,
    contig: str,
    pos_1based: int,
    ref: str,
    flank: int = 20,
) -> tuple[str, bool]:
    start = pos_1based - 1
    context_start = max(0, start - flank)
    context_stop = min(
        fasta.get_reference_length(contig),
        start + len(ref) + flank,
    )
    context = fasta.fetch(contig, context_start, context_stop)
    observed_ref = fasta.fetch(contig, start, start + len(ref))
    return context, observed_ref.upper() == ref.upper()
```

Validate the entire REF allele, not only its first base. A mismatch often
means the VCF and FASTA use different assemblies, contig aliases, or
normalization.

### Strand-aware extraction

Coordinates do not encode strand. Reverse-complement after fetching:

```python
IUPAC_COMPLEMENT = str.maketrans(
    "ACGTRYMKBDHVNacgtrymkbdhvn",
    "TGCAYRKMVHDBNtgcayrkmvhdbn",
)


def reverse_complement(sequence: str) -> str:
    return sequence.translate(IUPAC_COMPLEMENT)[::-1]


sequence = fasta.fetch("chr1", start, stop)
if strand == "-":
    sequence = reverse_complement(sequence)
```

Confirm annotation coordinates before conversion: BED is normally 0-based
half-open; GFF/GTF text is normally 1-based inclusive.

## Sequential FASTA and FASTQ

`FastxFile` streams FASTA, FASTQ, or mixed FASTX records. It does not implement
random access.

```python
with pysam.FastxFile("reads.fastq.gz") as reads:
    for record in reads:
        print(record.name)
        print(record.sequence)
        print(record.comment)
        print(record.quality)
```

The current class is `FastxFile`; `FastqFile` is an old compatibility name.

### Record persistence

`persist=True` is the default and copies each record so it remains valid.
For high-throughput scans, `persist=False` avoids the copy:

```python
with pysam.FastxFile("reads.fastq.gz", persist=False) as reads:
    for record in reads:
        process(record.name, record.sequence)
        # Do not save `record` for use after the iterator advances.
```

With `persist=False`, records are read-only proxies and cease to be valid after
iteration advances. Copy needed strings or use the default when retaining
records.

### Quality scores

```python
with pysam.FastxFile("reads.fastq") as reads:
    for record in reads:
        if record.quality is None:  # FASTA record
            continue
        qualities = record.get_quality_array()
        mean_quality = (
            sum(qualities) / len(qualities) if qualities else None
        )
```

Pysam converts the FASTQ quality string to numeric Phred scores. Confirm the
source encoding for legacy FASTQ; modern data is normally Phred+33.

### Safe writing

`str(record)` preserves whether the record is FASTA or FASTQ and includes the
comment and quality line correctly:

```python
with pysam.FastxFile("reads.fastq.gz") as source, open(
    "filtered.fastq", "x", encoding="utf-8"
) as destination:
    for record in source:
        qualities = record.get_quality_array()
        if qualities and sum(qualities) / len(qualities) >= 20:
            destination.write(str(record) + "\n")
```

Use exclusive creation (`"x"`) when replacement was not requested. Manual
four-line FASTQ formatting can lose comments or create sequence/quality length
mismatches.

### Streaming statistics

```python
def fastx_stats(path: str) -> dict[str, float | int | None]:
    record_count = 0
    base_count = 0
    quality_sum = 0
    quality_count = 0

    with pysam.FastxFile(path, persist=False) as records:
        for record in records:
            record_count += 1
            base_count += len(record.sequence)
            if record.quality is not None:
                qualities = record.get_quality_array()
                quality_sum += sum(qualities)
                quality_count += len(qualities)

    return {
        "records": record_count,
        "bases": base_count,
        "mean_length": (
            base_count / record_count if record_count else None
        ),
        "mean_quality": (
            quality_sum / quality_count if quality_count else None
        ),
    }
```

This is a full scan but has constant memory.

## BGZF and Tabix

`TabixFile` provides random access to coordinate-sorted, BGZF-compressed
tabular files.

### Non-destructive compression and indexing

```python
import pysam

pysam.tabix_compress("regions.bed", "regions.bed.gz")
pysam.tabix_index("regions.bed.gz", preset="bed")
```

This leaves `regions.bed` intact. By contrast, calling `tabix_index()` directly
on an uncompressed file may automatically compress it and remove the original
unless `keep_original=True`.

Do not use `force=True` unless replacing existing compressed data or indexes is
explicitly intended.

### Input requirements

- Sort by contig and coordinate first. `tabix_index()` does not verify sort
  order.
- Use BGZF, not ordinary gzip.
- Select the correct preset: commonly `bed`, `gff`, `sam`, or `vcf`.
- Presets define columns and coordinate conventions.

For a custom table:

```python
pysam.tabix_index(
    "custom.tsv.gz",
    seq_col=0,
    start_col=1,
    end_col=2,
    zerobased=True,
)
```

Python column indices are 0-based. File coordinates are assumed 1-based unless
`zerobased=True`. This is separate from query coordinates, which are always
numeric 0-based in the Python API.

Use CSI for references beyond legacy TBI limits:

```python
pysam.tabix_index(
    "regions.bed.gz",
    preset="bed",
    csi=True,
    min_shift=14,
)
```

### Querying

```python
with pysam.TabixFile(
    "regions.bed.gz",
    parser=pysam.asBed(),
    threads=4,
) as regions:
    for row in regions.fetch("chr1", 1_000, 2_000):
        print(row.contig, row.start, row.end, row.name)
```

Numeric query coordinates are 0-based, half-open. Region strings are
samtools-style 1-based inclusive.

Useful parsers:

- `pysam.asTuple()`: tuple-like fields
- `pysam.asBed()`: BED fields with 0-based start/end
- `pysam.asGTF()`: GTF/GFF-like fields and attributes
- `pysam.asVCF()`: lightweight tabix VCF parser

For complete VCF semantics, use `VariantFile`, not `TabixFile(asVCF())`.

Without a parser, each result is the raw tab-delimited string:

```python
with pysam.TabixFile("annotations.tsv.gz") as table:
    for line in table.fetch("chr1", 1_000, 2_000):
        fields = line.split("\t")
```

### Headers and multiple iterators

```python
with pysam.TabixFile("annotations.gff.gz") as table:
    header_lines = list(table.header)
    first = table.fetch("chr1", multiple_iterators=True)
    second = table.fetch("chr2", multiple_iterators=True)
```

Header lines are yielded without trailing newlines. Each
`multiple_iterators=True` iterator reopens the file and adds overhead.

## Choosing the Right Interface

| Data | Interface | Access |
|---|---|---|
| Reference FASTA | `FastaFile` | indexed random access |
| FASTA/FASTQ reads | `FastxFile` | sequential |
| BED/GFF/GTF/custom table | `TabixFile` | BGZF + tabix/CSI random access |
| VCF/BCF | `VariantFile` | structured records, sequential or indexed |

## Common Pitfalls

- Mixing numeric 0-based coordinates with 1-based region strings
- Expecting `FastaFile` to open without `.fai`
- Using ordinary gzip for indexed FASTA or tabix data
- Retaining a `persist=False` FASTX proxy
- Assuming every FASTX record has qualities
- Manually formatting FASTQ and losing comments or quality alignment
- Letting `tabix_index()` remove the uncompressed source unexpectedly
- Indexing an unsorted file
- Forgetting `zerobased=True` for custom 0-based table coordinates
- Using a TBI index for coordinates beyond its legacy range

### `references/sources.md`

# Authoritative Sources

Last researched: **2026-07-23**

Skill baseline: **pysam 0.24.0**, released **2026-04-27**, wrapping
**HTSlib/samtools/bcftools 1.23.1**.

Use these sources in priority order when refreshing this skill. Do not assume
that the newest standalone HTSlib release is the version embedded in the
current pysam wheel.

## Pysam Release and Package Metadata

- [pysam on PyPI](https://pypi.org/project/pysam/) — current published version,
  release date, wheels, release history, and provenance attestations
- [Pysam release notes](https://pysam.readthedocs.io/en/latest/release.html) —
  0.24 CRAM changes, Python support, bundled component versions, bug fixes, and
  deprecations
- [pysam-developers/pysam](https://github.com/pysam-developers/pysam) —
  upstream source and current development state
- [pysam 0.24.0 source tag](https://github.com/pysam-developers/pysam/tree/v0.24.0)
  — version-specific implementation and tests

As of the research date, PyPI identifies 0.24.0 as latest. The 0.24 release
notes state:

- tested Python versions: 3.8 through 3.14
- wheels: macOS and Linux, ARM and x86-64
- bundled HTSlib/samtools/bcftools: 1.23.1
- default newly written CRAM: 3.1
- implicit EBI CRAM reference fetching: removed
- `format_options`: Python `str` values work as documented
- top-level CIGAR constants remain compatibility aliases; prefer
  `pysam.CIGAR_OPS`

Re-check all of these before changing the version pin.

## Official Pysam Documentation

- [Documentation index](https://pysam.readthedocs.io/en/latest/index.html)
- [Installation](https://pysam.readthedocs.io/en/latest/installation.html)
- [Usage guide](https://pysam.readthedocs.io/en/latest/usage.html)
- [API reference](https://pysam.readthedocs.io/en/latest/api.html)
- [FAQ](https://pysam.readthedocs.io/en/latest/faq.html)
- [Release notes](https://pysam.readthedocs.io/en/latest/release.html)
- [Glossary](https://pysam.readthedocs.io/en/latest/glossary.html)

Use the API reference for signatures and documented defaults. Use the FAQ for
iterator lifetime, threading, coordinate, pileup, and quality-editing
behavior. Where prose in the older usage guide conflicts with the current API,
verify against the 0.24 source/tests and installed runtime.

One known example: a real Python file object exposing `fileno()` works with
`AlignmentFile`, while `io.BytesIO` does not. The API constructor documents
file-object support; the usage guide's broad statement about "true python file
objects" is too general.

## Bundled Tool Manuals

Pysam 0.24 wraps the 1.23.1 tool line. Consult manuals matching that line when
using dispatchers:

- [samtools 1.23 manual](https://www.htslib.org/doc/1.23/samtools.html)
- [bcftools 1.23 manual](https://www.htslib.org/doc/1.23/bcftools.html)
- [tabix 1.23 manual](https://www.htslib.org/doc/1.23/tabix.html)
- [bgzip 1.23 manual](https://www.htslib.org/doc/1.23/bgzip.html)
- [faidx 1.23 format/manual](https://www.htslib.org/doc/1.23/faidx.html)
- [HTSlib documentation index](https://www.htslib.org/doc/)

Pysam dispatchers emulate command-line subcommands but capture stdout/stderr.
The pysam usage guide, not only the tool manual, defines `catch_stdout`,
`save_stdout`, `split_lines`, `get_messages()`, and `SamtoolsError`.

## CRAM References

- [Pysam 0.24 release notes](https://pysam.readthedocs.io/en/latest/release.html#release-0-24-0)
  — CRAM 3.1 default and removal of implicit EBI lookup
- [Samtools reference-sequence guidance](https://www.htslib.org/doc/1.23/samtools.html)
  — CRAM reference search order and `REF_PATH`/`REF_CACHE`
- [Using CRAM within Samtools](https://www.htslib.org/workflow/cram.html) —
  reference-based compression, M5 tags, local caches, and workflow concepts

The older CRAM workflow page describes historical fallback to EBI. For pysam
0.24/HTSlib 1.23 behavior, the 0.24 release notes and matching samtools manual
take precedence: implicit EBI lookup is no longer the default.

## Canonical Format Specifications

- [HTS format specifications index](https://samtools.github.io/hts-specs/)
- [SAM/BAM and BAI specification](https://samtools.github.io/hts-specs/SAMv1.pdf)
- [SAM optional tags specification](https://samtools.github.io/hts-specs/SAMtags.pdf)
- [CRAM 3 specification](https://samtools.github.io/hts-specs/CRAMv3.pdf)
- [VCF 4.5 specification](https://samtools.github.io/hts-specs/VCFv4.5.pdf)
- [BCF 2 quick reference](https://samtools.github.io/hts-specs/BCFv2_qref.pdf)
- [Tabix index specification](https://samtools.github.io/hts-specs/tabix.pdf)
- [CSI specification](https://samtools.github.io/hts-specs/CSIv1.pdf)
- [BED 1 specification](https://samtools.github.io/hts-specs/BEDv1.pdf)

Use format specifications for coordinate fields, flags, tags, header
semantics, binary encodings, and index limits. Use pysam documentation for how
those concepts are translated into Python properties.

## Research Queries Used for This Refresh

Parallel web search/extract was used for:

- current stable pysam version, date, Python range, and wheel platforms
- recent 0.22–0.24 release changes and deprecations
- current AlignmentFile, pileup, VariantFile, FASTA/FASTQ, and Tabix APIs
- current coordinate, iterator, thread-safety, and pileup FAQ guidance
- HTSlib CRAM reference behavior and canonical format specifications

Context7 cross-checked the upstream source documentation for:

- pysam 0.24 release/CRAM behavior
- AlignmentFile signatures and defaults
- VariantFile, FastaFile, FastxFile, and TabixFile APIs

No generated research JSON is part of this skill.

## Refresh Checklist

When updating:

1. Check PyPI for the newest published pysam.
2. Read all release notes since the pinned version.
3. Record the embedded HTSlib/samtools/bcftools version.
4. Verify supported Python versions and wheel platforms.
5. Re-check CRAM defaults and reference lookup.
6. Compare API signatures in `api.html` and the tagged source.
7. Run bundled scripts against the new version.
8. Re-run Agent Skills validation and the security scanner.

### `references/variant_files.md`

# Variant Files: VCF and BCF

This reference targets pysam 0.24.0. Numeric pysam coordinates are 0-based,
half-open even though VCF text uses a 1-based `POS`.

## Open and Iterate

`VariantFile` auto-detects VCF, BGZF-compressed VCF, and BCF input:

```python
import pysam

with pysam.VariantFile("cohort.vcf.gz", threads=4) as variants:
    for record in variants:
        print(record.contig, record.pos, record.ref, record.alts)
```

Common modes:

- `r`: VCF input
- `rb`: BCF input; input auto-detection usually makes an explicit mode
  unnecessary
- `w`: VCF output; a `.vcf.gz` suffix selects BGZF-compressed VCF
- `wb`: compressed BCF output
- `wbu` / `wb0`: uncompressed BCF output

Writing requires a `VariantHeader`.

Useful constructor options:

- `index_filename=` for a nonstandard or remote index
- `drop_samples=True` to skip sample data
- `threads=` for compression/decompression
- `ignore_truncation=True` for missing BGZF EOF markers; not compatible with
  `threads > 1`

## Coordinates and Region Queries

```python
with pysam.VariantFile("cohort.vcf.gz") as variants:
    # Numeric coordinates: [999_999, 2_000_000)
    numeric = variants.fetch("chr1", 999_999, 2_000_000)

    # Region string: 1-based inclusive
    text = variants.fetch(region="chr1:1000000-2000000")
```

`VariantFile.fetch()` explicitly defines numeric `start`/`stop` as 0-based,
half-open. Region strings follow samtools notation.

For each `VariantRecord`:

- `contig` / `chrom`: contig name
- `pos`: 1-based VCF position
- `start`: 0-based inclusive position
- `stop`: 0-based exclusive record end
- `rlen`: reference span

Do not subtract one from a numeric `start` passed to `fetch()`. Use
`record.start` when integrating with BAM, BED, or FASTA APIs.

Random access requires:

- BGZF VCF: `.tbi` or `.csi`
- BCF: `.csi`

An unindexed VCF.gz or BCF can still be read sequentially with normal
iteration. `fetch()` with no region is index-driven; use `for record in
variants` for a true sequential pass.

For simultaneous iterators, `VariantFile.fetch()` uses `reopen=True`:

```python
first = variants.fetch("chr1", reopen=True)
second = variants.fetch("chr2", reopen=True)
```

## Header Model

```python
with pysam.VariantFile("cohort.vcf.gz") as variants:
    header = variants.header
    print(list(header.samples))

    for name, contig in header.contigs.items():
        print(name, contig.length)

    for name, field in header.info.items():
        print(name, field.number, field.type, field.description)
```

Important collections:

- `header.contigs`
- `header.samples`
- `header.filters`
- `header.info`
- `header.formats`
- `header.records`

INFO and FORMAT values can only be interpreted safely when their definitions
exist in the header. Do not infer missing Number/Type metadata.

## Record Fields

```python
for record in variants:
    alleles = record.alleles       # (REF, ALT1, ALT2, ...)
    alt_alleles = record.alts      # tuple or None
    identifier = record.id         # string or None
    quality = record.qual          # float or None
    filters = tuple(record.filter.keys())
```

`record.alleles_variant_types` classifies alleles with values such as `REF`,
`SNP`, `MNP`, `INDEL`, `BND`, `OVERLAP`, and `OTHER`.

Handle non-simple alleles:

- multiallelic records can have several ALT alleles
- symbolic alleles include `<DEL>`, `<DUP>`, `<INS>`, and others
- breakends use bracket notation
- spanning deletion uses `*`
- gVCF records often use `<NON_REF>` or `<*>`

Do not apply single-nucleotide logic to every record.

## INFO Fields

```python
for record in variants:
    depth = record.info.get("DP")
    frequencies = record.info.get("AF")
    if frequencies is not None:
        for allele_index, frequency in enumerate(frequencies, start=1):
            alt = record.alleles[allele_index]
            print(alt, frequency)
```

Number semantics matter:

- `1`: one value
- `A`: one value per ALT allele
- `R`: one value per REF+ALT allele
- `G`: one value per genotype
- `.`: variable number

Flag fields are represented as booleans. Missing values may be `None`, a tuple
containing `None`, or absent from the mapping depending on the field.

## FILTER Semantics

```python
filters = tuple(record.filter.keys())

if "PASS" in filters:
    status = "pass"
elif not filters:
    status = "unfiltered"  # VCF '.'
else:
    status = "failed"
```

`PASS`, an empty filter set (`.`), and a failed filter are distinct states. Do
not treat `.` as equivalent to `PASS` without an explicit policy.

## Sample and Genotype Data

```python
for sample_name, call in record.samples.items():
    genotype = call.get("GT")
    depth = call.get("DP")
    genotype_quality = call.get("GQ")
    phased = call.phased
    allele_strings = call.alleles
```

Genotype allele integers index `record.alleles`:

- `0`: REF
- `1`: first ALT
- `2`: second ALT
- `None`: missing allele

Do not assume diploidy:

```python
def called_alleles(genotype):
    if genotype is None:
        return ()
    return tuple(allele for allele in genotype if allele is not None)


called = called_alleles(record.samples["sample_A"].get("GT"))
alternate_count = sum(allele > 0 for allele in called)
```

`call.phased` records separator semantics but the Python GT remains a tuple.

## Efficient Sample Subsetting

Call `subset_samples()` before retrieving any record:

```python
samples = ["sample_A", "sample_B"]

with pysam.VariantFile("cohort.bcf") as source:
    source.subset_samples(samples)
    output_header = source.header.copy()

    with pysam.VariantFile(
        "subset.bcf", "wb", header=output_header, threads=4
    ) as destination:
        for record in source:
            destination.write(record)
```

This reduces decoding and memory. Do not copy a header, clear its sample
collection, and manually reconstruct records; that approach is error-prone.
Validate that every requested sample is present before subsetting.

## Writing Unchanged Records

When the destination uses the input header:

```python
with pysam.VariantFile("input.vcf.gz") as source, pysam.VariantFile(
    "passing.vcf.gz",
    "w",
    header=source.header,
    threads=4,
) as destination:
    for record in source:
        if "PASS" in record.filter:
            destination.write(record)
```

Write to a new file. Reopen and validate it before replacing any source.

## Safely Add Header Fields

Records are tied to their originating header. When the destination header is
changed, copy and translate records:

```python
with pysam.VariantFile("input.vcf.gz") as source:
    output_header = source.header.copy()
    output_header.info.add(
        "BAM_DP",
        number=1,
        type="Integer",
        description="Aligned base depth from the selected BAM and filters",
    )

    with pysam.VariantFile(
        "annotated.vcf.gz", "w", header=output_header
    ) as destination:
        for input_record in source:
            record = input_record.copy()
            record.translate(output_header)
            record.info["BAM_DP"] = 27
            destination.write(record)
```

Declare INFO, FORMAT, FILTER, and contig metadata before assigning values. Use
distinct field names when the new value has semantics different from an
existing field.

## Construct New Records

```python
header = pysam.VariantHeader()
header.add_meta("fileformat", value="VCFv4.5")
header.contigs.add("chr1", length=248_956_422)
header.info.add(
    "DP",
    number=1,
    type="Integer",
    description="Total depth",
)
header.formats.add(
    "GT",
    number=1,
    type="String",
    description="Genotype",
)
header.add_sample("sample_A")

with pysam.VariantFile("new.vcf.gz", "w", header=header) as output:
    record = output.header.new_record(
        contig="chr1",
        start=99_999,
        stop=100_000,
        alleles=("A", "G"),
        id="example",
        qual=60,
    )
    record.filter.add("PASS")
    record.info["DP"] = 40
    record.samples["sample_A"]["GT"] = (0, 1)
    output.write(record)
```

`start`/`stop` here are numeric Python coordinates. `start=99_999` writes VCF
`POS=100000`.

## Filtering Patterns

Make missing-value policy explicit:

```python
def passes(record, *, min_qual=30.0, min_dp=10) -> bool:
    if record.qual is None or record.qual < min_qual:
        return False
    depth = record.info.get("DP")
    if depth is None or depth < min_dp:
        return False
    return "PASS" in record.filter
```

For ALT-frequency filtering:

```python
frequencies = record.info.get("AF")
keep = (
    frequencies is not None
    and any(value is not None and value >= 0.01 for value in frequencies)
)
```

For genotype predicates, ignore missing alleles and preserve ploidy:

```python
gt = record.samples["sample_A"].get("GT")
has_alt = gt is not None and any(
    allele is not None and allele > 0 for allele in gt
)
```

## Compression and Indexing

Plain VCF must be coordinate sorted before compression/indexing:

```python
import pysam

pysam.tabix_compress("sorted.vcf", "sorted.vcf.gz")
pysam.tabix_index("sorted.vcf.gz", preset="vcf")
```

The last call creates TBI. To choose CSI instead, compress first and then use
bcftools indexing:

```python
import pysam.bcftools

pysam.bcftools.index("--csi", "sorted.vcf.gz", catch_stdout=False)
```

Do not use ordinary gzip for a random-access VCF. BGZF permits blocked random
access.

`tabix_index()` can automatically compress an uncompressed input and delete
the original unless `keep_original=True`; the explicit two-step pattern above
is safer. Do not use `force=True` unless overwrite is intended.

For BCF:

```python
pysam.bcftools.index("--csi", "cohort.bcf", catch_stdout=False)
```

Use CSI when contigs may exceed the legacy TBI coordinate limit. Read
`coordinates_and_indexing.md` for index selection.

## Header Translation Across Inputs

Do not merge VCFs by grouping Python records and appending sample calls. Inputs
can differ in contig order, INFO/FORMAT definitions, normalization, and allele
representation. Prefer `bcftools merge`, `bcftools concat`, or a dedicated
variant-merging tool after normalization and header reconciliation.

`record.translate(destination_header)` remaps header dictionaries but does not
normalize alleles, split multiallelic records, or resolve conflicting metadata.

## Validation Checklist

- Reopen the written file with `VariantFile`.
- Confirm contig order and sample order.
- Confirm each assigned INFO/FORMAT/FILTER field is declared with correct
  Number and Type.
- Check missing, haploid, polyploid, multiallelic, symbolic, and filtered
  records.
- Index the final coordinate-sorted output and fetch known edge intervals.
- Use bcftools validation/normalization commands when format-level guarantees
  are required.

### `scripts/alignment_qc.py`

```python
#!/usr/bin/env python3
"""Stream a local SAM/BAM/CRAM file and write aggregate QC counts as JSON.

Counts are alignment-record counts, not unique templates. A whole-file scan
uses fetch(until_eof=True) and needs no index. --region is a 1-based inclusive
samtools region string and requires an index. CRAM requires --reference.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterator, Optional

import pysam


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="local SAM/BAM/CRAM file")
    parser.add_argument(
        "--reference",
        type=Path,
        help="local indexed reference FASTA; required for CRAM",
    )
    parser.add_argument(
        "--index",
        type=Path,
        help="explicit local BAI/CSI/CRAI index",
    )
    parser.add_argument(
        "--region",
        help="1-based inclusive samtools region, for example chr1:1-1000000",
    )
    parser.add_argument(
        "--threads",
        type=positive_int,
        default=1,
        help="HTSlib decompression threads",
    )
    parser.add_argument(
        "--max-records",
        type=nonnegative_int,
        default=0,
        help="stop after this many records; 0 scans the complete selection",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write JSON to a new file instead of stdout; refuses overwrite",
    )
    return parser


def require_local_file(path: Path, label: str) -> Path:
    resolved = path.expanduser()
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{label} is not a regular file: {resolved}")
    return resolved


def alignment_mode(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".sam"):
        return "r"
    if name.endswith(".cram"):
        return "rc"
    if name.endswith(".bam"):
        return "rb"
    raise ValueError("input suffix must be .sam, .bam, or .cram")


def ratio(numerator: int, denominator: int) -> Optional[float]:
    return numerator / denominator if denominator else None


def average(total: int, count: int) -> Optional[float]:
    return total / count if count else None


def selected_reads(
    alignments: pysam.AlignmentFile,
    region: Optional[str],
) -> Iterator[pysam.AlignedSegment]:
    if region is None:
        return alignments.fetch(until_eof=True)
    return alignments.fetch(region=region)


def empty_counts() -> dict[str, int]:
    return {
        "total_records": 0,
        "primary_records": 0,
        "mapped_records": 0,
        "unmapped_records": 0,
        "secondary_records": 0,
        "supplementary_records": 0,
        "duplicate_records": 0,
        "qc_fail_records": 0,
        "paired_records": 0,
        "proper_pair_records": 0,
        "read1_records": 0,
        "read2_records": 0,
        "reverse_records": 0,
        "mate_unmapped_records": 0,
        "cigar_missing_records": 0,
        "sequence_missing_records": 0,
        "mapq_255_records": 0,
    }


def inspect_alignments(args: argparse.Namespace) -> dict[str, Any]:
    path = require_local_file(args.input, "input")
    reference = (
        require_local_file(args.reference, "reference")
        if args.reference is not None
        else None
    )
    index = (
        require_local_file(args.index, "index")
        if args.index is not None
        else None
    )
    mode = alignment_mode(path)

    if mode == "rc" and reference is None:
        raise ValueError("CRAM QC requires --reference")

    kwargs: dict[str, Any] = {
        "threads": args.threads,
        "require_index": args.region is not None,
    }
    if reference is not None:
        kwargs["reference_filename"] = str(reference)
    if index is not None:
        kwargs["index_filename"] = str(index)

    counts = empty_counts()
    query_length_sum = 0
    query_length_count = 0
    aligned_query_bases = 0
    mapq_sum = 0
    mapq_count = 0
    record_limit_reached = False

    with pysam.AlignmentFile(str(path), mode, **kwargs) as alignments:
        header = alignments.header.to_dict()
        for read in selected_reads(alignments, args.region):
            if args.max_records and counts["total_records"] >= args.max_records:
                record_limit_reached = True
                break

            counts["total_records"] += 1

            is_primary = not read.is_secondary and not read.is_supplementary
            if is_primary:
                counts["primary_records"] += 1
            if read.is_unmapped:
                counts["unmapped_records"] += 1
            else:
                counts["mapped_records"] += 1
                if read.mapping_quality == 255:
                    counts["mapq_255_records"] += 1
                else:
                    mapq_sum += int(read.mapping_quality)
                    mapq_count += 1
            if read.is_secondary:
                counts["secondary_records"] += 1
            if read.is_supplementary:
                counts["supplementary_records"] += 1
            if read.is_duplicate:
                counts["duplicate_records"] += 1
            if read.is_qcfail:
                counts["qc_fail_records"] += 1
            if read.is_paired:
                counts["paired_records"] += 1
            if read.is_proper_pair:
                counts["proper_pair_records"] += 1
            if read.is_read1:
                counts["read1_records"] += 1
            if read.is_read2:
                counts["read2_records"] += 1
            if read.is_reverse:
                counts["reverse_records"] += 1
            if read.mate_is_unmapped:
                counts["mate_unmapped_records"] += 1
            if read.cigartuples is None:
                counts["cigar_missing_records"] += 1
            if read.query_sequence is None:
                counts["sequence_missing_records"] += 1

            if read.query_length is not None:
                query_length_sum += int(read.query_length)
                query_length_count += 1
            if read.query_alignment_length is not None:
                aligned_query_bases += int(read.query_alignment_length)

        try:
            has_index = bool(alignments.has_index())
        except (AttributeError, OSError, ValueError):
            has_index = False

        report = {
            "schema_version": "1.0",
            "pysam_version": pysam.__version__,
            "samtools_version": getattr(
                pysam, "__samtools_version__", None
            ),
            "file_name": path.name,
            "format": (
                "CRAM"
                if alignments.is_cram
                else "BAM"
                if alignments.is_bam
                else "SAM"
            ),
            "sort_order": header.get("HD", {}).get("SO"),
            "has_index": has_index,
            "selection": {
                "region": args.region,
                "region_coordinate_system": (
                    "1-based inclusive samtools string"
                    if args.region is not None
                    else None
                ),
                "whole_file_order": args.region is None,
                "max_records": args.max_records,
                "record_limit_reached": record_limit_reached,
            },
            "semantics": (
                "Counts are alignment records, not unique query names, "
                "templates, or fragments. MAPQ 255 is reported as unavailable "
                "and excluded from mean_mapping_quality."
            ),
            "counts": counts,
            "derived": {
                "mapping_rate_all_records": ratio(
                    counts["mapped_records"],
                    counts["total_records"],
                ),
                "duplicate_rate_all_records": ratio(
                    counts["duplicate_records"],
                    counts["total_records"],
                ),
                "proper_pair_rate_paired_records": ratio(
                    counts["proper_pair_records"],
                    counts["paired_records"],
                ),
                "mean_query_length": average(
                    query_length_sum,
                    query_length_count,
                ),
                "mean_mapping_quality": average(mapq_sum, mapq_count),
                "aligned_query_bases": aligned_query_bases,
            },
        }
    return report


def write_report(report: dict[str, Any], output: Optional[Path]) -> None:
    text = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )
    if output is None:
        sys.stdout.write(text + "\n")
        return

    destination = output.expanduser()
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(text + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.output is not None:
        try:
            if args.output.expanduser().resolve() == args.input.expanduser().resolve():
                parser.error("--output must not overwrite the input file")
        except OSError:
            pass

    try:
        report = inspect_alignments(args)
        write_report(report, args.output)
    except (
        FileExistsError,
        FileNotFoundError,
        IndexError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        print(f"alignment_qc: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/filter_alignments.py`

```python
#!/usr/bin/env python3
"""Filter a local SAM/BAM/CRAM into a new alignment file.

The script preserves record order and the input header; it does not sort.
Whole-file iteration includes unplaced unmapped records and needs no index.
--region is a 1-based inclusive samtools region and requires an input index.
CRAM input or output requires --reference. Existing outputs are never replaced.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Optional

import pysam


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="local SAM/BAM/CRAM input")
    parser.add_argument("output", type=Path, help="new SAM/BAM/CRAM output")
    parser.add_argument(
        "--reference",
        type=Path,
        help="local indexed reference FASTA; required for CRAM",
    )
    parser.add_argument(
        "--input-index",
        type=Path,
        help="explicit local BAI/CSI/CRAI input index",
    )
    parser.add_argument(
        "--region",
        help="1-based inclusive samtools region, for example chr1:1-1000000",
    )
    parser.add_argument(
        "--min-mapq",
        type=nonnegative_int,
        default=0,
        help="minimum mapping quality; MAPQ 255 passes this numeric threshold",
    )
    parser.add_argument(
        "--exclude-unmapped",
        action="store_true",
        help="exclude unmapped records",
    )
    parser.add_argument(
        "--exclude-secondary",
        action="store_true",
        help="exclude secondary alignments",
    )
    parser.add_argument(
        "--exclude-supplementary",
        action="store_true",
        help="exclude supplementary alignments",
    )
    parser.add_argument(
        "--exclude-duplicates",
        action="store_true",
        help="exclude records marked duplicate",
    )
    parser.add_argument(
        "--exclude-qcfail",
        action="store_true",
        help="exclude records marked QC fail",
    )
    parser.add_argument(
        "--proper-pairs-only",
        action="store_true",
        help="keep only records marked as proper paired alignments",
    )
    parser.add_argument(
        "--threads",
        type=positive_int,
        default=1,
        help="HTSlib compression/decompression threads",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="index output; requires coordinate sort order and BAM/CRAM",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="write JSON summary to a new file instead of stdout",
    )
    return parser


def require_local_file(path: Path, label: str) -> Path:
    resolved = path.expanduser()
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{label} is not a regular file: {resolved}")
    return resolved


def alignment_mode(path: Path, *, writing: bool) -> str:
    name = path.name.lower()
    if name.endswith(".sam"):
        return "w" if writing else "r"
    if name.endswith(".bam"):
        return "wb" if writing else "rb"
    if name.endswith(".cram"):
        return "wc" if writing else "rc"
    raise ValueError("alignment suffix must be .sam, .bam, or .cram")


def selected_reads(
    alignments: pysam.AlignmentFile,
    region: Optional[str],
) -> Iterator[pysam.AlignedSegment]:
    if region is None:
        return alignments.fetch(until_eof=True)
    return alignments.fetch(region=region)


def exclusion_reasons(
    read: pysam.AlignedSegment,
    args: argparse.Namespace,
) -> list[str]:
    reasons = []
    if args.exclude_unmapped and read.is_unmapped:
        reasons.append("unmapped")
    if args.exclude_secondary and read.is_secondary:
        reasons.append("secondary")
    if args.exclude_supplementary and read.is_supplementary:
        reasons.append("supplementary")
    if args.exclude_duplicates and read.is_duplicate:
        reasons.append("duplicate")
    if args.exclude_qcfail and read.is_qcfail:
        reasons.append("qc_fail")
    if args.proper_pairs_only and not read.is_proper_pair:
        reasons.append("not_proper_pair")
    if read.mapping_quality < args.min_mapq:
        reasons.append("mapq_below_threshold")
    return reasons


def validate_destinations(
    input_path: Path,
    output_path: Path,
    summary_path: Optional[Path],
) -> None:
    if not output_path.parent.exists():
        raise FileNotFoundError(
            f"output parent does not exist: {output_path.parent}"
        )
    if output_path.exists():
        raise FileExistsError(f"output already exists: {output_path}")
    if input_path.resolve() == output_path.resolve():
        raise ValueError("output must not be the input file")

    if summary_path is not None:
        if not summary_path.parent.exists():
            raise FileNotFoundError(
                f"summary parent does not exist: {summary_path.parent}"
            )
        if summary_path.exists():
            raise FileExistsError(
                f"summary output already exists: {summary_path}"
            )
        if summary_path.resolve() in {
            input_path.resolve(),
            output_path.resolve(),
        }:
            raise ValueError("summary path must differ from input and output")


def filter_file(args: argparse.Namespace) -> dict[str, Any]:
    input_path = require_local_file(args.input, "input")
    output_path = args.output.expanduser()
    summary_path = (
        args.summary.expanduser() if args.summary is not None else None
    )
    validate_destinations(input_path, output_path, summary_path)

    reference = (
        require_local_file(args.reference, "reference")
        if args.reference is not None
        else None
    )
    input_index = (
        require_local_file(args.input_index, "input index")
        if args.input_index is not None
        else None
    )
    input_mode = alignment_mode(input_path, writing=False)
    output_mode = alignment_mode(output_path, writing=True)

    if (input_mode == "rc" or output_mode == "wc") and reference is None:
        raise ValueError("CRAM input or output requires --reference")
    if args.index and output_mode == "w":
        raise ValueError("SAM output cannot be indexed")

    input_kwargs: dict[str, Any] = {
        "threads": args.threads,
        "require_index": args.region is not None,
    }
    if reference is not None:
        input_kwargs["reference_filename"] = str(reference)
    if input_index is not None:
        input_kwargs["index_filename"] = str(input_index)

    output_kwargs: dict[str, Any] = {"threads": args.threads}
    if reference is not None:
        output_kwargs["reference_filename"] = str(reference)

    reason_counts: Counter[str] = Counter()
    selected = 0
    written = 0
    excluded = 0
    sort_order: Optional[str] = None

    try:
        with pysam.AlignmentFile(
            str(input_path),
            input_mode,
            **input_kwargs,
        ) as source:
            sort_order = source.header.to_dict().get("HD", {}).get("SO")
            if args.index and sort_order != "coordinate":
                raise ValueError(
                    "--index requires input header sort order 'coordinate'; "
                    "this script preserves order but does not sort"
                )

            with pysam.AlignmentFile(
                str(output_path),
                output_mode,
                template=source,
                **output_kwargs,
            ) as destination:
                for read in selected_reads(source, args.region):
                    selected += 1
                    reasons = exclusion_reasons(read, args)
                    if reasons:
                        excluded += 1
                        reason_counts.update(reasons)
                        continue
                    destination.write(read)
                    written += 1
    except Exception:
        if output_path.exists():
            output_path.unlink()
        raise

    if args.index:
        pysam.samtools.index(
            "-@",
            str(args.threads),
            str(output_path),
            catch_stdout=False,
        )

    return {
        "schema_version": "1.0",
        "pysam_version": pysam.__version__,
        "samtools_version": getattr(pysam, "__samtools_version__", None),
        "input_file_name": input_path.name,
        "output_file_name": output_path.name,
        "input_mode": input_mode,
        "output_mode": output_mode,
        "sort_order_preserved": sort_order,
        "selection": {
            "region": args.region,
            "region_coordinate_system": (
                "1-based inclusive samtools string"
                if args.region is not None
                else None
            ),
        },
        "filters": {
            "min_mapq": args.min_mapq,
            "exclude_unmapped": args.exclude_unmapped,
            "exclude_secondary": args.exclude_secondary,
            "exclude_supplementary": args.exclude_supplementary,
            "exclude_duplicates": args.exclude_duplicates,
            "exclude_qcfail": args.exclude_qcfail,
            "proper_pairs_only": args.proper_pairs_only,
        },
        "counts": {
            "selected_records": selected,
            "written_records": written,
            "excluded_records": excluded,
            "exclusion_reasons": dict(sorted(reason_counts.items())),
        },
        "indexed_output": args.index,
        "semantics": (
            "Exclusion reason counts can exceed excluded_records because one "
            "record can fail multiple filters. Counts are alignment records."
        ),
    }


def write_summary(
    report: dict[str, Any],
    output: Optional[Path],
) -> None:
    text = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )
    if output is None:
        sys.stdout.write(text + "\n")
        return
    with output.expanduser().open("x", encoding="utf-8") as handle:
        handle.write(text + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report = filter_file(args)
        write_summary(report, args.summary)
    except (
        FileExistsError,
        FileNotFoundError,
        IndexError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        pysam.SamtoolsError,
    ) as error:
        print(f"filter_alignments: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/inspect_hts.py`

```python
#!/usr/bin/env python3
"""Inspect a local HTS/sequence file and emit a bounded JSON summary.

The default report reads headers and index metadata only. It does not emit
alignment query names, FASTX record names, VCF sample names, or full headers.
CRAM requires an explicit local --reference to avoid hidden reference lookup.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

import pysam


KINDS = ("alignment", "variant", "fasta", "fastx", "tabix")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def detect_kind(path: Path) -> str:
    name = path.name.lower()

    if name.endswith((".bam", ".sam", ".cram")):
        return "alignment"
    if name.endswith((".vcf", ".vcf.gz", ".vcf.bgz", ".bcf")):
        return "variant"
    if name.endswith(
        (
            ".fa",
            ".fasta",
            ".fna",
            ".fas",
            ".fa.gz",
            ".fasta.gz",
            ".fna.gz",
            ".fas.gz",
        )
    ):
        return "fasta"
    if name.endswith(
        (
            ".fq",
            ".fastq",
            ".fq.gz",
            ".fastq.gz",
            ".fq.bgz",
            ".fastq.bgz",
        )
    ):
        return "fastx"
    if name.endswith(
        (
            ".bed.gz",
            ".bed.bgz",
            ".gff.gz",
            ".gff3.gz",
            ".gtf.gz",
            ".tsv.gz",
            ".tab.gz",
        )
    ):
        return "tabix"

    raise ValueError(
        "could not infer file kind from suffix; pass --kind "
        + ", ".join(KINDS)
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="local genomic data file")
    parser.add_argument(
        "--kind",
        choices=("auto",) + KINDS,
        default="auto",
        help="file interface to use",
    )
    parser.add_argument(
        "--reference",
        type=Path,
        help="local indexed reference FASTA; required for CRAM",
    )
    parser.add_argument(
        "--index",
        type=Path,
        help="explicit local BAI/CSI/CRAI/TBI/FAI index",
    )
    parser.add_argument(
        "--threads",
        type=positive_int,
        default=1,
        help="HTSlib decompression threads",
    )
    parser.add_argument(
        "--max-items",
        type=nonnegative_int,
        default=100,
        help="maximum contigs and metadata keys to include; 0 includes all",
    )
    parser.add_argument(
        "--include-identifiers",
        action="store_true",
        help="include VCF sample names and alignment read-group IDs",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write JSON to a new file instead of stdout; refuses overwrite",
    )
    return parser


def require_local_file(path: Path, label: str) -> Path:
    resolved = path.expanduser()
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{label} is not a regular file: {resolved}")
    return resolved


def limited(values: list[Any], maximum: int) -> tuple[list[Any], bool]:
    if maximum == 0 or len(values) <= maximum:
        return values, False
    return values[:maximum], True


def contig_records(
    names: tuple[str, ...] | list[str],
    lengths: tuple[int, ...] | list[int],
    maximum: int,
) -> tuple[list[dict[str, Any]], bool]:
    records = [
        {"name": name, "length": int(length)}
        for name, length in zip(names, lengths)
    ]
    return limited(records, maximum)


def alignment_mode(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".sam"):
        return "r"
    if name.endswith(".cram"):
        return "rc"
    return "rb"


def inspect_alignment(
    path: Path,
    *,
    reference: Optional[Path],
    index: Optional[Path],
    threads: int,
    max_items: int,
    include_identifiers: bool,
) -> dict[str, Any]:
    if path.name.lower().endswith(".cram") and reference is None:
        raise ValueError("CRAM inspection requires --reference")

    kwargs: dict[str, Any] = {"threads": threads}
    if reference is not None:
        kwargs["reference_filename"] = str(reference)
    if index is not None:
        kwargs["index_filename"] = str(index)

    with pysam.AlignmentFile(
        str(path),
        alignment_mode(path),
        **kwargs,
    ) as alignments:
        contigs, contigs_truncated = contig_records(
            list(alignments.references),
            list(alignments.lengths),
            max_items,
        )
        header = alignments.header.to_dict()
        read_groups = header.get("RG", [])
        programs = header.get("PG", [])

        try:
            has_index = bool(alignments.has_index())
        except (AttributeError, OSError, ValueError):
            has_index = False

        report: dict[str, Any] = {
            "format": (
                "CRAM"
                if alignments.is_cram
                else "BAM"
                if alignments.is_bam
                else "SAM"
            ),
            "is_remote": bool(alignments.is_remote),
            "has_index": has_index,
            "sort_order": header.get("HD", {}).get("SO"),
            "reference_count": len(alignments.references),
            "contigs": contigs,
            "contigs_truncated": contigs_truncated,
            "read_group_count": len(read_groups),
            "program_record_count": len(programs),
            "comment_count": len(header.get("CO", [])),
        }

        if include_identifiers:
            read_group_ids = [
                group.get("ID")
                for group in read_groups
                if group.get("ID") is not None
            ]
            report["read_group_ids"], report["read_group_ids_truncated"] = (
                limited(read_group_ids, max_items)
            )

        if has_index:
            try:
                statistics = alignments.get_index_statistics()
                report["index_statistics"] = {
                    "mapped": sum(item.mapped for item in statistics),
                    "unmapped_with_coordinates": sum(
                        item.unmapped for item in statistics
                    ),
                    "no_coordinate": int(alignments.nocoordinate),
                }
            except (AttributeError, OSError, ValueError):
                report["index_statistics"] = None

        return report


def variant_index_loaded(variants: pysam.VariantFile) -> bool:
    try:
        return variants.index is not None
    except (AttributeError, OSError, ValueError):
        return False


def inspect_variant(
    path: Path,
    *,
    index: Optional[Path],
    threads: int,
    max_items: int,
    include_identifiers: bool,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"threads": threads}
    if index is not None:
        kwargs["index_filename"] = str(index)

    with pysam.VariantFile(str(path), **kwargs) as variants:
        header = variants.header
        contig_values = [
            {"name": name, "length": metadata.length}
            for name, metadata in header.contigs.items()
        ]
        contigs, contigs_truncated = limited(contig_values, max_items)
        info_keys, info_truncated = limited(list(header.info), max_items)
        format_keys, formats_truncated = limited(
            list(header.formats), max_items
        )
        filter_keys, filters_truncated = limited(
            list(header.filters), max_items
        )

        report: dict[str, Any] = {
            "format": (
                "BCF"
                if bool(getattr(variants, "is_bcf", False))
                else "VCF"
            ),
            "is_remote": bool(variants.is_remote),
            "has_index": variant_index_loaded(variants),
            "contig_count": len(header.contigs),
            "contigs": contigs,
            "contigs_truncated": contigs_truncated,
            "sample_count": len(header.samples),
            "info_keys": info_keys,
            "info_keys_truncated": info_truncated,
            "format_keys": format_keys,
            "format_keys_truncated": formats_truncated,
            "filter_keys": filter_keys,
            "filter_keys_truncated": filters_truncated,
        }
        if include_identifiers:
            sample_names, samples_truncated = limited(
                list(header.samples), max_items
            )
            report["sample_names"] = sample_names
            report["sample_names_truncated"] = samples_truncated
        return report


def inspect_fasta(
    path: Path,
    *,
    index: Optional[Path],
    max_items: int,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    if index is not None:
        kwargs["filepath_index"] = str(index)

    with pysam.FastaFile(str(path), **kwargs) as fasta:
        contigs, contigs_truncated = contig_records(
            list(fasta.references),
            list(fasta.lengths),
            max_items,
        )
        return {
            "format": "FASTA",
            "random_access": True,
            "reference_count": fasta.nreferences,
            "total_bases": sum(fasta.lengths),
            "contigs": contigs,
            "contigs_truncated": contigs_truncated,
        }


def inspect_fastx(path: Path) -> dict[str, Any]:
    with pysam.FastxFile(str(path), persist=False):
        return {
            "format": "FASTA/FASTQ",
            "random_access": False,
            "content_scanned": False,
            "note": (
                "FastxFile has no header index; use a streaming QC workflow "
                "to summarize records."
            ),
        }


def inspect_tabix(
    path: Path,
    *,
    index: Optional[Path],
    threads: int,
    max_items: int,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {"threads": threads}
    if index is not None:
        kwargs["index"] = str(index)

    with pysam.TabixFile(str(path), **kwargs) as table:
        contigs, contigs_truncated = limited(
            list(table.contigs), max_items
        )
        header_line_count = sum(1 for _ in table.header)
        return {
            "format": "TABIX",
            "has_index": True,
            "contig_count": len(table.contigs),
            "contigs": contigs,
            "contigs_truncated": contigs_truncated,
            "header_line_count": header_line_count,
        }


def inspect_file(args: argparse.Namespace) -> dict[str, Any]:
    path = require_local_file(args.input, "input")
    reference = (
        require_local_file(args.reference, "reference")
        if args.reference is not None
        else None
    )
    index = (
        require_local_file(args.index, "index")
        if args.index is not None
        else None
    )
    kind = detect_kind(path) if args.kind == "auto" else args.kind

    if kind == "alignment":
        details = inspect_alignment(
            path,
            reference=reference,
            index=index,
            threads=args.threads,
            max_items=args.max_items,
            include_identifiers=args.include_identifiers,
        )
    elif kind == "variant":
        details = inspect_variant(
            path,
            index=index,
            threads=args.threads,
            max_items=args.max_items,
            include_identifiers=args.include_identifiers,
        )
    elif kind == "fasta":
        details = inspect_fasta(
            path,
            index=index,
            max_items=args.max_items,
        )
    elif kind == "fastx":
        details = inspect_fastx(path)
    else:
        details = inspect_tabix(
            path,
            index=index,
            threads=args.threads,
            max_items=args.max_items,
        )

    return {
        "schema_version": "1.0",
        "pysam_version": pysam.__version__,
        "samtools_version": getattr(
            pysam, "__samtools_version__", None
        ),
        "file_name": path.name,
        "size_bytes": path.stat().st_size,
        "kind": kind,
        "identifiers_included": args.include_identifiers,
        "details": details,
    }


def write_report(report: dict[str, Any], output: Optional[Path]) -> None:
    text = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )
    if output is None:
        sys.stdout.write(text + "\n")
        return

    destination = output.expanduser()
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(text + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.output is not None:
        try:
            if args.output.expanduser().resolve() == args.input.expanduser().resolve():
                parser.error("--output must not overwrite the input file")
        except OSError:
            pass

    try:
        report = inspect_file(args)
        write_report(report, args.output)
    except (
        FileExistsError,
        FileNotFoundError,
        IndexError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        print(f"inspect_hts: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/variant_summary.py`

```python
#!/usr/bin/env python3
"""Stream a local VCF/BCF and emit variant/genotype summary counts as JSON.

Normal iteration scans in file order without an index. --region is a 1-based
inclusive samtools region string and requires TBI/CSI. Sample identifiers are
omitted unless --include-sample-names is supplied.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Optional

import pysam


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="local VCF/VCF.gz/BCF file")
    parser.add_argument(
        "--index",
        type=Path,
        help="explicit local TBI/CSI index",
    )
    parser.add_argument(
        "--region",
        help="1-based inclusive samtools region, for example chr1:1-1000000",
    )
    parser.add_argument(
        "--sample",
        action="append",
        default=[],
        help="sample to decode; repeat for multiple samples (default: all)",
    )
    parser.add_argument(
        "--include-sample-names",
        action="store_true",
        help="include decoded sample identifiers in the JSON report",
    )
    parser.add_argument(
        "--threads",
        type=positive_int,
        default=1,
        help="HTSlib decompression threads",
    )
    parser.add_argument(
        "--max-records",
        type=nonnegative_int,
        default=0,
        help="stop after this many records; 0 scans the complete selection",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write JSON to a new file instead of stdout; refuses overwrite",
    )
    return parser


def require_local_file(path: Path, label: str) -> Path:
    resolved = path.expanduser()
    if not resolved.exists():
        raise FileNotFoundError(f"{label} does not exist: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"{label} is not a regular file: {resolved}")
    return resolved


def variant_records(
    variants: pysam.VariantFile,
    region: Optional[str],
) -> Iterator[pysam.VariantRecord]:
    if region is None:
        return iter(variants)
    return variants.fetch(region=region)


def is_symbolic_or_breakend(allele: str) -> bool:
    return (
        allele == "*"
        or allele.startswith("<")
        or "[" in allele
        or "]" in allele
    )


def classify_record(record: pysam.VariantRecord) -> str:
    alts = record.alts or ()
    if not alts:
        return "no_alt"
    if any(is_symbolic_or_breakend(alt) for alt in alts):
        return "symbolic_or_breakend"
    if len(record.ref) == 1 and all(len(alt) == 1 for alt in alts):
        return "snv"
    if all(len(alt) == len(record.ref) for alt in alts):
        return "mnv"
    if any(len(alt) != len(record.ref) for alt in alts):
        return "indel_or_mixed"
    return "other"


def filter_status(record: pysam.VariantRecord) -> str:
    labels = tuple(record.filter.keys())
    if "PASS" in labels:
        return "pass"
    if not labels:
        return "unfiltered"
    return "failed"


def update_substitution_counts(
    record: pysam.VariantRecord,
    counts: Counter[str],
) -> None:
    alts = record.alts or ()
    if len(alts) != 1:
        return
    ref = record.ref.upper()
    alt = alts[0].upper()
    if ref not in "ACGT" or alt not in "ACGT" or len(ref) != 1 or len(alt) != 1:
        return

    pair = frozenset((ref, alt))
    if pair in (frozenset(("A", "G")), frozenset(("C", "T"))):
        counts["transitions"] += 1
    else:
        counts["transversions"] += 1


def update_genotype_counts(
    record: pysam.VariantRecord,
    counts: Counter[str],
    ploidy_counts: Counter[int],
) -> None:
    for call in record.samples.values():
        genotype = call.get("GT")
        counts["genotypes_seen"] += 1

        if genotype is None or all(allele is None for allele in genotype):
            counts["missing_genotypes"] += 1
            continue

        ploidy_counts[len(genotype)] += 1
        if any(allele is None for allele in genotype):
            counts["partially_missing_genotypes"] += 1
            continue

        called = tuple(int(allele) for allele in genotype)
        counts["called_genotypes"] += 1
        counts["called_alleles"] += len(called)
        counts["alternate_alleles"] += sum(
            allele > 0 for allele in called
        )
        if call.phased:
            counts["phased_called_genotypes"] += 1

        unique = set(called)
        if unique == {0}:
            counts["reference_only_genotypes"] += 1
        elif len(called) == 1:
            counts["haploid_alternate_genotypes"] += 1
        elif len(unique) == 1:
            counts["same_alternate_allele_genotypes"] += 1
        else:
            counts["mixed_allele_genotypes"] += 1


def summarize_variants(args: argparse.Namespace) -> dict[str, Any]:
    path = require_local_file(args.input, "input")
    index = (
        require_local_file(args.index, "index")
        if args.index is not None
        else None
    )

    kwargs: dict[str, Any] = {"threads": args.threads}
    if index is not None:
        kwargs["index_filename"] = str(index)

    record_counts: Counter[str] = Counter()
    filter_label_counts: Counter[str] = Counter()
    substitution_counts: Counter[str] = Counter()
    genotype_counts: Counter[str] = Counter()
    ploidy_counts: Counter[int] = Counter()
    quality_sum = 0.0
    quality_count = 0
    record_limit_reached = False

    with pysam.VariantFile(str(path), **kwargs) as variants:
        available_samples = list(variants.header.samples)
        if args.sample:
            missing = sorted(set(args.sample) - set(available_samples))
            if missing:
                raise ValueError(
                    "samples not present in header: " + ", ".join(missing)
                )
            variants.subset_samples(args.sample)

        decoded_samples = list(variants.header.samples)

        for record in variant_records(variants, args.region):
            if args.max_records and record_counts["total"] >= args.max_records:
                record_limit_reached = True
                break

            record_counts["total"] += 1
            record_counts[classify_record(record)] += 1
            record_counts[filter_status(record)] += 1

            alts = record.alts or ()
            if len(alts) == 1:
                record_counts["biallelic"] += 1
            elif len(alts) > 1:
                record_counts["multiallelic"] += 1

            if record.qual is None:
                record_counts["missing_quality"] += 1
            else:
                quality_sum += float(record.qual)
                quality_count += 1

            labels = tuple(record.filter.keys())
            if not labels:
                filter_label_counts["."] += 1
            else:
                filter_label_counts.update(labels)

            update_substitution_counts(record, substitution_counts)
            update_genotype_counts(
                record,
                genotype_counts,
                ploidy_counts,
            )

        try:
            has_index = variants.index is not None
        except (AttributeError, OSError, ValueError):
            has_index = False

        report: dict[str, Any] = {
            "schema_version": "1.0",
            "pysam_version": pysam.__version__,
            "samtools_version": getattr(
                pysam, "__samtools_version__", None
            ),
            "file_name": path.name,
            "format": (
                "BCF"
                if bool(getattr(variants, "is_bcf", False))
                else "VCF"
            ),
            "has_index": has_index,
            "selection": {
                "region": args.region,
                "region_coordinate_system": (
                    "1-based inclusive samtools string"
                    if args.region is not None
                    else None
                ),
                "max_records": args.max_records,
                "record_limit_reached": record_limit_reached,
                "available_sample_count": len(available_samples),
                "decoded_sample_count": len(decoded_samples),
            },
            "record_counts": dict(sorted(record_counts.items())),
            "filter_label_counts": dict(
                sorted(filter_label_counts.items())
            ),
            "substitution_counts": dict(
                sorted(substitution_counts.items())
            ),
            "quality": {
                "records_with_quality": quality_count,
                "mean_quality": (
                    quality_sum / quality_count
                    if quality_count
                    else None
                ),
            },
            "genotypes": dict(sorted(genotype_counts.items())),
            "observed_genotype_ploidy_counts": {
                str(ploidy): count
                for ploidy, count in sorted(ploidy_counts.items())
            },
            "semantics": (
                "PASS, unfiltered '.', and failed FILTER states are distinct. "
                "Record classes are mutually exclusive; indel_or_mixed can "
                "include multiallelic records with mixed allele lengths."
            ),
        }
        if args.include_sample_names:
            report["selection"]["decoded_samples"] = decoded_samples
        return report


def write_report(report: dict[str, Any], output: Optional[Path]) -> None:
    text = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    )
    if output is None:
        sys.stdout.write(text + "\n")
        return

    destination = output.expanduser()
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(text + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.output is not None:
        try:
            if args.output.expanduser().resolve() == args.input.expanduser().resolve():
                parser.error("--output must not overwrite the input file")
        except OSError:
            pass

    try:
        report = summarize_variants(args)
        write_report(report, args.output)
    except (
        FileExistsError,
        FileNotFoundError,
        IndexError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
    ) as error:
        print(f"variant_summary: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
