---
name: docx
description: Use this skill whenever the user wants to create, read, edit, or manipulate Word documents (.docx files) or Word templates (.dotx files). Triggers include: any mention of 'Word doc', 'word document', '.docx', '.dotx', or requests to produce professional documents with formatting like tables of contents, headings, page numbers, or letterheads. Also use when extracting or reorganizing content from .docx or .dotx files, inserting or replacing images in documents, performing find-and-replace in Word files, working with tracked changes or comments, or converting content into a polished Word document. If the user asks for a 'report', 'memo', 'letter', 'template', or similar deliverable as a Word or .docx file, use this skill. Do NOT use for PDFs, spreadsheets, Google Docs, or general coding tasks unrelated to document generation.
---

# DOCX creation, editing, and analysis

A `.docx` is a ZIP archive of XML files. Choose your approach by task:

| Task | Approach |
|---|---|
| **Create** a new document | Write a `docx` (npm) script — see gotchas below |
| **Edit** an existing document | `unzip` → edit `word/document.xml` → `zip` (docx-js cannot open existing files) |
| **Read** content | `pandoc -t markdown file.docx` |

> Script paths below are relative to this skill's directory.

## Creating with docx-js — gotchas

`docx` is preinstalled — do not run `npm install` first; write the script and `require('docx')` directly. Only if that require fails: `npm install docx`. The model knows the API; these are the footguns:

- **Page size defaults to A4.** For US Letter set `page: { size: { width: 12240, height: 15840 } }` (DXA; 1440 = 1″).
- **Landscape:** pass portrait dimensions and `orientation: PageOrientation.LANDSCAPE` — docx-js swaps width/height internally.
- **Tables need dual widths:** set `columnWidths` on the table AND `width` on every cell, both in `WidthType.DXA` (PERCENTAGE breaks in Google Docs). Column widths must sum to the table width.
- **Table shading:** use `ShadingType.CLEAR`, never `SOLID` (renders black).
- **Lists:** never insert `•` literally; use a `numbering` config with `LevelFormat.BULLET`.
- **`ImageRun` requires `type:`** (`"png"`, `"jpg"`, …).
- **`PageBreak` must be inside a `Paragraph`.**
- **Never use `\n`** — use separate `Paragraph` elements.
- **TOC:** headings must use built-in `HeadingLevel.*`; custom heading styles need `outlineLevel` set or they won't appear.
- **Don't use a table as a horizontal rule** — use a paragraph bottom border instead.
- **Dot-leader / right-aligned-on-same-line:** use `PositionalTab` (`alignment: PositionalTabAlignment.RIGHT`, `leader: PositionalTabLeader.DOT`) inside a `TextRun`, not literal `.` or space padding.

## Verify the output

After writing a `.docx`, render it and look at it:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 100 output.pdf page
ls page-*.jpg   # then Read the images
```

`pdftoppm` zero-pads page numbers to the width of the page count (`page-01.jpg`…`page-12.jpg`).

## Editing existing documents

Legacy `.doc` files must be converted first: `python scripts/office/soffice.py --headless --convert-to docx file.doc`.

```bash
unzip -q doc.docx -d unpacked/
find unpacked -type l -delete   # strip symlink entries — docx from external parties is untrusted
python scripts/merge_runs.py unpacked/   # coalesce fragmented runs so text is findable
# edit unpacked/word/document.xml in place — do NOT reformat or pretty-print
(cd unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
python scripts/office/validate.py out.docx --original doc.docx   # XSD checks; --auto-repair fixes common issues
# redlining? add --author "<the name you redlined under>" to check every edit is tracked
```

Word splits text across many `<w:r>` runs (revision ids, spell-check markers), so a phrase you can see in the document often doesn't exist as a contiguous string in the XML. `merge_runs.py` merges adjacent identically-formatted runs in `word/document.xml` without changing content or rendering; it also accepts a `.docx` directly (`python scripts/merge_runs.py doc.docx -o merged.docx`).

**Tracked changes:** when redlining, validate with `--author "<the name you redlined under>"` (needs `--original`) — it reports any text you changed without a `<w:ins>`/`<w:del>` around it, which is easy to do by accident and invisible in the accepted view. Wrap runs in `<w:ins>`/`<w:del>` with `w:id`, `w:author`, `w:date` attributes. Inside `<w:del>`, the text element is `<w:delText>`, not `<w:t>`. A deleted paragraph mark (`<w:pPr><w:rPr><w:del w:id=".." w:author=".." w:date=".."/></w:rPr></w:pPr>`) means "merge this paragraph into the next" — so deleting a paragraph outright is that plus a `<w:del>` around every run. The `<w:del/>` must come before the rPr's other children; their order is schema-enforced.

To produce a clean copy with all tracked changes accepted: `python scripts/accept_changes.py in.docx out.docx`.

Accepting a deleted paragraph mark should join that paragraph to the one below it, so a paragraph whose runs are *all* deleted vanishes. Word does this; `accept_changes.py` and `pandoc --track-changes=accept` don't always. Both fail the same way — they strip the deleted text but leave the emptied paragraph behind, which reads as a stray empty bullet when it was auto-numbered:

- `pandoc --track-changes=accept` never joins the paragraphs.
- `accept_changes.py` (LibreOffice) joins them correctly, except when the deleted paragraph is followed by an empty spacer paragraph.

An empty bullet in either view is an artifact of that view, not a defect in the document. Check paragraph deletions in the XML.

## Comments

Comments require six cross-linked files. Use the helper — directory mode when you'll also be editing `document.xml` (saves an unzip/rezip cycle), `.docx`-direct mode otherwise:

```bash
# Against an already-unpacked directory (preferred when also placing markers)
python scripts/comment.py unpacked/ "Fees & expenses cap is too low"
python scripts/comment.py unpacked/ "Agreed" --parent 0

# Against a .docx directly
python scripts/comment.py contract.docx "This cap is too low" -o annotated.docx
```

The script writes `comments.xml`, `commentsExtended.xml`, `commentsIds.xml`, `commentsExtensible.xml`, the relationships, and the content-type overrides. Comment IDs are auto-assigned. It then prints the `<w:commentRangeStart>`/`<w:commentRangeEnd>`/`<w:commentReference>` snippet to add to `word/document.xml` so the comment anchors to specific text — until you place those markers, the comment exists but is not visible.

## Dependencies

`docx` (npm, preinstalled — install only if `require('docx')` fails) · `pandoc` · LibreOffice (`soffice`) · `pdftoppm` (Poppler)

---

*This skill is created and maintained by [Anthropic](https://github.com/anthropics/skills/tree/main/skills/docx). Vendored here unmodified except for frontmatter metadata; see LICENSE.txt for terms.*

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/docx/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

> Excluded (not usable as inline text — binary assets, vendored schemas, or bulk data): scripts/office/schemas/ISO-IEC29500-4_2016/dml-chart.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-chartDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-diagram.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-lockedCanvas.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-main.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-picture.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-spreadsheetDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-wordprocessingDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/pml.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-additionalCharacteristics.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-bibliography.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-commonSimpleTypes.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-customXmlDataProperties.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-customXmlSchemaProperties.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-documentPropertiesCustom.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-documentPropertiesExtended.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-documentPropertiesVariantTypes.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-math.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-relationshipReference.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/sml.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-main.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-officeDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-presentationDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-spreadsheetDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-wordprocessingDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/wml.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/xml.xsd, scripts/office/schemas/ecma/fouth-edition/opc-contentTypes.xsd, scripts/office/schemas/ecma/fouth-edition/opc-coreProperties.xsd, scripts/office/schemas/ecma/fouth-edition/opc-digSig.xsd, scripts/office/schemas/ecma/fouth-edition/opc-relationships.xsd, scripts/office/schemas/mce/mc.xsd, scripts/office/schemas/microsoft/wml-2010.xsd, scripts/office/schemas/microsoft/wml-2012.xsd, scripts/office/schemas/microsoft/wml-2018.xsd, scripts/office/schemas/microsoft/wml-cex-2018.xsd, scripts/office/schemas/microsoft/wml-cid-2016.xsd, scripts/office/schemas/microsoft/wml-sdtdatahash-2020.xsd, scripts/office/schemas/microsoft/wml-symex-2015.xsd

### `scripts/__init__.py`

```python

```

### `scripts/accept_changes.py`

```python
"""Accept all tracked changes in a DOCX file using LibreOffice.

Requires LibreOffice (soffice) to be installed.
"""

import argparse
import logging
import shutil
import subprocess
from pathlib import Path

from office.soffice import get_soffice_env

logger = logging.getLogger(__name__)

LIBREOFFICE_PROFILE = "/tmp/libreoffice_docx_profile"
MACRO_DIR = f"{LIBREOFFICE_PROFILE}/user/basic/Standard"

ACCEPT_CHANGES_MACRO = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Module1" script:language="StarBasic">
    Sub AcceptAllTrackedChanges()
        Dim document As Object
        Dim dispatcher As Object

        document = ThisComponent.CurrentController.Frame
        dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")

        dispatcher.executeDispatch(document, ".uno:AcceptAllTrackedChanges", "", 0, Array())
        ThisComponent.store()
        ThisComponent.close(True)
    End Sub
</script:module>"""


def accept_changes(
    input_file: str,
    output_file: str,
) -> tuple[None, str]:
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        return None, f"Error: Input file not found: {input_file}"

    if not input_path.suffix.lower() == ".docx":
        return None, f"Error: Input file is not a DOCX file: {input_file}"

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_path, output_path)
    except Exception as e:
        return None, f"Error: Failed to copy input file to output location: {e}"

    if not _setup_libreoffice_macro():
        return None, "Error: Failed to setup LibreOffice macro"

    cmd = [
        "soffice",
        "--headless",
        f"-env:UserInstallation=file://{LIBREOFFICE_PROFILE}",
        "--norestore",
        "vnd.sun.star.script:Standard.Module1.AcceptAllTrackedChanges?language=Basic&location=application",
        str(output_path.absolute()),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=get_soffice_env(),
        )
    except subprocess.TimeoutExpired:
        return (
            None,
            f"Successfully accepted all tracked changes: {input_file} -> {output_file}",
        )

    if result.returncode != 0:
        return None, f"Error: LibreOffice failed: {result.stderr}"

    return (
        None,
        f"Successfully accepted all tracked changes: {input_file} -> {output_file}",
    )


def _setup_libreoffice_macro() -> bool:
    macro_dir = Path(MACRO_DIR)
    macro_file = macro_dir / "Module1.xba"

    if macro_file.exists() and "AcceptAllTrackedChanges" in macro_file.read_text():
        return True

    if not macro_dir.exists():
        subprocess.run(
            [
                "soffice",
                "--headless",
                f"-env:UserInstallation=file://{LIBREOFFICE_PROFILE}",
                "--terminate_after_init",
            ],
            capture_output=True,
            timeout=10,
            check=False,
            env=get_soffice_env(),
        )
        macro_dir.mkdir(parents=True, exist_ok=True)

    try:
        macro_file.write_text(ACCEPT_CHANGES_MACRO)
        return True
    except Exception as e:
        logger.warning(f"Failed to setup LibreOffice macro: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Accept all tracked changes in a DOCX file"
    )
    parser.add_argument("input_file", help="Input DOCX file with tracked changes")
    parser.add_argument(
        "output_file", help="Output DOCX file (clean, no tracked changes)"
    )
    args = parser.parse_args()

    _, message = accept_changes(args.input_file, args.output_file)
    print(message)

    if "Error" in message:
        raise SystemExit(1)
```

### `scripts/comment.py`

```python
"""Add comments to a DOCX document.

Accepts either an unpacked directory OR a .docx/.dotx file directly.

Usage:
    # Against an unpacked directory (writes satellite files in place)
    python comment.py unpacked/ "Comment text"
    python comment.py unpacked/ "Reply text" --parent 0

    # Against a .docx directly (extracts, writes satellite files, rezips)
    python comment.py contract.docx "This cap is too low" -o annotated.docx
    python comment.py contract.docx "Comment" --id 5      # explicit ID

The comment ID is auto-assigned (max existing + 1) unless --id is given.
Plain text is XML-escaped automatically; if you pass already-escaped text
(e.g. &amp;, &#x2019;) use --raw to skip escaping.

After running, add markers to word/document.xml so the comment is visible:
  <w:commentRangeStart w:id="N"/>
  ... commented content ...
  <w:commentRangeEnd w:id="N"/>
  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="N"/></w:r>
"""

import argparse
import random
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import defusedxml.minidom
from xml.parsers.expat import ExpatError
from xml.sax.saxutils import escape as xml_escape

from office.helpers import opc_target, rezip as _rezip, safe_extract as _safe_extract

TEMPLATE_DIR = Path(__file__).parent / "templates"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16cid": "http://schemas.microsoft.com/office/word/2016/wordml/cid",
    "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
}

COMMENT_XML = """\
<w:comment w:id="{id}" w:author="{author}" w:date="{date}" w:initials="{initials}">
  <w:p w14:paraId="{para_id}" w14:textId="77777777">
    <w:r>
      <w:rPr><w:rStyle w:val="CommentReference"/></w:rPr>
      <w:annotationRef/>
    </w:r>
    <w:r>
      <w:rPr>
        <w:color w:val="000000"/>
        <w:sz w:val="20"/>
        <w:szCs w:val="20"/>
      </w:rPr>
      <w:t xml:space="preserve">{text}</w:t>
    </w:r>
  </w:p>
</w:comment>"""

COMMENT_MARKER_TEMPLATE = """
Add to word/document.xml (markers must be direct children of w:p, never inside w:r):
  <w:commentRangeStart w:id="{cid}"/>
  <w:r>...</w:r>
  <w:commentRangeEnd w:id="{cid}"/>
  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{cid}"/></w:r>"""

REPLY_MARKER_TEMPLATE = """
Nest markers inside parent {pid}'s markers (direct children of w:p, never inside w:r):
  <w:commentRangeStart w:id="{pid}"/><w:commentRangeStart w:id="{cid}"/>
  <w:r>...</w:r>
  <w:commentRangeEnd w:id="{cid}"/><w:commentRangeEnd w:id="{pid}"/>
  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{pid}"/></w:r>
  <w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{cid}"/></w:r>"""

SMART_QUOTE_ENTITIES = {
    "“": "&#x201C;",
    "”": "&#x201D;",
    "‘": "&#x2018;",
    "’": "&#x2019;",
}


def _generate_hex_id() -> str:
    return f"{random.randint(0, 0x7FFFFFFE):08X}"


def _encode_smart_quotes(text: str) -> str:
    for char, entity in SMART_QUOTE_ENTITIES.items():
        text = text.replace(char, entity)
    return text


def _append_xml(xml_path: Path, root_tag: str, content: str) -> None:
    dom = defusedxml.minidom.parseString(xml_path.read_text(encoding="utf-8"))
    root = dom.getElementsByTagName(root_tag)[0]
    ns_attrs = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items())
    wrapper_dom = defusedxml.minidom.parseString(f"<root {ns_attrs}>{content}</root>")
    for child in wrapper_dom.documentElement.childNodes:  
        if child.nodeType == child.ELEMENT_NODE:
            root.appendChild(dom.importNode(child, True))
    output = _encode_smart_quotes(dom.toxml(encoding="UTF-8").decode("utf-8"))
    xml_path.write_text(output, encoding="utf-8")


def _find_para_id(comments_path: Path, comment_id: int) -> str | None:
    dom = defusedxml.minidom.parseString(comments_path.read_text(encoding="utf-8"))
    for c in dom.getElementsByTagName("w:comment"):
        if c.getAttribute("w:id") == str(comment_id):
            for p in c.getElementsByTagName("w:p"):
                if pid := p.getAttribute("w14:paraId"):
                    return pid
    return None


def _next_comment_id(comments_path: Path) -> int:
    if not comments_path.exists():
        return 0
    dom = defusedxml.minidom.parseString(comments_path.read_text(encoding="utf-8"))
    ids = []
    for c in dom.getElementsByTagName("w:comment"):
        try:
            ids.append(int(c.getAttribute("w:id")))
        except ValueError:
            pass
    return (max(ids) + 1) if ids else 0


def _get_next_rid(rels_path: Path) -> int:
    dom = defusedxml.minidom.parseString(rels_path.read_text(encoding="utf-8"))
    max_rid = 0
    for rel in dom.getElementsByTagName("Relationship"):
        rid = rel.getAttribute("Id")
        if rid and rid.startswith("rId"):
            try:
                max_rid = max(max_rid, int(rid[3:]))
            except ValueError:
                pass
    return max_rid + 1


def _has_relationship(rels_path: Path, target: str) -> bool:
    dom = defusedxml.minidom.parseString(rels_path.read_text(encoding="utf-8"))
    return any(
        rel.getAttribute("Target") == target
        for rel in dom.getElementsByTagName("Relationship")
    )


def _has_content_type(ct_path: Path, part_name: str) -> bool:
    dom = defusedxml.minidom.parseString(ct_path.read_text(encoding="utf-8"))
    return any(
        o.getAttribute("PartName") == part_name
        for o in dom.getElementsByTagName("Override")
    )


_COMMENT_RELS = [
    ("http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments", "comments.xml"),
    ("http://schemas.microsoft.com/office/2011/relationships/commentsExtended", "commentsExtended.xml"),
    ("http://schemas.microsoft.com/office/2016/09/relationships/commentsIds", "commentsIds.xml"),
    ("http://schemas.microsoft.com/office/2018/08/relationships/commentsExtensible", "commentsExtensible.xml"),
]
_COMMENT_OVERRIDES = [
    ("/word/comments.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"),
    ("/word/commentsExtended.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml"),
    ("/word/commentsIds.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsIds+xml"),
    ("/word/commentsExtensible.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtensible+xml"),
]


def _ensure_comment_relationships(unpacked_dir: Path) -> None:
    rels_path = unpacked_dir / "word" / "_rels" / "document.xml.rels"
    if not rels_path.exists():
        return
    dom = defusedxml.minidom.parseString(rels_path.read_text(encoding="utf-8"))
    root = dom.documentElement
    comment_types = {rel_type for rel_type, _ in _COMMENT_RELS}
    existing = set()
    for rel in dom.getElementsByTagName("Relationship"):
        if rel.getAttribute("Type") not in comment_types:
            continue
        part = opc_target(
            rel.getAttribute("Target"),
            "word/document.xml",
            rel.getAttribute("TargetMode"),
        )
        if part is not None:
            existing.add(part)
    next_rid = _get_next_rid(rels_path)
    changed = False
    for rel_type, target in _COMMENT_RELS:
        if opc_target(target, "word/document.xml") in existing:
            continue
        rel = dom.createElement("Relationship")
        rel.setAttribute("Id", f"rId{next_rid}")
        rel.setAttribute("Type", rel_type)
        rel.setAttribute("Target", target)
        root.appendChild(rel)  
        next_rid += 1
        changed = True
    if changed:
        rels_path.write_bytes(dom.toxml(encoding="UTF-8"))


def _ensure_comment_content_types(unpacked_dir: Path) -> None:
    ct_path = unpacked_dir / "[Content_Types].xml"
    if not ct_path.exists():
        return
    dom = defusedxml.minidom.parseString(ct_path.read_text(encoding="utf-8"))
    root = dom.documentElement
    existing = {
        o.getAttribute("PartName")
        for o in dom.getElementsByTagName("Override")
    }
    changed = False
    for part_name, content_type in _COMMENT_OVERRIDES:
        if part_name in existing:
            continue
        override = dom.createElement("Override")
        override.setAttribute("PartName", part_name)
        override.setAttribute("ContentType", content_type)
        root.appendChild(override)  
        changed = True
    if changed:
        ct_path.write_bytes(dom.toxml(encoding="UTF-8"))


def add_comment(
    unpacked_dir: Path | str,
    text: str,
    comment_id: int | None = None,
    author: str = "Claude",
    initials: str = "C",
    parent_id: int | None = None,
    raw: bool = False,
) -> tuple[int, str, str]:
    unpacked_dir = Path(unpacked_dir)
    if not raw:
        text = xml_escape(text)
    author = xml_escape(author, {'"': "&quot;"})
    initials = xml_escape(initials, {'"': "&quot;"})
    word = unpacked_dir / "word"
    if not word.exists():
        raise FileNotFoundError(f"{word} not found (not an unpacked .docx?)")

    comments = word / "comments.xml"
    if comment_id is None:
        comment_id = _next_comment_id(comments)

    parent_para = None
    if parent_id is not None:
        parent_para = _find_para_id(comments, parent_id) if comments.exists() else None
        if not parent_para:
            raise ValueError(f"parent comment {parent_id} not found")

    para_id, durable_id = _generate_hex_id(), _generate_hex_id()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not comments.exists():
        shutil.copy(TEMPLATE_DIR / "comments.xml", comments)
    _ensure_comment_relationships(unpacked_dir)
    _ensure_comment_content_types(unpacked_dir)
    _append_xml(
        comments,
        "w:comments",
        COMMENT_XML.format(
            id=comment_id, author=author, date=ts, initials=initials,
            para_id=para_id, text=text,
        ),
    )

    ext = word / "commentsExtended.xml"
    if not ext.exists():
        shutil.copy(TEMPLATE_DIR / "commentsExtended.xml", ext)
    if parent_para is not None:
        _append_xml(
            ext, "w15:commentsEx",
            f'<w15:commentEx w15:paraId="{para_id}" w15:paraIdParent="{parent_para}" w15:done="0"/>',
        )
    else:
        _append_xml(
            ext, "w15:commentsEx",
            f'<w15:commentEx w15:paraId="{para_id}" w15:done="0"/>',
        )

    ids = word / "commentsIds.xml"
    if not ids.exists():
        shutil.copy(TEMPLATE_DIR / "commentsIds.xml", ids)
    _append_xml(
        ids, "w16cid:commentsIds",
        f'<w16cid:commentId w16cid:paraId="{para_id}" w16cid:durableId="{durable_id}"/>',
    )

    extensible = word / "commentsExtensible.xml"
    if not extensible.exists():
        shutil.copy(TEMPLATE_DIR / "commentsExtensible.xml", extensible)
    _append_xml(
        extensible, "w16cex:commentsExtensible",
        f'<w16cex:commentExtensible w16cex:durableId="{durable_id}" w16cex:dateUtc="{ts}"/>',
    )

    action = "reply" if parent_id is not None else "comment"
    return comment_id, para_id, f"Added {action} id={comment_id} (paraId={para_id})"


def main() -> None:
    p = argparse.ArgumentParser(description="Add a comment to a DOCX (directory or .docx file).")
    p.add_argument("input", help="Unpacked DOCX directory OR a .docx/.dotx file")
    p.add_argument("text", help="Comment text (plain text; XML-escaped automatically)")
    p.add_argument("--raw", action="store_true",
                   help="Treat text as pre-escaped XML (skip automatic escaping)")
    p.add_argument("--id", type=int, dest="comment_id",
                   help="Comment ID (default: auto-assign as max existing + 1)")
    p.add_argument("--author", default="Claude", help="Author name")
    p.add_argument("--initials", default="C", help="Author initials")
    p.add_argument("--parent", type=int, help="Parent comment ID (makes this a reply)")
    p.add_argument("-o", "--output",
                   help="Output .docx path (only used when input is a .docx; default: overwrite input)")
    args = p.parse_args()

    src = Path(args.input)

    try:
        if src.is_dir():
            if args.output:
                print("Warning: --output ignored for directory input", file=sys.stderr)
            cid, _, msg = add_comment(
                src, args.text, comment_id=args.comment_id,
                author=args.author, initials=args.initials,
                parent_id=args.parent, raw=args.raw,
            )
            print(msg)
        elif src.is_file() and src.suffix.lower() in (".docx", ".dotx"):
            out = Path(args.output) if args.output else src
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                with zipfile.ZipFile(src) as zf:
                    _safe_extract(zf, tmp_path)
                cid, _, msg = add_comment(
                    tmp_path, args.text, comment_id=args.comment_id,
                    author=args.author, initials=args.initials,
                    parent_id=args.parent, raw=args.raw,
                )
                _rezip(tmp_path, out)
            print(msg)
            print(f"Wrote {out} (comment defined; add markers to word/document.xml to make it visible)")
        else:
            print(f"Error: {src} is neither a directory nor a .docx/.dotx file", file=sys.stderr)
            sys.exit(1)
    except (FileNotFoundError, ValueError, zipfile.BadZipFile, ExpatError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.parent is not None:
        print(REPLY_MARKER_TEMPLATE.format(pid=args.parent, cid=cid))
    else:
        print(COMMENT_MARKER_TEMPLATE.format(cid=cid))


if __name__ == "__main__":
    main()
```

### `scripts/merge_runs.py`

```python
"""Merge adjacent identically-formatted runs in a DOCX.

Word fragments paragraph text across many <w:r> elements (revision ids,
spell-check markers, editing history), which makes find-and-replace on
word/document.xml unreliable — the string you're looking for is split
across runs. This coalesces adjacent runs whose formatting (<w:rPr>) is
identical, strips rsid attributes and proofErr markers, and consolidates the
text elements — <w:t>, and <w:delText> for text inside a tracked deletion.

Rendering is unchanged. The text you search is what Word draws, which is not
always the bytes in the file: an element without xml:space="preserve" has its
edge whitespace trimmed before it reaches the page, so `<w:t>Hello </w:t>`
followed by `<w:t>world</w:t>` reads "Helloworld" and merges to exactly that.

Runs in two different <w:ins>/<w:del> wrappers are never merged: that would
rewrite tracked-change structure, collapsing separate revisions into one.

Only word/document.xml is processed (not headers, footers, or footnotes).

Usage:
    python merge_runs.py unpacked/                  # after unzip, before editing
    python merge_runs.py document.docx              # rewrite in place
    python merge_runs.py document.docx -o out.docx
"""


import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom

from office.helpers import XML_SPACE, rendered_text, rezip, safe_extract

WORDML_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def merge_runs(input_dir: str) -> tuple[int, str]:
    doc_xml = Path(input_dir) / "word" / "document.xml"

    if not doc_xml.exists():
        return 0, f"Error: {doc_xml} not found"

    try:
        dom = defusedxml.minidom.parseString(doc_xml.read_text(encoding="utf-8"))
        root = dom.documentElement
        run_names = _run_tag_names(root)

        _remove_elements(root, "proofErr")

        runs = _find_runs(root, run_names)
        _strip_rsid_attrs(runs)

        merge_count = 0
        for container in {run.parentNode for run in runs}:
            merge_count += _merge_runs_in(container, run_names)

        doc_xml.write_bytes(dom.toxml(encoding="UTF-8"))
        return merge_count, f"Merged {merge_count} runs"

    except Exception as e:
        return 0, f"Error: {e}"




def _is_element(node, tag: str) -> bool:
    name = node.localName or node.tagName
    return name == tag or name.endswith(f":{tag}")


def _run_tag_names(root) -> set[str]:
    names = set()
    for attr in root.attributes.values():
        if attr.value == WORDML_NS:
            if attr.name == "xmlns":
                names.add("r")
            elif attr.name.startswith("xmlns:"):
                names.add(attr.name.split(":", 1)[1] + ":r")
    return names or {"w:r", "r"}


def _find_elements(root, tag: str) -> list:
    results = []

    def traverse(node):
        if node.nodeType == node.ELEMENT_NODE:
            if _is_element(node, tag):
                results.append(node)
            for child in node.childNodes:
                traverse(child)

    traverse(root)
    return results


def _find_runs(root, run_names: set[str]) -> list:
    return [e for e in _find_elements(root, "r") if _is_run(e, run_names)]


def _get_child(parent, tag: str):
    return next(iter(_get_children(parent, tag)), None)


def _get_children(parent, tag: str) -> list:
    return [
        child
        for child in parent.childNodes
        if child.nodeType == child.ELEMENT_NODE and _is_element(child, tag)
    ]


def _is_adjacent(elem1, elem2) -> bool:
    node = elem1.nextSibling
    while node:
        if node == elem2:
            return True
        if node.nodeType == node.ELEMENT_NODE:
            return False
        if node.nodeType == node.TEXT_NODE and node.data.strip(XML_SPACE):
            return False
        node = node.nextSibling
    return False




def _remove_elements(root, tag: str):
    for elem in _find_elements(root, tag):
        if elem.parentNode:
            elem.parentNode.removeChild(elem)


def _strip_rsid_attrs(runs: list):
    for run in runs:
        for attr in list(run.attributes.values()):
            if "rsid" in attr.name.lower():
                run.removeAttribute(attr.name)




def _merge_runs_in(container, run_names: set[str]) -> int:
    merge_count = 0
    run = _first_child_run(container, run_names)

    while run:
        while True:
            next_elem = _next_element_sibling(run)
            if next_elem and _is_run(next_elem, run_names) and _can_merge(run, next_elem):
                _merge_run_content(run, next_elem)
                container.removeChild(next_elem)
                merge_count += 1
            else:
                break

        _consolidate_text(run)
        run = _next_sibling_run(run, run_names)

    return merge_count


def _first_child_run(container, run_names: set[str]):
    for child in container.childNodes:
        if child.nodeType == child.ELEMENT_NODE and _is_run(child, run_names):
            return child
    return None


def _next_element_sibling(node):
    sibling = node.nextSibling
    while sibling:
        if sibling.nodeType == sibling.ELEMENT_NODE:
            return sibling
        sibling = sibling.nextSibling
    return None


def _next_sibling_run(node, run_names: set[str]):
    sibling = node.nextSibling
    while sibling:
        if sibling.nodeType == sibling.ELEMENT_NODE:
            if _is_run(sibling, run_names):
                return sibling
        sibling = sibling.nextSibling
    return None


def _is_run(node, run_names: set[str]) -> bool:
    return node.tagName in run_names


def _can_merge(run1, run2) -> bool:
    rpr1 = _get_child(run1, "rPr")
    rpr2 = _get_child(run2, "rPr")

    if (rpr1 is None) != (rpr2 is None):
        return False
    if rpr1 is None:
        return True
    return rpr1.toxml() == rpr2.toxml()  


def _merge_run_content(target, source):
    for child in list(source.childNodes):
        if child.nodeType == child.ELEMENT_NODE:
            name = child.localName or child.tagName
            if name != "rPr" and not name.endswith(":rPr"):
                target.appendChild(child)


def _element_text(elem) -> str:
    return "".join(
        child.data
        for child in elem.childNodes
        if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE)
    )


def _has_preserve(elem) -> bool:
    return elem.getAttribute("xml:space") == "preserve"


def _rendered_text(elem) -> str:
    return rendered_text(_element_text(elem), _has_preserve(elem))


def _consolidate_text(run):
    for tag in ("t", "delText"):
        _consolidate_text_elements(run, tag)


def _consolidate_text_elements(run, tag: str):
    t_elements = _get_children(run, tag)

    for i in range(len(t_elements) - 1, 0, -1):
        curr, prev = t_elements[i], t_elements[i - 1]

        if _is_adjacent(prev, curr):
            merged = _rendered_text(prev) + _rendered_text(curr)
            had_preserve = _has_preserve(prev) or _has_preserve(curr)

            new_text = run.ownerDocument.createTextNode(merged)
            for node in list(prev.childNodes):
                if node.nodeType in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
                    prev.removeChild(node)
                else:
                    run.insertBefore(node, curr)
            prev.appendChild(new_text)
            for node in list(curr.childNodes):
                if node.nodeType not in (node.TEXT_NODE, node.CDATA_SECTION_NODE):
                    run.insertBefore(node, curr)

            if merged != merged.strip(XML_SPACE) or had_preserve:
                prev.setAttribute("xml:space", "preserve")
            elif prev.hasAttribute("xml:space"):
                prev.removeAttribute("xml:space")

            run.removeChild(curr)




def _merge_or_die(path: Path) -> str:
    _, msg = merge_runs(str(path))
    if msg.startswith("Error"):
        print(msg, file=sys.stderr)
        sys.exit(1)
    return msg


def main() -> None:
    p = argparse.ArgumentParser(
        description="Merge adjacent identically-formatted runs in a DOCX (directory or .docx file)."
    )
    p.add_argument("input", help="Unpacked DOCX directory OR a .docx/.dotx file")
    p.add_argument(
        "-o", "--output",
        help="Output .docx path (only valid when input is a .docx; default: overwrite input)",
    )
    args = p.parse_args()

    src = Path(args.input)

    try:
        if src.is_dir():
            if args.output:
                p.error("--output is only valid for .docx input; directory input is modified in place")
            print(_merge_or_die(src))
        elif src.is_file() and src.suffix.lower() in (".docx", ".dotx"):
            out = Path(args.output) if args.output else src
            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                with zipfile.ZipFile(src) as zf:
                    safe_extract(zf, tmp_path)
                msg = _merge_or_die(tmp_path)
                rezip(tmp_path, out)
            print(f"{msg}; wrote {out}")
        else:
            print(f"Error: {src} is neither a directory nor a .docx/.dotx file", file=sys.stderr)
            sys.exit(1)
    except (OSError, ValueError, zipfile.BadZipFile) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### `scripts/office/helpers/__init__.py`

```python
import os
import posixpath
import re
import stat
import tempfile
import urllib.parse
import zipfile
from pathlib import Path

OOXML_FAMILY = {
    ".docx": "docx",
    ".dotx": "docx",
    ".pptx": "pptx",
    ".potx": "pptx",
    ".xlsx": "xlsx",
    ".xltx": "xlsx",
}

_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")

SLIDE_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"


def opc_target(target: str, source_part: str, target_mode: str = "") -> str | None:
    if not target:
        return None
    if target_mode.lower() == "external":
        return None
    if _SCHEME_RE.match(target):
        return None

    target = urllib.parse.unquote(target)

    if "\\" in target:
        raise ValueError(f"relationship target is not a POSIX part name: {target!r}")

    if target.startswith("/"):
        joined = target.lstrip("/")
    else:
        joined = posixpath.join(posixpath.dirname(source_part), target)

    parts: list[str] = []
    for segment in posixpath.normpath(joined).split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if not parts:
                raise ValueError(f"relationship target escapes the package: {target!r}")
            parts.pop()
        else:
            parts.append(segment)

    if not parts:
        raise ValueError(f"relationship target resolves to nothing: {target!r}")
    return "/".join(parts)


def rels_source_part(rels_file: Path, unpacked_dir: Path) -> str:
    owner_dir = rels_file.parent.parent.relative_to(unpacked_dir)
    return posixpath.join(owner_dir.as_posix(), rels_file.name[: -len(".rels")]).lstrip("./")


def part_text(data: bytes) -> str:
    return data.decode("utf-8", "surrogateescape")


XML_SPACE = " \t\r\n"


def rendered_text(text: str, preserve: bool) -> str:
    return text if preserve else text.strip(XML_SPACE)


def safe_extract(zf: zipfile.ZipFile, dest: Path) -> None:
    dest = dest.resolve()
    for m in zf.infolist():
        if stat.S_ISLNK(m.external_attr >> 16):
            raise ValueError(f"symlink archive entry not allowed: {m.filename!r}")
        target = (dest / m.filename).resolve()
        if not target.is_relative_to(dest):
            raise ValueError(f"unsafe archive entry: {m.filename!r}")
        zf.extract(m, dest)


def rezip(src_dir: Path, out_path: Path) -> None:
    files = sorted(p for p in src_dir.rglob("*") if p.is_file())
    ct = src_dir / "[Content_Types].xml"
    fd, tmp_name = tempfile.mkstemp(
        prefix=out_path.name + ".", suffix=".tmp", dir=out_path.parent
    )
    tmp_out = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            with zipfile.ZipFile(fh, "w", zipfile.ZIP_DEFLATED) as zf:
                if ct.exists():
                    zf.write(ct, ct.relative_to(src_dir), compress_type=zipfile.ZIP_STORED)
                for f in files:
                    if f == ct:
                        continue
                    zf.write(f, f.relative_to(src_dir))
        if out_path.exists():
            mode = out_path.stat().st_mode & 0o777
        else:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
        os.chmod(tmp_out, mode)
        os.replace(tmp_out, out_path)
    finally:
        if tmp_out.exists():
            tmp_out.unlink()
```

### `scripts/office/helpers/pptx_chart.py`

```python
"""Find chart XML that PowerPoint refuses but the schema accepts.

Detection only: for either fault more than one repair is valid, and only the
author knows which was meant.
"""


from __future__ import annotations

import re
from typing import Mapping

from . import part_text


_CHART_PART_RE = re.compile(r"ppt/charts/chart\d+\.xml")

_GROUPING_RE = re.compile(r"""<c:grouping\b[^>]*?\bval=["'](\w+)["']""")
_DLBL_POS_RE = re.compile(r"""<c:dLblPos\b[^>]*?\bval=["'](\w+)["']""")

def _strip_ext_lst(text: str) -> str:
    out, cursor = [], 0
    for lo, hi in _ext_lst_spans(text):
        out.append(text[cursor:lo])
        cursor = hi
    out.append(text[cursor:])
    return "".join(out)

_BAR_GROUP_RE = re.compile(r"<c:(bar3DChart|barChart)\b[^>]*(?<!/)>.*?</c:\1\s*>", re.DOTALL)

STACKED_GROUPINGS = frozenset({"stacked", "percentStacked"})
ILLEGAL_ON_STACKED = frozenset({"outEnd"})
LEGAL_ON_STACKED = ("ctr", "inEnd", "inBase")


def _check_stacked_label_positions(part: str, xml: str) -> list[str]:
    problems: list[str] = []
    for match in _BAR_GROUP_RE.finditer(xml):
        block = _strip_ext_lst(match.group(0))
        group = match.group(1)

        grouping = _GROUPING_RE.search(block)
        if grouping is None or grouping.group(1) not in STACKED_GROUPINGS:
            continue

        bad = [p for p in _DLBL_POS_RE.findall(block) if p in ILLEGAL_ON_STACKED]
        for pos in sorted(set(bad)):
            problems.append(
                f'{part}: {bad.count(pos)} data label(s) use dLblPos="{pos}" on a '
                f"{grouping.group(1)} {group}; PowerPoint allows only "
                f"{', '.join(LEGAL_ON_STACKED)} there"
            )
    return problems



_ANY_CHART_GROUP_RE = re.compile(r"<c:(\w+Chart)\b[^>]*(?<!/)>.*?</c:\1\s*>", re.DOTALL)

_AXID_RE = re.compile(
    r"""\s*<c:axId\b[^>]*?\bval=["'](-?\d+)["']\s*(?:/>|>\s*</c:axId\s*>)"""
)

_AXIS_DECL_RE = re.compile(
    r"""<c:(catAx|valAx|serAx|dateAx)\b[^>]*(?<!/)>\s*<c:axId\b[^>]*?\bval=["'](-?\d+)["']"""
)

AXID_LIMIT = {
    "barChart": 2, "lineChart": 2, "areaChart": 2, "scatterChart": 2,
    "bubbleChart": 2, "radarChart": 2, "stockChart": 2,
    "bar3DChart": 3, "line3DChart": 3, "area3DChart": 3,
    "surfaceChart": 3, "surface3DChart": 3,
}

AXID_MINIMUM = {
    "barChart": 2, "lineChart": 2, "areaChart": 2, "scatterChart": 2,
    "bubbleChart": 2, "radarChart": 2, "stockChart": 2,
    "bar3DChart": 2, "area3DChart": 2, "surfaceChart": 2,
    "line3DChart": 3, "surface3DChart": 3,
}


def _declared_axes(xml: str) -> dict[str, list[str]]:
    axes: dict[str, list[str]] = {}
    for kind, axid in _AXIS_DECL_RE.findall(xml):
        axes.setdefault(kind, []).append(axid)
    return axes


def _canonical_ids(axes: dict[str, list[str]], limit: int) -> list[str] | None:
    category = axes.get("catAx", []) + axes.get("dateAx", [])
    value = axes.get("valAx", [])
    series = axes.get("serAx", [])
    if len(category) != 1 or len(value) != 1 or len(series) > 1:
        return None
    ids = [category[0], value[0]]
    if limit >= 3 and series:
        ids.append(series[0])
    return ids


def _undeclared_axes(kind: str, block: str, axes: dict[str, list[str]]) -> list[str] | None:
    if kind not in AXID_LIMIT:
        return None
    ids = _AXID_RE.findall(block)
    declared = {i for group in axes.values() for i in group}
    if len([i for i in ids if i in declared]) >= 2:
        return None
    return ids


def _check_chart_axis_references(part: str, xml: str) -> list[str]:
    axes = _declared_axes(xml)
    problems: list[str] = []
    declared = {i for group in axes.values() for i in group}
    for match in _ANY_CHART_GROUP_RE.finditer(xml):
        kind, block = match.group(1), match.group(0)
        ids = _undeclared_axes(kind, block, axes)
        if ids is None:
            continue
        if not ids:
            problems.append(
                f"{part}: <c:{kind}> declares no <c:axId> this part can resolve; a chart "
                f"group needs {AXID_MINIMUM[kind]}, and PowerPoint discards one with fewer"
            )
            continue
        dead = [i for i in ids if i not in declared]
        canonical = _canonical_ids(axes, AXID_LIMIT[kind])
        if canonical is not None and len(canonical) >= AXID_MINIMUM[kind]:
            hint = f"Fix: point them at the axes this part declares ({', '.join(canonical)})"
        else:
            hint = ("Fix: the part declares several axes of a kind -- declare the "
                    "secondary axes the series expects, or drop them")
        detail = (f"of which {', '.join(dead)} name no declared axis"
                  if dead else f"only {len(ids)} of which this part declares")
        problems.append(
            f"{part}: <c:{kind}> references axId {', '.join(ids)}, {detail}, "
            f"leaving fewer than two live axes; PowerPoint discards the chart. {hint}"
        )
    return problems


def _ext_lst_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    depth = 0
    start = 0
    for match in re.finditer(r"<(/?)c:extLst\b[^>]*?(/?)>", text):
        closing, self_closing = match.group(1), match.group(2)
        if self_closing:
            continue
        if closing:
            depth -= 1
            if depth == 0:
                spans.append((start, match.end()))
        else:
            if depth == 0:
                start = match.start()
            depth += 1
    return spans


CHART_CHECKS = (_check_stacked_label_positions, _check_chart_axis_references)


def find_chart_problems(files: Mapping[str, bytes]) -> list[str]:
    problems: list[str] = []
    for part in sorted(n for n in files if _CHART_PART_RE.fullmatch(n)):
        xml = part_text(files[part])
        for check in CHART_CHECKS:
            problems.extend(check(part, xml))
    return problems
```

### `scripts/office/helpers/pptx_slide.py`

```python
"""Pick the slide-XML schema errors PowerPoint refuses the file over.

A denylist over lxml's messages, so an unrecognised error class is a miss rather
than a false alarm.
"""


from __future__ import annotations

import re

SLIDE_PART_RE = re.compile(
    r"ppt/(slides|slideLayouts|slideMasters|notesSlides|notesMasters|handoutMasters)"
    r"/[^/]+\.xml"
)

FATAL_SLIDE_ERRORS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(r"\}tableStyleId': This element is not expected"),
        "two <a:tableStyleId> in one <a:tblPr> (the schema allows one)",
    ),
    (
        re.compile(r"\}srgbClr', attribute 'val'"),
        "a colour that is not six hex digits",
    ),
    (
        re.compile(r"\}txBody': Missing child element"),
        "a <p:txBody> with no children",
    ),
    (
        re.compile(r"\}miter', attribute 'lim'"),
        'a line join with lim="NaN"',
    ),
    (
        re.compile(r"\}uLnTx': This element is not expected"),
        "<a:uLnTx> in a position the schema forbids",
    ),
    (
        re.compile(r"\}overrideClrMapping': This element is not expected"),
        "<p:overrideClrMapping> in a position the schema forbids",
    ),
    (
        re.compile(r"\}nvGrpSpPr': Missing child element"),
        "a <p:nvGrpSpPr> with no children",
    ),
)


def is_schema_verdict(error: str) -> bool:
    return error.startswith("Element ")


def fatal_slide_errors(errors: set[str]) -> list[str]:
    out = []
    for error in sorted(errors):
        for pattern, meaning in FATAL_SLIDE_ERRORS:
            if pattern.search(error):
                out.append(f"{meaning}: {error}")
                break
    return out
```

### `scripts/office/helpers/pptx_theme.py`

```python
"""Find masters sharing a theme part in the way PowerPoint refuses to open.

Reports only; the fix is to move <p:notesMasterIdLst> back to directly after
<p:sldIdLst> in ppt/presentation.xml.
"""


from __future__ import annotations

import posixpath
import re
from typing import Mapping

from . import part_text

THEME_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"

_MASTER_RE = re.compile(
    r"^ppt/(?P<group>slideMasters|notesMasters|handoutMasters)/"
    r"(?:slide|notes|handout)Master(?P<num>\d+)\.xml$"
)
_GROUP_ORDER = {"slideMasters": 0, "notesMasters": 1, "handoutMasters": 2}

_RELATIONSHIP_RE = re.compile(
    r"<Relationship\b[^>]*?(?:/>|>.*?</Relationship\s*>)", re.DOTALL
)


def _sort_key(name: str) -> tuple[int, int]:
    m = _MASTER_RE.match(name)
    assert m is not None
    return (_GROUP_ORDER[m.group("group")], int(m.group("num")))


def _rels_path(part: str) -> str:
    directory, base = posixpath.split(part)
    return f"{directory}/_rels/{base}.rels"


def _resolve(rels_path: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    part_dir = posixpath.dirname(posixpath.dirname(rels_path))
    return posixpath.normpath(posixpath.join(part_dir, target))


def _theme_rel(files: Mapping[str, bytes], master: str):
    rels_path = _rels_path(master)
    rels = files.get(rels_path)
    if rels is None:
        return None
    for element in _RELATIONSHIP_RE.findall(part_text(rels)):
        if f'Type="{THEME_REL_TYPE}"' not in element:
            continue
        target = re.search(r'\bTarget="([^"]+)"', element)
        if target is None:
            continue
        return rels_path, element, _resolve(rels_path, target.group(1))
    return None


def _masters(files: Mapping[str, bytes]) -> list[str]:
    return sorted((n for n in files if _MASTER_RE.match(n)), key=_sort_key)


_PRESENTATION = "ppt/presentation.xml"
_NOTES_MASTERS = "ppt/notesMasters/"
_IGNORABLE_RE = re.compile(r"<!--.*?-->|<\?.*?\?>", re.DOTALL)
_AFTER_SLDIDLST_RE = re.compile(
    r"<p:sldIdLst\b(?:[^>]*/>|[^>]*>.*?</p:sldIdLst\s*>)\s*(<[^>\s/]+)", re.DOTALL
)


def _notes_master_share_is_inert(files: Mapping[str, bytes]) -> bool:
    data = files.get(_PRESENTATION)
    if data is None:
        return False
    match = _AFTER_SLDIDLST_RE.search(_IGNORABLE_RE.sub("", part_text(data)))
    return match is not None and match.group(1) == "<p:notesMasterIdLst"


def _shares(files: Mapping[str, bytes]):
    owner: dict[str, str] = {}
    for master in _masters(files):
        found = _theme_rel(files, master)
        if found is None:
            continue
        rels_path, element, theme = found
        if theme not in files:
            continue  
        if theme in owner:
            yield master, rels_path, element, theme, owner[theme]
        else:
            owner[theme] = master


def _is_inert(master: str, inert_notes: bool) -> bool:
    return inert_notes and master.startswith(_NOTES_MASTERS)


def find_shared_master_themes(files: Mapping[str, bytes]) -> list[str]:
    return [
        f"{master} shares {theme} with {first}"
        for master, _, _, theme, first in _shares(files)
    ]


def live_shared_master_themes(files: Mapping[str, bytes]) -> list[str]:
    inert_notes = _notes_master_share_is_inert(files)
    return [
        f"{master} shares {theme} with {first}"
        for master, _, _, theme, first in _shares(files)
        if not _is_inert(master, inert_notes)
    ]
```

### `scripts/office/soffice.py`

```python
"""
Helper for running LibreOffice (soffice) in environments where AF_UNIX
sockets may be blocked (e.g., sandboxed VMs).  Detects the restriction
at runtime and applies an LD_PRELOAD shim if needed.

Usage:
    from office.soffice import run_soffice

    result = run_soffice(["--headless", "--convert-to", "pdf", "input.docx"])

Call soffice through run_soffice, not through subprocess with get_soffice_env():
the env dict carries the shim but names no user profile, and a non-root sandbox
cannot bootstrap the default one -- soffice aborts with "User installation could
not be completed" and converts nothing. get_soffice_env() stays public for the
callers that build their own argv (they must pass -env:UserInstallation too).
"""

import atexit
import contextlib
import os
import shutil
import socket
import subprocess
import tempfile
from collections.abc import Iterable
from pathlib import Path


# soffice inherits only these. LibreOffice needs a working process environment,
# not the caller's credentials, so the env is built from an allowlist rather than
# copied: an API key or token exported for the agent must not reach a converter
# subprocess just because it happened to be in scope.
FORWARDED_ENV_VARS = (
    # Locating soffice, its native libraries, and scratch space.
    "PATH", "HOME", "LD_LIBRARY_PATH", "TMPDIR", "TMP", "TEMP",
    # Locale decides number, date, and currency formatting in converted output.
    "LANG", "LANGUAGE", "LC_ALL", "LC_CTYPE", "LC_NUMERIC", "LC_TIME",
    # soffice writes its profile and cache under these when they are set.
    "XDG_RUNTIME_DIR", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME",
    # For callers that run against a real display instead of the svp backend.
    "DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY",
    "USER", "LOGNAME",
    # Windows needs these for process startup, temp files, and DLL resolution.
    "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT", "SYSTEMDRIVE",
    "APPDATA", "LOCALAPPDATA", "USERPROFILE",
    "PROGRAMFILES", "PROGRAMFILES(X86)", "PROGRAMDATA",
)


def get_soffice_env() -> dict:
    """Return a minimal environment for a soffice subprocess.

    Assembled from FORWARDED_ENV_VARS instead of inheriting the parent
    environment, so secrets in scope for the caller are not passed to soffice.
    """
    env = {name: os.environ[name] for name in FORWARDED_ENV_VARS if name in os.environ}
    env["SAL_USE_VCLPLUGIN"] = "svp"

    if _needs_shim():
        shim = _ensure_shim()
        env["LD_PRELOAD"] = str(shim)

    return env


def run_soffice(args: Iterable[str], **kwargs) -> subprocess.CompletedProcess:
    args = list(args)
    with contextlib.ExitStack() as stack:
        if not any(str(a).startswith("-env:UserInstallation") for a in args):
            profile = stack.enter_context(
                tempfile.TemporaryDirectory(prefix="lo_profile_", ignore_cleanup_errors=True)
            )
            args = [f"-env:UserInstallation={Path(profile).as_uri()}"] + args
        return subprocess.run(["soffice"] + args, env=get_soffice_env(), **kwargs)



#: Compiled once per process, not cached on disk between runs. An earlier version
#: built the shim at a fixed /tmp/lo_socket_shim.so and reused whatever was already
#: there, which let any local user pre-plant a shared object at that predictable
#: path and get it LD_PRELOADed into every subsequent soffice run. mkdtemp gives an
#: unpredictable directory created 0700 and owned by us, so neither the .c we
#: compile nor the .so we load can be swapped by another user.
_shim_so: Path | None = None


def _needs_shim() -> bool:
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.close()
        return False
    except OSError:
        return True


def _ensure_shim() -> Path:
    global _shim_so
    if _shim_so is not None and _shim_so.exists():
        return _shim_so

    shim_dir = Path(tempfile.mkdtemp(prefix="lo-shim-"))
    atexit.register(shutil.rmtree, shim_dir, True)

    src = shim_dir / "lo_socket_shim.c"
    so = shim_dir / "lo_socket_shim.so"
    src.write_text(_SHIM_SOURCE)
    subprocess.run(
        ["gcc", "-shared", "-fPIC", "-o", str(so), str(src), "-ldl"],
        check=True,
        capture_output=True,
    )
    src.unlink()
    _shim_so = so
    return _shim_so



_SHIM_SOURCE = r"""
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>

static int (*real_socket)(int, int, int);
static int (*real_socketpair)(int, int, int, int[2]);
static int (*real_listen)(int, int);
static int (*real_accept)(int, struct sockaddr *, socklen_t *);
static int (*real_close)(int);
static int (*real_read)(int, void *, size_t);

/* Per-FD bookkeeping (FDs >= 1024 are passed through unshimmed). */
static int is_shimmed[1024];
static int peer_of[1024];
static int wake_r[1024];            /* accept() blocks reading this */
static int wake_w[1024];            /* close()  writes to this      */
static int listener_fd = -1;        /* FD that received listen()    */

__attribute__((constructor))
static void init(void) {
    real_socket     = dlsym(RTLD_NEXT, "socket");
    real_socketpair = dlsym(RTLD_NEXT, "socketpair");
    real_listen     = dlsym(RTLD_NEXT, "listen");
    real_accept     = dlsym(RTLD_NEXT, "accept");
    real_close      = dlsym(RTLD_NEXT, "close");
    real_read       = dlsym(RTLD_NEXT, "read");
    for (int i = 0; i < 1024; i++) {
        peer_of[i] = -1;
        wake_r[i]  = -1;
        wake_w[i]  = -1;
    }
}

/* ---- socket ---------------------------------------------------------- */
int socket(int domain, int type, int protocol) {
    if (domain == AF_UNIX) {
        int fd = real_socket(domain, type, protocol);
        if (fd >= 0) return fd;
        /* socket(AF_UNIX) blocked – fall back to socketpair(). */
        int sv[2];
        if (real_socketpair(domain, type, protocol, sv) == 0) {
            if (sv[0] >= 0 && sv[0] < 1024) {
                is_shimmed[sv[0]] = 1;
                peer_of[sv[0]]    = sv[1];
                int wp[2];
                if (pipe(wp) == 0) {
                    wake_r[sv[0]] = wp[0];
                    wake_w[sv[0]] = wp[1];
                }
            }
            return sv[0];
        }
        errno = EPERM;
        return -1;
    }
    return real_socket(domain, type, protocol);
}

/* ---- listen ---------------------------------------------------------- */
int listen(int sockfd, int backlog) {
    if (sockfd >= 0 && sockfd < 1024 && is_shimmed[sockfd]) {
        listener_fd = sockfd;
        return 0;
    }
    return real_listen(sockfd, backlog);
}

/* ---- accept ---------------------------------------------------------- */
int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen) {
    if (sockfd >= 0 && sockfd < 1024 && is_shimmed[sockfd]) {
        /* Block until close() writes to the wake pipe. */
        if (wake_r[sockfd] >= 0) {
            char buf;
            real_read(wake_r[sockfd], &buf, 1);
        }
        errno = ECONNABORTED;
        return -1;
    }
    return real_accept(sockfd, addr, addrlen);
}

/* ---- close ----------------------------------------------------------- */
int close(int fd) {
    if (fd >= 0 && fd < 1024 && is_shimmed[fd]) {
        int was_listener = (fd == listener_fd);
        is_shimmed[fd] = 0;

        if (wake_w[fd] >= 0) {              /* unblock accept() */
            char c = 0;
            write(wake_w[fd], &c, 1);
            real_close(wake_w[fd]);
            wake_w[fd] = -1;
        }
        if (wake_r[fd] >= 0) { real_close(wake_r[fd]); wake_r[fd]  = -1; }
        if (peer_of[fd] >= 0) { real_close(peer_of[fd]); peer_of[fd] = -1; }

        if (was_listener)
            _exit(0);                        /* conversion done – exit */
    }
    return real_close(fd);
}
"""



if __name__ == "__main__":
    import sys
    result = run_soffice(sys.argv[1:])
    sys.exit(result.returncode)
```

### `scripts/office/validate.py`

```python
"""
Command line tool to validate Office document XML files against XSD schemas and tracked changes.

Usage:
    python validate.py <path> [--original <original_file>] [--auto-repair] [--author NAME]

The first argument can be either:
- An unpacked directory containing the Office document XML files
- A packed Office file (.docx/.pptx/.xlsx or .dotx/.potx/.xltx template) which will be unpacked to a temp directory

Auto-repair fixes:
- paraId/durableId values that exceed OOXML limits
- Missing xml:space="preserve" on w:t elements with whitespace
"""

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path

import defusedxml.ElementTree as ET
from defusedxml.common import DefusedXmlException

from helpers import OOXML_FAMILY, rezip, safe_extract
from validators import DOCXSchemaValidator, PPTXSchemaValidator, RedliningValidator

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _fail(message: str):
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(2)


def _has_tracked_changes(unpacked_dir: Path) -> bool:
    document = unpacked_dir / "word" / "document.xml"
    if not document.is_file():
        return False
    try:
        root = ET.parse(document).getroot()
    except (ET.ParseError, DefusedXmlException):
        return False  
    tracked = {f"{{{WORD_NS}}}ins", f"{{{WORD_NS}}}del"}
    return any(elem.tag in tracked for elem in root.iter())


def main():
    parser = argparse.ArgumentParser(description="Validate Office document XML files")
    parser.add_argument(
        "path",
        help="Path to unpacked directory or packed Office file (.docx/.pptx/.xlsx or .dotx/.potx/.xltx)",
    )
    parser.add_argument(
        "--original",
        required=False,
        default=None,
        help="Path to original file (.docx/.pptx/.xlsx or .dotx/.potx/.xltx). If omitted, all XSD errors are reported and redlining validation is skipped.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help="Automatically repair common issues (hex IDs, whitespace preservation). "
        "Modifies the input in place: repairs to a packed file are written back to it.",
    )
    parser.add_argument(
        "--author",
        default=None,
        help="The name you are redlining under. Passing it turns on the "
        "tracked-change check: any text differing from --original without a "
        "<w:ins>/<w:del> recording it is reported. Untracked edits carry no "
        "author, so the check covers them whoever made them — the name marks "
        "the run as redlining work and is not used to filter. Requires "
        "--original; docx only.",
    )
    args = parser.parse_args()

    if args.author is not None and not args.original:
        _fail("--author requires --original")

    path = Path(args.path)
    if not path.exists():
        _fail(f"{path} does not exist")

    original_file = None
    if args.original:
        original_file = Path(args.original)
        if not original_file.is_file():
            _fail(f"{original_file} is not a file")
        if original_file.suffix.lower() not in OOXML_FAMILY:
            _fail(f"{original_file} must be one of: {', '.join(sorted(OOXML_FAMILY))}")

    family = OOXML_FAMILY.get((original_file or path).suffix.lower())
    if family is None:
        _fail(
            f"Cannot determine file type from {path}. Use --original or provide one of: {', '.join(sorted(OOXML_FAMILY))}."
        )

    if args.author is not None and family != "docx":
        _fail(f"--author only applies to docx files, not {family}")

    packed_file = None
    temp_dir_ctx = None
    if path.is_file() and path.suffix.lower() in OOXML_FAMILY:
        packed_file = path
        temp_dir_ctx = tempfile.TemporaryDirectory()
        unpacked_dir = Path(temp_dir_ctx.name)
        try:
            with zipfile.ZipFile(path, "r") as zf:
                safe_extract(zf, unpacked_dir)
        except (zipfile.BadZipFile, ValueError, OSError) as e:
            _fail(f"cannot unpack {path}: {e}")
    else:
        if not path.is_dir():
            _fail(f"{path} is not a directory or Office file")
        unpacked_dir = path

    match family:
        case "docx":
            validators = [
                DOCXSchemaValidator(unpacked_dir, original_file, verbose=args.verbose),
            ]
            if args.author is not None:
                validators.append(
                    RedliningValidator(unpacked_dir, original_file, verbose=args.verbose)  
                )
            elif original_file and _has_tracked_changes(unpacked_dir):
                print(
                    "Note: this document has tracked changes; they were not "
                    "checked against the original (pass --author to check)."
                )
        case "pptx":
            validators = [
                PPTXSchemaValidator(unpacked_dir, original_file, verbose=args.verbose),
            ]
        case "xlsx":
            exts = ", ".join(k for k, v in sorted(OOXML_FAMILY.items()) if v == "xlsx")
            print(
                f"No XSD schema validation is performed for xlsx-family files ({exts}). "
                "For formula-error checking, use scripts/recalc.py instead."
            )
            sys.exit(0)
        case _:
            print(f"Error: Validation not supported for file type {family}")
            sys.exit(1)

    if args.auto_repair:
        total_repairs = sum(v.repair() for v in validators)
        if total_repairs:
            print(f"Auto-repaired {total_repairs} issue(s)")
            if packed_file is not None:
                rezip(unpacked_dir, packed_file)
                print(f"Wrote repaired file to {packed_file}")

    success = all([v.validate() for v in validators])

    if temp_dir_ctx is not None:
        temp_dir_ctx.cleanup()

    if success:
        print("All validations PASSED!")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

### `scripts/office/validators/__init__.py`

```python
"""
Validation modules for Word document processing.
"""

from .base import BaseSchemaValidator
from .docx import DOCXSchemaValidator
from .pptx import PPTXSchemaValidator
from .redlining import RedliningValidator

__all__ = [
    "BaseSchemaValidator",
    "DOCXSchemaValidator",
    "PPTXSchemaValidator",
    "RedliningValidator",
]
```

### `scripts/office/validators/base.py`

```python
"""
Base validator with common validation logic for document files.
"""

import re
from pathlib import Path

import defusedxml.minidom
from functools import lru_cache

import lxml.etree

from helpers import safe_extract


@lru_cache(maxsize=None)
def _load_schema(schema_path: str):
    with open(schema_path, "rb") as xsd_file:
        xsd_doc = lxml.etree.parse(
            xsd_file, parser=lxml.etree.XMLParser(), base_url=schema_path
        )
    return lxml.etree.XMLSchema(xsd_doc)

class BaseSchemaValidator:

    IGNORED_VALIDATION_ERRORS = [
        "hyphenationZone",
        "purl.org/dc/terms",
    ]

    UNIQUE_ID_REQUIREMENTS = {
        "comment": ("id", "file"),  
        "commentrangestart": ("id", "file"),  
        "commentrangeend": ("id", "file"),  
        "bookmarkstart": ("id", "file"),  
        "bookmarkend": ("id", "file"),  
        "sldid": ("id", "file"),  
        "sldmasterid": ("id", "global"),  
        "sldlayoutid": ("id", "global"),  
        "cm": ("authorid", "file"),  
        "sheet": ("sheetid", "file"),  
        "definedname": ("id", "file"),  
        "cxnsp": ("id", "file"),  
        "sp": ("id", "file"),  
        "pic": ("id", "file"),  
        "grpsp": ("id", "file"),  
    }

    EXCLUDED_ID_CONTAINERS = {
        "sectionlst",  
    }

    ELEMENT_RELATIONSHIP_TYPES = {}

    SCHEMA_MAPPINGS = {
        "word": "ISO-IEC29500-4_2016/wml.xsd",  
        "ppt": "ISO-IEC29500-4_2016/pml.xsd",  
        "xl": "ISO-IEC29500-4_2016/sml.xsd",  
        "[Content_Types].xml": "ecma/fouth-edition/opc-contentTypes.xsd",
        "app.xml": "ISO-IEC29500-4_2016/shared-documentPropertiesExtended.xsd",
        "core.xml": "ecma/fouth-edition/opc-coreProperties.xsd",
        "custom.xml": "ISO-IEC29500-4_2016/shared-documentPropertiesCustom.xsd",
        ".rels": "ecma/fouth-edition/opc-relationships.xsd",
        "people.xml": "microsoft/wml-2012.xsd",
        "commentsIds.xml": "microsoft/wml-cid-2016.xsd",
        "commentsExtensible.xml": "microsoft/wml-cex-2018.xsd",
        "commentsExtended.xml": "microsoft/wml-2012.xsd",
        "chart": "ISO-IEC29500-4_2016/dml-chart.xsd",
        "theme": "ISO-IEC29500-4_2016/dml-main.xsd",
        "drawing": "ISO-IEC29500-4_2016/dml-main.xsd",
    }

    MC_NAMESPACE = "http://schemas.openxmlformats.org/markup-compatibility/2006"
    XML_NAMESPACE = "http://www.w3.org/XML/1998/namespace"

    PACKAGE_RELATIONSHIPS_NAMESPACE = (
        "http://schemas.openxmlformats.org/package/2006/relationships"
    )
    OFFICE_RELATIONSHIPS_NAMESPACE = (
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    )
    CONTENT_TYPES_NAMESPACE = (
        "http://schemas.openxmlformats.org/package/2006/content-types"
    )

    MAIN_CONTENT_FOLDERS = {"word", "ppt", "xl"}

    OOXML_NAMESPACES = {
        "http://schemas.openxmlformats.org/officeDocument/2006/math",
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "http://schemas.openxmlformats.org/schemaLibrary/2006/main",
        "http://schemas.openxmlformats.org/drawingml/2006/main",
        "http://schemas.openxmlformats.org/drawingml/2006/chart",
        "http://schemas.openxmlformats.org/drawingml/2006/chartDrawing",
        "http://schemas.openxmlformats.org/drawingml/2006/diagram",
        "http://schemas.openxmlformats.org/drawingml/2006/picture",
        "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
        "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
        "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "http://schemas.openxmlformats.org/presentationml/2006/main",
        "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "http://schemas.openxmlformats.org/officeDocument/2006/sharedTypes",
        "http://www.w3.org/XML/1998/namespace",
    }

    def __init__(self, unpacked_dir, original_file=None, verbose=False):
        self.unpacked_dir = Path(unpacked_dir).resolve()
        self.original_file = Path(original_file) if original_file else None
        self.verbose = verbose

        self.schemas_dir = Path(__file__).parent.parent / "schemas"

        patterns = ["*.xml", "*.rels"]
        self.xml_files = [
            f for pattern in patterns for f in self.unpacked_dir.rglob(pattern)
        ]

        if not self.xml_files:
            print(f"Warning: No XML files found in {self.unpacked_dir}")

    def validate(self):
        raise NotImplementedError("Subclasses must implement the validate method")

    def repair(self) -> int:
        return self.repair_whitespace_preservation()

    def repair_whitespace_preservation(self) -> int:
        repairs = 0

        for xml_file in self.xml_files:
            try:
                content = xml_file.read_text(encoding="utf-8")
                dom = defusedxml.minidom.parseString(content)
                pending = []  

                for elem in dom.getElementsByTagName("*"):
                    local_name = elem.tagName.rsplit(":", 1)[-1]
                    if local_name in ("t", "delText", "instrText", "delInstrText"):
                        text = "".join(
                            child.data
                            for child in elem.childNodes
                            if child.nodeType in (child.TEXT_NODE, child.CDATA_SECTION_NODE)
                        )
                        ws = (" ", "\t", "\n", "\r")
                        if text and (text.startswith(ws) or text.endswith(ws)):
                            if elem.getAttribute("xml:space") != "preserve":
                                elem.setAttribute("xml:space", "preserve")
                                text_preview = repr(text[:30]) + "..." if len(text) > 30 else repr(text)
                                pending.append(f"  Repaired: {xml_file.name}: Added xml:space='preserve' to {elem.tagName}: {text_preview}")

                if pending:
                    xml_file.write_bytes(dom.toxml(encoding="UTF-8"))
                    for message in pending:
                        print(message)
                    repairs += len(pending)

            except Exception:
                pass

        return repairs

    def validate_xml(self):
        errors = []

        for xml_file in self.xml_files:
            try:
                lxml.etree.parse(str(xml_file))
            except lxml.etree.XMLSyntaxError as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: "
                    f"Line {e.lineno}: {e.msg}"
                )
            except Exception as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: "
                    f"Unexpected error: {str(e)}"
                )

        if errors:
            print(f"FAILED - Found {len(errors)} XML violations:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - All XML files are well-formed")
            return True

    def validate_namespaces(self):
        errors = []

        for xml_file in self.xml_files:
            try:
                root = lxml.etree.parse(str(xml_file)).getroot()
                declared = set(root.nsmap.keys()) - {None}  

                for attr_val in [
                    v for k, v in root.attrib.items() if k.endswith("Ignorable")
                ]:
                    undeclared = set(attr_val.split()) - declared
                    errors.extend(
                        f"  {xml_file.relative_to(self.unpacked_dir)}: "
                        f"Namespace '{ns}' in Ignorable but not declared"
                        for ns in undeclared
                    )
            except lxml.etree.XMLSyntaxError:
                continue

        if errors:
            print(f"FAILED - {len(errors)} namespace issues:")
            for error in errors:
                print(error)
            return False
        if self.verbose:
            print("PASSED - All namespace prefixes properly declared")
        return True

    def validate_unique_ids(self):
        errors = []
        global_ids = {}  

        for xml_file in self.xml_files:
            try:
                root = lxml.etree.parse(str(xml_file)).getroot()
                file_ids = {}  

                mc_elements = root.xpath(
                    ".//mc:AlternateContent", namespaces={"mc": self.MC_NAMESPACE}
                )
                for elem in mc_elements:
                    elem.getparent().remove(elem)

                for elem in root.iter():
                    if not hasattr(elem, "tag") or callable(elem.tag):
                        continue
                    tag = (
                        elem.tag.split("}")[-1].lower()
                        if "}" in elem.tag
                        else elem.tag.lower()
                    )

                    if tag in self.UNIQUE_ID_REQUIREMENTS:
                        in_excluded_container = any(
                            ancestor.tag.split("}")[-1].lower() in self.EXCLUDED_ID_CONTAINERS
                            for ancestor in elem.iterancestors()
                        )
                        if in_excluded_container:
                            continue

                        attr_name, scope = self.UNIQUE_ID_REQUIREMENTS[tag]

                        id_value = None
                        for attr, value in elem.attrib.items():
                            attr_local = (
                                attr.split("}")[-1].lower()
                                if "}" in attr
                                else attr.lower()
                            )
                            if attr_local == attr_name:
                                id_value = value
                                break

                        if id_value is not None:
                            if scope == "global":
                                if id_value in global_ids:
                                    prev_file, prev_line, prev_tag = global_ids[
                                        id_value
                                    ]
                                    errors.append(
                                        f"  {xml_file.relative_to(self.unpacked_dir)}: "
                                        f"Line {elem.sourceline}: Global ID '{id_value}' in <{tag}> "
                                        f"already used in {prev_file} at line {prev_line} in <{prev_tag}>"
                                    )
                                else:
                                    global_ids[id_value] = (
                                        xml_file.relative_to(self.unpacked_dir),
                                        elem.sourceline,
                                        tag,
                                    )
                            elif scope == "file":
                                key = (tag, attr_name)
                                if key not in file_ids:
                                    file_ids[key] = {}

                                if id_value in file_ids[key]:
                                    prev_line = file_ids[key][id_value]
                                    errors.append(
                                        f"  {xml_file.relative_to(self.unpacked_dir)}: "
                                        f"Line {elem.sourceline}: Duplicate {attr_name}='{id_value}' in <{tag}> "
                                        f"(first occurrence at line {prev_line})"
                                    )
                                else:
                                    file_ids[key][id_value] = elem.sourceline

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"FAILED - Found {len(errors)} ID uniqueness violations:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - All required IDs are unique")
            return True

    def validate_file_references(self):
        errors = []

        rels_files = list(self.unpacked_dir.rglob("*.rels"))

        if not rels_files:
            if self.verbose:
                print("PASSED - No .rels files found")
            return True

        all_files = []
        for file_path in self.unpacked_dir.rglob("*"):
            if (
                file_path.is_file()
                and file_path.name != "[Content_Types].xml"
                and not file_path.name.endswith(".rels")
            ):  
                all_files.append(file_path.resolve())

        all_referenced_files = set()

        if self.verbose:
            print(
                f"Found {len(rels_files)} .rels files and {len(all_files)} target files"
            )

        for rels_file in rels_files:
            try:
                rels_root = lxml.etree.parse(str(rels_file)).getroot()

                rels_dir = rels_file.parent

                referenced_files = set()
                broken_refs = []

                for rel in rels_root.findall(
                    ".//ns:Relationship",
                    namespaces={"ns": self.PACKAGE_RELATIONSHIPS_NAMESPACE},
                ):
                    target = rel.get("Target")
                    if rel.get("TargetMode") == "External":
                        continue
                    if target and not target.startswith(
                        ("http", "mailto:")
                    ):  
                        if target.startswith("/"):
                            target_path = self.unpacked_dir / target.lstrip("/")
                        elif rels_file.name == ".rels":
                            target_path = self.unpacked_dir / target
                        else:
                            base_dir = rels_dir.parent
                            target_path = base_dir / target

                        try:
                            target_path = target_path.resolve()
                            if target_path.exists() and target_path.is_file():
                                referenced_files.add(target_path)
                                all_referenced_files.add(target_path)
                            else:
                                broken_refs.append((target, rel.sourceline))
                        except (OSError, ValueError):
                            broken_refs.append((target, rel.sourceline))

                if broken_refs:
                    rel_path = rels_file.relative_to(self.unpacked_dir)
                    for broken_ref, line_num in broken_refs:
                        errors.append(
                            f"  {rel_path}: Line {line_num}: Broken reference to {broken_ref}"
                        )

            except Exception as e:
                rel_path = rels_file.relative_to(self.unpacked_dir)
                errors.append(f"  Error parsing {rel_path}: {e}")

        unreferenced_files = set(all_files) - all_referenced_files

        if unreferenced_files:
            for unref_file in sorted(unreferenced_files):
                unref_rel_path = unref_file.relative_to(self.unpacked_dir)
                errors.append(f"  Unreferenced file: {unref_rel_path}")

        if errors:
            print(f"FAILED - Found {len(errors)} relationship validation errors:")
            for error in errors:
                print(error)
            print(
                "CRITICAL: These errors will cause the document to appear corrupt. "
                + "Broken references MUST be fixed, "
                + "and unreferenced files MUST be referenced or removed."
            )
            return False
        else:
            if self.verbose:
                print(
                    "PASSED - All references are valid and all files are properly referenced"
                )
            return True

    def validate_all_relationship_ids(self):
        import lxml.etree

        errors = []

        for xml_file in self.xml_files:
            if xml_file.suffix == ".rels":
                continue

            rels_dir = xml_file.parent / "_rels"
            rels_file = rels_dir / f"{xml_file.name}.rels"

            if not rels_file.exists():
                continue

            try:
                rels_root = lxml.etree.parse(str(rels_file)).getroot()
                rid_to_type = {}

                for rel in rels_root.findall(
                    f".//{{{self.PACKAGE_RELATIONSHIPS_NAMESPACE}}}Relationship"
                ):
                    rid = rel.get("Id")
                    rel_type = rel.get("Type", "")
                    if rid:
                        if rid in rid_to_type:
                            rels_rel_path = rels_file.relative_to(self.unpacked_dir)
                            errors.append(
                                f"  {rels_rel_path}: Line {rel.sourceline}: "
                                f"Duplicate relationship ID '{rid}' (IDs must be unique)"
                            )
                        type_name = (
                            rel_type.split("/")[-1] if "/" in rel_type else rel_type
                        )
                        rid_to_type[rid] = type_name

                xml_root = lxml.etree.parse(str(xml_file)).getroot()

                r_ns = self.OFFICE_RELATIONSHIPS_NAMESPACE
                rid_attrs_to_check = ["id", "embed", "link"]
                for elem in xml_root.iter():
                    if not hasattr(elem, "tag") or callable(elem.tag):
                        continue
                    for attr_name in rid_attrs_to_check:
                        rid_attr = elem.get(f"{{{r_ns}}}{attr_name}")
                        if not rid_attr:
                            continue
                        xml_rel_path = xml_file.relative_to(self.unpacked_dir)
                        elem_name = (
                            elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                        )

                        if rid_attr not in rid_to_type:
                            errors.append(
                                f"  {xml_rel_path}: Line {elem.sourceline}: "
                                f"<{elem_name}> r:{attr_name} references non-existent relationship '{rid_attr}' "
                                f"(valid IDs: {', '.join(sorted(rid_to_type.keys())[:5])}{'...' if len(rid_to_type) > 5 else ''})"
                            )
                        elif attr_name == "id" and self.ELEMENT_RELATIONSHIP_TYPES:
                            expected_type = self._get_expected_relationship_type(
                                elem_name
                            )
                            if expected_type:
                                actual_type = rid_to_type[rid_attr]
                                if expected_type not in actual_type.lower():
                                    errors.append(
                                        f"  {xml_rel_path}: Line {elem.sourceline}: "
                                        f"<{elem_name}> references '{rid_attr}' which points to '{actual_type}' "
                                        f"but should point to a '{expected_type}' relationship"
                                    )

            except Exception as e:
                xml_rel_path = xml_file.relative_to(self.unpacked_dir)
                errors.append(f"  Error processing {xml_rel_path}: {e}")

        if errors:
            print(f"FAILED - Found {len(errors)} relationship ID reference errors:")
            for error in errors:
                print(error)
            print("\nThese ID mismatches will cause the document to appear corrupt!")
            return False
        else:
            if self.verbose:
                print("PASSED - All relationship ID references are valid")
            return True

    def _get_expected_relationship_type(self, element_name):
        elem_lower = element_name.lower()

        if elem_lower in self.ELEMENT_RELATIONSHIP_TYPES:
            return self.ELEMENT_RELATIONSHIP_TYPES[elem_lower]

        if elem_lower.endswith("id") and len(elem_lower) > 2:
            prefix = elem_lower[:-2]  
            if prefix.endswith("master"):
                return prefix.lower()
            elif prefix.endswith("layout"):
                return prefix.lower()
            else:
                if prefix == "sld":
                    return "slide"
                return prefix.lower()

        if elem_lower.endswith("reference") and len(elem_lower) > 9:
            prefix = elem_lower[:-9]  
            return prefix.lower()

        return None

    def validate_content_types(self):
        errors = []

        content_types_file = self.unpacked_dir / "[Content_Types].xml"
        if not content_types_file.exists():
            print("FAILED - [Content_Types].xml file not found")
            return False

        try:
            root = lxml.etree.parse(str(content_types_file)).getroot()
            declared_parts = set()
            declared_extensions = set()

            for override in root.findall(
                f".//{{{self.CONTENT_TYPES_NAMESPACE}}}Override"
            ):
                part_name = override.get("PartName")
                if part_name is not None:
                    declared_parts.add(part_name.lstrip("/"))

            for default in root.findall(
                f".//{{{self.CONTENT_TYPES_NAMESPACE}}}Default"
            ):
                extension = default.get("Extension")
                if extension is not None:
                    declared_extensions.add(extension.lower())

            declarable_roots = {
                "sld",
                "sldLayout",
                "sldMaster",
                "presentation",  
                "document",  
                "workbook",
                "worksheet",  
                "theme",  
            }

            media_extensions = {
                "png": "image/png",
                "jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "gif": "image/gif",
                "bmp": "image/bmp",
                "tiff": "image/tiff",
                "wmf": "image/x-wmf",
                "emf": "image/x-emf",
            }

            all_files = list(self.unpacked_dir.rglob("*"))
            all_files = [f for f in all_files if f.is_file()]

            for xml_file in self.xml_files:
                path_str = str(xml_file.relative_to(self.unpacked_dir)).replace(
                    "\\", "/"
                )

                if any(
                    skip in path_str
                    for skip in [".rels", "[Content_Types]", "docProps/", "_rels/"]
                ):
                    continue

                try:
                    root_tag = lxml.etree.parse(str(xml_file)).getroot().tag
                    root_name = root_tag.split("}")[-1] if "}" in root_tag else root_tag

                    if root_name in declarable_roots and path_str not in declared_parts:
                        errors.append(
                            f"  {path_str}: File with <{root_name}> root not declared in [Content_Types].xml"
                        )

                except Exception:
                    continue  

            for file_path in all_files:
                if file_path.suffix.lower() in {".xml", ".rels"}:
                    continue
                if file_path.name == "[Content_Types].xml":
                    continue
                if "_rels" in file_path.parts or "docProps" in file_path.parts:
                    continue

                extension = file_path.suffix.lstrip(".").lower()
                if extension and extension not in declared_extensions:
                    if extension in media_extensions:
                        relative_path = file_path.relative_to(self.unpacked_dir)
                        errors.append(
                            f'  {relative_path}: File with extension \'{extension}\' not declared in [Content_Types].xml - should add: <Default Extension="{extension}" ContentType="{media_extensions[extension]}"/>'
                        )

        except Exception as e:
            errors.append(f"  Error parsing [Content_Types].xml: {e}")

        if errors:
            print(f"FAILED - Found {len(errors)} content type declaration errors:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print(
                    "PASSED - All content files are properly declared in [Content_Types].xml"
                )
            return True

    def validate_file_against_xsd(self, xml_file, verbose=False):
        xml_file = Path(xml_file).resolve()
        unpacked_dir = self.unpacked_dir.resolve()

        is_valid, current_errors = self._validate_single_file_xsd(
            xml_file, unpacked_dir
        )

        if is_valid is None:
            return None, set()  
        elif is_valid:
            return True, set()  

        original_errors = self._get_original_file_errors(xml_file)

        assert current_errors is not None
        new_errors = current_errors - original_errors

        new_errors = {
            e for e in new_errors
            if not any(pattern in e for pattern in self.IGNORED_VALIDATION_ERRORS)
        }

        if new_errors:
            if verbose:
                relative_path = xml_file.relative_to(unpacked_dir)
                print(f"FAILED - {relative_path}: {len(new_errors)} new error(s)")
                for error in list(new_errors)[:3]:
                    truncated = error[:250] + "..." if len(error) > 250 else error
                    print(f"  - {truncated}")
            return False, new_errors
        else:
            if verbose:
                print(
                    f"PASSED - No new errors (original had {len(current_errors)} errors)"
                )
            return True, set()

    def validate_against_xsd(self):
        new_errors = []
        original_error_count = 0
        valid_count = 0
        skipped_count = 0

        for xml_file in self.xml_files:
            relative_path = str(xml_file.relative_to(self.unpacked_dir))
            is_valid, new_file_errors = self.validate_file_against_xsd(
                xml_file, verbose=False
            )

            if is_valid is None:
                skipped_count += 1
                continue
            elif is_valid and not new_file_errors:
                valid_count += 1
                continue
            elif is_valid:
                original_error_count += 1
                valid_count += 1
                continue

            new_errors.append(f"  {relative_path}: {len(new_file_errors)} new error(s)")
            for error in list(new_file_errors)[:3]:  
                new_errors.append(
                    f"    - {error[:250]}..." if len(error) > 250 else f"    - {error}"
                )

        if self.verbose:
            print(f"Validated {len(self.xml_files)} files:")
            print(f"  - Valid: {valid_count}")
            print(f"  - Skipped (no schema): {skipped_count}")
            if original_error_count:
                print(f"  - With original errors (ignored): {original_error_count}")
            print(
                f"  - With NEW errors: {len(new_errors) > 0 and len([e for e in new_errors if not e.startswith('    ')]) or 0}"
            )

        if new_errors:
            print("\nFAILED - Found NEW validation errors:")
            for error in new_errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("\nPASSED - No new XSD validation errors introduced")
            return True

    def _get_schema_path(self, xml_file):
        if xml_file.name in self.SCHEMA_MAPPINGS:
            return self.schemas_dir / self.SCHEMA_MAPPINGS[xml_file.name]

        if xml_file.suffix == ".rels":
            return self.schemas_dir / self.SCHEMA_MAPPINGS[".rels"]

        if "charts/" in str(xml_file) and xml_file.name.startswith("chart"):
            return self.schemas_dir / self.SCHEMA_MAPPINGS["chart"]

        if "theme/" in str(xml_file) and xml_file.name.startswith("theme"):
            return self.schemas_dir / self.SCHEMA_MAPPINGS["theme"]

        if xml_file.parent.name in self.MAIN_CONTENT_FOLDERS:
            return self.schemas_dir / self.SCHEMA_MAPPINGS[xml_file.parent.name]

        return None

    def _clean_ignorable_namespaces(self, xml_doc):
        xml_string = lxml.etree.tostring(xml_doc, encoding="unicode")
        xml_copy = lxml.etree.fromstring(xml_string)

        for elem in xml_copy.iter():
            attrs_to_remove = []

            for attr in elem.attrib:
                if "{" in attr:
                    ns = attr.split("}")[0][1:]
                    if ns not in self.OOXML_NAMESPACES:
                        attrs_to_remove.append(attr)

            for attr in attrs_to_remove:
                del elem.attrib[attr]

        self._remove_ignorable_elements(xml_copy)

        return lxml.etree.ElementTree(xml_copy)

    def _remove_ignorable_elements(self, root):
        elements_to_remove = []

        for elem in list(root):
            if not hasattr(elem, "tag") or callable(elem.tag):
                continue

            tag_str = str(elem.tag)
            if tag_str.startswith("{"):
                ns = tag_str.split("}")[0][1:]
                if ns not in self.OOXML_NAMESPACES:
                    elements_to_remove.append(elem)
                    continue

            self._remove_ignorable_elements(elem)

        for elem in elements_to_remove:
            root.remove(elem)

    def _preprocess_for_mc_ignorable(self, xml_doc):
        root = xml_doc.getroot()

        if f"{{{self.MC_NAMESPACE}}}Ignorable" in root.attrib:
            del root.attrib[f"{{{self.MC_NAMESPACE}}}Ignorable"]

        return xml_doc

    def _preprocess_for_schema(self, xml_doc, relative_path):
        return xml_doc

    def _validate_single_file_xsd(self, xml_file, base_path, schema_path=None):
        schema_path = schema_path or self._get_schema_path(xml_file)
        if not schema_path:
            return None, None  

        try:
            schema = _load_schema(str(schema_path))

            with open(xml_file, "r") as f:
                xml_doc = lxml.etree.parse(f)

            xml_doc, _ = self._remove_template_tags_from_text_nodes(xml_doc)
            xml_doc = self._preprocess_for_mc_ignorable(xml_doc)

            relative_path = xml_file.relative_to(base_path)
            if (
                relative_path.parts
                and relative_path.parts[0] in self.MAIN_CONTENT_FOLDERS
            ):
                xml_doc = self._clean_ignorable_namespaces(xml_doc)

            xml_doc = self._preprocess_for_schema(xml_doc, relative_path)

            if schema.validate(xml_doc):
                return True, set()
            else:
                errors = set()
                for error in schema.error_log:
                    errors.add(error.message)
                return False, errors

        except Exception as e:
            return False, {str(e)}

    def _get_original_file_errors(self, xml_file, schema_path=None):
        if self.original_file is None:
            return set()

        import tempfile
        import zipfile

        xml_file = Path(xml_file).resolve()
        unpacked_dir = self.unpacked_dir.resolve()
        relative_path = xml_file.relative_to(unpacked_dir)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                with zipfile.ZipFile(self.original_file, "r") as zip_ref:
                    safe_extract(zip_ref, temp_path)
            except (zipfile.BadZipFile, ValueError, OSError):
                return set()

            original_xml_file = temp_path / relative_path

            if not original_xml_file.exists():
                return set()

            is_valid, errors = self._validate_single_file_xsd(
                original_xml_file, temp_path, schema_path=schema_path
            )
            return errors if errors else set()

    def _remove_template_tags_from_text_nodes(self, xml_doc):
        warnings = []
        template_pattern = re.compile(r"\{\{[^}]*\}\}")

        xml_string = lxml.etree.tostring(xml_doc, encoding="unicode")
        xml_copy = lxml.etree.fromstring(xml_string)

        def process_text_content(text, content_type):
            if not text:
                return text
            matches = list(template_pattern.finditer(text))
            if matches:
                for match in matches:
                    warnings.append(
                        f"Found template tag in {content_type}: {match.group()}"
                    )
                return template_pattern.sub("", text)
            return text

        for elem in xml_copy.iter():
            if not hasattr(elem, "tag") or callable(elem.tag):
                continue
            tag_str = str(elem.tag)
            if tag_str.endswith("}t") or tag_str == "t":
                continue

            elem.text = process_text_content(elem.text, "text content")
            elem.tail = process_text_content(elem.tail, "tail content")

        return lxml.etree.ElementTree(xml_copy), warnings


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly.")
```

### `scripts/office/validators/docx.py`

```python
"""
Validator for Word document XML files against XSD schemas.
"""

import random
import re
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom
import lxml.etree

from helpers import safe_extract

from .base import BaseSchemaValidator


class DOCXSchemaValidator(BaseSchemaValidator):

    WORD_2006_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    W14_NAMESPACE = "http://schemas.microsoft.com/office/word/2010/wordml"
    W16CID_NAMESPACE = "http://schemas.microsoft.com/office/word/2016/wordml/cid"

    ELEMENT_RELATIONSHIP_TYPES = {}

    def validate(self):
        if not self.validate_xml():
            return False

        all_valid = True
        if not self.validate_namespaces():
            all_valid = False

        if not self.validate_unique_ids():
            all_valid = False

        if not self.validate_file_references():
            all_valid = False

        if not self.validate_content_types():
            all_valid = False

        if not self.validate_against_xsd():
            all_valid = False

        if not self.validate_whitespace_preservation():
            all_valid = False

        if not self.validate_deletions():
            all_valid = False

        if not self.validate_insertions():
            all_valid = False

        if not self.validate_all_relationship_ids():
            all_valid = False

        if not self.validate_id_constraints():
            all_valid = False

        if not self.validate_comment_markers():
            all_valid = False

        self.compare_paragraph_counts()

        return all_valid

    def validate_whitespace_preservation(self):
        errors = []

        for xml_file in self.xml_files:
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()

                for elem in root.iter(f"{{{self.WORD_2006_NAMESPACE}}}t"):
                    if elem.text:
                        text = elem.text
                        if re.search(r"^[ \t\n\r]", text) or re.search(
                            r"[ \t\n\r]$", text
                        ):
                            xml_space_attr = f"{{{self.XML_NAMESPACE}}}space"
                            if (
                                xml_space_attr not in elem.attrib
                                or elem.attrib[xml_space_attr] != "preserve"
                            ):
                                text_preview = (
                                    repr(text)[:50] + "..."
                                    if len(repr(text)) > 50
                                    else repr(text)
                                )
                                errors.append(
                                    f"  {xml_file.relative_to(self.unpacked_dir)}: "
                                    f"Line {elem.sourceline}: w:t element with whitespace missing xml:space='preserve': {text_preview}"
                                )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"FAILED - Found {len(errors)} whitespace preservation violations:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - All whitespace is properly preserved")
            return True

    def validate_deletions(self):
        errors = []

        for xml_file in self.xml_files:
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()
                namespaces = {"w": self.WORD_2006_NAMESPACE}

                for t_elem in root.xpath(".//w:del//w:t", namespaces=namespaces):
                    if t_elem.text:
                        text_preview = (
                            repr(t_elem.text)[:50] + "..."
                            if len(repr(t_elem.text)) > 50
                            else repr(t_elem.text)
                        )
                        errors.append(
                            f"  {xml_file.relative_to(self.unpacked_dir)}: "
                            f"Line {t_elem.sourceline}: <w:t> found within <w:del>: {text_preview}"
                        )

                for instr_elem in root.xpath(
                    ".//w:del//w:instrText", namespaces=namespaces
                ):
                    text_preview = (
                        repr(instr_elem.text or "")[:50] + "..."
                        if len(repr(instr_elem.text or "")) > 50
                        else repr(instr_elem.text or "")
                    )
                    errors.append(
                        f"  {xml_file.relative_to(self.unpacked_dir)}: "
                        f"Line {instr_elem.sourceline}: <w:instrText> found within <w:del> (use <w:delInstrText>): {text_preview}"
                    )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"FAILED - Found {len(errors)} deletion validation violations:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - No w:t elements found within w:del elements")
            return True

    def count_paragraphs_in_unpacked(self):
        count = 0

        for xml_file in self.xml_files:
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()
                paragraphs = root.findall(f".//{{{self.WORD_2006_NAMESPACE}}}p")
                count = len(paragraphs)
            except Exception as e:
                print(f"Error counting paragraphs in unpacked document: {e}")

        return count

    def count_paragraphs_in_original(self):
        original = self.original_file
        if original is None:
            return 0

        count = 0

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(original, "r") as zip_ref:
                    safe_extract(zip_ref, Path(temp_dir))

                doc_xml_path = temp_dir + "/word/document.xml"
                root = lxml.etree.parse(doc_xml_path).getroot()

                paragraphs = root.findall(f".//{{{self.WORD_2006_NAMESPACE}}}p")
                count = len(paragraphs)

        except Exception as e:
            print(f"Error counting paragraphs in original document: {e}")

        return count

    def validate_insertions(self):
        errors = []

        for xml_file in self.xml_files:
            if xml_file.name != "document.xml":
                continue

            try:
                root = lxml.etree.parse(str(xml_file)).getroot()
                namespaces = {"w": self.WORD_2006_NAMESPACE}

                invalid_elements = root.xpath(
                    ".//w:ins//w:delText[not(ancestor::w:del)]", namespaces=namespaces
                )

                for elem in invalid_elements:
                    text_preview = (
                        repr(elem.text or "")[:50] + "..."
                        if len(repr(elem.text or "")) > 50
                        else repr(elem.text or "")
                    )
                    errors.append(
                        f"  {xml_file.relative_to(self.unpacked_dir)}: "
                        f"Line {elem.sourceline}: <w:delText> within <w:ins>: {text_preview}"
                    )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"FAILED - Found {len(errors)} insertion validation violations:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - No w:delText elements within w:ins elements")
            return True

    def compare_paragraph_counts(self):
        new_count = self.count_paragraphs_in_unpacked()
        if self.original_file is None:
            print(f"\nParagraphs: {new_count}")
            return

        original_count = self.count_paragraphs_in_original()
        diff = new_count - original_count
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        print(f"\nParagraphs: {original_count} → {new_count} ({diff_str})")

    def _parse_id_value(self, val: str, base: int = 16) -> int:
        return int(val, base)

    def validate_id_constraints(self):
        errors = []
        para_id_attr = f"{{{self.W14_NAMESPACE}}}paraId"
        durable_id_attr = f"{{{self.W16CID_NAMESPACE}}}durableId"

        for xml_file in self.xml_files:
            try:
                for elem in lxml.etree.parse(str(xml_file)).iter():
                    if val := elem.get(para_id_attr):
                        try:
                            if self._parse_id_value(val, base=16) >= 0x80000000:
                                errors.append(
                                    f"  {xml_file.name}:{elem.sourceline}: paraId={val} >= 0x80000000"
                                )
                        except ValueError:
                            errors.append(
                                f"  {xml_file.name}:{elem.sourceline}: "
                                f"paraId={val} is not valid hex"
                            )

                    if val := elem.get(durable_id_attr):
                        if xml_file.name == "numbering.xml":
                            try:
                                if self._parse_id_value(val, base=10) >= 0x7FFFFFFF:
                                    errors.append(
                                        f"  {xml_file.name}:{elem.sourceline}: "
                                        f"durableId={val} >= 0x7FFFFFFF"
                                    )
                            except ValueError:
                                errors.append(
                                    f"  {xml_file.name}:{elem.sourceline}: "
                                    f"durableId={val} must be decimal in numbering.xml"
                                )
                        else:
                            try:
                                if self._parse_id_value(val, base=16) >= 0x7FFFFFFF:
                                    errors.append(
                                        f"  {xml_file.name}:{elem.sourceline}: "
                                        f"durableId={val} >= 0x7FFFFFFF"
                                    )
                            except ValueError:
                                errors.append(
                                    f"  {xml_file.name}:{elem.sourceline}: "
                                    f"durableId={val} is not valid hex"
                                )
            except lxml.etree.XMLSyntaxError:
                continue  

        if errors:
            print(f"FAILED - {len(errors)} ID constraint violations:")
            for e in errors:
                print(e)
        elif self.verbose:
            print("PASSED - All paraId/durableId values within constraints")
        return not errors

    def validate_comment_markers(self):
        errors = []

        document_xml = None
        comments_xml = None
        for xml_file in self.xml_files:
            if xml_file.name == "document.xml" and "word" in str(xml_file):
                document_xml = xml_file
            elif xml_file.name == "comments.xml":
                comments_xml = xml_file

        if not document_xml:
            if self.verbose:
                print("PASSED - No document.xml found (skipping comment validation)")
            return True

        try:
            doc_root = lxml.etree.parse(str(document_xml)).getroot()
            namespaces = {"w": self.WORD_2006_NAMESPACE}

            range_starts = {
                elem.get(f"{{{self.WORD_2006_NAMESPACE}}}id")
                for elem in doc_root.xpath(
                    ".//w:commentRangeStart", namespaces=namespaces
                )
            }
            range_ends = {
                elem.get(f"{{{self.WORD_2006_NAMESPACE}}}id")
                for elem in doc_root.xpath(
                    ".//w:commentRangeEnd", namespaces=namespaces
                )
            }
            references = {
                elem.get(f"{{{self.WORD_2006_NAMESPACE}}}id")
                for elem in doc_root.xpath(
                    ".//w:commentReference", namespaces=namespaces
                )
            }

            orphaned_ends = range_ends - range_starts
            for comment_id in sorted(
                orphaned_ends, key=lambda x: int(x) if x and x.isdigit() else 0
            ):
                errors.append(
                    f'  document.xml: commentRangeEnd id="{comment_id}" has no matching commentRangeStart'
                )

            orphaned_starts = range_starts - range_ends
            for comment_id in sorted(
                orphaned_starts, key=lambda x: int(x) if x and x.isdigit() else 0
            ):
                errors.append(
                    f'  document.xml: commentRangeStart id="{comment_id}" has no matching commentRangeEnd'
                )

            comment_ids = set()
            if comments_xml and comments_xml.exists():
                comments_root = lxml.etree.parse(str(comments_xml)).getroot()
                comment_ids = {
                    elem.get(f"{{{self.WORD_2006_NAMESPACE}}}id")
                    for elem in comments_root.xpath(
                        ".//w:comment", namespaces=namespaces
                    )
                }

                marker_ids = range_starts | range_ends | references
                invalid_refs = marker_ids - comment_ids
                for comment_id in sorted(
                    invalid_refs, key=lambda x: int(x) if x and x.isdigit() else 0
                ):
                    if comment_id:  
                        errors.append(
                            f'  document.xml: marker id="{comment_id}" references non-existent comment'
                        )

        except (lxml.etree.XMLSyntaxError, Exception) as e:
            errors.append(f"  Error parsing XML: {e}")

        if errors:
            print(f"FAILED - {len(errors)} comment marker violations:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - All comment markers properly paired")
            return True

    def repair(self) -> int:
        repairs = super().repair()
        repairs += self.repair_durableId()
        return repairs

    def repair_durableId(self) -> int:
        DURABLE_ID_ATTRS = ("w16cid:durableId", "w16cex:durableId")
        repairs = 0
        renames: dict = {}  

        for xml_file in self.xml_files:
            try:
                content = xml_file.read_text(encoding="utf-8")
                dom = defusedxml.minidom.parseString(content)
                is_numbering = xml_file.name == "numbering.xml"
                base = 10 if is_numbering else 16
                pending = []  
                seen_in_file = set()
                modified = False

                for elem in dom.getElementsByTagName("*"):
                    for attr_name in DURABLE_ID_ATTRS:
                        if not elem.hasAttribute(attr_name):
                            continue

                        durable_id = elem.getAttribute(attr_name)
                        try:
                            key = self._parse_id_value(durable_id, base=base)
                            needs_repair = key >= 0x7FFFFFFF
                        except ValueError:
                            key = durable_id
                            needs_repair = True

                        if needs_repair:
                            if key in seen_in_file:
                                value = random.randint(1, 0x7FFFFFFE)
                            else:
                                seen_in_file.add(key)
                                if key not in renames:
                                    renames[key] = random.randint(1, 0x7FFFFFFE)
                                value = renames[key]
                            new_id = str(value) if is_numbering else f"{value:08X}"

                            elem.setAttribute(attr_name, new_id)
                            pending.append(
                                f"  Repaired: {xml_file.name}: durableId {durable_id} → {new_id}"
                            )
                            modified = True

                if modified:
                    xml_file.write_bytes(dom.toxml(encoding="UTF-8"))
                    for message in pending:
                        print(message)
                    repairs += len(pending)

            except Exception:
                pass

        return repairs


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly.")
```

### `scripts/office/validators/pptx.py`

```python
"""
Validator for PowerPoint presentation XML files against XSD schemas.
"""

import re
from pathlib import Path

from helpers import opc_target, rels_source_part, safe_extract

from .base import BaseSchemaValidator


class PPTXSchemaValidator(BaseSchemaValidator):

    PRESENTATIONML_NAMESPACE = (
        "http://schemas.openxmlformats.org/presentationml/2006/main"
    )

    ELEMENT_RELATIONSHIP_TYPES = {
        "sldid": "slide",
        "sldmasterid": "slidemaster",
        "notesmasterid": "notesmaster",
        "sldlayoutid": "slidelayout",
        "themeid": "theme",
        "tablestyleid": "tablestyles",
    }

    def validate(self):
        if not self.validate_xml():
            return False

        all_valid = True
        if not self.validate_namespaces():
            all_valid = False

        if not self.validate_unique_ids():
            all_valid = False

        if not self.validate_uuid_ids():
            all_valid = False

        if not self.validate_file_references():
            all_valid = False

        if not self.validate_slide_layout_ids():
            all_valid = False

        if not self.validate_content_types():
            all_valid = False

        if not self.validate_against_xsd():
            all_valid = False

        if not self.validate_notes_slide_references():
            all_valid = False

        if not self.validate_all_relationship_ids():
            all_valid = False

        if not self.validate_no_duplicate_slide_layouts():
            all_valid = False

        if not self.validate_master_theme_uniqueness():
            all_valid = False

        if not self.validate_charts():
            all_valid = False

        if not self.validate_slides():
            all_valid = False

        return all_valid

    def _package_map(self) -> dict:
        wanted = []
        wanted += list(self.unpacked_dir.glob("[[]Content_Types[]].xml"))
        wanted += list(self.unpacked_dir.glob("ppt/presentation.xml"))
        wanted += list(self.unpacked_dir.glob("ppt/theme/*.xml"))
        wanted += list(self.unpacked_dir.glob("ppt/theme/_rels/*.rels"))
        wanted += list(self.unpacked_dir.glob("ppt/charts/chart*.xml"))
        for group in ("slideMasters", "notesMasters", "handoutMasters"):
            wanted += list(self.unpacked_dir.glob(f"ppt/{group}/*.xml"))
            wanted += list(self.unpacked_dir.glob(f"ppt/{group}/_rels/*.rels"))
        return {
            p.relative_to(self.unpacked_dir).as_posix(): p.read_bytes()
            for p in wanted
            if p.is_file()
        }

    def validate_master_theme_uniqueness(self):
        from helpers.pptx_theme import _NOTES_MASTERS, live_shared_master_themes

        shared = live_shared_master_themes(self._package_map())
        if shared:
            print(f"FAILED - Found {len(shared)} master(s) sharing a theme part:")
            for message in shared:
                print(f"  {message}")
            if any(m.startswith(_NOTES_MASTERS) for m in shared):
                print("  Fix: in ppt/presentation.xml, move <p:notesMasterIdLst> back to "
                      "directly after <p:sldIdLst>. PowerPoint reads that happily.")
            else:
                print("  Fix: give each master its own theme part.")
            return False

        if self.verbose:
            print("PASSED - No master shares a theme part in a way PowerPoint refuses")
        return True

    def validate_charts(self):
        from helpers.pptx_chart import find_chart_problems

        problems = find_chart_problems(self._package_map())
        if problems:
            print(f"FAILED - Found {len(problems)} chart problem(s) PowerPoint rejects:")
            for message in problems:
                print(f"  {message}")
            return False

        if self.verbose:
            print("PASSED - Charts satisfy the constraints PowerPoint enforces")
        return True

    def _original_slide_defects(self, schema) -> set[str]:
        import tempfile
        import zipfile

        from helpers.pptx_slide import SLIDE_PART_RE, fatal_slide_errors

        if self.original_file is None:
            return set()

        found: set[str] = set()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            try:
                with zipfile.ZipFile(self.original_file, "r") as zf:
                    safe_extract(zf, temp_path)
            except (zipfile.BadZipFile, ValueError, OSError):
                return set()  

            for part in sorted(temp_path.rglob("*.xml")):
                relative = part.relative_to(temp_path).as_posix()
                if not SLIDE_PART_RE.fullmatch(relative):
                    continue
                ok, errors = self._validate_single_file_xsd(
                    part.resolve(), temp_path.resolve(), schema_path=schema
                )
                if ok is None or ok or not errors:
                    continue
                found |= set(fatal_slide_errors(set(errors)))
        return found

    def validate_slides(self):
        from helpers.pptx_slide import (
            SLIDE_PART_RE,
            fatal_slide_errors,
            is_schema_verdict,
        )

        schema = self.schemas_dir / self.SCHEMA_MAPPINGS["ppt"]
        inherited = self._original_slide_defects(schema)
        problems: list[str] = []
        broken: list[str] = []

        for xml_file in self.xml_files:
            relative = xml_file.relative_to(self.unpacked_dir).as_posix()
            if not SLIDE_PART_RE.fullmatch(relative):
                continue
            ok, errors = self._validate_single_file_xsd(
                xml_file.resolve(), self.unpacked_dir.resolve(), schema_path=schema
            )
            if ok is None or not errors:
                continue

            unreadable = [f"{relative}: {e}" for e in errors if not is_schema_verdict(e)]
            if unreadable:
                broken.extend(unreadable)
                continue
            if ok:
                continue

            for message in fatal_slide_errors(set(errors)):
                if message in inherited:
                    continue  
                problems.append(f"{relative}: {message}")

        if broken:
            print(f"FAILED - Could not check {len(broken)} slide part(s):")
            for message in sorted(broken):
                print(f"  {message[:240]}")

        if problems:
            print(f"FAILED - Found {len(problems)} slide problem(s) PowerPoint rejects:")
            for message in sorted(problems):
                print(f"  {message[:240]}")

        if broken or problems:
            return False

        if self.verbose:
            print("PASSED - Slide XML has none of the defects PowerPoint refuses")
        return True

    def _get_schema_path(self, xml_file):
        if xml_file.parent.name == "charts" and xml_file.name.startswith("chart"):
            return None
        return super()._get_schema_path(xml_file)

    def _preprocess_for_schema(self, xml_doc, relative_path):
        if relative_path.as_posix() != "ppt/presentation.xml":
            return xml_doc

        root = xml_doc.getroot()
        ns = f"{{{self.PRESENTATIONML_NAMESPACE}}}"
        notes = root.find(f"{ns}notesMasterIdLst")
        slides = root.find(f"{ns}sldIdLst")
        if notes is None or slides is None:
            return xml_doc

        children = list(root)
        if children.index(notes) < children.index(slides):
            return xml_doc  

        root.remove(notes)
        root.insert(list(root).index(slides), notes)
        return xml_doc

    def validate_uuid_ids(self):
        import lxml.etree

        errors = []
        uuid_pattern = re.compile(
            r"^[\{\(]?[0-9A-Fa-f]{8}-?[0-9A-Fa-f]{4}-?[0-9A-Fa-f]{4}-?[0-9A-Fa-f]{4}-?[0-9A-Fa-f]{12}[\}\)]?$"
        )

        for xml_file in self.xml_files:
            try:
                root = lxml.etree.parse(str(xml_file)).getroot()

                for elem in root.iter():
                    for attr, value in elem.attrib.items():
                        attr_name = attr.split("}")[-1].lower()
                        if attr_name == "id" or attr_name.endswith("id"):
                            if self._looks_like_uuid(value):
                                if not uuid_pattern.match(value):
                                    errors.append(
                                        f"  {xml_file.relative_to(self.unpacked_dir)}: "
                                        f"Line {elem.sourceline}: ID '{value}' appears to be a UUID but contains invalid hex characters"
                                    )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {xml_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"FAILED - Found {len(errors)} UUID ID validation errors:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - All UUID-like IDs contain valid hex values")
            return True

    def _looks_like_uuid(self, value):
        clean_value = value.strip("{}()").replace("-", "")
        return len(clean_value) == 32 and all(c.isalnum() for c in clean_value)

    def validate_slide_layout_ids(self):
        import lxml.etree

        errors = []

        slide_masters = list(self.unpacked_dir.glob("ppt/slideMasters/*.xml"))

        if not slide_masters:
            if self.verbose:
                print("PASSED - No slide masters found")
            return True

        for slide_master in slide_masters:
            try:
                root = lxml.etree.parse(str(slide_master)).getroot()

                rels_file = slide_master.parent / "_rels" / f"{slide_master.name}.rels"

                if not rels_file.exists():
                    errors.append(
                        f"  {slide_master.relative_to(self.unpacked_dir)}: "
                        f"Missing relationships file: {rels_file.relative_to(self.unpacked_dir)}"
                    )
                    continue

                rels_root = lxml.etree.parse(str(rels_file)).getroot()

                valid_layout_rids = set()
                for rel in rels_root.findall(
                    f".//{{{self.PACKAGE_RELATIONSHIPS_NAMESPACE}}}Relationship"
                ):
                    rel_type = rel.get("Type", "")
                    if "slideLayout" in rel_type:
                        valid_layout_rids.add(rel.get("Id"))

                for sld_layout_id in root.findall(
                    f".//{{{self.PRESENTATIONML_NAMESPACE}}}sldLayoutId"
                ):
                    r_id = sld_layout_id.get(
                        f"{{{self.OFFICE_RELATIONSHIPS_NAMESPACE}}}id"
                    )
                    layout_id = sld_layout_id.get("id")

                    if r_id and r_id not in valid_layout_rids:
                        errors.append(
                            f"  {slide_master.relative_to(self.unpacked_dir)}: "
                            f"Line {sld_layout_id.sourceline}: sldLayoutId with id='{layout_id}' "
                            f"references r:id='{r_id}' which is not found in slide layout relationships"
                        )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {slide_master.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print(f"FAILED - Found {len(errors)} slide layout ID validation errors:")
            for error in errors:
                print(error)
            print(
                "Remove invalid references or add missing slide layouts to the relationships file."
            )
            return False
        else:
            if self.verbose:
                print("PASSED - All slide layout IDs reference valid slide layouts")
            return True

    def validate_no_duplicate_slide_layouts(self):
        import lxml.etree

        errors = []
        slide_rels_files = list(self.unpacked_dir.glob("ppt/slides/_rels/*.xml.rels"))

        for rels_file in slide_rels_files:
            try:
                root = lxml.etree.parse(str(rels_file)).getroot()

                layout_rels = [
                    rel
                    for rel in root.findall(
                        f".//{{{self.PACKAGE_RELATIONSHIPS_NAMESPACE}}}Relationship"
                    )
                    if "slideLayout" in rel.get("Type", "")
                ]

                if len(layout_rels) > 1:
                    errors.append(
                        f"  {rels_file.relative_to(self.unpacked_dir)}: has {len(layout_rels)} slideLayout references"
                    )

            except Exception as e:
                errors.append(
                    f"  {rels_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        if errors:
            print("FAILED - Found slides with duplicate slideLayout references:")
            for error in errors:
                print(error)
            return False
        else:
            if self.verbose:
                print("PASSED - All slides have exactly one slideLayout reference")
            return True

    def validate_notes_slide_references(self):
        import lxml.etree

        errors = []
        notes_slide_references = {}  

        slide_rels_files = list(self.unpacked_dir.glob("ppt/slides/_rels/*.xml.rels"))

        if not slide_rels_files:
            if self.verbose:
                print("PASSED - No slide relationship files found")
            return True

        for rels_file in slide_rels_files:
            try:
                root = lxml.etree.parse(str(rels_file)).getroot()

                for rel in root.findall(
                    f".//{{{self.PACKAGE_RELATIONSHIPS_NAMESPACE}}}Relationship"
                ):
                    rel_type = rel.get("Type", "")
                    if "notesSlide" in rel_type:
                        part = opc_target(
                            rel.get("Target", ""),
                            rels_source_part(rels_file, self.unpacked_dir),
                            rel.get("TargetMode", ""),
                        )
                        if part:
                            slide_name = rels_file.stem.replace(
                                ".xml", ""
                            )  

                            notes_slide_references.setdefault(part, []).append(
                                (slide_name, rels_file)
                            )

            except (lxml.etree.XMLSyntaxError, Exception) as e:
                errors.append(
                    f"  {rels_file.relative_to(self.unpacked_dir)}: Error: {e}"
                )

        for target, references in notes_slide_references.items():
            if len(references) > 1:
                slide_names = [ref[0] for ref in references]
                errors.append(
                    f"  Notes slide '{target}' is referenced by multiple slides: {', '.join(slide_names)}"
                )
                for slide_name, rels_file in references:
                    errors.append(f"    - {rels_file.relative_to(self.unpacked_dir)}")

        if errors:
            print(
                f"FAILED - Found {len([e for e in errors if not e.startswith('    ')])} notes slide reference validation errors:"
            )
            for error in errors:
                print(error)
            print("Each slide may optionally have its own slide file.")
            return False
        else:
            if self.verbose:
                print("PASSED - All notes slide references are unique")
            return True


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly.")
```

### `scripts/office/validators/redlining.py`

```python
"""
Validator for tracked changes in Word documents.

Detects untracked edits in word/document.xml: text that differs from the
original without a <w:ins>/<w:del> wrapper recording it. The tracked changes
that are new relative to the original are undone, and the result is compared
against the original; whatever text still differs was edited without being
tracked.

Only the document body is compared. Headers, footers, footnotes and endnotes
are separate parts and are not checked.
"""

import subprocess
import tempfile
import zipfile
from pathlib import Path

import defusedxml.ElementTree as ET
from defusedxml.common import DefusedXmlException

from helpers import rendered_text, safe_extract


class RedliningValidator:

    def __init__(self, unpacked_dir, original_docx, verbose=False):
        self.unpacked_dir = Path(unpacked_dir)
        self.original_docx = Path(original_docx)
        self.verbose = verbose
        self.namespaces = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }

    def repair(self) -> int:
        return 0

    def validate(self):
        modified_file = self.unpacked_dir / "word" / "document.xml"
        if not modified_file.exists():
            print(f"FAILED - Modified document.xml not found at {modified_file}")
            return False

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            try:
                with zipfile.ZipFile(self.original_docx, "r") as zip_ref:
                    safe_extract(zip_ref, temp_path)
            except Exception as e:
                print(f"FAILED - Error unpacking original docx: {e}")
                return False

            original_file = temp_path / "word" / "document.xml"
            if not original_file.exists():
                print(
                    f"FAILED - Original document.xml not found in {self.original_docx}"
                )
                return False

            try:
                modified_tree = ET.parse(modified_file)
                modified_root = modified_tree.getroot()
                original_tree = ET.parse(original_file)
                original_root = original_tree.getroot()
            except (ET.ParseError, DefusedXmlException) as e:
                print(f"FAILED - Error parsing XML files: {e}")
                return False

            new_changes = self._new_tracked_changes(original_root, modified_root)
            self._remove_tracked_changes(modified_root, new_changes)

            modified_text = self._extract_text_content(modified_root)
            original_text = self._extract_text_content(original_root)

            if modified_text != original_text:
                error_message = self._generate_detailed_diff(
                    original_text, modified_text
                )
                print(error_message)
                return False

            if self.verbose:
                print(
                    f"PASSED - All {len(new_changes)} change(s) against the original "
                    "are properly tracked"
                )
            return True

    def _tracked_change_elements(self, root):
        ins_tag = f"{{{self.namespaces['w']}}}ins"
        del_tag = f"{{{self.namespaces['w']}}}del"
        return [elem for elem in root.iter() if elem.tag in (ins_tag, del_tag)]

    def _rendered_text(self, elem):
        preserve = elem.get("{http://www.w3.org/XML/1998/namespace}space") == "preserve"
        return rendered_text(elem.text or "", preserve)

    def _text_elements(self, elem):
        w = self.namespaces["w"]
        return [
            node
            for node in elem.iter()
            if node.tag in (f"{{{w}}}t", f"{{{w}}}delText")
        ]

    def _tracked_change_key(self, elem):
        w = self.namespaces["w"]
        text = "".join(self._rendered_text(node) for node in self._text_elements(elem))
        return (elem.tag, elem.get(f"{{{w}}}author"), elem.get(f"{{{w}}}date"), text)

    def _new_tracked_changes(self, original_root, modified_root):
        original = self._tracked_change_elements(original_root)
        modified = self._tracked_change_elements(modified_root)

        pool = {}
        for elem in original:
            pool.setdefault(self._tracked_change_key(elem), []).append(elem)

        matched, leftover = set(), []
        for elem in modified:
            bucket = pool.get(self._tracked_change_key(elem))
            if bucket:
                matched.add(bucket.pop())
            else:
                leftover.append(elem)

        def group(elem):
            return self._tracked_change_key(elem)[:3]

        def text_of(elems):
            return "".join(self._tracked_change_key(e)[3] for e in elems)

        unmatched_original = {}
        for elem in original:
            if elem not in matched:
                unmatched_original.setdefault(group(elem), []).append(elem)

        by_group = {}
        for elem in leftover:
            by_group.setdefault(group(elem), []).append(elem)

        new = set()
        for key, elems in by_group.items():
            rebuilt = text_of(elems)
            if rebuilt and rebuilt == text_of(unmatched_original.get(key, [])):
                continue  
            new.update(elems)
        return new

    def _generate_detailed_diff(self, original_text, modified_text):
        error_parts = [
            "FAILED - Document text doesn't match after removing the tracked changes",
            "",
            "Likely causes:",
            "  1. Modified text inside another author's <w:ins> or <w:del> tags",
            "  2. Made edits without proper tracked changes",
            "  3. Didn't nest <w:del> inside <w:ins> when deleting another's insertion",
            "  4. Rewrote another author's <w:ins>/<w:del> and changed its text on",
            "     the way. A tracked change from the original is recognised by its",
            "     author, date and text; anything that doesn't reproduce one exactly",
            "     reads as new, and the text it carried is reported missing.",
            "",
            "For pre-redlined documents, use correct patterns:",
            "  - To reject another's INSERTION: Nest <w:del> inside their <w:ins>",
            "  - To reject PART of one: nest <w:del> around only the runs you reject.",
            "    Their <w:ins> may be split around it, so long as the pieces keep",
            "    their author and date and still spell out the same text.",
            "  - To restore another's DELETION: Add new <w:ins> AFTER their <w:del>",
            "",
        ]

        git_diff = self._get_git_word_diff(original_text, modified_text)
        if git_diff:
            error_parts.extend(["Differences:", "============", git_diff])
        else:
            error_parts.append("Unable to generate word diff (git not available)")

        return "\n".join(error_parts)

    def _get_git_word_diff(self, original_text, modified_text):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                original_file = temp_path / "original.txt"
                modified_file = temp_path / "modified.txt"

                original_file.write_text(original_text, encoding="utf-8")
                modified_file.write_text(modified_text, encoding="utf-8")

                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--word-diff=plain",
                        "--word-diff-regex=.",  
                        "-U0",  
                        "--no-index",
                        str(original_file),
                        str(modified_file),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.stdout.strip():
                    lines = result.stdout.split("\n")
                    content_lines = []
                    in_content = False
                    for line in lines:
                        if line.startswith("@@"):
                            in_content = True
                            continue
                        if in_content and line.strip():
                            content_lines.append(line)

                    if content_lines:
                        return "\n".join(content_lines)

                result = subprocess.run(
                    [
                        "git",
                        "diff",
                        "--word-diff=plain",
                        "-U0",  
                        "--no-index",
                        str(original_file),
                        str(modified_file),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.stdout.strip():
                    lines = result.stdout.split("\n")
                    content_lines = []
                    in_content = False
                    for line in lines:
                        if line.startswith("@@"):
                            in_content = True
                            continue
                        if in_content and line.strip():
                            content_lines.append(line)
                    return "\n".join(content_lines)

        except (subprocess.CalledProcessError, FileNotFoundError, Exception):
            pass

        return None

    def _remove_tracked_changes(self, root, targets):
        ins_tag = f"{{{self.namespaces['w']}}}ins"
        del_tag = f"{{{self.namespaces['w']}}}del"

        for parent in root.iter():
            to_remove = []
            for child in parent:
                if child.tag == ins_tag and child in targets:
                    to_remove.append(child)
            for elem in to_remove:
                parent.remove(elem)

        deltext_tag = f"{{{self.namespaces['w']}}}delText"
        t_tag = f"{{{self.namespaces['w']}}}t"

        for parent in root.iter():
            to_process = []
            for child in parent:
                if child.tag == del_tag and child in targets:
                    to_process.append((child, list(parent).index(child)))

            for del_elem, del_index in reversed(to_process):
                for elem in del_elem.iter():
                    if elem.tag == deltext_tag:
                        elem.tag = t_tag

                for child in reversed(list(del_elem)):
                    parent.insert(del_index, child)
                parent.remove(del_elem)

    def _extract_text_content(self, root):
        p_tag = f"{{{self.namespaces['w']}}}p"
        t_tag = f"{{{self.namespaces['w']}}}t"

        paragraphs = []
        for p_elem in root.findall(f".//{p_tag}"):
            text_parts = []
            for t_elem in p_elem.findall(f".//{t_tag}"):
                text_parts.append(self._rendered_text(t_elem))
            paragraph_text = "".join(text_parts)
            if paragraph_text:
                paragraphs.append(paragraph_text)

        return "\n".join(paragraphs)


if __name__ == "__main__":
    raise RuntimeError("This module should not be run directly.")
```

### `scripts/templates/comments.xml`

```xml
<?xml version="1.0" ?>
<w:comments xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex" xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex" xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex" xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex" xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex" xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex" xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14">
</w:comments>
```

### `scripts/templates/commentsExtended.xml`

```xml
<?xml version="1.0" ?>
<w15:commentsEx xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex" xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex" xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex" xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex" xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex" xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex" xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14">
</w15:commentsEx>
```

### `scripts/templates/commentsExtensible.xml`

```xml
<?xml version="1.0" ?>
<w16cex:commentsExtensible xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex" xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex" xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex" xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex" xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex" xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex" xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" xmlns:cr="http://schemas.microsoft.com/office/comments/2020/reactions" mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl cr w16du wp14">
</w16cex:commentsExtensible>
```

### `scripts/templates/commentsIds.xml`

```xml
<?xml version="1.0" ?>
<w16cid:commentsIds xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex" xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex" xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex" xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex" xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex" xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex" xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14">
</w16cid:commentsIds>
```

### `scripts/templates/people.xml`

```xml
<?xml version="1.0" ?>
<w15:people xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml">
</w15:people>
```

### `LICENSE.txt`

```text
© 2025 Anthropic, PBC. All rights reserved.

LICENSE: Use of these materials (including all code, prompts, assets, files,
and other components of this Skill) is governed by your agreement with
Anthropic regarding use of Anthropic's services. If no separate agreement
exists, use is governed by Anthropic's Consumer Terms of Service or
Commercial Terms of Service, as applicable:
https://www.anthropic.com/legal/consumer-terms
https://www.anthropic.com/legal/commercial-terms
Your applicable agreement is referred to as the "Agreement." "Services" are
as defined in the Agreement.

ADDITIONAL RESTRICTIONS: Notwithstanding anything in the Agreement to the
contrary, users may not:

- Extract these materials from the Services or retain copies of these
  materials outside the Services
- Reproduce or copy these materials, except for temporary copies created
  automatically during authorized use of the Services
- Create derivative works based on these materials
- Distribute, sublicense, or transfer these materials to any third party
- Make, offer to sell, sell, or import any inventions embodied in these
  materials
- Reverse engineer, decompile, or disassemble these materials

The receipt, viewing, or possession of these materials does not convey or
imply any license or right beyond those expressly granted above.

Anthropic retains all right, title, and interest in these materials,
including all copyrights, patents, and other intellectual property rights.
```
