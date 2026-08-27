---
name: geniml
description: Use Geniml for audited local genomic-interval workflows: validate BED and universe contracts, plan Region2Vec or scEmbed runs, inspect model/tokenizer compatibility, and assess consensus universes.
---

# Geniml

Use Geniml for machine learning and statistical workflows over genomic interval
sets. Treat coordinates, assemblies, token vocabularies, model artifacts, and
sample grouping as explicit contracts. The bundled scripts validate or plan;
they do not import Geniml, contact services, deserialize models, or execute
training.

`Bash` is declared only for explicit, user-approved `uv`, Python, Geniml,
Gtars, Git, and native CLI commands shown in this guide; bundled Python helpers
do not spawn subprocesses. Example paths under `data/`, `refs/`, `work/`, and
`models/` are user-provided project placeholders, not missing bundled files.

## Verified release snapshot

- Latest stable PyPI release on 2026-07-23: `geniml==0.8.4` (2026-01-14).
- PyPI does not declare `Requires-Python`; its classifiers list Python
  3.10-3.14. Prefer Python 3.11 or 3.12 where all native/ML wheels resolve.
- `geniml==0.8.4` accepts `gtars>=0.2.5`; the verified base smoke used current
  `gtars==0.9.2` (2026-06-17, Python >=3.10).
- Extras are `ml` and `test`. The base install omits Torch, Gensim, Scanpy,
  Hugging Face Hub, pyBigWig, and HMM dependencies.
- Upstream documentation contains stale examples. Release source and installed
  `--help` output take precedence where they conflict.

## Install reproducibly

Use a project environment and commit its generated lockfile:

```bash
uv venv --python 3.12
uv pip install "geniml==0.8.4" "gtars==0.9.2"
```

For Region2Vec, scEmbed, evaluation, or universe methods needing ML libraries:

```bash
uv pip install "geniml[ml]==0.8.4" "gtars==0.9.2"
```

For a durable project, prefer:

```bash
uv add "geniml[ml]==0.8.4" "gtars==0.9.2"
uv lock
```

Do not install an unpinned Git branch. Record Python, OS/architecture, the
resolved lockfile, and the PyPI artifact digest. Geniml itself is BSD-2-Clause;
the `MIT` frontmatter value licenses this skill's content.

## Start with the safety gate

Before importing Geniml or running an external binary:

1. Work only with explicit local regular files. Reject URLs, FIFOs, devices,
   and symlinks unless the user deliberately changes that policy.
2. Validate BED structure and the declared assembly against a trusted local
   chromosome-sizes file.
3. Bound file count, bytes, rows, workers, epochs, and output size.
4. Separate train/validation/test by patient, donor, biological replicate, or
   other independent unit—not by BED row or cell alone.
5. Inventory and checksum the universe, tokenizer, model, config, inputs,
   metadata manifest, and native binaries.
6. Obtain explicit approval before any BEDbase or Hugging Face download. Never
   infer approval from a model ID or BEDbase identifier.
7. Keep logs aggregate and bounded. BED filenames, sample IDs, phenotypes,
   labels, barcodes, and genomic intervals may be sensitive.

## Coordinate and assembly contract

BED intervals are normally **0-based, half-open** `[start, end)`: start is
included, end is excluded, and length is `end - start`. Do not mix them with
1-based closed coordinates from VCF/GFF or user-facing genome browsers.

For every corpus and artifact, record:

- assembly and patch/accession where possible (for example GRCh38 versus
  GRCh38.p14), plus the chromosome-sizes checksum;
- contig naming convention (`chr1` versus `1`), alt/random/decoy policy, and
  mitochondrial naming;
- coordinate convention, sorting order, duplicate/overlap policy, and whether
  BED strand is meaningful;
- liftover tool, chain digest, source/target assemblies, unmapped fraction, and
  post-liftover validation.

Reject negative coordinates, `end <= start`, integer overflow, unknown
contigs, ends beyond contig length, malformed columns, mixed assemblies, and
silent contig renaming. Sorting and normalization never repair an assembly
mismatch. BED3 has no strand; when column 6 is present, preserve `+`, `-`, or
`.` unless the assay contract says otherwise.

Run a bounded validation and normalization **plan** before analysis:

```bash
python skills/geniml/scripts/bed_validator.py \
  --input data/peaks.bed \
  --assembly GRCh38 \
  --chrom-sizes refs/GRCh38.chrom.sizes
```

The validator reports proposed actions but never rewrites the BED file.

## Current API map

### Region and tokenizer I/O

Prefer Gtars for new interval/tokenizer code:

```python
from gtars.models import Region, RegionSet
from gtars.tokenizers import Tokenizer

regions = RegionSet("data/peaks.bed")
tokenizer = Tokenizer.from_bed("refs/universe.bed")
encoded = tokenizer(regions)
input_ids = encoded["input_ids"]
```

`RegionSet` and `Tokenizer` also accept remote inputs in some constructors;
this skill permits local paths only unless network access is explicitly
approved. `geniml.io.RegionSet(regions, backed=False)` remains available as a
legacy Python implementation; backed sets are iterable but not indexable.
`geniml.io.Region` uses `stop`, while `gtars.models.Region` uses `end`.

With gtars 0.9.2, seven special tokens are added to a BED vocabulary. Therefore
`len(tokenizer)` is not simply the number of universe rows. Preserve universe
row order and the exact special-token map.

### Region2Vec

The modern class lives at a concrete module path:

```python
from geniml.region2vec.main import Region2VecExModel
from geniml.region2vec.utils import Region2VecDataset
from gtars.tokenizers import Tokenizer

tokenizer = Tokenizer.from_bed("refs/universe.bed")
dataset = Region2VecDataset("work/tokens.parquet", shuffle=True)
model = Region2VecExModel(tokenizer=tokenizer, embedding_dim=100)
model.train(dataset, epochs=10, window_size=5, num_cpus=4, seed=42)
```

The Parquet input must contain one list-valued `tokens` column, one document
per row. See [references/region2vec.md](references/region2vec.md) for export,
encoding, legacy CLI, and evaluation details.

### scEmbed

Import `ScEmbed` from `geniml.scembed.main`. AnnData `.var` must contain
`chr`, `start`, and `end`; rows are cells and nonzero features identify
accessible regions. Pre-tokenize to a Parquet `tokens` column and use the same
Tokenizer for training and inference. See
[references/scembed.md](references/scembed.md).

### BEDspace

BEDspace remains in 0.8.4 and invokes an external StarSpace executable.
StarSpace is archived and upstream Geniml does not pin a compatible revision.
Treat BEDspace as a legacy reproduction path, not the default for new systems.
See [references/bedspace.md](references/bedspace.md) for the exact stable CLI
spelling and an immutable, explicitly unverified build baseline.

### Consensus universes and assessment

The installed 0.8.4 CLI uses:

```text
geniml build-universe {cc,ccf,ml,hmm} ...
geniml assess-universe ...
geniml eval {gdst,npt,ctt,rct,bin-gen} ...
```

CC/CCF/ML/HMM consume precomputed coverage bigWigs. Do not concatenate or
generate coverage until all BED files pass the same assembly contract.
Assessment and embedding metrics are distinct: `assess-universe` measures fit
of a universe to interval collections, while `eval` implements CTT, RCT, GDST,
and NPT for embeddings. See
[references/consensus_peaks.md](references/consensus_peaks.md) and
[references/utilities.md](references/utilities.md).

## Important 0.8.4 migration notes

- The 0.7.0 changelog moved new RegionSet/tokenizer work toward Gtars.
- The 0.4.0 names `TreeTokenizer` and `AnnDataTokenizer` are historical; the
  current Gtars API exposes `Tokenizer`.
- In the 0.8.4 wheel, `geniml.region2vec` and `geniml.scembed` do not re-export
  their modern classes/functions. Use the concrete module paths above.
- `geniml tokenize` and `geniml region2vec` call names no longer exported by
  their package `__init__` files; do not build new workflows around those CLI
  paths without an installed-version smoke test.
- `geniml scembed` parses legacy MatrixMarket options but its command body is a
  no-op in 0.8.4. Use `geniml.scembed.main.ScEmbed`.
- Official pages still show `geniml assess`; the release command is
  `geniml assess-universe`.
- `.gtok` remains present in legacy datasets, but upstream issue #14 proposes
  deprecating many-file `.gtok` workflows. Prefer one bounded Parquet corpus.
- Config key `embedding_size` is accepted only for backward compatibility;
  use `embedding_dim`.

## Model and universe compatibility

A Region2Vec/scEmbed inference bundle is valid only when these agree:

- model `config.yaml` `vocab_size` and `embedding_dim`;
- exact `universe.bed` bytes/order and assembly;
- tokenizer implementation/version and special-token IDs;
- checkpoint tensor shapes and pooling policy;
- Geniml/Gtars versions and any tokenization parameters.

Geniml 0.8.4 defaults to `checkpoint.pt`, `config.yaml`, and `universe.bed`.
Its loader uses `torch.load(..., weights_only=True)`, but `.pt`, Gensim
`.model`, pickle, joblib, and native binaries remain untrusted inputs. Inspect
and checksum artifacts before loading; use an isolated environment and never
load a checkpoint merely to discover its metadata.

```bash
python skills/geniml/scripts/model_artifact_inspector.py \
  --model-dir models/region2vec

python skills/geniml/scripts/tokenizer_compatibility.py \
  --model-dir models/region2vec \
  --universe refs/universe.bed \
  --assembly GRCh38
```

`Region2VecExModel(model_path="org/repo")`, `ScEmbed(model_path="org/repo")`,
and Gtars `Tokenizer.from_pretrained(...)` can download from Hugging Face.
Local `from_pretrained("models/local")` loads a local bundle. Pin Hub revision
and expected hashes when a user approves download; then work offline from the
verified cache.

## BEDbase downloads and caches

`BBClient.load_bed`, `load_bedset`, and token-cache operations may contact
`https://api.bedbase.org`. The default cache is
`$BBCLIENT_CACHE` or `~/.bbcache`; `BEDBASE_API` changes the endpoint. Do not
read unrelated environment variables. Set an explicit project cache, estimate
size, approve identifiers/endpoints, and verify returned checksums before use.

Local inspection commands are safer:

```text
geniml bbclient seek ID --cache-folder /absolute/project/cache
geniml bbclient inspect-bedfiles --cache-folder /absolute/project/cache
geniml bbclient inspect-bedsets --cache-folder /absolute/project/cache
```

The `cache-bed`, `cache-bedset`, and `cache-tokens` subcommands may use the
network. Do not run them implicitly or include sensitive local BED files in an
upload/cache workflow.

## Local audit and planning CLIs

All scripts are standard-library-only and default to redacted JSON:

```bash
# Audit manifest paths, checksums, assemblies, and patient/donor leakage
python skills/geniml/scripts/corpus_auditor.py \
  --manifest data/manifest.tsv --assembly-column assembly \
  --group-column patient_id --split-column split

# Plan tokenizer/model compatibility checks
python skills/geniml/scripts/tokenizer_compatibility.py \
  --model-dir models/r2v --universe refs/universe.bed --assembly GRCh38

# Plan consensus construction; does not execute Geniml or coverage tools
python skills/geniml/scripts/consensus_plan.py \
  --manifest data/manifest.tsv --chrom-sizes refs/GRCh38.chrom.sizes \
  --assembly GRCh38 --method cc --output-dir work/consensus

# Plan an embedding run; does not import ML libraries
python skills/geniml/scripts/embedding_plan.py \
  --mode region2vec --data work/tokens.parquet \
  --universe refs/universe.bed --output-dir work/r2v \
  --assembly GRCh38
```

Use `--help` for resource limits and explicit path-disclosure controls.

## References

- [Region2Vec](references/region2vec.md): modern API, artifacts, CLI drift,
  training, encoding, and evaluation.
- [scEmbed](references/scembed.md): AnnData/token preparation, training,
  inference, annotation, privacy, and leakage.
- [BEDspace](references/bedspace.md): metadata schema, exact legacy CLI,
  StarSpace status, artifacts, and retrieval.
- [Consensus peaks](references/consensus_peaks.md): coverage prerequisites,
  CC/CCF/ML/HMM, assessment, and assembly safeguards.
- [Utilities](references/utilities.md): I/O, Gtars tokenizers, BBClient,
  evaluation, model safety, migration, and dated sources.

Source snapshot and primary-paper links are dated in
[references/utilities.md](references/utilities.md). Re-check release metadata
and installed signatures before changing the pinned versions.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/geniml/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/bedspace.md`

# BEDspace

Verified against `geniml==0.8.4` release source, the official BEDbase tutorial,
and the archived StarSpace repository on 2026-07-23.

## Status

BEDspace jointly embeds region sets and metadata labels using the external
StarSpace program. The primary paper evaluates label-to-region,
region-to-label, and region-to-region retrieval.

Primary source: Gharavi et al. (2024), *Joint representation learning for
retrieval and annotation of genomic interval sets*,
doi:[10.3390/bioengineering11030263](https://doi.org/10.3390/bioengineering11030263).

The code path still exists in Geniml 0.8.4, but it is a **legacy reproduction
workflow**:

- StarSpace is not a Python dependency and must be compiled separately.
- `facebookresearch/StarSpace` is archived.
- Geniml does not state or enforce a compatible StarSpace version.
- several official examples and 0.8.4 CLI/API details disagree;
- the 0.8.4 `bedspace search` dispatcher imports a `main` function that is
  absent from `geniml.bedspace.search`.

Do not choose BEDspace by default for a new production search service. Use it
when reproducing the published method or an existing pinned workflow, and
record the limitations.

## Data and privacy contract

Required inputs:

- a local directory of validated BED files;
- a local metadata CSV with a file-path/name column and selected label columns;
- a local universe BED;
- explicit train/test manifests grouped by patient/donor;
- one assembly, coordinate convention, and contig policy.

Metadata values can reveal diagnoses, cell types, tissues, treatment, cohort,
or donor identity. BEDspace places selected labels directly into training text
and writes filenames/labels into result CSVs. Keep inputs and outputs in a
restricted project directory. Default logs should report only row/file counts
and schema names, not values.

Before preprocessing:

1. Split complete patients/donors into train/validation/test.
2. Build or select the universe using training data only.
3. Validate every BED and the universe against the same chromosome sizes.
4. Confirm metadata path values resolve to intended local regular files.
5. Reject URLs, symlinks, duplicate paths, missing files, and mixed assemblies.
6. Decide how missing/multi-valued labels are encoded.

```bash
python skills/geniml/scripts/corpus_auditor.py \
  --manifest data/bedspace.tsv \
  --group-column patient_id \
  --split-column split \
  --assembly-column assembly
```

## Exact 0.8.4 CLI surface

The release exposes:

```text
geniml bedspace preprocess
geniml bedspace train
geniml bedspace distances
geniml bedspace search
```

Use installed `--help` as the final authority. Source-backed flags follow.

### Preprocess

```bash
geniml bedspace preprocess \
  --input /absolute/project/beds \
  --metadata /absolute/project/train.csv \
  --universe /absolute/project/universe.bed \
  --labels "cell_type,target" \
  --output /absolute/project/preprocessed/
```

The implementation creates a Gtars `Tokenizer` from the universe, uses a
hard-coded pool of eight processes, and writes:

```text
<output>train_input.txt
```

The code joins this filename by string concatenation, not `os.path.join`, so
the output argument must end in a path separator. Create and validate the
directory first. The preprocessing text contains labels and tokenized genomic
content; protect it as sensitive derived data.

The current source does not expose worker bounds through the CLI. Run only
after estimating memory and CPU impact, or invoke a reviewed wrapper that
controls resources.

### Train

The long source flag is misspelled:

```text
--path-to-starsapce
```

Use the stable short form `-s`. Its value must be the **directory containing**
the executable named `starspace`; despite some help text, do not pass the
executable itself.

```bash
geniml bedspace train \
  -s /absolute/project/vendor/StarSpace \
  --input /absolute/project/preprocessed/train_input.txt \
  --output /absolute/project/model/ \
  --dim 100 \
  --epochs 50 \
  --lr 0.05
```

Geniml invokes an argv list equivalent to:

```text
starspace train
  -trainFile INPUT
  -model OUTPUT/starspace_trained_model
  -trainMode 0
  -dim DIM
  -epoch EPOCHS
  -negSearchLimit 5
  -thread 20
  -lr LEARNING_RATE
```

The thread count is hard-coded to 20. The implementation waits for the process
but does not check a nonzero return code. Verify output existence, size, and
checksums yourself. If an existing model path is present, Geniml adds
`-initModel` and resumes/mutates training; use a fresh output directory unless
resume is intentional.

### Distances

```bash
geniml bedspace distances \
  -i /absolute/project/model/starspace_trained_model \
  -s /absolute/project/vendor/StarSpace \
  --metadata-train /absolute/project/train.csv \
  --metadata-test /absolute/project/test.csv \
  --universe /absolute/project/universe.bed \
  --project-name heldout \
  --files /absolute/project/beds \
  --labels "cell_type,target" \
  --output /absolute/project/distances/ \
  --threshold 0.5
```

The current outputs are CSV/text files, not a single pickle:

- `raw_cosdist_rl.csv`
- `similarity_score_rl.csv`
- `similarity_score_rr.csv`
- `<project>_starspace_embed.txt`
- `<project>_train_starspace_embed.txt`

The implementation also uses `~/.bedspace/test_documents.txt` and
`~/.bedspace/train_documents.txt`. Isolate `HOME` or review that cache before
running on sensitive data. Output CSVs contain filenames and labels; never
paste unredacted rows into chat or CI logs.

### Search

The CLI advertises search types `l2r`, `r2l`, and `r2r`, with the query as a
positional argument:

```text
geniml bedspace search QUERY -t l2r -d DISTANCES.csv -n 10
```

Do not rely on this path in 0.8.4: the dispatcher imports
`geniml.bedspace.search.main`, but the release file defines only
`run_scenario1`, `run_scenario2`, and `run_scenario3`. There is no
`BEDSpaceModel` class in the release API. Read the verified CSVs with a safe
local data-frame workflow instead of loading an old `.pkl` or calling the
broken dispatcher.

## StarSpace setup: explicit legacy-only baseline

Only do this after the user approves network access and native compilation.
There is no upstream Geniml compatibility pin. The only immutable baseline
available from the archived upstream default branch is its final commit:

```text
8aee0a950aa607c023e5c91cff518bec335b5df5
```

A reproducible source checkout is:

```bash
git init vendor/StarSpace
git -C vendor/StarSpace remote add origin https://github.com/facebookresearch/StarSpace.git
git -C vendor/StarSpace fetch --depth 1 origin 8aee0a950aa607c023e5c91cff518bec335b5df5
git -C vendor/StarSpace checkout --detach FETCH_HEAD
make -C vendor/StarSpace
```

This pin makes the source immutable; it does **not** establish compatibility
with Geniml 0.8.4. Compile in an isolated build environment after reviewing
the archived source and Boost/native toolchain. Record:

- commit and repository URL;
- compiler, make, Boost, OS, and architecture;
- build log;
- SHA-256 and executable permissions of `vendor/StarSpace/starspace`;
- a synthetic preprocess/train/distances smoke result.

Never execute an unverified StarSpace binary downloaded from a third party.
Do not add its directory globally to `PATH`; pass the explicit local directory
with `-s`.

## Model and retrieval provenance

Keep one immutable manifest covering:

- Geniml/Gtars and StarSpace versions/commit;
- Python lockfile and native binary checksum;
- train/test manifest checksums and grouping;
- universe checksum, assembly, row order, and tokenizer special tokens;
- selected metadata columns and missing-value policy;
- preprocessing text checksum;
- dimension, epochs, learning rate, hard-coded thread count, and resume state;
- every model/embedding/distance output checksum.

Similarity is not a calibrated probability. Validate retrieval on held-out
patients/donors, report per-query metrics and class support, and compare with
metadata-only and interval-overlap baselines. Avoid searching the test set
while selecting labels, thresholds, or the universe.

## Migration guidance

Old guidance to remove:

- `BEDSpaceModel.load(...)` / `.search(...)`: not present in 0.8.4.
- `distances.pkl`: current distance code writes CSV/text.
- `--path-to-starspace`: official docs show it, but release source spells the
  long flag `--path-to-starsapce`; use `-s`.
- advice to install StarSpace from an unpinned branch.

For new systems, first define the retrieval task and privacy boundary. A
maintained vector-search stack over locally generated, fully versioned
embeddings may be safer than building new infrastructure around archived
StarSpace, but it is not automatically method-equivalent to BEDspace.

## Official sources

- [Official BEDspace tutorial](https://docs.bedbase.org/geniml/tutorials/bedspace/)
  (undated; accessed 2026-07-23)
- [Geniml v0.8.4 BEDspace source](https://github.com/databio/geniml/tree/v0.8.4/geniml/bedspace)
  (released 2026-01-14; accessed 2026-07-23)
- [Archived StarSpace repository](https://github.com/facebookresearch/StarSpace)
  (final default-branch commit dated 2019-12-13; repository archived; accessed
  2026-07-23)
- [Primary BEDspace paper](https://doi.org/10.3390/bioengineering11030263)
  (2024)

### `references/consensus_peaks.md`

# Consensus peaks and universe assessment

Verified against `geniml==0.8.4` release source and official BEDbase
documentation on 2026-07-23.

## Method scope

A Geniml universe is a reference interval vocabulary derived from coverage
across a collection of BED files. Release 0.8.4 implements:

- **CC**: coverage cutoff;
- **CCF**: coverage cutoff with flexible core/boundary fields;
- **ML**: maximum-likelihood flexible universe;
- **HMM**: hidden-state model over start/core/end coverage.

Primary source: Rymuza et al. (2024), *Methods for constructing and evaluating
consensus genomic interval sets*,
doi:[10.1093/nar/gkae685](https://doi.org/10.1093/nar/gkae685).

The paper motivates and evaluates these methods; it does not make one method
universally best. Choose using training-only data, assay-specific validation,
resource constraints, and held-out universe-fit metrics.

## Non-negotiable input contract

All source BED files and chromosome sizes must agree on:

- assembly/accession and patch;
- 0-based half-open BED coordinates;
- chromosome/contig naming and inclusion policy;
- sort order;
- duplicate and overlap handling;
- strand interpretation;
- liftover provenance, if any.

Reject malformed rows, negative starts, `end <= start`, coordinates beyond
contig length, unknown contigs, mixed assemblies, and integer overflow before
coverage generation. A chromosome name match alone is not proof of assembly
compatibility.

Build the universe only from the training patients/donors. If samples from a
held-out patient contribute to coverage, the resulting vocabulary leaks test
feature prevalence.

```bash
python skills/geniml/scripts/corpus_auditor.py \
  --manifest data/train_manifest.tsv \
  --group-column patient_id \
  --split-column split \
  --assembly-column assembly
```

## Coverage prerequisites

Geniml consumes bigWig tracks in a local coverage directory. With the default
prefix `all`, methods expect:

```text
all_start.bw
all_core.bw
all_end.bw
```

CC and CCF read `all_core.bw`. HMM and likelihood-based methods use
start/core/end tracks. The tracks must share contigs and lengths with the
checksummed chromosome-sizes file.

Official Geniml pages describe producing these tracks with the ecosystem's
coverage tooling, but the current Gtars CLI has changed across releases. Do not
emit or run a guessed `uniwig` command. Pin the exact Gtars/uniwig executable,
capture its `--help`, and smoke-test its output naming on synthetic local BED
data. Record:

- tool version and binary SHA-256;
- complete argv (not a shell-expanded wildcard);
- chromosome-sizes SHA-256;
- ordered input manifest and checksums;
- smoothing/binning parameters;
- output track sizes, contigs, lengths, and checksums.

The bundled planner validates local inputs and emits the Geniml stage, but
intentionally marks coverage generation as an external prerequisite:

```bash
python skills/geniml/scripts/consensus_plan.py \
  --manifest data/train_manifest.tsv \
  --chrom-sizes refs/GRCh38.chrom.sizes \
  --assembly GRCh38 \
  --method cc \
  --cutoff 2 \
  --output-dir work/consensus
```

It does not execute Geniml, Gtars, native binaries, or network requests.

## Exact 0.8.4 CLI

The top-level command is `build-universe`, not `universe build`.

### CC

```bash
geniml build-universe cc \
  --coverage-folder /absolute/project/coverage \
  --coverage-prefix all \
  --output-file /absolute/project/universe_cc.bed \
  --cutoff 2 \
  --merge 100 \
  --filter-size 50
```

`--cutoff` is an integer. If omitted, release source uses mean base coverage
for each chromosome. `--merge` merges nearby output segments; `--filter-size`
removes shorter segments. The output file must not already exist.

Do not claim `cutoff=number_of_files` is a strict sample intersection unless
coverage generation contributes exactly one unit per sample at each base.
Fragment/read coverage or duplicated intervals can violate that assumption.

Python:

```python
from geniml.universe.cc_universe import cc_universe

cc_universe(
    cove="work/coverage",
    file_out="work/universe_cc.bed",
    cove_prefix="all",
    merge=100,
    filter_size=50,
    cutoff=2,
)
```

### CCF

```bash
geniml build-universe ccf \
  --coverage-folder /absolute/project/coverage \
  --coverage-prefix all \
  --output-file /absolute/project/universe_ccf.bed
```

Python:

```python
from geniml.universe.ccf_universe import ccf_universe

ccf_universe(
    cove="work/coverage",
    file_out="work/universe_ccf.bed",
    cove_prefix="all",
)
```

The stable source has no CCF `--confidence`, `--merge`, or `--filter-size`
arguments. CCF writes BED9-like rows carrying core/boundary information; do
not reduce them to BED3 before confirming downstream semantics.

### Likelihood model and ML universe

The 0.8.4 likelihood command has no `build_model` subcommand:

```bash
geniml lh \
  --model-file /absolute/project/model.tar \
  --coverage-folder /absolute/project/coverage \
  --coverage-prefix all \
  --file-no 4
```

Then:

```bash
geniml build-universe ml \
  --model-file /absolute/project/model.tar \
  --coverage-folder /absolute/project/coverage \
  --coverage-prefix all \
  --output-file /absolute/project/universe_ml.bed
```

Python:

```python
from geniml.likelihood.build_model import main as build_likelihood
from geniml.universe.ml_universe import ml_universe

build_likelihood(
    model_file="work/model.tar",
    coverage_folder="work/coverage",
    coverage_prefix="all",
    file_no=4,
)
ml_universe(
    model_file="work/model.tar",
    cove_folder="work/coverage",
    cove_prefix="all",
    file_out="work/universe_ml.bed",
)
```

Treat the `.tar` likelihood model as an untrusted archive if it is not locally
created and checksummed. Inspect archive member names and reject absolute
paths, `..`, links, devices, and excessive expansion before extraction.

### HMM

```bash
geniml build-universe hmm \
  --coverage-folder /absolute/project/coverage \
  --coverage-prefix all \
  --output-file /absolute/project/universe_hmm.bed
```

Use `--not-normalize` only after validating what scale the model expects.
`--save-max-cove` adds maximum coverage information. The 0.8.4 CLI has no
`--states` argument; the model structure is defined in source constants.

Python:

```python
from geniml.universe.hmm_universe import hmm_universe

hmm_universe(
    coverage_folder="work/coverage",
    out_file="work/universe_hmm.bed",
    prefix="all",
    normalize=True,
    save_max_cove=False,
)
```

## Validate every output

Universe builders do not replace input validation. After construction:

1. Re-run BED validation against the same chromosome sizes.
2. Confirm sorted, nonempty output and expected BED column count.
3. Check region count, length distribution, covered bases, overlaps, and
   duplicate coordinates.
4. Confirm no unknown contigs or out-of-bounds ends.
5. Record output SHA-256 and method parameters.
6. Build a fresh Gtars tokenizer and record vocabulary/special-token sizes.
7. Never reorder the universe after a model or token corpus has been created.

Some 0.8.4 functions assume at least one selected base per chromosome and may
index an empty result. Test sparse/empty chromosomes synthetically and fail
closed rather than accepting a partial output.

## Assess fit to held-out collections

The release CLI is:

```bash
geniml assess-universe \
  --raw-data-folder /absolute/project/validation_beds \
  --file-list /absolute/project/validation_files.txt \
  --universe /absolute/project/universe_cc.bed \
  --overlap \
  --distance \
  --distance-universe-to-file \
  --folder-out /absolute/project/assessment \
  --pref validation \
  --no-workers 4
```

Available flags include:

- `--overlap`;
- `--distance`;
- `--distance-flexible`;
- `--distance-universe-to-file`;
- `--distance-flexible-universe-to-file`;
- `--save-to-file`;
- `--save-each`.

`--save-each` can generate large, sensitive per-interval outputs. Leave it off
unless required and bound output size. The docs still show `geniml assess`;
that is not the 0.8.4 top-level command.

Python entry points include:

```python
from geniml.assess.assess import (
    get_f_10_score,
    get_mean_rbs,
    run_all_assessment_methods,
)
```

F10, reciprocal-boundary-style distance summaries, and likelihood measure
different properties. Compare multiple candidate universes on validation
patients, then evaluate the chosen one once on test patients. Do not tune the
cutoff, merging, or method on the test collection.

## Reproducibility record

Store:

- ordered input manifest and grouping;
- assembly/accession, chromosome sizes, coordinate and contig policy;
- every input and coverage checksum;
- exact coverage and Geniml argv;
- Geniml, Gtars, pyBigWig, NumPy, HMM, Python, OS, and architecture versions;
- method, cutoff/model, prefix, normalization, merge/filter parameters;
- output and assessment checksums;
- exclusions, failures, empty contigs, and liftover losses.

Keep file names and sample labels redacted in portable reports.

## Migration corrections

Remove or correct these stale patterns:

- `geniml universe build ...` → `geniml build-universe ...`;
- `geniml universe evaluate ...` → `geniml assess-universe ...`;
- CCF `--confidence` → not present in 0.8.4;
- HMM `--states` → not present in 0.8.4;
- ML `--model-type gaussian|poisson` → not present in 0.8.4;
- generic `build_universe(...)` → not exported by the stable universe module;
- claims that a fixed percentage coverage is universally appropriate.

## Official sources

- [Official consensus CLI guide](https://docs.bedbase.org/geniml/tutorials/create-consensus-peaks)
  (undated; accessed 2026-07-23)
- [Official consensus Python guide](https://docs.bedbase.org/geniml/notebooks/create-consensus-peaks-python)
  (undated; accessed 2026-07-23)
- [Official universe assessment guide](https://docs.bedbase.org/geniml/tutorials/assess-universe/)
  (undated; accessed 2026-07-23)
- [Geniml v0.8.4 universe source](https://github.com/databio/geniml/tree/v0.8.4/geniml/universe)
  (released 2026-01-14; accessed 2026-07-23)
- [Primary consensus-universe paper](https://doi.org/10.1093/nar/gkae685)
  (2024)

### `references/region2vec.md`

# Region2Vec

Verified against `geniml==0.8.4` release source and the official BEDbase
documentation on 2026-07-23.

## What the method does

Region2Vec learns vectors for genomic regions from region co-occurrence within
interval sets. The primary paper describes randomizing regions within each set
to create word2vec-like contexts, then pooling region vectors to represent
sets. Treat learned proximity as a property of the training corpus and
universe, not as proof of a biological mechanism.

Primary method source: Gharavi et al. (2021), *Embeddings of genomic region sets
capture rich biological associations in low dimensions*,
doi:[10.1093/bioinformatics/btab439](https://doi.org/10.1093/bioinformatics/btab439).

## Stable 0.8.4 API reality

Use concrete module paths:

```python
from geniml.region2vec.main import Region2VecExModel
from geniml.region2vec.utils import Region2VecDataset
from gtars.tokenizers import Tokenizer
```

The release's `geniml.region2vec.__init__` does not export
`Region2VecExModel` or the legacy `region2vec` function. Consequently,
`from geniml.region2vec import region2vec` and the installed
`geniml region2vec ...` dispatch path are not reliable in 0.8.4. The old
function still exists at `geniml.region2vec.main_legacy.region2vec`, but use it
only to reproduce an existing workflow after a pinned smoke test.

## Universe and tokenizer contract

Create the tokenizer from a validated local BED universe:

```python
from gtars.tokenizers import Tokenizer

tokenizer = Tokenizer.from_bed("refs/universe.bed")
```

With verified `gtars==0.9.2`:

- universe regions receive stable IDs in file order;
- seven special tokens are added (`unk`, `pad`, `mask`, `cls`, `eos`, `bos`,
  and `sep`);
- `len(tokenizer)` is universe row count plus special tokens;
- `tokenizer(region_set)["input_ids"]` returns integer IDs.

Compatibility requires the exact universe bytes/order, assembly, contig policy,
Gtars version, special-token map/IDs, and tokenization behavior. Re-sorting a
universe changes IDs even when the interval set is mathematically identical.
Never infer compatibility from a shared filename such as `hg38.bed`.

Before tokenizing:

1. Validate BED as 0-based half-open intervals.
2. Confirm a single assembly with a checksummed chromosome-sizes file.
3. Resolve `chr1`/`1`, alt-contig, mitochondrial, and strand policies.
4. Split by patient/donor before learning or evaluating representations.
5. Record the universe SHA-256 and row count.

Run:

```bash
python skills/geniml/scripts/bed_validator.py \
  --input refs/universe.bed \
  --assembly GRCh38 \
  --chrom-sizes refs/GRCh38.chrom.sizes
```

## Prepare the token corpus

`Region2VecDataset` reads a Parquet file with one list-valued column named
`tokens`; each row is one BED document, sample, or cell. IDs must come from the
same tokenizer that initializes the model.

```python
import pyarrow as pa
import pyarrow.parquet as pq
from gtars.models import RegionSet

documents = []
for local_bed in validated_local_beds:
    ids = tokenizer(RegionSet(local_bed))["input_ids"]
    documents.append(ids)

table = pa.table({"tokens": pa.array(documents, type=pa.list_(pa.int32()))})
pq.write_table(table, "work/tokens.parquet")
```

This example assumes `validated_local_beds` came from a bounded, local
manifest. Do not discover arbitrary directory contents, follow symlinks, or
log sample filenames. Ensure every token is an integer in
`[0, len(tokenizer))`. Empty or unusually short documents need an explicit
policy; do not silently discard them after splitting.

`Region2VecDataset(path, shuffle=True, convert_to_str=False)` loads the full
Parquet `tokens` column into memory. Bound rows and total tokens before
construction. `shuffle=True` mutates each document order when accessed; record
the training seed, but do not assume every library/thread schedule is bitwise
deterministic.

## Train the modern model

```python
from geniml.region2vec.main import Region2VecExModel
from geniml.region2vec.utils import Region2VecDataset

dataset = Region2VecDataset("work/tokens.parquet", shuffle=True)
model = Region2VecExModel(
    tokenizer=tokenizer,
    embedding_dim=100,
    pooling_method="mean",
    device="cpu",
)
model.train(
    dataset,
    window_size=5,
    epochs=10,
    min_count=10,
    num_cpus=4,
    seed=42,
)
```

Current source defaults are not fully consistent across legacy and modern
modules. Pass every material setting explicitly. `train` uses Gensim
Word2Vec, then copies learned weights into a Torch embedding matrix.
`load_from_checkpoint` and per-epoch Gensim `.model` files deserialize Gensim
artifacts; load only artifacts you created or independently trust.

Suggested run record:

- Geniml, Gtars, Python, Torch, Gensim, NumPy, and PyArrow versions;
- lockfile digest and platform;
- universe/checkpoint/config/token-corpus/manifest SHA-256;
- assembly, coordinate and contig contracts;
- vocabulary and special-token sizes;
- embedding dimension, window, epochs, `min_count`, workers, seed, shuffling,
  pooling, and device;
- train/validation/test grouping and excluded documents.

Generate a bounded plan first:

```bash
python skills/geniml/scripts/embedding_plan.py \
  --mode region2vec \
  --data work/tokens.parquet \
  --universe refs/universe.bed \
  --output-dir work/region2vec \
  --assembly GRCh38 \
  --embedding-dim 100 --epochs 10 --workers 4 --seed 42
```

## Export and inspect artifacts

The 0.8.4 constants are:

- `checkpoint.pt`
- `config.yaml`
- `universe.bed`

The config uses `vocab_size` and `embedding_dim`; `embedding_size` is accepted
only for backward compatibility and is marked for future deprecation.

Important release-source caveat: `model.export(path)` calls
`export_region2vec_model`, which writes the Torch checkpoint and YAML config
but does **not** write the tokenizer's universe, despite the API docstring.
Copy the exact validated universe into the bundle yourself, without changing
row order, then create a checksum manifest.

```python
from pathlib import Path
import shutil

bundle = Path("models/region2vec")
model.export(str(bundle))
shutil.copyfile("refs/universe.bed", bundle / "universe.bed")
```

Do not overwrite an existing bundle without preserving its prior manifest.
Inspect without deserialization:

```bash
python skills/geniml/scripts/model_artifact_inspector.py \
  --model-dir models/region2vec

python skills/geniml/scripts/tokenizer_compatibility.py \
  --model-dir models/region2vec \
  --universe refs/universe.bed \
  --assembly GRCh38
```

The checkpoint is a `.pt` file. Geniml's local loader uses
`torch.load(..., weights_only=True)`, which reduces but does not eliminate
untrusted-artifact risks such as resource exhaustion, parser defects, or
native-library vulnerabilities. Never use `torch.load`, Gensim load, pickle,
or joblib merely to inspect metadata.

## Load only after verification

Local bundle:

```python
from geniml.region2vec.main import Region2VecExModel

model = Region2VecExModel.from_pretrained("models/region2vec")
```

Despite its name, this classmethod joins local filenames and makes no Hub
request. In contrast:

```python
model = Region2VecExModel(model_path="organization/model")
```

calls `huggingface_hub.hf_hub_download` for the checkpoint, universe, and
config. Do not use that form without explicit network approval, a pinned Hub
revision, an approved cache directory, and expected hashes.

The loader constructs the tokenizer from `universe.bed`, reads `config.yaml`
with YAML `safe_load`, creates a model of `vocab_size × embedding_dim`, and
loads checkpoint weights. A checksum match is necessary but not sufficient:
also compare assembly, special tokens, shape, pooling, and software versions.

## Encode intervals and sets

`Region2VecExModel.encode` accepts a local BED path, a Region, a sequence of
regions, `geniml.io.RegionSet`, or `gtars.models.RegionSet`.

```python
vectors = model.encode(
    "data/query.bed",
    pooling="mean",
    batch_size=64,
)
```

The method tokenizes each input region, projects its token IDs, and applies
mean or max pooling. It returns one vector per input region. It does not
validate assembly or repair malformed intervals. Validate first, and report
aggregate shapes/statistics rather than raw genomic coordinates.

## Evaluate without leakage

Geniml's `eval` module implements the paper's:

- CTT: cluster tendency;
- RCT: preservation of training-occurrence information;
- GDST: relation between genomic and embedding distance;
- NPT: preservation of genomic neighborhoods.

Source-backed CLI:

```text
geniml eval ctt --model-path MODEL --embed-type region2vec
geniml eval gdst --model-path MODEL --embed-type region2vec
geniml eval npt --model-path MODEL --embed-type region2vec --K 10
geniml eval rct --model-path MODEL --embed-type region2vec \
  --bin-path BINARY_EMBEDDINGS
```

`rct` also requires binary embeddings from the same tokenized corpus. The
official tutorial and `eval bin-gen` write pickle; treat that format as trusted
local output only and never load a third-party pickle. Hold out independent
patients/donors before universe selection, hyperparameter tuning, training, and
metric selection. Report all metrics and baselines rather than selecting a
single favorable score.

Primary evaluation source: Zheng et al. (2024), *Methods for evaluating
unsupervised vector representations of genomic regions*,
doi:[10.1093/nargab/lqae086](https://doi.org/10.1093/nargab/lqae086).

## Official sources

- [PyPI geniml 0.8.4](https://pypi.org/project/geniml/0.8.4/) (released
  2026-01-14; accessed 2026-07-23)
- [v0.8.4 release source](https://github.com/databio/geniml/tree/v0.8.4)
  (commit `5e8dd14126c45d14917df74de4fb405f383afb61`; accessed 2026-07-23)
- [Official Region2Vec tutorial](https://docs.bedbase.org/geniml/tutorials/region2vec/)
  (undated; accessed 2026-07-23; contains legacy imports)
- [Official evaluation tutorial](https://docs.bedbase.org/geniml/tutorials/evaluation/)
  (undated; accessed 2026-07-23)
- [Gtars tokenizer documentation](https://docs.bedbase.org/gtars/tokenizers)
  (undated; accessed 2026-07-23)

### `references/scembed.md`

# scEmbed

Verified against `geniml==0.8.4` release source, current Gtars
`0.9.2`, and official BEDbase documentation on 2026-07-23.

## Scope and evidence

scEmbed learns region embeddings from scATAC-seq accessibility and pools them
to represent cells. The primary paper reports that pre-trained region
embeddings can support clustering and transfer to unseen datasets. Do not turn
that result into a universal accuracy claim; performance depends on assay,
reference corpus, universe, filtering, cell types, and split design.

Primary source: LeRoy et al. (2024), *Fast clustering and cell-type annotation
of scATAC data with pre-trained embeddings*,
doi:[10.1093/nargab/lqae073](https://doi.org/10.1093/nargab/lqae073).

## Stable API and known drift

Use:

```python
from geniml.scembed.main import ScEmbed
from geniml.region2vec.utils import Region2VecDataset
from geniml.tokenization.utils import tokenize_anndata
from gtars.tokenizers import Tokenizer
```

Do not use `from geniml.scembed import ScEmbed`: the 0.8.4 package
`__init__` does not export it. The installed `geniml scembed` command parses
legacy MatrixMarket options but its 0.8.4 command body does no training or
encoding.

The source method `ScEmbed.encode(adata)` is public, but 0.8.4's nested token
handling does not match the current `tokenize_anndata` return shape observed
with modern Gtars. Require a pinned synthetic smoke test before relying on
that convenience method. For production, pre-tokenize explicitly, inspect the
shape, and keep the exact versions locked.

## AnnData contract

The AnnData object must satisfy:

- rows (`obs`) are cells;
- columns (`var`) are accessible regions/features;
- `var["chr"]`, `var["start"]`, and `var["end"]` describe each feature;
- coordinates are validated 0-based half-open BED coordinates;
- all features use one declared assembly and contig convention;
- `X` is sparse CSR for bounded tokenization performance;
- duplicate feature coordinates and duplicate barcodes have an explicit policy.

Confirm matrix orientation. A 10x peak-by-barcode MatrixMarket file is often
transposed when constructing AnnData; inspect dimensions instead of copying a
blind `.T`.

Do not expose barcodes, patient IDs, phenotypes, rare cell labels, or raw
intervals in logs. An `.h5ad` may contain identifying metadata in `obs`,
`uns`, embeddings, and file provenance. Output only bounded aggregate counts
unless the user explicitly approves disclosure.

## Leakage-safe split order

Split before fitting or selecting anything:

1. Group cells by patient/donor and biological replicate.
2. Assign complete groups to train/validation/test.
3. Fit QC thresholds, feature/universe selection, token vocabulary, model,
   annotation references, and hyperparameters on training data only.
4. Apply the frozen universe/tokenizer/model to validation and test.
5. Keep technical replicates and multiple samples from one patient together.

Randomly splitting cells from the same donor leaks donor- and batch-specific
accessibility. Building a consensus universe from all patients can also leak
test-set feature prevalence even when labels are hidden.

Audit a local manifest without printing metadata values:

```bash
python skills/geniml/scripts/corpus_auditor.py \
  --manifest data/cells.tsv \
  --group-column patient_id \
  --split-column split \
  --assembly-column assembly
```

## Build and validate the tokenizer

Use a local, checksummed universe from the training partition:

```python
from gtars.tokenizers import Tokenizer

tokenizer = Tokenizer.from_bed("refs/training_universe.bed")
```

Record:

- source cohort and split;
- assembly, chromosome sizes, coordinate/contig/strand policy;
- universe SHA-256, row order, and row count;
- Gtars version and special-token map/IDs;
- `len(tokenizer)`.

Do not use `Tokenizer.from_pretrained("organization/model")` unless the user
approves a network download and supplies a pinned revision and expected
hashes. A model and tokenizer are compatible only when the exact universe,
special-token IDs, and model vocabulary size agree.

## Pre-tokenize to one bounded Parquet file

```python
import pyarrow as pa
import pyarrow.parquet as pq
import scanpy as sc
from geniml.tokenization.utils import tokenize_anndata

adata = sc.read_h5ad("data/train.h5ad")
adata.X = adata.X.tocsr()

encoded_cells = tokenize_anndata(adata, tokenizer)
cells = [encoded["input_ids"] for encoded in encoded_cells]

table = pa.table({
    "tokens": pa.array(cells, type=pa.list_(pa.int32()))
})
pq.write_table(table, "work/train_tokens.parquet")
```

Before writing:

- verify `len(cells) == adata.n_obs`;
- check each token list is bounded and contains IDs in
  `[0, len(tokenizer))`;
- quantify empty cells and out-of-vocabulary/unmatched features;
- preserve row correspondence in a separate protected manifest;
- do not include barcodes or labels in the training Parquet unless required.

The upstream issue
[`databio/geniml#14`](https://github.com/databio/geniml/issues/14)
(opened 2025-09-05) proposes moving away from one `.gtok` file per cell.
Prefer the single Parquet corpus for current work; treat `.gtok` as legacy.

## Train

```python
from geniml.region2vec.utils import Region2VecDataset
from geniml.scembed.main import ScEmbed

dataset = Region2VecDataset(
    "work/train_tokens.parquet",
    shuffle=True,
)
model = ScEmbed(
    tokenizer=tokenizer,
    embedding_dim=100,
    pooling_method="mean",
    device="cpu",
)
model.train(
    dataset,
    window_size=5,
    epochs=10,
    min_count=10,
    num_cpus=4,
    seed=42,
)
```

Bound cells, nonzeros, tokens per cell, workers, epochs, checkpoint frequency,
RAM, and disk. `Region2VecDataset` loads the full Parquet token column into
memory. Training uses Gensim and Torch; Gensim checkpoint loading is unsafe for
untrusted `.model` files.

Generate a run plan first:

```bash
python skills/geniml/scripts/embedding_plan.py \
  --mode scembed \
  --data work/train_tokens.parquet \
  --universe refs/training_universe.bed \
  --output-dir work/scembed \
  --assembly GRCh38 \
  --embedding-dim 100 --epochs 10 --workers 4 --seed 42
```

## Export and local loading

```python
from pathlib import Path
import shutil

bundle = Path("models/scembed")
model.export(str(bundle))
shutil.copyfile(
    "refs/training_universe.bed",
    bundle / "universe.bed",
)
```

As in Region2Vec, the 0.8.4 export utility writes `checkpoint.pt` and
`config.yaml` but does not write the tokenizer universe. Add the exact
validated `universe.bed` yourself and generate checksums.

Inspect before loading:

```bash
python skills/geniml/scripts/model_artifact_inspector.py \
  --model-dir models/scembed

python skills/geniml/scripts/tokenizer_compatibility.py \
  --model-dir models/scembed \
  --universe refs/training_universe.bed \
  --assembly GRCh38
```

Then, for a trusted local bundle:

```python
from geniml.scembed.main import ScEmbed

model = ScEmbed.from_pretrained("models/scembed")
```

This classmethod is local. In contrast,
`ScEmbed(model_path="organization/model")` downloads three files through
Hugging Face Hub. Never trigger that constructor implicitly. Pin a revision,
cache path, expected size, and checksums when a download is explicitly
approved.

`checkpoint.pt` is loaded with Torch `weights_only=True`. Continue to treat it
as untrusted until verified and load in an isolated, resource-bounded
environment. Never inspect it using pickle.

## Generate and attach cell embeddings

After a pinned synthetic smoke test confirms the installed convenience API:

```python
embeddings = model.encode(adata, pooling="mean")
assert embeddings.shape[0] == adata.n_obs
adata.obsm["X_scembed"] = embeddings
```

If the smoke fails, do not patch around token nesting silently. Pin a known
compatible Geniml/Gtars pair or implement an explicit, tested projection using
the verified token IDs and model contract. Never substitute a different
universe to make shapes fit.

For Scanpy downstream analysis:

```python
import scanpy as sc

sc.pp.neighbors(adata, use_rep="X_scembed")
sc.tl.leiden(adata, resolution=0.5, random_state=42)
sc.tl.umap(adata, random_state=42)
```

UMAP and Leiden are exploratory unless validated on held-out donors. Store
software versions, seeds, neighborhood parameters, and the embedding checksum.

## Cell-type annotation

The release contains `geniml.scembed.annotation.Annotator`, which queries a
Qdrant collection and can use local or remote endpoints. That is a separate
network/data-disclosure decision: embeddings and metadata can be sensitive.
Do not create or contact an annotation server without explicit approval.

For any KNN annotation:

- reference and query embeddings must use the same model/tokenizer/universe;
- fit the reference index using training donors only;
- tune `k` and score thresholds on validation donors;
- include unknown/reject behavior;
- report per-class metrics and calibration on held-out donors;
- avoid claiming labels for absent reference cell types.

Never send raw barcodes, patient metadata, or interval lists to a hosted vector
store by default.

## Evaluation

Report:

- donor-grouped clustering metrics with confidence intervals;
- annotation macro/micro F1 and per-class support;
- unknown/reject rate;
- batch/donor association;
- runtime and peak memory;
- baselines fitted on the same training split.

Do not select clusters, labels, or universe parameters by inspecting the test
UMAP. If pre-trained public models were trained on overlapping donors or
datasets, document that possible leakage.

## Official sources

- [scEmbed training tutorial](https://docs.bedbase.org/geniml/tutorials/train-scembed-model)
  (undated; accessed 2026-07-23)
- [scEmbed API page](https://docs.bedbase.org/geniml/api-reference/scembed/)
  (undated; accessed 2026-07-23)
- [Geniml v0.8.4 source](https://github.com/databio/geniml/tree/v0.8.4/geniml/scembed)
  (released 2026-01-14; accessed 2026-07-23)
- [Gtars tokenizer documentation](https://docs.bedbase.org/gtars/tokenizers)
  (undated; accessed 2026-07-23)
- [Primary scEmbed paper](https://doi.org/10.1093/nargab/lqae073)
  (2024)

### `references/utilities.md`

# I/O, tokenization, caches, evaluation, and security

Research snapshot: 2026-07-23. API claims below use official documentation,
PyPI metadata, and the `geniml` v0.8.4 release source. Where current docs and
release code disagree, the discrepancy is stated explicitly.

## Release and dependency facts

`geniml==0.8.4` was released on 2026-01-14. PyPI metadata:

- does not set `Requires-Python`;
- classifies Python 3.10, 3.11, 3.12, 3.13, and 3.14;
- provides `ml` and `test` extras;
- ships a pure-Python wheel, but dependencies include native packages;
- uses Trusted Publishing with a Sigstore provenance link to tag `v0.8.4`.

Release files:

```text
geniml-0.8.4-py3-none-any.whl
sha256 ac0fc520cde6f6461120aee6b40d3cbf20e1e3d8bdb95a3a45345724eee545b5

geniml-0.8.4.tar.gz
sha256 6f429c7c89d06a4c2c378e349d14b3a2d984dc441440ada38473772fce6addb1
```

The stable release requires `gtars>=0.2.5` without an upper bound. The
2026-07-23 verified base smoke resolved `gtars==0.9.2` and successfully
imported Geniml 0.8.4, `geniml.io.RegionSet`, and
`gtars.tokenizers.Tokenizer`. Gtars 0.9.2 was released 2026-06-17 and requires
Python >=3.10.

Pin both direct packages and retain an `uv.lock`; upstream transitive
requirements are mostly lower bounds.

## BED coordinates and validation

BED is normally 0-based, half-open `[start, end)`. A valid BED3 row requires:

- nonempty contig;
- integer `start >= 0`;
- integer `end > start`;
- `end` no greater than the declared contig length;
- values within bounded integer limits.

Do not confuse BED with 1-based closed VCF/GFF coordinates. BED columns beyond
BED3 have their own constraints; preserve them rather than guessing.
BED3 carries no strand. When BED6 strand exists, preserve `+`, `-`, or `.`
unless a documented assay conversion says otherwise.

Assembly compatibility requires more than matching `chr` prefixes. BEDbase
describes chromosome-name sensitivity (XS), out-of-bounds regions (OOBR), and
sequence fit (SF) as separate criteria. Record a concrete assembly/accession
and chromosome-sizes digest. Reject unknown alt/decoy contigs rather than
dropping them silently.

Run:

```bash
python skills/geniml/scripts/bed_validator.py \
  --input data/peaks.bed \
  --assembly GRCh38 \
  --chrom-sizes refs/GRCh38.chrom.sizes
```

The script emits aggregate errors and a normalization plan. It never rewrites
coordinates or performs liftover.

## Region and RegionSet APIs

### Gtars API for new workflows

```python
from gtars.models import Region, RegionSet

region = Region("chr1", 100, 200, None)
regions = RegionSet("data/peaks.bed")
print(len(regions))
regions.to_bed("work/peaks.copy.bed")
```

Gtars 0.9.2 exposes operations including `sort`, `reduce`, `coverage`,
`count_overlaps`, `jaccard`, `nearest_neighbors`, `to_bed`, `to_bed_gz`, and
`to_bigbed`. Do not assume these operations validate assembly or coordinate
semantics. Validate before constructing the object and after writing output.

Official Gtars constructors can accept URLs. This skill restricts them to
validated local regular files by default.

### Legacy Geniml I/O

```python
from geniml.io import BedSet, Region, RegionSet

region = Region("chr1", 100, 200)  # third field is named stop
regions = RegionSet("data/peaks.bed", backed=False)
```

`geniml.io.RegionSet(regions, backed=False)` accepts a path/URL or a list of
legacy Regions. With `backed=True`, it streams the BED, supports iteration and
length, and does not support indexing. Other release classes include `BedSet`,
`Maf`, `SNP`, `TokenizedRegionSet`, and `RegionSetCollection`, though only
`Region`, `RegionSet`, and `BedSet` are exported from `geniml.io`.

The 0.7.0 changelog says RegionSet use switched toward Gtars. Avoid mixing
legacy and Gtars Region objects accidentally: field names and accepted types
differ.

## Tokenization

### Current Gtars tokenizer

```python
from gtars.models import RegionSet
from gtars.tokenizers import Tokenizer

tokenizer = Tokenizer.from_bed("refs/universe.bed")
encoded = tokenizer(RegionSet("data/peaks.bed"))
input_ids = encoded["input_ids"]
```

Gtars also documents `Tokenizer.from_config` and
`Tokenizer.from_pretrained`. The latter can access Hugging Face; do not call it
without explicit network approval, revision pinning, cache bounds, and
expected hashes.

With Gtars 0.9.2, a two-region universe produced `len(tokenizer) == 9` because
seven special tokens are included. Preserve:

- universe bytes, row order, and assembly;
- Gtars version;
- `special_tokens_map` and every special-token ID;
- tokenizer length;
- token-corpus schema and checksum.

Run the local compatibility planner:

```bash
python skills/geniml/scripts/tokenizer_compatibility.py \
  --model-dir models/region2vec \
  --universe refs/universe.bed \
  --assembly GRCh38
```

### Legacy hard tokenization

The stable file `geniml.tokenization.main` defines:

```python
hard_tokenization_main(
    src_folder,
    dst_folder,
    universe_file,
    fraction=1e-9,
    file_list=None,
    num_workers=10,
    bedtools_path="bedtools",
)
```

It invokes an external Bedtools executable and multiprocessing. The
`fraction` is passed to interval intersection logic; it is **not a statistical
p-value**. The package `geniml.tokenization.__init__` comments out its public
exports, so `from geniml.tokenization import hard_tokenization` and the
installed `geniml tokenize` dispatcher are unreliable in 0.8.4.

Do not use an arbitrary `bedtools` found on `PATH`. If reproducing the legacy
path, pin and checksum the binary, pass an explicit absolute path, validate
argv, bound workers, use a fresh output directory, and compare synthetic
results with the Gtars tokenizer.

The current preferred token corpus is a bounded Parquet file with one
list-valued `tokens` column. Upstream issue #14 proposes deprecating one
`.gtok` file per cell.

## BBClient and cache behavior

```python
from geniml.bbclient import BBClient

client = BBClient(cache_folder="/absolute/project/.bbcache")
```

Release defaults:

- endpoint: `BEDBASE_API` or `https://api.bedbase.org`;
- cache root: `BBCLIENT_CACHE` or `~/.bbcache`;
- BEDs under `bedfiles/`;
- BED sets under `bedsets/`;
- token cache in `tokens.zarr`.

`load_bed`, `load_bedset`, `add_bed_tokens_to_cache`, and corresponding
`cache-*` CLI commands may use the network. `add_bed_to_s3` and
`get_bed_from_s3` accept cloud credentials and endpoints; do not use them
without an explicit upload/download request and a separate credential review.
Never read or print the environment broadly. Only consult `BEDBASE_API` and
`BBCLIENT_CACHE` when the user approves those overrides.

Local-oriented CLI:

```text
geniml bbclient seek ID --cache-folder CACHE
geniml bbclient inspect-bedfiles --cache-folder CACHE
geniml bbclient inspect-bedsets --cache-folder CACHE
geniml bbclient rm ID --cache-folder CACHE
```

`rm` mutates cache state; confirm the exact resolved target first. Inspection
can still expose BED IDs and local paths, so redact output in shared logs.

Before an approved download:

1. approve endpoint and exact IDs;
2. set a project-scoped cache and byte quota;
3. reject redirects to unapproved hosts where tooling permits;
4. verify compressed and expanded size;
5. checksum downloaded bytes;
6. validate BED and assembly;
7. record provenance and retrieval time.

No bundled skill script performs BBClient or Hub downloads.

## Model loading and artifact safety

Modern local classes:

```python
from geniml.region2vec.main import Region2VecExModel
from geniml.scembed.main import ScEmbed

r2v = Region2VecExModel.from_pretrained("models/region2vec")
sce = ScEmbed.from_pretrained("models/scembed")
```

These classmethods use local bundle paths. Constructors with
`model_path="organization/model"` call Hugging Face Hub and download
`checkpoint.pt`, `universe.bed`, and `config.yaml`.

Geniml's loader uses `torch.load(..., weights_only=True)` and YAML
`safe_load`. This is safer than unrestricted pickle, but artifacts can still
cause resource exhaustion or exploit parser/native-library vulnerabilities.
Gensim `.model`, pickle, joblib, TorchScript, shared libraries, and external
binaries require even stronger distrust.

Inspect without importing Torch or deserializing:

```bash
python skills/geniml/scripts/model_artifact_inspector.py \
  --model-dir models/region2vec \
  --verify-manifest models/region2vec/SHA256SUMS
```

The inspector reads bounded metadata formats, hashes bytes, flags risky
extensions, rejects URLs/symlinks/traversal, and never loads model objects.

## Embedding evaluation

The `geniml eval` release CLI has:

```text
gdst     Genome distance scaling test
npt      Neighborhood preserving test
ctt      Cluster tendency test
rct      Reconstruction test
bin-gen  Generate binary embeddings
```

Examples:

```bash
geniml eval gdst \
  --model-path /absolute/project/model \
  --embed-type region2vec \
  --num-samples 10000 \
  --seed 42

geniml eval npt \
  --model-path /absolute/project/model \
  --embed-type region2vec \
  --K 10 \
  --num-samples 1000 \
  --seed 42 \
  --num-workers 4
```

The official tutorial's `BaseEmbeddings` and `bin-gen` workflows use pickle
for binary embedding objects. Generate them locally and never load an
untrusted pickle. Bound samples/workers and record random seeds. Evaluate on
patients/donors excluded from universe selection and training.

Primary source: Zheng et al. (2024), *Methods for evaluating unsupervised
vector representations of genomic regions*,
doi:[10.1093/nargab/lqae086](https://doi.org/10.1093/nargab/lqae086).

## BEDshift

The integrated Bedshift CLI is:

```text
geniml bedshift --help
```

It can use a local chromosome-length file or resolve a Refgenie genome through
`refgenconf`. Prefer an explicit, checksummed local chromosome-sizes file to
avoid implicit lookup/network behavior. Set a seed, output bound, and
perturbation policy matching the null hypothesis. Validate randomized
coordinates exactly like originals.

Primary source: Gu et al. (2021), *Bedshift: perturbation of genomic interval
sets*, doi:[10.1186/s13059-021-02440-w](https://doi.org/10.1186/s13059-021-02440-w).

## Privacy and bounded reporting

Potentially sensitive:

- BED coordinates and filenames;
- sample, donor, patient, treatment, diagnosis, and tissue metadata;
- cell barcodes and rare labels;
- embeddings that permit membership or nearest-neighbor inference;
- local cache paths and BEDbase identifiers.

Default reports should contain only aggregate counts, schema names, checksums,
software versions, and redacted file IDs. Cap error examples; never dump
entire malformed rows or metadata values. Store full provenance manifests in
the protected project, not chat output.

## Migration and deprecation ledger

- 0.4.0: tokenizers renamed to `TreeTokenizer` and `AnnDataTokenizer`.
- 0.7.0: RegionSet use moved toward Gtars and encoding changed.
- 0.8.0: Atacformer added.
- 0.8.1: BEDspace fixed according to the changelog.
- 0.8.4: latest stable; release notes contain only the version bump.
- Current Gtars API: use the unified `gtars.tokenizers.Tokenizer`.
- `.gtok`: proposed for deprecation in upstream issue #14; prefer Parquet.
- `embedding_size`: backward-compatible config key; use `embedding_dim`.
- Top-level Region2Vec/scEmbed/tokenization exports shown by old docs are
  absent/commented in the 0.8.4 wheel.
- Official `geniml assess` examples are stale; use
  `geniml assess-universe`.

## Dated authoritative sources

Package and source:

- [PyPI: geniml 0.8.4](https://pypi.org/project/geniml/0.8.4/) — released
  2026-01-14; accessed 2026-07-23.
- [PyPI JSON: geniml 0.8.4](https://pypi.org/pypi/geniml/0.8.4/json) —
  artifact hashes, dependencies, extras, and null `Requires-Python`; accessed
  2026-07-23.
- [GitHub release v0.8.4](https://github.com/databio/geniml/releases/tag/v0.8.4)
  — commit `5e8dd14126c45d14917df74de4fb405f383afb61`; released
  2026-01-14; accessed 2026-07-23.
- [Geniml changelog](https://docs.bedbase.org/geniml/changelog/) — through
  0.8.1 on the rendered page; accessed 2026-07-23.
- [PyPI: gtars 0.9.2](https://pypi.org/project/gtars/0.9.2/) — released
  2026-06-17; accessed 2026-07-23.

Official API/ecosystem documentation:

- [Geniml documentation](https://docs.bedbase.org/geniml/) — accessed
  2026-07-23.
- [Geniml I/O API](https://docs.bedbase.org/geniml/api-reference/io/) —
  accessed 2026-07-23.
- [Gtars RegionSet](https://docs.bedbase.org/gtars/regionSet) — accessed
  2026-07-23.
- [Gtars tokenizers](https://docs.bedbase.org/gtars/tokenizers) — accessed
  2026-07-23.
- [BEDbase reference-genome compatibility](https://docs.bedbase.org/bedbase/user/reference-genome-compatibility/)
  — accessed 2026-07-23.
- [BEDbase BBClient and caching](https://docs.bedbase.org/bedbase/user/bbclient/)
  — accessed 2026-07-23.
- [Geniml evaluation tutorial](https://docs.bedbase.org/geniml/tutorials/evaluation/)
  — accessed 2026-07-23.
- [Official citation map](https://docs.bedbase.org/citations) — accessed
  2026-07-23.

Primary papers:

- [Gharavi et al. 2021, Region2Vec](https://doi.org/10.1093/bioinformatics/btab439)
- [Gu et al. 2021, BEDshift](https://doi.org/10.1186/s13059-021-02440-w)
- [Gharavi et al. 2024, BEDspace](https://doi.org/10.3390/bioengineering11030263)
- [LeRoy et al. 2024, scEmbed](https://doi.org/10.1093/nargab/lqae073)
- [Rymuza et al. 2024, consensus universes](https://doi.org/10.1093/nar/gkae685)
- [Zheng et al. 2024, embedding evaluation](https://doi.org/10.1093/nargab/lqae086)

### `scripts/__init__.py`

```python
"""Dependency-free local helpers for the Geniml skill."""
```

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared, dependency-free safety helpers for local Geniml skill CLIs."""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any, Iterator


HARD_MAX_FILES = 100_000
HARD_MAX_BYTES = 8 * 1024**3
HARD_MAX_RECORDS = 10_000_000
HARD_MAX_LINE_BYTES = 1024 * 1024
HARD_MAX_WORKERS = 256
HARD_MAX_EPOCHS = 100_000
MAX_COORDINATE = 2**63 - 1

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
_INTEGER = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
_FLOAT = re.compile(
    r"^-?(?:(?:0|[1-9][0-9]*)\.[0-9]+|(?:0|[1-9][0-9]*)(?:[eE][+-]?[0-9]+))$"
)
_YAML_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")


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
        raise SafetyError(f"{label} must be an integer") from exc
    if parsed < minimum or parsed > maximum:
        raise SafetyError(f"{label} must be between {minimum} and {maximum}")
    return parsed


def int_type(*, minimum: int = 0, maximum: int, label: str):
    """Return an argparse-compatible bounded integer parser."""

    def parse(value: str) -> int:
        try:
            return bounded_int(
                value,
                minimum=minimum,
                maximum=maximum,
                label=label,
            )
        except SafetyError as exc:
            raise ValueError(str(exc)) from exc

    return parse


def _reject_unsafe_text_path(raw: str) -> None:
    if not raw or "\x00" in raw:
        raise SafetyError("path must be a nonempty string without NUL bytes")
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
    """Yield UTF-8 text lines with compressed and expanded bounds."""
    if max_bytes < 1 or max_bytes > HARD_MAX_BYTES:
        raise SafetyError("max_bytes is outside the hard safety bound")
    if max_records < 1 or max_records > HARD_MAX_RECORDS:
        raise SafetyError("max_records is outside the hard safety bound")
    if max_line_bytes < 1 or max_line_bytes > HARD_MAX_LINE_BYTES:
        raise SafetyError("max_line_bytes is outside the hard safety bound")
    if path.stat().st_size > max_bytes:
        raise SafetyError("compressed/input file exceeds byte limit")

    expanded_bytes = 0
    with _open_binary_nofollow(path) as raw_handle:
        if path.name.lower().endswith(".gz"):
            stream = gzip.GzipFile(fileobj=raw_handle, mode="rb")
        else:
            stream = raw_handle
        try:
            for line_number, raw_line in enumerate(stream, start=1):
                if line_number > max_records:
                    raise SafetyError(f"record limit exceeded in {path}")
                if len(raw_line) > max_line_bytes:
                    raise SafetyError(f"line {line_number} exceeds line-size limit")
                expanded_bytes += len(raw_line)
                if expanded_bytes > max_bytes:
                    raise SafetyError("expanded text exceeds byte limit")
                if b"\x00" in raw_line:
                    raise SafetyError(f"NUL byte found at line {line_number}")
                try:
                    text = raw_line.decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise SafetyError(
                        f"file is not valid UTF-8 near line {line_number}"
                    ) from exc
                yield line_number, text.rstrip("\r\n")
        finally:
            if stream is not raw_handle:
                stream.close()


def sha256_file(path: Path, *, max_bytes: int) -> tuple[str, int]:
    """Hash a bounded regular file without following symlinks."""
    if max_bytes < 1 or max_bytes > HARD_MAX_BYTES:
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


def display_path(path: Path, index: int, mode: str) -> str:
    """Render a path using the requested disclosure level."""
    if mode == "redacted":
        return f"file_{index:04d}"
    if mode == "basename":
        return path.name
    if mode == "full":
        return str(path)
    raise SafetyError(f"unknown path display mode: {mode}")


def add_path_mode_argument(parser) -> None:
    parser.add_argument(
        "--path-mode",
        choices=("redacted", "basename", "full"),
        default="redacted",
        help="Path disclosure in output (default: redacted).",
    )


def print_json(payload: dict[str, Any]) -> None:
    """Print deterministic JSON with no non-finite values."""
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, allow_nan=False)
    sys.stdout.write("\n")


def read_delimited_manifest(
    path: Path,
    *,
    delimiter_name: str,
    max_bytes: int,
    max_rows: int,
) -> tuple[list[str], list[dict[str, str]]]:
    """Read a bounded UTF-8 CSV/TSV manifest."""
    delimiter = "\t" if delimiter_name == "tsv" else ","
    lines = [
        line
        for _, line in iter_text_lines(
            path,
            max_bytes=max_bytes,
            max_records=max_rows + 1,
        )
    ]
    if not lines:
        raise SafetyError("manifest is empty")
    reader = csv.DictReader(io.StringIO("\n".join(lines)), delimiter=delimiter)
    if not reader.fieldnames:
        raise SafetyError("manifest has no header")
    raw_fieldnames = [field if field is not None else "" for field in reader.fieldnames]
    if any(field != field.strip() for field in raw_fieldnames):
        raise SafetyError("manifest column names must not have surrounding whitespace")
    fieldnames = raw_fieldnames
    if any(not field for field in fieldnames):
        raise SafetyError("manifest contains an empty column name")
    if len(set(fieldnames)) != len(fieldnames):
        raise SafetyError("manifest contains duplicate column names")
    if len(fieldnames) > 1_000:
        raise SafetyError("manifest exceeds the 1,000-column safety bound")

    rows: list[dict[str, str]] = []
    for row_number, row in enumerate(reader, start=2):
        if len(rows) >= max_rows:
            raise SafetyError("manifest row limit exceeded")
        if None in row:
            raise SafetyError(f"manifest row {row_number} has extra fields")
        normalized = {
            key.strip(): (value.strip() if value is not None else "")
            for key, value in row.items()
        }
        rows.append(normalized)
    return fieldnames, rows


def delimiter_from_path(path: Path, requested: str) -> str:
    if requested != "auto":
        return requested
    return "csv" if path.suffix.lower() == ".csv" else "tsv"


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
                f"chromosome-sizes line {line_number} must have two tab-separated fields"
            )
        chrom, size_text = fields
        if not chrom or any(character.isspace() for character in chrom):
            raise SafetyError(f"invalid contig name at line {line_number}")
        if chrom in sizes:
            raise SafetyError(f"duplicate contig in chromosome sizes: {chrom}")
        if not _INTEGER.fullmatch(size_text):
            raise SafetyError(f"invalid contig size at line {line_number}")
        size = int(size_text)
        if size <= 0 or size > MAX_COORDINATE:
            raise SafetyError(f"contig size out of bounds at line {line_number}")
        sizes[chrom] = size
        order.append(chrom)
    if not sizes:
        raise SafetyError("chromosome-sizes file has no records")
    return sizes, order


def simple_yaml_mapping(
    path: Path,
    *,
    max_bytes: int,
    max_records: int = 10_000,
) -> dict[str, Any]:
    """Parse a conservative top-level scalar YAML mapping without PyYAML."""
    result: dict[str, Any] = {}
    for line_number, line in iter_text_lines(
        path,
        max_bytes=max_bytes,
        max_records=max_records,
    ):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped == "---":
            continue
        if line[:1].isspace():
            raise SafetyError("nested YAML is not supported by the safe inspector")
        if ":" not in line:
            raise SafetyError(f"unsupported YAML at line {line_number}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not _YAML_KEY.fullmatch(key):
            raise SafetyError(f"invalid YAML key at line {line_number}")
        if key in result:
            raise SafetyError(f"duplicate YAML key: {key}")
        if any(marker in raw_value for marker in ("!", "&", "*", "{", "[", "|", ">")):
            raise SafetyError(f"complex YAML is not supported at line {line_number}")
        if not raw_value or raw_value in {"null", "Null", "NULL", "~"}:
            value: Any = None
        elif raw_value in {"true", "True", "TRUE"}:
            value = True
        elif raw_value in {"false", "False", "FALSE"}:
            value = False
        elif _INTEGER.fullmatch(raw_value):
            value = int(raw_value)
        elif _FLOAT.fullmatch(raw_value):
            value = float(raw_value)
        elif (
            len(raw_value) >= 2
            and raw_value[0] == raw_value[-1]
            and raw_value[0] in {"'", '"'}
        ):
            value = raw_value[1:-1]
        else:
            value = raw_value
        result[key] = value
    return result


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

### `scripts/bed_validator.py`

```python
#!/usr/bin/env python3
"""Validate one local BED file and emit a non-mutating normalization plan."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    MAX_COORDINATE,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    int_type,
    iter_text_lines,
    load_chrom_sizes,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "bed-validator"
_DECIMAL = re.compile(r"^-?[0-9]+$")
_VALID_STRANDS = {"+", "-", "."}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a local BED file as 0-based half-open intervals and emit "
            "a bounded normalization plan. The input is never rewritten."
        )
    )
    parser.add_argument("--input", required=True, help="Local BED or BED.GZ file.")
    parser.add_argument(
        "--assembly",
        required=True,
        help="Declared assembly/accession recorded in the report.",
    )
    parser.add_argument(
        "--chrom-sizes",
        help="Optional local two-column chromosome-sizes file for contig/bounds checks.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=512 * 1024**2,
        help="Maximum compressed and expanded input bytes (default: 512 MiB).",
    )
    parser.add_argument(
        "--max-records",
        type=int_type(minimum=1, maximum=HARD_MAX_RECORDS, label="max-records"),
        default=1_000_000,
        help="Maximum text records, including headers (default: 1,000,000).",
    )
    parser.add_argument(
        "--max-examples",
        type=int_type(minimum=0, maximum=100, label="max-examples"),
        default=10,
        help="Maximum redacted issue examples (default: 10).",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Do not treat a BED with zero data records as an error.",
    )
    add_path_mode_argument(parser)
    return parser


def _record_issue(
    counter: Counter[str],
    examples: list[dict[str, int | str]],
    code: str,
    line_number: int,
    maximum: int,
) -> None:
    counter[code] += 1
    if len(examples) < maximum:
        examples.append({"code": code, "line": line_number})


def validate(args: argparse.Namespace) -> tuple[dict, int]:
    if not args.assembly.strip() or len(args.assembly) > 200:
        raise SafetyError("assembly must be a nonempty value of at most 200 characters")

    bed_path = local_path(args.input, kind="file")
    chrom_sizes: dict[str, int] | None = None
    chrom_order: dict[str, int] | None = None
    chrom_sizes_digest: str | None = None
    if args.chrom_sizes:
        chrom_path = local_path(args.chrom_sizes, kind="file")
        sizes, order = load_chrom_sizes(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
            max_records=min(args.max_records, 1_000_000),
        )
        chrom_sizes = sizes
        chrom_order = {chrom: index for index, chrom in enumerate(order)}
        chrom_sizes_digest, _ = sha256_file(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
        )

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    examples: list[dict[str, int | str]] = []
    records = 0
    skipped = 0
    min_columns: int | None = None
    max_columns = 0
    contigs: set[str] = set()
    seen: set[tuple[str, int, int]] = set()
    duplicate_count = 0
    overlap_count = 0
    max_end_by_contig: dict[str, int] = {}
    previous_sort_key: tuple[int | str, int, int] | None = None
    unsorted_count = 0
    strand_rows = 0

    for line_number, line in iter_text_lines(
        bed_path,
        max_bytes=args.max_bytes,
        max_records=args.max_records,
    ):
        if not line:
            skipped += 1
            warnings["blank_line"] += 1
            continue
        if line.startswith("#") or line.startswith("track") or line.startswith("browser"):
            skipped += 1
            continue

        fields = line.split("\t")
        if len(fields) < 3:
            _record_issue(
                errors,
                examples,
                "fewer_than_three_columns",
                line_number,
                args.max_examples,
            )
            continue
        records += 1
        min_columns = len(fields) if min_columns is None else min(min_columns, len(fields))
        max_columns = max(max_columns, len(fields))

        chrom = fields[0]
        if not chrom or any(character.isspace() or ord(character) < 32 for character in chrom):
            _record_issue(
                errors,
                examples,
                "invalid_contig",
                line_number,
                args.max_examples,
            )
            continue

        start_text, end_text = fields[1], fields[2]
        if not _DECIMAL.fullmatch(start_text) or not _DECIMAL.fullmatch(end_text):
            _record_issue(
                errors,
                examples,
                "non_decimal_coordinate",
                line_number,
                args.max_examples,
            )
            continue
        start, end = int(start_text), int(end_text)
        if start < 0 or end < 0:
            _record_issue(
                errors,
                examples,
                "negative_coordinate",
                line_number,
                args.max_examples,
            )
            continue
        if start > MAX_COORDINATE or end > MAX_COORDINATE:
            _record_issue(
                errors,
                examples,
                "coordinate_integer_overflow",
                line_number,
                args.max_examples,
            )
            continue
        if end == start:
            _record_issue(
                errors,
                examples,
                "zero_length_interval",
                line_number,
                args.max_examples,
            )
            continue
        if end < start:
            _record_issue(
                errors,
                examples,
                "end_before_start",
                line_number,
                args.max_examples,
            )
            continue

        if chrom_sizes is not None:
            if chrom not in chrom_sizes:
                _record_issue(
                    errors,
                    examples,
                    "unknown_contig",
                    line_number,
                    args.max_examples,
                )
                continue
            if end > chrom_sizes[chrom]:
                _record_issue(
                    errors,
                    examples,
                    "end_beyond_contig",
                    line_number,
                    args.max_examples,
                )
                continue

        if len(fields) >= 6:
            strand_rows += 1
            if fields[5] not in _VALID_STRANDS:
                _record_issue(
                    errors,
                    examples,
                    "invalid_bed6_strand",
                    line_number,
                    args.max_examples,
                )

        contigs.add(chrom)
        key = (chrom, start, end)
        if key in seen:
            duplicate_count += 1
        else:
            seen.add(key)

        prior_end = max_end_by_contig.get(chrom)
        if prior_end is not None and start < prior_end:
            overlap_count += 1
        max_end_by_contig[chrom] = max(end, prior_end or end)

        if chrom_order is None:
            sort_key: tuple[int | str, int, int] = (chrom, start, end)
        else:
            sort_key = (chrom_order[chrom], start, end)
        if previous_sort_key is not None and sort_key < previous_sort_key:
            unsorted_count += 1
        previous_sort_key = sort_key

    if records == 0 and not args.allow_empty:
        errors["no_data_records"] += 1
    if chrom_sizes is None:
        warnings["bounds_not_checked_without_chrom_sizes"] += 1
    if unsorted_count:
        warnings["out_of_order_records"] = unsorted_count
    if duplicate_count:
        warnings["duplicate_intervals"] = duplicate_count
    if overlap_count:
        warnings["overlapping_intervals"] = overlap_count

    digest, size = sha256_file(bed_path, max_bytes=args.max_bytes)
    actions: list[dict[str, str | int]] = []
    if errors:
        actions.append(
            {
                "action": "reject_or_quarantine_invalid_rows",
                "count": sum(errors.values()),
            }
        )
    if unsorted_count:
        actions.append(
            {
                "action": "stable_sort",
                "detail": (
                    "use chromosome-sizes order, then numeric start/end"
                    if chrom_order is not None
                    else "supply chromosome sizes before choosing contig order"
                ),
            }
        )
    if duplicate_count:
        actions.append(
            {
                "action": "decide_duplicate_policy",
                "count": duplicate_count,
            }
        )
    if chrom_sizes is None:
        actions.append(
            {
                "action": "supply_chromosome_sizes",
                "detail": "required before overflow/contig normalization",
            }
        )
    actions.append(
        {
            "action": "preserve_coordinate_semantics",
            "detail": "BED 0-based half-open; no implicit liftover or chr renaming",
        }
    )

    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": args.assembly,
            "coordinate_system": "0-based-half-open",
            "input_mutated": False,
            "network_used": False,
        },
        "input": {
            "path": display_path(bed_path, 1, args.path_mode),
            "sha256": digest,
            "size_bytes": size,
        },
        "chromosome_sizes_sha256": chrom_sizes_digest,
        "summary": {
            "records": records,
            "skipped_header_or_blank_lines": skipped,
            "contig_count": len(contigs),
            "minimum_columns": min_columns,
            "maximum_columns": max_columns if records else None,
            "bed6_or_wider_rows": strand_rows,
            "duplicate_intervals": duplicate_count,
            "overlap_observations": overlap_count,
            "out_of_order_records": unsorted_count,
        },
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "issue_examples": examples,
        "normalization_plan": actions,
    }
    return report, 0 if not errors else 2


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        report, exit_code = validate(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/consensus_plan.py`

```python
#!/usr/bin/env python3
"""Create a bounded, local-only Geniml consensus-universe execution plan."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_FILES,
    SafetyError,
    add_path_mode_argument,
    delimiter_from_path,
    display_path,
    fail_json,
    int_type,
    load_chrom_sizes,
    local_path,
    print_json,
    read_delimited_manifest,
    sha256_file,
)


TOOL = "consensus-peaks-planner"
_SAFE_PREFIX = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate local consensus inputs and emit argv arrays for Geniml "
            "0.8.4. No command, coverage tool, or network request is executed."
        )
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--chrom-sizes", required=True)
    parser.add_argument("--assembly", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--coverage-dir")
    parser.add_argument("--likelihood-model")
    parser.add_argument("--method", choices=("cc", "ccf", "ml", "hmm"), required=True)
    parser.add_argument("--coverage-prefix", default="all")
    parser.add_argument(
        "--cutoff",
        type=int_type(minimum=1, maximum=2**31 - 1, label="cutoff"),
    )
    parser.add_argument(
        "--merge",
        type=int_type(minimum=0, maximum=10_000_000, label="merge"),
        default=0,
    )
    parser.add_argument(
        "--filter-size",
        type=int_type(minimum=0, maximum=10_000_000, label="filter-size"),
        default=0,
    )
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--save-max-coverage", action="store_true")
    parser.add_argument("--path-column", default="path")
    parser.add_argument("--assembly-column", default="assembly")
    parser.add_argument(
        "--delimiter",
        choices=("auto", "csv", "tsv"),
        default="auto",
    )
    parser.add_argument(
        "--max-files",
        type=int_type(minimum=1, maximum=HARD_MAX_FILES, label="max-files"),
        default=10_000,
    )
    parser.add_argument(
        "--max-manifest-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-manifest-bytes",
        ),
        default=64 * 1024**2,
    )
    parser.add_argument(
        "--max-total-input-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-total-input-bytes",
        ),
        default=4 * 1024**3,
    )
    add_path_mode_argument(parser)
    return parser


def _manifest_bed(raw: str, manifest: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = manifest.parent / candidate
    return local_path(str(candidate), kind="file")


def _render(path: Path, label: str, mode: str) -> str:
    if mode == "full":
        return str(path)
    if mode == "basename":
        return path.name
    return f"<{label}>"


def plan(args: argparse.Namespace) -> tuple[dict, int]:
    if not args.assembly.strip() or len(args.assembly) > 200:
        raise SafetyError("assembly must be a nonempty value of at most 200 characters")
    if not _SAFE_PREFIX.fullmatch(args.coverage_prefix):
        raise SafetyError("coverage prefix contains unsupported characters")
    if args.cutoff is not None and args.cutoff < 1:
        raise SafetyError("cutoff must be at least 1")
    if args.method != "cc" and (
        args.cutoff is not None or args.merge != 0 or args.filter_size != 0
    ):
        raise SafetyError("cutoff, merge, and filter-size apply only to method cc")
    if args.method != "hmm" and (args.no_normalize or args.save_max_coverage):
        raise SafetyError("normalization and max-coverage flags apply only to method hmm")
    if args.likelihood_model and args.method != "ml":
        raise SafetyError("likelihood-model applies only to method ml")

    manifest = local_path(args.manifest, kind="file")
    chrom_sizes = local_path(args.chrom_sizes, kind="file")
    output_dir = local_path(args.output_dir, kind="dir")
    delimiter = delimiter_from_path(manifest, args.delimiter)
    fields, rows = read_delimited_manifest(
        manifest,
        delimiter_name=delimiter,
        max_bytes=args.max_manifest_bytes,
        max_rows=args.max_files,
    )
    if args.path_column not in fields:
        raise SafetyError(f"path column is missing: {args.path_column}")
    if args.assembly_column not in fields:
        raise SafetyError(f"assembly column is missing: {args.assembly_column}")
    if not rows:
        raise SafetyError("manifest has no data rows")

    sizes, contig_order = load_chrom_sizes(
        chrom_sizes,
        max_bytes=min(args.max_manifest_bytes, 128 * 1024**2),
        max_records=1_000_000,
    )
    manifest_digest, manifest_size = sha256_file(
        manifest,
        max_bytes=args.max_manifest_bytes,
    )
    chrom_digest, chrom_size_bytes = sha256_file(
        chrom_sizes,
        max_bytes=min(args.max_manifest_bytes, 128 * 1024**2),
    )

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    local_beds: list[Path] = []
    total_input_bytes = 0
    for row in rows:
        raw_path = row.get(args.path_column, "")
        if not raw_path:
            errors["blank_path"] += 1
            continue
        if row.get(args.assembly_column, "") != args.assembly:
            errors["assembly_mismatch"] += 1
        try:
            bed = _manifest_bed(raw_path, manifest)
        except (OSError, SafetyError):
            errors["invalid_or_missing_local_bed"] += 1
            continue
        local_beds.append(bed)
        total_input_bytes += bed.lstat().st_size
        if total_input_bytes > args.max_total_input_bytes:
            raise SafetyError("BED corpus exceeds max-total-input-bytes")
    if len(set(local_beds)) != len(local_beds):
        errors["duplicate_bed_paths"] = len(local_beds) - len(set(local_beds))

    coverage_dir: Path | None = None
    required_coverage_names = (
        [f"{args.coverage_prefix}_core.bw"]
        if args.method in {"cc", "ccf"}
        else [
            f"{args.coverage_prefix}_start.bw",
            f"{args.coverage_prefix}_core.bw",
            f"{args.coverage_prefix}_end.bw",
        ]
    )
    coverage_files: list[dict[str, str | int]] = []
    if args.coverage_dir:
        coverage_dir = local_path(args.coverage_dir, kind="dir")
        for index, name in enumerate(required_coverage_names, start=1):
            try:
                coverage_file = local_path(str(coverage_dir / name), kind="file")
            except (OSError, SafetyError):
                errors[f"missing_coverage:{name}"] += 1
                continue
            digest, size = sha256_file(
                coverage_file,
                max_bytes=args.max_total_input_bytes,
            )
            coverage_files.append(
                {
                    "name": name,
                    "sha256": digest,
                    "size_bytes": size,
                }
            )
    else:
        warnings["coverage_generation_required"] += 1

    output_file = output_dir / f"universe_{args.method}.bed"
    if output_file.exists() or output_file.is_symlink():
        errors["output_file_already_exists"] += 1

    coverage_arg = (
        _render(coverage_dir, "LOCAL_COVERAGE_DIR", args.path_mode)
        if coverage_dir
        else "<LOCAL_COVERAGE_DIR>"
    )
    output_arg = _render(output_file, "OUTPUT_UNIVERSE_BED", args.path_mode)

    stages: list[dict] = [
        {
            "stage": "validate_beds",
            "executed": False,
            "instruction": (
                "Run bed_validator.py for every BED using the same chromosome sizes; "
                "reject any invalid result."
            ),
        },
        {
            "stage": "generate_coverage",
            "executed": False,
            "blocked": coverage_dir is None,
            "required_outputs": required_coverage_names,
            "instruction": (
                "Use an explicitly pinned and checksummed coverage executable. "
                "Capture its installed --help; this planner does not guess a Gtars/uniwig argv."
            ),
        },
    ]

    likelihood_path: Path | None = None
    if args.method == "ml":
        if args.likelihood_model:
            likelihood_path = local_path(args.likelihood_model, kind="file")
        else:
            likelihood_path = output_dir / "likelihood_model.tar"
            if likelihood_path.exists() or likelihood_path.is_symlink():
                errors["planned_likelihood_model_already_exists"] += 1
            lh_template = [
                "geniml",
                "lh",
                "--model-file",
                "<LIKELIHOOD_MODEL_TAR>",
                "--coverage-folder",
                "<LOCAL_COVERAGE_DIR>",
                "--coverage-prefix",
                args.coverage_prefix,
                "--file-no",
                str(len(set(local_beds))),
            ]
            lh_argv = None
            if args.path_mode == "full" and coverage_dir:
                lh_argv = [
                    "geniml",
                    "lh",
                    "--model-file",
                    str(likelihood_path),
                    "--coverage-folder",
                    str(coverage_dir),
                    "--coverage-prefix",
                    args.coverage_prefix,
                    "--file-no",
                    str(len(set(local_beds))),
                ]
            stages.append(
                {
                    "stage": "build_likelihood_model",
                    "executed": False,
                    "argv_template": lh_template,
                    "argv": lh_argv,
                }
            )

    command_template = [
        "geniml",
        "build-universe",
        args.method,
        "--coverage-folder",
        "<LOCAL_COVERAGE_DIR>",
        "--coverage-prefix",
        args.coverage_prefix,
        "--output-file",
        "<OUTPUT_UNIVERSE_BED>",
    ]
    command = [
        "geniml",
        "build-universe",
        args.method,
        "--coverage-folder",
        coverage_arg,
        "--coverage-prefix",
        args.coverage_prefix,
        "--output-file",
        output_arg,
    ]
    if args.method == "cc":
        if args.cutoff is not None:
            command_template.extend(["--cutoff", str(args.cutoff)])
            command.extend(["--cutoff", str(args.cutoff)])
            if args.cutoff > len(set(local_beds)):
                warnings["cutoff_exceeds_file_count"] += 1
        command_template.extend(["--merge", str(args.merge), "--filter-size", str(args.filter_size)])
        command.extend(["--merge", str(args.merge), "--filter-size", str(args.filter_size)])
    elif args.method == "ml":
        command_template.extend(["--model-file", "<LIKELIHOOD_MODEL_TAR>"])
        command.extend(
            [
                "--model-file",
                _render(
                    likelihood_path,
                    "LIKELIHOOD_MODEL_TAR",
                    args.path_mode,
                ),
            ]
        )
    elif args.method == "hmm":
        if args.no_normalize:
            command_template.append("--not-normalize")
            command.append("--not-normalize")
        if args.save_max_coverage:
            command_template.append("--save-max-cove")
            command.append("--save-max-cove")

    stages.append(
        {
            "stage": "build_universe",
            "executed": False,
            "argv_template": command_template,
            "argv": command if args.path_mode == "full" and coverage_dir else None,
        }
    )
    stages.append(
        {
            "stage": "validate_output",
            "executed": False,
            "instruction": (
                "Validate BED coordinates, sorting, contigs, bounds, nonempty output, "
                "and checksum before constructing a tokenizer."
            ),
        }
    )

    ready = not errors and coverage_dir is not None
    report = {
        "ok": not errors,
        "ready_to_execute": ready,
        "tool": TOOL,
        "contract": {
            "assembly": args.assembly,
            "coordinate_system": "0-based-half-open",
            "method": args.method,
            "network_used": False,
            "commands_executed": False,
            "paths_disclosed": args.path_mode == "full",
        },
        "inputs": {
            "manifest": {
                "path": display_path(manifest, 1, args.path_mode),
                "sha256": manifest_digest,
                "size_bytes": manifest_size,
            },
            "chromosome_sizes": {
                "path": display_path(chrom_sizes, 2, args.path_mode),
                "sha256": chrom_digest,
                "size_bytes": chrom_size_bytes,
                "contig_count": len(sizes),
                "first_contigs": contig_order[:10],
            },
            "bed_rows": len(rows),
            "unique_local_beds": len(set(local_beds)),
            "total_bed_bytes": total_input_bytes,
            "coverage_files": coverage_files,
        },
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "stages": stages,
        "provenance_requirements": [
            "patient/donor-grouped training-only manifest",
            "input BED and chromosome-sizes checksums",
            "coverage executable version, checksum, help output, and argv",
            "coverage-track and universe checksums",
            "Geniml/Gtars/Python lockfile and platform",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, exit_code = plan(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/corpus_auditor.py`

```python
#!/usr/bin/env python3
"""Audit a local interval manifest without exposing sample metadata values."""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_FILES,
    SafetyError,
    add_path_mode_argument,
    delimiter_from_path,
    display_path,
    fail_json,
    int_type,
    local_path,
    print_json,
    read_delimited_manifest,
    sha256_file,
)


TOOL = "interval-corpus-auditor"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a local CSV/TSV manifest for paths, assemblies, duplicate "
            "content, and patient/donor split leakage. Metadata values are not printed."
        )
    )
    parser.add_argument("--manifest", required=True, help="Local CSV/TSV manifest.")
    parser.add_argument(
        "--delimiter",
        choices=("auto", "csv", "tsv"),
        default="auto",
    )
    parser.add_argument(
        "--path-column",
        default="path",
        help="Column containing BED paths (default: path).",
    )
    parser.add_argument(
        "--assembly-column",
        default="assembly",
        help="Assembly column (default: assembly).",
    )
    parser.add_argument(
        "--expected-assembly",
        help="Optional expected assembly/accession.",
    )
    parser.add_argument(
        "--group-column",
        action="append",
        default=[],
        help="Patient/donor grouping column; repeat as needed.",
    )
    parser.add_argument(
        "--split-column",
        help="Train/validation/test column used for leakage checks.",
    )
    parser.add_argument(
        "--checksums",
        action="store_true",
        help="Hash each bounded BED to detect duplicate content.",
    )
    parser.add_argument(
        "--max-files",
        type=int_type(minimum=1, maximum=HARD_MAX_FILES, label="max-files"),
        default=10_000,
    )
    parser.add_argument(
        "--max-manifest-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-manifest-bytes",
        ),
        default=64 * 1024**2,
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-file-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-total-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-total-bytes"),
        default=4 * 1024**3,
    )
    parser.add_argument(
        "--max-output-files",
        type=int_type(minimum=0, maximum=1_000, label="max-output-files"),
        default=100,
        help="Maximum bounded per-file summaries (default: 100).",
    )
    add_path_mode_argument(parser)
    return parser


def _manifest_local_path(raw: str, manifest: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = manifest.parent / candidate
    return local_path(str(candidate), kind="file")


def audit(args: argparse.Namespace) -> tuple[dict, int]:
    manifest = local_path(args.manifest, kind="file")
    delimiter = delimiter_from_path(manifest, args.delimiter)
    fields, rows = read_delimited_manifest(
        manifest,
        delimiter_name=delimiter,
        max_bytes=args.max_manifest_bytes,
        max_rows=args.max_files,
    )
    if args.path_column not in fields:
        raise SafetyError(f"path column is missing: {args.path_column}")
    if args.split_column and args.split_column not in fields:
        raise SafetyError(f"split column is missing: {args.split_column}")
    if len(args.group_column) > 20:
        raise SafetyError("at most 20 group columns may be checked")
    missing_groups = [column for column in args.group_column if column not in fields]
    if missing_groups:
        raise SafetyError(f"group columns are missing: {', '.join(missing_groups)}")
    if args.expected_assembly and not args.expected_assembly.strip():
        raise SafetyError("expected assembly must not be blank")

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    path_counts: Counter[Path] = Counter()
    assembly_counts: Counter[str] = Counter()
    group_splits: dict[str, dict[str, set[str]]] = {
        column: defaultdict(set) for column in args.group_column
    }
    missing_group_values: Counter[str] = Counter()
    split_missing = 0
    total_bytes = 0
    file_summaries: list[dict] = []
    checksum_counts: Counter[str] = Counter()

    if args.assembly_column not in fields:
        warnings["assembly_column_missing"] += 1

    for row_index, row in enumerate(rows, start=1):
        raw_path = row.get(args.path_column, "")
        if not raw_path:
            errors["blank_path"] += 1
            continue
        try:
            bed_path = _manifest_local_path(raw_path, manifest)
        except (OSError, SafetyError):
            errors["invalid_or_missing_local_path"] += 1
            continue

        path_counts[bed_path] += 1
        size = bed_path.lstat().st_size
        if size > args.max_file_bytes:
            errors["file_exceeds_byte_limit"] += 1
            continue
        total_bytes += size
        if total_bytes > args.max_total_bytes:
            raise SafetyError("corpus exceeds max-total-bytes")
        lowered_name = bed_path.name.lower()
        if not (lowered_name.endswith(".bed") or lowered_name.endswith(".bed.gz")):
            warnings["nonstandard_bed_extension"] += 1

        assembly = row.get(args.assembly_column, "") if args.assembly_column in fields else ""
        if assembly:
            if len(assembly) > 200:
                errors["assembly_value_too_long"] += 1
            else:
                assembly_counts[assembly] += 1
                if args.expected_assembly and assembly != args.expected_assembly:
                    errors["unexpected_assembly"] += 1
        elif args.assembly_column in fields:
            errors["blank_assembly"] += 1

        split = row.get(args.split_column, "") if args.split_column else ""
        if args.split_column and not split:
            split_missing += 1
        for group_column in args.group_column:
            group_value = row.get(group_column, "")
            if not group_value:
                missing_group_values[group_column] += 1
            elif args.split_column and split:
                group_splits[group_column][group_value].add(split)

        checksum: str | None = None
        if args.checksums:
            checksum, _ = sha256_file(bed_path, max_bytes=args.max_file_bytes)
            checksum_counts[checksum] += 1
        if len(file_summaries) < args.max_output_files:
            summary = {
                "path": display_path(bed_path, row_index, args.path_mode),
                "size_bytes": size,
            }
            if checksum:
                summary["sha256"] = checksum
            file_summaries.append(summary)

    duplicate_path_rows = sum(count - 1 for count in path_counts.values() if count > 1)
    if duplicate_path_rows:
        warnings["duplicate_path_rows"] = duplicate_path_rows
    if len(assembly_counts) > 1:
        errors["mixed_assemblies"] = len(assembly_counts)
    if not assembly_counts:
        warnings["assembly_not_recorded"] += 1
    if split_missing:
        errors["blank_split"] = split_missing
    for column, count in missing_group_values.items():
        if count:
            errors[f"blank_group:{column}"] = count

    leakage: dict[str, dict[str, int]] = {}
    for column, groups in group_splits.items():
        crossing = sum(1 for splits in groups.values() if len(splits) > 1)
        leakage[column] = {
            "distinct_groups": len(groups),
            "groups_crossing_splits": crossing,
        }
        if crossing:
            errors[f"group_leakage:{column}"] = crossing

    duplicate_content_groups = 0
    duplicate_content_files = 0
    if args.checksums:
        duplicate_content_groups = sum(1 for count in checksum_counts.values() if count > 1)
        duplicate_content_files = sum(
            count for count in checksum_counts.values() if count > 1
        )
        if duplicate_content_groups:
            warnings["duplicate_content_groups"] = duplicate_content_groups

    manifest_digest, manifest_size = sha256_file(
        manifest,
        max_bytes=args.max_manifest_bytes,
    )
    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "network_used": False,
            "metadata_values_emitted": False,
            "symlinks_allowed": False,
        },
        "manifest": {
            "path": display_path(manifest, 0, args.path_mode),
            "sha256": manifest_digest,
            "size_bytes": manifest_size,
            "delimiter": delimiter,
            "column_count": len(fields),
            "column_names_emitted": False,
        },
        "summary": {
            "manifest_rows": len(rows),
            "valid_local_file_rows": sum(path_counts.values()),
            "unique_local_files": len(path_counts),
            "total_input_bytes": total_bytes,
            "assembly_count": len(assembly_counts),
            "assemblies": (
                sorted(assembly_counts)[:20]
                if args.path_mode == "full"
                else "<redacted>"
            ),
            "duplicate_path_rows": duplicate_path_rows,
            "duplicate_content_groups": duplicate_content_groups,
            "duplicate_content_files": duplicate_content_files,
            "file_summaries_omitted": max(
                0,
                sum(path_counts.values()) - len(file_summaries),
            ),
        },
        "leakage_checks": leakage,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "files": file_summaries,
        "recommendations": [
            "keep every patient/donor/biological replicate in exactly one split",
            "build universes and fit preprocessing on training groups only",
            "validate each BED against one checksummed chromosome-sizes file",
            "store full metadata only in the protected project manifest",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, exit_code = audit(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/embedding_plan.py`

```python
#!/usr/bin/env python3
"""Plan a bounded local Geniml embedding run without importing ML packages."""

from __future__ import annotations

import argparse
import os
import stat
import sys
from collections import Counter
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_EPOCHS,
    HARD_MAX_WORKERS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    int_type,
    local_path,
    print_json,
    sha256_file,
    simple_yaml_mapping,
)


TOOL = "embedding-run-planner"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate local inputs and emit a redacted Region2Vec, scEmbed, or "
            "BEDspace run plan. No package, model, binary, or network call is executed."
        )
    )
    parser.add_argument("--mode", choices=("region2vec", "scembed", "bedspace"), required=True)
    parser.add_argument("--data", required=True, help="Token Parquet or BED directory.")
    parser.add_argument("--metadata", help="BEDspace metadata CSV.")
    parser.add_argument("--universe", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-dir", help="Optional trusted local model bundle.")
    parser.add_argument("--starspace-dir", help="BEDspace-only local StarSpace directory.")
    parser.add_argument("--assembly", required=True)
    parser.add_argument(
        "--split-unit",
        choices=("patient", "donor", "biological-replicate", "sample", "cell"),
        default="patient",
    )
    parser.add_argument(
        "--embedding-dim",
        type=int_type(minimum=1, maximum=4096, label="embedding-dim"),
        default=100,
    )
    parser.add_argument(
        "--epochs",
        type=int_type(minimum=1, maximum=HARD_MAX_EPOCHS, label="epochs"),
        default=10,
    )
    parser.add_argument(
        "--workers",
        type=int_type(minimum=1, maximum=HARD_MAX_WORKERS, label="workers"),
        default=4,
    )
    parser.add_argument(
        "--window-size",
        type=int_type(minimum=1, maximum=100_000, label="window-size"),
        default=5,
    )
    parser.add_argument(
        "--min-count",
        type=int_type(minimum=1, maximum=10_000_000, label="min-count"),
        default=10,
    )
    parser.add_argument(
        "--batch-size",
        type=int_type(minimum=1, maximum=1_000_000, label="batch-size"),
        default=64,
    )
    parser.add_argument(
        "--seed",
        type=int_type(minimum=0, maximum=2**32 - 1, label="seed"),
        default=42,
    )
    parser.add_argument("--pooling", choices=("mean", "max"), default="mean")
    parser.add_argument("--geniml-version", default="0.8.4")
    parser.add_argument("--gtars-version", default="0.9.2")
    parser.add_argument(
        "--max-file-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-file-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-total-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-total-bytes"),
        default=4 * 1024**3,
    )
    add_path_mode_argument(parser)
    return parser


def _parquet_magic(path: Path) -> bool:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_size < 8:
            return False
        first = os.read(descriptor, 4)
        os.lseek(descriptor, -4, os.SEEK_END)
        last = os.read(descriptor, 4)
        return first == b"PAR1" and last == b"PAR1"
    finally:
        os.close(descriptor)


def _render(path: Path, label: str, mode: str) -> str:
    if mode == "full":
        return str(path)
    if mode == "basename":
        return path.name
    return f"<{label}>"


def plan(args: argparse.Namespace) -> tuple[dict, int]:
    if not args.assembly.strip() or len(args.assembly) > 200:
        raise SafetyError("assembly must be a nonempty value of at most 200 characters")
    if args.mode != "bedspace" and (args.metadata or args.starspace_dir):
        raise SafetyError("metadata and starspace-dir apply only to bedspace")
    if args.mode == "bedspace" and not args.metadata:
        raise SafetyError("bedspace requires --metadata")
    if args.mode == "bedspace" and args.model_dir:
        raise SafetyError("model-dir applies only to Region2Vec or scEmbed bundles")

    data = local_path(args.data, kind="dir" if args.mode == "bedspace" else "file")
    universe = local_path(args.universe, kind="file")
    output_dir = local_path(args.output_dir, kind="dir")
    model_dir = local_path(args.model_dir, kind="dir") if args.model_dir else None
    metadata = local_path(args.metadata, kind="file") if args.metadata else None
    starspace_dir = (
        local_path(args.starspace_dir, kind="dir") if args.starspace_dir else None
    )

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    if args.split_unit == "cell":
        errors["nonindependent_split_unit:cell"] += 1
    elif args.split_unit == "sample":
        warnings["verify_samples_are_independent_across_patients"] += 1
    if any(output_dir.iterdir()):
        warnings["output_directory_not_empty"] += 1

    universe_digest, universe_size = sha256_file(
        universe,
        max_bytes=args.max_file_bytes,
    )
    input_summary: dict[str, object] = {
        "data": display_path(data, 1, args.path_mode),
        "universe": display_path(universe, 2, args.path_mode),
        "universe_sha256": universe_digest,
        "universe_size_bytes": universe_size,
        "output_dir": display_path(output_dir, 3, args.path_mode),
    }

    if args.mode in {"region2vec", "scembed"}:
        data_digest, data_size = sha256_file(data, max_bytes=args.max_file_bytes)
        parquet_ok = _parquet_magic(data)
        if not parquet_ok:
            errors["data_not_parquet"] += 1
        input_summary.update(
            {
                "data_sha256": data_digest,
                "data_size_bytes": data_size,
                "parquet_magic_valid": parquet_ok,
                "parquet_schema_inspected": False,
            }
        )
    else:
        bed_entries = list(data.iterdir())
        if len(bed_entries) > 100_000:
            raise SafetyError("BEDspace input directory exceeds 100,000 entries")
        symlinks = sum(1 for entry in bed_entries if entry.is_symlink())
        special = sum(
            1
            for entry in bed_entries
            if not entry.is_symlink() and not entry.is_file()
        )
        if symlinks:
            errors["bedspace_data_symlinks"] = symlinks
        if special:
            errors["bedspace_non_file_entries"] = special
        total_bed_bytes = 0
        oversized_beds = 0
        for entry in bed_entries:
            if entry.is_symlink() or not entry.is_file():
                continue
            size = entry.lstat().st_size
            total_bed_bytes += size
            if size > args.max_file_bytes:
                oversized_beds += 1
            if total_bed_bytes > args.max_total_bytes:
                raise SafetyError("BEDspace input directory exceeds max-total-bytes")
        if oversized_beds:
            errors["bedspace_files_exceed_byte_limit"] = oversized_beds
        metadata_digest, metadata_size = sha256_file(
            metadata,
            max_bytes=args.max_file_bytes,
        )
        input_summary.update(
            {
                "bed_directory_entries": len(bed_entries),
                "bed_directory_bytes": total_bed_bytes,
                "metadata": display_path(metadata, 4, args.path_mode),
                "metadata_sha256": metadata_digest,
                "metadata_size_bytes": metadata_size,
                "metadata_values_emitted": False,
            }
        )

    model_summary = None
    if model_dir:
        config = local_path(str(model_dir / "config.yaml"), kind="file")
        checkpoint = local_path(str(model_dir / "checkpoint.pt"), kind="file")
        bundle_universe = local_path(str(model_dir / "universe.bed"), kind="file")
        config_metadata = simple_yaml_mapping(
            config,
            max_bytes=min(args.max_file_bytes, 16 * 1024**2),
        )
        config_digest, config_size = sha256_file(
            config,
            max_bytes=min(args.max_file_bytes, 16 * 1024**2),
        )
        checkpoint_digest, checkpoint_size = sha256_file(
            checkpoint,
            max_bytes=args.max_file_bytes,
        )
        bundle_digest, bundle_size = sha256_file(
            bundle_universe,
            max_bytes=args.max_file_bytes,
        )
        if bundle_digest != universe_digest:
            errors["model_universe_checksum_mismatch"] += 1
        if config_metadata.get("embedding_dim", config_metadata.get("embedding_size")) != (
            args.embedding_dim
        ):
            warnings["planned_embedding_dim_differs_from_model"] += 1
        model_summary = {
            "path": display_path(model_dir, 5, args.path_mode),
            "config_sha256": config_digest,
            "config_size_bytes": config_size,
            "checkpoint_sha256": checkpoint_digest,
            "checkpoint_size_bytes": checkpoint_size,
            "bundle_universe_sha256": bundle_digest,
            "bundle_universe_size_bytes": bundle_size,
            "metadata": {
                "vocab_size": config_metadata.get("vocab_size"),
                "embedding_dim": config_metadata.get(
                    "embedding_dim",
                    config_metadata.get("embedding_size"),
                ),
                "pooling_method": config_metadata.get("pooling_method"),
            },
            "deserialized": False,
        }

    stages: list[dict] = [
        {
            "stage": "environment",
            "executed": False,
            "requirements": [
                f"geniml[ml]=={args.geniml_version}",
                f"gtars=={args.gtars_version}",
            ],
            "instruction": "resolve with uv and retain the generated lockfile",
        },
        {
            "stage": "data_contract",
            "executed": False,
            "instruction": (
                "verify 0-based half-open coordinates, one assembly/chromosome-sizes "
                "digest, bounded token counts, and patient/donor-grouped splits"
            ),
        },
    ]

    if args.mode == "region2vec":
        stages.extend(
            [
                {
                    "stage": "api_smoke",
                    "executed": False,
                    "imports": [
                        "geniml.region2vec.main.Region2VecExModel",
                        "geniml.region2vec.utils.Region2VecDataset",
                        "gtars.tokenizers.Tokenizer",
                    ],
                    "note": "do not use the broken 0.8.4 top-level region2vec export",
                },
                {
                    "stage": "train",
                    "executed": False,
                    "parameters": {
                        "embedding_dim": args.embedding_dim,
                        "epochs": args.epochs,
                        "window_size": args.window_size,
                        "min_count": args.min_count,
                        "num_cpus": args.workers,
                        "seed": args.seed,
                        "pooling_method": args.pooling,
                    },
                },
            ]
        )
    elif args.mode == "scembed":
        stages.extend(
            [
                {
                    "stage": "api_smoke",
                    "executed": False,
                    "imports": [
                        "geniml.scembed.main.ScEmbed",
                        "geniml.region2vec.utils.Region2VecDataset",
                        "gtars.tokenizers.Tokenizer",
                    ],
                    "note": (
                        "synthetically test ScEmbed.encode token shape with the pinned "
                        "Gtars version before real data"
                    ),
                },
                {
                    "stage": "train",
                    "executed": False,
                    "parameters": {
                        "embedding_dim": args.embedding_dim,
                        "epochs": args.epochs,
                        "window_size": args.window_size,
                        "min_count": args.min_count,
                        "num_cpus": args.workers,
                        "seed": args.seed,
                        "pooling_method": args.pooling,
                    },
                },
            ]
        )
    else:
        starspace_summary = None
        if starspace_dir:
            binary = local_path(str(starspace_dir / "starspace"), kind="file")
            binary_digest, binary_size = sha256_file(
                binary,
                max_bytes=args.max_file_bytes,
            )
            starspace_summary = {
                "directory": display_path(starspace_dir, 6, args.path_mode),
                "binary_sha256": binary_digest,
                "binary_size_bytes": binary_size,
                "executed": False,
            }
        else:
            warnings["starspace_binary_required"] += 1
        preprocess_template = [
            "geniml",
            "bedspace",
            "preprocess",
            "--input",
            "<LOCAL_BED_DIRECTORY>",
            "--metadata",
            "<LOCAL_METADATA_CSV>",
            "--universe",
            "<LOCAL_UNIVERSE_BED>",
            "--output",
            "<LOCAL_OUTPUT_DIRECTORY_WITH_TRAILING_SEPARATOR>",
        ]
        train_template = [
            "geniml",
            "bedspace",
            "train",
            "-s",
            "<LOCAL_STARSPACE_DIRECTORY>",
            "--input",
            "<LOCAL_OUTPUT_DIRECTORY>/train_input.txt",
            "--output",
            "<LOCAL_OUTPUT_DIRECTORY>",
            "--dim",
            str(args.embedding_dim),
            "--epochs",
            str(args.epochs),
        ]
        stages.extend(
            [
                {
                    "stage": "legacy_dependency_review",
                    "executed": False,
                    "starspace": starspace_summary,
                    "note": (
                        "StarSpace is archived; Geniml has no compatibility pin and "
                        "hard-codes 20 training threads"
                    ),
                },
                {
                    "stage": "preprocess",
                    "executed": False,
                    "argv_template": preprocess_template,
                },
                {
                    "stage": "train",
                    "executed": False,
                    "argv_template": train_template,
                    "note": "the 0.8.4 bedspace search dispatcher is not usable",
                },
            ]
        )

    stages.append(
        {
            "stage": "export_and_verify",
            "executed": False,
            "instruction": (
                "export to a fresh directory, copy the exact universe.bed, create "
                "SHA-256 provenance, and inspect without deserialization"
            ),
            "expected_local_output": _render(
                output_dir,
                "LOCAL_OUTPUT_DIRECTORY",
                args.path_mode,
            ),
        }
    )

    report = {
        "ok": not errors,
        "ready_to_execute": not errors
        and (args.mode != "bedspace" or starspace_dir is not None),
        "tool": TOOL,
        "contract": {
            "mode": args.mode,
            "assembly": args.assembly,
            "coordinate_system": "0-based-half-open",
            "split_unit": args.split_unit,
            "network_used": False,
            "packages_imported": False,
            "models_deserialized": False,
            "commands_executed": False,
        },
        "inputs": input_summary,
        "existing_model": model_summary,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "stages": stages,
        "required_postconditions": [
            "token IDs are within the pinned tokenizer vocabulary",
            "universe bytes/order and special-token IDs match model config",
            "all output artifacts have provenance and SHA-256 checksums",
            "evaluation uses patients/donors excluded from fitting and model selection",
            "logs contain aggregate/redacted values only",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, exit_code = plan(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/model_artifact_inspector.py`

```python
#!/usr/bin/env python3
"""Inspect local model artifacts and checksums without deserialization."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
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
    simple_yaml_mapping,
)


TOOL = "model-artifact-inspector"
_HASH_LINE = re.compile(r"^([0-9a-fA-F]{64})[ \t]+[* ]?(.+?)$")
_DESERIALIZATION_RISK = {
    ".pt",
    ".pth",
    ".ckpt",
    ".bin",
    ".pkl",
    ".pickle",
    ".joblib",
    ".model",
}
_NATIVE_RISK = {".so", ".dylib", ".dll", ".exe"}
_ARCHIVE_RISK = {".tar", ".zip", ".tgz", ".gz", ".bz2", ".xz"}
_METADATA_KEYS = {
    "architectures",
    "embedding_dim",
    "embedding_size",
    "model_type",
    "pooling_method",
    "vocab_size",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory and hash a local Geniml model bundle without importing "
            "ML libraries, extracting archives, or deserializing model files."
        )
    )
    parser.add_argument("--model-dir", required=True)
    parser.add_argument(
        "--verify-manifest",
        help="Optional local SHA256SUMS-style manifest.",
    )
    parser.add_argument(
        "--max-files",
        type=int_type(minimum=1, maximum=HARD_MAX_FILES, label="max-files"),
        default=1_000,
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-file-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-total-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-total-bytes"),
        default=4 * 1024**3,
    )
    parser.add_argument(
        "--max-output-files",
        type=int_type(minimum=0, maximum=5_000, label="max-output-files"),
        default=200,
    )
    add_path_mode_argument(parser)
    return parser


def _walk_regular_files(root: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            ordered = sorted(entries, key=lambda entry: entry.name)
        for entry in ordered:
            path = Path(entry.path)
            if entry.is_symlink():
                raise SafetyError("symlink is not allowed in model bundle")
            if entry.is_dir(follow_symlinks=False):
                pending.append(path)
            elif entry.is_file(follow_symlinks=False):
                files.append(path)
                if len(files) > max_files:
                    raise SafetyError("model bundle exceeds max-files")
            else:
                raise SafetyError("special filesystem entry is not allowed")
    return sorted(files)


def _risk_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in _DESERIALIZATION_RISK:
        return "deserialization"
    if suffix in _NATIVE_RISK:
        return "native-executable"
    if suffix in _ARCHIVE_RISK:
        return "archive-expansion"
    if suffix == ".safetensors":
        return "bounded-format-still-untrusted"
    return "data-or-metadata"


def _safe_json(path: Path, max_bytes: int):
    lines = [
        line
        for _, line in iter_text_lines(
            path,
            max_bytes=max_bytes,
            max_records=100_000,
        )
    ]
    try:
        return json.loads("\n".join(lines))
    except json.JSONDecodeError as exc:
        raise SafetyError("invalid JSON metadata") from exc


def _read_checksum_manifest(
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
        match = _HASH_LINE.fullmatch(line)
        if not match:
            raise SafetyError(f"invalid checksum manifest line {line_number}")
        digest, name = match.groups()
        relative = Path(name)
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or not relative.parts
            or "://" in name
            or name.startswith("~")
        ):
            raise SafetyError(f"unsafe checksum path at line {line_number}")
        normalized = relative.as_posix()
        if normalized in expected:
            raise SafetyError(f"duplicate checksum entry at line {line_number}")
        expected[normalized] = digest.lower()
        if len(expected) > max_files:
            raise SafetyError("checksum manifest exceeds max-files")
    return expected


def _redacted_metadata(value) -> tuple[dict[str, object], int]:
    if not isinstance(value, dict):
        raise SafetyError("config metadata must be a mapping")
    selected: dict[str, object] = {}
    for key in _METADATA_KEYS:
        if key not in value:
            continue
        item = value[key]
        if isinstance(item, (str, int, float, bool)) or item is None:
            if isinstance(item, str) and len(item) > 200:
                selected[key] = "<redacted-long-string>"
            else:
                selected[key] = item
        elif key == "architectures" and isinstance(item, list):
            selected[key] = [
                entry if isinstance(entry, str) and len(entry) <= 100 else "<redacted>"
                for entry in item[:20]
            ]
    return selected, max(0, len(value) - len(selected))


def inspect(args: argparse.Namespace) -> tuple[dict, int]:
    model_dir = local_path(args.model_dir, kind="dir")
    files = _walk_regular_files(model_dir, args.max_files)
    if not files:
        raise SafetyError("model directory is empty")

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    risk_counts: Counter[str] = Counter()
    computed: dict[str, str] = {}
    summaries: list[dict] = []
    metadata: dict[str, object] = {}
    total_bytes = 0

    for index, path in enumerate(files, start=1):
        relative = path.relative_to(model_dir).as_posix()
        size = path.lstat().st_size
        if size > args.max_file_bytes:
            errors["file_exceeds_byte_limit"] += 1
            continue
        total_bytes += size
        if total_bytes > args.max_total_bytes:
            raise SafetyError("model bundle exceeds max-total-bytes")
        digest, hashed_size = sha256_file(path, max_bytes=args.max_file_bytes)
        computed[relative] = digest
        risk = _risk_for(path)
        risk_counts[risk] += 1
        if risk in {"deserialization", "native-executable", "archive-expansion"}:
            warnings[f"risky_artifact:{risk}"] += 1

        if path.name in {"config.yaml", "config.yml"}:
            parsed = simple_yaml_mapping(
                path,
                max_bytes=min(args.max_file_bytes, 16 * 1024**2),
            )
            selected, omitted = _redacted_metadata(parsed)
            metadata[path.name] = selected
            if omitted:
                warnings["config_metadata_fields_redacted"] += omitted
        elif path.name in {"config.json", "tokenizer_config.json"}:
            parsed = _safe_json(
                path,
                max_bytes=min(args.max_file_bytes, 16 * 1024**2),
            )
            selected, omitted = _redacted_metadata(parsed)
            metadata[path.name] = selected
            if omitted:
                warnings["config_metadata_fields_redacted"] += omitted

        if len(summaries) < args.max_output_files:
            if args.path_mode == "redacted":
                shown_path = f"artifact_{index:04d}"
            elif args.path_mode == "basename":
                shown_path = path.name
            else:
                shown_path = str(path)
            summaries.append(
                {
                    "path": shown_path,
                    "sha256": digest,
                    "size_bytes": hashed_size,
                    "risk_class": risk,
                    "deserialized": False,
                }
            )

    standard = {
        name: name in computed for name in ("checkpoint.pt", "config.yaml", "universe.bed")
    }
    for name, present in standard.items():
        if not present:
            errors[f"missing_standard_artifact:{name}"] += 1

    verification = None
    if args.verify_manifest:
        manifest = local_path(args.verify_manifest, kind="file")
        expected = _read_checksum_manifest(
            manifest,
            max_bytes=min(args.max_file_bytes, 64 * 1024**2),
            max_files=args.max_files,
        )
        missing = sorted(set(expected) - set(computed))
        unlisted = sorted(set(computed) - set(expected))
        mismatched = sorted(
            name
            for name in set(expected) & set(computed)
            if expected[name] != computed[name]
        )
        if missing:
            errors["checksum_manifest_missing_files"] = len(missing)
        if mismatched:
            errors["checksum_mismatches"] = len(mismatched)
        if unlisted:
            warnings["files_not_listed_in_checksum_manifest"] = len(unlisted)
        verification = {
            "manifest": display_path(manifest, 2, args.path_mode),
            "expected_entries": len(expected),
            "missing_count": len(missing),
            "mismatch_count": len(mismatched),
            "unlisted_count": len(unlisted),
            "verified": not missing and not mismatched,
        }

    config = metadata.get("config.yaml")
    if isinstance(config, dict):
        vocab_size = config.get("vocab_size")
        embedding_dim = config.get("embedding_dim", config.get("embedding_size"))
        if not isinstance(vocab_size, int) or vocab_size <= 0:
            errors["config:invalid_vocab_size"] += 1
        if not isinstance(embedding_dim, int) or embedding_dim <= 0:
            errors["config:invalid_embedding_dim"] += 1
        if "embedding_size" in config and "embedding_dim" not in config:
            warnings["config:deprecated_embedding_size_key"] += 1

    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "network_used": False,
            "model_deserialized": False,
            "archives_extracted": False,
            "dynamic_imports_used": False,
            "symlinks_allowed": False,
        },
        "model_dir": display_path(model_dir, 1, args.path_mode),
        "summary": {
            "file_count": len(files),
            "hashed_file_count": len(computed),
            "total_bytes": total_bytes,
            "output_file_summaries": len(summaries),
            "omitted_file_summaries": max(0, len(files) - len(summaries)),
            "risk_classes": dict(sorted(risk_counts.items())),
            "standard_artifacts": standard,
        },
        "metadata": metadata,
        "checksum_verification": verification,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "files": summaries,
        "loading_policy": [
            "verify provenance and checksums before loading",
            "never inspect .pt/.model/pickle/joblib by deserializing it",
            "load only in an isolated environment with CPU, RAM, disk, and time bounds",
            "compare universe bytes/order, tokenizer special IDs, vocab size, and assembly",
            "treat native binaries and archives as independently untrusted",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, exit_code = inspect(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/tokenizer_compatibility.py`

```python
#!/usr/bin/env python3
"""Plan local tokenizer/universe/model compatibility checks without imports."""

from __future__ import annotations

import argparse
import os
import stat
import sys
from collections import Counter
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    MAX_COORDINATE,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    int_type,
    iter_text_lines,
    local_path,
    print_json,
    sha256_file,
    simple_yaml_mapping,
)


TOOL = "tokenizer-universe-compatibility"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a local model bundle and universe using checksums and bounded "
            "metadata only. No model is deserialized and no package is imported."
        )
    )
    parser.add_argument("--model-dir", required=True, help="Local model bundle directory.")
    parser.add_argument("--universe", required=True, help="Expected local universe BED.")
    parser.add_argument("--assembly", required=True, help="Declared assembly/accession.")
    parser.add_argument("--config-name", default="config.yaml")
    parser.add_argument("--checkpoint-name", default="checkpoint.pt")
    parser.add_argument("--bundle-universe-name", default="universe.bed")
    parser.add_argument(
        "--token-corpus",
        help="Optional local Parquet token corpus to fingerprint (not parsed).",
    )
    parser.add_argument("--geniml-version", default="0.8.4")
    parser.add_argument("--gtars-version", default="0.9.2")
    parser.add_argument(
        "--special-token-count",
        type=int_type(minimum=0, maximum=100, label="special-token-count"),
        default=7,
        help="Expected Gtars special tokens (0.9.2 default: 7).",
    )
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-universe-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-universe-records",
        ),
        default=5_000_000,
    )
    add_path_mode_argument(parser)
    return parser


def _safe_child(directory: Path, name: str) -> Path:
    if not name or Path(name).name != name or name in {".", ".."}:
        raise SafetyError("artifact names must be plain filenames")
    return local_path(str(directory / name), kind="file")


def _count_universe(
    path: Path,
    *,
    max_bytes: int,
    max_records: int,
) -> tuple[int, int, Counter[str]]:
    records = 0
    duplicates = 0
    issues: Counter[str] = Counter()
    seen: set[tuple[str, int, int]] = set()
    for _, line in iter_text_lines(
        path,
        max_bytes=max_bytes,
        max_records=max_records,
    ):
        if not line or line.startswith("#") or line.startswith("track") or line.startswith("browser"):
            continue
        fields = line.split("\t")
        if len(fields) < 3:
            issues["fewer_than_three_columns"] += 1
            continue
        chrom = fields[0]
        try:
            start = int(fields[1])
            end = int(fields[2])
        except ValueError:
            issues["non_integer_coordinate"] += 1
            continue
        if (
            not chrom
            or start < 0
            or end <= start
            or start > MAX_COORDINATE
            or end > MAX_COORDINATE
        ):
            issues["invalid_interval"] += 1
            continue
        records += 1
        key = (chrom, start, end)
        if key in seen:
            duplicates += 1
        else:
            seen.add(key)
    return records, duplicates, issues


def _parquet_magic(path: Path) -> bool:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        mode = os.fstat(descriptor).st_mode
        size = os.fstat(descriptor).st_size
        if not stat.S_ISREG(mode) or size < 8:
            return False
        first = os.read(descriptor, 4)
        os.lseek(descriptor, -4, os.SEEK_END)
        last = os.read(descriptor, 4)
        return first == b"PAR1" and last == b"PAR1"
    finally:
        os.close(descriptor)


def inspect(args: argparse.Namespace) -> tuple[dict, int]:
    if not args.assembly.strip() or len(args.assembly) > 200:
        raise SafetyError("assembly must be a nonempty value of at most 200 characters")
    model_dir = local_path(args.model_dir, kind="dir")
    expected_universe = local_path(args.universe, kind="file")
    config_path = _safe_child(model_dir, args.config_name)
    checkpoint_path = _safe_child(model_dir, args.checkpoint_name)
    bundle_universe = _safe_child(model_dir, args.bundle_universe_name)

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    checks: list[dict[str, str | int | bool | None]] = []

    expected_digest, expected_size = sha256_file(
        expected_universe,
        max_bytes=args.max_bytes,
    )
    bundle_digest, bundle_size = sha256_file(
        bundle_universe,
        max_bytes=args.max_bytes,
    )
    universe_rows, duplicate_rows, universe_issues = _count_universe(
        expected_universe,
        max_bytes=args.max_bytes,
        max_records=args.max_universe_records,
    )
    for code, count in universe_issues.items():
        errors[f"universe:{code}"] = count
    if duplicate_rows:
        errors["universe:duplicate_intervals"] = duplicate_rows
    if universe_rows == 0:
        errors["universe:no_valid_records"] += 1

    universe_match = expected_digest == bundle_digest
    if not universe_match:
        errors["bundle_universe_checksum_mismatch"] += 1
    checks.append(
        {
            "check": "exact_universe_bytes_and_order",
            "passed": universe_match,
            "expected_sha256": expected_digest,
            "bundle_sha256": bundle_digest,
        }
    )

    config = simple_yaml_mapping(
        config_path,
        max_bytes=min(args.max_bytes, 16 * 1024**2),
    )
    vocab_size = config.get("vocab_size")
    embedding_dim = config.get("embedding_dim")
    old_embedding_dim = config.get("embedding_size")
    if embedding_dim is None and old_embedding_dim is not None:
        embedding_dim = old_embedding_dim
        warnings["deprecated_config_key:embedding_size"] += 1
    if not isinstance(vocab_size, int) or vocab_size <= 0:
        errors["config:invalid_vocab_size"] += 1
    if not isinstance(embedding_dim, int) or embedding_dim <= 0:
        errors["config:invalid_embedding_dim"] += 1
    pooling = config.get("pooling_method")
    if pooling is not None and pooling not in {"mean", "max"}:
        errors["config:invalid_pooling_method"] += 1

    expected_vocab_size = universe_rows + args.special_token_count
    vocab_match = isinstance(vocab_size, int) and vocab_size == expected_vocab_size
    if not vocab_match:
        errors["model_tokenizer_vocab_size_mismatch"] += 1
    checks.append(
        {
            "check": "vocab_size_equals_universe_plus_special_tokens",
            "passed": vocab_match,
            "model_vocab_size": vocab_size,
            "universe_records": universe_rows,
            "special_token_count": args.special_token_count,
            "expected_vocab_size": expected_vocab_size,
        }
    )

    config_digest, config_size = sha256_file(
        config_path,
        max_bytes=min(args.max_bytes, 16 * 1024**2),
    )
    checkpoint_digest, checkpoint_size = sha256_file(
        checkpoint_path,
        max_bytes=args.max_bytes,
    )
    if checkpoint_size == 0:
        errors["checkpoint:empty"] += 1

    token_corpus_summary = None
    if args.token_corpus:
        token_path = local_path(args.token_corpus, kind="file")
        token_digest, token_size = sha256_file(token_path, max_bytes=args.max_bytes)
        magic_ok = _parquet_magic(token_path)
        if not magic_ok:
            errors["token_corpus:invalid_parquet_magic"] += 1
        token_corpus_summary = {
            "path": display_path(token_path, 4, args.path_mode),
            "sha256": token_digest,
            "size_bytes": token_size,
            "parquet_magic_valid": magic_ok,
            "schema_inspected": False,
        }

    warnings["assembly_provenance_not_embedded_in_standard_config"] += 1
    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": args.assembly,
            "coordinate_system": "0-based-half-open",
            "geniml_version": args.geniml_version,
            "gtars_version": args.gtars_version,
            "network_used": False,
            "model_deserialized": False,
        },
        "paths": {
            "model_dir": display_path(model_dir, 1, args.path_mode),
            "expected_universe": display_path(expected_universe, 2, args.path_mode),
            "bundle_universe": display_path(bundle_universe, 3, args.path_mode),
        },
        "artifacts": {
            "checkpoint": {
                "name": checkpoint_path.name,
                "sha256": checkpoint_digest,
                "size_bytes": checkpoint_size,
                "deserialized": False,
            },
            "config": {
                "name": config_path.name,
                "sha256": config_digest,
                "size_bytes": config_size,
                "metadata": {
                    "vocab_size": vocab_size,
                    "embedding_dim": embedding_dim,
                    "pooling_method": pooling,
                },
            },
            "expected_universe": {
                "sha256": expected_digest,
                "size_bytes": expected_size,
                "records": universe_rows,
                "duplicate_intervals": duplicate_rows,
            },
            "bundle_universe": {
                "sha256": bundle_digest,
                "size_bytes": bundle_size,
            },
            "token_corpus": token_corpus_summary,
        },
        "checks": checks,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "next_checks": [
            "compare assembly accession and chromosome-sizes checksum",
            "instantiate the pinned tokenizer only after this plan passes",
            "verify every special-token name and ID in a synthetic smoke test",
            "verify all token IDs are in range and Parquet has one list-valued tokens column",
            "load the checkpoint only in an isolated, resource-bounded environment",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, exit_code = inspect(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
```
