---
name: neurokit2
description: Use NeuroKit2 to build or audit reproducible research workflows for physiological time-series preprocessing, event/interval analysis, multimodal alignment, variability, and complexity. Trigger when code imports neurokit2 or needs its current APIs, schemas, and method-aware validation—not for diagnosis or device validation.
---

# NeuroKit2

## Scope and evidence cutoff

Use this skill for method-aware, reproducible biosignal research with NeuroKit2. The
snapshot was checked on **2026-07-23** against:

- stable PyPI **0.2.13**, released 2026-03-02;
- Python metadata (`>=3.10`; classifiers 3.10–3.14) and wheel dependencies;
- GitHub release notes/tags, `NEWS.rst`, source at tag `v0.2.13`;
- official API pages/examples (the live site identified itself as
  `0.2.13.dev214`); and
- pinned 0.2.13 runtime signatures and synthetic output schemas.

The live documentation can be ahead of the stable wheel. Prefer the pinned runtime
for reproducible work and name both versions if consulting development docs.

## Boundary

NeuroKit2 is a research and educational toolbox. Do **not** present its output as:

- a diagnosis, treatment recommendation, patient-monitoring decision, or alarm;
- validation, certification, or regulatory evidence for a medical device; or
- proof that a physiological construct is measured validly in a new sensor,
  protocol, environment, population, or disease group.

Validate acquisition hardware, electrode/optode placement, units, sampling and clock
accuracy, preprocessing, detector/decomposition method, population, task, and
outcomes for the intended study. Preserve raw data and an auditable exclusion log.
Use deidentified local files only; do not place PHI in prompts, logs, examples, or
bundled fixtures.

## Reproducible installation

```bash
uv pip install "neurokit2==0.2.13"
```

For optional features, create a uv project, add only the packages actually required at
reviewed exact versions, and commit/review the resulting `uv.lock` before
`uv sync --locked`. NeuroKit2 exposes an upstream `full` extra, but this skill
intentionally does not install that floating transitive set in an automated workflow.
Optional capabilities can require MNE, cvxopt, Plotly, PyEMD, pyRQA, Pillow, OpenCV,
or file readers. Record the resolved environment with the analysis. Provision any MNE
data/template download as an explicit, checksummed study input. Do not install a moving
development branch for a reproducible study.

## Required data contract

Before processing, record:

1. signal identity and sensor/channel configuration;
2. native sampling rate in Hz and physical unit (or explicitly `arbitrary_unit`);
3. clock, timestamp origin, drift correction, and synchronization evidence;
4. polarity/orientation and acquisition-side filters/gain;
5. missing samples, discontinuities, saturation, flatlines, motion, and annotations;
6. whether event onsets are zero-based sample indices or seconds;
7. planned preprocessing order, methods, parameters, exclusions, and outputs; and
8. participant-level grouping needed to prevent leakage in later statistics.

Never infer units from a column name. Do not silently treat samples as milliseconds,
volts, microsiemens, or arbitrary units.

## Core workflow

### 1. Inspect before transforming

```bash
python skills/neurokit2/scripts/inspect_signal.py \
  --input recording.csv --root . --deidentified \
  --columns ECG,RSP,EDA --time-column time_s \
  --units ECG=mV,RSP=a.u.,EDA=uS
```

The inspector is bounded and emits no row values or paths. Resolve non-monotonic time,
duplicate samples, gaps, non-finite values, flat runs, and sampling-rate disagreement
before filtering.

### 2. Preserve preprocessing order

Use this default reasoning order, adapting it to the acquisition and cited method:

1. preserve immutable raw signal and annotations;
2. verify time base, units, polarity, clipping, gaps, and artifacts;
3. segment at long gaps; only interpolate short gaps under a declared policy;
4. apply modality-specific cleaning at the native sampling rate;
5. detect peaks/onsets or decompose components;
6. inspect quality outputs and raw overlays;
7. correct peaks only with logged categories and sensitivity checks;
8. derive rates/features;
9. align continuous modalities on a declared common time grid; and
10. map event indices to that grid, epoch, baseline, and analyze.

Do not resample binary markers or peak-index arrays as ordinary continuous signals.
Map their timestamps to the target grid. Filtering and interpolation can create edge
artifacts and false precision; retain masks for padded, missing, and rejected regions.

### 3. Treat schemas as runtime observations

Return columns depend on NeuroKit2 version, function, method, signal availability, and
analysis mode. Never claim that one column list is universal.

```python
signals, info = nk.ecg_process(ecg, sampling_rate=250)
observed_schema = {
    "columns": list(signals.columns),
    "info_keys": sorted(info),
}
```

Persist the observed schema with package version, method parameters, sampling rate, and
quality/exclusion summary. Reference files list verified default schemas for 0.2.13,
not guarantees for every method.

## Current patterns

### ECG, corrected peaks, and duration-aware HRV

In stable 0.2.13, `ecg_process()` performs cleaning, R-peak detection with
`correct_artifacts=True`, rate, default `averageQRS` quality, DWT delineation, and phase.

```python
signals, info = nk.ecg_process(ecg, sampling_rate=250, method="neurokit")
time_hrv = nk.hrv_time(info, sampling_rate=250)
```

Inspect `ECG_R_Peaks_Uncorrected` and `ECG_fixpeaks_*`; a corrected series is not
automatically a valid NN series. For frequency/nonlinear HRV, enforce metric-specific
duration and beat-count requirements. Five minutes is the conventional short-term
reference; ULF is a long-recording measure, and VLF interpretation from short records
is unsafe. Do not interpret LF/HF as a direct sympathovagal balance. PPG pulse-rate
variability is not interchangeable with ECG HRV.

Use the bounded pipeline:

```bash
python skills/neurokit2/scripts/ecg_hrv_pipeline.py \
  --synthetic --sampling-rate 250 --duration 300 \
  --domains time,frequency,nonlinear
```

### EDA with explicit decomposition

The stable default `eda_process(method="neurokit")` uses high-pass tonic/phasic
decomposition, not cvxEDA. Choose and report decomposition explicitly:

```python
clean = nk.eda_clean(eda, sampling_rate=100, method="neurokit")
components = nk.eda_phasic(clean, sampling_rate=100, method="highpass")
markers, info = nk.eda_peaks(
    components["EDA_Phasic"],
    sampling_rate=100,
    method="neurokit",
    amplitude_min=0.1,
)
```

For `neurokit`/`kim2004`, `amplitude_min` is relative to the largest detected response;
it is not an absolute microsiemens threshold. cvxEDA needs optional `cvxopt`.

```bash
python skills/neurokit2/scripts/eda_pipeline.py \
  --synthetic --sampling-rate 100 --duration 60 \
  --phasic-method highpass --peak-method neurokit
```

### Events, epochs, and baseline

`events_find()` reports zero-based sample onsets; duration/spacing arguments are in
samples. `epochs_create()` takes epoch limits in seconds.

```python
events = nk.events_find(trigger, threshold=0.5, duration_min=2)
epochs = nk.epochs_create(
    signals,
    events,
    sampling_rate=100,
    epochs_start=-0.2,
    epochs_end=0.8,
    baseline_correction=False,
)
```

Plan sample-exact windows first:

```bash
python skills/neurokit2/scripts/plan_epochs.py \
  --events 1000,2500,4000 --event-unit samples \
  --sampling-rate 100 --recording-samples 5000 \
  --epoch-start -0.2 --epoch-end 0.8 \
  --baseline-start -0.2 --baseline-end 0
```

In 0.2.13 the epoch slice is end-exclusive, but the generated floating time index
includes `epochs_end`. Built-in baseline correction subtracts the epoch mean from its
start through `t=0`; use manual correction for a narrower prespecified baseline.
Boundary epochs are padded and can contain NaN. Decide drop/pad/error before analysis.

### RSA and multimodal processing

`bio_process()` assumes all inputs already share one sampling rate and alignment. It
does not resample, synchronize, estimate drift, or create nested modality dictionaries;
its `info` output is flat. Unequal lengths are concatenated by index and can introduce
NaN. RSA is added only when synchronized ECG and RSP are present.

Validate a strict local manifest before calling it:

```bash
python skills/neurokit2/scripts/validate_multimodal.py \
  --manifest streams.json --root . --deidentified
```

After independent modality QC and alignment:

```python
bio_signals, bio_info = nk.bio_process(
    ecg=ecg_aligned,
    rsp=rsp_aligned,
    eda=eda_aligned,
    sampling_rate=common_rate,
)
rsa_summary = nk.hrv_rsa(
    bio_signals,
    bio_signals,
    rpeaks=bio_info,
    sampling_rate=common_rate,
    continuous=False,
)
```

Summary RSA is a dictionary; `continuous=True` returns a DataFrame with `RSA_P2T` and
`RSA_Gates` in the verified default workflow. Co-record respiration and report its
rate/depth/context; RSA is not a direct, context-free measure of vagal tone.

### Complexity returns values plus metadata

Most complexity functions in 0.2.13 return `(value, info)`. The convenience function
also returns two objects:

```python
features, details = nk.complexity(signal)  # default which="makowski2022"
sampen, sampen_info = nk.entropy_sample(signal)
dfa, dfa_info = nk.fractal_dfa(signal)
```

The default convenience selection is not “all measures.” Complexity estimates are
sensitive to length, stationarity, normalization, delay, dimension, tolerance, scale,
and implementation. Predefine them and run sensitivity/surrogate analyses.

## Bundled command-line helpers

All helpers reject URLs, path traversal, and symlinks; bound bytes/rows/channels; refuse
overwrite unless `--force`; use lazy scientific imports so `--help` works without
NeuroKit2; never use pickle; and produce deterministic JSON/CSV. Real-data commands
require `--deidentified`.

| Helper | Purpose |
|---|---|
| `scripts/generate_synthetic.py` | Dependency-free deterministic CSV fixtures |
| `scripts/inspect_signal.py` | Bounded CSV/time/gap/flatline inspection |
| `scripts/ecg_hrv_pipeline.py` | Pinned ECG, quality, peak-correction, HRV workflow |
| `scripts/eda_pipeline.py` | Explicit cleaning, decomposition, SCR workflow |
| `scripts/plan_epochs.py` | Sample-exact event, boundary, baseline planner |
| `scripts/validate_multimodal.py` | Strict units/rates/clocks/alignment schema validator |

Generate a fixture without exposing participant data:

```bash
python skills/neurokit2/scripts/generate_synthetic.py \
  --output synthetic.csv --root . --duration 30 \
  --sampling-rate 250 --seed 42
```

## Security note

No example or helper uses Python `eval()` or `exec()`. NeuroKit2 names such as
`eeg_*`, `events_*`, and `*_eventrelated()` are ordinary library calls. If a static
scanner reports an eval/exec pattern based on a substring, inspect the exact line and
record it as a scanner false positive only after confirming no dynamic execution exists.

## References

Read only the files needed for the modality or decision:
All bundled Markdown paths below are under `references/`; this skill has no
`templates/` or `assets/` reference paths.

| File | Contents |
|---|---|
| `references/signal_processing.md` | Filters, gaps, resampling, peaks, PSD, schemas |
| `references/epochs_events.md` | Event indexing, epoch boundaries, baselines |
| `references/ecg_cardiac.md` | ECG process, quality, delineation, peak correction |
| `references/hrv.md` | HRV/RSA inputs, duration, ectopy, interpretation |
| `references/eda.md` | Cleaning, decomposition, SCR detection |
| `references/emg.md` | EMG cleaning, amplitude, activation |
| `references/eog.md` | EOG polarity, MNE default, blink features |
| `references/eeg.md` | EEG/MNE helpers, power, QC, microstates |
| `references/ppg.md` | PPG methods, quality semantics, PRV limitations |
| `references/rsp.md` | Respiration polarity, rate, RRV/RVT/RAV |
| `references/bio_module.md` | Multimodal alignment and `bio_*` schemas |
| `references/complexity.md` | Tuple returns, parameter sensitivity, RQA |

## Primary sources checked 2026-07-23

- [PyPI 0.2.13](https://pypi.org/project/neurokit2/)
- [Official documentation](https://neuropsychology.github.io/NeuroKit/)
- [API index](https://neuropsychology.github.io/NeuroKit/functions/index.html)
- [GitHub releases](https://github.com/neuropsychology/NeuroKit/releases)
- [Makowski et al. (2021), NeuroKit2](https://doi.org/10.3758/s13428-020-01516-y)
- [Pham et al. (2021), HRV tutorial](https://doi.org/10.3390/s21123998)
- [Makowski et al. (2022), complexity comparison](https://doi.org/10.3390/e24081036)
- [SPR guideline index](https://sprweb.org/guidelines-papers)
- [Quigley et al. (2024), HR/HRV guidelines](https://doi.org/10.1111/psyp.14604)

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/neurokit2/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/bio_module.md`

# Multimodal processing with `bio_process`

Checked **2026-07-23** against NeuroKit2 0.2.13 stable source/runtime
and the official Bio API/examples.

## What `bio_process()` does—and does not do

Stable signature:

```text
bio_process(
  ecg=None, rsp=None, eda=None, emg=None,
  ppg=None, eog=None, keep=None, sampling_rate=1000
)
```

It dispatches each non-`None` vector to the modality's `*_process()` function,
concatenates outputs by pandas index, adds `keep`, and computes continuous RSA when ECG
and RSP are both present.

It does **not**:

- infer or accept one native sampling rate per modality;
- synchronize clocks, estimate lag/drift, or align timestamps;
- automatically resample streams to `sampling_rate`;
- reject unequal lengths before concatenation;
- standardize units; or
- return a nested modality-info structure.

Passing ECG at 1000 Hz and EDA at 100 Hz with `sampling_rate=1000` falsely tells the
EDA processor that its samples are 1000 Hz. Unequal lengths are outer-concatenated by
index and can introduce NaN. Align first.

## Flat output schema

```python
bio_signals, bio_info = nk.bio_process(
    ecg=ecg_aligned,
    rsp=rsp_aligned,
    eda=eda_aligned,
    sampling_rate=100,
)
```

`bio_signals` is one wide DataFrame. With pinned synthetic ECG+RSP+EDA, it contained
43 columns:

- 19 ECG raw/clean/rate/quality/peaks/delineation/phase columns;
- 11 RSP raw/clean/amplitude/rate/RVT/phase/symmetry/extrema columns;
- 11 EDA raw/clean/tonic/phasic/SCR columns; and
- `RSA_P2T`, `RSA_Gates`.

`bio_info` is one flat dict built with repeated `dict.update()`. The pinned run
contained prefixed ECG/RSP/SCR keys, method metadata, and one `sampling_rate`; it did
not support:

```python
bio_info["ECG"]["ECG_R_Peaks"]  # wrong for stable 0.2.13
```

Use:

```python
rpeaks = bio_info["ECG_R_Peaks"]
rsp_troughs = bio_info["RSP_Troughs"]
```

Output columns depend on provided modalities, methods, optional dependencies, and
release. Save `list(bio_signals.columns)` and `sorted(bio_info)`.

## Alignment workflow

### 1. Preserve native clocks

For each stream record:

- timestamp origin/time zone or monotonic device time;
- native rate and observed timestamp intervals;
- dropped/duplicate/backward samples;
- clock reset, drift, and synchronization events;
- sensor latency and acquisition filters; and
- unit, polarity, and artifact mask.

Do not align only by truncating arrays to equal length.

### 2. Establish synchronization evidence

Prefer:

1. one acquisition system/shared clock;
2. common hardware trigger captured on each device;
3. validated timestamps with drift correction; or
4. a documented manual alignment with uncertainty.

Cross-correlation can support QC when signals share physiology, but a correlation peak
can be ambiguous and physiologically lagged. It is not a replacement for a clock.

### 3. Process at native rates

Apply modality-specific cleaning, peak detection, decomposition, and quality at the
correct native rate. Preserve native event/peak timestamps.

### 4. Build a common grid

Choose the target rate from the fastest retained continuous feature and analysis—not
convenience. Anti-alias downsampling; report interpolation/filter method and edge
validity. Map discrete peaks/triggers by time, using an explicit rounding/tolerance
policy; never spline binary markers.

### 5. Validate before `bio_process()`

The bundled validator accepts a strict JSON manifest:

```json
{
  "schema_version": "1.0",
  "streams": [
    {
      "name": "ECG",
      "path": "ecg.csv",
      "value_column": "ECG",
      "time_column": "time_s",
      "sampling_rate_hz": 250,
      "unit": "mV"
    },
    {
      "name": "RSP",
      "path": "rsp.csv",
      "value_column": "RSP",
      "time_column": "time_s",
      "sampling_rate_hz": 50,
      "unit": "a.u."
    }
  ],
  "alignment": {
    "reference_stream": "ECG",
    "synchronization": "shared_clock",
    "max_start_offset_ms": 2,
    "minimum_overlap_s": 60
  }
}
```

```bash
python skills/neurokit2/scripts/validate_multimodal.py \
  --manifest streams.json --root . --deidentified
```

The validator reports units, rates, timestamp order/jitter, missingness, starts, common
overlap, and whether streams can be passed directly to `bio_process()`. It does not
resample or modify data.

## `keep`

`keep` must be a pandas Series or DataFrame and is concatenated after processed
modalities. It is useful for a pre-aligned trigger or covariate:

```python
bio_signals, bio_info = nk.bio_process(
    ecg=ecg,
    rsp=rsp,
    keep=aligned[["Trigger"]],
    sampling_rate=100,
)
```

Verify equal index/length first. Do not use `keep` for participant identifiers or PHI.

## EOG and optional dependencies

The high-level Bio wrapper calls `eog_process()` without exposing an EOG method.
Stable EOG peak detection defaults to MNE, which is optional. A core-only environment
can therefore fail when `eog` is supplied. Process EOG explicitly with a chosen method
and merge after alignment, or add MNE at a reviewed exact version to the project lock.

## RSA

When both ECG and RSP are present, stable `bio_process()` adds continuous:

```text
RSA_P2T, RSA_Gates
```

This assumes the arrays already represent synchronized samples at the supplied rate.
It does not check respiration polarity, sensor lag, clock drift, or R-peak validity.
For summary RSA:

```python
rsa = nk.hrv_rsa(
    bio_signals,
    bio_signals,
    rpeaks=bio_info,
    sampling_rate=100,
    continuous=False,
)
```

Report the RSA method/output family, respiration behavior, usable cycles/windows, and
alignment uncertainty. See `hrv.md`.

## `bio_analyze()`

```text
bio_analyze(
  data, sampling_rate=1000, method="auto",
  window_lengths="constant"
)
```

It detects available column prefixes and joins modality-specific analysis. With
interval-related data it can add summary RSA. `method="auto"` uses event-related mode
when mean duration is under 10 seconds; use explicit `event-related` or
`interval-related` for a prespecified design.

`window_lengths` can assign different epoch subwindows by modality. Prespecify them;
choosing each window after seeing effects multiplies researcher degrees of freedom.

There is no generic “multimodal arousal,” coherence, or cardiorespiratory-coupling
score automatically produced by this wrapper. Any custom cross-modal statistic needs
its own synchronization, lag, stationarity, null model, and multiplicity analysis.

## Missingness and statistics

- Keep one validity/artifact mask per modality; complete-case intersection can remove
  large or condition-dependent periods.
- Do not replace a poor modality with another and claim the same construct.
- Summarize quality/exclusions by participant and condition.
- Split train/test/validation by participant, not rows or epochs.
- Avoid pseudo-replication from dense samples.
- Predefine cross-modal features and correct multiplicity.

## Interpretation boundary

Multimodal convergence does not prove a latent state, diagnosis, or causal mechanism.
Use `bio_*` for research/education only—not patient, worker, driver, athlete, or device
monitoring and not medical-device validation.

## Sources checked 2026-07-23

- [Official Bio API](https://neuropsychology.github.io/NeuroKit/functions/bio.html)
- [Official custom Bio example](https://neuropsychology.github.io/NeuroKit/examples/bio_custom/bio_custom.html)
- [Stable v0.2.13 `bio_process` source](https://github.com/neuropsychology/NeuroKit/blob/v0.2.13/neurokit2/bio/bio_process.py)
- [NeuroKit2 main paper](https://doi.org/10.3758/s13428-020-01516-y)
- [Grossman & Taylor (2007), RSA interpretation](https://doi.org/10.1016/j.biopsycho.2005.11.014)

### `references/complexity.md`

# Complexity, entropy, fractals, and RQA

Checked **2026-07-23** against NeuroKit2 0.2.13 stable runtime/source,
the official Complexity API, and the NeuroKit2 complexity comparison paper.

## Return convention changed from older examples

Most stable 0.2.13 complexity functions return:

```python
value, info = function(signal, ...)
```

Examples:

```python
sampen, sampen_info = nk.entropy_sample(
    signal, delay=1, dimension=2, tolerance="sd"
)
dfa, dfa_info = nk.fractal_dfa(signal)
hfd, hfd_info = nk.fractal_higuchi(signal, k_max=10)
lyapunov, lyapunov_info = nk.complexity_lyapunov(signal)
fi, fi_info = nk.fisher_information(signal)
```

Do not treat the tuple as a scalar. The current public name is
`fisher_information()`; `information_fisher()` is not exported.

Exceptions exist: for example, `mutual_information()` returns a float. Check the
stable signature and persist runtime type/schema.

## `complexity()` is a selected panel

```python
features, details = nk.complexity(
    signal,
    which="makowski2022",
    delay=1,
    dimension=2,
    tolerance="sd",
)
```

The default does not compute “all complexity measures.” The pinned 0.2.13 probe
returned a one-row DataFrame with 15 columns:

```text
AttEn, BubbEn, CWPEn, Hjorth, LL,
MFDFA_Asymmetry, MFDFA_Delta, MFDFA_Fluctuation,
MFDFA_Increment, MFDFA_Max, MFDFA_Mean,
MFDFA_Peak, MFDFA_Width, MSPEn, SVDEn
```

The accompanying dict had method-specific details. This panel reflects a published
empirical comparison and implementation choices; it is not a universal optimum for
every signal, endpoint, or population.

## Parameter selection

Phase-space/entropy estimates depend on:

- delay (`tau`);
- embedding dimension (`m`);
- tolerance/radius (`r`);
- scale/coarse-graining;
- symbolization/binning;
- detrending/integration/order;
- sampling rate and bandwidth; and
- usable length and stationarity.

Stable utilities also return metadata:

```python
delay, delay_info = nk.complexity_delay(
    signal, delay_max=100, method="fraser1986", show=False
)
dimension, dimension_info = nk.complexity_dimension(
    signal, delay=delay, dimension_max=10, method="afnn", show=False
)
tolerance, tolerance_info = nk.complexity_tolerance(
    signal,
    method="maxApEn",
    delay=delay,
    dimension=dimension,
    show=False,
)
```

Optimization can return no solution or raise when search bounds are inadequate. Do not
silently replace failure with an arbitrary default. Predefine the algorithm/search
range, report failures, and test sensitivity.

`tolerance="sd"` commonly maps to a fraction of standard deviation, but amplitude
normalization, outliers, and signal length alter it. One conventional parameter set is
not method validation.

## Major stable families

### Entropy

Available functions include approximate, sample, fuzzy, permutation, spectral,
multiscale, dispersion, symbolic-dynamic, SVD, Shannon, Rényi, Tsallis, and other
variants.

Pinned probes confirmed `(value, info)` for:

- `entropy_approximate()`;
- `entropy_sample()`;
- `entropy_multiscale()`;
- `entropy_permutation()`; and
- `entropy_spectral()`.

Some values are corrected/normalized by default (for example corrected permutation
entropy). Record every parameter and logarithm base. Entropy values from different
algorithms/normalizations are not interchangeable.

### Fractals

Stable functions include Katz, Higuchi, Petrosian, Sevcik, NLD, PSD slope, Hurst,
correlation dimension, DFA/MFDFA, density, line length, and tMF.

`fractal_dfa()` returns `(float, info)` for monofractal mode and can return a
DataFrame-like multifractal summary. Report scales, overlap, integration, detrending
order, q values, and fit diagnostics. Do not interpret alpha values without checking
which regime and preprocessing generated them.

### Lyapunov and RQA

```python
lle, lle_info = nk.complexity_lyapunov(
    signal,
    delay=1,
    dimension=2,
    method="rosenstein1993",
    separation="auto",
)
rqa, rqa_info = nk.complexity_rqa(
    signal,
    dimension=3,
    delay=1,
    tolerance="sd",
    method="python",
)
```

The pinned RQA DataFrame had fields such as `RecurrenceRate`, `Determinism`,
`Laminarity`, `TrappingTime`, line-length/entropy, divergence, and vertical/white-line
statistics. `rqa_info` included full recurrence and distance matrices, which scale
quadratically in signal length. Bound input length and memory.

A positive estimated Lyapunov exponent does not by itself prove deterministic chaos.
RQA results depend strongly on embedding, tolerance, norm, Theiler window, line
thresholds, nonstationarity, and sample size.

## Signal preparation

1. Preserve raw signal and physical unit.
2. Apply modality-specific artifact/missing-data policy first.
3. Define the analysis window and usable length.
4. Decide detrending, filtering, resampling, and standardization before viewing group
   effects.
5. Check stationarity or segment according to the estimand.
6. Compute prespecified measures and diagnostics.
7. Compare with surrogates/nulls and parameter sensitivity.

Do not apply blanket z-scoring: amplitude-sensitive measures may change, while scale
invariant measures may not. Report both rationale and implementation.

## Length and comparability

There is no universal minimum sample count across complexity measures. Required length
grows with embedding dimension, delay, scale count, tolerance, and estimator. Multiscale
entropy loses points at each coarse-graining scale; RQA and correlation dimension can
be computationally and statistically unstable on short data.

- Use equal-duration/beat-count windows for direct comparisons unless a validated
  correction is used.
- Quantify estimate reliability with simulation/resampling.
- Avoid comparing measures computed at different sample rates or bandwidths without
  explicit validation.
- Return missing/unsupported rather than a numerically convenient but invalid value.

## Interpretation

High entropy can mean noise, not useful complexity. “Healthy complexity,” “complexity
loss,” consciousness, disease, stress, and aging claims require a prespecified theory,
validated acquisition/preprocessing, appropriate controls, and independent evidence.

Do not use these measures for diagnosis, anesthesia/consciousness monitoring, seizure
detection, prognosis, or medical-device validation based on this toolbox alone.

## Reproducible report

Record:

- NeuroKit2 version and function return schema;
- signal type/unit/rate/bandwidth/window/length;
- exclusions, interpolation, filtering, detrending, resampling, normalization;
- algorithm, delay, dimension, tolerance, scales/bins/q/order;
- optimization method/search space and failures;
- fit/convergence diagnostics and runtime warnings;
- surrogate/null and sensitivity results; and
- multiplicity control and participant-level statistical design.

## Sources checked 2026-07-23

- [Official Complexity API](https://neuropsychology.github.io/NeuroKit/functions/complexity.html)
- [Stable v0.2.13 complexity source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/complexity)
- [Makowski et al. (2022), empirical comparison using NeuroKit2](https://doi.org/10.3390/e24081036)
- [Richman & Moorman (2000), sample entropy](https://doi.org/10.1152/ajpheart.2000.278.6.H2039)
- [Peng et al. (1995), DFA](https://doi.org/10.1063/1.166141)
- [Costa et al. (2005), multiscale entropy](https://doi.org/10.1103/PhysRevE.71.021906)

### `references/ecg_cardiac.md`

# ECG and cardiac processing

Checked **2026-07-23** against NeuroKit2 0.2.13 stable source/runtime,
the live ECG API, and current psychophysiology measurement guidance.

## Acquisition contract

Record lead/configuration, electrode placement, reference/ground, hardware gain and
filters, ADC resolution/range, physical unit, native sampling rate, timestamp clock,
posture/task, medication and relevant population variables, and artifact annotations.
Do not infer millivolts from a column named `ECG`.

Sampling must support the intended endpoint. Rate/R-peak timing and P–QRS–T morphology
have different bandwidth and precision needs. Psychophysiology guidance commonly uses
at least 125 Hz and regards 500 Hz as conservative for HRV timing, but this is not a
universal validation threshold. Validate the complete acquisition and detector on
representative signals; morphology/delineation often uses 250–1000 Hz.

## `ecg_process()` in stable 0.2.13

```python
signals, info = nk.ecg_process(
    ecg,
    sampling_rate=250,
    method="neurokit",
)
```

The stable source performs:

1. `signal_sanitize()` (index reset only);
2. `ecg_clean()` with the selected method;
3. `ecg_peaks(..., correct_artifacts=True)`;
4. interpolated rate;
5. default `ecg_quality(..., method="averageQRS")`;
6. DWT delineation; and
7. atrial/ventricular phase.

The pinned default probe observed these 19 columns:

```text
ECG_Raw, ECG_Clean, ECG_Rate, ECG_Quality, ECG_R_Peaks,
ECG_P_Peaks, ECG_P_Onsets, ECG_P_Offsets, ECG_Q_Peaks,
ECG_R_Onsets, ECG_R_Offsets, ECG_S_Peaks, ECG_T_Peaks,
ECG_T_Onsets, ECG_T_Offsets, ECG_Phase_Atrial,
ECG_Phase_Completion_Atrial, ECG_Phase_Ventricular,
ECG_Phase_Completion_Ventricular
```

This is a verified default schema, not a universal promise. Persist
`list(signals.columns)` and `sorted(info)`.

`info` is a flat dict. In the default pinned run it included corrected and uncorrected
R-peaks, `ECG_fixpeaks_*` diagnostics, sampling rate, methods, and delineated wave
indices. It is not nested under an `ECG` key.

## Cleaning and R-peak methods

High-level methods documented for `ecg_process()` include `neurokit`,
`pantompkins1985`, `hamilton2002`, `elgendi2010`, and `engzeemod2012`.
`ecg_clean()` and lower-level peak detection expose additional methods. A cleaning
method and detector encode different assumptions; do not select whichever produces
the expected group effect.

For custom control:

```python
clean = nk.ecg_clean(ecg, sampling_rate=250, method="neurokit")
markers, peak_info = nk.ecg_peaks(
    clean,
    sampling_rate=250,
    method="neurokit",
    correct_artifacts=False,
)
```

Validate:

- R-peak precision, false positives, missed beats, and ectopy;
- performance during motion, changing rate, and low-amplitude QRS;
- lead polarity and possible inversion;
- filter edge regions and discontinuities; and
- failure modes by participant, condition, device, and population.

## Peak correction

`ecg_process()` always requests Lipponen–Tarvainen correction in 0.2.13. Inspect:

```python
uncorrected = info["ECG_R_Peaks_Uncorrected"]
corrected = info["ECG_R_Peaks"]
categories = {
    key: info.get(f"ECG_fixpeaks_{key}", [])
    for key in ["ectopic", "missed", "extra", "longshort"]
}
```

Correction can improve a tachogram but can also alter HRV. Report corrected proportions,
categories, thresholds/method, excluded segments, and sensitivity with uncorrected or
alternative policies. Do not assume an algorithm can distinguish ectopic from erroneous
detection without waveform review or appropriate labels.

## ECG quality is method-dependent

```python
quality = nk.ecg_quality(
    clean,
    rpeaks=peak_info["ECG_R_Peaks"],
    sampling_rate=250,
    method="averageQRS",
)
```

Stable options include `averageQRS`, `templatematch`, `zhao2018`,
`dissimilarity`, and `ho2025`.

- `averageQRS`: continuous array scaled 0–1 by this implementation.
- `templatematch`: continuous morphology-template correlation; it is relative to the
  recording.
- `zhao2018`: one classification string (`Unacceptable`, `Barely acceptable`, or
  `Excellent`).
- `dissimilarity`: direction/scale differs from similarity scores.
- `ho2025`: beat/interval-oriented quality based on detector agreement.

There is no universal `>0.6` acceptance rule across these methods. A quality output is
not device validation. Define thresholds on independent labeled data and preserve the
method name and scale.

## Delineation return order

```python
delineation_signals, waves = nk.ecg_delineate(
    clean,
    rpeaks=peak_info["ECG_R_Peaks"],
    sampling_rate=250,
    method="dwt",
)
```

The first object is a same-length marker DataFrame; the second is a dict of wave sample
indices. Stable methods include `peak`, `prominence`, `cwt`, and `dwt`. Missing wave
indices may be NaN. Validate every wave endpoint needed for an interval/morphology
claim; R-peak accuracy does not validate P/T delineation.

## Phase and event-related analysis

`ECG_Phase_Atrial` and `ECG_Phase_Ventricular` are binary phase labels;
completion columns are fractions from 0 to 1. Their validity depends on delineation.
For cardiac-locked stimuli, characterize trigger latency/jitter independently of
software phase estimates.

`ecg_eventrelated()` and `ecg_intervalrelated()` inspect available columns. Their output
columns are conditional. Use explicit dispatch and save observed columns:

```python
features = nk.ecg_analyze(
    epochs,
    sampling_rate=250,
    method="event-related",
)
```

## ECG-derived respiration

`ecg_rsp()` takes a heart-rate series, not raw/clean ECG:

```python
edr = nk.ecg_rsp(signals["ECG_Rate"], sampling_rate=250, method="vangent2019")
```

EDR is a proxy and depends on ECG morphology/rate modulation. It is not interchangeable
with a calibrated respiration sensor for RSA, tidal volume, or respiratory diagnosis.

## Bounded pipeline

```bash
python skills/neurokit2/scripts/ecg_hrv_pipeline.py \
  --input deidentified.csv --column ECG --root . --deidentified \
  --sampling-rate 250 --method neurokit --domains time \
  --signals-output ecg_processed.csv --output ecg_report.json
```

The helper rejects missing/non-finite samples instead of silently interpolating them,
reports observed schemas and correction categories, and gates longer HRV domains.

## Sources checked 2026-07-23

- [Official ECG API](https://neuropsychology.github.io/NeuroKit/functions/ecg.html)
- [Stable v0.2.13 `ecg_process` source](https://github.com/neuropsychology/NeuroKit/blob/v0.2.13/neurokit2/ecg/ecg_process.py)
- [Quigley et al. (2024), HR/HRV measurement guidelines](https://doi.org/10.1111/psyp.14604)
- [Laborde et al. (2017), HRV planning/reporting](https://doi.org/10.3389/fpsyg.2017.00213)
- [Lipponen & Tarvainen (2019), correction algorithm](https://doi.org/10.1080/03091902.2019.1640306)
- [Pan & Tompkins (1985)](https://doi.org/10.1109/TBME.1985.325532)

### `references/eda.md`

# Electrodermal activity

Checked **2026-07-23** against NeuroKit2 0.2.13 stable runtime/source,
the official EDA API/examples, and Society for Psychophysiological Research guidance.

## Measurement contract

Record:

- conductance versus resistance, physical unit, range, and calibration;
- constant-voltage/current system and electrode material/area;
- palmar/plantar or other site, laterality, placement, and skin preparation;
- sampling rate, hardware filters, temperature, humidity, acclimation, and movement;
- missing/detached/saturated intervals; and
- participant/task factors and response definition.

Do not infer microsiemens from `EDA` or compare arbitrary sensor units with published
µS thresholds. Sensor site, hardware, environment, and population require validation.

## Default stable pipeline

```python
signals, info = nk.eda_process(
    eda,
    sampling_rate=100,
    method="neurokit",
)
```

In stable 0.2.13 the NeuroKit pipeline performs cleaning, **high-pass**
tonic/phasic decomposition, and NeuroKit SCR detection. It does not use cvxEDA by
default.

The pinned default schema observed:

```text
EDA_Raw, EDA_Clean, EDA_Tonic, EDA_Phasic,
SCR_Onsets, SCR_Peaks, SCR_Height, SCR_Amplitude,
SCR_RiseTime, SCR_Recovery, SCR_RecoveryTime
```

`info` was a flat dict containing SCR arrays plus `sampling_rate`. Treat this as a
default 0.2.13 observation, not a universal schema.

There is no public `eda_quality()` in stable 0.2.13. Quality must combine acquisition
metadata, missing/flat/clipped/motion checks, raw/clean overlays, decomposition
plausibility, and response review.

## Make decomposition explicit

```python
clean = nk.eda_clean(eda, sampling_rate=100, method="neurokit")
components = nk.eda_phasic(
    clean,
    sampling_rate=100,
    method="highpass",
)
```

`eda_clean()` options include `neurokit`, `biosppy`, and `none`. The NeuroKit path
uses a 3 Hz low-pass, and skips it below 7 Hz.

`eda_phasic()` returns a DataFrame with `EDA_Tonic` and `EDA_Phasic`. Methods include:

- `highpass`: default stable method; phasic high-pass separation;
- `smoothmedian`: median-smoothed tonic estimate;
- `cvxeda`: convex optimization; needs optional `cvxopt`;
- `sparseda`: sparse decomposition.

These methods estimate different latent components and are not interchangeable.
Report method, all kwargs, optional dependency versions, convergence/failure behavior,
and sensitivity. Do not call one decomposition “physiologically true” without
appropriate validation.

## SCR detection

```python
markers, peak_info = nk.eda_peaks(
    components["EDA_Phasic"],
    sampling_rate=100,
    method="neurokit",
    amplitude_min=0.1,
)
```

Stable methods include `neurokit`, `gamboa2008`, `kim2004`, `vanhalem2020`, and
`nabian2018`. For `neurokit` and `kim2004`, `amplitude_min` is a fraction relative to
the largest amplitude in the analyzed signal—not an absolute µS threshold.

`eda_peaks()` returns `(signals, info)`:

- marker/feature DataFrame: `SCR_Onsets`, `SCR_Peaks`, `SCR_Height`,
  `SCR_Amplitude`, `SCR_RiseTime`, `SCR_Recovery`, `SCR_RecoveryTime`;
- info dict: event-indexed arrays and sampling rate.

Marker columns are same-length arrays; feature values are placed at relevant marker
locations and are otherwise missing. Use `info` for event-level arrays. Do not average
same-length feature columns as if every sample were an independent response.

`eda_fixpeaks()` is documented as a placeholder that does not currently correct EDA
peaks.

## Missingness and artifacts

EDA motion/electrode artifacts can resemble fast responses, while detachment can look
flat. Before decomposition:

1. inspect raw units, range, clipping, steps, flatlines, and missing runs;
2. segment long discontinuities;
3. annotate motion, temperature changes, and contact problems;
4. avoid broad interpolation across SCR morphology; and
5. keep an artifact/validity mask through epoching.

Filtering cannot restore a detached or saturated channel. A low response count can be
physiological, methodological, or a sensor failure; it is not automatically a
“non-responder.”

## Event-related EDA

Create epochs only after event and signal clocks are aligned:

```python
epochs = nk.epochs_create(
    signals,
    events,
    sampling_rate=100,
    epochs_start=-1,
    epochs_end=10,
    baseline_correction=False,
)
features = nk.eda_eventrelated(epochs)
```

Stable event-related output is conditional on available columns. Documented features
include `EDA_SCR`, first-response amplitude/time/rise/recovery fields, tonic/phasic
summaries, labels, conditions, and event onset. Inspect `features.columns`.

Prespecify response latency/window, overlap handling, baseline approach, minimum
amplitude definition, non-response coding, and trial artifact rules. Slow responses can
overlap adjacent events; a peak in a window is not automatically elicited by that event.

## Interval analysis and sympathetic index

```python
features = nk.eda_intervalrelated(signals, sampling_rate=100)
```

The pinned official example showed six columns, including SCR count/amplitude,
`EDA_Tonic_SD`, `EDA_Sympathetic`, `EDA_SympatheticN`, and
`EDA_Autocorrelation`; output depends on duration and available columns.

`eda_sympathetic()` supports `posada` and `ghiasi`, with a default 0.045–0.25 Hz
band. The implementation/documentation uses at least 64 seconds to support the spectral
estimate. Report exact usable duration, frequency band, estimator, normalization, and
units. Do not turn this index into a direct clinical sympathetic-state measure.

## Bounded pipeline

```bash
python skills/neurokit2/scripts/eda_pipeline.py \
  --input deidentified.csv --column EDA --root . --deidentified \
  --sampling-rate 100 --unit uS \
  --clean-method neurokit --phasic-method highpass \
  --peak-method neurokit --amplitude-min 0.1
```

The helper rejects missing/non-finite samples, records the observed schema, and makes
decomposition/threshold semantics explicit.

## Interpretation boundary

EDA indexes eccrine sweat-gland activity under the recording conditions. It does not
uniquely identify stress, emotion, deception, pain, diagnosis, or intent. Compare
within a theory-driven design with contextual measures and validated preprocessing.
Do not use this workflow for clinical/driver/workplace monitoring or medical-device
validation.

## Sources checked 2026-07-23

- [Official EDA API](https://neuropsychology.github.io/NeuroKit/functions/eda.html)
- [Official SCR example](https://neuropsychology.github.io/NeuroKit/examples/eda_peaks/eda_peaks.html)
- [Stable v0.2.13 EDA source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/eda)
- [SPR Ad Hoc Committee (2012), publication recommendations](https://doi.org/10.1111/j.1469-8986.2012.01384.x)
- [Greco et al. (2016), cvxEDA](https://doi.org/10.1109/TBME.2015.2474131)
- [NeuroKit2 main paper](https://doi.org/10.3758/s13428-020-01516-y)

### `references/eeg.md`

# EEG and microstates

Checked **2026-07-23** against NeuroKit2 0.2.13 stable source/runtime,
the official EEG/microstate APIs, and SPR EEG/MEG guidance.

## Scope

NeuroKit2 does not expose an `eeg_process()` equivalent to its ECG/EDA pipelines.
It provides selected feature, QC, re-reference, MNE, source, and microstate helpers.
Use MNE or another validated EEG framework for the full acquisition/preprocessing
workflow, while recording every transform and bad-segment decision.

For NumPy input, NeuroKit2 EEG functions expect shape:

```text
(channels, time_samples)
```

Do not pass `(time, channels)` silently. Preserve channel names/order, montage,
reference, sensor locations, units (typically volts in MNE), sampling rate, and bad
channel/segment annotations.

## Current stable helpers

### Power

```python
power = nk.eeg_power(
    eeg_channels_by_time,
    sampling_rate=250,
    frequency_band=["Gamma", "Beta", "Alpha", "Theta", "Delta"],
)
```

The argument is singular `frequency_band`, not `frequency_bands`. The pinned default
array probe returned one row per channel with:

```text
Channel, Gamma, Beta, Alpha, Theta, Delta
```

Standard named bands in the docs include Delta 1–4, Theta 4–8, Alpha 8–13, Beta
13–30, and Gamma 30–80 Hz, with additional sub-bands. Band definitions are conventions,
not universal physiology. Report exact boundaries, PSD parameters, reference, artifact
handling, absolute/relative normalization, and usable duration.

### Bad channels

```python
bads, channel_info = nk.eeg_badchannels(
    eeg_channels_by_time,
    bad_threshold=0.5,
    distance_threshold=0.99,
    show=False,
)
```

Return order is a list plus a DataFrame. The pinned info schema contained `SD`, `Mean`,
`MAD`, `Median`, `Skewness`, `Kurtosis`, `Amplitude`, interval bounds,
`n_ZeroCrossings`, and `Bad`.

This statistical screen is not a universal rejection rule. Review raw data, montage,
bridging, line noise, drift, channel location, task, and condition. Fit thresholds
without leaking group/condition outcomes.

### Re-reference, GFP, and dissimilarity

```python
rereferenced = nk.eeg_rereference(eeg_channels_by_time, reference="average")
gfp = nk.eeg_gfp(rereferenced, method="l1")
diss = nk.eeg_diss(rereferenced, gfp=gfp)
```

For array input `eeg_rereference()` returns an array. For MNE input it returns an MNE
object. Average reference requires adequate channel coverage and bad-channel handling;
it is not automatically appropriate for sparse montages.

`eeg_gfp()` defaults to L1 in NeuroKit2, while publications may use other definitions.
Report method, standardization, normalization, smoothing, and reference.

## Optional MNE requirements

Core NeuroKit2 does not install MNE. Stable functions that require it include:

- `eeg_simulate()` (confirmed by pinned runtime);
- `mne_data()` and MNE object helpers;
- `eeg_source()` / `eeg_source_extract()`; and
- `mne_templateMRI()`.

Add only the optional package(s) required for the analysis at reviewed exact versions,
commit/review the resulting `uv.lock`, and install with `uv sync --locked`. Do not
install the upstream floating `full` extra in an automated workflow without such a
lock.

Some MNE helpers download datasets/templates. Treat network access, cache paths,
licenses, versions, and checksums as study dependencies; do not use them in a
restricted/offline workflow without prior provisioning.

## Source reconstruction

Stable signature:

```text
eeg_source(raw, src, bem, method="sLORETA", show=False, ...)
```

It requires an MNE Raw object, source space, BEM/head model, montage/electrode
locations, and appropriate co-registration. `eeg_source_extract(stc, src, ...)` returns
region time series from a segmentation.

A template MRI does not validate localization for an individual or population.
Report coordinate frames, digitization, head/conductivity model, inverse method,
regularization, noise covariance, depth/orientation choices, atlas, and uncertainty.
Do not use NeuroKit2 source estimates for diagnosis, surgical planning, or clinical
localization.

## Microstates

### Segmentation

```python
out = nk.microstates_segment(
    eeg_channels_by_time,
    n_microstates=4,
    train="gfp",
    method="kmod",
    sampling_rate=250,
    n_runs=50,
    random_state=42,
)
```

Stable methods include `kmod`, `kmeans`, `kmedoids`, `pca`, `ica`, and `aahc`.
The pinned 0.2.13 output dict included:

```text
Microstates, Sequence, GEV, GEV_per_microstate, GFP,
Polarity, Info, Info_algorithm
```

It did **not** use lowercase `maps`, `labels`, `gfp`, or `gev`. `Microstates` contains
maps, and `Sequence` is the sample-wise class assignment.

### Preparation and summaries

```python
clean, train_indices, gfp, input_info = nk.microstates_clean(
    eeg_channels_by_time,
    sampling_rate=250,
    train="gfp",
)

static = nk.microstates_static(out["Sequence"], sampling_rate=250)
dynamic = nk.microstates_dynamic(out["Sequence"])
```

`microstates_clean()` is a utility for array normalization/standardization and training
sample selection; it does not implement a full EEG artifact pipeline.

`microstates_classify()` is experimental and requires two arguments:

```python
sequence, maps = nk.microstates_classify(
    out["Sequence"],
    out["Microstates"],
)
```

Its classification depends on channel ordering, so it is not a reliable substitute for
template matching with a defined montage.

`microstates_findnumber()` returns `(optimal_number, scores_dataframe)`. Choosing a
state count from the same dataset and then testing selected-state effects can inflate
research flexibility. Prespecify or cross-validate clustering choices and assess
initialization stability.

## Preprocessing/reporting

At minimum report:

- hardware, montage/locations/reference/ground, unit, sample rate, online filters;
- resampling, offline filters/notches, edge handling, and line frequency;
- bad channels/segments and interpolation;
- ocular/muscle/cardiac correction and ICA details;
- epoch/baseline definitions and retained trials;
- PSD/time-frequency estimator and normalization;
- microstate input band/reference, GFP definition, training points, algorithm,
  state count, runs/seed, polarity, smoothing, and fit/stability; and
- exact NeuroKit2/MNE versions and observed schemas.

Avoid frequency-band mental-state labels such as “beta = anxiety” or
“theta/beta = ADHD.” EEG features are not diagnosis, consciousness monitoring,
anesthesia control, seizure detection, or neurofeedback validation without a separate
validated system and intended-use evidence.

## Sources checked 2026-07-23

- [Official EEG API](https://neuropsychology.github.io/NeuroKit/functions/eeg.html)
- [Official microstates API](https://neuropsychology.github.io/NeuroKit/functions/microstates.html)
- [Stable v0.2.13 EEG source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/eeg)
- [Stable v0.2.13 microstates source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/microstates)
- [Keil et al. (2014), EEG/MEG publication guidelines](https://doi.org/10.1111/psyp.12147)
- [Keil et al. (2022), frequency/time-frequency guidelines](https://doi.org/10.1111/psyp.14052)
- [Michel & Koenig (2018), microstate review](https://doi.org/10.1016/j.neuroimage.2017.11.062)

### `references/emg.md`

# Electromyography

Checked **2026-07-23** against NeuroKit2 0.2.13 stable runtime/source,
the official EMG API, and human surface-EMG guidance.

## Acquisition contract

Record muscle and task, electrode type/size/orientation/inter-electrode distance,
reference, skin preparation, amplifier gain/range, hardware filters, unit, sampling
rate, synchronization, posture/contraction, and artifact annotations. Follow a
muscle-specific placement protocol such as SENIAM when applicable.

EMG amplitude depends on geometry, subcutaneous tissue, cross-talk, electrode contact,
hardware, and contraction history. It is not a direct universal force scale.

## Stable processing pipeline

```python
signals, info = nk.emg_process(emg, sampling_rate=1000)
```

Pinned 0.2.13 default columns:

```text
EMG_Raw, EMG_Clean, EMG_Amplitude,
EMG_Activity, EMG_Onsets, EMG_Offsets
```

`info` contained event-level `EMG_Activity`, `EMG_Onsets`, `EMG_Offsets`, and
`sampling_rate`. This is a default observation, not a universal schema.

## Cleaning and amplitude

```python
clean = nk.emg_clean(emg, sampling_rate=1000, method="biosppy")
amplitude = nk.emg_amplitude(clean)
```

Important stable details:

- `emg_clean()` currently offers `biosppy` and `none`.
- The BioSPPy path uses a fourth-order 100 Hz high-pass Butterworth filter followed by
  constant detrending.
- `emg_amplitude()` takes only the cleaned vector; it has no `sampling_rate` argument
  in 0.2.13.

A 100 Hz high-pass may be unsuitable for some surface-EMG endpoints and impossible at
low sampling rates. Do not treat the package default as a universal acquisition
standard. Set sampling rate above twice the highest retained frequency with transition
band margin; surface EMG is commonly acquired around 1000–2000 Hz, but the study,
hardware, muscle, and endpoint determine requirements.

## Activation detection

Stable signature:

```text
emg_activation(
  emg_amplitude=None, emg_cleaned=None, sampling_rate=1000,
  method="threshold", threshold="default", duration_min="default",
  size=None, threshold_size=None, **kwargs
)
```

Use the correct input for the method:

- `threshold` or `mixture`: pass `emg_amplitude`;
- `pelt`, `biosppy`, or `silva`: pass `emg_cleaned`.

```python
activity_signals, activity_info = nk.emg_activation(
    emg_amplitude=amplitude,
    sampling_rate=1000,
    method="threshold",
    threshold="default",
    duration_min=0.05,
)
```

Return order is `(activity_signals, info)`. The DataFrame has same-length
`EMG_Activity`, `EMG_Onsets`, and `EMG_Offsets`; the dict contains event indices.
`duration_min` is seconds. `size` semantics are method-specific.

Automatic thresholds are hypotheses, not ground truth. Tune/validate on independent
labeled contractions or a prespecified baseline. Report threshold, window, smoothing,
minimum duration, and false/missed activation performance.

## Missing data and artifacts

Inspect and annotate:

- clipping/saturation and disconnected/flat channels;
- motion/cable artifacts and low-frequency transients;
- powerline interference;
- ECG contamination, especially trunk/proximal sites;
- cross-talk from adjacent muscles; and
- baseline changes from contact/sweat.

Do not interpolate across a burst or activation onset. Segment long gaps, preserve a
validity mask, and reject affected trials/windows under prespecified rules. Filtering
cannot establish that a deflection came from the target muscle.

## Event and interval features

```python
epochs = nk.epochs_create(
    signals,
    events,
    sampling_rate=1000,
    epochs_start=-0.1,
    epochs_end=1.0,
    baseline_correction=False,
)
event_features = nk.emg_eventrelated(epochs)
interval_features = nk.emg_intervalrelated(signals)
```

Documented event-related features include `EMG_Activation`,
`EMG_Amplitude_Mean`, `EMG_Amplitude_Max`, `EMG_Amplitude_SD`,
`EMG_Amplitude_Max_Time`, and `EMG_Bursts`. Interval analysis returns
`EMG_Activation_N` and `EMG_Amplitude_Mean` in the pinned official example.
Columns are conditional; inspect output.

For startle or rapid onset work, hardware latency, synchronization, filter group delay,
rectification/smoothing, and onset-definition error can dominate the result.

## Normalization

Raw/envelope amplitude is usually not comparable across participants or sessions.
Possible denominators include MVC, reference contraction, or within-participant
standardization, but each changes the estimand.

If using MVC:

- acquire it with a validated, safe protocol;
- inspect fatigue, pain, effort, clipping, and target/cross-talk;
- define which statistic and window represent MVC;
- report repetitions and reliability; and
- never divide by a near-zero/invalid reference.

Normalization does not make electrode/site differences disappear.

## Interpretation boundary

NeuroKit2 EMG can support research on amplitude and detected activity. It does not
provide validated motor-unit decomposition, neuromuscular diagnosis, fatigue
monitoring, prosthetic control safety, rehabilitation decisions, or sleep scoring.
Those require endpoint-specific acquisition, algorithms, standards, and independent
validation.

## Sources checked 2026-07-23

- [Official EMG API](https://neuropsychology.github.io/NeuroKit/functions/emg.html)
- [Stable v0.2.13 EMG source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/emg)
- [Fridlund & Cacioppo (1986), human EMG guidelines](https://pubmed.ncbi.nlm.nih.gov/3809364/)
- [Hermens et al. (2000), SENIAM sensor/placement recommendations](https://doi.org/10.1016/S1050-6411(00)00027-4)
- [Blumenthal et al. (2005), startle eyeblink EMG guidelines](https://doi.org/10.1111/j.1469-8986.2005.00271.x)

### `references/eog.md`

# Electrooculography

Checked **2026-07-23** against NeuroKit2 0.2.13 stable source/runtime
and the official EOG API/example.

## Scope and orientation

NeuroKit2's EOG pipeline is primarily a **vertical EOG blink** workflow. Stable
`eog_process()` requires blinks to be positive-going peaks. Verify channel montage,
polarity, reference, physical unit, sampling rate, hardware filters, amplifier range,
clock, and synchronization before processing.

Do not use this module as a full gaze, saccade, fixation, or sleep-scoring system.
Horizontal/vertical eye-movement interpretation and clinical/drowsiness monitoring need
separate validated methods.

## Optional MNE default

`eog_peaks()` and `eog_findpeaks()` default to `method="mne"`. In the core 0.2.13
installation, MNE is optional; the default can therefore raise an ImportError. Either
add MNE at a reviewed exact version to the project lock or choose a core method:

```python
signals, info = nk.eog_process(
    veog,
    sampling_rate=200,
    method="neurokit",
)
```

`eog_process()` forwards `**kwargs` to cleaning and peak finding. Record the explicit
method rather than relying on an environment-dependent default.

## Stable schemas

The high-level return is `(signals, info)`. Default columns are:

```text
EOG_Raw, EOG_Clean, EOG_Blinks, EOG_Rate
```

`info` has `EOG_Blinks` (sample indices) and `sampling_rate`.

Low-level interfaces differ:

```python
clean = nk.eog_clean(veog, sampling_rate=200, method="neurokit")

# Returns only an array of blink sample indices.
blink_indices = nk.eog_findpeaks(
    clean,
    sampling_rate=200,
    method="neurokit",
)

# Returns (same-length marker DataFrame, info dict).
blink_markers, blink_info = nk.eog_peaks(
    clean,
    sampling_rate=200,
    method="neurokit",
)
```

The 0.2.13 `eog_peaks()` docstring return section says array, while its tagged source
returns `(signals, info)`. The pinned source/runtime is authoritative for stable work.

Stable cleaning methods include `neurokit`, `agarwal2019`, `mne`, `brainstorm`, and
`kong1998`. Peak methods include `neurokit`, `mne`, `brainstorm`, and `blinker`.
MNE and some method paths need optional dependencies.

## Blink features

```python
features = nk.eog_features(
    clean,
    blink_info["EOG_Blinks"],
    sampling_rate=200,
)
```

`eog_features()` needs both the cleaned signal and peak-index array. It returns a dict
with event-level fields such as:

```text
Blink_LeftZeros, Blink_RightZeros, Blink_pAVR,
Blink_nAVR, Blink_BAR, Blink_Duration
```

Do not pass the processed DataFrame as the only argument. Feature validity depends on
positive orientation and accurate blink segmentation.

## Sampling and artifacts

Choose a rate from the endpoint and hardware bandwidth, not a universal number. Basic
blink timing may use lower rates than detailed eyelid velocity or saccade morphology.
Validate temporal error against labeled data at the actual rate; 200–500 Hz is common
in research but not a guarantee.

Inspect:

- saturation and clipping during large eye movements;
- baseline drift and electrode polarization;
- frontal/facial EMG and movement/cable artifacts;
- line noise and channel detachment;
- polarity and montage changes across sessions; and
- missing samples and synchronization with EEG/events.

Do not interpolate through a blink or across detachment. Preserve raw/clean overlays,
blink markers, rejected segments, and manual review outcomes.

## Event and interval analysis

```python
epochs = nk.epochs_create(
    signals,
    events,
    sampling_rate=200,
    epochs_start=-0.5,
    epochs_end=2,
    baseline_correction=False,
)
event_features = nk.eog_eventrelated(epochs)
interval_features = nk.eog_intervalrelated(signals)
```

Documented event-related fields include `EOG_Rate_Baseline`, rate min/max/mean/SD and
times, plus `EOG_Blinks_Presence`. Interval analysis returns `EOG_Peaks_N` and
`EOG_Rate_Mean` in the official example. It does not universally return blink
amplitude or duration summaries. Inspect columns at runtime.

Blink rate over short windows is unstable and task-dependent. A count/rate change does
not uniquely identify attention, fatigue, stress, dry eye, dopamine, or a neurological
condition.

## EEG integration

EOG can help identify ocular contamination in EEG, but NeuroKit2 does not provide a
complete validated correction pipeline here. With MNE:

1. synchronize and preserve dedicated EOG channels;
2. fit artifact identification/correction on appropriate data;
3. verify component or regression selection without removing neural signal;
4. compare raw and corrected ERPs/spectra/topographies; and
5. report method, channels, filters, thresholds, components, and exclusions.

Avoid circularly selecting correction settings to maximize an experimental result.

## Sources checked 2026-07-23

- [Official EOG API](https://neuropsychology.github.io/NeuroKit/functions/eog.html)
- [Official EOG example](https://neuropsychology.github.io/NeuroKit/examples/eog_analyze/eog_analyze.html)
- [Stable v0.2.13 EOG source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/eog)
- [Kleifges et al. (2017), BLINKER](https://doi.org/10.3389/fnins.2017.00012)
- [Keil et al. (2014), EEG/MEG reporting guidance](https://doi.org/10.1111/psyp.12147)

### `references/epochs_events.md`

# Events and epochs

Checked **2026-07-23** against NeuroKit2 0.2.13 stable source/runtime and
the live Events and Epochs API pages.

## Event coordinate contract

Choose one canonical representation before analysis:

- absolute time with a named clock and unit;
- zero-based sample index on a named stream; and
- event duration and condition/label metadata.

`events_find()` uses zero-based sample positions. Its `start_at`, `end_at`,
`duration_min`, `duration_max`, and `inter_min` arguments are sample counts, not
seconds.

```python
events = nk.events_find(
    trigger,
    threshold=0.5,
    threshold_keep="above",
    duration_min=2,
    inter_min=5,
    event_conditions=["A", "B", "A"],
)
```

Stable signature:

```text
events_find(
  event_channel, threshold="auto", threshold_keep="above",
  start_at=0, end_at=None, duration_min=1, duration_max=None,
  inter_min=0, discard_first=0, discard_last=0,
  event_labels=None, event_conditions=None
)
```

The default return is a dict containing `onset`, `duration`, and `label`; optional
conditions use the singular key `condition`. Multi-channel input can add
`events_channel` and generates conditions from the digital combination.

Do not infer trigger semantics from amplitude alone. Verify polarity, threshold,
debouncing, pulse width, dropped triggers, device latency, and whether simultaneous
digital inputs are encoded as expected.

## Build events explicitly when possible

```python
events = nk.events_create(
    event_onsets=[1000, 2500, 4000],
    event_durations=[100, 100, 100],
    event_labels=["1", "2", "3"],
    event_conditions=["A", "B", "A"],
)
```

Labels must be unique. Keep experimental trial IDs outside participant-identifying
names.

## `epochs_create()` semantics in 0.2.13

```text
epochs_create(
  data, events=None, sampling_rate=1000,
  epochs_start=0, epochs_end="from_events",
  event_labels=None, event_conditions=None,
  baseline_correction=False
)
```

- `epochs_start` and `epochs_end` are seconds relative to each event.
- The data slice is `[start_sample, end_sample)` (end-exclusive).
- Each epoch is a DataFrame in a dict keyed by label.
- The original sample coordinate is stored in `Index`.
- The DataFrame index is rebuilt with `numpy.linspace(..., endpoint=True)`, so the
  displayed last index equals `epochs_end` even though the end sample is excluded.
- `Label` and optional `Condition` are added as columns.
- Events near a boundary are padded by internal buffers. Floating columns receive
  NaN; integer columns can receive zero because of dtype preservation.

The pinned probe for one signal, `-0.2` to `0.5` s at 100 Hz, produced 70 rows with
an index from exactly `-0.2` through `0.5`. Do not derive sample count from that
floating index. Use `Index`, the known sampling rate, and explicit half-open bounds.

## Boundary policy

Decide before analysis:

- `drop`: remove incomplete trials and report condition-wise counts;
- `pad`: retain them with an explicit validity mask; or
- `error`: stop and repair event/window definitions.

Do not let NaN padding or integer zero padding silently become a physiological
baseline. The dependency-free planner reports affected trials:

```bash
python skills/neurokit2/scripts/plan_epochs.py \
  --events 1000,2500,4000 --event-unit samples \
  --sampling-rate 100 --recording-samples 5000 \
  --epoch-start -0.2 --epoch-end 0.8 \
  --baseline-start -0.2 --baseline-end 0
```

For events supplied in seconds, use `--event-unit seconds`; the planner rejects
onsets/windows that do not map exactly to samples.

## Baseline correction

`baseline_correction=True` subtracts the mean from epoch start through `t=0`
(inclusive in the rebuilt time index). If the epoch starts after zero, it uses the
epoch start. The operation is applied broadly to numeric columns present at that
point, including marker/index columns.

Prefer selective, manual correction:

```python
epochs = nk.epochs_create(
    processed,
    events,
    sampling_rate=100,
    epochs_start=-0.2,
    epochs_end=0.8,
    baseline_correction=False,
)

amplitude_columns = ["EDA_Phasic"]
for epoch in epochs.values():
    baseline = epoch.loc[(epoch.index >= -0.2) & (epoch.index < 0), amplitude_columns]
    epoch.loc[:, amplitude_columns] = (
        epoch.loc[:, amplitude_columns] - baseline.mean()
    )
```

Prespecify baseline interval and estimand. Baseline subtraction is not universally
appropriate for rates, binary peaks, phase, quality, or absolute tonic levels.
Reject/flag a trial if its baseline has missing data or artifact rather than quietly
using fewer samples.

## Conversions

`epochs_to_df()` stacks epochs and adds a `Time` column; the stable probe observed
`Signal`, `Index`, `Label`, `Condition`, and `Time`.

`epochs_to_array()` does not take a `column` argument in 0.2.13. Equal-length,
single-signal epochs produced shape `(time, epochs)` in the pinned probe. Multiple
signal columns add an intermediate dimension. Unequal epochs are not supported.

`epochs_average()` signature is:

```text
epochs_average(epochs, which=None, indices=["mean", "std", "ci"], show=False)
```

For `which="Signal"`, the pinned schema contained `Time`, `Signal_Mean`,
`Signal_SD`, `Signal_CI_low`, and `Signal_CI_high` (plus a reset-index column).
This is not a universal event-related feature schema.

## Signal-specific analysis

Functions such as `ecg_eventrelated()`, `eda_eventrelated()`,
`rsp_eventrelated()`, `ppg_eventrelated()`, `emg_eventrelated()`, and
`eog_eventrelated()` inspect available processed columns. Their output changes when
quality, phase, amplitude, condition, or trend columns are absent.

Use explicit dispatch:

```python
ecg_features = nk.ecg_analyze(
    epochs, sampling_rate=100, method="event-related"
)
```

`method="auto"` chooses event-related analysis when mean duration is under 10 seconds.
That software threshold is not scientific justification for a window or analysis.

## Trial QC and statistics

Before averaging:

1. inspect trigger detection against the raw marker channel;
2. quantify boundary padding and missing baseline/post-event samples;
3. apply modality-specific artifact rules without looking at condition outcomes;
4. report retained trials per participant and condition;
5. avoid threshold tuning on the same effects being tested; and
6. model participant/trial hierarchy rather than treating epochs as independent.

There is no universal minimum number of trials or universal epoch window. Determine
both from the expected response, acquisition, study design, reliability, and power
analysis.

## Sources checked 2026-07-23

- [Official Events API](https://neuropsychology.github.io/NeuroKit/functions/events.html)
- [Official Epochs API](https://neuropsychology.github.io/NeuroKit/functions/epochs.html)
- [Official event-related example](https://neuropsychology.github.io/NeuroKit/examples/bio_eventrelated/bio_eventrelated.html)
- [Stable v0.2.13 epoch source](https://github.com/neuropsychology/NeuroKit/blob/v0.2.13/neurokit2/epochs/epochs_create.py)
- [SPR EEG/ERP guideline index](https://sprweb.org/guidelines-papers)

### `references/hrv.md`

# Heart-rate variability and RSA

Checked **2026-07-23** against NeuroKit2 0.2.13 stable runtime/source,
the official HRV API/tutorial, and HRV/RSA measurement guidance.

## Define the interval series

HRV analysis needs beat timing plus a defensible classification/correction policy.
Distinguish:

- **RR/RRI**: intervals between detected R peaks;
- **NN**: intervals between beats judged normal sinus beats; and
- **PP/PRV**: intervals between peripheral pulse peaks.

Do not relabel automatically corrected RR or PPG intervals as NN. Preserve raw waveform,
raw peaks, corrected peaks, excluded segments, correction categories, and interval units.

Accepted NeuroKit2 inputs include:

- a list/array of peak sample indices;
- marker/info objects from `ecg_peaks()`, `ppg_peaks()`, `ecg_process()`, or
  `bio_process()`; and
- a dict with `RRI` (milliseconds) and `RRI_Time` (seconds).

Always pass the sampling rate of the continuous signal in which peak indices were
defined.

## Current functions and schemas

```python
time = nk.hrv_time(peaks, sampling_rate=250)
frequency = nk.hrv_frequency(peaks, sampling_rate=250)
nonlinear = nk.hrv_nonlinear(peaks, sampling_rate=250)
all_domains = nk.hrv(peaks, sampling_rate=250)
```

All four return one-row DataFrames. `hrv()` concatenates the available domains and can
append RSA when its input contains processed respiration data. Columns vary with data
length, kwargs, available modalities, and release.

Pinned 0.2.13 observations:

- `hrv_time()` returned 25 columns, including `HRV_MeanNN`, `HRV_SDNN`,
  `HRV_RMSSD`, `HRV_SDSD`, `HRV_CVNN`, `HRV_CVSD`, robust interval summaries,
  `HRV_pNN50`, `HRV_pNN20`, `HRV_HTI`, and `HRV_TINN`. Long-segment indices
  (`SDANN*`, `SDNNI*`) can be NaN when duration is insufficient.
- `hrv_frequency()` returned exactly `HRV_ULF`, `HRV_VLF`, `HRV_LF`, `HRV_HF`,
  `HRV_VHF`, `HRV_TP`, `HRV_LFHF`, `HRV_LFn`, `HRV_HFn`, and `HRV_LnHF` in the
  default probe.
- `hrv_nonlinear()` returned Poincaré, asymmetry, fragmentation, DFA/MFDFA,
  entropy/fractal, Lempel–Ziv, and symbolic-dynamics columns. Stable 0.2.13 added
  default `HRV_Symbolic_EqualProb4_*` features.

Do not hard-code a “complete” HRV column list. Persist `list(result.columns)` and map
only prespecified outputs.

## Units and interval helpers

Time-domain metrics are milliseconds where applicable. Frequency power is based on
millisecond intervals and therefore commonly has ms²-derived units, but normalization
and estimator settings change interpretation.

```python
processed_rri, processed_time, interpolation_rate = nk.intervals_process(
    rri_ms,
    intervals_time=time_s,
    interpolate=True,
    interpolation_rate=4,
    detrend=None,
)
peaks = nk.intervals_to_peaks(rri_ms, sampling_rate=1000)
```

`intervals_process()` returns three objects: intervals in milliseconds, timestamps in
seconds, and interpolation rate. `intervals_to_peaks()` returns integer peak indices,
with a constructed first peak. Verify external-device interval definitions and dropped
beats before conversion.

## Recording duration

Duration requirements are metric-, population-, protocol-, and estimator-specific.
Use these conservative planning principles:

- Five minutes is the conventional standardized short-term HRV window.
- RMSSD can be computed on shorter windows, but ultra-short estimates require
  endpoint- and population-specific reliability/validity evidence.
- A spectral segment should contain enough cycles of the lowest frequency interpreted.
  Five minutes is a practical reference for conventional LF/HF short-term analysis.
- Do not interpret ULF from a short recording; it is conventionally associated with
  long, often 24-hour recordings.
- VLF physiological interpretation in short recordings is uncertain.
- Entropy, DFA, MFDFA, correlation dimension, and RQA need enough beats for stable
  estimation; defaults returning a number do not establish adequacy.

Do not compare metrics estimated from unequal durations without a validated strategy.
Report exact usable duration and beat count after exclusions, not nominal acquisition
duration.

## Ectopy and artifact policy

1. Inspect ECG/PPG quality and peak overlays.
2. Review the tachogram and interval histogram.
3. Identify non-sinus beats separately from detector errors when possible.
4. Report raw and corrected beat counts and percentage.
5. Limit interpolation/correction according to a prespecified exclusion rule.
6. Repeat key analyses under plausible correction choices.

`ecg_process()` requests artifact correction automatically in 0.2.13. If that is not
the planned policy, run `ecg_clean()` and `ecg_peaks()` explicitly.

Heavy correction can manufacture smooth HRV. A segment with excessive ectopy,
detachment, or motion may need exclusion rather than interpolation.

## Frequency domain

Stable signature:

```text
hrv_frequency(
  peaks, sampling_rate=1000,
  ulf=(0, 0.0033), vlf=(0.0033, 0.04),
  lf=(0.04, 0.15), hf=(0.15, 0.4), vhf=(0.4, 0.5),
  psd_method="welch", normalize=True, interpolation_rate=100, ...
)
```

Set `interpolation_rate=4` to approximate a common Kubios interpolation choice; set it
to `None` for already-interpolated intervals or Lomb–Scargle. Record detrending,
interpolation, PSD method, window/order, frequency bands, and normalization.

Do **not** interpret `HRV_LFHF` as a direct “sympathovagal balance.” LF contains mixed
influences; HF depends on breathing frequency/depth and can miss respiratory variation
outside the default 0.15–0.4 Hz band.

## PPG-derived variability

PPG pulse timing includes pre-ejection and pulse-transit effects, and varies with site,
vascular state, posture, temperature, motion, contact pressure, and sensor design.
Label results PRV/PPG-derived HRV and validate against synchronized ECG for the endpoint,
conditions, sites, and population. Agreement at rest does not imply agreement during
exercise or stress.

## Respiratory sinus arrhythmia

Stable signature:

```text
hrv_rsa(
  ecg_signals, rsp_signals=None, rpeaks=None,
  sampling_rate=1000, continuous=False,
  window=None, window_number=None
)
```

Use synchronized processed ECG and respiration DataFrames:

```python
rsa = nk.hrv_rsa(
    ecg_signals,
    rsp_signals,
    rpeaks=ecg_info,
    sampling_rate=100,
    continuous=False,
)
```

The pinned summary returned a dict with P2T and Gates statistics, including
`RSA_P2T_Mean`, `RSA_P2T_SD`, `RSA_P2T_NoRSA`, `RSA_PorgesBohrer`, and Gates
mean/SD/log fields. `continuous=True` returned a same-length DataFrame with
`RSA_P2T` and `RSA_Gates`.

Requirements:

- shared clock, sampling grid, and defined lag/drift policy;
- valid R peaks and respiration cycles;
- enough cycles/windows for the chosen method;
- measured respiration rate and context; and
- reporting of P2T/Gates method and all window parameters.

RSA/HF-HRV is often related to cardiac vagal modulation but is not a direct,
context-free vagal-tone assay. Respiration, activity, beta-adrenergic influence, age,
posture, and within- versus between-person contrasts can change interpretation.

## Analysis/report checklist

- package version and observed output schema;
- ECG/PPG source, sensor/site, sampling, clock, units, and raw-data access;
- duration, usable duration, beat count, and exclusions;
- peak detector, quality method, ectopy/artifact criteria, and correction percentage;
- RRI/NN/PRV terminology;
- PSD/interpolation/detrending/bands/normalization;
- respiration measurement and rate/depth context;
- prespecified metrics and multiplicity control; and
- no diagnostic, monitoring, or medical-device claim without separate validation.

## Sources checked 2026-07-23

- [Official HRV API](https://neuropsychology.github.io/NeuroKit/functions/hrv.html)
- [Official HRV example](https://neuropsychology.github.io/NeuroKit/examples/ecg_hrv/ecg_hrv.html)
- [Pham et al. (2021), NeuroKit2 HRV review/tutorial](https://doi.org/10.3390/s21123998)
- [Quigley et al. (2024), current SPR HR/HRV guidelines](https://doi.org/10.1111/psyp.14604)
- [ESC/NASPE Task Force (1996)](https://pubmed.ncbi.nlm.nih.gov/8598068/)
- [Berntson et al. (1997), interpretive caveats](https://doi.org/10.1111/j.1469-8986.1997.tb02140.x)
- [Laborde et al. (2017), planning/reporting](https://doi.org/10.3389/fpsyg.2017.00213)
- [Grossman & Taylor (2007), RSA caveats](https://doi.org/10.1016/j.biopsycho.2005.11.014)

### `references/ppg.md`

# Photoplethysmography

Checked **2026-07-23** against NeuroKit2 0.2.13 stable runtime/source,
the official PPG API, 0.2.13 release notes, and measurement guidance.

## Acquisition contract

Record sensor mode (reflectance/transmission), wavelength(s), anatomical site,
attachment/contact pressure, device/firmware, raw unit/range, ambient-light handling,
sampling rate, clock, temperature/perfusion, activity/posture, and motion/accelerometer
channels. Validate across representative skin pigmentation, anatomy, age, vascular
state, motion, and intended population.

PPG is optical blood-volume-pulse measurement, not cardiac electrical activity.
Pulse timing and morphology depend on site and vascular/transit dynamics.

## Stable high-level pipeline

```python
signals, info = nk.ppg_process(
    ppg,
    sampling_rate=100,
    method="elgendi",
    method_quality="templatematch",
)
```

Pinned 0.2.13 default columns:

```text
PPG_Raw, PPG_Clean, PPG_Rate, PPG_Quality, PPG_Peaks
```

`info` contained `PPG_Peaks`, `sampling_rate`, and peak/correction method metadata.
The live doc's older codebook can omit `PPG_Quality`; stable runtime/source includes it.

## Cleaning and peak methods

For explicit selection:

```python
clean = nk.ppg_clean(
    ppg,
    sampling_rate=100,
    method="elgendi",
)
markers, peak_info = nk.ppg_peaks(
    clean,
    sampling_rate=100,
    method="elgendi",
    correct_artifacts=False,
)
```

Stable cleaning methods include:

- `elgendi`;
- `nabian2018` (can use expected heart rate);
- `langevin2021`;
- `goda2024`; and
- `none`.

Stable peak methods include:

- `elgendi`;
- `bishop` (peaks plus pulse onsets);
- `charlton` (MSPTDfast v2; peaks plus onsets); and
- `charlton2024` (superseded v1).

Method-dependent extra outputs are a primary reason not to hard-code one schema.
Validate peak/onset performance against labeled data at the actual site, rate,
perfusion, motion, and population.

`correct_artifacts=True` uses the cardiac peak-correction path. Retain raw/corrected
peaks and correction categories; correction cannot repair a low-quality optical
waveform.

## Quality outputs added/expanded in 0.2.13

```python
quality = nk.ppg_quality(
    clean,
    peaks=peak_info["PPG_Peaks"],
    sampling_rate=100,
    method="templatematch",
)
```

Stable quality methods and scales differ:

- `templatematch`: continuous similarity, typically 0–1;
- `dissimilarity`: unbounded, where zero is highest similarity;
- `ho2025`/interval-consistency path: binary interval quality;
- `skewness`, `kurtosis`, `entropy`: unbounded windowed metrics;
- `perfusion`: percentage-like 0–100 and requires raw PPG; and
- `relative_power`: 0–1, requires raw PPG, and defaults to 60 s windows.

No threshold is universal across these outputs. Name the method and direction/scale.
Short signals can be invalid for a method's default window. `ppg_process()` passes
peak indices—not the whole info dict—to quality estimation.

Quality relative to an average pulse does not prove physiological accuracy: repeated
motion-corrupted beats can be morphologically consistent. Combine morphology, motion,
contact/perfusion, missingness, detector agreement, and endpoint-specific validation.

## Sampling and preprocessing

Sampling requirements depend on endpoint:

- pulse rate needs less bandwidth than morphology, onset timing, or derivatives;
- wrist wearables commonly use lower rates than laboratory finger systems;
- resampling cannot recover missing onset precision or a dicrotic feature; and
- a nominal rate does not establish clock accuracy or anti-alias filtering.

Do not prescribe one universal minimum. Validate rate and filters for the exact
detector/feature and report native/processed rates. Process at native rate before
multimodal alignment when possible.

Motion, contact pressure, ambient light, vasoconstriction, temperature, pigmentation,
site, and clipping can all change amplitude/morphology. Preserve a quality/artifact
mask and accelerometry where available. Avoid interpolating through corrupted pulses.

## PPG-derived variability is PRV

```python
prv = nk.hrv_time(peak_info, sampling_rate=100)
```

NeuroKit2 accepts PPG peaks in HRV functions, but interpretation remains pulse-rate
variability. PRV contains pre-ejection and pulse-transit variability and can differ
from ECG HRV by site, posture, respiration, activity, temperature, and vascular state.

For an HRV-equivalence claim:

1. acquire synchronized ECG and PPG;
2. validate pulse/beat matching and lag/drift;
3. prespecify agreement metrics and acceptable error for each HRV endpoint;
4. test rest, task/activity, motion, and relevant populations/sites; and
5. report PRV terminology when equivalence is not established.

Do not infer ECG morphology, rhythm diagnosis, oxygen saturation, blood pressure, or
arterial stiffness from this basic PPG pipeline.

## Event and interval analysis

```python
epochs = nk.epochs_create(
    signals,
    events,
    sampling_rate=100,
    epochs_start=-1,
    epochs_end=10,
    baseline_correction=False,
)
event_features = nk.ppg_eventrelated(epochs)
interval_features = nk.ppg_intervalrelated(signals)
```

Documented event fields include baseline/min/max/mean/SD rate, times, and polynomial
trend coefficients. Interval output includes mean rate and HRV-family columns.
Availability depends on input columns, duration, and release; inspect runtime output.

## Pulse morphology

`ppg_segment()` returns a dict of pulse epochs. Morphology comparisons require:

- consistent site, attachment, pressure, wavelength, and polarity;
- validated onsets/peaks and quality masks;
- appropriate baseline/amplitude normalization;
- sufficient sampling/bandwidth;
- control of heart rate and vascular state; and
- endpoint-specific evidence.

A dicrotic feature in a processed waveform does not by itself validate aortic valve
timing or arterial stiffness.

## Interpretation boundary

Use these tools for research and education. They are not validated here for arrhythmia,
oxygen saturation, blood pressure, disease detection, remote patient monitoring,
alarms, or wearable medical-device validation.

## Sources checked 2026-07-23

- [Official PPG API](https://neuropsychology.github.io/NeuroKit/functions/ppg.html)
- [Stable v0.2.13 PPG source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/ppg)
- [NeuroKit2 0.2.13 release](https://github.com/neuropsychology/NeuroKit/releases/tag/v0.2.13)
- [Charlton et al. (2023), wearable PPG roadmap](https://doi.org/10.1088/1361-6579/acead2)
- [Allen (2007), PPG measurement review](https://doi.org/10.1088/0967-3334/28/3/R01)
- [Quigley et al. (2024), ECG/PPG and HRV guidance](https://doi.org/10.1111/psyp.14604)
- [Yuda et al. (2020), PRV site differences](https://pmc.ncbi.nlm.nih.gov/articles/PMC7035641/)

### `references/rsp.md`

# Respiration

Checked **2026-07-23** against NeuroKit2 0.2.13 stable runtime/source,
the official RSP API/examples, and cardiorespiratory interpretation guidance.

## Acquisition contract and polarity

Record sensor type (belt, airflow, capnography, impedance, derived proxy), placement,
gain/range, physical unit, native rate, clock, hardware filters, calibration, and
annotations for speech, cough, sigh, breath hold, swallowing, movement, and detachment.

A belt/impedance amplitude is not tidal volume unless calibrated and validated.
Different devices have opposite polarity. NeuroKit2's documented convention labels:

- `RSP_Peaks`: exhalation onsets;
- `RSP_Troughs`: inhalation onsets; and
- `RSP_Phase`: `1` inspiration, `0` expiration.

Verify these labels against the actual device and a known breath. Invert or relabel
explicitly before interpretation if needed.

## Stable high-level pipeline

```python
signals, info = nk.rsp_process(
    rsp,
    sampling_rate=50,
    method="khodadad2018",
    method_rvt="harrison2021",
)
```

Pinned default columns:

```text
RSP_Raw, RSP_Clean, RSP_Amplitude, RSP_Rate, RSP_RVT,
RSP_Phase, RSP_Phase_Completion,
RSP_Symmetry_PeakTrough, RSP_Symmetry_RiseDecay,
RSP_Peaks, RSP_Troughs
```

`info` contained `RSP_Peaks`, `RSP_Troughs`, and `sampling_rate`. This is a
default schema observation, not a universal contract.

## Cleaning and extrema

```python
clean = nk.rsp_clean(rsp, sampling_rate=50, method="khodadad2018")
markers, extrema = nk.rsp_peaks(
    clean,
    sampling_rate=50,
    method="khodadad2018",
)
```

Stable peak methods include `khodadad2018`, `biosppy`, `scipy`, and
`schafer2008`. `rsp_fixpeaks()` is currently documented as a placeholder that does
not correct respiration extrema.

Validate extrema during irregular breathing, pauses, speech, motion, and changing
amplitude. A smooth sinusoidal simulation is not enough.

## Rate, amplitude, and phase signatures

These functions do not all accept the same peak object:

```python
rate = nk.rsp_rate(
    clean,
    troughs=extrema["RSP_Troughs"],
    sampling_rate=50,
    method="trough",
)
amplitude = nk.rsp_amplitude(
    clean,
    peaks=extrema["RSP_Peaks"],
    troughs=extrema["RSP_Troughs"],
)
phase = nk.rsp_phase(
    extrema["RSP_Peaks"],
    troughs=extrema["RSP_Troughs"],
    desired_length=len(clean),
)
```

- `rsp_rate()` takes the cleaned signal first; `method="trough"` uses inhalation
  onsets, while `method="xcorr"` estimates a windowed principal rate.
- `rsp_amplitude()` returns a same-length interpolated amplitude series.
- `rsp_phase()` takes peaks/troughs, not the cleaned signal, and returns a DataFrame
  with phase and completion.

Rates are breaths/minute. Amplitude remains in the sensor's arbitrary/calibrated unit.
Phase accuracy depends on extrema and polarity.

## RRV and RAV

```python
rrv = nk.rsp_rrv(
    signals["RSP_Rate"],
    troughs=info["RSP_Troughs"],
    sampling_rate=50,
)
rav = nk.rsp_rav(
    signals["RSP_Amplitude"],
    peaks=info,
)
```

The pinned `rsp_rrv()` output had 20 columns spanning interval, frequency, Poincaré,
and entropy metrics (`RRV_RMSSD` through `RRV_SampEn`). The pinned RAV output had
`RAV_Mean`, `RAV_SD`, `RAV_RMSSD`, and `RAV_CVSD`.

Do not interpret RRV/RAV from only a few breaths. Choose duration from the lowest
frequency and nonlinear metric being estimated, and report breath count, usable
duration, irregular-breath exclusions, and sensitivity. There is no universal
“higher is healthier” interpretation.

## Respiratory volume per time

Direct stable signature:

```text
rsp_rvt(
  rsp_signal, sampling_rate=1000, method="power2020",
  boundaries=[2.0, 0.033333...], iterations=10, ...
)
```

Direct `rsp_rvt()` defaults to `power2020`, while `rsp_process()` defaults its
`method_rvt` to `harrison2021`. Other stable option: `birn2006`.

```python
rvt = nk.rsp_rvt(
    clean,
    sampling_rate=50,
    method="harrison2021",
)
```

RVT is a derived proxy/regressor. It is not calibrated respiratory volume or minute
ventilation. For fMRI nuisance modeling, match the cited definition, acquisition,
lag/convolution, resampling, and scanner preprocessing; do not treat one method as
interchangeable with another.

## Missing data and artifacts

Respiration signals commonly contain nonstationary physiology. Do not automatically
classify sighs, pauses, speech, coughing, or swallowing as noise. Annotate them according
to the research question.

- Segment long gaps/detachment.
- Do not interpolate across apnea-like pauses or speech and then compute rate.
- Preserve raw/clean/extrema overlays.
- Track filter and window edge validity.
- Quantify missing breaths and altered intervals after exclusions.
- Verify belt slippage and baseline drift separately from breathing depth.

## Event and interval analysis

```python
epochs = nk.epochs_create(
    signals,
    events,
    sampling_rate=50,
    epochs_start=-1,
    epochs_end=8,
    baseline_correction=False,
)
event_features = nk.rsp_eventrelated(epochs)
interval_features = nk.rsp_intervalrelated(signals, sampling_rate=50)
```

Event-related features are conditional and include rate/amplitude baselines and
post-event summaries, phase/completion at onset, and RVT fields when present. Interval
analysis can append RRV/RAV and inspiration/expiration duration features. Inspect the
runtime schema.

Baseline subtraction is usually inappropriate for binary phase/peak columns. Prespecify
which continuous features, if any, are baseline corrected.

## RSA and alignment

For RSA, ECG and respiration need a shared clock and verified lag/drift:

```python
rsa = nk.hrv_rsa(
    ecg_signals,
    rsp_signals,
    rpeaks=ecg_info,
    sampling_rate=common_rate,
    continuous=False,
)
```

Measure and report respiration; spontaneous or paced breathing changes the estimand.
RSA can reflect cardiac vagal modulation under suitable conditions but is confounded by
respiratory parameters, activity, posture, age, and adrenergic influence.

## Interpretation boundary

Use this module for respiratory time-series research. It is not a validated system for
apnea detection, capnography, tidal-volume measurement, respiratory diagnosis,
biofeedback safety, patient/driver monitoring, or ventilatory control.

## Sources checked 2026-07-23

- [Official RSP API](https://neuropsychology.github.io/NeuroKit/functions/rsp.html)
- [Official RRV example](https://neuropsychology.github.io/NeuroKit/examples/rsp_rrv/rsp_rrv.html)
- [Stable v0.2.13 RSP source](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/rsp)
- [Grossman & Taylor (2007), respiration/RSA caveats](https://doi.org/10.1016/j.biopsycho.2005.11.014)
- [Berntson et al. (1997), HRV origins/methods/caveats](https://doi.org/10.1111/j.1469-8986.1997.tb02140.x)
- [Birn et al. (2006), RVT and fMRI](https://doi.org/10.1016/j.neuroimage.2005.11.053)

### `references/signal_processing.md`

# General signal processing

Checked **2026-07-23** against NeuroKit2 0.2.13, its stable wheel, tagged
source, and the live signal API page (`0.2.13.dev214`).

## Start with a signal contract

For every channel retain:

- sensor/channel identity and physical unit;
- native sampling rate and timestamps;
- polarity, gain, acquisition filters, and ADC range;
- missing/discontinuous intervals and artifact annotations;
- expected physiological bandwidth; and
- the exact NeuroKit2 function, method, parameters, and package version.

`signal_sanitize()` does **not** clean artifacts or interpolate missing values. In
0.2.13 it resets an indexed pandas Series to a default index.

## Safe preprocessing order

1. Preserve the original samples and time axis.
2. Check timestamp order, rate, clipping, flatlines, non-finite values, and gaps.
3. Split at long gaps. Interpolate only short, prespecified gaps and retain a mask.
4. Remove offsets/trends only when justified.
5. Apply a modality/method-specific filter at the native rate.
6. Trim or flag filter transients.
7. Detect/correct peaks or derive features.
8. Resample continuous outputs only when alignment or modeling requires it.

Do not use a filter to “fix” clipping, sensor detachment, dropped packets, or motion.
Do not interpolate event markers, quality flags, or peak indicator vectors as
continuous amplitudes.

## Verified 0.2.13 interfaces

| Function | Stable behavior relevant to schemas |
|---|---|
| `signal_filter()` | Returns one array. Default is order-2 Butterworth; available behavior depends on `method`, cutoffs, and sampling rate. |
| `signal_sanitize()` | Resets pandas Series indexing; it is not a NaN/artifact cleaner. |
| `signal_fillmissing()` | Forward, backward, or both-direction fill only (`method="forward"`, `"backward"`, or `"both"`). |
| `signal_resample()` | Returns one array; accepts target length or source/target rates. Methods include interpolation, FFT, polyphase, NumPy, and pandas paths. |
| `signal_interpolate()` | Returns interpolated values; explicitly provide source and target coordinates for irregular time. |
| `signal_findpeaks()` | Returns a dict. The pinned default synthetic probe observed `Peaks`, `Height`, `Distance`, `Onsets`, `Offsets`, and `Width`; keys can change with input/method. |
| `signal_fixpeaks()` | Returns `(info, corrected_peaks)` in stable source. Default Kubios `info` includes artifact categories and diagnostics. |
| `signal_period()` | Takes peak locations and returns period in seconds, optionally interpolated to a requested sample length. |
| `signal_rate()` | Takes peak locations and returns events/minute, optionally interpolated. |
| `signal_psd()` | Returns a DataFrame; the pinned Welch probe observed `Frequency` and `Power`. |
| `signal_power()` | Returns a one-row DataFrame with band-derived names such as `Hz_0.5_2`; names depend on requested bands. |
| `signal_timefrequency()` | Returns `(frequency, time, representation)`; frequency is the first object. |
| `signal_synchrony()` | Returns an array; supported methods are Hilbert phase synchrony and rolling correlation. |
| `signal_decompose()` | Returns a component array; stable methods are EMD and SSA, not a component dictionary. |
| `signal_changepoints()` | Implements PELT and returns change-point sample indices. |

Never unpack `signal_psd()` into `(psd, frequencies)` in 0.2.13:

```python
psd = nk.signal_psd(
    signal,
    sampling_rate=250,
    method="welch",
    normalize=False,
    show=False,
)
frequency_hz = psd["Frequency"]
power = psd["Power"]
```

`normalize=True` scales by maximum PSD power. It is not physical calibration. Use
`normalize=False` when absolute spectral units are required and derive those units from
the acquisition and estimator.

## Filtering and resampling

Cutoffs are in Hz and must lie below Nyquist. Report:

- filter family and implementation (`butterworth`, FIR, Savitzky–Golay, powerline);
- order, low/high cutoff, notch frequency, and whether processing is zero phase;
- padding/edge handling and samples discarded; and
- source and target sampling rates plus resampling method.

Example:

```python
filtered = nk.signal_filter(
    signal,
    sampling_rate=250,
    lowcut=0.5,
    highcut=40,
    method="butterworth",
    order=2,
)
resampled = nk.signal_resample(
    filtered,
    sampling_rate=250,
    desired_sampling_rate=100,
    method="poly",
)
```

Downsampling requires anti-alias filtering. Resampling cannot recover timing precision or
bandwidth absent from the acquisition. For multimodal data, preserve native processing
and timestamps first; choose a common grid only after clock alignment.

## Missing data

Forward/backward fill can create artificial constant segments. Generic interpolation can
create smooth but fictional morphology and peaks. Record:

- count and maximum run of missing samples;
- gap durations in seconds;
- whether each gap was segmented, excluded, padded, or interpolated;
- interpolation method and maximum allowed gap; and
- whether downstream quality and uncertainty include the imputed mask.

Most modality pipelines may warn and internally forward-fill some missing samples. That
convenience is not a study-level missing-data policy.

## Peak correction

```python
info, corrected = nk.signal_fixpeaks(
    peaks,
    sampling_rate=250,
    method="Kubios",
    iterative=True,
)
```

The Kubios/Lipponen–Tarvainen path is intended for ECG/PPG beats. `method="neurokit"`
supports explicit interval limits and can be used more generically. Always retain raw
and corrected peaks, counts by artifact category, affected time ranges, and results with
and without correction. Do not call corrected beat intervals “normal-to-normal” unless
the study actually identifies non-sinus/ectopic beats.

## Quality and reproducibility

Useful QC is multimodal and method-specific:

- raw/clean overlays and filter-edge review;
- missing, flatline, clipping, and saturation fractions;
- peak/onset overlays and interval distributions;
- quality values with their method-specific direction and scale;
- sensitivity to plausible filter/detector settings; and
- synthetic fixtures plus labeled empirical validation data.

The bundled inspector is dependency-free:

```bash
python skills/neurokit2/scripts/inspect_signal.py \
  --input signal.csv --root . --deidentified \
  --columns ECG --time-column time_s --units ECG=mV
```

## Sources checked 2026-07-23

- [Official signal API](https://neuropsychology.github.io/NeuroKit/functions/signal.html)
- [Stable v0.2.13 source tag](https://github.com/neuropsychology/NeuroKit/tree/v0.2.13/neurokit2/signal)
- [NeuroKit2 main paper](https://doi.org/10.3758/s13428-020-01516-y)
- [Lipponen & Tarvainen (2019), peak correction](https://doi.org/10.1080/03091902.2019.1640306)

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared bounded, local-only helpers for the NeuroKit2 skill CLIs."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import stat
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

NEUROKIT2_VERSION = "0.2.13"
PINNED_INSTALL = 'uv pip install "neurokit2==0.2.13"'
MAX_CSV_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 4 * 1024 * 1024
MAX_OUTPUT_BYTES = 128 * 1024 * 1024
MAX_ROWS = 500_000
MAX_CHANNELS = 64
MAX_SELECTED_COLUMNS = 16
MAX_CELL_CHARS = 4096
MISSING_TOKENS = {"", "na", "n/a", "nan", "none", "null"}


class CliError(ValueError):
    """An expected command-line validation error."""


def _reject_constant(value: str) -> None:
    raise CliError(f"non-standard JSON constant is not allowed: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CliError(f"duplicate JSON key is not allowed: {key!r}")
        result[key] = value
    return result


def _reject_url(value: str) -> None:
    lowered = value.strip().lower()
    if "://" in lowered or lowered.startswith(
        ("http:", "https:", "ftp:", "s3:", "gs:", "file:")
    ):
        raise CliError("URLs are not accepted; provide a bounded local path")
    if "\x00" in value:
        raise CliError("paths must not contain a NUL byte")


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _reject_symlink_components(path: Path) -> None:
    absolute = _absolute_lexical(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        try:
            if current.is_symlink():
                raise CliError(f"symlink paths are not accepted: {current.name!r}")
        except OSError as exc:
            raise CliError(
                f"cannot inspect path component {current.name!r}: {exc}"
            ) from exc


def checked_root(value: str | os.PathLike[str]) -> Path:
    """Return an existing, non-symlink directory used as an I/O boundary."""

    raw = os.fspath(value)
    _reject_url(raw)
    supplied = _absolute_lexical(Path(raw).expanduser())
    if supplied.is_symlink():
        raise CliError("root directory must not itself be a symlink")
    try:
        root = supplied.resolve(strict=True)
        info = root.stat()
    except OSError as exc:
        raise CliError(f"cannot access root directory: {exc}") from exc
    if not stat.S_ISDIR(info.st_mode):
        raise CliError("root must be an existing directory")
    _reject_symlink_components(root)
    return root


def _within_root(candidate: Path, root: Path) -> None:
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise CliError("path escapes the declared root directory") from exc


def _suffix_matches(path: Path, suffixes: Iterable[str]) -> bool:
    lowered = path.name.lower()
    return any(lowered.endswith(suffix.lower()) for suffix in suffixes)


def checked_input_file(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    suffixes: Iterable[str],
    max_bytes: int,
) -> Path:
    """Return a bounded regular local file within root, rejecting symlinks."""

    raw = os.fspath(value)
    _reject_url(raw)
    root_path = checked_root(root)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root_path / path
    path = _absolute_lexical(path)
    if path.is_symlink():
        raise CliError(f"input must not be a symlink: {path.name!r}")
    try:
        resolved = path.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise CliError(f"cannot access input file {path.name!r}: {exc}") from exc
    _within_root(resolved, root_path)
    _reject_symlink_components(resolved)
    if not stat.S_ISREG(info.st_mode):
        raise CliError(f"input is not a regular file: {path.name!r}")
    if info.st_size > max_bytes:
        raise CliError(
            f"input {path.name!r} is {info.st_size} bytes; limit is {max_bytes}"
        )
    if not _suffix_matches(resolved, suffixes):
        allowed = ", ".join(sorted({suffix.lower() for suffix in suffixes}))
        raise CliError(f"input suffix must be one of: {allowed}")
    return resolved


def checked_output_file(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    suffixes: Iterable[str],
    force: bool = False,
) -> Path:
    """Return a local output path within root without following symlinks."""

    raw = os.fspath(value)
    _reject_url(raw)
    root_path = checked_root(root)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root_path / path
    path = _absolute_lexical(path)
    if path.name in {"", ".", ".."}:
        raise CliError("output must name a file")
    if not _suffix_matches(path, suffixes):
        allowed = ", ".join(sorted({suffix.lower() for suffix in suffixes}))
        raise CliError(f"output suffix must be one of: {allowed}")
    if path.is_symlink() or path.parent.is_symlink():
        raise CliError("output and its parent must not be symlinks")
    try:
        parent = path.parent.resolve(strict=True)
        parent_info = parent.stat()
    except OSError as exc:
        raise CliError(f"cannot access output parent: {exc}") from exc
    _within_root(parent, root_path)
    _reject_symlink_components(parent)
    if not stat.S_ISDIR(parent_info.st_mode):
        raise CliError("output parent must be an existing directory")
    destination = parent / path.name
    if destination.exists():
        if not destination.is_file():
            raise CliError("output exists and is not a regular file")
        if not force:
            raise CliError(f"refusing to overwrite existing output: {path.name!r}")
    return destination


def atomic_write_bytes(
    destination: str | os.PathLike[str],
    payload: bytes,
    *,
    root: str | os.PathLike[str] = ".",
    suffixes: Iterable[str],
    force: bool = False,
) -> Path:
    """Atomically write a private, bounded file."""

    if len(payload) > MAX_OUTPUT_BYTES:
        raise CliError(f"output is {len(payload)} bytes; limit is {MAX_OUTPUT_BYTES}")
    destination_path = checked_output_file(
        destination, root=root, suffixes=suffixes, force=force
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination_path.name}.",
        suffix=".tmp",
        dir=destination_path.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        if destination_path.exists() and not force:
            raise CliError(
                f"refusing to overwrite existing output: {destination_path.name!r}"
            )
        os.replace(temporary, destination_path)
    finally:
        temporary.unlink(missing_ok=True)
    return destination_path


def strict_json_bytes(document: Any) -> bytes:
    """Serialize deterministic RFC-compatible JSON."""

    try:
        payload = (
            json.dumps(
                document,
                indent=2,
                sort_keys=True,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CliError(f"report is not strict JSON: {exc}") from exc
    if len(payload) > MAX_OUTPUT_BYTES:
        raise CliError(f"report is {len(payload)} bytes; limit is {MAX_OUTPUT_BYTES}")
    return payload


def emit_json(
    document: Any,
    *,
    output: str | os.PathLike[str] | None = None,
    root: str | os.PathLike[str] = ".",
    force: bool = False,
) -> None:
    """Print strict JSON or atomically write it with private permissions."""

    payload = strict_json_bytes(document)
    if output is None:
        print(payload.decode("utf-8"), end="")
        return
    atomic_write_bytes(
        output,
        payload,
        root=root,
        suffixes={".json"},
        force=force,
    )


def load_json_object(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    max_bytes: int = MAX_JSON_BYTES,
) -> dict[str, Any]:
    """Load a bounded strict JSON object."""

    path = checked_input_file(
        value,
        root=root,
        suffixes={".json"},
        max_bytes=max_bytes,
    )
    try:
        with path.open("r", encoding="utf-8") as handle:
            document = json.load(
                handle,
                parse_constant=_reject_constant,
                object_pairs_hook=_unique_object,
            )
    except CliError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CliError(f"cannot read valid JSON from {path.name!r}: {exc}") from exc
    if not isinstance(document, dict):
        raise CliError("JSON root must be an object")
    return document


def validate_keys(
    value: Mapping[str, Any],
    *,
    allowed: Iterable[str],
    required: Iterable[str] = (),
    context: str,
) -> None:
    allowed_set = set(allowed)
    required_set = set(required)
    unknown = sorted(set(value) - allowed_set)
    missing = sorted(required_set - set(value))
    if unknown:
        raise CliError(f"{context} has unknown keys: {', '.join(unknown)}")
    if missing:
        raise CliError(f"{context} is missing keys: {', '.join(missing)}")


def bounded_int(
    value: Any,
    *,
    name: str,
    minimum: int,
    maximum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CliError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise CliError(f"{name} must be between {minimum} and {maximum}")
    return value


def finite_float(
    value: Any,
    *,
    name: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CliError(f"{name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise CliError(f"{name} must be finite")
    if minimum is not None and number < minimum:
        raise CliError(f"{name} must be at least {minimum}")
    if maximum is not None and number > maximum:
        raise CliError(f"{name} must be at most {maximum}")
    return number


def parse_name_list(value: str | None, *, name: str) -> list[str]:
    if value is None:
        return []
    names = [item.strip() for item in value.split(",")]
    if not names or any(not item for item in names):
        raise CliError(f"{name} must be a comma-separated list of nonempty names")
    if len(names) != len(set(names)):
        raise CliError(f"{name} must not contain duplicates")
    return names


def require_deidentified(confirmed: bool) -> None:
    if not confirmed:
        raise CliError(
            "local participant data require --deidentified; remove direct identifiers "
            "and review quasi-identifiers before use"
        )


def _read_header(reader: Any) -> list[str]:
    try:
        header = next(reader)
    except StopIteration as exc:
        raise CliError("CSV is empty") from exc
    if not header or any(not name.strip() for name in header):
        raise CliError("CSV header names must be nonempty")
    header = [name.strip() for name in header]
    if len(header) != len(set(header)):
        raise CliError("CSV header names must be unique")
    if len(header) > MAX_CHANNELS:
        raise CliError(f"CSV has {len(header)} columns; limit is {MAX_CHANNELS}")
    return header


def read_numeric_columns(
    path: Path,
    columns: Sequence[str],
    *,
    max_rows: int = MAX_ROWS,
    allow_missing: bool = False,
) -> tuple[dict[str, list[float | None]], list[str], int]:
    """Read selected numeric CSV columns after bounded structural validation."""

    if not 1 <= max_rows <= MAX_ROWS:
        raise CliError(f"max_rows must be between 1 and {MAX_ROWS}")
    if not columns or len(columns) > MAX_SELECTED_COLUMNS:
        raise CliError(f"select between 1 and {MAX_SELECTED_COLUMNS} numeric columns")
    if len(columns) != len(set(columns)):
        raise CliError("selected columns must be unique")
    selected: dict[str, list[float | None]] = {name: [] for name in columns}
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = _read_header(reader)
            missing = [name for name in columns if name not in header]
            if missing:
                raise CliError(f"CSV is missing columns: {', '.join(missing)}")
            positions = {name: header.index(name) for name in columns}
            row_count = 0
            for row_count, row in enumerate(reader, start=1):
                if row_count > max_rows:
                    raise CliError(f"CSV exceeds the row limit of {max_rows}")
                if len(row) != len(header):
                    raise CliError(
                        f"CSV row {row_count + 1} has {len(row)} cells; "
                        f"expected {len(header)}"
                    )
                for name, position in positions.items():
                    cell = row[position].strip()
                    if len(cell) > MAX_CELL_CHARS:
                        raise CliError(
                            f"CSV cell in column {name!r} exceeds "
                            f"{MAX_CELL_CHARS} characters"
                        )
                    if cell.lower() in MISSING_TOKENS:
                        if allow_missing:
                            selected[name].append(None)
                            continue
                        raise CliError(
                            f"column {name!r} contains a missing value at data row "
                            f"{row_count}; segment or apply a documented bounded "
                            "imputation policy before processing"
                        )
                    try:
                        number = float(cell)
                    except ValueError as exc:
                        raise CliError(
                            f"column {name!r} contains non-numeric data at data row "
                            f"{row_count}"
                        ) from exc
                    if not math.isfinite(number):
                        raise CliError(
                            f"column {name!r} contains a non-finite value at data row "
                            f"{row_count}"
                        )
                    selected[name].append(number)
    except CliError:
        raise
    except (OSError, UnicodeError, csv.Error) as exc:
        raise CliError(f"cannot read bounded CSV: {exc}") from exc
    if row_count == 0:
        raise CliError("CSV has a header but no data rows")
    return selected, header, row_count


def _format_csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return format(value, ".12g")
    item = getattr(value, "item", None)
    if callable(item):
        converted = item()
        if converted is not value:
            return _format_csv_value(converted)
    text = str(value)
    if len(text) > MAX_CELL_CHARS:
        raise CliError("output CSV cell is too large")
    return text


def csv_bytes(columns: Sequence[str], rows: Iterable[Sequence[Any]]) -> bytes:
    """Serialize a deterministic UTF-8 CSV with Unix newlines."""

    if not columns or len(columns) > MAX_CHANNELS:
        raise CliError(f"CSV output must have 1 to {MAX_CHANNELS} columns")
    if len(columns) != len(set(columns)):
        raise CliError("CSV output columns must be unique")
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(columns)
    count = 0
    for count, row in enumerate(rows, start=1):
        if count > MAX_ROWS:
            raise CliError(f"CSV output exceeds the row limit of {MAX_ROWS}")
        values = list(row)
        if len(values) != len(columns):
            raise CliError("CSV output row length does not match columns")
        writer.writerow([_format_csv_value(value) for value in values])
        if buffer.tell() > MAX_OUTPUT_BYTES:
            raise CliError(f"CSV output exceeds {MAX_OUTPUT_BYTES} bytes")
    if count == 0:
        raise CliError("refusing to write a CSV without data rows")
    payload = buffer.getvalue().encode("utf-8")
    if len(payload) > MAX_OUTPUT_BYTES:
        raise CliError(f"CSV output exceeds {MAX_OUTPUT_BYTES} bytes")
    return payload


def write_csv(
    destination: str | os.PathLike[str],
    columns: Sequence[str],
    rows: Iterable[Sequence[Any]],
    *,
    root: str | os.PathLike[str] = ".",
    force: bool = False,
) -> bytes:
    payload = csv_bytes(columns, rows)
    atomic_write_bytes(
        destination,
        payload,
        root=root,
        suffixes={".csv"},
        force=force,
    )
    return payload


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def json_number(value: Any) -> float | int | None:
    """Return a finite JSON scalar from Python or NumPy numeric input."""

    item = getattr(value, "item", None)
    if callable(item):
        value = item()
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def dataframe_rows(frame: Any) -> Iterable[Sequence[Any]]:
    """Yield rows without importing pandas at module import time."""

    return frame.itertuples(index=False, name=None)


def run_cli(function: Any) -> int:
    """Run a CLI body with concise expected-error handling."""

    try:
        function()
    except CliError as exc:
        print(f"error: {exc}", file=os.sys.stderr)
        return 2
    except ModuleNotFoundError as exc:
        package = exc.name or "a required package"
        print(
            f"error: missing dependency {package!r}; install the pinned environment "
            f"with: {PINNED_INSTALL}",
            file=os.sys.stderr,
        )
        return 2
    except ImportError as exc:
        print(f"error: optional dependency unavailable: {exc}", file=os.sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("error: interrupted", file=os.sys.stderr)
        return 130
    return 0
```

### `scripts/ecg_hrv_pipeline.py`

```python
#!/usr/bin/env python3
"""Run a bounded ECG processing and duration-aware HRV workflow."""

from __future__ import annotations

import argparse
from typing import Any

from _common import (
    MAX_CSV_BYTES,
    MAX_ROWS,
    NEUROKIT2_VERSION,
    PINNED_INSTALL,
    CliError,
    checked_input_file,
    dataframe_rows,
    emit_json,
    finite_float,
    json_number,
    parse_name_list,
    read_numeric_columns,
    require_deidentified,
    run_cli,
    sha256_bytes,
    write_csv,
)

ECG_METHODS = (
    "neurokit",
    "pantompkins1985",
    "hamilton2002",
    "elgendi2010",
    "engzeemod2012",
)
HRV_DOMAINS = {"time", "frequency", "nonlinear"}


def _row_to_json(frame: Any) -> dict[str, float | int | None]:
    if len(frame) != 1:
        raise CliError("expected one-row HRV output")
    return {str(column): json_number(frame.iloc[0][column]) for column in frame.columns}


def _summary(values: Any) -> dict[str, float | int | None]:
    finite = values[values.notna()] if hasattr(values, "notna") else values
    if len(finite) == 0:
        return {"count": 0, "maximum": None, "mean": None, "minimum": None}
    return {
        "count": len(finite),
        "maximum": json_number(finite.max()),
        "mean": json_number(finite.mean()),
        "minimum": json_number(finite.min()),
    }


def _artifact_counts(info: dict[str, Any]) -> dict[str, int]:
    result: dict[str, int] = {}
    for name in ("ectopic", "missed", "extra", "longshort"):
        value = info.get(f"ECG_fixpeaks_{name}", [])
        try:
            result[name] = len(value)
        except TypeError:
            result[name] = 0
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Process a bounded deidentified ECG CSV or a reproducible synthetic "
            "signal with NeuroKit2 0.2.13, report peak correction and quality, "
            "and gate HRV domains by duration and beat count."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="local .csv input")
    source.add_argument("--synthetic", action="store_true")
    parser.add_argument("--column", default="ECG")
    parser.add_argument("--sampling-rate", type=float, required=True, help="Hz")
    parser.add_argument("--method", choices=ECG_METHODS, default="neurokit")
    parser.add_argument(
        "--domains",
        default="time",
        help="comma-separated subset of time,frequency,nonlinear",
    )
    parser.add_argument(
        "--duration", type=float, default=60.0, help="synthetic seconds"
    )
    parser.add_argument("--heart-rate", type=float, default=70.0, help="synthetic BPM")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-rows", type=int, default=MAX_ROWS)
    parser.add_argument(
        "--deidentified",
        action="store_true",
        help="required with --input",
    )
    parser.add_argument("--signals-output", help="optional processed local .csv")
    parser.add_argument("--output", help="optional local .json report")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sampling_rate = finite_float(
        args.sampling_rate,
        name="--sampling-rate",
        minimum=20.0,
        maximum=20_000.0,
    )
    domains = set(parse_name_list(args.domains, name="--domains"))
    unknown = sorted(domains - HRV_DOMAINS)
    if unknown:
        raise CliError(f"unknown HRV domains: {', '.join(unknown)}")
    if not domains:
        raise CliError("select at least one HRV domain")
    if not 1 <= args.max_rows <= MAX_ROWS:
        raise CliError(f"--max-rows must be between 1 and {MAX_ROWS}")
    if not -(2**31) <= args.seed < 2**31:
        raise CliError("--seed must be a signed 32-bit integer")

    import neurokit2 as nk
    import numpy as np

    installed = str(nk.__version__)
    if installed != NEUROKIT2_VERSION:
        raise CliError(
            f"this reproducible workflow requires NeuroKit2 {NEUROKIT2_VERSION}; "
            f"found {installed}. Install with: {PINNED_INSTALL}"
        )

    if args.input:
        require_deidentified(args.deidentified)
        path = checked_input_file(
            args.input,
            root=args.root,
            suffixes={".csv"},
            max_bytes=MAX_CSV_BYTES,
        )
        selected, _, row_count = read_numeric_columns(
            path,
            [args.column],
            max_rows=args.max_rows,
        )
        ecg = np.asarray(selected[args.column], dtype=float)
        source = "deidentified_local_csv"
    else:
        duration = finite_float(
            args.duration,
            name="--duration",
            minimum=5.0,
            maximum=3600.0,
        )
        heart_rate = finite_float(
            args.heart_rate,
            name="--heart-rate",
            minimum=20.0,
            maximum=240.0,
        )
        if not sampling_rate.is_integer():
            raise CliError(
                "--sampling-rate must be an integer for NeuroKit2 synthetic ECG"
            )
        row_count = round(duration * sampling_rate)
        if not 1 <= row_count <= args.max_rows:
            raise CliError(f"synthetic row count must be between 1 and {args.max_rows}")
        try:
            ecg = nk.ecg_simulate(
                duration=duration,
                sampling_rate=int(sampling_rate),
                heart_rate=heart_rate,
                random_state=args.seed,
            )
        except (TypeError, ValueError, RuntimeError) as exc:
            raise CliError(f"synthetic ECG generation failed: {exc}") from exc
        row_count = len(ecg)
        source = "neurokit2_synthetic"

    duration_s = len(ecg) / sampling_rate
    if duration_s < 5:
        raise CliError("ECG must contain at least 5 seconds for this pipeline")
    try:
        signals, info = nk.ecg_process(
            ecg,
            sampling_rate=sampling_rate,
            method=args.method,
        )
    except (TypeError, ValueError, RuntimeError, IndexError) as exc:
        raise CliError(f"ECG processing failed: {exc}") from exc
    peaks = info.get("ECG_R_Peaks")
    if peaks is None or len(peaks) < 3:
        raise CliError("fewer than three R-peaks were detected")
    beat_count = len(peaks)

    warnings: list[str] = []
    hrv: dict[str, dict[str, float | int | None]] = {}
    if "time" in domains:
        if beat_count < 20:
            warnings.append("time-domain HRV skipped: fewer than 20 detected beats")
        else:
            try:
                hrv["time"] = _row_to_json(
                    nk.hrv_time(info, sampling_rate=sampling_rate)
                )
            except (TypeError, ValueError, RuntimeError, ZeroDivisionError) as exc:
                warnings.append(f"time-domain HRV failed: {exc}")
        if duration_s < 300:
            warnings.append(
                "time-domain HRV is shorter than the conventional 5-minute "
                "short-term recording; metric-specific validation is required"
            )
    if "frequency" in domains:
        if duration_s < 120 or beat_count < 50:
            warnings.append(
                "frequency-domain HRV skipped: require at least 120 seconds and "
                "50 detected beats in this conservative CLI"
            )
        else:
            try:
                hrv["frequency"] = _row_to_json(
                    nk.hrv_frequency(info, sampling_rate=sampling_rate)
                )
            except (TypeError, ValueError, RuntimeError, ZeroDivisionError) as exc:
                warnings.append(f"frequency-domain HRV failed: {exc}")
            if duration_s < 300:
                warnings.append(
                    "frequency-domain HRV is below the conventional 5-minute "
                    "short-term window; do not interpret VLF/ULF and justify bands"
                )
    if "nonlinear" in domains:
        if beat_count < 100:
            warnings.append(
                "nonlinear HRV skipped: fewer than 100 detected beats; many "
                "entropy/fractal metrics need substantially more"
            )
        else:
            try:
                hrv["nonlinear"] = _row_to_json(
                    nk.hrv_nonlinear(info, sampling_rate=sampling_rate)
                )
            except (TypeError, ValueError, RuntimeError, ZeroDivisionError) as exc:
                warnings.append(f"nonlinear HRV failed: {exc}")

    artifact_counts = _artifact_counts(info)
    corrected_total = sum(artifact_counts.values())
    if corrected_total:
        warnings.append(
            "R-peak corrections were applied by ecg_process(); inspect the raw "
            "trace, uncorrected peaks, and correction categories"
        )
    if source == "deidentified_local_csv":
        warnings.append(
            "input amplitude units are not inferred; record sensor units, lead, "
            "gain, filters, and clock metadata separately"
        )

    report: dict[str, Any] = {
        "artifact_correction": {
            "algorithm": "Lipponen-Tarvainen via ecg_process(correct_artifacts=True)",
            "category_counts": artifact_counts,
            "corrected_event_count_sum": corrected_total,
            "uncorrected_peak_count": len(info.get("ECG_R_Peaks_Uncorrected", peaks)),
        },
        "detected_r_peaks": beat_count,
        "duration_s": duration_s,
        "hrv": hrv,
        "hrv_requested_domains": sorted(domains),
        "neurokit2_version": installed,
        "output_schema_observed": {
            "info_keys": sorted(str(key) for key in info),
            "signal_columns": [str(column) for column in signals.columns],
        },
        "path_redacted": True,
        "quality": _summary(signals["ECG_Quality"]),
        "research_use_only": True,
        "row_count": row_count,
        "sampling_rate_hz": sampling_rate,
        "source": source,
        "warning": (
            "This output is for research and education, not diagnosis, patient "
            "monitoring, or medical-device validation. Validate the detector, "
            "sensor, population, protocol, and artifact policy for the intended use."
        ),
        "warnings": warnings,
    }
    if args.signals_output:
        payload = write_csv(
            args.signals_output,
            [str(column) for column in signals.columns],
            dataframe_rows(signals),
            root=args.root,
            force=args.force,
        )
        report["signals_csv"] = {
            "path_redacted": True,
            "sha256": sha256_bytes(payload),
        }
    emit_json(report, output=args.output, root=args.root, force=args.force)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
```

### `scripts/eda_pipeline.py`

```python
#!/usr/bin/env python3
"""Run an explicit, bounded EDA cleaning/decomposition/SCR workflow."""

from __future__ import annotations

import argparse
import statistics
from typing import Any

from _common import (
    MAX_CSV_BYTES,
    MAX_ROWS,
    NEUROKIT2_VERSION,
    PINNED_INSTALL,
    CliError,
    checked_input_file,
    dataframe_rows,
    emit_json,
    finite_float,
    json_number,
    read_numeric_columns,
    require_deidentified,
    run_cli,
    sha256_bytes,
    write_csv,
)

CLEAN_METHODS = ("neurokit", "biosppy", "none")
PHASIC_METHODS = ("highpass", "smoothmedian", "cvxeda", "sparseda")
PEAK_METHODS = ("neurokit", "gamboa2008", "kim2004", "vanhalem2020", "nabian2018")


def _finite_values(values: Any) -> list[float]:
    result: list[float] = []
    for value in values:
        number = json_number(value)
        if number is not None:
            result.append(float(number))
    return result


def _stats(values: Any) -> dict[str, float | int | None]:
    finite = _finite_values(values)
    return {
        "count": len(finite),
        "maximum": max(finite) if finite else None,
        "mean": statistics.fmean(finite) if finite else None,
        "median": statistics.median(finite) if finite else None,
        "minimum": min(finite) if finite else None,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Clean, explicitly decompose, and detect SCRs in bounded "
            "deidentified EDA CSV data or a reproducible synthetic signal using "
            "NeuroKit2 0.2.13."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="local .csv input")
    source.add_argument("--synthetic", action="store_true")
    parser.add_argument("--column", default="EDA")
    parser.add_argument("--sampling-rate", type=float, required=True, help="Hz")
    parser.add_argument("--clean-method", choices=CLEAN_METHODS, default="neurokit")
    parser.add_argument("--phasic-method", choices=PHASIC_METHODS, default="highpass")
    parser.add_argument("--peak-method", choices=PEAK_METHODS, default="neurokit")
    parser.add_argument(
        "--amplitude-min",
        type=float,
        default=0.1,
        help="relative-to-largest SCR threshold for neurokit/kim2004",
    )
    parser.add_argument(
        "--sympathetic-method",
        choices=("none", "posada", "ghiasi"),
        default="none",
    )
    parser.add_argument("--unit", default="unspecified")
    parser.add_argument(
        "--duration", type=float, default=60.0, help="synthetic seconds"
    )
    parser.add_argument("--scr-number", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-rows", type=int, default=MAX_ROWS)
    parser.add_argument(
        "--deidentified",
        action="store_true",
        help="required with --input",
    )
    parser.add_argument("--signals-output", help="optional processed local .csv")
    parser.add_argument("--output", help="optional local .json report")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sampling_rate = finite_float(
        args.sampling_rate,
        name="--sampling-rate",
        minimum=1.0,
        maximum=5000.0,
    )
    amplitude_min = finite_float(
        args.amplitude_min,
        name="--amplitude-min",
        minimum=0.0,
        maximum=1.0,
    )
    if not 1 <= args.max_rows <= MAX_ROWS:
        raise CliError(f"--max-rows must be between 1 and {MAX_ROWS}")
    if not 0 <= args.scr_number <= 10_000:
        raise CliError("--scr-number must be between 0 and 10000")
    if not -(2**31) <= args.seed < 2**31:
        raise CliError("--seed must be a signed 32-bit integer")
    if not args.unit or len(args.unit) > 32:
        raise CliError("--unit must be a nonempty string of at most 32 characters")

    import neurokit2 as nk
    import numpy as np
    import pandas as pd

    installed = str(nk.__version__)
    if installed != NEUROKIT2_VERSION:
        raise CliError(
            f"this reproducible workflow requires NeuroKit2 {NEUROKIT2_VERSION}; "
            f"found {installed}. Install with: {PINNED_INSTALL}"
        )

    if args.input:
        require_deidentified(args.deidentified)
        path = checked_input_file(
            args.input,
            root=args.root,
            suffixes={".csv"},
            max_bytes=MAX_CSV_BYTES,
        )
        selected, _, row_count = read_numeric_columns(
            path,
            [args.column],
            max_rows=args.max_rows,
        )
        raw = np.asarray(selected[args.column], dtype=float)
        source = "deidentified_local_csv"
    else:
        duration = finite_float(
            args.duration,
            name="--duration",
            minimum=5.0,
            maximum=3600.0,
        )
        if not sampling_rate.is_integer():
            raise CliError(
                "--sampling-rate must be an integer for NeuroKit2 synthetic EDA"
            )
        row_count = round(duration * sampling_rate)
        if not 1 <= row_count <= args.max_rows:
            raise CliError(f"synthetic row count must be between 1 and {args.max_rows}")
        try:
            raw = nk.eda_simulate(
                length=row_count,
                sampling_rate=int(sampling_rate),
                scr_number=args.scr_number,
                random_state=args.seed,
            )
        except (TypeError, ValueError, RuntimeError) as exc:
            raise CliError(f"synthetic EDA generation failed: {exc}") from exc
        row_count = len(raw)
        source = "neurokit2_synthetic"

    duration_s = len(raw) / sampling_rate
    try:
        clean = nk.eda_clean(
            raw,
            sampling_rate=sampling_rate,
            method=args.clean_method,
        )
        components = nk.eda_phasic(
            clean,
            sampling_rate=sampling_rate,
            method=args.phasic_method,
        )
        peak_signals, peak_info = nk.eda_peaks(
            components["EDA_Phasic"],
            sampling_rate=sampling_rate,
            method=args.peak_method,
            amplitude_min=amplitude_min,
        )
    except (TypeError, ValueError, RuntimeError, IndexError) as exc:
        raise CliError(f"EDA processing failed: {exc}") from exc

    signals = pd.concat(
        [
            pd.DataFrame({"EDA_Raw": raw, "EDA_Clean": clean}),
            components.reset_index(drop=True),
            peak_signals.reset_index(drop=True),
        ],
        axis=1,
    )
    amplitudes = _finite_values(peak_info.get("SCR_Amplitude", []))
    scr_count = len(peak_info.get("SCR_Peaks", []))
    warnings: list[str] = []
    if args.phasic_method == "cvxeda":
        warnings.append(
            "cvxEDA requires the optional cvxopt dependency; report its version "
            "and validate decomposition parameters"
        )
    if source == "deidentified_local_csv" and args.unit == "unspecified":
        warnings.append(
            "EDA units were not declared; do not interpret amplitudes as "
            "microsiemens without acquisition metadata"
        )
    if scr_count == 0:
        warnings.append(
            "no SCR peaks were detected; inspect signal orientation and quality"
        )
    sympathetic: dict[str, float | int | None] | None = None
    if args.sympathetic_method != "none":
        if duration_s < 64:
            warnings.append(
                "EDA sympathetic index skipped: this CLI requires at least 64 seconds"
            )
        else:
            try:
                result = nk.eda_sympathetic(
                    clean,
                    sampling_rate=sampling_rate,
                    method=args.sympathetic_method,
                    show=False,
                )
                sympathetic = {
                    str(key): json_number(value) for key, value in result.items()
                }
            except (TypeError, ValueError, RuntimeError, ZeroDivisionError) as exc:
                warnings.append(f"EDA sympathetic index failed: {exc}")

    report: dict[str, Any] = {
        "duration_s": duration_s,
        "input_unit": args.unit,
        "methods": {
            "clean": args.clean_method,
            "decomposition": args.phasic_method,
            "peak_detection": args.peak_method,
            "peak_threshold_relative_to_largest": amplitude_min,
            "sympathetic": args.sympathetic_method,
        },
        "neurokit2_version": installed,
        "output_schema_observed": {
            "info_keys": sorted(str(key) for key in peak_info),
            "signal_columns": [str(column) for column in signals.columns],
        },
        "path_redacted": True,
        "research_use_only": True,
        "row_count": row_count,
        "sampling_rate_hz": sampling_rate,
        "scr": {
            "amplitude": _stats(amplitudes),
            "count": scr_count,
        },
        "source": source,
        "sympathetic": sympathetic,
        "tonic": _stats(signals["EDA_Tonic"]),
        "warning": (
            "EDA features are method-, sensor-, site-, unit-, and population-dependent. "
            "This output is not diagnosis, monitoring, or medical-device validation."
        ),
        "warnings": warnings,
    }
    if args.signals_output:
        payload = write_csv(
            args.signals_output,
            [str(column) for column in signals.columns],
            dataframe_rows(signals),
            root=args.root,
            force=args.force,
        )
        report["signals_csv"] = {
            "path_redacted": True,
            "sha256": sha256_bytes(payload),
        }
    emit_json(report, output=args.output, root=args.root, force=args.force)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
```

### `scripts/generate_synthetic.py`

```python
#!/usr/bin/env python3
"""Generate deterministic, dependency-free synthetic biosignal CSV fixtures."""

from __future__ import annotations

import argparse
import math
import random
from collections.abc import Sequence
from typing import Any

from _common import (
    MAX_ROWS,
    CliError,
    emit_json,
    finite_float,
    parse_name_list,
    run_cli,
    sha256_bytes,
    write_csv,
)

MODALITIES = ("ecg", "ppg", "rsp", "eda", "emg", "trigger")
UNITS = {
    "time_s": "s",
    "ecg": "arbitrary_unit",
    "ppg": "arbitrary_unit",
    "rsp": "arbitrary_unit",
    "eda": "arbitrary_unit",
    "emg": "arbitrary_unit",
    "trigger": "binary",
}


def _gaussian(phase: float, center: float, width: float) -> float:
    distance = min(abs(phase - center), 1.0 - abs(phase - center))
    return math.exp(-0.5 * (distance / width) ** 2)


def _event_times(duration: float, interval: float) -> list[float]:
    first = interval
    return [
        first + index * interval
        for index in range(max(0, int((duration - first) // interval) + 1))
        if first + index * interval < duration
    ]


def generate_rows(
    *,
    duration: float,
    sampling_rate: float,
    heart_rate: float,
    respiratory_rate: float,
    modalities: Sequence[str],
    seed: int,
    event_interval: float,
) -> tuple[list[str], list[list[float]], list[float]]:
    """Return deterministic analytic fixtures, not validated physiology."""

    samples = round(duration * sampling_rate)
    if not 1 <= samples <= MAX_ROWS:
        raise CliError(f"synthetic row count must be between 1 and {MAX_ROWS}")
    rng = random.Random(seed)
    events = _event_times(duration, event_interval)
    cardiac_period = 60.0 / heart_rate
    respiratory_period = 60.0 / respiratory_rate
    columns = ["time_s", *modalities]
    rows: list[list[float]] = []

    for sample in range(samples):
        time_s = sample / sampling_rate
        cardiac_phase = (time_s % cardiac_period) / cardiac_period
        respiratory_phase = (time_s % respiratory_period) / respiratory_period
        values: dict[str, float] = {}

        if "ecg" in modalities:
            values["ecg"] = (
                0.12 * _gaussian(cardiac_phase, 0.18, 0.025)
                - 0.15 * _gaussian(cardiac_phase, 0.36, 0.012)
                + 1.00 * _gaussian(cardiac_phase, 0.40, 0.010)
                - 0.25 * _gaussian(cardiac_phase, 0.43, 0.014)
                + 0.30 * _gaussian(cardiac_phase, 0.68, 0.055)
                + rng.gauss(0.0, 0.008)
            )
        if "ppg" in modalities:
            pulse = max(0.0, math.sin(math.pi * cardiac_phase)) ** 2.5
            notch = 0.12 * _gaussian(cardiac_phase, 0.72, 0.035)
            values["ppg"] = pulse - notch + rng.gauss(0.0, 0.006)
        if "rsp" in modalities:
            values["rsp"] = math.sin(2 * math.pi * respiratory_phase) + rng.gauss(
                0.0, 0.01
            )
        if "eda" in modalities:
            phasic = 0.0
            for event_time in events:
                elapsed = time_s - event_time
                if elapsed >= 0:
                    phasic += (1.0 - math.exp(-elapsed / 0.45)) * math.exp(
                        -elapsed / 2.2
                    )
            values["eda"] = (
                1.0 + 0.002 * time_s + 0.15 * phasic + rng.gauss(0.0, 0.0015)
            )
        if "emg" in modalities:
            active = any(0.5 <= time_s - event_time < 1.2 for event_time in events)
            scale = 0.16 if active else 0.01
            values["emg"] = rng.gauss(0.0, scale)
        if "trigger" in modalities:
            values["trigger"] = (
                1.0
                if any(
                    0 <= time_s - event_time < max(0.02, 2.0 / sampling_rate)
                    for event_time in events
                )
                else 0.0
            )
        rows.append([time_s, *(values[name] for name in modalities)])
    return columns, rows, events


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic local CSV of analytic biosignal-like fixtures. "
            "The output is for software tests and education, not physiological validation."
        )
    )
    parser.add_argument("--output", required=True, help="local .csv output path")
    parser.add_argument("--root", default=".", help="existing local I/O boundary")
    parser.add_argument("--duration", type=float, default=30.0, help="seconds")
    parser.add_argument("--sampling-rate", type=float, default=250.0, help="Hz")
    parser.add_argument("--heart-rate", type=float, default=70.0, help="beats/min")
    parser.add_argument(
        "--respiratory-rate", type=float, default=15.0, help="breaths/min"
    )
    parser.add_argument(
        "--modalities",
        default="ecg,rsp,eda,trigger",
        help=f"comma-separated subset of: {', '.join(MODALITIES)}",
    )
    parser.add_argument("--event-interval", type=float, default=5.0, help="seconds")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--report", help="optional local .json report path")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    duration = finite_float(
        args.duration, name="--duration", minimum=0.1, maximum=3600.0
    )
    sampling_rate = finite_float(
        args.sampling_rate,
        name="--sampling-rate",
        minimum=1.0,
        maximum=5000.0,
    )
    heart_rate = finite_float(
        args.heart_rate, name="--heart-rate", minimum=20.0, maximum=240.0
    )
    respiratory_rate = finite_float(
        args.respiratory_rate,
        name="--respiratory-rate",
        minimum=2.0,
        maximum=80.0,
    )
    event_interval = finite_float(
        args.event_interval,
        name="--event-interval",
        minimum=0.5,
        maximum=3600.0,
    )
    modalities = parse_name_list(args.modalities, name="--modalities")
    unknown = sorted(set(modalities) - set(MODALITIES))
    if unknown:
        raise CliError(f"unknown modalities: {', '.join(unknown)}")
    if not modalities:
        raise CliError("select at least one modality")
    if not -(2**31) <= args.seed < 2**31:
        raise CliError("--seed must be a signed 32-bit integer")

    columns, rows, event_times = generate_rows(
        duration=duration,
        sampling_rate=sampling_rate,
        heart_rate=heart_rate,
        respiratory_rate=respiratory_rate,
        modalities=modalities,
        seed=args.seed,
        event_interval=event_interval,
    )
    payload = write_csv(
        args.output,
        columns,
        rows,
        root=args.root,
        force=args.force,
    )
    report: dict[str, Any] = {
        "artifact": "synthetic_biosignal_fixture",
        "columns": columns,
        "duration_s": duration,
        "event_onsets_s": event_times,
        "path_redacted": True,
        "physiological_validation": False,
        "row_count": len(rows),
        "sampling_rate_hz": sampling_rate,
        "seed": args.seed,
        "sha256": sha256_bytes(payload),
        "units": {column: UNITS[column] for column in columns},
        "warning": (
            "Analytic waveforms are deterministic software fixtures; they do not "
            "validate a sensor, method, population, diagnosis, or medical device."
        ),
    }
    emit_json(report, output=args.report, root=args.root, force=args.force)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
```

### `scripts/inspect_signal.py`

```python
#!/usr/bin/env python3
"""Inspect bounded local biosignal CSV structure without exposing row values."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path
from typing import Any

from _common import (
    MAX_CELL_CHARS,
    MAX_CHANNELS,
    MAX_CSV_BYTES,
    MAX_ROWS,
    MISSING_TOKENS,
    CliError,
    checked_input_file,
    emit_json,
    finite_float,
    parse_name_list,
    require_deidentified,
    run_cli,
)


class OnlineStats:
    def __init__(self) -> None:
        self.numeric = 0
        self.missing = 0
        self.nonfinite = 0
        self.nonnumeric = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.minimum = math.inf
        self.maximum = -math.inf
        self.previous: float | None = None
        self.transitions = 0
        self.flat_transitions = 0
        self.flat_run = 0
        self.max_flat_run = 0
        self.gap_run = 0
        self.max_gap_run = 0

    def add_cell(self, cell: str) -> float | None:
        normalized = cell.strip()
        if normalized.lower() in MISSING_TOKENS:
            self.missing += 1
            self.gap_run += 1
            self.max_gap_run = max(self.max_gap_run, self.gap_run)
            self.previous = None
            self.flat_run = 0
            return None
        try:
            value = float(normalized)
        except ValueError:
            self.nonnumeric += 1
            self.gap_run += 1
            self.max_gap_run = max(self.max_gap_run, self.gap_run)
            self.previous = None
            self.flat_run = 0
            return None
        if not math.isfinite(value):
            self.nonfinite += 1
            self.gap_run += 1
            self.max_gap_run = max(self.max_gap_run, self.gap_run)
            self.previous = None
            self.flat_run = 0
            return None

        self.gap_run = 0
        self.numeric += 1
        delta = value - self.mean
        self.mean += delta / self.numeric
        self.m2 += delta * (value - self.mean)
        self.minimum = min(self.minimum, value)
        self.maximum = max(self.maximum, value)
        if self.previous is not None:
            self.transitions += 1
            if value == self.previous:
                self.flat_transitions += 1
                self.flat_run += 1
            else:
                self.flat_run = 0
            self.max_flat_run = max(self.max_flat_run, self.flat_run)
        self.previous = value
        return value

    def report(self, unit: str | None) -> dict[str, Any]:
        variance = self.m2 / (self.numeric - 1) if self.numeric > 1 else None
        return {
            "flat_transition_fraction": (
                self.flat_transitions / self.transitions if self.transitions else None
            ),
            "maximum": self.maximum if self.numeric else None,
            "max_flat_run_samples": self.max_flat_run + 1 if self.max_flat_run else 0,
            "max_gap_run_samples": self.max_gap_run,
            "mean": self.mean if self.numeric else None,
            "minimum": self.minimum if self.numeric else None,
            "missing_count": self.missing,
            "nonfinite_count": self.nonfinite,
            "nonnumeric_count": self.nonnumeric,
            "numeric_count": self.numeric,
            "sample_sd": math.sqrt(variance) if variance is not None else None,
            "unit": unit or "unspecified",
        }


def _parse_units(value: str | None, selected: list[str]) -> dict[str, str]:
    if value is None:
        return {}
    result: dict[str, str] = {}
    for item in value.split(","):
        if "=" not in item:
            raise CliError("--units entries must use COLUMN=UNIT")
        column, unit = (part.strip() for part in item.split("=", 1))
        if not column or not unit:
            raise CliError("--units entries must have nonempty column and unit")
        if column in result:
            raise CliError(f"duplicate unit declaration for {column!r}")
        if column not in selected:
            raise CliError(f"unit declared for unselected column {column!r}")
        if len(unit) > 32 or any(ord(character) < 32 for character in unit):
            raise CliError("units must be short printable strings")
        result[column] = unit
    return result


def inspect_csv(
    path: Path,
    *,
    selected_names: list[str] | None,
    time_column: str | None,
    declared_sampling_rate: float | None,
    units_value: str | None,
    max_rows: int,
    max_channels: int,
) -> dict[str, Any]:
    if not 1 <= max_rows <= MAX_ROWS:
        raise CliError(f"--max-rows must be between 1 and {MAX_ROWS}")
    if not 1 <= max_channels <= MAX_CHANNELS:
        raise CliError(f"--max-channels must be between 1 and {MAX_CHANNELS}")

    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except (OSError, UnicodeError) as exc:
        raise CliError(f"cannot open CSV: {exc}") from exc
    with handle:
        reader = csv.reader(handle)
        try:
            header = [name.strip() for name in next(reader)]
        except StopIteration as exc:
            raise CliError("CSV is empty") from exc
        if not header or any(not name for name in header):
            raise CliError("CSV header names must be nonempty")
        if len(header) != len(set(header)):
            raise CliError("CSV header names must be unique")
        if len(header) > max_channels:
            raise CliError(
                f"CSV has {len(header)} columns; --max-channels is {max_channels}"
            )
        if time_column is not None and time_column not in header:
            raise CliError(f"time column {time_column!r} is absent")
        selected = selected_names or []
        if not selected:
            raise CliError("no signal columns selected")
        if len(selected) > max_channels:
            raise CliError(
                f"selected {len(selected)} columns; --max-channels is {max_channels}"
            )
        missing = [name for name in selected if name not in header]
        if missing:
            raise CliError(f"CSV is missing selected columns: {', '.join(missing)}")
        if time_column in selected:
            raise CliError("--time-column must not also be a signal column")
        units = _parse_units(units_value, selected)
        positions = {name: header.index(name) for name in selected}
        time_position = header.index(time_column) if time_column else None
        stats = {name: OnlineStats() for name in selected}
        time_stats = OnlineStats() if time_column else None
        positive_deltas: list[float] = []
        previous_time: float | None = None
        duplicate_times = 0
        backward_times = 0
        row_count = 0

        try:
            for row_count, row in enumerate(reader, start=1):
                if row_count > max_rows:
                    raise CliError(f"CSV exceeds --max-rows={max_rows}")
                if len(row) != len(header):
                    raise CliError(
                        f"CSV row {row_count + 1} has {len(row)} cells; "
                        f"expected {len(header)}"
                    )
                for cell in row:
                    if len(cell) > MAX_CELL_CHARS:
                        raise CliError(
                            f"CSV row {row_count + 1} contains a cell longer than "
                            f"{MAX_CELL_CHARS} characters"
                        )
                for name, position in positions.items():
                    stats[name].add_cell(row[position])
                if time_position is not None and time_stats is not None:
                    time_value = time_stats.add_cell(row[time_position])
                    if time_value is not None and previous_time is not None:
                        delta = time_value - previous_time
                        if delta > 0:
                            positive_deltas.append(delta)
                        elif delta == 0:
                            duplicate_times += 1
                        else:
                            backward_times += 1
                    if time_value is not None:
                        previous_time = time_value
        except csv.Error as exc:
            raise CliError(f"cannot parse CSV: {exc}") from exc

    if row_count == 0:
        raise CliError("CSV has a header but no data rows")

    observed_sampling_rate: float | None = None
    median_delta: float | None = None
    maximum_relative_jitter: float | None = None
    if positive_deltas:
        median_delta = statistics.median(positive_deltas)
        if median_delta > 0:
            observed_sampling_rate = 1.0 / median_delta
            maximum_relative_jitter = max(
                abs(delta - median_delta) / median_delta for delta in positive_deltas
            )

    duration_s: float | None = None
    effective_rate = observed_sampling_rate or declared_sampling_rate
    if effective_rate and row_count > 1:
        duration_s = (row_count - 1) / effective_rate

    channel_reports = {name: stats[name].report(units.get(name)) for name in selected}
    warnings: list[str] = []
    for name, report in channel_reports.items():
        invalid = (
            report["missing_count"]
            + report["nonfinite_count"]
            + report["nonnumeric_count"]
        )
        if invalid:
            warnings.append(
                f"{name}: {invalid} missing, non-finite, or non-numeric samples"
            )
        flat_fraction = report["flat_transition_fraction"]
        if isinstance(flat_fraction, float) and flat_fraction > 0.20:
            warnings.append(
                f"{name}: more than 20% of adjacent finite samples are identical"
            )
    if duplicate_times:
        warnings.append("time column contains duplicate timestamps")
    if backward_times:
        warnings.append("time column contains backward timestamps")
    if (
        declared_sampling_rate
        and observed_sampling_rate
        and abs(observed_sampling_rate - declared_sampling_rate)
        / declared_sampling_rate
        > 0.01
    ):
        warnings.append(
            "observed timestamp rate differs from declared sampling rate by more than 1%"
        )
    if maximum_relative_jitter is not None and maximum_relative_jitter > 0.01:
        warnings.append("timestamp intervals vary by more than 1% from the median")

    return {
        "channel_count_in_file": len(header),
        "channels": channel_reports,
        "declared_sampling_rate_hz": declared_sampling_rate,
        "duration_s_estimate": duration_s,
        "observed_sampling_rate_hz": observed_sampling_rate,
        "path_redacted": True,
        "research_use_only": True,
        "row_count": row_count,
        "selected_columns": selected,
        "time": {
            "backward_step_count": backward_times,
            "duplicate_count": duplicate_times,
            "maximum_relative_interval_jitter": maximum_relative_jitter,
            "median_interval_s": median_delta,
            "name": time_column,
            "stats": time_stats.report("s") if time_stats else None,
        },
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect a bounded local CSV for numeric coverage, gaps, flat runs, "
            "timestamp order, and sampling-rate consistency. Row values and paths "
            "are never emitted."
        )
    )
    parser.add_argument("--input", required=True, help="local .csv input")
    parser.add_argument("--root", default=".", help="existing local I/O boundary")
    parser.add_argument(
        "--columns",
        required=True,
        help="explicit comma-separated signal columns",
    )
    parser.add_argument("--time-column", help="numeric time column in seconds")
    parser.add_argument(
        "--sampling-rate", type=float, help="declared sampling rate in Hz"
    )
    parser.add_argument(
        "--units", help="comma-separated COLUMN=UNIT declarations, e.g. ECG=mV,EDA=uS"
    )
    parser.add_argument("--max-rows", type=int, default=MAX_ROWS)
    parser.add_argument("--max-channels", type=int, default=32)
    parser.add_argument(
        "--deidentified",
        action="store_true",
        help="confirm direct and reviewed quasi-identifiers were removed",
    )
    parser.add_argument("--output", help="optional local .json report")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    require_deidentified(args.deidentified)
    declared_rate = (
        finite_float(
            args.sampling_rate,
            name="--sampling-rate",
            minimum=0.01,
            maximum=1_000_000.0,
        )
        if args.sampling_rate is not None
        else None
    )
    path = checked_input_file(
        args.input,
        root=args.root,
        suffixes={".csv"},
        max_bytes=MAX_CSV_BYTES,
    )
    report = inspect_csv(
        path,
        selected_names=parse_name_list(args.columns, name="--columns"),
        time_column=args.time_column,
        declared_sampling_rate=declared_rate,
        units_value=args.units,
        max_rows=args.max_rows,
        max_channels=args.max_channels,
    )
    emit_json(report, output=args.output, root=args.root, force=args.force)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
```

### `scripts/plan_epochs.py`

```python
#!/usr/bin/env python3
"""Plan sample-exact event epochs without loading NeuroKit2."""

from __future__ import annotations

import argparse
import math
from typing import Any

from _common import (
    MAX_CSV_BYTES,
    MAX_ROWS,
    CliError,
    checked_input_file,
    emit_json,
    finite_float,
    read_numeric_columns,
    require_deidentified,
    run_cli,
)

MAX_EVENTS = 100_000


def _parse_events(value: str) -> list[float]:
    pieces = [piece.strip() for piece in value.split(",")]
    if not pieces or any(not piece for piece in pieces):
        raise CliError("--events must be a comma-separated numeric list")
    if len(pieces) > MAX_EVENTS:
        raise CliError(f"event count exceeds {MAX_EVENTS}")
    events: list[float] = []
    for index, piece in enumerate(pieces, start=1):
        try:
            event = float(piece)
        except ValueError as exc:
            raise CliError(f"event {index} is not numeric") from exc
        if not math.isfinite(event) or event < 0:
            raise CliError(f"event {index} must be finite and nonnegative")
        events.append(event)
    return events


def _sample_offset(seconds: float, sampling_rate: float, *, name: str) -> int:
    exact = seconds * sampling_rate
    rounded = round(exact)
    if not math.isclose(exact, rounded, rel_tol=0.0, abs_tol=1e-8):
        raise CliError(
            f"{name}={seconds} s is not sample-aligned at {sampling_rate} Hz "
            f"({exact} samples)"
        )
    return int(rounded)


def _event_samples(
    values: list[float],
    *,
    unit: str,
    sampling_rate: float,
) -> list[int]:
    samples: list[int] = []
    for index, value in enumerate(values, start=1):
        if unit == "samples":
            rounded = round(value)
            if not math.isclose(value, rounded, rel_tol=0.0, abs_tol=1e-9):
                raise CliError(f"event {index} is not an integer sample index: {value}")
            sample = int(rounded)
        else:
            sample = _sample_offset(value, sampling_rate, name=f"event {index} onset")
        samples.append(sample)
    return samples


def plan(
    events: list[int],
    *,
    recording_samples: int,
    sampling_rate: float,
    epoch_start_s: float,
    epoch_end_s: float,
    baseline_start_s: float | None,
    baseline_end_s: float | None,
    boundary_policy: str,
) -> dict[str, Any]:
    start_offset = _sample_offset(epoch_start_s, sampling_rate, name="--epoch-start")
    end_offset = _sample_offset(epoch_end_s, sampling_rate, name="--epoch-end")
    if end_offset <= start_offset:
        raise CliError("--epoch-end must be after --epoch-start")
    if recording_samples < 1 or recording_samples > MAX_ROWS:
        raise CliError(f"--recording-samples must be between 1 and {MAX_ROWS}")

    baseline: dict[str, Any] | None = None
    if (baseline_start_s is None) != (baseline_end_s is None):
        raise CliError("provide both --baseline-start and --baseline-end")
    if baseline_start_s is not None and baseline_end_s is not None:
        baseline_start = _sample_offset(
            baseline_start_s, sampling_rate, name="--baseline-start"
        )
        baseline_end = _sample_offset(
            baseline_end_s, sampling_rate, name="--baseline-end"
        )
        if not start_offset <= baseline_start < baseline_end <= end_offset:
            raise CliError("baseline must be a nonempty subset of the epoch")
        if baseline_end > 0:
            raise CliError("baseline must not extend after event onset")
        baseline = {
            "end_offset_samples_exclusive": baseline_end,
            "end_s_exclusive": baseline_end_s,
            "sample_count": baseline_end - baseline_start,
            "start_offset_samples": baseline_start,
            "start_s": baseline_start_s,
        }

    rows: list[dict[str, Any]] = []
    invalid = 0
    for ordinal, onset in enumerate(events, start=1):
        start = onset + start_offset
        end = onset + end_offset
        before = max(0, -start)
        after = max(0, end - recording_samples)
        complete = before == 0 and after == 0
        if not complete:
            invalid += 1
        if boundary_policy == "drop" and not complete:
            continue
        rows.append(
            {
                "complete": complete,
                "end_sample_exclusive": end,
                "event_ordinal": ordinal,
                "onset_sample": onset,
                "pad_after_samples": after,
                "pad_before_samples": before,
                "start_sample": start,
            }
        )
    if boundary_policy == "error" and invalid:
        raise CliError(f"{invalid} event(s) would cross recording boundaries")

    warnings: list[str] = []
    if events != sorted(events):
        warnings.append("event onsets are not sorted")
    if len(events) != len(set(events)):
        warnings.append("duplicate event onsets are present")
    if invalid:
        warnings.append(
            f"{invalid} event(s) cross a boundary; NeuroKit2 0.2.13 pads "
            "non-integer signal columns with NaN"
        )

    return {
        "baseline": baseline,
        "boundary_policy": boundary_policy,
        "event_count_input": len(events),
        "event_count_output": len(rows),
        "events": rows,
        "indexing": {
            "event_onsets": "zero-based sample indices",
            "window": "[start_sample, end_sample_exclusive)",
        },
        "neurokit2_epoch_note": (
            "epochs_create() slices the end sample exclusively but labels its "
            "floating time index with an inclusive epochs_end endpoint. Its "
            "baseline_correction=True subtracts the mean from epoch start through "
            "t=0; use manual correction for a narrower baseline."
        ),
        "recording_samples": recording_samples,
        "sampling_rate_hz": sampling_rate,
        "window": {
            "end_offset_samples_exclusive": end_offset,
            "end_s_exclusive": epoch_end_s,
            "sample_count": end_offset - start_offset,
            "start_offset_samples": start_offset,
            "start_s": epoch_start_s,
        },
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan zero-based, sample-exact event epochs and boundary handling. "
            "No signal values or NeuroKit2 imports are required."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--events", help="comma-separated onsets")
    source.add_argument("--events-csv", help="bounded local CSV containing onsets")
    parser.add_argument("--onset-column", default="onset")
    parser.add_argument(
        "--event-unit", choices=("samples", "seconds"), default="samples"
    )
    parser.add_argument("--sampling-rate", type=float, required=True, help="Hz")
    parser.add_argument("--recording-samples", type=int, required=True)
    parser.add_argument("--epoch-start", type=float, required=True, help="seconds")
    parser.add_argument("--epoch-end", type=float, required=True, help="seconds")
    parser.add_argument("--baseline-start", type=float, help="seconds")
    parser.add_argument("--baseline-end", type=float, help="seconds")
    parser.add_argument(
        "--boundary-policy",
        choices=("report", "drop", "error"),
        default="report",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--deidentified",
        action="store_true",
        help="required with --events-csv",
    )
    parser.add_argument("--max-events", type=int, default=MAX_EVENTS)
    parser.add_argument("--output", help="optional local .json report")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sampling_rate = finite_float(
        args.sampling_rate,
        name="--sampling-rate",
        minimum=0.01,
        maximum=1_000_000.0,
    )
    epoch_start = finite_float(args.epoch_start, name="--epoch-start")
    epoch_end = finite_float(args.epoch_end, name="--epoch-end")
    baseline_start = (
        finite_float(args.baseline_start, name="--baseline-start")
        if args.baseline_start is not None
        else None
    )
    baseline_end = (
        finite_float(args.baseline_end, name="--baseline-end")
        if args.baseline_end is not None
        else None
    )
    if not 1 <= args.max_events <= MAX_EVENTS:
        raise CliError(f"--max-events must be between 1 and {MAX_EVENTS}")

    if args.events_csv:
        require_deidentified(args.deidentified)
        path = checked_input_file(
            args.events_csv,
            root=args.root,
            suffixes={".csv"},
            max_bytes=MAX_CSV_BYTES,
        )
        data, _, row_count = read_numeric_columns(
            path,
            [args.onset_column],
            max_rows=args.max_events,
        )
        if row_count > args.max_events:
            raise CliError(f"event count exceeds {args.max_events}")
        values = [float(value) for value in data[args.onset_column]]
    else:
        values = _parse_events(args.events)
        if len(values) > args.max_events:
            raise CliError(f"event count exceeds {args.max_events}")

    event_samples = _event_samples(
        values,
        unit=args.event_unit,
        sampling_rate=sampling_rate,
    )
    report = plan(
        event_samples,
        recording_samples=args.recording_samples,
        sampling_rate=sampling_rate,
        epoch_start_s=epoch_start,
        epoch_end_s=epoch_end,
        baseline_start_s=baseline_start,
        baseline_end_s=baseline_end,
        boundary_policy=args.boundary_policy,
    )
    report["input_event_unit"] = args.event_unit
    report["path_redacted"] = True
    emit_json(report, output=args.output, root=args.root, force=args.force)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
```

### `scripts/validate_multimodal.py`

```python
#!/usr/bin/env python3
"""Validate bounded multimodal stream schemas and temporal alignment."""

from __future__ import annotations

import argparse
import math
import re
import statistics
from itertools import pairwise
from pathlib import Path
from typing import Any

from _common import (
    MAX_CSV_BYTES,
    MAX_ROWS,
    CliError,
    checked_input_file,
    checked_root,
    emit_json,
    finite_float,
    load_json_object,
    read_numeric_columns,
    require_deidentified,
    run_cli,
    validate_keys,
)

MAX_STREAMS = 16
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$")
SYNC_METHODS = {
    "hardware_trigger",
    "shared_clock",
    "timestamp",
    "validated_manual",
}


def _stream_profile(
    stream: dict[str, Any],
    *,
    root: Path,
    max_rows: int,
) -> tuple[dict[str, Any], list[str], list[str]]:
    validate_keys(
        stream,
        allowed={
            "name",
            "path",
            "value_column",
            "time_column",
            "sampling_rate_hz",
            "unit",
            "start_time_s",
        },
        required={"name", "path", "value_column", "sampling_rate_hz", "unit"},
        context="stream",
    )
    name = stream["name"]
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        raise CliError("stream name must be a short identifier beginning with a letter")
    for key in ("path", "value_column", "unit"):
        if not isinstance(stream[key], str) or not stream[key].strip():
            raise CliError(f"stream {name!r} {key} must be a nonempty string")
    if len(stream["unit"]) > 32:
        raise CliError(f"stream {name!r} unit is too long")
    time_column = stream.get("time_column")
    if time_column is not None and (
        not isinstance(time_column, str) or not time_column.strip()
    ):
        raise CliError(f"stream {name!r} time_column must be a nonempty string")
    if time_column is not None and "start_time_s" in stream:
        raise CliError(
            f"stream {name!r} must not combine time_column with start_time_s"
        )
    declared_rate = finite_float(
        stream["sampling_rate_hz"],
        name=f"{name}.sampling_rate_hz",
        minimum=0.01,
        maximum=1_000_000.0,
    )
    start_time = (
        finite_float(stream["start_time_s"], name=f"{name}.start_time_s")
        if "start_time_s" in stream
        else 0.0
    )
    path = checked_input_file(
        stream["path"],
        root=root,
        suffixes={".csv"},
        max_bytes=MAX_CSV_BYTES,
    )
    columns = [stream["value_column"]]
    if time_column is not None:
        columns.append(time_column)
    values, _, row_count = read_numeric_columns(
        path,
        columns,
        max_rows=max_rows,
        allow_missing=True,
    )
    signal = values[stream["value_column"]]
    missing_count = sum(value is None for value in signal)
    finite_signal = [float(value) for value in signal if value is not None]
    flat_count = sum(
        current == previous for previous, current in pairwise(finite_signal)
    )
    flat_fraction = (
        flat_count / (len(finite_signal) - 1) if len(finite_signal) > 1 else None
    )
    errors: list[str] = []
    warnings: list[str] = []
    observed_rate: float | None = None
    interval_jitter: float | None = None

    if time_column is not None:
        raw_times = values[time_column]
        if any(value is None for value in raw_times):
            errors.append("time column contains missing values")
            times = [float(value) for value in raw_times if value is not None]
        else:
            times = [float(value) for value in raw_times]
        if len(times) >= 2:
            deltas = [current - previous for previous, current in pairwise(times)]
            if any(delta <= 0 for delta in deltas):
                errors.append("timestamps are not strictly increasing")
            positive = [delta for delta in deltas if delta > 0]
            if positive:
                median_delta = statistics.median(positive)
                observed_rate = 1.0 / median_delta
                interval_jitter = max(
                    abs(delta - median_delta) / median_delta for delta in positive
                )
            start_time = times[0]
            end_time = times[-1]
        else:
            errors.append("fewer than two valid timestamps")
            end_time = start_time
    else:
        end_time = start_time + (row_count - 1) / declared_rate

    if observed_rate is not None:
        relative_rate_error = abs(observed_rate - declared_rate) / declared_rate
        if relative_rate_error > 0.01:
            errors.append(
                "observed timestamp rate differs from declared rate by more than 1%"
            )
    if interval_jitter is not None and interval_jitter > 0.01:
        warnings.append("timestamp interval jitter exceeds 1% of the median")
    if missing_count:
        warnings.append(f"{missing_count} signal values are missing")
    if flat_fraction is not None and flat_fraction > 0.20:
        warnings.append("more than 20% of adjacent finite signal values are identical")

    profile = {
        "declared_sampling_rate_hz": declared_rate,
        "duration_s": max(0.0, end_time - start_time),
        "end_time_s": end_time,
        "flat_transition_fraction": flat_fraction,
        "missing_count": missing_count,
        "name": name,
        "observed_sampling_rate_hz": observed_rate,
        "path_redacted": True,
        "row_count": row_count,
        "start_time_s": start_time,
        "timestamp_maximum_relative_jitter": interval_jitter,
        "unit": stream["unit"],
    }
    return profile, errors, warnings


def validate_manifest(
    document: dict[str, Any],
    *,
    root: Path,
    max_rows: int,
) -> dict[str, Any]:
    validate_keys(
        document,
        allowed={"schema_version", "streams", "alignment"},
        required={"schema_version", "streams", "alignment"},
        context="manifest",
    )
    if document["schema_version"] != "1.0":
        raise CliError("schema_version must be '1.0'")
    streams = document["streams"]
    if not isinstance(streams, list) or not 1 <= len(streams) <= MAX_STREAMS:
        raise CliError(f"streams must contain 1 to {MAX_STREAMS} objects")
    if any(not isinstance(stream, dict) for stream in streams):
        raise CliError("every stream must be an object")
    alignment = document["alignment"]
    if not isinstance(alignment, dict):
        raise CliError("alignment must be an object")
    validate_keys(
        alignment,
        allowed={
            "reference_stream",
            "synchronization",
            "max_start_offset_ms",
            "minimum_overlap_s",
        },
        required={
            "reference_stream",
            "synchronization",
            "max_start_offset_ms",
            "minimum_overlap_s",
        },
        context="alignment",
    )
    if alignment["synchronization"] not in SYNC_METHODS:
        raise CliError(
            "alignment.synchronization must be one of: "
            + ", ".join(sorted(SYNC_METHODS))
        )
    max_offset_ms = finite_float(
        alignment["max_start_offset_ms"],
        name="alignment.max_start_offset_ms",
        minimum=0.0,
        maximum=60_000.0,
    )
    minimum_overlap_s = finite_float(
        alignment["minimum_overlap_s"],
        name="alignment.minimum_overlap_s",
        minimum=0.0,
        maximum=31_536_000.0,
    )

    profiles: list[dict[str, Any]] = []
    errors: list[str] = []
    warnings: list[str] = []
    for index, stream in enumerate(streams, start=1):
        try:
            profile, stream_errors, stream_warnings = _stream_profile(
                stream, root=root, max_rows=max_rows
            )
        except CliError as exc:
            raise CliError(f"stream {index}: {exc}") from exc
        profiles.append(profile)
        errors.extend(f"{profile['name']}: {message}" for message in stream_errors)
        warnings.extend(f"{profile['name']}: {message}" for message in stream_warnings)

    names = [profile["name"] for profile in profiles]
    if len(names) != len(set(names)):
        raise CliError("stream names must be unique")
    reference_name = alignment["reference_stream"]
    if reference_name not in names:
        raise CliError("alignment.reference_stream is not a stream name")
    reference = next(
        profile for profile in profiles if profile["name"] == reference_name
    )

    start_offsets_ms: dict[str, float] = {}
    for profile in profiles:
        offset_ms = (profile["start_time_s"] - reference["start_time_s"]) * 1000.0
        start_offsets_ms[profile["name"]] = offset_ms
        if abs(offset_ms) > max_offset_ms:
            errors.append(
                f"{profile['name']}: start offset {offset_ms:.6g} ms exceeds "
                f"{max_offset_ms:.6g} ms"
            )
    overlap_start = max(profile["start_time_s"] for profile in profiles)
    overlap_end = min(profile["end_time_s"] for profile in profiles)
    overlap_s = max(0.0, overlap_end - overlap_start)
    if overlap_s < minimum_overlap_s:
        errors.append(
            f"common overlap {overlap_s:.6g} s is below {minimum_overlap_s:.6g} s"
        )

    rates = [profile["declared_sampling_rate_hz"] for profile in profiles]
    counts = [profile["row_count"] for profile in profiles]
    same_rate = all(
        math.isclose(rate, rates[0], rel_tol=1e-9, abs_tol=1e-12) for rate in rates[1:]
    )
    same_count = all(count == counts[0] for count in counts[1:])
    no_missing = all(profile["missing_count"] == 0 for profile in profiles)
    starts_within_sample = all(
        abs(start_offsets_ms[profile["name"]])
        <= (500.0 / profile["declared_sampling_rate_hz"])
        for profile in profiles
    )
    bio_process_compatible = (
        same_rate and same_count and no_missing and starts_within_sample and not errors
    )
    if not same_rate:
        warnings.append(
            "native sampling rates differ; process at native rates, align clocks, "
            "then resample continuous channels to an explicit common grid"
        )
    if not bio_process_compatible:
        warnings.append(
            "do not pass these streams directly to bio_process(); NeuroKit2 "
            "0.2.13 does not synchronize or automatically resample inputs"
        )

    return {
        "alignment": {
            "common_overlap_s": overlap_s,
            "max_start_offset_ms": max_offset_ms,
            "minimum_overlap_s": minimum_overlap_s,
            "reference_stream": reference_name,
            "start_offsets_ms": start_offsets_ms,
            "synchronization": alignment["synchronization"],
        },
        "bio_process_direct_input_compatible": bio_process_compatible,
        "errors": errors,
        "path_redacted": True,
        "schema_version": "1.0",
        "streams": profiles,
        "valid": not errors,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a strict JSON manifest of bounded local biosignal CSV "
            "streams, units, clocks, rates, starts, overlap, and missingness."
        )
    )
    parser.add_argument("--manifest", required=True, help="local .json manifest")
    parser.add_argument("--root", default=".", help="existing local I/O boundary")
    parser.add_argument("--max-rows", type=int, default=MAX_ROWS)
    parser.add_argument(
        "--deidentified",
        action="store_true",
        help="confirm direct and reviewed quasi-identifiers were removed",
    )
    parser.add_argument("--output", help="optional local .json report")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    require_deidentified(args.deidentified)
    if not 1 <= args.max_rows <= MAX_ROWS:
        raise CliError(f"--max-rows must be between 1 and {MAX_ROWS}")
    root = checked_root(args.root)
    document = load_json_object(args.manifest, root=root)
    report = validate_manifest(document, root=root, max_rows=args.max_rows)
    emit_json(report, output=args.output, root=root, force=args.force)
    if not report["valid"]:
        raise CliError(
            f"multimodal validation failed with {len(report['errors'])} error(s)"
        )


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
```
