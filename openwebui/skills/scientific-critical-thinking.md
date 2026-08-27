---
name: scientific-critical-thinking
description: Evaluate scientific claims and evidence quality. Use for assessing experimental design validity, identifying biases and confounders, applying evidence grading frameworks (GRADE, Cochrane Risk of Bias), or teaching critical analysis. Best for understanding evidence quality, identifying flaws. For formal peer review writing use peer-review.
---

# Scientific Critical Thinking

## Overview

Critical thinking is a systematic process for evaluating scientific rigor. Assess methodology, experimental design, statistical validity, biases, confounding, and evidence quality using GRADE and Cochrane ROB frameworks. Apply this skill for critical analysis of scientific claims.

## When to Use This Skill

This skill should be used when:
- Evaluating research methodology and experimental design
- Assessing statistical validity and evidence quality
- Identifying biases and confounding in studies
- Reviewing scientific claims and conclusions
- Conducting systematic reviews or meta-analyses
- Applying GRADE or Cochrane risk of bias assessments
- Providing critical analysis of research papers

## Visual Aids (Optional)

Only add figures when the **user explicitly requests** a diagram (for example, a GRADE flowchart, bias decision tree, or evidence-quality framework).

**When figures help:**
- Critical thinking framework diagrams
- Bias identification decision trees
- Evidence quality assessment flowcharts
- GRADE or risk-of-bias evaluation frameworks

**How to create figures:**
- **Preferred:** Use the **scientific-schematics** skill for AI-generated diagrams from a natural-language description
- **Alternative:** Build figures in your usual tools (draw.io, PowerPoint, matplotlib, etc.)

From the `scientific-schematics` skill directory, with `OPENROUTER_API_KEY` set:

```bash
python scripts/generate_schematic.py "GRADE evidence assessment flowchart with downgrade and upgrade factors" -o figures/grade_flowchart.png --doc-type report
```

**Disclosure:** AI schematic generation sends your prompt to [OpenRouter](https://openrouter.ai/) (a third-party API). Do not include unpublished sensitive details unless that transmission is appropriate for your project.

---

## Core Capabilities

Seven capability areas, each with the questions to ask and what the answers imply, are in
[references/core_capabilities.md](references/core_capabilities.md):

1. **Methodology critique** — design, controls, confounding, and whether the method can
   answer the question asked.
2. **Bias detection** — selection, measurement, publication, and cognitive biases.
3. **Statistical analysis evaluation** — power, multiplicity, p-value misuse, effect sizes.
4. **Evidence quality assessment** — study hierarchy, replication, and strength of inference.
5. **Logical fallacy identification** — the fallacies that recur in scientific argument.
6. **Research design guidance** — how to strengthen a design before data collection.
7. **Claim evaluation** — separating what was shown from what is being asserted.

Per-topic detail is in [references/scientific_method.md](references/scientific_method.md),
[references/common_biases.md](references/common_biases.md),
[references/statistical_pitfalls.md](references/statistical_pitfalls.md),
[references/evidence_hierarchy.md](references/evidence_hierarchy.md),
[references/logical_fallacies.md](references/logical_fallacies.md), and
[references/experimental_design.md](references/experimental_design.md).

## Application Guidelines

### General Approach

1. **Be Constructive**
   - Identify strengths as well as weaknesses
   - Suggest improvements rather than just criticizing
   - Distinguish between fatal flaws and minor limitations
   - Recognize that all research has limitations

2. **Be Specific**
   - Point to specific instances (e.g., "Table 2 shows..." or "In the Methods section...")
   - Quote problematic statements
   - Provide concrete examples of issues
   - Reference specific principles or standards violated

3. **Be Proportionate**
   - Match criticism severity to issue importance
   - Distinguish between major threats to validity and minor concerns
   - Consider whether issues affect primary conclusions
   - Acknowledge uncertainty in your own assessments

4. **Apply Consistent Standards**
   - Use same criteria across all studies
   - Don't apply stricter standards to findings you dislike
   - Acknowledge your own potential biases
   - Base judgments on methodology, not results

5. **Consider Context**
   - Acknowledge practical and ethical constraints
   - Consider field-specific norms for effect sizes and methods
   - Recognize exploratory vs. confirmatory contexts
   - Account for resource limitations in evaluating studies

### When Providing Critique

**Structure feedback as:**

1. **Summary:** Brief overview of what was evaluated
2. **Strengths:** What was done well (important for credibility and learning)
3. **Concerns:** Issues organized by severity
   - Critical issues (threaten validity of main conclusions)
   - Important issues (affect interpretation but not fatally)
   - Minor issues (worth noting but don't change conclusions)
4. **Specific Recommendations:** Actionable suggestions for improvement
5. **Overall Assessment:** Balanced conclusion about evidence quality and what can be concluded

**Use precise terminology:**
- Name specific biases, fallacies, and methodological issues
- Reference established standards and guidelines
- Cite principles from scientific methodology
- Use technical terms accurately

### When Uncertain

- **Acknowledge uncertainty:** "This could be X or Y; additional information needed is Z"
- **Ask clarifying questions:** "Was [methodological detail] done? This affects interpretation."
- **Provide conditional assessments:** "If X was done, then Y follows; if not, then Z is concern"
- **Note what additional information would resolve uncertainty**

## Reference Materials

This skill includes comprehensive reference materials that provide detailed frameworks for critical evaluation:

- **`references/scientific_method.md`** - Core principles of scientific methodology, the scientific process, critical evaluation criteria, red flags in scientific claims, causal inference standards, peer review, and open science principles

- **`references/common_biases.md`** - Comprehensive taxonomy of cognitive, experimental, methodological, statistical, and analysis biases with detection and mitigation strategies

- **`references/statistical_pitfalls.md`** - Common statistical errors and misinterpretations including p-value misunderstandings, multiple comparisons problems, sample size issues, effect size mistakes, correlation/causation confusion, regression pitfalls, and meta-analysis issues

- **`references/evidence_hierarchy.md`** - Traditional evidence hierarchy, GRADE system, study quality assessment criteria, domain-specific considerations, evidence synthesis principles, and practical decision frameworks

- **`references/logical_fallacies.md`** - Logical fallacies common in scientific discourse organized by type (causation, generalization, authority, relevance, structure, statistical) with examples and detection strategies

- **`references/experimental_design.md`** - Comprehensive experimental design checklist covering research questions, hypotheses, study design selection, variables, sampling, blinding, randomization, control groups, procedures, measurement, bias minimization, data management, statistical planning, ethical considerations, validity threats, and reporting standards

**When to consult references:**
- Load references into context when detailed frameworks are needed
- Use grep to search references for specific topics: `grep -r "pattern" references/`
- References provide depth; SKILL.md provides procedural guidance
- Consult references for comprehensive lists, detailed criteria, and specific examples

## Remember

**Scientific critical thinking is about:**
- Systematic evaluation using established principles
- Constructive critique that improves science
- Proportional confidence to evidence strength
- Transparency about uncertainty and limitations
- Consistent application of standards
- Recognition that all research has limitations
- Balance between skepticism and openness to evidence

**Always distinguish between:**
- Data (what was observed) and interpretation (what it means)
- Correlation and causation
- Statistical significance and practical importance
- Exploratory and confirmatory findings
- What is known and what is uncertain
- Evidence against a claim and evidence for the null

**Goals of critical thinking:**
1. Identify strengths and weaknesses accurately
2. Determine what conclusions are supported
3. Recognize limitations and uncertainties
4. Suggest improvements for future work
5. Advance scientific understanding

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/scientific-critical-thinking/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/common_biases.md`

# Common Biases in Scientific Research

## Cognitive Biases Affecting Researchers

### 1. Confirmation Bias
**Description:** Tendency to search for, interpret, and recall information that confirms preexisting beliefs.

**Manifestations:**
- Designing studies that can only support the hypothesis
- Interpreting ambiguous results as supportive
- Remembering hits and forgetting misses
- Selectively citing literature that agrees

**Mitigation:**
- Preregister hypotheses and analysis plans
- Actively seek disconfirming evidence
- Use blinded data analysis
- Consider alternative hypotheses

### 2. Hindsight Bias (I-Knew-It-All-Along Effect)
**Description:** After an event, people perceive it as having been more predictable than it actually was.

**Manifestations:**
- HARKing (Hypothesizing After Results are Known)
- Claiming predictions that weren't made
- Underestimating surprise at results

**Mitigation:**
- Document predictions before data collection
- Preregister studies
- Distinguish exploratory from confirmatory analyses

### 3. Publication Bias (File Drawer Problem)
**Description:** Positive/significant results are more likely to be published than negative/null results.

**Manifestations:**
- Literature appears to support effects that don't exist
- Overestimation of effect sizes
- Inability to estimate true effects from published literature

**Mitigation:**
- Publish null results
- Use preregistration and registered reports
- Conduct systematic reviews with grey literature
- Check for funnel plot asymmetry in meta-analyses

### 4. Anchoring Bias
**Description:** Over-reliance on the first piece of information encountered.

**Manifestations:**
- Initial hypotheses unduly influence interpretation
- First studies in a field set expectations
- Pilot data biases main study interpretation

**Mitigation:**
- Consider multiple initial hypotheses
- Evaluate evidence independently
- Use structured decision-making

### 5. Availability Heuristic
**Description:** Overestimating likelihood of events based on how easily examples come to mind.

**Manifestations:**
- Overemphasizing recent or dramatic findings
- Neglecting base rates
- Anecdotal evidence overshadowing statistics

**Mitigation:**
- Consult systematic reviews, not memorable papers
- Consider base rates explicitly
- Use statistical thinking, not intuition

### 6. Bandwagon Effect
**Description:** Adopting beliefs because many others hold them.

**Manifestations:**
- Following research trends without critical evaluation
- Citing widely-cited papers without reading
- Accepting "textbook knowledge" uncritically

**Mitigation:**
- Evaluate evidence independently
- Read original sources
- Question assumptions

### 7. Belief Perseverance
**Description:** Maintaining beliefs even after evidence disproving them.

**Manifestations:**
- Defending theories despite contradictory evidence
- Finding ad hoc explanations for discrepant results
- Dismissing replication failures

**Mitigation:**
- Explicitly consider what evidence would change your mind
- Update beliefs based on evidence
- Distinguish between theories and ego

### 8. Outcome Bias
**Description:** Judging decisions based on outcomes rather than the quality of the decision at the time.

**Manifestations:**
- Valuing lucky guesses over sound methodology
- Dismissing good studies with null results
- Rewarding sensational findings over rigorous methods

**Mitigation:**
- Evaluate methodology independently of results
- Value rigor and transparency
- Recognize role of chance

## Experimental and Methodological Biases

### 9. Selection Bias
**Description:** Systematic differences between those selected for study and those not selected.

**Types:**
- **Sampling bias:** Non-random sample
- **Attrition bias:** Systematic dropout
- **Volunteer bias:** Self-selected participants differ
- **Berkson's bias:** Hospital patients differ from general population
- **Survivorship bias:** Only examining "survivors"

**Detection:**
- Compare characteristics of participants vs. target population
- Analyze dropout patterns
- Consider who is missing from the sample

**Mitigation:**
- Random sampling
- Track and analyze non-responders
- Use strategies to minimize dropout
- Report participant flow diagrams

### 10. Observer Bias (Detection Bias)
**Description:** Researchers' expectations influence observations or measurements.

**Manifestations:**
- Measuring outcomes differently across groups
- Interpreting ambiguous results based on group assignment
- Unconsciously cueing participants

**Mitigation:**
- Blinding of observers/assessors
- Objective, automated measurements
- Standardized protocols
- Inter-rater reliability checks

### 11. Performance Bias
**Description:** Systematic differences in care provided to comparison groups.

**Manifestations:**
- Treating experimental group differently
- Providing additional attention to one group
- Differential adherence to protocols

**Mitigation:**
- Standardize all procedures
- Blind participants and providers
- Use placebo controls
- Monitor protocol adherence

### 12. Measurement Bias (Information Bias)
**Description:** Systematic errors in how variables are measured.

**Types:**
- **Recall bias:** Systematic differences in accuracy of recall
- **Social desirability bias:** Responding in socially acceptable ways
- **Interviewer bias:** Interviewer's characteristics affect responses
- **Instrument bias:** Measurement tools systematically err

**Mitigation:**
- Use validated, objective measures
- Standardize data collection
- Blind participants to hypotheses
- Verify self-reports with objective data

### 13. Confounding Bias
**Description:** Effect of extraneous variable mixed with the variable of interest.

**Examples:**
- Age confounding relationship between exercise and health
- Socioeconomic status confounding education and outcomes
- Indication bias in treatment studies

**Mitigation:**
- Randomization
- Matching
- Statistical adjustment
- Stratification
- Restriction

### 14. Reporting Bias
**Description:** Selective reporting of results.

**Types:**
- **Outcome reporting bias:** Selectively reporting outcomes
- **Time-lag bias:** Delayed publication of negative results
- **Language bias:** Publishing positive results in English
- **Citation bias:** Preferentially citing positive studies

**Mitigation:**
- Preregister all outcomes
- Report all planned analyses
- Distinguish primary from secondary outcomes
- Use study registries

### 15. Spectrum Bias
**Description:** Test performance varies depending on the spectrum of disease severity in the sample.

**Manifestations:**
- Diagnostic tests appearing more accurate in extreme cases
- Treatment effects differing by severity

**Mitigation:**
- Test in representative samples
- Report performance across disease spectrum
- Avoid case-control designs for diagnostic studies

### 16. Lead-Time Bias
**Description:** Apparent survival benefit due to earlier detection, not improved outcomes.

**Example:**
- Screening detecting disease earlier makes survival seem longer, even if death occurs at same age

**Mitigation:**
- Measure mortality, not just survival from diagnosis
- Use randomized screening trials
- Consider length-time and overdiagnosis bias

### 17. Length-Time Bias
**Description:** Screening disproportionately detects slower-growing, less aggressive cases.

**Example:**
- Slow-growing cancers detected more often than fast-growing ones, making screening appear beneficial

**Mitigation:**
- Randomized trials with mortality endpoints
- Consider disease natural history

### 18. Response Bias
**Description:** Systematic pattern in how participants respond.

**Types:**
- **Acquiescence bias:** Tendency to agree
- **Extreme responding:** Always choosing extreme options
- **Neutral responding:** Avoiding extreme responses
- **Demand characteristics:** Responding based on perceived expectations

**Mitigation:**
- Mix positive and negative items
- Use multiple response formats
- Blind participants to hypotheses
- Use behavioral measures

## Statistical and Analysis Biases

### 19. P-Hacking (Data Dredging)
**Description:** Manipulating data or analyses until significant results emerge.

**Manifestations:**
- Collecting data until significance reached
- Testing multiple outcomes, reporting only significant ones
- Trying multiple analysis methods
- Excluding "outliers" to reach significance
- Subgroup analyses until finding significance

**Detection:**
- Suspiciously perfect p-values (just below .05)
- Many researcher degrees of freedom
- Undisclosed analyses
- Fishing expeditions

**Mitigation:**
- Preregister analysis plans
- Report all analyses conducted
- Correct for multiple comparisons
- Distinguish exploratory from confirmatory

### 20. HARKing (Hypothesizing After Results are Known)
**Description:** Presenting post hoc hypotheses as if they were predicted a priori.

**Why problematic:**
- Inflates apparent evidence
- Conflates exploration with confirmation
- Misrepresents the scientific process

**Mitigation:**
- Preregister hypotheses
- Clearly label exploratory analyses
- Require replication of unexpected findings

### 21. Base Rate Neglect
**Description:** Ignoring prior probability when evaluating evidence.

**Example:**
- Test with 95% accuracy in rare disease (1% prevalence): positive result only 16% likely to indicate disease

**Mitigation:**
- Always consider base rates/prior probability
- Use Bayesian reasoning
- Report positive and negative predictive values

### 22. Regression to the Mean
**Description:** Extreme measurements tend to be followed by less extreme ones.

**Manifestations:**
- Treatment effects in extreme groups may be regression artifacts
- "Sophomore slump" in high performers

**Mitigation:**
- Use control groups
- Consider natural variation
- Don't select based on extreme baseline values without controls

### 23. Texas Sharpshooter Fallacy
**Description:** Selecting data after seeing patterns, like shooting arrows then drawing targets around clusters.

**Manifestations:**
- Finding patterns in random data
- Subgroup analyses selected post hoc
- Geographic clustering studies without correction

**Mitigation:**
- Prespecify hypotheses
- Correct for multiple comparisons
- Replicate findings in independent data

## Reducing Bias: Best Practices

### Study Design
1. Randomization
2. Blinding (single, double, triple)
3. Control groups
4. Adequate sample size
5. Preregistration

### Data Collection
1. Standardized protocols
2. Validated instruments
3. Objective measures when possible
4. Multiple observers/raters
5. Complete data collection

### Analysis
1. Intention-to-treat analysis
2. Prespecified analyses
3. Appropriate statistical tests
4. Multiple comparison corrections
5. Sensitivity analyses

### Reporting
1. Complete transparency
2. CONSORT, PRISMA, or similar guidelines
3. Report all outcomes
4. Distinguish exploratory from confirmatory
5. Share data and code

### Meta-Level
1. Adversarial collaboration
2. Replication studies
3. Open science practices
4. Peer review
5. Systematic reviews

### `references/core_capabilities.md`

# Core Capabilities

The seven capability areas in full: methodology critique, bias detection, statistical
analysis evaluation, evidence quality assessment, logical fallacy identification,
research design guidance, and claim evaluation — each with the questions to ask and what
the answers imply.

## Core Capabilities

### 1. Methodology Critique

Evaluate research methodology for rigor, validity, and potential flaws.

**Apply when:**
- Reviewing research papers
- Assessing experimental designs
- Evaluating study protocols
- Planning new research

**Evaluation framework:**

1. **Study Design Assessment**
   - Is the design appropriate for the research question?
   - Can the design support causal claims being made?
   - Are comparison groups appropriate and adequate?
   - Consider whether experimental, quasi-experimental, or observational design is justified

2. **Validity Analysis**
   - **Internal validity:** Can we trust the causal inference?
     - Check randomization quality
     - Evaluate confounding control
     - Assess selection bias
     - Review attrition/dropout patterns
   - **External validity:** Do results generalize?
     - Evaluate sample representativeness
     - Consider ecological validity of setting
     - Assess whether conditions match target application
   - **Construct validity:** Do measures capture intended constructs?
     - Review measurement validation
     - Check operational definitions
     - Assess whether measures are direct or proxy
   - **Statistical conclusion validity:** Are statistical inferences sound?
     - Verify adequate power/sample size
     - Check assumption compliance
     - Evaluate test appropriateness

3. **Control and Blinding**
   - Was randomization properly implemented (sequence generation, allocation concealment)?
   - Was blinding feasible and implemented (participants, providers, assessors)?
   - Are control conditions appropriate (placebo, active control, no treatment)?
   - Could performance or detection bias affect results?

4. **Measurement Quality**
   - Are instruments validated and reliable?
   - Are measures objective when possible, or subjective with acknowledged limitations?
   - Is outcome assessment standardized?
   - Are multiple measures used to triangulate findings?

**Reference:** See `references/scientific_method.md` for detailed principles and `references/experimental_design.md` for comprehensive design checklist.

### 2. Bias Detection

Identify and evaluate potential sources of bias that could distort findings.

**Apply when:**
- Reviewing published research
- Designing new studies
- Interpreting conflicting evidence
- Assessing research quality

**Systematic bias review:**

1. **Cognitive Biases (Researcher)**
   - **Confirmation bias:** Are only supporting findings highlighted?
   - **HARKing:** Were hypotheses stated a priori or formed after seeing results?
   - **Publication bias:** Are negative results missing from literature?
   - **Cherry-picking:** Is evidence selectively reported?
   - Check for preregistration and analysis plan transparency

2. **Selection Biases**
   - **Sampling bias:** Is sample representative of target population?
   - **Volunteer bias:** Do participants self-select in systematic ways?
   - **Attrition bias:** Is dropout differential between groups?
   - **Survivorship bias:** Are only "survivors" visible in sample?
   - Examine participant flow diagrams and compare baseline characteristics

3. **Measurement Biases**
   - **Observer bias:** Could expectations influence observations?
   - **Recall bias:** Are retrospective reports systematically inaccurate?
   - **Social desirability:** Are responses biased toward acceptability?
   - **Instrument bias:** Do measurement tools systematically err?
   - Evaluate blinding, validation, and measurement objectivity

4. **Analysis Biases**
   - **P-hacking:** Were multiple analyses conducted until significance emerged?
   - **Outcome switching:** Were non-significant outcomes replaced with significant ones?
   - **Selective reporting:** Are all planned analyses reported?
   - **Subgroup fishing:** Were subgroup analyses conducted without correction?
   - Check for study registration and compare to published outcomes

5. **Confounding**
   - What variables could affect both exposure and outcome?
   - Were confounders measured and controlled (statistically or by design)?
   - Could unmeasured confounding explain findings?
   - Are there plausible alternative explanations?

**Reference:** See `references/common_biases.md` for comprehensive bias taxonomy with detection and mitigation strategies.

### 3. Statistical Analysis Evaluation

Critically assess statistical methods, interpretation, and reporting.

**Apply when:**
- Reviewing quantitative research
- Evaluating data-driven claims
- Assessing clinical trial results
- Reviewing meta-analyses

**Statistical review checklist:**

1. **Sample Size and Power**
   - Was a priori power analysis conducted?
   - Is sample adequate for detecting meaningful effects?
   - Is the study underpowered (common problem)?
   - Do significant results from small samples raise flags for inflated effect sizes?

2. **Statistical Tests**
   - Are tests appropriate for data type and distribution?
   - Were test assumptions checked and met?
   - Are parametric tests justified, or should non-parametric alternatives be used?
   - Is the analysis matched to study design (e.g., paired vs. independent)?

3. **Multiple Comparisons**
   - Were multiple hypotheses tested?
   - Was correction applied (Bonferroni, FDR, other)?
   - Are primary outcomes distinguished from secondary/exploratory?
   - Could findings be false positives from multiple testing?

4. **P-Value Interpretation**
   - Are p-values interpreted correctly (probability of data if null is true)?
   - Is non-significance incorrectly interpreted as "no effect"?
   - Is statistical significance conflated with practical importance?
   - Are exact p-values reported, or only "p < .05"?
   - Is there suspicious clustering just below .05?

5. **Effect Sizes and Confidence Intervals**
   - Are effect sizes reported alongside significance?
   - Are confidence intervals provided to show precision?
   - Is the effect size meaningful in practical terms?
   - Are standardized effect sizes interpreted with field-specific context?

6. **Missing Data**
   - How much data is missing?
   - Is missing data mechanism considered (MCAR, MAR, MNAR)?
   - How is missing data handled (deletion, imputation, maximum likelihood)?
   - Could missing data bias results?

7. **Regression and Modeling**
   - Is the model overfitted (too many predictors, no cross-validation)?
   - Are predictions made outside the data range (extrapolation)?
   - Are multicollinearity issues addressed?
   - Are model assumptions checked?

8. **Common Pitfalls**
   - Correlation treated as causation
   - Ignoring regression to the mean
   - Base rate neglect
   - Texas sharpshooter fallacy (pattern finding in noise)
   - Simpson's paradox (confounding by subgroups)

**Reference:** See `references/statistical_pitfalls.md` for detailed pitfalls and correct practices.

### 4. Evidence Quality Assessment

Evaluate the strength and quality of evidence systematically.

**Apply when:**
- Weighing evidence for decisions
- Conducting literature reviews
- Comparing conflicting findings
- Determining confidence in conclusions

**Evidence evaluation framework:**

1. **Study Design Hierarchy**
   - Systematic reviews/meta-analyses (highest for intervention effects)
   - Randomized controlled trials
   - Cohort studies
   - Case-control studies
   - Cross-sectional studies
   - Case series/reports
   - Expert opinion (lowest)

   **Important:** Higher-level designs aren't always better quality. A well-designed observational study can be stronger than a poorly-conducted RCT.

2. **Quality Within Design Type**
   - Risk of bias assessment (use appropriate tool: Cochrane RoB 2 for RCTs, ROBINS-I for non-randomized studies, Newcastle-Ottawa, etc.)
   - Methodological rigor
   - Transparency and reporting completeness
   - Conflicts of interest

3. **GRADE Considerations (if applicable)**
   - Start with design type (RCT = high, observational = low)
   - **Downgrade for:**
     - Risk of bias
     - Inconsistency across studies
     - Indirectness (wrong population/intervention/outcome)
     - Imprecision (wide confidence intervals, small samples)
     - Publication bias
   - **Upgrade for:**
     - Large effect sizes
     - Dose-response relationships
     - Confounders would reduce (not increase) effect

4. **Convergence of Evidence**
   - **Stronger when:**
     - Multiple independent replications
     - Different research groups and settings
     - Different methodologies converge on same conclusion
     - Mechanistic and empirical evidence align
   - **Weaker when:**
     - Single study or research group
     - Contradictory findings in literature
     - Publication bias evident
     - No replication attempts

5. **Contextual Factors**
   - Biological/theoretical plausibility
   - Consistency with established knowledge
   - Temporality (cause precedes effect)
   - Specificity of relationship
   - Strength of association

**Reference:** See `references/evidence_hierarchy.md` for detailed hierarchy, GRADE system, and quality assessment tools.

### 5. Logical Fallacy Identification

Detect and name logical errors in scientific arguments and claims.

**Apply when:**
- Evaluating scientific claims
- Reviewing discussion/conclusion sections
- Assessing popular science communication
- Identifying flawed reasoning

**Common fallacies in science:**

1. **Causation Fallacies**
   - **Post hoc ergo propter hoc:** "B followed A, so A caused B"
   - **Correlation = causation:** Confusing association with causality
   - **Reverse causation:** Mistaking cause for effect
   - **Single cause fallacy:** Attributing complex outcomes to one factor

2. **Generalization Fallacies**
   - **Hasty generalization:** Broad conclusions from small samples
   - **Anecdotal fallacy:** Personal stories as proof
   - **Cherry-picking:** Selecting only supporting evidence
   - **Ecological fallacy:** Group patterns applied to individuals

3. **Authority and Source Fallacies**
   - **Appeal to authority:** "Expert said it, so it's true" (without evidence)
   - **Ad hominem:** Attacking person, not argument
   - **Genetic fallacy:** Judging by origin, not merits
   - **Appeal to nature:** "Natural = good/safe"

4. **Statistical Fallacies**
   - **Base rate neglect:** Ignoring prior probability
   - **Texas sharpshooter:** Finding patterns in random data
   - **Multiple comparisons:** Not correcting for multiple tests
   - **Prosecutor's fallacy:** Confusing P(E|H) with P(H|E)

5. **Structural Fallacies**
   - **False dichotomy:** "Either A or B" when more options exist
   - **Moving goalposts:** Changing evidence standards after they're met
   - **Begging the question:** Circular reasoning
   - **Straw man:** Misrepresenting arguments to attack them

6. **Science-Specific Fallacies**
   - **Galileo gambit:** "They laughed at Galileo, so my fringe idea is correct"
   - **Argument from ignorance:** "Not proven false, so true"
   - **Nirvana fallacy:** Rejecting imperfect solutions
   - **Unfalsifiability:** Making untestable claims

**When identifying fallacies:**
- Name the specific fallacy
- Explain why the reasoning is flawed
- Identify what evidence would be needed for valid inference
- Note that fallacious reasoning doesn't prove the conclusion false—just that this argument doesn't support it

**Reference:** See `references/logical_fallacies.md` for comprehensive fallacy catalog with examples and detection strategies.

### 6. Research Design Guidance

Provide constructive guidance for planning rigorous studies.

**Apply when:**
- Helping design new experiments
- Planning research projects
- Reviewing research proposals
- Improving study protocols

**Design process:**

1. **Research Question Refinement**
   - Ensure question is specific, answerable, and falsifiable
   - Verify it addresses a gap or contradiction in literature
   - Confirm feasibility (resources, ethics, time)
   - Define variables operationally

2. **Design Selection**
   - Match design to question (causal → experimental; associational → observational)
   - Consider feasibility and ethical constraints
   - Choose between-subjects, within-subjects, or mixed designs
   - Plan factorial designs if testing multiple factors

3. **Bias Minimization Strategy**
   - Implement randomization when possible
   - Plan blinding at all feasible levels (participants, providers, assessors)
   - Identify and plan to control confounds (randomization, matching, stratification, statistical adjustment)
   - Standardize all procedures
   - Plan to minimize attrition

4. **Sample Planning**
   - Conduct a priori power analysis (specify expected effect, desired power, alpha)
   - Account for attrition in sample size
   - Define clear inclusion/exclusion criteria
   - Consider recruitment strategy and feasibility
   - Plan for sample representativeness

5. **Measurement Strategy**
   - Select validated, reliable instruments
   - Use objective measures when possible
   - Plan multiple measures of key constructs (triangulation)
   - Ensure measures are sensitive to expected changes
   - Establish inter-rater reliability procedures

6. **Analysis Planning**
   - Prespecify all hypotheses and analyses
   - Designate primary outcome clearly
   - Plan statistical tests with assumption checks
   - Specify how missing data will be handled
   - Plan to report effect sizes and confidence intervals
   - Consider multiple comparison corrections

7. **Transparency and Rigor**
   - Preregister study and analysis plan
   - Use reporting guidelines (CONSORT, STROBE, PRISMA)
   - Plan to report all outcomes, not just significant ones
   - Distinguish confirmatory from exploratory analyses
   - Commit to data/code sharing

**Reference:** See `references/experimental_design.md` for comprehensive design checklist covering all stages from question to dissemination.

### 7. Claim Evaluation

Systematically evaluate scientific claims for validity and support.

**Apply when:**
- Assessing conclusions in papers
- Evaluating media reports of research
- Reviewing abstract or introduction claims
- Checking if data support conclusions

**Claim evaluation process:**

1. **Identify the Claim**
   - What exactly is being claimed?
   - Is it a causal claim, associational claim, or descriptive claim?
   - How strong is the claim (proven, likely, suggested, possible)?

2. **Assess the Evidence**
   - What evidence is provided?
   - Is evidence direct or indirect?
   - Is evidence sufficient for the strength of claim?
   - Are alternative explanations ruled out?

3. **Check Logical Connection**
   - Do conclusions follow from the data?
   - Are there logical leaps?
   - Is correlational data used to support causal claims?
   - Are limitations acknowledged?

4. **Evaluate Proportionality**
   - Is confidence proportional to evidence strength?
   - Are hedging words used appropriately?
   - Are limitations downplayed?
   - Is speculation clearly labeled?

5. **Check for Overgeneralization**
   - Do claims extend beyond the sample studied?
   - Are population restrictions acknowledged?
   - Is context-dependence recognized?
   - Are caveats about generalization included?

6. **Red Flags**
   - Causal language from correlational studies
   - "Proves" or absolute certainty
   - Cherry-picked citations
   - Ignoring contradictory evidence
   - Dismissing limitations
   - Extrapolation beyond data

**Provide specific feedback:**
- Quote the problematic claim
- Explain what evidence would be needed to support it
- Suggest appropriate hedging language if warranted
- Distinguish between data (what was found) and interpretation (what it means)

### `references/evidence_hierarchy.md`

# Evidence Hierarchy and Quality Assessment

## Traditional Evidence Hierarchy (Medical/Clinical)

### Level 1: Systematic Reviews and Meta-Analyses
**Description:** Comprehensive synthesis of all available evidence on a question.

**Strengths:**
- Combines multiple studies for greater power
- Reduces impact of single-study anomalies
- Can identify patterns across studies
- Quantifies overall effect size

**Weaknesses:**
- Quality depends on included studies ("garbage in, garbage out")
- Publication bias can distort findings
- Heterogeneity may make pooling inappropriate
- Can mask important differences between studies

**Critical evaluation:**
- Was search comprehensive (multiple databases, grey literature)?
- Were inclusion criteria appropriate and prespecified?
- Was study quality assessed?
- Was heterogeneity explored?
- Was publication bias assessed (funnel plots, fail-safe N)?
- Were appropriate statistical methods used?

### Level 2: Randomized Controlled Trials (RCTs)
**Description:** Experimental studies with random assignment to conditions.

**Strengths:**
- Gold standard for establishing causation
- Controls for known and unknown confounders
- Minimizes selection bias
- Enables causal inference

**Weaknesses:**
- May not be ethical or feasible
- Artificial settings may limit generalizability
- Often short-term with selected populations
- Expensive and time-consuming

**Critical evaluation:**
- Was randomization adequate (sequence generation, allocation concealment)?
- Was blinding implemented (participants, providers, assessors)?
- Was sample size adequate (power analysis)?
- Was intention-to-treat analysis used?
- Was attrition rate acceptable and balanced?
- Are results generalizable?

### Level 3: Cohort Studies
**Description:** Observational studies following groups over time.

**Types:**
- **Prospective:** Follow forward from exposure to outcome
- **Retrospective:** Look backward at existing data

**Strengths:**
- Can study multiple outcomes
- Establishes temporal sequence
- Can calculate incidence and relative risk
- More feasible than RCTs for many questions

**Weaknesses:**
- Susceptible to confounding
- Selection bias possible
- Attrition can bias results
- Cannot prove causation definitively

**Critical evaluation:**
- Were cohorts comparable at baseline?
- Was exposure measured reliably?
- Was follow-up adequate and complete?
- Were potential confounders measured and controlled?
- Was outcome assessment blinded to exposure?

### Level 4: Case-Control Studies
**Description:** Compare people with outcome (cases) to those without (controls), looking back at exposures.

**Strengths:**
- Efficient for rare outcomes
- Relatively quick and inexpensive
- Can study multiple exposures
- Useful for generating hypotheses

**Weaknesses:**
- Cannot calculate incidence
- Susceptible to recall bias
- Selection of controls is challenging
- Cannot prove causation

**Critical evaluation:**
- Were cases and controls defined clearly?
- Were controls appropriate (same source population)?
- Was matching appropriate?
- How was exposure ascertained (records vs. recall)?
- Were potential confounders controlled?
- Could recall bias explain findings?

### Level 5: Cross-Sectional Studies
**Description:** Snapshot observation at single point in time.

**Strengths:**
- Quick and inexpensive
- Can assess prevalence
- Useful for hypothesis generation
- Can study multiple outcomes and exposures

**Weaknesses:**
- Cannot establish temporal sequence
- Cannot determine causation
- Prevalence-incidence bias
- Survival bias

**Critical evaluation:**
- Was sample representative?
- Were measures validated?
- Could reverse causation explain findings?
- Are confounders acknowledged?

### Level 6: Case Series and Case Reports
**Description:** Description of observations in clinical practice.

**Strengths:**
- Can identify new diseases or effects
- Hypothesis-generating
- Details rare phenomena
- Quick to report

**Weaknesses:**
- No control group
- No statistical inference possible
- Highly susceptible to bias
- Cannot establish causation or frequency

**Use:** Primarily for hypothesis generation and clinical description.

### Level 7: Expert Opinion
**Description:** Statements by recognized authorities.

**Strengths:**
- Synthesizes experience
- Useful when no research available
- May integrate multiple sources

**Weaknesses:**
- Subjective and potentially biased
- May not reflect current evidence
- Appeal to authority fallacy risk
- Individual expertise varies

**Use:** Lowest level of evidence; should be supported by data when possible.

## Nuances and Limitations of Traditional Hierarchy

### When Lower-Level Evidence Can Be Strong
1. **Well-designed observational studies** with:
   - Large effects (hard to confound)
   - Dose-response relationships
   - Consistent findings across contexts
   - Biological plausibility
   - No plausible confounders

2. **Multiple converging lines of evidence** from different study types

3. **Natural experiments** approximating randomization

### When Higher-Level Evidence Can Be Weak
1. **Poor-quality RCTs** with:
   - Inadequate randomization
   - High attrition
   - No blinding when feasible
   - Conflicts of interest

2. **Biased meta-analyses**:
   - Publication bias
   - Selective inclusion
   - Inappropriate pooling
   - Poor search strategy

3. **Not addressing the right question**:
   - Wrong population
   - Wrong comparison
   - Wrong outcome
   - Too artificial to generalize

## Alternative: GRADE System

GRADE (Grading of Recommendations Assessment, Development and Evaluation) assesses evidence quality across four levels:

### High Quality
**Definition:** Very confident that true effect is close to estimated effect.

**Characteristics:**
- Well-conducted RCTs
- Overwhelming evidence from observational studies
- Large, consistent effects
- No serious limitations

### Moderate Quality
**Definition:** Moderately confident; true effect likely close to estimated, but could be substantially different.

**Downgrades from high:**
- Some risk of bias
- Inconsistency across studies
- Indirectness (different populations/interventions)
- Imprecision (wide confidence intervals)
- Publication bias suspected

### Low Quality
**Definition:** Limited confidence; true effect may be substantially different.

**Downgrades:**
- Serious limitations in above factors
- Observational studies without special strengths

### Very Low Quality
**Definition:** Very limited confidence; true effect likely substantially different.

**Characteristics:**
- Very serious limitations
- Expert opinion
- Multiple serious flaws

## Study Quality Assessment Criteria

### Internal Validity (Bias Control)
**Questions:**
- Was randomization adequate?
- Was allocation concealed?
- Were groups similar at baseline?
- Was blinding implemented?
- Was attrition minimal and balanced?
- Was intention-to-treat used?
- Were all outcomes reported?

### External Validity (Generalizability)
**Questions:**
- Is sample representative of target population?
- Are inclusion/exclusion criteria too restrictive?
- Is setting realistic?
- Are results applicable to other populations?
- Are effects consistent across subgroups?

### Statistical Conclusion Validity
**Questions:**
- Was sample size adequate (power)?
- Were statistical tests appropriate?
- Were assumptions checked?
- Were effect sizes and confidence intervals reported?
- Were multiple comparisons addressed?
- Was analysis prespecified?

### Construct Validity (Measurement)
**Questions:**
- Were measures validated and reliable?
- Was outcome defined clearly and appropriately?
- Were assessors blinded?
- Were exposures measured accurately?
- Was timing of measurement appropriate?

## Critical Appraisal Tools

### For Different Study Types

**RCTs:**
- Cochrane RoB 2 (Risk of Bias 2) — current standard for randomized trials
- PEDro Scale (for trials in physical therapy)
- Legacy: Cochrane RoB 1, Jadad Scale (historical; prefer RoB 2 for new reviews)

**Observational Studies:**
- ROBINS-I (Risk of Bias in Non-randomized Studies — of Interventions)
- Newcastle-Ottawa Scale

**Diagnostic Studies:**
- QUADAS-2 (Quality Assessment of Diagnostic Accuracy Studies)

**Systematic Reviews:**
- PRISMA 2020 checklist (reporting standard for systematic reviews)
- AMSTAR-2 (A Measurement Tool to Assess Systematic Reviews)

**All Study Types:**
- CASP Checklists (Critical Appraisal Skills Programme)

## Domain-Specific Considerations

### Basic Science Research
**Hierarchy differs:**
1. Multiple convergent lines of evidence
2. Mechanistic understanding
3. Reproducible experiments
4. Established theoretical framework

**Key considerations:**
- Replication essential
- Mechanistic plausibility
- Consistency across model systems
- Convergence of methods

### Psychological Research
**Additional concerns:**
- Replication crisis
- Publication bias particularly problematic
- Small effect sizes often expected
- Cultural context matters
- Measures often indirect (self-report)

**Strong evidence includes:**
- Preregistered studies
- Large samples
- Multiple measures
- Behavioral (not just self-report) outcomes
- Cross-cultural replication

### Epidemiology
**Causal inference frameworks:**
- Bradford Hill criteria
- Rothman's causal pies
- Directed Acyclic Graphs (DAGs)

**Strong observational evidence:**
- Dose-response relationships
- Temporal consistency
- Biological plausibility
- Specificity
- Consistency across populations
- Large effects unlikely due to confounding

### Social Sciences
**Challenges:**
- Complex interventions
- Context-dependent effects
- Measurement challenges
- Ethical constraints on RCTs

**Strengthening evidence:**
- Mixed methods
- Natural experiments
- Instrumental variables
- Regression discontinuity designs
- Multiple operationalizations

## Synthesizing Evidence Across Studies

### Consistency
**Strong evidence:**
- Multiple studies, different investigators
- Different populations and settings
- Different research designs converge
- Different measurement methods

**Weak evidence:**
- Single study
- Only one research group
- Conflicting results
- Publication bias evident

### Biological/Theoretical Plausibility
**Strengthens evidence:**
- Known mechanism
- Consistent with other knowledge
- Dose-response relationship
- Coherent with animal/in vitro data

**Weakens evidence:**
- No plausible mechanism
- Contradicts established knowledge
- Biological implausibility

### Temporality
**Essential for causation:**
- Cause must precede effect
- Cross-sectional studies cannot establish
- Reverse causation must be ruled out

### Specificity
**Moderate indicator:**
- Specific cause → specific effect strengthens causation
- But lack of specificity doesn't rule out causation
- Most causes have multiple effects

### Strength of Association
**Strong evidence:**
- Large effects unlikely to be due to confounding
- Dose-response relationships
- All-or-none effects

**Caution:**
- Small effects may still be real
- Large effects can still be confounded

## Red Flags in Evidence Quality

### Study Design Red Flags
- No control group
- Self-selected participants
- No randomization when feasible
- No blinding when feasible
- Very small sample
- Inappropriate statistical tests

### Reporting Red Flags
- Selective outcome reporting
- No study registration/protocol
- Missing methodological details
- No conflicts of interest statement
- Cherry-picked citations
- Results don't match methods

### Interpretation Red Flags
- Causal language from correlational data
- Claiming "proof"
- Ignoring limitations
- Overgeneralizing
- Spinning negative results
- Post hoc rationalization

### Context Red Flags
- Industry funding without independence
- Single study in isolation
- Contradicts preponderance of evidence
- No replication
- Published in predatory journal
- Press release before peer review

## Practical Decision Framework

### When Evaluating Evidence, Ask:

1. **What type of study is this?** (Design)
2. **How well was it conducted?** (Quality)
3. **What does it actually show?** (Results)
4. **How likely is bias?** (Internal validity)
5. **Does it apply to my question?** (External validity)
6. **How does it fit with other evidence?** (Context)
7. **Are the conclusions justified?** (Interpretation)
8. **What are the limitations?** (Uncertainty)

### Making Decisions with Imperfect Evidence

**High-quality evidence:**
- Strong confidence in acting on findings
- Reasonable to change practice/policy

**Moderate-quality evidence:**
- Provisional conclusions
- Consider in conjunction with other factors
- May warrant action depending on stakes

**Low-quality evidence:**
- Weak confidence
- Hypothesis-generating
- Insufficient for major decisions alone
- Consider cost/benefit of waiting for better evidence

**Very low-quality evidence:**
- Very uncertain
- Should not drive decisions alone
- Useful for identifying gaps and research needs

### When Evidence is Conflicting

**Strategies:**
1. Weight by study quality
2. Look for systematic differences (population, methods)
3. Consider publication bias
4. Update with most recent, rigorous evidence
5. Conduct/await systematic review
6. Consider if question is well-formed

## Communicating Evidence Strength

**Avoid:**
- Absolute certainty ("proves")
- False balance (equal weight to unequal evidence)
- Ignoring uncertainty
- Cherry-picking studies

**Better:**
- Quantify uncertainty
- Describe strength of evidence
- Acknowledge limitations
- Present range of evidence
- Distinguish established from emerging findings
- Be clear about what is/isn't known

### `references/experimental_design.md`

# Experimental Design Checklist

## Research Question Formulation

### Is the Question Well-Formed?
- [ ] **Specific:** Clearly defined variables and relationships
- [ ] **Answerable:** Can be addressed with available methods
- [ ] **Relevant:** Addresses a gap in knowledge or practical need
- [ ] **Feasible:** Resources, time, and ethical considerations allow it
- [ ] **Falsifiable:** Can be proven wrong if incorrect

### Have You Reviewed the Literature?
- [ ] Identified what's already known
- [ ] Found gaps or contradictions to address
- [ ] Learned from methodological successes and failures
- [ ] Identified appropriate outcome measures
- [ ] Determined typical effect sizes in the field

## Hypothesis Development

### Is Your Hypothesis Testable?
- [ ] Makes specific, quantifiable predictions
- [ ] Variables are operationally defined
- [ ] Specifies direction/nature of expected relationships
- [ ] Can be falsified by potential observations

### Types of Hypotheses
- [ ] **Null hypothesis (H₀):** No effect/relationship exists
- [ ] **Alternative hypothesis (H₁):** Effect/relationship exists
- [ ] **Directional vs. non-directional:** One-tailed vs. two-tailed tests

## Study Design Selection

### What Type of Study is Appropriate?

**Experimental (Intervention) Studies:**
- [ ] **Randomized Controlled Trial (RCT):** Gold standard for causation
- [ ] **Quasi-experimental:** Non-random assignment but manipulation
- [ ] **Within-subjects:** Same participants in all conditions
- [ ] **Between-subjects:** Different participants per condition
- [ ] **Factorial:** Multiple independent variables
- [ ] **Crossover:** Participants receive multiple interventions sequentially

**Observational Studies:**
- [ ] **Cohort:** Follow groups over time
- [ ] **Case-control:** Compare those with/without outcome
- [ ] **Cross-sectional:** Snapshot at one time point
- [ ] **Ecological:** Population-level data

**Consider:**
- [ ] Can you randomly assign participants?
- [ ] Can you manipulate the independent variable?
- [ ] Is the outcome rare (favor case-control) or common?
- [ ] Do you need to establish temporal sequence?
- [ ] What's feasible given ethical, practical constraints?

## Variables

### Independent Variables (Manipulated/Predictor)
- [ ] Clearly defined and operationalized
- [ ] Appropriate levels/categories chosen
- [ ] Manipulation is sufficient to test hypothesis
- [ ] Manipulation check planned (if applicable)

### Dependent Variables (Outcome/Response)
- [ ] Directly measures the construct of interest
- [ ] Validated and reliable measurement
- [ ] Sensitive enough to detect expected effects
- [ ] Appropriate for statistical analysis planned
- [ ] Primary outcome clearly designated

### Control Variables
- [ ] **Confounding variables identified:**
  - Variables that affect both IV and DV
  - Alternative explanations for findings
- [ ] **Strategy for control:**
  - Randomization
  - Matching
  - Stratification
  - Statistical adjustment
  - Restriction (inclusion/exclusion criteria)
  - Blinding

### Extraneous Variables
- [ ] Potential sources of noise identified
- [ ] Standardized procedures to minimize
- [ ] Environmental factors controlled
- [ ] Time of day, setting, equipment standardized

## Sampling

### Population Definition
- [ ] **Target population:** Who you want to generalize to
- [ ] **Accessible population:** Who you can actually sample from
- [ ] **Sample:** Who actually participates
- [ ] Difference between these documented

### Sampling Method
- [ ] **Probability sampling (preferred for generalizability):**
  - Simple random sampling
  - Stratified sampling
  - Cluster sampling
  - Systematic sampling
- [ ] **Non-probability sampling (common but limits generalizability):**
  - Convenience sampling
  - Purposive sampling
  - Snowball sampling
  - Quota sampling

### Sample Size
- [ ] **A priori power analysis conducted**
  - Expected effect size (from literature or pilot)
  - Desired power (typically .80 or .90)
  - Significance level (typically .05)
  - Statistical test to be used
- [ ] Accounts for expected attrition/dropout
- [ ] Sufficient for planned subgroup analyses
- [ ] Practical constraints acknowledged

### Inclusion/Exclusion Criteria
- [ ] Clearly defined and justified
- [ ] Not overly restrictive (limits generalizability)
- [ ] Based on theoretical or practical considerations
- [ ] Ethical considerations addressed
- [ ] Documented and applied consistently

## Blinding and Randomization

### Randomization
- [ ] **What is randomized:**
  - Participant assignment to conditions
  - Order of conditions (within-subjects)
  - Stimuli/items presented
- [ ] **Method of randomization:**
  - Computer-generated random numbers
  - Random number tables
  - Coin flips (for very small studies)
- [ ] **Allocation concealment:**
  - Sequence generated before recruitment
  - Allocation hidden until after enrollment
  - Sequentially numbered, sealed envelopes (if needed)
- [ ] **Stratified randomization:**
  - Balance important variables across groups
  - Block randomization to ensure equal group sizes
- [ ] **Check randomization:**
  - Compare groups at baseline
  - Report any significant differences

### Blinding
- [ ] **Single-blind:** Participants don't know group assignment
- [ ] **Double-blind:** Participants and researchers don't know
- [ ] **Triple-blind:** Participants, researchers, and data analysts don't know
- [ ] **Blinding feasibility:**
  - Is true blinding possible?
  - Placebo/sham controls needed?
  - Identical appearance of interventions?
- [ ] **Blinding check:**
  - Assess whether blinding maintained
  - Ask participants/researchers to guess assignments

## Control Groups and Conditions

### What Type of Control?
- [ ] **No treatment control:** Natural course of condition
- [ ] **Placebo control:** Inert treatment for comparison
- [ ] **Active control:** Standard treatment comparison
- [ ] **Wait-list control:** Delayed treatment
- [ ] **Attention control:** Matches contact time without active ingredient

### Multiple Conditions
- [ ] Factorial designs for multiple factors
- [ ] Dose-response relationship assessment
- [ ] Mechanism testing with component analyses

## Procedures

### Protocol Development
- [ ] **Detailed, written protocol:**
  - Step-by-step procedures
  - Scripts for standardized instructions
  - Decision rules for handling issues
  - Data collection forms
- [ ] Pilot tested before main study
- [ ] Staff trained to criterion
- [ ] Compliance monitoring planned

### Standardization
- [ ] Same instructions for all participants
- [ ] Same equipment and materials
- [ ] Same environment/setting when possible
- [ ] Same assessment timing
- [ ] Deviations from protocol documented

### Data Collection
- [ ] **When collected:**
  - Baseline measurements
  - Post-intervention
  - Follow-up timepoints
- [ ] **Who collects:**
  - Trained researchers
  - Blinded when possible
  - Inter-rater reliability established
- [ ] **How collected:**
  - Valid, reliable instruments
  - Standardized administration
  - Multiple methods if possible (triangulation)

## Measurement

### Validity
- [ ] **Face validity:** Appears to measure construct
- [ ] **Content validity:** Covers all aspects of construct
- [ ] **Criterion validity:** Correlates with gold standard
  - Concurrent validity
  - Predictive validity
- [ ] **Construct validity:** Measures theoretical construct
  - Convergent validity (correlates with related measures)
  - Discriminant validity (doesn't correlate with unrelated measures)

### Reliability
- [ ] **Test-retest:** Consistent over time
- [ ] **Internal consistency:** Items measure same construct (Cronbach's α)
- [ ] **Inter-rater reliability:** Agreement between raters (Cohen's κ, ICC)
- [ ] **Parallel forms:** Alternative versions consistent

### Measurement Considerations
- [ ] Objective measures preferred when possible
- [ ] Validated instruments used when available
- [ ] Multiple measures of key constructs
- [ ] Sensitivity to change considered
- [ ] Floor/ceiling effects avoided
- [ ] Response formats appropriate
- [ ] Recall periods appropriate
- [ ] Cultural appropriateness considered

## Bias Minimization

### Selection Bias
- [ ] Random sampling when possible
- [ ] Clearly defined eligibility criteria
- [ ] Document who declines and why
- [ ] Minimize self-selection

### Performance Bias
- [ ] Standardized protocols
- [ ] Blinding of providers
- [ ] Monitor protocol adherence
- [ ] Document deviations

### Detection Bias
- [ ] Blinding of outcome assessors
- [ ] Objective measures when possible
- [ ] Standardized assessment procedures
- [ ] Multiple raters with reliability checks

### Attrition Bias
- [ ] Strategies to minimize dropout
- [ ] Track reasons for dropout
- [ ] Compare dropouts to completers
- [ ] Intention-to-treat analysis planned

### Reporting Bias
- [ ] Preregister study and analysis plan
- [ ] Designate primary vs. secondary outcomes
- [ ] Commit to reporting all outcomes
- [ ] Distinguish planned from exploratory analyses

## Data Management

### Data Collection
- [ ] Data collection forms designed and tested
- [ ] REDCap, Qualtrics, or similar platforms
- [ ] Range checks and validation rules
- [ ] Regular backups
- [ ] Secure storage (HIPAA/GDPR compliant if needed)

### Data Quality
- [ ] Real-time data validation
- [ ] Regular quality checks
- [ ] Missing data patterns monitored
- [ ] Outliers identified and investigated
- [ ] Protocol deviations documented

### Data Security
- [ ] De-identification procedures
- [ ] Access controls
- [ ] Audit trails
- [ ] Compliance with regulations (IRB, HIPAA, GDPR)

## Statistical Analysis Planning

### Analysis Plan (Prespecify Before Data Collection)
- [ ] **Primary analysis:**
  - Statistical test(s) specified
  - Hypothesis clearly stated
  - Significance level set (usually α = .05)
  - One-tailed or two-tailed
- [ ] **Secondary analyses:**
  - Clearly designated as secondary
  - Exploratory analyses labeled as such
- [ ] **Multiple comparisons:**
  - Adjustment method specified (if needed)
  - Primary outcome protects from inflation

### Assumptions
- [ ] Assumptions of statistical tests identified
- [ ] Plan to check assumptions
- [ ] Backup non-parametric alternatives
- [ ] Transformation options considered

### Missing Data
- [ ] Anticipated amount of missingness
- [ ] Missing data mechanism (MCAR, MAR, MNAR)
- [ ] Handling strategy:
  - Complete case analysis
  - Multiple imputation
  - Maximum likelihood
- [ ] Sensitivity analyses planned

### Effect Sizes
- [ ] Appropriate effect size measures identified
- [ ] Will be reported alongside p-values
- [ ] Confidence intervals planned

### Statistical Software
- [ ] Software selected (R, SPSS, Stata, Python, etc.)
- [ ] Version documented
- [ ] Analysis scripts prepared in advance
- [ ] Will be made available (Open Science)

## Ethical Considerations

### Ethical Approval
- [ ] IRB/Ethics committee approval obtained
- [ ] Study registered (ClinicalTrials.gov, etc.) if applicable
- [ ] Protocol follows Declaration of Helsinki or equivalent

### Informed Consent
- [ ] Voluntary participation
- [ ] Comprehensible explanation
- [ ] Risks and benefits disclosed
- [ ] Right to withdraw without penalty
- [ ] Privacy protections explained
- [ ] Compensation disclosed

### Risk-Benefit Analysis
- [ ] Potential benefits outweigh risks
- [ ] Risks minimized
- [ ] Vulnerable populations protected
- [ ] Data safety monitoring (if high risk)

### Confidentiality
- [ ] Data de-identified
- [ ] Secure storage
- [ ] Limited access
- [ ] Reporting doesn't allow re-identification

## Validity Threats

### Internal Validity (Causation)
- [ ] **History:** External events between measurements
- [ ] **Maturation:** Changes in participants over time
- [ ] **Testing:** Effects of repeated measurement
- [ ] **Instrumentation:** Changes in measurement over time
- [ ] **Regression to mean:** Extreme scores becoming less extreme
- [ ] **Selection:** Groups differ at baseline
- [ ] **Attrition:** Differential dropout
- [ ] **Diffusion:** Control group receives treatment elements

### External Validity (Generalizability)
- [ ] Sample representative of population
- [ ] Setting realistic/natural
- [ ] Treatment typical of real-world implementation
- [ ] Outcome measures ecologically valid
- [ ] Time frame appropriate

### Construct Validity (Measurement)
- [ ] Measures actually tap intended constructs
- [ ] Operations match theoretical definitions
- [ ] No confounding of constructs
- [ ] Adequate coverage of construct

### Statistical Conclusion Validity
- [ ] Adequate statistical power
- [ ] Assumptions met
- [ ] Appropriate tests used
- [ ] Alpha level appropriate
- [ ] Multiple comparisons addressed

## Reporting and Transparency

### Preregistration
- [ ] Study preregistered (OSF, ClinicalTrials.gov, AsPredicted)
- [ ] Hypotheses stated a priori
- [ ] Analysis plan documented
- [ ] Distinguishes confirmatory from exploratory

### Reporting Guidelines
- [ ] **RCTs:** CONSORT 2010 checklist (with applicable extensions)
- [ ] **Observational studies:** STROBE checklist
- [ ] **Systematic reviews:** PRISMA 2020 checklist
- [ ] **Diagnostic studies:** STARD checklist
- [ ] **Qualitative research:** COREQ checklist
- [ ] **Case reports:** CARE guidelines

### Transparency
- [ ] All measures reported
- [ ] All manipulations disclosed
- [ ] Sample size determination explained
- [ ] Exclusion criteria and numbers reported
- [ ] Attrition documented
- [ ] Deviations from protocol noted
- [ ] Conflicts of interest disclosed

### Open Science
- [ ] Data sharing planned (when ethical)
- [ ] Analysis code shared
- [ ] Materials available
- [ ] Preprint posted
- [ ] Open access publication when possible

## Post-Study Considerations

### Data Analysis
- [ ] Follow preregistered plan
- [ ] Clearly label deviations and exploratory analyses
- [ ] Check assumptions
- [ ] Report all outcomes
- [ ] Report effect sizes and CIs, not just p-values

### Interpretation
- [ ] Conclusions supported by data
- [ ] Limitations acknowledged
- [ ] Alternative explanations considered
- [ ] Generalizability discussed
- [ ] Clinical/practical significance addressed

### Dissemination
- [ ] Publish regardless of results (reduce publication bias)
- [ ] Present at conferences
- [ ] Share findings with participants (when appropriate)
- [ ] Communicate to relevant stakeholders
- [ ] Plain language summaries

### Next Steps
- [ ] Replication needed?
- [ ] Follow-up studies identified
- [ ] Mechanism studies planned
- [ ] Clinical applications considered

## Common Pitfalls to Avoid

- [ ] No power analysis → underpowered study
- [ ] Hypothesis formed after seeing data (HARKing)
- [ ] No blinding when feasible → bias
- [ ] P-hacking (data fishing, optional stopping)
- [ ] Multiple testing without correction → false positives
- [ ] Inadequate control group
- [ ] Confounding not addressed
- [ ] Instruments not validated
- [ ] High attrition not addressed
- [ ] Cherry-picking results to report
- [ ] Causal language from correlational data
- [ ] Ignoring assumptions of statistical tests
- [ ] Not preregistering changes literature bias
- [ ] Conflicts of interest not disclosed

## Final Checklist Before Starting

- [ ] Research question is clear and important
- [ ] Hypothesis is testable and specific
- [ ] Study design is appropriate
- [ ] Sample size is adequate (power analysis)
- [ ] Measures are valid and reliable
- [ ] Confounds are controlled
- [ ] Randomization and blinding implemented
- [ ] Data collection is standardized
- [ ] Analysis plan is prespecified
- [ ] Ethical approval obtained
- [ ] Study is preregistered
- [ ] Resources are sufficient
- [ ] Team is trained
- [ ] Protocol is documented
- [ ] Backup plans exist for problems

## Remember

**Good experimental design is about:**
- Asking clear questions
- Minimizing bias
- Maximizing validity
- Appropriate inference
- Transparency
- Reproducibility

**The best time to think about these issues is before collecting data, not after.**

### `references/logical_fallacies.md`

# Logical Fallacies in Scientific Discourse

## Fallacies of Causation

### 1. Post Hoc Ergo Propter Hoc (After This, Therefore Because of This)
**Description:** Assuming that because B happened after A, A caused B.

**Examples:**
- "I took this supplement and my cold went away, so the supplement cured my cold."
- "Autism diagnoses increased after vaccine schedules changed, so vaccines cause autism."
- "I wore my lucky socks and won the game, so the socks caused the win."

**Why fallacious:** Temporal sequence is necessary but not sufficient for causation. Correlation ≠ causation.

**Related:** *Cum hoc ergo propter hoc* (with this, therefore because of this) - correlation mistaken for causation even without temporal order.

### 2. Confusing Correlation with Causation
**Description:** Assuming correlation implies direct causal relationship.

**Examples:**
- "Countries that eat more chocolate have more Nobel Prize winners, so chocolate makes you smarter."
- "Ice cream sales correlate with drowning deaths, so ice cream causes drowning."

**Reality:** Often due to confounding variables (hot weather causes both ice cream sales and swimming).

### 3. Reverse Causation
**Description:** Confusing cause and effect direction.

**Examples:**
- "Depression is associated with inflammation, so inflammation causes depression." (Could be: depression causes inflammation)
- "Wealthy people are healthier, so wealth causes health." (Could be: health enables wealth accumulation)

**Solution:** Longitudinal studies and experimental designs to establish temporal order.

### 4. Single Cause Fallacy
**Description:** Attributing complex phenomena to one cause when multiple factors contribute.

**Examples:**
- "Crime is caused by poverty." (Ignores many other contributing factors)
- "Heart disease is caused by fat intake." (Oversimplifies multifactorial disease)

**Reality:** Most outcomes have multiple contributing causes.

## Fallacies of Generalization

### 5. Hasty Generalization
**Description:** Drawing broad conclusions from insufficient evidence.

**Examples:**
- "My uncle smoked and lived to 90, so smoking isn't dangerous."
- "This drug worked in 5 patients, so it's effective for everyone."
- "I saw three black swans, so all swans are black."

**Why fallacious:** Small, unrepresentative samples don't support universal claims.

### 6. Anecdotal Fallacy
**Description:** Using personal experience or isolated examples as proof.

**Examples:**
- "I know someone who survived cancer using alternative medicine, so it works."
- "My grandmother never exercised and lived to 100, so exercise is unnecessary."

**Why fallacious:** Anecdotes are unreliable due to selection bias, memory bias, and confounding. Plural of anecdote ≠ data.

### 7. Cherry Picking (Suppressing Evidence)
**Description:** Selecting only evidence that supports your position while ignoring contradictory evidence.

**Examples:**
- Citing only studies showing supplement benefits while ignoring null findings
- Highlighting successful predictions while ignoring failed ones
- Showing graphs that start at convenient points

**Detection:** Look for systematic reviews, not individual studies.

### 8. Ecological Fallacy
**Description:** Inferring individual characteristics from group statistics.

**Example:**
- "Average income in this neighborhood is high, so this person must be wealthy."
- "This country has low disease rates, so any individual from there is unlikely to have disease."

**Why fallacious:** Group-level patterns don't necessarily apply to individuals.

## Fallacies of Authority and Tradition

### 9. Appeal to Authority (Argumentum ad Verecundiam)
**Description:** Accepting claims because an authority figure said them, without evidence.

**Examples:**
- "Dr. X says this treatment works, so it must." (If Dr. X provides no data)
- "Einstein believed in God, so God exists." (Einstein's physics expertise doesn't transfer)
- "99% of doctors recommend..." (Appeal to majority + authority without evidence)

**Valid use of authority:** Experts providing evidence-based consensus in their domain.

**Invalid:** Authority opinions without evidence, or outside their expertise.

### 10. Appeal to Antiquity/Tradition
**Description:** Assuming something is true or good because it's old or traditional.

**Examples:**
- "Traditional medicine has been used for thousands of years, so it must work."
- "This theory has been accepted for decades, so it must be correct."

**Why fallacious:** Age doesn't determine validity. Many old beliefs have been disproven.

### 11. Appeal to Novelty
**Description:** Assuming something is better because it's new.

**Examples:**
- "This is the latest treatment, so it must be superior."
- "New research overturns everything we knew." (Often overstated)

**Why fallacious:** New ≠ better. Established treatments often outperform novel ones.

## Fallacies of Relevance

### 12. Ad Hominem (Attack the Person)
**Description:** Attacking the person making the argument rather than the argument itself.

**Types:**
- **Abusive:** "He's an idiot, so his theory is wrong."
- **Circumstantial:** "She's funded by industry, so her findings are false."
- **Tu Quoque:** "You smoke, so your anti-smoking argument is invalid."

**Why fallacious:** Personal characteristics don't determine argument validity.

**Note:** Conflicts of interest are worth noting but don't invalidate evidence.

### 13. Genetic Fallacy
**Description:** Judging something based on its origin rather than its merits.

**Examples:**
- "This idea came from a drug company, so it's wrong."
- "Ancient Greeks believed this, so it's outdated."

**Better approach:** Evaluate evidence regardless of source.

### 14. Appeal to Emotion
**Description:** Manipulating emotions instead of presenting evidence.

**Types:**
- **Appeal to fear:** "If you don't vaccinate, your child will die."
- **Appeal to pity:** "Think of the suffering patients who need this unproven treatment."
- **Appeal to flattery:** "Smart people like you know that..."

**Why fallacious:** Emotional reactions don't determine truth.

### 15. Appeal to Consequences (Argumentum ad Consequentiam)
**Description:** Arguing something is true/false based on whether consequences are desirable.

**Examples:**
- "Climate change can't be real because the solutions would hurt the economy."
- "Free will must exist because without it, morality is impossible."

**Why fallacious:** Reality is independent of what we wish were true.

### 16. Appeal to Nature (Naturalistic Fallacy)
**Description:** Assuming "natural" means good, safe, or effective.

**Examples:**
- "This treatment is natural, so it's safe."
- "Organic food is natural, so it's healthier."
- "Vaccines are unnatural, so they're harmful."

**Why fallacious:**
- Many natural things are deadly (arsenic, snake venom, hurricanes)
- Many synthetic things are beneficial (antibiotics, vaccines)
- "Natural" is often poorly defined

### 17. Moralistic Fallacy
**Description:** Assuming what ought to be true is true.

**Examples:**
- "There shouldn't be sex differences in ability, so they don't exist."
- "People should be rational, so they are."

**Why fallacious:** Desires about reality don't change reality.

## Fallacies of Structure

### 18. False Dichotomy (False Dilemma)
**Description:** Presenting only two options when more exist.

**Examples:**
- "Either you're with us or against us."
- "It's either genetic or environmental." (Usually both)
- "Either the treatment works or it doesn't." (Ignores partial effects)

**Reality:** Most issues have multiple options and shades of gray.

### 19. Begging the Question (Circular Reasoning)
**Description:** Assuming what you're trying to prove.

**Examples:**
- "This medicine works because it has healing properties." (What are healing properties? That it works!)
- "God exists because the Bible says so, and the Bible is true because it's God's word."

**Detection:** Check if the conclusion is hidden in the premises.

### 20. Moving the Goalposts
**Description:** Changing standards of evidence after initial standards are met.

**Example:**
- Skeptic: "Show me one study."
- [Shows study]
- Skeptic: "That's just one study; show me a meta-analysis."
- [Shows meta-analysis]
- Skeptic: "But meta-analyses have limitations..."

**Why problematic:** No amount of evidence will ever be sufficient.

### 21. Slippery Slope
**Description:** Arguing that one step will inevitably lead to extreme outcomes without justification.

**Example:**
- "If we allow gene editing for disease, we'll end up with designer babies and eugenics."

**When valid:** If intermediate steps are actually likely.

**When fallacious:** If chain of events is speculative without evidence.

### 22. Straw Man
**Description:** Misrepresenting an argument to make it easier to attack.

**Example:**
- Position: "We should teach evolution in schools."
- Straw man: "So you think we should tell kids they're just monkeys?"

**Detection:** Ask: Is this really what they're claiming?

## Fallacies of Statistical and Scientific Reasoning

### 23. Texas Sharpshooter Fallacy
**Description:** Cherry-picking data clusters to fit a pattern, like shooting arrows then drawing targets around them.

**Examples:**
- Finding cancer clusters and claiming environmental causes (without accounting for random clustering)
- Data mining until finding significant correlations

**Why fallacious:** Patterns in random data are inevitable; finding them doesn't prove causation.

### 24. Base Rate Fallacy
**Description:** Ignoring prior probability when evaluating evidence.

**Example:**
- Disease affects 0.1% of population; test is 99% accurate
- Positive test ≠ 99% probability of disease
- Actually ~9% probability (due to false positives exceeding true positives)

**Solution:** Use Bayesian reasoning; consider base rates.

### 25. Prosecutor's Fallacy
**Description:** Confusing P(Evidence|Innocent) with P(Innocent|Evidence).

**Example:**
- "The probability of this DNA match occurring by chance is 1 in 1 million, so there's only a 1 in 1 million chance the defendant is innocent."

**Why fallacious:** Ignores base rates and prior probability.

### 26. McNamara Fallacy (Quantitative Fallacy)
**Description:** Focusing only on what can be easily measured while ignoring important unmeasured factors.

**Example:**
- Judging school quality only by test scores (ignoring creativity, social skills, ethics)
- Measuring healthcare only by quantifiable outcomes (ignoring quality of life)

**Quote:** "Not everything that counts can be counted, and not everything that can be counted counts."

### 27. Multiple Comparisons Fallacy
**Description:** Not accounting for increased false positive rate when testing many hypotheses.

**Example:**
- Testing 20 hypotheses at p < .05 gives ~65% chance of at least one false positive
- Claiming jellybean color X causes acne after testing 20 colors

**Solution:** Correct for multiple comparisons (Bonferroni, FDR).

### 28. Reification (Hypostatization)
**Description:** Treating abstract concepts as if they were concrete things.

**Examples:**
- "Evolution wants organisms to survive." (Evolution doesn't "want")
- "The gene for intelligence" (Intelligence isn't one gene)
- "Nature selects..." (Nature doesn't consciously select)

**Why problematic:** Can lead to confused thinking about mechanisms.

## Fallacies of Scope and Definition

### 29. No True Scotsman
**Description:** Retroactively excluding counterexamples by redefining criteria.

**Example:**
- "No natural remedy has side effects."
- "But poison ivy is natural and causes reactions."
- "Well, no *true* natural remedy has side effects."

**Why fallacious:** Moves goalposts to protect claim from falsification.

### 30. Equivocation
**Description:** Using a word with multiple meanings inconsistently.

**Example:**
- "Evolution is just a theory. Theories are guesses. So evolution is just a guess."
- (Conflates colloquial "theory" with scientific "theory")

**Detection:** Check if key terms are used consistently.

### 31. Ambiguity
**Description:** Using vague language that can be interpreted multiple ways.

**Example:**
- "Quantum healing" (What does "quantum" mean here?)
- "Natural" (Animals? Not synthetic? Organic? Common?)

**Why problematic:** Claims become unfalsifiable when terms are undefined.

### 32. Mind Projection Fallacy
**Description:** Projecting mental constructs onto reality.

**Example:**
- Assuming categories that exist in language exist in nature
- "Which chromosome is the gene for X on?" when X is polygenic and partially environmental

**Better:** Recognize human categories may not carve nature at the joints.

## Fallacies Specific to Science

### 33. Galileo Gambit
**Description:** "They laughed at Galileo, and he was right, so if they're laughing at me, I must be right too."

**Why fallacious:**
- They laughed at Galileo, and he was right
- They also laughed at countless crackpots who were wrong
- Being an outsider doesn't make you right

**Reality:** Revolutionary ideas are usually well-supported by evidence.

### 34. Argument from Ignorance (Ad Ignorantiam)
**Description:** Assuming something is true because it hasn't been proven false (or vice versa).

**Examples:**
- "No one has proven homeopathy doesn't work, so it works."
- "We haven't found evidence of harm, so it must be safe."

**Why fallacious:** Absence of evidence ≠ evidence of absence (though it can be, depending on how hard we've looked).

**Burden of proof:** Falls on the claimant, not the skeptic.

### 35. God of the Gaps
**Description:** Explaining gaps in knowledge by invoking supernatural or unfalsifiable causes.

**Examples:**
- "We don't fully understand consciousness, so it must be spiritual."
- "This complexity couldn't arise naturally, so it must be designed."

**Why problematic:**
- Fills gaps with non-explanations
- Discourages genuine investigation
- History shows gaps get filled by natural explanations

### 36. Nirvana Fallacy (Perfect Solution Fallacy)
**Description:** Rejecting solutions because they're imperfect.

**Examples:**
- "Vaccines aren't 100% effective, so they're worthless."
- "This diet doesn't work for everyone, so it doesn't work."

**Reality:** Most interventions are partial; perfection is rare.

**Better:** Compare to alternatives, not to perfection.

### 37. Special Pleading
**Description:** Applying standards to others but not to oneself.

**Examples:**
- "My anecdotes count as evidence, but yours don't."
- "Mainstream medicine needs RCTs, but my alternative doesn't."
- "Correlation doesn't imply causation—except when it supports my view."

**Why fallacious:** Evidence standards should apply consistently.

### 38. Unfalsifiability
**Description:** Formulating claims in ways that cannot be tested or disproven.

**Examples:**
- "This energy can't be detected by any instrument."
- "It works, but only if you truly believe."
- "Failures prove the conspiracy is even deeper."

**Why problematic:** Unfalsifiable claims aren't scientific; they can't be tested.

**Good science:** Makes specific, testable predictions.

### 39. Affirming the Consequent
**Description:** If A, then B. B is true. Therefore, A is true.

**Example:**
- "If the drug works, symptoms improve. Symptoms improved. Therefore, the drug worked."
- (Could be placebo, natural history, regression to mean)

**Why fallacious:** Other causes could produce the same outcome.

**Valid form:** Modus ponens: If A, then B. A is true. Therefore, B is true.

### 40. Denying the Antecedent
**Description:** If A, then B. A is false. Therefore, B is false.

**Example:**
- "If you have fever, you have infection. You don't have fever. Therefore, you don't have infection."

**Why fallacious:** B can be true even when A is false.

## Avoiding Logical Fallacies

### Practical Steps

1. **Identify the claim** - What exactly is being argued?

2. **Identify the evidence** - What supports the claim?

3. **Check the logic** - Does the evidence actually support the claim?

4. **Look for hidden assumptions** - What unstated beliefs does the argument rely on?

5. **Consider alternatives** - What other explanations fit the evidence?

6. **Check for emotional manipulation** - Is the argument relying on feelings rather than facts?

7. **Evaluate the source** - Are there conflicts of interest? Is this within their expertise?

8. **Look for balance** - Are counterarguments addressed fairly?

9. **Assess the evidence** - Is it anecdotal, observational, or experimental? How strong?

10. **Be charitable** - Interpret arguments in their strongest form (steel man, not straw man).

### Questions to Ask

- Is the conclusion supported by the premises?
- Are there unstated assumptions?
- Is the evidence relevant to the conclusion?
- Are counterarguments acknowledged?
- Could alternative explanations account for the evidence?
- Is the reasoning consistent?
- Are terms defined clearly?
- Is evidence being cherry-picked?
- Are emotions being manipulated?
- Would this reasoning apply consistently to other cases?

### Common Patterns

**Good Arguments:**
- Clearly defined terms
- Relevant, sufficient evidence
- Valid logical structure
- Acknowledges limitations and alternatives
- Proportional conclusions
- Transparent about uncertainty
- Applies consistent standards

**Poor Arguments:**
- Vague or shifting definitions
- Irrelevant or insufficient evidence
- Logical leaps
- Ignores counterevidence
- Overclaimed conclusions
- False certainty
- Double standards

## Remember

- **Fallacious reasoning doesn't mean the conclusion is false** - just that this argument doesn't support it.
- **Identifying fallacies isn't about winning** - it's about better understanding reality.
- **We all commit fallacies** - recognizing them in ourselves is as important as in others.
- **Charity principle** - Interpret arguments generously; don't assume bad faith.
- **Focus on claims, not people** - Ad hominem goes both ways.

### `references/scientific_method.md`

# Scientific Method Core Principles

## Fundamental Principles

### 1. Empiricism
- Knowledge derives from observable, measurable evidence
- Claims must be testable through observation or experiment
- Subjective experience alone is insufficient for scientific conclusions

### 2. Falsifiability (Popper's Criterion)
- A hypothesis must be capable of being proven false
- Unfalsifiable claims are not scientific (e.g., "invisible, undetectable forces")
- Good hypotheses make specific, testable predictions

### 3. Reproducibility
- Results must be replicable by independent researchers
- Methods must be described with sufficient detail for replication
- Single studies are rarely definitive; replication strengthens confidence

### 4. Parsimony (Occam's Razor)
- Prefer simpler explanations over complex ones when both fit the data
- Don't multiply entities unnecessarily
- Extraordinary claims require extraordinary evidence

### 5. Systematic Observation
- Use standardized, rigorous methods
- Control for confounding variables
- Minimize observer bias through blinding and protocols

## The Scientific Process

### 1. Question Formation
- Identify a specific, answerable question
- Ensure the question is within the scope of scientific inquiry
- Consider whether current methods can address the question

### 2. Literature Review
- Survey existing knowledge
- Identify gaps and contradictions
- Build on previous work rather than reinventing

### 3. Hypothesis Development
- State a clear, testable prediction
- Define variables operationally
- Specify the expected relationship between variables

### 4. Experimental Design
- Choose appropriate methodology
- Identify independent and dependent variables
- Control confounding variables
- Select appropriate sample size and population
- Plan statistical analyses in advance

### 5. Data Collection
- Follow protocols consistently
- Record all observations, including unexpected results
- Maintain detailed lab notebooks or data logs
- Use validated measurement instruments

### 6. Analysis
- Apply appropriate statistical methods
- Test assumptions of statistical tests
- Consider effect size, not just significance
- Look for alternative explanations

### 7. Interpretation
- Distinguish between correlation and causation
- Acknowledge limitations
- Consider alternative interpretations
- Avoid overgeneralizing beyond the data

### 8. Communication
- Report methods transparently
- Include negative results
- Acknowledge conflicts of interest
- Make data and code available when possible

## Critical Evaluation Criteria

### When Reviewing Scientific Work, Ask:

**Validity Questions:**
- Does the study measure what it claims to measure?
- Are the methods appropriate for the research question?
- Were controls adequate?
- Could confounding variables explain the results?

**Reliability Questions:**
- Are measurements consistent?
- Would the study produce similar results if repeated?
- Are inter-rater reliability and measurement precision reported?

**Generalizability Questions:**
- Is the sample representative of the target population?
- Are the conditions realistic or artificial?
- Do the results apply beyond the specific context?

**Statistical Questions:**
- Is the sample size adequate for the analysis?
- Are the statistical tests appropriate?
- Are effect sizes reported alongside p-values?
- Were multiple comparisons corrected?

**Logical Questions:**
- Do the conclusions follow from the data?
- Are alternative explanations considered?
- Are causal claims supported by the study design?
- Are limitations acknowledged?

## Red Flags in Scientific Claims

1. **Cherry-picking data** - Highlighting only supporting evidence
2. **Moving goalposts** - Changing predictions after seeing results
3. **Ad hoc hypotheses** - Adding explanations to rescue a failed prediction
4. **Appeal to authority** - "Expert X says" without evidence
5. **Anecdotal evidence** - Relying on personal stories over systematic data
6. **Correlation implies causation** - Confusing association with causality
7. **Post hoc rationalization** - Explaining results after the fact without prediction
8. **Ignoring base rates** - Not considering prior probability
9. **Confirmation bias** - Seeking only evidence that supports beliefs
10. **Publication bias** - Only positive results get published

## Standards for Causal Inference

### Bradford Hill Criteria (adapted)
1. **Strength** - Strong associations are more likely causal
2. **Consistency** - Repeated observations by different researchers
3. **Specificity** - Specific outcomes from specific causes
4. **Temporality** - Cause precedes effect (essential)
5. **Biological gradient** - Dose-response relationship
6. **Plausibility** - Coherent with existing knowledge
7. **Coherence** - Consistent with other evidence
8. **Experiment** - Experimental evidence supports causation
9. **Analogy** - Similar cause-effect relationships exist

### Establishing Causation Requires:
- Temporal precedence (cause before effect)
- Covariation (cause and effect correlate)
- Elimination of alternative explanations
- Ideally: experimental manipulation showing cause produces effect

## Peer Review and Scientific Consensus

### Understanding Peer Review
- Filters obvious errors but isn't perfect
- Reviewers can miss problems or have biases
- Published ≠ proven; it means "passed initial scrutiny"
- Retraction mechanisms exist for flawed papers

### Scientific Consensus
- Emerges from convergence of multiple independent lines of evidence
- Consensus can change with new evidence
- Individual studies rarely overturn consensus
- Consider the weight of evidence, not individual papers

## Open Science Principles

### Transparency Practices
- Preregistration of hypotheses and methods
- Open data sharing
- Open-source code
- Preprints for rapid dissemination
- Registered reports (peer review before data collection)

### Why Transparency Matters
- Reduces publication bias
- Enables verification
- Prevents p-hacking and HARKing (Hypothesizing After Results are Known)
- Accelerates scientific progress

### `references/statistical_pitfalls.md`

# Common Statistical Pitfalls

## P-Value Misinterpretations

### Pitfall 1: P-Value = Probability Hypothesis is True
**Misconception:** p = .05 means 5% chance the null hypothesis is true.

**Reality:** P-value is the probability of observing data this extreme (or more) *if* the null hypothesis is true. It says nothing about the probability the hypothesis is true.

**Correct interpretation:** "If there were truly no effect, we would observe data this extreme only 5% of the time."

### Pitfall 2: Non-Significant = No Effect
**Misconception:** p > .05 proves there's no effect.

**Reality:** Absence of evidence ≠ evidence of absence. Non-significant results may indicate:
- Insufficient statistical power
- True effect too small to detect
- High variability
- Small sample size

**Better approach:**
- Report confidence intervals
- Conduct power analysis
- Consider equivalence testing

### Pitfall 3: Significant = Important
**Misconception:** Statistical significance means practical importance.

**Reality:** With large samples, trivial effects become "significant." A statistically significant 0.1 IQ point difference is meaningless in practice.

**Better approach:**
- Report effect sizes
- Consider practical significance
- Use confidence intervals

### Pitfall 4: P = .049 vs. P = .051
**Misconception:** These are meaningfully different because one crosses the .05 threshold.

**Reality:** These represent nearly identical evidence. The .05 threshold is arbitrary.

**Better approach:**
- Treat p-values as continuous measures of evidence
- Report exact p-values
- Consider context and prior evidence

### Pitfall 5: One-Tailed Tests Without Justification
**Misconception:** One-tailed tests are free extra power.

**Reality:** One-tailed tests assume effects can only go one direction, which is rarely true. They're often used to artificially boost significance.

**When appropriate:** Only when effects in one direction are theoretically impossible or equivalent to null.

## Multiple Comparisons Problems

### Pitfall 6: Multiple Testing Without Correction
**Problem:** Testing 20 hypotheses at p < .05 gives ~65% chance of at least one false positive.

**Examples:**
- Testing many outcomes
- Testing many subgroups
- Conducting multiple interim analyses
- Testing at multiple time points

**Solutions:**
- Bonferroni correction (divide α by number of tests)
- False Discovery Rate (FDR) control
- Prespecify primary outcome
- Treat exploratory analyses as hypothesis-generating

### Pitfall 7: Subgroup Analysis Fishing
**Problem:** Testing many subgroups until finding significance.

**Why problematic:**
- Inflates false positive rate
- Often reported without disclosure
- "Interaction was significant in women" may be random

**Solutions:**
- Prespecify subgroups
- Use interaction tests, not separate tests
- Require replication
- Correct for multiple comparisons

### Pitfall 8: Outcome Switching
**Problem:** Analyzing many outcomes, reporting only significant ones.

**Detection signs:**
- Secondary outcomes emphasized
- Incomplete outcome reporting
- Discrepancy between registration and publication

**Solutions:**
- Preregister all outcomes
- Report all planned outcomes
- Distinguish primary from secondary

## Sample Size and Power Issues

### Pitfall 9: Underpowered Studies
**Problem:** Small samples have low probability of detecting true effects.

**Consequences:**
- High false negative rate
- Significant results more likely to be false positives
- Overestimated effect sizes (when significant)

**Solutions:**
- Conduct a priori power analysis
- Aim for 80-90% power
- Consider effect size from prior research

### Pitfall 10: Post-Hoc Power Analysis
**Problem:** Calculating power after seeing results is circular and uninformative.

**Why useless:**
- Non-significant results always have low "post-hoc power"
- It recapitulates the p-value without new information

**Better approach:**
- Calculate confidence intervals
- Plan replication with adequate sample
- Conduct prospective power analysis for future studies

### Pitfall 11: Small Sample Fallacy
**Problem:** Trusting results from very small samples.

**Issues:**
- High sampling variability
- Outliers have large influence
- Assumptions of tests violated
- Confidence intervals very wide

**Guidelines:**
- Be skeptical of n < 30
- Check assumptions carefully
- Consider non-parametric tests
- Replicate findings

## Effect Size Misunderstandings

### Pitfall 12: Ignoring Effect Size
**Problem:** Focusing only on significance, not magnitude.

**Why problematic:**
- Significance ≠ importance
- Can't compare across studies
- Doesn't inform practical decisions

**Solutions:**
- Always report effect sizes
- Use standardized measures (Cohen's d, r, η²)
- Interpret using field conventions
- Consider minimum clinically important difference

### Pitfall 13: Misinterpreting Standardized Effect Sizes
**Problem:** Treating Cohen's d = 0.5 as "medium" without context.

**Reality:**
- Field-specific norms vary
- Some fields have larger typical effects
- Real-world importance depends on context

**Better approach:**
- Compare to effects in same domain
- Consider practical implications
- Look at raw effect sizes too

### Pitfall 14: Confusing Explained Variance with Importance
**Problem:** "Only explains 5% of variance" = unimportant.

**Reality:**
- Height explains ~5% of variation in NBA player salary but is crucial
- Complex phenomena have many small contributors
- Predictive accuracy ≠ causal importance

**Consideration:** Context matters more than percentage alone.

## Correlation and Causation

### Pitfall 15: Correlation Implies Causation
**Problem:** Inferring causation from correlation.

**Alternative explanations:**
- Reverse causation (B causes A, not A causes B)
- Confounding (C causes both A and B)
- Coincidence
- Selection bias

**Criteria for causation:**
- Temporal precedence
- Covariation
- No plausible alternatives
- Ideally: experimental manipulation

### Pitfall 16: Ecological Fallacy
**Problem:** Inferring individual-level relationships from group-level data.

**Example:** Countries with more chocolate consumption have more Nobel laureates doesn't mean eating chocolate makes you win Nobels.

**Why problematic:** Group-level correlations may not hold at individual level.

### Pitfall 17: Simpson's Paradox
**Problem:** Trend appears in groups but reverses when combined (or vice versa).

**Example:** Treatment appears worse overall but better in every subgroup.

**Cause:** Confounding variable distributed differently across groups.

**Solution:** Consider confounders and look at appropriate level of analysis.

## Regression and Modeling Pitfalls

### Pitfall 18: Overfitting
**Problem:** Model fits sample data well but doesn't generalize.

**Causes:**
- Too many predictors relative to sample size
- Fitting noise rather than signal
- No cross-validation

**Solutions:**
- Use cross-validation
- Penalized regression (LASSO, ridge)
- Independent test set
- Simpler models

### Pitfall 19: Extrapolation Beyond Data Range
**Problem:** Predicting outside the range of observed data.

**Why dangerous:**
- Relationships may not hold outside observed range
- Increased uncertainty not reflected in predictions

**Solution:** Only interpolate; avoid extrapolation.

### Pitfall 20: Ignoring Model Assumptions
**Problem:** Using statistical tests without checking assumptions.

**Common violations:**
- Non-normality (for parametric tests)
- Heteroscedasticity (unequal variances)
- Non-independence
- Linearity
- No multicollinearity

**Solutions:**
- Check assumptions with diagnostics
- Use robust methods
- Transform data
- Use appropriate non-parametric alternatives

### Pitfall 21: Treating Non-Significant Covariates as Eliminating Confounding
**Problem:** "We controlled for X and it wasn't significant, so it's not a confounder."

**Reality:** Non-significant covariates can still be important confounders. Significance ≠ confounding.

**Solution:** Include theoretically important covariates regardless of significance.

### Pitfall 22: Collinearity Masking Effects
**Problem:** When predictors are highly correlated, true effects may appear non-significant.

**Manifestations:**
- Large standard errors
- Unstable coefficients
- Sign changes when adding/removing variables

**Detection:**
- Variance Inflation Factors (VIF)
- Correlation matrices

**Solutions:**
- Remove redundant predictors
- Combine correlated variables
- Use regularization methods

## Specific Test Misuses

### Pitfall 23: T-Test for Multiple Groups
**Problem:** Conducting multiple t-tests instead of ANOVA.

**Why wrong:** Inflates Type I error rate dramatically.

**Correct approach:**
- Use ANOVA first
- Follow with planned comparisons or post-hoc tests with correction

### Pitfall 24: Pearson Correlation for Non-Linear Relationships
**Problem:** Using Pearson's r for curved relationships.

**Why misleading:** r measures linear relationships only.

**Solutions:**
- Check scatterplots first
- Use Spearman's ρ for monotonic relationships
- Consider polynomial or non-linear models

### Pitfall 25: Chi-Square with Small Expected Frequencies
**Problem:** Chi-square test with expected cell counts < 5.

**Why wrong:** Violates test assumptions, p-values inaccurate.

**Solutions:**
- Fisher's exact test
- Combine categories
- Increase sample size

### Pitfall 26: Paired vs. Independent Tests
**Problem:** Using independent samples test for paired data (or vice versa).

**Why wrong:**
- Wastes power (paired data analyzed as independent)
- Violates independence assumption (independent data analyzed as paired)

**Solution:** Match test to design.

## Confidence Interval Misinterpretations

### Pitfall 27: 95% CI = 95% Probability True Value Inside
**Misconception:** "95% chance the true value is in this interval."

**Reality:** The true value either is or isn't in this specific interval. If we repeated the study many times, 95% of resulting intervals would contain the true value.

**Better interpretation:** "We're 95% confident this interval contains the true value."

### Pitfall 28: Overlapping CIs = No Difference
**Problem:** Assuming overlapping confidence intervals mean no significant difference.

**Reality:** Overlapping CIs are less stringent than difference tests. Two CIs can overlap while the difference between groups is significant.

**Guideline:** Overlap of point estimate with other CI is more relevant than overlap of intervals.

### Pitfall 29: Ignoring CI Width
**Problem:** Focusing only on whether CI includes zero, not precision.

**Why important:** Wide CIs indicate high uncertainty. "Significant" effects with huge CIs are less convincing.

**Consider:** Both significance and precision.

## Bayesian vs. Frequentist Confusions

### Pitfall 30: Mixing Bayesian and Frequentist Interpretations
**Problem:** Making Bayesian statements from frequentist analyses.

**Examples:**
- "Probability hypothesis is true" (Bayesian) from p-value (frequentist)
- "Evidence for null" from non-significant result (frequentist can't support null)

**Solution:**
- Be clear about framework
- Use Bayesian methods for Bayesian questions
- Use Bayes factors to compare hypotheses

### Pitfall 31: Ignoring Prior Probability
**Problem:** Treating all hypotheses as equally likely initially.

**Reality:** Extraordinary claims need extraordinary evidence. Prior plausibility matters.

**Consider:**
- Plausibility given existing knowledge
- Mechanism plausibility
- Base rates

## Data Transformation Issues

### Pitfall 32: Dichotomizing Continuous Variables
**Problem:** Splitting continuous variables at arbitrary cutoffs.

**Consequences:**
- Loss of information and power
- Arbitrary distinctions
- Discarding individual differences

**Exceptions:** Clinically meaningful cutoffs with strong justification.

**Better:** Keep continuous or use multiple categories.

### Pitfall 33: Trying Multiple Transformations
**Problem:** Testing many transformations until finding significance.

**Why problematic:** Inflates Type I error, is a form of p-hacking.

**Better approach:**
- Prespecify transformations
- Use theory-driven transformations
- Correct for multiple testing if exploring

## Missing Data Problems

### Pitfall 34: Listwise Deletion by Default
**Problem:** Automatically deleting all cases with any missing data.

**Consequences:**
- Reduced power
- Potential bias if data not missing completely at random (MCAR)

**Better approaches:**
- Multiple imputation
- Maximum likelihood methods
- Analyze missingness patterns

### Pitfall 35: Ignoring Missing Data Mechanisms
**Problem:** Not considering why data are missing.

**Types:**
- MCAR (Missing Completely at Random): Safe to delete
- MAR (Missing at Random): Can impute
- MNAR (Missing Not at Random): May bias results

**Solution:** Analyze patterns, use appropriate methods, consider sensitivity analyses.

## Publication and Reporting Issues

### Pitfall 36: Selective Reporting
**Problem:** Only reporting significant results or favorable analyses.

**Consequences:**
- Literature appears more consistent than reality
- Meta-analyses biased
- Wasted research effort

**Solutions:**
- Preregistration
- Report all analyses
- Use reporting guidelines (CONSORT, PRISMA, etc.)

### Pitfall 37: Rounding to p < .05
**Problem:** Reporting exact p-values selectively (e.g., p = .049 but p < .05 for .051).

**Why problematic:** Obscures values near threshold, enables p-hacking detection evasion.

**Better:** Always report exact p-values.

### Pitfall 38: No Data Sharing
**Problem:** Not making data available for verification or reanalysis.

**Consequences:**
- Can't verify results
- Can't include in meta-analyses
- Hinders scientific progress

**Best practice:** Share data unless privacy concerns prohibit.

## Cross-Validation and Generalization

### Pitfall 39: No Cross-Validation
**Problem:** Testing model on same data used to build it.

**Consequence:** Overly optimistic performance estimates.

**Solutions:**
- Split data (train/test)
- K-fold cross-validation
- Independent validation sample

### Pitfall 40: Data Leakage
**Problem:** Information from test set leaking into training.

**Examples:**
- Normalizing before splitting
- Feature selection on full dataset
- Including temporal information

**Consequence:** Inflated performance metrics.

**Prevention:** All preprocessing decisions made using only training data.

## Meta-Analysis Pitfalls

### Pitfall 41: Apples and Oranges
**Problem:** Combining studies with different designs, populations, or measures.

**Balance:** Need homogeneity but also comprehensiveness.

**Solutions:**
- Clear inclusion criteria
- Subgroup analyses
- Meta-regression for moderators

### Pitfall 42: Ignoring Publication Bias
**Problem:** Published studies overrepresent significant results.

**Consequences:** Overestimated effects in meta-analyses.

**Detection:**
- Funnel plots
- Trim-and-fill
- PET-PEESE
- P-curve analysis

**Solutions:**
- Include unpublished studies
- Register reviews
- Use bias-correction methods

## General Best Practices

1. **Preregister studies** - Distinguish confirmatory from exploratory
2. **Report transparently** - All analyses, not just significant ones
3. **Check assumptions** - Don't blindly apply tests
4. **Use appropriate tests** - Match test to data and design
5. **Report effect sizes** - Not just p-values
6. **Consider practical significance** - Not just statistical
7. **Replicate findings** - One study is rarely definitive
8. **Share data and code** - Enable verification
9. **Use confidence intervals** - Show uncertainty
10. **Think causally carefully** - Most research is correlational
