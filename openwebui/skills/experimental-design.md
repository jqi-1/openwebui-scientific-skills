---
name: experimental-design
description: Design experiments and studies BEFORE data is collected — choosing a design, randomizing, blocking, and laying out treatment combinations so results are interpretable. Use whenever someone is planning a study, asks how to assign subjects/samples to groups, mentions randomization, blocking, stratification, controls, factorial or fractional-factorial designs, design of experiments (DOE), screening many factors, response-surface optimization, crossover or repeated-measures or split-plot designs, cluster/group randomization, Latin squares, plate layouts, batch/run-order effects, replication vs. pseudoreplication, or sequential/adaptive/group-sequential designs. Trigger even for informal phrasings like "how should I set up this experiment", "how do I avoid confounding", "what's the best way to test these 6 factors", or "assign these mice to conditions". For computing the sample size or power once the design is chosen, use statistical-power; for analyzing data already collected, use statistical-analysis.
---

# Experimental Design

## Overview

The design of a study — how units are assigned to conditions, what is held constant, what is varied, and in what structure — determines what questions the data can answer. No analysis can rescue a confounded or pseudoreplicated design after the fact. This skill is about the decisions made *before* data collection: picking a design that isolates the effect of interest, randomizing to license causal claims, blocking to remove known nuisance variation, and structuring multi-factor experiments so effects are estimable rather than tangled together.

The three ideas behind almost every good design (Fisher's principles):
- **Randomization** — assign treatments at random so that confounders, known and unknown, are balanced in expectation. This is what turns a comparison into a causal claim.
- **Replication** — independent repetition at the right level, so you can estimate variability and your effects aren't artifacts of a single unit. The most common fatal error is **pseudoreplication**: counting repeated measurements on the same unit as independent replicates.
- **Blocking / local control** — group similar units (by batch, day, site, litter) and randomize within blocks, removing that nuisance variation from the error term instead of letting it inflate noise.

This skill helps you choose among design types, generate the actual randomization or DOE layout (with reproducible scripts), and avoid the structural mistakes that make data uninterpretable.

## When to Use This Skill

- Planning any comparative experiment or trial and deciding how to assign units
- Randomizing subjects/samples to arms (simple, blocked, stratified, or cluster)
- Removing nuisance variation by blocking or stratification
- Designing multi-factor experiments: full or fractional factorial, screening designs
- Optimizing a response over continuous factors (response-surface designs)
- Within-subject / repeated-measures, crossover, split-plot, or Latin-square designs
- Cluster- or group-randomized designs (sites, clinics, classrooms, litters)
- Deciding the number and level of replicates and avoiding pseudoreplication
- Sequential, group-sequential, or adaptive designs with interim analyses
- Laying out plates/batches and randomizing run order to defeat drift

## Installation

```bash
uv pip install "numpy>=1.26" "pandas>=2.0" pyDOE3
```

`pyDOE3` is the maintained successor to pyDOE/pyDOE2 and supplies factorial,
fractional-factorial, Plackett-Burman, central-composite, Box-Behnken, and
Latin-hypercube generators. The bundled scripts wrap it to return designs in real
factor units with named columns and randomized run order.

---

## Choosing a design

Start from the question and the structure of your units, not from a favorite design.

```
What are you trying to learn?
│
├─ Compare a few predefined conditions (A vs B vs C)?
│   ├─ Units independent, possibly with a known nuisance factor (day, batch, site)?
│   │     → Completely randomized (no nuisance) or RANDOMIZED BLOCK design.
│   ├─ Each unit can receive every condition in sequence (washout possible)?
│   │     → CROSSOVER / repeated-measures design (more power, watch carry-over).
│   └─ You can only randomize groups, not individuals (schools, clinics)?
│         → CLUSTER-randomized design (analyze at the cluster level; see pseudoreplication).
│
├─ Screen MANY factors (5+) to find the few that matter?
│     → FRACTIONAL FACTORIAL or PLACKETT-BURMAN screening design.
│
├─ Quantify main effects AND interactions among a handful of factors?
│     → FULL 2^k FACTORIAL design.
│
├─ Find the settings that OPTIMIZE a response (curvature matters)?
│     → RESPONSE-SURFACE design: central composite or Box-Behnken.
│
└─ Explore a simulation/computer model over a continuous space?
      → SPACE-FILLING design: Latin hypercube.
```

Detailed guidance per branch:
- **Randomization, blocking, stratification, controls** → `references/randomization_and_blocking.md`
- **Factorial, fractional-factorial, screening, response-surface, DOE concepts (aliasing, resolution)** → `references/factorial_and_doe.md`
- **Crossover, repeated-measures, split-plot, Latin-square, cluster, nested designs** → `references/design_types.md`
- **Sequential, group-sequential, and adaptive designs (interim analyses)** → `references/sequential_and_adaptive.md`

---

## Generating the design

Two scripts produce ready-to-use, reproducible layouts. Run them from the skill's
`scripts/` directory or add it to `sys.path`. Everything is seeded so the exact
schedule can be archived and regenerated — a requirement for trial registration
and good lab practice.

### Randomization / allocation schedules — `scripts/randomization.py`

```python
from randomization import (
    simple_randomization, block_randomization,
    stratified_block_randomization, cluster_randomization,
    assign_factorial_runs, arm_balance,
)

# Permuted blocks keep the arms balanced throughout enrollment (use for n < ~100
# or sequential intake — simple randomization can drift out of balance with small n)
sched = block_randomization(n=60, arms=["treatment", "control"], seed=42)

# Balance a prognostic variable across arms by randomizing within each stratum
sched = stratified_block_randomization({"siteA": 30, "siteB": 30},
                                       arms=["drug", "placebo"], ratio=(2, 1), seed=42)

# Randomize whole clusters, not individuals (the cluster is the unit)
sched = cluster_randomization(["clinic1", "clinic2", "clinic3", "clinic4"], seed=42)

arm_balance(sched)            # sanity-check the counts per arm
sched.to_csv("allocation_schedule.csv", index=False)
```

Choosing among them: **simple** is fine for large n but can produce imbalance with
small n; **block** guarantees balance throughout; **stratified block** additionally
balances a known prognostic factor; **cluster** is mandatory when the intervention
is delivered at a group level. See `references/randomization_and_blocking.md`.

### DOE matrices — `scripts/doe_designs.py`

```python
from doe_designs import (
    full_factorial, two_level_factorial, fractional_factorial,
    plackett_burman, central_composite, box_behnken, latin_hypercube,
)

# Factors as real-world (low, high) ranges -> design comes back in real units
factors = {"temp_C": (20, 60), "conc_mM": (1, 10), "pH": (6, 8)}

# Full 2^3: all main effects + all interactions (8 runs), run order randomized
design = two_level_factorial(factors, seed=42)

# Screen 7 factors cheaply (main effects only)
many = {f"factor_{i}": (0, 1) for i in range(7)}
design = plackett_burman(many, seed=42)

# Optimize over 2 factors with curvature (response-surface)
design = central_composite({"temp_C": (20, 60), "conc_mM": (1, 10)}, seed=42)

design.to_csv("experimental_runs.csv", index=False)
```

Run order is randomized by default so factors aren't confounded with time/drift
(machine warm-up, reagent aging). See `references/factorial_and_doe.md` for picking
generators, reading the alias structure, and choosing resolution.

---

## The mistakes that ruin studies

These are structural — they can't be fixed in analysis, only in design.

1. **Pseudoreplication.** Treating repeated measurements of one unit as independent
   replicates: 3 mice with 100 cells each is n = 3 (mice), not n = 300 (cells), for
   any treatment applied to the mouse. The replicate must be at the level the
   treatment is randomized. This single error invalidates a large share of published
   experiments. Randomize and replicate at the right level; analyze with the nesting
   respected (mixed model). See `references/design_types.md`.
2. **Confounding by a nuisance variable.** Running all treatment samples on Monday
   and all controls on Tuesday confounds treatment with day. Randomize across, or
   block on, every nuisance factor you can name (batch, day, plate, technician,
   instrument, position).
3. **No or broken randomization.** Convenience assignment (first-come → treatment)
   lets confounders sneak in. Use a seeded schedule and follow it.
4. **No proper control.** Without a concurrent control (and, where relevant, a
   vehicle/sham and blinding), you can't separate the treatment effect from time,
   placebo, or handling effects.
5. **Batch effects mistaken for biology.** In omics especially, process samples in a
   randomized/blocked order across batches; never let batch align with the condition.
6. **Edge/position effects on plates.** Evaporation and thermal gradients make plate
   edges differ. Randomize or block sample positions; don't put all controls in
   column 1.
7. **Aliasing ignored in fractional designs.** A low-resolution fractional factorial
   confounds main effects with interactions; know your alias structure before
   concluding a factor "has no effect."
8. **Optimizing without curvature.** A two-level factorial can't detect a curved
   response; you'll miss an interior optimum. Use a response-surface design.

---

## Workflow

1. **State the question, the unit, and the response.** What is randomized? What is
   measured? At what level is a true independent replicate? This determines everything.
2. **List nuisance factors** (batch, day, site, operator, position) — plan to block,
   stratify, or randomize across each.
3. **Pick the design** using the decision tree and reference files.
4. **Decide replication** at the correct level (and get n from the
   **statistical-power** skill for the chosen design).
5. **Generate the layout** with `randomization.py` / `doe_designs.py`, seeded.
6. **Randomize run/processing order** and plate/batch positions.
7. **Document** the design, seed, and schedule (pre-register if possible) so the
   analysis is confirmatory and the layout is auditable.
8. **Match the analysis to the design** — blocks, strata, clusters, and nesting must
   appear in the model (hand off to **statistical-analysis** / **statsmodels**).

---

## Resources

### Scripts
- `scripts/randomization.py` — seeded allocation schedules: `simple_randomization`,
  `block_randomization`, `stratified_block_randomization`, `cluster_randomization`,
  `assign_factorial_runs`, `arm_balance`.
- `scripts/doe_designs.py` — DOE matrices in real units: `full_factorial`,
  `two_level_factorial`, `fractional_factorial`, `plackett_burman`,
  `central_composite`, `box_behnken`, `latin_hypercube`.

### References
- `references/randomization_and_blocking.md` — randomization methods, blocking,
  stratification, controls, blinding, batch/plate layout.
- `references/factorial_and_doe.md` — factorial and fractional designs, resolution
  and aliasing, screening, and response-surface methodology.
- `references/design_types.md` — completely randomized, randomized block, crossover,
  repeated-measures, split-plot, Latin-square, cluster, and nested designs; the
  pseudoreplication problem in depth.
- `references/sequential_and_adaptive.md` — group-sequential designs, alpha spending,
  interim stopping, and adaptive sample-size re-estimation.

### Related skills
- **statistical-power** — required sample size / power for the design you've chosen.
- **statistical-analysis** — running and reporting the analysis after collection.
- **statsmodels** / **pymc** — fitting the models the design implies.

### Key references
- Fisher, R. A. (1935). *The Design of Experiments*.
- Montgomery, D. C. (2019). *Design and Analysis of Experiments* (10th ed.).
- Hurlbert, S. H. (1984). Pseudoreplication and the design of ecological field
  experiments. *Ecological Monographs*, 54(2), 187–211.
- Lazic, S. E. (2016). *Experimental Design for Laboratory Biologists*.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/experimental-design/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/design_types.md`

# Design Types and the Replication Structure

Choosing the right design structure is mostly about matching the *unit of
randomization* and the *unit of replication* to your question, and respecting any
nesting in the analysis. This file walks through the standard structures and then
treats the single most common fatal error — pseudoreplication — in depth.

## Table of contents
- [Completely randomized design](#completely-randomized-design)
- [Randomized complete block design](#randomized-complete-block-design)
- [Latin square](#latin-square)
- [Repeated-measures and crossover](#repeated-measures-and-crossover)
- [Split-plot designs](#split-plot-designs)
- [Cluster / group-randomized designs](#cluster--group-randomized-designs)
- [Nested designs and pseudoreplication](#nested-designs-and-pseudoreplication)

## Completely randomized design

Units are assigned to treatments purely at random, no blocking. Simplest design;
appropriate when units are homogeneous and there's no identifiable nuisance factor.
Analyze with one-way ANOVA / regression. If units are *not* homogeneous, the
nuisance variation inflates error — block instead.

## Randomized complete block design

Group units into **blocks** of similar units (day, batch, litter), and randomize all
treatments *within* each block. Every treatment appears once per block. The
between-block variation is removed from the error term, sharply increasing precision
when blocks differ. Analyze with `treatment + block` in the model. This is the
default upgrade over a completely randomized design whenever a nuisance factor exists.

## Latin square

Controls **two** nuisance factors simultaneously with a square layout: each treatment
appears exactly once in every row and every column. Classic uses: row = day, column =
position/order, cell = treatment. Requires #treatments = #rows = #columns, and assumes
no interactions between the blocking factors and treatment. Efficient when both
nuisance dimensions matter and runs are limited. (Graeco-Latin squares extend this to
three nuisance factors.)

## Repeated-measures and crossover

Each subject receives more than one condition, serving as its own control. This
removes between-subject variation — usually the largest noise source — so these
designs are far more powerful per subject.

- **Repeated measures:** the same units measured under several conditions or over
  time.
- **Crossover:** each subject receives each treatment in sequence, with **washout**
  periods between to clear carry-over. Subjects are randomized to treatment *orders*
  (e.g. an AB/BA crossover; or a Williams square for ≥3 treatments to balance order).

Watch for:
- **Carry-over / residual effects** — an effect of the previous treatment persisting
  into the next period. Adequate washout is essential; otherwise the design is biased.
- **Period effects** — systematic change over time (learning, fatigue, disease
  progression). Balanced orders let you separate period from treatment.
- **Correlation within subject** — the repeated observations are not independent; the
  analysis must model it (mixed model / repeated-measures ANOVA). Sample-size/power
  for these depends on the within-subject correlation — use simulation in the
  **statistical-power** skill.

## Split-plot designs

Arises when some factors are **hard to change** (applied to large units) and others
are **easy to change** (applied to sub-units). The hard-to-change factor is randomized
to whole plots; the easy factor is randomized to subplots within each whole plot.
Example: oven temperature (whole plot — you can't re-set it per sample) × coating type
(subplot — applied per sample). Crucially there are **two different error terms** — one
for whole-plot factors, one for subplot factors — and the analysis must use both.
Treating a split-plot as a completely randomized factorial gives wrong (usually
anticonservative) tests for the whole-plot factor. Industrial DOE and agricultural
trials are full of accidental split-plots; recognize when a factor can't be reset per
run.

## Cluster / group-randomized designs

When the intervention is delivered to a *group* (a clinic's protocol, a classroom
curriculum, a village water supply), you can only randomize at the group level. The
**cluster is the unit of randomization**, and because members of a cluster are
correlated, it is effectively the unit of replication too.

- Power depends on the number of **clusters** far more than the number of individuals,
  and on the **intraclass correlation (ICC)**. Adding people to existing clusters
  helps much less than adding clusters.
- The **design effect** `DEFF = 1 + (m − 1)·ICC` (m = cluster size) quantifies how
  much the effective sample size shrinks; even a small ICC with large clusters costs
  dearly. Power these by simulation (see **statistical-power**).
- Analyze with a method that accounts for clustering (mixed model with a cluster
  random effect, or GEE). Analyzing individuals as independent is pseudoreplication.

## Nested designs and pseudoreplication

**Pseudoreplication** is treating non-independent measurements as independent
replicates. It is the most common and most damaging design error in experimental
biology, and it cannot be fixed after data collection — only by designing and
analyzing at the correct level.

The principle: **the replicate is whatever the treatment is independently applied
and randomized to.** Measurements taken below that level are *technical replicates* —
they improve the precision of a single unit's value but do **not** add degrees of
freedom for testing the treatment.

Worked examples:
- **One dish per treatment, 50 cells imaged.** Treatment applied to the dish ⇒ n = 1
  per treatment. The 50 cells describe that one dish; they are not 50 independent
  tests of the treatment. You need multiple independently treated dishes.
- **3 mice per group, 100 cells each.** n = 3 (mice) for a treatment given to the
  mouse, not 300 (cells). Average within mouse, or use a mixed model with mouse as a
  random effect.
- **One tank of fish given a diet, every fish measured.** The tank is the unit (the
  diet was randomized to the tank) ⇒ n = number of tanks, not number of fish. Shared
  tank water, temperature, and social effects make fish within a tank correlated.
- **Repeated measurements over time on the same subject** are nested within subject;
  the subject is the replicate.

How to avoid it:
1. **Identify the experimental unit** = the smallest physical entity to which a
   treatment level is independently and randomly assigned.
2. **Replicate at that level** — more independently treated units, not more
   measurements per unit (though technical replicates can reduce measurement noise).
3. **Analyze with the nesting respected** — average to the unit level, or fit a mixed
   model with random effects for the nesting (cells in mice, fish in tanks, time in
   subjects). The fixed-effect treatment test then uses the correct, larger error and
   correct degrees of freedom.

Technical replicates are still worth taking — they sharpen each unit's estimate — but
report and analyze them as what they are, never as independent biological replicates.
For sample size of nested/clustered designs, use simulation in **statistical-power**.

### `references/factorial_and_doe.md`

# Factorial and Design-of-Experiments (DOE)

When several factors might affect a response, testing them **one factor at a time
(OFAT)** is both wasteful and blind to interactions. Factorial designs vary factors
*together*, so you estimate every main effect and interaction from the same runs,
with better precision per run. This file covers the family of DOE designs and the
concepts (resolution, aliasing) needed to read them. Generate them with
`scripts/doe_designs.py`.

## Table of contents
- [Why factorial beats OFAT](#why-factorial-beats-ofat)
- [Full factorial (2^k)](#full-factorial)
- [Fractional factorial (2^(k-p))](#fractional-factorial)
- [Resolution and aliasing](#resolution-and-aliasing)
- [Screening designs (Plackett-Burman)](#screening-designs)
- [Response-surface designs](#response-surface-designs)
- [Space-filling designs](#space-filling-designs)
- [Choosing a design](#choosing-a-design)

## Why factorial beats OFAT

Vary one factor while holding others fixed and you (1) spend runs inefficiently and
(2) can never see **interactions** — cases where the effect of A depends on the level
of B, which are the rule, not the exception, in real systems. A factorial varies all
factors simultaneously across runs; each effect is estimated using *all* the data, so
a 2^k factorial is more precise than k separate OFAT studies of the same size.

## Full factorial

A **2^k** design runs every combination of k factors at two levels (low/high, coded
−1/+1). It estimates all k main effects and all 2^k − k − 1 interactions.

- Runs = 2^k: 8 for 3 factors, 16 for 4, 32 for 5. Practical to ~5 factors.
- Use when you have a handful of factors and want a full picture including
  interactions.
- `two_level_factorial({"temp": (20,60), "conc": (1,10), "pH": (6,8)})` → 8 runs.
- For factors with more than two levels, use `full_factorial` with explicit level
  lists (runs = product of level counts — grows fast).

Add **center points** (all factors at their midpoint) to a two-level design to get a
cheap check for curvature: if the center response departs from the factorial average,
a linear model is inadequate and you need a response-surface design.

## Fractional factorial

When k is large, 2^k is too many runs — but most high-order interactions are
negligible (the *sparsity-of-effects* principle). A **2^(k−p)** fractional factorial
runs a carefully chosen fraction (1/2, 1/4, ...) of the full design, trading the
ability to estimate some interactions for far fewer runs.

- `fractional_factorial(factors, generator="a b c abc")` builds a half-fraction of 4
  factors in 8 runs. The generator string (Yates notation) assigns each factor to a
  column; a multi-letter token aliases that factor with an interaction.
- The price is **aliasing**: some effects become indistinguishable. You must know
  which.

## Resolution and aliasing

**Aliasing** (confounding) means two effects are estimated by the same contrast — the
data cannot separate them. Which effects are aliased is summarized by the design's
**resolution**:

| Resolution | Aliasing | Interpretation |
|------------|----------|----------------|
| **III** | main effects aliased with 2-factor interactions | Screening only; a "significant" main effect might be an interaction |
| **IV** | main effects clear of 2FI, but 2FIs aliased with each other | Good for screening; main effects trustworthy |
| **V** | main effects and 2FIs all clear of each other (aliased with 3FI+) | Can model main effects and 2-factor interactions confidently |

Always state the resolution and inspect the alias structure before interpreting a
fractional design. Concluding "factor C has no effect" is unsafe if C is aliased with
a real interaction (it could cancel out). When in doubt, choose a higher-resolution
generator (more runs) or add runs to **de-alias** (fold-over / augment the design).

## Screening designs

When the goal is to **find the vital few** factors out of many (5, 10, 20+), use a
screening design that estimates main effects only, as cheaply as possible:
- **Plackett-Burman** (`plackett_burman`): runs = the next multiple of 4 above k
  (e.g. 12 runs for up to 11 factors). Resolution III — two-factor interactions are
  heavily confounded with main effects. Perfect for triage: run it, keep the few
  factors with large effects, then study those with a full or higher-resolution
  factorial.
- Resolution III fractional factorials serve the same purpose.

Screen first, optimize later — don't try to learn interactions and find the optimum
in one cheap design.

## Response-surface designs

Two-level designs fit only a flat (linear + interaction) model; they cannot locate an
interior optimum or describe **curvature**. To fit a quadratic and optimize, use a
response-surface methodology (RSM) design over continuous factors:

- **Central composite design (CCD)** (`central_composite`): a 2^k factorial + center
  points + axial ("star") points. The axial points add the levels needed to estimate
  quadratic terms. With `face="circumscribed"` (default) the axial points sit
  *outside* the factorial box (so actual factor levels exceed your stated low/high);
  use `face="inscribed"` or `"faced"` to keep everything within the original range.
- **Box-Behnken** (`box_behnken`, needs ≥3 factors): a quadratic design that avoids
  the extreme all-low/all-high corners — useful when those corners are unsafe,
  expensive, or infeasible. More economical than a CCD for 3–5 factors.

Workflow: screen → factorial (find important factors & rough region) → response
surface (model curvature, locate optimum), often moving the experimental region
between steps (path of steepest ascent).

## Space-filling designs

For **computer experiments / simulations** (deterministic or expensive models) where
classical replication and blocking don't apply, you want even coverage of a
high-dimensional input space:
- **Latin hypercube** (`latin_hypercube`): each factor's range is divided into
  n_samples equal bins, sampled once each, arranged to spread points apart
  (`criterion="maximin"`). Gives good coverage with relatively few points and is the
  standard input design for surrogate/emulator modeling and sensitivity analysis.

## Choosing a design

| Goal | Factors | Design | Script function |
|------|---------|--------|-----------------|
| Screen many factors | 5–20+ | Plackett-Burman / Res III | `plackett_burman` |
| Main effects, some interactions, few runs | 4–8 | Res IV/V fractional | `fractional_factorial` |
| All effects + interactions | 2–5 | Full 2^k factorial | `two_level_factorial` |
| Multi-level categorical | few | Full factorial | `full_factorial` |
| Optimize a response (curvature) | 2–5 | Central composite / Box-Behnken | `central_composite`, `box_behnken` |
| Cover a simulation input space | any | Latin hypercube | `latin_hypercube` |

In all cases, **randomize run order** (the scripts do by default) so factors aren't
confounded with time-related drift, and add center points to two-level designs as a
curvature check.

### `references/randomization_and_blocking.md`

# Randomization, Blocking, Stratification, and Controls

These are the tools of *local control*: removing or balancing nuisance variation so
the comparison you care about is clean. Randomization handles the unknown
confounders; blocking and stratification handle the known ones; controls and
blinding handle the systematic biases.

## Randomization — why and how

Randomization assigns treatments to units by chance, so that in expectation every
confounder (measured or not, known or unknown) is balanced across arms. This is the
foundation of causal inference: without it, an observed difference could always be
due to some variable that happened to track the grouping.

Use a **seeded, reproducible** schedule (see `scripts/randomization.py`) and follow
it exactly. Record the seed. "I randomized somehow" is neither auditable nor
reproducible.

### Methods (and when each is right)

| Method | What it does | Use when |
|--------|--------------|----------|
| **Simple** | Independent random assignment per unit | n is large (≳100); simplicity matters; imbalance is tolerable |
| **Permuted block** | Within each block, arms appear in fixed ratio; order shuffled | You need balance throughout enrollment, or n is small/moderate, or intake is sequential |
| **Stratified block** | Separate blocks within each level of a prognostic factor | A known covariate (site, sex, stage) must be balanced across arms |
| **Cluster** | Whole groups (clinics, classes) assigned to arms | The intervention is delivered at a group level |
| **Minimization** | Adaptively assign to minimize imbalance across several covariates | Many prognostic factors and small n (specialized; not in the script) |

**Simple randomization caveat:** with small n it behaves like flipping a few coins —
you can easily get 12 vs. 8 instead of 10 vs. 10, and worse for subgroups. Blocking
fixes this.

**Block size:** must be a multiple of the ratio unit (e.g. for 1:1, sizes 2, 4, 6).
Smaller blocks balance more tightly but are more predictable in unblinded trials
(a clinician who knows the block size can guess the last allocation). Vary block
size or keep it concealed when predictability is a concern.

## Blocking — removing known nuisance variation

A **block** is a group of units expected to be similar (same day, batch, litter,
plate, instrument run). You randomize treatments *within* each block. The nuisance
variation between blocks is then removed from the error term, so the treatment
comparison is more precise — often dramatically so.

Block on anything that (a) you can identify before the experiment and (b) you
expect to affect the response but isn't of interest itself:
- **Time:** day, week, session, processing batch.
- **Space:** plate, plate position/edge, shelf, cage rack, field plot.
- **Material:** reagent lot, animal litter, cell passage, donor.
- **People/instruments:** technician, machine, sequencing run.

Rule of thumb: *"Block what you can, randomize what you cannot."* If you suspect a
factor matters but can't block it, at least randomize across it and record it as a
covariate.

**Randomized complete block design (RCBD):** every treatment appears once in every
block. This is the workhorse design — analyze with treatment + block in the model.

## Stratification vs. blocking vs. covariate adjustment

These overlap; the distinction is about *when* you control the variable:
- **Stratify / block at design time** when the factor is known before assignment and
  you want guaranteed balance (the safest, since it doesn't rely on a model).
- **Adjust as a covariate at analysis time** (ANCOVA, regression) when the factor is
  continuous or measured after assignment. Often you do both: stratify on the big
  ones, adjust for the rest.

A few strata are better than many: stratifying on too many factors at once leaves
strata with too few units to block effectively. For many covariates and small n,
minimization is the alternative.

## Controls

A comparison needs a concurrent baseline. Match the control to the threat you're
ruling out:
- **Untreated / standard-of-care control** — isolates the treatment effect from time.
- **Vehicle / sham control** — isolates the active ingredient from the delivery
  (injection stress, vehicle solvent, sham surgery).
- **Positive control** — a treatment known to produce the effect, to confirm the
  assay can detect one at all.
- **Concurrent, not historical** — controls run at the same time as the treatment;
  historical controls reintroduce time confounding.

## Blinding

Blinding prevents expectation from biasing measurement and behavior:
- **Single-blind:** the subject doesn't know the assignment.
- **Double-blind:** neither subject nor experimenter/assessor knows.
- **Blinded outcome assessment:** at minimum, whoever measures the outcome shouldn't
  know the group — cheap and high-value even in animal/bench work.
Allocation concealment (the person enrolling can't foresee the next assignment) is
distinct from blinding and just as important; a sealed seeded schedule provides it.

## Batch effects and plate layout (especially omics / HTS)

Batch effects are systematic technical differences between processing groups and are
a leading cause of irreproducible high-throughput results.
- **Never let batch align with the biological condition.** If all cases are in batch
  1 and all controls in batch 2, condition and batch are perfectly confounded and
  no normalization can separate them.
- **Randomize or block sample-to-batch and position-within-plate.** Spread each
  condition across all batches and across plate positions.
- **Avoid edge effects:** evaporation and thermal gradients make outer wells differ;
  don't load all controls into edge columns. Randomize positions, or include
  replicates spanning edge and interior.
- **Include anchor/reference samples** in every batch to estimate and correct batch
  shifts.
- Use `assign_factorial_runs()` / the randomization functions to generate a
  randomized processing order and position map.

## Documentation

Record, and ideally pre-register: the randomization method, the seed, block sizes,
stratification factors, the schedule itself, and the planned analysis (which must
include block/stratum/cluster terms). This is what makes the study auditable and the
primary analysis confirmatory rather than exploratory.

### `references/sequential_and_adaptive.md`

# Sequential and Adaptive Designs

A fixed design commits to a single sample size and one analysis at the end.
**Sequential** and **adaptive** designs allow looks at the data *during* the study and
let you stop early (for benefit, harm, or futility) or modify the design — saving
participants, time, and money. The catch: every interim look at the data is another
chance to cross the significance threshold by luck, so the error rate must be
controlled explicitly. Peeking at accumulating data and stopping the first time
p < 0.05 inflates the Type I error rate badly (to ~0.20+ with a few looks) — this is
the core problem these methods solve.

## Why naive peeking fails

If you test at α = 0.05 at each of K interim analyses and stop at the first
significant result, the *overall* false-positive rate is far above 0.05 — roughly
0.08 for 2 looks, ~0.14 for 5, ~0.20 for 10. The fix is to spend your total α across
the looks so the *cumulative* Type I error stays at 0.05.

## Group-sequential designs

Pre-plan a fixed number of interim analyses (e.g. after 25%, 50%, 75%, 100% of data)
and use **adjusted, more stringent boundaries** at each look so the overall α is
preserved. Common boundary families:

- **Pocock:** constant (equally stringent) nominal significance level at every look.
  Easier to stop early, but pays a larger penalty at the final analysis.
- **O'Brien–Fleming:** very stringent early (hard to stop in the first looks), relaxing
  toward the planned final α. Most popular in confirmatory trials because the final
  boundary is close to the unadjusted 0.05 and early stopping is reserved for dramatic
  effects.
- **Alpha-spending functions (Lan–DeMets):** generalize the above by defining how much
  α is "spent" as a function of information accrued, so the number and timing of looks
  need not be fixed in advance — only the spending function is.

You can stop for:
- **Efficacy** — the effect crosses the upper boundary.
- **Futility** — the effect is so small that continuing is unlikely to ever reach
  significance (a non-binding or binding lower boundary / conditional power threshold).
- **Harm** — safety boundary crossed.

Group-sequential designs require a modestly larger maximum sample size than a fixed
design (to pay for the looks), but the *expected* sample size is usually smaller
because many trials stop early.

### Tooling

Python support is thinner than for fixed designs; common options:
- **statsmodels** has limited sequential utilities; for full boundary computation,
  most practitioners call R packages via `rpy2` or a subprocess:
  - R `gsDesign` — the standard for group-sequential boundaries and spending functions.
  - R `rpact` — confirmatory adaptive and group-sequential designs.
- For custom rules, **simulate** the whole sequential procedure (generate data, apply
  the boundaries look by look, repeat) to confirm the realized Type I error and to
  estimate expected sample size and power. This mirrors the simulation approach in the
  **statistical-power** skill and is the most flexible route.

## Adaptive designs

Broader than group-sequential: the design itself can change at an interim based on
accumulating data, within a pre-specified plan that still controls error. Main types:

- **Sample-size re-estimation:** recompute the required n at an interim using the
  observed nuisance parameter (e.g. the variance or control-arm rate), without
  unblinding the treatment effect. Protects against a misjudged variance at planning.
- **Adaptive randomization:** shift allocation probabilities toward the better-
  performing arm as data accrue (response-adaptive), or to improve covariate balance.
- **Drop-the-loser / arm selection:** start with several arms or doses and drop
  inferior ones at interims (seamless phase II/III).
- **Adaptive enrichment:** narrow enrollment to a subgroup that appears to benefit.

Adaptive designs are powerful but easy to get wrong: any adaptation that uses the
unblinded treatment effect can inflate Type I error and bias the final effect estimate
unless the method explicitly corrects for it. Two non-negotiables:
1. **Pre-specify** the adaptation rule and the error-control method before the study.
2. **Validate by simulation** that the *entire* procedure preserves the Type I error
   rate and yields acceptable power and unbiased-enough estimates.

## When to use them

- **Confirmatory trials, expensive or risky enrollment** — group-sequential with
  O'Brien–Fleming boundaries to allow ethical early stopping.
- **Uncertain nuisance parameters at planning** — blinded sample-size re-estimation.
- **Many candidate doses/arms** — adaptive arm selection / seamless designs.
- **Pure exploration / fixed cheap data** — usually not worth the overhead; a fixed
  design is simpler and the analysis is unambiguous.

## Practical checklist

- Decide the **number and timing** of interim analyses (or the spending function).
- Choose a **boundary family** matched to how eager you are to stop early.
- Specify **futility** rules if you want to stop for lack of effect.
- Inflate the **maximum** sample size to cover the looks; report the **expected**
  sample size too.
- Pre-register the full sequential/adaptive plan, including the stopping rules.
- Have an independent **data monitoring committee** look at unblinded interims in
  human trials, not the study team.
- **Simulate** the design end to end to confirm error control before running it.

### `scripts/doe_designs.py`

```python
"""Design-of-experiments (DOE) matrices as labeled, decoded pandas DataFrames.

pyDOE3 returns designs in *coded* units (-1/+1, or 0..k-1). Researchers want the
design in *real* factor units (temperature in C, concentration in mM) with named
columns, randomized run order, and a clear sense of what each design is for. This
module wraps pyDOE3 to do exactly that.

A `factors` spec maps factor names to their real-world levels:
  - two-level / continuous:  {"temp": (20, 60), "conc": (1, 10)}   # (low, high)
  - multi-level categorical:  {"catalyst": ["A", "B", "C"]}

Functions:
  full_factorial          every combination of given levels (cost grows fast)
  two_level_factorial     2^k full factorial (screening + interactions)
  fractional_factorial    2^(k-p) fraction (screening many factors cheaply)
  plackett_burman         very economical main-effects-only screening
  central_composite       response-surface design (curvature / optimization)
  box_behnken             response-surface design, no extreme corners
  latin_hypercube         space-filling sample for simulation / computer experiments

Each returns a DataFrame in real units; pass randomize=True (default) to also get
a randomized 'run_order'. Requires: pyDOE3, numpy, pandas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _decode_two_level(coded, factors):
    """Map a -1/+1 coded matrix to real (low/high) units per factor."""
    names = list(factors)
    out = {}
    for j, name in enumerate(names):
        lvl = factors[name]
        low, high = lvl[0], lvl[1]
        mid, half = (high + low) / 2.0, (high - low) / 2.0
        out[name] = mid + coded[:, j] * half
    return pd.DataFrame(out)


def _randomize(df, randomize, seed):
    if not randomize:
        return df.reset_index(drop=True)
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(df)) + 1
    df = df.copy()
    df.insert(0, "run_order", order)
    return df.sort_values("run_order").reset_index(drop=True)


def full_factorial(factors, randomize=True, seed=0):
    """Every combination of the listed levels.

    factors values are explicit level lists, e.g.
      {"temp": [20, 40, 60], "catalyst": ["A", "B"]}  -> 3*2 = 6 runs.
    Runs = product of level counts, so this explodes quickly with many factors.
    """
    from pyDOE3 import fullfact
    names = list(factors)
    levels = [list(factors[n]) for n in names]
    counts = [len(l) for l in levels]
    coded = fullfact(counts).astype(int)
    data = {n: [levels[j][coded[i, j]] for i in range(len(coded))]
            for j, n in enumerate(names)}
    return _randomize(pd.DataFrame(data), randomize, seed)


def two_level_factorial(factors, randomize=True, seed=0):
    """Full 2^k factorial: all main effects and all interactions, estimable.

    Each factor needs a (low, high) pair. Use for k up to ~5; beyond that the
    run count (2^k) gets expensive — switch to fractional_factorial or
    plackett_burman for screening.
    """
    from pyDOE3 import ff2n
    coded = ff2n(len(factors))
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def fractional_factorial(factors, generator, randomize=True, seed=0):
    """2^(k-p) fractional factorial from a generator string.

    `generator` is pyDOE3's Yates notation, e.g. for 4 factors in 8 runs (one of
    them aliased): "a b c abc". Each token defines a column; multi-letter tokens
    alias a factor with an interaction (this is the tradeoff — fewer runs, some
    effects confounded). Choose a higher-resolution generator if you need to
    separate main effects from two-factor interactions.
    """
    from pyDOE3 import fracfact
    coded = fracfact(generator)
    if coded.shape[1] != len(factors):
        raise ValueError(f"generator defines {coded.shape[1]} factors but "
                         f"{len(factors)} were named")
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def plackett_burman(factors, randomize=True, seed=0):
    """Plackett-Burman screening design: main effects only, very few runs.

    Ideal for screening many factors (run count is the next multiple of 4 above k)
    to find the vital few. Two-factor interactions are heavily confounded with main
    effects, so use it to screen, not to model interactions.
    """
    from pyDOE3 import pbdesign
    coded = pbdesign(len(factors))  # may include extra dummy columns
    coded = coded[:, :len(factors)]
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def central_composite(factors, center=(0, 1), alpha="orthogonal",
                      face="circumscribed", randomize=True, seed=0):
    """Central composite design (CCD) for response-surface / optimization work.

    Adds axial ("star") points and center points to a 2^k factorial so you can fit
    a quadratic model and locate an optimum. With face='circumscribed' the axial
    points sit OUTSIDE the (low, high) box (so real levels exceed your stated
    range); use face='inscribed' or 'faced' to keep everything within range.
    `center` = (n center pts in factorial block, n in axial block).
    """
    from pyDOE3 import ccdesign
    coded = ccdesign(len(factors), center=center, alpha=alpha, face=face)
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def box_behnken(factors, center=1, randomize=True, seed=0):
    """Box-Behnken response-surface design (needs >= 3 factors).

    Like a CCD it fits a quadratic, but it never uses the extreme corner
    combinations (all-low or all-high), which is useful when those corners are
    unsafe or infeasible. More economical than a CCD for 3-5 factors.
    """
    from pyDOE3 import bbdesign
    if len(factors) < 3:
        raise ValueError("box_behnken requires at least 3 factors")
    coded = bbdesign(len(factors), center=center)
    return _randomize(_decode_two_level(coded, factors), randomize, seed)


def latin_hypercube(factors, n_samples, criterion="maximin", seed=0,
                    randomize=False):
    """Space-filling Latin hypercube sample over continuous factor ranges.

    For computer experiments / simulations where you want even coverage of a
    high-dimensional space with relatively few points. Each factor needs a
    (low, high) range. `criterion`: 'maximin' spreads points apart;
    'center'/'centermaximin'/'correlation' are alternatives.
    """
    from pyDOE3 import lhs
    # pyDOE3 draws from its own default_rng, so seeding numpy's global RNG has
    # no effect -- the seed has to be handed to lhs itself.
    names = list(factors)
    unit = lhs(  # in [0,1]
        len(names), samples=n_samples, criterion=criterion, seed=int(seed)
    )
    out = {}
    for j, n in enumerate(names):
        low, high = factors[n][0], factors[n][1]
        out[n] = low + unit[:, j] * (high - low)
    df = pd.DataFrame(out)
    return _randomize(df, randomize, seed)


if __name__ == "__main__":
    f2 = {"temp": (20, 60), "conc": (1, 10), "ph": (6, 8)}

    print("== 2^3 full factorial ==")
    print(two_level_factorial(f2, seed=1).to_string(index=False))

    print("\n== fractional 2^(4-1), generator 'a b c abc' ==")
    f4 = {"A": (-1, 1), "B": (-1, 1), "C": (-1, 1), "D": (-1, 1)}
    print(fractional_factorial(f4, "a b c abc", seed=1).to_string(index=False))

    print("\n== Plackett-Burman screening, 5 factors ==")
    f5 = {f"x{i}": (0, 1) for i in range(1, 6)}
    print(f"runs = {len(plackett_burman(f5, randomize=False))}")

    print("\n== central composite (2 factors) ==")
    print(central_composite({"temp": (20, 60), "conc": (1, 10)}, seed=1).round(2).to_string(index=False))

    print("\n== Latin hypercube, 8 samples over 3 factors ==")
    print(latin_hypercube(f2, 8, seed=1).round(2).to_string(index=False))
```

### `scripts/randomization.py`

```python
"""Reproducible randomization / allocation schedules for experiments and trials.

Randomization is what licenses causal inference: it breaks the link between
treatment assignment and any confounder, measured or not. But "I shuffled it"
is not enough — the *method* matters (simple vs. blocked vs. stratified) and the
schedule must be reproducible (seeded) and auditable. This module produces
allocation tables as pandas DataFrames, with a fixed seed so the exact schedule
can be regenerated and archived.

Functions:
  simple_randomization        independent coin-flip per unit (can yield imbalance)
  block_randomization         permuted blocks -> balance throughout enrollment
  stratified_block_randomization   blocks within strata -> balance per subgroup
  cluster_randomization       randomize whole clusters (sites/classes), not units
  assign_factorial_runs       randomize the RUN ORDER of a list of design rows

Requires: numpy, pandas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _normalize_ratio(arms, ratio):
    """Turn arms + integer ratio into a block template list, e.g.
    arms=['A','B'], ratio=(2,1) -> ['A','A','B']."""
    if ratio is None:
        ratio = [1] * len(arms)
    if len(ratio) != len(arms):
        raise ValueError("ratio must have one entry per arm")
    if any(r <= 0 for r in ratio):
        raise ValueError("ratio entries must be positive integers")
    template = []
    for arm, r in zip(arms, ratio):
        template += [arm] * int(r)
    return template


def simple_randomization(n, arms=("treatment", "control"), ratio=None, seed=0):
    """Independent random assignment per unit.

    Simplest method; with small n it can produce noticeable arm-size imbalance
    (like flipping few coins). Fine for large n. Use block_randomization when you
    need balance, especially for n < ~100 or sequential enrollment.
    """
    rng = np.random.default_rng(seed)
    arms = list(arms)
    template = _normalize_ratio(arms, ratio)
    probs = np.array([template.count(a) for a in arms], dtype=float)
    probs /= probs.sum()
    assign = rng.choice(arms, size=n, p=probs)
    return pd.DataFrame({"unit_id": np.arange(1, n + 1), "arm": assign})


def block_randomization(n, arms=("treatment", "control"), block_size=None,
                        ratio=None, seed=0):
    """Permuted-block randomization: balance is maintained throughout enrollment.

    Within each block every arm appears in the specified ratio; the order inside
    a block is shuffled. block_size must be a multiple of sum(ratio). Leaving it
    None picks a small valid size. Mild caveat: fixed small blocks are slightly
    predictable in unblinded trials — vary block size if that matters.
    """
    rng = np.random.default_rng(seed)
    arms = list(arms)
    template = _normalize_ratio(arms, ratio)
    unit = len(template)
    if block_size is None:
        block_size = unit * 2  # two of each ratio-unit per block
    if block_size % unit != 0:
        raise ValueError(f"block_size ({block_size}) must be a multiple of "
                         f"sum(ratio)={unit}")
    reps = block_size // unit

    out = []
    block_id = 0
    while len(out) < n:
        block = template * reps
        rng.shuffle(block)
        for a in block:
            out.append((len(out) + 1, block_id, a))
        block_id += 1
    df = pd.DataFrame(out[:n], columns=["unit_id", "block", "arm"])
    return df


def stratified_block_randomization(strata, arms=("treatment", "control"),
                                   block_size=None, ratio=None, seed=0):
    """Block-randomize independently within each stratum.

    Use when a prognostic variable (site, sex, disease stage) must be balanced
    across arms. `strata` is a dict {stratum_label: n_in_that_stratum} or a
    sequence of stratum labels (one per unit). Each stratum gets its own permuted
    blocks, guaranteeing balance within every subgroup.
    """
    if isinstance(strata, dict):
        items = list(strata.items())
    else:  # sequence of labels
        s = pd.Series(list(strata))
        items = list(s.value_counts().sort_index().items())

    frames = []
    for i, (label, count) in enumerate(items):
        df = block_randomization(count, arms=arms, block_size=block_size,
                                 ratio=ratio, seed=seed + 1 + i)
        df.insert(1, "stratum", label)
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out["unit_id"] = np.arange(1, len(out) + 1)
    return out


def cluster_randomization(clusters, arms=("treatment", "control"), ratio=None,
                          block_size=None, seed=0):
    """Randomize whole clusters (clinics, schools, litters) to arms.

    The cluster — not the individual — is the unit of randomization AND the unit
    of analysis-level independence. `clusters` is a list of cluster IDs (or an int
    count). Returns one row per cluster. Analyze with a method that accounts for
    clustering (mixed model / GEE); treating members as independent is
    pseudoreplication. Uses blocking across clusters for arm balance.
    """
    if isinstance(clusters, int):
        clusters = [f"cluster_{i+1}" for i in range(clusters)]
    clusters = list(clusters)
    df = block_randomization(len(clusters), arms=arms, ratio=ratio,
                             block_size=block_size, seed=seed)
    df = df.drop(columns=["unit_id"])
    df.insert(0, "cluster_id", clusters)
    return df


def assign_factorial_runs(design_df, seed=0):
    """Randomize the execution order of a set of design runs (e.g. a DOE matrix).

    Run order matters: executing a factorial design in a systematic order
    confounds the factors with time/drift (the machine warms up, the reagent
    degrades). Randomizing run order protects against that. Returns the design
    with a 'run_order' column and rows sorted by it.
    """
    rng = np.random.default_rng(seed)
    df = design_df.copy().reset_index(drop=True)
    order = rng.permutation(len(df)) + 1
    df["run_order"] = order
    return df.sort_values("run_order").reset_index(drop=True)


def arm_balance(df, arm_col="arm", by=None):
    """Quick check: counts per arm (optionally within each stratum/block)."""
    if by:
        return df.groupby([by, arm_col]).size().unstack(fill_value=0)
    return df[arm_col].value_counts()


if __name__ == "__main__":
    print("== simple (n=10) ==")
    print(arm_balance(simple_randomization(10, seed=1)).to_dict())

    print("\n== permuted blocks, 2:1 treatment:control, n=12 ==")
    d = block_randomization(12, arms=["treatment", "control"], ratio=(2, 1), seed=1)
    print(d.to_string(index=False))
    print("balance:", arm_balance(d).to_dict())

    print("\n== stratified by site (A=8, B=6) ==")
    d = stratified_block_randomization({"siteA": 8, "siteB": 6}, seed=1)
    print(arm_balance(d, by="stratum").to_string())

    print("\n== cluster randomization (6 clinics) ==")
    print(cluster_randomization(6, seed=1).to_string(index=False))
```
