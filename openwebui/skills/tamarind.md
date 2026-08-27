---
name: tamarind
description: Tamarind Bio API key sent as the x-api-key header.
---

# Tamarind Bio

Tamarind Bio is a cloud platform that runs computational biology tools — structure prediction, protein and antibody design, docking, binding-affinity, MSA generation, and molecular dynamics — on managed GPUs. Users submit sequences or structures and get back predicted structures, designs, and biophysical scores, without provisioning their own hardware. It exposes hundreds of tools (AlphaFold, Boltz-2, Chai-1, RFdiffusion, ProteinMPNN, BoltzGen, ESMFold2, DiffDock, Autodock Vina, and many more) through one uniform job API.

**Official docs:** [app.tamarind.bio/api-docs](https://app.tamarind.bio/api-docs) · platform UI at [app.tamarind.bio](https://app.tamarind.bio)

## Canonical sources — fetch these, don't rely on a stale copy

Tamarind publishes live, machine-readable sources. Prefer fetching them at runtime over trusting any hardcoded list — tool names, schemas, and endpoints change frequently:

- **`https://app.tamarind.bio/llms.txt`** — LLM index: links to the spec, API docs, and MCP guide.
- **`https://app.tamarind.bio/openapi.yaml`** — OpenAPI 3.0 spec for the 8 core job endpoints (submit-job/-batch, jobs, result, upload, files, delete-job/-file; auth `ApiKeyAuth`). Fetch it for those exact shapes. Discovery/management endpoints (`/tools`, `/usage-statistics`, pipelines, …) aren't in it — use the MCP/REST discovery tools for those.
- **`https://docs.tamarind.bio/llms.txt`** — documentation index; every page has a `.md` form (e.g. `docs.tamarind.bio/tamarind/batch.md`, `/tamarind/api.md`, `/tamarind/pipelines.md`).
- **Live tool discovery** — `GET /tools` (REST) or MCP `getAvailableTools` + `getJobSchema(jobType)` are the source of truth for what tools exist and their parameters.

This skill teaches the surface + the non-obvious behaviors those sources don't spell out (see the reference files). When in doubt about a shape, fetch `openapi.yaml`.

## When to use this skill

Use Tamarind when the user wants to:

- **Predict structure** of a protein, complex, or protein-ligand system (AlphaFold, Boltz-2, Chai-1, ESMFold2, Chai/Boltz cofolding)
- **Design proteins or binders** (RFdiffusion, BoltzGen, BindCraft, ProteinMPNN/LigandMPNN inverse folding)
- **Design or characterize antibodies/nanobodies** (sequence generation, humanization, developability, immunogenicity)
- **Dock small molecules** to a protein (DiffDock, Autodock Vina) or predict **binding affinity**
- **Generate MSAs** for downstream folding
- **Run molecular dynamics** or other biophysical workflows on managed GPUs
- **Batch-screen** many sequences or designs through the same tool
- **Chain tools** into pipelines (e.g. design → fold → score) using the output of one job as the input of the next

This skill is the right fit when the work should run on Tamarind's managed cloud rather than on a local install. For purely local cheminformatics or one-off sequence I/O, use a local library (RDKit, BioPython) instead.

## Access and authentication

1. Sign in at [app.tamarind.bio](https://app.tamarind.bio) and create an API key from the account/API settings.
2. Authenticate every REST request with the `x-api-key` header.
3. **Never hardcode the key.** Read it from the `TAMARIND_API_KEY` environment variable or a `.env` file (use `python-dotenv`). Never commit keys to source control.

**Pricing:** Every user gets **10 free jobs**. For larger usage, contact [info@tamarind.bio](mailto:info@tamarind.bio) to purchase a subscription.

```bash
export TAMARIND_API_KEY="your_api_key"
# List available tools
curl https://app.tamarind.bio/api/tools \
  -H "x-api-key: $TAMARIND_API_KEY"
```

**Base URL:** `https://app.tamarind.bio/api/`

There is **no official Python SDK** — the PyPI package named `tamarind` is an unrelated Neo4j tool. Do not `uv pip install tamarind`. Write plain `requests` calls against the REST API (the endpoint shapes are in `openapi.yaml`), or use the MCP server for agent hosts.

## Two ways to call Tamarind

### MCP server (best for AI agents)

Tamarind hosts an MCP server at `https://mcp.tamarind.bio/mcp` (API-key auth via the `X-API-Key` header). When your agent host supports MCP, prefer it — the tools mirror the REST API with agent-friendly schemas:

- `listModalities()` / `listTags()` — the live filter vocabulary (molecule type / function) with labels + tool counts; call these to learn valid `modality`/`function` values instead of hardcoding
- `getAvailableTools(modality?, function?, search?, custom?)` — discover tools (`category`/`tag` are deprecated aliases still honored)
- `getJobSchema(jobType)` — exact parameter schema for a tool, plus an `exampleJob` starting payload (validate it before submitting)
- `validateJob(jobName, type, settings)` — dry-run validation before submitting
- `submitJob(jobName, type, settings)` / `submitBatch(batchName, type, settings[], jobNames[])`
- `getJobs(jobName?, batch?, limit?, includeSequences?)` — list/inspect jobs and statuses (the bulky per-job input blob is omitted by default; pass `includeSequences=true` to keep it)
- `getJobLogs(jobName)` — fetch output logs for debugging
- `listJobFiles(jobName)` — list output files (returns `s3Path` for chaining)
- `getResult(jobName, fileName?)` — download results
- `uploadFile(filename)` — presigned upload URL; or `uploadFileContent(filename, content, encoding?)` to send file content through MCP when the host can't reach S3 (sandboxed agents)

Scope note: MCP query tools (`getJobs`, `getResult`, `listJobFiles`, …) are scoped to the authenticated account.

### REST API (universal)

Use plain HTTP with `requests` — the endpoint shapes are in `openapi.yaml`. The core loop is below; `references/workflows.md` has full recipes.

## Core workflow

Always follow discover → schema → validate → submit → poll → results. Do not hardcode tool names or settings — the catalog changes frequently.

```python
import os, time, requests

BASE = "https://app.tamarind.bio/api"
HEADERS = {"x-api-key": os.environ["TAMARIND_API_KEY"]}

# 1. Discover tools. REST /tools returns the full list; filter client-side.
tools = requests.get(f"{BASE}/tools", headers=HEADERS).json()
alphafold = next(t for t in tools if t["name"] == "alphafold")

# 2. Get the exact schema for the chosen tool.
#    REST: each /tools entry already includes its inline `settings` schema
#          (parameter list) — find the entry whose name == your job type.
#    MCP:  getJobSchema(jobType) returns the same per-tool detail.

# 3. Submit a job. `settings` is tool-specific — match the schema exactly.
payload = {
    "jobName": "my-alphafold-run",          # ^[a-zA-Z0-9_-]+$, <=100 chars, unique
    "type": "alphafold",
    "settings": {
        "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
        "numRecycles": 3,
    },
}
resp = requests.post(f"{BASE}/submit-job", headers=HEADERS, json=payload)
resp.raise_for_status()   # 200 ok; 400 bad request; 403 budget exceeded; 401 unauthorized

# 4. Poll for completion.
#    NOTE the response shape: GET /jobs?jobName=<name> returns the job ROW
#    directly (no "jobs" wrapper); the list query (no jobName) returns
#    {"jobs": [...]}. Don't index ["jobs"][0] on the by-name response.
while True:
    job = requests.get(f"{BASE}/jobs", headers=HEADERS,
                       params={"jobName": "my-alphafold-run"}).json()
    if job["JobStatus"] in ("Complete", "Stopped", "Deleted"):
        break
    time.sleep(30)

# 5. Retrieve results. POST /result returns a presigned URL *string*;
#    GET that URL to download the actual results zip (two-step).
url = requests.post(f"{BASE}/result", headers=HEADERS,
                    json={"jobName": "my-alphafold-run"}).text.strip('"')
open("my-alphafold-run.zip", "wb").write(requests.get(url).content)
```

For the agentic version of this loop using MCP tools, and for richer examples, see `references/workflows.md`.

## Discovering tools

The catalog has hundreds of tools. Always enumerate at runtime — never rely on a hardcoded list.

**REST** `GET /tools` returns the **full list** (it does not filter server-side); each item is `{name, displayName, github, paper, description, settings}` where `settings` is that tool's inline parameter schema. Filter client-side:

```python
tools = requests.get(f"{BASE}/tools", headers=HEADERS).json()   # a list
boltz = [t for t in tools if "boltz" in t["name"].lower()]
```

Note: both surfaces return one row per tool name — REST `/tools` and MCP `getAvailableTools` are both deduplicated (the MCP keeps the newest tool version), so a name match returns a single row.

**MCP** `getAvailableTools(search=..., modality=..., function=...)` filters server-side and adds `categories`/`tags` per tool (`category`/`tag` are deprecated aliases of `modality`/`function`, still honored). Don't hardcode the vocabulary — it drifts. Get the live values from `listModalities()` / `listTags()` (each returns `value`, `label`, `description`, and `toolCount`), or read the `availableCategories` / `availableTags` facet arrays returned on every `getAvailableTools` response. Modalities are molecule types (protein, antibody, peptide, small-molecule, nucleic-acid, …); functions are what a tool does (structure-prediction, binder-design, protein-ligand-docking, …).

A representative set of widely-used tools (verify with `/tools`): `alphafold`, `boltz` (Boltz-2), `chai` (Chai-1), `esmfold` / `esmfold2`, `rfdiffusion`, `proteinmpnn`, `ligandmpnn`, `boltzgen`, `bindcraft`, `diffdock`. See `references/tool_catalog.md` for the full category/tag map and how to read tool metadata.

## Choosing the right tool

The catalog has many tools per task; **don't hardcode a favorite — filter by `function` (and `modality`), then read each candidate's `description` and match it to the user's actual goal** (input you have, output you need, constraints like speed or "no MSA"). The `description` and `tags` fields are the public "what it's for" signal; let them, plus `validateJob`, drive the pick. Quick orientation by task:

- **Fold a single protein / complex** (`function=structure-prediction`): the AlphaFold3-class reproductions — `boltz`/`chai`/`openfold`/`protenix`/`intfold` — are the accurate default for **everything**, including protein-only systems; they also handle **nucleic-acid + small-molecule complexes**, so reach for them whenever a ligand/RNA/DNA is part of the system (and `boltz` adds binding-affinity). `alphafold` (AF2) remains a solid choice for monomers + multimers (join chains with `:`). `esmfold` is single-sequence (no MSA) and fast — reach for it when you want speed and have no MSA; `esmfold2` is newer and conditions on an MSA by default (its `model` setting offers a faster single-sequence mode). Specialized folders exist for antibodies (`abodybuilder`, `immunebuilder`), cyclic peptides (`highfold`), and conformational ensembles (`afcluster`, `alphaflow`) — filter and read descriptions.
- **Design a binder** (`function=binder-design`): `bindcraft` (de novo miniprotein binders) and `boltzgen` (binders for protein **and** small-molecule targets, incl. nanobodies/antibodies/peptides) are the go-to de novo binder tools; `rfdiffusion` also does binder design and is the pick for **motif scaffolding** / diversifying an existing backbone. Antibody-specific generators live under `function=antibody-design`.
- **Design sequence for a known backbone** (`function=inverse-folding`): `proteinmpnn` (general), `ligandmpnn` (ligand-aware), plus thermostable/soluble/antibody MPNN variants. Inverse folding takes a **structure** and emits **sequences** — fold them back to verify (see chaining).
- **Dock a small molecule** (`function=protein-ligand-docking`): prefer `boltz`/`chai` — they co-fold the ligand into the complex and predict the bound structure rather than docking into a fixed receptor; reach for `autodock-vina` when you need fast, large-scale screening against a known pocket.
- **Predict binding affinity** (`function=binding-affinity`) or **generate an MSA** (search `msa`) — filter and read.

When the user names a specific tool, evaluate that one **and** sanity-check the alternatives in its `tag` group — a faster or more appropriate sibling often exists. When unsure, `getJobSchema`/`validateJob` to confirm a candidate actually accepts the input you have before committing.

## Job settings, schemas, and validation

Each tool has its own `settings` schema. Fetch it before submitting:

- **REST** `/tools` entry: each `settings` param is a **trimmed** dict. Only `name` and `required` are always present; `type`, `default`, `description`, `options` appear only when relevant (≈60% have `type`) — so use `param.get("type")`, not `param["type"]`. The advanced gating keys (`exclude`, `conditionals`) are **NOT in the REST response** at all.
- **MCP** `getJobSchema(jobType)`: the **full** schema, including `exclude`, `conditionals`, and bounds. Use MCP when you need to reason about those gating keys. (`restrictOrgs` is stripped on both surfaces — an org-gated param you can't use is simply omitted; see `references/api_reference.md`.)

**Always `validateJob` (MCP) before submitting** — it's the reliable guard. It runs the same validation as `/submit-job` without submitting, and surfaces the first missing/invalid field. Don't try to hand-derive which fields to strip from the schema keys (over REST you can't see them anyway) — let `validateJob` tell you. (The response may include a `source` field, e.g. `"static-fallback"` — an internal note on which schema source validated; `valid: true/false` is the signal you act on.)

`validateJob` echoes a `normalized` view of your settings with defaults filled in. Submit the same clean `settings` you validated; treat `normalized` as informational (it can carry defaults you didn't set, and for some tools platform-managed fields), so build your submit from your own settings rather than the normalized blob.

**Sequences:** amino-acid string; separate chains of a multimer with a colon (`:`), e.g. `"MVLS...:EVQL..."`. Note that some tools (e.g. `boltz`, `chai`) require more than `sequence` — `boltz` also requires `inputFormat` (and accepts `yamlFile`/`molecules`). Always `getJobSchema`/`validateJob` to learn a tool's required fields; don't assume `sequence` alone suffices.

**Platform-internal fields** — never set these yourself; the platform owns them: `submit_method`, `monomer_msa`, `msa`. See `references/api_reference.md` for the full field-handling rules.

**Surface consequential choices before submitting, don't default silently.** When the request fully specifies what to run, proceed. But when it's open-ended, or when a setting materially changes the results, runtime, or cost (model/variant, number of samples or seeds, MSA on/off, GPU tier, batch size), present the meaningful options plus the default you'd otherwise apply and let the user pick **before** you submit — rather than choosing silently and reporting it after the job is queued. `getJobSchema` and `validateJob`'s `normalized` show exactly which knobs you're filling in on the user's behalf, so you can flag the few worth a quick confirm. This matters most for **batches**, where one shared-settings choice multiplies across every job.

## File inputs (PDB, CIF, SDF, …)

Tools with file parameters accept input three ways:

1. **Upload first, then reference by bare filename.** `PUT /upload/{filename}`, or MCP `uploadFile` → presigned URL → `curl -X PUT -T file "<url>"`. If your host can't reach S3 (a sandboxed agent with no outbound network), use MCP `uploadFileContent(filename, content, encoding?)` to send the file's content through the MCP channel instead — text by default, `encoding="base64"` for binary. The object lands at the S3 key `{email}/{filename}`, **but you reference it in `settings` by the bare `filename` only** (e.g. `"targetFile": "GLP1R_ECD.pdb"`) — the platform scopes it to your account automatically. **Do NOT prefix the email**: passing `{email}/{filename}` double-prefixes the lookup and `submit-job` 400s with `"The following files have not been uploaded: <email>/<file>"`. Confirm the exact name the store registered with MCP `getFiles(search=...)` / REST `GET /files` (a flat list of bare names).
2. **Reference a prior job's output** by its path: `JobName/path/to/file.ext` (this is how you chain jobs — see below).
3. **Inline content.** Send the file's text content directly as the field value.

**Foot-gun:** for a file-typed parameter, a **plain string value is treated as inline file content**, not as a path to an existing object. To point at an already-uploaded file, use the bare `filename` (not the `{email}/...` S3 key) or, for a prior job's output, the `JobName/...` path form — not a bare string you expect to resolve to new content.

**`validateJob` notes.** The response may carry a `source` field (e.g. `"static-fallback"`) — it labels how the tool's *schema* was resolved (built-in tools always report `static-fallback`), **not** whether the validator was reachable, so act on `valid`, not `source`. For file params: reference an uploaded file by its **bare filename** (above) — a bare name resolves to your account-scoped object, whereas an email-prefixed string can be read as inline content and fail the file-type check (`"... must contain ATOM records"`). And passing **inline** file content makes `validateJob` upload it synchronously before validating, which can be slow; prefer referencing an uploaded file by name (above). If a dry-run is slow, skip it and let `submit-job` validate.

## Chaining jobs into pipelines

A finished job's output becomes the next job's input — no download/re-upload. **Match the input type the next tool actually wants:** a sequence-design tool (ProteinMPNN) emits *sequences*, so you fold them by passing each as a `sequence`; a tool that takes a *file* parameter takes a path.

The cleanest design→fold chain is the MCP `submitBatch(fromJob=...)`, which reads a completed design job's generated sequences and folds each as one job:

```
# ProteinMPNN designs sequences -> fold every one with AlphaFold, one call:
submitBatch(batchName="verify-designs", type="alphafold", fromJob="my-proteinmpnn-job")
```

For a **file** input (e.g. a tool that takes a `.pdb`/`.cif`), reference a prior job's output by the path form `JobName/path/to/file.ext` in that file parameter. Two cautions, both confirmed by validation: (1) match the parameter's required **file type** — e.g. AlphaFold's `templateFiles` accepts only `.cif` and is a list, and is gated behind `templateMode: "custom"`; (2) `templateFiles` is for *structural templates*, not for "fold this designed sequence" — to fold a sequence, pass `sequence`. Always `getJobSchema`/`validateJob` to confirm a file param's type/conditions before chaining into it.

To discover a job's exact output paths, use MCP `listJobFiles(job1)` — it returns each file's `s3Path`, usable directly in the next `submitJob`. (The REST `GET /files` lists your account's *uploaded* files as a flat name list; it does not enumerate a job's outputs.) Tamarind also supports saved **pipelines**: build one in the UI, then drive it with `/run-pipeline` (`{pipelineName, initialInputs, inputs}`) or define `stages[]` inline via `/submit-pipeline` (each stage names a `task` + `toolSettings`, using `"pdbFile": "pipe"` to thread one stage's output into the next). See `references/workflows.md`.

## Batch submission

Submit many jobs of the **same tool** in one call. The Python form uses parallel `settings[]` and `jobNames[]` arrays (same length, up to 100):

```python
requests.post(f"{BASE}/submit-batch", headers=HEADERS, json={
    "batchName": "egfr-binder-screen",
    "type": "alphafold",
    "jobNames": ["seq1", "seq2", "seq3"],
    "settings": [{"sequence": "..."}, {"sequence": "..."}, {"sequence": "..."}],
    # optional: "maxRuntimeSeconds": 3600, "weightedHoursBudget": 100,
    # (some accounts also accept an optional "gpuType" — confirm with support)
})
```

**Poll the batch *parent* on `batchStatus`, not subjob `JobStatus`.** A batch creates a parent job (`Type: "batch"`) plus subjobs. Subjobs flip to `Complete` as soon as they finish computing, but the batch then spends a few minutes **aggregating** results into the final downloadable output. Fetch the parent by name and watch `batchStatus`:

```python
import time
while True:
    # ?jobName= returns the parent ROW directly (no "jobs" wrapper)
    parent = requests.get(f"{BASE}/jobs", headers=HEADERS,
                          params={"jobName": "egfr-binder-screen"}).json()
    bs = parent.get("batchStatus")
    if bs == "Complete":
        break
    if bs in ("Stopped", "AggregationFailed"):
        raise RuntimeError(parent.get("AggregationError", bs))
    time.sleep(15)   # Running / Aggregating -> keep waiting
# When Complete, the parent carries a presigned `resultUrl` and a `statuses`
# subjob tally ({Complete, Running, In Queue, Stopped}).
open("batch.zip", "wb").write(requests.get(parent["resultUrl"]).content)
```

Add `includeSubjobs=true` to `GET /jobs?batch=<name>` to list per-subjob rows.

## Job status lifecycle

Single jobs report `JobStatus`; batch parents report `batchStatus` (poll that for batches — see above).

| Status | Meaning |
|---|---|
| `In Queue` | Accepted, waiting for capacity |
| `Running` | Executing on a worker |
| `Complete` | Finished successfully — results available |
| `Stopped` | Stopped (failure, timeout, manual stop, or budget) |
| `Deleted` | Job was deleted out-of-band |
| `Aggregating` | (batch parent only) subjobs done; building the final output |
| `AggregationFailed` | (batch parent only) aggregation step failed |

Completed jobs carry a `Score` (tool-specific metrics, e.g. pLDDT/pTM/ipTM for folding) and `WeightedHours`. Treat `Complete`/`Stopped`/`Deleted` (and `AggregationFailed` for batches) as terminal; poll on a 15-30s interval. **Break your poll loop on any terminal status, not just `Complete`/`Stopped`** — a job that goes `Deleted` mid-poll would otherwise loop forever. For a `Stopped` job, fetch `getJobLogs(jobName)` to see why. `WeightedHours` is the usage unit billed per job; cap a batch with `weightedHoursBudget`, and a `403` on submit means a budget was hit (see `references/api_reference.md` and the `/usage-statistics` endpoint).

## Error handling

| Code | Meaning | Action |
|---|---|---|
| 400 | Bad request / invalid settings | Re-check against the schema; run `validateJob` first |
| 401 | Unauthorized | Check `x-api-key` |
| 403 | Budget exceeded (org/team) | Lower scope or raise the budget |
| 429 | Rate limited | Back off and retry |
| 500 | Server error | Retry; if persistent, contact support |

## Reference files

The `openapi.yaml` spec is the source of truth for endpoint shapes; these files add the behaviors and gotchas the spec doesn't spell out:

- `references/examples.md` — **validated** `settings` payloads per common tool (alphafold/boltz/diffdock/autodock-vina/proteinmpnn/batch), a copy-paste self-check, the "what fails and the exact error" list, and output-shape notes. Start here for a working payload.
- `references/api_reference.md` — endpoint quick-reference + the non-obvious shapes: `/jobs` by-name returns a bare row (not `{jobs:[...]}`), `/result` is a two-step download, batch parents poll on `batchStatus`, `/files` is a flat name list, the `settings` field-handling rules.
- `references/tool_catalog.md` — category/tag map, how to read tool + parameter metadata, common tool families.
- `references/workflows.md` — end-to-end recipes: fold a sequence, validate-before-submit, upload + reference a file, design→fold chaining, batch screen with aggregation polling, usage stats, pagination, and the non-blocking submit-now/check-later pattern for long jobs.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/tamarind/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/api_reference.md`

# Tamarind Bio REST API reference

**Spec:** the OpenAPI spec at `https://app.tamarind.bio/openapi.yaml` (3.0, auth `ApiKeyAuth`) covers the 8 **core job endpoints** (`/submit-job`, `/submit-batch`, `/jobs`, `/result`, `/upload/{filename}`, `/files`, `/delete-job`, `/delete-file`) — fetch it for those exact shapes. It does **not** include the discovery/management endpoints (`/tools`, `/usage-statistics`, `/submit-pipeline`, `/run-pipeline`, `/stop-job`) — for those, use this file + the live MCP `getAvailableTools`/`getJobSchema`/`getJobs`. This file also adds the behaviors no spec spells out (response-shape-by-query, two-step result download, batch aggregation polling, REST-vs-MCP field differences).

Base URL: `https://app.tamarind.bio/api/`
Authentication: `x-api-key: <YOUR_KEY>` header on every request.
Interactive docs: [app.tamarind.bio/api-docs](https://app.tamarind.bio/api-docs) · markdown docs at [docs.tamarind.bio](https://docs.tamarind.bio)

There is no official Python SDK. Call the API with `requests` (Python) or `curl`. An MCP server (`https://mcp.tamarind.bio/mcp`, `X-API-Key` header) exposes the same operations with agent-friendly schemas.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/tools` | List available tools and their inline parameter schemas. Returns the **full list** (no server-side filtering — filter client-side). |
| POST | `/submit-job` | Submit one job. Body: `jobName`, `type`, `settings` (+ optional `projectTag`). |
| POST | `/submit-batch` | Submit many jobs of the same tool. See payload shapes below. |
| GET | `/jobs` | List/inspect jobs. Query: `jobName`, `batch`, `limit`, `startKey`, `organization`, `includeSubjobs`, `jobEmail`. |
| POST | `/result` | Get a presigned download URL for job results (two-step — see below). Body: `jobName` (+ optional `fileName`, `pdbsOnly`, `jobEmail`). |
| POST | `/stop-job` | Stop a running or queued job. Body: `jobName`. |
| DELETE | `/delete-job` | Delete a job and its data. Body: `jobName`. |
| PUT | `/upload/{filename}` | Upload a file (`--data-binary`; add `?folder=` to file it). Or get a presigned URL via MCP `uploadFile`. |
| GET | `/files` | List your account's uploaded files as a flat array of filename strings. Query: `folder`, `includeFolders=true`. Does **not** enumerate a specific job's outputs — use MCP `listJobFiles` for that. |
| DELETE | `/delete-file` | Remove a file/folder. Query: `filePath` or `folder`. |
| POST | `/submit-pipeline` | Run a multi-step pipeline defined inline via `stages[]`. |
| POST | `/run-pipeline` | Run a pipeline saved in the UI. Body: `pipelineName`, `initialInputs`/`inputs`. |
| GET | `/usage-statistics` | Usage/billing. Query: `statistic` (`weighted_hours`/`jobs`), `scope` (`user`/org). |

## Request shapes

### GET /tools

Returns a JSON **array**. Each element:

```json
{
  "name": "alphafold",
  "displayName": "AlphaFold",
  "description": "Accurate and quick protein structure prediction ...",
  "github": "https://github.com/...",
  "paper": "https://...",
  "settings": [ { "name": "sequence", "type": "sequence", "required": true, "description": "..." }, ... ]
}
```

In each `settings` param, only `name` and `required` are guaranteed; `type`, `default`, `description`, `options` are present only when applicable (about 60% of params carry `type`). Read them with `param.get("type")`, not `param["type"]`.

`settings` is the tool's inline parameter schema — read it directly, no separate schema endpoint over REST. The REST list is not filtered by query params; filter client-side on `name`/`displayName`/`description`. (The MCP `getAvailableTools` wraps the list as `{"totalTools", "tools":[...]}` and adds `categories`/`tags` per tool plus server-side `search`/`category`/`tag` filtering.)

### POST /submit-job

```json
{
  "jobName": "my-protein-analysis",
  "type": "alphafold",
  "settings": { "sequence": "MKT...", "numRecycles": 3 },
  "projectTag": "proj_xxxxxxxx"
}
```

- `jobName` — unique, `^[a-zA-Z0-9_-]+$`, 1-100 chars.
- `type` — a tool name from `/tools`. The list changes often; never hardcode.
- `settings` — tool-specific; match the schema from `/tools` (or MCP `getJobSchema`).
- `projectTag` — optional `proj_...` ProjectId to file the job under a project.

Response (200): a confirmation string like `myJobName submitted to queue.`

### POST /submit-batch

Two payload shapes appear in the official docs — the **Python** form uses parallel arrays; the **curl** form uses a `jobs[]` array of objects with a `tool` key. The parallel-array form matches the MCP `submitBatch` and is the recommended one:

```json
{
  "batchName": "egfr-screen",
  "type": "alphafold",
  "jobNames": ["seq1", "seq2"],
  "settings": [{ "sequence": "..." }, { "sequence": "..." }],
  "maxRuntimeSeconds": 3600,
  "weightedHoursBudget": 100
}
```

curl-form alternative (same endpoint): `{ "tool": "<type>", "batchName": ..., "jobs": [{ "jobName": ..., "settings": {...} }, ...] }`.

- `jobNames` and `settings` are parallel arrays, same length, 1-100 items, all using the same tool.
- `maxRuntimeSeconds` — optional per-job timeout. `weightedHoursBudget` — optional budget cap.
- The MCP `submitBatch` schema exposes `maxRuntimeSeconds` + `weightedHoursBudget`. Some accounts/tools may accept an optional `gpuType` (seen in the docs UI), but it isn't in `openapi.yaml` or the MCP schema — treat it as unverified and confirm with support before relying on it.

### GET /jobs

**Response shape depends on the query:**
- **List / batch query** (no `jobName`, or `?batch=`/`?organization=`) → `{ "jobs": [...], "startKey": "...", "statuses": {...} }`.
- **By-name** (`?jobName=<name>`) → the **job row object directly** (no `jobs` wrapper). Don't index `["jobs"][0]` on this response.

Each job row includes `JobName`, `Type`, `JobStatus`, `Created`, `Started`, `Completed`, `Settings` (JSON string), `Score` (JSON string, tool metrics), `WeightedHours`. Use `startKey` for pagination past the `limit` (default 1000). Only top-level jobs return by default; add `includeSubjobs=true` for batch subjobs.

**Batch parent rows** have `Type: "batch"` and carry `batchStatus`. Fetched by name (`?jobName=<batchName>`), a complete batch parent also includes `resultUrl` (presigned download). `batchStatus` transitions: `Running` → `Aggregating` → `Complete` (or `AggregationFailed`, with `AggregationError`). Poll the parent's `batchStatus`, not subjob `JobStatus` — subjobs go `Complete` before the aggregated output is ready.

**Discriminate batch vs single by `Type == "batch"` (or presence of `batchStatus`), not by `statuses`.** A by-name response can carry a `statuses` tally even for a single (non-batch) job, so `statuses` presence is not a reliable batch signal.

### POST /result (two-step download)

POST returns a presigned URL as a **bare string** (not JSON). Fetch that URL with a second GET to download the results zip:

```python
url = requests.post(f"{BASE}/result", headers=H, json={"jobName": "myJob"}).text.strip('"')
open("myJob.zip", "wb").write(requests.get(url).content)
```

Optional body fields: `fileName` (one file instead of the zip), `pdbsOnly: true` (PDB outputs only), `jobEmail` (a teammate's job, if permitted).

## Status codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request — invalid parameters/settings |
| 401 | Unauthorized — invalid/missing `x-api-key` |
| 403 | Budget exceeded (org/team) |
| 429 | Rate limited |
| 404 | Not found (e.g. unknown job) |
| 500 | Server error |

## Field-handling rules (important)

**The REST and MCP schemas expose different fields.** The REST `/tools` entry
gives a trimmed per-param view — `{name, type, required, default, description, options}`.
The advanced gating keys `exclude` and `conditionals` appear **only in MCP
`getJobSchema`**, not in REST `/tools` (`restrictOrgs` is no longer returned by
either surface — see below). So don't try to hand-derive what to strip from REST
schema keys — they aren't there. The reliable guard on
both surfaces is **`validateJob`** (MCP): it runs `/submit-job`'s exact validation
without submitting and returns the first error.

- **Build your submit from your own settings, not `validateJob`'s `normalized` output.**
  `normalized` is informational (defaults filled in, sometimes platform-managed
  fields). Submit the same clean settings you validated, not the normalized echo.
- **Platform-internal routing fields** — `submit_method`, `monomer_msa`, `msa` are
  set by the platform. Never pass them.
- **`restrictOrgs`** — org-gated parameters. `getJobSchema` no longer returns this
  key (it's stripped server-side): a parameter your account isn't authorized for is
  dropped from the schema entirely, and any param you do see is one you may set. So
  you won't encounter `restrictOrgs` in a response — don't look for it.
- **`conditionals`** (MCP schema only) — a field only applies when another field
  has a given value (e.g. `pairMode` applies only when `useMSA` is `true`). Don't
  send conditioned fields when their condition isn't met.
- **`exclude: [...]`** (MCP schema only) — marks a field as UI/pipeline-only for a
  surface. Treat it as advisory; `validateJob` is the authority on what a given
  submission accepts.
- **`required: true`** — must be present. Some tools require more than `sequence`
  (e.g. `boltz` requires `inputFormat`). Run `validateJob` to get the first
  missing/invalid field before submitting.
- **File-typed fields with a plain string value are treated as INLINE CONTENT**,
  not a path. To reference an **uploaded file**, use its **bare filename**
  (`target.pdb`) — the platform scopes it to your account, so do NOT email-prefix
  it. The `{email}/{filename}` form is the underlying S3 key, and passing it makes
  `submit-job` 400 with `"The following files have not been uploaded: <email>/<file>"`.
  To reference a **prior job's output**, use `JobName/path/to/file.ext`. Confirm the
  exact registered name with `getFiles` / `GET /files` (a flat list of bare names).

## Authentication and secrets

- Read the key from `TAMARIND_API_KEY` (env or `.env`); never hardcode or commit it.
- The same key authenticates REST (`x-api-key`) and the MCP server (`X-API-Key`).
- Query operations are scoped to the authenticated account (and, with `organization=true`/`jobEmail`, to your org if permitted).

### `references/examples.md`

# Tamarind Bio — validated examples & output shapes

**The freshest example for any tool is the `exampleJob` field MCP `getJobSchema(<tool>)`
now returns** — an `{jobName, type, settings}` built from each param's example/default
(with an `exampleJobNote`; org-gated params you can't use are omitted, file params get
placeholder filenames). It's the best starting point, but **run `validateJob` on it
before submitting** — it's assembled from per-param examples, not a guaranteed-valid
payload, so a given tool's `exampleJob` can need a tweak. The payloads below are a
`validateJob`-confirmed fallback for REST callers or when you want a worked example.
Tool schemas evolve — if one stops validating, re-fetch with `getJobSchema(<tool>)` /
`GET /tools`. Sequences here are illustrative; swap your own.

**File params (`proteinFile`, `pdbFile`, `ligandFile`, …) need a real file value** —
either the **bare filename** of an uploaded file (`target.pdb` — NOT email-prefixed),
a prior-job output **path** (`JobName/out/x.pdb`), or
**inline PDB/SDF-format text** (multi-line `ATOM`/`HETATM` records). The
`<...>` placeholders below are NOT valid as written — replace them. **Do not put an
amino-acid sequence in a file param** — `validateJob` rejects it with
`File ... must be of types: ["pdb"]`. (A sequence goes in `sequence`, a structure
goes in a file param.)

`BASE = "https://app.tamarind.bio/api"`, `HEADERS = {"x-api-key": <key>}`.

## Self-check (run this first to confirm the skill works for you)

Read-only + dry-run, no submission, no cost. Confirms the discover → schema →
validate loop end-to-end:

```python
import os, requests
BASE, HEADERS = "https://app.tamarind.bio/api", {"x-api-key": os.environ["TAMARIND_API_KEY"]}

# 1. discovery reachable?
tools = requests.get(f"{BASE}/tools", headers=HEADERS).json()
assert isinstance(tools, list) and any(t["name"] == "alphafold" for t in tools), "tools endpoint"

# 2. validate a known-good payload (MCP validateJob; or skip if REST-only)
#    expect {"valid": true, ...}
```

With the MCP server: `validateJob(jobName="selfcheck", type="alphafold",
settings={"sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIE"})` → `valid: true`.

## Validated input payloads

### AlphaFold — monomer
```json
{ "sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKR",
  "numModels": "1", "numRecycles": 3 }
```
Only `sequence` is required; everything else has a default. `numModels` is a string
dropdown (`"1"`–`"5"`).

### AlphaFold — multimer (colon-separated chains)
```json
{ "sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIE:DIQMTQSPSSLSASVGDRVTITCRASQSISSYLN" }
```
Join chains with `:`. No separate "multimer" flag — chain count drives it.

### Boltz-2 — sequence mode
```json
{ "inputFormat": "sequence",
  "sequence": "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALP" }
```
`inputFormat` is **required** (`"sequence"` / `"list"` / `"molecules"` / `"yaml"`).
Omitting it fails — see "What fails" below.

### DiffDock — protein + SMILES ligand
```json
{ "ligandFormat": "SMILES",
  "ligandSmiles": "CC(=O)Oc1ccccc1C(=O)O",
  "proteinFile": "<uploaded-path-or-inline-PDB-text>" }
```
`ligandFormat` chooses the conditional field: `"SMILES"` → `ligandSmiles`;
`"sdf/mol2 file"` → `ligandFile`. `proteinFile` is a file param — pass an uploaded
file's bare filename (`target.pdb`, not email-prefixed), a prior-job path
(`JobName/...`), or inline PDB text (see file-input rules in `api_reference.md`).

### Autodock Vina — protein + SMILES ligand (classical docking into a pocket)
```json
{ "receptorFile": "receptor.pdb",
  "ligandFormat": "smiles",
  "ligandSmiles": "CC(=O)Oc1ccccc1C(=O)O",
  "boxX": 15.19, "boxY": 53.903, "boxZ": 16.917,
  "width": 20, "height": 20, "depth": 20 }
```
Unlike DiffDock, Autodock Vina docks into a **fixed pocket**, so it requires a bounding
box (`boxX/Y/Z` center + `width/height/depth`, all required) and the receptor in
`receptorFile` (not `proteinFile`). Its `ligandFormat` enum is **lowercase**
(`"smiles"` / `"sdf"`) — different from DiffDock's `"SMILES"` / `"sdf/mol2 file"`, so
don't copy DiffDock's value across. `exhaustiveness` (default 8) is optional. `validateJob`-confirmed.

### ProteinMPNN — design residues on a backbone
```json
{ "pdbFile": "<uploaded-path-or-inline-PDB-text>",
  "designedResidues": { "A": "1 2 3 4 5" },
  "numSequences": 4, "modelType": "proteinmpnn" }
```
Requires `pdbFile` + `designedResidues` (per-chain, space-separated resnums).
`modelType` ∈ `proteinmpnn`/`ligandmpnn`/`solublempnn`/`hypermpnn`/`abmpnn`.
Note `designedChains` is `exclude:["api"]` — don't send it over the API.

### Batch (same tool, many jobs)
```json
{ "batchName": "screen-1", "type": "alphafold",
  "jobNames": ["s1", "s2"],
  "settings": [ { "sequence": "MKT..." }, { "sequence": "AVF..." } ] }
```

## What fails (and the exact error) — confirmed live

- **Boltz without `inputFormat`** → `valid:false`, `Missing required boltz field "inputFormat"`. Always check required fields with `getJobSchema` first; `sequence` alone is not enough for boltz/chai.
- **Building a submit from `validateJob`'s `normalized` blob** — `normalized` is informational (defaults filled in, sometimes platform-managed fields). Submit the clean `settings` you validated, not the normalized echo.
- **File param given a bare string that isn't a real path** → treated as INLINE file content (uploaded as `<email>/<jobname>-<param>.<ext>`), not a reference. To point at an existing uploaded file use its **bare filename** (`target.pdb` — do NOT email-prefix it; `{email}/{filename}` is the S3 key and 400s as not-uploaded), or `JobName/...` for a prior job's output. Referencing a path that doesn't exist → `File ... has not been uploaded`.

## Output shapes (describe, don't expect exact values)

Outputs are non-deterministic (seed/model/MSA) — reason about the *shape*, not
golden numbers.

- **Job row `Score`** (JSON string on completed jobs): tool-family dependent.
  - Folding (alphafold/boltz/chai/esmfold): `plddt`, `ptm`, and for complexes
    `iptm` plus interface metrics (`ipSAE_*`, `pDockQ_*`). Higher pLDDT/pTM = more
    confident; iptm/ipSAE gauge interface quality.
  - Other families carry their own metrics — read the keys, don't assume.
- **Results zip** (`POST /result` → presigned URL → GET): per-tool, typically the
  structure files (`rank_*.pdb` / `*.cif`), a scores CSV, and logs. Use
  `listJobFiles(jobName)` (MCP) to enumerate exact filenames before downloading.
- **`WeightedHours`** on the row is the billing unit (see `usage-statistics`).

To learn a specific tool's exact outputs, run one small job and `listJobFiles` it —
don't hardcode filenames, which vary by tool and version.

### `references/tool_catalog.md`

# Tamarind Bio tool catalog

Tamarind exposes hundreds of tools through one uniform job API. The catalog changes frequently — **always enumerate at runtime** with `GET /tools` (or MCP `getAvailableTools`) rather than hardcoding names. This file is a map for interpreting what you get back.

## How to discover

**REST** `GET /tools` returns the **full list** (it does not filter server-side). Filter client-side:

```python
tools = requests.get(f"{BASE}/tools", headers=HEADERS).json()      # a list
docking = [t for t in tools if "vina" in t["name"].lower()]
```

Each REST tool entry carries: `name` (the `type` you submit), `displayName`, `description`, `github`, `paper`, and `settings` (the inline parameter schema). REST entries do **not** include `categories`/`tags`.

**MCP** `getAvailableTools(search=..., modality=..., function=...)` filters server-side and returns entries with `categories` and `tags` (`category`/`tag` are deprecated aliases of `modality`/`function`, still honored).

## Modalities and functions (the two filter axes)

Don't hardcode the filter vocabulary — it drifts as tools are added. Fetch it live: `listModalities()` returns the molecule-type axis (protein, antibody, enzyme, peptide, nucleic-acid, small-molecule, small-molecule-binding-protein, cryoem, …); `listTags()` returns the function axis (structure-prediction, protein-design, binder-design, protein-ligand-docking, binding-affinity, inverse-folding, developability, molecular-dynamics, finetuning, …). Each entry carries `value`, `label`, `description`, and a live `toolCount`. Every `getAvailableTools` response also includes `availableCategories` / `availableTags` arrays computed from the current catalog. Filter with `getAvailableTools(modality=..., function=...)`.

## Representative tool families

Verify exact names and availability with `/tools` — these are common anchors, not an exhaustive or guaranteed list.

**Structure prediction / folding**
- `alphafold` — AlphaFold; monomer + multimer, MSA + templates, recycles, relaxation.
- `boltz` — Boltz-2; structure + affinity, biomolecular complexes incl. ligands.
- `chai` — Chai-1; complex structure prediction with optional MSA.
- `esmfold` / `esmfold2` — fast single-sequence folding.

**Protein / binder design**
- `rfdiffusion` — protein/binder design and motif scaffolding.
- `boltzgen` — generative design.
- `bindcraft` — binder design.
- `proteinmpnn` / `ligandmpnn` — inverse folding (sequence given backbone; ligand-aware variant).

**Docking / affinity**
- `boltz` / `chai` — co-fold the ligand into the complex (predict the bound structure); the default for protein-small-molecule docking.
- `autodock-vina` — classical docking into a known pocket; the pick for fast, large-scale screening.
- Boltz/affinity tools — binding-affinity prediction.

**Antibody**
- Antibody language models and generators, humanization, developability, immunogenicity scoring.

**MSA / utilities**
- MSA generation tools feed downstream folding; utilities cover format conversion, scoring, and analysis.

## Reading a tool schema

`getJobSchema(jobType)` (MCP) or the `/tools` entry returns a `parameters` list. Each parameter has:

- `name`, `type` (`sequence`, `number`, `boolean`, `dropdown`, file types like `pdb`/`cif`/`sdf`, …)
- `descr`, `displayName`
- `required`, `default`
- `options` / `optionsDescr` (for dropdowns), `lowerBound` / `upperBound` / `lengthLimit`
- `conditionals` — applies only when another field has a given value
- `exclude` (`["api"]` / `["batch"]`) — omit on that surface
- `list: true` — accepts multiple values/files
- `example` — a sample value

(Org-gated parameters are filtered server-side: `getJobSchema` drops a param your account isn't authorized for and never returns the old `restrictOrgs` key.)

Top-level tool metadata also includes a `hint`, and `getJobSchema` returns an `exampleJob` built from each parameter's example/default — start from that (then `validateJob` it) rather than hand-building `settings`.

Always read the schema before constructing `settings`, and run `validateJob` to confirm before `submitJob`.

### `references/workflows.md`

# Tamarind Bio workflow recipes

End-to-end examples using plain `requests`. All use `BASE = "https://app.tamarind.bio/api"` and
`HEADERS = {"x-api-key": os.environ["TAMARIND_API_KEY"]}`. For exact request/response
shapes, fetch the spec at `https://app.tamarind.bio/openapi.yaml`.

The canonical loop is always: **discover → schema → validate → submit → poll → results**.

## 1. Fold a single sequence (AlphaFold)

```python
import os, time, requests
BASE = "https://app.tamarind.bio/api"
HEADERS = {"x-api-key": os.environ["TAMARIND_API_KEY"]}

# discover + confirm the tool exists (REST returns the full list; filter client-side)
tools = requests.get(f"{BASE}/tools", headers=HEADERS).json()
assert any(t["name"] == "alphafold" for t in tools)

job = {
    "jobName": "ubiquitin-fold",
    "type": "alphafold",
    "settings": {
        "sequence": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
        "numModels": "5",
        "numRecycles": 3,
        "useMSA": True,
    },
}
requests.post(f"{BASE}/submit-job", headers=HEADERS, json=job).raise_for_status()

# poll. GET /jobs?jobName= returns the job ROW directly (no "jobs" wrapper).
while True:
    row = requests.get(f"{BASE}/jobs", headers=HEADERS,
                       params={"jobName": "ubiquitin-fold"}).json()
    if row["JobStatus"] in ("Complete", "Stopped", "Deleted"):
        break
    time.sleep(30)

print("status:", row["JobStatus"], "score:", row.get("Score"))

# results download is two-step: POST /result returns a presigned URL *string*,
# then GET that URL for the zip.
url = requests.post(f"{BASE}/result", headers=HEADERS,
                    json={"jobName": "ubiquitin-fold"}).text.strip('"')
open("ubiquitin-fold.zip", "wb").write(requests.get(url).content)
```

## 2. Multimer / complex (colon-separated chains)

For AlphaFold, a multimer is just one `sequence` with chains joined by `:`.

```python
job = {
    "jobName": "ab-ag-complex",
    "type": "alphafold",
    "settings": {
        # heavy:light:antigen — separate chains with ":"
        "sequence": "EVQLVESGGG...:DIQMTQSPSS...:MKTAYIAKQR...",
    },
}
requests.post(f"{BASE}/submit-job", headers=HEADERS, json=job).raise_for_status()
```

Other folding tools need more fields — `boltz`/`chai` require `inputFormat`
(`"sequence"`/`"list"`/`"molecules"`/`"yaml"`), e.g. boltz sequence-mode is
`{"inputFormat": "sequence", "sequence": "...:..."}`. **Always check required
fields with `getJobSchema`/`validateJob` first** — don't assume `sequence` alone
is enough.

## 3. Validate before submitting (MCP)

When your agent host has the Tamarind MCP server, dry-run first to catch errors
without spending a submission. Validate and submit **your own clean settings** —
build the submit from `my_settings`, not `verdict["normalized"]` (normalized is
informational: defaults filled in, sometimes platform-managed fields).

```
getJobSchema(jobType="boltz")               # learn required fields first
my_settings = {"inputFormat": "sequence", "sequence": "...:..."}
verdict = validateJob(jobName="x", type="boltz", settings=my_settings)
# verdict.valid == True  -> good; submit my_settings (NOT verdict.normalized)
# verdict.valid == False -> verdict.error is the first problem to fix
if verdict["valid"]:
    submitJob(jobName="x", type="boltz", settings=my_settings)
```

## 4. Upload a structure, then submit a job that uses it

```python
# REST: PUT the file to /upload/{filename}
with open("target.pdb", "rb") as fh:
    requests.put(f"{BASE}/upload/target.pdb", headers=HEADERS, data=fh).raise_for_status()
# the object's S3 key is "{your-email}/target.pdb", but you reference it by the
# BARE filename — the platform scopes it to your account. Do NOT email-prefix it.
job = {
    "jobName": "dock-run",
    "type": "diffdock",
    "settings": {
        "proteinFile": "target.pdb",   # bare filename, NOT inline content, NOT email-prefixed
        "ligandFormat": "SMILES",                       # required; gates ligandSmiles vs ligandFile
        "ligandSmiles": "CC(=O)Oc1ccccc1C(=O)O",
    },
}
requests.post(f"{BASE}/submit-job", headers=HEADERS, json=job).raise_for_status()
```

MCP variant: `uploadFile("target.pdb")` returns a presigned `uploadUrl`; then
`curl -X PUT -T target.pdb "<uploadUrl>"`.

**Reminder:** a bare *non-filename* string in a file-typed field is uploaded as inline content.
To point at an existing uploaded file, use its **bare filename** (`target.pdb`) — NOT the
`{email}/{filename}` S3-key form, which `submit-job` 400s as `"... has not been uploaded"`.
Confirm the registered name with `getFiles`/`GET /files`. For a prior job's output, use `JobName/...`.

For `autodock-vina` instead of DiffDock, the same upload-then-reference flow applies, but the
settings differ: it docks into a fixed pocket, so it needs `receptorFile` + a bounding box
(`boxX/Y/Z`, `width/height/depth`) and a **lowercase** `ligandFormat` (`"smiles"`/`"sdf"`).
Run `getJobSchema("autodock-vina")` for the full shape; see `examples.md` for a worked payload.

## 5. Chain jobs: design → fold

A sequence-design tool (ProteinMPNN) emits **sequences**, so you fold them by
passing each as a `sequence` — NOT via a template/file field. The cleanest way is
the MCP `submitBatch(fromJob=...)`, which reads the design job's generated
sequences and folds each as one job in a single call:

```
# Step 1: design sequences for a backbone
submitJob(jobName="design-step", type="proteinmpnn", settings={...})   # poll to Complete

# Step 2: fold every designed sequence (MCP reads them from the design job)
submitBatch(batchName="fold-designs", type="alphafold", fromJob="design-step")
```

Doing it over plain REST instead: read the design job's output sequences (MCP
`listJobFiles("design-step")` → `s3Path`, or download the FASTA via `/result`),
then submit one fold per sequence with `settings={"sequence": "<designed seq>"}`.

**Don't chain a designed sequence through a file/template field.** A file
parameter wants a *file of the right type*, and a template field is for structural
homology, not "fold this sequence." Example of the trap: AlphaFold's
`templateFiles` accepts only `.cif`, must be a **list**, and is gated behind
`templateMode: "custom"` — so `{"templateFiles": "design-step/out/x.pdb"}` fails
validation three ways and isn't how you fold a design anyway. When a chain really
does feed a file (e.g. a PDB into a docking tool), `getJobSchema`/`validateJob`
first to confirm the param's type and conditions.

For reusable multi-step flows, build a saved pipeline with `/submit-pipeline`
and run it with `/run-pipeline`.

## 6. Batch screen many sequences through one tool

Submit, then poll the batch **parent** on `batchStatus` (not subjob `JobStatus`)
— the batch aggregates results after subjobs finish computing.

```python
seqs = ["MKT...", "AVF...", "GEV..."]
requests.post(f"{BASE}/submit-batch", headers=HEADERS, json={
    "batchName": "binder-screen",
    "type": "alphafold",
    "jobNames":  [f"cand-{i}" for i in range(len(seqs))],
    "settings":  [{"sequence": s} for s in seqs],
    "weightedHoursBudget": 50,        # optional budget cap
}).raise_for_status()

# poll the parent until the aggregated output is ready
# (?jobName= returns the parent ROW directly — no "jobs" wrapper)
while True:
    parent = requests.get(f"{BASE}/jobs", headers=HEADERS,
                          params={"jobName": "binder-screen"}).json()
    bs = parent.get("batchStatus")
    if bs == "Complete":
        break
    if bs in ("Stopped", "AggregationFailed"):
        raise RuntimeError(parent.get("AggregationError", bs))
    time.sleep(15)        # Running / Aggregating -> keep waiting

print(parent["statuses"])  # e.g. {"Complete": 3, "Running": 0, "In Queue": 0, "Stopped": 0}
open("binder-screen.zip", "wb").write(requests.get(parent["resultUrl"]).content)

# Per-subjob rows (e.g. to read each candidate's Score):
subjobs = requests.get(f"{BASE}/jobs", headers=HEADERS,
                       params={"batch": "binder-screen", "includeSubjobs": "true"}).json()
```

## 7. Debug a stopped job

```python
# REST: pull results/log path; MCP gives logs directly
logs = getJobLogs("binder-screen-cand-2")   # MCP: last N lines of output log
# Inspect the tail for the failure reason (bad input, OOM, timeout, budget).
```

A `Stopped` status with no `Score` usually means a failure — read the log tail.
A `403` at submit means a budget cap was hit.

## 8. List every job (paginate past the 1000 limit)

The list query returns `{"jobs": [...], "startKey": ...}`; pass `startKey` back
until it's absent.

```python
jobs, params = [], {"limit": 1000}
while True:
    resp = requests.get(f"{BASE}/jobs", headers=HEADERS, params=params).json()
    jobs += resp["jobs"]
    if "startKey" not in resp:
        break
    params["startKey"] = resp["startKey"]
print(len(jobs))
```

## 9. Submit now, check back later (non-blocking)

Bio jobs run for minutes to hours — you don't have to hold a blocking poll loop
open. Jobs are addressable by `jobName` from any process, so submit, **persist the
names**, and reconnect in a separate session/process to collect results. This is the
right pattern for long campaigns or fire-and-forget pipelines.

```python
# --- Session 1: submit and save the job names ---
import os, json, requests
BASE = "https://app.tamarind.bio/api"
HEADERS = {"x-api-key": os.environ["TAMARIND_API_KEY"]}

seqs = {"cand-a": "MKT...", "cand-b": "AVF...", "cand-c": "GEV..."}
for name, seq in seqs.items():
    requests.post(f"{BASE}/submit-job", headers=HEADERS,
                  json={"jobName": name, "type": "alphafold",
                        "settings": {"sequence": seq}}).raise_for_status()
json.dump(list(seqs), open("pending_jobs.json", "w"))   # persist to disk/db
print("submitted; check back later")
```

```python
# --- Session 2 (later, fresh process): collect whatever is done ---
import os, json, requests
BASE = "https://app.tamarind.bio/api"
HEADERS = {"x-api-key": os.environ["TAMARIND_API_KEY"]}

names = json.load(open("pending_jobs.json"))
done, pending = [], []
for name in names:
    row = requests.get(f"{BASE}/jobs", headers=HEADERS,
                       params={"jobName": name}).json()   # bare row, by-name
    (done if row["JobStatus"] in ("Complete", "Stopped", "Deleted") else pending).append(name)

print(f"{len(done)} terminal, {len(pending)} still running")
for name in done:
    url = requests.post(f"{BASE}/result", headers=HEADERS,
                        json={"jobName": name}).text.strip('"')
    open(f"{name}.zip", "wb").write(requests.get(url).content)
```

Re-run session 2 until `pending` is empty. For a server-driven variant, poll a batch
parent's `batchStatus` (recipe 6) instead of looping job-by-job.

## Notes

- **Polling cadence:** 15-30s. `Complete` and `Stopped` are terminal.
- **Scores:** completed folding jobs return pLDDT / pTM / ipTM (and interface
  metrics like ipSAE / pDockQ for complexes) in the `Score` field.
