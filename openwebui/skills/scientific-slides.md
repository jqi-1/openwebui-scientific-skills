---
name: scientific-slides
description: OpenRouter API key for the skill's LLM-powered steps.
---

# Scientific Slides

## Overview

Scientific presentations are a critical medium for communicating research, sharing findings, and engaging with academic and professional audiences. This skill provides comprehensive guidance for creating effective scientific presentations, from structure and content development to visual design and delivery preparation.

**Key Focus**: Oral presentations for conferences, seminars, defenses, and professional talks.

**CRITICAL DESIGN PHILOSOPHY**: Scientific presentations should be VISUALLY ENGAGING and RESEARCH-BACKED. Avoid dry, text-heavy slides at all costs. Great scientific presentations combine:
- **Compelling visuals**: High-quality figures, images, diagrams (not just bullet points)
- **Research context**: Proper citations from research-lookup establishing credibility
- **Minimal text**: Bullet points as prompts, YOU provide the explanation verbally
- **Professional design**: Modern color schemes, strong visual hierarchy, generous white space
- **Story-driven**: Clear narrative arc, not just data dumps

**Remember**: Boring presentations = forgotten science. Make your slides visually memorable while maintaining scientific rigor through proper citations.

## When to Use This Skill

This skill should be used when:
- Preparing conference presentations (5-20 minutes)
- Developing academic seminars (45-60 minutes)
- Creating thesis or dissertation defense presentations
- Designing grant pitch presentations
- Preparing journal club presentations
- Giving research talks at institutions or companies
- Teaching or tutorial presentations on scientific topics

## Slide Generation with Nano Banana Pro

**This skill uses Nano Banana Pro AI to generate stunning presentation slides automatically.**

There are two workflows depending on output format:

### Default Workflow: PDF Slides (Recommended)

Generate each slide as a complete image using Nano Banana Pro, then combine into a PDF. This produces the most visually stunning results.

**How it works:**
1. **Plan the deck**: Create a detailed plan for each slide (title, key points, visual elements)
2. **Generate slides**: Call Nano Banana Pro for each slide to create complete slide images
3. **Combine to PDF**: Assemble slide images into a single PDF presentation

**Step 1: Plan Each Slide**

Before generating, create a detailed plan for your presentation:

```markdown
# Presentation Plan: Introduction to Machine Learning

## Slide 1: Title Slide
- Title: "Machine Learning: From Theory to Practice"
- Subtitle: "AI Conference 2025"
- Speaker: Dr. Jane Smith, University of XYZ
- Visual: Modern abstract neural network background

## Slide 2: Introduction
- Title: "Why Machine Learning Matters"
- Key points: Industry adoption, breakthrough applications, future potential
- Visual: Icons showing different ML applications (healthcare, finance, robotics)

## Slide 3: Core Concepts
- Title: "The Three Types of Learning"
- Content: Supervised, Unsupervised, Reinforcement
- Visual: Three-part diagram showing each type with examples

... (continue for all slides)
```

**Step 2: Generate Each Slide**

Use the `generate_slide_image.py` script to create each slide.

**CRITICAL: Formatting Consistency Protocol**

To ensure unified formatting across all slides in a presentation:

1. **Define a Formatting Goal** at the start of your presentation and include it in EVERY prompt:
   - Color scheme (e.g., "dark blue background, white text, gold accents")
   - Typography style (e.g., "bold sans-serif titles, clean body text")
   - Visual style (e.g., "minimal, professional, corporate aesthetic")
   - Layout approach (e.g., "generous white space, left-aligned content")

2. **Always attach the previous slide** when generating subsequent slides using `--attach`:
   - This allows Nano Banana Pro to see and match the existing style
   - Creates visual continuity throughout the deck
   - Ensures consistent colors, fonts, and design language

3. **Default author is "K-Dense"** unless another name is specified

4. **Include citations directly in the prompt** for slides that reference research:
   - Add citations in the prompt text so they appear on the generated slide
   - Use format: "Include citation: (Author et al., Year)" or "Show reference: Author et al., Year"
   - For multiple citations, list them all in the prompt
   - Citations should appear in small text at the bottom of the slide or near relevant content

5. **Attach existing figures/data for results slides** (CRITICAL for data-driven presentations):
   - When creating slides about results, ALWAYS check for existing figures in:
     - The working directory (e.g., `figures/`, `results/`, `plots/`, `images/`)
     - User-provided input files or directories
     - Any data visualizations, charts, or graphs relevant to the presentation
   - Use `--attach` to include these figures so Nano Banana Pro can incorporate them:
     - Attach the actual data figure/chart for results slides
     - Attach relevant diagrams for methodology slides
     - Attach logos or institutional images for title slides
   - When attaching data figures, describe what you want in the prompt:
     - "Create a slide presenting the attached results chart with key findings highlighted"
     - "Build a slide around this attached figure, add title and bullet points explaining the data"
     - "Incorporate the attached graph into a results slide with interpretation"
   - **Before generating results slides**: List files in the working directory to find relevant figures
   - Multiple figures can be attached: `--attach fig1.png --attach fig2.png`

**Example with formatting consistency, citations, and figure attachments:**

```bash
# Title slide (first slide - establishes the style)
python scripts/generate_slide_image.py "Title slide for presentation: 'Machine Learning: From Theory to Practice'. Subtitle: 'AI Conference 2025'. Speaker: K-Dense. FORMATTING GOAL: Dark blue background (#1a237e), white text, gold accents (#ffc107), minimal design, sans-serif fonts, generous margins, no decorative elements." -o slides/01_title.png

# Content slide with citations (attach previous slide for consistency)
python scripts/generate_slide_image.py "Presentation slide titled 'Why Machine Learning Matters'. Three key points with simple icons: 1) Industry adoption, 2) Breakthrough applications, 3) Future potential. CITATIONS: Include at bottom in small text: (LeCun et al., 2015; Goodfellow et al., 2016). FORMATTING GOAL: Match attached slide style - dark blue background, white text, gold accents, minimal professional design, no visual clutter." -o slides/02_intro.png --attach slides/01_title.png

# Background slide with multiple citations
python scripts/generate_slide_image.py "Presentation slide titled 'Deep Learning Revolution'. Key milestones: ImageNet breakthrough (2012), transformer architecture (2017), GPT models (2018-present). CITATIONS: Show references at bottom: (Krizhevsky et al., 2012; Vaswani et al., 2017; Brown et al., 2020). FORMATTING GOAL: Match attached slide style exactly - same colors, fonts, minimal design." -o slides/03_background.png --attach slides/02_intro.png

# RESULTS SLIDE - Attach actual data figure from working directory
# First, check what figures exist: ls figures/ or ls results/
python scripts/generate_slide_image.py "Presentation slide titled 'Model Performance Results'. Create a slide presenting the attached accuracy chart. Key findings to highlight: 1) 95% accuracy achieved, 2) Outperforms baseline by 12%, 3) Consistent across test sets. CITATIONS: Include at bottom: (Our results, 2025). FORMATTING GOAL: Match attached slide style exactly." -o slides/04_results.png --attach slides/03_background.png --attach figures/accuracy_chart.png

# RESULTS SLIDE - Multiple figures comparison
python scripts/generate_slide_image.py "Presentation slide titled 'Before vs After Comparison'. Build a side-by-side comparison slide using the two attached figures. Left: baseline results, Right: our improved results. Add brief labels explaining the improvement. FORMATTING GOAL: Match attached slide style exactly." -o slides/05_comparison.png --attach slides/04_results.png --attach figures/baseline.png --attach figures/improved.png

# METHODOLOGY SLIDE - Attach existing diagram
python scripts/generate_slide_image.py "Presentation slide titled 'System Architecture'. Present the attached architecture diagram with brief explanatory bullet points: 1) Input processing, 2) Model inference, 3) Output generation. FORMATTING GOAL: Match attached slide style exactly." -o slides/06_architecture.png --attach slides/05_comparison.png --attach diagrams/system_architecture.png
```

**IMPORTANT: Before creating results slides, always:**
1. List files in working directory: `ls -la figures/` or `ls -la results/`
2. Check user-provided directories for relevant figures
3. Attach ALL relevant figures that should appear on the slide
4. Describe how Nano Banana Pro should incorporate the attached figures

**Prompt Template:**

Include these elements in every prompt (customize as needed):
```
[Slide content description]
CITATIONS: Include at bottom: (Author1 et al., Year; Author2 et al., Year)
FORMATTING GOAL: [Background color], [text color], [accent color], minimal professional design, no decorative elements, consistent with attached slide style.
```

**Step 3: Combine to PDF**

```bash
# Combine all slides into a PDF presentation
python scripts/slides_to_pdf.py slides/*.png -o presentation.pdf
```

### PPT Workflow: PowerPoint with Generated Visuals

When creating PowerPoint presentations, use Nano Banana Pro to generate images and figures for each slide, then add text separately using the PPTX skill.

**How it works:**
1. **Plan the deck**: Create content plan for each slide
2. **Generate visuals**: Use Nano Banana Pro with `--visual-only` flag to create images for slides
3. **Build PPTX**: Use the PPTX skill (html2pptx or template-based) to create slides with generated visuals and separate text

**Step 1: Generate Visuals for Each Slide**

```bash
# Generate a figure for the introduction slide
python scripts/generate_slide_image.py "Professional illustration showing machine learning applications: healthcare diagnosis, financial analysis, autonomous vehicles, and robotics. Modern flat design, colorful icons on white background." -o figures/ml_applications.png --visual-only

# Generate a diagram for the methods slide
python scripts/generate_slide_image.py "Neural network architecture diagram showing input layer, three hidden layers, and output layer. Clean, technical style with node connections. Blue and gray color scheme." -o figures/neural_network.png --visual-only

# Generate a conceptual graphic for results
python scripts/generate_slide_image.py "Before and after comparison showing improvement: left side shows cluttered data, right side shows organized insights. Arrow connecting them. Professional business style." -o figures/results_visual.png --visual-only
```

**Step 2: Build PowerPoint with PPTX Skill**

Use the PPTX skill's html2pptx workflow to create slides that include:
- Generated images from step 1
- Title and body text added separately
- Professional layout and formatting

See `skills/pptx/SKILL.md` for complete PPTX creation documentation.

---

## Visual Enhancement with Scientific Schematics

In addition to slide generation, use the **scientific-schematics** skill for technical diagrams:

**When to use scientific-schematics instead:**
- Complex technical diagrams (circuit diagrams, chemical structures)
- Publication-quality figures for papers (higher quality threshold)
- Diagrams requiring scientific accuracy review

**How to generate schematics:**
```bash
python scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

For detailed guidance on creating schematics, refer to the scientific-schematics skill documentation.

---

## Core Capabilities

Presentation structure and organization, slide design principles, data visualization for
slides, talk-specific guidance, implementation options (Beamer / PowerPoint / generated
PDF), visual review and iteration, timing and pacing, and validation are all documented
in [references/slide_capabilities.md](references/slide_capabilities.md).

The staged development process — planning, design and creation, content development,
visual validation, practice and refinement, and final preparation — is in
[references/presentation_workflow.md](references/presentation_workflow.md).

Prompt-writing guidance for both full-slide and visual-only generation is in
[references/prompt_writing.md](references/prompt_writing.md). Every bundled script's
arguments and options are in
[references/script_reference.md](references/script_reference.md). The mistakes that most
often sink a talk are catalogued in
[references/common_pitfalls.md](references/common_pitfalls.md).

## Integration with Other Skills

**Research Lookup** (Critical for Scientific Presentations):
- **Background development**: Search literature to build introduction context
- **Citation gathering**: Find key papers to cite in your talk
- **Gap identification**: Identify what's unknown to motivate research
- **Prior work comparison**: Find papers to compare your results against
- **Supporting evidence**: Locate literature supporting your interpretations
- **Question preparation**: Find papers that might inform Q&A responses
- **Always use research-lookup** when developing any scientific presentation to ensure proper context and citations

**Scientific Writing**:
- Convert paper content to presentation format
- Extract key findings and simplify
- Use same figures (but redesigned for slides)
- Maintain consistent terminology

**PPTX Skill**:
- Use for PowerPoint creation and editing
- Leverage scripts for template workflows
- Use thumbnail generation for validation
- Reference html2pptx for programmatic creation

**Data Visualization**:
- Create presentation-appropriate figures
- Simplify complex visualizations
- Ensure readability from distance
- Use progressive disclosure

## Reference Files

Comprehensive guides for specific aspects:

- **`references/presentation_structure.md`**: Detailed structure for all talk types, timing allocation, opening/closing strategies, transition techniques
- **`references/slide_design_principles.md`**: Typography, color theory, layout, accessibility, visual hierarchy, design workflow
- **`references/data_visualization_slides.md`**: Simplifying figures, chart types, progressive disclosure, common mistakes, recreation workflow
- **`references/talk_types_guide.md`**: Specific guidance for conferences, seminars, defenses, grants, journal clubs, with examples
- **`references/beamer_guide.md`**: Complete LaTeX Beamer documentation, themes, customization, advanced features, compilation
- **`references/visual_review_workflow.md`**: PDF to images conversion, systematic inspection, issue documentation, iterative improvement

- **`references/slide_capabilities.md`**: presentation structure, design principles, data visualization, talk types, implementation options, visual review, timing, validation
- **`references/presentation_workflow.md`**: the six development stages from planning to final preparation
- **`references/prompt_writing.md`**: full-slide and visual-only prompt patterns
- **`references/script_reference.md`**: arguments and options for every bundled script
- **`references/common_pitfalls.md`**: content, design, and timing mistakes to avoid

## Assets

### Templates

- **`assets/beamer_template_conference.tex`**: 15-minute conference talk template
- **`assets/beamer_template_seminar.tex`**: 45-minute academic seminar template
- **`assets/beamer_template_defense.tex`**: Dissertation defense template

### Guides

- **`assets/powerpoint_design_guide.md`**: Complete PowerPoint design and implementation guide
- **`assets/timing_guidelines.md`**: Comprehensive timing, pacing, and practice strategies

## Quick Start Guide

### For a 15-Minute Conference Talk (PDF Workflow - Recommended)

1. **Research & Plan** (45 minutes):
   - **Use research-lookup** to find 8-12 relevant papers for citations
   - Build reference list (background, comparison studies)
   - Outline content (intro → methods → 2-3 key results → conclusion)
   - **Create detailed plan for each slide** (title, key points, visual elements)
   - Target 15-18 slides

2. **Generate Slides with Nano Banana Pro** (1-2 hours):
   
   **Important: Use consistent formatting, attach previous slides, and include citations!**
   
   ```bash
   # Title slide (establishes style - default author: K-Dense)
   python scripts/generate_slide_image.py "Title slide: 'Your Research Title'. Conference name, K-Dense. FORMATTING GOAL: [your color scheme], minimal professional design, no decorative elements, clean and corporate." -o slides/01_title.png
   
   # Introduction slide with citations (attach previous for consistency)
   python scripts/generate_slide_image.py "Slide titled 'Why This Matters'. Three key points with simple icons. CITATIONS: Include at bottom: (Smith et al., 2023; Jones et al., 2024). FORMATTING GOAL: Match attached slide style exactly." -o slides/02_intro.png --attach slides/01_title.png
   
   # Continue for each slide (always attach previous, include citations where relevant)
   python scripts/generate_slide_image.py "Slide titled 'Methods'. Key methodology points. CITATIONS: (Based on Chen et al., 2022). FORMATTING GOAL: Match attached slide style exactly." -o slides/03_methods.png --attach slides/02_intro.png
   
   # Combine to PDF
   python scripts/slides_to_pdf.py slides/*.png -o presentation.pdf
   ```

3. **Review & Iterate** (30 minutes):
   - Open the PDF and review each slide
   - Regenerate any slides that need improvement
   - Re-combine to PDF

4. **Practice** (2-3 hours):
   - Practice 3-5 times with timer
   - Aim for 13-14 minutes (leave buffer)
   - Record yourself, watch playback
   - **Prepare for questions** (use research-lookup to anticipate)

5. **Finalize** (30 minutes):
   - Generate backup/appendix slides if needed
   - Save multiple copies
   - Test on presentation computer

Total time: ~5-6 hours for quality AI-generated presentation

### Alternative: PowerPoint Workflow

If you need editable slides (e.g., for company templates):

1. **Plan slides** as above
2. **Generate visuals** with `--visual-only` flag:
   ```bash
   python scripts/generate_slide_image.py "diagram description" -o figures/fig1.png --visual-only
   ```
3. **Build PPTX** using the PPTX skill with generated images
4. **Add text** separately using PPTX workflow

See `skills/pptx/SKILL.md` for complete PowerPoint workflow.

## Summary: Key Principles

1. **Visual-First Design**: Every slide needs strong visual element (figure, image, diagram) - avoid text-only slides
2. **Research-Backed**: Use research-lookup to find 8-15 papers, cite 3-5 in intro, 3-5 in discussion
3. **Modern Aesthetics**: Choose contemporary color palette matching topic, not default themes
4. **Minimal Text**: 3-4 bullets, 4-6 words each (24-28pt font), let visuals tell story
5. **Structure**: Follow story arc, spend 40-50% on results
6. **High Contrast**: 7:1 preferred for professional appearance
7. **Varied Layouts**: Mix full-figure, two-column, visual overlays (not all bullets)
8. **Timing**: Practice 3-5 times, ~1 slide per minute, never skip conclusions
9. **Validation**: Visual review workflow to catch overflow and overlap
10. **White Space**: 40-50% of slide empty for visual breathing room

**Remember**: 
- **Boring = Forgotten**: Dry, text-heavy slides fail to communicate your science
- **Visual + Research = Impact**: Combine compelling visuals with research-backed context
- **You are the presentation, slides are visual support**: They should enhance, not replace your talk

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/scientific-slides/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/beamer_guide.md`

# LaTeX Beamer Guide for Scientific Presentations

## Overview

Beamer is a LaTeX document class for creating presentations with professional, consistent formatting. It's particularly well-suited for scientific presentations containing equations, code, algorithms, and citations. This guide covers Beamer basics, themes, customization, and advanced features for effective scientific talks.

## Why Use Beamer?

### Advantages

**Professional Quality**:
- Consistent, polished appearance
- Beautiful typography (especially for math)
- Publication-quality output
- Professional themes and templates

**Scientific Content**:
- Native equation support (LaTeX math)
- Code listings with syntax highlighting
- Algorithm environments
- Bibliography integration
- Cross-referencing

**Reproducibility**:
- Plain text source (version control friendly)
- Programmatic figure generation
- Consistent styling across presentations
- Easy to maintain and update

**Efficiency**:
- Reuse content across presentations
- Template once, use forever
- Automated elements (page numbers, navigation)
- No manual formatting

### Disadvantages

**Learning Curve**:
- Requires LaTeX knowledge
- Compilation time
- Debugging can be challenging
- Less WYSIWYG than PowerPoint

**Flexibility**:
- Complex custom layouts require effort
- Image editing requires external tools
- Some design elements easier in PowerPoint
- Animations more limited

**Collaboration**:
- Not ideal for non-LaTeX users
- Version conflicts possible
- Requires LaTeX installation

## Basic Beamer Document Structure

### Minimal Example

```latex
\documentclass{beamer}

% Theme
\usetheme{Madrid}
\usecolortheme{beaver}

% Title information
\title{Your Presentation Title}
\subtitle{Optional Subtitle}
\author{Your Name}
\institute{Your Institution}
\date{\today}

\begin{document}

% Title slide
\begin{frame}
  \titlepage
\end{frame}

% Content slide
\begin{frame}{Slide Title}
  Content goes here
\end{frame}

\end{document}
```

### Essential Packages

```latex
\documentclass{beamer}

% Encoding and fonts
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

% Graphics
\usepackage{graphicx}
\graphicspath{{./figures/}}

% Math
\usepackage{amsmath, amssymb, amsthm}

% Tables
\usepackage{booktabs}
\usepackage{multirow}

% Colors
\usepackage{xcolor}

% Algorithms
\usepackage{algorithm}
\usepackage{algorithmic}

% Code listings
\usepackage{listings}

% Citations
\usepackage[style=authoryear,backend=biber]{biblatex}
\addbibresource{references.bib}
```

### Frame Basics

```latex
% Basic frame
\begin{frame}{Title}
  Content
\end{frame}

% Frame with subtitle
\begin{frame}{Title}{Subtitle}
  Content
\end{frame}

% Frame without title
\begin{frame}
  Content
\end{frame}

% Fragile frame (for verbatim/code)
\begin{frame}[fragile]{Code Example}
  \begin{verbatim}
  def hello():
      print("Hello")
  \end{verbatim}
\end{frame}

% Plain frame (no header/footer)
\begin{frame}[plain]
  Full slide content
\end{frame}
```

## Themes and Appearance

### Presentation Themes

Beamer includes many built-in themes controlling overall layout:

**Classic Themes**:
```latex
\usetheme{Berlin}      % Sections in header
\usetheme{Copenhagen}  % Minimal, clean
\usetheme{Madrid}      % Professional, rounded
\usetheme{Boadilla}    % Simple footer
\usetheme{AnnArbor}    % Vertical navigation
```

**Modern Themes**:
```latex
\usetheme{CambridgeUS}  % Blue theme
\usetheme{Singapore}    % Minimalist
\usetheme{Rochester}    % Very minimal
\usetheme{Antibes}      % Tree navigation
```

**Popular for Science**:
```latex
% Clean and minimal
\usetheme{default}
\usetheme{Copenhagen}

% Professional with navigation
\usetheme{Madrid}
\usetheme{Berlin}

% Traditional academic
\usetheme{Pittsburgh}
\usetheme{Boadilla}
```

### Color Themes

```latex
% Blue themes
\usecolortheme{default}      % Blue
\usecolortheme{dolphin}      % Cyan-blue
\usecolortheme{seagull}      % Grayscale

% Warm themes
\usecolortheme{beaver}       % Red/brown
\usecolortheme{rose}         % Pink/red

% Nature themes
\usecolortheme{orchid}       % Purple
\usecolortheme{crane}        % Orange/yellow

% Professional
\usecolortheme{albatross}    % Gray/blue
```

### Font Themes

```latex
\usefonttheme{default}              % Standard
\usefonttheme{serif}                % Serif fonts
\usefonttheme{structurebold}        % Bold structure
\usefonttheme{structureitalicserif} % Italic serif
\usefonttheme{professionalfonts}    % Professional fonts
```

### Custom Colors

```latex
% Define custom colors
\definecolor{myblue}{RGB}{0,115,178}
\definecolor{myred}{RGB}{214,40,40}

% Apply to theme elements
\setbeamercolor{structure}{fg=myblue}
\setbeamercolor{title}{fg=myred}
\setbeamercolor{frametitle}{fg=myblue,bg=white}
\setbeamercolor{block title}{fg=white,bg=myblue}
```

### Minimal Custom Theme

```latex
% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Page numbers
\setbeamertemplate{footline}[frame number]

% Simple itemize
\setbeamertemplate{itemize items}[circle]

% Clean blocks
\setbeamertemplate{blocks}[rounded][shadow=false]

% Colors
\setbeamercolor{structure}{fg=blue!70!black}
\setbeamercolor{title}{fg=black}
\setbeamercolor{frametitle}{fg=blue!70!black}
```

## Content Elements

### Lists

**Itemize**:
```latex
\begin{frame}{Bullet Points}
  \begin{itemize}
    \item First point
    \item Second point
      \begin{itemize}
        \item Nested point
      \end{itemize}
    \item Third point
  \end{itemize}
\end{frame}
```

**Enumerate**:
```latex
\begin{frame}{Numbered List}
  \begin{enumerate}
    \item First item
    \item Second item
    \item Third item
  \end{enumerate}
\end{frame}
```

**Description**:
```latex
\begin{frame}{Definitions}
  \begin{description}
    \item[Term 1] Definition of term 1
    \item[Term 2] Definition of term 2
  \end{description}
\end{frame}
```

### Columns

```latex
\begin{frame}{Two Column Layout}
  \begin{columns}
    
    % Left column
    \begin{column}{0.5\textwidth}
      \begin{itemize}
        \item Point 1
        \item Point 2
      \end{itemize}
    \end{column}
    
    % Right column
    \begin{column}{0.5\textwidth}
      \includegraphics[width=\textwidth]{figure.png}
    \end{column}
    
  \end{columns}
\end{frame}
```

**Three Column Layout**:
```latex
\begin{columns}[T] % Align at top
  \begin{column}{0.32\textwidth}
    Content A
  \end{column}
  \begin{column}{0.32\textwidth}
    Content B
  \end{column}
  \begin{column}{0.32\textwidth}
    Content C
  \end{column}
\end{columns}
```

### Figures

```latex
\begin{frame}{Figure Example}
  \begin{figure}
    \centering
    \includegraphics[width=0.8\textwidth]{figure.pdf}
    \caption{Figure caption text}
  \end{figure}
\end{frame}
```

**Side-by-Side Figures**:
```latex
\begin{frame}{Comparison}
  \begin{columns}
    \begin{column}{0.5\textwidth}
      \includegraphics[width=\textwidth]{fig1.pdf}
      \caption{Condition A}
    \end{column}
    \begin{column}{0.5\textwidth}
      \includegraphics[width=\textwidth]{fig2.pdf}
      \caption{Condition B}
    \end{column}
  \end{columns}
\end{frame}
```

**Subfigures**:
```latex
\usepackage{subcaption}

\begin{frame}{Multiple Panels}
  \begin{figure}
    \centering
    \begin{subfigure}{0.45\textwidth}
      \includegraphics[width=\textwidth]{fig1.pdf}
      \caption{Panel A}
    \end{subfigure}
    \hfill
    \begin{subfigure}{0.45\textwidth}
      \includegraphics[width=\textwidth]{fig2.pdf}
      \caption{Panel B}
    \end{subfigure}
    \caption{Overall figure caption}
  \end{figure}
\end{frame}
```

### Tables

```latex
\begin{frame}{Table Example}
  \begin{table}
    \centering
    \begin{tabular}{lcc}
      \toprule
      Method & Accuracy & Time \\
      \midrule
      Method A & 0.85 & 10s \\
      Method B & 0.92 & 25s \\
      Method C & 0.88 & 15s \\
      \bottomrule
    \end{tabular}
    \caption{Performance comparison}
  \end{table}
\end{frame}
```

### Blocks

**Standard Blocks**:
```latex
\begin{frame}{Block Examples}
  
  % Standard block
  \begin{block}{Block Title}
    Block content goes here
  \end{block}
  
  % Alert block (red)
  \begin{alertblock}{Important}
    Warning or important information
  \end{alertblock}
  
  % Example block (green)
  \begin{exampleblock}{Example}
    Example content
  \end{exampleblock}
  
\end{frame}
```

**Theorem Environments**:
```latex
\begin{frame}{Mathematical Results}
  
  \begin{theorem}
    Statement of theorem
  \end{theorem}
  
  \begin{proof}
    Proof goes here
  \end{proof}
  
  \begin{definition}
    Definition text
  \end{definition}
  
  \begin{lemma}
    Lemma statement
  \end{lemma}
  
\end{frame}
```

## Overlays and Animations

### Progressive Disclosure with \pause

```latex
\begin{frame}{Revealing Content}
  First point appears immediately
  
  \pause
  
  Second point appears on click
  
  \pause
  
  Third point appears on another click
\end{frame}
```

### Overlay Specifications

**Itemize with Overlays**:
```latex
\begin{frame}{Sequential Bullets}
  \begin{itemize}
    \item<1-> Appears on slide 1 and stays
    \item<2-> Appears on slide 2 and stays
    \item<3-> Appears on slide 3 and stays
  \end{itemize}
\end{frame}
```

**Alternative Syntax**:
```latex
\begin{frame}{Sequential Bullets}
  \begin{itemize}[<+->]  % Automatically sequential
    \item First point
    \item Second point
    \item Third point
  \end{itemize}
\end{frame}
```

### Highlighting with Overlays

**Alert on Specific Slides**:
```latex
\begin{frame}{Highlighting}
  \begin{itemize}
    \item Normal text
    \item<2-| alert@2> Text highlighted on slide 2
    \item Normal text
  \end{itemize}
\end{frame}
```

**Temporary Appearance**:
```latex
\begin{frame}{Appearing and Disappearing}
  Appears on all slides
  
  \only<2>{Only visible on slide 2}
  
  \uncover<3->{Appears on slide 3 and stays}
  
  \visible<4->{Also appears on slide 4, but reserves space}
\end{frame}
```

### Building Complex Figures

```latex
\begin{frame}{Building a Figure}
  \begin{tikzpicture}
    % Base elements (always visible)
    \draw (0,0) rectangle (4,3);
    
    % Add on slide 2+
    \draw<2-> (1,1) circle (0.5);
    
    % Add on slide 3+
    \draw<3->[->, thick] (2,1.5) -- (3,2);
    
    % Highlight on slide 4
    \node<4>[red,thick] at (2,1.5) {Result};
  \end{tikzpicture}
\end{frame}
```

## Mathematical Content

### Equations

**Inline Math**:
```latex
\begin{frame}{Inline Math}
  The equation $E = mc^2$ is famous.
  
  We can also write $\alpha + \beta = \gamma$.
\end{frame}
```

**Display Math**:
```latex
\begin{frame}{Display Equations}
  Single equation:
  \begin{equation}
    f(x) = \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
  \end{equation}
  
  Multiple equations:
  \begin{align}
    E &= mc^2 \\
    F &= ma \\
    V &= IR
  \end{align}
\end{frame}
```

**Equation Arrays**:
```latex
\begin{frame}{Equation System}
  \begin{equation}
    \begin{cases}
      \dot{x} = f(x,y) \\
      \dot{y} = g(x,y)
    \end{cases}
  \end{equation}
\end{frame}
```

### Matrices

```latex
\begin{frame}{Matrix Example}
  \begin{equation}
    A = \begin{bmatrix}
      a_{11} & a_{12} & a_{13} \\
      a_{21} & a_{22} & a_{23} \\
      a_{31} & a_{32} & a_{33}
    \end{bmatrix}
  \end{equation}
\end{frame}
```

## Code and Algorithms

### Code Listings

```latex
\begin{frame}[fragile]{Python Code}
  \begin{lstlisting}[language=Python]
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
  \end{lstlisting}
\end{frame}
```

**Custom Code Styling**:
```latex
\lstset{
  language=Python,
  basicstyle=\ttfamily\small,
  keywordstyle=\color{blue},
  commentstyle=\color{green!60!black},
  stringstyle=\color{orange},
  numbers=left,
  numberstyle=\tiny,
  frame=single,
  breaklines=true
}

\begin{frame}[fragile]{Styled Code}
  \begin{lstlisting}
  # This is a comment
  def hello(name):
      """Greet someone"""
      print(f"Hello, {name}")
  \end{lstlisting}
\end{frame}
```

### Algorithms

```latex
\begin{frame}{Algorithm Example}
  \begin{algorithm}[H]
    \caption{Quicksort}
    \begin{algorithmic}[1]
      \REQUIRE Array $A$, indices $low$, $high$
      \ENSURE Sorted array
      \IF{$low < high$}
        \STATE $pivot \gets partition(A, low, high)$
        \STATE $quicksort(A, low, pivot-1)$
        \STATE $quicksort(A, pivot+1, high)$
      \ENDIF
    \end{algorithmic}
  \end{algorithm}
\end{frame}
```

## Citations and Bibliography

### Inline Citations

```latex
\begin{frame}{Background}
  Previous work \cite{smith2020} showed that...
  
  Multiple studies \cite{jones2019,brown2021} have found...
  
  According to \textcite{davis2022}, the method works by...
\end{frame}
```

### Bibliography Slide

```latex
% At end of presentation
\begin{frame}[allowframebreaks]{References}
  \printbibliography
\end{frame}
```

### Custom Bibliography Style

```latex
% In preamble
\usepackage[style=authoryear,maxbibnames=2,maxcitenames=2]{biblatex}
\addbibresource{references.bib}

% Smaller font for references
\renewcommand*{\bibfont}{\scriptsize}
```

## Advanced Features

### Section Organization

```latex
\section{Introduction}
\begin{frame}{Introduction}
  Content
\end{frame}

\section{Methods}
\begin{frame}{Methods}
  Content
\end{frame}

% Automatic outline
\begin{frame}{Outline}
  \tableofcontents
\end{frame}

% Outline at each section
\AtBeginSection{
  \begin{frame}{Outline}
    \tableofcontents[currentsection]
  \end{frame}
}
```

### Backup Slides

```latex
% Main presentation ends
\begin{frame}{Thank You}
  Questions?
\end{frame}

% Backup slides (not counted in numbering)
\appendix

\begin{frame}{Extra Data}
  Additional analysis for questions
\end{frame}

\begin{frame}{Detailed Methods}
  More methodological details
\end{frame}
```

### Hyperlinks

```latex
% Define labels
\begin{frame}{Main Result}
  \label{mainresult}
  This is the main finding.
\end{frame}

% Link to labeled frame
\begin{frame}{Reference}
  As shown in the \hyperlink{mainresult}{main result}...
\end{frame}

% External links
\begin{frame}{Resources}
  Visit \url{https://example.com} for more information.
  
  \href{https://github.com/user/repo}{GitHub Repository}
\end{frame}
```

### QR Codes

```latex
\usepackage{qrcode}

\begin{frame}{Scan for Paper}
  \begin{center}
    \qrcode[height=3cm]{https://doi.org/10.1234/paper}
    
    \vspace{0.5cm}
    Scan for full paper
  \end{center}
\end{frame}
```

### Multimedia

```latex
\usepackage{multimedia}

\begin{frame}{Video}
  \movie[width=8cm,height=6cm]{Click to play}{video.mp4}
\end{frame}
```

**Note**: Multimedia support varies by PDF viewer.

## TikZ Graphics

### Basic Shapes

```latex
\usepackage{tikz}

\begin{frame}{TikZ Example}
  \begin{tikzpicture}
    % Rectangle
    \draw (0,0) rectangle (2,1);
    
    % Circle
    \draw (3,0.5) circle (0.5);
    
    % Line with arrow
    \draw[->, thick] (0,0) -- (3,2);
    
    % Node with text
    \node at (1.5,2) {Label};
  \end{tikzpicture}
\end{frame}
```

### Flowcharts

```latex
\usetikzlibrary{shapes,arrows,positioning}

\begin{frame}{Workflow}
  \begin{tikzpicture}[node distance=2cm]
    \node[rectangle,draw] (start) {Start};
    \node[rectangle,draw,right=of start] (process) {Process};
    \node[rectangle,draw,right=of process] (end) {End};
    
    \draw[->,thick] (start) -- (process);
    \draw[->,thick] (process) -- (end);
  \end{tikzpicture}
\end{frame}
```

### Plots

```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

\begin{frame}{Data Plot}
  \begin{tikzpicture}
    \begin{axis}[
      xlabel={$x$},
      ylabel={$y$},
      width=8cm,
      height=6cm
    ]
    \addplot[blue,thick] coordinates {
      (0,0) (1,1) (2,4) (3,9)
    };
    \addplot[red,dashed] {x};
    \end{axis}
  \end{tikzpicture}
\end{frame}
```

## Compilation

### Basic Compilation

```bash
# Standard compilation
pdflatex presentation.tex

# With bibliography
pdflatex presentation.tex
biber presentation
pdflatex presentation.tex
pdflatex presentation.tex
```

### Modern Compilation (Recommended)

```bash
# Using latexmk (automated)
latexmk -pdf presentation.tex

# With continuous preview
latexmk -pdf -pvc presentation.tex
```

### Compilation Options

```bash
# Faster compilation (draft mode)
pdflatex -draftmode presentation.tex

# Specific engine
lualatex presentation.tex    # Better Unicode support
xelatex presentation.tex     # System fonts

# Output directory
pdflatex -output-directory=build presentation.tex
```

## Handouts and Notes

### Creating Handouts

```latex
% In preamble
\documentclass[handout]{beamer}

% This removes overlays and creates one frame per slide
```

### Speaker Notes

```latex
\usepackage{pgfpages}
\setbeameroption{show notes on second screen=right}

\begin{frame}{Slide Title}
  Slide content visible to audience
  
  \note{
    These notes are visible only to speaker:
    - Remember to emphasize X
    - Mention collaboration with Y
    - Expect question about Z
  }
\end{frame}
```

### Handout with Notes

```latex
\documentclass[handout]{beamer}
\usepackage{pgfpages}
\pgfpagesuselayout{2 on 1}[a4paper,border shrink=5mm]
```

## Best Practices

### Do's

- ✅ Use consistent theme throughout
- ✅ Keep equations simple and large
- ✅ Use progressive disclosure (\pause, overlays)
- ✅ Include frame numbers
- ✅ Use vector graphics (PDF) for figures
- ✅ Test compilation early and often
- ✅ Use meaningful section names
- ✅ Keep backup slides in appendix

### Don'ts

- ❌ Don't use too many different fonts or colors
- ❌ Don't fill slides with dense text
- ❌ Don't use tiny font sizes
- ❌ Don't include complex animations (limited support)
- ❌ Don't forget fragile frames for code
- ❌ Don't mix themes inconsistently
- ❌ Don't ignore compilation warnings

## Troubleshooting

### Common Issues

**Missing Fragile**:
```
Error: Verbatim environment in frame
Solution: Add [fragile] option to frame
```

**Package Conflicts**:
```
Error: Option clash for package X
Solution: Load package in preamble only once
```

**Image Not Found**:
```
Error: File `figure.pdf' not found
Solution: Check path, use \graphicspath, ensure file exists
```

**Overlay Issues**:
```
Problem: Overlays not working as expected
Solution: Check syntax <n-> vs <n-m>, test incremental builds
```

### Debugging Tips

```latex
% Show frame labels
\usepackage[notref,notcite]{showkeys}

% Draft mode (faster, shows boxes)
\documentclass[draft]{beamer}

% Verbose error messages
\errorcontextlines=999
```

## Templates and Examples

### Minimal Working Example

See `assets/beamer_template_conference.tex` for a complete, customizable template for conference talks.

### Resources

- Beamer User Guide: `texdoc beamer`
- Theme Gallery: https://deic.uab.cat/~iblanes/beamer_gallery/
- TikZ Examples: https://texample.net/tikz/

## Summary

Beamer excels at:
- Mathematical content
- Consistent professional formatting
- Reproducible presentations
- Version control
- Citations and cross-references

Choose Beamer when:
- Presentation contains significant math/equations
- You value version control and plain text
- Consistent styling is priority
- You're comfortable with LaTeX

Consider PowerPoint when:
- Extensive custom graphics needed
- Collaborating with non-LaTeX users
- Complex animations required
- Rapid prototyping needed

### `references/common_pitfalls.md`

# Common Pitfalls to Avoid

Content, design, and timing mistakes, with the corrections for each.

## Common Pitfalls to Avoid

### Content Mistakes

**Dry, Boring Presentations** (CRITICAL TO AVOID):
- Problem: Text-heavy slides with no visual interest, missing research context
- Signs: All bullet points, no images, default templates, no citations
- Solution: 
  - Use research-lookup to find 8-15 papers for credible context
  - Add high-quality visuals to EVERY slide (figures, photos, diagrams, icons)
  - Choose modern color palette reflecting your topic
  - Vary slide layouts (not all bullet lists)
  - Tell a story with visuals, use text sparingly

**Too Much Content**:
- Problem: Trying to include everything from paper
- Solution: Focus on 1-2 key findings for short talks, show visually

**Too Much Text**:
- Problem: Full paragraphs on slides, dense bullet points, reading verbatim
- Solution: 3-4 bullets with 4-6 words each, let visuals carry the message

**Missing Research Context**:
- Problem: No citations, claims without support, unclear positioning
- Solution: Use research-lookup to find papers, cite 3-5 in intro, 3-5 in discussion

**Poor Narrative**:
- Problem: Jumping between topics, no clear story, no flow
- Solution: Follow story arc, use visual transitions, maintain thread

**Rushing Through Results**:
- Problem: Brief methods, brief results, long discussion
- Solution: Spend 40-50% of time on results, show data visually

### Design Mistakes

**Generic, Default Appearance**:
- Problem: Using default PowerPoint/Beamer themes without customization, looks dated
- Solution: Choose modern color palette, customize fonts/layouts, add visual personality

**Text-Heavy, Visual-Poor**:
- Problem: All bullet point slides, no images or graphics, boring to look at
- Solution: Add figures, photos, diagrams, icons to EVERY slide, make visually interesting

**Small Fonts**:
- Problem: Body text <18pt, unreadable from back, looks unprofessional
- Solution: 24-28pt for body (not just 18pt minimum), 36-44pt for titles

**Low Contrast**:
- Problem: Light text on light background, poor visibility, hard to read
- Solution: High contrast (7:1 preferred, not just 4.5:1 minimum), test with contrast checker

**Cluttered Slides**:
- Problem: Too many elements, no white space, overwhelming
- Solution: One idea per slide, 40-50% white space, generous spacing

**Inconsistent Formatting**:
- Problem: Different fonts, colors, layouts slide-to-slide, looks amateurish
- Solution: Use master slides, maintain design system, professional consistency

**Missing Visual Hierarchy**:
- Problem: Everything same size and color, no emphasis, unclear focus
- Solution: Size differences (titles large, body medium), color for emphasis, clear focal point

### Timing Mistakes

**Not Practicing**:
- Problem: First time through is during presentation
- Solution: Practice minimum 3 times with timer

**No Time Checkpoints**:
- Problem: Don't realize running behind until too late
- Solution: Set 3-4 checkpoints, monitor throughout

**Going Over Time**:
- Problem: Extremely unprofessional, cuts into Q&A
- Solution: Practice to exact time, prepare Plan B (slides to skip)

**Skipping Conclusions**:
- Problem: Running out of time, rush through or skip ending
- Solution: Never skip conclusions, cut earlier content instead

### `references/data_visualization_slides.md`

# Data Visualization for Slides

## Overview

Effective data visualization in presentations differs fundamentally from journal figures. While publications prioritize comprehensive detail, presentation slides must emphasize clarity, impact, and immediate comprehension. This guide covers adapting figures for slides, choosing appropriate chart types, and avoiding common visualization mistakes.

## Key Principles for Presentation Figures

### 1. Simplify, Don't Replicate

**The Core Difference**:
- **Journal figures**: Dense, detailed, for careful study
- **Presentation figures**: Clear, simplified, for quick understanding

**Simplification Strategies**:

**Remove Non-Essential Elements**:
- ❌ Minor gridlines
- ❌ Detailed legends (label directly instead)
- ❌ Multiple panels (split into separate slides)
- ❌ Secondary axes (rarely work in presentations)
- ❌ Dense tick marks and minor labels

**Focus on Key Message**:
- Show only the data supporting your current point
- Subset data if full dataset is overwhelming
- Highlight the specific comparison you're discussing
- Remove context that isn't immediately relevant

**Example Transformation**:
```
Journal Figure:
- 6 panels (A-F)
- 4 experimental conditions per panel
- 50+ data points visible
- Complex statistical annotations
- Small font labels

Presentation Version:
- 3 separate slides (1-2 panels each)
- Focus on key comparison per slide
- Large, clear data representation
- One statistical result highlighted
- Large, readable labels
```

### 2. Emphasize Visual Hierarchy

**Guide Attention**:
- Make key result visually dominant
- De-emphasize background or comparison data
- Use size, color, and position strategically

**Techniques**:

**Color Emphasis**:
```
Main Result: Bold, saturated color (e.g., blue)
Comparison: Muted gray or desaturated color
Background: Very light gray or white
```

**Size Emphasis**:
```
Key line/bar: Thicker (3-4pt)
Reference lines: Thinner (1-2pt)
Grid lines: Very thin (0.5pt) or remove
```

**Annotation**:
```
Add text callouts: "34% increase" with arrow
Add shapes: Circle key region
Add color highlights: Background shading for important area
```

### 3. Maximize Readability

**Font Sizes for Presentations**:
- **Axis labels**: 18-24pt minimum
- **Tick labels**: 16-20pt minimum
- **Title**: 24-32pt
- **Legend**: 16-20pt (or label directly on plot)
- **Annotations**: 18-24pt

**The Distance Test**:
- If your figure isn't readable at 2-3 feet from your laptop screen, it won't work in a presentation
- Test by stepping back from screen
- Better to split into multiple simpler figures

**Line and Marker Sizes**:
- **Lines**: 2-4pt thickness (thicker than journal figures)
- **Markers**: 8-12pt size
- **Error bars**: 1.5-2pt thickness
- **Bars**: Adequate width with clear spacing

### 4. Use Progressive Disclosure

**Build Complex Figures Incrementally**:

Instead of showing complete figure at once:
1. **Baseline**: Show axes and basic setup
2. **Data Group 1**: Add first dataset
3. **Data Group 2**: Add comparison dataset
4. **Highlight**: Emphasize key difference
5. **Interpretation**: Add annotation with finding

**Benefits**:
- Controls audience attention
- Prevents information overload
- Guides interpretation
- Emphasizes narrative structure

**Implementation**:
- PowerPoint: Use animation to reveal layers
- Beamer: Use `\pause` or overlays
- Static: Create sequence of slides building the figure

## Chart Types and When to Use Them

### Bar Charts

**Best For**:
- Comparing discrete categories
- Showing counts or frequencies
- Highlighting differences between groups

**Presentation Optimization**:
```
✅ DO:
- Large, clear bars with adequate spacing
- Horizontal bars for long category names
- Direct labeling on bars (not legend)
- Order by value (highest to lowest) unless natural order exists
- Start y-axis at zero for accurate visual comparison

❌ DON'T:
- Too many categories (max 8-10)
- 3D bars (distorts perception)
- Multiple grouped comparisons (split to separate slides)
- Decorative patterns or gradients
```

**Example Enhancement**:
```
Before: 12 categories, small fonts, legend
After: Top 6 categories only, large fonts, direct labels, key bar highlighted
```

### Line Graphs

**Best For**:
- Trends over time
- Continuous data relationships
- Comparing trajectories

**Presentation Optimization**:
```
✅ DO:
- Thick lines (2-4pt)
- Distinct colors AND line styles (solid, dashed, dotted)
- Direct line labeling (at end of lines, not legend)
- Highlight key line with color/thickness
- Minimal gridlines or none
- Clear markers at data points

❌ DON'T:
- More than 4-5 lines per plot
- Similar colors (ensure high contrast)
- Small markers or thin lines
- Cluttered with excess gridlines
```

**Time Series Tips**:
- Mark key events or interventions with vertical lines
- Annotate important time points
- Use shaded regions for different phases

### Scatter Plots

**Best For**:
- Relationships between two variables
- Correlations
- Distributions
- Outliers

**Presentation Optimization**:
```
✅ DO:
- Large, distinct markers (8-12pt)
- Color code groups clearly
- Show trendline if discussing correlation
- Annotate key points (outliers, examples)
- Report R² or p-value directly on plot

❌ DON'T:
- Overplot (too many overlapping points)
- Small markers
- Multiple marker types that look similar
- Missing scale information
```

**Overplotting Solutions**:
- Transparency (alpha) for overlapping points
- Hexbin or density plots for very large datasets
- Random jitter for discrete data
- Marginal distributions on axes

### Box Plots / Violin Plots

**Best For**:
- Distribution comparisons
- Showing variability and outliers
- Multiple group comparisons

**Presentation Optimization**:
```
✅ DO:
- Large, clear boxes
- Color code groups
- Add individual data points if n is small (< 30)
- Annotate median or mean values
- Explain components (quartiles, whiskers) first time shown

❌ DON'T:
- Assume audience knows box plot conventions
- Use without brief explanation
- Too many groups (max 6-8)
- Omit axis labels and units
```

**First Use**:
If your audience may be unfamiliar, briefly explain: "Box shows middle 50% of data, line is median, whiskers show range"

### Heatmaps

**Best For**:
- Matrix data
- Gene expression or correlation patterns
- Large datasets with patterns

**Presentation Optimization**:
```
✅ DO:
- Large cells (readable grid)
- Clear, intuitive color scale (diverging or sequential)
- Label rows and columns with large fonts
- Show color scale legend prominently
- Cluster or order meaningfully
- Highlight key region with border

❌ DON'T:
- Too many rows/columns (200×200 matrix unreadable)
- Poor color scales (rainbow, red-green)
- Missing dendrograms if claiming clusters
- Tiny labels
```

**Simplification**:
- Show subset of most interesting rows/columns
- Zoom to relevant region
- Split large heatmap across multiple slides

### Network Diagrams

**Best For**:
- Relationships and connections
- Pathways and networks
- Hierarchical structures

**Presentation Optimization**:
```
✅ DO:
- Large nodes and labels
- Clear edge directionality (arrows)
- Color or size code importance
- Highlight path of interest
- Simplify to essential connections
- Use layout that minimizes crossing edges

❌ DON'T:
- Show entire complex network at once
- Hairball diagrams (too many connections)
- Small labels on nodes
- Unclear what nodes and edges represent
```

**Build Strategy**:
1. Show simplified structure
2. Add key nodes progressively
3. Highlight path or subnetwork of interest
4. Annotate with functional interpretation

### Statistical Plots

**Kaplan-Meier Survival Curves**:
```
✅ Optimize:
- Thick lines (3-4pt)
- Show confidence intervals as shaded regions
- Mark censored observations clearly
- Report hazard ratio and p-value on plot
- Extend axes to show full follow-up
```

**Forest Plots**:
```
✅ Optimize:
- Large markers (diamonds or squares)
- Clear confidence interval bars
- Large font for study names
- Highlight overall estimate
- Show line of no effect prominently
```

**ROC Curves**:
```
✅ Optimize:
- Thick curve line
- Show diagonal reference line (AUC = 0.5)
- Report AUC with confidence interval on plot
- Mark optimal threshold if discussing cutpoint
- Compare ≤ 3 curves per plot
```

## Color in Data Visualizations

### Sequential Color Scales

**When to Use**: Ordered data (low to high)

**Good Palettes**:
- Blues: Light blue → Dark blue
- Greens: Light green → Dark green  
- Grays: Light gray → Black
- Viridis: Yellow → Purple (perceptually uniform)

**Avoid**:
- Rainbow scales (non-uniform perception)
- Red-green scales (color blindness)

### Diverging Color Scales

**When to Use**: Data with meaningful midpoint (e.g., +/− change, correlation from -1 to +1)

**Good Palettes**:
- Blue → White → Red
- Purple → White → Orange
- Blue → Gray → Orange

**Key Principle**: Midpoint should be visually neutral (white or light gray)

### Categorical Colors

**When to Use**: Distinct groups with no order

**Good Practices**:
- Maximum 5-7 colors for clarity
- High contrast between adjacent categories
- Color-blind safe combinations
- Consistent color mapping across slides

**Example Set**:
```
Blue (#0173B2)
Orange (#DE8F05)
Green (#029E73)
Purple (#CC78BC)
Red (#CA3542)
```

### Highlight Colors

**Strategy**: Use color to direct attention

```
Main Result: Bright, saturated color (e.g., blue)
Comparison: Neutral (gray) or muted color
Background: Very light gray or white
```

**Example Application**:
- Bar chart: Key bar in blue, others in light gray
- Line plot: Main line in bold blue, reference lines in thin gray
- Scatter: Group of interest in color, others faded

## Common Visualization Mistakes

### Mistake 1: Overwhelming Complexity

**Problem**: Showing too much data at once

**Example**:
- Figure with 12 panels
- Each panel has 6 experimental conditions
- Tiny fonts and dense layout
- Audience has 10 seconds to process

**Solution**:
- Split into 3-4 slides
- One comparison per slide
- Focus on key result
- Build understanding progressively

### Mistake 2: Illegible Labels

**Problem**: Text too small to read

**Common Issues**:
- 8-10pt axis labels (need ≥18pt)
- Tiny legend text
- Subscripts and superscripts disappear
- Fine-print p-values

**Solution**:
- Recreate figures for presentation (don't use journal versions directly)
- Test readability from distance
- Remove or enlarge small text
- Put detailed statistics in notes

### Mistake 3: Chart Junk

**Problem**: Unnecessary decorative elements

**Examples**:
- 3D effects on 2D data
- Excessive gridlines
- Distracting backgrounds
- Decorative borders or shadows
- Animation for decoration only

**Solution**:
- Remove all non-data ink
- Maximize data-ink ratio
- Clean, minimal design
- Let data be the focus

### Mistake 4: Misleading Scales

**Problem**: Visual representation distorts data

**Examples**:
- Bar charts not starting at zero
- Truncated y-axes exaggerating differences
- Inconsistent scales between panels
- Log scales without clear labeling

**Solution**:
- Bar charts: Always start at zero
- Line charts: Can truncate, but make clear
- Label log scales explicitly
- Maintain consistent scales for comparisons

### Mistake 5: Poor Color Choices

**Problem**: Colors reduce clarity or accessibility

**Examples**:
- Red-green for color-blind audience
- Low contrast (yellow on white)
- Too many colors
- Inconsistent color meaning

**Solution**:
- Use color-blind safe palettes
- Test contrast (minimum 4.5:1)
- Limit to 5-7 colors maximum
- Consistent meaning across slides

### Mistake 6: Missing Context

**Problem**: Audience can't interpret visualization

**Missing Elements**:
- Axis labels or units
- Sample sizes (n)
- Error bar meaning (SEM vs SD vs CI)
- Statistical significance indicators
- Scale or reference points

**Solution**:
- Label everything clearly
- Define abbreviations
- Report key statistics on plot
- Provide reference for comparison

### Mistake 7: Inefficient Chart Type

**Problem**: Wrong visualization for data type

**Examples**:
- Pie chart for >5 categories (use bar chart)
- 3D pie chart (especially bad)
- Dual y-axes (confusing)
- Line plot for discrete categories (use bar chart)

**Solution**:
- Match chart type to data type
- Consider what comparison you're showing
- Choose format that makes pattern obvious
- Test if message is immediately clear

## Progressive Disclosure Techniques

### Building a Complex Figure

**Scenario**: Showing multi-panel experimental result

**Approach 1: Sequential Panels**
```
Slide 1: Panel A only (baseline condition)
Slide 2: Panels A+B (add treatment effect)
Slide 3: Panels A+B+C (add time course)
Slide 4: All panels with interpretation overlay
```

**Approach 2: Layered Data**
```
Slide 1: Axes and experimental design schematic
Slide 2: Add control group data
Slide 3: Add treatment group data
Slide 4: Highlight difference, show statistics
```

**Approach 3: Zoom and Context**
```
Slide 1: Full dataset overview
Slide 2: Zoom to interesting region
Slide 3: Highlight specific points in zoomed view
```

### Animation vs. Multiple Slides

**Use Animation** (PowerPoint/Beamer overlays):
- Building bullet points
- Adding layers to same plot
- Highlighting different regions sequentially
- Smooth transitions within a concept

**Use Separate Slides**:
- Different data or experiments
- Major conceptual shifts
- Want to return to previous view
- Need to control timing flexibly

## Figure Preparation Workflow

### Step 1: Start with High-Quality Source

**For Generated Figures**:
- Export at high resolution (300 DPI minimum)
- Vector formats preferred (PDF, SVG)
- Large size (can scale down, not up)
- Clean, professional appearance

**For Published Figures**:
- Request high-resolution versions from authors/publishers
- Recreate if source not available
- Check reuse permissions

### Step 2: Simplify for Presentation

**Edit in Graphics Software**:
- Remove non-essential panels
- Enlarge fonts and labels
- Increase line widths and marker sizes
- Remove or simplify legends
- Add direct labels
- Remove excess gridlines

**Tools**:
- Adobe Illustrator (vector editing)
- Inkscape (free vector editing)
- PowerPoint/Keynote (basic editing)
- Python/R (programmatic recreation)

### Step 3: Optimize for Projection

**Check**:
- ✅ Readable from 10 feet away
- ✅ High contrast between elements
- ✅ Large enough to fill significant slide area
- ✅ Maintains quality when projected
- ✅ Works in various lighting conditions

**Test**:
- View on different screens
- Project if possible before talk
- Print at small scale (simulates distance)
- Check in grayscale (color-blind simulation)

### Step 4: Add Context and Annotations

**Enhancements**:
- Arrows pointing to key features
- Text boxes with key findings ("p < 0.001")
- Circles or rectangles highlighting regions
- Color coding matched to verbal description
- Reference lines or benchmarks

**Verbal Integration**:
- Plan what you'll say about each element
- Use "Notice that..." or "Here you can see..."
- Point to specific features during talk
- Explain axes and scales first time shown

## Recreating Journal Figures for Presentations

### When to Recreate

**Recreate When**:
- Original has small fonts
- Too many panels for one slide
- Multiple comparisons to parse
- Colors not accessible
- Data available to you

**Reuse When**:
- Already simple and clear
- Appropriate font sizes
- Single focused message
- High resolution available
- Remaking not feasible

### Recreation Tools

**Python (matplotlib, seaborn)**:
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set presentation-friendly defaults
plt.rcParams['font.size'] = 18
plt.rcParams['axes.linewidth'] = 2
plt.rcParams['lines.linewidth'] = 3
plt.rcParams['figure.figsize'] = (10, 6)

# Create plot with large, clear elements
# Export as high-res PNG or PDF
```

**R (ggplot2)**:
```r
library(ggplot2)

# Presentation theme
theme_presentation <- theme_minimal() +
  theme(
    text = element_text(size = 18),
    axis.text = element_text(size = 16),
    axis.title = element_text(size = 20),
    legend.text = element_text(size = 16)
  )

# Apply to plots
ggplot(data, aes(x, y)) + geom_point(size=4) + theme_presentation
```

**GraphPad Prism**:
- Increase font sizes in Format Axes
- Thicken lines in Format Graph
- Enlarge symbols
- Export as high-resolution image

**Excel/PowerPoint**:
- Select chart, Format → Text Options → Size (increase to 18-24pt)
- Format → Line → Width (increase to 2-3pt)
- Format → Marker → Size (increase to 10-12pt)

## Summary Checklist

Before including a figure in your presentation:

**Clarity**:
- [ ] One clear message per figure
- [ ] Immediately understandable (< 5 seconds)
- [ ] Appropriate chart type for data
- [ ] Simplified from journal version (if applicable)

**Readability**:
- [ ] Font sizes ≥18pt for labels
- [ ] Thick lines (2-4pt) and large markers (8-12pt)
- [ ] High contrast colors
- [ ] Readable from back of room

**Design**:
- [ ] Minimal chart junk (removed gridlines, simplify)
- [ ] Axes clearly labeled with units
- [ ] Color-blind friendly palette
- [ ] Consistent style with other figures

**Context**:
- [ ] Sample sizes indicated (n)
- [ ] Statistical results shown (p-values, CI)
- [ ] Error bars defined (SE, SD, or CI?)
- [ ] Key finding annotated or highlighted

**Technical Quality**:
- [ ] High resolution (300 DPI minimum)
- [ ] Vector format preferred
- [ ] Properly sized for slide
- [ ] Quality maintained when projected

**Progressive Disclosure** (if complex):
- [ ] Plan for building figure incrementally
- [ ] Each step adds one new element
- [ ] Final version shows complete picture
- [ ] Animation or separate slides prepared

### `references/presentation_structure.md`

# Presentation Structure Guide

## Overview

Effective scientific presentations follow a clear narrative structure that guides the audience through your research story. This guide provides structure templates for different talk lengths and contexts, helping you organize content for maximum impact and clarity.

## Core Narrative Structure

All scientific presentations should follow a story arc that engages, informs, and persuades:

1. **Hook**: Grab attention immediately (30 seconds - 1 minute)
2. **Context**: Establish the research area and importance (5-10% of talk)
3. **Problem/Gap**: Identify what's unknown or problematic (5-10% of talk)
4. **Approach**: Explain your solution or method (15-25% of talk)
5. **Results**: Present key findings (40-50% of talk)
6. **Implications**: Discuss meaning and impact (15-20% of talk)
7. **Closure**: Memorable conclusion and call to action (1-2 minutes)

This arc mirrors the scientific method while maintaining narrative flow that keeps audiences engaged.

## Slide Count Guidelines

**General Rule**: Approximately 1 slide per minute, with adjustments based on content complexity.

| Talk Duration | Total Slides | Title/Intro | Methods | Results | Discussion | Conclusion |
|---------------|--------------|-------------|---------|---------|------------|------------|
| 5 minutes (lightning) | 5-7 | 1-2 | 0-1 | 2-3 | 1 | 1 |
| 10 minutes (short) | 10-12 | 2 | 1-2 | 4-5 | 2-3 | 1 |
| 15 minutes (conference) | 15-18 | 2-3 | 2-3 | 6-8 | 3-4 | 1-2 |
| 20 minutes (extended) | 20-24 | 3 | 3-4 | 8-10 | 4-5 | 2 |
| 30 minutes (seminar) | 25-30 | 3-4 | 5-6 | 10-12 | 6-8 | 2 |
| 45 minutes (keynote) | 35-45 | 4-5 | 8-10 | 15-20 | 8-10 | 2-3 |
| 60 minutes (lecture) | 45-60 | 5-6 | 10-12 | 20-25 | 10-12 | 3-4 |

**Adjustments**:
- **Complex data**: Reduce slide count (spend more time per slide)
- **Simple concepts**: Can increase slide count slightly
- **Heavy animations**: Count as multiple slides if building incrementally
- **Q&A included**: Reduce content slides by 20-30%

## Structure by Talk Length

### 5-Minute Lightning Talk

**Purpose**: Communicate one key idea quickly and memorably.

**Structure** (5-7 slides):
1. **Title slide** (15 seconds): Title, name, affiliation
2. **The Problem** (45 seconds): One compelling problem statement with visual
3. **Your Solution** (60 seconds): Core approach or finding (1 slide or 2 if showing before/after)
4. **Key Result** (90 seconds): Single most important finding with clear visualization
5. **Impact** (45 seconds): Why it matters, one key implication
6. **Closing** (30 seconds): Memorable takeaway, contact info

**Tips**:
- Focus on ONE message only
- Maximize visuals, minimize text
- Practice exact timing
- No methods details (mention in one sentence)
- Prepare for "tell me more" conversations after

### 10-Minute Conference Talk

**Purpose**: Present a complete research story with key findings.

**Structure** (10-12 slides):
1. **Title slide** (30 seconds)
2. **Hook + Context** (60 seconds): Compelling opening that establishes importance
3. **Problem Statement** (60 seconds): Knowledge gap or challenge
4. **Approach Overview** (60-90 seconds): High-level methods (1-2 slides)
5. **Key Results** (4-5 minutes): Main findings (4-5 slides)
   - Result 1: Primary finding
   - Result 2: Supporting evidence
   - Result 3: Additional validation or application
   - (Optional) Result 4: Extension or implication
6. **Interpretation** (90 seconds): What it means (1-2 slides)
7. **Conclusions** (45 seconds): Main takeaways
8. **Acknowledgments** (15 seconds): Funding, collaborators

**Tips**:
- Spend 40-50% of time on results
- Use build animations to control information flow
- Practice transitions between sections
- Leave 2-3 minutes for questions if Q&A is included
- Have 1-2 backup slides with extra data

### 15-Minute Conference Talk (Standard)

**Purpose**: Comprehensive presentation of a research project with detailed results.

**Structure** (15-18 slides):
1. **Title slide** (30 seconds)
2. **Opening Hook** (45 seconds): Attention-grabbing problem or statistic
3. **Background/Context** (90 seconds): Why this research area matters (1-2 slides)
4. **Knowledge Gap** (60 seconds): What's unknown or problematic
5. **Research Question/Hypothesis** (45 seconds): Clear statement of objectives
6. **Methods Overview** (2-3 minutes): Experimental design (2-3 slides)
   - Study design/participants
   - Key procedures or techniques
   - Analysis approach
7. **Results** (6-7 minutes): Detailed findings (6-8 slides)
   - Opening: Sample characteristics or validation
   - Main finding 1: Primary outcome with statistics
   - Main finding 2: Secondary outcome or subgroup
   - Main finding 3: Mechanism or extension
   - (Optional) Additional analyses or sensitivity tests
8. **Discussion** (2-3 minutes): Interpretation and context (3-4 slides)
   - Relationship to prior work
   - Mechanisms or explanations
   - Limitations
   - Implications
9. **Conclusions** (60 seconds): Key takeaways (1-2 slides)
10. **Acknowledgments + Questions** (30 seconds)

**Tips**:
- Budget time for each section and practice with timer
- Use section dividers or progress indicators
- Spend most time on results (40-45%)
- Anticipate likely questions and prepare backup slides
- Have a "Plan B" for running over (know which slides to skip)

### 20-Minute Extended Talk

**Purpose**: In-depth presentation with room for multiple studies or detailed methodology.

**Structure** (20-24 slides):

Similar to 15-minute talk but with:
- More detailed methods (3-4 slides with diagrams)
- Additional result categories or subanalyses
- More extensive discussion of prior work
- Deeper dive into one or two key findings
- More context on limitations and future directions

**Distribution**:
- Introduction: 3 minutes (3 slides)
- Methods: 4 minutes (3-4 slides)
- Results: 9 minutes (8-10 slides)
- Discussion: 3 minutes (4-5 slides)
- Conclusion: 1 minute (2 slides)

### 30-Minute Seminar

**Purpose**: Comprehensive research presentation with methodological depth.

**Structure** (25-30 slides):
1. **Opening** (2-3 minutes): Title, hook, outline (3-4 slides)
2. **Background** (4-5 minutes): Detailed context and prior work (4-5 slides)
3. **Research Questions** (1 minute): Clear objectives (1 slide)
4. **Methods** (5-6 minutes): Detailed methodology (5-6 slides)
   - Study design with rationale
   - Participants/materials
   - Procedures (possibly multiple slides)
   - Analysis plan
   - Validation or pilot data
5. **Results** (10-12 minutes): Comprehensive findings (10-12 slides)
   - Demographics/baseline
   - Primary analyses (multiple slides)
   - Secondary analyses
   - Subgroup analyses
   - Sensitivity analyses
   - Summary visualization
6. **Discussion** (5-6 minutes): Interpretation and implications (6-8 slides)
   - Summary of findings
   - Comparison to literature (multiple references)
   - Mechanisms
   - Strengths and limitations (detailed)
   - Clinical/practical implications
   - Future directions
7. **Conclusions** (1-2 minutes): Key messages (2 slides)
8. **Acknowledgments/Questions** (1 minute)

**Tips**:
- Include an outline slide showing talk structure
- Use section headers to maintain orientation
- Can include animations and builds for complex concepts
- More detailed methods are expected
- Address potential objections proactively
- Leave 5-10 minutes for Q&A

### 45-Minute Keynote or Invited Talk

**Purpose**: Comprehensive overview of a research program or major project with broader context.

**Structure** (35-45 slides):
1. **Opening** (3-5 minutes): Hook, personal connection, outline (4-5 slides)
2. **Big Picture** (5-7 minutes): Field overview and importance (5-7 slides)
3. **Prior Work** (3-5 minutes): Literature review and gaps (4-5 slides)
4. **Your Research Program** (25-30 minutes):
   - Study 1: Question, methods, results (8-10 slides)
   - Transition: What we learned and what remained unknown
   - Study 2: Question, methods, results (8-10 slides)
   - (Optional) Study 3: Extensions or applications (5-7 slides)
5. **Synthesis** (5-7 minutes): What it all means (5-7 slides)
   - Integrated findings
   - Theoretical implications
   - Practical applications
   - Limitations
6. **Future Directions** (2-3 minutes): Where the field is going (2-3 slides)
7. **Conclusions** (2 minutes): Key messages (2 slides)
8. **Acknowledgments** (1 minute)

**Tips**:
- Tell a story arc across multiple studies
- Show evolution of thinking
- Include more personal elements and humor
- Can discuss failed experiments or pivots
- More philosophical and forward-looking
- Engage audience with rhetorical questions
- Leave 10-15 minutes for discussion

### 60-Minute Lecture or Tutorial

**Purpose**: Educational presentation teaching a concept, method, or field overview.

**Structure** (45-60 slides):
1. **Introduction** (5 minutes): Topic importance, learning objectives (5-6 slides)
2. **Foundations** (10-12 minutes): Essential background (10-12 slides)
3. **Core Content - Part 1** (15-18 minutes): First major topic (15-20 slides)
4. **Core Content - Part 2** (15-18 minutes): Second major topic (15-20 slides)
5. **Applications** (5-7 minutes): Real-world examples (5-7 slides)
6. **Summary** (3-5 minutes): Key takeaways, resources (3-4 slides)
7. **Questions/Discussion** (Remaining time)

**Tips**:
- Include checkpoints: "Are there questions so far?"
- Use examples and analogies liberally
- Build complexity gradually
- Include interactive elements if possible
- Provide resources for further learning
- Repeat key concepts at transitions
- Use consistent visual templates for concept types

## Opening Strategies

### The Hook (First 30-60 seconds)

Your opening sets the tone and captures attention. Effective hooks:

**1. Surprising Statistic**
- "Every year, X million people experience Y, yet only Z% receive effective treatment."
- Works well for applied research with societal impact

**2. Provocative Question**
- "What if I told you that everything we thought about X is wrong?"
- Engages audience immediately, creates curiosity

**3. Personal Story**
- "Five years ago, I encountered a patient/problem that changed how I think about..."
- Humanizes research, creates emotional connection

**4. Visual Puzzle**
- Start with an intriguing image or data visualization
- "Look at this pattern. What could explain it?"

**5. Contrasting Paradigms**
- "The traditional view says X, but new evidence suggests Y."
- Sets up tension and your contribution

**6. Scope and Scale**
- "This problem affects X people, costs Y dollars, and has been unsolved for Z years."
- Establishes immediate importance

### Title Slide Essentials

Your title slide should include:
- **Clear, specific title** (not generic)
- **Your name and credentials**
- **Affiliation(s) with logos**
- **Date and venue** (conference name)
- **Optional**: QR code to paper, slides, or resources
- **Optional**: Compelling background image related to research

**Title Crafting**:
- Be specific: "Machine Learning Predicts Alzheimer's Risk from Retinal Images" 
- Not vague: "Applications of AI in Healthcare"
- Include key method and outcome
- Maximum 15 words
- Avoid jargon if presenting to broader audience

### Outline Slides

For talks >20 minutes, include a brief outline slide:
- Shows 3-5 main sections
- Provides roadmap for audience
- Can return to outline as section dividers
- Keep simple and visual (not just bullet list)

Example outline approach:
```
[Icon] Background → [Icon] Methods → [Icon] Results → [Icon] Implications
```

## Closing Strategies

### Effective Conclusions

The last 1-2 minutes are most remembered. Strong conclusions:

**1. Key Takeaways Format**
- 3-5 bullet points summarizing main messages
- Each should be a complete, memorable sentence
- Not just "Results": make claims

**2. Call-Back Hook**
- Reference your opening hook or question
- "Remember that surprising statistic? Our findings suggest..."
- Creates narrative closure

**3. Practical Implications**
- "What does this mean for clinicians/researchers/policy?"
- Action-oriented takeaways
- Bridges science to application

**4. Visual Summary**
- Single powerful figure integrating all findings
- Conceptual model showing relationships
- Before/after comparison

**5. Future Outlook**
- "These findings open doors to..."
- 1-2 specific next steps
- Inspiration for audience's own work

### Acknowledgments Slide

Essential elements:
- **Funding sources** (with grant numbers)
- **Key collaborators** (with photos if space)
- **Institution/lab** (with logo)
- **Study participants** (appropriate mention)
- Keep brief (15-30 seconds max)
- Optional: Include contact info and QR codes here

### Final Slide

Your final slide stays visible during Q&A. Include:
- **"Thank you" or "Questions?"**
- **Your contact information** (email, Twitter/X)
- **QR code to paper, preprint, or slides**
- **Lab website or GitHub**
- **Key visual from your research** (not just text)

Avoid ending with "References" or dense acknowledgments—these don't facilitate discussion.

## Transition Techniques

Smooth transitions maintain narrative flow and audience orientation.

### Between Major Sections

**Explicit Transition Slides**:
- Use consistent visual style (color, icon, position)
- Single word or short phrase: "Methods" "Results" "Implications"
- Optional: Return to outline with current section highlighted

**Verbal Transitions**:
- "Now that we've established X, let's examine how we studied Y..."
- "With that background, I'll turn to our key findings..."
- "This raises the question: How did we measure this?"

### Between Related Slides

**Visual Continuity**:
- Repeat key element (figure, title format) across slides
- Use consistent color coding
- Progressive builds of same figure

**Verbal Bridges**:
- "Building on this finding..."
- "To test this further..."
- "This pattern was consistent across..."

### Signposting Language

Help audience track progress through talk:
- "First, I'll show... Second... Finally..."
- "There are three key findings to discuss..."
- "Now, let's turn to the most surprising result..."
- "Coming back to our original question..."

## Pacing and Timing

### Time Budgeting

**Plan timing for each slide**:
- Simple title/transition slides: 15-30 seconds
- Text content slides: 45-90 seconds
- Complex figures: 2-3 minutes
- Key results: 2-4 minutes each

**Common Timing Mistakes**:
- ❌ Spending too long on introduction (>15% of talk)
- ❌ Rushing through results (should be 40-50%)
- ❌ Not leaving time for questions
- ❌ Going over time (extremely unprofessional)

### Practice Strategies

**Full Run-Throughs** (Do 3-5 times):
1. **First run**: Rough timing, identify problem areas
2. **Second run**: Practice transitions, smooth language
3. **Third run**: Final timing with backup plans
4. **Recording**: Video yourself, watch for tics/filler words
5. **Audience practice**: Present to colleagues for feedback

**Section Practice**:
- Practice complex result slides multiple times
- Rehearse opening and closing until flawless
- Prepare ad-libs for common questions

**Timing Techniques**:
- Note target time at bottom of key slides
- Set phone/watch to vibrate at checkpoints
- Have Plan B: know which slides to skip if running over
- Practice with live timer visible

### Managing Time During Talk

**If Running Ahead** (rarely a problem):
- Expand on key points naturally
- Take questions mid-talk if appropriate
- Provide more context or examples
- Slow down slightly (but don't add filler)

**If Running Behind**:
- Skip backup slides or extra examples (prepare these in advance)
- Summarize rather than detail on secondary points
- Never rush through conclusions—skip earlier content instead
- NEVER say "I'll go quickly through these" (just skip them)

**Time Checkpoints**:
- 25% through talk = 25% through time
- 50% through talk = 50% through time
- After results = should have 5-10 minutes left
- Start conclusions with 2-3 minutes remaining

## Audience Engagement

### Reading the Room

**Visual Cues**:
- **Engaged**: Leaning forward, nodding, taking notes
- **Lost**: Confused expressions, checking phones
- **Bored**: Leaning back, glazed eyes, fidgeting

**Adjustments**:
- If losing audience: Speed up, add humor, show compelling visual
- If audience confused: Slow down, ask "Does this make sense?", re-explain
- If highly engaged: Can add more detail, encourage questions

### Interactive Elements

For seminars and longer talks:

**Rhetorical Questions**:
- "Why do you think this pattern occurred?"
- "What would you predict happens next?"
- Pauses for thought (don't immediately answer)

**Quick Polls** (if appropriate):
- "Raise your hand if you've encountered X..."
- "How many think the result will be A vs. B?"
- Brief, not disruptive

**Checkpoint Questions**:
- "Before I continue, are there questions about the methods?"
- "Is everyone comfortable with this concept?"
- For longer talks or tutorials

### Body Language and Delivery

**Effective Practices**:
- ✅ Stand to side of screen, facing audience
- ✅ Use pointer deliberately for specific elements
- ✅ Make eye contact with different sections of room
- ✅ Gesture naturally to emphasize points
- ✅ Vary voice pitch and pace
- ✅ Pause after important points

**Avoid**:
- ❌ Reading slides verbatim
- ❌ Turning back to audience
- ❌ Standing in front of projection
- ❌ Fidgeting with pointer/objects
- ❌ Pacing repetitively
- ❌ Monotone delivery

## Special Considerations

### Virtual Presentations

**Technical Setup**:
- Test screen sharing, audio, and video beforehand
- Use presenter mode if available (see notes)
- Ensure good lighting and camera angle
- Minimize background distractions

**Engagement Challenges**:
- Can't read audience body language as well
- More explicit engagement needed
- Use polls, chat, reactions if platform allows
- Encourage unmuting for questions

**Pacing**:
- Slightly slower pace (harder to interrupt virtually)
- More explicit transitions and signposting
- Build in planned pauses for questions
- Monitor chat for questions during talk

### Handling Questions

**During Talk**:
- For short talks: "Please hold questions until the end"
- For seminars: "Feel free to interrupt with questions"
- If interrupted: "Great question, let me finish this point and come back to it"

**Q&A Session**:
- **Listen fully** before answering
- **Repeat or rephrase** question for whole audience
- **Answer concisely** (30-90 seconds max)
- **Be honest** if you don't know: "That's a great question I don't have data on yet"
- **Redirect if off-topic**: "That's interesting but beyond scope. Happy to discuss after."
- **Have backup slides** with extra data/analyses ready

**Difficult Questions**:
- **Hostile**: Stay calm, acknowledge concern, stick to data
- **Confusing**: Ask for clarification: "Could you rephrase that?"
- **Out of scope**: "I focused on X, but your question about Y is important for future work"

### Technical Difficulties

**Preparation**:
- Have backup: PDF on laptop, cloud, and USB drive
- Test connections and adapters beforehand
- Know how to reset display if needed
- Have printout of slides as absolute backup

**During Talk**:
- Stay calm and professional
- Fill time with verbal explanation while fixing
- Skip problem slide if necessary
- Apologize briefly but don't dwell on it

## Adapting to Different Venues

### Conference Presentation

**Context**:
- Concurrent sessions, some audience may arrive late
- Audience has seen many talks that day
- Strict time limits
- May be recorded

**Adaptations**:
- Strong hook to capture attention
- Clear, focused message (not trying to show everything)
- Adhere exactly to time limits
- Compelling visuals (tired audiences need visual interest)
- Provide URL or QR code for more information

### Department Seminar

**Context**:
- Familiar audience with domain knowledge
- More relaxed atmosphere
- Can go deeper into methods
- Questions encouraged throughout

**Adaptations**:
- Can use more technical language
- Show more methodological details
- Discuss failed experiments or challenges
- Engage in back-and-forth discussion
- Less formal style acceptable

### Thesis Defense

**Context**:
- Committee has read dissertation
- Evaluating your mastery of field
- Formal assessment situation
- Extended Q&A expected

**Adaptations**:
- Comprehensive coverage required
- Show depth of knowledge
- Address limitations proactively
- Demonstrate independent thinking
- More formal, professional tone
- Prepare extensively for questions

### Grant Pitch or Industry Talk

**Context**:
- Audience evaluating feasibility and impact
- Emphasis on applications and outcomes
- May include non-scientists
- Shorter attention for technical details

**Adaptations**:
- Lead with impact and significance
- Minimal methods details (what, not how)
- Show preliminary data and proof of concept
- Emphasize feasibility and timeline
- Clear, simple language
- Strong business case or societal benefit

## Summary Checklist

Before finalizing your presentation structure:

**Overall Structure**:
- [ ] Clear narrative arc (hook → context → problem → solution → results → impact)
- [ ] Appropriate slide count for time available (~1 slide/minute)
- [ ] 40-50% of time allocated to results
- [ ] Strong opening and closing
- [ ] Smooth transitions between sections

**Timing**:
- [ ] Practiced full talk at least 3 times
- [ ] Timing noted for key sections
- [ ] Plan B for running over (slides to skip)
- [ ] Buffer time for questions (if applicable)

**Engagement**:
- [ ] Opening hook captures attention
- [ ] Clear signposting throughout
- [ ] Conclusion provides memorable takeaways
- [ ] Final slide facilitates discussion

**Technical**:
- [ ] Slides numbered (for question reference)
- [ ] Backup slides prepared for anticipated questions
- [ ] Contact info and QR codes on final slide
- [ ] Multiple copies of presentation saved

**Practice**:
- [ ] Comfortable with content (minimal note reliance)
- [ ] Transitions smooth and natural
- [ ] Prepared for likely questions
- [ ] Tested with live audience if possible

### `references/presentation_workflow.md`

# Presentation Development Workflow

The six stages from planning through final preparation, with the checks that belong at
each stage.

## Workflow for Presentation Development

### Stage 1: Planning (Before Creating Slides)

**Define Context**:
1. What type of talk? (Conference, seminar, defense, etc.)
2. How long? (Duration in minutes)
3. Who is the audience? (Specialists, general, mixed)
4. What's the venue? (Room size, A/V setup, virtual/in-person)
5. What happens after? (Q&A, discussion, networking)

**Research and Literature Review** (Use research-lookup skill):
1. **Search for background literature**: Find 5-10 key papers establishing context
2. **Identify knowledge gaps**: Use research-lookup to find what's unknown
3. **Locate comparison studies**: Find papers with similar methods or results
4. **Gather supporting citations**: Collect papers supporting your interpretations
5. **Build reference list**: Create .bib file or citation list for slides
6. **Note key findings to cite**: Document specific results to reference

**Develop Content Outline**:
1. Identify 1-3 core messages
2. Select key findings to present
3. Choose essential figures (typically 3-6 for 15-min talk)
4. Plan narrative arc with proper citations
5. Allocate time by section

**Example Outline for 15-Minute Talk**:
```
1. Title (30 sec)
2. Hook: Compelling problem (60 sec) [Cite 1-2 papers via research-lookup]
3. Background (90 sec) [Cite 3-4 key papers establishing context]
4. Research question (45 sec) [Cite papers showing gap]
5. Methods overview (2 min)
6-8. Main result 1 (3 min, 3 slides)
9-10. Main result 2 (2 min, 2 slides)
11-12. Result 3 or validation (2 min, 2 slides)
13-14. Discussion and implications (2 min) [Compare to 2-3 prior studies]
15. Conclusions (45 sec)
16. Acknowledgments (15 sec)

NOTE: Use research-lookup to find papers for background (slides 2-4) 
and discussion (slides 13-14) BEFORE creating slides.
```

### Stage 2: Design and Creation

**Choose Implementation Method**:

**Option A: PowerPoint (via PPTX skill)**
1. Read `assets/powerpoint_design_guide.md`
2. Read `skills/pptx/SKILL.md`
3. Choose approach (programmatic or template-based)
4. Create master slides with consistent design
5. Build presentation following outline

**Option B: LaTeX Beamer**
1. Read `references/beamer_guide.md`
2. Select appropriate template from `assets/`
3. Customize theme and colors
4. Write content in LaTeX
5. Compile to PDF

**Design Considerations** (Make It Visually Appealing):
- **Select MODERN color palette**: Match your topic (biotech=vibrant, physics=sleek, health=warm)
  - Use pptx skill's color palette examples (Teal & Coral, Bold Red, Deep Purple & Emerald, etc.)
  - NOT just default blue/gray themes
  - 3-5 colors with high contrast
- **Choose clean fonts**: Sans-serif, large sizes (24pt+ body)
- **Plan visual elements**: What images, diagrams, icons for each slide?
- **Create varied layouts**: Mix full-figure, two-column, text-overlay (not all bullets)
- **Design section dividers**: Visual breaks with striking graphics
- **Plan animations/builds**: Control information flow for complex slides
- **Add visual interest**: Background images, color blocks, shapes, icons

### Stage 3: Content Development

**Populate Slides** (Visual-First Strategy):
1. **Start with visuals**: Plan which figures, images, diagrams for each key point
2. **Use research-lookup extensively**: Find 8-15 papers for proper citations
3. **Create visual backbone first**: Add all figures, charts, images, diagrams
4. **Add minimal text as support**: Bullet points complement visuals, don't replace them
5. **Design section dividers**: Visual breaks with images or graphics (not just text)
6. **Polish title/closing**: Make visually striking, include contact info
7. **Add transitions/builds**: Control information flow

**VISUAL CONTENT REQUIREMENTS** (Make Slides Engaging):
- **Images**: Use high-quality photos, illustrations, conceptual graphics
- **Icons**: Visual representations of concepts (not decoration)
- **Diagrams**: Flowcharts, schematics, process diagrams
- **Figures**: Simplified research figures with LARGE labels (18-24pt)
- **Charts**: Clean data visualizations with clear messages
- **Graphics**: Visual metaphors, conceptual illustrations
- **Color blocks**: Use colored shapes to organize content visually
- Target: MINIMUM 1-2 strong visual elements per slide

**Scientific Content** (Research-Backed):
- **Citations**: Use research-lookup EXTENSIVELY to find relevant papers
  - Introduction: Cite 3-5 papers establishing context and gap
  - Background: Show key prior work visually (not just cite)
  - Discussion: Cite 3-5 papers for comparison with your results
  - Use author-year format (Smith et al., 2023) for readability
  - Citations establish credibility and scientific rigor
- **Figures**: Simplified from papers, LARGE labels (18-24pt minimum)
- **Equations**: Large, clear, explain each term (use sparingly)
- **Tables**: Minimal, highlight key comparisons (not data dumps)
- **Code/Algorithms**: Use syntax highlighting, keep brief

**Text Guidelines** (Less is More):
- Bullet points, NEVER paragraphs
- 3-4 bullets per slide (max 6 only if essential)
- 4-6 words per bullet (shorter than 6×6 rule)
- Key terms in bold
- Text is SUPPORTING ROLE, visuals are stars
- Use builds to control pacing

### Stage 4: Visual Validation

**Generate Images**:
```bash
# Convert PDF to images
python scripts/pdf_to_images.py presentation.pdf review/slides

# Or create thumbnail grid
python skills/pptx/scripts/thumbnail.py presentation.pptx review/grid
```

**Systematic Review**:
1. View each slide image
2. Check against issue checklist
3. Document problems with slide numbers
4. Test readability from distance (view at 50% size)

**Common Issues to Fix**:
- Text extending beyond boundaries
- Figures overlapping with text
- Font sizes too small
- Poor contrast
- Misalignment

**Iteration**:
1. Fix identified issues in source
2. Regenerate PDF/presentation
3. Convert to images again
4. Re-inspect
5. Repeat until clean

### Stage 5: Practice and Refinement

**Practice Schedule**:
- Run 1: Rough draft (will run long)
- Run 2: Smooth transitions
- Run 3: Exact timing
- Run 4: Final polish
- Run 5+: Maintenance (day before, morning of)

**What to Practice**:
- Full talk with timer
- Difficult explanations
- Transitions between sections
- Opening and closing (until flawless)
- Anticipated questions

**Refinement Based on Practice**:
- Cut slides if running over
- Expand explanations if unclear
- Adjust wording for clarity
- Mark timing checkpoints
- Prepare backup slides

### Stage 6: Final Preparation

**Technical Checks**:
- [ ] Multiple copies saved (laptop, cloud, USB)
- [ ] Works on presentation computer
- [ ] Adapters/cables available
- [ ] Backup PDF version
- [ ] Tested with projector (if possible)

**Content Final**:
- [ ] No typos or errors
- [ ] All figures high quality
- [ ] Slide numbers correct
- [ ] Contact info on final slide
- [ ] Backup slides ready

**Delivery Prep**:
- [ ] Notes prepared (if using)
- [ ] Timer/phone ready
- [ ] Water available
- [ ] Business cards/handouts
- [ ] Comfortable with material (3+ practices)

### `references/prompt_writing.md`

# Prompt Writing for Slide Generation

How to phrase prompts for the two workflows: complete slides rendered as images (PDF
workflow) and standalone visuals for embedding (PPT workflow).

## Prompt Writing for Slide Generation

### Full Slide Prompts (PDF Workflow)

For complete slides, include:
1. **Slide type**: Title slide, content slide, diagram slide, etc.
2. **Title**: The slide title text
3. **Content**: Key points, bullet items, or descriptions
4. **Visual elements**: What imagery, icons, or graphics to include
5. **Design style**: Color scheme, mood, aesthetic

**Example prompts:**

```
Title slide:
"Title slide for a medical research presentation. Title: 'Advances in Cancer Immunotherapy'. Subtitle: 'Clinical Trial Results 2024'. Professional medical theme with subtle DNA helix in background. Navy blue and white color scheme."

Content slide:
"Presentation slide titled 'Key Findings'. Three bullet points: 1) 40% improvement in response rate, 2) Reduced side effects, 3) Extended survival outcomes. Include relevant medical icons. Clean, professional design with green and white colors."

Diagram slide:
"Presentation slide showing the research methodology. Title: 'Study Design'. Flowchart showing: Patient Screening → Randomization → Treatment Groups (A, B, Control) → Follow-up → Analysis. CONSORT-style flow diagram. Professional academic style."
```

### Visual-Only Prompts (PPT Workflow)

For images to embed in PowerPoint, focus on the visual element only:

```
"Flowchart showing machine learning pipeline: Data Collection → Preprocessing → Model Training → Validation → Deployment. Clean technical style, blue and gray colors."

"Conceptual illustration of cloud computing with servers, data flow, and connected devices. Modern flat design, suitable for business presentation."

"Scientific diagram of cell division process showing mitosis phases. Educational style with labels, colorblind-friendly colors."
```

---

### `references/script_reference.md`

# Bundled Script Reference

Arguments, options, and usage for `generate_slide_image.py`, `slides_to_pdf.py`,
`validate_presentation.py`, and `pdf_to_images.py`, plus the pptx-skill scripts and
external tools this skill relies on.

## Nano Banana Pro Script Reference

### generate_slide_image.py

Generate presentation slides or visuals using Nano Banana Pro AI.

```bash
# Full slide (default) - generates complete slide as image
python scripts/generate_slide_image.py "slide description" -o output.png

# Visual only - generates just the image/figure for embedding in PPT
python scripts/generate_slide_image.py "visual description" -o output.png --visual-only

# With reference images attached (Nano Banana Pro will see these)
python scripts/generate_slide_image.py "Create a slide explaining this chart" -o slide.png --attach chart.png
python scripts/generate_slide_image.py "Combine these into a comparison slide" -o compare.png --attach before.png --attach after.png
```

**Options:**
- `-o, --output`: Output file path (required)
- `--attach IMAGE`: Attach image file(s) as context for generation (can use multiple times)
- `--visual-only`: Generate just the visual/figure, not a complete slide
- `--iterations`: Max refinement iterations (default: 2)
- `--api-key`: OpenRouter API key (or set OPENROUTER_API_KEY env var)
- `-v, --verbose`: Verbose output

**Attaching Reference Images:**

Use `--attach` when you want Nano Banana Pro to see existing images as context:
- "Create a slide about this data" + attach the data chart
- "Make a title slide with this logo" + attach the logo
- "Combine these figures into one slide" + attach multiple images
- "Explain this diagram in a slide" + attach the diagram

**Environment Setup:**
```bash
export OPENROUTER_API_KEY='your_api_key_here'
# Get key at: https://openrouter.ai/keys
```

### slides_to_pdf.py

Combine multiple slide images into a single PDF.

```bash
# Combine PNG files
python scripts/slides_to_pdf.py slides/*.png -o presentation.pdf

# Combine specific files in order
python scripts/slides_to_pdf.py title.png intro.png methods.png -o talk.pdf

# From directory (sorted by filename)
python scripts/slides_to_pdf.py slides/ -o presentation.pdf
```

**Options:**
- `-o, --output`: Output PDF path (required)
- `--dpi`: PDF resolution (default: 150)
- `-v, --verbose`: Verbose output

**Tip:** Name slides with numbers for correct ordering: `01_title.png`, `02_intro.png`, etc.

---

## Tools and Scripts

### Nano Banana Pro Scripts

**generate_slide_image.py** - Generate slides or visuals with AI:
```bash
# Full slide (for PDF workflow)
python scripts/generate_slide_image.py "Title: Introduction\nContent: Key points" -o slide.png

# Visual only (for PPT workflow)
python scripts/generate_slide_image.py "Diagram description" -o figure.png --visual-only

# Options:
# -o, --output       Output file path (required)
# --visual-only      Generate just the visual, not complete slide
# --iterations N     Max refinement iterations (default: 2)
# -v, --verbose      Verbose output
```

**slides_to_pdf.py** - Combine slide images into PDF:
```bash
# From glob pattern
python scripts/slides_to_pdf.py slides/*.png -o presentation.pdf

# From directory (sorted by filename)
python scripts/slides_to_pdf.py slides/ -o presentation.pdf

# Options:
# -o, --output    Output PDF path (required)
# --dpi N         PDF resolution (default: 150)
# -v, --verbose   Verbose output
```

### Validation Scripts

**validate_presentation.py**:
```bash
python scripts/validate_presentation.py presentation.pdf --duration 15

# Checks:
# - Slide count vs. recommended range
# - File size warnings
# - Slide dimensions
# - Font sizes (PowerPoint)
# - Compilation (Beamer)
```

**pdf_to_images.py**:
```bash
python scripts/pdf_to_images.py presentation.pdf output/slide --dpi 150

# Converts PDF to images for visual inspection
# Supports: JPG, PNG
# Adjustable DPI
# Page range selection
```

### PPTX Skill Scripts

From `skills/pptx/scripts/`:
- `thumbnail.py`: Create thumbnail grids
- `rearrange.py`: Duplicate and reorder slides
- `inventory.py`: Extract text content
- `replace.py`: Update text programmatically

### External Tools

**Recommended**:
- PDF viewer: For reviewing presentations
- Color contrast checker: WebAIM Contrast Checker
- Color blindness simulator: Coblis
- Timer app: For practice sessions
- Screen recorder: For self-review

### `references/slide_capabilities.md`

# Slide Capabilities

Presentation structure, design principles, data visualization for slides, talk-specific
guidance, implementation options, visual review and iteration, timing and pacing, and
validation and quality assurance.

## Core Capabilities

### 1. Presentation Structure and Organization

Build presentations with clear narrative flow and appropriate structure for different contexts. For detailed guidance, refer to `references/presentation_structure.md`.

**Universal Story Arc**:
1. **Hook**: Grab attention (30-60 seconds)
2. **Context**: Establish importance (5-10% of talk)
3. **Problem/Gap**: Identify what's unknown (5-10% of talk)
4. **Approach**: Explain your solution (15-25% of talk)
5. **Results**: Present key findings (40-50% of talk)
6. **Implications**: Discuss meaning (15-20% of talk)
7. **Closure**: Memorable conclusion (1-2 minutes)

**Talk-Specific Structures**:
- **Conference talks (15 min)**: Focused on 1-2 key findings, minimal methods
- **Academic seminars (45 min)**: Comprehensive coverage, detailed methods, multiple studies
- **Thesis defenses (60 min)**: Complete dissertation overview, all studies covered
- **Grant pitches (15 min)**: Emphasis on significance, feasibility, and impact
- **Journal clubs (30 min)**: Critical analysis of published work

### 2. Slide Design Principles

Create professional, readable, and accessible slides that enhance understanding. For complete design guidelines, refer to `references/slide_design_principles.md`.

**ANTI-PATTERN: Avoid Dry, Text-Heavy Presentations**

❌ **What Makes Presentations Dry and Forgettable:**
- Walls of text (more than 6 bullets per slide)
- Small fonts (<24pt body text)
- Black text on white background only (no visual interest)
- No images or graphics (bullet points only)
- Generic templates with no customization
- Dense, paragraph-like bullet points
- Missing research context (no citations)
- All slides look the same (repetitive)

✅ **What Makes Presentations Engaging and Memorable:**
- HIGH-QUALITY VISUALS dominate (figures, photos, diagrams, icons)
- Large, clear text as accent (not the main content)
- Modern, purposeful color schemes (not default themes)
- Generous white space (slides breathe)
- Research-backed context (proper citations from research-lookup)
- Variety in slide layouts (not all bullet lists)
- Story-driven flow with visual anchors
- Professional, polished appearance

**Core Design Principles**:

**Visual-First Approach** (CRITICAL):
- Start with visuals (figures, images, diagrams), add text as support
- Every slide should have STRONG visual element (figure, chart, photo, diagram)
- Text explains or complements visuals, not replaces them
- Think: "How can I show this, not just tell it?"
- Target: 60-70% visual content, 30-40% text

**Simplicity with Impact**:
- One main idea per slide
- MINIMAL text (3-4 bullets, 4-6 words each preferred)
- Generous white space (40-50% of slide)
- Clear visual focus
- Bold, confident design choices

**Typography for Engagement**:
- Sans-serif fonts (Arial, Calibri, Helvetica)
- LARGE fonts: 24-28pt for body text (not minimum 18pt)
- 36-44pt for slide titles (make bold)
- High contrast (minimum 4.5:1, prefer 7:1)
- Use size for hierarchy, not just weight

**Color for Impact**:
- MODERN color palettes (not default blue/gray)
- Consider your topic: biotech? vibrant colors. Physics? sleek darks. Health? warm tones.
- Limited palette (3-5 colors total)
- High contrast combinations
- Color-blind safe (avoid red-green combinations)
- Use color purposefully (not decoration)

**Layout for Visual Interest**:
- Vary layouts (not all bullet lists)
- Use two-column layouts (text + figure)
- Full-slide figures for key results
- Asymmetric compositions (more interesting than centered)
- Rule of thirds for focal points
- Consistent but not repetitive

### 3. Data Visualization for Slides

Adapt scientific figures for presentation context. For detailed guidance, refer to `references/data_visualization_slides.md`.

**Key Differences from Journal Figures**:
- Simplify, don't replicate
- Larger fonts (18-24pt minimum)
- Fewer panels (split across slides)
- Direct labeling (not legends)
- Emphasis through color and size
- Progressive disclosure for complex data

**Visualization Best Practices**:
- **Bar charts**: Comparing discrete categories
- **Line graphs**: Trends and trajectories
- **Scatter plots**: Relationships and correlations
- **Heatmaps**: Matrix data and patterns
- **Network diagrams**: Relationships and connections

**Common Mistakes to Avoid**:
- Tiny fonts (<18pt)
- Too many panels on one slide
- Complex legends
- Insufficient contrast
- Cluttered layouts

### 4. Talk-Specific Guidance

Different presentation contexts require different approaches. For comprehensive guidance on each type, refer to `references/talk_types_guide.md`.

**Conference Talks** (10-20 minutes):
- Structure: Brief intro → minimal methods → key results → quick conclusion
- Focus: 1-2 main findings only
- Style: Engaging, fast-paced, memorable
- Goal: Generate interest, network, get invited

**Academic Seminars** (45-60 minutes):
- Structure: Comprehensive coverage with detailed methods
- Focus: Multiple findings, depth of analysis
- Style: Scholarly, interactive, discussion-oriented
- Goal: Demonstrate expertise, get feedback, collaborate

**Thesis Defenses** (45-60 minutes):
- Structure: Complete dissertation overview, all studies
- Focus: Demonstrating mastery and independent thinking
- Style: Formal, comprehensive, prepared for interrogation
- Goal: Pass examination, defend research decisions

**Grant Pitches** (10-20 minutes):
- Structure: Problem → significance → approach → feasibility → impact
- Focus: Innovation, preliminary data, team qualifications
- Style: Persuasive, focused on outcomes and impact
- Goal: Secure funding, demonstrate viability

**Journal Clubs** (20-45 minutes):
- Structure: Context → methods → results → critical analysis
- Focus: Understanding and critiquing published work
- Style: Educational, critical, discussion-facilitating
- Goal: Learn, critique, discuss implications

### 5. Implementation Options

#### Nano Banana Pro PDF (Default - Recommended)

**Best for**: Visually stunning slides, fast creation, non-technical audiences

**This is the default and recommended approach.** Generate each slide as a complete image using AI.

**Workflow**:
1. Plan each slide (title, content, visual elements)
2. Generate each slide with `generate_slide_image.py`
3. Combine into PDF with `slides_to_pdf.py`

```bash
# Generate slides
python scripts/generate_slide_image.py "Title: Introduction..." -o slides/01.png
python scripts/generate_slide_image.py "Title: Methods..." -o slides/02.png

# Combine to PDF
python scripts/slides_to_pdf.py slides/*.png -o presentation.pdf
```

**Advantages**:
- Most visually impressive results
- Fast creation (describe and generate)
- No design skills required
- Consistent, professional appearance
- Perfect for general audiences

**Best for**:
- Conference talks
- Business presentations
- General scientific talks
- Pitch presentations

#### PowerPoint via PPTX Skill

**Best for**: Editable slides, custom designs, template-based workflows

**Reference**: See `skills/pptx/SKILL.md` for complete documentation

Use Nano Banana Pro with `--visual-only` to generate images, then build PPTX with text.

**Key Resources**:
- `assets/powerpoint_design_guide.md`: Complete PowerPoint design guide
- PPTX skill's `html2pptx.md`: Programmatic creation workflow
- PPTX skill's scripts: `rearrange.py`, `inventory.py`, `replace.py`, `thumbnail.py`

**Workflow**:
1. Generate visuals with `generate_slide_image.py --visual-only`
2. Design HTML slides (for programmatic) or use templates
3. Create presentation using html2pptx or template editing
4. Add generated images and text content
5. Generate thumbnails for visual validation
6. Iterate based on visual inspection

**Advantages**:
- Editable slides (can modify text later)
- Complex animations and transitions
- Interactive elements
- Company template compatibility

#### LaTeX Beamer

**Best for**: Mathematical content, consistent formatting, version control

**Reference**: See `references/beamer_guide.md` for complete documentation

**Templates Available**:
- `assets/beamer_template_conference.tex`: 15-minute conference talk
- `assets/beamer_template_seminar.tex`: 45-minute academic seminar
- `assets/beamer_template_defense.tex`: Dissertation defense

**Workflow**:
1. Choose appropriate template
2. Customize theme and colors
3. Add content (LaTeX native: equations, code, algorithms)
4. Compile to PDF
5. Convert to images for visual validation

**Advantages**:
- Beautiful mathematics and equations
- Consistent, professional appearance
- Version control friendly (plain text)
- Excellent for algorithms and code
- Reproducible and programmatic

### 6. Visual Review and Iteration

Implement iterative improvement through visual inspection. For complete workflow, refer to `references/visual_review_workflow.md`.

**Visual Validation Workflow**:

**Step 1: Generate PDF** (if not already PDF)
- PowerPoint: Export as PDF
- Beamer: Compile LaTeX source

**Step 2: Convert to Images**
```bash
# Using the pdf_to_images script
python scripts/pdf_to_images.py presentation.pdf review/slide --dpi 150

# Or use pptx skill's thumbnail tool
python skills/pptx/scripts/thumbnail.py presentation.pptx review/thumb
```

**Step 3: Systematic Inspection**

Check each slide for:
- **Text overflow**: Text cut off at edges
- **Element overlap**: Text overlapping images or other text
- **Font sizes**: Text too small (<18pt)
- **Contrast**: Insufficient contrast between text and background
- **Layout issues**: Misalignment, poor spacing
- **Visual quality**: Pixelated images, poor rendering

**Step 4: Document Issues**

Create issue log:
```
Slide # | Issue Type | Description | Priority
--------|-----------|-------------|----------
3       | Text overflow | Bullet 4 extends beyond box | High
7       | Overlap | Figure overlaps with caption | High
12      | Font size | Axis labels too small | Medium
```

**Step 5: Apply Fixes**

Make corrections to source files:
- PowerPoint: Edit text boxes, resize elements
- Beamer: Adjust LaTeX code, recompile

**Step 6: Re-Validate**

Repeat Steps 1-5 until no critical issues remain.

**Stopping Criteria**:
- No text overflow
- No inappropriate overlaps
- All text readable (≥18pt equivalent)
- Adequate contrast (≥4.5:1)
- Professional appearance

### 7. Timing and Pacing

Ensure presentations fit allocated time. For comprehensive timing guidance, refer to `assets/timing_guidelines.md`.

**The One-Slide-Per-Minute Rule**:
- General guideline: ~1 slide per minute
- Adjust for complex slides (2-3 minutes)
- Adjust for simple slides (15-30 seconds)

**Time Allocation**:
- Introduction: 15-20%
- Methods: 15-20%
- Results: 40-50% (MOST TIME)
- Discussion: 15-20%
- Conclusion: 5%

**Practice Requirements**:
- 5-minute talk: Practice 5-7 times
- 15-minute talk: Practice 3-5 times
- 45-minute talk: Practice 3-4 times
- Defense: Practice 4-6 times

**Timing Checkpoints**:

For 15-minute talk:
- 3-4 minutes: Finishing introduction
- 7-8 minutes: Halfway through results
- 12-13 minutes: Starting conclusions

**Emergency Strategies**:
- Running behind: Skip backup slides (prepare in advance)
- Running ahead: Expand examples, slow slightly
- Never skip conclusions

### 8. Validation and Quality Assurance

**Automated Validation**:
```bash
# Validate slide count, timing, file size
python scripts/validate_presentation.py presentation.pdf --duration 15

# Generates report on:
# - Slide count vs. recommended range
# - File size warnings
# - Slide dimensions
# - Font size issues (PowerPoint)
# - Compilation success (Beamer)
```

**Manual Validation Checklist**:
- [ ] Slide count appropriate for duration
- [ ] Title slide complete (name, affiliation, date)
- [ ] Clear narrative flow
- [ ] One main idea per slide
- [ ] Font sizes ≥18pt (preferably 24pt+)
- [ ] High contrast colors
- [ ] Figures large and readable
- [ ] No text overflow or element overlap
- [ ] Consistent design throughout
- [ ] Slide numbers present
- [ ] Contact info on final slide
- [ ] Backup slides prepared
- [ ] Tested on projector (if possible)

### `references/slide_design_principles.md`

# Slide Design Principles for Scientific Presentations

## Overview

Effective slide design enhances comprehension, maintains audience attention, and ensures your scientific message is communicated clearly. This guide covers visual hierarchy, typography, color theory, layout principles, and accessibility considerations for creating professional scientific presentations.

## Core Design Principles

### 1. Simplicity and Clarity

**The Fundamental Rule**: Each slide should communicate ONE main idea.

**Why It Matters**:
- Audiences can only process limited information at once
- Complexity causes cognitive overload
- Simple slides are remembered; busy slides are forgotten

**Application**:
- ✅ One message per slide
- ✅ Minimal text (audiences read OR listen, not both simultaneously)
- ✅ Clear visual focus
- ✅ Generous white space
- ❌ Avoid cramming multiple concepts onto one slide

**Example Comparison**:
```
BAD: Single slide with:
- 3 different graphs
- 8 bullet points
- 2 tables
- Dense caption text

GOOD: Three separate slides:
- Slide 1: First graph with 2-3 key points
- Slide 2: Second graph with interpretation
- Slide 3: Summary table with highlighted finding
```

### 2. Visual Hierarchy

Guide attention to the most important elements through size, color, and position.

**Hierarchy Levels**:
1. **Primary**: Main message or key data (largest, highest contrast)
2. **Secondary**: Supporting information (medium size)
3. **Tertiary**: Details and labels (smaller, lower contrast)

**Techniques**:

**Size**:
- Title: Largest (36-54pt)
- Key findings: Large (24-32pt)
- Supporting text: Medium (18-24pt)
- Labels and notes: Smallest but legible (14-18pt)

**Color**:
- High contrast for key elements
- Accent colors for emphasis
- Muted colors for background or secondary info

**Position**:
- Top-left or top-center: Primary content (Western reading pattern)
- Center: Focal point for key visuals
- Bottom or sides: Supporting details

**Weight**:
- Bold for emphasis on key terms
- Regular weight for body text
- Light weight for de-emphasized content

### 3. Consistency

Maintain visual consistency throughout the presentation.

**Elements to Keep Consistent**:
- **Fonts**: Same font family for all slides
- **Colors**: Defined color palette (3-5 colors)
- **Layouts**: Similar slides use same structure
- **Spacing**: Margins and padding uniform
- **Style**: Figure formats, bullet styles, numbering

**Benefits**:
- Professional appearance
- Reduced cognitive load (audiences learn your visual language)
- Focus on content, not adjusting to new formats
- Easy to identify information types

**Template Approach**:
- Create master slide with standard elements
- Design 3-5 layout variants (title, content, figure, section divider)
- Apply consistently throughout

## Typography

### Font Selection

**Recommended Font Types**:

**Sans-Serif Fonts** (Highly Recommended):
- **Arial**: Universal, highly legible
- **Helvetica**: Clean, professional
- **Calibri**: Modern default, works well
- **Gill Sans**: Elegant sans-serif
- **Futura**: Geometric, modern
- **Avenir**: Friendly, professional

**Serif Fonts** (Use Sparingly):
- Generally harder to read on screens
- Acceptable for titles in some contexts
- Avoid for body text in presentations

**Avoid**:
- ❌ Script or handwriting fonts (illegible from distance)
- ❌ Decorative fonts (distracting)
- ❌ Condensed fonts (hard to read)
- ❌ Multiple font families (>2 looks unprofessional)

### Font Sizes

**Minimum Readable Sizes**:
- **Title slide title**: 44-54pt
- **Section headers**: 36-44pt
- **Slide titles**: 32-40pt
- **Body text**: 24-28pt (absolute minimum 18pt)
- **Figure labels**: 18-24pt
- **Captions and citations**: 14-16pt (use sparingly)

**The Room Test**:
- Can text be read from the back of the room?
- Rule: Body text should be readable at 6× screen height distance
- When in doubt: go larger

**Size Relationships**:
```
Title: 40pt
━━━━━━━━━━━━━━━━━
Subheading: 28pt
─────────────
Body text: 24pt
Regular content for audience

Caption: 16pt
```

### Text Formatting

**Best Practices**:

**Line Length**:
- Maximum 50-60 characters per line
- Break long sentences into multiple lines
- Use phrases, not full sentences when possible

**Line Spacing**:
- 1.2-1.5× line height for readability
- More spacing for dense content
- Consistent spacing throughout

**Alignment**:
- **Left-aligned**: Best for body text (natural reading)
- **Center-aligned**: Titles, short phrases, key messages
- **Right-aligned**: Rarely used (occasionally for design balance)
- **Justified**: Avoid (creates awkward spacing)

**Emphasis**:
- ✅ **Bold** for key terms (use sparingly)
- ✅ Color for emphasis (consistent meaning)
- ✅ Size increase for importance
- ❌ Avoid italics (hard to read from distance)
- ❌ Avoid underline (confused with hyperlinks)
- ❌ AVOID ALL CAPS FOR BODY TEXT (READS AS SHOUTING)

### The 6×6 Rule

**Guideline**: Maximum 6 bullets per slide, maximum 6 words per bullet.

**Rationale**:
- More text = audience reads instead of listens
- Bullet points are prompts, not sentences
- You provide the explanation verbally

**Better Approach**:
- 3-4 bullets optimal
- 4-8 words per bullet
- Use fragments, not complete sentences
- Consider replacing text with visuals

**Example Transformation**:
```
TOO MUCH TEXT:
• Our study examined the relationship between dietary interventions 
  and cardiovascular outcomes in 1,500 participants over 5 years
• We found that participants in the intervention group showed 
  significantly reduced risk compared to controls
• The effect size was larger than previous studies and persisted 
  at long-term follow-up

BETTER:
• 5-year dietary intervention study
• 27% reduced cardiovascular risk
• Largest effect to date
```

## Color Theory

### Color Palettes for Scientific Presentations

**Purpose-Driven Color Selection**:

**Professional/Academic** (Conservative):
- Navy blue (#1C3D5A), gray (#4A5568), white (#FFFFFF)
- Accent: Orange (#E67E22) or green (#27AE60)
- Use: Faculty seminars, grant presentations, institutional talks

**Modern/Engaging** (Energetic):
- Teal (#0A9396), coral (#EE6C4D), cream (#F4F1DE)
- Accent: Burgundy (#780000)
- Use: Conference talks, public engagement, TED-style talks

**High Contrast** (Maximum Legibility):
- Black text (#000000) on white (#FFFFFF)
- Dark blue (#003366) on white
- White on dark gray (#2D3748)
- Use: Large venues, virtual presentations, accessibility priority

**Data Visualization** (Color-blind Safe):
- Blue (#0173B2), orange (#DE8F05), green (#029E73), red (#CC78BC)
- Based on Wong/IBM palettes
- Use: Figures with categorical data, bar charts, line plots

### Color Psychology in Science

**Blue**:
- Associations: Trust, stability, professionalism, intelligence
- Use: Backgrounds, institutional presentations, technology topics
- Caution: Can feel cold; balance with warmer accents

**Green**:
- Associations: Growth, health, nature, sustainability
- Use: Biology, environmental science, health outcomes
- Caution: Avoid red-green combinations (color blindness)

**Red/Orange**:
- Associations: Energy, urgency, warning, importance
- Use: Highlighting critical findings, emphasis, calls to action
- Caution: Don't overuse; loses impact

**Purple**:
- Associations: Innovation, creativity, wisdom
- Use: Neuroscience, novel methods, creative research
- Caution: Can appear less serious in some contexts

**Gray**:
- Associations: Neutrality, professionalism, sophistication
- Use: Backgrounds, de-emphasized content, grounding
- Caution: Can feel dull if overused

### Color Contrast and Accessibility

**WCAG Standards** (Web Content Accessibility Guidelines):
- **Level AA**: 4.5:1 contrast ratio for normal text
- **Level AAA**: 7:1 contrast ratio (preferred for presentations)

**High Contrast Combinations**:
- ✅ Black on white (21:1)
- ✅ Dark blue (#003366) on white (12.6:1)
- ✅ White on dark gray (#2D3748) (11.8:1)
- ✅ Dark text (#333333) on cream (#F4F1DE) (9.7:1)

**Low Contrast Combinations** (Avoid):
- ❌ Light gray on white
- ❌ Yellow on white
- ❌ Pastel colors on white backgrounds
- ❌ Red on black (difficult to read)

**Testing Contrast**:
- Use online tools (e.g., WebAIM Contrast Checker)
- Print slide in grayscale (should remain legible)
- View from distance (simulate audience perspective)

### Color Blindness Considerations

**Prevalence**: ~8% of men, ~0.5% of women have color vision deficiency

**Most Common**: Red-green color blindness (protanopia/deuteranopia)

**Safe Practices**:
- ✅ Use blue/orange instead of red/green
- ✅ Add patterns or shapes in addition to color
- ✅ Use color AND other differentiators (shape, size, position)
- ✅ Test with color blindness simulator

**Color-Blind Safe Palettes**:
```
Primary: Blue (#0173B2)
Contrast: Orange (#DE8F05)  [NOT green]
Additional: Magenta (#CC78BC), Teal (#029E73)
```

**Figure Design**:
- Don't rely solely on red vs. green lines
- Use different line styles (solid, dashed, dotted)
- Use symbols (circle, square, triangle) for scatter plots
- Label directly on plot rather than color legend only

## Layout and Composition

### The Rule of Thirds

Divide slide into 3×3 grid; place key elements at intersections or along lines.

**Application**:
```
+-------+-------+-------+
|   ┃   |   ┃   |   ┃   |
|---●---|---●---|---●---|  ← Key focal points (●)
|   ┃   |   ┃   |   ┃   |
|---●---|---●---|---●---|
|   ┃   |   ┃   |   ┃   |
|---●---|---●---|---●---|
|   ┃   |   ┃   |   ┃   |
+-------+-------+-------+
```

**Benefits**:
- More visually interesting than centered layouts
- Natural eye flow
- Professional appearance
- Guides attention strategically

**Example Usage**:
- Place key figure at right third
- Text summary on left two-thirds
- Title at top third line
- Logo at bottom-right intersection

### White Space

**Definition**: Empty space around and between elements.

**Purpose**:
- Gives content room to "breathe"
- Increases focus on important elements
- Prevents overwhelming the audience
- Projects professionalism and confidence

**Guidelines**:
- Margins: Minimum 5-10% of slide on all sides
- Element spacing: Clear separation between unrelated items
- Text padding: Space around text blocks
- Don't fill every pixel: Empty space is valuable

**Common Mistakes**:
- Cramming too much on one slide
- Extending content to edges
- No space between elements
- Fear of "wasting" space

### Layout Patterns

**Title + Content**:
```
┌─────────────────────────┐
│ Slide Title             │
├─────────────────────────┤
│                         │
│    Content Area         │
│    (text, figure,       │
│     or combination)     │
│                         │
└─────────────────────────┘
```
Use: Standard slide type, most common

**Two Column**:
```
┌─────────────────────────┐
│ Slide Title             │
├───────────┬─────────────┤
│           │             │
│  Text     │   Figure    │
│  Column   │   Column    │
│           │             │
└───────────┴─────────────┘
```
Use: Comparing items, text + figure

**Full-Slide Figure**:
```
┌─────────────────────────┐
│                         │
│                         │
│    Large Figure or      │
│    Image                │
│                         │
│                         │
└─────────────────────────┘
```
Use: Key results, impactful visuals

**Text Overlay**:
```
┌─────────────────────────┐
│   ┌─────────────┐       │
│   │ Text Box    │       │
│   └─────────────┘       │
│     Background Image    │
│                         │
└─────────────────────────┘
```
Use: Title slide, section dividers

**Grid Layout**:
```
┌─────────────────────────┐
│ Title                   │
├─────────┬───────┬───────┤
│ Item 1  │ Item 2│ Item 3│
├─────────┼───────┼───────┤
│ Item 4  │ Item 5│ Item 6│
└─────────┴───────┴───────┘
```
Use: Multiple related items, comparisons

### Alignment

**Principle**: Align elements to create visual order and relationships.

**Types**:

**Edge Alignment**:
- Align left edges of text blocks
- Align right edges of figures
- Align top edges of items in row

**Center Alignment**:
- Center title on slide
- Center key messages
- Center lone figures

**Grid Alignment**:
- Use invisible grid
- Snap elements to grid lines
- Maintains consistency across slides

**Visual Impact**:
- Aligned elements look intentional and professional
- Misaligned elements appear careless
- Small misalignments are very noticeable

## Background Design

### Background Colors

**Best Practices**:

**Light Backgrounds** (Most Common):
- White or off-white (#FFFFFF, #F8F9FA)
- Very light gray (#F5F5F5)
- Cream/beige (#FAF8F3)

**Advantages**:
- Maximum contrast for dark text
- Works in any lighting
- Professional and clean
- Easier on projectors

**Dark Backgrounds**:
- Dark gray (#2D3748)
- Navy blue (#1A202C)
- Black (#000000)

**Advantages**:
- Modern, sophisticated
- Good for dark venues
- Reduces eye strain in dark rooms
- Makes colors pop

**Disadvantages**:
- Requires light-colored text
- Can be difficult in bright rooms
- Some projectors handle poorly

**Gradient Backgrounds**:
- ✅ Subtle gradients acceptable (light to lighter)
- ❌ Avoid busy or high-contrast gradients
- ❌ Don't distract from content

**Image Backgrounds**:
- Use only for title/section slides
- Ensure sufficient contrast with text
- Add semi-transparent overlay if needed
- Avoid busy or cluttered images

### Borders and Frames

**Minimal Approach** (Recommended):
- No borders on most slides
- Let white space define boundaries
- Clean, modern appearance

**Selective Borders**:
- Around key figures for emphasis
- Separating distinct sections
- Highlighting callout boxes
- Simple, thin lines only

**Avoid**:
- Decorative borders
- Thick, colorful frames
- Clipart-style elements
- 3D effects and shadows

## Visual Elements

### Icons and Graphics

**Purpose**:
- Visual anchors for concepts
- Break up text-heavy slides
- Quick recognition of section types
- Add visual interest

**Best Practices**:
- ✅ Consistent style (all outline or all filled)
- ✅ Simple, recognizable designs
- ✅ Appropriate size (not too large or small)
- ✅ Limited color palette matching theme
- ❌ Avoid clipart or cartoonish graphics (unless appropriate)
- ❌ Don't use for decoration only (should convey meaning)

**Sources**:
- Font Awesome
- Noun Project
- Material Design Icons
- Custom scientific illustrations

### Bullets and Lists

**Bullet Styles**:
- **Simple shapes**: Circle (•), square (■), dash (−)
- **Avoid**: Complex symbols, changing bullet styles within list
- **Hierarchy**: Different bullets for different levels

**List Best Practices**:
- Maximum 4-6 items per list
- Parallel structure (all start with verb, or all nouns, etc.)
- Use fragments, not complete sentences
- Adequate spacing between items (1.5-2× line height)

**Alternative to Bullets**:
- **Numbered lists**: When order matters
- **Icons**: Visual representation of each point
- **Progressive builds**: Reveal one point at a time
- **Separate slides**: One concept per slide

### Shapes and Dividers

**Uses**:
- Background rectangles to highlight content
- Arrows showing relationships or flow
- Circles for emphasis or grouping
- Lines separating sections

**Guidelines**:
- Keep shapes simple (rectangles, circles, lines)
- Use brand colors
- Maintain consistency
- Avoid 3D effects
- Don't overuse

## Animation and Builds

### When to Use Animation

**Appropriate Uses**:
- **Progressive disclosure**: Reveal bullet points one at a time
- **Build complex figures**: Add layers incrementally
- **Show process**: Illustrate sequential steps
- **Emphasize transitions**: Highlight connections
- **Control pacing**: Prevent audience from reading ahead

**Inappropriate Uses**:
- ❌ Decoration or entertainment
- ❌ Every slide transition
- ❌ Multiple animations per slide
- ❌ Distracting effects (spin, bounce, etc.)

### Types of Animations

**Entrance**:
- **Appear**: Instant (good for fast-paced talks)
- **Fade**: Subtle, professional
- **Wipe**: Directional reveal
- Avoid: Fly in, bounce, spiral, etc.

**Exit**:
- Rarely needed
- Use to remove intermediary steps
- Keep simple (fade or disappear)

**Emphasis**:
- Color change for highlighting
- Bold/underline to draw attention
- Grow slightly for importance
- Use very sparingly

**Builds**:
- Reveal bullet points progressively
- Add elements to complex figure
- Show before/after states
- Demonstrate process steps

**Best Practices**:
- Fast transitions (0.2-0.3 seconds)
- Consistent animation type throughout
- Click to advance (not automatic timing)
- Builds should add clarity, not complexity

## Common Design Mistakes

### Content Mistakes

**Too Much Text**:
- Problem: Audience reads instead of listening
- Fix: Use key phrases, not paragraphs; move details to notes

**Too Many Concepts per Slide**:
- Problem: Cognitive overload, unclear focus
- Fix: One idea per slide; split complex slides into multiple

**Inconsistent Formatting**:
- Problem: Looks unprofessional, distracting
- Fix: Use templates, maintain style guide

**Poor Contrast**:
- Problem: Illegible from distance
- Fix: Test at actual presentation size, use high-contrast combinations

**Tiny Fonts**:
- Problem: Unreadable for audience
- Fix: Minimum 18pt, preferably 24pt+ for body text

### Visual Mistakes

**Cluttered Slides**:
- Problem: No clear focal point, overwhelming
- Fix: Embrace white space, remove non-essential elements

**Low-Quality Images**:
- Problem: Pixelated or blurry figures
- Fix: Use high-resolution images (300 DPI minimum)

**Distracting Backgrounds**:
- Problem: Competes with content
- Fix: Simple, solid colors or subtle gradients

**Overuse of Effects**:
- Problem: Looks amateurish, distracting
- Fix: Minimal or no shadows, gradients, 3D effects

**Misaligned Elements**:
- Problem: Appears careless
- Fix: Use alignment tools, grids, and guides

### Color Mistakes

**Insufficient Contrast**:
- Problem: Hard to read
- Fix: Test with contrast checker, use dark on light or light on dark

**Too Many Colors**:
- Problem: Chaotic, unprofessional
- Fix: Limit to 3-5 colors total

**Red-Green Combinations**:
- Problem: Invisible to color-blind audience members
- Fix: Use blue-orange or add patterns/shapes

**Clashing Colors**:
- Problem: Visually jarring
- Fix: Use color palette tools, test combinations

## Accessibility

### Designing for All Audiences

**Visual Impairments**:
- High contrast text (minimum 4.5:1, preferably 7:1)
- Large fonts (minimum 18pt, prefer 24pt+)
- Simple, clear fonts
- No reliance on color alone to convey meaning

**Color Blindness**:
- Avoid red-green combinations
- Use patterns, shapes, or labels in addition to color
- Test with color blindness simulator
- Provide alternative visual cues

**Cognitive Considerations**:
- Simple, uncluttered layouts
- One concept per slide
- Clear visual hierarchy
- Consistent navigation and structure

**Presentation Environment**:
- Works in various lighting conditions
- Visible from distance (back of large room)
- Readable on different screens (laptop, projector, phone)
- Printable in grayscale if needed

### Alternative Text and Descriptions

**For Figures**:
- Provide verbal description during talk
- Include detailed caption in notes
- Describe key patterns: "Notice the increasing trend..."

**For Complex Visuals**:
- Break into components
- Use progressive builds
- Provide interpretive context

## Design Workflow

### Step 1: Define Visual Identity

Before creating slides:
1. **Color palette**: Choose 3-5 colors
2. **Fonts**: Select 1-2 font families
3. **Style**: Decide on overall aesthetic (minimal, bold, traditional)
4. **Templates**: Create master slides for different types

### Step 2: Create Master Templates

Design 4-6 slide layouts:
1. **Title slide**: Name, title, affiliation
2. **Section divider**: Major transitions
3. **Content slide**: Standard text/bullets
4. **Figure slide**: Large visual focus
5. **Two-column**: Text + figure side-by-side
6. **Closing**: Questions, contact, acknowledgments

### Step 3: Apply Consistently

For each slide:
- Choose appropriate template
- Add content (text or visuals)
- Ensure alignment and spacing
- Check font sizes and contrast
- Verify consistency with other slides

### Step 4: Review and Refine

Review checklist:
- [ ] Every slide has clear focus
- [ ] Text is minimal and readable
- [ ] Visual hierarchy is clear
- [ ] Colors are consistent and accessible
- [ ] Alignment is precise
- [ ] White space is adequate
- [ ] Animations are purposeful
- [ ] Overall flow is smooth

## Tools and Resources

### Design Software

**PowerPoint**:
- Master slides for templates
- Alignment guides and gridlines
- Design Ideas feature for inspiration
- Morph transition for smooth animations

**Keynote** (Mac):
- Beautiful default templates
- Smooth animations
- Magic Move for object transitions

**Google Slides**:
- Collaborative editing
- Cloud-based access
- Simple, clean interface

**LaTeX Beamer**:
- Consistent, professional appearance
- Excellent for equations and code
- Version control friendly
- Reproducible designs

### Design Resources

**Color Tools**:
- Coolors.co: Palette generator
- Adobe Color: Color scheme creator
- WebAIM Contrast Checker: Accessibility testing
- Coblis: Color blindness simulator

**Icon Sources**:
- Font Awesome: General icons
- Noun Project: Specific concepts
- BioIcons: Science-specific graphics
- Flaticon: Large collection

**Inspiration**:
- Scientific presentation examples in your field
- TED talks for delivery style
- Conference websites for design trends
- Design portfolios (Behance, Dribbble)

## Summary Checklist

Before finalizing your slide design:

**Typography**:
- [ ] Font size ≥18pt minimum, preferably 24pt+ for body
- [ ] Maximum 6 bullets per slide, 6 words per bullet
- [ ] Sans-serif fonts used throughout
- [ ] Consistent font family (1-2 max)

**Color**:
- [ ] High contrast text-background (4.5:1 minimum)
- [ ] Limited color palette (3-5 colors)
- [ ] Color-blind safe combinations
- [ ] Consistent color use throughout

**Layout**:
- [ ] One main idea per slide
- [ ] Generous white space (don't fill every pixel)
- [ ] Elements aligned precisely
- [ ] Consistent layouts for similar content

**Visual Elements**:
- [ ] High-resolution images (300 DPI)
- [ ] Consistent icon/graphic style
- [ ] Minimal decorative elements
- [ ] Clear visual hierarchy

**Accessibility**:
- [ ] Readable from back of room
- [ ] Works in various lighting conditions
- [ ] No reliance on color alone
- [ ] Clear without audio (for recorded talks)

**Professional Polish**:
- [ ] Consistent template throughout
- [ ] No typos or formatting errors
- [ ] Smooth animations (if any)
- [ ] Clean, uncluttered appearance

### `references/talk_types_guide.md`

# Scientific Talk Types Guide

## Overview

Different presentation contexts require different approaches, structures, and emphasis. This guide provides detailed guidance for common scientific talk types: conference presentations, academic seminars, thesis defenses, grant pitches, and journal club presentations.

## Conference Talks

### Context and Expectations

**Typical Characteristics**:
- **Duration**: 10-20 minutes (15 minutes most common)
- **Audience**: Mix of specialists and non-specialists in your field
- **Setting**: Concurrent sessions, audience may arrive late
- **Goal**: Communicate key findings, generate interest, network
- **Format**: Often followed by 2-5 minutes of questions

**Challenges**:
- Limited time for comprehensive coverage
- Competing with other interesting talks
- Audience fatigue (many talks in one day)
- May be recorded or photographed
- Need to make strong impression quickly

### Structure for 15-Minute Conference Talk

**Recommended Slide Count**: 15-18 slides

**Time Allocation**:
```
Introduction (2-3 minutes, 2-3 slides):
- Title + hook (30 seconds)
- Background and significance (90 seconds)
- Research question (60 seconds)

Methods (2-3 minutes, 2-3 slides):
- Study design overview
- Key methodological approach
- Analysis strategy

Results (6-7 minutes, 6-8 slides):
- Primary finding (2-3 minutes, 2-3 slides)
- Secondary finding (2 minutes, 2 slides)
- Additional validation (2 minutes, 2-3 slides)

Discussion (2-3 minutes, 3-4 slides):
- Interpretation
- Comparison to prior work
- Implications
- Limitations

Conclusion (1 minute, 1-2 slides):
- Key takeaways
- Acknowledgments
```

### Conference Talk Best Practices

**Opening**:
- ✅ Start with attention-grabbing hook (surprising fact, compelling image)
- ✅ Clearly state why this work matters
- ✅ Preview main finding early ("spoiler alert" acceptable)
- ❌ Don't spend >2 minutes on background
- ❌ Don't start with "I'm honored to be here..."

**Content**:
- ✅ Focus on 1-2 key findings (not everything from paper)
- ✅ Use compelling visuals
- ✅ Show data, not just conclusions
- ✅ Explain implications clearly
- ❌ Don't go into excessive methodological detail
- ❌ Don't include every analysis from paper
- ❌ Don't use small fonts or busy slides

**Delivery**:
- ✅ Practice to ensure exact timing
- ✅ Make eye contact with audience
- ✅ Show enthusiasm for your work
- ✅ End with clear, memorable conclusion
- ❌ Don't run over time (extremely unprofessional)
- ❌ Don't rush through slides at end
- ❌ Don't read slides verbatim

**Q&A Strategy**:
- Prepare backup slides with extra data
- Anticipate likely questions
- Keep answers concise (30-60 seconds)
- Direct skeptics to poster or paper for details
- Have business cards or contact info ready

### Lightning Talks (5-7 Minutes)

**Ultra-Focused Structure**:
```
Slide 1: Title (15 seconds)
Slide 2: The Problem (45 seconds)
Slide 3: Your Approach (60 seconds)
Slide 4-5: Key Result (2-3 minutes)
Slide 6: Impact/Implications (45 seconds)
Slide 7: Conclusion + Contact (30 seconds)
```

**Key Principles**:
- ONE main message only
- Maximize visuals, minimize text
- No methods details (just mention approach)
- Practice exact timing rigorously
- Make memorable impression
- Goal: Generate "tell me more" conversations

### Poster Spotlight Talks (3 Minutes)

**Purpose**: Drive traffic to poster session

**Structure**:
```
1 slide: Title + Context (30 seconds)
2 slides: Problem + Approach (60 seconds)
2 slides: Most Interesting Result (60 seconds)
1 slide: "Visit my poster at #42" (30 seconds)
```

**Tips**:
- Show teaser, not full story
- Include poster number prominently
- Use QR code for details
- Explicitly invite audience: "Come ask me about..."

## Academic Seminars

### Context and Expectations

**Typical Characteristics**:
- **Duration**: 45-60 minutes
- **Audience**: Department faculty, students, postdocs
- **Setting**: Single presentation, full attention
- **Goal**: Deep dive into research, get feedback, show expertise
- **Format**: Extended Q&A (10-15 minutes), interruptions welcome

**Challenges**:
- Maintaining engagement for longer duration
- Balancing depth and accessibility
- Handling interruptions smoothly
- Demonstrating mastery of broader field
- Satisfying both experts and non-experts

### Structure for 50-Minute Seminar

**Recommended Slide Count**: 40-50 slides

**Time Allocation**:
```
Introduction (8-10 minutes, 8-10 slides):
- Personal introduction (1 minute)
- Big picture context (3-4 minutes)
- Literature review (3-4 minutes)
- Research questions (1-2 minutes)
- Roadmap/outline (1 minute)

Methods (8-10 minutes, 8-10 slides):
- Study design with rationale (2-3 minutes)
- Participants/materials (2 minutes)
- Procedures (3-4 minutes)
- Analysis approach (2 minutes)

Results (18-22 minutes, 16-20 slides):
- Overview/demographics (2 minutes)
- Main finding 1 (6-8 minutes)
- Main finding 2 (6-8 minutes)
- Additional analyses (4-6 minutes)
- Summary slide (1 minute)

Discussion (10-12 minutes, 8-10 slides):
- Summary of findings (2 minutes)
- Relation to literature (3-4 minutes)
- Mechanisms/explanations (2-3 minutes)
- Limitations (2 minutes)
- Implications (2 minutes)

Conclusion (2-3 minutes, 2-3 slides):
- Key messages (1 minute)
- Future directions (1-2 minutes)
- Acknowledgments (30 seconds)
```

### Seminar Best Practices

**Opening**:
- ✅ Establish credibility and context
- ✅ Make personal connection to research
- ✅ Show enthusiasm and passion
- ✅ Provide roadmap of talk structure
- ❌ Don't assume all background knowledge
- ❌ Don't be overly formal or stiff

**Content**:
- ✅ Go deeper into methods than conference talk
- ✅ Show multiple related findings or studies
- ✅ Discuss failed experiments and pivots (shows thinking)
- ✅ Present ongoing/unpublished work
- ✅ Connect to broader theoretical questions
- ❌ Don't present every detail of every analysis
- ❌ Don't ignore alternative explanations
- ❌ Don't oversell findings

**Engagement**:
- ✅ Welcome interruptions: "Please feel free to ask questions"
- ✅ Use checkpoint questions: "Does this make sense?"
- ✅ Engage with questioners genuinely
- ✅ Admit what you don't know
- ✅ Ask audience for input on challenges
- ❌ Don't be defensive about criticism
- ❌ Don't dismiss questions as "off topic"
- ❌ Don't monopolize Q&A time

**Pacing**:
- Build in natural pause points
- Don't rush (you have time)
- Vary delivery speed and tone
- Use humor appropriately
- Monitor audience engagement

### Job Talk Considerations

**Additional Expectations**:
- Show research program trajectory (past → present → future)
- Demonstrate independent thinking
- Show you can mentor students
- Explain funding strategy
- Fit with department emphasized
- Teaching philosophy may be discussed

**Structure Adaptation**:
- Add "Future Directions" section (5 minutes, 3-4 slides)
- Show multiple projects if relevant
- Discuss collaborative opportunities
- Mention grant applications/funding

## Thesis and Dissertation Defenses

### Context and Expectations

**Typical Characteristics**:
- **Duration**: 30-60 minutes (varies by institution)
- **Audience**: Committee, colleagues, family
- **Setting**: Formal examination
- **Goal**: Demonstrate mastery, defend research decisions
- **Format**: Extended Q&A (30-90 minutes), private or public

**Unique Aspects**:
- Committee has read dissertation
- Questioning can be extensive and critical
- Evaluation of student's independence and expertise
- May include private committee discussion
- Career milestone, significant pressure

### Structure for 45-Minute Defense

**Recommended Slide Count**: 40-50 slides

**Time Allocation**:
```
Introduction (5 minutes, 5-6 slides):
- Research context and motivation
- Central thesis question
- Overview of studies/chapters
- Roadmap

Literature Review (5 minutes, 4-5 slides):
- Theoretical framework
- Key prior findings
- Knowledge gaps
- Your contribution

Study 1 (8-10 minutes, 10-12 slides):
- Research question
- Methods
- Results
- Interim conclusions

Study 2 (8-10 minutes, 10-12 slides):
- Research question
- Methods
- Results
- Interim conclusions

Study 3 (optional) (8-10 minutes, 10-12 slides):
- Research question
- Methods
- Results
- Interim conclusions

General Discussion (8-10 minutes, 8-10 slides):
- Synthesis across studies
- Theoretical implications
- Practical applications
- Limitations (comprehensive)
- Future research directions

Conclusions (2-3 minutes, 2-3 slides):
- Main contributions
- Final thoughts
- Acknowledgments
```

### Defense Best Practices

**Preparation**:
- ✅ Practice extensively (5+ times)
- ✅ Anticipate every possible question
- ✅ Prepare backup slides with extra analyses
- ✅ Review key literature thoroughly
- ✅ Understand limitations deeply
- ✅ Practice Q&A with colleagues
- ❌ Don't assume committee remembers all details
- ❌ Don't leave preparation to last minute

**Content**:
- ✅ Comprehensive coverage of all studies
- ✅ Clear connection between studies
- ✅ Address limitations proactively
- ✅ Show theoretical contribution
- ✅ Demonstrate independent thinking
- ✅ Acknowledge contributions of others
- ❌ Don't minimize limitations
- ❌ Don't oversell findings
- ❌ Don't ignore null results

**Q&A Approach**:
- ✅ Listen carefully to full question
- ✅ Pause before answering (shows thoughtfulness)
- ✅ Admit when you don't know
- ✅ Engage with criticism constructively
- ✅ Refer to specific slides or dissertation sections
- ✅ Thank questioner for insights
- ❌ Don't be defensive or argumentative
- ❌ Don't dismiss concerns
- ❌ Don't ramble in answers

**Handling Difficult Questions**:
- **Critique of methods**: Acknowledge limitation, explain rationale, note in future work
- **Alternative interpretations**: "That's an interesting perspective. I focused on X because... but Y is worth exploring"
- **Why didn't you do X?**: "That would be valuable. Due to [constraint], I prioritized... Future work should examine that"
- **Contradiction in results**: "You're right that seems inconsistent. One possible explanation is..."

## Grant Pitches and Funding Presentations

### Context and Expectations

**Typical Characteristics**:
- **Duration**: 10-20 minutes (varies widely)
- **Audience**: Funding panel, non-specialists, decision-makers
- **Setting**: Evaluative, competitive
- **Goal**: Secure funding, demonstrate feasibility and impact
- **Format**: Presentation + Q&A focused on logistics and impact

**Evaluation Criteria**:
- Significance and innovation
- Approach and feasibility
- Investigator qualifications
- Environment and resources
- Budget justification

### Structure for 15-Minute Grant Pitch

**Recommended Slide Count**: 12-15 slides

**Time Allocation**:
```
Significance (3-4 minutes, 3-4 slides):
- Problem statement with impact (90 seconds)
- Current state and limitations (90 seconds)
- Opportunity and innovation (60-90 seconds)

Approach (5-6 minutes, 5-6 slides):
- Overall strategy (60 seconds)
- Aim 1: Approach and expected outcomes (90 seconds)
- Aim 2: Approach and expected outcomes (90 seconds)
- Aim 3: Approach and expected outcomes (optional, 90 seconds)
- Timeline and milestones (60 seconds)

Impact and Feasibility (4-5 minutes, 3-4 slides):
- Preliminary data (2 minutes)
- Expected impact (1 minute)
- Team and resources (1 minute)
- Alternative strategies for risks (60 seconds)

Conclusion (1 minute, 1 slide):
- Summary of innovation and impact
- Budget highlight (if appropriate)
```

### Grant Pitch Best Practices

**Significance**:
- ✅ Lead with impact (lives saved, costs reduced, knowledge gained)
- ✅ Use compelling statistics and real-world examples
- ✅ Clearly state innovation (what's new?)
- ✅ Connect to funder's mission and priorities
- ❌ Don't assume audience knows why it matters
- ❌ Don't be vague about expected outcomes

**Approach**:
- ✅ Show feasibility (you can actually do this)
- ✅ Present clear, logical aims
- ✅ Show preliminary data demonstrating proof-of-concept
- ✅ Explain why your approach will work
- ✅ Address potential challenges proactively
- ❌ Don't be overly technical
- ❌ Don't ignore obvious challenges
- ❌ Don't propose unrealistic timelines

**Team and Resources**:
- ✅ Highlight key personnel expertise
- ✅ Show institutional support
- ✅ Mention prior funding success
- ✅ Demonstrate appropriate resources available
- ❌ Don't undersell your qualifications
- ❌ Don't propose work beyond your expertise without collaborators

**Q&A Focus**:
- Expect questions about:
  - Budget justification
  - Timeline and milestones
  - What if Aim 1 fails?
  - How is this different from X's work?
  - How will you sustain this beyond grant period?
  - Dissemination and translation plans

## Journal Club Presentations

### Context and Expectations

**Typical Characteristics**:
- **Duration**: 20-45 minutes
- **Audience**: Lab members, colleagues, students
- **Setting**: Educational, critical discussion
- **Goal**: Understand paper, critique methods, discuss implications
- **Format**: Heavy Q&A, interactive discussion

**Unique Aspects**:
- Presenting others' work, not your own
- Critical analysis expected
- Audience may have read paper
- Educational component important
- Discussion more important than presentation

### Structure for 30-Minute Journal Club

**Recommended Slide Count**: 15-20 slides

**Time Allocation**:
```
Context (2-3 minutes, 2-3 slides):
- Paper citation and authors
- Why you chose this paper
- Background and significance

Introduction (3-4 minutes, 2-3 slides):
- Research question
- Prior work and gaps
- Hypotheses

Methods (5-7 minutes, 4-6 slides):
- Study design
- Participants/materials
- Procedures
- Analysis approach
- Your assessment of methods

Results (8-10 minutes, 5-7 slides):
- Main findings
- Key figures explained
- Statistical results
- Your interpretation

Discussion (5-7 minutes, 3-4 slides):
- Authors' interpretation
- Strengths of study
- Limitations and concerns
- Implications for field
- Future directions

Critical Analysis (3-5 minutes, 1-2 slides):
- What did we learn?
- What questions remain?
- How does this change our thinking?
- Relevance to our work
```

### Journal Club Best Practices

**Preparation**:
- ✅ Read paper multiple times
- ✅ Read key cited references
- ✅ Look up unfamiliar methods or concepts
- ✅ Check other papers from same group
- ✅ Prepare critical questions for discussion
- ❌ Don't just summarize without analysis

**Presentation**:
- ✅ Explain paper clearly (not everyone may have read it)
- ✅ Highlight key figures and data
- ✅ Point out strengths and innovations
- ✅ Identify limitations or concerns
- ✅ Be fair but critical
- ✅ Connect to group's research interests
- ❌ Don't just read the paper aloud
- ❌ Don't be overly harsh or dismissive
- ❌ Don't skip methods (often most important)

**Critical Analysis**:
- ✅ Question methodological choices
- ✅ Consider alternative interpretations
- ✅ Identify what's missing
- ✅ Discuss implications thoughtfully
- ✅ Suggest follow-up experiments
- ❌ Don't accept everything at face value
- ❌ Don't nitpick minor issues while missing major flaws
- ❌ Don't let personal biases dominate

**Discussion Facilitation**:
- Pose open-ended questions
- "What do you think about their interpretation of Figure 3?"
- "Is this the right control experiment?"
- "How would you design the follow-up study?"
- Encourage quiet members to contribute
- Keep discussion focused and productive

## Industry and Investor Presentations

### Context and Expectations

**Typical Characteristics**:
- **Duration**: 10-30 minutes (often shorter)
- **Audience**: Non-scientists, business decision-makers
- **Setting**: High stakes, evaluative
- **Goal**: Secure investment, partnership, or approval
- **Format**: Emphasis on business case and timeline

**Key Differences from Academic Talks**:
- Emphasis on applications, not mechanisms
- Market size and competition important
- Intellectual property considerations
- Return on investment focus
- Less technical detail expected

### Structure for 20-Minute Industry Pitch

**Time Allocation**:
```
Problem and Market (3-4 minutes):
- Unmet need or problem
- Market size and opportunity
- Current solutions and limitations

Solution (4-5 minutes):
- Your technology or approach
- Key innovations
- Proof of concept data
- Advantages over alternatives

Development Plan (5-6 minutes):
- Current status (TRL/stage)
- Development roadmap
- Key milestones and timeline
- Regulatory pathway (if applicable)

Business Case (4-5 minutes):
- Target customers/users
- Revenue model
- Competitive landscape
- Intellectual property status
- Team and partnerships

Funding Ask (2-3 minutes):
- Investment needed
- Use of funds
- Expected outcomes
- Exit strategy or ROI
```

### Industry Pitch Best Practices

**Language**:
- ✅ Simple, clear language (no jargon)
- ✅ Focus on benefits and outcomes
- ✅ Use business metrics (TAM, SAM, SOM)
- ✅ Emphasize competitive advantages
- ❌ Don't use academic terminology
- ❌ Don't focus on mechanistic details
- ❌ Don't ignore commercial viability

**Emphasis**:
- Lead with problem and market opportunity
- Show proof of concept clearly
- Demonstrate clear path to commercialization
- Highlight team's ability to execute
- Be realistic about risks and challenges

## Teaching and Tutorial Presentations

### Context and Expectations

**Typical Characteristics**:
- **Duration**: 45-90 minutes
- **Audience**: Students, learners, varied expertise
- **Setting**: Educational, classroom or workshop
- **Goal**: Teach concepts, methods, or skills
- **Format**: Interactive, may include exercises

**Structure for 60-Minute Tutorial**:
```
Introduction (5 minutes):
- Learning objectives
- Why this topic matters
- Prerequisites and assumptions

Foundations (10-15 minutes):
- Essential background
- Key concepts defined
- Simple examples

Core Content - Part 1 (15-20 minutes):
- Main topic area 1
- Detailed explanation
- Examples and demonstrations

Core Content - Part 2 (15-20 minutes):
- Main topic area 2
- Detailed explanation
- Examples and demonstrations

Practice/Application (10-15 minutes):
- Hands-on exercise or case study
- Q&A and discussion
- Common pitfalls

Summary (5 minutes):
- Key takeaways
- Resources for further learning
- Next steps
```

### Tutorial Best Practices

**Content**:
- ✅ Build complexity gradually
- ✅ Use many examples
- ✅ Repeat key concepts
- ✅ Check understanding frequently
- ✅ Provide resources and references
- ❌ Don't assume prior knowledge
- ❌ Don't move too quickly

**Engagement**:
- ✅ Ask questions to audience
- ✅ Include interactive elements
- ✅ Use demonstrations
- ✅ Encourage questions throughout
- ✅ Provide practice opportunities
- ❌ Don't lecture non-stop for 60 minutes

## Summary: Choosing the Right Approach

| Talk Type | Duration | Audience | Depth | Key Focus |
|-----------|----------|----------|-------|-----------|
| Lightning | 5-7 min | General | Minimal | One key finding |
| Conference | 15 min | Specialists | Moderate | Main results |
| Seminar | 45-60 min | Experts | Deep | Comprehensive |
| Defense | 45-60 min | Committee | Complete | All studies |
| Grant | 15-20 min | Mixed | Moderate | Impact & feasibility |
| Journal Club | 30-45 min | Lab group | Critical | Methods & interpretation |
| Industry | 15-30 min | Non-scientists | Applied | Business case |

### Adaptation Checklist

When preparing any talk, consider:

- [ ] Who is my audience? (Expertise level, background, expectations)
- [ ] How much time do I have? (Strictly enforced or flexible?)
- [ ] What is the goal? (Inform, persuade, teach, impress?)
- [ ] What format is expected? (Formal vs. interactive, Q&A style)
- [ ] What will happen afterward? (Q&A, discussion, evaluation, networking)
- [ ] What are the logistics? (Room size, A/V setup, recording, remote?)

Adapt your structure, content depth, language, and delivery style accordingly.

### `references/visual_review_workflow.md`

# Visual Review Workflow for Presentations

## Overview

Visual review is a critical quality assurance step for presentations, allowing you to identify and fix layout issues, text overflow, element overlap, and design problems before presenting. This guide covers converting presentations to images, systematic visual inspection, common issues, and iterative improvement strategies.

## ⚠️ CRITICAL RULE: NEVER READ PDF PRESENTATIONS DIRECTLY

**MANDATORY: Always convert presentation PDFs to images FIRST, then review the images.**

### Why This Rule Exists

- **Buffer Overflow Prevention**: Presentation PDFs (especially multi-slide decks) cause "JSON message exceeded maximum buffer size" errors when read directly
- **Visual Accuracy**: Images show exactly what the audience will see, including rendering issues
- **Performance**: Image-based review is faster and more reliable than PDF text extraction
- **Consistency**: Ensures uniform review process for all presentations

### The ONLY Correct Workflow for Presentations

1. ✅ Generate PDF from PowerPoint/Beamer source
2. ✅ **Convert PDF to images** using the pdf_to_images.py script
3. ✅ **Review the image files** systematically
4. ✅ Document issues by slide number
5. ✅ Fix issues in source files
6. ✅ Regenerate PDF and repeat

### What NOT To Do

- ❌ NEVER use read_file tool on presentation PDFs
- ❌ NEVER attempt to read PDF slides as text
- ❌ NEVER skip the image conversion step
- ❌ NEVER assume PDF is "small enough" to read directly

**If you're reviewing a presentation and haven't converted to images yet, STOP and convert first.**

## Why Visual Review Matters

### Common Problems Invisible in Source

**LaTeX Beamer Issues**:
- Text overflow from text boxes
- Overlapping elements (equations over images)
- Poor line breaking
- Figures extending beyond slide boundaries
- Font size issues at actual resolution

**PowerPoint Issues**:
- Text cut off by shapes or slide edges
- Images overlapping with text
- Inconsistent spacing between slides
- Color rendering differences
- Font substitution problems

**Projection Issues**:
- Content visible on laptop but cut off when projected
- Colors looking different on projector
- Low contrast elements becoming invisible
- Small details disappearing

### Benefits of Visual Review

- **Catch layout errors early**: Fix before printing or presenting
- **Verify readability**: Ensure text is large enough and high contrast
- **Check consistency**: Spot inconsistencies across slides
- **Test accessibility**: Verify color contrast and clarity
- **Validate design**: Ensure professional appearance

## Conversion: PDF to Images

### Method 1: Using pdf_to_images.py Script (Recommended)

**No External Dependencies Required**:
The script uses PyMuPDF, a self-contained Python library - no poppler or other system software needed.

**Installation**:
```bash
# PyMuPDF is included as a project dependency
uv pip install pymupdf
```

**Basic Conversion**:
```bash
# Convert all slides to JPEG images
python skills/scientific-slides/scripts/pdf_to_images.py presentation.pdf slide --dpi 150

# Creates: slide-001.jpg, slide-002.jpg, slide-003.jpg, ...
```

**High-Resolution Conversion**:
```bash
# Higher quality for detailed inspection (300 DPI)
python skills/scientific-slides/scripts/pdf_to_images.py presentation.pdf slide --dpi 300

# PNG format (lossless, larger files)
python skills/scientific-slides/scripts/pdf_to_images.py presentation.pdf slide --dpi 150 --format png
```

**Convert Specific Slides**:
```bash
# Slides 5-10 only
python skills/scientific-slides/scripts/pdf_to_images.py presentation.pdf slide --dpi 150 --first 5 --last 10

# Single slide
python skills/scientific-slides/scripts/pdf_to_images.py presentation.pdf slide --dpi 150 --first 3 --last 3
```

**Output Options**:
```bash
# Different output directory
python skills/scientific-slides/scripts/pdf_to_images.py presentation.pdf review/slide --dpi 150

# Custom naming
python skills/scientific-slides/scripts/pdf_to_images.py presentation.pdf output/presentation --dpi 150
```

### Method 2: Using PowerPoint Thumbnail Script

For PowerPoint presentations, use the pptx skill's thumbnail tool:

```bash
# Create thumbnail grid
python scripts/thumbnail.py presentation.pptx output --cols 4

# Individual slides
python scripts/thumbnail.py presentation.pptx slides/slide --individual
```

**Advantages**:
- Optimized for PowerPoint files
- Can create overview grids
- Handles .pptx format directly
- Customizable layout

### Method 3: Using ImageMagick

**Installation**:
```bash
# Ubuntu/Debian
sudo apt-get install imagemagick

# macOS
brew install imagemagick
```

**Conversion**:
```bash
# Convert PDF to images
convert -density 150 presentation.pdf slide.jpg

# Higher quality
convert -density 300 presentation.pdf slide.jpg

# Specific format
convert -density 150 presentation.pdf slide.png
```

### Method 4: Using Python (Programmatic)

```python
import fitz  # PyMuPDF

# Open PDF
doc = fitz.open('presentation.pdf')

# Convert each page to image
zoom = 200 / 72  # 200 DPI (72 is base DPI)
matrix = fitz.Matrix(zoom, zoom)

for i, page in enumerate(doc, start=1):
    pixmap = page.get_pixmap(matrix=matrix)
    pixmap.save(f'slide-{i:03d}.jpg', output='jpeg')

doc.close()
```

**Install PyMuPDF**:
```bash
uv pip install pymupdf
# No external dependencies needed!
```

## Systematic Visual Inspection

### Inspection Workflow

**Step 1: Overview Pass**
- View all slides quickly
- Note overall consistency
- Identify obviously problematic slides
- Create list of slides needing detailed review

**Step 2: Detailed Inspection**
- Review each flagged slide carefully
- Check against issue checklist (below)
- Document specific problems with slide numbers
- Take notes on required fixes

**Step 3: Cross-Slide Comparison**
- Check consistency across similar slides
- Verify uniform spacing and alignment
- Ensure consistent font sizes
- Check color scheme consistency

**Step 4: Distance Test**
- View images at reduced size (simulates projection)
- Check readability from ~6 feet
- Verify key elements are visible
- Test if main message is clear

### Issue Checklist

Review each slide for these common problems:

#### Text Issues

**Overflow and Truncation**:
- [ ] Text cut off at slide edges
- [ ] Text extending beyond text boxes
- [ ] Equations running into margins
- [ ] Captions cut off at bottom
- [ ] Bullet points extending beyond boundary

**Readability**:
- [ ] Font size too small (minimum 18pt visible)
- [ ] Poor contrast (text vs background)
- [ ] Inadequate line spacing
- [ ] Text too close to slide edge
- [ ] Overlapping lines of text

#### Element Overlap

**Text Overlaps**:
- [ ] Text overlapping with images
- [ ] Text overlapping with shapes
- [ ] Multiple text boxes overlapping
- [ ] Labels overlapping with data points
- [ ] Title overlapping with content

**Visual Element Overlaps**:
- [ ] Images overlapping
- [ ] Shapes overlapping inappropriately
- [ ] Figures extending into margins
- [ ] Legend overlapping with plot
- [ ] Watermark obscuring content

#### Layout and Spacing

**Alignment Issues**:
- [ ] Misaligned text boxes
- [ ] Uneven margins
- [ ] Inconsistent element positioning
- [ ] Off-center titles
- [ ] Unaligned bullet points

**Spacing Problems**:
- [ ] Cramped content (insufficient white space)
- [ ] Too much empty space (poor use of slide area)
- [ ] Inconsistent spacing between elements
- [ ] Uneven gaps in multi-column layouts
- [ ] Poor distribution of content

#### Color and Contrast

**Visibility**:
- [ ] Insufficient contrast (text vs background)
- [ ] Colors too similar (hard to distinguish)
- [ ] Text on busy backgrounds
- [ ] Light text on light background
- [ ] Dark text on dark background

**Consistency**:
- [ ] Inconsistent color schemes between slides
- [ ] Unexpected color changes
- [ ] Clashing color combinations
- [ ] Poor color choices for data visualization

#### Figures and Graphics

**Quality**:
- [ ] Pixelated or blurry images
- [ ] Low-resolution figures
- [ ] Distorted aspect ratios
- [ ] Poor quality screenshots
- [ ] Jagged edges on graphics

**Layout**:
- [ ] Figures too small to read
- [ ] Axis labels too small
- [ ] Legend text illegible
- [ ] Complex figures without explanation
- [ ] Figures not centered or aligned

#### Technical Issues

**Rendering**:
- [ ] Missing fonts (substituted)
- [ ] Special characters not displaying
- [ ] Equations rendering incorrectly
- [ ] Broken images or missing files
- [ ] Incorrect colors (RGB vs CMYK)

**Consistency**:
- [ ] Slide numbers incorrect or missing
- [ ] Inconsistent footer/header
- [ ] Navigation elements broken
- [ ] Hyperlinks not working (if testing interactively)

## Documentation Template

### Issue Log Format

Create a spreadsheet or document tracking all issues:

```
Slide # | Issue Category | Description | Severity | Status
--------|---------------|-------------|----------|--------
3       | Text Overflow | Bullet point 4 extends beyond box | High | Fixed
7       | Element Overlap | Figure overlaps with caption | High | Fixed
12      | Font Size | Axis labels too small | Medium | Fixed
15      | Alignment | Title not centered | Low | Fixed
22      | Contrast | Yellow text on white background | High | Fixed
```

**Severity Levels**:
- **Critical**: Makes slide unusable or unprofessional
- **High**: Significantly impacts readability or appearance
- **Medium**: Noticeable but doesn't prevent comprehension
- **Low**: Minor cosmetic issues

### Example Issue Documentation

**Good Documentation**:
```
Slide 8: Text Overflow Issue
- Description: Last bullet point "...implementation details" 
  extends ~0.5 inches beyond right margin of text box
- Cause: Bullet text too long for available width
- Fix: Reduce text to "...implementation" or increase box width
- Verification: Check neighboring slides for similar issue
```

**Poor Documentation**:
```
Slide 8: text problem
- Fix: make smaller
```

## Common Issues and Solutions

### Issue 1: Text Overflow

**Problem**: Text extends beyond boundaries

**Identification**:
- Visible text cut off at edge
- Text running into margins
- Partial characters visible

**Solutions**:

**LaTeX Beamer**:
```latex
% Reduce text
\begin{frame}{Title}
  \begin{itemize}
    \item Shorten this long bullet point
    % or
    \item Use abbreviations or acronyms
    % or
    \item<alert@1> Split into multiple bullets
  \end{itemize}
\end{frame}

% Adjust margins
\newgeometry{margin=1.5cm}
\begin{frame}
  Content with wider margins
\end{frame}
\restoregeometry

% Smaller font for specific element
{\small
  Long text that needs to fit
}
```

**PowerPoint**:
- Reduce font size for that element
- Shorten text content
- Increase text box size
- Use text box auto-fit options (cautiously)
- Split into multiple slides

### Issue 2: Element Overlap

**Problem**: Elements overlapping inappropriately

**Identification**:
- Text obscured by images
- Shapes covering text
- Figures overlapping

**Solutions**:

**LaTeX Beamer**:
```latex
% Use columns for better separation
\begin{columns}
  \begin{column}{0.5\textwidth}
    Text content
  \end{column}
  \begin{column}{0.5\textwidth}
    \includegraphics[width=\textwidth]{figure.pdf}
  \end{column}
\end{columns}

% Add spacing
\vspace{0.5cm}

% Adjust figure size
\includegraphics[width=0.7\textwidth]{figure.pdf}
```

**PowerPoint**:
- Use alignment guides to reposition
- Reduce element sizes
- Use two-column layout
- Send elements backward/forward (layering)
- Increase spacing between elements

### Issue 3: Poor Contrast

**Problem**: Text difficult to read due to color choices

**Identification**:
- Squinting required to read text
- Text fades into background
- Colors too similar

**Solutions**:

**LaTeX Beamer**:
```latex
% Increase contrast
\setbeamercolor{frametitle}{fg=black,bg=white}
\setbeamercolor{normal text}{fg=black,bg=white}

% Use darker colors
\definecolor{darkblue}{RGB}{0,50,100}
\setbeamercolor{structure}{fg=darkblue}

% Test in grayscale
\usepackage{xcolor}
\selectcolormodel{gray}  % Temporarily for testing
```

**PowerPoint**:
- Choose high-contrast color combinations
- Use dark text on light background or vice versa
- Avoid pastels for text
- Test with WebAIM contrast checker
- Add text background box if needed

### Issue 4: Tiny Fonts

**Problem**: Text too small to read from distance

**Identification**:
- Can't read text from 3 feet away
- Axis labels disappear when viewing normally
- Captions illegible

**Solutions**:

**LaTeX Beamer**:
```latex
% Increase base font size
\documentclass[14pt]{beamer}  % Instead of 11pt default

% Recreate figures with larger fonts
% In matplotlib:
plt.rcParams['font.size'] = 18
plt.rcParams['axes.labelsize'] = 20

% In R/ggplot2:
theme_set(theme_minimal(base_size = 16))
```

**PowerPoint**:
- Minimum 18pt for body text, 24pt preferred
- Recreate figures with larger labels
- Use direct labeling instead of legends
- Simplify complex figures
- Split dense content across multiple slides

### Issue 5: Misalignment

**Problem**: Elements not properly aligned

**Identification**:
- Uneven margins
- Titles at different positions
- Irregular spacing

**Solutions**:

**LaTeX Beamer**:
```latex
% Use consistent templates
\setbeamertemplate{frametitle}[default][center]

% Align columns at top
\begin{columns}[T]  % T = top alignment
  \begin{column}{0.5\textwidth}
    Content
  \end{column}
  \begin{column}{0.5\textwidth}
    Content
  \end{column}
\end{columns}

% Center figures
\begin{center}
  \includegraphics[width=0.8\textwidth]{figure.pdf}
\end{center}
```

**PowerPoint**:
- Use alignment tools (Align Left/Center/Right)
- Enable gridlines and guides
- Use snap to grid
- Distribute objects evenly
- Create master slides with consistent layouts

## Iterative Improvement Process

### Workflow Cycle

```
1. Generate PDF
    ↓
2. Convert to images
    ↓
3. Systematic visual inspection
    ↓
4. Document issues
    ↓
5. Prioritize fixes
    ↓
6. Apply corrections to source
    ↓
7. Regenerate PDF
    ↓
8. Re-inspect (go to step 2)
    ↓
9. Complete when no critical issues remain
```

### Prioritization Strategy

**Fix Immediately** (Block presentation):
- Text overflow making content unreadable
- Critical element overlaps obscuring data
- Broken figures or missing content
- Severely poor contrast

**Fix Before Presenting**:
- Font sizes too small
- Moderate alignment issues
- Inconsistent spacing
- Moderate contrast problems

**Fix If Time Permits**:
- Minor misalignments
- Small spacing inconsistencies
- Cosmetic improvements
- Non-critical color adjustments

### Stopping Criteria

**Minimum Standards**:
- [ ] No text overflow or truncation
- [ ] No element overlaps obscuring content
- [ ] All text readable at minimum 18pt equivalent
- [ ] Adequate contrast (4.5:1 ratio minimum)
- [ ] Figures and images display correctly
- [ ] Consistent slide structure

**Ideal Standards**:
- [ ] Professional appearance throughout
- [ ] Consistent alignment and spacing
- [ ] High contrast (7:1 ratio)
- [ ] Optimal font sizes (24pt+)
- [ ] Polished visual design
- [ ] Zero layout issues

## Automated Detection Strategies

### Python Script for Text Overflow Detection

```python
from PIL import Image
import numpy as np

def detect_edge_content(image_path, threshold=10):
    """
    Detect if content extends too close to slide edges.
    Returns True if potential overflow detected.
    """
    img = Image.open(image_path).convert('L')  # Grayscale
    arr = np.array(img)
    
    # Check edges (10 pixel border)
    left_edge = arr[:, :threshold]
    right_edge = arr[:, -threshold:]
    top_edge = arr[:threshold, :]
    bottom_edge = arr[-threshold:, :]
    
    # Look for non-white pixels (content)
    white_threshold = 240
    
    issues = []
    if np.any(left_edge < white_threshold):
        issues.append("Left edge")
    if np.any(right_edge < white_threshold):
        issues.append("Right edge")
    if np.any(top_edge < white_threshold):
        issues.append("Top edge")
    if np.any(bottom_edge < white_threshold):
        issues.append("Bottom edge")
    
    return issues

# Usage
for slide_num in range(1, 26):
    issues = detect_edge_content(f'slide-{slide_num}.jpg')
    if issues:
        print(f"Slide {slide_num}: Content near {', '.join(issues)}")
```

### Contrast Checking

```python
from PIL import Image
import numpy as np

def check_contrast(image_path):
    """
    Estimate contrast ratio in image.
    Simple version: compare lightest and darkest regions.
    """
    img = Image.open(image_path).convert('L')
    arr = np.array(img)
    
    # Get brightness values
    bright = np.percentile(arr, 95)
    dark = np.percentile(arr, 5)
    
    # Rough contrast ratio
    contrast = (bright + 0.05) / (dark + 0.05)
    
    if contrast < 4.5:
        return f"Low contrast: {contrast:.1f}:1 (minimum 4.5:1)"
    return f"OK: {contrast:.1f}:1"

# Usage
for slide_num in range(1, 26):
    result = check_contrast(f'slide-{slide_num}.jpg')
    print(f"Slide {slide_num}: {result}")
```

## Manual Review Best Practices

### Review Environment

**Setup**:
- Large monitor or dual monitors
- Good lighting (not too bright, not dark)
- Distraction-free environment
- Image viewer with zoom capability
- Notepad or spreadsheet for tracking issues

**Viewing Options**:
- View at 100% for detail inspection
- View at 50% to simulate distance
- View in sequence to check consistency
- Compare similar slides side-by-side

### Review Tips

**Fresh Eyes**:
- Take breaks every 15-20 slides
- Review at different times of day
- Get colleague to review
- Come back next day for final check

**Systematic Approach**:
- Review in order (slide 1 → end)
- Focus on one issue type at a time
- Use checklist to ensure thoroughness
- Document as you go, not from memory

**Common Oversights**:
- Backup slides (review these too!)
- Title slide (first impression matters)
- Acknowledgments slide (often forgotten)
- Last slide (visible during Q&A)

## Tools and Resources

### Recommended Software

**PDF to Image Conversion**:
- **PyMuPDF** (Python): Fast, no external dependencies (recommended)
- **pdf_to_images.py script**: Wrapper for easy CLI usage
- **ImageMagick**: Flexible, many options (optional)

**Image Viewing**:
- **IrfanView** (Windows): Fast, many formats
- **Preview** (macOS): Built-in, simple
- **Eye of GNOME** (Linux): Lightweight
- **XnView**: Cross-platform, batch operations

**Issue Tracking**:
- **Spreadsheet** (Excel, Google Sheets): Simple, flexible
- **Markdown file**: Version control friendly
- **Issue tracker** (GitHub, Jira): If team collaboration
- **Checklist app**: For mobile review

### Contrast Checkers

- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Colour Contrast Analyser**: Desktop application
- **Chrome DevTools**: Built-in contrast checking

### Color Blindness Simulators

- **Coblis**: https://www.color-blindness.com/coblis-color-blindness-simulator/
- **Color Oracle**: Free desktop application
- **Photoshop/GIMP**: Built-in color blindness filters

## Summary Checklist

Before finalizing your presentation:

**Conversion**:
- [ ] PDF converted to images at adequate resolution (150-300 DPI)
- [ ] All slides converted (including backup slides)
- [ ] Images saved in organized directory

**Visual Inspection**:
- [ ] All slides reviewed systematically
- [ ] Issue checklist completed for each slide
- [ ] Problems documented with slide numbers
- [ ] Severity assigned to each issue

**Issue Resolution**:
- [ ] Critical issues fixed
- [ ] High-priority issues addressed
- [ ] Source files updated (not just PDF)
- [ ] Regenerated and re-inspected

**Final Verification**:
- [ ] No text overflow or truncation
- [ ] No inappropriate element overlaps
- [ ] Adequate contrast throughout
- [ ] Consistent layout and spacing
- [ ] Professional appearance
- [ ] Ready for projection or distribution

**Testing**:
- [ ] Tested on projector if possible
- [ ] Viewed from back of room distance
- [ ] Checked in various lighting conditions
- [ ] Backup copy saved

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

### `scripts/generate_slide_image.py`

```python
#!/usr/bin/env python3
"""
Slide image generation using Nano Banana Pro.

Generate presentation slides or visuals by describing them in natural language.
Nano Banana Pro handles everything automatically with smart iterative refinement.

Two modes:
- Default (full slide): Generate complete slides with title, content, visuals (for PDF workflow)
- Visual only: Generate just images/figures to place on slides (for PPT workflow)

Supports attaching reference images for context (Nano Banana Pro will see these).

Usage:
    # Generate full slide for PDF workflow
    python generate_slide_image.py "Title: Introduction\\nKey points: AI, ML, Deep Learning" -o slide_01.png
    
    # Generate visual only for PPT workflow
    python generate_slide_image.py "Neural network diagram" -o figure.png --visual-only
    
    # With reference images attached
    python generate_slide_image.py "Create a slide about this data" -o slide.png --attach chart.png
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
        description="Generate presentation slides or visuals using Nano Banana Pro AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
How it works:
  Describe your slide or visual in natural language.
  Nano Banana Pro generates it automatically with:
  - Smart iteration (only regenerates if quality is below threshold)
  - Quality review by Gemini 3.6 Flash
  - Publication-ready output

Modes:
  Default (full slide):  Generate complete slide with title, content, visuals
                         Use for PDF workflow where each slide is an image
  
  Visual only:           Generate just the image/figure
                         Use for PPT workflow where you add text separately

Attachments:
  Use --attach to provide reference images that Nano Banana Pro will see.
  This allows you to say "create a slide about this chart" and attach the chart.

Examples:
  # Full slide (default) - for PDF workflow
  python generate_slide_image.py "Title: Machine Learning\\nPoints: supervised, unsupervised, reinforcement" -o slide_01.png
  
  # Visual only - for PPT workflow  
  python generate_slide_image.py "Flowchart showing data pipeline" -o figure.png --visual-only
  
  # With reference images attached
  python generate_slide_image.py "Create a slide explaining this chart" -o slide.png --attach chart.png
  python generate_slide_image.py "Combine these into a comparison" -o compare.png --attach before.png --attach after.png
  
  # Multiple slides for PDF
  python generate_slide_image.py "Title slide: AI Conference 2025" -o slides/01_title.png
  python generate_slide_image.py "Title: Introduction\\nOverview of deep learning" -o slides/02_intro.png

Environment Variables:
  OPENROUTER_API_KEY    Required for AI generation
        """
    )
    
    parser.add_argument("prompt", help="Description of the slide or visual to generate")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("--attach", action="append", dest="attachments", metavar="IMAGE",
                       help="Attach image file(s) as context (can use multiple times)")
    parser.add_argument("--visual-only", action="store_true",
                       help="Generate just the visual/figure (for PPT workflow)")
    parser.add_argument("--iterations", type=int, default=2,
                       help="Maximum refinement iterations (default: 2, max: 2)")
    parser.add_argument("--api-key", help="OpenRouter API key (or use OPENROUTER_API_KEY env var)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
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
    ai_script = script_dir / "generate_slide_image_ai.py"
    
    if not ai_script.exists():
        print(f"Error: AI generation script not found: {ai_script}")
        sys.exit(1)
    
    # Build command
    cmd = [sys.executable, str(ai_script), args.prompt, "-o", args.output]
    
    # Add attachments
    if args.attachments:
        for att in args.attachments:
            cmd.extend(["--attach", att])
    
    if args.visual_only:
        cmd.append("--visual-only")
    
    # Enforce max 2 iterations
    iterations = min(args.iterations, 2)
    if iterations != 2:
        cmd.extend(["--iterations", str(iterations)])
    
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

### `scripts/generate_slide_image_ai.py`

```python
#!/usr/bin/env python3
"""
AI-powered slide image generation using Nano Banana Pro.

This script generates presentation slides or slide visuals using AI:
- full_slide mode: Generate complete slides with title, content, and visuals (for PDF workflow)
- visual_only mode: Generate just images/figures to place on slides (for PPT workflow)

Supports attaching reference images for context (e.g., "create a slide about this chart").

Uses smart iterative refinement:
1. Generate initial image with Nano Banana Pro
2. Quality review using Gemini 3.6 Flash
3. Only regenerate if quality is below threshold
4. Repeat until quality meets standards (max iterations)

Requirements:
    - OPENROUTER_API_KEY environment variable
    - requests library

Usage:
    # Full slide for PDF workflow
    python generate_slide_image_ai.py "Title: Introduction to ML\nKey points: supervised learning, neural networks" -o slide_01.png
    
    # Visual only for PPT workflow
    python generate_slide_image_ai.py "Neural network architecture diagram" -o figure.png --visual-only
    
    # With reference images attached
    python generate_slide_image_ai.py "Create a slide explaining this chart" -o slide.png --attach chart.png --attach logo.png
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
    invents a score: a slide whose quality was not measured is reported as
    unmeasured, not as passing.
    """

    critique: str
    score: Optional[float]
    needs_improvement: bool
    reviewed: bool
    error: Optional[str] = None


# Markdown decoration the reviewer routinely wraps its answer in. Gemini writes
# "**SCORE:** 8.5" far more often than the bare "SCORE: 8.5" the rubric asks
# for, and a pattern that does not allow for it silently scores every image
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
    the range quietly passes lenient thresholds while failing strict ones.
    """
    normalized = _normalize_review_text(text)
    match = _SCORE_PATTERN.search(normalized) or _LOOSE_SCORE_PATTERN.search(normalized)
    if not match:
        return None
    score = float(match.group(1))
    # A number outside the rubric's range means something other than the score
    # was matched -- a slide number, a percentage, an iteration number.
    return score if 0.0 <= score <= 10.0 else None


def _parse_verdict(text: str) -> Optional[str]:
    """Return ACCEPTABLE / NEEDS_IMPROVEMENT from the verdict line, or None.

    Anchored to the start of a line. The rubric prompt spells out both tokens
    when it explains the response format, so a reviewer that echoes those
    instructions back would fail a perfectly good image under a plain
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


class SlideImageGenerator:
    """Generate presentation slides or visuals using AI with iterative refinement.
    
    Two modes:
    - full_slide: Generate complete slide with title, content, visuals (for PDF workflow)
    - visual_only: Generate just the image/figure for a slide (for PPT workflow)
    """
    
    # Quality threshold for presentations (lower than journal/conference papers)
    QUALITY_THRESHOLD = 6.5
    
    # Guidelines for generating full slides (complete slide images)
    FULL_SLIDE_GUIDELINES = """
Create a professional presentation slide image with these requirements:

SLIDE LAYOUT (16:9 aspect ratio):
- Clean, modern slide design
- Clear visual hierarchy: title at top, content below
- Generous margins (at least 5% on all sides)
- Balanced composition with intentional white space

TYPOGRAPHY:
- LARGE, bold title text (easily readable from distance)
- Clear, sans-serif fonts throughout
- High contrast text (dark on light or light on dark)
- Bullet points or key phrases, NOT paragraphs
- Maximum 5-6 lines of text content
- Default author/presenter: "K-Dense" (use this unless another name is specified)

VISUAL ELEMENTS:
- Use GENERIC, simple images and icons - avoid overly specific or detailed imagery
- MINIMAL extra elements - no decorative borders, shadows, or flourishes
- Visuals should support and enhance the message, not distract
- Professional, clean aesthetic with restraint
- Consistent color scheme (2-3 main colors only)
- Prefer abstract/conceptual visuals over literal representations

PROFESSIONAL MINIMALISM:
- Less is more: favor empty space over additional elements
- No unnecessary decorations, gradients, or visual noise
- Clean lines and simple shapes
- Focused content without visual clutter
- Corporate/academic level of professionalism

PRESENTATION QUALITY:
- Designed for projection (high contrast)
- Bold, impactful design that commands attention
- Professional and polished appearance
- No cluttered or busy layouts
- Consistent styling throughout the deck
"""

    # Guidelines for generating slide visuals only (figures/images for PPT)
    VISUAL_ONLY_GUIDELINES = """
Create a high-quality visual/figure for a presentation slide:

IMAGE QUALITY:
- Clean, professional appearance
- High resolution and sharp details
- Suitable for embedding in a slide

DESIGN:
- Simple, clear composition with MINIMAL elements
- High contrast for projection readability
- No text unless essential to the visual
- Transparent or white background preferred
- GENERIC imagery - avoid overly specific or detailed visuals

PROFESSIONAL MINIMALISM:
- Favor simplicity over complexity
- No decorative elements, shadows, or flourishes
- Clean lines and simple shapes only
- Remove any unnecessary visual noise
- Abstract/conceptual rather than literal representations

STYLE:
- Modern, professional aesthetic
- Colorblind-friendly colors
- Bold but restrained imagery
- Suitable for scientific/professional presentations
- Corporate/academic level of polish
"""
    
    def __init__(self, api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize the generator.
        
        Args:
            api_key: OpenRouter API key (or use OPENROUTER_API_KEY env var)
            verbose: Print detailed progress information
        """
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
        self._last_error = None
        self.base_url = "https://openrouter.ai/api/v1"
        # Nano Banana Pro for image generation. The slug must be an image-output
        # model; a text-only chat model is rejected with "No endpoints found that
        # support the requested output modalities".
        # https://openrouter.ai/google/gemini-3.1-flash-image
        self.image_model = "google/gemini-3.1-flash-image"
        # Gemini 3.6 Flash for quality review - reads the image, answers in text
        self.review_model = "google/gemini-3.7-flash"
        
    def _log(self, message: str):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def _make_request(self, model: str, messages: List[Dict[str, Any]], 
                     modalities: Optional[List[str]] = None) -> Dict[str, Any]:
        """Make a request to OpenRouter API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/scientific-writer",
            "X-Title": "Scientific Slide Generator"
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
            
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                response_json = {"raw_text": response.text[:500]}
            
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
        """Extract base64-encoded image from API response."""
        try:
            choices = response.get("choices", [])
            if not choices:
                self._log("No choices in response")
                return None
            
            message = choices[0].get("message", {})
            
            # Nano Banana Pro returns images in the 'images' field
            images = message.get("images", [])
            if images and len(images) > 0:
                self._log(f"Found {len(images)} image(s) in 'images' field")
                
                first_image = images[0]
                if isinstance(first_image, dict):
                    if first_image.get("type") == "image_url":
                        url = first_image.get("image_url", {})
                        if isinstance(url, dict):
                            url = url.get("url", "")
                        
                        if url and url.startswith("data:image"):
                            if "," in url:
                                base64_str = url.split(",", 1)[1]
                                base64_str = base64_str.replace('\n', '').replace('\r', '').replace(' ', '')
                                self._log(f"Extracted base64 data (length: {len(base64_str)})")
                                return base64.b64decode(base64_str)
            
            # Fallback: check content field
            content = message.get("content", "")
            
            if isinstance(content, str) and "data:image" in content:
                import re
                match = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=\n\r]+)', content, re.DOTALL)
                if match:
                    base64_str = match.group(1).replace('\n', '').replace('\r', '').replace(' ', '')
                    self._log(f"Found image in content field (length: {len(base64_str)})")
                    return base64.b64decode(base64_str)
            
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
            return None
    
    def _image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 data URL."""
        with open(image_path, "rb") as f:
            image_data = f.read()
        
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
    
    def generate_image(self, prompt: str, attachments: Optional[List[str]] = None) -> Optional[bytes]:
        """
        Generate an image using Nano Banana Pro.
        
        Args:
            prompt: Text description of the image to generate
            attachments: Optional list of image file paths to attach as context
            
        Returns:
            Image bytes or None if generation failed
        """
        self._last_error = None
        
        # Build content with text and optional image attachments
        content = []
        
        # Add text prompt
        content.append({
            "type": "text",
            "text": prompt
        })
        
        # Add attached images as context
        if attachments:
            for img_path in attachments:
                try:
                    img_data_url = self._image_to_base64(img_path)
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img_data_url}
                    })
                    self._log(f"Attached image: {img_path}")
                except Exception as e:
                    self._log(f"Warning: Could not attach {img_path}: {e}")
        
        messages = [
            {
                "role": "user",
                "content": content if attachments else prompt
            }
        ]
        
        try:
            response = self._make_request(
                model=self.image_model,
                messages=messages,
                modalities=["image", "text"]
            )
            
            if self.verbose:
                self._log(f"Response keys: {response.keys()}")
                if "error" in response:
                    self._log(f"API Error: {response['error']}")
            
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
                self._last_error = "No image data in API response"
                self._log(f"✗ {self._last_error}")
            
            return image_data
        except RuntimeError as e:
            self._last_error = str(e)
            self._log(f"✗ Generation failed: {self._last_error}")
            return None
        except Exception as e:
            self._last_error = f"Unexpected error: {str(e)}"
            self._log(f"✗ Generation failed: {self._last_error}")
            return None
    
    def review_image(self, image_path: str, original_prompt: str, 
                    iteration: int, visual_only: bool = False,
                    max_iterations: int = 2) -> ReviewResult:
        """Review generated image using Gemini 3.6 Flash."""
        image_data_url = self._image_to_base64(image_path)
        threshold = self.QUALITY_THRESHOLD
        
        image_type = "slide visual/figure" if visual_only else "presentation slide"
        
        review_prompt = f"""You are an expert reviewer evaluating a {image_type} for presentation quality.

ORIGINAL REQUEST: {original_prompt}

QUALITY THRESHOLD: {threshold}/10
ITERATION: {iteration}/{max_iterations}

Evaluate this {image_type} on these criteria:

1. **Visual Impact** (0-2 points)
   - Bold, attention-grabbing design
   - Professional appearance
   - Suitable for projection

2. **Clarity** (0-2 points)
   - Easy to understand at a glance
   - Clear visual hierarchy
   - Not cluttered or busy

3. **Readability** (0-2 points)
   - Text is large and readable (if present)
   - High contrast
   - Clean typography

4. **Composition** (0-2 points)
   - Balanced layout
   - Good use of space
   - Appropriate margins

5. **Relevance** (0-2 points)
   - Matches the requested content
   - Appropriate style for presentations
   - Professional quality

RESPOND IN THIS EXACT FORMAT:
SCORE: [total score 0-10]

STRENGTHS:
- [strength 1]
- [strength 2]

ISSUES:
- [issue 1 if any]
- [issue 2 if any]

VERDICT: [ACCEPTABLE or NEEDS_IMPROVEMENT]

If score >= {threshold}, the image is ACCEPTABLE.
If score < {threshold}, mark as NEEDS_IMPROVEMENT with specific suggestions."""

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": review_prompt},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
            }
        ]
        
        try:
            response = self._make_request(model=self.review_model, messages=messages)
            
            choices = response.get("choices", [])
            if not choices:
                # A normal enough outcome -- a rate limit, a content filter, a
                # provider hiccup. The image itself is fine; only its review is
                # missing, and saying so beats inventing a score.
                reason = "the review model returned no choices"
                self._log(f"⚠ Review unavailable: {reason}")
                return ReviewResult(
                    f"Review unavailable: {reason}.",
                    None, False, reviewed=False, error=reason,
                )

            message = choices[0].get("message", {})
            content = message.get("content", "")

            reasoning = message.get("reasoning", "")
            if reasoning and not content:
                content = reasoning

            if isinstance(content, list):
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

            return ReviewResult(
                content if content else "Review returned no text",
                score,
                needs_improvement,
                reviewed=True,
                error=None if score is not None else "no score found in the review",
            )
        except Exception as e:
            # A failed review must not fail the run -- the image is already
            # generated -- but it must not read as a pass either.
            self._log(f"⚠ Review failed: {str(e)}")
            return ReviewResult(
                f"Review failed: {str(e)}",
                None, False, reviewed=False, error=str(e),
            )
    
    def improve_prompt(self, original_prompt: str, critique: str, 
                      iteration: int, visual_only: bool = False) -> str:
        """Improve the generation prompt based on critique."""
        guidelines = self.VISUAL_ONLY_GUIDELINES if visual_only else self.FULL_SLIDE_GUIDELINES
        
        return f"""{guidelines}

USER REQUEST: {original_prompt}

ITERATION {iteration}: Based on previous feedback, address these specific improvements:
{critique}

Generate an improved version that addresses all the critique points."""
    
    def generate_slide(self, user_prompt: str, output_path: str,
                      visual_only: bool = False,
                      iterations: int = 2,
                      attachments: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a slide image or visual with iterative refinement.
        
        Args:
            user_prompt: Description of the slide/visual to generate
            output_path: Path to save final image
            visual_only: If True, generate just the visual (for PPT workflow)
            iterations: Maximum refinement iterations (default: 2)
            attachments: Optional list of image file paths to attach as context
            
        Returns:
            Dictionary with generation results and metadata
        """
        output_path = Path(output_path)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        base_name = output_path.stem
        extension = output_path.suffix or ".png"
        
        mode = "visual_only" if visual_only else "full_slide"
        guidelines = self.VISUAL_ONLY_GUIDELINES if visual_only else self.FULL_SLIDE_GUIDELINES
        
        results = {
            "user_prompt": user_prompt,
            "mode": mode,
            "quality_threshold": self.QUALITY_THRESHOLD,
            "attachments": attachments or [],
            "iterations": [],
            "final_image": None,
            # None, not 0.0 -- a run whose review never completed has no score,
            # and a number here would be read as one the reviewer gave.
            "final_score": None,
            "final_reviewed": False,
            "success": False,
            "early_stop": False
        }
        
        current_prompt = f"""{guidelines}

USER REQUEST: {user_prompt}

Generate a high-quality {'visual/figure' if visual_only else 'presentation slide'} that meets all the guidelines above."""
        
        print(f"\n{'='*60}")
        print(f"Generating Slide {'Visual' if visual_only else 'Image'}")
        print(f"{'='*60}")
        print(f"Description: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}")
        print(f"Mode: {mode}")
        if attachments:
            print(f"Attachments: {len(attachments)} image(s)")
            for att in attachments:
                print(f"  - {att}")
        print(f"Quality Threshold: {self.QUALITY_THRESHOLD}/10")
        print(f"Max Iterations: {iterations}")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")
        
        # Track temporary files for cleanup
        temp_files = []
        final_image_data = None
        
        for i in range(1, iterations + 1):
            print(f"\n[Iteration {i}/{iterations}]")
            print("-" * 40)
            
            print(f"Generating image with Nano Banana Pro...")
            image_data = self.generate_image(current_prompt, attachments=attachments)
            
            if not image_data:
                error_msg = self._last_error or 'Image generation failed'
                print(f"✗ Generation failed: {error_msg}")
                results["iterations"].append({
                    "iteration": i,
                    "success": False,
                    "error": error_msg
                })
                continue
            
            # Save to temporary file for review (will be cleaned up)
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(suffix=extension)
            os.close(temp_fd)
            temp_path = Path(temp_path)
            temp_files.append(temp_path)
            
            with open(temp_path, "wb") as f:
                f.write(image_data)
            print(f"✓ Generated image (iteration {i})")
            
            print(f"Reviewing image with {self.review_model}...")
            review = self.review_image(
                str(temp_path), user_prompt, i, visual_only, iterations
            )
            if review.score is not None:
                print(f"✓ Score: {review.score}/10 (threshold: {self.QUALITY_THRESHOLD}/10)")
            else:
                print(f"⚠ Review unavailable — image kept, quality not verified")
                print(f"  Reason: {review.error}")

            results["iterations"].append({
                "iteration": i,
                "critique": review.critique,
                "score": review.score,
                "reviewed": review.reviewed,
                "review_error": review.error,
                "needs_improvement": review.needs_improvement,
                "success": True
            })

            if not review.needs_improvement:
                if review.score is not None:
                    print(f"\n✓ Quality meets threshold ({review.score} >= {self.QUALITY_THRESHOLD})")
                else:
                    # Regenerating cannot fix a reviewer that did not answer.
                    print(f"\n⚠ Stopping without a verified score — review the image yourself")
                final_image_data = image_data
                results["final_score"] = review.score
                results["final_reviewed"] = review.reviewed and review.score is not None
                results["success"] = True
                results["early_stop"] = True
                break

            if i == iterations:
                print(f"\n⚠ Maximum iterations reached")
                final_image_data = image_data
                results["final_score"] = review.score
                results["final_reviewed"] = review.reviewed and review.score is not None
                results["success"] = True
                break

            print(f"\n⚠ Quality below threshold ({review.score} < {self.QUALITY_THRESHOLD})")
            print(f"Improving prompt...")
            current_prompt = self.improve_prompt(user_prompt, review.critique, i + 1, visual_only)
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except Exception:
                pass
        
        # Save only the final image to output path
        if results["success"] and final_image_data:
            with open(output_path, "wb") as f:
                f.write(final_image_data)
            results["final_image"] = str(output_path)
            print(f"\n✓ Final image: {output_path}")
        
        print(f"\n{'='*60}")
        print(f"Generation Complete!")
        if results["final_score"] is not None:
            print(f"Final Score: {results['final_score']}/10")
        else:
            print(f"Final Score: unavailable (the review did not produce one)")
        if results["early_stop"]:
            success_count = len([r for r in results['iterations'] if r.get('success')])
            print(f"Iterations Used: {success_count}/{iterations} (early stop)")
        print(f"{'='*60}\n")
        
        return results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Generate presentation slides or visuals using Nano Banana Pro AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a full slide (for PDF workflow)
  python generate_slide_image_ai.py "Title: Machine Learning Basics\\nKey points: supervised learning, neural networks, deep learning" -o slide_01.png
  
  # Generate just a visual/figure (for PPT workflow)
  python generate_slide_image_ai.py "Neural network architecture diagram with input, hidden, and output layers" -o figure.png --visual-only
  
  # With reference images attached (Nano Banana Pro will see these)
  python generate_slide_image_ai.py "Create a slide explaining this chart with key insights" -o slide.png --attach chart.png
  python generate_slide_image_ai.py "Combine these images into a comparison slide" -o compare.png --attach before.png --attach after.png
  
  # With custom iterations
  python generate_slide_image_ai.py "Title slide for AI Conference 2025" -o title.png --iterations 2
  
  # Verbose output
  python generate_slide_image_ai.py "Data flow diagram" -o flow.png -v

Environment:
  OPENROUTER_API_KEY    OpenRouter API key (required)
        """
    )
    
    parser.add_argument("prompt", help="Description of the slide or visual to generate")
    parser.add_argument("-o", "--output", required=True, help="Output image path")
    parser.add_argument("--attach", action="append", dest="attachments", metavar="IMAGE",
                       help="Attach image file(s) as context for generation (can use multiple times)")
    parser.add_argument("--visual-only", action="store_true",
                       help="Generate just the visual/figure (for PPT workflow)")
    parser.add_argument("--iterations", type=int, default=2,
                       help="Maximum refinement iterations (default: 2)")
    parser.add_argument("--api-key", help="OpenRouter API key (or set OPENROUTER_API_KEY)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Resolves --api-key, the environment, then any .env file
    api_key = _resolve_api_key(args.api_key)
    if not api_key:
        print("Error: OPENROUTER_API_KEY not found")
        print("\nSet it with:")
        print("  export OPENROUTER_API_KEY='your_api_key'")
        print("\nOr add OPENROUTER_API_KEY=your_api_key to a .env file")
        print("Or provide via --api-key flag")
        sys.exit(1)
    
    if args.iterations < 1 or args.iterations > 2:
        print("Error: Iterations must be between 1 and 2")
        sys.exit(1)
    
    # Validate attachments exist
    if args.attachments:
        for att in args.attachments:
            if not Path(att).exists():
                print(f"Error: Attachment file not found: {att}")
                sys.exit(1)
    
    try:
        generator = SlideImageGenerator(api_key=api_key, verbose=args.verbose)
        results = generator.generate_slide(
            user_prompt=args.prompt,
            output_path=args.output,
            visual_only=args.visual_only,
            iterations=args.iterations,
            attachments=args.attachments
        )
        
        if results["success"]:
            print(f"\n✓ Success! Image saved to: {args.output}")
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

### `scripts/pdf_to_images.py`

```python
#!/usr/bin/env python3
"""
PDF to Images Converter for Presentations

Converts presentation PDFs to images for visual inspection and review.
Supports multiple output formats and resolutions.

Uses PyMuPDF (fitz) as the primary conversion method - no external
dependencies required (no poppler, ghostscript, or ImageMagick needed).
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List

# Try to import pymupdf (preferred - no external dependencies)
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


class PDFToImagesConverter:
    """Converts PDF presentations to images."""
    
    def __init__(
        self,
        pdf_path: str,
        output_prefix: str,
        dpi: int = 150,
        format: str = 'jpg',
        first_page: Optional[int] = None,
        last_page: Optional[int] = None
    ):
        self.pdf_path = Path(pdf_path)
        self.output_prefix = output_prefix
        self.dpi = dpi
        self.format = format.lower()
        self.first_page = first_page
        self.last_page = last_page
        
        # Validate format
        if self.format not in ['jpg', 'jpeg', 'png']:
            raise ValueError(f"Unsupported format: {format}. Use jpg or png.")
    
    def convert(self) -> List[Path]:
        """Convert PDF to images using PyMuPDF."""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {self.pdf_path}")
        
        print(f"Converting: {self.pdf_path.name}")
        print(f"Output prefix: {self.output_prefix}")
        print(f"DPI: {self.dpi}")
        print(f"Format: {self.format}")
        
        if HAS_PYMUPDF:
            return self._convert_with_pymupdf()
        else:
            raise RuntimeError(
                "PyMuPDF not installed. Install it with:\n"
                "  uv pip install pymupdf\n\n"
                "PyMuPDF is a self-contained library - no external dependencies needed."
            )
    
    def _convert_with_pymupdf(self) -> List[Path]:
        """Convert using PyMuPDF library (no external dependencies)."""
        print("Using PyMuPDF (no external dependencies required)...")
        
        # Open the PDF
        doc = fitz.open(self.pdf_path)
        
        # Determine page range
        start_page = (self.first_page - 1) if self.first_page else 0
        end_page = self.last_page if self.last_page else doc.page_count
        
        # Calculate zoom factor from DPI (72 DPI is the base)
        zoom = self.dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        
        output_files = []
        output_dir = Path(self.output_prefix).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for page_num in range(start_page, end_page):
            page = doc[page_num]
            
            # Render page to pixmap
            pixmap = page.get_pixmap(matrix=matrix)
            
            # Determine output path
            output_path = Path(f"{self.output_prefix}-{page_num + 1:03d}.{self.format}")
            
            # Save the image
            if self.format in ['jpg', 'jpeg']:
                pixmap.save(str(output_path), output="jpeg")
            else:
                pixmap.save(str(output_path), output="png")
            
            output_files.append(output_path)
            print(f"  Created: {output_path.name}")
        
        doc.close()
        return output_files


def main():
    parser = argparse.ArgumentParser(
        description='Convert presentation PDFs to images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s presentation.pdf slides
    → Creates slides-001.jpg, slides-002.jpg, ...
  
  %(prog)s presentation.pdf output/slide --dpi 300 --format png
    → Creates output/slide-001.png, slide-002.png, ... at high resolution
  
  %(prog)s presentation.pdf review/s --first 5 --last 10
    → Converts only slides 5-10

Output:
  Images are named: PREFIX-001.FORMAT, PREFIX-002.FORMAT, etc.
  
Resolution:
  - 150 DPI: Good for screen review (default)
  - 200 DPI: Higher quality for detailed inspection
  - 300 DPI: Print quality (larger files)

Requirements:
  Install PyMuPDF (no external dependencies needed):
    uv pip install pymupdf
        """
    )
    
    parser.add_argument(
        'pdf_path',
        help='Path to PDF presentation'
    )
    
    parser.add_argument(
        'output_prefix',
        help='Output filename prefix (e.g., "slides" or "output/slide")'
    )
    
    parser.add_argument(
        '--dpi', '-r',
        type=int,
        default=150,
        help='Resolution in DPI (default: 150)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['jpg', 'jpeg', 'png'],
        default='jpg',
        help='Output format (default: jpg)'
    )
    
    parser.add_argument(
        '--first',
        type=int,
        help='First page to convert (1-indexed)'
    )
    
    parser.add_argument(
        '--last',
        type=int,
        help='Last page to convert (1-indexed)'
    )
    
    args = parser.parse_args()
    
    # Create output directory if needed
    output_dir = Path(args.output_prefix).parent
    if output_dir != Path('.'):
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Convert
    try:
        converter = PDFToImagesConverter(
            pdf_path=args.pdf_path,
            output_prefix=args.output_prefix,
            dpi=args.dpi,
            format=args.format,
            first_page=args.first,
            last_page=args.last
        )
        
        output_files = converter.convert()
        
        print()
        print("=" * 60)
        print(f"✅ Success! Created {len(output_files)} image(s)")
        print("=" * 60)
        
        if output_files:
            print(f"\nFirst image: {output_files[0]}")
            print(f"Last image: {output_files[-1]}")
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in output_files)
            size_mb = total_size / (1024 * 1024)
            print(f"Total size: {size_mb:.2f} MB")
            
            print("\nNext steps:")
            print("  1. Review images for layout issues")
            print("  2. Check for text overflow or element overlap")
            print("  3. Verify readability from distance")
            print("  4. Document issues with slide numbers")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### `scripts/slides_to_pdf.py`

```python
#!/usr/bin/env python3
"""
Combine slide images into a single PDF presentation.

This script takes multiple slide images (PNG, JPG) and combines them
into a single PDF file, maintaining aspect ratio and quality.

Usage:
    # Combine all PNG files in a directory
    python slides_to_pdf.py slides/*.png -o presentation.pdf
    
    # Combine specific files in order
    python slides_to_pdf.py slide_01.png slide_02.png slide_03.png -o presentation.pdf
    
    # From a directory (sorted by filename)
    python slides_to_pdf.py slides/ -o presentation.pdf
"""

import argparse
import sys
from pathlib import Path
from typing import List

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow library not found. Install with: uv pip install Pillow")
    sys.exit(1)


def get_image_files(paths: List[str]) -> List[Path]:
    """
    Get list of image files from paths (files or directories).
    
    Args:
        paths: List of file paths or directory paths
        
    Returns:
        Sorted list of image file paths
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
    image_files = []
    
    for path_str in paths:
        path = Path(path_str)
        
        if path.is_file():
            if path.suffix.lower() in image_extensions:
                image_files.append(path)
            else:
                print(f"Warning: Skipping non-image file: {path}")
        elif path.is_dir():
            # Get all images in directory
            for ext in image_extensions:
                image_files.extend(path.glob(f"*{ext}"))
                image_files.extend(path.glob(f"*{ext.upper()}"))
        else:
            # Try glob pattern
            parent = path.parent
            pattern = path.name
            if parent.exists():
                matches = list(parent.glob(pattern))
                for match in matches:
                    if match.suffix.lower() in image_extensions:
                        image_files.append(match)
    
    # Remove duplicates and sort
    image_files = list(set(image_files))
    image_files.sort(key=lambda x: x.name)
    
    return image_files


def combine_images_to_pdf(image_paths: List[Path], output_path: Path, 
                         dpi: int = 150, verbose: bool = False) -> bool:
    """
    Combine multiple images into a single PDF.
    
    Args:
        image_paths: List of image file paths
        output_path: Output PDF path
        dpi: Resolution for the PDF (default: 150)
        verbose: Print progress information
        
    Returns:
        True if successful, False otherwise
    """
    if not image_paths:
        print("Error: No image files found")
        return False
    
    if verbose:
        print(f"Combining {len(image_paths)} images into PDF...")
    
    # Load all images
    images = []
    for i, img_path in enumerate(image_paths):
        try:
            img = Image.open(img_path)
            # Convert to RGB if necessary (PDF doesn't support RGBA)
            if img.mode in ('RGBA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            images.append(img)
            
            if verbose:
                print(f"  [{i+1}/{len(image_paths)}] Loaded: {img_path.name} ({img.size[0]}x{img.size[1]})")
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            return False
    
    if not images:
        print("Error: No images could be loaded")
        return False
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save as PDF
    try:
        # First image
        first_image = images[0]
        
        # Remaining images (if any)
        remaining_images = images[1:] if len(images) > 1 else []
        
        # Save to PDF
        first_image.save(
            output_path,
            "PDF",
            resolution=dpi,
            save_all=True,
            append_images=remaining_images
        )
        
        if verbose:
            print(f"\n✓ PDF created: {output_path}")
            print(f"  Total slides: {len(images)}")
            file_size = output_path.stat().st_size
            if file_size > 1024 * 1024:
                print(f"  File size: {file_size / (1024 * 1024):.1f} MB")
            else:
                print(f"  File size: {file_size / 1024:.1f} KB")
        
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False
    finally:
        # Close all images
        for img in images:
            img.close()


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Combine slide images into a single PDF presentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Combine PNG files using glob pattern
  python slides_to_pdf.py slides/*.png -o presentation.pdf
  
  # Combine specific files in order
  python slides_to_pdf.py title.png intro.png methods.png results.png -o talk.pdf
  
  # Combine all images from a directory (sorted by filename)
  python slides_to_pdf.py slides/ -o presentation.pdf
  
  # With custom DPI and verbose output
  python slides_to_pdf.py slides/*.png -o presentation.pdf --dpi 200 -v

Supported formats: PNG, JPG, JPEG, GIF, WEBP, BMP

Tips:
  - Name your slide images with numbers for correct ordering:
    01_title.png, 02_intro.png, 03_methods.png, etc.
  - Use the generate_slide_image.py script to create slides first
  - Standard presentation aspect ratio is 16:9 (1920x1080 or 1280x720)
        """
    )
    
    parser.add_argument("images", nargs="+", 
                       help="Image files, directories, or glob patterns")
    parser.add_argument("-o", "--output", required=True,
                       help="Output PDF file path")
    parser.add_argument("--dpi", type=int, default=150,
                       help="PDF resolution in DPI (default: 150)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Get image files
    image_files = get_image_files(args.images)
    
    if not image_files:
        print("Error: No image files found matching the specified paths")
        print("\nUsage examples:")
        print("  python slides_to_pdf.py slides/*.png -o presentation.pdf")
        print("  python slides_to_pdf.py slide1.png slide2.png -o presentation.pdf")
        sys.exit(1)
    
    print(f"Found {len(image_files)} image(s)")
    if args.verbose:
        for f in image_files:
            print(f"  - {f}")
    
    # Combine into PDF
    output_path = Path(args.output)
    success = combine_images_to_pdf(
        image_files, 
        output_path, 
        dpi=args.dpi, 
        verbose=args.verbose
    )
    
    if success:
        print(f"\n✓ PDF created: {output_path}")
        sys.exit(0)
    else:
        print(f"\n✗ Failed to create PDF")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### `scripts/validate_presentation.py`

```python
#!/usr/bin/env python3
"""
Presentation Validation Script

Validates scientific presentations for common issues:
- Slide count vs. duration
- LaTeX compilation
- File size checks
- Basic format validation
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# PDF page and geometry analysis. pypdf is the maintained continuation of
# PyPDF2 and exposes the same PdfReader API, so accept whichever is installed.
try:
    from pypdf import PdfReader
    HAS_PDF_READER = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        HAS_PDF_READER = True
    except ImportError:
        HAS_PDF_READER = False

# Try to import python-pptx for PowerPoint analysis
try:
    from pptx import Presentation
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False


class PresentationValidator:
    """Validates presentations for common issues."""
    
    # Recommended slide counts by duration (min, recommended, max)
    SLIDE_GUIDELINES = {
        5: (5, 6, 8),
        10: (8, 11, 14),
        15: (13, 16, 20),
        20: (18, 22, 26),
        30: (22, 27, 33),
        45: (32, 40, 50),
        60: (40, 52, 65),
    }
    
    def __init__(self, filepath: str, duration: Optional[int] = None):
        self.filepath = Path(filepath)
        self.duration = duration
        self.file_type = self.filepath.suffix.lower()
        self.issues = []
        self.warnings = []
        self.info = []
        
    def validate(self) -> Dict:
        """Run all validations and return results."""
        print(f"Validating: {self.filepath.name}")
        print(f"File type: {self.file_type}")
        print("=" * 60)
        
        # Check file exists
        if not self.filepath.exists():
            self.issues.append(f"File not found: {self.filepath}")
            return self._format_results()
        
        # File size check
        self._check_file_size()
        
        # Type-specific validation
        if self.file_type == '.pdf':
            self._validate_pdf()
        elif self.file_type in ['.pptx', '.ppt']:
            self._validate_pptx()
        elif self.file_type in ['.tex']:
            self._validate_latex()
        else:
            self.warnings.append(f"Unknown file type: {self.file_type}")
        
        return self._format_results()
    
    def _check_file_size(self):
        """Check if file size is reasonable."""
        size_mb = self.filepath.stat().st_size / (1024 * 1024)
        self.info.append(f"File size: {size_mb:.2f} MB")
        
        if size_mb > 100:
            self.issues.append(
                f"File is very large ({size_mb:.1f} MB). "
                "Consider compressing images."
            )
        elif size_mb > 50:
            self.warnings.append(
                f"File is large ({size_mb:.1f} MB). "
                "May be slow to email or upload."
            )
    
    def _validate_pdf(self):
        """Validate PDF presentation."""
        if not HAS_PDF_READER:
            self.warnings.append(
                "pypdf not installed. Install with: uv pip install pypdf"
            )
            return

        try:
            with open(self.filepath, 'rb') as f:
                reader = PdfReader(f)
                num_pages = len(reader.pages)
                
                self.info.append(f"Number of slides: {num_pages}")
                
                # Check slide count against duration
                if self.duration:
                    self._check_slide_count(num_pages)
                
                # Get page size
                first_page = reader.pages[0]
                media_box = first_page.mediabox
                width = float(media_box.width)
                height = float(media_box.height)
                
                # Convert points to inches (72 points = 1 inch)
                width_in = width / 72
                height_in = height / 72
                aspect = width / height
                
                self.info.append(
                    f"Slide dimensions: {width_in:.1f}\" × {height_in:.1f}\" "
                    f"(aspect ratio: {aspect:.2f})"
                )
                
                # Check common aspect ratios
                if abs(aspect - 16/9) < 0.01:
                    self.info.append("Aspect ratio: 16:9 (widescreen)")
                elif abs(aspect - 4/3) < 0.01:
                    self.info.append("Aspect ratio: 4:3 (standard)")
                else:
                    self.warnings.append(
                        f"Unusual aspect ratio: {aspect:.2f}. "
                        "Confirm this matches venue requirements."
                    )
                
        except Exception as e:
            self.issues.append(f"Error reading PDF: {str(e)}")
    
    def _validate_pptx(self):
        """Validate PowerPoint presentation."""
        if not HAS_PPTX:
            self.warnings.append(
                "python-pptx not installed. Install with: uv pip install python-pptx"
            )
            return
        
        try:
            prs = Presentation(self.filepath)
            num_slides = len(prs.slides)
            
            self.info.append(f"Number of slides: {num_slides}")
            
            # Check slide count against duration
            if self.duration:
                self._check_slide_count(num_slides)
            
            # Get slide dimensions
            width_inches = prs.slide_width / 914400  # EMU to inches
            height_inches = prs.slide_height / 914400
            aspect = prs.slide_width / prs.slide_height
            
            self.info.append(
                f"Slide dimensions: {width_inches:.1f}\" × {height_inches:.1f}\" "
                f"(aspect ratio: {aspect:.2f})"
            )
            
            # Check fonts and text
            self._check_pptx_content(prs)
            
        except Exception as e:
            self.issues.append(f"Error reading PowerPoint: {str(e)}")
    
    def _check_pptx_content(self, prs):
        """Check PowerPoint content for common issues."""
        small_text_slides = []
        many_bullets_slides = []
        
        for idx, slide in enumerate(prs.slides, start=1):
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                
                text_frame = shape.text_frame
                
                # Check for small fonts
                for paragraph in text_frame.paragraphs:
                    for run in paragraph.runs:
                        if run.font.size and run.font.size.pt < 18:
                            small_text_slides.append(idx)
                            break
                
                # Check for too many bullets
                bullet_count = sum(1 for p in text_frame.paragraphs if p.level == 0)
                if bullet_count > 6:
                    many_bullets_slides.append(idx)
        
        # Report issues
        if small_text_slides:
            unique_slides = sorted(set(small_text_slides))
            self.warnings.append(
                f"Small text (<18pt) found on slides: {unique_slides[:5]}"
                + (" ..." if len(unique_slides) > 5 else "")
            )
        
        if many_bullets_slides:
            unique_slides = sorted(set(many_bullets_slides))
            self.warnings.append(
                f"Many bullets (>6) on slides: {unique_slides[:5]}"
                + (" ..." if len(unique_slides) > 5 else "")
            )
    
    def _validate_latex(self):
        """Validate LaTeX Beamer presentation."""
        self.info.append("LaTeX source file detected")
        
        # Try to compile
        if self._try_compile_latex():
            self.info.append("LaTeX compilation: SUCCESS")
            
            # If PDF was generated, validate it
            pdf_path = self.filepath.with_suffix('.pdf')
            if pdf_path.exists():
                pdf_validator = PresentationValidator(str(pdf_path), self.duration)
                pdf_results = pdf_validator.validate()
                
                # Merge results
                self.info.extend(pdf_results['info'])
                self.warnings.extend(pdf_results['warnings'])
                self.issues.extend(pdf_results['issues'])
        else:
            self.issues.append(
                "LaTeX compilation failed. Check .log file for errors."
            )
    
    def _try_compile_latex(self) -> bool:
        """Try to compile LaTeX file."""
        try:
            # Try pdflatex
            result = subprocess.run(
                ['pdflatex', '-no-shell-escape', '-interaction=nonstopmode', self.filepath.name],
                cwd=self.filepath.parent,
                capture_output=True,
                timeout=60
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_slide_count(self, num_slides: int):
        """Check if slide count is appropriate for duration."""
        if self.duration not in self.SLIDE_GUIDELINES:
            # Find nearest duration
            durations = sorted(self.SLIDE_GUIDELINES.keys())
            nearest = min(durations, key=lambda x: abs(x - self.duration))
            min_slides, rec_slides, max_slides = self.SLIDE_GUIDELINES[nearest]
            self.info.append(
                f"Using guidelines for {nearest}-minute talk "
                f"(closest to {self.duration} minutes)"
            )
        else:
            min_slides, rec_slides, max_slides = self.SLIDE_GUIDELINES[self.duration]
        
        self.info.append(
            f"Recommended slides for {self.duration}-minute talk: "
            f"{min_slides}-{max_slides} (optimal: ~{rec_slides})"
        )
        
        if num_slides < min_slides:
            self.warnings.append(
                f"Fewer slides ({num_slides}) than recommended ({min_slides}-{max_slides}). "
                "May have too much time or too little content."
            )
        elif num_slides > max_slides:
            self.warnings.append(
                f"More slides ({num_slides}) than recommended ({min_slides}-{max_slides}). "
                "Likely to run over time."
            )
        else:
            self.info.append(
                f"Slide count ({num_slides}) is within recommended range."
            )
    
    def _format_results(self) -> Dict:
        """Format validation results."""
        return {
            'filepath': str(self.filepath),
            'file_type': self.file_type,
            'info': self.info,
            'warnings': self.warnings,
            'issues': self.issues,
            'valid': len(self.issues) == 0
        }


def print_results(results: Dict):
    """Print validation results in a readable format."""
    print()
    print("=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    # Print info
    if results['info']:
        print("\n📋 Information:")
        for item in results['info']:
            print(f"  • {item}")
    
    # Print warnings
    if results['warnings']:
        print("\n⚠️  Warnings:")
        for item in results['warnings']:
            print(f"  • {item}")
    
    # Print issues
    if results['issues']:
        print("\n❌ Issues:")
        for item in results['issues']:
            print(f"  • {item}")
    
    # Overall status
    print("\n" + "=" * 60)
    if results['valid']:
        print("✅ Validation PASSED")
        if results['warnings']:
            print(f"   ({len(results['warnings'])} warning(s) found)")
    else:
        print("❌ Validation FAILED")
        print(f"   ({len(results['issues'])} issue(s) found)")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Validate scientific presentations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s presentation.pdf --duration 15
  %(prog)s slides.pptx --duration 45
  %(prog)s beamer_talk.tex --duration 20

Supported file types:
  - PDF (.pdf)
  - PowerPoint (.pptx, .ppt)
  - LaTeX Beamer (.tex)

Validation checks:
  - Slide count vs. duration
  - File size
  - Slide dimensions
  - Font sizes (PowerPoint)
  - LaTeX compilation (Beamer)
        """
    )
    
    parser.add_argument(
        'filepath',
        help='Path to presentation file (PDF, PPTX, or TEX)'
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=int,
        help='Presentation duration in minutes'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only show issues and warnings'
    )
    
    args = parser.parse_args()
    
    # Validate
    validator = PresentationValidator(args.filepath, args.duration)
    results = validator.validate()
    
    # Print results
    if args.quiet:
        # Only show warnings and issues
        if results['warnings'] or results['issues']:
            print_results(results)
        else:
            print("✅ No issues found")
    else:
        print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if results['valid'] else 1)


if __name__ == '__main__':
    main()
```

### `assets/beamer_template_conference.tex`

```latex
\documentclass[aspectratio=169,11pt]{beamer}

% Encoding
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

% Theme and colors
\usetheme{Madrid}
\usecolortheme{beaver}

% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Page numbers in footer
\setbeamertemplate{footline}[frame number]

% Graphics
\usepackage{graphicx}
\graphicspath{{./figures/}}

% Math
\usepackage{amsmath, amssymb}

% Tables
\usepackage{booktabs}

% Citations
\usepackage[style=authoryear,maxcitenames=2,backend=biber]{biblatex}
\addbibresource{references.bib}
\renewcommand*{\bibfont}{\tiny}

% Colors (customize these)
\definecolor{primaryblue}{RGB}{0,90,156}
\definecolor{secondaryorange}{RGB}{228,108,10}

% Custom colors for theme elements
\setbeamercolor{structure}{fg=primaryblue}
\setbeamercolor{title}{fg=primaryblue}
\setbeamercolor{frametitle}{fg=primaryblue}
\setbeamercolor{block title}{fg=white,bg=primaryblue}

% Title page information
\title[Short Title]{Full Presentation Title:\\Descriptive and Specific}
\subtitle{Optional Subtitle}
\author[Author Name]{Author Name\inst{1}}
\institute[Institution]{
  \inst{1}
  Department of XYZ\\
  University Name\\
  \vspace{0.2cm}
  \texttt{email@university.edu}
}
\date{Conference Name\\Month Day, Year}

% Optional: Logo
% \logo{\includegraphics[height=0.8cm]{logo.png}}

\begin{document}

% Title slide
\begin{frame}[plain]
  \titlepage
\end{frame}

% Outline (optional for conference talks)
% \begin{frame}{Outline}
%   \tableofcontents
% \end{frame}

%==============================================
% INTRODUCTION
%==============================================

\section{Introduction}

\begin{frame}{The Problem}
  \begin{itemize}
    \item<1-> Start with a compelling hook or problem statement
    \item<2-> Establish why this research matters
    \item<3-> Set up the knowledge gap
    \item<4-> Preview your contribution
  \end{itemize}
  
  \vfill
  
  \uncover<4->{
    \begin{block}{Research Question}
      State your specific research question or hypothesis clearly
    \end{block}
  }
\end{frame}

\begin{frame}{Background and Context}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Prior Work:}
      \begin{itemize}
        \item Key finding 1 \cite{reference1}
        \item Key finding 2 \cite{reference2}
        \item Knowledge gap identified
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      % Example figure
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{context_figure.pdf}
        \framebox[0.9\textwidth][c]{[Figure: Context or Prior Work]}
        \caption{Illustration of the problem}
      \end{figure}
    \end{column}
    
  \end{columns}
\end{frame}

%==============================================
% METHODS
%==============================================

\section{Methods}

\begin{frame}{Study Design}
  \begin{columns}[T]
    
    \begin{column}{0.6\textwidth}
      \textbf{Approach:}
      \begin{itemize}
        \item Study type/design
        \item Participants/sample (n = X)
        \item Key procedures
        \item Analysis strategy
      \end{itemize}
      
      \vspace{0.5cm}
      
      \begin{alertblock}{Key Innovation}
        Highlight what makes your approach novel or improved
      \end{alertblock}
    \end{column}
    
    \begin{column}{0.4\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{methods_schematic.pdf}
        \framebox[0.9\textwidth][c]{[Methods Diagram]}
        \caption{Experimental design}
      \end{figure}
    \end{column}
    
  \end{columns}
\end{frame}

\begin{frame}{Analysis Overview}
  \begin{itemize}
    \item \textbf{Primary outcome:} What you measured
    \item \textbf{Statistical approach:} Tests used
    \item \textbf{Sample size justification:} Power analysis (if applicable)
    \item \textbf{Software:} Tools and versions used
  \end{itemize}
  
  \vspace{0.5cm}
  
  % Optional: Show key equation
  \begin{exampleblock}{Key Model}
    \begin{equation}
      Y = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \epsilon
    \end{equation}
  \end{exampleblock}
\end{frame}

%==============================================
% RESULTS
%==============================================

\section{Results}

\begin{frame}{Main Finding 1}
  \begin{figure}
    \centering
    % \includegraphics[width=0.85\textwidth]{result1.pdf}
    \framebox[0.8\textwidth][c]{[Figure: Main Result 1]}
    \caption{Primary outcome showing significant effect ($p < 0.001$)}
  \end{figure}
  
  \vspace{0.3cm}
  
  \begin{itemize}
    \item<2-> Key observation: Description of pattern
    \item<3-> Statistical result: Effect size and significance
    \item<4-> Interpretation: What this means
  \end{itemize}
\end{frame}

\begin{frame}{Main Finding 2}
  \begin{columns}[c]
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{result2a.pdf}
        \framebox[0.9\textwidth][c]{[Result 2A]}
        \caption{Condition A}
      \end{figure}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{result2b.pdf}
        \framebox[0.9\textwidth][c]{[Result 2B]}
        \caption{Condition B}
      \end{figure}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \begin{itemize}
    \item Comparison shows: Key difference
    \item Statistical test: $t(50) = 3.4, p = 0.001$
  \end{itemize}
\end{frame}

\begin{frame}{Supporting Evidence}
  \begin{table}
    \centering
    \caption{Summary of key results across conditions}
    \begin{tabular}{lccc}
      \toprule
      \textbf{Condition} & \textbf{Metric 1} & \textbf{Metric 2} & \textbf{$p$-value} \\
      \midrule
      Control    & 45.2 $\pm$ 3.1 & 0.65 & --- \\
      Treatment  & 67.8 $\pm$ 2.9 & 0.82 & $< 0.001$ \\
      \bottomrule
    \end{tabular}
  \end{table}
  
  \vspace{0.5cm}
  
  \begin{itemize}
    \item Consistent pattern across multiple metrics
    \item Effect robust to various controls
  \end{itemize}
\end{frame}

%==============================================
% DISCUSSION
%==============================================

\section{Discussion}

\begin{frame}{Interpretation}
  \textbf{Key Findings:}
  \begin{enumerate}
    \item First main result and its significance
    \item Second main result and its implications
    \item Supporting evidence strengthens conclusions
  \end{enumerate}
  
  \vspace{0.5cm}
  
  \textbf{Relation to Prior Work:}
  \begin{itemize}
    \item Consistent with \cite{reference1}
    \item Extends beyond \cite{reference2}
    \item Resolves controversy from \cite{reference3}
  \end{itemize}
\end{frame}

\begin{frame}{Implications and Impact}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Scientific Impact:}
      \begin{itemize}
        \item Advances understanding of X
        \item Provides new framework for Y
        \item Opens avenue for Z research
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \textbf{Practical Applications:}
      \begin{itemize}
        \item Clinical relevance
        \item Policy implications
        \item Technological applications
      \end{itemize}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \begin{block}{Limitations}
    \begin{itemize}
      \item Acknowledge key limitation 1
      \item Note limitation 2 and how future work addresses it
    \end{itemize}
  \end{block}
\end{frame}

%==============================================
% CONCLUSION
%==============================================

\section{Conclusion}

\begin{frame}{Conclusions}
  \begin{block}{Key Takeaways}
    \begin{enumerate}
      \item \textbf{First main finding:} Brief statement
      \item \textbf{Second main finding:} Brief statement
      \item \textbf{Broader impact:} Significance for field
    \end{enumerate}
  \end{block}
  
  \vspace{0.5cm}
  
  \textbf{Future Directions:}
  \begin{itemize}
    \item Extend to population/context Y
    \item Investigate mechanism Z
    \item Collaborate with domain X
  \end{itemize}
\end{frame}

\begin{frame}[plain]
  \begin{center}
    {\Large \textbf{Thank You}}
    
    \vspace{1cm}
    
    {\large Questions?}
    
    \vspace{1cm}
    
    \begin{columns}
      \begin{column}{0.5\textwidth}
        \textbf{Contact:}\\
        Author Name\\
        \texttt{email@university.edu}\\
        \url{https://yourwebsite.edu}
      \end{column}
      
      \begin{column}{0.5\textwidth}
        % Optional: QR code to paper or website
        % \includegraphics[width=3cm]{qrcode.png}\\
        % {\small Scan for paper/code}
      \end{column}
    \end{columns}
    
    \vspace{0.5cm}
    
    {\footnotesize
      Funding: Grant Agency Award \#12345\\
      Collaborators: Colleague 1, Colleague 2
    }
  \end{center}
\end{frame}

%==============================================
% BACKUP SLIDES
%==============================================

\appendix

\begin{frame}{Backup: Additional Data}
  \begin{figure}
    \centering
    % \includegraphics[width=0.7\textwidth]{supplementary_figure.pdf}
    \framebox[0.6\textwidth][c]{[Supplementary Analysis]}
    \caption{Additional analysis for questions}
  \end{figure}
\end{frame}

\begin{frame}{Backup: Methodological Details}
  \textbf{Detailed Procedure:}
  \begin{itemize}
    \item Step-by-step protocol details
    \item Equipment specifications
    \item Parameter settings
    \item Quality control measures
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Alternative Analyses:}
  \begin{itemize}
    \item Sensitivity analysis results
    \item Different statistical approaches
    \item Subgroup analyses
  \end{itemize}
\end{frame}

%==============================================
% REFERENCES
%==============================================

\begin{frame}[allowframebreaks]{References}
  \printbibliography
\end{frame}

\end{document}
```

### `assets/beamer_template_defense.tex`

```latex
\documentclass[aspectratio=169,12pt]{beamer}

% Encoding
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

% Theme - professional and formal for defense
\usetheme{Boadilla}
\usecolortheme{whale}

% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Page numbers with total
\setbeamertemplate{footline}{
  \leavevmode%
  \hbox{%
  \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{author in head/foot}%
    \usebeamerfont{author in head/foot}\insertshortauthor
  \end{beamercolorbox}%
  \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,center]{title in head/foot}%
    \usebeamerfont{title in head/foot}\insertshorttitle
  \end{beamercolorbox}%
  \begin{beamercolorbox}[wd=.333333\paperwidth,ht=2.25ex,dp=1ex,right]{date in head/foot}%
    \usebeamerfont{date in head/foot}\insertshortdate{}\hspace*{2em}
    \insertframenumber{} / \inserttotalframenumber\hspace*{2ex}
  \end{beamercolorbox}}%
  \vskip0pt%
}

% Section pages
\AtBeginSection[]{
  \begin{frame}
    \vfill
    \centering
    \begin{beamercolorbox}[sep=8pt,center,shadow=true,rounded=true]{title}
      \usebeamerfont{title}\insertsectionhead\par%
    \end{beamercolorbox}
    \vfill
  \end{frame}
}

% Graphics
\usepackage{graphicx}
\graphicspath{{./figures/}}

% Math
\usepackage{amsmath, amssymb, amsthm}

% Tables
\usepackage{booktabs}
\usepackage{multirow}

% Citations
\usepackage[style=authoryear,maxcitenames=2,backend=biber]{biblatex}
\addbibresource{references.bib}
\renewcommand*{\bibfont}{\scriptsize}

% Custom colors - conservative for formal defense
\definecolor{universityblue}{RGB}{0,60,113}
\definecolor{accentgold}{RGB}{179,136,12}

\setbeamercolor{structure}{fg=universityblue}
\setbeamercolor{title}{fg=universityblue}
\setbeamercolor{frametitle}{fg=universityblue}
\setbeamercolor{block title}{fg=white,bg=universityblue}

% Title page information
\title[Dissertation Defense]{Title of Your Dissertation:\\Comprehensive and Descriptive}
\subtitle{Dissertation Defense}
\author[Your Name]{Your Name, M.S.\\
  \vspace{0.3cm}
  Doctoral Candidate\\
  Department of Your Field}
\institute[University]{
  University Name\\
  \vspace{0.3cm}
  \textbf{Dissertation Committee:}\\
  Prof. Advisor Name (Chair)\\
  Prof. Committee Member 2\\
  Prof. Committee Member 3\\
  Prof. Committee Member 4\\
  Prof. External Member
}
\date{\today}

% University logo
% \logo{\includegraphics[height=0.8cm]{university_logo.png}}

\begin{document}

% Title slide
\begin{frame}[plain]
  \titlepage
\end{frame}

% Committee and acknowledgments
\begin{frame}{Dissertation Committee}
  \begin{center}
    \textbf{Committee Chair:}\\
    Prof. Advisor Name, PhD\\
    Department of Your Field
    
    \vspace{0.5cm}
    
    \textbf{Committee Members:}\\
    Prof. Member 2, PhD -- Department of Related Field\\
    Prof. Member 3, PhD -- Department of Your Field\\
    Prof. Member 4, PhD -- Department of Statistics\\
    Prof. External Member, PhD -- External Institution
    
    \vspace{0.8cm}
    
    \textit{Thank you to my committee for your guidance, support, and invaluable feedback throughout this dissertation research.}
  \end{center}
\end{frame}

% Overview
\begin{frame}{Dissertation Overview}
  \begin{exampleblock}{Central Thesis}
    Brief statement of the overarching thesis or argument that ties together all dissertation studies.
  \end{exampleblock}
  
  \vspace{0.5cm}
  
  \textbf{Dissertation Structure:}
  \begin{itemize}
    \item \textbf{Chapter 1:} Introduction and theoretical framework
    \item \textbf{Chapter 2:} Study 1 -- [Brief description]
    \item \textbf{Chapter 3:} Study 2 -- [Brief description]
    \item \textbf{Chapter 4:} Study 3 -- [Brief description]
    \item \textbf{Chapter 5:} General discussion and conclusions
  \end{itemize}
\end{frame}

\begin{frame}{Outline}
  \tableofcontents
\end{frame}

%==============================================
% CHAPTER 1: INTRODUCTION
%==============================================

\section{Chapter 1: Introduction and Background}

\begin{frame}{The Problem}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Real-World Significance:}
      \begin{itemize}
        \item Prevalence: X affects Y million people
        \item Impact: Costs \$Z billion annually
        \item Need: Current solutions inadequate
        \item Opportunity: New approach needed
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{problem_figure.pdf}
        \framebox[0.9\textwidth][c]{[Problem Illustration]}
        \caption{Visualization of the problem}
      \end{figure}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \begin{alertblock}{Central Question}
    How can we understand and address this critical challenge using novel theoretical framework X?
  \end{alertblock}
\end{frame}

\subsection{Theoretical Framework}

\begin{frame}{Theoretical Background}
  \textbf{Historical Development:}
  \begin{itemize}
    \item \textbf{Early theories (1950s-1980s):} Established foundational concepts \cite{foundational1975}
    \item \textbf{Modern frameworks (1990s-2000s):} Refined understanding \cite{refinement2000}
    \item \textbf{Recent advances (2010s-present):} Novel approaches emerge \cite{recent2018}
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Key Theoretical Constructs:}
  \begin{enumerate}
    \item \textbf{Construct A:} Describes mechanism X
    \item \textbf{Construct B:} Explains process Y
    \item \textbf{Construct C:} Predicts outcome Z
  \end{enumerate}
  
  \vspace{0.5cm}
  
  \begin{block}{Theoretical Gap}
    Existing theories fail to account for interaction between A and B under conditions C
  \end{block}
\end{frame}

\begin{frame}{Literature Review: What We Know}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Established Findings:}
      \begin{itemize}
        \item Finding 1: Well-replicated
        \item Finding 2: Meta-analytically supported
        \item Finding 3: Cross-culturally validated
        \item Finding 4: Mechanism partially understood
      \end{itemize}
      
      \vspace{0.3cm}
      
      \textbf{Methodological Advances:}
      \begin{itemize}
        \item Technique A: Improved measurement
        \item Technique B: Better controls
        \item Technique C: Novel analysis
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \textbf{Remaining Questions:}
      \begin{itemize}
        \item[\alert{?}] How does A interact with B?
        \item[\alert{?}] What role does C play?
        \item[\alert{?}] Does effect generalize to D?
        \item[\alert{?}] What are boundary conditions?
      \end{itemize}
      
      \vspace{0.3cm}
      
      \begin{exampleblock}{Dissertation Focus}
        This dissertation addresses these gaps through three complementary studies
      \end{exampleblock}
    \end{column}
    
  \end{columns}
\end{frame}

\subsection{Dissertation Aims}

\begin{frame}{Overarching Goals and Specific Aims}
  \begin{block}{Overall Dissertation Goal}
    To develop and test a comprehensive framework for understanding how X influences Y through mechanisms A, B, and C across contexts.
  \end{block}
  
  \vspace{0.5cm}
  
  \textbf{Specific Aims:}
  
  \begin{enumerate}
    \item \textbf{Study 1:} Establish relationship between X and Y
    \begin{itemize}
      \item Method: Cross-sectional survey (n = 500)
      \item Goal: Characterize X→Y relationship
    \end{itemize}
    
    \item \textbf{Study 2:} Identify mediating mechanisms A and B
    \begin{itemize}
      \item Method: Longitudinal study (n = 250, 3 waves)
      \item Goal: Test mediation and temporal precedence
    \end{itemize}
    
    \item \textbf{Study 3:} Test causal model and generalizability
    \begin{itemize}
      \item Method: Experimental manipulation (n = 180)
      \item Goal: Establish causality and boundary conditions
    \end{itemize}
  \end{enumerate}
\end{frame}

%==============================================
% CHAPTER 2: STUDY 1
%==============================================

\section{Chapter 2: Study 1}

\begin{frame}{Study 1: Overview}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Research Question:}\\
      Does X predict Y, and is this relationship moderated by individual difference Z?
      
      \vspace{0.5cm}
      
      \textbf{Hypotheses:}
      \begin{enumerate}
        \item H1: X positively predicts Y
        \item H2: Z moderates X→Y
        \item H3: Effect varies by demographic factors
      \end{enumerate}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \textbf{Design:}
      \begin{itemize}
        \item Cross-sectional survey
        \item N = 500 participants
        \item Online recruitment
        \item Power: .95 for medium effects
      \end{itemize}
      
      \vspace{0.3cm}
      
      \textbf{Measures:}
      \begin{itemize}
        \item X: Validated scale (α = .89)
        \item Y: Performance measure
        \item Z: Individual difference
        \item Controls: Demographics
      \end{itemize}
    \end{column}
    
  \end{columns}
\end{frame}

\begin{frame}{Study 1: Methods}
  \textbf{Participants:}
  \begin{itemize}
    \item N = 500 (62\% female; Age: $M = 34.2$, $SD = 11.5$)
    \item Recruited via university participant pool and online platforms
    \item Inclusion: Ages 18-65, fluent in English
    \item Exclusion: Prior participation in related studies
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Procedure:}
  \begin{enumerate}
    \item Informed consent and demographics
    \item Battery of questionnaires (45 minutes)
    \item Debriefing and compensation
  \end{enumerate}
  
  \vspace{0.5cm}
  
  \textbf{Analysis:}
  \begin{itemize}
    \item Hierarchical regression for H1 and H2
    \item Moderation analysis using PROCESS macro
    \item Subgroup analyses for H3
  \end{itemize}
\end{frame}

\begin{frame}{Study 1: Results}
  \begin{columns}[c]
    
    \begin{column}{0.6\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{study1_main_result.pdf}
        \framebox[0.9\textwidth][c]{[Study 1: Main Result]}
        \caption{X predicts Y ($\beta = 0.47$, $p < .001$, $R^2 = .22$)}
      \end{figure}
    \end{column}
    
    \begin{column}{0.4\textwidth}
      \textbf{Key Findings:}
      \begin{itemize}
        \item H1 supported: Strong X→Y relationship
        \item H2 supported: Z moderates effect
        \item H3 partially supported: Age effects found
      \end{itemize}
      
      \vspace{0.5cm}
      
      \begin{block}{Conclusion}
        Study 1 establishes foundational X→Y relationship
      \end{block}
    \end{column}
    
  \end{columns}
\end{frame}

%==============================================
% CHAPTER 3: STUDY 2
%==============================================

\section{Chapter 3: Study 2}

\begin{frame}{Study 2: Overview}
  \begin{exampleblock}{Research Question}
    What mechanisms (A and B) mediate the X→Y relationship, and what is the temporal ordering?
  \end{exampleblock}
  
  \vspace{0.5cm}
  
  \textbf{Rationale:}
  \begin{itemize}
    \item Study 1 showed X→Y relationship exists
    \item Need to identify mediating processes
    \item Longitudinal design establishes temporal precedence
    \item Tests proposed theoretical model
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Design:}
  \begin{itemize}
    \item Three-wave longitudinal study
    \item N = 250, assessments 6 months apart
    \item Measures: X (T1), A and B (T2), Y (T3)
    \item Analysis: Cross-lagged panel model, mediation
  \end{itemize}
\end{frame}

\begin{frame}{Study 2: Methods}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Sample:}
      \begin{itemize}
        \item N = 250 at baseline
        \item Retention: 88\% at T2, 82\% at T3
        \item Age: $M = 36.4$, $SD = 12.1$
        \item 58\% female, diverse sample
      \end{itemize}
      
      \vspace{0.5cm}
      
      \textbf{Timeline:}
      \begin{itemize}
        \item T1 (baseline): X measured
        \item T2 (+6 months): A, B measured
        \item T3 (+12 months): Y measured
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{study2_design.pdf}
        \framebox[0.9\textwidth][c]{[Longitudinal Design]}
        \caption{Three-wave design with proposed mediation model}
      \end{figure}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \textbf{Analysis:}
  \begin{itemize}
    \item Structural equation modeling for mediation
    \item Cross-lagged panel model for temporal precedence
    \item Missing data handled via FIML
  \end{itemize}
\end{frame}

\begin{frame}{Study 2: Results}
  \begin{figure}
    \centering
    % \includegraphics[width=0.8\textwidth]{study2_mediation.pdf}
    \framebox[0.75\textwidth][c]{[Mediation Model with Path Coefficients]}
    \caption{Serial mediation: X → A → B → Y}
  \end{figure}
  
  \vspace{0.5cm}
  
  \textbf{Path Coefficients:}
  \begin{itemize}
    \item X → A: $\beta = 0.42$, $p < .001$
    \item A → B: $\beta = 0.35$, $p < .001$
    \item B → Y: $\beta = 0.38$, $p < .001$
    \item X → Y (direct): $\beta = 0.18$, $p = .032$
    \item Indirect effect: $\beta = 0.29$, 95\% CI [0.19, 0.41]
  \end{itemize}
  
  \alert{61\% of total effect mediated by A→B pathway}
\end{frame}

%==============================================
% CHAPTER 4: STUDY 3
%==============================================

\section{Chapter 4: Study 3}

\begin{frame}{Study 3: Overview}
  \begin{alertblock}{Research Question}
    Can we establish causality by experimentally manipulating X, and does the effect generalize across contexts?
  \end{alertblock}
  
  \vspace{0.5cm}
  
  \textbf{Motivation:}
  \begin{itemize}
    \item Studies 1-2 showed correlational evidence
    \item Need experimental test for causality
    \item Test generalizability to applied context
    \item Examine boundary conditions
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Design:}
  \begin{itemize}
    \item 2 (X: low vs. high) × 2 (Context: lab vs. field) factorial
    \item N = 180 (45 per condition)
    \item Random assignment to conditions
    \item Outcome: Y measured post-manipulation
  \end{itemize}
\end{frame}

\begin{frame}{Study 3: Methods}
  \textbf{Experimental Manipulation:}
  \begin{itemize}
    \item \textbf{Low X condition:} Control procedure
    \item \textbf{High X condition:} Experimental manipulation designed to increase X
    \item Manipulation check: Successful ($t(178) = 8.92$, $p < .001$, $d = 1.34$)
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Contexts:}
  \begin{itemize}
    \item \textbf{Lab context:} Controlled laboratory setting (original)
    \item \textbf{Field context:} Applied real-world setting (generalization test)
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Measures:}
  \begin{itemize}
    \item Primary outcome Y (same as Studies 1-2)
    \item Mediators A and B
    \item Moderator Z
    \item Potential confounds
  \end{itemize}
\end{frame}

\begin{frame}{Study 3: Results}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{study3_results.pdf}
        \framebox[0.9\textwidth][c]{[Experimental Results]}
        \caption{Main effect of X on Y}
      \end{figure}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \textbf{ANOVA Results:}
      \begin{itemize}
        \item Main effect of X: $F(1,176) = 45.2$, $p < .001$, $\eta^2_p = .20$
        \item Main effect of Context: $F(1,176) = 2.1$, $p = .15$
        \item X × Context: $F(1,176) = 0.8$, $p = .38$
      \end{itemize}
      
      \vspace{0.5cm}
      
      \begin{block}{Key Finding}
        Causal effect of X on Y confirmed; generalizes across contexts
      \end{block}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \textbf{Mediation:} Experimental mediation analysis confirmed A and B as mechanisms
\end{frame}

%==============================================
% CHAPTER 5: GENERAL DISCUSSION
%==============================================

\section{Chapter 5: General Discussion}

\begin{frame}{Synthesis Across Studies}
  \begin{table}
    \centering
    \caption{Summary of findings across three studies}
    \small
    \begin{tabular}{lccc}
      \toprule
      \textbf{Finding} & \textbf{Study 1} & \textbf{Study 2} & \textbf{Study 3} \\
      \midrule
      X → Y relationship & Yes & Yes & Yes (causal) \\
      Mediation by A & --- & Yes & Yes \\
      Mediation by B & --- & Yes & Yes \\
      Moderation by Z & Yes & Yes & Yes \\
      Generalization & --- & --- & Yes \\
      \bottomrule
    \end{tabular}
  \end{table}
  
  \vspace{0.5cm}
  
  \textbf{Convergent Evidence:}
  \begin{itemize}
    \item Robust X→Y relationship across designs and samples
    \item Consistent mediation by A→B pathway
    \item Moderation by Z replicated
    \item Effects generalize from lab to field
  \end{itemize}
\end{frame}

\begin{frame}{Theoretical Contributions}
  \begin{exampleblock}{Novel Theoretical Framework}
    This dissertation proposes and validates the XYZ Model, which integrates constructs A, B, and C to explain how X influences Y.
  \end{exampleblock}
  
  \vspace{0.5cm}
  
  \textbf{Specific Contributions:}
  \begin{enumerate}
    \item \textbf{Integration:} Bridges previously separate literatures on A and B
    \item \textbf{Mechanism:} Identifies A→B as key mediating pathway
    \item \textbf{Boundary conditions:} Specifies role of moderator Z
    \item \textbf{Generalizability:} Shows effects across contexts
    \item \textbf{Causality:} Establishes X as causal factor
  \end{enumerate}
  
  \vspace{0.5cm}
  
  \textbf{Advances Beyond Prior Work:}
  \begin{itemize}
    \item More comprehensive than Theory 1 \cite{theory1}
    \item Resolves contradictions between Studies A and B
    \item Provides testable predictions for future research
  \end{itemize}
\end{frame}

\begin{frame}{Practical Implications}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Clinical Applications:}
      \begin{itemize}
        \item Assessment: Screen for X
        \item Intervention target: Increase A and B
        \item Tailoring: Consider moderator Z
        \item Outcome: Expect improvement in Y
      \end{itemize}
      
      \vspace{0.5cm}
      
      \textbf{Implementation:}
      \begin{itemize}
        \item Feasibility demonstrated in field study
        \item Scalable to larger populations
        \item Cost-effective approach
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \textbf{Policy Recommendations:}
      \begin{enumerate}
        \item Support programs targeting X
        \item Fund interventions enhancing A
        \item Consider individual differences Z
        \item Monitor outcomes Y
      \end{enumerate}
      
      \vspace{0.5cm}
      
      \begin{alertblock}{Impact}
        Findings suggest potential to improve outcomes for population experiencing low X
      \end{alertblock}
    \end{column}
    
  \end{columns}
\end{frame}

\begin{frame}{Limitations and Future Directions}
  \textbf{Study Limitations:}
  \begin{enumerate}
    \item \textbf{Sample:} Primarily university-educated, young adults
    \begin{itemize}
      \item Future: Community samples, diverse populations
    \end{itemize}
    
    \item \textbf{Measures:} Some reliance on self-report
    \begin{itemize}
      \item Future: Multi-method assessment (behavioral, biological)
    \end{itemize}
    
    \item \textbf{Time frame:} Longest follow-up was 12 months
    \begin{itemize}
      \item Future: Longer-term longitudinal studies
    \end{itemize}
    
    \item \textbf{Mechanisms:} Other pathways may exist
    \begin{itemize}
      \item Future: Explore alternative mediators
    \end{itemize}
  \end{enumerate}
\end{frame}

\begin{frame}{Future Research Program}
  \begin{block}{Immediate Next Steps}
    \begin{itemize}
      \item Replicate in clinical populations
      \item Develop intervention based on findings
      \item Test with diverse samples
      \item Examine individual differences in response
    \end{itemize}
  \end{block}
  
  \vspace{0.5cm}
  
  \textbf{Long-Term Research Agenda:}
  \begin{enumerate}
    \item \textbf{Mechanism refinement:} Neural/biological underpinnings
    \item \textbf{Intervention development:} RCT of theory-driven treatment
    \item \textbf{Moderator exploration:} Genetic, environmental factors
    \item \textbf{Translation:} Dissemination and implementation science
    \item \textbf{Extension:} Apply framework to related phenomena
  \end{enumerate}
  
  \vspace{0.5cm}
  
  \textbf{Collaboration Opportunities:}
  \begin{itemize}
    \item Clinical partners for intervention trials
    \item Neuroscientists for mechanism studies
    \item Community organizations for implementation
  \end{itemize}
\end{frame}

%==============================================
% CONCLUSIONS
%==============================================

\section{Conclusions}

\begin{frame}{Dissertation Conclusions}
  \begin{exampleblock}{Central Thesis (Revisited)}
    Through three complementary studies, this dissertation demonstrates that X influences Y through mechanisms A and B, moderated by Z, with effects generalizing across contexts.
  \end{exampleblock}
  
  \vspace{0.5cm}
  
  \textbf{Key Achievements:}
  \begin{enumerate}
    \item Established robust X→Y relationship across designs
    \item Identified and validated A→B mediating pathway
    \item Demonstrated causality via experimental manipulation
    \item Showed generalizability from lab to field
    \item Proposed novel XYZ theoretical framework
  \end{enumerate}
  
  \vspace{0.5cm}
  
  \textbf{Significance:}
  \begin{itemize}
    \item Theoretical advancement in understanding X→Y processes
    \item Methodological contribution through multi-study design
    \item Practical applications for intervention and policy
    \item Foundation for sustained research program
  \end{itemize}
\end{frame}

\begin{frame}{Final Thoughts}
  \begin{block}{Take-Home Message}
    This dissertation provides compelling converging evidence that X causes Y through mechanisms A and B, offering both theoretical understanding and practical pathways for intervention.
  \end{block}
  
  \vspace{1cm}
  
  \textbf{Broader Impact:}
  \begin{itemize}
    \item Advances scientific understanding of fundamental process
    \item Provides evidence-based framework for practitioners
    \item Opens new avenues for future research
    \item Demonstrates potential to improve outcomes for affected populations
  \end{itemize}
  
  \vspace{1cm}
  
  \begin{center}
    \textit{"The best way to predict the future is to create it."} \\
    -- Peter Drucker
  \end{center}
\end{frame}

\begin{frame}[plain]
  \begin{center}
    {\LARGE \textbf{Thank You}}
    
    \vspace{1cm}
    
    {\Large Questions from the Committee}
    
    \vspace{1.5cm}
    
    \textbf{Your Name, M.S.}\\
    Doctoral Candidate\\
    Department of Your Field\\
    University Name\\
    \texttt{yourname@university.edu}
    
    \vspace{1cm}
    
    {\footnotesize
      \textbf{Funding Acknowledgment:}\\
      This research was supported by [Grant Agency] Grant \#[Number],\\
      [Fellowship Name], and [University] Dissertation Fellowship
      
      \vspace{0.5cm}
      
      \textbf{Special Thanks:}\\
      My advisor Prof. [Name], committee members, lab colleagues,\\
      study participants, and my family for their unwavering support
    }
  \end{center}
\end{frame}

%==============================================
% BACKUP SLIDES
%==============================================

\appendix

\begin{frame}{Backup: Study 1 Full Results}
  \begin{table}
    \centering
    \caption{Complete regression results for Study 1}
    \footnotesize
    \begin{tabular}{lcccc}
      \toprule
      \textbf{Predictor} & $\boldsymbol{\beta}$ & \textbf{SE} & \textbf{$t$} & \textbf{$p$} \\
      \midrule
      \multicolumn{5}{l}{\textit{Step 1: Demographics}} \\
      Age & 0.12 & 0.04 & 3.00 & .003 \\
      Gender & 0.08 & 0.05 & 1.60 & .110 \\
      Education & 0.15 & 0.04 & 3.75 & < .001 \\
      \midrule
      \multicolumn{5}{l}{\textit{Step 2: Main Effect}} \\
      X & 0.47 & 0.04 & 11.75 & < .001 \\
      \midrule
      \multicolumn{5}{l}{\textit{Step 3: Moderation}} \\
      Z & 0.18 & 0.04 & 4.50 & < .001 \\
      X × Z & 0.12 & 0.04 & 3.00 & .003 \\
      \bottomrule
      \multicolumn{5}{l}{Final model: $R^2 = .28$, $F(6,493) = 32.1$, $p < .001$} \\
    \end{tabular}
  \end{table}
\end{frame}

\begin{frame}{Backup: Study 2 Model Fit}
  \textbf{Structural Equation Model Fit Indices:}
  
  \begin{table}
    \centering
    \begin{tabular}{lcc}
      \toprule
      \textbf{Index} & \textbf{Value} & \textbf{Criterion} \\
      \midrule
      $\chi^2$/df & 2.34 & < 3.0 \\
      CFI & 0.96 & > 0.95 \\
      TLI & 0.95 & > 0.95 \\
      RMSEA & 0.045 & < 0.06 \\
      SRMR & 0.038 & < 0.08 \\
      \bottomrule
    \end{tabular}
  \end{table}
  
  \vspace{0.5cm}
  
  \textbf{Conclusion:} Excellent model fit, proposed model fits data well
  
  \vspace{0.5cm}
  
  \textbf{Alternative Models Tested:}
  \begin{itemize}
    \item Direct-only model: $\Delta\chi^2(2) = 45.6$, $p < .001$ (worse fit)
    \item Reverse mediation: $\Delta\chi^2(2) = 38.2$, $p < .001$ (worse fit)
    \item Proposed model provides best fit
  \end{itemize}
\end{frame}

\begin{frame}{Backup: Study 3 Additional Analyses}
  \textbf{Subgroup Effects:}
  
  \begin{figure}
    \centering
    % \includegraphics[width=0.7\textwidth]{study3_subgroups.pdf}
    \framebox[0.65\textwidth][c]{[Subgroup Analysis Results]}
    \caption{Effect of X on Y by moderator Z levels}
  \end{figure}
  
  \begin{itemize}
    \item High Z: $d = 0.95$, $p < .001$
    \item Medium Z: $d = 0.72$, $p < .001$
    \item Low Z: $d = 0.45$, $p = .008$
    \item Moderation: $F(2,174) = 6.8$, $p = .001$
  \end{itemize}
\end{frame}

%==============================================
% REFERENCES
%==============================================

\begin{frame}[allowframebreaks]{References}
  \printbibliography
\end{frame}

\end{document}
```

### `assets/beamer_template_seminar.tex`

```latex
\documentclass[aspectratio=169,11pt]{beamer}

% Encoding
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}

% Theme and colors
\usetheme{Madrid}
\usecolortheme{dolphin}

% Remove navigation symbols
\setbeamertemplate{navigation symbols}{}

% Section pages
\AtBeginSection[]{
  \begin{frame}
    \vfill
    \centering
    \begin{beamercolorbox}[sep=8pt,center,shadow=true,rounded=true]{title}
      \usebeamerfont{title}\insertsectionhead\par%
    \end{beamercolorbox}
    \vfill
  \end{frame}
}

% Graphics
\usepackage{graphicx}
\graphicspath{{./figures/}}

% Math
\usepackage{amsmath, amssymb, amsthm}

% Tables
\usepackage{booktabs}
\usepackage{multirow}

% Citations
\usepackage[style=authoryear,maxcitenames=2,backend=biber]{biblatex}
\addbibresource{references.bib}
\renewcommand*{\bibfont}{\tiny}

% Algorithms
\usepackage{algorithm}
\usepackage{algorithmic}

% Code
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\small,
  keywordstyle=\color{blue},
  commentstyle=\color{green!60!black},
  stringstyle=\color{orange},
  numbers=left,
  numberstyle=\tiny,
  frame=single,
  breaklines=true
}

% Custom colors
\definecolor{darkblue}{RGB}{0,75,135}
\definecolor{lightblue}{RGB}{100,150,200}

\setbeamercolor{structure}{fg=darkblue}
\setbeamercolor{title}{fg=darkblue}
\setbeamercolor{frametitle}{fg=darkblue}

% Title information
\title[Short Title for Footer]{Full Title of Your Research:\\Comprehensive and Descriptive}
\subtitle{Research Seminar Presentation}
\author[Your Name]{Your Name, PhD Candidate\\
  Advisor: Prof. Advisor Name}
\institute[University]{
  Department of Your Field\\
  University Name\\
  \vspace{0.2cm}
  \texttt{yourname@university.edu}
}
\date{\today}

% Logo (optional)
% \logo{\includegraphics[height=0.8cm]{university_logo.png}}

\begin{document}

% Title slide
\begin{frame}[plain]
  \titlepage
\end{frame}

% Outline
\begin{frame}{Outline}
  \tableofcontents
\end{frame}

%==============================================
% INTRODUCTION
%==============================================

\section{Introduction}

\begin{frame}{Motivation}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{The Big Picture:}
      \begin{itemize}
        \item Why this research area matters
        \item Real-world impact and applications
        \item Current challenges in the field
        \item Opportunity for advancement
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{motivation_figure.pdf}
        \framebox[0.9\textwidth][c]{[Motivating Figure]}
        \caption{Illustration of the problem or impact}
      \end{figure}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \begin{block}{Central Question}
    How can we address this important challenge using novel approach X?
  \end{block}
\end{frame}

\subsection{Background}

\begin{frame}{Prior Work: Overview}
  \textbf{Historical Development:}
  \begin{itemize}
    \item Early work established foundation \cite{seminal1990}
    \item Key advances in 2000s \cite{advance2005,advance2007}
    \item Recent developments \cite{recent2020,recent2022}
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Current State of Knowledge:}
  \begin{enumerate}
    \item We know that X affects Y
    \item Evidence suggests mechanism involves Z
    \item However, questions remain about W
  \end{enumerate}
\end{frame}

\begin{frame}{Knowledge Gap}
  \begin{columns}[c]
    
    \begin{column}{0.6\textwidth}
      \textbf{What We Know:}
      \begin{itemize}
        \item Point 1: Established finding
        \item Point 2: Replicated result
        \item Point 3: General consensus
      \end{itemize}
      
      \vspace{0.5cm}
      
      \textbf{What Remains Unknown:}
      \begin{itemize}
        \item \alert{Gap 1:} Critical unknown
        \item \alert{Gap 2:} Methodological limitation
        \item \alert{Gap 3:} Unexplored context
      \end{itemize}
    \end{column}
    
    \begin{column}{0.4\textwidth}
      \begin{alertblock}{The Problem}
        Existing approaches fail to account for X, limiting our understanding of Y and preventing application to Z.
      \end{alertblock}
    \end{column}
    
  \end{columns}
\end{frame}

\subsection{Research Questions}

\begin{frame}{Research Objectives}
  \begin{exampleblock}{Overall Goal}
    To investigate how X influences Y under conditions Z, and develop a framework for understanding mechanism W.
  \end{exampleblock}
  
  \vspace{0.5cm}
  
  \textbf{Specific Aims:}
  \begin{enumerate}
    \item \textbf{Aim 1:} Characterize relationship between X and Y
    \begin{itemize}
      \item Hypothesis: X positively correlates with Y
    \end{itemize}
    
    \item \textbf{Aim 2:} Identify mechanism W mediating X→Y
    \begin{itemize}
      \item Hypothesis: W explains the X-Y relationship
    \end{itemize}
    
    \item \textbf{Aim 3:} Test generalizability to context Z
    \begin{itemize}
      \item Hypothesis: Effect persists across conditions
    \end{itemize}
  \end{enumerate}
\end{frame}

%==============================================
% METHODS
%==============================================

\section{Methods}

\subsection{Study Design}

\begin{frame}{Overall Approach}
  \begin{figure}
    \centering
    % \includegraphics[width=0.9\textwidth]{study_design.pdf}
    \framebox[0.8\textwidth][c]{[Study Design Schematic]}
    \caption{Three-phase experimental design}
  \end{figure}
  
  \begin{itemize}
    \item \textbf{Phase 1:} Observational study (n = 150)
    \item \textbf{Phase 2:} Controlled experiment (n = 80)
    \item \textbf{Phase 3:} Validation in new context (n = 120)
  \end{itemize}
\end{frame}

\subsection{Participants and Materials}

\begin{frame}{Sample Characteristics}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Inclusion Criteria:}
      \begin{itemize}
        \item Age 18-65 years
        \item Criterion 2
        \item Criterion 3
      \end{itemize}
      
      \vspace{0.3cm}
      
      \textbf{Exclusion Criteria:}
      \begin{itemize}
        \item Confound 1
        \item Confound 2
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{table}
        \centering
        \caption{Sample demographics}
        \small
        \begin{tabular}{lc}
          \toprule
          \textbf{Variable} & \textbf{Value} \\
          \midrule
          N & 150 \\
          Age (years) & 32.5 $\pm$ 8.2 \\
          Female (\%) & 58 \\
          Education (years) & 15.2 $\pm$ 2.1 \\
          \bottomrule
        \end{tabular}
      \end{table}
    \end{column}
    
  \end{columns}
  
  \vspace{0.3cm}
  
  \footnotesize Recruitment: University community and online platforms
\end{frame}

\subsection{Procedures}

\begin{frame}{Experimental Procedure}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Session 1 (60 min):}
      \begin{enumerate}
        \item Informed consent
        \item Baseline measures
        \item Training phase (20 min)
        \item Test phase (30 min)
      \end{enumerate}
      
      \vspace{0.5cm}
      
      \textbf{Session 2 (45 min):}
      \begin{enumerate}
        \setcounter{enumi}{4}
        \item Follow-up measures
        \item Manipulation (15 min)
        \item Final assessment (25 min)
      \end{enumerate}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{procedure_timeline.pdf}
        \framebox[0.9\textwidth][c]{[Timeline Diagram]}
        \caption{Experimental timeline}
      \end{figure}
      
      \vspace{0.5cm}
      
      \begin{alertblock}{Key Innovation}
        Novel manipulation technique combining approach A with method B
      \end{alertblock}
    \end{column}
    
  \end{columns}
\end{frame}

\subsection{Analysis}

\begin{frame}{Statistical Analysis Plan}
  \textbf{Primary Analyses:}
  \begin{itemize}
    \item \textbf{Aim 1:} Linear regression: $Y = \beta_0 + \beta_1 X + \epsilon$
    \item \textbf{Aim 2:} Mediation analysis using bootstrapping (5000 iterations)
    \item \textbf{Aim 3:} Mixed-effects model accounting for context effects
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Secondary Analyses:}
  \begin{itemize}
    \item Sensitivity analyses with different covariates
    \item Subgroup analyses by demographic factors
    \item Exploratory analyses of individual differences
  \end{itemize}
  
  \vspace{0.5cm}
  
  \begin{block}{Software}
    R 4.2.1 (lme4, lavaan packages); Python 3.10 (scikit-learn); SPSS 28
  \end{block}
\end{frame}

%==============================================
% RESULTS
%==============================================

\section{Results}

\subsection{Preliminary Analyses}

\begin{frame}{Data Quality and Assumptions}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Data Screening:}
      \begin{itemize}
        \item Missing data: < 5\% per variable
        \item Outliers: 3 cases removed
        \item Assumptions: All met
      \end{itemize}
      
      \vspace{0.3cm}
      
      \textbf{Descriptive Statistics:}
      \begin{itemize}
        \item Variable X: $M = 45.2$, $SD = 8.1$
        \item Variable Y: $M = 67.8$, $SD = 12.3$
        \item Correlation: $r = 0.54$, $p < .001$
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{descriptives.pdf}
        \framebox[0.9\textwidth][c]{[Descriptive Plots]}
        \caption{Variable distributions}
      \end{figure}
    \end{column}
    
  \end{columns}
\end{frame}

\subsection{Aim 1 Results}

\begin{frame}{Aim 1: X Predicts Y}
  \begin{columns}[c]
    
    \begin{column}{0.6\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{aim1_result.pdf}
        \framebox[0.9\textwidth][c]{[Regression Plot]}
        \caption{Relationship between X and Y ($R^2 = 0.29$, $p < .001$)}
      \end{figure}
    \end{column}
    
    \begin{column}{0.4\textwidth}
      \begin{table}
        \centering
        \caption{Regression results}
        \tiny
        \begin{tabular}{lccc}
          \toprule
          \textbf{Predictor} & $\boldsymbol{\beta}$ & \textbf{SE} & \textbf{$p$} \\
          \midrule
          Intercept & 12.45 & 3.21 & < .001 \\
          X & 0.54 & 0.08 & < .001 \\
          Age & 0.12 & 0.05 & .018 \\
          Gender & 2.34 & 1.12 & .038 \\
          \bottomrule
        \end{tabular}
      \end{table}
      
      \vspace{0.3cm}
      
      \begin{block}{Key Finding}
        X significantly predicts Y, controlling for demographics
      \end{block}
    \end{column}
    
  \end{columns}
\end{frame}

\subsection{Aim 2 Results}

\begin{frame}{Aim 2: Mediation by W}
  \begin{figure}
    \centering
    % \includegraphics[width=0.8\textwidth]{mediation_model.pdf}
    \framebox[0.7\textwidth][c]{[Mediation Diagram]}
    \caption{Mediation analysis showing W mediates X→Y relationship}
  \end{figure}
  
  \begin{itemize}
    \item \textbf{Direct effect:} $c' = 0.31$, $p = .021$ (reduced from $c = 0.54$)
    \item \textbf{Indirect effect:} $ab = 0.23$, 95\% CI [0.14, 0.35]
    \item \textbf{Proportion mediated:} 43\% of total effect
  \end{itemize}
  
  \vspace{0.3cm}
  
  \alert{W partially mediates the relationship between X and Y}
\end{frame}

\subsection{Aim 3 Results}

\begin{frame}{Aim 3: Generalization to Context Z}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{aim3_context1.pdf}
        \framebox[0.9\textwidth][c]{[Context 1]}
        \caption{Original context}
      \end{figure}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \begin{figure}
        \centering
        % \includegraphics[width=\textwidth]{aim3_context2.pdf}
        \framebox[0.9\textwidth][c]{[Context 2]}
        \caption{New context Z}
      \end{figure}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \textbf{Mixed-Effects Model Results:}
  \begin{itemize}
    \item Main effect of X: $\beta = 0.51$, $p < .001$
    \item Context × X interaction: $\beta = -0.08$, $p = .231$ (ns)
    \item \alert{Effect generalizes across contexts}
  \end{itemize}
\end{frame}

\subsection{Additional Analyses}

\begin{frame}{Sensitivity and Robustness Checks}
  \textbf{Alternative Specifications:}
  \begin{itemize}
    \item Result robust to different model specifications
    \item Consistent across multiple imputation methods
    \item Findings hold with/without covariates
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Subgroup Analyses:}
  \begin{table}
    \centering
    \caption{Effect sizes by subgroup}
    \small
    \begin{tabular}{lccc}
      \toprule
      \textbf{Subgroup} & \textbf{$n$} & $\boldsymbol{\beta}$ & \textbf{$p$} \\
      \midrule
      Young (< 30) & 67 & 0.58 & < .001 \\
      Older ($\geq$ 30) & 83 & 0.49 & < .001 \\
      Male & 63 & 0.52 & < .001 \\
      Female & 87 & 0.55 & < .001 \\
      \bottomrule
    \end{tabular}
  \end{table}
  
  Effect consistent across demographic groups
\end{frame}

%==============================================
% DISCUSSION
%==============================================

\section{Discussion}

\subsection{Summary of Findings}

\begin{frame}{Key Results Recap}
  \begin{exampleblock}{Main Findings}
    \begin{enumerate}
      \item X significantly predicts Y ($\beta = 0.54$, $p < .001$), explaining 29\% of variance
      \item W mediates 43\% of the X→Y relationship
      \item Effect generalizes to new context Z
      \item Results robust across subgroups and specifications
    \end{enumerate}
  \end{exampleblock}
  
  \vspace{0.5cm}
  
  \textbf{These findings:}
  \begin{itemize}
    \item Support our hypotheses
    \item Provide evidence for mechanism W
    \item Extend previous work to new domains
    \item Have implications for theory and practice
  \end{itemize}
\end{frame}

\subsection{Interpretation}

\begin{frame}{Relation to Previous Research}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Consistent With:}
      \begin{itemize}
        \item Prior findings on X→Y \cite{jones2020}
        \item Theoretical predictions \cite{smith2019}
        \item Meta-analytic trends \cite{meta2021}
      \end{itemize}
      
      \vspace{0.5cm}
      
      \textbf{Extensions Beyond:}
      \begin{itemize}
        \item Identifies mechanism W (new)
        \item Tests in context Z (novel)
        \item Larger sample than prior work
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \textbf{Resolves Contradictions:}
      \begin{itemize}
        \item Explains why Study A found X
        \item Reconciles Studies B and C
        \item Clarifies conditions for effect
      \end{itemize}
      
      \vspace{0.5cm}
      
      \begin{alertblock}{Novel Contribution}
        First study to demonstrate W as mediator and show generalization to Z
      \end{alertblock}
    \end{column}
    
  \end{columns}
\end{frame}

\begin{frame}{Mechanisms and Explanations}
  \textbf{Why does X affect Y through W?}
  
  \vspace{0.3cm}
  
  \begin{enumerate}
    \item<1-> \textbf{Hypothesis 1:} X activates process W
    \begin{itemize}
      \item<1-> Evidence: Temporal precedence in data
      \item<1-> Consistent with neurobiological models
    \end{itemize}
    
    \vspace{0.3cm}
    
    \item<2-> \textbf{Hypothesis 2:} W is necessary for Y
    \begin{itemize}
      \item<2-> Evidence: Mediation analysis results
      \item<2-> Supported by experimental manipulations
    \end{itemize}
    
    \vspace{0.3cm}
    
    \item<3-> \textbf{Integrated Model:} X → W → Y pathway
    \begin{itemize}
      \item<3-> Explains 43\% of total effect
      \item<3-> Other pathways remain to be identified
    \end{itemize}
  \end{enumerate}
\end{frame}

\subsection{Implications}

\begin{frame}{Theoretical Implications}
  \textbf{Advances to Theory:}
  \begin{itemize}
    \item Refines existing framework by identifying W
    \item Suggests revision of Model XYZ
    \item Provides testable predictions for future work
    \item Integrates previously separate literatures
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Broader Scientific Impact:}
  \begin{itemize}
    \item Methodology can be applied to related domains
    \item Framework generalizable to other contexts
    \item Opens new research directions
  \end{itemize}
\end{frame}

\begin{frame}{Practical Applications}
  \begin{columns}[T]
    
    \begin{column}{0.5\textwidth}
      \textbf{Clinical/Applied:}
      \begin{itemize}
        \item Intervention target: W
        \item Assessment tool: Measure X
        \item Treatment planning: Consider Z
        \item Expected benefit: Improvement in Y
      \end{itemize}
    \end{column}
    
    \begin{column}{0.5\textwidth}
      \textbf{Policy Implications:}
      \begin{itemize}
        \item Recommendation 1
        \item Recommendation 2
        \item Implementation considerations
        \item Cost-benefit analysis
      \end{itemize}
    \end{column}
    
  \end{columns}
  
  \vspace{0.5cm}
  
  \begin{exampleblock}{Translational Path}
    Findings suggest feasibility of intervention targeting W to improve Y in population experiencing X
  \end{exampleblock}
\end{frame}

\subsection{Limitations and Future Directions}

\begin{frame}{Limitations}
  \textbf{Study Limitations:}
  \begin{enumerate}
    \item \textbf{Cross-sectional design}: Cannot establish causality definitively
    \begin{itemize}
      \item Future: Longitudinal or experimental design
    \end{itemize}
    
    \item \textbf{Sample characteristics}: University students, may limit generalizability
    \begin{itemize}
      \item Future: Community sample, diverse populations
    \end{itemize}
    
    \item \textbf{Measurement}: Self-report bias possible for some variables
    \begin{itemize}
      \item Future: Incorporate objective measures
    \end{itemize}
    
    \item \textbf{Unmeasured confounds}: Other factors could explain relationships
    \begin{itemize}
      \item Future: Control for additional variables
    \end{itemize}
  \end{enumerate}
\end{frame}

\begin{frame}{Future Research Directions}
  \begin{block}{Immediate Next Steps}
    \begin{itemize}
      \item Replicate in independent sample
      \item Test causal model experimentally
      \item Examine boundary conditions
    \end{itemize}
  \end{block}
  
  \vspace{0.5cm}
  
  \textbf{Longer-Term Goals:}
  \begin{itemize}
    \item Develop intervention based on findings
    \item Investigate neural mechanisms
    \item Explore individual differences
    \item Translate to applied settings
  \end{itemize}
  
  \vspace{0.5cm}
  
  \textbf{Collaborations Sought:}
  \begin{itemize}
    \item Experts in domain A for validation
    \item Clinical partners for translation
    \item Methodologists for advanced analyses
  \end{itemize}
\end{frame}

%==============================================
% CONCLUSION
%==============================================

\section{Conclusion}

\begin{frame}{Conclusions}
  \begin{exampleblock}{Key Contributions}
    \begin{enumerate}
      \item Demonstrated robust X→Y relationship
      \item Identified W as mediating mechanism
      \item Showed generalizability across contexts
      \item Provided framework for future research
    \end{enumerate}
  \end{exampleblock}
  
  \vspace{0.5cm}
  
  \begin{block}{Take-Home Message}
    Our findings reveal that X influences Y through mechanism W, providing new understanding of this important process and suggesting potential intervention targets.
  \end{block}
  
  \vspace{0.5cm}
  
  \textbf{Impact:}
  \begin{itemize}
    \item Theoretical advancement in understanding X→Y
    \item Practical implications for interventions
    \item Foundation for future research program
  \end{itemize}
\end{frame}

\begin{frame}[plain]
  \begin{center}
    {\LARGE \textbf{Thank You}}
    
    \vspace{1cm}
    
    {\Large Questions \& Discussion}
    
    \vspace{1.5cm}
    
    \begin{columns}
      \begin{column}{0.6\textwidth}
        \textbf{Contact Information:}\\
        Your Name\\
        Department of Your Field\\
        University Name\\
        \texttt{yourname@university.edu}\\
        \url{https://yourlab.university.edu}
      \end{column}
      
      \begin{column}{0.4\textwidth}
        % QR code to lab website or paper
        % \includegraphics[width=4cm]{qrcode_website.png}\\
        % {\small Scan for more info}
      \end{column}
    \end{columns}
    
    \vspace{1cm}
    
    {\footnotesize
      \textbf{Acknowledgments:}\\
      Funding: NSF Grant \#12345, NIH Grant R01-67890\\
      Lab Members: Person A, Person B, Person C\\
      Collaborators: Prof. X (University Y), Dr. Z (Institution W)
    }
  \end{center}
\end{frame}

%==============================================
% BACKUP SLIDES
%==============================================

\appendix

\begin{frame}{Backup: Full Regression Table}
  \begin{table}
    \centering
    \caption{Complete regression results with all covariates}
    \footnotesize
    \begin{tabular}{lcccc}
      \toprule
      \textbf{Predictor} & $\boldsymbol{\beta}$ & \textbf{SE} & \textbf{$t$} & \textbf{$p$} \\
      \midrule
      Intercept & 12.45 & 3.21 & 3.88 & < .001 \\
      X (primary predictor) & 0.54 & 0.08 & 6.75 & < .001 \\
      Age & 0.12 & 0.05 & 2.40 & .018 \\
      Gender (female) & 2.34 & 1.12 & 2.09 & .038 \\
      Education & 0.45 & 0.31 & 1.45 & .149 \\
      Covariate Z & -0.18 & 0.09 & -2.00 & .047 \\
      \midrule
      $R^2$ & \multicolumn{4}{c}{0.35} \\
      Adjusted $R^2$ & \multicolumn{4}{c}{0.32} \\
      $F$(5,144) & \multicolumn{4}{c}{15.48, $p < .001$} \\
      \bottomrule
    \end{tabular}
  \end{table}
\end{frame}

\begin{frame}{Backup: Alternative Analysis}
  \begin{figure}
    \centering
    % \includegraphics[width=0.75\textwidth]{sensitivity_analysis.pdf}
    \framebox[0.7\textwidth][c]{[Sensitivity Analysis Results]}
    \caption{Results robust across different model specifications}
  \end{figure}
\end{frame}

\begin{frame}{Backup: Detailed Methods}
  \textbf{Measurement Details:}
  \begin{itemize}
    \item \textbf{Variable X:} Scale name (Author, Year)
    \begin{itemize}
      \item 12 items, 5-point Likert scale
      \item Cronbach's $\alpha = 0.89$
      \item Example item: "Statement here"
    \end{itemize}
    
    \item \textbf{Variable Y:} Assessment tool
    \begin{itemize}
      \item Performance-based measure
      \item Inter-rater reliability: ICC = 0.92
      \item Range: 0-100
    \end{itemize}
    
    \item \textbf{Mediator W:} Experimental manipulation check
    \begin{itemize}
      \item Manipulation successful: $t(149) = 8.45$, $p < .001$
      \item Effect size: $d = 1.38$
    \end{itemize}
  \end{itemize}
\end{frame}

%==============================================
% REFERENCES
%==============================================

\begin{frame}[allowframebreaks]{References}
  \printbibliography
\end{frame}

\end{document}
```

### `assets/powerpoint_design_guide.md`

# PowerPoint Design Guide for Scientific Presentations

## Overview

This guide provides comprehensive instructions for creating professional scientific presentations using PowerPoint, with emphasis on integration with the pptx skill for programmatic creation and best practices for scientific content.

**CRITICAL**: Avoid dry, text-heavy presentations. Scientific slides should be:
- **Visually engaging**: High-quality images, figures, diagrams on EVERY slide
- **Research-backed**: Citations from research-lookup for credibility (8-15 papers minimum)
- **Modern design**: Contemporary color palettes, not default themes
- **Minimal text**: 3-4 bullets with 4-6 words each, visuals do the talking
- **Professional polish**: Consistent but varied layouts, generous white space

**Anti-Pattern Warning**: All-bullet-point slides with black text on white background = instant boredom and forgotten science.

## Using the PPTX Skill

### Reference

For complete technical documentation on PowerPoint creation, refer to:
- **Main documentation**: `document-skills/pptx/SKILL.md`
- **HTML to PowerPoint workflow**: Detailed in `pptx/html2pptx.md`
- **OOXML editing**: For advanced editing in `pptx/ooxml.md`

### Two Approaches to PowerPoint Creation

#### 1. Programmatic Creation (html2pptx)

**Best for**: Creating presentations from scratch with custom designs and data visualizations.

**Workflow**:
1. Read `document-skills/pptx/SKILL.md` completely
2. Design slides in HTML with proper dimensions (720pt × 405pt for 16:9)
3. Create JavaScript file using `html2pptx()` function
4. Add charts and tables using PptxGenJS API
5. Generate thumbnails and validate visually
6. Iterate based on visual inspection

**Example Structure**:
```javascript
const pptx = new PptxGenJS();

// Add title slide
const slide1 = pptx.addSlide();
slide1.addText("Your Title", {
  x: 1, y: 2, w: 8, h: 1,
  fontSize: 44, bold: true, align: "center"
});

// Add content slide with figure
const slide2 = pptx.addSlide();
slide2.addText("Results", { x: 0.5, y: 0.5, fontSize: 32 });
slide2.addImage({ path: "figure.png", x: 1, y: 1.5, w: 8, h: 4 });

pptx.writeFile({ fileName: "presentation.pptx" });
```

#### 2. Template-Based Creation

**Best for**: Using existing PowerPoint templates or editing existing presentations.

**Workflow**:
1. Start with template.pptx
2. Use `scripts/rearrange.py` to duplicate/reorder slides
3. Use `scripts/inventory.py` to extract text
4. Generate replacement text JSON
5. Use `scripts/replace.py` to update content
6. Validate with thumbnail grids

**Key Scripts**:
- `rearrange.py`: Duplicate and reorder slides
- `inventory.py`: Extract all text shapes
- `replace.py`: Apply text replacements
- `thumbnail.py`: Visual validation

## Design Principles for Scientific Presentations

### 1. Layout and Structure

**Slide Master Setup**:
- Create consistent master slides
- Define 4-5 layout types (title, content, figure, two-column, closing)
- Set default fonts, colors, and spacing
- Include placeholders for logos and footers

**Standard Layouts**:

**Title Slide**:
```
┌─────────────────────────┐
│                         │
│   Presentation Title    │
│   Your Name             │
│   Institution           │
│   Date / Conference     │
│                         │
└─────────────────────────┘
```

**Content Slide**:
```
┌─────────────────────────┐
│ Slide Title             │
├─────────────────────────┤
│ • Bullet point 1        │
│ • Bullet point 2        │
│ • Bullet point 3        │
│                         │
│ [Optional figure]       │
└─────────────────────────┘
```

**Two-Column Slide**:
```
┌─────────────────────────┐
│ Slide Title             │
├───────────┬─────────────┤
│           │             │
│  Text     │   Figure    │
│  Content  │   or        │
│           │   Data      │
└───────────┴─────────────┘
```

**Full-Figure Slide**:
```
┌─────────────────────────┐
│ Figure Title (small)    │
├─────────────────────────┤
│                         │
│    Large Figure or      │
│    Visualization        │
│                         │
└─────────────────────────┘
```

### 2. Typography

**Font Selection**:
- **Primary**: Sans-serif (Arial, Calibri, Helvetica)
- **Alternative**: Verdana, Tahoma, Trebuchet MS
- **Avoid**: Serif fonts (harder to read on screens), decorative fonts

**Font Sizes**:
- Title slide title: 44-54pt
- Slide titles: 32-40pt
- Body text: 24-28pt (minimum 18pt)
- Captions: 16-20pt
- Footer: 10-12pt

**Text Formatting**:
- **Bold**: For emphasis (use sparingly)
- **Color**: For highlighting (consistent meaning)
- **Size**: For hierarchy
- **Alignment**: Left for body, center for titles

**The 6×6 Rule**:
- Maximum 6 bullet points per slide
- Maximum 6 words per bullet
- Better: 3-4 bullets with 4-8 words each

### 3. Color Schemes

**Selecting Colors**:

Consider your subject matter and audience:
- **Academic/Professional**: Navy blue, gray, white with minimal accent
- **Biomedical**: Blue and green tones (avoid red-green combinations)
- **Technology**: Modern colors (teal, orange, purple)
- **Clinical**: Conservative (blue, gray, subdued greens)

**Example Palettes**:

**Classic Scientific**:
- Background: White (#FFFFFF)
- Title: Navy (#1C3D5A)
- Text: Dark gray (#2D3748)
- Accent: Orange (#E67E22)

**Modern Research**:
- Background: Light gray (#F7FAFC)
- Title: Teal (#0A9396)
- Text: Charcoal (#2C2C2C)
- Accent: Coral (#EE6C4D)

**High Contrast** (for large venues):
- Background: White (#FFFFFF)
- Title: Black (#000000)
- Text: Dark gray (#1A1A1A)
- Accent: Bright blue (#0066CC)

**Accessibility Guidelines**:
- Minimum contrast ratio: 4.5:1 (body text)
- Preferred contrast ratio: 7:1 (AAA standard)
- Avoid red-green combinations (8% of men are color-blind)
- Use patterns or shapes in addition to color for data

### 4. Visual Elements

**Figures and Images**:
- **Resolution**: Minimum 300 DPI for print, 150 DPI for projection
- **Format**: PNG for screenshots, PDF/SVG for vector graphics
- **Size**: Large enough to be readable from back of room
- **Placement**: Center or use two-column layout

**Data Visualizations**:
- **Simplify** from journal figures (fewer panels, larger text)
- **Font sizes**: 18-24pt for axis labels
- **Line widths**: 2-4pt thickness
- **Colors**: High contrast, color-blind safe
- **Labels**: Direct labeling preferred over legends

**Icons and Shapes**:
- Use for visual interest and organization
- Consistent style (all outline or all filled)
- Size appropriately (not too large or small)
- Limit colors (match theme)

### 5. Animations and Transitions

**When to Use**:
- ✅ Progressive disclosure of bullet points
- ✅ Building complex figures incrementally
- ✅ Emphasizing key findings
- ✅ Showing process steps

**When to Avoid**:
- ❌ Decoration or entertainment
- ❌ Every single slide
- ❌ Distracting effects (fly in, bounce, spin)

**Recommended Animations**:
- **Appear**: Clean, professional
- **Fade**: Subtle transition
- **Wipe**: Directional reveal
- **Duration**: Fast (0.2-0.3 seconds)
- **Trigger**: On click (not automatic)

**Slide Transitions**:
- Use consistent transition throughout (or none)
- Recommended: None, Fade, or Push
- Avoid: 3D rotations, complex effects
- Duration: Very fast (0.3-0.5 seconds)

## Creating Presentations with PPTX Skill

### Design-First Workflow

**Step 0: Choose Modern Color Palette Based on Topic**

**CRITICAL**: Select colors that reflect your subject matter, not generic defaults.

**Topic-Based Palette Examples:**
- **Biotechnology/Life Sciences**: Teal (#0A9396), Coral (#EE6C4D), Cream (#F4F1DE)
- **Neuroscience/Brain Research**: Deep Purple (#722880), Magenta (#D72D51), White
- **Machine Learning/AI**: Bold Red (#E74C3C), Orange (#F39C12), Dark Gray (#2C2C2C)
- **Physics/Engineering**: Navy (#1C3D5A), Orange (#E67E22), Light Gray (#F7FAFC)
- **Medicine/Healthcare**: Teal (#5EA8A7), Coral (#FE4447), White (#FFFFFF)
- **Environmental Science**: Sage (#87A96B), Terracotta (#E07A5F), Cream (#F4F1DE)

See full palette options in pptx skill SKILL.md (lines 76-94).

**Step 1: Plan Design System** (With Modern Palette)
```javascript
// Define design constants with MODERN colors (not defaults)
const DESIGN = {
  colors: {
    primary: "0A9396",    // Teal (modern, engaging)
    accent: "EE6C4D",     // Coral (attention-grabbing)
    text: "2C2C2C",       // Charcoal (readable)
    background: "FFFFFF"  // White (clean)
  },
  fonts: {
    title: { size: 40, bold: true, face: "Arial" },
    heading: { size: 28, bold: true, face: "Arial" },
    body: { size: 24, face: "Arial" },
    caption: { size: 16, face: "Arial" }
  },
  layout: {
    margin: 0.5,
    titleY: 0.5,
    contentY: 1.5
  }
};
```

**Step 2: Create Reusable Functions**
```javascript
function addTitleSlide(pptx, title, subtitle, author) {
  const slide = pptx.addSlide();
  slide.background = { color: DESIGN.colors.primary };
  
  slide.addText(title, {
    x: 1, y: 2, w: 8, h: 1,
    fontSize: 44, bold: true, color: "FFFFFF",
    align: "center"
  });
  
  slide.addText(subtitle, {
    x: 1, y: 3.2, w: 8, h: 0.5,
    fontSize: 24, color: "FFFFFF",
    align: "center"
  });
  
  slide.addText(author, {
    x: 1, y: 4, w: 8, h: 0.4,
    fontSize: 18, color: "FFFFFF",
    align: "center"
  });
  
  return slide;
}

function addContentSlide(pptx, title, bullets) {
  const slide = pptx.addSlide();
  
  slide.addText(title, {
    x: DESIGN.layout.margin,
    y: DESIGN.layout.titleY,
    w: 9,
    h: 0.5,
    ...DESIGN.fonts.heading,
    color: DESIGN.colors.primary
  });
  
  slide.addText(bullets, {
    x: DESIGN.layout.margin,
    y: DESIGN.layout.contentY,
    w: 9,
    h: 3,
    ...DESIGN.fonts.body,
    bullet: true
  });
  
  return slide;
}
```

**Step 3: Build Presentation** (Visual-First Approach)
```javascript
const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_16x9";

// Title slide with background image or color block
const titleSlide = pptx.addSlide();
titleSlide.background = { color: DESIGN.colors.primary }; // Bold color background
addTitleSlide(
  pptx,
  "Research Title",
  "Subtitle or Conference Name",
  "Your Name • Institution • Date"
);

// Introduction with image/icon
const introSlide = pptx.addSlide();
introSlide.addImage({
  path: "concept_image.png",  // Visual representation of concept
  x: 5, y: 1.5, w: 4, h: 3
});
introSlide.addText("Background", { x: 0.5, y: 0.5, fontSize: 36, bold: true });
introSlide.addText([
  "Key context point 1 (AuthorA, 2023)",
  "Key context point 2 (AuthorB, 2022)",
  "Research gap identified (AuthorC, 2021)"
], {
  x: 0.5, y: 1.5, w: 4, h: 2,
  fontSize: 24, bullet: true
});

// Results slide - FIGURE DOMINATES
const resultsSlide = pptx.addSlide();
resultsSlide.addText("Main Finding", { x: 0.5, y: 0.5, fontSize: 32, bold: true });
resultsSlide.addImage({
  path: "results_figure.png",  // Large, clear figure
  x: 0.5, y: 1.5, w: 9, h: 4   // Nearly full slide
});
// Minimal text annotation only
resultsSlide.addText("34% improvement (p < 0.001)", {
  x: 7, y: 1, fontSize: 20, color: DESIGN.colors.accent, bold: true
});

// Save
pptx.writeFile({ fileName: "presentation.pptx" });
```

**Key Changes from Dry Presentations:**
- Title slide uses bold background color (not plain white)
- Introduction includes relevant image (not just bullets)
- Results slide is figure-dominated (not text-dominated)
- Citations included in bullets for research context
- Text is minimal and supporting, visuals are primary

### Adding Scientific Content

**Equations** (as images):
```javascript
// Render equation as PNG first (using LaTeX or online tool)
// Then add to slide
slide.addImage({
  path: "equation.png",
  x: 2, y: 3, w: 6, h: 1
});
```

**Tables**:
```javascript
slide.addTable([
  [
    { text: "Method", options: { bold: true } },
    { text: "Accuracy", options: { bold: true } },
    { text: "Time (s)", options: { bold: true } }
  ],
  ["Method A", "0.85", "10"],
  ["Method B", "0.92", "25"],
  ["Method C", "0.88", "15"]
], {
  x: 2, y: 2, w: 6,
  fontSize: 20,
  border: { pt: 1, color: "888888" },
  fill: { color: "F5F5F5" }
});
```

**Charts**:
```javascript
// Bar chart
slide.addChart(pptx.ChartType.bar, [
  {
    name: "Control",
    labels: ["Metric 1", "Metric 2", "Metric 3"],
    values: [45, 67, 82]
  },
  {
    name: "Treatment",
    labels: ["Metric 1", "Metric 2", "Metric 3"],
    values: [52, 78, 91]
  }
], {
  x: 1, y: 1.5, w: 8, h: 4,
  chartColors: [DESIGN.colors.primary, DESIGN.colors.accent],
  showTitle: false,
  showLegend: true,
  fontSize: 18
});
```

## Visual Validation Workflow

### Generate Thumbnails

After creating presentation:

```bash
# Create thumbnail grid for quick review
python scripts/thumbnail.py presentation.pptx review/thumbnails --cols 4

# Or for individual slides
python scripts/thumbnail.py presentation.pptx review/slide
```

### Inspection Checklist

For each slide, check:
- [ ] Text readable (not cut off or too small)
- [ ] No element overlap
- [ ] Consistent colors and fonts
- [ ] Adequate white space
- [ ] Figures clear and properly sized
- [ ] Alignment correct

### Common Issues

**Text Overflow**:
- Reduce font size or text length
- Increase text box size
- Split into multiple slides

**Element Overlap**:
- Use two-column layout
- Reduce element sizes
- Adjust positioning

**Poor Contrast**:
- Choose higher contrast colors
- Use dark text on light background
- Test with contrast checker

## Templates and Examples

### Starting from Template

If you have an existing template:

1. **Extract template structure**:
```bash
python scripts/inventory.py template.pptx inventory.json
```

2. **Create thumbnail grid**:
```bash
python scripts/thumbnail.py template.pptx template_review
```

3. **Analyze layouts** and document which slides to use

4. **Rearrange slides**:
```bash
python scripts/rearrange.py template.pptx working.pptx 0,5,5,12,18,22
```

5. **Replace content**:
```bash
python scripts/replace.py working.pptx replacements.json output.pptx
```

## Best Practices Summary

### Do's (Make Presentations Engaging)

- ✅ Use research-lookup to find 8-15 papers for citations
- ✅ Add HIGH-QUALITY visuals to EVERY slide (figures, images, diagrams, icons)
- ✅ Choose MODERN color palette reflecting your topic (not defaults)
- ✅ Keep text MINIMAL (3-4 bullets, 4-6 words each)
- ✅ Use LARGE fonts (24-28pt body, 36-44pt titles)
- ✅ Vary slide layouts (full-figure, two-column, visual overlays)
- ✅ Maintain high contrast (7:1 preferred)
- ✅ Generous white space (40-50% of slide)
- ✅ Cite papers in intro and discussion (establish credibility)
- ✅ Test readability from distance
- ✅ Validate visually before presenting

### Don'ts (Avoid Dry Presentations)

- ❌ Don't create text-only slides (add visuals to EVERY slide)
- ❌ Don't use default themes unchanged (customize for your topic)
- ❌ Don't have all bullet-point slides (vary layouts)
- ❌ Don't skip research-lookup (presentations need citations too)
- ❌ Don't cram too much text on one slide
- ❌ Don't use tiny fonts (<24pt for body)
- ❌ Don't rely solely on color
- ❌ Don't use complex animations
- ❌ Don't mix too many font styles
- ❌ Don't ignore accessibility
- ❌ Don't skip visual validation

## Accessibility Considerations

**Color Contrast**:
- Use WebAIM contrast checker
- Minimum 4.5:1 for normal text
- Preferred 7:1 for optimal readability

**Color Blindness**:
- Test with Coblis simulator
- Use patterns/shapes with colors
- Avoid red-green combinations

**Readability**:
- Sans-serif fonts only
- Minimum 18pt, prefer 24pt+
- Clear visual hierarchy
- Adequate spacing

## Integration with Other Skills

**With Scientific Writing**:
- Convert paper content to slides
- Simplify dense text
- Extract key findings
- Create visual abstracts

**With Data Visualization**:
- Simplify journal figures
- Recreate with larger labels
- Use progressive disclosure
- Emphasize key results

**With Research Lookup**:
- Find relevant papers
- Extract key citations
- Build background context
- Support claims with evidence

## Resources

**PowerPoint Tutorials**:
- Microsoft PowerPoint documentation
- PowerPoint design templates
- Scientific presentation examples

**Design Tools**:
- Color palette generators (Coolors.co)
- Contrast checkers (WebAIM)
- Icon libraries (Noun Project)
- Image editing (PowerPoint built-in, external tools)

**PPTX Skill Documentation**:
- `document-skills/pptx/SKILL.md`: Main documentation
- `document-skills/pptx/html2pptx.md`: HTML to PPTX workflow
- `document-skills/pptx/ooxml.md`: Advanced editing
- `document-skills/pptx/scripts/`: Utility scripts

## Quick Reference

### Common Slide Dimensions

- **16:9 aspect ratio**: 10" × 5.625" (720pt × 405pt)
- **4:3 aspect ratio**: 10" × 7.5" (720pt × 540pt)

### Measurement Units

- PowerPoint uses inches
- 72 points = 1 inch
- Position (x, y) from top-left corner
- Size (w, h) for width and height

### Font Size Guidelines

| Element | Minimum | Recommended |
|---------|---------|-------------|
| Title slide | 40pt | 44-54pt |
| Slide title | 28pt | 32-40pt |
| Body text | 18pt | 24-28pt |
| Caption | 14pt | 16-20pt |
| Footer | 10pt | 10-12pt |

### Color Usage

- **Backgrounds**: White or very light colors
- **Text**: Dark (black/dark gray) on light, or white on dark
- **Accents**: One or two accent colors max
- **Data**: Color-blind safe palettes (blue/orange)

## Troubleshooting

**Problem**: Text appears cut off
- **Solution**: Increase text box size or reduce font size

**Problem**: Figures are blurry
- **Solution**: Use higher resolution images (300 DPI)

**Problem**: Colors look different when projected
- **Solution**: Test with projector beforehand, use high contrast

**Problem**: File size too large
- **Solution**: Compress images, reduce image resolution

**Problem**: Animations not working
- **Solution**: Check PowerPoint version compatibility

## Conclusion

Effective PowerPoint presentations for science require:
1. Clear, simple design
2. Readable text (24pt+ body)
3. High-quality figures
4. Consistent formatting
5. Visual validation
6. Accessibility considerations

Use the pptx skill for programmatic creation and the visual review workflow to ensure professional quality before presenting.

### `assets/timing_guidelines.md`

# Presentation Timing Guidelines

## Overview

Proper timing is critical for professional scientific presentations. This guide provides detailed guidelines for slide counts, time allocation, pacing strategies, and practice techniques to ensure your presentation fits the allotted time while maintaining engagement and clarity.

## The One-Slide-Per-Minute Rule

### Basic Guideline

**Rule of Thumb**: Plan for approximately 1 slide per minute of presentation time.

**Why It Works**:
- Allows adequate time to explain each concept
- Accounts for transitions and questions
- Provides buffer for variations in pace
- Industry-standard baseline for planning

**Adjustments**:
- **Complex slides** (data-heavy, detailed figures): 2-3 minutes each
- **Simple slides** (title, section dividers): 15-30 seconds each
- **Key result slides**: 2-4 minutes each
- **Build slides** (animations): Count as multiple slides

### Slide Count by Talk Length

| Duration | Total Slides | Title/Intro | Methods | Results | Discussion | Conclusion |
|----------|--------------|-------------|---------|---------|------------|------------|
| 5 min    | 5-7          | 1-2         | 0-1     | 2-3     | 1          | 1          |
| 10 min   | 10-12        | 2           | 1-2     | 4-5     | 2-3        | 1          |
| 15 min   | 15-18        | 2-3         | 2-3     | 6-8     | 3-4        | 1-2        |
| 20 min   | 20-24        | 3           | 3-4     | 8-10    | 4-5        | 2          |
| 30 min   | 25-30        | 3-4         | 5-6     | 10-12   | 6-8        | 2          |
| 45 min   | 35-45        | 4-5         | 8-10    | 15-20   | 8-10       | 2-3        |
| 60 min   | 45-60        | 5-6         | 10-12   | 20-25   | 10-12      | 3-4        |

### Exceptions to the Rule

**When to Use More Slides**:
- Many simple concepts to cover
- Highly visual presentation (minimal text)
- Progressive builds (each build = new "slide")
- Fast-paced overview talks

**When to Use Fewer Slides**:
- Deep dive into few concepts
- Complex data visualizations
- Interactive discussions expected
- Technical/mathematical content

## Time Allocation by Section

### 15-Minute Conference Talk (Standard)

**Total: 15 minutes, 15-18 slides**

```
Introduction (2-3 minutes, 2-3 slides):
├─ Title slide: 30 seconds
├─ Hook/Background: 90 seconds
└─ Research question: 60 seconds

Methods (2-3 minutes, 2-3 slides):
├─ Study design: 60-90 seconds
├─ Key procedures: 60 seconds
└─ Analysis: 30-60 seconds

Results (6-7 minutes, 6-8 slides):
├─ Result 1: 2-3 minutes (2-3 slides)
├─ Result 2: 2 minutes (2 slides)
└─ Result 3: 2 minutes (2-3 slides)

Discussion (2-3 minutes, 3-4 slides):
├─ Interpretation: 60 seconds
├─ Prior work: 60 seconds
└─ Implications: 60 seconds

Conclusion (1 minute, 1-2 slides):
├─ Key takeaways: 45 seconds
└─ Acknowledgments: 15 seconds

Buffer: 1-2 minutes for transitions and variation
```

**Key Principle**: Spend 40-50% of time on results.

### 45-Minute Seminar

**Total: 45 minutes, 35-45 slides**

```
Introduction (8-10 minutes, 8-10 slides):
├─ Title and personal intro: 1 minute
├─ Big picture: 3-4 minutes
├─ Literature review: 3-4 minutes
├─ Research questions: 1-2 minutes
└─ Roadmap: 1 minute

Methods (8-10 minutes, 8-10 slides):
├─ Design with rationale: 2-3 minutes
├─ Participants/materials: 2 minutes
├─ Procedures: 3-4 minutes
└─ Analysis approach: 2 minutes

Results (18-22 minutes, 16-20 slides):
├─ Overview: 2 minutes
├─ Main finding 1: 6-8 minutes
├─ Main finding 2: 6-8 minutes
├─ Additional analyses: 4-6 minutes
└─ Summary: 1 minute

Discussion (10-12 minutes, 8-10 slides):
├─ Summary: 2 minutes
├─ Literature comparison: 3-4 minutes
├─ Mechanisms: 2-3 minutes
├─ Limitations: 2 minutes
└─ Implications: 2 minutes

Conclusion (2-3 minutes, 2-3 slides):
├─ Key messages: 1 minute
├─ Future directions: 1-2 minutes
└─ Acknowledgments: 30 seconds

Reserve: 5-10 minutes for Q&A or discussion
```

### Lightning Talk (5 Minutes)

**Total: 5 minutes, 5-7 slides**

```
Slide 1: Title (15 seconds)
Slide 2: The Problem (45 seconds)
Slide 3: Your Solution (60 seconds)
Slide 4-5: Key Result (2-3 minutes total)
Slide 6: Impact/Implications (45 seconds)
Slide 7: Conclusion + Contact (30 seconds)
```

**Critical**: Practice exact timing. No buffer room.

## Timing Each Slide

### Simple Slides

**Title/Section Dividers** (15-30 seconds):
- Say title
- Brief transition comment
- Move on quickly

**Single Bullet Point Slides** (30-45 seconds):
- Read or paraphrase point
- Provide 1-2 sentences of explanation
- Transition to next

### Standard Content Slides

**Bullet Point Slides** (1-2 minutes):
- 3-4 bullets: ~1 minute
- 5-6 bullets: ~2 minutes
- **Strategy**:
  - Don't read bullets verbatim
  - Explain each point (15-20 seconds per bullet)
  - Use builds to control pacing

**Equation Slides** (1-2 minutes):
- Introduce equation context (20 seconds)
- Explain each term (40 seconds)
- Discuss implications (20-40 seconds)

### Complex Slides

**Data Visualization Slides** (2-3 minutes):
```
30 seconds: Set up (what you're showing)
60 seconds: Walk through key patterns
30 seconds: Highlight main finding
30 seconds: Statistical results
30 seconds: Interpretation/transition
```

**Multi-Panel Figures** (2-4 minutes):
```
Option 1 - Progressive Build:
- Show panel 1: 60 seconds
- Add panel 2: 60 seconds  
- Add panel 3: 60 seconds
- Integrate: 60 seconds

Option 2 - All at Once:
- Overview: 30 seconds
- Panel 1: 60 seconds
- Panel 2: 60 seconds
- Panel 3: 60 seconds
- Integration: 30 seconds
```

**Table Slides** (1-2 minutes):
- Don't read every cell
- Guide attention: "Notice the top row..."
- Highlight key comparison
- State statistical result

## Pacing Strategies

### Maintaining Steady Pace

**Natural Checkpoints** (Use these to self-monitor):

For 15-minute talk:
- **3-4 minutes**: Should be finishing introduction
- **7-8 minutes**: Should be halfway through results
- **12-13 minutes**: Should be starting conclusions

For 45-minute talk:
- **10 minutes**: Finishing introduction
- **20 minutes**: Halfway through methods
- **35 minutes**: Finishing results
- **40 minutes**: In discussion

### Signs You're Running Behind

- Rushing through slides
- Skipping explanations
- Feeling time pressure
- Glancing at clock frequently
- Audience looking confused

**Recovery Strategies**:
1. Skip backup/secondary slides (prepare these in advance)
2. Summarize instead of detailing
3. Cut discussion, not results
4. NEVER skip conclusions

### Signs You're Ahead of Schedule

- Finishing slides too quickly
- Running out of things to say
- Awkward pauses
- Reaching conclusion with time left

**Adjustment Strategies**:
1. Expand on key points naturally
2. Provide additional examples
3. Take questions mid-talk (if appropriate)
4. Slow down slightly (don't add filler)

## Practice Techniques

### Practice Schedule

**Minimum Practice Requirements**:

| Talk Type | Practice Runs | Time Commitment |
|-----------|--------------|-----------------|
| Lightning (5 min) | 5-7 times | 3 hours |
| Conference (15 min) | 3-5 times | 4-5 hours |
| Seminar (45 min) | 3-4 times | 6-8 hours |
| Defense (60 min) | 4-6 times | 10-15 hours |

### Practice Progression

**Run 1: Rough Draft**
- Focus: Get through all slides
- Time it (will likely run long)
- Identify problem areas
- Note where you stumble

**Run 2: Smoothing**
- Focus: Improve transitions
- Practice specific wording
- Time each section
- Start cutting if over time

**Run 3: Refinement**
- Focus: Exact timing
- Practice with timer visible
- Implement timing strategies
- Fine-tune explanations

**Run 4: Final Polish**
- Focus: Delivery quality
- Record yourself (video)
- Practice Q&A scenarios
- Perfect timing

**Run 5+: Maintenance**
- Day before talk
- Morning of talk (if time)
- Just opening and closing

### Practice Methods

**Solo Practice**:
```
1. Full talk with timer
2. Section-by-section focus
3. Speak aloud (not mental review)
4. Stand and use gestures
5. Simulate presentation environment
```

**Recorded Practice**:
```
1. Video yourself
2. Watch playback critically
3. Note:
   - Timing issues
   - Filler words ("um", "uh", "like")
   - Body language
   - Pace variations
4. Re-record after improvements
```

**Live Audience Practice**:
```
1. Lab meeting or colleagues
2. Request honest feedback
3. Take questions
4. Time strictly
5. Note:
   - Confusing sections
   - Questions asked
   - Engagement level
```

### Timing Tools

**During Practice**:
- Phone timer (visible)
- Stopwatch with lap times
- Timer app with alerts
- Record for later analysis

**During Presentation**:
- Phone/watch timer (subtle glances)
- Session clock (if provided)
- Time notes on slides (bottom corner)
- Vibrating watch alerts at key checkpoints

**Timing Notes on Slides**:
```
Add small text (8pt, corner):
Slide 1: "0:00"
Slide 5: "3:30"
Slide 10: "7:00"
Slide 15: "12:00"
Slide 18: "14:00"
```

## Handling Time Constraints

### If Time is Cut Short

**Scenario**: "We're running behind, can you cut to 10 minutes?"

**Strategy**:
1. Keep introduction (brief)
2. Mention methods (30 seconds)
3. Show main result only (3 minutes)
4. Brief conclusion (30 seconds)
5. Skip: Secondary results, detailed discussion

**Pre-Prepare**:
- Know which slides are "must keep"
- Mark "optional" slides
- Have 5, 10, and 15-minute versions ready

### If Given Extra Time

**Scenario**: "Previous speaker cancelled, you have 30 minutes instead of 15"

**Options**:
1. Go deeper on key results
2. Show backup slides
3. Include additional analyses
4. Extend discussion
5. Allow more Q&A time

**Don't**:
- Repeat content
- Add filler
- Slow down artificially
- Include low-quality material

## Question and Answer Timing

### Including Q&A in Your Time

**If Q&A is within your slot**:
- Plan for 20-30% of time for questions
- 15-minute talk: Reserve 3-4 minutes
- 45-minute talk: Reserve 10-15 minutes
- Finish content 2-3 minutes early

**Q&A Time Management**:
- Brief answers (30-90 seconds each)
- "Great question, let me keep this brief..."
- Redirect detailed questions: "Let's discuss after"
- Moderator or self-police time

### Separate Q&A Time

**If Q&A is after your slot**:
- Use full allotted time
- Finish exactly at time limit
- Don't assume extra time
- Have backup slides ready

## Time Budgeting Template

### Create Your Own Timing Plan

```
Talk Title: _______________________
Total Duration: ____ minutes
Target Slides: ____ slides

Introduction:
- Slide 1: Title (__:__ - __:__)
- Slide 2: Hook (__:__ - __:__)
- Slide 3: Background (__:__ - __:__)
[Continue for all slides...]

CHECKPOINT: By __:__, should be at Slide ___

Methods:
- Slide __: [description] (__:__ - __:__)
[...]

CHECKPOINT: By __:__, should be at Slide ___

Results:
[...]

[Continue for all sections]

Total Planned Time: ____
Buffer: ____ minutes
```

### Example Timing Sheet

```
15-Minute Conference Talk
Target: 15:00, Slides: 1-18

00:00 - 00:30 | Slide 1  | Title
00:30 - 02:00 | Slide 2  | Background
02:00 - 03:00 | Slide 3  | Research question
------CHECKPOINT: 3 min, Slide 3------
03:00 - 04:00 | Slide 4  | Study design
04:00 - 05:00 | Slide 5  | Methods
05:00 - 05:30 | Slide 6  | Analysis
------CHECKPOINT: 5:30, Slide 6------
05:30 - 08:00 | Slide 7-8 | Main result
08:00 - 10:00 | Slide 9-10 | Result 2
10:00 - 11:30 | Slide 11-12 | Result 3
------CHECKPOINT: 11:30, Slide 12------
11:30 - 12:30 | Slide 13-14 | Discussion
12:30 - 13:30 | Slide 15-16 | Implications
13:30 - 14:30 | Slide 17 | Conclusions
14:30 - 15:00 | Slide 18 | Acknowledgments
------END: 15:00------
```

## Common Timing Mistakes

### Mistake 1: Over-Preparing Introduction

**Problem**: Spending 5 minutes of 15-minute talk on background

**Solution**:
- Limit intro to 15-20% of total time
- Jump to your contribution quickly
- Save detailed review for discussion

### Mistake 2: Equal Time Per Slide

**Problem**: Spending same time on title slide as key result

**Solution**:
- Vary pace based on importance
- Rush through simple slides
- Linger on key findings

### Mistake 3: No Time Checkpoints

**Problem**: Realizing you're behind only at minute 12 of 15

**Solution**:
- Set 3-4 checkpoints
- Glance at timer regularly
- Adjust in real-time

### Mistake 4: Skipping Practice

**Problem**: First time through is during actual presentation

**Solution**:
- Practice minimum 3 times
- Time each practice
- Get feedback

### Mistake 5: Not Preparing Plan B

**Problem**: Run over time with no strategy

**Solution**:
- Know which slides to skip
- Have condensed versions ready
- Practice shortened version

## Special Timing Considerations

### Virtual Presentations

**Adjustments**:
- Slightly slower pace (5-10%)
- More explicit transitions
- Built-in pauses for lag
- Buffer for technical issues

**Time Allocation**:
- Start 1-2 minutes early (tech check)
- More time for Q&A (typing delays)
- Share slides in advance if possible

### Poster Spotlight Talks (3 Minutes)

**Ultra-Tight Timing**:
```
0:00-0:30 | Title + Context
0:30-1:30 | Problem + Approach
1:30-2:30 | Key Result (one figure)
2:30-3:00 | "Visit poster #42"
```

**Practice**: 10+ times to get exactly right

### Invited Talks (45-60 Minutes)

**More Flexibility**:
- Can adjust pace based on audience
- Welcome interruptions
- Conversational style acceptable
- Less rigid timing

**Still Important**:
- Have overall time structure
- Monitor major checkpoints
- Respect Q&A time

## Summary: Key Timing Principles

1. **Plan for 1 slide per minute** (adjust for complexity)
2. **Spend 40-50% on results**
3. **Practice 3-5 times minimum**
4. **Set 3-4 time checkpoints**
5. **Have Plan B for running over**
6. **Never skip conclusions**
7. **Finish on time** (non-negotiable)

## Quick Reference Card

```
PRESENTATION TIMING CHEAT SHEET

General Rule: 1 slide = 1 minute

Section Time Allocation (15-min talk):
├─ Intro: 2-3 min (20%)
├─ Methods: 2-3 min (15-20%)
├─ Results: 6-7 min (45%)
├─ Discussion: 2-3 min (15%)
└─ Conclusion: 1 min (5%)

Practice Schedule:
├─ Run 1: Rough (expect to run long)
├─ Run 2: Smooth (fix transitions)
├─ Run 3: Timed (hit targets)
└─ Run 4+: Polish (perfect delivery)

Checkpoints (15-min talk):
├─ 3-4 min: End of intro
├─ 7-8 min: Halfway through results
└─ 12-13 min: Starting conclusions

Emergency Strategies:
├─ Running over? Skip backup slides
├─ Running under? Expand examples
├─ Lost? Return to time checkpoints
└─ Technical issue? Verbal summary

Remember: Better to finish early than run over!
```
