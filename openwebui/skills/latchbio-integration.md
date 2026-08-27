---
name: latchbio-integration
description: Build, register, debug, and operate bioinformatics workflows on Latch using the Python SDK, CLI, Latch Data and Registry, Nextflow, Snakemake, programmatic execution, and Latch MCP. Use when authoring or deploying Latch workflows, configuring resources or interfaces, moving data, integrating Registry, or launching and monitoring runs.
---

# LatchBio Integration

## Current Baseline

This skill targets **Latch SDK 2.76.8**, released July 10, 2026. The package
metadata supports Python 3.9–3.12 and declares Python 3.9+.

Treat the installed package and its changelog as authoritative when a guide
disagrees with the SDK. Some Latch guides retain older Python ranges or
compatibility-specific pre-release pins, especially the Snakemake v2 tutorial.
Never combine commands or imports from different tracks without checking their
version requirements.

## When to Use

Use this skill to:

- Create or maintain Python SDK workflows and task graphs
- Package and register Python, Nextflow, or Snakemake pipelines
- Configure task CPU, memory, storage, GPU, caching, retries, and timeouts
- Work with Latch Data through `LPath`, `LatchFile`, `LatchDir`, or the CLI
- Read or update Latch Registry projects, tables, and records
- Design workflow forms, launch plans, samplesheets, messages, and result links
- Stage and debug workflow images with `latch register --staging` and `latch develop`
- Launch and monitor workflows through Python or Latch MCP
- Discover and use ready-to-run Latch workflows

## Route to the Right Reference

Read only the references needed for the task:

| Need | Reference |
|---|---|
| Python workflows, tasks, maps, conditions, caching | `references/workflow-creation.md` |
| `LPath`, legacy file types, Latch URLs, data CLI | `references/data-management.md` |
| Registry reads, transactions, samplesheets | `references/registry.md` |
| CPU, memory, storage, GPU, dynamic resources | `references/resource-configuration.md` |
| Nextflow and Snakemake packaging | `references/nextflow-snakemake.md` |
| Metadata, forms, launch plans, messages, automations | `references/ui-and-automation.md` |
| Registration, development, execution, monitoring | `references/operations-and-debugging.md` |
| Ready-to-use workflows and `latch.verified` | `references/verified-workflows.md` |
| Remote MCP setup and tool workflow | `references/latch-mcp.md` |

Before relying on a symbol, run `scripts/inspect_latch_sdk.py` against the
target SDK version. It performs local imports only and does not authenticate or
make network requests.

## Installation and Authentication

For a reproducible environment:

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install "latch==2.76.8"
```

On Windows, use WSL for the documented Linux workflow tooling.

Authenticate through the supported OAuth flow; do not read, print, copy, or
parse `~/.latch/token` manually:

```bash
latch login
latch workspace
```

Select a workspace non-interactively when its numeric ID is already known:

```bash
latch workspace --id 12345
```

`latch login` credentials are for the SDK and CLI. Latch MCP uses a separate
OAuth authorization and its credentials cannot be reused for general SDK
access.

## Fast Path

Create and remotely register the maintained subprocess template:

```bash
latch init covid-wf --template subprocess
latch register --yes --open covid-wf
```

Remote image building is the default. Use `--no-remote` only when a local
Docker daemon is available and a local build is intentional.

## Minimal Python Workflow

Keep workflow bodies declarative: invoke tasks and return their promises.
Perform computation and side effects inside tasks.

```python
from latch import small_task, workflow


@small_task
def reverse_complement(sequence: str) -> str:
    table = str.maketrans("ACGTacgt", "TGCAtgca")
    return sequence.translate(table)[::-1]


@workflow
def reverse_complement_workflow(sequence: str) -> str:
    """Return the reverse complement of a DNA sequence."""
    return reverse_complement(sequence=sequence)
```

Use `@workflow(metadata)` when the generated interface needs custom labels,
sections, validation rules, samplesheets, or documentation links. Use `LatchFile` or
`LatchDir` for automatic task input staging and output upload; use `LPath` for
imperative remote path operations.

## Recommended Development Lifecycle

1. **Inspect compatibility**
   - Confirm the installed SDK and Python version.
   - Identify whether the project is Python, Nextflow, the legacy Snakemake
     flag path, or the separately pinned Snakemake v2 tutorial track.

2. **Define a typed interface**
   - Annotate every workflow and task input and output.
   - Keep module import time free of network calls, data mutations, and secret
     retrieval. Isolate documented exceptions such as `workflow_reference`,
     which resolves the active workspace when its decorator is evaluated.
   - Use dataclasses and enums for structured parameters.

3. **Configure metadata and resources**
   - Match metadata parameter keys to the workflow signature.
   - Start with named task decorators, then use `custom_task` only when measured
     requirements justify it.

4. **Validate in the execution image**

   Fresh Nextflow and Snakemake projects must generate their
   version-compatible Python entrypoint before staging. In SDK 2.76.8, the
   staging branch does not generate one from `--nf-script` or `--snakefile`.

   ```bash
   latch register --staging .
   latch develop .
   ```

   Re-run staging registration after changing the Dockerfile or dependencies.
   Edits made inside the development container are not synced back.

5. **Register deliberately**

   ```bash
   latch register --yes --open .
   ```

   Useful controls:

   ```bash
   latch register --workspace-id 12345 .
   latch register --mark-as-release .
   latch register --workflow-module wf.custom_entrypoint .
   ```

   Duplicate registration exits with status `2`; it is not the same as a build
   failure.

6. **Launch only after reviewing cost and parameters**
   - Prefer the Console or Latch MCP for interactive operation.
   - Prefer `latch_cli.services.launch.launch_v2` for Python automation.
   - Do not use the deprecated `latch launch` CLI as a new integration pattern.

7. **Monitor and verify**
   - Check terminal status, task logs, result links, and scientific outputs.
   - Treat successful orchestration as necessary but not sufficient scientific
     validation.

## Operational Safety

- Ask for confirmation before launching paid compute, especially GPU or large
  batch runs.
- Ask for confirmation before `LPath.rmr`, `latch rmr`, Registry deletion, or
  overwriting shared destinations.
- Never log secrets, SDK tokens, signed URLs, or secret values.
- Call `get_secret()` only inside a task, use the returned value only for its
  intended service, and never return it as workflow output.
- Do not pass untrusted strings through shell commands. Prefer argument lists
  with `subprocess.run(..., check=True)`.
- Pin the SDK and workflow dependencies for releases. Upgrade only after
  reviewing the changelog and re-running staging tests.
- Treat generated files as generated: customize the documented extension file
  rather than editing output that the CLI will overwrite.

## Inspect the Installed SDK

From this skill directory:

```bash
uv run --no-project --python 3.12 --with "latch==2.76.8" \
  python scripts/inspect_latch_sdk.py
```

Use JSON output for automated comparisons:

```bash
uv run --no-project --python 3.12 --with "latch==2.76.8" \
  python scripts/inspect_latch_sdk.py --json
```

## Authoritative Sources

- Documentation index: https://wiki.latch.bio/llms.txt
- Workflow and SDK guides: https://wiki.latch.bio/workflows/overview
- SDK API reference: https://wiki.latch.bio/reference/sdk
- PyPI package: https://pypi.org/project/latch/
- SDK 2.76.8 release source: https://github.com/latchbio/latch/tree/0faa9dcd8186444ac008f50adf95d43f0fa30e06
- SDK changelog: https://github.com/latchbio/latch/blob/0faa9dcd8186444ac008f50adf95d43f0fa30e06/CHANGELOG.md
- Latch Console: https://console.latch.bio

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/latchbio-integration/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/data-management.md`

# Latch Data and Remote Paths

This reference distinguishes the two supported Python data models:

- `LPath` is the modern, `pathlib`-like API for explicit remote operations.
- `LatchFile` and `LatchDir` are the established workflow parameter types for
  automatic task staging and output upload.

Do not assume methods from one model exist on the other. In particular,
`LatchDir.glob()` is not a current SDK API.

## Choosing an API

Use `LPath` when you need to:

- Inspect, upload, download, copy, list, or delete a remote path explicitly
- Work from scripts, Pods, Plots, or task code
- Avoid automatic transfer of an entire directory
- Store an `LPath` value in Registry with SDK 2.67.22+

Use `LatchFile` or `LatchDir` when you need to:

- Expose a file or directory in a workflow form
- Automatically stage an input onto a task machine
- Automatically upload a returned task output
- Compose with older workflows or `latch.verified` wrappers

It is normal to accept a `LatchFile` in a workflow and construct an `LPath`
from its `remote_path` for a targeted remote operation.

## Latch URLs

Common forms include:

```text
latch:///path/in/current-workspace
latch://12345.account/path/in/workspace
latch://shared/path/to/shared-data
latch://67890.node
```

- `latch:///...` resolves relative to the active or execution workspace.
- Account-qualified URLs avoid ambiguity across workspaces.
- Node URLs address a Latch Data object by immutable numeric ID.
- Shared URLs refer to data shared across accounts.

Do not concatenate URLs with filesystem utilities that discard the URL scheme.
`LPath` supports `/` for child paths.

## `LPath`

Import it from its actual module:

```python
from latch.ldata.path import LPath
```

### Metadata and listing

```python
from latch.ldata.path import LPath

root = LPath("latch:///welcome")

if root.exists():
    print(root.node_id())
    print(root.name())
    print(root.is_dir())
    print(root.size_recursive())

    for child in root.iterdir():
        print(child.path, child.content_type(), child.size())
```

`iterdir()` is shallow. It returns an iterator of child `LPath` objects and
does not recursively traverse nested directories.

Metadata is cached for the lifetime of the object after a lookup. Call
`fetch_metadata()` after an external rename or modification when fresh values
are required.

### Download

Always provide an explicit destination for durable files:

```python
from pathlib import Path

from latch.ldata.path import LPath

remote = LPath("latch:///inputs/design.csv")
local = remote.download(Path("work/design.csv"), cache=True)
print(local.read_text(encoding="utf-8"))
```

Without a destination, the SDK downloads beneath `~/.latch/lpath/` and
registers the temporary directory for cleanup when the process exits. Do not
rely on that path after process termination.

With `cache=True`, the SDK uses the remote version identifier and local extended
attributes where supported. Explicit paths plus caching are especially
important in long-lived Pods and Plots.

### Upload

The destination's parent must exist:

```python
from pathlib import Path

from latch.ldata.path import LPath

destination_dir = LPath("latch:///results/run-001")
destination_dir.mkdirp()

report = destination_dir / "report.txt"
report.upload_from(Path("report.txt"))
```

`upload_from` accepts either a local file or directory. Avoid concurrent writes
to the same destination.

### Remote copy and delete

```python
from latch.ldata.path import LPath

source = LPath("latch:///results/run-001/report.txt")
backup = LPath("latch:///archive/run-001/report.txt")
source.copy_to(backup)
```

Deletion is recursive and destructive:

```python
target = LPath("latch:///scratch/run-001")
target.rmr()
```

Before `rmr()`:

1. Print or otherwise surface the exact resolved path.
2. Confirm it is not a workspace root, shared production folder, or active
   workflow output.
3. Obtain user confirmation unless deletion was already explicit.

## `LatchFile` and `LatchDir`

These types carry both a local execution path and an optional remote path:

```python
from pathlib import Path

from latch import small_task
from latch.types import LatchFile


@small_task
def summarize(input_file: LatchFile) -> LatchFile:
    source = Path(input_file.local_path)
    output = Path("/root/summary.txt")
    output.write_text(
        f"name={source.name}\nbytes={source.stat().st_size}\n",
        encoding="utf-8",
    )
    return LatchFile(str(output), "latch:///results/summary.txt")
```

For a passed input:

- `local_path` is the staged path on the task machine.
- `remote_path` identifies its source in Latch Data or S3.

For a returned value:

- The first constructor argument is the local file or directory.
- The second argument is the remote destination.

Use `LatchOutputFile` and `LatchOutputDir` in workflow signatures for
destinations that may not exist yet:

```python
from latch.types import LatchOutputDir, LatchOutputFile
```

### Directory behavior

Returning a local `LatchDir` to an existing remote directory adds or updates
the returned children. It does not imply deletion of unrelated remote files.
Do not depend on this merge behavior as a synchronization or cleanup strategy.

`LatchDir.iterdir()` lists children of a remote directory. For globbing local
task outputs into remote `LatchFile` values, use `file_glob`:

```python
from latch import small_task
from latch.types import LatchFile, file_glob


@small_task
def collect_fastq_outputs() -> list[LatchFile]:
    # Run the scientific tool here; it must create outputs/*.fastq.gz.
    return file_glob("outputs/*.fastq.gz", "latch:///results/fastq/")
```

## Data CLI

Inspect help for the installed version before scripting a command:

```bash
latch --version
latch cp --help
latch sync --help
```

Common operations:

```bash
# List
latch ls latch:///inputs

# Upload or download
latch cp ./sample.fastq.gz latch:///inputs/sample.fastq.gz
latch cp latch:///results/report.html ./report.html

# Create parents
latch mkdirp latch:///results/run-001

# Synchronize a local tree to a remote directory
latch sync ./results latch:///results/run-001

# Recursive removal — confirm the target first
latch rmr latch:///scratch/run-001
```

Prefer `mkdirp` and `rmr`; the older `mkdir`, `rm`, `touch`, and `open` commands
were deprecated.

## Reliability and Security

- Never print signed download URLs or authentication headers.
- Avoid loading a whole remote directory when only one file is needed.
- Use unique run destinations to prevent concurrent output collisions.
- Validate local checksums or scientific file integrity when correctness
  depends on complete transfer.
- Treat mounted cloud paths according to the source bucket's access policy.
- Keep workspace IDs explicit in automation that can access several workspaces.
- Do not call data mutations at module import time.

## Official Sources

- Remote files (`LPath`): https://wiki.latch.bio/workflows/sdk/api/working-with-files
- Legacy file support: https://wiki.latch.bio/workflows/sdk/python/legacy-file-support
- Latch URLs: https://wiki.latch.bio/workflows/sdk/python/latch-urls
- Data CLI: https://wiki.latch.bio/data/data-command-line
- Data overview: https://wiki.latch.bio/data/overview
- `LPath` source in the 2.76.8 release commit: https://github.com/latchbio/latch/blob/0faa9dcd8186444ac008f50adf95d43f0fa30e06/src/latch/ldata/path.py

### `references/latch-mcp.md`

# Latch MCP

Latch provides a remote Model Context Protocol server:

```text
https://mcp.latch.bio/mcp
```

It lets compatible AI clients discover workflows and interact with Latch Data
and executions through an OAuth-authorized tool surface.

## Authentication Boundary

- A Latch account is required.
- MCP uses OAuth in the connected AI client.
- MCP authorization does not authenticate the Latch SDK, CLI, or Console.
- SDK login credentials do not replace MCP authorization.
- Actions launched through MCP incur the same normal Latch charges as the
  corresponding Console or SDK action.

Never copy OAuth tokens between these authentication domains.

## Setup

### Cursor

Add:

```json
{
  "mcpServers": {
    "LatchBio": {
      "url": "https://mcp.latch.bio/mcp"
    }
  }
}
```

Then open **Cursor Settings → Tools & MCP(s)**, select LatchBio, click
**Connect**, and complete OAuth.

### Claude Code

```bash
claude mcp add --transport http latchbio https://mcp.latch.bio/mcp
```

Run `/mcp` and complete OAuth.

### Codex

```bash
codex mcp add latchbio --url https://mcp.latch.bio/mcp
codex mcp login latchbio
```

For another MCP client, configure the same remote HTTP URL and follow that
client's OAuth flow.

## Documented Tools

The current guide lists:

| Tool | Purpose |
|---|---|
| `list_files` | List immediate children of a Latch Data directory |
| `list_workspaces` | List accessible workspaces and the default |
| `list_workflows` | Discover workspace and public workflows |
| `get_workflow_schema` | Retrieve launch metadata and parameter schema |
| `launch_workflow` | Launch with schema-compatible values |
| `list_executions` | Filter executions by workspace, workflow, name, or status |
| `get_execution` | Get status, task nodes, result files, and Console URL |
| `get_task_logs` | Get inline logs or a signed URL for complete logs |

Tool names and schemas can evolve. Discover the connected server's current
tools before calling them.

## Safe Launch Workflow

1. **Select a workspace**
   - Call `list_workspaces`.
   - Prefer the default only when it is clearly the intended target.

2. **Discover rather than guess**
   - Call `list_workflows`.
   - Identify the exact workflow and version.

3. **Fetch the schema**
   - Call `get_workflow_schema`.
   - Use returned types, required values, enums, defaults, and path rules.

4. **Resolve data**
   - Use `list_files` only for the minimum directories needed.
   - It lists metadata, not file contents.
   - Do not browse unrelated or sensitive directories.

5. **Prepare a launch summary**
   - Workspace
   - Workflow and version
   - Input paths and parameters
   - Output destination
   - Expected resource/cost implications

6. **Confirm**
   - Obtain user approval before launching paid compute.
   - Reconfirm unusually large, GPU, or fan-out workloads.

7. **Launch**
   - Call `launch_workflow` once.
   - Preserve the returned execution identifier and Console URL.

8. **Monitor**
   - Poll with `get_execution`.
   - Use `get_task_logs` only for relevant nodes.
   - Avoid repeatedly downloading full logs when an inline excerpt is enough.

## Example Agent Plan

```text
list_workspaces
→ choose workspace 12345
→ list_workflows
→ choose Bulk RNA-seq version X
→ get_workflow_schema
→ validate sample paths and output directory
→ present launch summary and request confirmation
→ launch_workflow
→ get_execution until terminal status
→ get_task_logs only if a task fails
```

## Cost and Data Safety

- Listing resources is read-only; launching is not.
- Do not launch during exploratory discovery.
- Do not expose signed log URLs; they may grant temporary access.
- Do not paste secrets into workflow parameters.
- Confirm paths belong to the selected workspace.
- Avoid broad file listing when exact paths are already known.
- Stop polling after a terminal state.
- Scientific validation still requires inspecting outputs and method
  assumptions after orchestration succeeds.

## When MCP Is Unavailable

Use:

- Latch Console for interactive discovery and launch
- `latch_cli.services.launch.launch_v2` for Python automation
- `latch ls` or `LPath` for data inspection
- Latch Console for execution monitoring; `latch get-executions` remains in
  2.76.8 but is deprecated and scheduled for removal

Do not simulate a missing MCP tool by inventing undocumented HTTP endpoints.

## Official Source

- Latch MCP guide: https://wiki.latch.bio/agent/latch-mcp

### `references/nextflow-snakemake.md`

# Nextflow and Snakemake Integration

Latch supports Python, Nextflow, and Snakemake workflows, but their packaging
paths are not interchangeable. Confirm the SDK version and choose one track
before generating files.

## Nextflow: Documented SDK Wrapper Path

### Prerequisites

- A runnable Nextflow pipeline
- A `nextflow_schema.json`
- Containers or a documented execution profile for every process
- A pinned Latch SDK

Install:

```bash
uv pip install "latch==2.76.8"
```

### Generate metadata

```bash
latch generate-metadata nextflow_schema.json --nextflow
```

Current generation creates:

```text
latch_metadata/
├── __init__.py
└── generated.py
```

- `generated.py` is regenerated from the schema. Do not edit it.
- Put persistent custom metadata and flow changes in `latch_metadata/__init__.py`.
- Re-run generation after changing `nextflow_schema.json`.
- Review inferred file, enum, default, and required types before registration.

SDK 2.67.0 changed Nextflow generation to use one generated dataclass containing
all parameters and a generated base flow. Older `parameters.py` examples may no
longer match the generated layout.

### Register

The currently documented wrapper command is:

```bash
latch login
latch register . \
  --nf-script main.nf \
  --nf-execution-profile docker,test
```

Registration generates a Latch workflow wrapper and `latch.config`. The exact
entrypoint location depends on the generation path and SDK version.

Important:

- If a root `Dockerfile` exists, registration uses it.
- Otherwise Latch can generate a Dockerfile under `.latch/`.
- Passing `--nf-script` again can regenerate and overwrite wrapper code.
- After intentionally customizing a generated entrypoint, re-register without
  `--nf-script` to preserve it.
- Keep custom code in a separate module when possible.

### Generate an entrypoint explicitly

SDK 2.76.8 also exposes:

```bash
latch nextflow generate-entrypoint . \
  --nf-script main.nf \
  --execution-profile docker,test \
  --output wf/custom_entrypoint.py
```

This requires a valid `NextflowMetadata` object in the metadata root.

### Experimental Forch-only registration

The CLI also has:

```bash
latch nextflow register . --script-path main.nf
```

The official CLI guide marks this command **experimental** and only applicable
to Forch, Latch's architecture for running Nextflow in the user's own AWS
account. It is not a general alternative to `latch register --nf-script`.
Use it only for a configured Forch/BYOC project with current Latch guidance.

### Nextflow configuration rules

- Define every process container.
- Use profiles for environment-specific settings rather than editing the
  pipeline for Latch.
- Keep Latch's generated `latch.config` in the effective config chain.
- Use the official Latch shared-storage guidance for processes that need a
  common work directory.
- Configure private registries through Latch's supported credentials path.
- Follow the Latch GPU guide for process accelerators; do not translate Python
  task decorators into Nextflow resource syntax.
- Set `NextflowRuntimeResources.storage_gib` for the runtime/shared filesystem,
  not just final outputs.
- Understand storage-retention cost before increasing
  `storage_expiration_hours`.

### Debugging

```bash
latch register --staging .
latch develop .
latch nextflow attach --execution-id <execution-id>
```

Within `latch develop`, the production storage initializer is unavailable.
Follow the official debug-mode guidance: use the local executor, bypass the
initializer in debug mode, use a compatible Latch Nextflow base image, and
reduce process resources.

## Snakemake: Choose a Compatibility Track

The current docs and current stable package expose different Snakemake tracks.
Do not mix them.

### Track A: legacy flags in 2.76.8 source (documentation conflict)

The `2.76.8` wheel still exposes the `snakemake` extra, legacy metadata classes,
`generate-metadata --snakemake`, and `register --snakefile`. However, the
official CLI guide marks the Snakemake metadata and registration flags
deprecated and says metadata generation no longer works for
`latch >= 2.55.0.a6`.

Treat this as an unresolved source/documentation conflict. The commands below
are useful when maintaining a legacy project already known to use this path,
but should not be presented as a supported new-project flow without confirming
with current Latch documentation or support.

Use Python 3.11 for the broadest compatibility with the pinned Snakemake 7.x
dependency:

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install "latch[snakemake]==2.76.8"
```

Generate metadata from the workflow config:

```bash
latch generate-metadata config.yaml --snakemake
```

Register:

```bash
latch register . --snakefile Snakefile
```

Relevant options:

```bash
latch register . \
  --snakefile Snakefile \
  --metadata-root latch_metadata \
  --cache-tasks
```

Use the current `SnakemakeMetadata`, `SnakemakeParameter`, `FileMetadata`,
`EnvironmentConfig`, and `DockerMetadata` APIs from `latch.types.metadata`.
Inspect their signatures before generating hand-written metadata.

### Track B: official Snakemake v2 tutorial

The current Snakemake v2 tutorial is a compatibility-specific path. At the time
of this refresh, it explicitly requires:

```bash
uv venv --python 3.11
source .venv/bin/activate
uv pip install "latch==2.62.1a2"
```

It uses imports such as:

```python
from latch.types.metadata.snakemake_v2 import SnakemakeV2Metadata
```

and commands such as:

```bash
latch snakemake generate-entrypoint .
latch dockerfile --snakemake -c environment.yaml . -f
latch register -y .
```

Those v2 metadata modules and the `latch snakemake` command group are not
present in the stable 2.76.8 source tree. The tutorial's generated Dockerfile
also pins the workflow runtime separately to
`latch[snakemake]==2.55.0.a6`.

Therefore:

- Re-check the official tutorial's exact pin before starting.
- Use an isolated environment.
- Preserve and review both the local CLI pin and generated runtime pin.
- Do not upgrade that environment to stable 2.76.8 without a migration plan.
- Do not copy v2 imports into a stable-track project.
- Treat the alpha pin as pre-release software and validate end to end.

### Snakemake resource and environment rules

- Give every rule CPU and memory resources or define safe defaults in
  `profiles/default/config.yaml`.
- Pin Conda and container environments.
- Keep the Latch executor/storage plugin configuration from the chosen track.
- Use `LatchOutputDir` for output destinations exposed in the form.
- Avoid embedding credentials in `environment.yaml`, Dockerfiles, profiles, or
  generated metadata.

## Generated-File Discipline

Before editing a generated file:

1. Find the command and source file that generated it.
2. Determine whether regeneration overwrites the file.
3. Prefer the documented extension file.
4. If customization of generated code is unavoidable, record the generation
   command and stop passing flags that regenerate it.
5. Diff generated output after every SDK upgrade.

## Release Checklist

- SDK and pipeline-engine versions are pinned.
- Schema/config and generated metadata are in sync.
- Every parameter has the expected type and default.
- Containers and package environments are immutable enough to reproduce.
- Small test data succeeds.
- Resume/cache behavior has been exercised.
- Shared storage has enough capacity and an intentional retention period.
- Result paths and execution reports appear in the Console.
- A clean registration from a fresh checkout works.

## Official Sources

- Nextflow tutorial: https://wiki.latch.bio/workflows/sdk/nextflow/tutorial
- Nextflow overview: https://wiki.latch.bio/workflows/sdk/nextflow/overview
- Nextflow dependencies: https://wiki.latch.bio/workflows/sdk/nextflow/dependencies
- Nextflow profiles: https://wiki.latch.bio/workflows/sdk/nextflow/profiles
- Nextflow GPU guide: https://wiki.latch.bio/workflows/sdk/nextflow/gpus
- Nextflow shared storage: https://wiki.latch.bio/workflows/sdk/nextflow/shared-storage
- Snakemake v2 tutorial: https://wiki.latch.bio/workflows/sdk/snakemake-v2/tutorial
- Snakemake v2 overview: https://wiki.latch.bio/workflows/sdk/snakemake-v2/overview
- CLI source in the 2.76.8 release commit: https://github.com/latchbio/latch/blob/0faa9dcd8186444ac008f50adf95d43f0fa30e06/src/latch_cli/main.py
- Changelog in the 2.76.8 release commit: https://github.com/latchbio/latch/blob/0faa9dcd8186444ac008f50adf95d43f0fa30e06/CHANGELOG.md

### `references/operations-and-debugging.md`

# Operations, Registration, Debugging, and Execution

This reference targets the current stable CLI and SDK (`latch==2.76.8`).

## Authenticate and Select a Workspace

```bash
latch login
latch workspace
```

Select a known workspace by numeric ID:

```bash
latch workspace --id 12345
```

The active workspace controls unqualified `latch:///` paths, Registry access,
workflow registration, and programmatic execution. Surface it before a
destructive or costly action.

Do not read or print `~/.latch/token`. Use the CLI's supported login and token
handling.

## Registration

Basic remote registration:

```bash
latch register --yes --open .
```

Remote builds are the default:

```bash
latch register --remote .
```

Use a local Docker build only when intentional:

```bash
latch register --no-remote .
```

Important options:

```bash
# Register into another workspace
latch register --workspace-id 12345 .

# Mark the version as a release
latch register --mark-as-release .

# Register workflows from a non-default Python module
latch register --workflow-module wf.custom_entrypoint .

# Use a specific Dockerfile
latch register --dockerfile Dockerfile.release .

# Plain build output for CI logs
latch register --docker-progress plain .
```

### Version behavior

Registration combines the project `version` with automatic content/version
information unless disabled. Do not disable automatic versioning merely to
force an overwrite.

A duplicate workflow registration exits with status `2`. CI should distinguish
that from status `1`, which indicates registration failure.

### Release behavior

Before `--mark-as-release`:

- Pin SDK, Python, system, and scientific dependencies.
- Record tool and database versions.
- Run a representative launch plan.
- Confirm result links and metadata.
- Verify the source commit is clean and reproducible.

## Staging and Development Shell

Build an image without publishing a workflow version:

```bash
latch register --staging .
```

Open a remote interactive shell in that image:

```bash
latch develop .
```

Choose a development instance:

```bash
latch develop . --instance-size small_gpu_task
```

Use `latch develop --help` to inspect the installed version's supported sizes.

### Sync behavior

- Local files under the workflow root are synced into the container.
- Files outside that root are not synced.
- Local updates overwrite corresponding container files.
- Local deletions do not remove existing container files.
- Container-side edits are not synced back and can be overwritten.
- `.gitignore` and `.dockerignore` are respected.
- Re-run staging registration after changing the Dockerfile or dependencies.

Place small test fixtures under the project root and exclude private or large
data from registration archives.

## Debug a Running Task

Open an interactive shell for an execution or task:

```bash
latch exec --execution-id <execution-id>
```

For a Nextflow work directory:

```bash
latch nextflow attach --execution-id <execution-id>
```

Use interactive access for diagnosis, not for modifying the source of record.
Reproduce and fix the issue locally, then register a new version.

## Programmatic Execution

The old `latch launch` CLI is deprecated. Use
`latch_cli.services.launch.launch_v2`.

### Launch with Python parameters

```python
import asyncio

from latch.types import LatchFile
from latch_cli.services.launch.launch_v2 import launch

execution = launch(
    wf_name="my_workflow",
    version="1.2.3-abcd12",
    params={
        "reads": LatchFile("latch:///test-data/reads.fastq.gz"),
        "minimum_quality": 20,
    },
)

completed = asyncio.run(execution.wait())
if completed is None:
    raise RuntimeError("execution polling ended without a result")
if completed.status != "SUCCEEDED":
    raise RuntimeError(
        f"execution {completed.id} ended with {completed.status}"
    )

print(completed.output)
print([path.path for path in completed.ingress_data])
```

`wf_name` is the registered workflow name (check `.latch/workflow_name` or the
Console), not the human-readable metadata display name.

`launch` defaults `best_effort=True`, allowing compatible dictionaries,
dataclasses, strings for enum values, and other schema-guided conversions.
Set `best_effort=False` only when the caller imports exactly the same Python
types as the registered workflow.

Compatibility:

- Programmatic launch requires workflows registered with SDK 2.62.0+.
- Typed output decoding requires workflows registered with SDK 2.65.1+.
- Python versions and imported classes must remain compatible for strict
  serialized type decoding.

### Launch a registered launch plan

```python
import asyncio

from latch_cli.services.launch.launch_v2 import launch_from_launch_plan

execution = launch_from_launch_plan(
    wf_name="my_workflow",
    version="1.2.3-abcd12",
    lp_name="Small public example",
)

completed = asyncio.run(execution.wait())
if completed is None or completed.status != "SUCCEEDED":
    raise RuntimeError("launch-plan execution did not succeed")
```

### Poll or abort

`Execution` exposes:

- `id`
- `status`
- `poll()`
- async `wait()`
- `abort()`

Abort only the intended active execution:

```python
if execution.status not in {"SUCCEEDED", "FAILED", "ABORTED"}:
    execution.abort()
```

## Interactive Execution Through MCP

When Latch MCP is available:

1. List workspaces.
2. List workflows.
3. Fetch the selected workflow schema.
4. Validate parameters.
5. Obtain confirmation for paid compute.
6. Launch.
7. Poll execution state.
8. Fetch task logs only for relevant failed or running nodes.

MCP authorization is separate from SDK login. See
`references/latch-mcp.md`.

## Monitoring

Console execution monitoring provides:

- Overall execution status
- Graph and task-node status
- Inputs and outputs
- Logs
- Provenance and result files
- Resource monitoring

The 2.76.8 CLI still provides the following deprecated command:

```bash
latch get-executions
```

The official CLI guide says it will be removed in a future version. Prefer the
Console or Latch MCP for new monitoring integrations.

For every production workflow, emit:

- Concise `message()` calls for actionable warnings and errors
- Result links for high-value outputs
- Normal structured logs for detailed diagnostics

Do not log secrets or signed URLs.

## Troubleshooting

### Authentication failure

```bash
latch login
latch workspace
```

Confirm the workspace is the one containing the data, workflow, and Registry
objects. Do not attempt to repair authentication by modifying token files.

### Registration cannot find the workflow

- Confirm the workflow root and `wf` package.
- Check `--workflow-module`.
- Compile the Python package.
- Verify metadata imports do not perform network calls.
- Inspect task-specific Dockerfile arguments; they must be string literals.

### Build failure

- Reproduce through staging registration.
- Use `--docker-progress plain`.
- Check `.dockerignore` did not omit required files.
- Confirm system packages and architecture.
- Use `--no-remote` only when the local Docker environment is known-good.

### Runtime import or executable failure

- Enter `latch develop`.
- Check `which python3`, installed packages, `$PATH`, and executable permissions.
- Run the task-level test script inside the image.
- Rebuild staging after dependency changes.

### Out of memory or storage

- Inspect resource monitoring.
- Measure peak rather than average use.
- Adjust one resource dimension at a time.
- See `references/resource-configuration.md`.

### Programmatic launch type error

- Fetch the workflow's current schema/version.
- Verify every required parameter.
- Use `best_effort=True` for compatible external representations.
- Re-register old workflows with a current SDK when typed outputs are needed.

## Official Sources

- CLI commands: https://wiki.latch.bio/workflows/sdk/cli/commands
- Development and debugging: https://wiki.latch.bio/workflows/sdk/testing-and-debugging-a-workflow/development-and-debugging
- Programmatic execution: https://wiki.latch.bio/workflows/sdk/testing-and-debugging-a-workflow/programmatic-execution
- Execution monitoring: https://wiki.latch.bio/workflows/sdk/console/execution-monitoring
- Resource monitoring: https://wiki.latch.bio/workflows/sdk/console/resource-monitoring
- Versioning: https://wiki.latch.bio/workflows/sdk/console/versioning
- CLI source in the 2.76.8 release commit: https://github.com/latchbio/latch/blob/0faa9dcd8186444ac008f50adf95d43f0fa30e06/src/latch_cli/main.py

### `references/registry.md`

# Latch Registry SDK

The current Registry API is object- and transaction-based. Older examples that
call `Project.create`, `Table.create`, `Record.create`, `Record.list`,
`record.update`, or `record.delete` do not match the current SDK.

This reference targets `latch==2.76.8`.

## Object Model

```text
Account (workspace)
└── Project
    └── Table
        └── Record
```

Current classes:

```python
from latch.account import Account
from latch.registry.project import Project
from latch.registry.record import Record
from latch.registry.table import Table
```

Objects are identified by numeric-string IDs. Display names are not globally
unique and must not be used as stable identifiers.

## Read Projects and Tables

```python
from latch.account import Account

account = Account.current()

for project in account.list_registry_projects():
    print(project.id, project.get_display_name())

    for table in project.list_tables():
        print("  ", table.id, table.get_display_name())
```

Most getters lazily call `load()` and cache the result. Use `load()` explicitly
when another process may have changed an object and fresh state is required.

Permissions are evaluated in the active CLI workspace or the workspace running
the task.

## Read Records

`Table.list_records()` is paginated and yields dictionaries keyed by record ID:

```python
from latch.registry.table import Table

table = Table(id="12345")

for page in table.list_records(page_size=100):
    for record_id, record in page.items():
        print(
            record_id,
            record.get_name(),
            record.get_values(),
            record.get_creation_time(),
            record.get_last_updated(),
        )
```

Record names are unique only within their table. Use `record.id` when a global
identifier is required.

To load one known record:

```python
from latch.registry.record import Record

record = Record(id="67890")
values = record.get_values()
table_id = record.get_table_id()
```

## DataFrames

`Table.get_dataframe()` requires the pandas extra:

```bash
uv pip install "latch[pandas]==2.76.8"
```

```python
frame = Table(id="12345").get_dataframe()
```

Use `list_records()` when streaming or dependency minimization matters.

## Transactional Updates

Updates are queued in a context manager and committed atomically when the
context exits successfully.

### Create a project

```python
from latch.account import Account

account = Account.current()
with account.update() as update:
    update.upsert_registry_project("RNA-seq Studies")
```

Despite the method name, creating projects and tables is not idempotent: two
calls with the same display name create two objects.

### Create a table

```python
from latch.registry.project import Project

project = Project(id="123")
with project.update() as update:
    update.upsert_table("Samples")
```

### Add columns and records

```python
from latch.registry.table import Table
from latch.types import LatchFile

table = Table(id="456")

with table.update() as update:
    update.upsert_column("condition", str, required=True)
    update.upsert_column("replicate", int)
    update.upsert_column("reads", LatchFile)

with table.update() as update:
    update.upsert_record(
        "sample-001",
        condition="treated",
        replicate=1,
        reads=LatchFile("latch:///inputs/sample-001.fastq.gz"),
    )
```

`upsert_record` takes the record name followed by column values as keyword
arguments. Unknown columns raise an error.

Supported column types include strings, integers, floats, dates, datetimes,
Booleans, `LatchFile`, `LatchDir`, enums, linked records, and selected list
forms. Check `TableUpdate.upsert_column` in the installed SDK before using a
less common nested type.

`TableUpdate.upsert_record` accepts `LPath` values in SDK 2.67.22 and later:

```python
from latch.ldata.path import LPath

with table.update() as update:
    update.upsert_record(
        "sample-002",
        reads=LPath("latch:///inputs/sample-002.fastq.gz"),
    )
```

### Delete

Deletion is queued through the corresponding updater:

```python
with table.update() as update:
    update.delete_record("sample-001")

with project.update() as update:
    update.delete_table("456")

with account.update() as update:
    update.delete_registry_project("123")
```

Record deletion takes a record **name**. Table and project deletion take IDs.
Confirm destructive operations and the active workspace first.

## Registry Samplesheets in Workflow Forms

`SamplesheetItem` preserves the source Registry record when a user imports rows
into a workflow form.

```python
from dataclasses import dataclass

from latch import small_task, workflow
from latch.registry.table import Table
from latch.types import LatchFile
from latch.types.metadata import (
    LatchAuthor,
    LatchMetadata,
    LatchParameter,
)
from latch.types.samplesheet_item import SamplesheetItem


@dataclass
class SampleRow:
    sample_name: str
    reads: LatchFile
    qc_status: str


metadata = LatchMetadata(
    display_name="Registry-aware QC",
    author=LatchAuthor(name="Workflow Team"),
    parameters={
        "samples": LatchParameter(
            display_name="Samples",
            samplesheet=True,
        )
    },
)


@small_task
def process_samples(samples: list[SamplesheetItem[SampleRow]]) -> int:
    updated = 0

    for item in samples:
        if item.record is None:
            continue

        table = Table(id=item.record.get_table_id())
        with table.update() as update:
            update.upsert_record(
                item.record.get_name(),
                qc_status="complete",
            )
        updated += 1

    return updated


@workflow(metadata)
def registry_qc(samples: list[SamplesheetItem[SampleRow]]) -> int:
    return process_samples(samples=samples)
```

Important behavior:

- `item.data` is the typed dataclass value.
- `item.record` is a `Record` when imported from Registry.
- `item.record` is `None` for a manually entered row.
- Dataclass fields should match Registry column keys where possible.
- The target table must already contain columns written by the task.
- Restrict selectable tables with `LatchParameter.allowed_tables` when the
  workflow should not accept arbitrary Registry schemas.

## Consistency and Error Handling

- Call `load()` again after out-of-band changes.
- Treat `NotFoundError` variants as either absent objects or missing permission.
- Do not infer IDs by choosing the first matching display name.
- Keep transactions focused; a failure prevents the context's commit.
- Avoid one transaction per row when a single updater can batch many changes.
- Validate all paths and types before queuing a large update.
- Record provenance fields rather than overwriting source metadata.

## Official Sources

- Registry SDK overview: https://wiki.latch.bio/registry/sdk/latch-sdk-registry-integration
- Account objects: https://wiki.latch.bio/registry/sdk/account-objects
- Project objects: https://wiki.latch.bio/registry/sdk/registry-projects
- Table objects: https://wiki.latch.bio/registry/sdk/table-objects
- Record objects: https://wiki.latch.bio/registry/sdk/record-objects
- Workflow Registry tutorial: https://wiki.latch.bio/workflows/sdk/api/registry-usage-tutorial
- Registry source in the 2.76.8 release commit: https://github.com/latchbio/latch/tree/0faa9dcd8186444ac008f50adf95d43f0fa30e06/src/latch/registry

### `references/resource-configuration.md`

# Task Resource Configuration

This reference targets `latch==2.76.8`. Resource shapes are operational
configuration and can change independently of examples. Inspect the installed
SDK before making cost or capacity guarantees.

## Selection Strategy

1. Start with the smallest named decorator that can run the task.
2. Measure CPU, peak RSS, temporary storage, wall time, and GPU utilization.
3. Move to a larger named decorator only when evidence justifies it.
4. Use `custom_task` for CPU-only shapes not represented by a named decorator.
5. Use a named GPU decorator; `custom_task` does not accept `gpu` or
   `gpu_type` arguments.
6. Re-measure with representative scientific data before release.

## Named CPU Decorators

```python
from latch.resources.tasks import large_task, medium_task, small_task


@small_task
def parse_manifest():
    ...


@medium_task
def align_reads():
    ...


@large_task
def assemble_genome():
    ...
```

SDK 2.76.8 configures these scheduler requests:

| Decorator | CPU | RAM | Ephemeral storage |
|---|---:|---:|---:|
| `small_task` | 2 | 4 GiB | 100 GiB |
| `medium_task` | 30 | 100 GiB | 1500 GiB |
| `large_task` | 90 | 170 GiB | 4500 GiB |

The public guide may display nominal instance capacities rather than the
schedulable requests encoded in the package. The installed package determines
what registration serializes.

## Named GPU Decorators

Generic GPU shapes:

```python
from latch.resources.tasks import large_gpu_task, small_gpu_task
```

| Decorator | CPU | RAM | GPU |
|---|---:|---:|---|
| `small_gpu_task` | 7 | 30 GiB | 1× T4-class |
| `large_gpu_task` | 63 | 245 GiB | 1× A10G-class |

V100 shapes:

```python
from latch.resources.tasks import (
    v100_x1_task,
    v100_x4_task,
    v100_x8_task,
)
```

L40S shapes:

```python
from latch.resources.tasks import (
    g6e_xlarge_task,
    g6e_2xlarge_task,
    g6e_4xlarge_task,
    g6e_8xlarge_task,
    g6e_12xlarge_task,
    g6e_16xlarge_task,
    g6e_24xlarge_task,
    g6e_48xlarge_task,
)
```

Current L40S scheduler requests and limits:

| Decorator | Request CPU | Request RAM | Limit CPU | Limit RAM | GPUs |
|---|---:|---:|---:|---:|---:|
| `g6e_xlarge_task` | 2 | 28 GiB | 4 | 32 GiB | 1 |
| `g6e_2xlarge_task` | 6 | 57 GiB | 8 | 64 GiB | 1 |
| `g6e_4xlarge_task` | 14 | 115 GiB | 16 | 128 GiB | 1 |
| `g6e_8xlarge_task` | 30 | 230 GiB | 32 | 256 GiB | 1 |
| `g6e_12xlarge_task` | 46 | 345 GiB | 48 | 384 GiB | 4 |
| `g6e_16xlarge_task` | 62 | 460 GiB | 64 | 512 GiB | 1 |
| `g6e_24xlarge_task` | 94 | 691 GiB | 96 | 768 GiB | 4 |
| `g6e_48xlarge_task` | 190 | 1382 GiB | 192 | 1536 GiB | 8 |

GPU availability, quotas, and platform mapping can change. Confirm in the
current docs or with Latch support before promising a specific model to users.

## Custom CPU, Memory, and Storage

Exact stable signature:

```python
custom_task(
    cpu,
    memory,
    *,
    storage_gib=500,
    timeout=0,
    **task_options,
)
```

Example:

```python
from datetime import timedelta

from latch import custom_task


@custom_task(
    cpu=12,
    memory=48,
    storage_gib=750,
    timeout=timedelta(hours=6),
    retries=1,
)
def call_variants():
    ...
```

In SDK 2.76.8, `custom_task` accepts up to 126 CPU cores, 975 GiB RAM, and
4949 GiB ephemeral storage. Not every arbitrary combination fits a schedulable
node group; the decorator selects the smallest configured group that satisfies
all three requests.

`custom_memory_optimized_task` is deprecated. Use `custom_task`.

## Dynamic Resources

Each `cpu`, `memory`, or `storage_gib` argument may be a function of task
inputs. The resource function's annotated parameters must exist in the task
with exactly matching annotations.

```python
from latch import custom_task
from latch.types import LatchFile


def allocate_cpu(files: list[LatchFile]) -> int:
    return min(32, max(2, len(files) * 2))


def allocate_storage(files: list[LatchFile]) -> int:
    sizes = [file.size() for file in files]
    if any(size is None for size in sizes):
        raise ValueError("unable to determine every input size")
    total_bytes = sum(int(size) for size in sizes)
    estimated_gib = total_bytes / (1024**3)
    return max(100, int(estimated_gib * 2) + 1)


@custom_task(
    cpu=allocate_cpu,
    memory=64,
    storage_gib=allocate_storage,
)
def merge_files(files: list[LatchFile]) -> LatchFile:
    ...
```

Dynamic functions execute at runtime before the task launches.

Guardrails:

- Return integers.
- Bound every computed resource.
- Include overhead for decompression and intermediate files.
- Keep computation deterministic and fast.
- Do not make network calls or retrieve secrets from resource functions.
- Test the exact annotation matching during staging registration.

## Cache, Retries, and Timeout

Named decorators and non-dynamic `custom_task` accept Flyte task options:

```python
@medium_task(
    cache=True,
    cache_version="aligner-2.1-reference-v4",
    retries=2,
    timeout=7200,
)
def align_reads():
    ...
```

- Cache deterministic outputs only.
- Include tool, reference, and behavior changes in `cache_version`.
- Use retries for transient infrastructure or network errors.
- Do not retry deterministic invalid-input failures.
- A timeout can be seconds or `datetime.timedelta`.

## Temporary and Persistent Storage

Ephemeral task storage is deleted with the task environment. Use it for:

- Decompressed inputs
- Tool work directories
- Sort spills
- Intermediate indexes

Return a `LatchFile` or `LatchDir`, or upload through `LPath`, for persistent
outputs. Never assume `/tmp` or `/root` survives task completion.

Estimate storage from peak simultaneous intermediates, not final output size:

```text
requested storage
  >= staged inputs
   + decompressed expansion
   + peak tool intermediates
   + final outputs
   + safety margin
```

## Cost and Launch Safety

- Surface the chosen resource class before registration or launch.
- Obtain confirmation before starting large or GPU-backed executions.
- Prefer a representative small launch plan for validation.
- Parallelism multiplies cost; map width matters as much as per-task size.
- Cache hits can reduce cost but are not a substitute for reproducible inputs.
- Compare resource monitoring against scientific throughput, not utilization
  alone.

## Troubleshooting

### Out of memory

- Check peak RSS, not average memory.
- Identify whether an algorithm scales with records, bases, or samples.
- Increase memory only after ruling out unbounded accumulation.

### Out of storage

- Inspect hidden tool caches and decompressed inputs.
- Clean intermediates within the task when safe.
- Increase `storage_gib` based on peak use.

### CPU under-utilization

- Confirm the scientific tool received its thread/process flag.
- Avoid requesting more cores than the tool can use.
- Check I/O and memory bandwidth before scaling CPU.

### GPU under-utilization

- Verify the tool was built with the expected CUDA support.
- Check batch size, data loading, and CPU preprocessing.
- Avoid multi-GPU shapes unless the application implements distributed work.

## Official Sources

- Resource guide: https://wiki.latch.bio/workflows/sdk/python/defining-cloud-resources
- Resource monitoring: https://wiki.latch.bio/workflows/sdk/console/resource-monitoring
- Task source in the 2.76.8 release commit: https://github.com/latchbio/latch/blob/0faa9dcd8186444ac008f50adf95d43f0fa30e06/src/latch/resources/tasks.py
- Changelog in the 2.76.8 release commit: https://github.com/latchbio/latch/blob/0faa9dcd8186444ac008f50adf95d43f0fa30e06/CHANGELOG.md

### `references/ui-and-automation.md`

# Workflow UI, Launch Plans, Messages, Results, and Automations

The workflow signature defines types. `LatchMetadata` defines how users
understand and enter those values. Treat interface design as part of workflow
correctness.

## Metadata

```python
from latch.types.metadata import (
    LatchAuthor,
    LatchMetadata,
    LatchParameter,
    LatchRule,
    Params,
    Section,
    Spoiler,
    Text,
)

metadata = LatchMetadata(
    display_name="Bulk RNA-seq QC",
    author=LatchAuthor(
        name="Workflow Team",
        github="https://github.com/example",
    ),
    documentation="https://example.org/docs/rnaseq-qc",
    repository="https://github.com/example/rnaseq-qc",
    license="MIT",
    tags=["RNA-seq", "QC"],
    parameters={
        "reads": LatchParameter(
            display_name="Reads",
            description="FASTQ input files.",
            samplesheet=True,
        ),
        "minimum_quality": LatchParameter(
            display_name="Minimum quality",
            description="Minimum accepted Phred score.",
            rules=[
                LatchRule(
                    regex=r"^(?:[0-9]|[1-3][0-9]|40)$",
                    message="Choose an integer from 0 through 40.",
                )
            ],
        ),
        "output_directory": LatchParameter(
            display_name="Output directory",
            description="Destination for reports and processed outputs.",
            output=True,
        ),
    },
    flow=[
        Section(
            "Inputs",
            Text("Select samples and input reads."),
            Params("reads"),
        ),
        Spoiler(
            "Advanced quality settings",
            Params("minimum_quality"),
        ),
        Section(
            "Outputs",
            Params("output_directory"),
        ),
    ],
)
```

Apply it:

```python
from dataclasses import dataclass
from pathlib import Path

from latch import small_task, workflow
from latch.types import LatchDir, LatchFile, LatchOutputDir


@dataclass
class SampleRow:
    sample_name: str
    reads: LatchFile


@small_task
def run_qc(
    reads: list[SampleRow],
    output_directory: LatchOutputDir,
    minimum_quality: int,
) -> LatchDir:
    local_output = Path("/root/rnaseq-qc")
    local_output.mkdir(parents=True, exist_ok=True)
    (local_output / "summary.txt").write_text(
        f"samples={len(reads)}\nminimum_quality={minimum_quality}\n",
        encoding="utf-8",
    )

    remote = output_directory.remote_path
    if remote is None:
        raise ValueError("output_directory must have a remote path")
    return LatchDir(str(local_output), remote)


@workflow(metadata)
def rnaseq_qc(
    reads: list[SampleRow],
    output_directory: LatchOutputDir,
    minimum_quality: int = 20,
) -> LatchDir:
    return run_qc(
        reads=reads,
        output_directory=output_directory,
        minimum_quality=minimum_quality,
    )
```

Metadata parameter keys must match the signature. The SDK adds default metadata
for signature parameters omitted from the metadata object.

Although `about_page_path` is documented, SDK 2.76.8 can fail while serializing
its `Path` value. Prefer `documentation=` and a descriptive workflow docstring
until that defect is fixed.

## Flow Elements

Current flow classes include:

- `Section(title, *children)`
- `Text(markdown)`
- `Title(markdown_title)`
- `Params(*parameter_names)`
- `Spoiler(title, *children)`
- `Fork(parameter_name, display_name, **branches)`
- `ForkBranch(display_name, *children)`

`flow` replaces the default top-to-bottom layout. Include every visible
parameter intentionally.

Use a `Fork` only with a matching string parameter in the workflow signature:

```python
from latch.types.metadata import Fork, ForkBranch, Params

read_type_flow = Fork(
    "read_type",
    "Read layout",
    paired=ForkBranch("Paired-end", Params("read1", "read2")),
    single=ForkBranch("Single-end", Params("read1")),
)
```

## Parameter Guidance

Use:

- `display_name` and `description` for scientific meaning
- `rules` for syntactic validation
- `hidden` for rarely changed values, not security
- `batch_table_column` for high-value bulk-run fields
- `samplesheet=True` for dataclass-backed tabular inputs
- `allowed_tables` to restrict Registry imports
- `output=True` or `LatchOutputFile` / `LatchOutputDir` for new destinations

Do not use form defaults to hide scientific assumptions. State reference
genome, strandedness, units, and algorithm defaults explicitly.

## Launch Plans

`LaunchPlan` creates a named set of defaults shown under Test Data in the
Console:

```python
from latch.resources.launch_plan import LaunchPlan
from latch.types import LatchFile, LatchOutputDir

LaunchPlan(
    rnaseq_qc,
    "Small public example",
    {
        "reads": [
            SampleRow(
                sample_name="example",
                reads=LatchFile("latch:///test-data/example.fastq.gz"),
            )
        ],
        "minimum_quality": 20,
        "output_directory": LatchOutputDir(
            "latch:///test-results/rnaseq-qc"
        ),
    },
    description="Small input for interface and integration testing.",
)
```

Constructor:

```python
LaunchPlan(
    workflow,
    name,
    default_params,
    *,
    description=None,
)
```

Rules:

- Define launch plans at module scope so registration discovers them.
- Parameter keys and values must match the workflow.
- A launch plan name cannot contain `.`.
- Use small public or workspace-safe test data.
- Avoid destinations shared by concurrent users.
- Never put secret values in a launch plan.

## Execution Messages

Use messages for concise user-facing signals, not raw logs:

```python
from latch import message, small_task


@small_task
def validate_columns(columns: list[str]) -> bool:
    required = {"sample_id", "condition"}
    missing = sorted(required.difference(columns))

    if missing:
        message(
            typ="error",
            data={
                "title": "Missing required columns",
                "body": ", ".join(missing),
            },
        )
        raise ValueError(f"missing columns: {missing}")

    message(
        typ="info",
        data={
            "title": "Input validated",
            "body": "Required sample columns are present.",
        },
    )
    return True
```

Valid message types are `info`, `warning`, and `error`. The data dictionary
requires `title` and `body`.

Do not put secrets, signed URLs, patient identifiers, or excessive raw data in
messages.

## Results Page

Publish the most useful result locations:

```python
from latch import small_task
from latch.executions import add_execution_results
from latch.types import LatchOutputDir


@small_task
def publish_results(output_directory: LatchOutputDir) -> None:
    remote = output_directory.remote_path
    if remote is None:
        raise ValueError("output directory must have a remote path")

    add_execution_results(
        [
            remote,
            f"{remote.rstrip('/')}/multiqc_report.html",
        ]
    )
```

For Nextflow parameters, `NextflowParameter.results_paths` can publish selected
subpaths under an output directory.

Result links improve discoverability; they do not upload missing outputs or
verify scientific validity.

## Automations

Automations are configured in the Console and can trigger from:

- A child added at any depth beneath a watched Latch Data directory
- A recurring time interval

### Data-added workflow contract

The automation workflow must have exactly one parameter:

```python
from latch import small_task, workflow
from latch.types import LatchDir


@small_task
def process_new_data(input_directory: LatchDir) -> None:
    children = list(input_directory.iterdir())
    print(f"observed {len(children)} children")


@workflow
def automation_workflow(input_directory: LatchDir) -> None:
    process_new_data(input_directory=input_directory)
```

The trigger fires after the configured follow-up update period following the
last addition. Modification or deletion alone does not trigger it.

### Interval workflow contract

The workflow must have no parameters:

```python
from latch import small_task, workflow


@small_task
def run_scheduled_check() -> None:
    print("scheduled check started")


@workflow
def scheduled_workflow() -> None:
    run_scheduled_check()
```

### Automation safety

- Automations can create recurring paid compute. Review frequency, map width,
  and worst-case cost before activation.
- Make processing idempotent. A Registry record or durable marker can prevent
  duplicate work.
- Do not hard-code secrets. Retrieve them inside tasks with `get_secret()`.
- Test the workflow manually before enabling the trigger.
- Start with a long enough debounce/update period to avoid launch storms.
- Disable the automation while changing its workflow contract.
- Ensure the watched directory does not include the automation's own outputs.

## Official Sources

- UI definition: https://wiki.latch.bio/workflows/sdk/ui/latch-metadata
- Launch plans: https://wiki.latch.bio/workflows/sdk/ui/launch-plans
- Messages: https://wiki.latch.bio/workflows/sdk/ui/messages
- Results: https://wiki.latch.bio/workflows/sdk/ui/results
- Automation overview: https://wiki.latch.bio/workflows/sdk/automation/overview
- Data-added trigger: https://wiki.latch.bio/workflows/sdk/automation/example-data-addition
- Interval trigger: https://wiki.latch.bio/workflows/sdk/automation/example-interval

### `references/verified-workflows.md`

# Ready-to-Use and Referenced Workflows

Latch exposes ready-to-run workflows in two distinct ways:

1. The Latch Console and Latch MCP expose a broad catalog, including workflows
   such as AlphaFold, CRISPResso2, Bulk RNA-seq, and others.
2. The `latch.verified` Python package exports a small set of typed reference
   launch plans that can be composed into a custom SDK workflow.

Do not assume every Console workflow has a Python import.

## Current `latch.verified` Exports

In `latch==2.76.8`, `latch.verified` exports:

```python
from latch.verified import (
    deseq2_wf,
    gene_ontology_pathway_analysis,
    mafft,
    rnaseq,
    trim_galore,
)
```

The package does **not** currently export:

- `alphafold`
- `colabfold`
- `bulk_rnaseq`
- `pathway_enrichment`
- `scvelo`
- `emptydrops`
- `crispresso2`
- `phylogenetics`
- `list_workflows`

Those names appeared in older generated examples but are not public exports in
the current SDK.

## Inspect Before Composing

Reference wrappers expose typed interfaces and internally pin a registered
workflow name and version. From the skill root, inspect exports and parameter
types:

```bash
uv run --no-project --python 3.12 --with "latch==2.76.8" \
  python scripts/inspect_latch_sdk.py
```

Or from the repository root:

```bash
uv run --no-project --python 3.12 --with "latch==2.76.8" \
  python skills/latchbio-integration/scripts/inspect_latch_sdk.py
```

Do not add a made-up `workflow_version=` argument. The wrapper's
`@reference_launch_plan` declaration controls its version.
Read the installed wrapper module when exact default values are needed.

## Compose MAFFT

```python
from latch import workflow
from latch.types import LatchFile, LatchOutputDir
from latch.verified import mafft
from latch.verified.mafft import AlignmentMode


@workflow
def multiple_sequence_alignment(
    unaligned_sequences: LatchFile,
    output_directory: LatchOutputDir,
) -> LatchFile:
    return mafft(
        output_directory=output_directory,
        unaligned_seqs=unaligned_sequences,
        alignment_mode=AlignmentMode.auto,
        gap_penalty=1.53,
        offset=0.0,
        maxiterate=0,
        output_file="aligned_mafft.fa",
    )
```

## Compose Pathway Analysis

```python
from latch import workflow
from latch.types import LatchDir, LatchFile, LatchOutputDir
from latch.verified import gene_ontology_pathway_analysis


@workflow
def pathway_report(
    contrast_csv: LatchFile,
    report_name: str,
    output_directory: LatchOutputDir,
) -> LatchDir:
    return gene_ontology_pathway_analysis(
        contrast_csv=contrast_csv,
        report_name=report_name,
        number_of_pathways=20,
        output_location=output_directory,
    )
```

## Other Typed Wrappers

### DESeq2

Import `deseq2_wf`. Its current interface supports single or multiple raw count
tables, manual conditions or a conditions table, a structured design formula,
plot count, and an optional output directory. Inspect the signature rather than
copying simplified examples that use nonexistent `count_matrix` or
`sample_metadata` parameters.

### RNA-seq

Import `rnaseq` plus its current types from `latch.verified.rnaseq`, including:

- `Sample`
- `SingleEndReads`
- `PairedEndReads`
- `Strandedness`
- `LatchGenome`
- `AlignmentTools`

The wrapper has several fork-selector parameters and is not interchangeable
with a hypothetical `bulk_rnaseq(fastq_r1=..., fastq_r2=...)` call.

### Trim Galore

Import `trim_galore` plus `BaseQualityEncoding` and `AdapterSequence` from
`latch.verified.trim_galore`. Its current signature is detailed and includes
paired inputs, adapter options, clipping, quality, and output settings.

## Discover Through Latch MCP

When Latch MCP is configured:

1. Call `list_workspaces` and choose the intended workspace.
2. Call `list_workflows` to discover public and workspace workflows.
3. Call `get_workflow_schema` for the selected workflow.
4. Validate every parameter against that returned schema.
5. Show the workflow, workspace, resource/cost implications, and parameter
   summary to the user.
6. Obtain confirmation.
7. Call `launch_workflow`.
8. Monitor with `get_execution` and retrieve logs only when needed.

This path is preferable to guessing Python imports for Console-only workflows.
See `references/latch-mcp.md`.

## Discover Through the Console

Use the Workflows page:

```text
https://console.latch.bio/workflows
```

The workflow's current parameter page is authoritative for that published
version. Record:

- Workflow ID and version
- Input and output schema
- Default resources
- Required reference data
- Scientific method and citations
- Expected cost and runtime

Do not infer scientific suitability from the "Verified" label alone. Confirm
reference genome, assay assumptions, tool versions, and validation needs.

## Referencing a Workspace Workflow

For a workflow in the active workspace, `workflow_reference` wraps Flyte's
reference launch plan:

```python
from latch import workflow, workflow_reference
from latch.types import LatchFile


@workflow_reference(
    name="wf.entrypoint.existing_workflow",
    version="1.2.3-abcd12",
)
def existing(input_file: LatchFile) -> LatchFile:
    ...


@workflow
def composed_workflow(input_file: LatchFile) -> LatchFile:
    return existing(input_file=input_file)
```

The decorated reference still needs an exact typed function signature. Prefer
generated or source-backed signatures; do not invent one from a display form.

`workflow_reference` resolves `current_workspace()` when the decorator is
evaluated. Importing this module therefore requires valid Latch authentication
and network access and will fail in a fully offline test environment. Verify the
active workspace before import/registration and isolate this coupling in a
small module.

## Version and Reproducibility Rules

- Pin the Latch SDK used to register the caller workflow.
- Record the referenced workflow ID/name and version.
- Re-run schema inspection after an SDK upgrade.
- Treat a changed wrapper signature or internal reference version as a behavior
  change.
- Use a small launch plan for integration testing.
- Preserve tool and database citations in downstream reports.

## Official Sources

- Workflow catalog overview: https://wiki.latch.bio/workflows/overview
- Ready-to-use workflow guides: https://wiki.latch.bio/llms.txt
- Verified exports in the 2.76.8 release commit: https://github.com/latchbio/latch/tree/0faa9dcd8186444ac008f50adf95d43f0fa30e06/src/latch/verified
- Latch MCP: https://wiki.latch.bio/agent/latch-mcp
- Latch Verified repositories: https://github.com/latch-verified

### `references/workflow-creation.md`

# Python Workflow Creation

This reference targets `latch==2.76.8`. Check the installed SDK with
`scripts/inspect_latch_sdk.py` before using version-sensitive symbols.

## Mental Model

- A function decorated with `@workflow` defines a graph.
- A function decorated with a task decorator runs in its own containerized task.
- Calling a task inside a workflow creates a node; it does not execute ordinary
  Python at graph-construction time.
- Workflow inputs and outputs must be typed.
- Put file I/O, subprocesses, network calls, secret lookup, and scientific
  computation inside tasks.
- Keep module import time deterministic and free of external side effects.

## Initialize a Project

```bash
latch init my-workflow --template subprocess
```

Current template choices are exposed by `latch init --help`; common choices
include `subprocess`, `conda`, `r`, and `empty`. A project commonly contains a
`wf/` Python package, a `version` file, dependency inputs, and optional
`Dockerfile` and metadata files.

Do not assume a hand-written Dockerfile is required. Registration can generate
one. If a Dockerfile is present at the project root, registration uses it.

## Tasks and Workflows

```python
from latch import small_task, workflow


@small_task
def normalize_name(sample_name: str) -> str:
    return sample_name.strip().replace(" ", "_")


@workflow
def normalize_sample(sample_name: str) -> str:
    """Normalize a sample identifier."""
    return normalize_name(sample_name=sample_name)
```

Use keyword arguments for task calls. They make graph wiring explicit and
survive parameter reordering.

### File input and output

`LatchFile` and `LatchDir` remain the most established workflow signature types.
Inputs are staged onto the task machine. Returned values pair a local path with
a remote destination.

```python
from pathlib import Path

from latch import small_task, workflow
from latch.types import LatchFile, LatchOutputDir


@small_task
def count_lines(input_file: LatchFile, output_dir: LatchOutputDir) -> LatchFile:
    source = Path(input_file.local_path)
    destination = Path("/root/line-count.txt")

    with source.open("r", encoding="utf-8") as handle:
        count = sum(1 for _ in handle)
    destination.write_text(f"{count}\n", encoding="utf-8")

    remote_dir = output_dir.remote_path
    if remote_dir is None:
        raise ValueError("output_dir must have a remote Latch path")

    return LatchFile(
        str(destination),
        f"{remote_dir.rstrip('/')}/line-count.txt",
    )


@workflow
def line_count_workflow(
    input_file: LatchFile,
    output_dir: LatchOutputDir,
) -> LatchFile:
    return count_lines(input_file=input_file, output_dir=output_dir)
```

For new imperative remote-path operations, prefer `LPath`; see
`references/data-management.md`. Do not silently replace typed workflow
parameters with plain strings merely to avoid learning the file types.

## Custom Workflow Metadata

Without metadata, the SDK derives a basic interface from the workflow
signature. Add `LatchMetadata` when the form needs deliberate design.

```python
from pathlib import Path

from latch import small_task, workflow
from latch.types import LatchFile
from latch.types.metadata import (
    LatchAuthor,
    LatchMetadata,
    LatchParameter,
    LatchRule,
)


@small_task
def validate_task(reads: LatchFile) -> bool:
    return Path(reads.local_path).stat().st_size > 0


metadata = LatchMetadata(
    display_name="FASTQ Validator",
    author=LatchAuthor(name="Workflow Team"),
    license="MIT",
    repository="https://github.com/example/fastq-validator",
    parameters={
        "reads": LatchParameter(
            display_name="Reads",
            description="Input FASTQ or compressed FASTQ file.",
            rules=[
                LatchRule(
                    regex=r".*\.(fastq|fq)(\.gz)?$",
                    message="Choose a .fastq, .fq, .fastq.gz, or .fq.gz file.",
                )
            ],
        )
    },
)


@workflow(metadata)
def validate_fastq(reads: LatchFile) -> bool:
    return validate_task(reads=reads)
```

Metadata keys must match workflow parameter names. The SDK rejects metadata
keys absent from the function signature.

Although `about_page_path` is documented, SDK 2.76.8 can fail while serializing
its `Path` value. Use `documentation=` and a descriptive workflow docstring
until that defect is fixed.

See `references/ui-and-automation.md` for sections, samplesheets, launch plans,
messages, and result links.

## Parallel Mapping

Use `map_task` when one task should run over a list. Mapping produces a single
map node rather than thousands of graph nodes.

```python
from pathlib import Path

from latch import map_task, small_task, workflow
from latch.types import LatchFile


@small_task
def validate_one(reads: LatchFile) -> bool:
    return Path(reads.local_path).stat().st_size > 0


@workflow
def validate_batch(reads: list[LatchFile]) -> list[bool]:
    return map_task(validate_one)(reads=reads)
```

Map task inputs must line up with the mapped function's parameter names.
Resource overrides are Flyte overrides and should be tested against the
installed SDK.

## Conditional Nodes

Ordinary Python `if` statements cannot branch on task promises. Build a
conditional node:

```python
from latch import create_conditional_section, small_task, workflow


@small_task
def double(value: float) -> float:
    return value * 2


@small_task
def square(value: float) -> float:
    return value**2


@workflow
def transform(value: float) -> float:
    doubled = double(value=value)
    return (
        create_conditional_section("choose-transform")
        .if_(doubled < 0.0)
        .then(double(value=doubled))
        .elif_(doubled > 0.0)
        .then(square(value=doubled))
        .else_()
        .fail("Zero is not accepted")
    )
```

Use `&` and `|` for compound promise expressions. For a task-produced Boolean,
use its promise truth checks rather than Python unary `not`.

## Caching, Retries, and Timeouts

Named task decorators forward Flyte task options:

```python
from datetime import timedelta

from latch import medium_task


@medium_task(
    cache=True,
    cache_version="reference-index-v2",
    retries=2,
    timeout=timedelta(hours=2),
)
def build_index(reference: LatchFile) -> LatchFile:
    ...
```

- Change `cache_version` whenever output-affecting logic or dependencies change.
- Cache only deterministic tasks.
- Retries should cover transient failures, not malformed inputs.
- Set a timeout with scientific runtime variance in mind.
- See `references/resource-configuration.md` before selecting a larger instance.

## Task-Specific Dockerfiles

Since SDK 2.57.0, a task decorator's `dockerfile` argument must be a string
literal so registration can discover it through static AST inspection:

```python
@small_task(dockerfile="Dockerfile.validation")
def validate_with_custom_image(reads: LatchFile) -> bool:
    ...
```

Do not pass a `Path`, variable, function call, or computed expression to this
argument.

## Workflow Design Checklist

- Every input and output has a concrete type.
- Workflow bodies only compose task, map, conditional, and reference nodes.
- Tasks return actual values rather than undefined placeholder variables.
- Output destinations do not collide across concurrent runs.
- Subprocess calls use argument lists and `check=True`.
- Dependencies and tool versions are pinned for releases.
- Metadata keys match the workflow signature.
- Cache versions reflect code and dependency changes.
- The image has been tested with staging registration and `latch develop`.

## Official Sources

- Python SDK overview: https://wiki.latch.bio/workflows/sdk/python/overview
- Quick start: https://wiki.latch.bio/workflows/sdk/python/quick-start
- Conditional sections: https://wiki.latch.bio/workflows/sdk/python/conditional-sections
- Map tasks: https://wiki.latch.bio/workflows/sdk/python/map-task
- Caching: https://wiki.latch.bio/workflows/sdk/python/caching
- Workflow environment: https://wiki.latch.bio/workflows/sdk/python/workflow-environment/overview
- SDK source at the 2.76.8 release commit: https://github.com/latchbio/latch/tree/0faa9dcd8186444ac008f50adf95d43f0fa30e06

### `scripts/inspect_latch_sdk.py`

```python
#!/usr/bin/env python3
"""Inspect the installed Latch SDK without authentication or network access."""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
import platform
import re
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any


SYMBOL_GROUPS: dict[str, list[tuple[str, str]]] = {
    "core": [
        ("latch", "workflow"),
        ("latch", "map_task"),
        ("latch", "create_conditional_section"),
        ("latch", "workflow_reference"),
    ],
    "tasks": [
        ("latch.resources.tasks", "small_task"),
        ("latch.resources.tasks", "medium_task"),
        ("latch.resources.tasks", "large_task"),
        ("latch.resources.tasks", "small_gpu_task"),
        ("latch.resources.tasks", "large_gpu_task"),
        ("latch.resources.tasks", "custom_task"),
        ("latch.resources.tasks", "custom_memory_optimized_task"),
        ("latch.resources.tasks", "v100_x1_task"),
        ("latch.resources.tasks", "v100_x4_task"),
        ("latch.resources.tasks", "v100_x8_task"),
        ("latch.resources.tasks", "g6e_xlarge_task"),
        ("latch.resources.tasks", "g6e_2xlarge_task"),
        ("latch.resources.tasks", "g6e_4xlarge_task"),
        ("latch.resources.tasks", "g6e_8xlarge_task"),
        ("latch.resources.tasks", "g6e_12xlarge_task"),
        ("latch.resources.tasks", "g6e_16xlarge_task"),
        ("latch.resources.tasks", "g6e_24xlarge_task"),
        ("latch.resources.tasks", "g6e_48xlarge_task"),
    ],
    "data": [
        ("latch.ldata.path", "LPath"),
        ("latch.types", "LatchFile"),
        ("latch.types", "LatchDir"),
        ("latch.types", "LatchOutputFile"),
        ("latch.types", "LatchOutputDir"),
        ("latch.types", "file_glob"),
    ],
    "metadata": [
        ("latch.types.metadata", "LatchMetadata"),
        ("latch.types.metadata", "LatchParameter"),
        ("latch.resources.launch_plan", "LaunchPlan"),
        ("latch.types.samplesheet_item", "SamplesheetItem"),
    ],
    "registry": [
        ("latch.account", "Account"),
        ("latch.registry.project", "Project"),
        ("latch.registry.table", "Table"),
        ("latch.registry.record", "Record"),
    ],
    "execution": [
        ("latch_cli.services.launch.launch_v2", "launch"),
        ("latch_cli.services.launch.launch_v2", "launch_from_launch_plan"),
        ("latch_cli.services.launch.launch_v2", "Execution"),
        ("latch_cli.services.launch.launch_v2", "CompletedExecution"),
    ],
    "verified": [
        ("latch.verified", "rnaseq"),
        ("latch.verified", "deseq2_wf"),
        ("latch.verified", "gene_ontology_pathway_analysis"),
        ("latch.verified", "mafft"),
        ("latch.verified", "trim_galore"),
    ],
}


METHODS: dict[str, tuple[str, str, list[str]]] = {
    "LPath": (
        "latch.ldata.path",
        "LPath",
        [
            "exists",
            "iterdir",
            "mkdirp",
            "copy_to",
            "upload_from",
            "download",
            "rmr",
            "fetch_metadata",
        ],
    ),
    "Table": (
        "latch.registry.table",
        "Table",
        ["load", "list_records", "get_dataframe", "update"],
    ),
    "Execution": (
        "latch_cli.services.launch.launch_v2",
        "Execution",
        ["poll", "wait", "abort"],
    ),
}

OBJECT_REPR = re.compile(r"<(?P<name>[^<>]+) object at 0x[0-9a-fA-F]+>")
ADDRESS_REPR = re.compile(r"0x[0-9a-fA-F]+")


def normalize_repr(value: str) -> str:
    """Remove process-specific memory addresses from introspection output."""
    value = OBJECT_REPR.sub(lambda match: f"<{match.group('name')}>", value)
    return ADDRESS_REPR.sub("0x<address>", value)


def safe_signature(obj: Any) -> str | None:
    try:
        return normalize_repr(str(inspect.signature(obj)))
    except (TypeError, ValueError):
        return None


def inspect_symbol(module_name: str, symbol_name: str) -> dict[str, Any]:
    qualified_name = f"{module_name}.{symbol_name}"
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # Import failures are the diagnostic output.
        return {
            "qualified_name": qualified_name,
            "available": False,
            "error": normalize_repr(f"{type(exc).__name__}: {exc}"),
        }

    if not hasattr(module, symbol_name):
        return {
            "qualified_name": qualified_name,
            "available": False,
            "error": "symbol not found",
        }

    obj = getattr(module, symbol_name)
    result = {
        "qualified_name": qualified_name,
        "available": True,
        "kind": type(obj).__name__,
        "signature": safe_signature(obj),
    }

    python_interface = getattr(obj, "python_interface", None)
    if python_interface is not None:
        result["python_interface"] = {
            "inputs": {
                name: normalize_repr(inspect.formatannotation(annotation))
                for name, annotation in python_interface.inputs.items()
            },
            "outputs": {
                name: normalize_repr(inspect.formatannotation(annotation))
                for name, annotation in python_interface.outputs.items()
            },
        }

    return result


def inspect_methods(
    module_name: str,
    class_name: str,
    method_names: list[str],
) -> dict[str, Any]:
    try:
        cls = getattr(importlib.import_module(module_name), class_name)
    except Exception as exc:
        return {"error": normalize_repr(f"{type(exc).__name__}: {exc}")}

    result: dict[str, Any] = {}
    for method_name in method_names:
        method = getattr(cls, method_name, None)
        result[method_name] = {
            "available": method is not None,
            "signature": safe_signature(method) if method is not None else None,
        }
    return result


def build_report() -> dict[str, Any]:
    try:
        latch_version = version("latch")
    except PackageNotFoundError:
        latch_version = None

    symbols = {
        group: [
            inspect_symbol(module_name, symbol_name)
            for module_name, symbol_name in entries
        ]
        for group, entries in SYMBOL_GROUPS.items()
    }

    methods = {
        label: inspect_methods(module_name, class_name, method_names)
        for label, (module_name, class_name, method_names) in METHODS.items()
    }

    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "latch_version": latch_version,
        "symbols": symbols,
        "methods": methods,
    }


def print_text(report: dict[str, Any]) -> None:
    print(f"Python: {report['python']}")
    print(f"Platform: {report['platform']}")
    print(f"Latch SDK: {report['latch_version'] or 'not installed'}")

    for group, entries in report["symbols"].items():
        print(f"\n[{group}]")
        for entry in entries:
            status = "ok" if entry["available"] else "missing"
            line = f"- {status}: {entry['qualified_name']}"
            if entry.get("signature"):
                line += entry["signature"]
            if entry.get("error"):
                line += f" ({entry['error']})"
            print(line)
            if entry.get("python_interface"):
                print(f"  inputs: {entry['python_interface']['inputs']}")
                print(f"  outputs: {entry['python_interface']['outputs']}")

    print("\n[methods]")
    for class_name, methods in report["methods"].items():
        print(f"- {class_name}")
        if "error" in methods:
            print(f"  error: {methods['error']}")
            continue
        for method_name, details in methods.items():
            status = "ok" if details["available"] else "missing"
            signature = details["signature"] or ""
            print(f"  - {status}: {method_name}{signature}")


def has_required_failures(report: dict[str, Any]) -> bool:
    required = {
        "latch.workflow",
        "latch.resources.tasks.small_task",
        "latch.resources.tasks.custom_task",
        "latch.ldata.path.LPath",
        "latch.registry.table.Table",
        "latch_cli.services.launch.launch_v2.launch",
    }
    observed = {
        entry["qualified_name"]: entry["available"]
        for entries in report["symbols"].values()
        for entry in entries
    }
    return any(not observed.get(name, False) for name in required)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when a core symbol is missing.",
    )
    args = parser.parse_args()

    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)

    if report["latch_version"] is None:
        return 2
    if args.strict and has_required_failures(report):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
