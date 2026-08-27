# Scientific Agent Skills for Open WebUI

Makes all **163 skills** from
[`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills)
usable in [Open WebUI](https://openwebui.com) by converting each Agent-Skills
**folder** (`SKILL.md` + references + scripts + assets) into a **single
markdown skill** — Open WebUI's format for storing and importing skills
(a `name` + `description` frontmatter, with the rest of the file as content).

## Contents

- `openwebui/` — the ready-to-import bundle
  - `skills/<id>.md` — 163 importable skills
  - `skills.json` — one-click bulk import (all 163)
  - `manifest.json` — build index (sizes, inlined/excluded files, sha256)
  - [`openwebui/README.md`](openwebui/README.md) — install & usage
- `convert_to_openwebui.py` — the converter (stdlib only)
- `LICENSE.md` — upstream MIT license (derived work)

## Install

Open an Open WebUI instance, go to **Workspace > Skills > Import JSON**, and
select `openwebui/skills.json`. Individual `.md` files import one at a time.

Full instructions, per-option install guides, fidelity notes, and the
upstream-update workflow are in [`openwebui/README.md`](openwebui/README.md).

## Regenerate after upstream changes

```bash
git clone --depth 1 https://github.com/K-Dense-AI/scientific-agent-skills.git _src
python3 convert_to_openwebui.py
```

## How it works / how Open WebUI skills are made

Open WebUI skills are plain-markdown instruction sets stored in its database:

- Schema (backend `Skill` table): `id` (slug), `name` (display), `description`,
  `content` (the whole markdown), `meta`, `is_active`.
- Import (frontend `Skills.svelte`): reads YAML frontmatter `name`/`description`
  from a `.md` file, slugifies `name` into `id`, stores the whole file as
  `content`; or accepts a JSON array of skill objects via "Import JSON";
  the backend rejects ids not matching `[a-z0-9_-]+`.
- Usage: `$` injects the full content into the prompt; model-attached skills
  inject only the manifest and lazy-load via `view_skill`.
