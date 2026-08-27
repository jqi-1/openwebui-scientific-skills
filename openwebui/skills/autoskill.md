---
name: autoskill
description: Optional Foundry access for drafting.
---

# autoskill

> **Requires a running [screenpipe](https://github.com/screenpipe/screenpipe) daemon.** This skill has no alternate data source — it reads exclusively from the local screenpipe HTTP API (default `http://localhost:3030`). If the daemon isn't running, `run()` raises `ScreenpipeUnreachable` with install instructions.

> **Network access & environment variables.** This skill makes authenticated HTTP requests to (a) the user's local screenpipe daemon on loopback, and (b) the user-configured LLM backend — one of `http://localhost:1234/v1` (LM Studio, default), `https://api.anthropic.com` (opt-in Claude), or a user-supplied BYOK Foundry gateway. The skill reads three environment variables — `SCREENPIPE_TOKEN`, `ANTHROPIC_API_KEY`, `FOUNDRY_API_KEY` — and uses each only to authenticate to the single endpoint its name implies. No other network destinations, no telemetry, no data egress to any third party.

## Overview

Turn the user's own workflow history — captured passively by the local [screenpipe](https://github.com/screenpipe/screenpipe) daemon — into new skills. This skill is on-demand: the user invokes it with a time window, it queries screenpipe's local HTTP API, clusters repeated workflow patterns, compares each pattern against the existing skills in this repo, and produces a staged folder of proposals the user can review, edit, and promote.

## When to Use This Skill

Invoke this skill when the user asks to:
- "Analyze my last 4 hours / day / week and propose new skills."
- "Look at what I've been doing and tell me what's not covered yet."
- "Draft a skill from my recent workflow."
- "Find composition recipes for workflows I repeat."

Do **not** invoke it for one-off questions about screenpipe itself, for real-time screen queries, or without an explicit user request — the skill analyzes sensitive local content and must stay explicitly user-triggered.

## Privacy Posture

- **Screenpipe handles app/window filtering at capture time.** Install a starter deny-list by copying `references/screenpipe-config.yaml` into the user's screenpipe config. Sensitive apps (password managers, messaging, banking) are never OCR'd in the first place.
- **Raw OCR never leaves the machine.** `scripts/fetch_window.py` pulls data over localhost HTTP. `scripts/cluster.py` reduces the timeline to app/duration/title summaries. `scripts/redact.py` strips emails, API keys, bearer tokens, and phone numbers as defense-in-depth before any cluster summary reaches the LLM.
- **LLM backend defaults to `local`.** The recommended setup is [LM Studio](https://lmstudio.ai/) running `Gemma-4-31B-it` — strong reasoning at a size that fits on most workstation GPUs, and no data ever leaves your machine. Cloud backends (`claude`, `foundry`) are opt-in and documented in `config.yaml` for users who explicitly want them. Detection and embeddings always run locally regardless of backend choice.
- **Dry-run mode** (`--plan`) prints the exact timeline that will be analyzed before any LLM call.
- **TLS for localhost** (optional, for corporate policy): see `references/https-proxy.md` for the Caddy pattern.

## Prerequisites

### 1. Screenpipe daemon

Either install the official release or build from source. Either way the daemon binds HTTP on `localhost:3030` by default.

**From source** (recommended if you want the CLI daemon without the desktop GUI):

```bash
git clone --depth 1 https://github.com/mediar-ai/screenpipe.git
cd screenpipe
cargo build -p screenpipe-engine --release
# System deps (macOS): cmake + full Xcode.app (not just Command Line Tools).
#   brew install cmake
#   # if xcodebuild plug-ins error: sudo xcodebuild -runFirstLaunch
./target/release/screenpipe doctor   # confirm permissions + ffmpeg
./target/release/screenpipe record --disable-audio --use-pii-removal
```

First run will prompt for macOS Screen Recording permission. Grant it and relaunch.

### 2. Screenpipe API token

The local API now requires bearer auth. Retrieve your token and export it:

```bash
export SCREENPIPE_TOKEN=$(screenpipe auth token)
```

(Or set `screenpipe.token` directly in `config.yaml` — env var is preferred since it keeps secrets out of version control.)

### 3. Python environment

Via `pipenv` from the repo root:

```bash
pipenv install httpx pyyaml sentence-transformers
```

The embedding model (`sentence-transformers/all-MiniLM-L6-v2`, ~80 MB) downloads on first run.

### 4. Local LLM (default path) — LM Studio

- Install [LM Studio](https://lmstudio.ai/).
- Download `Gemma-4-31B-it` (or another strong reasoning model; adjust `local.model` in `config.yaml`).
- Load it via the CLI for headless use (no GUI required):

```bash
lms load gemma-4-31b-it --context-length 131072 --gpu max -y
lms status   # confirm server running on :1234
```

### 5. Cloud LLM backends (optional, opt-in)

Only if you explicitly opt out of local:
- `claude`: set `ANTHROPIC_API_KEY`, flip `backend: claude` in `config.yaml`.
- `foundry`: set `FOUNDRY_API_KEY`, flip `backend: foundry`, set `foundry.endpoint` to your corporate gateway URL.

## Architecture

```
screenpipe daemon (user-installed)
        │  HTTP on localhost:3030
        ▼
scripts/fetch_window.py    → normalized timeline events
scripts/redact.py          → regex scrub (defense-in-depth)
scripts/cluster.py         → sessions + clusters (local only)
scripts/match_skills.py    → top-k vs existing 135 skills (local embeddings)
scripts/synthesize.py      → LLM judge: reuse / compose / novel
        │
        ▼
~/.autoskill/proposed/<timestamp>/        (default; override with --out)
  ├── report.md
  ├── composition-recipes/<name>/SKILL.md
  └── new-skills/<name>/SKILL.md

scripts/promote.py         → user-approved proposal → skills/<name>/
```

## Workflow

The skill ships a unified CLI at `scripts/autoskill.py` with three subcommands:

```bash
python scripts/autoskill.py doctor   --config config.yaml --skills-dir ../
python scripts/autoskill.py run      --start ... --end ... --config config.yaml
python scripts/autoskill.py promote  --proposed ~/.autoskill/proposed/<ts> --skills-dir ../ --name <skill>
```

### 0. Preflight with `doctor`

Before a full run, verify every dependency in one shot:

```bash
python scripts/autoskill.py doctor \
  --config skills/autoskill/config.yaml \
  --skills-dir skills
```

The report covers `config` (backend choice valid), `skills_dir` (exists), `screenpipe` (reachable + authed), and `llm` (LM Studio serving or API key present). Non-zero exit on any failure, with the offending line marked `error`.

### 1. Run the pipeline

```bash
export SCREENPIPE_TOKEN=$(screenpipe auth token)
python scripts/autoskill.py run \
  --start "2026-04-17T00:00:00Z" \
  --end   "2026-04-17T23:59:59Z" \
  --config skills/autoskill/config.yaml \
  --skills-dir skills
```

Proposals land in `~/.autoskill/proposed/<timestamp>/` by default, keeping experimental output out of the skills repo. Pass `--out PATH` to override.

Internally:
1. **Fetch** — `fetch_window` paginates screenpipe's `/search` endpoint, normalizes events to `{ts, app, window_title, text, content_type}`.
2. **Redact** — `redact` scrubs emails, API keys, bearer tokens, phones from OCR text and window titles as defense-in-depth over screenpipe's own PII removal.
3. **Cluster** — `segment_sessions` splits on idle gaps (default 10 min) and drops short sessions; `cluster_sessions` groups sessions by app-signature and keeps clusters of size `min_cluster_size` (default 2).
4. **Match** — `load_skill_descriptions` reads frontmatter from every `SKILL.md` in `skills/`; `top_k_matches` ranks each cluster against all skills using local `sentence-transformers` embeddings (cosine similarity).
5. **Synthesize** — `synthesize` prompts the configured LLM backend to classify each cluster as `reuse`, `compose`, or `novel` and emit a SKILL.md body where appropriate.
6. **Report** — writes `<out_dir>/<ts>/report.md`, plus `new-skills/<name>/SKILL.md` or `composition-recipes/<name>/SKILL.md` for each proposal.

Add `--dry-run` to stop after clustering; this skips the LLM (and the sentence-transformers load), writing only `plan.md` for inspection.

### 2. Review and promote

Open `~/.autoskill/proposed/<ts>/report.md`, edit drafts in place, delete anything you don't want. Then:

```bash
python scripts/autoskill.py promote \
  --proposed ~/.autoskill/proposed/2026-04-17T14-30-00 \
  --skills-dir skills \
  --name zotero-pubmed-helper
```

`promote` moves the directory into `skills/<name>/`, refusing to overwrite an existing skill. Exits non-zero with a friendly error if the proposal isn't found or the target already exists.

## Configuration

See `config.yaml` for the full shape. Default values (local-first):

```yaml
backend: local
local:
  endpoint: http://localhost:1234/v1   # LM Studio's Developer server
  model: Gemma-4-31B-it

screenpipe:
  url: http://localhost:3030           # or https://screenpipe.local via Caddy

cluster:
  min_session_minutes: 5
  idle_gap_minutes: 10
  min_cluster_size: 2
```

To opt into a cloud backend:

```yaml
backend: claude                         # or foundry
claude:
  model: claude-opus-4-7
```

## Composition recipes vs new skills

- **compose**: the LLM judged that chaining existing skills covers the workflow. The emitted SKILL.md is intentionally thin — frontmatter + a "Workflow" section that invokes existing skills in order. The same agent runtime that discovered the skill can then invoke it end-to-end.
- **novel**: no combination of existing skills covers it. A fuller SKILL.md is drafted, still following repo conventions (frontmatter, Overview, When to Use, Workflow). The user should always review new-skill drafts before promoting.

## Testing

The skill is covered by a small pytest suite at `tests/autoskill/` in the repository root. Each script is unit-tested in isolation with dependency injection (mock HTTP transport, stub backend, stub embedder):

```bash
python -m pytest tests/autoskill -v
```

## Composition with other skills in this repo

The autoskill's embedding index covers all 135 sibling skills. Workflows that look like scientific writing will match `scientific-writing` / `literature-review` / `citation-management`; figure work will match `scientific-schematics` / `generate-image` / `infographics`; slide prep matches `scientific-slides` / `pptx`; etc. When a cluster scores high against two or three sibling skills the emitted composition recipe names them explicitly, so the user's future agent invocations use the optimized paths already documented in this repo.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/autoskill/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/https-proxy.md`

# Optional: TLS for localhost screenpipe access

Screenpipe's HTTP server (Axum, binding `localhost:3030`) speaks plain HTTP. For a Python script running as the same user on the same host, plain HTTP is adequate — loopback traffic never hits a network adapter, so TLS provides no additional confidentiality.

TLS on localhost is only useful when:

- A corporate security policy mandates "TLS everywhere" regardless of transport.
- The screenpipe endpoint is tunneled or exposed off-host.
- A browser client requires a "secure context" (Service Workers, WebCrypto).

If you need it, put a one-line Caddy reverse proxy in front. Caddy's `tls internal` generates and trusts a local CA automatically.

## Caddy

Install:

```bash
brew install caddy   # macOS
# or see https://caddyserver.com/docs/install
```

Add to your `Caddyfile`:

```caddyfile
screenpipe.local {
    tls internal
    reverse_proxy localhost:3030
}
```

Ensure `screenpipe.local` resolves to loopback (add to `/etc/hosts`):

```
127.0.0.1   screenpipe.local
```

Start Caddy:

```bash
caddy run
```

Then update autoskill's `config.yaml`:

```yaml
screenpipe:
  url: https://screenpipe.local
```

No code change is required on the autoskill side. `httpx` handles both HTTP and HTTPS transparently.

## mkcert (alternative)

If you prefer managing the cert yourself instead of Caddy's internal CA:

```bash
brew install mkcert
mkcert -install
mkcert localhost 127.0.0.1
```

Then terminate TLS with nginx, Caddy, or stunnel using the generated cert.

### `references/screenpipe-config.yaml`

```yaml
# Starter screenpipe configuration for autoskill users.
#
# Copy the relevant sections into your screenpipe config (or pass as CLI
# flags when starting the daemon). Screenpipe handles app/window filtering
# at capture time — sensitive apps on this list will never be OCR'd, so
# their content never reaches autoskill's pipeline.
#
# Reference: https://github.com/screenpipe/screenpipe
#
# Review and edit for your setup. This is a conservative baseline, not
# an exhaustive list. Add any app where you handle secrets.

ignored_apps:
  # Password managers
  - "1Password"
  - "Bitwarden"
  - "Dashlane"
  - "Keeper"
  - "LastPass"
  - "KeePassXC"

  # Private messaging
  - "Signal"
  - "Telegram"
  - "WhatsApp"
  - "iMessage"
  - "Messages"

  # Mail composition (inbound reading is fine; composition often contains secrets)
  # Remove if you explicitly want mail workflows analyzed.
  - "Mail"
  - "Outlook"

  # Banking / finance apps (add yours)
  # - "Bank of America"
  # - "Chase"

# Window title globs to ignore (matched across all apps).
# Useful for catching sensitive URLs in browsers that are otherwise OK to observe.
ignored_windows:
  - "*Bitwarden*"
  - "*1Password*"
  - "*login*"
  - "*Sign in*"
  - "*Private Browsing*"
  - "*Incognito*"
  - "*online banking*"
  - "*bank*"
  - "*account settings*"

# Optionally restrict capture to specific hours (local time).
# Uncomment to apply.
# hours:
#   start: "09:00"
#   end:   "19:00"

# Content types to capture. Drop "audio" if you don't want transcripts.
content_types:
  - ocr
  - ui
  # - audio
```

### `scripts/autoskill.py`

```python
"""Unified CLI for the autoskill skill.

Subcommands:
  run      — detect workflows and draft proposed skills
  doctor   — verify screenpipe + LM Studio + config + skills dir
  promote  — move an approved proposal into skills/
"""

import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(prog="autoskill", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["run", "doctor", "promote"],
                        help="subcommand to run")
    parser.add_argument("rest", nargs=argparse.REMAINDER,
                        help="arguments forwarded to the subcommand")
    args = parser.parse_args(argv)

    if args.command == "run":
        import run as _run
        return _run.main(args.rest)
    if args.command == "doctor":
        import doctor as _doctor
        return _doctor.main(args.rest)
    if args.command == "promote":
        import promote as _promote
        return _promote.main(args.rest)
    raise AssertionError(f"unreachable: {args.command!r}")


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/backends.py`

```python
import ipaddress
import os
import sys
from urllib.parse import urlparse

import httpx


def _is_loopback(host):
    if host in ("localhost", ""):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def check_remote_endpoint(endpoint, label):
    """Reject cleartext transport to a remote host, and name the destination.

    This backend sends summaries derived from the user's screen-capture history.
    The endpoint is read from config.yaml, so it is worth being explicit about
    where that data is about to go, and refusing to send it -- along with an API
    key header -- over plaintext HTTP to anything but the local machine.
    """
    parsed = urlparse(endpoint)
    host = parsed.hostname or ""

    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"{label} endpoint must be an http:// or https:// URL, got {endpoint!r}"
        )

    if parsed.scheme == "http" and not _is_loopback(host):
        raise ValueError(
            f"{label} endpoint {endpoint!r} uses plaintext HTTP to a remote host. "
            "Screen-derived content and your API key would cross the network "
            "unencrypted. Use https://, or point the endpoint at localhost."
        )

    if not _is_loopback(host):
        print(
            f"[autoskill] sending screen-derived summaries to {parsed.scheme}://{host}",
            file=sys.stderr,
        )

    return endpoint


class ClaudeBackend:
    def __init__(self, api_key, model, client=None):
        self.api_key = api_key
        self.model = model
        self.client = client or httpx.Client(base_url="https://api.anthropic.com", timeout=60.0)

    def __call__(self, prompt):
        response = self.client.post(
            "/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["content"][0]["text"]


class LocalBackend:
    def __init__(self, endpoint, model, client=None):
        self.endpoint = endpoint
        self.model = model
        self.client = client or httpx.Client(base_url=endpoint, timeout=120.0)

    def __call__(self, prompt):
        response = self.client.post(
            "/chat/completions",
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]


def make_backend(config):
    kind = config.get("backend")
    if kind == "claude":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")
        model = config.get("claude", {}).get("model", "claude-opus-4-7")
        return ClaudeBackend(api_key=api_key, model=model)

    if kind == "foundry":
        api_key = os.environ.get("FOUNDRY_API_KEY")
        if not api_key:
            raise RuntimeError("FOUNDRY_API_KEY environment variable not set")
        f = config.get("foundry", {})
        endpoint = check_remote_endpoint(f["endpoint"], "foundry")
        client = httpx.Client(base_url=endpoint, timeout=60.0)
        return ClaudeBackend(api_key=api_key, model=f.get("model", "claude-opus-4-7"), client=client)

    if kind == "local":
        l = config.get("local", {})
        return LocalBackend(endpoint=check_remote_endpoint(l["endpoint"], "local"), model=l["model"])

    raise ValueError(f"unknown backend: {kind!r}")
```

### `scripts/cluster.py`

```python
from collections import defaultdict


def segment_sessions(events, idle_gap_seconds, min_session_seconds):
    if not events:
        return []
    events = sorted(events, key=lambda e: e["ts"])
    groups = [[events[0]]]
    for prev, curr in zip(events, events[1:]):
        if curr["ts"] - prev["ts"] > idle_gap_seconds:
            groups.append([curr])
        else:
            groups[-1].append(curr)

    sessions = []
    for group in groups:
        duration = group[-1]["ts"] - group[0]["ts"]
        if duration < min_session_seconds:
            continue
        apps, seen = [], set()
        for evt in group:
            if evt["app"] not in seen:
                seen.add(evt["app"])
                apps.append(evt["app"])
        sessions.append({
            "start_ts": group[0]["ts"],
            "end_ts": group[-1]["ts"],
            "duration_seconds": duration,
            "apps": apps,
            "window_titles": [e["window_title"] for e in group if e.get("window_title")],
        })
    return sessions


def cluster_sessions(sessions, min_cluster_size):
    buckets = defaultdict(list)
    for s in sessions:
        buckets[tuple(s["apps"])].append(s)

    clusters = []
    for apps, members in buckets.items():
        if len(members) < min_cluster_size:
            continue
        example_titles = []
        for m in members:
            if m["window_titles"]:
                example_titles.append(m["window_titles"][0])
        clusters.append({
            "apps": list(apps),
            "session_count": len(members),
            "total_duration_seconds": sum(m["duration_seconds"] for m in members),
            "example_titles": example_titles,
        })
    return clusters
```

### `scripts/doctor.py`

```python
import argparse
import os
import sys
from pathlib import Path

import httpx

_VALID_BACKENDS = {"local", "claude", "foundry"}


def default_screenpipe_probe(config):
    sp = config.get("screenpipe", {})
    url = sp.get("url", "http://localhost:3030")
    token = sp.get("token") or os.environ.get("SCREENPIPE_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = httpx.get(f"{url}/health", headers=headers, timeout=5.0)
        if r.status_code == 200:
            return ("ok", url)
        return ("error", f"{url} returned HTTP {r.status_code}")
    except httpx.HTTPError as e:
        return ("error", f"{url}: {e}")


def default_llm_probe(config):
    kind = config.get("backend")
    if kind == "local":
        endpoint = config.get("local", {}).get("endpoint", "http://localhost:1234/v1")
        try:
            r = httpx.get(f"{endpoint}/models", timeout=5.0)
            if r.status_code == 200:
                return ("ok", endpoint)
            return ("error", f"{endpoint} returned HTTP {r.status_code}")
        except httpx.HTTPError as e:
            return ("error", f"{endpoint}: {e}")
    if kind == "claude":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return ("error", "ANTHROPIC_API_KEY not set")
        return ("ok", "ANTHROPIC_API_KEY present (not probed)")
    if kind == "foundry":
        if not os.environ.get("FOUNDRY_API_KEY"):
            return ("error", "FOUNDRY_API_KEY not set")
        return ("ok", "FOUNDRY_API_KEY present (not probed)")
    return ("error", f"unknown backend: {kind!r}")


def check(config, *, skills_dir, screenpipe_probe, llm_probe):
    result = {}

    kind = config.get("backend")
    if kind in _VALID_BACKENDS:
        result["config"] = ("ok", f"backend={kind}")
    else:
        result["config"] = ("error", f"unknown backend: {kind!r}")

    skills_dir = Path(skills_dir)
    if skills_dir.is_dir():
        result["skills_dir"] = ("ok", str(skills_dir))
    else:
        result["skills_dir"] = ("error", f"not a directory: {skills_dir}")

    result["screenpipe"] = screenpipe_probe(config)
    result["llm"] = llm_probe(config)
    return result


def _format_report(result: dict) -> str:
    lines = ["autoskill doctor", "================"]
    for key in ("config", "skills_dir", "screenpipe", "llm"):
        status, detail = result[key]
        lines.append(f"  {key:12s}: {status:5s}  {detail}")
    return "\n".join(lines)


def main(argv=None):
    import yaml

    parser = argparse.ArgumentParser(
        prog="autoskill-doctor",
        description="Check that screenpipe, LM Studio, config, and skills dir are ready.",
    )
    parser.add_argument("--config", required=True,
                        help="path to autoskill config.yaml")
    parser.add_argument("--skills-dir", required=True,
                        help="path to skills/")
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text())
    result = check(
        config,
        skills_dir=args.skills_dir,
        screenpipe_probe=default_screenpipe_probe,
        llm_probe=default_llm_probe,
    )

    report = _format_report(result)
    print(report)

    any_error = any(status == "error" for status, _ in result.values())
    if any_error:
        print("\ndoctor: one or more checks failed", file=sys.stderr)
        return 1
    print("\ndoctor: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/fetch_window.py`

```python
_MAX_PAGES = 10_000  # bounded exit: hard ceiling so the loop cannot spin forever


def fetch_window(client, start_time, end_time, page_size=50, token=None):
    events = []
    offset = 0
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    for _page in range(_MAX_PAGES):
        response = client.get("/search", params={
            "start_time": start_time,
            "end_time": end_time,
            "limit": page_size,
            "offset": offset,
        }, headers=headers)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", [])
        total = payload.get("pagination", {}).get("total", 0)

        for item in data:
            content = item.get("content", {})
            events.append({
                "ts": content.get("timestamp"),
                "app": content.get("app_name", ""),
                "window_title": content.get("window_name", ""),
                "text": content.get("text", ""),
                "content_type": item.get("type", "").lower(),
            })

        offset += len(data)
        if not data or offset >= total:
            break
    return events
```

### `scripts/match_skills.py`

```python
import math
from pathlib import Path


def _parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    _, _, rest = content.partition("---\n")
    block, _, _ = rest.partition("\n---")
    out = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def load_skill_descriptions(skills_dir):
    skills_dir = Path(skills_dir)
    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        fm = _parse_frontmatter(skill_md.read_text())
        if "name" in fm and "description" in fm:
            skills.append({"name": fm["name"], "description": fm["description"]})
    return skills


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def top_k_matches(query, skills, embedder, k):
    q = embedder(query)
    scored = [
        {"name": s["name"], "description": s["description"],
         "score": _cosine(q, embedder(s["description"]))}
        for s in skills
    ]
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:k]
```

### `scripts/promote.py`

```python
import argparse
import shutil
import sys
from pathlib import Path


class PromoteError(Exception):
    pass


_KINDS = ("new-skills", "composition-recipes")


def promote(proposed_path, skills_dir, name):
    proposed_path = Path(proposed_path)
    skills_dir = Path(skills_dir)

    source = None
    for kind in _KINDS:
        candidate = proposed_path / kind / name
        if candidate.is_dir():
            source = candidate
            break
    if source is None:
        raise PromoteError(f"proposed skill {name!r} not found under {proposed_path}")

    target = skills_dir / name
    if target.exists():
        raise PromoteError(f"target {target} already exists")

    shutil.move(str(source), str(target))
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="autoskill-promote",
        description="Move a proposed skill from _proposed/<ts>/ into skills/",
    )
    parser.add_argument("--proposed", required=True,
                        help="path to the _proposed/<ts>/ directory")
    parser.add_argument("--skills-dir", required=True,
                        help="path to skills/")
    parser.add_argument("--name", required=True, help="skill name to promote")
    args = parser.parse_args(argv)

    try:
        target = promote(args.proposed, args.skills_dir, args.name)
    except PromoteError as e:
        print(f"promote failed: {e}", file=sys.stderr)
        return 1

    print(f"promoted: {args.name} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/redact.py`

```python
import re

# Order matters: multi-line and prefixed patterns run before narrower ones.
_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]*?-----END [A-Z ]+PRIVATE KEY-----"),
     "[REDACTED:private_key]"),

    # Known-env-var secret assignments: NAME=value  (catches long values only)
    (re.compile(
        r"\b(?:AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID|GITHUB_TOKEN|HF_TOKEN"
        r"|ANTHROPIC_API_KEY|OPENAI_API_KEY|FOUNDRY_API_KEY|SCREENPIPE_TOKEN"
        r"|GOOGLE_API_KEY|SLACK_TOKEN|DEEPGRAM_API_KEY)"
        r"\s*=\s*[^\s\"']+"
    ), "[REDACTED:kv_secret]"),

    (re.compile(r"Bearer\s+[A-Za-z0-9_\-\.=]+"), "[REDACTED:bearer]"),

    (re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),
     "[REDACTED:jwt]"),

    (re.compile(r"\bxox[bpars]-[A-Za-z0-9\-]{10,}"), "[REDACTED:api_key]"),
    (re.compile(r"\bhf_[A-Za-z0-9]{32,}"), "[REDACTED:api_key]"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), "[REDACTED:api_key]"),
    (re.compile(r"\b(?:sk|pk|rk)_live_[A-Za-z0-9]{24,}"), "[REDACTED:api_key]"),
    (re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "[REDACTED:api_key]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[REDACTED:api_key]"),
    (re.compile(r"\bAIza[A-Za-z0-9_\-]{35}\b"), "[REDACTED:api_key]"),

    (re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
     "[REDACTED:email]"),

    (re.compile(r"\(\d{3}\)\s*\d{3}-\d{4}"), "[REDACTED:phone]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED:ssn]"),
]


def redact(text: str) -> str:
    for pattern, placeholder in _PATTERNS:
        text = pattern.sub(placeholder, text)
    return text
```

### `scripts/run.py`

```python
import datetime as _dt
from pathlib import Path

import httpx

from cluster import cluster_sessions, segment_sessions
from fetch_window import fetch_window
from match_skills import load_skill_descriptions, top_k_matches
from redact import redact
from synthesize import synthesize


class ScreenpipeUnreachable(RuntimeError):
    """Raised when the screenpipe daemon cannot be reached.

    The autoskill skill cannot run without screenpipe. Install it from
    https://github.com/screenpipe/screenpipe and start the daemon before
    invoking this skill.
    """


def _default_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")


def _cluster_query(cluster: dict) -> str:
    parts = ["apps: " + ", ".join(cluster["apps"])]
    if cluster.get("example_titles"):
        parts.append("titles: " + "; ".join(cluster["example_titles"]))
    return " | ".join(parts)


def _write_plan(proposed_path: Path, clusters: list[dict]) -> None:
    lines = ["# Dry-run plan", ""]
    for i, c in enumerate(clusters, 1):
        lines += [
            f"## Cluster {i}",
            f"- apps: {', '.join(c['apps'])}",
            f"- sessions: {c['session_count']}",
            f"- total_duration_seconds: {c['total_duration_seconds']}",
            f"- example titles: {'; '.join(c.get('example_titles', []))}",
            "",
        ]
    (proposed_path / "plan.md").write_text("\n".join(lines))


def _write_report(proposed_path: Path, results: list[dict]) -> None:
    lines = ["# autoskill report", ""]
    if not results:
        lines.append("No clusters met the minimum size threshold. Nothing to propose.")
    for r in results:
        c = r["cluster"]
        lines += [
            f"## {', '.join(c['apps'])} — {c['session_count']}× ({c['total_duration_seconds']}s)",
            f"- verdict: **{r['verdict']}**",
        ]
        if r["verdict"] == "reuse":
            lines.append(f"- matched skill: `{r['target']}`")
        else:
            lines.append(f"- draft: `{r['draft_path']}`")
        lines.append("- top matches:")
        for s in r["top_k"]:
            lines.append(f"  - `{s['name']}` (score={s['score']:.2f})")
        lines.append("")
    (proposed_path / "report.md").write_text("\n".join(lines))


def run(config, *, start_time, end_time, out_dir,
        screenpipe_client, backend, embedder, skills_dir,
        screenpipe_token=None, now=None, dry_run=False):
    now = now or _default_now
    try:
        events = fetch_window(screenpipe_client, start_time, end_time,
                              token=screenpipe_token)
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        base = getattr(screenpipe_client, "base_url", "http://localhost:3030")
        raise ScreenpipeUnreachable(
            f"cannot reach screenpipe at {base}: {e}. "
            "Install and start the daemon — see "
            "https://github.com/screenpipe/screenpipe — "
            "or point config.yaml's screenpipe.url at your instance."
        ) from e

    for e in events:
        e["text"] = redact(e.get("text", ""))
        e["window_title"] = redact(e.get("window_title", ""))

    cluster_cfg = config.get("cluster", {})
    idle_gap = cluster_cfg.get("idle_gap_minutes", 10) * 60
    min_session = cluster_cfg.get("min_session_minutes", 5) * 60
    min_cluster = cluster_cfg.get("min_cluster_size", 2)

    # fetch_window returns ts as ISO strings; convert to epoch for segmentation
    for e in events:
        if isinstance(e["ts"], str):
            e["ts"] = int(_dt.datetime.fromisoformat(e["ts"].replace("Z", "+00:00")).timestamp())

    sessions = segment_sessions(events, idle_gap_seconds=idle_gap, min_session_seconds=min_session)
    clusters = cluster_sessions(sessions, min_cluster_size=min_cluster)

    proposed_path = Path(out_dir) / now()
    proposed_path.mkdir(parents=True, exist_ok=True)

    if dry_run:
        _write_plan(proposed_path, clusters)
        return proposed_path

    if not clusters:
        _write_report(proposed_path, [])
        return proposed_path

    skills = load_skill_descriptions(Path(skills_dir))
    results = []
    for cluster in clusters:
        query = _cluster_query(cluster)
        top_k = top_k_matches(query, skills, embedder=embedder, k=5)
        decision = synthesize(cluster, top_k, backend=backend)

        entry = {"cluster": cluster, "top_k": top_k, "verdict": decision["verdict"]}
        if decision["verdict"] == "reuse":
            entry["target"] = decision.get("target")
        else:
            kind = "new-skills" if decision["verdict"] == "novel" else "composition-recipes"
            name = decision["name"]
            draft_dir = proposed_path / kind / name
            draft_dir.mkdir(parents=True)
            (draft_dir / "SKILL.md").write_text(decision["skill_body"])
            entry["draft_path"] = str(draft_dir.relative_to(proposed_path))
        results.append(entry)

    _write_report(proposed_path, results)
    return proposed_path


def main(argv=None):
    import argparse
    import sys

    import httpx
    import yaml

    from backends import make_backend

    parser = argparse.ArgumentParser(prog="autoskill")
    parser.add_argument("--start", required=True, help="ISO start time, e.g. 2026-04-17T00:00:00Z")
    parser.add_argument("--end", required=True, help="ISO end time")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parent.parent / "config.yaml"))
    parser.add_argument("--out", default=None,
                        help="output directory for proposals (default: ~/.autoskill/proposed)")
    parser.add_argument("--skills-dir", default=None,
                        help="path to skills/ (default: parent of this skill's dir)")
    parser.add_argument("--dry-run", action="store_true",
                        help="stop after clustering; do not call the LLM backend")
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text())

    here = Path(__file__).resolve()
    skills_dir = Path(args.skills_dir) if args.skills_dir else here.parent.parent.parent
    out_dir = Path(args.out) if args.out else Path.home() / ".autoskill" / "proposed"

    import os
    screenpipe_cfg = config.get("screenpipe", {})
    screenpipe_url = screenpipe_cfg.get("url", "http://localhost:3030")
    screenpipe_token = (screenpipe_cfg.get("token")
                        or os.environ.get("SCREENPIPE_TOKEN"))
    screenpipe_client = httpx.Client(base_url=screenpipe_url, timeout=60.0)

    if args.dry_run:
        backend = None
        embedder = None
    else:
        backend = make_backend(config)
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(
            config.get("embeddings", {}).get("model", "sentence-transformers/all-MiniLM-L6-v2")
        )

        def embedder(text: str):
            return list(map(float, model.encode(text)))

    proposed = run(
        config,
        start_time=args.start, end_time=args.end, out_dir=out_dir,
        screenpipe_client=screenpipe_client, backend=backend, embedder=embedder,
        skills_dir=skills_dir, screenpipe_token=screenpipe_token,
        dry_run=args.dry_run,
    )
    print(f"proposals written to: {proposed}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/synthesize.py`

```python
import json
import re

VALID_VERDICTS = {"reuse", "compose", "novel"}


class SynthesisError(Exception):
    pass


def _build_prompt(cluster, top_k_skills):
    apps = ", ".join(cluster["apps"])
    titles = "; ".join(cluster.get("example_titles", []))
    candidates = "\n".join(
        f"- {s['name']} (score={s['score']:.2f}): {s['description']}"
        for s in top_k_skills
    )
    return f"""You are classifying an observed user workflow against an existing skill library.

Cluster:
- apps: {apps}
- sessions: {cluster['session_count']}
- total_duration_seconds: {cluster['total_duration_seconds']}
- example titles: {titles}

Candidate existing skills (ranked by semantic similarity):
{candidates}

Decide one of:
- "reuse": an existing skill already covers this workflow.
- "compose": no single skill covers it, but chaining existing skills does. Draft a thin SKILL.md that invokes them in order.
- "novel": not covered; draft a full new SKILL.md.

Respond with a single JSON object:
- reuse: {{"verdict": "reuse", "target": "<skill-name>"}}
- compose: {{"verdict": "compose", "name": "<new-skill-name>", "skill_body": "<SKILL.md body>"}}
- novel: {{"verdict": "novel", "name": "<new-skill-name>", "skill_body": "<SKILL.md body>"}}
"""


def _extract_json(text: str) -> dict:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        candidate = fence.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise SynthesisError(f"no JSON object found in response: {text!r}")
        candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        raise SynthesisError(f"invalid JSON in response: {e}") from e


def synthesize(cluster, top_k_skills, backend):
    prompt = _build_prompt(cluster, top_k_skills)
    response = backend(prompt)
    payload = _extract_json(response)

    verdict = payload.get("verdict")
    if verdict not in VALID_VERDICTS:
        raise SynthesisError(f"unknown verdict: {verdict!r}")

    result = {"verdict": verdict, "skill_body": None}
    if verdict == "reuse":
        result["target"] = payload.get("target")
    else:
        result["name"] = payload.get("name")
        result["skill_body"] = payload.get("skill_body")
    return result
```

### `.gitignore`

```text
__pycache__/
*.pyc
.pytest_cache/
```

### `config.yaml`

```yaml
# autoskill configuration
#
# LLM backend for skill synthesis. Detection/clustering always runs locally;
# only redacted cluster summaries are sent to the LLM.
#
# Local is the default — your screen content never leaves the machine.
# Cloud backends (claude, foundry) are available for users who explicitly
# opt in; see the backend sections below.
backend: local    # local | claude | foundry

# Per-backend settings. Only the selected backend's block is used.
local:
  # LM Studio exposes an OpenAI-compatible server. Start it from the
  # "Developer" tab; the default port is 1234.
  endpoint: http://localhost:1234/v1
  # Gemma-4-31B-it is the recommended default: strong reasoning at a size
  # most modern workstation GPUs can run. Swap for any LM Studio model ID.
  model: Gemma-4-31B-it

claude:
  model: claude-opus-4-7
  # api_key read from ANTHROPIC_API_KEY env var

foundry:
  endpoint: https://foundry.example.com/anthropic
  model: claude-opus-4-7
  # api_key read from FOUNDRY_API_KEY env var

# Screenpipe HTTP endpoint. For TLS, point this at your local Caddy proxy
# (see references/https-proxy.md).
screenpipe:
  url: http://localhost:3030
  # Screenpipe requires a bearer token for its local API. Either set `token`
  # here, or export SCREENPIPE_TOKEN in your environment (preferred — keeps
  # the token out of version control). Retrieve with: `screenpipe auth token`.
  # token: your-token-here

# Embedding model for matching against existing scientific skills.
# Local only; no API calls.
embeddings:
  model: sentence-transformers/all-MiniLM-L6-v2

# Clustering thresholds.
cluster:
  min_session_minutes: 5        # skip sessions shorter than this
  idle_gap_minutes: 10          # new session after this much inactivity
  min_cluster_size: 2           # need this many similar sessions before proposing

# Content redaction regexes applied before any cluster summary leaves
# the local detection layer. Defense-in-depth on top of screenpipe's
# own app/window filtering.
redaction:
  enabled: true
```
