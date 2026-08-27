---
name: exa-search
description: Exa search API key.
---

# Exa Web Toolkit

A skill for web-powered research tasks backed by [Exa](https://exa.ai): web search and URL extraction. Exa's index combines high-quality keyword and semantic retrieval, which makes it well-suited to scientific, technical, and conceptual queries.

## Routing — pick the right capability

Read the user's request and match it to one of the capabilities below. Read the corresponding reference file for detailed instructions before running commands.

| User wants to... | Capability | Where |
|---|---|---|
| Look something up, research a topic, find current info | **Web Search** | `references/web-search.md` |
| Fetch content from a specific URL (webpage, article, PDF) | **Web Extract** | `references/web-extract.md` |
| Install or authenticate | **Setup** | Below |

### Decision guide

- **Default to Web Search** for topic lookups, research questions, or "what is X?" queries. When the topic is scientific or technical, pass `--category "research paper"` to bias toward scholarly sources, and/or an academic `--include-domains` allowlist. See `references/web-search.md` for the two-pass academic strategy.
- **Use Web Extract** when the user provides a URL or asks you to read/fetch a specific page. Prefer this over the built-in WebFetch for batch extraction (multiple URLs in one call) and for academic PDFs.

### Academic source priority

For technical or scientific queries, prefer academic and scientific sources:
- Peer-reviewed journal articles and conference proceedings over blog posts or news
- Preprints (arXiv, bioRxiv, medRxiv) when peer-reviewed versions aren't available
- Institutional and government sources (NIH, WHO, NASA, NIST) over commercial sites
- Primary research over secondary summaries

Two levers to steer Exa toward scholarly content:
1. `--category "research paper"` biases retrieval toward scholarly sources.
2. `--include-domains` with a scholarly allowlist (arxiv.org, nature.com, pubmed.ncbi.nlm.nih.gov, etc.) restricts the domain pool.

Combine both for strictly academic results. See `references/web-search.md` for the full pattern.

When citing academic sources, include author names and publication year where available (e.g., [Smith et al., 2025](url)) in addition to the standard citation format. If a DOI is present, prefer the DOI link.

---

## Setup

This skill uses the [`exa-py`](https://github.com/exa-labs/exa-py) Python SDK. The scripts in `scripts/` declare their dependencies via PEP 723 inline metadata, so you can run them directly with `uv run` without a separate install step:

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_search.py" --help
```

If you prefer a persistent install:

```bash
uv pip install "exa-py>=1.14.0"
```

### Authentication

All commands read the API key from the `EXA_API_KEY` environment variable. Get your Exa API key at [dashboard.exa.ai/api-keys](https://dashboard.exa.ai/api-keys).

First, check if a `.env` file exists in the project root and contains `EXA_API_KEY`. If so, load it:

```bash
dotenv -f .env run -- uv run --with exa-py python "$SKILL_PATH/scripts/exa_search.py" "your query"
```

If `dotenv` isn't available, install it: `uv pip install python-dotenv[cli]`.

If there's no `.env`, export the key for the session:

```bash
export EXA_API_KEY="your-key"
```

Verify by running any script with `--help` — it will exit cleanly if the key is set and auth-check runs only when a real query is made.

### Tracking header

Every script in this skill sets the `x-exa-integration` request header to `k-dense-ai--scientific-agent-skills` so Exa can attribute usage from the K-Dense AI scientific-agent-skills repo to this integration. Do not remove or rename this header when adapting the scripts.

---

## Files in this skill

- `SKILL.md` — this file (routing and setup)
- `references/web-search.md` — detailed web search reference with academic strategy
- `references/web-extract.md` — URL content extraction reference
- `scripts/exa_search.py` — CLI wrapper around `client.search_and_contents`
- `scripts/exa_extract.py` — CLI wrapper around `client.get_contents`

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/exa-search/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/web-extract.md`

# URL Extraction

Extract content from: $ARGUMENTS

## Command

Choose a short, descriptive filename based on the URL or content (e.g., `alphafold-paper`, `nature-editorial`). Use lowercase with hyphens, no spaces.

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_extract.py" "$ARGUMENTS" \
  --text \
  -o "$FILENAME.json"
```

You can pass multiple URLs as positional arguments — the script batches them in a single `/contents` call, which is faster and cheaper than looping.

Content modes:

- `--text` (default if nothing else is passed) returns full-text content
- `--highlights` returns extracted passages instead of full text

## Academic content handling

When extracting from academic sources (arXiv, PubMed, journal sites, conference proceedings), use `--text` to get the full paper text:

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_extract.py" "$URL" \
  --text \
  -o "$FILENAME.json"
```

For arXiv, either the `/abs/` page URL or the raw PDF URL works. Prefer `/abs/` when available — it has cleaner metadata (title, authors, published date) attached to the result.

## Response format

Return content as:

**[Page Title](URL)**

For academic papers, include structured metadata when available:
- **Authors:** list of authors (from the `author` field)
- **Published:** from `published_date`

Then the extracted content, with these rules:
- Keep content verbatim — do not paraphrase or summarize
- Parse lists exhaustively — extract EVERY numbered/bulleted item
- Strip only obvious noise: nav menus, footers, ads
- Preserve all facts, names, numbers, dates, quotes
- For academic papers, preserve figure/table captions and references

**Partial-result handling** — when batching multiple URLs, one or more may fail (paywall, robots.txt, timeout). Report which URLs extracted successfully and which failed, rather than silently dropping failures.

After the response, mention the output file path (`$FILENAME.json`) so the user knows it's available for follow-up questions.

### `references/web-search.md`

# Web Search

Search the web for: $ARGUMENTS

## Command

Choose a short, descriptive filename based on the query (e.g., `ai-chip-news`, `crispr-off-target`). Use lowercase with hyphens, no spaces.

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_search.py" "$ARGUMENTS" \
  --text --highlights \
  -o "$FILENAME.json"
```

`$SKILL_PATH` is the path to this skill directory. The `-o` flag saves the full results to a JSON file so follow-up questions can reuse them without re-querying.

**Search type selection** — `--type` controls retrieval mode:

| Mode | When to use |
|---|---|
| `auto` (default) | Exa's general-purpose search. Use this unless you have a reason not to. |
| `fast` | Lowest latency. Use for simple lookups where speed matters more than nuance. |
| `deep` | Slowest but highest quality. Use for hard, conceptual, or exhaustive research queries where recall matters more than latency. |

**Content modes** — add any combination:

- `--text` returns full-text content per result
- `--highlights` returns the most relevant passages (good signal-to-noise, lower token cost than full text)

Default to `--highlights` for broad searches (cheaper, more skimmable). Add `--text` only when you need to quote or extract in detail.

**Filtering options** — Exa supports rich filtering via the SDK:

- `--start-published-date YYYY-MM-DD` / `--end-published-date YYYY-MM-DD` for time-sensitive queries
- `--include-domains domain1.com,domain2.com` to restrict to an allowlist
- `--exclude-domains spam.com,low-quality.com` to drop a blocklist
- `--category "research paper"` to bias toward scholarly content (also: `company`, `news`, `github`, `personal site`, `financial report`, `people`)
- `--user-location US` for locale-specific results

## Academic source strategy

For scientific or technical queries, Exa has two strong levers:

### 1. Use `--category "research paper"`

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_search.py" "$ARGUMENTS" \
  --category "research paper" \
  --text --highlights \
  -o "$FILENAME-academic.json"
```

This biases retrieval toward papers indexed as scholarly content (journals, preprint servers, conference proceedings) rather than blogs or news coverage.

### 2. Restrict to scholarly domains

For stricter academic filtering, combine the category with an explicit domain allowlist:

```bash
uv run --with exa-py python "$SKILL_PATH/scripts/exa_search.py" "$ARGUMENTS" \
  --category "research paper" \
  --include-domains "arxiv.org,biorxiv.org,medrxiv.org,pubmed.ncbi.nlm.nih.gov,nature.com,science.org" \
  --text --highlights \
  -o "$FILENAME-academic.json"
```

### Two-pass pattern for comprehensive coverage

Run **both** an academic-focused search and an unrestricted one, then merge with academic sources first:

1. Academic pass: `--category "research paper"` with the scholarly domain allowlist above.
2. General pass: the standard command without `--category` or `--include-domains`, to catch relevant non-academic sources (news coverage, lab blogs, institutional pages).

Merge results, leading with academic sources. If the query is clearly non-scientific, skip the academic pass.

**When to use the two-search pattern:** Any query involving scientific claims, medical information, research findings, technical mechanisms, statistical data, or anything where primary literature would be more reliable than secondary reporting.

## Parsing results

Parse the JSON output. Each result includes:

- `title`, `url`, `published_date`, `author`
- `score` — Exa's relevance score for the query
- `text` (if `--text`), `highlights` + `highlight_scores` (if `--highlights`)

**Snippet fallback** — any combination of content fields may be present. Cascade through them: prefer `highlights` (tight, pre-selected passages), fall back to a truncated slice of `text`. Never assume exactly one is present.

## Response format

**CRITICAL: Every claim must have an inline citation.** Use markdown links pulling only from the JSON output. Never invent or guess URLs.

For academic sources, use author-year citation style where metadata is available:
- Academic: [Smith et al., 2025](url) or [Smith & Jones, 2024](url)
- Non-academic: [Source Title](url)

Synthesize a response that:
- Leads with findings from peer-reviewed or preprint sources when available
- Clearly distinguishes between claims backed by primary research vs. secondary reporting
- Includes specific facts, names, numbers, dates
- Cites every fact inline — do not leave any claim uncited
- Organizes by theme if multiple topics
- Notes the evidence quality (e.g., "a randomized controlled trial found..." vs. "a blog post reports...")

**End with a Sources section** listing every URL referenced, grouped by type:

```
Sources:

Academic / Peer-reviewed:
- [Smith et al., 2025 — Title of Paper](https://doi.org/...) (Nature, 2025)
- [Jones & Lee, 2024 — Title of Paper](https://arxiv.org/...) (arXiv preprint)

Other:
- [Source Title](https://example.com/article) (Feb 2026)
```

This Sources section is mandatory. Do not omit it. If no academic sources were found, note that and explain why (e.g., the topic is too recent, not yet studied, or inherently non-academic).

After the Sources section, mention the output file path (`$FILENAME.json`) so the user knows it's available for follow-up questions.

### `scripts/exa_extract.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["exa-py>=1.14.0"]
# ///
"""Fetch and extract content from URLs using Exa's /contents endpoint.

Example:
    uv run exa_extract.py \\
        https://arxiv.org/abs/2401.04088 \\
        https://www.nature.com/articles/s41586-024-07566-y \\
        --text \\
        -o extracted.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

try:
    from exa_py import Exa
except ImportError:
    print(
        "exa_py not installed. Run: uv pip install exa-py  (or invoke with: uv run --with exa-py)",
        file=sys.stderr,
    )
    sys.exit(2)


EXA_INTEGRATION_HEADER = "k-dense-ai--scientific-agent-skills"


@dataclass
class ExtractedDocument:
    """Typed view of a single extracted document for JSON export."""

    url: str
    id: str | None
    title: str | None
    author: str | None
    published_date: str | None
    text: str | None = None
    highlights: list[str] = field(default_factory=list)


def _build_contents(text: bool, highlights: bool) -> dict[str, Any]:
    contents: dict[str, Any] = {}
    if text:
        contents["text"] = True
    if highlights:
        contents["highlights"] = True
    if not contents:
        # Default to full text when the caller doesn't pick anything.
        contents["text"] = True
    return contents


def _to_typed(item: Any) -> ExtractedDocument:
    return ExtractedDocument(
        url=getattr(item, "url", ""),
        id=getattr(item, "id", None),
        title=getattr(item, "title", None),
        author=getattr(item, "author", None),
        published_date=getattr(item, "published_date", None),
        text=getattr(item, "text", None),
        highlights=list(getattr(item, "highlights", None) or []),
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        print("EXA_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(2)

    client = Exa(api_key=api_key)
    client.headers["x-exa-integration"] = EXA_INTEGRATION_HEADER

    contents = _build_contents(args.text, args.highlights)
    response = client.get_contents(urls=args.urls, **contents)

    typed = [_to_typed(item) for item in getattr(response, "results", []) or []]
    return {
        "urls": list(args.urls),
        "num_results": len(typed),
        "results": [asdict(doc) for doc in typed],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract content from URLs with Exa.")
    parser.add_argument("urls", nargs="+", help="One or more URLs to extract.")
    parser.add_argument("--text", action="store_true", help="Return full-text content.")
    parser.add_argument("--highlights", action="store_true", help="Return extracted highlight snippets.")
    parser.add_argument("-o", "--output", default=None, help="Write JSON to this file (default: stdout).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run(args)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {len(payload['results'])} documents to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `scripts/exa_search.py`

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["exa-py>=1.14.0"]
# ///
"""Run an Exa web search and write results to JSON.

Uses the Exa Python SDK. Auth via the EXA_API_KEY environment variable.

Example:
    uv run exa_search.py "transformer architectures" \\
        --category "research paper" \\
        --text --highlights \\
        -o results.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

try:
    from exa_py import Exa
except ImportError:
    print(
        "exa_py not installed. Run: uv pip install exa-py  (or invoke with: uv run --with exa-py)",
        file=sys.stderr,
    )
    sys.exit(2)


EXA_INTEGRATION_HEADER = "k-dense-ai--scientific-agent-skills"


@dataclass
class SearchResult:
    """Typed view of a single Exa search result for JSON export."""

    title: str | None
    url: str
    id: str | None
    author: str | None
    published_date: str | None
    score: float | None
    text: str | None = None
    highlights: list[str] = field(default_factory=list)
    highlight_scores: list[float] = field(default_factory=list)


def _split_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def _build_contents(text: bool, highlights: bool) -> dict[str, Any] | None:
    contents: dict[str, Any] = {}
    if text:
        contents["text"] = True
    if highlights:
        contents["highlights"] = True
    return contents or None


def _result_to_typed(item: Any) -> SearchResult:
    highlights = list(getattr(item, "highlights", None) or [])
    scores = list(getattr(item, "highlight_scores", None) or [])
    return SearchResult(
        title=getattr(item, "title", None),
        url=getattr(item, "url", ""),
        id=getattr(item, "id", None),
        author=getattr(item, "author", None),
        published_date=getattr(item, "published_date", None),
        score=getattr(item, "score", None),
        text=getattr(item, "text", None),
        highlights=highlights,
        highlight_scores=scores,
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        print("EXA_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(2)

    client = Exa(api_key=api_key)
    # Attribute API usage to this skill for integration tracking.
    client.headers["x-exa-integration"] = EXA_INTEGRATION_HEADER

    contents = _build_contents(args.text, args.highlights)

    kwargs: dict[str, Any] = {
        "query": args.query,
        "num_results": args.num_results,
        "type": args.type,
    }
    if args.category:
        kwargs["category"] = args.category
    if include := _split_csv(args.include_domains):
        kwargs["include_domains"] = include
    if exclude := _split_csv(args.exclude_domains):
        kwargs["exclude_domains"] = exclude
    if args.start_published_date:
        kwargs["start_published_date"] = args.start_published_date
    if args.end_published_date:
        kwargs["end_published_date"] = args.end_published_date
    if args.user_location:
        kwargs["user_location"] = args.user_location

    if contents is not None:
        response = client.search_and_contents(**kwargs, **contents)
    else:
        response = client.search(**kwargs)

    typed = [_result_to_typed(item) for item in getattr(response, "results", []) or []]
    return {
        "query": args.query,
        "type": args.type,
        "num_results": len(typed),
        "autoprompt_string": getattr(response, "autoprompt_string", None),
        "results": [asdict(result) for result in typed],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Search the web with Exa.")
    parser.add_argument("query", help="Natural-language search query.")
    parser.add_argument(
        "--type",
        default="auto",
        choices=["auto", "fast", "deep"],
        help="Search type. 'auto' is Exa's general-purpose search; 'fast' is lowest latency; 'deep' is highest quality at higher latency.",
    )
    parser.add_argument("--num-results", type=int, default=10, help="Number of results (1-100).")
    parser.add_argument(
        "--category",
        default=None,
        choices=[
            "company",
            "research paper",
            "news",
            "github",
            "personal site",
            "financial report",
            "people",
        ],
        help="Bias results toward a content category.",
    )
    parser.add_argument("--include-domains", default=None, help="Comma-separated allowlist.")
    parser.add_argument("--exclude-domains", default=None, help="Comma-separated blocklist.")
    parser.add_argument("--start-published-date", default=None, help="ISO date, e.g. 2024-01-01.")
    parser.add_argument("--end-published-date", default=None, help="ISO date, e.g. 2024-12-31.")
    parser.add_argument("--user-location", default=None, help="Two-letter ISO country code.")
    parser.add_argument("--text", action="store_true", help="Return full-text content per result.")
    parser.add_argument("--highlights", action="store_true", help="Return extracted highlight snippets.")
    parser.add_argument("-o", "--output", default=None, help="Write JSON to this file (default: stdout).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = run(args)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Wrote {len(payload['results'])} results to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
