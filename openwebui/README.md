# Scientific Agent Skills for Open WebUI

All **163 skills** from [`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills)
converted into Open WebUI-compatible skills — single importable markdown
blobs (`name` + `description` frontmatter, body = full instructions).

Source skills are Agent-Skills **folders** (`SKILL.md` + `references/` +
`scripts/` + `assets/`). Open WebUI stores each skill as **one** markdown blob
and has no file tree to hold those siblings, so every sibling file is inlined
as a labelled section (see "Bundled files" at the end of each skill). When a
skill's instructions say "read `references/foo.md`", that content is in the
same document.

## Requirements

- Open WebUI **v0.5.x** or newer (Skills workspace; `view_skill` lazy loading for
  model-attached skills requires native function calling).

## Installation (choose one)

### Option A — bulk import (all 163 at once, recommended)

1. Open **Workspace > Skills**.
2. Click **Import JSON** (in the workspace header).
3. Select [`skills.json`](skills.json).

Every skill is created immediately (no per-skill confirmation). Shows up as
163 skills, each sharing the id/name of its upstream folder (e.g. `scanpy`,
`database-lookup`).

### Option B — import individual `.md` files

Each file under [`skills/`](skills/) imports through **Workspace > Skills >
Import** (select one `.md` at a time). Open WebUI reads the frontmatter
(`name`/`description`), pre-fills the editor; press **Save**.

### Option C — attach to a model

1. **Workspace > Skills** and ensure the wanted skills exist (A or B).
2. **Workspace > Models** → edit a model → **Skills** → select skills → **Save**.

Only the manifest (name + description) is injected; full instructions load
on-demand via `view_skill`.

## After importing

- Type `$` in chat to inject a skill, or use the **+ Integrations** menu for a
  per-chat toggle.
- `Workspace > Skills > Export` round-trips to the same JSON shape as
  [`skills.json`](skills.json).
- Remember skills still require read access for the user (default: private).

## What was converted

| | |
|---|---|
| Source | K-Dense `scientific-agent-skills` v2.64.0 (repo `main`) |
| Skill count | 163 |
| Converted files | `skills/<id>.md` (163) |
| Bulk import | `skills.json` (163 skills) |
| Build index | `manifest.json` (sizes, inlined/excluded files, sha256) |

### Fidelity notes

- `SKILL.md` is preserved verbatim (only its `name`/`description` move to the
  Open WebUI frontmatter; `license`, `metadata`, `allowed-tools` etc. were
  dropped because Open WebUI ignores them).
- `references/*.md`, `scripts/*.py`, and small `assets/` are inlined as fenced
  sections; code is documentation — execute it in an environment the model can
  reach (Open Terminal / Code Interpreter), it is never run by Open WebUI.
- Excluded (cannot be used as inline text, listed in each skill body):
  binary assets, archives, vendored `.xsd` schemas, and data dumps over
  200 KB (`bids/references/bids_schema.json`, `onekgpd/assets/kgpe.json`).

### Updating

Re-run the converter from this repository root to regenerate the bundle after
upstream changes:

```bash
git clone --depth 1 https://github.com/K-Dense-AI/scientific-agent-skills.git _src
python3 convert_to_openwebui.py
```

Requires only Python 3 stdlib.
