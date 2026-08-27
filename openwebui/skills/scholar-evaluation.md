---
name: scholar-evaluation
description: Provide qualitative-first, evidence-traceable developmental review of scholarly works and audit low-stakes research-assessment rubrics with optional local quality controls. Never use for ranking people or consequential decisions.
---

# Scholar Evaluation

## Purpose

Provide developmental, evidence-traceable feedback on a **scholarly work**:
paper, draft, protocol, literature synthesis, or research idea. Use
qualitative judgment first. Optional scores only describe how submitted
evidence maps to a predeclared bounded rubric.

This skill also audits whether a low-stakes assessment process documents its
construct, provenance, rater quality, uncertainty, traceability, sensitivity,
fairness, accessibility, privacy, and human governance.

## Hard safety boundary

Never use this skill to automate, recommend, materially influence, or score:

- hiring, promotion, or tenure;
- admissions;
- grants or other funding;
- prizes, honors, or awards;
- discipline, dismissal, or sanctions; or
- any other high-impact personnel decision.

Never rank people. Never reduce a person to a composite score. Never infer
ability, character, integrity, protected traits, future performance, or worth.
A nominal human-in-the-loop does not remove this boundary.

If asked for a prohibited use, stop. Offer developmental comments on a
scholarly work or a process-only audit that does not process applications,
compare people, recommend an outcome, or advise a decision.

Do not issue publication-readiness, accept/reject, or “top-tier” judgments.

Read `references/responsible_assessment.md` before any organizational use.

## ScholarEval status

The referenced ScholarEval project is an **experimental
literature-grounded research-idea evaluation framework**, not validated
psychometrics.

The verified primary record is Moussa et al., *ScholarEval: Research Idea
Evaluation Grounded in Literature*, arXiv:2510.16234v2, revised 2026-02-28.
It reports a retrieval-augmented soundness/contribution framework, a
117-idea four-discipline dataset, coverage experiments, and a user study.

Do not generalize those results to person assessment, consequential decisions,
all disciplines, or this skill's rubric. No peer-reviewed publication status
was verified during the dated review. See `references/source_ledger.md`.

## Metric and prestige policy

Do not score or infer quality from:

- Journal Impact Factor or other journal measures;
- h-index, publication counts, or citation counts;
- altmetrics or attention;
- journal, conference, venue, institution, employer, or geographic prestige;
- author affiliation, reputation, network, or career path.

The rubric validator rejects common proxy-measure criteria.

If a qualified reviewer mentions an indicator descriptively outside the
scoring tools, record its exact purpose, source, coverage, field and time
effects, uncertainty, missingness, biases, gaming risk, and why it does not
directly measure quality. Never hide indicators inside an opaque composite.

## Data boundary

Bundled scripts accept only strict local JSON/CSV containing pseudonymous IDs,
bounded ratings, statuses, uncertainty, and local references.

Do not put raw private applications, CVs, letters, reviewer identities,
contact details, protected attributes, or source-document text in inputs,
outputs, logs, examples, or prompts. Keep source content in the authorized
records system and use opaque local references.

Allowed classifications are:

- `synthetic`
- `public_scholarly_work`
- `deidentified_low_stakes`

No script searches the web, loads environment files, reads credentials, calls a
model, executes supplied text, deserializes executable objects, or launches a
process.

Use Bash only to invoke the documented local `python3` commands.

## Workflow

### 1. Confirm allowed use and authorization

Record:

- developmental purpose;
- unit of assessment: `scholarly_work`;
- work type, stage, discipline, language, and audience;
- authorized source location and data classification;
- accountable committee owner;
- conflicts and recusals;
- accessibility and accommodation process;
- appeal or correction route; and
- data purpose, access, retention, and deletion.

Stop on a prohibited decision context or unnecessary private data.

### 2. Define the construct before criteria

State:

- what quality or support is being examined;
- excluded constructs;
- intended interpretation;
- contexts where the interpretation does not travel;
- evidence requirements; and
- known limitations.

Start with values and disciplinary context, not available metrics.

### 3. Adapt and validate the rubric

Begin with `assets/rubric_template.json`, then obtain qualified disciplinary,
assessment-methods, stakeholder, accessibility, privacy, and fairness review.

The template deliberately records content validity as `not_established`.
Do not change that status without documented evidence for the exact intended
use.

Validate structure:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_rubric.py \
  --rubric assets/rubric_template.json
```

Read `references/evaluation_framework.md` for construct, anchor, validity, and
rater guidance.

### 4. Build traceable evidence records

Reviewers may read an authorized work outside the scripts. Record only stable
local locators and claim references in
`assets/evidence_manifest_template.json`.

For every criterion, distinguish:

- observed evidence from interpretation;
- supporting from contrary evidence;
- available from unavailable evidence;
- `missing` from `not_applicable`; and
- uncertainty from absence.

Failure to find prior work does not prove novelty.

### 5. Rate independently

Use `assets/evaluation_template.json`. Each criterion must be:

- `rated` with an anchor score, bounded uncertainty, evidence IDs, and a local
  rationale reference;
- `missing` with null score/uncertainty and a rationale reference; or
- `not_applicable` with null score/uncertainty and a rationale reference.

Do not encode missing or not-applicable as zero. Raters should train, calibrate,
disclose conflicts, rate independently, and document disagreement.

### 6. Run local quality checks

Bounded scoring, without labels or recommendation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/calculate_scores.py \
  --rubric assets/rubric_template.json \
  --evaluation assets/evaluation_template.json
```

Evidence traceability:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_traceability.py \
  --rubric assets/rubric_template.json \
  --evaluation assets/evaluation_template.json \
  --evidence assets/evidence_manifest_template.json
```

Inter-rater agreement:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/summarize_agreement.py \
  --rubric assets/rubric_template.json \
  --ratings assets/ratings_template.csv
```

Weight sensitivity requires two or more distinct scholarly-work evaluation
files:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/weight_sensitivity.py \
  --rubric assets/rubric_template.json \
  --evaluation /tmp/work-a-evaluation.json \
  --evaluation /tmp/work-b-evaluation.json
```

Process controls:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_process.py \
  --process assets/process_checklist_template.json
```

The checklist template is intentionally unconfirmed and fails closed.
Instructions and exact schemas are in `references/local_tooling.md`.

### 7. Synthesize qualitative findings

Lead with criterion-level evidence, not the composite. For each criterion:

1. cite evidence references;
2. state `rated`, `missing`, or `not_applicable`;
3. explain the anchor interpretation;
4. report score and uncertainty only if rated;
5. note disagreements and context;
6. identify strengths and limitations; and
7. offer non-prescriptive improvement options.

Generate an empty-reference scaffold if useful:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_report_scaffold.py \
  --rubric assets/rubric_template.json \
  --evaluation assets/evaluation_template.json \
  --output /tmp/developmental-report-scaffold.json
```

The scaffold does not read source documents or draft findings.

### 8. Human review and release

Before releasing an organizational report, a qualified accountable human
committee must verify:

- construct and rubric provenance;
- content-validity evidence and limits;
- rater training, agreement, inter-rater reliability evidence, and drift;
- evidence traceability and source access;
- missingness, not-applicable rationales, and uncertainty;
- weight sensitivity and order instability;
- disciplinary and subgroup bias review;
- conflicts and recusals;
- accessibility and accommodations;
- privacy, minimization, retention, and output controls; and
- correction or appeal information.

Document dissent. Do not imply consensus, validity, or precision beyond the
evidence. Periodically evaluate the evaluation and retire harmful criteria.

## Interpretation rules

- A score is an ordinal rubric summary, not a natural measurement.
- Normalization does not repair incomplete evidence.
- The bundled uncertainty range is not a confidence interval.
- Agreement does not establish reliability, validity, fairness, or correctness.
- Stable results under tested weights do not establish validity.
- The overall score never overrides criterion evidence or qualified judgment.
- No output is a decision recommendation.

## Bundled resources

- `references/responsible_assessment.md` — safety, metrics, governance,
  accessibility, privacy, and bias.
- `references/evaluation_framework.md` — ScholarEval boundary, construct,
  criteria, anchors, validity, and interpretation.
- `references/local_tooling.md` — strict schemas, formulas, commands, and
  output behavior.
- `references/source_ledger.md` — authoritative sources and publication-status
  verification dated 2026-07-23.
- `references/security_validation.md` — baseline remediation, validation, and
  residual security-scan record.
- `assets/rubric_template.json` — bounded rubric template.
- `assets/evaluation_template.json` — rating template.
- `assets/evidence_manifest_template.json` — traceability template.
- `assets/process_checklist_template.json` — fail-closed process checklist.
- `assets/ratings_template.csv` — synthetic agreement data.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/scholar-evaluation/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/evaluation_framework.md`

# Evaluation Framework

## What ScholarEval is—and is not

The paper currently referenced by this skill is Moussa et al.,
[*ScholarEval: Research Idea Evaluation Grounded in
Literature*](https://arxiv.org/abs/2510.16234), arXiv:2510.16234v2,
revised 2026-02-28.

The preprint describes an experimental retrieval-augmented system for evaluating
research ideas on:

- **soundness:** whether existing literature empirically supports proposed
  methods; and
- **contribution:** how an idea advances beyond prior work along comparison
  dimensions.

It reports a 117-idea, four-discipline dataset, coverage comparisons with
expert-annotated review points, and a user study. Those studies evaluate that
framework. They do **not** validate the generalized rubric in this skill as a
psychometric instrument, establish stable score meaning across disciplines, or
authorize use in consequential decisions.

As of the dated source review, arXiv and the official project repository were
the verified primary publication records. No peer-reviewed publication status
was verified. Cite it as an arXiv preprint unless a later primary record is
checked. See `references/source_ledger.md`.

## Relationship to this skill

This skill borrows the useful discipline of:

1. defining what is being assessed;
2. grounding judgments in traceable literature and work evidence;
3. separating soundness-like questions from contribution-like questions; and
4. auditing whether generated feedback covers expert concerns.

It does not reproduce ScholarEval's model pipeline, prompts, retrieval system,
dataset, or reported metrics. The bundled scripts do not call ScholarEval,
search the web, invoke a model, or evaluate private documents.

The template is a **locally governed developmental rubric**. Its default
construct is:

> Traceable support for a scholarly work's claims and methods: the degree to
> which a work states a bounded question, situates its contribution, uses
> fit-for-purpose methods, aligns analysis with claims, and documents
> transparent and responsible practices using traceable evidence.

This construct must be reviewed and adapted by relevant disciplinary experts.

## Five template criteria

### 1. Question and scope

Review:

- a clear, bounded question or objective;
- significance rationale appropriate to the field and work stage;
- assumptions, boundary conditions, and success conditions; and
- feasibility of the proposed or reported scope.

Do not treat fashionable topics, institutional affiliation, or venue
expectations as evidence of significance.

### 2. Literature grounding and contribution claim

Review:

- source-selection or search boundaries;
- engagement with relevant and contrary evidence;
- traceable primary sources for comparison claims;
- comparison dimensions used to define the contribution; and
- limits on novelty or advancement claims.

Failure to find prior work does not establish novelty. Search coverage varies by
database, language, date, indexing, terminology, discipline, and access.

### 3. Method and design fit

Review:

- alignment between question, design, data or materials, and method;
- sampling, corpus, inclusion, exclusion, and measurement choices;
- alternatives and design rationale;
- validity threats, bias, and mitigation;
- ethics, consent, privacy, safety, and governance; and
- detail sufficient for appropriate checking or reproduction.

Use discipline-specific reporting and methods standards. Do not reward
complexity for its own sake.

### 4. Analysis, claims, and uncertainty

Review:

- fit of analytical methods to data and inferential target;
- assumptions and diagnostics;
- robustness, sensitivity, negative cases, and alternative explanations;
- appropriate statistical or qualitative uncertainty;
- alignment between results and claims; and
- explicit limits on generalization and causal language.

The rubric's `uncertainty` value is a rater-supplied bounded judgment range. It
is not a sampling confidence interval, posterior interval, or standard error.

### 5. Transparency, integrity, and reproducibility

Review:

- complete reporting, provenance, and stable evidence locators;
- protocols, registrations, data, code, materials, and justified restrictions;
- negative, null, and contradictory findings where relevant;
- conflicts, limitations, corrections, and research-integrity safeguards;
- accessible communication; and
- transparent attribution of contributions.

Open practice is not an absolute requirement when privacy, consent, safety,
security, Indigenous data governance, commercial constraints, or other
legitimate restrictions apply. Assess whether restrictions are justified and
whether safe access or metadata alternatives are provided.

## Scale semantics

The template uses an ordinal 0–4 scale:

- **0 — no assessable evidence**
- **1 — limited support**
- **2 — mixed support**
- **3 — substantial support**
- **4 — strong support**

These are evidence anchors, not labels of a person or universal levels of
research quality. The rubric defines criterion-specific anchors. Raters must use
the anchor text, not intuition about what a number “usually means.”

Do not convert the score to:

- accept/reject or publication readiness;
- exceptional/poor labels;
- predicted success or impact;
- person ranking; or
- funding, hiring, promotion, tenure, admissions, award, or discipline advice.

## Rating statuses

Each criterion has exactly one status:

- `rated`: score, uncertainty, evidence identifiers, and rationale reference
  are required;
- `missing`: evidence needed for assessment is absent or unavailable; score and
  uncertainty are null; or
- `not_applicable`: the criterion does not apply to this work under a documented
  rationale; score and uncertainty are null.

Do not encode missing or not-applicable as zero.

## Transparent score math

For rated criteria \(R\), score \(s_i\), and predeclared weight \(w_i\):

\[
\text{descriptive score}
=
\frac{\sum_{i \in R} w_i s_i}
     {\sum_{i \in R} w_i}
\]

The score report separately provides:

- total, applicable, rated, missing, and not-applicable weight;
- coverage of applicable weight;
- each weighted contribution;
- the normalized descriptive score; and
- a bounded aggregation of criterion uncertainty ranges.

The uncertainty aggregation is not a confidence interval. Normalization does
not make incomplete evaluations comparable. Review missingness before looking
at any score.

## Rubric development record

Before replacing `content_validity_status: not_established`, document:

1. the exact discipline, work type, language, stage, and intended use;
2. construct definition and excluded constructs;
3. literature and standard review used to draft criteria;
4. disciplinary expert and stakeholder selection;
5. systematic mapping of criteria to construct components;
6. cognitive interviews or rater response-process evidence;
7. accessibility and translation review;
8. pilot sample and evidence-availability analysis;
9. revisions, dissent, unresolved gaps, and approval; and
10. the limits of any validity claim.

Rubric provenance must identify the version, owner role, source identifiers,
review date, and content-evidence reference.

## Rater protocol

At minimum:

1. select qualified raters with relevant disciplinary and methods expertise;
2. disclose conflicts and recuse where required;
3. train on construct boundaries, anchors, evidence rules, missingness,
   accessibility, bias, and privacy;
4. calibrate on synthetic or authorized examples;
5. rate independently before discussion;
6. record evidence identifiers and uncertainty;
7. summarize agreement and investigate systematic disagreements;
8. resolve only through documented evidence and rationale, not forced averaging;
9. monitor drift over time; and
10. retrain, revise, or suspend the rubric when evidence warrants.

The bundled agreement script reports exact agreement, within-one-step agreement,
and mean absolute difference. Those summaries do not replace a
design-appropriate reliability analysis. The rubric therefore separately
records `inter_rater_reliability_status` and
`inter_rater_reliability_ref`; the template leaves reliability not established.

## Evidence traceability

Each rated criterion must point to one or more entries in the evidence manifest.
Each entry records:

- pseudonymous evidence identifier;
- linked criterion identifiers;
- source type;
- local stable locator;
- local claim reference;
- access status; and
- verification status.

Never place an excerpt or raw private document in the manifest. Keep source
content in the authorized source system.

## Weight sensitivity and order instability

Weights are value judgments. Predeclare and justify them. Run
`scripts/weight_sensitivity.py` before interpreting a composite.

The script increases and decreases one weight at a time and renormalizes the
weights. It reports score ranges and whether pairwise ordinal relationships
among scholarly works change. Instability is evidence that an apparent order
depends on contestable weights.

The output must not be used to rank people or decide a high-impact outcome.
Even stable ordering does not establish validity.

## Interpretation template

For each criterion, qualified reviewers should record:

1. status and evidence references;
2. observed evidence;
3. interpretation against the anchor;
4. score and uncertainty, if rated;
5. missing or not-applicable rationale;
6. disciplinary and stage context;
7. strengths and limitations; and
8. non-prescriptive improvement options.

Conclude with construct, provenance, coverage, agreement, sensitivity, bias,
privacy, accessibility, and validity limitations—not a decision recommendation.

### `references/local_tooling.md`

# Local Deterministic Tooling

## Security properties

Every bundled script:

- uses only the Python standard library;
- reads bounded local `.json` or `.csv` files;
- rejects symbolic-link inputs, duplicate JSON keys, excessive depth or size,
  non-finite numbers, unknown schema fields, and common private-application
  fields;
- uses fixed schemas and never executes supplied text;
- has no network, model, credential, environment-file, dynamic-code,
  executable-serialization, or child-process behavior;
- writes only minimized JSON reports and refuses to overwrite by default; and
- does not copy evidence excerpts or raw source documents.

Inputs are limited to 2 MiB, JSON depth 20, 25,000 structure nodes, 50 rubric
criteria, 50 comparison evaluations, and 20,000 agreement rows. Outputs are
limited to 2 MiB.

Use an authorized local directory. Keep private source documents in the
institution's records system and reference them with opaque local identifiers.

## Templates

- `assets/rubric_template.json` — valid structure, but deliberately records
  content validity as not established.
- `assets/evaluation_template.json` — structurally valid all-missing example.
- `assets/evidence_manifest_template.json` — synthetic local-reference records.
- `assets/process_checklist_template.json` — fail-closed unconfirmed controls.
- `assets/ratings_template.csv` — pseudonymous synthetic agreement data.

Copy a template into an authorized working directory before editing it. Do not
replace synthetic identifiers with names or contact information.

## 1. Rubric schema validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_rubric.py \
  --rubric assets/rubric_template.json
```

The validator checks:

- fixed intended use and scholarly-work unit;
- complete prohibited-use list;
- construct, boundaries, limitations, and provenance;
- content-validity status and reference;
- bounded scale and complete anchors;
- unique criteria and weights summing to one;
- absence of common scored proxy measures;
- required rater training, calibration, agreement, separately recorded
  inter-rater reliability status, and drift controls; and
- committee, conflict, appeal, accessibility, data-protection, subgroup, and
  review-cycle governance.

A rubric can be structurally `valid` while warning that content validity is not
documented. Structural validity is not psychometric validity.

## 2. Bounded descriptive scoring

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/calculate_scores.py \
  --rubric assets/rubric_template.json \
  --evaluation assets/evaluation_template.json \
  --output /tmp/scholar-score.json
```

The evaluation contains one entry for every criterion:

```json
{
  "criterion_id": "method_design",
  "status": "rated",
  "score": 3,
  "uncertainty": 0.5,
  "evidence_ids": ["EVIDENCE-SYNTHETIC-METHOD"],
  "rationale_ref": "LOCAL-RATING-RATIONALE-METHOD"
}
```

For `missing` or `not_applicable`, `score` and `uncertainty` must be null and
`evidence_ids` must be empty. A local rationale reference remains required.

The output reports weighted contributions, coverage, missing and
not-applicable weight, normalized score, and a bounded uncertainty range. It
contains no quality label, threshold, decision, or recommendation.

## 3. Evidence traceability

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_traceability.py \
  --rubric assets/rubric_template.json \
  --evaluation assets/evaluation_template.json \
  --evidence assets/evidence_manifest_template.json
```

The checker verifies that:

- manifest, evaluation, work, and classification identifiers match;
- every evidence identifier is unique;
- every rated evidence reference resolves;
- evidence is linked to the criterion that cites it;
- source and access types are allowed; and
- evidence is available and verified.

It reports identifiers, paths, and counts only. It never opens or copies the
referenced source.

## 4. Weight sensitivity and rank instability

Provide two to 50 evaluation JSON files for distinct scholarly works:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/weight_sensitivity.py \
  --rubric assets/rubric_template.json \
  --evaluation /tmp/work-a-evaluation.json \
  --evaluation /tmp/work-b-evaluation.json \
  --delta 0.2 \
  --output /tmp/weight-sensitivity.json
```

For each criterion, the script multiplies its weight by `1-delta` and
`1+delta`, renormalizes all weights to one, and recomputes descriptive scores.
It reports:

- every scenario and its exact weights;
- each work's score and coverage per scenario;
- score ranges;
- base ordinal order; and
- pairwise order changes.

The base order is included solely to detect instability. It is not a ranking
recommendation and must never be used for people or high-impact decisions.

## 5. Inter-rater agreement summaries

The CSV header must be exactly:

```text
evaluation_id,work_id,rater_id,criterion_id,status,score
```

Use pseudonymous rater identifiers. Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/summarize_agreement.py \
  --rubric assets/rubric_template.json \
  --ratings assets/ratings_template.csv \
  --output /tmp/agreement-summary.json
```

For each criterion and overall, the report includes:

- pair observations;
- exact agreement rate;
- within-one-scale-step agreement rate;
- mean absolute difference;
- overlap, rated, missing, and not-applicable counts.

Rater identifiers are not emitted. These are descriptive agreement summaries,
not chance-corrected reliability, generalizability, validity, or fairness
evidence.

## 6. Bias and process checklist

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_process.py \
  --process assets/process_checklist_template.json
```

The template is intentionally unconfirmed and therefore does not pass. Complete
it only from documented local records. The checker covers:

- qualified committee and training;
- conflicts and recusal;
- appeal and correction;
- accessibility and accommodations;
- purpose limitation, minimization, access, retention, and output controls;
- construct, provenance, content evidence, rater quality, agreement,
  inter-rater reliability review, uncertainty, missingness, traceability, and
  sensitivity;
- stakeholder, disciplinary, subgroup, and protected-attribute safeguards;
- no automation, person ranking, or decision recommendation; and
- drift, unintended-consequence, and periodic review.

`high_impact_use: true` or any unconfirmed decision control blocks the process.
The checklist does not authorize a prohibited use.

## 7. Report scaffold

Generate a minimized scaffold:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_report_scaffold.py \
  --rubric assets/rubric_template.json \
  --evaluation assets/evaluation_template.json \
  --output /tmp/developmental-report-scaffold.json
```

Optional companion reports:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_report_scaffold.py \
  --rubric assets/rubric_template.json \
  --evaluation /tmp/work-a-evaluation.json \
  --traceability /tmp/traceability.json \
  --agreement /tmp/agreement-summary.json \
  --sensitivity /tmp/weight-sensitivity.json \
  --process /tmp/process-check.json \
  --output /tmp/developmental-report-scaffold.json
```

The scaffold includes:

- construct and provenance status;
- descriptive scores and uncertainty;
- empty local-reference slots for evidence, strengths, limitations, and
  improvement options;
- minimized quality-assurance statuses; and
- fixed limitations and human-review fields.

It does not draft findings from source documents or issue a decision.

## Exit behavior

- exit `0`: requested calculation or validation completed successfully;
- exit `2`: invalid, blocked, incomplete, failed traceability, or unsafe input.

Errors contain only stable codes and JSON paths, never supplied values. Use
`--force` only when replacing a known local report.

### `references/responsible_assessment.md`

# Responsible Assessment and Safety Boundary

## Non-negotiable boundary

This skill is for **developmental review of scholarly works** and for auditing a
low-stakes assessment process. It must not automate, recommend, materially
influence, or provide a score for:

- hiring, promotion, or tenure;
- admissions;
- grant or other funding decisions;
- prizes, honors, or awards;
- discipline, dismissal, or sanctions; or
- any other high-impact personnel decision.

Do not rank people. Do not convert several judgments into a single composite
person score. Do not infer a person's ability, character, integrity, future
performance, protected characteristics, or institutional worth.

This boundary remains in force when a human is nominally “in the loop.”
Checklists, committees, or disclaimers do not make a prohibited workflow safe.
If a request crosses the boundary, stop and offer one of these alternatives:

1. developmental comments on a public or authorized scholarly work, with no
   person comparison or decision advice;
2. an audit of whether an existing assessment process follows responsible
   assessment principles, without processing applications or recommending an
   outcome; or
3. neutral documentation of criteria for review by the organization's legal,
   privacy, accessibility, labor, ethics, and disciplinary experts.

## Allowed scope

Examples of allowed uses, subject to authorization and data protection:

- feedback on a draft paper, protocol, research idea, or literature synthesis;
- a retrospective methods or reporting review;
- calibration exercises using synthetic or public scholarly works;
- checking evidence traceability;
- describing the sensitivity of work-level scores to rubric weights; and
- auditing a low-stakes evaluation design for missing governance controls.

“Publication readiness” and “accept/reject” recommendations are excluded.
Describe evidence, limitations, and improvement options instead.

## Accountable human process

For any organizational use, an accountable committee must own the process. It
must include relevant disciplinary and assessment-methods expertise and must:

- publish the construct, intended use, rubric, weights, evidence requirements,
  and interpretation limits before reviewing;
- record member qualifications, training, calibration, and drift checks;
- disclose conflicts, require recusal, and maintain a conflict record;
- provide an understandable notice and a meaningful appeal or correction route;
- provide accessible materials and reasonable accommodations;
- define lawful purpose, access controls, minimization, retention, and deletion;
- review disciplinary, language, career-path, disability, and subgroup effects;
- document disagreements and uncertainty rather than force consensus; and
- periodically evaluate and revise the evaluation.

No script in this skill is the accountable reviewer. Script output is a
descriptive record for qualified human interpretation.

## Qualitative-first evidence

Start with the values and construct, not the data that happen to be available.
Use evidence that directly bears on the criterion:

- the work's questions, methods, analyses, outputs, limitations, and provenance;
- datasets, software, protocols, materials, registrations, replications, and
  negative or null findings where relevant;
- transparent records of responsible practices and justified restrictions;
- contribution records, including CRediT roles when useful, without treating a
  role as proof of quality; and
- influence on policy, practice, communities, teaching, infrastructure, or
  knowledge, when this is within the stated construct and supported by evidence.

Ask what is missing, inaccessible, contested, or not applicable. A missing item
is not a zero. A not-applicable item is not evidence of deficiency.

## Prohibited proxies and contextual indicators

Do not score or infer quality from:

- Journal Impact Factor or other journal-level measures;
- h-index, i10-index, publication counts, or citation counts;
- altmetrics or attention counts;
- journal, conference, institutional, geographic, or employer prestige;
- venue identity or ranking; or
- author affiliation, career path, network, or reputation.

The bundled rubric validator rejects common proxy-measure criteria.

If a qualified reviewer has a legitimate, predeclared reason to mention a
quantitative indicator descriptively outside the bundled scoring tools, record:

1. the exact construct and purpose;
2. why the indicator bears on that construct at the correct unit of analysis;
3. source, version, query date, coverage, exclusions, and data quality;
4. field, language, output-type, career-stage, and time-window effects;
5. uncertainty, missingness, gaming risks, and known biases;
6. why qualitative evidence is insufficient by itself; and
7. a statement that the indicator is not a direct measure of quality.

Never use an indicator merely because it is available. Never hide several
different indicators inside an opaque composite.

## Rubric evidence and psychometric caution

A rubric is a measurement claim. Before operational use, record:

- **construct:** what is and is not being assessed;
- **intended interpretation and use:** the exact meaning claimed for scores;
- **provenance:** who designed and approved criteria, anchors, and weights;
- **content evidence:** disciplinary expert and stakeholder review of coverage;
- **response process:** how raters interpret anchors and use evidence;
- **rater protocol:** selection, training, calibration, qualification, and drift;
- **agreement/reliability:** a design-appropriate analysis and its uncertainty;
- **fairness:** accessibility, subgroup, language, and disciplinary review;
- **traceability:** stable evidence references for each rating;
- **missing/not applicable:** explicit statuses and rationales;
- **weight sensitivity:** whether plausible weights change descriptive results;
- **consequences:** gaming, burden, goal displacement, and other effects; and
- **revision:** review date, owner, change record, and retirement criteria.

Do not call a rubric “validated” because experts reviewed it once, raters agreed,
or scores correlated with another judgment. Validity concerns the evidence for a
specific interpretation and use. Reliability or agreement alone is not validity.

The provided rubric explicitly records `content_validity_status` as
`not_established`. Replace that status only when a qualified team has documented
appropriate evidence for the exact discipline, population, language, and use.

## Bias and subgroup review

Perform the fairness review outside these scripts in an authorized environment.
Do not place protected-attribute records in rubric, evaluation, evidence, or
ratings files.

A qualified review should examine, where lawful and appropriate:

- access to the measured construct and accommodation effectiveness;
- differential missingness and evidence availability;
- criteria that privilege particular languages, methods, fields, institutions,
  career patterns, or resource levels;
- rater severity, drift, and disagreement patterns;
- differential effects of weights and not-applicable decisions;
- false precision and threshold effects;
- burden, gaming, and chilling of collaboration or risky research; and
- whether the evaluation should be redesigned or stopped.

Report sample limitations and uncertainty. Do not expose small cells or attempt
to infer sensitive characteristics.

## Privacy and data protection

Use only public scholarly works, synthetic records, or deidentified low-stakes
records processed under an approved local purpose. Do not put raw private
applications, CVs, recommendation letters, reviewer identities, contact
details, protected attributes, or source-document text into tool inputs or
outputs.

The bundled formats contain only:

- pseudonymous work, evaluation, rater, criterion, and evidence identifiers;
- bounded scores, statuses, and uncertainty;
- local stable references; and
- minimized control attestations and aggregate summaries.

Keep source documents in the authorized records system. Use local references to
them. Apply least privilege, retention limits, deletion, incident handling, and
any stricter local law or policy.

## Accessibility

Provide the rubric, evidence requirements, notices, feedback, and appeal
process in accessible formats. Do not penalize an accommodation, assistive
technology, language variant, or accessible presentation choice. Confirm that
the rubric measures the intended construct rather than fluency with an
inaccessible interface or format.

## Communicating results

Lead with qualitative, traceable findings. For every criterion:

1. cite local evidence references;
2. state the rating status;
3. distinguish observed evidence from interpretation;
4. report uncertainty and disagreement;
5. state missing or not-applicable evidence;
6. explain context and limitations; and
7. offer non-prescriptive improvement options.

Do not label a person, declare a work “top-tier,” predict success, recommend a
decision, or conceal uncertainty behind a decimal.

### `references/security_validation.md`

# Security Validation Record

Validation date: **2026-07-23**

## Baseline

The repository `SECURITY.md` entry recorded **10 findings** with maximum
severity **CRITICAL**:

- four CRITICAL cross-file, environment, and network-exfiltration findings;
- three MEDIUM credential, prompt, and environment-harvesting findings; and
- three LOW cross-skill, command, and resource-use findings.

The affected files were the two former schematic-generation scripts and the
old `SKILL.md`.

## Remediation

- Deleted both schematic-generation scripts.
- Removed all network requests, API-key handling, environment access,
  environment-file loading, third-party model behavior, image handling,
  child-process execution, cross-skill invocation, and mandatory figure
  instructions.
- Replaced the former recommendation-producing score calculator with bounded,
  transparent descriptive rubric math.
- Added a strict prohibition on automated or assisted hiring, promotion,
  tenure, admissions, funding, awards, discipline, person ranking, and other
  high-impact personnel decisions.
- Added qualitative-first metric and prestige safeguards.
- Added construct, provenance, content-evidence, rater, agreement, uncertainty,
  missingness, not-applicable, traceability, sensitivity, subgroup, conflict,
  appeal, accessibility, privacy, and accountable-human controls.
- Added dependency-free, bounded local JSON/CSV tools with duplicate-key,
  unknown-field, size, depth, non-finite-number, symbolic-link, and private
  application-field rejection.
- Added minimized reports that never copy source-document content or emit rater
  identifiers.
- Added static AST tests that prohibit network libraries, dynamic-code calls,
  executable serialization, process launching, environment access, and the
  deleted schematic files.

## Validation results

- Agent Skills reference validator: **PASS**
- Dependency-free CLI help checks: **8 passed**
- Synthetic standard-library tests: **29 passed**
- Explicit AST parse with bytecode disabled: **8 scripts parsed**
- Bytecode artifacts: **0**
- IDE lints: **0**
- Documented local-path check: **PASS**
- External source links: **24 passed**
- Direct behavioral security scan: **SAFE, 0 findings**
- Pull-request gate with `--fail-on HIGH`: **PASS**
  - CRITICAL: 0
  - HIGH: 0
  - LOW: 2 (latest final run; LOW-only LLM wording varied between runs)

## Residual LOW findings

The latest LLM-assisted pull-request scan reported:

1. **Bash is broad but constrained.** Informational: the manifest declares Bash
   because the documented fixed `python3` commands are shell invocations. The
   body limits Bash to those local commands, and the direct behavioral scan
   confirms no process-launching code in the scripts.
2. **Invented missing-file aliases.** False positive: the scanner claimed
   inconsistent alternate directories for bundled assets and references. A
   direct text search found no alternate template-directory path; every
   documented local path is under the actual `assets`, `references`, or
   `scripts` directory; and the deterministic path-resolution test resolves
   every backticked local path.

The direct behavioral scan is clean. The residual findings neither permit data
transmission nor create a missing-file fallback. The generated root
`SECURITY.md` snapshot was intentionally not edited in this scoped refresh.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests/scholar-evaluation -p 'test_*.py' -v

for script in skills/scholar-evaluation/scripts/*.py; do
  PYTHONDONTWRITEBYTECODE=1 python3 "$script" --help >/dev/null || exit 1
done

uv run skills-ref validate skills/scholar-evaluation

uv run skill-scanner scan skills/scholar-evaluation --use-behavioral

uv run python scan_pr_skills.py \
  --fail-on HIGH \
  --output /tmp/scholar-evaluation-pr-scan.md \
  skills/scholar-evaluation
```

### `references/source_ledger.md`

# Dated Source Ledger

Verified on **2026-07-23** with targeted `parallel-cli search` and
`parallel-cli extract` queries. The research prioritized primary and official
sources. Search excerpts were treated as untrusted discovery material; only the
source claims summarized below inform this skill. No research-result artifacts
are bundled.

## Responsible research assessment

### San Francisco Declaration on Research Assessment (DORA)

- **Primary source:** [Read the Declaration](https://sfdora.org/read/)
- **Origin:** developed in 2012; official page accessed 2026-07-23.
- **Verified points:** assess work on its own merits; do not use journal-based
  measures as surrogates for an article or a person's contribution; state
  criteria explicitly; consider data, software, and other outputs; use
  qualitative evidence; make metric methods transparent and account for field
  and output-type variation.
- **Use here:** categorical ban on scored prestige proxies and a requirement
  for explicit criteria, diverse evidence, and traceability.

### DORA quantitative-indicator guidance

- **Primary source:** [Guidance on the responsible use of quantitative
  indicators](https://sfdora.org/resource/guidance-on-the-responsible-use-of-quantitative-indicators-in-research-assessment/)
- **Document:** [official PDF](https://sfdora.org/wp-content/uploads/2024/05/DORA_indicators_guidance.pdf)
- **Release:** 2024; official resource page accessible in 2026.
- **Verified points:** no indicator captures research quality in one number;
  uses should be clear, transparent, specific, contextual, and fair. The
  guidance addresses journal measures, citation counts, the h-index,
  field-normalized indicators, and altmetrics; it warns about reductive,
  aggregate, composite, lagging, field, career-stage, and bias effects.
- **Use here:** quantitative indicators are excluded from rubric scores. If
  mentioned descriptively outside the tools, their purpose, data, coverage,
  time window, field normalization, uncertainty, bias, and non-quality meaning
  must be explicit.

### Leiden Manifesto

- **Primary source:** Hicks, Wouters, Waltman, de Rijcke, and Rafols,
  [“Bibliometrics: The Leiden Manifesto for research
  metrics”](https://doi.org/10.1038/520429a), *Nature* 520, 429–431.
- **Published:** 2015-04-22.
- **Verified points:** quantitative evaluation should support qualitative
  expert assessment; measure against missions; protect locally relevant
  research; account for field variation; keep data and analysis open and
  verifiable; allow those evaluated to verify data; account for age and gender;
  avoid false precision; recognize gaming and system effects; review indicators
  regularly.
- **Use here:** contextualization, inspectability, uncertainty, fairness review,
  and periodic revision.

### Agreement on Reforming Research Assessment / CoARA

- **Primary record:** [Agreement on Reforming Research
  Assessment](https://doi.org/10.5281/zenodo.13480728), version 1.
- **Published:** 2022-07-20; Zenodo record modified 2024-08-29.
- **Current official overview:** [CoARA Agreement](https://coara.eu/agreement/the-agreement-full-text/)
- **Verified points:** recognize diverse outputs, practices, activities, roles,
  and careers; base assessment primarily on qualitative judgment with peer
  review central; use quantitative indicators responsibly; abandon
  inappropriate uses of journal- and publication-based measures, especially
  Journal Impact Factor and h-index; publish criteria; train assessors; review
  and evaluate criteria, tools, and processes.
- **Use here:** qualitative-first process, rubric provenance, rater training,
  monitoring, and no metric shortcut.

### Hong Kong Principles

- **Primary article:** Moher et al. (2020), [“The Hong Kong Principles for
  assessing researchers: Fostering research
  integrity”](https://doi.org/10.1371/journal.pbio.3000737), *PLOS Biology*
  18(7):e3000737.
- **Published:** 2020-07-16.
- **Official implementation page:** [World Conferences on Research Integrity
  Foundation](https://www.wcrif.org/guidance/hong-kong-principles)
- **Verified points:** assess responsible practices, value complete reporting,
  reward open research, acknowledge diverse research activity, and recognize
  essential work such as review and mentoring.
- **Use here:** integrity, reporting, appropriate openness, and diverse
  contribution evidence. The principles do not supply validated score weights.

### The Metric Tide and its commissioned revisit

- **Primary public-sector source:** Research England/UKRI, [*The Metric
  Tide*](https://www.ukri.org/publications/review-of-metrics-in-research-assessment-and-management/).
- **Published:** 2015-07-06.
- **Revisit:** Curry, Gadd, and Wilsdon, [*Harnessing the Metric
  Tide*](https://doi.org/10.6084/m9.figshare.21701624).
- **Posted:** 2022-12-12; commissioned by the joint UK higher-education funding
  bodies for the Future Research Assessment Programme.
- **Verified points:** the revisit recommends putting principles into practice,
  evaluating with those evaluated, avoiding all-metric approaches, using data
  for public benefit, and rethinking rankings.
- **Status limitation:** *Harnessing the Metric Tide* describes itself as an
  independent input to deliberations, not the eventual policy conclusion.
- **Use here:** stakeholder participation, no all-metric process, and explicit
  scrutiny of rankings and system effects.

### Current UKRI guidance

- **Primary policy:** [UKRI funding assessment and decision-making policy and
  principles](https://www.ukri.org/publications/ukri-principles-of-assessment-and-decision-making/uk-research-and-innovation-ukri-funding-assessment-and-decision-making-policy-and-principles)
- **Primary implementation guidance:** [Résumé for Research and Innovation
  (R4RI)](https://www.ukri.org/apply-for-funding/develop-your-application/resume-for-research-and-innovation-r4ri-guidance/)
- **R4RI last updated:** 2026-04-30.
- **Verified points:** UKRI will not use journal-based measures as surrogates
  for article quality, individual contribution, or funding decisions. R4RI
  evidences a wider range of team contributions; assessors do not score its
  individual modules or view it in isolation.
- **Use here:** diverse contribution evidence and contextual review. This skill
  nevertheless blocks funding decisions entirely; the UKRI material is
  guidance context, not authorization to support such decisions.

### UNESCO Recommendation on Open Science

- **Primary source:** [UNESCO Recommendation on Open
  Science](https://unesdoc.unesco.org/ark:/48223/pf0000379949).
- **Adopted:** 2021-11-23 by the UNESCO General Conference.
- **Official overview:** [UNESCO Open Science](https://www.unesco.org/en/open-science/about)
- **Verified points:** quality and integrity, collective benefit, equity,
  fairness, diversity, inclusion, open engagement, training, and incentives
  aligned with open science; open science must not leave people, languages,
  disciplines, or knowledge systems behind.
- **Use here:** assess responsible openness in context. Privacy, safety,
  consent, sovereignty, and legitimate restrictions can outweigh openness.

### INORMS SCOPE framework

- **Primary source:** [SCOPE Framework full guide,
  v1.0](https://inorms.net/wp-content/uploads/2022/03/21655-scope-guide-v10.pdf).
- **Current official page:** [INORMS SCOPE Framework for Research
  Evaluation](https://inorms.net/scope-framework-for-research-evaluation).
- **Verified points:** Start with values; consider Context; identify Options;
  Probe for discrimination, gaming, unintended effects, and cost-benefit; and
  Evaluate the evaluation. Evaluate only where needed, with those evaluated,
  and with evaluation expertise.
- **Use here:** process design and the bias/process checklist.

### CRediT contributor taxonomy

- **Primary source:** [CRediT](https://credit.niso.org/).
- **Standard:** ANSI/NISO Z39.104-2022, approved 2022-01-14 and published
  2022-02-08.
- **Verified points:** 14 roles provide transparent attribution of diverse
  contributions. CRediT does not determine authorship or contribution quality.
- **Use here:** optional vocabulary for contribution evidence, never a score.

## Measurement, fairness, accessibility, and privacy

### Standards for Educational and Psychological Testing

- **Primary source:** AERA, APA, and NCME, [*Standards for Educational and
  Psychological Testing*, 2014
  edition](https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf).
- **Official status page:** [APA Testing Standards](https://www.apa.org/science/programs/testing/standards).
- **Status:** the 2014 edition is open access; the sponsoring organizations
  announced a revision process. No later completed edition was verified.
- **Verified points:** intended interpretations and uses require validity
  evidence; reliability/precision and relevant errors should be reported;
  rater selection, training, qualification, monitoring, agreement, accuracy,
  and drift need documentation; fairness and subgroup validity require
  evidence; uncertainty should accompany estimates.
- **Use here:** these are measurement principles, not proof that this rubric is
  a psychological test. The template records evidence gaps and must not be
  described as validated psychometrics.

### Accessibility

- **Primary source:** W3C, [Web Content Accessibility Guidelines
  2.2](https://www.w3.org/TR/WCAG22/).
- **Status:** W3C Recommendation published 2023-10-05; update noted
  2024-12-12.
- **Use here:** accessible materials and reasonable accommodation processes
  are required; local legal and institutional requirements may be broader.

### Data protection

- **Primary guidance:** UK Information Commissioner's Office,
  [purpose limitation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/purpose-limitation)
  and [data minimisation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation).
- **Current guidance dates found:** purpose limitation updated 2026-03-23;
  data minimisation page published 2025-09-09.
- **Verified points:** specify legitimate purposes and process only adequate,
  relevant, necessary data; review and delete data no longer needed.
- **Use here:** scripts accept only minimized IDs, scores, statuses, and local
  references. They reject common private-application fields and never reproduce
  raw source documents.

## ScholarEval paper and project status

- **Exact paper:** Hanane Nour Moussa, Patrick Queiroz Da Silva, Daniel
  Adu-Ampratwum, Alyson East, Zitong Lu, Nikki Puccetti, Mingyi Xue, Huan Sun,
  Bodhisattwa Prasad Majumder, and Sachin Kumar, [*ScholarEval: Research Idea
  Evaluation Grounded in Literature*](https://arxiv.org/abs/2510.16234).
- **Verified status:** arXiv:2510.16234, submitted 2025-10-17; latest verified
  version **v2**, revised 2026-02-28. The displayed DOI
  `10.48550/arXiv.2510.16234` is an arXiv/DataCite DOI, not evidence of journal
  publication.
- **Official project:** [skai-research/ScholarEval](https://github.com/skai-research/ScholarEval).
  The repository describes itself as official code and data and cites the work
  as `@misc`; no release or peer-reviewed publication claim was verified.
- **Review-status caution:** a public OpenReview forum for the title was
  discoverable, but the official page's decision/status was not accessible or
  exposed in indexed primary-source text during this refresh. It is therefore
  not used as evidence of acceptance or peer review.
- **What the preprint reports:** a retrieval-augmented framework assessing
  research ideas for soundness and contribution; a 117-idea, four-discipline
  dataset; coverage comparisons against expert-annotated review points; and a
  user study.
- **What it does not establish:** validated psychometric measurement of
  scholar quality, transportability to personnel or funding decisions, validity
  of this skill's generalized rubric, stable cross-discipline score meaning, or
  freedom from subgroup bias.

## Review cadence

Re-check this ledger before any rubric adoption and at least annually. Re-check
the ScholarEval arXiv and official project records before describing its
publication status. Record any local disciplinary standards separately; a
global source cannot substitute for local construct validation.

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Bounded, dependency-free helpers for local scholar-evaluation records."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = "2.0"
NOTICE = (
    "DESCRIPTIVE DEVELOPMENTAL ASSESSMENT ONLY — NOT A DECISION "
    "RECOMMENDATION — QUALIFIED HUMAN REVIEW REQUIRED"
)
PROHIBITED_USES = {
    "admissions",
    "awards",
    "discipline",
    "funding",
    "hiring",
    "promotion",
    "tenure",
    "other_high_impact_personnel_decision",
}
ALLOWED_PURPOSE = "developmental_review_of_scholarly_work"
ALLOWED_UNIT = "scholarly_work"
ALLOWED_CLASSIFICATIONS = {
    "synthetic",
    "public_scholarly_work",
    "deidentified_low_stakes",
}
RATING_STATUSES = {"rated", "missing", "not_applicable"}

MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
MAX_TEXT_CHARS = 4_000
MAX_LIST_ITEMS = 1_000
MAX_OBJECT_FIELDS = 100
MAX_DEPTH = 20
MAX_TOTAL_NODES = 25_000
MAX_CRITERIA = 50
MAX_EVALUATIONS = 50
MAX_CSV_ROWS = 20_000

IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{1,95}$")
PRIVATE_FIELD_KEYS = {
    "applicant_name",
    "application_text",
    "candidate_name",
    "cv_text",
    "date_of_birth",
    "dob",
    "document_text",
    "email",
    "full_name",
    "home_address",
    "person_name",
    "phone",
    "private_application",
    "raw_application",
    "resume_text",
    "social_security_number",
    "ssn",
}
PROXY_TERMS = (
    "journal impact factor",
    "impact factor",
    "h-index",
    "h index",
    "citation count",
    "altmetric",
    "conference ranking",
    "journal ranking",
    "institution prestige",
    "journal prestige",
    "venue prestige",
    "university ranking",
)


class ValidationError(ValueError):
    """A deterministic input failure that never includes a supplied value."""

    def __init__(self, code: str, path: str = "$") -> None:
        super().__init__(code)
        self.code = code
        self.path = path


@dataclass(frozen=True)
class Issue:
    """A minimized validation issue."""

    code: str
    path: str
    level: str = "error"

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "level": self.level}


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def _check_local_file(path: Path, suffix: str) -> None:
    if path.suffix.lower() != suffix:
        raise ValidationError("INPUT_SUFFIX_NOT_ALLOWED")
    if not path.exists():
        raise ValidationError("INPUT_NOT_FOUND")
    if path.is_symlink():
        raise ValidationError("INPUT_SYMLINK_NOT_ALLOWED")
    if not path.is_file():
        raise ValidationError("INPUT_NOT_REGULAR_FILE")
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ValidationError("INPUT_TOO_LARGE")


def _scan_structure(value: Any, path: str = "$") -> None:
    nodes = 0
    stack: list[tuple[Any, str, int]] = [(value, path, 0)]
    while stack:
        current, current_path, depth = stack.pop()
        nodes += 1
        if nodes > MAX_TOTAL_NODES:
            raise ValidationError("STRUCTURE_TOO_LARGE", current_path)
        if depth > MAX_DEPTH:
            raise ValidationError("STRUCTURE_TOO_DEEP", current_path)
        if isinstance(current, dict):
            if len(current) > MAX_OBJECT_FIELDS:
                raise ValidationError("OBJECT_TOO_LARGE", current_path)
            for key, child in current.items():
                if not isinstance(key, str):
                    raise ValidationError("OBJECT_KEY_NOT_TEXT", current_path)
                normalized = key.strip().lower()
                if normalized in PRIVATE_FIELD_KEYS:
                    raise ValidationError("PRIVATE_FIELD_NOT_ALLOWED", f"{current_path}.{key}")
                stack.append((child, f"{current_path}.{key}", depth + 1))
        elif isinstance(current, list):
            if len(current) > MAX_LIST_ITEMS:
                raise ValidationError("LIST_TOO_LARGE", current_path)
            for index, child in enumerate(current):
                stack.append((child, f"{current_path}[{index}]", depth + 1))
        elif isinstance(current, str) and len(current) > MAX_TEXT_CHARS:
            raise ValidationError("TEXT_TOO_LONG", current_path)
        elif current is not None and not isinstance(
            current, (str, int, float, bool)
        ):
            raise ValidationError("VALUE_TYPE_NOT_ALLOWED", current_path)
        if isinstance(current, float) and not math.isfinite(current):
            raise ValidationError("NUMBER_NOT_FINITE", current_path)


def read_json(path: Path | str) -> Any:
    """Read bounded JSON with duplicate-key and private-field rejection."""

    local_path = Path(path)
    _check_local_file(local_path, ".json")
    try:
        data = json.loads(
            local_path.read_text(encoding="utf-8"),
            object_pairs_hook=_pairs_no_duplicates,
        )
    except UnicodeDecodeError as error:
        raise ValidationError("INPUT_NOT_UTF8") from error
    except json.JSONDecodeError as error:
        raise ValidationError("JSON_INVALID") from error
    _scan_structure(data)
    return data


def read_csv_text(path: Path | str) -> str:
    """Read a bounded UTF-8 CSV file after local-path checks."""

    local_path = Path(path)
    _check_local_file(local_path, ".csv")
    try:
        return local_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValidationError("INPUT_NOT_UTF8") from error


def write_json(
    value: dict[str, Any], output: Path | None, *, force: bool = False
) -> None:
    """Write deterministic JSON locally or print it to standard output."""

    rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if len(rendered.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise ValidationError("OUTPUT_TOO_LARGE")
    if output is None:
        print(rendered, end="")
        return
    if output.suffix.lower() != ".json":
        raise ValidationError("OUTPUT_SUFFIX_NOT_ALLOWED")
    if output.is_symlink():
        raise ValidationError("OUTPUT_SYMLINK_NOT_ALLOWED")
    if output.exists() and not force:
        raise ValidationError("OUTPUT_EXISTS")
    if not output.parent.exists() or not output.parent.is_dir():
        raise ValidationError("OUTPUT_PARENT_NOT_FOUND")
    output.write_text(rendered, encoding="utf-8")


def failure_report(error: ValidationError) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "error",
        "issues": [Issue(error.code, error.path).as_dict()],
    }


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTIFIER_RE.fullmatch(value))


def is_nonempty_text(value: Any, maximum: int = MAX_TEXT_CHARS) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= maximum


def is_reference(value: Any) -> bool:
    if not is_nonempty_text(value, 500):
        return False
    lowered = value.strip().lower()
    return not (
        lowered.startswith(("http://", "https://", "file://"))
        or "\n" in value
        or "\r" in value
    )


def is_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return len(value) == 10


def exact_keys(
    value: Any,
    expected: Iterable[str],
    path: str,
    issues: list[Issue],
) -> bool:
    if not isinstance(value, dict):
        issues.append(Issue("SCHEMA_OBJECT_REQUIRED", path))
        return False
    expected_set = set(expected)
    actual_set = set(value)
    for missing in sorted(expected_set - actual_set):
        issues.append(Issue("SCHEMA_REQUIRED_FIELD", f"{path}.{missing}"))
    for unknown in sorted(actual_set - expected_set):
        issues.append(Issue("SCHEMA_UNKNOWN_FIELD", f"{path}.{unknown}"))
    return not (expected_set - actual_set)


def validate_identifier(
    value: Any, path: str, issues: list[Issue], code: str = "IDENTIFIER_INVALID"
) -> None:
    if not is_identifier(value):
        issues.append(Issue(code, path))


def validate_reference(
    value: Any, path: str, issues: list[Issue], *, allow_empty: bool = False
) -> None:
    if allow_empty and value == "":
        return
    if not is_reference(value):
        issues.append(Issue("LOCAL_REFERENCE_INVALID", path))


def validate_text(
    value: Any, path: str, issues: list[Issue], *, allow_empty: bool = False
) -> None:
    if allow_empty and value == "":
        return
    if not is_nonempty_text(value):
        issues.append(Issue("TEXT_INVALID", path))


def validate_bool(value: Any, path: str, issues: list[Issue]) -> None:
    if not isinstance(value, bool):
        issues.append(Issue("BOOLEAN_REQUIRED", path))


def validate_text_list(
    value: Any,
    path: str,
    issues: list[Issue],
    *,
    minimum: int = 0,
    maximum: int = 100,
    references: bool = False,
) -> None:
    if not isinstance(value, list):
        issues.append(Issue("LIST_REQUIRED", path))
        return
    if not minimum <= len(value) <= maximum:
        issues.append(Issue("LIST_LENGTH_INVALID", path))
    for index, item in enumerate(value):
        if references:
            validate_reference(item, f"{path}[{index}]", issues)
        else:
            validate_text(item, f"{path}[{index}]", issues)


def _validate_scale(scale: Any, issues: list[Issue]) -> tuple[float, float, float]:
    path = "$.scale"
    expected = {"minimum", "maximum", "step", "anchors"}
    if not exact_keys(scale, expected, path, issues):
        return 0.0, 0.0, 1.0
    minimum = scale.get("minimum")
    maximum = scale.get("maximum")
    step = scale.get("step")
    if not is_number(minimum) or not is_number(maximum) or not is_number(step):
        issues.append(Issue("SCALE_NUMBER_REQUIRED", path))
        return 0.0, 0.0, 1.0
    minimum_f = float(minimum)
    maximum_f = float(maximum)
    step_f = float(step)
    if minimum_f < 0 or maximum_f <= minimum_f or maximum_f - minimum_f > 10:
        issues.append(Issue("SCALE_BOUNDS_INVALID", path))
    if step_f <= 0 or step_f > maximum_f - minimum_f:
        issues.append(Issue("SCALE_STEP_INVALID", f"{path}.step"))
    anchors = scale.get("anchors")
    if not isinstance(anchors, list) or not 2 <= len(anchors) <= 21:
        issues.append(Issue("SCALE_ANCHORS_INVALID", f"{path}.anchors"))
        return minimum_f, maximum_f, step_f
    anchor_scores: list[float] = []
    for index, anchor in enumerate(anchors):
        anchor_path = f"{path}.anchors[{index}]"
        if not exact_keys(anchor, {"score", "label", "description"}, anchor_path, issues):
            continue
        score = anchor.get("score")
        if not is_number(score):
            issues.append(Issue("ANCHOR_SCORE_INVALID", f"{anchor_path}.score"))
        else:
            anchor_scores.append(float(score))
        validate_text(anchor.get("label"), f"{anchor_path}.label", issues)
        validate_text(anchor.get("description"), f"{anchor_path}.description", issues)
    if anchor_scores:
        if len(anchor_scores) != len(set(anchor_scores)):
            issues.append(Issue("ANCHOR_SCORE_DUPLICATE", f"{path}.anchors"))
        if min(anchor_scores) != minimum_f or max(anchor_scores) != maximum_f:
            issues.append(Issue("ANCHOR_BOUNDS_MISSING", f"{path}.anchors"))
    return minimum_f, maximum_f, step_f


def _validate_proxy_absence(value: Any, path: str, issues: list[Issue]) -> None:
    strings: list[str] = []
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, str):
            strings.append(current.lower())
        elif isinstance(current, list):
            stack.extend(current)
        elif isinstance(current, dict):
            stack.extend(current.values())
    combined = "\n".join(strings)
    if any(term in combined for term in PROXY_TERMS):
        issues.append(Issue("PROXY_METRIC_CRITERION_PROHIBITED", path))


def validate_rubric(rubric: Any) -> list[Issue]:
    """Validate the strict local rubric schema."""

    issues: list[Issue] = []
    top_keys = {
        "schema_version",
        "rubric_id",
        "title",
        "intended_use",
        "construct",
        "provenance",
        "scale",
        "criteria",
        "rater_protocol",
        "governance",
    }
    if not exact_keys(rubric, top_keys, "$", issues):
        return issues
    if rubric.get("schema_version") != SCHEMA_VERSION:
        issues.append(Issue("SCHEMA_VERSION_UNSUPPORTED", "$.schema_version"))
    validate_identifier(rubric.get("rubric_id"), "$.rubric_id", issues)
    validate_text(rubric.get("title"), "$.title", issues)

    intended = rubric.get("intended_use")
    if exact_keys(
        intended,
        {"purpose", "unit_of_assessment", "allowed_contexts", "prohibited_uses"},
        "$.intended_use",
        issues,
    ):
        if intended.get("purpose") != ALLOWED_PURPOSE:
            issues.append(Issue("PURPOSE_NOT_ALLOWED", "$.intended_use.purpose"))
        if intended.get("unit_of_assessment") != ALLOWED_UNIT:
            issues.append(
                Issue("UNIT_OF_ASSESSMENT_NOT_ALLOWED", "$.intended_use.unit_of_assessment")
            )
        validate_text_list(
            intended.get("allowed_contexts"),
            "$.intended_use.allowed_contexts",
            issues,
            minimum=1,
            maximum=20,
        )
        prohibited = intended.get("prohibited_uses")
        validate_text_list(
            prohibited,
            "$.intended_use.prohibited_uses",
            issues,
            minimum=len(PROHIBITED_USES),
            maximum=30,
        )
        prohibited_set = (
            set(prohibited)
            if isinstance(prohibited, list)
            and all(isinstance(item, str) for item in prohibited)
            else set()
        )
        if isinstance(prohibited, list) and not PROHIBITED_USES.issubset(
            prohibited_set
        ):
            issues.append(
                Issue("PROHIBITED_USES_INCOMPLETE", "$.intended_use.prohibited_uses")
            )

    construct = rubric.get("construct")
    if exact_keys(
        construct,
        {"label", "definition", "boundaries", "limitations"},
        "$.construct",
        issues,
    ):
        validate_text(construct.get("label"), "$.construct.label", issues)
        validate_text(construct.get("definition"), "$.construct.definition", issues)
        validate_text_list(
            construct.get("boundaries"),
            "$.construct.boundaries",
            issues,
            minimum=1,
            maximum=20,
        )
        validate_text_list(
            construct.get("limitations"),
            "$.construct.limitations",
            issues,
            minimum=1,
            maximum=20,
        )

    provenance = rubric.get("provenance")
    if exact_keys(
        provenance,
        {
            "rubric_version",
            "owner_role",
            "source_ids",
            "content_validity_status",
            "content_validity_evidence_ref",
            "last_reviewed_date",
        },
        "$.provenance",
        issues,
    ):
        validate_text(provenance.get("rubric_version"), "$.provenance.rubric_version", issues)
        validate_text(provenance.get("owner_role"), "$.provenance.owner_role", issues)
        validate_text_list(
            provenance.get("source_ids"),
            "$.provenance.source_ids",
            issues,
            minimum=1,
            maximum=50,
            references=True,
        )
        validity_status = provenance.get("content_validity_status")
        if validity_status not in {"not_established", "pilot_evidence", "documented"}:
            issues.append(
                Issue(
                    "CONTENT_VALIDITY_STATUS_INVALID",
                    "$.provenance.content_validity_status",
                )
            )
        validate_reference(
            provenance.get("content_validity_evidence_ref"),
            "$.provenance.content_validity_evidence_ref",
            issues,
            allow_empty=validity_status == "not_established",
        )
        if validity_status != "documented":
            issues.append(
                Issue(
                    "CONTENT_VALIDITY_NOT_DOCUMENTED",
                    "$.provenance.content_validity_status",
                    "warning",
                )
            )
        if not is_date(provenance.get("last_reviewed_date")):
            issues.append(Issue("DATE_INVALID", "$.provenance.last_reviewed_date"))

    scale_object = rubric.get("scale")
    minimum, maximum, step = _validate_scale(scale_object, issues)
    raw_scale_anchors = (
        scale_object.get("anchors") if isinstance(scale_object, dict) else []
    )
    if not isinstance(raw_scale_anchors, list):
        raw_scale_anchors = []
    scale_anchor_scores = {
        float(anchor["score"])
        for anchor in raw_scale_anchors
        if isinstance(anchor, dict) and is_number(anchor.get("score"))
    }

    criteria = rubric.get("criteria")
    criterion_ids: set[str] = set()
    total_weight = 0.0
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= MAX_CRITERIA:
        issues.append(Issue("CRITERIA_INVALID", "$.criteria"))
    else:
        for index, criterion in enumerate(criteria):
            path = f"$.criteria[{index}]"
            if not exact_keys(
                criterion,
                {
                    "criterion_id",
                    "label",
                    "construct_component",
                    "weight",
                    "required",
                    "anchors",
                    "evidence_requirements",
                    "limitations",
                },
                path,
                issues,
            ):
                continue
            criterion_id = criterion.get("criterion_id")
            validate_identifier(criterion_id, f"{path}.criterion_id", issues)
            if isinstance(criterion_id, str):
                if criterion_id in criterion_ids:
                    issues.append(Issue("CRITERION_ID_DUPLICATE", f"{path}.criterion_id"))
                criterion_ids.add(criterion_id)
            validate_text(criterion.get("label"), f"{path}.label", issues)
            validate_text(
                criterion.get("construct_component"),
                f"{path}.construct_component",
                issues,
            )
            validate_bool(criterion.get("required"), f"{path}.required", issues)
            weight = criterion.get("weight")
            if not is_number(weight) or not 0 < float(weight) <= 1:
                issues.append(Issue("CRITERION_WEIGHT_INVALID", f"{path}.weight"))
            else:
                total_weight += float(weight)
            validate_text_list(
                criterion.get("evidence_requirements"),
                f"{path}.evidence_requirements",
                issues,
                minimum=1,
                maximum=20,
            )
            validate_text_list(
                criterion.get("limitations"),
                f"{path}.limitations",
                issues,
                minimum=1,
                maximum=20,
            )
            anchors = criterion.get("anchors")
            criterion_anchor_scores: set[float] = set()
            if not isinstance(anchors, list) or not 2 <= len(anchors) <= 21:
                issues.append(Issue("CRITERION_ANCHORS_INVALID", f"{path}.anchors"))
            else:
                for anchor_index, anchor in enumerate(anchors):
                    anchor_path = f"{path}.anchors[{anchor_index}]"
                    if not exact_keys(
                        anchor, {"score", "description"}, anchor_path, issues
                    ):
                        continue
                    if not is_number(anchor.get("score")):
                        issues.append(
                            Issue("ANCHOR_SCORE_INVALID", f"{anchor_path}.score")
                        )
                    else:
                        criterion_anchor_scores.add(float(anchor["score"]))
                    validate_text(
                        anchor.get("description"),
                        f"{anchor_path}.description",
                        issues,
                    )
            if criterion_anchor_scores != scale_anchor_scores:
                issues.append(Issue("CRITERION_ANCHORS_INCOMPLETE", f"{path}.anchors"))
            _validate_proxy_absence(criterion, path, issues)
    if criteria and not math.isclose(total_weight, 1.0, abs_tol=1e-9):
        issues.append(Issue("CRITERION_WEIGHTS_MUST_SUM_TO_ONE", "$.criteria"))

    protocol = rubric.get("rater_protocol")
    if exact_keys(
        protocol,
        {
            "minimum_raters",
            "training_required",
            "training_ref",
            "calibration_required",
            "calibration_ref",
            "agreement_method",
            "inter_rater_reliability_status",
            "inter_rater_reliability_ref",
            "drift_monitoring_required",
            "drift_review_ref",
        },
        "$.rater_protocol",
        issues,
    ):
        minimum_raters = protocol.get("minimum_raters")
        if (
            not isinstance(minimum_raters, int)
            or isinstance(minimum_raters, bool)
            or not 2 <= minimum_raters <= 50
        ):
            issues.append(
                Issue("MINIMUM_RATERS_INVALID", "$.rater_protocol.minimum_raters")
            )
        for field in (
            "training_required",
            "calibration_required",
            "drift_monitoring_required",
        ):
            validate_bool(protocol.get(field), f"$.rater_protocol.{field}", issues)
            if protocol.get(field) is not True:
                issues.append(
                    Issue("RATER_CONTROL_MUST_BE_REQUIRED", f"$.rater_protocol.{field}")
                )
        for field in ("training_ref", "calibration_ref", "drift_review_ref"):
            validate_reference(protocol.get(field), f"$.rater_protocol.{field}", issues)
        if protocol.get("agreement_method") != (
            "exact_within_step_and_mean_absolute_difference"
        ):
            issues.append(
                Issue(
                    "AGREEMENT_METHOD_INVALID", "$.rater_protocol.agreement_method"
                )
            )
        reliability_status = protocol.get("inter_rater_reliability_status")
        if reliability_status not in {
            "not_established",
            "pilot_evidence",
            "documented",
        }:
            issues.append(
                Issue(
                    "INTER_RATER_RELIABILITY_STATUS_INVALID",
                    "$.rater_protocol.inter_rater_reliability_status",
                )
            )
        validate_reference(
            protocol.get("inter_rater_reliability_ref"),
            "$.rater_protocol.inter_rater_reliability_ref",
            issues,
            allow_empty=reliability_status == "not_established",
        )
        if reliability_status != "documented":
            issues.append(
                Issue(
                    "INTER_RATER_RELIABILITY_NOT_DOCUMENTED",
                    "$.rater_protocol.inter_rater_reliability_status",
                    "warning",
                )
            )

    governance = rubric.get("governance")
    governance_bool_fields = (
        "accountable_committee_required",
        "conflict_disclosure_required",
        "recusal_required",
        "appeal_process_required",
        "accessibility_accommodations_required",
        "data_protection_review_required",
        "subgroup_bias_review_required",
    )
    governance_ref_fields = (
        "committee_owner_role",
        "appeal_process_ref",
        "accessibility_process_ref",
        "data_protection_process_ref",
        "subgroup_review_ref",
        "review_cycle_ref",
    )
    if exact_keys(
        governance,
        set(governance_bool_fields) | set(governance_ref_fields),
        "$.governance",
        issues,
    ):
        for field in governance_bool_fields:
            validate_bool(governance.get(field), f"$.governance.{field}", issues)
            if governance.get(field) is not True:
                issues.append(
                    Issue("GOVERNANCE_CONTROL_MUST_BE_REQUIRED", f"$.governance.{field}")
                )
        for field in governance_ref_fields:
            validate_reference(governance.get(field), f"$.governance.{field}", issues)

    if maximum <= minimum or step <= 0:
        issues.append(Issue("SCALE_UNUSABLE", "$.scale"))
    return issues


def scale_values(rubric: dict[str, Any]) -> set[float]:
    return {
        float(anchor["score"])
        for anchor in rubric["scale"]["anchors"]
        if is_number(anchor["score"])
    }


def validate_evaluation(
    evaluation: Any, rubric: dict[str, Any]
) -> list[Issue]:
    """Validate one strict scholarly-work evaluation record."""

    issues: list[Issue] = []
    if not exact_keys(
        evaluation,
        {
            "schema_version",
            "evaluation_id",
            "rubric_id",
            "work_id",
            "data_classification",
            "purpose",
            "ratings",
        },
        "$",
        issues,
    ):
        return issues
    if evaluation.get("schema_version") != SCHEMA_VERSION:
        issues.append(Issue("SCHEMA_VERSION_UNSUPPORTED", "$.schema_version"))
    validate_identifier(evaluation.get("evaluation_id"), "$.evaluation_id", issues)
    validate_identifier(evaluation.get("rubric_id"), "$.rubric_id", issues)
    validate_identifier(evaluation.get("work_id"), "$.work_id", issues)
    if evaluation.get("rubric_id") != rubric.get("rubric_id"):
        issues.append(Issue("RUBRIC_ID_MISMATCH", "$.rubric_id"))
    if evaluation.get("data_classification") not in ALLOWED_CLASSIFICATIONS:
        issues.append(Issue("DATA_CLASSIFICATION_NOT_ALLOWED", "$.data_classification"))
    if evaluation.get("purpose") != ALLOWED_PURPOSE:
        issues.append(Issue("PURPOSE_NOT_ALLOWED", "$.purpose"))

    criteria = {criterion["criterion_id"]: criterion for criterion in rubric["criteria"]}
    accepted_scores = scale_values(rubric)
    maximum_uncertainty = float(rubric["scale"]["maximum"]) - float(
        rubric["scale"]["minimum"]
    )
    ratings = evaluation.get("ratings")
    seen: set[str] = set()
    if not isinstance(ratings, list) or not 1 <= len(ratings) <= MAX_CRITERIA:
        issues.append(Issue("RATINGS_INVALID", "$.ratings"))
        return issues
    for index, rating in enumerate(ratings):
        path = f"$.ratings[{index}]"
        if not exact_keys(
            rating,
            {
                "criterion_id",
                "status",
                "score",
                "uncertainty",
                "evidence_ids",
                "rationale_ref",
            },
            path,
            issues,
        ):
            continue
        criterion_id = rating.get("criterion_id")
        validate_identifier(criterion_id, f"{path}.criterion_id", issues)
        if isinstance(criterion_id, str):
            if criterion_id in seen:
                issues.append(Issue("RATING_DUPLICATE", f"{path}.criterion_id"))
            seen.add(criterion_id)
            if criterion_id not in criteria:
                issues.append(Issue("CRITERION_UNKNOWN", f"{path}.criterion_id"))
        status = rating.get("status")
        if status not in RATING_STATUSES:
            issues.append(Issue("RATING_STATUS_INVALID", f"{path}.status"))
        evidence_ids = rating.get("evidence_ids")
        if not isinstance(evidence_ids, list) or len(evidence_ids) > 100:
            issues.append(Issue("EVIDENCE_IDS_INVALID", f"{path}.evidence_ids"))
            evidence_ids = []
        else:
            hashable_evidence_ids = [
                evidence_id
                for evidence_id in evidence_ids
                if isinstance(evidence_id, str)
            ]
            if len(hashable_evidence_ids) != len(set(hashable_evidence_ids)):
                issues.append(Issue("EVIDENCE_ID_DUPLICATE", f"{path}.evidence_ids"))
            for evidence_index, evidence_id in enumerate(evidence_ids):
                validate_identifier(
                    evidence_id,
                    f"{path}.evidence_ids[{evidence_index}]",
                    issues,
                    "EVIDENCE_ID_INVALID",
                )
        validate_reference(rating.get("rationale_ref"), f"{path}.rationale_ref", issues)
        if status == "rated":
            score = rating.get("score")
            uncertainty = rating.get("uncertainty")
            if not is_number(score) or float(score) not in accepted_scores:
                issues.append(Issue("SCORE_NOT_ON_SCALE", f"{path}.score"))
            if (
                not is_number(uncertainty)
                or not 0 <= float(uncertainty) <= maximum_uncertainty
            ):
                issues.append(Issue("UNCERTAINTY_INVALID", f"{path}.uncertainty"))
            if not evidence_ids:
                issues.append(Issue("RATED_EVIDENCE_REQUIRED", f"{path}.evidence_ids"))
        elif status in {"missing", "not_applicable"}:
            if rating.get("score") is not None:
                issues.append(Issue("UNRATED_SCORE_MUST_BE_NULL", f"{path}.score"))
            if rating.get("uncertainty") is not None:
                issues.append(
                    Issue("UNRATED_UNCERTAINTY_MUST_BE_NULL", f"{path}.uncertainty")
                )
            if evidence_ids:
                issues.append(
                    Issue("UNRATED_EVIDENCE_MUST_BE_EMPTY", f"{path}.evidence_ids")
                )
    missing_criteria = set(criteria) - seen
    for criterion_id in sorted(missing_criteria):
        issues.append(Issue("CRITERION_RATING_REQUIRED", f"$.ratings.{criterion_id}"))
    return issues


def error_issues(issues: Iterable[Issue]) -> list[Issue]:
    return [issue for issue in issues if issue.level == "error"]


def require_valid(issues: Iterable[Issue]) -> None:
    errors = error_issues(issues)
    if errors:
        raise ValidationError(errors[0].code, errors[0].path)


def rounded(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 6)


def weights_by_criterion(rubric: dict[str, Any]) -> dict[str, float]:
    return {
        criterion["criterion_id"]: float(criterion["weight"])
        for criterion in rubric["criteria"]
    }


def score_evaluation(
    rubric: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Calculate bounded descriptive rubric math without a recommendation."""

    selected_weights = weights or weights_by_criterion(rubric)
    scale_minimum = float(rubric["scale"]["minimum"])
    scale_maximum = float(rubric["scale"]["maximum"])
    rating_by_id = {
        rating["criterion_id"]: rating for rating in evaluation["ratings"]
    }
    criteria_output: list[dict[str, Any]] = []
    weighted_sum = 0.0
    lower_sum = 0.0
    upper_sum = 0.0
    rated_weight = 0.0
    missing_weight = 0.0
    not_applicable_weight = 0.0
    for criterion in rubric["criteria"]:
        criterion_id = criterion["criterion_id"]
        rating = rating_by_id[criterion_id]
        weight = float(selected_weights[criterion_id])
        status = rating["status"]
        item: dict[str, Any] = {
            "criterion_id": criterion_id,
            "status": status,
            "weight": rounded(weight),
            "score": None,
            "uncertainty": None,
            "weighted_contribution": None,
            "lower_contribution": None,
            "upper_contribution": None,
        }
        if status == "rated":
            score = float(rating["score"])
            uncertainty = float(rating["uncertainty"])
            lower = max(scale_minimum, score - uncertainty)
            upper = min(scale_maximum, score + uncertainty)
            contribution = weight * score
            weighted_sum += contribution
            lower_sum += weight * lower
            upper_sum += weight * upper
            rated_weight += weight
            item.update(
                {
                    "score": rounded(score),
                    "uncertainty": rounded(uncertainty),
                    "weighted_contribution": rounded(contribution),
                    "lower_contribution": rounded(weight * lower),
                    "upper_contribution": rounded(weight * upper),
                }
            )
        elif status == "missing":
            missing_weight += weight
        else:
            not_applicable_weight += weight
        criteria_output.append(item)
    applicable_weight = rated_weight + missing_weight
    normalized = weighted_sum / rated_weight if rated_weight else None
    lower_score = lower_sum / rated_weight if rated_weight else None
    upper_score = upper_sum / rated_weight if rated_weight else None
    coverage = rated_weight / applicable_weight if applicable_weight else None
    warnings: list[str] = []
    if missing_weight > 0:
        warnings.append("MISSING_RATINGS_EXCLUDED_FROM_NORMALIZED_SCORE")
    if not_applicable_weight > 0:
        warnings.append("NOT_APPLICABLE_RATINGS_EXCLUDED")
    if coverage is None or coverage < 1.0:
        warnings.append("INCOMPLETE_APPLICABLE_COVERAGE")
    if normalized is None:
        warnings.append("NO_NORMALIZED_SCORE_AVAILABLE")
    return {
        "schema_version": SCHEMA_VERSION,
        "report_type": "bounded_descriptive_rubric_score",
        "notice": NOTICE,
        "evaluation_id": evaluation["evaluation_id"],
        "work_id": evaluation["work_id"],
        "rubric_id": rubric["rubric_id"],
        "scale": {"minimum": scale_minimum, "maximum": scale_maximum},
        "formula": (
            "normalized_score = sum(score_i * weight_i for rated criteria) "
            "/ sum(weight_i for rated criteria); missing and not_applicable "
            "criteria are reported and excluded"
        ),
        "criteria": criteria_output,
        "aggregates": {
            "total_weight": rounded(sum(selected_weights.values())),
            "applicable_weight": rounded(applicable_weight),
            "rated_weight": rounded(rated_weight),
            "missing_weight": rounded(missing_weight),
            "not_applicable_weight": rounded(not_applicable_weight),
            "coverage_of_applicable_weight": rounded(coverage),
            "weighted_sum": rounded(weighted_sum),
            "normalized_score": rounded(normalized),
            "uncertainty_interval": {
                "lower": rounded(lower_score),
                "upper": rounded(upper_score),
                "method": (
                    "weighted aggregation of criterion-level bounded uncertainty "
                    "intervals; not a confidence interval"
                ),
            },
        },
        "warnings": warnings,
        "decision_recommendation_provided": False,
    }
```

### `scripts/calculate_scores.py`

```python
#!/usr/bin/env python3
"""Calculate transparent bounded rubric math for one scholarly work."""

from __future__ import annotations

import argparse
from pathlib import Path

import _common


def calculate(rubric: dict, evaluation: dict) -> dict:
    rubric_issues = _common.validate_rubric(rubric)
    _common.require_valid(rubric_issues)
    evaluation_issues = _common.validate_evaluation(evaluation, rubric)
    _common.require_valid(evaluation_issues)
    report = _common.score_evaluation(rubric, evaluation)
    report["rubric_warnings"] = [
        issue.as_dict() for issue in rubric_issues if issue.level == "warning"
    ]
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compute bounded descriptive rubric scores with explicit missing, "
            "not-applicable, coverage, and uncertainty fields. The output never "
            "makes a decision recommendation."
        )
    )
    parser.add_argument("--rubric", required=True, type=Path, help="Local rubric JSON")
    parser.add_argument(
        "--evaluation", required=True, type=Path, help="Local evaluation JSON"
    )
    parser.add_argument("--output", type=Path, help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output JSON file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        rubric = _common.read_json(args.rubric)
        evaluation = _common.read_json(args.evaluation)
        report = calculate(rubric, evaluation)
        _common.write_json(report, args.output, force=args.force)
        return 0
    except _common.ValidationError as error:
        _common.write_json(_common.failure_report(error), None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/check_process.py`

```python
#!/usr/bin/env python3
"""Check low-stakes assessment governance and bias-process controls."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import _common

SECTION_FIELDS: dict[str, dict[str, tuple[str, ...]]] = {
    "committee": {
        "booleans": ("qualified_members_confirmed", "training_completed"),
        "references": ("accountable_owner_role", "training_record_ref"),
    },
    "conflicts": {
        "booleans": (
            "disclosure_process_confirmed",
            "recusal_process_confirmed",
        ),
        "references": ("record_ref",),
    },
    "appeals": {
        "booleans": ("process_confirmed",),
        "references": ("process_ref", "notice_ref"),
    },
    "accessibility": {
        "booleans": (
            "accommodations_process_confirmed",
            "accessible_materials_confirmed",
        ),
        "references": ("process_ref",),
    },
    "data_protection": {
        "booleans": (
            "purpose_limitation_confirmed",
            "data_minimisation_confirmed",
            "access_controls_confirmed",
            "retention_schedule_confirmed",
            "raw_private_documents_excluded_from_tool_outputs",
        ),
        "references": ("review_ref",),
    },
    "rubric_quality": {
        "booleans": (
            "construct_documented",
            "rubric_provenance_documented",
            "content_validity_documented",
            "rater_training_documented",
            "agreement_reviewed",
            "inter_rater_reliability_reviewed",
            "uncertainty_recorded",
            "missing_and_not_applicable_supported",
            "evidence_traceability_checked",
            "weight_sensitivity_reviewed",
        ),
        "references": ("quality_record_ref",),
    },
    "fairness": {
        "booleans": (
            "stakeholder_review_completed",
            "disciplinary_context_reviewed",
            "subgroup_bias_review_completed",
            "protected_attributes_excluded_from_scoring",
        ),
        "references": ("bias_review_ref",),
    },
    "decision_controls": {
        "booleans": (
            "no_automated_decision",
            "no_person_ranking",
            "no_decision_recommendation",
            "qualified_human_accountability",
        ),
        "references": (),
    },
    "monitoring": {
        "booleans": (
            "rater_drift_reviewed",
            "unintended_consequences_reviewed",
            "periodic_revision_scheduled",
        ),
        "references": ("review_record_ref", "revision_owner_role"),
    },
}


def validate_process(record: Any) -> list[_common.Issue]:
    issues: list[_common.Issue] = []
    top_fields = {
        "schema_version",
        "process_id",
        "purpose",
        "unit_of_assessment",
        "data_classification",
        "high_impact_use",
        *SECTION_FIELDS,
    }
    if not _common.exact_keys(record, top_fields, "$", issues):
        return issues
    if record.get("schema_version") != _common.SCHEMA_VERSION:
        issues.append(_common.Issue("SCHEMA_VERSION_UNSUPPORTED", "$.schema_version"))
    _common.validate_identifier(record.get("process_id"), "$.process_id", issues)
    if record.get("purpose") != _common.ALLOWED_PURPOSE:
        issues.append(_common.Issue("PURPOSE_NOT_ALLOWED", "$.purpose"))
    if record.get("unit_of_assessment") != _common.ALLOWED_UNIT:
        issues.append(
            _common.Issue(
                "UNIT_OF_ASSESSMENT_NOT_ALLOWED", "$.unit_of_assessment"
            )
        )
    if record.get("data_classification") not in _common.ALLOWED_CLASSIFICATIONS:
        issues.append(
            _common.Issue(
                "DATA_CLASSIFICATION_NOT_ALLOWED", "$.data_classification"
            )
        )
    _common.validate_bool(record.get("high_impact_use"), "$.high_impact_use", issues)
    for section_name, field_groups in SECTION_FIELDS.items():
        section = record.get(section_name)
        expected = set(field_groups["booleans"]) | set(field_groups["references"])
        if not _common.exact_keys(section, expected, f"$.{section_name}", issues):
            continue
        for field in field_groups["booleans"]:
            _common.validate_bool(
                section.get(field), f"$.{section_name}.{field}", issues
            )
        for field in field_groups["references"]:
            _common.validate_reference(
                section.get(field),
                f"$.{section_name}.{field}",
                issues,
                allow_empty=True,
            )
    return issues


def check_process(record: dict[str, Any]) -> dict[str, Any]:
    schema_issues = validate_process(record)
    if _common.error_issues(schema_issues):
        return {
            "schema_version": _common.SCHEMA_VERSION,
            "report_type": "bias_and_process_check",
            "status": "invalid",
            "process_id": record.get("process_id"),
            "issues": [issue.as_dict() for issue in schema_issues],
        }
    blockers: list[str] = []
    missing_controls: list[str] = []
    if record["high_impact_use"]:
        blockers.append("PROHIBITED_HIGH_IMPACT_USE")
    if record["purpose"] != _common.ALLOWED_PURPOSE:
        blockers.append("PROHIBITED_PURPOSE")
    if record["unit_of_assessment"] != _common.ALLOWED_UNIT:
        blockers.append("PROHIBITED_UNIT_OF_ASSESSMENT")
    for field in SECTION_FIELDS["decision_controls"]["booleans"]:
        if record["decision_controls"][field] is not True:
            blockers.append(f"DECISION_CONTROL_NOT_CONFIRMED:{field}")
    for section_name, field_groups in SECTION_FIELDS.items():
        for field in field_groups["booleans"]:
            if record[section_name][field] is not True:
                missing_controls.append(f"{section_name}.{field}")
        for field in field_groups["references"]:
            if not record[section_name][field]:
                missing_controls.append(f"{section_name}.{field}")
    status = (
        "blocked"
        if blockers
        else "incomplete"
        if missing_controls
        else "complete_for_low_stakes_process"
    )
    confirmed_count = sum(
        record[section_name][field] is True
        for section_name, groups in SECTION_FIELDS.items()
        for field in groups["booleans"]
    )
    boolean_count = sum(
        len(groups["booleans"]) for groups in SECTION_FIELDS.values()
    )
    return {
        "schema_version": _common.SCHEMA_VERSION,
        "report_type": "bias_and_process_check",
        "notice": _common.NOTICE,
        "status": status,
        "process_id": record["process_id"],
        "purpose": record["purpose"],
        "unit_of_assessment": record["unit_of_assessment"],
        "confirmed_boolean_controls": confirmed_count,
        "total_boolean_controls": boolean_count,
        "blockers": blockers,
        "missing_controls": sorted(set(missing_controls)),
        "prohibited_uses": sorted(_common.PROHIBITED_USES),
        "protected_attribute_data_processed": False,
        "decision_recommendation_provided": False,
        "issues": [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check committee, conflict, appeal, accessibility, data-protection, "
            "rubric-quality, fairness, and monitoring attestations for a "
            "low-stakes scholarly-work review process."
        )
    )
    parser.add_argument(
        "--process", required=True, type=Path, help="Local process-checklist JSON"
    )
    parser.add_argument("--output", type=Path, help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output JSON file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = check_process(_common.read_json(args.process))
        _common.write_json(report, args.output, force=args.force)
        return 0 if report["status"] == "complete_for_low_stakes_process" else 2
    except _common.ValidationError as error:
        _common.write_json(_common.failure_report(error), None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/check_traceability.py`

```python
#!/usr/bin/env python3
"""Check criterion-to-evidence traceability without copying source content."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import _common

SOURCE_TYPES = {
    "section",
    "table",
    "figure",
    "dataset",
    "code",
    "protocol",
    "registration",
    "other_local_record",
}
ACCESS_STATUSES = {"available", "restricted_authorized", "unavailable"}
VERIFICATION_STATUSES = {"verified", "unverified"}


def validate_manifest(
    manifest: Any, rubric: dict, evaluation: dict
) -> tuple[list[_common.Issue], dict[str, dict]]:
    issues: list[_common.Issue] = []
    evidence_by_id: dict[str, dict] = {}
    if not _common.exact_keys(
        manifest,
        {
            "schema_version",
            "evaluation_id",
            "work_id",
            "data_classification",
            "evidence",
        },
        "$",
        issues,
    ):
        return issues, evidence_by_id
    if manifest.get("schema_version") != _common.SCHEMA_VERSION:
        issues.append(_common.Issue("SCHEMA_VERSION_UNSUPPORTED", "$.schema_version"))
    if manifest.get("evaluation_id") != evaluation.get("evaluation_id"):
        issues.append(_common.Issue("EVALUATION_ID_MISMATCH", "$.evaluation_id"))
    if manifest.get("work_id") != evaluation.get("work_id"):
        issues.append(_common.Issue("WORK_ID_MISMATCH", "$.work_id"))
    if manifest.get("data_classification") != evaluation.get("data_classification"):
        issues.append(
            _common.Issue("DATA_CLASSIFICATION_MISMATCH", "$.data_classification")
        )
    if manifest.get("data_classification") not in _common.ALLOWED_CLASSIFICATIONS:
        issues.append(
            _common.Issue(
                "DATA_CLASSIFICATION_NOT_ALLOWED", "$.data_classification"
            )
        )
    criterion_ids = {criterion["criterion_id"] for criterion in rubric["criteria"]}
    evidence = manifest.get("evidence")
    if not isinstance(evidence, list) or len(evidence) > 5_000:
        issues.append(_common.Issue("EVIDENCE_LIST_INVALID", "$.evidence"))
        return issues, evidence_by_id
    for index, item in enumerate(evidence):
        path = f"$.evidence[{index}]"
        if not _common.exact_keys(
            item,
            {
                "evidence_id",
                "criterion_ids",
                "source_type",
                "locator_ref",
                "claim_ref",
                "access_status",
                "verification_status",
            },
            path,
            issues,
        ):
            continue
        evidence_id = item.get("evidence_id")
        _common.validate_identifier(
            evidence_id, f"{path}.evidence_id", issues, "EVIDENCE_ID_INVALID"
        )
        if isinstance(evidence_id, str):
            if evidence_id in evidence_by_id:
                issues.append(
                    _common.Issue("EVIDENCE_ID_DUPLICATE", f"{path}.evidence_id")
                )
            evidence_by_id[evidence_id] = item
        linked = item.get("criterion_ids")
        if not isinstance(linked, list) or not 1 <= len(linked) <= 50:
            issues.append(_common.Issue("CRITERION_IDS_INVALID", f"{path}.criterion_ids"))
        else:
            linked_text = [
                criterion_id
                for criterion_id in linked
                if isinstance(criterion_id, str)
            ]
            if len(linked_text) != len(set(linked_text)):
                issues.append(
                    _common.Issue(
                        "CRITERION_ID_DUPLICATE", f"{path}.criterion_ids"
                    )
                )
            for criterion_index, criterion_id in enumerate(linked):
                _common.validate_identifier(
                    criterion_id,
                    f"{path}.criterion_ids[{criterion_index}]",
                    issues,
                )
                if isinstance(criterion_id, str) and criterion_id not in criterion_ids:
                    issues.append(
                        _common.Issue(
                            "CRITERION_UNKNOWN",
                            f"{path}.criterion_ids[{criterion_index}]",
                        )
                    )
        if item.get("source_type") not in SOURCE_TYPES:
            issues.append(_common.Issue("SOURCE_TYPE_INVALID", f"{path}.source_type"))
        _common.validate_reference(item.get("locator_ref"), f"{path}.locator_ref", issues)
        _common.validate_reference(item.get("claim_ref"), f"{path}.claim_ref", issues)
        if item.get("access_status") not in ACCESS_STATUSES:
            issues.append(_common.Issue("ACCESS_STATUS_INVALID", f"{path}.access_status"))
        if item.get("access_status") == "unavailable":
            issues.append(_common.Issue("EVIDENCE_UNAVAILABLE", f"{path}.access_status"))
        if item.get("verification_status") not in VERIFICATION_STATUSES:
            issues.append(
                _common.Issue(
                    "VERIFICATION_STATUS_INVALID", f"{path}.verification_status"
                )
            )
        elif item.get("verification_status") != "verified":
            issues.append(
                _common.Issue("EVIDENCE_UNVERIFIED", f"{path}.verification_status")
            )
    return issues, evidence_by_id


def check_traceability(rubric: dict, evaluation: dict, manifest: dict) -> dict:
    rubric_issues = _common.validate_rubric(rubric)
    _common.require_valid(rubric_issues)
    evaluation_issues = _common.validate_evaluation(evaluation, rubric)
    _common.require_valid(evaluation_issues)
    issues, evidence_by_id = validate_manifest(manifest, rubric, evaluation)
    used_ids: set[str] = set()
    for index, rating in enumerate(evaluation["ratings"]):
        if rating["status"] != "rated":
            continue
        criterion_id = rating["criterion_id"]
        for evidence_index, evidence_id in enumerate(rating["evidence_ids"]):
            used_ids.add(evidence_id)
            path = f"$.ratings[{index}].evidence_ids[{evidence_index}]"
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                issues.append(_common.Issue("EVIDENCE_REFERENCE_UNRESOLVED", path))
            elif criterion_id not in evidence.get("criterion_ids", []):
                issues.append(_common.Issue("EVIDENCE_CRITERION_MISMATCH", path))
    for evidence_id in sorted(set(evidence_by_id) - used_ids):
        issues.append(
            _common.Issue(
                "EVIDENCE_UNUSED",
                f"$.evidence.{evidence_id}",
                "warning",
            )
        )
    errors = _common.error_issues(issues)
    rated_count = sum(
        rating["status"] == "rated" for rating in evaluation["ratings"]
    )
    resolved_count = sum(
        1
        for rating in evaluation["ratings"]
        if rating["status"] == "rated"
        and rating["evidence_ids"]
        and all(evidence_id in evidence_by_id for evidence_id in rating["evidence_ids"])
    )
    return {
        "schema_version": _common.SCHEMA_VERSION,
        "report_type": "evidence_traceability_check",
        "notice": _common.NOTICE,
        "status": "fail" if errors else "pass",
        "evaluation_id": evaluation["evaluation_id"],
        "work_id": evaluation["work_id"],
        "rated_criteria": rated_count,
        "rated_criteria_with_resolved_evidence": resolved_count,
        "evidence_records": len(evidence_by_id),
        "error_count": len(errors),
        "warning_count": len(issues) - len(errors),
        "issues": [issue.as_dict() for issue in issues],
        "source_content_copied_to_output": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify local evidence identifiers and criterion mappings. "
            "The report contains references and counts, never evidence excerpts."
        )
    )
    parser.add_argument("--rubric", required=True, type=Path, help="Local rubric JSON")
    parser.add_argument(
        "--evaluation", required=True, type=Path, help="Local evaluation JSON"
    )
    parser.add_argument(
        "--evidence", required=True, type=Path, help="Local evidence-manifest JSON"
    )
    parser.add_argument("--output", type=Path, help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output JSON file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = check_traceability(
            _common.read_json(args.rubric),
            _common.read_json(args.evaluation),
            _common.read_json(args.evidence),
        )
        _common.write_json(report, args.output, force=args.force)
        return 0 if report["status"] == "pass" else 2
    except _common.ValidationError as error:
        _common.write_json(_common.failure_report(error), None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/generate_report_scaffold.py`

```python
#!/usr/bin/env python3
"""Generate a minimized local JSON scaffold for qualified human review."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import _common


def _load_companion(
    report: dict[str, Any] | None,
    *,
    report_type: str,
    rubric_id: str | None = None,
    evaluation_id: str | None = None,
    work_id: str | None = None,
) -> dict[str, Any] | None:
    if report is None:
        return None
    if not isinstance(report, dict) or report.get("schema_version") != _common.SCHEMA_VERSION:
        raise _common.ValidationError("COMPANION_REPORT_INVALID")
    if report.get("report_type") != report_type:
        raise _common.ValidationError("COMPANION_REPORT_TYPE_MISMATCH")
    if rubric_id is not None and report.get("rubric_id") != rubric_id:
        raise _common.ValidationError("COMPANION_RUBRIC_ID_MISMATCH")
    if evaluation_id is not None and report.get("evaluation_id") != evaluation_id:
        raise _common.ValidationError("COMPANION_EVALUATION_ID_MISMATCH")
    if work_id is not None and report.get("work_id") != work_id:
        raise _common.ValidationError("COMPANION_WORK_ID_MISMATCH")
    return report


def generate_scaffold(
    rubric: dict[str, Any],
    evaluation: dict[str, Any],
    *,
    traceability: dict[str, Any] | None = None,
    agreement: dict[str, Any] | None = None,
    sensitivity: dict[str, Any] | None = None,
    process: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rubric_issues = _common.validate_rubric(rubric)
    _common.require_valid(rubric_issues)
    evaluation_issues = _common.validate_evaluation(evaluation, rubric)
    _common.require_valid(evaluation_issues)
    score_report = _common.score_evaluation(rubric, evaluation)
    traceability = _load_companion(
        traceability,
        report_type="evidence_traceability_check",
        evaluation_id=evaluation["evaluation_id"],
        work_id=evaluation["work_id"],
    )
    agreement = _load_companion(
        agreement,
        report_type="inter_rater_agreement_summary",
        rubric_id=rubric["rubric_id"],
    )
    sensitivity = _load_companion(
        sensitivity,
        report_type="weight_sensitivity_and_rank_instability",
        rubric_id=rubric["rubric_id"],
    )
    process = _load_companion(process, report_type="bias_and_process_check")
    if traceability and (
        traceability.get("status") not in {"pass", "fail"}
        or not isinstance(traceability.get("error_count"), int)
    ):
        raise _common.ValidationError("COMPANION_REPORT_INVALID")
    agreement_overall = agreement.get("overall") if agreement else None
    if agreement and (
        not isinstance(agreement_overall, dict)
        or not isinstance(agreement_overall.get("pair_observations"), int)
    ):
        raise _common.ValidationError("COMPANION_REPORT_INVALID")
    if sensitivity and not isinstance(
        sensitivity.get("rank_instability_detected"), bool
    ):
        raise _common.ValidationError("COMPANION_REPORT_INVALID")
    if process and process.get("status") not in {
        "invalid",
        "blocked",
        "incomplete",
        "complete_for_low_stakes_process",
    }:
        raise _common.ValidationError("COMPANION_REPORT_INVALID")
    criterion_scaffold = []
    for result in score_report["criteria"]:
        criterion_scaffold.append(
            {
                "criterion_id": result["criterion_id"],
                "status": result["status"],
                "score": result["score"],
                "uncertainty": result["uncertainty"],
                "evidence_finding_refs": [],
                "strength_refs": [],
                "limitation_refs": [],
                "improvement_option_refs": [],
                "qualified_reviewer_comment_ref": "",
            }
        )
    return {
        "schema_version": _common.SCHEMA_VERSION,
        "report_type": "developmental_scholarly_work_report_scaffold",
        "notice": _common.NOTICE,
        "evaluation_id": evaluation["evaluation_id"],
        "work_id": evaluation["work_id"],
        "rubric_id": rubric["rubric_id"],
        "purpose": _common.ALLOWED_PURPOSE,
        "unit_of_assessment": _common.ALLOWED_UNIT,
        "construct": {
            "rubric_record_ref": rubric["rubric_id"],
            "content_validity_status": rubric["provenance"][
                "content_validity_status"
            ],
            "rubric_source_count": len(rubric["provenance"]["source_ids"]),
        },
        "descriptive_score_summary": score_report["aggregates"],
        "criterion_scaffold": criterion_scaffold,
        "quality_assurance": {
            "traceability_status": (
                traceability.get("status") if traceability else "not_provided"
            ),
            "traceability_error_count": (
                traceability.get("error_count") if traceability else None
            ),
            "agreement_pair_observations": (
                agreement_overall.get("pair_observations") if agreement_overall else None
            ),
            "agreement_status": (
                "provided" if agreement else "not_provided"
            ),
            "inter_rater_reliability_status": rubric["rater_protocol"][
                "inter_rater_reliability_status"
            ],
            "weight_sensitivity_status": (
                "provided" if sensitivity else "not_provided"
            ),
            "rank_instability_detected": (
                sensitivity.get("rank_instability_detected")
                if sensitivity
                else None
            ),
            "process_check_status": (
                process.get("status") if process else "not_provided"
            ),
        },
        "human_review": {
            "committee_finding_refs": [],
            "conflict_and_recusal_record_ref": "",
            "disciplinary_context_ref": "",
            "accessibility_accommodation_record_ref": "",
            "subgroup_bias_review_ref": rubric["governance"][
                "subgroup_review_ref"
            ],
            "appeal_process_ref": rubric["governance"]["appeal_process_ref"],
            "final_human_review_record_ref": "",
        },
        "required_limitations": [
            "ScholarEval is an experimental literature-grounded research-idea framework, not validated psychometrics.",
            "This rubric requires separate validity, reliability, fairness, and intended-use evidence.",
            "Missing and not-applicable ratings limit comparability.",
            "Criterion uncertainty intervals are bounded judgment ranges, not confidence intervals.",
            "Journal, citation, prestige, institution, venue, and attention indicators do not establish quality.",
        ],
        "private_source_content_included": False,
        "person_ranking_provided": False,
        "decision_recommendation_provided": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a local JSON report scaffold containing bounded scores, "
            "quality-control summaries, and empty reference slots for qualified "
            "human findings. No source-document text is copied."
        )
    )
    parser.add_argument("--rubric", required=True, type=Path, help="Local rubric JSON")
    parser.add_argument(
        "--evaluation", required=True, type=Path, help="Local evaluation JSON"
    )
    parser.add_argument(
        "--traceability", type=Path, help="Optional traceability report JSON"
    )
    parser.add_argument(
        "--agreement", type=Path, help="Optional agreement report JSON"
    )
    parser.add_argument(
        "--sensitivity", type=Path, help="Optional sensitivity report JSON"
    )
    parser.add_argument(
        "--process", type=Path, help="Optional process-check report JSON"
    )
    parser.add_argument("--output", type=Path, help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output JSON file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        optional_paths = {
            "traceability": args.traceability,
            "agreement": args.agreement,
            "sensitivity": args.sensitivity,
            "process": args.process,
        }
        companions = {
            name: _common.read_json(path) if path else None
            for name, path in optional_paths.items()
        }
        report = generate_scaffold(
            _common.read_json(args.rubric),
            _common.read_json(args.evaluation),
            **companions,
        )
        _common.write_json(report, args.output, force=args.force)
        return 0
    except _common.ValidationError as error:
        _common.write_json(_common.failure_report(error), None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/summarize_agreement.py`

```python
#!/usr/bin/env python3
"""Summarize inter-rater agreement from pseudonymous local CSV ratings."""

from __future__ import annotations

import argparse
import csv
import io
import itertools
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import _common

CSV_FIELDS = [
    "evaluation_id",
    "work_id",
    "rater_id",
    "criterion_id",
    "status",
    "score",
]


def read_rows(path: Path, rubric: dict[str, Any]) -> list[dict[str, Any]]:
    text = _common.read_csv_text(path)
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != CSV_FIELDS:
        raise _common.ValidationError("CSV_HEADER_INVALID")
    accepted_scores = _common.scale_values(rubric)
    criterion_ids = {criterion["criterion_id"] for criterion in rubric["criteria"]}
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for index, row in enumerate(reader, start=2):
        if len(rows) >= _common.MAX_CSV_ROWS:
            raise _common.ValidationError("CSV_TOO_MANY_ROWS")
        path_prefix = f"$.rows[{index}]"
        if set(row) != set(CSV_FIELDS) or any(
            not isinstance(row.get(field), str) for field in CSV_FIELDS
        ):
            raise _common.ValidationError("CSV_ROW_SHAPE_INVALID", path_prefix)
        for field in ("evaluation_id", "work_id", "rater_id", "criterion_id"):
            if not _common.is_identifier(row.get(field)):
                raise _common.ValidationError(
                    "CSV_IDENTIFIER_INVALID", f"{path_prefix}.{field}"
                )
        if row["criterion_id"] not in criterion_ids:
            raise _common.ValidationError(
                "CRITERION_UNKNOWN", f"{path_prefix}.criterion_id"
            )
        if row["status"] not in _common.RATING_STATUSES:
            raise _common.ValidationError(
                "RATING_STATUS_INVALID", f"{path_prefix}.status"
            )
        key = (
            row["evaluation_id"],
            row["work_id"],
            row["rater_id"],
            row["criterion_id"],
        )
        if key in seen:
            raise _common.ValidationError("CSV_RATING_DUPLICATE", path_prefix)
        seen.add(key)
        score: float | None
        if row["status"] == "rated":
            try:
                score = float(row["score"])
            except ValueError as error:
                raise _common.ValidationError(
                    "CSV_SCORE_INVALID", f"{path_prefix}.score"
                ) from error
            if not math.isfinite(score) or score not in accepted_scores:
                raise _common.ValidationError(
                    "SCORE_NOT_ON_SCALE", f"{path_prefix}.score"
                )
        else:
            if row["score"].strip():
                raise _common.ValidationError(
                    "UNRATED_SCORE_MUST_BE_BLANK", f"{path_prefix}.score"
                )
            score = None
        rows.append({**row, "score": score})
    if not rows:
        raise _common.ValidationError("CSV_NO_ROWS")
    return rows


def _summary(differences: list[float], step: float) -> dict[str, Any]:
    if not differences:
        return {
            "pair_observations": 0,
            "exact_agreement_rate": None,
            "within_one_scale_step_rate": None,
            "mean_absolute_difference": None,
        }
    return {
        "pair_observations": len(differences),
        "exact_agreement_rate": _common.rounded(
            sum(difference <= 1e-9 for difference in differences)
            / len(differences)
        ),
        "within_one_scale_step_rate": _common.rounded(
            sum(difference <= step + 1e-9 for difference in differences)
            / len(differences)
        ),
        "mean_absolute_difference": _common.rounded(
            sum(differences) / len(differences)
        ),
    }


def summarize(rubric: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    rubric_issues = _common.validate_rubric(rubric)
    _common.require_valid(rubric_issues)
    grouped: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    status_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"rated": 0, "missing": 0, "not_applicable": 0}
    )
    raters_by_criterion: dict[str, set[str]] = defaultdict(set)
    works_by_criterion: dict[str, set[str]] = defaultdict(set)
    all_raters: set[str] = set()
    all_works: set[str] = set()
    for row in rows:
        criterion_id = row["criterion_id"]
        status_counts[criterion_id][row["status"]] += 1
        raters_by_criterion[criterion_id].add(row["rater_id"])
        works_by_criterion[criterion_id].add(row["work_id"])
        all_raters.add(row["rater_id"])
        all_works.add(row["work_id"])
        if row["status"] == "rated":
            grouped[criterion_id][row["work_id"]][row["rater_id"]] = row["score"]

    minimum_raters = int(rubric["rater_protocol"]["minimum_raters"])
    if len(all_raters) < minimum_raters:
        raise _common.ValidationError("MINIMUM_RATERS_NOT_MET")
    step = float(rubric["scale"]["step"])
    criterion_reports: list[dict[str, Any]] = []
    overall_differences: list[float] = []
    insufficient: list[str] = []
    for criterion in rubric["criteria"]:
        criterion_id = criterion["criterion_id"]
        differences: list[float] = []
        overlap_work_count = 0
        for work_ratings in grouped.get(criterion_id, {}).values():
            values = list(work_ratings.values())
            if len(values) >= 2:
                overlap_work_count += 1
            differences.extend(
                abs(first - second)
                for first, second in itertools.combinations(values, 2)
            )
        if not differences:
            insufficient.append(criterion_id)
        overall_differences.extend(differences)
        criterion_reports.append(
            {
                "criterion_id": criterion_id,
                "rater_count": len(raters_by_criterion.get(criterion_id, set())),
                "work_count": len(works_by_criterion.get(criterion_id, set())),
                "works_with_rater_overlap": overlap_work_count,
                "rated_rows": status_counts[criterion_id]["rated"],
                "missing_rows": status_counts[criterion_id]["missing"],
                "not_applicable_rows": status_counts[criterion_id][
                    "not_applicable"
                ],
                **_summary(differences, step),
            }
        )
    warnings = []
    if insufficient:
        warnings.append("INSUFFICIENT_OVERLAP_FOR_SOME_CRITERIA")
    if any(
        counts["missing"] or counts["not_applicable"]
        for counts in status_counts.values()
    ):
        warnings.append("MISSING_OR_NOT_APPLICABLE_RATINGS_PRESENT")
    return {
        "schema_version": _common.SCHEMA_VERSION,
        "report_type": "inter_rater_agreement_summary",
        "notice": _common.NOTICE,
        "rubric_id": rubric["rubric_id"],
        "rater_count": len(all_raters),
        "work_count": len(all_works),
        "row_count": len(rows),
        "scale_step": step,
        "overall": _summary(overall_differences, step),
        "criteria": criterion_reports,
        "criteria_with_insufficient_overlap": insufficient,
        "warnings": warnings,
        "rater_identifiers_in_output": False,
        "limitations": [
            "Percent agreement and mean absolute difference are descriptive.",
            "These summaries are not a psychometric validation or reliability coefficient.",
            "Select a construct- and design-appropriate reliability model with qualified measurement expertise.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize exact agreement, within-step agreement, and mean "
            "absolute difference from pseudonymous local CSV ratings."
        )
    )
    parser.add_argument("--rubric", required=True, type=Path, help="Local rubric JSON")
    parser.add_argument(
        "--ratings", required=True, type=Path, help="Local ratings CSV"
    )
    parser.add_argument("--output", type=Path, help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output JSON file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        rubric = _common.read_json(args.rubric)
        _common.require_valid(_common.validate_rubric(rubric))
        report = summarize(rubric, read_rows(args.ratings, rubric))
        _common.write_json(report, args.output, force=args.force)
        return 0
    except _common.ValidationError as error:
        _common.write_json(_common.failure_report(error), None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_rubric.py`

```python
#!/usr/bin/env python3
"""Validate a bounded scholar-evaluation rubric JSON file."""

from __future__ import annotations

import argparse
from pathlib import Path

import _common


def validate_file(path: Path) -> dict:
    rubric = _common.read_json(path)
    issues = _common.validate_rubric(rubric)
    errors = _common.error_issues(issues)
    return {
        "schema_version": _common.SCHEMA_VERSION,
        "report_type": "rubric_schema_validation",
        "status": "invalid" if errors else "valid",
        "rubric_id": rubric.get("rubric_id") if isinstance(rubric, dict) else None,
        "error_count": len(errors),
        "warning_count": len(issues) - len(errors),
        "issues": [issue.as_dict() for issue in issues],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a strict local rubric schema; no document content, "
            "credentials, models, or network access are used."
        )
    )
    parser.add_argument("--rubric", required=True, type=Path, help="Local rubric JSON")
    parser.add_argument("--output", type=Path, help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output JSON file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = validate_file(args.rubric)
        _common.write_json(report, args.output, force=args.force)
        return 0 if report["status"] == "valid" else 2
    except _common.ValidationError as error:
        _common.write_json(_common.failure_report(error), None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/weight_sensitivity.py`

```python
#!/usr/bin/env python3
"""Stress-test rubric weights and report scholarly-work order instability."""

from __future__ import annotations

import argparse
import itertools
from pathlib import Path
from typing import Any

import _common


def _normalized(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    return {criterion_id: weight / total for criterion_id, weight in weights.items()}


def _scenarios(
    base_weights: dict[str, float], delta: float
) -> list[tuple[str, str | None, float, dict[str, float]]]:
    scenarios = [("base", None, 1.0, dict(base_weights))]
    for criterion_id in sorted(base_weights):
        for label, multiplier in (("decrease", 1.0 - delta), ("increase", 1.0 + delta)):
            changed = dict(base_weights)
            changed[criterion_id] *= multiplier
            scenarios.append(
                (
                    f"{criterion_id}:{label}",
                    criterion_id,
                    multiplier,
                    _normalized(changed),
                )
            )
    return scenarios


def _direction(first: float | None, second: float | None) -> int | None:
    if first is None or second is None:
        return None
    difference = first - second
    if abs(difference) <= 1e-9:
        return 0
    return 1 if difference > 0 else -1


def analyze(
    rubric: dict[str, Any],
    evaluations: list[dict[str, Any]],
    delta: float,
) -> dict[str, Any]:
    rubric_issues = _common.validate_rubric(rubric)
    _common.require_valid(rubric_issues)
    if not 2 <= len(evaluations) <= _common.MAX_EVALUATIONS:
        raise _common.ValidationError("EVALUATION_COUNT_INVALID")
    work_ids: set[str] = set()
    evaluation_ids: set[str] = set()
    for index, evaluation in enumerate(evaluations):
        issues = _common.validate_evaluation(evaluation, rubric)
        _common.require_valid(issues)
        if evaluation["work_id"] in work_ids:
            raise _common.ValidationError(
                "WORK_ID_DUPLICATE", f"$.evaluations[{index}].work_id"
            )
        if evaluation["evaluation_id"] in evaluation_ids:
            raise _common.ValidationError(
                "EVALUATION_ID_DUPLICATE", f"$.evaluations[{index}].evaluation_id"
            )
        work_ids.add(evaluation["work_id"])
        evaluation_ids.add(evaluation["evaluation_id"])
    if not 0 < delta <= 0.5:
        raise _common.ValidationError("DELTA_OUT_OF_RANGE")

    base_weights = _common.weights_by_criterion(rubric)
    scenario_output: list[dict[str, Any]] = []
    score_ranges = {
        work_id: {"minimum": None, "maximum": None} for work_id in sorted(work_ids)
    }
    base_scores: dict[str, float | None] = {}
    pair_changes: set[tuple[str, str]] = set()
    pairs = list(itertools.combinations(sorted(work_ids), 2))
    incomplete_work_ids: set[str] = set()

    for scenario_index, (
        scenario_id,
        criterion_id,
        multiplier,
        weights,
    ) in enumerate(_scenarios(base_weights, delta)):
        item_scores: list[dict[str, Any]] = []
        score_lookup: dict[str, float | None] = {}
        for evaluation in evaluations:
            score_report = _common.score_evaluation(
                rubric, evaluation, weights=weights
            )
            score = score_report["aggregates"]["normalized_score"]
            coverage = score_report["aggregates"]["coverage_of_applicable_weight"]
            if score is None:
                raise _common.ValidationError(
                    "SENSITIVITY_SCORE_UNAVAILABLE", evaluation["work_id"]
                )
            if coverage is None or coverage < 1:
                incomplete_work_ids.add(evaluation["work_id"])
            score_lookup[evaluation["work_id"]] = score
            current_range = score_ranges[evaluation["work_id"]]
            current_range["minimum"] = (
                score
                if current_range["minimum"] is None
                else min(current_range["minimum"], score)
            )
            current_range["maximum"] = (
                score
                if current_range["maximum"] is None
                else max(current_range["maximum"], score)
            )
            item_scores.append(
                {
                    "work_id": evaluation["work_id"],
                    "normalized_score": score,
                    "coverage_of_applicable_weight": coverage,
                }
            )
        if scenario_index == 0:
            base_scores = score_lookup
        else:
            for first, second in pairs:
                if _direction(base_scores[first], base_scores[second]) != _direction(
                    score_lookup[first], score_lookup[second]
                ):
                    pair_changes.add((first, second))
        scenario_output.append(
            {
                "scenario_id": scenario_id,
                "perturbed_criterion_id": criterion_id,
                "weight_multiplier": _common.rounded(multiplier),
                "weights": {
                    key: _common.rounded(value)
                    for key, value in sorted(weights.items())
                },
                "item_scores": sorted(item_scores, key=lambda item: item["work_id"]),
            }
        )

    base_order = [
        work_id
        for work_id, _ in sorted(
            base_scores.items(),
            key=lambda item: (
                -(item[1] if item[1] is not None else float("-inf")),
                item[0],
            ),
        )
    ]
    range_output = [
        {
            "work_id": work_id,
            "minimum_score": _common.rounded(bounds["minimum"]),
            "maximum_score": _common.rounded(bounds["maximum"]),
            "range_width": _common.rounded(
                bounds["maximum"] - bounds["minimum"]
                if bounds["minimum"] is not None and bounds["maximum"] is not None
                else None
            ),
        }
        for work_id, bounds in sorted(score_ranges.items())
    ]
    warnings: list[str] = []
    if incomplete_work_ids:
        warnings.append("INCOMPLETE_COVERAGE_LIMITS_COMPARABILITY")
    if pair_changes:
        warnings.append("ORDINAL_ORDER_CHANGES_UNDER_WEIGHT_PERTURBATION")
    return {
        "schema_version": _common.SCHEMA_VERSION,
        "report_type": "weight_sensitivity_and_rank_instability",
        "notice": _common.NOTICE,
        "rubric_id": rubric["rubric_id"],
        "purpose": _common.ALLOWED_PURPOSE,
        "unit_of_assessment": _common.ALLOWED_UNIT,
        "delta": delta,
        "perturbation_method": (
            "multiply one criterion weight by 1-delta and 1+delta, then "
            "renormalize all weights to sum to one"
        ),
        "scenario_count": len(scenario_output),
        "base_ordinal_order": base_order,
        "base_order_is_a_decision_recommendation": False,
        "rank_instability_detected": bool(pair_changes),
        "changed_pair_count": len(pair_changes),
        "total_pair_count": len(pairs),
        "changed_work_pairs": [
            {"first_work_id": first, "second_work_id": second}
            for first, second in sorted(pair_changes)
        ],
        "incomplete_coverage_work_ids": sorted(incomplete_work_ids),
        "score_ranges": range_output,
        "scenarios": scenario_output,
        "warnings": warnings,
        "limitations": [
            "This is a deterministic local stress test, not a validity study.",
            "Ordinal order must not be used to rank people or make high-impact decisions.",
            "Results depend on the submitted rubric, ratings, missingness, and perturbation size.",
        ],
        "decision_recommendation_provided": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Perturb rubric weights and report score ranges and ordinal-order "
            "changes for scholarly works only. Never use this output to rank people."
        )
    )
    parser.add_argument("--rubric", required=True, type=Path, help="Local rubric JSON")
    parser.add_argument(
        "--evaluation",
        required=True,
        type=Path,
        action="append",
        help="Local evaluation JSON; repeat for 2 to 50 distinct scholarly works",
    )
    parser.add_argument(
        "--delta",
        type=float,
        default=0.2,
        help="Relative one-at-a-time weight change in (0, 0.5] (default: 0.2)",
    )
    parser.add_argument("--output", type=Path, help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output JSON file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = analyze(
            _common.read_json(args.rubric),
            [_common.read_json(path) for path in args.evaluation],
            args.delta,
        )
        _common.write_json(report, args.output, force=args.force)
        return 0
    except _common.ValidationError as error:
        _common.write_json(_common.failure_report(error), None)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

### `assets/evaluation_template.json`

```json
{
  "schema_version": "2.0",
  "evaluation_id": "EVALUATION-SYNTHETIC-001",
  "rubric_id": "RUBRIC-SYNTHETIC-001",
  "work_id": "WORK-SYNTHETIC-001",
  "data_classification": "synthetic",
  "purpose": "developmental_review_of_scholarly_work",
  "ratings": [
    {
      "criterion_id": "question_scope",
      "status": "missing",
      "score": null,
      "uncertainty": null,
      "evidence_ids": [],
      "rationale_ref": "LOCAL-MISSING-RATIONALE-QUESTION"
    },
    {
      "criterion_id": "literature_contribution",
      "status": "missing",
      "score": null,
      "uncertainty": null,
      "evidence_ids": [],
      "rationale_ref": "LOCAL-MISSING-RATIONALE-LITERATURE"
    },
    {
      "criterion_id": "method_design",
      "status": "missing",
      "score": null,
      "uncertainty": null,
      "evidence_ids": [],
      "rationale_ref": "LOCAL-MISSING-RATIONALE-METHOD"
    },
    {
      "criterion_id": "analysis_claims",
      "status": "missing",
      "score": null,
      "uncertainty": null,
      "evidence_ids": [],
      "rationale_ref": "LOCAL-MISSING-RATIONALE-ANALYSIS"
    },
    {
      "criterion_id": "transparency_integrity",
      "status": "missing",
      "score": null,
      "uncertainty": null,
      "evidence_ids": [],
      "rationale_ref": "LOCAL-MISSING-RATIONALE-TRANSPARENCY"
    }
  ]
}
```

### `assets/evidence_manifest_template.json`

```json
{
  "schema_version": "2.0",
  "evaluation_id": "EVALUATION-SYNTHETIC-001",
  "work_id": "WORK-SYNTHETIC-001",
  "data_classification": "synthetic",
  "evidence": [
    {
      "evidence_id": "EVIDENCE-SYNTHETIC-QUESTION",
      "criterion_ids": [
        "question_scope"
      ],
      "source_type": "section",
      "locator_ref": "LOCAL-WORK-SECTION-QUESTION",
      "claim_ref": "LOCAL-CLAIM-QUESTION",
      "access_status": "available",
      "verification_status": "verified"
    },
    {
      "evidence_id": "EVIDENCE-SYNTHETIC-LITERATURE",
      "criterion_ids": [
        "literature_contribution"
      ],
      "source_type": "section",
      "locator_ref": "LOCAL-WORK-SECTION-LITERATURE",
      "claim_ref": "LOCAL-CLAIM-CONTRIBUTION",
      "access_status": "available",
      "verification_status": "verified"
    },
    {
      "evidence_id": "EVIDENCE-SYNTHETIC-METHOD",
      "criterion_ids": [
        "method_design"
      ],
      "source_type": "protocol",
      "locator_ref": "LOCAL-WORK-PROTOCOL",
      "claim_ref": "LOCAL-CLAIM-METHOD",
      "access_status": "available",
      "verification_status": "verified"
    },
    {
      "evidence_id": "EVIDENCE-SYNTHETIC-ANALYSIS",
      "criterion_ids": [
        "analysis_claims"
      ],
      "source_type": "section",
      "locator_ref": "LOCAL-WORK-SECTION-ANALYSIS",
      "claim_ref": "LOCAL-CLAIM-ANALYSIS",
      "access_status": "available",
      "verification_status": "verified"
    },
    {
      "evidence_id": "EVIDENCE-SYNTHETIC-TRANSPARENCY",
      "criterion_ids": [
        "transparency_integrity"
      ],
      "source_type": "other_local_record",
      "locator_ref": "LOCAL-WORK-TRANSPARENCY-RECORD",
      "claim_ref": "LOCAL-CLAIM-TRANSPARENCY",
      "access_status": "available",
      "verification_status": "verified"
    }
  ]
}
```

### `assets/process_checklist_template.json`

```json
{
  "schema_version": "2.0",
  "process_id": "PROCESS-SYNTHETIC-001",
  "purpose": "developmental_review_of_scholarly_work",
  "unit_of_assessment": "scholarly_work",
  "data_classification": "synthetic",
  "high_impact_use": false,
  "committee": {
    "qualified_members_confirmed": false,
    "training_completed": false,
    "accountable_owner_role": "",
    "training_record_ref": ""
  },
  "conflicts": {
    "disclosure_process_confirmed": false,
    "recusal_process_confirmed": false,
    "record_ref": ""
  },
  "appeals": {
    "process_confirmed": false,
    "process_ref": "",
    "notice_ref": ""
  },
  "accessibility": {
    "accommodations_process_confirmed": false,
    "accessible_materials_confirmed": false,
    "process_ref": ""
  },
  "data_protection": {
    "purpose_limitation_confirmed": false,
    "data_minimisation_confirmed": false,
    "access_controls_confirmed": false,
    "retention_schedule_confirmed": false,
    "raw_private_documents_excluded_from_tool_outputs": false,
    "review_ref": ""
  },
  "rubric_quality": {
    "construct_documented": false,
    "rubric_provenance_documented": false,
    "content_validity_documented": false,
    "rater_training_documented": false,
    "agreement_reviewed": false,
    "inter_rater_reliability_reviewed": false,
    "uncertainty_recorded": false,
    "missing_and_not_applicable_supported": false,
    "evidence_traceability_checked": false,
    "weight_sensitivity_reviewed": false,
    "quality_record_ref": ""
  },
  "fairness": {
    "stakeholder_review_completed": false,
    "disciplinary_context_reviewed": false,
    "subgroup_bias_review_completed": false,
    "protected_attributes_excluded_from_scoring": false,
    "bias_review_ref": ""
  },
  "decision_controls": {
    "no_automated_decision": false,
    "no_person_ranking": false,
    "no_decision_recommendation": false,
    "qualified_human_accountability": false
  },
  "monitoring": {
    "rater_drift_reviewed": false,
    "unintended_consequences_reviewed": false,
    "periodic_revision_scheduled": false,
    "review_record_ref": "",
    "revision_owner_role": ""
  }
}
```

### `assets/ratings_template.csv`

```csv
evaluation_id,work_id,rater_id,criterion_id,status,score
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-1,question_scope,rated,3
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-2,question_scope,rated,4
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-1,literature_contribution,rated,2
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-2,literature_contribution,rated,3
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-1,method_design,rated,3
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-2,method_design,rated,3
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-1,analysis_claims,rated,2
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-2,analysis_claims,rated,3
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-1,transparency_integrity,rated,3
EVALUATION-SYNTHETIC-A,WORK-SYNTHETIC-A,RATER-SYNTHETIC-2,transparency_integrity,rated,3
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-1,question_scope,rated,2
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-2,question_scope,rated,2
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-1,literature_contribution,rated,3
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-2,literature_contribution,rated,2
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-1,method_design,rated,2
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-2,method_design,rated,3
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-1,analysis_claims,missing,
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-2,analysis_claims,rated,2
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-1,transparency_integrity,not_applicable,
EVALUATION-SYNTHETIC-B,WORK-SYNTHETIC-B,RATER-SYNTHETIC-2,transparency_integrity,not_applicable,
```

### `assets/rubric_template.json`

```json
{
  "schema_version": "2.0",
  "rubric_id": "RUBRIC-SYNTHETIC-001",
  "title": "Developmental scholarly-work evidence rubric",
  "intended_use": {
    "purpose": "developmental_review_of_scholarly_work",
    "unit_of_assessment": "scholarly_work",
    "allowed_contexts": [
      "draft feedback",
      "research idea feedback",
      "retrospective methods review"
    ],
    "prohibited_uses": [
      "admissions",
      "awards",
      "discipline",
      "funding",
      "hiring",
      "promotion",
      "tenure",
      "other_high_impact_personnel_decision"
    ]
  },
  "construct": {
    "label": "Traceable support for a scholarly work's claims and methods",
    "definition": "The degree to which a scholarly work states a bounded question, situates its contribution, uses fit-for-purpose methods, aligns analysis with claims, and documents transparent and responsible practices using traceable evidence.",
    "boundaries": [
      "The construct applies to a scholarly work, not a person or organization.",
      "Scores describe evidence against this rubric and do not establish merit, readiness, impact, or a decision outcome.",
      "Disciplinary experts must adapt criterion interpretation before use."
    ],
    "limitations": [
      "This template has not established content validity for any discipline or decision context.",
      "Ordinal ratings and weights are judgments rather than natural measurements.",
      "Literature coverage, rater interpretation, missing evidence, and rubric choices can change results."
    ]
  },
  "provenance": {
    "rubric_version": "1.0",
    "owner_role": "qualified accountable assessment-methods owner",
    "source_ids": [
      "SOURCE-DORA-DECLARATION",
      "SOURCE-DORA-INDICATORS-2024",
      "SOURCE-LEIDEN-2015",
      "SOURCE-COARA-2022",
      "SOURCE-HONG-KONG-2020",
      "SOURCE-SCOPE-2021",
      "SOURCE-TESTING-STANDARDS-2014"
    ],
    "content_validity_status": "not_established",
    "content_validity_evidence_ref": "",
    "last_reviewed_date": "2026-07-23"
  },
  "scale": {
    "minimum": 0,
    "maximum": 4,
    "step": 1,
    "anchors": [
      {
        "score": 0,
        "label": "No assessable evidence",
        "description": "Required evidence is absent, inaccessible, or too unclear to assess."
      },
      {
        "score": 1,
        "label": "Limited support",
        "description": "Some relevant evidence is present, but major gaps or unresolved contradictions remain."
      },
      {
        "score": 2,
        "label": "Mixed support",
        "description": "Evidence partly supports the criterion, with material limitations or uncertainty."
      },
      {
        "score": 3,
        "label": "Substantial support",
        "description": "Traceable evidence substantially supports the criterion and important limitations are stated."
      },
      {
        "score": 4,
        "label": "Strong support",
        "description": "Multiple appropriate evidence elements coherently support the criterion and boundaries are handled explicitly."
      }
    ]
  },
  "criteria": [
    {
      "criterion_id": "question_scope",
      "label": "Question and scope",
      "construct_component": "Clarity, boundedness, significance rationale, assumptions, and feasible scope",
      "weight": 0.15,
      "required": true,
      "anchors": [
        {
          "score": 0,
          "description": "No assessable question, scope, assumptions, or success conditions are provided."
        },
        {
          "score": 1,
          "description": "A question is suggested, but scope or assumptions are materially unclear."
        },
        {
          "score": 2,
          "description": "The question is identifiable, with mixed clarity, feasibility, or boundary specification."
        },
        {
          "score": 3,
          "description": "The question, scope, assumptions, and success conditions are substantially clear and feasible."
        },
        {
          "score": 4,
          "description": "The question and boundaries are precise, justified, feasible, and explicitly connected to success conditions."
        }
      ],
      "evidence_requirements": [
        "A stable locator for the stated question or objective",
        "A stable locator for scope, assumptions, and boundary conditions",
        "A stable locator for the significance rationale"
      ],
      "limitations": [
        "Significance is context-dependent and must be interpreted by relevant disciplinary experts."
      ]
    },
    {
      "criterion_id": "literature_contribution",
      "label": "Literature grounding and contribution claim",
      "construct_component": "Traceable engagement with relevant prior work and a bounded comparison-based contribution claim",
      "weight": 0.2,
      "required": true,
      "anchors": [
        {
          "score": 0,
          "description": "No assessable literature grounding or comparison-based contribution claim is provided."
        },
        {
          "score": 1,
          "description": "Prior work is referenced selectively or the contribution claim is largely unsupported."
        },
        {
          "score": 2,
          "description": "Relevant prior work and comparison evidence are present, with material coverage or inference gaps."
        },
        {
          "score": 3,
          "description": "The work is substantially grounded in relevant literature and the contribution claim is bounded by traceable comparisons."
        },
        {
          "score": 4,
          "description": "Search boundaries, contrary evidence, and comparison dimensions are explicit and strongly support a carefully limited contribution claim."
        }
      ],
      "evidence_requirements": [
        "A documented literature-search or source-selection boundary",
        "Traceable primary sources for comparison claims",
        "A stable locator for contrary, null, or competing evidence considered"
      ],
      "limitations": [
        "Absence from a search result does not establish novelty.",
        "Coverage varies by discipline, language, database, date, and access."
      ]
    },
    {
      "criterion_id": "method_design",
      "label": "Method and design fit",
      "construct_component": "Alignment of design, data or materials, methods, ethics, and validity safeguards with the question",
      "weight": 0.25,
      "required": true,
      "anchors": [
        {
          "score": 0,
          "description": "Methods are absent or cannot address the stated question."
        },
        {
          "score": 1,
          "description": "Methods are partly described but have major unresolved alignment or validity problems."
        },
        {
          "score": 2,
          "description": "The design is partly fit for purpose, with material weaknesses or incomplete safeguards."
        },
        {
          "score": 3,
          "description": "The design is substantially aligned, reproducibly described, and addresses major validity and ethics concerns."
        },
        {
          "score": 4,
          "description": "The design is strongly justified against alternatives, with comprehensive safeguards, transparent choices, and bounded claims."
        }
      ],
      "evidence_requirements": [
        "A stable locator for the design and method rationale",
        "A stable locator for data, sampling, materials, or corpus boundaries",
        "A stable locator for ethics, validity threats, and mitigation"
      ],
      "limitations": [
        "Method quality depends on disciplinary norms and the stated inferential target."
      ]
    },
    {
      "criterion_id": "analysis_claims",
      "label": "Analysis, claims, and uncertainty",
      "construct_component": "Fit of analysis, robustness checks, uncertainty representation, and proportionality of conclusions",
      "weight": 0.2,
      "required": true,
      "anchors": [
        {
          "score": 0,
          "description": "Analysis is absent, uninterpretable, or disconnected from the claims."
        },
        {
          "score": 1,
          "description": "Analysis is present but major assumptions, alternatives, or uncertainty are unaddressed."
        },
        {
          "score": 2,
          "description": "Analysis partly supports the claims, with material robustness or uncertainty limitations."
        },
        {
          "score": 3,
          "description": "Analysis substantially supports proportionate claims and reports important uncertainty and alternatives."
        },
        {
          "score": 4,
          "description": "Analysis, robustness checks, uncertainty, alternatives, and claim boundaries form a coherent and transparent evidentiary chain."
        }
      ],
      "evidence_requirements": [
        "A stable locator for analysis procedures and assumptions",
        "A stable locator for uncertainty or qualitative confidence treatment",
        "A stable locator for robustness checks and alternative explanations"
      ],
      "limitations": [
        "Criterion-level uncertainty records rater judgment range and is not a statistical confidence interval."
      ]
    },
    {
      "criterion_id": "transparency_integrity",
      "label": "Transparency, integrity, and reproducibility",
      "construct_component": "Complete reporting, traceability, responsible practice, openness where appropriate, and recognition of limitations",
      "weight": 0.2,
      "required": true,
      "anchors": [
        {
          "score": 0,
          "description": "Key procedures, provenance, limitations, or integrity safeguards are not assessable."
        },
        {
          "score": 1,
          "description": "Some transparency elements are present, but major omissions prevent checking or reuse."
        },
        {
          "score": 2,
          "description": "Reporting and provenance are partly traceable, with material gaps or unjustified restrictions."
        },
        {
          "score": 3,
          "description": "Reporting, provenance, limitations, and responsible-practice safeguards are substantially traceable and appropriate."
        },
        {
          "score": 4,
          "description": "The work provides strong, accessible traceability and justified openness or restrictions across methods, outputs, limitations, and contributions."
        }
      ],
      "evidence_requirements": [
        "Stable locators for methods, materials, data, code, or justified access restrictions",
        "A stable locator for limitations, conflicts, and ethical safeguards",
        "A stable locator for contribution and provenance records"
      ],
      "limitations": [
        "Open practice must account for privacy, safety, sovereignty, consent, and disciplinary constraints."
      ]
    }
  ],
  "rater_protocol": {
    "minimum_raters": 2,
    "training_required": true,
    "training_ref": "LOCAL-RATER-TRAINING-REQUIRED",
    "calibration_required": true,
    "calibration_ref": "LOCAL-RATER-CALIBRATION-REQUIRED",
    "agreement_method": "exact_within_step_and_mean_absolute_difference",
    "inter_rater_reliability_status": "not_established",
    "inter_rater_reliability_ref": "",
    "drift_monitoring_required": true,
    "drift_review_ref": "LOCAL-RATER-DRIFT-REVIEW-REQUIRED"
  },
  "governance": {
    "accountable_committee_required": true,
    "committee_owner_role": "qualified accountable human committee chair",
    "conflict_disclosure_required": true,
    "recusal_required": true,
    "appeal_process_required": true,
    "appeal_process_ref": "LOCAL-APPEAL-PROCESS-REQUIRED",
    "accessibility_accommodations_required": true,
    "accessibility_process_ref": "LOCAL-ACCESSIBILITY-PROCESS-REQUIRED",
    "data_protection_review_required": true,
    "data_protection_process_ref": "LOCAL-DATA-PROTECTION-REVIEW-REQUIRED",
    "subgroup_bias_review_required": true,
    "subgroup_review_ref": "LOCAL-SUBGROUP-BIAS-REVIEW-REQUIRED",
    "review_cycle_ref": "LOCAL-RUBRIC-REVIEW-CYCLE-REQUIRED"
  }
}
```
