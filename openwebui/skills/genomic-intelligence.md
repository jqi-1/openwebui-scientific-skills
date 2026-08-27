---
name: genomic-intelligence
description: Optional gi_ bearer key for the REST /v1 API and a higher MCP quota. The hosted MCP demo runs keyless; request a key at contact@genomicintelligence.ai.
---

# Genomic Intelligence — DNA Sequence Models

Genomic Intelligence (GI) serves transformer DNA language models over six
sequence-analysis tasks on managed GPUs. Give it a **gene symbol**, a **genomic
region**, or a **DNA/FASTA sequence**; it returns structured predictions —
promoter regions, splice sites, enhancer activity, chromatin state, expression
(log TPM), and de-novo gene annotation. Nothing runs locally: no model weights,
no GPU, no heavy Python stack. It is a thin client over a hosted, versioned
inference API.

**Official docs:** [docs.genomicintelligence.ai](https://docs.genomicintelligence.ai) ·
REST contract at [api.genomicintelligence.ai/v1/openapi.json](https://api.genomicintelligence.ai/v1/openapi.json) ·
hosted MCP server at `https://mcp.genomicintelligence.ai/mcp`

## When to use this skill

Use GI when the user has DNA and wants a model prediction:

- **Find promoters** in a genomic region (`promoter`)
- **Predict splice** donor/acceptor sites (`splice`)
- **Score enhancer activity** — developmental & housekeeping (`enhancer`)
- **Annotate chromatin state** across hundreds of tracks (`chromatin`)
- **Predict expression** as log(TPM+1) from a sequence + cell-type context (`expression`)
- **Annotate genes/transcripts** de novo, no reference needed (`annotation`)
- **Find the genes in a region and predict each one's expression** (composite)

Not for local alignment, variant calling, or file I/O — use a local tool
(BioPython, bcftools) for those. GI is for **model inference from sequence**.

> For research and development use, **not clinical or diagnostic decisions**.

## Two ways to call GI

### Hosted MCP server (best for AI agents — keyless)

GI hosts an MCP server at `https://mcp.genomicintelligence.ai/mcp` (Streamable
HTTP). When your agent host supports MCP, prefer it: it works **keyless** against
a capped public demo quota (zero setup), and an optional `gi_` bearer key raises
the quota. It exposes acquisition tools that return a **sequence handle**
(`sequence_ref`) and `predict_*` tools that take that handle — so large sequences
never bloat the context. See [MCP workflow](#mcp-workflow-handle-based) below and
`references/mcp.md`.

### REST API (universal)

Plain HTTP with `requests` against `https://api.genomicintelligence.ai/v1`. The
REST path **requires** a `GI_API_KEY` (a `gi_` bearer). Use it on any host, in
scripts, or when you need the raw envelope. See [Core REST workflow](#core-rest-workflow).

## Access and authentication

1. The **hosted MCP demo is keyless** — try it with nothing set.
2. The **REST `/v1` API needs a key**, sent as `Authorization: Bearer <key>`.
   Request one at [contact@genomicintelligence.ai](mailto:contact@genomicintelligence.ai).
3. **Never hardcode the key.** Read it from the `GI_API_KEY` environment variable
   (or a `.env` via `python-dotenv`). Never commit keys.

```bash
export GI_API_KEY="gi_yourkeyhere"     # optional for MCP; required for REST
export GI_BASE_URL="https://api.genomicintelligence.ai"   # override for staging
```

Keys are scoped to a partner tier with concurrency and per-minute caps. A `429`
means you hit a cap — back off and retry, or ask GI to raise your tier.

## The six tasks

All REST tasks share one shape: `POST /v1/tasks/{task}/predict` with body
`{sequence, sequence_name, model?, options?}`, returning a `{data, meta}`
envelope. What differs per task:

| Task | Mode | Length bound | Notes |
|---|---|---|---|
| `promoter` | sync | 1–500,000 bp | sliding-window promoter regions |
| `splice` | sync | 1–500,000 bp | donor/acceptor sites (long-context BigBird) |
| `enhancer` | sync | 1–500,000 bp | dev + housekeeping scores (DeepSTARR, *Drosophila*) |
| `chromatin` | sync | 1–500,000 bp | hundreds of tracks (DeepSEA) |
| `expression` | sync | **exactly 9,198 bp** | log(TPM+1); needs a cell-type `description` |
| `annotation` | **async** | 1–500,000 bp | de-novo transcripts; submit + poll |

**Omit `model` and the API uses the task's default** — that is the recommended
call. Default model IDs are intentionally **not** documented here: defaults
change and retired IDs fail hard, so never hardcode one. To pin a model, or to
pick a non-human one (Drosophila, yeast, and Arabidopsis models exist for several
tasks), discover IDs at call time with `GET /v1/tasks/{task}/models` (REST) or
`list_models` (MCP) — and **never invent one**. Full per-task output shapes are
in `references/tasks.md`.

Two hard rules the model enforces:

- **`expression` needs exactly 9,198 bp**, a window **centred on the TSS**
  (4,599 upstream + TSS + 4,598 downstream). Any other length is rejected. Use the acquisition helpers below to
  build it — do not truncate by hand.
- **`expression` needs a `description`** — a cell-type / assay string (e.g.
  `"K562 cells"`), passed as `options.description`.

## Sequence acquisition

You rarely start from a raw 9,198 bp string. Acquire sequence first:

- **From a gene symbol** → MCP `fetch_ensembl_sequence(gene=...)`; **from
  coordinates** → `fetch_region(region=...)`. Both fetch public Ensembl reference
  sequence (no key). REST users can query Ensembl REST directly. (`find_genes` is
  the annotation task, not an acquisition tool.)
- **For `expression`** → use the TSS-centred fetch so the window is exactly
  9,198 bp. MCP: `fetch_gene_for_expression` (handles the centring). Do not
  build the window by hand.
- **From a local FASTA** → MCP `store_inline_sequence`, or read the file yourself
  for REST. (`load_local_fasta` exists only in local deployments, not on the
  hosted server.)
- **A demo sequence** → MCP `load_demo_sequence(name=...)` returns a ready handle
  (great for a keyless smoke test); `name` is required.

See `references/sequence-acquisition.md` for the exact Ensembl calls and the
expression-window math.

## Core REST workflow

Sync tasks (promoter, splice, enhancer, chromatin, expression) are one call:

```python
import os, requests

BASE = os.environ.get("GI_BASE_URL", "https://api.genomicintelligence.ai")
HEADERS = {"Authorization": f"Bearer {os.environ['GI_API_KEY']}"}

def predict(task, sequence, sequence_name, model=None, options=None):
    body = {"sequence": sequence, "sequence_name": sequence_name}
    if model:   body["model"] = model
    if options: body["options"] = options
    r = requests.post(f"{BASE}/v1/tasks/{task}/predict", headers=HEADERS, json=body)
    r.raise_for_status()          # 400 invalid; 401 no/bad key; 413 too long; 429 rate limit
    return r.json()               # {"data": {...}, "meta": {...}}

# Promoter:
out = predict("promoter", seq, "TP53_region")
print(out["data"]["summary"])

# Expression — exactly 9,198 bp + a cell-type description:
out = predict("expression", tss_window_9198bp, "HBB",
              options={"description": "K562 cells"})
print(out["data"]["prediction"]["expression_log_tpm"])
```

### Async: annotation

`annotation` is submit-then-poll. Send `Prefer: respond-async`, get a `job_id`,
poll until terminal:

```python
import time

r = requests.post(f"{BASE}/v1/tasks/annotation/predict",
                  headers={**HEADERS, "Prefer": "respond-async"},
                  json={"sequence": seq, "sequence_name": "TP53"})
r.raise_for_status()              # 202 Accepted
job_id = r.json()["data"]["job_id"]

while True:
    j = requests.get(f"{BASE}/v1/tasks/jobs/{job_id}", headers=HEADERS)
    if j.status_code == 200:      # terminal: body is the final {data, meta}
        break
    j.raise_for_status()          # 202 = still running (2xx, won't raise)
    time.sleep(5)                 # ~20 s typical for ~20 kb
transcripts = j.json()["data"]["transcripts"]
```

## MCP workflow (handle-based)

On an MCP host, acquire a handle, then predict against it — sequences stay out of
the context:

```
# 1. Acquire a sequence handle (each returns a sequence_ref):
load_demo_sequence(name="promoter_tp53")  # keyless smoke test; `name` is REQUIRED
fetch_ensembl_sequence(gene="TP53")       # gene symbol or Ensembl ID -> handle
fetch_region(region="chr11:5,225,000-5,235,000")   # coordinates -> handle
fetch_gene_for_expression(gene="HBB")     # TSS-centred 9,198 bp handle for expression

# 2. Predict against the handle:
predict_promoter(sequence_ref=<ref>)
predict_expression(sequence_ref=<ref>, description="K562 cells")
predict_splice(sequence_ref=<ref>)        # + predict_enhancer / predict_chromatin

# 3. Annotation on MCP is `find_genes` (there is no predict_annotation).
#    It takes a handle, not a region, and runs async internally:
find_genes(sequence_ref=<ref>)            # wait=True (default) returns the result
find_genes(sequence_ref=<ref>, wait=False)  # -> job_id; poll get_job(job_id)

# Discover models with list_models(task); reference context lives in the
# gi://models, gi://docs/tasks, and gi://account MCP resources.
```

## Composite: find genes, then predict expression

To answer "what genes are in this region and how are they expressed?", use the
composite:

- **MCP:** `find_genes_and_predict_expression(sequence_ref=..., description=...)`
  — takes a **handle, not a region** (acquire one with `fetch_region` first);
  `description` is required. Finds genes in the sequence and returns an
  expression prediction for each.
- **REST:** call gene discovery, then loop `expression` per gene (build each
  TSS-centred 9,198 bp window via the acquisition helpers).

## Errors

| Code | Meaning | Action |
|---|---|---|
| 400 | Invalid request / bad sequence | Check the body; expression must be exactly 9,198 bp and carry `description` |
| 401 | Missing/invalid key (REST) | Set `GI_API_KEY`; or use the keyless MCP demo |
| 413 | Sequence too long | Stay within the task's length bound (≤500,000 bp) |
| 429 | Rate / concurrency cap | Back off and retry; ask GI to raise your tier |
| 422 | Validation failed (`validation_failed`) | The most common failure: expression not exactly 9,198 bp, or a sequence below the model's minimum length |
| 5xx | Server error | Retry; if persistent, contact support |

## Reference files

- `references/tasks.md` — per-task output shapes, model registries, the async
  annotation contract.
- `references/api-and-auth.md` — REST endpoints, the `{data, meta}` envelope,
  auth, base-URL override, tiers.
- `references/mcp.md` — the hosted MCP tool list, the handle-based flow, and the
  `gi://` resources.
- `references/sequence-acquisition.md` — Ensembl fetch calls and the
  expression-window (9,198 bp, TSS-centred) math.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/genomic-intelligence/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api-and-auth.md`

# REST API & Authentication

Base URL: `https://api.genomicintelligence.ai` (override with `GI_BASE_URL` for
staging). Live contract: <https://api.genomicintelligence.ai/v1/openapi.json>.

## Authentication

Every `/v1/*` REST call needs a partner bearer key, sent as
`Authorization: Bearer <key>`. Public routes needing no key: `/health`, `/docs`,
`/redoc`, `/v1/openapi.json`.

```bash
export GI_API_KEY="gi_yourkeyhere"
```

Keys begin with `gi_`. Request one at contact@genomicintelligence.ai. Read the
key from the environment (or a `.env` via `python-dotenv`); never hardcode or
commit it.

> The hosted **MCP** server (`mcp.genomicintelligence.ai/mcp`) is different: it
> runs **keyless** against a capped public demo quota, with the key optional for
> a higher quota. Only the **REST** path strictly requires a key. See `mcp.md`.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/tasks/{task}/predict` | Run a task (sync, or async for `annotation` with `Prefer: respond-async`) |
| GET | `/v1/tasks/jobs/{job_id}` | Poll an async job (202 running → 200 terminal) |
| GET | `/v1/tasks/{task}/models` | List available model IDs for a task |

## Request / response

Request body: `{sequence, sequence_name, model?, options?}`. `options` is
task-specific — most notably `options.description` (required for `expression`).

Success is a `{data, meta}` envelope; `data` is task-specific (see `tasks.md`),
`meta` carries model + request info. Errors use an `{error}` envelope carrying
`code`, `message`, `status` and `request_id`; the most common is `422`
`validation_failed` (wrong sequence length).

## Partner tiers

Keys are scoped to a tier with concurrency and per-minute caps. A `429` means a
cap was hit — back off and retry, or ask GI to raise the tier.

### `references/mcp.md`

# Hosted MCP Server

GI hosts a Model Context Protocol server (Streamable HTTP) at:

```
https://mcp.genomicintelligence.ai/mcp
```

It works **keyless** against a capped public demo quota, with no setup. An
optional `gi_` bearer key (`GI_API_KEY`) raises the quota. Prefer MCP on agent
hosts that support it: the tools use agent-friendly, handle-based schemas so large
sequences never enter the context.

The hosted server exposes **15 tools**. Verify with `tools/list` rather than
assuming; the list below is a point-in-time snapshot.

## The handle-based flow

Acquire a **sequence handle** (`sequence_ref`), then predict against it.

### 1. Acquire (each returns a handle)

| Tool | Required | Notes |
|---|---|---|
| `fetch_ensembl_sequence` | `gene` | Gene **symbol or Ensembl ID** (e.g. `"TP53"`). Also `species`, `flank_bp`. Not for coordinates. |
| `fetch_region` | `region` | Coordinate range, e.g. `"chr8:127,680,000-127,800,000"`. Also `species`, `strand`, `flank_bp`. Plus strand by default, which is what gene finding expects. |
| `fetch_gene_for_expression` | `gene` | Builds the **TSS-centred 9,198 bp** window `expression` needs. Also `species`. |
| `load_demo_sequence` | `name` | **`name` is required.** Valid names: `promoter_tp53`, `splice_hbb`, `enhancer_eve`, `chromatin_active_promoter_chr19`, `expression_hbb_k562`, `annotation_hbb_chr11`. |
| `store_inline_sequence` | `sequence` | Store an inline string; optional `name`. |

There is **no `load_local_fasta` on the hosted server** — it only exists in local
deployments. Over REST, read the file yourself.

### 2. Predict (pass the handle)

`predict_promoter`, `predict_splice`, `predict_enhancer`, `predict_chromatin`,
`predict_expression`. Each takes `sequence_ref` **or** `sequence` (mutually
exclusive), plus optional `model` and `sequence_name`.

`predict_expression` additionally needs `description` (cell type / assay, e.g.
`"K562 cells"`).

### 3. Gene finding (the annotation task on MCP)

**There is no `predict_annotation` tool.** The annotation task is surfaced as
**`find_genes`**, which takes `sequence_ref` or `sequence` — **not** a `region`.
Acquire a region handle with `fetch_region` first, then pass the handle.

`find_genes` runs async internally (~8-25 s). With `wait=True` (the default) it
blocks and returns the result directly, never a job id. With `wait=False` it
returns `{data: {job_id, status}}` to poll with `get_job(job_id)`.

## Composite

`find_genes_and_predict_expression` takes `sequence_ref` or `sequence` plus a
**required** `description`. It has **no `region` parameter** — acquire a handle
with `fetch_region` first. It finds genes in the sequence, then predicts
expression off each discovered TSS. Use it whenever you want expression for a
whole region: `predict_expression` cannot run on one, because it needs a single
per-gene 9,198 bp window.

## Jobs and discovery

- `get_job(job_id)` (required `job_id`) and `list_jobs` — poll detached work.
- `list_models(task)` — the model registry for a task. Do not invent model IDs,
  and do not hardcode a default; omit `model` and the server resolves it.

## Resources

Reference context lives in MCP resources: `gi://models`, `gi://docs/tasks`,
`gi://sequences`, `gi://account`. Read these instead of hardcoding model lists or
bounds.

## Small sequences

Small sequences may be passed inline via `sequence` on the `predict_*` tools, but
the handle flow above is preferred to keep context small.

## Worked example

```
# region -> handle -> genes -> expression per gene
h = fetch_region(region="chr11:5,225,000-5,235,000")
find_genes(sequence_ref=h.ref)
find_genes_and_predict_expression(sequence_ref=h.ref, description="K562 cells")

# gene -> handle -> promoter
g = fetch_ensembl_sequence(gene="TP53")
predict_promoter(sequence_ref=g.ref)

# keyless smoke test
d = load_demo_sequence(name="promoter_tp53")
predict_promoter(sequence_ref=d.ref)
```

### `references/sequence-acquisition.md`

# Sequence Acquisition (Ensembl)

Turn a **gene symbol** or a **genomic region** into reference sequence so users
don't have to bring a FASTA. Ensembl REST (`rest.ensembl.org`) is **public — no
key**; only the *prediction* step needs a key (and only over REST).

On MCP, the acquisition tools (`fetch_ensembl_sequence`, `fetch_region`,
`fetch_gene_for_expression`, `find_genes`) do this for you and return a handle.
Over REST, query Ensembl yourself, then feed the sequence to `/v1/tasks/...`.

## Modes

- **Full gene body** (any task except expression) — resolve the gene, fetch its
  sequence.
- **Coordinate range** — fetch `/sequence/region/{species}/{region}`.
- **Exact 9,198 bp TSS-centred window** (expression only) — see below.

## TSS-centring (why expression is special)

The expression model requires **exactly 9,198 bp centred on the transcription
start site (TSS)**. You cannot reliably build this from gene-body coordinates:
the annotated gene start/end can sit far from the real TSS (HBB's gene end is
2,324 bp from its canonical TSS; ACTB's is 33,301 bp). Mis-centring tanks the
prediction.

The correct construction: resolve the gene's **canonical transcript** (Ensembl
`expand=1`), take the TSS from it (transcript start on the + strand, end on the −
strand), and take **4,599 bp upstream + 4,598 bp downstream on the gene's
strand = 9,198 bp**; validate the length exactly. On MCP,
`fetch_gene_for_expression(gene=...)` does all of this. Because it needs a
transcript, it works from a **gene**, not a bare region.

## Species & assembly

- **Default: human, GRCh38.**
- Non-human: use the Ensembl **production name** — lowercase, underscored:
  `mus_musculus`, `drosophila_melanogaster`, `saccharomyces_cerevisiae`. `mouse`
  / `Drosophila` will be rejected.
- The **enhancer** default (DeepSTARR) is *Drosophila* — match species to model
  (see `tasks.md`).

## When to skip acquisition

Supply sequence directly when it is **not** reference genome — variant-bearing,
edited, synthetic, or from a non-Ensembl assembly. Acquisition only returns
reference sequence for the requested coordinates.

## Limits

Bounded by the task's own cap (500,000 bp for most; exactly 9,198 bp for
expression). Ensembl enforces its own per-request size limits; fetch very large
ranges in pieces.

### `references/tasks.md`

# Tasks Reference

Six DNA-sequence tasks, one shared REST shape: `POST /v1/tasks/{task}/predict`
with body `{sequence, sequence_name, model?, options?}`, returning a
`{data, meta}` envelope. On MCP, the equivalent is `predict_<task>(sequence_ref, ...)`.

**Omit `model` to get the task's default** — the API resolves it server-side
(`model` is optional: *"If omitted, the task's default model is used."*). Default
model **IDs are deliberately not listed here**: defaults change and old IDs are
retired, so a hardcoded ID is a future hard failure. Discover them at call time
with `GET /v1/tasks/{task}/models` (REST) or `list_models(task)` (MCP), and
**never invent one**.

Source of truth for bounds: the live OpenAPI at
<https://api.genomicintelligence.ai/v1/openapi.json>.

| Task | Mode | Length | Default architecture |
|---|---|---|---|
| promoter | sync | 1–500,000 bp | sliding-window; human/mammalian |
| splice | sync | 1–500,000 bp | BigBird (long-context) |
| enhancer | sync | 1–500,000 bp | DeepSTARR — ***Drosophila*** |
| chromatin | sync | 1–500,000 bp | DeepSEA — hundreds of tracks |
| expression | sync | **exactly 9,198 bp** | log(TPM+1) |
| annotation | **async** | 1–500,000 bp | de-novo transcripts |

## promoter
Promoter regions over a sliding window. `data.summary` reports
`promoter_windows` / `total_windows`; `data.regions` lists windows with `name`,
`start`, `end`, `score`, `strand`. Non-human models exist (Drosophila, yeast,
Arabidopsis) — pass `model`. Default targets human/mammalian sequence.

## splice
Splice **donor** and **acceptor** sites. `data.sites` lists each with `name`,
`start`, `end`, `site_type` (donor/acceptor), `score`, `strand`. The default is a
BigBird long-context model.

## enhancer
Enhancer activity. The default (DeepSTARR) reports **developmental**
and **housekeeping** scores — `summary.dev_score_max` / `summary.hk_score_max`
per window. DeepSTARR is a *Drosophila* model — match the species to the model.

## chromatin
Chromatin state across a large panel of tracks (histone marks, DNase, ATAC, TF
binding). The default (DeepSEA) covers hundreds of features.
`summary.total_annotations` is the headline; the full per-track matrix is in
`data`.

## expression
Expression as **log(TPM+1)** from a fixed window. Two enforced requirements:

1. **Exactly 9,198 bp** — a window **centred on the TSS** (4,599 upstream +
   TSS + 4,598 downstream). Other
   lengths are rejected. Build it with the acquisition helpers
   (`fetch_gene_for_expression` on MCP), not by hand — see
   `sequence-acquisition.md`.
2. **`options.description`** — a cell-type / assay string (e.g. `"K562 cells"`).
   Required.

Result: `data.prediction.expression_log_tpm` (and `expression_tpm`).

## annotation
De-novo gene / transcript structure — transcript intervals and strand, no
reference annotation. **Async only**: submit with
`Prefer: respond-async` → `job_id`; poll `GET /v1/tasks/jobs/{job_id}` until it
returns `200`. `data.transcripts` lists each transcript with `name`, `start`,
`end`, `strand`, `score`, plus structure fields (`length`, `tss_position`,
`polya_position`, `transcript_type`, `exons`, `introns`, `cds`).

## Composite: find genes + predict expression
"What genes are in this region, and how are they expressed?" — MCP
`find_genes_and_predict_expression(sequence_ref, description)` takes a **handle,
not a region** (acquire one with `fetch_region` first); `description` is
required. It finds genes in the sequence
and returns an expression prediction per gene. Over REST, discover genes then
loop `expression` per gene (build each TSS-centred 9,198 bp window first).
