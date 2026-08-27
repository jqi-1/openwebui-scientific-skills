---
name: clinical-reports
description: Create safety-bounded draft structures and run local deterministic checks for clinical case, diagnostic, trial, safety, and aggregate research reports. Use only with synthetic, de-identified, or aggregate inputs and verified source-fact manifests; every output requires qualified review.
---

# Clinical Reports

## Purpose

Prepare **draft reporting structures**, aggregate tables, and review manifests from verified authorized facts. Route each artifact to the correct reporting guidance, preserve provenance, and stop when source support or qualified review is missing.

This skill does not establish legal, regulatory, ethical, journal, accreditation, or institutional compliance. Its scripts check structure and internal consistency only.

## Non-Negotiable Boundary

Never:

- diagnose, recommend treatment, choose or change dosing, triage, or provide return precautions;
- interpret images, specimens, raw laboratory results, symptoms, or other clinical observations;
- invent, infer, normalize, “complete,” or silently reconcile observations, results, dates, units, denominators, causality, expectedness, seriousness, outcomes, or conclusions;
- create an individual case safety report from patient-level narrative or decide reportability;
- sign, attest, approve, file, transmit, submit, amend a source record, or act as a licensed clinician, pathologist, radiologist, laboratorian, safety physician, statistician, privacy officer, attorney, or regulatory professional;
- use real PHI in examples, assets, tests, prompts, logs, or external services;
- call an external LLM, image service, API, or another skill.

All generated artifacts must remain visibly marked:

> DRAFT — NOT FOR CLINICAL USE, SIGNATURE, FILING, OR SUBMISSION. Populate only from verified authorized source records. Qualified review and sign-off are required.

If the request crosses a boundary, stop the unsafe portion. Offer a blank structured template, a source-fact manifest, or a deterministic structural check. Direct clinical or regulatory decisions to the responsible qualified professional.

## Input Gate

Proceed only when all conditions are true:

1. **Purpose is explicit**: publication draft, diagnostic-report scaffold, trial-results manuscript, protocol reporting review, CSR draft, aggregate safety table, or aggregate research summary.
2. **Data class is allowed**: `synthetic`, `deidentified`, or `aggregate`.
3. **Authority is documented**: the requester is authorized to use the records for the stated purpose.
4. **Local-only handling is feasible**: no upload, remote API, telemetry, or credential is needed.
5. **Minimum necessary is defined**: exclude fields not needed for the artifact.
6. **Provenance exists**: every populated field or claim maps to one or more verified source-fact IDs.
7. **Review owner is identified**: qualified clinical, statistical, safety, privacy, legal, journal, and/or regulatory review as applicable.

Do not accept raw free-text patient records when a structured source-fact manifest can be supplied. Do not copy direct identifiers into this skill’s templates or scripts.

## Route Before Drafting

| Artifact | Primary route | Important boundary |
|---|---|---|
| Case report for publication | CARE 2013 checklist and 2017 explanation | Publication consent, privacy, journal policy, and clinical accuracy require human verification |
| Radiology draft scaffold | ACR 2025 communication practice parameter plus modality-specific ACR material | A qualified radiologist authors findings/impression and handles nonroutine communication |
| Pathology draft scaffold | Current specimen-specific CAP Cancer Protocol, if applicable | A qualified pathologist selects the protocol/version and authors diagnosis |
| Laboratory draft scaffold | 42 CFR 493.1291 and laboratory policy | The performing laboratory controls results, reference intervals, corrections, and release |
| Randomized-trial results report | CONSORT 2025 plus every applicable current extension | CONSORT is reporting guidance, not a conduct or submission standard |
| Randomized-trial protocol report | SPIRIT 2025 plus applicable extensions | SPIRIT is for protocols, not results or CSRs |
| Clinical Study Report | ICH E3 plus E3 Q&A; consider ICH E6(R3) and regional requirements | E3 is adaptable guidance, not a rigid universal template |
| Pre-approval safety report | ICH E2A; E2B(R3) for electronic ICSR data; applicable regional law/guidance | Qualified sponsor/investigator safety assessment controls reportability and timing |
| Post-approval individual safety report | ICH E2D(R1), E2B(R3), and regional requirements | Do not automate case assessment, coding, or submission |
| Aggregate safety presentation | Protocol/SAP, ICH E3, CONSORT Harms, and applicable FDA/ICH guidance | Aggregate tables never determine individual-case reportability |
| Aggregate research summary | Study-design-specific reporting guideline and source protocol/SAP | State population, estimand, denominator, missingness, and limitations exactly as verified |

Read `references/report_type_routing.md` before choosing a route. Use the dated primary-source ledger in `references/sources.md`; check the live official source when requirements could have changed.

## Safe Drafting Workflow

### 1. Create a source-fact manifest

Use `assets/provenance_manifest_template.json`. Record only local record locators, field paths, verification state, verifier role, verification date, and a SHA-256 value hash. Do not duplicate source content or direct identifiers.

Every draft claim or populated field must cite one or more fact IDs. Unsupported content remains `null` or `missing`; never replace it with plausible text.

### 2. Generate the correct template

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_report_template.py --list
PYTHONDONTWRITEBYTECODE=1 python3 scripts/generate_report_template.py \
  --type case-report \
  --output ./case-report-draft.json
```

The generator copies a fail-closed JSON template. It does not populate clinical content, create directories, overwrite files by default, or certify readiness.

### 3. Populate verified fields only

- Keep `draft_status` unchanged.
- Replace `null` only when a verified fact ID supports the field.
- Preserve uncertainty and “not assessed” exactly as recorded.
- Do not translate a raw observation into a diagnosis, code, grade, stage, seriousness, causality, expectedness, or recommendation.
- Use `not_applicable_with_rationale` only when a qualified reviewer supplied the rationale.
- Keep source record and draft separate.

### 4. Run deterministic checks

CARE structure:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_case_report.py \
  ./case-report-draft.json
```

ICH E3, CONSORT 2025, or SPIRIT 2025 structure:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_trial_report.py \
  ./trial-report-manifest.json
```

Aggregate adverse-event table:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/format_adverse_events.py \
  ./aggregate-ae.csv --metadata ./safety-aggregate.json \
  --output ./aggregate-ae-table.md
```

Terminology schema:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/terminology_validator.py \
  ./terminology-manifest.json
```

De-identification process documentation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_deidentification.py \
  ./deidentification-process.json
```

Traceability and consistency:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/provenance_validator.py ./provenance.json
PYTHONDONTWRITEBYTECODE=1 python3 scripts/consistency_checker.py ./consistency.json
```

These tools use the Python standard library, local bounded files, and no network, dynamic evaluation, serialization code execution, or patient-record extraction. A successful result still says review is required.

### 5. Apply the right review

At minimum:

- clinical facts and interpretations: qualified clinician for the specialty;
- statistical results, populations, estimands, denominators, and missingness: qualified statistician;
- safety coding, seriousness, causality, expectedness, and reportability: qualified safety professional;
- HIPAA, consent, authorization, and disclosure: privacy/legal/institutional review;
- CSR or regulatory safety output: sponsor regulatory and medical review;
- publication: all accountable authors and target-journal checks.

Never sign or submit on another person’s behalf.

## Case Reports

Use `assets/case_report_template.json` and `references/case_report_guidelines.md`.

- CARE’s current core checklist remains the 2013 checklist.
- Report only what the verified record supports.
- Do not turn a case into clinical advice or generalize causality from one case.
- Patient perspective and informed-consent status must be recorded accurately; do not draft a false consent statement.
- De-identification and consent are separate controls. Consent does not erase privacy risk.

## Diagnostic Report Scaffolds

Use the radiology, pathology, or laboratory JSON asset and `references/diagnostic_reports_standards.md`.

- The assets are field maps, not diagnostic authoring systems.
- Never generate findings, impressions, diagnoses, grades, stages, reference intervals, critical thresholds, or follow-up recommendations.
- Preserve preliminary/final/corrected status and source-system version.
- Use current, exact CAP protocol and version for the specimen; do not maintain a generic cancer staging default.
- Communication and correction actions remain with the responsible clinical service.

The former SOAP, H&P, consultation, and discharge-summary interfaces were removed. Do not recreate patient-care notes, medication plans, triage instructions, billing support, or disposition advice.

## Trial, CSR, and Safety Reporting

Read `references/clinical_trial_reporting.md` and `references/safety_reporting.md`.

- CONSORT 2025 has 30 minimum items for randomized-trial results; select relevant extensions from the current official catalogue.
- SPIRIT 2025 has 34 minimum items for randomized-trial protocols and supersedes SPIRIT 2013.
- ICH E3 remains the CSR basis; its 2012 Q&A explicitly permits justified adaptation.
- ICH E6(R3) consolidated Principles, Annex 1, and Annex 2 were adopted on 16 June 2026; regional implementation can differ.
- Distinguish seriousness from severity and an adverse event from a suspected adverse reaction.
- ICH E2B(R3) defines electronic ICSR data/message structure; it is not an aggregate-table format or a reportability decision rule.
- ICH E2D(R1), adopted 15 September 2025, addresses post-approval individual case safety reporting; aggregate periodic reporting is addressed separately.
- FDA requirements and electronic submission routes are role-, product-, study-, and date-specific. This skill never files or transmits.

## Privacy

Read `references/privacy_and_deidentification.md`.

- Handle only the minimum necessary data locally.
- HHS recognizes Safe Harbor and Expert Determination under 45 CFR 164.514(b).
- Safe Harbor also requires no actual knowledge that remaining information can identify an individual.
- Expert Determination must be performed and documented by an appropriately qualified expert.
- A checklist or pattern scan cannot establish de-identification or HIPAA compliance.
- Rare conditions, small cells, dates, free text, images, metadata, and combinations of quasi-identifiers can retain re-identification risk.

## Assets

All assets contain synthetic schemas only and start blocked:

- `assets/case_report_template.json`
- `assets/radiology_report_template.json`
- `assets/pathology_report_template.json`
- `assets/lab_report_template.json`
- `assets/clinical_trial_csr_template.json`
- `assets/clinical_trial_results_template.json`
- `assets/trial_protocol_reporting_checklist.json`
- `assets/clinical_trial_safety_aggregate_template.json`
- `assets/adverse_event_aggregate_input_template.csv`
- `assets/research_summary_template.json`
- `assets/deidentification_process_checklist.json`
- `assets/quality_review_checklist.json`
- `assets/provenance_manifest_template.json`
- `assets/terminology_manifest_template.json`
- `assets/consistency_manifest_template.json`

## References

- `references/README.md` — safe use and file map
- `references/report_type_routing.md` — artifact-to-guidance routing
- `references/case_report_guidelines.md` — CARE structure and publication safeguards
- `references/diagnostic_reports_standards.md` — ACR, CAP, and CLIA boundaries
- `references/clinical_trial_reporting.md` — CONSORT 2025, SPIRIT 2025, ICH E3/E6(R3)
- `references/safety_reporting.md` — ICH E2/FDA safety distinctions
- `references/privacy_and_deidentification.md` — HHS methods and limitations
- `references/medical_terminology.md` — versioned terminology and schema checks
- `references/data_presentation.md` — denominators, units, missingness, and aggregate tables
- `references/professional_review.md` — ethics, accountability, and sign-off
- `references/sources.md` — official source ledger, checked 2026-07-23

## Final Handoff

State:

1. artifact type and exact guidance/version used;
2. allowed data class and local-only handling;
3. unresolved `null`, `missing`, conflicts, and unsupported claims;
4. provenance and deterministic-check results;
5. required qualified reviewers;
6. the draft/non-submission warning.

Never say “compliant,” “HIPAA-safe,” “validated clinically,” “approved,” “ready to file,” or “ready to submit.”

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/clinical-reports/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/README.md`

# Clinical Reports References

These references support local, deterministic drafting and review. They are not clinical, legal, regulatory, privacy, publication, or accreditation advice and do not establish compliance.

## Safety boundary

- Use only synthetic, de-identified, or aggregate data.
- Populate drafts only from verified authorized source facts.
- Do not diagnose, treat, dose, triage, interpret raw observations, fabricate results, sign, file, or submit.
- Do not use external models, APIs, image tools, or cross-skill calls.
- Keep every output marked as a draft requiring qualified review.

## File map

| File | Use |
|---|---|
| `report_type_routing.md` | Select the artifact and exact source family before drafting |
| `case_report_guidelines.md` | CARE case-report structure, consent, and publication safeguards |
| `diagnostic_reports_standards.md` | Radiology, pathology, and laboratory field boundaries |
| `clinical_trial_reporting.md` | CONSORT 2025, SPIRIT 2025, ICH E3, and ICH E6(R3) |
| `safety_reporting.md` | ICH E2 and FDA safety-reporting distinctions |
| `privacy_and_deidentification.md` | HHS de-identification methods and process limits |
| `medical_terminology.md` | Versioned terminology and syntax-versus-semantics limits |
| `data_presentation.md` | Aggregate tables, denominators, units, dates, and missingness |
| `professional_review.md` | Ethics, accountability, review, and sign-off |
| `sources.md` | Dated official-source ledger |

## Source handling

`sources.md` records primary or official sources checked on 2026-07-23. Requirements, regional adoption, controlled terminologies, and professional standards can change. Before real-world use, a qualified reviewer must verify the current official source, applicable jurisdiction, institution, sponsor procedure, protocol, statistical analysis plan, and target-journal instructions.

## Terminology

“Required” in these references means required by the cited source within its stated scope, not universally required. “Complete” means structurally present in a manifest, not clinically correct. Script results never authorize use, release, signature, filing, or submission.

### `references/case_report_guidelines.md`

# CARE Case-Report Drafting

## Current source

The official CARE site continues to identify the **2013 CARE Checklist** as the core checklist. The 2017 explanation and elaboration supplies rationale and examples. CARE is reporting guidance for case reports; it does not authorize record access, establish consent, prove de-identification, or replace journal instructions.

## Thirteen checklist headings

Preserve the official structure:

1. title;
2. key words;
3. abstract;
4. introduction;
5. patient information;
6. clinical findings;
7. timeline;
8. diagnostic assessment;
9. therapeutic intervention;
10. follow-up and outcomes;
11. discussion;
12. patient perspective;
13. informed consent.

Use the official checklist and explanation for subitems. The local validator checks only that all headings have an allowed status and verified fact references; it does not judge clinical accuracy or CARE adherence.

## Safe use

- Begin with `assets/case_report_template.json`.
- Use de-identified source facts, not copied charts or free-text records.
- Keep direct identifiers and contact details out of the draft manifest.
- Represent chronology with relative study/case offsets when authorized and scientifically adequate; do not alter chronology to disguise conflicts.
- Preserve diagnostic and therapeutic statements as attributed facts from authorized records. Do not independently diagnose, rationalize treatment, or recommend care.
- Attribute the patient perspective to an authorized source; never invent a quote.
- Keep uncertainty, missing follow-up, adverse outcomes, and limitations visible.
- Do not claim novelty until an accountable author has reviewed the literature.
- Avoid causal or general treatment claims from a single case.

## Consent and privacy

CARE includes informed consent as an item, but a template cannot obtain or verify consent.

- Record only a consent status verified by the responsible human reviewer.
- Do not create a stock statement asserting that consent was obtained.
- Consent for publication and HIPAA de-identification are separate questions.
- De-identification does not necessarily remove all re-identification risk, particularly for rare conditions, small communities, images, unusual timelines, or distinctive combinations.
- Journal, institution, law, ethics-board policy, and circumstances involving minors, deceased persons, or persons unable to consent require qualified review.

## Fail-closed statuses

Each CARE item uses one of:

- `verified_present` — supported by one or more verified source-fact IDs;
- `not_applicable_with_rationale` — a qualified reviewer supplied a recorded rationale;
- `missing` — blocks structural readiness;
- `conflict` — source records disagree and human resolution is required.

The consent item cannot be waived by the script. A missing or unresolved consent status blocks publication handoff.

## Qualified review

Before any journal handoff, accountable authors and the appropriate clinical, privacy/legal, and institutional reviewers must verify:

- source accuracy and chronology;
- consent and authorization;
- privacy and image/metadata handling;
- terminology and clinical interpretation;
- discussion claims and citations;
- conflicts, limitations, and adverse outcomes;
- the target journal’s current instructions.

A structural result of `STRUCTURE_COMPLETE_REVIEW_REQUIRED` is not permission to submit.

### `references/clinical_trial_reporting.md`

# Clinical-Trial Reporting

## Keep the artifacts distinct

- **Protocol**: planned design and conduct. Route randomized-trial protocols to SPIRIT 2025.
- **Results manuscript**: completed trial reporting for publication. Route randomized-trial results to CONSORT 2025.
- **Clinical Study Report (CSR)**: integrated clinical and statistical report of an individual study. Route to ICH E3 and its Q&A.
- **Safety report**: individual or aggregate safety communication. Route separately; see `safety_reporting.md`.

One checklist does not substitute for another.

## CONSORT 2025

The official SPIRIT–CONSORT site describes CONSORT 2025 as a **30-item** minimum checklist plus a participant flow diagram for results of randomized trials. The primary statement was published 14 April 2025.

Use the statement, expanded checklist, and explanation/elaboration together. Check the current extension catalogue for every applicable design, data, intervention, and population extension. In particular, consider the current harms extension for adverse-event reporting.

The local template stores item IDs `C01`–`C30`; it does not reproduce, reinterpret, or score the checklist. A qualified methodologist must map each item to the official wording and resolve interactions with extensions.

Do not:

- fabricate a flow count or reason;
- infer analysis populations, endpoints, estimands, missing-data methods, or harms;
- add a figure when no verified data support it;
- treat a reporting checklist as proof of valid conduct or analysis.

## SPIRIT 2025

SPIRIT 2025 is the current reporting guideline for randomized-trial protocols. It was published 28 April 2025, contains **34 minimum items** plus a participant timeline figure, and supersedes SPIRIT 2013.

Notable updated areas include open science, harms assessment, intervention/comparator description, and patient/public involvement. Use the statement, expanded checklist, explanation/elaboration, and applicable extensions together.

The local template stores item IDs `S01`–`S34`. It checks item coverage only. It does not create a protocol, design a trial, select endpoints, specify interventions or doses, perform ethics review, or authorize conduct.

## ICH E3 Clinical Study Reports

ICH E3 reached Step 4 on 30 November 1995. The current E3 Q&A (R1), dated 6 July 2012, states that E3 is guidance rather than a rigid required template and may be adapted with justified additions, deletions, renaming, or reordering.

The structural validator expects these canonical sections:

1. Title Page
2. Synopsis
3. Table of Contents for the Individual Clinical Study Report
4. List of Abbreviations and Definitions of Terms
5. Ethics
6. Investigators and Study Administrative Structure
7. Introduction
8. Study Objectives
9. Investigational Plan
10. Study Patients
11. Efficacy Evaluation
12. Safety Evaluation
13. Discussion and Overall Conclusions
14. Tables, Figures, and Graphs Referred to but Not Included in the Text
15. Reference List
16. Appendices

Use `not_applicable_with_rationale` only when the study design and a qualified regulatory reviewer support the adaptation. The validator does not assess scientific content, appendices, eCTD placement, regional acceptability, or submission readiness.

## ICH E6(R3)

ICH adopted E6(R3) Principles and Annex 1 on 6 January 2025, Annex 2 on 3 June 2026, and a consolidated final guideline on 16 June 2026.

The guideline:

- applies to interventional trials of investigational products intended for regulatory submission, while principles may be applicable more broadly under local requirements;
- uses flexible, fit-for-purpose, proportionate, risk-based approaches;
- emphasizes participant rights, safety, and well-being and reliable results;
- requires attention to data governance, records, security, quality management, provenance, and traceability;
- expects the sponsor to describe the trial quality-management approach in the CSR.

Step 4 adoption does not prove regional implementation. A qualified regulatory professional must verify the applicable adopted version and transition rules.

## Data integrity and provenance

For every populated field:

- retain the protocol/SAP-defined population and endpoint language;
- identify the verified source and field path;
- preserve prespecified versus post hoc status;
- preserve database-cut and coding-dictionary versions;
- report denominators and missingness explicitly;
- record transformations and reconciliation decisions made by accountable humans;
- expose unresolved discrepancies.

Do not copy subject-level listings into local examples or tests. Use aggregate manifests and hashes.

## Review owners

- accountable clinical author: clinical interpretation;
- trial statistician: analysis populations, estimands, methods, outputs, and denominators;
- safety physician/professional: safety interpretation and individual-case decisions;
- data management/quality: source lineage and reconciliation;
- privacy/legal/ethics: authorization and disclosure;
- regulatory professional: CSR structure, regional rules, and submission package.

No script result replaces any of these reviews.

### `references/data_presentation.md`

# Aggregate Data Presentation

Present verified outputs without changing their meaning. Do not calculate a clinical conclusion, select an analysis, or repair source discrepancies.

## Mandatory table metadata

Every table should identify:

- artifact and analysis purpose;
- data cut and source-output version;
- analysis population/set;
- treatment/group labels;
- denominator for every group and row when it varies;
- whether a value is a subject count, event count, observation count, or estimate;
- units, time point/window, and summary statistic;
- missing, unknown, not assessed, suppressed, or not applicable values;
- coding dictionary/version/language where applicable;
- statistical method and multiplicity status only when copied from a verified output;
- provenance manifest and reviewer status.

## Counts and denominators

- Show `n/N (%)`, not a percentage alone, unless the governing output specifies another form.
- Require `0 <= n <= N` and `N > 0`.
- Recalculate only for consistency checking; do not silently replace the reported percentage.
- State the rounding rule and tolerance.
- Do not add subgroup percentages when the subgroup denominator is unknown.
- Do not infer that denominators are randomized, treated, evaluable, or safety populations.
- Keep event counts distinct from subjects affected; event counts can exceed the number of subjects.
- Do not sum non-mutually-exclusive categories.

## Dates and time

- Use ISO 8601 in structured manifests.
- Preserve source timezone and precision.
- Distinguish event date, collection date, database cut, report date, and verification date.
- Flag start-after-end and conflicting dates.
- Do not impute a missing day, month, timezone, or chronology.
- For de-identified case reports, use an authorized relative timeline; do not distort intervals.

## Units and precision

- Preserve source units.
- Require a unit for every dimensional quantity.
- Use one verified unit per comparable series or expose the mismatch.
- Do not convert or normalize without an authorized traceable conversion rule.
- Preserve clinically meaningful precision; do not create extra significant digits.
- Identify SD, SE, CI, IQR, range, and denominator explicitly.

## Missing and suppressed values

Keep these states distinct:

- `missing`;
- `not_collected`;
- `not_assessed`;
- `unknown`;
- `not_applicable`;
- `suppressed_for_privacy`;
- `zero`.

Never convert a blank to zero. State small-cell suppression rules and ensure totals or complementary cells do not reveal suppressed values.

## Adverse-event tables

For term-level aggregate tables:

- state MedDRA version and language;
- state analysis set and denominator;
- state counting rule from the verified SAP/output;
- show subjects affected and event count separately;
- do not add p-values or causal labels;
- do not interpret between-group differences;
- preserve threshold rules exactly;
- have safety and statistical reviewers verify deduplication, hierarchy, and population.

## Figures

No figure is mandatory. Create one only when requested, supported by verified aggregate data, allowed by the target guidance, and reviewable without external image generation.

A CONSORT flow diagram is part of CONSORT 2025 reporting, but every count and reason must come from verified trial outputs. A missing count remains missing; do not create a decorative or inferred diagram.

## Deterministic consistency check

`consistency_checker.py` can inspect:

- ISO date and range ordering;
- unit-label consistency;
- `n/N (%)` arithmetic;
- component-total arithmetic.

It reports mismatches and review needs. It does not change the input, choose the correct source, or validate clinical/statistical meaning.

### `references/diagnostic_reports_standards.md`

# Diagnostic-Report Scaffolds

These assets are structured field maps for authorized clinical services. They do not interpret data or produce a report suitable for patient care.

## Radiology

The ACR **Practice Parameter for Communication of Diagnostic Imaging Findings**, revised 2025 (Resolution 9), addresses diagnostic imaging reports, final-report principles, preliminary reports, nonroutine communication, informal communication, and organizational communication policies.

Use `assets/radiology_report_template.json` only to map verified facts such as:

- examination identity and status;
- clinical indication as supplied;
- technique and documented limitations;
- comparison-source references;
- findings and impression authored by the qualified interpreting professional;
- nonroutine-communication record references;
- amendments/corrections and report version.

Do not:

- inspect or interpret images;
- generate normal findings, pertinent negatives, differential diagnoses, urgency, follow-up, or management recommendations;
- select BI-RADS, LI-RADS, Lung-RADS, PI-RADS, or another category;
- infer that a preliminary report is final;
- initiate, simulate, or document a communication that did not occur.

The responsible radiologist and organization control report content, communication, correction, and signature.

## Pathology

CAP publishes and updates organ- and specimen-specific Cancer Protocols. The CAP template page showed protocol updates on 17 June 2026 and a Breast DCIS correction on 24 June 2026 when checked. Protocol versions and required/core or conditional elements can change.

Use `assets/pathology_report_template.json` only after a qualified pathologist selects:

- exact organ/site and specimen/procedure;
- current CAP protocol title and version, if applicable;
- applicable biomarker protocol and staging edition;
- local laboratory/reporting requirements.

For CAP synoptic reporting within its scope, core and conditionally required data elements are represented as data-element/response pairs; applicability depends on the exact current protocol.

Do not:

- generate a gross or microscopic observation;
- determine diagnosis, grade, stage, margin status, biomarker interpretation, or adequacy;
- apply a generic cancer checklist in place of the current exact protocol;
- convert `cannot be determined` or `not applicable` into a definitive value;
- create a signature or final diagnosis.

## Laboratory

For applicable US nonwaived testing, 42 CFR 493.1291 addresses accurate and timely transmission, required report information, referral-laboratory handling, accessibility, and corrected reports. The exact regulation and laboratory policy control.

Use `assets/lab_report_template.json` only to map results already released by the performing laboratory or verified source system. Preserve:

- report status and version;
- performing laboratory/source-system reference;
- specimen and test identifiers held in the authorized system, not copied into examples;
- result, units, reference interval, flags, method, and comments exactly as released;
- correction link to both original and corrected reports;
- documented notification reference when one exists.

Do not:

- calculate, normalize, convert, interpret, flag, or suppress a patient result;
- supply a reference interval or “critical” threshold;
- infer specimen adequacy;
- recommend follow-up or treatment;
- alter a referral laboratory’s result or interpretation;
- release or sign a report.

## Privacy and record integrity

Operational diagnostic reports often require identifiers for positive patient matching. This skill does not process those production records. It accepts only synthetic, de-identified, or aggregate manifests. Use institution-controlled systems for real clinical records and follow applicable access, retention, correction, audit, and disclosure procedures.

Every draft scaffold must remain `DRAFT_NOT_FOR_CLINICAL_USE` until the responsible licensed service reviews and completes it in its authorized system.

### `references/medical_terminology.md`

# Versioned Terminology and Schema Checks

Terminology selection and coding are clinical/regulatory tasks. The local checker validates manifest shape and code syntax; it does not confirm that a code exists, is current, matches a display, or is clinically appropriate.

## Required manifest fields

For every coded item record:

- `system`: controlled system name;
- `system_uri`: canonical identifier supplied by the implementing organization;
- `code`;
- `display`;
- `version`;
- `language`;
- `source_fact_id`;
- `coding_status`: `verified_by_qualified_reviewer` or `unverified`;
- `verified_by_role` and `verified_at` when verified.

Do not infer a code from narrative text.

## MedDRA

- ICH developed MedDRA for regulatory information about human medical products.
- MedDRA 29.0 was released in March 2026, with a transition date of 4 May 2026.
- MedDRA uses a multiaxial hierarchy and version-specific currency/relationships.
- State exact version and language.
- Use the study/sponsor-authorized version, official licensed files, and current Points to Consider.
- Do not assume the newest release is the required release.

The aggregate adverse-event formatter accepts SOC and PT labels as supplied and does not validate hierarchy, codes, or coding quality.

## LOINC

LOINC identifies health observations, measurements, and documents. LOINC 2.82 was released 24 February 2026 and was current when checked.

- A valid-looking `number-checkdigit` string is only syntactic evidence.
- The method, property, timing, system/specimen, scale, and version can affect meaning.
- Verify against the official release or authorized terminology service.
- Review the LOINC license and third-party content terms.

## SNOMED CT

SNOMED CT concept identifiers are not clinically validated by their numeric shape.

- Use the applicable international edition, national extension, and effective date.
- Verify concept activity, module, description, and reference-set membership.
- Comply with SNOMED International and national licensing/distribution requirements.
- Do not embed or redistribute licensed terminology content through these assets.

## ICD-10-CM

ICD-10-CM changes by fiscal-year release and may require encounter, laterality, or placeholder characters.

- Record the exact release and applicable jurisdiction.
- Verify with official CDC/CMS files and coding guidance.
- A regex match cannot establish billability, specificity, sequencing, or clinical correctness.
- This skill does not support billing or reimbursement decisions.

## UCUM and units

Record the original unit exactly and, when an organization uses UCUM, record the verified UCUM expression separately. Do not automatically convert units in a report draft.

Any conversion must have:

- an authorized rule and version;
- original value/unit;
- converted value/unit;
- precision/rounding rule;
- source-fact and reviewer traceability.

The consistency checker flags missing or inconsistent unit labels but performs no clinical conversion.

## Optional local dictionary

`terminology_validator.py --dictionary <file.json>` can compare code/display/version tuples with a caller-supplied local dictionary. The dictionary must be an authorized bounded JSON file.

A match means only “matched this supplied dictionary.” It does not prove:

- the dictionary is official, complete, current, or licensed for the use;
- the chosen code is appropriate;
- the clinical statement is true;
- the report is compliant or ready for release.

Without a dictionary, the strongest result is `SCHEMA_VALID_SYNTAX_ONLY_REVIEW_REQUIRED`.

### `references/privacy_and_deidentification.md`

# Privacy and De-identification

This reference documents a review process. It is not legal advice, a technical de-identification service, or evidence of HIPAA compliance.

## HHS framework

HHS guidance under 45 CFR 164.514(b) describes two methods:

1. **Expert Determination** — a person with appropriate knowledge and experience applies generally accepted statistical and scientific principles and documents that re-identification risk is very small under the anticipated conditions.
2. **Safe Harbor** — specified identifiers are removed and the covered entity has no actual knowledge that remaining information could identify an individual.

A local script cannot perform Expert Determination, establish “no actual knowledge,” or decide whether an organization is a covered entity or business associate.

## Safe Harbor identifier categories

The responsible privacy professional must review the exact regulation and HHS guidance. The categories include:

1. names;
2. geographic subdivisions smaller than a state, subject to the specific ZIP-code rule;
3. date elements more specific than year directly related to an individual, plus the age rule for persons over 89;
4. telephone numbers;
5. fax numbers;
6. email addresses;
7. Social Security numbers;
8. medical record numbers;
9. health-plan beneficiary numbers;
10. account numbers;
11. certificate or license numbers;
12. vehicle identifiers and serial numbers;
13. device identifiers and serial numbers;
14. URLs;
15. IP addresses;
16. biometric identifiers;
17. full-face photographs and comparable images;
18. other unique identifying numbers, characteristics, or codes.

Removal of obvious patterns is insufficient. Initials, partial identifiers, metadata, free text, rare events, small cells, unusual dates, images, and combined quasi-identifiers may still identify a person.

## Minimum necessary

HHS states that covered entities generally take reasonable steps to limit uses, disclosures, and requests for PHI to the minimum necessary for the purpose. HHS also lists exceptions, including certain treatment disclosures, disclosures to the individual, authorized uses/disclosures, uses/disclosures required for HIPAA administration, HHS enforcement, and uses/disclosures required by law.

Do not apply the phrase mechanically. The responsible privacy/legal reviewer determines scope, exceptions, authorization, waiver, limited-data-set rules, and any more protective law or policy.

## Local process

1. Define purpose, recipient, authority, jurisdiction, and data class.
2. Exclude fields not needed for the purpose.
3. Keep source records in the authorized system; use field-path references and hashes in the draft workspace.
4. Select Safe Harbor, Expert Determination, or a documented synthetic/aggregate-data rationale through the responsible reviewer.
5. Review structured fields, free text, attachments, images, headers, filenames, metadata, and linked data.
6. Review combinations and small-cell/rare-case risk.
7. Record actual-knowledge review or Expert Determination documentation as applicable.
8. Verify access controls, storage, transmission, retention, and deletion under organizational policy.
9. Obtain privacy/legal/institutional approval for the intended disclosure.
10. Re-review after every content, recipient, or purpose change.

## What the checklist does

`assets/deidentification_process_checklist.json` and `scripts/check_deidentification.py` verify that required process fields are documented. They deliberately:

- do not scan patient free text;
- do not output detected identifiers;
- do not label a document `COMPLIANT`, `SAFE`, or `DEIDENTIFIED`;
- do not substitute for Expert Determination or legal review;
- remain blocked when required human review is missing.

The strongest successful result is `PROCESS_DOCUMENTED_REVIEW_REQUIRED`.

## Consent and authorization

Publication consent, research consent, HIPAA authorization, IRB/Privacy Board waiver, and permission to use an image are distinct. Do not infer one from another or generate a stock assertion.

Record only the status and local documentation reference verified by the responsible human. Never store a signed consent form or direct identifier in this skill’s assets, tests, or example manifests.

## Incident handling

If real PHI is unexpectedly present:

1. stop processing;
2. do not echo, copy, transform, or upload it;
3. preserve only the minimum operational information needed under policy;
4. notify the authorized privacy/security contact through the institution’s process;
5. do not independently determine breach status or notification duties.

### `references/professional_review.md`

# Professional, Ethical, and Human Review

## Accountability

Automation may organize verified facts but cannot assume professional accountability. A named, qualified human must review each domain and take responsibility in the authorized system.

The ICMJE Recommendations, updated January 2026, retain four authorship criteria: substantive contribution; drafting or critical review; final approval; and accountability for accuracy and integrity. Writing assistance alone does not confer authorship. An AI system cannot be an author or approve a manuscript.

## Research ethics

The World Medical Association states that the **2024 Declaration of Helsinki** is the current official version. It applies to medical research involving human participants, including identifiable material or data, and emphasizes:

- participant rights and interests over research goals;
- privacy and confidentiality;
- scientific validity and a documented protocol;
- independent research-ethics review;
- informed consent;
- transparency and reporting.

This skill neither performs ethics review nor determines whether an activity is research, exempt, or authorized.

## Clinical-record confidentiality

AMA Code of Medical Ethics Opinion 3.3.2 states that information recorded in patient care is confidential regardless of form and identifies access restriction, audit capability, security/integrity, retrieval, sharing, third-party access, and disposition as responsibilities for electronic records.

Use institution-controlled systems for real clinical records. Local draft manifests should contain source locators and hashes rather than PHI.

## Required reviewers by artifact

| Domain | Reviewer responsibility |
|---|---|
| Clinical case facts | Qualified clinician verifies facts, uncertainty, chronology, and interpretation |
| Radiology | Qualified radiologist authors findings/impression and communication status |
| Pathology | Qualified pathologist selects protocol/version and authors diagnosis |
| Laboratory | Authorized laboratory professional verifies released result, method, status, and corrections |
| Statistics | Qualified statistician verifies analysis set, estimand, method, denominator, missingness, and output |
| Safety | Qualified safety professional verifies coding, seriousness, severity, causality, expectedness, and reportability |
| Privacy/legal | Authorized reviewer verifies data use, consent/authorization, disclosure, de-identification method, and jurisdiction |
| Regulatory | Qualified professional verifies adopted guidance, regional requirements, format, and submission process |
| Publication | All accountable authors verify content and current journal instructions |

## Review record

Record:

- reviewer role, not a fabricated name;
- scope reviewed;
- source version and data cut;
- unresolved conflicts and limitations;
- review date;
- decision in the authorized workflow;
- reference to the real sign-off record.

Do not place a signature, license number, direct contact detail, or copied approval document in a synthetic asset.

## Prohibited claims

Never state that a script or checklist proves:

- clinical correctness;
- HIPAA compliance or de-identification;
- GCP compliance;
- CARE, CONSORT, SPIRIT, ICH, ACR, CAP, or CLIA compliance;
- ethics approval or informed consent;
- regulatory reportability;
- readiness for signature, filing, publication, or submission.

Permitted script language is limited to structural findings such as `BLOCKED`, `STRUCTURE_COMPLETE_REVIEW_REQUIRED`, or `PROCESS_DOCUMENTED_REVIEW_REQUIRED`.

## Corrections and conflicts

- Never overwrite a source fact.
- Keep original and corrected versions linked.
- Expose conflicting sources and stop dependent claims.
- Require the responsible reviewer to resolve conflicts in the authorized system.
- Re-run structural and consistency checks after any correction.

No local script signs, timestamps an approval, files, transmits, or submits an artifact.

### `references/report_type_routing.md`

# Report-Type Routing

Select one route before opening a template. Do not merge routes merely because artifacts share clinical data.

## Decision sequence

1. Is the artifact a patient-care record?
   Stop. This skill does not create SOAP notes, H&Ps, consultation notes, discharge summaries, prescriptions, orders, triage instructions, or signed diagnostic reports.
2. Is it a single clinical case intended for publication?
   Use CARE.
3. Is it a diagnostic-report scaffold controlled by a clinical service?
   Use ACR, the current specimen-specific CAP protocol, or CLIA as applicable.
4. Is it a randomized-trial protocol?
   Use SPIRIT 2025 and applicable extensions.
5. Is it a randomized-trial results manuscript?
   Use CONSORT 2025 and applicable extensions.
6. Is it an integrated report of one clinical study for regulatory review?
   Use ICH E3 plus E3 Q&A, with ICH E6(R3) and regional requirements as applicable.
7. Is it individual pre-approval safety information?
   Route to ICH E2A, E2B(R3), protocol/sponsor procedures, and regional requirements. Do not automate the reportability decision.
8. Is it individual post-approval safety information?
   Route to ICH E2D(R1), E2B(R3), marketing-authorisation-holder procedures, and regional requirements. Do not automate.
9. Is it an aggregate safety table?
   Use the protocol/SAP, ICH E3, CONSORT Harms when applicable, and the relevant regional aggregate-analysis guidance.
10. Is it an aggregate research summary?
    Use the reporting guideline for the actual design and the verified protocol/SAP. Do not imply clinical applicability.

## Route matrix

| Artifact | Base source | Add-ons | Do not substitute |
|---|---|---|---|
| Case report | CARE 2013 | CARE 2017 explanation; target journal | CONSORT, CSR, or diagnostic-report rules |
| Radiology scaffold | ACR 2025 communication parameter | Current modality/program standard and local policy | A generic impression generator |
| Cancer pathology scaffold | Current CAP protocol for exact organ/specimen | Current biomarker protocol and local policy | A static generic TNM checklist |
| Laboratory scaffold | 42 CFR 493.1291 for applicable US nonwaived testing | Method, specialty, state, accreditor, and laboratory policy | Hardcoded reference or critical ranges |
| Trial protocol | SPIRIT 2025 | Current design/data/intervention extensions | CONSORT results checklist |
| Randomized results | CONSORT 2025 | Current design/data/intervention extensions; CONSORT Harms | SPIRIT protocol checklist |
| CSR | ICH E3 and E3 Q&A | E6(R3), protocol, SAP, regional submission rules | CONSORT alone |
| Pre-approval ICSR | ICH E2A and E2B(R3) | Regional law/guidance and sponsor procedure | Aggregate formatter |
| Post-approval ICSR | ICH E2D(R1) and E2B(R3) | Regional law/guidance and MAH procedure | Pre-approval timing rules |
| Periodic aggregate safety | ICH E2C(R2), where applicable | Regional periodic-report rules | E2B message schema |

## CONSORT/SPIRIT extension selection

The base statements address standard randomized trials. Check the live official extension catalogue for:

- design: adaptive, cluster, cluster-crossover, crossover, dose-finding, factorial, multi-arm, non-inferiority/equivalence, N-of-1, pilot/feasibility, pragmatic, stepped-wedge, routine-data, or within-person;
- data: abstracts, harms, outcomes, patient-reported outcomes, surrogate outcomes, equity, and pathology;
- intervention/population: non-pharmacological, AI, social/psychological, children/adolescents, or other specialty extensions.

Some current extensions were developed against CONSORT 2010 or SPIRIT 2013. Use the current extension with the 2025 base statement, document any conflict, and have a qualified methodologist resolve it. Do not silently renumber or reinterpret extension items.

## Jurisdiction and role gate

ICH Step 4 adoption does not itself prove implementation in a jurisdiction. FDA guidance is generally nonbinding but regulations are legally operative within scope. Institutional policy, protocol, contracts, ethics determinations, and sponsor procedures may add or change duties.

Record the jurisdiction, regulated-product category, responsible role, source version/date, and reviewer before drafting. If any is unknown, mark the route `BLOCKED_UNRESOLVED`.

### `references/safety_reporting.md`

# Safety Reporting Boundaries

Safety reporting is role-, product-, phase-, source-, jurisdiction-, and time-dependent. This skill formats verified aggregate counts only. It does not determine seriousness, severity, causality, expectedness, reportability, clock start, destination, format, or follow-up.

## Core distinctions

- **Adverse event (AE)**: an untoward medical occurrence temporally associated with a medicinal product; causality is not required.
- **Adverse reaction / suspected adverse reaction**: a causal relationship is at least reasonably possible or otherwise meets the applicable regional definition.
- **Seriousness**: outcome or regulatory criterion such as death, life-threatening experience at the time, hospitalization, disability/incapacity, congenital anomaly, or another medically important event.
- **Severity**: intensity. A severe event is not automatically serious; a serious event need not be severe in intensity.
- **Expectedness**: comparison with the applicable reference safety information under the governing procedure.

Only an authorized qualified safety professional may make or approve these assessments.

## ICH routes

### E2A — pre-approval expedited reporting

ICH E2A (Step 4, 27 October 1994) defines standards for expedited reporting during clinical development. It describes minimum information for an initial report and the distinction among serious, unexpected, and suspected reactions.

Do not apply E2A as a universal post-approval rule or encode its timelines without the current regional requirement and sponsor procedure.

### E2B(R3) — ICSR electronic data and message specification

E2B(R3) defines data elements and electronic transmission for individual case safety reports. It covers pre- and post-approval ICSRs within scope. It does not:

- decide whether a case is reportable;
- define an aggregate safety table;
- replace E2A, E2D(R1), or regional rules;
- validate clinical coding or narrative accuracy.

The ICH index listed E2B(R3) Q&As at Step 5 dated 18 July 2025 when checked. Use the current implementation guide, Q&As, code lists, regional implementation guide, and receiving-system rules.

### E2D(R1) — post-approval individual cases

ICH adopted E2D(R1), **Post-Approval Safety Data: Definitions and Standards for Management and Reporting of Individual Case Safety Reports**, on 15 September 2025.

It addresses post-approval ICSR sources and case management, including organized data collection systems, literature, digital platforms, and patient-support programs. It explicitly directs users to:

- E2B for ICSR structure/format/data elements;
- E2C for periodic aggregate safety reporting;
- regional/local requirements where they differ.

Do not use the aggregate formatter for an ICSR or use E2D(R1) to invent missing case data.

### E2C(R2) — periodic aggregate reporting

Where applicable, E2C(R2) addresses periodic benefit-risk evaluation reporting. Applicability and regional format require qualified review. Aggregate tables in this skill are display aids, not periodic reports.

## FDA IND safety reporting

For applicable US IND studies, 21 CFR 312.32 controls sponsor IND safety reporting. FDA issued final sponsor and investigator safety-reporting guidances in December 2025. The sponsor guidance includes aggregate-data assessment considerations; the investigator guidance clarifies investigator-to-sponsor and IRB responsibilities.

FDA’s IND safety-reporting page, current 23 June 2026 when checked, states:

- sponsors report qualifying potential serious risks under 21 CFR 312.32;
- unexpected fatal or life-threatening suspected adverse reactions have a 7-calendar-day outer limit after the relevant sponsor determination/receipt described by the regulation;
- other qualifying reports generally use the applicable 15-calendar-day requirement;
- as of 1 April 2026, commercial IND reports under 21 CFR 312.32(c)(1)(i) use FDA AEMS with E2B(R3), with stated exemptions for noncommercial INDs;
- other categories described on the page use the applicable eCTD route.

This summary is not a reporting clock or filing instruction. The responsible sponsor, investigator, IRB/IEC, and regulatory professionals must consult the current regulation, guidance, protocol, and procedures for each event.

## Aggregate formatter input

`format_adverse_events.py` accepts only aggregate rows:

- analysis set;
- treatment group;
- MedDRA version;
- system organ class;
- preferred term;
- subjects affected;
- event count;
- denominator.

It also requires a populated `clinical_trial_safety_aggregate_template.json` sidecar
that records authorization, protocol/SAP/data-cut references, analysis set, counting
and threshold rules, MedDRA version/language, provenance, and pending human reviews.

It rejects row-level identifiers, verbatim narratives, case IDs, and onset dates. It checks arithmetic and group consistency but does not verify:

- MedDRA term/code validity;
- coding quality or hierarchy placement;
- treatment relatedness;
- seriousness or fatality;
- analysis-set correctness;
- deduplication;
- whether a subject appears in multiple terms or SOCs;
- statistical inference.

## MedDRA caveats

MedDRA 29.0 (March 2026; transition date 4 May 2026) was current when this skill was refreshed. A report must use the study/sponsor-authorized dictionary version, not automatically the newest version.

State the exact version and language. Terms can change currency, names, or hierarchy across releases; codes can persist through renames. Use licensed official files and MedDRA Points to Consider. A syntax checker cannot validate coding.

## Required handoff

Every aggregate table must disclose:

- analysis set and denominator per group;
- whether values are subjects, events, or both;
- MedDRA version and language;
- counting rules and threshold supplied by the protocol/SAP;
- missing or suppressed cells;
- no inferential claim unless separately verified;
- qualified safety and statistical review required;
- not suitable for individual-case submission.

### `references/sources.md`

# Official Source Ledger

**Research cutoff and access date:** 2026-07-23
**Method:** targeted `parallel-cli search` restricted to official or primary-source domains, followed by review of returned primary-source excerpts.
**Use:** source routing and version awareness only. Always verify the live source, jurisdictional adoption, and local requirements before real-world use.

## Case reports

- **CARE Case Report Guidelines — home and current toolkit.** Identifies the 2013 checklist and 2017 explanation. <https://www.care-statement.org/>
- **2013 CARE Checklist.** Thirteen main reporting items. <https://www.care-statement.org/checklist>
- **CARE publications.** Primary 2013 statement and 2017 explanation/elaboration references. <https://www.care-statement.org/publications>

## Randomized-trial protocols and results

- **SPIRIT–CONSORT official site.** SPIRIT 2025: 34-item protocol checklist and figure. CONSORT 2025: 30-item results checklist and flow diagram. <https://www.consort-spirit.org/>
- **CONSORT/SPIRIT extension catalogue.** Current design, data, intervention, and population extensions; catalogue notes which base statement each extension used. <https://www.consort-spirit.org/extensions>
- **CONSORT 2025 primary statement.** Published 2025-04-14. <https://www.bmj.com/content/389/bmj-2024-081123>
- **SPIRIT 2025 primary statement.** Published 2025-04-28; states that SPIRIT 2025 supersedes SPIRIT 2013. <https://www.bmj.com/content/389/bmj-2024-081477>
- **SPIRIT 2025 explanation and elaboration.** Published 2025-04-28. <https://www.bmj.com/content/389/bmj-2024-081660>

## ICH clinical-study and GCP guidance

- **ICH E3 — Structure and Content of Clinical Study Reports.** Step 4, 1995-11-30. <https://database.ich.org/sites/default/files/E3_Guideline.pdf>
- **ICH E3 Questions & Answers (R1).** Current version dated 2012-07-06; clarifies that E3 is adaptable guidance, not a rigid template. <https://database.ich.org/sites/default/files/E3_Q%26As_R1_Q%26As.pdf>
- **ICH E6(R3) consolidated final guideline.** Principles, Annex 1, and Annex 2; adopted 2026-06-16. <https://database.ich.org/sites/default/files/ICH%20E6%28R3%29_Step4_FinalConsolidatedGuideline_2026_0616_.pdf>
- **ICH E6(R3) Annex 2 final.** Adopted 2026-06-03. <https://database.ich.org/sites/default/files/ICH_E6%28R3%29_Annex%202_Guideline_Step%204_2026_0603_0.pdf>
- **FDA ICH guidance index.** FDA’s current US ICH guidance entry point; verify regional adoption here. Content current 2026-04-16 when checked. <https://www.fda.gov/science-research/clinical-trials-and-human-subject-protection/ich-guidance-documents>

## Safety reporting

- **ICH E2A — Clinical Safety Data Management: Definitions and Standards for Expedited Reporting.** Step 4, 1994-10-27. <https://database.ich.org/sites/default/files/E2A_Guideline.pdf>
- **ICH E2B(R3) ICSR specification and related files.** Current implementation-guide, Q&A, code-list, and alignment entry point. <https://www.ich.org/page/e2br3-individual-case-safety-report-icsr-specification-and-related-files>
- **ICH guideline index.** Listed E2B(R3) Q&As at Step 5 dated 2025-07-18 and E2D(R1) at Step 5 dated 2025-09-15 when checked. <https://www.ich.org/page/search-index-ich-guidelines>
- **ICH E2D(R1) — Post-Approval Safety Data: Definitions and Standards for Management and Reporting of Individual Case Safety Reports.** Adopted 2025-09-15. <https://database.ich.org/sites/default/files/ICH_E2D%28R1%29_Step4_FinalGuideline_2025_0819.pdf>
- **21 CFR 312.32 — IND safety reporting.** Current eCFR text; verify current effective text and official annual CFR. <https://www.ecfr.gov/current/title-21/chapter-I/subchapter-D/part-312/subpart-B/section-312.32>
- **FDA IND Application Reporting: IND Safety Reports.** Content current 2026-06-23; includes AEMS/E2B(R3) electronic route effective 2026-04-01 within stated scope. <https://www.fda.gov/drugs/investigational-new-drug-ind-application/ind-application-reporting-ind-safety-reports>
- **FDA Sponsor Responsibilities — Safety Reporting Requirements and Safety Assessment for IND and BA/BE Studies.** Final guidance, December 2025. <https://www.fda.gov/regulatory-information/search-fda-guidance-documents/sponsor-responsibilities-safety-reporting-requirements-and-safety-assessment-ind-and>
- **FDA Investigator Responsibilities — Safety Reporting for Investigational Drugs and Devices.** Final guidance, December 2025. <https://www.fda.gov/regulatory-information/search-fda-guidance-documents/investigator-responsibilities-safety-reporting-investigational-drugs-and-devices>
- **FDA Postmarketing Adverse Event Reporting Compliance Program.** Content current 2025-12-19 when checked. <https://www.fda.gov/drugs/surveillance-post-drug-approval-activities/postmarketing-adverse-event-reporting-compliance-program>

## Privacy and de-identification

- **HHS Guidance Regarding Methods for De-identification of PHI.** Safe Harbor and Expert Determination under 45 CFR 164.514(b); page reviewed 2026-03-20. <https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html>
- **HHS Minimum Necessary Requirement.** 45 CFR 164.502(b) and 164.514(d), scope and exceptions. <https://www.hhs.gov/hipaa/for-professionals/privacy/guidance/minimum-necessary-requirement/index.html>

## Diagnostic reporting

- **ACR Practice Parameter for Communication of Diagnostic Imaging Findings.** Revised 2025 (Resolution 9). <https://gravitas.acr.org/PPTS/GetDocumentView?docId=74>
- **ACR Practice Parameters & Technical Standards portal.** Current modality- and program-specific source. <https://gravitas.acr.org/PPTS>
- **CAP Cancer Protocol Templates.** Current protocol downloads and 2026 change notices; page showed updates through 2026-06-24 when checked. <https://www.cap.org/protocols-and-guidelines/cancer-reporting-tools/cancer-protocol-templates>
- **CAP Cancer Protocols.** Current scope and synoptic-reporting entry point. <https://www.cap.org/protocols-and-guidelines/cancer-reporting-tools/cancer-protocols>
- **42 CFR 493.1291 — Test report.** CLIA postanalytic report requirements for applicable testing, including corrected-report handling. <https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-493/subpart-K/subject-group-ECFR9482366886d579f/section-493.1291>
- **42 CFR 493.1105 — Retention requirements.** Includes original, preliminary, final, and corrected-report retention provisions within scope. <https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-G/part-493/subpart-J/section-493.1105>

## Terminology

- **ICH MedDRA.** Governance, purpose, and Points to Consider. <https://www.ich.org/page/meddra>
- **MedDRA English support documentation.** Lists MedDRA 29.0 (March 2026), transition date 2026-05-04, and versioned support documents. <https://www.meddra.org/how-to-use/support-documentation/english/welcome>
- **MedDRA 29.0 Introductory Guide.** March 2026 hierarchy and version context. <https://alt.meddra.org/files_acrobat/intguide_29_0_English.pdf>
- **LOINC.** Version 2.82 released 2026-02-24; next release listed for August 2026 when checked. <https://loinc.org/>
- **SNOMED International licensing.** Member/non-member use and licensing conditions. <https://www.snomed.org/licensing>
- **NLM SNOMED CT licensing.** US distribution and licensing entry point. <https://www.nlm.nih.gov/healthit/snomedct/snomed_licensing.html>

## Ethics and professional publication guidance

- **WMA Declaration of Helsinki.** Current official version adopted October 2024; previous versions superseded for current use. <https://www.wma.net/policies-post/wma-declaration-of-helsinki>
- **ICMJE Recommendations.** Updated January 2026; authorship, accountability, participant protection, privacy, and publication practices. <https://www.icmje.org/icmje-recommendations.pdf>
- **AMA Code of Medical Ethics Opinion 3.3.2 — Confidentiality & Electronic Medical Records.** Electronic-record confidentiality, access, audit, security, integrity, sharing, and disposition. <https://code-medical-ethics.ama-assn.org/ethics-opinions/confidentiality-electronic-medical-records>

## Known source limitations

- eCFR is continuously updated but identifies itself as an unofficial online edition; use the current official annual CFR and legal review when status matters.
- ICH Step 4 documents require regional adoption/implementation review.
- Controlled terminologies and professional standards can change after this ledger date.
- Journal instructions, local policies, protocols, SAPs, contracts, and ethics determinations are not captured here.

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Bounded local-file and validation helpers for clinical-reports scripts."""

from __future__ import annotations

import json
import math
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

MAX_JSON_BYTES = 1_000_000
MAX_CSV_BYTES = 5_000_000
MAX_CSV_ROWS = 10_000
MAX_NODES = 25_000
MAX_DEPTH = 24
MAX_TEXT_LENGTH = 2_000

ALLOWED_DATA_CLASSES = {"synthetic", "deidentified", "aggregate"}
IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


class ValidationError(ValueError):
    """Raised for fail-closed input validation errors."""


def _reject_nonlocal(raw: str) -> None:
    if not raw or "\x00" in raw:
        raise ValidationError("path must be a non-empty local filesystem path")
    if "://" in raw or raw.startswith(("file:", "\\\\")):
        raise ValidationError("URLs, URI schemes, and network paths are not allowed")


def local_input_path(
    raw: str,
    *,
    suffixes: Iterable[str],
    max_bytes: int,
) -> Path:
    """Resolve a bounded, regular, non-symlink local input file."""
    _reject_nonlocal(raw)
    path = Path(raw).expanduser()
    if path.is_symlink():
        raise ValidationError("symbolic-link inputs are not allowed")
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValidationError(f"input file does not exist: {path}") from exc
    if not resolved.is_file():
        raise ValidationError("input must be a regular file")
    allowed = {suffix.lower() for suffix in suffixes}
    if resolved.suffix.lower() not in allowed:
        raise ValidationError(f"input suffix must be one of: {sorted(allowed)}")
    size = resolved.stat().st_size
    if size <= 0:
        raise ValidationError("input file is empty")
    if size > max_bytes:
        raise ValidationError(f"input exceeds {max_bytes} bytes")
    return resolved


def local_output_path(
    raw: str,
    *,
    suffixes: Iterable[str],
    overwrite: bool,
) -> Path:
    """Resolve a local output whose existing parent directory is trusted."""
    _reject_nonlocal(raw)
    path = Path(raw).expanduser()
    allowed = {suffix.lower() for suffix in suffixes}
    if path.suffix.lower() not in allowed:
        raise ValidationError(f"output suffix must be one of: {sorted(allowed)}")
    if path.exists():
        if path.is_symlink() or not path.is_file():
            raise ValidationError("existing output must be a regular non-symlink file")
        if not overwrite:
            raise ValidationError("output exists; pass --overwrite to replace it")
    parent = path.parent
    if parent.is_symlink():
        raise ValidationError("symbolic-link output directories are not allowed")
    try:
        resolved_parent = parent.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValidationError("output parent directory must already exist") from exc
    if not resolved_parent.is_dir():
        raise ValidationError("output parent is not a directory")
    return resolved_parent / path.name


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _check_tree(value: Any, *, depth: int = 0, counter: list[int] | None = None) -> None:
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > MAX_NODES:
        raise ValidationError(f"JSON exceeds {MAX_NODES} nodes")
    if depth > MAX_DEPTH:
        raise ValidationError(f"JSON exceeds maximum depth {MAX_DEPTH}")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or len(key) > 128:
                raise ValidationError("JSON object keys must be strings of at most 128 characters")
            _check_tree(child, depth=depth + 1, counter=counter)
    elif isinstance(value, list):
        for child in value:
            _check_tree(child, depth=depth + 1, counter=counter)
    elif isinstance(value, str):
        if len(value) > MAX_TEXT_LENGTH:
            raise ValidationError(
                f"JSON strings may not exceed {MAX_TEXT_LENGTH} characters"
            )
        if any(ord(char) < 32 and char not in "\t\n\r" for char in value):
            raise ValidationError("JSON strings contain disallowed control characters")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValidationError("non-finite numbers are not allowed")


def load_json_object(raw_path: str) -> tuple[Path, dict[str, Any]]:
    """Load a bounded JSON object with duplicate-key and depth checks."""
    path = local_input_path(
        raw_path,
        suffixes={".json"},
        max_bytes=MAX_JSON_BYTES,
    )
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_object_without_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValidationError(f"invalid JSON number: {token}")
            ),
        )
    except UnicodeDecodeError as exc:
        raise ValidationError("JSON input must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValidationError("top-level JSON value must be an object")
    _check_tree(value)
    return path, value


def write_json_report(
    report: dict[str, Any],
    raw_output: str | None,
    *,
    overwrite: bool,
) -> None:
    """Print JSON or write it to an explicitly bounded local path."""
    rendered = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if raw_output is None:
        print(rendered, end="")
        return
    output = local_output_path(
        raw_output,
        suffixes={".json"},
        overwrite=overwrite,
    )
    output.write_text(rendered, encoding="utf-8")


def require_data_class(value: Any) -> str:
    """Require an allowed, explicitly declared data class."""
    if value not in ALLOWED_DATA_CLASSES:
        raise ValidationError(
            f"data classification must be one of: {sorted(ALLOWED_DATA_CLASSES)}"
        )
    return str(value)


def require_exact_keys(
    value: Any,
    expected: Iterable[str],
    field: str,
) -> dict[str, Any]:
    """Reject missing and unknown fields in a structured object."""
    if not isinstance(value, dict):
        raise ValidationError(f"{field} must be an object")
    expected_set = set(expected)
    missing = sorted(expected_set - set(value))
    extra = sorted(set(value) - expected_set)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing={missing}")
        if extra:
            details.append(f"unknown={extra}")
        raise ValidationError(f"{field} fields are invalid ({'; '.join(details)})")
    return value


def require_identifier(value: Any, field: str) -> str:
    """Require a bounded machine identifier."""
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise ValidationError(f"{field} must match {IDENTIFIER_RE.pattern}")
    return value


def require_string(value: Any, field: str, *, max_length: int = 256) -> str:
    """Require a non-empty bounded string."""
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be a string")
    normalized = value.strip()
    if not normalized or len(normalized) > max_length:
        raise ValidationError(f"{field} must contain 1-{max_length} characters")
    return normalized


def require_bool(value: Any, field: str) -> bool:
    """Require an actual JSON boolean."""
    if not isinstance(value, bool):
        raise ValidationError(f"{field} must be a boolean")
    return value


def require_nonnegative_int(value: Any, field: str) -> int:
    """Require an integer count without accepting booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValidationError(f"{field} must be a non-negative integer")
    return value


def parse_iso_date(value: Any, field: str) -> date:
    """Parse an ISO calendar date without inferring missing precision."""
    text = require_string(value, field, max_length=10)
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationError(f"{field} must be YYYY-MM-DD") from exc


def parse_iso_datetime(value: Any, field: str) -> datetime:
    """Parse an ISO datetime and require an explicit timezone."""
    text = require_string(value, field, max_length=40)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field} must be an ISO 8601 datetime") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{field} must include a timezone")
    return parsed


def error_report(tool: str, exc: Exception) -> dict[str, Any]:
    """Return a non-sensitive machine-readable error."""
    return {
        "tool": tool,
        "status": "BLOCKED_INVALID_INPUT",
        "errors": [str(exc)],
        "review_required": True,
        "authorizes_clinical_use_or_submission": False,
    }
```

### `scripts/check_deidentification.py`

```python
#!/usr/bin/env python3
"""Validate de-identification process documentation without scanning patient text."""

from __future__ import annotations

import argparse
import sys
from typing import Any

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    ValidationError,
    error_report,
    load_json_object,
    require_bool,
    require_data_class,
    require_exact_keys,
    require_string,
    write_json_report,
)

TOOL = "check_deidentification"
SAFE_HARBOR_KEYS = (
    "names",
    "geographic_subdivisions",
    "dates_and_ages",
    "telephone_numbers",
    "fax_numbers",
    "email_addresses",
    "social_security_numbers",
    "medical_record_numbers",
    "health_plan_numbers",
    "account_numbers",
    "certificate_and_license_numbers",
    "vehicle_identifiers",
    "device_identifiers",
    "urls",
    "ip_addresses",
    "biometric_identifiers",
    "full_face_images",
    "other_unique_characteristics_or_codes",
)
RESIDUAL_KEYS = (
    "free_text",
    "small_cells_and_rare_cases",
    "images_and_metadata",
    "linked_data_and_quasi_identifiers",
)
METHODS = {
    "safe_harbor",
    "expert_determination",
    "not_applicable_synthetic_or_aggregate",
}
CLEAR_STATUSES = {"cleared_by_authorized_reviewer", "not_present_by_design"}
RESIDUAL_CLEAR_STATUSES = {
    "reviewed_no_unresolved_issue",
    "not_applicable_with_rationale",
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "artifact_kind",
    "process_status",
    "safety_notice",
    "data_scope",
    "authorized_purpose",
    "authorization_verified",
    "local_only_handling_confirmed",
    "minimum_necessary_reviewed",
    "method",
    "safe_harbor_identifiers",
    "actual_knowledge_review",
    "expert_determination",
    "synthetic_or_aggregate_rationale",
    "residual_risk_review",
    "review",
}


def _required_true(
    data: dict[str, Any],
    field: str,
    errors: list[str],
) -> None:
    try:
        if not require_bool(data.get(field), field):
            errors.append(f"{field} must be true")
    except ValidationError as exc:
        errors.append(str(exc))


def validate_process(data: dict[str, Any]) -> dict[str, Any]:
    """Validate recorded process gates without asserting de-identification."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        require_exact_keys(data, TOP_LEVEL_FIELDS, "checklist")
        if data.get("schema_version") != "2.0":
            raise ValidationError("schema_version must be 2.0")
        if data.get("process_status") != "BLOCKED_NOT_ASSESSED":
            raise ValidationError("process_status must remain BLOCKED_NOT_ASSESSED")
        require_string(data.get("safety_notice"), "safety_notice", max_length=1000)
        require_exact_keys(
            data.get("safe_harbor_identifiers"),
            SAFE_HARBOR_KEYS,
            "safe_harbor_identifiers",
        )
        require_exact_keys(
            data.get("actual_knowledge_review"),
            {"completed_by_authorized_privacy_reviewer", "record_reference"},
            "actual_knowledge_review",
        )
        require_exact_keys(
            data.get("expert_determination"),
            {
                "completed_by_qualified_expert",
                "expert_documentation_reference",
                "anticipated_recipient_and_conditions_documented",
            },
            "expert_determination",
        )
        require_exact_keys(
            data.get("synthetic_or_aggregate_rationale"),
            {"origin_verified", "record_reference"},
            "synthetic_or_aggregate_rationale",
        )
        require_exact_keys(
            data.get("residual_risk_review"),
            RESIDUAL_KEYS,
            "residual_risk_review",
        )
        require_exact_keys(
            data.get("review"),
            {
                "privacy_legal_review",
                "institutional_release_review",
                "release_authorized",
            },
            "review",
        )
    except ValidationError as exc:
        errors.append(str(exc))
    if data.get("artifact_kind") != "deidentification_process_checklist":
        errors.append("artifact_kind must be deidentification_process_checklist")
    try:
        data_scope = require_data_class(data.get("data_scope"))
        require_string(data.get("authorized_purpose"), "authorized_purpose")
    except ValidationError as exc:
        errors.append(str(exc))
        data_scope = ""

    for field in (
        "authorization_verified",
        "local_only_handling_confirmed",
        "minimum_necessary_reviewed",
    ):
        _required_true(data, field, errors)

    method = data.get("method")
    if method not in METHODS:
        errors.append(f"method must be one of {sorted(METHODS)}")
    elif method == "safe_harbor":
        statuses = data.get("safe_harbor_identifiers")
        if not isinstance(statuses, dict):
            errors.append("safe_harbor_identifiers must be an object")
        else:
            missing = sorted(set(SAFE_HARBOR_KEYS) - set(statuses))
            extra = sorted(set(statuses) - set(SAFE_HARBOR_KEYS))
            if missing:
                errors.append(f"missing Safe Harbor categories: {missing}")
            if extra:
                errors.append(f"unexpected Safe Harbor categories: {extra}")
            for key in SAFE_HARBOR_KEYS:
                if statuses.get(key) not in CLEAR_STATUSES:
                    errors.append(f"safe_harbor_identifiers.{key} is not cleared")
        actual = data.get("actual_knowledge_review")
        if not isinstance(actual, dict):
            errors.append("actual_knowledge_review must be an object")
        else:
            try:
                if not require_bool(
                    actual.get("completed_by_authorized_privacy_reviewer"),
                    "actual_knowledge_review.completed_by_authorized_privacy_reviewer",
                ):
                    errors.append("authorized actual-knowledge review is required")
                require_string(
                    actual.get("record_reference"),
                    "actual_knowledge_review.record_reference",
                )
            except ValidationError as exc:
                errors.append(str(exc))
    elif method == "expert_determination":
        expert = data.get("expert_determination")
        if not isinstance(expert, dict):
            errors.append("expert_determination must be an object")
        else:
            try:
                if not require_bool(
                    expert.get("completed_by_qualified_expert"),
                    "expert_determination.completed_by_qualified_expert",
                ):
                    errors.append("qualified Expert Determination is required")
                require_string(
                    expert.get("expert_documentation_reference"),
                    "expert_determination.expert_documentation_reference",
                )
                if not require_bool(
                    expert.get("anticipated_recipient_and_conditions_documented"),
                    "expert_determination.anticipated_recipient_and_conditions_documented",
                ):
                    errors.append("anticipated recipient and conditions must be documented")
            except ValidationError as exc:
                errors.append(str(exc))
    elif method == "not_applicable_synthetic_or_aggregate":
        if data_scope not in {"synthetic", "aggregate"}:
            errors.append(
                "not_applicable_synthetic_or_aggregate requires synthetic or aggregate scope"
            )
        rationale = data.get("synthetic_or_aggregate_rationale")
        if not isinstance(rationale, dict):
            errors.append("synthetic_or_aggregate_rationale must be an object")
        else:
            try:
                if not require_bool(
                    rationale.get("origin_verified"),
                    "synthetic_or_aggregate_rationale.origin_verified",
                ):
                    errors.append("synthetic or aggregate origin must be verified")
                require_string(
                    rationale.get("record_reference"),
                    "synthetic_or_aggregate_rationale.record_reference",
                )
            except ValidationError as exc:
                errors.append(str(exc))

    residual = data.get("residual_risk_review")
    if not isinstance(residual, dict):
        errors.append("residual_risk_review must be an object")
    else:
        for key in RESIDUAL_KEYS:
            if residual.get(key) not in RESIDUAL_CLEAR_STATUSES:
                errors.append(f"residual_risk_review.{key} is unresolved")

    review = data.get("review")
    if not isinstance(review, dict):
        errors.append("review must be an object")
    else:
        for field in ("privacy_legal_review", "institutional_release_review"):
            if review.get(field) != "completed":
                warnings.append(f"review.{field} remains required")
        if review.get("release_authorized") is not False:
            errors.append("review.release_authorized must remain false")

    return {
        "tool": TOOL,
        "status": "BLOCKED" if errors else "PROCESS_DOCUMENTED_REVIEW_REQUIRED",
        "method": method,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "No patient text or files were scanned.",
            "Does not establish de-identification, no-actual-knowledge, Expert Determination, or HIPAA compliance.",
        ],
        "review_required": True,
        "authorizes_release_or_submission": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check bounded JSON de-identification process documentation. "
            "Never labels data HIPAA-compliant or guaranteed de-identified."
        )
    )
    parser.add_argument("input_file", help="Local process checklist (.json)")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _, data = load_json_object(args.input_file)
        report = validate_process(data)
    except (OSError, ValidationError) as exc:
        report = error_report(TOOL, exc)
    try:
        write_json_report(report, args.output, overwrite=args.overwrite)
    except (OSError, ValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0 if report["status"] == "PROCESS_DOCUMENTED_REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/consistency_checker.py`

```python
#!/usr/bin/env python3
"""Check structured dates, units, denominators, percentages, and totals."""

from __future__ import annotations

import argparse
import math
import sys
from typing import Any

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    ValidationError,
    error_report,
    load_json_object,
    parse_iso_date,
    require_bool,
    require_data_class,
    require_exact_keys,
    require_identifier,
    require_nonnegative_int,
    require_string,
    write_json_report,
)

TOOL = "consistency_checker"
TOP_LEVEL_FIELDS = {
    "schema_version",
    "artifact_kind",
    "manifest_status",
    "safety_notice",
    "data_classification",
    "authorized_purpose",
    "authorization_verified",
    "provenance_manifest",
    "dates",
    "date_ranges",
    "quantities",
    "proportions",
    "totals",
}


def _array(data: dict[str, Any], field: str, errors: list[str]) -> list[Any]:
    value = data.get(field, [])
    if not isinstance(value, list):
        errors.append(f"{field} must be an array")
        return []
    if len(value) > 10_000:
        errors.append(f"{field} may contain at most 10,000 items")
        return value[:10_000]
    return value


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{field} must be a number")
    number = float(value)
    if not math.isfinite(number):
        raise ValidationError(f"{field} must be finite")
    return number


def _track_id(
    value: Any,
    field: str,
    seen: set[str],
    errors: list[str],
) -> str | None:
    try:
        identifier = require_identifier(value, field)
    except ValidationError as exc:
        errors.append(str(exc))
        return None
    if identifier in seen:
        errors.append(f"duplicate check id: {identifier}")
    seen.add(identifier)
    return identifier


def validate_consistency(data: dict[str, Any]) -> dict[str, Any]:
    """Return deterministic discrepancies without changing any values."""
    errors: list[str] = []
    discrepancies: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()
    checked = 0

    try:
        require_exact_keys(data, TOP_LEVEL_FIELDS, "manifest")
        if data.get("schema_version") != "2.0":
            raise ValidationError("schema_version must be 2.0")
        if data.get("manifest_status") != "BLOCKED_INCOMPLETE":
            raise ValidationError("manifest_status must remain BLOCKED_INCOMPLETE")
        require_string(data.get("safety_notice"), "safety_notice", max_length=1000)
        require_string(data.get("authorized_purpose"), "authorized_purpose")
        if not require_bool(data.get("authorization_verified"), "authorization_verified"):
            raise ValidationError("authorization_verified must be true")
        require_string(data.get("provenance_manifest"), "provenance_manifest")
    except ValidationError as exc:
        errors.append(str(exc))
    if data.get("artifact_kind") != "consistency_manifest":
        errors.append("artifact_kind must be consistency_manifest")
    try:
        require_data_class(data.get("data_classification"))
    except ValidationError as exc:
        errors.append(str(exc))

    for index, item in enumerate(_array(data, "dates", errors)):
        try:
            item = require_exact_keys(
                item,
                {"id", "date", "source_fact_id"},
                f"dates[{index}]",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        check_id = _track_id(item.get("id"), f"dates[{index}].id", seen_ids, errors)
        try:
            parse_iso_date(item.get("date"), f"dates[{index}].date")
            require_identifier(
                item.get("source_fact_id"),
                f"dates[{index}].source_fact_id",
            )
            checked += 1
        except ValidationError as exc:
            errors.append(str(exc))
        if check_id is None:
            continue

    for index, item in enumerate(_array(data, "date_ranges", errors)):
        try:
            item = require_exact_keys(
                item,
                {"id", "start", "end", "source_fact_id"},
                f"date_ranges[{index}]",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        check_id = _track_id(
            item.get("id"),
            f"date_ranges[{index}].id",
            seen_ids,
            errors,
        )
        try:
            start = parse_iso_date(item.get("start"), f"date_ranges[{index}].start")
            end = parse_iso_date(item.get("end"), f"date_ranges[{index}].end")
            require_identifier(
                item.get("source_fact_id"),
                f"date_ranges[{index}].source_fact_id",
            )
            checked += 1
            if start > end and check_id:
                discrepancies.append(f"{check_id}: start date is after end date")
        except ValidationError as exc:
            errors.append(str(exc))

    series_units: dict[str, str] = {}
    for index, item in enumerate(_array(data, "quantities", errors)):
        try:
            item = require_exact_keys(
                item,
                {
                    "id",
                    "series_id",
                    "value",
                    "unit",
                    "expected_unit",
                    "source_fact_id",
                },
                f"quantities[{index}]",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        check_id = _track_id(
            item.get("id"),
            f"quantities[{index}].id",
            seen_ids,
            errors,
        )
        try:
            series_id = require_identifier(
                item.get("series_id"),
                f"quantities[{index}].series_id",
            )
            _finite_number(item.get("value"), f"quantities[{index}].value")
            unit = require_string(
                item.get("unit"),
                f"quantities[{index}].unit",
                max_length=80,
            )
            require_identifier(
                item.get("source_fact_id"),
                f"quantities[{index}].source_fact_id",
            )
            checked += 1
            prior = series_units.get(series_id)
            if prior is not None and prior != unit and check_id:
                discrepancies.append(
                    f"{check_id}: unit {unit!r} differs from prior series unit {prior!r}"
                )
            else:
                series_units[series_id] = unit
            expected = item.get("expected_unit")
            if expected is not None:
                expected_unit = require_string(
                    expected,
                    f"quantities[{index}].expected_unit",
                    max_length=80,
                )
                if expected_unit != unit and check_id:
                    discrepancies.append(
                        f"{check_id}: unit does not match expected_unit"
                    )
        except ValidationError as exc:
            errors.append(str(exc))

    for index, item in enumerate(_array(data, "proportions", errors)):
        try:
            item = require_exact_keys(
                item,
                {
                    "id",
                    "numerator",
                    "denominator",
                    "reported_percent",
                    "tolerance_percentage_points",
                    "source_fact_id",
                },
                f"proportions[{index}]",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        check_id = _track_id(
            item.get("id"),
            f"proportions[{index}].id",
            seen_ids,
            errors,
        )
        try:
            numerator = require_nonnegative_int(
                item.get("numerator"),
                f"proportions[{index}].numerator",
            )
            denominator = require_nonnegative_int(
                item.get("denominator"),
                f"proportions[{index}].denominator",
            )
            reported = _finite_number(
                item.get("reported_percent"),
                f"proportions[{index}].reported_percent",
            )
            tolerance = _finite_number(
                item.get("tolerance_percentage_points", 0.05),
                f"proportions[{index}].tolerance_percentage_points",
            )
            require_identifier(
                item.get("source_fact_id"),
                f"proportions[{index}].source_fact_id",
            )
            checked += 1
            if denominator == 0:
                errors.append(f"proportions[{index}].denominator must be greater than zero")
            elif numerator > denominator and check_id:
                discrepancies.append(f"{check_id}: numerator exceeds denominator")
            elif not 0 <= reported <= 100 and check_id:
                discrepancies.append(f"{check_id}: reported_percent is outside 0-100")
            elif tolerance < 0:
                errors.append(
                    f"proportions[{index}].tolerance_percentage_points must be non-negative"
                )
            else:
                calculated = numerator / denominator * 100
                if abs(calculated - reported) > tolerance and check_id:
                    discrepancies.append(
                        f"{check_id}: reported_percent differs from n/N beyond tolerance"
                    )
        except ValidationError as exc:
            errors.append(str(exc))

    for index, item in enumerate(_array(data, "totals", errors)):
        try:
            item = require_exact_keys(
                item,
                {"id", "components", "reported_total", "source_fact_ids"},
                f"totals[{index}]",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        check_id = _track_id(
            item.get("id"),
            f"totals[{index}].id",
            seen_ids,
            errors,
        )
        try:
            components = item.get("components")
            if not isinstance(components, list) or not components:
                raise ValidationError(f"totals[{index}].components must be non-empty")
            parsed_components = [
                require_nonnegative_int(value, f"totals[{index}].components")
                for value in components
            ]
            reported_total = require_nonnegative_int(
                item.get("reported_total"),
                f"totals[{index}].reported_total",
            )
            source_fact_ids = item.get("source_fact_ids")
            if not isinstance(source_fact_ids, list) or not source_fact_ids:
                raise ValidationError(
                    f"totals[{index}].source_fact_ids must be non-empty"
                )
            for fact_id in source_fact_ids:
                require_identifier(fact_id, f"totals[{index}].source_fact_ids")
            checked += 1
            if sum(parsed_components) != reported_total and check_id:
                discrepancies.append(f"{check_id}: components do not equal reported_total")
        except ValidationError as exc:
            errors.append(str(exc))

    if checked == 0:
        errors.append("manifest contains no valid checks")
    if not discrepancies and not errors:
        warnings.append("No discrepancy was found within the declared checks and tolerances.")

    status = (
        "BLOCKED_INVALID_SCHEMA"
        if errors
        else "DISCREPANCIES_REQUIRE_RESOLUTION"
        if discrepancies
        else "CONSISTENT_WITHIN_DECLARED_TOLERANCES_REVIEW_REQUIRED"
    )
    return {
        "tool": TOOL,
        "status": status,
        "checks_completed": checked,
        "errors": errors,
        "discrepancies": discrepancies,
        "warnings": warnings,
        "limitations": [
            "No source was chosen as authoritative and no value was changed.",
            "Arithmetic and format checks do not validate clinical or statistical meaning.",
        ],
        "review_required": True,
        "authorizes_clinical_use_or_submission": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check bounded structured dates, units, n/N percentages, and totals. "
            "Does not infer, convert, reconcile, or alter values."
        )
    )
    parser.add_argument("input_file", help="Local consistency manifest (.json)")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _, data = load_json_object(args.input_file)
        report = validate_consistency(data)
    except (OSError, ValidationError) as exc:
        report = error_report(TOOL, exc)
    try:
        write_json_report(report, args.output, overwrite=args.overwrite)
    except (OSError, ValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return (
        0
        if report["status"]
        == "CONSISTENT_WITHIN_DECLARED_TOLERANCES_REVIEW_REQUIRED"
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/format_adverse_events.py`

```python
#!/usr/bin/env python3
"""Format bounded aggregate adverse-event counts into a review-only Markdown table."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    MAX_CSV_BYTES,
    MAX_CSV_ROWS,
    ValidationError,
    load_json_object,
    local_input_path,
    local_output_path,
    require_bool,
    require_data_class,
    require_exact_keys,
    require_string,
)

TOOL = "format_adverse_events"
REQUIRED_COLUMNS = (
    "analysis_set",
    "treatment_group",
    "meddra_version",
    "system_organ_class",
    "preferred_term",
    "subjects_affected",
    "event_count",
    "denominator",
)
FORBIDDEN_HEADER_FRAGMENTS = {
    "patient",
    "subject_id",
    "participant",
    "case_id",
    "initial",
    "name",
    "email",
    "phone",
    "address",
    "narrative",
    "verbatim",
    "onset",
    "date",
    "mrn",
}
VERSION_RE = re.compile(r"^\d{1,2}\.\d$")
METADATA_FIELDS = {
    "schema_version",
    "artifact_kind",
    "draft_status",
    "safety_notice",
    "data_classification",
    "authorized_purpose",
    "authorization_verified",
    "local_only_handling_confirmed",
    "analysis_metadata",
    "input_csv",
    "required_columns",
    "prohibited_content",
    "provenance_manifest",
    "review",
}
ANALYSIS_METADATA_FIELDS = {
    "protocol_reference",
    "sap_reference",
    "data_cut_reference",
    "analysis_set",
    "counting_rule",
    "threshold_rule",
    "meddra_version",
    "meddra_language",
    "coding_source_reference",
}


@dataclass(frozen=True)
class AggregateRow:
    analysis_set: str
    treatment_group: str
    meddra_version: str
    system_organ_class: str
    preferred_term: str
    subjects_affected: int
    event_count: int
    denominator: int


def validate_aggregate_metadata(
    data: dict[str, object],
    *,
    input_name: str,
) -> dict[str, object]:
    """Require an authorized aggregate-only sidecar manifest."""
    require_exact_keys(data, METADATA_FIELDS, "metadata")
    if data.get("schema_version") != "2.0":
        raise ValidationError("metadata schema_version must be 2.0")
    if data.get("artifact_kind") != "clinical_trial_safety_aggregate_draft":
        raise ValidationError(
            "metadata artifact_kind must be clinical_trial_safety_aggregate_draft"
        )
    if (
        data.get("draft_status")
        != "BLOCKED_INCOMPLETE_NOT_AN_INDIVIDUAL_CASE_SAFETY_REPORT"
    ):
        raise ValidationError("metadata must preserve the blocked non-ICSR status")
    require_string(data.get("safety_notice"), "metadata.safety_notice", max_length=1000)
    if require_data_class(data.get("data_classification")) != "aggregate":
        raise ValidationError("AE formatter accepts aggregate data only")
    require_string(data.get("authorized_purpose"), "metadata.authorized_purpose")
    if not require_bool(
        data.get("authorization_verified"),
        "metadata.authorization_verified",
    ):
        raise ValidationError("metadata.authorization_verified must be true")
    if not require_bool(
        data.get("local_only_handling_confirmed"),
        "metadata.local_only_handling_confirmed",
    ):
        raise ValidationError("metadata.local_only_handling_confirmed must be true")
    require_string(data.get("provenance_manifest"), "metadata.provenance_manifest")
    if data.get("input_csv") != input_name:
        raise ValidationError("metadata.input_csv must equal the aggregate CSV filename")
    if data.get("required_columns") != list(REQUIRED_COLUMNS):
        raise ValidationError("metadata.required_columns does not match the formatter schema")
    prohibited = data.get("prohibited_content")
    if not isinstance(prohibited, list) or not prohibited:
        raise ValidationError("metadata.prohibited_content must be non-empty")

    analysis = require_exact_keys(
        data.get("analysis_metadata"),
        ANALYSIS_METADATA_FIELDS,
        "metadata.analysis_metadata",
    )
    for field in ANALYSIS_METADATA_FIELDS:
        require_string(
            analysis.get(field),
            f"metadata.analysis_metadata.{field}",
            max_length=500,
        )
    if not VERSION_RE.fullmatch(str(analysis["meddra_version"])):
        raise ValidationError("metadata MedDRA version must look like 29.0")

    review = require_exact_keys(
        data.get("review"),
        {
            "safety_coding_review",
            "statistical_review",
            "privacy_review",
            "regulatory_review",
            "submission_authorized",
        },
        "metadata.review",
    )
    if review.get("submission_authorized") is not False:
        raise ValidationError("metadata.review.submission_authorized must remain false")
    return data


def load_aggregate_metadata(
    raw_path: str,
    *,
    input_name: str,
) -> dict[str, object]:
    """Load a bounded aggregate metadata sidecar."""
    _, data = load_json_object(raw_path)
    return validate_aggregate_metadata(data, input_name=input_name)


def _label(value: str | None, field: str) -> str:
    if value is None:
        raise ValidationError(f"{field} is required")
    text = value.strip()
    if (
        not 1 <= len(text) <= 200
        or not text[0].isalnum()
        or any(char in "|`<>\r\n" or ord(char) < 32 for char in text)
    ):
        raise ValidationError(
            f"{field} must be a bounded label without markup or line breaks"
        )
    return text


def _count(value: str | None, field: str) -> int:
    if value is None or not re.fullmatch(r"\d{1,9}", value.strip()):
        raise ValidationError(f"{field} must be a non-negative integer")
    return int(value)


def load_aggregate_csv(raw_path: str) -> list[AggregateRow]:
    """Load and validate aggregate-only AE rows."""
    path = local_input_path(
        raw_path,
        suffixes={".csv"},
        max_bytes=MAX_CSV_BYTES,
    )
    try:
        path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValidationError("CSV input must be UTF-8") from exc
    handle = path.open("r", encoding="utf-8-sig", newline="")

    rows: list[AggregateRow] = []
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValidationError("CSV header is required")
        normalized_headers = [header.strip() for header in reader.fieldnames]
        lowered = {header.lower() for header in normalized_headers}
        for header in lowered:
            if any(fragment in header for fragment in FORBIDDEN_HEADER_FRAGMENTS):
                raise ValidationError(f"row-level or sensitive column is prohibited: {header}")
        if set(normalized_headers) != set(REQUIRED_COLUMNS):
            raise ValidationError(
                f"CSV columns must be exactly: {list(REQUIRED_COLUMNS)}"
            )

        for line_number, raw in enumerate(reader, start=2):
            if len(rows) >= MAX_CSV_ROWS:
                raise ValidationError(f"CSV exceeds {MAX_CSV_ROWS} data rows")
            if None in raw:
                raise ValidationError(f"row {line_number} contains extra columns")
            row = AggregateRow(
                analysis_set=_label(raw.get("analysis_set"), f"row {line_number} analysis_set"),
                treatment_group=_label(
                    raw.get("treatment_group"),
                    f"row {line_number} treatment_group",
                ),
                meddra_version=_label(
                    raw.get("meddra_version"),
                    f"row {line_number} meddra_version",
                ),
                system_organ_class=_label(
                    raw.get("system_organ_class"),
                    f"row {line_number} system_organ_class",
                ),
                preferred_term=_label(
                    raw.get("preferred_term"),
                    f"row {line_number} preferred_term",
                ),
                subjects_affected=_count(
                    raw.get("subjects_affected"),
                    f"row {line_number} subjects_affected",
                ),
                event_count=_count(
                    raw.get("event_count"),
                    f"row {line_number} event_count",
                ),
                denominator=_count(
                    raw.get("denominator"),
                    f"row {line_number} denominator",
                ),
            )
            if not VERSION_RE.fullmatch(row.meddra_version):
                raise ValidationError(
                    f"row {line_number} MedDRA version must look like 29.0"
                )
            if row.denominator == 0:
                raise ValidationError(f"row {line_number} denominator must be greater than zero")
            if row.subjects_affected > row.denominator:
                raise ValidationError(
                    f"row {line_number} subjects_affected exceeds denominator"
                )
            if row.event_count < row.subjects_affected:
                raise ValidationError(
                    f"row {line_number} event_count is less than subjects_affected"
                )
            rows.append(row)

    if not rows:
        raise ValidationError("CSV must contain at least one aggregate data row")

    group_metadata: dict[tuple[str, str], tuple[int, str]] = {}
    row_keys: set[tuple[str, str, str, str]] = set()
    for row in rows:
        group = (row.analysis_set, row.treatment_group)
        metadata = (row.denominator, row.meddra_version)
        if group in group_metadata and group_metadata[group] != metadata:
            raise ValidationError(
                f"inconsistent denominator or MedDRA version for group {group}"
            )
        group_metadata[group] = metadata
        row_key = (
            row.analysis_set,
            row.treatment_group,
            row.system_organ_class,
            row.preferred_term,
        )
        if row_key in row_keys:
            raise ValidationError(f"duplicate aggregate row: {row_key}")
        row_keys.add(row_key)
    return rows


def render_markdown(
    rows: list[AggregateRow],
    *,
    metadata: dict[str, object],
    expected_meddra_version: str | None = None,
) -> str:
    """Render rows without inferring missing cells or statistical comparisons."""
    versions = sorted({row.meddra_version for row in rows})
    if len(versions) != 1:
        raise ValidationError("one table may contain exactly one MedDRA version")
    analysis_metadata = metadata["analysis_metadata"]
    if not isinstance(analysis_metadata, dict):
        raise ValidationError("metadata.analysis_metadata must be an object")
    metadata_version = str(analysis_metadata["meddra_version"])
    if versions != [metadata_version]:
        raise ValidationError(
            "CSV MedDRA version does not match metadata.analysis_metadata.meddra_version"
        )
    if expected_meddra_version is not None:
        if not VERSION_RE.fullmatch(expected_meddra_version):
            raise ValidationError("--expected-meddra-version must look like 29.0")
        if versions != [expected_meddra_version]:
            raise ValidationError(
                f"input MedDRA versions {versions} do not match expected "
                f"{expected_meddra_version}"
            )

    analysis_sets = sorted({row.analysis_set for row in rows})
    if len(analysis_sets) != 1:
        raise ValidationError(
            "one output table may contain exactly one analysis_set"
        )
    if analysis_sets[0] != analysis_metadata["analysis_set"]:
        raise ValidationError(
            "CSV analysis_set does not match metadata.analysis_metadata.analysis_set"
        )
    groups = sorted({row.treatment_group for row in rows})
    denominators = {
        group: next(row.denominator for row in rows if row.treatment_group == group)
        for group in groups
    }
    lookup = {
        (row.system_organ_class, row.preferred_term, row.treatment_group): row
        for row in rows
    }
    terms = sorted({(row.system_organ_class, row.preferred_term) for row in rows})

    headers = ["System organ class", "Preferred term"]
    for group in groups:
        headers.extend(
            [
                f"{group}: subjects n/N (%)",
                f"{group}: events",
            ]
        )
    lines = [
        "# Draft aggregate adverse-event table",
        "",
        "> DRAFT — aggregate display only. Not an ICSR, reportability decision, "
        "clinical interpretation, filing, or submission. Qualified safety and "
        "statistical review is required.",
        "",
        f"- Analysis set: {analysis_sets[0]}",
        f"- MedDRA version(s), as supplied and not terminology-validated: {', '.join(versions)}",
        f"- MedDRA language, as supplied: {analysis_metadata['meddra_language']}",
        f"- Counting rule, as supplied: {analysis_metadata['counting_rule']}",
        f"- Threshold rule, as supplied: {analysis_metadata['threshold_rule']}",
        "- Missing group/term cells are shown as an em dash and are not assumed to be zero.",
        "- Subjects and events are distinct; event counts may exceed subject counts.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for soc, term in terms:
        cells = [soc, term]
        for group in groups:
            row = lookup.get((soc, term, group))
            if row is None:
                cells.extend(["—", "—"])
                continue
            percent = row.subjects_affected / row.denominator * 100
            cells.extend(
                [
                    f"{row.subjects_affected}/{row.denominator} ({percent:.1f}%)",
                    str(row.event_count),
                ]
            )
        lines.append("| " + " | ".join(cells) + " |")
    lines.extend(
        [
            "",
            "Denominators by treatment group: "
            + "; ".join(f"{group} N={denominators[group]}" for group in groups)
            + ".",
            "",
            "No MedDRA semantic validation, deduplication, inference, causal assessment, "
            "or between-group testing was performed.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Format aggregate-only AE CSV rows as review-only Markdown. "
            "Rejects row-level identifiers and performs no safety assessment."
        )
    )
    parser.add_argument("input_file", help="Local aggregate CSV")
    parser.add_argument(
        "--metadata",
        required=True,
        help="Authorized aggregate safety metadata sidecar (.json)",
    )
    parser.add_argument("-o", "--output", help="Optional local Markdown output")
    parser.add_argument("--expected-meddra-version")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rows = load_aggregate_csv(args.input_file)
        input_name = Path(args.input_file).name
        metadata = load_aggregate_metadata(
            args.metadata,
            input_name=input_name,
        )
        rendered = render_markdown(
            rows,
            metadata=metadata,
            expected_meddra_version=args.expected_meddra_version,
        )
        if args.output:
            output = local_output_path(
                args.output,
                suffixes={".md"},
                overwrite=args.overwrite,
            )
            output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (OSError, ValidationError, csv.Error) as exc:
        print(f"{TOOL}: BLOCKED_INVALID_INPUT: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/generate_report_template.py`

```python
#!/usr/bin/env python3
"""Copy a fail-closed structured clinical-report template to a local path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    ValidationError,
    load_json_object,
    local_input_path,
    local_output_path,
)

TOOL = "generate_report_template"
TEMPLATES = {
    "case-report": "case_report_template.json",
    "radiology-scaffold": "radiology_report_template.json",
    "pathology-scaffold": "pathology_report_template.json",
    "lab-scaffold": "lab_report_template.json",
    "csr": "clinical_trial_csr_template.json",
    "trial-results": "clinical_trial_results_template.json",
    "trial-protocol-checklist": "trial_protocol_reporting_checklist.json",
    "safety-aggregate": "clinical_trial_safety_aggregate_template.json",
    "adverse-event-csv": "adverse_event_aggregate_input_template.csv",
    "research-summary": "research_summary_template.json",
    "deidentification-checklist": "deidentification_process_checklist.json",
    "quality-review": "quality_review_checklist.json",
    "provenance": "provenance_manifest_template.json",
    "terminology": "terminology_manifest_template.json",
    "consistency": "consistency_manifest_template.json",
}


def template_directory() -> Path:
    """Return the fixed bundled asset directory."""
    return Path(__file__).resolve().parent.parent / "assets"


def list_templates() -> str:
    """Return a stable machine-readable-friendly list."""
    lines = ["Available fail-closed templates:"]
    lines.extend(f"- {name}: {TEMPLATES[name]}" for name in sorted(TEMPLATES))
    return "\n".join(lines) + "\n"


def generate_template(
    template_type: str,
    raw_output: str,
    *,
    overwrite: bool = False,
) -> Path:
    """Copy one fixed asset without interpolation or clinical content."""
    if template_type not in TEMPLATES:
        raise ValidationError(f"unknown template type: {template_type}")
    source = template_directory() / TEMPLATES[template_type]
    suffix = source.suffix.lower()
    validated_source = local_input_path(
        str(source),
        suffixes={suffix},
        max_bytes=1_000_000,
    )
    if suffix == ".json":
        load_json_object(str(validated_source))
    output = local_output_path(
        raw_output,
        suffixes={suffix},
        overwrite=overwrite,
    )
    output.write_bytes(validated_source.read_bytes())
    return output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Copy a bundled fail-closed JSON/CSV template. No interpolation, "
            "network access, clinical inference, signing, filing, or submission."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true", help="List template types")
    mode.add_argument("--type", choices=sorted(TEMPLATES), help="Template type")
    parser.add_argument("-o", "--output", help="Required local output when --type is used")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list:
        if args.output:
            print("--output is not used with --list", file=sys.stderr)
            return 2
        print(list_templates(), end="")
        return 0
    if not args.output:
        print("--output is required with --type", file=sys.stderr)
        return 2
    try:
        output = generate_template(args.type, args.output, overwrite=args.overwrite)
        print(f"Created blocked draft template: {output}")
        print("Qualified review is required; this output is not for clinical use or submission.")
        return 0
    except (OSError, ValidationError) as exc:
        print(f"{TOOL}: BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/provenance_validator.py`

```python
#!/usr/bin/env python3
"""Validate source-fact-to-claim traceability without opening source records."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    SHA256_RE,
    ValidationError,
    error_report,
    load_json_object,
    parse_iso_date,
    require_bool,
    require_data_class,
    require_exact_keys,
    require_identifier,
    require_string,
    write_json_report,
)

TOOL = "provenance_validator"
LOCAL_LOCATOR_RE = re.compile(r"^local:[A-Za-z0-9_./:-]{1,280}$")
SOURCE_KINDS = {
    "synthetic_record",
    "deidentified_record",
    "aggregate_output",
    "protocol",
    "statistical_analysis_plan",
    "published_source",
    "authorized_system_record",
}
FACT_FIELDS = {
    "fact_id",
    "source_record_kind",
    "record_locator",
    "field_path",
    "value_hash_sha256",
    "verification_status",
    "verified_by_role",
    "verified_at",
    "source_version",
}
CLAIM_FIELDS = {
    "claim_id",
    "artifact_field_path",
    "fact_ids",
    "support_status",
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "artifact_kind",
    "manifest_status",
    "safety_notice",
    "data_classification",
    "authorized_purpose",
    "authorization_verified",
    "facts",
    "claims",
    "review",
}


def validate_provenance(data: dict[str, Any]) -> dict[str, Any]:
    """Validate bounded metadata links while preserving source separation."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        require_exact_keys(data, TOP_LEVEL_FIELDS, "manifest")
        if data.get("schema_version") != "2.0":
            raise ValidationError("schema_version must be 2.0")
        if data.get("manifest_status") != "BLOCKED_INCOMPLETE":
            raise ValidationError("manifest_status must remain BLOCKED_INCOMPLETE")
        require_string(data.get("safety_notice"), "safety_notice", max_length=1000)
    except ValidationError as exc:
        errors.append(str(exc))
    if data.get("artifact_kind") != "provenance_manifest":
        errors.append("artifact_kind must be provenance_manifest")
    try:
        require_data_class(data.get("data_classification"))
        require_string(data.get("authorized_purpose"), "authorized_purpose")
        if not require_bool(data.get("authorization_verified"), "authorization_verified"):
            errors.append("authorization_verified must be true")
    except ValidationError as exc:
        errors.append(str(exc))

    facts = data.get("facts")
    claims = data.get("claims")
    if not isinstance(facts, list) or not facts:
        errors.append("facts must be a non-empty array")
        facts = []
    if not isinstance(claims, list) or not claims:
        errors.append("claims must be a non-empty array")
        claims = []
    if len(facts) > 10_000:
        errors.append("facts may contain at most 10,000 items")
    if len(claims) > 10_000:
        errors.append("claims may contain at most 10,000 items")

    fact_ids: set[str] = set()
    for index, fact in enumerate(facts[:10_000]):
        try:
            fact = require_exact_keys(fact, FACT_FIELDS, f"facts[{index}]")
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        try:
            fact_id = require_identifier(fact.get("fact_id"), f"facts[{index}].fact_id")
            if fact_id in fact_ids:
                errors.append(f"duplicate fact_id: {fact_id}")
            fact_ids.add(fact_id)
            if fact.get("source_record_kind") not in SOURCE_KINDS:
                errors.append(f"facts[{index}].source_record_kind is invalid")
            locator = require_string(
                fact.get("record_locator"),
                f"facts[{index}].record_locator",
                max_length=286,
            )
            if not LOCAL_LOCATOR_RE.fullmatch(locator):
                errors.append(
                    f"facts[{index}].record_locator must be a local: locator"
                )
            require_string(
                fact.get("field_path"),
                f"facts[{index}].field_path",
                max_length=300,
            )
            value_hash = require_string(
                fact.get("value_hash_sha256"),
                f"facts[{index}].value_hash_sha256",
                max_length=64,
            )
            if not SHA256_RE.fullmatch(value_hash):
                errors.append(f"facts[{index}].value_hash_sha256 is invalid")
            if fact.get("verification_status") != "verified":
                errors.append(f"facts[{index}] is not verified")
            require_string(
                fact.get("verified_by_role"),
                f"facts[{index}].verified_by_role",
                max_length=100,
            )
            parse_iso_date(fact.get("verified_at"), f"facts[{index}].verified_at")
            require_string(
                fact.get("source_version"),
                f"facts[{index}].source_version",
                max_length=100,
            )
        except ValidationError as exc:
            errors.append(str(exc))

    claim_ids: set[str] = set()
    referenced_facts: set[str] = set()
    for index, claim in enumerate(claims[:10_000]):
        try:
            claim = require_exact_keys(claim, CLAIM_FIELDS, f"claims[{index}]")
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        try:
            claim_id = require_identifier(
                claim.get("claim_id"),
                f"claims[{index}].claim_id",
            )
            if claim_id in claim_ids:
                errors.append(f"duplicate claim_id: {claim_id}")
            claim_ids.add(claim_id)
            require_string(
                claim.get("artifact_field_path"),
                f"claims[{index}].artifact_field_path",
                max_length=300,
            )
            links = claim.get("fact_ids")
            if not isinstance(links, list) or not links:
                errors.append(f"claims[{index}].fact_ids must be a non-empty array")
                links = []
            for linked in links:
                linked_id = require_identifier(linked, f"claims[{index}].fact_ids")
                referenced_facts.add(linked_id)
                if linked_id not in fact_ids:
                    errors.append(
                        f"claims[{index}] references unknown fact_id {linked_id}"
                    )
            if claim.get("support_status") != "supported_by_verified_facts":
                errors.append(f"claims[{index}] is not marked supported_by_verified_facts")
        except ValidationError as exc:
            errors.append(str(exc))

    unused = sorted(fact_ids - referenced_facts)
    if unused:
        warnings.append(f"{len(unused)} verified facts are not linked to a claim")

    review = data.get("review")
    try:
        review = require_exact_keys(
            review,
            {
                "source_owner_review",
                "quality_review",
                "privacy_review",
                "release_authorized",
            },
            "review",
        )
        for field in ("source_owner_review", "quality_review", "privacy_review"):
            if review.get(field) != "completed":
                warnings.append(f"review.{field} remains required")
        if review.get("release_authorized") is not False:
            errors.append("review.release_authorized must remain false")
    except ValidationError as exc:
        errors.append(str(exc))

    return {
        "tool": TOOL,
        "status": "BLOCKED" if errors else "TRACEABILITY_COMPLETE_REVIEW_REQUIRED",
        "fact_count": len(facts),
        "claim_count": len(claims),
        "linked_fact_count": len(referenced_facts),
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "Source records were not opened and hash values were not recomputed.",
            "Traceability metadata does not establish source truth or clinical correctness.",
        ],
        "review_required": True,
        "authorizes_clinical_use_or_submission": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check bounded local source-fact traceability metadata. "
            "Does not open source records or copy clinical content."
        )
    )
    parser.add_argument("input_file", help="Local provenance manifest (.json)")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _, data = load_json_object(args.input_file)
        report = validate_provenance(data)
    except (OSError, ValidationError) as exc:
        report = error_report(TOOL, exc)
    try:
        write_json_report(report, args.output, overwrite=args.overwrite)
    except (OSError, ValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0 if report["status"] == "TRACEABILITY_COMPLETE_REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/terminology_validator.py`

```python
#!/usr/bin/env python3
"""Check terminology-manifest schema and optional caller-supplied local dictionary."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    ValidationError,
    error_report,
    load_json_object,
    parse_iso_date,
    require_bool,
    require_data_class,
    require_exact_keys,
    require_identifier,
    require_string,
    write_json_report,
)

TOOL = "terminology_validator"
CODE_PATTERNS = {
    "MedDRA": re.compile(r"^\d{8}$"),
    "LOINC": re.compile(r"^\d{1,7}-\d$"),
    "SNOMED_CT": re.compile(r"^[1-9]\d{5,17}$"),
    "ICD_10_CM": re.compile(r"^[A-Z][0-9A-Z]{2}(?:\.[0-9A-Z]{1,4})?$"),
    "UCUM": re.compile(r"^[A-Za-z0-9%.\[\]{}()/*^+'_-]{1,80}$"),
}
CODING_STATUSES = {"verified_by_qualified_reviewer", "unverified"}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "artifact_kind",
    "manifest_status",
    "safety_notice",
    "data_classification",
    "authorized_purpose",
    "authorization_verified",
    "provenance_manifest",
    "entries",
}
ENTRY_FIELDS = {
    "system",
    "system_uri",
    "code",
    "display",
    "version",
    "language",
    "source_fact_id",
    "coding_status",
    "verified_by_role",
    "verified_at",
}


def _validate_entry(entry: Any, index: int) -> tuple[str, str, str, str, list[str]]:
    entry = require_exact_keys(entry, ENTRY_FIELDS, f"entries[{index}]")
    system = require_string(entry.get("system"), f"entries[{index}].system", max_length=32)
    if system not in CODE_PATTERNS:
        raise ValidationError(
            f"entries[{index}].system must be one of {sorted(CODE_PATTERNS)}"
        )
    require_string(
        entry.get("system_uri"),
        f"entries[{index}].system_uri",
        max_length=200,
    )
    code = require_string(entry.get("code"), f"entries[{index}].code", max_length=80)
    if not CODE_PATTERNS[system].fullmatch(code):
        raise ValidationError(f"entries[{index}].code fails {system} syntax")
    display = require_string(
        entry.get("display"),
        f"entries[{index}].display",
        max_length=500,
    )
    version = require_string(
        entry.get("version"),
        f"entries[{index}].version",
        max_length=80,
    )
    require_string(entry.get("language"), f"entries[{index}].language", max_length=32)
    require_identifier(
        entry.get("source_fact_id"),
        f"entries[{index}].source_fact_id",
    )
    status = entry.get("coding_status")
    if status not in CODING_STATUSES:
        raise ValidationError(f"entries[{index}].coding_status is invalid")
    warnings: list[str] = []
    if status == "verified_by_qualified_reviewer":
        require_string(
            entry.get("verified_by_role"),
            f"entries[{index}].verified_by_role",
            max_length=100,
        )
        parse_iso_date(entry.get("verified_at"), f"entries[{index}].verified_at")
    else:
        warnings.append(f"entries[{index}] remains unverified")
    if system == "MedDRA" and not re.fullmatch(r"\d{1,2}\.\d", version):
        warnings.append(f"entries[{index}] MedDRA version has an unusual format")
    return system, version, code, display, warnings


def _load_dictionary(raw_path: str) -> dict[tuple[str, str, str], str]:
    _, data = load_json_object(raw_path)
    require_exact_keys(
        data,
        {"schema_version", "artifact_kind", "entries"},
        "dictionary",
    )
    if data.get("schema_version") != "2.0":
        raise ValidationError("dictionary schema_version must be 2.0")
    if data.get("artifact_kind") != "terminology_dictionary":
        raise ValidationError("dictionary artifact_kind must be terminology_dictionary")
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValidationError("dictionary entries must be a non-empty array")
    if len(entries) > 20_000:
        raise ValidationError("dictionary may contain at most 20,000 entries")
    dictionary: dict[tuple[str, str, str], str] = {}
    for index, entry in enumerate(entries):
        entry = require_exact_keys(
            entry,
            {"system", "version", "code", "display"},
            f"dictionary entries[{index}]",
        )
        system = require_string(
            entry.get("system"),
            f"dictionary entries[{index}].system",
            max_length=32,
        )
        version = require_string(
            entry.get("version"),
            f"dictionary entries[{index}].version",
            max_length=80,
        )
        code = require_string(
            entry.get("code"),
            f"dictionary entries[{index}].code",
            max_length=80,
        )
        display = require_string(
            entry.get("display"),
            f"dictionary entries[{index}].display",
            max_length=500,
        )
        key = (system, version, code)
        if key in dictionary and dictionary[key] != display:
            raise ValidationError(f"dictionary contains conflicting duplicate at index {index}")
        dictionary[key] = display
    return dictionary


def validate_terminology_manifest(
    data: dict[str, Any],
    dictionary: dict[tuple[str, str, str], str] | None = None,
) -> dict[str, Any]:
    """Validate schema and optional exact tuple matches."""
    errors: list[str] = []
    warnings: list[str] = []
    try:
        require_exact_keys(data, TOP_LEVEL_FIELDS, "manifest")
        if data.get("schema_version") != "2.0":
            raise ValidationError("schema_version must be 2.0")
        if data.get("manifest_status") != "BLOCKED_INCOMPLETE":
            raise ValidationError("manifest_status must remain BLOCKED_INCOMPLETE")
        require_string(data.get("safety_notice"), "safety_notice", max_length=1000)
        require_string(data.get("authorized_purpose"), "authorized_purpose")
        if not require_bool(data.get("authorization_verified"), "authorization_verified"):
            raise ValidationError("authorization_verified must be true")
        require_string(data.get("provenance_manifest"), "provenance_manifest")
    except ValidationError as exc:
        errors.append(str(exc))
    if data.get("artifact_kind") != "terminology_manifest":
        errors.append("artifact_kind must be terminology_manifest")
    try:
        require_data_class(data.get("data_classification"))
    except ValidationError as exc:
        errors.append(str(exc))

    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("entries must be a non-empty array")
        entries = []
    if len(entries) > 5_000:
        errors.append("entries may contain at most 5,000 items")

    seen: set[tuple[str, str, str]] = set()
    verified_count = 0
    dictionary_match_count = 0
    for index, entry in enumerate(entries[:5_000]):
        try:
            system, version, code, display, entry_warnings = _validate_entry(
                entry,
                index,
            )
            warnings.extend(entry_warnings)
            key = (system, version, code)
            if key in seen:
                errors.append(f"entries[{index}] duplicates a prior system/version/code")
            seen.add(key)
            if entry.get("coding_status") == "verified_by_qualified_reviewer":
                verified_count += 1
            if dictionary is not None:
                expected_display = dictionary.get(key)
                if expected_display is None:
                    errors.append(f"entries[{index}] is absent from the supplied dictionary")
                elif expected_display != display:
                    errors.append(
                        f"entries[{index}] display does not match the supplied dictionary"
                    )
                else:
                    dictionary_match_count += 1
        except ValidationError as exc:
            errors.append(str(exc))

    if dictionary is None:
        warnings.append(
            "No local dictionary supplied; code existence, currency, and display were not checked."
        )
        success_status = "SCHEMA_VALID_SYNTAX_ONLY_REVIEW_REQUIRED"
    else:
        success_status = "SCHEMA_AND_LOCAL_DICTIONARY_MATCH_REVIEW_REQUIRED"

    return {
        "tool": TOOL,
        "status": "BLOCKED" if errors else success_status,
        "entry_count": len(entries),
        "qualified_reviewer_verified_count": verified_count,
        "local_dictionary_match_count": dictionary_match_count,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "Syntax or local-dictionary matching does not establish clinical correctness.",
            "Caller is responsible for dictionary authority, version, license, and completeness.",
        ],
        "review_required": True,
        "authorizes_clinical_use_or_submission": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check a bounded terminology JSON manifest. Optional dictionary comparison "
            "uses a caller-supplied local JSON file and never calls a network service."
        )
    )
    parser.add_argument("input_file", help="Local terminology manifest (.json)")
    parser.add_argument("--dictionary", help="Optional authorized local dictionary (.json)")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _, data = load_json_object(args.input_file)
        dictionary = _load_dictionary(args.dictionary) if args.dictionary else None
        report = validate_terminology_manifest(data, dictionary)
    except (OSError, ValidationError) as exc:
        report = error_report(TOOL, exc)
    try:
        write_json_report(report, args.output, overwrite=args.overwrite)
    except (OSError, ValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0 if report["status"].startswith("SCHEMA_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_case_report.py`

```python
#!/usr/bin/env python3
"""Validate a structured CARE coverage manifest without reading patient narrative."""

from __future__ import annotations

import argparse
import sys
from typing import Any

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    ValidationError,
    error_report,
    load_json_object,
    require_bool,
    require_data_class,
    require_exact_keys,
    require_identifier,
    require_string,
    write_json_report,
)

TOOL = "validate_case_report"
CARE_ITEMS = (
    "title",
    "key_words",
    "abstract",
    "introduction",
    "patient_information",
    "clinical_findings",
    "timeline",
    "diagnostic_assessment",
    "therapeutic_intervention",
    "follow_up_and_outcomes",
    "discussion",
    "patient_perspective",
    "informed_consent",
)
ALLOWED_ITEM_STATUSES = {
    "verified_present",
    "not_applicable_with_rationale",
    "missing",
    "conflict",
}
NA_ALLOWED = {"patient_perspective"}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "artifact_kind",
    "draft_status",
    "safety_notice",
    "data_classification",
    "authorized_purpose",
    "authorization_verified",
    "provenance_manifest",
    "guidance",
    "care_items",
    "privacy",
    "review",
}
EXPECTED_DRAFT_STATUS = (
    "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_CLINICAL_USE_OR_SUBMISSION"
)


def _fact_ids(item: dict[str, Any], field: str) -> list[str]:
    value = item.get("source_fact_ids")
    if not isinstance(value, list):
        raise ValidationError(f"{field}.source_fact_ids must be an array")
    return [require_identifier(fact_id, f"{field}.source_fact_ids") for fact_id in value]


def validate_case_manifest(data: dict[str, Any]) -> dict[str, Any]:
    """Return fail-closed structural findings for a CARE manifest."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        require_exact_keys(data, TOP_LEVEL_FIELDS, "manifest")
        if data.get("schema_version") != "2.0":
            raise ValidationError("schema_version must be 2.0")
        if data.get("artifact_kind") != "case_report_draft":
            raise ValidationError("artifact_kind must be case_report_draft")
        if data.get("draft_status") != EXPECTED_DRAFT_STATUS:
            raise ValidationError(
                "draft_status must preserve the blocked non-clinical-use warning"
            )
        require_string(data.get("safety_notice"), "safety_notice", max_length=1000)
        require_data_class(data.get("data_classification"))
        if not require_bool(data.get("authorization_verified"), "authorization_verified"):
            errors.append("authorization_verified must be true")
        require_string(data.get("authorized_purpose"), "authorized_purpose")
        require_string(data.get("provenance_manifest"), "provenance_manifest")
    except ValidationError as exc:
        errors.append(str(exc))

    guidance = data.get("guidance")
    try:
        guidance = require_exact_keys(
            guidance,
            {
                "name",
                "checklist_version",
                "explanation_version",
                "target_journal_instructions_checked",
            },
            "guidance",
        )
        if guidance.get("name") != "CARE":
            errors.append("guidance.name must be CARE")
        if guidance.get("checklist_version") != "2013":
            errors.append("guidance.checklist_version must be 2013")
        if guidance.get("explanation_version") != "2017":
            errors.append("guidance.explanation_version must be 2017")
        if guidance.get("target_journal_instructions_checked") is not True:
            warnings.append("target journal instructions remain to be checked")
    except ValidationError as exc:
        errors.append(str(exc))

    items = data.get("care_items")
    if not isinstance(items, dict):
        errors.append("care_items must be an object")
        items = {}
    missing_keys = sorted(set(CARE_ITEMS) - set(items))
    extra_keys = sorted(set(items) - set(CARE_ITEMS))
    if missing_keys:
        errors.append(f"missing CARE item keys: {missing_keys}")
    if extra_keys:
        errors.append(f"unexpected CARE item keys: {extra_keys}")

    coverage: dict[str, str] = {}
    for key in CARE_ITEMS:
        item = items.get(key)
        if not isinstance(item, dict):
            errors.append(f"care_items.{key} must be an object")
            continue
        try:
            item = require_exact_keys(
                item,
                {"status", "source_fact_ids", "rationale"},
                f"care_items.{key}",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        status = item.get("status")
        coverage[key] = str(status)
        if status not in ALLOWED_ITEM_STATUSES:
            errors.append(f"care_items.{key}.status is invalid")
            continue
        try:
            facts = _fact_ids(item, f"care_items.{key}")
        except ValidationError as exc:
            errors.append(str(exc))
            facts = []
        if status == "verified_present" and not facts:
            errors.append(f"care_items.{key} requires at least one verified source fact")
        elif status == "not_applicable_with_rationale":
            if key not in NA_ALLOWED:
                errors.append(f"care_items.{key} cannot be marked not applicable")
            try:
                require_string(
                    item.get("rationale"),
                    f"care_items.{key}.rationale",
                    max_length=500,
                )
            except ValidationError as exc:
                errors.append(str(exc))
        elif status in {"missing", "conflict"}:
            errors.append(f"care_items.{key} is {status}")

    privacy = data.get("privacy")
    try:
        privacy = require_exact_keys(
            privacy,
            {
                "deidentification_process_record",
                "publication_consent_record",
                "image_or_media_included",
                "reidentification_risk_reviewed",
            },
            "privacy",
        )
        for field in ("deidentification_process_record", "publication_consent_record"):
            try:
                require_string(privacy.get(field), f"privacy.{field}")
            except ValidationError as exc:
                errors.append(str(exc))
        try:
            if not require_bool(
                privacy.get("reidentification_risk_reviewed"),
                "privacy.reidentification_risk_reviewed",
            ):
                errors.append("privacy.reidentification_risk_reviewed must be true")
        except ValidationError as exc:
            errors.append(str(exc))
        try:
            require_bool(privacy.get("image_or_media_included"), "privacy.image_or_media_included")
        except ValidationError as exc:
            errors.append(str(exc))
    except ValidationError as exc:
        errors.append(str(exc))

    review = data.get("review")
    try:
        review = require_exact_keys(
            review,
            {
                "qualified_clinical_review",
                "privacy_legal_review",
                "accountable_author_review",
                "submission_authorized",
            },
            "review",
        )
        for field in (
            "qualified_clinical_review",
            "privacy_legal_review",
            "accountable_author_review",
        ):
            if review.get(field) != "completed":
                warnings.append(f"review.{field} remains required")
        if review.get("submission_authorized") is not False:
            errors.append("submission_authorized must remain false in this draft manifest")
    except ValidationError as exc:
        errors.append(str(exc))

    status = "BLOCKED" if errors else "STRUCTURE_COMPLETE_REVIEW_REQUIRED"
    return {
        "tool": TOOL,
        "status": status,
        "guidance": "CARE 2013 with 2017 explanation",
        "coverage": coverage,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "Structure and provenance metadata only; no clinical-content validation.",
            "Does not establish consent, de-identification, CARE adherence, or journal readiness.",
        ],
        "review_required": True,
        "authorizes_clinical_use_or_submission": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check a bounded JSON CARE coverage manifest. "
            "Does not read patient narrative or claim compliance."
        )
    )
    parser.add_argument("input_file", help="Local case-report manifest (.json)")
    parser.add_argument("-o", "--output", help="Optional local JSON report path")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing an existing output file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _, data = load_json_object(args.input_file)
        report = validate_case_manifest(data)
    except (OSError, ValidationError) as exc:
        report = error_report(TOOL, exc)
    try:
        write_json_report(report, args.output, overwrite=args.overwrite)
    except (OSError, ValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0 if report["status"] == "STRUCTURE_COMPLETE_REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_trial_report.py`

```python
#!/usr/bin/env python3
"""Validate structured ICH E3, CONSORT 2025, or SPIRIT 2025 coverage."""

from __future__ import annotations

import argparse
import sys
from typing import Any

sys.dont_write_bytecode = True

from _common import (  # noqa: E402
    ValidationError,
    error_report,
    load_json_object,
    require_bool,
    require_data_class,
    require_exact_keys,
    require_identifier,
    require_string,
    write_json_report,
)

TOOL = "validate_trial_report"
ALLOWED_STATUSES = {
    "verified_present",
    "not_applicable_with_rationale",
    "missing",
    "conflict",
}
E3_SECTIONS = (
    "title_page",
    "synopsis",
    "table_of_contents",
    "abbreviations_and_definitions",
    "ethics",
    "investigators_and_administration",
    "introduction",
    "study_objectives",
    "investigational_plan",
    "study_patients",
    "efficacy_evaluation",
    "safety_evaluation",
    "discussion_and_conclusions",
    "tables_figures_graphs_not_in_text",
    "reference_list",
    "appendices",
)
COMMON_TOP_FIELDS = {
    "schema_version",
    "artifact_kind",
    "draft_status",
    "safety_notice",
    "data_classification",
    "authorized_purpose",
    "authorization_verified",
    "guidance",
    "provenance_manifest",
    "review",
}
ROUTES = {
    "clinical_study_report_draft": {
        "container": "sections",
        "keys": E3_SECTIONS,
        "guidance": "ICH E3 Step 4 1995-11-30 with Q&A R1 2012-07-06",
        "review_fields": (
            "medical_review",
            "statistical_review",
            "safety_review",
            "privacy_legal_review",
            "quality_review",
            "regulatory_review",
        ),
        "authorization_field": "submission_authorized",
        "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_FILING_OR_SUBMISSION",
        "top_fields": COMMON_TOP_FIELDS | {"study_metadata", "sections"},
        "metadata_name": "study_metadata",
        "item_fields": {"status", "source_fact_ids", "rationale"},
    },
    "randomized_trial_results_draft": {
        "container": "checklist_items",
        "keys": tuple(f"C{number:02d}" for number in range(1, 31)),
        "guidance": "CONSORT 2025",
        "review_fields": (
            "accountable_author_review",
            "methodologist_review",
            "statistical_review",
            "safety_review",
        ),
        "authorization_field": "publication_authorized",
        "draft_status": (
            "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_PUBLICATION_OR_SUBMISSION"
        ),
        "top_fields": COMMON_TOP_FIELDS
        | {
            "study_metadata",
            "checklist_items",
            "not_applicable_rationales",
            "participant_flow_source_fact_ids",
        },
        "metadata_name": "study_metadata",
        "item_fields": {"status", "source_fact_ids", "official_item_locator"},
    },
    "randomized_trial_protocol_reporting_manifest": {
        "container": "checklist_items",
        "keys": tuple(f"S{number:02d}" for number in range(1, 35)),
        "guidance": "SPIRIT 2025",
        "review_fields": (
            "investigator_sponsor_review",
            "methodologist_review",
            "statistical_review",
            "safety_review",
            "ethics_regulatory_review",
        ),
        "authorization_field": "protocol_approved",
        "draft_status": (
            "BLOCKED_INCOMPLETE_REPORTING_CHECKLIST_NOT_A_PROTOCOL_OR_ETHICS_APPROVAL"
        ),
        "top_fields": COMMON_TOP_FIELDS
        | {
            "protocol_metadata",
            "checklist_items",
            "not_applicable_rationales",
            "participant_timeline_source_fact_ids",
        },
        "metadata_name": "protocol_metadata",
        "item_fields": {"status", "source_fact_ids", "official_item_locator"},
    },
}


def _validate_guidance(
    artifact_kind: str,
    guidance: Any,
    errors: list[str],
) -> None:
    if not isinstance(guidance, dict):
        errors.append("guidance must be an object")
        return
    if artifact_kind == "clinical_study_report_draft":
        try:
            guidance = require_exact_keys(
                guidance,
                {
                    "base",
                    "base_version",
                    "qa_version",
                    "gcp_version_considered",
                    "regional_adoption_verified",
                },
                "guidance",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            return
        if guidance.get("base") != "ICH E3":
            errors.append("CSR guidance.base must be ICH E3")
        if guidance.get("base_version") != "Step 4 1995-11-30":
            errors.append("CSR base_version is not the supported ICH E3 version")
        if guidance.get("qa_version") != "R1 2012-07-06":
            errors.append("CSR qa_version is not the supported E3 Q&A version")
        if (
            guidance.get("gcp_version_considered")
            != "ICH E6(R3) consolidated 2026-06-16"
        ):
            errors.append("CSR must record consideration of current ICH E6(R3)")
        if guidance.get("regional_adoption_verified") is not True:
            errors.append("CSR regional adoption/version review is required")
    elif artifact_kind == "randomized_trial_results_draft":
        try:
            guidance = require_exact_keys(
                guidance,
                {
                    "base",
                    "item_count",
                    "statement_and_explanation_checked",
                    "applicable_extensions",
                    "applicable_extensions_reviewed",
                    "extension_conflicts_resolved_by_methodologist",
                },
                "guidance",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            return
        if guidance.get("base") != "CONSORT 2025" or guidance.get("item_count") != 30:
            errors.append("results manifest must declare CONSORT 2025 with 30 items")
        if guidance.get("statement_and_explanation_checked") is not True:
            errors.append("CONSORT statement and explanation must be checked")
        if guidance.get("applicable_extensions_reviewed") is not True:
            errors.append("applicable CONSORT extensions must be reviewed")
        extensions = guidance.get("applicable_extensions")
        if not isinstance(extensions, list):
            errors.append("guidance.applicable_extensions must be an array")
        else:
            for index, extension in enumerate(extensions):
                try:
                    require_string(
                        extension,
                        f"guidance.applicable_extensions[{index}]",
                        max_length=200,
                    )
                except ValidationError as exc:
                    errors.append(str(exc))
        try:
            conflicts_resolved = require_bool(
                guidance.get("extension_conflicts_resolved_by_methodologist"),
                "guidance.extension_conflicts_resolved_by_methodologist",
            )
            if extensions and not conflicts_resolved:
                errors.append("extension conflicts require methodologist resolution")
        except ValidationError as exc:
            errors.append(str(exc))
    elif artifact_kind == "randomized_trial_protocol_reporting_manifest":
        try:
            guidance = require_exact_keys(
                guidance,
                {
                    "base",
                    "item_count",
                    "statement_and_explanation_checked",
                    "applicable_extensions",
                    "applicable_extensions_reviewed",
                    "extension_conflicts_resolved_by_methodologist",
                },
                "guidance",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            return
        if guidance.get("base") != "SPIRIT 2025" or guidance.get("item_count") != 34:
            errors.append("protocol manifest must declare SPIRIT 2025 with 34 items")
        if guidance.get("statement_and_explanation_checked") is not True:
            errors.append("SPIRIT statement and explanation must be checked")
        if guidance.get("applicable_extensions_reviewed") is not True:
            errors.append("applicable SPIRIT extensions must be reviewed")
        extensions = guidance.get("applicable_extensions")
        if not isinstance(extensions, list):
            errors.append("guidance.applicable_extensions must be an array")
        else:
            for index, extension in enumerate(extensions):
                try:
                    require_string(
                        extension,
                        f"guidance.applicable_extensions[{index}]",
                        max_length=200,
                    )
                except ValidationError as exc:
                    errors.append(str(exc))
        try:
            conflicts_resolved = require_bool(
                guidance.get("extension_conflicts_resolved_by_methodologist"),
                "guidance.extension_conflicts_resolved_by_methodologist",
            )
            if extensions and not conflicts_resolved:
                errors.append("extension conflicts require methodologist resolution")
        except ValidationError as exc:
            errors.append(str(exc))


def _validate_metadata(
    artifact_kind: str,
    value: Any,
    errors: list[str],
    warnings: list[str],
) -> None:
    if artifact_kind == "clinical_study_report_draft":
        fields = {
            "protocol_reference",
            "sap_reference",
            "data_cut_reference",
            "analysis_output_reference",
            "coding_dictionary_versions",
        }
        try:
            metadata = require_exact_keys(value, fields, "study_metadata")
            for field in fields - {"coding_dictionary_versions"}:
                require_string(metadata.get(field), f"study_metadata.{field}")
            versions = metadata.get("coding_dictionary_versions")
            if not isinstance(versions, list) or not versions:
                raise ValidationError(
                    "study_metadata.coding_dictionary_versions must be non-empty"
                )
            for index, version in enumerate(versions):
                require_string(
                    version,
                    f"study_metadata.coding_dictionary_versions[{index}]",
                    max_length=100,
                )
        except ValidationError as exc:
            errors.append(str(exc))
    elif artifact_kind == "randomized_trial_results_draft":
        fields = {
            "protocol_reference",
            "sap_reference",
            "registry_reference",
            "data_cut_reference",
            "analysis_output_reference",
        }
        try:
            metadata = require_exact_keys(value, fields, "study_metadata")
            for field in fields:
                require_string(metadata.get(field), f"study_metadata.{field}")
        except ValidationError as exc:
            errors.append(str(exc))
    else:
        fields = {
            "authorized_protocol_reference",
            "protocol_version",
            "registry_reference",
            "ethics_record_reference",
        }
        try:
            metadata = require_exact_keys(value, fields, "protocol_metadata")
            for field in fields - {"ethics_record_reference"}:
                require_string(metadata.get(field), f"protocol_metadata.{field}")
            if metadata.get("ethics_record_reference") is None:
                warnings.append("protocol_metadata.ethics_record_reference remains pending")
            else:
                require_string(
                    metadata.get("ethics_record_reference"),
                    "protocol_metadata.ethics_record_reference",
                )
        except ValidationError as exc:
            errors.append(str(exc))


def _validated_fact_ids(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValidationError(f"{field} must be an array")
    return [require_identifier(item, field) for item in value]


def validate_trial_manifest(data: dict[str, Any]) -> dict[str, Any]:
    """Return structural findings without evaluating trial content."""
    errors: list[str] = []
    warnings: list[str] = []
    artifact_kind = data.get("artifact_kind")
    route = ROUTES.get(artifact_kind)
    if route is None:
        return {
            "tool": TOOL,
            "status": "BLOCKED",
            "errors": [f"unsupported artifact_kind: {artifact_kind!r}"],
            "warnings": [],
            "review_required": True,
            "authorizes_clinical_use_or_submission": False,
        }

    try:
        require_exact_keys(data, route["top_fields"], "manifest")
        if data.get("schema_version") != "2.0":
            raise ValidationError("schema_version must be 2.0")
        if data.get("draft_status") != route["draft_status"]:
            raise ValidationError(
                "draft_status must preserve the blocked non-use/non-submission warning"
            )
        require_string(data.get("safety_notice"), "safety_notice", max_length=1000)
        require_data_class(data.get("data_classification"))
        require_string(data.get("authorized_purpose"), "authorized_purpose")
        if not require_bool(data.get("authorization_verified"), "authorization_verified"):
            errors.append("authorization_verified must be true")
        require_string(data.get("provenance_manifest"), "provenance_manifest")
    except ValidationError as exc:
        errors.append(str(exc))

    _validate_guidance(str(artifact_kind), data.get("guidance"), errors)
    _validate_metadata(
        str(artifact_kind),
        data.get(route["metadata_name"]),
        errors,
        warnings,
    )

    container_name = str(route["container"])
    expected_keys = tuple(route["keys"])
    container = data.get(container_name)
    if not isinstance(container, dict):
        errors.append(f"{container_name} must be an object")
        container = {}
    missing_keys = sorted(set(expected_keys) - set(container))
    extra_keys = sorted(set(container) - set(expected_keys))
    if missing_keys:
        errors.append(f"missing {container_name} keys: {missing_keys}")
    if extra_keys:
        errors.append(f"unexpected {container_name} keys: {extra_keys}")

    coverage: dict[str, str] = {}
    rationale_map = data.get("not_applicable_rationales", {})
    if container_name == "checklist_items" and not isinstance(rationale_map, dict):
        errors.append("not_applicable_rationales must be an object")
        rationale_map = {}
    for key in expected_keys:
        item = container.get(key)
        if not isinstance(item, dict):
            errors.append(f"{container_name}.{key} must be an object")
            continue
        try:
            item = require_exact_keys(
                item,
                route["item_fields"],
                f"{container_name}.{key}",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            continue
        status = item.get("status")
        coverage[key] = str(status)
        if status not in ALLOWED_STATUSES:
            errors.append(f"{container_name}.{key}.status is invalid")
            continue
        try:
            facts = _validated_fact_ids(
                item.get("source_fact_ids"),
                f"{container_name}.{key}.source_fact_ids",
            )
        except ValidationError as exc:
            errors.append(str(exc))
            facts = []
        if status == "verified_present":
            if not facts:
                errors.append(f"{container_name}.{key} requires a verified source fact")
            if container_name == "checklist_items":
                try:
                    require_string(
                        item.get("official_item_locator"),
                        f"{container_name}.{key}.official_item_locator",
                    )
                except ValidationError as exc:
                    errors.append(str(exc))
        elif status == "not_applicable_with_rationale":
            try:
                require_string(
                    (
                        item.get("rationale")
                        if container_name == "sections"
                        else rationale_map.get(key)
                    ),
                    (
                        f"{container_name}.{key}.rationale"
                        if container_name == "sections"
                        else f"not_applicable_rationales.{key}"
                    ),
                    max_length=500,
                )
            except ValidationError as exc:
                errors.append(str(exc))
        else:
            errors.append(f"{container_name}.{key} is {status}")

    if artifact_kind == "randomized_trial_results_draft":
        try:
            flow_facts = _validated_fact_ids(
                data.get("participant_flow_source_fact_ids"),
                "participant_flow_source_fact_ids",
            )
            if not flow_facts:
                errors.append("participant flow requires verified source facts")
        except ValidationError as exc:
            errors.append(str(exc))
    elif artifact_kind == "randomized_trial_protocol_reporting_manifest":
        try:
            timeline_facts = _validated_fact_ids(
                data.get("participant_timeline_source_fact_ids"),
                "participant_timeline_source_fact_ids",
            )
            if not timeline_facts:
                errors.append("participant timeline requires verified source facts")
        except ValidationError as exc:
            errors.append(str(exc))

    review = data.get("review")
    try:
        review = require_exact_keys(
            review,
            {*route["review_fields"], route["authorization_field"]},
            "review",
        )
        for field in route["review_fields"]:
            if review.get(field) != "completed":
                warnings.append(f"review.{field} remains required")
        authorization_field = str(route["authorization_field"])
        if review.get(authorization_field) is not False:
            errors.append(f"review.{authorization_field} must remain false")
    except ValidationError as exc:
        errors.append(str(exc))

    return {
        "tool": TOOL,
        "artifact_kind": artifact_kind,
        "guidance": route["guidance"],
        "status": "BLOCKED" if errors else "STRUCTURE_COMPLETE_REVIEW_REQUIRED",
        "coverage": coverage,
        "errors": errors,
        "warnings": warnings,
        "limitations": [
            "Checks item keys, statuses, and provenance references only.",
            "Does not validate conduct, analyses, clinical content, compliance, or submission format.",
        ],
        "review_required": True,
        "authorizes_clinical_use_or_submission": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check a bounded JSON ICH E3, CONSORT 2025, or SPIRIT 2025 "
            "coverage manifest; never claims compliance."
        )
    )
    parser.add_argument("input_file", help="Local trial-report manifest (.json)")
    parser.add_argument("-o", "--output", help="Optional local JSON report path")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _, data = load_json_object(args.input_file)
        report = validate_trial_manifest(data)
    except (OSError, ValidationError) as exc:
        report = error_report(TOOL, exc)
    try:
        write_json_report(report, args.output, overwrite=args.overwrite)
    except (OSError, ValidationError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0 if report["status"] == "STRUCTURE_COMPLETE_REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `assets/adverse_event_aggregate_input_template.csv`

```csv
analysis_set,treatment_group,meddra_version,system_organ_class,preferred_term,subjects_affected,event_count,denominator
```

### `assets/case_report_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "case_report_draft",
  "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_CLINICAL_USE_OR_SUBMISSION",
  "safety_notice": "Populate only from verified authorized synthetic or de-identified source facts. Do not infer clinical content. Qualified clinical, privacy, legal, authorship, and journal review is required.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "provenance_manifest": null,
  "guidance": {
    "name": "CARE",
    "checklist_version": "2013",
    "explanation_version": "2017",
    "target_journal_instructions_checked": false
  },
  "care_items": {
    "title": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "key_words": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "abstract": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "introduction": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "patient_information": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "clinical_findings": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "timeline": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "diagnostic_assessment": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "therapeutic_intervention": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "follow_up_and_outcomes": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "discussion": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "patient_perspective": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "informed_consent": {"status": "missing", "source_fact_ids": [], "rationale": null}
  },
  "privacy": {
    "deidentification_process_record": null,
    "publication_consent_record": null,
    "image_or_media_included": false,
    "reidentification_risk_reviewed": false
  },
  "review": {
    "qualified_clinical_review": "pending",
    "privacy_legal_review": "pending",
    "accountable_author_review": "pending",
    "submission_authorized": false
  }
}
```

### `assets/clinical_trial_csr_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "clinical_study_report_draft",
  "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_FILING_OR_SUBMISSION",
  "safety_notice": "Populate only from verified aggregate trial outputs and authorized source-fact manifests. Do not invent analyses, efficacy, safety, conclusions, or appendices. Qualified medical, statistical, safety, privacy, quality, and regulatory review is required.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "guidance": {
    "base": "ICH E3",
    "base_version": "Step 4 1995-11-30",
    "qa_version": "R1 2012-07-06",
    "gcp_version_considered": "ICH E6(R3) consolidated 2026-06-16",
    "regional_adoption_verified": false
  },
  "study_metadata": {
    "protocol_reference": null,
    "sap_reference": null,
    "data_cut_reference": null,
    "analysis_output_reference": null,
    "coding_dictionary_versions": []
  },
  "sections": {
    "title_page": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "synopsis": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "table_of_contents": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "abbreviations_and_definitions": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "ethics": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "investigators_and_administration": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "introduction": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "study_objectives": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "investigational_plan": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "study_patients": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "efficacy_evaluation": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "safety_evaluation": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "discussion_and_conclusions": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "tables_figures_graphs_not_in_text": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "reference_list": {"status": "missing", "source_fact_ids": [], "rationale": null},
    "appendices": {"status": "missing", "source_fact_ids": [], "rationale": null}
  },
  "provenance_manifest": null,
  "review": {
    "medical_review": "pending",
    "statistical_review": "pending",
    "safety_review": "pending",
    "privacy_legal_review": "pending",
    "quality_review": "pending",
    "regulatory_review": "pending",
    "submission_authorized": false
  }
}
```

### `assets/clinical_trial_results_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "randomized_trial_results_draft",
  "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_PUBLICATION_OR_SUBMISSION",
  "safety_notice": "This manifest tracks CONSORT item coverage only. It cannot design analyses, create results, infer participant flow, assess harms, or establish trial validity.",
  "data_classification": "aggregate",
  "authorized_purpose": null,
  "authorization_verified": false,
  "guidance": {
    "base": "CONSORT 2025",
    "item_count": 30,
    "statement_and_explanation_checked": false,
    "applicable_extensions": [],
    "applicable_extensions_reviewed": false,
    "extension_conflicts_resolved_by_methodologist": false
  },
  "study_metadata": {
    "protocol_reference": null,
    "sap_reference": null,
    "registry_reference": null,
    "data_cut_reference": null,
    "analysis_output_reference": null
  },
  "checklist_items": {
    "C01": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C02": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C03": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C04": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C05": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C06": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C07": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C08": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C09": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C10": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C11": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C12": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C13": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C14": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C15": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C16": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C17": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C18": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C19": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C20": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C21": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C22": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C23": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C24": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C25": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C26": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C27": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C28": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C29": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "C30": {"status": "missing", "source_fact_ids": [], "official_item_locator": null}
  },
  "not_applicable_rationales": {},
  "participant_flow_source_fact_ids": [],
  "provenance_manifest": null,
  "review": {
    "accountable_author_review": "pending",
    "methodologist_review": "pending",
    "statistical_review": "pending",
    "safety_review": "pending",
    "publication_authorized": false
  }
}
```

### `assets/clinical_trial_safety_aggregate_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "clinical_trial_safety_aggregate_draft",
  "draft_status": "BLOCKED_INCOMPLETE_NOT_AN_INDIVIDUAL_CASE_SAFETY_REPORT",
  "safety_notice": "Aggregate display only. Do not use for individual-case assessment, reportability, transmission, causality, expectedness, seriousness, filing, or submission.",
  "data_classification": "aggregate",
  "authorized_purpose": null,
  "authorization_verified": false,
  "local_only_handling_confirmed": false,
  "analysis_metadata": {
    "protocol_reference": null,
    "sap_reference": null,
    "data_cut_reference": null,
    "analysis_set": null,
    "counting_rule": null,
    "threshold_rule": null,
    "meddra_version": null,
    "meddra_language": null,
    "coding_source_reference": null
  },
  "input_csv": "adverse_event_aggregate_input_template.csv",
  "required_columns": [
    "analysis_set",
    "treatment_group",
    "meddra_version",
    "system_organ_class",
    "preferred_term",
    "subjects_affected",
    "event_count",
    "denominator"
  ],
  "prohibited_content": [
    "patient identifiers",
    "subject identifiers",
    "case identifiers",
    "verbatim terms",
    "narratives",
    "exact event dates",
    "contact information"
  ],
  "provenance_manifest": null,
  "review": {
    "safety_coding_review": "pending",
    "statistical_review": "pending",
    "privacy_review": "pending",
    "regulatory_review": "pending",
    "submission_authorized": false
  }
}
```

### `assets/consistency_manifest_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "consistency_manifest",
  "manifest_status": "BLOCKED_INCOMPLETE",
  "safety_notice": "Structured arithmetic and format checks only. Do not include identifiers or free-text patient records. The checker does not choose an authoritative source or change values.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "provenance_manifest": null,
  "dates": [],
  "date_ranges": [],
  "quantities": [],
  "proportions": [],
  "totals": []
}
```

### `assets/deidentification_process_checklist.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "deidentification_process_checklist",
  "process_status": "BLOCKED_NOT_ASSESSED",
  "safety_notice": "This checklist cannot guarantee de-identification or HIPAA compliance. Safe Harbor requires all regulatory conditions, including no actual knowledge of identifiability. Expert Determination requires an appropriately qualified expert.",
  "data_scope": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "local_only_handling_confirmed": false,
  "minimum_necessary_reviewed": false,
  "method": "not_selected",
  "safe_harbor_identifiers": {
    "names": "not_assessed",
    "geographic_subdivisions": "not_assessed",
    "dates_and_ages": "not_assessed",
    "telephone_numbers": "not_assessed",
    "fax_numbers": "not_assessed",
    "email_addresses": "not_assessed",
    "social_security_numbers": "not_assessed",
    "medical_record_numbers": "not_assessed",
    "health_plan_numbers": "not_assessed",
    "account_numbers": "not_assessed",
    "certificate_and_license_numbers": "not_assessed",
    "vehicle_identifiers": "not_assessed",
    "device_identifiers": "not_assessed",
    "urls": "not_assessed",
    "ip_addresses": "not_assessed",
    "biometric_identifiers": "not_assessed",
    "full_face_images": "not_assessed",
    "other_unique_characteristics_or_codes": "not_assessed"
  },
  "actual_knowledge_review": {
    "completed_by_authorized_privacy_reviewer": false,
    "record_reference": null
  },
  "expert_determination": {
    "completed_by_qualified_expert": false,
    "expert_documentation_reference": null,
    "anticipated_recipient_and_conditions_documented": false
  },
  "synthetic_or_aggregate_rationale": {
    "origin_verified": false,
    "record_reference": null
  },
  "residual_risk_review": {
    "free_text": "not_assessed",
    "small_cells_and_rare_cases": "not_assessed",
    "images_and_metadata": "not_assessed",
    "linked_data_and_quasi_identifiers": "not_assessed"
  },
  "review": {
    "privacy_legal_review": "pending",
    "institutional_release_review": "pending",
    "release_authorized": false
  }
}
```

### `assets/lab_report_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "laboratory_report_scaffold",
  "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_CLINICAL_USE_OR_RELEASE",
  "safety_notice": "Copy only released, verified laboratory source facts. Do not calculate, convert, interpret, flag, suppress, set reference intervals, set critical thresholds, notify, correct, release, or sign.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "guidance": {
    "base": "42 CFR 493.1291",
    "scope_verified_by_laboratory": false,
    "specialty_requirements": null,
    "state_accreditor_and_local_policy_versions": null
  },
  "report_status": null,
  "source_system_record": null,
  "fields": {
    "performing_laboratory": {"status": "missing", "source_fact_ids": []},
    "specimen": {"status": "missing", "source_fact_ids": []},
    "test_and_method": {"status": "missing", "source_fact_ids": []},
    "released_result": {"status": "missing", "source_fact_ids": []},
    "released_units": {"status": "missing", "source_fact_ids": []},
    "released_reference_interval": {"status": "missing", "source_fact_ids": []},
    "released_flags_or_comments": {"status": "missing", "source_fact_ids": []},
    "referral_laboratory_information": {"status": "missing", "source_fact_ids": []},
    "original_and_corrected_report_linkage": {"status": "missing", "source_fact_ids": []},
    "documented_notification_record": {"status": "missing", "source_fact_ids": []}
  },
  "provenance_manifest": null,
  "review": {
    "authorized_laboratory_review": "pending",
    "privacy_review": "pending",
    "released_from_authorized_system": false,
    "signature_present": false
  }
}
```

### `assets/pathology_report_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "pathology_report_scaffold",
  "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_CLINICAL_USE_OR_SIGNATURE",
  "safety_notice": "This scaffold cannot examine specimens or author observations, diagnosis, grade, stage, margins, biomarkers, or recommendations. A qualified pathologist must select current protocols and author the report.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "protocol_selection": {
    "cap_protocol_title": null,
    "cap_protocol_version": null,
    "specimen_and_procedure_scope_verified": false,
    "biomarker_protocol_title_and_version": null,
    "staging_system_and_edition": null,
    "local_policy_version": null
  },
  "report_status": null,
  "source_system_record": null,
  "fields": {
    "specimen_information": {"status": "missing", "source_fact_ids": []},
    "clinical_information_as_submitted": {"status": "missing", "source_fact_ids": []},
    "gross_observations_authored_by_pathologist": {"status": "missing", "source_fact_ids": []},
    "microscopic_observations_authored_by_pathologist": {"status": "missing", "source_fact_ids": []},
    "diagnosis_authored_by_pathologist": {"status": "missing", "source_fact_ids": []},
    "synoptic_data_element_response_pairs": {"status": "missing", "source_fact_ids": []},
    "ancillary_and_biomarker_results": {"status": "missing", "source_fact_ids": []},
    "correction_or_addendum_linkage": {"status": "missing", "source_fact_ids": []}
  },
  "provenance_manifest": null,
  "review": {
    "qualified_pathologist_review": "pending",
    "privacy_review": "pending",
    "final_report_created_in_authorized_system": false,
    "signature_present": false
  }
}
```

### `assets/provenance_manifest_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "provenance_manifest",
  "manifest_status": "BLOCKED_INCOMPLETE",
  "safety_notice": "Record local source locators, field paths, hashes, and verification metadata only. Do not copy PHI or patient narratives into this manifest.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "facts": [],
  "claims": [],
  "review": {
    "source_owner_review": "pending",
    "quality_review": "pending",
    "privacy_review": "pending",
    "release_authorized": false
  }
}
```

### `assets/quality_review_checklist.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "clinical_report_quality_review",
  "review_status": "BLOCKED_NOT_ASSESSED",
  "safety_notice": "A completed checklist records review activity only. It does not prove clinical correctness, compliance, approval, or readiness for signature, filing, publication, or submission.",
  "artifact_reference": null,
  "artifact_kind_reviewed": null,
  "guidance_and_version": [],
  "checks": {
    "allowed_data_class_confirmed": "not_assessed",
    "authorized_purpose_confirmed": "not_assessed",
    "minimum_necessary_confirmed": "not_assessed",
    "draft_warning_present": "not_assessed",
    "required_structure_present": "not_assessed",
    "all_populated_fields_have_verified_fact_ids": "not_assessed",
    "unsupported_claims_absent": "not_assessed",
    "source_conflicts_exposed": "not_assessed",
    "dates_and_chronology_checked": "not_assessed",
    "units_and_precision_checked": "not_assessed",
    "counts_denominators_and_percentages_checked": "not_assessed",
    "missingness_and_suppression_disclosed": "not_assessed",
    "terminology_versions_recorded": "not_assessed",
    "privacy_process_reviewed": "not_assessed",
    "consent_authorization_or_ethics_status_verified_if_applicable": "not_assessed",
    "clinical_specialist_review_completed": "not_assessed",
    "statistical_review_completed_if_applicable": "not_assessed",
    "safety_review_completed_if_applicable": "not_assessed",
    "privacy_legal_review_completed": "not_assessed",
    "regulatory_or_journal_review_completed_if_applicable": "not_assessed"
  },
  "unresolved_items": [],
  "review_record_references": [],
  "release_or_submission_authorized": false
}
```

### `assets/radiology_report_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "radiology_report_scaffold",
  "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_CLINICAL_USE_OR_SIGNATURE",
  "safety_notice": "This scaffold cannot interpret images or author findings, impressions, urgency, or recommendations. A qualified radiologist must author and sign the report in an authorized clinical system.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "guidance": {
    "base": "ACR Practice Parameter for Communication of Diagnostic Imaging Findings",
    "revision": "2025",
    "modality_specific_source": null,
    "local_policy_version": null
  },
  "report_status": null,
  "source_system_record": null,
  "fields": {
    "examination": {"status": "missing", "source_fact_ids": []},
    "clinical_indication": {"status": "missing", "source_fact_ids": []},
    "technique_and_limitations": {"status": "missing", "source_fact_ids": []},
    "comparison": {"status": "missing", "source_fact_ids": []},
    "findings_authored_by_radiologist": {"status": "missing", "source_fact_ids": []},
    "impression_authored_by_radiologist": {"status": "missing", "source_fact_ids": []},
    "nonroutine_communication_record": {"status": "missing", "source_fact_ids": []},
    "correction_or_addendum_linkage": {"status": "missing", "source_fact_ids": []}
  },
  "provenance_manifest": null,
  "review": {
    "qualified_radiologist_review": "pending",
    "privacy_review": "pending",
    "final_report_created_in_authorized_system": false,
    "signature_present": false
  }
}
```

### `assets/research_summary_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "aggregate_clinical_research_summary_draft",
  "draft_status": "BLOCKED_INCOMPLETE_DRAFT_NOT_FOR_CLINICAL_DECISION_MAKING",
  "safety_notice": "Summarize only verified aggregate research outputs. Do not generate patient-level content, clinical advice, causal conclusions, or unverified interpretations.",
  "data_classification": "aggregate",
  "authorized_purpose": null,
  "authorization_verified": false,
  "reporting_route": {
    "study_design": null,
    "base_reporting_guideline_and_version": null,
    "applicable_extensions": [],
    "protocol_reference": null,
    "sap_reference": null,
    "registry_reference": null
  },
  "sections": {
    "scope_and_population": {"status": "missing", "source_fact_ids": []},
    "methods": {"status": "missing", "source_fact_ids": []},
    "analysis_set_and_estimand": {"status": "missing", "source_fact_ids": []},
    "results": {"status": "missing", "source_fact_ids": []},
    "missingness_and_exclusions": {"status": "missing", "source_fact_ids": []},
    "safety_summary_if_applicable": {"status": "missing", "source_fact_ids": []},
    "limitations": {"status": "missing", "source_fact_ids": []},
    "interpretation_by_accountable_authors": {"status": "missing", "source_fact_ids": []},
    "funding_and_conflicts": {"status": "missing", "source_fact_ids": []}
  },
  "provenance_manifest": null,
  "review": {
    "accountable_author_review": "pending",
    "statistical_review": "pending",
    "clinical_review": "pending",
    "privacy_review": "pending",
    "publication_authorized": false
  }
}
```

### `assets/terminology_manifest_template.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "terminology_manifest",
  "manifest_status": "BLOCKED_INCOMPLETE",
  "safety_notice": "Record only codes already selected and verified by qualified reviewers. Syntax or local-dictionary matching does not validate clinical meaning.",
  "data_classification": null,
  "authorized_purpose": null,
  "authorization_verified": false,
  "provenance_manifest": null,
  "entries": []
}
```

### `assets/trial_protocol_reporting_checklist.json`

```json
{
  "schema_version": "2.0",
  "artifact_kind": "randomized_trial_protocol_reporting_manifest",
  "draft_status": "BLOCKED_INCOMPLETE_REPORTING_CHECKLIST_NOT_A_PROTOCOL_OR_ETHICS_APPROVAL",
  "safety_notice": "This manifest tracks SPIRIT reporting-item coverage only. It does not design, approve, register, conduct, amend, or submit a trial protocol.",
  "data_classification": "aggregate",
  "authorized_purpose": null,
  "authorization_verified": false,
  "guidance": {
    "base": "SPIRIT 2025",
    "item_count": 34,
    "statement_and_explanation_checked": false,
    "applicable_extensions": [],
    "applicable_extensions_reviewed": false,
    "extension_conflicts_resolved_by_methodologist": false
  },
  "protocol_metadata": {
    "authorized_protocol_reference": null,
    "protocol_version": null,
    "registry_reference": null,
    "ethics_record_reference": null
  },
  "checklist_items": {
    "S01": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S02": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S03": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S04": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S05": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S06": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S07": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S08": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S09": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S10": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S11": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S12": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S13": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S14": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S15": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S16": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S17": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S18": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S19": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S20": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S21": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S22": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S23": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S24": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S25": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S26": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S27": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S28": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S29": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S30": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S31": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S32": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S33": {"status": "missing", "source_fact_ids": [], "official_item_locator": null},
    "S34": {"status": "missing", "source_fact_ids": [], "official_item_locator": null}
  },
  "not_applicable_rationales": {},
  "participant_timeline_source_fact_ids": [],
  "provenance_manifest": null,
  "review": {
    "investigator_sponsor_review": "pending",
    "methodologist_review": "pending",
    "statistical_review": "pending",
    "safety_review": "pending",
    "ethics_regulatory_review": "pending",
    "protocol_approved": false
  }
}
```
