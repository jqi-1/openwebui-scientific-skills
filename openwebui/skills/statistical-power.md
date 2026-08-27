---
name: statistical-power
description: Sample-size and statistical power calculations for planning studies. Use whenever someone asks "how many subjects/samples/replicates do I need", wants an a priori power analysis, a minimum detectable effect (MDE), a power curve, or needs to justify a sample size for a grant, IRB protocol, or pre-registration. Covers closed-form power for t-tests, ANOVA, proportions, correlations, chi-square, and regression, plus simulation-based (Monte Carlo) power for designs with no formula — logistic/Poisson regression, mixed models, cluster-randomized trials, survival, and interactions. Use this skill even when the request only mentions an effect size, alpha, or "80% power" without saying "power analysis" explicitly. For laying out the study (randomization, blocking, factorial/DOE, crossover, sequential designs) use experimental-design; for analyzing data already collected and reporting it use statistical-analysis.
---

# Statistical Power & Sample Size

## Overview

Power analysis answers one of the most consequential questions in study planning: **how large a sample do you need to reliably detect an effect of a given size, and what could you detect with the sample you can afford?** An underpowered study wastes resources and produces inconclusive or irreproducible results; an overpowered one wastes participants, money, and (in clinical work) exposes more people to risk than necessary. Getting this right *before* data collection is the single highest-leverage statistical decision in a project.

Four quantities are locked together for any given test: **sample size (n)**, **effect size**, **significance level (α)**, and **power (1 − β)**. Fix any three and the fourth is determined. Every calculation in this skill is some rearrangement of that relationship.

This skill covers the two ways to do power analysis:
- **Closed-form** formulas (fast, exact for standard tests) — see `references/closed_form_recipes.md`.
- **Simulation / Monte Carlo** (works for *any* design or model you can simulate and analyze) — see `references/simulation_based_power.md`.

For choosing and converting effect sizes — usually the hardest part — see `references/effect_sizes.md`.

## When to Use This Skill

- Determining required sample size before collecting data (a priori power analysis)
- Finding the minimum detectable effect (MDE) for a fixed, already-determined sample size
- Producing power curves (power vs. n, or power vs. effect size) for a grant or protocol
- Justifying a sample size for an IRB submission, grant, or pre-registration
- Powering designs with unequal group sizes or non-1:1 allocation
- Powering anything without a textbook formula (mixed models, logistic/Poisson regression, cluster-randomized trials, survival analysis, mediation, interactions) via simulation
- Accounting for multiple comparisons, attrition/dropout, or clustering in the sample-size estimate

## Installation

Use **uv**. Pin versions in production; unpinned is fine for exploration.

```bash
uv pip install "statsmodels>=0.14.6" "scipy>=1.11" "pingouin>=0.6" "numpy>=1.26" matplotlib pandas
# For simulation-based power of advanced models (optional, add as needed):
uv pip install lifelines            # survival
# mixed models and GLMs come with statsmodels
```

**Compatibility note:** use `statsmodels>=0.14.6` with `scipy>=1.11` to avoid `_lazywhere` import errors on SciPy 1.16+. Pingouin 0.5+ renamed power-function arguments to match the names used below.

---

## The one decision that drives everything: the effect size

Power calculations are only as trustworthy as the effect size you feed them. **Do not invent a number.** Use, in rough order of preference:

1. A **minimally important effect** — the smallest effect that would actually change a decision or matter scientifically/clinically (the "smallest effect size of interest", SESOI). This is the most defensible basis: you power to detect what matters, not what you hope to see.
2. A **pilot or prior-study estimate**, but shrink it — published and pilot effects are inflated by publication bias and the winner's curse. Powering on a raw pilot estimate routinely underpowers the real study.
3. A **convention** (Cohen's small/medium/large) only as a last resort, and say so explicitly.

Whatever you pick, run a **sensitivity analysis**: report how required n changes across a plausible range of effect sizes, not a single point. A power analysis presented as one number hides its biggest source of uncertainty. See `references/effect_sizes.md` for benchmarks and conversions between d, f, r, η², odds ratios, and Cohen's h/w.

> **Avoid post-hoc ("observed") power.** Computing power from the effect size you just estimated is circular: it is a deterministic function of the p-value and tells you nothing new. If a study is already done and you want to know what it could have detected, report a **sensitivity analysis** (MDE at the achieved n) or, better, the confidence interval around the observed effect. This is a common reviewer complaint — do not produce observed power even if asked without flagging the issue.

---

## Quick recipes (closed-form)

The bundled `scripts/power.py` wraps statsmodels into one consistent interface so you don't have to remember which solver belongs to which test. Run from the skill directory or add `scripts/` to `sys.path`.

```python
from power import sample_size, power, mde, power_curve

# 1. How many per group to detect Cohen's d = 0.5, two-sided, 80% power?
sample_size(test="t_ind", effect_size=0.5, power=0.80, alpha=0.05)
# -> required n per group

# 2. Two groups, 3:1 allocation (e.g. more controls than cases)
sample_size(test="t_ind", effect_size=0.5, power=0.80, ratio=3.0)

# 3. Fixed n=30/group — what's the minimum detectable d at 80% power?
mde(test="t_ind", nobs1=30, power=0.80, alpha=0.05)

# 4. One-way ANOVA, 4 groups, detect Cohen's f = 0.25
sample_size(test="anova", effect_size=0.25, k_groups=4, power=0.80)

# 5. Two proportions: 0.40 vs 0.55 (auto-converts to Cohen's h)
sample_size(test="two_proportions", prop1=0.40, prop2=0.55, power=0.80)

# 6. Correlation: detect r = 0.30
sample_size(test="correlation", effect_size=0.30, power=0.80)

# 7. Power curve for the grant figure
power_curve(test="t_ind", effect_size=0.5, n_range=range(10, 120, 5),
            save="power_curve.png")
```

Supported `test=` values: `t_ind` (two independent means), `t_paired`/`t_one` (paired or one-sample mean), `anova` (one-way), `two_proportions`, `one_proportion`, `correlation`, `chi2` (goodness-of-fit / contingency via effect size *w*), `linear_regression` (R² increment / f²). Full argument tables and the underlying statsmodels calls are in `references/closed_form_recipes.md`.

---

## When there is no formula: simulate

Closed-form power exists only for a handful of simple tests. For **logistic/Poisson regression, mixed-effects / repeated-measures models, cluster-randomized trials, survival analysis, mediation, multi-way interactions, or any non-standard analysis**, the right tool is simulation. The logic is always the same three steps:

1. **Simulate** a dataset from your assumed truth (the effect you want to detect, plus realistic noise, baseline rates, cluster structure, etc.).
2. **Analyze** it with the *exact* test/model you plan to use on the real data.
3. **Repeat** many times (≥1,000; 5,000–10,000 for a stable estimate near 80%). Power is the fraction of replicates in which the test is significant.

`scripts/simulate_power.py` provides a reusable harness plus worked examples (two-group difference, logistic regression, cluster-randomized trial with an ICC, and a linear mixed model). The core is just:

```python
from simulate_power import simulate_power

def gen_and_test(n, rng):
    # build a dataset of size n under the assumed effect, run the planned test,
    # return True if the result is significant
    ...

est = simulate_power(gen_and_test, n=200, n_sims=2000, alpha=0.05)
print(f"Power at n=200: {est.power:.3f} (95% CI {est.ci_low:.3f}-{est.ci_high:.3f})")
```

Report the **Monte Carlo confidence interval** on the estimate (the harness returns it) so the reader knows whether 0.81 vs. 0.79 is signal or simulation noise. See `references/simulation_based_power.md` for the full patterns, including how to search for the n that hits target power and how to model dropout and clustering.

---

## Adjustments people forget

These routinely make the difference between an adequately powered study and an underpowered one. Apply them explicitly and state that you did.

- **Multiple comparisons.** If the analysis tests *m* hypotheses with a Bonferroni-style correction, power each test at the corrected α (e.g. α/m), which raises n. Better: power on the family-wise or FDR-controlled procedure directly via simulation. Ignoring this silently underpowers every secondary endpoint.
- **Attrition / dropout / unusable samples.** Power gives the n you need *analyzed*. Inflate the *enrolled* n: `n_enroll = ceil(n_analyzed / (1 − dropout_rate))`. A 20% dropout rate means enrolling 25% more than the formula returns.
- **Clustering (design effect).** When observations are nested (patients within clinics, cells within animals, repeated measures within subject), the effective sample size is smaller than the raw count. Inflate by the design effect `DEFF = 1 + (m − 1)·ICC`, where *m* is cluster size and ICC the intraclass correlation. Treating clustered data as independent is **pseudoreplication** and badly overstates power — for cluster-randomized designs, simulate instead.
- **One- vs. two-sided.** Two-sided is the default and almost always the right choice; a one-sided test buys power only by refusing to detect an effect in the unexpected direction. Justify any one-sided test.
- **Unequal allocation.** Equal groups are most efficient for a fixed total n. If allocation is fixed by design (e.g. 2:1 treatment:control), pass `ratio=` so the calculation reflects it.

---

## Workflow

1. **State the design and the planned analysis.** The test you will run determines the power method. If the analysis is a mixed model or GLM, go straight to simulation.
2. **Choose the effect size** on a defensible basis (SESOI > shrunk pilot > convention) and write down the justification.
3. **Set α and target power.** Conventional defaults are α = 0.05 (two-sided) and power = 0.80; 0.90 is common for confirmatory/clinical work. State them.
4. **Compute** with `scripts/power.py` (closed-form) or `scripts/simulate_power.py` (simulation).
5. **Sensitivity analysis.** Recompute across a range of plausible effect sizes and produce a power curve. This is the deliverable, not a single number.
6. **Apply adjustments** for dropout, clustering, and multiplicity.
7. **Report** following the template below.

---

## Reporting template

A defensible power statement contains every input, so a reader could reproduce it. Adapt:

```
A priori power analysis was conducted to determine the sample size needed to detect
a [between-group difference of Cohen's d = 0.50], which we considered the smallest
effect of clinical interest. With α = .05 (two-sided) and power = .80, a two-sample
t-test requires n = 64 per group (128 total; computed with statsmodels 0.14).
Allowing for 20% attrition, we will enrol 160 participants. A sensitivity analysis
showed required n ranges from 45 to 105 per group across plausible effects
d = 0.40–0.60 (Figure X).
```

For simulation: also state the data-generating assumptions (baseline rate, residual SD, ICC, cluster sizes), the number of simulations, and the Monte Carlo CI.

---

## Common pitfalls

1. **Inventing the effect size** or copying an inflated pilot estimate — the most common way power analyses go wrong.
2. **Reporting a single n** instead of a sensitivity range / power curve.
3. **Post-hoc / observed power** — circular and uninformative; use sensitivity analysis or the effect-size CI instead.
4. **Ignoring clustering** (pseudoreplication) — counting cells/measurements as if they were independent subjects.
5. **Forgetting dropout** — powering the analyzed n but enrolling the same number.
6. **Confusing α with power**, or one-sided with two-sided.
7. **Powering only the primary endpoint** while reporting secondary/interaction tests that need far larger n.
8. **Using a t-test formula for a model you won't actually fit** (e.g. planning a logistic regression with a means-based calculation) — match the power method to the planned analysis.

---

## Resources

### Scripts
- `scripts/power.py` — unified closed-form interface (`sample_size`, `power`, `mde`, `power_curve`) over statsmodels/pingouin for all standard tests.
- `scripts/simulate_power.py` — Monte Carlo power harness with `simulate_power()` and `find_sample_size()`, plus worked examples (two-group, logistic regression, cluster-randomized, linear mixed model).

### References
- `references/closed_form_recipes.md` — per-test argument tables and exact statsmodels/pingouin calls, including proportions, chi-square, and regression.
- `references/simulation_based_power.md` — full simulation patterns for GLMs, mixed models, cluster designs, survival, and dropout.
- `references/effect_sizes.md` — choosing effect sizes (SESOI), Cohen's benchmarks, and conversions between d, f, r, η²/f², OR, h, and w.

### Related skills
- **experimental-design** — once you know n, lay out the actual study (randomization, blocking, factorial/DOE, crossover, sequential designs).
- **statistical-analysis** — assumption checks, running the test, effect sizes, and APA reporting after data collection.
- **statsmodels** / **pymc** — fitting the models referenced here.

### Key references
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.).
- Lakens, D. (2022). *Sample Size Justification*. Collabra: Psychology, 8(1).
- Arnold, B. F. et al. (2011). Simulation methods to estimate design power. *BMC Medical Research Methodology*, 11:94.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/statistical-power/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/closed_form_recipes.md`

# Closed-Form Power Recipes

Exact argument tables and the underlying statsmodels/scipy calls for every test
the `scripts/power.py` helper supports. Use this when you need to call statsmodels
directly, understand an argument, or handle a case the wrapper doesn't cover.

The four solver quantities — `effect_size`, sample size, `alpha`, `power` — obey
one identity: pass three, set the fourth to `None`, and `solve_power` returns it.

## Table of contents
- [Two independent means (t-test)](#two-independent-means)
- [Paired / one-sample mean](#paired--one-sample-mean)
- [One-way ANOVA](#one-way-anova)
- [Two proportions](#two-proportions)
- [One proportion](#one-proportion)
- [Correlation](#correlation)
- [Chi-square (goodness-of-fit / contingency)](#chi-square)
- [Multiple regression (R² increment)](#multiple-regression)
- [Effect-size argument cheat sheet](#effect-size-units-per-test)

---

## Two independent means

Effect size = **Cohen's d** = (μ₁ − μ₂) / σ_pooled.

```python
from statsmodels.stats.power import TTestIndPower
analysis = TTestIndPower()

# n per group for d=0.5, 80% power, two-sided
n1 = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.80,
                          ratio=1.0, alternative="two-sided")

# achieved power at n1=64 per group
pw = analysis.solve_power(effect_size=0.5, nobs1=64, alpha=0.05,
                          ratio=1.0, alternative="two-sided")

# minimum detectable d at n1=30 per group, 80% power
d_min = analysis.solve_power(nobs1=30, alpha=0.05, power=0.80, ratio=1.0,
                             alternative="two-sided")
```

`ratio = nobs2 / nobs1`. For 2:1 allocation set `ratio=2.0`; the returned `nobs1`
is the smaller group. `alternative` ∈ `"two-sided"`, `"larger"`, `"smaller"`.

## Paired / one-sample mean

Effect size = **Cohen's dz** for paired (mean difference / SD of the differences),
or d for one-sample. Use `TTestPower` (single-sample solver); `nobs` is the number
of pairs / observations.

```python
from statsmodels.stats.power import TTestPower
TTestPower().solve_power(effect_size=0.4, alpha=0.05, power=0.80,
                         alternative="two-sided")  # -> number of pairs
```

Note: for paired designs dz depends on the within-pair correlation ρ:
`dz = d_raw / sqrt(2(1−ρ))`. Higher ρ ⇒ larger dz ⇒ smaller n. If you only know
the raw mean difference and SDs, estimate ρ or simulate.

## One-way ANOVA

Effect size = **Cohen's f** = sqrt(η² / (1 − η²)). `nobs` here is **total** n
across all groups; divide by `k_groups` for per-group n.

```python
from statsmodels.stats.power import FTestAnovaPower
total_n = FTestAnovaPower().solve_power(effect_size=0.25, k_groups=4,
                                        alpha=0.05, power=0.80)
per_group = total_n / 4
```

Conversions: f = 0.10 (small), 0.25 (medium), 0.40 (large). From η²:
`f = sqrt(eta2/(1-eta2))`. From R²: same formula with R².

## Two proportions

Effect size = **Cohen's h** = 2·asin(√p₁) − 2·asin(√p₂). Convert proportions to h,
then use the normal approximation `NormalIndPower`.

```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
h = proportion_effectsize(0.40, 0.55)
n1 = NormalIndPower().solve_power(effect_size=h, alpha=0.05, power=0.80,
                                  ratio=1.0, alternative="two-sided")
```

Alternative (exact-ish, gives per-group n directly, handles unequal n via `ratio`):

```python
from statsmodels.stats.proportion import samplesize_proportions_2indep_onetail
# one-sided; double alpha intent by passing alpha/... per your convention
```

For small samples or rare events, prefer **simulation** with the exact test you'll
run (Fisher's exact, or a chi-square with continuity correction).

## One proportion

Test p against a fixed reference p₀. Convert both to the arcsine scale via Cohen's h
and treat the reference group as infinite (`ratio=0`).

```python
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
h = proportion_effectsize(0.60, 0.50)
n = NormalIndPower().solve_power(effect_size=h, alpha=0.05, power=0.80, ratio=0.0)
```

For exact binomial planning use `statsmodels.stats.proportion.proportion_effectsize`
with the exact-test power via simulation if the sample is small.

## Correlation

Effect size = **Pearson r**. No statsmodels solver; use the Fisher z transform
(implemented in `power.py`). Required n for r at power 1−β, two-sided:

```
z_r = arctanh(r)
n   = ((z_{1-α/2} + z_{1-β}) / z_r)^2 + 3
```

`pingouin.power_corr(r=0.3, power=0.8, alternative="two-sided")` gives the same
answer if you prefer a library call.

## Chi-square

Effect size = **Cohen's w** = sqrt(Σ (p_i − p0_i)² / p0_i). For a contingency table,
`w = sqrt(χ²/N)` and equals Cramér's V·sqrt(min(r−1, c−1)). Degrees of freedom:
goodness-of-fit `dof = k − 1`; contingency `dof = (r−1)(c−1)`. `n_bins = dof + 1`.

```python
from statsmodels.stats.power import GofChisquarePower
n = GofChisquarePower().solve_power(effect_size=0.3, n_bins=5, alpha=0.05, power=0.80)
```

w benchmarks: 0.10 (small), 0.30 (medium), 0.50 (large).

## Multiple regression

Effect size = **Cohen's f²** = R²/(1−R²) for the overall model, or
ΔR²/(1−R²_full) for a set of added predictors. `power.py` solves this directly via
the noncentral F (noncentrality λ = f²·n), which is more reliable than
statsmodels' `FTestPower` for sample-size search.

```python
from power import sample_size, power
# detect f^2 = 0.15 from 3 tested predictors (3 total in the model)
sample_size("linear_regression", effect_size=0.15, df_num=3, k_total=3, power=0.80)
```

- `df_num` = number of predictors being **tested** (the numerator df).
- `k_total` = total predictors in the model (including controls). `df_denom = n − k_total − 1`.

f² benchmarks: 0.02 (small), 0.15 (medium), 0.35 (large).

## Effect-size units per test

| Test | `power.py` `test=` | Effect size | Small / Medium / Large |
|------|--------------------|-------------|------------------------|
| Two independent means | `t_ind` | Cohen's d | 0.2 / 0.5 / 0.8 |
| Paired / one-sample | `t_paired`, `t_one` | Cohen's d (dz) | 0.2 / 0.5 / 0.8 |
| One-way ANOVA | `anova` | Cohen's f | 0.1 / 0.25 / 0.4 |
| Two proportions | `two_proportions` | Cohen's h (auto from props) | 0.2 / 0.5 / 0.8 |
| One proportion | `one_proportion` | Cohen's h (auto) | 0.2 / 0.5 / 0.8 |
| Correlation | `correlation` | Pearson r | 0.1 / 0.3 / 0.5 |
| Chi-square | `chi2` | Cohen's w | 0.1 / 0.3 / 0.5 |
| Regression (ΔR²) | `linear_regression` | Cohen's f² | 0.02 / 0.15 / 0.35 |

Benchmarks are last-resort conventions — prefer a smallest-effect-of-interest.
See `effect_sizes.md`.

### `references/effect_sizes.md`

# Choosing and Converting Effect Sizes

The effect size is the input that makes or breaks a power analysis, and it is the
one people most often get wrong. Power computed from a guessed or inflated effect
is worse than no power analysis, because it carries false authority. This file
covers how to pick a defensible value and how to convert between the metrics
different tests use.

## How to choose (in order of preference)

### 1. Smallest effect size of interest (SESOI) — best
Power to detect the smallest effect that would actually **change a decision** or
matter scientifically/clinically, not the effect you hope or expect to see. Ways to
set it:
- **Anchor-based:** the smallest difference patients/users can perceive or that
  crosses a clinical threshold (e.g. a 5-point change on a validated scale).
- **Resource/decision-based:** the smallest effect that would justify adopting the
  intervention given its cost.
- **Benchmark-based:** an effect smaller than which you'd treat the result as
  practically null.

Powering on the SESOI is the most defensible choice: if the true effect is larger,
you're even better powered; if it's smaller, you've decided it doesn't matter.

### 2. Prior estimate — but shrink it
Pilot studies and published effects are **biased upward** (publication bias, the
"winner's curse," and the fact that significant pilots are the ones that get
followed up). Powering on a raw pilot d routinely underpowers the real study. If
you must use a prior estimate:
- Use the **lower bound of its confidence interval**, or
- Apply a **shrinkage / safeguard** (e.g. Perugini et al.'s safeguard power uses the
  CI lower limit), and
- Never rely on a single small pilot (n < ~50) for a point estimate of the effect.

### 3. Convention — last resort, and say so
Cohen's small/medium/large are arbitrary and field-blind. They were never meant as
substitutes for domain knowledge. Use them only when nothing better exists, state
explicitly that you did, and prefer "small" unless you have a reason — most real
effects in many fields are small.

## Always do a sensitivity analysis
Whatever you pick, report how required n varies across a plausible range of effects
(e.g. a power curve, or a small table of n at d = 0.3, 0.4, 0.5). A single n hides
the dominant source of uncertainty. This is the actual deliverable of a good power
analysis.

## Benchmark table (Cohen's conventions)

| Metric | Used for | Small | Medium | Large |
|--------|----------|-------|--------|-------|
| d | mean differences (t-tests) | 0.20 | 0.50 | 0.80 |
| f | ANOVA | 0.10 | 0.25 | 0.40 |
| f² | regression / multiple R² | 0.02 | 0.15 | 0.35 |
| r | correlation | 0.10 | 0.30 | 0.50 |
| η² (eta-squared) | ANOVA variance explained | 0.01 | 0.06 | 0.14 |
| h | proportions (arcsine) | 0.20 | 0.50 | 0.80 |
| w | chi-square | 0.10 | 0.30 | 0.50 |
| OR | 2×2 odds ratio | ~1.5 | ~2.5 | ~4.3 |

(OR benchmarks are very context-dependent and depend on the base rate — treat as
rough only.)

## Conversions

**d ↔ r**  (two-group comparison ↔ point-biserial)
```
r = d / sqrt(d^2 + 4)            # equal groups
d = 2r / sqrt(1 - r^2)
```

**d ↔ Cohen's f**  (k groups; for two equal groups f = d/2)
```
f = d / 2                        # two groups
```

**f ↔ η²**
```
f   = sqrt(eta2 / (1 - eta2))
eta2 = f^2 / (1 + f^2)
```

**f² ↔ R²**  (regression)
```
f2 = R2 / (1 - R2)               # whole model
f2 = dR2 / (1 - R2_full)         # increment from added predictors
```

**proportions → Cohen's h**
```
h = 2*asin(sqrt(p1)) - 2*asin(sqrt(p2))
```
In Python: `statsmodels.stats.proportion.proportion_effectsize(p1, p2)`.

**proportions → Cohen's w** (for chi-square, against expected p0_i)
```
w = sqrt( sum( (p_i - p0_i)^2 / p0_i ) )
```
For a 2×2 table, `w = sqrt(chi2 / N)`, and `w = V * sqrt(min(r-1, c-1))` where V is
Cramér's V.

**odds ratio → log-odds** (for logistic-regression power by simulation)
```
beta = log(OR)                   # coefficient to plug into the simulated linear predictor
```

**standardized → raw**
A standardized effect is only as good as the SD you divide by. If you know the raw
difference and the SD, work in raw units and convert at the end:
`d = (mean1 - mean2) / sd_pooled`. For paired designs, `dz` uses the SD of the
*differences*, which depends on the within-pair correlation — see
`closed_form_recipes.md`.

## Common mistakes

- **Using the observed/expected effect instead of the SESOI** — you end up powered
  for your hopes, not for what matters.
- **Copying a published d without shrinking** — inflated by publication bias.
- **Mixing up d and f, or η² and f²** — they differ by the conversions above; a
  factor-of-2 error in d quadruples or quarters the required n.
- **Reporting one number** — always show the sensitivity range.
- **Treating Cohen's benchmarks as truth** — they're conventions, not measurements.

### `references/simulation_based_power.md`

# Simulation-Based (Monte Carlo) Power

Closed-form power exists for a handful of standard tests. For everything else,
simulate. This is not a second-best approximation — for complex designs it is the
*correct* method, and it has one big advantage: the power estimate uses the exact
analysis you will run on the real data, so there is no mismatch between the
planning model and the analysis model.

## The recipe (always the same)

1. **Simulate** a dataset of size *n* from your assumed truth: the effect you want
   to detect, plus realistic structure (baseline rates, residual SD, cluster random
   effects, dropout, covariate distributions).
2. **Analyze** it with the *exact* model/test planned for the real study.
3. **Repeat** R times. Power = fraction of replicates where the test is significant.
   Use R ≥ 1,000; use 5,000–10,000 for a stable estimate near the 80% decision point.

Always report the **Monte Carlo confidence interval** on the estimate (the
`scripts/simulate_power.py` harness returns a Wilson interval). With R = 1,000 the
±2 SE width near p = 0.8 is roughly ±0.025, so don't over-interpret 0.81 vs 0.79.

## Using the harness

`scripts/simulate_power.py` gives you `simulate_power()` and `find_sample_size()`.
You supply a function `gen_and_test(n, rng) -> bool` that builds one dataset, runs
the analysis, and returns whether it was significant. The `rng` is a seeded
`numpy.random.Generator` so runs are reproducible and replicates are independent.

```python
from simulate_power import simulate_power, find_sample_size

def gen_and_test(n, rng):
    # ... simulate n observations under the assumed effect ...
    # ... fit the planned model ...
    return pvalue < 0.05

# power at a fixed n
print(simulate_power(gen_and_test, n=200, n_sims=2000))

# search for the n that hits 80% power
n, est = find_sample_size(gen_and_test, target_power=0.80, n_sims=2000)
```

The file ships four adaptable examples: two-group difference (a sanity check
against the closed-form t-test), logistic regression, a cluster-randomized trial
with an ICC, and a repeated-measures linear mixed model. Copy the closest one and
edit the data-generating block.

## When you must simulate

| Design / analysis | Why no formula | What to simulate |
|-------------------|----------------|------------------|
| Logistic / Poisson regression | Power depends on the full covariate distribution | Generate predictors, compute the linear predictor, draw the outcome, fit the GLM |
| Mixed-effects / repeated measures | Random effects + within-subject correlation | Draw subject/cluster random effects, then observations; fit `mixedlm` |
| Cluster-randomized trial | ICC inflates variance; clusters are the unit | Cluster random intercepts via ICC; fit a mixed model or use the design effect |
| Survival (Cox / log-rank) | Censoring and event-time distribution | Draw event and censoring times; fit `lifelines` CoxPH or run a log-rank test |
| Interaction terms | Power for an interaction ≪ power for main effects | Generate the factorial structure and the interaction effect; test that coefficient |
| Mediation | Product-of-coefficients null is non-normal | Simulate the path model; bootstrap or test the indirect effect |
| Non-standard / custom test | No theory at all | Whatever your analysis script does |

## Key correctness points

- **Analyze exactly as planned.** If the real analysis adjusts for covariates,
  include them in the simulation. If it uses a robust SE or a specific correction,
  apply it in `gen_and_test`. The whole value of simulation is fidelity to the plan.
- **Handle estimation failures.** GLMs and mixed models can fail to converge or hit
  perfect separation. Wrap the fit in `try/except` and count a failure as
  *not significant* (conservative). If failures are common, that itself is a
  warning about the design or sample size.
- **Watch Type I error too.** As a check, simulate under the *null* (effect = 0)
  and confirm the rejection rate ≈ α. If it's inflated (common with small-cluster
  mixed models or naive cluster SEs), your planned analysis is anticonservative and
  the power number is meaningless until you fix the analysis.
- **Seed it.** A fixed seed makes the search reproducible and stops `find_sample_size`
  from chasing simulation noise around the boundary.

## Modeling realistic complications

- **Dropout.** Either simulate missingness directly (drop rows / occasions under
  the assumed mechanism, then analyze the reduced data — captures the real power
  loss including any bias), or compute the analyzed n and inflate the enrolled n by
  `1/(1−dropout)`.
- **Clustering / ICC.** Split total variance into between-cluster (τ²) and residual
  (σ²) with `ICC = τ²/(τ²+σ²)`, draw a cluster random effect ~ N(0, τ), add it to
  every member of the cluster. See `example_cluster_randomized`.
- **Unequal allocation / stratification.** Generate the exact group sizes and strata
  the design will produce; don't assume balance the design won't deliver.
- **Repeated measures.** Subject random intercept (and slope, if relevant) plus a
  within-subject residual; the within-subject correlation is `τ²/(τ²+σ²)`.

## Reporting a simulation-based power analysis

State enough that someone could rerun it:

```
Power was estimated by simulation (5,000 replicates per sample size). Data were
generated assuming a baseline event rate of 20%, a treatment log-odds of 0.8, and
analyzed with logistic regression adjusting for age and site, matching the planned
analysis. A sample of n = 150 per arm yielded 82% power (95% Monte Carlo CI
80.5-83.5%) at α = .05 (two-sided). Code is available at [link].
```

### `scripts/power.py`

```python
"""Unified closed-form power / sample-size interface over statsmodels and scipy.

One function each for the three things people actually want:
  - sample_size(...)  : solve for n given effect size, alpha, power
  - power(...)        : solve for achieved power given n and effect size
  - mde(...)          : solve for the minimum detectable effect given n and power
  - power_curve(...)  : plot power vs. n (or vs. effect size) for planning figures

Every call routes to the right statsmodels solver based on `test=`, so callers
don't need to remember which Power class belongs to which test. All four solver
quantities (effect_size, nobs, alpha, power) obey the identity "fix three, solve
the fourth"; these helpers just expose that cleanly.

Supported tests:
  t_ind          two independent means (Cohen's d)
  t_paired/t_one paired or one-sample mean (Cohen's d)
  anova          one-way ANOVA, k groups (Cohen's f)
  two_proportions  two independent proportions (give prop1, prop2; uses Cohen's h)
  one_proportion   one proportion vs. a reference (give prop1, prop0)
  correlation    Pearson r (give effect_size=r)
  chi2           goodness-of-fit / contingency (Cohen's w; give dof)
  linear_regression  added predictors via Cohen's f^2 (give f2 as effect_size, df_num)

Requires: statsmodels>=0.14.6, scipy>=1.11, numpy, matplotlib.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from statsmodels.stats.power import (
    FTestAnovaPower,
    GofChisquarePower,
    NormalIndPower,
    TTestIndPower,
    TTestPower,
)
from statsmodels.stats.proportion import proportion_effectsize


# --------------------------------------------------------------------------- #
# internal: build the statsmodels solver and the kwargs for the given test
# --------------------------------------------------------------------------- #
def _resolve(test, effect_size, alpha, alternative, **kw):
    """Return (solver, base_kwargs, n_key) for a test.

    n_key is the keyword the solver uses for "number of observations" so the
    sample_size/power/mde wrappers can fill in the right argument generically.
    """
    test = test.lower()

    if test == "t_ind":
        solver = TTestIndPower()
        es = effect_size
        base = dict(effect_size=es, alpha=alpha, alternative=alternative,
                    ratio=kw.get("ratio", 1.0))
        return solver, base, "nobs1"

    if test in ("t_paired", "t_one"):
        solver = TTestPower()
        base = dict(effect_size=effect_size, alpha=alpha, alternative=alternative)
        return solver, base, "nobs"

    if test == "anova":
        solver = FTestAnovaPower()
        k = kw.get("k_groups")
        if k is None:
            raise ValueError("anova requires k_groups=")
        base = dict(effect_size=effect_size, alpha=alpha, k_groups=k)
        return solver, base, "nobs"  # nobs = TOTAL n across all groups

    if test == "two_proportions":
        # convert proportions to Cohen's h, then use the normal approximation
        p1, p2 = kw.get("prop1"), kw.get("prop2")
        if p1 is None or p2 is None:
            raise ValueError("two_proportions requires prop1= and prop2=")
        h = proportion_effectsize(p1, p2)
        solver = NormalIndPower()
        base = dict(effect_size=h, alpha=alpha, alternative=alternative,
                    ratio=kw.get("ratio", 1.0))
        return solver, base, "nobs1"

    if test == "one_proportion":
        p1, p0 = kw.get("prop1"), kw.get("prop0")
        if p1 is None or p0 is None:
            raise ValueError("one_proportion requires prop1= and prop0=")
        h = proportion_effectsize(p1, p0)
        # one-sample: NormalIndPower with an effectively infinite second group
        solver = NormalIndPower()
        base = dict(effect_size=h, alpha=alpha, alternative=alternative, ratio=0.0)
        return solver, base, "nobs1"

    if test == "correlation":
        # Power for Pearson r via Fisher z; handled analytically below, but we
        # still route through a solver-shaped object for a uniform interface.
        return "correlation", dict(effect_size=effect_size, alpha=alpha,
                                   alternative=alternative), "nobs"

    if test == "chi2":
        solver = GofChisquarePower()
        dof = kw.get("dof")
        if dof is None:
            raise ValueError("chi2 requires dof= (n_bins-1, or (r-1)(c-1))")
        base = dict(effect_size=effect_size, alpha=alpha, n_bins=dof + 1)
        return solver, base, "nobs"

    if test == "linear_regression":
        # Handled by a dedicated noncentral-F solver (statsmodels' FTestPower is
        # unreliable when solving for sample size). See _reg_* helpers below.
        df_num = kw.get("df_num")
        if df_num is None:
            raise ValueError("linear_regression requires df_num= (number of tested predictors)")
        return "regression", dict(effect_size=effect_size, alpha=alpha,
                                  df_num=df_num,
                                  k_total=kw.get("k_total", df_num)), "nobs"

    raise ValueError(f"unknown test '{test}'")


# --------------------------------------------------------------------------- #
# correlation power (Fisher z transform) -- closed form, no statsmodels solver
# --------------------------------------------------------------------------- #
def _corr_power(r, n, alpha, alternative):
    from scipy import stats
    z = math.atanh(r)
    se = 1.0 / math.sqrt(n - 3)
    if alternative == "two-sided":
        zc = stats.norm.ppf(1 - alpha / 2)
    else:
        zc = stats.norm.ppf(1 - alpha)
    return float(stats.norm.cdf(z / se - zc) + stats.norm.cdf(-z / se - zc))


def _corr_sample_size(r, alpha, power, alternative):
    from scipy import stats
    z = abs(math.atanh(r))
    if alternative == "two-sided":
        zc = stats.norm.ppf(1 - alpha / 2)
    else:
        zc = stats.norm.ppf(1 - alpha)
    zp = stats.norm.ppf(power)
    return ((zc + zp) / z) ** 2 + 3


# --------------------------------------------------------------------------- #
# multiple-regression power via the noncentral F (Cohen's f^2)
# --------------------------------------------------------------------------- #
def _reg_power(f2, n, df_num, k_total, alpha):
    """Power of the F-test for df_num tested predictors in a model with k_total
    total predictors, total sample size n. Noncentrality lambda = f^2 * n."""
    from scipy import stats
    df_denom = n - k_total - 1
    if df_denom < 1:
        return 0.0
    ncp = f2 * n
    crit = stats.f.ppf(1 - alpha, df_num, df_denom)
    return float(1 - stats.ncf.cdf(crit, df_num, df_denom, ncp))


def _reg_sample_size(f2, df_num, k_total, alpha, power):
    n = k_total + 2  # smallest n with df_denom >= 1
    while _reg_power(f2, n, df_num, k_total, alpha) < power:
        n += 1
        if n > 1_000_000:
            raise RuntimeError("sample size did not converge below 1e6")
    return n


def _reg_mde(n, df_num, k_total, alpha, power):
    """Smallest detectable f^2 at fixed n (bisection)."""
    lo, hi = 1e-6, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _reg_power(mid, n, df_num, k_total, alpha) < power:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #
def sample_size(test, effect_size=None, alpha=0.05, power=0.80,
                alternative="two-sided", round_up=True, **kw):
    """Solve for required sample size.

    For per-group tests (t_ind, two_proportions) returns n PER GROUP.
    For anova returns TOTAL n across all groups. For chi2/regression returns total n.
    """
    solver, base, n_key = _resolve(test, effect_size, alpha, alternative, **kw)

    if solver == "correlation":
        n = _corr_sample_size(effect_size, alpha, power, alternative)
        return math.ceil(n) if round_up else n

    if solver == "regression":
        return _reg_sample_size(base["effect_size"], base["df_num"],
                                base["k_total"], alpha, power)

    base["power"] = power
    base[n_key] = None
    n = solver.solve_power(**base)
    if round_up:
        n = math.ceil(n)
    return n


def power(test, effect_size=None, nobs1=None, nobs=None, alpha=0.05,
          alternative="two-sided", **kw):
    """Solve for achieved power given the sample size.

    Pass nobs1 for per-group tests (t_ind, two_proportions), nobs for total-n tests.
    """
    solver, base, n_key = _resolve(test, effect_size, alpha, alternative, **kw)

    n = nobs1 if nobs1 is not None else nobs
    if n is None:
        raise ValueError("provide nobs1= (per-group tests) or nobs= (total-n tests)")

    if solver == "correlation":
        return _corr_power(effect_size, n, alpha, alternative)

    if solver == "regression":
        return _reg_power(base["effect_size"], n, base["df_num"],
                          base["k_total"], alpha)

    base[n_key] = n
    return float(solver.solve_power(**base))


def mde(test, nobs1=None, nobs=None, alpha=0.05, power=0.80,
        alternative="two-sided", **kw):
    """Solve for the minimum detectable effect (standardized) at a fixed n.

    Returns the effect size in the test's native units (d, f, h, w, r, ...).
    """
    solver, base, n_key = _resolve(test, None, alpha, alternative, **kw)

    n = nobs1 if nobs1 is not None else nobs
    if n is None:
        raise ValueError("provide nobs1= or nobs=")

    if solver == "correlation":
        # invert the Fisher-z sample-size formula
        from scipy import stats
        zc = stats.norm.ppf(1 - alpha / 2) if alternative == "two-sided" \
            else stats.norm.ppf(1 - alpha)
        zp = stats.norm.ppf(power)
        z = (zc + zp) / math.sqrt(n - 3)
        return float(math.tanh(z))

    if solver == "regression":
        return _reg_mde(n, base["df_num"], base["k_total"], alpha, power)

    base["power"] = power
    base["effect_size"] = None
    base[n_key] = n
    return float(solver.solve_power(**base))


def power_curve(test, effect_size=None, n_range=None, alpha=0.05, power_target=0.80,
                alternative="two-sided", save=None, show=False, **kw):
    """Plot power vs. sample size. Returns (n_array, power_array).

    n_range iterates the per-group n for per-group tests, total n otherwise.
    """
    import matplotlib.pyplot as plt

    if n_range is None:
        n_range = range(5, 205, 5)
    ns = np.array(list(n_range), dtype=float)

    pwr = []
    for n in ns:
        if test in ("t_ind", "two_proportions"):
            pwr.append(power(test, effect_size=effect_size, nobs1=n, alpha=alpha,
                             alternative=alternative, **kw))
        else:
            pwr.append(power(test, effect_size=effect_size, nobs=n, alpha=alpha,
                             alternative=alternative, **kw))
    pwr = np.array(pwr)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ns, pwr, lw=2)
    ax.axhline(power_target, ls="--", color="crimson", lw=1,
               label=f"target power = {power_target:g}")
    ax.set_xlabel("Sample size" + (" per group" if test in ("t_ind", "two_proportions") else " (total)"))
    ax.set_ylabel("Power (1 - β)")
    ax.set_ylim(0, 1.02)
    es_label = effect_size if effect_size is not None else ""
    ax.set_title(f"Power curve: {test} (effect = {es_label}, α = {alpha:g})")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if save:
        fig.savefig(save, dpi=150)
    if show:
        plt.show()
    plt.close(fig)
    return ns, pwr


if __name__ == "__main__":
    # quick smoke test of the main paths
    print("t_ind  d=0.5, 80% power -> n/group =",
          sample_size("t_ind", effect_size=0.5, power=0.80))
    print("anova  f=0.25, k=4, 80% -> total n =",
          sample_size("anova", effect_size=0.25, k_groups=4, power=0.80))
    print("2 props 0.40 vs 0.55, 80% -> n/group =",
          sample_size("two_proportions", prop1=0.40, prop2=0.55, power=0.80))
    print("correlation r=0.30, 80% -> n =",
          sample_size("correlation", effect_size=0.30, power=0.80))
    print("MDE for t_ind at n=30/group, 80% power -> d =",
          round(mde("t_ind", nobs1=30, power=0.80), 3))
    print("power for t_ind d=0.5 at n=64/group ->",
          round(power("t_ind", effect_size=0.5, nobs1=64), 3))
```

### `scripts/simulate_power.py`

```python
"""Monte Carlo power for designs with no closed-form formula.

Closed-form power covers a handful of standard tests. For anything else --
logistic/Poisson regression, mixed-effects models, cluster-randomized trials,
survival analysis, mediation, interactions -- you estimate power by simulation:

    1. simulate a dataset under the assumed truth
    2. analyze it with the EXACT test/model you will use on real data
    3. repeat many times; power = fraction of replicates that reach significance

This module provides the harness (`simulate_power`, `find_sample_size`) plus four
worked, runnable examples. Copy an example and swap in your own data-generating
process and analysis -- that is the intended workflow.

Requires: numpy, scipy, statsmodels. The survival example also needs lifelines.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass
class PowerEstimate:
    power: float
    n_sims: int
    n: int
    ci_low: float
    ci_high: float

    def __str__(self):
        return (f"n={self.n}: power={self.power:.3f} "
                f"(95% MC CI {self.ci_low:.3f}-{self.ci_high:.3f}, {self.n_sims} sims)")


def _wilson_ci(k, n, z=1.96):
    """Wilson score interval for a proportion -- the right CI for a simulated rate."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def simulate_power(gen_and_test, n, n_sims=2000, alpha=0.05, seed=0):
    """Estimate power at sample size `n`.

    gen_and_test(n, rng) -> bool : build a dataset of size n under the assumed
        effect, run the planned analysis, and return True iff it is significant.
        It receives a numpy Generator `rng` so results are reproducible and each
        replicate is independent. (Take alpha into account inside the function,
        or compare a returned p-value yourself; see examples.)

    Returns a PowerEstimate including a Wilson confidence interval, so you can
    tell whether 0.81 vs 0.79 is real or just simulation noise.
    """
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_sims):
        if gen_and_test(n, rng):
            hits += 1
    lo, hi = _wilson_ci(hits, n_sims)
    return PowerEstimate(power=hits / n_sims, n_sims=n_sims, n=n,
                         ci_low=lo, ci_high=hi)


def find_sample_size(gen_and_test, target_power=0.80, n_sims=2000, alpha=0.05,
                     lo=10, hi=2000, seed=0, verbose=True):
    """Smallest n reaching target_power, via bisection over n.

    Assumes power is (roughly) monotincreasing in n -- true for essentially all
    real designs. Uses a fixed seed per n so the search is stable; widen n_sims
    near the boundary if the curve is noisy. Returns (n, PowerEstimate).
    """
    # expand hi until it clears target (guards against too-small upper bound)
    while True:
        est_hi = simulate_power(gen_and_test, hi, n_sims, alpha, seed)
        if est_hi.power >= target_power or hi >= 1_000_000:
            break
        lo, hi = hi, hi * 2

    best = est_hi
    while lo < hi:
        mid = (lo + hi) // 2
        est = simulate_power(gen_and_test, mid, n_sims, alpha, seed)
        if verbose:
            print(est)
        if est.power >= target_power:
            hi, best = mid, est
        else:
            lo = mid + 1
    return hi, best


# ========================================================================== #
# Worked examples -- run this file directly to see them.
# Each is a `gen_and_test(n, rng)` you can adapt.
# ========================================================================== #

def example_two_group_difference(effect=0.5, sd=1.0, alpha=0.05):
    """Two-group difference in means (sanity check vs. the closed-form t-test)."""
    from scipy import stats

    def gen_and_test(n, rng):  # n per group
        a = rng.normal(0.0, sd, n)
        b = rng.normal(effect, sd, n)
        _, p = stats.ttest_ind(a, b)
        return p < alpha

    return gen_and_test


def example_logistic_regression(beta=0.8, base_rate=0.2, x_sd=1.0, alpha=0.05):
    """Power for a single coefficient in logistic regression.

    beta is the log-odds change per 1-SD increase in a continuous predictor x.
    No closed form -- this is the canonical reason to simulate.
    """
    import statsmodels.api as sm

    intercept = math.log(base_rate / (1 - base_rate))

    def gen_and_test(n, rng):
        x = rng.normal(0, x_sd, n)
        logit = intercept + beta * x
        p = 1 / (1 + np.exp(-logit))
        y = rng.binomial(1, p)
        X = sm.add_constant(x)
        try:
            res = sm.Logit(y, X).fit(disp=0)
            return res.pvalues[1] < alpha
        except Exception:
            return False  # non-convergence / perfect separation -> not significant

    return gen_and_test


def example_cluster_randomized(effect=0.3, icc=0.05, cluster_size=20,
                               resid_sd=1.0, alpha=0.05):
    """Cluster-randomized trial: clusters (not individuals) are randomized.

    Ignoring the clustering (analyzing individuals as independent) would badly
    overstate power -- that is pseudoreplication. Here `n` is the number of
    clusters PER ARM; the analysis is a mixed model with a random cluster intercept.
    """
    import statsmodels.formula.api as smf
    import pandas as pd

    # split total variance into between-cluster (tau^2) and residual by the ICC
    tau = math.sqrt(icc * resid_sd**2 / (1 - icc)) if icc > 0 else 0.0

    def gen_and_test(n, rng):  # n clusters per arm
        rows = []
        cid = 0
        for arm in (0, 1):
            for _ in range(n):
                u = rng.normal(0, tau)  # cluster random effect
                for _ in range(cluster_size):
                    y = effect * arm + u + rng.normal(0, resid_sd)
                    rows.append((y, arm, cid))
                cid += 1
        df = pd.DataFrame(rows, columns=["y", "arm", "cluster"])
        try:
            res = smf.mixedlm("y ~ arm", df, groups=df["cluster"]).fit()
            return res.pvalues["arm"] < alpha
        except Exception:
            return False

    return gen_and_test


def example_linear_mixed_repeated(effect=0.4, n_timepoints=3, subj_sd=0.7,
                                  resid_sd=1.0, alpha=0.05):
    """Repeated-measures: a linear time trend within subjects, random intercepts.

    `n` is the number of subjects; each is measured at n_timepoints occasions.
    `effect` is the slope per time unit. Tests whether the time slope != 0.
    """
    import statsmodels.formula.api as smf
    import pandas as pd

    def gen_and_test(n, rng):  # n subjects
        rows = []
        for s in range(n):
            b0 = rng.normal(0, subj_sd)
            for t in range(n_timepoints):
                y = b0 + effect * t + rng.normal(0, resid_sd)
                rows.append((y, t, s))
        df = pd.DataFrame(rows, columns=["y", "time", "subj"])
        try:
            res = smf.mixedlm("y ~ time", df, groups=df["subj"]).fit()
            return res.pvalues["time"] < alpha
        except Exception:
            return False

    return gen_and_test


if __name__ == "__main__":
    print("== two-group difference (compare to closed-form t-test n/group=64) ==")
    g = example_two_group_difference(effect=0.5)
    print(simulate_power(g, n=64, n_sims=2000))

    print("\n== logistic regression, beta=0.8 ==")
    g = example_logistic_regression(beta=0.8, base_rate=0.2)
    print(simulate_power(g, n=150, n_sims=1000))

    print("\n== search: subjects needed for repeated-measures slope=0.4 ==")
    g = example_linear_mixed_repeated(effect=0.4, n_timepoints=3)
    n, est = find_sample_size(g, target_power=0.80, n_sims=500, lo=10, hi=60,
                              verbose=False)
    print(f"-> need ~{n} subjects ({est})")
```
