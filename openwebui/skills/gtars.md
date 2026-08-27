---
name: gtars
description: Use Gtars for local genomic interval models and set algebra, overlaps and counts, consensus and coverage, tokenization, fragment processing, and refget/BEDbase planning across Python, Rust, and the CLI.
---

# Gtars

Gtars provides native Rust implementations, Python bindings, and a feature-gated
`gtars` binary for genomic interval and reference-sequence work. Start with the
bundled local inspectors; call upstream code only after the data contract,
provenance, resource bounds, and side effects are explicit.

## Verified snapshot (2026-07-23)

- Python: [`gtars==0.9.2`](https://pypi.org/project/gtars/), released
  2026-06-17, `Requires-Python >=3.10`.
- Rust meta-crate: [`gtars=0.9.0`](https://crates.io/crates/gtars), released
  2026-06-15. Its default feature set is empty.
- CLI crate/binary: [`gtars-cli=0.9.0`](https://crates.io/crates/gtars-cli);
  the installed binary is named `gtars`.
- Direct refget crate: [`gtars-refget=0.9.1`](https://crates.io/crates/gtars-refget),
  released 2026-06-17. `gtars=0.9.0` itself pins its component release set, which
  includes refget 0.9.0.
- Upstream intentionally versions workspace crates, Python bindings, and CLI
  independently. Do not assume matching numbers mean matching artifacts.
- The published docs changelog stops at 0.5.1. API examples here were checked
  against the 0.9.2 Python stubs/runtime and the `v0.9.0` CLI/Rust source.

The `license: MIT` field covers this skill. Published `gtars` crates declare MIT,
while the GitHub repository currently displays BSD-2-Clause at the root; verify
the exact artifact's license before redistribution.

## Native-code trust gate and exact pins

The Python wheel contains a PyO3 native extension. Cargo installation compiles a
native binary and can run dependency build scripts. Treat either path as code
execution:

1. Confirm the official PyPI/crates.io/GitHub owner and immutable version.
2. Review filenames, platform tags, release provenance, license, and SHA-256.
   GitHub's v0.9.0 binary release includes per-archive `.sha256` sidecars.
3. Never run an untrusted prebuilt binary, wheel, source tree, Cargo build script,
   or archive installer. Use isolation and CPU/RAM/disk/time limits.
4. Keep a lockfile and artifact hashes with the analysis manifest.

After that review, create an isolated Python environment:

```bash
uv venv --python 3.11 .venv-gtars
uv pip install --dry-run --python .venv-gtars/bin/python "gtars==0.9.2"
uv pip install --python .venv-gtars/bin/python "gtars==0.9.2"
.venv-gtars/bin/python -c \
  "import gtars; assert gtars.__version__ == '0.9.2'; print(gtars.__version__)"
```

For the reviewed CLI source release:

```bash
cargo install gtars-cli --version 0.9.0 --locked
gtars --version
gtars --help
```

For a Rust project, pin the wrapper exactly and enable only required features:

```toml
[dependencies]
gtars = { version = "=0.9.0", default-features = false, features = [
  "core", "overlaprs", "uniwig", "tokenizers", "refget"
] }
```

Use `gtars-refget = "=0.9.1"` directly only when the newer direct component API is
required and compatibility has been tested. Do not replace these pins with a Git
branch or an unreviewed release.

## Genomic data contract

Apply this contract before every operation:

1. **Coordinates:** BED intervals are 0-based and half-open: `[start, end)`.
   Require `0 <= start < end <= contig_length`. Gtars coordinates are `u32`, so
   reject values above `4,294,967,295`.
2. **Assembly:** record an assembly accession/version and the SHA-256 of the exact
   chromosome-sizes or refget sequence-collection metadata. Never infer assembly
   from filenames or `chr` prefixes.
3. **Contigs:** compare names exactly. `1` and `chr1`, alternate loci, decoys, and
   mitochondrial aliases are not interchangeable. Rename or liftover only as a
   separately reviewed transformation.
4. **Sorting:** preserve the original file, then sort a copy by chromosome-sizes
   order and numeric start/end when the operation requires it. Python
   `RegionSet(path)` currently sorts lexicographically by contig and start while
   loading; do not rely on original row order afterward.
5. **Strand:** BED6 uses `+`, `-`, or `.`. `Region.rest` retains trailing BED
   fields, but a file-backed Python `RegionSet` currently initializes its separate
   `strands` vector to `*`. Several set operations drop strand. Preserve and
   validate strand externally when it is scientifically meaningful.
6. **Duplicates/adjacency:** choose policies explicitly. `reduce()` and consensus
   merge overlapping **and adjacent** intervals; ordinary half-open overlap does
   not treat `[0,10)` and `[10,20)` as overlapping.

Run the local validator first:

```bash
python3 -B scripts/bed_validator.py \
  --input data.bed.gz \
  --assembly GRCh38.p14 \
  --chrom-sizes GRCh38.p14.chrom.sizes \
  --require-sorted
```

## Safe local workflow

1. Inventory local files, checksums, assembly, contig dictionary, coordinate
   system, strand policy, patient/replicate groups, and intended outputs.
2. Validate BED/fragments and estimate work. Pilot a small synthetic file.
3. Choose Python, CLI, or Rust from the documented surface; do not translate API
   names by guesswork.
4. Set hard limits for input bytes/records/files, threads/jobs, memory, temporary
   disk, output size, and wall time.
5. Run in a dedicated output directory. Refuse collisions unless overwrite was
   explicitly approved.
6. Revalidate output sorting, bounds, row counts, checksums, and provenance.

## Current Python core

Imports are from submodules, not the `gtars` top level:

```python
from gtars.models import Region, RegionSet

query = RegionSet.from_regions(
    [
        Region(chr="chr1", start=100, end=200, rest=None),
        Region(chr="chr1", start=300, end=400, rest=None),
    ],
    strands=["+", "-"],
)
universe = RegionSet.from_vectors(
    ["chr1", "chr1"],
    [150, 500],
    [350, 600],
)

counts = query.count_overlaps(universe)       # one count per query region
flags = query.any_overlaps(universe)          # one bool per query region
indices = query.find_overlaps(universe)       # indices into universe
pieces = query.intersect_all(universe)        # all intersection fragments
fraction = query.coverage(universe)           # fraction of query bp covered
```

`RegionSet.sort()` mutates and returns `None`. Set algebra includes `reduce`,
`setdiff`, `pintersect` (pairs by index), `concat`, `union`, `jaccard`,
`coverage`, `overlap_coefficient`, `intersect_all`, `closest`, `cluster`, and
`gaps`. Read `references/python-api.md` before relying on ordering or strand.

Consensus is a Python binding in a different module:

```python
from gtars.genomic_distributions import consensus

rows = consensus([query, universe])
# rows: [{"chr": ..., "start": ..., "end": ..., "count": ...}, ...]
```

Signal-track generation is **not** exposed as `gtars.uniwig` in Python 0.9.2;
use the reviewed CLI or Rust API. `RegionSet.coverage()` is a base-pair set metric,
not a WIG/bigWig generator.

## Tokenizers, fragments, and reference stores

Use only local constructors by default:

```python
from gtars.models import RegionSet
from gtars.tokenizers import Tokenizer

tokenizer = Tokenizer.from_bed("reviewed-universe.bed")
regions = RegionSet("local-query.bed")
tokens = tokenizer.tokenize(regions)
encoding = tokenizer(regions)
ids = encoding["input_ids"]
```

`Tokenizer.from_pretrained(name)` contacts Hugging Face and writes its cache when
the argument is not an existing local directory; it exposes no revision or cache
argument. Obtain explicit approval, fetch an immutable revision through a reviewed
mechanism, verify checksums, then pass the local snapshot directory. See
`references/tokenizers.md`.

For refget, prefer `RefgetStore.in_memory()` or `RefgetStore.open_local(path)`.
`open_remote(cache_path, remote_url)` contacts a remote service, creates/uses a
local cache, and performs on-demand range reads. See `references/refget.md`.

## Network and cache gate

No download or cache write is implicit in this skill. Before any network-capable
upstream call:

- obtain explicit user approval for the exact host, endpoint, data, and cache;
- allowlist HTTPS hosts and reject unreviewed redirects;
- record immutable revision/identifier, retrieval time, expected SHA-256 and
  domain digest, assembly accession, size quota, and provenance;
- disclose sensitive BED coordinates, barcodes, sample labels, and reference
  choices that could leave the approved environment;
- validate downloaded content as untrusted before using it.

Important side effects:

- `RegionSet(path)` has HTTP support; a nonexistent local string may be treated as
  a URL. Check that the local path exists before construction.
- `Tokenizer.from_pretrained` may download `universe.bed.gz` into the Hugging Face
  cache.
- `RefgetStore.on_disk` creates/writes a store. `open_remote` loads remote metadata
  and enables persistence by default.
- `gtars bbcache` creates cache directories even when constructing the client.
  Cache/download commands use `BBCLIENT_CACHE` (default `~/.bbcache`) and
  `BEDBASE_API` (default `https://api.bedbase.org`).

## Sensitive metadata and leakage

Genomic intervals, rare loci, barcodes, sample names, phenotypes, and assembly
choices can be identifying. Keep full paths and raw coordinates out of logs;
default bundled reports redact paths and emit only counts/checksums.

Freeze splits by patient/donor first, then keep all technical and biological
replicates in the same split. Fit consensus sets, universes, tokenizers, scaling,
thresholds, and QC rules on training data only. Do not create a universe from all
samples and then split: that leaks validation/test locus support. Record excluded
samples and replicate aggregation separately.

## Bundled deterministic CLIs

All six helpers reject URLs, traversal, symlinks, and special files; apply byte,
record, file, coordinate, and worker caps; use no network or gtars import; and
write no output files. Plans contain fixed argv templates and never launch them.

```bash
python3 -B scripts/bed_validator.py --help
python3 -B scripts/execution_plan.py --help
python3 -B scripts/tokenizer_manifest.py --help
python3 -B scripts/refget_digest_plan.py --help
python3 -B scripts/coverage_preflight.py --help
python3 -B scripts/artifact_inspector.py --help
```

Run synthetic tests without bytecode:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s tests/gtars -p 'test_*.py' -v
```

## Migration traps removed in 1.1

Do not use stale examples containing `gtars.RegionSet`,
`RegionSet.from_bed`, `TreeTokenizer`, `gtars.igd.build_index`,
`gtars.uniwig.coverage_from_bed`, `gtars.RefgetStore`, global
`set_option`/`set_log_level`, `parallel_apply`, or invented exception classes.
CLI forms such as `uniwig generate`, `igd build`, `scoring score`, and
`fragsplit cluster-split` are also stale for 0.9.0.

Upstream's published docs and stubs have some drift (for example the older
`GlobalRefgetStore` tutorial and incomplete 0.9.2 stubs). Prefer installed
signature smoke tests plus immutable tagged source when they conflict.

## Bundled references

These are the only six bundled references; all links are local and present:

- `references/python-api.md` — exact Python 0.9.2 imports and behavior
- `references/overlap.md` — overlap/count/set algebra and consensus semantics
- `references/coverage.md` — uniwig, bigWig, coverage, sorting, and resources
- `references/tokenizers.md` — tokenizer/universe and fragment compatibility
- `references/refget.md` — digests, stores, BEDbase, network/cache controls
- `references/cli.md` — CLI 0.9.0 commands, features, and migrations

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/gtars/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/cli.md`

# Command-line interface (`gtars-cli==0.9.0`)

Verified from the published crate and `v0.9.0` tagged source on **2026-07-23**.
The package is `gtars-cli`; the installed binary is `gtars`.

## Trust, installation, and features

Cargo installation compiles native code and may run transitive build scripts.
Review the official crate/source, lock resolution, license, and build environment
before:

```bash
cargo install gtars-cli --version 0.9.0 --locked
gtars --version
gtars --help
```

The v0.9.0 GitHub release also publishes platform archives plus `.sha256`
sidecars. Verify the archive checksum before extraction and do not execute an
untrusted binary. The bundled `artifact_inspector.py` hashes/classifies an
artifact without extracting or executing it.

Default CLI features are:

```text
scoring uniwig bbcache igd fragsplit overlaprs genomicdist refget
```

To build a reduced binary:

```bash
cargo install gtars-cli --version 0.9.0 --locked \
  --no-default-features --features "overlaprs,genomicdist"
```

Feature availability controls subcommand availability. There is no 0.9.0 CLI
`tokenizers` feature/subcommand. Do not copy an old `--all-features` binary's
command assumptions into a reduced binary.

## Global behavior

```bash
gtars --help
gtars --version
gtars <command> --help
```

Tagged source defines no global `--threads`, `--memory-limit`, `--buffer-size`,
`--verbose`, `--quiet`, `--strict`, `--continue-on-error`, or `--log-file`
options. Concurrency is command-specific.

Before every real command, run the exact installed `--help`. This reference is
pinned to 0.9.0; unversioned web documentation can drift.

## `overlaprs`

```bash
gtars overlaprs \
  --query query.bed \
  --universe universe.bed \
  --backend bits
```

Options:

- `-q/--query PATH` (required);
- `-u/--universe PATH` (required);
- `-e/--backend bits|ailist` (handler default: `bits`);
- `--streaming` is parsed but ignored by the v0.9.0 handler.

Output is BED3 universe-hit coordinates to stdout, one row per overlap. It is not
a count table and does not retain query IDs. See `overlap.md`.

## `igd`

Create from a **folder** of BED files:

```bash
gtars igd create \
  --filelist approved-bed-directory \
  --output index-directory \
  --dbname reference_index
```

Search with a BED/BED.GZ query:

```bash
gtars igd search \
  --database index-directory \
  --query query.bed
```

Current subcommands are `create` and `search`, not `build`, `query`, or `count`.
The `--filelist` help text calls the input a path to a list but specifies a
folder; validate installed behavior on a synthetic directory before scaling.

## `uniwig`

Batch BigWig:

```bash
gtars uniwig \
  --file sorted.bed.gz \
  --filetype bed \
  --chromref assembly.chrom.sizes \
  --smoothsize 5 \
  --stepsize 1 \
  --fileheader output/sample_ \
  --outputtype bw \
  --counttype core \
  --threads 4
```

BAM QC:

```bash
gtars uniwig bamqc \
  --input aligned.bam \
  --output bamqc.tsv \
  --threads 1
```

BED streaming adds `--streaming` and supports only WIG/bedGraph output. Read
`coverage.md` for all flags, sorting/bounds, BAM behavior, and resource limits.

## `consensus`

```bash
gtars consensus \
  --beds a.bed b.bed c.bed \
  --min-count 2 \
  --output consensus.bed
```

- `--beds` requires at least two paths;
- `--min-count` defaults to 1;
- output defaults to stdout and is BED4 (`chr start end count`).

Consensus counts input sets overlapping a reduced union component; it is not
per-base support segmentation. See `overlap.md`.

## `ranges`

`ranges` exposes interval algebra:

```text
gtars ranges reduce      --input BED [--output OUT]
gtars ranges trim        --input BED --chrom-sizes SIZES [--output OUT]
gtars ranges promoters   --input BED [--upstream 2000] [--downstream 200] [--output OUT]
gtars ranges setdiff     -a BED_A -b BED_B [--output OUT]
gtars ranges pintersect  -a BED_A -b BED_B [--output OUT]
gtars ranges concat      -a BED_A -b BED_B [--output OUT]
gtars ranges union       -a BED_A -b BED_B [--output OUT]
gtars ranges jaccard     -a BED_A -b BED_B
gtars ranges shift       --input BED --offset N [--output OUT]
gtars ranges flank       --input BED --width N [--start|--both] [--output OUT]
gtars ranges resize      --input BED --width N [--fix start|end|center] [--output OUT]
gtars ranges narrow      --input BED [--start N] [--end N] [--width N] [--output OUT]
gtars ranges disjoin     --input BED [--output OUT]
gtars ranges gaps        --input BED --chrom-sizes SIZES [--output OUT]
gtars ranges intersect   -a BED_A -b BED_B [--output OUT]
```

Operations without `--output` write to stdout. `promoters` is anchored on region
starts in core behavior; do not assume strand-aware TSS handling.

## `fscoring` fragment counts

File-by-peak matrix:

```bash
gtars fscoring "fragments/sample01.fragments.tsv.gz" consensus.bed \
  --mode atac \
  --output counts.csv.gz
```

Arguments are positional:

```text
gtars fscoring <fragments> <consensus> [--mode atac|chip] [--output PATH]
```

- `fragments` is interpreted by `FragmentFileGlob`; a single explicit local file
  is safest. Shell globs can expose unintended files, while quoted globs are
  expanded by the library.
- default mode is `atac`;
- default output is `fscoring.csv.gz`;
- `atac` uses cut-site scoring semantics; `chip` uses fragment overlap semantics.

Sparse barcode mode:

```bash
gtars fscoring sample.fragments.tsv.gz consensus.bed \
  --barcode \
  --output output/sample01
```

This writes:

```text
output/sample01_matrix.mtx.gz
output/sample01_barcodes.tsv.gz
output/sample01_features.tsv.gz
```

The fragment file must carry valid coordinates and barcodes. Do not expose raw
barcodes in logs or reports; cap cells, peaks, nonzeros, memory, and output.

## `pb` pseudobulk splitting

The current command name is `pb`, not `fragsplit`:

```bash
gtars pb sample.fragments.tsv.gz barcode_to_cluster.tsv \
  --output pseudobulk-output
```

Positional arguments are fragments then mapping; default output is `out/`.
This writes cluster-specific files. Validate mapping uniqueness, unknown
barcodes, safe cluster names, output collisions, file-count bounds, and patient
split policy first.

## `genomicdist`

Minimal call:

```bash
gtars genomicdist \
  --bed regions.bed \
  --chrom-sizes assembly.chrom.sizes \
  --bins 250 \
  --output distribution.json
```

Optional inputs/features:

- `--gtf GTF` for partitions and derived TSS distances;
- `--tss BED` to override GTF-derived TSS;
- `--signal-matrix TSV`;
- `--fasta FASTA|FAB` for GC content;
- `--dinucl-freq` and `--dinucl-raw-counts`;
- `--ignore-unk-chroms`;
- `--promoter-upstream`, `--promoter-downstream`;
- `--compact`.

Supplying chromosome sizes makes region-distribution bins comparable across
files and enables bounds-related operations. Omitting them derives scale from
observed ends and is unsuitable for cross-file comparison.

## `prep`

```text
gtars prep --gtf genes.gtf.gz [--output genes.gda]
gtars prep --signal-matrix matrix.tsv.gz [--output matrix.bin]
gtars prep --fasta reference.fa [--output reference.fab]
```

`prep` serializes local inputs into Gtars-specific binary formats. Treat these
artifacts as versioned native data: hash inputs/outputs, record 0.9.0, reject
untrusted serialized files, and bound expansion/memory.

## `refget`

```bash
gtars refget build reference.fa reference-alt.fa.gz \
  --output refget-store \
  --jobs 1
```

Other options are `--file-list/-f`, `--raw`, and `--force`; `--jobs 0` means
automatic concurrency. There are no current CLI `digest`, `verify`, or remote
query subcommands. See `refget.md`.

## `bbcache`

```text
gtars bbcache cache-bed       --identifier VALUE [--cache-folder DIR]
gtars bbcache cache-bedset    --identifier VALUE [--cache-folder DIR]
gtars bbcache seek            --identifier VALUE [--cache-folder DIR]
gtars bbcache inspect-bedfiles                 [--cache-folder DIR]
gtars bbcache inspect-bedsets                  [--cache-folder DIR]
gtars bbcache rm              --identifier VALUE [--cache-folder DIR]
```

Client construction creates cache directories. Cache/download calls can contact
BEDbase or arbitrary URL hosts and write SQLite/cache files. `rm` deletes local
content. The tagged source has a likely ID-only download mismatch described in
`refget.md`; do not guess a workaround.

## Threading and resource controls

There is no global thread flag:

- batch uniwig `--threads/-p` defaults to 6;
- `uniwig bamqc --threads/-t` defaults to 1; values above 1 need a BAM index;
- `refget build --jobs/-j` defaults to 0 (auto);
- other commands expose no documented thread setting.

Set command-specific values explicitly. Also bound input bytes/records/files,
glob matches, hit pairs/nonzeros, stdout, memory, temporary disk, cache, and
wall time externally.

## Safe dry-run planning

```bash
python3 -B scripts/execution_plan.py --help
python3 -B scripts/coverage_preflight.py --help
```

These helpers produce fixed argv templates only. They do not invoke `gtars`,
expand globs, download data, create caches, or write outputs.

## Removed stale command forms

Do not use:

```text
gtars igd build/query/count
gtars overlaprs overlap/count/filter/subtract
gtars uniwig generate
gtars scoring score/batch
gtars fragsplit split/cluster-split/filter
gtars refget digest/verify
gtars --threads/--memory-limit/--verbose
```

## Official sources (accessed 2026-07-23)

- [gtars-cli 0.9.0 crate](https://crates.io/crates/gtars-cli)
- [Gtars v0.9.0 release](https://github.com/databio/gtars/releases/tag/v0.9.0)
- [CLI main parser at v0.9.0](https://github.com/databio/gtars/blob/v0.9.0/gtars-cli/src/main.rs)
- [CLI feature manifest at v0.9.0](https://github.com/databio/gtars/blob/v0.9.0/gtars-cli/Cargo.toml)
- [Official CLI guide](https://docs.bedbase.org/gtars/cli/)
- [Official versioning policy](https://docs.bedbase.org/gtars/versioning/)

### `references/coverage.md`

# Coverage, uniwig, and bigWig

Verified against `gtars-cli==0.9.0` / `gtars-uniwig==0.9.0` on
**2026-07-23**. The public BEDbase page is partly under construction; tagged CLI
and crate source take precedence where examples differ.

## Distinguish two meanings of coverage

- Python `RegionSet.coverage(other)` returns a single fraction of base pairs in
  the first set covered by the second.
- `gtars uniwig` creates positional signal tracks (WIG, NPY, bedGraph, bigWig,
  and limited BAM-derived outputs).

Python 0.9.2 does not export `gtars.uniwig`. Old examples using
`gtars.uniwig.coverage_from_bed`, `coverage.normalize()`, `smooth()`,
`call_peaks()`, or `to_bigwig()` are not current APIs.

## Input contract

For BED and narrowPeak:

1. use 0-based half-open intervals;
2. supply the exact assembly's local `chrom.sizes`;
3. require every contig to exist and every end to be within bounds;
4. sort by chromosome dictionary order, then numeric start/end;
5. use one local file (BED, narrowPeak, or BAM);
6. preserve strand separately—uniwig's BED path produces start/end/core counts,
   not a generic BED6 strand-aware split.

The official module guide states that uniwig expects a single chromosome-sorted
input. Never concatenate samples, patients, or assemblies without a reviewed
aggregation policy.

Run the deterministic preflight:

```bash
python3 -B scripts/coverage_preflight.py \
  --input fragments.sorted.bed.gz \
  --input-type bed \
  --chrom-sizes GRCh38.p14.chrom.sizes \
  --assembly GRCh38.p14 \
  --output-prefix derived/sample01 \
  --output-type bw \
  --count-type core \
  --threads 4
```

It validates local paths, bounds, sorting, Gtars `u32` coordinates, output
collision, and a conservative dense-value budget. It writes and executes
nothing.

## Current batch CLI

BigWig generation uses the root `uniwig` command directly—there is no `generate`
subcommand:

```bash
gtars uniwig \
  --file fragments.sorted.bed.gz \
  --filetype bed \
  --chromref GRCh38.p14.chrom.sizes \
  --smoothsize 5 \
  --stepsize 1 \
  --fileheader derived/sample01_ \
  --outputtype bw \
  --counttype core \
  --threads 4 \
  --zoom 1
```

Equivalent short options are `-f`, `-t`, `-c`, `-m`, `-s`, `-l`, `-y`, `-u`,
`-p`, and `-z`. Valid batch count types are:

- `start`: accumulations at interval starts;
- `end`: accumulations at interval ends;
- `core`: interval-body accumulations;
- `all`: produce start, end, and core;
- `shift`: BAM-specific shifted workflow.

The implementation accepts `wig`, `npy`, `bedgraph`, `bw`, and `bigwig` strings
along relevant paths, but use the documented compact `bw` for BigWig. BED and
narrowPeak can produce WIG, NPY, bedGraph, or BigWig. BAM paths produce BigWig or
BED in the documented workflow.

Other batch flags:

- `--score` uses narrowPeak score;
- `--bamscale FLOAT` scales BAM values (default `1.0`);
- `--no-bamshift` disables direction-aware BAM shifting;
- `--wigstep fixed|variable` selects WIG step style;
- `--debug` increases output.

Validate scientific meaning before using start/end/shift signals. ATAC cut-site
shifts and ChIP fragment-body counts are not interchangeable.

## Streaming mode

For very large **BED** input, 0.9.0 exposes a streaming processor whose state is
bounded by smoothing/gap behavior:

```bash
gtars uniwig \
  --file fragments.sorted.bed.gz \
  --filetype bed \
  --chromref GRCh38.p14.chrom.sizes \
  --smoothsize 5 \
  --stepsize 1 \
  --fileheader derived/sample01_ \
  --outputtype bedgraph \
  --counttype core \
  --streaming \
  --dense 0
```

Streaming constraints in tagged source:

- only BED input;
- only `wig` or `bedgraph` output, not BigWig or NPY;
- count type `start`, `end`, `core`, or `all` (not BAM `shift`);
- `--dense 0` is sparse, `--dense -1` is fully dense, and positive `N` fills
  gaps no wider than `N`;
- `--stdout` is available; multiple count types receive separator comments.

If stdin is used with `--counttype all`, the handler buffers stdin into memory so
it can replay it. Do not claim constant memory for that combination.

## BAM QC and BAM coverage

Library-complexity metrics are a subcommand:

```bash
gtars uniwig bamqc \
  --input aligned.bam \
  --output bamqc.tsv \
  --threads 1
```

Parallel BAM QC (`--threads >1`) requires a `.bai` index. Bound BAM size, index
size, decompression work, threads, and output. Metrics NRF/PBC1/PBC2 are technical
QC summaries, not evidence of biological quality or suitability.

For BAM-to-bigWig, the batch path requires the same `--smoothsize`,
`--stepsize`, `--fileheader`, `--chromref`, and output controls. Keep alignment
assembly, filtering, duplicate policy, paired-end handling, and shift/scaling in
the provenance record.

## BigWig preflight and postflight

Before generation:

- verify the exact chromosome dictionary and checksum;
- reject unknown/out-of-bounds contigs;
- ensure sorted input and numeric signal values;
- reserve disk for intermediate bedGraph plus final BigWig;
- set threads explicitly (upstream batch default is 6);
- use a new output prefix;
- avoid patient identifiers in filenames and track labels.

After generation:

- verify nonzero file size and BigWig readability with a trusted, pinned reader;
- compare its chromosome dictionary and lengths with the input checksum;
- query fixed synthetic positions with known expected coverage;
- check min/max/NaN behavior and start/end/core suffixes;
- record SHA-256, tool versions, parameters, and input hashes.

UCSC documents bedGraph coordinates as 0-based half-open and numerically ordered.
Its BigWig tools require matching chromosome sizes. A successful binary write
does not prove the assembly or signal semantics are correct.

## Rust APIs

Enable only uniwig:

```toml
[dependencies]
gtars = { version = "=0.9.0", default-features = false, features = ["uniwig"] }
```

The wrapper re-exports `gtars_uniwig` as `gtars::uniwig`. The primary batch
function is:

```text
uniwig_main(
  vec_count_type, smoothsize, filepath, chromsizerefpath, bwfileheader,
  output_type, filetype, num_threads, score, stepsize, zoom, debug,
  bam_shift, bam_scale, wigstep
) -> Result<(), Box<dyn Error>>
```

It is deliberately string-heavy and has many arguments; prefer the pinned CLI
unless embedding is necessary. The typed streaming API is:

```text
uniwig::stream::uniwig_streaming(
  input, output, chrom_sizes, smooth_size, step_size,
  CountType::{Start|End|Core},
  OutputFormat::{Wig|BedGraph},
  max_gap
)
```

`read_chrom_sizes(BufRead)` parses the dictionary. BigWig is a batch API, not a
streaming `OutputFormat`.

## Threading and resources

- Batch uniwig builds a Rayon pool of exactly `--threads`; the CLI default is 6.
- Streaming mode is not controlled by the batch `--threads` path.
- Output work can scale with total assembly span divided by step size, not only
  with BED row count.
- Smoothing, dense gap filling, three count types, BigWig intermediates, and high
  thread counts can multiply memory/disk.
- Start with one thread and one small synthetic contig. Increase only after
  measuring peak RSS, temporary disk, throughput, and deterministic equivalence.

## Official sources (accessed 2026-07-23)

- [Gtars uniwig module guide](https://docs.bedbase.org/gtars/uniwig/)
- [CLI uniwig parser at v0.9.0](https://github.com/databio/gtars/blob/v0.9.0/gtars-cli/src/uniwig/cli.rs)
- [CLI uniwig handler at v0.9.0](https://github.com/databio/gtars/blob/v0.9.0/gtars-cli/src/uniwig/handlers.rs)
- [Rust uniwig 0.9.0 source](https://github.com/databio/gtars/tree/v0.9.0/gtars-uniwig)
- [UCSC bedGraph format](https://genome.ucsc.edu/goldenPath/help/bedgraph.html)
- [UCSC BigWig format](https://genome.ucsc.edu/goldenPath/help/bigWig.html)

### `references/overlap.md`

# Overlap, counts, set algebra, and consensus

Verified against Gtars Python 0.9.2 and Rust/CLI 0.9.0 on **2026-07-23**.

## Interval meaning

Use 0-based, half-open intervals. Two valid intervals overlap when:

```text
a.start < b.end and b.start < a.end
```

Thus `[0,10)` overlaps `[9,20)` but not adjacent `[10,20)`. Validate assembly,
exact contig names, `start < end`, chromosome bounds, and Gtars' `u32` coordinate
limit before indexing.

Overlap and reduction answer different questions:

- overlap/query methods use ordinary half-open overlap;
- `reduce()` merges overlapping **and adjacent** intervals;
- `union()` reduces the concatenated sets;
- consensus first reduces the union, so adjacency can combine support domains.

## Python directional overlap queries

```python
from gtars.models import RegionSet

query = RegionSet("query.bed")
universe = RegionSet("universe.bed")

counts = query.count_overlaps(universe)
any_hit = query.any_overlaps(universe)
hit_indices = query.find_overlaps(universe)
query_with_hits = query.subset_by_overlaps(universe)
```

Interpretation is directional:

- `counts[i]` is the number of universe intervals overlapping query interval `i`;
- `any_hit[i]` is a boolean for query interval `i`;
- `hit_indices[i]` contains 0-based indices into the in-memory `universe`;
- `subset_by_overlaps` preserves only query intervals with one or more hits.

Both file-backed sets are sorted by the constructor. Do not join these arrays to
the original unsorted row number without carrying a separate stable identifier.

For actual intersection coordinates:

```python
pieces = query.intersect_all(universe)
```

`intersect_all` computes `[max(starts), min(ends))` for every overlapping pair.
It differs from `pintersect`, which pairs two sets by index position.

## Base-pair set metrics

```python
reduced = query.reduce()
difference = query.setdiff(universe)
combined = query.concat(universe)
union = query.union(universe)
pairwise = query.pintersect(universe)

jaccard = query.jaccard(universe)
covered_fraction = query.coverage(universe)
overlap_coefficient = query.overlap_coefficient(universe)
```

- Jaccard: `intersection_bp / union_bp`.
- Coverage: fraction of query base pairs covered by universe after overlap
  normalization.
- Overlap coefficient: `intersection_bp / min(query_bp, universe_bp)`.
- `concat` does not merge; `union` does.
- `setdiff` can split query intervals.

Empty-set edge cases and zero denominators should be tested with the exact pinned
version before relying on metric values.

## Rust index API

The exact wrapper dependency is:

```toml
[dependencies]
gtars = { version = "=0.9.0", default-features = false, features = [
  "core", "overlaprs"
] }
```

A build-once/query-many pattern uses the component re-exports:

```rust
use gtars::core::models::RegionSet;
use gtars::overlaprs::IndexedRegionSet;
use std::error::Error;

fn main() -> Result<(), Box<dyn Error>> {
    let universe = RegionSet::try_from("universe.bed")?;
    let query = RegionSet::try_from("query.bed")?;
    let index = IndexedRegionSet::new(universe);

    let counts = index.count_overlaps(&query, None);
    let flags = index.any_overlaps(&query, None);
    let hits = index.find_overlaps(&query, None);

    assert_eq!(counts.len(), query.len());
    assert_eq!(flags.len(), query.len());
    assert_eq!(hits.len(), query.len());
    Ok(())
}
```

The optional second argument is a region filter in the component API; `None`
queries all regions. Consult the exact
[`gtars-overlaprs 0.6.0` docs](https://docs.rs/gtars-overlaprs/0.6.0/gtars_overlaprs/)
selected by the 0.9.0 wrapper.

## CLI `overlaprs` is not a count command

The current CLI form is:

```bash
gtars overlaprs \
  --query query.bed \
  --universe universe.bed \
  --backend bits
```

Valid backends are `bits` and `ailist`; the handler defaults to `bits`. The
command writes every overlapping **universe interval** as BED3 to stdout. It does
not emit query coordinates, query IDs, universe IDs, or one count per query.
Repeated universe hits can therefore be indistinguishable in the output.

Use Python `count_overlaps` when row-aligned counts are required. The CLI exposes
a `--streaming` flag in 0.9.0, but the tagged handler does not read it; do not
claim lower memory from that flag.

Build a non-executing local plan first:

```bash
python3 -B scripts/execution_plan.py \
  --operation overlap \
  --query query.bed \
  --universe universe.bed \
  --assembly GRCh38.p14 \
  --chrom-sizes GRCh38.p14.chrom.sizes
```

## Consensus semantics

Python:

```python
from gtars.genomic_distributions import consensus

rows = consensus([replicate_a, replicate_b, replicate_c])
```

CLI:

```bash
gtars consensus \
  --beds replicate_a.bed replicate_b.bed replicate_c.bed \
  --min-count 2 \
  --output consensus.bed
```

The algorithm:

1. concatenates every set;
2. reduces all ranges to a non-overlapping union, merging adjacency;
3. for each union range, counts how many input **sets** have at least one overlap;
4. returns BED4-like `chr, start, end, count`, sorted by chromosome/start.

It does not cut ranges at every support transition. For example, partially
overlapping `[0,10)` and `[5,15)` produce union `[0,15)` with count 2, even though
the edges are supported by one set. This is set-level support for a merged union
component, not per-base support.

`--min-count` filters after consensus computation and must be positive. Validate
that it does not exceed the number of input sets.

## Replicates and leakage

- Define biological replicate/donor/patient groups before consensus.
- Keep all samples from one patient in one train/validation/test split.
- Build a training consensus/universe from training replicates only.
- Do not use held-out overlap counts to tune `min-count`, merge gaps, blacklist
  handling, or backend parameters.
- Report per-replicate support and exclusions; a merged consensus is not evidence
  that every replicate supports every base.

## Scaling and bounds

- `RegionSet` loads full interval vectors and sorts them.
- Index memory scales with universe size; hit output can scale with the number of
  overlap pairs, much larger than either input.
- Cap input records/bytes, output rows/bytes, memory, and wall time.
- Pilot both backends on representative training data; identical semantics and
  deterministic result ordering must be verified before switching.
- Keep stdout redirected only to an approved nonexisting output path and verify
  it after completion.

## Removed stale APIs

There is no current Python `gtars.igd.build_index`, `igd.query`,
`filter_overlapping`, `filter_non_overlapping`, `overlap_fraction`, or
`overlap_coverage` surface matching the old skill. CLI `igd` has only `create`
and `search`; see `cli.md`.

## Official sources (accessed 2026-07-23)

- [Python RegionSet 0.9.2 binding](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/src/models/region_set.rs)
- [Rust overlaprs source at v0.9.0](https://github.com/databio/gtars/tree/v0.9.0/gtars-overlaprs)
- [CLI overlap parser](https://github.com/databio/gtars/blob/v0.9.0/gtars-cli/src/overlaprs/cli.rs)
- [CLI overlap handler/output](https://github.com/databio/gtars/blob/v0.9.0/gtars-cli/src/overlaprs/handlers.rs)
- [Consensus implementation](https://github.com/databio/gtars/blob/v0.9.0/gtars-genomicdist/src/consensus.rs)
- [Gtars overlap module guide](https://docs.bedbase.org/gtars/overlaprs/)

### `references/python-api.md`

# Python API (`gtars==0.9.2`)

Research and runtime verification date: **2026-07-23**. The PyPI package requires
Python 3.10+ and contains a native PyO3 extension.

## Import surface

Public functionality is grouped into submodules:

```python
import gtars
from gtars.models import Region, RegionSet
from gtars.genomic_distributions import consensus
from gtars.tokenizers import Tokenizer, tokenize_fragment_file
from gtars.refget import RefgetStore, digest_fasta, digest_sequence
```

`gtars.__version__` is `0.9.2`. `Region`, `RegionSet`, `Tokenizer`, and
`RefgetStore` are not documented as top-level classes. Python 0.9.2 does not
export Python `uniwig`, `igd`, `scoring`, `fragsplit`, or `bbcache` submodules.

## Verified signatures

The installed 0.9.2 wheel reported:

```text
Region(chr, start, end, rest)
RegionSet(path)
RegionSet.from_regions(regions, strands=None)
RegionSet.from_vectors(chrs, starts, ends, strands=None)
RegionSet.count_overlaps(self, other)
RegionSet.coverage(self, other)
Tokenizer(path)
Tokenizer.from_bed(path)
Tokenizer.from_pretrained(path)
tokenize_fragment_file(file, tokenizer)
consensus(region_sets)
RefgetStore.open_local(path)
RefgetStore.open_remote(cache_path, remote_url)
RefgetStore.get_substring(self, seq_digest, start, end)
```

The shipped `.pyi` stubs omit some runtime methods (`from_vectors`, `disjoin`,
`strands`, and several refget load methods). The tagged PyO3 source and the
installed runtime are authoritative for those omissions.

## `Region`

```python
from gtars.models import Region

region = Region(
    chr="chr1",
    start=100,
    end=200,
    rest="peak_001\t500\t+",
)
assert len(region) == 100
assert (region.chr, region.start, region.end) == ("chr1", 100, 200)
```

`start` and `end` are Rust `u32`. Validate `0 <= start < end <= contig_length`
before construction. The constructor does not itself prove assembly or contig
compatibility. Equality compares only chromosome/start/end; trailing `rest`
content is not part of equality.

## `RegionSet` constructors

### Local file

```python
from pathlib import Path
from gtars.models import RegionSet

path = Path("reviewed-input.bed.gz")
if not path.is_file() or path.is_symlink():
    raise ValueError("expected a reviewed local regular file")
regions = RegionSet(str(path))
```

The Python build enables `gtars-core`'s HTTP feature. If the supplied string is
not an existing local file, core code attempts to open it as a URL. Therefore,
checking `is_file()` before construction is a security boundary, not just an
error-message improvement.

File parsing:

- accepts tab-separated BED-like input and `.gz`;
- skips `browser`, `track`, and `#` lines;
- treats a first row with a nonnumeric second field as a column header;
- requires at least three columns;
- stores columns 4+ as one tab-joined `Region.rest` string;
- rejects an empty region set;
- sorts in memory by lexicographic chromosome then numeric start.

The original file is not rewritten, but input row order is not preserved in the
object.

### In-memory regions

```python
from gtars.models import Region, RegionSet

regions = RegionSet.from_regions(
    [
        Region("chr1", 100, 200, None),
        Region("chr2", 300, 450, None),
    ],
    strands=["+", "-"],
)

same = RegionSet.from_vectors(
    ["chr1", "chr2"],
    [100, 300],
    [200, 450],
    strands=["+", "-"],
)
```

All coordinate vectors, and the optional strand vector, must have equal length.
When strands are omitted, the separate strand vector contains `"*"`.

## Properties and mutability

```python
n = len(regions)
first = regions[0]       # negative indices are supported
identifier = regions.identifier
file_digest = regions.file_digest
header = regions.header
strands = regions.strands

regions.sort()           # in-place; returns None
regions.to_bed("out.bed")
regions.to_bed_gz("out.bed.gz")
regions.to_bigbed("out.bb", "assembly.chrom.sizes")
```

- `identifier` is an MD5-like identifier over sorted first-three-column content.
- `file_digest` includes retained trailing columns. Neither value substitutes for
  an independently recorded SHA-256 provenance hash.
- `path` raises `ValueError` for a set created from regions/vectors.
- Writers overwrite/create the specified output; check output policy first.
- `to_bigbed` needs chromosome sizes matching every contig and bound.

## Interval statistics and structural operations

The following methods are current:

```python
widths = regions.widths()                 # list[int]
same_widths = regions.region_widths()     # alias
mean_width = regions.mean_region_width()  # runtime returns float
length = regions.get_nucleotide_length()
max_ends = regions.get_max_end_per_chr()
stats = regions.chromosome_statistics()

reduced = regions.reduce()
disjoint = regions.disjoin()
trimmed = regions.trim({"chr1": 248956422})
gaps = regions.gaps({"chr1": 248956422})
clusters = regions.cluster(max_gap=100)
```

`reduce()` merges overlapping **and adjacent** ranges. `trim()` drops unknown
contigs and clamps bounds. These transformations do not perform liftover and can
drop the separate strand vector.

`promoters(upstream, downstream)` is relative to each region's start in the
current implementation; it is not a safe substitute for a strand-aware TSS
workflow. Establish strand and TSS semantics independently.

`neighbor_distances()` and `nearest_neighbors()` can return fewer values than
input regions because singletons on a chromosome are skipped; results are not
row-aligned.

`distribution(n_bins=250, chrom_sizes=None)` uses observed maximum ends when
chromosome sizes are absent, making results non-comparable across files. Supply
the exact assembly dictionary. Unknown/out-of-bounds regions are skipped when
sizes are supplied, so summed counts may be lower than input count.

## Pairwise and all-vs-all operations

```python
a = RegionSet("a.bed")
b = RegionSet("b.bed")

concatenated = a.concat(b)          # no merge
union = a.union(b)                  # minimal merged set
difference = a.setdiff(b)           # subtract b bases from a
pairwise = a.pintersect(b)          # pair by index, not genomic all-vs-all
all_pieces = a.intersect_all(b)     # every genomic overlap fragment

jaccard = a.jaccard(b)
coverage = a.coverage(b)
coefficient = a.overlap_coefficient(b)
closest = a.closest(b)
```

`coverage` is `covered base pairs in a / merged base pairs in a`, in `[0,1]`.
It is not signal coverage and does not produce WIG/bigWig. `pintersect` depends
on index position after constructors may have sorted the inputs.

Overlap query methods are directional:

```python
counts = a.count_overlaps(b)        # one integer for each region in a
flags = a.any_overlaps(b)           # one bool for each region in a
indices = a.find_overlaps(b)        # indices into b for each region in a
subset = a.subset_by_overlaps(b)    # regions from a having at least one hit
```

## Consensus

```python
from gtars.genomic_distributions import consensus

result = consensus([a, b])
# [{"chr": "chr1", "start": 100, "end": 500, "count": 2}, ...]
```

The implementation concatenates all sets, reduces them into merged union
intervals (including adjacency), then counts how many input sets have at least
one overlap with each union interval. It does **not** segment a merged interval
at every support-change boundary. Use this exact meaning when interpreting
`count`.

## Tokenizer and fragment boundary

`Tokenizer.tokenize()` accepts a `RegionSet` or region objects accepted by the
native extractor. Despite older prose examples, the verified wheel rejected a
list of region strings. Use:

```python
from gtars.tokenizers import Tokenizer

tokenizer = Tokenizer.from_bed("local-universe.bed")
tokens = tokenizer.tokenize(a)
ids = tokenizer(a)["input_ids"]
```

See `tokenizers.md` for special-token, universe-order, remote download, and
fragment-file behavior.

## Error handling

The package does not export the invented `gtars.FileNotFoundError`,
`InvalidFormatError`, or `ParseError` classes from the old skill. Validate before
the call, then catch only the narrow built-in/native errors relevant to the
operation:

```python
try:
    regions = RegionSet("reviewed-local.bed")
except (OSError, RuntimeError, ValueError) as exc:
    raise RuntimeError("Gtars could not load the validated BED") from exc
```

Do not use a broad catch to continue past corrupted rows.

## APIs that are not present

The 0.9.2 Python surface does not provide:

- `gtars.RegionSet` or `RegionSet.from_bed`;
- `total_coverage`, `filter_by_size`, `filter_by_chromosome`, `intersect`,
  `subtract`, or `symmetric_difference` under the old names;
- `to_json`, `from_json`, NumPy array getters, `from_arrays`;
- `stream_bed`, `mmap=True`, `parallel=True`, or `parallel_apply`;
- global `set_option`, `option_context`, or `set_log_level`;
- a Python `uniwig` coverage object.

## Official sources (accessed 2026-07-23)

- [PyPI gtars 0.9.2](https://pypi.org/project/gtars/)
- [Python 0.9.2 model stubs](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/py_src/gtars/models/__init__.pyi)
- [Python 0.9.2 Region binding](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/src/models/region.rs)
- [Python 0.9.2 RegionSet binding](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/src/models/region_set.rs)
- [Python 0.9.2 genomic-distribution stubs](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/py_src/gtars/genomic_distributions/__init__.pyi)
- [Gtars model guide](https://docs.bedbase.org/gtars/regionSet/)

### `references/refget.md`

# Refget, sequence digests, stores, and BEDbase

Verified on **2026-07-23** against Python `gtars==0.9.2`,
`gtars-refget==0.9.1`, and `gtars-cli==0.9.0`.

## Digest terminology

Current Python functions:

```python
from gtars.refget import (
    compute_fai,
    digest_fasta,
    digest_sequence,
    load_fasta,
    md5_digest,
    sha512t24u_digest,
)

digest = sha512t24u_digest("ACGT")
assert digest == "aKF498dAxcJAqme6QYQ7EZ07-fiw8Kw2"
assert md5_digest("ACGT") == "f1f8f4bf413b16ad135722aa4591043e"
```

Gtars returns the 32-character unprefixed `sha512t24u` value. The preferred
GA4GH refget sequence identifier adds `SQ.`:

```text
SQ.aKF498dAxcJAqme6QYQ7EZ07-fiw8Kw2
```

MD5 is retained for legacy lookup and is not a collision-resistant provenance
hash. Keep an independent SHA-256 for artifact integrity.

`digest_sequence(data: bytes, name=None, description=None)` uppercases sequence
bytes and returns a `SequenceRecord` containing metadata and data.
`digest_fasta(path)` computes a `SequenceCollection`; `load_fasta(path)` loads
sequence data into memory. `compute_fai(path)` is for uncompressed FASTA.

GA4GH refget normalizes sequence content before computing its sequence
identifier. Do not hash raw FASTA bytes and call that a sequence digest: headers,
line wrapping, compression, and sequence normalization are different layers.

## Current Python store class

The runtime class is `RefgetStore`, not the older tutorial name
`GlobalRefgetStore`:

```python
from gtars.refget import RefgetStore
```

Verified constructors:

```text
RefgetStore.in_memory()
RefgetStore.on_disk(cache_path)
RefgetStore.open_local(path)
RefgetStore.open_remote(cache_path, remote_url)
RefgetStore.store_exists(path)
```

### Local and in-memory modes

```python
from gtars.refget import RefgetStore

store = RefgetStore.in_memory()
metadata, was_new = store.add_sequence_collection_from_fasta(
    "reviewed-reference.fa",
    force=False,
    namespaces=["refseq"],
)

store.write_store_to_dir("approved-store")
reopened = RefgetStore.open_local("approved-store")
```

Side effects:

- `in_memory()` does not write.
- `on_disk(path)` opens an existing store or creates a new disk-backed store.
- `open_local(path)` reads store metadata/indexes and lazy-loads local sequence
  data.
- `write_store_to_dir` and `enable_persistence` create/write files.
- `force=True` can replace existing collection/sequence entries.

Use `store_exists(path)` before choosing create versus open. Refuse symlinks,
unexpected files, output collisions, and unapproved stores.

Batch import:

```python
results = store.add_sequence_collections_from_fastas(
    ["ref-a.fa.gz", "ref-b.fa.gz"],
    file_list=None,
    jobs=1,
    force=False,
    namespaces=["refseq"],
)
```

`fastas` can also accept globs or directories and `jobs=0` means automatic
concurrency. For controlled runs, enumerate reviewed files explicitly and set a
positive bounded job count.

## Metadata-only and sequence access

Metadata methods avoid loading full sequence content:

```python
collections_page = store.list_collections(page=0, page_size=100)
sequence_metadata = store.list_sequences()
one_metadata = store.get_sequence_metadata(sequence_digest)
collection_metadata = store.get_collection_metadata(collection_digest)
```

Data methods:

```python
record = store.get_sequence(sequence_digest)
by_name = store.get_sequence_by_name(collection_digest, "chr1")
piece = store.get_substring(sequence_digest, 100, 200)
pieces = store.get_substrings(sequence_digest, [(100, 200), (500, 550)])

for chunk in store.stream_sequence(
    sequence_digest,
    start=0,
    end=1_000_000,
    chunk_size=65_536,
):
    consume_bounded(chunk)
```

Substring ranges are 0-based half-open. Validate `0 <= start <= end <= length`.
`stream_sequence` bounds peak result memory, but downstream accumulation can
still defeat streaming.

The 0.9.2 runtime also exposes `load_sequence`, `load_collection`,
`load_all_sequences`, and `load_all_collections`. These materialize more data;
do not call an all-load method without an explicit byte/RAM budget.

## Remote stores require an approval gate

```python
# Network + cache side effects: do not call before approval.
remote = RefgetStore.open_remote(
    approved_cache_path,
    approved_https_base_url,
)
```

`open_remote` takes only a cache path and base URL. It fetches remote metadata,
creates/uses local cache state, and enables persistence by default. In 0.9.2:

- `get_substring` can issue remote byte-range reads without downloading the
  whole sequence;
- `stream_sequence` can stream remote ranges;
- `load_sequence` is the whole-sequence path and can persist it.

Calling `disable_persistence()` after opening does not undo metadata/cache work
already performed. There is no constructor parameter for revision, endpoint
allowlist, checksum manifest, byte quota, or offline mode.

Before `open_remote`:

1. obtain explicit approval for exact HTTPS host/path and cache directory;
2. reject credentials in URLs and unreviewed redirects;
3. pin an immutable server/store revision or content-addressed identifier;
4. record expected collection/sequence digests and independent SHA-256 where
   applicable;
5. cap metadata, per-range, total transfer, sequence length, cache, retries,
   concurrency, and time;
6. disclose that request coordinates/digests and network metadata leave the
   environment;
7. validate returned lengths and digests before scientific use.

Custom/patient-specific assemblies and requested ranges can be sensitive even
when a public reference genome is not.

## Read-only concurrent stores

`into_readonly()` converts a mutable store into `ReadonlyRefgetStore` for
concurrent reads. It consumes/replaces the mutable store and cannot lazy-load
collections that were not prepared. Load only the bounded data required before
conversion; do not use `load_all_*` reflexively.

## CLI store build

The only current refget CLI subcommand is local store construction:

```bash
gtars refget build reference.fa reference-alt.fa.gz \
  --output approved-store \
  --jobs 1
```

Options:

- `--file-list/-f PATH`: file of paths/globs/directories;
- `--output/-o DIR`: required;
- `--jobs/-j N`: concurrent FASTA files, default `0` (auto);
- `--raw`: raw instead of default encoded 2-bit storage;
- `--force`: overwrite existing entries.

There is no current `gtars refget digest` or `verify` CLI matching the old skill.
Use the Python digest functions, direct Rust API, or a local store build after
preflight.

## Offline metadata/digest plan

The bundled helper accepts a conservative local policy manifest:

```json
{
  "schema_version": "1.0",
  "assembly": "GRCh38.p14",
  "coordinate_system": "0-based-half-open",
  "collection_digest": "<32-char sha512t24u-like value>",
  "sequences": [
    {
      "name": "chr1",
      "length": 248956422,
      "sha512t24u": "<32-char digest>",
      "md5": "<32 lowercase hex>"
    }
  ]
}
```

This is a **skill policy manifest**, not an upstream refget wire schema. Validate
it and optionally recompute sequence-level digests from local FASTA:

```bash
python3 -B scripts/refget_digest_plan.py \
  --metadata refget-metadata.json \
  --fasta reference.fa.gz \
  --assembly GRCh38.p14
```

The helper does not recompute the sequence-collection digest; it validates its
shape and verifies each listed local sequence's length, sha512t24u, and MD5.
Use Gtars' pinned collection implementation for final seqcol verification.

## BEDbase and `bbcache`

BEDbase caching is separate from refget. In CLI 0.9.0:

```text
gtars bbcache cache-bed
gtars bbcache cache-bedset
gtars bbcache seek
gtars bbcache inspect-bedfiles
gtars bbcache inspect-bedsets
gtars bbcache rm
```

Defaults from tagged source:

- API: `BEDBASE_API`, otherwise `https://api.bedbase.org`;
- cache: `BBCLIENT_CACHE`, otherwise `$HOME/.bbcache/` (or `/tmp/.bbcache/`);
- cached BEDs: `bedfiles/<first>/<second>/<id>.bed.gz`;
- BED sets: `bedsets/<first>/<second>/<id>.txt`;
- cache metadata includes SQLite state through the cache dependency.

Constructing `BBClient` creates the root and BED/BED-set subdirectories, even for
inspection/seek. `cache-bed` accepts a local file/directory, URL, or intended
BEDbase identifier; `cache-bedset` accepts a local directory/list or intended
BEDbase ID. `rm` deletes files and cache records and can remove member BEDs for a
BED set.

Important source finding: the v0.9.0 `BBClient.load_bed(id)` delegates a bare ID
to `RegionSet::try_from`, while the core source has the bare-BEDbase-ID fallback
commented out. Therefore, ID-only `cache-bed`/BED-set downloads may fail in this
release even though the public docs claim support. Do not work around this with
guessed URLs. Verify the installed help/behavior on a non-sensitive approved
test, or resolve an explicit official file URL through reviewed BEDbase metadata.

The bbcache source does not expose an expected SHA-256/revision parameter. Treat
downloads as untrusted:

- approve and allowlist `api.bedbase.org` and any exact data host separately;
- record BEDbase record ID, API response revision/time, explicit file URL,
  expected identifier/digest, and SHA-256;
- use an explicit quota-limited cache folder;
- validate BED assembly/bounds/content before indexing;
- never rely on a successful cache write as integrity proof.

## Rust pin

For the latest direct refget component:

```toml
[dependencies]
gtars-refget = "=0.9.1"
```

For the 0.9.0 wrapper release set:

```toml
[dependencies]
gtars = { version = "=0.9.0", default-features = false, features = ["refget"] }
```

Do not assume these expose identical refget patch behavior.

## Official sources (accessed 2026-07-23)

- [Python refget 0.9.2 stubs](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/py_src/gtars/refget/__init__.pyi)
- [Python 0.9.2 release](https://github.com/databio/gtars/releases/tag/gtars-python-v0.9.2)
- [gtars-refget 0.9.1 crate](https://crates.io/crates/gtars-refget)
- [Gtars refget module guide](https://docs.bedbase.org/gtars/refget/)
- [Gtars Python refget API](https://docs.bedbase.org/gtars/python/refget-api/)
- [CLI refget parser](https://github.com/databio/gtars/blob/v0.9.0/gtars-cli/src/refget/cli.rs)
- [BEDbase cache source](https://github.com/databio/gtars/tree/v0.9.0/gtars-bbcache)
- [BEDbase caching guide](https://docs.bedbase.org/gtars/bbcache/)
- [GA4GH refget sequences v2](https://ga4gh.github.io/refget/sequences)
- [GA4GH refget sequence collections](https://ga4gh.github.io/refget/seqcols/)

### `references/tokenizers.md`

# Genomic tokenizers and fragment tokenization

Verified against Python `gtars==0.9.2`, wrapper crate `gtars==0.9.0`, and
component `gtars-tokenizers==0.5.3` on **2026-07-23**.

## Current class and constructors

The class is `Tokenizer`, not `TreeTokenizer`:

```python
from gtars.tokenizers import Tokenizer

tokenizer = Tokenizer.from_bed("reviewed-universe.bed")
```

Verified Python signatures:

```text
Tokenizer(path)
Tokenizer.from_config(path)
Tokenizer.from_bed(path)
Tokenizer.from_pretrained(path)
Tokenizer.tokenize(regions)
Tokenizer.encode(tokens)
Tokenizer.decode(ids)
Tokenizer.convert_ids_to_tokens(ids)
Tokenizer.convert_tokens_to_ids(tokens)
Tokenizer.get_vocab()
```

`Tokenizer(path)` auto-detects only `.toml`, `.bed`, and `.bed.gz`. The local
constructors read local files and build an in-memory overlap index.

## Local config

`from_config` expects TOML, not YAML:

```toml
universe = "universe.bed.gz"
tokenizer_type = "bits"
```

The universe path is relative to the config file. `tokenizer_type` is optional
and accepts `bits` or `ailist`; omitted means `bits`. A `special_tokens` array can
override defaults, but its values must be valid region-token strings and all
seven roles must remain compatible with the model. Prefer defaults unless a
pinned model manifest explicitly defines every role.

Default roles are:

```text
unk, pad, mask, cls, bos, eos, sep
```

For a unique N-row universe, the tested implementation has `N + 7` vocabulary
entries. Do not hardcode IDs from another universe.

## Tokenization semantics

```python
from gtars.models import Region, RegionSet
from gtars.tokenizers import Tokenizer

universe_path = "training-universe.bed"
tokenizer = Tokenizer.from_bed(universe_path)

query = RegionSet.from_regions(
    [Region("chr1", 100, 200, None)],
)
tokens = tokenizer.tokenize(query)
batch = tokenizer(query)
input_ids = batch["input_ids"]
attention_mask = batch["attention_mask"]
```

The overlap index returns every universe region overlapping each query region.
A query can therefore produce zero, one, or multiple region tokens; if the
entire call yields no overlap, it returns the unknown token. Unknown contigs also
fall through to unknown behavior.

The verified 0.9.2 wheel rejected a list of strings such as
`["chr1:100-200"]` because the native extractor expected region objects.
Older documentation showing string-list input is not reliable for this pin.
Pass a `RegionSet` or `Region` objects.

Conversion methods:

```python
ids = tokenizer.convert_tokens_to_ids(tokens)
round_trip = tokenizer.convert_ids_to_tokens(ids)
vocabulary = tokenizer.get_vocab()
vocab_size = tokenizer.vocab_size
specials = tokenizer.special_tokens_map
```

`encode()` maps token strings to IDs. Calling the tokenizer on regions performs
region overlap tokenization plus encoding. These are different stages.

## Universe compatibility is byte/order sensitive

Token IDs depend on the exact universe rows, their order, duplicate policy,
special-token assignment, and backend/config. Assembly labels alone are
insufficient.

Record this manifest before training or inference:

```json
{
  "schema_version": "1.0",
  "assembly": "GRCh38.p14",
  "coordinate_system": "0-based-half-open",
  "gtars_python_version": "0.9.2",
  "universe": {
    "sha256": "<64 lowercase hex>",
    "records": 100000,
    "chrom_sizes_sha256": "<64 lowercase hex>"
  },
  "tokenizer": {
    "backend": "bits",
    "vocab_size": 100007,
    "special_token_ids": {
      "unk": 100000,
      "pad": 100001,
      "mask": 100002,
      "cls": 100003,
      "bos": 100004,
      "eos": 100005,
      "sep": 100006
    }
  }
}
```

The numbers above illustrate the schema, not guaranteed default ID order.
Generate the values from the reviewed local tokenizer.

Validate without importing gtars:

```bash
python3 -B scripts/tokenizer_manifest.py \
  --manifest tokenizer-manifest.json \
  --universe universe.bed \
  --assembly GRCh38.p14 \
  --chrom-sizes GRCh38.p14.chrom.sizes
```

The helper requires exact SHA-256 and record count, seven distinct in-range
special IDs, compatible assembly/coordinates/version, and a unique valid BED.

## `from_pretrained` is network-capable

Tagged source implements:

1. if `path` exists locally, append `universe.bed.gz`;
2. otherwise construct a synchronous Hugging Face Hub client;
3. fetch `universe.bed.gz` from the named model repository into the Hub cache.

The Python signature exposes no `revision`, `cache_dir`, `local_files_only`, or
expected checksum. Therefore:

- do not call `Tokenizer.from_pretrained("owner/model")` by default;
- obtain approval for `huggingface.co`, repository, exact commit/revision,
  transfer size, cache path, and metadata disclosure;
- fetch through a reviewed revision-pinning mechanism;
- verify SHA-256 and manifest;
- present an existing local directory containing the reviewed
  `universe.bed.gz`.

No remote model code is needed for a universe file; never enable remote code.

## Fragment tokenization

Current Python binding:

```python
from gtars.tokenizers import Tokenizer, tokenize_fragment_file

tokenizer = Tokenizer.from_bed("training-universe.bed")
by_barcode = tokenize_fragment_file("fragments.tsv.gz", tokenizer)
# dict[str, list[int]]
```

Tagged implementation requires at least five whitespace-separated fields:

```text
chrom  start  end  barcode  count
```

It uses chromosome/start/end/barcode, but does **not** use the fifth count field.
Each input row contributes its overlapping token IDs once, and duplicate IDs are
retained in each barcode list. This can differ from expanding a fragment-support
count. Validate that this is the intended weighting.

The function accumulates all barcodes and token lists in memory. Set caps on
compressed and expanded bytes, rows, distinct barcodes, tokens per row, total
tokens, and process RSS before using it on single-cell data. Never print raw
barcodes.

For count matrices, the CLI's `fscoring --barcode` path uses a separate sparse
count implementation and writes Matrix Market outputs; see `cli.md`.

## Split leakage

Fit universes and tokenizers only from training patients/donors. All technical
and biological replicates from one patient must stay in one split. A universe
derived from all peaks leaks held-out locus support even if the model weights are
trained later.

Freeze and hash:

- patient/replicate split manifest;
- training-only BED inputs;
- consensus/universe BED and chromosome sizes;
- tokenizer manifest and special IDs;
- tokenized corpus schema and checksum;
- package/artifact versions.

Do not tune unknown handling, universe support threshold, backend, or special
tokens on validation/test outcomes more than the declared selection protocol
allows.

## Rust API

```toml
[dependencies]
gtars = { version = "=0.9.0", default-features = false, features = ["tokenizers"] }
```

The wrapper exposes:

```rust
use gtars::tokenizers::Tokenizer;

let tokenizer = Tokenizer::from_bed("universe.bed")?;
let tokens = tokenizer.tokenize(&regions)?;
let ids = tokenizer.encode(&regions)?;
```

Rust also supports `from_config`, `from_auto`, and—because the wrapper enables
the `huggingface` feature—`from_pretrained`. Apply the same local-first and
revision/checksum gate.

## Removed stale claims

The current API does not provide `TreeTokenizer.from_bed_file`,
`from_region_string`, YAML tokenizer config, token objects with `.metadata`, or
the old CLI `tokenize` command in `gtars-cli 0.9.0`.

## Official sources (accessed 2026-07-23)

- [Gtars tokenizer guide](https://docs.bedbase.org/gtars/tokenizers/)
- [Python 0.9.2 tokenizer stubs](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/py_src/gtars/tokenizers/__init__.pyi)
- [Python 0.9.2 tokenizer binding](https://github.com/databio/gtars/blob/gtars-python-v0.9.2/gtars-python/src/tokenizers/py_tokenizers/mod.rs)
- [Tokenizer implementation at v0.9.0](https://github.com/databio/gtars/blob/v0.9.0/gtars-tokenizers/src/tokenizer.rs)
- [Tokenizer TOML schema at v0.9.0](https://github.com/databio/gtars/blob/v0.9.0/gtars-tokenizers/src/config.rs)
- [Fragment tokenizer source at v0.9.0](https://github.com/databio/gtars/blob/v0.9.0/gtars-tokenizers/src/utils/fragments.rs)

### `scripts/__init__.py`

```python
"""Dependency-free local helpers for the Gtars skill."""
```

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared dependency-free safety helpers for local Gtars skill CLIs."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import stat
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator


HARD_MAX_BYTES = 8 * 1024**3
HARD_MAX_RECORDS = 10_000_000
HARD_MAX_FILES = 100_000
HARD_MAX_WORKERS = 256
HARD_MAX_LINE_BYTES = 1024 * 1024
MAX_COORDINATE = 2**32 - 1

_SCHEMES = (
    "http:",
    "https:",
    "ftp:",
    "file:",
    "s3:",
    "gs:",
    "hf:",
    "ssh:",
)
_INTEGER = re.compile(r"^(?:0|[1-9][0-9]*)$")
_VALID_STRANDS = {"+", "-", "."}


class SafetyError(ValueError):
    """Raised when a local-input safety contract is violated."""


def bounded_int(
    value: str,
    *,
    minimum: int = 0,
    maximum: int,
    label: str,
) -> int:
    """Parse an integer while enforcing an explicit hard bound."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be an integer") from exc
    if parsed < minimum or parsed > maximum:
        raise argparse.ArgumentTypeError(
            f"{label} must be between {minimum} and {maximum}"
        )
    return parsed


def int_type(*, minimum: int = 0, maximum: int, label: str):
    """Return an argparse-compatible bounded integer parser."""

    def parse(value: str) -> int:
        return bounded_int(
            value,
            minimum=minimum,
            maximum=maximum,
            label=label,
        )

    return parse


def _reject_unsafe_text_path(raw: str) -> None:
    if not raw or "\x00" in raw:
        raise SafetyError("path must be nonempty and contain no NUL byte")
    lowered = raw.strip().lower()
    if lowered.startswith(_SCHEMES) or "://" in lowered:
        raise SafetyError("URLs and URI-like paths are not allowed")
    if raw.startswith("~"):
        raise SafetyError("home expansion is not allowed; pass an explicit path")
    if ".." in Path(raw).parts:
        raise SafetyError("parent traversal ('..') is not allowed")


def _reject_symlink_components(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise SafetyError("symlink path component is not allowed")


def local_path(
    raw: str,
    *,
    must_exist: bool = True,
    kind: str = "any",
) -> Path:
    """Resolve a strict local path without following symlinks."""
    _reject_unsafe_text_path(raw)
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    candidate = Path(os.path.abspath(candidate))
    _reject_symlink_components(candidate)

    try:
        mode = candidate.lstat().st_mode
    except FileNotFoundError:
        if must_exist:
            raise SafetyError("required local path does not exist")
        parent = candidate.parent
        try:
            parent_mode = parent.lstat().st_mode
        except FileNotFoundError as exc:
            raise SafetyError("output parent does not exist") from exc
        if not stat.S_ISDIR(parent_mode):
            raise SafetyError("output parent is not a directory")
        return candidate

    if stat.S_ISLNK(mode):
        raise SafetyError("symlinks are not allowed")
    if kind == "file" and not stat.S_ISREG(mode):
        raise SafetyError("expected a regular file")
    if kind == "dir" and not stat.S_ISDIR(mode):
        raise SafetyError("expected a directory")
    if kind == "any" and not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
        raise SafetyError("only regular files and directories are allowed")
    return candidate


def _open_binary_nofollow(path: Path):
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    mode = os.fstat(descriptor).st_mode
    if not stat.S_ISREG(mode):
        os.close(descriptor)
        raise SafetyError("expected a regular file")
    return os.fdopen(descriptor, "rb")


def iter_text_lines(
    path: Path,
    *,
    max_bytes: int,
    max_records: int,
    max_line_bytes: int = HARD_MAX_LINE_BYTES,
) -> Iterator[tuple[int, str]]:
    """Yield bounded UTF-8 lines from a local plain-text or gzip file."""
    if not 1 <= max_bytes <= HARD_MAX_BYTES:
        raise SafetyError("max_bytes is outside the hard safety bound")
    if not 1 <= max_records <= HARD_MAX_RECORDS:
        raise SafetyError("max_records is outside the hard safety bound")
    if not 1 <= max_line_bytes <= HARD_MAX_LINE_BYTES:
        raise SafetyError("max_line_bytes is outside the hard safety bound")
    if path.stat().st_size > max_bytes:
        raise SafetyError("compressed/input file exceeds byte limit")

    expanded = 0
    with _open_binary_nofollow(path) as raw_handle:
        stream = (
            gzip.GzipFile(fileobj=raw_handle, mode="rb")
            if path.name.lower().endswith(".gz")
            else raw_handle
        )
        try:
            for line_number, raw_line in enumerate(stream, start=1):
                if line_number > max_records:
                    raise SafetyError("record limit exceeded")
                if len(raw_line) > max_line_bytes:
                    raise SafetyError(f"line {line_number} exceeds line-size limit")
                expanded += len(raw_line)
                if expanded > max_bytes:
                    raise SafetyError("expanded text exceeds byte limit")
                if b"\x00" in raw_line:
                    raise SafetyError(f"NUL byte found at line {line_number}")
                try:
                    line = raw_line.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise SafetyError(
                        f"input is not UTF-8 near line {line_number}"
                    ) from exc
                yield line_number, line.rstrip("\r\n")
        finally:
            if stream is not raw_handle:
                stream.close()


def sha256_file(path: Path, *, max_bytes: int) -> tuple[str, int]:
    """Hash a bounded regular file without following symlinks."""
    if not 1 <= max_bytes <= HARD_MAX_BYTES:
        raise SafetyError("max_bytes is outside the hard safety bound")
    digest = hashlib.sha256()
    total = 0
    with _open_binary_nofollow(path) as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise SafetyError("file exceeds hash byte limit")
            digest.update(chunk)
    return digest.hexdigest(), total


def load_json(path: Path, *, max_bytes: int) -> Any:
    """Load strict bounded JSON, rejecting duplicate keys and non-finite values."""
    text = "\n".join(
        line
        for _, line in iter_text_lines(
            path,
            max_bytes=max_bytes,
            max_records=min(HARD_MAX_RECORDS, 1_000_000),
        )
    )

    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise SafetyError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value: str):
        raise SafetyError(f"non-finite JSON number is not allowed: {value}")

    try:
        return json.loads(
            text,
            object_pairs_hook=object_pairs,
            parse_constant=invalid_constant,
        )
    except json.JSONDecodeError as exc:
        raise SafetyError("invalid JSON") from exc


def load_chrom_sizes(
    path: Path,
    *,
    max_bytes: int,
    max_records: int,
) -> tuple[dict[str, int], list[str]]:
    """Load a strict two-column chromosome-sizes file."""
    sizes: dict[str, int] = {}
    order: list[str] = []
    for line_number, line in iter_text_lines(
        path,
        max_bytes=max_bytes,
        max_records=max_records,
    ):
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) != 2:
            raise SafetyError(
                f"chromosome-sizes line {line_number} must have two tab fields"
            )
        chrom, size_text = fields
        if (
            not chrom
            or any(character.isspace() or ord(character) < 32 for character in chrom)
            or chrom in sizes
        ):
            raise SafetyError(f"invalid or duplicate contig at line {line_number}")
        if not _INTEGER.fullmatch(size_text):
            raise SafetyError(f"invalid contig size at line {line_number}")
        size = int(size_text)
        if not 1 <= size <= MAX_COORDINATE:
            raise SafetyError(f"contig size out of bounds at line {line_number}")
        sizes[chrom] = size
        order.append(chrom)
    if not sizes:
        raise SafetyError("chromosome-sizes file contains no records")
    return sizes, order


def inspect_bed(
    path: Path,
    *,
    max_bytes: int,
    max_records: int,
    chrom_sizes: dict[str, int] | None = None,
    chrom_order: list[str] | None = None,
    max_examples: int = 10,
) -> dict[str, Any]:
    """Inspect BED-like records without returning genomic coordinates."""
    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    examples: list[dict[str, int | str]] = []
    seen: set[tuple[str, int, int]] = set()
    max_end: dict[str, int] = {}
    records = 0
    skipped = 0
    contigs: set[str] = set()
    min_columns: int | None = None
    max_columns = 0
    unsorted = 0
    duplicates = 0
    overlap_observations = 0
    bed6_rows = 0
    previous_key: tuple[int | str, int, int] | None = None
    order_map = (
        {chrom: index for index, chrom in enumerate(chrom_order)}
        if chrom_order is not None
        else None
    )

    def issue(kind: str, code: str, line_number: int) -> None:
        target = errors if kind == "error" else warnings
        target[code] += 1
        if len(examples) < max_examples:
            examples.append({"severity": kind, "code": code, "line": line_number})

    for line_number, line in iter_text_lines(
        path,
        max_bytes=max_bytes,
        max_records=max_records,
    ):
        if not line:
            skipped += 1
            warnings["blank_line"] += 1
            continue
        if line.startswith(("#", "track", "browser")):
            skipped += 1
            continue
        fields = line.split("\t")
        if len(fields) < 3:
            issue("error", "fewer_than_three_columns", line_number)
            continue
        records += 1
        min_columns = len(fields) if min_columns is None else min(min_columns, len(fields))
        max_columns = max(max_columns, len(fields))
        chrom = fields[0]
        if not chrom or any(
            character.isspace() or ord(character) < 32 for character in chrom
        ):
            issue("error", "invalid_contig", line_number)
            continue
        if not _INTEGER.fullmatch(fields[1]) or not _INTEGER.fullmatch(fields[2]):
            issue("error", "non_unsigned_decimal_coordinate", line_number)
            continue
        start, end = int(fields[1]), int(fields[2])
        if start > MAX_COORDINATE or end > MAX_COORDINATE:
            issue("error", "coordinate_exceeds_gtars_u32", line_number)
            continue
        if end <= start:
            issue(
                "error",
                "zero_length_interval" if end == start else "end_before_start",
                line_number,
            )
            continue
        if chrom_sizes is not None:
            if chrom not in chrom_sizes:
                issue("error", "unknown_contig", line_number)
                continue
            if end > chrom_sizes[chrom]:
                issue("error", "end_beyond_contig", line_number)
                continue
        if len(fields) >= 6:
            bed6_rows += 1
            if fields[5] not in _VALID_STRANDS:
                issue("error", "invalid_bed6_strand", line_number)

        contigs.add(chrom)
        key = (chrom, start, end)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
        prior_end = max_end.get(chrom)
        if prior_end is not None and start < prior_end:
            overlap_observations += 1
        max_end[chrom] = max(end, prior_end or end)

        sort_key: tuple[int | str, int, int]
        if order_map is None:
            sort_key = (chrom, start, end)
        else:
            sort_key = (order_map[chrom], start, end)
        if previous_key is not None and sort_key < previous_key:
            unsorted += 1
        previous_key = sort_key

    if duplicates:
        warnings["duplicate_intervals"] = duplicates
    if overlap_observations:
        warnings["overlapping_intervals"] = overlap_observations
    if unsorted:
        warnings["out_of_order_records"] = unsorted
    if chrom_sizes is None:
        warnings["bounds_not_checked_without_chrom_sizes"] += 1

    digest, size = sha256_file(path, max_bytes=max_bytes)
    return {
        "sha256": digest,
        "size_bytes": size,
        "records": records,
        "skipped_records": skipped,
        "contig_count": len(contigs),
        "minimum_columns": min_columns,
        "maximum_columns": max_columns if records else None,
        "bed6_or_wider_rows": bed6_rows,
        "duplicate_intervals": duplicates,
        "overlap_observations": overlap_observations,
        "out_of_order_records": unsorted,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "issue_examples": examples,
    }


def add_path_mode_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--path-mode",
        choices=("redacted", "basename", "full"),
        default="redacted",
        help="Path disclosure in output (default: redacted).",
    )


def display_path(path: Path, index: int, mode: str) -> str:
    """Render a path using the requested disclosure level."""
    if mode == "redacted":
        return f"file_{index:04d}"
    if mode == "basename":
        return path.name
    if mode == "full":
        return str(path)
    raise SafetyError(f"unknown path mode: {mode}")


def print_json(payload: dict[str, Any]) -> None:
    """Print deterministic JSON with no non-finite values."""
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, allow_nan=False)
    sys.stdout.write("\n")


def fail_json(tool: str, exc: Exception) -> int:
    """Emit a bounded machine-readable error."""
    print_json(
        {
            "ok": False,
            "tool": tool,
            "error": type(exc).__name__,
            "message": str(exc)[:500],
        }
    )
    return 2
```

### `scripts/artifact_inspector.py`

```python
#!/usr/bin/env python3
"""Hash and classify local Gtars artifacts without loading or executing them."""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from email.parser import Parser
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_FILES,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    int_type,
    iter_text_lines,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-artifact-inspector"
_WHEEL = re.compile(r"^gtars-(\d+\.\d+\.\d+)-.+\.whl$")
_CRATE = re.compile(r"^(gtars|gtars-cli)-(\d+\.\d+\.\d+)\.crate$")
_CHECKSUM = re.compile(r"^([0-9a-fA-F]{64})[ \t]+[* ]?([^/\\]+)$")
_ARCHIVES = (".tar.gz", ".tgz", ".zip", ".crate", ".whl")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory, hash, and version-screen local Gtars wheels, crates, "
            "release archives, native extensions, binaries, or METADATA files. "
            "Archives are not extracted and code is never loaded or executed."
        )
    )
    parser.add_argument(
        "--artifact",
        action="append",
        required=True,
        help="Local regular file; repeat for multiple artifacts.",
    )
    parser.add_argument("--checksum-manifest", help="Local SHA256SUMS-style file.")
    parser.add_argument("--expected-python-version", default="0.9.2")
    parser.add_argument("--expected-rust-version", default="0.9.0")
    parser.add_argument("--expected-cli-version", default="0.9.0")
    parser.add_argument(
        "--max-files",
        type=int_type(minimum=1, maximum=HARD_MAX_FILES, label="max-files"),
        default=1_000,
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-file-bytes",
        ),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-total-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-total-bytes",
        ),
        default=4 * 1024**3,
    )
    add_path_mode_argument(parser)
    return parser


def _read_prefix(path: Path, length: int = 16) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise SafetyError("artifact must be a regular file")
        return os.read(descriptor, length)
    finally:
        os.close(descriptor)


def _native_format(prefix: bytes) -> str | None:
    if prefix.startswith(b"\x7fELF"):
        return "elf"
    if prefix.startswith(b"MZ"):
        return "portable-executable"
    if prefix[:4] in {
        b"\xfe\xed\xfa\xce",
        b"\xce\xfa\xed\xfe",
        b"\xfe\xed\xfa\xcf",
        b"\xcf\xfa\xed\xfe",
        b"\xca\xfe\xba\xbe",
        b"\xbe\xba\xfe\xca",
    }:
        return "mach-o"
    return None


def _parse_metadata(path: Path, max_bytes: int) -> dict[str, str | None]:
    text = "\n".join(
        line
        for _, line in iter_text_lines(
            path,
            max_bytes=max_bytes,
            max_records=100_000,
        )
    )
    message = Parser().parsestr(text)
    return {
        "name": message.get("Name"),
        "version": message.get("Version"),
        "requires_python": message.get("Requires-Python"),
    }


def _read_checksums(
    path: Path,
    *,
    max_bytes: int,
    max_files: int,
) -> dict[str, str]:
    expected: dict[str, str] = {}
    for line_number, line in iter_text_lines(
        path,
        max_bytes=max_bytes,
        max_records=max_files + 100,
    ):
        if not line or line.startswith("#"):
            continue
        match = _CHECKSUM.fullmatch(line)
        if match is None:
            raise SafetyError(f"invalid checksum line {line_number}")
        digest, name = match.groups()
        if name in expected:
            raise SafetyError(f"duplicate checksum entry at line {line_number}")
        expected[name] = digest.lower()
        if len(expected) > max_files:
            raise SafetyError("checksum manifest exceeds max-files")
    return expected


def inspect(args: argparse.Namespace) -> tuple[dict, int]:
    if len(args.artifact) > args.max_files:
        raise SafetyError("artifact count exceeds max-files")
    paths = [local_path(raw, kind="file") for raw in args.artifact]
    if len({str(path) for path in paths}) != len(paths):
        raise SafetyError("duplicate artifact path")

    checksum_path = None
    checksums: dict[str, str] = {}
    checksum_report = None
    if args.checksum_manifest:
        checksum_path = local_path(args.checksum_manifest, kind="file")
        checksums = _read_checksums(
            checksum_path,
            max_bytes=min(args.max_file_bytes, 64 * 1024**2),
            max_files=args.max_files,
        )

    errors: dict[str, int] = {}
    warnings: dict[str, int] = {}
    summaries: list[dict] = []
    total = 0
    verified = 0

    for index, path in enumerate(paths, start=1):
        digest, size = sha256_file(path, max_bytes=args.max_file_bytes)
        total += size
        if total > args.max_total_bytes:
            raise SafetyError("artifacts exceed max-total-bytes")
        name = path.name
        prefix = _read_prefix(path)
        native = _native_format(prefix)
        kind = "data-or-metadata"
        version = None
        package = None
        metadata = None

        wheel_match = _WHEEL.fullmatch(name)
        crate_match = _CRATE.fullmatch(name)
        if wheel_match:
            kind = "python-wheel-native-code"
            package = "gtars"
            version = wheel_match.group(1)
            if version != args.expected_python_version:
                errors["python_version_mismatch"] = (
                    errors.get("python_version_mismatch", 0) + 1
                )
        elif crate_match:
            kind = "cargo-crate-archive"
            package, version = crate_match.groups()
            expected = (
                args.expected_cli_version
                if package == "gtars-cli"
                else args.expected_rust_version
            )
            if version != expected:
                errors[f"{package}_version_mismatch"] = (
                    errors.get(f"{package}_version_mismatch", 0) + 1
                )
        elif name == "METADATA":
            kind = "python-distribution-metadata"
            metadata = _parse_metadata(path, min(args.max_file_bytes, 16 * 1024**2))
            package = metadata["name"]
            version = metadata["version"]
            if package != "gtars":
                errors["metadata_package_name_mismatch"] = 1
            if version != args.expected_python_version:
                errors["metadata_python_version_mismatch"] = 1
            if metadata["requires_python"] != ">=3.10":
                warnings["metadata_requires_python_differs_from_snapshot"] = 1
        elif native is not None:
            kind = "native-executable-code"
            warnings["native_version_not_verified_without_execution"] = (
                warnings.get("native_version_not_verified_without_execution", 0) + 1
            )
        elif name.endswith(_ARCHIVES):
            kind = "archive-not-extracted"
            warnings["archive_contents_not_inspected"] = (
                warnings.get("archive_contents_not_inspected", 0) + 1
            )

        expected_digest = checksums.get(name)
        checksum_ok = expected_digest == digest if expected_digest is not None else None
        if checksum_ok:
            verified += 1
        elif checksum_ok is False:
            errors["checksum_mismatch"] = errors.get("checksum_mismatch", 0) + 1
        elif checksums:
            warnings["artifact_missing_from_checksum_manifest"] = (
                warnings.get("artifact_missing_from_checksum_manifest", 0) + 1
            )

        summaries.append(
            {
                "path": display_path(path, index, args.path_mode),
                "basename": name if args.path_mode != "redacted" else None,
                "sha256": digest,
                "size_bytes": size,
                "kind": kind,
                "native_format": native,
                "package": package,
                "version": version,
                "metadata": metadata,
                "checksum_verified": checksum_ok,
                "loaded": False,
                "executed": False,
                "extracted": False,
            }
        )

    if checksum_path is not None:
        manifest_digest, manifest_size = sha256_file(
            checksum_path,
            max_bytes=min(args.max_file_bytes, 64 * 1024**2),
        )
        checksum_report = {
            "path": display_path(
                checksum_path,
                len(paths) + 1,
                args.path_mode,
            ),
            "sha256": manifest_digest,
            "size_bytes": manifest_size,
            "entries": len(checksums),
            "verified_artifacts": verified,
        }

    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "network_used": False,
            "packages_imported": False,
            "native_code_loaded": False,
            "artifacts_executed": False,
            "archives_extracted": False,
            "symlinks_allowed": False,
        },
        "expected_versions": {
            "python": args.expected_python_version,
            "rust_meta_crate": args.expected_rust_version,
            "cli": args.expected_cli_version,
        },
        "summary": {
            "artifact_count": len(paths),
            "total_bytes": total,
            "checksum_verified_count": verified,
        },
        "checksum_manifest": checksum_report,
        "artifacts": summaries,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "trust_gate": [
            "accept only an approved official source and immutable release",
            "verify the artifact SHA-256 against an independently obtained value",
            "do not run untrusted binaries or Cargo build scripts",
            "load or execute only in isolation with CPU, RAM, disk, and time limits",
            "after trust approval, verify gtars --version or gtars.__version__",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, status = inspect(args)
        print_json(report)
        return status
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/bed_validator.py`

```python
#!/usr/bin/env python3
"""Validate a local BED file without rewriting or uploading it."""

from __future__ import annotations

import argparse
import sys

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    inspect_bed,
    int_type,
    load_chrom_sizes,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-bed-validator"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate one local BED/BED.GZ file as 0-based half-open intervals. "
            "No input is rewritten and no network operation is available."
        )
    )
    parser.add_argument("--input", required=True, help="Local BED or BED.GZ file.")
    parser.add_argument(
        "--assembly",
        required=True,
        help="Declared reference assembly/accession for the report.",
    )
    parser.add_argument(
        "--chrom-sizes",
        help="Local two-column chrom.sizes file for contig and bounds checks.",
    )
    parser.add_argument(
        "--require-sorted",
        action="store_true",
        help="Fail if rows are not in chrom.sizes order then numeric start/end.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow a BED with no data records.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=512 * 1024**2,
        help="Compressed and expanded byte cap (default: 512 MiB).",
    )
    parser.add_argument(
        "--max-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-records",
        ),
        default=1_000_000,
    )
    parser.add_argument(
        "--max-examples",
        type=int_type(minimum=0, maximum=100, label="max-examples"),
        default=10,
    )
    add_path_mode_argument(parser)
    return parser


def validate(args: argparse.Namespace) -> tuple[dict, int]:
    assembly = args.assembly.strip()
    if not assembly or len(assembly) > 200:
        raise SafetyError("assembly must contain 1-200 characters")

    bed_path = local_path(args.input, kind="file")
    chrom_sizes = None
    chrom_order = None
    chrom_sizes_report = None
    if args.chrom_sizes:
        chrom_path = local_path(args.chrom_sizes, kind="file")
        chrom_sizes, chrom_order = load_chrom_sizes(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
            max_records=min(args.max_records, 1_000_000),
        )
        chrom_digest, chrom_bytes = sha256_file(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
        )
        chrom_sizes_report = {
            "path": display_path(chrom_path, 2, args.path_mode),
            "sha256": chrom_digest,
            "size_bytes": chrom_bytes,
            "contig_count": len(chrom_sizes),
        }

    summary = inspect_bed(
        bed_path,
        max_bytes=args.max_bytes,
        max_records=args.max_records,
        chrom_sizes=chrom_sizes,
        chrom_order=chrom_order,
        max_examples=args.max_examples,
    )
    errors = dict(summary.pop("errors"))
    warnings = dict(summary.pop("warnings"))
    examples = summary.pop("issue_examples")
    if summary["records"] == 0 and not args.allow_empty:
        errors["no_data_records"] = 1
    if args.require_sorted and summary["out_of_order_records"]:
        errors["sorting_required"] = summary["out_of_order_records"]

    plan: list[dict[str, str]] = [
        {
            "action": "preserve_coordinate_contract",
            "detail": "BED is 0-based, start-inclusive, end-exclusive",
        },
        {
            "action": "preserve_assembly_and_contig_names",
            "detail": "do not rename contigs or liftover implicitly",
        },
    ]
    if chrom_sizes is None:
        plan.append(
            {
                "action": "supply_chromosome_sizes",
                "detail": "required before contig and interval-bound validation",
            }
        )
    if summary["out_of_order_records"]:
        plan.append(
            {
                "action": "stable_sort_a_copy",
                "detail": "chrom.sizes order, numeric start, numeric end; retain original",
            }
        )

    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": assembly,
            "coordinate_system": "0-based-half-open",
            "input_mutated": False,
            "network_used": False,
            "subprocess_used": False,
            "symlinks_allowed": False,
            "gtars_coordinate_limit": "u32",
        },
        "input": {
            "path": display_path(bed_path, 1, args.path_mode),
            **summary,
        },
        "chromosome_sizes": chrom_sizes_report,
        "errors": errors,
        "warnings": warnings,
        "issue_examples": examples,
        "normalization_plan": plan,
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, status = validate(args)
        print_json(report)
        return status
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/coverage_preflight.py`

```python
#!/usr/bin/env python3
"""Preflight local Gtars uniwig coverage and bigWig generation."""

from __future__ import annotations

import argparse
import math
import sys

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    HARD_MAX_WORKERS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    inspect_bed,
    int_type,
    load_chrom_sizes,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-coverage-preflight"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check a sorted local BED/narrowPeak input, chromosome sizes, bounds, "
            "and output budget for gtars uniwig 0.9.0. Nothing is generated."
        )
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--input-type", choices=("bed", "narrowpeak"), default="bed")
    parser.add_argument("--chrom-sizes", required=True)
    parser.add_argument("--assembly", required=True)
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument(
        "--output-type",
        choices=("bw", "wig", "bedgraph", "npy"),
        default="bw",
    )
    parser.add_argument(
        "--count-type",
        choices=("start", "end", "core", "all"),
        default="core",
    )
    parser.add_argument(
        "--smooth-size",
        type=int_type(minimum=1, maximum=10_000_000, label="smooth-size"),
        default=5,
    )
    parser.add_argument(
        "--step-size",
        type=int_type(minimum=1, maximum=10_000_000, label="step-size"),
        default=1,
    )
    parser.add_argument(
        "--threads",
        type=int_type(minimum=1, maximum=HARD_MAX_WORKERS, label="threads"),
        default=1,
    )
    parser.add_argument(
        "--zoom",
        type=int_type(minimum=0, maximum=10_000, label="zoom"),
        default=1,
    )
    parser.add_argument(
        "--streaming",
        action="store_true",
        help="Use BED streaming; only wig/bedgraph output is supported upstream.",
    )
    parser.add_argument(
        "--dense",
        type=int_type(minimum=-1, maximum=MAX_DENSE_GAP, label="dense"),
        default=100,
        help="Streaming gap fill: 0 sparse, -1 fully dense, N fills gaps <=N.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-records",
        ),
        default=5_000_000,
    )
    parser.add_argument(
        "--max-estimated-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-estimated-bytes",
        ),
        default=4 * 1024**3,
        help="Planning cap for dense uncompressed coverage values.",
    )
    add_path_mode_argument(parser)
    return parser


MAX_DENSE_GAP = 10_000_000


def preflight(args: argparse.Namespace) -> tuple[dict, int]:
    assembly = args.assembly.strip()
    if not assembly or len(assembly) > 200:
        raise SafetyError("assembly must contain 1-200 characters")
    input_path = local_path(args.input, kind="file")
    chrom_path = local_path(args.chrom_sizes, kind="file")
    output_prefix = local_path(args.output_prefix, must_exist=False)

    chrom_sizes, chrom_order = load_chrom_sizes(
        chrom_path,
        max_bytes=min(args.max_bytes, 128 * 1024**2),
        max_records=min(args.max_records, 1_000_000),
    )
    chrom_digest, chrom_bytes = sha256_file(
        chrom_path,
        max_bytes=min(args.max_bytes, 128 * 1024**2),
    )
    bed = inspect_bed(
        input_path,
        max_bytes=args.max_bytes,
        max_records=args.max_records,
        chrom_sizes=chrom_sizes,
        chrom_order=chrom_order,
    )
    errors: dict[str, int] = dict(bed["errors"])
    warnings: dict[str, int] = {}
    if bed["records"] == 0:
        errors["no_data_records"] = 1
    if bed["out_of_order_records"]:
        errors["sorting_required"] = bed["out_of_order_records"]
    if args.input_type == "narrowpeak" and (bed["minimum_columns"] or 0) < 10:
        errors["narrowpeak_requires_ten_columns"] = 1
    if output_prefix.exists():
        errors["output_prefix_already_exists"] = 1
    if args.streaming and args.output_type not in {"wig", "bedgraph"}:
        errors["streaming_output_type_unsupported"] = 1
    if args.streaming and args.input_type != "bed":
        errors["streaming_requires_bed_input"] = 1

    count_outputs = 3 if args.count_type == "all" else 1
    genome_span = sum(chrom_sizes.values())
    estimated_values = math.ceil(genome_span / args.step_size) * count_outputs
    estimated_uncompressed_bytes = estimated_values * 8
    if estimated_uncompressed_bytes > args.max_estimated_bytes:
        errors["estimated_dense_coverage_exceeds_budget"] = 1
    if args.threads > 1:
        warnings["parallel_memory_may_scale_with_threads"] = args.threads
    if args.output_type == "bw":
        warnings["bigwig_size_is_data_dependent_estimate_is_not_file_size"] = 1
    if args.streaming and args.dense == -1:
        warnings["fully_dense_streaming_requested"] = 1

    argv = [
        "gtars",
        "uniwig",
        "--file",
        "<input>",
        "--filetype",
        args.input_type,
        "--chromref",
        "<chrom-sizes>",
        "--smoothsize",
        str(args.smooth_size),
        "--stepsize",
        str(args.step_size),
        "--fileheader",
        "<output-prefix>",
        "--outputtype",
        args.output_type,
        "--counttype",
        args.count_type,
    ]
    if args.streaming:
        argv.extend(["--streaming", "--dense", str(args.dense)])
    else:
        argv.extend(["--threads", str(args.threads), "--zoom", str(args.zoom)])

    report = {
        "ok": not errors,
        "ready_to_execute": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": assembly,
            "coordinate_system": "0-based-half-open",
            "gtars_cli_version": "0.9.0",
            "commands_executed": False,
            "files_written": False,
            "network_used": False,
            "symlinks_allowed": False,
        },
        "input": {
            "path": display_path(input_path, 1, args.path_mode),
            "sha256": bed["sha256"],
            "size_bytes": bed["size_bytes"],
            "records": bed["records"],
            "minimum_columns": bed["minimum_columns"],
            "out_of_order_records": bed["out_of_order_records"],
        },
        "chromosome_sizes": {
            "path": display_path(chrom_path, 2, args.path_mode),
            "sha256": chrom_digest,
            "size_bytes": chrom_bytes,
            "contig_count": len(chrom_sizes),
            "total_span": genome_span,
        },
        "output": {
            "prefix": display_path(output_prefix, 3, args.path_mode),
            "type": args.output_type,
            "count_type": args.count_type,
        },
        "resource_estimate": {
            "step_size": args.step_size,
            "count_outputs": count_outputs,
            "dense_value_upper_bound": estimated_values,
            "uncompressed_bytes_proxy": estimated_uncompressed_bytes,
            "budget_bytes": args.max_estimated_bytes,
            "not_a_bigwig_size_prediction": True,
        },
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "argv_template": argv,
        "approval_gate": [
            "review the sorted/bounds report and assembly checksum",
            "pilot one bounded contig or small synthetic BED first",
            "set CPU, RAM, disk, and wall-time limits before running",
            "inspect the resulting bigWig header and chromosome dictionary",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, status = preflight(args)
        print_json(report)
        return status
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/execution_plan.py`

```python
#!/usr/bin/env python3
"""Build a bounded local Gtars overlap/coverage execution plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    HARD_MAX_WORKERS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    inspect_bed,
    int_type,
    load_chrom_sizes,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-execution-plan"
GTARS_CLI_VERSION = "0.9.0"
GTARS_PYTHON_VERSION = "0.9.2"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate local inputs and emit a fixed Gtars 0.9 execution plan. "
            "The helper never imports gtars or runs a subprocess."
        )
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=("overlap", "count", "coverage", "consensus", "fragment-score"),
    )
    parser.add_argument("--assembly", required=True)
    parser.add_argument("--query", help="Query BED or fragment file.")
    parser.add_argument("--universe", help="Universe/consensus BED file.")
    parser.add_argument(
        "--input",
        action="append",
        default=[],
        help="Consensus input BED; repeat at least twice.",
    )
    parser.add_argument("--chrom-sizes", help="Local chromosome-sizes file.")
    parser.add_argument("--output", help="Planned local output or output prefix.")
    parser.add_argument("--backend", choices=("bits", "ailist"), default="bits")
    parser.add_argument(
        "--coverage-format",
        choices=("bw", "wig", "bedgraph", "npy"),
        default="bw",
    )
    parser.add_argument(
        "--coverage-streaming",
        action="store_true",
        help="Plan O(smooth-size) BED streaming; only wig/bedgraph are supported.",
    )
    parser.add_argument(
        "--smooth-size",
        type=int_type(minimum=1, maximum=10_000_000, label="smooth-size"),
        default=5,
    )
    parser.add_argument(
        "--step-size",
        type=int_type(minimum=1, maximum=10_000_000, label="step-size"),
        default=1,
    )
    parser.add_argument(
        "--count-type",
        choices=("start", "end", "core", "all"),
        default="core",
    )
    parser.add_argument(
        "--threads",
        type=int_type(minimum=1, maximum=HARD_MAX_WORKERS, label="threads"),
        default=1,
    )
    parser.add_argument(
        "--min-count",
        type=int_type(minimum=1, maximum=1_000_000, label="min-count"),
        default=1,
    )
    parser.add_argument("--scoring-mode", choices=("atac", "chip"), default="atac")
    parser.add_argument(
        "--barcode",
        action="store_true",
        help="Plan fscoring sparse barcode mode.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=1024**3,
    )
    parser.add_argument(
        "--max-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-records",
        ),
        default=2_000_000,
    )
    add_path_mode_argument(parser)
    return parser


def _require(value: str | None, option: str) -> str:
    if value is None:
        raise SafetyError(f"{option} is required for this operation")
    return value


def _output(raw: str | None) -> Path:
    return local_path(_require(raw, "--output"), must_exist=False)


def build_plan(args: argparse.Namespace) -> tuple[dict, int]:
    assembly = args.assembly.strip()
    if not assembly or len(assembly) > 200:
        raise SafetyError("assembly must contain 1-200 characters")

    chrom_sizes = None
    chrom_order = None
    chrom_report = None
    if args.chrom_sizes:
        chrom_path = local_path(args.chrom_sizes, kind="file")
        chrom_sizes, chrom_order = load_chrom_sizes(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
            max_records=min(args.max_records, 1_000_000),
        )
        digest, size = sha256_file(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
        )
        chrom_report = {
            "path": display_path(chrom_path, 1, args.path_mode),
            "sha256": digest,
            "size_bytes": size,
            "contig_count": len(chrom_sizes),
        }

    inputs: list[dict] = []
    errors: dict[str, int] = {}
    next_index = 2

    def add_bed(raw: str, role: str, *, sorted_required: bool = False) -> Path:
        nonlocal next_index
        path = local_path(raw, kind="file")
        summary = inspect_bed(
            path,
            max_bytes=args.max_bytes,
            max_records=args.max_records,
            chrom_sizes=chrom_sizes,
            chrom_order=chrom_order,
        )
        for code, count in summary["errors"].items():
            errors[f"{role}:{code}"] = count
        if summary["records"] == 0:
            errors[f"{role}:no_data_records"] = 1
        if sorted_required and summary["out_of_order_records"]:
            errors[f"{role}:sorting_required"] = summary["out_of_order_records"]
        inputs.append(
            {
                "role": role,
                "path": display_path(path, next_index, args.path_mode),
                "sha256": summary["sha256"],
                "size_bytes": summary["size_bytes"],
                "records": summary["records"],
                "minimum_columns": summary["minimum_columns"],
                "out_of_order_records": summary["out_of_order_records"],
            }
        )
        next_index += 1
        return path

    operation = args.operation
    plan: dict[str, object]
    output_report = None

    if operation in {"overlap", "count"}:
        add_bed(_require(args.query, "--query"), "query")
        add_bed(_require(args.universe, "--universe"), "universe")
        if operation == "overlap":
            plan = {
                "interface": "cli",
                "argv_template": [
                    "gtars",
                    "overlaprs",
                    "--query",
                    "<query-bed>",
                    "--universe",
                    "<universe-bed>",
                    "--backend",
                    args.backend,
                ],
                "stdout": (
                    "one BED3 universe-hit row per overlap; query IDs and counts "
                    "are not emitted"
                ),
            }
        else:
            plan = {
                "interface": "python",
                "imports": ["from gtars.models import RegionSet"],
                "call": "query.count_overlaps(universe)",
                "return": "one integer per query region",
            }
    elif operation == "coverage":
        if chrom_sizes is None:
            raise SafetyError("--chrom-sizes is required for coverage")
        add_bed(_require(args.query, "--query"), "coverage_input", sorted_required=True)
        out = _output(args.output)
        output_report = {
            "path": display_path(out, next_index, args.path_mode),
            "already_exists": out.exists(),
        }
        if out.exists():
            errors["output_already_exists"] = 1
        if args.coverage_streaming and args.coverage_format not in {"wig", "bedgraph"}:
            raise SafetyError(
                "streaming coverage supports only wig or bedgraph, not bw/npy"
            )
        argv = [
            "gtars",
            "uniwig",
            "--file",
            "<coverage-input>",
            "--filetype",
            "bed",
            "--chromref",
            "<chrom-sizes>",
            "--smoothsize",
            str(args.smooth_size),
            "--stepsize",
            str(args.step_size),
            "--fileheader",
            "<output-prefix>",
            "--outputtype",
            args.coverage_format,
            "--counttype",
            args.count_type,
        ]
        if args.coverage_streaming:
            argv.append("--streaming")
        else:
            argv.extend(["--threads", str(args.threads)])
        plan = {
            "interface": "cli",
            "argv_template": argv,
            "note": (
                "batch mode is required for bigWig; run coverage_preflight.py "
                "before approval"
            ),
        }
    elif operation == "consensus":
        if len(args.input) < 2:
            raise SafetyError("consensus requires at least two --input BED files")
        for index, raw in enumerate(args.input, start=1):
            add_bed(raw, f"consensus_{index}")
        out = _output(args.output)
        output_report = {
            "path": display_path(out, next_index, args.path_mode),
            "already_exists": out.exists(),
        }
        if out.exists():
            errors["output_already_exists"] = 1
        plan = {
            "interface": "cli",
            "argv_template": [
                "gtars",
                "consensus",
                "--beds",
                *[f"<bed-{index}>" for index in range(1, len(args.input) + 1)],
                "--min-count",
                str(args.min_count),
                "--output",
                "<output-bed>",
            ],
            "semantics": (
                "reduce the union (including adjacent intervals), then count "
                "input sets having any overlap with each union interval"
            ),
        }
    else:
        fragment = add_bed(_require(args.query, "--query"), "fragments")
        add_bed(_require(args.universe, "--universe"), "consensus")
        fragment_summary = next(item for item in inputs if item["role"] == "fragments")
        if (fragment_summary["minimum_columns"] or 0) < 5:
            errors["fragments:fewer_than_five_columns"] = 1
        out = _output(args.output)
        output_report = {
            "path": display_path(out, next_index, args.path_mode),
            "already_exists": out.exists(),
        }
        if out.exists():
            errors["output_already_exists"] = 1
        argv = [
            "gtars",
            "fscoring",
            "<fragment-file>",
            "<consensus-bed>",
            "--output",
            "<output-or-prefix>",
        ]
        if args.barcode:
            argv.append("--barcode")
        else:
            argv.extend(["--mode", args.scoring_mode])
        plan = {
            "interface": "cli",
            "argv_template": argv,
            "fragment_input_is_single_local_file": fragment.is_file(),
        }

    report = {
        "ok": not errors,
        "ready_to_execute": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": assembly,
            "coordinate_system": "0-based-half-open",
            "gtars_cli_version": GTARS_CLI_VERSION,
            "gtars_python_version": GTARS_PYTHON_VERSION,
            "commands_executed": False,
            "packages_imported": False,
            "network_used": False,
            "files_written": False,
            "symlinks_allowed": False,
        },
        "operation": operation,
        "chromosome_sizes": chrom_report,
        "inputs": inputs,
        "output": output_report,
        "errors": errors,
        "execution_plan": plan,
        "approval_gate": [
            "review checksums, assembly, contigs, sorting, and output collision",
            "set CPU, RAM, disk, file-count, and wall-time limits",
            "run only the exact pinned interface after explicit approval",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, status = build_plan(args)
        print_json(report)
        return status
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/refget_digest_plan.py`

```python
#!/usr/bin/env python3
"""Validate local refget metadata and FASTA sequence digests without networking."""

from __future__ import annotations

import argparse
import base64
import hashlib
import re
import sys
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    int_type,
    iter_text_lines,
    load_json,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-refget-digest-plan"
_SHA512T24U = re.compile(r"^[A-Za-z0-9_-]{32}$")
_MD5 = re.compile(r"^[0-9a-f]{32}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a local refget metadata JSON document and optionally compare "
            "it with a local FASTA. No store is opened and no endpoint is contacted."
        )
    )
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--fasta", help="Optional local FASTA or FASTA.GZ.")
    parser.add_argument("--assembly", required=True)
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-records",
        ),
        default=5_000_000,
        help="Maximum FASTA text lines (default: 5,000,000).",
    )
    add_path_mode_argument(parser)
    return parser


def sha512t24u(sequence: bytes) -> str:
    """Return the unprefixed GA4GH sha512t24u digest used by gtars."""
    digest = hashlib.sha512(sequence.upper()).digest()[:24]
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _normalize_expected_digest(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    if value.lower().startswith("sq."):
        value = value[3:]
    return value if _SHA512T24U.fullmatch(value) else None


def _read_fasta(
    path: Path,
    *,
    max_bytes: int,
    max_records: int,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    name: str | None = None
    chunks: list[bytes] = []
    names: set[str] = set()

    def finish() -> None:
        nonlocal name, chunks
        if name is None:
            return
        sequence = b"".join(chunks).upper()
        if not sequence:
            raise SafetyError("FASTA contains an empty sequence")
        records.append(
            {
                "name": name,
                "length": len(sequence),
                "sha512t24u": sha512t24u(sequence),
                "md5": hashlib.md5(sequence).hexdigest(),
            }
        )

    for line_number, line in iter_text_lines(
        path,
        max_bytes=max_bytes,
        max_records=max_records,
    ):
        if line.startswith(">"):
            finish()
            header = line[1:].strip()
            candidate = header.split(maxsplit=1)[0] if header else ""
            if not candidate or len(candidate) > 1_000:
                raise SafetyError(f"invalid FASTA name at line {line_number}")
            if candidate in names:
                raise SafetyError("duplicate FASTA sequence name")
            names.add(candidate)
            name = candidate
            chunks = []
            continue
        if name is None:
            if line.strip():
                raise SafetyError("FASTA sequence data appears before the first header")
            continue
        compact = "".join(line.split())
        try:
            encoded = compact.encode("ascii")
        except UnicodeEncodeError as exc:
            raise SafetyError(
                f"non-ASCII FASTA sequence near line {line_number}"
            ) from exc
        if any(byte < 33 or byte > 126 for byte in encoded):
            raise SafetyError(f"invalid FASTA sequence byte near line {line_number}")
        chunks.append(encoded)
    finish()
    if not records:
        raise SafetyError("FASTA contains no sequences")
    return records


def validate(args: argparse.Namespace) -> tuple[dict, int]:
    assembly = args.assembly.strip()
    if not assembly or len(assembly) > 200:
        raise SafetyError("assembly must contain 1-200 characters")
    metadata_path = local_path(args.metadata, kind="file")
    document = load_json(
        metadata_path,
        max_bytes=min(args.max_bytes, 64 * 1024**2),
    )
    if not isinstance(document, dict):
        raise SafetyError("metadata root must be a JSON object")

    errors: dict[str, int] = {}
    warnings: dict[str, int] = {}
    if document.get("schema_version") != "1.0":
        errors["metadata:unsupported_schema_version"] = 1
    if document.get("assembly") != assembly:
        errors["metadata:assembly_mismatch"] = 1
    if document.get("coordinate_system") != "0-based-half-open":
        errors["metadata:coordinate_system_mismatch"] = 1

    collection_digest = document.get("collection_digest")
    if not isinstance(collection_digest, str) or not _SHA512T24U.fullmatch(
        collection_digest
    ):
        errors["metadata:invalid_collection_digest_shape"] = 1
    else:
        warnings["collection_digest_shape_only_not_recomputed"] = 1

    expected = document.get("sequences")
    if not isinstance(expected, list) or not expected:
        raise SafetyError("metadata.sequences must be a nonempty array")
    if len(expected) > args.max_records:
        raise SafetyError("metadata sequence count exceeds max-records")

    expected_by_name: dict[str, dict] = {}
    for item in expected:
        if not isinstance(item, dict):
            errors["metadata:non_object_sequence_record"] = (
                errors.get("metadata:non_object_sequence_record", 0) + 1
            )
            continue
        name = item.get("name")
        length = item.get("length")
        digest = _normalize_expected_digest(item.get("sha512t24u"))
        md5 = item.get("md5")
        if not isinstance(name, str) or not name or len(name) > 1_000:
            errors["metadata:invalid_sequence_name"] = (
                errors.get("metadata:invalid_sequence_name", 0) + 1
            )
            continue
        if name in expected_by_name:
            errors["metadata:duplicate_sequence_name"] = (
                errors.get("metadata:duplicate_sequence_name", 0) + 1
            )
            continue
        expected_by_name[name] = item
        if type(length) is not int or length < 1:
            errors["metadata:invalid_sequence_length"] = (
                errors.get("metadata:invalid_sequence_length", 0) + 1
            )
        if digest is None:
            errors["metadata:invalid_sha512t24u"] = (
                errors.get("metadata:invalid_sha512t24u", 0) + 1
            )
        if not isinstance(md5, str) or not _MD5.fullmatch(md5.lower()):
            errors["metadata:invalid_md5"] = errors.get("metadata:invalid_md5", 0) + 1

    fasta_report = None
    if args.fasta:
        fasta_path = local_path(args.fasta, kind="file")
        actual = _read_fasta(
            fasta_path,
            max_bytes=args.max_bytes,
            max_records=args.max_records,
        )
        actual_by_name = {item["name"]: item for item in actual}
        missing = set(expected_by_name) - set(actual_by_name)
        unexpected = set(actual_by_name) - set(expected_by_name)
        length_mismatch = 0
        sha_mismatch = 0
        md5_mismatch = 0
        for name in set(expected_by_name) & set(actual_by_name):
            expected_item = expected_by_name[name]
            actual_item = actual_by_name[name]
            if expected_item.get("length") != actual_item["length"]:
                length_mismatch += 1
            expected_sha = _normalize_expected_digest(
                expected_item.get("sha512t24u")
            )
            if expected_sha != actual_item["sha512t24u"]:
                sha_mismatch += 1
            expected_md5 = expected_item.get("md5")
            if (
                not isinstance(expected_md5, str)
                or expected_md5.lower() != actual_item["md5"]
            ):
                md5_mismatch += 1
        for code, count in (
            ("fasta:missing_sequences", len(missing)),
            ("fasta:unexpected_sequences", len(unexpected)),
            ("fasta:length_mismatches", length_mismatch),
            ("fasta:sha512t24u_mismatches", sha_mismatch),
            ("fasta:md5_mismatches", md5_mismatch),
        ):
            if count:
                errors[code] = count
        fasta_digest, fasta_bytes = sha256_file(
            fasta_path,
            max_bytes=args.max_bytes,
        )
        fasta_report = {
            "path": display_path(fasta_path, 2, args.path_mode),
            "sha256": fasta_digest,
            "size_bytes": fasta_bytes,
            "sequence_count": len(actual),
            "all_sequence_digests_match": not any(
                (missing, unexpected, length_mismatch, sha_mismatch, md5_mismatch)
            ),
        }
    else:
        warnings["fasta_not_supplied_digest_values_not_recomputed"] = 1

    metadata_digest, metadata_bytes = sha256_file(
        metadata_path,
        max_bytes=min(args.max_bytes, 64 * 1024**2),
    )
    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": assembly,
            "coordinate_system": "0-based-half-open",
            "network_used": False,
            "store_opened": False,
            "cache_written": False,
            "packages_imported": False,
            "symlinks_allowed": False,
        },
        "metadata": {
            "path": display_path(metadata_path, 1, args.path_mode),
            "sha256": metadata_digest,
            "size_bytes": metadata_bytes,
            "sequence_count": len(expected_by_name),
            "collection_digest_present": isinstance(collection_digest, str),
        },
        "fasta": fasta_report,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "approved_execution_plan": [
            "prefer RefgetStore.open_local for a reviewed local store",
            "for a new store use RefgetStore.in_memory, verify, then persist explicitly",
            "before open_remote record an HTTPS allowlist, immutable revision, expected digests, cache path, byte quota, and approval",
            "treat get_substring and stream_sequence on a remote store as network reads",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, status = validate(args)
        print_json(report)
        return status
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/tokenizer_manifest.py`

```python
#!/usr/bin/env python3
"""Check a local Gtars tokenizer manifest against its exact universe."""

from __future__ import annotations

import argparse
import re
import sys

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    inspect_bed,
    int_type,
    load_chrom_sizes,
    load_json,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-tokenizer-manifest"
DEFAULT_GTARS_PYTHON_VERSION = "0.9.2"
SPECIAL_TOKEN_NAMES = {"unk", "pad", "mask", "cls", "bos", "eos", "sep"}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a local JSON tokenizer manifest with a local universe BED. "
            "No tokenizer is imported and no model repository is contacted."
        )
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--universe", required=True)
    parser.add_argument("--assembly", required=True)
    parser.add_argument("--chrom-sizes")
    parser.add_argument(
        "--expected-python-version",
        default=DEFAULT_GTARS_PYTHON_VERSION,
    )
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=1024**3,
    )
    parser.add_argument(
        "--max-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-records",
        ),
        default=5_000_000,
    )
    add_path_mode_argument(parser)
    return parser


def _mapping(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise SafetyError(f"{label} must be a JSON object")
    return value


def check(args: argparse.Namespace) -> tuple[dict, int]:
    assembly = args.assembly.strip()
    if not assembly or len(assembly) > 200:
        raise SafetyError("assembly must contain 1-200 characters")
    manifest_path = local_path(args.manifest, kind="file")
    universe_path = local_path(args.universe, kind="file")
    manifest = _mapping(
        load_json(manifest_path, max_bytes=min(args.max_bytes, 16 * 1024**2)),
        "manifest",
    )

    chrom_sizes = None
    chrom_order = None
    chrom_digest = None
    chrom_report = None
    if args.chrom_sizes:
        chrom_path = local_path(args.chrom_sizes, kind="file")
        chrom_sizes, chrom_order = load_chrom_sizes(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
            max_records=min(args.max_records, 1_000_000),
        )
        chrom_digest, chrom_bytes = sha256_file(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
        )
        chrom_report = {
            "path": display_path(chrom_path, 3, args.path_mode),
            "sha256": chrom_digest,
            "size_bytes": chrom_bytes,
        }

    universe = inspect_bed(
        universe_path,
        max_bytes=args.max_bytes,
        max_records=args.max_records,
        chrom_sizes=chrom_sizes,
        chrom_order=chrom_order,
    )
    errors: dict[str, int] = {
        f"universe:{code}": count for code, count in universe["errors"].items()
    }
    warnings: dict[str, int] = {}
    if universe["records"] == 0:
        errors["universe:no_data_records"] = 1
    if universe["duplicate_intervals"]:
        errors["universe:duplicate_intervals"] = universe["duplicate_intervals"]
    if universe["out_of_order_records"]:
        warnings["universe:order_is_part_of_token_ids"] = universe[
            "out_of_order_records"
        ]

    manifest_universe = _mapping(manifest.get("universe"), "manifest.universe")
    tokenizer = _mapping(manifest.get("tokenizer"), "manifest.tokenizer")
    expected_sha = manifest_universe.get("sha256")
    if not isinstance(expected_sha, str) or not _SHA256.fullmatch(expected_sha):
        errors["manifest:invalid_universe_sha256"] = 1
    elif expected_sha != universe["sha256"]:
        errors["manifest:universe_sha256_mismatch"] = 1

    expected_records = manifest_universe.get("records")
    if type(expected_records) is not int or expected_records < 1:
        errors["manifest:invalid_universe_record_count"] = 1
    elif expected_records != universe["records"]:
        errors["manifest:universe_record_count_mismatch"] = 1

    if manifest.get("schema_version") != "1.0":
        errors["manifest:unsupported_schema_version"] = 1
    if manifest.get("assembly") != assembly:
        errors["manifest:assembly_mismatch"] = 1
    if manifest.get("coordinate_system") != "0-based-half-open":
        errors["manifest:coordinate_system_mismatch"] = 1
    if manifest.get("gtars_python_version") != args.expected_python_version:
        errors["manifest:gtars_python_version_mismatch"] = 1
    if chrom_digest is not None:
        if manifest_universe.get("chrom_sizes_sha256") != chrom_digest:
            errors["manifest:chrom_sizes_sha256_mismatch"] = 1

    backend = tokenizer.get("backend")
    if backend not in {"bits", "ailist"}:
        errors["manifest:invalid_backend"] = 1
    vocab_size = tokenizer.get("vocab_size")
    expected_vocab = universe["records"] + len(SPECIAL_TOKEN_NAMES)
    if type(vocab_size) is not int or vocab_size < 1:
        errors["manifest:invalid_vocab_size"] = 1
    elif vocab_size != expected_vocab:
        errors["manifest:vocab_size_mismatch"] = 1

    token_ids = tokenizer.get("special_token_ids")
    if not isinstance(token_ids, dict):
        errors["manifest:missing_special_token_ids"] = 1
        token_ids = {}
    else:
        names = set(token_ids)
        if names != SPECIAL_TOKEN_NAMES:
            errors["manifest:special_token_name_set_mismatch"] = 1
        values = list(token_ids.values())
        if any(type(value) is not int or value < 0 for value in values):
            errors["manifest:invalid_special_token_id"] = 1
        elif len(values) != len(set(values)):
            errors["manifest:duplicate_special_token_ids"] = 1
        elif type(vocab_size) is int and any(value >= vocab_size for value in values):
            errors["manifest:special_token_id_out_of_range"] = 1

    manifest_digest, manifest_bytes = sha256_file(
        manifest_path,
        max_bytes=min(args.max_bytes, 16 * 1024**2),
    )
    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": assembly,
            "coordinate_system": "0-based-half-open",
            "expected_gtars_python_version": args.expected_python_version,
            "network_used": False,
            "packages_imported": False,
            "model_deserialized": False,
            "files_written": False,
            "symlinks_allowed": False,
        },
        "manifest": {
            "path": display_path(manifest_path, 1, args.path_mode),
            "sha256": manifest_digest,
            "size_bytes": manifest_bytes,
            "schema_version": manifest.get("schema_version"),
        },
        "universe": {
            "path": display_path(universe_path, 2, args.path_mode),
            "sha256": universe["sha256"],
            "size_bytes": universe["size_bytes"],
            "records": universe["records"],
            "duplicate_intervals": universe["duplicate_intervals"],
            "out_of_order_records": universe["out_of_order_records"],
        },
        "chromosome_sizes": chrom_report,
        "compatibility": {
            "backend": backend,
            "vocab_size": vocab_size,
            "expected_vocab_size": expected_vocab,
            "special_token_count": len(token_ids),
            "universe_bytes_and_order_match": expected_sha == universe["sha256"],
        },
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "next_checks": [
            "freeze patient and replicate splits before fitting the universe",
            "instantiate Tokenizer.from_bed only after this local manifest passes",
            "verify a small fixed set of token IDs with gtars==0.9.2",
            "do not use from_pretrained until an immutable snapshot is approved locally",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, status = check(args)
        print_json(report)
        return status
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```
