#!/usr/bin/env python3
"""Convert K-Dense scientific-agent-skills (Agent Skills folders) into
Open-WebUI-compatible single-file skills.

Open WebUI stores each skill as one markdown blob (`name`, `description`,
`content`). It imports:
  - `.md` files whose YAML frontmatter holds `name` and `description`;
    the rest of the file becomes `content`.
  - a JSON array of skill objects (`id`, `name`, `description`, `content`,
    `meta`, `is_active`) via "Import JSON".

This script turns each `skills/<skill>/` folder into one such `.md` file,
inlining every sibling file (references, scripts, assets) as labelled text so
the skill stays self-contained. Binary/vendored-data blobs (`.xsd` schemas,
images, archives, >200 KB `.json`/`.csv`) cannot be used as inline text and are
excluded with a note.

Usage:
  python3 convert_to_openwebui.py [SRC_DIR] [OUT_DIR]
Defaults: SRC_DIR=_src  OUT_DIR=openwebui

Output:
  OUT_DIR/skills/<id>.md     one importable skill per source skill
  OUT_DIR/skills.json        bulk import JSON (Open WebUI "Import JSON")
  OUT_DIR/manifest.json      build index (id -> files, sizes, exclusions)
  OUT_DIR/README.md          installation instructions
"""

import hashlib
import io
import json
import os
import re
import sys
import time

UPSTREAM = "https://github.com/K-Dense-AI/scientific-agent-skills"
# File extensions excluded from inlining: binary assets, vendored schemas, or
# bulk data the model cannot meaningfully consume as instructions.
EXCLUDED_EXTS = {
    ".xsd", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tiff",
    ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".zst", ".7z",
    ".pptx", ".docx", ".xlsx", ".ppt", ".xls", ".doc", ".odt", ".bin",
}
# Text-like data extensions only inlined up to a size cap (raw datasets).
DATA_EXTS = {".csv", ".json"}
DATA_MAX_BYTES = 200_000

FENCE_LANG = {".py": "python", ".sh": "bash", ".json": "json", ".csv": "csv",
              ".tex": "latex", ".bib": "bibtex", ".bst": "latex", ".sty": "latex",
              ".html": "html", ".xml": "xml", ".yaml": "yaml", ".yml": "yaml",
              ".mplstyle": "text", ".txt": "text", ".gitignore": "text"}


def parse_frontmatter(text):
    """Very small YAML-subset parser matching Open WebUI's frontmatter read."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fm, body = m.group(1), text[m.end():]
    keys = {}
    for line in fm.split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            keys[k.strip()] = v.strip().strip("\"'")
    return keys, body


def collect_files(root, prefix="", skip_dirs=()):
    """Return (included[(relpath, size)], excluded[relpath]) deterministically.
    relpath is expressed relative to `root`, prefixed with `prefix`.
    ```
    """
    included, excluded = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        if not prefix:
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for fn in sorted(filenames):
            p = os.path.join(dirpath, fn)
            rel = os.path.join(prefix, os.path.relpath(p, root)).replace(
                os.sep, "/")
            ext = os.path.splitext(fn)[1].lower()
            size = os.path.getsize(p)
            if ext in EXCLUDED_EXTS or (ext in DATA_EXTS and size > DATA_MAX_BYTES):
                excluded.append(rel)
                continue
            try:
                with io.open(p, encoding="utf-8") as fh:
                    fh.read()
            except (UnicodeDecodeError, OSError):
                excluded.append(rel)
            else:
                included.append((rel, size))
    included.sort()
    excluded.sort()
    return included, excluded
def build(skill_dir, out_dir, manifest):
    """Convert one skill folder -> content string; record metadata."""
    name = os.path.basename(skill_dir)
    raw = io.open(os.path.join(skill_dir, "SKILL.md"), encoding="utf-8").read()
    fm, body = parse_frontmatter(raw)

    # id: Open WebUI backend enforces lowercase [a-z0-9_-]+ ids.
    skill_id = (fm.get("name") or name).strip().lower().replace(" ", "-")
    if not re.fullmatch(r"[a-z0-9_-]+", skill_id):
        skill_id = re.sub(r"[^a-z0-9_-]", "", skill_id) or name
    description = (fm.get("description") or "").strip()

    # Order: references, scripts, assets (documentation first).
    included_all, excluded_all = [], []
    for sub in ("references", "scripts", "assets", ""):
        root = os.path.join(skill_dir, sub) if sub else skill_dir
        if not os.path.isdir(root):
            continue
        inc, exc = collect_files(
            root, prefix=sub, skip_dirs=("references", "scripts", "assets"))
        included_all.extend(inc)
        excluded_all.extend(exc)

    blocks = []
    for rel, _size in included_all:
        if rel == "SKILL.md":
            continue
        with io.open(os.path.join(skill_dir, rel), encoding="utf-8") as f:
            text = f.read()
        rstrip = text.rstrip()
        if rel.endswith(".md"):
            blocks.append(("### `{rel}`\n\n{text}").format(rel=rel, text=rstrip))
        else:
            lang = FENCE_LANG.get(os.path.splitext(rel)[1].lower(), "text")
            blocks.append(("### `{rel}`\n\n```{lang}\n{text}\n```").format(
                rel=rel, lang=lang, text=rstrip))

    appendix = [
        "---",
        "## Bundled files (Open WebUI single-file edition)",
        "> This is a conversion of `skills/%s/` from the K-Dense "
        "scientific-agent-skills package (%s) for Open WebUI, which stores "
        "each skill as a single markdown blob. Sibling files the skill text "
        "refers to (references, scripts, assets) are inlined below: when "
        "instructions mention `references/foo.md`, its content is here." % (name, UPSTREAM),
    ]
    if excluded_all:
        appendix.append("> Excluded (not usable as inline text — binary assets, "
                        "vendored schemas, or bulk data): %s" % ", ".join(excluded_all))
    if blocks:
        appendix.extend(blocks)
    else:
        appendix.append("No sibling files to inline.")

    content = "---\nname: {id}\ndescription: {desc}\n---\n\n{body}".format(
        id=skill_id, desc=description, body=body.rstrip())
    content += "\n\n" + "\n\n".join(appendix).rstrip() + "\n"

    manifest[name] = {
        "id": skill_id,
        "description": description,
        "sizes": {
            "SKILL.md": len(raw),
            "inlined": sum(s for _, s in included_all),
            "content": len(content),
        },
        "files_inlined": [r for r, _ in included_all if r != "SKILL.md"],
        "files_excluded": excluded_all,
        "sha256": "sha256:" + hashlib.sha256(content.encode()).hexdigest(),
    }

    out = os.path.join(out_dir, "skills", "{}.md".format(skill_id))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(content)
    return content


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "_src"
    out = sys.argv[2] if len(sys.argv) > 2 else "openwebui"
    base = os.path.join(src, "skills")
    manifest, json_items = {}, []
    for folder in sorted(os.listdir(base)):
        if not os.path.isfile(os.path.join(base, folder, "SKILL.md")):
            continue
        content = build(os.path.join(base, folder), out, manifest)
        m = manifest[folder]
        json_items.append({
            "id": m["id"],
            "name": m["id"],  # display name == id; Open WebUI formats on import
            "description": m["description"],
            "content": content,
            "meta": {"tags": ["scientific-agent-skills"]},
            "is_active": True,
            "access_grants": [],
        })

    total = sum(m["sizes"]["content"] for m in manifest.values())
    with io.open(os.path.join(out, "skills.json"), "w", encoding="utf-8") as f:
        json.dump(json_items, f, ensure_ascii=False, indent=2)
    with io.open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({
            "source": UPSTREAM,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "skill_count": len(json_items),
            "content_bytes": total,
            "skills": manifest,
        }, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
