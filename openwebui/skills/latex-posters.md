---
name: latex-posters
description: OpenRouter API key for the skill's LLM-powered steps.
---

# LaTeX Research Posters

## Overview

Research posters are a critical medium for scientific communication at conferences, symposia, and academic events. This skill provides comprehensive guidance for creating professional, visually appealing research posters using LaTeX packages. Generate publication-quality posters with proper layout, typography, color schemes, and visual hierarchy.

## When to Use This Skill

This skill should be used when:
- Creating research posters for conferences, symposia, or poster sessions
- Designing academic posters for university events or thesis defenses
- Preparing visual summaries of research for public engagement
- Converting scientific papers into poster format
- Creating template posters for research groups or departments
- Designing posters that comply with specific conference size requirements (A0, A1, 36×48", etc.)
- Building posters with complex multi-column layouts
- Integrating figures, tables, equations, and citations in poster format

## AI-Powered Visual Element Generation

**STANDARD WORKFLOW: Generate ALL major visual elements using AI before creating the LaTeX poster.**

This is the recommended approach for creating visually compelling posters:
1. Plan all visual elements needed (title, intro, methods, results, conclusions)
2. Generate each element using scientific-schematics or Nano Banana Pro
3. Assemble generated images in the LaTeX template
4. Add text content around the visuals

**Target: 60-70% of poster area should be AI-generated visuals, 30-40% text.**

---

### Hard limits (do not exceed)

These are limits, not guidelines. Violating them is the single most common cause of a
failed poster. Full reasoning, per-graphic-type tables, and worked examples are in
[references/ai_graphics_for_posters.md](references/ai_graphics_for_posters.md).

| Constraint | Limit |
| --- | --- |
| Elements per AI-generated graphic | **3-4 maximum** (3 ideal) |
| Words per graphic | **10 maximum** |
| White space per graphic | **50% minimum** (60% better) |
| Key numbers / metrics | **120pt+** |
| Labels | **80pt+** |
| Body text on the poster | **24pt+** |
| Content sections (A0) | **5-6 maximum** |
| Total words on the poster | **300-800** |
| Figure width | `0.85\linewidth`, never `1.0` |

Every graphic prompt must include: `POSTER FORMAT for A0`, an explicit element or word
count (`ONLY 3 icons`, `3 words total`), a font size (`GIANT (120pt+)`), `60% white space`,
and a viewing distance (`readable from 10-12 feet`).

**Two mandatory review gates.** Skipping either is how unreadable posters happen:

- **Before generating** — for each planned graphic, confirm it is 3-4 items, one message,
  under 10 words, and not a 5+ stage workflow. If not, split it into several graphics.
- **After generating, before assembly** — open each figure at 25% zoom. All text readable,
  4 or fewer elements, 50%+ white space, understandable in 2 seconds. Any failure means
  regenerate or split. Do not assemble a poster from figures that failed.

Patterns that always fail: `7-stage workflow`, `timeline with annual milestones`,
`3 case studies in one graphic`, `comparison of 5+ methods`, `architecture with all layers`.
Collapse each to 3 high-level items, or make several separate graphics.

**Overflow is an error, not a warning.** After compiling, run `grep -i overfull poster.log`
and inspect all four edges at 100% zoom. See
[references/compilation_and_quality_control.md](references/compilation_and_quality_control.md).

## Scientific Schematics Integration

For detailed guidance on creating schematics, refer to the **scientific-schematics** skill documentation.

**Key capabilities:**
- Nano Banana Pro automatically generates, reviews, and refines diagrams
- Creates publication-quality images with proper formatting
- Ensures accessibility (colorblind-friendly, high contrast)
- Supports iterative refinement for complex diagrams

---

## Core Capabilities

Three poster packages are supported — **beamerposter** (Beamer syntax, institutional
themes), **tikzposter** (modern, colorful, flexible), and **baposter** (structured
multi-column). Package comparison, layout and grid systems, design principles, standard
sizes, per-package templates, figure and image integration, color schemes, typography,
and QR codes are all documented in
[references/latex_poster_reference.md](references/latex_poster_reference.md).

Reusable per-section content patterns, accessibility requirements, and presentation-day
guidance are in
[references/poster_patterns_and_presentation.md](references/poster_patterns_and_presentation.md).

## Workflow for Poster Creation

### Stage 1: Planning and Content Development

1. **Determine poster requirements**:
   - Conference size specifications (A0, 36×48", etc.)
   - Orientation (portrait vs. landscape)
   - Submission deadlines and format requirements

2. **Develop content outline**:
   - Identify 1-3 core messages
   - Select key figures (typically 3-6 main visuals)
   - Draft concise text for each section (bullet points preferred)
   - Aim for 300-800 words total

3. **Choose LaTeX package**:
   - beamerposter: If familiar with Beamer, need institutional themes
   - tikzposter: For modern, colorful designs with flexibility
   - baposter: For structured, professional multi-column layouts

### Stage 2: Generate Visual Elements (AI-Powered)

**CRITICAL: Generate SIMPLE figures with MINIMAL content. Each graphic = ONE message.**

**Content limits:**
- Maximum 4-5 elements per graphic
- Maximum 15 words total per graphic
- 50% white space minimum
- GIANT fonts (80pt+ for labels, 120pt+ for key numbers)

1. **Create figures directory**:
   ```bash
   mkdir -p figures
   ```

2. **Generate SIMPLE visual elements**:
   ```bash
   # Introduction - ONLY 3 icons/elements
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE visual with ONLY 3 elements: [icon1] [icon2] [icon3]. ONE word labels (80pt+). 50% white space. Readable from 8 feet." -o figures/intro.png
   
   # Methods - ONLY 4 steps maximum
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE flowchart with ONLY 4 boxes: STEP1 → STEP2 → STEP3 → STEP4. GIANT labels (100pt+). 50% white space. NO sub-steps." -o figures/methods.png
   
   # Results - ONLY 3 bars/comparisons
   python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE chart with ONLY 3 bars. GIANT percentages ON bars (120pt+). NO axis, NO legend. 50% white space." -o figures/results.png
   
   # Conclusions - EXACTLY 3 items with GIANT numbers
   python scripts/generate_schematic.py "POSTER FORMAT for A0. EXACTLY 3 key findings: '[NUMBER]' (150pt) '[LABEL]' (60pt) for each. 50% white space. NO other text." -o figures/conclusions.png
   ```

3. **Review generated figures - check for overflow:**
   - **View at 25% zoom**: All text still readable?
   - **Count elements**: More than 5? → Regenerate simpler
   - **Check white space**: Less than 40%? → Add "60% white space" to prompt
   - **Font too small?**: Add "EVEN LARGER" or increase pt sizes
   - **Still overflowing?**: Reduce to 3 elements instead of 4-5

### Stage 3: Design and Layout

1. **Select or create template**:
   - Start with provided templates in `assets/`
   - Customize color scheme to match branding
   - Configure page size and orientation

2. **Design layout structure**:
   - Plan column structure (2, 3, or 4 columns)
   - Map content flow (typically left-to-right, top-to-bottom)
   - Allocate space for title (10-15%), content (70-80%), footer (5-10%)

3. **Set typography**:
   - Configure font sizes for different hierarchy levels
   - Ensure minimum 24pt body text
   - Test readability from 4-6 feet distance

### Stage 4: Content Integration

1. **Create poster header**:
   - Title (concise, descriptive, 10-15 words)
   - Authors and affiliations
   - Institution logos (high-resolution)
   - Conference logo if required

2. **Integrate AI-generated figures**:
   - Add all figures from Stage 2 to appropriate sections
   - Use `\includegraphics` with proper sizing
   - Ensure figures dominate each section (visuals first, text second)
   - Center figures within blocks for visual impact

3. **Add minimal supporting text**:
   - Keep text minimal and scannable (300-800 words total)
   - Use bullet points, not paragraphs
   - Write in active voice
   - Text should complement figures, not duplicate them

4. **Add supplementary elements**:
   - QR codes for supplementary materials
   - References (cite key papers only, 5-10 typical)
   - Contact information and acknowledgments

### Stage 5: Refinement and Testing

1. **Review and iterate**:
   - Check for typos and errors
   - Verify all figures are high resolution
   - Ensure consistent formatting
   - Confirm color scheme works well together

2. **Test readability**:
   - Print at 25% scale and read from 2-3 feet (simulates poster from 8-12 feet)
   - Check color on different monitors
   - Verify QR codes function correctly
   - Ask colleague to review

3. **Optimize for printing**:
   - Embed all fonts in PDF
   - Verify image resolution
   - Check PDF size requirements
   - Include bleed area if required

### Stage 6: Compilation and Delivery

1. **Compile final PDF**:
   ```bash
   pdflatex poster.tex
   # Or for better font support:
   lualatex poster.tex
   ```

2. **Verify output quality**:
   - Check all elements are visible and correctly positioned
   - Zoom to 100% and inspect figure quality
   - Verify colors match expectations
   - Confirm PDF opens correctly on different viewers

3. **Prepare for printing**:
   - Export as PDF/X-1a if required
   - Save backup copies
   - Get test print on regular paper first
   - Order professional printing 2-3 days before deadline

4. **Create supplementary materials**:
   - Save PNG/JPG version for social media
   - Create handout version (8.5×11" summary)
   - Prepare digital version for email sharing

## Integration with Other Skills

This skill works effectively with:
- **Scientific Schematics**: CRITICAL - Use for generating all poster diagrams and flowcharts
- **Generate Image / Nano Banana Pro**: For stylized graphics, conceptual illustrations, and summary visuals
- **Scientific Writing**: For developing poster content from papers
- **Literature Review**: For contextualizing research
- **Data Analysis**: For creating result figures and charts

**Recommended workflow**: Always use scientific-schematics and generate-image skills BEFORE creating the LaTeX poster to generate all visual elements.

## Common Pitfalls to Avoid

**AI-Generated Graphics Mistakes (MOST COMMON):**
- ❌ Too many elements in one graphic (10+ items) → Keep to 3-5 max
- ❌ Text too small in AI graphics → Specify "GIANT (100pt+)" or "HUGE (150pt+)"
- ❌ Too much detail in prompts → Use "SIMPLE" and "ONLY X elements"
- ❌ No white space specification → Add "50% white space" to every prompt
- ❌ Complex flowcharts with 8+ steps → Limit to 4-5 steps maximum
- ❌ Comparison charts with 6+ items → Limit to 3 items maximum
- ❌ Key findings with 5+ metrics → Show only top 3

**Fixing Overflow in AI Graphics:**
If your AI-generated graphics are overflowing or have small text:
1. Add "SIMPLER" or "ONLY 3 elements" to prompt
2. Increase font sizes: "150pt+" instead of "80pt+"
3. Add "60% white space" instead of "50%"
4. Remove sub-details: "NO sub-steps", "NO axis labels", "NO legend"
5. Regenerate with fewer elements

**Design Mistakes**:
- ❌ Too much text (over 1000 words)
- ❌ Font sizes too small (under 24pt body text)
- ❌ Low-contrast color combinations
- ❌ Cluttered layout with no white space
- ❌ Inconsistent styling across sections
- ❌ Poor quality or pixelated images

**Content Mistakes**:
- ❌ No clear narrative or message
- ❌ Too many research questions or objectives
- ❌ Overuse of jargon without definitions
- ❌ Results without context or interpretation
- ❌ Missing author contact information

**Technical Mistakes**:
- ❌ Wrong poster dimensions for conference requirements
- ❌ RGB colors sent to CMYK printer (color shift)
- ❌ Fonts not embedded in PDF
- ❌ File size too large for submission portal
- ❌ QR codes too small or not tested

**Best Practices**:
- ✅ Generate SIMPLE AI graphics with 3-5 elements max
- ✅ Use GIANT fonts (100pt+) for key numbers in graphics
- ✅ Specify "50% white space" in every AI prompt
- ✅ Follow conference size specifications exactly
- ✅ Test print at reduced scale before final printing
- ✅ Use high-contrast, accessible color schemes
- ✅ Keep text minimal and highly scannable
- ✅ Include clear contact information and QR codes
- ✅ Proofread carefully (errors are magnified on posters!)

## Package Installation

Ensure required LaTeX packages are installed:

```bash
# For TeX Live (Linux/Mac)
tlmgr install beamerposter tikzposter baposter

# For MiKTeX (Windows)
# Packages typically auto-install on first use

# Additional recommended packages
tlmgr install qrcode graphics xcolor tcolorbox subcaption
```

## Scripts and Automation

Helper scripts available in `scripts/` directory:

- `review_poster.sh`: Poster review and validation
- `generate_schematic.py`: Generate scientific diagrams and schematics

## References

- [references/ai_graphics_for_posters.md](references/ai_graphics_for_posters.md): full AI
  graphic rules, per-type limits, worked prompt examples, and the review gates.
- [references/latex_poster_reference.md](references/latex_poster_reference.md): packages,
  layout, design, sizes, templates, figures, color, typography, QR codes.
- [references/compilation_and_quality_control.md](references/compilation_and_quality_control.md):
  compilation engines and the complete pre-print QC procedure.
- [references/poster_patterns_and_presentation.md](references/poster_patterns_and_presentation.md):
  content patterns, accessibility, presentation tips.
- [references/latex_poster_packages.md](references/latex_poster_packages.md): detailed
  comparison of beamerposter, tikzposter, and baposter with examples.
- [references/poster_layout_design.md](references/poster_layout_design.md): layout
  principles, grid systems, and visual flow.
- [references/poster_design_principles.md](references/poster_design_principles.md):
  typography, color theory, visual hierarchy, and accessibility.
- [references/poster_content_guide.md](references/poster_content_guide.md): content
  organization, writing style, and section-specific guidance.

## Templates

Ready-to-use poster templates in `assets/` directory:

- beamerposter templates (classic, modern, colorful)
- tikzposter templates (default, rays, wave, envelope)
- baposter templates (portrait, landscape, minimal)
- Example posters from various scientific disciplines
- Color scheme definitions and institutional templates

Load these templates and customize for your specific research and conference requirements.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/latex-posters/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/README.md`

# LaTeX Research Poster Generation Skill

Create professional, publication-ready research posters for conferences and academic presentations using LaTeX.

## Overview

This skill provides comprehensive guidance for creating research posters with three major LaTeX packages:
- **beamerposter**: Traditional academic posters, familiar Beamer syntax
- **tikzposter**: Modern, colorful designs with TikZ integration
- **baposter**: Structured multi-column layouts with automatic positioning

## Quick Start

### 1. Choose a Template

Browse templates in `assets/`:
- `beamerposter_template.tex` - Classic academic style
- `tikzposter_template.tex` - Modern, colorful design
- `baposter_template.tex` - Structured multi-column layout

### 2. Customize Content

Edit the template with your research:
- Title, authors, affiliations
- Introduction, methods, results, conclusions
- Replace placeholder figures with your images
- Update references and acknowledgments

### 3. Configure for Full Page

Posters should span the entire page with minimal margins:

```latex
% beamerposter - full page setup
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}
\setbeamersize{text margin left=5mm, text margin right=5mm}
\usepackage[margin=10mm]{geometry}

% tikzposter - full page setup
\documentclass[25pt,a0paper,portrait,margin=10mm,innermargin=15mm]{tikzposter}

% baposter - full page setup
\documentclass[a0paper,portrait,fontscale=0.285]{baposter}
```

### 4. Compile

```bash
pdflatex poster.tex

# Or for better font support:
lualatex poster.tex
xelatex poster.tex
```

### 5. Review PDF Quality

**Essential before printing!**

```bash
# Run automated checks
./scripts/review_poster.sh poster.pdf

# Manual verification (see checklist below)
```

## Key Features

### Full Page Coverage

All templates configured to maximize content area:
- Minimal outer margins (5-15mm)
- Optimal spacing between columns (15-20mm)
- Proper block padding for readability
- No wasted white space

### PDF Quality Control

**Automated Checks** (`review_poster.sh`):
- Page size verification
- Font embedding check
- Image resolution analysis
- File size optimization

**Manual Verification** (`assets/poster_quality_checklist.md`):
- Visual inspection at 100% zoom
- Reduced-scale print test (25%)
- Typography and spacing review
- Content completeness check

### Design Principles

All templates follow evidence-based poster design:
- **Typography**: 72pt+ title, 48-72pt headers, 24-36pt body text
- **Color**: High contrast (≥4.5:1), color-blind friendly palettes
- **Layout**: Clear visual hierarchy, logical flow
- **Content**: 300-800 words maximum, 40-50% visual content

## Common Poster Sizes

Templates support all standard sizes:

| Size | Dimensions | Configuration |
|------|------------|---------------|
| A0 | 841 × 1189 mm | `size=a0` or `a0paper` |
| A1 | 594 × 841 mm | `size=a1` or `a1paper` |
| 36×48" | 914 × 1219 mm | Custom page size |
| 42×56" | 1067 × 1422 mm | Custom page size |

## Documentation

### Reference Guides

**Comprehensive Documentation** (in `references/`):

1. **`latex_poster_packages.md`** (746 lines)
   - Detailed comparison of beamerposter, tikzposter, baposter
   - Package-specific syntax and examples
   - Strengths, limitations, best use cases
   - Theme and color customization
   - Compilation tips and troubleshooting

2. **`poster_design_principles.md`** (807 lines)
   - Visual hierarchy and white space
   - Typography: font selection, sizing, readability
   - Color theory: schemes, contrast, accessibility
   - Color-blind friendly palettes
   - Icons, graphics, and visual elements
   - Common design mistakes to avoid

3. **`poster_layout_design.md`** (650+ lines)
   - Grid systems (2, 3, 4-column layouts)
   - Visual flow and reading patterns
   - Spatial organization strategies
   - White space management
   - Block and box design
   - Layout patterns by research type

4. **`poster_content_guide.md`** (900+ lines)
   - Content strategy (3-5 minute rule)
   - Word budgets by section
   - Visual-to-text ratio (40-50% visual)
   - Section-specific writing guidance
   - Figure integration and captions
   - From paper to poster adaptation

5. **`ai_graphics_for_posters.md`**
   - Hard limits on elements, words, white space, and font sizes
   - Per-graphic-type content limits with worked before/after prompts
   - The mandatory pre- and post-generation review gates
   - Patterns that always fail, and how to split them

6. **`latex_poster_reference.md`**
   - Package selection, layout, and standard poster sizes
   - Figure and image integration, QR codes
   - Color schemes and typography

7. **`compilation_and_quality_control.md`**
   - Compilation engines and bibliography handling
   - Page-size verification and overflow detection
   - Reduced-scale test prints, font embedding, image DPI, file size
   - Log-warning triage

8. **`poster_patterns_and_presentation.md`**
   - Reusable content patterns per poster section
   - Accessibility and inclusive design
   - Presentation-day guidance

### Tools and Assets

**Scripts** (in `scripts/`):
- `review_poster.sh`: Automated PDF quality check
  - Page size verification
  - Font embedding check
  - Image resolution analysis
  - File size assessment

**Checklists** (in `assets/`):
- `poster_quality_checklist.md`: Comprehensive pre-printing checklist
  - Pre-compilation checks
  - PDF quality verification
  - Visual inspection items
  - Accessibility checks
  - Peer review guidelines
  - Final printing checklist

**Templates** (in `assets/`):
- `beamerposter_template.tex`: Full working template
- `tikzposter_template.tex`: Full working template
- `baposter_template.tex`: Full working template

## Workflow

### Recommended Poster Creation Process

**1. Planning** (before LaTeX)
- Determine conference requirements (size, orientation)
- Identify 3-5 key results to highlight
- Create figures (300+ DPI)
- Draft 300-800 word content outline

**2. Template Selection**
- Choose package based on needs:
  - **beamerposter**: Traditional conferences, institutional branding
  - **tikzposter**: Modern conferences, creative fields
  - **baposter**: Multi-section posters, structured layouts

**3. Content Integration**
- Copy template and customize
- Replace placeholder text
- Add figures and ensure high resolution
- Configure colors to match branding

**4. Compilation & Review**
- Compile to PDF
- Run `review_poster.sh` for automated checks
- Review visually at 100% zoom
- Check against `poster_quality_checklist.md`

**5. Test Print**
- **Critical step!** Print at 25% scale
- A0 → A4 paper, 36×48" → Letter paper
- View from 2-3 feet (simulates 8-12 feet for full poster)
- Verify readability and colors

**6. Revisions**
- Fix any issues identified
- Proofread carefully (errors are magnified!)
- Get colleague feedback
- Final compilation

**7. Printing**
- Verify page size: `pdfinfo poster.pdf`
- Check fonts embedded: `pdffonts poster.pdf`
- Send to professional printer 2-3 days before deadline
- Keep backup copy

## Troubleshooting

### Large White Margins

**Problem**: Excessive white space around poster edges

**Solution**:
```latex
% beamerposter
\setbeamersize{text margin left=5mm, text margin right=5mm}
\usepackage[margin=10mm]{geometry}

% tikzposter
\documentclass[..., margin=5mm, innermargin=10mm]{tikzposter}

% baposter
\documentclass[a0paper, margin=5mm]{baposter}
```

### Content Cut Off

**Problem**: Text or figures extending beyond page

**Solution**:
- Check total width: columns + spacing + margins = pagewidth
- Reduce column widths or spacing
- Debug with visible page boundary:
```latex
\usepackage{eso-pic}
\AddToShipoutPictureBG{
  \AtPageLowerLeft{
    \put(0,0){\framebox(\LenToUnit{\paperwidth},\LenToUnit{\paperheight}){}}
  }
}
```

### Blurry Images

**Problem**: Pixelated or low-quality figures

**Solution**:
- Use vector graphics (PDF, SVG) when possible
- Raster images: minimum 300 DPI at final print size
- For A0 width (33.1"): 300 DPI = 9930 pixels minimum
- Check with: `pdfimages -list poster.pdf`

### Fonts Not Embedded

**Problem**: Printer rejects PDF due to missing fonts

**Solution**:
```bash
# Recompile with embedded fonts
pdflatex -dEmbedAllFonts=true poster.tex

# Verify embedding
pdffonts poster.pdf
# All fonts should show "yes" in "emb" column
```

### File Too Large

**Problem**: PDF exceeds email size limit (>50MB)

**Solution**:
```bash
# Compress for digital sharing
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=poster_compressed.pdf poster.pdf

# Keep original uncompressed version for printing
```

## Common Mistakes to Avoid

### Content
- ❌ Too much text (>1000 words)
- ❌ Font sizes too small (<24pt body text)
- ❌ No clear main message
- ✅ 300-800 words, 30pt+ body text, 1-3 key findings

### Design
- ❌ Poor color contrast (<4.5:1)
- ❌ Red-green color combinations (color-blind issue)
- ❌ Cluttered layout with no white space
- ✅ High contrast, accessible colors, generous spacing

### Technical
- ❌ Wrong poster dimensions
- ❌ Low resolution images (<300 DPI)
- ❌ Fonts not embedded
- ✅ Verify specs, high-res images, embedded fonts

## Package Comparison

Quick reference for choosing the right package:

| Feature | beamerposter | tikzposter | baposter |
|---------|--------------|------------|----------|
| **Learning Curve** | Easy (Beamer users) | Moderate | Moderate |
| **Aesthetics** | Traditional | Modern | Professional |
| **Customization** | Moderate | High (TikZ) | Structured |
| **Compilation Speed** | Fast | Slower | Fast-Medium |
| **Best For** | Academic conferences | Creative designs | Multi-column layouts |

**Recommendation**:
- First-time poster makers: **beamerposter** (familiar, simple)
- Modern conferences: **tikzposter** (beautiful, flexible)
- Complex layouts: **baposter** (automatic positioning)

## Example Usage

### In Scientific Writer CLI

```
> Create a research poster for NeurIPS conference on transformer attention

The assistant will:
1. Ask about poster size and orientation
2. Generate complete LaTeX poster with your content
3. Configure for full page coverage
4. Provide compilation instructions
5. Run quality checks on generated PDF
```

### Manual Creation

```bash
# 1. Copy template
cp assets/tikzposter_template.tex my_poster.tex

# 2. Edit content
vim my_poster.tex

# 3. Compile
pdflatex my_poster.tex

# 4. Review
./scripts/review_poster.sh my_poster.pdf

# 5. Test print at 25% scale
# (A0 on A4 paper)

# 6. Final printing
```

## Tips for Success

### Content Strategy
1. **One main message**: What's the one thing viewers should remember?
2. **3-5 key figures**: Visual content dominates
3. **300-800 words**: Less is more
4. **Bullet points**: More scannable than paragraphs

### Design Strategy
1. **High contrast**: Dark on light or light on dark
2. **Large fonts**: 30pt+ body text for readability from distance
3. **White space**: 30-40% of poster should be empty
4. **Visual hierarchy**: Vary sizes significantly (title 3× body text)

### Technical Strategy
1. **Test early**: Print at 25% scale before final printing
2. **Vector graphics**: Use PDF/SVG when possible
3. **Verify specs**: Check page size, fonts, resolution
4. **Get feedback**: Ask colleague to review before printing

## Additional Resources

### Online Tools
- **Color contrast checker**: https://webaim.org/resources/contrastchecker/
- **Color blindness simulator**: https://www.color-blindness.com/coblis-color-blindness-simulator/
- **Color palette generator**: https://coolors.co/

### LaTeX Packages
- `beamerposter`: Extends Beamer for poster-sized documents
- `tikzposter`: Modern poster creation with TikZ
- `baposter`: Box-based automatic poster layout
- `qrcode`: Generate QR codes in LaTeX
- `graphicx`: Include images
- `tcolorbox`: Colored boxes and frames

### Further Reading
- All reference documents in `references/` directory
- Quality checklist in `assets/poster_quality_checklist.md`
- Package comparison in `references/latex_poster_packages.md`

## Support

For issues or questions:
- Review reference documentation in `references/`
- Check troubleshooting section above
- Run automated review: `./scripts/review_poster.sh`
- Use quality checklist: `assets/poster_quality_checklist.md`

## Version

LaTeX Poster Skill v1.0
Compatible with: beamerposter, tikzposter, baposter
Last updated: January 2025

### `references/ai_graphics_for_posters.md`

# AI Graphics for Posters

Full rules, worked examples, and the mandatory review gates for generating poster
visuals. `SKILL.md` carries the hard limits; this file carries the reasoning, the
per-graphic-type tables, and the complete before/after prompt examples.

### CRITICAL: Preventing Content Overflow

**⚠️ POSTERS MUST NOT HAVE TEXT OR CONTENT CUT OFF AT EDGES.**

**Common Overflow Problems:**
1. **Title/footer text extending beyond page boundaries**
2. **Too many sections crammed into available space**
3. **Figures placed too close to edges**
4. **Text blocks exceeding column widths**

**Prevention Rules:**

**1. Limit Content Sections (MAXIMUM 5-6 sections for A0):**
```
✅ GOOD - 5 sections with room to breathe:
   - Title/Header
   - Introduction/Problem
   - Methods
   - Results (1-2 key findings)
   - Conclusions

❌ BAD - 8+ sections crammed together:
   - Overview, Introduction, Background, Methods, 
   - Results 1, Results 2, Discussion, Conclusions, Future Work
```

**2. Set Safe Margins in LaTeX:**
```latex
% tikzposter - add generous margins
\documentclass[25pt, a0paper, portrait, margin=25mm]{tikzposter}

% baposter - ensure content doesn't touch edges
\begin{poster}{
  columns=3,
  colspacing=2em,           % Space between columns
  headerheight=0.1\textheight,  % Smaller header
  % Leave space at bottom
}
```

**3. Figure Sizing - Never 100% Width:**
```latex
% Leave margins around figures
\includegraphics[width=0.85\linewidth]{figure.png}  % NOT 1.0\linewidth
```

**4. Check for Overflow Before Printing:**
```bash
# Compile and check PDF at 100% zoom
pdflatex poster.tex

# Look for:
# - Text cut off at any edge
# - Content touching page boundaries  
# - Overfull hbox warnings in .log file
grep -i "overfull" poster.log
```

**5. Word Count Limits:**
- **A0 poster**: 300-800 words MAXIMUM
- **Per section**: 50-100 words maximum
- **If you have more content**: Cut it or make a handout

---

### CRITICAL: Poster-Size Font Requirements

**⚠️ ALL text within AI-generated visualizations MUST be poster-readable.**

When generating graphics for posters, you MUST include font size specifications in EVERY prompt. Poster graphics are viewed from 4-6 feet away, so text must be LARGE.

**⚠️ COMMON PROBLEM: Content Overflow and Density**

The #1 issue with AI-generated poster graphics is **TOO MUCH CONTENT**. This causes:
- Text overflow beyond boundaries
- Unreadable small fonts
- Cluttered, overwhelming visuals
- Poor white space usage

**SOLUTION: Generate SIMPLE graphics with MINIMAL content.**

**MANDATORY prompt requirements for EVERY poster graphic:**

```
POSTER FORMAT REQUIREMENTS (STRICTLY ENFORCE):
- ABSOLUTE MAXIMUM 3-4 elements per graphic (3 is ideal)
- ABSOLUTE MAXIMUM 10 words total in the entire graphic
- NO complex workflows with 5+ steps (split into 2-3 simple graphics instead)
- NO multi-level nested diagrams (flatten to single level)
- NO case studies with multiple sub-sections (one key point per case)
- ALL text GIANT BOLD (80pt+ for labels, 120pt+ for key numbers)
- High contrast ONLY (dark on white OR white on dark, NO gradients with text)
- MANDATORY 50% white space minimum (half the graphic should be empty)
- Thick lines only (5px+ minimum), large icons (200px+ minimum)
- ONE SINGLE MESSAGE per graphic (not 3 related messages)
```

**⚠️ BEFORE GENERATING: Review your prompt and count elements**
- If your description has 5+ items → STOP. Split into multiple graphics
- If your workflow has 5+ stages → STOP. Show only 3-4 high-level steps
- If your comparison has 4+ methods → STOP. Show only top 3 or Our vs Best Baseline

**Content limits per graphic type (STRICT):**
| Graphic Type | Max Elements | Max Words | Reject If | Good Example |
|--------------|--------------|-----------|-----------|--------------|
| Flowchart | **3-4 boxes MAX** | **8 words** | 5+ stages, nested steps | "DISCOVER → VALIDATE → APPROVE" (3 words) |
| Key findings | **3 items MAX** | **9 words** | 4+ metrics, paragraphs | "95% ACCURATE" "2X FASTER" "FDA READY" (6 words) |
| Comparison chart | **3 bars MAX** | **6 words** | 4+ methods, legend text | "OURS: 95%" "BEST: 85%" (4 words) |
| Case study | **1 case, 3 elements** | **6 words** | Multiple cases, substories | Logo + "18 MONTHS" + "to discovery" (2 words) |
| Timeline | **3-4 points MAX** | **8 words** | Year-by-year detail | "2020 START" "2022 TRIAL" "2024 APPROVED" (6 words) |

**Example - WRONG (7-stage workflow - TOO COMPLEX):**
```bash
# ❌ BAD - This creates tiny unreadable text like the drug discovery poster
python scripts/generate_schematic.py "Drug discovery workflow showing: Stage 1 Target Identification, Stage 2 Molecular Synthesis, Stage 3 Virtual Screening, Stage 4 AI Lead Optimization, Stage 5 Clinical Trial Design, Stage 6 FDA Approval. Include success metrics, timelines, and validation steps for each stage." -o figures/workflow.png
# Result: 7+ stages with tiny text, unreadable from 6 feet - POSTER FAILURE
```

**Example - CORRECT (simplified to 3 key stages):**
```bash
# ✅ GOOD - Same content, split into ONE simple high-level graphic
python scripts/generate_schematic.py "POSTER FORMAT for A0. ULTRA-SIMPLE 3-box workflow: 'DISCOVER' → 'VALIDATE' → 'APPROVE'. Each word in GIANT bold (120pt+). Thick arrows (10px). 60% white space. NO substeps, NO details. 3 words total. Readable from 10 feet." -o figures/workflow_overview.png
# Result: Clean, impactful, readable - can add detail graphics separately if needed
```

**Example - WRONG (complex case studies with multiple sections):**
```bash
# ❌ BAD - Creates cramped unreadable sections
python scripts/generate_schematic.py "Case studies: Insilico Medicine (drug candidate, discovery time, clinical trials), Recursion Pharma (platform, methodology, results), Exscientia (drug candidates, FDA status, timeline). Include company logos, metrics, and outcomes." -o figures/cases.png
# Result: 3 case studies with 4+ elements each = 12+ total elements, tiny text
```

**Example - CORRECT (one case study, one key metric):**
```bash
# ✅ GOOD - Show ONE case with ONE key number
python scripts/generate_schematic.py "POSTER FORMAT for A0. ONE case study card: Company logo (large), '18 MONTHS' in GIANT text (150pt), 'to discovery' below (60pt). 3 elements total: logo + number + caption. 50% white space. Readable from 10 feet." -o figures/case_single.png
# Result: Clear, readable, impactful. Make 3 separate graphics if you need 3 cases.
```

**Example - WRONG (key findings too complex):**
```bash
# BAD - too many items, too much detail
python scripts/generate_schematic.py "Key findings showing 8 metrics: accuracy 95%, precision 92%, recall 94%, F1 0.93, AUC 0.97, training time 2.3 hours, inference 50ms, model size 145MB with comparison to 5 baseline methods" -o figures/findings.png
# Result: Cramped graphic with tiny numbers
```

**Example - CORRECT (key findings simple):**
```bash
# GOOD - only 3 key items, giant numbers
python scripts/generate_schematic.py "POSTER FORMAT for A0. KEY FINDINGS with ONLY 3 large cards. Card 1: '95%' in GIANT text (120pt) with 'ACCURACY' below (48pt). Card 2: '2X' in GIANT text with 'FASTER' below. Card 3: checkmark icon with 'VALIDATED' in large text. 50% white space. High contrast colors. NO other text or details." -o figures/findings.png
# Result: Bold, readable impact statement
```

**Font size reference for poster prompts:**
| Element | Minimum Size | Prompt Keywords |
|---------|--------------|-----------------|
| Main numbers/metrics | 72pt+ | "huge", "very large", "giant", "poster-size" |
| Section titles | 60pt+ | "large bold", "prominent" |
| Labels/captions | 36pt+ | "readable from 6 feet", "clear labels" |
| Body text | 24pt+ | "poster-readable", "large text" |

**Always include in prompts:**
- "POSTER FORMAT" or "for A0 poster" or "readable from 6 feet"
- "VERY LARGE TEXT" or "huge bold fonts"
- Specific text that should appear (so it's baked into the image)
- "minimal text, maximum impact"
- "high contrast" for readability
- "generous margins" and "no text near edges"

---

### CRITICAL: AI-Generated Graphic Sizing

**⚠️ Each AI-generated graphic should focus on ONE concept with MINIMAL content.**

**Problem**: Generating complex diagrams with many elements leads to small text.

**Solution**: Generate SIMPLE graphics with FEW elements and LARGE text.

**Example - WRONG (too complex, text will be small):**
```bash
# BAD - too many elements in one graphic
python scripts/generate_schematic.py "Complete ML pipeline showing data collection, 
preprocessing with 5 steps, feature engineering with 8 techniques, model training 
with hyperparameter tuning, validation with cross-validation, and deployment with 
monitoring. Include all labels and descriptions." -o figures/pipeline.png
```

**Example - CORRECT (simple, focused, large text):**
```bash
# GOOD - split into multiple simple graphics with large text

# Graphic 1: High-level overview (3-4 elements max)
python scripts/generate_schematic.py "POSTER FORMAT for A0: Simple 4-step pipeline. 
Four large boxes: DATA → PROCESS → MODEL → RESULTS. 
GIANT labels (80pt+), thick arrows, lots of white space. 
Only 4 words total. Readable from 8 feet." -o figures/overview.png

# Graphic 2: Key result (1 metric highlighted)
python scripts/generate_schematic.py "POSTER FORMAT for A0: Single key metric display.
Giant '95%' text (150pt+) with 'ACCURACY' below (60pt+).
Checkmark icon. Minimal design, high contrast.
Readable from 10 feet." -o figures/accuracy.png
```

**Rules for AI-generated poster graphics:**
| Rule | Limit | Reason |
|------|-------|--------|
| **Elements per graphic** | 3-5 maximum | More elements = smaller text |
| **Words per graphic** | 10-15 maximum | Minimal text = larger fonts |
| **Flowchart steps** | 4-5 maximum | Keeps labels readable |
| **Chart categories** | 3-4 maximum | Prevents crowding |
| **Nested levels** | 1-2 maximum | Avoids complexity |

**Split complex content into multiple simple graphics:**
```
Instead of 1 complex diagram with 12 elements:
→ Create 3 simple diagrams with 4 elements each
→ Each graphic can have LARGER text
→ Arrange in poster with clear visual flow
```

---

### Step 0: MANDATORY Pre-Generation Review (DO THIS FIRST)

**⚠️ BEFORE generating ANY graphics, review your content plan:**

**For EACH planned graphic, ask these questions:**
1. **Element count**: Can I describe this in 3-4 items or less?
   - ❌ NO → Simplify or split into multiple graphics
   - ✅ YES → Continue

2. **Complexity check**: Is this a multi-stage workflow (5+ steps) or nested diagram?
   - ❌ YES → Flatten to 3-4 high-level steps only
   - ✅ NO → Continue

3. **Word count**: Can I describe all text in 10 words or less?
   - ❌ NO → Cut text, use single-word labels
   - ✅ YES → Continue

4. **Message clarity**: Does this graphic convey ONE clear message?
   - ❌ NO → Split into multiple focused graphics
   - ✅ YES → Continue to generation

**Common patterns that ALWAYS fail (reject these):**
- "Show stages 1 through 7..." → Split into high-level overview (3 stages) + detail graphics
- "Multiple case studies..." → One case per graphic
- "Timeline from 2015 to 2024 with annual milestones..." → Show only 3-4 key years
- "Comparison of 6 methods..." → Show only top 3 or Our method vs Best baseline
- "Architecture with all layers and connections..." → High-level only (3-4 components)

### Step 1: Plan Your Poster Elements

After passing the pre-generation review, identify visual elements needed:

1. **Title Block** - Stylized title with institutional branding (optional - can be LaTeX text)
2. **Introduction Graphic** - Conceptual overview (3 elements max)
3. **Methods Diagram** - High-level workflow (3-4 steps max)
4. **Results Figures** - Key findings (3 metrics max per figure, may need 2-3 separate figures)
5. **Conclusion Graphic** - Summary visual (3 takeaways max)
6. **Supplementary Icons** - Simple icons, QR codes, logos (minimal)

### Step 2: Generate Each Element (After Pre-Generation Review)

**⚠️ CRITICAL: Review Step 0 checklist before proceeding.**

Use the appropriate tool for each element type:

**For Schematics and Diagrams (scientific-schematics):**
```bash
# Create figures directory
mkdir -p figures

# Drug discovery workflow - HIGH-LEVEL ONLY, 3 stages
# BAD: "Stage 1: Target ID, Stage 2: Molecular Synthesis, Stage 3: Virtual Screening, Stage 4: AI Lead Opt..."
# GOOD: Collapse to 3 mega-stages
python scripts/generate_schematic.py "POSTER FORMAT for A0. ULTRA-SIMPLE 3-box workflow: 'DISCOVER' (120pt bold) → 'VALIDATE' (120pt bold) → 'APPROVE' (120pt bold). Thick arrows (10px). 60% white space. ONLY these 3 words. NO substeps. Readable from 12 feet." -o figures/workflow_simple.png

# System architecture - MAXIMUM 3 components
python scripts/generate_schematic.py "POSTER FORMAT for A0. ULTRA-SIMPLE 3-component stack: 'DATA' box (120pt) → 'AI MODEL' box (120pt) → 'PREDICTION' box (120pt). Thick vertical arrows. 60% white space. 3 words only. Readable from 12 feet." -o figures/architecture.png

# Timeline - ONLY 3 key milestones (not year-by-year)
# BAD: "2018, 2019, 2020, 2021, 2022, 2023, 2024 with events"
# GOOD: Only 3 breakthrough moments
python scripts/generate_schematic.py "POSTER FORMAT for A0. Timeline with ONLY 3 points: '2018' + icon, '2021' + icon, '2024' + icon. GIANT years (120pt). Large icons. 60% white space. NO connecting lines or details. Readable from 12 feet." -o figures/timeline.png

# Case study - ONE case, ONE key metric
# BAD: "3 case studies: Insilico (details), Recursion (details), Exscientia (details)"
# GOOD: ONE case with ONE number
python scripts/generate_schematic.py "POSTER FORMAT for A0. ONE case study: Large logo + '18 MONTHS' (150pt bold) + 'to discovery' (60pt). 3 elements total. 60% white space. Readable from 12 feet." -o figures/case1.png

# If you need 3 cases → make 3 separate simple graphics (not one complex graphic)
```

**For Stylized Blocks and Graphics (Nano Banana Pro):**
```bash
# Title block - SIMPLE
python scripts/generate_schematic.py "POSTER FORMAT for A0. Title block: 'ML FOR DRUG DISCOVERY' in HUGE bold text (120pt+). Dark blue background. ONE subtle icon. NO other text. 40% white space. Readable from 15 feet." -o figures/title_block.png

# Introduction visual - SIMPLE, 3 elements only
python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE problem visual with ONLY 3 icons: drug icon, arrow, target icon. ONE label per icon (80pt+). 50% white space. NO detailed text. Readable from 8 feet." -o figures/intro_visual.png

# Conclusion/summary - ONLY 3 items, GIANT numbers
python scripts/generate_schematic.py "POSTER FORMAT for A0. KEY FINDINGS with EXACTLY 3 cards only. Card 1: '95%' (150pt font) with 'ACCURACY' (60pt). Card 2: '2X' (150pt) with 'FASTER' (60pt). Card 3: checkmark icon with 'READY' (60pt). 50% white space. NO other text. Readable from 10 feet." -o figures/conclusions_graphic.png

# Background visual - SIMPLE, 3 icons only
python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE visual with ONLY 3 large icons in a row: problem icon → challenge icon → impact icon. ONE word label each (80pt+). 50% white space. NO detailed text. Readable from 8 feet." -o figures/background_visual.png
```

**For Data Visualizations - SIMPLE, 3 bars max:**
```bash
# SIMPLE chart with ONLY 3 bars, GIANT labels
python scripts/generate_schematic.py "POSTER FORMAT for A0. SIMPLE bar chart with ONLY 3 bars: BASELINE (70%), EXISTING (85%), OURS (95%). GIANT percentage labels ON the bars (100pt+). NO axis labels, NO legend, NO gridlines. Our bar highlighted in different color. 40% white space. Readable from 8 feet." -o figures/comparison_chart.png
```

### Step 2b: MANDATORY Post-Generation Review (Before Assembly)

**⚠️ CRITICAL: Review EVERY generated graphic before adding to poster.**

**For each generated figure, open at 25% zoom and check:**

1. **✅ PASS criteria (all must be true):**
   - Can read ALL text clearly at 25% zoom
   - Count elements: 3-4 or fewer
   - White space: 50%+ of image is empty
   - Simple enough to understand in 2 seconds
   - NOT a complex workflow with 5+ stages
   - NOT multiple nested sections

2. **❌ FAIL criteria (regenerate if ANY are true):**
   - Text is small or hard to read at 25% zoom → REGENERATE with "150pt+" fonts
   - More than 4 elements → REGENERATE with "ONLY 3 elements"
   - Less than 50% white space → REGENERATE with "60% white space"
   - Complex multi-stage workflow → SPLIT into 2-3 simple graphics
   - Multiple case studies cramped together → SPLIT into separate graphics
   - Takes more than 3 seconds to understand → SIMPLIFY and regenerate

**Common failures and fixes:**
- "7-stage workflow with tiny text" → Regenerate as "3 high-level stages only"
- "3 case studies in one graphic" → Generate 3 separate simple graphics
- "Timeline with 8 years" → Regenerate with "ONLY 3 key milestones"
- "Comparison of 5 methods" → Regenerate with "ONLY Our method vs Best baseline (2 bars)"

**DO NOT PROCEED to assembly if ANY graphic fails the checks above.**

### Step 3: Assemble in LaTeX Template

After all figures pass the post-generation review, include them in your poster template:

**tikzposter example:**
```latex
\documentclass[25pt, a0paper, portrait]{tikzposter}

\begin{document}

\maketitle

\begin{columns}
\column{0.5}

\block{Introduction}{
  \centering
  \includegraphics[width=0.85\linewidth]{figures/intro_visual.png}
  
  \vspace{0.5em}
  Brief context text here (2-3 sentences max).
}

\block{Methods}{
  \centering
  \includegraphics[width=0.9\linewidth]{figures/methods_flowchart.png}
}

\column{0.5}

\block{Results}{
  \begin{minipage}{0.48\linewidth}
    \centering
    \includegraphics[width=\linewidth]{figures/result_1.png}
  \end{minipage}
  \hfill
  \begin{minipage}{0.48\linewidth}
    \centering
    \includegraphics[width=\linewidth]{figures/result_2.png}
  \end{minipage}
  
  \vspace{0.5em}
  Key findings in 3-4 bullet points.
}

\block{Conclusions}{
  \centering
  \includegraphics[width=0.8\linewidth]{figures/conclusions_graphic.png}
}

\end{columns}

\end{document}
```

**baposter example:**
```latex
\headerbox{Methods}{name=methods,column=0,row=0}{
  \centering
  \includegraphics[width=0.95\linewidth]{figures/methods_flowchart.png}
}

\headerbox{Results}{name=results,column=1,row=0}{
  \includegraphics[width=\linewidth]{figures/comparison_chart.png}
  \vspace{0.3em}
  
  Key finding: Our method achieves 92% accuracy.
}
```

### Example: Complete Poster Generation Workflow

**Full workflow with ALL quality checks:**

```bash
# STEP 0: Pre-Generation Review (MANDATORY)
# Content plan: Drug discovery poster
# - Workflow: 7 stages → ❌ TOO MANY → Reduce to 3 mega-stages ✅
# - 3 case studies → ❌ TOO MANY → One case per graphic (make 3 graphics) ✅
# - Timeline 2018-2024 → ❌ TOO DETAILED → Only 3 key years ✅

# STEP 1: Create figures directory
mkdir -p figures

# STEP 2: Generate ULTRA-SIMPLE graphics with strict limits

# Workflow - HIGH-LEVEL ONLY (collapsed from 7 stages to 3)
python scripts/generate_schematic.py "POSTER FORMAT for A0. ULTRA-SIMPLE 3-box workflow: 'DISCOVER' → 'VALIDATE' → 'APPROVE'. Each word 120pt+ bold. Thick arrows (10px). 60% white space. ONLY 3 words total. Readable from 12 feet." -o figures/workflow.png

# Case study 1 - ONE case, ONE metric (will make 3 separate graphics)
python scripts/generate_schematic.py "POSTER FORMAT for A0. ONE case: Company logo + '18 MONTHS' (150pt bold) + 'to drug discovery' (60pt). 3 elements only. 60% white space. Readable from 12 feet." -o figures/case1.png

python scripts/generate_schematic.py "POSTER FORMAT for A0. ONE case: Company logo + '95% SUCCESS' (150pt bold) + 'in trials' (60pt). 3 elements only. 60% white space." -o figures/case2.png

python scripts/generate_schematic.py "POSTER FORMAT for A0. ONE case: Company logo + 'FDA APPROVED' (150pt bold) + '2024' (60pt). 3 elements only. 60% white space." -o figures/case3.png

# Timeline - ONLY 3 key years (not 7 years)
python scripts/generate_schematic.py "POSTER FORMAT for A0. ONLY 3 years: '2018' (150pt) + icon, '2021' (150pt) + icon, '2024' (150pt) + icon. Large icons. 60% white space. NO lines or details. Readable from 12 feet." -o figures/timeline.png

# Results - ONLY 2 bars (our method vs best baseline, not 5 methods)
python scripts/generate_schematic.py "POSTER FORMAT for A0. TWO bars only: 'BASELINE 70%' and 'OURS 95%' (highlighted). GIANT percentages (150pt) ON bars. NO axis, NO legend. 60% white space. Readable from 12 feet." -o figures/results.png

# STEP 2b: Post-Generation Review (MANDATORY)
# Open each figure at 25% zoom:
# ✅ workflow.png: 3 elements, text readable, 60% white - PASS
# ✅ case1.png: 3 elements, giant numbers, clean - PASS
# ✅ case2.png: 3 elements, giant numbers, clean - PASS  
# ✅ case3.png: 3 elements, giant numbers, clean - PASS
# ✅ timeline.png: 3 elements, readable, simple - PASS
# ✅ results.png: 2 bars, giant percentages, clear - PASS
# ALL PASS → Proceed to assembly

# STEP 3: Compile LaTeX poster
pdflatex poster.tex

# STEP 4: PDF Overflow Check (see Section 11)
grep "Overfull" poster.log
# Open at 100% and check all 4 edges
```

**If ANY graphic fails Step 2b review:**
- Too many elements → Regenerate with "ONLY 3 elements"
- Small text → Regenerate with "150pt+" or "GIANT BOLD (150pt+)"
- Cluttered → Regenerate with "60% white space" and "ULTRA-SIMPLE"
- Complex workflow → SPLIT into multiple simple 3-element graphics

### Visual Element Guidelines

**⚠️ CRITICAL: Each graphic must have ONE message and MAXIMUM 3-4 elements.**

**ABSOLUTE LIMITS - These are NOT guidelines, these are HARD LIMITS:**
- **MAXIMUM 3-4 elements** per graphic (3 is ideal)
- **MAXIMUM 10 words** total per graphic
- **MINIMUM 50% white space** (60% is better)
- **MINIMUM 120pt** for key numbers/metrics
- **MINIMUM 80pt** for labels

**For each poster section - STRICT requirements:**

| Section | Max Elements | Max Words | Example Prompt (REQUIRED PATTERN) |
|---------|--------------|-----------|-------------------------------------|
| **Introduction** | 3 icons | 6 words | "POSTER FORMAT for A0: ULTRA-SIMPLE 3 icons: [icon1] [icon2] [icon3]. ONE WORD labels (100pt bold). 60% white space. 3 words total." |
| **Methods** | 3 boxes | 6 words | "POSTER FORMAT for A0: ULTRA-SIMPLE 3-box workflow: 'STEP1' → 'STEP2' → 'STEP3'. GIANT labels (120pt+). 60% white space. 3 words only." |
| **Results** | 2-3 bars | 6 words | "POSTER FORMAT for A0: TWO bars: 'BASELINE 70%' 'OURS 95%'. GIANT percentages (150pt+) ON bars. NO axis. 60% white space." |
| **Conclusions** | 3 cards | 9 words | "POSTER FORMAT for A0: THREE cards: '95%' (150pt) 'ACCURATE', '2X' (150pt) 'FASTER', checkmark 'READY'. 60% white space." |
| **Case Study** | 3 elements | 5 words | "POSTER FORMAT for A0: ONE case: logo + '18 MONTHS' (150pt) + 'to discovery' (60pt). 60% white space." |
| **Timeline** | 3 points | 3 words | "POSTER FORMAT for A0: THREE years only: '2018' '2021' '2024' (150pt each). Large icons. 60% white space. NO details." |

**MANDATORY prompt elements (ALL required, NO exceptions):**
1. **"POSTER FORMAT for A0"** - MUST be first
2. **"ULTRA-SIMPLE"** or **"ONLY X elements"** - content limit
3. **"GIANT (120pt+)"** or specific font sizes - readability
4. **"60% white space"** - mandatory breathing room
5. **"readable from 10-12 feet"** - viewing distance
6. **Exact count** of words/elements - "3 words total" or "ONLY 3 icons"

**PATTERNS THAT ALWAYS FAIL (REJECT IMMEDIATELY):**
- ❌ "7-stage drug discovery workflow" → Split to "3 mega-stages"
- ❌ "Timeline from 2015-2024 with annual updates" → "ONLY 3 key years"
- ❌ "3 case studies with details" → Make 3 separate simple graphics
- ❌ "Comparison of 5 methods with metrics" → "ONLY 2: ours vs best"
- ❌ "Complete architecture showing all layers" → "3 components only"
- ❌ "Show stages 1,2,3,4,5,6" → "3 high-level stages"

**PATTERNS THAT WORK:**
- ✅ "3 mega-stages collapsed from 7" → Proper simplification
- ✅ "ONE case with ONE metric" → Will make multiple if needed
- ✅ "ONLY 3 milestones" → Selective, focused
- ✅ "2 bars: ours vs baseline" → Direct comparison
- ✅ "3-component high-level view" → Appropriately simplified

---

### `references/compilation_and_quality_control.md`

# Compilation and Quality Control

Compilation commands and engines, then the full pre-print QC procedure: page-size
verification, overflow detection, reduced-scale test prints, font embedding, image
DPI, file size, and log-warning triage.

### 10. Compilation and Output

Generate high-quality PDF output for printing or digital display:

**Compilation Commands**:
```bash
# Basic compilation
pdflatex poster.tex

# With bibliography
pdflatex poster.tex
bibtex poster
pdflatex poster.tex
pdflatex poster.tex

# For beamer-based posters
lualatex poster.tex  # Better font support
xelatex poster.tex   # Unicode and modern fonts
```

**Ensuring Full Page Coverage**:

Posters should use the entire page without excessive margins. Configure packages correctly:

**beamerposter - Full Page Setup**:
```latex
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}

% Remove default beamer margins
\setbeamersize{text margin left=0mm, text margin right=0mm}

% Use geometry for precise control
\usepackage[margin=10mm]{geometry}  % 10mm margins all around

% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Remove footline and headline if not needed
\setbeamertemplate{footline}{}
\setbeamertemplate{headline}{}
```

**tikzposter - Full Page Setup**:
```latex
\documentclass[
  25pt,                      % Font scaling
  a0paper,                   % Paper size
  portrait,                  % Orientation
  margin=10mm,               % Outer margins (minimal)
  innermargin=15mm,          % Space inside blocks
  blockverticalspace=15mm,   % Space between blocks
  colspace=15mm,             % Space between columns
  subcolspace=8mm            % Space between subcolumns
]{tikzposter}

% This ensures content fills the page
```

**baposter - Full Page Setup**:
```latex
\documentclass[a0paper,portrait,fontscale=0.285]{baposter}

\begin{poster}{
  grid=false,
  columns=3,
  colspacing=1.5em,          % Space between columns
  eyecatcher=true,
  background=plain,
  bgColorOne=white,
  borderColor=blue!50,
  headerheight=0.12\textheight,  % 12% for header
  textborder=roundedleft,
  headerborder=closed,
  boxheaderheight=2em        % Consistent box header heights
}
% Content here
\end{poster}
```

**Common Issues and Fixes**:

**Problem**: Large white margins around poster
```latex
% Fix for beamerposter
\setbeamersize{text margin left=5mm, text margin right=5mm}

% Fix for tikzposter
\documentclass[..., margin=5mm, innermargin=10mm]{tikzposter}

% Fix for baposter - adjust in document class
\documentclass[a0paper, margin=5mm]{baposter}
```

**Problem**: Content doesn't fill vertical space
```latex
% Use \vfill between sections to distribute space
\block{Introduction}{...}
\vfill
\block{Methods}{...}
\vfill
\block{Results}{...}

% Or manually adjust block spacing
\vspace{1cm}  % Add space between specific blocks
```

**Problem**: Poster extends beyond page boundaries
```latex
% Check total width calculation
% For 3 columns with spacing:
% Total = 3×columnwidth + 2×colspace + 2×margins
% Ensure this equals \paperwidth

% Debug by adding visible page boundary
\usepackage{eso-pic}
\AddToShipoutPictureBG{
  \AtPageLowerLeft{
    \put(0,0){\framebox(\LenToUnit{\paperwidth},\LenToUnit{\paperheight}){}}
  }
}
```

**Print Preparation**:
- Generate PDF/X-1a for professional printing
- Embed all fonts
- Convert colors to CMYK if required
- Check resolution of all images (minimum 300 DPI)
- Add bleed area if required by printer (usually 3-5mm)
- Verify page size matches requirements exactly

**Digital Display**:
- RGB color space for screen display
- Optimize file size for email/web
- Test readability on different screens

### 11. PDF Review and Quality Control

**CRITICAL**: Always review the generated PDF before printing or presenting. Use this systematic checklist:

**Step 1: Page Size Verification**
```bash
# Check PDF dimensions (should match poster size exactly)
pdfinfo poster.pdf | grep "Page size"

# Expected outputs:
# A0: 2384 x 3370 points (841 x 1189 mm)
# 36x48": 2592 x 3456 points
# A1: 1684 x 2384 points (594 x 841 mm)
```

**Step 2: OVERFLOW CHECK (CRITICAL) - DO THIS IMMEDIATELY AFTER COMPILATION**

**⚠️ THIS IS THE #1 CAUSE OF POSTER FAILURES. Check BEFORE proceeding.**

**Step 2a: Check LaTeX Log File**
```bash
# Check for overflow warnings (these are ERRORS, not suggestions)
grep -i "overfull\|underfull\|badbox" poster.log

# ANY "Overfull" warning = content is cut off or extending beyond boundaries
# FIX ALL OF THESE before proceeding
```

**Common overflow warnings and what they mean:**
- `Overfull \hbox (15.2pt too wide)` → Text or graphic is 15.2pt wider than column
- `Overfull \vbox (23.5pt too high)` → Content is 23.5pt taller than available space
- `Badbox` → LaTeX struggling to fit content within boundaries

**Step 2b: Visual Edge Inspection (100% zoom in PDF viewer)**

**Check ALL FOUR EDGES systematically:**

1. **TOP EDGE:**
   - [ ] Title completely visible (not cut off)
   - [ ] Author names fully visible
   - [ ] No graphics touching top margin
   - [ ] Header content within safe zone

2. **BOTTOM EDGE:**
   - [ ] References fully visible (not cut off)
   - [ ] Acknowledgments complete
   - [ ] Contact info readable
   - [ ] No graphics cut off at bottom

3. **LEFT EDGE:**
   - [ ] No text touching left margin
   - [ ] All bullet points fully visible
   - [ ] Graphics have left margin (not bleeding off)
   - [ ] Column content within bounds

4. **RIGHT EDGE:**
   - [ ] No text extending beyond right margin
   - [ ] Graphics not cut off on right
   - [ ] Column content stays within bounds
   - [ ] QR codes fully visible

5. **BETWEEN COLUMNS:**
   - [ ] Content stays within individual columns
   - [ ] No text bleeding into adjacent columns
   - [ ] Figures respect column boundaries

**If ANY check fails, you have overflow. FIX IMMEDIATELY before continuing:**

**Fix hierarchy (try in order):**
1. **Check AI-generated graphics first:**
   - Are they too complex (5+ elements)? → Regenerate simpler
   - Do they have tiny text? → Regenerate with "150pt+" fonts
   - Are there too many? → Reduce number of figures

2. **Reduce sections:**
   - More than 5-6 sections? → Combine or remove
   - Example: Merge "Discussion" into "Conclusions"

3. **Cut text content:**
   - More than 800 words total? → Cut to 300-500
   - More than 100 words per section? → Cut to 50-80

4. **Adjust figure sizing:**
   - Using `width=\linewidth`? → Change to `width=0.85\linewidth`
   - Using `width=1.0\columnwidth`? → Change to `width=0.9\columnwidth`

5. **Increase margins (last resort):**
   ```latex
   \documentclass[25pt, a0paper, portrait, margin=25mm]{tikzposter}
   ```

**DO NOT proceed to Step 3 if ANY overflow exists.**

**Step 3: Visual Inspection Checklist**

Open PDF at 100% zoom and check:

**Layout and Spacing**:
- [ ] Content fills entire page (no large white margins)
- [ ] Consistent spacing between columns
- [ ] Consistent spacing between blocks/sections
- [ ] All elements aligned properly (use ruler tool)
- [ ] No overlapping text or figures
- [ ] White space evenly distributed

**Typography**:
- [ ] Title clearly visible and large (72pt+)
- [ ] Section headers readable (48-72pt)
- [ ] Body text readable at 100% zoom (24-36pt minimum)
- [ ] No text cutoff or running off edges
- [ ] Consistent font usage throughout
- [ ] All special characters render correctly (symbols, Greek letters)

**Visual Elements**:
- [ ] All figures display correctly
- [ ] No pixelated or blurry images
- [ ] Figure captions present and readable
- [ ] Colors render as expected (not washed out or too dark)
- [ ] Logos display clearly
- [ ] QR codes visible and scannable

**Content Completeness**:
- [ ] Title and authors complete
- [ ] All sections present (Intro, Methods, Results, Conclusions)
- [ ] References included
- [ ] Contact information visible
- [ ] Acknowledgments (if applicable)
- [ ] No placeholder text remaining (Lorem ipsum, TODO, etc.)

**Technical Quality**:
- [ ] No LaTeX compilation warnings in important areas
- [ ] All citations resolved (no [?] marks)
- [ ] All cross-references working
- [ ] Page boundaries correct (no content cut off)

**Step 4: Reduced-Scale Print Test**

**Essential Pre-Printing Test**:
```bash
# Create reduced-size test print (25% of final size)
# This simulates viewing full poster from ~8-10 feet

# For A0 poster, print on A4 paper (24.7% scale)
# For 36x48" poster, print on letter paper (~25% scale)
```

**Print Test Checklist**:
- [ ] Title readable from 6 feet away
- [ ] Section headers readable from 4 feet away
- [ ] Body text readable from 2 feet away
- [ ] Figures clear and understandable
- [ ] Colors printed accurately
- [ ] No obvious design flaws

**Step 5: Digital Quality Checks**

**Font Embedding Verification**:
```bash
# Check that all fonts are embedded (required for printing)
pdffonts poster.pdf

# All fonts should show "yes" in "emb" column
# If any show "no", recompile with:
pdflatex -dEmbedAllFonts=true poster.tex
```

**Image Resolution Check**:
```bash
# Extract image information
pdfimages -list poster.pdf

# Check that all images are at least 300 DPI
# Formula: DPI = pixels / (inches in poster)
# For A0 width (33.1"): 300 DPI = 9930 pixels minimum
```

**File Size Optimization**:
```bash
# For email/web, compress if needed (>50MB)
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=poster_compressed.pdf poster.pdf

# For printing, keep original (no compression)
```

**Step 6: Accessibility Check**

**Color Contrast Verification**:
- [ ] Text-background contrast ratio ≥ 4.5:1 (WCAG AA)
- [ ] Important elements contrast ratio ≥ 7:1 (WCAG AAA)
- Test online: https://webaim.org/resources/contrastchecker/

**Color Blindness Simulation**:
- [ ] View PDF through color blindness simulator
- [ ] Information not lost with red-green simulation
- [ ] Use Coblis (color-blindness.com) or similar tool

**Step 7: Content Proofreading**

**Systematic Review**:
- [ ] Spell-check all text
- [ ] Verify all author names and affiliations
- [ ] Check all numbers and statistics for accuracy
- [ ] Confirm all citations are correct
- [ ] Review figure labels and captions
- [ ] Check for typos in headers and titles

**Peer Review**:
- [ ] Ask colleague to review poster
- [ ] 30-second test: Can they identify main message?
- [ ] 5-minute review: Do they understand conclusions?
- [ ] Note any confusing elements

**Step 8: Technical Validation**

**LaTeX Compilation Log Review**:
```bash
# Check for warnings in .log file
grep -i "warning\|error\|overfull\|underfull" poster.log

# Common issues to fix:
# - Overfull hbox: Text extending beyond margins
# - Underfull hbox: Excessive spacing
# - Missing references: Citations not resolved
# - Missing figures: Image files not found
```

**Fix Common Warnings**:
```latex
% Overfull hbox (text too wide)
\usepackage{microtype}  % Better spacing
\sloppy  % Allow slightly looser spacing
\hyphenation{long-word}  % Manual hyphenation

% Missing fonts
\usepackage[T1]{fontenc}  % Better font encoding

% Image not found
% Ensure paths are correct and files exist
\graphicspath{{./figures/}{./images/}}
```

**Step 9: Final Pre-Print Checklist**

**Before Sending to Printer**:
- [ ] PDF size exactly matches requirements (check with pdfinfo)
- [ ] All fonts embedded (check with pdffonts)
- [ ] Color mode correct (RGB for screen, CMYK for print if required)
- [ ] Bleed area added if required (usually 3-5mm)
- [ ] Crop marks visible if required
- [ ] Test print completed and reviewed
- [ ] File naming clear: [LastName]_[Conference]_Poster.pdf
- [ ] Backup copy saved

**Printing Specifications to Confirm**:
- [ ] Paper type (matte vs. glossy)
- [ ] Printing method (inkjet, large format, fabric)
- [ ] Color profile (provided to printer if required)
- [ ] Delivery deadline and shipping address
- [ ] Tube or flat packaging preference

**Digital Presentation Checklist**:
- [ ] PDF size optimized (<10MB for email)
- [ ] Tested on multiple PDF viewers (Adobe, Preview, etc.)
- [ ] Displays correctly on different screens
- [ ] QR codes tested and functional
- [ ] Alternative formats prepared (PNG for social media)

**Review Script** (Available in `scripts/review_poster.sh`):
```bash
#!/bin/bash
# Automated poster PDF review script

echo "Poster PDF Quality Check"
echo "======================="

# Check file exists
if [ ! -f "$1" ]; then
    echo "Error: File not found"
    exit 1
fi

echo "File: $1"
echo ""

# Check page size
echo "1. Page Dimensions:"
pdfinfo "$1" | grep "Page size"
echo ""

# Check fonts
echo "2. Font Embedding:"
pdffonts "$1" | head -20
echo ""

# Check file size
echo "3. File Size:"
ls -lh "$1" | awk '{print $5}'
echo ""

# Count pages (should be 1 for poster)
echo "4. Page Count:"
pdfinfo "$1" | grep "Pages"
echo ""

echo "Manual checks required:"
echo "- Visual inspection at 100% zoom"
echo "- Reduced-scale print test (25%)"
echo "- Color contrast verification"
echo "- Proofreading for typos"
```

**Common PDF Issues and Solutions**:

| Issue | Cause | Solution |
|-------|-------|----------|
| Large white margins | Incorrect margin settings | Reduce margin in documentclass |
| Content cut off | Exceeds page boundaries | Check total width/height calculations |
| Blurry images | Low resolution (<300 DPI) | Replace with higher resolution images |
| Missing fonts | Fonts not embedded | Compile with -dEmbedAllFonts=true |
| Wrong page size | Incorrect paper size setting | Verify documentclass paper size |
| Colors look wrong | RGB vs CMYK mismatch | Convert color space for print |
| File too large (>50MB) | Uncompressed images | Optimize images or compress PDF |
| QR codes don't work | Too small or low resolution | Minimum 2×2cm, high contrast |

### `references/latex_poster_packages.md`

# LaTeX Poster Packages: Comprehensive Comparison

## Overview

Three major LaTeX packages dominate research poster creation: beamerposter, tikzposter, and baposter. Each has distinct strengths, syntax, and use cases. This guide provides detailed comparisons and practical examples.

## Package Comparison Matrix

| Feature | beamerposter | tikzposter | baposter |
|---------|--------------|------------|----------|
| **Learning Curve** | Easy (if familiar with Beamer) | Moderate | Moderate |
| **Flexibility** | Moderate | High | Moderate-High |
| **Default Aesthetics** | Traditional/Academic | Modern/Colorful | Professional/Clean |
| **Theme Support** | Extensive (Beamer themes) | Built-in + Custom | Limited built-in |
| **Customization** | Moderate effort | Easy with TikZ | Structured approach |
| **Layout System** | Frame-based | Block-based | Box-based with grid |
| **Multi-column** | Manual | Automatic | Automatic |
| **Graphics Integration** | Standard includegraphics | TikZ + includegraphics | Standard + advanced |
| **Community Support** | Large (Beamer community) | Growing | Smaller |
| **Best For** | Traditional academic, institutional branding | Creative designs, custom graphics | Structured multi-column layouts |
| **File Size** | Small | Medium-Large (TikZ overhead) | Medium |
| **Compilation Speed** | Fast | Slower (TikZ processing) | Fast-Medium |

## 1. beamerposter

### Overview

beamerposter extends the popular Beamer presentation class for poster-sized documents. It inherits all Beamer functionality, themes, and customization options.

### Advantages

- **Familiar syntax**: If you know Beamer, you know beamerposter
- **Extensive themes**: Access to all Beamer themes and color schemes
- **Institutional branding**: Easy to match university templates
- **Stable and mature**: Well-tested, extensive documentation
- **Block structure**: Clear organizational units
- **Good for traditional posters**: Academic conferences, thesis defenses

### Disadvantages

- **Less flexible layouts**: Column-based system can be restrictive
- **Manual positioning**: Requires careful spacing adjustments
- **Traditional aesthetics**: Can look dated compared to modern designs
- **Limited built-in styling**: Requires theme customization for unique looks

### Basic Template

```latex
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}
\usetheme{Berlin}
\usecolortheme{beaver}

% Configure fonts
\setbeamerfont{title}{size=\VeryHuge,series=\bfseries}
\setbeamerfont{author}{size=\Large}
\setbeamerfont{block title}{size=\large,series=\bfseries}

\title{Your Research Title}
\author{Author Names}
\institute{Institution}

\begin{document}
\begin{frame}[t]
  
  % Title block
  \begin{block}{}
    \maketitle
  \end{block}
  
  \begin{columns}[t]
    \begin{column}{.45\linewidth}
      
      \begin{block}{Introduction}
        Your introduction text here...
      \end{block}
      
      \begin{block}{Methods}
        Your methods text here...
      \end{block}
      
    \end{column}
    
    \begin{column}{.45\linewidth}
      
      \begin{block}{Results}
        Your results text here...
        \includegraphics[width=\linewidth]{figure.pdf}
      \end{block}
      
      \begin{block}{Conclusions}
        Your conclusions here...
      \end{block}
      
    \end{column}
  \end{columns}
  
\end{frame}
\end{document}
```

### Popular Themes

```latex
% Traditional academic
\usetheme{Berlin}
\usecolortheme{beaver}

% Modern minimal
\usetheme{Madrid}
\usecolortheme{whale}

% Blue professional
\usetheme{Singapore}
\usecolortheme{dolphin}

% Dark theme
\usetheme{Warsaw}
\usecolortheme{seahorse}
```

### Custom Colors

```latex
% Define custom colors
\definecolor{primarycolor}{RGB}{0,51,102}      % Dark blue
\definecolor{secondarycolor}{RGB}{204,0,0}     % Red
\definecolor{accentcolor}{RGB}{255,204,0}      % Gold

% Apply to beamer elements
\setbeamercolor{structure}{fg=primarycolor}
\setbeamercolor{block title}{bg=primarycolor,fg=white}
\setbeamercolor{block body}{bg=primarycolor!10,fg=black}
```

### Advanced Customization

```latex
% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Custom title formatting
\setbeamertemplate{title page}{
  \begin{center}
    {\usebeamerfont{title}\usebeamercolor[fg]{title}\inserttitle}\\[1cm]
    {\usebeamerfont{author}\insertauthor}\\[0.5cm]
    {\usebeamerfont{institute}\insertinstitute}
  \end{center}
}

% Custom block style
\setbeamertemplate{block begin}{
  \par\vskip\medskipamount
  \begin{beamercolorbox}[colsep*=.75ex,rounded=true]{block title}
    \usebeamerfont*{block title}\insertblocktitle
  \end{beamercolorbox}
  {\parskip0pt\par}
  \usebeamerfont{block body}
  \begin{beamercolorbox}[colsep*=.75ex,vmode,rounded=true]{block body}
}
```

### Three-Column Layout

```latex
\begin{columns}[t]
  \begin{column}{.3\linewidth}
    % Left column content
  \end{column}
  \begin{column}{.3\linewidth}
    % Middle column content
  \end{column}
  \begin{column}{.3\linewidth}
    % Right column content
  \end{column}
\end{columns}
```

## 2. tikzposter

### Overview

tikzposter is built on the powerful TikZ graphics package, offering modern designs with extensive customization through TikZ commands.

### Advantages

- **Modern aesthetics**: Contemporary, colorful designs out-of-the-box
- **Flexible block placement**: Easy positioning anywhere on poster
- **Beautiful themes**: Multiple professionally designed themes included
- **TikZ integration**: Seamless graphics and custom drawings
- **Color customization**: Easy to create custom color palettes
- **Automatic spacing**: Intelligent block spacing and alignment

### Disadvantages

- **Compilation time**: TikZ processing can be slow for large posters
- **File size**: PDFs can be larger due to TikZ elements
- **Learning curve**: TikZ syntax can be complex for advanced customization
- **Less institutional theme support**: Requires more work to match branding

### Basic Template

```latex
\documentclass[25pt, a0paper, portrait, margin=0mm, innermargin=15mm,
     blockverticalspace=15mm, colspace=15mm, subcolspace=8mm]{tikzposter}

\title{Your Research Title}
\author{Author Names}
\institute{Institution}

% Choose theme and color style
\usetheme{Rays}
\usecolorstyle{Denmark}

\begin{document}

\maketitle

% First column
\begin{columns}
  \column{0.5}
  
  \block{Introduction}{
    Your introduction text here...
  }
  
  \block{Methods}{
    Your methods text here...
  }
  
  % Second column
  \column{0.5}
  
  \block{Results}{
    Your results text here...
    \begin{tikzfigure}
      \includegraphics[width=0.9\linewidth]{figure.pdf}
    \end{tikzfigure}
  }
  
  \block{Conclusions}{
    Your conclusions here...
  }
  
\end{columns}

\end{document}
```

### Available Themes

```latex
% Modern with radiating background
\usetheme{Rays}

% Clean with decorative wave
\usetheme{Wave}

% Minimal with envelope corners
\usetheme{Envelope}

% Traditional academic
\usetheme{Basic}

% Board-style with texture
\usetheme{Board}

% Clean minimal
\usetheme{Simple}

% Professional with lines
\usetheme{Default}

% Autumn color scheme
\usetheme{Autumn}

% Desert color palette
\usetheme{Desert}
```

### Color Styles

```latex
% Professional blue
\usecolorstyle{Denmark}

% Warm colors
\usecolorstyle{Australia}

% Cool tones
\usecolorstyle{Sweden}

% Earth tones
\usecolorstyle{Britain}

% Default color scheme
\usecolorstyle{Default}
```

### Custom Color Definition

```latex
\definecolorstyle{CustomStyle}{
  \definecolor{colorOne}{RGB}{0,51,102}      % Dark blue
  \definecolor{colorTwo}{RGB}{255,204,0}     % Gold
  \definecolor{colorThree}{RGB}{204,0,0}     % Red
}{
  % Background Colors
  \colorlet{backgroundcolor}{white}
  \colorlet{framecolor}{colorOne}
  % Title Colors
  \colorlet{titlefgcolor}{white}
  \colorlet{titlebgcolor}{colorOne}
  % Block Colors
  \colorlet{blocktitlebgcolor}{colorOne}
  \colorlet{blocktitlefgcolor}{white}
  \colorlet{blockbodybgcolor}{white}
  \colorlet{blockbodyfgcolor}{black}
  % Innerblock Colors
  \colorlet{innerblocktitlebgcolor}{colorTwo}
  \colorlet{innerblocktitlefgcolor}{black}
  \colorlet{innerblockbodybgcolor}{colorTwo!10}
  \colorlet{innerblockbodyfgcolor}{black}
  % Note colors
  \colorlet{notefgcolor}{black}
  \colorlet{notebgcolor}{colorThree!20}
}

\usecolorstyle{CustomStyle}
```

### Block Placement and Sizing

```latex
% Full-width block
\block{Title}{Content}

% Specify width
\block[width=0.8\linewidth]{Title}{Content}

% Position manually
\block[x=10, y=50, width=30]{Title}{Content}

% Inner blocks (nested, different styling)
\block{Outer Title}{
  \innerblock{Inner Title}{
    Highlighted content
  }
}

% Note blocks (for emphasis)
\note[width=0.4\linewidth]{
  Important note text
}
```

### Advanced Features

```latex
% QR codes with tikzposter styling
\block{Scan for More}{
  \begin{center}
    \qrcode[height=5cm]{https://github.com/project}\\
    \vspace{0.5cm}
    Visit our GitHub repository
  \end{center}
}

% Multi-column within block
\block{Results}{
  \begin{tabular}{cc}
    \includegraphics[width=0.45\linewidth]{fig1.pdf} &
    \includegraphics[width=0.45\linewidth]{fig2.pdf}
  \end{tabular}
}

% Custom TikZ graphics
\block{Methodology}{
  \begin{tikzpicture}
    \node[draw, rectangle, fill=blue!20] (A) {Step 1};
    \node[draw, rectangle, fill=green!20, right=of A] (B) {Step 2};
    \draw[->, thick] (A) -- (B);
  \end{tikzpicture}
}
```

## 3. baposter

### Overview

baposter (Box Area Poster) uses a box-based layout system with automatic positioning and spacing. Excellent for structured, professional multi-column layouts.

### Advantages

- **Automatic layout**: Intelligent box positioning and spacing
- **Professional defaults**: Clean, polished appearance out-of-the-box
- **Multi-column excellence**: Best-in-class column-based layouts
- **Header/footer boxes**: Easy institutional branding
- **Consistent spacing**: Automatic vertical and horizontal alignment
- **Print-ready**: Excellent CMYK support

### Disadvantages

- **Less flexible**: Box-based system can be constraining
- **Fewer themes**: Limited built-in theme options
- **Learning curve**: Unique syntax requires time to master
- **Less active development**: Smaller community compared to others

### Basic Template

```latex
\documentclass[a0paper,portrait]{baposter}

\usepackage{graphicx}
\usepackage{multicol}

\begin{document}

\begin{poster}{
  % Options
  grid=false,
  columns=3,
  colspacing=1em,
  bgColorOne=white,
  bgColorTwo=white,
  borderColor=blue!50,
  headerColorOne=blue!80,
  headerColorTwo=blue!70,
  headerFontColor=white,
  boxColorOne=white,
  boxColorTwo=blue!10,
  textborder=roundedleft,
  eyecatcher=true,
  headerborder=open,
  headerheight=0.12\textheight,
  headershape=roundedright,
  headershade=plain,
  headerfont=\Large\sf\bf,
  linewidth=2pt
}
% Eye Catcher (Logo)
{
  \includegraphics[height=6em]{logo.pdf}
}
% Title
{
  Your Research Title
}
% Authors
{
  Author Names\\
  Institution Name
}
% University Logo
{
  \includegraphics[height=6em]{university-logo.pdf}
}

% First column boxes
\headerbox{Introduction}{name=intro,column=0,row=0}{
  Your introduction text here...
}

\headerbox{Methods}{name=methods,column=0,below=intro}{
  Your methods text here...
}

% Second column boxes
\headerbox{Results}{name=results,column=1,row=0,span=2}{
  Your results here...
  \includegraphics[width=0.9\linewidth]{results.pdf}
}

\headerbox{Analysis}{name=analysis,column=1,below=results}{
  Analysis details...
}

\headerbox{Validation}{name=validation,column=2,below=results}{
  Validation results...
}

% Bottom spanning box
\headerbox{Conclusions}{name=conclusions,column=0,span=3,above=bottom}{
  Your conclusions here...
}

\end{poster}
\end{document}
```

### Box Positioning

```latex
% Position by column and row
\headerbox{Title}{name=box1, column=0, row=0}{Content}

% Position relative to other boxes
\headerbox{Title}{name=box2, column=0, below=box1}{Content}

% Above another box
\headerbox{Title}{name=box3, column=1, above=bottom}{Content}

% Span multiple columns
\headerbox{Title}{name=box4, column=0, span=2, row=0}{Content}

% Between two boxes vertically
\headerbox{Title}{name=box5, column=0, below=box1, above=box3}{Content}

% Aligned with another box
\headerbox{Title}{name=box6, column=1, aligned=box1}{Content}
```

### Styling Options

```latex
\begin{poster}{
  % Grid and layout
  grid=false,                    % Show layout grid (debug)
  columns=3,                     % Number of columns
  colspacing=1em,                % Space between columns
  
  % Background
  background=plain,              % plain, shadetb, shadelr, user
  bgColorOne=white,
  bgColorTwo=lightgray,
  
  % Borders
  borderColor=blue!50,
  linewidth=2pt,
  
  % Header
  headerColorOne=blue!80,
  headerColorTwo=blue!70,
  headerFontColor=white,
  headerheight=0.12\textheight,
  headershape=roundedright,      % rectangle, rounded, roundedright, roundedleft
  headershade=plain,             % plain, shadetb, shadelr
  headerborder=open,             % open, closed
  
  % Boxes
  boxColorOne=white,
  boxColorTwo=blue!10,
  boxshade=plain,                % plain, shadetb, shadelr
  textborder=roundedleft,        % none, rectangle, rounded, roundedleft, roundedright
  
  % Eye catcher
  eyecatcher=true
}
```

### Color Schemes

```latex
% Professional blue
\begin{poster}{
  headerColorOne=blue!80,
  headerColorTwo=blue!70,
  boxColorTwo=blue!10,
  borderColor=blue!50
}

% Academic green
\begin{poster}{
  headerColorOne=green!70!black,
  headerColorTwo=green!60!black,
  boxColorTwo=green!10,
  borderColor=green!50
}

% Corporate gray
\begin{poster}{
  headerColorOne=gray!60,
  headerColorTwo=gray!50,
  boxColorTwo=gray!10,
  borderColor=gray!40
}
```

## Package Selection Guide

### Choose beamerposter if:
- ✅ You're already familiar with Beamer
- ✅ You need to match institutional Beamer themes
- ✅ You prefer traditional academic aesthetics
- ✅ You want extensive theme options
- ✅ You need fast compilation times
- ✅ You're creating posters for conservative academic conferences

### Choose tikzposter if:
- ✅ You want modern, colorful designs
- ✅ You plan to create custom graphics with TikZ
- ✅ You value aesthetic flexibility
- ✅ You want built-in professional themes
- ✅ You don't mind slightly longer compilation
- ✅ You're presenting at design-conscious or public-facing events

### Choose baposter if:
- ✅ You need structured multi-column layouts
- ✅ You want automatic box positioning
- ✅ You prefer clean, professional defaults
- ✅ You need precise control over box relationships
- ✅ You're creating posters with many sections
- ✅ You value consistent spacing and alignment

## Conversion Between Packages

### From beamerposter to tikzposter

```latex
% beamerposter
\begin{block}{Title}
  Content
\end{block}

% tikzposter equivalent
\block{Title}{
  Content
}
```

### From beamerposter to baposter

```latex
% beamerposter
\begin{block}{Introduction}
  Content
\end{block}

% baposter equivalent
\headerbox{Introduction}{name=intro, column=0, row=0}{
  Content
}
```

### From tikzposter to baposter

```latex
% tikzposter
\block{Methods}{
  Content
}

% baposter equivalent
\headerbox{Methods}{name=methods, column=0, row=0}{
  Content
}
```

## Compilation Tips

### Faster Compilation

```bash
# Use draft mode for initial edits
\documentclass[draft]{tikzposter}

# Compile with faster engines when possible
pdflatex -interaction=nonstopmode poster.tex

# For tikzposter, use externalization to cache TikZ graphics
\usetikzlibrary{external}
\tikzexternalize
```

### Memory Issues

```latex
% Increase TeX memory for large posters
% Add to poster preamble:
\pdfminorversion=7
\pdfobjcompresslevel=2
```

### Font Embedding

```bash
# Ensure fonts are embedded (required for printing)
pdflatex -dEmbedAllFonts=true poster.tex

# Check font embedding
pdffonts poster.pdf
```

## Hybrid Approaches

You can combine strengths of different packages:

### beamerposter with TikZ Graphics

```latex
\documentclass[final]{beamer}
\usepackage[size=a0]{beamerposter}
\usepackage{tikz}

\begin{block}{Flowchart}
  \begin{tikzpicture}
    % Custom TikZ graphics within beamerposter
  \end{tikzpicture}
\end{block}
```

### tikzposter with Beamer Themes

```latex
\documentclass{tikzposter}

% Import specific Beamer color definitions
\definecolor{beamerblue}{RGB}{0,51,102}
\colorlet{blocktitlebgcolor}{beamerblue}
```

## Recommended Packages for All Systems

```latex
% Essential packages for any poster
\usepackage{graphicx}        % Images
\usepackage{amsmath,amssymb} % Math symbols
\usepackage{booktabs}        % Professional tables
\usepackage{multicol}        % Multiple columns in text
\usepackage{qrcode}          % QR codes
\usepackage{hyperref}        % Hyperlinks
\usepackage{caption}         % Caption customization
\usepackage{subcaption}      % Subfigures
```

## Performance Comparison

| Package | Compile Time (A0) | PDF Size | Memory Usage |
|---------|-------------------|----------|--------------|
| beamerposter | ~5-10 seconds | 2-5 MB | Low |
| tikzposter | ~15-30 seconds | 5-15 MB | Medium-High |
| baposter | ~8-15 seconds | 3-8 MB | Medium |

*Note: Times for poster with 5 figures, typical conference content*

## Conclusion

All three packages are excellent choices for different scenarios:

- **beamerposter**: Best for traditional academic settings and Beamer users
- **tikzposter**: Best for modern, visually striking presentations
- **baposter**: Best for structured, professional multi-section posters

Choose based on your specific needs, aesthetic preferences, and time constraints. When in doubt, start with tikzposter for modern conferences or beamerposter for traditional academic venues.

### `references/latex_poster_reference.md`

# LaTeX Poster Reference

Package selection, layout, design principles, standard sizes, templates, figures,
color, typography, and QR codes. See also `latex_poster_packages.md`,
`poster_layout_design.md`, and `poster_design_principles.md` for the deeper
per-topic guides.

## Core Capabilities

### 1. LaTeX Poster Packages

Support for three major LaTeX poster packages, each with distinct advantages. For detailed comparison and package-specific guidance, refer to `references/latex_poster_packages.md`.

**beamerposter**:
- Extension of the Beamer presentation class
- Familiar syntax for Beamer users
- Excellent theme support and customization
- Best for: Traditional academic posters, institutional branding

**tikzposter**:
- Modern, flexible design with TikZ integration
- Built-in color themes and layout templates
- Extensive customization through TikZ commands
- Best for: Colorful, modern designs, custom graphics

**baposter**:
- Box-based layout system
- Automatic spacing and positioning
- Professional-looking default styles
- Best for: Multi-column layouts, consistent spacing

### 2. Poster Layout and Structure

Create effective poster layouts following visual communication principles. For comprehensive layout guidance, refer to `references/poster_layout_design.md`.

**Common Poster Sections**:
- **Header/Title**: Title, authors, affiliations, logos
- **Introduction/Background**: Research context and motivation
- **Methods/Approach**: Methodology and experimental design
- **Results**: Key findings with figures and data visualizations
- **Conclusions**: Main takeaways and implications
- **References**: Key citations (typically abbreviated)
- **Acknowledgments**: Funding, collaborators, institutions

**Layout Strategies**:
- **Column-based layouts**: 2-column, 3-column, or 4-column grids
- **Block-based layouts**: Flexible arrangement of content blocks
- **Z-pattern flow**: Guide readers through content logically
- **Visual hierarchy**: Use size, color, and spacing to emphasize key points

### 3. Design Principles for Research Posters

Apply evidence-based design principles for maximum impact. For detailed design guidance, refer to `references/poster_design_principles.md`.

**Typography**:
- Title: 72-120pt for visibility from distance
- Section headers: 48-72pt
- Body text: 24-36pt minimum for readability from 4-6 feet
- Use sans-serif fonts (Arial, Helvetica, Calibri) for clarity
- Limit to 2-3 font families maximum

**Color and Contrast**:
- Use high-contrast color schemes for readability
- Institutional color palettes for branding
- Color-blind friendly palettes (avoid red-green combinations)
- White space is active space—don't overcrowd

**Visual Elements**:
- High-resolution figures (300 DPI minimum for print)
- Large, clear labels on all figures
- Consistent figure styling throughout
- Strategic use of icons and graphics
- Balance text with visual content (40-50% visual recommended)

**Content Guidelines**:
- **Less is more**: 300-800 words total recommended
- Bullet points over paragraphs for scannability
- Clear, concise messaging
- Self-explanatory figures with minimal text explanation
- QR codes for supplementary materials or online resources

### 4. Standard Poster Sizes

Support for international and conference-specific poster dimensions:

**International Standards**:
- A0 (841 × 1189 mm / 33.1 × 46.8 inches) - Most common European standard
- A1 (594 × 841 mm / 23.4 × 33.1 inches) - Smaller format
- A2 (420 × 594 mm / 16.5 × 23.4 inches) - Compact posters

**North American Standards**:
- 36 × 48 inches (914 × 1219 mm) - Common US conference size
- 42 × 56 inches (1067 × 1422 mm) - Large format
- 48 × 72 inches (1219 × 1829 mm) - Extra large

**Orientation**:
- Portrait (vertical) - Most common, traditional
- Landscape (horizontal) - Better for wide content, timelines

### 5. Package-Specific Templates

Provide ready-to-use templates for each major package. Templates available in `assets/` directory.

**beamerposter Templates**:
- `beamerposter_template.tex` - Customizable beamerposter template

**tikzposter Templates**:
- `tikzposter_template.tex` - Customizable tikzposter template

**baposter Templates**:
- `baposter_template.tex` - Customizable baposter template

### 6. Figure and Image Integration

Optimize visual content for poster presentations:

**Best Practices**:
- Use vector graphics (PDF, SVG) when possible for scalability
- Raster images: minimum 300 DPI at final print size
- Consistent image styling (borders, captions, sizes)
- Group related figures together
- Use subfigures for comparisons

**LaTeX Figure Commands**:
```latex
% Include graphics package
\usepackage{graphicx}

% Simple figure
\includegraphics[width=0.8\linewidth]{figure.pdf}

% Figure with caption in tikzposter
\block{Results}{
  \begin{tikzfigure}
    \includegraphics[width=0.9\linewidth]{results.png}
  \end{tikzfigure}
}

% Multiple subfigures
\usepackage{subcaption}
\begin{figure}
  \begin{subfigure}{0.48\linewidth}
    \includegraphics[width=\linewidth]{fig1.pdf}
    \caption{Condition A}
  \end{subfigure}
  \begin{subfigure}{0.48\linewidth}
    \includegraphics[width=\linewidth]{fig2.pdf}
    \caption{Condition B}
  \end{subfigure}
\end{figure}
```

### 7. Color Schemes and Themes

Provide professional color palettes for various contexts:

**Academic Institution Colors**:
- Match university or department branding
- Use official color codes (RGB, CMYK, or LaTeX color definitions)

**Scientific Color Palettes** (color-blind friendly):
- Viridis: Professional gradient from purple to yellow
- ColorBrewer: Research-tested palettes for data visualization
- IBM Color Blind Safe: Accessible corporate palette

**Package-Specific Theme Selection**:

**beamerposter**:
```latex
\usetheme{Berlin}
\usecolortheme{beaver}
```

**tikzposter**:
```latex
\usetheme{Rays}
\usecolorstyle{Denmark}
```

**baposter**:
```latex
\begin{poster}{
  background=plain,
  bgColorOne=white,
  headerColorOne=blue!70,
  textborder=rounded
}
```

### 8. Typography and Text Formatting

Ensure readability and visual appeal:

**Font Selection**:
```latex
% Sans-serif fonts recommended for posters
\usepackage{helvet}      % Helvetica
\usepackage{avant}       % Avant Garde
\usepackage{sfmath}      % Sans-serif math fonts

% Set default to sans-serif
\renewcommand{\familydefault}{\sfdefault}
```

**Text Sizing**:
```latex
% Adjust text sizes for visibility
\setbeamerfont{title}{size=\VeryHuge}
\setbeamerfont{author}{size=\Large}
\setbeamerfont{institute}{size=\normalsize}
```

**Emphasis and Highlighting**:
- Use bold for key terms: `\textbf{important}`
- Color highlights sparingly: `\textcolor{blue}{highlight}`
- Boxes for critical information
- Avoid italics (harder to read from distance)

### 9. QR Codes and Interactive Elements

Enhance poster interactivity for modern conferences:

**QR Code Integration**:
```latex
\usepackage{qrcode}

% Link to paper, code repository, or supplementary materials
\qrcode[height=2cm]{https://github.com/username/project}

% QR code with caption
\begin{center}
  \qrcode[height=3cm]{https://doi.org/10.1234/paper}\\
  \small Scan for full paper
\end{center}
```

**Digital Enhancements**:
- Link to GitHub repositories for code
- Link to video presentations or demos
- Link to interactive web visualizations
- Link to supplementary data or appendices

### `references/poster_content_guide.md`

# Research Poster Content Guide

## Overview

Content is king in research posters. This guide covers writing strategies, section-specific guidance, visual-text balance, and best practices for communicating research effectively in poster format.

## Core Content Principles

### 1. The 3-5 Minute Rule

**Reality**: Most viewers spend 3-5 minutes at your poster
- **1 minute**: Scanning from distance (title, figures)
- **2-4 minutes**: Reading key points up close
- **5+ minutes**: Engaged conversation (if interested)

**Design Implication**: Poster must work at three levels:
1. **Distance view** (6-10 feet): Title and main figure visible
2. **Browse view** (3-6 feet): Section headers and key results readable
3. **Detail view** (1-3 feet): Full content accessible

### 2. Tell a Story, Not a Paper

**Poster ≠ Condensed Paper**

**Paper approach** (❌):
- Comprehensive literature review
- Detailed methodology
- All results presented
- Lengthy discussion
- 50+ references

**Poster approach** (✅):
- One sentence background
- Visual methods diagram
- 3-5 key results
- 3-4 bullet point conclusions
- 5-10 key references

**Story Arc for Posters**:
```
Hook (Problem) → Approach → Discovery → Impact
```

**Example**:
- **Hook**: "Antibiotic resistance threatens millions of lives annually"
- **Approach**: "We developed an AI system to predict resistance patterns"
- **Discovery**: "Our model achieves 87% accuracy, 20% better than existing methods"
- **Impact**: "Could reduce treatment failures by identifying resistance earlier"

### 3. The 800-Word Maximum

**Word Count Guidelines**:
- **Ideal**: 300-500 words
- **Maximum**: 800 words
- **Hard limit**: 1000 words (beyond this, poster is unreadable)

**Word Budget by Section**:
| Section | Word Count | % of Total |
|---------|-----------|------------|
| Introduction/Background | 50-100 | 15% |
| Methods | 100-150 | 25% |
| Results (text) | 100-200 | 25% |
| Discussion/Conclusions | 100-150 | 25% |
| References/Acknowledgments | 50-100 | 10% |

**Counting Tool**:
```latex
% Add word count to poster (remove for final)
\usepackage{texcount}
% Compile with: texcount -inc poster.tex
```

### 4. Visual-to-Text Ratio

**Optimal Balance**: 40-50% visual content, 50-60% text+white space

**Visual Content Includes**:
- Figures and graphs
- Photos and images
- Diagrams and flowcharts
- Icons and symbols
- Color blocks and design elements

**Too Text-Heavy** (❌):
- Wall of text
- Small figures
- Intimidating to viewers
- Low engagement

**Well-Balanced** (✅):
- Clear figures dominate
- Text supports visuals
- Easy to scan
- Inviting appearance

## Section-Specific Content Guidance

### Title

**Purpose**: Capture attention, convey topic, establish credibility

**Characteristics of Effective Titles**:
- **Concise**: 10-15 words maximum
- **Descriptive**: Clearly states research topic
- **Active**: Uses strong verbs when possible
- **Specific**: Avoids vague terms
- **Jargon-aware**: Balances field-specific terms with accessibility

**Title Formulas**:

**1. Descriptive**:
```
[Method/Approach] for [Problem/Application]

Example: "Deep Learning for Early Detection of Alzheimer's Disease"
```

**2. Question**:
```
[Research Question]?

Example: "Can Microbiome Diversity Predict Treatment Response?"
```

**3. Assertion**:
```
[Finding] in [Context]

Example: "Novel Mechanism Identified in Drug Resistance Pathways"
```

**4. Colon Format**:
```
[Topic]: [Specific Approach/Finding]

Example: "Urban Heat Islands: A Machine Learning Framework for Mitigation"
```

**Avoid**:
- ❌ Generic titles: "A Study of X"
- ❌ Overly cute or clever wordplay (confuses message)
- ❌ Excessive jargon: "Utilization of CRISPR-Cas9..."
- ❌ Unnecessarily long: "Investigation of the potential role of..."

**LaTeX Title Formatting**:
```latex
% Emphasize key words with bold
\title{Deep Learning for \textbf{Early Detection} of Alzheimer's Disease}

% Two-line titles for long names
\title{Machine Learning Framework for\\Urban Heat Island Mitigation}

% Avoid ALL CAPS (harder to read)
```

### Authors and Affiliations

**Best Practices**:
- **Presenting author**: Bold, underline, or asterisk
- **Corresponding author**: Include email
- **Affiliations**: Superscript numbers or symbols
- **Institutional logos**: 2-4 maximum

**Format Examples**:
```latex
% Simple format
\author{\textbf{Jane Smith}\textsuperscript{1}, John Doe\textsuperscript{2}}
\institute{
  \textsuperscript{1}University of Example, 
  \textsuperscript{2}Research Institute
}

% With contact
\author{Jane Smith\textsuperscript{1,*}}
\institute{
  \textsuperscript{1}Department, University\\
  \textsuperscript{*}jane.smith@university.edu
}
```

### Introduction/Background

**Purpose**: Establish context, motivate research, state objective

**Structure** (50-100 words):
1. **Problem statement** (1-2 sentences): What's the issue?
2. **Knowledge gap** (1-2 sentences): What's unknown/unsolved?
3. **Research objective** (1 sentence): What did you do?

**Example** (95 words):
```
Antibiotic resistance causes 700,000 deaths annually, projected to reach 
10 million by 2050. Current diagnostic methods require 48-72 hours, 
delaying appropriate treatment. Machine learning offers potential for 
rapid resistance prediction, but existing models lack generalizability 
across bacterial species. 

We developed a transformer-based deep learning model to predict antibiotic 
resistance from genomic sequences across multiple pathogen species. Our 
approach integrates evolutionary information and protein structure to 
improve cross-species accuracy.
```

**Visual Support**:
- Conceptual diagram showing problem
- Infographic with statistics
- Image of application context

**Common Mistakes**:
- ❌ Extensive literature review
- ❌ Too much background detail
- ❌ Undefined acronyms at first use
- ❌ Missing clear objective statement

### Methods

**Purpose**: Describe approach sufficiently for understanding (not replication)

**Key Question**: "How did you do it?" not "How could someone else replicate it?"

**Content Strategy**:
- **Prioritize**: Visual methods diagram > text description
- **Include**: Study design, key procedures, analysis approach
- **Omit**: Detailed protocols, routine procedures, specific reagent details

**Visual Methods (Highly Recommended)**:
```latex
% Flowchart of study design
\begin{tikzpicture}[node distance=2cm]
  \node (start) [box] {Data Collection\\n=1,000 samples};
  \node (process) [box, below of=start] {Preprocessing\\Quality Control};
  \node (analysis) [box, below of=process] {Statistical Analysis\\Mixed Models};
  \node (end) [box, below of=analysis] {Validation\\Independent Cohort};
  
  \draw [arrow] (start) -- (process);
  \draw [arrow] (process) -- (analysis);
  \draw [arrow] (analysis) -- (end);
\end{tikzpicture}
```

**Text Methods** (50-150 words):

**For Experimental Studies**:
```
Methods
• Study design: Randomized controlled trial (n=200)
• Participants: Adults aged 18-65 with Type 2 diabetes
• Intervention: 12-week exercise program vs. standard care
• Outcomes: HbA1c (primary), insulin sensitivity (secondary)
• Analysis: Linear mixed models, intention-to-treat
```

**For Computational Studies**:
```
Methods
• Dataset: 10,000 labeled images from ImageNet
• Architecture: ResNet-50 with custom attention mechanism
• Training: 100 epochs, Adam optimizer, learning rate 0.001
• Validation: 5-fold cross-validation
• Comparison: Baseline CNN, VGG-16, Inception-v3
```

**Format Options**:
- **Bullet points**: Quick scanning (recommended)
- **Numbered list**: Sequential procedures
- **Diagram + brief text**: Ideal combination
- **Table**: Multiple conditions or parameters

### Results

**Purpose**: Present key findings visually and clearly

**Golden Rule**: Show, don't tell

**Content Allocation**:
- **Figures**: 70-80% of Results section
- **Text**: 20-30% (brief descriptions, statistics)

**How Many Results**:
- **Ideal**: 3-5 main findings
- **Maximum**: 6-7 distinct results
- **Focus**: Primary outcomes, most impactful findings

**Figure Selection Criteria**:
1. Does it support the main message?
2. Is it self-explanatory with caption?
3. Can it be understood in 10 seconds?
4. Does it add information beyond text?

**Figure Captions**:
- **Descriptive**: Explain what is shown
- **Standalone**: Understandable without reading full poster
- **Statistical**: Include significance indicators, sample sizes
- **Concise**: 1-3 sentences

**Example Caption**:
```latex
\caption{Treatment significantly improved outcomes. 
Mean±SD shown for control (blue, n=45) and treatment (orange, n=47) groups. 
**p<0.01, ***p<0.001 (two-tailed t-test).}
```

**Text Support for Results** (100-200 words):
- State main finding per figure
- Include key statistics
- Note trends or patterns
- Avoid detailed interpretation (save for Discussion)

**Example Results Text**:
```
Key Findings
• Model achieved 87% accuracy on test set (vs. 73% baseline)
• Performance consistent across 5 bacterial species (p<0.001)
• Prediction speed: <30 seconds per isolate
• Feature importance: protein structure (42%), sequence (35%), 
  evolutionary conservation (23%)
```

**Data Presentation Formats**:

**1. Bar Charts**: Comparing categories
```latex
\begin{tikzpicture}
  \begin{axis}[
    ybar,
    ylabel=Accuracy (\%),
    symbolic x coords={Baseline, Model A, Our Method},
    xtick=data,
    nodes near coords
  ]
  \addplot coordinates {(Baseline,73) (Model A,81) (Our Method,87)};
  \end{axis}
\end{tikzpicture}
```

**2. Line Graphs**: Trends over time
**3. Scatter Plots**: Correlations
**4. Heatmaps**: Matrix data, clustering
**5. Box Plots**: Distributions, comparisons
**6. ROC Curves**: Classification performance

### Discussion/Conclusions

**Purpose**: Interpret findings, state implications, acknowledge limitations

**Structure** (100-150 words):

**1. Main Conclusions** (50-75 words):
- 3-5 bullet points
- Clear, specific takeaways
- Linked to research objectives

**Example**:
```
Conclusions
• First cross-species model for antibiotic resistance prediction 
  achieving >85% accuracy
• Protein structure integration critical for generalizability 
  (improved accuracy by 14%)
• Prediction speed enables clinical decision support within 
  consultation timeframe
• Potential to reduce inappropriate antibiotic use by 20-30%
```

**2. Limitations** (25-50 words, optional but recommended):
- Acknowledge key constraints
- Brief, honest
- Shows scientific rigor

**Example**:
```
Limitations
• Training data limited to 5 bacterial species
• Requires genomic sequencing (not widely available)
• Validation needed in prospective clinical trials
```

**3. Future Directions** (25-50 words, optional):
- Next steps
- Broader implications
- Call to action

**Example**:
```
Next Steps
• Expand to 20+ additional species
• Develop point-of-care sequencing integration
• Launch multi-center clinical validation study (2025)
```

**Avoid**:
- ❌ Overstating findings: "This revolutionary breakthrough..."
- ❌ Extensive comparison to other work
- ❌ New results in Discussion
- ❌ Vague conclusions: "Further research is needed"

### References

**How Many**: 5-10 key citations

**Selection Criteria**:
- Include seminal work in the field
- Recent relevant studies (last 5 years)
- Methods cited in your poster
- Controversial claims that need support

**Format**: Abbreviated, consistent style

**Examples**:

**Numbered (Vancouver)**:
```
References
1. Smith et al. (2023). Nature. 615:234-240.
2. Jones & Lee (2024). Science. 383:112-118.
3. Chen et al. (2022). Cell. 185:456-470.
```

**Author-Year (APA)**:
```
References
Smith, J. et al. (2023). Title. Nature, 615, 234-240.
Jones, A., & Lee, B. (2024). Title. Science, 383, 112-118.
```

**Minimal (For Space Constraints)**:
```
Key References: Smith (Nature 2023), Jones (Science 2024), 
Chen (Cell 2022). Full bibliography: [QR Code]
```

**Alternative**: QR code linking to full reference list

### Acknowledgments

**Include**:
- Funding sources (with grant numbers)
- Major collaborators
- Core facilities used
- Dataset sources

**Format** (25-50 words):
```
Acknowledgments
Funded by NIH Grant R01-123456 and NSF Award 7890123. 
We thank Dr. X for data access, the Y Core Facility for 
sequencing, and Z for helpful discussions.
```

### Contact Information

**Essential Elements**:
- Name of presenting/corresponding author
- Email address
- Optional: Lab website, Twitter/X, LinkedIn, ORCID

**Format**:
```
Contact: Jane Smith, jane.smith@university.edu
Lab: smithlab.university.edu | Twitter: @smithlab
```

**QR Code Alternative**:
- Link to personal/lab website
- Link to paper preprint/publication
- Link to code repository (GitHub)
- Link to supplementary materials

## Writing Style for Posters

### Active vs. Passive Voice

**Prefer Active Voice** (more engaging, clearer):
- ✅ "We developed a model..."
- ✅ "The treatment reduced symptoms..."

**Passive Voice** (when appropriate):
- ✅ "Samples were collected from..."
- ✅ "Data were analyzed using..."

### Sentence Length

**Keep Sentences Short**:
- **Ideal**: 10-15 words per sentence
- **Maximum**: 20-25 words
- **Avoid**: >30 words (hard to follow)

**Example Revision**:
- ❌ Long: "We performed a comprehensive analysis of gene expression data from 500 patients with colorectal cancer using RNA sequencing and identified 47 differentially expressed genes associated with treatment response." (31 words)
- ✅ Short: "We analyzed RNA sequencing data from 500 colorectal cancer patients. We identified 47 genes associated with treatment response." (19 words total, two sentences)

### Bullet Points vs. Paragraphs

**Use Bullet Points For**:
- ✅ Lists of items or findings
- ✅ Key conclusions
- ✅ Methods steps
- ✅ Study characteristics

**Use Short Paragraphs For**:
- ✅ Narrative flow (Introduction)
- ✅ Complex explanations
- ✅ Connected ideas

**Bullet Point Best Practices**:
- Start with action verbs or nouns
- Parallel structure throughout list
- 3-7 bullets per list (not too many)
- Brief (1-2 lines each)

**Example**:
```
Methods
• Participants: 200 adults (18-65 years)
• Design: Double-blind RCT (12 weeks)
• Intervention: Daily 30-min exercise
• Control: Standard care
• Analysis: Mixed models (SPSS v.28)
```

### Acronyms and Jargon

**First Use Rule**: Define at first appearance
```
We used machine learning (ML) to analyze... Later, ML predicted...
```

**Common Acronyms**: May not need definition if universal to field
- DNA, RNA, MRI, CT, PCR (in biomedical context)
- AI, ML, CNN (in computer science context)

**Avoid Excessive Jargon**:
- ❌ "Utilized" → ✅ "Used"
- ❌ "Implement utilization of" → ✅ "Use"
- ❌ "A majority of" → ✅ "Most"

### Numbers and Statistics

**Present Statistics Clearly**:
- Always include measure of variability (SD, SE, CI)
- Report sample sizes: n=50
- Indicate significance: p<0.05, p<0.01, p<0.001
- Use symbols consistently: * for p<0.05, ** for p<0.01

**Format Numbers**:
- Round appropriately (avoid false precision)
- Use consistent decimal places
- Include units: 25 mg/dL, 37°C
- Large numbers: 1,000 or 1000 (be consistent)

**Example**:
```
Treatment increased response by 23.5% (95% CI: 18.2-28.8%, p<0.001, n=150)
```

## Visual-Text Integration

### Figure-Text Relationship

**Figure First, Text Second**:
1. Design poster around key figures
2. Add text to support and explain visuals
3. Ensure figures can stand alone

**Text Placement Relative to Figures**:
- **Above**: Context, "What you're about to see"
- **Below**: Explanation, statistics, caption
- **Beside**: Comparison, interpretation

### Callouts and Annotations

**On-Figure Annotations**:
```latex
\begin{tikzpicture}
  \node[inner sep=0] (img) {\includegraphics[width=10cm]{figure.pdf}};
  \draw[->, thick, red] (8,5) -- (6,3) node[left] {Key region};
  \draw[red, thick] (3,2) circle (1cm) node[above=1.2cm] {Anomaly};
\end{tikzpicture}
```

**Callout Boxes**:
```latex
\begin{tcolorbox}[colback=yellow!10, colframe=orange!80, 
                  title=Key Finding]
Our method reduces errors by 34\% compared to state-of-the-art.
\end{tcolorbox}
```

### Icons for Section Headers

**Visual Section Markers**:
```latex
\usepackage{fontawesome5}

\block{\faFlask~Introduction}{...}
\block{\faCog~Methods}{...}
\block{\faChartBar~Results}{...}
\block{\faLightbulb~Conclusions}{...}
```

## Content Adaptation Strategies

### From Paper to Poster

**Condensation Process**:

**1. Identify Core Message** (The Elevator Pitch):
- What's the one thing you want people to remember?
- If you had 30 seconds, what would you say?

**2. Select Key Results**:
- Choose 3-5 most impactful findings
- Omit supporting/secondary results
- Focus on figures with strong visual impact

**3. Simplify Methods**:
- Visual flowchart > text description
- Omit routine procedures
- Include only essential parameters

**4. Trim Literature Review**:
- One sentence background
- One sentence gap/motivation
- One sentence your contribution

**5. Condense Discussion**:
- Main conclusions only
- Brief limitations
- One sentence future direction

### For Different Audiences

**Specialist Audience** (Same Field):
- Can use field-specific jargon
- Less background needed
- Focus on novel methodology
- Emphasize nuanced findings

**General Scientific Audience**:
- Define key terms
- More context/background
- Broader implications
- Visual metaphors helpful

**Public/Lay Audience**:
- Minimal jargon, all defined
- Extensive context
- Real-world applications
- Analogies and simple language

**Example Adaptation**:

**Specialist**: "CRISPR-Cas9 knockout of BRCA1 induced synthetic lethality with PARP inhibitors"

**General**: "We used gene editing to make cancer cells vulnerable to existing drugs"

**Public**: "We found a way to make cancer treatments work better by targeting specific genetic weaknesses"

## Quality Control Checklist

### Content Review

**Clarity**:
- [ ] Main message immediately clear
- [ ] All acronyms defined
- [ ] Sentences short and direct
- [ ] No unnecessary jargon

**Completeness**:
- [ ] Research question/objective stated
- [ ] Methods sufficiently described
- [ ] Key results presented
- [ ] Conclusions drawn
- [ ] Limitations acknowledged

**Accuracy**:
- [ ] All statistics correct
- [ ] Figure captions accurate
- [ ] References properly cited
- [ ] No overstated claims

**Engagement**:
- [ ] Compelling title
- [ ] Visual interest
- [ ] Clear take-home message
- [ ] Conversation starters

### Readability Testing

**Distance Test**:
- Print at 25% scale
- View from 2-3 feet (simulates 8-12 feet for full poster)
- Can you read: Title? Section headers? Body text?

**Scan Test**:
- Give poster to colleague for 30 seconds
- Ask: "What is this poster about?"
- They should identify: Topic, approach, main finding

**Detail Test**:
- Ask colleague to read poster thoroughly (5 min)
- Ask: "What are the key conclusions?"
- Verify understanding matches your intent

## Common Content Mistakes

**1. Too Much Text**
- ❌ >1000 words
- ❌ Long paragraphs
- ❌ Full paper condensed
- ✅ 300-800 words, bullet points, key findings only

**2. Unclear Message**
- ❌ Multiple unrelated findings
- ❌ No clear conclusion
- ❌ Vague implications
- ✅ 1-3 main points, explicit conclusions

**3. Methods Overkill**
- ❌ Detailed protocols
- ❌ All parameters listed
- ❌ Routine procedures described
- ✅ Visual flowchart, key details only

**4. Poor Figure Integration**
- ❌ Figures without context
- ❌ Unclear captions
- ❌ Text doesn't reference figures
- ✅ Figures central, well-captioned, text integrated

**5. Missing Context**
- ❌ No background
- ❌ Undefined acronyms
- ❌ Assumes expert knowledge
- ✅ Brief context, definitions, accessible to broader audience

## Conclusion

Effective poster content:
- **Concise**: 300-800 words maximum
- **Visual**: 40-50% figures and graphics
- **Clear**: One main message, 3-5 key findings
- **Engaging**: Compelling story, not just facts
- **Accessible**: Appropriate for target audience
- **Actionable**: Clear implications and next steps

Remember: Your poster is a conversation starter, not a comprehensive treatise. Design content to intrigue, engage, and invite discussion.

### `references/poster_design_principles.md`

# Research Poster Design Principles

## Overview

Effective poster design balances visual appeal, readability, and scientific content. This guide covers typography, color theory, visual hierarchy, accessibility, and evidence-based design principles for research posters.

## Core Design Principles

### 1. Visual Hierarchy

Guide viewers through content in logical order using size, color, position, and contrast.

**Hierarchy Levels**:

1. **Primary (Title)**: Largest, most prominent
   - Size: 72-120pt
   - Position: Top center or top spanning
   - Weight: Bold
   - Purpose: Capture attention from 20+ feet

2. **Secondary (Section Headers)**: Organize content
   - Size: 48-72pt
   - Weight: Bold or semi-bold
   - Purpose: Section navigation, readable from 10 feet

3. **Tertiary (Body Text)**: Main content
   - Size: 24-36pt minimum
   - Weight: Regular
   - Purpose: Detailed information, readable from 4-6 feet

4. **Quaternary (Captions, References)**: Supporting info
   - Size: 18-24pt
   - Weight: Regular or light
   - Purpose: Context and attribution

**Implementation**:
```latex
% Define hierarchy in LaTeX
\setbeamerfont{title}{size=\VeryHuge,series=\bfseries}        % 90pt+
\setbeamerfont{block title}{size=\Huge,series=\bfseries}      % 60pt
\setbeamerfont{block body}{size=\LARGE}                        % 30pt
\setbeamerfont{caption}{size=\large}                           % 24pt
```

### 2. White Space (Negative Space)

Empty space is not wasted space—it enhances readability and guides attention.

**White Space Functions**:
- **Breathing room**: Prevents overwhelming viewers
- **Grouping**: Shows which elements belong together
- **Focus**: Draws attention to important elements
- **Flow**: Creates visual pathways through content

**Guidelines**:
- Minimum 5-10% margins on all sides
- Consistent spacing between blocks (1-2cm)
- Space around figures equal to or greater than border width
- Group related items closely, separate unrelated items
- Don't fill every inch—aim for 40-60% text coverage

**LaTeX Implementation**:
```latex
% beamerposter spacing
\setbeamertemplate{block begin}{
  \vskip2ex  % Space before block
  ...
}

% tikzposter spacing
\documentclass[..., blockverticalspace=15mm, colspace=15mm]{tikzposter}

% Manual spacing
\vspace{2cm}  % Vertical space
\hspace{1cm}  % Horizontal space
```

### 3. Alignment and Grid Systems

Proper alignment creates professional, organized appearance.

**Alignment Types**:
- **Left-aligned text**: Most readable for body text (Western audiences)
- **Center-aligned**: Headers, titles, symmetric layouts
- **Right-aligned**: Rarely used, special cases only
- **Justified**: Avoid (creates uneven spacing)

**Grid Systems**:
- **2-column**: Simple, traditional, good for narrative flow
- **3-column**: Most common, balanced, versatile
- **4-column**: Complex, information-dense, requires careful design
- **Asymmetric**: Creative, modern, requires expertise

**Best Practices**:
- Align block edges to invisible grid lines
- Keep consistent column widths (unless intentionally asymmetric)
- Align similar elements (all figures, all text blocks)
- Use consistent margins throughout

### 4. Visual Flow and Reading Patterns

Design for natural eye movement and logical content progression.

**Common Reading Patterns**:

**Z-Pattern (Landscape posters)**:
```
Start → → → Top Right
  ↓
Middle Left → → Middle
  ↓
Bottom Left → → → End
```

**F-Pattern (Portrait posters)**:
```
Title → → → →
↓
Section 1 → →
↓
Section 2 → →
↓
Section 3 → →
↓
Conclusion → →
```

**Gutenberg Diagram**:
```
Primary Area     Strong Fallow
(top-left)       (top-right)
        ↓              ↓
Weak Fallow      Terminal Area
(bottom-left)    (bottom-right)
```

**Implementation Strategy**:
1. Place most important content in "hot zones" (top-left, center)
2. Create visual paths with arrows, lines, or color
3. Use numbering for sequential information (Methods steps)
4. Design left-to-right, top-to-bottom flow (Western audiences)
5. Position conclusions prominently (bottom-right is natural endpoint)

## Typography

### Font Selection

**Recommended Fonts**:

**Sans-Serif (Recommended for posters)**:
- **Helvetica**: Clean, professional, widely available
- **Arial**: Similar to Helvetica, universal compatibility
- **Calibri**: Modern, friendly, good readability
- **Open Sans**: Contemporary, excellent web and print
- **Roboto**: Modern, Google design, highly readable
- **Lato**: Warm, professional, works at all sizes

**Serif (Use sparingly)**:
- **Times New Roman**: Traditional, formal
- **Garamond**: Elegant, good for humanities
- **Georgia**: Designed for screens, readable

**Avoid**:
- ❌ Comic Sans (unprofessional)
- ❌ Decorative or script fonts (illegible from distance)
- ❌ Mixing more than 2-3 font families

**LaTeX Implementation**:
```latex
% Helvetica (sans-serif)
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

% Arial-like
\usepackage{avant}
\renewcommand{\familydefault}{\sfdefault}

% Modern fonts with fontspec (requires LuaLaTeX/XeLaTeX)
\usepackage{fontspec}
\setmainfont{Helvetica Neue}
\setsansfont{Open Sans}
```

### Font Sizing

**Absolute Minimum Sizes** (readable from 4-6 feet):
- Title: 72pt+ (85-120pt recommended)
- Section headers: 48-72pt
- Body text: 24-36pt (30pt+ recommended)
- Captions/small text: 18-24pt
- References: 16-20pt minimum

**Testing Readability**:
- Print at 25% scale
- Read from 2-3 feet distance
- If legible, full-scale poster will be readable from 8-12 feet

**Size Conversion**:
| LaTeX Command | Approximate Size | Use Case |
|---------------|------------------|----------|
| `\tiny` | 10pt | Avoid on posters |
| `\small` | 16pt | Minimal use only |
| `\normalsize` | 20pt | References (scaled up) |
| `\large` | 24pt | Captions, small text |
| `\Large` | 28pt | Body text (minimum) |
| `\LARGE` | 32pt | Body text (recommended) |
| `\huge` | 36pt | Subheadings |
| `\Huge` | 48pt | Section headers |
| `\VeryHuge` | 72pt+ | Title |

### Text Formatting Best Practices

**Use**:
- ✅ **Bold** for emphasis and headers
- ✅ Short paragraphs (3-5 lines maximum)
- ✅ Bullet points for lists
- ✅ Adequate line spacing (1.2-1.5)
- ✅ High contrast (dark text on light background)

**Avoid**:
- ❌ Italics from distance (hard to read)
- ❌ ALL CAPS FOR LONG TEXT (SLOW TO READ)
- ❌ Underlines (old-fashioned, interferes with descenders)
- ❌ Long paragraphs (> 6 lines)
- ❌ Light text on light backgrounds

**Line Spacing**:
```latex
% Increase line spacing for readability
\usepackage{setspace}
\setstretch{1.3}  % 1.3x normal spacing

% Or in specific blocks
\begin{spacing}{1.5}
  Your text here with extra spacing
\end{spacing}
```

## Color Theory for Posters

### Color Psychology and Meaning

Colors convey meaning and affect viewer perception:

| Color | Associations | Use Cases |
|-------|--------------|-----------|
| **Blue** | Trust, professionalism, science | Academic, medical, technology |
| **Green** | Nature, health, growth | Environmental, biology, health |
| **Red** | Energy, urgency, passion | Attention, warnings, bold statements |
| **Orange** | Creativity, enthusiasm | Innovative research, friendly approach |
| **Purple** | Wisdom, creativity, luxury | Humanities, arts, premium research |
| **Gray** | Neutral, professional, modern | Technology, minimal designs |
| **Yellow** | Optimism, attention, caution | Highlights, energy, caution areas |

### Color Scheme Types

**1. Monochromatic**: Variations of single hue
- **Pros**: Harmonious, professional, easy to execute
- **Cons**: Can be boring, less visual interest
- **Use**: Conservative conferences, institutional branding

```latex
% Monochromatic blue scheme
\definecolor{darkblue}{RGB}{0,51,102}
\definecolor{medblue}{RGB}{51,102,153}
\definecolor{lightblue}{RGB}{204,229,255}
```

**2. Analogous**: Adjacent colors on color wheel
- **Pros**: Harmonious, visually comfortable
- **Cons**: Low contrast, may lack excitement
- **Use**: Nature/biology topics, smooth gradients

```latex
% Analogous blue-green scheme
\definecolor{blue}{RGB}{0,102,204}
\definecolor{teal}{RGB}{0,153,153}
\definecolor{green}{RGB}{51,153,102}
```

**3. Complementary**: Opposite colors on wheel
- **Pros**: High contrast, vibrant, energetic
- **Cons**: Can be overwhelming if intense
- **Use**: Drawing attention, modern designs

```latex
% Complementary blue-orange scheme
\definecolor{primary}{RGB}{0,71,171}     % Blue
\definecolor{accent}{RGB}{255,127,0}     % Orange
```

**4. Triadic**: Three evenly spaced colors
- **Pros**: Balanced, vibrant, visually rich
- **Cons**: Can appear busy if not balanced
- **Use**: Multi-topic posters, creative fields

```latex
% Triadic scheme
\definecolor{blue}{RGB}{0,102,204}
\definecolor{red}{RGB}{204,0,51}
\definecolor{yellow}{RGB}{255,204,0}
```

**5. Split-Complementary**: Base + two adjacent to complement
- **Pros**: High contrast but less tense than complementary
- **Cons**: Complex to balance
- **Use**: Sophisticated designs, experienced designers

### High-Contrast Combinations

Ensure readability with sufficient contrast:

**Excellent Contrast (Use these)**:
- Dark blue on white
- Black on white
- White on dark blue/green/purple
- Dark gray on light yellow
- Black on light cyan

**Poor Contrast (Avoid)**:
- ❌ Red on green (color-blind issue)
- ❌ Yellow on white
- ❌ Light gray on white
- ❌ Blue on black (hard to read)
- ❌ Any pure colors on each other

**Contrast Ratio Standards**:
- Minimum: 4.5:1 (WCAG AA)
- Recommended: 7:1 (WCAG AAA)
- Test at: https://webaim.org/resources/contrastchecker/

**LaTeX Color Contrast**:
```latex
% High contrast header
\setbeamercolor{block title}{bg=black, fg=white}

% Medium contrast body
\setbeamercolor{block body}{bg=gray!10, fg=black}

% Check contrast manually or use online tools
```

### Color-Blind Friendly Palettes

~8% of males and ~0.5% of females have color vision deficiency.

**Safe Color Combinations**:
- Blue + Orange (most universally distinguishable)
- Blue + Yellow
- Blue + Red
- Purple + Green (use with caution)

**Avoid**:
- ❌ Red + Green (indistinguishable to most common color blindness)
- ❌ Green + Brown
- ❌ Blue + Purple (can be problematic)
- ❌ Light green + Yellow

**Recommended Palettes**:

**IBM Color Blind Safe** (excellent accessibility):
```latex
\definecolor{ibmblue}{RGB}{100,143,255}
\definecolor{ibmmagenta}{RGB}{254,97,0}
\definecolor{ibmpurple}{RGB}{220,38,127}
\definecolor{ibmcyan}{RGB}{33,191,115}
```

**Okabe-Ito Palette** (scientifically tested):
```latex
\definecolor{okorange}{RGB}{230,159,0}
\definecolor{okskyblue}{RGB}{86,180,233}
\definecolor{okgreen}{RGB}{0,158,115}
\definecolor{okyellow}{RGB}{240,228,66}
\definecolor{okblue}{RGB}{0,114,178}
\definecolor{okvermillion}{RGB}{213,94,0}
\definecolor{okpurple}{RGB}{204,121,167}
```

**Paul Tol's Bright Palette**:
```latex
\definecolor{tolblue}{RGB}{68,119,170}
\definecolor{tolred}{RGB}{204,102,119}
\definecolor{tolgreen}{RGB}{34,136,51}
\definecolor{tolyellow}{RGB}{238,221,136}
\definecolor{tolcyan}{RGB}{102,204,238}
```

### Institutional Branding

Match university or department colors:

```latex
% Example: Stanford colors
\definecolor{stanford-red}{RGB}{140,21,21}
\definecolor{stanford-gray}{RGB}{83,86,90}

% Example: MIT colors
\definecolor{mit-red}{RGB}{163,31,52}
\definecolor{mit-gray}{RGB}{138,139,140}

% Example: Cambridge colors
\definecolor{cambridge-blue}{RGB}{163,193,173}
\definecolor{cambridge-lblue}{RGB}{212,239,223}
```

## Accessibility Considerations

### Universal Design Principles

Design posters usable by the widest range of people:

**1. Visual Accessibility**:
- High contrast text (minimum 4.5:1 ratio)
- Large font sizes (24pt+ body text)
- Color-blind safe palettes
- Clear visual hierarchy
- Avoid relying solely on color to convey information

**2. Cognitive Accessibility**:
- Clear, simple language
- Logical organization
- Consistent layout
- Visual cues for navigation (arrows, numbers)
- Avoid clutter and information overload

**3. Physical Accessibility**:
- Position critical content at wheelchair-accessible height (3-5 feet)
- Include QR codes to digital versions
- Provide printed handouts for detail viewing
- Consider lighting and reflection in poster material choice

### Alternative Text and Descriptions

Make posters accessible to screen readers (for digital versions):

```latex
% Add alt text to figures
\includegraphics[width=\linewidth]{figure.pdf}
% Alternative: Include detailed caption
\caption{Bar graph showing mean±SD of treatment outcomes. 
Control group (blue): 45±5\%; Treatment group (orange): 78±6\%. 
Asterisks indicate significance: *p<0.05, **p<0.01.}
```

### Multi-Modal Information

Don't rely on single sensory channel:

**Use Redundant Encoding**:
- Color + Shape (not just color for categories)
- Color + Pattern (hatching, stippling)
- Color + Label (text labels on graph elements)
- Text + Icons (visual + verbal)

**Example**:
```latex
% Good: Color + shape + label
\begin{tikzpicture}
  \draw[fill=blue, circle] (0,0) circle (0.3) node[right] {Male: 45\%};
  \draw[fill=red, rectangle] (0,-1) rectangle (0.6,-0.4) node[right] {Female: 55\%};
\end{tikzpicture}
```

## Layout Composition

### Rule of Thirds

Divide poster into 3×3 grid; place key elements at intersections:

```
+-----+-----+-----+
|  ×  |     |  ×  |  ← Top third (title, logos)
+-----+-----+-----+
|     |  ×  |     |  ← Middle third (main content)
+-----+-----+-----+
|  ×  |     |  ×  |  ← Bottom third (conclusions)
+-----+-----+-----+
  ↑           ↑
Left        Right
```

**Power Points** (intersections):
- Top-left: Primary section start
- Top-right: Logos, QR codes
- Center: Key figure or main result
- Bottom-right: Conclusions, contact

### Balance and Symmetry

**Symmetric Layouts**:
- Formal, traditional, stable
- Easy to design
- Can appear static or boring
- Good for conservative audiences

**Asymmetric Layouts**:
- Dynamic, modern, interesting
- Harder to execute well
- More visually engaging
- Good for creative fields

**Visual Weight Balance**:
- Large elements = heavy weight
- Dark colors = heavy weight
- Dense text = heavy weight
- Distribute weight evenly across poster

### Proximity and Grouping

**Gestalt Principles**:

**Proximity**: Items close together are perceived as related
```
[Introduction]  [Methods]

[Results]       [Discussion]
```

**Similarity**: Similar items are perceived as grouped
- Use consistent colors for related sections
- Same border styles for similar content types

**Continuity**: Eyes follow lines and paths
- Use arrows to guide through methods
- Align elements to create invisible lines

**Closure**: Mind completes incomplete shapes
- Use partial borders to group without boxing in

## Visual Elements

### Icons and Graphics

Strategic use of icons enhances comprehension:

**Benefits**:
- Universal language (crosses linguistic barriers)
- Faster processing than text
- Adds visual interest
- Clarifies concepts

**Best Practices**:
- Use consistent style (all line, all filled, all flat)
- Appropriate size (1-3cm typical)
- Label ambiguous icons
- Source: Font Awesome, Noun Project, academic icon sets

**LaTeX Implementation**:
```latex
% Font Awesome icons
\usepackage{fontawesome5}
\faFlask{} Methods \quad \faChartBar{} Results

% Custom icons with TikZ
\begin{tikzpicture}
  \node[circle, draw, thick, minimum size=1cm] {\Huge \faAtom};
\end{tikzpicture}
```

### Borders and Dividers

**Use Borders To**:
- Define sections
- Group related content
- Add visual interest
- Match institutional branding

**Border Styles**:
- Solid lines: Traditional, formal
- Dashed lines: Informal, secondary info
- Rounded corners: Friendly, modern
- Drop shadows: Depth, modern (use sparingly)

**Guidelines**:
- Keep consistent width (2-5pt typical)
- Use sparingly (not every element needs a border)
- Match border color to content or theme
- Ensure sufficient padding inside borders

```latex
% tikzposter borders
\usecolorstyle{Denmark}
\tikzposterlatexaffectionproofoff  % Remove bottom-right logo

% Custom border style
\defineblockstyle{CustomBlock}{
  titlewidthscale=1, bodywidthscale=1, titleleft,
  titleoffsetx=0pt, titleoffsety=0pt, bodyoffsetx=0pt, bodyoffsety=0pt,
  bodyverticalshift=0pt, roundedcorners=10, linewidth=2pt,
  titleinnersep=8mm, bodyinnersep=8mm
}{
  \draw[draw=blocktitlebgcolor, fill=blockbodybgcolor, 
        rounded corners=\blockroundedcorners, line width=\blocklinewidth]
       (blockbody.south west) rectangle (blocktitle.north east);
}
```

### Background and Texture

**Background Options**:

**Plain (Recommended)**:
- White or very light color
- Maximum readability
- Professional
- Print-friendly

**Gradient**:
- Subtle gradients acceptable
- Top-to-bottom or radial
- Avoid strong contrasts that interfere with text

**Textured**:
- Very subtle textures only
- Watermarks of logos/molecules (5-10% opacity)
- Avoid patterns that create visual noise

**Avoid**:
- ❌ Busy backgrounds
- ❌ Images behind text
- ❌ High contrast backgrounds
- ❌ Repeating patterns that cause visual artifacts

```latex
% Gradient background in tikzposter
\documentclass{tikzposter}
\definecolorstyle{GradientStyle}{
  % ...color definitions...
}{
  \colorlet{backgroundcolor}{white!90!blue}
  \colorlet{framecolor}{white!70!blue}
}

% Watermark
\usepackage{tikz}
\AddToShipoutPictureBG{
  \AtPageCenter{
    \includegraphics[width=0.5\paperwidth,opacity=0.05]{university-seal.pdf}
  }
}
```

## Common Design Mistakes

### Critical Errors

**1. Too Much Text** (Most common mistake)
- ❌ More than 1000 words
- ❌ Long paragraphs (>5 lines)
- ❌ Small font sizes to fit more content
- ✅ Solution: Cut ruthlessly, use bullet points, focus on key messages

**2. Poor Contrast**
- ❌ Light text on light background
- ❌ Colored text on colored background
- ✅ Solution: Dark on light or light on dark, test contrast ratio

**3. Font Size Too Small**
- ❌ Body text under 24pt
- ❌ Trying to fit full paper content
- ✅ Solution: 30pt+ body text, prioritize key findings

**4. Cluttered Layout**
- ❌ No white space
- ❌ Elements touching edges
- ❌ Random placement
- ✅ Solution: Generous margins, grid alignment, intentional white space

**5. Inconsistent Styling**
- ❌ Multiple font families
- ❌ Varying header styles
- ❌ Misaligned elements
- ✅ Solution: Define style guide, use templates, align to grid

### Moderate Issues

**6. Poor Figure Quality**
- ❌ Pixelated images (<300 DPI)
- ❌ Tiny axis labels
- ❌ Unreadable legends
- ✅ Solution: Vector graphics (PDF/SVG), large labels, clear legends

**7. Color Overload**
- ❌ Too many colors (>5 distinct hues)
- ❌ Neon or overly saturated colors
- ✅ Solution: Limit to 2-3 main colors, use tints/shades for variation

**8. Ignoring Visual Hierarchy**
- ❌ All text same size
- ❌ No clear entry point
- ✅ Solution: Vary sizes significantly, clear title, visual flow

**9. Information Overload**
- ❌ Trying to show everything
- ❌ Too many figures
- ✅ Solution: Show 3-5 key results, link to full paper via QR code

**10. Poor Typography**
- ❌ Justified text (uneven spacing)
- ❌ All caps body text
- ❌ Mixing serif and sans-serif randomly
- ✅ Solution: Left-align body, sentence case, consistent fonts

## Design Checklist

### Before Printing

- [ ] Title visible and readable from 20+ feet
- [ ] Body text minimum 24pt, ideally 30pt+
- [ ] High contrast (4.5:1 minimum) throughout
- [ ] Color-blind friendly palette
- [ ] Less than 800 words total
- [ ] White space around all elements
- [ ] Consistent alignment and spacing
- [ ] All figures high resolution (300+ DPI)
- [ ] Figure labels readable (18pt+ minimum)
- [ ] No orphaned text or awkward breaks
- [ ] Contact information included
- [ ] QR codes tested and functional
- [ ] Consistent font usage (2-3 families max)
- [ ] All acronyms defined
- [ ] Proper institutional branding/logos
- [ ] Print test at 25% scale for readability check

### Content Review

- [ ] Clear narrative arc (problem → approach → findings → impact)
- [ ] 1-3 main messages clearly communicated
- [ ] Methods concise but reproducible
- [ ] Results visually presented (not just text)
- [ ] Conclusions actionable and clear
- [ ] References cited appropriately
- [ ] No typos or grammatical errors
- [ ] Figures have descriptive captions
- [ ] Data visualizations are clear and honest
- [ ] Statistical significance properly indicated

## Evidence-Based Design Recommendations

Research on poster effectiveness shows:

**Findings from Studies**:
1. **Viewers spend 3-5 minutes average** on posters
   - Design for scanning, not deep reading
   - Most important info must be visible immediately

2. **Visual content processed 60,000× faster** than text
   - Use figures, not paragraphs, to convey key findings
   - Images attract attention first

3. **High contrast improves recall** by 40%
   - Dark on light > light on dark for comprehension
   - Color contrast aids memory retention

4. **White space increases comprehension** by 20%
   - Don't fear empty space
   - Margins and padding are essential

5. **Three-column layouts most effective** for portrait posters
   - Balanced visual weight
   - Natural reading flow

6. **QR codes increase engagement** by 30%
   - Provide digital access to full paper
   - Link to videos, code repositories, data

## Resources and Tools

### Color Tools
- **Coolors.co**: Generate color palettes
- **Adobe Color**: Color wheel and accessibility checker
- **ColorBrewer**: Scientific visualization palettes
- **WebAIM Contrast Checker**: Test contrast ratios

### Design Resources
- **Canva**: Poster mockups and inspiration
- **Figma**: Design prototypes before LaTeX
- **Noun Project**: Icons and graphics
- **Font Awesome**: Icon fonts for LaTeX

### Testing Tools
- **Coblis**: Color blindness simulator
- **Vischeck**: Another color blindness checker
- **Accessibility Checker**: WCAG compliance

### LaTeX Packages
- `xcolor`: Extended color support
- `tcolorbox`: Colored boxes and frames
- `fontawesome5`: Icon fonts
- `qrcode`: QR code generation
- `tikz`: Custom graphics

## Conclusion

Effective poster design requires balancing aesthetics, readability, and scientific content. Follow these core principles:

1. **Less is more**: Prioritize key messages over comprehensive detail
2. **Size matters**: Make text large enough to read from distance
3. **Contrast is critical**: Ensure all text is highly readable
4. **Accessibility first**: Design for diverse audiences
5. **Visual hierarchy**: Guide viewers through content logically
6. **Test early**: Print at reduced scale and gather feedback

Remember: A poster is an advertisement for your research and a conversation starter—not a substitute for reading the full paper.

### `references/poster_layout_design.md`

# Poster Layout and Design Guide

## Overview

Effective poster layout organizes content for maximum impact and comprehension. This guide covers grid systems, spatial organization, visual flow, and layout patterns for research posters.

## Grid Systems and Column Layouts

### Common Grid Patterns

#### 1. Two-Column Layout

**Characteristics**:
- Simple, traditional structure
- Easy to design and execute
- Clear narrative flow
- Good for text-heavy content
- Best for A1 size or smaller

**Content Organization**:
```
+-------------------------+
|       Title/Header      |
+-------------------------+
| Column 1  | Column 2    |
|           |             |
| Intro     | Results     |
|           |             |
| Methods   | Discussion  |
|           |             |
|           | Conclusions |
+-------------------------+
|    References/Contact   |
+-------------------------+
```

**LaTeX Implementation (beamerposter)**:
```latex
\begin{columns}[t]
  \begin{column}{.48\linewidth}
    \begin{block}{Introduction}
      % Content
    \end{block}
    \begin{block}{Methods}
      % Content
    \end{block}
  \end{column}
  
  \begin{column}{.48\linewidth}
    \begin{block}{Results}
      % Content
    \end{block}
    \begin{block}{Conclusions}
      % Content
    \end{block}
  \end{column}
\end{columns}
```

**Best For**:
- Small posters (A1, A2)
- Narrative-heavy content
- Simple comparisons (before/after, control/treatment)
- Linear storytelling

**Limitations**:
- Limited space for multiple results
- Can appear basic or dated
- Less visual variety

#### 2. Three-Column Layout (Most Popular)

**Characteristics**:
- Balanced, professional appearance
- Optimal for A0 posters
- Versatile content distribution
- Natural visual rhythm
- Industry standard

**Content Organization**:
```
+--------------------------------+
|          Title/Header          |
+--------------------------------+
| Column 1  | Column 2 | Column 3|
|           |          |         |
| Intro     | Results  | Results |
|           | (Fig 1)  | (Fig 2) |
| Methods   |          |         |
|           | Results  | Discuss |
| Methods   | (Fig 3)  |         |
| (cont.)   |          | Concl.  |
+--------------------------------+
|     Acknowledgments/Refs       |
+--------------------------------+
```

**LaTeX Implementation (tikzposter)**:
```latex
\begin{columns}
  \column{0.33}
  \block{Introduction}{...}
  \block{Methods}{...}
  
  \column{0.33}
  \block{Results Part 1}{...}
  \block{Results Part 2}{...}
  
  \column{0.33}
  \block{Results Part 3}{...}
  \block{Discussion}{...}
  \block{Conclusions}{...}
\end{columns}
```

**Best For**:
- Standard A0 conference posters
- Multiple results/figures (4-6)
- Balanced content distribution
- Professional academic presentations

**Strengths**:
- Visual balance and symmetry
- Adequate space for text and figures
- Clear section delineation
- Easy to scan left-to-right

#### 3. Four-Column Layout

**Characteristics**:
- Information-dense
- Modern, structured appearance
- Best for large posters (>A0)
- Requires careful design
- More complex to balance

**Content Organization**:
```
+----------------------------------------+
|             Title/Header               |
+----------------------------------------+
| Col 1  | Col 2  | Col 3    | Col 4    |
|        |        |          |          |
| Intro  | Method | Results  | Results  |
|        | (Flow) | (Fig 1)  | (Fig 3)  |
| Motiv. |        |          |          |
|        | Method | Results  | Discuss. |
| Hypoth.| (Stats)| (Fig 2)  |          |
|        |        |          | Concl.   |
+----------------------------------------+
|          References/Contact            |
+----------------------------------------+
```

**LaTeX Implementation (baposter)**:
```latex
\begin{poster}{columns=4, colspacing=1em, ...}
  
  \headerbox{Intro}{name=intro, column=0, row=0}{...}
  \headerbox{Methods}{name=methods, column=1, row=0}{...}
  \headerbox{Results 1}{name=res1, column=2, row=0}{...}
  \headerbox{Results 2}{name=res2, column=3, row=0}{...}
  
  % Continue with below=... for stacking
  
\end{poster}
```

**Best For**:
- Large format posters (48×72")
- Data-heavy presentations
- Comparison studies (multiple conditions)
- Engineering/technical posters

**Challenges**:
- Can appear crowded
- Requires more white space management
- Harder to achieve visual balance
- Risk of overwhelming viewers

#### 4. Asymmetric Layouts

**Characteristics**:
- Dynamic, modern appearance
- Flexible content arrangement
- Emphasizes hierarchy
- Requires design expertise
- Best for creative fields

**Example Pattern**:
```
+--------------------------------+
|          Title/Header          |
+--------------------------------+
| Wide Column  | Narrow Column   |
| (66%)        | (33%)           |
|              |                 |
| Intro +      | Key             |
| Methods      | Figure          |
| (narrative)  | (emphasized)    |
|              |                 |
+--------------------------------+
| Results (spanning full width)  |
+--------------------------------+
| Discussion   | Conclusions     |
| (50%)        | (50%)           |
+--------------------------------+
```

**LaTeX Implementation (tikzposter)**:
```latex
\begin{columns}
  \column{0.65}
  \block{Introduction and Methods}{
    % Combined narrative section
  }
  
  \column{0.35}
  \block{}{
    % Key figure with minimal text
    \includegraphics[width=\linewidth]{key-figure.pdf}
  }
\end{columns}

\block[width=1.0\linewidth]{Results}{
  % Full-width results section
}
```

**Best For**:
- Design-oriented conferences
- Single key finding with supporting content
- Modern, non-traditional fields
- Experienced poster designers

### Grid Alignment Principles

**Baseline Grid**:
- Establish invisible horizontal lines
- Align all text blocks to grid
- Typical spacing: 5mm or 10mm increments
- Creates visual rhythm and professionalism

**Column Grid**:
- Divide width into equal units (12, 16, or 24 units common)
- Elements span multiple units
- Allows flexible but structured layouts

**Example 12-Column Grid**:
```
| 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |10 |11 |12 |
|-------|-------|-------|-------|-------|-------|
| Block spanning 6 units| Block spanning 6 units|
|               Block spanning 12 units          |
| 4 units  | 8 units (emphasized)               |
```

**LaTeX Grid Helper**:
```latex
% Debug grid overlay (remove for final version)
\usepackage{tikz}
\AddToShipoutPictureBG{
  \begin{tikzpicture}[remember picture, overlay]
    \draw[help lines, step=5cm, very thin, gray!30] 
      (current page.south west) grid (current page.north east);
  \end{tikzpicture}
}
```

## Visual Flow and Reading Patterns

### Z-Pattern (Landscape Posters)

Viewers' eyes naturally follow a Z-shape on landscape layouts:

```
START → → → → → → → → → → → → → → TOP RIGHT
  ↓                                    ↓
  ↓                                    ↓
MIDDLE LEFT → → → → → → → → → MIDDLE RIGHT
  ↓                                    ↓
  ↓                                    ↓
BOTTOM LEFT → → → → → → → → → → → → END
```

**Design Strategy**:
1. **Top-left**: Title and introduction (entry point)
2. **Top-right**: Institution logo, QR code
3. **Center**: Key result or main figure
4. **Bottom-right**: Conclusions and contact (exit point)

**Content Placement**:
- Critical information at corners and center
- Support information along diagonal paths
- Use arrows or visual cues to reinforce flow

### F-Pattern (Portrait Posters)

Portrait posters follow F-shaped eye movement:

```
TITLE → → → → → → → → → → → →
  ↓
INTRO → → → →
  ↓
METHODS
  ↓
RESULTS → → →
  ↓
RESULTS (cont.)
  ↓
DISCUSSION
  ↓
CONCLUSIONS → → → → → → → → →
```

**Design Strategy**:
1. Place engaging content at top-left
2. Use section headers to create horizontal scan points
3. Most important figures in upper-middle area
4. Conclusions visible without scrolling (if digital) or from distance

### Gutenberg Diagram

Classic newspaper layout principle:

```
+------------------+------------------+
| PRIMARY AREA     | STRONG FALLOW    |
| (most attention) | (moderate attn)  |
|   ↓              |        ↓         |
+------------------+------------------+
| WEAK FALLOW      | TERMINAL AREA    |
| (least attention)| (final resting)  |
|                  |        ↑         |
+------------------+------------------+
```

**Optimization**:
- **Primary Area** (top-left): Introduction, problem statement
- **Strong Fallow** (top-right): Supporting figure, logo
- **Weak Fallow** (bottom-left): Methods details, references
- **Terminal Area** (bottom-right): Conclusions, take-home message

### Directional Cues

Guide viewers explicitly through content:

**Numerical Ordering**:
```latex
\block{❶ Introduction}{...}
\block{❷ Methods}{...}
\block{❸ Results}{...}
\block{❹ Conclusions}{...}
```

**Arrows and Lines**:
```latex
\begin{tikzpicture}
  \node[block] (intro) {Introduction};
  \node[block, right=of intro] (methods) {Methods};
  \node[block, right=of methods] (results) {Results};
  \draw[->, thick, blue] (intro) -- (methods);
  \draw[->, thick, blue] (methods) -- (results);
\end{tikzpicture}
```

**Color Progression**:
- Light to dark shades indicating progression
- Cool to warm colors showing importance increase
- Consistent color for related sections

## Spatial Organization Strategies

### Header/Title Area

**Typical Size**: 10-15% of total poster height

**Essential Elements**:
- **Title**: Concise, descriptive (10-15 words max)
- **Authors**: Full names, presenting author emphasized
- **Affiliations**: Institutions, departments
- **Logos**: University, funding agencies (2-4 max)
- **Conference info** (optional): Name, date, location

**Layout Options**:

**Centered**:
```
+----------------------------------------+
|  [Logo]    POSTER TITLE HERE    [Logo]|
|         Authors and Affiliations       |
|           email@university.edu         |
+----------------------------------------+
```

**Left-aligned**:
```
+----------------------------------------+
| POSTER TITLE HERE            [Logo]   |
| Authors and Affiliations     [Logo]   |
+----------------------------------------+
```

**Split**:
```
+----------------------------------------+
| [Logo]           | Authors & Affil.    |
| POSTER TITLE     | email@edu          |
|                  | [QR Code]          |
+----------------------------------------+
```

**LaTeX Header (beamerposter)**:
```latex
\begin{columns}[T]
  \begin{column}{.15\linewidth}
    \includegraphics[width=\linewidth]{logo1.pdf}
  \end{column}
  
  \begin{column}{.7\linewidth}
    \centering
    {\VeryHuge\textbf{Your Research Title Here}}\\[0.5cm]
    {\Large Author One\textsuperscript{1}, Author Two\textsuperscript{2}}\\[0.3cm]
    {\normalsize \textsuperscript{1}University A, \textsuperscript{2}University B}
  \end{column}
  
  \begin{column}{.15\linewidth}
    \includegraphics[width=\linewidth]{logo2.pdf}
  \end{column}
\end{columns}
```

### Main Content Area

**Typical Size**: 70-80% of total poster

**Organization Principles**:

**1. Top-to-Bottom Flow**:
```
Introduction/Background
        ↓
Methods/Approach
        ↓
Results (Multiple panels)
        ↓
Discussion/Conclusions
```

**2. Left-to-Right, Top-to-Bottom**:
```
[Intro] [Results 1] [Results 3]
[Methods] [Results 2] [Discussion]
```

**3. Centralized Main Figure**:
```
[Intro]  [Main Figure]  [Discussion]
[Methods]   (center)    [Conclusions]
```

**Section Sizing**:
- Introduction: 10-15% of content area
- Methods: 15-20%
- Results: 40-50% (largest section)
- Discussion/Conclusions: 15-20%

### Footer Area

**Typical Size**: 5-10% of total poster height

**Common Elements**:
- References (abbreviated, 5-10 key citations)
- Acknowledgments (funding, collaborators)
- Contact information
- QR codes (paper, code, data)
- Social media handles (optional)
- Conference hashtags

**Layout**:
```
+----------------------------------------+
| References: 1. Author (2023) ... |  📱  |
| Acknowledgments: Funded by ...   | QR   |
| Contact: name@email.edu          | Code |
+----------------------------------------+
```

**LaTeX Footer**:
```latex
\begin{block}{}
  \footnotesize
  \begin{columns}[T]
    \begin{column}{0.7\linewidth}
      \textbf{References}
      \begin{enumerate}
        \item Author A et al. (2023). Journal. doi:...
        \item Author B et al. (2024). Conference.
      \end{enumerate}
      
      \textbf{Acknowledgments}
      This work was supported by Grant XYZ.
      
      \textbf{Contact}: firstname.lastname@university.edu
    \end{column}
    
    \begin{column}{0.25\linewidth}
      \centering
      \qrcode[height=3cm]{https://doi.org/10.1234/paper}\\
      \tiny Scan for full paper
    \end{column}
  \end{columns}
\end{block}
```

## White Space Management

### Margins and Padding

**Outer Margins**:
- Minimum: 2-3cm (0.75-1 inch)
- Recommended: 3-5cm (1-2 inches)
- Prevents edge trimming issues in printing
- Provides visual breathing room

**Inner Spacing**:
- Between columns: 1-2cm
- Between blocks: 1-2cm
- Inside blocks (padding): 0.5-1.5cm
- Around figures: 0.5-1cm

**LaTeX Margin Control**:
```latex
% beamerposter
\usepackage[size=a0, scale=1.4]{beamerposter}
\setbeamersize{text margin left=3cm, text margin right=3cm}

% tikzposter
\documentclass[..., margin=30mm, innermargin=15mm]{tikzposter}

% baposter
\begin{poster}{
  colspacing=1.5em,  % Horizontal spacing
  ...
}
```

### Active White Space vs. Passive White Space

**Active White Space**: Intentionally placed for specific purpose
- Around key figures (draws attention)
- Between major sections (creates clear separation)
- Above/below titles (emphasizes hierarchy)

**Passive White Space**: Natural result of layout
- Margins and borders
- Line spacing
- Gaps between elements

**Balance**: Aim for 30-40% white space overall

### Visual Breathing Room

**Avoid**:
- ❌ Elements touching edges
- ❌ Text blocks directly adjacent
- ❌ Figures without surrounding space
- ❌ Cramped, claustrophobic feel

**Implement**:
- ✅ Clear separation between sections
- ✅ Space around focal points
- ✅ Generous padding inside boxes
- ✅ Balanced distribution of content

## Block and Box Design

### Block Types and Functions

**Title Block**: Poster header
- Full width, top position
- High visual weight
- Contains identifying information

**Content Blocks**: Main sections
- Column-based or free-floating
- Hierarchical sizing (larger = more important)
- Clear headers and structure

**Callout Blocks**: Emphasized information
- Key findings or quotes
- Different color or style
- Visually distinct

**Reference Blocks**: Supporting info
- Footer position
- Smaller, less prominent
- Informational, not critical

### Block Styling Options

**Border Styles**:
```latex
% Rounded corners (friendly, modern)
\begin{block}{Title}
  % beamerposter with rounded
  \setbeamertemplate{block begin}[rounded]
  
% Sharp corners (formal, traditional)
  \setbeamertemplate{block begin}[default]

% No border (minimal, clean)
  \setbeamercolor{block title}{bg=white, fg=black}
  \setbeamercolor{block body}{bg=white, fg=black}
```

**Shadow and Depth**:
```latex
% tikzposter shadow
\tikzset{
  block/.append style={
    drop shadow={shadow xshift=2mm, shadow yshift=-2mm}
  }
}

% tcolorbox drop shadow
\usepackage{tcolorbox}
\begin{tcolorbox}[enhanced, drop shadow]
  Content with shadow
\end{tcolorbox}
```

**Background Shading**:
- **Solid**: Clean, professional
- **Gradient**: Modern, dynamic
- **Transparent**: Layered, sophisticated

### Relationship and Grouping

**Visual Grouping Techniques**:

**1. Proximity**: Place related items close
```
[Intro Text]
[Related Figure]
    ↓ grouped
[Methods Text]
[Methods Diagram]
```

**2. Color Coding**: Use color to show relationships
- All "Methods" blocks in blue
- All "Results" blocks in green
- Conclusions in orange

**3. Borders**: Enclose related elements
```latex
\begin{tcolorbox}[title=Experimental Pipeline]
  \begin{enumerate}
    \item Sample preparation
    \item Data collection
    \item Analysis
  \end{enumerate}
\end{tcolorbox}
```

**4. Alignment**: Aligned elements appear related
```
[Block A Left-aligned]
[Block B Left-aligned]
    vs.
[Block C Centered]
```

## Responsive and Adaptive Layouts

### Designing for Different Poster Sizes

**Scaling Strategy**:
- Design for target size (e.g., A0)
- Test at other common sizes (A1, 36×48")
- Use relative sizing (percentages, not absolute)

**Font Scaling**:
```latex
% Scale fonts proportionally
\usepackage[size=a0, scale=1.4]{beamerposter}  % A0 at 140%
\usepackage[size=a1, scale=1.0]{beamerposter}  % A1 at 100%

% Or define sizes relatively
\newcommand{\titlesize}{\fontsize{96}{110}\selectfont}
\newcommand{\headersize}{\fontsize{60}{72}\selectfont}
```

**Content Adaptation**:
- **A0 (full)**: All content, 5-6 figures
- **A1 (reduced)**: Condense to 3-4 main figures
- **A2 (compact)**: Key finding only, 1-2 figures

### Portrait vs. Landscape Orientation

**Portrait (Vertical)**:
- **Pros**: Traditional, more common stands, natural reading flow
- **Cons**: Less width for figures, can feel cramped
- **Best for**: Text-heavy posters, multi-section flow, conferences

**Landscape (Horizontal)**:
- **Pros**: Wide figures, natural for timelines, modern feel
- **Cons**: Harder to read from distance, less common
- **Best for**: Timelines, wide data visualizations, non-traditional venues

**LaTeX Orientation**:
```latex
% Portrait
\usepackage[size=a0, orientation=portrait]{beamerposter}
\documentclass[..., portrait]{tikzposter}

% Landscape
\usepackage[size=a0, orientation=landscape]{beamerposter}
\documentclass[..., landscape]{tikzposter}
```

## Layout Patterns by Research Type

### Experimental Research

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Background | Methods      |
| Problem    | (Diagram)    |
+---------------------------+
| Results (Figure 1)        |
| Results (Figure 2)        |
+---------------------------+
| Discussion | Conclusions  |
| Limitations| Future Work  |
+---------------------------+
[References and Contact]
```

**Emphasis**: Visual results, clear methodology

### Computational/Modeling

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Motivation | Algorithm    |
|            | (Flowchart)  |
+---------------------------+
| Implementation Details    |
+---------------------------+
| Results    | Results      |
| (Benchmark)| (Comparison) |
+---------------------------+
| Conclusions| Code QR      |
+---------------------------+
[GitHub, Docker, Documentation]
```

**Emphasis**: Algorithm clarity, reproducibility

### Clinical/Medical

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Background | Methods      |
| Clinical   | - Design     |
| Need       | - Population |
|            | - Outcomes   |
+---------------------------+
| Results               |    |
| (Primary Outcome)     | Key|
|                       | Fig|
+---------------------------+
| Discussion | Clinical     |
|            | Implications |
+---------------------------+
[Trial Registration, Ethics, Funding]
```

**Emphasis**: Patient outcomes, clinical relevance

### Review/Meta-Analysis

**Typical Flow**:
```
[Title and Authors]
+---------------------------+
| Research  | Search        |
| Question  | Strategy      |
|           | (PRISMA Flow) |
+---------------------------+
| Included Studies Overview |
+---------------------------+
| Findings  | Findings      |
| (Theme 1) | (Theme 2)     |
+---------------------------+
| Synthesis | Gaps &        |
|           | Future Needs  |
+---------------------------+
[Systematic Review Registration]
```

**Emphasis**: Comprehensive coverage, synthesis

## Layout Testing and Iteration

### Design Iteration Process

**1. Sketch Phase**:
- Hand-draw rough layout
- Experiment with different arrangements
- Mark primary, secondary, tertiary content

**2. Digital Mockup**:
- Create low-fidelity version in LaTeX
- Use placeholder text/figures
- Test different grid systems

**3. Content Integration**:
- Replace placeholders with actual content
- Adjust spacing and sizing
- Refine visual hierarchy

**4. Refinement**:
- Fine-tune alignment
- Balance visual weight
- Optimize white space

**5. Testing**:
- Print at reduced scale (25%)
- View from distance
- Get colleague feedback

### Feedback Checklist

**Visual Balance**:
- [ ] No single area feels too heavy or too light
- [ ] Color distributed evenly across poster
- [ ] Text and figures balanced
- [ ] White space well-distributed

**Hierarchy and Flow**:
- [ ] Clear entry point (title visible)
- [ ] Logical reading path
- [ ] Section relationships clear
- [ ] Conclusions easy to find

**Technical Execution**:
- [ ] Consistent alignment
- [ ] Uniform spacing
- [ ] Professional appearance
- [ ] No awkward breaks or orphans

## Common Layout Mistakes

**1. Unbalanced Visual Weight**
- ❌ All content on left, empty right side
- ❌ Large figure dominating, tiny text elsewhere
- ✅ Distribute content evenly across poster

**2. Inconsistent Spacing**
- ❌ Random gaps between blocks
- ❌ Elements touching in some places, spaced in others
- ✅ Use consistent spacing values throughout

**3. Poor Column Width**
- ❌ Extremely narrow columns (hard to read)
- ❌ Very wide columns (eye tracking difficult)
- ✅ Optimal: 40-80 characters per line

**4. Ignoring Grid**
- ❌ Random placement of elements
- ❌ Misaligned blocks
- ✅ Align to invisible grid, consistent positioning

**5. Overcrowding**
- ❌ No white space, cramped feel
- ❌ Trying to fit too much content
- ✅ Generous margins, clear separation

## Conclusion

Effective layout design:
- Uses appropriate grid systems (2, 3, or 4 columns)
- Follows natural eye movement patterns
- Maintains visual balance and hierarchy
- Provides adequate white space
- Groups related content clearly
- Adapts to different poster sizes and orientations

Remember: Layout should support content, not compete with it. When viewers focus on your research rather than your design, you've succeeded.

### `references/poster_patterns_and_presentation.md`

# Poster Patterns, Accessibility, and Presentation

Reusable content patterns per poster section, accessibility and inclusive-design
requirements, and how to present the poster on the day.

### 11. Common Poster Content Patterns

Effective content organization for different research types:

**Experimental Research Poster**:
1. Title and authors
2. Introduction: Problem and hypothesis
3. Methods: Experimental design (with diagram)
4. Results: Key findings (2-4 main figures)
5. Conclusions: Main takeaways (3-5 bullet points)
6. Future work (optional)
7. References and acknowledgments

**Computational/Modeling Poster**:
1. Title and authors
2. Motivation: Problem statement
3. Approach: Algorithm or model (with flowchart)
4. Implementation: Technical details
5. Results: Performance metrics and comparisons
6. Applications: Use cases
7. Code availability (QR code to GitHub)
8. References

**Review/Survey Poster**:
1. Title and authors
2. Scope: Topic overview
3. Methods: Literature search strategy
4. Key findings: Main themes (organized by category)
5. Trends: Visualizations of publication patterns
6. Gaps: Identified research needs
7. Conclusions: Summary and implications
8. References

### 12. Accessibility and Inclusive Design

Design posters that are accessible to diverse audiences:

**Color Blindness Considerations**:
- Avoid red-green combinations (most common color blindness)
- Use patterns or shapes in addition to color
- Test with color-blindness simulators
- Provide high contrast (WCAG AA standard: 4.5:1 minimum)

**Visual Impairment Accommodations**:
- Large, clear fonts (minimum 24pt body text)
- High contrast text and background
- Clear visual hierarchy
- Avoid complex textures or patterns in backgrounds

**Language and Content**:
- Clear, concise language
- Define acronyms and jargon
- International audience considerations
- Consider multilingual QR code options for global conferences

### 13. Poster Presentation Best Practices

Guidance beyond LaTeX for effective poster sessions:

**Content Strategy**:
- Tell a story, don't just list facts
- Focus on 1-3 main messages
- Use visual abstract or graphical summary
- Leave room for conversation (don't over-explain)

**Physical Presentation Tips**:
- Bring printed handouts or business cards with QR code
- Prepare 30-second, 2-minute, and 5-minute verbal summaries
- Stand to the side, not blocking the poster
- Engage viewers with open-ended questions

**Digital Backups**:
- Save poster as PDF on mobile device
- Prepare digital version for email sharing
- Create social media-friendly image version
- Have backup printed copy or digital display option

### `scripts/generate_schematic.py`

```python
#!/usr/bin/env python3
"""
Scientific schematic generation using Nano Banana 2.

Generate any scientific diagram by describing it in natural language.
Nano Banana 2 handles everything automatically with smart iterative refinement.

Smart iteration: Only regenerates if quality is below threshold for your document type.
Quality review: Uses Gemini 3.6 Flash for professional scientific evaluation.

Usage:
    # Generate for journal paper (highest quality threshold)
    python generate_schematic.py "CONSORT flowchart" -o flowchart.png --doc-type journal
    
    # Generate for presentation (lower threshold, faster)
    python generate_schematic.py "Transformer architecture" -o transformer.png --doc-type presentation
    
    # Generate for poster
    python generate_schematic.py "MAPK signaling pathway" -o pathway.png --doc-type poster
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Variables forwarded to the generation subprocess. The child needs the
# OpenRouter credential; the rest keep networking, TLS, and locale working.
# Copying the whole parent environment instead would hand the child every
# unrelated secret that happens to be exported in the calling shell.
FORWARDED_ENV_VARS = (
    "PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH",
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "no_proxy",
    "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE",
    # Windows needs these for sockets, temp files, and interpreter startup.
    "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT",
    "APPDATA", "LOCALAPPDATA", "USERPROFILE", "TEMP", "TMP",
)


def resolve_api_key(explicit=None):
    """Resolve the OpenRouter key from --api-key, the environment, then any .env file.

    The .env scan walks up from the working directory and finally checks the
    script's own directory, so running from anywhere inside a project picks up
    the key at its root. The child process is handed the resolved value through
    build_subprocess_env, so it never has to repeat this search.
    """
    if explicit:
        return explicit

    from_env = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if from_env:
        return from_env

    cwd = Path.cwd()
    for directory in [cwd, *cwd.parents, Path(__file__).resolve().parent]:
        env_file = directory / ".env"
        if not env_file.is_file():
            continue
        try:
            content = env_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for raw in content.splitlines():
            line = raw.strip()
            if line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "OPENROUTER_API_KEY":
                value = value.strip().strip('"').strip("'")
                if value:
                    return value

    return None


def build_subprocess_env(api_key):
    """Return a minimal environment for the AI generation subprocess."""
    env = {name: os.environ[name] for name in FORWARDED_ENV_VARS if name in os.environ}
    if api_key:
        env["OPENROUTER_API_KEY"] = api_key
    return env


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate scientific schematics using AI with smart iterative refinement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
How it works:
  Simply describe your diagram in natural language
  Nano Banana 2 generates it automatically with:
  - Smart iteration (only regenerates if quality is below threshold)
  - Quality review by Gemini 3.6 Flash
  - Document-type aware quality thresholds
  - Publication-ready output

Document Types (quality thresholds):
  journal      8.5/10  - Nature, Science, peer-reviewed journals
  conference   8.0/10  - Conference papers
  thesis       8.0/10  - Dissertations, theses
  grant        8.0/10  - Grant proposals
  preprint     7.5/10  - arXiv, bioRxiv, etc.
  report       7.5/10  - Technical reports
  poster       7.0/10  - Academic posters
  presentation 6.5/10  - Slides, talks
  default      7.5/10  - General purpose

Examples:
  # Generate for journal paper (strict quality)
  python generate_schematic.py "CONSORT participant flow" -o flowchart.png --doc-type journal
  
  # Generate for poster (moderate quality)
  python generate_schematic.py "Transformer architecture" -o arch.png --doc-type poster
  
  # Generate for slides (faster, lower threshold)
  python generate_schematic.py "System diagram" -o system.png --doc-type presentation
  
  # Custom max iterations
  python generate_schematic.py "Complex pathway" -o pathway.png --iterations 2
  
  # Verbose output
  python generate_schematic.py "Circuit diagram" -o circuit.png -v

Environment Variables:
  OPENROUTER_API_KEY    Required for AI generation
        """
    )
    
    parser.add_argument("prompt", 
                       help="Description of the diagram to generate")
    parser.add_argument("-o", "--output", required=True,
                       help="Output file path")
    parser.add_argument("--doc-type", default="default",
                       choices=["journal", "conference", "poster", "presentation",
                               "report", "grant", "thesis", "preprint", "default"],
                       help="Document type for quality threshold (default: default)")
    parser.add_argument("--iterations", type=int, default=2,
                       help="Maximum refinement iterations (default: 2, max: 2)")
    parser.add_argument("--api-key", 
                       help="OpenRouter API key (or use OPENROUTER_API_KEY env var)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()

    # Validated here rather than clamped silently, and before the credential
    # lookup so an out-of-range value reports itself rather than an absent key.
    if not 1 <= args.iterations <= 2:
        parser.error("--iterations must be 1 or 2")

    # Check for API key — resolves --api-key, the environment, then any .env file
    api_key = resolve_api_key(args.api_key)
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found")
        print("\nFor AI generation, you need an OpenRouter API key.")
        print("Get one at: https://openrouter.ai/keys")
        print("\nSet it with:")
        print("  export OPENROUTER_API_KEY='your_api_key'")
        print("\nOr add OPENROUTER_API_KEY=your_api_key to a .env file")
        print("Or use --api-key flag")
        sys.exit(1)
    
    # Find AI generation script
    script_dir = Path(__file__).parent
    ai_script = script_dir / "generate_schematic_ai.py"
    
    if not ai_script.exists():
        print(f"Error: AI generation script not found: {ai_script}")
        sys.exit(1)
    
    # Build command
    cmd = [sys.executable, str(ai_script), args.prompt, "-o", args.output]
    
    if args.doc_type != "default":
        cmd.extend(["--doc-type", args.doc_type])

    cmd.extend(["--iterations", str(args.iterations)])

    if args.verbose:
        cmd.append("-v")
    
    # Execute — pass API key via environment to avoid exposure in process listings
    try:
        result = subprocess.run(cmd, check=False, env=build_subprocess_env(api_key))
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error executing AI generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### `scripts/generate_schematic_ai.py`

```python
#!/usr/bin/env python3
"""
AI-powered scientific schematic generation using Nano Banana 2.

This script uses a smart iterative refinement approach:
1. Generate initial image with Nano Banana 2
2. AI quality review using Gemini 3.6 Flash for scientific critique
3. Only regenerate if quality is below threshold for document type
4. Repeat until quality meets standards (max iterations)

Requirements:
    - OPENROUTER_API_KEY environment variable
    - requests library

Usage:
    python generate_schematic_ai.py "Create a flowchart showing CONSORT participant flow" -o flowchart.png
    python generate_schematic_ai.py "Neural network architecture diagram" -o architecture.png --iterations 2
    python generate_schematic_ai.py "Simple block diagram" -o diagram.png --doc-type poster
"""

import argparse
import base64
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, NamedTuple

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: uv pip install requests")
    sys.exit(1)


class ReviewResult(NamedTuple):
    """The outcome of one quality review.

    A named tuple rather than a bare tuple because the review has several
    failure modes -- the model returns no choices, the request raises, the
    answer arrives in an unexpected shape -- and each of them used to be a
    chance to return the wrong number of values to the caller.

    `score` is None whenever no usable number was parsed, and `reviewed` is
    False whenever the review never produced an answer at all. Neither case
    invents a score: a diagram whose quality was not measured is reported as
    unmeasured, not as passing.
    """

    critique: str
    score: Optional[float]
    needs_improvement: bool
    reviewed: bool
    error: Optional[str] = None


# Markdown decoration the reviewer routinely wraps its answer in. Gemini writes
# "**SCORE:** 8.5" far more often than the bare "SCORE: 8.5" the rubric asks
# for, and a pattern that does not allow for it silently scores every diagram
# at whatever the default happens to be.
_MARKUP = re.compile(r"[*_`#]")

_SCORE_PATTERN = re.compile(r"\bSCORE\s*:?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
_LOOSE_SCORE_PATTERN = re.compile(
    r"(?:score|rating|quality)\s*[:\s]\s*(\d+(?:\.\d+)?)\s*(?:/\s*10)?", re.IGNORECASE
)
# The underscore is optional because normalization strips it out of
# NEEDS_IMPROVEMENT along with the surrounding markdown.
_VERDICT_PATTERN = re.compile(
    r"^\s*VERDICT\s*:?\s*(ACCEPTABLE|NEEDS[_ ]?IMPROVEMENT)", re.IGNORECASE | re.MULTILINE
)


def _normalize_review_text(text: str) -> str:
    """Strip markdown decoration so the rubric's fields can be found."""
    return _MARKUP.sub("", text or "")


def _parse_score(text: str) -> Optional[float]:
    """Return the reviewer's 0-10 score, or None when there isn't a usable one.

    None rather than a default: a fabricated score is indistinguishable from a
    real one once it reaches the review log, and a default near the middle of
    the range quietly passes lenient document types while failing strict ones.
    """
    normalized = _normalize_review_text(text)
    match = _SCORE_PATTERN.search(normalized) or _LOOSE_SCORE_PATTERN.search(normalized)
    if not match:
        return None
    score = float(match.group(1))
    # A number outside the rubric's range means something other than the score
    # was matched -- a figure count, a percentage, an iteration number.
    return score if 0.0 <= score <= 10.0 else None


def _parse_verdict(text: str) -> Optional[str]:
    """Return ACCEPTABLE / NEEDS_IMPROVEMENT from the verdict line, or None.

    Anchored to the start of a line. The rubric prompt spells out both tokens
    when it explains the response format, so a reviewer that echoes those
    instructions back would fail a perfectly good diagram under a plain
    substring search.
    """
    match = _VERDICT_PATTERN.search(_normalize_review_text(text))
    if not match:
        return None
    verdict = match.group(1).upper().replace(" ", "").replace("_", "")
    return "NEEDS_IMPROVEMENT" if verdict == "NEEDSIMPROVEMENT" else "ACCEPTABLE"


def _resolve_api_key(explicit: Optional[str] = None) -> Optional[str]:
    """Resolve the OpenRouter key from --api-key, the environment, then any .env file.

    The .env scan walks up from the working directory and finally checks the
    script's own directory, so running from anywhere inside a project picks up
    the key at its root. Only the standard library is used: python-dotenv is a
    common omission, and a missing optional dependency should not read as a
    missing credential.
    """
    if explicit:
        return explicit

    from_env = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if from_env:
        return from_env

    cwd = Path.cwd()
    for directory in [cwd, *cwd.parents, Path(__file__).resolve().parent]:
        env_file = directory / ".env"
        if not env_file.is_file():
            continue
        try:
            content = env_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for raw in content.splitlines():
            line = raw.strip()
            if line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == "OPENROUTER_API_KEY":
                value = value.strip().strip('"').strip("'")
                if value:
                    return value

    return None


class ScientificSchematicGenerator:
    """Generate scientific schematics using AI with smart iterative refinement.
    
    Uses Gemini 3.6 Flash for quality review to determine if regeneration is needed.
    Multiple passes only occur if the generated schematic doesn't meet the
    quality threshold for the target document type.
    """
    
    # Quality thresholds by document type (score out of 10)
    # Higher thresholds for more formal publications
    QUALITY_THRESHOLDS = {
        "journal": 8.5,      # Nature, Science, etc. - highest standards
        "conference": 8.0,   # Conference papers - high standards
        "poster": 7.0,       # Academic posters - good quality
        "presentation": 6.5, # Slides/talks - clear but less formal
        "report": 7.5,       # Technical reports - professional
        "grant": 8.0,        # Grant proposals - must be compelling
        "thesis": 8.0,       # Dissertations - formal academic
        "preprint": 7.5,     # arXiv, etc. - good quality
        "default": 7.5,      # Default threshold
    }
    
    # Scientific diagram best practices prompt template
    SCIENTIFIC_DIAGRAM_GUIDELINES = """
Create a high-quality scientific diagram with these requirements:

VISUAL QUALITY:
- Clean white or light background (no textures or gradients)
- High contrast for readability and printing
- Professional, publication-ready appearance
- Sharp, clear lines and text
- Adequate spacing between elements to prevent crowding

TYPOGRAPHY:
- Clear, readable sans-serif fonts (Arial, Helvetica style)
- Minimum 10pt font size for all labels
- Consistent font sizes throughout
- All text horizontal or clearly readable
- No overlapping text

SCIENTIFIC STANDARDS:
- Accurate representation of concepts
- Clear labels for all components
- Include scale bars, legends, or axes where appropriate
- Use standard scientific notation and symbols
- Include units where applicable

ACCESSIBILITY:
- Colorblind-friendly color palette (use Okabe-Ito colors if using color)
- High contrast between elements
- Redundant encoding (shapes + colors, not just colors)
- Works well in grayscale

LAYOUT:
- Logical flow (left-to-right or top-to-bottom)
- Clear visual hierarchy
- Balanced composition
- Appropriate use of whitespace
- No clutter or unnecessary decorative elements

IMPORTANT - NO FIGURE NUMBERS:
- Do NOT include "Figure 1:", "Fig. 1", or any figure numbering in the image
- Do NOT add captions or titles like "Figure: ..." at the top or bottom
- Figure numbers and captions are added separately in the document/LaTeX
- The diagram should contain only the visual content itself
"""
    
    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize the generator.
        
        Args:
            api_key: OpenRouter API key (or use OPENROUTER_API_KEY env var)
            verbose: Print detailed progress information
        """
        # Priority: 1) explicit api_key param, 2) environment variable, 3) .env file
        self.api_key = _resolve_api_key(api_key)

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found. Please either:\n"
                "  1. Set the OPENROUTER_API_KEY environment variable\n"
                "  2. Add OPENROUTER_API_KEY to your .env file\n"
                "  3. Pass api_key parameter to the constructor\n"
                "Get your API key from: https://openrouter.ai/keys"
            )
        
        self.verbose = verbose
        self._last_error = None  # Track last error for better reporting
        self.base_url = "https://openrouter.ai/api/v1"
        # Nano Banana 2 - Google's advanced image generation model. The slug must
        # be an image-output model; a text-only chat model is rejected with
        # "No endpoints found that support the requested output modalities".
        # https://openrouter.ai/google/gemini-3.1-flash-image
        self.image_model = "google/gemini-3.1-flash-image"
        # Gemini 3.6 Flash for quality review - excellent vision and reasoning
        self.review_model = "google/gemini-3.7-flash"
        
    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def _make_request(self, model: str, messages: List[Dict[str, Any]], 
                     modalities: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Make a request to OpenRouter API.
        
        Args:
            model: Model identifier
            messages: List of message dictionaries
            modalities: Optional list of modalities (e.g., ["image", "text"])
            
        Returns:
            API response as dictionary
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/scientific-writer",
            "X-Title": "Scientific Schematic Generator"
        }
        
        payload = {
            "model": model,
            "messages": messages
        }
        
        if modalities:
            payload["modalities"] = modalities
        
        self._log(f"Making request to {model}...")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            # Try to get response body even on error
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                response_json = {"raw_text": response.text[:500]}
            
            # Check for HTTP errors but include response body in error message
            if response.status_code != 200:
                error_detail = response_json.get("error", response_json)
                self._log(f"HTTP {response.status_code}: {error_detail}")
                raise RuntimeError(f"API request failed (HTTP {response.status_code}): {error_detail}")
            
            return response_json
        except requests.exceptions.Timeout:
            raise RuntimeError("API request timed out after 120 seconds")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"API request failed: {str(e)}")
    
    def _extract_image_from_response(self, response: Dict[str, Any]) -> Optional[bytes]:
        """
        Extract base64-encoded image from API response.
        
        For Nano Banana 2, images are returned in the 'images' field of the message,
        not in the 'content' field.
        
        Args:
            response: API response dictionary
            
        Returns:
            Image bytes or None if not found
        """
        try:
            choices = response.get("choices", [])
            if not choices:
                self._log("No choices in response")
                return None
            
            message = choices[0].get("message", {})
            
            # IMPORTANT: Nano Banana 2 returns images in the 'images' field
            images = message.get("images", [])
            if images and len(images) > 0:
                self._log(f"Found {len(images)} image(s) in 'images' field")
                
                # Get first image
                first_image = images[0]
                if isinstance(first_image, dict):
                    # Extract image_url
                    if first_image.get("type") == "image_url":
                        url = first_image.get("image_url", {})
                        if isinstance(url, dict):
                            url = url.get("url", "")
                        
                        if url and url.startswith("data:image"):
                            # Extract base64 data after comma
                            if "," in url:
                                base64_str = url.split(",", 1)[1]
                                # Clean whitespace
                                base64_str = base64_str.replace('\n', '').replace('\r', '').replace(' ', '')
                                self._log(f"Extracted base64 data (length: {len(base64_str)})")
                                return base64.b64decode(base64_str)
            
            # Fallback: check content field (for other models or future changes)
            content = message.get("content", "")
            
            if self.verbose:
                self._log(f"Content type: {type(content)}, length: {len(str(content))}")
            
            # Handle string content
            if isinstance(content, str) and "data:image" in content:
                match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=\n\r]+)', content, re.DOTALL)
                if match:
                    base64_str = match.group(1).replace('\n', '').replace('\r', '').replace(' ', '')
                    self._log(f"Found image in content field (length: {len(base64_str)})")
                    return base64.b64decode(base64_str)
            
            # Handle list content
            if isinstance(content, list):
                for i, block in enumerate(content):
                    if isinstance(block, dict) and block.get("type") == "image_url":
                        url = block.get("image_url", {})
                        if isinstance(url, dict):
                            url = url.get("url", "")
                        if url and url.startswith("data:image") and "," in url:
                            base64_str = url.split(",", 1)[1].replace('\n', '').replace('\r', '').replace(' ', '')
                            self._log(f"Found image in content block {i}")
                            return base64.b64decode(base64_str)
            
            self._log("No image data found in response")
            return None
            
        except Exception as e:
            self._log(f"Error extracting image: {str(e)}")
            import traceback
            if self.verbose:
                traceback.print_exc()
            return None
    
    def _image_to_base64(self, image_path: str) -> str:
        """
        Convert image file to base64 data URL.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 data URL string
        """
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Determine image type from extension
        ext = Path(image_path).suffix.lower()
        mime_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }.get(ext, "image/png")
        
        base64_data = base64.b64encode(image_data).decode("utf-8")
        return f"data:{mime_type};base64,{base64_data}"
    
    def generate_image(self, prompt: str) -> Optional[bytes]:
        """
        Generate an image using Nano Banana 2.
        
        Args:
            prompt: Description of the diagram to generate
            
        Returns:
            Image bytes or None if generation failed
        """
        self._last_error = None  # Reset error
        
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        try:
            response = self._make_request(
                model=self.image_model,
                messages=messages,
                modalities=["image", "text"]
            )
            
            # Debug: print response structure if verbose
            if self.verbose:
                self._log(f"Response keys: {response.keys()}")
                if "error" in response:
                    self._log(f"API Error: {response['error']}")
                if "choices" in response and response["choices"]:
                    msg = response["choices"][0].get("message", {})
                    self._log(f"Message keys: {msg.keys()}")
                    # Show content preview without printing huge base64 data
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        preview = content[:200] + "..." if len(content) > 200 else content
                        self._log(f"Content preview: {preview}")
                    elif isinstance(content, list):
                        self._log(f"Content is list with {len(content)} items")
                        for i, item in enumerate(content[:3]):
                            if isinstance(item, dict):
                                self._log(f"  Item {i}: type={item.get('type')}")
            
            # Check for API errors in response
            if "error" in response:
                error_msg = response["error"]
                if isinstance(error_msg, dict):
                    error_msg = error_msg.get("message", str(error_msg))
                self._last_error = f"API Error: {error_msg}"
                print(f"✗ {self._last_error}")
                return None
            
            image_data = self._extract_image_from_response(response)
            if image_data:
                self._log(f"✓ Generated image ({len(image_data)} bytes)")
            else:
                self._last_error = "No image data in API response - model may not support image generation"
                self._log(f"✗ {self._last_error}")
                # Additional debug info when image extraction fails
                if self.verbose and "choices" in response:
                    msg = response["choices"][0].get("message", {})
                    self._log(f"Full message structure: {json.dumps({k: type(v).__name__ for k, v in msg.items()})}")
            
            return image_data
        except RuntimeError as e:
            self._last_error = str(e)
            self._log(f"✗ Generation failed: {self._last_error}")
            return None
        except Exception as e:
            self._last_error = f"Unexpected error: {str(e)}"
            self._log(f"✗ Generation failed: {self._last_error}")
            import traceback
            if self.verbose:
                traceback.print_exc()
            return None
    
    def review_image(self, image_path: str, original_prompt: str, 
                    iteration: int, doc_type: str = "default",
                    max_iterations: int = 2) -> ReviewResult:
        """
        Review the generated image for quality, using the vision review model.

        Args:
            image_path: Path to the generated image
            original_prompt: Original user prompt
            iteration: Current iteration number
            doc_type: Document type (journal, poster, presentation, etc.)
            max_iterations: Maximum iterations allowed

        Returns:
            A ReviewResult. When the review cannot be completed -- the request
            fails, or the model answers with nothing usable -- `reviewed` is
            False and `score` is None rather than a stand-in number, and
            `needs_improvement` is False: the fault is in the reviewer, not in
            the diagram, so regenerating would not help.
        """
        image_data_url = self._image_to_base64(image_path)
        
        # Get quality threshold for this document type
        threshold = self.QUALITY_THRESHOLDS.get(doc_type.lower(), 
                                                 self.QUALITY_THRESHOLDS["default"])
        
        review_prompt = f"""You are an expert reviewer evaluating a scientific diagram for publication quality.

ORIGINAL REQUEST: {original_prompt}

DOCUMENT TYPE: {doc_type} (quality threshold: {threshold}/10)
ITERATION: {iteration}/{max_iterations}

Carefully evaluate this diagram on these criteria:

1. **Scientific Accuracy** (0-2 points)
   - Correct representation of concepts
   - Proper notation and symbols
   - Accurate relationships shown

2. **Clarity and Readability** (0-2 points)
   - Easy to understand at a glance
   - Clear visual hierarchy
   - No ambiguous elements

3. **Label Quality** (0-2 points)
   - All important elements labeled
   - Labels are readable (appropriate font size)
   - Consistent labeling style

4. **Layout and Composition** (0-2 points)
   - Logical flow (top-to-bottom or left-to-right)
   - Balanced use of space
   - No overlapping elements

5. **Professional Appearance** (0-2 points)
   - Publication-ready quality
   - Clean, crisp lines and shapes
   - Appropriate colors/contrast

RESPOND IN THIS EXACT FORMAT:
SCORE: [total score 0-10]

STRENGTHS:
- [strength 1]
- [strength 2]

ISSUES:
- [issue 1 if any]
- [issue 2 if any]

VERDICT: [ACCEPTABLE or NEEDS_IMPROVEMENT]

If score >= {threshold}, the diagram is ACCEPTABLE for {doc_type} publication.
If score < {threshold}, mark as NEEDS_IMPROVEMENT with specific suggestions."""

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": review_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        }
                    }
                ]
            }
        ]
        
        try:
            response = self._make_request(
                model=self.review_model,
                messages=messages
            )

            # Extract text response
            choices = response.get("choices", [])
            if not choices:
                # A normal enough outcome -- a rate limit, a content filter, a
                # provider hiccup. The diagram itself is fine; only its review
                # is missing, and saying so beats inventing a score.
                reason = "the review model returned no choices"
                self._log(f"⚠ Review unavailable: {reason}")
                return ReviewResult(
                    f"Review unavailable: {reason}.",
                    None, False, reviewed=False, error=reason,
                )

            message = choices[0].get("message", {})
            content = message.get("content", "")

            # Some models put their analysis in a separate reasoning field
            reasoning = message.get("reasoning", "")
            if reasoning and not content:
                content = reasoning

            if isinstance(content, list):
                # Extract text from content blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(block.get("text", ""))
                content = "\n".join(text_parts)

            score = _parse_score(content)
            verdict = _parse_verdict(content)

            if score is None and verdict is None:
                reason = "no score or verdict found in the review"
                self._log(f"⚠ Review unusable: {reason}")
                return ReviewResult(
                    content if content else f"Review unusable: {reason}.",
                    None, False, reviewed=True, error=reason,
                )

            needs_improvement = verdict == "NEEDS_IMPROVEMENT" or (
                score is not None and score < threshold
            )

            shown = f"{score}/10" if score is not None else "not stated"
            self._log(f"✓ Review complete (Score: {shown}, Threshold: {threshold}/10)")
            self._log(f"  Verdict: {'Needs improvement' if needs_improvement else 'Acceptable'}")

            return ReviewResult(
                content if content else "Review returned no text",
                score,
                needs_improvement,
                reviewed=True,
                error=None if score is not None else "no score found in the review",
            )
        except Exception as e:
            # A failed review must not fail the run -- the image is already
            # generated and saved -- but it must not read as a pass either.
            self._log(f"⚠ Review failed: {str(e)}")
            return ReviewResult(
                f"Review failed: {str(e)}",
                None, False, reviewed=False, error=str(e),
            )
    
    def improve_prompt(self, original_prompt: str, critique: str, 
                      iteration: int) -> str:
        """
        Improve the generation prompt based on critique.
        
        Args:
            original_prompt: Original user prompt
            critique: Review critique from previous iteration
            iteration: Current iteration number
            
        Returns:
            Improved prompt for next generation
        """
        improved_prompt = f"""{self.SCIENTIFIC_DIAGRAM_GUIDELINES}

USER REQUEST: {original_prompt}

ITERATION {iteration}: Based on previous feedback, address these specific improvements:
{critique}

Generate an improved version that addresses all the critique points while maintaining scientific accuracy and professional quality."""
        
        return improved_prompt
    
    def generate_iterative(self, user_prompt: str, output_path: str,
                          iterations: int = 2, 
                          doc_type: str = "default") -> Dict[str, Any]:
        """
        Generate scientific schematic with smart iterative refinement.
        
        Only regenerates if the quality score is below the threshold for the
        specified document type. This saves API calls and time when the first
        generation is already good enough.
        
        Args:
            user_prompt: User's description of desired diagram
            output_path: Path to save final image
            iterations: Maximum refinement iterations (default: 2, max: 2)
            doc_type: Document type for quality threshold (journal, poster, etc.)
            
        Returns:
            Dictionary with generation results and metadata
        """
        output_path = Path(output_path)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = output_path.stem
        extension = output_path.suffix or ".png"
        
        # Get quality threshold for this document type
        threshold = self.QUALITY_THRESHOLDS.get(doc_type.lower(), 
                                                 self.QUALITY_THRESHOLDS["default"])
        
        results = {
            "user_prompt": user_prompt,
            "doc_type": doc_type,
            "quality_threshold": threshold,
            "iterations": [],
            "final_image": None,
            # None, not 0.0 -- a run whose review never completed has no score,
            # and a number here would be read as one the reviewer gave.
            "final_score": None,
            "final_reviewed": False,
            "success": False,
            "early_stop": False,
            "early_stop_reason": None
        }
        
        current_prompt = f"""{self.SCIENTIFIC_DIAGRAM_GUIDELINES}

USER REQUEST: {user_prompt}

Generate a publication-quality scientific diagram that meets all the guidelines above."""
        
        print(f"\n{'='*60}")
        print(f"Generating Scientific Schematic")
        print(f"{'='*60}")
        print(f"Description: {user_prompt}")
        print(f"Document Type: {doc_type}")
        print(f"Quality Threshold: {threshold}/10")
        print(f"Max Iterations: {iterations}")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")
        
        for i in range(1, iterations + 1):
            print(f"\n[Iteration {i}/{iterations}]")
            print("-" * 40)
            
            # Generate image
            print(f"Generating image...")
            image_data = self.generate_image(current_prompt)
            
            if not image_data:
                error_msg = getattr(self, '_last_error', 'Image generation failed - no image data returned')
                print(f"✗ Generation failed: {error_msg}")
                results["iterations"].append({
                    "iteration": i,
                    "success": False,
                    "error": error_msg
                })
                continue
            
            # Save iteration image
            iter_path = output_dir / f"{base_name}_v{i}{extension}"
            with open(iter_path, "wb") as f:
                f.write(image_data)
            print(f"✓ Saved: {iter_path}")
            
            # Review the image with the vision review model
            print(f"Reviewing image with {self.review_model}...")
            review = self.review_image(
                str(iter_path), user_prompt, i, doc_type, iterations
            )
            if review.score is not None:
                print(f"✓ Score: {review.score}/10 (threshold: {threshold}/10)")
            else:
                print(f"⚠ Review unavailable — image kept, quality not verified")
                print(f"  Reason: {review.error}")

            # Save iteration results
            iteration_result = {
                "iteration": i,
                "image_path": str(iter_path),
                "prompt": current_prompt,
                "critique": review.critique,
                "score": review.score,
                "reviewed": review.reviewed,
                "review_error": review.error,
                "needs_improvement": review.needs_improvement,
                "success": True
            }
            results["iterations"].append(iteration_result)

            # Check if quality is acceptable - STOP EARLY if so
            if not review.needs_improvement:
                if review.score is not None:
                    print(f"\n✓ Quality meets {doc_type} threshold ({review.score} >= {threshold})")
                    print(f"  No further iterations needed!")
                    reason = (f"Quality score {review.score} meets threshold "
                              f"{threshold} for {doc_type}")
                else:
                    # Regenerating cannot fix a reviewer that did not answer.
                    print(f"\n⚠ Stopping without a verified score — review the image yourself")
                    reason = f"Review did not produce a score: {review.error}"
                results["final_image"] = str(iter_path)
                results["final_score"] = review.score
                results["final_reviewed"] = review.reviewed and review.score is not None
                results["success"] = True
                results["early_stop"] = True
                results["early_stop_reason"] = reason
                break

            # If this is the last iteration, we're done regardless
            if i == iterations:
                print(f"\n⚠ Maximum iterations reached")
                results["final_image"] = str(iter_path)
                results["final_score"] = review.score
                results["final_reviewed"] = review.reviewed and review.score is not None
                results["success"] = True
                break

            # Quality below threshold - improve prompt for next iteration
            print(f"\n⚠ Quality below threshold ({review.score} < {threshold})")
            print(f"Improving prompt based on feedback...")
            current_prompt = self.improve_prompt(user_prompt, review.critique, i + 1)
        
        # Copy final version to output path
        if results["success"] and results["final_image"]:
            final_iter_path = Path(results["final_image"])
            if final_iter_path != output_path:
                import shutil
                shutil.copy(final_iter_path, output_path)
                print(f"\n✓ Final image: {output_path}")
        
        # Save review log
        log_path = output_dir / f"{base_name}_review_log.json"
        with open(log_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✓ Review log: {log_path}")
        
        print(f"\n{'='*60}")
        print(f"Generation Complete!")
        if results["final_score"] is not None:
            print(f"Final Score: {results['final_score']}/10")
        else:
            print(f"Final Score: unavailable (the review did not produce one)")
        if results["early_stop"]:
            print(f"Iterations Used: {len([r for r in results['iterations'] if r.get('success')])}/{iterations} (early stop)")
        print(f"{'='*60}\n")
        
        return results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate scientific schematics using AI with smart iterative refinement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a flowchart for a journal paper
  python generate_schematic_ai.py "CONSORT participant flow diagram" -o flowchart.png --doc-type journal
  
  # Generate neural network architecture for presentation (lower threshold)
  python generate_schematic_ai.py "Transformer encoder-decoder architecture" -o transformer.png --doc-type presentation
  
  # Generate with custom max iterations for poster
  python generate_schematic_ai.py "Biological signaling pathway" -o pathway.png --iterations 2 --doc-type poster
  
  # Verbose output
  python generate_schematic_ai.py "Circuit diagram" -o circuit.png -v

Document Types (quality thresholds):
  journal      8.5/10  - Nature, Science, peer-reviewed journals
  conference   8.0/10  - Conference papers
  thesis       8.0/10  - Dissertations, theses
  grant        8.0/10  - Grant proposals
  preprint     7.5/10  - arXiv, bioRxiv, etc.
  report       7.5/10  - Technical reports
  poster       7.0/10  - Academic posters
  presentation 6.5/10  - Slides, talks
  default      7.5/10  - General purpose

Note: Multiple iterations only occur if quality is BELOW the threshold.
      If the first generation meets the threshold, no extra API calls are made.

Environment:
  OPENROUTER_API_KEY    OpenRouter API key (required)
        """
    )
    
    parser.add_argument("prompt", help="Description of the diagram to generate")
    parser.add_argument("-o", "--output", required=True, 
                       help="Output image path (e.g., diagram.png)")
    parser.add_argument("--iterations", type=int, default=2,
                       help="Maximum refinement iterations (default: 2, max: 2)")
    parser.add_argument("--doc-type", default="default",
                       choices=["journal", "conference", "poster", "presentation", 
                               "report", "grant", "thesis", "preprint", "default"],
                       help="Document type for quality threshold (default: default)")
    parser.add_argument("--api-key", help="OpenRouter API key (or set OPENROUTER_API_KEY)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Check for API key — resolves --api-key, the environment, then any .env file
    api_key = _resolve_api_key(args.api_key)
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found")
        print("\nSet it with:")
        print("  export OPENROUTER_API_KEY='your_api_key'")
        print("\nOr add OPENROUTER_API_KEY=your_api_key to a .env file")
        print("Or provide via --api-key flag")
        sys.exit(1)
    
    # Validate iterations - enforce max of 2
    if args.iterations < 1 or args.iterations > 2:
        print("Error: Iterations must be between 1 and 2")
        sys.exit(1)
    
    try:
        generator = ScientificSchematicGenerator(api_key=api_key, verbose=args.verbose)
        results = generator.generate_iterative(
            user_prompt=args.prompt,
            output_path=args.output,
            iterations=args.iterations,
            doc_type=args.doc_type
        )
        
        if results["success"]:
            print(f"\n✓ Success! Image saved to: {args.output}")
            used = len([r for r in results['iterations'] if r.get('success')])
            if results.get("final_reviewed"):
                if results.get("early_stop"):
                    print(f"  (Completed in {used} iteration(s) - quality threshold met)")
            else:
                # The image is real; the quality claim is not. Say which.
                print(f"  (Completed in {used} iteration(s) - quality NOT verified,"
                      f" the review produced no score. Check the image yourself.)")
            sys.exit(0)
        else:
            print(f"\n✗ Generation failed. Check review log for details.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### `scripts/review_poster.sh`

```bash
#!/bin/bash

# Poster PDF Quality Check Script
# Usage: ./review_poster.sh poster.pdf

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if file argument provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No file specified${NC}"
    echo "Usage: $0 <poster.pdf>"
    exit 1
fi

POSTER_FILE="$1"

# Check if file exists
if [ ! -f "$POSTER_FILE" ]; then
    echo -e "${RED}Error: File '$POSTER_FILE' not found${NC}"
    exit 1
fi

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Poster PDF Quality Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}File:${NC} $POSTER_FILE"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Page Size Check
echo -e "${YELLOW}[1] Page Dimensions:${NC}"
if command_exists pdfinfo; then
    PAGE_SIZE=$(pdfinfo "$POSTER_FILE" 2>/dev/null | grep "Page size")
    if [ -n "$PAGE_SIZE" ]; then
        echo "    $PAGE_SIZE"
        
        # Extract dimensions and check common sizes
        WIDTH=$(echo "$PAGE_SIZE" | awk '{print $3}')
        HEIGHT=$(echo "$PAGE_SIZE" | awk '{print $5}')
        
        # Check against common poster sizes (approximate)
        if [ "$WIDTH" = "2384" ] && [ "$HEIGHT" = "3370" ]; then
            echo -e "    ${GREEN}✓ Detected: A0 Portrait${NC}"
        elif [ "$WIDTH" = "3370" ] && [ "$HEIGHT" = "2384" ]; then
            echo -e "    ${GREEN}✓ Detected: A0 Landscape${NC}"
        elif [ "$WIDTH" = "1684" ] && [ "$HEIGHT" = "2384" ]; then
            echo -e "    ${GREEN}✓ Detected: A1 Portrait${NC}"
        elif [ "$WIDTH" = "2592" ] && [ "$HEIGHT" = "3456" ]; then
            echo -e "    ${GREEN}✓ Detected: 36×48 inches Portrait${NC}"
        else
            echo -e "    ${YELLOW}⚠ Non-standard size detected${NC}"
        fi
    else
        echo -e "    ${RED}✗ Could not extract page size${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdfinfo not installed (install: brew install poppler or apt-get install poppler-utils)${NC}"
fi
echo ""

# 2. Page Count
echo -e "${YELLOW}[2] Page Count:${NC}"
if command_exists pdfinfo; then
    PAGE_COUNT=$(pdfinfo "$POSTER_FILE" 2>/dev/null | grep "Pages" | awk '{print $2}')
    if [ "$PAGE_COUNT" = "1" ]; then
        echo -e "    ${GREEN}✓ Single page (correct for poster)${NC}"
    else
        echo -e "    ${RED}✗ Multiple pages detected: $PAGE_COUNT${NC}"
        echo -e "    ${YELLOW}  Posters should be single page${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdfinfo not installed${NC}"
fi
echo ""

# 3. File Size
echo -e "${YELLOW}[3] File Size:${NC}"
if command_exists ls; then
    FILE_SIZE=$(ls -lh "$POSTER_FILE" | awk '{print $5}')
    FILE_SIZE_BYTES=$(ls -l "$POSTER_FILE" | awk '{print $5}')
    echo "    Size: $FILE_SIZE"
    
    # Check if file is too large for email
    if [ "$FILE_SIZE_BYTES" -gt 52428800 ]; then  # 50MB
        echo -e "    ${YELLOW}⚠ Large file (>50MB) - may need compression for email${NC}"
        echo -e "    ${BLUE}  Compress with: gs -sDEVICE=pdfwrite -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf $POSTER_FILE${NC}"
    elif [ "$FILE_SIZE_BYTES" -lt 1048576 ]; then  # 1MB
        echo -e "    ${YELLOW}⚠ Small file - check image quality${NC}"
    else
        echo -e "    ${GREEN}✓ Reasonable file size${NC}"
    fi
fi
echo ""

# 4. Font Embedding Check
echo -e "${YELLOW}[4] Font Embedding:${NC}"
if command_exists pdffonts; then
    echo "    Checking first 20 fonts..."
    FONT_OUTPUT=$(pdffonts "$POSTER_FILE" 2>/dev/null | head -21)
    echo "$FONT_OUTPUT" | tail -20 | while IFS= read -r line; do
        echo "    $line"
    done
    
    # Check for non-embedded fonts
    NON_EMBEDDED=$(echo "$FONT_OUTPUT" | tail -n +3 | awk '{if ($4 == "no") print $0}')
    if [ -n "$NON_EMBEDDED" ]; then
        echo -e "    ${RED}✗ Some fonts are NOT embedded (printing may fail)${NC}"
        echo -e "    ${BLUE}  Fix: Recompile with 'pdflatex -dEmbedAllFonts=true poster.tex'${NC}"
    else
        echo -e "    ${GREEN}✓ All fonts appear to be embedded${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdffonts not installed (install: brew install poppler or apt-get install poppler-utils)${NC}"
fi
echo ""

# 5. Image Quality Check
echo -e "${YELLOW}[5] Image Quality:${NC}"
if command_exists pdfimages; then
    IMAGE_COUNT=$(pdfimages -list "$POSTER_FILE" 2>/dev/null | tail -n +3 | wc -l | tr -d ' ')
    if [ "$IMAGE_COUNT" -gt 0 ]; then
        echo "    Found $IMAGE_COUNT image(s)"
        echo "    Image details:"
        pdfimages -list "$POSTER_FILE" 2>/dev/null | head -20
        
        # Note: DPI calculation would require page size knowledge
        echo -e "    ${BLUE}  Verify images are at least 300 DPI for printing${NC}"
        echo -e "    ${BLUE}  Formula: DPI = pixels / (inches in poster)${NC}"
    else
        echo -e "    ${YELLOW}⚠ No images found${NC}"
    fi
else
    echo -e "    ${YELLOW}⚠ pdfimages not installed (install: brew install poppler or apt-get install poppler-utils)${NC}"
fi
echo ""

# 6. Manual Checks Required
echo -e "${YELLOW}[6] Manual Visual Inspection Required:${NC}"
echo ""
echo -e "${BLUE}Layout and Spacing:${NC}"
echo "    [ ] Content fills entire page (no large white margins)"
echo "    [ ] Consistent spacing between columns"
echo "    [ ] Consistent spacing between blocks/sections"
echo "    [ ] All elements aligned properly"
echo "    [ ] No overlapping text or figures"
echo ""

echo -e "${BLUE}Typography:${NC}"
echo "    [ ] Title visible and large (72pt+)"
echo "    [ ] Section headers readable (48-72pt)"
echo "    [ ] Body text readable (24-36pt minimum)"
echo "    [ ] No text cutoff or running off edges"
echo "    [ ] Consistent font usage"
echo ""

echo -e "${BLUE}Visual Elements:${NC}"
echo "    [ ] All figures display correctly"
echo "    [ ] No pixelated or blurry images"
echo "    [ ] Figure captions present and readable"
echo "    [ ] Colors render as expected"
echo "    [ ] Logos display clearly"
echo "    [ ] QR codes visible and scannable"
echo ""

echo -e "${BLUE}Content:${NC}"
echo "    [ ] All sections present (Intro, Methods, Results, Conclusions)"
echo "    [ ] References included"
echo "    [ ] Contact information visible"
echo "    [ ] No placeholder text (Lorem ipsum, TODO, etc.)"
echo ""

# 7. Recommended Tests
echo -e "${YELLOW}[7] Recommended Next Steps:${NC}"
echo ""
echo -e "${BLUE}Test Print:${NC}"
echo "    • Print at 25% scale (A0→A4, 36×48→Letter)"
echo "    • Check readability from 2-3 feet"
echo "    • Verify colors printed accurately"
echo ""

echo -e "${BLUE}Digital Checks:${NC}"
echo "    • View at 100% zoom in PDF viewer"
echo "    • Test on different screens/devices"
echo "    • Verify QR codes work with scanner app"
echo ""

echo -e "${BLUE}Proofreading:${NC}"
echo "    • Spell-check all text"
echo "    • Verify author names and affiliations"
echo "    • Confirm all statistics and numbers"
echo "    • Ask colleague to review"
echo ""

# 8. Summary
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Quality Check Complete${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "Review the checks above and complete manual verification."
echo -e "For full checklist, see: ${BLUE}assets/poster_quality_checklist.md${NC}"
echo ""

exit 0
```

### `assets/baposter_template.tex`

```latex
% ==============================================================================
% Research Poster Template - baposter
% ==============================================================================
% A structured, professional poster template using baposter
% Excellent for multi-column layouts with automatic positioning
% ==============================================================================

\documentclass[a0paper,portrait,fontscale=0.285]{baposter}

% Packages
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{multicol}
\usepackage{qrcode}
\usepackage{hyperref}
\usepackage{enumitem}

% Set list spacing
\setlist{nosep}

% ==============================================================================
% POSTER CONTENT - CUSTOMIZE BELOW
% ==============================================================================

\begin{document}

\begin{poster}{
  % ============================================================================
  % POSTER CONFIGURATION
  % ============================================================================
  
  % Grid and columns
  grid=false,                    % Set to true for debugging layout
  columns=3,                     % Number of columns
  colspacing=1.5em,              % Space between columns
  
  % Background
  background=plain,              % plain, shadetb, shadelr
  bgColorOne=white,
  bgColorTwo=white,
  
  % Borders
  borderColor=blue!50!black,
  linewidth=2pt,
  
  % Header
  headerColorOne=blue!70!black,
  headerColorTwo=blue!60!black,
  headerFontColor=white,
  headerheight=0.12\textheight,
  headershape=roundedright,      % rectangle, rounded, roundedright, roundedleft
  headershade=plain,             % plain, shadetb, shadelr
  headerborder=closed,           % open, closed
  headerfont=\Large\sf\bf,
  
  % Boxes
  boxColorOne=white,
  boxColorTwo=blue!10,
  boxshade=plain,
  textborder=roundedleft,        % none, rectangle, rounded, roundedleft, roundedright
  
  % Eye catcher
  eyecatcher=true
}
% ============================================================================
% HEADER CONTENT
% ============================================================================
% Eye Catcher (Left Logo)
{
  \includegraphics[height=6em]{logo1.pdf}
}
% Title
{
  \sf\bf Your Research Title: Concise and Descriptive
}
% Authors
{
  \vspace{0.3em}
  Author One\textsuperscript{1}, Author Two\textsuperscript{2}, \underline{Presenting Author}\textsuperscript{1}\\[0.3em]
  {\small
  \textsuperscript{1}Department, University Name, City, Country\\
  \textsuperscript{2}Research Institute Name, City, Country}
}
% University Logo (Right)
{
  \includegraphics[height=6em]{logo2.pdf}
}

% ==============================================================================
% LEFT COLUMN
% ==============================================================================

\headerbox{Introduction}{name=intro,column=0,row=0}{
  \textbf{Background}
  
  Brief context establishing the importance of your research area (1-2 sentences).
  
  \vspace{0.3cm}
  
  \textbf{Problem Statement}
  
  What gap or challenge does your work address? (1-2 sentences)
  
  \vspace{0.3cm}
  
  \textbf{Objective}
  
  Clear statement of your research goal (1 sentence).
}

\headerbox{Methods}{name=methods,column=0,below=intro}{
  \textbf{Study Design}
  \begin{itemize}
    \item Experimental approach or study type
    \item Sample: n = X participants/samples
    \item Key procedures
  \end{itemize}
  
  \vspace{0.3cm}
  
  \textbf{Analysis}
  \begin{itemize}
    \item Statistical methods
    \item Software: R 4.3, Python 3.10
    \item Significance: p < 0.05
  \end{itemize}
  
  \vspace{0.3cm}
  
  \begin{center}
    \includegraphics[width=0.9\linewidth]{methods_flowchart.pdf}
  \end{center}
}

% ==============================================================================
% MIDDLE COLUMN (SPANS 2 COLUMNS FOR LARGE RESULT)
% ==============================================================================

\headerbox{Results: Main Finding}{name=results1,column=1,row=0,span=2}{
  Brief description of your primary result. What is the key observation?
  
  \vspace{0.3cm}
  
  \begin{center}
    \includegraphics[width=0.95\linewidth]{figure1.pdf}
  \end{center}
  
  \textbf{Figure 1:} Descriptive caption explaining the main result. Include statistics (Mean ± SD, n=X, **p<0.01).
}

% ==============================================================================
% MIDDLE COLUMN (CONTINUES BELOW)
% ==============================================================================

\headerbox{Results: Finding 2}{name=results2,column=1,below=results1}{
  Brief description of second key result.
  
  \begin{center}
    \includegraphics[width=0.9\linewidth]{figure2.pdf}
  \end{center}
  
  \textbf{Figure 2:} Supporting result or comparison.
}

% ==============================================================================
% RIGHT COLUMN
% ==============================================================================

\headerbox{Results: Finding 3}{name=results3,column=2,below=results1}{
  Brief description of third result or validation.
  
  \begin{center}
    \includegraphics[width=0.9\linewidth]{figure3.pdf}
  \end{center}
  
  \textbf{Figure 3:} Additional finding.
}

% ==============================================================================
% BOTTOM ROW (SPANS ALL COLUMNS)
% ==============================================================================

\headerbox{Conclusions}{name=conclusions,column=0,span=2,above=bottom}{
  \begin{multicols}{2}
    \textbf{Key Findings}
    \begin{itemize}
      \item Main conclusion 1 with significance
      \item Main conclusion 2 with impact
      \item Main conclusion 3 with implications
    \end{itemize}
    
    \vspace{0.3cm}
    
    \textbf{Limitations}
    \begin{itemize}
      \item Study constraints
      \item Interpretation context
    \end{itemize}
    
    \columnbreak
    
    \textbf{Future Directions}
    \begin{itemize}
      \item Ongoing studies
      \item Broader applications
      \item Next research questions
    \end{itemize}
    
    \vspace{0.3cm}
    
    \textbf{Clinical/Practical Implications}
    \begin{itemize}
      \item Real-world applications
      \item Impact on practice
    \end{itemize}
  \end{multicols}
}

\headerbox{Scan for More}{name=qr,column=2,above=bottom}{
  \begin{center}
    \qrcode[height=4cm]{https://doi.org/10.1234/your-paper}\\
    \vspace{0.3cm}
    \small Full paper, code \& data
  \end{center}
}

% ==============================================================================
% FOOTER (FULL WIDTH AT BOTTOM)
% ==============================================================================

\headerbox{}{name=footer,column=0,span=3,above=bottom,below=conclusions}{
  \footnotesize
  \begin{multicols}{2}
    \textbf{References}
    \begin{enumerate}
      \item Author A et al. (2023). Title. \textit{Journal}, 10(2), 123-145.
      \item Author B et al. (2024). Title. \textit{Conference}.
      \item Author C et al. (2022). Title. \textit{Journal}, 15(3), 456-478.
    \end{enumerate}
    
    \columnbreak
    
    \textbf{Acknowledgments}
    
    Funded by Grant Agency (Grant \#12345). Thanks to collaborators at Institution X.
    
    \vspace{0.3cm}
    
    \textbf{Contact:} presenter.email@university.edu | labname.university.edu
  \end{multicols}
}

\end{poster}

\end{document}
```

### `assets/beamerposter_template.tex`

```latex
% ==============================================================================
% Research Poster Template - beamerposter
% ==============================================================================
% A professional academic poster template using beamerposter
% Customize colors, content, and layout as needed
% ==============================================================================

\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}
\usetheme{Berlin}
\usecolortheme{beaver}

% Remove default margins for full page coverage
\setbeamersize{text margin left=5mm, text margin right=5mm}
\usepackage[margin=10mm]{geometry}

% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Packages
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{multicol}
\usepackage{qrcode}
\usepackage{hyperref}

% Font configuration
\setbeamerfont{title}{size=\VeryHuge,series=\bfseries}
\setbeamerfont{author}{size=\Large}
\setbeamerfont{institute}{size=\normalsize}
\setbeamerfont{block title}{size=\huge,series=\bfseries}
\setbeamerfont{block body}{size=\LARGE}

% Custom colors (customize to match your institution)
\definecolor{primarycolor}{RGB}{0,51,102}      % Dark blue
\definecolor{secondarycolor}{RGB}{204,0,0}     % Red
\definecolor{accentcolor}{RGB}{255,204,0}      % Gold

\setbeamercolor{structure}{fg=primarycolor}
\setbeamercolor{block title}{bg=primarycolor,fg=white}
\setbeamercolor{block body}{bg=primarycolor!10,fg=black}

% ==============================================================================
% POSTER CONTENT - CUSTOMIZE BELOW
% ==============================================================================

\title{Your Research Title: Concise and Descriptive}
\author{Author One\textsuperscript{1}, Author Two\textsuperscript{2}, \underline{Presenting Author}\textsuperscript{1}}
\institute{
  \textsuperscript{1}Department, University Name\\
  \textsuperscript{2}Research Institute Name
}

\begin{document}

\begin{frame}[t]
  
  % ============================================================================
  % HEADER
  % ============================================================================
  \begin{block}{}
    \begin{columns}[T]
      \begin{column}{.15\linewidth}
        % Left logo
        \includegraphics[width=0.9\linewidth]{logo1.pdf}
      \end{column}
      
      \begin{column}{.7\linewidth}
        \centering
        \usebeamerfont{title}\inserttitle\\[0.5cm]
        \usebeamerfont{author}\insertauthor\\[0.3cm]
        \usebeamerfont{institute}\insertinstitute
      \end{column}
      
      \begin{column}{.15\linewidth}
        % Right logo
        \includegraphics[width=0.9\linewidth]{logo2.pdf}
      \end{column}
    \end{columns}
  \end{block}
  
  \vspace{1cm}
  
  % ============================================================================
  % MAIN CONTENT - 3 COLUMN LAYOUT
  % ============================================================================
  
  \begin{columns}[t]
    
    % ==========================================================================
    % LEFT COLUMN
    % ==========================================================================
    \begin{column}{.3\linewidth}
      
      \begin{block}{Introduction}
        \textbf{Background:} Brief context about your research area (1-2 sentences).
        
        \vspace{0.5cm}
        
        \textbf{Problem:} What gap or challenge does your work address? (1-2 sentences)
        
        \vspace{0.5cm}
        
        \textbf{Objective:} Clear statement of your research goal (1 sentence).
      \end{block}
      
      \vspace{1cm}
      
      \begin{block}{Methods}
        \textbf{Study Design:}
        \begin{itemize}
          \item Experimental approach or design
          \item Sample size and population
          \item Key procedures
        \end{itemize}
        
        \vspace{0.5cm}
        
        \textbf{Analysis:}
        \begin{itemize}
          \item Statistical methods
          \item Software/tools used
          \item Validation approach
        \end{itemize}
        
        \vspace{0.5cm}
        
        % Optional: Methods flowchart
        \begin{center}
          \includegraphics[width=0.9\linewidth]{methods_flowchart.pdf}
        \end{center}
      \end{block}
      
    \end{column}
    
    % ==========================================================================
    % MIDDLE COLUMN
    % ==========================================================================
    \begin{column}{.3\linewidth}
      
      \begin{block}{Results}
        \textbf{Finding 1:} Brief description
        
        \begin{center}
          \includegraphics[width=0.95\linewidth]{figure1.pdf}
          \small Figure 1: Descriptive caption with key statistics (n=X, p<0.01).
        \end{center}
        
        \vspace{1cm}
        
        \textbf{Finding 2:} Brief description
        
        \begin{center}
          \includegraphics[width=0.95\linewidth]{figure2.pdf}
          \small Figure 2: Another key result showing comparison or trend.
        \end{center}
      \end{block}
      
    \end{column}
    
    % ==========================================================================
    % RIGHT COLUMN
    % ==========================================================================
    \begin{column}{.3\linewidth}
      
      \begin{block}{Results (continued)}
        \textbf{Finding 3:} Brief description
        
        \begin{center}
          \includegraphics[width=0.95\linewidth]{figure3.pdf}
          \small Figure 3: Additional important result or validation.
        \end{center}
      \end{block}
      
      \vspace{1cm}
      
      \begin{block}{Conclusions}
        \textbf{Key Findings:}
        \begin{itemize}
          \item Main conclusion 1 with impact
          \item Main conclusion 2 with significance
          \item Main conclusion 3 with implications
        \end{itemize}
        
        \vspace{0.5cm}
        
        \textbf{Limitations:}
        \begin{itemize}
          \item Brief acknowledgment of constraints
          \item Context for interpretation
        \end{itemize}
        
        \vspace{0.5cm}
        
        \textbf{Future Directions:}
        \begin{itemize}
          \item Next steps or ongoing work
          \item Broader applications
        \end{itemize}
      \end{block}
      
    \end{column}
    
  \end{columns}
  
  \vspace{1cm}
  
  % ============================================================================
  % FOOTER
  % ============================================================================
  
  \begin{block}{}
    \footnotesize
    \begin{columns}[T]
      \begin{column}{.75\linewidth}
        \textbf{References}
        \begin{enumerate}
          \item Author A et al. (2023). Title. \textit{Journal}, 10(2), 123-145.
          \item Author B et al. (2024). Title. \textit{Conference Proceedings}.
          \item Author C et al. (2022). Title. \textit{Journal}, 15(3), 456-478.
        \end{enumerate}
        
        \vspace{0.3cm}
        
        \textbf{Acknowledgments:} Funded by Grant Agency (Grant \#12345). Thanks to collaborators and facility staff.
        
        \vspace{0.3cm}
        
        \textbf{Contact:} presenter.email@university.edu | Lab Website: labname.university.edu
      \end{column}
      
      \begin{column}{.2\linewidth}
        \centering
        \qrcode[height=3.5cm]{https://doi.org/10.1234/your-paper}\\
        \tiny Scan for full paper
      \end{column}
    \end{columns}
  \end{block}
  
\end{frame}

\end{document}
```

### `assets/poster_quality_checklist.md`

# Research Poster Quality Checklist

Use this comprehensive checklist before printing or presenting your research poster.

## Pre-Compilation Checks

### Content Completeness
- [ ] Title is concise and descriptive (10-15 words)
- [ ] All author names spelled correctly
- [ ] Affiliations complete and accurate
- [ ] Contact email address included
- [ ] All sections present: Introduction, Methods, Results, Conclusions
- [ ] References cited (5-10 key citations)
- [ ] Acknowledgments included (funding, collaborators)
- [ ] No placeholder text remaining (TODO, Lorem ipsum, etc.)

### Visual Content
- [ ] All figures prepared and high resolution (300+ DPI)
- [ ] Figure captions written and descriptive
- [ ] Logos available (university, funding agencies)
- [ ] QR codes generated and tested
- [ ] Icons/graphics sourced (if used)

### LaTeX Configuration
- [ ] Correct paper size specified (A0, A1, 36×48", etc.)
- [ ] Correct orientation (portrait/landscape)
- [ ] Minimal margins configured (5-15mm)
- [ ] Font sizes appropriate (title 72pt+, body 24pt+)
- [ ] Color scheme defined
- [ ] All packages installed and working

## Compilation Checks

### Successful Compilation
- [ ] PDF compiles without errors
- [ ] No critical warnings in .log file
- [ ] All citations resolved (no [?] marks)
- [ ] All cross-references working
- [ ] Bibliography generated correctly (if using BibTeX)

### Warning Review
Run in terminal: `grep -i "warning\|overfull\|underfull" poster.log`

- [ ] No overfull hbox warnings (text too wide)
- [ ] No underfull hbox warnings (excessive spacing)
- [ ] No missing figure warnings
- [ ] No missing font warnings
- [ ] No undefined reference warnings

## PDF Quality Checks

### Automated Checks

Run: `./scripts/review_poster.sh poster.pdf` or manually verify:

#### Page Specifications
```bash
pdfinfo poster.pdf | grep "Page size"
```
- [ ] Page size matches requirements exactly
- [ ] Single page document (not multi-page)
- [ ] Correct orientation

#### Font Embedding
```bash
pdffonts poster.pdf
```
- [ ] All fonts show "yes" in "emb" column
- [ ] No bitmap fonts (should be Type 1 or TrueType)

#### Image Quality
```bash
pdfimages -list poster.pdf
```
- [ ] All images at least 300 DPI
- [ ] No JPEG artifacts in figures
- [ ] Vector graphics used where possible

#### File Size
```bash
ls -lh poster.pdf
```
- [ ] Reasonable size (2-50 MB typical)
- [ ] Not too large for email (<50 MB) if sharing digitally
- [ ] Not suspiciously small (<1 MB - may indicate low quality)

## Visual Inspection (100% Zoom)

### Layout and Spacing
- [ ] Content fills entire page (no excessive white margins)
- [ ] Consistent spacing between columns (1-2cm)
- [ ] Consistent spacing between blocks (1-2cm)
- [ ] All elements aligned to grid
- [ ] No overlapping text or figures
- [ ] White space evenly distributed (30-40% total)
- [ ] Visual balance across poster (no heavy/empty areas)

### Typography
- [ ] Title readable and prominent (72-120pt)
- [ ] Section headers clear (48-72pt)
- [ ] Body text large enough (24-36pt minimum, 30pt+ recommended)
- [ ] Captions readable (18-24pt)
- [ ] No text running off edges
- [ ] Consistent font usage throughout
- [ ] Line spacing adequate (1.2-1.5×)
- [ ] No awkward hyphenation or word breaks
- [ ] All special characters render correctly (Greek, math symbols)

### Visual Elements
- [ ] All figures display correctly
- [ ] No pixelated or blurry images
- [ ] Figure resolution high (zoom to 200% to verify)
- [ ] Figure labels large and clear
- [ ] Graph axes labeled with units
- [ ] Color schemes consistent across figures
- [ ] Legends readable and well-positioned
- [ ] Logos crisp and professional
- [ ] QR codes sharp and high-contrast (minimum 2×2cm)
- [ ] No visual artifacts or rendering errors

### Colors
- [ ] Colors render as intended (not washed out)
- [ ] High contrast between text and background (≥4.5:1)
- [ ] Color scheme harmonious
- [ ] Colors appropriate for printing (not too bright/neon)
- [ ] Institutional colors used correctly
- [ ] Color-blind friendly palette (avoid red-green only)

### Content
- [ ] Title complete and correctly positioned
- [ ] All author names and affiliations visible
- [ ] All sections present and labeled
- [ ] Results section has figures/data
- [ ] Conclusions clearly stated
- [ ] References formatted consistently
- [ ] Contact information clearly visible
- [ ] No missing content

## Reduced-Scale Print Test (CRITICAL)

### Test Print Preparation
Print poster at 25% scale:
- A0 poster → Print on A4 paper
- 36×48" poster → Print on Letter paper
- A1 poster → Print on A5 paper

### Readability from Distance

**From 6 feet (2 meters):**
- [ ] Title clearly readable
- [ ] Authors identifiable
- [ ] Main figures visible

**From 4 feet (1.2 meters):**
- [ ] Section headers readable
- [ ] Figure captions readable
- [ ] Key results visible

**From 2 feet (0.6 meters):**
- [ ] Body text readable
- [ ] References readable
- [ ] All details clear

### Print Quality
- [ ] Colors accurate (match screen expectations)
- [ ] No banding or color shifts
- [ ] Sharp edges (not blurry)
- [ ] Consistent print density
- [ ] No printer artifacts

## Content Proofreading

### Text Accuracy
- [ ] Spell-checked all text
- [ ] Grammar checked
- [ ] All author names spelled correctly
- [ ] All affiliations accurate
- [ ] Email address correct
- [ ] No typos in title or headers

### Scientific Accuracy
- [ ] All numbers and statistics verified
- [ ] Units included and correct
- [ ] Statistical significance correctly indicated
- [ ] Sample sizes (n=) reported
- [ ] Figure numbering consistent
- [ ] Citations accurate and complete
- [ ] Methodology accurately described
- [ ] Results match figures/data
- [ ] Conclusions supported by data

### Consistency
- [ ] Terminology consistent throughout
- [ ] Abbreviations defined at first use
- [ ] Consistent notation (italics for genes, etc.)
- [ ] Consistent units (don't mix metric/imperial)
- [ ] Consistent decimal places
- [ ] Consistent citation format

## Accessibility Checks

### Color Contrast
Test at: https://webaim.org/resources/contrastchecker/

- [ ] Title-background contrast ≥ 7:1
- [ ] Body text-background contrast ≥ 4.5:1
- [ ] All text meets WCAG AA standard minimum

### Color Blindness
Test with simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/

- [ ] Information not lost with deuteranopia (red-green)
- [ ] Key distinctions visible with protanopia
- [ ] Patterns/shapes used in addition to color
- [ ] No critical info conveyed by color alone

### Visual Clarity
- [ ] Clear visual hierarchy (size, weight, position)
- [ ] Logical reading order
- [ ] Grouping of related elements obvious
- [ ] Important info emphasized appropriately

## Peer Review

### 30-Second Test
Show poster to colleague for 30 seconds, then ask:
- [ ] They can identify the research topic
- [ ] They can state the main finding
- [ ] They remember the key figure

### 5-Minute Review
Ask colleague to read poster (5 minutes), then ask:
- [ ] They understand the research question
- [ ] They can explain the approach
- [ ] They can summarize the conclusions
- [ ] They identify what makes it novel/important

### Feedback
- [ ] Noted any confusing elements
- [ ] Identified any unclear figures
- [ ] Checked for jargon that needs definition
- [ ] Verified logical flow

## Pre-Printing Final Checks

### Technical Specifications
- [ ] PDF size exactly matches conference requirements
- [ ] Orientation correct (portrait vs landscape)
- [ ] All fonts embedded (verified with pdffonts)
- [ ] Color space correct (RGB for screen, CMYK if printer requires)
- [ ] Resolution adequate (300+ DPI for all images)
- [ ] Bleed area added if required (typically 3-5mm)
- [ ] Crop marks visible if required
- [ ] File naming convention followed

### Printer Communication
- [ ] Confirmed paper type (matte vs glossy)
- [ ] Confirmed poster size
- [ ] Provided color profile if required
- [ ] Verified delivery deadline
- [ ] Confirmed shipping/pickup arrangements
- [ ] Discussed backup plan if issues arise

### Backup and Storage
- [ ] PDF saved with clear filename: `LastName_Conference_Poster.pdf`
- [ ] Source .tex file backed up
- [ ] All figure files backed up
- [ ] Copy saved to cloud storage
- [ ] Copy saved on USB drive for conference
- [ ] Digital version ready to email if requested

## Digital Presentation Checks

If presenting digitally or sharing online:

### File Optimization
- [ ] PDF compressed if >10MB (for email)
- [ ] Test opens in Adobe Reader
- [ ] Test opens in Preview (Mac)
- [ ] Test opens in browser PDF viewers
- [ ] Test on mobile devices

### Interactive Elements
- [ ] All QR codes tested and functional
- [ ] QR codes link to correct URLs
- [ ] Hyperlinks work (if included)
- [ ] Links open in new tabs/windows appropriately

### Alternative Formats
- [ ] PNG version created for social media (if needed)
- [ ] Thumbnail image created
- [ ] Poster description/abstract prepared
- [ ] Hashtags and social media text ready

## Conference-Specific

### Requirements Verification
- [ ] Poster size matches conference specifications exactly
- [ ] Orientation matches requirements
- [ ] File format correct (usually PDF)
- [ ] Submission deadline met
- [ ] File naming convention followed
- [ ] Abstract/description submitted if required

### Physical Preparation
- [ ] Poster printed and inspected
- [ ] Backup printed copy prepared
- [ ] Push pins/mounting materials ready
- [ ] Poster tube or flat portfolio for transport
- [ ] Business cards/handouts prepared
- [ ] Digital backup on laptop/phone

### Presentation Preparation
- [ ] 30-second elevator pitch prepared
- [ ] 2-minute summary prepared
- [ ] 5-minute detailed explanation prepared
- [ ] Anticipated questions considered
- [ ] Follow-up materials ready (QR code to paper, etc.)

## Final Sign-Off

Date: ________________

Poster Title: _______________________________________________

Conference: _______________________________________________

Reviewed by: _______________________________________________

All critical items checked: [ ]

Ready for printing: [ ]

Ready for presentation: [ ]

Notes/Issues to address:
_________________________________________________________
_________________________________________________________
_________________________________________________________

---

## Quick Reference: Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Large white margins | Reduce margin in documentclass: `margin=5mm` |
| Text too small | Increase scale: `scale=1.5` in beamerposter |
| Blurry figures | Use vector graphics (PDF) or higher resolution (600+ DPI) |
| Colors wrong | Check RGB vs CMYK, test print before final |
| Fonts not embedded | Compile with: `pdflatex -dEmbedAllFonts=true` |
| Content cut off | Check total width: columns + spacing + margins = pagewidth |
| QR codes don't scan | Increase size (min 2×2cm), ensure high contrast |
| File too large | Compress: `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/printer ...` |

## Checklist Version
Version 1.0 - For use with LaTeX poster packages (beamerposter, tikzposter, baposter)

### `assets/tikzposter_template.tex`

```latex
% ==============================================================================
% Research Poster Template - tikzposter
% ==============================================================================
% A modern, colorful poster template using tikzposter
% Customize themes, colors, and content as needed
% ==============================================================================

\documentclass[
  25pt,                      % Font scaling
  a0paper,                   % Paper size
  portrait,                  % Orientation
  margin=10mm,               % Outer margins (minimal for full page)
  innermargin=15mm,          % Space inside blocks
  blockverticalspace=15mm,   % Space between blocks
  colspace=15mm,             % Space between columns
  subcolspace=8mm            % Space between subcolumns
]{tikzposter}

% Packages
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{qrcode}
\usepackage{hyperref}

% Theme selection (uncomment your choice)
\usetheme{Rays}           % Modern with radiating background
% \usetheme{Wave}         % Clean with decorative wave
% \usetheme{Board}        % Board-style with texture
% \usetheme{Envelope}     % Minimal with envelope corners
% \usetheme{Default}      % Professional with lines

% Color style (uncomment your choice)
\usecolorstyle{Denmark}   % Professional blue
% \usecolorstyle{Australia} % Warm colors
% \usecolorstyle{Sweden}    % Cool tones
% \usecolorstyle{Britain}   % Earth tones

% Custom color scheme (optional - comment out if using built-in)
% \definecolorstyle{CustomStyle}{
%   \definecolor{colorOne}{RGB}{0,51,102}      % Dark blue
%   \definecolor{colorTwo}{RGB}{255,204,0}     % Gold
%   \definecolor{colorThree}{RGB}{204,0,0}     % Red
% }{
%   % Background Colors
%   \colorlet{backgroundcolor}{white}
%   \colorlet{framecolor}{colorOne}
%   % Title Colors
%   \colorlet{titlefgcolor}{white}
%   \colorlet{titlebgcolor}{colorOne}
%   % Block Colors
%   \colorlet{blocktitlebgcolor}{colorOne}
%   \colorlet{blocktitlefgcolor}{white}
%   \colorlet{blockbodybgcolor}{white}
%   \colorlet{blockbodyfgcolor}{black}
% }
% \usecolorstyle{CustomStyle}

% ==============================================================================
% POSTER CONTENT - CUSTOMIZE BELOW
% ==============================================================================

\title{Your Research Title: Concise and Descriptive}
\author{Author One\textsuperscript{1}, Author Two\textsuperscript{2}, \underline{Presenting Author}\textsuperscript{1}}
\institute{
  \textsuperscript{1}Department, University Name, City, Country\\
  \textsuperscript{2}Research Institute Name, City, Country
}

% Title matter (logos)
\titlegraphic{
  \includegraphics[width=0.1\textwidth]{logo1.pdf}
  \hspace{3cm}
  \includegraphics[width=0.1\textwidth]{logo2.pdf}
}

\begin{document}

\maketitle

% ==============================================================================
% MAIN CONTENT - 3 COLUMN LAYOUT
% ==============================================================================

\begin{columns}
  
  % ============================================================================
  % LEFT COLUMN
  % ============================================================================
  \column{0.33}
  
  \block{Introduction}{
    \textbf{Background}
    
    Brief context about your research area. One to two sentences establishing the importance of the topic.
    
    \vspace{0.5cm}
    
    \textbf{Problem Statement}
    
    What gap or challenge does your work address? Why is this important? One to two sentences.
    
    \vspace{0.5cm}
    
    \textbf{Research Objective}
    
    Clear, concise statement of what you set out to do in this study.
  }
  
  \block{Methods}{
    \textbf{Study Design}
    \begin{itemize}
      \item Experimental approach or study type
      \item Sample size: n = X participants/samples
      \item Key inclusion/exclusion criteria
    \end{itemize}
    
    \vspace{0.5cm}
    
    \textbf{Procedures}
    \begin{itemize}
      \item Main experimental steps
      \item Key measurements or interventions
      \item Data collection approach
    \end{itemize}
    
    \vspace{0.5cm}
    
    \textbf{Analysis}
    \begin{itemize}
      \item Statistical methods used
      \item Software/tools (e.g., R 4.3, Python)
      \item Significance threshold (p < 0.05)
    \end{itemize}
    
    \vspace{0.5cm}
    
    % Optional: Methods flowchart
    \begin{tikzfigure}
      \includegraphics[width=0.9\linewidth]{methods_diagram.pdf}
    \end{tikzfigure}
  }
  
  % ============================================================================
  % MIDDLE COLUMN
  % ============================================================================
  \column{0.33}
  
  \block{Results: Finding 1}{
    Brief description of your first main result. What did you observe?
    
    \begin{tikzfigure}
      \includegraphics[width=0.95\linewidth]{figure1.pdf}
    \end{tikzfigure}
    
    \textbf{Figure 1:} Descriptive caption explaining the figure. Include key statistics (Mean ± SD, n=X, **p<0.01).
  }
  
  \block{Results: Finding 2}{
    Brief description of your second main result.
    
    \begin{tikzfigure}
      \includegraphics[width=0.95\linewidth]{figure2.pdf}
    \end{tikzfigure}
    
    \textbf{Figure 2:} Another key result showing comparison, trend, or correlation.
  }
  
  % ============================================================================
  % RIGHT COLUMN
  % ============================================================================
  \column{0.33}
  
  \block{Results: Finding 3}{
    Brief description of your third main result or validation.
    
    \begin{tikzfigure}
      \includegraphics[width=0.95\linewidth]{figure3.pdf}
    \end{tikzfigure}
    
    \textbf{Figure 3:} Additional important finding or supporting data.
  }
  
  \block{Conclusions}{
    \textbf{Key Findings}
    \begin{itemize}
      \item \textbf{Main conclusion 1:} Impact and significance
      \item \textbf{Main conclusion 2:} Novel contribution
      \item \textbf{Main conclusion 3:} Practical implications
    \end{itemize}
    
    \vspace{0.5cm}
    
    \textbf{Limitations}
    \begin{itemize}
      \item Brief acknowledgment of study constraints
      \item Context for result interpretation
    \end{itemize}
    
    \vspace{0.5cm}
    
    \textbf{Future Directions}
    \begin{itemize}
      \item Ongoing or planned follow-up studies
      \item Broader applications of findings
    \end{itemize}
  }
  
  \block{Scan for More}{
    \begin{center}
      \qrcode[height=5cm]{https://doi.org/10.1234/your-paper}\\
      \vspace{0.5cm}
      \large Full paper, code, and data
    \end{center}
  }
  
\end{columns}

% ==============================================================================
% FOOTER (Full Width)
% ==============================================================================

\block[width=1.0\linewidth]{}{
  \footnotesize
  \begin{minipage}{0.7\textwidth}
    \textbf{References}
    \begin{enumerate}
      \item Author A et al. (2023). Title of paper. \textit{Journal Name}, 10(2), 123-145. doi:10.xxxx/xxxxx
      \item Author B et al. (2024). Title of paper. \textit{Conference Proceedings}.
      \item Author C et al. (2022). Title of paper. \textit{Journal Name}, 15(3), 456-478.
    \end{enumerate}
    
    \vspace{0.3cm}
    
    \textbf{Acknowledgments:} This work was supported by Funding Agency (Grant \#12345). We thank collaborators at Institution X and the Core Facility for technical support.
    
    \vspace{0.3cm}
    
    \textbf{Contact:} presenter.email@university.edu | Twitter: @labname | Website: labname.university.edu
  \end{minipage}%
  \hfill
  \begin{minipage}{0.25\textwidth}
    \raggedleft
    Conference Name 2024\\
    Location, Dates\\
    Poster \#XXX
  \end{minipage}
}

\end{document}
```
