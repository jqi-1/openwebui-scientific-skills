# Scientific Agent Skills for Open WebUI

Makes all **166 skills** from
[`K-Dense-AI/scientific-agent-skills`](https://github.com/K-Dense-AI/scientific-agent-skills)
usable in [Open WebUI](https://openwebui.com) by converting each Agent-Skills
**folder** (`SKILL.md` + references + scripts + assets) into a **single
markdown skill** — Open WebUI's format for storing and importing skills
(a `name` + `description` frontmatter, with the rest of the file as content).

## Contents

- `openwebui/` — the ready-to-import bundle
  - `skills/<id>.md` — 166 importable skills
  - `skills.json` — one-click bulk import (all 166)
  - `manifest.json` — build index (sizes, inlined/excluded files, sha256)
  - [`openwebui/README.md`](openwebui/README.md) — install & usage
- `convert_to_openwebui.py` — the converter (stdlib only)
- `LICENSE.md` — upstream MIT license (derived work)

## One-click install all (no UI clicks)

Open WebUI exposes skills only through `POST /api/v1/skills/create` (one call
per skill) — there is no bulk endpoint, and the official community site imports
**Tools and Functions only, not Skills** (verified in their docs/source; folder
`SKILL.md` support is an unmerged PR [#21275](https://github.com/open-webui/open-webui/pull/21275)).
The built-in **Import JSON** button is the UI's only "install many at once".
For true one-click installs of all 166:

```bash
# API token:
python3 install_to_openwebui.py --url http://localhost:8080 --token <JWT>

# or admin login (script signs in for you):
python3 install_to_openwebui.py --url http://localhost:8080 \
    --email admin@example.com --password '...'
```

Creates all 166 skills via the official API in ~1 second; rerunning is safe
(existing skills skipped). `--dry-run` checks connectivity only.

`install_to_openwebui.py` is stdlib-only and reads `openwebui/skills.json` —
the same payload the built-in **Import JSON** button consumes, so the result
is identical to a manual bulk import.

## Install (UI)

Open an Open WebUI instance, go to **Workspace > Skills > Import JSON**, and
select `openwebui/skills.json`. Individual `.md` files import one at a time;
full per-skill and model-binding walkthroughs are in
[`openwebui/README.md`](openwebui/README.md).

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
