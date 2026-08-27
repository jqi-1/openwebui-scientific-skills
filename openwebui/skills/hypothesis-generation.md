---
name: hypothesis-generation
description: Formulate evidence-bounded scientific questions, candidate hypotheses, rival explanations, causal or associational claims, discriminating predictions, measurements, and preregistration-ready analysis plans. Use when turning observations or preliminary findings into transparent, testable research plans without treating hypotheses as facts.
---

# Scientific Hypothesis Generation

Turn an observation into a transparent set of candidate explanations and tests. A hypothesis is a proposal to be challenged, not a finding, fact, diagnosis, or recommendation.

## Non-negotiable boundaries

Before using unpublished, sensitive, controlled, personal, proprietary, export-controlled, or security-relevant material:

1. Confirm authorization and the applicable institutional, funder, publisher, data-use, privacy, and AI policies.
2. Keep the material local unless an authorized human explicitly approves a named external destination and data scope.
3. Minimize inputs. Do not place sensitive or unpublished data in web searches or external AI systems without authorization.
4. Stop at the appropriate human, animal, biosafety, dual-use, data-governance, or regulatory gate.

Never:

- present a hypothesis, mechanism, causal effect, citation, or apparent pattern as established evidence;
- claim novelty because a quick search found nothing;
- infer causation from association, temporal order alone, predictive accuracy, or model output;
- supply patient-specific diagnosis, treatment, dose, prognosis, or other clinical advice;
- provide harmful experimental optimization or operational detail for pathogens, toxins, weapons, evasion, or other misuse;
- bypass IRB/REC, IACUC, IBC, biosafety, dual-use, privacy, legal, or regulatory review;
- fabricate sources, identifiers, search coverage, data, results, approvals, or preregistration;
- automatically score, rank, select, accept, or reject scientific hypotheses.

If a request crosses a safety gate, produce only a high-level risk/oversight note and route it to the qualified local authority. Do not continue with operational detail.

## Keep the objects distinct

| Object | Meaning |
|---|---|
| **Observation** | What was measured, noticed, or reported, with provenance and uncertainty |
| **Research question** | The answerable question that defines scope |
| **Hypothesis** | A candidate explanatory or relational proposition |
| **Mechanism** | The proposed process connecting conditions to an outcome |
| **Causal estimand** | The precisely defined causal contrast to estimate |
| **Prediction** | An observable implication derived before checking the target result |
| **Alternative explanation** | A rival account, including bias or non-causal explanations |
| **Null hypothesis** | A specified no-effect/no-difference model used by an analysis |
| **Negative control** | A control expected not to operate through the proposed mechanism |
| **Operationalization** | How a construct becomes a variable, measurement, intervention, or category |
| **Analysis plan** | Prespecified transformations, models, contrasts, uncertainty, and decision rules |
| **Evidence** | Observations or sources that bear on a claim; never the claim itself |

Do not collapse these labels. A mechanistic story is not a prediction; a prediction is not evidence; rejection of one null does not prove a mechanism; support for one candidate does not eliminate unconsidered rivals.

## Workflow

### 1. Run the scope and safety gate

Record:

- accountable human owner and intended use;
- data sensitivity, authorization, retention, and permitted processing;
- affected people, animals, ecosystems, communities, or security interests;
- required ethics, feasibility, biosafety, dual-use, and regulatory reviews;
- unresolved blocks and domain expertise needed.

No script approval is an ethics, safety, regulatory, or scientific approval.

### 2. Freeze the observation

Write the observation before interpretation:

- measurement or source;
- population, system, place, and time;
- unit of observation and unit of analysis;
- uncertainty, missingness, exclusions, and preprocessing;
- whether the pattern was expected, exploratory, or selected after viewing results.

Use “reported,” “observed,” or “associated,” not causal language, unless a causal design and estimand justify it.

### 3. Frame the research question

Choose a framework only when it fits:

- **PICO/PICOT** for intervention/effectiveness questions: population, intervention, comparator, outcome, and optionally time.
- **PECO** for exposure questions.
- **Population–index test–reference standard–target condition** for diagnostic accuracy.
- **Population–prognostic factor–outcome–time** for prognosis.
- A domain-specific construct–context–outcome frame for qualitative, descriptive, mechanistic, or theoretical work.

PICO is not a universal template. Define stakeholders, context, boundaries, feasibility, and what answer would change knowledge or practice. FINER is a question-refinement mnemonic—Feasible, Interesting, Novel, Ethical, Relevant—not a scoring system. Treat “Novel” as unresolved until a documented, fit-for-purpose search and expert review support it.

### 4. Establish a dated evidence boundary

Search before making literature-dependent statements. Prefer primary research, official policies, primary methods papers, current reporting guidelines, and systematic reviews used for orientation.

Record:

- search date and cutoff;
- databases/indexes, queries, filters, and screening boundary;
- included and excluded source types;
- sources supporting, challenging, or contextualizing each claim;
- known access, language, database, and time limitations.

A search can establish what was searched, not universal absence. Say “not located within the documented search boundary,” never “no prior work exists.” Use `assets/search_boundary_template.json`, `assets/evidence_ledger_template.csv`, and `references/literature_search_strategies.md`.

### 5. Generate rivals before choosing tests

Create multiple candidates from genuinely different explanatory classes when plausible:

- proposed mechanism;
- measurement or processing artifact;
- confounding or common cause;
- selection or attrition;
- conditioning on a collider;
- reverse causation;
- temporal, contextual, or boundary-condition differences;
- stochastic variation;
- competing mechanisms at another scale.

Generate an initial rival set independently before AI-assisted expansion to reduce anchoring and homogenization. Do not force a fixed number or false symmetry. Keep every candidate labeled `candidate`.

Platt’s strong-inference pattern motivates alternative hypotheses and crucial tests, but failed alternatives do not make the survivor true. Unknown alternatives, auxiliary assumptions, measurement error, and mixed mechanisms remain possible.

### 6. Declare the claim type and estimand

Classify each target as:

- descriptive;
- associational;
- predictive;
- causal;
- mechanistic.

For a causal target, define before analysis:

- target population or system;
- intervention/exposure and comparator;
- outcome and time horizon;
- population-level summary;
- treatment versions and intercurrent-event handling where relevant;
- identification assumptions and target-trial/design analogue.

Document confounding, selection, collider, measurement, and reverse-causation risks separately. An observational causal estimate remains assumption-dependent. Use `references/causal_inference_and_claims.md`.

### 7. Derive discriminating predictions

For every candidate:

1. State conditions and boundary conditions.
2. Name the observable and measurement.
3. State the expected pattern and uncertainty.
4. State a result incompatible with the candidate under declared assumptions.
5. Contrast the expected result with at least one rival.
6. Define indeterminate outcomes and what would be learned from them.

Prefer tests where rivals predict meaningfully different outcomes. Add positive, procedural, and negative controls when scientifically appropriate. A negative control must be incapable of operating through the target mechanism while sharing relevant bias pathways; it is not a decorative untreated group.

Use `assets/prediction_rival_matrix_template.csv` and `assets/falsification_controls_template.json`.

### 8. Operationalize and validate measurement

For every construct record:

- variable role and operational definition;
- population/system, unit, timing, and conditions;
- instrument/method, calibration, quality control, and masking;
- reliability/repeatability;
- validity evidence and applicability;
- missingness, detection limits, transformations, cut points, and their rationales;
- measurement invariance or cross-group comparability when relevant;
- foreseeable measurement bias and limitations.

Do not treat a convenient proxy as the construct itself. Validate with:

```bash
python3 scripts/check_operationalization.py local-operationalization.json
```

### 9. Match design and analysis to the claim

Specify:

- sampling, experimental unit, allocation, randomization, masking, and controls;
- inclusion/exclusion and stopping rules;
- sample-size, precision, or information rationale based on declared assumptions;
- outcomes, contrasts, estimands, models, effect measures, and uncertainty;
- missing-data and intercurrent-event handling;
- multiplicity across outcomes, models, subgroups, looks, and hypotheses;
- assumptions, diagnostics, robustness, and sensitivity analyses;
- replication or independent validation plan;
- what is confirmatory versus exploratory.

Do not use universal sample-size minima. Do not interpret a thresholded p-value as the probability a hypothesis is true or as effect importance. See `references/experimental_design_patterns.md`.

For intervention trials, use the current SPIRIT 2025 protocol guidance and CONSORT 2025 reporting guidance where applicable. These improve completeness; they do not certify design quality, ethics, or regulatory compliance.

### 10. Prevent HARKing and expose deviations

Before accessing the target outcomes, timestamp the question, candidates, predictions, outcomes, exclusions, transformations, analysis, multiplicity, missing-data plan, and stopping rule when feasible.

Afterward:

- label data-dependent ideas and analyses exploratory;
- preserve and report planned analyses;
- list deviations with date, rationale, who decided, and expected impact;
- never rewrite an observed pattern as an a priori prediction.

Preregistration is a transparent plan, not a ban on adaptation. Registered Reports add results-blind peer review and in-principle acceptance under journal policy. See `references/preregistration_and_open_science.md`.

### 11. Plan replication and updating

Distinguish:

- **reproducibility:** consistent computational results from the same data/code/conditions;
- **replicability:** consistency across studies collecting new data for the same question.

Preserve provenance, versions, code, materials, and decision logs when sharing is authorized. Plan independent replication or transport tests across relevant boundaries. Update candidate status when contrary, null, or replication evidence arrives; do not hide negative results.

### 12. Apply human accountability

The accountable human must verify:

- every citation and source-to-claim link;
- domain plausibility and measurement validity;
- causal assumptions and statistical design;
- ethics, feasibility, safety, privacy, and regulatory status;
- all AI-assisted text, ideas, and citations;
- whether broader expertise or community input is required.

AI can confabulate citations, anchor reasoning, and homogenize candidate sets. Record permitted AI use and material influence. Keep independent human ideation and rival generation in the process.

## Local tool index

All CLIs are bounded, dependency-free, local, deterministic, and non-scoring:

| Task | Asset | Command |
|---|---|---|
| Hypothesis-record schema | `assets/hypothesis_record_template.json` | `python3 scripts/validate_hypothesis_schema.py record.json` |
| Measurement checklist | `assets/operationalization_template.json` | `python3 scripts/check_operationalization.py checklist.json` |
| Prediction/rival matrix | `assets/prediction_rival_matrix_template.csv` | `python3 scripts/validate_prediction_matrix.py matrix.csv` |
| Claim-language lint | Annotated Markdown | `python3 scripts/lint_causal_claims.py draft.md` |
| Falsification/controls | `assets/falsification_controls_template.json` | `python3 scripts/check_falsification_controls.py controls.json` |
| Evidence/source audit | `assets/evidence_ledger_template.csv` + `assets/search_boundary_template.json` | `python3 scripts/audit_evidence_ledger.py ledger.csv boundary.json` |
| Preregistration scaffold | `assets/preregistration_scaffold_template.md` | `python3 scripts/generate_preregistration_scaffold.py record.json -o preregistration.md` |

Exit codes are `0` for structurally valid output, `1` for completed validation with errors, and `2` for malformed/unsafe input. Reports validate declarations and internal consistency only; they do not verify scientific truth or choose a hypothesis. Full schemas are in `references/tool_reference.md`.

## References

- `references/concepts_and_workflow.md` — object model, strong inference, uncertainty, and candidate lifecycle
- `references/hypothesis_quality_criteria.md` — non-scoring human review criteria
- `references/literature_search_strategies.md` — traceable, bounded evidence search
- `references/causal_inference_and_claims.md` — estimands and causal-bias risks
- `references/experimental_design_patterns.md` — design, controls, measurement, multiplicity, and replication
- `references/preregistration_and_open_science.md` — preregistration, Registered Reports, deviations, and open science
- `references/ethics_safety_and_ai.md` — oversight gates, dual use, data handling, and responsible AI
- `references/tool_reference.md` — CLI schemas, limits, and examples
- `references/source_ledger.md` — dated authoritative source notes
- `references/security_validation.md` — baseline findings and validation record

The bundled source ledger is `assets/source_ledger.csv`, verified through **2026-07-23**. Recheck time-sensitive policy and guidance before a later or jurisdiction-specific use.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/hypothesis-generation/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/causal_inference_and_claims.md`

# Causal Inference and Claim Discipline

## Start with the scientific target

Association, prediction, intervention effects, and mechanisms answer different questions:

- **Descriptive:** What is the distribution or pattern?
- **Associational:** How do measured variables co-vary in the observed data?
- **Predictive:** How well does information predict outcomes in a target setting?
- **Causal:** What would differ under specified interventions or exposure conditions?
- **Mechanistic:** Through which process would the causal change occur?

A model can predict accurately without identifying a causal effect. A randomized effect estimate can identify an intervention contrast without establishing the complete mechanism.

## Define a causal estimand

Following the causal-question and ICH E9(R1) principles where applicable, specify:

1. **Population/system:** To whom or what does the contrast apply?
2. **Intervention/exposure:** What condition is set, assigned, or contrasted?
3. **Comparator:** What alternative condition is compared?
4. **Outcome:** What variable is affected and how is it measured?
5. **Time horizon:** When is the outcome assessed?
6. **Population summary:** Mean difference, risk ratio, quantile contrast, survival summary, or another target.
7. **Intercurrent events:** How are post-assignment events handled when they affect interpretation or measurement?
8. **Treatment versions:** Are interventions sufficiently well defined?

The estimand should exist before choosing an estimator or model.

## Counterfactual contrast

Causal effects compare outcomes under different conditions for the same target units, although both conditions cannot usually be observed for one unit. Identification therefore depends on design and assumptions.

For observational data, state:

- target-trial analogue or other design logic;
- consistency/well-defined intervention assumptions;
- exchangeability/no-unmeasured-confounding assumptions;
- positivity/overlap;
- interference assumptions;
- measurement and missingness assumptions;
- model assumptions introduced by estimation.

Do not write “controlled for confounding” as if adjustment proves exchangeability.

## Bias pathways

### Confounding

A common cause of exposure/intervention and outcome can create or obscure an association. Address through design, randomization where ethical/feasible, restriction, matching, measurement and adjustment of justified common causes, negative controls, sensitivity analysis, or triangulation.

Risks:

- unmeasured or poorly measured common causes;
- time-varying confounders affected by prior treatment;
- inappropriate adjustment for instruments, mediators, or colliders;
- residual confounding after coarse categorization.

### Selection bias

Selection into the sample, analysis, follow-up, or observed outcome can depend on causes of exposure and outcome. Record:

- sampling and eligibility;
- participation and consent;
- exclusions;
- attrition and censoring;
- complete-case restrictions;
- availability of measurements;
- conditioning introduced by data linkage.

### Collider bias

A collider is a common effect of two variables. Conditioning on it or its descendant can open a non-causal path. Common sources include:

- selection into a study or subgroup;
- restricting to diagnosed, hospitalized, tested, or surviving participants;
- adjusting for a post-exposure variable affected by another cause of the outcome;
- using complete cases when missingness is jointly caused.

More covariates are not automatically better.

### Reverse causation

The outcome or its precursors may influence the exposure or measurement. Cross-sectional order is especially weak evidence of direction. Use temporal design, lagged measurements, incident outcomes, intervention, negative controls, or explicit bidirectional candidates where appropriate.

### Measurement bias

Measurement error can:

- attenuate or inflate estimates;
- differ by exposure or outcome;
- induce apparent interactions;
- distort covariate adjustment;
- affect selection into analysis.

Operationalization and validation are part of causal design, not a later documentation task.

## Mediators and effect modifiers

- A **mediator** lies on a causal pathway. Adjusting for it changes the target from total to a direct or controlled effect and introduces additional assumptions.
- An **effect modifier** describes variation in a causal contrast across strata. It is not synonymous with statistical interaction in every scale.
- A **confounder** is defined relative to a target causal contrast and design, not simply by association with the outcome.

Label the intended role before analysis and justify it with domain knowledge and a causal structure.

## Negative controls

Lipsitch, Tchetgen Tchetgen, and Cohen distinguish negative-control exposures and outcomes:

- A negative-control exposure should not cause the target outcome through the proposed mechanism but should share relevant confounding/bias pathways.
- A negative-control outcome should not be caused by the target exposure through the proposed mechanism but should share relevant bias pathways.

Specify:

- why the target mechanism cannot operate;
- which biases should be shared;
- expected result;
- implication of control failure;
- alternative reasons for a non-null control result.

Negative controls detect some biases under assumptions; they do not prove absence of bias.

## Claim-language rules

### Associational

Use:

- “was associated with”;
- “co-varied with”;
- “predicted in the evaluated dataset”;
- “the adjusted association.”

State design, population, timing, effect/summary measure, uncertainty, and limitations.

### Causal

Use causal verbs only when:

- the causal estimand is explicit;
- design/identification logic is stated;
- assumptions and sensitivity are visible;
- confounding, selection, collider, reverse-causation, and measurement risks are addressed;
- language is calibrated to the evidence.

For observational work, “estimated causal effect under the stated assumptions” is often more accurate than an unqualified causal declaration.

### Mechanistic

Distinguish:

- direct evidence for process steps;
- mediation or intermediate measurements;
- perturbation/rescue evidence;
- temporal ordering;
- analogy or plausibility only.

A causal intervention effect does not by itself verify the proposed pathway.

## Markdown claim annotations

The bundled linter recognizes line-level annotations:

```markdown
[claim:associational] Exposure X was associated with outcome Y in the observed cohort.

[claim:causal][estimand:E1][identification:observational_assumption_dependent][confounding:unresolved][selection:assessed][collider:assessed][reverse-causation:assessed] Under the stated assumptions, intervention X would reduce outcome Y over 12 months.
```

Allowed risk states are `assessed`, `unresolved`, and `not_applicable`. “Assessed” records that a human evaluation exists; it does not mean the risk is absent.

Run:

```bash
python3 scripts/lint_causal_claims.py local-draft.md
```

The linter is lexical. It can miss causal language, flag benign phrases, and cannot judge whether a design identifies an effect.

## Intervention-trial context

For intervention hypotheses:

- align objectives, estimands, outcomes, timing, harms, and analysis;
- use SPIRIT 2025 for protocol reporting and CONSORT 2025 for trial-result reporting;
- preserve access to protocol and statistical analysis plan;
- report important post-start changes and non-prespecified outcomes/analyses;
- include harms and participant/public involvement where applicable.

Reporting completeness is not proof of ethical approval, design validity, regulatory compliance, or treatment efficacy.

### `references/concepts_and_workflow.md`

# Concepts and Candidate Lifecycle

## Purpose

This reference prevents common category errors in hypothesis work. It is a vocabulary and workflow guide, not a theory of confirmation and not an automatic ranking method.

## Object model

### Observation

A bounded account of what was detected or reported:

- source or measurement;
- population/system, place, and time;
- unit of observation;
- preprocessing, exclusions, missingness, and uncertainty;
- whether the observation was expected or selected after inspection.

An observation can be mistaken, biased, or unrepresentative. It does not explain itself.

### Research question

An answerable question that fixes the scope of inquiry. It should identify the target population/system, variables or interventions, comparator where meaningful, outcome, timeframe, context, and claim type.

PICO/PICOT is appropriate for many intervention-effect questions. It is not a universal ontology. Use a framework matched to the question and involve affected stakeholders where appropriate.

### Hypothesis

A candidate proposition that could explain or relate observations and yield testable implications. Keep its status as `candidate` until evidence changes the state. Avoid “validated hypothesis,” “proven mechanism,” and similar language unless the statement is being used only to quote a source accurately.

### Mechanism

A proposed process connecting antecedent conditions to an outcome. A mechanism should identify entities, activities, ordering, and boundary conditions where the domain permits. A plausible narrative without discriminating predictions remains a story.

### Causal estimand

A precise target causal contrast. At minimum, state:

- target population/system;
- intervention/exposure and comparator;
- outcome and time horizon;
- population-level summary;
- treatment versions and intercurrent-event strategy where relevant;
- identification assumptions.

The estimand is the target, the estimator is the method, and the estimate is the numerical result.

### Prediction

An observable implication derived from a candidate before checking the target result. A useful prediction specifies conditions, measurement, expected pattern, uncertainty, and an incompatible result. It should distinguish at least one rival when possible.

### Alternative explanation

A rival account that could produce the same observation. Rivals include:

- distinct mechanisms;
- measurement or processing artifacts;
- confounding/common causes;
- selection or attrition;
- collider conditioning;
- reverse causation;
- contextual or temporal heterogeneity;
- stochastic variation.

Rivals can coexist. Do not force mutual exclusivity when a mixed explanation is scientifically plausible.

### Null hypothesis

A defined no-effect/no-difference model used in an analysis. It is not “nothing happened,” and failure to reject it does not establish equivalence or absence. Define compatibility, equivalence, or non-inferiority rules separately when those are the scientific targets.

### Negative control

A control in which the target mechanism should not operate but relevant bias pathways should remain. Negative exposure and negative outcome controls can reveal confounding, selection, measurement, or analytic bias when their assumptions are credible. A negative control does not repair bias automatically.

### Operationalization

The mapping from a construct to a measurement, category, intervention, or variable. Record instrument/method, unit, timing, population/system, validity, reliability, calibration, missingness, transformations, cut points, and limitations.

### Analysis plan

The planned mapping from data to estimand, prediction, or descriptive target. It includes units, populations, transformations, models, contrasts, effect measures, uncertainty, missingness, multiplicity, diagnostics, sensitivity analyses, and decision rules.

### Evidence

Empirical observations or documented sources that bear on claims. Record whether a source supports, challenges, contextualizes, or supplies a method. Citation presence does not prove claim support; a human must inspect the source.

## Candidate lifecycle

Use explicit states:

1. **Draft candidate** — generated but not yet searched or operationalized.
2. **Evidence-bounded candidate** — linked to a dated search and source ledger.
3. **Test-ready candidate** — has measurements, rivals, falsifiers, controls, and analysis links.
4. **Preregistered candidate** — time-stamped before the relevant outcome was inspected.
5. **Tested candidate** — results and deviations are available.
6. **Retained, revised, challenged, or unresolved** — human interpretation with uncertainty.

Never use `true`, `proven`, or `selected_winner` as a machine-generated state.

## Multiple hypotheses and strong inference

Platt’s 1964 strong-inference essay advocates:

1. devising alternative hypotheses;
2. devising a crucial experiment with alternative possible outcomes that exclude candidates;
3. performing the experiment cleanly;
4. recycling the process with subhypotheses.

Use this as a discipline for contrast, not as a guarantee of truth. In practice:

- alternatives may be incomplete;
- candidates may not be mutually exclusive;
- auxiliary assumptions can fail;
- measurements may not distinguish the intended mechanisms;
- a “crucial” result may be indeterminate;
- exclusions remain provisional.

Always include an “unknown or mixed explanation” path in interpretation.

## Exploratory and confirmatory modes

### Exploratory

- Generates observations, candidates, variables, and models.
- Can be data-dependent.
- Must record that dependence.
- Produces hypotheses for future tests rather than relabeling the same-data analysis as confirmation.

### Confirmatory

- Defines hypotheses, outcomes, exclusions, transformations, models, and decision rules before inspecting the target result.
- Preserves the planned analysis.
- Reports deviations and additional analyses transparently.

Both modes are scientifically valuable. The integrity failure is not exploration; it is presenting exploration as if it were prespecified.

## Uncertainty vocabulary

Prefer:

- “candidate explanation”;
- “consistent with under the stated assumptions”;
- “challenges this candidate if measurement and design assumptions hold”;
- “not distinguished by this result”;
- “not located within the documented search boundary”;
- “requires replication or external validation.”

Avoid:

- “proved” or “disproved” for ordinary empirical results;
- “novel” based only on no quick search hit;
- “no effect” from a non-significant result;
- “causes” from an unqualified association;
- “the mechanism” when several remain plausible.

## Minimum handoff

A hypothesis package should contain:

- frozen observation;
- framed question and claim type;
- dated search boundary and source ledger;
- candidate hypotheses and mechanisms;
- rivals and bias explanations;
- causal estimand if applicable;
- discriminating predictions and falsifiers;
- operationalization and measurement-validity record;
- nulls and controls;
- design and analysis plan;
- uncertainty and boundary conditions;
- ethics/safety/regulatory gates;
- preregistration/deviation plan;
- accountable human review.

### `references/ethics_safety_and_ai.md`

# Ethics, Safety, Feasibility, and Responsible AI

## This is a routing guide

This reference helps identify gates. It is not legal, medical, regulatory, biosafety, biosecurity, export-control, ethics, or institutional advice. Requirements vary by jurisdiction, sponsor, institution, organism, material, and intended use.

When applicability is uncertain, mark the gate `undetermined`, stop operational planning, and obtain a determination from the qualified local authority.

## Universal intake

Record:

- accountable owner and institution;
- intended purpose and foreseeable misuse;
- affected people, animals, communities, ecosystems, infrastructure, or security interests;
- data and material sensitivity;
- funding, jurisdiction, and collaborating sites;
- required expertise;
- conflicts and incentives;
- approvals, determinations, and unresolved blocks;
- less risky ways to answer the question.

Feasibility never overrides ethics or safety.

## Human-participant gate

Potential triggers include:

- intervention or interaction with living people;
- identifiable private information or biospecimens;
- secondary use, linkage, re-identification, recruitment, or contact;
- vulnerable populations or sensitive topics;
- international or community-governed data.

Required action:

- obtain an IRB/REC or other authorized determination before research starts;
- do not self-declare exemption;
- address consent or authorized waiver, privacy, security, equitable selection, risk/benefit, compensation, return of results, and community governance as applicable;
- use additional protections required by law or policy.

In the United States, HHS 45 CFR 46 includes the Common Rule and additional subparts. Local and non-U.S. rules can differ. The 2024 revision of the World Medical Association Declaration of Helsinki is a relevant international ethical statement for medical research involving human participants.

This skill does not provide clinical advice or authorize an intervention.

## Animal-research gate

Potential triggers include live vertebrate animals, field capture, breeding, procedures, tissues tied to ongoing animal activities, or covered training/testing.

Required action:

- obtain the applicable IACUC or equivalent approval before work;
- establish institutional assurance and veterinary oversight where required;
- apply replacement, reduction, and refinement;
- justify species/model, numbers, endpoints, welfare monitoring, analgesia/anesthesia, and humane endpoints through the authorized process;
- use current reporting guidance such as ARRIVE when applicable.

The bundled tools do not calculate animal numbers or approve protocols.

## Biosafety and biosecurity gate

Potential triggers include:

- recombinant or synthetic nucleic acids;
- infectious agents, toxins, biological materials, gene transfer, or modified organisms;
- environmental release;
- select agents or regulated materials;
- procedures that could alter hazard, host range, pathogenicity, transmissibility, resistance, or detection;
- work beyond established institutional containment and training.

Required action:

- stop before operational detail;
- route to the biosafety officer, Institutional Biosafety Committee, and other required authority;
- use the current NIH Guidelines, CDC/NIH *Biosafety in Microbiological and Biomedical Laboratories*, local biosafety manual, and applicable regulations;
- document containment and occupational-health decisions only after authorized review.

Do not infer a containment level or operating procedure from this skill.

## Dual-use and harmful-use gate

Potential triggers include research, data, models, or protocols that could reasonably enable:

- increased biological harm or spread;
- evasion of detection, treatment, control, or safeguards;
- scalable production or dissemination of harmful agents;
- weaponization;
- exploitation of critical vulnerabilities;
- transfer of restricted technical information.

Required action:

1. Do not provide optimization, stepwise procedures, parameter choices, sequences, acquisition pathways, or troubleshooting that increase harmful capability.
2. Preserve only a high-level scientific question, benefit rationale, and risk statement.
3. Route to institutional dual-use/biosecurity review, funder, legal/export-control, and other required authorities.
4. Follow current policy, award terms, and jurisdiction-specific controls.

### U.S. policy status checked 2026-07-23

- Executive Order 14292 of May 5, 2025 directed revision/replacement of the 2024 U.S. Government DURC/PEPP policy and paused federally funded research meeting its “dangerous gain-of-function” definition pending the replacement policy.
- NIH Notice NOT-OD-25-112 stated that the Executive Order superseded NIH implementation of the 2024 DURC/PEPP policy and rescinded NOT-OD-25-061.
- The HHS/ASPR policy page still stated at the verification date that federal departments and agencies would revise or replace the 2024 policy and that the page would be updated when the revised policy became available.

Do not use the superseded 2024 implementation as current clearance. Recheck the official policy and award terms for every project because this status is time-sensitive.

WHO’s *Global Guidance Framework for the Responsible Use of the Life Sciences* provides an international risk-governance framework; it does not replace national or local rules.

## Data-governance gate

Before using data:

- confirm authority, consent, license, data-use agreement, and purpose limitation;
- classify sensitivity and re-identification risk;
- minimize fields and access;
- use approved storage, retention, deletion, audit, and sharing controls;
- address community and Indigenous governance;
- separate public, controlled, confidential, proprietary, and export-controlled materials.

Passing a local schema check is not de-identification, anonymization, HIPAA compliance, GDPR compliance, or authorization to share.

## Regulatory gate

Potential triggers include:

- human interventions or clinical investigations;
- drugs, biologics, devices, diagnostics, or software intended for clinical use;
- environmental release;
- genetically modified organisms;
- regulated laboratory, animal, agricultural, or chemical activities;
- claims intended for product labeling, approval, or public-health action.

Record:

- intended use;
- jurisdiction;
- product/activity classification;
- sponsor and responsible regulatory owner;
- applicable quality system or submission route;
- current determination and source/date.

Do not infer regulatory status from a research label, reporting checklist, or generated artifact.

## Feasibility gate

Assess:

- scientific and technical capability;
- validated measurement;
- statistical information/precision;
- qualified personnel and facilities;
- time and resources;
- access to population/system;
- approvals and material/data access;
- foreseeable failure and stopping criteria.

If infeasible, revise the question or conduct a bounded feasibility study. Do not weaken protections or invent optimistic assumptions.

## Responsible AI policy

### Local-first rule

Default to local processing. Do not send sensitive, unpublished, confidential, personal, proprietary, controlled, or security-relevant information to an external AI system without:

- explicit authorization;
- a named approved service and account;
- a defined minimum data scope;
- contract, retention, training-use, location, and access review;
- applicable publisher, funder, institutional, and participant permission.

The bundled scripts make no network, model, image, or external-service calls and read no environment credentials.

### Human accountability

An accountable human must:

- own the question, candidate set, and final scientific decisions;
- verify every citation, identifier, quotation, and source-to-claim link;
- verify calculations and scientific plausibility;
- inspect omitted rivals and boundary conditions;
- review ethics, safety, privacy, dual-use, and regulatory implications;
- disclose AI assistance where policy requires;
- retain or delete records under the controlling policy.

AI output is not evidence and cannot grant approval.

### Known AI risks

NIST AI 600-1 identifies generative-AI risks including confabulation, data privacy, harmful bias/homogenization, information integrity, human–AI configuration, and dangerous recommendations. Mitigate by:

- independent human ideation before AI expansion;
- generating rivals from different disciplinary perspectives;
- separating source retrieval from claim synthesis;
- checking primary sources directly;
- recording prompts/tool versions when authorized and scientifically relevant;
- challenging convergent, polished, or overly confident output;
- using multiple human reviewers for high-consequence work.

Doshi and Hauser’s 2024 experiment found AI-assisted stories were more similar to one another even while some individual creativity measures improved. Do not generalize that one study to all scientific ideation; treat homogenization as a plausible risk and preserve independent candidate generation.

UNESCO’s AI ethics recommendation emphasizes human rights, privacy/data protection, responsibility/accountability, transparency, and human oversight. Ultimate responsibility remains human.

## Stop conditions

Stop and escalate when:

- authorization is absent or ambiguous;
- a required review is missing;
- data or material classification is unknown;
- harmful-use potential cannot be bounded;
- a request seeks operational harmful detail;
- patient-specific advice is requested;
- a regulatory or legal determination is needed;
- the proposed measurement cannot validly bear on the construct;
- qualified expertise is unavailable.

Record the block without copying sensitive details into a general-purpose artifact.

### `references/experimental_design_patterns.md`

# Design Patterns for Discriminating Tests

## Design starts from the prediction

For each test, link:

`candidate → mechanism → prediction → observable → operationalization → design → analysis → interpretation`

Choose the design that can distinguish candidates under realistic uncertainty. Do not select a design merely because it is familiar or available.

## NIH-aligned rigor questions

Where applicable, address:

- rigor of the prior research forming the scientific premise;
- unbiased and well-controlled design;
- relevant biological variables such as sex, age, weight, or health condition;
- authentication and validity of key biological/chemical resources;
- transparent methods, analysis, interpretation, and reporting.

Apply only the elements relevant to the science and explain omissions.

## Core design record

Every design should state:

- study system and target population;
- experimental/observational unit and analysis unit;
- sampling frame and recruitment/selection;
- interventions/exposures and comparator versions;
- allocation, randomization, concealment, and masking;
- outcomes, timing, measurement IDs, and quality control;
- positive, negative, vehicle/sham, procedural, or reference controls as applicable;
- inclusion, exclusion, attrition, and stopping;
- sample-size, precision, or information rationale;
- analysis IDs and estimands;
- safety, ethics, feasibility, data, and regulatory gates;
- replication, transport, and external-validation plan.

## Experimental designs

### Randomized intervention

Useful for causal contrasts when intervention, allocation, and ethics permit.

Check:

- allocation sequence and concealment;
- intervention versions, adherence, contamination, and co-interventions;
- masking of participants, providers, outcome assessors, and analysts where feasible;
- primary estimand and intercurrent events;
- intention-to-treat or other analysis population aligned to the estimand;
- harms, stopping, missing outcomes, and protocol deviations.

Randomization does not solve measurement bias, nonadherence, post-randomization selection, interference, or poor external validity.

### Factorial design

Useful for multiple interventions and interactions.

Check:

- scientific meaning and scale of interaction;
- power/precision for interactions, not only main effects;
- compatibility and safety of combined conditions;
- multiplicity and hierarchy;
- whether sparse combinations undermine interpretation.

### Within-unit or crossover design

Useful when effects are reversible and carryover can be controlled.

Check:

- period and sequence effects;
- washout rationale;
- time trends and learning;
- missing periods;
- whether the condition is stable and intervention reversible.

### Perturbation and rescue

Useful for mechanistic candidates when ethically and technically appropriate.

Check:

- perturbation specificity and off-target effects;
- manipulation check;
- rescue interpretation and overexpression artifacts;
- temporal order;
- orthogonal perturbations and measurements;
- relevant negative and positive controls.

A rescue can still be explained by compensatory or non-specific effects.

### Time-course

Useful when candidates predict different ordering or dynamics.

Check:

- sampling times justified by expected process;
- independent versus repeated units;
- baseline and pre-trend;
- measurement stability across time;
- multiple looks and timepoint multiplicity;
- lag, feedback, and reverse causation.

## Observational designs

### Cross-sectional

Can estimate prevalence and associations at a defined time. It usually cannot establish temporal direction. Explicitly consider selection, reverse causation, survival/prevalence bias, and common-method measurement.

### Cohort/longitudinal

Can establish measured temporal ordering and incidence. It does not eliminate confounding.

Check:

- time zero and eligibility;
- exposure updates and time-varying confounding;
- loss to follow-up and informative censoring;
- competing events;
- immortal-time and delayed-entry risks;
- outcome ascertainment changes.

### Case-control

Efficient for some rare outcomes.

Check:

- source population and control sampling;
- matching implications;
- exposure measurement and recall;
- selection mechanisms;
- correct effect measure and sampling analysis.

### Natural/quasi-experimental

Can strengthen causal identification when an assignment mechanism or discontinuity is credible.

Check:

- assignment mechanism and manipulation;
- continuity, parallel trends, exclusion, or instrument assumptions as applicable;
- anticipation and spillovers;
- bandwidth/window choices;
- placebo/negative-control tests;
- sensitivity to specification and clustering.

The design label alone does not establish identification.

## Computational and theoretical designs

### Simulation

Use to test implications of assumptions, estimator behavior, or model dynamics.

Record:

- data-generating process and parameter ranges;
- rationale for scenarios;
- seeds and software versions;
- performance targets and uncertainty;
- failure cases and sensitivity;
- separation between simulated truth and empirical validity.

Simulation can show consequences within a model, not that the model describes nature.

### Predictive model evaluation

Separate prediction from causation.

Check:

- target population, outcome, time origin, and horizon;
- leakage and preprocessing;
- train/tune/test independence;
- calibration and discrimination;
- uncertainty and subgroup performance;
- temporal/geographic/external validation;
- dataset shift and update policy.

### Secondary-data analysis

Record provenance, data-generating process, inclusion, missingness, transformations, version, and prior analysis exposure. Avoid using the same data to generate and confirm a hypothesis without transparent separation or independent validation.

## Controls

### Positive control

A condition expected to produce a known response. It checks whether the system and measurement can detect a relevant effect.

### Procedural control

Matches handling, timing, delivery, or processing without the target active component.

### Negative control

Should not operate through the target mechanism but should share relevant bias pathways. State assumptions and failure interpretation.

### Null comparator

A comparator representing no intervention or no difference may be useful, but it is not equivalent to a negative control and may not isolate placebo, handling, expectancy, or background trends.

## Measurement validity

Before collecting target outcomes:

- define constructs and proxies;
- verify instrument validity in the target context;
- assess reliability/repeatability;
- calibrate and authenticate resources;
- prespecify detection limits and quality failures;
- plan masking and standardized acquisition;
- define missing/invalid values;
- test cross-site, cross-device, cross-group, or longitudinal comparability where relevant.

A precise measure can be precisely wrong. Technical replicates do not replace independent biological, participant, site, or experimental units.

## Sample size and precision

Do not use universal minima.

Base planning on:

- primary estimand and effect/precision target;
- expected variability and dependence;
- allocation ratio;
- attrition/missingness;
- multiplicity or sequential design;
- model complexity;
- feasibility and ethical burden;
- uncertainty in planning values.

Report assumptions and sensitivity to them. Pilot data may be too unstable for definitive effect-size planning; use external evidence, conservative ranges, or precision-based goals where appropriate.

## Multiplicity

Inventory:

- candidate hypotheses;
- outcomes and timepoints;
- subgroups and interactions;
- model specifications and transformations;
- interim looks and stopping;
- repeated datasets or cohorts.

Prespecify a strategy appropriate to the inferential goal, such as:

- family-wise error control;
- false-discovery-rate control;
- hierarchical/gatekeeping testing;
- multilevel estimation;
- clearly labeled exploratory analysis without confirmatory claims.

Do not report only favorable analyses. Threshold crossing is not a quality score or probability that a candidate is true.

## Missing data and deviations

Define:

- missingness by variable, time, and group;
- reasons and data-collection process;
- primary handling;
- assumptions;
- sensitivity analyses;
- protocol and analysis deviations.

Complete-case analysis is not automatically unbiased. Record deviations without overwriting the original plan.

## Replication and open materials

Following the National Academies terminology:

- reproducibility uses the same data/code/conditions;
- replicability collects new data to address the same question.

Plan:

- code, environment, seeds, and workflow capture;
- provenance and versioning;
- shareable materials and justified restrictions;
- independent replication;
- boundary-condition and transport tests;
- reporting of null and contrary results.

Open sharing remains subject to consent, privacy, community governance, intellectual property, biosecurity, and other controls.

## Intervention reporting

For randomized intervention work:

- use SPIRIT 2025 and its explanation/elaboration for protocol completeness;
- use CONSORT 2025 and its explanation/elaboration for result reporting;
- include trial registration, protocol and statistical-analysis-plan access, outcomes, harms, intervention/comparator details, analysis populations, missing data, and important changes;
- use applicable extensions.

These are reporting guidelines. They do not replace ethics review, trial registration rules, statistical expertise, or regulatory requirements.

### `references/hypothesis_quality_criteria.md`

# Human Review Criteria for Candidate Hypotheses

## No automatic quality score

These criteria structure expert review. Do not sum them, assign weights, calculate a “quality score,” rank candidates automatically, or select a winner. Trade-offs and domain assumptions are not commensurable numbers.

For each criterion record:

- evidence or rationale;
- uncertainty and missing information;
- source IDs;
- reviewer role and date;
- revision or test needed.

## Question-level review

### Feasibility

- Are required data, samples, methods, expertise, time, and resources available?
- Is the unit of analysis attainable without pseudoreplication?
- Can the needed precision or information be achieved?
- Are approvals and governance pathways realistically available?
- Would a pilot answer feasibility rather than the scientific hypothesis?

### Interest and relevance

- Which scientific, stakeholder, policy, or practical decision could the answer inform?
- Were affected groups or domain experts involved where appropriate?
- Is the burden of the work proportionate to its expected informational value?

### Novelty

Treat novelty as a separate evidence claim:

- What databases, indexes, registries, patents, repositories, and grey literature were searched?
- What queries, dates, languages, and screening limits were used?
- Was prior work examined for conceptually equivalent terminology?
- Did a domain expert assess near neighbors and historical literature?

Use “not located within the documented search boundary” when that is all the evidence supports. Absence from a quick search is not evidence of novelty.

### Ethics

- Are human, animal, environmental, privacy, community, biosafety, dual-use, and regulatory implications assessed?
- Is there a less burdensome way to answer the question?
- Are harms, benefits, fairness, consent, and stewardship addressed?
- Are required reviews complete before work begins?

FINER—Feasible, Interesting, Novel, Ethical, Relevant—is a mnemonic for refining a question, not a pass/fail instrument. The earliest source located in this refresh is the first edition of *Designing Clinical Research* (Hulley and Cummings, 1988); later editions and current methodological articles present the mnemonic. The dated search did not establish that the 1988 edition was the first printed use, so do not claim coinage without checking the primary text.

## Hypothesis-level review

### Clarity

- Is the statement a candidate proposition rather than an observation or question?
- Are population/system, conditions, variables, direction, and timeframe explicit?
- Is the mechanism separate from the hypothesis statement?
- Are undefined terms and escape clauses removed?

### Testability

- Are observables and measurements available?
- Does the candidate generate at least one prospective prediction?
- Can a feasible design bear on the prediction?
- Are assumptions needed to connect result to candidate stated?

### Falsifiability and vulnerability

- What result would be incompatible under the stated assumptions?
- Could the candidate explain every possible outcome after the fact?
- Are indeterminate outcomes acknowledged?
- Does the proposed test risk only “confirming” the preferred candidate?

A null result can be uninformative because of low precision, failed manipulation, insensitive measurement, missingness, or assumption failure. Record these possibilities before calling a result falsifying.

### Discriminability

- Which rival predicts a different observable pattern?
- Is the difference larger than expected measurement uncertainty?
- Can the test distinguish mixed mechanisms?
- Are positive, procedural, and negative controls informative?
- What result supports neither candidate?

### Mechanistic adequacy

- Does the mechanism specify entities, activities, ordering, and context?
- Does it respect established constraints or explicitly identify where it departs?
- Are intermediate steps measurable?
- Could a simpler bias or measurement explanation produce the observation?

Mechanistic detail is not evidence. A more elaborate story can be less testable.

### Boundary conditions and transport

- Where, when, and for whom should the candidate apply?
- What exposure/intervention versions matter?
- What effect modifiers or contextual dependencies are plausible?
- Which populations, species, platforms, or scales are outside scope?
- What independent replication or external-validation test is planned?

### Assumption transparency

Separate:

- scientific assumptions;
- measurement assumptions;
- design/identification assumptions;
- statistical/model assumptions;
- implementation assumptions.

State which assumptions are testable, partially diagnosable, or fundamentally untestable with available data.

### Evidence alignment

For every source:

- identify the exact claim it bears on;
- distinguish direct from indirect or analogous evidence;
- note design, population/system, and limitations;
- include challenging and null evidence;
- avoid venue prestige, citation count, or author reputation as a substitute for appraisal.

### Uncertainty

- Are direction, magnitude, and interval uncertainty separated?
- Is model or structural uncertainty acknowledged?
- Is measurement uncertainty propagated or discussed?
- Are unknown alternatives and residual confounding visible?
- Are conclusions calibrated to the evidence?

## Prediction-level review

A prediction should identify:

- prediction ID and parent candidate;
- conditions and boundary conditions;
- observable and measurement ID;
- expected pattern, direction, magnitude/range if justified, and timing;
- rival and rival-expected pattern;
- falsifier/incompatible result;
- indeterminate outcome;
- linked analysis ID;
- assumptions and uncertainty.

Do not invent numerical effect sizes merely to appear specific. If magnitude is unknown, prespecify the direction, smallest effect of scientific interest, precision target, or a range of plausible values with rationale.

## Operationalization review

For each construct ask:

- Does the variable actually represent the construct?
- Is the instrument validated in the target context?
- Are reliability, calibration, detection limits, and quality control addressed?
- Are timing and aggregation aligned with the mechanism?
- Are cut points prespecified and justified?
- Are missingness and measurement error mechanisms considered?
- Is comparability across groups, time, sites, species, or devices established?
- Could the measurement itself be affected by exposure, outcome, or selection?

## Causal-claim review

Require:

- a well-defined intervention/exposure contrast;
- causal estimand;
- target population and horizon;
- design/target-trial analogue;
- identification assumptions;
- confounding, selection, collider, measurement, and reverse-causation assessment;
- positivity/overlap and interference considerations where applicable;
- sensitivity analyses and negative controls where scientifically defensible.

Predictive performance does not identify a causal effect. Adjustment does not guarantee exchangeability. Conditioning on a mediator or collider can introduce bias.

## Analysis-plan review

Check:

- unit and dependence structure;
- sample-size/precision rationale;
- exclusions and stopping;
- outcome and analysis populations;
- transformations and model specification;
- effect/summary measures and uncertainty;
- missing data and intercurrent events;
- multiplicity across hypotheses, outcomes, subgroups, models, and looks;
- assumptions and diagnostics;
- robustness and sensitivity analyses;
- confirmatory/exploratory labels;
- deviation-reporting process.

## Decision record

End human review with one of:

- `revise_before_test`;
- `ready_for_preregistration_review`;
- `blocked_by_safety_or_ethics_gate`;
- `blocked_by_measurement_or_feasibility`;
- `retain_as_exploratory_candidate`;
- `requires_specialist_review`.

These are workflow states, not scientific truth judgments and not outputs of a score.

### `references/literature_search_strategies.md`

# Evidence Search and Source Traceability

## Scope

This workflow supports hypothesis formulation. It is not automatically a systematic review, evidence-grade, patentability search, regulatory determination, or proof of novelty.

## Data and confidentiality gate

Before searching:

- remove confidential identifiers, unpublished results, proprietary sequences, exact vulnerabilities, and controlled operational details from queries;
- confirm that external search is authorized;
- translate sensitive observations into the minimum non-sensitive concepts needed;
- use approved local or institutional search tools when policy requires;
- record what was withheld and how that limits the search.

Do not send unpublished or sensitive data to an external search engine, AI service, citation service, or model without explicit authorization.

## Frame the search

Separate search objectives:

1. **Phenomenon:** Has the observation or a close analogue been reported?
2. **Mechanism:** Which processes could explain it?
3. **Rivals:** Which alternative mechanisms, artifacts, or biases are documented?
4. **Measurement:** How have the constructs been operationalized and validated?
5. **Design:** Which tests discriminate the candidates?
6. **Contrary evidence:** What findings challenge each candidate?
7. **Safety and governance:** Which ethical, biosafety, dual-use, data, or regulatory rules apply?
8. **Priority/novelty:** What prior work, registrations, preprints, patents, and grey literature address the same claim?

Use separate queries so a mechanism search is not mistaken for a novelty search.

## Question structures

Choose a structure matched to the question:

- PICO/PICOT: population, intervention, comparator, outcome, optional time;
- PECO: population, exposure, comparator, outcome;
- diagnostic: population, index test, reference standard, target condition;
- prognostic: population, prognostic factor, outcome, time;
- qualitative: population/sample, phenomenon, context;
- mechanistic: system, perturbation/condition, mediator/process, observable outcome;
- computational/theoretical: model class, assumptions, parameter regime, predicted observable.

Cochrane uses PICO for intervention-effect review questions and distinguishes review PICO, PICO for each synthesis, and PICO of included studies. Do not force PICO onto every domain.

## Source priority

Prefer the source closest to the claim:

1. law, regulation, official policy, or current institutional guidance for governance claims;
2. original paper, protocol, dataset, standard, or methods source for primary claims;
3. current reporting guideline and explanation/elaboration for reporting expectations;
4. systematic review or consensus report for landscape orientation;
5. narrative review for terminology and citation mining;
6. preprint or conference abstract, clearly labeled, for recent unreviewed work;
7. secondary webpages only when they point to a primary source or document current implementation.

Authority does not replace critical appraisal. A primary study may be weak, and a current official policy may be jurisdiction-specific.

## Search sequence

### 1. Broad orientation

- Search the phenomenon and field terminology.
- Locate one or more current reviews or consensus documents.
- Extract synonyms, controlled vocabulary, candidate mechanisms, and landmark sources.

### 2. Primary evidence

- Search each candidate mechanism separately.
- Search the original observation and closest analogues.
- Search prospective, experimental, longitudinal, and replication evidence where relevant.
- Search measurement-validation papers for each operationalization.

### 3. Rival and falsification search

For every candidate, run terms such as:

- alternative explanation;
- confounding;
- selection bias;
- collider bias;
- reverse causation;
- measurement error/artifact;
- negative control;
- failed replication;
- null or contradictory result;
- boundary condition/effect modification.

Record whether a source challenges the mechanism, the measurement, the design, or only its generalizability.

### 4. Foundational and historical search

Use backward citation tracing from methods and review papers. Search original titles, authors, books, standards, and DOI/PMID records. Recency is not a proxy for relevance.

### 5. Forward citation and registration search

Use citation indexes, trial registries, preregistration repositories, preprint servers, data/code repositories, and correction/retraction records as appropriate.

### 6. Policy search

Use current official sites and record:

- jurisdiction and applicability;
- effective or revision date;
- superseded documents;
- local implementation requirements;
- date checked.

For high-consequence work, a search result is not legal, regulatory, ethics, biosafety, or dual-use clearance.

## Search documentation

Complete `assets/search_boundary_template.json`. At minimum include:

- `search_boundary_id`;
- `searched_on`;
- purpose;
- databases/indexes;
- exact queries or reproducible query descriptions;
- date/language/source-type limits;
- inclusion and exclusion scope;
- stop rule or last result screened;
- known access and coverage limitations;
- novelty status.

Use `novelty_status: not_assessed` unless a qualified human has reviewed a fit-for-purpose search. Even a comprehensive search supports only a bounded statement.

## Evidence ledger

Complete `assets/evidence_ledger_template.csv` with one row per source:

- stable source ID;
- linked claim IDs;
- title and author/organization;
- publication date;
- source type and identifier;
- canonical HTTPS URL;
- access date;
- relation: supportive, challenging, contextual, method, safety, or mixed;
- design/document type;
- limitations and notes.

The audit validates structure and links only:

```bash
python3 scripts/audit_evidence_ledger.py \
  local-evidence-ledger.csv \
  local-search-boundary.json \
  --record local-hypothesis-record.json
```

It does not visit URLs, verify existence, appraise evidence, or decide whether a citation supports a claim.

## Claim-to-source notes

For each consequential claim, record:

- the exact source location (section, table, figure, page, or quoted sentence);
- whether the evidence is direct, indirect, analogous, or contradictory;
- study design and target population/system;
- magnitude and uncertainty actually reported;
- key limitations and conflicts;
- applicability to the candidate.

Verify every identifier and claim against the source. Do not rely on search snippets or AI-generated citations.

## Search stopping

Use a documented stop rule, such as:

- all prespecified databases searched;
- a fixed result depth screened per query;
- forward/backward citation tracing completed for named seed sources;
- predefined date and language boundary reached;
- saturation documented for terminology or mechanisms.

Do not stop merely because:

- preferred evidence was found;
- new results seem repetitive;
- a citation count is high;
- a source appears in a prestigious venue.

## Reporting bounded conclusions

Use:

> Searches were conducted on YYYY-MM-DD in [indexes] using [queries/strategy]. Within the documented date, language, access, and screening limits, we located [scope]. This does not establish universal absence, priority, or novelty.

For gaps:

> No directly matching source was located within the documented search boundary. Related work was found on [near neighbors]. A broader specialist search is required before making a novelty claim.

## Common failures

- Treating impact factor or citation count as study validity
- Searching only for support
- Using only one database
- Ignoring terminology changes or historical work
- Citing a review for a claim that should cite the primary study
- Treating preprints as peer-reviewed
- Omitting corrections, retractions, or protocol/registration records
- Searching confidential text verbatim
- Claiming an exhaustive search without a reproducible protocol
- Conflating “not found” with “does not exist”

### `references/preregistration_and_open_science.md`

# Preregistration, Registered Reports, and Open Science

## Purpose

Preregistration records a time-stamped plan before the relevant data are collected or analyzed. Its main value is making planned and data-dependent work distinguishable.

Preregistration does not:

- guarantee a valid design or analysis;
- prevent all researcher degrees of freedom;
- make a hypothesis true;
- forbid exploration or justified adaptation;
- replace ethics, safety, data, or regulatory review;
- require public release of restricted information.

## What to preregister

### Administrative

- title and project ID;
- accountable owner and roles;
- registration date and repository;
- study status and prior access to relevant data;
- conflicts, funding, and sponsor roles.

### Question and candidates

- observation and provenance;
- research question and claim type;
- candidate hypotheses and mechanisms;
- rivals and alternative explanations;
- causal estimands where applicable;
- boundary conditions and uncertainty.

### Predictions and controls

- prediction IDs and parent candidates;
- conditions, measurements, expected patterns, and timing;
- falsifiers and indeterminate outcomes;
- discriminating expectations for rivals;
- null hypotheses;
- positive, procedural, and negative controls.

### Design

- population/system and sampling;
- experimental and analysis units;
- allocation, randomization, concealment, and masking;
- interventions/exposures and comparators;
- inclusion, exclusion, attrition, and stopping;
- sample-size or precision rationale;
- outcomes and measurement timing;
- ethics, safety, data, and regulatory status.

### Analysis

- analysis populations;
- transformations and data exclusions;
- models, contrasts, estimators, and effect/summary measures;
- uncertainty intervals or other inferential summaries;
- missing-data and intercurrent-event handling;
- multiplicity;
- assumptions and diagnostics;
- sensitivity and robustness analyses;
- rules for interpreting support, challenge, and indeterminacy.

### Transparency

- data, code, materials, and metadata plans;
- restrictions and controlled-access process;
- software/environment versions;
- AI/tool use;
- deviation log and reporting plan.

## Timing and prior access

State what had already occurred:

- no data collected;
- data collected but target outcomes unseen;
- data available but analyst blinded;
- summary statistics viewed;
- exploratory analysis already performed;
- existing dataset reused.

When data have already informed the plan, label the work transparently and use independent data, a held-out set, or a new replication for confirmatory testing where feasible.

## Confirmatory versus exploratory

### Confirmatory

- planned before checking the target result;
- tied to specified outcomes and analyses;
- reported whether favorable, unfavorable, or null.

### Exploratory

- generated after or while viewing data;
- useful for discovery;
- labeled as data-dependent;
- treated as a source of future predictions.

Do not call exploratory work “post hoc confirmation.”

## HARKing

Kerr defined HARKing as presenting a post hoc hypothesis as if it were a priori. Prevent it by:

- preserving dated versions;
- separating planned and unplanned analyses;
- reporting all prespecified outcomes and tests;
- documenting when each candidate was generated;
- not rewriting unexpected results as predictions;
- seeking independent replication.

## Deviations

Preregistration is a plan, not a prison. For every material deviation record:

- date;
- affected section and IDs;
- original plan;
- change;
- reason;
- who made the decision;
- whether the target result was known;
- likely effect on bias or interpretation;
- whether the original analysis is still reported.

Do not silently replace the registration. Preserve the original and append amendments.

## Registered Reports

Registered Reports add journal peer review before results are known:

1. Stage 1 protocol submission;
2. review of question, methods, and analysis;
3. in-principle acceptance under the journal’s conditions;
4. study conduct;
5. Stage 2 review focused on adherence, justified deviations, and interpretation.

Check the current journal policy. In-principle acceptance is not ethics approval, funding, regulatory authorization, or assurance of a favorable result.

## Intervention trials

For randomized intervention hypotheses:

- use current registration requirements for the applicable jurisdiction, funder, and venue;
- use SPIRIT 2025 for protocol reporting;
- align objectives, estimands, outcomes, harms, intervention details, statistical methods, and data sharing;
- use CONSORT 2025 for completed-trial reporting;
- report important changes, including non-prespecified outcomes or analyses.

The preregistration scaffold in this skill is generic and is not a trial-registry submission, SPIRIT checklist, protocol, statistical analysis plan, or regulatory document.

## Reproducibility and replicability

Use the National Academies definitions:

- **reproducibility:** obtaining consistent computational results with the same data, code, methods, and analysis conditions;
- **replicability:** obtaining consistent results in a new study addressing the same question with new data.

Plan for:

- stable identifiers and version control;
- code and environment capture;
- provenance and decision logs;
- independent replication;
- exact and conceptual replication;
- boundary-condition and transport tests;
- publication of null and challenging results.

Non-replication does not automatically imply misconduct or that the original study was invalid. Differences can reveal heterogeneity, measurement limitations, context, or sampling variation.

## Open-science limits

“Open” does not override:

- participant consent and privacy;
- Indigenous or community data governance;
- contractual or intellectual-property restrictions;
- export controls;
- biosafety and dual-use review;
- endangered-species or sensitive-location protections;
- security-sensitive vulnerabilities.

Share the maximum responsibly permitted, not the maximum technically possible. Use metadata, synthetic examples, controlled access, or redacted protocols when full release is unsafe.

## Scaffold generation

Generate a local draft only after the hypothesis record validates:

```bash
python3 scripts/generate_preregistration_scaffold.py \
  local-hypothesis-record.json \
  -o local-preregistration.md
```

The result:

- is marked as an unregistered draft;
- includes every candidate without ranking;
- carries unresolved placeholders;
- requires human review and repository-specific completion;
- does not submit, register, upload, or transmit anything.

### `references/security_validation.md`

# Security Validation Record

Validation date: **2026-07-23** (local project date).

## Baseline

The repository `SECURITY.md` section recorded **10 findings** with maximum severity **CRITICAL**:

- cross-file environment-variable/network exfiltration;
- a multi-file collection/transmission chain;
- environment harvesting in both schematic scripts;
- credential transmission and local `.env` loading;
- subprocess delegation and full-environment propagation;
- fabricated or unverified model identifiers;
- unpinned external dependencies.

The affected files were:

- deleted: scripts/generate_schematic.py;
- deleted: scripts/generate_schematic_ai.py;
- the former credential and mandatory-figure instructions in `SKILL.md`.

## Remediation

- Deleted both external schematic scripts and all former LaTeX/figure assets.
- Removed credential declarations, environment access, `.env` loading, subprocesses, HTTP requests, external models, image generation, mandatory figures, and cross-skill behavior.
- Replaced the workflow with bounded deterministic local JSON/CSV/Markdown validators and a preregistration scaffold generator.
- Added strict duplicate-key/header detection, size/row/cell/list limits, symlink and URL-path rejection, private atomic outputs, and no implicit overwrite.
- Added AST tests rejecting network libraries, subprocesses, executable serialization, dynamic code execution, and environment credential access.
- Added local-first confidentiality, source verification, human accountability, ethics, biosafety, dual-use, data, clinical-scope, and regulatory gates.
- Tools report declarations and cross-links only; they do not score or select hypotheses.

## Validation results

- Agent Skills reference validator: **PASS**
- Dependency-free CLI help checks: **PASS** for all 7 public CLIs
- Synthetic standard-library tests: **27 passed**
- Explicit AST parse with bytecode disabled: **8 scripts parsed**
- Bytecode artifacts: **0**
- IDE lints: **0**
- Documented local-path link test: **PASS**
- Authoritative-source link extraction: **36/36 reachable, 0 errors**
- Direct behavioral security scan: **SAFE, 0 findings**
- Pull-request gate with `--fail-on HIGH`: **PASS**
  - CRITICAL: 0
  - HIGH: 0
  - LOW: 2

## Residual LOW findings

The LLM-assisted pull-request scan reported:

1. **Missing `allowed-tools` declaration** — informational. The Agent Skills specification does not require this optional field. The compatibility declaration and body constrain bundled tools to bounded local standard-library processing with no network, models, images, credentials, or environment access.
2. **Missing referenced files** — analyzer false positive. It invented paths under `templates/` and mismatched existing `assets/` and `references/` files. The deterministic local-path test resolved every documented bundled path and passed. No script implements network fallback or substitute retrieval.

Neither LOW finding permits data transmission, credential access, scientific scoring, or automatic hypothesis selection. No CRITICAL or HIGH issue remains.

## Reproduction

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s tests/hypothesis-generation -p "test_*.py" -v

uv run skills-ref validate skills/hypothesis-generation

uv run skill-scanner scan skills/hypothesis-generation --use-behavioral

uv run python scan_pr_skills.py \
  --fail-on HIGH \
  --output /tmp/hypothesis-generation-pr-scan.md \
  skills/hypothesis-generation
```

The repository-level `SECURITY.md` is intentionally not edited in this scoped refresh; its generated snapshot updates through the repository’s normal scan process.

### `references/source_ledger.md`

# Dated Source Ledger

Verification and research cutoff: **2026-07-23**.

Machine-readable ledger: `assets/source_ledger.csv`.

## Search boundary

Research used `parallel-cli` search against official or primary domains with focused queries for:

- NIH rigor, reproducibility, and the 2026 replication initiative;
- Cochrane PICO and the original well-built clinical-question article;
- FINER’s attributed historical source and current interpretation;
- Platt’s original strong-inference essay;
- COS/OSF preregistration and Registered Reports;
- SPIRIT 2025 and CONSORT 2025;
- causal questions, counterfactuals, estimands, and bias;
- negative controls, HARKing, multiplicity, reproducibility, and replication;
- NIST/UNESCO responsible AI and primary evidence on output homogenization;
- human, animal, biosafety, biosecurity, dual-use, data, and regulatory gates.

Searches prioritized official domains and primary publications. Full-text extraction or search excerpts were used to verify titles, dates, versions, and relevant passages. This was a targeted skill refresh, not a systematic review, patent search, or proof of scientific novelty.

## Core methodology sources

### Question formulation

- `SRC-COCHRANE-PICO` — current Cochrane Handbook Chapter 2. PICO is used for intervention-effect review questions, with objectives defined in advance and stakeholder input where appropriate.
- `SRC-PICO-ORIGINAL` — Richardson et al., 1995, *The well-built clinical question*. Foundational four-part clinical-question article.
- `SRC-FINER-1988` — Hulley and Cummings, *Designing Clinical Research*, first edition metadata (1988). It is the earliest FINER-attributed source located in this refresh.
- `SRC-FINER-CURRENT` — Werner and Willis, 2023, current FINER interpretation.

**Historical limitation:** the available targeted search confirmed the 1988 book’s bibliographic metadata and later attribution but did not establish the exact first printed use or coinage of the FINER mnemonic. The skill therefore does not claim that provenance as proven.

### Multiple hypotheses and falsification

- `SRC-PLATT-1964` — John R. Platt, “Strong Inference,” *Science* 146:347–353, DOI `10.1126/science.146.3642.347`.
- `SRC-NEG-CONTROL` — Lipsitch, Tchetgen Tchetgen, and Cohen, 2010, negative controls for confounding and bias, DOI `10.1097/EDE.0b013e3181d61eeb`.
- `SRC-HARKING` — Kerr, 1998, HARKing, DOI `10.1207/s15327957pspr0203_4`.
- `SRC-ASA-PVALUE` — ASA statement: thresholds alone do not support scientific conclusions; p-values do not measure hypothesis truth or effect importance; full reporting is required.

### Rigor, reproducibility, and replication

- `SRC-NIH-RIGOR` — NIH guidance on scientific premise, rigorous design, relevant biological variables, authentication, and transparency.
- `SRC-NIH-REPLICATION` — NIH’s agency-wide replication and reproducibility initiative, page reviewed June 22, 2026.
- `SRC-NASEM-RR` — National Academies 2019 consensus report defining computational reproducibility and replicability with new data.
- `SRC-TOP` — Transparency and Openness Promotion guidelines.
- `SRC-NIH-DMS` — NIH Data Management and Sharing Policy.

Open practices remain subject to consent, privacy, community governance, intellectual property, export control, and security restrictions.

## Preregistration and intervention trials

- `SRC-COS-PREREG` — preregistration separates planned from unplanned work; transparent exploration remains valuable.
- `SRC-OSF-REG` — current OSF registration/preregistration implementation guidance.
- `SRC-COS-RR` — Registered Reports and results-blind protocol review.
- `SRC-SPIRIT-2025` — current 34-item randomized-trial protocol guideline; supersedes SPIRIT 2013.
- `SRC-CONSORT-2025` — current 30-item randomized-trial result-reporting guideline, including open science, harms, outcomes, intervention details, and important changes.

SPIRIT and CONSORT are reporting guidelines, not design-quality, ethics, regulatory, or efficacy certifications.

## Causal inference and estimands

- `SRC-WHATIF` — Hernán and Robins, *Causal Inference: What If*. The author page linked the latest revision found during verification.
- `SRC-ICH-E9R1` — ICH E9(R1), defining the estimand as the precise treatment-effect target and aligning planning, design, analysis, sensitivity analysis, and interpretation.

These sources ground the distinctions among target causal contrast, estimator, and estimate, and the explicit treatment of confounding, selection, collider, measurement, and intervention-definition assumptions.

## Responsible AI

- `SRC-NIST-GENAI` — NIST AI 600-1, covering confabulation, privacy, harmful bias/homogenization, information integrity, dangerous recommendations, and human–AI configuration.
- `SRC-UNESCO-AI` — human rights, privacy, accountability, transparency, diversity, and human oversight.
- `SRC-DOSHI-HAUSER` — Doshi and Hauser, 2024, DOI `10.1126/sciadv.adn5290`. In the studied story-writing task, AI-assisted outputs were more similar to one another while some individual creativity measures improved.

The primary homogenization result is task-specific. The skill treats idea homogenization as a plausible risk, not a universal measured effect across scientific domains.

## Ethics and oversight

### Humans

- `SRC-HHS-COMMON-RULE` — U.S. Common Rule/45 CFR 46 portal.
- `SRC-BELMONT` — respect for persons, beneficence, and justice.
- `SRC-HELSINKI` — World Medical Association Declaration of Helsinki, revised October 2024.

An authorized IRB/REC or equivalent must determine applicability; the skill does not self-declare exemption.

### Animals

- `SRC-OLAW-PHS` — PHS Policy and IACUC/Assurance requirements for covered work.
- `SRC-ARRIVE` — ARRIVE 2.0 reporting guidance.

### Biosafety and dual use

- `SRC-NIH-RSNA` — NIH Guidelines for research involving recombinant or synthetic nucleic acid molecules.
- `SRC-NIH-BIOSEC` — current NIH biosafety/biosecurity portal.
- `SRC-BMBL` — CDC/NIH BMBL sixth edition.
- `SRC-WHO-LIFE` — WHO Global Guidance Framework for the Responsible Use of the Life Sciences.

### U.S. dual-use transition status

At the verification date:

- `SRC-EO-14292` directed revision/replacement of the 2024 DURC/PEPP policy and pause/termination actions for covered dangerous gain-of-function research.
- `SRC-NIH-NOT-25-112` stated the Executive Order superseded NIH’s 2024 implementation and rescinded NOT-OD-25-061.
- `SRC-ASPR-DURC` still described the 2024 policy as awaiting revision or replacement and promised an update when the revised policy became available.

This status is time-sensitive. Recheck current federal, funder, award, institutional, and jurisdiction-specific rules before any related work. Do not use this ledger as clearance.

## Source-use rules

1. Verify each citation and identifier against the live primary source before publication or registration.
2. Recheck time-sensitive policy after the cutoff date.
3. Link every scientific claim to evidence in `assets/evidence_ledger_template.csv`.
4. Include challenging, null, and limitation evidence, not only support.
5. Do not infer novelty from this source ledger; it documents the skill refresh, not a user’s research topic.
6. Do not expose a sensitive research question in an external search query without authorization.

### `references/tool_reference.md`

# Local Tool Reference

## Runtime and safety model

All bundled CLIs:

- require Python 3.11+ standard library only;
- read explicit local JSON, CSV, or Markdown paths;
- reject URL-like paths, symlinks, wrong suffixes, oversized inputs, invalid UTF-8, and NUL bytes;
- cap inputs at 2 MiB, CSV data at 1,000 rows, cells/Markdown lines at 8,000 characters, and JSON collections at bounded sizes;
- reject duplicate JSON keys and require exact ordered CSV headers;
- make no network, model, image, subprocess, credential, or environment-variable calls;
- write only to an explicit existing local directory;
- refuse implicit overwrite unless `--force` is given;
- use private mode (`0600`) and atomic replacement for generated output.

Reports contain identifiers, counts, rule codes, and line numbers rather than copying scientific prose where practical.

## Exit codes

- `0`: input was structurally valid; warnings or human-review gaps may remain.
- `1`: input was parsed, but consistency or required-control errors were found.
- `2`: malformed, unsafe, missing, oversized, or wrong-type input.

No exit code means a hypothesis is true, novel, ethical, safe, feasible, supported, or selected.

## 1. Hypothesis schema validator

Asset: `assets/hypothesis_record_template.json`

```bash
python3 scripts/validate_hypothesis_schema.py local-record.json
python3 scripts/validate_hypothesis_schema.py \
  local-record.json -o local-validation.json
```

The exact top-level objects are:

- observation;
- research question;
- hypotheses;
- causal estimands;
- predictions;
- alternative explanations;
- null hypotheses;
- negative controls;
- operationalizations;
- analysis plan;
- evidence/search link;
- causal-bias risk register;
- ethics/feasibility gates;
- AI-use record.

All hypothesis statuses must be `candidate`. Causal questions require at least one estimand. Cross-links among candidate, prediction, rival, measurement, analysis, control, and source IDs are checked.

The validator does not read the evidence ledger, test measurements, appraise sources, or interpret results.

## 2. Operationalization and measurement checklist

Asset: `assets/operationalization_template.json`

```bash
python3 scripts/check_operationalization.py local-operationalization.json
```

Each measurement item records:

- construct, operational definition, population/system, unit/categories, timing, and method completion;
- variable role;
- validity source IDs and applicability review;
- reliability/repeatability;
- calibration/quality control;
- invariance/comparability;
- masking;
- missingness;
- threshold/cut-point status;
- limitations and human review.

`planned`, `unresolved`, and `pending` states are reported as gaps, not converted to scores. A checklist cannot establish measurement validity.

## 3. Prediction/rival matrix validator

Asset: `assets/prediction_rival_matrix_template.csv`

Exact header:

```text
prediction_id,hypothesis_id,rival_hypothesis_ids,conditions,observable,expected_if_focal,expected_if_rivals,falsifier,indeterminate_result,boundary_conditions,measurement_ids,negative_control_ids,analysis_ids,uncertainty
```

Use semicolons inside ID-list cells:

```bash
python3 scripts/validate_prediction_matrix.py local-matrix.csv
python3 scripts/validate_prediction_matrix.py \
  local-matrix.csv --record local-record.json
```

Checks include:

- unique prediction IDs;
- focal candidate not listed as its own rival;
- declared focal and rival expectations are not lexically identical;
- required falsifier, indeterminate result, boundary, measurement, control, analysis, and uncertainty fields;
- optional cross-links to the hypothesis record.

The validator cannot determine whether two predictions are scientifically distinguishable.

## 4. Causal-versus-associational Markdown lint

```bash
python3 scripts/lint_causal_claims.py local-draft.md
```

Use one claim per annotated line:

```markdown
[claim:associational] Exposure X was associated with outcome Y in the observed sample.

[claim:causal][estimand:E1][identification:observational_assumption_dependent][confounding:unresolved][selection:assessed][collider:assessed][reverse-causation:assessed] Under the stated assumptions, intervention X would reduce outcome Y.
```

Claim types:

- `causal`
- `associational`
- `descriptive`
- `predictive`
- `mechanistic`

Identification values:

- `randomized`
- `quasi_experimental`
- `observational_assumption_dependent`
- `mechanistic_experiment`
- `other_assumption_dependent`

Risk values:

- `assessed`
- `unresolved`
- `not_applicable`

The linter flags a bounded causal lexicon and annotation consistency. It is not a semantic classifier and will have false positives and false negatives.

## 5. Falsification and negative-control checklist

Asset: `assets/falsification_controls_template.json`

```bash
python3 scripts/check_falsification_controls.py local-controls.json
python3 scripts/check_falsification_controls.py \
  local-controls.json --record local-record.json
```

For each candidate it requires:

- assumptions and boundary conditions;
- a prediction-linked falsifier and assumption-failure checks;
- at least one discriminating test with focal, rival, and indeterminate outcomes;
- a linked null and interpretation limit;
- controls including at least one negative-control type;
- outcome paths for consistency, challenge, and neither/mixed;
- human-review status.

The checker does not validate that a negative control is biologically or causally appropriate.

## 6. Evidence ledger and search-boundary audit

Assets:

- `assets/evidence_ledger_template.csv`
- `assets/search_boundary_template.json`

Exact evidence-ledger header:

```text
source_id,claim_ids,title,authors_or_organization,publication_date,source_type,identifier,url,accessed_on,relation,study_design_or_document_type,limitations,notes
```

```bash
python3 scripts/audit_evidence_ledger.py \
  local-evidence.csv local-search-boundary.json

python3 scripts/audit_evidence_ledger.py \
  local-evidence.csv local-search-boundary.json \
  --record local-record.json
```

The audit checks:

- exact schema and date/HTTPS/identifier formats;
- unique source IDs;
- source-to-claim links;
- source-type and relation declarations;
- dated search boundary, queries, limits, stop rule, and novelty status;
- optional source, claim, and boundary links to a hypothesis record.

It deliberately performs no network access. It cannot verify that a URL exists, a source says what is claimed, evidence is complete, or an idea is novel.

Allowed novelty states:

- `not_assessed`
- `requires_specialist_review`
- `supported_by_documented_comprehensive_search`

The final state still requires a qualified human and supports only a bounded statement.

## 7. Preregistration scaffold generator

Asset: `assets/preregistration_scaffold_template.md`

```bash
python3 scripts/generate_preregistration_scaffold.py \
  local-record.json -o local-preregistration.md
```

The generator:

- first runs record validation;
- refuses unresolved ethics/safety/feasibility gates;
- renders all candidates and rivals without ranking;
- escapes inserted text for inert Markdown;
- marks the output as an unregistered draft;
- leaves repository-, design-, oversight-, and sign-off fields for humans.

It never uploads, registers, timestamps externally, or submits the result.

## Suggested local sequence

```bash
python3 scripts/validate_hypothesis_schema.py local-record.json
python3 scripts/check_operationalization.py local-operationalization.json
python3 scripts/validate_prediction_matrix.py \
  local-predictions.csv --record local-record.json
python3 scripts/check_falsification_controls.py \
  local-controls.json --record local-record.json
python3 scripts/audit_evidence_ledger.py \
  local-evidence.csv local-search-boundary.json --record local-record.json
python3 scripts/lint_causal_claims.py local-draft.md
python3 scripts/generate_preregistration_scaffold.py \
  local-record.json -o local-preregistration.md
```

Qualified human review remains mandatory after every command.

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared, dependency-free safety helpers for local hypothesis CLIs."""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Iterable

MAX_INPUT_BYTES = 2 * 1024 * 1024
MAX_ROWS = 1_000
MAX_CELL_CHARS = 8_000
MAX_TEXT_CHARS = 20_000
MAX_LIST_ITEMS = 500

IDENTIFIER_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._:-]{0,95}$")
URL_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
HTTPS_URL_RE = re.compile(r"^https://[^\s]+$", re.IGNORECASE)
PARTIAL_DATE_RE = re.compile(r"^\d{4}(?:-\d{2}(?:-\d{2})?)?$")


class ValidationError(ValueError):
    """A deterministic, user-correctable validation failure."""


def _duplicate_safe_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"JSON object contains duplicate key: {key}")
        result[key] = value
    return result


def _reject_url_like_path(raw_path: str | Path, context: str) -> None:
    if URL_SCHEME_RE.match(str(raw_path).strip()):
        raise ValidationError(f"{context} must be a local file path")


def safe_input_path(raw_path: str | Path, suffixes: Iterable[str]) -> Path:
    """Resolve a bounded regular local file and reject symlink inputs."""
    _reject_url_like_path(raw_path, "input")
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
    _reject_url_like_path(raw_path, "output")
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
    if any(len(line) > MAX_CELL_CHARS for line in text.splitlines()):
        raise ValidationError(
            f"Markdown contains a line longer than {MAX_CELL_CHARS} characters"
        )
    return text


def read_csv_records(
    raw_path: str | Path,
    *,
    fields: Iterable[str],
    max_rows: int = MAX_ROWS,
) -> list[dict[str, str]]:
    """Read strict UTF-8 CSV with an exact ordered header and bounded cells."""
    path = safe_input_path(raw_path, {".csv"})
    expected = tuple(fields)
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames
            if not headers:
                raise ValidationError(f"CSV has no header: {path}")
            normalized = tuple(header.strip() for header in headers)
            if any(not header for header in normalized):
                raise ValidationError("CSV headers must not be blank")
            if len(normalized) != len(set(normalized)):
                raise ValidationError("CSV headers must be unique")
            if normalized != expected:
                raise ValidationError(
                    "CSV header must exactly match: " + ",".join(expected)
                )
            reader.fieldnames = list(normalized)
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
    item_maximum: int = 1_000,
) -> list[str]:
    items = require_list(value, context, minimum=minimum, maximum=maximum)
    return [
        require_text(item, f"{context}[{index}]", maximum=item_maximum)
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


def require_partial_date(value: Any, context: str) -> str:
    text = require_text(value, context, maximum=10)
    if not PARTIAL_DATE_RE.fullmatch(text):
        raise ValidationError(f"{context} must be YYYY, YYYY-MM, or YYYY-MM-DD")
    try:
        if len(text) == 4:
            date(int(text), 1, 1)
        elif len(text) == 7:
            date.fromisoformat(f"{text}-01")
        else:
            date.fromisoformat(text)
    except ValueError as exc:
        raise ValidationError(f"{context} contains an invalid date") from exc
    return text


def require_https_url(value: Any, context: str) -> str:
    text = require_text(value, context, maximum=2_000)
    if not HTTPS_URL_RE.fullmatch(text):
        raise ValidationError(f"{context} must be an https URL")
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
    """Create a content-free finding safe for reports."""
    return {"code": code, "field": field}


def error_exit(exc: ValidationError) -> int:
    print(f"ERROR: {exc}", file=sys.stderr)
    return 2
```

### `scripts/audit_evidence_ledger.py`

```python
#!/usr/bin/env python3
"""Audit a local evidence ledger and dated search boundary without networking."""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_csv_records,
    read_json,
    require_enum,
    require_exact_keys,
    require_https_url,
    require_identifier,
    require_iso_date,
    require_object,
    require_partial_date,
    require_text,
    require_text_list,
    require_unique,
    split_identifiers,
    write_json_report,
)
from validate_hypothesis_schema import load_hypothesis_record, validate_record

FIELDS = (
    "source_id",
    "claim_ids",
    "title",
    "authors_or_organization",
    "publication_date",
    "source_type",
    "identifier",
    "url",
    "accessed_on",
    "relation",
    "study_design_or_document_type",
    "limitations",
    "notes",
)
SOURCE_TYPES = {
    "official_guidance",
    "regulation_policy",
    "reporting_guideline",
    "primary_research",
    "primary_method",
    "systematic_review",
    "consensus_report",
    "book",
    "dataset_or_registry",
    "preprint",
    "other",
}
RELATIONS = {"supportive", "challenging", "contextual", "method", "safety", "mixed"}
NOVELTY_STATES = {
    "not_assessed",
    "requires_specialist_review",
    "supported_by_documented_comprehensive_search",
}


def load_ledger(raw_path: str) -> list[dict[str, Any]]:
    rows = read_csv_records(raw_path, fields=FIELDS)
    parsed: list[dict[str, Any]] = []
    source_ids: list[str] = []
    for line_number, row in enumerate(rows, start=2):
        context = f"ledger row {line_number}"
        source_id = require_identifier(row["source_id"], f"{context}.source_id")
        source_ids.append(source_id)
        parsed.append(
            {
                "source_id": source_id,
                "claim_ids": split_identifiers(
                    row["claim_ids"], f"{context}.claim_ids"
                ),
                "title": require_text(
                    row["title"], f"{context}.title", minimum=5, maximum=2_000
                ),
                "authors_or_organization": require_text(
                    row["authors_or_organization"],
                    f"{context}.authors_or_organization",
                    minimum=2,
                    maximum=1_000,
                ),
                "publication_date": require_partial_date(
                    row["publication_date"], f"{context}.publication_date"
                ),
                "source_type": require_enum(
                    row["source_type"], SOURCE_TYPES, f"{context}.source_type"
                ),
                "identifier": require_text(
                    row["identifier"],
                    f"{context}.identifier",
                    minimum=3,
                    maximum=1_000,
                ),
                "url": require_https_url(row["url"], f"{context}.url"),
                "accessed_on": require_iso_date(
                    row["accessed_on"], f"{context}.accessed_on"
                ),
                "relation": require_enum(
                    row["relation"], RELATIONS, f"{context}.relation"
                ),
                "study_design_or_document_type": require_text(
                    row["study_design_or_document_type"],
                    f"{context}.study_design_or_document_type",
                    minimum=3,
                    maximum=1_000,
                ),
                "limitations": require_text(
                    row["limitations"],
                    f"{context}.limitations",
                    minimum=3,
                    maximum=2_000,
                ),
                "notes": require_text(
                    row["notes"],
                    f"{context}.notes",
                    allow_empty=True,
                    maximum=2_000,
                ),
            }
        )
    require_unique(source_ids, "evidence ledger")
    return parsed


def load_search_boundary(payload: Any) -> dict[str, Any]:
    root = require_object(payload, "search_boundary")
    fields = {
        "schema_version",
        "search_boundary_id",
        "searched_on",
        "searched_by",
        "purpose",
        "databases_or_indexes",
        "queries",
        "date_limits",
        "language_limits",
        "inclusion_scope",
        "exclusion_scope",
        "known_limitations",
        "last_result_screened_or_stop_rule",
        "novelty_status",
    }
    require_exact_keys(root, required=fields, context="search_boundary")
    return {
        "schema_version": require_enum(
            root["schema_version"], {"2.0"}, "search_boundary.schema_version"
        ),
        "search_boundary_id": require_identifier(
            root["search_boundary_id"], "search_boundary.search_boundary_id"
        ),
        "searched_on": require_iso_date(
            root["searched_on"], "search_boundary.searched_on"
        ),
        "searched_by": require_text(
            root["searched_by"], "search_boundary.searched_by", minimum=3
        ),
        "purpose": require_text(
            root["purpose"], "search_boundary.purpose", minimum=10
        ),
        "databases_or_indexes": require_text_list(
            root["databases_or_indexes"],
            "search_boundary.databases_or_indexes",
            minimum=1,
            maximum=100,
        ),
        "queries": require_text_list(
            root["queries"], "search_boundary.queries", minimum=1, maximum=200
        ),
        "date_limits": require_text(
            root["date_limits"], "search_boundary.date_limits", minimum=3
        ),
        "language_limits": require_text(
            root["language_limits"], "search_boundary.language_limits", minimum=3
        ),
        "inclusion_scope": require_text(
            root["inclusion_scope"], "search_boundary.inclusion_scope", minimum=10
        ),
        "exclusion_scope": require_text(
            root["exclusion_scope"], "search_boundary.exclusion_scope", minimum=10
        ),
        "known_limitations": require_text_list(
            root["known_limitations"],
            "search_boundary.known_limitations",
            minimum=1,
            maximum=100,
        ),
        "last_result_screened_or_stop_rule": require_text(
            root["last_result_screened_or_stop_rule"],
            "search_boundary.last_result_screened_or_stop_rule",
            minimum=10,
        ),
        "novelty_status": require_enum(
            root["novelty_status"],
            NOVELTY_STATES,
            "search_boundary.novelty_status",
        ),
    }


def _record_claim_ids(record: dict[str, Any]) -> set[str]:
    identifiers = {"OBS1", record["project_id"]}
    identifiers.update(item["hypothesis_id"] for item in record["hypotheses"])
    identifiers.update(item["estimand_id"] for item in record["causal_estimands"])
    identifiers.update(item["prediction_id"] for item in record["predictions"])
    identifiers.update(
        item["alternative_id"] for item in record["alternative_explanations"]
    )
    identifiers.update(item["null_id"] for item in record["null_hypotheses"])
    identifiers.update(item["control_id"] for item in record["negative_controls"])
    identifiers.update(
        item["measurement_id"] for item in record["operationalizations"]
    )
    identifiers.update(
        item["analysis_id"] for item in record["analysis_plan"]["analyses"]
    )
    return identifiers


def audit(
    ledger: list[dict[str, Any]],
    boundary: dict[str, Any],
    record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    source_type_counts: Counter[str] = Counter()
    relation_counts: Counter[str] = Counter()
    ledger_source_ids = {row["source_id"] for row in ledger}
    linked_claim_ids: set[str] = set()

    searched_on = date.fromisoformat(boundary["searched_on"])
    for row in ledger:
        source_type_counts[row["source_type"]] += 1
        relation_counts[row["relation"]] += 1
        linked_claim_ids.update(row["claim_ids"])
        if date.fromisoformat(row["accessed_on"]) > searched_on:
            warnings.append(
                issue("SOURCE_ACCESSED_AFTER_SEARCH_BOUNDARY", row["source_id"])
            )

    if not relation_counts["challenging"]:
        warnings.append(issue("NO_CHALLENGING_SOURCE_DECLARED", "ledger"))
    if boundary["novelty_status"] == "supported_by_documented_comprehensive_search":
        warnings.append(
            issue("NOVELTY_STATUS_REQUIRES_QUALIFIED_HUMAN_REVIEW", "search_boundary")
        )

    record_cross_check = record is not None
    if record is not None:
        record_report = validate_record(record)
        if not record_report["valid"]:
            raise ValidationError(
                "optional hypothesis record must pass schema validation first"
            )
        if record["evidence"]["search_boundary_id"] != boundary["search_boundary_id"]:
            errors.append(
                issue("SEARCH_BOUNDARY_ID_MISMATCH", boundary["search_boundary_id"])
            )
        record_source_ids = set(record["evidence"]["source_ids"])
        for source_id in sorted(record_source_ids - ledger_source_ids):
            errors.append(issue("RECORD_SOURCE_MISSING_FROM_LEDGER", source_id))
        for source_id in sorted(ledger_source_ids - record_source_ids):
            warnings.append(issue("LEDGER_SOURCE_NOT_DECLARED_IN_RECORD", source_id))
        allowed_claim_ids = _record_claim_ids(record)
        for claim_id in sorted(linked_claim_ids - allowed_claim_ids):
            errors.append(issue("UNKNOWN_CLAIM_ID", claim_id))

    return {
        "schema_version": "2.0",
        "search_boundary_id": boundary["search_boundary_id"],
        "searched_on": boundary["searched_on"],
        "novelty_status": boundary["novelty_status"],
        "valid": not errors,
        "status": "INVALID_LEDGER" if errors else "VALID_FOR_HUMAN_SOURCE_REVIEW",
        "errors": errors,
        "warnings": warnings,
        "source_count": len(ledger),
        "source_type_counts": dict(sorted(source_type_counts.items())),
        "relation_counts": dict(sorted(relation_counts.items())),
        "source_ids": sorted(ledger_source_ids),
        "linked_claim_ids": sorted(linked_claim_ids),
        "record_cross_check_performed": record_cross_check,
        "notice": (
            "This local audit does not visit URLs, verify source existence or "
            "content, appraise evidence, establish novelty, or determine whether "
            "a source supports a claim. Verify every source and link manually."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a bounded local evidence CSV and search-boundary JSON without "
            "network access or scientific scoring."
        )
    )
    parser.add_argument("ledger", help="Local evidence ledger CSV")
    parser.add_argument("search_boundary", help="Local search-boundary JSON")
    parser.add_argument(
        "--record", help="Optional local hypothesis record JSON for cross-checks"
    )
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        record = (
            load_hypothesis_record(read_json(args.record)) if args.record else None
        )
        report = audit(
            load_ledger(args.ledger),
            load_search_boundary(read_json(args.search_boundary)),
            record,
        )
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/check_falsification_controls.py`

```python
#!/usr/bin/env python3
"""Audit falsifiers, discriminating tests, nulls, and controls without scoring."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_json,
    require_enum,
    require_exact_keys,
    require_identifier,
    require_list,
    require_object,
    require_text,
    require_text_list,
    require_unique,
    write_json_report,
)
from validate_hypothesis_schema import load_hypothesis_record, validate_record

CONTROL_TYPES = {
    "negative_exposure",
    "negative_outcome",
    "procedural_negative",
    "positive_control",
    "vehicle_or_sham",
    "other",
}
NEGATIVE_TYPES = {"negative_exposure", "negative_outcome", "procedural_negative"}


def _parse_falsifier(raw: Any, context: str) -> dict[str, Any]:
    value = require_object(raw, context)
    require_exact_keys(
        value,
        required={
            "prediction_id",
            "conditions",
            "observable",
            "incompatible_result",
            "assumption_failure_checks",
        },
        context=context,
    )
    return {
        "prediction_id": require_identifier(
            value["prediction_id"], f"{context}.prediction_id"
        ),
        "conditions": require_text(
            value["conditions"], f"{context}.conditions", minimum=10
        ),
        "observable": require_text(
            value["observable"], f"{context}.observable", minimum=5
        ),
        "incompatible_result": require_text(
            value["incompatible_result"],
            f"{context}.incompatible_result",
            minimum=10,
        ),
        "assumption_failure_checks": require_text_list(
            value["assumption_failure_checks"],
            f"{context}.assumption_failure_checks",
            minimum=1,
        ),
    }


def _parse_discriminating_tests(raw: Any, context: str) -> list[dict[str, str]]:
    values = require_list(raw, context, minimum=1, maximum=100)
    parsed: list[dict[str, str]] = []
    identifiers: list[str] = []
    fields = {
        "test_id",
        "rival_hypothesis_id",
        "focal_expected",
        "rival_expected",
        "indeterminate_result",
    }
    for index, raw_value in enumerate(values):
        item_context = f"{context}[{index}]"
        value = require_object(raw_value, item_context)
        require_exact_keys(value, required=fields, context=item_context)
        test_id = require_identifier(value["test_id"], f"{item_context}.test_id")
        identifiers.append(test_id)
        parsed.append(
            {
                "test_id": test_id,
                "rival_hypothesis_id": require_identifier(
                    value["rival_hypothesis_id"],
                    f"{item_context}.rival_hypothesis_id",
                ),
                "focal_expected": require_text(
                    value["focal_expected"],
                    f"{item_context}.focal_expected",
                    minimum=10,
                ),
                "rival_expected": require_text(
                    value["rival_expected"],
                    f"{item_context}.rival_expected",
                    minimum=10,
                ),
                "indeterminate_result": require_text(
                    value["indeterminate_result"],
                    f"{item_context}.indeterminate_result",
                    minimum=10,
                ),
            }
        )
    require_unique(identifiers, context)
    return parsed


def _parse_nulls(raw: Any, context: str) -> list[dict[str, str]]:
    values = require_list(raw, context, minimum=1, maximum=100)
    parsed: list[dict[str, str]] = []
    identifiers: list[str] = []
    fields = {"null_id", "statement", "analysis_id", "interpretation_limit"}
    for index, raw_value in enumerate(values):
        item_context = f"{context}[{index}]"
        value = require_object(raw_value, item_context)
        require_exact_keys(value, required=fields, context=item_context)
        null_id = require_identifier(value["null_id"], f"{item_context}.null_id")
        identifiers.append(null_id)
        parsed.append(
            {
                "null_id": null_id,
                "statement": require_text(
                    value["statement"], f"{item_context}.statement", minimum=10
                ),
                "analysis_id": require_identifier(
                    value["analysis_id"], f"{item_context}.analysis_id"
                ),
                "interpretation_limit": require_text(
                    value["interpretation_limit"],
                    f"{item_context}.interpretation_limit",
                    minimum=10,
                ),
            }
        )
    require_unique(identifiers, context)
    return parsed


def _parse_controls(raw: Any, context: str) -> list[dict[str, str]]:
    values = require_list(raw, context, minimum=1, maximum=100)
    parsed: list[dict[str, str]] = []
    identifiers: list[str] = []
    fields = {
        "control_id",
        "control_type",
        "rationale",
        "expected_result",
        "failure_implication",
    }
    for index, raw_value in enumerate(values):
        item_context = f"{context}[{index}]"
        value = require_object(raw_value, item_context)
        require_exact_keys(value, required=fields, context=item_context)
        control_id = require_identifier(
            value["control_id"], f"{item_context}.control_id"
        )
        identifiers.append(control_id)
        parsed.append(
            {
                "control_id": control_id,
                "control_type": require_enum(
                    value["control_type"],
                    CONTROL_TYPES,
                    f"{item_context}.control_type",
                ),
                "rationale": require_text(
                    value["rationale"], f"{item_context}.rationale", minimum=10
                ),
                "expected_result": require_text(
                    value["expected_result"],
                    f"{item_context}.expected_result",
                    minimum=5,
                ),
                "failure_implication": require_text(
                    value["failure_implication"],
                    f"{item_context}.failure_implication",
                    minimum=10,
                ),
            }
        )
    require_unique(identifiers, context)
    return parsed


def _parse_outcome_interpretation(raw: Any, context: str) -> dict[str, str]:
    value = require_object(raw, context)
    fields = {
        "consistent_with_candidate",
        "challenges_candidate",
        "supports_neither_or_mixed",
    }
    require_exact_keys(value, required=fields, context=context)
    return {
        field: require_text(value[field], f"{context}.{field}", minimum=10)
        for field in fields
    }


def load_checklist(payload: Any) -> dict[str, Any]:
    root = require_object(payload, "checklist")
    require_exact_keys(
        root,
        required={"schema_version", "checklist_id", "record_id", "hypotheses"},
        context="checklist",
    )
    raw_hypotheses = require_list(
        root["hypotheses"], "checklist.hypotheses", minimum=1, maximum=50
    )
    parsed_hypotheses: list[dict[str, Any]] = []
    hypothesis_ids: list[str] = []
    fields = {
        "hypothesis_id",
        "candidate_status",
        "assumptions",
        "boundary_conditions",
        "falsifier",
        "discriminating_tests",
        "nulls",
        "controls",
        "outcome_interpretation",
        "human_review_status",
    }
    for index, raw_hypothesis in enumerate(raw_hypotheses):
        context = f"checklist.hypotheses[{index}]"
        hypothesis = require_object(raw_hypothesis, context)
        require_exact_keys(hypothesis, required=fields, context=context)
        hypothesis_id = require_identifier(
            hypothesis["hypothesis_id"], f"{context}.hypothesis_id"
        )
        hypothesis_ids.append(hypothesis_id)
        parsed_hypotheses.append(
            {
                "hypothesis_id": hypothesis_id,
                "candidate_status": require_enum(
                    hypothesis["candidate_status"],
                    {"candidate"},
                    f"{context}.candidate_status",
                ),
                "assumptions": require_text_list(
                    hypothesis["assumptions"],
                    f"{context}.assumptions",
                    minimum=1,
                ),
                "boundary_conditions": require_text_list(
                    hypothesis["boundary_conditions"],
                    f"{context}.boundary_conditions",
                    minimum=1,
                ),
                "falsifier": _parse_falsifier(
                    hypothesis["falsifier"], f"{context}.falsifier"
                ),
                "discriminating_tests": _parse_discriminating_tests(
                    hypothesis["discriminating_tests"],
                    f"{context}.discriminating_tests",
                ),
                "nulls": _parse_nulls(
                    hypothesis["nulls"], f"{context}.nulls"
                ),
                "controls": _parse_controls(
                    hypothesis["controls"], f"{context}.controls"
                ),
                "outcome_interpretation": _parse_outcome_interpretation(
                    hypothesis["outcome_interpretation"],
                    f"{context}.outcome_interpretation",
                ),
                "human_review_status": require_enum(
                    hypothesis["human_review_status"],
                    {"pending", "complete", "specialist_required"},
                    f"{context}.human_review_status",
                ),
            }
        )
    require_unique(hypothesis_ids, "checklist.hypotheses")
    return {
        "schema_version": require_enum(
            root["schema_version"], {"2.0"}, "checklist.schema_version"
        ),
        "checklist_id": require_identifier(
            root["checklist_id"], "checklist.checklist_id"
        ),
        "record_id": require_identifier(root["record_id"], "checklist.record_id"),
        "hypotheses": parsed_hypotheses,
    }


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def audit(
    checklist: dict[str, Any], record: dict[str, Any] | None = None
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    review_counts: Counter[str] = Counter()
    test_ids: list[str] = []
    null_ids: list[str] = []

    record_ids: dict[str, set[str]] | None = None
    if record is not None:
        record_report = validate_record(record)
        if not record_report["valid"]:
            raise ValidationError(
                "optional hypothesis record must pass schema validation first"
            )
        record_ids = {
            "hypotheses": {
                item["hypothesis_id"] for item in record["hypotheses"]
            },
            "predictions": {
                item["prediction_id"] for item in record["predictions"]
            },
            "analyses": {
                item["analysis_id"] for item in record["analysis_plan"]["analyses"]
            },
            "controls": {
                item["control_id"] for item in record["negative_controls"]
            },
            "nulls": {item["null_id"] for item in record["null_hypotheses"]},
        }

    for hypothesis in checklist["hypotheses"]:
        hypothesis_id = hypothesis["hypothesis_id"]
        review_counts[hypothesis["human_review_status"]] += 1
        if hypothesis["human_review_status"] != "complete":
            warnings.append(issue("HUMAN_REVIEW_INCOMPLETE", hypothesis_id))

        falsifier = hypothesis["falsifier"]
        if record_ids is not None:
            if hypothesis_id not in record_ids["hypotheses"]:
                errors.append(issue("UNKNOWN_HYPOTHESIS_ID", hypothesis_id))
            if falsifier["prediction_id"] not in record_ids["predictions"]:
                errors.append(
                    issue("UNKNOWN_PREDICTION_ID", falsifier["prediction_id"])
                )

        for test in hypothesis["discriminating_tests"]:
            test_ids.append(test["test_id"])
            if test["rival_hypothesis_id"] == hypothesis_id:
                errors.append(issue("FOCAL_HYPOTHESIS_LISTED_AS_RIVAL", test["test_id"]))
            if _normalize(test["focal_expected"]) == _normalize(
                test["rival_expected"]
            ):
                errors.append(
                    issue("FOCAL_AND_RIVAL_EXPECTATIONS_IDENTICAL", test["test_id"])
                )
            if (
                record_ids is not None
                and test["rival_hypothesis_id"] not in record_ids["hypotheses"]
            ):
                errors.append(
                    issue("UNKNOWN_RIVAL_HYPOTHESIS_ID", test["test_id"])
                )

        for null in hypothesis["nulls"]:
            null_ids.append(null["null_id"])
            if record_ids is not None:
                if null["null_id"] not in record_ids["nulls"]:
                    errors.append(issue("UNKNOWN_NULL_ID", null["null_id"]))
                if null["analysis_id"] not in record_ids["analyses"]:
                    errors.append(
                        issue("UNKNOWN_ANALYSIS_ID", null["analysis_id"])
                    )

        negative_controls = [
            control
            for control in hypothesis["controls"]
            if control["control_type"] in NEGATIVE_TYPES
        ]
        if not negative_controls:
            errors.append(issue("NEGATIVE_CONTROL_REQUIRED", hypothesis_id))
        if record_ids is not None:
            for control in negative_controls:
                if control["control_id"] not in record_ids["controls"]:
                    errors.append(
                        issue("UNKNOWN_NEGATIVE_CONTROL_ID", control["control_id"])
                    )

    require_unique(test_ids, "checklist.discriminating_tests")
    require_unique(null_ids, "checklist.nulls")

    return {
        "schema_version": "2.0",
        "checklist_id": checklist["checklist_id"],
        "record_id": checklist["record_id"],
        "valid": not errors,
        "status": (
            "INVALID_CHECKLIST"
            if errors
            else "VALID_PENDING_HUMAN_REVIEW"
            if any(item["human_review_status"] != "complete" for item in checklist["hypotheses"])
            else "VALID_HUMAN_REVIEW_DECLARED_COMPLETE"
        ),
        "errors": errors,
        "warnings": warnings,
        "hypothesis_ids": sorted(
            item["hypothesis_id"] for item in checklist["hypotheses"]
        ),
        "discriminating_test_ids": sorted(test_ids),
        "null_ids": sorted(null_ids),
        "human_review_status_counts": dict(sorted(review_counts.items())),
        "record_cross_check_performed": record is not None,
        "notice": (
            "This audit checks declared falsifiers, rival contrasts, nulls, "
            "controls, and links. It does not prove falsifiability, validate "
            "control assumptions, interpret results, or select a hypothesis."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a bounded local falsification/control JSON checklist without "
            "scientific scoring or candidate selection."
        )
    )
    parser.add_argument("checklist", help="Local falsification/control checklist JSON")
    parser.add_argument(
        "--record", help="Optional local hypothesis record JSON for cross-checks"
    )
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        record = (
            load_hypothesis_record(read_json(args.record)) if args.record else None
        )
        report = audit(load_checklist(read_json(args.checklist)), record)
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/check_operationalization.py`

```python
#!/usr/bin/env python3
"""Audit a local operationalization and measurement checklist without scoring."""

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
    require_unique,
    write_json_report,
)

ROLES = {
    "intervention",
    "exposure",
    "outcome",
    "mediator",
    "confounder",
    "selection",
    "effect_modifier",
    "negative_control",
    "positive_control",
    "other",
}
PLANNING_STATUSES = {"planned", "complete", "not_applicable", "unresolved"}
REVIEW_STATUSES = {"pending", "complete", "specialist_required"}
BOOLEAN_FIELDS = (
    "construct_defined",
    "operational_definition_recorded",
    "population_scope_recorded",
    "unit_or_categories_recorded",
    "timing_recorded",
    "instrument_or_method_recorded",
    "validity_applicability_reviewed",
    "reliability_or_repeatability_plan_recorded",
    "missingness_plan_recorded",
    "limitations_recorded",
)
STATUS_FIELDS = (
    "calibration_or_quality_control_status",
    "measurement_invariance_or_comparability_status",
    "masking_status",
    "threshold_or_cutpoint_status",
)


def load_checklist(payload: Any) -> dict[str, Any]:
    root = require_object(payload, "checklist")
    require_exact_keys(
        root,
        required={
            "schema_version",
            "checklist_id",
            "record_id",
            "human_reviewer",
            "items",
        },
        context="checklist",
    )
    raw_items = require_list(root["items"], "checklist.items", minimum=1, maximum=200)
    parsed_items: list[dict[str, Any]] = []
    identifiers: list[str] = []
    item_fields = {
        "measurement_id",
        "applicability",
        "variable_role",
        "validity_evidence_source_ids",
        "human_review_status",
        "note",
        *BOOLEAN_FIELDS,
        *STATUS_FIELDS,
    }
    for index, raw_item in enumerate(raw_items):
        context = f"checklist.items[{index}]"
        item = require_object(raw_item, context)
        require_exact_keys(item, required=item_fields, context=context)
        measurement_id = require_identifier(
            item["measurement_id"], f"{context}.measurement_id"
        )
        identifiers.append(measurement_id)
        parsed: dict[str, Any] = {
            "measurement_id": measurement_id,
            "applicability": require_enum(
                item["applicability"],
                {"applicable", "not_applicable"},
                f"{context}.applicability",
            ),
            "variable_role": require_enum(
                item["variable_role"], ROLES, f"{context}.variable_role"
            ),
            "validity_evidence_source_ids": require_identifier_list(
                item["validity_evidence_source_ids"],
                f"{context}.validity_evidence_source_ids",
                maximum=100,
            ),
            "human_review_status": require_enum(
                item["human_review_status"],
                REVIEW_STATUSES,
                f"{context}.human_review_status",
            ),
            "note": require_text(
                item["note"], f"{context}.note", allow_empty=True, maximum=2_000
            ),
        }
        for field in BOOLEAN_FIELDS:
            parsed[field] = require_bool(item[field], f"{context}.{field}")
        for field in STATUS_FIELDS:
            parsed[field] = require_enum(
                item[field], PLANNING_STATUSES, f"{context}.{field}"
            )
        parsed_items.append(parsed)
    require_unique(identifiers, "checklist.items")
    return {
        "schema_version": require_enum(
            root["schema_version"], {"2.0"}, "checklist.schema_version"
        ),
        "checklist_id": require_identifier(
            root["checklist_id"], "checklist.checklist_id"
        ),
        "record_id": require_identifier(root["record_id"], "checklist.record_id"),
        "human_reviewer": require_text(
            root["human_reviewer"], "checklist.human_reviewer", minimum=3
        ),
        "items": parsed_items,
    }


def audit(checklist: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    gaps_by_measurement: dict[str, list[str]] = {}
    role_counts: Counter[str] = Counter()
    review_counts: Counter[str] = Counter()

    for item in checklist["items"]:
        measurement_id = item["measurement_id"]
        role_counts[item["variable_role"]] += 1
        review_counts[item["human_review_status"]] += 1
        gaps: list[str] = []

        if item["applicability"] == "not_applicable":
            if not item["note"]:
                errors.append(issue("NOT_APPLICABLE_RATIONALE_REQUIRED", measurement_id))
            continue

        for field in BOOLEAN_FIELDS:
            if not item[field]:
                gaps.append(field)
        if not item["validity_evidence_source_ids"]:
            errors.append(issue("VALIDITY_SOURCE_REQUIRED", measurement_id))
        for field in STATUS_FIELDS:
            status = item[field]
            if status in {"planned", "unresolved"}:
                gaps.append(field)
            if status == "not_applicable" and not item["note"]:
                errors.append(
                    issue("NOT_APPLICABLE_STATUS_NEEDS_RATIONALE", f"{measurement_id}:{field}")
                )
        if item["human_review_status"] != "complete":
            gaps.append("human_review_status")
        if not item["note"]:
            warnings.append(issue("MEASUREMENT_NOTE_EMPTY", measurement_id))
        if gaps:
            gaps_by_measurement[measurement_id] = sorted(set(gaps))

    if not role_counts["outcome"]:
        warnings.append(issue("NO_OUTCOME_MEASUREMENT_DECLARED", "items"))
    if not (role_counts["intervention"] or role_counts["exposure"]):
        warnings.append(issue("NO_INTERVENTION_OR_EXPOSURE_DECLARED", "items"))

    return {
        "schema_version": "2.0",
        "checklist_id": checklist["checklist_id"],
        "record_id": checklist["record_id"],
        "valid": not errors,
        "status": (
            "INVALID_CHECKLIST"
            if errors
            else "VALID_WITH_MEASUREMENT_GAPS"
            if gaps_by_measurement
            else "VALID_HUMAN_REVIEW_COMPLETE"
        ),
        "errors": errors,
        "warnings": warnings,
        "measurement_count": len(checklist["items"]),
        "role_counts": dict(sorted(role_counts.items())),
        "human_review_status_counts": dict(sorted(review_counts.items())),
        "gap_fields_by_measurement_id": gaps_by_measurement,
        "notice": (
            "This checklist records declared measurement work. It does not test "
            "an instrument, establish construct validity, certify comparability, "
            "or score measurement quality. Qualified human review is required."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a bounded local JSON operationalization checklist and report "
            "measurement IDs and unresolved fields without scientific scoring."
        )
    )
    parser.add_argument("checklist", help="Local operationalization checklist JSON")
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

### `scripts/generate_preregistration_scaffold.py`

```python
#!/usr/bin/env python3
"""Generate a deterministic local Markdown preregistration scaffold."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    read_json,
    read_markdown,
    write_markdown,
)
from validate_hypothesis_schema import load_hypothesis_record, validate_record

TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "preregistration_scaffold_template.md"
)
PLACEHOLDER_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}")
MARKDOWN_SPECIAL_RE = re.compile(r"([\\`*_[\]{}#+|])")


def _safe_text(value: Any) -> str:
    """Render bounded input as inert one-line Markdown text."""
    text = " ".join(str(value).split())
    text = html.escape(text, quote=False)
    return MARKDOWN_SPECIAL_RE.sub(r"\\\1", text)


def _bullet(label: str, value: Any) -> str:
    return f"- **{_safe_text(label)}:** {_safe_text(value)}"


def _render_ethics(record: dict[str, Any]) -> str:
    ethics = record["ethics_and_feasibility"]
    lines = [
        _bullet(field.replace("_", " "), ethics[field])
        for field in (
            "human_subjects_gate",
            "animal_research_gate",
            "biosafety_gate",
            "dual_use_gate",
            "regulatory_gate",
            "data_governance_gate",
            "feasibility_status",
        )
    ]
    reviews = ethics["required_reviews"] or ["None declared"]
    blocks = ethics["unresolved_blocks"] or ["None declared"]
    lines.append(_bullet("required reviews", "; ".join(reviews)))
    lines.append(_bullet("unresolved blocks", "; ".join(blocks)))
    return "\n".join(lines)


def _render_evidence(record: dict[str, Any]) -> str:
    evidence = record["evidence"]
    lines = [
        _bullet("search boundary ID", evidence["search_boundary_id"]),
        _bullet("evidence ledger path", evidence["ledger_path"]),
        _bullet("declared source IDs", "; ".join(evidence["source_ids"])),
        _bullet("evidence limitations", "; ".join(evidence["evidence_limitations"])),
    ]
    return "\n".join(lines)


def _render_observation(record: dict[str, Any]) -> str:
    observation = record["observation"]
    return "\n".join(
        [
            _bullet("statement", observation["statement"]),
            _bullet("provenance", observation["provenance"]),
            _bullet("source IDs", "; ".join(observation["source_ids"])),
            _bullet("uncertainties", "; ".join(observation["uncertainties"])),
        ]
    )


def _render_question(record: dict[str, Any]) -> str:
    question = record["research_question"]
    return "\n".join(
        _bullet(field.replace("_", " "), question[field])
        for field in (
            "statement",
            "framework",
            "question_type",
            "population_or_system",
            "intervention_or_exposure",
            "comparator",
            "outcome",
            "timeframe",
        )
    )


def _render_hypotheses(record: dict[str, Any]) -> str:
    sections: list[str] = []
    for hypothesis in record["hypotheses"]:
        sections.extend(
            [
                f"### {_safe_text(hypothesis['hypothesis_id'])}",
                "",
                _bullet("status", hypothesis["status"]),
                _bullet("candidate statement", hypothesis["statement"]),
                _bullet("proposed mechanism", hypothesis["mechanism"]),
                _bullet("rival IDs", "; ".join(hypothesis["rival_hypothesis_ids"])),
                _bullet("assumptions", "; ".join(hypothesis["assumptions"])),
                _bullet(
                    "boundary conditions", "; ".join(hypothesis["boundary_conditions"])
                ),
                _bullet("uncertainties", "; ".join(hypothesis["uncertainties"])),
                _bullet("source IDs", "; ".join(hypothesis["source_ids"])),
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _render_estimands(record: dict[str, Any]) -> str:
    if not record["causal_estimands"]:
        return "- Not applicable to the declared non-causal question."
    sections: list[str] = []
    for estimand in record["causal_estimands"]:
        sections.extend(
            [
                f"### {_safe_text(estimand['estimand_id'])}",
                "",
                _bullet(
                    "linked hypothesis IDs",
                    "; ".join(estimand["linked_hypothesis_ids"]),
                ),
                _bullet("population", estimand["population"]),
                _bullet(
                    "intervention or exposure", estimand["intervention_or_exposure"]
                ),
                _bullet("comparator", estimand["comparator"]),
                _bullet("outcome", estimand["outcome"]),
                _bullet("time horizon", estimand["time_horizon"]),
                _bullet("population summary", estimand["population_summary"]),
                _bullet(
                    "intercurrent-event strategy",
                    estimand["intercurrent_event_strategy"],
                ),
                _bullet(
                    "identification assumptions",
                    "; ".join(estimand["identification_assumptions"]),
                ),
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _render_predictions(record: dict[str, Any]) -> str:
    sections: list[str] = []
    for prediction in record["predictions"]:
        sections.extend(
            [
                f"### {_safe_text(prediction['prediction_id'])} "
                f"({_safe_text(prediction['hypothesis_id'])})",
                "",
                _bullet("statement", prediction["statement"]),
                _bullet("conditions", prediction["conditions"]),
                _bullet("observable", prediction["observable"]),
                _bullet("expected pattern", prediction["expected_pattern"]),
                _bullet("falsifier", prediction["falsifier"]),
                _bullet(
                    "rival hypothesis IDs",
                    "; ".join(prediction["rival_hypothesis_ids"]),
                ),
                _bullet("measurement IDs", "; ".join(prediction["measurement_ids"])),
                _bullet("analysis IDs", "; ".join(prediction["analysis_ids"])),
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _render_nulls_and_controls(record: dict[str, Any]) -> str:
    sections = ["### Null hypotheses", ""]
    for null in record["null_hypotheses"]:
        sections.extend(
            [
                _bullet(
                    null["null_id"],
                    f"{null['statement']} | Rule: "
                    f"{null['rejection_or_compatibility_rule']}",
                ),
                "",
            ]
        )
    sections.extend(["### Negative controls", ""])
    for control in record["negative_controls"]:
        sections.extend(
            [
                _bullet(
                    control["control_id"],
                    f"{control['control_type']} | Rationale: {control['rationale']} "
                    f"| Expected: {control['expected_result']} | Failure: "
                    f"{control['failure_implication']}",
                ),
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _render_operationalizations(record: dict[str, Any]) -> str:
    sections: list[str] = []
    for measurement in record["operationalizations"]:
        sections.extend(
            [
                f"### {_safe_text(measurement['measurement_id'])}",
                "",
                _bullet("construct", measurement["construct"]),
                _bullet("variable and role", f"{measurement['variable']} / {measurement['role']}"),
                _bullet(
                    "operational definition", measurement["operational_definition"]
                ),
                _bullet(
                    "instrument or method", measurement["instrument_or_method"]
                ),
                _bullet("unit", measurement["unit"]),
                _bullet("timing", measurement["timing"]),
                _bullet("population or system", measurement["population_or_system"]),
                _bullet(
                    "validity evidence source IDs",
                    "; ".join(measurement["validity_evidence_source_ids"]),
                ),
                _bullet("reliability plan", measurement["reliability_plan"]),
                _bullet("missingness plan", measurement["missingness_plan"]),
                _bullet(
                    "blinding or masking", measurement["blinding_or_masking"]
                ),
                _bullet("threshold rationale", measurement["threshold_rationale"]),
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _render_analyses(record: dict[str, Any]) -> str:
    sections: list[str] = []
    for analysis in record["analysis_plan"]["analyses"]:
        sections.extend(
            [
                f"### {_safe_text(analysis['analysis_id'])}",
                "",
                _bullet("mode", analysis["exploratory_or_confirmatory"]),
                _bullet("prediction IDs", "; ".join(analysis["prediction_ids"])),
                _bullet("estimand IDs", "; ".join(analysis["estimand_ids"]) or "None"),
                _bullet("analysis population", analysis["analysis_population"]),
                _bullet("method", analysis["method"]),
                _bullet(
                    "effect or summary measure",
                    analysis["effect_or_summary_measure"],
                ),
                _bullet("uncertainty method", analysis["uncertainty_method"]),
                _bullet("missing-data plan", analysis["missing_data_plan"]),
                _bullet("multiplicity plan", analysis["multiplicity_plan"]),
                _bullet(
                    "sensitivity analyses",
                    "; ".join(analysis["sensitivity_analyses"]),
                ),
                _bullet("decision rule", analysis["decision_rule"]),
                "",
            ]
        )
    return "\n".join(sections).rstrip()


def _render_ai_use(record: dict[str, Any]) -> str:
    ai_use = record["ai_use"]
    return "\n".join(
        [
            _bullet("AI used", str(ai_use["used"]).lower()),
            _bullet(
                "sensitive or unpublished data sent externally",
                str(
                    ai_use["sensitive_or_unpublished_data_sent_externally"]
                ).lower(),
            ),
            _bullet(
                "local policy checked", str(ai_use["local_policy_checked"]).lower()
            ),
            _bullet(
                "citation verification required",
                str(ai_use["citation_verification_required"]).lower(),
            ),
            _bullet(
                "human accountable", str(ai_use["human_accountable"]).lower()
            ),
            _bullet("diversity mitigation", ai_use["diversity_mitigation"]),
        ]
    )


def generate(
    record: dict[str, Any], template_path: Path = TEMPLATE_PATH
) -> str:
    """Render all candidates into a local draft without ranking or selection."""
    validation = validate_record(record)
    if not validation["valid"]:
        codes = sorted({item["code"] for item in validation["errors"]})
        raise ValidationError(
            "hypothesis record is invalid; resolve these controls first: "
            + ", ".join(codes)
        )
    if validation["unresolved_gate_fields"]:
        raise ValidationError(
            "hypothesis record has unresolved safety or feasibility gates: "
            + ", ".join(validation["unresolved_gate_fields"])
        )

    template = read_markdown(template_path)
    replacements = {
        "{{PROJECT_ID}}": _safe_text(record["project_id"]),
        "{{GENERATED_ON}}": _safe_text(record["updated_on"]),
        "{{HUMAN_OWNER}}": _safe_text(record["human_owner"]),
        "{{RECORD_STATUS}}": _safe_text(record["status"]),
        "{{UPDATED_ON}}": _safe_text(record["updated_on"]),
        "{{ETHICS_AND_FEASIBILITY}}": _render_ethics(record),
        "{{EVIDENCE_BOUNDARY}}": _render_evidence(record),
        "{{OBSERVATION}}": _render_observation(record),
        "{{RESEARCH_QUESTION}}": _render_question(record),
        "{{HYPOTHESES}}": _render_hypotheses(record),
        "{{ESTIMANDS}}": _render_estimands(record),
        "{{PREDICTIONS}}": _render_predictions(record),
        "{{NULLS_AND_CONTROLS}}": _render_nulls_and_controls(record),
        "{{OPERATIONALIZATIONS}}": _render_operationalizations(record),
        "{{ANALYSES}}": _render_analyses(record),
        "{{AI_USE}}": _render_ai_use(record),
        "{{DEVIATION_PLAN}}": _safe_text(
            record["analysis_plan"]["deviation_reporting"]
        ),
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
    return rendered.rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a private local Markdown preregistration scaffold from a "
            "valid hypothesis record; no upload or registration occurs."
        )
    )
    parser.add_argument("record", help="Local hypothesis record JSON")
    parser.add_argument("-o", "--output", required=True, help="Output Markdown path")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        record = load_hypothesis_record(read_json(args.record))
        destination = write_markdown(
            generate(record), args.output, force=args.force
        )
        print(f"Created local preregistration scaffold: {destination}")
        return 0
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/lint_causal_claims.py`

```python
#!/usr/bin/env python3
"""Lexically lint causal versus associational claims in bounded Markdown."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from typing import Any

from _common import (
    ValidationError,
    error_exit,
    issue,
    read_markdown,
    write_json_report,
)

TAG_RE = re.compile(
    r"\[(claim|estimand|identification|confounding|selection|collider|"
    r"reverse-causation):([A-Za-z0-9_.:-]+)\]",
    re.IGNORECASE,
)
CAUSAL_RE = re.compile(
    r"\b(?:causes?|caused|causal\s+(?:effect|impact)|effect\s+of|"
    r"leads?\s+to|results?\s+in|increases?|reduces?|prevents?|improves?|"
    r"worsens?|drives?|mediates?|produces?)\b",
    re.IGNORECASE,
)
ASSOCIATION_RE = re.compile(
    r"\b(?:associated\s+with|association|correlates?\s+with|correlation|"
    r"co-var(?:y|ies|ied)\s+with|predicts?|linked\s+to)\b",
    re.IGNORECASE,
)
CLAIM_TYPES = {"causal", "associational", "descriptive", "predictive", "mechanistic"}
IDENTIFICATION_TYPES = {
    "randomized",
    "quasi_experimental",
    "observational_assumption_dependent",
    "mechanistic_experiment",
    "other_assumption_dependent",
}
RISK_STATES = {"assessed", "unresolved", "not_applicable"}
REQUIRED_CAUSAL_TAGS = (
    "estimand",
    "identification",
    "confounding",
    "selection",
    "collider",
    "reverse-causation",
)


def _finding(code: str, line_number: int) -> dict[str, Any]:
    return {"code": code, "line": line_number}


def lint(markdown: str) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    claim_counts: Counter[str] = Counter()
    causal_trigger_lines = 0
    association_trigger_lines = 0
    in_fence = False

    for line_number, raw_line in enumerate(markdown.splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped or stripped.startswith("#"):
            continue

        matches = [(key.casefold(), value) for key, value in TAG_RE.findall(stripped)]
        key_counts = Counter(key for key, _ in matches)
        for key, count in key_counts.items():
            if count > 1:
                errors.append(_finding(f"DUPLICATE_{key.upper()}_TAG", line_number))
        tags = {key: value for key, value in matches}
        claim_type = tags.get("claim", "").casefold()
        has_causal_language = CAUSAL_RE.search(stripped) is not None
        has_association_language = ASSOCIATION_RE.search(stripped) is not None

        if claim_type:
            if claim_type not in CLAIM_TYPES:
                errors.append(_finding("INVALID_CLAIM_TYPE", line_number))
            else:
                claim_counts[claim_type] += 1

        if has_causal_language:
            causal_trigger_lines += 1
            if not claim_type:
                errors.append(_finding("UNMARKED_CAUSAL_LANGUAGE", line_number))
            elif claim_type not in {"causal", "mechanistic"}:
                errors.append(
                    _finding("CAUSAL_LANGUAGE_IN_NONCAUSAL_CLAIM", line_number)
                )

        if has_association_language:
            association_trigger_lines += 1
            if not claim_type:
                warnings.append(
                    _finding("UNMARKED_ASSOCIATIONAL_LANGUAGE", line_number)
                )
            elif claim_type == "causal" and not has_causal_language:
                warnings.append(
                    _finding("CAUSAL_TAG_WITH_ASSOCIATION_ONLY_LANGUAGE", line_number)
                )

        if claim_type == "causal":
            for required_tag in REQUIRED_CAUSAL_TAGS:
                if required_tag not in tags:
                    code_tag = required_tag.replace("-", "_").upper()
                    errors.append(
                        _finding(
                            f"CAUSAL_CLAIM_MISSING_{code_tag}_TAG",
                            line_number,
                        )
                    )
            identification = tags.get("identification", "").casefold()
            if identification and identification not in IDENTIFICATION_TYPES:
                errors.append(_finding("INVALID_IDENTIFICATION_TAG", line_number))
            for risk_tag in (
                "confounding",
                "selection",
                "collider",
                "reverse-causation",
            ):
                state = tags.get(risk_tag, "").casefold()
                code_tag = risk_tag.replace("-", "_").upper()
                if state and state not in RISK_STATES:
                    errors.append(
                        _finding(f"INVALID_{code_tag}_STATE", line_number)
                    )
                if state == "unresolved":
                    warnings.append(
                        _finding(f"UNRESOLVED_{code_tag}_RISK", line_number)
                    )
        elif claim_type and "estimand" in tags:
            warnings.append(_finding("ESTIMAND_TAG_ON_NONCAUSAL_CLAIM", line_number))

    if in_fence:
        errors.append(issue("UNCLOSED_MARKDOWN_FENCE", "document"))

    return {
        "schema_version": "2.0",
        "valid": not errors,
        "status": "INVALID_CLAIM_MARKUP" if errors else "VALID_LEXICAL_LINT",
        "errors": errors,
        "warnings": warnings,
        "claim_type_counts": dict(sorted(claim_counts.items())),
        "causal_trigger_line_count": causal_trigger_lines,
        "associational_trigger_line_count": association_trigger_lines,
        "notice": (
            "This deterministic lexical lint does not determine whether language "
            "is scientifically causal, whether an estimand is well defined, or "
            "whether identification assumptions hold. Review every flagged and "
            "unflagged claim manually."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Lint bounded local Markdown for causal/associational claim annotations "
            "and emit only rule codes and line numbers."
        )
    )
    parser.add_argument("document", help="Local Markdown document")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = lint(read_markdown(args.document))
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_hypothesis_schema.py`

```python
#!/usr/bin/env python3
"""Validate a structured hypothesis record without judging scientific merit."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import PurePosixPath
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
    require_iso_date,
    require_list,
    require_object,
    require_text,
    require_text_list,
    require_unique,
    write_json_report,
)

QUESTION_TYPES = {"descriptive", "associational", "predictive", "causal", "mechanistic"}
HYPOTHESIS_STATUS = {"candidate"}
MEASUREMENT_ROLES = {
    "intervention",
    "exposure",
    "outcome",
    "mediator",
    "confounder",
    "selection",
    "negative_control",
    "positive_control",
    "effect_modifier",
    "other",
}
RISK_TYPES = {
    "confounding",
    "selection_bias",
    "collider_bias",
    "reverse_causation",
    "measurement_bias",
    "other",
}
CONTROL_TYPES = {
    "negative_exposure",
    "negative_outcome",
    "procedural_negative",
    "positive_control",
    "vehicle_or_sham",
    "other",
}
PLAN_MODES = {"confirmatory", "exploratory"}
GATE_STATES = {"not_applicable", "undetermined", "requires_review", "approved", "blocked"}
FEASIBILITY_STATES = {
    "undetermined",
    "feasible_for_planning",
    "requires_pilot",
    "infeasible",
    "blocked",
}


def _parse_observation(raw: Any) -> dict[str, Any]:
    value = require_object(raw, "record.observation")
    require_exact_keys(
        value,
        required={"statement", "provenance", "source_ids", "uncertainties"},
        context="record.observation",
    )
    return {
        "statement": require_text(
            value["statement"], "record.observation.statement", minimum=10
        ),
        "provenance": require_text(
            value["provenance"], "record.observation.provenance", minimum=10
        ),
        "source_ids": require_identifier_list(
            value["source_ids"], "record.observation.source_ids", minimum=1
        ),
        "uncertainties": require_text_list(
            value["uncertainties"],
            "record.observation.uncertainties",
            minimum=1,
        ),
    }


def _parse_question(raw: Any) -> dict[str, str]:
    value = require_object(raw, "record.research_question")
    fields = {
        "statement",
        "framework",
        "question_type",
        "population_or_system",
        "intervention_or_exposure",
        "comparator",
        "outcome",
        "timeframe",
    }
    require_exact_keys(value, required=fields, context="record.research_question")
    parsed = {
        field: require_text(
            value[field],
            f"record.research_question.{field}",
            minimum=2 if field == "framework" else 5,
        )
        for field in fields
        if field != "question_type"
    }
    parsed["question_type"] = require_enum(
        value["question_type"],
        QUESTION_TYPES,
        "record.research_question.question_type",
    )
    return parsed


def _parse_hypotheses(raw: Any) -> list[dict[str, Any]]:
    entries = require_list(raw, "record.hypotheses", minimum=1, maximum=50)
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "hypothesis_id",
        "statement",
        "mechanism",
        "status",
        "source_ids",
        "assumptions",
        "boundary_conditions",
        "uncertainties",
        "prediction_ids",
        "rival_hypothesis_ids",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.hypotheses[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["hypothesis_id"], f"{context}.hypothesis_id")
        identifiers.append(identifier)
        parsed.append(
            {
                "hypothesis_id": identifier,
                "statement": require_text(
                    entry["statement"], f"{context}.statement", minimum=10
                ),
                "mechanism": require_text(
                    entry["mechanism"], f"{context}.mechanism", minimum=10
                ),
                "status": require_enum(
                    entry["status"], HYPOTHESIS_STATUS, f"{context}.status"
                ),
                "source_ids": require_identifier_list(
                    entry["source_ids"], f"{context}.source_ids", minimum=1
                ),
                "assumptions": require_text_list(
                    entry["assumptions"], f"{context}.assumptions", minimum=1
                ),
                "boundary_conditions": require_text_list(
                    entry["boundary_conditions"],
                    f"{context}.boundary_conditions",
                    minimum=1,
                ),
                "uncertainties": require_text_list(
                    entry["uncertainties"], f"{context}.uncertainties", minimum=1
                ),
                "prediction_ids": require_identifier_list(
                    entry["prediction_ids"], f"{context}.prediction_ids", minimum=1
                ),
                "rival_hypothesis_ids": require_identifier_list(
                    entry["rival_hypothesis_ids"],
                    f"{context}.rival_hypothesis_ids",
                ),
            }
        )
    require_unique(identifiers, "record.hypotheses")
    return parsed


def _parse_estimands(raw: Any) -> list[dict[str, Any]]:
    entries = require_list(raw, "record.causal_estimands", maximum=50)
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "estimand_id",
        "linked_hypothesis_ids",
        "population",
        "intervention_or_exposure",
        "comparator",
        "outcome",
        "time_horizon",
        "population_summary",
        "intercurrent_event_strategy",
        "identification_assumptions",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.causal_estimands[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["estimand_id"], f"{context}.estimand_id")
        identifiers.append(identifier)
        parsed.append(
            {
                "estimand_id": identifier,
                "linked_hypothesis_ids": require_identifier_list(
                    entry["linked_hypothesis_ids"],
                    f"{context}.linked_hypothesis_ids",
                    minimum=1,
                ),
                "population": require_text(entry["population"], f"{context}.population"),
                "intervention_or_exposure": require_text(
                    entry["intervention_or_exposure"],
                    f"{context}.intervention_or_exposure",
                ),
                "comparator": require_text(
                    entry["comparator"], f"{context}.comparator"
                ),
                "outcome": require_text(entry["outcome"], f"{context}.outcome"),
                "time_horizon": require_text(
                    entry["time_horizon"], f"{context}.time_horizon"
                ),
                "population_summary": require_text(
                    entry["population_summary"], f"{context}.population_summary"
                ),
                "intercurrent_event_strategy": require_text(
                    entry["intercurrent_event_strategy"],
                    f"{context}.intercurrent_event_strategy",
                ),
                "identification_assumptions": require_text_list(
                    entry["identification_assumptions"],
                    f"{context}.identification_assumptions",
                    minimum=1,
                ),
            }
        )
    require_unique(identifiers, "record.causal_estimands")
    return parsed


def _parse_predictions(raw: Any) -> list[dict[str, Any]]:
    entries = require_list(raw, "record.predictions", minimum=1, maximum=200)
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "prediction_id",
        "hypothesis_id",
        "statement",
        "observable",
        "conditions",
        "expected_pattern",
        "falsifier",
        "rival_hypothesis_ids",
        "measurement_ids",
        "analysis_ids",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.predictions[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["prediction_id"], f"{context}.prediction_id")
        identifiers.append(identifier)
        parsed.append(
            {
                "prediction_id": identifier,
                "hypothesis_id": require_identifier(
                    entry["hypothesis_id"], f"{context}.hypothesis_id"
                ),
                "statement": require_text(
                    entry["statement"], f"{context}.statement", minimum=10
                ),
                "observable": require_text(
                    entry["observable"], f"{context}.observable", minimum=5
                ),
                "conditions": require_text(
                    entry["conditions"], f"{context}.conditions", minimum=5
                ),
                "expected_pattern": require_text(
                    entry["expected_pattern"], f"{context}.expected_pattern", minimum=5
                ),
                "falsifier": require_text(
                    entry["falsifier"], f"{context}.falsifier", minimum=10
                ),
                "rival_hypothesis_ids": require_identifier_list(
                    entry["rival_hypothesis_ids"],
                    f"{context}.rival_hypothesis_ids",
                    minimum=1,
                ),
                "measurement_ids": require_identifier_list(
                    entry["measurement_ids"],
                    f"{context}.measurement_ids",
                    minimum=1,
                ),
                "analysis_ids": require_identifier_list(
                    entry["analysis_ids"], f"{context}.analysis_ids", minimum=1
                ),
            }
        )
    require_unique(identifiers, "record.predictions")
    return parsed


def _parse_alternatives(raw: Any) -> list[dict[str, Any]]:
    entries = require_list(raw, "record.alternative_explanations", minimum=1, maximum=100)
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "alternative_id",
        "statement",
        "linked_hypothesis_ids",
        "risk_types",
        "discriminating_prediction_ids",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.alternative_explanations[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["alternative_id"], f"{context}.alternative_id")
        identifiers.append(identifier)
        risk_types = require_text_list(
            entry["risk_types"], f"{context}.risk_types", minimum=1, maximum=10
        )
        for risk_index, risk_type in enumerate(risk_types):
            require_enum(risk_type, RISK_TYPES, f"{context}.risk_types[{risk_index}]")
        require_unique(risk_types, f"{context}.risk_types")
        parsed.append(
            {
                "alternative_id": identifier,
                "statement": require_text(
                    entry["statement"], f"{context}.statement", minimum=10
                ),
                "linked_hypothesis_ids": require_identifier_list(
                    entry["linked_hypothesis_ids"],
                    f"{context}.linked_hypothesis_ids",
                    minimum=1,
                ),
                "risk_types": risk_types,
                "discriminating_prediction_ids": require_identifier_list(
                    entry["discriminating_prediction_ids"],
                    f"{context}.discriminating_prediction_ids",
                    minimum=1,
                ),
            }
        )
    require_unique(identifiers, "record.alternative_explanations")
    return parsed


def _parse_nulls(raw: Any) -> list[dict[str, Any]]:
    entries = require_list(raw, "record.null_hypotheses", minimum=1, maximum=100)
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "null_id",
        "statement",
        "linked_prediction_ids",
        "rejection_or_compatibility_rule",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.null_hypotheses[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["null_id"], f"{context}.null_id")
        identifiers.append(identifier)
        parsed.append(
            {
                "null_id": identifier,
                "statement": require_text(
                    entry["statement"], f"{context}.statement", minimum=10
                ),
                "linked_prediction_ids": require_identifier_list(
                    entry["linked_prediction_ids"],
                    f"{context}.linked_prediction_ids",
                    minimum=1,
                ),
                "rejection_or_compatibility_rule": require_text(
                    entry["rejection_or_compatibility_rule"],
                    f"{context}.rejection_or_compatibility_rule",
                    minimum=10,
                ),
            }
        )
    require_unique(identifiers, "record.null_hypotheses")
    return parsed


def _parse_controls(raw: Any) -> list[dict[str, Any]]:
    entries = require_list(raw, "record.negative_controls", minimum=1, maximum=100)
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "control_id",
        "control_type",
        "rationale",
        "expected_result",
        "failure_implication",
        "linked_prediction_ids",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.negative_controls[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["control_id"], f"{context}.control_id")
        identifiers.append(identifier)
        parsed.append(
            {
                "control_id": identifier,
                "control_type": require_enum(
                    entry["control_type"], CONTROL_TYPES, f"{context}.control_type"
                ),
                "rationale": require_text(
                    entry["rationale"], f"{context}.rationale", minimum=10
                ),
                "expected_result": require_text(
                    entry["expected_result"], f"{context}.expected_result", minimum=5
                ),
                "failure_implication": require_text(
                    entry["failure_implication"],
                    f"{context}.failure_implication",
                    minimum=10,
                ),
                "linked_prediction_ids": require_identifier_list(
                    entry["linked_prediction_ids"],
                    f"{context}.linked_prediction_ids",
                    minimum=1,
                ),
            }
        )
    require_unique(identifiers, "record.negative_controls")
    return parsed


def _parse_operationalizations(raw: Any) -> list[dict[str, Any]]:
    entries = require_list(raw, "record.operationalizations", minimum=1, maximum=200)
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "measurement_id",
        "construct",
        "variable",
        "role",
        "operational_definition",
        "instrument_or_method",
        "unit",
        "timing",
        "population_or_system",
        "validity_evidence_source_ids",
        "reliability_plan",
        "missingness_plan",
        "blinding_or_masking",
        "threshold_rationale",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.operationalizations[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["measurement_id"], f"{context}.measurement_id")
        identifiers.append(identifier)
        text_fields = fields - {
            "measurement_id",
            "role",
            "validity_evidence_source_ids",
        }
        parsed_entry: dict[str, Any] = {
            "measurement_id": identifier,
            "role": require_enum(entry["role"], MEASUREMENT_ROLES, f"{context}.role"),
            "validity_evidence_source_ids": require_identifier_list(
                entry["validity_evidence_source_ids"],
                f"{context}.validity_evidence_source_ids",
                minimum=1,
            ),
        }
        for field in text_fields:
            parsed_entry[field] = require_text(
                entry[field],
                f"{context}.{field}",
                minimum=2 if field in {"unit", "variable"} else 5,
            )
        parsed.append(parsed_entry)
    require_unique(identifiers, "record.operationalizations")
    return parsed


def _parse_analysis_plan(raw: Any) -> dict[str, Any]:
    plan = require_object(raw, "record.analysis_plan")
    require_exact_keys(
        plan,
        required={"analyses", "harking_control", "deviation_reporting"},
        context="record.analysis_plan",
    )
    entries = require_list(
        plan["analyses"], "record.analysis_plan.analyses", minimum=1, maximum=200
    )
    parsed: list[dict[str, Any]] = []
    identifiers: list[str] = []
    fields = {
        "analysis_id",
        "prediction_ids",
        "estimand_ids",
        "analysis_population",
        "method",
        "effect_or_summary_measure",
        "uncertainty_method",
        "missing_data_plan",
        "multiplicity_plan",
        "sensitivity_analyses",
        "decision_rule",
        "exploratory_or_confirmatory",
    }
    for index, raw_entry in enumerate(entries):
        context = f"record.analysis_plan.analyses[{index}]"
        entry = require_object(raw_entry, context)
        require_exact_keys(entry, required=fields, context=context)
        identifier = require_identifier(entry["analysis_id"], f"{context}.analysis_id")
        identifiers.append(identifier)
        parsed.append(
            {
                "analysis_id": identifier,
                "prediction_ids": require_identifier_list(
                    entry["prediction_ids"], f"{context}.prediction_ids", minimum=1
                ),
                "estimand_ids": require_identifier_list(
                    entry["estimand_ids"], f"{context}.estimand_ids"
                ),
                "analysis_population": require_text(
                    entry["analysis_population"],
                    f"{context}.analysis_population",
                    minimum=5,
                ),
                "method": require_text(entry["method"], f"{context}.method", minimum=5),
                "effect_or_summary_measure": require_text(
                    entry["effect_or_summary_measure"],
                    f"{context}.effect_or_summary_measure",
                    minimum=3,
                ),
                "uncertainty_method": require_text(
                    entry["uncertainty_method"],
                    f"{context}.uncertainty_method",
                    minimum=5,
                ),
                "missing_data_plan": require_text(
                    entry["missing_data_plan"],
                    f"{context}.missing_data_plan",
                    minimum=5,
                ),
                "multiplicity_plan": require_text(
                    entry["multiplicity_plan"],
                    f"{context}.multiplicity_plan",
                    minimum=5,
                ),
                "sensitivity_analyses": require_text_list(
                    entry["sensitivity_analyses"],
                    f"{context}.sensitivity_analyses",
                    minimum=1,
                ),
                "decision_rule": require_text(
                    entry["decision_rule"], f"{context}.decision_rule", minimum=10
                ),
                "exploratory_or_confirmatory": require_enum(
                    entry["exploratory_or_confirmatory"],
                    PLAN_MODES,
                    f"{context}.exploratory_or_confirmatory",
                ),
            }
        )
    require_unique(identifiers, "record.analysis_plan.analyses")
    return {
        "analyses": parsed,
        "harking_control": require_text(
            plan["harking_control"],
            "record.analysis_plan.harking_control",
            minimum=10,
        ),
        "deviation_reporting": require_text(
            plan["deviation_reporting"],
            "record.analysis_plan.deviation_reporting",
            minimum=10,
        ),
    }


def _parse_evidence(raw: Any) -> dict[str, Any]:
    value = require_object(raw, "record.evidence")
    require_exact_keys(
        value,
        required={
            "ledger_path",
            "source_ids",
            "search_boundary_id",
            "evidence_limitations",
        },
        context="record.evidence",
    )
    ledger_path = require_text(
        value["ledger_path"], "record.evidence.ledger_path", maximum=500
    )
    pure_path = PurePosixPath(ledger_path)
    if pure_path.is_absolute() or ".." in pure_path.parts or "://" in ledger_path:
        raise ValidationError("record.evidence.ledger_path must be a safe relative path")
    if pure_path.suffix.lower() != ".csv":
        raise ValidationError("record.evidence.ledger_path must end in .csv")
    return {
        "ledger_path": ledger_path,
        "source_ids": require_identifier_list(
            value["source_ids"], "record.evidence.source_ids", minimum=1
        ),
        "search_boundary_id": require_identifier(
            value["search_boundary_id"], "record.evidence.search_boundary_id"
        ),
        "evidence_limitations": require_text_list(
            value["evidence_limitations"],
            "record.evidence.evidence_limitations",
            minimum=1,
        ),
    }


def _parse_risk_register(raw: Any) -> dict[str, list[str]]:
    value = require_object(raw, "record.risk_register")
    fields = {
        "confounding",
        "selection_bias",
        "collider_bias",
        "reverse_causation",
        "measurement_bias",
        "other",
    }
    require_exact_keys(value, required=fields, context="record.risk_register")
    return {
        field: require_text_list(
            value[field], f"record.risk_register.{field}", maximum=50
        )
        for field in fields
    }


def _parse_ethics(raw: Any) -> dict[str, Any]:
    value = require_object(raw, "record.ethics_and_feasibility")
    gate_fields = {
        "human_subjects_gate",
        "animal_research_gate",
        "biosafety_gate",
        "dual_use_gate",
        "regulatory_gate",
        "data_governance_gate",
    }
    require_exact_keys(
        value,
        required=gate_fields
        | {"feasibility_status", "required_reviews", "unresolved_blocks"},
        context="record.ethics_and_feasibility",
    )
    parsed: dict[str, Any] = {
        field: require_enum(
            value[field], GATE_STATES, f"record.ethics_and_feasibility.{field}"
        )
        for field in gate_fields
    }
    parsed["feasibility_status"] = require_enum(
        value["feasibility_status"],
        FEASIBILITY_STATES,
        "record.ethics_and_feasibility.feasibility_status",
    )
    parsed["required_reviews"] = require_text_list(
        value["required_reviews"],
        "record.ethics_and_feasibility.required_reviews",
        maximum=50,
    )
    parsed["unresolved_blocks"] = require_text_list(
        value["unresolved_blocks"],
        "record.ethics_and_feasibility.unresolved_blocks",
        maximum=50,
    )
    return parsed


def _parse_ai_use(raw: Any) -> dict[str, Any]:
    value = require_object(raw, "record.ai_use")
    fields = {
        "used",
        "sensitive_or_unpublished_data_sent_externally",
        "local_policy_checked",
        "citation_verification_required",
        "human_accountable",
        "diversity_mitigation",
    }
    require_exact_keys(value, required=fields, context="record.ai_use")
    return {
        "used": require_bool(value["used"], "record.ai_use.used"),
        "sensitive_or_unpublished_data_sent_externally": require_bool(
            value["sensitive_or_unpublished_data_sent_externally"],
            "record.ai_use.sensitive_or_unpublished_data_sent_externally",
        ),
        "local_policy_checked": require_bool(
            value["local_policy_checked"], "record.ai_use.local_policy_checked"
        ),
        "citation_verification_required": require_bool(
            value["citation_verification_required"],
            "record.ai_use.citation_verification_required",
        ),
        "human_accountable": require_bool(
            value["human_accountable"], "record.ai_use.human_accountable"
        ),
        "diversity_mitigation": require_text(
            value["diversity_mitigation"],
            "record.ai_use.diversity_mitigation",
            minimum=10,
        ),
    }


def load_hypothesis_record(payload: Any) -> dict[str, Any]:
    """Parse the exact v2 record schema and normalize bounded values."""
    root = require_object(payload, "record")
    fields = {
        "schema_version",
        "project_id",
        "status",
        "updated_on",
        "human_owner",
        "observation",
        "research_question",
        "hypotheses",
        "causal_estimands",
        "predictions",
        "alternative_explanations",
        "null_hypotheses",
        "negative_controls",
        "operationalizations",
        "analysis_plan",
        "evidence",
        "risk_register",
        "ethics_and_feasibility",
        "ai_use",
    }
    require_exact_keys(root, required=fields, context="record")
    return {
        "schema_version": require_enum(
            root["schema_version"], {"2.0"}, "record.schema_version"
        ),
        "project_id": require_identifier(root["project_id"], "record.project_id"),
        "status": require_enum(
            root["status"], {"draft", "preregistered", "archived"}, "record.status"
        ),
        "updated_on": require_iso_date(root["updated_on"], "record.updated_on"),
        "human_owner": require_text(
            root["human_owner"], "record.human_owner", minimum=3
        ),
        "observation": _parse_observation(root["observation"]),
        "research_question": _parse_question(root["research_question"]),
        "hypotheses": _parse_hypotheses(root["hypotheses"]),
        "causal_estimands": _parse_estimands(root["causal_estimands"]),
        "predictions": _parse_predictions(root["predictions"]),
        "alternative_explanations": _parse_alternatives(
            root["alternative_explanations"]
        ),
        "null_hypotheses": _parse_nulls(root["null_hypotheses"]),
        "negative_controls": _parse_controls(root["negative_controls"]),
        "operationalizations": _parse_operationalizations(root["operationalizations"]),
        "analysis_plan": _parse_analysis_plan(root["analysis_plan"]),
        "evidence": _parse_evidence(root["evidence"]),
        "risk_register": _parse_risk_register(root["risk_register"]),
        "ethics_and_feasibility": _parse_ethics(root["ethics_and_feasibility"]),
        "ai_use": _parse_ai_use(root["ai_use"]),
    }


def _missing_references(
    values: list[str], valid_values: set[str], code: str, field: str
) -> list[dict[str, str]]:
    return [
        issue(code, f"{field}:{value}")
        for value in sorted(set(values) - valid_values)
    ]


def validate_record(record: dict[str, Any]) -> dict[str, Any]:
    """Check cross-links and safety declarations without scoring candidates."""
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    hypothesis_ids = {item["hypothesis_id"] for item in record["hypotheses"]}
    estimand_ids = {item["estimand_id"] for item in record["causal_estimands"]}
    prediction_ids = {item["prediction_id"] for item in record["predictions"]}
    measurement_ids = {
        item["measurement_id"] for item in record["operationalizations"]
    }
    analysis_ids = {
        item["analysis_id"] for item in record["analysis_plan"]["analyses"]
    }
    control_ids = {item["control_id"] for item in record["negative_controls"]}
    source_ids = set(record["evidence"]["source_ids"])

    used_sources = set(record["observation"]["source_ids"])
    for hypothesis in record["hypotheses"]:
        used_sources.update(hypothesis["source_ids"])
        errors.extend(
            _missing_references(
                hypothesis["prediction_ids"],
                prediction_ids,
                "UNKNOWN_PREDICTION_ID",
                hypothesis["hypothesis_id"],
            )
        )
        errors.extend(
            _missing_references(
                hypothesis["rival_hypothesis_ids"],
                hypothesis_ids,
                "UNKNOWN_RIVAL_HYPOTHESIS_ID",
                hypothesis["hypothesis_id"],
            )
        )
        if hypothesis["hypothesis_id"] in hypothesis["rival_hypothesis_ids"]:
            errors.append(
                issue("HYPOTHESIS_CANNOT_RIVAL_ITSELF", hypothesis["hypothesis_id"])
            )
        if len(hypothesis_ids) > 1 and not hypothesis["rival_hypothesis_ids"]:
            warnings.append(
                issue("RIVAL_HYPOTHESIS_LINK_MISSING", hypothesis["hypothesis_id"])
            )
    for operationalization in record["operationalizations"]:
        used_sources.update(operationalization["validity_evidence_source_ids"])
    errors.extend(
        _missing_references(
            sorted(used_sources),
            source_ids,
            "SOURCE_NOT_DECLARED_IN_EVIDENCE",
            "record.evidence.source_ids",
        )
    )

    if len(hypothesis_ids) == 1:
        warnings.append(issue("SINGLE_CANDIDATE_REQUIRES_RIVAL_REVIEW", "hypotheses"))

    for estimand in record["causal_estimands"]:
        errors.extend(
            _missing_references(
                estimand["linked_hypothesis_ids"],
                hypothesis_ids,
                "UNKNOWN_HYPOTHESIS_ID",
                estimand["estimand_id"],
            )
        )
    if (
        record["research_question"]["question_type"] == "causal"
        and not record["causal_estimands"]
    ):
        errors.append(issue("CAUSAL_QUESTION_REQUIRES_ESTIMAND", "causal_estimands"))

    predictions_by_hypothesis: Counter[str] = Counter()
    for prediction in record["predictions"]:
        prediction_id = prediction["prediction_id"]
        predictions_by_hypothesis[prediction["hypothesis_id"]] += 1
        errors.extend(
            _missing_references(
                [prediction["hypothesis_id"]],
                hypothesis_ids,
                "UNKNOWN_HYPOTHESIS_ID",
                prediction_id,
            )
        )
        errors.extend(
            _missing_references(
                prediction["rival_hypothesis_ids"],
                hypothesis_ids,
                "UNKNOWN_RIVAL_HYPOTHESIS_ID",
                prediction_id,
            )
        )
        errors.extend(
            _missing_references(
                prediction["measurement_ids"],
                measurement_ids,
                "UNKNOWN_MEASUREMENT_ID",
                prediction_id,
            )
        )
        errors.extend(
            _missing_references(
                prediction["analysis_ids"],
                analysis_ids,
                "UNKNOWN_ANALYSIS_ID",
                prediction_id,
            )
        )
        if prediction["hypothesis_id"] in prediction["rival_hypothesis_ids"]:
            errors.append(issue("PREDICTION_RIVAL_IS_FOCAL", prediction_id))
    for hypothesis_id in sorted(hypothesis_ids):
        if predictions_by_hypothesis[hypothesis_id] == 0:
            errors.append(issue("HYPOTHESIS_HAS_NO_PREDICTION", hypothesis_id))

    for alternative in record["alternative_explanations"]:
        errors.extend(
            _missing_references(
                alternative["linked_hypothesis_ids"],
                hypothesis_ids,
                "UNKNOWN_HYPOTHESIS_ID",
                alternative["alternative_id"],
            )
        )
        errors.extend(
            _missing_references(
                alternative["discriminating_prediction_ids"],
                prediction_ids,
                "UNKNOWN_PREDICTION_ID",
                alternative["alternative_id"],
            )
        )

    for null in record["null_hypotheses"]:
        errors.extend(
            _missing_references(
                null["linked_prediction_ids"],
                prediction_ids,
                "UNKNOWN_PREDICTION_ID",
                null["null_id"],
            )
        )

    for control in record["negative_controls"]:
        errors.extend(
            _missing_references(
                control["linked_prediction_ids"],
                prediction_ids,
                "UNKNOWN_PREDICTION_ID",
                control["control_id"],
            )
        )
    if not any(
        control["control_type"]
        in {"negative_exposure", "negative_outcome", "procedural_negative"}
        for control in record["negative_controls"]
    ):
        warnings.append(issue("NEGATIVE_CONTROL_TYPE_REVIEW_REQUIRED", "controls"))

    for analysis in record["analysis_plan"]["analyses"]:
        errors.extend(
            _missing_references(
                analysis["prediction_ids"],
                prediction_ids,
                "UNKNOWN_PREDICTION_ID",
                analysis["analysis_id"],
            )
        )
        errors.extend(
            _missing_references(
                analysis["estimand_ids"],
                estimand_ids,
                "UNKNOWN_ESTIMAND_ID",
                analysis["analysis_id"],
            )
        )

    for category, entries in record["risk_register"].items():
        if not entries:
            warnings.append(issue("RISK_CATEGORY_EMPTY_REQUIRES_RATIONALE", category))

    ethics = record["ethics_and_feasibility"]
    gate_values = {
        key: value for key, value in ethics.items() if key.endswith("_gate")
    }
    unresolved_gate_names = sorted(
        key
        for key, value in gate_values.items()
        if value in {"undetermined", "requires_review", "blocked"}
    )
    if unresolved_gate_names and not ethics["unresolved_blocks"]:
        errors.append(
            issue("UNRESOLVED_GATE_REQUIRES_BLOCK_RECORD", "ethics_and_feasibility")
        )
    if (
        any(value == "requires_review" for value in gate_values.values())
        and not ethics["required_reviews"]
    ):
        errors.append(
            issue("REQUIRED_REVIEW_LIST_MISSING", "ethics_and_feasibility")
        )
    if ethics["feasibility_status"] in {"undetermined", "infeasible", "blocked"}:
        unresolved_gate_names.append("feasibility_status")

    ai_use = record["ai_use"]
    if ai_use["sensitive_or_unpublished_data_sent_externally"]:
        errors.append(
            issue(
                "EXTERNAL_SENSITIVE_DATA_NOT_SUPPORTED",
                "ai_use.sensitive_or_unpublished_data_sent_externally",
            )
        )
    if not ai_use["local_policy_checked"]:
        errors.append(issue("LOCAL_AI_POLICY_NOT_CHECKED", "ai_use.local_policy_checked"))
    if not ai_use["citation_verification_required"]:
        errors.append(
            issue(
                "CITATION_VERIFICATION_MUST_BE_REQUIRED",
                "ai_use.citation_verification_required",
            )
        )
    if not ai_use["human_accountable"]:
        errors.append(
            issue("HUMAN_ACCOUNTABILITY_REQUIRED", "ai_use.human_accountable")
        )

    return {
        "schema_version": "2.0",
        "project_id": record["project_id"],
        "valid": not errors,
        "status": (
            "INVALID_RECORD"
            if errors
            else "VALID_BLOCKED_BY_GATES"
            if unresolved_gate_names
            else "VALID_FOR_HUMAN_REVIEW"
        ),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "hypotheses": len(hypothesis_ids),
            "causal_estimands": len(estimand_ids),
            "predictions": len(prediction_ids),
            "alternative_explanations": len(record["alternative_explanations"]),
            "null_hypotheses": len(record["null_hypotheses"]),
            "negative_controls": len(control_ids),
            "operationalizations": len(measurement_ids),
            "analyses": len(analysis_ids),
            "declared_sources": len(source_ids),
        },
        "identifiers": {
            "hypothesis_ids": sorted(hypothesis_ids),
            "estimand_ids": sorted(estimand_ids),
            "prediction_ids": sorted(prediction_ids),
            "measurement_ids": sorted(measurement_ids),
            "analysis_ids": sorted(analysis_ids),
            "control_ids": sorted(control_ids),
        },
        "unresolved_gate_fields": sorted(set(unresolved_gate_names)),
        "notice": (
            "This report validates schema, cross-references, and declared safety "
            "controls only. It does not verify evidence, scientific validity, "
            "novelty, ethics approval, causal identification, or hypothesis merit, "
            "and it does not rank or select candidates."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a bounded local hypothesis JSON record and emit identifiers, "
            "counts, and rule codes without scientific scoring."
        )
    )
    parser.add_argument("record", help="Local hypothesis record JSON")
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        record = load_hypothesis_record(read_json(args.record))
        report = validate_record(record)
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_prediction_matrix.py`

```python
#!/usr/bin/env python3
"""Validate a prediction/rival-hypothesis CSV without ranking candidates."""

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
    read_json,
    require_identifier,
    require_text,
    require_unique,
    split_identifiers,
    write_json_report,
)
from validate_hypothesis_schema import load_hypothesis_record, validate_record

FIELDS = (
    "prediction_id",
    "hypothesis_id",
    "rival_hypothesis_ids",
    "conditions",
    "observable",
    "expected_if_focal",
    "expected_if_rivals",
    "falsifier",
    "indeterminate_result",
    "boundary_conditions",
    "measurement_ids",
    "negative_control_ids",
    "analysis_ids",
    "uncertainty",
)


def load_matrix(raw_path: str) -> list[dict[str, Any]]:
    rows = read_csv_records(raw_path, fields=FIELDS)
    parsed: list[dict[str, Any]] = []
    prediction_ids: list[str] = []
    for line_number, row in enumerate(rows, start=2):
        context = f"matrix row {line_number}"
        prediction_id = require_identifier(
            row["prediction_id"], f"{context}.prediction_id"
        )
        prediction_ids.append(prediction_id)
        parsed.append(
            {
                "prediction_id": prediction_id,
                "hypothesis_id": require_identifier(
                    row["hypothesis_id"], f"{context}.hypothesis_id"
                ),
                "rival_hypothesis_ids": split_identifiers(
                    row["rival_hypothesis_ids"],
                    f"{context}.rival_hypothesis_ids",
                ),
                "conditions": require_text(
                    row["conditions"], f"{context}.conditions", minimum=5
                ),
                "observable": require_text(
                    row["observable"], f"{context}.observable", minimum=5
                ),
                "expected_if_focal": require_text(
                    row["expected_if_focal"],
                    f"{context}.expected_if_focal",
                    minimum=5,
                ),
                "expected_if_rivals": require_text(
                    row["expected_if_rivals"],
                    f"{context}.expected_if_rivals",
                    minimum=5,
                ),
                "falsifier": require_text(
                    row["falsifier"], f"{context}.falsifier", minimum=10
                ),
                "indeterminate_result": require_text(
                    row["indeterminate_result"],
                    f"{context}.indeterminate_result",
                    minimum=10,
                ),
                "boundary_conditions": require_text(
                    row["boundary_conditions"],
                    f"{context}.boundary_conditions",
                    minimum=5,
                ),
                "measurement_ids": split_identifiers(
                    row["measurement_ids"], f"{context}.measurement_ids"
                ),
                "negative_control_ids": split_identifiers(
                    row["negative_control_ids"],
                    f"{context}.negative_control_ids",
                ),
                "analysis_ids": split_identifiers(
                    row["analysis_ids"], f"{context}.analysis_ids"
                ),
                "uncertainty": require_text(
                    row["uncertainty"], f"{context}.uncertainty", minimum=10
                ),
            }
        )
    require_unique(prediction_ids, "prediction matrix")
    return parsed


def _normalized_expectation(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _unknown(
    values: list[str], allowed: set[str], code: str, field: str
) -> list[dict[str, str]]:
    return [
        issue(code, f"{field}:{value}")
        for value in sorted(set(values) - allowed)
    ]


def validate_matrix(
    rows: list[dict[str, Any]], record: dict[str, Any] | None = None
) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    hypothesis_counts: Counter[str] = Counter()

    record_ids: dict[str, set[str]] | None = None
    if record is not None:
        record_report = validate_record(record)
        if not record_report["valid"]:
            raise ValidationError(
                "optional hypothesis record must pass schema validation first"
            )
        record_ids = {
            "hypotheses": {
                item["hypothesis_id"] for item in record["hypotheses"]
            },
            "predictions": {
                item["prediction_id"] for item in record["predictions"]
            },
            "measurements": {
                item["measurement_id"] for item in record["operationalizations"]
            },
            "controls": {
                item["control_id"] for item in record["negative_controls"]
            },
            "analyses": {
                item["analysis_id"] for item in record["analysis_plan"]["analyses"]
            },
        }

    for row in rows:
        prediction_id = row["prediction_id"]
        hypothesis_id = row["hypothesis_id"]
        hypothesis_counts[hypothesis_id] += 1
        if hypothesis_id in row["rival_hypothesis_ids"]:
            errors.append(issue("FOCAL_HYPOTHESIS_LISTED_AS_RIVAL", prediction_id))
        if (
            _normalized_expectation(row["expected_if_focal"])
            == _normalized_expectation(row["expected_if_rivals"])
        ):
            errors.append(issue("FOCAL_AND_RIVAL_EXPECTATIONS_IDENTICAL", prediction_id))
        if not row["negative_control_ids"]:
            warnings.append(issue("NEGATIVE_CONTROL_LINK_MISSING", prediction_id))

        if record_ids is not None:
            errors.extend(
                _unknown(
                    [hypothesis_id],
                    record_ids["hypotheses"],
                    "UNKNOWN_HYPOTHESIS_ID",
                    prediction_id,
                )
            )
            errors.extend(
                _unknown(
                    row["rival_hypothesis_ids"],
                    record_ids["hypotheses"],
                    "UNKNOWN_RIVAL_HYPOTHESIS_ID",
                    prediction_id,
                )
            )
            errors.extend(
                _unknown(
                    [prediction_id],
                    record_ids["predictions"],
                    "UNKNOWN_PREDICTION_ID",
                    prediction_id,
                )
            )
            errors.extend(
                _unknown(
                    row["measurement_ids"],
                    record_ids["measurements"],
                    "UNKNOWN_MEASUREMENT_ID",
                    prediction_id,
                )
            )
            errors.extend(
                _unknown(
                    row["negative_control_ids"],
                    record_ids["controls"],
                    "UNKNOWN_CONTROL_ID",
                    prediction_id,
                )
            )
            errors.extend(
                _unknown(
                    row["analysis_ids"],
                    record_ids["analyses"],
                    "UNKNOWN_ANALYSIS_ID",
                    prediction_id,
                )
            )
            record_prediction = next(
                (
                    item
                    for item in record["predictions"]
                    if item["prediction_id"] == prediction_id
                ),
                None,
            )
            if (
                record_prediction is not None
                and record_prediction["hypothesis_id"] != hypothesis_id
            ):
                errors.append(
                    issue("PREDICTION_HYPOTHESIS_MISMATCH", prediction_id)
                )

    return {
        "schema_version": "2.0",
        "valid": not errors,
        "status": "INVALID_MATRIX" if errors else "VALID_FOR_HUMAN_REVIEW",
        "errors": errors,
        "warnings": warnings,
        "prediction_count": len(rows),
        "hypothesis_prediction_counts": dict(sorted(hypothesis_counts.items())),
        "prediction_ids": sorted(row["prediction_id"] for row in rows),
        "record_cross_check_performed": record is not None,
        "notice": (
            "This report checks CSV structure, identifiers, declared contrasts, "
            "and optional cross-links. It cannot determine whether a prediction "
            "is scientifically discriminating, sufficiently precise, or likely, "
            "and it never ranks or selects a hypothesis."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a bounded local prediction/rival CSV and emit identifiers "
            "and rule codes without scientific scoring."
        )
    )
    parser.add_argument("matrix", help="Local prediction/rival matrix CSV")
    parser.add_argument(
        "--record", help="Optional local hypothesis record JSON for cross-checks"
    )
    parser.add_argument("-o", "--output", help="Optional local JSON report")
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output file"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        record = (
            load_hypothesis_record(read_json(args.record)) if args.record else None
        )
        report = validate_matrix(load_matrix(args.matrix), record)
        write_json_report(report, args.output, force=args.force)
        return 0 if report["valid"] else 1
    except ValidationError as exc:
        return error_exit(exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `assets/evidence_ledger_template.csv`

```csv
source_id,claim_ids,title,authors_or_organization,publication_date,source_type,identifier,url,accessed_on,relation,study_design_or_document_type,limitations,notes
SRC-SYN-001,OBS1;H1;H2;P1;P2,"Synthetic source record for schema demonstration","Synthetic Example Group",2026-07-23,other,SYNTHETIC:HG-001,https://example.invalid/hypothesis-generation/synthetic-source,2026-07-23,contextual,"Synthetic documentation record","Not scientific evidence; does not support a real-world claim","Replace this row with verified sources and preserve challenging as well as supportive evidence"
```

### `assets/falsification_controls_template.json`

```json
{
  "schema_version": "2.0",
  "checklist_id": "FC-SYN-001",
  "record_id": "HG-SYN-001",
  "hypotheses": [
    {
      "hypothesis_id": "H1",
      "candidate_status": "candidate",
      "assumptions": [
        "Synthetic assignment, manipulation, and measurements operate as declared."
      ],
      "boundary_conditions": [
        "Synthetic eligible units over one prespecified interval."
      ],
      "falsifier": {
        "prediction_id": "P1",
        "conditions": "The manipulation and measurement checks pass and uncertainty is small enough to distinguish the patterns.",
        "observable": "Intermediate M and outcome Y measured at prespecified times.",
        "incompatible_result": "Outcome Y changes without the prespecified change in intermediate M.",
        "assumption_failure_checks": [
          "Verify assignment, manipulation, calibration, missingness, and temporal ordering before interpreting incompatibility."
        ]
      },
      "discriminating_tests": [
        {
          "test_id": "DT1",
          "rival_hypothesis_id": "H2",
          "focal_expected": "Intermediate M changes before outcome Y with no negative-control reference shift.",
          "rival_expected": "Outcome Y and the negative-control reference shift together without the prespecified intermediate change.",
          "indeterminate_result": "Both intermediate M and the negative-control reference change, so mixed mechanisms or bias remain possible."
        }
      ],
      "nulls": [
        {
          "null_id": "N1",
          "statement": "The population mean of outcome Y is equal under X and comparator at the prespecified horizon.",
          "analysis_id": "A1",
          "interpretation_limit": "Failure to reject is not equivalence, absence of effect, or proof of the rival."
        }
      ],
      "controls": [
        {
          "control_id": "NC1",
          "control_type": "negative_outcome",
          "rationale": "The synthetic reference cannot be changed by process M but shares the acquisition workflow.",
          "expected_result": "No assignment-linked reference difference after the prespecified acquisition adjustment.",
          "failure_implication": "Investigate acquisition, selection, or analysis bias before a causal interpretation."
        },
        {
          "control_id": "PC1",
          "control_type": "positive_control",
          "rationale": "A known synthetic calibration input checks whether the outcome procedure detects a declared change.",
          "expected_result": "The calibration input is recovered within the locked tolerance.",
          "failure_implication": "The target test is not interpretable until measurement performance is restored."
        }
      ],
      "outcome_interpretation": {
        "consistent_with_candidate": "The focal pattern is observed, the rival pattern is not, controls pass, and uncertainty is compatible with the prespecified target.",
        "challenges_candidate": "The incompatible result is observed while manipulation, measurements, and declared assumptions remain credible.",
        "supports_neither_or_mixed": "The result matches neither pattern, both patterns occur, or an assumption/control fails."
      },
      "human_review_status": "pending"
    },
    {
      "hypothesis_id": "H2",
      "candidate_status": "candidate",
      "assumptions": [
        "Any synthetic acquisition drift affects the outcome and reference through a shared pathway."
      ],
      "boundary_conditions": [
        "Synthetic acquisition periods covered by the declared reference process."
      ],
      "falsifier": {
        "prediction_id": "P2",
        "conditions": "Independent calibration periods overlap both assigned conditions and reference measurement is valid.",
        "observable": "Synthetic negative-control reference and outcome Y by acquisition period.",
        "incompatible_result": "The reference remains stable while outcome Y changes reproducibly by assignment.",
        "assumption_failure_checks": [
          "Verify reference sensitivity, batch overlap, calibration, and missing acquisition records."
        ]
      },
      "discriminating_tests": [
        {
          "test_id": "DT2",
          "rival_hypothesis_id": "H1",
          "focal_expected": "Reference and outcome shift together by acquisition period.",
          "rival_expected": "Outcome changes by assignment without a reference shift and after intermediate M changes.",
          "indeterminate_result": "Acquisition period is confounded with assignment, so the rivals cannot be separated."
        }
      ],
      "nulls": [
        {
          "null_id": "N2",
          "statement": "The negative-control reference mean is equal across acquisition periods.",
          "analysis_id": "A2",
          "interpretation_limit": "Failure to reject does not prove absence of drift when precision or reference sensitivity is insufficient."
        }
      ],
      "controls": [
        {
          "control_id": "NC1",
          "control_type": "negative_outcome",
          "rationale": "The reference is outside process M while sharing the acquisition pathway.",
          "expected_result": "A drift explanation predicts a shared acquisition-linked shift.",
          "failure_implication": "A stable, sensitive reference challenges the drift candidate."
        }
      ],
      "outcome_interpretation": {
        "consistent_with_candidate": "Outcome and reference shifts align by acquisition period under valid measurement.",
        "challenges_candidate": "The stable reference and independent calibration are incompatible with the declared shared-drift process.",
        "supports_neither_or_mixed": "Assignment and acquisition cannot be separated or both mechanism and drift patterns occur."
      },
      "human_review_status": "pending"
    }
  ]
}
```

### `assets/hypothesis_record_template.json`

```json
{
  "schema_version": "2.0",
  "project_id": "HG-SYN-001",
  "status": "draft",
  "updated_on": "2026-07-23",
  "human_owner": "Accountable human investigator",
  "observation": {
    "statement": "In a synthetic demonstration dataset, units measured after condition X had a different mean value of outcome Y than units measured after the comparator condition.",
    "provenance": "Synthetic demonstration only; no human, animal, clinical, proprietary, or security-sensitive data.",
    "source_ids": [
      "SRC-SYN-001"
    ],
    "uncertainties": [
      "The synthetic pattern could reflect the generating process, selection, measurement, or random variation."
    ]
  },
  "research_question": {
    "statement": "In the synthetic target system, what is the effect of assigning condition X rather than the comparator on outcome Y after one measurement interval?",
    "framework": "PICO",
    "question_type": "causal",
    "population_or_system": "Synthetic independent units meeting the declared eligibility rule",
    "intervention_or_exposure": "Assignment to synthetic condition X",
    "comparator": "Assignment to the synthetic comparator condition",
    "outcome": "Validated synthetic outcome Y",
    "timeframe": "One prespecified measurement interval"
  },
  "hypotheses": [
    {
      "hypothesis_id": "H1",
      "statement": "Condition X changes outcome Y through the proposed synthetic process M.",
      "mechanism": "Condition X changes intermediate M before outcome Y is measured.",
      "status": "candidate",
      "source_ids": [
        "SRC-SYN-001"
      ],
      "assumptions": [
        "The synthetic assignment and measurement procedures operate as declared."
      ],
      "boundary_conditions": [
        "The candidate is limited to the declared synthetic units and one-interval horizon."
      ],
      "uncertainties": [
        "The intermediate may be a marker rather than a mediator."
      ],
      "prediction_ids": [
        "P1"
      ],
      "rival_hypothesis_ids": [
        "H2"
      ]
    },
    {
      "hypothesis_id": "H2",
      "statement": "The observed difference in outcome Y is produced by a synthetic measurement drift rather than process M.",
      "mechanism": "A time-linked offset changes the recorded outcome without changing the target construct.",
      "status": "candidate",
      "source_ids": [
        "SRC-SYN-001"
      ],
      "assumptions": [
        "The synthetic measurement offset is not removed by calibration."
      ],
      "boundary_conditions": [
        "The candidate applies only to measurements from the affected synthetic acquisition period."
      ],
      "uncertainties": [
        "The size and stability of any offset are unknown."
      ],
      "prediction_ids": [
        "P2"
      ],
      "rival_hypothesis_ids": [
        "H1"
      ]
    }
  ],
  "causal_estimands": [
    {
      "estimand_id": "E1",
      "linked_hypothesis_ids": [
        "H1"
      ],
      "population": "Synthetic eligible units",
      "intervention_or_exposure": "Assignment to condition X",
      "comparator": "Assignment to comparator",
      "outcome": "Outcome Y measured with method M-OUTCOME",
      "time_horizon": "One measurement interval",
      "population_summary": "Difference in population mean outcome Y",
      "intercurrent_event_strategy": "Not applicable in the synthetic demonstration",
      "identification_assumptions": [
        "Random assignment, no interference, consistent treatment versions, and valid outcome measurement."
      ]
    }
  ],
  "predictions": [
    {
      "prediction_id": "P1",
      "hypothesis_id": "H1",
      "statement": "Under matched acquisition conditions, assignment to X will precede a change in intermediate M and then outcome Y.",
      "observable": "Ordered changes in intermediate M and outcome Y",
      "conditions": "Synthetic units are randomly assigned and measured with calibrated instruments.",
      "expected_pattern": "Intermediate M changes before outcome Y in X but not comparator units.",
      "falsifier": "Outcome Y changes without the prespecified change in intermediate M under a successful manipulation and valid measurements.",
      "rival_hypothesis_ids": [
        "H2"
      ],
      "measurement_ids": [
        "M-INTERMEDIATE",
        "M-OUTCOME"
      ],
      "analysis_ids": [
        "A1"
      ]
    },
    {
      "prediction_id": "P2",
      "hypothesis_id": "H2",
      "statement": "A reference quantity measured in the same acquisition period will show a similar offset even though process M cannot affect it.",
      "observable": "Offset in the negative-control reference quantity",
      "conditions": "The same acquisition and calibration workflow is used.",
      "expected_pattern": "The reference quantity and outcome Y shift together by acquisition period.",
      "falsifier": "The reference quantity remains stable while outcome Y changes reproducibly across independently calibrated periods.",
      "rival_hypothesis_ids": [
        "H1"
      ],
      "measurement_ids": [
        "M-NEGATIVE-CONTROL",
        "M-OUTCOME"
      ],
      "analysis_ids": [
        "A2"
      ]
    }
  ],
  "alternative_explanations": [
    {
      "alternative_id": "ALT1",
      "statement": "Synthetic selection into the analyzed set creates the observed difference.",
      "linked_hypothesis_ids": [
        "H1",
        "H2"
      ],
      "risk_types": [
        "selection_bias"
      ],
      "discriminating_prediction_ids": [
        "P1",
        "P2"
      ]
    }
  ],
  "null_hypotheses": [
    {
      "null_id": "N1",
      "statement": "The population mean of outcome Y is equal under assignment to X and comparator at the prespecified horizon.",
      "linked_prediction_ids": [
        "P1"
      ],
      "rejection_or_compatibility_rule": "Use the prespecified interval estimate and decision rule in analysis A1; do not equate failure to reject with equivalence."
    },
    {
      "null_id": "N2",
      "statement": "The synthetic negative-control reference mean is equal across acquisition periods.",
      "linked_prediction_ids": [
        "P2"
      ],
      "rejection_or_compatibility_rule": "Use analysis A2 as a bias diagnostic; failure to reject does not prove absence of drift when precision or reference sensitivity is insufficient."
    }
  ],
  "negative_controls": [
    {
      "control_id": "NC1",
      "control_type": "negative_outcome",
      "rationale": "The reference quantity cannot be changed by process M but shares the synthetic acquisition workflow.",
      "expected_result": "No difference by assigned condition after accounting for acquisition period.",
      "failure_implication": "A non-null control result raises concern about acquisition, selection, or analysis bias.",
      "linked_prediction_ids": [
        "P2"
      ]
    }
  ],
  "operationalizations": [
    {
      "measurement_id": "M-INTERMEDIATE",
      "construct": "Synthetic intermediate M",
      "variable": "m_value",
      "role": "mediator",
      "operational_definition": "Calibrated continuous synthetic measurement at the prespecified early time.",
      "instrument_or_method": "Deterministic synthetic measurement procedure",
      "unit": "synthetic units",
      "timing": "Early prespecified time",
      "population_or_system": "Synthetic eligible units",
      "validity_evidence_source_ids": [
        "SRC-SYN-001"
      ],
      "reliability_plan": "Repeat the deterministic check on an independent synthetic batch.",
      "missingness_plan": "Report missingness by assignment and use the prespecified sensitivity analysis.",
      "blinding_or_masking": "Synthetic analyst label is masked until validation completes.",
      "threshold_rationale": "No threshold; analyze the continuous measurement."
    },
    {
      "measurement_id": "M-OUTCOME",
      "construct": "Synthetic outcome Y",
      "variable": "y_value",
      "role": "outcome",
      "operational_definition": "Calibrated continuous synthetic outcome at one interval.",
      "instrument_or_method": "Deterministic synthetic measurement procedure",
      "unit": "synthetic units",
      "timing": "One prespecified measurement interval",
      "population_or_system": "Synthetic eligible units",
      "validity_evidence_source_ids": [
        "SRC-SYN-001"
      ],
      "reliability_plan": "Verify calibration and repeatability before unmasking assignment.",
      "missingness_plan": "Report reasons and analyze under the prespecified primary and sensitivity assumptions.",
      "blinding_or_masking": "Outcome acquisition and validation are masked to assignment.",
      "threshold_rationale": "No threshold; estimate the continuous mean contrast."
    },
    {
      "measurement_id": "M-NEGATIVE-CONTROL",
      "construct": "Synthetic reference quantity",
      "variable": "reference_value",
      "role": "negative_control",
      "operational_definition": "Stable synthetic reference measured in the same acquisition workflow.",
      "instrument_or_method": "Deterministic synthetic reference procedure",
      "unit": "synthetic reference units",
      "timing": "Concurrent with outcome Y",
      "population_or_system": "Synthetic acquisition batches",
      "validity_evidence_source_ids": [
        "SRC-SYN-001"
      ],
      "reliability_plan": "Check repeatability across synthetic batches.",
      "missingness_plan": "Treat a missing reference as an acquisition-quality failure.",
      "blinding_or_masking": "Reference processing is independent of assignment labels.",
      "threshold_rationale": "Use the prespecified calibration tolerance."
    }
  ],
  "analysis_plan": {
    "analyses": [
      {
        "analysis_id": "A1",
        "prediction_ids": [
          "P1"
        ],
        "estimand_ids": [
          "E1"
        ],
        "analysis_population": "All randomized synthetic eligible units under the declared estimand strategy",
        "method": "Estimate the prespecified mean contrast with its uncertainty interval.",
        "effect_or_summary_measure": "Difference in population means",
        "uncertainty_method": "Prespecified interval estimate under the declared independent-unit assumptions",
        "missing_data_plan": "Primary declared assumption plus a bounded sensitivity analysis",
        "multiplicity_plan": "A1 is the sole confirmatory contrast; all additional contrasts are exploratory.",
        "sensitivity_analyses": [
          "Repeat under the prespecified alternative missingness assumption."
        ],
        "decision_rule": "Interpret compatibility with predicted patterns and rivals; do not select a hypothesis automatically.",
        "exploratory_or_confirmatory": "confirmatory"
      },
      {
        "analysis_id": "A2",
        "prediction_ids": [
          "P2"
        ],
        "estimand_ids": [],
        "analysis_population": "All synthetic acquisition batches with valid reference measurements",
        "method": "Estimate reference shifts by acquisition period and assigned condition.",
        "effect_or_summary_measure": "Difference in reference means",
        "uncertainty_method": "Prespecified interval estimate",
        "missing_data_plan": "Report and exclude acquisition failures according to the locked quality rule.",
        "multiplicity_plan": "Negative-control analysis is interpreted as a bias diagnostic, not a candidate-selection score.",
        "sensitivity_analyses": [
          "Repeat after excluding the prespecified failed-calibration batch category."
        ],
        "decision_rule": "A non-null reference shift triggers investigation and limits causal interpretation.",
        "exploratory_or_confirmatory": "confirmatory"
      }
    ],
    "harking_control": "Freeze this record before viewing the target synthetic outcomes and label later candidates or analyses exploratory.",
    "deviation_reporting": "Preserve the original plan and log each deviation with date, rationale, decision owner, result-awareness status, and interpretive impact."
  },
  "evidence": {
    "ledger_path": "local-evidence-ledger.csv",
    "source_ids": [
      "SRC-SYN-001"
    ],
    "search_boundary_id": "SEARCH-SYN-001",
    "evidence_limitations": [
      "The bundled row is synthetic and demonstrates structure only."
    ]
  },
  "risk_register": {
    "confounding": [
      "Synthetic assignment failure or implementation differences could act as common causes."
    ],
    "selection_bias": [
      "Post-assignment exclusion could make analyzed groups non-comparable."
    ],
    "collider_bias": [
      "Restricting analysis to a jointly caused quality indicator could open bias."
    ],
    "reverse_causation": [
      "Temporal ordering is built into the synthetic design but must be verified."
    ],
    "measurement_bias": [
      "Acquisition-period drift could change recorded outcome Y."
    ],
    "other": [
      "Random variation and model misspecification remain possible."
    ]
  },
  "ethics_and_feasibility": {
    "human_subjects_gate": "not_applicable",
    "animal_research_gate": "not_applicable",
    "biosafety_gate": "not_applicable",
    "dual_use_gate": "not_applicable",
    "regulatory_gate": "not_applicable",
    "data_governance_gate": "approved",
    "feasibility_status": "feasible_for_planning",
    "required_reviews": [],
    "unresolved_blocks": []
  },
  "ai_use": {
    "used": false,
    "sensitive_or_unpublished_data_sent_externally": false,
    "local_policy_checked": true,
    "citation_verification_required": true,
    "human_accountable": true,
    "diversity_mitigation": "Generate independent rivals before any authorized AI-assisted expansion and retain human-origin candidates."
  }
}
```

### `assets/operationalization_template.json`

```json
{
  "schema_version": "2.0",
  "checklist_id": "OP-SYN-001",
  "record_id": "HG-SYN-001",
  "human_reviewer": "Qualified measurement reviewer pending",
  "items": [
    {
      "measurement_id": "M-OUTCOME",
      "applicability": "applicable",
      "construct_defined": true,
      "variable_role": "outcome",
      "operational_definition_recorded": true,
      "population_scope_recorded": true,
      "unit_or_categories_recorded": true,
      "timing_recorded": true,
      "instrument_or_method_recorded": true,
      "validity_evidence_source_ids": [
        "SRC-SYN-001"
      ],
      "validity_applicability_reviewed": false,
      "reliability_or_repeatability_plan_recorded": true,
      "calibration_or_quality_control_status": "planned",
      "measurement_invariance_or_comparability_status": "unresolved",
      "masking_status": "planned",
      "missingness_plan_recorded": true,
      "threshold_or_cutpoint_status": "not_applicable",
      "limitations_recorded": true,
      "human_review_status": "pending",
      "note": "Synthetic example. A qualified human must determine whether the validity evidence applies to the target system."
    },
    {
      "measurement_id": "M-NEGATIVE-CONTROL",
      "applicability": "applicable",
      "construct_defined": true,
      "variable_role": "negative_control",
      "operational_definition_recorded": true,
      "population_scope_recorded": true,
      "unit_or_categories_recorded": true,
      "timing_recorded": true,
      "instrument_or_method_recorded": true,
      "validity_evidence_source_ids": [
        "SRC-SYN-001"
      ],
      "validity_applicability_reviewed": false,
      "reliability_or_repeatability_plan_recorded": true,
      "calibration_or_quality_control_status": "planned",
      "measurement_invariance_or_comparability_status": "not_applicable",
      "masking_status": "not_applicable",
      "missingness_plan_recorded": true,
      "threshold_or_cutpoint_status": "planned",
      "limitations_recorded": true,
      "human_review_status": "pending",
      "note": "Synthetic example. Confirm that the target mechanism cannot affect this control and that relevant bias pathways are shared."
    }
  ]
}
```

### `assets/prediction_rival_matrix_template.csv`

```csv
prediction_id,hypothesis_id,rival_hypothesis_ids,conditions,observable,expected_if_focal,expected_if_rivals,falsifier,indeterminate_result,boundary_conditions,measurement_ids,negative_control_ids,analysis_ids,uncertainty
P1,H1,H2,"Random assignment, successful manipulation, calibrated measurements, and masked validation","Ordering of synthetic intermediate M and outcome Y","Intermediate M changes before outcome Y in condition X","H2 predicts no condition-specific intermediate change and a shift shared with the reference quantity","Outcome Y changes without the prespecified intermediate change after successful manipulation and valid measurement","Manipulation or measurement check fails, or uncertainty is too large to distinguish the patterns","Synthetic eligible units over one prespecified interval",M-INTERMEDIATE;M-OUTCOME,NC1,A1,"Magnitude is not assumed; the planned interval and measurement resolution determine whether patterns are distinguishable"
P2,H2,H1,"Matched synthetic acquisition and calibration workflow","Shift in the synthetic negative-control reference quantity","Reference quantity and outcome Y shift together by acquisition period","H1 predicts outcome Y changes without a corresponding reference shift","Reference quantity is stable across independently calibrated periods while outcome Y changes reproducibly by assignment","Reference measurement fails or acquisition periods do not overlap assigned conditions","Synthetic acquisition batches covered by the declared calibration process",M-NEGATIVE-CONTROL;M-OUTCOME,NC1,A2,"A control shift can have causes other than the stated measurement-drift rival"
```

### `assets/preregistration_scaffold_template.md`

# Preregistration scaffold: {{PROJECT_ID}}

> **UNREGISTERED DRAFT — NOT AN APPROVAL OR SCIENTIFIC ENDORSEMENT**
>
> Generated locally on {{GENERATED_ON}} from a validated structural record. Complete repository-specific fields, obtain required human/ethics/safety/regulatory review, and verify every statement before registration.

## 1. Administrative record

- Project ID: {{PROJECT_ID}}
- Accountable human owner: {{HUMAN_OWNER}}
- Record status: {{RECORD_STATUS}}
- Record updated: {{UPDATED_ON}}
- Registration repository and identifier: [TO COMPLETE]
- Registration timestamp: [TO COMPLETE]
- Study status and prior access to target data: [TO COMPLETE]
- Roles, funding, conflicts, sponsor role: [TO COMPLETE]

## 2. Authorization and oversight gates

{{ETHICS_AND_FEASIBILITY}}

- Human/animal/biosafety/dual-use/data/regulatory determinations and identifiers: [TO COMPLETE]
- Local policy and jurisdiction checked on: [TO COMPLETE]
- Unresolved work must not begin until the responsible authority clears it.

## 3. Search boundary and evidence

{{EVIDENCE_BOUNDARY}}

- Attach the completed search-boundary record and evidence ledger.
- “Not located within this boundary” does not establish universal absence or novelty.
- Verify every citation and claim-to-source link against the primary source.

## 4. Frozen observation

{{OBSERVATION}}

- Units, preprocessing, exclusions, missingness, and uncertainty: [TO COMPLETE]
- Whether expected or selected after inspection: [TO COMPLETE]

## 5. Research question and claim type

{{RESEARCH_QUESTION}}

## 6. Candidate hypotheses and mechanisms

{{HYPOTHESES}}

All listed hypotheses remain candidates. This scaffold does not rank or select one.

## 7. Causal estimand(s), if applicable

{{ESTIMANDS}}

- Target-trial/design analogue and identification logic: [TO COMPLETE]
- Confounding, selection, collider, measurement, reverse-causation, positivity, and interference assumptions: [TO COMPLETE]

## 8. Predictions, rivals, and falsification

{{PREDICTIONS}}

- Indeterminate and mixed-mechanism outcomes: [TO COMPLETE]
- Assumption/manipulation checks required before interpreting a challenge: [TO COMPLETE]

## 9. Null hypotheses and controls

{{NULLS_AND_CONTROLS}}

- Positive/procedural-control details: [TO COMPLETE]
- Why each negative control cannot operate through the target mechanism and which bias pathways it shares: [TO COMPLETE]

## 10. Operationalization and measurement validity

{{OPERATIONALIZATIONS}}

- Validity applicability, reliability/repeatability, calibration, detection limits, masking, missingness, invariance/comparability, and limitations: [TO COMPLETE]

## 11. Design

- Target population/system and sampling frame: [TO COMPLETE]
- Experimental/observational unit and analysis unit: [TO COMPLETE]
- Eligibility, recruitment/selection, and exclusions: [TO COMPLETE]
- Intervention/exposure and comparator versions: [TO COMPLETE]
- Allocation, randomization, concealment, and masking: [TO COMPLETE]
- Measurement schedule and quality control: [TO COMPLETE]
- Sample-size, precision, or information rationale with sensitivity to assumptions: [TO COMPLETE]
- Stopping, attrition, and missing-outcome plan: [TO COMPLETE]
- Replication, transport, and external-validation plan: [TO COMPLETE]

## 12. Analysis plan

{{ANALYSES}}

- Software, environment, versions, and seeds where applicable: [TO COMPLETE]
- Assumption diagnostics and model checks: [TO COMPLETE]
- Full multiplicity family across hypotheses, outcomes, timepoints, subgroups, models, and looks: [TO COMPLETE]
- Confirmatory versus exploratory outputs: [TO COMPLETE]

## 13. Data, code, materials, and retention

- Provenance and versioning: [TO COMPLETE]
- Data/code/material availability or justified restriction: [TO COMPLETE]
- Consent, privacy, community governance, intellectual property, export-control, biosafety, and dual-use limits: [TO COMPLETE]
- Approved storage, access, retention, and deletion: [TO COMPLETE]

## 14. AI and tool assistance

{{AI_USE}}

- Named tools/versions and material influence: [TO COMPLETE IF PERMITTED]
- Verification and disclosure plan: [TO COMPLETE]
- Sensitive or unpublished information must remain local unless explicitly authorized for a named service and scope.

## 15. Deviations and amendments

{{DEVIATION_PLAN}}

For each deviation record:

- date;
- affected section and IDs;
- original plan;
- change and rationale;
- decision owner;
- whether target results were known;
- expected interpretive impact;
- whether the original analysis will still be reported.

## 16. Human sign-off

- Domain expert: [NAME / DATE / STATUS]
- Measurement expert: [NAME / DATE / STATUS]
- Methodologist/statistician: [NAME / DATE / STATUS]
- Ethics/safety/data/regulatory authorities as applicable: [NAME / DATE / STATUS]
- Accountable investigator: [NAME / DATE / STATUS]

No signature turns a hypothesis into fact. Interpret results with uncertainty, rivals, boundary conditions, controls, and replication evidence.

### `assets/search_boundary_template.json`

```json
{
  "schema_version": "2.0",
  "search_boundary_id": "SEARCH-SYN-001",
  "searched_on": "2026-07-23",
  "searched_by": "Accountable human or authorized research assistant",
  "purpose": "Demonstrate a bounded, traceable search record for a synthetic hypothesis package.",
  "databases_or_indexes": [
    "Synthetic index for format demonstration"
  ],
  "queries": [
    "synthetic condition X outcome Y mechanism",
    "synthetic condition X alternative explanation measurement drift"
  ],
  "date_limits": "No date restriction in the synthetic demonstration.",
  "language_limits": "Synthetic English records only.",
  "inclusion_scope": "Sources bearing on the observation, candidate process, measurement, rivals, and methods.",
  "exclusion_scope": "No real scientific sources were screened in this synthetic template.",
  "known_limitations": [
    "This is a schema example and cannot support novelty, priority, or an evidence claim."
  ],
  "last_result_screened_or_stop_rule": "Replace with the actual result depth, saturation rule, or protocol completion statement.",
  "novelty_status": "not_assessed"
}
```

### `assets/source_ledger.csv`

```csv
source_id,organization,title,version_or_date,source_type,url,verified_on,status,notes
SRC-NIH-RIGOR,National Institutes of Health,Guidance: Rigor and Reproducibility in Grant Applications,Page updated 2024-10-16,official guidance,https://grants.nih.gov/policy-and-compliance/policy-topics/reproducibility/guidance,2026-07-23,current_official,"Scientific premise, rigorous design, biological variables, resource authentication, and transparency"
SRC-NIH-REPLICATION,National Institutes of Health,Strengthening Replication and Reproducibility of NIH-funded Research,Page reviewed 2026-06-22,official initiative,https://www.nih.gov/replicationandreproducibility,2026-07-23,current_official,"Agency-wide replication and reproducibility initiative; policy implementation may continue to evolve"
SRC-COCHRANE-PICO,Cochrane,Handbook Chapter 2: Determining the scope of the review and the questions it will address,Current handbook chapter,official handbook,https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-02,2026-07-23,current_official,"PICO for intervention reviews, protocol-stage definition, synthesis-level distinctions, and stakeholder input"
SRC-PICO-ORIGINAL,Richardson et al.,The well-built clinical question: a key to evidence-based decisions,Published 1995-11-01,primary methods article,https://www.acpjournals.org/doi/10.7326/ACPJC-1995-123-3-A12,2026-07-23,foundational_primary,"Original four-part well-built clinical-question article; DOI 10.7326/ACPJC-1995-123-3-A12"
SRC-FINER-1988,Hulley and Cummings,Designing Clinical Research: An Epidemiologic Approach,First edition 1988,foundational book metadata,https://books.google.com/books/about/Designing_Clinical_Research.html?id=hKdpAAAAMAAJ,2026-07-23,historical_metadata_limited,"Earliest FINER-attributed source located in this search; bibliographic preview confirms edition metadata but the search did not prove first printed use or coinage"
SRC-FINER-CURRENT,Werner and Willis,Back to the basics: guidance for formulating good research questions,Published 2023-10-12,current methods article,https://pmc.ncbi.nlm.nih.gov/articles/PMC11129835/,2026-07-23,current_primary,"Current discussion of FINER as a practical question-appraisal framework; novelty requires literature review"
SRC-PLATT-1964,John R. Platt,Strong Inference,Published 1964-10-16,primary methods essay,https://www.science.org/doi/10.1126/science.146.3642.347,2026-07-23,foundational_primary,"Multiple alternatives, crucial experiments, and iterative exclusion; DOI 10.1126/science.146.3642.347"
SRC-COS-PREREG,Center for Open Science,Preregistration,Current official page,official guidance,https://www.cos.io/initiatives/prereg,2026-07-23,current_official,"Separates planned from unplanned work and requires transparent changes; exploration remains valid"
SRC-OSF-REG,Center for Open Science / OSF,Welcome to Registrations and Preregistrations,Current 2026 help page,official implementation guidance,https://help.osf.io/article/330-welcome-to-registrations,2026-07-23,current_official,"Timestamped plans, template guidance, analysis details, and anticipated deviations"
SRC-COS-RR,Center for Open Science,Registered Reports,Current official initiative page,official guidance,https://www.cos.io/initiatives/registered-reports,2026-07-23,current_official,"Results-blind protocol review and in-principle acceptance; verify the target journal policy"
SRC-SPIRIT-2025,SPIRIT-CONSORT Group,SPIRIT 2025 statement: updated guideline for protocols of randomised trials,Published 2025-04-28,primary reporting guideline,https://www.bmj.com/content/389/bmj-2024-081477,2026-07-23,current_primary,"34 minimum protocol items; supersedes SPIRIT 2013; DOI 10.1136/bmj-2024-081477"
SRC-CONSORT-2025,SPIRIT-CONSORT Group,CONSORT 2025 statement: updated guideline for reporting randomised trials,Published 2025-04-14,primary reporting guideline,https://www.bmj.com/content/389/bmj-2024-081123,2026-07-23,current_primary,"30-item result-reporting guideline with open-science, harms, outcomes, intervention, and change-reporting updates"
SRC-ICH-E9R1,International Council for Harmonisation,ICH E9(R1) Addendum on Estimands and Sensitivity Analysis in Clinical Trials,Step 4 2019; implemented 2020,official statistical guidance,https://database.ich.org/sites/default/files/E9-R1_Step4_Guideline_2019_1203.pdf,2026-07-23,current_official,"Defines estimand as the precise treatment-effect target and aligns planning, design, analysis, sensitivity, and interpretation"
SRC-WHATIF,Hernán and Robins,Causal Inference: What If,2020 citation; latest author-hosted revision linked 2025-11-21,foundational methods book,https://miguelhernan.org/whatifbook,2026-07-23,current_author_source,"Causal questions, counterfactuals, interventions, confounding, selection, causal diagrams, measurement, and target-trial emulation"
SRC-NEG-CONTROL,Lipsitch Tchetgen Tchetgen and Cohen,Negative controls: a tool for detecting confounding and bias in observational studies,Published 2010-05,primary methods article,https://pubmed.ncbi.nlm.nih.gov/20335814/,2026-07-23,foundational_primary,"Negative exposure and outcome controls; DOI 10.1097/EDE.0b013e3181d61eeb"
SRC-HARKING,Norbert L. Kerr,HARKing: hypothesizing after the results are known,Published 1998,primary methods article,https://pubmed.ncbi.nlm.nih.gov/15647155/,2026-07-23,foundational_primary,"Defines presenting a post hoc hypothesis as if a priori; DOI 10.1207/s15327957pspr0203_4"
SRC-ASA-PVALUE,American Statistical Association,ASA Statement on Statistical Significance and P-Values,Released 2016-03-07,professional statistical statement,https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf,2026-07-23,current_official,"Thresholds alone do not support scientific conclusions; p-values do not measure hypothesis truth or effect importance; full reporting is required"
SRC-NASEM-RR,National Academies of Sciences Engineering and Medicine,Reproducibility and Replicability in Science,Published 2019-05-07,consensus report,https://www.nationalacademies.org/read/25303,2026-07-23,current_authoritative,"Defines reproducibility using same data/code and replicability using new data; DOI 10.17226/25303"
SRC-TOP,Center for Open Science collaborators,Promoting an open research culture,Published 2015-06-26,primary transparency framework,https://www.science.org/doi/10.1126/science.aab2374,2026-07-23,current_primary,"Transparency and Openness Promotion guidelines; apply with privacy, consent, governance, and security limits"
SRC-NIH-DMS,National Institutes of Health,Data Management and Sharing Policy,Effective 2023-01-25,official policy,https://sharing.nih.gov/data-management-and-sharing-policy,2026-07-23,current_official,"Prospective data-management and sharing planning for covered NIH-funded research; sharing remains subject to justified limits"
SRC-NIST-GENAI,National Institute of Standards and Technology,Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile,NIST AI 600-1 July 2024; page updated 2026-04-08,official risk framework,https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence,2026-07-23,current_official,"Confabulation, privacy, harmful bias/homogenization, information integrity, dangerous recommendations, and human-AI configuration"
SRC-DOSHI-HAUSER,Doshi and Hauser,Generative AI enhances individual creativity but reduces the collective diversity of novel content,Published 2024-07-12,primary research,https://www.science.org/doi/10.1126/sciadv.adn5290,2026-07-23,current_primary,"AI-assisted stories were more similar in this experiment; do not generalize beyond the studied task without evidence"
SRC-UNESCO-AI,UNESCO,Recommendation on the Ethics of Artificial Intelligence,Adopted 2021; official page current 2026,international recommendation,https://www.unesco.org/en/artificial-intelligence/recommendation-ethics,2026-07-23,current_official,"Human rights, privacy, accountability, transparency, diversity, and human oversight"
SRC-UNESCO-OPEN,UNESCO,Recommendation on Open Science,Adopted 2021,international recommendation,https://unesdoc.unesco.org/ark:/48223/pf0000379949,2026-07-23,current_official,"Open-science values and practices with responsibility, inclusiveness, and governance"
SRC-HHS-COMMON-RULE,U.S. Department of Health and Human Services,Federal Policy for the Protection of Human Subjects (Common Rule),Official page updated 2026-01-15,regulation and policy index,https://www.hhs.gov/ohrp/regulations-and-policy/regulations/common-rule/index.html,2026-07-23,current_official,"45 CFR 46 applicability and agency implementation; obtain an authorized local determination"
SRC-BELMONT,U.S. Department of Health and Human Services,The Belmont Report,Published 1979,ethical principles report,https://www.hhs.gov/ohrp/regulations-and-policy/belmont-report/index.html,2026-07-23,current_foundational,"Respect for persons, beneficence, and justice"
SRC-HELSINKI,World Medical Association,WMA Declaration of Helsinki: Ethical Principles for Medical Research Involving Human Participants,Revised October 2024,international ethical declaration,https://www.wma.net/policies-post/wma-declaration-of-helsinki/,2026-07-23,current_official,"Current international medical-research ethics statement; local law and review remain controlling"
SRC-OLAW-PHS,Office of Laboratory Animal Welfare,Public Health Service Policy on Humane Care and Use of Laboratory Animals,Current official policy page,official animal-welfare policy,https://grants.nih.gov/policy-and-compliance/policy-topics/animal-welfare/laws-regulations/phs-policy,2026-07-23,current_official,"Institutional assurance and IACUC review for covered PHS-conducted or supported animal activities"
SRC-ARRIVE,NC3Rs / ARRIVE Group,ARRIVE Guidelines 2.0,Published 2020,animal reporting guideline,https://arriveguidelines.org/arrive-guidelines,2026-07-23,current_official,"Reporting guidance for in vivo animal research; not an ethics approval or design-quality certificate"
SRC-NIH-RSNA,National Institutes of Health,NIH Guidelines for Research Involving Recombinant or Synthetic Nucleic Acid Molecules,April 2024 or latest revision,official biosafety policy,https://osp.od.nih.gov/wp-content/uploads/NIH_Guidelines.htm,2026-07-23,current_official,"Institutional biosafety oversight and covered research categories; verify the latest revision and local applicability"
SRC-NIH-BIOSEC,NIH Office of Science Policy,Biosafety and Biosecurity Policy,Official page updated 2026-04-09,official policy portal,https://osp.od.nih.gov/policies/biosafety-and-biosecurity-policy,2026-07-23,current_official,"Current NIH biosafety, biosecurity, IBC, transparency, and Executive Order implementation links"
SRC-BMBL,Centers for Disease Control and Prevention and National Institutes of Health,Biosafety in Microbiological and Biomedical Laboratories,6th edition June 2020,official biosafety guidance,https://www.cdc.gov/labs/bmbl/index.html,2026-07-23,current_official,"Risk assessment and biosafety guidance; use qualified institutional review rather than inferring procedures from this skill"
SRC-WHO-LIFE,World Health Organization,Global Guidance Framework for the Responsible Use of the Life Sciences,Published 2022-09-13,international guidance,https://www.who.int/publications/i/item/9789240056107,2026-07-23,current_official,"Values, principles, tools, and governance for biorisks and dual-use throughout the research lifecycle"
SRC-EO-14292,The White House,Executive Order 14292: Improving the Safety and Security of Biological Research,Signed 2025-05-05,executive order,https://www.whitehouse.gov/presidential-actions/2025/05/improving-the-safety-and-security-of-biological-research,2026-07-23,current_official,"Directed revision/replacement of 2024 DURC/PEPP policy and pause/termination actions for covered dangerous gain-of-function research"
SRC-NIH-NOT-25-112,National Institutes of Health,NOT-OD-25-112: Implementation Update—Improving the Safety and Security of Biological Research,Issued 2025-05,official funding notice,https://grants.nih.gov/grants/guide/notice-files/NOT-OD-25-112.html,2026-07-23,current_official,"States Executive Order definitions superseded NIH's 2024 DURC/PEPP implementation and rescinds NOT-OD-25-061"
SRC-ASPR-DURC,U.S. Department of Health and Human Services ASPR,Dual Use Research of Concern Oversight Policy Framework,Official page current at verification,official policy status page,https://aspr.hhs.gov/S3/Pages/Dual-Use-Research-of-Concern-Oversight-Policy-Framework.aspx,2026-07-23,current_transition_notice,"At verification, states the 2024 DURC/PEPP policy will be revised or replaced and page will update when revised policy is available"
```
