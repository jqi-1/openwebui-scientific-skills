---
name: pptx
description: Use this skill any time a .pptx or .potx file is involved in any way — as input, output, or both. This includes: creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from any .pptx or .potx file (even if the extracted content will be used elsewhere, like in an email or summary); editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates (.potx), layouts, speaker notes, or comments. Trigger whenever the user mentions \"deck,\" \"slides,\" \"presentation,\" or references a .pptx or .potx filename, regardless of what they plan to do with the content afterward. If a .pptx or .potx file needs to be opened, created, or touched, use this skill.
---

# PPTX creation, editing, and analysis

A `.pptx` is a ZIP archive of XML files. Choose your approach by task:

| Task | Approach |
|---|---|
| **Create** a new deck | Write a `pptxgenjs` script — see gotchas below |
| **Edit** an existing deck, or build from a template | unzip → edit `ppt/slides/slideN.xml` → zip |
| **Read** content | `markitdown deck.pptx` (one block per slide under `<!-- Slide number: N -->` markers); visual grid: `python scripts/thumbnail.py deck.pptx` |

## Scripts

Paths are relative to this skill's directory. Everything else is plain Python, `node`, or shell.

| Script | What it does |
|---|---|
| `scripts/thumbnail.py deck.pptx [prefix]` | Labeled grid of every slide, for picking template layouts. `.pptx` only. Pass `prefix` — it defaults to `thumbnails`, which overwrites the grids of any other deck done in the same directory |
| `scripts/add_slide.py unpacked/ slide2.xml [--after slideN.xml]` | Duplicate a slide (or a `slideLayoutN.xml`) with all the package bookkeeping. Also takes a `.pptx` directly with `-o out.pptx` |
| `scripts/clean.py unpacked/` | Delete slides, media, and rels no longer referenced. Run **after** `<p:sldIdLst>` is final |
| `scripts/office/validate.py deck.pptx [--original src.pptx]` | Schema, relationship, content-type, chart and slide checks; each failure names its fix. Pass `--original` for any template-derived deck — it baselines the schema checks against the template, so the template's own XSD errors don't read as yours |
| `scripts/office/soffice.py --headless --convert-to pdf deck.pptx` | LibreOffice wrapper — bare `soffice` hangs in this sandbox |

## Creating with pptxgenjs — gotchas

`pptxgenjs` is preinstalled — do not run `npm install` first; write the script and `require('pptxgenjs')` directly. Only if that require fails: `npm install pptxgenjs`. The model knows the API; these are the footguns:

- **Set `pres.layout` before adding slides.** The default canvas is `LAYOUT_16x9` = **10" × 5.625"**, not 13.3" wide. Coordinates past the edge are written, not clamped — the shape just isn't on the slide. (`LAYOUT_WIDE` is 13.3" × 7.5".)
- **Hex colors: never `#`, never 8 digits.** `color: "FF0000"`. Both `"#FF0000"` and alpha baked into the hex (`"00000020"`) **corrupt the file**. For translucency: `transparency: 0-100` on fills and images, `opacity: 0.0-1.0` on shadows — each is silently ignored on the other.
- **pptxgenjs mutates option objects in place** (converts values to EMU on first use). Never share one `shadow`/options object across two `add*` calls — build a fresh object each time.
- **Shadow `offset` must be ≥ 0** — a negative offset corrupts the file. To cast a shadow upward, use `angle: 270` with a positive offset.
- **`letterSpacing` is silently ignored** — the real option is `charSpacing`.
- **Lists:** `bullet: true` on each item, never a literal `•` (renders double bullets). Set `breakLine: true` on every array item except the last. Space bulleted paragraphs with `paraSpaceAfter`, not `lineSpacing` (huge gaps).
- **One `new pptxgen()` per output file** — never reuse an instance.
- **`rectRadius` only works on `ROUNDED_RECTANGLE`**, not `RECTANGLE`.
- **Gradient fills aren't supported** — use a gradient image as the background instead.
- **Text boxes have built-in internal padding** — set `margin: 0` whenever text must align with a shape, line, or icon at the same x.
- **Speaker notes go in `slide.addNotes("...")`** (plain text, once per slide), never in a text box on the slide.
- **Keep charts native.** Use `addChart()` for everything PowerPoint can chart (pass an array of `{type, data, options}` for combos). For PowerPoint-native features the library doesn't expose (trendlines, error bars), compute the extra series yourself or post-process the generated OOXML — do not fall back to a rendered image. Only chart types PowerPoint has no native form for (Sankey, network, chord) go in as images.
- **Default charts render bare** — no title, no data labels, dated palette. Set `showTitle` + `title`, `showValue: true` + `dataLabelPosition`, `chartColors: [...]` from your palette, and quiet the frame (`catAxisLabelColor`/`valAxisLabelColor`, `valGridLine: { color, size }`, `catGridLine: { style: "none" }`, `showLegend: false` for a single series).
- **On a stacked bar or column chart, `dataLabelPosition` must be `ctr`, `inEnd`, or `inBase`.** `outEnd` **corrupts the file**.
- **A combo series using `secondaryValAxis`/`secondaryCatAxis` needs both `valAxes` and `catAxes` on the chart options, two entries each.** Without them pptxgenjs writes axis *ids* it never declares, and PowerPoint **discards that chart** and reports the file as corrupt. Supplying only `valAxes` is not enough.
- **After `writeFile()`, run `python scripts/office/validate.py deck.pptx`.** It reports the two chart faults above and the slide-XML defects PowerPoint refuses, and names the fix for each. Fix them in your generator, not by hand-editing the packed XML.
- **Never reorder the children of `<p:presentation>`.** pptxgenjs writes `<p:notesMasterIdLst>` right after `<p:sldIdLst>` and points both masters at one theme part. PowerPoint reads that happily — move the element and the same deck becomes unopenable.
- **Icons:** render `react-icons` to SVG (`ReactDOMServer.renderToStaticMarkup`), rasterize with `sharp` at ≥256px, and insert via `addImage({ data: "image/png;base64," + buf.toString("base64") })` — the `image/png;base64,` prefix is required (`react-icons`, `react`, `react-dom`, and `sharp` are preinstalled — `npm install react-icons react react-dom sharp` only if a require fails).

## Editing existing decks and templates

Pick layouts first: `python scripts/thumbnail.py template.pptx template-thumbs` writes a labeled grid of every slide and prints the file(s) it created — `template-thumbs.jpg`, split into `template-thumbs-N.jpg` past 12 slides. **Always pass that second argument, named after the deck.** It defaults to `thumbnails`, so two decks thumbnailed in one directory silently overwrite each other's grids — the first deck's are simply gone (template analysis only — visual QA needs the full-resolution renders from [Converting to Images](#converting-to-images); it only accepts `.pptx`, so copy a `.potx` to a `.pptx` name first). Use it with `markitdown` to map each content section onto a template slide, and vary the layouts — don't put every section on the same title-and-bullets slide.

```bash
python3 -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall('unpacked')" deck.pptx
python scripts/add_slide.py unpacked/ slide2.xml --after slide2.xml   # duplicate a slide (or slideLayoutN.xml); prints the new slide's path
# reorder / delete slides = edit <p:sldIdLst> in ppt/presentation.xml
python scripts/clean.py unpacked/                                     # after deletions: removes orphaned slides, media, rels
# edit slide content in ppt/slides/slideN.xml
(cd unpacked && rm -f ../out.pptx && zip -Xr ../out.pptx .)           # zip from INSIDE the dir; rm first or deleted parts survive
python scripts/office/validate.py out.pptx --original deck.pptx
```

- **Do all structural work — add, delete, reorder — before editing any slide's content.** `add_slide.py` copies a slide file verbatim, so duplicating after you edit clones the edited content; and `clean.py` deletes any slide missing from `<p:sldIdLst>`, including one you just wrote.
- **Never copy a slide file by hand** — `add_slide.py` does every registration a new slide needs and reports what it made (`Created ppt/slides/slide17.xml from slide2.xml`). It also works directly on a file: `add_slide.py deck.pptx slide2.xml -o out.pptx` — **pass `-o`, or it rewrites the input deck in place.** A duplicated slide still *references* its source's chart/SmartArt/embedded-object parts rather than cloning them, so editing one slide's chart changes the other's.
- **If you use `python-pptx`**, three things it won't do: duplicate a slide (its only entry point is `add_slide(layout)`), preserve formatting through `text_frame.text = "..."` (that collapses the paragraph to a single unstyled run — assign `run.text` instead), or read the SVG/EMF most template art uses (`add_picture` raises `UnidentifiedImageError`).
- Legacy `.ppt` must be converted first: `python scripts/office/soffice.py --headless --convert-to pptx file.ppt`. `.potx` templates unpack and pack identically — keep the `.potx` extension on the output.
- To reuse a template icon or image, duplicate a slide or layout that already contains it.

When filling in a template:

- If you script an XML transform, parse with `defusedxml.minidom` — round-tripping OOXML through `xml.etree.ElementTree` rewrites namespace prefixes and corrupts the deck.
- **Template slots ≠ source items.** If the template shows 4 team members and you have 3, delete the 4th member's entire group (image + text boxes), not just its text — then check for orphaned visuals in QA.
- One `<a:p>` per list item — never concatenate items into a single paragraph. Copy the sibling `<a:pPr>` to preserve spacing, and put `b="1"` on the `<a:rPr>` of titles, section headers, and inline labels (`Status:`, `Owner:`).
- Let bullets inherit from the layout; only add `<a:buChar>`, `<a:buAutoNum>` (numbered), or `<a:buNone>` to override — never a literal `•` in the text.
- Text with leading or trailing spaces needs `xml:space="preserve"` on its `<a:t>`.

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Consider ideas from this list for each slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles. Carry it across every slide. **Do not use a color bar or accent stripe as your motif** (see Avoid list).

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Font names you write into the .pptx are rendered by the user's PowerPoint, not by this environment.** Your visual QA renders via LibreOffice, which substitutes fonts it doesn't have — and for some fonts the substitute has different widths, so your QA preview can show text overflow (or fit) that the real deck won't have. To keep your QA trustworthy:

- **Safe fonts** (render true-to-width in QA *and* ship with Office): **Arial, Calibri, Cambria, Times New Roman, Courier New, Bookman Old Style, Century Schoolbook**. Use these for body text and anything where fit matters.
- **Headers with personality at zero QA risk**: pair a safe-list serif header (Cambria, Bookman Old Style, Century Schoolbook) with a safe-list sans body (Calibri or Arial). You get visual contrast without giving up reliable overflow checks.
- **If the user asks for a font outside the safe list** (e.g. Georgia or Trebuchet MS): use it where the user asked, but size those containers with extra slack (~10%) and don't trust QA text-fit on those elements — the preview of that font is approximate. If the user hasn't specified, prefer safe-list fonts for body text.
- **QA-unreliable fonts** (substitute has different widths — overflow checks can be wrong): Georgia, Trebuchet MS, Impact, Arial Black, Garamond, Consolas, Palatino Linotype. Calibri Light substitution varies by environment; treat as QA-unreliable. Fine for titles/accents with slack; don't trust QA text-fit on these.
- **Never default to Aptos** — Office's post-2023 default has no metric-compatible substitute here *and* is missing from older Office installs, so it's unreliable on both ends.

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead
- **NEVER add decorative color bars or accent stripes** — this includes: header/footer bars spanning the slide width, vertical sidebar stripes down one edge of the slide, thin accent stripes along one edge of a card or content block, and "single-side borders" on rectangles. These read as AI-generated filler. If you want to set a card apart, use a subtle background tint, a drop shadow, or an icon — not an edge stripe.
- **Don't default to cream/beige backgrounds** — when no background is specified, use white (`FFFFFF`) or the user's brand palette; avoid warm-neutral defaults like `F5F5DC`, `FAF0E6`, `FAEBD7`, `FFF8E1`
- **Don't ship text that overflows its shape** — if text doesn't fit, reduce font size, split across slides, or enlarge the container; never leave content cut off or spilling past bounds

## QA (Required)

Your first render usually has a few real issues — overlaps, overflow, misalignment. Find and fix those, re-render only the slides you changed, and stop.

### Content QA

```bash
markitdown output.pptx
```

Check for missing content, typos, wrong order.

**When using templates, check for leftover placeholder text:**

```bash
markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert|this.*(page|slide).*layout"
```

If grep returns results, fix them before declaring success.

### File QA (required)

```bash
python scripts/office/validate.py output.pptx                      # built from scratch
python scripts/office/validate.py output.pptx --original src.pptx  # built from a template
```

**If the deck came from a template, always pass `--original`.** A template may itself
contain parts the XSD rejects, so a bare run can report failures you never caused — and
a genuine regression can hide among them. `--original` baselines
the schema and slide checks against the template, suppressing errors it already had.
The structural checks — relationships, content types, charts — ignore `--original` and
report template-inherited problems either way, so read those on their own merits.

pptxgenjs emits chart XML PowerPoint refuses to open, and every other tool
accepts: python-pptx opens those decks, LibreOffice renders them, the XSD
passes them. Every failure names its fix. Fix it in the generator and rebuild.

### Visual QA

Convert the slides to images (see [Converting to Images](#converting-to-images)) and inspect every one. After staring at the generating code you tend to see what you expect rather than what rendered, so look at the images fresh (a subagent works well for this if you have one). User-visible defects to look for:

- **Text overflow or text cut off at a box or slide boundary — check this first.** It is the most common defect and always user-visible. (For a font the previewer renders unreliably per Typography, the preview is approximate: trust the ~10% slack you left, not its apparent fit.)
- Overlapping elements (text through shapes, lines through words, stacked elements)
- Source citations or footers colliding with content above
- Elements too close (< 0.3" gaps) or cards/sections nearly touching
- Uneven gaps (large empty area in one place, cramped in another)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text (e.g., light gray text on cream-colored background)
- Template decoration mispositioned after text replacement — e.g., a title underline positioned for one line, but the replaced title wrapped to two
- Low-contrast icons (e.g., dark icons on dark backgrounds without a contrasting circle)
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content

## Converting to Images

Convert presentations to individual slide images for visual inspection:

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
ls -1 "$PWD"/slide-*.jpg
```

**Pass the absolute paths printed above directly to the view tool.** The `rm` clears stale images from prior runs. `pdftoppm` zero-pads based on page count: `slide-1.jpg` for decks under 10 pages, `slide-01.jpg` for 10-99, `slide-001.jpg` for 100+.

**After fixes, rerun all four commands above** — the PDF must be regenerated from the edited `.pptx` before `pdftoppm` can reflect your changes.

## Dependencies

`pptxgenjs` (npm, preinstalled — install only if `require('pptxgenjs')` fails) · `markitdown[pptx]`, `Pillow`, `defusedxml`, `lxml` (pip — text dump, thumbnail, clean, validate) · LibreOffice (`soffice`, auto-configured for sandboxed environments via `scripts/office/soffice.py`) · `pdftoppm` (Poppler)

---

*This skill is created and maintained by [Anthropic](https://github.com/anthropics/skills/tree/main/skills/pptx). Vendored here unmodified except for frontmatter metadata; see LICENSE.txt for terms.*

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pptx/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

> Excluded (not usable as inline text — binary assets, vendored schemas, or bulk data): scripts/office/schemas/ISO-IEC29500-4_2016/dml-chart.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-chartDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-diagram.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-lockedCanvas.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-main.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-picture.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-spreadsheetDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/dml-wordprocessingDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/pml.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-additionalCharacteristics.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-bibliography.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-commonSimpleTypes.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-customXmlDataProperties.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-customXmlSchemaProperties.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-documentPropertiesCustom.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-documentPropertiesExtended.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-documentPropertiesVariantTypes.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-math.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/shared-relationshipReference.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/sml.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-main.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-officeDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-presentationDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-spreadsheetDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/vml-wordprocessingDrawing.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/wml.xsd, scripts/office/schemas/ISO-IEC29500-4_2016/xml.xsd, scripts/office/schemas/ecma/fouth-edition/opc-contentTypes.xsd, scripts/office/schemas/ecma/fouth-edition/opc-coreProperties.xsd, scripts/office/schemas/ecma/fouth-edition/opc-digSig.xsd, scripts/office/schemas/ecma/fouth-edition/opc-relationships.xsd, scripts/office/schemas/mce/mc.xsd, scripts/office/schemas/microsoft/wml-2010.xsd, scripts/office/schemas/microsoft/wml-2012.xsd, scripts/office/schemas/microsoft/wml-2018.xsd, scripts/office/schemas/microsoft/wml-cex-2018.xsd, scripts/office/schemas/microsoft/wml-cid-2016.xsd, scripts/office/schemas/microsoft/wml-sdtdatahash-2020.xsd, scripts/office/schemas/microsoft/wml-symex-2015.xsd

### `scripts/__init__.py`

```python

```

### `scripts/add_slide.py`

```python
"""Add a slide to a PPTX: duplicate an existing slide or instantiate a layout.

Does all of the package bookkeeping, so the deck stays valid:
  - writes the new ppt/slides/slideN.xml (and its .rels, minus any
    notesSlide reference, so the source's speaker notes aren't shared)
  - registers it in [Content_Types].xml
  - adds a slide relationship with a fresh rId to presentation.xml.rels
  - inserts <p:sldId id="..." r:id="..."/> with a fresh id into
    <p:sldIdLst> — at the end, or after --after SLIDE

Works on an unpacked directory (during an editing session) or directly on a
.pptx/.potx file (extracted to a temp dir, then rezipped atomically; the
temp dir is discarded, so unpack the output if you still need to edit the
new slide's content).

Usage:
    python add_slide.py unpacked/ slide2.xml                 # duplicate slide2
    python add_slide.py unpacked/ slideLayout3.xml           # new slide from a layout
    python add_slide.py unpacked/ slide2.xml --after slide2.xml
    python add_slide.py deck.pptx slide2.xml                 # rewrite deck.pptx in place
    python add_slide.py deck.pptx slide2.xml -o out.pptx

A duplicated slide still holds the source's content: edit ppt/slides/slideN.xml
(printed on success) to change it. To list layouts: ls <dir>/ppt/slideLayouts/
"""

import argparse
import re
import shutil
import sys
from typing import NoReturn
import tempfile
import zipfile
from pathlib import Path

from office.helpers import rezip, safe_extract

MINIMAL_SLIDE_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr>
    <a:masterClrMapping/>
  </p:clrMapOvr>
</p:sld>'''

SHARED_PART_TYPES = ("chart", "diagramData", "oleObject", "package")

NOTES_SLIDE_TYPE_RE = re.compile(r"""Type=["'][^"']*/relationships/notesSlide["']""")
RELATIONSHIP_RE = re.compile(r"<Relationship\b[^>]*?(?:/>|>.*?</Relationship\s*>)", re.DOTALL)

SLIDE_ID_MIN = 256
SLIDE_ID_MAX = 2147483647


def _die(msg: str) -> NoReturn:
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def get_next_slide_number(slides_dir: Path) -> int:
    existing = [int(m.group(1)) for f in slides_dir.glob("slide*.xml")
                if (m := re.match(r"slide(\d+)\.xml", f.name))]
    return max(existing) + 1 if existing else 1


def parse_source(source: str) -> tuple[str, str | None]:
    if source.startswith("slideLayout") and source.endswith(".xml"):
        return ("layout", source)

    return ("slide", None)


def create_slide_from_layout(unpacked_dir: Path, layout_file: str, after: str | None = None) -> str:
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    layout_path = unpacked_dir / "ppt" / "slideLayouts" / layout_file

    if not layout_path.exists():
        _die(f"{layout_path} not found")

    next_num = get_next_slide_number(slides_dir)
    dest = f"slide{next_num}.xml"
    after_rid = _precheck_registration(unpacked_dir, after, dest)
    slides_dir.mkdir(parents=True, exist_ok=True)

    (slides_dir / dest).write_text(MINIMAL_SLIDE_XML, encoding="utf-8")

    rels_dir.mkdir(exist_ok=True)
    rels_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout_file}"/>
</Relationships>'''
    (rels_dir / f"{dest}.rels").write_text(rels_xml, encoding="utf-8")

    _register_slide(unpacked_dir, dest, layout_file, after_rid)
    return dest


def duplicate_slide(unpacked_dir: Path, source: str, after: str | None = None) -> str:
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    source_slide = slides_dir / source

    if not source_slide.exists():
        _die(f"{source_slide} not found")

    next_num = get_next_slide_number(slides_dir)
    dest = f"slide{next_num}.xml"
    after_rid = _precheck_registration(unpacked_dir, after, dest)

    shutil.copy2(source_slide, slides_dir / dest)

    source_rels = rels_dir / f"{source}.rels"
    shared_parts: list[str] = []
    if source_rels.exists():
        dest_rels = rels_dir / f"{dest}.rels"
        shutil.copy2(source_rels, dest_rels)
        rels_content = dest_rels.read_text(encoding="utf-8")
        rels_content = RELATIONSHIP_RE.sub(
            lambda m: "" if NOTES_SLIDE_TYPE_RE.search(m.group(0)) else m.group(0),
            rels_content,
        )
        dest_rels.write_text(rels_content, encoding="utf-8")
        shared_parts = sorted({
            t for t in re.findall(r'Type="[^"]*/relationships/(\w+)"', rels_content)
            if t in SHARED_PART_TYPES
        })

    _register_slide(unpacked_dir, dest, source, after_rid)
    if shared_parts:
        print(
            f"Note: {dest} shares its {', '.join(shared_parts)} part(s) with {source} "
            f"(they are referenced, not copied) — editing those parts changes both slides"
        )
    return dest


def _precheck_registration(unpacked_dir: Path, after: str | None, dest: str) -> str | None:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    if not pres_path.exists():
        _die(f"{pres_path} not found — is this an unpacked PPTX?")
    xml = pres_path.read_text(encoding="utf-8")

    has_slot = (
        "</p:sldIdLst>" in xml
        or re.search(r"<p:sldIdLst\s*/>", xml)
        or "</p:sldMasterIdLst>" in xml
    )
    if not has_slot:
        _die("presentation.xml has no <p:sldIdLst> (or <p:sldMasterIdLst> to anchor a new one)")

    stale = []
    content_types = unpacked_dir / "[Content_Types].xml"
    if content_types.exists() and f'PartName="/ppt/slides/{dest}"' in content_types.read_text(encoding="utf-8"):
        stale.append("[Content_Types].xml")
    pres_rels = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    if pres_rels.exists() and _find_slide_relationship(
        pres_rels.read_text(encoding="utf-8"), dest
    ):
        stale.append("presentation.xml.rels")
    if stale:
        _die(
            f"{dest} is still registered in {' and '.join(stale)} but absent from ppt/slides/ — "
            f"run clean.py first"
        )

    if not after:
        return None
    after_rid = _rid_for_slide(unpacked_dir, after)
    if not re.search(rf'<p:sldId\b[^>]*r:id="{re.escape(after_rid)}"[^>]*>', xml):
        _die(f"{after} ({after_rid}) is not listed in <p:sldIdLst>")
    return after_rid


def _register_slide(unpacked_dir: Path, dest: str, source_desc: str, after_rid: str | None) -> None:
    _add_to_content_types(unpacked_dir, dest)
    rid = _add_to_presentation_rels(unpacked_dir, dest)
    slide_id = _get_next_slide_id(unpacked_dir)
    pos, total = _insert_into_sld_id_lst(unpacked_dir, slide_id, rid, after_rid)

    print(f"Created ppt/slides/{dest} from {source_desc}")
    print(
        f'Inserted <p:sldId id="{slide_id}" r:id="{rid}"/> into <p:sldIdLst> '
        f"at position {pos} of {total}"
    )


def _add_to_content_types(unpacked_dir: Path, dest: str) -> None:
    content_types_path = unpacked_dir / "[Content_Types].xml"
    content_types = content_types_path.read_text(encoding="utf-8")

    new_override = f'<Override PartName="/ppt/slides/{dest}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'

    if f'PartName="/ppt/slides/{dest}"' not in content_types:
        content_types = content_types.replace("</Types>", f"  {new_override}\n</Types>")
        content_types_path.write_text(content_types, encoding="utf-8")


def _add_to_presentation_rels(unpacked_dir: Path, dest: str) -> str:
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    pres_rels = pres_rels_path.read_text(encoding="utf-8")

    existing = _find_slide_relationship(pres_rels, dest)
    if existing:
        return existing

    pres_xml = (unpacked_dir / "ppt" / "presentation.xml").read_text(encoding="utf-8")
    used = {int(n) for n in re.findall(r'\bId="rId(\d+)"', pres_rels)}
    used |= {int(n) for n in re.findall(r'\br:id="rId(\d+)"', pres_xml)}
    rid = f"rId{max(used) + 1 if used else 1}"

    new_rel = f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/{dest}"/>'
    pres_rels = pres_rels.replace("</Relationships>", f"  {new_rel}\n</Relationships>")
    pres_rels_path.write_text(pres_rels, encoding="utf-8")

    return rid


def _find_slide_relationship(pres_rels: str, slide_name: str) -> str | None:
    for m in re.finditer(r"<Relationship\b[^>]*>", pres_rels):
        element = m.group(0)
        if re.search(rf'Target="(?:/ppt/)?slides/{re.escape(slide_name)}"', element):
            id_match = re.search(r'\bId="([^"]+)"', element)
            if id_match:
                return id_match.group(1)
    return None


def _get_next_slide_id(unpacked_dir: Path) -> int:
    pres_content = (unpacked_dir / "ppt" / "presentation.xml").read_text(encoding="utf-8")
    used = {int(m) for m in re.findall(r'<p:sldId[^>]*\bid="(\d+)"', pres_content)}

    candidate = max((i for i in used if i >= SLIDE_ID_MIN), default=SLIDE_ID_MIN - 1) + 1
    if candidate <= SLIDE_ID_MAX and candidate not in used:
        return candidate
    for i in range(SLIDE_ID_MIN, SLIDE_ID_MAX + 1):
        if i not in used:
            return i
    _die("no slide id available in [256, 2147483647] — the deck is full")


def _insert_into_sld_id_lst(
    unpacked_dir: Path, slide_id: int, rid: str, after_rid: str | None = None
) -> tuple[int, int]:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    xml = pres_path.read_text(encoding="utf-8")
    entry = f'<p:sldId id="{slide_id}" r:id="{rid}"/>'

    if f'r:id="{rid}"' in xml:
        _die(f"presentation.xml already references {rid}; refusing to add a duplicate")

    if after_rid:
        open_tag = re.search(rf'<p:sldId\b[^>]*r:id="{re.escape(after_rid)}"[^>]*>', xml)
        if not open_tag:
            _die(f"{after_rid} is not listed in <p:sldIdLst>")
        end = open_tag.end()
        if not open_tag.group(0).endswith("/>"):
            close = xml.find("</p:sldId>", end)
            if close == -1:
                _die(f"unclosed <p:sldId> for {after_rid} in presentation.xml")
            end = close + len("</p:sldId>")
        xml = xml[:end] + entry + xml[end:]
    elif "</p:sldIdLst>" in xml:
        xml = xml.replace("</p:sldIdLst>", f"{entry}</p:sldIdLst>", 1)
    elif re.search(r"<p:sldIdLst\s*/>", xml):
        xml = re.sub(r"<p:sldIdLst\s*/>", f"<p:sldIdLst>{entry}</p:sldIdLst>", xml, count=1)
    elif "</p:sldMasterIdLst>" in xml:
        xml = xml.replace(
            "</p:sldMasterIdLst>", f"</p:sldMasterIdLst><p:sldIdLst>{entry}</p:sldIdLst>", 1
        )
    else:
        _die("presentation.xml has no <p:sldIdLst> (or <p:sldMasterIdLst> to anchor a new one)")

    pres_path.write_text(xml, encoding="utf-8")

    lst = re.search(r"<p:sldIdLst>(.*)</p:sldIdLst>", xml, re.DOTALL)
    entries = re.findall(r"<p:sldId\b[^>]*>", lst.group(1)) if lst else []
    position = next(
        (i for i, e in enumerate(entries, 1) if f'r:id="{rid}"' in e), len(entries)
    )
    return position, len(entries)


def _rid_for_slide(unpacked_dir: Path, slide_name: str) -> str:
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"
    rid = _find_slide_relationship(pres_rels_path.read_text(encoding="utf-8"), slide_name)
    if not rid:
        _die(f"{slide_name} has no relationship in presentation.xml.rels")
    return rid


def add_slide(unpacked_dir: Path, source: str, after: str | None = None) -> str:
    source_type, layout_file = parse_source(source)
    if source_type == "layout" and layout_file is not None:
        return create_slide_from_layout(unpacked_dir, layout_file, after)
    return duplicate_slide(unpacked_dir, source, after)


def add_slide_to_package(
    package: Path, source: str, after: str | None = None, output: Path | None = None
) -> str:
    out = output or package
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(package) as zf:
            safe_extract(zf, tmp_path)
        dest = add_slide(tmp_path, source, after)
        rezip(tmp_path, out)
    print(f"Wrote {out} — the new slide is ppt/slides/{dest} inside it (unpack to edit its content)")
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a slide to a PPTX: duplicate a slide or instantiate a layout. "
        "Registers content types, relationships, and <p:sldIdLst>."
    )
    parser.add_argument("target", help="Unpacked PPTX directory OR a .pptx/.potx file")
    parser.add_argument(
        "source",
        help="slideN.xml to duplicate, or slideLayoutN.xml to create from a layout "
        "(list layouts with: ls <dir>/ppt/slideLayouts/)",
    )
    parser.add_argument(
        "--after",
        metavar="SLIDE",
        help="insert after this slide, e.g. slide2.xml (default: append at the end)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="output file (only with a .pptx/.potx target; default: rewrite the input in place)",
    )
    args = parser.parse_args()

    target = Path(args.target)
    if target.is_dir():
        if args.output:
            parser.error("--output is only valid for .pptx/.potx input; a directory is modified in place")
        add_slide(target, args.source, args.after)
    elif target.is_file() and target.suffix.lower() in (".pptx", ".potx"):
        try:
            add_slide_to_package(target, args.source, args.after, Path(args.output) if args.output else None)
        except (OSError, ValueError, zipfile.BadZipFile) as e:
            _die(str(e))
    else:
        _die(f"{target} is neither a directory nor a .pptx/.potx file")


if __name__ == "__main__":
    main()
```

### `scripts/clean.py`

```python
"""Remove unreferenced files from an unpacked PPTX directory.

Usage: python clean.py <unpacked_dir>

Example:
    python clean.py unpacked/

This script removes:
- Orphaned slides (not in sldIdLst) and their relationships
- [trash] directory (unreferenced files)
- Orphaned .rels files for deleted resources
- Unreferenced media, embeddings, charts, diagrams, drawings, ink files
- Unreferenced theme files
- Unreferenced notes slides
- Content-Type overrides for deleted files
"""

import posixpath
import re
import sys
from pathlib import Path

import defusedxml.minidom

from office.helpers import SLIDE_REL_TYPE, opc_target, rels_source_part


def _slide_rids(pres_rels_path: Path, unpacked_dir: Path) -> dict[str, str]:
    source_part = rels_source_part(pres_rels_path, unpacked_dir)
    rels_dom = defusedxml.minidom.parse(str(pres_rels_path))

    rids: dict[str, str] = {}
    for rel in rels_dom.getElementsByTagName("Relationship"):
        if rel.getAttribute("Type") != SLIDE_REL_TYPE:
            continue
        part = opc_target(
            rel.getAttribute("Target"), source_part, rel.getAttribute("TargetMode")
        )
        if part is not None:
            rids[rel.getAttribute("Id")] = part
    return rids


def get_slides_in_sldidlst(unpacked_dir: Path) -> set[str]:
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"

    if not pres_path.exists() or not pres_rels_path.exists():
        return set()

    rid_to_slide = _slide_rids(pres_rels_path, unpacked_dir)

    pres_content = pres_path.read_text(encoding="utf-8")
    referenced_rids = set(re.findall(r'<p:sldId[^>]*r:id="([^"]+)"', pres_content))

    return {
        posixpath.basename(rid_to_slide[rid])
        for rid in referenced_rids
        if rid in rid_to_slide
    }


class RefusedToClean(Exception):
    """The package does not look the way a readable package should."""


def remove_orphaned_slides(unpacked_dir: Path) -> list[str]:
    slides_dir = unpacked_dir / "ppt" / "slides"
    slides_rels_dir = slides_dir / "_rels"
    pres_rels_path = unpacked_dir / "ppt" / "_rels" / "presentation.xml.rels"

    if not slides_dir.exists():
        return []

    referenced_slides = get_slides_in_sldidlst(unpacked_dir)
    on_disk = sorted(slides_dir.glob("slide*.xml"))

    if on_disk and not any(s.name in referenced_slides for s in on_disk):
        listed = re.findall(
            r'<p:sldId[^>]*r:id="([^"]+)"',
            (unpacked_dir / "ppt" / "presentation.xml").read_text(encoding="utf-8")
            if (unpacked_dir / "ppt" / "presentation.xml").exists()
            else "",
        )
        if listed:
            raise RefusedToClean(
                f"<p:sldIdLst> lists {len(listed)} slide(s) and none of the "
                f"{len(on_disk)} slide(s) on disk match any of them. Refusing to "
                f"delete them all — this is a parse failure, not an empty deck."
            )

    removed = []

    for slide_file in on_disk:
        if slide_file.name not in referenced_slides:
            rel_path = slide_file.relative_to(unpacked_dir)
            slide_file.unlink()
            removed.append(str(rel_path))

            rels_file = slides_rels_dir / f"{slide_file.name}.rels"
            if rels_file.exists():
                rels_file.unlink()
                removed.append(str(rels_file.relative_to(unpacked_dir)))

    if removed and pres_rels_path.exists():
        rels_dom = defusedxml.minidom.parse(str(pres_rels_path))
        source_part = rels_source_part(pres_rels_path, unpacked_dir)
        changed = False

        for rel in list(rels_dom.getElementsByTagName("Relationship")):
            if rel.getAttribute("Type") != SLIDE_REL_TYPE:
                continue
            part = opc_target(
                rel.getAttribute("Target"), source_part, rel.getAttribute("TargetMode")
            )
            if part is None:
                continue
            if posixpath.basename(part) not in referenced_slides:
                if rel.parentNode:
                    rel.parentNode.removeChild(rel)
                    changed = True

        if changed:
            with open(pres_rels_path, "wb") as f:
                f.write(rels_dom.toxml(encoding="utf-8"))

    return removed


def remove_trash_directory(unpacked_dir: Path) -> list[str]:
    trash_dir = unpacked_dir / "[trash]"
    removed = []

    if trash_dir.exists() and trash_dir.is_dir():
        for file_path in trash_dir.iterdir():
            if file_path.is_file():
                rel_path = file_path.relative_to(unpacked_dir)
                removed.append(str(rel_path))
                file_path.unlink()
        trash_dir.rmdir()

    return removed


def _referenced_by(rels_files, unpacked_dir: Path) -> set:
    referenced = set()

    for rels_file in rels_files:
        source_part = rels_source_part(rels_file, unpacked_dir)
        dom = defusedxml.minidom.parse(str(rels_file))
        for rel in dom.getElementsByTagName("Relationship"):
            part = opc_target(
                rel.getAttribute("Target"), source_part, rel.getAttribute("TargetMode")
            )
            if part is not None:
                referenced.add(Path(part))

    return referenced


def remove_orphaned_rels_files(unpacked_dir: Path) -> list[str]:
    resource_dirs = ["charts", "diagrams", "drawings"]
    removed = []

    for dir_name in resource_dirs:
        rels_dir = unpacked_dir / "ppt" / dir_name / "_rels"
        if not rels_dir.exists():
            continue

        for rels_file in rels_dir.glob("*.rels"):
            resource_file = rels_dir.parent / rels_file.name.replace(".rels", "")
            if not resource_file.exists():
                rels_file.unlink()
                removed.append(str(rels_file.relative_to(unpacked_dir)))

    return removed


def get_referenced_files(unpacked_dir: Path) -> set:
    return _referenced_by(sorted(unpacked_dir.rglob("*.rels")), unpacked_dir)


def remove_orphaned_files(unpacked_dir: Path, referenced: set) -> list[str]:
    resource_dirs = ["media", "embeddings", "charts", "diagrams", "tags", "drawings", "ink"]
    removed = []

    for dir_name in resource_dirs:
        dir_path = unpacked_dir / "ppt" / dir_name
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("*"):
            if not file_path.is_file():
                continue
            rel_path = file_path.relative_to(unpacked_dir)
            if rel_path not in referenced:
                file_path.unlink()
                removed.append(str(rel_path))

    theme_dir = unpacked_dir / "ppt" / "theme"
    if theme_dir.exists():
        for file_path in theme_dir.glob("theme*.xml"):
            rel_path = file_path.relative_to(unpacked_dir)
            if rel_path not in referenced:
                file_path.unlink()
                removed.append(str(rel_path))
                theme_rels = theme_dir / "_rels" / f"{file_path.name}.rels"
                if theme_rels.exists():
                    theme_rels.unlink()
                    removed.append(str(theme_rels.relative_to(unpacked_dir)))

    notes_dir = unpacked_dir / "ppt" / "notesSlides"
    if notes_dir.exists():
        for file_path in notes_dir.glob("*.xml"):
            if not file_path.is_file():
                continue
            rel_path = file_path.relative_to(unpacked_dir)
            if rel_path not in referenced:
                file_path.unlink()
                removed.append(str(rel_path))

        notes_rels_dir = notes_dir / "_rels"
        if notes_rels_dir.exists():
            for file_path in notes_rels_dir.glob("*.rels"):
                notes_file = notes_dir / file_path.name.replace(".rels", "")
                if not notes_file.exists():
                    file_path.unlink()
                    removed.append(str(file_path.relative_to(unpacked_dir)))

    return removed


def update_content_types(unpacked_dir: Path, removed_files: list[str]) -> None:
    ct_path = unpacked_dir / "[Content_Types].xml"
    if not ct_path.exists():
        return

    dom = defusedxml.minidom.parse(str(ct_path))
    changed = False

    for override in list(dom.getElementsByTagName("Override")):
        part_name = override.getAttribute("PartName").lstrip("/")
        if part_name in removed_files:
            if override.parentNode:
                override.parentNode.removeChild(override)
                changed = True

    if changed:
        with open(ct_path, "wb") as f:
            f.write(dom.toxml(encoding="utf-8"))


def clean_unused_files(unpacked_dir: Path) -> list[str]:
    all_removed = []

    if list(unpacked_dir.rglob("*.rels")) and not get_referenced_files(unpacked_dir):
        raise RefusedToClean(
            "no relationship in this package names a part we can resolve. "
            "Refusing to treat every file as unreferenced."
        )

    slides_removed = remove_orphaned_slides(unpacked_dir)
    all_removed.extend(slides_removed)

    trash_removed = remove_trash_directory(unpacked_dir)
    all_removed.extend(trash_removed)

    while True:
        removed_rels = remove_orphaned_rels_files(unpacked_dir)
        referenced = get_referenced_files(unpacked_dir)
        removed_files = remove_orphaned_files(unpacked_dir, referenced)

        total_removed = removed_rels + removed_files
        if not total_removed:
            break

        all_removed.extend(total_removed)

    if all_removed:
        update_content_types(unpacked_dir, all_removed)

    return all_removed


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python clean.py <unpacked_dir>", file=sys.stderr)
        print("Example: python clean.py unpacked/", file=sys.stderr)
        sys.exit(1)

    unpacked_dir = Path(sys.argv[1])

    if not unpacked_dir.exists():
        print(f"Error: {unpacked_dir} not found", file=sys.stderr)
        sys.exit(1)

    try:
        removed = clean_unused_files(unpacked_dir)
    except (RefusedToClean, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Nothing was deleted.", file=sys.stderr)
        sys.exit(1)

    if removed:
        print(f"Removed {len(removed)} unreferenced files:")
        for f in removed:
            print(f"  {f}")
    else:
        print("No unreferenced files found")
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

### `scripts/thumbnail.py`

```python
"""Create thumbnail grids from PowerPoint presentation slides.

Creates a grid layout of slide thumbnails for quick visual analysis.
Labels each thumbnail with its XML filename (e.g., slide1.xml).
Hidden slides are shown with a placeholder pattern.

Usage:
    python thumbnail.py input.pptx [output_prefix] [--cols N]

Examples:
    python thumbnail.py presentation.pptx
    # Creates: thumbnails.jpg

    python thumbnail.py template.pptx grid --cols 4
    # Creates: grid.jpg (or grid-1.jpg, grid-2.jpg for large decks)
"""

import argparse
import posixpath
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import defusedxml.minidom
from defusedxml import ElementTree
from office.helpers import SLIDE_REL_TYPE, opc_target
from office.soffice import run_soffice
from PIL import Image, ImageDraw, ImageFont


THUMBNAIL_WIDTH = 300
CONVERSION_DPI = 100
MAX_COLS = 6
DEFAULT_COLS = 3
JPEG_QUALITY = 95
GRID_PADDING = 20
BORDER_WIDTH = 2
FONT_SIZE_RATIO = 0.10
LABEL_PADDING_RATIO = 0.4


def main():
    parser = argparse.ArgumentParser(
        description="Create thumbnail grids from PowerPoint slides."
    )
    parser.add_argument("input", help="Input PowerPoint file (.pptx)")
    parser.add_argument(
        "output_prefix",
        nargs="?",
        default="thumbnails",
        help="Output prefix for image files (default: thumbnails)",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=DEFAULT_COLS,
        help=f"Number of columns (default: {DEFAULT_COLS}, max: {MAX_COLS})",
    )

    args = parser.parse_args()

    cols = min(args.cols, MAX_COLS)
    if args.cols > MAX_COLS:
        print(f"Warning: Columns limited to {MAX_COLS}")

    input_path = Path(args.input)
    if not input_path.exists() or input_path.suffix.lower() != ".pptx":
        print(f"Error: Invalid PowerPoint file: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(f"{args.output_prefix}.jpg")

    try:
        slide_info = get_slide_info(input_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            visible_images = convert_to_images(input_path, temp_path)

            if not visible_images and not any(s["hidden"] for s in slide_info):
                print("Error: No slides found", file=sys.stderr)
                sys.exit(1)

            slides = build_slide_list(slide_info, visible_images, temp_path)

            grid_files = create_grids(slides, cols, THUMBNAIL_WIDTH, output_path)

            print(f"Created {len(grid_files)} grid(s):")
            for grid_file in grid_files:
                print(f"  {grid_file}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _is_hidden(zf: zipfile.ZipFile, part: str) -> bool:
    try:
        with zf.open(part) as f:
            for _, root in ElementTree.iterparse(f, events=("start",)):
                return root.get("show") in ("0", "false")  
    except (KeyError, ElementTree.ParseError):
        return False
    return False


def get_slide_info(pptx_path: Path) -> list[dict]:
    with zipfile.ZipFile(pptx_path, "r") as zf:
        rels_content = zf.read("ppt/_rels/presentation.xml.rels").decode("utf-8")
        rels_dom = defusedxml.minidom.parseString(rels_content)

        rid_to_part = {}
        for rel in rels_dom.getElementsByTagName("Relationship"):
            if rel.getAttribute("Type") != SLIDE_REL_TYPE:
                continue
            part = opc_target(
                rel.getAttribute("Target"),
                "ppt/presentation.xml",
                rel.getAttribute("TargetMode"),
            )
            if part is not None:
                rid_to_part[rel.getAttribute("Id")] = part

        pres_content = zf.read("ppt/presentation.xml").decode("utf-8")
        pres_dom = defusedxml.minidom.parseString(pres_content)

        present = set(zf.namelist())

        slides = []
        for sld_id in pres_dom.getElementsByTagName("p:sldId"):
            part = rid_to_part.get(sld_id.getAttribute("r:id"))
            if part is not None and part in present:
                slides.append(
                    {"name": posixpath.basename(part), "hidden": _is_hidden(zf, part)}
                )

        return slides


def build_slide_list(
    slide_info: list[dict],
    visible_images: list[Path],
    temp_dir: Path,
) -> list[tuple[Path, str]]:
    visible_count = sum(1 for info in slide_info if not info["hidden"])
    rendered_hidden = len(visible_images) == len(slide_info) != visible_count

    if not rendered_hidden and visible_count != len(visible_images):
        raise ValueError(
            f"LibreOffice rendered {len(visible_images)} page(s) for {visible_count} "
            f"visible slide(s) of {len(slide_info)}; thumbnails would be mislabeled"
        )

    if visible_images:
        with Image.open(visible_images[0]) as img:
            placeholder_size = img.size
    else:
        placeholder_size = (1920, 1080)

    slides = []
    visible_idx = 0

    for info in slide_info:
        if info["hidden"] and not rendered_hidden:
            placeholder_path = temp_dir / f"hidden-{info['name']}.jpg"
            placeholder_img = create_hidden_placeholder(placeholder_size)
            placeholder_img.save(placeholder_path, "JPEG")
            slides.append((placeholder_path, f"{info['name']} (hidden)"))
        else:
            label = f"{info['name']} (hidden)" if info["hidden"] else info["name"]
            slides.append((visible_images[visible_idx], label))
            visible_idx += 1

    return slides


def create_hidden_placeholder(size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size, color="#F0F0F0")
    draw = ImageDraw.Draw(img)
    line_width = max(5, min(size) // 100)
    draw.line([(0, 0), size], fill="#CCCCCC", width=line_width)
    draw.line([(size[0], 0), (0, size[1])], fill="#CCCCCC", width=line_width)
    return img


def convert_to_images(pptx_path: Path, temp_dir: Path) -> list[Path]:
    pdf_path = temp_dir / f"{pptx_path.stem}.pdf"

    result = run_soffice(
        ["--headless", "--convert-to", "pdf", "--outdir", str(temp_dir), str(pptx_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not pdf_path.exists():
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"PDF conversion failed: {detail}" if detail else "PDF conversion failed")

    result = subprocess.run(
        [
            "pdftoppm",
            "-jpeg",
            "-r",
            str(CONVERSION_DPI),
            str(pdf_path),
            str(temp_dir / "slide"),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError("Image conversion failed")

    return sorted(temp_dir.glob("slide-*.jpg"))


def create_grids(
    slides: list[tuple[Path, str]],
    cols: int,
    width: int,
    output_path: Path,
) -> list[str]:
    max_per_grid = cols * (cols + 1)
    grid_files = []

    for chunk_idx, start_idx in enumerate(range(0, len(slides), max_per_grid)):
        end_idx = min(start_idx + max_per_grid, len(slides))
        chunk_slides = slides[start_idx:end_idx]

        grid = create_grid(chunk_slides, cols, width)

        if len(slides) <= max_per_grid:
            grid_filename = output_path
        else:
            stem = output_path.stem
            suffix = output_path.suffix
            grid_filename = output_path.parent / f"{stem}-{chunk_idx + 1}{suffix}"

        grid_filename.parent.mkdir(parents=True, exist_ok=True)
        grid.save(str(grid_filename), quality=JPEG_QUALITY)
        grid_files.append(str(grid_filename))

    return grid_files


def create_grid(
    slides: list[tuple[Path, str]],
    cols: int,
    width: int,
) -> Image.Image:
    font_size = int(width * FONT_SIZE_RATIO)
    label_padding = int(font_size * LABEL_PADDING_RATIO)

    with Image.open(slides[0][0]) as img:
        aspect = img.height / img.width
    height = int(width * aspect)

    rows = (len(slides) + cols - 1) // cols
    grid_w = cols * width + (cols + 1) * GRID_PADDING
    grid_h = rows * (height + font_size + label_padding * 2) + (rows + 1) * GRID_PADDING

    grid = Image.new("RGB", (grid_w, grid_h), "white")
    draw = ImageDraw.Draw(grid)

    try:
        font = ImageFont.load_default(size=font_size)
    except Exception:
        font = ImageFont.load_default()

    for i, (img_path, slide_name) in enumerate(slides):
        row, col = i // cols, i % cols
        x = col * width + (col + 1) * GRID_PADDING
        y_base = (
            row * (height + font_size + label_padding * 2) + (row + 1) * GRID_PADDING
        )

        label = slide_name
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (x + (width - text_w) // 2, y_base + label_padding),
            label,
            fill="black",
            font=font,
        )

        y_thumbnail = y_base + label_padding + font_size + label_padding

        with Image.open(img_path) as img:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            w, h = img.size
            tx = x + (width - w) // 2
            ty = y_thumbnail + (height - h) // 2
            grid.paste(img, (tx, ty))

            if BORDER_WIDTH > 0:
                draw.rectangle(
                    [
                        (tx - BORDER_WIDTH, ty - BORDER_WIDTH),
                        (tx + w + BORDER_WIDTH - 1, ty + h + BORDER_WIDTH - 1),
                    ],
                    outline="gray",
                    width=BORDER_WIDTH,
                )

    return grid


if __name__ == "__main__":
    main()
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
