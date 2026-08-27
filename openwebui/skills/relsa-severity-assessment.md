---
name: relsa-severity-assessment
description: Multivariate severity assessment and humane endpoint prediction for laboratory animal studies using the RELSA (RELative Severity Assessment) score and ARIMA-based foRcast forecasting. Use when combining welfare readouts — body weight or weight loss, body temperature, clinical or nesting scores, biomarkers, activity, heart rate, burrowing, wheel running — into one severity score per animal per day, when asking which animals are at risk of reaching a humane endpoint or when one will be reached, when defining attention/danger zones or thresholds on a severity scale by kernel density estimation, or when reporting severity for a 3Rs, refinement, animal-welfare, or EU Directive 2010/63/EU severity-assessment context. Covers directionality ("turned" variables), baseline normalization, reference sets, RELSA weights, ARIMA prediction intervals, and RMSE/PICP/MPIW evaluation.
---

# RELSA severity assessment and humane endpoint forecasting

## Overview

Severity assessment in animal research is legally mandatory and scientifically load-bearing:
it drives humane endpoint decisions, and poor welfare monitoring degrades reproducibility.
The usual practice evaluates each readout in isolation — weight loss here, a clinical score
there — which makes it hard to say how badly an individual animal is actually doing.

This skill implements two published procedures that address that:

- **RELSA** (Talbot et al., 2022) combines several outcome measures into one score per animal
  per time point, expressed *relative to a reference set of known burden*. RELSA = 0 is
  baseline; RELSA = 1 means the animal has reached the reference set's maximum deviation.
- **foRcast** (Lutscher et al., 2026) fits an ARIMA model to an individual animal's RELSA
  trajectory and forecasts the next score with a 95% prediction interval, so animals heading
  for a humane endpoint can be identified before they get there. Kernel density estimation on
  the RELSA scale supplies candidate *attention* and *danger* zones for interpretation.

The point is **refinement**: give at-risk animals attention earlier, and avoid euthanising
animals that would have recovered. Both procedures are aids to severity assessment, not
decision rules — see [Boundaries](#boundaries-state-these-when-you-report).

## When to use this skill

- Combining weight loss, temperature, clinical scoring, biomarkers, or telemetry into a single
  per-animal severity score
- Asking which animals in a cohort are at risk of reaching a humane endpoint, or predicting
  the severity score at a coming time point
- Comparing severity between treatment groups, interventions, or animal models on a common
  relative scale
- Defining thresholds or zones on a severity scale from the data
- Writing the severity-assessment section of an animal welfare report, a 3Rs/refinement
  analysis, or an application under EU Directive 2010/63/EU

For general forecasting of a time series that is not a severity score, use
**timesfm-forecasting** or **statsmodels**. For study design and sample size, use
**experimental-design** and **statistical-power**.

## Installation

```bash
uv pip install "numpy>=1.26" "pandas>=2.0" "scipy>=1.11" "statsmodels>=0.14" matplotlib
```

`relsa_score.py` and `kde_thresholds.py` need only numpy/pandas/scipy; statsmodels is required
for forecasting and matplotlib only for figures.

## Data format

One row per animal per time point, in a CSV:

| id | treatment | condition | day | temp | weight | score | il6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | treated | endpoint | -1 | 37.15 | 25.17 | 0 | 35.1 |
| M01 | treated | endpoint | 0 | 37.26 | 25.25 | 0 | 39.5 |
| M01 | treated | endpoint | 1 | 35.83 | 23.12 | 4 | 162.0 |

- `id` and a time column (`day`, `time`, `hour`, …) are required; `treatment` and `condition`
  are optional labels used for grouping and for selecting the reference set.
- Time may be days, hours, or minutes — just keep it monotonic per animal. The RELSA
  convention codes the baseline time point as `-1`.
- **One row per animal per time point.** Average hourly telemetry to one value per interval
  first (the published models average heart rate, HRV, and temperature, and sum activity).
- Leave missing measurements empty. They are dropped from the score, never imputed — a
  missing value treated as "no deviation" biases severity downward.

`assets/example_cohort.csv` is a small synthetic cohort (6 mice, 9 days, temperature, body
weight, an 0–8 clinical score, and an IL-6-like biomarker) used by every command below, so
each one is runnable as written.

## The four decisions that determine the result

Make these explicitly and write them into the methods. Nothing else about the procedure
matters as much.

**1. Directionality — which variables rise under worsening?** Falling is the default (body
weight, activity, food intake, burrowing, wheel running). Variables that *rise* must be
declared as `--turned`: clinical scores, inflammatory biomarkers, fever, tachycardia. Get
this wrong and the variable contributes nothing at all, silently, because deviations in the
"wrong" direction are floored at zero. Body temperature is model-dependent — it *falls* in
sepsis and endotoxaemia, *rises* in fever models. Nothing in the data can settle this for you:
in the published sepsis model activity legitimately swings further above baseline than below,
so only a variable that *never once* moves the declared way is detectable, and
`build_reference()` warns about exactly that case.

**2. The reference set — relative to what?** RELSA scores mean nothing without it. Use the
group assumed to carry the greatest burden in your model (the published studies use the
highest-dose or endpoint-reaching treatment group). Too mild a reference pushes every score
above 1; too severe compresses everything toward 0. Save it with `--save-reference` and reuse
it with `--load-reference` so later cohorts stay on the same scale.

**3. Scores with a zero baseline.** A clinical score of 0 in a healthy animal cannot be
ratio-normalized — `0/0` is undefined. Use `--score-scale score=8` to map the score's scale
instead (healthy → 100%, worst possible → 200%), which also marks it as turned. This mapping
is a modelling choice about how much one score point is worth relative to one percent of body
weight; state it. The alternative is to keep the score out of RELSA and use it as an
independent endpoint criterion.

**4. Which variables are measured throughout.** Because the score averages over whichever
variables are available, a variable that appears or disappears mid-trajectory moves the score
by itself. In the published sepsis data, adding body weight — recorded only on the day of
euthanasia — drops that animal's endpoint score from 0.93 to 0.83 for no biological reason.
`relsa_scores()` warns when composition changes; score the variables present throughout.

## Workflow

### Step 1 — compute RELSA scores

```bash
python scripts/relsa_score.py assets/example_cohort.csv \
    --variables weight,temp,score,il6 \
    --normalize weight,temp,il6 \
    --turned il6 \
    --score-scale score=8 \
    --baseline-time -1 \
    --reference-group condition=endpoint \
    --save-reference reference.json \
    --out relsa_scores.csv
```

The reference model is echoed so the scale is auditable:

```
reference model: assets/example_cohort.csv [condition=endpoint]
  animals=2  rows=18  baseline_time=-1.0
  variable      turned   max reached   max delta
  weight            no         82.40       17.60
  temp              no         92.79        7.21
  score            yes        187.50       87.50
  il6              yes        797.72      697.72
```

`relsa_scores.csv` holds each variable's weight alongside the score, which is what makes a
score explainable — here M01 deteriorating to its endpoint, M03 peaking on day 3 and
recovering:

```
 id  time  weight  temp  score  il6  n_vars  relsa
M01     1    0.46  0.49   0.57 0.52       4   0.51
M01     3    0.84  0.76   1.00 0.89       4   0.88
M01     5    1.00  1.00   1.00 1.00       4   1.00
M03     3    0.56  0.44   0.57 0.54       4   0.53
M03     5    0.35  0.26   0.43 0.32       4   0.35
M03     7    0.12  0.06   0.14 0.11       4   0.11
```

A weight of 1.00 means that variable hit the reference maximum; `n_vars` is how many
variables entered the score at that time point.

Same thing from Python, when you need the objects:

```python
import sys; sys.path.insert(0, "scripts")
from _common import read_relsa_table, score_to_percent
from relsa_score import prepare, build_reference, relsa_scores

frame = read_relsa_table("assets/example_cohort.csv")
frame["score"] = score_to_percent(frame["score"], max_score=8)   # 0-8 clinical score
VARS, TURNED = ["weight", "temp", "score", "il6"], ["score", "il6"]

prepared  = prepare(frame, normalize=["weight", "temp", "il6"], baseline_time=-1)
reference = build_reference(prepared[prepared.condition == "endpoint"],
                           variables=VARS, turned=TURNED, baseline_time=-1,
                           label="endpoint-reaching animals")
scores    = relsa_scores(prepared, reference)
```

### Step 2 — forecast the endpoint

Train on everything up to the time point *before* the endpoint, predict the score at the
endpoint, and score the prediction:

```bash
python scripts/forecast_relsa.py relsa_scores.csv \
    --animals M01,M02 --endpoints M01=5 --endpoints M02=6 \
    --group-col condition --plot-dir figs --endpoint-line 1.0
```

```
 id  time  predicted    lower    upper        model  actual
M01   5.0   0.932585 0.670443 1.194728 ARIMA(1,1,0)    1.00
M02   6.0   0.955696 0.748309 1.163084 ARIMA(1,1,0)    0.94

   group             id        model  n   rmse  picp  mpiw
endpoint            M01 ARIMA(1,1,0)  1 0.0674 100.0 0.524
endpoint            M02 ARIMA(1,1,0)  1 0.0157 100.0 0.415
endpoint -- endpoint --               2 0.0489 100.0 0.470
                OVERALL               2 0.0489 100.0 0.470
```

Report all three metrics together. **RMSE** is point accuracy, **PICP** the percentage of
actual values inside the interval, and **MPIW** the mean interval width in RELSA units — a
model can reach PICP = 100% by making the interval so wide it says nothing, which is exactly
what the paper's pancreatic cancer row (PICP 100%, MPIW 7.35, i.e. 735% of the RELSA range)
shows.

For live monitoring, forecast one step ahead at every time point instead:

```bash
python scripts/forecast_relsa.py relsa_scores.csv --mode rolling --animals M03
```

Two things to know before trusting a forecast:

- **Interpolation is on by default** (`--interpolate-step 0.1`), because one measurement per
  day is far too sparse for ARIMA. It buys usable model selection and narrower intervals at
  the cost of honest uncertainty. Set `--interpolate-step 0` when measurement frequency
  allows.
- **ARIMA cannot predict a cliff.** It assumes stationarity and linearity, so an abrupt
  collapse in the last hours before an endpoint will not be forecast from a smooth prior
  trajectory — the paper's own failure case. Act on the *upper* bound of the interval, and
  never let a low forecast override an animal that looks unwell.

### Step 3 — put the score in context with severity zones

```bash
python scripts/kde_thresholds.py relsa_scores.csv \
    --group treatment=treated --n-thresholds 2 --plot zones.png --json zones.json
```

```
KDE on 33 RELSA scores  (bandwidth = 0.1502)
  candidate thresholds (density minima): 0.703
  density modes: 0.264, 0.866
  normal    [0.000, 0.703)  n=25 (75.8%)
  danger    >= 0.703  n=8 (24.2%)
```

Thresholds are the *minima* of the score density — the sparse valleys between clusters of
scores. Include endpoint animals, survivors, and shams: the zones are meant to separate
those states, so all of them must be represented.

**Check the bandwidth before believing a threshold.** On the published sepsis data this
implementation finds minima at 0.355 and 0.655 (published: 0.337 and 0.643) — but a 10%
larger bandwidth removes both minima entirely. Run the sweep in
`references/thresholds-and-zones.md` and report the sweep, not a bare pair of numbers. An
empty threshold list is a legitimate answer: the scores form one cluster and there is no
data-driven place to cut.

## Boundaries: state these when you report

- **RELSA is an aid to severity assessment, not a decisive parameter.** An animal with a low
  RELSA score that shows other signs of distress must still be handled accordingly. Neither
  procedure is a validated predictor of death.
- **KDE zones are not regulatory severity gradings.** EU Directive 2010/63/EU's categories
  (non-recovery, mild, moderate, severe) are assigned prospectively by a different process.
  The paper is explicit that its thresholds "should not be confused with regulatory severity
  gradings" and are not directly translatable to them.
- **Scores are not comparable across reference sets or models.** RELSA is relative by
  construction, and clinical scoring is not harmonized between laboratories. Always report
  the reference set with the score.
- **The published evidence is a proof of concept**: 13 animals across seven models, five of
  those rows resting on one or two animals. The overall RMSE of 0.069 and PICP of 96% come
  from 13 endpoint predictions.
- **An underestimated score is the dangerous error**, because it discourages attention and can
  delay a euthanasia decision, whereas an overestimate merely prompts extra care.

## Reporting checklist

A severity analysis is reproducible only if all of this is stated:

1. Outcome measures, their units, and their **directionality** (which were turned, and why).
2. The **baseline** time point or window, and which variables were normalized.
3. Any **score mapping** applied to ordinal variables, with its scale.
4. The **reference set**: which animals, which group, how many, and why they are assumed to
   carry the greatest burden.
5. Humane endpoint criteria actually applied in the study, separately from the RELSA score.
6. For forecasts: interpolation step, the selected ARIMA order per animal, and RMSE, PICP,
   *and* MPIW.
7. For thresholds: the bandwidth, the number of scores, and a bandwidth sensitivity sweep.
8. Software versions, and the statement that thresholds are model-specific and not regulatory
   gradings.

## Common pitfalls

1. **Wrong directionality** — a rising variable not listed in `--turned` contributes exactly
   zero, silently, and no warning is possible unless it never once falls. Check the reference
   model table yourself: `max reached` should be below 100 for a falling variable and above 100
   for a turned one, and `max delta` should be a plausible size for that measure.
2. **Normalizing a percentage twice** — `bwc [%]` and mapped scores are already on the percent
   scale; passing them to `--normalize` flattens them.
3. **A zero baseline** — a clinical score of 0 makes the ratio undefined; the variable becomes
   all-NaN with a warning. Use `--score-scale`.
4. **A reference set that does not express the burden** — a variable that never deviates in it
   raises an error rather than dividing by zero, and one that barely deviates inflates every
   score.
5. **Changing variable composition along a trajectory** — see decision 4 above.
6. **Reading MPIW as a good thing** — a wide interval raises PICP while destroying the
   forecast's usefulness.
7. **Reporting a KDE threshold without its bandwidth** — thresholds can vanish under a 10%
   bandwidth change.
8. **Treating the forecast as permission to wait** — the model cannot see abrupt
   deterioration, and the humane endpoint criteria of the protocol always take precedence.
9. **Comparing RELSA scores between models** — only valid within one reference frame.

## Resources

### Scripts

- `scripts/relsa_score.py` — the RELSA procedure: `prepare()`, `build_reference()`,
  `relsa_scores()`, `relsa_weights()`, and a `ReferenceModel` that serialises to JSON.
  Reproduces the R package's published worked example to two decimals.
- `scripts/forecast_relsa.py` — the foRcast tool: `auto_arima()` (Hyndman–Khandakar stepwise
  AICc selection), `forecast_animal()`, `predict_endpoint()`, `rolling_forecast()`,
  `forecast_indirect()`, `summarize()`, and Figure-1-style plots.
- `scripts/kde_thresholds.py` — severity zones: `bw_nrd0()` (R's bandwidth), `density_curve()`,
  `find_thresholds()`, zone assignment, and Figure-3-style density plots.
- `scripts/_common.py` — RELSA-format I/O, validation, `score_to_percent()`,
  `percent_of_baseline()`, and `forecast_metrics()` (RMSE/PICP/MPIW).

### References

- `references/relsa-method.md` — the four steps in full, the score/zero-baseline problem, the
  variable-composition trap, parity notes against the R package, and the outcome measures and
  endpoint criteria of all seven published models.
- `references/forecasting.md` — ARIMA selection, why interpolation is a distortion, direct vs
  indirect prediction, the metrics, the published Table 1, and what this port reproduces.
- `references/thresholds-and-zones.md` — KDE method, published thresholds, the bandwidth
  sensitivity sweep, the regulatory boundary, and alternatives when KDE gives nothing.

### Assets

- `assets/example_cohort.csv` — synthetic 6-mouse cohort with temperature, body weight, a
  clinical score, and a biomarker; illustrative only, not real data.

### Related skills

- **experimental-design**, **statistical-power** — designing the study and sizing the groups.
- **statsmodels**, **timesfm-forecasting** — general time-series modelling.
- **statistical-analysis**, **scientific-visualization** — group comparisons and figures.

### Key references

- Talbot, S. R. et al. (2022). RELSA — a multidimensional procedure for the comparative
  assessment of well-being and the quantitative determination of severity in experimental
  procedures. *Front. Vet. Sci.* 9:937711. R package: <https://github.com/mytalbot/RELSA>
- Lutscher, S. et al. (2026). Refining humane endpoint detection by time-series forecasting
  and threshold definition using a multivariate severity score. *Front. Physiol.* 17:1869563.
- Hyndman, R. J. & Khandakar, Y. (2008). Automatic time series forecasting: the forecast
  package for R. *J. Stat. Softw.* 27, 1–22.
- EU Commission (2010). Directive 2010/63/EU on the protection of animals used for scientific
  purposes.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/relsa-severity-assessment/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/forecasting.md`

# foRcast: ARIMA forecasting of RELSA trajectories

`scripts/forecast_relsa.py` ports the foRcast tool of Lutscher et al. (2026),
*Front. Physiol.* 17:1869563 — an ARIMA model fitted per animal to its own RELSA trajectory,
forecasting the score at the next time point (or at the humane endpoint) with a 95%
prediction interval.

The purpose is **triage, not automation**: identify the individuals at risk of reaching a
humane endpoint so handling personnel give them attention, while avoiding euthanising animals
that would have recovered. It is a proof of concept on 13 animals across seven models, not a
validated clinical tool.

## Why ARIMA

ARIMA(p, d, q) combines an autoregressive part (p lags of the series), differencing (d, to
remove trend and reach stationarity), and a moving-average part (q lags of the forecast
errors). It needs nothing but the animal's own history, which suits single-animal severity
assessment where each individual is its own control.

Model selection follows Hyndman & Khandakar (2008), i.e. `forecast::auto.arima`:

1. Choose `d` by successive KPSS tests (null = stationary; difference while it is rejected).
2. Fit four seed models — (2,d,2), (0,d,0), (1,d,0), (0,d,1) — with and without a
   constant/drift term.
3. Hill-climb from the best of those over neighbouring `(p, q)` and the drift term until AICc
   stops improving.

`auto_arima(..., stepwise=False)` searches the full `p × q` grid instead. Both are bounded by
`max_p`, `max_q`, `max_d`; the paper notes that the globally best model could lie outside that
range, which is a limitation of the approach rather than of one implementation.

## Interpolation: the necessary distortion

Animal experiments typically produce **one measurement per animal per day**. ARIMA is
conventionally said to want ~50 observations (Box et al., 2016), a number recently challenged
(Hassouna & Al-Sahili, 2020) but still far above what a 7-day study yields. The paper's
workaround is to interpolate linearly between observed values at 0.1-day increments and fit
the model to that denser series, and it is explicit that this is an alteration of the method,
not a free improvement:

- It **raises autocorrelation and partial autocorrelation**, which is what lets automatic
  order selection work at all on such short series.
- It **narrows the prediction interval**, improving coverage (PICP) at the cost of honestly
  representing uncertainty. The paper identifies interpolation as necessary "to minimize
  errors while maximizing prediction interval coverage with narrower boundaries".
- It adds no information. Interpolated points are a smoothness assumption, and a trajectory
  that actually moved non-linearly between measurements is misrepresented.

`interpolate_step=None` / `--interpolate-step 0` fits the observed series directly. Prefer it
whenever measurement frequency allows — with automated home-cage or telemetry monitoring the
interpolation step becomes unnecessary, which is the paper's own outlook.

## Forecast directly, not variable-by-variable

Two routes to a predicted RELSA score:

- **Direct** — forecast the RELSA series itself. `forecast_animal()`, `predict_endpoint()`.
- **Indirect** — forecast each outcome measure, then compute RELSA from the forecasts.
  `forecast_indirect()`.

The paper compared them in the sepsis model and direct won clearly: median deviation from the
actual score −0.002 (direct) versus −0.240 (indirect), a large effect
(d = 1.42, 95% CI [1.03, 1.81]). The reason is error propagation — each variable's forecast
error accumulates through the score, whereas the direct forecast carries only its own error.

Use direct. `forecast_indirect()` exists to reproduce the comparison and to inspect which
variable is driving a forecast.

## Metrics

Reported together, because each hides a failure the others catch
(`_common.forecast_metrics`):

| Metric | Meaning | Failure mode it exposes |
| --- | --- | --- |
| **RMSE** | root mean square deviation of predictions from actual RELSA scores | point-forecast accuracy |
| **PICP** | % of actual values falling inside the prediction interval | interval calibration |
| **MPIW** | mean prediction interval width, in RELSA units | a model that buys 100% PICP by making the interval useless |

MPIW is read against the RELSA scale, which normally spans about 0–1: the paper's overall
MPIW of 1.69 means the average interval covered 169% of the RELSA range, and the pancreatic
cancer model's 7.35 means 735% — a technically perfect PICP with almost no information in it.
Always report MPIW next to PICP.

## Published performance (Table 1)

Predicting the RELSA score at the (pre-)humane endpoint from all measurements up to the time
point immediately before it:

| Model / intervention | Animals | RMSE | PICP [%] | MPIW |
| --- | --- | --- | --- | --- |
| Sepsis | 2 | 0.009 | 100 | 0.30 |
| 1.5% DSS + restraint stress | 2 | 0.007 | 100 | 0.66 |
| 1% DSS + blood sampling | 4 | 0.046 | 75 | 0.53 |
| 1.5% DSS + blood sampling | 2 | 0.065 | 100 | 0.84 |
| 1.5% DSS | 1 | 0.095 | 100 | 1.64 |
| Pancreatic cancer | 1 | 0.177 | 100 | 7.35 |
| Neurosurgery | 1 | 0.082 | 100 | 0.54 |
| **Overall** | **13** | **0.069** | **96** | **1.69** |

Five of the seven rows rest on one or two animals. The overall PICP of 96% comes from 13
endpoint predictions.

## What this port reproduces

Using the public sepsis data (`tm_sepsis.txt`, 7 mice) with the paper's four telemetry
variables, no turned variables, and the CLP animals as reference set:

- Mouse ID_801 (the paper's Figure 1A): predicted RELSA 0.94 at the endpoint hour against an
  actual 0.93, RMSE 0.010, actual value inside the 95% interval. The published sepsis row is
  RMSE 0.009 over two animals.
- PICP 100% for both endpoint animals, matching the published row.
- MPIW 0.42–0.46 against a published 0.30 — this port's intervals are wider. The exact width
  depends on the interpolation step, the fitted variance, and the state-space implementation
  (statsmodels SARIMAX versus R's `arima`), so treat MPIW comparisons across
  implementations as approximate.

The paper's exact reference set and baseline window per model are in its Supplementary Table
S2, which is not bundled here; small differences in those choices shift every score slightly.

## Limits that matter more than the metrics

- **ARIMA cannot predict a cliff.** The model assumes stationarity and linearity. An abrupt
  collapse in the last hours before an endpoint is not forecastable from a smooth prior
  trajectory — this is the paper's own failure case (Figure 1C, the DSS blood-sampling mouse
  whose pre-endpoint score rose sharply and fell outside the 95% bounds). For sudden change,
  the paper points to Bayesian online changepoint detection (Adams & MacKay, 2007) or
  Markov switching models (Hamilton, 2020) as alternatives.
- **An underestimated score is the dangerous error.** An overestimate merely prompts extra
  attention; an underestimate discourages personnel from giving an animal the attention it
  needs and can delay a euthanasia decision. Asymmetric consequences deserve asymmetric
  handling: act on the *upper* bound of the interval.
- **RELSA is a severity-assessment aid, not a decision rule.** An animal with a low RELSA
  score that shows other signs of distress must still be handled accordingly. The paper is
  explicit that RELSA is "intended as an aid to severity assessment rather than a decisive
  parameter", and the RELSA package's own documentation states it is not a predictor of death.
- **Two prior measurements are not enough.** The paper's largest direct-prediction errors
  (Δ = 0.76 and 0.74) came from forecasts made at the earliest possible time point with only
  two prior observations. `forecast_animal()` records a warning below four observed points.
- **Parameter volatility hurts.** Activity forecast worst of the sepsis variables, being both
  intrinsically volatile and measured at low frequency. Including a noisy variable in the
  multivariate RELSA score mitigates its noise — one argument for the composite over
  single-parameter forecasting.

## Key references

- Hyndman, R. J. & Khandakar, Y. (2008). Automatic time series forecasting: the forecast
  package for R. *J. Stat. Softw.* 27, 1–22.
- Hyndman, R. J. & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd ed.
- Khosravi, A. et al. (2011). Comprehensive review of neural network-based prediction
  intervals. *IEEE Trans. Neural Netw.* 22, 1341. (PICP/MPIW)
- Pang, J. et al. (2018). Optimize the coverage probability of prediction interval for anomaly
  detection of sensor-based monitoring series. *Sensors* 18, 967.
- Petrică, A. et al. (2016). Limitation of ARIMA models in financial and monetary economics.
  *Theor. Appl. Econ.* 23, 19–42.

### `references/relsa-method.md`

# The RELSA score: algorithm, decisions, and parity with the R package

RELSA (RELative Severity Assessment) turns several welfare outcome measures into one
interpretable number per animal per time point. It was introduced in Talbot et al. (2022),
*Front. Vet. Sci.* 9:937711, and implemented in the R package
[`mytalbot/RELSA`](https://github.com/mytalbot/RELSA) (GPL-3). `scripts/relsa_score.py` is a
Python port of that implementation.

## The four steps

### 1. Directionality

Every variable must be declared as falling or rising under worsening welfare. The default
assumption is that a *decrease* means a worse outcome (body weight, activity, burrowing,
wheel running, food intake). Variables that *increase* are **turned**: clinical scores,
inflammatory biomarkers, fever, tachycardia.

Directionality is model-specific and getting it wrong silently zeroes a variable's
contribution, because deviations in the "wrong" direction are floored at 0. Body temperature
is the classic trap: it falls in CLP sepsis and endotoxaemia (hypothermia predicts death) and
rises in fever models.

`build_reference()` warns when a variable's *only* observed deviation runs against its declared
direction, and rejects one that never deviates at all. It cannot do better than that: in the
published sepsis data activity swings 530% above baseline and 100% below, so "which direction
is worse" is not recoverable from the data and has to come from the biology of the model.

### 2. Normalization to the individual baseline

Each variable is divided by that animal's own baseline value and expressed as a percentage,
so every trajectory starts at 100%:

```
x_norm(t) = 100 * x(t) / x(baseline)
```

Using each animal's own baseline is what makes RELSA robust to between-animal variation in
absolute values. The baseline may be one time point (the RELSA convention codes it as
`day = -1`) or the mean of a baseline window — pass several times to `--baseline-time`.

Two variable types must **not** be normalized again:

- Variables already expressed as percent change from baseline, such as body weight change
  (`bwc [%]`) in the published datasets.
- Ordinal severity scores whose healthy baseline is 0. `0/0` is undefined, so ratio
  normalization cannot represent them at all. Use `score_to_percent()` /
  `--score-scale COL=MAX`, which maps the score's *scale* instead of its ratio: the healthy
  score becomes 100, the worst possible score becomes 200, and one score point is worth
  `100 / (max - baseline)` percent. The variable is then a turned variable like any other.

  This mapping is this skill's convention, not something the paper specifies. It is a
  choice about how much a score point is worth relative to a percent of body weight, and it
  should be stated in the methods. The defensible alternative is to keep the score out of
  RELSA entirely and use it as an independent endpoint criterion, which is what the DSS
  blood-sampling model in the paper does (its clinical score of 5 is an endpoint trigger,
  while RELSA is computed from `bwc` and wheel running).

### 3. The reference set

The reference set is the cohort assumed to carry the greatest burden in the model, and it
fixes the meaning of the scale. For each variable, RELSA records the most extreme normalized
value reached anywhere in that cohort:

```
maxsev_i  = min over reference set (or max, for turned variables)
maxdelta_i = |100 - maxsev_i|
```

The paper uses "the animal in the treatment group suspected to experience the greatest burden
under the respective model" — e.g. the highest DSS dose with phlebotomy in the DSS blood
sampling dataset.

This is the single most consequential choice in the whole procedure. RELSA is *relative*:
change the reference set and every score changes. A reference cohort that is too mild pushes
scores above 1; one that is too severe compresses everything toward 0. A score is
meaningless without the reference set it came from, which is why `ReferenceModel` carries a
`label` and `--save-reference` writes it to JSON for reuse on later cohorts.

A variable that never deviates in the reference set has `maxdelta = 0`, would divide by zero,
and is rejected with an error rather than silently dropped.

### 4. Weights and the score

```
delta_i(t) = 100 - x_norm,i(t)        (turned: x_norm,i(t) - 100), floored at 0
RW_i(t)    = delta_i(t) / maxdelta_i
RELSA(t)   = sqrt( (1/n) * sum_i RW_i(t)^2 )     over the n variables measured at t
```

The root-mean-square, rather than the arithmetic mean, is deliberate: severity is signalled
by *extremes*, so squaring gives a large deviation in one variable more influence than the
mean would. A single variable at the reference maximum with three others at baseline gives
RELSA = 0.5, not 0.25.

Missing values are dropped from the mean, never imputed and never treated as 0 — treating a
missing measurement as "no deviation" would bias every score downward. This is why a score
is defined whenever at least one variable was measured.

**Interpretation.** RELSA = 0 is baseline; 0.73 means the animal reached 73% of the reference
set's maximum deviation; above 1 means it exceeded the reference set. The score is
dimensionless and comparable *within* a reference frame, not across reference sets or models.

## A trap the published data demonstrates

Because the score averages over whichever variables were measured, **a variable that appears
or disappears mid-trajectory moves the score by itself.** In the published sepsis dataset,
body weight is recorded only on the day of euthanasia. Include `bwc` in that model and mouse
ID_801's endpoint score falls from 0.93 to 0.83 — not because the animal improved, but
because a variable with a low weight (0.16) joined the mean at exactly that time point. The
paper's sepsis model uses only the four telemetry parameters, which are present throughout.

Score the variables measured throughout the trajectory; keep the intermittent ones as
separate endpoint criteria. `relsa_scores()` warns when the composition changes.

## Parity with the R package

`relsa_score.py` reproduces the R package's own published worked example — the `surgery`
dataset, animal `Ca_001`, variables `bwc, burON, hr, hrv, temp, act`, turned `hr, temp` — to
the two decimals the package prints: every normalized value, every weight, and the RELSA
scores 0.00, 0.73, 0.55, 0.44, 0.44, 0.41 for days -1 to 4, including the `NA` weight where
`burON` is missing. The test suite pins this.

Details worth knowing if you compare against R directly:

- **Rounding is part of the algorithm.** R rounds the deltas and the weights to two decimals
  *before* the root-mean-square, so the port does too. `round_digits=None` /
  `--full-precision` skips it, which changes scores in the third decimal — and, because KDE
  minima are sensitive to the granularity of the score distribution, can change the number of
  thresholds found. Keep the default when reproducing published work.
- **`relsa()`'s `wf` column is not the score.** The R function returns both a mean weight
  factor (`wf`) and the root-mean-square (`rms`); the RELSA score is `rms`. In the released
  package `wf` divides the weight sum by the count of *missing* variables rather than the
  count of present ones (the vignette has the intended form), and because `wf` is used to
  mask `rms`, a complete row sitting exactly at baseline is returned as `NA` instead of 0 by
  that code path. The rendered vignette prints 0.00 for the baseline day, so the port
  returns 0.0, matching the published output and the formula.
- Column order does not matter here. The R functions address `set[, 4:ncol]` positionally;
  this port uses named `id` / `time` columns.

## Outcome measures and directionality in the published models

From Lutscher et al. (2026) and the studies it re-analyses. Use it as a template for
declaring your own model, not as a set of defaults to copy.

| Model / intervention | Variables in RELSA | Turned | Humane endpoint criterion |
| --- | --- | --- | --- |
| CLP sepsis (telemetry) | `hr`, `hrv`, `temp`, `act` | none | >25% temperature loss over two consecutive monitoring intervals |
| DSS colitis + restraint stress | `hr`, `hrv`, `temp`, `act`, `bwc` | `hr`, `temp` | 20% body weight loss |
| DSS colitis + facial vein blood sampling | `bwc`, `vwr` (voluntary wheel running) | none | 20% body weight loss or clinical score 5 |
| Pancreatic cancer (6606PDA) | `bwc`, `vwr` | none | 20% body weight loss |
| Neurosurgery (intracranial electrode) | `bwc`, nesting score, Neuro Score (modified Irwin) | nesting, neuro | total clinical score of 7 |

Heart rate, heart rate variability and temperature were averaged per interval; activity was
summed. Clinical scoring differed between laboratories and models, so the paper states
plainly that clinical scores are **not directly comparable** across those studies — one of
its central caveats about a generalized RELSA scale.

## Data for testing against published work

- Sepsis and 1.5% DSS + restraint stress: <https://github.com/mytalbot/RELSA/tree/master/raw_data>
- DSS with repeated facial vein blood sampling: <https://doi.org/10.1371/journal.pbio.2006159.s002>
- Pancreatic cancer: <https://doi.org/10.1371/journal.pone.0261662>
- Neurosurgery: <https://doi.org/10.6084/m9.figshare.26030569>

## Key references

- Talbot, S. R. et al. (2022). RELSA — a multidimensional procedure for the comparative
  assessment of well-being and the quantitative determination of severity in experimental
  procedures. *Front. Vet. Sci.* 9:937711.
- Lutscher, S. et al. (2026). Refining humane endpoint detection by time-series forecasting
  and threshold definition using a multivariate severity score. *Front. Physiol.*
  17:1869563. doi:10.3389/fphys.2026.1869563
- Talbot, S. R. et al. (2020). Defining body-weight reduction as a humane endpoint: a
  critical appraisal. *Lab. Anim.* 54, 99–110.
- Russell, W. M. S. & Burch, R. L. (1959). *The Principles of Humane Experimental Technique.*

### `references/thresholds-and-zones.md`

# Severity zones on the RELSA scale via kernel density estimation

A RELSA score of 0.55 is only interpretable once you know where the cut-points lie. Lutscher
et al. (2026) derive candidate cut-points from the data itself: estimate the probability
density of all RELSA scores observed in a model, and take the **minima** of that density —
the sparsely populated valleys between clusters of scores. `scripts/kde_thresholds.py`
implements this.

## Method

For each observation a Gaussian kernel of bandwidth `h` is placed; averaging them yields the
density estimate, and interior local minima mark low-occurrence regions that can serve as
thresholds (Korneev et al., 2022; Gilles & Heal, 2014).

Two minima split the scale into three zones:

| Zone | Meaning |
| --- | --- |
| normal | below the lower minimum — within the range the model's animals mostly occupy |
| attention | between the minima — flag the animal for closer monitoring |
| danger | above the upper minimum — approaching or at the individual endpoint |

The implementation reproduces R's `stats::density` defaults, because that is what the paper
used: Gaussian kernel, Silverman's `bw.nrd0` bandwidth
(`0.9 * min(sd, IQR/1.349) * n^(-1/5)`), and a 512-point grid extended three bandwidths past
the data range. Note that scipy's own `bw_method='silverman'` is a **different formula** and
would shift every threshold, which is why `bw_nrd0()` is implemented explicitly.

Include all animals in the model — those that reached the endpoint *and* the survivors and
sham controls. The zones are meant to separate the trajectories of animals in different
states, which requires all of those states to be represented.

## Published thresholds

| Model | Thresholds | Notes |
| --- | --- | --- |
| Sepsis (CLP) | 0.337 and 0.643 | 7 mice, 239 scores; the paper's Figure 3 |
| DSS + restraint stress | 0.250 | single threshold |
| DSS + blood sampling | 0.649 | single threshold |

The pancreatic cancer and neurosurgery models were excluded from this analysis: with one
animal each, the score distribution is too sparse for a meaningful density.

The abstract of the paper gives the sepsis upper threshold as 0.647 while its Results and
Figure 3 give 0.643 — a reminder of how little separates two runs of this procedure.

## What this port reproduces, and how fragile it is

On the public sepsis data with the paper's four telemetry variables and the CLP animals as
reference set, excluding the baseline time point (where RELSA = 0 by construction):

- **239 scores** — exactly the paper's stated 239 data points from 7 mice.
- Thresholds **0.355 and 0.655** against the published 0.337 and 0.643. Including `bwc` in
  the score gives 0.363 and 0.644.
- At 0.9 × `bw.nrd0` the minima move to **0.335 and 0.633**, essentially the published pair.

That last line is the important one. A bandwidth sensitivity sweep on the same 239 scores:

| Bandwidth (× `bw.nrd0` = 0.0732) | Minima found |
| --- | --- |
| 0.70 | 0.310, 0.630 |
| 0.80 | 0.322, 0.628 |
| 0.90 | 0.335, 0.633 |
| 1.00 | 0.355, 0.655 |
| 1.10 | **none — the density is unimodal** |
| ≥ 1.25 | none |

A 10% change in bandwidth destroys both thresholds. The lower threshold sits in a broad,
shallow valley and moves by 0.045 across a plausible bandwidth range; the upper one is
comparatively stable. Two further sensitivities: dropping one variable from the score can
change the number of minima, and turning off the algorithm's 2-decimal rounding changed this
dataset from two minima to one.

**Therefore:** never report KDE thresholds as a bare pair of numbers. Report the bandwidth,
the number of scores, the variables, the reference set, and a sensitivity sweep. Prefer the
sweep to the point estimate — if a threshold survives only at one bandwidth, you have found a
property of the smoother, not of the animals.

## These are not regulatory severity gradings

EU Directive 2010/63/EU requires prospective assignment of procedures to four categories:
non-recovery, mild, moderate, and severe. **KDE zones on the RELSA scale are not those
categories,** and the paper says so twice: the thresholds "should not be confused with
regulatory severity gradings" and are "neither generalizable nor directly translatable to
severity categories under EU Directive 2010/63/EU".

They are also not comparable between models. Because RELSA is relative to a reference set and
because clinical scoring is not harmonized across laboratories, a threshold of 0.337 in one
model means nothing in another. The paper's own observation that the sepsis (0.337/0.643) and
DSS (0.250, 0.649) thresholds are "fairly close" is offered as a hint about where common
thresholds might eventually lie, not as evidence that they transfer.

What a unified scale would require, per the paper's outlook: the same parameters measured with
harmonized technical and methodological approaches across models — realistically, automated
home-cage monitoring at high frequency.

## Practical use

```bash
# candidate zones for one model, with a figure and a sensitivity check
python scripts/kde_thresholds.py relsa_scores.csv --n-thresholds 2 \
    --plot zones.png --json zones.json --label-out zoned.csv

# does the answer survive a different bandwidth?
for f in 0.8 0.9 1.0 1.1 1.2; do
  python - "$f" <<'PY'
import sys, pandas as pd
sys.path.insert(0, "scripts")
from kde_thresholds import find_thresholds, bw_nrd0
v = pd.read_csv("relsa_scores.csv")["relsa"].dropna()
bw = bw_nrd0(v.to_numpy()) * float(sys.argv[1])
print(sys.argv[1], [round(t, 3) for t in find_thresholds(v, bandwidth=bw).thresholds])
PY
done
```

An empty threshold list is a real answer: this cohort's scores form one cluster, and there is
no data-driven place to cut. Do not lower the bandwidth until minima appear.

### The thin-zone filter

A finite sample's density estimate wiggles in its tails, and a wiggle produces a local minimum
that separates one stray score from the rest. On 300 draws from a single normal distribution
this implementation finds such a minimum, and it isolates exactly **one** observation — a
property of the smoother, not a severity zone. `min_zone_fraction` (default 0.02) therefore
requires every zone to hold at least 2% of the scores, dropping the shallowest threshold
bounding any zone that does not, until all of them do.

This does not touch the published sepsis result: its three zones hold 68.2%, 22.2%, and 9.6%
of the 239 scores. Set `--min-zone-fraction 0` to see the raw minima, and expect tail
artefacts among them.

Two alternatives when KDE gives nothing usable:

- **k-means levels.** The original RELSA package derives `k+1` levels by k-means clustering of
  the reference set's scores (`relsa_levels`, default `k = 4`). Also data-driven, also
  reference-set-specific, and it always returns levels — including when there is no real
  structure to find.
- **The model's own endpoint criterion.** Compute the RELSA score at the time the humane
  endpoint was actually reached in previous animals, and use that value as the line to watch.
  This is directly interpretable and needs no smoother, which is what the "individual
  endpoint" line in the paper's Figure 1 shows.

## Key references

- Rosenblatt, M. (1956). Remarks on some nonparametric estimates of a density function.
  *Ann. Math. Stat.* 27, 832–837.
- Parzen, E. (1962). On estimation of a probability density function and mode.
  *Ann. Math. Stat.* 33, 1065–1076.
- Węglarczyk, S. (2018). Kernel density estimation and its application. *ITM Web Conf.* 23, 37.
- Korneev, A. et al. (2022). Multiclass histogram-based thresholding using kernel density
  estimation and scale-space representations. arXiv:2202.04785.
- EU Commission (2010). Directive 2010/63/EU. *Official Journal of the European Union* 53,
  16–25.

### `scripts/_common.py`

```python
"""Shared I/O, validation, and variable-preparation helpers for the RELSA workflow.

The RELSA long format is one row per animal per time point:

    id   treatment   condition   time   var_1 ... var_n

``id`` and ``time`` are required; ``treatment`` and ``condition`` are optional
grouping labels carried through untouched. Time may be days, hours, or minutes
as long as it increases monotonically per animal. The RELSA convention codes the
baseline time point as -1, but any value works when it is named explicitly.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

ID_COL = "id"
TIME_COL = "time"
META_COLS = ("treatment", "condition")

# Time-column aliases accepted on input; all are renamed to ``time`` internally.
TIME_ALIASES = ("time", "day", "days", "hour", "hours", "timepoint", "t")


class RelsaDataError(ValueError):
    """Raised when input data cannot support a RELSA calculation."""


# --------------------------------------------------------------------------- #
# loading
# --------------------------------------------------------------------------- #
def read_relsa_table(
    path: str | Path,
    sep: str | None = None,
    id_col: str = ID_COL,
    time_col: str | None = None,
) -> pd.DataFrame:
    """Read a RELSA-format table from CSV/TSV and return it with canonical names.

    ``sep=None`` sniffs the delimiter. A leading unnamed index column (as written
    by R's ``write.table``, and present in the published RELSA raw data) is
    dropped. The time column is detected from ``TIME_ALIASES`` unless named.
    """
    path = Path(path)
    if sep is None:
        sep = "\t" if path.suffix.lower() in {".txt", ".tsv", ".tab"} else ","
    frame = pd.read_csv(path, sep=sep)

    unnamed = [c for c in frame.columns if str(c).startswith("Unnamed:")]
    frame = frame.drop(columns=unnamed)

    return canonicalize(frame, id_col=id_col, time_col=time_col)


def canonicalize(
    frame: pd.DataFrame,
    id_col: str = ID_COL,
    time_col: str | None = None,
) -> pd.DataFrame:
    """Rename the id/time columns to ``id``/``time`` and sort by animal and time."""
    frame = frame.copy()

    if id_col != ID_COL:
        if id_col not in frame.columns:
            raise RelsaDataError(f"id column {id_col!r} not in {list(frame.columns)}")
        frame = frame.rename(columns={id_col: ID_COL})
    if ID_COL not in frame.columns:
        raise RelsaDataError(f"no {ID_COL!r} column in {list(frame.columns)}")

    if time_col is None:
        found = [c for c in frame.columns if str(c).lower() in TIME_ALIASES]
        if not found:
            raise RelsaDataError(
                "no time column found; expected one of "
                f"{TIME_ALIASES} or an explicit time_col"
            )
        time_col = found[0]
    elif time_col not in frame.columns:
        raise RelsaDataError(f"time column {time_col!r} not in {list(frame.columns)}")
    if time_col != TIME_COL:
        frame = frame.rename(columns={time_col: TIME_COL})

    frame[TIME_COL] = pd.to_numeric(frame[TIME_COL], errors="coerce")
    if frame[TIME_COL].isna().any():
        raise RelsaDataError("time column contains non-numeric values")

    return frame.sort_values([ID_COL, TIME_COL], kind="stable").reset_index(drop=True)


def variable_columns(frame: pd.DataFrame) -> list[str]:
    """Every numeric measurement column: not id, time, or a metadata label."""
    reserved = {ID_COL, TIME_COL, *META_COLS}
    return [c for c in frame.columns if c not in reserved]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def validate(frame: pd.DataFrame, variables: Sequence[str]) -> None:
    """Check the invariants RELSA depends on, raising or warning as appropriate.

    Duplicate (id, time) rows are fatal: normalization and forecasting both
    assume one measurement per animal per time point. Everything else is a
    warning, because RELSA is explicitly designed to tolerate missing data.
    """
    missing = [v for v in variables if v not in frame.columns]
    if missing:
        raise RelsaDataError(f"variables not in data: {missing}")

    dup = frame.duplicated([ID_COL, TIME_COL], keep=False)
    if dup.any():
        offenders = (
            frame.loc[dup, [ID_COL, TIME_COL]].astype(str).agg(" @ ".join, axis=1).unique()
        )
        raise RelsaDataError(
            "multiple rows share an (id, time) pair, so normalization would be "
            f"ambiguous: {list(offenders)[:5]}. Aggregate per time point first "
            "(the published models average hourly telemetry to one value per day)."
        )

    for var in variables:
        col = pd.to_numeric(frame[var], errors="coerce")
        if col.notna().sum() == 0:
            warnings.warn(f"variable {var!r} is entirely missing", stacklevel=2)

    per_animal = frame.groupby(ID_COL)[TIME_COL].size()
    if per_animal.nunique() > 1:
        warnings.warn(
            "animals have different numbers of time points; RELSA handles this, "
            "but check that gaps are genuinely missing data and not misaligned time axes",
            stacklevel=2,
        )


# --------------------------------------------------------------------------- #
# variable preparation
# --------------------------------------------------------------------------- #
def score_to_percent(
    values: Iterable[float],
    max_score: float,
    baseline_score: float = 0.0,
) -> np.ndarray:
    """Map an ordinal severity score onto the RELSA percent scale.

    RELSA normalizes by dividing each measurement by its own baseline, which is
    undefined for a clinical score whose healthy baseline is 0. This maps the
    score's *scale* instead of its ratio: ``baseline_score`` becomes 100 and
    ``max_score`` becomes 200, so the variable behaves like any other "turned"
    parameter (rises above 100 as the animal worsens) and one full score point
    is worth ``100 / |max_score - baseline_score|`` percent.

    ``max_score`` may lie *below* ``baseline_score`` for scales where a lower
    number is worse — a nesting score where a well-built nest scores 5 and no
    nest scores 0 is ``score_to_percent(nesting, max_score=0,
    baseline_score=5)``. Either way the mapped variable is "turned".

    Pass the resulting column straight to the RELSA calculation, list it in
    ``turned``, and leave it out of ``normalize`` — it is already normalized.
    """
    values = np.asarray(list(values), dtype=float)
    span = float(max_score) - float(baseline_score)
    if span == 0:
        raise RelsaDataError(
            f"max_score ({max_score}) must differ from baseline_score ({baseline_score})"
        )
    return 100.0 + 100.0 * (values - float(baseline_score)) / span


def percent_of_baseline(
    frame: pd.DataFrame,
    variables: Sequence[str],
    baseline_time: float | Sequence[float] | None = None,
) -> pd.DataFrame:
    """Express each variable as a percentage of that animal's own baseline.

    ``baseline_time`` selects the baseline: a single time value, several time
    values (averaged, i.e. a baseline window), or ``None`` for each animal's
    first time point. Animals whose baseline is missing or zero yield all-NaN
    for that variable, with a warning — a zero baseline makes the ratio
    undefined, which is what ``score_to_percent`` exists to avoid.
    """
    out = frame.copy()
    if baseline_time is None:
        window: list[float] | None = None
    elif np.isscalar(baseline_time):
        window = [float(baseline_time)]  # type: ignore[arg-type]
    else:
        window = [float(t) for t in baseline_time]  # type: ignore[union-attr]

    for var in variables:
        out[var] = pd.to_numeric(out[var], errors="coerce")

    problems: list[str] = []
    for animal, block in out.groupby(ID_COL, sort=False):
        if window is None:
            rows = block.index[:1]
        else:
            rows = block.index[block[TIME_COL].isin(window)]
            if len(rows) == 0:
                problems.append(f"{animal} (no baseline time point)")
                out.loc[block.index, list(variables)] = np.nan
                continue
        for var in variables:
            window_values = out.loc[rows, var].to_numpy(dtype=float)
            finite = window_values[np.isfinite(window_values)]
            base = float(finite.mean()) if finite.size else np.nan
            if not np.isfinite(base) or base == 0:
                problems.append(f"{animal}/{var} (baseline {base})")
                out.loc[block.index, var] = np.nan
                continue
            out.loc[block.index, var] = out.loc[block.index, var] / base * 100.0

    if problems:
        warnings.warn(
            "baseline missing or zero, variable set to NaN for: "
            + ", ".join(problems[:8])
            + ("..." if len(problems) > 8 else "")
            + ". For scores whose healthy baseline is 0, use score_to_percent().",
            stacklevel=2,
        )
    return out


def parse_list(value: str | None) -> list[str]:
    """Split a comma-separated CLI option into a clean list."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


# --------------------------------------------------------------------------- #
# metrics
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ForecastMetrics:
    """The three error metrics reported in Lutscher et al. (2026), Table 1."""

    n: int
    rmse: float
    picp: float
    mpiw: float

    def as_dict(self) -> dict[str, float]:
        return {"n": self.n, "rmse": self.rmse, "picp": self.picp, "mpiw": self.mpiw}


def forecast_metrics(
    actual: Iterable[float],
    predicted: Iterable[float],
    lower: Iterable[float] | None = None,
    upper: Iterable[float] | None = None,
) -> ForecastMetrics:
    """RMSE, prediction-interval coverage probability, and mean interval width.

    RMSE and PICP answer different questions and are reported together on
    purpose: a model can widen its intervals until PICP hits 100% without
    predicting anything, which is why MPIW (the mean width, in RELSA units)
    has to be read alongside the coverage.
    """
    a = np.asarray(list(actual), dtype=float)
    p = np.asarray(list(predicted), dtype=float)
    if a.shape != p.shape:
        raise ValueError(f"actual {a.shape} and predicted {p.shape} differ in length")

    ok = np.isfinite(a) & np.isfinite(p)
    rmse = float(np.sqrt(np.mean((a[ok] - p[ok]) ** 2))) if ok.any() else float("nan")

    picp = float("nan")
    mpiw = float("nan")
    if lower is not None and upper is not None:
        lo = np.asarray(list(lower), dtype=float)
        hi = np.asarray(list(upper), dtype=float)
        band = np.isfinite(lo) & np.isfinite(hi)
        if band.any():
            mpiw = float(np.mean(hi[band] - lo[band]))
        cov = band & np.isfinite(a)
        if cov.any():
            inside = (a[cov] >= lo[cov]) & (a[cov] <= hi[cov])
            picp = float(100.0 * np.mean(inside))

    return ForecastMetrics(n=int(ok.sum()), rmse=rmse, picp=picp, mpiw=mpiw)
```

### `scripts/forecast_relsa.py`

```python
#!/usr/bin/env python3
"""foRcast — ARIMA forecasting of RELSA severity trajectories.

Port of the foRcast tool of Lutscher et al. (2026), Front. Physiol. 17:1869563:
an ARIMA model fitted per animal to its RELSA trajectory, forecasting the score
at the next (or the humane-endpoint) time point with a 95% prediction interval,
scored by RMSE, PICP, and MPIW.

Three design choices carried over from the paper:

* **Interpolation.** Animal experiments usually yield one measurement per day,
  far short of the ~50 points classically wanted for ARIMA. The paper linearly
  interpolates between observations at 0.1-day increments to feed the model.
  This is a deliberate alteration: it raises autocorrelation and narrows the
  prediction interval, buying coverage at the cost of honest uncertainty. Turn
  it off with ``interpolate_step=None`` once continuous home-cage monitoring
  makes it unnecessary.
* **Direct beats indirect.** Forecasting the RELSA score itself (direct)
  outperformed forecasting each variable and then computing RELSA from the
  forecasts (indirect, median deviation -0.240, d = 1.42), because
  single-parameter errors accumulate through the score. ``direct=True`` is the
  default; the indirect path is provided for comparison.
* **ARIMA cannot see cliffs.** The model assumes stationarity and linearity, so
  an abrupt collapse in the last hours before an endpoint is not predictable
  from a smooth prior trajectory — the paper's own failure case (Figure 1C).
  Treat a forecast as a watch-list trigger, never as a licence to wait.
"""

from __future__ import annotations

import argparse
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    ID_COL,
    TIME_COL,
    ForecastMetrics,
    forecast_metrics,
    parse_list,
)

DEFAULT_STEP = 0.1
MIN_TRAIN_POINTS = 4


# --------------------------------------------------------------------------- #
# interpolation
# --------------------------------------------------------------------------- #
def interpolate_series(
    times: Iterable[float],
    values: Iterable[float],
    step: float = DEFAULT_STEP,
) -> tuple[np.ndarray, np.ndarray]:
    """Linearly interpolate a sparse trajectory onto a regular ``step`` grid.

    Leading and trailing missing values are dropped rather than extrapolated.
    Returns the grid times and interpolated values.
    """
    t = np.asarray(list(times), dtype=float)
    y = np.asarray(list(values), dtype=float)
    ok = np.isfinite(t) & np.isfinite(y)
    t, y = t[ok], y[ok]
    if t.size < 2:
        raise ValueError("need at least 2 observed points to interpolate")
    order = np.argsort(t)
    t, y = t[order], y[order]
    grid = np.arange(t[0], t[-1] + step / 2, step)
    return grid, np.interp(grid, t, y)


# --------------------------------------------------------------------------- #
# automatic ARIMA
# --------------------------------------------------------------------------- #
@dataclass
class ArimaFit:
    """A selected ARIMA model and the information criterion that chose it."""

    order: tuple[int, int, int]
    drift: bool
    aicc: float
    aic: float
    n_obs: int
    results: object = field(repr=False, default=None)

    def label(self) -> str:
        p, d, q = self.order
        return f"ARIMA({p},{d},{q})" + (" with drift" if self.drift else "")


def _select_d(y: np.ndarray, max_d: int) -> int:
    """Choose the differencing order by successive KPSS tests, as auto.arima does."""
    from statsmodels.tsa.stattools import kpss

    series = np.asarray(y, dtype=float)
    for d in range(max_d + 1):
        if series.size < 8 or np.allclose(series, series[0]):
            return d
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                p_value = kpss(series, regression="c", nlags="auto")[1]
        except Exception:
            return d
        if p_value > 0.05:  # KPSS null is stationarity -> stop differencing
            return d
        series = np.diff(series)
    return max_d


def _fit_one(
    y: np.ndarray, order: tuple[int, int, int], drift: bool
) -> ArimaFit | None:
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    k = sum(order[::2]) + (1 if drift else 0) + 1
    if y.size - order[1] <= k + 2:
        return None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = SARIMAX(
                y,
                order=order,
                trend="c" if drift else "n",
                enforce_stationarity=True,
                enforce_invertibility=True,
            )
            res = model.fit(disp=False)
    except Exception:
        return None
    aic = float(res.aic)
    if not np.isfinite(aic):
        return None
    n = int(res.nobs)
    penalty = 2 * k * (k + 1) / (n - k - 1) if n - k - 1 > 0 else np.inf
    return ArimaFit(order=order, drift=drift, aicc=aic + penalty, aic=aic,
                    n_obs=n, results=res)


def auto_arima(
    y: Iterable[float],
    max_p: int = 5,
    max_q: int = 5,
    max_d: int = 2,
    d: int | None = None,
    allow_drift: bool = True,
    stepwise: bool = True,
) -> ArimaFit:
    """Select an ARIMA model by minimising AICc (Hyndman–Khandakar stepwise).

    Mirrors ``forecast::auto.arima``: differencing order from KPSS tests, then
    four seed models — (2,d,2), (0,d,0), (1,d,0), (0,d,1) — followed by a
    hill-climb over neighbouring (p, q) and the drift term. ``stepwise=False``
    searches the full grid, which is slower and rarely changes the answer.

    The best model found is not guaranteed to be the globally best one: the
    search covers a bounded range of p, d, q, which the paper notes as a
    limitation of the approach rather than of one implementation.
    """
    series = np.asarray(list(y), dtype=float)
    series = series[np.isfinite(series)]
    if series.size < MIN_TRAIN_POINTS:
        raise ValueError(
            f"need at least {MIN_TRAIN_POINTS} finite points to fit ARIMA, got {series.size}"
        )

    order_d = _select_d(series, max_d) if d is None else int(d)
    drifts = (True, False) if allow_drift else (False,)

    tried: dict[tuple[tuple[int, int, int], bool], ArimaFit | None] = {}

    def attempt(order: tuple[int, int, int], drift: bool) -> ArimaFit | None:
        if order[0] > max_p or order[2] > max_q or min(order[0], order[2]) < 0:
            return None
        key = (order, drift)
        if key not in tried:
            tried[key] = _fit_one(series, order, drift)
        return tried[key]

    candidates: list[ArimaFit] = []
    if not stepwise:
        for p in range(max_p + 1):
            for q in range(max_q + 1):
                for drift in drifts:
                    fit = attempt((p, order_d, q), drift)
                    if fit:
                        candidates.append(fit)
    else:
        seeds = [(2, order_d, 2), (0, order_d, 0), (1, order_d, 0), (0, order_d, 1)]
        for seed in seeds:
            for drift in drifts:
                fit = attempt(seed, drift)
                if fit:
                    candidates.append(fit)
        if candidates:
            best = min(candidates, key=lambda f: f.aicc)
            improved = True
            while improved:
                improved = False
                p, dd, q = best.order
                neighbours = [
                    ((p + 1, dd, q), best.drift),
                    ((p - 1, dd, q), best.drift),
                    ((p, dd, q + 1), best.drift),
                    ((p, dd, q - 1), best.drift),
                    ((p + 1, dd, q + 1), best.drift),
                    ((p - 1, dd, q - 1), best.drift),
                    ((p, dd, q), not best.drift),
                ]
                for order, drift in neighbours:
                    if drift and not allow_drift:
                        continue
                    fit = attempt(order, drift)
                    if fit and fit.aicc < best.aicc - 1e-8:
                        best, improved = fit, True
                        break
            candidates.append(best)

    if not candidates:
        # Nothing converged (usually a near-constant or very short series):
        # fall back to a random walk, which always fits.
        fit = _fit_one(series, (0, min(1, max_d), 0), False)
        if fit is None:
            raise RuntimeError("no ARIMA model could be fitted to this series")
        return fit
    return min(candidates, key=lambda f: f.aicc)


# --------------------------------------------------------------------------- #
# forecasting one animal
# --------------------------------------------------------------------------- #
@dataclass
class Forecast:
    """A forecast of one animal's RELSA trajectory."""

    animal: str
    fit: ArimaFit
    times: np.ndarray
    predicted: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    actual: np.ndarray | None = None
    train_times: np.ndarray | None = None
    train_values: np.ndarray | None = None
    interpolated: bool = True
    alpha: float = 0.05
    warnings: list[str] = field(default_factory=list)

    def metrics(self) -> ForecastMetrics:
        if self.actual is None:
            raise ValueError("no actual values to score this forecast against")
        return forecast_metrics(self.actual, self.predicted, self.lower, self.upper)

    def to_frame(self) -> pd.DataFrame:
        data = {
            ID_COL: self.animal,
            TIME_COL: self.times,
            "predicted": self.predicted,
            "lower": self.lower,
            "upper": self.upper,
            "model": self.fit.label(),
        }
        if self.actual is not None:
            data["actual"] = self.actual
        return pd.DataFrame(data)


def forecast_animal(
    times: Iterable[float],
    values: Iterable[float],
    target_times: Iterable[float] | None = None,
    animal: str = "",
    interpolate_step: float | None = DEFAULT_STEP,
    alpha: float = 0.05,
    clip_at_zero: bool = True,
    **arima_kwargs,
) -> Forecast:
    """Fit ARIMA to one RELSA trajectory and forecast the requested time points.

    ``target_times`` defaults to one observation-spacing step beyond the last
    training point. With ``interpolate_step`` set, the model is fitted on the
    interpolated grid and the horizon is converted to grid steps, so targets
    must lie on (or near) that grid.

    ``clip_at_zero`` floors the forecast and its interval at 0, since RELSA is
    non-negative by construction; the raw Gaussian interval can dip below.
    """
    t = np.asarray(list(times), dtype=float)
    y = np.asarray(list(values), dtype=float)
    ok = np.isfinite(t) & np.isfinite(y)
    t, y = t[ok], y[ok]
    order = np.argsort(t)
    t, y = t[order], y[order]
    notes: list[str] = []

    if t.size < 2:
        raise ValueError(f"animal {animal!r}: fewer than 2 observed RELSA scores")

    spacing = float(np.median(np.diff(t))) if t.size > 1 else 1.0
    if target_times is None:
        targets = np.array([t[-1] + spacing], dtype=float)
    else:
        targets = np.asarray(list(target_times), dtype=float)
    if np.any(targets <= t[-1]):
        raise ValueError(
            f"animal {animal!r}: target times must be after the last training point "
            f"({t[-1]}); got {targets.tolist()}"
        )

    if interpolate_step:
        grid, series = interpolate_series(t, y, step=interpolate_step)
        step = interpolate_step
        origin = grid[-1]
        notes.append(
            f"fitted on {series.size} points interpolated at {interpolate_step} "
            f"time units from {t.size} observations; prediction intervals are "
            "narrower than the observation density alone would justify"
        )
    else:
        if not np.allclose(np.diff(t), spacing, rtol=1e-6, atol=1e-9):
            notes.append(
                "observation times are unevenly spaced and interpolation is off; "
                "ARIMA treats them as a regular series, so horizons are approximate"
            )
        series = y
        step = spacing
        origin = t[-1]

    if t.size < MIN_TRAIN_POINTS:
        notes.append(
            f"only {t.size} observed points before the forecast — the paper's "
            "own weakest predictions come from exactly this situation; treat the "
            "interval, not the point estimate, as the message"
        )

    fit = auto_arima(series, **arima_kwargs)
    steps = int(np.ceil((targets.max() - origin) / step - 1e-9))
    steps = max(steps, 1)
    forecast = fit.results.get_forecast(steps=steps)  # type: ignore[union-attr]
    mean = np.asarray(forecast.predicted_mean, dtype=float)
    conf = np.asarray(forecast.conf_int(alpha=alpha), dtype=float)
    grid_times = origin + step * np.arange(1, steps + 1)

    idx = [int(np.argmin(np.abs(grid_times - target))) for target in targets]
    predicted, lower, upper = mean[idx], conf[idx, 0], conf[idx, 1]
    if clip_at_zero:
        predicted = np.clip(predicted, 0.0, None)
        lower = np.clip(lower, 0.0, None)
        upper = np.clip(upper, 0.0, None)

    return Forecast(
        animal=animal,
        fit=fit,
        times=targets,
        predicted=predicted,
        lower=lower,
        upper=upper,
        train_times=t,
        train_values=y,
        interpolated=bool(interpolate_step),
        alpha=alpha,
        warnings=notes,
    )


# --------------------------------------------------------------------------- #
# endpoint prediction across a cohort
# --------------------------------------------------------------------------- #
def predict_endpoint(
    scores: pd.DataFrame,
    endpoints: dict[str, float] | None = None,
    score_col: str = "relsa",
    **kwargs,
) -> list[Forecast]:
    """Predict each animal's RELSA score at its humane endpoint.

    This is the paper's primary evaluation: every measurement *up to the time
    point immediately before* the endpoint trains the model, which then predicts
    the score at the endpoint itself, where the actual score is known and can be
    compared. ``endpoints`` maps animal id to endpoint time; omit it to use each
    animal's last observed time point.
    """
    out: list[Forecast] = []
    for animal, block in scores.groupby(ID_COL, sort=False):
        block = block.dropna(subset=[score_col]).sort_values(TIME_COL)
        if block.empty:
            warnings.warn(f"animal {animal}: no finite RELSA scores", stacklevel=2)
            continue
        endpoint = (
            float(block[TIME_COL].iloc[-1])
            if endpoints is None
            else endpoints.get(str(animal))
        )
        if endpoint is None:
            continue
        train = block[block[TIME_COL] < endpoint]
        truth = block[np.isclose(block[TIME_COL], endpoint)]
        if len(train) < 2:
            warnings.warn(
                f"animal {animal}: only {len(train)} points before the endpoint, skipping",
                stacklevel=2,
            )
            continue
        forecast = forecast_animal(
            train[TIME_COL], train[score_col], target_times=[endpoint],
            animal=str(animal), **kwargs,
        )
        if not truth.empty:
            forecast.actual = np.array([float(truth[score_col].iloc[0])])
        out.append(forecast)
    return out


def forecast_indirect(
    prepared: pd.DataFrame,
    reference,
    target_time: float,
    animal: str = "",
    score_col: str = "relsa",
    **kwargs,
) -> dict[str, object]:
    """The *indirect* prediction: forecast each variable, then score the forecasts.

    ``prepared`` is the normalized measurement table for one animal (percent
    scale) and ``reference`` a ``relsa_score.ReferenceModel``. Each variable is
    forecast to ``target_time`` independently, and the RELSA score is computed
    from those forecasts.

    The paper found this worse than forecasting RELSA directly (median deviation
    -0.240 vs -0.002, d = 1.42): each variable's forecast error propagates into
    the score, whereas the direct forecast carries only its own error. Use this
    to reproduce that comparison, not as the working method.
    """
    from relsa_score import relsa_scores

    block = prepared.sort_values(TIME_COL)
    train = block[block[TIME_COL] < target_time]
    row: dict[str, object] = {ID_COL: animal, TIME_COL: target_time}
    predicted_row = {ID_COL: animal, TIME_COL: target_time}
    for var in reference.variables:
        series = train[[TIME_COL, var]].dropna()
        if len(series) < 2:
            predicted_row[var] = np.nan
            continue
        try:
            forecast = forecast_animal(
                series[TIME_COL], series[var], target_times=[target_time],
                animal=f"{animal}:{var}", clip_at_zero=False, **kwargs,
            )
            predicted_row[var] = float(forecast.predicted[0])
        except Exception:
            predicted_row[var] = np.nan
    scored = relsa_scores(pd.DataFrame([predicted_row]), reference, keep_meta=False)
    row["predicted"] = float(scored[score_col].iloc[0])
    row.update({f"pred_{k}": v for k, v in predicted_row.items()
                if k not in (ID_COL, TIME_COL)})
    truth = block[np.isclose(block[TIME_COL], target_time)]
    if not truth.empty:
        actual = relsa_scores(truth, reference, keep_meta=False)
        row["actual"] = float(actual[score_col].iloc[0])
    return row


def rolling_forecast(
    times: Iterable[float],
    values: Iterable[float],
    min_train: int = 3,
    animal: str = "",
    **kwargs,
) -> pd.DataFrame:
    """One-step-ahead forecast at every time point, refitting as data accrue.

    This is how the paper compares predictability across outcome measures
    (Figure 2): at each time point, forecast the next one and record the
    deviation from what actually happened.
    """
    t = np.asarray(list(times), dtype=float)
    y = np.asarray(list(values), dtype=float)
    rows: list[dict[str, object]] = []
    for cut in range(min_train, len(t)):
        train_t, train_y = t[:cut], y[:cut]
        if np.isfinite(train_y).sum() < 2:
            continue
        try:
            forecast = forecast_animal(
                train_t, train_y, target_times=[t[cut]], animal=animal, **kwargs
            )
        except Exception as exc:  # a single failed refit must not stop the sweep
            rows.append({ID_COL: animal, TIME_COL: t[cut], "predicted": np.nan,
                         "lower": np.nan, "upper": np.nan, "actual": y[cut],
                         "model": f"failed: {type(exc).__name__}"})
            continue
        rows.append({
            ID_COL: animal,
            TIME_COL: float(t[cut]),
            "predicted": float(forecast.predicted[0]),
            "lower": float(forecast.lower[0]),
            "upper": float(forecast.upper[0]),
            "actual": float(y[cut]),
            "model": forecast.fit.label(),
        })
    return pd.DataFrame(rows)


def summarize(forecasts: Sequence[Forecast], group: dict[str, str] | None = None) -> pd.DataFrame:
    """Per-animal and overall RMSE / PICP / MPIW, in the layout of the paper's Table 1."""
    rows: list[dict[str, object]] = []
    actual: list[float] = []
    predicted: list[float] = []
    lower: list[float] = []
    upper: list[float] = []
    for forecast in forecasts:
        if forecast.actual is None:
            continue
        metrics = forecast.metrics()
        rows.append({
            "group": (group or {}).get(forecast.animal, ""),
            ID_COL: forecast.animal,
            "model": forecast.fit.label(),
            "n": metrics.n,
            "rmse": round(metrics.rmse, 4),
            "picp": round(metrics.picp, 1),
            "mpiw": round(metrics.mpiw, 3),
        })
        actual.extend(forecast.actual.tolist())
        predicted.extend(forecast.predicted.tolist())
        lower.extend(forecast.lower.tolist())
        upper.extend(forecast.upper.tolist())

    frame = pd.DataFrame(rows)
    if not actual:
        return frame
    overall = forecast_metrics(actual, predicted, lower, upper)
    if not frame.empty and frame["group"].astype(bool).any():
        for label, block in frame.groupby("group"):
            if not label:
                continue
            sub = [f for f in forecasts if f.animal in set(block[ID_COL])]
            agg = forecast_metrics(
                np.concatenate([f.actual for f in sub]),  # type: ignore[arg-type]
                np.concatenate([f.predicted for f in sub]),
                np.concatenate([f.lower for f in sub]),
                np.concatenate([f.upper for f in sub]),
            )
            frame = pd.concat([frame, pd.DataFrame([{
                "group": label, ID_COL: f"-- {label} --", "model": "",
                "n": agg.n, "rmse": round(agg.rmse, 4),
                "picp": round(agg.picp, 1), "mpiw": round(agg.mpiw, 3),
            }])], ignore_index=True)
    return pd.concat([frame, pd.DataFrame([{
        "group": "", ID_COL: "OVERALL", "model": "",
        "n": overall.n, "rmse": round(overall.rmse, 4),
        "picp": round(overall.picp, 1), "mpiw": round(overall.mpiw, 3),
    }])], ignore_index=True)


def plot_forecast(
    forecast: Forecast,
    path: str | Path,
    endpoint_threshold: float | None = None,
    zones: Sequence[float] = (),
    title: str | None = None,
) -> Path:
    """Trajectory, forecast, and interval in the style of the paper's Figure 1."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(5.6, 3.8), constrained_layout=True)
    if forecast.train_times is not None:
        ax.plot(forecast.train_times, forecast.train_values, "-o", color="black",
                ms=4, lw=1.3, label="actual RELSA")
    ax.fill_between(
        np.concatenate([[forecast.train_times[-1]], forecast.times]),
        np.concatenate([[forecast.train_values[-1]], forecast.lower]),
        np.concatenate([[forecast.train_values[-1]], forecast.upper]),
        color="#4fc3c7", alpha=0.45,
        label=f"{100 * (1 - forecast.alpha):.0f}% prediction interval",
    )
    ax.plot(forecast.times, forecast.predicted, "o--", color="#1f7a7d", ms=5,
            label="predicted RELSA")
    if forecast.actual is not None:
        ax.plot(forecast.times, forecast.actual, "o", color="black", ms=5)
    if endpoint_threshold is not None:
        ax.axhline(endpoint_threshold, ls="--", color="#c1453b", lw=1.2)
        ax.annotate("individual endpoint", xy=(0.02, endpoint_threshold),
                    xycoords=("axes fraction", "data"), xytext=(0, 4),
                    textcoords="offset points", color="#c1453b", fontsize=8)
    for zone in zones:
        ax.axhline(zone, ls=":", color="#666666", lw=1.0)
    ax.set_xlabel("time")
    ax.set_ylabel("RELSA score")
    ax.set_title(title or f"{forecast.animal}  —  {forecast.fit.label()}", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    path = Path(path)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Forecast RELSA trajectories with ARIMA (the foRcast tool).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("scores", help="CSV of RELSA scores (output of relsa_score.py)")
    parser.add_argument("--score-col", default="relsa")
    parser.add_argument(
        "--mode", choices=("endpoint", "rolling"), default="endpoint",
        help="endpoint: predict the score at each animal's endpoint; "
        "rolling: one-step-ahead forecast at every time point",
    )
    parser.add_argument(
        "--endpoints", metavar="ID=TIME", action="append", default=[],
        help="humane-endpoint time per animal, repeatable "
        "(default: each animal's last time point)",
    )
    parser.add_argument("--animals", help="comma-separated ids to restrict to")
    parser.add_argument(
        "--interpolate-step", type=float, default=DEFAULT_STEP,
        help="grid for linear interpolation before fitting; 0 disables it",
    )
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="1 - alpha is the prediction interval level")
    parser.add_argument("--max-p", type=int, default=5)
    parser.add_argument("--max-q", type=int, default=5)
    parser.add_argument("--max-d", type=int, default=2)
    parser.add_argument("--full-grid", action="store_true",
                        help="exhaustive p/q search instead of the stepwise hill-climb")
    parser.add_argument("--group-col", help="column labelling model/intervention, for the summary")
    parser.add_argument("--out", help="write per-forecast rows to this CSV")
    parser.add_argument("--summary-out", help="write the metric summary to this CSV")
    parser.add_argument("--plot-dir", help="write one figure per animal into this directory")
    parser.add_argument("--endpoint-line", type=float, default=None,
                        help="RELSA value to draw as the individual endpoint in plots")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    frame = pd.read_csv(args.scores)
    for col in (ID_COL, TIME_COL):
        if col not in frame.columns:
            raise SystemExit(f"column {col!r} missing from {args.scores}")
    if args.score_col not in frame.columns:
        raise SystemExit(f"score column {args.score_col!r} missing from {args.scores}")

    keep = parse_list(args.animals)
    if keep:
        frame = frame[frame[ID_COL].astype(str).isin(keep)]
        if frame.empty:
            raise SystemExit(f"no rows for animals {keep}")

    endpoints: dict[str, float] | None = None
    if args.endpoints:
        endpoints = {}
        for pair in args.endpoints:
            if "=" not in pair:
                raise SystemExit(f"--endpoints expects ID=TIME, got {pair!r}")
            animal, value = pair.split("=", 1)
            endpoints[animal] = float(value)

    groups = None
    if args.group_col:
        if args.group_col not in frame.columns:
            raise SystemExit(f"--group-col {args.group_col!r} not in data")
        groups = (
            frame.groupby(ID_COL)[args.group_col].first().astype(str).to_dict()
        )
        groups = {str(k): v for k, v in groups.items()}

    step = args.interpolate_step or None
    arima_kwargs = dict(
        interpolate_step=step,
        alpha=args.alpha,
        max_p=args.max_p,
        max_q=args.max_q,
        max_d=args.max_d,
        stepwise=not args.full_grid,
    )

    if args.mode == "rolling":
        rows = []
        for animal, block in frame.groupby(ID_COL, sort=False):
            block = block.dropna(subset=[args.score_col]).sort_values(TIME_COL)
            rows.append(
                rolling_forecast(
                    block[TIME_COL], block[args.score_col], animal=str(animal),
                    **arima_kwargs,
                )
            )
        table = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
        if table.empty:
            raise SystemExit("no forecasts could be produced")
        metrics = forecast_metrics(
            table["actual"], table["predicted"], table["lower"], table["upper"]
        )
        print(table.to_string(index=False))
        print(
            f"\nrolling one-step-ahead: n={metrics.n}  RMSE={metrics.rmse:.4f}  "
            f"PICP={metrics.picp:.1f}%  MPIW={metrics.mpiw:.3f}"
        )
        if args.out:
            table.to_csv(args.out, index=False)
            print(f"wrote {args.out}", file=sys.stderr)
        return 0

    forecasts = predict_endpoint(
        frame, endpoints=endpoints, score_col=args.score_col, **arima_kwargs
    )
    if not forecasts:
        raise SystemExit("no animal had enough data to forecast")

    detail = pd.concat([f.to_frame() for f in forecasts], ignore_index=True)
    print(detail.to_string(index=False))
    summary = summarize(forecasts, group=groups)
    print("\n" + summary.to_string(index=False))

    for forecast in forecasts:
        for note in forecast.warnings:
            print(f"note [{forecast.animal}]: {note}", file=sys.stderr)

    if args.out:
        detail.to_csv(args.out, index=False)
        print(f"wrote {args.out}", file=sys.stderr)
    if args.summary_out:
        summary.to_csv(args.summary_out, index=False)
        print(f"wrote {args.summary_out}", file=sys.stderr)
    if args.plot_dir:
        directory = Path(args.plot_dir)
        directory.mkdir(parents=True, exist_ok=True)
        for forecast in forecasts:
            written = plot_forecast(
                forecast, directory / f"{forecast.animal}.png",
                endpoint_threshold=args.endpoint_line,
            )
            print(f"wrote {written}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/kde_thresholds.py`

```python
#!/usr/bin/env python3
"""Kernel-density thresholds on the RELSA scale (severity zones).

Lutscher et al. (2026) define candidate severity thresholds by estimating the
probability density of the RELSA scores observed in a model and taking the
*minima* of that density — the sparsely populated valleys between clusters of
scores. Two minima split the scale into three zones: normal, attention, danger.

The published sepsis analysis (n = 7 mice, 239 scores) yields minima at
RELSA = 0.337 and 0.643. The KDE here reproduces R's ``stats::density``
defaults — Gaussian kernel, Silverman's ``bw.nrd0`` bandwidth, a 512-point grid
extended three bandwidths past the data — so thresholds match the R workflow
the paper used.

Thresholds are **model-specific and bandwidth-sensitive**, and they are not the
severity categories of EU Directive 2010/63/EU. Report them as candidate zones
for one model with the reference set and bandwidth stated, never as a
regulatory grading.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

DEFAULT_GRID = 512
DEFAULT_CUT = 3.0
IQR_TO_SIGMA = 1.349  # R's bw.nrd0 uses this literal, not 1.34898


def bw_nrd0(values: np.ndarray) -> float:
    """Silverman's rule of thumb exactly as R's ``bw.nrd0`` computes it.

    ``0.9 * min(sd, IQR/1.349) * n^(-1/5)``, with R's fallback chain when the
    spread estimate collapses to zero. scipy's own ``'silverman'`` factor is a
    *different* formula, so passing it would shift every threshold.
    """
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        raise ValueError("need at least 2 finite values to estimate a bandwidth")
    sd = float(np.std(values, ddof=1))
    q75, q25 = np.percentile(values, [75, 25])  # linear interpolation == R type 7
    lo = min(sd, float(q75 - q25) / IQR_TO_SIGMA)
    if lo == 0:
        lo = sd or abs(float(values[0])) or 1.0
    return 0.9 * lo * values.size ** (-0.2)


@dataclass
class ThresholdResult:
    """Density minima on the RELSA scale plus the zones they imply."""

    thresholds: list[float]
    modes: list[float]
    bandwidth: float
    n: int
    grid: np.ndarray = field(repr=False)
    density: np.ndarray = field(repr=False)
    zone_counts: dict[str, int] = field(default_factory=dict)

    def zone_edges(self) -> list[tuple[float, float]]:
        edges = [0.0, *self.thresholds, float("inf")]
        return list(zip(edges[:-1], edges[1:]))

    def zone_names(self) -> list[str]:
        n_zones = len(self.thresholds) + 1
        if n_zones == 1:
            return ["all"]
        if n_zones == 2:
            return ["normal", "danger"]
        if n_zones == 3:
            return ["normal", "attention", "danger"]
        return [f"zone{i + 1}" for i in range(n_zones)]

    def assign(self, values: Iterable[float]) -> list[str]:
        """Label each RELSA score with the zone it falls in."""
        names = self.zone_names()
        out: list[str] = []
        for value in values:
            if not np.isfinite(value):
                out.append("undefined")
                continue
            index = int(np.searchsorted(self.thresholds, value, side="right"))
            out.append(names[index])
        return out

    def describe(self) -> str:
        lines = [
            f"KDE on {self.n} RELSA scores  (bandwidth = {self.bandwidth:.4f})",
            "  candidate thresholds (density minima): "
            + (", ".join(f"{t:.3f}" for t in self.thresholds) or "none found"),
            "  density modes: " + ", ".join(f"{m:.3f}" for m in self.modes),
        ]
        for name, (low, high) in zip(self.zone_names(), self.zone_edges()):
            span = f"[{low:.3f}, {high:.3f})" if np.isfinite(high) else f">= {low:.3f}"
            count = self.zone_counts.get(name)
            tail = f"  n={count} ({100 * count / self.n:.1f}%)" if count is not None else ""
            lines.append(f"  {name:<10}{span}{tail}")
        return "\n".join(lines)

    def as_dict(self) -> dict:
        return {
            "thresholds": [round(float(t), 4) for t in self.thresholds],
            "modes": [round(float(m), 4) for m in self.modes],
            "bandwidth": round(float(self.bandwidth), 6),
            "n": self.n,
            "zones": {
                name: {
                    "low": round(float(low), 4),
                    "high": None if not np.isfinite(high) else round(float(high), 4),
                    "n": self.zone_counts.get(name),
                }
                for name, (low, high) in zip(self.zone_names(), self.zone_edges())
            },
        }


def density_curve(
    values: Iterable[float],
    bandwidth: float | None = None,
    grid_size: int = DEFAULT_GRID,
    cut: float = DEFAULT_CUT,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Gaussian KDE on R's grid: ``[min - cut*bw, max + cut*bw]``, ``grid_size`` points."""
    from scipy.stats import gaussian_kde

    data = np.asarray(list(values), dtype=float)
    data = data[np.isfinite(data)]
    if data.size < 2:
        raise ValueError("need at least 2 finite RELSA scores")

    bw = float(bandwidth) if bandwidth else bw_nrd0(data)
    # gaussian_kde scales its factor by the sample sd, so divide it back out.
    sd = float(np.std(data, ddof=1))
    kde = gaussian_kde(data, bw_method=bw / sd if sd > 0 else bw)
    grid = np.linspace(data.min() - cut * bw, data.max() + cut * bw, grid_size)
    return grid, kde(grid), bw


def _zone_counts(data: np.ndarray, thresholds: Sequence[float]) -> list[int]:
    edges = [-np.inf, *thresholds, np.inf]
    return [
        int(np.sum((data >= low) & (data < high)))
        for low, high in zip(edges[:-1], edges[1:])
    ]


def _prune_thin_zones(
    data: np.ndarray,
    minima: list[tuple[float, float]],
    min_zone_fraction: float,
) -> list[tuple[float, float]]:
    """Drop thresholds that carve off a zone holding almost no observations.

    A finite sample's density estimate wiggles in the tails, and a wiggle can
    produce a minimum that separates one stray observation from the rest. That
    is a property of the smoother, not a severity zone. Each surviving zone must
    hold at least ``min_zone_fraction`` of the scores; when one does not, the
    shallowest threshold bounding it is removed and the check repeats.
    """
    if min_zone_fraction <= 0 or not minima:
        return minima
    kept = sorted(minima)
    floor = min_zone_fraction * data.size
    while kept:
        counts = _zone_counts(data, [m[0] for m in kept])
        thinnest = int(np.argmin(counts))
        if counts[thinnest] >= floor:
            break
        # Zone i is bounded by thresholds i-1 and i; drop the shallower one.
        bounding = [j for j in (thinnest - 1, thinnest) if 0 <= j < len(kept)]
        kept.pop(max(bounding, key=lambda j: kept[j][1]))
    return kept


def find_thresholds(
    values: Iterable[float],
    bandwidth: float | None = None,
    grid_size: int = DEFAULT_GRID,
    cut: float = DEFAULT_CUT,
    n_thresholds: int | None = None,
    within_data: bool = True,
    min_zone_fraction: float = 0.02,
) -> ThresholdResult:
    """Locate density minima and turn them into severity zones.

    ``n_thresholds`` keeps only the *deepest* k minima (the paper keeps two);
    ``within_data`` discards minima outside the observed score range, which the
    padded grid can otherwise produce; ``min_zone_fraction`` discards thresholds
    that would isolate a near-empty zone (see ``_prune_thin_zones``).

    When the density is unimodal there are no interior minima and the result
    carries an empty threshold list — a real answer, meaning this cohort's
    scores form one cluster and give no data-driven place to cut.
    """
    data = np.asarray(list(values), dtype=float)
    data = data[np.isfinite(data)]
    grid, dens, bw = density_curve(data, bandwidth, grid_size, cut)

    lower, upper = float(data.min()), float(data.max())
    minima: list[tuple[float, float]] = []
    maxima: list[float] = []
    for i in range(1, len(grid) - 1):
        if dens[i] <= dens[i - 1] and dens[i] < dens[i + 1]:
            if not within_data or lower <= grid[i] <= upper:
                minima.append((float(grid[i]), float(dens[i])))
        elif dens[i] >= dens[i - 1] and dens[i] > dens[i + 1]:
            if not within_data or lower <= grid[i] <= upper:
                maxima.append(float(grid[i]))

    minima = _prune_thin_zones(data, minima, min_zone_fraction)
    if n_thresholds is not None and len(minima) > n_thresholds:
        minima = sorted(sorted(minima, key=lambda m: m[1])[:n_thresholds])

    thresholds = [m[0] for m in sorted(minima)]
    result = ThresholdResult(
        thresholds=thresholds,
        modes=maxima,
        bandwidth=bw,
        n=int(data.size),
        grid=grid,
        density=dens,
    )
    labels = result.assign(data)
    result.zone_counts = {
        name: int(sum(1 for label in labels if label == name))
        for name in result.zone_names()
    }
    return result


def plot_thresholds(
    result: ThresholdResult,
    values: Iterable[float],
    path: str | Path,
    title: str = "RELSA severity zones",
) -> Path:
    """Density curve with the minima marked, in the style of the paper's Figure 3."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = np.asarray(list(values), dtype=float)
    data = data[np.isfinite(data)]

    fig, ax = plt.subplots(figsize=(5.5, 4.0), constrained_layout=True)
    ax.plot(result.grid, result.density, color="#333333", lw=1.6)
    ax.fill_between(result.grid, result.density, color="#333333", alpha=0.08)
    colors = ["#4c9f70", "#e0a458", "#c1453b", "#7b3f9e"]
    edges = [result.grid.min(), *result.thresholds, result.grid.max()]
    for i, (low, high) in enumerate(zip(edges[:-1], edges[1:])):
        band = (result.grid >= low) & (result.grid <= high)
        ax.fill_between(
            result.grid[band], result.density[band], color=colors[i % len(colors)], alpha=0.30
        )
    for threshold in result.thresholds:
        ax.axvline(threshold, ls="--", lw=1.2, color="black")
        ax.annotate(
            f"{threshold:.3f}",
            xy=(threshold, ax.get_ylim()[1]),
            xytext=(3, -12),
            textcoords="offset points",
            fontsize=9,
        )
    ax.plot(data, np.full_like(data, -0.02 * result.density.max()), "|", color="#444444",
            ms=6, alpha=0.6)
    ax.set_xlabel("RELSA score")
    ax.set_ylabel("density")
    ax.set_title(f"{title}  (n={result.n}, bw={result.bandwidth:.3f})", fontsize=10)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    path = Path(path)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Find candidate RELSA severity thresholds by kernel density estimation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("scores", help="CSV of RELSA scores (output of relsa_score.py)")
    parser.add_argument("--column", default="relsa", help="column holding the RELSA score")
    parser.add_argument(
        "--group", action="append", default=[], metavar="COL=VALUE",
        help="restrict to a subset before estimating the density, repeatable",
    )
    parser.add_argument(
        "--n-thresholds", type=int, default=None,
        help="keep only the k deepest minima (the paper keeps 2)",
    )
    parser.add_argument("--bandwidth", type=float, default=None,
                        help="override the bw.nrd0 bandwidth")
    parser.add_argument("--grid-size", type=int, default=DEFAULT_GRID)
    parser.add_argument(
        "--include-outside", action="store_true",
        help="keep minima outside the observed score range",
    )
    parser.add_argument(
        "--min-zone-fraction", type=float, default=0.02,
        help="discard a threshold that would isolate a zone holding less than "
        "this fraction of the scores (tail wiggle in the density estimate)",
    )
    parser.add_argument("--plot", help="write a density figure to this path")
    parser.add_argument("--json", help="write the thresholds to this JSON file")
    parser.add_argument(
        "--label-out", help="write the input scores back out with a zone column"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    frame = pd.read_csv(args.scores)
    if args.column not in frame.columns:
        raise SystemExit(f"column {args.column!r} not in {list(frame.columns)}")

    for pair in args.group:
        if "=" not in pair:
            raise SystemExit(f"--group expects col=value, got {pair!r}")
        col, value = pair.split("=", 1)
        if col not in frame.columns:
            raise SystemExit(f"--group column {col!r} not in data")
        frame = frame[frame[col].astype(str) == value]
    if frame.empty:
        raise SystemExit("no rows left after --group filtering")

    values = pd.to_numeric(frame[args.column], errors="coerce")
    result = find_thresholds(
        values,
        bandwidth=args.bandwidth,
        grid_size=args.grid_size,
        n_thresholds=args.n_thresholds,
        within_data=not args.include_outside,
        min_zone_fraction=args.min_zone_fraction,
    )
    print(result.describe())
    print(
        "\nThese are candidate, model-specific zones on the RELSA scale. They are "
        "not\nseverity categories under EU Directive 2010/63/EU and are not "
        "comparable\nacross models or reference sets.",
        file=sys.stderr,
    )

    if args.plot:
        print(f"wrote {plot_thresholds(result, values, args.plot)}", file=sys.stderr)
    if args.json:
        Path(args.json).write_text(json.dumps(result.as_dict(), indent=2) + "\n")
        print(f"wrote {args.json}", file=sys.stderr)
    if args.label_out:
        labelled = frame.copy()
        labelled["zone"] = result.assign(values)
        labelled.to_csv(args.label_out, index=False)
        print(f"wrote {args.label_out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/relsa_score.py`

```python
#!/usr/bin/env python3
"""RELSA (RELative Severity Assessment) score — a faithful Python port.

Implements the four-step procedure of Talbot et al. (2022), Front. Vet. Sci.
9:937711, as coded in the R package ``mytalbot/RELSA``:

1. directionality — variables that *rise* under duress are "turned";
2. normalization — each variable divided by that animal's own baseline (100%);
3. reference set — the cohort of assumed greatest burden fixes the scale;
4. weights and score — per-variable deviation relative to the reference
   maximum, combined by a root-mean-square:

       delta_i(t)  = 100 - x_i(t)            (turned: x_i(t) - 100), floored at 0
       RW_i(t)     = delta_i(t) / |100 - max_i,ref|
       RELSA(t)    = sqrt( mean_i RW_i(t)^2 )   over non-missing i

RELSA = 0 means "at baseline"; RELSA = 1 means the animal reached the reference
set's maximum deviation; above 1 means it exceeded it. Missing variables are
dropped from the mean rather than imputed, so a score is defined whenever at
least one variable was measured.

Numerically reproduces the R package's published worked example (surgery
dataset, animal Ca_001) to the two decimals the package prints; see
``tests/relsa-severity-assessment/``.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    ID_COL,
    TIME_COL,
    RelsaDataError,
    parse_list,
    percent_of_baseline,
    read_relsa_table,
    score_to_percent,
    validate,
    variable_columns,
)

BASELINE_PCT = 100.0


# --------------------------------------------------------------------------- #
# reference model
# --------------------------------------------------------------------------- #
@dataclass
class ReferenceModel:
    """The severity scale RELSA scores are relative to.

    ``maxsev`` is the most extreme normalized value each variable reached
    anywhere in the reference cohort (minimum, or maximum for turned
    variables); ``maxdelta`` is its distance from baseline, the denominator of
    every weight. A RELSA score is only interpretable together with the
    reference set that produced it, so record ``label`` in any report.
    """

    variables: tuple[str, ...]
    turned: tuple[str, ...]
    maxsev: dict[str, float]
    maxdelta: dict[str, float]
    n_animals: int
    n_rows: int
    label: str = ""
    baseline_time: float | list[float] | None = None
    notes: dict[str, str] = field(default_factory=dict)

    def to_json(self, path: str | Path) -> None:
        payload = {
            "variables": list(self.variables),
            "turned": list(self.turned),
            "maxsev": self.maxsev,
            "maxdelta": self.maxdelta,
            "n_animals": self.n_animals,
            "n_rows": self.n_rows,
            "label": self.label,
            "baseline_time": self.baseline_time,
            "notes": self.notes,
        }
        Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    @classmethod
    def from_json(cls, path: str | Path) -> "ReferenceModel":
        payload = json.loads(Path(path).read_text())
        return cls(
            variables=tuple(payload["variables"]),
            turned=tuple(payload["turned"]),
            maxsev={k: float(v) for k, v in payload["maxsev"].items()},
            maxdelta={k: float(v) for k, v in payload["maxdelta"].items()},
            n_animals=int(payload["n_animals"]),
            n_rows=int(payload["n_rows"]),
            label=payload.get("label", ""),
            baseline_time=payload.get("baseline_time"),
            notes=payload.get("notes", {}),
        )

    def describe(self) -> str:
        rows = [
            f"reference model: {self.label or '(unlabelled)'}",
            f"  animals={self.n_animals}  rows={self.n_rows}  "
            f"baseline_time={self.baseline_time}",
            f"  {'variable':<12}{'turned':>8}{'max reached':>14}{'max delta':>12}",
        ]
        for var in self.variables:
            rows.append(
                f"  {var:<12}{'yes' if var in self.turned else 'no':>8}"
                f"{self.maxsev[var]:>14.2f}{self.maxdelta[var]:>12.2f}"
            )
        return "\n".join(rows)


def build_reference(
    frame: pd.DataFrame,
    variables: Sequence[str],
    turned: Sequence[str] = (),
    baseline_time: float | Sequence[float] | None = None,
    label: str = "",
) -> ReferenceModel:
    """Derive the reference scale from an already-normalized cohort.

    ``frame`` must be on the percent scale (baseline = 100) — run
    ``prepare`` or ``_common.percent_of_baseline`` first. ``turned`` names the
    variables whose *increase* signals worsening.
    """
    variables = list(variables)
    turned = [t for t in turned if t in variables]
    validate(frame, variables)

    maxsev: dict[str, float] = {}
    maxdelta: dict[str, float] = {}
    degenerate: list[str] = []
    for var in variables:
        col = pd.to_numeric(frame[var], errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(col).any():
            raise RelsaDataError(
                f"variable {var!r} has no finite values in the reference set"
            )
        extreme = float(np.nanmax(col)) if var in turned else float(np.nanmin(col))
        maxsev[var] = extreme
        maxdelta[var] = abs(BASELINE_PCT - extreme)
        if maxdelta[var] == 0:
            degenerate.append(var)

    if degenerate:
        raise RelsaDataError(
            f"variables {degenerate} never deviate from baseline in the reference "
            "set, so their weight would divide by zero. Drop them, or choose a "
            "reference cohort that actually expresses the burden (the published "
            "models use the treatment group of assumed greatest severity)."
        )

    wrong_way = [
        v for v in variables if (maxsev[v] > BASELINE_PCT) != (v in turned)
    ]
    if wrong_way:
        warnings.warn(
            f"variables {wrong_way} deviate in the opposite direction to their "
            "declared directionality — check the `turned` list. A variable that "
            "only ever rises must be turned; one that only falls must not be.",
            stacklevel=2,
        )

    return ReferenceModel(
        variables=tuple(variables),
        turned=tuple(turned),
        maxsev=maxsev,
        maxdelta=maxdelta,
        n_animals=int(frame[ID_COL].nunique()),
        n_rows=int(len(frame)),
        label=label,
        baseline_time=(
            None
            if baseline_time is None
            else (float(baseline_time) if np.isscalar(baseline_time) else [float(t) for t in baseline_time])  # type: ignore[arg-type]
        ),
    )


# --------------------------------------------------------------------------- #
# score
# --------------------------------------------------------------------------- #
def relsa_weights(
    frame: pd.DataFrame,
    reference: ReferenceModel,
    drop: Sequence[str] = (),
    round_digits: int | None = 2,
) -> pd.DataFrame:
    """Per-variable RELSA weights (RW) for every animal and time point.

    Rounding to two decimals is the R package's behaviour and is applied to the
    deltas and to the weights, before the root-mean-square. Pass
    ``round_digits=None`` for full precision (scores then differ from R in the
    third decimal).
    """
    used = [v for v in reference.variables if v not in set(drop)]
    if not used:
        raise RelsaDataError("every reference variable was dropped")
    missing = [v for v in used if v not in frame.columns]
    if missing:
        raise RelsaDataError(
            f"variables {missing} are in the reference model but not in the data. "
            "The test set must carry the same variable names as the reference."
        )
    validate(frame, used)

    out = frame[[ID_COL, TIME_COL]].copy()
    for var in used:
        values = pd.to_numeric(frame[var], errors="coerce").to_numpy(dtype=float)
        delta = (
            values - BASELINE_PCT if var in reference.turned else BASELINE_PCT - values
        )
        delta = np.where(np.isfinite(delta), np.clip(delta, 0.0, None), np.nan)
        if round_digits is not None:
            delta = np.round(delta, round_digits)
        weight = delta / reference.maxdelta[var]
        if round_digits is not None:
            weight = np.round(weight, round_digits)
        out[var] = weight
    return out


def _warn_on_composition_change(scored: pd.DataFrame, used: Sequence[str]) -> None:
    """Warn when the set of available variables changes along an animal's trajectory.

    RELSA averages over whichever variables were measured, so a variable that
    appears or disappears mid-trajectory moves the score even when the animal's
    state is unchanged. In the published sepsis data, body weight is recorded
    only on the day of euthanasia; including it drops that animal's endpoint
    score from 0.93 to 0.83 purely by changing the mean's composition. Score the
    variables that are measured throughout, and keep the rest as separate
    endpoint criteria.
    """
    offenders: list[str] = []
    for animal, block in scored.groupby(ID_COL, sort=False):
        present = block[list(used)].notna()
        signatures = {tuple(row) for row in present.itertuples(index=False)}
        signatures.discard(tuple([False] * len(used)))  # fully missing rows are fine
        if len(signatures) > 1:
            varying = [
                var for var in used if present[var].nunique(dropna=False) > 1
            ]
            offenders.append(f"{animal}: {', '.join(varying)}")
    if offenders:
        warnings.warn(
            "the set of measured variables changes across time points, so RELSA "
            "scores along these trajectories are not strictly comparable — a "
            "variable appearing or disappearing shifts the score by itself: "
            + "; ".join(offenders[:5])
            + ("..." if len(offenders) > 5 else ""),
            stacklevel=3,
        )


def relsa_scores(
    frame: pd.DataFrame,
    reference: ReferenceModel,
    drop: Sequence[str] = (),
    round_digits: int | None = 2,
    keep_meta: bool = True,
) -> pd.DataFrame:
    """RELSA score per animal per time point, with the weights that produced it.

    Returns ``id``, ``time``, any metadata columns, one column per variable
    holding its weight, ``n_vars`` (variables available at that time point), and
    ``relsa``. Rows where every variable is missing get ``relsa = NaN``.
    """
    weights = relsa_weights(frame, reference, drop=drop, round_digits=round_digits)
    used = [c for c in weights.columns if c not in (ID_COL, TIME_COL)]

    matrix = weights[used].to_numpy(dtype=float)
    available = np.isfinite(matrix).sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean_square = np.nansum(matrix**2, axis=1) / available
    score = np.sqrt(mean_square)
    score = np.where(available == 0, np.nan, score)
    if round_digits is not None:
        score = np.round(score, round_digits)

    out = weights.copy()
    out["n_vars"] = available
    out["relsa"] = score

    _warn_on_composition_change(out, used)

    if keep_meta:
        meta = [c for c in ("treatment", "condition") if c in frame.columns]
        if meta:
            labels = frame[[ID_COL, TIME_COL, *meta]]
            out = out.merge(labels, on=[ID_COL, TIME_COL], how="left")
            order = [ID_COL, TIME_COL, *meta, *used, "n_vars", "relsa"]
            out = out[order]
    return out


def prepare(
    frame: pd.DataFrame,
    normalize: Sequence[str] = (),
    baseline_time: float | Sequence[float] | None = None,
) -> pd.DataFrame:
    """Normalize the named variables to each animal's own baseline (= 100%).

    Variables *not* named are left untouched — that is the RELSA convention and
    it matters: body-weight change (bwc) and scores mapped with
    ``score_to_percent`` already sit on the percent scale, and normalizing them
    twice silently flattens them.
    """
    if not normalize:
        return frame.copy()
    return percent_of_baseline(frame, list(normalize), baseline_time=baseline_time)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _filter_group(frame: pd.DataFrame, pairs: Sequence[str]) -> pd.DataFrame:
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"--reference-group expects col=value, got {pair!r}")
        col, value = pair.split("=", 1)
        if col not in frame.columns:
            raise SystemExit(f"--reference-group column {col!r} not in data")
        frame = frame[frame[col].astype(str) == value]
        if frame.empty:
            raise SystemExit(f"--reference-group {pair!r} selected no rows")
    return frame


def _parse_score_scale(spec: str, frame: pd.DataFrame) -> tuple[str, tuple[float, float]]:
    """Parse ``COL=MAX`` or ``COL=MAX:BASELINE`` from --score-scale."""
    if "=" not in spec:
        raise SystemExit(f"--score-scale expects COL=MAX[:BASELINE], got {spec!r}")
    column, bounds = spec.split("=", 1)
    if column not in frame.columns:
        raise SystemExit(f"--score-scale column {column!r} not in data")
    parts = bounds.split(":")
    try:
        max_score = float(parts[0])
        baseline = float(parts[1]) if len(parts) > 1 else 0.0
    except ValueError:
        raise SystemExit(f"--score-scale bounds must be numeric, got {bounds!r}") from None
    return column, (max_score, baseline)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute RELSA severity scores for a RELSA-format table.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("data", help="CSV/TSV in RELSA long format (id, time, variables)")
    parser.add_argument(
        "--variables",
        help="comma-separated variables to score (default: every measurement column)",
    )
    parser.add_argument(
        "--turned",
        help="comma-separated variables that RISE under worsening severity "
        "(clinical scores, biomarkers, fever, tachycardia)",
    )
    parser.add_argument(
        "--normalize",
        help="comma-separated variables to divide by their own baseline; omit any "
        "variable already on a percent scale (bwc, mapped scores)",
    )
    parser.add_argument(
        "--score-scale",
        action="append",
        default=[],
        metavar="COL=MAX[:BASELINE]",
        help="map an ordinal severity score onto the percent scale, where MAX is "
        "the worst possible score and BASELINE the healthy one (default 0). "
        "Required for scores whose baseline is 0, which cannot be ratio-normalized. "
        "Implies the variable is turned and not normalized. Repeatable.",
    )
    parser.add_argument(
        "--baseline-time",
        help="time value(s) defining the baseline, comma-separated to average a "
        "window (default: each animal's first time point)",
    )
    parser.add_argument(
        "--reference-group",
        action="append",
        default=[],
        metavar="COL=VALUE",
        help="restrict the reference set, repeatable (e.g. treatment=CLP)",
    )
    parser.add_argument(
        "--reference-data",
        help="separate table for the reference set (default: the same file)",
    )
    parser.add_argument(
        "--load-reference", help="reuse a reference model saved by --save-reference"
    )
    parser.add_argument("--save-reference", help="write the reference model to JSON")
    parser.add_argument("--drop", help="comma-separated variables to exclude from scoring")
    parser.add_argument(
        "--full-precision",
        action="store_true",
        help="skip the 2-decimal rounding the R package applies",
    )
    parser.add_argument("--out", help="write scores to this CSV (default: stdout)")
    parser.add_argument("--id-col", default=ID_COL)
    parser.add_argument("--time-col", help="name of the time column, if not auto-detected")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    digits = None if args.full_precision else 2

    frame = read_relsa_table(args.data, id_col=args.id_col, time_col=args.time_col)
    normalize = parse_list(args.normalize)
    turned = parse_list(args.turned)
    variables = parse_list(args.variables) or variable_columns(frame)

    for spec in args.score_scale:
        column, bounds = _parse_score_scale(spec, frame)
        frame[column] = score_to_percent(frame[column], *bounds)
        if column not in turned:
            turned.append(column)
        if column in normalize:
            normalize.remove(column)
            print(
                f"note: {column} is mapped by --score-scale, so it is not "
                "baseline-normalized as well",
                file=sys.stderr,
            )
        if column not in variables:
            variables.append(column)

    baseline_time: float | list[float] | None = None
    if args.baseline_time:
        times = [float(t) for t in parse_list(args.baseline_time)]
        baseline_time = times[0] if len(times) == 1 else times

    prepared = prepare(frame, normalize=normalize, baseline_time=baseline_time)

    if args.load_reference:
        reference = ReferenceModel.from_json(args.load_reference)
    else:
        if args.reference_data:
            ref_raw = read_relsa_table(
                args.reference_data, id_col=args.id_col, time_col=args.time_col
            )
            ref_frame = prepare(ref_raw, normalize=normalize, baseline_time=baseline_time)
        else:
            ref_frame = prepared
        ref_frame = _filter_group(ref_frame, args.reference_group)
        label = args.reference_data or args.data
        if args.reference_group:
            label = f"{label} [{', '.join(args.reference_group)}]"
        reference = build_reference(
            ref_frame,
            variables=variables,
            turned=turned,
            baseline_time=baseline_time,
            label=label,
        )
    if args.save_reference:
        reference.to_json(args.save_reference)

    print(reference.describe(), file=sys.stderr)

    scores = relsa_scores(
        prepared, reference, drop=parse_list(args.drop), round_digits=digits
    )
    if args.out:
        scores.to_csv(args.out, index=False)
        print(f"wrote {len(scores)} rows to {args.out}", file=sys.stderr)
    else:
        scores.to_csv(sys.stdout, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `assets/example_cohort.csv`

```csv
id,treatment,condition,day,temp,weight,score,il6
M01,treated,endpoint,-1,37.15,25.17,0,35.1
M01,treated,endpoint,0,37.26,25.25,0,39.5
M01,treated,endpoint,1,35.83,23.12,4,162.0
M01,treated,endpoint,2,35.29,21.82,5,218.8
M01,treated,endpoint,3,35.12,21.44,7,252.8
M01,treated,endpoint,4,35.22,20.92,7,266.9
M01,treated,endpoint,5,34.47,20.74,7,280.0
M01,treated,endpoint,6,,,,
M01,treated,endpoint,7,,,,
M02,treated,endpoint,-1,37.37,21.87,0,48.5
M02,treated,endpoint,0,37.32,21.94,0,51.4
M02,treated,endpoint,1,36.13,20.15,3,194.1
M02,treated,endpoint,2,35.72,19.31,5,280.2
M02,treated,endpoint,3,35.39,18.82,6,317.3
M02,treated,endpoint,4,34.86,18.49,7,343.6
M02,treated,endpoint,5,35.01,18.29,7,368.0
M02,treated,endpoint,6,35.2,18.11,7,372.2
M02,treated,endpoint,7,,,,
M03,treated,survivor,-1,37.29,24.65,0,39.1
M03,treated,survivor,0,37.28,24.74,0,32.9
M03,treated,survivor,1,36.61,23.2,2,117.3
M03,treated,survivor,2,36.17,22.61,3,165.0
M03,treated,survivor,3,36.11,22.22,4,187.0
M03,treated,survivor,4,36.54,22.45,3,162.8
M03,treated,survivor,5,36.6,23.12,3,126.1
M03,treated,survivor,6,36.49,23.46,2,104.0
M03,treated,survivor,7,37.13,24.11,1,70.4
M04,treated,survivor,-1,37.09,24.99,0,36.1
M04,treated,survivor,0,36.88,24.98,0,37.1
M04,treated,survivor,1,36.57,23.95,1,93.4
M04,treated,survivor,2,36.6,23.55,2,118.1
M04,treated,survivor,3,36.27,23.08,3,138.1
M04,treated,survivor,4,36.09,23.38,3,151.1
M04,treated,survivor,5,36.46,23.51,2,100.4
M04,treated,survivor,6,36.52,24.11,2,86.4
M04,treated,survivor,7,36.94,24.76,1,58.1
S01,sham,sham,-1,37.49,25.34,0,49.6
S01,sham,sham,0,37.67,25.39,0,58.1
S01,sham,sham,1,37.1,25.39,1,74.9
S01,sham,sham,2,37.27,24.88,0,75.6
S01,sham,sham,3,37.02,24.89,0,72.0
S01,sham,sham,4,37.17,25.23,1,78.6
S01,sham,sham,5,37.51,25.12,1,88.2
S01,sham,sham,6,37.53,25.03,0,75.9
S01,sham,sham,7,37.47,25.21,0,44.4
S02,sham,sham,-1,37.18,24.96,0,36.6
S02,sham,sham,0,37.19,25.0,0,51.9
S02,sham,sham,1,36.68,24.88,0,51.8
S02,sham,sham,2,36.99,24.77,1,44.5
S02,sham,sham,3,36.7,24.65,1,66.5
S02,sham,sham,4,37.19,24.75,0,60.5
S02,sham,sham,5,37.07,24.98,1,50.0
S02,sham,sham,6,36.83,24.95,0,50.5
S02,sham,sham,7,37.26,24.67,0,38.2
```
