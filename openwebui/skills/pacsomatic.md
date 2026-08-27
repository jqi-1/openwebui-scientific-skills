---
name: pacsomatic
description: Operator toolkit for nf-core/pacsomatic matched tumor-normal workflows from BAM inputs. Use this skill when the user needs to validate run inputs, generate pacsomatic-compliant samplesheets, prepare reproducible Nextflow launch artifacts, run locally or submit to schedulers (LSF/Slurm/PBS/SGE), and triage execution failures. Triggers on requests to run pacsomatic, prepare launch commands/scripts, perform dry-run checks, or troubleshoot pipeline startup and scheduler submission errors.
---

# pacsomatic

## Overview

This skill provides a reproducible execution workflow for nf-core/pacsomatic, centered on a single helper entrypoint that handles validation, artifact generation, and optional execution.

Primary entrypoint:
- `scripts/run_pacsomatic.py`

The helper script:
- validates required identifiers, files, reference mode, and runtime prerequisites
- writes a pacsomatic-compatible samplesheet (`patient,sample,status,bam,pbi`)
- generates a params YAML and launch script for reproducible reruns
- supports dry-run validation and run/submit execution paths

Use this skill as the default path for pacsomatic operations. Do not bypass it with manually assembled `nextflow run nf-core/pacsomatic` commands unless the user explicitly asks for manual command construction.

## When to Use This Skill

Invoke this skill when the user asks to:
- run matched tumor-normal analysis from BAM files
- generate or fix pacsomatic samplesheet and launch artifacts
- execute locally or submit to schedulers (LSF/Slurm/PBS/SGE)
- perform dry-run validation before execution
- troubleshoot launch failures or summarize run outputs

Do not use this skill for:
- deep biological interpretation beyond run-level sanity checks
- editing pipeline internals unless explicitly requested

Typical trigger phrases:
- "run nf-core/pacsomatic for this tumor-normal pair"
- "prepare pacsomatic samplesheet and launch script"
- "do a dry run first and tell me what is missing"
- "submit pacsomatic to slurm/lsf and return the job id"
- "why did pacsomatic submission fail"

## Routing and Execution Rules

1. Always collect required run inputs first.
2. Always route through `scripts/run_pacsomatic.py` for validation and artifact generation.
3. Default to `--dry-run` when the user asks for checks/validation only.
4. Use `--run` only when the user asks to execute/submit.
5. For scheduler modes, include executor-specific resource arguments and return detected job ID when available.
6. If execution fails, report first failure point and next triage target (`.nextflow.log`, `pipeline_info`, failing task logs).

## Inputs Required

Required:
- tumor BAM path
- normal BAM path
- patient ID
- tumor sample ID
- normal sample ID
- output directory
- exactly one reference mode: `--fasta` or `--genome`

Optional:
- profile, resources, scheduler account/queue
- pipeline version (`-r`)
- params file, resume/report/dag flags
- `--dry-run` and/or `--run`

## Workflow

1. Validate identity and input constraints.
2. Validate required local paths (BAM, optional PBI, optional FASTA).
3. Resolve runtime and dependency checks.
4. Build samplesheet and generated params YAML.
5. Generate launch script for selected executor.
6. If `--dry-run` and not `--run`, stop after artifact generation.
7. If `--run`, execute locally or submit to scheduler.
8. Return command/script path, validation status, and job ID (if detected).

## Agent Response Contract

Every response after invocation should include:
- exact command used or generated script path
- confirmation that validation checks ran
- run type (`dry-run` vs `run`)
- scheduler job ID when available
- one concrete next step for validation/triage

## Quick Start

Dry run:

```bash
python scripts/run_pacsomatic.py \
  --tumor-bam /path/to/tumor.bam \
  --normal-bam /path/to/normal.bam \
  --patient-id P001 \
  --tumor-sample-id P001_T \
  --normal-sample-id P001_N \
  --outdir /path/to/output \
  --genome GRCh38 \
  --profile singularity,sanger \
  --dry-run
```

Scheduler execution example (Slurm):

```bash
python scripts/run_pacsomatic.py \
  --tumor-bam /path/to/tumor.bam \
  --normal-bam /path/to/normal.bam \
  --patient-id P001 \
  --tumor-sample-id P001_T \
  --normal-sample-id P001_N \
  --outdir /path/to/output \
  --genome GRCh38 \
  --profile singularity,sanger \
  --executor slurm \
  --queue compute \
  --project my_account \
  --cpus 16 \
  --memory-gb 64 \
  --walltime 48:00 \
  --run
```

## Configuration

Use `config.yaml` as the baseline for profile/executor/runtime defaults. Override at invocation time when user requirements differ.

## Testing

Run unit tests from skill root:

```bash
python -m unittest discover -s tests/pacsomatic -v
```

## References

- `references/agent-playbook.md`
- `references/config-and-output.md`
- `references/pacsomatic_guide.md`
- `scripts/run_pacsomatic.py`

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pacsomatic/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/agent-playbook.md`

# Agent Playbook

## What The User Needs To Provide

Users only need to provide run inputs; they do not need to know pipeline internals:

- tumor BAM path
- normal BAM path
- reference input (`--fasta` path or `--genome` key)
- output directory

Optional:

- sample metadata IDs
- executor/resource preferences
- optional `pbi` paths

No repository checkout directory is required for this skill.

Use this sequence when helping a user run nf-core/pacsomatic:

1. Collect required inputs.
   - tumor BAM
   - normal BAM
   - patient ID
   - tumor sample ID
   - normal sample ID
   - output directory
   - one reference mode: `--fasta` or `--genome`
2. Validate naming rules.
   Patient/sample identifiers cannot contain spaces.
3. Validate local input paths.
   Local BAMs must exist. `pbi` is optional, but if provided the file must exist.
4. Start with a dry run when uncertain.
   Use `--dry-run` to validate assumptions and generate artifacts without scheduling.
5. Launch when requested.
   Use `--run` with a selected `--executor` (`local`, `lsf`, `slurm`, `pbs`, or `sge`).
6. After submission.
   Report generated samplesheet path, script path, printed run command, and detected job ID if present.
7. If pipeline fails later.
   Inspect launcher logs first, then Nextflow report and DAG outputs.

Recommended helper command:

```bash
python .github/skills/pacsomatic/scripts/run_pacsomatic.py \
  --tumor-bam /path/to/tumor.bam \
  --normal-bam /path/to/normal.bam \
  --patient-id P001 \
  --tumor-sample-id P001_T \
  --normal-sample-id P001_N \
  --outdir /path/to/output \
  --genome GRCh38 \
  --profile singularity,sanger \
   --executor local \
  --dry-run
```

Launch command variant:

```bash
python .github/skills/pacsomatic/scripts/run_pacsomatic.py \
  --tumor-bam /path/to/tumor.bam \
  --normal-bam /path/to/normal.bam \
  --patient-id P001 \
  --tumor-sample-id P001_T \
  --normal-sample-id P001_N \
  --outdir /path/to/output \
  --fasta /path/to/reference.fa \
  --profile singularity,sanger \
   --executor lsf \
  --run
```

### `references/config-and-output.md`

# Config And Output

## Required Inputs

- `--tumor-bam`: tumor BAM path
- `--normal-bam`: normal BAM path
- `--patient-id`
- `--tumor-sample-id`
- `--normal-sample-id`
- `--outdir`
- one reference mode:
  - `--fasta`, or
  - `--genome`

## Core Optional Controls

- `--profile`: Nextflow profile list (for example `singularity,sanger`)
- `--pipeline-version`: release pin for reproducibility
- `--params-file`: structured pipeline params
- `--resume`: rerun interrupted work
- `--with-report`: Nextflow report path
- `--with-dag`: Nextflow DAG path

## Execution Backend Controls

- `--executor`: `local`, `none`, `lsf`, `slurm`, `pbs`, or `sge`

Direct CLI execution is supported in all modes. When `--run` is used, the
helper runs backend-native launch commands:

- `local` / `none`: `bash <script>`
- `lsf`: `bsub < <script>`
- `slurm`: `sbatch <script>`
- `pbs` / `sge`: `qsub <script>`

## Scheduler Controls (when executor is scheduler-backed)

- `--project`
- `--queue`
- `--cpus`
- `--memory-gb`
- `--walltime`
- `--job-name`
- `--logdir`
- `--stdout-file`
- `--stderr-file`

## Helper Outputs

The helper writes:

- samplesheet CSV (default `<outdir>/samplesheet.csv`)
- launch script (default `<outdir>/run_pacsomatic.<executor>.sh`)

It also prints:

- backend-specific run command (for example `bash`, `bsub`, `sbatch`, or `qsub`)
- launcher output when `--run` is used
- detected job ID when parseable from scheduler output

## Samplesheet Schema

Expected columns:

- `patient`
- `sample`
- `status`
- `bam`
- `pbi`

Notes:

- `bam` should be the full path to the sample BAM.
- `pbi` is optional.

Status values:

- tumor: `1`
- normal: `0`

## Run Modes

- generate only (default): write artifacts, no scheduler submission
- `--dry-run`: validate inputs/dependencies and write artifacts
- `--run`: execute or submit generated launch script using selected `--executor`

## Official Output Anchors

nf-core/pacsomatic organizes results under grouped directories, including:

- `alignment`
- `germline_snv`
- `somatic_snv`
- `somatic_sv`
- `somatic_cnv`
- `methylation`
- `tumor_clonality`
- `signature_analysis`
- `pipeline_info`
- `multiqc`

### `references/pacsomatic_guide.md`

# Pacsomatic Guide

This guide summarizes the official nf-core/pacsomatic usage and how this skill
helps an agent validate, prepare, and launch runs across compute platforms.

## What nf-core/pacsomatic runs

nf-core/pacsomatic is a Nextflow pipeline for matched tumor/normal PacBio HiFi
somatic analysis.

Typical upstream command from official docs:

```bash
nextflow run nf-core/pacsomatic \
  -profile <docker/singularity/.../institute> \
  --input samplesheet.csv \
  --outdir <OUTDIR> \
  --genome GRCh38
```

Important notes from docs:

- Input is a CSV samplesheet with columns: `patient,sample,status,bam[,pbi]`.
- `status` uses `1` for tumor and `0` for normal.
- Pipeline parameters should be passed via CLI flags or `-params-file`, not `-c`.

## Cross-agent reuse

This skill can be reused by other agents in the same workspace.

- Keep the whole folder `.github/skills/pacsomatic` intact when reusing.
- Other agents can either:
  - call `scripts/run_pacsomatic.py` to generate a backend-aware launch script, or
  - emit a direct platform-native script and return the matching launcher command.
- If moving to another repository, copy the same folder structure and keep
  `SKILL.md`, `references/`, and `scripts/` together.
- Validate environment assumptions per cluster (Nextflow module version,
  profile such as `singularity,sanger`, queue/project names, and network access
  for remote BAM URLs).

## Minimal samplesheet format

```csv
patient,sample,status,bam,pbi
ID1,ID1_tumor,1,/path/ID1_tumor.bam,/path/ID1_tumor.bam.pbi
ID1,ID1_normal,0,/path/ID1_normal.bam,/path/ID1_normal.bam.pbi
```

`pbi` is optional. If not available, leave it blank.

## Platform-aware execution model in this skill

By default, the helper generates artifacts. With `--run`, it executes/submits
using the selected `--executor` backend.

It produces:

- A validated samplesheet CSV from tumor/normal BAM inputs
- A standalone launch script that runs Nextflow + nf-core/pacsomatic
- A ready run command (for example `bash`, `bsub`, `sbatch`, `qsub`)
- Launcher output and detected job ID when `--run` is enabled

## Example: generate script only

```bash
python .github/skills/pacsomatic/scripts/run_pacsomatic.py \
  --tumor-bam /data/P1_tumor.bam \
  --normal-bam /data/P1_normal.bam \
  --patient-id P1 \
  --tumor-sample-id P1_tumor \
  --normal-sample-id P1_normal \
  --fasta /refs/GRCh38.fa \
  --outdir /results/p1 \
  --profile singularity \
  --executor local \
  --queue normal \
  --cpus 16 \
  --memory-gb 64 \
  --walltime 48:00
```

## Example: dry-run validation

```bash
python .github/skills/pacsomatic/scripts/run_pacsomatic.py \
  --tumor-bam /data/P1_tumor.bam \
  --normal-bam /data/P1_normal.bam \
  --patient-id P1 \
  --tumor-sample-id P1_tumor \
  --normal-sample-id P1_normal \
  --genome GRCh38 \
  --outdir /results/p1 \
  --profile singularity \
  --executor local \
  --dry-run
```

## Example: generate and submit immediately

```bash
python .github/skills/pacsomatic/scripts/run_pacsomatic.py \
  --tumor-bam /data/P1_tumor.bam \
  --normal-bam /data/P1_normal.bam \
  --patient-id P1 \
  --tumor-sample-id P1_tumor \
  --normal-sample-id P1_normal \
  --genome GRCh38 \
  --outdir /results/p1 \
  --profile singularity \
  --executor lsf \
  --run
```

## Example: submit on Slurm

```bash
python .github/skills/pacsomatic/scripts/run_pacsomatic.py \
  --tumor-bam /data/P1_tumor.bam \
  --normal-bam /data/P1_normal.bam \
  --patient-id P1 \
  --tumor-sample-id P1_tumor \
  --normal-sample-id P1_normal \
  --genome GRCh38 \
  --outdir /results/p1 \
  --profile singularity \
  --executor slurm \
  --queue compute \
  --cpus 16 \
  --memory-gb 64 \
  --run
```

## Direct command-line operation (no agent wrapper)

The helper is a standalone CLI and can be run directly from shell scripts,
terminal sessions, CI jobs, or workflow launch wrappers.

Supported HPC schedulers via `--executor`:

- `lsf` (uses `bsub`)
- `slurm` (uses `sbatch`)
- `pbs` (uses `qsub`)
- `sge` (uses `qsub`)

Local direct execution is also supported with:

- `--executor local` (runs generated script with `bash`)

## Direct LSF script (no Python wrapper)

If users request a ready-to-submit LSF script directly, provide a `.lsf.sh`
file that can be submitted as-is.

Example file: `submit_pacsomatic_hg008.lsf.sh`

```bash
#!/usr/bin/env bash
#BSUB -J Somatic_singularity
#BSUB -P Somatic_singularity
#BSUB -q heavy_io
#BSUB -n 16
#BSUB -M 64000
#BSUB -W 48:00
#BSUB -o out%J.out
#BSUB -e err%J.err

set -euo pipefail

RUN_DIR="${RUN_DIR:-$PWD/pacsomatic_hg008_run}"
OUTDIR="${OUTDIR:-$RUN_DIR/results}"
WORKDIR="${WORKDIR:-$RUN_DIR/work}"
SAMPLESHEET="$RUN_DIR/samplesheet.csv"

mkdir -p "$RUN_DIR" "$OUTDIR" "$WORKDIR"

cat > "$SAMPLESHEET" << 'CSV'
patient,sample,status,bam,pbi
Patient_HG008,DS_MT_T,1,https://raw.githubusercontent.com/nf-core/test-datasets/pacsomatic/testdata/HG008_Downsample_MT_tumor.bam,
Patient_HG008,DS_MT_N,0,https://raw.githubusercontent.com/nf-core/test-datasets/pacsomatic/testdata/HG008_Downsample_MT_normal.bam,
CSV

module load nextflow/21.10.5
export NXF_WORK="$WORKDIR"

nextflow run nf-core/pacsomatic \
  -profile singularity,sanger \
  --input "$SAMPLESHEET" \
  --outdir "$OUTDIR" \
  --genome GRCh38 \
  -with-report "$OUTDIR/HiFi_Somatic_Nextflow_Run_Report.html" \
  -with-dag "$OUTDIR/HiFi_Somatic_Flowchart.png" \
  -resume
```

Submit with:

```bash
bsub < submit_pacsomatic_hg008.lsf.sh
```

## LSF examples aligned with your cluster style

The script supports your style of submission, including `-P`, queue switching,
`module load nextflow/21.10.5`, `-resume`, and report/DAG outputs.

Built-in defaults now match your common combo:

- project: `Somatic_singularity`
- queue: `heavy_io`
- module-load: `module load nextflow/21.10.5`

Default LSF output naming now follows your style:

- stdout: `out%J.out`
- stderr: `err%J.err`

You can override with `--stdout-file` and `--stderr-file`, and optionally set
`--logdir` to place them under a specific directory.

```bash
python .github/skills/pacsomatic/scripts/run_pacsomatic.py \
  --tumor-bam /data/P1_tumor.bam \
  --normal-bam /data/P1_normal.bam \
  --patient-id P1 \
  --tumor-sample-id P1_tumor \
  --normal-sample-id P1_normal \
  --genome GRCh38 \
  --outdir /results/p1 \
  --project Somatic_test \
  --queue heavy_io \
  --memory-gb 20 \
  --job-name Somatic_test \
  --module-load "module load nextflow/21.10.5" \
  --with-report HiFi_Somatic_Nextflow_Run_Report.html \
  --with-dag HiFi_Somatic_Flowchart.png
```

For your Sanger configs usage, set combined profiles such as:

```bash
--profile singularity,sanger
```

Reference: <https://nf-co.re/configs/sanger/>

## Best practices

- Ensure BAMs are coordinate-valid and index files are available when possible.
- Use explicit pipeline version with `--pipeline-version` for reproducibility.
- Prefer pinning `--pipeline-version` when using fixed test datasets to avoid schema drift across pipeline revisions.
- Use `--params-file` for large parameter sets and keep script options minimal.
- Prefer containerized profile (`singularity` or `docker`) on HPC.
- Set `NXF_OPTS` memory ceiling if Nextflow launcher memory spikes.
- nf-core/pacsomatic may require a newer Nextflow than legacy module versions; if the cluster allows, prefer a modern Nextflow release compatible with the pipeline.

### `scripts/run_pacsomatic.py`

```python
"""Prepare, validate, and optionally launch nf-core/pacsomatic across platforms."""

import argparse
import csv
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

SCHEDULER_CMDS = {
    "lsf": "bsub",
    "slurm": "sbatch",
    "pbs": "qsub",
    "sge": "qsub",
}

PACSOMATIC_HOST_TOOLS = [
    "pbmm2",
    "samtools",
    "mosdepth",
    "clair3",
    "hiphase",
    "deepsomatic",
    "severus",
    "cnvkit.py",
    "vep",
    "svpack",
    "AnnotSV",
    "multiqc",
]

MIN_JAVA_MAJOR = 17


def fail(message):
    print(f"[ERROR] {message}", file=sys.stderr)
    raise SystemExit(1)


def info(message):
    print(f"[INFO] {message}")


def warn(message):
    print(f"[WARN] {message}")


def script_dir():
    return Path(__file__).resolve().parent


def is_remote_path(path):
    parsed = urlparse(path)
    return parsed.scheme in {"http", "https", "s3", "gs", "ftp"}


def normalize_walltime_hhmmss(value, label):
    if re.fullmatch(r"\d{1,3}:\d{2}:\d{2}", value):
        return value
    if re.fullmatch(r"\d{1,3}:\d{2}", value):
        return f"{value}:00"
    fail(f"Invalid {label} format: {value!r}. Use HH:MM or HH:MM:SS")


def has_any_command(names):
    return next((name for name in names if shutil.which(name) is not None), "")


def detect_java_major_version():
    if shutil.which("java") is None:
        return None
    completed = subprocess.run(["java", "-version"], capture_output=True, text=True)
    raw = f"{completed.stdout}\n{completed.stderr}"
    match = re.search(r'version\s+"([0-9]+)(?:\.[0-9._]+)?"', raw)
    if match:
        return int(match.group(1))
    return None


def ensure_no_spaces(label, value):
    if any(ch.isspace() for ch in value):
        fail(f"{label} must not contain spaces: {value!r}")


def validate_repo(repo_path):
    repo_path = repo_path.expanduser().resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        fail(f"Repository path does not exist or is not a directory: {repo_path}")
    entry = repo_path / "main.nf"
    if not entry.exists():
        fail(f"Could not find main.nf in repository path: {repo_path}")
    return repo_path


def ensure_pipeline_repo(args):
    if not args.repo_path and not args.checkout_dir:
        return

    if args.repo_path:
        repo = validate_repo(Path(args.repo_path))
        args.pipeline = str(repo)
        info(f"Using local pipeline repository: {repo}")
        return

    if shutil.which("git") is None:
        fail("git is required to clone pipeline repository")

    checkout_dir = Path(args.checkout_dir).expanduser().resolve()
    checkout_dir.mkdir(parents=True, exist_ok=True)
    target = checkout_dir / args.repo_name
    if not target.exists():
        cmd = ["git", "clone", args.repo_url, str(target)]
        info("Cloning repository: " + " ".join(cmd))
        completed = subprocess.run(cmd)
        if completed.returncode != 0:
            fail(f"git clone failed with code {completed.returncode}")

    repo = validate_repo(target)
    args.pipeline = str(repo)
    info(f"Using cloned pipeline repository: {repo}")


def parse_env_list_output(raw_output, env_name):
    for line in raw_output.splitlines():
        line = line.strip()
        if not line or line.startswith("Name") or line.startswith("#"):
            continue
        tokens = line.split()
        path_token = next((token for token in reversed(tokens) if token.startswith("/")), None)
        if path_token is None:
            continue
        prefix = Path(path_token)
        if prefix.name == env_name:
            return prefix
        if tokens and tokens[0] == env_name:
            return prefix
    return None


def find_conda_env_prefix(env_name):
    commands = []
    if shutil.which("mamba"):
        commands.append(["mamba", "env", "list"])
    if shutil.which("conda"):
        commands.append(["conda", "env", "list"])

    for cmd in commands:
        completed = subprocess.run(cmd, capture_output=True, text=True)
        combined = f"{completed.stdout}\n{completed.stderr}"
        prefix = parse_env_list_output(combined, env_name)
        if prefix is not None and prefix.exists():
            return prefix

    return None


def default_conda_env_file():
    return script_dir().parent / "environment" / "nextflow-env.yml"


def create_conda_env(env_name, env_file):
    env_file = Path(env_file).expanduser().resolve()
    if not env_file.exists():
        fail(f"Conda environment file does not exist: {env_file}")

    if shutil.which("mamba"):
        cmd = ["mamba", "env", "create", "-n", env_name, "-f", str(env_file)]
    elif shutil.which("conda"):
        cmd = ["conda", "env", "create", "-n", env_name, "-f", str(env_file)]
    else:
        fail("Neither mamba nor conda is available to create environment")

    info("Creating conda environment: " + " ".join(cmd))
    completed = subprocess.run(cmd)
    if completed.returncode != 0:
        fail(f"Environment creation failed with code {completed.returncode}")


def resolve_runtime(args):
    if args.use_current_path:
        return None

    prefix = find_conda_env_prefix(args.conda_env)
    if prefix is None and args.create_conda_env:
        env_file = args.conda_env_file or str(default_conda_env_file())
        create_conda_env(args.conda_env, env_file)
        prefix = find_conda_env_prefix(args.conda_env)

    if prefix is None:
        if args.run:
            fail(
                f"Conda environment '{args.conda_env}' was not found. "
                "Re-run with --create-conda-env or use --use-current-path."
            )
        warn(
            f"Conda environment '{args.conda_env}' was not found. "
            "Dry-run/generate-only continues; run mode requires a resolvable runtime."
        )
        return None

    nextflow_bin = prefix / "bin" / "nextflow"
    if nextflow_bin.exists():
        args.nextflow_bin = str(nextflow_bin)
        info(f"Using Nextflow from conda environment: {nextflow_bin}")
    else:
        warn(
            f"Conda environment found at {prefix}, but nextflow was not found in {prefix / 'bin'}. "
            "Falling back to --nextflow-bin PATH lookup."
        )

    return prefix


def build_generated_params_content(args, samplesheet_path):
    lines = [
        f"input: {samplesheet_path}",
        f"outdir: {args.outdir}",
    ]
    if args.fasta:
        lines.append(f"fasta: {args.fasta}")
    elif args.genome:
        lines.append(f"genome: {args.genome}")
    return "\n".join(lines) + "\n"


def write_generated_params_file(args, samplesheet_path):
    config_path = os.path.join(args.outdir, args.config_name)
    os.makedirs(os.path.dirname(config_path) or ".", exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as handle:
        handle.write(build_generated_params_content(args, samplesheet_path))
    return config_path


def build_samplesheet(args, samplesheet_path):
    rows = [
        {
            "patient": args.patient_id,
            "sample": args.tumor_sample_id,
            "status": "1",
            "bam": args.tumor_bam,
            "pbi": args.tumor_pbi or "",
        },
        {
            "patient": args.patient_id,
            "sample": args.normal_sample_id,
            "status": "0",
            "bam": args.normal_bam,
            "pbi": args.normal_pbi or "",
        },
    ]

    with open(samplesheet_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["patient", "sample", "status", "bam", "pbi"])
        writer.writeheader()
        writer.writerows(rows)


def resolve_reference_args(args):
    if args.fasta:
        return ["--fasta", args.fasta]
    if args.genome:
        return ["--genome", args.genome]
    raise ValueError("Either --fasta or --genome must be provided.")


def build_nextflow_command(args, samplesheet_path):
    cmd = [
        args.nextflow_bin,
        "run",
        args.pipeline,
        "-profile",
        args.profile,
        "--input",
        samplesheet_path,
        "--outdir",
        args.outdir,
    ]
    cmd.extend(resolve_reference_args(args))

    if args.pipeline_version:
        cmd.extend(["-r", args.pipeline_version])

    params_file = args.params_file
    if not params_file and args.use_generated_params_file and args.generated_params_file:
        params_file = args.generated_params_file
    if params_file:
        cmd.extend(["-params-file", params_file])

    if args.resume:
        cmd.append("-resume")

    if args.with_report:
        cmd.extend(["-with-report", args.with_report])

    if args.with_dag:
        cmd.extend(["-with-dag", args.with_dag])

    if args.extra_args:
        cmd.extend(shlex.split(args.extra_args))

    return cmd


def scheduler_header_lines(args):
    mem_mb = int(args.memory_gb * 1024)
    stdout_path = os.path.join(args.logdir, args.stdout_file) if args.logdir else args.stdout_file
    stderr_path = os.path.join(args.logdir, args.stderr_file) if args.logdir else args.stderr_file
    walltime_hhmmss = normalize_walltime_hhmmss(args.walltime, "walltime")

    if args.executor == "lsf":
        lines = [
            f"#BSUB -J {args.job_name}",
            f"#BSUB -n {args.cpus}",
            f"#BSUB -M {mem_mb}",
            f"#BSUB -W {args.walltime}",
            f"#BSUB -o {stdout_path}",
            f"#BSUB -e {stderr_path}",
        ]
        if args.queue:
            lines.insert(1, f"#BSUB -q {args.queue}")
        if args.project:
            lines.insert(1, f"#BSUB -P {args.project}")
        return lines

    if args.executor == "slurm":
        lines = [
            f"#SBATCH --job-name={args.job_name}",
            f"#SBATCH --cpus-per-task={args.cpus}",
            f"#SBATCH --mem={mem_mb}",
            f"#SBATCH --time={args.walltime}",
            f"#SBATCH --output={stdout_path}",
            f"#SBATCH --error={stderr_path}",
        ]
        if args.queue:
            lines.insert(1, f"#SBATCH --partition={args.queue}")
        if args.project:
            lines.insert(1, f"#SBATCH --account={args.project}")
        return lines

    if args.executor == "pbs":
        lines = [
            f"#PBS -N {args.job_name}",
            f"#PBS -l select=1:ncpus={args.cpus}:mem={int(args.memory_gb)}gb",
            f"#PBS -l walltime={walltime_hhmmss}",
            f"#PBS -o {stdout_path}",
            f"#PBS -e {stderr_path}",
        ]
        if args.queue:
            lines.insert(1, f"#PBS -q {args.queue}")
        if args.project:
            lines.insert(1, f"#PBS -A {args.project}")
        return lines

    if args.executor == "sge":
        lines = [
            f"#$ -N {args.job_name}",
            f"#$ -pe smp {args.cpus}",
            f"#$ -l h_vmem={max(1, int(args.memory_gb / max(1, args.cpus)))}G",
            f"#$ -l h_rt={walltime_hhmmss}",
            f"#$ -o {stdout_path}",
            f"#$ -e {stderr_path}",
        ]
        if args.queue:
            lines.insert(1, f"#$ -q {args.queue}")
        if args.project:
            lines.insert(1, f"#$ -P {args.project}")
        return lines

    return []


def default_script_path(args):
    suffix = args.executor if args.executor in SCHEDULER_CMDS else "local"
    return os.path.join(args.outdir, f"run_pacsomatic.{suffix}.sh")


def write_launch_script(args, script_path, nextflow_cmd):
    quoted_cmd = " ".join(shlex.quote(token) for token in nextflow_cmd)
    mkdir_targets = [args.outdir, args.workdir]
    if args.logdir:
        mkdir_targets.append(args.logdir)

    lines = ["#!/usr/bin/env bash"]
    lines.extend(scheduler_header_lines(args))
    lines.extend([
        "",
        "set -euo pipefail",
        f"mkdir -p {' '.join(shlex.quote(path) for path in mkdir_targets)}",
        f"export NXF_WORK={shlex.quote(args.workdir)}",
    ])

    if args.nxf_opts:
        lines.append(f"export NXF_OPTS={shlex.quote(args.nxf_opts)}")

    if args.singularity_cache:
        lines.append(f"export NXF_SINGULARITY_CACHEDIR={shlex.quote(args.singularity_cache)}")

    if args.runtime_prefix:
        lines.append(f"export PATH={shlex.quote(str(Path(args.runtime_prefix) / 'bin'))}:$PATH")
        lines.append(f"export CONDA_PREFIX={shlex.quote(str(args.runtime_prefix))}")

    lines.append("")
    if args.module_load:
        lines.append(args.module_load)
    lines.append(quoted_cmd)

    with open(script_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    os.chmod(script_path, 0o755)


def verify_bam_and_index(label, bam_path, pbi_path):
    if is_remote_path(bam_path):
        info(f"{label} BAM is remote; skipping local existence checks: {bam_path}")
        return

    if not os.path.exists(bam_path):
        fail(f"{label} BAM does not exist: {bam_path}")

    bai_candidates = [f"{bam_path}.bai", re.sub(r"\.bam$", ".bai", bam_path, flags=re.IGNORECASE)]
    csi_candidate = f"{bam_path}.csi"
    has_standard_index = any(os.path.exists(path) for path in bai_candidates + [csi_candidate])
    if not has_standard_index:
        warn(
            f"{label} BAM has no local .bai/.csi index alongside input path. "
            "This is allowed, but some pipeline steps may require indexed BAMs."
        )

    if pbi_path and not os.path.exists(pbi_path):
        fail(f"{label} .pbi path was provided but does not exist: {pbi_path}")


#: Characters that would let --module-load smuggle something other than a module
#: command into the generated launch script. Everything else written into that
#: script goes through shlex.quote(); this argument is emitted as a bare shell
#: line, so it is constrained here instead.
_SHELL_METACHARACTERS = set("$`|><&(){}[]*?!~\n\r\\\"'")


def normalize_module_load(raw):
    """Validate --module-load and return it as a safe shell line.

    Accepts one or more `module ...` commands separated by `&&` or `;` -- the
    documented shape, e.g. "module purge && module load nextflow/23.10.0".
    Rejects anything else so a caller-supplied string cannot become arbitrary
    shell in the launch script the operator later executes.
    """
    if not raw or not raw.strip():
        return ""

    segments = [seg.strip() for seg in re.split(r"&&|;", raw) if seg.strip()]
    if not segments:
        fail("--module-load contained no command.")

    normalized = []
    for segment in segments:
        if any(ch in _SHELL_METACHARACTERS for ch in segment):
            fail(
                f"--module-load segment {segment!r} contains shell metacharacters. "
                "Only plain 'module ...' commands are accepted."
            )
        try:
            tokens = shlex.split(segment)
        except ValueError as exc:
            fail(f"--module-load segment {segment!r} could not be parsed: {exc}")
        if not tokens or tokens[0] != "module":
            fail(
                f"--module-load segment {segment!r} does not start with 'module'. "
                "Pass module commands only, e.g. 'module load nextflow/23.10.0'."
            )
        normalized.append(" ".join(shlex.quote(token) for token in tokens))

    return " && ".join(normalized)


def validate_inputs(args):
    args.module_load = normalize_module_load(args.module_load)
    ensure_no_spaces("patient-id", args.patient_id)
    ensure_no_spaces("tumor-sample-id", args.tumor_sample_id)
    ensure_no_spaces("normal-sample-id", args.normal_sample_id)
    if args.tumor_sample_id == args.normal_sample_id:
        fail("tumor-sample-id and normal-sample-id must be different.")

    if not args.fasta and not args.genome:
        fail("Either --fasta or --genome must be provided.")

    if args.fasta and args.genome:
        info("Both --fasta and --genome were provided; --fasta will be used.")

    verify_bam_and_index("tumor", args.tumor_bam, args.tumor_pbi)
    verify_bam_and_index("normal", args.normal_bam, args.normal_pbi)

    if args.fasta and not is_remote_path(args.fasta) and not os.path.exists(args.fasta):
        fail(f"Reference FASTA does not exist: {args.fasta}")


def ensure_runtime_tools(args):
    nextflow_missing = shutil.which(args.nextflow_bin) is None
    if args.run and nextflow_missing:
        fail(f"Could not find Nextflow executable: {args.nextflow_bin}")
    if not args.run and nextflow_missing:
        warn(
            f"Nextflow executable not found ({args.nextflow_bin}). "
            "Dry-run and generate-only modes can continue without Nextflow."
        )

    if args.run and args.executor in SCHEDULER_CMDS:
        submit_cmd = SCHEDULER_CMDS[args.executor]
        if shutil.which(submit_cmd) is None:
            fail(f"{submit_cmd} is required for --run with --executor {args.executor}")


def ensure_dependency_tools(args):
    profile_items = [item.strip().lower() for item in args.profile.split(",") if item.strip()]
    missing_run = []
    missing_warn = []
    missing_host = []

    java_cmd = has_any_command(["java"])
    java_major = detect_java_major_version()
    if not java_cmd:
        if args.run:
            missing_run.append("java")
        else:
            missing_warn.append("java")
    elif java_major is None:
        warn("Unable to detect Java version. Nextflow requires Java 17 or later.")
    elif java_major < MIN_JAVA_MAJOR:
        if args.run:
            missing_run.append(f"java>={MIN_JAVA_MAJOR}")
        else:
            missing_warn.append(f"java>={MIN_JAVA_MAJOR}")

    if "docker" in profile_items and not has_any_command(["docker"]):
        if args.run:
            missing_run.append("docker")
        else:
            missing_warn.append("docker")

    if "singularity" in profile_items or "apptainer" in profile_items:
        container_cmd = has_any_command(["singularity", "apptainer"])
        if not container_cmd:
            if args.run:
                missing_run.append("singularity|apptainer")
            else:
                missing_warn.append("singularity|apptainer")

    if "conda" in profile_items and not has_any_command(["conda", "mamba"]):
        if args.run:
            missing_run.append("conda|mamba")
        else:
            missing_warn.append("conda|mamba")

    # Local profile typically expects host tools to be available directly on PATH.
    auto_check_host_tools = args.run and "local" in profile_items
    should_check_host_tools = args.check_host_bio_tools or auto_check_host_tools

    if should_check_host_tools:
        for tool in PACSOMATIC_HOST_TOOLS:
            if shutil.which(tool) is None:
                missing_host.append(tool)

        if missing_host:
            msg = (
                "Missing host bioinformatics tools requested by --check-host-bio-tools: "
                + ", ".join(sorted(set(missing_host)))
            )
            if args.run and (args.strict_host_bio_tools or auto_check_host_tools):
                fail(msg)
            warn(msg)

    if missing_warn:
        warn(
            "Potentially missing dependency tools for selected profile/runtime: "
            + ", ".join(sorted(set(missing_warn)))
            + ". Dry-run/generate-only continues."
        )

    if missing_run:
        fail(
            "Missing dependency tools for selected profile/runtime: "
            + ", ".join(sorted(set(missing_run)))
        )


def submit_command_for_executor(executor, script_path):
    """Return (argv, stdin_path) for submitting the launch script.

    lsf reads the script from stdin (`bsub < script`); every other executor
    takes it as an argument. Returning an argv list rather than a shell string
    keeps submission off a shell entirely, so a script path containing shell
    metacharacters cannot extend the command that runs.
    """
    if executor == "lsf":
        return ["bsub"], script_path
    if executor == "slurm":
        return ["sbatch", script_path], None
    if executor in {"pbs", "sge"}:
        return ["qsub", script_path], None
    return ["bash", script_path], None


def format_submit_command(argv, stdin_path):
    """Render a submission as a copy-pasteable shell line, for display only."""
    line = shlex.join(argv)
    if stdin_path:
        line += f" < {shlex.quote(stdin_path)}"
    return line


def extract_job_id(executor, output):
    patterns = {
        "lsf": r"<([0-9]+)>",
        "slurm": r"Submitted batch job\s+([0-9]+)",
        "pbs": r"^([0-9]+(?:\.[A-Za-z0-9_.-]+)?)$",
        "sge": r"job\s+([0-9]+)",
    }
    pattern = patterns.get(executor)
    if not pattern:
        return None

    for line in output.splitlines():
        match = re.search(pattern, line.strip())
        if match:
            return match.group(1)
    return None


def execute_launch(args, script_path):
    argv, stdin_path = submit_command_for_executor(args.executor, script_path)
    if stdin_path:
        with open(stdin_path, "rb") as handle:
            completed = subprocess.run(argv, stdin=handle, text=True, capture_output=True)
    else:
        completed = subprocess.run(argv, text=True, capture_output=True)
    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()

    if completed.returncode != 0:
        if stderr:
            print(stderr, file=sys.stderr)
        fail(f"Execution failed with exit code {completed.returncode}")

    print("--- Launch Complete ---")
    if stdout:
        print(stdout)

    job_id = extract_job_id(args.executor, stdout)
    if job_id:
        info(f"Detected job id: {job_id}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepare and optionally launch nf-core/pacsomatic from matched tumor/normal BAMs"
    )

    parser.add_argument("--tumor-bam", required=True, help="Tumor BAM path")
    parser.add_argument("--normal-bam", required=True, help="Normal BAM path")
    parser.add_argument("--tumor-pbi", default="", help="Tumor BAM index (.pbi) path, optional")
    parser.add_argument("--normal-pbi", default="", help="Normal BAM index (.pbi) path, optional")
    parser.add_argument("--patient-id", required=True, help="Patient ID for samplesheet")
    parser.add_argument("--tumor-sample-id", required=True, help="Tumor sample ID")
    parser.add_argument("--normal-sample-id", required=True, help="Normal sample ID")

    parser.add_argument("--fasta", default="", help="Reference FASTA path")
    parser.add_argument("--genome", default="", help="Reference genome key, e.g. GRCh38")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--workdir", default="", help="Nextflow work directory, default: <outdir>/work")
    parser.add_argument("--logdir", default="", help="Optional scheduler logs directory; if unset use current directory")
    parser.add_argument("--stdout-file", default="out%J.out", help="Scheduler stdout filename pattern")
    parser.add_argument("--stderr-file", default="err%J.err", help="Scheduler stderr filename pattern")
    parser.add_argument("--samplesheet", default="", help="Samplesheet path, default: <outdir>/samplesheet.csv")
    parser.add_argument("--script-path", default="", help="Launch script path, default: <outdir>/run_pacsomatic.<executor>.sh")

    parser.add_argument("--pipeline", default="nf-core/pacsomatic", help="Pipeline name or repo")
    parser.add_argument("--repo-path", default="", help="Optional local pipeline repository path (contains main.nf)")
    parser.add_argument("--repo-url", default="https://github.com/nf-core/pacsomatic.git", help="Pipeline repository URL when cloning")
    parser.add_argument("--checkout-dir", default="", help="Directory where pipeline repo should be cloned")
    parser.add_argument("--repo-name", default="pacsomatic", help="Folder name inside checkout-dir for cloned repo")
    parser.add_argument("--pipeline-version", default="", help="Pipeline version for -r")
    parser.add_argument("--nextflow-bin", default="nextflow", help="Nextflow executable path")
    parser.add_argument("--profile", default="singularity", help="Nextflow profile, e.g. singularity or singularity,institute")
    parser.add_argument("--params-file", default="", help="Path to Nextflow -params-file (yaml/json)")
    parser.add_argument("--config-name", default="pacsomatic.params.generated.yaml", help="Generated params YAML filename under outdir")
    parser.add_argument("--use-generated-params-file", action="store_true", help="Use generated params YAML via -params-file when params-file is not provided")
    parser.add_argument("--resume", action="store_true", help="Add -resume to Nextflow command")
    parser.add_argument("--with-report", default="", help="Path for Nextflow -with-report output")
    parser.add_argument("--with-dag", default="", help="Path for Nextflow -with-dag output")
    parser.add_argument("--extra-args", default="", help="Extra raw args appended to Nextflow command")

    parser.add_argument(
        "--executor",
        default="local",
        choices=["local", "none", "lsf", "slurm", "pbs", "sge"],
        help="Execution backend for generated script and --run behavior",
    )
    parser.add_argument("--job-name", default="pacsomatic", help="Scheduler job name")
    parser.add_argument("--project", default="", help="Scheduler project/account when supported")
    parser.add_argument("--queue", default="", help="Scheduler queue/partition when supported")
    parser.add_argument("--cpus", type=int, default=16, help="CPU slots/threads")
    parser.add_argument("--memory-gb", type=float, default=64.0, help="Requested memory in GB")
    parser.add_argument("--walltime", default="48:00", help="Requested walltime in HH:MM or HH:MM:SS")
    parser.add_argument("--nxf-opts", default="", help="Optional NXF_OPTS, e.g. '-Xms1g -Xmx4g'")
    parser.add_argument("--singularity-cache", default="", help="Optional NXF_SINGULARITY_CACHEDIR")
    parser.add_argument("--conda-env", default="pacsomatic-nextflow", help="Conda environment name used to resolve Nextflow runtime")
    parser.add_argument("--conda-env-file", default="", help="Conda environment YAML used with --create-conda-env")
    parser.add_argument("--create-conda-env", action="store_true", help="Create conda environment when missing")
    parser.add_argument("--use-current-path", action="store_true", help="Use current PATH and skip conda runtime resolution")
    parser.add_argument(
        "--module-load",
        default="",
        help="Optional module command prefix, e.g. 'module load nextflow/23.10.0'",
    )

    parser.add_argument(
        "--check-host-bio-tools",
        action="store_true",
        help="Check pacsomatic host bioinformatics tools on PATH (mainly for non-container local runs)",
    )
    parser.add_argument(
        "--strict-host-bio-tools",
        action="store_true",
        help="Fail in --run mode if --check-host-bio-tools finds missing host tools",
    )

    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and write artifacts without execution")
    parser.add_argument("--run", action="store_true", help="Execute or submit the generated launch script")
    parser.add_argument("--submit", action="store_true", help="Backward-compatible alias for --run")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.submit:
        args.run = True

    args.runtime_prefix = None
    args.generated_params_file = ""

    ensure_pipeline_repo(args)
    runtime_prefix = resolve_runtime(args)
    if runtime_prefix is not None:
        args.runtime_prefix = str(runtime_prefix)

    validate_inputs(args)
    ensure_runtime_tools(args)
    ensure_dependency_tools(args)

    os.makedirs(args.outdir, exist_ok=True)

    args.workdir = args.workdir or os.path.join(args.outdir, "work")
    samplesheet_path = args.samplesheet or os.path.join(args.outdir, "samplesheet.csv")
    launch_script_path = args.script_path or default_script_path(args)

    if args.logdir:
        os.makedirs(args.logdir, exist_ok=True)
    os.makedirs(os.path.dirname(samplesheet_path) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(launch_script_path) or ".", exist_ok=True)

    build_samplesheet(args, samplesheet_path)
    args.generated_params_file = write_generated_params_file(args, samplesheet_path)
    nextflow_cmd = build_nextflow_command(args, samplesheet_path)
    write_launch_script(args, launch_script_path, nextflow_cmd)

    submit_argv, submit_stdin = submit_command_for_executor(args.executor, launch_script_path)

    print("--- Pacsomatic Launch Assets Prepared ---")
    print(f"Samplesheet : {os.path.abspath(samplesheet_path)}")
    print(f"Launch script: {os.path.abspath(launch_script_path)}")
    print(f"Params YAML : {os.path.abspath(args.generated_params_file)}")
    print(f"Executor    : {args.executor}")
    print(f"Run cmd     : {format_submit_command(submit_argv, submit_stdin)}")

    if args.dry_run and not args.run:
        info("Dry run complete. Inputs and runtime dependencies validated.")
        return

    if not args.run:
        info("Artifacts generated. Re-run with --run to execute/submit.")
        return

    execute_launch(args, launch_script_path)


if __name__ == "__main__":
    main()
```

### `LICENSE`

```text
MIT License

Copyright (c) 2026 Beifang Niu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### `config.yaml`

```yaml
# Baseline configuration for nf-core/pacsomatic skill usage.
# These values are intended as defaults for operators and agents.

pipeline:
  name: nf-core/pacsomatic
  repo_url: https://github.com/nf-core/pacsomatic.git
  default_version: ""

runtime:
  conda_env: pacsomatic-nextflow
  use_current_path: false
  create_conda_env: false
  conda_env_file: ""

execution:
  profile: singularity,sanger
  executor: local  # local | none | lsf | slurm | pbs | sge
  cpus: 16
  memory_gb: 64
  walltime: "48:00"
  queue: ""
  project: ""
  job_name: pacsomatic

outputs:
  samplesheet_name: samplesheet.csv
  generated_params_name: pacsomatic.params.generated.yaml
  launch_script_suffix_local: local
  default_workdir_name: work

validation:
  enforce_no_spaces_in_ids: true
  require_exactly_one_reference_mode: true
  warn_if_bam_index_missing: true
  min_java_major: 17

agent_response:
  include_command_or_script_path: true
  include_validation_confirmation: true
  include_run_type: true
  include_job_id_if_available: true
  include_next_triage_step: true
```
