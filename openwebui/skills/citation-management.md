---
name: citation-management
description: Contact email for the faster OpenAlex polite pool.
---

# Citation Management

## Overview

Manage citations systematically throughout the research and writing process. This skill provides tools and strategies for searching academic databases (Google Scholar, PubMed), extracting accurate metadata from multiple sources (CrossRef, PubMed, arXiv), validating citation information, and generating properly formatted BibTeX entries.

Critical for maintaining citation accuracy, avoiding reference errors, and ensuring reproducible research. Integrates seamlessly with the literature-review skill for comprehensive research workflows.

## When to Use This Skill

Use this skill when:
- Searching for specific papers on Google Scholar or PubMed
- Converting DOIs, PMIDs, or arXiv IDs to properly formatted BibTeX
- Extracting complete metadata for citations (authors, title, journal, year, etc.)
- Validating existing citations for accuracy
- Cleaning and formatting BibTeX files
- Finding highly cited papers in a specific field
- Verifying that citation information matches the actual publication
- Building a bibliography for a manuscript or thesis
- Checking for duplicate citations
- Ensuring consistent citation formatting

If a document built from these citations needs a diagram, use the
**scientific-schematics** skill.

---

## Core Workflow

Citation management follows a systematic process. Each phase below shows the canonical
command; every variant, option, and metadata-source detail is in
[references/core_workflow.md](references/core_workflow.md).

### Phase 1: Paper Discovery and Search

Find relevant papers. Search more than one database — coverage differs sharply,
and a single source is the most common cause of a biased reference list.

```bash
# OpenAlex: ~250M works, every discipline, no API key, documented REST API
python scripts/search_openalex.py "CRISPR gene editing" --limit 50 --output results.json

# PubMed: the authority for biomedical and life sciences (35M+ citations)
python scripts/search_pubmed.py "Alzheimer's disease treatment" --limit 100 --output alz.json

# Google Scholar: broadest reach, but scraped -- rate-limited and prone to blocking
python scripts/search_google_scholar.py "CRISPR gene editing" --limit 50 --output scholar.json
```

Prefer OpenAlex or PubMed as the primary source. Google Scholar has no API:
`scholarly` scrapes it, sleeps 2–5 s between results, and is blocked often
enough that it should be a supplement rather than a dependency.

Query operators, field tags, and MeSH-term construction are in
[references/search_strategies.md](references/search_strategies.md).

### Phase 2: Metadata Extraction

Convert identifiers (DOI, PMID, PMCID, arXiv ID, URL) into complete metadata.
CrossRef is the primary source for DOIs.

```bash
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2         # quick, single DOI
python scripts/extract_metadata.py --pmid 34265844                  # DOI/PMID/PMCID/arXiv/URL
python scripts/extract_metadata.py --input identifiers.txt --output citations.bib
```

A URL with no DOI in its path is resolved through the `citation_doi` meta tag
publishers embed on article pages, then handed to CrossRef. Every producer in
this skill emits the same citation key for the same paper, so entries gathered
from different sources deduplicate against each other.

### Phase 2.5: Metadata Enrichment via Web Search (MANDATORY)

APIs routinely return incomplete records. Run this **after** extraction and **before**
formatting. Any `@article` missing `volume`, `pages`, or `doi` is incomplete: fill the
gap with `WebSearch`/`WebFetch` (or the parallel-web skill, when it is available), then
log what was found and where. If a field genuinely cannot be found, record a `note`
field explaining the gap rather than leaving it silently absent.

Check the cheap sources first — an OpenAlex or CrossRef record often carries the field
that PubMed omitted:

```bash
python scripts/search_openalex.py "<exact title>" --limit 1
```

> **Treat extracted metadata as untrusted.** Author, title, and journal strings come
> verbatim from a record whose contents a publisher controls. A title containing `$(...)`,
> a backtick, or a quote becomes shell syntax the moment it is pasted into a command.
> Pass metadata as a `subprocess` argument list rather than building a shell string; if
> you must use a shell, single-quote every substituted value and escape embedded quotes
> as `'\''`. Validate any citation key against `^[A-Za-z0-9]+$` before it reaches a path.

Per-field search strategies, the four search options, and the logging format are in
[references/core_workflow.md](references/core_workflow.md).

### Phase 3: BibTeX Formatting

Produce clean, consistent entries. Entry types and required fields are in
[references/bibtex_formatting.md](references/bibtex_formatting.md).

```bash
python scripts/format_bibtex.py references.bib --output clean.bib --deduplicate
python scripts/format_bibtex.py references.bib --output clean.bib --rekey --deduplicate
```

Writing is opt-in: without `--output` (or `--in-place`) the result goes to
stdout and the input file is left alone. Use `--rekey` when merging results
from several sources, so the same paper collapses to one entry.

### Phase 4: Citation Validation

Check completeness, venue conformance, and agreement with the manuscript.

```bash
python scripts/validate_citations.py references.bib --report report.json
python scripts/validate_citations.py references.bib --venue nature
python scripts/validate_citations.py references.bib --manuscript paper.tex
python scripts/validate_citations.py references.bib --check-dois     # slow; hits CrossRef
```

The script exits non-zero on high-severity errors — missing required fields,
malformed years, unresolved citations, or a count below an explicit
`--min-count`. Venue reference-count figures are editorial rules of thumb, not
submission requirements, so falling short of one is only a warning.

Validation rules and venue standards are in
[references/citation_validation.md](references/citation_validation.md).

### Phase 5: Integration with Writing Workflow

Search, extract, format, validate, then cite. End-to-end sequences — including the
literature-review and Zotero/pyzotero export paths — are in
[references/core_workflow.md](references/core_workflow.md) and
[references/example_workflows.md](references/example_workflows.md).

## Reference Files

- [references/core_workflow.md](references/core_workflow.md): all five phases in full.
- [references/search_strategies.md](references/search_strategies.md): OpenAlex, Google Scholar, and PubMed query construction.
- [references/script_reference.md](references/script_reference.md): every bundled script's arguments and examples.
- [references/best_practices.md](references/best_practices.md): search, extraction, BibTeX quality, validation.
- [references/example_workflows.md](references/example_workflows.md): four end-to-end worked examples.
- [references/google_scholar_search.md](references/google_scholar_search.md), [references/pubmed_search.md](references/pubmed_search.md): advanced search syntax.
- [references/metadata_extraction.md](references/metadata_extraction.md), [references/bibtex_formatting.md](references/bibtex_formatting.md), [references/citation_validation.md](references/citation_validation.md): per-topic detail.

## Common Pitfalls to Avoid

1. **Single source bias**: Only using one database
   - **Solution**: Search at least OpenAlex and PubMed, then merge with
     `format_bibtex.py --rekey --deduplicate`

2. **Accepting metadata blindly**: Not verifying extracted information
   - **Solution**: Spot-check extracted metadata against original sources

3. **Ignoring DOI errors**: Broken or incorrect DOIs in bibliography
   - **Solution**: Run validation before final submission

4. **Inconsistent formatting**: Mixed citation key styles, formatting
   - **Solution**: Use format_bibtex.py to standardize

5. **Duplicate entries**: Same paper cited multiple times with different keys
   - **Solution**: Use duplicate detection in validation

6. **Missing required fields**: Incomplete BibTeX entries (volume, pages, DOI missing)
   - **Solution**: Run Phase 2.5 metadata enrichment — web search for every missing field before proceeding. NEVER leave an @article entry without volume, pages, and DOI.

7. **Outdated preprints**: Citing preprint when published version exists
   - **Solution**: Check if preprints have been published, update to journal version

8. **Special character issues**: Broken LaTeX compilation due to characters
   - **Solution**: Use proper escaping or Unicode in BibTeX

9. **No validation before submission**: Submitting with citation errors
   - **Solution**: Always run validation as final check

10. **Manual BibTeX entry**: Typing entries by hand
    - **Solution**: Always extract from metadata sources using scripts

## Integration with Other Skills

### Literature Review Skill

**Citation Management** provides the technical infrastructure for **Literature Review**:

- **Literature Review**: Multi-database systematic search and synthesis
- **Citation Management**: Metadata extraction and validation

**Combined workflow**:
1. Use literature-review for systematic search methodology
2. Use citation-management to extract and validate citations
3. Use literature-review to synthesize findings
4. Use citation-management to ensure bibliography accuracy

### Scientific Writing Skill

**Citation Management** ensures accurate references for **Scientific Writing**:

- Export validated BibTeX for use in LaTeX manuscripts
- Verify citations match publication standards
- Format references according to journal requirements

### Venue Templates Skill

**Citation Management** works with **Venue Templates** for submission-ready manuscripts:

- Different venues require different citation styles
- Generate properly formatted references
- Validate citations meet venue requirements

## Resources

### Bundled Resources

**References** (in `references/`):
- `google_scholar_search.md`: Complete Google Scholar search guide
- `pubmed_search.md`: PubMed and E-utilities API documentation
- `metadata_extraction.md`: Metadata sources and field requirements
- `citation_validation.md`: Validation criteria and quality checks
- `bibtex_formatting.md`: BibTeX entry types and formatting rules

**Scripts** (in `scripts/`):
- `search_openalex.py`: OpenAlex search client (no API key)
- `search_pubmed.py`: PubMed E-utilities API client
- `search_google_scholar.py`: Google Scholar search automation
- `extract_metadata.py`: Universal metadata extractor
- `validate_citations.py`: Citation validation and verification
- `format_bibtex.py`: BibTeX formatter and cleaner
- `doi_to_bibtex.py`: Quick DOI to BibTeX converter
- `_common.py`: shared BibTeX parser, renderer, and citation-key scheme

**Assets** (in `assets/`):
- `bibtex_template.bib`: Example BibTeX entries for all types
- `citation_checklist.md`: Quality assurance checklist

### External Resources

**Search Engines**:
- OpenAlex: https://openalex.org/
- Google Scholar: https://scholar.google.com/
- PubMed: https://pubmed.ncbi.nlm.nih.gov/
- PubMed Advanced Search: https://pubmed.ncbi.nlm.nih.gov/advanced/

**Metadata APIs**:
- OpenAlex API: https://docs.openalex.org/
- CrossRef API: https://api.crossref.org/
- PubMed E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- arXiv API: https://arxiv.org/help/api/
- DataCite API: https://api.datacite.org/

**Tools and Validators**:
- MeSH Browser: https://meshb.nlm.nih.gov/search
- DOI Resolver: https://doi.org/
- BibTeX Format: http://www.bibtex.org/Format/

**Citation Styles**:
- BibTeX documentation: http://www.bibtex.org/
- LaTeX bibliography management: https://www.overleaf.com/learn/latex/Bibliography_management

## Dependencies

### Required Python Packages

```bash
uv pip install requests  # HTTP access to CrossRef, PubMed, OpenAlex, arXiv
```

BibTeX parsing, rendering, deduplication, and validation are standard library
(`scripts/_common.py`), so `format_bibtex.py` and `validate_citations.py` run
with no third-party packages at all.

### Optional

```bash
uv pip install scholarly  # only for search_google_scholar.py
```

### Where credentials are sent

This skill needs no API key. The two environment variables it reads are
optional identifiers, each sent to the one service it belongs to and nowhere
else; no script bundles environment variables together.

| Variable | Sent only to | Purpose |
|---|---|---|
| `NCBI_API_KEY` | `eutils.ncbi.nlm.nih.gov` | Raises Entrez rate limits |
| `NCBI_EMAIL` | `eutils.ncbi.nlm.nih.gov` | Entrez caller identification (requested by NCBI) |
| `OPENALEX_EMAIL` | `api.openalex.org` | Joins the faster OpenAlex polite pool |

`api.openalex.org`, `api.crossref.org`, `api.datacite.org`, `export.arxiv.org`,
and `eutils.ncbi.nlm.nih.gov` are all queried without credentials when these are
unset.

## Summary

The citation-management skill provides:

1. **Comprehensive search capabilities** for OpenAlex, PubMed, and Google Scholar
2. **Automated metadata extraction** from DOI, PMID, PMCID, arXiv ID, URLs
3. **Citation validation** with DOI verification and completeness checking
4. **BibTeX formatting** with standardization and cleaning tools
5. **Quality assurance** through validation and reporting
6. **Integration** with scientific writing workflow
7. **Reproducibility** through documented search and extraction methods

Use this skill to maintain accurate, complete citations throughout your research and ensure publication-ready bibliographies.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/citation-management/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/best_practices.md`

# Best Practices

Search strategy, metadata extraction, BibTeX quality, and validation practices.

## Best Practices

### Search Strategy

1. **Start broad, then narrow**:
   - Begin with general terms to understand the field
   - Refine with specific keywords and filters
   - Use synonyms and related terms

2. **Use multiple sources**:
   - Google Scholar for comprehensive coverage
   - PubMed for biomedical focus
   - arXiv for preprints
   - Combine results for completeness

3. **Leverage citations**:
   - Check "Cited by" for seminal papers
   - Review references from key papers
   - Use citation networks to discover related work

4. **Document your searches**:
   - Save search queries and dates
   - Record number of results
   - Note any filters or restrictions applied

### Metadata Extraction

1. **Always use DOIs when available**:
   - Most reliable identifier
   - Permanent link to the publication
   - Best metadata source via CrossRef

2. **Verify extracted metadata**:
   - Check author names are correct
   - Verify journal/conference names
   - Confirm publication year
   - Validate page numbers and volume

3. **Handle edge cases**:
   - Preprints: Include repository and ID
   - Preprints later published: Use published version
   - Conference papers: Include conference name and location
   - Book chapters: Include book title and editors

4. **Maintain consistency**:
   - Use consistent author name format
   - Standardize journal abbreviations
   - Use same DOI format (URL preferred)

### BibTeX Quality

1. **Follow conventions**:
   - Use meaningful citation keys (FirstAuthor2024keyword)
   - Protect capitalization in titles with {}
   - Use -- for page ranges (not single dash)
   - Include DOI field for all modern publications

2. **Keep it clean**:
   - Remove unnecessary fields
   - No redundant information
   - Consistent formatting
   - Validate syntax regularly

3. **Organize systematically**:
   - Sort by year or topic
   - Group related papers
   - Use separate files for different projects
   - Merge carefully to avoid duplicates

### Validation

1. **Validate early and often**:
   - Check citations when adding them
   - Validate complete bibliography before submission
   - Re-validate after any manual edits

2. **Fix issues promptly**:
   - Broken DOIs: Find correct identifier
   - Missing fields: Extract from original source
   - Duplicates: Choose best version, remove others
   - Format errors: Use auto-fix when safe

3. **Manual review for critical citations**:
   - Verify key papers cited correctly
   - Check author names match publication
   - Confirm page numbers and volume
   - Ensure URLs are current

### `references/bibtex_formatting.md`

# BibTeX Formatting Guide

Comprehensive guide to BibTeX entry types, required fields, formatting conventions, and best practices.

## Overview

BibTeX is the standard bibliography format for LaTeX documents. Proper formatting ensures:
- Correct citation rendering
- Consistent formatting
- Compatibility with citation styles
- No compilation errors

This guide covers all common entry types and formatting rules.

## Entry Types

### @article - Journal Articles

**Most common entry type** for peer-reviewed journal articles.

**Required fields**:
- `author`: Author names
- `title`: Article title
- `journal`: Journal name
- `year`: Publication year

**Optional fields**:
- `volume`: Volume number
- `number`: Issue number
- `pages`: Page range
- `month`: Publication month
- `doi`: Digital Object Identifier
- `url`: URL
- `note`: Additional notes

**Template**:
```bibtex
@article{CitationKey2024,
  author  = {Last1, First1 and Last2, First2},
  title   = {Article Title Here},
  journal = {Journal Name},
  year    = {2024},
  volume  = {10},
  number  = {3},
  pages   = {123--145},
  doi     = {10.1234/journal.2024.123456},
  month   = jan
}
```

**Example**:
```bibtex
@article{Jumper2021,
  author  = {Jumper, John and Evans, Richard and Pritzel, Alexander and others},
  title   = {Highly Accurate Protein Structure Prediction with {AlphaFold}},
  journal = {Nature},
  year    = {2021},
  volume  = {596},
  number  = {7873},
  pages   = {583--589},
  doi     = {10.1038/s41586-021-03819-2}
}
```

### @book - Books

**For entire books**.

**Required fields**:
- `author` OR `editor`: Author(s) or editor(s)
- `title`: Book title
- `publisher`: Publisher name
- `year`: Publication year

**Optional fields**:
- `volume`: Volume number (if multi-volume)
- `series`: Series name
- `address`: Publisher location
- `edition`: Edition number
- `isbn`: ISBN
- `url`: URL

**Template**:
```bibtex
@book{CitationKey2024,
  author    = {Last, First},
  title     = {Book Title},
  publisher = {Publisher Name},
  year      = {2024},
  edition   = {3},
  address   = {City, Country},
  isbn      = {978-0-123-45678-9}
}
```

**Example**:
```bibtex
@book{Kumar2021,
  author    = {Kumar, Vinay and Abbas, Abul K. and Aster, Jon C.},
  title     = {Robbins and Cotran Pathologic Basis of Disease},
  publisher = {Elsevier},
  year      = {2021},
  edition   = {10},
  address   = {Philadelphia, PA},
  isbn      = {978-0-323-53113-9}
}
```

### @inproceedings - Conference Papers

**For papers in conference proceedings**.

**Required fields**:
- `author`: Author names
- `title`: Paper title
- `booktitle`: Conference/proceedings name
- `year`: Year

**Optional fields**:
- `editor`: Proceedings editor(s)
- `volume`: Volume number
- `series`: Series name
- `pages`: Page range
- `address`: Conference location
- `month`: Conference month
- `organization`: Organizing body
- `publisher`: Publisher
- `doi`: DOI

**Template**:
```bibtex
@inproceedings{CitationKey2024,
  author    = {Last, First},
  title     = {Paper Title},
  booktitle = {Proceedings of Conference Name},
  year      = {2024},
  pages     = {123--145},
  address   = {City, Country},
  month     = jun
}
```

**Example**:
```bibtex
@inproceedings{Vaswani2017,
  author    = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and others},
  title     = {Attention is All You Need},
  booktitle = {Advances in Neural Information Processing Systems 30 (NeurIPS 2017)},
  year      = {2017},
  pages     = {5998--6008},
  address   = {Long Beach, CA}
}
```

**Note**: `@conference` is an alias for `@inproceedings`.

### @incollection - Book Chapters

**For chapters in edited books**.

**Required fields**:
- `author`: Chapter author(s)
- `title`: Chapter title
- `booktitle`: Book title
- `publisher`: Publisher name
- `year`: Publication year

**Optional fields**:
- `editor`: Book editor(s)
- `volume`: Volume number
- `series`: Series name
- `type`: Type of section (e.g., "chapter")
- `chapter`: Chapter number
- `pages`: Page range
- `address`: Publisher location
- `edition`: Edition
- `month`: Month

**Template**:
```bibtex
@incollection{CitationKey2024,
  author    = {Last, First},
  title     = {Chapter Title},
  booktitle = {Book Title},
  editor    = {Editor, Last and Editor2, Last},
  publisher = {Publisher Name},
  year      = {2024},
  pages     = {123--145},
  chapter   = {5}
}
```

**Example**:
```bibtex
@incollection{Brown2020,
  author    = {Brown, Peter O. and Botstein, David},
  title     = {Exploring the New World of the Genome with {DNA} Microarrays},
  booktitle = {DNA Microarrays: A Molecular Cloning Manual},
  editor    = {Eisen, Michael B. and Brown, Patrick O.},
  publisher = {Cold Spring Harbor Laboratory Press},
  year      = {2020},
  pages     = {1--45},
  address   = {Cold Spring Harbor, NY}
}
```

### @phdthesis - Doctoral Dissertations

**For PhD dissertations and theses**.

**Required fields**:
- `author`: Author name
- `title`: Thesis title
- `school`: Institution
- `year`: Year

**Optional fields**:
- `type`: Type (e.g., "PhD dissertation", "PhD thesis")
- `address`: Institution location
- `month`: Month
- `url`: URL
- `note`: Additional notes

**Template**:
```bibtex
@phdthesis{CitationKey2024,
  author = {Last, First},
  title  = {Dissertation Title},
  school = {University Name},
  year   = {2024},
  type   = {{PhD} dissertation},
  address = {City, State}
}
```

**Example**:
```bibtex
@phdthesis{Johnson2023,
  author  = {Johnson, Mary L.},
  title   = {Novel Approaches to Cancer Immunotherapy Using {CRISPR} Technology},
  school  = {Stanford University},
  year    = {2023},
  type    = {{PhD} dissertation},
  address = {Stanford, CA}
}
```

**Note**: `@mastersthesis` is similar but for Master's theses.

### @mastersthesis - Master's Theses

**For Master's theses**.

**Required fields**:
- `author`: Author name
- `title`: Thesis title
- `school`: Institution
- `year`: Year

**Template**:
```bibtex
@mastersthesis{CitationKey2024,
  author = {Last, First},
  title  = {Thesis Title},
  school = {University Name},
  year   = {2024}
}
```

### @misc - Miscellaneous

**For items that don't fit other categories** (preprints, datasets, software, websites, etc.).

**Required fields**:
- `author` (if known)
- `title`
- `year`

**Optional fields**:
- `howpublished`: Repository, website, format
- `url`: URL
- `doi`: DOI
- `note`: Additional information
- `month`: Month

**Template for preprints**:
```bibtex
@misc{CitationKey2024,
  author       = {Last, First},
  title        = {Preprint Title},
  year         = {2024},
  howpublished = {bioRxiv},
  doi          = {10.1101/2024.01.01.123456},
  note         = {Preprint}
}
```

**Template for datasets**:
```bibtex
@misc{DatasetName2024,
  author       = {Last, First},
  title        = {Dataset Title},
  year         = {2024},
  howpublished = {Zenodo},
  doi          = {10.5281/zenodo.123456},
  note         = {Version 1.2}
}
```

**Template for software**:
```bibtex
@misc{SoftwareName2024,
  author       = {Last, First},
  title        = {Software Name},
  year         = {2024},
  howpublished = {GitHub},
  url          = {https://github.com/user/repo},
  note         = {Version 2.0}
}
```

### @techreport - Technical Reports

**For technical reports**.

**Required fields**:
- `author`: Author name(s)
- `title`: Report title
- `institution`: Institution
- `year`: Year

**Optional fields**:
- `type`: Type of report
- `number`: Report number
- `address`: Institution location
- `month`: Month

**Template**:
```bibtex
@techreport{CitationKey2024,
  author      = {Last, First},
  title       = {Report Title},
  institution = {Institution Name},
  year        = {2024},
  type        = {Technical Report},
  number      = {TR-2024-01}
}
```

### @unpublished - Unpublished Work

**For unpublished works** (not preprints - use @misc for those).

**Required fields**:
- `author`: Author name(s)
- `title`: Work title
- `note`: Description

**Optional fields**:
- `month`: Month
- `year`: Year

**Template**:
```bibtex
@unpublished{CitationKey2024,
  author = {Last, First},
  title  = {Work Title},
  note   = {Unpublished manuscript},
  year   = {2024}
}
```

### @online/@electronic - Online Resources

**For web pages and online-only content**.

**Note**: Not standard BibTeX, but supported by many bibliography packages (biblatex).

**Required fields**:
- `author` OR `organization`
- `title`
- `url`
- `year`

**Template**:
```bibtex
@online{CitationKey2024,
  author = {{Organization Name}},
  title  = {Page Title},
  url    = {https://example.com/page},
  year   = {2024},
  note   = {Accessed: 2024-01-15}
}
```

## Formatting Rules

### Citation Keys

**Convention**: `FirstAuthorYEARkeyword`

**Examples**:
```bibtex
Smith2024protein
Doe2023machine
JohnsonWilliams2024cancer  % Multiple authors, no space
NatureEditorial2024        % No author, use publication
WHO2024guidelines          % Organization author
```

**Rules**:
- Alphanumeric plus: `-`, `_`, `.`, `:`
- No spaces
- Case-sensitive
- Unique within file
- Descriptive

**Avoid**:
- Special characters: `@`, `#`, `&`, `%`, `$`
- Spaces: use CamelCase or underscores
- Starting with numbers: `2024Smith` (some systems disallow)

### Author Names

**Recommended format**: `Last, First Middle`

**Single author**:
```bibtex
author = {Smith, John}
author = {Smith, John A.}
author = {Smith, John Andrew}
```

**Multiple authors** - separate with `and`:
```bibtex
author = {Smith, John and Doe, Jane}
author = {Smith, John A. and Doe, Jane M. and Johnson, Mary L.}
```

**Many authors** (10+):
```bibtex
author = {Smith, John and Doe, Jane and Johnson, Mary and others}
```

**Special cases**:
```bibtex
% Suffix (Jr., III, etc.)
author = {King, Jr., Martin Luther}

% Organization as author
author = {{World Health Organization}}
% Note: Double braces keep as single entity

% Multiple surnames
author = {Garc{\'i}a-Mart{\'i}nez, Jos{\'e}}

% Particles (van, von, de, etc.)
author = {van der Waals, Johannes}
author = {de Broglie, Louis}
```

**Wrong formats** (don't use):
```bibtex
author = {Smith, J.; Doe, J.}  % Semicolons (wrong)
author = {Smith, J., Doe, J.}  % Commas (wrong)
author = {Smith, J. & Doe, J.} % Ampersand (wrong)
author = {Smith J}             % No comma
```

### Title Capitalization

**Protect capitalization** with braces:

```bibtex
% Proper nouns, acronyms, formulas
title = {{AlphaFold}: Protein Structure Prediction}
title = {Machine Learning for {DNA} Sequencing}
title = {The {Ising} Model in Statistical Physics}
title = {{CRISPR-Cas9} Gene Editing Technology}
```

**Reason**: Citation styles may change capitalization. Braces protect.

**Examples**:
```bibtex
% Good
title = {Advances in {COVID-19} Treatment}
title = {Using {Python} for Data Analysis}
title = {The {AlphaFold} Protein Structure Database}

% Will be lowercase in title case styles
title = {Advances in COVID-19 Treatment}  % covid-19
title = {Using Python for Data Analysis}  % python
```

**Whole title protection** (rarely needed):
```bibtex
title = {{This Entire Title Keeps Its Capitalization}}
```

### Page Ranges

**Use en-dash** (double hyphen `--`):

```bibtex
pages = {123--145}     % Correct
pages = {1234--1256}   % Correct
pages = {e0123456}     % Article ID (PLOS, etc.)
pages = {123}          % Single page
```

**Wrong**:
```bibtex
pages = {123-145}      % Single hyphen (don't use)
pages = {pp. 123-145}  % "pp." not needed
pages = {123–145}      % Unicode en-dash (may cause issues)
```

### Month Names

**Use three-letter abbreviations** (unquoted):

```bibtex
month = jan
month = feb
month = mar
month = apr
month = may
month = jun
month = jul
month = aug
month = sep
month = oct
month = nov
month = dec
```

**Or numeric**:
```bibtex
month = {1}   % January
month = {12}  % December
```

**Or full name in braces**:
```bibtex
month = {January}
```

**Standard abbreviations work without quotes** because they're defined in BibTeX.

### Journal Names

**Full name** (not abbreviated):

```bibtex
journal = {Nature}
journal = {Science}
journal = {Cell}
journal = {Proceedings of the National Academy of Sciences}
journal = {Journal of the American Chemical Society}
```

**Bibliography style** will handle abbreviation if needed.

**Avoid manual abbreviation**:
```bibtex
% Don't do this in BibTeX file
journal = {Proc. Natl. Acad. Sci. U.S.A.}

% Do this instead
journal = {Proceedings of the National Academy of Sciences}
```

**Exception**: If style requires abbreviations, use full abbreviated form:
```bibtex
journal = {Proc. Natl. Acad. Sci. U.S.A.}  % If required by style
```

### DOI Formatting

**URL format** (preferred):

```bibtex
doi = {10.1038/s41586-021-03819-2}
```

**Not**:
```bibtex
doi = {https://doi.org/10.1038/s41586-021-03819-2}  % Don't include URL
doi = {doi:10.1038/s41586-021-03819-2}              % Don't include prefix
```

**LaTeX** will format as URL automatically.

**Note**: No period after DOI field!

### URL Formatting

```bibtex
url = {https://www.example.com/article}
```

**Use**:
- When DOI not available
- For web pages
- For supplementary materials

**Don't duplicate**:
```bibtex
% Don't include both if DOI URL is same as url
doi = {10.1038/nature12345}
url = {https://doi.org/10.1038/nature12345}  % Redundant!
```

### Special Characters

**Accents and diacritics**:
```bibtex
author = {M{\"u}ller, Hans}        % ü
author = {Garc{\'i}a, Jos{\'e}}    % í, é
author = {Erd{\H{o}}s, Paul}       % ő
author = {Schr{\"o}dinger, Erwin}  % ö
```

**Or use UTF-8** (with proper LaTeX setup):
```bibtex
author = {Müller, Hans}
author = {García, José}
```

**Mathematical symbols**:
```bibtex
title = {The $\alpha$-helix Structure}
title = {$\beta$-sheet Prediction}
```

**Chemical formulas**:
```bibtex
title = {H$_2$O Molecular Dynamics}
% Or with chemformula package:
title = {\ce{H2O} Molecular Dynamics}
```

### Field Order

**Recommended order** (for readability):

```bibtex
@article{Key,
  author  = {},
  title   = {},
  journal = {},
  year    = {},
  volume  = {},
  number  = {},
  pages   = {},
  doi     = {},
  url     = {},
  note    = {}
}
```

**Rules**:
- Most important fields first
- Consistent across entries
- Use formatter to standardize

## Best Practices

### 1. Consistent Formatting

Use same format throughout:
- Author name format
- Title capitalization
- Journal names
- Citation key style

### 2. Required Fields

Always include:
- All required fields for entry type
- DOI for modern papers (2000+)
- Volume and pages for articles
- Publisher for books

### 3. Protect Capitalization

Use braces for:
- Proper nouns: `{AlphaFold}`
- Acronyms: `{DNA}`, `{CRISPR}`
- Formulas: `{H2O}`
- Names: `{Python}`, `{R}`

### 4. Complete Author Lists

Include all authors when possible:
- All authors if <10
- Use "and others" for 10+
- Don't abbreviate to "et al." manually

### 5. Use Standard Entry Types

Choose correct entry type:
- Journal article → `@article`
- Book → `@book`
- Conference paper → `@inproceedings`
- Preprint → `@misc`

### 6. Validate Syntax

Check for:
- Balanced braces
- Commas after fields
- Unique citation keys
- Valid entry types

### 7. Use Formatters

Use automated tools:
```bash
python scripts/format_bibtex.py references.bib
```

Benefits:
- Consistent formatting
- Catch syntax errors
- Standardize field order
- Fix common issues

## Common Mistakes

### 1. Wrong Author Separator

**Wrong**:
```bibtex
author = {Smith, J.; Doe, J.}    % Semicolon
author = {Smith, J., Doe, J.}    % Comma
author = {Smith, J. & Doe, J.}   % Ampersand
```

**Correct**:
```bibtex
author = {Smith, John and Doe, Jane}
```

### 2. Missing Commas

**Wrong**:
```bibtex
@article{Smith2024,
  author = {Smith, John}    % Missing comma!
  title = {Title}
}
```

**Correct**:
```bibtex
@article{Smith2024,
  author = {Smith, John},   % Comma after each field
  title = {Title}
}
```

### 3. Unprotected Capitalization

**Wrong**:
```bibtex
title = {Machine Learning with Python}
% "Python" will become "python" in title case
```

**Correct**:
```bibtex
title = {Machine Learning with {Python}}
```

### 4. Single Hyphen in Pages

**Wrong**:
```bibtex
pages = {123-145}   % Single hyphen
```

**Correct**:
```bibtex
pages = {123--145}  % Double hyphen (en-dash)
```

### 5. Redundant "pp." in Pages

**Wrong**:
```bibtex
pages = {pp. 123--145}
```

**Correct**:
```bibtex
pages = {123--145}
```

### 6. DOI with URL Prefix

**Wrong**:
```bibtex
doi = {https://doi.org/10.1038/nature12345}
doi = {doi:10.1038/nature12345}
```

**Correct**:
```bibtex
doi = {10.1038/nature12345}
```

## Example Complete Bibliography

```bibtex
% Journal article
@article{Jumper2021,
  author  = {Jumper, John and Evans, Richard and Pritzel, Alexander and others},
  title   = {Highly Accurate Protein Structure Prediction with {AlphaFold}},
  journal = {Nature},
  year    = {2021},
  volume  = {596},
  number  = {7873},
  pages   = {583--589},
  doi     = {10.1038/s41586-021-03819-2}
}

% Book
@book{Kumar2021,
  author    = {Kumar, Vinay and Abbas, Abul K. and Aster, Jon C.},
  title     = {Robbins and Cotran Pathologic Basis of Disease},
  publisher = {Elsevier},
  year      = {2021},
  edition   = {10},
  address   = {Philadelphia, PA},
  isbn      = {978-0-323-53113-9}
}

% Conference paper
@inproceedings{Vaswani2017,
  author    = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and others},
  title     = {Attention is All You Need},
  booktitle = {Advances in Neural Information Processing Systems 30 (NeurIPS 2017)},
  year      = {2017},
  pages     = {5998--6008}
}

% Book chapter
@incollection{Brown2020,
  author    = {Brown, Peter O. and Botstein, David},
  title     = {Exploring the New World of the Genome with {DNA} Microarrays},
  booktitle = {DNA Microarrays: A Molecular Cloning Manual},
  editor    = {Eisen, Michael B. and Brown, Patrick O.},
  publisher = {Cold Spring Harbor Laboratory Press},
  year      = {2020},
  pages     = {1--45}
}

% PhD thesis
@phdthesis{Johnson2023,
  author  = {Johnson, Mary L.},
  title   = {Novel Approaches to Cancer Immunotherapy},
  school  = {Stanford University},
  year    = {2023},
  type    = {{PhD} dissertation}
}

% Preprint
@misc{Zhang2024,
  author       = {Zhang, Yi and Chen, Li and Wang, Hui},
  title        = {Novel Therapeutic Targets in {Alzheimer}'s Disease},
  year         = {2024},
  howpublished = {bioRxiv},
  doi          = {10.1101/2024.01.001},
  note         = {Preprint}
}

% Dataset
@misc{AlphaFoldDB2021,
  author       = {{DeepMind} and {EMBL-EBI}},
  title        = {{AlphaFold} Protein Structure Database},
  year         = {2021},
  howpublished = {Database},
  url          = {https://alphafold.ebi.ac.uk/},
  doi          = {10.1093/nar/gkab1061}
}
```

## Summary

BibTeX formatting essentials:

✓ **Choose correct entry type** (@article, @book, etc.)  
✓ **Include all required fields**  
✓ **Use `and` for multiple authors**  
✓ **Protect capitalization** with braces  
✓ **Use `--` for page ranges**  
✓ **Include DOI** for modern papers  
✓ **Validate syntax** before compilation  

Use formatting tools to ensure consistency:
```bash
python scripts/format_bibtex.py references.bib
```

Properly formatted BibTeX ensures correct, consistent citations across all bibliography styles!

### `references/citation_validation.md`

# Citation Validation Guide

Comprehensive guide to validating citation accuracy, completeness, and formatting in BibTeX files.

## Overview

Citation validation ensures:
- All citations are accurate and complete
- DOIs resolve correctly
- Required fields are present
- No duplicate entries
- Proper formatting and syntax
- Links are accessible

Validation should be performed:
- After extracting metadata
- Before manuscript submission
- After manual edits to BibTeX files
- Periodically for maintained bibliographies

## Validation Categories

### 1. DOI Verification

**Purpose**: Ensure DOIs are valid and resolve correctly.

#### What to Check

**DOI format**:
```
Valid:   10.1038/s41586-021-03819-2
Valid:   10.1126/science.aam9317
Invalid: 10.1038/invalid
Invalid: doi:10.1038/... (should omit "doi:" prefix in BibTeX)
```

**DOI resolution**:
- DOI should resolve via https://doi.org/
- Should redirect to actual article
- Should not return 404 or error

**Metadata consistency**:
- CrossRef metadata should match BibTeX
- Author names should align
- Title should match
- Year should match

#### How to Validate

**Manual check**:
1. Copy DOI from BibTeX
2. Visit https://doi.org/10.1038/nature12345
3. Verify it redirects to correct article
4. Check metadata matches

**Automated check** (recommended):
```bash
python scripts/validate_citations.py references.bib --check-dois
```

**Process**:
1. Extract all DOIs from BibTeX file
2. Query doi.org resolver for each
3. Query CrossRef API for metadata
4. Compare metadata with BibTeX entry
5. Report discrepancies

#### Common Issues

**Broken DOIs**:
- Typos in DOI
- Publisher changed DOI (rare)
- Article retracted
- Solution: Find correct DOI from publisher site

**Mismatched metadata**:
- BibTeX has old/incorrect information
- Solution: Re-extract metadata from CrossRef

**Missing DOIs**:
- Older articles may not have DOIs
- Acceptable for pre-2000 publications
- Add URL or PMID instead

### 2. Required Fields

**Purpose**: Ensure all necessary information is present.

#### Required by Entry Type

**@article**:
```bibtex
author   % REQUIRED
title    % REQUIRED
journal  % REQUIRED
year     % REQUIRED
volume   % Highly recommended
pages    % Highly recommended
doi      % Highly recommended for modern papers
```

**@book**:
```bibtex
author OR editor  % REQUIRED (at least one)
title            % REQUIRED
publisher        % REQUIRED
year             % REQUIRED
isbn             % Recommended
```

**@inproceedings**:
```bibtex
author     % REQUIRED
title      % REQUIRED
booktitle  % REQUIRED (conference/proceedings name)
year       % REQUIRED
pages      % Recommended
```

**@incollection** (book chapter):
```bibtex
author     % REQUIRED
title      % REQUIRED (chapter title)
booktitle  % REQUIRED (book title)
publisher  % REQUIRED
year       % REQUIRED
editor     % Recommended
pages      % Recommended
```

**@phdthesis**:
```bibtex
author  % REQUIRED
title   % REQUIRED
school  % REQUIRED
year    % REQUIRED
```

**@misc** (preprints, datasets, etc.):
```bibtex
author  % REQUIRED
title   % REQUIRED
year    % REQUIRED
howpublished  % Recommended (bioRxiv, Zenodo, etc.)
doi OR url    % At least one required
```

#### Validation Script

```bash
python scripts/validate_citations.py references.bib
```

**Output**:
```
Error: Entry 'Smith2024' missing required field 'journal'
Error: Entry 'Doe2023' missing required field 'year'
Warning: Entry 'Jones2022' missing recommended field 'volume'
```

### 3. Author Name Formatting

**Purpose**: Ensure consistent, correct author name formatting.

#### Proper Format

**Recommended BibTeX format**:
```bibtex
author = {Last1, First1 and Last2, First2 and Last3, First3}
```

**Examples**:
```bibtex
% Correct
author = {Smith, John}
author = {Smith, John A.}
author = {Smith, John Andrew}
author = {Smith, John and Doe, Jane}
author = {Smith, John and Doe, Jane and Johnson, Mary}

% For many authors
author = {Smith, John and Doe, Jane and others}

% Incorrect
author = {John Smith}  % First Last format (not recommended)
author = {Smith, J.; Doe, J.}  % Semicolon separator (wrong)
author = {Smith J, Doe J}  % Missing commas
```

#### Special Cases

**Suffixes (Jr., III, etc.)**:
```bibtex
author = {King, Jr., Martin Luther}
```

**Multiple surnames (hyphenated)**:
```bibtex
author = {Smith-Jones, Mary}
```

**Van, von, de, etc.**:
```bibtex
author = {van der Waals, Johannes}
author = {de Broglie, Louis}
```

**Organizations as authors**:
```bibtex
author = {{World Health Organization}}
% Double braces treat as single author
```

#### Validation Checks

**Automated validation**:
```bash
python scripts/validate_citations.py references.bib
```

**Checks for**:
- Proper separator (and, not &, ; , etc.)
- Comma placement
- Empty author fields
- Malformed names

### 4. Data Consistency

**Purpose**: Ensure all fields contain valid, reasonable values.

#### Year Validation

**Valid years**:
```bibtex
year = {2024}    % Current/recent
year = {1953}    % Watson & Crick DNA structure (historical)
year = {1665}    % Hooke's Micrographia (very old)
```

**Invalid years**:
```bibtex
year = {24}      % Two digits (ambiguous)
year = {202}     % Typo
year = {2025}    % Future (unless accepted/in press)
year = {0}       % Obviously wrong
```

**Check**:
- Four digits
- Reasonable range (1600-current+1)
- Not all zeros

#### Volume/Number Validation

```bibtex
volume = {123}      % Numeric
volume = {12}       % Valid
number = {3}        % Valid
number = {S1}       % Supplement issue (valid)
```

**Invalid**:
```bibtex
volume = {Vol. 123}  % Should be just number
number = {Issue 3}   % Should be just number
```

#### Page Range Validation

**Correct format**:
```bibtex
pages = {123--145}    % En-dash (two hyphens)
pages = {e0123456}    % PLOS-style article ID
pages = {123}         % Single page
```

**Incorrect format**:
```bibtex
pages = {123-145}     % Single hyphen (use --)
pages = {pp. 123-145} % Remove "pp."
pages = {123–145}     % Unicode en-dash (may cause issues)
```

#### URL Validation

**Check**:
- URLs are accessible (return 200 status)
- HTTPS when available
- No obvious typos
- Permanent links (not temporary)

**Valid**:
```bibtex
url = {https://www.nature.com/articles/nature12345}
url = {https://arxiv.org/abs/2103.14030}
```

**Questionable**:
```bibtex
url = {http://...}  % HTTP instead of HTTPS
url = {file:///...} % Local file path
url = {bit.ly/...}  % URL shortener (not permanent)
```

### 5. Duplicate Detection

**Purpose**: Find and remove duplicate entries.

#### Types of Duplicates

**Exact duplicates** (same DOI):
```bibtex
@article{Smith2024a,
  doi = {10.1038/nature12345},
  ...
}

@article{Smith2024b,
  doi = {10.1038/nature12345},  % Same DOI!
  ...
}
```

**Near duplicates** (similar title/authors):
```bibtex
@article{Smith2024,
  title = {Machine Learning for Drug Discovery},
  ...
}

@article{Smith2024method,
  title = {Machine learning for drug discovery},  % Same, different case
  ...
}
```

**Preprint + Published**:
```bibtex
@misc{Smith2023arxiv,
  title = {AlphaFold Results},
  howpublished = {arXiv},
  ...
}

@article{Smith2024,
  title = {AlphaFold Results},  % Same paper, now published
  journal = {Nature},
  ...
}
% Keep published version only
```

#### Detection Methods

**By DOI** (most reliable):
- Same DOI = exact duplicate
- Keep one, remove other

**By title similarity**:
- Normalize: lowercase, remove punctuation
- Calculate similarity (e.g., Levenshtein distance)
- Flag if >90% similar

**By author-year-title**:
- Same first author + year + similar title
- Likely duplicate

**Automated detection**:
```bash
python scripts/validate_citations.py references.bib
```

**Output**:
```
Warning: Possible duplicate entries:
  - Smith2024a (DOI: 10.1038/nature12345)
  - Smith2024b (DOI: 10.1038/nature12345)
  Recommendation: Keep one entry, remove the other.
```

### 6. Format and Syntax

**Purpose**: Ensure valid BibTeX syntax.

#### Common Syntax Errors

**Missing commas**:
```bibtex
@article{Smith2024,
  author = {Smith, John}   % Missing comma!
  title = {Title}
}
% Should be:
  author = {Smith, John},  % Comma after each field
```

**Unbalanced braces**:
```bibtex
title = {Title with {Protected} Text  % Missing closing brace
% Should be:
title = {Title with {Protected} Text}
```

**Missing closing brace for entry**:
```bibtex
@article{Smith2024,
  author = {Smith, John},
  title = {Title}
  % Missing closing brace!
% Should end with:
}
```

**Invalid characters in keys**:
```bibtex
@article{Smith&Doe2024,  % & not allowed in key
  ...
}
% Use:
@article{SmithDoe2024,
  ...
}
```

#### BibTeX Syntax Rules

**Entry structure**:
```bibtex
@TYPE{citationkey,
  field1 = {value1},
  field2 = {value2},
  ...
  fieldN = {valueN}
}
```

**Citation keys**:
- Alphanumeric and some punctuation (-, _, ., :)
- No spaces
- Case-sensitive
- Unique within file

**Field values**:
- Enclosed in {braces} or "quotes"
- Braces preferred for complex text
- Numbers can be unquoted: `year = 2024`

**Special characters**:
- `{` and `}` for grouping
- `\` for LaTeX commands
- Protect capitalization: `{AlphaFold}`
- Accents: `{\"u}`, `{\'e}`, `{\aa}`

#### Validation

```bash
python scripts/validate_citations.py references.bib
```

**Checks**:
- Valid BibTeX structure
- Balanced braces
- Proper commas
- Valid entry types
- Unique citation keys

## Validation Workflow

### Step 1: Basic Validation

Run comprehensive validation:

```bash
python scripts/validate_citations.py references.bib
```

**Checks all**:
- DOI resolution
- Required fields
- Author formatting
- Data consistency
- Duplicates
- Syntax

### Step 2: Review Report

Examine validation report:

```json
{
  "total_entries": 150,
  "valid_entries": 140,
  "errors": [
    {
      "entry": "Smith2024",
      "error": "missing_required_field",
      "field": "journal",
      "severity": "high"
    },
    {
      "entry": "Doe2023",
      "error": "invalid_doi",
      "doi": "10.1038/broken",
      "severity": "high"
    }
  ],
  "warnings": [
    {
      "entry": "Jones2022",
      "warning": "missing_recommended_field",
      "field": "volume",
      "severity": "medium"
    }
  ],
  "duplicates": [
    {
      "entries": ["Smith2024a", "Smith2024b"],
      "reason": "same_doi",
      "doi": "10.1038/nature12345"
    }
  ]
}
```

### Step 3: Fix Issues

**High-priority** (errors):
1. Add missing required fields
2. Fix broken DOIs
3. Remove duplicates
4. Correct syntax errors

**Medium-priority** (warnings):
1. Add recommended fields
2. Improve author formatting
3. Fix page ranges

**Low-priority**:
1. Standardize formatting
2. Add URLs for accessibility

### Step 4: Apply the safe corrections

`validate_citations.py` only reports; `format_bibtex.py` is what rewrites.
Send the result to a new file so the original survives a bad run:

```bash
python scripts/format_bibtex.py references.bib \
  --output fixed_references.bib
```

**It can**:
- Fix page range format (- to --), and expand abbreviated ranges (1123-30)
- Remove "pp." from pages
- Standardize author separators
- Strip URL prefixes from DOIs
- Normalize field order
- Rewrite citation keys to one scheme (`--rekey`)
- Drop duplicates by DOI or key (`--deduplicate`)

**It cannot**:
- Add missing information
- Find correct DOIs
- Determine which duplicate to keep — it keeps the first
- Fix semantic errors

### Step 5: Manual Review

Review auto-fixed file:
```bash
# Check what changed
diff references.bib fixed_references.bib

# Review specific entries that had errors
grep -A 10 "Smith2024" fixed_references.bib
```

### Step 6: Re-Validate

Validate after fixes:

```bash
python scripts/validate_citations.py fixed_references.bib --verbose
```

Should show:
```
✓ All DOIs valid
✓ All required fields present
✓ No duplicates found
✓ Syntax valid
✓ 150/150 entries valid
```

## Validation Checklist

Use this checklist before final submission:

### DOI Validation
- [ ] All DOIs resolve correctly
- [ ] Metadata matches between BibTeX and CrossRef
- [ ] No broken or invalid DOIs

### Completeness
- [ ] All entries have required fields
- [ ] Modern papers (2000+) have DOIs
- [ ] Authors properly formatted
- [ ] Journals/conferences properly named

### Consistency
- [ ] Years are 4-digit numbers
- [ ] Page ranges use -- not -
- [ ] Volume/number are numeric
- [ ] URLs are accessible

### Duplicates
- [ ] No entries with same DOI
- [ ] No near-duplicate titles
- [ ] Preprints updated to published versions

### Formatting
- [ ] Valid BibTeX syntax
- [ ] Balanced braces
- [ ] Proper commas
- [ ] Unique citation keys

### Final Checks
- [ ] Bibliography compiles without errors
- [ ] All citations in text appear in bibliography
- [ ] All bibliography entries cited in text
- [ ] Citation style matches journal requirements

## Best Practices

### 1. Validate Early and Often

```bash
# After extraction
python scripts/extract_metadata.py --doi ... --output refs.bib
python scripts/validate_citations.py refs.bib

# After manual edits
python scripts/validate_citations.py refs.bib

# Before submission
python scripts/validate_citations.py refs.bib --check-dois
```

### 2. Use Automated Tools

Don't validate manually - use scripts:
- Faster
- More comprehensive
- Catches errors humans miss
- Generates reports

### 3. Write to a new file and diff before replacing

`format_bibtex.py` writes only where you tell it to: with neither `--output`
nor `--in-place` it prints to stdout and leaves the input alone.

```bash
# Reformat into a separate file
python scripts/format_bibtex.py references.bib \
  --output references_fixed.bib

# Review changes
diff references.bib references_fixed.bib

# If satisfied, replace
mv references_fixed.bib references.bib
```

### 4. Fix High-Priority First

**Priority order**:
1. Syntax errors (prevent compilation)
2. Missing required fields (incomplete citations)
3. Broken DOIs (broken links)
4. Duplicates (confusion, wasted space)
5. Missing recommended fields
6. Formatting inconsistencies

### 5. Document Exceptions

For entries that can't be fixed:

```bibtex
@article{Old1950,
  author = {Smith, John},
  title = {Title},
  journal = {Obscure Journal},
  year = {1950},
  volume = {12},
  pages = {34--56},
  note = {DOI not available for publications before 2000}
}
```

### 6. Validate Against Journal Requirements

Different journals have different requirements:
- Citation style (numbered, author-year)
- Abbreviations (journal names)
- Maximum reference count
- Format (BibTeX, EndNote, manual)

Check journal author guidelines!

## Common Validation Issues

### Issue 1: Metadata Mismatch

**Problem**: BibTeX says 2023, CrossRef says 2024.

**Cause**:
- Online-first vs print publication
- Correction/update
- Extraction error

**Solution**:
1. Check actual article
2. Use more recent/accurate date
3. Update BibTeX entry
4. Re-validate

### Issue 2: Special Characters

**Problem**: LaTeX compilation fails on special characters.

**Cause**:
- Accented characters (é, ü, ñ)
- Chemical formulas (H₂O)
- Math symbols (α, β, ±)

**Solution**:
```bibtex
% Use LaTeX commands
author = {M{\"u}ller, Hans}  % Müller
title = {Study of H\textsubscript{2}O}  % H₂O
% Or use UTF-8 with proper LaTeX packages
```

### Issue 3: Incomplete Extraction (REQUIRES WEB SEARCH)

**Problem**: Extracted metadata missing fields (volume, pages, DOI, issue number).

**Cause**:
- Source API doesn't provide all metadata
- Extraction error
- Incomplete database record
- Online-first publication without final pagination

**Solution — MANDATORY web search to fill gaps**:

1. **Identify the missing fields** by scanning the BibTeX entry for empty or absent `volume`, `pages`, `number`, `doi` fields.

2. **Search for the missing metadata using web search** (parallel-web skill):
   ```bash
   # Search by author + title to find complete citation info
   parallel-cli search "AUTHOR_NAME PAPER_TITLE JOURNAL volume pages DOI" \
     --json --max-results 10 \
     -o sources/search_citation_CITATIONKEY.json
   ```

3. **If DOI is known, extract from DOI resolver page**:
   ```bash
   parallel-cli extract "https://doi.org/DOI_HERE" --json \
     --objective "extract volume, issue number, page range, publication date" \
     -o sources/extract_doi_CITATIONKEY.json
   ```

4. **If DOI is unknown, search for it**:
   ```bash
   parallel-cli search "AUTHOR_NAME PAPER_TITLE JOURNAL_NAME DOI" \
     --json --max-results 10 \
     -o sources/search_find_doi_CITATIONKEY.json
   ```

5. **Try alternative metadata sources**:
   - CrossRef API (via DOI): Most reliable for volume/pages
   - PubMed (via PMID): Good for biomedical papers
   - Google Scholar: Fallback for hard-to-find papers
   - Publisher website: Last resort

6. **Update the BibTeX entry** with the found metadata and log:
   ```
   [HH:MM:SS] METADATA ENRICHED: [CitationKey] - added volume, pages, doi ✅
   ```

7. **If truly unfindable** (rare), add a note field:
   ```bibtex
   note = {Complete pagination not yet assigned — online-first publication}
   ```

**CRITICAL**: Never leave an `@article` entry without `volume`, `pages`, and `doi` unless you have exhausted all search options and documented the reason.

### Issue 4: Cannot Find Duplicate

**Problem**: Same paper appears twice, not detected.

**Cause**:
- Different DOIs (should be rare)
- Different titles (abbreviated, typo)
- Different citation keys

**Solution**:
- Manual search for author + year
- Check for similar titles
- Remove manually

## Summary

Validation ensures citation quality:

✓ **Accuracy**: DOIs resolve, metadata correct  
✓ **Completeness**: All required fields present  
✓ **Consistency**: Proper formatting throughout  
✓ **No duplicates**: Each paper cited once  
✓ **Valid syntax**: BibTeX compiles without errors  

**Always validate** before final submission!

Use automated tools:
```bash
python scripts/validate_citations.py references.bib
```

Follow workflow:
1. Extract metadata
2. Validate
3. Fix errors
4. Re-validate
5. Submit

### `references/core_workflow.md`

# Core Workflow

The five phases in full: paper discovery, metadata extraction, the mandatory
web-search enrichment pass, BibTeX formatting, validation, and integration with the
writing workflow. Every command variant and option lives here.

## Core Workflow

Citation management follows a systematic process:

### Phase 1: Paper Discovery and Search

**Goal**: Find relevant papers using academic search engines.

#### Google Scholar Search

Google Scholar provides the most comprehensive coverage across disciplines.

**Basic Search**:
```bash
# Search for papers on a topic
python scripts/search_google_scholar.py "CRISPR gene editing" \
  --limit 50 \
  --output results.json

# Search with year filter
python scripts/search_google_scholar.py "machine learning protein folding" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100 \
  --output ml_proteins.json
```

**Advanced Search Strategies** (see `references/google_scholar_search.md`):
- Use quotation marks for exact phrases: `"deep learning"`
- Search by author: `author:LeCun`
- Search in title: `intitle:"neural networks"`
- Exclude terms: `machine learning -survey`
- Find highly cited papers using sort options
- Filter by date ranges to get recent work

**Best Practices**:
- Use specific, targeted search terms
- Include key technical terms and acronyms
- Filter by recent years for fast-moving fields
- Check "Cited by" to find seminal papers
- Export top results for further analysis

#### PubMed Search

PubMed specializes in biomedical and life sciences literature (35+ million citations).

**Basic Search**:
```bash
# Search PubMed
python scripts/search_pubmed.py "Alzheimer's disease treatment" \
  --limit 100 \
  --output alzheimers.json

# Search with MeSH terms and filters
python scripts/search_pubmed.py \
  --query '"Alzheimer Disease"[MeSH] AND "Drug Therapy"[MeSH]' \
  --date-start 2020 \
  --date-end 2024 \
  --publication-types "Clinical Trial,Review" \
  --output alzheimers_trials.json
```

**Advanced PubMed Queries** (see `references/pubmed_search.md`):
- Use MeSH terms: `"Diabetes Mellitus"[MeSH]`
- Field tags: `"cancer"[Title]`, `"Smith J"[Author]`
- Boolean operators: `AND`, `OR`, `NOT`
- Date filters: `2020:2024[Publication Date]`
- Publication types: `"Review"[Publication Type]`
- Combine with E-utilities API for automation

**Best Practices**:
- Use MeSH Browser to find correct controlled vocabulary
- Construct complex queries in PubMed Advanced Search Builder first
- Include multiple synonyms with OR
- Retrieve PMIDs for easy metadata extraction
- Export to JSON or directly to BibTeX

### Phase 2: Metadata Extraction

**Goal**: Convert paper identifiers (DOI, PMID, arXiv ID) to complete, accurate metadata.

#### Quick DOI to BibTeX Conversion

For single DOIs, use the quick conversion tool:

```bash
# Convert single DOI
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2

# Convert multiple DOIs from a file
python scripts/doi_to_bibtex.py --input dois.txt --output references.bib

# Different output formats
python scripts/doi_to_bibtex.py 10.1038/nature12345 --format json
```

#### Comprehensive Metadata Extraction

For DOIs, PMIDs, arXiv IDs, or URLs:

```bash
# Extract from DOI
python scripts/extract_metadata.py --doi 10.1038/s41586-021-03819-2

# Extract from PMID
python scripts/extract_metadata.py --pmid 34265844

# Extract from arXiv ID
python scripts/extract_metadata.py --arxiv 2103.14030

# Extract from URL
python scripts/extract_metadata.py --url "https://www.nature.com/articles/s41586-021-03819-2"

# Batch extraction from file (mixed identifiers)
python scripts/extract_metadata.py --input identifiers.txt --output citations.bib
```

**Metadata Sources** (see `references/metadata_extraction.md`):

1. **CrossRef API**: Primary source for DOIs
   - Comprehensive metadata for journal articles
   - Publisher-provided information
   - Includes authors, title, journal, volume, pages, dates
   - Free, no API key required

2. **PubMed E-utilities**: Biomedical literature
   - Official NCBI metadata
   - Includes MeSH terms, abstracts
   - PMID and PMCID identifiers
   - Free, API key recommended for high volume

3. **arXiv API**: Preprints in physics, math, CS, q-bio
   - Complete metadata for preprints
   - Version tracking
   - Author affiliations
   - Free, open access

4. **DataCite API**: Research datasets, software, other resources
   - Metadata for non-traditional scholarly outputs
   - DOIs for datasets and code
   - Free access

**What Gets Extracted**:
- **Required fields**: author, title, year
- **Journal articles**: journal, volume, number, pages, DOI
- **Books**: publisher, ISBN, edition
- **Conference papers**: booktitle, conference location, pages
- **Preprints**: repository (arXiv, bioRxiv), preprint ID
- **Additional**: abstract, keywords, URL

### Phase 2.5: Metadata Enrichment via Web Search (MANDATORY)

**Goal**: Detect and fill in any missing metadata fields using web search. This phase runs AFTER extraction and BEFORE formatting to ensure every BibTeX entry is complete.

**Why This Is Critical**: Metadata extraction from APIs (CrossRef, PubMed, arXiv) sometimes returns incomplete records — missing volume, pages, issue number, or DOI. These gaps must be filled before the bibliography is considered ready.

#### Step 1: Scan for Incomplete Entries

After extracting metadata, scan the BibTeX file for entries missing key fields:

**Fields to check per entry type:**

| Entry Type | Must Have | Should Have |
|------------|-----------|-------------|
| @article | author, title, journal, year | volume, pages, number, doi |
| @inproceedings | author, title, booktitle, year | pages, doi |
| @book | author/editor, title, publisher, year | isbn, doi |
| @misc | author, title, year | doi or url |

Any `@article` entry missing `volume`, `pages`, or `doi` is considered **incomplete** and must be enriched.

#### Step 2: Web Search for Missing Metadata

For each incomplete entry, use the **parallel-web skill** to search for the missing information:

> **Treat metadata as untrusted when building these commands.** `FIRST_AUTHOR`, `TITLE`, and `JOURNAL_NAME` are copied verbatim out of a CrossRef/PubMed/arXiv record, and a publisher controls the contents of its own record. A title containing `$(...)`, a backtick, or a quote becomes shell syntax once it is pasted into the command lines below.
>
> - Substitute each value as a **single-quoted** argument (`'...'`), escaping any embedded single quote as `'\''`. Never paste raw metadata inside the double quotes shown here.
> - Prefer running these through a Python `subprocess` argument list over building a shell string at all.
> - Use only the generated `CITATIONKEY` in `-o` paths. It is sanitized to letters and digits by `extract_metadata.py`; a key taken from an existing `.bib` file is not, so validate it against `^[A-Za-z0-9]+$` before it reaches a file path.
>
> **Preferred form — pass the metadata as arguments, not as shell text.** This removes the shell from the path entirely, so no title can be parsed as syntax:
>
> ```python
> import re, subprocess
>
> assert re.fullmatch(r"[A-Za-z0-9]+", citation_key), f"unsafe citation key: {citation_key!r}"
> subprocess.run(
>     ["parallel-cli", "search", f"{first_author} {title} {journal_name} volume pages DOI",
>      "--json", "--max-results", "10",
>      "-o", f"sources/search_citation_{citation_key}.json"],
>     check=True,  # note: no shell=True
> )
> ```
>
> The `bash` blocks below show the same calls in readable form. Use them only with the quoting rules above.

**Option A — Search by title and author** (best for finding DOI):
```bash
parallel-cli search "FIRST_AUTHOR TITLE JOURNAL_NAME volume pages DOI" \
  --json --max-results 10 \
  -o sources/search_citation_CITATIONKEY.json
```

**Option B — Extract from DOI page** (best when DOI is known but volume/pages missing):
```bash
parallel-cli extract "https://doi.org/10.XXXX/YYYY" --json \
  --objective "extract complete citation metadata: volume, issue, pages, publication date" \
  -o sources/extract_doi_CITATIONKEY.json
```

**Option C — Search CrossRef API directly** (programmatic, fast):
```bash
parallel-cli search "crossref DOI metadata FIRST_AUTHOR TITLE" \
  --json --max-results 10 \
  -o sources/search_crossref_CITATIONKEY.json
```

**Option D — Search Google Scholar** (fallback for hard-to-find papers):
```bash
parallel-cli search "google scholar FIRST_AUTHOR TITLE YEAR complete citation" \
  --json --max-results 10 \
  -o sources/search_scholar_CITATIONKEY.json
```

#### Step 3: Update BibTeX Entries

After finding the missing metadata:

1. Open `references.bib`
2. Add the missing fields to the incomplete entry
3. Verify the found metadata is consistent with existing fields (same author, title, year)
4. Log each fix:
   ```
   [HH:MM:SS] METADATA ENRICHED: [CitationKey] - added volume={X}, pages={Y--Z}, doi={10.XXX/YYY} ✅
   ```

#### Step 4: Handle Unfindable Metadata

If metadata genuinely cannot be found after web search (very old paper, obscure conference, etc.):

1. Add a `note` field to the BibTeX entry explaining the gap:
   ```bibtex
   note = {Volume and pages not available — published online only}
   ```
2. Log the exception:
   ```
   [HH:MM:SS] METADATA INCOMPLETE: [CitationKey] - pages unavailable (online-only publication) ⚠️
   ```
3. These exceptions should be rare — most modern papers have complete metadata findable via web search.

#### Quick Reference: Common Missing Fields and Where to Find Them

| Missing Field | Best Search Strategy |
|---------------|---------------------|
| DOI | Search "AUTHOR TITLE DOI" via parallel-cli search |
| Volume | Extract from DOI page or search "JOURNAL YEAR TITLE volume" |
| Pages | Extract from DOI page or search publisher website |
| Issue/Number | Extract from DOI page or CrossRef |
| Publisher | Search "JOURNAL publisher" or check journal website |

---

### Phase 3: BibTeX Formatting

**Goal**: Generate clean, properly formatted BibTeX entries.

#### Understanding BibTeX Entry Types

See `references/bibtex_formatting.md` for complete guide.

**Common Entry Types**:
- `@article`: Journal articles (most common)
- `@book`: Books
- `@inproceedings`: Conference papers
- `@incollection`: Book chapters
- `@phdthesis`: Dissertations
- `@misc`: Preprints, software, datasets

**Required Fields by Type**:

```bibtex
@article{citationkey,
  author  = {Last1, First1 and Last2, First2},
  title   = {Article Title},
  journal = {Journal Name},
  year    = {2024},
  volume  = {10},
  number  = {3},
  pages   = {123--145},
  doi     = {10.1234/example}
}

@inproceedings{citationkey,
  author    = {Last, First},
  title     = {Paper Title},
  booktitle = {Conference Name},
  year      = {2024},
  pages     = {1--10}
}

@book{citationkey,
  author    = {Last, First},
  title     = {Book Title},
  publisher = {Publisher Name},
  year      = {2024}
}
```

#### Formatting and Cleaning

Use the formatter to standardize BibTeX files:

```bash
# Format and clean BibTeX file
python scripts/format_bibtex.py references.bib \
  --output formatted_references.bib

# Sort entries by citation key
python scripts/format_bibtex.py references.bib \
  --sort key \
  --output sorted_references.bib

# Sort by year (newest first)
python scripts/format_bibtex.py references.bib \
  --sort year \
  --descending \
  --output sorted_references.bib

# Remove duplicates
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --output clean_references.bib

# Merge sources: one key scheme, then drop duplicates
python scripts/format_bibtex.py references.bib \
  --rekey \
  --deduplicate \
  --output merged_references.bib
```

**Formatting Operations**:
- Standardize field order
- Consistent indentation and spacing
- Proper capitalization in titles (protected with {})
- Standardized author name format
- Consistent citation key format
- Remove unnecessary fields
- Fix common errors (missing commas, braces)

### Phase 4: Citation Validation

**Goal**: Verify all citations are accurate and complete.

#### Comprehensive Validation

```bash
# Validate BibTeX file
python scripts/validate_citations.py references.bib

# Validate against a venue standard (e.g., Nature, NeurIPS, Literature Review)
python scripts/validate_citations.py references.bib --venue nature
python scripts/validate_citations.py references.bib --venue neurips
python scripts/validate_citations.py references.bib --venue review

# Validate with custom minimum citation count
python scripts/validate_citations.py references.bib --min-count 40

# Check references against a written manuscript file (detect missing or unused citations)
python scripts/validate_citations.py references.bib --manuscript paper.md

# Generate detailed validation report
python scripts/validate_citations.py references.bib \
  --venue nature \
  --manuscript paper.md \
  --report validation_report.json \
  --verbose
```

**Validation Checks** (see `references/citation_validation.md`):

1. **DOI Verification**:
   - DOI resolves correctly via doi.org
   - Metadata matches between BibTeX and CrossRef
   - No broken or invalid DOIs

2. **Required Fields**:
   - All required fields present for entry type
   - No empty or missing critical information
   - Author names properly formatted

3. **Data Consistency**:
   - Year is valid (4 digits, reasonable range)
   - Volume/number are numeric
   - Pages formatted correctly (e.g., 123--145)
   - URLs are accessible

4. **Duplicate Detection**:
   - Same DOI used multiple times
   - Similar titles (possible duplicates)
   - Same author/year/title combinations

5. **Format Compliance**:
   - Valid BibTeX syntax
   - Proper bracing and quoting
   - Citation keys are unique
   - Special characters handled correctly

**Validation Output**:
```json
{
  "total_entries": 150,
  "valid_entries": 145,
  "errors": [
    {
      "citation_key": "Smith2023",
      "error_type": "missing_field",
      "field": "journal",
      "severity": "high"
    },
    {
      "citation_key": "Jones2022",
      "error_type": "invalid_doi",
      "doi": "10.1234/broken",
      "severity": "high"
    }
  ],
  "warnings": [
    {
      "citation_key": "Brown2021",
      "warning_type": "possible_duplicate",
      "duplicate_of": "Brown2021a",
      "severity": "medium"
    }
  ]
}
```

#### Citation Count Standards by Venue

**Citations must always be high in number based on standards for journal and conference publications in the venue of choice or recommendation.** Never settle for a sparse reference list; establish an authoritative, rich context with dense, verified citations.

| Venue Type | Target Citation Count |
|------------|----------------------|
| High-impact multidisciplinary journals (Nature, Science, Cell) | **35-50+** |
| ML / CS conferences (NeurIPS, ICML, ICLR, CVPR, ACL) | **30-45+** |
| Comprehensive literature reviews / market research reports | **40-65+** |
| Medical journals (NEJM, Lancet, JAMA) | **30-45+** |

Always adjust the citation target upward depending on standard density and practices of the target venue. Avoid 'lazy' citation over-repetition — do not repeatedly cite the same 1 or 2 papers to support multiple unrelated claims; draw from a diverse, high-quality set of reputable references.

Enforce these standards programmatically with `validate_citations.py --venue <venue>` or `--min-count <N>`.

#### Mandatory Post-Writing Reference Checks (Non-Negotiable)

Once the entire scientific report or paper has been drafted and written, perform a comprehensive post-writing verification of all citations before compiling the final deliverables:

1. **Verify No Missing or Unresolved Citations**: Check the draft or compiled document to ensure that every in-text citation correctly resolves to a reference in `references.bib`. There must be ZERO broken citation keys, missing identifiers, or unresolved references (e.g., `[?]` or `[citation needed]`).
2. **Verify No Unused (Dangling) Bibliography Entries**: Check that every entry in `references.bib` is actually cited in the body of the report. Remove any unused entries to keep the bibliography perfectly clean.
3. **Verify Citation Quantity Against Target Standards**: Ensure the final citation count meets or exceeds the high standard of the chosen or recommended venue (see table above). If the count is below standard, perform additional literature search first, find high-quality papers, and integrate them into appropriate sections.
4. **Verify Metadata Completeness**: Confirm that all cited entries contain complete, fully-verified fields (all author names, complete journal/conference names, exact year, volume, issue, page range, and valid DOI).

Run all of these checks in one command:

```bash
python scripts/validate_citations.py references.bib \
  --venue <venue> \
  --manuscript paper.md \
  --report post_writing_check.json
```

### Phase 5: Integration with Writing Workflow

#### Building References for Manuscripts

Complete workflow for creating a bibliography:

```bash
# 1. Search for papers on your topic
python scripts/search_pubmed.py \
  '"CRISPR-Cas Systems"[MeSH] AND "Gene Editing"[MeSH]' \
  --date-start 2020 \
  --limit 200 \
  --output crispr_papers.json

# 2. Extract DOIs from search results and convert to BibTeX
python scripts/extract_metadata.py \
  --input crispr_papers.json \
  --output crispr_refs.bib

# 3. Add specific papers by DOI
python scripts/doi_to_bibtex.py 10.1038/nature12345 >> crispr_refs.bib
python scripts/doi_to_bibtex.py 10.1126/science.abcd1234 >> crispr_refs.bib

# 4. Format and clean the BibTeX file
python scripts/format_bibtex.py crispr_refs.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output references.bib

# 5. Validate all citations
python scripts/validate_citations.py references.bib \
  --report validation.json

# 6. Review validation report and fix any remaining issues
cat validation.json

# 7. Use in your LaTeX document
# \bibliography{final_references}
```

#### Integration with Literature Review Skill

This skill complements the `literature-review` skill:

**Literature Review Skill** → Systematic search and synthesis
**Citation Management Skill** → Technical citation handling

**Combined Workflow**:
1. Use `literature-review` for comprehensive multi-database search
2. Use `citation-management` to extract and validate all citations
3. Use `literature-review` to synthesize findings thematically
4. Use `citation-management` to verify final bibliography accuracy

```bash
# After completing literature review
# Verify all citations in the review document
python scripts/validate_citations.py my_review_references.bib --report review_validation.json

# Normalise formatting (venue style is chosen by the .bst at build time)
python scripts/format_bibtex.py my_review_references.bib \
  --output formatted_refs.bib
```

#### Integration with Zotero (pyzotero Skill)

When the user already keeps references in Zotero, treat the Zotero library as the source of truth for the bibliography and use this skill for validation and formatting. The `pyzotero` skill covers the library side — reading items and collections, creating and updating references, uploading attachments, and exporting citations via the Zotero Web API v3.

**Zotero Library (`pyzotero`)** → Library of record: storage, collections, tags, attachments
**Citation Management Skill** → Metadata accuracy: validation, enrichment, style formatting

**Combined Workflow**:
1. Use `pyzotero` to pull the working set from the Zotero library, filtered by collection or tag
2. Export it as BibTeX with `zot.add_parameters(format='bibtex')` (see `pyzotero` → `references/exports.md`)
3. Use `citation-management` to validate the exported entries and repair incomplete metadata
4. Use `citation-management` to format for the target venue
5. Optionally use `pyzotero` to write corrected fields back so the library benefits from the fixes

```bash
# 1-2. Export the desired collection from Zotero as BibTeX (pyzotero skill)
#      zot.add_parameters(format='bibtex'); bibtex = zot.collection_items(collection_id)
#      → write to zotero_export.bib

# 3. Validate the exported bibliography
python scripts/validate_citations.py zotero_export.bib --report zotero_validation.json

# 4. Normalise the export (venue style comes from the .bst at build time)
python scripts/format_bibtex.py zotero_export.bib \
  --output formatted_refs.bib
```

Zotero exports are only as good as what was captured — browser-connector entries in particular often carry missing DOIs, truncated author lists, or preprint metadata for papers since published. Run the validation step before submission rather than trusting the export, and prefer writing corrections back to Zotero so the same errors do not resurface in the next manuscript.

### `references/example_workflows.md`

# Example Workflows

Four end-to-end worked examples: building a bibliography for a paper, converting a
list of DOIs, cleaning an existing BibTeX file, and finding and citing seminal papers.

## Example Workflows

### Example 1: Building a Bibliography for a Paper

```bash
# Step 1: Find key papers on your topic
python scripts/search_google_scholar.py "transformer neural networks" \
  --year-start 2017 \
  --limit 50 \
  --output transformers_gs.json

python scripts/search_pubmed.py "deep learning medical imaging" \
  --date-start 2020 \
  --limit 50 \
  --output medical_dl_pm.json

# Step 2: Extract metadata from search results
python scripts/extract_metadata.py \
  --input transformers_gs.json \
  --output transformers.bib

python scripts/extract_metadata.py \
  --input medical_dl_pm.json \
  --output medical.bib

# Step 3: Add specific papers you already know
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2 >> specific.bib
python scripts/doi_to_bibtex.py 10.1126/science.aam9317 >> specific.bib

# Step 4: Combine all BibTeX files
cat transformers.bib medical.bib specific.bib > combined.bib

# Step 5: Format and deduplicate
python scripts/format_bibtex.py combined.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output formatted.bib

# Step 6: Validate
python scripts/validate_citations.py formatted.bib \
  --report validation.json

# Step 7: Review any issues
cat validation.json | grep -A 3 '"errors"'

# Step 8: Use in LaTeX
# \bibliography{final_references}
```

### Example 2: Converting a List of DOIs

```bash
# You have a text file with DOIs (one per line)
# dois.txt contains:
# 10.1038/s41586-021-03819-2
# 10.1126/science.aam9317
# 10.1016/j.cell.2023.01.001

# Convert all to BibTeX
python scripts/doi_to_bibtex.py --input dois.txt --output references.bib

# Validate the result
python scripts/validate_citations.py references.bib --verbose
```

### Example 3: Cleaning an Existing BibTeX File

```bash
# You have a messy BibTeX file from various sources
# Clean it up systematically

# Step 1: Format and standardize
python scripts/format_bibtex.py messy_references.bib \
  --output step1_formatted.bib

# Step 2: Remove duplicates
python scripts/format_bibtex.py step1_formatted.bib \
  --deduplicate \
  --output step2_deduplicated.bib

# Step 3: Check what is still wrong before sorting
python scripts/validate_citations.py step2_deduplicated.bib \
  --report step3_validation.json

# Step 4: Sort by year
python scripts/format_bibtex.py step2_deduplicated.bib \
  --sort year \
  --descending \
  --output clean_references.bib

# Step 5: Final validation report
python scripts/validate_citations.py clean_references.bib \
  --report final_validation.json \
  --verbose

# Review report
cat final_validation.json
```

### Example 4: Finding and Citing Seminal Papers

```bash
# Find highly cited papers on a topic
python scripts/search_google_scholar.py "AlphaFold protein structure" \
  --year-start 2020 \
  --year-end 2024 \
  --sort-by citations \
  --limit 20 \
  --output alphafold_seminal.json

# Extract the top 10 by citation count
# (script will have included citation counts in JSON)

# Convert to BibTeX
python scripts/extract_metadata.py \
  --input alphafold_seminal.json \
  --output alphafold_refs.bib

# The BibTeX file now contains the most influential papers
```

### `references/google_scholar_search.md`

# Google Scholar Search Guide

Comprehensive guide to searching Google Scholar for academic papers, including advanced search operators, filtering strategies, and metadata extraction.

## Overview

Google Scholar provides the most comprehensive coverage of academic literature across all disciplines:
- **Coverage**: 100+ million scholarly documents
- **Scope**: All academic disciplines
- **Content types**: Journal articles, books, theses, conference papers, preprints, patents, court opinions
- **Citation tracking**: "Cited by" links for forward citation tracking
- **Accessibility**: Free to use, no account required

## Basic Search

### Simple Keyword Search

Search for papers containing specific terms anywhere in the document (title, abstract, full text):

```
CRISPR gene editing
machine learning protein folding
climate change impact agriculture
quantum computing algorithms
```

**Tips**:
- Use specific technical terms
- Include key acronyms and abbreviations
- Start broad, then refine
- Check spelling of technical terms

### Exact Phrase Search

Use quotation marks to search for exact phrases:

```
"deep learning"
"CRISPR-Cas9"
"systematic review"
"randomized controlled trial"
```

**When to use**:
- Technical terms that must appear together
- Proper names
- Specific methodologies
- Exact titles

## Advanced Search Operators

### Author Search

Find papers by specific authors:

```
author:LeCun
author:"Geoffrey Hinton"
author:Church synthetic biology
```

**Variations**:
- Single last name: `author:Smith`
- Full name in quotes: `author:"Jane Smith"`
- Author + topic: `author:Doudna CRISPR`

**Tips**:
- Authors may publish under different name variations
- Try with and without middle initials
- Consider name changes (marriage, etc.)
- Use quotation marks for full names

### Title Search

Search only in article titles:

```
intitle:transformer
intitle:"attention mechanism"
intitle:review climate change
```

**Use cases**:
- Finding papers specifically about a topic
- More precise than full-text search
- Reduces irrelevant results
- Good for finding reviews or methods

### Source (Journal) Search

Search within specific journals or conferences:

```
source:Nature
source:"Nature Communications"
source:NeurIPS
source:"Journal of Machine Learning Research"
```

**Applications**:
- Track publications in top-tier venues
- Find papers in specialized journals
- Identify conference-specific work
- Verify publication venue

### Exclusion Operator

Exclude terms from results:

```
machine learning -survey
CRISPR -patent
climate change -news
deep learning -tutorial -review
```

**Common exclusions**:
- `-survey`: Exclude survey papers
- `-review`: Exclude review articles
- `-patent`: Exclude patents
- `-book`: Exclude books
- `-news`: Exclude news articles
- `-tutorial`: Exclude tutorials

### OR Operator

Search for papers containing any of multiple terms:

```
"machine learning" OR "deep learning"
CRISPR OR "gene editing"
"climate change" OR "global warming"
```

**Best practices**:
- OR must be uppercase
- Combine synonyms
- Include acronyms and spelled-out versions
- Use with exact phrases

### Wildcard Search

Use asterisk (*) as wildcard for unknown words:

```
"machine * learning"
"CRISPR * editing"
"* neural network"
```

**Note**: Limited wildcard support in Google Scholar compared to other databases.

## Advanced Filtering

### Year Range

Filter by publication year:

**Using interface**:
- Click "Since [year]" on left sidebar
- Select custom range

**Using search operators**:
```
# Not directly in search query
# Use interface or URL parameters
```

**In script**:
```bash
python scripts/search_google_scholar.py "quantum computing" \
  --year-start 2020 \
  --year-end 2024
```

### Sorting Options

**By relevance** (default):
- Google's algorithm determines relevance
- Considers citations, author reputation, publication venue
- Generally good for most searches

**By date**:
- Most recent papers first
- Good for fast-moving fields
- May miss highly cited older papers
- Click "Sort by date" in interface

**By citation count** (via script):
```bash
python scripts/search_google_scholar.py "transformers" \
  --sort-by citations \
  --limit 50
```

### Language Filtering

**In interface**:
- Settings → Languages
- Select preferred languages

**Default**: English and papers with English abstracts

## Search Strategies

### Finding Seminal Papers

Identify highly influential papers in a field:

1. **Search by topic** with broad terms
2. **Sort by citations** (most cited first)
3. **Look for review articles** for comprehensive overviews
4. **Check publication dates** for foundational vs recent work

**Example**:
```
"generative adversarial networks"
# Sort by citations
# Top results: original GAN paper (Goodfellow et al., 2014), key variants
```

### Finding Recent Work

Stay current with latest research:

1. **Search by topic**
2. **Filter to recent years** (last 1-2 years)
3. **Sort by date** for newest first
4. **Set up alerts** for ongoing tracking

**Example**:
```bash
python scripts/search_google_scholar.py "AlphaFold protein structure" \
  --year-start 2023 \
  --year-end 2024 \
  --limit 50
```

### Finding Review Articles

Get comprehensive overviews of a field:

```
intitle:review "machine learning"
"systematic review" CRISPR
intitle:survey "natural language processing"
```

**Indicators**:
- "review", "survey", "perspective" in title
- Often highly cited
- Published in review journals (Nature Reviews, Trends, etc.)
- Comprehensive reference lists

### Citation Chain Search

**Forward citations** (papers citing a key paper):
1. Find seminal paper
2. Click "Cited by X"
3. See all papers that cite it
4. Identify how field has developed

**Backward citations** (references in a key paper):
1. Find recent review or important paper
2. Check its reference list
3. Identify foundational work
4. Trace development of ideas

**Example workflow**:
```
# Find original transformer paper
"Attention is all you need" author:Vaswani

# Check "Cited by 120,000+"
# See evolution: BERT, GPT, T5, etc.

# Check references in original paper
# Find RNN, LSTM, attention mechanism origins
```

### Comprehensive Literature Search

For thorough coverage (e.g., systematic reviews):

1. **Generate synonym list**:
   - Main terms + alternatives
   - Acronyms + spelled out
   - US vs UK spelling

2. **Use OR operators**:
   ```
   ("machine learning" OR "deep learning" OR "neural networks")
   ```

3. **Combine multiple concepts**:
   ```
   ("machine learning" OR "deep learning") ("drug discovery" OR "drug development")
   ```

4. **Search without date filters** initially:
   - Get total landscape
   - Filter later if too many results

5. **Export results** for systematic analysis:
   ```bash
   python scripts/search_google_scholar.py \
     '"machine learning" OR "deep learning" drug discovery' \
     --limit 500 \
     --output comprehensive_search.json
   ```

## Extracting Citation Information

### From Google Scholar Results Page

Each result shows:
- **Title**: Paper title (linked to full text if available)
- **Authors**: Author list (often truncated)
- **Source**: Journal/conference, year, publisher
- **Cited by**: Number of citations + link to citing papers
- **Related articles**: Link to similar papers
- **All versions**: Different versions of the same paper

### Export Options

**Manual export**:
1. Click "Cite" under paper
2. Select BibTeX format
3. Copy citation

**Limitations**:
- One paper at a time
- Manual process
- Time-consuming for many papers

**Automated export** (using script):
```bash
# Search and export to BibTeX
python scripts/search_google_scholar.py "quantum computing" \
  --limit 50 \
  --format bibtex \
  --output quantum_papers.bib
```

### Metadata Available

From Google Scholar you can typically extract:
- Title
- Authors (may be incomplete)
- Year
- Source (journal/conference)
- Citation count
- Link to full text (when available)
- Link to PDF (when available)

**Note**: Metadata quality varies:
- Some fields may be missing
- Author names may be incomplete
- Need to verify with DOI lookup for accuracy

## Rate Limiting and Access

### Rate Limits

Google Scholar has rate limiting to prevent automated scraping:

**Symptoms of rate limiting**:
- CAPTCHA challenges
- Temporary IP blocks
- 429 "Too Many Requests" errors

**Best practices**:
1. **Add delays between requests**: 2-5 seconds minimum
2. **Limit query volume**: Don't search hundreds of queries rapidly
3. **Use scholarly library**: Handles rate limiting automatically
4. **Rotate User-Agents**: Appear as different browsers
5. **Consider proxies**: For large-scale searches (use ethically)

**In our scripts**:
```python
# Automatic rate limiting built in
time.sleep(random.uniform(3, 7))  # Random delay 3-7 seconds
```

### Ethical Considerations

**DO**:
- Respect rate limits
- Use reasonable delays
- Cache results (don't re-query)
- Use official APIs when available
- Attribute data properly

**DON'T**:
- Scrape aggressively
- Use multiple IPs to bypass limits
- Violate terms of service
- Burden servers unnecessarily
- Use data commercially without permission

### Institutional Access

**Benefits of institutional access**:
- Access to full-text PDFs through library subscriptions
- Better download capabilities
- Integration with library systems
- Link resolver to full text

**Setup**:
- Google Scholar → Settings → Library links
- Add your institution
- Links appear in search results

## Tips and Best Practices

### Search Optimization

1. **Start simple, then refine**:
   ```
   # Too specific initially
   intitle:"deep learning" intitle:review source:Nature 2023..2024
   
   # Better approach
   deep learning review
   # Review results
   # Add intitle:, source:, year filters as needed
   ```

2. **Use multiple search strategies**:
   - Keyword search
   - Author search for known experts
   - Citation chaining from key papers
   - Source search in top journals

3. **Check spelling and variations**:
   - Color vs colour
   - Optimization vs optimisation
   - Tumor vs tumour
   - Try common misspellings if few results

4. **Combine operators strategically**:
   ```
   # Good combination
   author:Church intitle:"synthetic biology" 2015..2024
   
   # Find reviews by specific author on topic in recent years
   ```

### Result Evaluation

1. **Check citation counts**:
   - High citations indicate influence
   - Recent papers may have low citations but be important
   - Citation counts vary by field

2. **Verify publication venue**:
   - Peer-reviewed journals vs preprints
   - Conference proceedings
   - Book chapters
   - Technical reports

3. **Check for full text access**:
   - [PDF] link on right side
   - "All X versions" may have open access version
   - Check institutional access
   - Try author's website or ResearchGate

4. **Look for review articles**:
   - Comprehensive overviews
   - Good starting point for new topics
   - Extensive reference lists

### Managing Results

1. **Use citation manager integration**:
   - Export to BibTeX
   - Import to Zotero, Mendeley, EndNote
   - Maintain organized library

2. **Set up alerts** for ongoing research:
   - Google Scholar → Alerts
   - Get emails for new papers matching query
   - Track specific authors or topics

3. **Create collections**:
   - Save papers to Google Scholar Library
   - Organize by project or topic
   - Add labels and notes

4. **Export systematically**:
   ```bash
   # Save search results for later analysis
   python scripts/search_google_scholar.py "your topic" \
     --output topic_papers.json
   
   # Can re-process later without re-searching
   python scripts/extract_metadata.py \
     --input topic_papers.json \
     --output topic_refs.bib
   ```

## Advanced Techniques

### Boolean Logic Combinations

Combine multiple operators for precise searches:

```
# Highly cited reviews on specific topic by known authors
intitle:review "machine learning" ("drug discovery" OR "drug development")
author:Horvath OR author:Bengio 2020..2024

# Method papers excluding reviews
intitle:method "protein folding" -review -survey

# Papers in top journals only
("Nature" OR "Science" OR "Cell") CRISPR 2022..2024
```

### Finding Open Access Papers

```
# Search with generic terms
machine learning

# Filter by "All versions" which often includes preprints
# Look for green [PDF] links (often open access)
# Check arXiv, bioRxiv versions
```

**In script**: the Scholar client has no open-access filter, but each result
carries an `eprint_url` when a free copy exists, so filter the JSON:

```bash
python scripts/search_google_scholar.py "topic" --output papers.json
python -c "import json;d=json.load(open('papers.json'));print(json.dumps([r for r in d['results'] if r['eprint_url']],indent=2))" > open_access_papers.json
```

OpenAlex exposes this directly as a field:

```bash
python scripts/search_openalex.py "topic" --output papers.json   # each result has is_open_access
```

### Tracking Research Impact

**For a specific paper**:
1. Find the paper
2. Click "Cited by X"
3. Analyze citing papers:
   - How is it being used?
   - What fields cite it?
   - Recent vs older citations?

**For an author**:
1. Search `author:LastName`
2. Check h-index and i10-index
3. View citation history graph
4. Identify most influential papers

**For a topic**:
1. Search topic
2. Sort by citations
3. Identify seminal papers (highly cited, older)
4. Check recent highly-cited papers (emerging important work)

### Finding Preprints and Early Work

```
# arXiv papers
source:arxiv "deep learning"

# bioRxiv papers
source:biorxiv CRISPR

# All preprint servers
("arxiv" OR "biorxiv" OR "medrxiv") your topic
```

**Note**: Preprints are not peer-reviewed. Always check if published version exists.

## Common Issues and Solutions

### Too Many Results

**Problem**: Search returns 100,000+ results, overwhelming.

**Solutions**:
1. Add more specific terms
2. Use `intitle:` to search only titles
3. Filter by recent years
4. Add exclusions (e.g., `-review`)
5. Search within specific journals

### Too Few Results

**Problem**: Search returns 0-10 results, suspiciously few.

**Solutions**:
1. Remove restrictive operators
2. Try synonyms and related terms
3. Check spelling
4. Broaden year range
5. Use OR for alternative terms

### Irrelevant Results

**Problem**: Results don't match intent.

**Solutions**:
1. Use exact phrases with quotes
2. Add more specific context terms
3. Use `intitle:` for title-only search
4. Exclude common irrelevant terms
5. Combine multiple specific terms

### CAPTCHA or Rate Limiting

**Problem**: Google Scholar shows CAPTCHA or blocks access.

**Solutions**:
1. Wait several minutes before continuing
2. Reduce query frequency
3. Use longer delays in scripts (5-10 seconds)
4. Switch to different IP/network
5. Consider using institutional access

### Missing Metadata

**Problem**: Author names, year, or venue missing from results.

**Solutions**:
1. Click through to see full details
2. Check "All versions" for better metadata
3. Look up by DOI if available
4. Extract metadata from CrossRef/PubMed instead
5. Manually verify from paper PDF

### Duplicate Results

**Problem**: Same paper appears multiple times.

**Solutions**:
1. Click "All X versions" to see consolidated view
2. Choose version with best metadata
3. Use deduplication in post-processing:
   ```bash
   python scripts/format_bibtex.py results.bib \
     --deduplicate \
     --output clean_results.bib
   ```

## Integration with Scripts

### search_google_scholar.py Usage

**Basic search**:
```bash
python scripts/search_google_scholar.py "machine learning drug discovery"
```

**With year filter**:
```bash
python scripts/search_google_scholar.py "CRISPR" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100
```

**Sort by citations**:
```bash
python scripts/search_google_scholar.py "transformers" \
  --sort-by citations \
  --limit 50
```

**Export to BibTeX**:
```bash
python scripts/search_google_scholar.py "quantum computing" \
  --format bibtex \
  --output quantum.bib
```

**Export to JSON for later processing**:
```bash
python scripts/search_google_scholar.py "topic" \
  --format json \
  --output results.json

# Later: extract full metadata
python scripts/extract_metadata.py \
  --input results.json \
  --output references.bib
```

### Batch Searching

For multiple topics:

```bash
# Create file with search queries (queries.txt)
# One query per line

# Search each query
while read query; do
  python scripts/search_google_scholar.py "$query" \
    --limit 50 \
    --output "${query// /_}.json"
  sleep 10  # Delay between queries
done < queries.txt
```

## Summary

Google Scholar is the most comprehensive academic search engine, providing:

✓ **Broad coverage**: All disciplines, 100M+ documents  
✓ **Free access**: No account or subscription required  
✓ **Citation tracking**: "Cited by" for impact analysis  
✓ **Multiple formats**: Articles, books, theses, patents  
✓ **Full-text search**: Not just abstracts  

Key strategies:
- Use advanced operators for precision
- Combine author, title, source searches
- Track citations for impact
- Export systematically to citation manager
- Respect rate limits and access policies
- Verify metadata with CrossRef/PubMed

For biomedical research, complement with PubMed for MeSH terms and curated metadata.

### `references/metadata_extraction.md`

# Metadata Extraction Guide

Comprehensive guide to extracting accurate citation metadata from DOIs, PMIDs, arXiv IDs, and URLs using various APIs and services.

## Overview

Accurate metadata is essential for proper citations. This guide covers:
- Identifying paper identifiers (DOI, PMID, arXiv ID)
- Querying metadata APIs (CrossRef, PubMed, arXiv, DataCite)
- Required BibTeX fields by entry type
- Handling edge cases and special situations
- Validating extracted metadata

## Paper Identifiers

### DOI (Digital Object Identifier)

**Format**: `10.XXXX/suffix`

**Examples**:
```
10.1038/s41586-021-03819-2    # Nature article
10.1126/science.aam9317       # Science article
10.1016/j.cell.2023.01.001    # Cell article
10.1371/journal.pone.0123456  # PLOS ONE article
```

**Properties**:
- Permanent identifier
- Most reliable for metadata
- Resolves to current location
- Publisher-assigned

**Where to find**:
- First page of article
- Article webpage
- CrossRef, Google Scholar, PubMed
- Usually prominent on publisher site

### PMID (PubMed ID)

**Format**: 8-digit number (typically)

**Examples**:
```
34265844
28445112
35476778
```

**Properties**:
- Specific to PubMed database
- Biomedical literature only
- Assigned by NCBI
- Permanent identifier

**Where to find**:
- PubMed search results
- Article page on PubMed
- Often in article PDF footer
- PMC (PubMed Central) pages

### PMCID (PubMed Central ID)

**Format**: PMC followed by numbers

**Examples**:
```
PMC8287551
PMC7456789
```

**Properties**:
- Free full-text articles in PMC
- Subset of PubMed articles
- Open access or author manuscripts

### arXiv ID

**Format**: YYMM.NNNNN or archive/YYMMNNN

**Examples**:
```
2103.14030        # New format (since 2007)
2401.12345        # 2024 submission
arXiv:hep-th/9901001  # Old format
```

**Properties**:
- Preprints (not peer-reviewed)
- Physics, math, CS, q-bio, etc.
- Version tracking (v1, v2, etc.)
- Free, open access

**Where to find**:
- arXiv.org
- Often cited before publication
- Paper PDF header

### Other Identifiers

**ISBN** (Books):
```
978-0-12-345678-9
0-123-45678-9
```

**arXiv category**:
```
cs.LG    # Computer Science - Machine Learning
q-bio.QM # Quantitative Biology - Quantitative Methods
math.ST  # Mathematics - Statistics
```

## Metadata APIs

### CrossRef API

**Primary source for DOIs** - Most comprehensive metadata for journal articles.

**Base URL**: `https://api.crossref.org/works/`

**No API key required**, but polite pool recommended:
- Add email to User-Agent
- Gets better service
- No rate limits

#### Basic DOI Lookup

**Request**:
```
GET https://api.crossref.org/works/10.1038/s41586-021-03819-2
```

**Response** (simplified):
```json
{
  "message": {
    "DOI": "10.1038/s41586-021-03819-2",
    "title": ["Article title here"],
    "author": [
      {"given": "John", "family": "Smith"},
      {"given": "Jane", "family": "Doe"}
    ],
    "container-title": ["Nature"],
    "volume": "595",
    "issue": "7865",
    "page": "123-128",
    "published-print": {"date-parts": [[2021, 7, 1]]},
    "publisher": "Springer Nature",
    "type": "journal-article",
    "ISSN": ["0028-0836"]
  }
}
```

#### Fields Available

**Always present**:
- `DOI`: Digital Object Identifier
- `title`: Article title (array)
- `type`: Content type (journal-article, book-chapter, etc.)

**Usually present**:
- `author`: Array of author objects
- `container-title`: Journal/book title
- `published-print` or `published-online`: Publication date
- `volume`, `issue`, `page`: Publication details
- `publisher`: Publisher name

**Sometimes present**:
- `abstract`: Article abstract
- `subject`: Subject categories
- `ISSN`: Journal ISSN
- `ISBN`: Book ISBN
- `reference`: Reference list
- `is-referenced-by-count`: Citation count

#### Content Types

CrossRef `type` field values:
- `journal-article`: Journal articles
- `book-chapter`: Book chapters
- `book`: Books
- `proceedings-article`: Conference papers
- `posted-content`: Preprints
- `dataset`: Research datasets
- `report`: Technical reports
- `dissertation`: Theses/dissertations

### PubMed E-utilities API

**Specialized for biomedical literature** - Curated metadata with MeSH terms.

**Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

**API key recommended** (free):
- Higher rate limits
- Better performance

#### PMID to Metadata

**Step 1: EFetch for full record**

```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?
  db=pubmed&
  id=34265844&
  retmode=xml&
  api_key=YOUR_KEY
```

**Response**: XML with comprehensive metadata

**Step 2: Parse XML**

Key fields:
```xml
<PubmedArticle>
  <MedlineCitation>
    <PMID>34265844</PMID>
    <Article>
      <ArticleTitle>Title here</ArticleTitle>
      <AuthorList>
        <Author><LastName>Smith</LastName><ForeName>John</ForeName></Author>
      </AuthorList>
      <Journal>
        <Title>Nature</Title>
        <JournalIssue>
          <Volume>595</Volume>
          <Issue>7865</Issue>
          <PubDate><Year>2021</Year></PubDate>
        </JournalIssue>
      </Journal>
      <Pagination><MedlinePgn>123-128</MedlinePgn></Pagination>
      <Abstract><AbstractText>Abstract text here</AbstractText></Abstract>
    </Article>
  </MedlineCitation>
  <PubmedData>
    <ArticleIdList>
      <ArticleId IdType="doi">10.1038/s41586-021-03819-2</ArticleId>
      <ArticleId IdType="pmc">PMC8287551</ArticleId>
    </ArticleIdList>
  </PubmedData>
</PubmedArticle>
```

#### Unique PubMed Fields

**MeSH Terms**: Controlled vocabulary
```xml
<MeshHeadingList>
  <MeshHeading>
    <DescriptorName UI="D003920">Diabetes Mellitus</DescriptorName>
  </MeshHeading>
</MeshHeadingList>
```

**Publication Types**:
```xml
<PublicationTypeList>
  <PublicationType UI="D016428">Journal Article</PublicationType>
  <PublicationType UI="D016449">Randomized Controlled Trial</PublicationType>
</PublicationTypeList>
```

**Grant Information**:
```xml
<GrantList>
  <Grant>
    <GrantID>R01-123456</GrantID>
    <Agency>NIAID NIH HHS</Agency>
    <Country>United States</Country>
  </Grant>
</GrantList>
```

### arXiv API

**Preprints in physics, math, CS, q-bio** - Free, open access.

**Base URL**: `http://export.arxiv.org/api/query`

**No API key required**

#### arXiv ID to Metadata

**Request**:
```
GET http://export.arxiv.org/api/query?id_list=2103.14030
```

**Response**: Atom XML

```xml
<entry>
  <id>http://arxiv.org/abs/2103.14030v2</id>
  <title>Highly accurate protein structure prediction with AlphaFold</title>
  <author><name>John Jumper</name></author>
  <author><name>Richard Evans</name></author>
  <published>2021-03-26T17:47:17Z</published>
  <updated>2021-07-01T16:51:46Z</updated>
  <summary>Abstract text here...</summary>
  <arxiv:doi>10.1038/s41586-021-03819-2</arxiv:doi>
  <category term="q-bio.BM" scheme="http://arxiv.org/schemas/atom"/>
  <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
</entry>
```

#### Key Fields

- `id`: arXiv URL
- `title`: Preprint title
- `author`: Author list
- `published`: First version date
- `updated`: Latest version date
- `summary`: Abstract
- `arxiv:doi`: DOI if published
- `arxiv:journal_ref`: Journal reference if published
- `category`: arXiv categories

#### Version Tracking

arXiv tracks versions:
- `v1`: Initial submission
- `v2`, `v3`, etc.: Revisions

**Always check** if preprint has been published in journal (use DOI if available).

### DataCite API

**Research datasets, software, other outputs** - Assigns DOIs to non-traditional scholarly works.

**Base URL**: `https://api.datacite.org/dois/`

**Similar to CrossRef** but for datasets, software, code, etc.

**Request**:
```
GET https://api.datacite.org/dois/10.5281/zenodo.1234567
```

**Response**: JSON with metadata for dataset/software

## Required BibTeX Fields

### @article (Journal Articles)

**Required**:
- `author`: Author names
- `title`: Article title
- `journal`: Journal name
- `year`: Publication year

**Optional but recommended**:
- `volume`: Volume number
- `number`: Issue number
- `pages`: Page range (e.g., 123--145)
- `doi`: Digital Object Identifier
- `url`: URL if no DOI
- `month`: Publication month

**Example**:
```bibtex
@article{Smith2024,
  author  = {Smith, John and Doe, Jane},
  title   = {Novel Approach to Protein Folding},
  journal = {Nature},
  year    = {2024},
  volume  = {625},
  number  = {8001},
  pages   = {123--145},
  doi     = {10.1038/nature12345}
}
```

### @book (Books)

**Required**:
- `author` or `editor`: Author(s) or editor(s)
- `title`: Book title
- `publisher`: Publisher name
- `year`: Publication year

**Optional but recommended**:
- `edition`: Edition number (if not first)
- `address`: Publisher location
- `isbn`: ISBN
- `url`: URL
- `series`: Series name

**Example**:
```bibtex
@book{Kumar2021,
  author    = {Kumar, Vinay and Abbas, Abul K. and Aster, Jon C.},
  title     = {Robbins and Cotran Pathologic Basis of Disease},
  publisher = {Elsevier},
  year      = {2021},
  edition   = {10},
  isbn      = {978-0-323-53113-9}
}
```

### @inproceedings (Conference Papers)

**Required**:
- `author`: Author names
- `title`: Paper title
- `booktitle`: Conference/proceedings name
- `year`: Year

**Optional but recommended**:
- `pages`: Page range
- `organization`: Organizing body
- `publisher`: Publisher
- `address`: Conference location
- `month`: Conference month
- `doi`: DOI if available

**Example**:
```bibtex
@inproceedings{Vaswani2017,
  author    = {Vaswani, Ashish and Shazeer, Noam and others},
  title     = {Attention is All You Need},
  booktitle = {Advances in Neural Information Processing Systems},
  year      = {2017},
  pages     = {5998--6008},
  volume    = {30}
}
```

### @incollection (Book Chapters)

**Required**:
- `author`: Chapter author(s)
- `title`: Chapter title
- `booktitle`: Book title
- `publisher`: Publisher name
- `year`: Publication year

**Optional but recommended**:
- `editor`: Book editor(s)
- `pages`: Chapter page range
- `chapter`: Chapter number
- `edition`: Edition
- `address`: Publisher location

**Example**:
```bibtex
@incollection{Brown2020,
  author    = {Brown, Peter O. and Botstein, David},
  title     = {Exploring the New World of the Genome with {DNA} Microarrays},
  booktitle = {DNA Microarrays: A Molecular Cloning Manual},
  editor    = {Eisen, Michael B. and Brown, Patrick O.},
  publisher = {Cold Spring Harbor Laboratory Press},
  year      = {2020},
  pages     = {1--45}
}
```

### @phdthesis (Dissertations)

**Required**:
- `author`: Author name
- `title`: Thesis title
- `school`: Institution
- `year`: Year

**Optional**:
- `type`: Type (e.g., "PhD dissertation")
- `address`: Institution location
- `month`: Month
- `url`: URL

**Example**:
```bibtex
@phdthesis{Johnson2023,
  author = {Johnson, Mary L.},
  title  = {Novel Approaches to Cancer Immunotherapy},
  school = {Stanford University},
  year   = {2023},
  type   = {{PhD} dissertation}
}
```

### @misc (Preprints, Software, Datasets)

**Required**:
- `author`: Author(s)
- `title`: Title
- `year`: Year

**For preprints, add**:
- `howpublished`: Repository (e.g., "bioRxiv")
- `doi`: Preprint DOI
- `note`: Preprint ID

**Example (preprint)**:
```bibtex
@misc{Zhang2024,
  author       = {Zhang, Yi and Chen, Li and Wang, Hui},
  title        = {Novel Therapeutic Targets in Alzheimer's Disease},
  year         = {2024},
  howpublished = {bioRxiv},
  doi          = {10.1101/2024.01.001},
  note         = {Preprint}
}
```

**Example (software)**:
```bibtex
@misc{AlphaFold2021,
  author       = {DeepMind},
  title        = {{AlphaFold} Protein Structure Database},
  year         = {2021},
  howpublished = {Software},
  url          = {https://alphafold.ebi.ac.uk/},
  doi          = {10.5281/zenodo.5123456}
}
```

## Extraction Workflows

### From DOI

**Best practice** - Most reliable source:

```bash
# Single DOI
python scripts/extract_metadata.py --doi 10.1038/s41586-021-03819-2

# Multiple DOIs
python scripts/extract_metadata.py \
  --doi 10.1038/nature12345 \
  --doi 10.1126/science.abc1234 \
  --output refs.bib
```

**Process**:
1. Query CrossRef API with DOI
2. Parse JSON response
3. Extract required fields
4. Determine entry type (@article, @book, etc.)
5. Format as BibTeX
6. Validate completeness

### From PMID

**For biomedical literature**:

```bash
# Single PMID
python scripts/extract_metadata.py --pmid 34265844

# Multiple PMIDs
python scripts/extract_metadata.py \
  --pmid 34265844 \
  --pmid 28445112 \
  --output refs.bib
```

**Process**:
1. Query PubMed EFetch with PMID
2. Parse XML response
3. Extract metadata including MeSH terms
4. Check for DOI in response
5. If DOI exists, optionally query CrossRef for additional metadata
6. Format as BibTeX

### From arXiv ID

**For preprints**:

```bash
python scripts/extract_metadata.py --arxiv 2103.14030
```

**Process**:
1. Query arXiv API with ID
2. Parse Atom XML response
3. Check for published version (DOI in response)
4. If published: Use DOI and CrossRef
5. If not published: Use preprint metadata
6. Format as @misc with preprint note

**Important**: Always check if preprint has been published!

### From URL

**When you only have URL**:

```bash
python scripts/extract_metadata.py \
  --url "https://www.nature.com/articles/s41586-021-03819-2"
```

**Process**:
1. Parse URL to extract identifier
2. Identify type (DOI, PMID, arXiv)
3. Extract identifier from URL
4. Query appropriate API
5. Format as BibTeX

**URL patterns**:
```
# DOI URLs
https://doi.org/10.1038/nature12345
https://dx.doi.org/10.1126/science.abc123
https://www.nature.com/articles/s41586-021-03819-2

# PubMed URLs
https://pubmed.ncbi.nlm.nih.gov/34265844/
https://www.ncbi.nlm.nih.gov/pubmed/34265844

# arXiv URLs
https://arxiv.org/abs/2103.14030
https://arxiv.org/pdf/2103.14030.pdf
```

### Batch Processing

**From file with mixed identifiers**:

```bash
# Create file with one identifier per line
# identifiers.txt:
#   10.1038/nature12345
#   34265844
#   2103.14030
#   https://doi.org/10.1126/science.abc123

python scripts/extract_metadata.py \
  --input identifiers.txt \
  --output references.bib
```

**Process**:
- Script auto-detects identifier type
- Queries appropriate API
- Combines all into single BibTeX file
- Handles errors gracefully

## Special Cases and Edge Cases

### Preprints Later Published

**Issue**: Preprint cited, but journal version now available.

**Solution**:
1. Check arXiv metadata for DOI field
2. If DOI present, use published version
3. Update citation to journal article
4. Note preprint version in comments if needed

**Example**:
```bibtex
% Originally: arXiv:2103.14030
% Published as:
@article{Jumper2021,
  author  = {Jumper, John and Evans, Richard and others},
  title   = {Highly Accurate Protein Structure Prediction with {AlphaFold}},
  journal = {Nature},
  year    = {2021},
  volume  = {596},
  pages   = {583--589},
  doi     = {10.1038/s41586-021-03819-2}
}
```

### Multiple Authors (et al.)

**Issue**: Many authors (10+).

**BibTeX practice**:
- Include all authors if <10
- Use "and others" for 10+
- Or list all (journals vary)

**Example**:
```bibtex
@article{LargeCollaboration2024,
  author = {First, Author and Second, Author and Third, Author and others},
  ...
}
```

### Author Name Variations

**Issue**: Authors publish under different name formats.

**Standardization**:
```
# Common variations
John Smith
John A. Smith
John Andrew Smith
J. A. Smith
Smith, J.
Smith, J. A.

# BibTeX format (recommended)
author = {Smith, John A.}
```

**Extraction preference**:
1. Use full name if available
2. Include middle initial if available
3. Format: Last, First Middle

### No DOI Available

**Issue**: Older papers or books without DOIs.

**Solutions**:
1. Use PMID if available (biomedical)
2. Use ISBN for books
3. Use URL to stable source
4. Include full publication details

**Example**:
```bibtex
@article{OldPaper1995,
  author  = {Author, Name},
  title   = {Title Here},
  journal = {Journal Name},
  year    = {1995},
  volume  = {123},
  pages   = {45--67},
  url     = {https://stable-url-here},
  note    = {PMID: 12345678}
}
```

### Conference Papers vs Journal Articles

**Issue**: Same work published in both.

**Best practice**:
- Cite journal version if both available
- Journal version is archival
- Conference version for timeliness

**If citing conference**:
```bibtex
@inproceedings{Smith2024conf,
  author    = {Smith, John},
  title     = {Title},
  booktitle = {Proceedings of NeurIPS 2024},
  year      = {2024}
}
```

**If citing journal**:
```bibtex
@article{Smith2024journal,
  author  = {Smith, John},
  title   = {Title},
  journal = {Journal of Machine Learning Research},
  year    = {2024}
}
```

### Book Chapters vs Edited Collections

**Extract correctly**:
- Chapter: Use `@incollection`
- Whole book: Use `@book`
- Book editor: List in `editor` field
- Chapter author: List in `author` field

### Datasets and Software

**Use @misc** with appropriate fields:

```bibtex
@misc{DatasetName2024,
  author       = {Author, Name},
  title        = {Dataset Title},
  year         = {2024},
  howpublished = {Zenodo},
  doi          = {10.5281/zenodo.123456},
  note         = {Version 1.2}
}
```

## Validation After Extraction

Always validate extracted metadata:

```bash
python scripts/validate_citations.py extracted_refs.bib
```

**Check**:
- All required fields present
- DOI resolves correctly
- Author names formatted consistently
- Year is reasonable (4 digits)
- Journal/publisher names correct
- Page ranges use -- not -
- Special characters handled properly

## Best Practices

### 1. Prefer DOI When Available

DOIs provide:
- Permanent identifier
- Best metadata source
- Publisher-verified information
- Resolvable link

### 2. Verify Automatically Extracted Metadata

Spot-check:
- Author names match publication
- Title matches (including capitalization)
- Year is correct
- Journal name is complete

### 3. Handle Special Characters

**LaTeX special characters**:
- Protect capitalization: `{AlphaFold}`
- Handle accents: `M{\"u}ller` or use Unicode
- Chemical formulas: `H$_2$O` or `\ce{H2O}`

### 4. Use Consistent Citation Keys

**Convention**: `FirstAuthorYEARkeyword`
```
Smith2024protein
Doe2023machine
Johnson2024cancer
```

### 5. Include DOI for Modern Papers

All papers published after ~2000 should have DOI:
```bibtex
doi = {10.1038/nature12345}
```

### 6. Document Source

For non-standard sources, add note:
```bibtex
note = {Preprint, not peer-reviewed}
note = {Technical report}
note = {Dataset accompanying [citation]}
```

## Summary

Metadata extraction workflow:

1. **Identify**: Determine identifier type (DOI, PMID, arXiv, URL)
2. **Query**: Use appropriate API (CrossRef, PubMed, arXiv)
3. **Extract**: Parse response for required fields
4. **Format**: Create properly formatted BibTeX entry
5. **Validate**: Check completeness and accuracy
6. **Verify**: Spot-check critical citations

**Use scripts** to automate:
- `extract_metadata.py`: Universal extractor
- `doi_to_bibtex.py`: Quick DOI conversion
- `validate_citations.py`: Verify accuracy

**Always validate** extracted metadata before final submission!

### `references/pubmed_search.md`

# PubMed Search Guide

Comprehensive guide to searching PubMed for biomedical and life sciences literature, including MeSH terms, field tags, advanced search strategies, and E-utilities API usage.

## Overview

PubMed is the premier database for biomedical literature:
- **Coverage**: 35+ million citations
- **Scope**: Biomedical and life sciences
- **Sources**: MEDLINE, life science journals, online books
- **Authority**: Maintained by National Library of Medicine (NLM) / NCBI
- **Access**: Free, no account required
- **Updates**: Daily with new citations
- **Curation**: High-quality metadata, MeSH indexing

## Basic Search

### Simple Keyword Search

PubMed automatically maps terms to MeSH and searches multiple fields:

```
diabetes
CRISPR gene editing
Alzheimer's disease treatment
cancer immunotherapy
```

**Automatic Features**:
- Automatic MeSH mapping
- Plural/singular variants
- Abbreviation expansion
- Spell checking

### Exact Phrase Search

Use quotation marks for exact phrases:

```
"CRISPR-Cas9"
"systematic review"
"randomized controlled trial"
"machine learning"
```

## MeSH (Medical Subject Headings)

### What is MeSH?

MeSH is a controlled vocabulary thesaurus for indexing biomedical literature:
- **Hierarchical structure**: Organized in tree structures
- **Consistent indexing**: Same concept always tagged the same way
- **Comprehensive**: Covers diseases, drugs, anatomy, techniques, etc.
- **Professional curation**: NLM indexers assign MeSH terms

### Finding MeSH Terms

**MeSH Browser**: https://meshb.nlm.nih.gov/search

**Example**:
```
Search: "heart attack"
MeSH term: "Myocardial Infarction"
```

**In PubMed**:
1. Search with keyword
2. Check "MeSH Terms" in left sidebar
3. Select relevant MeSH terms
4. Add to search

### Using MeSH in Searches

**Basic MeSH search**:
```
"Diabetes Mellitus"[MeSH]
"CRISPR-Cas Systems"[MeSH]
"Alzheimer Disease"[MeSH]
"Neoplasms"[MeSH]
```

**MeSH with subheadings**:
```
"Diabetes Mellitus/drug therapy"[MeSH]
"Neoplasms/genetics"[MeSH]
"Heart Failure/prevention and control"[MeSH]
```

**Common subheadings**:
- `/drug therapy`: Drug treatment
- `/diagnosis`: Diagnostic aspects
- `/genetics`: Genetic aspects
- `/epidemiology`: Occurrence and distribution
- `/prevention and control`: Prevention methods
- `/etiology`: Causes
- `/surgery`: Surgical treatment
- `/metabolism`: Metabolic aspects

### MeSH Explosion

By default, MeSH searches include narrower terms (explosion):

```
"Neoplasms"[MeSH]
# Includes: Breast Neoplasms, Lung Neoplasms, etc.
```

**Disable explosion** (exact term only):
```
"Neoplasms"[MeSH:NoExp]
```

### MeSH Major Topic

Search only where MeSH term is a major focus:

```
"Diabetes Mellitus"[MeSH Major Topic]
# Only papers where diabetes is main topic
```

## Field Tags

Field tags specify which part of the record to search.

### Common Field Tags

**Title and Abstract**:
```
cancer[Title]                    # In title only
treatment[Title/Abstract]        # In title or abstract
"machine learning"[Title/Abstract]
```

**Author**:
```
"Smith J"[Author]
"Doudna JA"[Author]
"Collins FS"[Author]
```

**Author - Full Name**:
```
"Smith, John"[Full Author Name]
```

**Journal**:
```
"Nature"[Journal]
"Science"[Journal]
"New England Journal of Medicine"[Journal]
"Nat Commun"[Journal]           # Abbreviated form
```

**Publication Date**:
```
2023[Publication Date]
2020:2024[Publication Date]      # Date range
2023/01/01:2023/12/31[Publication Date]
```

**Date Created**:
```
2023[Date - Create]              # When added to PubMed
```

**Publication Type**:
```
"Review"[Publication Type]
"Clinical Trial"[Publication Type]
"Meta-Analysis"[Publication Type]
"Randomized Controlled Trial"[Publication Type]
```

**Language**:
```
English[Language]
French[Language]
```

**DOI**:
```
10.1038/nature12345[DOI]
```

**PMID (PubMed ID)**:
```
12345678[PMID]
```

**Article ID**:
```
PMC1234567[PMC]                  # PubMed Central ID
```

### Less Common But Useful Tags

```
humans[MeSH Terms]               # Only human studies
animals[MeSH Terms]              # Only animal studies
"United States"[Place of Publication]
nih[Grant Number]                # NIH-funded research
"Female"[Sex]                    # Female subjects
"Aged, 80 and over"[Age]        # Elderly subjects
```

## Boolean Operators

Combine search terms with Boolean logic.

### AND

Both terms must be present (default behavior):

```
diabetes AND treatment
"CRISPR-Cas9" AND "gene editing"
cancer AND immunotherapy AND "clinical trial"[Publication Type]
```

### OR

Either term must be present:

```
"heart attack" OR "myocardial infarction"
diabetes OR "diabetes mellitus"
CRISPR OR Cas9 OR "gene editing"
```

**Use case**: Synonyms and related terms

### NOT

Exclude terms:

```
cancer NOT review
diabetes NOT animal
"machine learning" NOT "deep learning"
```

**Caution**: May exclude relevant papers that mention both terms.

### Combining Operators

Use parentheses for complex logic:

```
(diabetes OR "diabetes mellitus") AND (treatment OR therapy)

("CRISPR" OR "gene editing") AND ("therapeutic" OR "therapy") 
  AND 2020:2024[Publication Date]

(cancer OR neoplasm) AND (immunotherapy OR "immune checkpoint inhibitor") 
  AND ("clinical trial"[Publication Type] OR "randomized controlled trial"[Publication Type])
```

## Advanced Search Builder

**Access**: https://pubmed.ncbi.nlm.nih.gov/advanced/

**Features**:
- Visual query builder
- Add multiple query boxes
- Select field tags from dropdowns
- Combine with AND/OR/NOT
- Preview results
- Shows final query string
- Save queries

**Workflow**:
1. Add search terms in separate boxes
2. Select field tags
3. Choose Boolean operators
4. Preview results
5. Refine as needed
6. Copy final query string
7. Use in scripts or save

**Example built query**:
```
#1: "Diabetes Mellitus, Type 2"[MeSH]
#2: "Metformin"[MeSH]
#3: "Clinical Trial"[Publication Type]
#4: 2020:2024[Publication Date]
#5: #1 AND #2 AND #3 AND #4
```

## Filters and Limits

### Article Types

```
"Review"[Publication Type]
"Systematic Review"[Publication Type]
"Meta-Analysis"[Publication Type]
"Clinical Trial"[Publication Type]
"Randomized Controlled Trial"[Publication Type]
"Case Reports"[Publication Type]
"Comparative Study"[Publication Type]
```

### Species

```
humans[MeSH Terms]
mice[MeSH Terms]
rats[MeSH Terms]
```

### Sex

```
"Female"[MeSH Terms]
"Male"[MeSH Terms]
```

### Age Groups

```
"Infant"[MeSH Terms]
"Child"[MeSH Terms]
"Adolescent"[MeSH Terms]
"Adult"[MeSH Terms]
"Aged"[MeSH Terms]
"Aged, 80 and over"[MeSH Terms]
```

### Text Availability

```
free full text[Filter]           # Free full-text available
```

### Journal Categories

```
"Journal Article"[Publication Type]
```

## E-utilities API

NCBI provides programmatic access via E-utilities (Entrez Programming Utilities).

### Overview

**Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

**Main Tools**:
- **ESearch**: Search and retrieve PMIDs
- **EFetch**: Retrieve full records
- **ESummary**: Retrieve document summaries
- **ELink**: Find related articles
- **EInfo**: Database statistics

**No API key required**, but recommended for:
- Higher rate limits (10/sec vs 3/sec)
- Better performance
- Identify your project

**Get API key**: https://www.ncbi.nlm.nih.gov/account/

### ESearch - Search PubMed

Retrieve PMIDs for a query.

**Endpoint**: `/esearch.fcgi`

**Parameters**:
- `db`: Database (pubmed)
- `term`: Search query
- `retmax`: Maximum results (default 20, max 10000)
- `retstart`: Starting position (for pagination)
- `sort`: Sort order (relevance, pub_date, author)
- `api_key`: Your API key (optional but recommended)

**Example URL**:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?
  db=pubmed&
  term=diabetes+AND+treatment&
  retmax=100&
  retmode=json&
  api_key=YOUR_API_KEY
```

**Response**:
```json
{
  "esearchresult": {
    "count": "250000",
    "retmax": "100",
    "idlist": ["12345678", "12345679", ...]
  }
}
```

### EFetch - Retrieve Records

Get full metadata for PMIDs.

**Endpoint**: `/efetch.fcgi`

**Parameters**:
- `db`: Database (pubmed)
- `id`: Comma-separated PMIDs
- `retmode`: Format (xml, json, text)
- `rettype`: Type (abstract, medline, full)
- `api_key`: Your API key

**Example URL**:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?
  db=pubmed&
  id=12345678,12345679&
  retmode=xml&
  api_key=YOUR_API_KEY
```

**Response**: XML with complete metadata including:
- Title
- Authors (with affiliations)
- Abstract
- Journal
- Publication date
- DOI
- PMID, PMCID
- MeSH terms
- Keywords

### ESummary - Get Summaries

Lighter-weight alternative to EFetch.

**Example**:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?
  db=pubmed&
  id=12345678&
  retmode=json&
  api_key=YOUR_API_KEY
```

**Returns**: Key metadata without full abstract and details.

### ELink - Find Related Articles

Find related articles or links to other databases.

**Example**:
```
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?
  dbfrom=pubmed&
  db=pubmed&
  id=12345678&
  linkname=pubmed_pubmed_citedin
```

**Link types**:
- `pubmed_pubmed`: Related articles
- `pubmed_pubmed_citedin`: Papers citing this article
- `pubmed_pmc`: PMC full-text versions
- `pubmed_protein`: Related protein records

### Rate Limiting

**Without API key**:
- 3 requests per second
- Block if exceeded

**With API key**:
- 10 requests per second
- Better for programmatic access

**Best practice**:
```python
import time
time.sleep(0.34)  # ~3 requests/second
# or
time.sleep(0.11)  # ~10 requests/second with API key
```

### API Key Usage

**Get API key**:
1. Create NCBI account: https://www.ncbi.nlm.nih.gov/account/
2. Settings → API Key Management
3. Create new API key
4. Copy key

**Use in requests**:
```
&api_key=YOUR_API_KEY_HERE
```

**Store securely**:
```bash
# In environment variable
export NCBI_API_KEY="your_key_here"

# In script
import os
api_key = os.getenv('NCBI_API_KEY')
```

## Search Strategies

### Comprehensive Systematic Search

For systematic reviews and meta-analyses:

```
# 1. Identify key concepts
Concept 1: Diabetes
Concept 2: Treatment
Concept 3: Outcomes

# 2. Find MeSH terms and synonyms
Concept 1: "Diabetes Mellitus"[MeSH] OR diabetes OR diabetic
Concept 2: "Drug Therapy"[MeSH] OR treatment OR therapy OR medication
Concept 3: "Treatment Outcome"[MeSH] OR outcome OR efficacy OR effectiveness

# 3. Combine with AND
("Diabetes Mellitus"[MeSH] OR diabetes OR diabetic) 
  AND ("Drug Therapy"[MeSH] OR treatment OR therapy OR medication)
  AND ("Treatment Outcome"[MeSH] OR outcome OR efficacy OR effectiveness)

# 4. Add filters
AND 2015:2024[Publication Date]
AND ("Clinical Trial"[Publication Type] OR "Randomized Controlled Trial"[Publication Type])
AND English[Language]
AND humans[MeSH Terms]
```

### Finding Clinical Trials

```
# Specific disease + clinical trials
"Alzheimer Disease"[MeSH] 
  AND ("Clinical Trial"[Publication Type] 
       OR "Randomized Controlled Trial"[Publication Type])
  AND 2020:2024[Publication Date]

# Specific drug trials
"Metformin"[MeSH] 
  AND "Diabetes Mellitus, Type 2"[MeSH]
  AND "Randomized Controlled Trial"[Publication Type]
```

### Finding Reviews

```
# Systematic reviews on topic
"CRISPR-Cas Systems"[MeSH] 
  AND ("Systematic Review"[Publication Type] OR "Meta-Analysis"[Publication Type])

# Reviews in high-impact journals
cancer immunotherapy 
  AND "Review"[Publication Type]
  AND ("Nature"[Journal] OR "Science"[Journal] OR "Cell"[Journal])
```

### Finding Recent Papers

```
# Papers from last year
"machine learning"[Title/Abstract] 
  AND "drug discovery"[Title/Abstract]
  AND 2024[Publication Date]

# Recent papers in specific journal
"CRISPR"[Title/Abstract] 
  AND "Nature"[Journal]
  AND 2023:2024[Publication Date]
```

### Author Tracking

```
# Specific author's recent work
"Doudna JA"[Author] AND 2020:2024[Publication Date]

# Author + topic
"Church GM"[Author] AND "synthetic biology"[Title/Abstract]
```

### High-Quality Evidence

```
# Meta-analyses and systematic reviews
(diabetes OR "diabetes mellitus") 
  AND (treatment OR therapy)
  AND ("Meta-Analysis"[Publication Type] OR "Systematic Review"[Publication Type])

# RCTs only
cancer immunotherapy 
  AND "Randomized Controlled Trial"[Publication Type]
  AND 2020:2024[Publication Date]
```

## Script Integration

### search_pubmed.py Usage

**Basic search**:
```bash
python scripts/search_pubmed.py "diabetes treatment"
```

**With MeSH terms**:
```bash
python scripts/search_pubmed.py \
  --query '"Diabetes Mellitus"[MeSH] AND "Drug Therapy"[MeSH]'
```

**Date range filter**:
```bash
python scripts/search_pubmed.py "CRISPR" \
  --date-start 2020-01-01 \
  --date-end 2024-12-31 \
  --limit 200
```

**Publication type filter**:
```bash
python scripts/search_pubmed.py "cancer immunotherapy" \
  --publication-types "Clinical Trial,Randomized Controlled Trial" \
  --limit 100
```

**Export to BibTeX**:
```bash
python scripts/search_pubmed.py "Alzheimer's disease" \
  --limit 100 \
  --format bibtex \
  --output alzheimers.bib
```

**Complex query from file**:
```bash
# Save complex query in query.txt
cat > query.txt << 'EOF'
("Diabetes Mellitus, Type 2"[MeSH] OR "diabetes"[Title/Abstract])
AND ("Metformin"[MeSH] OR "metformin"[Title/Abstract])
AND "Randomized Controlled Trial"[Publication Type]
AND 2015:2024[Publication Date]
AND English[Language]
EOF

# Run search
python scripts/search_pubmed.py --query-file query.txt --limit 500
```

### Batch Searches

```bash
# Search multiple topics
TOPICS=("diabetes treatment" "cancer immunotherapy" "CRISPR gene editing")

for topic in "${TOPICS[@]}"; do
  python scripts/search_pubmed.py "$topic" \
    --limit 100 \
    --output "${topic// /_}.json"
  sleep 1
done
```

### Extract Metadata

```bash
# Search returns PMIDs
python scripts/search_pubmed.py "topic" --output results.json

# Extract full metadata
python scripts/extract_metadata.py \
  --input results.json \
  --output references.bib
```

## Tips and Best Practices

### Search Construction

1. **Start with MeSH terms**:
   - Use MeSH Browser to find correct terms
   - More precise than keyword search
   - Captures all papers on topic regardless of terminology

2. **Include text word variants**:
   ```
   # Better coverage
   ("Diabetes Mellitus"[MeSH] OR diabetes OR diabetic)
   ```

3. **Use field tags appropriately**:
   - `[MeSH]` for standardized concepts
   - `[Title/Abstract]` for specific terms
   - `[Author]` for known authors
   - `[Journal]` for specific venues

4. **Build incrementally**:
   ```
   # Step 1: Basic search
   diabetes
   
   # Step 2: Add specificity
   "Diabetes Mellitus, Type 2"[MeSH]
   
   # Step 3: Add treatment
   "Diabetes Mellitus, Type 2"[MeSH] AND "Metformin"[MeSH]
   
   # Step 4: Add study type
   "Diabetes Mellitus, Type 2"[MeSH] AND "Metformin"[MeSH] 
     AND "Clinical Trial"[Publication Type]
   
   # Step 5: Add date range
   ... AND 2020:2024[Publication Date]
   ```

### Optimizing Results

1. **Too many results**: Add filters
   - Restrict publication type
   - Narrow date range
   - Add more specific MeSH terms
   - Use Major Topic: `[MeSH Major Topic]`

2. **Too few results**: Broaden search
   - Remove restrictive filters
   - Use OR for synonyms
   - Expand date range
   - Use MeSH explosion (default)

3. **Irrelevant results**: Refine terms
   - Use more specific MeSH terms
   - Add exclusions with NOT
   - Use Title field instead of all fields
   - Add MeSH subheadings

### Quality Control

1. **Document search strategy**:
   - Save exact query string
   - Record search date
   - Note number of results
   - Save filters used

2. **Export systematically**:
   - Use consistent file naming
   - Export to JSON for flexibility
   - Convert to BibTeX as needed
   - Keep original search results

3. **Validate retrieved citations**:
   ```bash
   python scripts/validate_citations.py pubmed_results.bib
   ```

### Staying Current

1. **Set up search alerts**:
   - PubMed → Save search
   - Receive email updates
   - Daily, weekly, or monthly

2. **Track specific journals**:
   ```
   "Nature"[Journal] AND CRISPR[Title]
   ```

3. **Follow key authors**:
   ```
   "Church GM"[Author]
   ```

## Common Issues and Solutions

### Issue: MeSH Term Not Found

**Solution**: 
- Check spelling
- Use MeSH Browser
- Try related terms
- Use text word search as fallback

### Issue: Zero Results

**Solution**:
- Remove filters
- Check query syntax
- Use OR for broader search
- Try synonyms

### Issue: Poor Quality Results

**Solution**:
- Add publication type filters
- Restrict to recent years
- Use MeSH Major Topic
- Filter by journal quality

### Issue: Duplicates from Different Sources

**Solution**:
```bash
python scripts/format_bibtex.py results.bib \
  --deduplicate \
  --output clean.bib
```

### Issue: API Rate Limiting

**Solution**:
- Get API key (increases limit to 10/sec)
- Add delays in scripts
- Process in batches
- Use off-peak hours

## Summary

PubMed provides authoritative biomedical literature search:

✓ **Curated content**: MeSH indexing, quality control  
✓ **Precise search**: Field tags, MeSH terms, filters  
✓ **Programmatic access**: E-utilities API  
✓ **Free access**: No subscription required  
✓ **Comprehensive**: 35M+ citations, daily updates  

Key strategies:
- Use MeSH terms for precise searching
- Combine with text words for comprehensive coverage
- Apply appropriate field tags
- Filter by publication type and date
- Use E-utilities API for automation
- Document search strategy for reproducibility

For broader coverage across disciplines, complement with Google Scholar.

### `references/script_reference.md`

# Bundled Script Reference

Purpose, arguments, and usage examples for each script in `scripts/`:
`search_openalex.py`, `search_pubmed.py`, `search_google_scholar.py`,
`extract_metadata.py`, `validate_citations.py`, `format_bibtex.py`, and
`doi_to_bibtex.py`.

`_common.py` is not a command. It holds the brace-aware BibTeX parser, the
entry renderer, the page-range normaliser, and the citation-key scheme that
every script above shares — which is what lets entries found through different
databases deduplicate against each other.

## Tools and Scripts

### search_openalex.py

Search OpenAlex. No API key; ~250 million works across every discipline.

**Features**:
- Keyless REST API with cursor pagination
- Year range and work-type filtering
- Sort by relevance or citation count
- Abstracts reconstructed from OpenAlex's inverted index
- Open-access status on every record
- Export to JSON or BibTeX

**Usage**:
```bash
# Basic search
python scripts/search_openalex.py "quantum computing"

# Most-cited work in a window
python scripts/search_openalex.py "quantum computing" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100 \
  --sort-by citations \
  --output quantum_papers.json

# Reviews only, straight to BibTeX
python scripts/search_openalex.py "CRISPR gene editing" \
  --type review \
  --limit 50 \
  --format bibtex \
  --output crispr_reviews.bib
```

Set `OPENALEX_EMAIL` (or pass `--email`) to join OpenAlex's polite pool, which
is faster and more reliably available.

### search_google_scholar.py

Search Google Scholar and export results.

**Features**:
- Automated searching with rate limiting
- Pagination support
- Year range filtering
- Export to JSON or BibTeX
- Citation count information

**Usage**:
```bash
# Basic search
python scripts/search_google_scholar.py "quantum computing"

# Advanced search with filters
python scripts/search_google_scholar.py "quantum computing" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100 \
  --sort-by citations \
  --output quantum_papers.json

# Export directly to BibTeX
python scripts/search_google_scholar.py "machine learning" \
  --limit 50 \
  --format bibtex \
  --output ml_papers.bib
```

### search_pubmed.py

Search PubMed using E-utilities API.

**Features**:
- Complex query support (MeSH, field tags, Boolean)
- Date range filtering
- Publication type filtering
- Batch retrieval with metadata
- Export to JSON or BibTeX

**Usage**:
```bash
# Simple keyword search
python scripts/search_pubmed.py "CRISPR gene editing"

# Complex query with filters
python scripts/search_pubmed.py \
  --query '"CRISPR-Cas Systems"[MeSH] AND "therapeutic"[Title/Abstract]' \
  --date-start 2020-01-01 \
  --date-end 2024-12-31 \
  --publication-types "Clinical Trial,Review" \
  --limit 200 \
  --output crispr_therapeutic.json

# Export to BibTeX
python scripts/search_pubmed.py "Alzheimer's disease" \
  --limit 100 \
  --format bibtex \
  --output alzheimers.bib
```

### extract_metadata.py

Extract complete metadata from paper identifiers.

**Features**:
- Supports DOI, PMID, arXiv ID, URL
- Queries CrossRef, PubMed, arXiv APIs
- Handles multiple identifier types
- Batch processing
- Multiple output formats

**Usage**:
```bash
# Single DOI
python scripts/extract_metadata.py --doi 10.1038/s41586-021-03819-2

# Single PMID
python scripts/extract_metadata.py --pmid 34265844

# Single arXiv ID
python scripts/extract_metadata.py --arxiv 2103.14030

# From URL
python scripts/extract_metadata.py \
  --url "https://www.nature.com/articles/s41586-021-03819-2"

# Batch processing (file with one identifier per line)
python scripts/extract_metadata.py \
  --input paper_ids.txt \
  --output references.bib

# Different output formats
python scripts/extract_metadata.py \
  --doi 10.1038/nature12345 \
  --format json  # or bibtex, yaml
```

### validate_citations.py

Validate BibTeX entries for accuracy, completeness, citation count standard compliance, and manuscript integration.

**Features**:
- DOI verification via doi.org and CrossRef
- Required field checking
- Duplicate detection
- Format validation
- **Publication standard citation count checks** against specified venues (Nature, NeurIPS, review, etc.) or custom thresholds.
- **Mandatory post-writing checks** matching manuscript citations (Markdown or LaTeX) with defined BibTeX entries to detect unresolved/missing or unused references.
- Detailed reporting

**Usage**:
```bash
# Basic validation
python scripts/validate_citations.py references.bib

# Validate against a venue standard (e.g., Nature, NeurIPS, Literature Review)
python scripts/validate_citations.py references.bib --venue nature
python scripts/validate_citations.py references.bib --venue neurips
python scripts/validate_citations.py references.bib --venue review

# Validate with custom minimum citation count
python scripts/validate_citations.py references.bib --min-count 40

# Check references against a written manuscript file (detect missing or unused citations)
python scripts/validate_citations.py references.bib --manuscript paper.md

# Combined full validation
python scripts/validate_citations.py references.bib \
  --venue nature \
  --manuscript paper.md \
  --report validation_report.json \
  --verbose
```

### format_bibtex.py

Format and clean BibTeX files.

**Features**:
- Standardize formatting
- Sort entries (by key, year, author)
- Remove duplicates
- Validate syntax
- Fix common errors
- Enforce citation key conventions

**Usage**:
```bash
# Basic formatting
python scripts/format_bibtex.py references.bib

# Sort by year (newest first)
python scripts/format_bibtex.py references.bib \
  --sort year \
  --descending \
  --output sorted_refs.bib

# Remove duplicates
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --output clean_refs.bib

# Complete cleanup
python scripts/format_bibtex.py references.bib \
  --rekey \
  --deduplicate \
  --sort year \
  --output final_refs.bib
```

### doi_to_bibtex.py

Quick DOI to BibTeX conversion.

**Features**:
- Fast single DOI conversion
- Batch processing
- Multiple output formats
- Clipboard support

**Usage**:
```bash
# Single DOI
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2

# Multiple DOIs
python scripts/doi_to_bibtex.py \
  10.1038/nature12345 \
  10.1126/science.abc1234 \
  10.1016/j.cell.2023.01.001

# From file (one DOI per line)
python scripts/doi_to_bibtex.py --input dois.txt --output references.bib

# Copy to clipboard (macOS; use xclip on Linux)
python scripts/doi_to_bibtex.py 10.1038/nature12345 | pbcopy
```

### `references/search_strategies.md`

# Search Strategies

Google Scholar and PubMed query construction: operators, field tags, MeSH terms,
date and publication-type filters, and worked query examples.

## Search Strategies

### Google Scholar Best Practices

**Finding Seminal and High-Impact Papers** (CRITICAL):

Always prioritize papers based on citation count, venue quality, and author reputation:

**Citation Count Thresholds:**
| Paper Age | Citations | Classification |
|-----------|-----------|----------------|
| 0-3 years | 20+ | Noteworthy |
| 0-3 years | 100+ | Highly Influential |
| 3-7 years | 100+ | Significant |
| 3-7 years | 500+ | Landmark Paper |
| 7+ years | 500+ | Seminal Work |
| 7+ years | 1000+ | Foundational |

**Venue Quality Tiers:**
- **Tier 1 (Prefer):** Nature, Science, Cell, NEJM, Lancet, JAMA, PNAS
- **Tier 2 (High Priority):** Impact Factor >10, top conferences (NeurIPS, ICML, ICLR)
- **Tier 3 (Good):** Specialized journals (IF 5-10)
- **Tier 4 (Sparingly):** Lower-impact peer-reviewed venues

**Author Reputation Indicators:**
- Senior researchers with h-index >40
- Multiple publications in Tier-1 venues
- Leadership at recognized institutions
- Awards and editorial positions

**Search Strategies for High-Impact Papers:**
- Sort by citation count (most cited first)
- Look for review articles from Tier-1 journals for overview
- Check "Cited by" for impact assessment and recent follow-up work
- Use citation alerts for tracking new citations to key papers
- Filter by top venues using `source:Nature` or `source:Science`
- Search for papers by known field leaders using `author:LastName`

**Advanced Operators** (full list in `references/google_scholar_search.md`):
```
"exact phrase"           # Exact phrase matching
author:lastname          # Search by author
intitle:keyword          # Search in title only
source:journal           # Search specific journal
-exclude                 # Exclude terms
OR                       # Alternative terms
2020..2024              # Year range
```

**Example Searches**:
```
# Find recent reviews on a topic
"CRISPR" intitle:review 2023..2024

# Find papers by specific author on topic
author:Church "synthetic biology"

# Find highly cited foundational work
"deep learning" 2012..2015 sort:citations

# Exclude surveys and focus on methods
"protein folding" -survey -review intitle:method
```

### PubMed Best Practices

**Using MeSH Terms**:
MeSH (Medical Subject Headings) provides controlled vocabulary for precise searching.

1. **Find MeSH terms** at https://meshb.nlm.nih.gov/search
2. **Use in queries**: `"Diabetes Mellitus, Type 2"[MeSH]`
3. **Combine with keywords** for comprehensive coverage

**Field Tags**:
```
[Title]              # Search in title only
[Title/Abstract]     # Search in title or abstract
[Author]             # Search by author name
[Journal]            # Search specific journal
[Publication Date]   # Date range
[Publication Type]   # Article type
[MeSH]              # MeSH term
```

**Building Complex Queries**:
```bash
# Clinical trials on diabetes treatment published recently
"Diabetes Mellitus, Type 2"[MeSH] AND "Drug Therapy"[MeSH] 
AND "Clinical Trial"[Publication Type] AND 2020:2024[Publication Date]

# Reviews on CRISPR in specific journal
"CRISPR-Cas Systems"[MeSH] AND "Nature"[Journal] AND "Review"[Publication Type]

# Specific author's recent work
"Smith AB"[Author] AND cancer[Title/Abstract] AND 2022:2024[Publication Date]
```

**E-utilities for Automation**:
The scripts use NCBI E-utilities API for programmatic access:
- **ESearch**: Search and retrieve PMIDs
- **EFetch**: Retrieve full metadata
- **ESummary**: Get summary information
- **ELink**: Find related articles

See `references/pubmed_search.md` for complete API documentation.

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared BibTeX parsing and rendering for the citation-management scripts.

Standard library only.

The parser here is brace-depth aware. That matters more than it sounds: a
regular expression of the form ``\\{([^}]*)\\}`` stops at the first closing
brace, so it truncates every title that protects a capitalised term --
``{Highly accurate prediction with {AlphaFold}}`` -- and writing the truncated
value back out produces a ``.bib`` file with unbalanced braces that no BibTeX
engine will read. Capitalisation protection is routine in real bibliographies,
and ``extract_metadata.py`` emits it deliberately, so the naive form corrupts
this skill's own output.

Every producer in this skill renders through :func:`render_entry` and keys
through :func:`citation_key`, so entries from Crossref, PubMed, OpenAlex, and
Scholar are directly comparable and deduplication works across sources.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from collections import OrderedDict
from typing import Dict, List, Optional

# Field order used when rendering. Anything not listed keeps its input order
# and is appended after these.
FIELD_ORDER = [
    'author', 'editor', 'title', 'booktitle', 'journal',
    'year', 'month', 'volume', 'number', 'pages',
    'publisher', 'address', 'edition', 'series',
    'school', 'institution', 'organization',
    'howpublished', 'doi', 'url', 'isbn', 'issn',
    'note', 'abstract', 'keywords',
]

# @string, @comment and @preamble are not bibliography entries.
_NON_ENTRY_TYPES = {'string', 'comment', 'preamble'}

_FIELD_NAME = re.compile(r'\s*([A-Za-z][A-Za-z0-9_+:.-]*)\s*=\s*(.*)$', re.DOTALL)


def _is_outer_braced(value: str) -> bool:
    """True when the whole value is wrapped in one matched brace pair."""
    if not (value.startswith('{') and value.endswith('}')):
        return False
    depth = 0
    for index, char in enumerate(value):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                # Only a wrapper if it closes at the very end; `{a} # {b}`
                # and `{a}{b}` must be left alone.
                return index == len(value) - 1
    return False


def _unwrap(value: str) -> str:
    """Strip one layer of delimiters, preserving any nested braces inside."""
    value = value.strip()
    if _is_outer_braced(value):
        return value[1:-1].strip()
    if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
        return value[1:-1].strip()
    return value


def _split_top_level(body: str) -> List[str]:
    """Split on commas that sit outside braces and quotes."""
    parts: List[str] = []
    buffer: List[str] = []
    depth = 0
    in_quote = False

    for char in body:
        if char == '"' and depth == 0:
            in_quote = not in_quote
        elif char == '{':
            depth += 1
        elif char == '}':
            depth -= 1

        if char == ',' and depth == 0 and not in_quote:
            parts.append(''.join(buffer))
            buffer = []
        else:
            buffer.append(char)

    parts.append(''.join(buffer))
    return parts


def parse_bibtex(content: str) -> List[Dict]:
    """Parse BibTeX source into entry dictionaries.

    Each entry is ``{'type', 'key', 'fields', 'raw'}`` with ``fields`` an
    ``OrderedDict`` of lowercased field names to their unwrapped values.
    Malformed or unterminated entries are skipped rather than raised on.
    """
    entries: List[Dict] = []
    length = len(content)
    position = 0

    while True:
        at = content.find('@', position)
        if at < 0:
            break

        cursor = at + 1
        while cursor < length and content[cursor].isalpha():
            cursor += 1
        entry_type = content[at + 1:cursor].lower()

        if not entry_type:
            position = at + 1
            continue

        while cursor < length and content[cursor].isspace():
            cursor += 1

        if cursor >= length or content[cursor] not in '{(':
            position = at + 1
            continue

        opener = content[cursor]
        closer = '}' if opener == '{' else ')'

        # Walk to the delimiter that matches the opener, counting depth.
        depth = 0
        end = -1
        scan = cursor
        while scan < length:
            char = content[scan]
            if char == opener:
                depth += 1
            elif char == closer:
                depth -= 1
                if depth == 0:
                    end = scan
                    break
            scan += 1

        if end < 0:
            # Unterminated entry: nothing reliable left to read.
            break

        position = end + 1

        if entry_type in _NON_ENTRY_TYPES:
            continue

        body = content[cursor + 1:end]
        chunks = _split_top_level(body)
        if not chunks:
            continue

        citation_key_text = chunks[0].strip()
        if not citation_key_text or '=' in citation_key_text:
            # No citation key -- not an entry we can work with.
            continue

        fields: "OrderedDict[str, str]" = OrderedDict()
        for chunk in chunks[1:]:
            if not chunk.strip():
                continue
            match = _FIELD_NAME.match(chunk)
            if not match:
                continue
            fields[match.group(1).lower()] = _unwrap(match.group(2))

        entries.append({
            'type': entry_type,
            'key': citation_key_text,
            'fields': fields,
            'raw': content[at:end + 1],
        })

    return entries


def parse_bibtex_file(filepath: str) -> List[Dict]:
    """Parse a BibTeX file, reporting read errors rather than raising."""
    try:
        with open(filepath, 'r', encoding='utf-8') as handle:
            return parse_bibtex(handle.read())
    except OSError as error:
        print(f'Error reading file: {error}', file=sys.stderr)
        return []


def render_entry(entry_type: str, key: str, fields: Dict[str, str]) -> str:
    """Render one entry with fields in a stable order and aligned values.

    Empty values are dropped, so callers can pass a dictionary built from
    metadata that may or may not have been populated.
    """
    present = OrderedDict()
    for name in FIELD_ORDER:
        value = fields.get(name)
        if value:
            present[name] = str(value)
    for name, value in fields.items():
        if name not in present and value:
            present[name] = str(value)

    if not present:
        return f'@{entry_type}{{{key},\n}}'

    width = max(len(name) for name in present)
    lines = [f'@{entry_type}{{{key},']
    rendered = [f'  {name.ljust(width)} = {{{value}}}' for name, value in present.items()]
    lines.append(',\n'.join(rendered))
    lines.append('}')
    return '\n'.join(lines)


_PAGE_RANGE = re.compile(r'^(\d+)\s*(?:-{1,3}|–|—)\s*(\d+)$')


def format_pages(raw: Optional[str]) -> str:
    """Normalise a page field to a BibTeX en-dash range.

    Handles the two mistakes the previous per-script implementations made:
    a blanket ``replace('-', '--')`` turned an already-correct ``583--589``
    into ``583----589``, and PubMed's abbreviated ``MedlinePgn`` ranges
    (``1123-30``) need their end page expanded to ``1123--1130`` rather than
    being left as a nonsensical ``1123--30``.

    Values that are not ranges -- article numbers such as ``e0123456``,
    or discontinuous lists -- are returned unchanged.
    """
    if not raw:
        return ''

    pages = re.sub(r'^\s*pp?\.\s*', '', str(raw).strip(), flags=re.IGNORECASE)
    match = _PAGE_RANGE.match(pages)
    if not match:
        return pages

    start, end = match.group(1), match.group(2)
    if len(end) < len(start):
        end = start[:len(start) - len(end)] + end
    return f'{start}--{end}'


def _ascii_fold(text: str) -> str:
    """Reduce accented Latin characters to ASCII (Muller from Müller)."""
    decomposed = unicodedata.normalize('NFKD', text)
    return ''.join(char for char in decomposed if not unicodedata.combining(char))


def sanitize_key(text: str) -> str:
    """Reduce a string to characters that are safe in a BibTeX citation key.

    Keys reach both LaTeX and, in some workflows, the filesystem, and their
    source is a publisher-controlled metadata record. Restricting them to
    ASCII letters and digits keeps `O'Brien` and `Müller` from producing an
    entry that LaTeX rejects.
    """
    return re.sub(r'[^A-Za-z0-9]', '', _ascii_fold(text or ''))


def _looks_like_initials(word: str) -> bool:
    """True for `J`, `JA`, `J.A.` -- the initials half of a PubMed author."""
    stripped = word.replace('.', '')
    return bool(stripped) and len(stripped) <= 3 and stripped.isupper()


def citation_key(authors: str, year: str, title: str) -> str:
    """Build the citation key used by every producer in this skill.

    ``<FirstAuthorSurname><Year><FirstSubstantiveTitleWord>``, ASCII-folded and
    stripped of anything outside ``[A-Za-z0-9]``. Sharing one scheme across
    Crossref, PubMed, OpenAlex, and Scholar output is what makes the
    deduplication in ``format_bibtex.py`` and ``validate_citations.py`` able to
    see the same paper twice.
    """
    surname = ''
    if authors:
        first = authors.split(' and ')[0].strip()
        if ',' in first:
            surname = first.split(',')[0]
        else:
            words = first.split()
            if not words:
                surname = ''
            elif len(words) > 1 and _looks_like_initials(words[-1]):
                # PubMed's comma-less form puts the surname first: `Smith JA`.
                surname = words[0]
            else:
                # Western given-name-first order: `John Smith`.
                surname = words[-1]

    surname = sanitize_key(surname) or 'unknown'

    digits = re.sub(r'[^0-9]', '', str(year or ''))
    year_part = digits[:4] if digits else 'XXXX'

    words = re.findall(r'[A-Za-z]{4,}', _ascii_fold(title or ''))
    keyword = words[0].lower() if words else 'paper'

    return f'{surname}{year_part}{keyword}'


# Terms whose capitalisation BibTeX would otherwise flatten in a title.
PROTECTED_TERMS = [
    'AlphaFold', 'CRISPR', 'COVID', 'SARS', 'DNA', 'RNA', 'mRNA', 'HIV',
    'AIDS', 'MRI', 'PCR', 'USA', 'UK', 'EU', 'GPU', 'CPU', 'AI', 'ML',
]


def protect_title(title: str) -> str:
    """Brace terms whose capitalisation must survive BibTeX style processing.

    Terms already inside braces are left alone, so running this twice is safe.
    """
    if not title:
        return ''

    for term in PROTECTED_TERMS:
        # Skip occurrences already wrapped, so the function is idempotent.
        title = re.sub(
            rf'(?<!\{{)\b{re.escape(term)}\b(?!\}})',
            f'{{{term}}}',
            title,
        )
    return title
```

### `scripts/doi_to_bibtex.py`

```python
#!/usr/bin/env python3
"""
DOI to BibTeX Converter
Quick utility to convert DOIs to BibTeX format using CrossRef API.
"""

import sys
import requests
import argparse
import time
import json
from typing import Optional, List

class DOIConverter:
    """Convert DOIs to BibTeX entries using CrossRef API."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DOIConverter/1.0 (Citation Management Tool; mailto:support@example.com)'
        })
    
    def doi_to_bibtex(self, doi: str) -> Optional[str]:
        """
        Convert a single DOI to BibTeX format.
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            BibTeX string or None if conversion fails
        """
        # Clean DOI (remove URL prefix if present)
        doi = doi.strip()
        if doi.startswith('https://doi.org/'):
            doi = doi.replace('https://doi.org/', '')
        elif doi.startswith('http://doi.org/'):
            doi = doi.replace('http://doi.org/', '')
        elif doi.startswith('doi:'):
            doi = doi.replace('doi:', '')
        
        # Request BibTeX from CrossRef content negotiation
        url = f'https://doi.org/{doi}'
        headers = {
            'Accept': 'application/x-bibtex',
            'User-Agent': 'DOIConverter/1.0 (Citation Management Tool)'
        }
        
        try:
            response = self.session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                bibtex = response.text.strip()
                # CrossRef sometimes returns entries with @data type, convert to @misc
                if bibtex.startswith('@data{'):
                    bibtex = bibtex.replace('@data{', '@misc{', 1)
                return bibtex
            elif response.status_code == 404:
                print(f'Error: DOI not found: {doi}', file=sys.stderr)
                return None
            else:
                print(f'Error: Failed to retrieve BibTeX for {doi} (status {response.status_code})', file=sys.stderr)
                return None
                
        except requests.exceptions.Timeout:
            print(f'Error: Request timeout for DOI: {doi}', file=sys.stderr)
            return None
        except requests.exceptions.RequestException as e:
            print(f'Error: Request failed for {doi}: {e}', file=sys.stderr)
            return None
    
    def convert_multiple(self, dois: List[str], delay: float = 0.5) -> List[str]:
        """
        Convert multiple DOIs to BibTeX.
        
        Args:
            dois: List of DOIs
            delay: Delay between requests (seconds) for rate limiting
            
        Returns:
            List of BibTeX entries (excludes failed conversions)
        """
        bibtex_entries = []
        
        for i, doi in enumerate(dois):
            print(f'Converting DOI {i+1}/{len(dois)}: {doi}', file=sys.stderr)
            bibtex = self.doi_to_bibtex(doi)
            
            if bibtex:
                bibtex_entries.append(bibtex)
            
            # Rate limiting
            if i < len(dois) - 1:  # Don't delay after last request
                time.sleep(delay)
        
        return bibtex_entries


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Convert DOIs to BibTeX format using CrossRef API',
        epilog='Example: python doi_to_bibtex.py 10.1038/s41586-021-03819-2'
    )
    
    parser.add_argument(
        'dois',
        nargs='*',
        help='DOI(s) to convert (can provide multiple)'
    )
    
    parser.add_argument(
        '-i', '--input',
        help='Input file with DOIs (one per line)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file for BibTeX (default: stdout)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between requests in seconds (default: 0.5)'
    )
    
    parser.add_argument(
        '--format',
        choices=['bibtex', 'json'],
        default='bibtex',
        help='Output format (default: bibtex)'
    )
    
    args = parser.parse_args()
    
    # Collect DOIs from command line and/or file
    dois = []
    
    if args.dois:
        dois.extend(args.dois)
    
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                file_dois = [line.strip() for line in f if line.strip()]
                dois.extend(file_dois)
        except FileNotFoundError:
            print(f'Error: Input file not found: {args.input}', file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f'Error reading input file: {e}', file=sys.stderr)
            sys.exit(1)
    
    if not dois:
        parser.print_help()
        sys.exit(1)
    
    # Convert DOIs
    converter = DOIConverter()
    
    if len(dois) == 1:
        bibtex = converter.doi_to_bibtex(dois[0])
        if bibtex:
            bibtex_entries = [bibtex]
        else:
            sys.exit(1)
    else:
        bibtex_entries = converter.convert_multiple(dois, delay=args.delay)
    
    if not bibtex_entries:
        print('Error: No successful conversions', file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'bibtex':
        output = '\n\n'.join(bibtex_entries) + '\n'
    else:  # json
        output = json.dumps({
            'count': len(bibtex_entries),
            'entries': bibtex_entries
        }, indent=2)
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f'Successfully wrote {len(bibtex_entries)} entries to {args.output}', file=sys.stderr)
        except Exception as e:
            print(f'Error writing output file: {e}', file=sys.stderr)
            sys.exit(1)
    else:
        print(output)
    
    # Summary
    if len(dois) > 1:
        success_rate = len(bibtex_entries) / len(dois) * 100
        print(f'\nConverted {len(bibtex_entries)}/{len(dois)} DOIs ({success_rate:.1f}%)', file=sys.stderr)


if __name__ == '__main__':
    main()
```

### `scripts/extract_metadata.py`

```python
#!/usr/bin/env python3
"""
Metadata Extraction Tool
Extract citation metadata from DOI, PMID, arXiv ID, or URL using various APIs.
"""

import sys
import os
import requests
import argparse
import time
import re
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse, quote

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    citation_key,
    format_pages,
    protect_title,
    render_entry,
)

class MetadataExtractor:
    """Extract metadata from various sources and generate BibTeX."""
    
    def __init__(self, email: Optional[str] = None):
        """
        Initialize extractor.
        
        Args:
            email: Email for Entrez API (recommended for PubMed)
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MetadataExtractor/1.0 (Citation Management Tool)'
        })
        self.email = email or os.getenv('NCBI_EMAIL', '')
    
    def identify_type(self, identifier: str) -> Tuple[str, str]:
        """
        Identify the type of identifier.
        
        Args:
            identifier: DOI, PMID, arXiv ID, or URL
            
        Returns:
            Tuple of (type, cleaned_identifier)
        """
        identifier = identifier.strip()
        
        # Check if URL
        if identifier.startswith('http://') or identifier.startswith('https://'):
            return self._parse_url(identifier)
        
        # Check for DOI
        if identifier.startswith('10.'):
            return ('doi', identifier)
        
        # Check for arXiv ID
        if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', identifier):
            return ('arxiv', identifier)
        if identifier.startswith('arXiv:'):
            return ('arxiv', identifier.replace('arXiv:', ''))
        
        # Check for PMID (8-digit number typically)
        if identifier.isdigit() and len(identifier) >= 7:
            return ('pmid', identifier)
        
        # Check for PMCID
        if identifier.upper().startswith('PMC') and identifier[3:].isdigit():
            return ('pmcid', identifier.upper())
        
        return ('unknown', identifier)
    
    def _parse_url(self, url: str) -> Tuple[str, str]:
        """Parse URL to extract identifier type and value."""
        parsed = urlparse(url)
        
        # DOI URLs
        if 'doi.org' in parsed.netloc:
            doi = parsed.path.lstrip('/')
            return ('doi', doi)
        
        # PubMed URLs
        if 'pubmed.ncbi.nlm.nih.gov' in parsed.netloc or 'ncbi.nlm.nih.gov/pubmed' in url:
            pmid = re.search(r'/(\d+)', parsed.path)
            if pmid:
                return ('pmid', pmid.group(1))
        
        # arXiv URLs
        if 'arxiv.org' in parsed.netloc:
            arxiv_id = re.search(r'/abs/(\d{4}\.\d{4,5})', parsed.path)
            if arxiv_id:
                return ('arxiv', arxiv_id.group(1))
        
        # Nature, Science, Cell, etc. - try to extract DOI from URL
        doi_match = re.search(r'10\.\d{4,}/[^\s/]+', url)
        if doi_match:
            return ('doi', doi_match.group())
        
        return ('url', url)
    
    def extract_from_doi(self, doi: str) -> Optional[Dict]:
        """
        Extract metadata from DOI using CrossRef API.
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Metadata dictionary or None
        """
        # A DOI is publisher-controlled text and may legitimately contain
        # `#`, `?`, `<` or `>`, so it cannot be interpolated into a URL raw.
        url = f'https://api.crossref.org/works/{quote(doi, safe="")}'

        try:
            response = self.session.get(url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})

                container = message.get('container-title') or ['']
                isbns = message.get('ISBN') or []
                issns = message.get('ISSN') or []

                metadata = {
                    'type': 'doi',
                    'entry_type': self._crossref_type_to_bibtex(message.get('type')),
                    'doi': doi,
                    'title': (message.get('title') or [''])[0],
                    'authors': self._format_authors_crossref(message.get('author', [])),
                    'editors': self._format_authors_crossref(message.get('editor', [])),
                    'year': self._extract_year_crossref(message),
                    'journal': container[0] if container else '',
                    'volume': str(message.get('volume', '')) if message.get('volume') else '',
                    'issue': str(message.get('issue', '')) if message.get('issue') else '',
                    'pages': message.get('page', ''),
                    'publisher': message.get('publisher', ''),
                    'isbn': isbns[0] if isbns else '',
                    'issn': issns[0] if issns else '',
                    'url': f'https://doi.org/{doi}'
                }

                return metadata
            else:
                print(f'Error: CrossRef API returned status {response.status_code} for DOI: {doi}', file=sys.stderr)
                return None
                
        except Exception as e:
            print(f'Error extracting metadata from DOI {doi}: {e}', file=sys.stderr)
            return None
    
    def extract_from_pmid(self, pmid: str) -> Optional[Dict]:
        """
        Extract metadata from PMID using PubMed E-utilities.
        
        Args:
            pmid: PubMed ID
            
        Returns:
            Metadata dictionary or None
        """
        url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
        params = {
            'db': 'pubmed',
            'id': pmid,
            'retmode': 'xml',
            'rettype': 'abstract'
        }
        
        if self.email:
            params['email'] = self.email
        
        api_key = os.getenv('NCBI_API_KEY')
        if api_key:
            params['api_key'] = api_key
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                article = root.find('.//PubmedArticle')
                
                if article is None:
                    print(f'Error: No article found for PMID: {pmid}', file=sys.stderr)
                    return None
                
                # Extract metadata from XML
                medline_citation = article.find('.//MedlineCitation')
                article_elem = medline_citation.find('.//Article')
                journal = article_elem.find('.//Journal')
                
                # Get DOI if available
                doi = None
                article_ids = article.findall('.//ArticleId')
                for article_id in article_ids:
                    if article_id.get('IdType') == 'doi':
                        doi = article_id.text
                        break
                
                metadata = {
                    'type': 'pmid',
                    'entry_type': 'article',
                    'pmid': pmid,
                    'title': self._pubmed_title(article_elem.find('.//ArticleTitle')),
                    'authors': self._format_authors_pubmed(article_elem.findall('.//Author')),
                    'year': self._extract_year_pubmed(article_elem),
                    'journal': journal.findtext('.//Title', ''),
                    'volume': journal.findtext('.//JournalIssue/Volume', ''),
                    'issue': journal.findtext('.//JournalIssue/Issue', ''),
                    'pages': article_elem.findtext('.//Pagination/MedlinePgn', ''),
                    'doi': doi
                }
                
                return metadata
            else:
                print(f'Error: PubMed API returned status {response.status_code} for PMID: {pmid}', file=sys.stderr)
                return None
                
        except Exception as e:
            print(f'Error extracting metadata from PMID {pmid}: {e}', file=sys.stderr)
            return None
    
    @staticmethod
    def _pubmed_title(element) -> str:
        """Read a PubMed ArticleTitle as a citation title.

        `itertext`, not `findtext`, because titles carry inline markup such as
        <i> and <sup> and findtext returns only the leading run. PubMed also
        terminates titles with a full stop that is not part of the title; a
        trailing `?` or `!` is, so only the period is dropped.
        """
        if element is None:
            return ''
        text = ' '.join(''.join(element.itertext()).split())
        return text[:-1] if text.endswith('.') else text

    def extract_from_arxiv(self, arxiv_id: str) -> Optional[Dict]:
        """
        Extract metadata from arXiv ID using arXiv API.
        
        Args:
            arxiv_id: arXiv identifier
            
        Returns:
            Metadata dictionary or None
        """
        url = 'http://export.arxiv.org/api/query'
        params = {
            'id_list': arxiv_id,
            'max_results': 1
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                # Parse Atom XML
                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
                
                entry = root.find('atom:entry', ns)
                if entry is None:
                    print(f'Error: No entry found for arXiv ID: {arxiv_id}', file=sys.stderr)
                    return None
                
                # Extract DOI if published
                doi_elem = entry.find('arxiv:doi', ns)
                doi = doi_elem.text if doi_elem is not None else None
                
                # Extract journal reference if published
                journal_ref_elem = entry.find('arxiv:journal_ref', ns)
                journal_ref = journal_ref_elem.text if journal_ref_elem is not None else None
                
                # Get publication date
                published = entry.findtext('atom:published', '', ns)
                year = published[:4] if published else ''
                
                # Get authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.findtext('atom:name', '', ns)
                    if name:
                        authors.append(name)
                
                # Only call it an @article when there is a journal to name.
                # A DOI alone is not enough -- arXiv mints DataCite DOIs for
                # unpublished preprints -- and an @article without a `journal`
                # fails the required-field check in validate_citations.py.
                journal = self._journal_from_arxiv_ref(journal_ref)

                metadata = {
                    'type': 'arxiv',
                    'entry_type': 'article' if journal else 'misc',
                    'arxiv_id': arxiv_id,
                    'title': entry.findtext('atom:title', '', ns).strip().replace('\n', ' '),
                    'authors': ' and '.join(authors),
                    'year': year,
                    'doi': doi,
                    'journal': journal,
                    'journal_ref': journal_ref,
                    'abstract': entry.findtext('atom:summary', '', ns).strip().replace('\n', ' '),
                    'url': f'https://arxiv.org/abs/{arxiv_id}'
                }

                return metadata
            else:
                print(f'Error: arXiv API returned status {response.status_code} for ID: {arxiv_id}', file=sys.stderr)
                return None
                
        except Exception as e:
            print(f'Error extracting metadata from arXiv {arxiv_id}: {e}', file=sys.stderr)
            return None
    
    def metadata_to_bibtex(self, metadata: Dict, citation_key: Optional[str] = None) -> str:
        """
        Convert metadata dictionary to BibTeX format.
        
        Args:
            metadata: Metadata dictionary
            citation_key: Optional custom citation key
            
        Returns:
            BibTeX string
        """
        if not citation_key:
            citation_key = self._generate_citation_key(metadata)

        entry_type = metadata.get('entry_type', 'misc')

        fields = {
            'author': metadata.get('authors', ''),
            'editor': metadata.get('editors', ''),
            'title': protect_title(metadata.get('title', '')),
            'year': metadata.get('year', ''),
            'volume': metadata.get('volume', ''),
            'number': metadata.get('issue', ''),
            'pages': format_pages(metadata.get('pages')),
            'doi': metadata.get('doi') or '',
            'isbn': metadata.get('isbn', ''),
            'issn': metadata.get('issn', ''),
        }

        # The venue field's name depends on the entry type, and a book or
        # report needs its publisher/institution or it fails validation.
        if entry_type in ('inproceedings', 'incollection'):
            fields['booktitle'] = metadata.get('journal', '')
        elif entry_type != 'misc':
            fields['journal'] = metadata.get('journal', '')

        if entry_type in ('book', 'incollection', 'inproceedings'):
            fields['publisher'] = metadata.get('publisher', '')
        elif entry_type == 'techreport':
            fields['institution'] = metadata.get('publisher', '')

        if entry_type == 'misc' and metadata.get('type') == 'arxiv':
            arxiv_id = metadata.get('arxiv_id', '')
            fields['howpublished'] = f'arXiv:{arxiv_id}' if arxiv_id else 'arXiv'

        # A DOI is the stable locator; only fall back to a URL without one.
        if not fields['doi'] and metadata.get('url'):
            fields['url'] = metadata['url']

        # BibTeX takes one `note` per entry, so build it from all the parts
        # that would otherwise each claim the field.
        notes = []
        if metadata.get('pmid'):
            notes.append(f'PMID: {metadata["pmid"]}')
        if metadata.get('type') == 'arxiv' and entry_type == 'misc':
            notes.append('Preprint')
        if notes:
            fields['note'] = '. '.join(notes)

        return render_entry(entry_type, citation_key, fields)

    @staticmethod
    def _journal_from_arxiv_ref(journal_ref: Optional[str]) -> str:
        """Pull a journal name out of arXiv's free-text `journal_ref`.

        The field has no schema -- `Nature 596, 583-589 (2021)` is typical --
        so take the leading run of non-numeric text and leave the rest for the
        enrichment pass rather than guessing at volume and pages.
        """
        if not journal_ref:
            return ''
        head = re.split(r'[,;]|\s\d', journal_ref.strip(), maxsplit=1)[0]
        return head.strip(' .')
    
    def _crossref_type_to_bibtex(self, crossref_type: str) -> str:
        """Map CrossRef type to BibTeX entry type."""
        type_map = {
            'journal-article': 'article',
            'book': 'book',
            'book-chapter': 'incollection',
            'proceedings-article': 'inproceedings',
            'posted-content': 'misc',
            'dataset': 'misc',
            'report': 'techreport'
        }
        return type_map.get(crossref_type, 'misc')
    
    def _format_authors_crossref(self, authors: List[Dict]) -> str:
        """Format author list from CrossRef data."""
        if not authors:
            return ''
        
        formatted = []
        for author in authors:
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                if given:
                    formatted.append(f'{family}, {given}')
                else:
                    formatted.append(family)
        
        return ' and '.join(formatted)
    
    def _format_authors_pubmed(self, authors: List) -> str:
        """Format author list from PubMed XML."""
        formatted = []
        for author in authors:
            last_name = author.findtext('.//LastName', '')
            fore_name = author.findtext('.//ForeName', '')
            if last_name:
                if fore_name:
                    formatted.append(f'{last_name}, {fore_name}')
                else:
                    formatted.append(last_name)
        
        return ' and '.join(formatted)
    
    def _extract_year_crossref(self, message: Dict) -> str:
        """Extract year from CrossRef message."""
        # Try published-print first, then published-online
        date_parts = message.get('published-print', {}).get('date-parts', [[]])
        if not date_parts or not date_parts[0]:
            date_parts = message.get('published-online', {}).get('date-parts', [[]])
        
        if date_parts and date_parts[0]:
            return str(date_parts[0][0])
        return ''
    
    def _extract_year_pubmed(self, article: ET.Element) -> str:
        """Extract year from PubMed XML."""
        year = article.findtext('.//Journal/JournalIssue/PubDate/Year', '')
        if not year:
            medline_date = article.findtext('.//Journal/JournalIssue/PubDate/MedlineDate', '')
            if medline_date:
                year_match = re.search(r'\d{4}', medline_date)
                if year_match:
                    year = year_match.group()
        return year
    
    def _generate_citation_key(self, metadata: Dict) -> str:
        """Generate a citation key from metadata.

        Shared with every other producer in this skill so that entries from
        different sources collide when -- and only when -- they are the same
        paper. Values arrive verbatim from a publisher-controlled record, and
        the key reaches both LaTeX and, in some workflows, a file path, so the
        shared helper restricts it to ASCII letters and digits.
        """
        return citation_key(
            metadata.get('authors', ''),
            metadata.get('year', ''),
            metadata.get('title', ''),
        )

    def _protect_title(self, title: str) -> str:
        """Protect capitalization in title for BibTeX."""
        return protect_title(title)

    def extract_from_pmcid(self, pmcid: str) -> Optional[Dict]:
        """Resolve a PMCID to a PMID via the NCBI ID converter, then extract."""
        url = 'https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/'
        params = {'ids': pmcid, 'format': 'json', 'tool': 'citation-management'}
        if self.email:
            params['email'] = self.email

        try:
            response = self.session.get(url, params=params, timeout=15)
            if response.status_code != 200:
                print(f'Error: ID converter returned status {response.status_code} for {pmcid}', file=sys.stderr)
                return None

            records = response.json().get('records', [])
            if not records or 'pmid' not in records[0]:
                if records and records[0].get('doi'):
                    return self.extract_from_doi(records[0]['doi'])
                print(f'Error: Could not resolve {pmcid} to a PMID or DOI', file=sys.stderr)
                return None

            return self.extract_from_pmid(records[0]['pmid'])

        except (requests.exceptions.RequestException, ValueError) as e:
            print(f'Error resolving PMCID {pmcid}: {e}', file=sys.stderr)
            return None

    def extract_from_url(self, url: str) -> Optional[Dict]:
        """Extract via a DOI advertised in the page's citation metadata.

        Publishers embed `citation_doi` / `DC.Identifier` meta tags on article
        pages. Reading the DOI and handing off to Crossref is far more reliable
        than scraping the page itself, and it fails honestly when absent.
        """
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                print(f'Error: URL returned status {response.status_code}: {url}', file=sys.stderr)
                return None

            head = response.text[:200000]
            patterns = [
                r'<meta[^>]+name=["\'](?:citation_doi|DC\.Identifier|dc\.identifier)["\'][^>]+content=["\']([^"\']+)["\']',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\'](?:citation_doi|DC\.Identifier|dc\.identifier)["\']',
            ]
            for pattern in patterns:
                match = re.search(pattern, head, re.IGNORECASE)
                if match:
                    doi = match.group(1).strip()
                    doi = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:)', '', doi, flags=re.IGNORECASE)
                    if doi.startswith('10.'):
                        print(f'Found DOI in page metadata: {doi}', file=sys.stderr)
                        return self.extract_from_doi(doi)

            print(f'Error: No DOI found in page metadata for {url}', file=sys.stderr)
            return None

        except requests.exceptions.RequestException as e:
            print(f'Error fetching {url}: {e}', file=sys.stderr)
            return None


    def extract(self, identifier: str) -> Optional[str]:
        """
        Extract metadata and return BibTeX.
        
        Args:
            identifier: DOI, PMID, arXiv ID, or URL
            
        Returns:
            BibTeX string or None
        """
        id_type, clean_id = self.identify_type(identifier)
        
        print(f'Identified as {id_type}: {clean_id}', file=sys.stderr)
        
        metadata = None
        
        if id_type == 'doi':
            metadata = self.extract_from_doi(clean_id)
        elif id_type == 'pmid':
            metadata = self.extract_from_pmid(clean_id)
        elif id_type == 'arxiv':
            metadata = self.extract_from_arxiv(clean_id)
        elif id_type == 'pmcid':
            metadata = self.extract_from_pmcid(clean_id)
        elif id_type == 'url':
            metadata = self.extract_from_url(clean_id)
        else:
            print(f'Error: Unknown identifier type: {identifier}', file=sys.stderr)
            return None
        
        if metadata:
            return self.metadata_to_bibtex(metadata)
        else:
            return None

    def extract_record(self, identifier: str) -> Optional[Dict]:
        """Extract metadata and return it with its rendered BibTeX attached."""
        id_type, clean_id = self.identify_type(identifier)

        print(f'Identified as {id_type}: {clean_id}', file=sys.stderr)

        handlers = {
            'doi': self.extract_from_doi,
            'pmid': self.extract_from_pmid,
            'arxiv': self.extract_from_arxiv,
            'pmcid': self.extract_from_pmcid,
            'url': self.extract_from_url,
        }

        handler = handlers.get(id_type)
        if handler is None:
            print(f'Error: Unknown identifier type: {identifier}', file=sys.stderr)
            return None

        metadata = handler(clean_id)
        if not metadata:
            return None

        record = dict(metadata)
        record['citation_key'] = self._generate_citation_key(metadata)
        record['bibtex'] = self.metadata_to_bibtex(metadata, record['citation_key'])
        return record


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Extract citation metadata from DOI, PMID, arXiv ID, or URL',
        epilog='Example: python extract_metadata.py --doi 10.1038/s41586-021-03819-2'
    )
    
    parser.add_argument('--doi', help='Digital Object Identifier')
    parser.add_argument('--pmid', help='PubMed ID')
    parser.add_argument('--arxiv', help='arXiv ID')
    parser.add_argument('--url', help='URL to article')
    parser.add_argument('-i', '--input', help='Input file with identifiers (one per line)')
    parser.add_argument('-o', '--output', help='Output file for BibTeX (default: stdout)')
    parser.add_argument('--format', choices=['bibtex', 'json'], default='bibtex', help='Output format')
    parser.add_argument('--email', help='Email for NCBI E-utilities (recommended)')
    
    args = parser.parse_args()
    
    # Collect identifiers
    identifiers = []
    if args.doi:
        identifiers.append(args.doi)
    if args.pmid:
        identifiers.append(args.pmid)
    if args.arxiv:
        identifiers.append(args.arxiv)
    if args.url:
        identifiers.append(args.url)
    
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                file_ids = [line.strip() for line in f if line.strip()]
                identifiers.extend(file_ids)
        except Exception as e:
            print(f'Error reading input file: {e}', file=sys.stderr)
            sys.exit(1)
    
    if not identifiers:
        parser.print_help()
        sys.exit(1)
    
    # Extract metadata
    extractor = MetadataExtractor(email=args.email)
    records = []

    for i, identifier in enumerate(identifiers):
        print(f'\nProcessing {i+1}/{len(identifiers)}...', file=sys.stderr)
        record = extractor.extract_record(identifier)
        if record:
            records.append(record)

        # Rate limiting
        if i < len(identifiers) - 1:
            time.sleep(0.5)

    if not records:
        print('Error: No successful extractions', file=sys.stderr)
        sys.exit(1)

    bibtex_entries = [record['bibtex'] for record in records]

    # Format output
    if args.format == 'bibtex':
        output = '\n\n'.join(bibtex_entries) + '\n'
    else:  # json
        output = json.dumps({
            'count': len(records),
            'entries': records
        }, indent=2)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nSuccessfully wrote {len(records)} entries to {args.output}", file=sys.stderr)
    else:
        print(output)
    
    print(f'\nExtracted {len(bibtex_entries)}/{len(identifiers)} entries', file=sys.stderr)


if __name__ == '__main__':
    main()
```

### `scripts/format_bibtex.py`

```python
#!/usr/bin/env python3
"""
BibTeX Formatter and Cleaner
Format, clean, sort, and deduplicate BibTeX files.

Writing is opt-in: pass --output to write elsewhere, or --in-place to
overwrite the input. Neither flag prints the result to stdout and leaves the
input untouched.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict
from typing import Dict, List, Optional

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    FIELD_ORDER,
    citation_key,
    format_pages,
    parse_bibtex_file,
    render_entry,
)


class BibTeXFormatter:
    """Format and clean BibTeX entries."""

    def __init__(self):
        # Standard field order for readability
        self.field_order = list(FIELD_ORDER)

    def parse_bibtex_file(self, filepath: str) -> List[Dict]:
        """
        Parse BibTeX file and extract entries.

        Args:
            filepath: Path to BibTeX file

        Returns:
            List of entry dictionaries
        """
        return parse_bibtex_file(filepath)

    def format_entry(self, entry: Dict) -> str:
        """
        Format a single BibTeX entry.

        Args:
            entry: Entry dictionary

        Returns:
            Formatted BibTeX string
        """
        return render_entry(entry['type'], entry['key'], entry['fields'])

    def fix_common_issues(self, entry: Dict) -> Dict:
        """
        Fix common formatting issues in entry.

        Args:
            entry: Entry dictionary

        Returns:
            Fixed entry dictionary
        """
        fixed = dict(entry)
        fields = OrderedDict(entry['fields'])

        # Normalise page ranges: strip `pp.`, use an en-dash range, and expand
        # abbreviated end pages. Idempotent, unlike a blanket hyphen replace.
        if 'pages' in fields:
            fields['pages'] = format_pages(fields['pages'])

        # Fix DOI (remove URL prefix if present)
        if 'doi' in fields:
            doi = fields['doi']
            doi = doi.replace('https://doi.org/', '')
            doi = doi.replace('http://doi.org/', '')
            doi = doi.replace('https://dx.doi.org/', '')
            doi = doi.replace('http://dx.doi.org/', '')
            doi = doi.replace('doi:', '')
            fields['doi'] = doi.strip()

        # Fix author separators (semicolon or ampersand to 'and')
        if 'author' in fields:
            author = fields['author']
            author = author.replace(';', ' and')
            author = author.replace(' & ', ' and ')
            # Clean up multiple 'and's
            author = re.sub(r'\s+and\s+and\s+', ' and ', author)
            author = re.sub(r'\s+', ' ', author).strip()
            fields['author'] = author

        fixed['fields'] = fields
        return fixed

    def deduplicate_entries(self, entries: List[Dict]) -> List[Dict]:
        """
        Remove duplicate entries based on DOI or citation key.

        Args:
            entries: List of entry dictionaries

        Returns:
            List of unique entries
        """
        seen_dois = set()
        seen_keys = set()
        unique_entries = []

        for entry in entries:
            doi = entry['fields'].get('doi', '').strip().lower()
            key = entry['key']

            # Check DOI first (more reliable)
            if doi:
                if doi in seen_dois:
                    print(f'Duplicate DOI found: {doi} (skipping {key})', file=sys.stderr)
                    continue
                seen_dois.add(doi)

            # Check citation key
            if key in seen_keys:
                print(f'Duplicate citation key found: {key} (skipping)', file=sys.stderr)
                continue
            seen_keys.add(key)

            unique_entries.append(entry)

        return unique_entries

    def rekey_entries(self, entries: List[Dict]) -> List[Dict]:
        """Rewrite citation keys to this skill's shared scheme.

        Entries pulled from different sources arrive with different key
        conventions, which hides duplicates. Collisions between genuinely
        distinct papers get a letter suffix.
        """
        rekeyed = []
        used = {}

        for entry in entries:
            fields = entry['fields']
            base = citation_key(
                fields.get('author', ''),
                fields.get('year', ''),
                fields.get('title', ''),
            )
            if base in used:
                used[base] += 1
                # 'a' is the original, so the second occurrence becomes 'b'.
                new_key = f'{base}{chr(ord("a") + used[base])}'
            else:
                used[base] = 0
                new_key = base

            updated = dict(entry)
            updated['key'] = new_key
            rekeyed.append(updated)

        return rekeyed

    def sort_entries(self, entries: List[Dict], sort_by: str = 'key', descending: bool = False) -> List[Dict]:
        """
        Sort entries by specified field.

        Args:
            entries: List of entry dictionaries
            sort_by: Field to sort by ('key', 'year', 'author', 'title')
            descending: Sort in descending order

        Returns:
            Sorted list of entries
        """
        def get_sort_key(entry: Dict) -> str:
            if sort_by == 'year':
                # Zero-pad so string comparison orders numerically, and push
                # undated entries to the end.
                year = entry['fields'].get('year', '')
                digits = re.sub(r'[^0-9]', '', year)
                return digits.zfill(4) if digits else '9999'
            if sort_by == 'author':
                author = entry['fields'].get('author', '')
                if not author:
                    return 'zzz'
                first = author.split(' and ')[0]
                if ',' in first:
                    return first.split(',')[0].strip().lower()
                words = first.split()
                return words[-1].lower() if words else 'zzz'
            if sort_by == 'title':
                return entry['fields'].get('title', '').lower()
            return entry['key'].lower()

        return sorted(entries, key=get_sort_key, reverse=descending)

    def format_file(self, filepath: str, output: Optional[str] = None,
                    deduplicate: bool = False, sort_by: Optional[str] = None,
                    descending: bool = False, fix_issues: bool = True,
                    rekey: bool = False) -> Optional[str]:
        """
        Format entire BibTeX file.

        Args:
            filepath: Input BibTeX file
            output: Output file, or None to return the formatted text
            deduplicate: Remove duplicates
            sort_by: Field to sort by
            descending: Sort in descending order
            fix_issues: Fix common formatting issues
            rekey: Rewrite citation keys to the shared scheme

        Returns:
            The formatted BibTeX text, or None when nothing was parsed.
        """
        print(f'Parsing {filepath}...', file=sys.stderr)
        entries = self.parse_bibtex_file(filepath)

        if not entries:
            print('No entries found', file=sys.stderr)
            return None

        print(f'Found {len(entries)} entries', file=sys.stderr)

        # Fix common issues
        if fix_issues:
            print('Fixing common issues...', file=sys.stderr)
            entries = [self.fix_common_issues(e) for e in entries]

        # Rekey before deduplicating, so cross-source duplicates collapse.
        if rekey:
            print('Rewriting citation keys...', file=sys.stderr)
            entries = self.rekey_entries(entries)

        # Deduplicate
        if deduplicate:
            print('Removing duplicates...', file=sys.stderr)
            original_count = len(entries)
            entries = self.deduplicate_entries(entries)
            removed = original_count - len(entries)
            if removed > 0:
                print(f'Removed {removed} duplicate(s)', file=sys.stderr)

        # Sort
        if sort_by:
            print(f'Sorting by {sort_by}...', file=sys.stderr)
            entries = self.sort_entries(entries, sort_by, descending)

        # Format entries
        print('Formatting entries...', file=sys.stderr)
        formatted_entries = [self.format_entry(e) for e in entries]
        output_content = '\n\n'.join(formatted_entries) + '\n'

        if output is None:
            return output_content

        try:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f'Successfully wrote {len(entries)} entries to {output}', file=sys.stderr)
        except OSError as e:
            print(f'Error writing file: {e}', file=sys.stderr)
            sys.exit(1)

        return output_content


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Format, clean, sort, and deduplicate BibTeX files',
        epilog='Example: python format_bibtex.py references.bib -o clean.bib --deduplicate --sort year'
    )

    parser.add_argument(
        'file',
        help='BibTeX file to format'
    )

    parser.add_argument(
        '-o', '--output',
        help='Write the result to this file'
    )

    parser.add_argument(
        '--in-place',
        action='store_true',
        help='Overwrite the input file (mutually exclusive with --output)'
    )

    parser.add_argument(
        '--deduplicate', '--remove-duplicates',
        dest='deduplicate',
        action='store_true',
        help='Remove duplicate entries'
    )

    parser.add_argument(
        '--rekey',
        action='store_true',
        help="Rewrite citation keys to this skill's shared scheme before deduplicating"
    )

    parser.add_argument(
        '--sort',
        choices=['key', 'year', 'author', 'title'],
        help='Sort entries by field'
    )

    parser.add_argument(
        '--descending',
        action='store_true',
        help='Sort in descending order'
    )

    parser.add_argument(
        '--no-fix',
        action='store_true',
        help='Do not fix common issues'
    )

    args = parser.parse_args()

    if args.output and args.in_place:
        parser.error('--output and --in-place are mutually exclusive')

    destination = args.file if args.in_place else args.output

    # Format file
    formatter = BibTeXFormatter()
    result = formatter.format_file(
        args.file,
        output=destination,
        deduplicate=args.deduplicate,
        sort_by=args.sort,
        descending=args.descending,
        fix_issues=not args.no_fix,
        rekey=args.rekey,
    )

    if result is None:
        sys.exit(1)

    # Without a destination the input is left alone and the result goes to
    # stdout, so a mistaken invocation cannot destroy a bibliography.
    if destination is None:
        print(result, end='')


if __name__ == '__main__':
    main()
```

### `scripts/search_google_scholar.py`

```python
#!/usr/bin/env python3
"""
Google Scholar Search Tool
Search Google Scholar and export results.

Note: This script requires the 'scholarly' library.
Install with: uv pip install scholarly
"""

import sys
import argparse
import json
import time
import random
from typing import List, Dict, Optional

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    citation_key,
    protect_title,
    render_entry,
)

try:
    from scholarly import scholarly, ProxyGenerator
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False
    print('Warning: scholarly library not installed. Install with: uv pip install scholarly', file=sys.stderr)

class GoogleScholarSearcher:
    """Search Google Scholar using scholarly library."""
    
    def __init__(self, use_proxy: bool = False):
        """
        Initialize searcher.
        
        Args:
            use_proxy: Use free proxy (helps avoid rate limiting)
        """
        if not SCHOLARLY_AVAILABLE:
            raise ImportError('scholarly library required. Install with: uv pip install scholarly')
        
        # Setup proxy if requested
        if use_proxy:
            try:
                pg = ProxyGenerator()
                pg.FreeProxies()
                scholarly.use_proxy(pg)
                print('Using free proxy', file=sys.stderr)
            except Exception as e:
                print(f'Warning: Could not setup proxy: {e}', file=sys.stderr)
    
    def search(self, query: str, max_results: int = 50,
               year_start: Optional[int] = None, year_end: Optional[int] = None,
               sort_by: str = 'relevance') -> List[Dict]:
        """
        Search Google Scholar.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            year_start: Start year filter
            year_end: End year filter
            sort_by: Sort order ('relevance' or 'citations')
            
        Returns:
            List of result dictionaries
        """
        if not SCHOLARLY_AVAILABLE:
            print('Error: scholarly library not installed', file=sys.stderr)
            return []
        
        print(f'Searching Google Scholar: {query}', file=sys.stderr)
        print(f'Max results: {max_results}', file=sys.stderr)
        
        results = []
        
        try:
            # Perform search
            search_query = scholarly.search_pubs(query)
            
            for i, result in enumerate(search_query):
                if i >= max_results:
                    break
                
                print(f'Retrieved {i+1}/{max_results}', file=sys.stderr)
                
                # Extract metadata
                metadata = {
                    'title': result.get('bib', {}).get('title', ''),
                    'authors': ', '.join(result.get('bib', {}).get('author', [])),
                    'year': result.get('bib', {}).get('pub_year', ''),
                    'venue': result.get('bib', {}).get('venue', ''),
                    'abstract': result.get('bib', {}).get('abstract', ''),
                    'citations': result.get('num_citations', 0),
                    'url': result.get('pub_url', ''),
                    'eprint_url': result.get('eprint_url', ''),
                }
                
                # Filter by year
                if year_start or year_end:
                    try:
                        pub_year = int(metadata['year']) if metadata['year'] else 0
                        if year_start and pub_year < year_start:
                            continue
                        if year_end and pub_year > year_end:
                            continue
                    except ValueError:
                        pass
                
                results.append(metadata)
                
                # Rate limiting to avoid blocking
                time.sleep(random.uniform(2, 5))
            
        except Exception as e:
            print(f'Error during search: {e}', file=sys.stderr)
        
        # Sort if requested
        if sort_by == 'citations' and results:
            results.sort(key=lambda x: x.get('citations', 0), reverse=True)
        
        return results
    
    def metadata_to_bibtex(self, metadata: Dict) -> str:
        """Convert metadata to BibTeX format.

        Scholar records carry no DOI and an unstructured venue string, so an
        entry built from one is a starting point: run it through the metadata
        enrichment pass before citing it.
        """
        # Scholar gives authors as a list; `search` joined it with ', '.
        authors = ' and '.join(
            part.strip() for part in metadata.get('authors', '').split(',') if part.strip()
        )

        key = citation_key(authors, metadata.get('year', ''), metadata.get('title', ''))

        # Determine entry type (guess based on venue)
        venue = metadata.get('venue', '').lower()
        if 'proceedings' in venue or 'conference' in venue or 'symposium' in venue:
            entry_type = 'inproceedings'
            venue_field = 'booktitle'
        else:
            entry_type = 'article'
            venue_field = 'journal'

        fields = {
            'author': authors,
            'title': protect_title(metadata.get('title', '')),
            venue_field: metadata.get('venue', ''),
            'year': metadata.get('year', ''),
            'url': metadata.get('url', ''),
        }

        # The citation count deliberately does not go in the `.bib`: it changes
        # every week, and baking it into a bibliography makes the file wrong
        # the moment it is written. It stays in the JSON output instead.

        return render_entry(entry_type, key, fields)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Search Google Scholar (requires scholarly library)',
        epilog='Example: python search_google_scholar.py "machine learning" --limit 50'
    )
    
    parser.add_argument(
        'query',
        help='Search query'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of results (default: 50)'
    )
    
    parser.add_argument(
        '--year-start',
        type=int,
        help='Start year for filtering'
    )
    
    parser.add_argument(
        '--year-end',
        type=int,
        help='End year for filtering'
    )
    
    parser.add_argument(
        '--sort-by',
        choices=['relevance', 'citations'],
        default='relevance',
        help='Sort order (default: relevance)'
    )
    
    parser.add_argument(
        '--use-proxy',
        action='store_true',
        help='Use free proxy to avoid rate limiting'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'bibtex'],
        default='json',
        help='Output format (default: json)'
    )
    
    args = parser.parse_args()
    
    if not SCHOLARLY_AVAILABLE:
        print('\nError: scholarly library not installed', file=sys.stderr)
        print('Install with: uv pip install scholarly', file=sys.stderr)
        print('\nAlternatively, use PubMed search for biomedical literature:', file=sys.stderr)
        print('  python search_pubmed.py "your query"', file=sys.stderr)
        sys.exit(1)
    
    # Search
    searcher = GoogleScholarSearcher(use_proxy=args.use_proxy)
    results = searcher.search(
        args.query,
        max_results=args.limit,
        year_start=args.year_start,
        year_end=args.year_end,
        sort_by=args.sort_by
    )
    
    if not results:
        print('No results found', file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'json':
        output = json.dumps({
            'query': args.query,
            'count': len(results),
            'results': results
        }, indent=2)
    else:  # bibtex
        bibtex_entries = [searcher.metadata_to_bibtex(r) for r in results]
        output = '\n\n'.join(bibtex_entries) + '\n'
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Wrote {len(results)} results to {args.output}', file=sys.stderr)
    else:
        print(output)
    
    print(f'\nRetrieved {len(results)} results', file=sys.stderr)


if __name__ == '__main__':
    main()
```

### `scripts/search_openalex.py`

```python
#!/usr/bin/env python3
"""
OpenAlex Search Tool
Search OpenAlex and export results as JSON or BibTeX.

OpenAlex indexes ~250 million scholarly works across every discipline, needs no
API key, and has a documented REST API rather than a scraped HTML surface. It
is the third leg of this skill's coverage: PubMed is authoritative for
biomedicine, Google Scholar is broad but fragile and rate-limited, and OpenAlex
is broad, stable, and machine-readable.

Setting OPENALEX_EMAIL (or passing --email) joins OpenAlex's "polite pool",
which is faster and more reliably available. The address is sent to
api.openalex.org only, as a query parameter, exactly as OpenAlex documents.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Dict, List, Optional

import requests

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    citation_key,
    format_pages,
    protect_title,
    render_entry,
)

API_URL = 'https://api.openalex.org/works'

# OpenAlex work types -> BibTeX entry types.
TYPE_MAP = {
    'article': 'article',
    'journal-article': 'article',
    'review': 'article',
    'book': 'book',
    'book-chapter': 'incollection',
    'monograph': 'book',
    'proceedings-article': 'inproceedings',
    'proceedings': 'inproceedings',
    'dissertation': 'phdthesis',
    'report': 'techreport',
    'preprint': 'misc',
    'posted-content': 'misc',
    'dataset': 'misc',
}


class OpenAlexSearcher:
    """Search OpenAlex via its public REST API."""

    def __init__(self, email: Optional[str] = None):
        self.email = email or os.getenv('OPENALEX_EMAIL', '')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OpenAlexSearcher/1.0 (Citation Management Tool)'
        })

    def search(self, query: str, max_results: int = 50,
               year_start: Optional[int] = None, year_end: Optional[int] = None,
               work_type: Optional[str] = None,
               sort_by: str = 'relevance') -> List[Dict]:
        """
        Search OpenAlex and return normalised metadata records.

        Args:
            query: Free-text search query
            max_results: Maximum number of works to return
            year_start: Earliest publication year, inclusive
            year_end: Latest publication year, inclusive
            work_type: OpenAlex work type filter (e.g. 'article', 'review')
            sort_by: 'relevance' or 'citations'

        Returns:
            List of metadata dictionaries
        """
        filters = []
        if year_start:
            filters.append(f'from_publication_date:{year_start}-01-01')
        if year_end:
            filters.append(f'to_publication_date:{year_end}-12-31')
        if work_type:
            filters.append(f'type:{work_type}')

        params = {
            'search': query,
            'per-page': str(min(200, max_results)),
            'cursor': '*',
        }
        if filters:
            params['filter'] = ','.join(filters)
        if sort_by == 'citations':
            params['sort'] = 'cited_by_count:desc'
        if self.email:
            params['mailto'] = self.email

        print(f'Searching OpenAlex: {query}', file=sys.stderr)

        results: List[Dict] = []
        reported_total = False

        while len(results) < max_results:
            try:
                response = self.session.get(API_URL, params=params, timeout=30)
                response.raise_for_status()
                payload = response.json()
            except requests.exceptions.RequestException as e:
                print(f'Error searching OpenAlex: {e}', file=sys.stderr)
                break
            except ValueError as e:
                print(f'Error: OpenAlex returned invalid JSON: {e}', file=sys.stderr)
                break

            if not reported_total:
                total = payload.get('meta', {}).get('count', 0)
                print(f'Found {total} results, retrieving up to {max_results}', file=sys.stderr)
                reported_total = True

            works = payload.get('results', [])
            if not works:
                break

            for work in works:
                results.append(self._normalise(work))
                if len(results) >= max_results:
                    break

            next_cursor = payload.get('meta', {}).get('next_cursor')
            if not next_cursor or len(results) >= max_results:
                break
            params['cursor'] = next_cursor

            # OpenAlex asks for courteous pacing even in the polite pool.
            time.sleep(0.1)

        print(f'Retrieved {len(results)} results', file=sys.stderr)
        return results

    def _normalise(self, work: Dict) -> Dict:
        """Flatten one OpenAlex work into this skill's metadata shape."""
        authors = [
            authorship.get('author', {}).get('display_name', '')
            for authorship in work.get('authorships', [])
        ]
        authors = [name for name in authors if name]

        location = work.get('primary_location') or {}
        source = location.get('source') or {}
        biblio = work.get('biblio') or {}

        first_page = biblio.get('first_page') or ''
        last_page = biblio.get('last_page') or ''
        if first_page and last_page and first_page != last_page:
            pages = f'{first_page}-{last_page}'
        else:
            pages = first_page or ''

        doi = work.get('doi') or ''
        if doi.startswith('https://doi.org/'):
            doi = doi[len('https://doi.org/'):]

        return {
            'openalex_id': work.get('id', ''),
            'doi': doi,
            'title': work.get('title') or work.get('display_name') or '',
            'authors': ' and '.join(authors),
            'journal': source.get('display_name', '') or '',
            'publisher': source.get('host_organization_name', '') or '',
            'year': str(work.get('publication_year') or ''),
            'volume': biblio.get('volume') or '',
            'issue': biblio.get('issue') or '',
            'pages': pages,
            'type': work.get('type') or '',
            'citations': work.get('cited_by_count', 0),
            'is_open_access': (work.get('open_access') or {}).get('is_oa', False),
            'abstract': self._abstract(work.get('abstract_inverted_index')),
        }

    @staticmethod
    def _abstract(inverted_index: Optional[Dict]) -> str:
        """Rebuild the abstract from OpenAlex's inverted index."""
        if not inverted_index:
            return ''
        positions = []
        for word, indices in inverted_index.items():
            for index in indices:
                positions.append((index, word))
        positions.sort()
        return ' '.join(word for _, word in positions)

    def metadata_to_bibtex(self, metadata: Dict) -> str:
        """Convert a normalised record to a BibTeX entry."""
        entry_type = TYPE_MAP.get(metadata.get('type', ''), 'misc')

        key = citation_key(
            metadata.get('authors', ''),
            metadata.get('year', ''),
            metadata.get('title', ''),
        )

        fields = {
            'author': metadata.get('authors', ''),
            'title': protect_title(metadata.get('title', '')),
            'year': metadata.get('year', ''),
            'volume': metadata.get('volume', ''),
            'number': metadata.get('issue', ''),
            'pages': format_pages(metadata.get('pages')),
            'doi': metadata.get('doi', ''),
        }

        venue = metadata.get('journal', '')
        if entry_type in ('inproceedings', 'incollection'):
            fields['booktitle'] = venue
        elif entry_type != 'misc':
            fields['journal'] = venue

        if entry_type in ('book', 'incollection', 'inproceedings'):
            fields['publisher'] = metadata.get('publisher', '')
        elif entry_type == 'techreport':
            fields['institution'] = metadata.get('publisher', '')

        if entry_type == 'misc':
            if venue:
                fields['howpublished'] = venue
            fields['note'] = 'Preprint'

        if not fields['doi'] and metadata.get('openalex_id'):
            fields['url'] = metadata['openalex_id']

        return render_entry(entry_type, key, fields)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Search OpenAlex (no API key required)',
        epilog='Example: python search_openalex.py "CRISPR gene editing" --limit 50 --format bibtex'
    )

    parser.add_argument('query', help='Search query')
    parser.add_argument('--limit', type=int, default=50,
                        help='Maximum number of results (default: 50)')
    parser.add_argument('--year-start', type=int, help='Earliest publication year')
    parser.add_argument('--year-end', type=int, help='Latest publication year')
    parser.add_argument('--type', dest='work_type',
                        help='OpenAlex work type filter (e.g. article, review, preprint)')
    parser.add_argument('--sort-by', choices=['relevance', 'citations'], default='relevance',
                        help='Sort order (default: relevance)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--format', choices=['json', 'bibtex'], default='json',
                        help='Output format (default: json)')
    parser.add_argument('--email',
                        help='Contact email for the OpenAlex polite pool (or set OPENALEX_EMAIL)')

    args = parser.parse_args()

    searcher = OpenAlexSearcher(email=args.email)
    results = searcher.search(
        args.query,
        max_results=args.limit,
        year_start=args.year_start,
        year_end=args.year_end,
        work_type=args.work_type,
        sort_by=args.sort_by,
    )

    if not results:
        print('No results found', file=sys.stderr)
        sys.exit(1)

    if args.format == 'json':
        output = json.dumps({
            'query': args.query,
            'count': len(results),
            'results': results,
        }, indent=2)
    else:
        output = '\n\n'.join(searcher.metadata_to_bibtex(r) for r in results) + '\n'

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Wrote {len(results)} results to {args.output}', file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
```

### `scripts/search_pubmed.py`

```python
#!/usr/bin/env python3
"""
PubMed Search Tool
Search PubMed using E-utilities API and export results.
"""

import sys
import os
import re
import requests
import argparse
import json
import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    citation_key,
    format_pages,
    protect_title,
    render_entry,
)

class PubMedSearcher:
    """Search PubMed using NCBI E-utilities API."""
    
    def __init__(self, api_key: Optional[str] = None, email: Optional[str] = None):
        """
        Initialize searcher.
        
        Args:
            api_key: NCBI API key (optional but recommended)
            email: Email for Entrez (optional but recommended)
        """
        self.api_key = api_key or os.getenv('NCBI_API_KEY', '')
        self.email = email or os.getenv('NCBI_EMAIL', '')
        self.base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        self.session = requests.Session()
        
        # Rate limiting
        self.delay = 0.11 if self.api_key else 0.34  # 10/sec with key, 3/sec without
    
    def search(self, query: str, max_results: int = 100,
               date_start: Optional[str] = None, date_end: Optional[str] = None,
               publication_types: Optional[List[str]] = None) -> List[str]:
        """
        Search PubMed and return PMIDs.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            date_start: Start date (YYYY/MM/DD or YYYY)
            date_end: End date (YYYY/MM/DD or YYYY)
            publication_types: List of publication types to filter
            
        Returns:
            List of PMIDs
        """
        # Build query with filters
        full_query = query
        
        # Add date range
        if date_start or date_end:
            start = date_start or '1900'
            end = date_end or datetime.now().strftime('%Y')
            full_query += f' AND {start}:{end}[Publication Date]'
        
        # Add publication types
        if publication_types:
            pub_type_query = ' OR '.join([f'"{pt}"[Publication Type]' for pt in publication_types])
            full_query += f' AND ({pub_type_query})'
        
        print(f'Searching PubMed: {full_query}', file=sys.stderr)

        # ESearch caps retmax at 10000; asking for more is silently truncated,
        # so say so rather than letting the caller believe they got everything.
        if max_results > 10000:
            print(
                f'Note: ESearch returns at most 10000 records per request; '
                f'requesting 10000 rather than {max_results}. Narrow the query '
                f'or split it by date range for a larger set.',
                file=sys.stderr,
            )
            max_results = 10000

        # ESearch to get PMIDs
        esearch_url = self.base_url + 'esearch.fcgi'
        params = {
            'db': 'pubmed',
            'term': full_query,
            'retmax': max_results,
            'retmode': 'json'
        }
        
        if self.email:
            params['email'] = self.email
        if self.api_key:
            params['api_key'] = self.api_key
        
        try:
            response = self.session.get(esearch_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pmids = data['esearchresult']['idlist']
            count = int(data['esearchresult']['count'])
            
            print(f'Found {count} results, retrieving {len(pmids)}', file=sys.stderr)
            
            return pmids
            
        except Exception as e:
            print(f'Error searching PubMed: {e}', file=sys.stderr)
            return []
    
    def fetch_metadata(self, pmids: List[str]) -> List[Dict]:
        """
        Fetch metadata for PMIDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of metadata dictionaries
        """
        if not pmids:
            return []
        
        metadata_list = []
        
        # Fetch in batches of 200
        batch_size = 200
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            print(f'Fetching metadata for PMIDs {i+1}-{min(i+batch_size, len(pmids))}...', file=sys.stderr)
            
            efetch_url = self.base_url + 'efetch.fcgi'
            params = {
                'db': 'pubmed',
                'id': ','.join(batch),
                'retmode': 'xml',
                'rettype': 'abstract'
            }
            
            if self.email:
                params['email'] = self.email
            if self.api_key:
                params['api_key'] = self.api_key
            
            try:
                response = self.session.get(efetch_url, params=params, timeout=60)
                response.raise_for_status()
                
                # Parse XML
                root = ET.fromstring(response.content)
                articles = root.findall('.//PubmedArticle')
                
                for article in articles:
                    metadata = self._extract_metadata_from_xml(article)
                    if metadata:
                        metadata_list.append(metadata)
                
                # Rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                print(f'Error fetching metadata for batch: {e}', file=sys.stderr)
                continue
        
        return metadata_list
    
    @staticmethod
    def _element_text(element: Optional[ET.Element]) -> str:
        """Flatten an element's text, including any inline markup children.

        PubMed terminates titles with a full stop that is not part of the
        title; a trailing `?` or `!` is, so only the period is dropped.
        """
        if element is None:
            return ''
        text = ' '.join(''.join(element.itertext()).split())
        return text[:-1] if text.endswith('.') else text

    def _extract_metadata_from_xml(self, article: ET.Element) -> Optional[Dict]:
        """Extract metadata from PubmedArticle XML element."""
        try:
            medline_citation = article.find('.//MedlineCitation')
            article_elem = medline_citation.find('.//Article')
            journal = article_elem.find('.//Journal')
            
            # Get PMID
            pmid = medline_citation.findtext('.//PMID', '')
            
            # Get DOI
            doi = None
            article_ids = article.findall('.//ArticleId')
            for article_id in article_ids:
                if article_id.get('IdType') == 'doi':
                    doi = article_id.text
                    break
            
            # Get authors
            authors = []
            author_list = article_elem.find('.//AuthorList')
            if author_list is not None:
                for author in author_list.findall('.//Author'):
                    last_name = author.findtext('.//LastName', '')
                    fore_name = author.findtext('.//ForeName', '')
                    if last_name:
                        if fore_name:
                            authors.append(f'{last_name}, {fore_name}')
                        else:
                            authors.append(last_name)
            
            # Get year
            year = article_elem.findtext('.//Journal/JournalIssue/PubDate/Year', '')
            if not year:
                medline_date = article_elem.findtext('.//Journal/JournalIssue/PubDate/MedlineDate', '')
                if medline_date:
                    year_match = re.search(r'\d{4}', medline_date)
                    if year_match:
                        year = year_match.group()

            # Structured abstracts split into several labelled AbstractText
            # elements; taking only the first drops most of the abstract.
            sections = []
            for chunk in article_elem.findall('.//Abstract/AbstractText'):
                text = ''.join(chunk.itertext()).strip()
                if not text:
                    continue
                label = chunk.get('Label')
                sections.append(f'{label}: {text}' if label else text)
            abstract = ' '.join(sections)


            metadata = {
                'pmid': pmid,
                'doi': doi,
                # itertext, not findtext: titles carry inline markup such as
                # <i> and <sup>, and findtext returns only the leading run.
                'title': self._element_text(article_elem.find('.//ArticleTitle')),
                'authors': ' and '.join(authors),
                'journal': journal.findtext('.//Title', ''),
                'year': year,
                'volume': journal.findtext('.//JournalIssue/Volume', ''),
                'issue': journal.findtext('.//JournalIssue/Issue', ''),
                'pages': article_elem.findtext('.//Pagination/MedlinePgn', ''),
                'abstract': abstract
            }
            
            return metadata
            
        except Exception as e:
            print(f'Error extracting metadata: {e}', file=sys.stderr)
            return None
    
    def metadata_to_bibtex(self, metadata: Dict) -> str:
        """Convert metadata to BibTeX format.

        Uses the shared key scheme rather than appending the PMID, so an entry
        found here and the same paper found via Crossref or OpenAlex collide
        and can be deduplicated.
        """
        key = citation_key(
            metadata.get('authors', ''),
            metadata.get('year', ''),
            metadata.get('title', ''),
        )

        fields = {
            'author': metadata.get('authors', ''),
            'title': protect_title(metadata.get('title', '')),
            'journal': metadata.get('journal', ''),
            'year': metadata.get('year', ''),
            'volume': metadata.get('volume', ''),
            'number': metadata.get('issue', ''),
            'pages': format_pages(metadata.get('pages')),
            'doi': metadata.get('doi') or '',
        }

        if metadata.get('pmid'):
            fields['note'] = f'PMID: {metadata["pmid"]}'

        return render_entry('article', key, fields)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Search PubMed using E-utilities API',
        epilog='Example: python search_pubmed.py "CRISPR gene editing" --limit 100'
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Search query (PubMed syntax)'
    )
    
    parser.add_argument(
        '--query',
        dest='query_arg',
        help='Search query (alternative to positional argument)'
    )
    
    parser.add_argument(
        '--query-file',
        help='File containing search query'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum number of results (default: 100)'
    )
    
    parser.add_argument(
        '--date-start',
        help='Start date (YYYY/MM/DD or YYYY)'
    )
    
    parser.add_argument(
        '--date-end',
        help='End date (YYYY/MM/DD or YYYY)'
    )
    
    parser.add_argument(
        '--publication-types',
        help='Comma-separated publication types (e.g., "Review,Clinical Trial")'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'bibtex'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--api-key',
        help='NCBI API key (or set NCBI_API_KEY env var)'
    )
    
    parser.add_argument(
        '--email',
        help='Email for Entrez (or set NCBI_EMAIL env var)'
    )
    
    args = parser.parse_args()
    
    # Get query
    query = args.query or args.query_arg
    
    if args.query_file:
        try:
            with open(args.query_file, 'r', encoding='utf-8') as f:
                query = f.read().strip()
        except Exception as e:
            print(f'Error reading query file: {e}', file=sys.stderr)
            sys.exit(1)
    
    if not query:
        parser.print_help()
        sys.exit(1)
    
    # Parse publication types
    pub_types = None
    if args.publication_types:
        pub_types = [pt.strip() for pt in args.publication_types.split(',')]
    
    # Search PubMed
    searcher = PubMedSearcher(api_key=args.api_key, email=args.email)
    pmids = searcher.search(
        query,
        max_results=args.limit,
        date_start=args.date_start,
        date_end=args.date_end,
        publication_types=pub_types
    )
    
    if not pmids:
        print('No results found', file=sys.stderr)
        sys.exit(1)
    
    # Fetch metadata
    metadata_list = searcher.fetch_metadata(pmids)
    
    # Format output
    if args.format == 'json':
        output = json.dumps({
            'query': query,
            'count': len(metadata_list),
            'results': metadata_list
        }, indent=2)
    else:  # bibtex
        bibtex_entries = [searcher.metadata_to_bibtex(m) for m in metadata_list]
        output = '\n\n'.join(bibtex_entries) + '\n'
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Wrote {len(metadata_list)} results to {args.output}', file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
```

### `scripts/validate_citations.py`

```python
#!/usr/bin/env python3
"""
Citation Validation Tool
Validate BibTeX files for accuracy, completeness, and format compliance.
"""

import sys
import re
import requests
import argparse
import json
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from urllib.parse import quote

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))

from _common import parse_bibtex_file as _parse_bibtex_file  # noqa: E402

# Typical reference-list lengths, as (minimum, typical maximum, display name).
#
# These are editorial rules of thumb drawn from what published papers at these
# venues tend to carry -- not sourced submission requirements, most of which do
# not cap references at all. They drive warnings only; a bibliography is never
# wrong merely for being short.
VENUE_STANDARDS = {
    'nature': (35, 50, 'Nature'),
    'science': (35, 50, 'Science'),
    'cell': (35, 50, 'Cell'),
    'multidisciplinary': (35, 50, 'High-impact Multidisciplinary Journal'),
    'neurips': (30, 45, 'NeurIPS'),
    'icml': (30, 45, 'ICML'),
    'iclr': (30, 45, 'ICLR'),
    'cvpr': (30, 45, 'CVPR'),
    'acl': (30, 45, 'ACL'),
    'ml_cs_conf': (30, 45, 'ML/CS Conference'),
    'review': (40, 65, 'Comprehensive Literature Review'),
    'market_research': (40, 65, 'Market Research Report'),
    'literature_review': (40, 65, 'Literature Review / Market Research'),
    'nejm': (30, 45, 'NEJM'),
    'lancet': (30, 45, 'The Lancet'),
    'jama': (30, 45, 'JAMA'),
    'medical': (30, 45, 'Medical Journal'),
}


class CitationValidator:
    """Validate BibTeX entries for errors and inconsistencies."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CitationValidator/1.0 (Citation Management Tool)'
        })
        self.venue_standards = VENUE_STANDARDS

        # Required fields by entry type
        self.required_fields = {
            'article': ['author', 'title', 'journal', 'year'],
            'book': ['title', 'publisher', 'year'],  # author OR editor
            'inproceedings': ['author', 'title', 'booktitle', 'year'],
            'incollection': ['author', 'title', 'booktitle', 'publisher', 'year'],
            'phdthesis': ['author', 'title', 'school', 'year'],
            'mastersthesis': ['author', 'title', 'school', 'year'],
            'techreport': ['author', 'title', 'institution', 'year'],
            'misc': ['title', 'year']
        }
        
        # Recommended fields
        self.recommended_fields = {
            'article': ['volume', 'pages', 'doi'],
            'book': ['isbn'],
            'inproceedings': ['pages'],
        }
    
    def parse_bibtex_file(self, filepath: str) -> List[Dict]:
        """
        Parse BibTeX file and extract entries.
        
        Args:
            filepath: Path to BibTeX file
            
        Returns:
            List of entry dictionaries
        """
        return _parse_bibtex_file(filepath)
    
    def validate_entry(self, entry: Dict) -> Tuple[List[Dict], List[Dict]]:
        """
        Validate a single BibTeX entry.
        
        Args:
            entry: Entry dictionary
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        entry_type = entry['type']
        key = entry['key']
        fields = entry['fields']
        
        # Check required fields
        if entry_type in self.required_fields:
            for req_field in self.required_fields[entry_type]:
                if req_field not in fields or not fields[req_field]:
                    # Special case: book can have author OR editor
                    if entry_type == 'book' and req_field == 'author':
                        if 'editor' not in fields or not fields['editor']:
                            errors.append({
                                'type': 'missing_required_field',
                                'field': 'author or editor',
                                'severity': 'high',
                                'message': f'Entry {key}: Missing required field "author" or "editor"'
                            })
                    else:
                        errors.append({
                            'type': 'missing_required_field',
                            'field': req_field,
                            'severity': 'high',
                            'message': f'Entry {key}: Missing required field "{req_field}"'
                        })
        
        # Check recommended fields
        if entry_type in self.recommended_fields:
            for rec_field in self.recommended_fields[entry_type]:
                if rec_field not in fields or not fields[rec_field]:
                    warnings.append({
                        'type': 'missing_recommended_field',
                        'field': rec_field,
                        'severity': 'medium',
                        'message': f'Entry {key}: Missing recommended field "{rec_field}"'
                    })
        
        # Validate year
        if 'year' in fields:
            year = fields['year']
            if not re.match(r'^\d{4}$', year):
                errors.append({
                    'type': 'invalid_year',
                    'field': 'year',
                    'value': year,
                    'severity': 'high',
                    'message': f'Entry {key}: Invalid year format "{year}" (should be 4 digits)'
                })
            elif int(year) < 1600 or int(year) > 2030:
                warnings.append({
                    'type': 'suspicious_year',
                    'field': 'year',
                    'value': year,
                    'severity': 'medium',
                    'message': f'Entry {key}: Suspicious year "{year}" (outside reasonable range)'
                })
        
        # Validate DOI format
        if 'doi' in fields:
            doi = fields['doi']
            if not re.match(r'^10\.\d{4,}/[^\s]+$', doi):
                warnings.append({
                    'type': 'invalid_doi_format',
                    'field': 'doi',
                    'value': doi,
                    'severity': 'medium',
                    'message': f'Entry {key}: Invalid DOI format "{doi}"'
                })
        
        # Check for single hyphen in pages (should be --)
        if 'pages' in fields:
            pages = fields['pages']
            if re.search(r'\d-\d', pages) and '--' not in pages:
                warnings.append({
                    'type': 'page_range_format',
                    'field': 'pages',
                    'value': pages,
                    'severity': 'low',
                    'message': f'Entry {key}: Page range uses single hyphen, should use -- (en-dash)'
                })
        
        # Check author format
        if 'author' in fields:
            author = fields['author']
            if ';' in author or '&' in author:
                errors.append({
                    'type': 'invalid_author_format',
                    'field': 'author',
                    'severity': 'high',
                    'message': f'Entry {key}: Authors should be separated by " and ", not ";" or "&"'
                })
        
        return errors, warnings
    
    def verify_doi(self, doi: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify DOI resolves correctly and get metadata.
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Tuple of (is_valid, metadata)
        """
        # Ask the registration agency, not the publisher. A HEAD request to
        # doi.org follows the redirect to the publisher, and several publishers
        # answer HEAD with 403 or 405 behind a bot check -- which made a
        # perfectly good DOI look unresolvable.
        try:
            crossref_url = f'https://api.crossref.org/works/{quote(doi, safe="")}'
            metadata_response = self.session.get(crossref_url, timeout=10)

            if metadata_response.status_code == 200:
                data = metadata_response.json()
                message = data.get('message', {})

                # Extract key metadata
                metadata = {
                    'title': (message.get('title') or [''])[0],
                    'year': self._extract_year_crossref(message),
                    'authors': self._format_authors_crossref(message.get('author', [])),
                }
                return True, metadata

            if metadata_response.status_code == 404:
                # Not a Crossref DOI. DataCite registers datasets and many
                # preprints, so check there before calling it broken.
                datacite_url = f'https://api.datacite.org/dois/{quote(doi, safe="")}'
                datacite_response = self.session.get(datacite_url, timeout=10)
                if datacite_response.status_code == 200:
                    return True, None
                return False, None

            # Any other status is a transport problem on our side, not
            # evidence that the DOI is bad.
            return True, None

        except requests.exceptions.RequestException:
            return True, None
    
    def detect_duplicates(self, entries: List[Dict]) -> List[Dict]:
        """
        Detect duplicate entries.
        
        Args:
            entries: List of entry dictionaries
            
        Returns:
            List of duplicate groups
        """
        duplicates = []
        
        # Check for duplicate DOIs
        doi_map = defaultdict(list)
        for entry in entries:
            doi = entry['fields'].get('doi', '').strip()
            if doi:
                doi_map[doi].append(entry['key'])
        
        for doi, keys in doi_map.items():
            if len(keys) > 1:
                duplicates.append({
                    'type': 'duplicate_doi',
                    'doi': doi,
                    'entries': keys,
                    'severity': 'high',
                    'message': f'Duplicate DOI {doi} found in entries: {", ".join(keys)}'
                })
        
        # Check for duplicate citation keys
        key_counts = defaultdict(int)
        for entry in entries:
            key_counts[entry['key']] += 1
        
        for key, count in key_counts.items():
            if count > 1:
                duplicates.append({
                    'type': 'duplicate_key',
                    'key': key,
                    'count': count,
                    'severity': 'high',
                    'message': f'Citation key "{key}" appears {count} times'
                })
        
        # Check for similar titles (possible duplicates)
        titles = {}
        for entry in entries:
            title = entry['fields'].get('title', '').lower()
            title = re.sub(r'[^\w\s]', '', title)  # Remove punctuation
            title = ' '.join(title.split())  # Normalize whitespace
            
            if title:
                if title in titles:
                    duplicates.append({
                        'type': 'similar_title',
                        'entries': [titles[title], entry['key']],
                        'severity': 'medium',
                        'message': f'Possible duplicate: "{titles[title]}" and "{entry["key"]}" have identical titles'
                    })
                else:
                    titles[title] = entry['key']
        
        return duplicates
    
    def parse_manuscript_citations(self, filepath: str) -> List[str]:
        """
        Parse a manuscript file (Markdown or LaTeX) and extract all cited keys.
        
        Args:
            filepath: Path to manuscript file
            
        Returns:
            List of cited citation keys
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f'Error reading manuscript file {filepath}: {e}', file=sys.stderr)
            return []
        
        cited_keys = set()
        
        # 1. LaTeX citations: \cite{key1, key2}, \citep{key}, \citet{key}, etc.
        latex_matches = re.findall(r'\\cite[a-z]*\*?\{([^}]+)\}', content)
        for match in latex_matches:
            keys = [k.strip() for k in match.split(',')]
            for key in keys:
                if key:
                    cited_keys.add(key)
                    
        # 2. Markdown / Pandoc citations: @key or [@key1; @key2]
        # Match @ followed by valid citation key chars (alphanumeric, -, _, :, .)
        # Avoid email addresses, twitter handles, etc. by requiring that @ is not preceded by alphanumeric/dot/dash/underscore
        md_matches = re.findall(r'(?<![a-zA-Z0-9_.-])@([a-zA-Z0-9_\-:]+)', content)
        for key in md_matches:
            # Exclude common false positives
            if key and not key.isdigit():
                cited_keys.add(key)
                
        return list(cited_keys)

    def validate_file(self, filepath: str, check_dois: bool = False, min_count: Optional[int] = None, venue: Optional[str] = None, manuscript_filepath: Optional[str] = None) -> Dict:
        """
        Validate entire BibTeX file.
        
        Args:
            filepath: Path to BibTeX file
            check_dois: Whether to verify DOIs (slow)
            min_count: Optional minimum citation count to enforce
            venue: Optional venue type to check against standards
            manuscript_filepath: Optional path to manuscript to cross-check citations
            
        Returns:
            Validation report dictionary
        """
        print(f'Parsing {filepath}...', file=sys.stderr)
        entries = self.parse_bibtex_file(filepath)
        
        if not entries:
            return {
                'filepath': filepath,
                'total_entries': 0,
                'valid_entries': 0,
                'errors': [{
                    'type': 'empty_bibtex_file',
                    'severity': 'high',
                    'message': f'BibTeX file {filepath} has no valid entries.'
                }],
                'warnings': [],
                'duplicates': [],
                'venue_standard_checked': venue,
                'min_count_checked': min_count,
                'manuscript_results': {'checked': False}
            }
        
        print(f'Found {len(entries)} entries', file=sys.stderr)
        
        all_errors = []
        all_warnings = []
        
        # Validate each entry
        for i, entry in enumerate(entries):
            print(f'Validating entry {i+1}/{len(entries)}: {entry["key"]}', file=sys.stderr)
            errors, warnings = self.validate_entry(entry)
            
            for error in errors:
                error['entry'] = entry['key']
                all_errors.append(error)
            
            for warning in warnings:
                warning['entry'] = entry['key']
                all_warnings.append(warning)
        
        # Check for duplicates
        print('Checking for duplicates...', file=sys.stderr)
        duplicates = self.detect_duplicates(entries)
        
        # Verify DOIs if requested
        doi_errors = []
        if check_dois:
            print('Verifying DOIs...', file=sys.stderr)
            for i, entry in enumerate(entries):
                doi = entry['fields'].get('doi', '')
                if doi:
                    print(f'Verifying DOI {i+1}: {doi}', file=sys.stderr)
                    is_valid, metadata = self.verify_doi(doi)
                    
                    if not is_valid:
                        doi_errors.append({
                            'type': 'invalid_doi',
                            'entry': entry['key'],
                            'doi': doi,
                            'severity': 'high',
                            'message': f'Entry {entry["key"]}: DOI does not resolve: {doi}'
                        })
        
        all_errors.extend(doi_errors)
        
        # Count and Venue verification logic
        count_errors = []
        count_warnings = []

        target_min = None
        target_max = None
        venue_name = None

        if venue:
            v_lower = venue.lower().strip()
            if v_lower in self.venue_standards:
                target_min, target_max, venue_name = self.venue_standards[v_lower]
            else:
                print(f"Warning: Unknown venue '{venue}'. Supported venues are: {', '.join(self.venue_standards.keys())}", file=sys.stderr)
        
        if min_count is not None:
            target_min = min_count
            venue_name = f"Custom threshold (min: {min_count})"
            target_max = None
            
        # A reference list is never *wrong* for being short -- the right length
        # is whatever the argument needs -- so a shortfall is reported as a
        # warning. `--min-count` is the exception: an explicit floor the caller
        # asked to have enforced, so falling under it is an error.
        total_count = len(entries)
        if target_min is not None:
            if min_count is not None and total_count < min_count:
                count_errors.append({
                    'type': 'below_requested_minimum',
                    'severity': 'high',
                    'message': f'Total citation entries ({total_count}) is below the requested minimum of {min_count}.'
                })
            elif total_count < target_min:
                count_warnings.append({
                    'type': 'low_citation_count',
                    'severity': 'medium',
                    'message': f'Total citation entries ({total_count}) is below the {venue_name or "specified standard"} rule of thumb of {target_min}-{target_max or "+"}. This is a heuristic, not a submission requirement.'
                })

        # Manuscript checking logic
        manuscript_results = {
            'checked': False,
            'manuscript_filepath': None,
            'cited_keys': [],
            'missing_keys': [],
            'unused_keys': []
        }
        
        if manuscript_filepath:
            manuscript_results['checked'] = True
            manuscript_results['manuscript_filepath'] = manuscript_filepath
            
            # Parse cited keys
            cited_keys = self.parse_manuscript_citations(manuscript_filepath)
            manuscript_results['cited_keys'] = cited_keys
            
            bib_keys = {entry['key'] for entry in entries}
            
            # Missing references: cited in manuscript but not defined in BibTeX
            missing_keys = [key for key in cited_keys if key not in bib_keys]
            manuscript_results['missing_keys'] = missing_keys
            for key in missing_keys:
                all_errors.append({
                    'type': 'unresolved_citation',
                    'entry': key,
                    'severity': 'high',
                    'message': f'Unresolved citation: Key "@{key}" is cited in manuscript "{manuscript_filepath}" but not defined in the BibTeX file.'
                })
                
            # Unused references: defined in BibTeX but not cited in manuscript
            unused_keys = [key for key in bib_keys if key not in cited_keys]
            manuscript_results['unused_keys'] = unused_keys
            for key in unused_keys:
                all_warnings.append({
                    'type': 'unused_citation',
                    'entry': key,
                    'severity': 'medium',
                    'message': f'Unused citation: Reference "{key}" is defined in the BibTeX file but not cited in the manuscript.'
                })
                
            # Check the count of ACTUALLY used citations
            actual_count = len(cited_keys) - len(missing_keys)
            if target_min is not None:
                if min_count is not None and actual_count < min_count:
                    count_errors.append({
                        'type': 'manuscript_below_requested_minimum',
                        'severity': 'high',
                        'message': f'The manuscript cites {actual_count} references, below the requested minimum of {min_count}.'
                    })
                elif actual_count < target_min:
                    count_warnings.append({
                        'type': 'low_manuscript_citation_count',
                        'severity': 'medium',
                        'message': f'The manuscript cites {actual_count} references, below the {venue_name or "specified standard"} rule of thumb of {target_min}-{target_max or "+"}. This is a heuristic, not a submission requirement.'
                    })

        all_errors.extend(count_errors)
        all_warnings.extend(count_warnings)

        # Count entries carrying at least one high-severity error, rather than
        # subtracting the error count -- several errors can land on one entry,
        # which previously drove this figure negative.
        entries_with_errors = {
            error['entry'] for error in all_errors
            if error.get('severity') == 'high' and error.get('entry')
        }
        bib_keys_present = {entry['key'] for entry in entries}

        return {
            'filepath': filepath,
            'total_entries': len(entries),
            'valid_entries': len(entries) - len(entries_with_errors & bib_keys_present),
            'errors': all_errors,
            'warnings': all_warnings,
            'duplicates': duplicates,
            'venue_standard_checked': venue,
            'min_count_checked': min_count,
            'manuscript_results': manuscript_results
        }
    
    def _extract_year_crossref(self, message: Dict) -> str:
        """Extract year from CrossRef message."""
        date_parts = message.get('published-print', {}).get('date-parts', [[]])
        if not date_parts or not date_parts[0]:
            date_parts = message.get('published-online', {}).get('date-parts', [[]])
        
        if date_parts and date_parts[0]:
            return str(date_parts[0][0])
        return ''
    
    def _format_authors_crossref(self, authors: List[Dict]) -> str:
        """Format author list from CrossRef."""
        if not authors:
            return ''
        
        formatted = []
        for author in authors[:3]:  # First 3 authors
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                formatted.append(f'{family}, {given}' if given else family)
        
        if len(authors) > 3:
            formatted.append('et al.')
        
        return ', '.join(formatted)


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Validate BibTeX files for errors and inconsistencies',
        epilog='Example: python validate_citations.py references.bib'
    )
    
    parser.add_argument(
        'file',
        help='BibTeX file to validate'
    )
    
    parser.add_argument(
        '--check-dois',
        action='store_true',
        help='Verify DOIs resolve correctly (slow)'
    )
    
    parser.add_argument(
        '--report',
        help='Output file for the JSON validation report'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    
    parser.add_argument(
        '--min-count',
        type=int,
        help='Enforce a minimum number of citation entries'
    )
    
    parser.add_argument(
        '--venue',
        help='Enforce citation standards for a specific venue (e.g. nature, neurips, review)'
    )
    
    parser.add_argument(
        '--manuscript',
        help='Path to manuscript file (Markdown or LaTeX) to check for unresolved or unused citations'
    )
    
    args = parser.parse_args()
    
    # Validate file
    validator = CitationValidator()
    report = validator.validate_file(
        args.file, 
        check_dois=args.check_dois,
        min_count=args.min_count,
        venue=args.venue,
        manuscript_filepath=args.manuscript
    )
    
    # Print summary
    print('\n' + '='*60)
    print('CITATION VALIDATION REPORT')
    print('='*60)
    print(f'\nFile: {args.file}')
    if report.get('venue_standard_checked'):
        print(f'Venue Standard: {report["venue_standard_checked"]}')
    if report.get('min_count_checked') is not None:
        print(f'Required Min Count: {report["min_count_checked"]}')
    print(f'Total entries in BibTeX: {report["total_entries"]}')
    
    m_res = report.get('manuscript_results', {})
    if m_res.get('checked'):
        print(f'Manuscript checked: {m_res["manuscript_filepath"]}')
        print(f'  Actual unique citations in manuscript: {len(m_res["cited_keys"])}')
        print(f'  Missing/unresolved: {len(m_res["missing_keys"])}')
        print(f'  Unused in bib file: {len(m_res["unused_keys"])}')
        
    print(f'Valid entries: {report["valid_entries"]}')
    print(f'Errors: {len(report["errors"])}')
    print(f'Warnings: {len(report["warnings"])}')
    print(f'Duplicates: {len(report["duplicates"])}')
    
    # Print errors
    if report['errors']:
        print('\n' + '-'*60)
        print('ERRORS (must fix):')
        print('-'*60)
        for error in report['errors']:
            print(f'\n{error["message"]}')
            if args.verbose:
                print(f'  Type: {error["type"]}')
                print(f'  Severity: {error["severity"]}')
    
    # Print warnings
    if report['warnings'] and (args.verbose or report.get('venue_standard_checked') or report.get('min_count_checked') is not None or m_res.get('checked')):
        print('\n' + '-'*60)
        print('WARNINGS (should fix):')
        print('-'*60)
        for warning in report['warnings']:
            print(f'\n{warning["message"]}')
    
    # Print duplicates
    if report['duplicates']:
        print('\n' + '-'*60)
        print('DUPLICATES:')
        print('-'*60)
        for dup in report['duplicates']:
            print(f'\n{dup["message"]}')
    
    # Save report
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f'\nDetailed report saved to: {args.report}')
    
    # Exit with error code if there are high-severity errors
    has_high_errors = any(e.get('severity') == 'high' for e in report['errors'])
    if has_high_errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### `assets/bibtex_template.bib`

```bibtex
% BibTeX Template File
% Examples of properly formatted entries for all common types

% =============================================================================
% JOURNAL ARTICLES
% =============================================================================

@article{Jumper2021,
  author  = {Jumper, John and Evans, Richard and Pritzel, Alexander and Green, Tim and Figurnov, Michael and Ronneberger, Olaf and Tunyasuvunakool, Kathryn and Bates, Russ and {\v{Z}}{\'\i}dek, Augustin and Potapenko, Anna and others},
  title   = {Highly Accurate Protein Structure Prediction with {AlphaFold}},
  journal = {Nature},
  year    = {2021},
  volume  = {596},
  number  = {7873},
  pages   = {583--589},
  doi     = {10.1038/s41586-021-03819-2}
}

@article{Watson1953,
  author  = {Watson, James D. and Crick, Francis H. C.},
  title   = {Molecular Structure of Nucleic Acids: A Structure for Deoxyribose Nucleic Acid},
  journal = {Nature},
  year    = {1953},
  volume  = {171},
  number  = {4356},
  pages   = {737--738},
  doi     = {10.1038/171737a0}
}

@article{Doudna2014,
  author  = {Doudna, Jennifer A. and Charpentier, Emmanuelle},
  title   = {The New Frontier of Genome Engineering with {CRISPR-Cas9}},
  journal = {Science},
  year    = {2014},
  volume  = {346},
  number  = {6213},
  pages   = {1258096},
  doi     = {10.1126/science.1258096}
}

% =============================================================================
% BOOKS
% =============================================================================

@book{Kumar2021,
  author    = {Kumar, Vinay and Abbas, Abul K. and Aster, Jon C.},
  title     = {Robbins and Cotran Pathologic Basis of Disease},
  publisher = {Elsevier},
  year      = {2021},
  edition   = {10},
  address   = {Philadelphia, PA},
  isbn      = {978-0-323-53113-9}
}

@book{Alberts2014,
  author    = {Alberts, Bruce and Johnson, Alexander and Lewis, Julian and Morgan, David and Raff, Martin and Roberts, Keith and Walter, Peter},
  title     = {Molecular Biology of the Cell},
  publisher = {Garland Science},
  year      = {2014},
  edition   = {6},
  address   = {New York, NY},
  isbn      = {978-0-815-34432-2}
}

% Book with editor instead of author
@book{Sambrook2001,
  editor    = {Sambrook, Joseph and Russell, David W.},
  title     = {Molecular Cloning: A Laboratory Manual},
  publisher = {Cold Spring Harbor Laboratory Press},
  year      = {2001},
  edition   = {3},
  address   = {Cold Spring Harbor, NY},
  isbn      = {978-0-879-69576-7}
}

% =============================================================================
% CONFERENCE PAPERS (PROCEEDINGS)
% =============================================================================

@inproceedings{Vaswani2017,
  author    = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, {\L}ukasz and Polosukhin, Illia},
  title     = {Attention is All You Need},
  booktitle = {Advances in Neural Information Processing Systems 30 (NeurIPS 2017)},
  year      = {2017},
  pages     = {5998--6008},
  address   = {Long Beach, CA},
  url       = {https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html}
}

@inproceedings{He2016,
  author    = {He, Kaiming and Zhang, Xiangyu and Ren, Shaoqing and Sun, Jian},
  title     = {Deep Residual Learning for Image Recognition},
  booktitle = {Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  year      = {2016},
  pages     = {770--778},
  address   = {Las Vegas, NV},
  doi       = {10.1109/CVPR.2016.90}
}

% =============================================================================
% BOOK CHAPTERS
% =============================================================================

@incollection{Brown2020,
  author    = {Brown, Peter O. and Botstein, David},
  title     = {Exploring the New World of the Genome with {DNA} Microarrays},
  booktitle = {DNA Microarrays: A Molecular Cloning Manual},
  editor    = {Eisen, Michael B. and Brown, Patrick O.},
  publisher = {Cold Spring Harbor Laboratory Press},
  year      = {2020},
  pages     = {1--45},
  address   = {Cold Spring Harbor, NY}
}

% =============================================================================
% PHD THESES / DISSERTATIONS
% =============================================================================

@phdthesis{Johnson2023,
  author  = {Johnson, Mary L.},
  title   = {Novel Approaches to Cancer Immunotherapy Using {CRISPR} Technology},
  school  = {Stanford University},
  year    = {2023},
  type    = {{PhD} dissertation},
  address = {Stanford, CA}
}

% =============================================================================
% MASTER'S THESES
% =============================================================================

@mastersthesis{Smith2022,
  author  = {Smith, Robert J.},
  title   = {Machine Learning Methods for Protein Structure Prediction},
  school  = {Massachusetts Institute of Technology},
  year    = {2022},
  type    = {{Master's} thesis},
  address = {Cambridge, MA}
}

% =============================================================================
% TECHNICAL REPORTS
% =============================================================================

@techreport{WHO2020,
  author      = {{World Health Organization}},
  title       = {Clinical Management of {COVID-19}: Interim Guidance},
  institution = {World Health Organization},
  year        = {2020},
  type        = {Technical Report},
  number      = {WHO/2019-nCoV/clinical/2020.5},
  address     = {Geneva, Switzerland}
}

% =============================================================================
% PREPRINTS
% =============================================================================

% bioRxiv preprint
@misc{Zhang2024preprint,
  author       = {Zhang, Yi and Chen, Li and Wang, Hui and Liu, Xin},
  title        = {Novel Therapeutic Targets in {Alzheimer}'s Disease},
  year         = {2024},
  howpublished = {bioRxiv},
  doi          = {10.1101/2024.01.15.575432},
  note         = {Preprint}
}

% arXiv preprint
@misc{Brown2024arxiv,
  author       = {Brown, Alice and Green, Bob},
  title        = {Advances in Quantum Computing},
  year         = {2024},
  howpublished = {arXiv},
  note         = {arXiv:2401.12345}
}

% =============================================================================
% DATASETS
% =============================================================================

@misc{AlphaFoldDB2021,
  author       = {{DeepMind} and {EMBL-EBI}},
  title        = {{AlphaFold} Protein Structure Database},
  year         = {2021},
  howpublished = {Database},
  url          = {https://alphafold.ebi.ac.uk/},
  doi          = {10.1093/nar/gkab1061},
  note         = {Version 4}
}

% =============================================================================
% SOFTWARE / CODE
% =============================================================================

@misc{McKinney2010pandas,
  author       = {McKinney, Wes},
  title        = {pandas: A Foundational {Python} Library for Data Analysis and Statistics},
  year         = {2010},
  howpublished = {Software},
  url          = {https://pandas.pydata.org/},
  note         = {Python Data Analysis Library}
}

% =============================================================================
% WEBSITES / ONLINE RESOURCES
% =============================================================================

@misc{NCBI2024,
  author       = {{National Center for Biotechnology Information}},
  title        = {{PubMed}: Database of Biomedical Literature},
  year         = {2024},
  howpublished = {Website},
  url          = {https://pubmed.ncbi.nlm.nih.gov/},
  note         = {Accessed: 2024-01-15}
}

% =============================================================================
% SPECIAL CASES
% =============================================================================

% Article with organization as author
@article{NatureEditorial2023,
  author  = {{Nature Editorial Board}},
  title   = {The Future of {AI} in Scientific Research},
  journal = {Nature},
  year    = {2023},
  volume  = {615},
  pages   = {1--2},
  doi     = {10.1038/d41586-023-00001-1}
}

% Article with no volume number (some journals)
@article{OpenAccess2024,
  author  = {Williams, Sarah and Thomas, Michael},
  title   = {Open Access Publishing in the 21st Century},
  journal = {Journal of Scholarly Communication},
  year    = {2024},
  pages   = {e123456},
  doi     = {10.1234/jsc.2024.123456}
}

% Conference paper with DOI
@inproceedings{Garcia2023,
  author    = {Garc{\'i}a-Mart{\'i}nez, Jos{\'e} and M{\"u}ller, Hans},
  title     = {International Collaboration in Science},
  booktitle = {Proceedings of the International Conference on Academic Publishing},
  year      = {2023},
  pages     = {45--52},
  doi       = {10.1109/ICAP.2023.123456}
}

% Article with PMID but no DOI (older papers)
@article{OldPaper1995,
  author  = {Anderson, Philip W.},
  title   = {Through the Glass Lightly},
  journal = {Science},
  year    = {1995},
  volume  = {267},
  number  = {5204},
  pages   = {1615--1616},
  note    = {PMID: 17808148}
}
```

### `assets/citation_checklist.md`

# Citation Quality Checklist

Use this checklist to ensure your citations are accurate, complete, and properly formatted before final submission.

## Pre-Submission Checklist

### ✓ Metadata Accuracy

- [ ] All author names are correct and properly formatted
- [ ] Article titles match the actual publication
- [ ] Journal/conference names are complete (not abbreviated unless required)
- [ ] Publication years are accurate
- [ ] Volume and issue numbers are correct
- [ ] Page ranges are accurate

### ✓ Required Fields

- [ ] All @article entries have: author, title, journal, year
- [ ] All @book entries have: author/editor, title, publisher, year
- [ ] All @inproceedings entries have: author, title, booktitle, year
- [ ] Modern papers (2000+) include DOI when available
- [ ] All entries have unique citation keys

### ✓ DOI Verification

- [ ] All DOIs are properly formatted (10.XXXX/...)
- [ ] DOIs resolve correctly to the article
- [ ] No DOI prefix in the BibTeX field (no "doi:" or "https://doi.org/")
- [ ] Metadata from CrossRef matches your BibTeX entry
- [ ] Run: `python scripts/validate_citations.py references.bib --check-dois`

### ✓ Formatting Consistency

- [ ] Page ranges use double hyphen (--) not single (-)
- [ ] No "pp." prefix in pages field
- [ ] Author names use "and" separator (not semicolon or ampersand)
- [ ] Capitalization protected in titles ({AlphaFold}, {CRISPR}, etc.)
- [ ] Month names use standard abbreviations if included
- [ ] Citation keys follow consistent format

### ✓ Duplicate Detection

- [ ] No duplicate DOIs in bibliography
- [ ] No duplicate citation keys
- [ ] No near-duplicate titles
- [ ] Preprints updated to published versions when available
- [ ] Run: `python scripts/validate_citations.py references.bib`

### ✓ Special Characters

- [ ] Accented characters properly formatted (e.g., {\"u} for ü)
- [ ] Mathematical symbols use LaTeX commands
- [ ] Chemical formulas properly formatted
- [ ] No unescaped special characters (%, &, $, #, etc.)

### ✓ BibTeX Syntax

- [ ] All entries have balanced braces {}
- [ ] Fields separated by commas
- [ ] No comma after last field in each entry
- [ ] Valid entry types (@article, @book, etc.)
- [ ] Run: `python scripts/validate_citations.py references.bib`

### ✓ File Organization

- [ ] Bibliography sorted in logical order (by year, author, or key)
- [ ] Consistent formatting throughout
- [ ] No formatting inconsistencies between entries
- [ ] Run: `python scripts/format_bibtex.py references.bib --sort year`

## Automated Validation

### Step 1: Format and Clean

```bash
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output clean_references.bib
```

**What this does**:
- Removes duplicates
- Standardizes formatting
- Fixes common issues (page ranges, DOI format, etc.)
- Sorts by year (newest first)

### Step 2: Validate

```bash
python scripts/validate_citations.py clean_references.bib \
  --check-dois \
  --report validation_report.json \
  --verbose
```

**What this does**:
- Checks required fields
- Verifies DOIs resolve
- Detects duplicates
- Validates syntax
- Generates detailed report

### Step 3: Review Report

```bash
cat validation_report.json
```

**Address any**:
- **Errors**: Must fix (missing fields, broken DOIs, syntax errors)
- **Warnings**: Should fix (missing recommended fields, formatting issues)
- **Duplicates**: Remove or consolidate

### Step 4: Final Check

```bash
python scripts/validate_citations.py clean_references.bib --verbose
```

**Goal**: Zero errors, minimal warnings

## Manual Review Checklist

### Critical Citations (Top 10-20 Most Important)

For your most important citations, manually verify:

- [ ] Visit DOI link and confirm it's the correct article
- [ ] Check author names against the actual publication
- [ ] Verify year matches publication date
- [ ] Confirm journal/conference name is correct
- [ ] Check that volume/pages match

### Common Issues to Watch For

**Missing Information**:
- [ ] No DOI for papers published after 2000
- [ ] Missing volume or page numbers for journal articles
- [ ] Missing publisher for books
- [ ] Missing conference location for proceedings

**Formatting Errors**:
- [ ] Single hyphen in page ranges (123-145 → 123--145)
- [ ] Ampersands in author lists (Smith & Jones → Smith and Jones)
- [ ] Unprotected acronyms in titles (DNA → {DNA})
- [ ] DOI includes URL prefix (https://doi.org/10.xxx → 10.xxx)

**Metadata Mismatches**:
- [ ] Author names differ from publication
- [ ] Year is online-first instead of print publication
- [ ] Journal name abbreviated when it should be full
- [ ] Volume/issue numbers swapped

**Duplicates**:
- [ ] Same paper cited with different citation keys
- [ ] Preprint and published version both cited
- [ ] Conference paper and journal version both cited

## Field-Specific Checks

### Biomedical Sciences

- [ ] PubMed Central ID (PMCID) included when available
- [ ] MeSH terms appropriate (if using)
- [ ] Clinical trial registration number included (if applicable)
- [ ] All references to treatments/drugs accurately cited

### Computer Science

- [ ] arXiv ID included for preprints
- [ ] Conference proceedings properly cited (not just "NeurIPS")
- [ ] Software/dataset citations include version numbers
- [ ] GitHub links stable and permanent

### General Sciences

- [ ] Data availability statements properly cited
- [ ] Retracted papers identified and removed
- [ ] Preprints checked for published versions
- [ ] Supplementary materials referenced if critical

## Final Pre-Submission Steps

### 1 Week Before Submission

- [ ] Run full validation with DOI checking
- [ ] Fix all errors and critical warnings
- [ ] Manually verify top 10-20 most important citations
- [ ] Check for any retracted papers

### 3 Days Before Submission

- [ ] Re-run validation after any manual edits
- [ ] Ensure all in-text citations have corresponding bibliography entries
- [ ] Ensure all bibliography entries are cited in text
- [ ] Check citation style matches journal requirements

### 1 Day Before Submission

- [ ] Final validation check
- [ ] LaTeX compilation successful with no warnings
- [ ] PDF renders all citations correctly
- [ ] Bibliography appears in correct format
- [ ] No placeholder citations (Smith et al. XXXX)

### Submission Day

- [ ] One final validation run
- [ ] No last-minute edits without re-validation
- [ ] Bibliography file included in submission package
- [ ] Figures/tables referenced in text match bibliography

## Quality Metrics

### Excellent Bibliography

- ✓ 100% of entries have DOIs (for modern papers)
- ✓ Zero validation errors
- ✓ Zero missing required fields
- ✓ Zero broken DOIs
- ✓ Zero duplicates
- ✓ Consistent formatting throughout
- ✓ All citations manually spot-checked

### Acceptable Bibliography

- ✓ 90%+ of modern entries have DOIs
- ✓ Zero high-severity errors
- ✓ Minor warnings only (e.g., missing recommended fields)
- ✓ Key citations manually verified
- ✓ Compilation succeeds without errors

### Needs Improvement

- ✗ Missing DOIs for recent papers
- ✗ High-severity validation errors
- ✗ Broken or incorrect DOIs
- ✗ Duplicate entries
- ✗ Inconsistent formatting
- ✗ Compilation warnings or errors

## Emergency Fixes

If you discover issues at the last minute:

### Broken DOI

```bash
# Find correct DOI
# Option 1: Search CrossRef
# https://www.crossref.org/

# Option 2: Search on publisher website
# Option 3: Google Scholar

# Re-extract metadata
python scripts/extract_metadata.py --doi CORRECT_DOI
```

### Missing Information

```bash
# Extract from DOI
python scripts/extract_metadata.py --doi 10.xxxx/yyyy

# Or from PMID (biomedical)
python scripts/extract_metadata.py --pmid 12345678

# Or from arXiv
python scripts/extract_metadata.py --arxiv 2103.12345
```

### Duplicate Entries

```bash
# Auto-remove duplicates
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --output fixed_references.bib
```

### Formatting Errors

```bash
# Auto-fix common issues
python scripts/format_bibtex.py references.bib \
  --output fixed_references.bib

# Then validate
python scripts/validate_citations.py fixed_references.bib
```

## Long-Term Best Practices

### During Research

- [ ] Add citations to bibliography file as you find them
- [ ] Extract metadata immediately using DOI
- [ ] Validate after every 10-20 additions
- [ ] Keep bibliography file under version control

### During Writing

- [ ] Cite as you write
- [ ] Use consistent citation keys
- [ ] Don't delay adding references
- [ ] Validate weekly

### Before Submission

- [ ] Allow 2-3 days for citation cleanup
- [ ] Don't wait until the last day
- [ ] Automate what you can
- [ ] Manually verify critical citations

## Tool Quick Reference

### Extract Metadata

```bash
# From DOI
python scripts/doi_to_bibtex.py 10.1038/nature12345

# From multiple sources
python scripts/extract_metadata.py \
  --doi 10.1038/nature12345 \
  --pmid 12345678 \
  --arxiv 2103.12345 \
  --output references.bib
```

### Validate

```bash
# Basic validation
python scripts/validate_citations.py references.bib

# With DOI checking (slow but thorough)
python scripts/validate_citations.py references.bib --check-dois

# Generate report
python scripts/validate_citations.py references.bib \
  --report validation.json \
  --verbose
```

### Format and Clean

```bash
# Format and fix issues
python scripts/format_bibtex.py references.bib

# Remove duplicates and sort
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output clean_refs.bib
```

## Summary

**Minimum Requirements**:
1. Run `format_bibtex.py --deduplicate`
2. Run `validate_citations.py`
3. Fix all errors
4. Compile successfully

**Recommended**:
1. Format, deduplicate, and sort
2. Validate with `--check-dois`
3. Fix all errors and warnings
4. Manually verify top citations
5. Re-validate after fixes

**Best Practice**:
1. Validate throughout research process
2. Use automated tools consistently
3. Keep bibliography clean and organized
4. Document any special cases
5. Final validation 1-3 days before submission

**Remember**: Citation errors reflect poorly on your scholarship. Taking time to ensure accuracy is worthwhile!
