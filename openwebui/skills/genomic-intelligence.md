---
name: genomic-intelligence
description: Optional gi_ bearer key for the REST /v1 API and higher MCP rate and concurrency limits. The hosted MCP demo runs keyless; request a key at contact@genomicintelligence.ai.
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

> Research and development use. Not for clinical or diagnostic decisions.

## Two ways to call GI

### Hosted MCP server (keyless; preferred on MCP hosts)

GI hosts an MCP server at `https://mcp.genomicintelligence.ai/mcp` (Streamable
HTTP). When your agent host supports MCP, prefer it: it works **keyless** against
a rate- and concurrency-limited public demo tier, and an optional `gi_` bearer
key raises those limits. It exposes acquisition tools that return a **sequence handle**
(`sequence_ref`) and `predict_*` tools that take that handle, so large sequences
stay out of the context. See [MCP workflow](#mcp-workflow-handle-based) below and
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

Each task is **its own published operation** with its own request schema, its own
minimum length, and its own closed `options` object — `POST
/v1/tasks/promoter/predict`, `/v1/tasks/splice/predict`,
`/v1/tasks/enhancer/predict`, `/v1/tasks/chromatin/predict`,
`/v1/tasks/annotation/predict`, `/v1/tasks/expression/predict`. Each path is a
literal string, so nothing needs to be constructed, and there is no shared
`PredictRequest` schema. Body is `{sequence, sequence_name?, model?,
options?}`, returning a `{data, meta}` envelope. What differs per task:

| Task | Recommended mode | Accepted length | `context_window_bp` | Notes |
|---|---|---|---|---|
| `promoter` | sync | 300–500,000 bp | 2,000 bp | sliding-window promoter regions |
| `splice` | sync | 100–500,000 bp | 15,000 bp | donor/acceptor sites (long-context BigBird); strand-specific — feed transcript orientation |
| `enhancer` | sync | 50–500,000 bp | 249 bp | dev + housekeeping scores (DeepSTARR, *Drosophila*) |
| `chromatin` | sync | 200–500,000 bp | 1,000 bp | hundreds of tracks (DeepSEA) |
| `expression` | sync | **9,198–500,000 bp** | n/a (`trained_window_bp` 9,198) | log(TPM+1); needs `tss_index` unless exactly 9,198 bp, plus a cell-type `description` |
| `annotation` | async | 1,000–500,000 bp | n/a | de-novo transcripts; submit + poll; sync above 200,000 bp is `413 sync_too_large` |

`Recommended mode` is guidance, not a constraint — every task accepts both. Omit `Prefer` for a synchronous `200`; send `Prefer: respond-async` for a `202` plus `GET /v1/tasks/jobs/{job_id}`. The one enforced limit is per operation: where `/v1/openapi.json` publishes `x-sync-limit-bp` on a `POST`, a synchronous request above that length is `413 sync_too_large` — 200,000 bp on `annotation` and 50,000 bp on the composite workflow as of `info.version` 2026.09.10.1. Read the field rather than memorising the numbers; the other predict tasks carry no limit today.

**The minimum is admission control, not regime.** A request above the floor but
shorter than the selected model's `bio_spec.context_window_bp` is *accepted and
scored* — against a window padded out to the context window. Enhancer is the
sharp case: the floor is 50 bp but the context window is 249 bp, so 50–248 bp is
scored mostly on padding. Compare your length against
`context_window_bp` from `GET /v1/tasks/{task}/models` to know whether the model
saw real sequence. Longer-than-context input is fine — the scanner steps a
prediction window at a time and pads only the final partial window.

Under the floor and over the 500,000 bp cap are **both `422 validation_failed`**
at `loc ["body","sequence"]`; over-length is *not* a `413`. All lengths are
measured after whitespace is stripped, so a line-wrapped FASTA body can be pasted
verbatim (a `>` header line still fails the alphabet check).

`options` is typed and **closed** (`additionalProperties: false`) per task — an
unknown key is a hard `422 validation_failed` with `type: "extra_forbidden"`,
never ignored:

| Task | `options` keys |
|---|---|
| promoter | `threshold` (0–1, default 0.5) |
| splice | `threshold` (0–1, default 0.5), `site_types` (subset of `["donor","acceptor"]`, default both) |
| enhancer | *(none)* |
| chromatin | `threshold` (0–1, default 0.5) |
| annotation | `batch_size` (1–128, default 8), `shift_coordinates`, `reverse_complement` (default true) |
| expression | `description` — **required**, and the only key |

`Prefer: respond-async` is a declared header on **all six** predict operations
and on the composite, not just `annotation` — see [Async](#async-any-task-recommended-for-annotation).

**Omit `model` and the API uses the task's default** — that is the recommended
call. Default model IDs are intentionally **not** documented here: defaults
change and retired IDs fail hard, so never hardcode one. To pin a model, or to
pick a non-human one (Drosophila, yeast, and Arabidopsis models exist for several
tasks), discover IDs at call time with `GET /v1/tasks/{task}/models` (REST) or
`list_models` (MCP) — and **never invent one**. Full per-task output shapes are
in `references/tasks.md`.

`expression` is the strictest of the six: alone among them its schema requires
`options` as well as `sequence`. Three hard rules it enforces — every violation
is a `422`, nothing is padded or clamped, and there is no opt-out flag, header,
or query parameter:

- **It always scores exactly one 9,198 bp TSS-centred window** —
  `sequence[tss_index-4599 : tss_index+4599]`. The endpoint itself accepts
  **9,198–500,000 bp**; anything below 9,198 bp is rejected outright.
- **`tss_index` is required unless the sequence is exactly 9,198 bp.** It is the
  0-based TSS offset into the **whitespace-stripped** sequence, bounded by
  `4599 ≤ tss_index ≤ len(sequence) − 4599`. At exactly 9,198 bp it defaults to
  4,599, the only legal value there. So you may submit a whole locus (up to
  500 kb) and let the server cut the window — but the server does **not**
  discover the TSS for you (that is the composite workflow's job), and does
  **not** reverse-complement: submit gene-sense sequence.
- **`options.description`** — a cell-type / assay string (e.g. `"K562 cells"`) —
  is required, and is the **only** key `expression` accepts inside `options`.
  Unknown top-level body fields are rejected too.

> Note: the legal `tss_index` range is wide, so an offset that is merely
> *wrong* (counted over raw FASTA characters including newlines, or relative to
> a locus start rather than the submitted slice) does not error — it returns a
> confident `200` for the wrong window. Assert on
> `meta.task_specific_counts.scored_window` / `.tss_index` in the response.
> The length you submitted is `meta.sequence_length` (also echoed as
> `data.input.submitted_sequence_length`); the scored width is always 9,198,
> i.e. `scored_window[1] - scored_window[0]`. (`data.input.sequence_length`
> was removed at contract revision 13.)
>
> Both `tss_index` violations — "required unless exactly 9,198 bp" and the range
> check — come from a whole-model validator, so they surface at the body level
> rather than under `tss_index`. Match on `error.code == "validation_failed"`
> and use the message for display only. Any `loc` tuple quoted in this skill is
> illustrative of that shape, not part of the contract: it is not published in
> the schema and must not be branched on.

## Sequence acquisition

You rarely start from a raw 9,198 bp string. Acquire sequence first:

- **From a gene symbol** → MCP `fetch_ensembl_sequence(gene=...)`; **from
  coordinates** → `fetch_region(region=...)`. Both fetch public Ensembl reference
  sequence (no key). REST users can query Ensembl REST directly. (`find_genes` is
  the annotation task, not an acquisition tool.)
- **For `expression`** → use the TSS-centred fetch so the window is exactly
  9,198 bp. MCP: `fetch_gene_for_expression` (handles the centring). Otherwise
  fetch a wider locus and pass the TSS as `tss_index` so the server cuts the
  window — but compute that offset on the stripped nucleotide string, not on
  file characters.
- **From a local FASTA** → MCP `store_inline_sequence`, or read the file yourself
  for REST. (`load_local_fasta` exists only in local deployments, not on the
  hosted server.)
- **A demo sequence** → MCP `load_demo_sequence(name=...)` returns a ready handle
  for a keyless smoke test; `name` is required.

See `references/sequence-acquisition.md` for the exact Ensembl calls and the
expression-window math.

## Core REST workflow

Called synchronously — the default for every task — a prediction is one call:

```python
import os, requests

BASE = os.environ.get("GI_BASE_URL", "https://api.genomicintelligence.ai")
HEADERS = {"Authorization": f"Bearer {os.environ['GI_API_KEY']}"}

def predict(task, sequence, sequence_name, model=None, options=None, tss_index=None):
    body = {"sequence": sequence, "sequence_name": sequence_name}
    if model:   body["model"] = model
    if options: body["options"] = options
    if tss_index is not None: body["tss_index"] = tss_index   # expression only
    # Each task is its own published operation, but the URL string is unchanged.
    r = requests.post(f"{BASE}/v1/tasks/{task}/predict", headers=HEADERS, json=body)
    # 422 validation_failed  — sequence under the task floor OR over 500,000 bp,
    #                          bad tss_index, missing options.description,
    #                          or ANY unknown body/options key (options is closed)
    # 401 no/bad key · 404 unknown task · 413 body over 16 MiB · 429 rate limit
    r.raise_for_status()
    return r.json()               # {"data": {...}, "meta": {...}}

# Promoter:
out = predict("promoter", seq, "TP53_region")
print(out["data"]["summary"])

# Expression — a pre-cut 9,198 bp TSS-centred window (tss_index defaults to 4,599):
out = predict("expression", tss_window_9198bp, "HBB",
              options={"description": "K562 cells"})
print(out["data"]["prediction"]["expression_log_tpm"])

# Expression — a whole locus; the server slices ±4,599 bp around the TSS you name.
# tss_index is 0-based into the whitespace-stripped sequence.
out = predict("expression", locus_seq, "HBB",
              options={"description": "K562 cells"}, tss_index=tss_offset_in_locus)
print(out["meta"]["task_specific_counts"]["scored_window"])   # confirm the window scored
```

### Async (any task; recommended for annotation)

`Prefer: respond-async` is a declared header parameter on all six predict
operations and on the composite. A `202` carries the same `{data, meta}` envelope
as a sync `200`, with `data = {job_id, status: "accepted", links}`; the job id is
also in the `Content-Location` and `X-Job-Id` response headers. Async is
JSON-only — combining it with a text `format` is rejected. `annotation` is the
task that needs it:

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
load_demo_sequence(name="promoter_tp53")  # keyless smoke test; name is required
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
- **REST:** one call — `POST /v1/workflows/find-genes-and-predict-expression`,
  body `{sequence, options}` with `sequence` 1,000–500,000 bp and
  `options.description` (cell type / assay) required; a missing or empty
  description is a `422 validation_failed`. It annotates, centres a 9,198 bp
  window on each discovered gene's TSS (padding with `N` up to half the window
  rather than dropping an edge gene), and returns a prediction per gene.
  `meta.task_specific_counts` = `{genes_found, genes_predicted, genes_skipped}`
  with `genes_predicted + genes_skipped == genes_found`; per-gene causes in
  `data.expression_predictions[].skip_reason`. Above **50,000 bp** (its `x-sync-limit-bp`) it forces
  async: a synchronous request over that size is `413 sync_too_large` with
  `error.details = {sequence_length, threshold}` — retry the same body with
  `Prefer: respond-async`.

## Errors

| Code | `error.code` | Meaning | Action |
|---|---|---|---|
| 400 | `bad_request` | Malformed request | Check the body shape |
| 401 / 403 | `unauthorized` / `forbidden` | Missing/invalid key (REST) | Set `GI_API_KEY`; or use the keyless MCP demo |
| 404 | `not_found` | **Unknown task** (`/v1/tasks/bogus/predict`) or unknown job | Check the task name — an unrecognised task is a 404, not a 422 |
| 413 | `payload_too_large` | Raw request body over **16 MiB** | Split the input — this is the body cap, not the sequence cap |
| 413 | `sync_too_large` | Synchronous request above the operation's `x-sync-limit-bp` (200,000 bp on `annotation`, 50,000 bp on the composite) | Retry with `Prefer: respond-async` |
| 415 | `unsupported_format` | Unsupported `format` query value | Use a format the task supports; there is no silent fallback to JSON |
| 422 | `validation_failed` | The most common failure: sequence **under the task floor or over 500,000 bp**, expression below 9,198 bp, a missing/out-of-range `tss_index`, a missing `options.description`, or **any unknown body or `options` key** | Read the message; fix the body |
| 429 | `rate_limited` / `too_many_requests` | Rate / concurrency cap | Back off (honour `Retry-After`); ask GI to raise your tier |
| 5xx | `internal_error` / `service_unavailable` / `model_loading` / `timeout` | Server error | Retry; if persistent, contact support |

`error.code` is a closed 21-value enum (`bad_request`, `unauthorized`,
`forbidden`, `not_found`, `conflict`, `job_expired`, `payload_too_large`,
`sync_too_large`, `unsupported_format`, `validation_failed`,
`too_many_requests`, `rate_limited`, `internal_error`, `timeout`,
`insufficient_memory`, `model_not_found`, `task_not_supported_by_model`,
`model_loading`, `service_unavailable`, `http_error`, `unknown`); treat an
unlisted value as a generic failure, not a parse error.

**Branch on `code`, never on `details` or `loc`.** `details` is keyed on the
sibling `code`; for `validation_failed` it is the `{errors: [{loc, msg, type}, …]}`
object the schema declares. Treat it as display-only — `code` is the stable
discriminator.

For correlation, `error.request_id` and the `X-Request-Id` **header** are both
set on every response, and success envelopes carry `meta.request_id`. Reading
the header first remains a safe default.
Every response carries `RateLimit-Limit`, `RateLimit-Remaining`,
`RateLimit-Reset`, `RateLimit-Policy`; a `429` adds `Retry-After`.

> Verified against OpenAPI `info.version` **2026.08.20.7**. The contract moves,
> and `info.version` in `/v1/openapi.json` reports what a given deployment
> serves: if it is ahead of the version above, re-check the numbers in this file
> against that document, which is the arbiter if the two disagree.

## Reference files

- `references/tasks.md` — per-task output shapes, model registries, the async
  annotation contract.
- `references/api-and-auth.md` — REST endpoints, the `{data, meta}` envelope,
  auth, base-URL override, tiers.
- `references/mcp.md` — the hosted MCP tool list, the handle-based flow, and the
  `gi://` resources.
- `references/sequence-acquisition.md` — Ensembl fetch calls and the
  expression-window (9,198 bp, TSS-centred) math, including `tss_index`.

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
> runs **keyless** against a rate- and concurrency-limited public demo tier, with
> the key optional for higher limits. Only the **REST** path strictly requires a
> key. See `mcp.md`.

## Endpoints

Eleven operations are published. The six predict paths are **literal, one per
task**; the published document has no templated `/v1/tasks/{task}/predict`
operation.

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/tasks/promoter/predict` | `PromoterPredictRequest` |
| POST | `/v1/tasks/splice/predict` | `SplicePredictRequest` |
| POST | `/v1/tasks/enhancer/predict` | `EnhancerPredictRequest` |
| POST | `/v1/tasks/chromatin/predict` | `ChromatinPredictRequest` |
| POST | `/v1/tasks/annotation/predict` | `AnnotationPredictRequest` |
| POST | `/v1/tasks/expression/predict` | `ExpressionPredictRequest` (also requires `options`) |
| POST | `/v1/workflows/find-genes-and-predict-expression` | Composite: find genes, predict each one's expression |
| GET | `/v1/tasks/jobs` | List async jobs |
| GET | `/v1/tasks/jobs/{job_id}` | Poll an async job (202 running → 200 terminal) |
| GET | `/v1/tasks/{task}/models` | List available model IDs for a task |
| GET | `/health` | Public liveness |

There is no usable templated route to fall back on: the six literal paths are
matched first, and any other task segment is `404 not_found`
(`"Unknown task: bogus"`), never a `422`.

`Prefer: respond-async` is a declared header parameter on all six predict
operations and on the composite — it is not an annotation-only extra. Omit it
for a synchronous `200`; send it for a `202` carrying
`{data: {job_id, status: "accepted", links}, meta}`, with the id also in
`Content-Location` and `X-Job-Id`, then poll `GET /v1/tasks/jobs/{job_id}`.
Async is JSON-only: combining it with a text `format` is a `400`.

## Request / response

Request body: `{sequence, sequence_name?, model?, options?}` — but there is no
longer a shared `PredictRequest`. Each task has its own request model with its own
`minLength` (promoter 300, splice 100, enhancer 50, chromatin 200, annotation
1,000, expression 9,198, composite 1,000; `maxLength` 500,000 for all), and every
one is `additionalProperties: false`. `options` is likewise typed and closed per
task, so an unknown key is `422 validation_failed` with `type: "extra_forbidden"`
at `loc ["body","options","<key>"]`.

**`expression` differs further**: its body is
`{sequence, options, tss_index?, sequence_name?, model?}`, `options` is required
(`ExpressionOptions.required = ["description"]`, the only key it accepts), and
`tss_index` is required unless `sequence` is exactly 9,198 bp. See
`tasks.md#expression`.

Hand-built requests are unaffected. A client **generated** from an older OpenAPI
document must be regenerated against the current one: the shared `PredictRequest`
model such clients were built from is not in the published document.

Success is a `{data, meta}` envelope; `data` is task-specific (see `tasks.md`),
`meta` carries model + request info. **Exception:** `GET /v1/tasks/{task}/models`
is *not* enveloped — it returns a flat
`{task, default_model, models: [{id, name, description, is_default, bio_spec}]}`.

Errors use an `{error}` envelope carrying `code`, `message`, `request_id` and an
optional `details`; the most common is `422 validation_failed` (wrong sequence
length — under the floor *or* over 500,000 bp; over-length is not a `413`).

## `bio_spec` (from `GET /v1/tasks/{task}/models`)

- `request_max_bp` — the enforced ceiling: 500,000 for every model.
- `context_window_bp` — the model's own sliding window; `null` for annotation and
  expression. The promoter default reports 2,000 (the 300 bp promoter models
  report 300), splice 15,000, enhancer 249, chromatin 1,000. Compare your sequence
  length against this to know whether the model scored real sequence or padding.
- `trained_window_bp` — fixed receptive field; 9,198 for the expression model,
  `null` for sliding-window models.
- The legacy `max_seq_length_bp` is not part of `bio_spec` and is absent from the
  response. It was ambiguous — it read 9,198 for the expression model, the trained
  window rather than a request cap, so gating on it wrongly rejected the
  9,198–500,000 bp range expression accepts. Use `request_max_bp`.

There is no `strand_sensitive` flag. The splice model is strand-specific in
practice — feed transcript orientation.

## Partner tiers

Keys are scoped to a tier with concurrency and per-minute caps. A `429` means a
cap was hit — back off and retry, or ask GI to raise the tier.

### `references/mcp.md`

# Hosted MCP Server

GI hosts a Model Context Protocol server (Streamable HTTP) at:

```
https://mcp.genomicintelligence.ai/mcp
```

It works **keyless** against a rate- and concurrency-limited public demo tier,
with no setup. An optional `gi_` bearer key (`GI_API_KEY`) raises those limits. Prefer MCP on agent
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
- **9,198 bp TSS-centred window, or a wider locus + a `tss_index`** (expression
  only) — see below.

## TSS-centring (why expression is special)

The expression model always scores **exactly 9,198 bp centred on the
transcription start site (TSS)**. You can either hand it a pre-cut 9,198 bp
window, or hand it up to 500,000 bp plus `tss_index` — the 0-based TSS offset
into the whitespace-stripped sequence — and let the server slice
`sequence[tss_index-4599 : tss_index+4599]`. Either way you must know where the
TSS is; the endpoint never discovers it, never pads, and never
reverse-complements. You cannot reliably build this from gene-body coordinates:
the annotated gene start/end can sit far from the real TSS (HBB's gene end is
2,324 bp from its canonical TSS; ACTB's is 33,301 bp). Mis-centring tanks the
prediction.

The correct construction: resolve the gene's **canonical transcript** (Ensembl
`expand=1`), take the TSS from it (transcript start on the + strand, end on the −
strand), and take **4,599 bp upstream + 4,598 bp downstream on the gene's
strand = 9,198 bp**; validate the length exactly. On MCP,
`fetch_gene_for_expression(gene=...)` does all of this. Because it needs a
transcript, it works from a **gene**, not a bare region.

If instead you submit a wider locus with `tss_index`, the offset must be counted
on the **stripped nucleotide string** (no newlines, no FASTA header) and satisfy
`4599 ≤ tss_index ≤ len(sequence) − 4599`. An offset that is out of range 422s;
one that is merely *wrong* but in range silently scores the wrong window, so
check `meta.task_specific_counts.scored_window` on the response.

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

Bounded by the task's own cap (500,000 bp for every task) and its **floor**:
promoter 300, splice 100, enhancer 50, chromatin 200, annotation 1,000,
expression 9,198 bp. Clearing the floor only gets the request accepted — fetch at
least the model's `context_window_bp` (promoter 2,000, splice 15,000, enhancer
249, chromatin 1,000) if you want the score to reflect real sequence rather than
padding. Ensembl enforces its own per-request size limits; fetch very large
ranges in pieces.

### `references/tasks.md`

# Tasks Reference

Six DNA-sequence tasks, each its own published REST operation —
`POST /v1/tasks/promoter/predict`, `/v1/tasks/splice/predict`,
`/v1/tasks/enhancer/predict`, `/v1/tasks/chromatin/predict`,
`/v1/tasks/annotation/predict`, `/v1/tasks/expression/predict` — with body
`{sequence, sequence_name?, model?, options?}`, returning a `{data, meta}`
envelope. Each path is a literal string, and each carries its own request schema,
its own `minLength`, and its own closed `options` object; there is no shared
`PredictRequest`. On MCP, the equivalent is `predict_<task>(sequence_ref, ...)`.

**Omit `model` to get the task's default** — the API resolves it server-side
(`model` is optional: *"If omitted, the task's default model is used."*). Default
model **IDs are deliberately not listed here**: defaults change and old IDs are
retired, so a hardcoded ID is a future hard failure. Discover them at call time
with `GET /v1/tasks/{task}/models` (REST) or `list_models(task)` (MCP), and
**never invent one**.

Source of truth for bounds: the live OpenAPI at
<https://api.genomicintelligence.ai/v1/openapi.json>.

| Task | Recommended mode | Accepted length | `context_window_bp` | Default architecture |
|---|---|---|---|---|
| promoter | sync | 300–500,000 bp | 2,000 bp | sliding-window; human/mammalian |
| splice | sync | 100–500,000 bp | 15,000 bp | BigBird (long-context) |
| enhancer | sync | 50–500,000 bp | 249 bp | DeepSTARR — ***Drosophila*** |
| chromatin | sync | 200–500,000 bp | 1,000 bp | DeepSEA — hundreds of tracks |
| expression | sync | **9,198–500,000 bp** (scores one 9,198 bp window) | n/a (`trained_window_bp` 9,198) | log(TPM+1) |
| annotation | async | 1,000–500,000 bp | n/a | de-novo transcripts; sync above 200,000 bp (`x-sync-limit-bp`) is `413 sync_too_large` |

`Recommended mode` is guidance, not a constraint — every task accepts both. Omit `Prefer` for a synchronous `200`; send `Prefer: respond-async` for a `202` plus `GET /v1/tasks/jobs/{job_id}`. The one enforced limit is per operation: where `/v1/openapi.json` publishes `x-sync-limit-bp` on a `POST`, a synchronous request above that length is `413 sync_too_large` — 200,000 bp on `annotation` and 50,000 bp on the composite workflow as of `info.version` 2026.09.10.1. Read the field rather than memorising the numbers; the other predict tasks carry no limit today.

The minimum is published as `minLength` on each task's request schema and enforced
before any model loads. There are **no per-model floors**: a task's floor is the
strictest its models need, and every model stays listed and loadable.

**Floor ≠ regime.** A request above the floor but shorter than the selected
model's `bio_spec.context_window_bp` is accepted and scored — against a window
padded out to the context window. Enhancer is the sharp case: the floor is 50 bp
while the context window is 249 bp, so 50–248 bp is scored mostly on padding.
Compare your length against `context_window_bp` to know whether the model saw
real sequence.
Longer-than-context input is fine — the scanner steps a prediction window at a
time and pads only the final partial window.

Under the floor and over the cap are both `422 validation_failed` at
`loc ["body","sequence"]`; over-length is **not** a `413`. All lengths are
measured after whitespace is stripped.

`options` is typed and closed (`additionalProperties: false`) per task — an
unknown key is a hard `422` (`type: "extra_forbidden"`), never ignored:

| Task | `options` keys |
|---|---|
| promoter | `threshold` (0–1, default 0.5) |
| splice | `threshold` (0–1, default 0.5), `site_types` (subset of `["donor","acceptor"]`, default both) |
| enhancer | *(none)* |
| chromatin | `threshold` (0–1, default 0.5) |
| annotation | `batch_size` (1–128, default 8), `shift_coordinates`, `reverse_complement` (default true) |
| expression | `description` — **required**, and the only key |
| composite | `description`, `annotation_model`, `expression_model`, `batch_size`, `shift_coordinates` |

Per-task output `format` values (an unsupported one is `415 unsupported_format`,
never a silent fallback to JSON; text formats are synchronous-only): promoter
`json|bed|bedgraph`, splice `json|bed|gff3`, enhancer `json|bedgraph`, chromatin
`json|bed`, annotation `json|bed|gff3`, expression JSON only.

## promoter
Promoter regions over a sliding window. `data.summary` reports
`promoter_windows` / `total_windows`; `data.regions` lists windows with `name`,
`start`, `end`, `score`, `strand`. Non-human models exist (Drosophila, yeast,
Arabidopsis) — pass `model`. Default targets human/mammalian sequence.

## splice
Splice **donor** and **acceptor** sites. `data.sites` lists each with `name`,
`start`, `end`, `site_type` (donor/acceptor), `score`, `strand`. The default is a
BigBird long-context model.

**Strand-specific — and the wrong strand fails silently.** Submit transcript
orientation (reverse-complement minus-strand genes). A reverse-complemented
sequence does *not* return zeros or an empty result: measured live, it returns
plausible sites at different positions, often still at high confidence, and site
counts can hold or collapse depending on the locus. **Neither the score nor the
count tells you the orientation was wrong**, and the obvious post-hoc check does
not work either — get the orientation right on input.

That check was measured (2026-08-20; HBB, SMN1 and BRCA1 exon 11, both
orientations, threshold 0.5) and it does not discriminate. Canonical donor `GT`
at the reported boundary holds well above chance in *both* orientations
(12/14 gene-sense, 2/3 reverse complement, against a ~5% random null); the `AC`
signature a mirrored call would leave never appears (0/14, 0/3). Acceptor `AG`
inside the reported span is 100% in both orientations (13/13, 7/7, against a
30–45% null) because the post-processor snaps the span onto an `AG`, so that
test passes every input, including a deliberately wrong-strand one. The model
does not mirror sites onto the other strand; it calls a different, usually
smaller set, anchored on real `GT`s in whatever orientation it was given.

**`start`/`end` are token spans, not junctions.** Each site's `start`/`end` is a
variable-width BPE token span — 4 to 8 bp on the HBB fixture — with a
`token_index` beside it, not a base-resolution exon/intron boundary. Anything
that intersects these against a reference annotation is off by up to ~10 bp
regardless of strand. The `gff3` export writes the same spans to columns 4–5,
so saved files carry them too. Report the span as a span; do not derive a
single junction position from it.

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
Expression as **log(TPM+1)** from a fixed window. Its operation is
`POST /v1/tasks/expression/predict`, schema `ExpressionPredictRequest` — alone
among the six it requires `options` as well as `sequence`. Body:
`{sequence, options, tss_index?, sequence_name?, model?}`, closed to unknown
fields. Three enforced requirements, each a `422` when violated:

1. **9,198–500,000 bp.** The model scores exactly one 9,198 bp window
   **centred on the TSS** — `sequence[tss_index-4599 : tss_index+4599]` — but
   the endpoint accepts up to 500 kb and slices for you. Below 9,198 bp is
   rejected; nothing is padded or truncated.
2. **`tss_index`** — 0-based TSS offset into the **whitespace-stripped**
   sequence. Required unless the sequence is exactly 9,198 bp (where it defaults
   to 4,599, the only legal value). Bounds:
   `4599 ≤ tss_index ≤ len(sequence) − 4599`. The server does not find the TSS
   for you and does not reverse-complement — submit gene-sense.
3. **`options.description`** — a cell-type / assay string (e.g. `"K562 cells"`).
   Required, and the only key `options` accepts here.

Whitespace is stripped before lengths and `tss_index` are interpreted, so a
line-wrapped FASTA *body* can be pasted verbatim — but a `>` header line cannot
(it fails the A/C/G/T/N alphabet check), and offsets must be counted on the
stripped string, not on file characters.

Result: `data.prediction.expression_log_tpm` (and `expression_tpm`).
`meta.task_specific_counts` carries `tss_index` and `scored_window`
(`[start, end]`, always 9,198 wide) — assert on it, because an in-range but
wrong `tss_index` scores the wrong window with a `200`. `data.input` echoes
`tss_index`, `scored_window`, and `submitted_sequence_length`; the length you
submitted is `meta.sequence_length`, and the scored width is always 9,198.

Both `tss_index` failures come from a whole-model validator and so report at
`loc: ["body"]`, **never** `body.tss_index`. Match on
`error.code == "validation_failed"` — never on `loc`.

## annotation
De-novo gene / transcript structure — transcript intervals and strand, no
reference annotation. **Run it async** (`Prefer: respond-async` is available on
every predict operation; annotation is the one that most often needs it):
submit with
`Prefer: respond-async` → `job_id`; poll `GET /v1/tasks/jobs/{job_id}` until it
returns `200`. `data.transcripts` lists each transcript with `name`, `start`,
`end`, `strand`, `score`, plus structure fields (`length`, `tss_position`,
`polya_position`, `transcript_type`, `exons`, `introns`, `cds`).

## Composite: find genes + predict expression
"What genes are in this region, and how are they expressed?" — MCP
`find_genes_and_predict_expression(sequence_ref, description)` takes a **handle,
not a region** (acquire one with `fetch_region` first); `description` is
required. It finds genes in the sequence
and returns an expression prediction per gene. The composite does its own gene
finding and windowing, so it has **no** 9,198 bp floor and takes **no**
`tss_index`.

Over REST it is a single published operation:
`POST /v1/workflows/find-genes-and-predict-expression`, request
`FindGenesAndPredictExpressionRequest` — `sequence` 1,000–500,000 bp and
`options` both required, and `options.description` required too (enforced at
runtime rather than marked `required` in `FindGenesAndPredictExpressionOptions`,
so a missing or empty value is `422 validation_failed`, *"options.description is
required (cell type / assay context)"*). Optional: `annotation_model`,
`expression_model`, `batch_size` (1–128, default 8), `shift_coordinates`.

It cuts a TSS-centred 9,198 bp window per discovered gene, padding with `N` up to
half the window rather than dropping an edge gene — the direct expression route
refuses to pad at all. `meta.task_specific_counts` =
`{genes_found, genes_predicted, genes_skipped}` with
`genes_predicted + genes_skipped == genes_found`; per-gene causes in
`data.expression_predictions[].skip_reason`.

Above **50,000 bp** (its `x-sync-limit-bp`) it forces async: a synchronous
request over that size is `413 sync_too_large` with
`error.details = {sequence_length, threshold}`. Retry the same body with
`Prefer: respond-async`. `annotation` carries the same guard at 200,000 bp; no
other predict task publishes one today.

The equivalent by hand is `annotation` to discover genes, then one `expression`
call per gene with that gene's window and `tss_index` — useful when you want
per-gene control, though you then own the TSS-centring the composite does for
you.
