---
name: datalad
description: Retrieve, version, and publish scientific datasets with DataLad and git-annex, and capture computational provenance with datalad run, rerun, and containers-run. Use when cloning or fetching data from OpenNeuro, DANDI, datasets.datalad.org, or any DataLad dataset; when a file in a dataset reads as a broken symlink or a small pointer instead of real data; when an analysis needs a machine-readable record of how each output was produced so it can be re-executed; or when publishing a dataset to siblings such as a GitHub repository plus a storage remote. Also use to decide between DataLad and plain Git for a data-carrying repository.
---

# DataLad

## Overview

DataLad is a data management layer over Git and git-annex. Git tracks the dataset
structure, small text files, and the history. git-annex tracks the *content* of large
files, storing each file as a key and keeping the bytes somewhere that is not necessarily
the local repository.

That split is the single most important thing to internalise, because it means a freshly
cloned dataset contains the full history and the full file listing while containing almost
none of the data. A 100 TB dataset clones in seconds and occupies a few megabytes. The
bytes arrive only when asked for, per file, with `datalad get`.

The second thing DataLad adds is provenance. `datalad run` executes a command and commits
the result together with a machine-readable record of the command, its inputs, and its
outputs. `datalad rerun` reads that record back and re-executes it. This turns "how was
this figure produced" from an archaeology problem into a command.

## When to use DataLad instead of plain Git

Use DataLad when any of the following holds:

- Files are too large for Git to handle comfortably, or the total exceeds what every
  collaborator wants on disk.
- Data lives in more than one place (a lab server, a cluster scratch, S3, a supercomputer)
  and you need to know which copies exist.
- The analysis must be re-executable, and a plain commit message is not enough evidence.
- You are consuming published datasets from OpenNeuro, DANDI, or `datasets.datalad.org`,
  which are distributed as DataLad datasets.
- The project nests other datasets inside it and you want each one to keep its own
  independent history.

Use plain Git when the repository is code and text only, everything fits comfortably in
Git, and nobody needs partial checkouts. DataLad on top of a small pure-code repository
adds indirection without buying anything.

## Installation

```bash
# git-annex is NOT written in Python but is available from PyPI if you already
# have git itself installed:
uv pip install git-annex
# You can also install it first from the system
# (Debian/Ubuntu: apt install git-annex; macOS: brew install git-annex;
#  conda-forge: conda install -c conda-forge git-annex)
uv pip install datalad
uv pip install datalad-container   # only for containers-run

datalad wtf --section dependencies   # confirm git-annex version is visible
```

The PyPI `git-annex` package ships the prebuilt binary as a wheel for Linux, macOS, and
Windows rather than building the Haskell sources, so it installs like any other Python
dependency and can be pinned in the same environment as DataLad. It does not bring git
along with it.

`datalad wtf` prints the resolved environment and is the first thing to run when behaviour
looks impossible. An old or missing git-annex is behind a large share of confusing errors.

DataLad itself is MIT licensed. git-annex is a separate tool under the AGPL, which matters
only if you redistribute a modified git-annex rather than call it.

## The failure that bites first: pointers are not data

After `datalad clone`, annexed files exist as symlinks into `.git/annex/objects/` (or as
small pointer files where symlinks are unavailable, such as on Windows or a crippled
filesystem). Nothing has downloaded the content yet.

```bash
datalad clone https://github.com/OpenNeuroDatasets/ds000001.git
cd ds000001
ls sub-01/anat/            # the file is listed
python -c "import nibabel; nibabel.load('sub-01/anat/sub-01_T1w.nii.gz')"   # fails
datalad get sub-01/anat/sub-01_T1w.nii.gz                                   # now it works
```

The failure mode to recognise: a tool reports the file as empty, truncated, corrupt, "not
a gzip file", or a broken symlink, and the file size on disk is a few hundred bytes. That
is a pointer, not a corrupted download. **Run `datalad get` before reading data, and treat
"file exists" as insufficient evidence that its content is present.**

Before an analysis touches a directory, fetch it explicitly:

```bash
datalad get sub-01/                  # everything under a path
datalad get -r .                     # everything, including subdatasets
datalad get -n -r .                  # subdataset structure only, no file content
```

`datalad status --annex` reports how much content is present locally, and
`git annex whereis <path>` reports which repositories hold a given file. `whereis` reads
recorded state and does not contact the remotes, so it tells you what git-annex last
learned rather than what is true right now.

See [data-access.md](references/data-access.md) for finding datasets, subdataset
behaviour, dropping content safely, and repairing a dataset.

## Recording provenance with datalad run

`datalad run` is the reason to reach for DataLad in a methods context. It saves the
command alongside its effect, in the same commit:

```bash
datalad run -m "extract brain mask" \
  --input "sub-01/anat/sub-01_T1w.nii.gz" \
  --output "derivatives/sub-01_brain.nii.gz" \
  "bet {inputs} {outputs} -m"
```

What each part does, and why skipping it hurts:

- `--input` retrieves the content before running, so the command does not fail on a
  pointer. It also records the dependency, which is what lets `rerun` fetch the same
  inputs on a different machine.
- `--output` unlocks or removes the target first, so git-annex does not refuse to write
  over content it is protecting. Without it, a second run of the same command commonly
  fails with a permission error on an annexed file that looks read-only.
- `{inputs}` and `{outputs}` expand to those values. `{pwd}`, `{dspath}`, and `{tmpdir}`
  are also available, and `{inputs[0]}` indexes individual entries.
- The commit message carries a JSON run record between `=== Do not change lines below ===`
  and `^^^ Do not change lines above ^^^`. Do not hand-edit that block; `rerun` parses it.

`datalad run` refuses to start when the dataset has unsaved modifications, because an
unclean starting state makes the record unreliable. Save or discard first, or pass
`--explicit` to declare that the listed inputs and outputs are the complete story. Check a
command before committing to it with `--dry-run basic` or `--dry-run command`.

A run that changes nothing produces no commit, exactly as `datalad save` does.

### Re-executing

```bash
datalad rerun                       # redo the run recorded at HEAD
datalad rerun --report              # show what would be done, change nothing
datalad rerun --script recompute.sh # extract the commands instead of running them
datalad rerun --since <commit> -b check <revision>   # replay a range onto a new branch
```

Rerunning onto a branch (`-b`) is the safe way to test reproducibility: the replay lands
somewhere else, and a diff against the original branch answers whether the outputs came
back identical.

### Containers

With the `datalad-container` extension, register an image once and every subsequent run
records which image produced the outputs:

```bash
datalad containers-add fsl --url docker://brainlife/fsl:6.0.4
datalad containers-run -n fsl -m "brain mask in container" \
  --input "sub-01/anat/sub-01_T1w.nii.gz" \
  --output "derivatives/sub-01_brain.nii.gz" \
  "bet {inputs} {outputs} -m"
```

The image itself is tracked in the dataset, so the software environment travels with the
data and the provenance record rather than living in someone's shell history. When only
one container is configured, `-n` may be omitted.

See [provenance.md](references/provenance.md) for the STAMPED principles and the YODA
project layout, the run record format, `--explicit` and `--assume-ready` semantics, and
exporting provenance toward W3C PROV.

## Saving and inspecting changes

```bash
datalad status                 # what changed, including subdataset state
datalad save -m "add QC report" path/to/file
datalad save -m "checkpoint" -r                 # recurse into subdatasets
datalad save -m "small text file" --to-git notes.md
```

`datalad save` decides per file whether content goes to Git or to git-annex, following the
dataset's `.gitattributes`. Force a file into Git with `--to-git`, which is the right call
for code and small text files that should stay directly readable. The `yoda` procedure
(`datalad create -c yoda`) sets this up for `code/`, `README.md`, and `CHANGELOG.md`
automatically.

## Creating a dataset

```bash
datalad create my_dataset               # plain dataset
datalad create -c yoda my_analysis      # analysis layout (code/ tracked in Git,
                                        # README.md and CHANGELOG.md preconfigured)
datalad create -d . inputs/raw          # register a new subdataset under an existing one
```

`-c yoda` applies the analysis project layout described in
[provenance.md](references/provenance.md). `-d .` is what registers a new dataset as a
subdataset of the parent rather than leaving an unrelated repository inside it.

## Publishing

A DataLad dataset is usually published to two places at once: a Git hosting service for
the history, and a storage remote for the annexed content.

```bash
datalad create-sibling-github myaccount/mydataset
git annex initremote store type=S3 bucket=my-bucket encryption=none autoenable=true
datalad siblings configure -s github --publish-depends store
datalad push --to github
```

The Git sibling and the storage sibling are created by different tools on purpose. A Git
sibling is a Git remote, and `datalad create-sibling-*` handles the hosting-service ones.
An S3 bucket (or WebDAV, or an SSH directory) is a *git-annex special remote*, not a Git
remote, so it is created with `git annex initremote`. `datalad siblings` picks the special
remote up afterwards and treats it like any other. Using `datalad siblings add --url
s3://...` here is the mistake this section exists to prevent: `--url` is a Git remote URL,
S3 is not, and the `push --to github` below then fails on the `--publish-depends` hop.

`--publish-depends` is what stops the common broken publication: a Git repository whose
history references content that was never uploaded, so collaborators clone successfully
and then find every `datalad get` failing. Declaring the dependency makes the storage
sibling publish first, every time.

`datalad push` sends both the Git history and, by default (`--data auto-if-wanted`), the
annexed content the target is configured to want. Pass `--data anything` to push all
content regardless of the target's preferences.

See [publishing.md](references/publishing.md) for RIA stores, special remotes, credential
handling, and configuring which sibling holds what.

## Freeing disk space

```bash
git annex whereis sub-01/                 # confirm another copy exists first
datalad drop sub-01/                      # remove local content, keep the pointer
datalad drop --what all --reckless kill <path>   # last resort, destroys data
```

`datalad drop` refuses by default when it cannot verify another copy of the content
exists, which is a safety check rather than an obstacle. `--nocheck` and `--if-dirty` are
deprecated; the current spelling is `--reckless availability`, and it means what it says.
`--what` selects between `filecontent` (the default), `allkeys`, `datasets`, and `all`.

## Failure modes worth knowing

| Symptom | Cause | Fix |
|---|---|---|
| File reads as empty, truncated, or a broken symlink | Content not retrieved; only the pointer is present | `datalad get <path>` |
| "Permission denied" writing an existing output | git-annex write-protects annexed content | Declare it with `--output`, or `datalad unlock <path>` |
| `datalad run` refuses to start | Dataset has unsaved changes | `datalad save` first, or pass `--explicit` |
| `datalad drop` refuses | No verified second copy of the content | Push to a sibling first, or accept `--reckless availability` |
| Collaborator clones but every `get` fails | History published without the content | Publish the storage sibling, and set `--publish-depends` |
| Clone succeeds, subdataset directories are empty | Subdatasets are not installed by default | `datalad get -n -r .`, then `get` the paths you need |
| Commands behave impossibly | git-annex missing or too old | `datalad wtf --section dependencies` |

## Detailed references

- [data-access.md](references/data-access.md): finding published datasets
  (`registry.datalad.org`, OpenNeuro, DANDI, `datasets.datalad.org` and the `///`
  shortcut), clone and get options, subdataset handling, annex content states, dropping
  and removing, and `fsck` repair.
- [provenance.md](references/provenance.md): the STAMPED principles and the YODA layout,
  the run record format, `run` and `rerun` options in full, `containers-run`, and the
  current state of exporting DataLad provenance toward W3C PROV.
- [publishing.md](references/publishing.md): siblings and their actions,
  `create-sibling-*` variants, RIA stores, special remotes, `push` semantics, and
  credential handling.

## Related skills

The `bids` skill covers the Brain Imaging Data Structure that most of the neuroimaging
datasets distributed through DataLad are organised in. A typical workflow clones a BIDS
dataset with DataLad, validates it with the BIDS tooling, then runs a BIDS-App under
`datalad containers-run` so the derivatives carry provenance.

## Primary sources

- DataLad documentation: <https://docs.datalad.org/en/stable/>
- DataLad Handbook: <https://handbook.datalad.org/en/latest/>
- `datalad run` chapter: <https://handbook.datalad.org/en/latest/basics/101-108-run.html>
- YODA principles: <https://handbook.datalad.org/en/latest/basics/101-127-yoda.html>
- STAMPED principles (operationalized from YODA): <https://stamped-principles.org>
- datalad-container: <https://docs.datalad.org/projects/container/en/stable/>
- git-annex: <https://git-annex.branchable.com/>
- Dataset registry: <https://registry.datalad.org>

## Acknowledgment

Topic scope for this skill was informed in part by @bcmcpher's MIT-licensed
[datalad-cli](https://github.com/bcmcpher/my-skills/tree/main/plugins/datalad-cli)
plugin (nineteen per-command slash-command skills). The text here is written
independently and grounded in the upstream DataLad documentation; overlap is unavoidable
because both cover DataLad, but the structure, style, and specific technical claims are
different.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/datalad/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/data-access.md`

# Finding, retrieving, and releasing dataset content

## Finding published datasets

| Source | What it holds | How to reach it |
|---|---|---|
| [registry.datalad.org](https://registry.datalad.org) | Search across roughly 16,000 unique DataLad and git-annex datasets, indexing URL, dataset ID, branches, tags, and metadata | Search box supports a bare word, a quoted phrase, `AND`/`OR`/`NOT`, and field-specific terms; results give clone URLs |
| [datasets.datalad.org](https://datasets.datalad.org) | The DataLad superdataset, a nested collection of curated public datasets | `datalad clone ///` for the superdataset, `datalad clone ///<name>` for one entry |
| [OpenNeuroDatasets](https://github.com/OpenNeuroDatasets) | Public BIDS neuroimaging datasets from OpenNeuro, one repository per accession | `datalad clone https://github.com/OpenNeuroDatasets/ds00XXXX.git` |
| [dandisets](https://github.com/dandisets) | DANDI archive dandisets, mostly neurophysiology in NWB | `datalad clone https://github.com/dandisets/000XXX.git` |

The `///` shortcut is a DataLad resource identifier that resolves to the superdataset on
`datasets.datalad.org`. Because that superdataset is itself made of subdatasets, cloning
it gives a browsable tree of dataset names with no data in it, which is the intended way
to explore before choosing.

## Cloning

```
datalad clone [-h] [-d DATASET] [-D DESCRIPTION] [--reckless
    [auto|ephemeral|shared-...]] [-m MESSAGE] [-c PROC] [--version]
    SOURCE [PATH] ...
```

`SOURCE` accepts a URL, a local path, the `///` shortcut, or a RIA store URL such as
`ria+http://store.datalad.org#~hcp-openaccess`.

- `-d/--dataset` registers the new clone as a subdataset of the given parent, which is the
  correct way to bring external data into a project rather than copying it in.
- `--reckless auto` hard-links content between clones on the same filesystem, and
  `--reckless ephemeral` symlinks the annex to the origin's annex. Both trade safety for
  speed and disk, and both are recorded in local config and inherited by subdatasets. Use
  them for throwaway clones on a cluster, not for anything you will edit and push. For
  maintaining multiple concurrent checkouts of the same dataset without re-cloning, see
  the [git worktree workflow with DataLad](https://blog.datalad.org/posts/git-worktree-workflow/)
  post.
- `-D/--description` labels this particular copy. git-annex reports that label in
  `whereis` output, so a meaningful description ("scratch on cluster node") is what makes
  copy tracking readable later.

## Retrieving content

```
datalad get [-h] [-s LABEL] [-d PATH] [-r] [-R LEVELS] [-n] [-c PROC] [-D
    DESCRIPTION] [--reckless [auto|ephemeral|shared-...]] [-J NJOBS]
    [--data {anything|nothing|auto|auto-if-wanted}] [--version]
    [PATH ...]
```

- `-r/--recursive` descends into subdatasets, and `-R/--recursion-limit` bounds the depth.
  `-R existing` limits recursion to subdatasets already installed.
- `-n/--no-data` installs subdatasets without fetching any file content. This is the usual
  first move on a nested dataset: get the structure, look at it, then fetch selectively.
- `-s/--source` names a specific sibling to fetch from when several could serve the file.
- `-J/--jobs` parallelises retrieval, and `-J auto` uses the configured maximum. On a
  dataset of many small files this is the difference between minutes and hours.

When resolving where a subdataset lives, DataLad ranks candidate locations by cost,
considering the recorded URL, the superdataset's remote URL, and configured URL templates.
A subdataset that fails to install from its recorded URL can often still be reached
through the superdataset's own hosting.

## Annex content states

Every annexed file has two things that can independently exist:

1. The **pointer**, tracked in Git. It is a symlink into `.git/annex/objects/`, or a small
   plain file containing an annex key on filesystems without symlinks. Deleting it removes
   the file from the dataset.
2. The **content**, the actual bytes. They live in the local annex, on a remote, or both.

| Pointer | Content local | What you see |
|---|---|---|
| present | present | Normal file, readable |
| present | absent | Listed by `ls`, unreadable, restorable with `datalad get` |
| absent | not applicable | Gone from the dataset's working tree |

Inspect the state rather than guessing:

```bash
datalad status --annex           # local content summary for the dataset
git annex whereis <path>         # which repositories hold this file, and how many copies
git annex whereis --json <path>  # same, machine-readable, one JSON object per line
git annex list <path>            # compact matrix of files against remotes
```

`git annex whereis` reports the last information received from remotes and does not
contact them, so a remote that has since lost the file will still be listed. Treat it as a
record of belief, not a live check.

## Editing annexed files

git-annex write-protects annexed content, so a direct write to an annexed file fails with
a permission error even as the owner. That is deliberate: the file's content is
content-addressed and shared by hard link with the annex object, so writing in place would
corrupt every other reference to it.

```bash
datalad unlock <path>            # make it writable
# edit
datalad save -m "revise <path>"  # re-annexes and re-locks
```

Inside `datalad run`, declaring the file with `--output` performs the unlock
automatically, which is why the flag matters beyond documentation.

## Releasing content

```
datalad drop [-h] [--what {filecontent|allkeys|datasets|all}] [--reckless
    {modification|availability|undead|kill}] [-d DATASET] [-r] [-R LEVELS] [-J NJOBS]
    [--nocheck] [--if-dirty IF_DIRTY] [--version] [PATH ...]
```

- `--what filecontent` is the default and drops only file content, leaving pointers and
  the dataset intact.
- `--what allkeys` drops all keys including those not currently in the working tree,
  `--what datasets` uninstalls subdatasets, and `--what all` does both.
- `--reckless availability` overrides the check that another copy exists. This is the
  option that loses data when the check was right.
- `--reckless modification` allows dropping despite unsaved modifications,
  `--reckless undead` proceeds when the annex believes a copy exists somewhere
  unreachable, and `--reckless kill` is a last-resort removal.
- `--nocheck` and `--if-dirty` are deprecated. `--nocheck` is replaced by
  `--reckless availability`; `--if-dirty` is ignored entirely.

The real check is `datalad drop`'s own refusal to remove content it cannot verify
elsewhere; the commands below are a pre-flight look at what `whereis` already believes:

```bash
git annex whereis <path>                                # read the copy list yourself
git annex whereis --json <path> | jq '.whereis | length'  # count known copies
datalad push --to store   # make a second copy where none was, then
datalad drop <path>
```

`whereis` prints one `N copies` line per file, so a pipe into `grep -c 'copies'` returns
the file count, not the copy count — for a single file it always prints `1`, whether the
content exists in five places or nowhere but the local annex. The JSON form is what you
want when a script has to decide.

Never use `rm` or `git rm` on an annexed file to free space. `rm` leaves the pointer
pointing at nothing while the annex object survives, and `git rm` removes the pointer
without dropping the object. Both leave the dataset in a state that has to be repaired
rather than simply reverted.

## Repair and verification

`fsck` belongs to git-annex, not to DataLad, so call it directly:

```bash
git annex fsck                       # verify local content against recorded checksums
git annex fsck --fast                # skip checksum verification, check presence only
git annex fsck --from <remote>       # verify what a remote claims to hold
git annex unused                     # find annex objects no longer referenced
git annex dropunused all             # remove them
```

Run `git annex fsck --from <remote>` after any suspicion that a remote lost data, since it
is the only thing that replaces recorded belief with a live check. Run
`datalad wtf --section dependencies` when behaviour is inconsistent with the documentation,
since an old git-annex is behind a large share of confusing errors; DataLad 1.6 was
released alongside git-annex 10.x and drift from that pairing is the first thing to check.

### `references/provenance.md`

# Computational provenance with DataLad

## Why this is the interesting half

Version control tells you that a file changed. Provenance tells you what produced it, from
what, and with which software. `datalad run` captures all three in the same commit that
carries the change, which means the evidence cannot drift away from the result. `datalad
rerun` then reads that record back and re-executes it, so "is this reproducible" becomes a
command rather than an argument.

## Principles: STAMPED, and the YODA layout it grew out of

YODA ("YODAs Organigram on Data Analysis") is the convention DataLad analyses were
originally built on, and it is still what `datalad create -c yoda` configures. Its three
principles (one thing one dataset, record where the data came from, record what was done
to it) describe what a well-formed analysis looks like, but they were inspirational rather
than operational: there is nothing in them to check a dataset against.

STAMPED (<https://stamped-principles.org>) is the operationalized successor, formalized by
some of the original YODA authors. It states seven properties of a reproducible research
object, each backed by normative MUST/SHOULD/MAY requirements:

| Property | Core requirement |
|---|---|
| **S**elf-contained | Everything essential to replicate the computation is reachable within a single top-level research object |
| **T**racked | Persistent content identification and provenance are recorded for every component and every modification, including the versions involved |
| **A**ctionable | The object carries enough instruction to reproduce all results, specified as *executable* specifications rather than prose |
| **M**odular | Components are organized as independently versioned modules, included directly or linked as subdatasets |
| **P**ortable | Procedures depend on no undocumented host state; environments are explicitly specified and version controlled |
| **E**phemeral | Results are produced in disposable environments built only from the object's own contents |
| **D**istributable | Every referenced module and component is persistently retrievable by others |

**Actionable is the property `datalad run` exists to satisfy.** A README describing how a
figure was produced is documentation; a run record is an executable specification, and
`datalad rerun` is what makes it executable. The same commit satisfies Tracked, because
the command, its inputs, its outputs, and the versions they were taken at are recorded
next to the change rather than in a separate log that can drift away from it. Modular maps
onto subdatasets, Portable and Ephemeral onto `containers-run`, and Distributable onto
siblings and RIA stores (see [publishing.md](publishing.md)).

Two companion resources make this checkable rather than aspirational:
<https://checklist.stamped-principles.org> walks the requirements as a MUST/SHOULD/MAY
checklist, and <https://examples.stamped-principles.org> collects worked patterns,
including ones built directly on `datalad run` and `datalad rerun`.

### The YODA layout in practice

Apply the layout at creation time:

```bash
datalad create -c yoda "my_analysis"
```

That produces:

```text
.
├── .gitattributes
├── CHANGELOG.md
├── code
│   ├── .gitattributes
│   └── README.md
└── README.md
```

The configuration matters more than the directories. Everything in `code/`, plus
`README.md` and `CHANGELOG.md`, is tracked by Git rather than git-annex, so scripts stay
directly readable and diffable in a clone that has fetched no data at all. Input data is
then added as a subdataset:

```bash
datalad clone -d . https://github.com/OpenNeuroDatasets/ds000001.git inputs/raw
```

The `-d .` is what registers the clone as a subdataset of the analysis rather than leaving
an unrelated repository sitting inside it.

## datalad run

```
datalad run [-h] [-d DATASET] [-i PATH] [-o PATH] [--expand {inputs|outputs|both}]
    [--assume-ready {inputs|outputs|both}] [--explicit] [-m MESSAGE]
    [--sidecar {yes|no}] [--dry-run {basic|command}] [-J NJOBS]
    [--version] ...
```

| Option | Documented behaviour | Practical consequence |
|---|---|---|
| `-i/--input PATH` | "A dependency for the run. Before running the command, the content for this relative path will be retrieved." | The command does not fail on an unfetched pointer, and `rerun` knows what to fetch elsewhere |
| `-o/--output PATH` | "Prepare this relative path to be an output file of the command." | Unlocks or removes the target so git-annex write protection does not block the write |
| `--explicit` | "Consider the specification of inputs and outputs to be explicit. Don't warn if the repository is dirty." | Lets a run proceed in a dirty dataset, and saves only the declared outputs |
| `--assume-ready {inputs\|outputs\|both}` | "Assume that inputs do not need to be retrieved and/or outputs do not need to unlocked or removed." | Skips preparation for speed; only safe when you have already done it |
| `--expand {inputs\|outputs\|both}` | "Expand globs when storing inputs and/or outputs in the commit message." | Records the concrete file list rather than the glob, which is what you want when the glob's meaning could change |
| `--dry-run {basic\|command}` | "Do not run the command; just display details about the command execution." | Check placeholder expansion before committing anything |
| `--sidecar {yes\|no}` | Store the run record in a separate file rather than in the commit message | Keeps long records out of `git log` output |

Placeholders available in the command string: `{pwd}` (current working directory),
`{dspath}` (dataset path), `{tmpdir}` (a temporary directory), `{inputs}` and `{outputs}`
(the values of the corresponding flags), and `{inputs[0]}` for indexed access.

Globs are permitted in `--input` and `--output`, and multiple flags may be given:

```bash
datalad run -m "second-level model" \
  -i "derivatives/sub-*/func/*_bold.nii.gz" \
  -i "code/model.py" \
  -o "results/group_map.nii.gz" \
  --expand inputs \
  "python code/model.py {outputs}"
```

### The run record

The commit message carries a machine-readable JSON block between the markers
`=== Do not change lines below ===` and `^^^ Do not change lines above ^^^`. It records
the command, the dataset ID, the exit status, and the input and output specifications. The
handbook is explicit that this section is "less for the human user" and exists "for
DataLad, in particular for the `datalad rerun` command". Editing it by hand, including
during an interactive rebase, breaks `rerun` silently.

Two behaviours that surprise people:

- A run producing no change to the dataset produces no commit at all, exactly as a
  `datalad save` with nothing to save does. An empty history entry is not evidence the run
  failed to execute, only that it changed nothing.
- `datalad run` refuses to start in a dirty dataset. This is the point of the command: a
  record built on an unknown starting state does not establish anything. Save or discard
  first, or state the scope with `--explicit`.

## datalad rerun

```
datalad rerun [-h] [--since SINCE] [-d DATASET] [-b NAME] [-m MESSAGE] [--onto base]
    [--script FILE] [--report] [--assume-ready {inputs|outputs|both}] [--explicit]
    [-J NJOBS] [--version] [REVISION]
```

- `REVISION` selects which recorded command to replay and defaults to `HEAD`.
- `--since SINCE` replays a range: "the commands from all commits that are reachable from
  revision but not SINCE will be re-executed (in other words, the commands in
  `git log SINCE..REVISION`)". This is how a multi-step pipeline is replayed in order.
- `--onto base` gives the "start point for rerunning the commands. If not specified,
  commands are executed at HEAD." Use `--onto ''` to replay from the state each command
  originally ran on.
- `-b/--branch NAME` creates and checks out a branch before replaying.
- `--report` displays what would be done without executing, which is the safe first call.
- `--script FILE` extracts the commands to a file instead of running them, with `-` for
  stdout. This is how a DataLad history becomes a plain shell script for a reviewer or a
  cluster submission.

The reproducibility check worth building into a project:

```bash
datalad rerun --report --since <first-analysis-commit> HEAD    # inspect the plan
datalad rerun -b repro-check --since <first-analysis-commit> HEAD
git diff main repro-check -- results/                          # empty means reproduced
```

Rerunning onto a branch keeps the original results intact while the replay lands
elsewhere, so a mismatch is a finding rather than a lost result.

## Containers

`datalad-container` (PyPI `datalad-container`, currently 1.2.x) records the software
environment alongside the command.

```
datalad containers-add [-h] [-u URL] [-d DATASET] [--call-fmt FORMAT]
    [-i IMAGE] [--update] [--extra-input FILE] [--version] NAME
```

Supported URL schemes:

- `shub://` for Singularity Hub, for example `shub://neurodebian/dcm2niix:latest`.
- `docker://` for Docker images pulled through Singularity, for example
  `docker://debian:stable-slim`.
- `dhub://`, where "the rest of the URL will be interpreted as the argument to
  `docker pull`". Docker execution is configured automatically, mounting the working
  directory to `/tmp` and setting the working directory there.

For `shub://` and `docker://`, a Singularity-based call format is configured
automatically unless `--call-fmt` overrides it. `--call-fmt` is what you change to add
bind mounts, environment variables, or GPU flags that a given image needs.

```
datalad containers-run [-h] [-n NAME] [-d DATASET] [-i PATH] [-o PATH] [-m MESSAGE]
    [--expand {inputs|outputs|both}] [--explicit] [--sidecar {yes|no}] [--version] ...
```

`-n/--name` selects "the name of or a path to a known container to use for execution, in
case multiple containers are configured". With exactly one container configured it may be
omitted. During execution the environment variable `DATALAD_CONTAINER_NAME` holds the name
of the container in use, which is available to the command itself.

The image is tracked in the dataset like any other file, so it is annexed content: a
collaborator gets it with `datalad get` and the provenance record points at a specific
image rather than at a tag someone may have re-pushed.

## Exporting provenance to a standard form

DataLad's run records are DataLad's own format. Converting them to an interoperable
representation is an open area rather than a solved one, and this is worth stating plainly
rather than implying a pipeline exists:

- **W3C PROV** is the standard target for provenance interchange. See
  <https://www.w3.org/TR/prov-overview/>.
- **datalad-metalad** ships a `runprov` extractor that reads DataLad run records, at
  <https://github.com/datalad/datalad-metalad/blob/master/datalad_metalad/extractors/runprov.py>.
  It exists but is not in active use, so treat it as a starting point to validate rather
  than a supported path.
- **BIDS BEP028** is bringing PROV support into the BIDS specification, at
  <https://bids.neuroimaging.io/bep028>. For a BIDS derivatives dataset this is where
  exported provenance would eventually belong.

Until one of those is settled, the durable artifact is the DataLad history itself plus
`datalad rerun --script`, which produces a plain, reviewable command sequence that does
not depend on DataLad to read.

## Further reading

- `datalad run` chapter of the handbook:
  <https://handbook.datalad.org/en/latest/basics/101-108-run.html>
- YODA principles: <https://handbook.datalad.org/en/latest/basics/101-127-yoda.html>
- STAMPED principles (operationalized from YODA): <https://stamped-principles.org>
  - Compliance checklist: <https://checklist.stamped-principles.org>
  - Worked examples and stencils: <https://examples.stamped-principles.org>
- datalad-container documentation:
  <https://docs.datalad.org/projects/container/en/stable/>

### `references/publishing.md`

# Siblings, publishing, and credentials

## The two-target model

A DataLad dataset almost never publishes to one place. The Git history and the annexed
content usually go to different targets, because Git hosting services will not store the
data. The normal shape is a Git sibling plus a storage sibling, with a declared dependency
between them.

Getting this wrong produces the most common broken publication: collaborators clone
successfully, see every file listed, and then find every `datalad get` failing because the
content was never uploaded anywhere reachable.

## Managing siblings

```
datalad siblings [-h] [-d DATASET] [-s NAME] [--url [URL]] [--pushurl PUSHURL]
    [-D DESCRIPTION] [--fetch] [--as-common-datasrc NAME] [--publish-depends SIBLINGNAME]
    [--publish-by-default REFSPEC] [--annex-wanted EXPR] [--annex-required EXPR]
    [--annex-group EXPR] [--annex-groupwanted EXPR] [--inherit] [--no-annex-info]
    [-r] [-R LEVELS] [--version] [{query|add|remove|configure|enable}]
```

Five actions. `query` is the default and reports known siblings. `add` and `configure` are
the same operation except that adding a sibling whose name already exists fails while
reconfiguring does not. `enable` completes access for a git-annex special remote in a
fresh clone. `remove` de-configures a sibling.

Options that carry real consequences:

- `--publish-depends SIBLINGNAME` adds "a dependency such that the given existing sibling
  is always published prior to the new sibling". Set this on the Git sibling, naming the
  storage sibling, and the ordering problem stops being something anyone has to remember.
- `--annex-wanted EXPR` sets a git-annex preferred-content expression for the sibling, for
  example `standard` combined with a group, or `include=*.nii.gz`. `--annex-required`
  makes content mandatory there rather than merely wanted.
- `--pushurl` supplies a separate write URL when the read URL cannot be pushed to, the
  usual case for an HTTPS read path with an SSH write path.
- `--as-common-datasrc NAME` configures a sibling "as a common data source of the dataset
  that can be automatically used by all consumers", which is how a public mirror becomes
  usable by anyone who clones without them configuring anything.
- `--inherit` takes configuration from the superdataset's corresponding sibling, which
  matters when publishing a nested dataset hierarchy.

## Creating siblings

Rather than configuring by hand, use the `create-sibling-*` family, which creates the
remote side and configures the local side together:

| Command                                           | Target                          |
| ------------------------------------------------- | ------------------------------- |
| `datalad create-sibling-github`                   | A GitHub repository             |
| `datalad create-sibling-gitlab`                   | A GitLab project                |
| `datalad create-sibling-gogs` / `-gin` / `-gitea` | GOGS, GIN, and Gitea instances  |
| `datalad create-sibling-ria`                      | A RIA store                     |
| `datalad create-sibling`                          | A generic sibling over SSH      |

The `create-sibling-*` family covers *Git* siblings (a Git remote plus a hosting-service
repository or project) and the RIA layout, which packages a Git remote and a matching
git-annex special remote together. Storage-only targets — S3 buckets, WebDAV, plain SSH
directories, rclone-reachable services — are git-annex *special remotes* rather than Git
remotes, and they are created with `git annex initremote` rather than `create-sibling-*`.
That distinction is what the two-target model turns on: the Git sibling carries history,
the storage sibling carries content, and only in the RIA and GIN cases does one target
carry both.

GIN is worth knowing about in a neuroscience context because it hosts annexed content
directly, which collapses the two-target model back into one target.

## RIA stores

A RIA store is a flat, filesystem-level layout for holding many datasets, designed for
cluster and institutional storage where per-dataset repositories are impractical. Clone
URLs use a `ria+` prefix and a fragment identifying the dataset:

```bash
datalad clone ria+ssh://[user@]hostname/absolute/path/to/ria-store#<dataset-id>
datalad clone ria+file:///home/me/myriastore#e3e70682-c209-4cac-629f-6fbed82c07cd
datalad clone ria+file://$HOME/myriastore#~dl-101
```

The fragment is either the full dataset ID or an alias prefixed with `~`. Aliases exist
because dataset IDs are UUIDs and nobody remembers them.

```bash
datalad create-sibling-ria -s ria-backup --alias dl-101 --new-store-ok \
  "ria+file:///home/me/myriastore"
```

- `--new-store-ok` permits creating the store when it does not already exist. Without it,
  pointing at a nonexistent path is an error rather than a silent creation.
- `--alias` sets the friendly name used in the clone fragment.
- `--storage-sibling` controls the git-annex special remote. `off` disables it, and `only`
  creates the special remote without the regular RIA sibling.
- `--shared` sets multi-user permissions using the values `git init --shared` accepts.

By default the command creates both a regular sibling and a storage sibling named with a
`-storage` suffix.

## Pushing

```
datalad push [-h] [-d DATASET] [--to SIBLING] [--since SINCE] [--data
    {anything|nothing|auto|auto-if-wanted}] [-f
    {all|gitpush|checkdatapresent}] [-r] [-R LEVELS] [-J NJOBS]
    [--version] [PATH ...]
```

`--data` controls annexed content transfer, and the default is `auto-if-wanted`:

| Value | Behaviour |
|---|---|
| `anything` | Transfer all annexed content |
| `nothing` | Skip `git annex copy` entirely, publishing history only |
| `auto` | Use `git annex copy --auto`, so preferred-content settings decide |
| `auto-if-wanted` | Default. Use auto mode only when wanted settings exist on the remote |

The default is the reason a push can succeed while transferring no data: with no
preferred-content configuration on the target, `auto-if-wanted` has nothing to act on.
When a collaborator reports that `get` fails after you pushed, check this before anything
else, and push again with `--data anything`.

`--since SINCE` limits what is considered, and `--since '^'` uses the last known state of
the sibling's branch as the baseline. `-f/--force` accepts `gitpush` (override Git push
safety), `checkdatapresent` (skip the git-annex copy optimisation and transfer regardless
of what the remote is believed to hold), or `all`.

A complete first publication:

```bash
datalad create-sibling-github myaccount/mydataset
git annex initremote store type=S3 bucket=my-bucket encryption=none autoenable=true
datalad siblings configure -s github --publish-depends store
datalad push --to github --data anything -r
```

The Git sibling is created by `datalad create-sibling-github`, the storage sibling by
`git annex initremote`; see the note under "Creating siblings" above for why the two
are not the same tool. `autoenable=true` lets a fresh clone reach the storage sibling
without a manual `enableremote` step, and `encryption=none` is the right default for a
public bucket — turn it on when the content is not intended to be world-readable.

Verify from the other side rather than trusting the push output:

```bash
datalad clone https://github.com/myaccount/mydataset.git /tmp/verify
datalad get -d /tmp/verify <a representative file>
```

## Credentials

DataLad resolves credentials in a defined order and stores interactively entered secrets
through the `keyring` package, using whichever backend that package finds on the system.

Three ways to supply them, in increasing order of automation:

1. **Interactive.** DataLad prompts when a credential is needed and not available, and
   stores the answer in the active keyring backend.
2. **Configuration.** A configuration item `datalad.credential.<name>.<component>` set at
   any DataLad configuration level.
3. **Environment.** "Variable names take the form of `DATALAD_CREDENTIAL_<NAME>_<COMPONENT>`,
   and standard replacement rules into configuration variable names apply." The
   transformation replaces `__` with a hyphen, then `_` with a dot, then lowercases. Keep
   credential names simple and free of underscores so this stays predictable.

Setting `datalad.credentials.force-ask` forces interactive re-entry, overriding a stored
credential with a new value. That is the fix when a rotated key keeps failing because the
old one is still cached.

For git-annex special remotes on a fresh clone, the credential is not enough on its own.
The special remote also has to be enabled locally:

```bash
datalad siblings -d . enable -s store
# or, at the git-annex level
git annex enableremote store
```

A clone that can reach the Git history but reports no available source for content is
usually a special remote that was never enabled, not a missing credential. Check
`git annex info` for the remote's status before assuming an authentication problem.

Never commit credentials into the dataset. The whole point of the dataset is that it gets
published, and a secret in the history is published with it.
