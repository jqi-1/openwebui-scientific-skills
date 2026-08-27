---
name: peer-review
description: Prepare evidence-bounded, constructive peer-review drafts and structured manuscript assessments. Use for authorized review of scientific manuscripts, protocols, preprints, or research proposals; reporting-guideline selection; claim–evidence checks; methods, statistics, reproducibility, ethics, figure/table, and citation critique; or revision-response planning.
---

# Peer Review

Support an accountable human reviewer with a rigorous, fair, actionable assessment. Treat every unpublished submission and review as confidential.

## Mandatory safety boundary

Before reading or analyzing unpublished content:

1. Confirm the user is authorized by the publisher, editor, author, or other material owner.
2. Check the target venue’s review, confidentiality, co-review, retention, and AI/tool policies.
3. Record conflicts, competence limits, requested scope, and specialist-review needs.
4. Default to local-only processing.

If authorization is unclear, do not inspect or quote the manuscript. Ask for confirmation or use only the bundled local CLIs, whose reports do not echo manuscript text.

Never:

- Send unpublished manuscript, supplement, review, or editorial text to an external service without specific publisher/author authorization and venue permission
- Upload confidential content to a public model, search engine, citation service, grammar tool, plagiarism checker, or image service
- Reuse content for training, benchmarking, product improvement, or unrelated research
- Read broad environment state, `.env` files, API keys, or credentials
- Call a network, LLM, or image API from bundled tools
- Invoke another skill or a PDF/image pipeline automatically
- Impersonate an assigned reviewer, editor, journal, funder, or author
- Fabricate manuscript details, review findings, citations, analyses, experiments, reproduction, or an editorial outcome
- Announce a decision that belongs to an editor or panel

Delete local copies and derivatives when policy requires; otherwise retain only what the controlling policy authorizes. Record deletion or retention without copying confidential content into the record.

Read `references/ethical_review_practice.md` before handling confidential material.

## Human accountability

Label generated text as a working draft. The accountable human must:

- Read the complete authorized submission and relevant supplements
- Verify every factual statement, calculation, citation, and manuscript location
- Resolve conflicts and disclose assistance as required
- Rewrite comments in their own expert judgment
- Submit through the authorized channel

Automated coverage, consistency, or lint results are not peer review and do not establish manuscript merit.

## Intake gate

Copy and complete `assets/review_intake_template.json`, then run:

```bash
python3 scripts/validate_review_intake.py completed-intake.json
```

Proceed only when status is `READY_FOR_LOCAL_REVIEW`.

The validator blocks:

- Undocumented authorization
- Missing human accountability
- Unassessed or unresolved conflicts
- Unknown review model or unchecked venue policy
- Unauthorized AI assistance
- External service use
- Data reuse
- Missing deletion/retention planning

It validates declarations, not their truth.

## Review workflow

### 1. Establish scope and available evidence

Record:

- Submission type and stage
- Review question and requested focus
- Target venue and review model
- Materials actually available: manuscript, supplements, protocol, registration, analysis plan, data/code statement, prior decision, or response letter
- Competence areas and limits
- Missing material that prevents assessment

Do not infer absent content. Use “not reported” or “not available for review.”

### 2. Orient without deciding

Create a short neutral map:

- Research question
- Population or system
- Design and unit
- Intervention, exposure, test, or model
- Comparator/reference
- Outcomes and timing
- Principal claims

Do not write an acceptance/rejection recommendation. Identify what evidence would be needed to evaluate each claim.

### 3. Select reporting guidance

Copy `assets/study_profile_template.json` and run:

```bash
python3 scripts/select_reporting_guidelines.py local-profile.json
```

For checklist coverage:

```bash
python3 scripts/select_reporting_guidelines.py \
  local-profile.json \
  --coverage local-coverage.csv
```

Use the current base guideline, explanation/elaboration, applicable extensions, and target venue policy. See `references/reporting_standards.md`.

**Critical distinction:** reporting completeness is not design quality, risk of bias, validity, or merit. Never convert missing items into an automatic score or publication judgment.

### 4. Map claims to evidence

Prioritize central, causal, mechanistic, safety, diagnostic, prediction, and generalization claims.

For each claim, record:

- Location and claim ID
- Supporting result, figure, table, analysis, or citation IDs
- Direction, magnitude, population, outcome, timepoint, and uncertainty alignment
- Limitation or alternative explanation
- Bounded requested action

Run:

```bash
python3 scripts/validate_claim_evidence.py local-claim-matrix.csv
```

Start from `assets/claim_evidence_matrix_template.csv`. The report emits IDs and counts, not claim text.

### 5. Review methods and statistics

Assess in this order:

1. Question and target quantity
2. Design and unit of inference
3. Sampling, allocation, controls, masking, and timing
4. Sample-size or precision rationale
5. Inclusion, exclusion, attrition, and missingness
6. Analysis–design alignment and assumptions
7. Multiplicity and prespecification
8. Effect estimates, uncertainty, denominators, and harms
9. Interpretation, causality, and generalizability

Use `references/common_issues.md` and `references/statistical_reproducibility.md`.

For a structured local audit:

```bash
python3 scripts/audit_statistics_reproducibility.py \
  local-statistics-reproducibility.json
```

Start from `assets/statistical_reproducibility_template.json`. Request specialist review when a central method exceeds competence; do not hide uncertainty behind a generic critique.

### 6. Review reproducibility and transparency

Check, as applicable:

- Protocol, registration, amendments, and analysis-plan consistency
- Data provenance, exclusions, transformations, and accession IDs
- Software, package, model, and parameter versions
- Code, environment, seeds, run instructions, and tests
- Data, code, materials, and model availability or justified restrictions
- Domain metadata standards

Do not claim reproduction unless authorized inputs were actually run with documented commands, environment, and outputs.

### 7. Review ethics and integrity

Check applicable approvals, consent, welfare, privacy, community governance, funding, sponsor role, conflicts, authorship/contribution, registration, biosafety, and dual-use concerns.

Describe observable evidence and uncertainty. Do not accuse authors or investigate them. Route credible concerns through the confidential editor channel under venue policy.

### 8. Review figures, tables, and citations

For figures and tables, assess:

- Consistency with text and supplements
- Denominators, units, axes, scales, uncertainty, and legends
- Accessible encoding and sufficient context
- Image acquisition/processing disclosure and source-data policy

This skill has no image-generation or PDF-conversion workflow. Use only user-authorized local artifacts and tools.

For Pandoc-style citations such as `[@ref-id]`:

```bash
python3 scripts/audit_citations.py local-manuscript.md local-references.csv
```

Start from `assets/citation_references_template.csv`. This checks key consistency and identifier format only; it does not verify that a source exists or supports a claim.

### 9. Draft actionable comments

Generate a private scaffold only after intake passes:

```bash
python3 scripts/generate_review_scaffold.py \
  completed-intake.json \
  -o private-review.md
```

Every major/minor comment should include:

- **Location**
- **Observation**
- **Evidence or criterion**
- **Why it matters**
- **Requested action**

Prioritize:

- Claim–evidence alignment
- Methods and statistical validity
- Reproducibility and transparency
- Ethics and participant/animal protection
- Reporting needed for appraisal
- Figures, tables, limitations, and citations

Requests for new work must be necessary to support a central claim and proportionate to scope. Offer narrowing, clarification, sensitivity analysis, correction, or limitation language when that is sufficient.

### 10. Keep channels separate

**Comments to authors** contain the scientific review, strengths, major/minor comments, and limitations.

**Confidential comments to editor** contain only policy-appropriate conflicts, competence limits, assistance disclosure, specialist requests, or substantiated integrity/process concerns that require a separate route.

Do not place ordinary criticism only in confidential notes. Do not reveal reviewer identity under an anonymized process.

### 11. Lint and finalize

```bash
python3 scripts/lint_review.py private-review.md
```

The linter checks channel separation, unresolved placeholders, a narrow abusive-language lexicon, role/decision phrases, and required actionability fields. It emits line numbers and rule IDs, not review text. Human tone and scientific review remain mandatory.

Before handoff:

- Verify all locations and evidence.
- Remove unsupported or speculative criticism.
- Confirm professional, non-abusive language.
- State review limits and specialist needs.
- Disclose permitted assistance.
- Remove all placeholders.
- Ensure no invented citation, experiment, reanalysis, or outcome.
- Follow the documented deletion/retention rule.

## Local tool index

- `scripts/validate_review_intake.py` — scope, authorization, conflicts, policy, handling
- `scripts/select_reporting_guidelines.py` — dated selector and non-scoring coverage audit
- `scripts/validate_claim_evidence.py` — claim/evidence alignment matrix
- `scripts/audit_statistics_reproducibility.py` — methods/statistics/reproducibility checklist
- `scripts/audit_citations.py` — local citation/reference consistency
- `scripts/generate_review_scaffold.py` — separated private Markdown scaffold
- `scripts/lint_review.py` — tone, channel, and actionability lint

Full schemas and exit codes: `references/tool_reference.md`.

## References and assets

- `references/ethical_review_practice.md` — COPE/ICMJE duties, confidentiality, AI, channels
- `references/reporting_standards.md` — current major guidelines and verified domain standards
- `references/statistical_reproducibility.md` — methods, statistics, and reproducibility review
- `references/common_issues.md` — contextual issue patterns and constructive responses
- `references/security_validation.md` — baseline remediation and local scan results
- `assets/source_ledger.csv` — authoritative sources verified 2026-07-23
- `assets/reporting_guidelines.json` — local selector catalog
- `assets/review_scaffold_template.md` — private structured draft

The source ledger is dated. Recheck live primary sources and the target venue policy for a later review, without exposing confidential manuscript text in search queries.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/peer-review/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/common_issues.md`

# Common Issues in Manuscript Review

Use this reference as a prompt for inquiry, not a defect checklist. A possible issue becomes a review comment only when it is relevant to the study and supported by a manuscript location, supplied artifact, or applicable method principle.

Do not infer misconduct, poor quality, or manuscript merit from a missing reporting item. Separate:

- **Not reported:** the manuscript does not provide enough information to assess the point.
- **Potential design or analysis problem:** the reported method may not answer the stated question.
- **Demonstrated inconsistency:** two supplied artifacts or manuscript locations conflict.
- **Integrity concern:** credible evidence should be described neutrally and routed through the journal process, normally in confidential editor notes.

## Claim–evidence alignment

Check each central claim against the design, analysis, result, and uncertainty that support it.

Common mismatches:

- Causal wording from an observational or otherwise non-identifying design
- Mechanistic conclusions supported only by association or prediction
- Conclusions based on a secondary, exploratory, or post hoc outcome without labeling
- Directionally correct claims that overstate magnitude or precision
- Population, setting, intervention, comparator, outcome, or time-horizon extrapolation
- “No effect,” “equivalent,” or “safe” conclusions from imprecise or non-significant results
- Abstract or conclusion claims that omit material harms, uncertainty, subgroup caveats, or null findings
- Novelty claims that are broader than the search or cited literature supports

Constructive response:

1. Identify the claim and its location.
2. Identify the relevant result or missing evidence.
3. Explain the alignment problem.
4. Request a bounded remedy: narrow wording, add uncertainty, clarify exploratory status, provide the prespecified analysis, or justify the inference.

Use `scripts/validate_claim_evidence.py` for a local identifier-based matrix. Its report never echoes claim text.

## Study question, design, and units

### Question–design mismatch

Check whether the population, intervention or exposure, comparator, outcomes, timing, and target quantity align from objectives through interpretation. For trials, identify the estimand when relevant. For prediction, distinguish model development from performance evaluation. For diagnostic studies, distinguish diagnostic accuracy from clinical utility.

### Experimental or observational unit

Potential issues include:

- Technical replicates treated as independent biological units
- Multiple cells, images, lesions, eyes, visits, or samples per subject analyzed as independent
- Cluster assignment analyzed at the individual level without accounting for clustering
- Paired or repeated observations analyzed as unpaired
- Site, operator, batch, family, spatial, or temporal dependence ignored

Request a clear definition of the unit, nesting, repeated measures, and analysis that reflects dependence. Do not assume a mixed model is always the correct remedy; the model must match the design and question.

### Selection, allocation, and masking

Assess, as applicable:

- Sampling frame, recruitment, eligibility, and exclusions
- Sequence generation and allocation concealment
- Prospective stopping rules
- Blinding or masking of participants, personnel, outcome assessors, and analysts
- Consequences and mitigation when masking is infeasible
- Baseline measurement timing and post-allocation exclusions

Avoid treating baseline significance tests as proof of successful randomization. Focus on chance imbalance, clinically important imbalance, prespecified adjustment, and departures from the randomized comparison.

### Confounding and causal identification

For causal claims, ask:

- What target causal contrast is intended?
- Which assumptions connect the design and analysis to that contrast?
- Were confounders selected using subject-matter reasoning rather than outcome-driven screening?
- Could adjustment introduce collider or mediator bias?
- Are time-varying treatment, censoring, immortal time, or informative observation processes relevant?
- Are negative controls, sensitivity analyses, or alternative explanations appropriate?

Do not demand a specific causal method without showing why it fits the data-generating process.

## Sample size, precision, and replication

Avoid fixed heuristics such as “n < 30 is too small” or “three replicates are sufficient.” Adequacy depends on the target effect or precision, variability, design effect, event count, model complexity, multiplicity, attrition, and decision context.

Check:

- Prospective rationale for sample size or precision
- Inputs, assumptions, software or method, and allowance for attrition or clustering
- Whether the primary outcome and analysis match the calculation
- Event and outcome information relative to model complexity
- Effective sample size after dependence, missingness, weighting, or splitting
- Independent biological replication and validation where the claim requires it
- Precision of estimates, not only nominal power

Observed or post hoc power calculated from the observed effect generally adds little beyond the estimate and its interval. Request effect estimates and uncertainty rather than “achieved power.”

## Statistical analysis

### Analysis–design alignment

Check whether the analysis respects:

- Outcome scale and distribution
- Pairing, clustering, repeated measures, censoring, and competing events
- Sampling design, weights, matching, stratification, or blocking
- Outcome hierarchy and prespecified estimand
- Non-inferiority or equivalence margins and analysis populations
- Longitudinal timing and informative dropout

Do not prescribe “parametric” or “non-parametric” methods from sample size alone.

### Assumptions and diagnostics

The relevant assumptions depend on the estimand and model. A standalone normality test is not a universal gatekeeper and can be uninformative in very small or large samples. Look for design-aware diagnostics, residual behavior, influential observations, functional form, calibration, proportional hazards where applicable, and sensitivity to reasonable alternatives.

Comments should identify the assumption at risk and why it matters. “Check normality” without specifying the modeled quantity or consequence is not actionable.

### Effect estimates and uncertainty

Flag:

- Thresholded interpretation of p-values
- P-values used as effect size, importance, or probability that a hypothesis is true
- “Significant” versus “not significant” used as evidence of a difference between effects
- Missing effect estimates, compatible intervals, denominators, or units
- Excessive precision or inconsistent rounding
- Confidence, credible, or prediction intervals described incorrectly
- Clinical or practical importance conflated with statistical compatibility

Prefer estimates, uncertainty, assumptions, and context. The ASA p-value principles and SAMPL reporting guidance are indexed in `assets/source_ledger.csv`.

### Multiplicity and analysis flexibility

Assess:

- Number and hierarchy of outcomes, time points, subgroups, contrasts, and models
- Interim looks, adaptive changes, or repeated data inspection
- Family or false-discovery control when required by the inferential aim
- Transparent labeling of confirmatory and exploratory analyses
- Consistency with protocol, registration, and statistical analysis plan
- Complete reporting rather than selective presentation of favorable analyses

Not every collection of analyses requires the same correction. Ask authors to state the inferential family and rationale instead of automatically demanding Bonferroni adjustment.

### Missing data and intercurrent events

Check:

- Amount and reasons by group and time
- Distinction between intercurrent events and missing observations when relevant
- Assumptions behind complete-case, imputation, weighting, likelihood, or other methods
- Inclusion of variables and uncertainty in multiple imputation
- Sensitivity analyses to plausible departures from assumptions
- Alignment between the target quantity, data collection, and missing-data strategy

Do not require a test that data are “missing completely at random”; missingness assumptions are not generally established by a single diagnostic test.

### Outliers, transformations, and limits

Check whether exclusions, transformations, winsorization, detection-limit handling, and influential-observation rules were prespecified or transparently justified. Request sensitivity analyses when conclusions depend materially on discretionary handling. Do not demand deletion merely because a value is extreme.

### Subgroups and heterogeneity

Look for prespecification, adequate interaction analysis, multiplicity, uncertainty, biological or clinical rationale, and consistency of direction. Within-group significance and between-group non-significance do not establish subgroup differences.

### Prediction and machine learning

Check:

- Clear target population, outcome, prediction time, and intended use
- Separation of training, tuning, and evaluation without leakage
- Representative evaluation data and transportability
- Handling of missing values and preprocessing within resampling folds
- Calibration as well as discrimination when relevant
- Uncertainty around performance and decision consequences
- Overfitting, optimism correction, and external evaluation
- Model and preprocessing availability, versioning, and human oversight
- Fairness analyses tied to intended use, not demographic metrics without context

TRIPOD+AI applies to regression and machine-learning prediction models; STARD-AI applies when diagnostic accuracy is the primary evaluation target.

## Reproducibility and transparency

Check whether another qualified researcher could understand and, where permissions allow, repeat the work:

- Protocol, registration, amendments, and analysis plan
- Data provenance, processing stages, exclusions, and versioned identifiers
- Reagents, materials, instruments, software, package versions, parameters, and seeds
- Code, environment or lock file, run order, and computational resources
- Data, code, model, and material availability statements
- Repository accession numbers and persistent identifiers
- Clear, justified restrictions for privacy, consent, security, licensing, or community governance

“Available on request” is not automatically invalid, and open release is not always ethical or lawful. Evaluate whether the access route is specific, feasible, and consistent with governance.

Do not claim to have reproduced an analysis unless it was actually run with documented inputs, environment, commands, and outputs.

## Figures, tables, and images

Assess the supplied artifact directly; do not infer manipulation from low-resolution rendering alone.

Check:

- Axes, units, denominators, scales, legends, and uncertainty definitions
- Individual data or distribution display when summary graphics conceal relevant structure
- Accessibility and redundant encoding beyond color alone
- Consistency among text, tables, figures, and supplements
- Sample sizes and exclusions for each panel or analysis
- Image acquisition, processing, normalization, scale bars, and representative-image selection
- Disclosed splicing or adjustments and availability of source images when policy requires
- Avoidance of deceptive truncation, area/volume encoding, or dual-axis implication

Possible duplication or manipulation should be documented neutrally by location and referred to the editor under the journal’s image-integrity process. Do not accuse authors of fabrication.

## Ethics, welfare, privacy, and integrity

Check what is applicable:

- Ethics committee or institutional review and identifiers
- Consent, assent, waiver, or lawful basis
- Trial registration and prospective protocol availability
- Animal welfare, humane endpoints, and relevant ARRIVE items
- Privacy, identifiability, community governance, and controlled access
- Funding, sponsor role, author conflicts, and contributor roles
- Dual-use, biosafety, environmental, or security considerations
- Prior publication, overlapping reports, and transparent secondary analyses

If a concern cannot safely be raised with authors, use the confidential editor channel. State the evidence and uncertainty; do not investigate people, contact institutions, or reveal the manuscript outside the authorized process.

## Citations and references

Check:

- Every consequential literature claim has an appropriate source
- The cited source supports the stated proposition
- Primary sources are used for methods, data, and policies when available
- Retracted or corrected work is handled appropriately
- Contradictory and relevant evidence is represented fairly
- Self-citation requests are necessary, specific, and not coercive
- Citation identifiers and reference entries are internally consistent

The local `scripts/audit_citations.py` checks Pandoc-style keys such as `[@ref-id]` against a CSV. It does not verify source existence or support and must not be described as doing so.

## Writing actionable comments

For each major or minor comment, include:

- **Location**
- **Observation**
- **Evidence or criterion**
- **Why it matters**
- **Requested action**

Prefer: “At Methods, paragraph 3, the experimental unit is unclear. Because three measurements appear to come from each participant, please define the unit and explain how within-participant dependence was handled.”

Avoid: “The statistics are bad.”

Requests for new experiments should be necessary to support an existing central claim, ethically and practically proportionate, and distinguished from optional future work. Often the appropriate remedy is to narrow a claim, add a limitation, provide missing analysis detail, or share an existing artifact.

### `references/ethical_review_practice.md`

# Ethical and Confidential Peer Review

Verified on **2026-07-23** against COPE, ICMJE, and illustrative publisher policies listed in `assets/source_ledger.csv`.

COPE identifies peer review as one of its 10 Core Practices and states that the process should be transparently described and well managed, with policies for conflicts, appeals, and disputes. The target journal’s published process controls the individual assignment.

## Role boundary

This skill supports an accountable human preparing a review draft or structured assessment. It must not:

- Claim to be the assigned reviewer, editor, journal, funder, or decision-maker
- Submit a review or contact authors, editors, institutions, or third parties without authorization
- Invent manuscript content, experiments, analyses, citations, reviewer identity, or editorial outcomes
- Present generated text as an independently completed review
- Investigate authors or search unpublished content outside the authorized process

The editor decides the editorial outcome. The reviewer provides evidence-bounded advice within the requested scope.

## Before accepting or starting

COPE’s Ethical Guidelines for Peer Reviewers and ICMJE recommendations require reviewers to consider:

### Competence

- Accept only work for which the reviewer can provide a useful assessment.
- State material subject-matter, methods, statistics, ethics, language, or domain limits.
- Ask the editor for a specialist reviewer when a central issue exceeds competence.
- Do not conceal limits by producing confident generic criticism.

### Conflicts

Disclose actual, potential, or perceived conflicts before proceeding. They can be:

- Financial or commercial
- Personal or family
- Institutional
- Recent collaboration, supervision, mentorship, or competition
- Intellectual commitments or directly competing work
- Political, religious, advocacy, or legal interests

The journal decides whether a disclosed conflict permits review. If unresolved, stop. Do not accept merely to gain access to unpublished work.

### Capacity and timeliness

Accept only if the review can be completed within the agreed time. Tell the editor promptly if scope or timing changes.

### Journal policy

Record:

- Review model and anonymity expectations
- Whether co-review is allowed and how contributors are named
- Confidentiality and retention requirements
- Required author-facing and editor-only fields
- AI and tool policy
- Citation, image-integrity, data, ethics, and reporting expectations

Journal practices differ. A policy from another publisher is an example, not authority for the target venue.

Use `scripts/validate_review_intake.py` before substantive review.

## Confidentiality and data handling

An unpublished manuscript, its supplements, review comments, and editorial correspondence are privileged confidential material.

### Default rule

Keep processing local. Do not send, paste, upload, transcribe, summarize, or expose unpublished manuscript or review text to:

- Public or external generative-AI systems
- Search engines or web research tools
- Citation, plagiarism, grammar, translation, or image services
- Unapproved collaborators
- Cloud storage or telemetry outside the authorized environment

unless the publisher or author has authorized that specific use, the target venue permits it, and applicable privacy, contract, intellectual-property, and data-governance requirements are satisfied.

Authorization to review is not automatically authorization to disclose material to a service. A tool’s promise not to train on data is not, by itself, authorization.

The bundled CLIs:

- Use only Python’s standard library
- Read bounded local JSON, CSV, or Markdown
- Make no network, model, image, subprocess, environment-variable, or dynamic-code calls
- Emit identifiers, counts, rule codes, and line numbers rather than raw manuscript or review text
- Refuse symlink inputs and implicit output overwrite

They do not make an external service safe and do not authorize its use.

### Assistance and co-review

Obtain journal permission before sharing with a trainee or colleague. Record the contributor and acknowledge the contribution to the editor as required. The invited reviewer remains responsible for confidentiality and the submitted report.

### No reuse

Do not:

- Appropriate ideas, methods, code, data, or language before publication
- Use the material for model training, benchmarking, product improvement, or unrelated research
- Build a private corpus of manuscripts or reviews
- Retain content for convenience beyond policy

### Retention and deletion

After submitting or ending the review:

1. Follow the target venue’s retention rule.
2. Delete local manuscript and review copies when required.
3. Empty derivative exports and temporary files within the authorized workspace.
4. Retain only what policy requires.
5. Record deletion or authorized retention without copying confidential content into the record.

ICMJE recommends that reviewers not retain manuscripts for personal use and delete copies after review. Local law, publisher policy, or a documented investigation may impose a different rule; follow the controlling requirement.

## AI and automated assistance

ICMJE says reviewers must follow the journal’s AI policy or request permission before using AI, maintain confidentiality, disclose use, and remain responsible for output that may be incorrect, incomplete, or biased.

For any permitted assistance:

- Identify the tool, version, purpose, and material exposed
- Use only the minimum necessary content
- Keep an accountable human in control
- Verify every statement, citation, calculation, and proposed comment
- Disclose use exactly as the journal requires
- Do not let a model create an autonomous review or editorial outcome

If permission is absent, the policy is unclear, or confidentiality cannot be assured, do not use AI on the material. Local deterministic checks may still be possible if policy and authorization permit local file processing.

Illustrative policies, not universal rules:

- [Nature Portfolio](https://www.nature.com/nature-portfolio/editorial-policies/peer-review) asks reviewers not to upload manuscripts to generative-AI tools and asks for transparent declaration when AI supported claim evaluation.
- [BMJ](https://authors.bmj.com/policies/ai-use) requires declaration of AI used for review-language assistance and prohibits placing unpublished material into publicly available tools when confidentiality cannot be guaranteed.
- [JAMA Network](https://jamanetwork.com/journals/jama/fullarticle/2807956) states that entering manuscript, abstract, or review text into a chatbot or language model violates its confidentiality agreement and requires disclosure of other AI resource use.

Always check the current target-venue policy.

## Preparing the report

COPE and ICMJE emphasize constructive, honest, polite, fair, and timely comments.

### Evidence and proportionality

- Anchor every consequential criticism to a location and reason.
- Distinguish missing reporting from demonstrated methodological error.
- Explain why the issue changes validity, interpretation, reproducibility, ethics, or reader understanding.
- Request the least burdensome adequate remedy.
- Label optional suggestions as optional.
- Do not expand the study beyond its stated scope merely to satisfy reviewer preference.
- Do not request citations to benefit the reviewer or associates.

### Tone

Critique the work, not the people. Avoid:

- Insults, sarcasm, ridicule, threats, or speculation about competence or motives
- Language policing unrelated to scientific clarity
- Bias based on identity, institution, location, seniority, language, or reputation
- Accusations when the evidence supports only a question or discrepancy
- Vague commands such as “redo the statistics” or “needs more work”

Use direct language without hostility:

> “The analysis appears to treat three observations per participant as independent. Please define the analysis unit and account for within-participant dependence, or explain why independence is justified.”

### Requests for additional work

Request a new experiment or analysis only when it is necessary and proportionate to evaluate or support a central claim. State:

- Which claim depends on it
- Why existing evidence is insufficient
- Whether a narrower claim, correction, sensitivity analysis, or limitation would be an adequate alternative

Do not turn review into an opportunity to redesign the authors’ research program.

## Separate communication channels

### Comments to authors

Include:

- Neutral summary of the work actually reviewed
- Specific strengths
- Major comments affecting validity, interpretation, reproducibility, ethics, or central claims
- Minor comments affecting clarity, consistency, figures, tables, citations, or reporting
- Review limitations and unavailable materials when useful

Do not include:

- Reviewer identity when policy requires anonymity
- Unnecessary personal information
- Editor-only conflict details
- Accusations or investigative instructions
- An editorial outcome presented as decided

### Confidential comments to editor

Use only for matters that require a separate channel:

- Reviewer conflicts or competence limits
- Permission, confidentiality, or AI-use disclosures
- Credible ethics, integrity, duplicate-publication, image, or security concerns
- Reasons an issue cannot safely be raised directly with authors
- Requests for specialist review

Ordinary scientific criticism should not appear only in the editor channel. Do not write a harsher private review that contradicts the author-facing report. The bundled scaffold keeps these channels visibly separate.

## Suspected integrity problems

Reviewers identify concerns; they do not adjudicate misconduct.

1. Preserve confidentiality.
2. Record the exact location and observable discrepancy.
3. Describe uncertainty and plausible benign explanations.
4. Notify the editor through the designated confidential route.
5. Do not contact authors, institutions, journals, funders, or media independently.
6. Do not run external similarity, face-recognition, image, or data-search services on confidential material without authorization.
7. Follow editor instructions and retain or delete evidence according to policy.

Use “Figure 3 appears similar to Figure 5 after rotation; please assess under the journal’s image-integrity process,” not “the authors fabricated the data.”

## Final ethical check

- Authorization and role are documented.
- Conflicts are resolved or disclosed.
- Competence limits and specialist needs are stated.
- Target-venue policy and review model are known.
- No unauthorized person or service received confidential material.
- AI or other assistance is permitted and disclosed.
- Author and editor channels are separate.
- Every criticism is specific, evidence-backed, proportionate, and professional.
- No invented citation, analysis, experiment, or editorial outcome appears.
- Deletion or authorized retention is planned.

### `references/reporting_standards.md`

# Reporting Guidelines and Domain Metadata Standards

Verified against primary or official sources on **2026-07-23**. The dated evidence record is `assets/source_ledger.csv`; the machine-readable selector catalog is `assets/reporting_guidelines.json`.

## What reporting guidelines do—and do not do

A reporting guideline identifies information that should be reported so readers can understand and appraise a study. It is not, by itself:

- A method for designing or conducting the study
- A risk-of-bias tool
- A statistical reanalysis
- A measure of truth, importance, novelty, or manuscript merit
- A publication recommendation

Checklist completion must never be converted automatically into a quality score. A fully reported study can have serious design problems; an incompletely reported study may be impossible to assess. Record missing information as a reporting gap, then separately assess any design, conduct, analysis, reproducibility, or ethics concern using appropriate evidence and expertise.

Use the guideline’s current statement together with its explanation and elaboration. Check applicable extensions and the target venue’s instructions. Do not copy checklist wording into a review when a specific, contextual comment is more useful.

## Selection workflow

1. Identify the **report kind**: results, protocol, abstract, or data release.
2. Identify the **study design**, not merely the topic or journal section.
3. Add cross-cutting features: AI intervention, diagnostic AI, routinely collected data, clustered design, qualitative interviews, and so on.
4. Select the current base guideline and applicable extensions.
5. Use the official checklist to record `reported`, `partly_reported`, `not_reported`, `not_applicable`, or `not_assessed`.
6. Explain `not_applicable`; do not treat it as a defect.
7. Keep reporting coverage separate from methodological appraisal.

Run:

```bash
python3 scripts/select_reporting_guidelines.py \
  assets/study_profile_template.json \
  --coverage assets/reporting_checklist_template.csv
```

The bundled catalog is a dated aid, not a live registry. Consult the [EQUATOR Network](https://www.equator-network.org/) and official guideline site when the study type is unclear or a newer extension may apply.

## Major current health-research guidelines

### Randomized trial results — CONSORT 2025

- Current statement: **CONSORT 2025**, published 14 April 2025
- Structure: 30 main checklist items and a participant flow diagram
- Supersedes: CONSORT 2010
- Use for: reports of randomized trials
- Review with: explanation and elaboration plus design/intervention extensions
- Important boundary: the statement explicitly says it is not a quality assessment instrument

Check registration, protocol and statistical analysis plan consistency, allocation, participant flow, outcomes and harms, effect estimates and uncertainty, protocol changes, data sharing, conflicts, and patient/public involvement where applicable.

Official sources: [CONSORT–SPIRIT](https://www.consort-spirit.org/) and the [CONSORT 2025 statement](https://www.bmj.com/content/389/bmj-2024-081123).

### Randomized trial protocols — SPIRIT 2025

- Current statement: **SPIRIT 2025**, published 28 April 2025
- Structure: 34 main checklist items and a participant timeline
- Supersedes: SPIRIT 2013
- Use for: randomized trial protocols

Compare the protocol with registration, statistical analysis plan, ethics records, amendments, and any completed-trial report. Explicitly stated non-applicability with rationale is not missing reporting.

Official sources: [CONSORT–SPIRIT](https://www.consort-spirit.org/) and the [SPIRIT 2025 statement](https://www.bmj.com/content/389/bmj-2024-081477).

### Systematic reviews — PRISMA 2020

- Current statement: **PRISMA 2020** (named 2020; published 2021)
- Structure: 27 main items, expanded checklist, abstract checklist, and flow diagrams
- Use for: completed systematic reviews, primarily reviews of intervention effects
- Protocols: use PRISMA-P
- Extensions: use the appropriate extension for scoping, diagnostic, individual-participant-data, network, equity, harms, or other specialized reviews

PRISMA explicitly does not assess review conduct or methodological quality. Use appropriate methods and risk-of-bias tools separately.

Official sources: [PRISMA 2020 resources](https://www.prisma-statement.org/prisma-2020) and the [primary statement](https://www.bmj.com/content/372/bmj.n71).

### Observational studies — STROBE

- Current base statement: **STROBE 2007**
- Structure: 22 main items with cohort, case-control, cross-sectional, and combined checklists
- Use for: reports of observational epidemiologic studies
- Extensions: examples include RECORD for routinely collected health data, STREGA for genetic association studies, STROBE-MR, and domain-specific extensions

STROBE helps identify whether selection, measurement, bias, confounding, missing data, sensitivity analyses, and generalizability are reported. It does not establish that those methods were adequate.

Official source: [STROBE](https://www.strobe-statement.org/).

### Diagnostic accuracy — STARD 2015

- Current base statement: **STARD 2015**
- Structure: 30 main items and a flow diagram
- Use for: studies estimating diagnostic accuracy against a reference standard

Separately assess risk of bias and applicability with a suitable tool such as the current QUADAS family when relevant. STARD’s official implementation guidance explicitly says not to use the reporting checklist as a design-quality tool.

Official source: [STARD 2015](https://www.equator-network.org/reporting-guidelines/stard/).

### AI-centered diagnostic accuracy — STARD-AI

- Current statement: **STARD-AI 2025**
- Published: 15 September 2025; an author correction was published 13 July 2026
- Structure: 40 items, including 18 new or modified items relative to STARD 2015
- Use for: AI-centered diagnostic accuracy studies, including suitable diagnostic classification tasks

Check dataset practices, index-test specification, evaluation, algorithmic bias and fairness, applicability, and generalizability. If the primary aim is development or evaluation of a multivariable prediction model, use TRIPOD+AI instead.

Official source: [STARD-AI](https://www.nature.com/articles/s41591-025-03953-8).

### Clinical prediction models — TRIPOD+AI

- Current statement: **TRIPOD+AI 2024**
- Structure: 27 main items plus a 13-item abstract checklist
- Replaces: TRIPOD 2015
- Use for: development, evaluation, or updating of diagnostic or prognostic prediction models using regression or machine-learning methods

Do not select it solely because software called “AI” appears in a paper. Select it when the study’s primary object is a prediction model. Relevant extensions include TRIPOD-Cluster, TRIPOD-SRMA, and TRIPOD-LLM.

Official sources: [TRIPOD](https://www.tripod-statement.org/) and the [TRIPOD+AI statement](https://www.bmj.com/content/385/bmj-2023-078378).

### Case reports — CARE

- Current base checklist: **CARE 2013**
- Explanation and elaboration/manual: 2017
- Structure: 13 main items
- Use for: clinical case reports

Check timeline, diagnostic reasoning, interventions, outcomes, adverse events, patient perspective where available, informed consent, privacy, and venue requirements.

Official source: [CARE checklist](https://www.care-statement.org/checklist).

### In vivo animal research — ARRIVE 2.0

- Current statement: **ARRIVE 2.0**, published July 2020
- Structure: Essential 10 plus 11 Recommended Set items
- Use for: research involving live animals across bioscience disciplines

The Essential 10 are a minimum reporting set, not a ranking. Review study design, sample size, inclusion/exclusion, randomization, blinding, outcome measures, statistics, animal details, procedures, and results; also assess ethics, welfare, humane endpoints, adverse events, protocol registration, data access, and interests.

Official source: [ARRIVE 2.0](https://arriveguidelines.org/arrive-guidelines).

### Quality improvement — SQUIRE 2.0

- Current statement: **SQUIRE 2.0**, published 2015
- Structure: 18 main items
- Use for: system-level work intended to improve healthcare quality, safety, value, or equity where methods seek to relate outcomes to the intervention

SQUIRE states that every item should be considered, but not every element belongs in every manuscript. Attend to local context, rationale, intervention evolution, measures, analysis, ethics, unintended consequences, and sustainability.

Official source: [SQUIRE 2.0](https://www.squire-statement.org/index.cfm?fuseaction=page.viewPage&pageID=471&nodeID=1).

### Health economic evaluations — CHEERS 2022

- Current statement: **CHEERS 2022**
- Structure: 28 main items
- Replaces: CHEERS 2013
- Use for: economic evaluations of health interventions

Assess perspective, comparators, time horizon, discounting, outcome and cost measurement, model assumptions, heterogeneity, distributional effects where applicable, uncertainty, engagement, funding, and conflicts. Use a separate critical-appraisal framework for methodological quality.

Official source: [ISPOR CHEERS](https://www.ispor.org/heor-resources/good-practices/cheers).

### Qualitative research — SRQR and COREQ

- **SRQR**: broad qualitative research reporting standard
- **COREQ**: 32-item checklist specifically for interviews and focus groups

Select by methods, not by the presence of quotations. Review researcher reflexivity, sampling, context, data collection, analytic process, credibility, participant voice, ethics, and limitations without imposing one epistemology on all qualitative traditions.

Official registry records: [SRQR](https://www.equator-network.org/reporting-guidelines/srqr) and [COREQ](https://www.equator-network.org/reporting-guidelines/coreq/).

## AI extensions and overlap

Use the guideline that matches the study’s primary design and claim:

- Randomized trial of an AI intervention: CONSORT 2025 plus current CONSORT-AI guidance
- Protocol for such a trial: SPIRIT 2025 plus current SPIRIT-AI guidance
- AI diagnostic accuracy: STARD-AI
- Prediction model development or performance evaluation: TRIPOD+AI
- Biomedical large-language-model prediction or evaluation: check TRIPOD-LLM and design-specific guidance
- Medical imaging AI: consider current modality guidance in addition to the design-specific base

Multiple guidelines can apply, but do not create redundant demands. State which base and extension address each concern.

## Domain metadata standards: verified legacy status

These standards describe minimum experiment or repository metadata. They complement, rather than replace, study-design reporting and methodological appraisal.

### MIAME and MINSEQE

**Retain with qualification.** NCBI GEO’s page was last modified 8 July 2026 and still states that GEO submission procedures implement:

- MIAME for microarray experiments
- MINSEQE for next-generation/high-throughput sequencing experiments

ArrayExpress/Annotare also continues to reference these standards. Verify the current repository’s fields, file formats, raw/processed data expectations, and accession requirements; do not rely on an old static project page alone.

Official implementation source: [GEO and MIAME/MINSEQE](https://www.ncbi.nlm.nih.gov/geo/info/MIAME.html).

### MIAPE

**Retain as a modular current-qualified standard.** The HUPO Proteomics Standards Initiative lists released components with separate versions, including mass spectrometry, mass-spectrometry informatics, quantification, gel electrophoresis, gel informatics, chromatography, and capillary electrophoresis.

Select only components relevant to the actual workflow and verify current repository expectations. Do not present “MIAPE” as one unversioned universal checklist.

Official source: [HUPO-PSI MIAPE](https://www.psidev.info/miape).

### MIFlowCyt

**Retain with qualification.** ISAC continues to identify MIFlowCyt 1.0 as an ISAC recommendation for experiment overview, samples, instrumentation, and data analysis. Also check current FCS, gating, panel, controls, and FlowRepository requirements.

Official source: [ISAC MIFlowCyt](https://isac-net.org/miflowcyt-2/).

### MIAPPE

**Use MIAPPE 1.2**, released October 2024, for plant phenotyping metadata. It remains compatible with 1.1; version 2.0 was still in early development on the verification date.

Official source: [MIAPPE releases](https://www.miappe.org/releases).

### MIGS and MIMS

**Do not present standalone MIGS/MIMS as the current umbrella.** The Genomic Standards Consortium now organizes these legacy checklists within **MIxS** (Minimum Information about any Sequence), alongside newer checklists and environmental packages. Select the current MIxS release and applicable checklist/package.

Official source: [GSC standards](https://www.gensc.org/pages/standards-intro.html).

## Other study types

The EQUATOR database contains hundreds of guidelines. Common additional choices include:

- Protocols: design-specific protocol guidance
- Routinely collected health data: RECORD
- Clinical practice guidelines: RIGHT and AGREE reporting guidance
- Surveys: design-appropriate survey reporting guidance
- Implementation studies: current implementation-reporting guidance
- Mixed methods: current mixed-methods guidance
- Laboratory and omics studies: study-design reporting plus current repository metadata standards

If no suitable guideline exists, say so. Do not force the nearest checklist or invent one.

## Coverage language for reviews

Use:

> “Item 12 is not reported clearly enough to determine the analysis population. Please identify the included participants and reconcile this denominator with Figure 1.”

Avoid:

> “The manuscript scores 18/30 on CONSORT and is therefore low quality.”

Report counts or item identifiers only as navigation aids. The local selector deliberately emits no percentage or merit score.

### `references/security_validation.md`

# Security Validation Record

Validation date: **2026-07-23** (local project date).

## Baseline

The repository `SECURITY.md` entry recorded **10 findings** with maximum severity **CRITICAL**:

- Cross-file environment-variable and network exfiltration
- A multi-file collection/transmission chain
- Environment harvesting in both schematic scripts
- API-key transmission to an external model service
- Full environment propagation to a subprocess
- Repeated costly model/image operations
- Mandatory external schematic/cross-skill behavior

The affected files were:

- Deleted: scripts/generate_schematic.py
- Deleted: scripts/generate_schematic_ai.py
- The former `SKILL.md`

## Remediation

- Deleted both external schematic scripts.
- Removed credentials, environment access, `.env` loading, subprocess chaining, network requests, model calls, image generation, mandatory figures, and cross-skill calls.
- Replaced them with bounded deterministic local JSON/CSV/Markdown validators and generators.
- Added strict schemas, duplicate-key/header detection, size/row/cell limits, symlink rejection, private atomic output, and no implicit overwrite.
- Added report minimization: IDs, counts, rule codes, and line numbers instead of manuscript/review prose.
- Added AST tests that reject network libraries, executable serialization, dynamic code execution, and environment credential access.
- Added confidentiality, no-reuse, authorization, conflict, competence, AI-policy, disclosure, and deletion/retention gates.

## Validation results

- Agent Skills reference validator: **PASS**
- Dependency-free CLI help checks: **PASS**
- Synthetic standard-library tests: **26 passed**
- Explicit AST parse with bytecode disabled: **8 scripts parsed**
- Bytecode artifacts: **0**
- IDE lints: **0**
- Documented local-path link test: **PASS**
- Markdown link check: **PASS** (access-controlled HTTP 403 treated as reachable)
- Direct behavioral security scan: **SAFE, 0 findings**
- Pull-request gate with `--fail-on HIGH`: **PASS**
  - CRITICAL: 0
  - HIGH: 0
  - LOW: 3

## Residual LOW findings

The final LLM-assisted pull-request scan reported:

1. **Missing `allowed-tools` declaration** — informational. This field is optional under the Agent Skills specification. The compatibility and body explicitly constrain bundled tools to local standard-library processing with no network, model, image, credential, or environment access.
2. **Broad description** — accepted as a scoped capability description. The mandatory authorization and venue-policy gate applies before confidential content is read, and the body limits all functions to peer-review assessment.
3. **Bounded CSV/JSON processing** — defensive observation with “no action required” in the scanner output. Inputs are already limited to 4 MiB, 5,000 CSV rows, 12,000 characters per cell, and finite list sizes; tests cover oversize rejection.

None of the LOW findings permits data transmission or credential access. No CRITICAL or HIGH issue remains.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests/peer-review -p "test_*.py" -v

uv run skills-ref validate skills/peer-review

uv run skill-scanner scan skills/peer-review --use-behavioral

uv run python scan_pr_skills.py \
  --fail-on HIGH \
  --output /tmp/peer-review-pr-scan.md \
  skills/peer-review
```

The repository-level `SECURITY.md` was intentionally not edited in this scoped refresh; its generated snapshot will update through the repository’s normal scan process.

### `references/statistical_reproducibility.md`

# Statistical, Methods, and Reproducibility Review

This guide supports structured questions; it does not replace a statistician, methodologist, domain expert, or independent reanalysis. Sources verified on **2026-07-23** are recorded in `assets/source_ledger.csv`.

## Evidence hierarchy for the review

Use, in order:

1. The stated research question and target population
2. Protocol, registration, analysis plan, and amendments
3. Reported design and data-generating process
4. Methods, code, tables, figures, supplements, and repository records
5. Applicable primary method or regulatory guidance
6. Current reporting guidance
7. Target venue policy

Do not reject a method merely because another method is more familiar. Explain the estimand, assumption, error, or interpretation at stake.

## Core review sequence

### 1. Define what is being estimated

Write down:

- Unit of inference
- Population
- Intervention, exposure, test, or predictors
- Comparator or reference condition
- Outcome and time horizon
- Target effect, association, accuracy, or predictive performance
- Intercurrent events, censoring, and missing observations where relevant

Then trace whether design, data collection, analysis, result, and claim target the same quantity.

For applicable clinical trials, ICH E9(R1) provides a framework for estimands and sensitivity analyses. It is not a universal rule for every study.

### 2. Reconstruct the design

Identify:

- Prospective, retrospective, cross-sectional, longitudinal, experimental, or observational structure
- Recruitment or sampling frame
- Experimental/observational unit
- Pairing, nesting, clustering, repeated measures, sites, batches, and time
- Allocation, concealment, blinding, matching, or weighting
- Primary and secondary outcomes
- Prespecified versus exploratory analyses

If the design cannot be reconstructed, first request missing reporting. Do not label the design invalid solely because details are absent.

### 3. Trace every denominator

Reconcile:

- Eligible, enrolled, assigned, treated/exposed, followed, measured, and analyzed units
- Outcome-specific denominators
- Exclusions before and after allocation or measurement
- Missing values and reasons
- Complete-case, imputed, weighted, or model-based analysis populations
- Figure, table, abstract, text, and supplement totals

Report the exact mismatch and locations; do not infer why counts differ.

### 4. Assess analysis–design alignment

Ask whether the method accounts for:

- Outcome scale and distribution
- Pairing and repeated measures
- Clustering and multilevel structure
- Unequal follow-up, censoring, or competing events
- Sampling weights or matched designs
- Baseline adjustment and prespecified covariates
- Multiplicity and outcome hierarchy
- Model tuning and validation
- Missingness assumptions

The name of a statistical test is not enough. The report should state inputs, model form, uncertainty method, software/version, and relevant diagnostics.

### 5. Assess estimates and interpretation

Prefer:

- Effect or performance estimates with units
- Compatible uncertainty intervals
- Absolute as well as relative quantities when decision-relevant
- Exact denominators and analysis sets
- Assumption and sensitivity context
- Clinical, biological, policy, or practical relevance distinct from statistical compatibility

The ASA’s six p-value principles include:

- A p-value is about incompatibility with a specified model, not the probability a hypothesis is true.
- Threshold crossing alone should not determine scientific conclusions.
- Transparent reporting of all relevant analyses is required.
- Statistical significance does not measure effect size or importance.
- A p-value alone is not a good measure of evidence.

SAMPL provides concise biomedical statistical reporting guidance. Apply it as reporting guidance, not a universal analysis recipe.

## Topic-specific checks

### Sample size and precision

Look for:

- Prospective calculation or precision rationale
- Target effect or interval width
- Variance, event rate, prevalence, or accuracy assumptions
- Type I error, power, sidedness, and multiplicity when applicable
- Design effect, clustering, attrition, noncompliance, and missingness
- Model complexity and effective sample size
- Simulation details for complex designs

Do not request observed/post hoc power as a remedy for an imprecise result. Examine the estimate and uncertainty.

### Randomized trials

Check:

- Allocation sequence and concealment
- Prespecified estimand and analysis population
- Protocol/registry/outcome consistency
- Baseline adjustment and stratification factors
- Intercurrent events, adherence, treatment switching, and missing data
- Harms and unintended effects
- Sensitivity and supplementary analyses
- Non-inferiority/equivalence margin and interpretation if relevant

Use CONSORT 2025 and SPIRIT 2025 for reporting. Use ICH E9/E9(R1) only when its scope and decision context fit.

### Observational causal analyses

Check:

- Causal question and target contrast
- Time zero, eligibility, treatment/exposure assignment, follow-up, and outcome timing
- Confounder rationale and measurement timing
- Positivity/overlap
- Exchangeability and consistency assumptions
- Missingness, censoring, selection, and measurement error
- Model specification and balance diagnostics
- Sensitivity to unmeasured confounding or alternative specifications

Avoid judging causal identification from adjusted versus unadjusted p-values.

### Diagnostic accuracy

Check:

- Intended use, setting, and participant spectrum
- Index test and reference standard
- Threshold prespecification
- Blinding and timing
- Indeterminate/missing results
- Verification and incorporation bias
- Two-by-two denominators and uncertainty
- External applicability

STARD/STARD-AI describe reporting; use an appropriate risk-of-bias framework separately.

### Prediction models

Check:

- Intended use, prediction time, outcome, and target population
- Data source and participant flow
- Predictor availability at intended use
- Missing-data and preprocessing leakage
- Sample size relative to outcome information and complexity
- Internal validation and optimism correction
- Independent evaluation and dataset shift
- Calibration, discrimination, decision utility, and uncertainty
- Hyperparameter tuning separated from evaluation
- Reproducible model specification and preprocessing
- Subgroup performance tied to plausible use and harms

TRIPOD+AI replaces TRIPOD 2015 for regression and machine-learning prediction model reporting. STARD-AI is more appropriate when diagnostic accuracy of an index test is the primary aim.

### Systematic reviews and meta-analyses

Check:

- Protocol and registration
- Eligibility criteria and information sources
- Reproducible search dates and strategies
- Duplicate screening/extraction processes or justified alternatives
- Risk-of-bias assessment
- Effect measure and synthesis model
- Heterogeneity and prediction intervals when appropriate
- Dependence among estimates
- Small-study and reporting biases
- Certainty assessment, if claimed
- Transparent deviations and unavailable data

PRISMA 2020 assesses reporting. Do not substitute PRISMA coverage for review-conduct appraisal.

### Clustered and longitudinal data

Check:

- Level of assignment, measurement, and inference
- Within-cluster/subject correlation
- Number and distribution of clusters
- Small-cluster corrections where needed
- Time structure, nonlinear change, and irregular measurement
- Informative visit, dropout, or censoring processes
- Cluster-level versus individual-level covariates

Repeated observations do not increase independent sample size one-for-one.

### Multiplicity

Identify the inferential family before recommending adjustment:

- Multiple primary outcomes
- Multiple intervention arms or contrasts
- Repeated time points
- Subgroups and interactions
- Interim analyses
- High-dimensional features
- Model selection

Possible responses include hierarchical testing, family-wise control, false-discovery control, multilevel modeling, transparent exploratory labeling, or emphasis on estimates and uncertainty. The remedy depends on the claim and decision rule.

### Missing data

Check:

- Missingness by group, variable, outcome, and time
- Reasons and relation to intercurrent events
- Information used by imputation or weighting
- Number of imputations and pooling when applicable
- Compatibility of imputation and analysis models
- Uncertainty propagation
- Sensitivity to plausible departures from assumptions

Avoid demanding one preferred technique without considering the estimand and missingness process.

## Reproducibility review

### Materials and provenance

Check:

- Stable identifiers for datasets, samples, models, protocols, and materials
- Raw-to-processed provenance
- Exclusion and transformation records
- Versioned analysis inputs and outputs
- Repository accession numbers
- Data dictionary, units, and coding
- Domain metadata standard where applicable

Legacy domain standards and their current status are summarized in `references/reporting_standards.md`.

### Code and computational environment

Check:

- Executable code for central analyses when sharing is permitted
- Dependency versions or lock/environment file
- Operating-system or hardware requirements that affect results
- Random seeds and nondeterminism
- Parameter, configuration, and model checkpoints
- Run order and instructions
- Tests or validation of custom code
- License and access restrictions

Code availability does not prove that the code generated the reported result. Provenance and a reproducible run record are separate evidence.

### Data and access

Open sharing may be limited by consent, privacy, indigenous/community governance, security, contracts, or licensing. A useful statement should identify:

- What exists
- Where it is held
- Who can request access
- Criteria and process
- Expected timeline
- Restrictions and rationale
- Whether code or synthetic/aggregate alternatives are available

Do not request disclosure that would violate ethics, law, consent, or governance.

### Independent reproduction

Claim independent reproduction only if the reviewer actually:

1. Obtained authorized inputs.
2. Recorded versions and environment.
3. Ran documented commands.
4. Preserved content hashes or equivalent provenance.
5. Compared prespecified outputs.
6. Recorded deviations and failures.

A static consistency audit is not reproduction.

## When to request specialist review

Escalate when a central conclusion depends on methods outside competence, including:

- Complex adaptive, Bayesian, causal, survival, multilevel, spatial, or longitudinal methods
- High-dimensional omics or multiple-testing procedures
- Diagnostic, prediction, or AI evaluation
- Survey weighting or complex sampling
- Economic modeling
- Meta-analysis with dependent effects or network structure
- Unfamiliar qualitative or mixed-methods methodology
- Image forensics, biosecurity, privacy, or domain-specific ethics

Say what expertise is needed and which claim depends on it. Do not mask uncertainty with an automated score.

## Using the local checklist

Copy `assets/statistical_reproducibility_template.json`, record evidence locations without pasting manuscript prose into report fields, and run:

```bash
python3 scripts/audit_statistics_reproducibility.py local-checklist.json
```

Statuses:

- `verified_present`
- `partly_documented`
- `missing`
- `not_assessed`
- `not_applicable` with rationale

The tool reports item IDs and counts. It does not calculate merit, rerun analyses, or certify reproducibility.

### `references/tool_reference.md`

# Local Tool Contracts

All bundled tools are deterministic Python 3.11+ standard-library CLIs. They make no network, model, image, subprocess, environment-variable, dynamic-code, or pickle calls.

## Shared safety behavior

- Inputs: local JSON, CSV, or Markdown only
- Maximum input size: 4 MiB
- Maximum CSV rows: 5,000
- UTF-8 only; NUL bytes rejected
- Symlink inputs and outputs rejected
- Duplicate JSON keys and CSV headers rejected
- Unknown schema fields rejected by JSON validators
- Existing outputs are not replaced unless `--force` is explicit
- JSON and Markdown outputs are written atomically with owner-only permissions where supported
- Reports contain IDs, counts, rule codes, and line numbers—not raw manuscript, review, claim, title, author, or reference prose

Exit codes:

- `0`: structurally valid or completed
- `1`: a validly parsed audit is blocked or has rule errors
- `2`: malformed input, unsafe path, unsupported field, or CLI validation error

Run tools from the skill directory or use absolute script paths.

## Intake validator

```bash
python3 scripts/validate_review_intake.py \
  assets/review_intake_template.json
```

Purpose:

- Confirm documented authorization and human accountability
- Record role, competence areas and limits, conflicts, target-venue policy, and review model
- Enforce local-only processing, no external service use, no data reuse, and a deletion/retention record
- Gate approved AI assistance on venue policy, permission, and disclosure

The bundled template is intentionally blocked until the human completes the controls.

Top-level JSON fields:

- `schema_version`: `2.0`
- `review_id`: safe local identifier, not a manuscript title
- `material`: status and sensitive-data flag
- `authorization`: basis and documented permissions
- `reviewer`: capacity, accountability, competence, and conflicts
- `venue_policy`: checked status, review model, confidential-note channel
- `ai_use`: policy, plan, permission, disclosure
- `handling`: local-only, external-service, reuse, retention controls
- `scope`: manuscript type, requested focus, limits, specialist needs

The report validates declarations, not their truth.

## Reporting-guideline selector and coverage audit

Selection only:

```bash
python3 scripts/select_reporting_guidelines.py \
  assets/study_profile_template.json
```

Selection plus coverage:

```bash
python3 scripts/select_reporting_guidelines.py \
  assets/study_profile_template.json \
  --coverage assets/reporting_checklist_template.csv
```

Profile fields:

- `schema_version`: `2.0`
- `profile_id`
- `study_types`: identifiers such as `randomized_trial`
- `report_kind`: `results`, `protocol`, `abstract`, or `data_release`
- `features`: for example `ai_based`, `ai_intervention`, `large_language_model`
- `domains`: for example `health`, `genomics`, `proteomics`

Coverage columns:

- `guideline_id`
- `item_id`: aggregate main item number for guidelines with a known main count
- `status`: `reported`, `partly_reported`, `not_reported`, `not_applicable`, `not_assessed`
- `location`: required for reported or partly reported items
- `rationale`: required for not-applicable items

The catalog is `assets/reporting_guidelines.json`, verified on the date embedded in that file. It does not fetch live updates. The output deliberately has no percentage or quality score.

## Claim–evidence matrix validator

```bash
python3 scripts/validate_claim_evidence.py \
  assets/claim_evidence_matrix_template.csv
```

Columns:

- `claim_id`
- `location`
- `claim_type`
- `claim_summary`: input-only; never echoed
- `evidence_ids`: semicolon-delimited local IDs
- `support_level`: `supported`, `partly_supported`, `unsupported`, `not_assessed`
- `alignment_issue`: direction, magnitude, population, outcome, timepoint, causal language, scope, uncertainty, selective reporting, other, or none
- `limitation`: input-only; never echoed
- `requested_action`: input-only; never echoed

Rules include:

- Supported claims need evidence IDs and no declared alignment issue.
- Partly supported claims need evidence, an issue code, and a requested action.
- Unsupported claims need an issue code.
- Claim IDs must be unique.

The tool does not determine whether evidence is true or sufficient.

## Statistics and reproducibility checklist

```bash
python3 scripts/audit_statistics_reproducibility.py \
  assets/statistical_reproducibility_template.json
```

The JSON contains:

- Checklist and study-design IDs
- Specialist-review declaration
- Core item records with category, applicability, status, evidence locations, note, and requested action

Core areas:

- Question/estimand alignment
- Unit, independence, sample size, allocation, and blinding
- Inclusion/exclusion, missing data, and data handling
- Prespecification, method alignment, assumptions, multiplicity, and dependence
- Effect estimates, uncertainty, denominators, outcomes, and harms
- Data/material access, code/environment, and provenance
- Ethics/governance, claim interpretation, and selective reporting

The tool requires the core item IDs but permits additional safe IDs. It reports gaps and specialist-review triggers without a score.

## Citation/reference consistency audit

The Markdown must use Pandoc-style citation keys:

```markdown
The synthetic method is described elsewhere [@ref-synthetic-2026].
Several sources may be grouped [@ref-one; @ref-two].
```

Run:

```bash
python3 scripts/audit_citations.py \
  local-manuscript.md \
  assets/citation_references_template.csv
```

Reference CSV columns:

- `reference_id`
- `title`
- `authors`
- `year`
- `doi`
- `url`
- `verification_status`: `verified_primary`, `verified_secondary`, or `not_verified`

The audit finds:

- Citation keys without reference rows
- Reference rows not cited
- Cited references not marked verified
- References without DOI or URL
- Malformed citation syntax

It validates DOI/URL shape only. It does not resolve identifiers, search the web, verify existence, or determine whether a reference supports a claim.

## Review scaffold generator

The intake must pass first:

```bash
python3 scripts/generate_review_scaffold.py \
  completed-intake.json \
  -o private-review.md
```

The generator:

- Reads `assets/review_scaffold_template.md`
- Interpolates only safe intake identifiers
- Never reads or embeds manuscript text
- Separates comments to authors from confidential editor notes
- Provides structured major/minor comment fields
- Includes human-accountability and no-editorial-decision warnings

It refuses unresolved intake controls and implicit overwrite.

## Tone and actionability lint

```bash
python3 scripts/lint_review.py private-review.md
```

Required headings:

- `# Comments to authors`
- `# Confidential comments to editor`

Structured comment headings:

- `### Major comment M1`
- `### Minor comment m1`

Each comment must contain non-placeholder values for:

- `Location`
- `Observation`
- `Evidence or criterion`
- `Why it matters`
- `Requested action`

The linter flags:

- Missing or reversed author/editor channels
- Editor-only markers in the author channel
- Unresolved scaffold placeholders
- A narrow lexicon of abusive or personal language
- Role impersonation and editorial-decision phrases
- Missing actionability fields
- Claims of executed analysis that need provenance

Lexical lint has false positives and false negatives. Human review remains required.

## Private output examples

All JSON-reporting CLIs accept:

```bash
-o local-report.json
```

To replace an existing output deliberately:

```bash
--force
```

Do not place outputs in a synced or shared directory unless the authorization and venue policy permit it. Delete or retain inputs, drafts, and reports according to the documented review policy.

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared, dependency-free safety helpers for local peer-review CLIs."""

from __future__ import annotations

import csv
import json
import os
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Iterable

MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_ROWS = 5_000
MAX_CELL_CHARS = 12_000
MAX_TEXT_CHARS = 50_000
MAX_LIST_ITEMS = 2_000

IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,95}$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)


class ValidationError(ValueError):
    """A deterministic, user-correctable validation failure."""


def _duplicate_safe_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"JSON object contains duplicate key: {key}")
        result[key] = value
    return result


def safe_input_path(raw_path: str | Path, suffixes: Iterable[str]) -> Path:
    """Resolve a bounded regular local file and reject symlink inputs."""
    path = Path(raw_path).expanduser()
    if path.is_symlink():
        raise ValidationError(f"symlink inputs are not allowed: {path}")
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValidationError(f"input file does not exist: {path}") from exc
    if not resolved.is_file():
        raise ValidationError(f"input path is not a regular file: {resolved}")
    allowed = {suffix.lower() for suffix in suffixes}
    if resolved.suffix.lower() not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValidationError(f"expected one of [{choices}]: {resolved}")
    size = resolved.stat().st_size
    if size > MAX_INPUT_BYTES:
        raise ValidationError(
            f"input exceeds {MAX_INPUT_BYTES} bytes: {resolved} ({size} bytes)"
        )
    return resolved


def safe_output_path(
    raw_path: str | Path, suffix: str, *, force: bool = False
) -> Path:
    """Resolve an output in an existing directory without implicit overwrite."""
    path = Path(raw_path).expanduser()
    if path.suffix.lower() != suffix.lower():
        raise ValidationError(f"output must use {suffix}: {path}")
    try:
        parent = path.parent.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValidationError(f"output parent does not exist: {path.parent}") from exc
    if not parent.is_dir():
        raise ValidationError(f"output parent is not a directory: {parent}")
    resolved = parent / path.name
    if resolved.is_symlink():
        raise ValidationError(f"symlink outputs are not allowed: {resolved}")
    if resolved.exists():
        if not resolved.is_file():
            raise ValidationError(f"output is not a regular file: {resolved}")
        if not force:
            raise ValidationError(
                f"output already exists; pass --force to replace it: {resolved}"
            )
    return resolved


def read_json(raw_path: str | Path) -> Any:
    """Read strict UTF-8 JSON with duplicate-key detection."""
    path = safe_input_path(raw_path, {".json"})
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"JSON must be UTF-8: {path}") from exc
    if "\x00" in text:
        raise ValidationError(f"JSON contains a NUL byte: {path}")
    try:
        return json.loads(text, object_pairs_hook=_duplicate_safe_object)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def read_markdown(raw_path: str | Path) -> str:
    """Read one bounded UTF-8 Markdown file."""
    path = safe_input_path(raw_path, {".md", ".markdown"})
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"Markdown must be UTF-8: {path}") from exc
    if "\x00" in text:
        raise ValidationError(f"Markdown contains a NUL byte: {path}")
    return text


def read_csv_records(
    raw_path: str | Path,
    *,
    required_fields: Iterable[str],
    allowed_fields: Iterable[str] | None = None,
    max_rows: int = MAX_ROWS,
) -> list[dict[str, str]]:
    """Read strict UTF-8 CSV records with bounded, unique cells and headers."""
    path = safe_input_path(raw_path, {".csv"})
    required = tuple(required_fields)
    allowed = set(allowed_fields) if allowed_fields is not None else None
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames
            if not headers:
                raise ValidationError(f"CSV has no header: {path}")
            normalized = [header.strip() for header in headers]
            if any(not header for header in normalized):
                raise ValidationError("CSV headers must not be blank")
            if len(normalized) != len(set(normalized)):
                raise ValidationError("CSV headers must be unique")
            missing = sorted(set(required) - set(normalized))
            if missing:
                raise ValidationError(
                    f"CSV is missing required columns: {', '.join(missing)}"
                )
            if allowed is not None:
                unknown = sorted(set(normalized) - allowed)
                if unknown:
                    raise ValidationError(
                        f"CSV contains unknown columns: {', '.join(unknown)}"
                    )
            reader.fieldnames = normalized
            records: list[dict[str, str]] = []
            for line_number, row in enumerate(reader, start=2):
                if line_number - 1 > max_rows:
                    raise ValidationError(f"CSV exceeds {max_rows} data rows")
                if None in row:
                    raise ValidationError(
                        f"row {line_number} has more cells than the header"
                    )
                cleaned: dict[str, str] = {}
                for key, value in row.items():
                    cell = "" if value is None else value.strip()
                    if "\x00" in cell:
                        raise ValidationError(
                            f"row {line_number}, column {key} contains a NUL byte"
                        )
                    if len(cell) > MAX_CELL_CHARS:
                        raise ValidationError(
                            f"row {line_number}, column {key} exceeds "
                            f"{MAX_CELL_CHARS} characters"
                        )
                    cleaned[key] = cell
                if any(cleaned.values()):
                    records.append(cleaned)
    except UnicodeDecodeError as exc:
        raise ValidationError(f"CSV must be UTF-8: {path}") from exc
    except csv.Error as exc:
        raise ValidationError(f"invalid CSV: {exc}") from exc
    if not records:
        raise ValidationError("CSV must contain at least one data row")
    return records


def require_object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{context} must be a JSON object")
    return value


def require_exact_keys(
    value: dict[str, Any],
    *,
    required: Iterable[str],
    optional: Iterable[str] = (),
    context: str,
) -> None:
    required_set = set(required)
    allowed = required_set | set(optional)
    missing = sorted(required_set - set(value))
    unknown = sorted(set(value) - allowed)
    if missing:
        raise ValidationError(f"{context} is missing fields: {', '.join(missing)}")
    if unknown:
        raise ValidationError(f"{context} has unknown fields: {', '.join(unknown)}")


def require_list(
    value: Any,
    context: str,
    *,
    minimum: int = 0,
    maximum: int = MAX_LIST_ITEMS,
) -> list[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{context} must be a JSON array")
    if not minimum <= len(value) <= maximum:
        raise ValidationError(
            f"{context} must contain between {minimum} and {maximum} items"
        )
    return value


def require_text(
    value: Any,
    context: str,
    *,
    allow_empty: bool = False,
    minimum: int = 1,
    maximum: int = MAX_TEXT_CHARS,
) -> str:
    if not isinstance(value, str):
        raise ValidationError(f"{context} must be a string")
    text = value.strip()
    if not allow_empty and not text:
        raise ValidationError(f"{context} must not be empty")
    if text and len(text) < minimum:
        raise ValidationError(f"{context} must contain at least {minimum} characters")
    if len(text) > maximum:
        raise ValidationError(f"{context} exceeds {maximum} characters")
    if "\x00" in text:
        raise ValidationError(f"{context} contains a NUL byte")
    return text


def require_bool(value: Any, context: str) -> bool:
    if type(value) is not bool:
        raise ValidationError(f"{context} must be true or false")
    return value


def require_enum(value: Any, choices: Iterable[str], context: str) -> str:
    text = require_text(value, context, maximum=96)
    allowed = set(choices)
    if text not in allowed:
        raise ValidationError(
            f"{context} must be one of: {', '.join(sorted(allowed))}"
        )
    return text


def require_identifier(value: Any, context: str) -> str:
    identifier = require_text(value, context, maximum=96)
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValidationError(f"{context} has an invalid identifier format")
    return identifier


def require_unique(values: Iterable[str], context: str) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    if duplicates:
        raise ValidationError(
            f"{context} contains duplicate IDs: {', '.join(sorted(duplicates))}"
        )


def require_text_list(
    value: Any,
    context: str,
    *,
    minimum: int = 0,
    maximum: int = 100,
) -> list[str]:
    items = require_list(value, context, minimum=minimum, maximum=maximum)
    return [
        require_text(item, f"{context}[{index}]", maximum=500)
        for index, item in enumerate(items)
    ]


def require_identifier_list(
    value: Any,
    context: str,
    *,
    minimum: int = 0,
    maximum: int = 100,
) -> list[str]:
    items = require_list(value, context, minimum=minimum, maximum=maximum)
    parsed = [
        require_identifier(item, f"{context}[{index}]")
        for index, item in enumerate(items)
    ]
    require_unique(parsed, context)
    return parsed


def split_identifiers(
    value: Any, context: str, *, allow_empty: bool = False
) -> list[str]:
    text = require_text(value, context, allow_empty=allow_empty, maximum=MAX_CELL_CHARS)
    if not text:
        return []
    parts = [part.strip() for part in text.split(";")]
    if any(not part for part in parts):
        raise ValidationError(f"{context} contains an empty identifier")
    parsed = [require_identifier(part, context) for part in parts]
    require_unique(parsed, context)
    return parsed


def require_iso_date(value: Any, context: str) -> str:
    text = require_text(value, context, maximum=10)
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationError(f"{context} must be an ISO date (YYYY-MM-DD)") from exc
    return text


def require_url(value: Any, context: str, *, allow_empty: bool = False) -> str:
    text = require_text(value, context, allow_empty=allow_empty, maximum=2_000)
    if text and not URL_RE.fullmatch(text):
        raise ValidationError(f"{context} must be an http or https URL")
    return text


def require_doi(value: Any, context: str, *, allow_empty: bool = False) -> str:
    text = require_text(value, context, allow_empty=allow_empty, maximum=500)
    if text and not DOI_RE.fullmatch(text):
        raise ValidationError(f"{context} has an invalid DOI format")
    return text


def atomic_write_text(
    destination: Path, text: str, *, mode: int = 0o600
) -> Path:
    """Atomically write private local text to a validated destination."""
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary_name = handle.name
        os.chmod(temporary_name, mode)
        os.replace(temporary_name, destination)
        os.chmod(destination, mode)
    finally:
        if temporary_name and Path(temporary_name).exists():
            Path(temporary_name).unlink()
    return destination


def write_json_report(
    data: Any, output: str | Path | None, *, force: bool = False
) -> None:
    """Print JSON or atomically write it to an explicitly selected local file."""
    serialized = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output is None:
        print(serialized, end="")
        return
    destination = safe_output_path(output, ".json", force=force)
    atomic_write_text(destination, serialized)


def write_markdown(
    text: str, output: str | Path, *, force: bool = False
) -> Path:
    destination = safe_output_path(output, ".md", force=force)
    return atomic_write_text(destination, text)


def issue(code: str, field: str) -> dict[str, str]:
    """Create a content-free finding safe for confidential reports."""
    return {"code": code, "field": field}


def error_exit(exc: ValidationError) -> int:
    print(f"ERROR: {exc}", file=os.sys.stderr)
    return 2
```

### `scripts/audit_citations.py`

```python
#!/usr/bin/env python3
"""Audit Markdown citation keys against a local reference CSV without network use."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_csv_records,
    read_markdown,
    require_doi,
    require_enum,
    require_identifier,
    require_text,
    require_unique,
    require_url,
    write_json_report,
)

REFERENCE_FIELDS = (
    "reference_id",
    "title",
    "authors",
    "year",
    "doi",
    "url",
    "verification_status",
)
VERIFICATION_STATUSES = {
    "verified_primary",
    "verified_secondary",
    "not_verified",
}
CITATION_GROUP_RE = re.compile(r"\[([^\]\n]{1,1000})\]")
CITATION_KEY_RE = re.compile(r"@([A-Za-z][A-Za-z0-9._:-]{0,95})")
YEAR_RE = re.compile(r"^(?:1[5-9]\d{2}|20\d{2}|2100)$")


def load_references(raw_path: str) -> list[dict[str, str]]:
    rows = read_csv_records(
        raw_path,
        required_fields=REFERENCE_FIELDS,
        allowed_fields=REFERENCE_FIELDS,
    )
    parsed: list[dict[str, str]] = []
    ids: list[str] = []
    for line_number, row in enumerate(rows, start=2):
        context = f"references row {line_number}"
        reference_id = require_identifier(
            row["reference_id"], f"{context}.reference_id"
        )
        ids.append(reference_id)
        year = require_text(row["year"], f"{context}.year", maximum=4)
        if not YEAR_RE.fullmatch(year):
            raise ValidationError(f"{context}.year must be a four-digit year")
        parsed.append(
            {
                "reference_id": reference_id,
                "title": require_text(
                    row["title"], f"{context}.title", minimum=3, maximum=2_000
                ),
                "authors": require_text(
                    row["authors"], f"{context}.authors", minimum=2, maximum=2_000
                ),
                "year": year,
                "doi": require_doi(
                    row["doi"], f"{context}.doi", allow_empty=True
                ),
                "url": require_url(
                    row["url"], f"{context}.url", allow_empty=True
                ),
                "verification_status": require_enum(
                    row["verification_status"],
                    VERIFICATION_STATUSES,
                    f"{context}.verification_status",
                ),
            }
        )
    require_unique(ids, "reference IDs")
    return parsed


def extract_citations(markdown: str) -> tuple[dict[str, list[int]], list[int]]:
    citations: dict[str, list[int]] = {}
    malformed_lines: list[int] = []
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        matched_starts = 0
        for group in CITATION_GROUP_RE.finditer(line):
            content = group.group(1)
            if "@" not in content:
                continue
            matched_starts += content.count("@")
            keys = CITATION_KEY_RE.findall(content)
            if not keys:
                malformed_lines.append(line_number)
                continue
            for key in keys:
                citations.setdefault(key, []).append(line_number)
        if line.count("[@") > matched_starts:
            malformed_lines.append(line_number)
    return citations, sorted(set(malformed_lines))


def audit(markdown: str, references: list[dict[str, str]]) -> dict[str, Any]:
    citations, malformed_lines = extract_citations(markdown)
    by_id = {row["reference_id"]: row for row in references}
    cited_ids = set(citations)
    reference_ids = set(by_id)
    missing_ids = sorted(cited_ids - reference_ids)
    uncited_ids = sorted(reference_ids - cited_ids)
    unverified_ids = sorted(
        reference_id
        for reference_id in cited_ids.intersection(reference_ids)
        if by_id[reference_id]["verification_status"] == "not_verified"
    )
    no_locator_ids = sorted(
        row["reference_id"]
        for row in references
        if not row["doi"] and not row["url"]
    )
    errors: list[dict[str, str]] = [
        issue("CITATION_WITHOUT_REFERENCE", reference_id)
        for reference_id in missing_ids
    ]
    errors.extend(
        issue("MALFORMED_CITATION_SYNTAX", f"line:{line_number}")
        for line_number in malformed_lines
    )
    warnings: list[dict[str, str]] = [
        issue("REFERENCE_NOT_CITED", reference_id) for reference_id in uncited_ids
    ]
    warnings.extend(
        issue("CITED_REFERENCE_NOT_VERIFIED", reference_id)
        for reference_id in unverified_ids
    )
    warnings.extend(
        issue("REFERENCE_HAS_NO_PERSISTENT_LOCATOR", reference_id)
        for reference_id in no_locator_ids
    )
    verification_counts = Counter(
        row["verification_status"] for row in references
    )
    return {
        "schema_version": "2.0",
        "valid": not errors,
        "status": "VALID" if not errors else "CITATION_INCONSISTENCIES",
        "errors": errors,
        "warnings": warnings,
        "citation_occurrence_count": sum(len(lines) for lines in citations.values()),
        "cited_reference_count": len(cited_ids),
        "reference_count": len(references),
        "missing_reference_ids": missing_ids,
        "missing_reference_line_numbers": {
            reference_id: sorted(set(citations[reference_id]))
            for reference_id in missing_ids
        },
        "uncited_reference_ids": uncited_ids,
        "unverified_cited_reference_ids": unverified_ids,
        "references_without_persistent_locator": no_locator_ids,
        "verification_counts": dict(sorted(verification_counts.items())),
        "malformed_citation_line_numbers": malformed_lines,
        "notice": (
            "This local audit checks structured citation-key consistency and "
            "identifier format only. It does not query registries, verify that a "
            "source exists, confirm that a citation supports a claim, or echo "
            "manuscript/reference prose."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit Pandoc-style Markdown citations such as [@ref-id] against a "
            "strict local reference CSV. No network calls are made."
        )
    )
    parser.add_argument("manuscript", help="Local Markdown file")
    parser.add_argument("references", help="Local reference CSV")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = audit(
            read_markdown(args.manuscript),
            load_references(args.references),
        )
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/audit_statistics_reproducibility.py`

```python
#!/usr/bin/env python3
"""Audit a structured statistics and reproducibility checklist locally."""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_json,
    require_bool,
    require_enum,
    require_exact_keys,
    require_identifier,
    require_identifier_list,
    require_list,
    require_object,
    require_text,
    require_text_list,
    require_unique,
    write_json_report,
)

CORE_ITEM_IDS = (
    "question.estimand_alignment",
    "design.unit_and_independence",
    "design.sample_size_precision",
    "design.allocation_randomization",
    "design.blinding",
    "data.inclusion_exclusion",
    "data.missing_data",
    "data.outliers_transformations",
    "analysis.prespecification",
    "analysis.method_design_alignment",
    "analysis.assumptions_diagnostics",
    "analysis.multiplicity",
    "analysis.clustering_repeated_measures",
    "results.effect_sizes_uncertainty",
    "results.denominators_flow",
    "results.complete_outcomes_harms",
    "reproducibility.data_materials_access",
    "reproducibility.code_environment_parameters",
    "reproducibility.provenance_versions",
    "ethics.approval_consent_governance",
    "interpretation.claim_evidence_causality",
    "integrity.deviations_selective_reporting",
)
CATEGORIES = {
    "question",
    "design",
    "data",
    "analysis",
    "results",
    "reproducibility",
    "ethics",
    "interpretation",
    "integrity",
}
APPLICABILITY = {"applicable", "not_applicable"}
STATUSES = {
    "verified_present",
    "partly_documented",
    "missing",
    "not_assessed",
    "not_applicable",
}
SPECIALIST_TRIGGER_IDS = {
    "question.estimand_alignment",
    "data.missing_data",
    "analysis.method_design_alignment",
    "analysis.assumptions_diagnostics",
    "analysis.multiplicity",
    "analysis.clustering_repeated_measures",
    "results.effect_sizes_uncertainty",
    "interpretation.claim_evidence_causality",
}


def load_checklist(payload: Any) -> dict[str, Any]:
    root = require_object(payload, "checklist")
    require_exact_keys(
        root,
        required={
            "schema_version",
            "checklist_id",
            "study_design",
            "specialist_review",
            "items",
        },
        context="checklist",
    )
    schema_version = require_enum(
        root["schema_version"], {"2.0"}, "checklist.schema_version"
    )
    checklist_id = require_identifier(root["checklist_id"], "checklist.checklist_id")
    study_design = require_identifier(root["study_design"], "checklist.study_design")

    specialist = require_object(
        root["specialist_review"], "checklist.specialist_review"
    )
    require_exact_keys(
        specialist,
        required={"needed", "areas", "requested"},
        context="checklist.specialist_review",
    )
    specialist_review = {
        "needed": require_enum(
            specialist["needed"],
            {"yes", "no", "undetermined"},
            "checklist.specialist_review.needed",
        ),
        "areas": require_identifier_list(
            specialist["areas"], "checklist.specialist_review.areas"
        ),
        "requested": require_bool(
            specialist["requested"], "checklist.specialist_review.requested"
        ),
    }

    raw_items = require_list(root["items"], "checklist.items", minimum=1, maximum=200)
    items: list[dict[str, Any]] = []
    item_ids: list[str] = []
    for index, raw_item in enumerate(raw_items):
        context = f"checklist.items[{index}]"
        item = require_object(raw_item, context)
        require_exact_keys(
            item,
            required={
                "id",
                "category",
                "applicability",
                "status",
                "evidence_locations",
                "note",
                "requested_action",
            },
            context=context,
        )
        item_id = require_identifier(item["id"], f"{context}.id")
        item_ids.append(item_id)
        items.append(
            {
                "id": item_id,
                "category": require_enum(
                    item["category"], CATEGORIES, f"{context}.category"
                ),
                "applicability": require_enum(
                    item["applicability"], APPLICABILITY, f"{context}.applicability"
                ),
                "status": require_enum(
                    item["status"], STATUSES, f"{context}.status"
                ),
                "evidence_locations": require_text_list(
                    item["evidence_locations"],
                    f"{context}.evidence_locations",
                    maximum=50,
                ),
                "note": require_text(
                    item["note"],
                    f"{context}.note",
                    allow_empty=True,
                    maximum=2_000,
                ),
                "requested_action": require_text(
                    item["requested_action"],
                    f"{context}.requested_action",
                    allow_empty=True,
                    maximum=2_000,
                ),
            }
        )
    require_unique(item_ids, "checklist.items")
    return {
        "schema_version": schema_version,
        "checklist_id": checklist_id,
        "study_design": study_design,
        "specialist_review": specialist_review,
        "items": items,
    }


def audit(checklist: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    items_by_id = {item["id"]: item for item in checklist["items"]}
    missing_core = sorted(set(CORE_ITEM_IDS) - set(items_by_id))
    if missing_core:
        errors.extend(issue("CORE_ITEM_MISSING", item_id) for item_id in missing_core)

    status_counts = Counter()
    gaps_by_category: dict[str, list[str]] = {}
    action_missing: list[str] = []
    specialist_triggers: list[str] = []

    for item in checklist["items"]:
        item_id = item["id"]
        status = item["status"]
        status_counts[status] += 1
        if item["applicability"] == "not_applicable":
            if status != "not_applicable":
                errors.append(issue("APPLICABILITY_STATUS_MISMATCH", item_id))
            if not item["note"]:
                errors.append(issue("NOT_APPLICABLE_RATIONALE_REQUIRED", item_id))
            continue
        if status == "not_applicable":
            errors.append(issue("APPLICABILITY_STATUS_MISMATCH", item_id))
            continue
        if status == "verified_present" and not item["evidence_locations"]:
            errors.append(issue("EVIDENCE_LOCATION_REQUIRED", item_id))
        if status == "partly_documented":
            if not item["evidence_locations"]:
                errors.append(issue("PARTIAL_ITEM_NEEDS_EVIDENCE_LOCATION", item_id))
            if not item["requested_action"]:
                errors.append(issue("PARTIAL_ITEM_NEEDS_REQUESTED_ACTION", item_id))
        if status in {"partly_documented", "missing", "not_assessed"}:
            gaps_by_category.setdefault(item["category"], []).append(item_id)
            if not item["requested_action"]:
                action_missing.append(item_id)
                warnings.append(issue("REQUESTED_ACTION_MISSING", item_id))
            if item_id in SPECIALIST_TRIGGER_IDS:
                specialist_triggers.append(item_id)

    specialist = checklist["specialist_review"]
    specialist_recommended = bool(specialist_triggers)
    if specialist["needed"] == "yes" and not specialist["requested"]:
        warnings.append(
            issue("SPECIALIST_REVIEW_NOT_REQUESTED", "specialist_review.requested")
        )
    if specialist["needed"] == "undetermined":
        warnings.append(
            issue("SPECIALIST_REVIEW_UNDETERMINED", "specialist_review.needed")
        )
    if specialist_recommended and specialist["needed"] == "no":
        warnings.append(
            issue("SPECIALIST_REVIEW_DECLARATION_RECHECK", "specialist_review.needed")
        )

    return {
        "schema_version": "2.0",
        "checklist_id": checklist["checklist_id"],
        "valid": not errors,
        "status": (
            "INVALID_CHECKLIST"
            if errors
            else "VALID_WITH_REVIEW_GAPS"
            if gaps_by_category
            else "VALID_NO_RECORDED_GAPS"
        ),
        "errors": errors,
        "warnings": warnings,
        "study_design": checklist["study_design"],
        "item_count": len(checklist["items"]),
        "status_counts": dict(sorted(status_counts.items())),
        "gap_item_ids_by_category": {
            category: sorted(item_ids)
            for category, item_ids in sorted(gaps_by_category.items())
        },
        "item_ids_missing_requested_action": sorted(action_missing),
        "specialist_review": {
            "declared_needed": specialist["needed"],
            "declared_areas": specialist["areas"],
            "declared_requested": specialist["requested"],
            "trigger_item_ids": sorted(specialist_triggers),
            "recheck_recommended": specialist_recommended,
        },
        "notice": (
            "This is a structured completeness and consistency audit, not a "
            "statistical reanalysis, reproducibility claim, quality score, or "
            "publication recommendation. A qualified specialist must evaluate "
            "methods outside the reviewer's competence."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a local statistics/reproducibility checklist and emit only "
            "item identifiers and counts."
        )
    )
    parser.add_argument("checklist", help="Local checklist JSON")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = audit(load_checklist(read_json(args.checklist)))
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/generate_review_scaffold.py`

```python
#!/usr/bin/env python3
"""Generate a local structured peer-review draft scaffold from validated intake."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    read_markdown,
    write_markdown,
)
from validate_review_intake import validate_intake

TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1] / "assets" / "review_scaffold_template.md"
)
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")


def generate(payload: Any, template_path: Path = TEMPLATE_PATH) -> str:
    """Render only safe intake identifiers; never interpolate manuscript prose."""
    report = validate_intake(payload)
    if not report["valid"]:
        codes = sorted({item["code"] for item in report["errors"]})
        raise ValidationError(
            "intake is blocked; resolve these controls first: " + ", ".join(codes)
        )
    template = read_markdown(template_path)
    replacements = {
        "{{REVIEW_ID}}": report["review_id"],
        "{{REVIEWER_CAPACITY}}": report["normalized_scope"]["capacity"],
        "{{PEER_REVIEW_MODEL}}": report["normalized_scope"]["peer_review_model"],
        "{{AI_PLAN}}": report["normalized_scope"]["ai_plan"],
    }
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    unresolved = sorted(set(PLACEHOLDER_RE.findall(rendered)))
    if unresolved:
        raise ValidationError(
            "scaffold template contains unresolved placeholders: "
            + ", ".join(unresolved)
        )
    return rendered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a private local Markdown review scaffold after intake "
            "authorization and conflict controls pass."
        )
    )
    parser.add_argument("intake", help="Local review intake JSON")
    parser.add_argument("-o", "--output", required=True, help="Output Markdown path")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        from _common import read_json

        rendered = generate(read_json(args.intake))
        destination = write_markdown(rendered, args.output, force=args.force)
        print(f"Created local review scaffold: {destination}")
        return 0
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/lint_review.py`

```python
#!/usr/bin/env python3
"""Lint a structured review for channel separation, tone, and actionability."""

from __future__ import annotations

import argparse
import re
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_markdown,
    write_json_report,
)

AUTHOR_HEADING = "# Comments to authors"
EDITOR_HEADING = "# Confidential comments to editor"
COMMENT_HEADING_RE = re.compile(
    r"^###\s+(?P<kind>Major|Minor)\s+comment(?:\s+(?P<id>[A-Za-z0-9._:-]+))?\s*$",
    re.IGNORECASE,
)
FIELD_RE = re.compile(
    r"^-\s*(?P<label>Location|Observation|Evidence or criterion|"
    r"Why it matters|Requested action):\s*(?P<value>.*)$",
    re.IGNORECASE,
)
REQUIRED_FIELDS = {
    "location",
    "observation",
    "evidence or criterion",
    "why it matters",
    "requested action",
}
PLACEHOLDER_RE = re.compile(
    r"^\s*(?:"
    r"\[(?:write|state|describe|identify|add|cite|section|figure|table|line|"
    r"explain|request|replace|if)\b[^\]]*\]"
    r"|TBD|TODO|<[^>]+>)\s*$",
    re.IGNORECASE,
)
UNRESOLVED_SCAFFOLD_RE = re.compile(
    r"\[(?:write|state|describe|identify|add|cite|explain|request|replace)\b",
    re.IGNORECASE,
)
ABUSIVE_RE = re.compile(
    r"\b(?:idiot(?:ic)?|incompetent|ridiculous|nonsense|garbage|lazy|sloppy|"
    r"clueless|amateurish|embarrassing|worthless)\b",
    re.IGNORECASE,
)
PERSONAL_ATTACK_RE = re.compile(
    r"\b(?:the\s+)?authors?\s+(?:do(?:es)?\s+not\s+understand|"
    r"failed\s+to\s+understand|are\s+unaware|are\s+careless|"
    r"are\s+dishonest)\b",
    re.IGNORECASE,
)
EDITORIAL_DECISION_RE = re.compile(
    r"\b(?:(?:i|we)\s+(?:recommend|would\s+recommend|have\s+decided|"
    r"decided)\s+(?:accept(?:ance)?|reject(?:ion)?)|"
    r"recommendation\s*:\s*(?:accept|reject|major\s+revision|"
    r"minor\s+revision))\b",
    re.IGNORECASE,
)
IMPERSONATION_RE = re.compile(
    r"\b(?:i\s+am\s+(?:the\s+)?(?:editor|assigned\s+reviewer)|"
    r"on\s+behalf\s+of\s+the\s+(?:journal|editor)|"
    r"we\s+have\s+made\s+the\s+editorial\s+decision)\b",
    re.IGNORECASE,
)
EXECUTION_CLAIM_RE = re.compile(
    r"\bi\s+(?:ran|performed|replicated|reproduced|verified|confirmed)\s+"
    r"(?:the|this|these)\s+(?:analysis|analyses|experiment|experiments|"
    r"results|dataset|data)\b",
    re.IGNORECASE,
)
CONFIDENTIAL_MARKER_RE = re.compile(
    r"\b(?:confidential\s+to\s+(?:the\s+)?editor|editor[- ]only)\b",
    re.IGNORECASE,
)


def _content_value(value: str) -> bool:
    text = value.strip()
    return bool(text) and not PLACEHOLDER_RE.fullmatch(text)


def _comment_blocks(lines: list[str]) -> list[dict[str, Any]]:
    starts: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(lines):
        match = COMMENT_HEADING_RE.match(line.strip())
        if match:
            starts.append((index, match))
    blocks: list[dict[str, Any]] = []
    for position, (start, match) in enumerate(starts):
        end = starts[position + 1][0] if position + 1 < len(starts) else len(lines)
        for candidate in range(start + 1, end):
            if lines[candidate].startswith("# ") or lines[candidate].startswith("## "):
                end = candidate
                break
        blocks.append(
            {
                "start": start,
                "end": end,
                "kind": match.group("kind").lower(),
                "id": match.group("id")
                or f"{match.group('kind')[0].upper()}-line-{start + 1}",
            }
        )
    return blocks


def lint(markdown: str) -> dict[str, Any]:
    lines = markdown.splitlines()
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    author_lines = [
        index for index, line in enumerate(lines) if line.strip() == AUTHOR_HEADING
    ]
    editor_lines = [
        index for index, line in enumerate(lines) if line.strip() == EDITOR_HEADING
    ]
    if len(author_lines) != 1:
        errors.append(issue("AUTHOR_CHANNEL_HEADING_REQUIRED_ONCE", "document"))
    if len(editor_lines) != 1:
        errors.append(issue("EDITOR_CHANNEL_HEADING_REQUIRED_ONCE", "document"))
    if author_lines and editor_lines and author_lines[0] >= editor_lines[0]:
        errors.append(issue("CHANNEL_ORDER_INVALID", "document"))

    author_start = author_lines[0] if len(author_lines) == 1 else None
    editor_start = editor_lines[0] if len(editor_lines) == 1 else None

    for line_number, line in enumerate(lines, start=1):
        subject = f"line:{line_number}"
        if ABUSIVE_RE.search(line):
            errors.append(issue("ABUSIVE_OR_DISMISSIVE_LANGUAGE", subject))
        if PERSONAL_ATTACK_RE.search(line):
            errors.append(issue("PERSONAL_ATTACK", subject))
        if EDITORIAL_DECISION_RE.search(line):
            errors.append(issue("EDITORIAL_DECISION_LANGUAGE", subject))
        if IMPERSONATION_RE.search(line):
            errors.append(issue("ROLE_IMPERSONATION_LANGUAGE", subject))
        if EXECUTION_CLAIM_RE.search(line):
            warnings.append(issue("EXECUTION_CLAIM_REQUIRES_PROVENANCE", subject))
        if UNRESOLVED_SCAFFOLD_RE.search(line):
            errors.append(issue("UNRESOLVED_SCAFFOLD_PLACEHOLDER", subject))
        if (
            author_start is not None
            and editor_start is not None
            and author_start < line_number - 1 < editor_start
            and CONFIDENTIAL_MARKER_RE.search(line)
        ):
            errors.append(issue("EDITOR_ONLY_CONTENT_IN_AUTHOR_CHANNEL", subject))

    blocks = _comment_blocks(lines)
    if not blocks:
        warnings.append(issue("NO_STRUCTURED_COMMENTS_FOUND", "document"))
    comment_summaries: list[dict[str, Any]] = []
    for block in blocks:
        fields: dict[str, tuple[str, int]] = {}
        for index in range(block["start"] + 1, block["end"]):
            match = FIELD_RE.match(lines[index].strip())
            if match:
                fields[match.group("label").lower()] = (
                    match.group("value"),
                    index + 1,
                )
        missing_fields = sorted(REQUIRED_FIELDS - set(fields))
        empty_fields = sorted(
            label for label, (value, _) in fields.items() if not _content_value(value)
        )
        for label in missing_fields:
            errors.append(
                issue(
                    "ACTIONABILITY_FIELD_MISSING",
                    f"{block['id']}:{label.replace(' ', '_')}",
                )
            )
        for label in empty_fields:
            errors.append(
                issue(
                    "ACTIONABILITY_FIELD_EMPTY",
                    f"{block['id']}:{label.replace(' ', '_')}",
                )
            )
        if editor_start is not None and block["start"] > editor_start:
            warnings.append(
                issue("AUTHOR_COMMENT_BLOCK_IN_EDITOR_CHANNEL", block["id"])
            )
        comment_summaries.append(
            {
                "comment_id": block["id"],
                "kind": block["kind"],
                "heading_line": block["start"] + 1,
                "missing_fields": missing_fields,
                "empty_fields": empty_fields,
            }
        )

    return {
        "schema_version": "2.0",
        "valid": not errors,
        "status": "READY_FOR_HUMAN_REVIEW" if not errors else "REVISION_REQUIRED",
        "errors": errors,
        "warnings": warnings,
        "line_count": len(lines),
        "structured_comment_count": len(blocks),
        "comments": comment_summaries,
        "channel_separation": {
            "author_heading_count": len(author_lines),
            "editor_heading_count": len(editor_lines),
            "author_before_editor": bool(
                author_lines
                and editor_lines
                and author_lines[0] < editor_lines[0]
            ),
        },
        "notice": (
            "This deterministic lint uses structural and lexical rules. It does "
            "not judge scientific validity, verify whether statements are true, "
            "or replace accountable human review. Findings contain line numbers "
            "and rule IDs, not review or manuscript text."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Lint a local structured review for author/editor channel separation, "
            "professional tone, and actionable comment fields."
        )
    )
    parser.add_argument("review", help="Local review Markdown")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = lint(read_markdown(args.review))
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/select_reporting_guidelines.py`

```python
#!/usr/bin/env python3
"""Select bundled reporting guidance and audit checklist coverage locally."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_csv_records,
    read_json,
    require_enum,
    require_exact_keys,
    require_identifier,
    require_identifier_list,
    require_object,
    require_text,
    require_url,
    write_json_report,
)

ASSET_CATALOG = Path(__file__).resolve().parents[1] / "assets" / "reporting_guidelines.json"
COVERAGE_FIELDS = (
    "guideline_id",
    "item_id",
    "status",
    "location",
    "rationale",
)
COVERAGE_STATUSES = {
    "reported",
    "partly_reported",
    "not_reported",
    "not_applicable",
    "not_assessed",
}
CATALOG_STATUSES = {"current", "legacy_current_qualified"}
CATEGORIES = {"reporting_guideline", "domain_metadata_standard"}
REPORT_KINDS = {"results", "protocol", "abstract", "data_release"}
ITEM_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,63}$")


def load_catalog(path: Path = ASSET_CATALOG) -> dict[str, Any]:
    payload = require_object(read_json(path), "catalog")
    require_exact_keys(
        payload,
        required={"schema_version", "reviewed_on", "notice", "guidelines"},
        context="catalog",
    )
    require_enum(payload["schema_version"], {"2.0"}, "catalog.schema_version")
    require_text(payload["reviewed_on"], "catalog.reviewed_on", maximum=10)
    require_text(payload["notice"], "catalog.notice", maximum=2_000)
    guidelines = payload["guidelines"]
    if not isinstance(guidelines, list) or not guidelines:
        raise ValidationError("catalog.guidelines must be a non-empty array")

    parsed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw_entry in enumerate(guidelines):
        context = f"catalog.guidelines[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(
            entry,
            required={
                "id",
                "name",
                "version",
                "status",
                "category",
                "study_types",
                "report_kinds",
                "required_features",
                "domains",
                "main_item_count",
                "url",
                "notes",
            },
            context=context,
        )
        guideline_id = require_identifier(entry["id"], f"{context}.id")
        if guideline_id in seen:
            raise ValidationError(f"catalog contains duplicate ID: {guideline_id}")
        seen.add(guideline_id)
        item_count = entry["main_item_count"]
        if item_count is not None:
            if type(item_count) is not int or not 1 <= item_count <= 200:
                raise ValidationError(
                    f"{context}.main_item_count must be null or an integer 1-200"
                )
        parsed.append(
            {
                "id": guideline_id,
                "name": require_text(entry["name"], f"{context}.name", maximum=200),
                "version": require_text(
                    entry["version"], f"{context}.version", maximum=100
                ),
                "status": require_enum(
                    entry["status"], CATALOG_STATUSES, f"{context}.status"
                ),
                "category": require_enum(
                    entry["category"], CATEGORIES, f"{context}.category"
                ),
                "study_types": require_identifier_list(
                    entry["study_types"], f"{context}.study_types", minimum=1
                ),
                "report_kinds": [
                    require_enum(item, REPORT_KINDS, f"{context}.report_kinds")
                    for item in entry["report_kinds"]
                ],
                "required_features": require_identifier_list(
                    entry["required_features"], f"{context}.required_features"
                ),
                "domains": require_identifier_list(
                    entry["domains"], f"{context}.domains", minimum=1
                ),
                "main_item_count": item_count,
                "url": require_url(entry["url"], f"{context}.url"),
                "notes": require_text(
                    entry["notes"], f"{context}.notes", maximum=1_000
                ),
            }
        )
    return {
        "schema_version": payload["schema_version"],
        "reviewed_on": payload["reviewed_on"],
        "notice": payload["notice"],
        "guidelines": parsed,
    }


def load_profile(payload: Any) -> dict[str, Any]:
    profile = require_object(payload, "profile")
    require_exact_keys(
        profile,
        required={
            "schema_version",
            "profile_id",
            "study_types",
            "report_kind",
            "features",
            "domains",
        },
        context="profile",
    )
    return {
        "schema_version": require_enum(
            profile["schema_version"], {"2.0"}, "profile.schema_version"
        ),
        "profile_id": require_identifier(profile["profile_id"], "profile.profile_id"),
        "study_types": require_identifier_list(
            profile["study_types"], "profile.study_types", minimum=1
        ),
        "report_kind": require_enum(
            profile["report_kind"], REPORT_KINDS, "profile.report_kind"
        ),
        "features": require_identifier_list(profile["features"], "profile.features"),
        "domains": require_identifier_list(
            profile["domains"], "profile.domains", minimum=1
        ),
    }


def select_guidelines(
    profile: dict[str, Any], catalog: dict[str, Any]
) -> list[dict[str, Any]]:
    study_types = set(profile["study_types"])
    features = set(profile["features"])
    domains = set(profile["domains"])
    selected: list[dict[str, Any]] = []
    for entry in catalog["guidelines"]:
        if not study_types.intersection(entry["study_types"]):
            continue
        if profile["report_kind"] not in entry["report_kinds"]:
            continue
        if not set(entry["required_features"]).issubset(features):
            continue
        if "all" not in entry["domains"] and not domains.intersection(entry["domains"]):
            continue
        selected.append(entry)
    return sorted(
        selected,
        key=lambda item: (
            item["category"] != "reporting_guideline",
            item["id"],
        ),
    )


def load_coverage(raw_path: str | Path) -> list[dict[str, str]]:
    rows = read_csv_records(
        raw_path,
        required_fields=COVERAGE_FIELDS,
        allowed_fields=COVERAGE_FIELDS,
    )
    seen: set[tuple[str, str]] = set()
    parsed: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=2):
        guideline_id = require_identifier(
            row["guideline_id"], f"coverage row {index}.guideline_id"
        )
        item_id = require_text(
            row["item_id"], f"coverage row {index}.item_id", maximum=64
        )
        if not ITEM_ID_RE.fullmatch(item_id):
            raise ValidationError(
                f"coverage row {index}.item_id has an invalid identifier format"
            )
        key = (guideline_id, item_id)
        if key in seen:
            raise ValidationError(
                f"coverage contains duplicate guideline/item pair: "
                f"{guideline_id}/{item_id}"
            )
        seen.add(key)
        status = require_enum(
            row["status"], COVERAGE_STATUSES, f"coverage row {index}.status"
        )
        location = require_text(
            row["location"],
            f"coverage row {index}.location",
            allow_empty=True,
            maximum=500,
        )
        rationale = require_text(
            row["rationale"],
            f"coverage row {index}.rationale",
            allow_empty=True,
            maximum=1_000,
        )
        parsed.append(
            {
                "guideline_id": guideline_id,
                "item_id": item_id,
                "status": status,
                "location": location,
                "rationale": rationale,
            }
        )
    return parsed


def assess(
    profile: dict[str, Any],
    catalog: dict[str, Any],
    coverage_rows: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    selected = select_guidelines(profile, catalog)
    selected_by_id = {entry["id"]: entry for entry in selected}
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    if not selected:
        warnings.append(issue("NO_BUNDLED_GUIDELINE_MATCH", "profile.study_types"))

    rows_by_guideline: dict[str, list[dict[str, str]]] = {}
    if coverage_rows is not None:
        for row in coverage_rows:
            rows_by_guideline.setdefault(row["guideline_id"], []).append(row)
            subject = f"{row['guideline_id']}:{row['item_id']}"
            if row["status"] in {"reported", "partly_reported"} and not row["location"]:
                errors.append(issue("COVERAGE_LOCATION_REQUIRED", subject))
            if row["status"] == "not_applicable" and not row["rationale"]:
                errors.append(issue("NOT_APPLICABLE_RATIONALE_REQUIRED", subject))
            if row["guideline_id"] not in selected_by_id:
                warnings.append(issue("COVERAGE_FOR_UNSELECTED_GUIDELINE", subject))

    coverage: list[dict[str, Any]] = []
    for entry in selected:
        rows = rows_by_guideline.get(entry["id"], [])
        statuses = Counter(row["status"] for row in rows)
        observed_ids = {row["item_id"] for row in rows}
        expected_count = entry["main_item_count"]
        unrecorded: list[str] = []
        unexpected: list[str] = []
        record_complete: bool | None = None
        if expected_count is not None:
            expected_ids = {str(number) for number in range(1, expected_count + 1)}
            unrecorded = sorted(
                expected_ids - observed_ids, key=lambda value: int(value)
            )
            unexpected = sorted(observed_ids - expected_ids)
            record_complete = not unrecorded and not unexpected
            if unexpected:
                warnings.append(
                    issue("NON_MAIN_ITEM_IDS_RECORDED", entry["id"])
                )
        elif rows:
            record_complete = None
            warnings.append(
                issue("OFFICIAL_ITEM_SET_MUST_BE_VERIFIED", entry["id"])
            )

        gap_ids = sorted(
            row["item_id"]
            for row in rows
            if row["status"]
            in {"partly_reported", "not_reported", "not_assessed"}
        )
        coverage.append(
            {
                "guideline_id": entry["id"],
                "main_item_count": expected_count,
                "recorded_item_count": len(rows),
                "coverage_record_complete": record_complete,
                "status_counts": dict(sorted(statuses.items())),
                "unrecorded_main_item_ids": unrecorded,
                "unexpected_item_ids": unexpected,
                "reporting_gap_item_ids": gap_ids,
            }
        )

    return {
        "schema_version": "2.0",
        "profile_id": profile["profile_id"],
        "valid": not errors,
        "status": "VALID" if not errors else "INVALID_COVERAGE_RECORD",
        "errors": errors,
        "warnings": warnings,
        "selected_guidelines": [
            {
                "id": entry["id"],
                "name": entry["name"],
                "version": entry["version"],
                "status": entry["status"],
                "category": entry["category"],
                "url": entry["url"],
                "notes": entry["notes"],
            }
            for entry in selected
        ],
        "coverage": coverage if coverage_rows is not None else None,
        "catalog_reviewed_on": catalog["reviewed_on"],
        "notice": (
            "Guideline selection and checklist coverage concern reporting "
            "completeness only. They are not scores and do not establish study "
            "quality, validity, conduct, or manuscript merit. Check the official "
            "guideline, applicable extensions, and target venue policy."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Select current bundled reporting guidance and optionally audit a "
            "local checklist coverage CSV. No network calls are made."
        )
    )
    parser.add_argument("profile", help="Local study profile JSON")
    parser.add_argument(
        "--coverage",
        help=(
            "Optional coverage CSV using aggregate main item IDs (for example, "
            "1 through 30 for CONSORT 2025)"
        ),
    )
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        profile = load_profile(read_json(args.profile))
        catalog = load_catalog()
        coverage = load_coverage(args.coverage) if args.coverage else None
        report = assess(profile, catalog, coverage)
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_claim_evidence.py`

```python
#!/usr/bin/env python3
"""Validate a bounded claim-evidence alignment matrix without echoing prose."""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_csv_records,
    require_enum,
    require_identifier,
    require_text,
    require_unique,
    split_identifiers,
    write_json_report,
)

FIELDS = (
    "claim_id",
    "location",
    "claim_type",
    "claim_summary",
    "evidence_ids",
    "support_level",
    "alignment_issue",
    "limitation",
    "requested_action",
)
CLAIM_TYPES = {
    "primary_outcome",
    "secondary_outcome",
    "causal",
    "mechanistic",
    "diagnostic",
    "prediction",
    "safety",
    "generalization",
    "methods",
    "other",
}
SUPPORT_LEVELS = {
    "supported",
    "partly_supported",
    "unsupported",
    "not_assessed",
}
ALIGNMENT_ISSUES = {
    "none",
    "direction",
    "magnitude",
    "population",
    "outcome",
    "timepoint",
    "causal_language",
    "scope",
    "uncertainty",
    "selective_reporting",
    "other",
}


def load_matrix(raw_path: str) -> list[dict[str, Any]]:
    rows = read_csv_records(
        raw_path,
        required_fields=FIELDS,
        allowed_fields=FIELDS,
    )
    parsed: list[dict[str, Any]] = []
    claim_ids: list[str] = []
    for line_number, row in enumerate(rows, start=2):
        context = f"matrix row {line_number}"
        claim_id = require_identifier(row["claim_id"], f"{context}.claim_id")
        claim_ids.append(claim_id)
        parsed.append(
            {
                "claim_id": claim_id,
                "location": require_text(
                    row["location"], f"{context}.location", maximum=500
                ),
                "claim_type": require_enum(
                    row["claim_type"], CLAIM_TYPES, f"{context}.claim_type"
                ),
                "claim_summary": require_text(
                    row["claim_summary"],
                    f"{context}.claim_summary",
                    minimum=10,
                    maximum=2_000,
                ),
                "evidence_ids": split_identifiers(
                    row["evidence_ids"],
                    f"{context}.evidence_ids",
                    allow_empty=True,
                ),
                "support_level": require_enum(
                    row["support_level"],
                    SUPPORT_LEVELS,
                    f"{context}.support_level",
                ),
                "alignment_issue": require_enum(
                    row["alignment_issue"],
                    ALIGNMENT_ISSUES,
                    f"{context}.alignment_issue",
                ),
                "limitation": require_text(
                    row["limitation"],
                    f"{context}.limitation",
                    allow_empty=True,
                    maximum=2_000,
                ),
                "requested_action": require_text(
                    row["requested_action"],
                    f"{context}.requested_action",
                    allow_empty=True,
                    maximum=2_000,
                ),
            }
        )
    require_unique(claim_ids, "claim-evidence matrix")
    return parsed


def validate_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    support_counts = Counter()
    issue_counts = Counter()
    gap_ids: list[str] = []
    action_missing_ids: list[str] = []

    for row in rows:
        claim_id = row["claim_id"]
        support = row["support_level"]
        alignment_issue = row["alignment_issue"]
        evidence_ids = row["evidence_ids"]
        support_counts[support] += 1
        issue_counts[alignment_issue] += 1

        if support == "supported":
            if not evidence_ids:
                errors.append(issue("SUPPORTED_CLAIM_HAS_NO_EVIDENCE", claim_id))
            if alignment_issue != "none":
                errors.append(issue("SUPPORTED_CLAIM_HAS_ALIGNMENT_ISSUE", claim_id))
        elif support == "partly_supported":
            gap_ids.append(claim_id)
            if not evidence_ids:
                errors.append(issue("PARTIAL_CLAIM_HAS_NO_EVIDENCE", claim_id))
            if alignment_issue == "none":
                errors.append(issue("PARTIAL_CLAIM_NEEDS_ISSUE_CODE", claim_id))
        elif support in {"unsupported", "not_assessed"}:
            gap_ids.append(claim_id)
            if alignment_issue == "none" and support == "unsupported":
                errors.append(issue("UNSUPPORTED_CLAIM_NEEDS_ISSUE_CODE", claim_id))

        if support != "supported" and not row["requested_action"]:
            action_missing_ids.append(claim_id)
            warnings.append(issue("REQUESTED_ACTION_MISSING", claim_id))
        if alignment_issue != "none" and not row["limitation"]:
            warnings.append(issue("LIMITATION_CONTEXT_MISSING", claim_id))
        if row["claim_type"] in {"causal", "mechanistic"} and support == "supported":
            warnings.append(
                issue("CAUSAL_OR_MECHANISTIC_SUPPORT_REQUIRES_EXPERT_REVIEW", claim_id)
            )

    return {
        "schema_version": "2.0",
        "valid": not errors,
        "status": (
            "INVALID_MATRIX"
            if errors
            else "VALID_WITH_ALIGNMENT_GAPS"
            if gap_ids
            else "VALID_NO_RECORDED_GAPS"
        ),
        "errors": errors,
        "warnings": warnings,
        "claim_count": len(rows),
        "support_counts": dict(sorted(support_counts.items())),
        "alignment_issue_counts": dict(sorted(issue_counts.items())),
        "claim_ids_requiring_resolution": sorted(gap_ids),
        "claim_ids_missing_requested_action": sorted(action_missing_ids),
        "notice": (
            "This report checks matrix structure and declared claim-evidence "
            "alignment only. It does not verify evidence truth, reproduce analyses, "
            "or determine manuscript merit. Reports contain identifiers, not claim "
            "or manuscript text."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a local claim-evidence CSV and emit only identifiers and "
            "counts; raw claim text is never echoed."
        )
    )
    parser.add_argument("matrix", help="Local claim-evidence matrix CSV")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = validate_matrix(load_matrix(args.matrix))
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_review_intake.py`

```python
#!/usr/bin/env python3
"""Validate peer-review scope, authorization, conflicts, and handling controls."""

from __future__ import annotations

import argparse
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_json,
    require_bool,
    require_enum,
    require_exact_keys,
    require_identifier,
    require_identifier_list,
    require_object,
    require_text_list,
    write_json_report,
)

MATERIAL_STATUSES = {
    "unpublished_confidential",
    "public_preprint",
    "published",
    "synthetic",
}
AUTHORIZATION_BASES = {
    "journal_invitation",
    "editor_assignment",
    "author_request",
    "public_material",
    "synthetic_training",
}
CAPACITIES = {
    "assigned_reviewer",
    "disclosed_co_reviewer",
    "author_requested_reader",
    "editorial_support",
    "training",
}
CONFLICT_STATUSES = {
    "not_assessed",
    "none_identified",
    "disclosed_to_editor",
    "unresolved",
}
PEER_REVIEW_MODELS = {
    "single_anonymized",
    "double_anonymized",
    "open",
    "transparent",
    "post_publication",
    "unknown",
}
AI_POLICIES = {
    "prohibited",
    "permission_required",
    "permitted_with_disclosure",
    "not_stated",
}
AI_PLANS = {"none", "local_deterministic_tools", "approved_ai_assistance"}
RETENTION_RULES = {
    "delete_after_review",
    "delete_after_editor_confirmation",
    "retain_per_venue_policy",
    "public_material",
}


def validate_intake(payload: Any) -> dict[str, Any]:
    """Return a content-free intake report; never echo manuscript text."""
    root = require_object(payload, "intake")
    require_exact_keys(
        root,
        required={
            "schema_version",
            "review_id",
            "material",
            "authorization",
            "reviewer",
            "venue_policy",
            "ai_use",
            "handling",
            "scope",
        },
        context="intake",
    )
    schema_version = require_enum(
        root["schema_version"], {"2.0"}, "intake.schema_version"
    )
    review_id = require_identifier(root["review_id"], "intake.review_id")

    material = require_object(root["material"], "intake.material")
    require_exact_keys(
        material,
        required={"status", "contains_personal_or_sensitive_data"},
        context="intake.material",
    )
    material_status = require_enum(
        material["status"], MATERIAL_STATUSES, "intake.material.status"
    )
    sensitive = require_bool(
        material["contains_personal_or_sensitive_data"],
        "intake.material.contains_personal_or_sensitive_data",
    )

    authorization = require_object(root["authorization"], "intake.authorization")
    require_exact_keys(
        authorization,
        required={
            "basis",
            "documented",
            "local_processing_authorized",
            "external_processing_authorized",
        },
        context="intake.authorization",
    )
    authorization_basis = require_enum(
        authorization["basis"],
        AUTHORIZATION_BASES,
        "intake.authorization.basis",
    )
    authorization_documented = require_bool(
        authorization["documented"], "intake.authorization.documented"
    )
    local_authorized = require_bool(
        authorization["local_processing_authorized"],
        "intake.authorization.local_processing_authorized",
    )
    external_authorized = require_bool(
        authorization["external_processing_authorized"],
        "intake.authorization.external_processing_authorized",
    )

    reviewer = require_object(root["reviewer"], "intake.reviewer")
    require_exact_keys(
        reviewer,
        required={
            "capacity",
            "human_accountable",
            "competence_areas",
            "competence_limits",
            "conflict_status",
            "conflicts",
        },
        context="intake.reviewer",
    )
    capacity = require_enum(
        reviewer["capacity"], CAPACITIES, "intake.reviewer.capacity"
    )
    human_accountable = require_bool(
        reviewer["human_accountable"], "intake.reviewer.human_accountable"
    )
    competence_areas = require_identifier_list(
        reviewer["competence_areas"],
        "intake.reviewer.competence_areas",
        minimum=1,
    )
    competence_limits = require_text_list(
        reviewer["competence_limits"], "intake.reviewer.competence_limits"
    )
    conflict_status = require_enum(
        reviewer["conflict_status"],
        CONFLICT_STATUSES,
        "intake.reviewer.conflict_status",
    )
    conflicts = require_text_list(
        reviewer["conflicts"], "intake.reviewer.conflicts", maximum=50
    )

    venue = require_object(root["venue_policy"], "intake.venue_policy")
    require_exact_keys(
        venue,
        required={
            "checked",
            "peer_review_model",
            "confidential_editor_notes_supported",
        },
        context="intake.venue_policy",
    )
    venue_checked = require_bool(venue["checked"], "intake.venue_policy.checked")
    peer_review_model = require_enum(
        venue["peer_review_model"],
        PEER_REVIEW_MODELS,
        "intake.venue_policy.peer_review_model",
    )
    confidential_notes_supported = require_bool(
        venue["confidential_editor_notes_supported"],
        "intake.venue_policy.confidential_editor_notes_supported",
    )

    ai_use = require_object(root["ai_use"], "intake.ai_use")
    require_exact_keys(
        ai_use,
        required={
            "policy",
            "planned",
            "permission_confirmed",
            "disclosure_planned",
        },
        context="intake.ai_use",
    )
    ai_policy = require_enum(
        ai_use["policy"], AI_POLICIES, "intake.ai_use.policy"
    )
    ai_plan = require_enum(ai_use["planned"], AI_PLANS, "intake.ai_use.planned")
    ai_permission = require_bool(
        ai_use["permission_confirmed"], "intake.ai_use.permission_confirmed"
    )
    ai_disclosure = require_bool(
        ai_use["disclosure_planned"], "intake.ai_use.disclosure_planned"
    )

    handling = require_object(root["handling"], "intake.handling")
    require_exact_keys(
        handling,
        required={
            "local_only",
            "external_service_use",
            "data_reuse_permitted",
            "retention_rule",
            "deletion_or_retention_record_planned",
        },
        context="intake.handling",
    )
    local_only = require_bool(handling["local_only"], "intake.handling.local_only")
    external_service_use = require_bool(
        handling["external_service_use"],
        "intake.handling.external_service_use",
    )
    data_reuse = require_bool(
        handling["data_reuse_permitted"],
        "intake.handling.data_reuse_permitted",
    )
    retention_rule = require_enum(
        handling["retention_rule"],
        RETENTION_RULES,
        "intake.handling.retention_rule",
    )
    handling_record = require_bool(
        handling["deletion_or_retention_record_planned"],
        "intake.handling.deletion_or_retention_record_planned",
    )

    scope = require_object(root["scope"], "intake.scope")
    require_exact_keys(
        scope,
        required={
            "manuscript_type",
            "requested_focus",
            "out_of_scope",
            "specialist_review_needed",
        },
        context="intake.scope",
    )
    manuscript_type = require_identifier(
        scope["manuscript_type"], "intake.scope.manuscript_type"
    )
    requested_focus = require_identifier_list(
        scope["requested_focus"], "intake.scope.requested_focus", minimum=1
    )
    out_of_scope = require_identifier_list(
        scope["out_of_scope"], "intake.scope.out_of_scope"
    )
    specialist_review_needed = require_identifier_list(
        scope["specialist_review_needed"],
        "intake.scope.specialist_review_needed",
    )

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if not authorization_documented:
        errors.append(issue("AUTHORIZATION_NOT_DOCUMENTED", "authorization.documented"))
    if not local_authorized:
        errors.append(
            issue(
                "LOCAL_PROCESSING_NOT_AUTHORIZED",
                "authorization.local_processing_authorized",
            )
        )
    if material_status == "unpublished_confidential" and authorization_basis in {
        "public_material",
        "synthetic_training",
    }:
        errors.append(
            issue("AUTHORIZATION_BASIS_MISMATCH", "authorization.basis")
        )
    if material_status in {"public_preprint", "published"} and authorization_basis not in {
        "public_material",
        "author_request",
    }:
        warnings.append(
            issue("PUBLIC_MATERIAL_BASIS_REVIEW", "authorization.basis")
        )
    if material_status == "synthetic" and authorization_basis != "synthetic_training":
        warnings.append(
            issue("SYNTHETIC_MATERIAL_BASIS_REVIEW", "authorization.basis")
        )

    if not human_accountable:
        errors.append(
            issue("HUMAN_ACCOUNTABILITY_REQUIRED", "reviewer.human_accountable")
        )
    if conflict_status == "not_assessed":
        errors.append(issue("CONFLICTS_NOT_ASSESSED", "reviewer.conflict_status"))
    elif conflict_status == "unresolved":
        errors.append(issue("CONFLICT_UNRESOLVED", "reviewer.conflict_status"))
    elif conflict_status == "none_identified" and conflicts:
        errors.append(issue("CONFLICT_STATUS_MISMATCH", "reviewer.conflicts"))
    elif conflict_status == "disclosed_to_editor":
        warnings.append(
            issue("EDITOR_CONFLICT_CLEARANCE_REQUIRED", "reviewer.conflict_status")
        )

    if not venue_checked:
        errors.append(issue("VENUE_POLICY_NOT_CHECKED", "venue_policy.checked"))
    if peer_review_model == "unknown":
        errors.append(
            issue("PEER_REVIEW_MODEL_UNKNOWN", "venue_policy.peer_review_model")
        )
    if not confidential_notes_supported:
        warnings.append(
            issue(
                "CONFIDENTIAL_NOTES_CHANNEL_UNAVAILABLE",
                "venue_policy.confidential_editor_notes_supported",
            )
        )

    if ai_plan == "approved_ai_assistance":
        if ai_policy in {"prohibited", "not_stated"}:
            errors.append(issue("AI_POLICY_DOES_NOT_PERMIT_USE", "ai_use.policy"))
        if not ai_permission:
            errors.append(
                issue("AI_PERMISSION_NOT_CONFIRMED", "ai_use.permission_confirmed")
            )
        if not ai_disclosure:
            errors.append(
                issue("AI_DISCLOSURE_NOT_PLANNED", "ai_use.disclosure_planned")
            )
    elif ai_plan in {"none", "local_deterministic_tools"}:
        if ai_permission or ai_disclosure:
            warnings.append(issue("AI_FIELDS_REQUIRE_REVIEW", "ai_use"))

    if not local_only:
        errors.append(issue("LOCAL_ONLY_REQUIRED", "handling.local_only"))
    if external_service_use:
        errors.append(
            issue("EXTERNAL_SERVICE_NOT_SUPPORTED", "handling.external_service_use")
        )
    if external_authorized and not external_service_use:
        warnings.append(
            issue(
                "EXTERNAL_AUTHORIZATION_NOT_USED",
                "authorization.external_processing_authorized",
            )
        )
    if data_reuse:
        errors.append(issue("DATA_REUSE_PROHIBITED", "handling.data_reuse_permitted"))
    if not handling_record:
        errors.append(
            issue(
                "DELETION_OR_RETENTION_RECORD_REQUIRED",
                "handling.deletion_or_retention_record_planned",
            )
        )
    if retention_rule == "public_material" and material_status not in {
        "public_preprint",
        "published",
        "synthetic",
    }:
        errors.append(issue("RETENTION_RULE_MISMATCH", "handling.retention_rule"))
    if sensitive:
        warnings.append(
            issue(
                "MINIMUM_NECESSARY_HANDLING_REQUIRED",
                "material.contains_personal_or_sensitive_data",
            )
        )
    if competence_limits:
        warnings.append(
            issue("COMPETENCE_LIMITS_MUST_BE_DISCLOSED", "reviewer.competence_limits")
        )
    if specialist_review_needed:
        warnings.append(
            issue(
                "SPECIALIST_REVIEW_NEEDED",
                "scope.specialist_review_needed",
            )
        )

    valid = not errors
    return {
        "schema_version": schema_version,
        "review_id": review_id,
        "valid": valid,
        "status": "READY_FOR_LOCAL_REVIEW" if valid else "BLOCKED",
        "errors": errors,
        "warnings": warnings,
        "normalized_scope": {
            "capacity": capacity,
            "competence_areas": competence_areas,
            "manuscript_type": manuscript_type,
            "requested_focus": requested_focus,
            "out_of_scope": out_of_scope,
            "peer_review_model": peer_review_model,
            "ai_plan": ai_plan,
        },
        "handling_assertions": {
            "bundled_tools_are_local_only": True,
            "external_service_use_authorized_by_this_report": False,
            "data_reuse_authorized": False,
            "author_and_editor_channels_must_remain_separate": True,
        },
        "notice": (
            "This validates declared process controls only. It does not establish "
            "reviewer competence, resolve conflicts, authorize external processing, "
            "or assess manuscript quality."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a local peer-review intake JSON without reading or echoing "
            "manuscript content."
        )
    )
    parser.add_argument("intake", help="Local review intake JSON")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = validate_intake(read_json(args.intake))
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `assets/citation_references_template.csv`

```csv
reference_id,title,authors,year,doi,url,verification_status
ref-synthetic-2026,Synthetic methods note for local testing,Example Research Group,2026,,https://example.invalid/synthetic,not_verified
```

### `assets/claim_evidence_matrix_template.csv`

```csv
claim_id,location,claim_type,claim_summary,evidence_ids,support_level,alignment_issue,limitation,requested_action
CLAIM-SYN-001,Abstract:results,primary_outcome,Synthetic primary outcome claim for structural testing,FIG-SYN-001;syn-analysis-001,supported,none,,
CLAIM-SYN-002,Discussion:paragraph-2,generalization,Synthetic broad generalization claim for structural testing,TAB-SYN-001,partly_supported,population,Synthetic sample does not represent the stated target population,Narrow the claim to the studied population or provide justified external evidence
CLAIM-SYN-003,Results:paragraph-4,safety,Synthetic safety claim awaiting evidence mapping,,not_assessed,none,,Map the claim to adverse-event denominators and uncertainty before review
```

### `assets/reporting_checklist_template.csv`

```csv
guideline_id,item_id,status,location,rationale
CONSORT-2025,1,not_assessed,,
CONSORT-2025,2,not_assessed,,
CONSORT-2025,3,not_assessed,,
CONSORT-2025,4,not_assessed,,
CONSORT-2025,5,not_assessed,,
CONSORT-2025,6,not_assessed,,
CONSORT-2025,7,not_assessed,,
CONSORT-2025,8,not_assessed,,
CONSORT-2025,9,not_assessed,,
CONSORT-2025,10,not_assessed,,
CONSORT-2025,11,not_assessed,,
CONSORT-2025,12,not_assessed,,
CONSORT-2025,13,not_assessed,,
CONSORT-2025,14,not_assessed,,
CONSORT-2025,15,not_assessed,,
CONSORT-2025,16,not_assessed,,
CONSORT-2025,17,not_assessed,,
CONSORT-2025,18,not_assessed,,
CONSORT-2025,19,not_assessed,,
CONSORT-2025,20,not_assessed,,
CONSORT-2025,21,not_assessed,,
CONSORT-2025,22,not_assessed,,
CONSORT-2025,23,not_assessed,,
CONSORT-2025,24,not_assessed,,
CONSORT-2025,25,not_assessed,,
CONSORT-2025,26,not_assessed,,
CONSORT-2025,27,not_assessed,,
CONSORT-2025,28,not_assessed,,
CONSORT-2025,29,not_assessed,,
CONSORT-2025,30,not_assessed,,
```

### `assets/reporting_guidelines.json`

```json
{
  "schema_version": "2.0",
  "reviewed_on": "2026-07-23",
  "notice": "This catalog supports reporting-guideline selection only. Verify the official source, applicable extensions, and target venue policy. Checklist coverage is not a quality or merit score.",
  "guidelines": [
    {
      "id": "ARRIVE-2.0",
      "name": "ARRIVE",
      "version": "2.0 (2020)",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "animal_in_vivo"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "all"
      ],
      "main_item_count": 21,
      "url": "https://arriveguidelines.org/arrive-guidelines",
      "notes": "Use Essential 10 and Recommended Set; reporting supports appraisal but does not by itself establish rigor."
    },
    {
      "id": "CARE-2013",
      "name": "CARE",
      "version": "2013 checklist; 2017 explanation",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "case_report"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 13,
      "url": "https://www.care-statement.org/checklist",
      "notes": "Confirm informed consent and privacy requirements with the target venue and applicable law."
    },
    {
      "id": "CHEERS-2022",
      "name": "CHEERS",
      "version": "2022",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "economic_evaluation"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 28,
      "url": "https://www.ispor.org/heor-resources/good-practices/cheers",
      "notes": "For economic evaluations of health interventions; use the explanation and elaboration."
    },
    {
      "id": "CONSORT-2025",
      "name": "CONSORT",
      "version": "2025",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "randomized_trial"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health",
        "all"
      ],
      "main_item_count": 30,
      "url": "https://www.consort-spirit.org/",
      "notes": "Supersedes CONSORT 2010. Check design-specific extensions; CONSORT is not a quality assessment instrument."
    },
    {
      "id": "CONSORT-AI-2020",
      "name": "CONSORT-AI",
      "version": "2020 extension",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "randomized_trial"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [
        "ai_intervention"
      ],
      "domains": [
        "health"
      ],
      "main_item_count": null,
      "url": "https://www.equator-network.org/reporting-guidelines/consort-artificial-intelligence/",
      "notes": "Use with CONSORT 2025 for randomized trials evaluating an AI intervention; verify whether updated extension guidance applies."
    },
    {
      "id": "COREQ-2007",
      "name": "COREQ",
      "version": "2007",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "qualitative_interview",
        "qualitative_focus_group"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 32,
      "url": "https://www.equator-network.org/reporting-guidelines/coreq/",
      "notes": "For interviews and focus groups; consider SRQR for broader qualitative study designs."
    },
    {
      "id": "PRISMA-2020",
      "name": "PRISMA",
      "version": "2020 (published 2021)",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "systematic_review"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "all"
      ],
      "main_item_count": 27,
      "url": "https://www.prisma-statement.org/prisma-2020",
      "notes": "Use the relevant extension for scoping, diagnostic, individual-participant-data, or other review types. PRISMA does not assess methodological quality."
    },
    {
      "id": "PRISMA-P-2015",
      "name": "PRISMA-P",
      "version": "2015",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "systematic_review"
      ],
      "report_kinds": [
        "protocol"
      ],
      "required_features": [],
      "domains": [
        "all"
      ],
      "main_item_count": null,
      "url": "https://www.equator-network.org/reporting-guidelines/prisma-protocols/",
      "notes": "Use for systematic review protocols rather than completed review reports."
    },
    {
      "id": "SPIRIT-2025",
      "name": "SPIRIT",
      "version": "2025",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "randomized_trial"
      ],
      "report_kinds": [
        "protocol"
      ],
      "required_features": [],
      "domains": [
        "health",
        "all"
      ],
      "main_item_count": 34,
      "url": "https://www.consort-spirit.org/",
      "notes": "Supersedes SPIRIT 2013. Compare protocol, registry, statistical analysis plan, amendments, and final report for consistency."
    },
    {
      "id": "SQUIRE-2.0",
      "name": "SQUIRE",
      "version": "2.0 (2015)",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "quality_improvement"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 18,
      "url": "https://www.squire-statement.org/index.cfm?fuseaction=page.viewPage&pageID=471&nodeID=1",
      "notes": "For system-level work to improve healthcare; not every element is applicable to every manuscript."
    },
    {
      "id": "SRQR-2014",
      "name": "SRQR",
      "version": "2014",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "qualitative_study"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 21,
      "url": "https://www.equator-network.org/reporting-guidelines/srqr",
      "notes": "Broad qualitative reporting standard; choose COREQ when interviews or focus groups are the primary methods."
    },
    {
      "id": "STARD-2015",
      "name": "STARD",
      "version": "2015",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "diagnostic_accuracy"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 30,
      "url": "https://www.equator-network.org/reporting-guidelines/stard/",
      "notes": "For diagnostic accuracy studies. Use a separate risk-of-bias tool for design/conduct appraisal."
    },
    {
      "id": "STARD-AI-2025",
      "name": "STARD-AI",
      "version": "2025",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "diagnostic_accuracy"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [
        "ai_based"
      ],
      "domains": [
        "health"
      ],
      "main_item_count": 40,
      "url": "https://www.nature.com/articles/s41591-025-03953-8",
      "notes": "Use for AI-centered diagnostic accuracy studies and alongside the applicable base and modality guidance."
    },
    {
      "id": "STROBE-2007",
      "name": "STROBE",
      "version": "2007",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "observational_study",
        "cohort_study",
        "case_control_study",
        "cross_sectional_study"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 22,
      "url": "https://www.strobe-statement.org/",
      "notes": "Select the design-specific checklist and applicable extensions such as RECORD, STREGA, or STROBE-MR."
    },
    {
      "id": "TRIPOD-AI-2024",
      "name": "TRIPOD+AI",
      "version": "2024",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "prediction_model"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [],
      "domains": [
        "health"
      ],
      "main_item_count": 27,
      "url": "https://www.tripod-statement.org/",
      "notes": "Replaces TRIPOD 2015 and applies to regression or machine-learning model development and performance evaluation."
    },
    {
      "id": "TRIPOD-LLM-2025",
      "name": "TRIPOD-LLM",
      "version": "2025",
      "status": "current",
      "category": "reporting_guideline",
      "study_types": [
        "prediction_model"
      ],
      "report_kinds": [
        "results"
      ],
      "required_features": [
        "large_language_model"
      ],
      "domains": [
        "health"
      ],
      "main_item_count": 19,
      "url": "https://www.equator-network.org/reporting-guidelines/the-tripod-llm-reporting-guideline-for-studies-using-large-language-models/",
      "notes": "Use with TRIPOD+AI for studies of large language models in biomedicine and healthcare."
    },
    {
      "id": "MIAME-2001",
      "name": "MIAME",
      "version": "2001 content standard; repository guidance current",
      "status": "legacy_current_qualified",
      "category": "domain_metadata_standard",
      "study_types": [
        "microarray"
      ],
      "report_kinds": [
        "results",
        "data_release"
      ],
      "required_features": [],
      "domains": [
        "functional_genomics"
      ],
      "main_item_count": null,
      "url": "https://www.ncbi.nlm.nih.gov/geo/info/MIAME.html",
      "notes": "Retained because GEO and ArrayExpress still implement it; verify current repository submission fields."
    },
    {
      "id": "MIAPE-CURRENT",
      "name": "MIAPE",
      "version": "modular released components",
      "status": "legacy_current_qualified",
      "category": "domain_metadata_standard",
      "study_types": [
        "proteomics"
      ],
      "report_kinds": [
        "results",
        "data_release"
      ],
      "required_features": [],
      "domains": [
        "proteomics"
      ],
      "main_item_count": null,
      "url": "https://www.psidev.info/miape",
      "notes": "Select the current PSI component for the actual workflow; MIAPE is modular, not one universal checklist."
    },
    {
      "id": "MIAPPE-1.2",
      "name": "MIAPPE",
      "version": "1.2 (October 2024)",
      "status": "current",
      "category": "domain_metadata_standard",
      "study_types": [
        "plant_phenotyping"
      ],
      "report_kinds": [
        "results",
        "data_release"
      ],
      "required_features": [],
      "domains": [
        "plant_science"
      ],
      "main_item_count": null,
      "url": "https://www.miappe.org/releases",
      "notes": "Use version 1.2; version 2.0 was still under early development at the review date."
    },
    {
      "id": "MIFlowCyt-1.0",
      "name": "MIFlowCyt",
      "version": "1.0; ISAC recommendation current",
      "status": "legacy_current_qualified",
      "category": "domain_metadata_standard",
      "study_types": [
        "flow_cytometry"
      ],
      "report_kinds": [
        "results",
        "data_release"
      ],
      "required_features": [],
      "domains": [
        "cytometry"
      ],
      "main_item_count": null,
      "url": "https://isac-net.org/miflowcyt-2/",
      "notes": "Retained as an active ISAC recommendation; also verify FCS, gating, and repository requirements."
    },
    {
      "id": "MINSEQE-CURRENT",
      "name": "MINSEQE",
      "version": "repository guidance current",
      "status": "legacy_current_qualified",
      "category": "domain_metadata_standard",
      "study_types": [
        "high_throughput_sequencing"
      ],
      "report_kinds": [
        "results",
        "data_release"
      ],
      "required_features": [],
      "domains": [
        "functional_genomics"
      ],
      "main_item_count": null,
      "url": "https://www.ncbi.nlm.nih.gov/geo/info/MIAME.html",
      "notes": "Retained because GEO and ArrayExpress still implement it; verify platform-specific repository requirements."
    },
    {
      "id": "MIxS-CURRENT",
      "name": "MIxS",
      "version": "current GSC release",
      "status": "current",
      "category": "domain_metadata_standard",
      "study_types": [
        "genome_sequence",
        "metagenome_sequence"
      ],
      "report_kinds": [
        "results",
        "data_release"
      ],
      "required_features": [],
      "domains": [
        "genomics"
      ],
      "main_item_count": null,
      "url": "https://www.gensc.org/pages/standards-intro.html",
      "notes": "Use MIxS as the current umbrella; MIGS and MIMS are legacy checklists within the MIxS framework."
    }
  ]
}
```

### `assets/review_intake_template.json`

```json
{
  "schema_version": "2.0",
  "review_id": "REVIEW-LOCAL-001",
  "material": {
    "status": "unpublished_confidential",
    "contains_personal_or_sensitive_data": false
  },
  "authorization": {
    "basis": "journal_invitation",
    "documented": false,
    "local_processing_authorized": false,
    "external_processing_authorized": false
  },
  "reviewer": {
    "capacity": "assigned_reviewer",
    "human_accountable": false,
    "competence_areas": [
      "subject_matter"
    ],
    "competence_limits": [],
    "conflict_status": "not_assessed",
    "conflicts": []
  },
  "venue_policy": {
    "checked": false,
    "peer_review_model": "unknown",
    "confidential_editor_notes_supported": false
  },
  "ai_use": {
    "policy": "not_stated",
    "planned": "local_deterministic_tools",
    "permission_confirmed": false,
    "disclosure_planned": false
  },
  "handling": {
    "local_only": true,
    "external_service_use": false,
    "data_reuse_permitted": false,
    "retention_rule": "delete_after_review",
    "deletion_or_retention_record_planned": false
  },
  "scope": {
    "manuscript_type": "randomized_trial",
    "requested_focus": [
      "methods",
      "statistics",
      "reporting"
    ],
    "out_of_scope": [],
    "specialist_review_needed": []
  }
}
```

### `assets/review_scaffold_template.md`

# Peer-review working draft — {{REVIEW_ID}}

> Private working document. Human review, policy checks, and factual verification are required. Do not submit this scaffold with unresolved placeholders. Do not make or announce an editorial decision.

## Intake record

- Reviewer capacity: `{{REVIEWER_CAPACITY}}`
- Peer-review model: `{{PEER_REVIEW_MODEL}}`
- Declared processing plan: `{{AI_PLAN}}`
- Manuscript text is not embedded by the generator.
- Reconfirm conflicts, competence limits, tool use, confidentiality, and deletion or retention obligations before submission.

# Comments to authors

## Evidence-bounded summary

[Write a neutral summary of the question, design, and principal claims. Do not invent findings or imply that unperformed analyses were run.]

## Strengths

[Identify specific strengths supported by a manuscript location or supplied material.]

## Major comments

### Major comment M1

- Location: [Section, page, line, figure, table, or claim ID]
- Observation: [State what is reported, missing, inconsistent, or unsupported]
- Evidence or criterion: [Cite manuscript evidence, a method principle, venue policy, or reporting item]
- Why it matters: [Explain the consequence for validity, interpretation, reproducibility, ethics, or reporting]
- Requested action: [Request clarification, correction, analysis, evidence, or a bounded revision]

## Minor comments

### Minor comment m1

- Location: [Section, page, line, figure, table, or reference ID]
- Observation: [State the local clarity, consistency, citation, figure, or reporting issue]
- Evidence or criterion: [Identify the relevant evidence or criterion]
- Why it matters: [Explain the reader-facing consequence]
- Requested action: [Request a specific correction or clarification]

## Methods, statistics, and reproducibility

[Summarize only assessed issues. Distinguish reporting gaps from design or analysis concerns and state where specialist review is needed.]

## Ethics, transparency, figures, tables, and citations

[Record specific, evidence-backed issues. Do not allege misconduct; route credible integrity concerns through the journal process.]

## Limitations of this review

[State competence limits, unavailable materials, analyses not independently reproduced, and unresolved uncertainty.]

# Confidential comments to editor

> Keep this channel separate from comments to authors. Follow the venue policy. Do not place ordinary scientific criticism only here.

## Reviewer disclosures

- Conflicts and editor clearance: [State the disclosed status without unnecessary personal detail]
- Competence limits or specialist review needed: [State areas]
- Assistance or tools used and required disclosure: [State policy-compliant details]
- Confidentiality or retention issue: [State any unresolved process concern]

## Editorial-process or integrity concerns

[Describe only substantiated process, ethics, confidentiality, or integrity concerns and their evidence locations. Avoid accusations and avoid an editorial outcome.]

### `assets/source_ledger.csv`

```csv
source_id,organization,title,version_or_date,source_type,url,verified_on,status,notes
SRC-COPE-ETHICS,COPE,Ethical Guidelines for Peer Reviewers,Version 2 September 2017,ethical guideline,https://publicationethics.org/guidance/guideline/ethical-guidelines-peer-reviewers,2026-07-23,current_official,"Core duties for competence, conflicts, confidentiality, timeliness, conduct, and bounded requests"
SRC-COPE-PEER,COPE,Peer review core practice and resources,Current page; first posted 2018,core practice,https://publicationethics.org/news-opinion/peer-review,2026-07-23,current_official,Use with the detailed ethical guideline and current target-journal policy
SRC-ICMJE-REVIEW,ICMJE,Responsibilities in the Submission and Peer-Review Process,Current 2026 recommendations,professional recommendation,https://www.icmje.org/recommendations/browse/roles-and-responsibilities/responsibilities-in-the-submission-and-peer-peview-process.html,2026-07-23,current_official,"Confidentiality, deletion, assistance disclosure, conflicts, constructive review, and editor responsibility"
SRC-ICMJE-AI,ICMJE,Use of AI by Reviewers,Current 2026 recommendations,professional recommendation,https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-reviewers.html,2026-07-23,current_official,"Follow journal policy, request permission, preserve confidentiality, disclose use, and validate output"
SRC-EQUATOR,EQUATOR Network,Library for health research reporting,Current database,reporting-guideline registry,https://www.equator-network.org/,2026-07-23,current_official,Primary registry for selecting study-type-specific health reporting guidance
SRC-EQUATOR-SELECT,EQUATOR Network,Selecting the appropriate reporting guideline for your article,Current toolkit,selection guidance,https://www.equator-network.org/toolkits/selecting-the-appropriate-reporting-guideline,2026-07-23,current_official,Selection aid for authors editors and peer reviewers
SRC-CONSORT-2025,CONSORT-SPIRIT Group,CONSORT 2025 statement: updated guideline for reporting randomised trials,Published 2025-04-14,primary guideline,https://www.bmj.com/content/389/bmj-2024-081123,2026-07-23,current_primary,"Thirty main items; supersedes 2010; explicitly not a quality assessment instrument"
SRC-SPIRIT-2025,CONSORT-SPIRIT Group,SPIRIT 2025 statement: updated guideline for protocols of randomised trials,Published 2025-04-28,primary guideline,https://www.bmj.com/content/389/bmj-2024-081477,2026-07-23,current_primary,Thirty-four main items; supersedes SPIRIT 2013
SRC-PRISMA-2020,PRISMA Group,PRISMA 2020,2020 statement published 2021,official guideline site,https://www.prisma-statement.org/prisma-2020,2026-07-23,current_official,"Statement, expanded checklist, abstract checklist, and flow diagrams"
SRC-PRISMA-QUALITY,PRISMA Group,The PRISMA 2020 statement: an updated guideline for reporting systematic reviews,Published 2021-03-29,primary guideline,https://www.bmj.com/content/372/bmj.n71,2026-07-23,current_primary,Explicitly not intended to assess conduct or methodological quality
SRC-STROBE,STROBE Initiative,Strengthening the Reporting of Observational Studies in Epidemiology,2007 statement; current site,official guideline site,https://www.strobe-statement.org/,2026-07-23,current_official,"Use design-specific checklist and applicable extensions"
SRC-STARD-2015,EQUATOR Network / STARD Group,STARD 2015: updated list for diagnostic accuracy studies,2015,registry record and primary links,https://www.equator-network.org/reporting-guidelines/stard/,2026-07-23,current_official,Thirty main reporting items for diagnostic accuracy studies
SRC-STARD-QUALITY,EQUATOR Network / STARD Group,STARD reporting guideline applicability guidance,STARD 2015 v1.1,implementation guidance,https://resources.equator-network.org/reporting-guidelines/stard,2026-07-23,current_official,Explicitly separates reporting assessment from design-quality appraisal
SRC-STARD-AI,STARD-AI Steering Committee,The STARD-AI reporting guideline for diagnostic accuracy studies using artificial intelligence,Published 2025-09-15,primary guideline,https://www.nature.com/articles/s41591-025-03953-8,2026-07-23,current_primary,Forty items for AI-centered diagnostic accuracy studies
SRC-TRIPOD-AI,TRIPOD Group,TRIPOD+AI statement: updated guidance for clinical prediction models,Published 2024-04-16; corrected 2024-04-18,primary guideline,https://www.bmj.com/content/385/bmj-2023-078378,2026-07-23,current_primary,"Twenty-seven items; replaces TRIPOD 2015 for regression and machine-learning prediction models"
SRC-CARE,CARE Group,CARE Checklist,2013 checklist; 2017 explanation,official guideline site,https://www.care-statement.org/checklist,2026-07-23,current_official,Case reports including patient perspective and informed consent
SRC-ARRIVE,NC3Rs / ARRIVE Group,The ARRIVE Guidelines 2.0,Published 2020,official guideline site,https://arriveguidelines.org/arrive-guidelines,2026-07-23,current_official,Essential 10 plus Recommended Set for in vivo animal research
SRC-SQUIRE,SQUIRE Group,SQUIRE 2.0 Guidelines,Published 2015,official guideline site,https://www.squire-statement.org/index.cfm?fuseaction=page.viewPage&pageID=471&nodeID=1,2026-07-23,current_official,Quality-improvement reporting; not every element applies to every manuscript
SRC-CHEERS,ISPOR,CHEERS 2022,Published 2022,official guideline site,https://www.ispor.org/heor-resources/good-practices/cheers,2026-07-23,current_official,Replaces 2013 guidance for health economic evaluations
SRC-SAMPL,EQUATOR Network / Lang and Altman,SAMPL guidelines for statistical reporting,2013; journal article 2015,statistical reporting guidance,https://www.equator-network.org/2013/02/11/sampl-guidelines-for-statistical-reporting/,2026-07-23,current_guidance,Succinct biomedical statistical reporting guidance for authors editors and reviewers
SRC-ASA-PVALUE,American Statistical Association,Statement on Statistical Significance and P-Values,Released 2016-03-07,statistical principle statement,https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf,2026-07-23,current_official,Do not base conclusions on thresholds alone; report transparently and distinguish effect size from significance
SRC-NIH-RIGOR,National Institutes of Health,Guidance: Rigor and Reproducibility in Grant Applications,Current page updated 2024-10-16,funder guidance,https://grants.nih.gov/policy-and-compliance/policy-topics/reproducibility/guidance,2026-07-23,current_official,"Rigor of prior research, robust design, authentication, and transparent reporting"
SRC-ICH-E9R1,International Council for Harmonisation,ICH E9(R1) Addendum on Estimands and Sensitivity Analysis in Clinical Trials,Step 4 2019; effective 2020,statistical guidance,https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf,2026-07-23,current_official,Trial estimands missing data and sensitivity analysis; use only when applicable
SRC-MIAME-MINSEQE,NCBI GEO,MIAME and MINSEQE guidelines,Page last modified 2026-07-08,repository implementation guidance,https://www.ncbi.nlm.nih.gov/geo/info/MIAME.html,2026-07-23,current_qualified,GEO still implements both standards; verify current repository submission fields
SRC-MIAPE,HUPO Proteomics Standards Initiative,MIAPE reporting guidelines for proteomics,Current page updated 2024-01-16,domain metadata standard,https://www.psidev.info/miape,2026-07-23,current_qualified,Modular released components have separate versions; select the component matching the workflow
SRC-MIFLOWCYT,International Society for Advancement of Cytometry,MIFlowCyt,Version 1.0; current ISAC recommendation,domain metadata standard,https://isac-net.org/miflowcyt-2/,2026-07-23,current_qualified,Retained as active ISAC guidance for flow-cytometry experiment reporting
SRC-MIAPPE,MIAPPE Community,MIAPPE Releases,Version 1.2 October 2024,domain metadata standard,https://www.miappe.org/releases,2026-07-23,current_official,Version 2.0 remained in early development at verification date
SRC-MIXS,Genomic Standards Consortium,Minimum Information about any Sequence,Current framework,domain metadata standard,https://www.gensc.org/pages/standards-intro.html,2026-07-23,current_official,MIGS and MIMS are legacy checklists within the current MIxS umbrella
SRC-NATURE-POLICY,Nature Portfolio,Peer Review,Current policy at verification,journal policy example,https://www.nature.com/nature-portfolio/editorial-policies/peer-review,2026-07-23,illustrative_policy,Example only; prohibits uploading manuscripts to generative AI and requests AI-use declaration
SRC-BMJ-POLICY,BMJ,AI use,Updated 2026-05-21,publisher policy example,https://authors.bmj.com/policies/ai-use,2026-07-23,illustrative_policy,Example only; protects unpublished material and requires declaration for review-language assistance
SRC-JAMA-POLICY,JAMA Network,Guidance for Authors Peer Reviewers and Editors on Use of AI Language Models and Chatbots,Published 2023-07-27,journal policy example,https://jamanetwork.com/journals/jama/fullarticle/2807956,2026-07-23,illustrative_policy,Example only; prohibits entering manuscript or review text into a chatbot and requires disclosure
```

### `assets/statistical_reproducibility_template.json`

```json
{
  "schema_version": "2.0",
  "checklist_id": "STAT-REPRO-SYNTHETIC-001",
  "study_design": "randomized_trial",
  "specialist_review": {
    "needed": "undetermined",
    "areas": [],
    "requested": false
  },
  "items": [
    {
      "id": "question.estimand_alignment",
      "category": "question",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Check alignment among the question, target quantity, design, analysis, and interpretation"
    },
    {
      "id": "design.unit_and_independence",
      "category": "design",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Identify the experimental or observational unit and assess dependence"
    },
    {
      "id": "design.sample_size_precision",
      "category": "design",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess prospective sample-size or precision justification and assumptions"
    },
    {
      "id": "design.allocation_randomization",
      "category": "design",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess sequence generation, allocation concealment, or sampling procedures as applicable"
    },
    {
      "id": "design.blinding",
      "category": "design",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess who was blinded or masked and likely consequences when blinding was infeasible"
    },
    {
      "id": "data.inclusion_exclusion",
      "category": "data",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Trace prespecified inclusion, exclusion, attrition, and analysis populations"
    },
    {
      "id": "data.missing_data",
      "category": "data",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess missingness amounts, reasons, assumptions, methods, and sensitivity analyses"
    },
    {
      "id": "data.outliers_transformations",
      "category": "data",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Check rules for exclusions, transformations, detection limits, and influential observations"
    },
    {
      "id": "analysis.prespecification",
      "category": "analysis",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Compare analyses with the protocol, registration, and statistical analysis plan"
    },
    {
      "id": "analysis.method_design_alignment",
      "category": "analysis",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess whether methods match the design, outcome type, estimand, and sampling structure"
    },
    {
      "id": "analysis.assumptions_diagnostics",
      "category": "analysis",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess model assumptions, diagnostics, robustness, and fallback analyses"
    },
    {
      "id": "analysis.multiplicity",
      "category": "analysis",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess outcome hierarchy, repeated looks, multiple comparisons, and error control"
    },
    {
      "id": "analysis.clustering_repeated_measures",
      "category": "analysis",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess clustering, pairing, repeated measures, nesting, and time dependence"
    },
    {
      "id": "results.effect_sizes_uncertainty",
      "category": "results",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Check effect estimates and compatible uncertainty intervals, not thresholded p-values alone"
    },
    {
      "id": "results.denominators_flow",
      "category": "results",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Reconcile denominators, participant or sample flow, exclusions, and analysis populations"
    },
    {
      "id": "results.complete_outcomes_harms",
      "category": "results",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Check all prespecified outcomes, null findings, adverse events, and deviations"
    },
    {
      "id": "reproducibility.data_materials_access",
      "category": "reproducibility",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess data, materials, protocol, repository, and justified access restrictions"
    },
    {
      "id": "reproducibility.code_environment_parameters",
      "category": "reproducibility",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess code, software versions, environments, seeds, parameters, and run instructions"
    },
    {
      "id": "reproducibility.provenance_versions",
      "category": "reproducibility",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Trace data provenance, transformations, versioned artifacts, and accession identifiers"
    },
    {
      "id": "ethics.approval_consent_governance",
      "category": "ethics",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Assess approvals, consent, welfare, privacy, governance, and conflicts as applicable"
    },
    {
      "id": "interpretation.claim_evidence_causality",
      "category": "interpretation",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Check claim strength against design, evidence, uncertainty, alternatives, and generalizability"
    },
    {
      "id": "integrity.deviations_selective_reporting",
      "category": "integrity",
      "applicability": "applicable",
      "status": "not_assessed",
      "evidence_locations": [],
      "note": "",
      "requested_action": "Check unexplained deviations, outcome switching, selective reporting, and internal inconsistencies"
    }
  ]
}
```

### `assets/study_profile_template.json`

```json
{
  "schema_version": "2.0",
  "profile_id": "PROFILE-SYNTHETIC-RCT",
  "study_types": [
    "randomized_trial"
  ],
  "report_kind": "results",
  "features": [],
  "domains": [
    "health"
  ]
}
```
