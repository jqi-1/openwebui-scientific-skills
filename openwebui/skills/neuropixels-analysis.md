---
name: neuropixels-analysis
description: For optional Claude API calls.
---

# Neuropixels Data Analysis

## Overview

Toolkit for analyzing Neuropixels high-density neural recordings using current best
practices from [SpikeInterface](https://spikeinterface.readthedocs.io/), the Allen
Institute, and the International Brain Laboratory (IBL). It covers the full workflow from
raw data to publication-ready curated units.

All examples use the real SpikeInterface API (`spikeinterface.full as si`) plus the
companion curation module (`spikeinterface.curation as sc`). The skill ships runnable
scripts in `scripts/` and a copy-and-edit template in `assets/` that implement this
workflow directly on top of SpikeInterface — there is no separate package to install
beyond the dependencies listed under [Installation](#installation).

## When to Use This Skill

This skill should be used when:
- Working with Neuropixels recordings (`.ap.bin`, `.lf.bin`, `.meta` files)
- Loading data from SpikeGLX, Open Ephys, or NWB formats
- Preprocessing neural recordings (filtering, common reference, bad-channel detection)
- Detecting and correcting motion/drift
- Running spike sorting (Kilosort4, SpykingCircus2, Mountainsort5, Tridesclous2)
- Computing quality metrics (SNR, ISI violations, presence ratio, amplitude cutoff)
- Curating units (threshold-based, model-based, or AI-assisted)
- Creating visualizations and exporting to Phy or NWB

## Supported Hardware & Formats

| Probe | Electrodes | Channels | Notes |
|-------|-----------|----------|-------|
| Neuropixels 1.0 | 960 | 384 | Use `phase_shift` for ADC correction |
| Neuropixels 2.0 (single) | 1280 | 384 | Denser geometry |
| Neuropixels 2.0 (4-shank) | 5120 | 384 | Multi-region recording |

| Format | Extension | Reader |
|--------|-----------|--------|
| SpikeGLX | `.ap.bin`, `.lf.bin`, `.meta` | `si.read_spikeglx()` |
| Open Ephys | `.continuous`, `.oebin` | `si.read_openephys()` |
| NWB | `.nwb` | `si.read_nwb()` |

## Quick Start

### Import and configure parallel processing

```python
import spikeinterface.full as si

# Global job kwargs are reused by all parallelizable steps
si.set_global_job_kwargs(n_jobs=-1, chunk_duration="1s", progress_bar=True)
```

### Loading data

```python
# Inspect available streams first
stream_names, stream_ids = si.get_neo_streams("spikeglx", "/path/to/run_g0/")
print(stream_names)  # e.g. ['imec0.ap', 'imec0.lf', 'nidq']

# SpikeGLX (most common) — select the AP stream by name
recording = si.read_spikeglx("/path/to/run_g0/", stream_name="imec0.ap", load_sync_channel=False)

# Open Ephys
recording = si.read_openephys("/path/to/Record_Node_101/")

# For quick iteration, slice the first 60 s
fs = recording.get_sampling_frequency()
recording_sub = recording.frame_slice(0, int(60 * fs))
```

### Full pipeline (bundled script)

The repository ships an end-to-end pipeline built on SpikeInterface:

```bash
python scripts/neuropixels_pipeline.py /path/to/spikeglx/data output/ --sorter kilosort4 --curation allen
```

It performs load → preprocess → drift check → optional motion correction → sorting →
postprocessing → quality metrics → curation → export. Read the steps below to run them
interactively or customize the pipeline.

## Standard Analysis Workflow

### 1. Preprocessing

Recommended chain, following the SpikeInterface Neuropixels how-to (IBL-style destriping
with channel removal + common reference):

```python
rec = si.highpass_filter(recording, freq_min=400.0)
bad_channel_ids, channel_labels = si.detect_bad_channels(rec)
rec = rec.remove_channels(bad_channel_ids)
rec = si.phase_shift(rec)  # ADC phase correction (Neuropixels 1.0)
rec = si.common_reference(rec, operator="median", reference="global")
```

Save the preprocessed recording (Kilosort needs a binary file, and it speeds up reuse):

```python
rec = rec.save(folder="preprocessed/", format="binary")
```

### 2. Check and correct drift

Always inspect drift before sorting:

```python
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks

noise_levels = si.get_noise_levels(rec, return_in_uV=False)
peaks = detect_peaks(rec, method="locally_exclusive", noise_levels=noise_levels,
                     detect_threshold=5, radius_um=50.0)
peak_locations = localize_peaks(rec, peaks, method="center_of_mass")

# Visualize the drift raster
si.plot_drift_raster_map(peaks=peaks, peak_locations=peak_locations,
                         recording=rec, clim=(-50, 50))
```

Apply correction if needed (presets: `rigid_fast`, `kilosort_like`,
`nonrigid_accurate`, `nonrigid_fast_and_accurate`, `dredge`, `dredge_fast`):

```python
rec_corrected = si.correct_motion(rec, preset="nonrigid_fast_and_accurate", folder="motion/")
```

### 3. Spike sorting

```python
# Kilosort4 (recommended, requires a CUDA GPU)
sorting = si.run_sorter("kilosort4", rec_corrected, folder="ks4_output")

# CPU alternatives (internally developed, no external install)
sorting = si.run_sorter("spykingcircus2", rec_corrected, folder="sc2_output")
sorting = si.run_sorter("tridesclous2", rec_corrected, folder="tdc2_output")
sorting = si.run_sorter("mountainsort5", rec_corrected, folder="ms5_output")

# External sorters can run in containers without local install
sorting = si.run_sorter("kilosort2_5", rec_corrected, folder="ks25_output", docker_image=True)

print(si.installed_sorters())
```

> Note: `run_sorter` uses the `folder=` argument. The older `output_folder=` is deprecated.

### 4. Postprocessing

```python
analyzer = si.create_sorting_analyzer(sorting, rec_corrected, sparse=True,
                                      format="binary_folder", folder="analyzer/")

analyzer.compute("random_spikes", method="uniform", max_spikes_per_unit=500)
analyzer.compute("waveforms", ms_before=1.0, ms_after=2.0)
analyzer.compute("templates", operators=["average", "std"])
analyzer.compute("noise_levels")
analyzer.compute("spike_amplitudes")
analyzer.compute("correlograms", window_ms=50.0, bin_ms=1.0)
analyzer.compute("unit_locations", method="monopolar_triangulation")
analyzer.compute("template_similarity")

metric_names = ["firing_rate", "presence_ratio", "snr", "isi_violation", "amplitude_cutoff"]
analyzer.compute("quality_metrics", metric_names=metric_names)
metrics = analyzer.get_extension("quality_metrics").get_data()
```

### 5. Curation by metric thresholds

```python
# Allen-style query (note: column is isi_violations_ratio)
query = "(amplitude_cutoff < 0.1) & (isi_violations_ratio < 0.5) & (presence_ratio > 0.9)"
good_unit_ids = metrics.query(query).index.values
```

For reusable, multi-threshold logic with `allen` / `ibl` / `strict` presets, use the
bundled `scripts/compute_metrics.py`. See
[references/AUTOMATED_CURATION.md](references/AUTOMATED_CURATION.md) for details and the
Bombcell / UnitMatch tools.

### 6. Model-based curation (UnitRefine)

SpikeInterface can apply pretrained machine-learning classifiers from Hugging Face via the
`spikeinterface.curation` module. The UnitRefine models were trained on real Neuropixels
data (V1, SC, ALM):

```python
import spikeinterface.curation as sc

# 1) noise vs neural
noise_labels = sc.model_based_label_units(
    sorting_analyzer=analyzer,
    repo_id="SpikeInterface/UnitRefine_noise_neural_classifier",
    trust_model=True,
)
neural = analyzer.remove_units(noise_labels[noise_labels["prediction"] == "noise"].index)

# 2) single-unit (sua) vs multi-unit (mua) on the surviving units
sua_mua_labels = sc.model_based_label_units(
    sorting_analyzer=neural,
    repo_id="SpikeInterface/UnitRefine_sua_mua_classifier",
    trust_model=True,
)
```

Each call returns a DataFrame with `prediction` and `probability` (confidence) per unit.
`trust_model=True` (or an explicit `trusted=[...]` list) is required to load the `.skops`
model — only load models from sources you trust. Models trained on other brain
areas/datasets may not transfer; validate against a manually labelled subset.

### 7. AI-assisted curation (for uncertain units)

When running inside an agent such as Cursor or Claude Code, the agent can directly inspect
waveform/correlogram plots and give an expert read — no API setup required. Generate plots
and ask the agent to assess isolation quality.

For programmatic vision-model access, **read API keys from the environment — never hardcode
credentials in analysis scripts** (they leak into version control and logs):

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])  # set this in your shell, not in code
```

See [references/AI_CURATION.md](references/AI_CURATION.md) for the full pattern (rendering a
unit summary image, building the prompt, and parsing the response).

### 8. Export results

```python
# Keep only good units, then export
analyzer_clean = analyzer.select_units(good_unit_ids, folder="analyzer_clean/", format="binary_folder")

# Phy for manual review
si.export_to_phy(analyzer_clean, output_folder="phy_export/",
                 compute_pc_features=True, compute_amplitudes=True)

# Figures report
si.export_report(analyzer_clean, "report/", format="png")

# NWB
from spikeinterface.exporters import export_to_nwb
export_to_nwb(analyzer_clean, "output.nwb")

# Metrics table
metrics.to_csv("quality_metrics.csv")
```

## Common Pitfalls and Best Practices

1. **Always check drift** before spike sorting — drift > ~10 μm meaningfully degrades quality.
2. **Use `phase_shift`** for Neuropixels 1.0 to correct ADC sampling offsets.
3. **Save the preprocessed recording** with `rec.save(folder=...)` to avoid recomputation (Kilosort also needs a binary file).
4. **Use a GPU** for Kilosort4 — it is far faster than CPU sorters.
5. **Review uncertain units** — automated/model-based curation is a starting point, not a verdict.
6. **Combine approaches** — thresholds for clear cases, model/AI for borderline units.
7. **Document thresholds and model repo IDs** for reproducibility.
8. **Export to Phy** for critical experiments — human oversight is valuable.

## Key Parameters to Adjust

### Preprocessing
- `freq_min`: highpass cutoff (300–400 Hz typical)
- `detect_bad_channels`: returns `(bad_channel_ids, channel_labels)`

### Motion Correction
- `preset`: `nonrigid_fast_and_accurate` (balanced), `nonrigid_accurate` (severe drift), `dredge` (state of the art)

### Spike Sorting (Kilosort4)
- `batch_size`: samples per batch (60000 default)
- `nblocks`: drift blocks (increase for long, drifty recordings)
- `Th_universal` / `Th_learned`: detection thresholds (lower = more spikes)

### Quality Metrics
- `snr`: signal-to-noise cutoff (3–5 typical)
- `isi_violations_ratio`: refractory violations (0.01–0.5)
- `presence_ratio`: recording coverage (0.5–0.95)

## Bundled Resources

### scripts/explore_recording.py
Quick inspection of a recording (streams, channels, duration, bad channels):
```bash
python scripts/explore_recording.py /path/to/data
```

### scripts/preprocess_recording.py
Automated preprocessing:
```bash
python scripts/preprocess_recording.py /path/to/data --output preprocessed/
```

### scripts/run_sorting.py
Run spike sorting:
```bash
python scripts/run_sorting.py preprocessed/ --sorter kilosort4 --output sorting/
```

### scripts/compute_metrics.py
Compute quality metrics and apply curation:
```bash
python scripts/compute_metrics.py sorting/ preprocessed/ --output metrics/ --curation allen
```

### scripts/export_to_phy.py
Export to Phy for manual curation:
```bash
python scripts/export_to_phy.py metrics/analyzer --output phy_export/
```

### scripts/neuropixels_pipeline.py
Complete end-to-end pipeline (see [Quick Start](#full-pipeline-bundled-script)).

### assets/analysis_template.py
Complete, editable analysis template. Copy and customize:
```bash
cp assets/analysis_template.py my_analysis.py
# Edit the PARAMETERS section, then run
python my_analysis.py
```

## Detailed Reference Guides

| Topic | Reference |
|-------|-----------|
| Full workflow | [references/standard_workflow.md](references/standard_workflow.md) |
| API reference (SpikeInterface) | [references/api_reference.md](references/api_reference.md) |
| Plotting guide | [references/plotting_guide.md](references/plotting_guide.md) |
| Preprocessing | [references/PREPROCESSING.md](references/PREPROCESSING.md) |
| Spike sorting | [references/SPIKE_SORTING.md](references/SPIKE_SORTING.md) |
| Motion correction | [references/MOTION_CORRECTION.md](references/MOTION_CORRECTION.md) |
| Quality metrics | [references/QUALITY_METRICS.md](references/QUALITY_METRICS.md) |
| Automated & model-based curation | [references/AUTOMATED_CURATION.md](references/AUTOMATED_CURATION.md) |
| AI-assisted curation | [references/AI_CURATION.md](references/AI_CURATION.md) |
| Waveform analysis | [references/ANALYSIS.md](references/ANALYSIS.md) |

## Installation

Requires Python ≥ 3.10. Using [uv](https://docs.astral.sh/uv/) is recommended.

```bash
# Core packages (SpikeInterface bundles the curation/model tooling)
uv pip install "spikeinterface[full]" probeinterface neo

# Spike sorters
uv pip install kilosort          # Kilosort4 (CUDA GPU required)
uv pip install spykingcircus     # SpykingCircus (legacy; SpykingCircus2 ships with SpikeInterface)
uv pip install mountainsort5     # Mountainsort5 (CPU)

# Model-based curation (UnitRefine) downloads from Hugging Face
uv pip install "huggingface_hub" skops

# Optional: AI-assisted visual curation
uv pip install anthropic

# Optional: IBL tools and Bombcell
uv pip install ibl-neuropixel ibllib bombcell
```

For reproducible environments, pin versions (current as of 2026-06: `spikeinterface==0.104.3`,
`kilosort==4.1.7`, `probeinterface==0.3.2`, `neo==0.14.4`). Unpinned installs are fine for
quick experimentation but should be pinned in production pipelines.

## Project Structure

```
project/
├── raw_data/
│   └── recording_g0/
│       └── recording_g0_imec0/
│           ├── recording_g0_t0.imec0.ap.bin
│           └── recording_g0_t0.imec0.ap.meta
├── preprocessed/           # Saved preprocessed recording
├── motion/                 # Motion estimation results
├── sorting_output/         # Spike sorter output
├── analyzer/               # SortingAnalyzer (waveforms, metrics)
├── phy_export/             # For manual curation
├── ai_curation/            # AI analysis reports
└── results/
    ├── quality_metrics.csv
    ├── curation_labels.json
    └── output.nwb
```

## Additional Resources

- **SpikeInterface Docs**: https://spikeinterface.readthedocs.io/
- **Neuropixels Tutorial**: https://spikeinterface.readthedocs.io/en/stable/how_to/analyze_neuropixels.html
- **Model-based Curation Tutorial**: https://spikeinterface.readthedocs.io/en/stable/tutorials/curation/plot_1_automated_curation.html
- **UnitRefine Models (Hugging Face)**: https://huggingface.co/SpikeInterface
- **Kilosort4 GitHub**: https://github.com/MouseLand/Kilosort
- **IBL Neuropixel Tools**: https://github.com/int-brain-lab/ibl-neuropixel
- **Allen Institute ecephys**: https://github.com/AllenInstitute/ecephys_spike_sorting
- **Bombcell (Automated QC)**: https://github.com/Julie-Fabre/bombcell
- **Awesome Neuropixels**: https://github.com/Julie-Fabre/awesome_neuropixels

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/neuropixels-analysis/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/AI_CURATION.md`

# AI-Assisted Curation Reference

Use vision-language models to analyze spike-sorting visualizations for borderline units,
complementing quantitative quality metrics.

```
Traditional:  Metrics → Threshold → Labels
AI-Enhanced:  Metrics → Render plots → Vision model → Confidence → Labels
```

> **Credential safety:** never hardcode API keys in analysis scripts — they end up in
> version control and logs. Read them from environment variables that you set in your shell
> (e.g. `export ANTHROPIC_API_KEY=...`). All examples below follow this pattern.

## Agent integration (no API key needed)

When you run this skill inside an agent (Cursor, Claude Code, etc.), the agent can inspect
images directly. Generate a unit summary figure and ask the agent to assess it:

```python
import spikeinterface.widgets as sw
import matplotlib.pyplot as plt

sw.plot_unit_summary(analyzer, unit_id=0)
plt.savefig("unit_0_summary.png", dpi=150, bbox_inches="tight")
# Then ask the agent: "Is unit 0 a well-isolated single unit, MUA, or noise? Consider
# waveform consistency, the refractory gap in the autocorrelogram, and amplitude stability."
```

The agent can assess waveform shape/consistency, refractory-period violations, amplitude
stability over time, and overall isolation quality.

## Programmatic API access

### Render a unit summary image

```python
import io, base64
import matplotlib.pyplot as plt
import spikeinterface.widgets as sw

def render_unit_image(analyzer, unit_id) -> str:
    """Return a base64-encoded PNG summary for one unit."""
    fig = plt.figure(figsize=(12, 8))
    sw.plot_unit_summary(analyzer, unit_id=unit_id, figure=fig)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
```

### Anthropic (Claude) example

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])  # set in shell, not in code

PROMPT = (
    "You are an expert electrophysiologist curating a spike-sorted unit. "
    "Based on the waveform, template, autocorrelogram, amplitude-over-time, and ISI "
    "histogram, classify this unit as exactly one of: good (well-isolated single unit), "
    "mua (multi-unit), or noise. Reply with the label and a one-sentence justification."
)

def analyze_unit_visually(analyzer, unit_id, model="claude-opus-4-5"):
    img_b64 = render_unit_image(analyzer, unit_id)
    msg = client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image",
                 "source": {"type": "base64", "media_type": "image/png", "data": img_b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    return msg.content[0].text

print(analyze_unit_visually(analyzer, unit_id=0))
```

### OpenAI example

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def analyze_unit_visually_openai(analyzer, unit_id, model="gpt-4o"):
    img_b64 = render_unit_image(analyzer, unit_id)
    resp = client.responses.create(
        model=model,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": PROMPT},
                {"type": "input_image", "image_url": f"data:image/png;base64,{img_b64}"},
            ],
        }],
    )
    return resp.output_text
```

> Model names change frequently. Use your provider's current vision-capable model
> (e.g. a current Claude or GPT multimodal model) rather than an old preview ID.

## Cost optimization: only call the model on uncertain units

```python
uncertain = metrics.query(
    "snr > 2 and snr < 8 and isi_violations_ratio > 0.001 and isi_violations_ratio < 0.1"
).index.tolist()

ai_labels = {}
for uid in uncertain:
    ai_labels[uid] = analyze_unit_visually(analyzer, uid)
```

## Hybrid curation: metrics + AI

```python
def hybrid_curation(analyzer, metrics):
    labels = {}
    for unit_id in metrics.index:
        row = metrics.loc[unit_id]
        if row["snr"] > 10 and row["isi_violations_ratio"] < 0.001:
            labels[unit_id] = "good"          # clearly good from metrics
        elif row["snr"] < 1.5:
            labels[unit_id] = "noise"         # clearly noise from metrics
        else:
            labels[unit_id] = analyze_unit_visually(analyzer, unit_id)  # ask the model
    return labels
```

## What each panel tells you

| Panel | Content | What to look for |
|-------|---------|------------------|
| Waveforms | Individual spike waveforms | Consistency, shape |
| Template | Mean ± std | Clean negative peak, physiological shape |
| Autocorrelogram | Spike timing | Gap at 0 ms (refractory period) |
| Amplitudes | Amplitude over time | Stability, no drift |
| ISI histogram | Inter-spike intervals | Refractory gap < ~1.5 ms |

## Best Practices

1. **Use AI for uncertain cases** — don't spend API calls on obvious good/noise units.
2. **Combine with metrics and model-based curation** — AI supplements, not replaces,
   quantitative measures (see [AUTOMATED_CURATION.md](AUTOMATED_CURATION.md)).
3. **Keep a human in the loop** for important analyses.
4. **Record reasoning** for each decision for reproducibility.
5. **Never commit credentials** — keep keys in environment variables.

## References

- [Anthropic Vision API](https://docs.anthropic.com/en/docs/build-with-claude/vision)
- [OpenAI Vision/Images](https://platform.openai.com/docs/guides/images-vision)
- [SpikeInterface model-based curation](https://spikeinterface.readthedocs.io/en/stable/tutorials/curation/plot_1_automated_curation.html)
- [SpikeAgent](https://github.com/SpikeAgent/SpikeAgent) — AI-powered spike-sorting assistant

### `references/ANALYSIS.md`

# Post-Processing & Analysis Reference

Comprehensive guide to quality metrics, visualization, and analysis of sorted Neuropixels data.

## Sorting Analyzer

The `SortingAnalyzer` is the central object for post-processing.

### Create Analyzer
```python
import spikeinterface.full as si

# Create analyzer
analyzer = si.create_sorting_analyzer(
    sorting,
    recording,
    sparse=True,                    # Use sparse representation
    format='binary_folder',         # Storage format
    folder='analyzer_output'        # Save location
)
```

### Compute Extensions
```python
# Compute all standard extensions
analyzer.compute('random_spikes')       # Random spike selection
analyzer.compute('waveforms')           # Extract waveforms
analyzer.compute('templates')           # Compute templates
analyzer.compute('noise_levels')        # Noise estimation
analyzer.compute('principal_components')  # PCA
analyzer.compute('spike_amplitudes')    # Amplitude per spike
analyzer.compute('correlograms')        # Auto/cross correlograms
analyzer.compute('unit_locations')      # Unit locations
analyzer.compute('spike_locations')     # Per-spike locations
analyzer.compute('template_similarity') # Template similarity matrix
analyzer.compute('quality_metrics')     # Quality metrics

# Or compute multiple at once
analyzer.compute([
    'random_spikes', 'waveforms', 'templates', 'noise_levels',
    'principal_components', 'spike_amplitudes', 'correlograms',
    'unit_locations', 'quality_metrics'
])
```

### Save and Load
```python
# Save
analyzer.save_as(folder='analyzer_saved', format='binary_folder')

# Load
analyzer = si.load_sorting_analyzer('analyzer_saved')
```

## Quality Metrics

### Compute Metrics
```python
analyzer.compute('quality_metrics')
qm = analyzer.get_extension('quality_metrics').get_data()
print(qm)
```

### Available Metrics

| Metric | Description | Good Values |
|--------|-------------|-------------|
| `snr` | Signal-to-noise ratio | > 5 |
| `isi_violations_ratio` | ISI violation ratio | < 0.01 (1%) |
| `isi_violations_count` | ISI violation count | Low |
| `presence_ratio` | Fraction of recording with spikes | > 0.9 |
| `firing_rate` | Spikes per second | 0.1-50 Hz |
| `amplitude_cutoff` | Estimated missed spikes | < 0.1 |
| `amplitude_median` | Median spike amplitude | - |
| `amplitude_cv` | Coefficient of variation | < 0.5 |
| `drift_ptp` | Peak-to-peak drift (um) | < 40 |
| `drift_std` | Standard deviation of drift | < 10 |
| `drift_mad` | Median absolute deviation | < 10 |
| `sliding_rp_violation` | Sliding refractory period | < 0.05 |
| `sync_spike_2` | Synchrony with other units | < 0.5 |
| `isolation_distance` | Mahalanobis distance | > 20 |
| `l_ratio` | L-ratio (isolation) | < 0.1 |
| `d_prime` | Discriminability | > 5 |
| `nn_hit_rate` | Nearest neighbor hit rate | > 0.9 |
| `nn_miss_rate` | Nearest neighbor miss rate | < 0.1 |
| `silhouette_score` | Cluster silhouette | > 0.5 |

### Compute Specific Metrics
```python
analyzer.compute(
    'quality_metrics',
    metric_names=['snr', 'isi_violations_ratio', 'presence_ratio', 'firing_rate']
)
```

### Custom Quality Thresholds
```python
qm = analyzer.get_extension('quality_metrics').get_data()

# Define quality criteria
quality_criteria = {
    'snr': ('>', 5),
    'isi_violations_ratio': ('<', 0.01),
    'presence_ratio': ('>', 0.9),
    'firing_rate': ('>', 0.1),
    'amplitude_cutoff': ('<', 0.1),
}

# Filter good units
good_units = qm.query(
    "(snr > 5) & (isi_violations_ratio < 0.01) & (presence_ratio > 0.9)"
).index.tolist()

print(f"Good units: {len(good_units)}/{len(qm)}")
```

## Waveforms & Templates

### Extract Waveforms
```python
analyzer.compute('waveforms', ms_before=1.5, ms_after=2.5, max_spikes_per_unit=500)

# Get waveforms for a unit
waveforms = analyzer.get_extension('waveforms').get_waveforms(unit_id=0)
print(f"Shape: {waveforms.shape}")  # (n_spikes, n_samples, n_channels)
```

### Compute Templates
```python
analyzer.compute('templates', operators=['average', 'std', 'median'])

# Get template
templates_ext = analyzer.get_extension('templates')
template = templates_ext.get_unit_template(unit_id=0, operator='average')
```

### Template Similarity
```python
analyzer.compute('template_similarity')
sim = analyzer.get_extension('template_similarity').get_data()
# Matrix of cosine similarities between templates
```

## Unit Locations

### Compute Locations
```python
analyzer.compute('unit_locations', method='monopolar_triangulation')
locations = analyzer.get_extension('unit_locations').get_data()
print(locations)  # x, y coordinates per unit
```

### Spike Locations
```python
analyzer.compute('spike_locations', method='center_of_mass')
spike_locs = analyzer.get_extension('spike_locations').get_data()
```

### Location Methods
- `'center_of_mass'` - Fast, less accurate
- `'monopolar_triangulation'` - More accurate, slower
- `'grid_convolution'` - Good balance

## Correlograms

### Auto-correlograms
```python
analyzer.compute('correlograms', window_ms=50, bin_ms=1)
correlograms, bins = analyzer.get_extension('correlograms').get_data()

# correlograms shape: (n_units, n_units, n_bins)
# Auto-correlogram for unit i: correlograms[i, i, :]
# Cross-correlogram units i,j: correlograms[i, j, :]
```

## Visualization

### Probe Map
```python
si.plot_probe_map(recording, with_channel_ids=True)
```

### Unit Templates
```python
# All units
si.plot_unit_templates(analyzer)

# Specific units
si.plot_unit_templates(analyzer, unit_ids=[0, 1, 2])
```

### Waveforms
```python
# Plot waveforms with template
si.plot_unit_waveforms(analyzer, unit_ids=[0])

# Waveform density
si.plot_unit_waveforms_density_map(analyzer, unit_id=0)
```

### Raster Plot
```python
si.plot_rasters(sorting, time_range=(0, 10))  # First 10 seconds
```

### Amplitudes
```python
analyzer.compute('spike_amplitudes')
si.plot_amplitudes(analyzer)

# Distribution
si.plot_all_amplitudes_distributions(analyzer)
```

### Correlograms
```python
# Auto-correlograms
si.plot_autocorrelograms(analyzer, unit_ids=[0, 1, 2])

# Cross-correlograms
si.plot_crosscorrelograms(analyzer, unit_ids=[0, 1])
```

### Quality Metrics
```python
# Summary plot
si.plot_quality_metrics(analyzer)

# Specific metric distribution
import matplotlib.pyplot as plt
qm = analyzer.get_extension('quality_metrics').get_data()
plt.hist(qm['snr'], bins=50)
plt.xlabel('SNR')
plt.ylabel('Count')
```

### Unit Locations on Probe
```python
si.plot_unit_locations(analyzer)
```

### Drift Map
```python
si.plot_drift_raster(sorting, recording)
```

### Summary Plot
```python
# Comprehensive unit summary
si.plot_unit_summary(analyzer, unit_id=0)
```

## LFP Analysis

### Load LFP Data
```python
lfp = si.read_spikeglx('/path/to/data', stream_name='imec0.lf')
print(f"LFP: {lfp.get_sampling_frequency()} Hz")
```

### Basic LFP Processing
```python
# Downsample if needed
lfp_ds = si.resample(lfp, resample_rate=1000)

# Common average reference
lfp_car = si.common_reference(lfp_ds, reference='global', operator='median')
```

### Extract LFP Traces
```python
import numpy as np

# Get traces (channels x samples)
traces = lfp.get_traces(start_frame=0, end_frame=30000)

# Specific channels
traces = lfp.get_traces(channel_ids=[0, 1, 2])
```

### Spectral Analysis
```python
from scipy import signal
import matplotlib.pyplot as plt

# Get single channel
trace = lfp.get_traces(channel_ids=[0]).flatten()
fs = lfp.get_sampling_frequency()

# Power spectrum
freqs, psd = signal.welch(trace, fs, nperseg=4096)
plt.semilogy(freqs, psd)
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power')
plt.xlim(0, 100)
```

### Spectrogram
```python
f, t, Sxx = signal.spectrogram(trace, fs, nperseg=2048, noverlap=1024)
plt.pcolormesh(t, f, 10*np.log10(Sxx), shading='gouraud')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.ylim(0, 100)
plt.colorbar(label='Power (dB)')
```

## Export Formats

### Export to Phy
```python
si.export_to_phy(
    analyzer,
    output_folder='phy_export',
    compute_pc_features=True,
    compute_amplitudes=True,
    copy_binary=True
)
# Then: phy template-gui phy_export/params.py
```

### Export to NWB
```python
from spikeinterface.exporters import export_to_nwb

export_to_nwb(
    recording,
    sorting,
    'output.nwb',
    metadata=dict(
        session_description='Neuropixels recording',
        experimenter='Name',
        lab='Lab name',
        institution='Institution'
    )
)
```

### Export Report
```python
si.export_report(
    analyzer,
    output_folder='report',
    remove_if_exists=True,
    format='html'
)
```

## Complete Analysis Pipeline

```python
import spikeinterface.full as si

def analyze_sorting(recording, sorting, output_dir):
    """Complete post-processing pipeline."""

    # Create analyzer
    analyzer = si.create_sorting_analyzer(
        sorting, recording,
        sparse=True,
        folder=f'{output_dir}/analyzer'
    )

    # Compute all extensions
    print("Computing extensions...")
    analyzer.compute(['random_spikes', 'waveforms', 'templates', 'noise_levels'])
    analyzer.compute(['principal_components', 'spike_amplitudes'])
    analyzer.compute(['correlograms', 'unit_locations', 'template_similarity'])
    analyzer.compute('quality_metrics')

    # Get quality metrics
    qm = analyzer.get_extension('quality_metrics').get_data()

    # Filter good units
    good_units = qm.query(
        "(snr > 5) & (isi_violations_ratio < 0.01) & (presence_ratio > 0.9)"
    ).index.tolist()

    print(f"Quality filtering: {len(good_units)}/{len(qm)} units passed")

    # Export
    si.export_to_phy(analyzer, f'{output_dir}/phy')
    si.export_report(analyzer, f'{output_dir}/report')

    # Save metrics
    qm.to_csv(f'{output_dir}/quality_metrics.csv')

    return analyzer, qm, good_units

# Usage
analyzer, qm, good_units = analyze_sorting(recording, sorting, 'output/')
```

### `references/AUTOMATED_CURATION.md`

# Automated Curation Reference

Guide to automated spike sorting curation using Bombcell, UnitRefine, and other tools.

## Why Automated Curation?

Manual curation is:
- **Slow**: Hours per recording session
- **Subjective**: Inter-rater variability
- **Non-reproducible**: Hard to standardize

Automated tools provide consistent, reproducible quality classification.

## Available Tools

| Tool | Classification | Language | Integration |
|------|---------------|----------|-------------|
| **Bombcell** | 4-class (single/multi/noise/non-somatic) | Python/MATLAB | SpikeInterface, Phy |
| **UnitRefine** | Machine learning-based | Python | SpikeInterface |
| **SpikeInterface QM** | Threshold-based | Python | Native |
| **UnitMatch** | Cross-session tracking | Python/MATLAB | Kilosort, Bombcell |

## Bombcell

### Overview

Bombcell classifies units into 4 categories:
1. **Single somatic units** - Well-isolated single neurons
2. **Multi-unit activity (MUA)** - Mixed neuronal signals
3. **Noise** - Non-neural artifacts
4. **Non-somatic** - Axonal or dendritic signals

### Installation

```bash
# Python
uv pip install bombcell

# Or development version
git clone https://github.com/Julie-Fabre/bombcell.git
cd bombcell/py_bombcell
uv pip install -e .
```

### Basic Usage (Python)

```python
import bombcell as bc

# Load sorted data (Kilosort output)
kilosort_folder = '/path/to/kilosort/output'
raw_data_path = '/path/to/recording.ap.bin'

# Run Bombcell
results = bc.run_bombcell(
    kilosort_folder,
    raw_data_path,
    sample_rate=30000,
    n_channels=384
)

# Get classifications
unit_labels = results['unit_labels']
# 'good' = single unit, 'mua' = multi-unit, 'noise' = noise
```

### Integration with SpikeInterface

```python
import spikeinterface.full as si

# After spike sorting (run_sorter uses folder=, not output_folder=)
sorting = si.run_sorter('kilosort4', recording, folder='ks4/')

# Create analyzer and compute required extensions
analyzer = si.create_sorting_analyzer(sorting, recording, sparse=True)
analyzer.compute('waveforms')
analyzer.compute('templates')
analyzer.compute('spike_amplitudes')

# Export to Phy format (Bombcell can read this)
si.export_to_phy(analyzer, output_folder='phy_export/')

# Run Bombcell on Phy export
import bombcell as bc
results = bc.run_bombcell_phy('phy_export/')
```

### Bombcell Metrics

Bombcell computes specific metrics for classification:

| Metric | Description | Used For |
|--------|-------------|----------|
| `peak_trough_ratio` | Waveform shape | Somatic vs non-somatic |
| `spatial_decay` | Amplitude across channels | Noise detection |
| `refractory_period_violations` | ISI violations | Single vs multi |
| `presence_ratio` | Temporal stability | Unit quality |
| `waveform_duration` | Peak-to-trough time | Cell type |

### Custom Thresholds

```python
# Customize classification thresholds
custom_params = {
    'isi_threshold': 0.01,          # ISI violation threshold
    'presence_threshold': 0.9,       # Minimum presence ratio
    'amplitude_threshold': 20,       # Minimum amplitude (μV)
    'spatial_decay_threshold': 40,   # Spatial decay (μm)
}

results = bc.run_bombcell(
    kilosort_folder,
    raw_data_path,
    **custom_params
)
```

## UnitRefine: Model-Based Curation

SpikeInterface ships pretrained machine-learning classifiers (the **UnitRefine** family) and
a loader for any scikit-learn pipeline shared on Hugging Face. Instead of hand-tuning
thresholds, you pass a `SortingAnalyzer` (with quality + template metrics computed) and the
model predicts a label and confidence per unit.

### Prepare the analyzer

The model needs the metrics it was trained on. Compute quality metrics and template metrics:

```python
import spikeinterface.full as si
import spikeinterface.curation as sc

analyzer = si.create_sorting_analyzer(sorting, recording, sparse=True, folder='analyzer/')
analyzer.compute([
    'noise_levels', 'random_spikes', 'waveforms', 'templates',
    'spike_locations', 'spike_amplitudes', 'correlograms',
    'principal_components', 'quality_metrics', 'template_metrics',
])
analyzer.compute('template_metrics', include_multi_channel_metrics=True)
```

### Apply the UnitRefine classifiers

The recommended flow chains two models: first noise vs neural, then SUA vs MUA on the
neural units. These models were trained on real Neuropixels data (V1, SC, ALM from 11 mice):

```python
# 1) noise vs neural
noise_labels = sc.model_based_label_units(
    sorting_analyzer=analyzer,
    repo_id='SpikeInterface/UnitRefine_noise_neural_classifier',
    trust_model=True,
)
neural = analyzer.remove_units(noise_labels[noise_labels['prediction'] == 'noise'].index)

# 2) single-unit (sua) vs multi-unit (mua)
sua_mua_labels = sc.model_based_label_units(
    sorting_analyzer=neural,
    repo_id='SpikeInterface/UnitRefine_sua_mua_classifier',
    trust_model=True,
)

import pandas as pd
all_labels = pd.concat(
    [sua_mua_labels, noise_labels[noise_labels['prediction'] == 'noise']]
).sort_index()
print(all_labels)   # columns: prediction, probability
```

### Loading a model explicitly

```python
model, model_info = sc.load_model(
    repo_id='SpikeInterface/toy_tetrode_model',
    trusted=['numpy.dtype'],
)
print(model.feature_names_in_)              # metrics the model expects
print(model_info['label_conversion'])      # integer -> human-readable label

# Apply a model from a local folder
labels = sc.model_based_label_units(sorting_analyzer=analyzer, model_folder='path/to/model/')
```

### Security and validation notes

- `trust_model=True` (or an explicit `trusted=[...]` list) is required to unpack the
  `.skops` model file. Only load models from sources you trust — treat `.skops`/`.pkl`
  files like any other executable artifact.
- Models trained on one brain area/dataset may not transfer. Use the confidence
  (`probability`) to decide which units to auto-accept vs. send to manual review, and
  validate against a manually labelled subset before trusting a model on new data.

## SpikeInterface Auto-Curation

### Threshold-Based Curation

```python
# Compute quality metrics
analyzer.compute('quality_metrics')
qm = analyzer.get_extension('quality_metrics').get_data()

# Define curation function
def auto_curate(qm):
    labels = {}
    for unit_id in qm.index:
        row = qm.loc[unit_id]

        # Classification logic
        if row['snr'] < 2 or row['presence_ratio'] < 0.5:
            labels[unit_id] = 'noise'
        elif row['isi_violations_ratio'] > 0.1:
            labels[unit_id] = 'mua'
        elif (row['snr'] > 5 and
              row['isi_violations_ratio'] < 0.01 and
              row['presence_ratio'] > 0.9):
            labels[unit_id] = 'good'
        else:
            labels[unit_id] = 'unsorted'

    return labels

unit_labels = auto_curate(qm)

# Filter by label
good_unit_ids = [u for u, l in unit_labels.items() if l == 'good']
sorting_curated = sorting.select_units(good_unit_ids)
```

### Using SpikeInterface Curation Module

```python
from spikeinterface.curation import (
    CurationSorting,
    MergeUnitsSorting,
    SplitUnitSorting
)

# Wrap sorting for curation
curation = CurationSorting(sorting)

# Remove noise units
noise_units = qm[qm['snr'] < 2].index.tolist()
curation.remove_units(noise_units)

# Merge similar units (based on template similarity)
analyzer.compute('template_similarity')
similarity = analyzer.get_extension('template_similarity').get_data()

# Find highly similar pairs
import numpy as np
threshold = 0.9
similar_pairs = np.argwhere(similarity > threshold)
# Merge pairs (careful - requires manual review)

# Get curated sorting
sorting_curated = curation.to_sorting()
```

## UnitMatch: Cross-Session Tracking

Track the same neurons across recording days.

### Installation

```bash
uv pip install unitmatch
# Or from source
git clone https://github.com/EnnyvanBeest/UnitMatch.git
```

### Usage

```python
# After running Bombcell on multiple sessions
session_folders = [
    '/path/to/session1/kilosort/',
    '/path/to/session2/kilosort/',
    '/path/to/session3/kilosort/',
]

from unitmatch import UnitMatch

# Run UnitMatch
um = UnitMatch(session_folders)
um.run()

# Get matching results
matches = um.get_matches()
# Returns DataFrame with unit IDs matched across sessions

# Assign unique IDs
unique_ids = um.get_unique_ids()
```

### Integration with Workflow

```python
# Typical workflow:
# 1. Spike sort each session
# 2. Run Bombcell for quality control
# 3. Run UnitMatch for cross-session tracking

# Session 1
sorting1 = si.run_sorter('kilosort4', rec1, folder='session1/ks4/')
# Run Bombcell
labels1 = bc.run_bombcell('session1/ks4/', raw1_path)

# Session 2
sorting2 = si.run_sorter('kilosort4', rec2, folder='session2/ks4/')
labels2 = bc.run_bombcell('session2/ks4/', raw2_path)

# Track units across sessions
um = UnitMatch(['session1/ks4/', 'session2/ks4/'])
matches = um.get_matches()
```

## Semi-Automated Workflow

Combine automated and manual curation:

```python
# Step 1: Automated classification
analyzer.compute('quality_metrics')
qm = analyzer.get_extension('quality_metrics').get_data()

# Auto-label obvious cases
auto_labels = {}
for unit_id in qm.index:
    row = qm.loc[unit_id]
    if row['snr'] < 1.5:
        auto_labels[unit_id] = 'noise'
    elif row['snr'] > 8 and row['isi_violations_ratio'] < 0.005:
        auto_labels[unit_id] = 'good'
    else:
        auto_labels[unit_id] = 'needs_review'

# Step 2: Export uncertain units for manual review
needs_review = [u for u, l in auto_labels.items() if l == 'needs_review']

# Export only uncertain units to Phy
sorting_review = sorting.select_units(needs_review)
analyzer_review = si.create_sorting_analyzer(sorting_review, recording)
analyzer_review.compute('waveforms')
analyzer_review.compute('templates')
si.export_to_phy(analyzer_review, output_folder='phy_review/')

# Manual review in Phy: phy template-gui phy_review/params.py

# Step 3: Load manual labels and merge
manual_labels = si.read_phy('phy_review/').get_property('quality')
# Combine auto + manual labels for final result
```

## Comparison of Methods

| Method | Pros | Cons |
|--------|------|------|
| **Manual (Phy)** | Gold standard, flexible | Slow, subjective |
| **SpikeInterface QM** | Fast, reproducible | Simple thresholds only |
| **Bombcell** | Multi-class, validated | Requires waveform extraction |
| **UnitRefine** | ML-based, pretrained models on Hugging Face | May not transfer across datasets |

## Best Practices

1. **Always visualize** - Don't blindly trust automated results
2. **Document thresholds** - Record exact parameters used
3. **Validate** - Compare automated vs manual on subset
4. **Be conservative** - When in doubt, exclude the unit
5. **Report methods** - Include curation criteria in publications

## Pipeline Example

```python
def curate_sorting(sorting, recording, output_dir):
    """Complete curation pipeline."""

    # Create analyzer
    analyzer = si.create_sorting_analyzer(sorting, recording, sparse=True,
                                          folder=f'{output_dir}/analyzer')

    # Compute required extensions
    analyzer.compute('random_spikes', max_spikes_per_unit=500)
    analyzer.compute('waveforms')
    analyzer.compute('templates')
    analyzer.compute('noise_levels')
    analyzer.compute('spike_amplitudes')
    analyzer.compute('quality_metrics')

    qm = analyzer.get_extension('quality_metrics').get_data()

    # Auto-classify
    labels = {}
    for unit_id in qm.index:
        row = qm.loc[unit_id]

        if row['snr'] < 2:
            labels[unit_id] = 'noise'
        elif row['isi_violations_ratio'] > 0.1 or row['presence_ratio'] < 0.8:
            labels[unit_id] = 'mua'
        elif (row['snr'] > 5 and
              row['isi_violations_ratio'] < 0.01 and
              row['presence_ratio'] > 0.9 and
              row['amplitude_cutoff'] < 0.1):
            labels[unit_id] = 'good'
        else:
            labels[unit_id] = 'unsorted'

    # Summary
    from collections import Counter
    print("Classification summary:")
    print(Counter(labels.values()))

    # Save labels
    import json
    with open(f'{output_dir}/unit_labels.json', 'w') as f:
        json.dump(labels, f)

    # Return good units
    good_ids = [u for u, l in labels.items() if l == 'good']
    return sorting.select_units(good_ids), labels

# Usage
sorting_curated, labels = curate_sorting(sorting, recording, 'output/')
```

## References

- [Bombcell GitHub](https://github.com/Julie-Fabre/bombcell)
- [UnitMatch GitHub](https://github.com/EnnyvanBeest/UnitMatch)
- [SpikeInterface Curation](https://spikeinterface.readthedocs.io/en/stable/modules/curation.html)
- [Model-based curation tutorial](https://spikeinterface.readthedocs.io/en/stable/tutorials/curation/plot_1_automated_curation.html)
- [UnitRefine models (Hugging Face)](https://huggingface.co/SpikeInterface)
- Fabre et al. (2023) "Bombcell: automated curation and cell classification"
- van Beest et al. (2024) "UnitMatch: tracking neurons across days with high-density probes"

### `references/MOTION_CORRECTION.md`

# Motion/Drift Correction Reference

Mechanical drift during acute probe insertion is a major challenge for Neuropixels recordings. This guide covers detection, estimation, and correction of motion artifacts.

## Why Motion Correction Matters

- Neuropixels probes can drift 10-100+ μm during recording
- Uncorrected drift leads to:
  - Units appearing/disappearing mid-recording
  - Waveform amplitude changes
  - Incorrect spike-unit assignments
  - Reduced unit yield

## Detection: Check Before Sorting

**Always visualize drift before running spike sorting!**

```python
import spikeinterface.full as si
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks

# Preprocess first (don't whiten - affects peak localization)
rec = si.highpass_filter(recording, freq_min=400.)
rec = si.common_reference(rec, operator='median', reference='global')

# Detect peaks
noise_levels = si.get_noise_levels(rec, return_in_uV=False)
peaks = detect_peaks(
    rec,
    method='locally_exclusive',
    noise_levels=noise_levels,
    detect_threshold=5,
    radius_um=50.,
    n_jobs=8,
    chunk_duration='1s',
    progress_bar=True
)

# Localize peaks
peak_locations = localize_peaks(
    rec, peaks,
    method='center_of_mass',
    n_jobs=8,
    chunk_duration='1s'
)

# Visualize drift
si.plot_drift_raster_map(
    peaks=peaks,
    peak_locations=peak_locations,
    recording=rec,
    clim=(-200, 0)  # Adjust color limits
)
```

### Interpreting Drift Plots

| Pattern | Interpretation | Action |
|---------|---------------|--------|
| Horizontal bands, stable | No significant drift | Skip correction |
| Diagonal bands (slow) | Gradual settling drift | Use motion correction |
| Rapid jumps | Brain pulsation or movement | Use non-rigid correction |
| Chaotic patterns | Severe instability | Consider discarding segment |

## Motion Correction Methods

### Quick Correction (Recommended Start)

```python
# Simple one-liner with preset
rec_corrected = si.correct_motion(
    recording=rec,
    preset='nonrigid_fast_and_accurate'
)
```

### Available Presets

| Preset | Speed | Accuracy | Best For |
|--------|-------|----------|----------|
| `rigid_fast` | Fast | Low | Quick check, small drift |
| `kilosort_like` | Medium | Good | Kilosort-compatible results |
| `nonrigid_accurate` | Slow | High | Publication-quality |
| `nonrigid_fast_and_accurate` | Medium | High | **Recommended default** |
| `dredge` | Slow | Highest | Best results, complex drift |
| `dredge_fast` | Medium | High | DREDge with less compute |

### Full Control Pipeline

```python
from spikeinterface.sortingcomponents.motion import (
    estimate_motion,
    interpolate_motion
)

# Step 1: Estimate motion
motion, temporal_bins, spatial_bins = estimate_motion(
    rec,
    peaks,
    peak_locations,
    method='decentralized',
    direction='y',
    rigid=False,          # Non-rigid for Neuropixels
    win_step_um=50,       # Spatial window step
    win_sigma_um=150,     # Spatial smoothing
    bin_s=2.0,            # Temporal bin size
    progress_bar=True
)

# Step 2: Visualize motion estimate
si.plot_motion(
    motion,
    temporal_bins,
    spatial_bins,
    recording=rec
)

# Step 3: Apply correction via interpolation
rec_corrected = interpolate_motion(
    recording=rec,
    motion=motion,
    temporal_bins=temporal_bins,
    spatial_bins=spatial_bins,
    border_mode='force_extrapolate'
)
```

### Save Motion Estimate

```python
# Save for later use
import numpy as np
np.savez('motion_estimate.npz',
         motion=motion,
         temporal_bins=temporal_bins,
         spatial_bins=spatial_bins)

# Load later
data = np.load('motion_estimate.npz')
motion = data['motion']
temporal_bins = data['temporal_bins']
spatial_bins = data['spatial_bins']
```

## DREDge: State-of-the-Art Method

DREDge (Decentralized Registration of Electrophysiology Data) is currently the best-performing motion correction method.

### Using DREDge Preset

```python
# AP-band motion estimation
rec_corrected = si.correct_motion(rec, preset='dredge')

# Or compute explicitly
motion, motion_info = si.compute_motion(
    rec,
    preset='dredge',
    output_motion_info=True,
    folder='motion_output/',
    **job_kwargs
)
```

### LFP-Based Motion Estimation

For very fast drift or when AP-band estimation fails:

```python
# Load LFP stream
lfp = si.read_spikeglx('/path/to/data', stream_name='imec0.lf')

# Estimate motion from LFP (faster, handles rapid drift)
motion_lfp, motion_info = si.compute_motion(
    lfp,
    preset='dredge_lfp',
    output_motion_info=True
)

# Apply to AP recording
rec_corrected = interpolate_motion(
    recording=rec,  # AP recording
    motion=motion_lfp,
    temporal_bins=motion_info['temporal_bins'],
    spatial_bins=motion_info['spatial_bins']
)
```

## Integration with Spike Sorting

### Option 1: Pre-correction (Recommended)

```python
# Correct before sorting
rec_corrected = si.correct_motion(rec, preset='nonrigid_fast_and_accurate')

# Save corrected recording
rec_corrected = rec_corrected.save(folder='preprocessed_motion_corrected/',
                                    format='binary', n_jobs=8)

# Run spike sorting on corrected data
sorting = si.run_sorter('kilosort4', rec_corrected, folder='ks4/')
```

### Option 2: Let Kilosort Handle It

Kilosort 2.5+ has built-in drift correction:

```python
sorting = si.run_sorter(
    'kilosort4',
    rec,  # Not motion corrected
    folder='ks4/',
    nblocks=5,  # Non-rigid blocks for drift correction
    do_correction=True  # Enable Kilosort's drift correction
)
```

### Option 3: Post-hoc Correction

```python
# Sort first
sorting = si.run_sorter('kilosort4', rec, folder='ks4/')

# Then estimate motion from sorted spikes
# (More accurate as it uses actual spike times)
from spikeinterface.sortingcomponents.motion import estimate_motion_from_sorting

motion = estimate_motion_from_sorting(sorting, rec)
```

## Parameters Deep Dive

### Peak Detection

```python
peaks = detect_peaks(
    rec,
    method='locally_exclusive',  # Best for dense probes
    noise_levels=noise_levels,
    detect_threshold=5,          # Lower = more peaks (noisier estimate)
    radius_um=50.,               # Exclusion radius
    exclude_sweep_ms=0.1,        # Temporal exclusion
)
```

### Motion Estimation

```python
motion = estimate_motion(
    rec, peaks, peak_locations,
    method='decentralized',      # 'decentralized' or 'iterative_template'
    direction='y',               # Along probe axis
    rigid=False,                 # False for non-rigid
    bin_s=2.0,                   # Temporal resolution (seconds)
    win_step_um=50,              # Spatial window step
    win_sigma_um=150,            # Spatial smoothing sigma
    margin_um=0,                 # Margin at probe edges
    win_scale_um=150,            # Window scale for weights
)
```

## Troubleshooting

### Over-correction (Wavy Patterns)

```python
# Increase temporal smoothing
motion = estimate_motion(..., bin_s=5.0)  # Larger bins

# Or use rigid correction for small drift
motion = estimate_motion(..., rigid=True)
```

### Under-correction (Drift Remains)

```python
# Decrease spatial window for finer non-rigid estimate
motion = estimate_motion(..., win_step_um=25, win_sigma_um=75)

# Use more peaks
peaks = detect_peaks(..., detect_threshold=4)  # Lower threshold
```

### Edge Artifacts

```python
rec_corrected = interpolate_motion(
    rec, motion, temporal_bins, spatial_bins,
    border_mode='force_extrapolate',  # or 'remove_channels'
    spatial_interpolation_method='kriging'
)
```

## Validation

After correction, re-visualize to confirm:

```python
# Re-detect peaks on corrected recording
peaks_corrected = detect_peaks(rec_corrected, ...)
peak_locations_corrected = localize_peaks(rec_corrected, peaks_corrected, ...)

# Plot before/after comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Before
si.plot_drift_raster_map(peaks, peak_locations, rec, ax=axes[0])
axes[0].set_title('Before Correction')

# After
si.plot_drift_raster_map(peaks_corrected, peak_locations_corrected,
                         rec_corrected, ax=axes[1])
axes[1].set_title('After Correction')
```

## References

- [SpikeInterface Motion Correction Docs](https://spikeinterface.readthedocs.io/en/stable/modules/motion_correction.html)
- [Handle Drift Tutorial](https://spikeinterface.readthedocs.io/en/stable/how_to/handle_drift.html)
- [DREDge GitHub](https://github.com/evarol/DREDge)
- Windolf et al. (2023) "DREDge: robust motion correction for high-density extracellular recordings"

### `references/PREPROCESSING.md`

# Neuropixels Preprocessing Reference

Comprehensive preprocessing techniques for Neuropixels neural recordings.

## Standard Preprocessing Pipeline

```python
import spikeinterface.full as si

# Load raw data
recording = si.read_spikeglx('/path/to/data', stream_name='imec0.ap')

# 1. Phase shift correction (for Neuropixels 1.0)
rec = si.phase_shift(recording)

# 2. Bandpass filter for spike detection
rec = si.bandpass_filter(rec, freq_min=300, freq_max=6000)

# 3. Common median reference (removes correlated noise)
rec = si.common_reference(rec, reference='global', operator='median')

# 4. Remove bad channels (optional)
rec = si.remove_bad_channels(rec, bad_channel_ids=bad_channels)
```

## Filtering Options

### Bandpass Filter
```python
# Standard AP band
rec = si.bandpass_filter(recording, freq_min=300, freq_max=6000)

# Wider band (preserve more waveform shape)
rec = si.bandpass_filter(recording, freq_min=150, freq_max=7500)

# Filter parameters
rec = si.bandpass_filter(
    recording,
    freq_min=300,
    freq_max=6000,
    filter_order=5,
    ftype='butter',  # 'butter', 'bessel', or 'cheby1'
    margin_ms=5.0    # Prevent edge artifacts
)
```

### Highpass Filter Only
```python
rec = si.highpass_filter(recording, freq_min=300)
```

### Notch Filter (Remove Line Noise)
```python
# Remove 60Hz and harmonics
rec = si.notch_filter(recording, freq=60, q=30)
rec = si.notch_filter(rec, freq=120, q=30)
rec = si.notch_filter(rec, freq=180, q=30)
```

## Reference Schemes

### Common Median Reference (Recommended)
```python
# Global median reference
rec = si.common_reference(recording, reference='global', operator='median')

# Per-shank reference (multi-shank probes)
rec = si.common_reference(recording, reference='global', operator='median',
                          groups=recording.get_channel_groups())
```

### Common Average Reference
```python
rec = si.common_reference(recording, reference='global', operator='average')
```

### Local Reference
```python
# Reference by local groups of channels
rec = si.common_reference(recording, reference='local', local_radius=(30, 100))
```

## Bad Channel Detection & Removal

### Automatic Detection
```python
# Detect bad channels
bad_channel_ids, channel_labels = si.detect_bad_channels(
    recording,
    method='coherence+psd',
    dead_channel_threshold=-0.5,
    noisy_channel_threshold=1.0,
    outside_channel_threshold=-0.3,
    n_neighbors=11
)

print(f"Bad channels: {bad_channel_ids}")
print(f"Labels: {dict(zip(bad_channel_ids, channel_labels))}")
```

### Remove Bad Channels
```python
rec_clean = si.remove_bad_channels(recording, bad_channel_ids=bad_channel_ids)
```

### Interpolate Bad Channels
```python
rec_interp = si.interpolate_bad_channels(recording, bad_channel_ids=bad_channel_ids)
```

## Motion Correction

### Estimate Motion
```python
# Estimate motion (drift)
motion, temporal_bins, spatial_bins = si.estimate_motion(
    recording,
    method='decentralized',
    rigid=False,              # Non-rigid motion estimation
    win_step_um=50,           # Spatial window step
    win_sigma_um=150,         # Spatial window sigma
    progress_bar=True
)
```

### Apply Motion Correction
```python
rec_corrected = si.correct_motion(
    recording,
    motion,
    temporal_bins,
    spatial_bins,
    interpolate_motion_border=True
)
```

### Motion Visualization
```python
si.plot_motion(motion, temporal_bins, spatial_bins)
```

## Probe-Specific Processing

### Neuropixels 1.0
```python
# Phase shift correction (different ADC per channel)
rec = si.phase_shift(recording)

# Then standard pipeline
rec = si.bandpass_filter(rec, freq_min=300, freq_max=6000)
rec = si.common_reference(rec, reference='global', operator='median')
```

### Neuropixels 2.0
```python
# No phase shift needed (single ADC)
rec = si.bandpass_filter(recording, freq_min=300, freq_max=6000)
rec = si.common_reference(rec, reference='global', operator='median')
```

### Multi-Shank (Neuropixels 2.0 4-shank)
```python
# Reference per shank
groups = recording.get_channel_groups()  # Returns shank assignments
rec = si.common_reference(recording, reference='global', operator='median', groups=groups)
```

## Whitening

```python
# Whiten data (decorrelate channels)
rec_whitened = si.whiten(recording, mode='local', local_radius_um=100)

# Global whitening
rec_whitened = si.whiten(recording, mode='global')
```

## Artifact Removal

### Remove Stimulation Artifacts
```python
# Define artifact times (in samples)
triggers = [10000, 20000, 30000]  # Sample indices

rec = si.remove_artifacts(
    recording,
    triggers,
    ms_before=0.5,
    ms_after=3.0,
    mode='cubic'  # 'zeros', 'linear', 'cubic'
)
```

### Blank Saturation Periods
```python
rec = si.blank_staturation(recording, threshold=0.95, fill_value=0)
```

## Saving Preprocessed Data

### Binary Format (Recommended)
```python
rec_preprocessed.save(folder='preprocessed/', format='binary', n_jobs=4)
```

### Zarr Format (Compressed)
```python
rec_preprocessed.save(folder='preprocessed.zarr', format='zarr')
```

### Save as Recording Extractor
```python
# Save for later use
rec_preprocessed.save(folder='preprocessed/', format='binary')

# Load later
rec_loaded = si.load_extractor('preprocessed/')
```

## Complete Pipeline Example

```python
import spikeinterface.full as si

def preprocess_neuropixels(data_path, output_path):
    """Standard Neuropixels preprocessing pipeline."""

    # Load data
    recording = si.read_spikeglx(data_path, stream_name='imec0.ap')
    print(f"Loaded: {recording.get_num_channels()} channels, "
          f"{recording.get_total_duration():.1f}s")

    # Phase shift (NP 1.0 only)
    rec = si.phase_shift(recording)

    # Filter
    rec = si.bandpass_filter(rec, freq_min=300, freq_max=6000)

    # Detect and remove bad channels
    bad_ids, _ = si.detect_bad_channels(rec)
    if len(bad_ids) > 0:
        print(f"Removing {len(bad_ids)} bad channels: {bad_ids}")
        rec = si.interpolate_bad_channels(rec, bad_ids)

    # Common reference
    rec = si.common_reference(rec, reference='global', operator='median')

    # Save
    rec.save(folder=output_path, format='binary', n_jobs=4)
    print(f"Saved to: {output_path}")

    return rec

# Usage
rec_preprocessed = preprocess_neuropixels(
    '/path/to/spikeglx/data',
    '/path/to/preprocessed'
)
```

## Performance Tips

```python
# Use parallel processing
rec.save(folder='output/', n_jobs=-1)  # Use all cores

# Use job kwargs for memory management
job_kwargs = dict(n_jobs=8, chunk_duration='1s', progress_bar=True)
rec.save(folder='output/', **job_kwargs)

# Set global job kwargs
si.set_global_job_kwargs(n_jobs=8, chunk_duration='1s')
```

### `references/QUALITY_METRICS.md`

# Quality Metrics Reference

Comprehensive guide to unit quality assessment using SpikeInterface metrics and Allen/IBL standards.

## Overview

Quality metrics assess three aspects of sorted units:

| Category | Question | Key Metrics |
|----------|----------|-------------|
| **Contamination** (Type I) | Are spikes from multiple neurons? | ISI violations, SNR |
| **Completeness** (Type II) | Are we missing spikes? | Amplitude cutoff, presence ratio |
| **Stability** | Is the unit stable over time? | Drift metrics, amplitude CV |

## Computing Quality Metrics

```python
import spikeinterface.full as si

# Create analyzer with computed waveforms
analyzer = si.create_sorting_analyzer(sorting, recording, sparse=True)
analyzer.compute('random_spikes', max_spikes_per_unit=500)
analyzer.compute('waveforms', ms_before=1.5, ms_after=2.0)
analyzer.compute('templates')
analyzer.compute('noise_levels')
analyzer.compute('spike_amplitudes')
analyzer.compute('principal_components', n_components=5)

# Compute all quality metrics
analyzer.compute('quality_metrics')

# Or compute specific metrics
analyzer.compute('quality_metrics', metric_names=[
    'firing_rate', 'snr', 'isi_violations_ratio',
    'presence_ratio', 'amplitude_cutoff'
])

# Get results
qm = analyzer.get_extension('quality_metrics').get_data()
print(qm.columns.tolist())  # Available metrics
```

## Metric Definitions & Thresholds

### Contamination Metrics

#### ISI Violations Ratio
Fraction of spikes violating refractory period. All neurons have a ~1.5ms refractory period.

```python
# Compute with custom refractory period
analyzer.compute('quality_metrics',
                 metric_names=['isi_violations_ratio'],
                 isi_threshold_ms=1.5,
                 min_isi_ms=0.0)
```

| Value | Interpretation |
|-------|---------------|
| < 0.01 | Excellent (well-isolated single unit) |
| 0.01 - 0.1 | Good (minor contamination) |
| 0.1 - 0.5 | Moderate (multi-unit activity likely) |
| > 0.5 | Poor (likely multi-unit) |

**Reference:** Hill et al. (2011) J Neurosci 31:8699-8705

#### Signal-to-Noise Ratio (SNR)
Ratio of peak waveform amplitude to background noise.

```python
analyzer.compute('quality_metrics', metric_names=['snr'])
```

| Value | Interpretation |
|-------|---------------|
| > 10 | Excellent |
| 5 - 10 | Good |
| 2 - 5 | Acceptable |
| < 2 | Poor (may be noise) |

#### Isolation Distance
Mahalanobis distance to nearest cluster in PCA space.

```python
analyzer.compute('quality_metrics',
                 metric_names=['isolation_distance'],
                 n_neighbors=4)
```

| Value | Interpretation |
|-------|---------------|
| > 50 | Well-isolated |
| 20 - 50 | Moderately isolated |
| < 20 | Poorly isolated |

#### L-ratio
Contamination measure based on Mahalanobis distances.

| Value | Interpretation |
|-------|---------------|
| < 0.05 | Well-isolated |
| 0.05 - 0.1 | Acceptable |
| > 0.1 | Contaminated |

#### D-prime
Discriminability between unit and nearest neighbor.

| Value | Interpretation |
|-------|---------------|
| > 8 | Excellent separation |
| 5 - 8 | Good separation |
| < 5 | Poor separation |

### Completeness Metrics

#### Amplitude Cutoff
Estimates fraction of spikes below detection threshold.

```python
analyzer.compute('quality_metrics',
                 metric_names=['amplitude_cutoff'],
                 peak_sign='neg')  # 'neg', 'pos', or 'both'
```

| Value | Interpretation |
|-------|---------------|
| < 0.01 | Excellent (nearly complete) |
| 0.01 - 0.1 | Good |
| 0.1 - 0.2 | Moderate (some missed spikes) |
| > 0.2 | Poor (many missed spikes) |

**For precise timing analyses:** Use < 0.01

#### Presence Ratio
Fraction of recording time with detected spikes.

```python
analyzer.compute('quality_metrics',
                 metric_names=['presence_ratio'],
                 bin_duration_s=60)  # 1-minute bins
```

| Value | Interpretation |
|-------|---------------|
| > 0.99 | Excellent |
| 0.9 - 0.99 | Good |
| 0.8 - 0.9 | Acceptable |
| < 0.8 | Unit may have drifted out |

### Stability Metrics

#### Drift Metrics
Measure unit movement over time.

```python
analyzer.compute('quality_metrics',
                 metric_names=['drift_ptp', 'drift_std', 'drift_mad'])
```

| Metric | Description | Good Value |
|--------|-------------|------------|
| `drift_ptp` | Peak-to-peak drift (μm) | < 40 |
| `drift_std` | Standard deviation of drift | < 10 |
| `drift_mad` | Median absolute deviation | < 10 |

#### Amplitude CV
Coefficient of variation of spike amplitudes.

| Value | Interpretation |
|-------|---------------|
| < 0.25 | Very stable |
| 0.25 - 0.5 | Acceptable |
| > 0.5 | Unstable (drift or contamination) |

### Cluster Quality Metrics

#### Silhouette Score
Cluster cohesion vs separation (-1 to 1).

| Value | Interpretation |
|-------|---------------|
| > 0.5 | Well-defined cluster |
| 0.25 - 0.5 | Moderate |
| < 0.25 | Overlapping clusters |

#### Nearest-Neighbor Metrics

```python
analyzer.compute('quality_metrics',
                 metric_names=['nn_hit_rate', 'nn_miss_rate'],
                 n_neighbors=4)
```

| Metric | Description | Good Value |
|--------|-------------|------------|
| `nn_hit_rate` | Fraction of spikes with same-unit neighbors | > 0.9 |
| `nn_miss_rate` | Fraction of spikes with other-unit neighbors | < 0.1 |

## Standard Filtering Criteria

### Allen Institute Defaults

```python
# Allen Visual Coding / Behavior defaults
allen_query = """
    presence_ratio > 0.95 and
    isi_violations_ratio < 0.5 and
    amplitude_cutoff < 0.1
"""
good_units = qm.query(allen_query).index.tolist()
```

### IBL Standards

```python
# IBL reproducible ephys criteria
ibl_query = """
    presence_ratio > 0.9 and
    isi_violations_ratio < 0.1 and
    amplitude_cutoff < 0.1 and
    firing_rate > 0.1
"""
good_units = qm.query(ibl_query).index.tolist()
```

### Strict Single-Unit Criteria

```python
# For precise timing / spike-timing analyses
strict_query = """
    snr > 5 and
    presence_ratio > 0.99 and
    isi_violations_ratio < 0.01 and
    amplitude_cutoff < 0.01 and
    isolation_distance > 20 and
    drift_ptp < 40
"""
single_units = qm.query(strict_query).index.tolist()
```

### Multi-Unit Activity (MUA)

```python
# Include multi-unit activity
mua_query = """
    snr > 2 and
    presence_ratio > 0.5 and
    isi_violations_ratio < 1.0
"""
all_units = qm.query(mua_query).index.tolist()
```

## Visualization

### Quality Metric Summary

```python
# Plot all metrics
si.plot_quality_metrics(analyzer)
```

### Individual Metric Distributions

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 3, figsize=(15, 10))

metrics = ['snr', 'isi_violations_ratio', 'presence_ratio',
           'amplitude_cutoff', 'firing_rate', 'drift_ptp']

for ax, metric in zip(axes.flat, metrics):
    ax.hist(qm[metric].dropna(), bins=50, edgecolor='black')
    ax.set_xlabel(metric)
    ax.set_ylabel('Count')
    # Add threshold line
    if metric == 'snr':
        ax.axvline(5, color='r', linestyle='--', label='threshold')
    elif metric == 'isi_violations_ratio':
        ax.axvline(0.01, color='r', linestyle='--')
    elif metric == 'presence_ratio':
        ax.axvline(0.9, color='r', linestyle='--')

plt.tight_layout()
```

### Unit Quality Summary

```python
# Comprehensive unit summary plot
si.plot_unit_summary(analyzer, unit_id=0)
```

### Quality vs Firing Rate

```python
fig, ax = plt.subplots()
scatter = ax.scatter(qm['firing_rate'], qm['snr'],
                     c=qm['isi_violations_ratio'],
                     cmap='RdYlGn_r', alpha=0.6)
ax.set_xlabel('Firing Rate (Hz)')
ax.set_ylabel('SNR')
plt.colorbar(scatter, label='ISI Violations')
ax.set_xscale('log')
```

## Compute All Metrics at Once

```python
# Full quality metrics computation
all_metric_names = [
    # Firing properties
    'firing_rate', 'presence_ratio',
    # Waveform
    'snr', 'amplitude_cutoff', 'amplitude_cv_median', 'amplitude_cv_range',
    # ISI
    'isi_violations_ratio', 'isi_violations_count',
    # Drift
    'drift_ptp', 'drift_std', 'drift_mad',
    # Isolation (require PCA)
    'isolation_distance', 'l_ratio', 'd_prime',
    # Nearest neighbor (require PCA)
    'nn_hit_rate', 'nn_miss_rate',
    # Cluster quality
    'silhouette_score',
    # Synchrony
    'sync_spike_2', 'sync_spike_4', 'sync_spike_8',
]

# Compute PCA first (required for some metrics)
analyzer.compute('principal_components', n_components=5)

# Compute metrics
analyzer.compute('quality_metrics', metric_names=all_metric_names)
qm = analyzer.get_extension('quality_metrics').get_data()

# Save to CSV
qm.to_csv('quality_metrics.csv')
```

## Custom Metrics

```python
from spikeinterface.qualitymetrics import compute_firing_rates, compute_snrs

# Compute individual metrics
firing_rates = compute_firing_rates(sorting)
snrs = compute_snrs(analyzer)

# Add custom metric to DataFrame
qm['custom_score'] = qm['snr'] * qm['presence_ratio'] / (qm['isi_violations_ratio'] + 0.001)
```

## References

- [SpikeInterface Quality Metrics](https://spikeinterface.readthedocs.io/en/latest/modules/qualitymetrics.html)
- [Allen Institute ecephys_quality_metrics](https://allensdk.readthedocs.io/en/latest/_static/examples/nb/ecephys_quality_metrics.html)
- Hill et al. (2011) "Quality metrics to accompany spike sorting of extracellular signals"
- Siegle et al. (2021) "Survey of spiking in the mouse visual system reveals functional hierarchy"

### `references/SPIKE_SORTING.md`

# Spike Sorting Reference

Comprehensive guide to spike sorting Neuropixels data.

## Available Sorters

| Sorter | GPU Required | Speed | Quality | Best For |
|--------|--------------|-------|---------|----------|
| **Kilosort4** | Yes (CUDA) | Fast | Excellent | Production use |
| **Kilosort3** | Yes (CUDA) | Fast | Very Good | Legacy compatibility |
| **Kilosort2.5** | Yes (CUDA) | Fast | Good | Older pipelines |
| **SpykingCircus2** | No | Medium | Good | CPU-only systems |
| **Mountainsort5** | No | Medium | Good | Small recordings |
| **Tridesclous2** | No | Medium | Good | Interactive sorting |

## Kilosort4 (Recommended)

### Installation
```bash
uv pip install kilosort
```

### Basic Usage
```python
import spikeinterface.full as si

# Run Kilosort4
sorting = si.run_sorter(
    'kilosort4',
    recording,
    folder='ks4_output',
    verbose=True
)

print(f"Found {len(sorting.unit_ids)} units")
```

### Custom Parameters
```python
sorting = si.run_sorter(
    'kilosort4',
    recording,
    folder='ks4_output',
    # Detection
    Th_universal=9,        # Spike detection threshold
    Th_learned=8,          # Learned threshold
    # Templates
    dmin=15,               # Min vertical distance between templates (um)
    dminx=12,              # Min horizontal distance (um)
    nblocks=5,             # Number of non-rigid blocks
    # Clustering
    max_channel_distance=None,  # Max distance for template channel
    # Output
    do_CAR=False,          # Skip CAR (done in preprocessing)
    skip_kilosort_preprocessing=True,
    save_extra_kwargs=True
)
```

### Kilosort4 Full Parameters
```python
# Get all available parameters
params = si.get_default_sorter_params('kilosort4')
print(params)

# Key parameters:
ks4_params = {
    # Detection
    'Th_universal': 9,      # Universal threshold for spike detection
    'Th_learned': 8,        # Threshold for learned templates
    'spkTh': -6,            # Spike threshold during extraction

    # Clustering
    'dmin': 15,             # Min distance between clusters (um)
    'dminx': 12,            # Min horizontal distance (um)
    'nblocks': 5,           # Blocks for non-rigid drift correction

    # Templates
    'n_templates': 6,       # Number of universal templates per group
    'nt': 61,               # Number of time samples in template

    # Performance
    'batch_size': 60000,    # Batch size in samples
    'nfilt_factor': 8,      # Factor for number of filters
}
```

## Kilosort3

### Usage
```python
sorting = si.run_sorter(
    'kilosort3',
    recording,
    folder='ks3_output',
    # Key parameters
    detect_threshold=6,
    projection_threshold=[9, 9],
    preclust_threshold=8,
    car=False,  # CAR done in preprocessing
    freq_min=300,
)
```

## SpykingCircus2 (CPU-Only)

### Installation
```bash
uv pip install spykingcircus
```

### Usage
```python
sorting = si.run_sorter(
    'spykingcircus2',
    recording,
    folder='sc2_output',
    # Parameters
    detect_threshold=5,
    selection_method='all',
)
```

## Mountainsort5 (CPU-Only)

### Installation
```bash
uv pip install mountainsort5
```

### Usage
```python
sorting = si.run_sorter(
    'mountainsort5',
    recording,
    folder='ms5_output',
    # Parameters
    detect_threshold=5.0,
    scheme='2',  # '1', '2', or '3'
)
```

## Running Multiple Sorters

### Compare Sorters
```python
# Run multiple sorters
sorting_ks4 = si.run_sorter('kilosort4', recording, folder='ks4/')
sorting_sc2 = si.run_sorter('spykingcircus2', recording, folder='sc2/')
sorting_ms5 = si.run_sorter('mountainsort5', recording, folder='ms5/')

# Compare results
comparison = si.compare_multiple_sorters(
    [sorting_ks4, sorting_sc2, sorting_ms5],
    name_list=['KS4', 'SC2', 'MS5']
)

# Get agreement scores
agreement = comparison.get_agreement_sorting()
```

### Ensemble Sorting
```python
# Create consensus sorting
sorting_ensemble = si.create_ensemble_sorting(
    [sorting_ks4, sorting_sc2, sorting_ms5],
    voting_method='agreement',
    min_agreement=2  # Unit must be found by at least 2 sorters
)
```

## Sorting in Docker/Singularity

### Using Docker
```python
sorting = si.run_sorter(
    'kilosort3',
    recording,
    folder='ks3_docker/',
    docker_image='spikeinterface/kilosort3-compiled-base:latest',
    verbose=True
)
```

### Using Singularity
```python
sorting = si.run_sorter(
    'kilosort3',
    recording,
    folder='ks3_singularity/',
    singularity_image='/path/to/kilosort3.sif',
    verbose=True
)
```

## Long Recording Strategy

### Concatenate Recordings
```python
# Multiple recording files
recordings = [
    si.read_spikeglx(f'/path/to/recording_{i}', stream_name='imec0.ap')
    for i in range(3)
]

# Concatenate
recording_concat = si.concatenate_recordings(recordings)

# Sort
sorting = si.run_sorter('kilosort4', recording_concat, folder='ks4/')

# Split back by original recording
sortings_split = si.split_sorting(sorting, recording_concat)
```

### Sort by Segment
```python
# For very long recordings, sort segments separately
from pathlib import Path

segments_output = Path('sorting_segments')
sortings = []

for i, segment in enumerate(recording.split_by_times([0, 3600, 7200, 10800])):
    sorting_seg = si.run_sorter(
        'kilosort4',
        segment,
        folder=segments_output / f'segment_{i}'
    )
    sortings.append(sorting_seg)
```

## Post-Sorting Curation

### Manual Curation with Phy
```python
# Export to Phy format
analyzer = si.create_sorting_analyzer(sorting, recording)
analyzer.compute(['random_spikes', 'waveforms', 'templates'])
si.export_to_phy(analyzer, output_folder='phy_export/')

# Open Phy
# Run in terminal: phy template-gui phy_export/params.py
```

### Load Phy Curation
```python
# After manual curation in Phy
sorting_curated = si.read_phy('phy_export/')

# Or apply Phy labels
sorting_curated = si.apply_phy_curation(sorting, 'phy_export/')
```

### Automatic Curation
```python
# Remove units below quality threshold
analyzer = si.create_sorting_analyzer(sorting, recording)
analyzer.compute('quality_metrics')

qm = analyzer.get_extension('quality_metrics').get_data()

# Define quality criteria
query = "(snr > 5) & (isi_violations_ratio < 0.01) & (presence_ratio > 0.9)"
good_unit_ids = qm.query(query).index.tolist()

sorting_clean = sorting.select_units(good_unit_ids)
print(f"Kept {len(good_unit_ids)}/{len(sorting.unit_ids)} units")
```

## Sorting Metrics

### Check Sorter Output
```python
# Basic stats
print(f"Units found: {len(sorting.unit_ids)}")
print(f"Total spikes: {sorting.get_total_num_spikes()}")

# Per-unit spike counts
for unit_id in sorting.unit_ids[:10]:
    n_spikes = len(sorting.get_unit_spike_train(unit_id))
    print(f"Unit {unit_id}: {n_spikes} spikes")
```

### Firing Rates
```python
# Compute firing rates
duration = recording.get_total_duration()
for unit_id in sorting.unit_ids:
    n_spikes = len(sorting.get_unit_spike_train(unit_id))
    fr = n_spikes / duration
    print(f"Unit {unit_id}: {fr:.2f} Hz")
```

## Troubleshooting

### Common Issues

**Out of GPU Memory**
```python
# Reduce batch size
sorting = si.run_sorter(
    'kilosort4',
    recording,
    folder='ks4/',
    batch_size=30000  # Smaller batch
)
```

**Too Few Units Found**
```python
# Lower detection threshold
sorting = si.run_sorter(
    'kilosort4',
    recording,
    folder='ks4/',
    Th_universal=7,  # Lower from default 9
    Th_learned=6
)
```

**Too Many Units (Over-splitting)**
```python
# Increase minimum distance between templates
sorting = si.run_sorter(
    'kilosort4',
    recording,
    folder='ks4/',
    dmin=20,   # Increase from 15
    dminx=16   # Increase from 12
)
```

**Check GPU Availability**
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### `references/api_reference.md`

# API Reference (SpikeInterface)

Quick reference for the SpikeInterface functions used throughout this skill. Import with:

```python
import spikeinterface.full as si
import spikeinterface.curation as sc
import spikeinterface.widgets as sw
```

All examples target SpikeInterface ≥ 0.104. Set global parallelization once:

```python
si.set_global_job_kwargs(n_jobs=-1, chunk_duration="1s", progress_bar=True)
```

## Loading

### Inspect streams

```python
stream_names, stream_ids = si.get_neo_streams("spikeglx", "/path/to/run_g0/")
# stream_names -> ['imec0.ap', 'imec0.lf', 'nidq']
```

### Readers

```python
si.read_spikeglx(folder_path, stream_name="imec0.ap", load_sync_channel=False)
si.read_openephys(folder_path, stream_name=None)
si.read_nwb(file_path)
```

Prefer `stream_name` (a value from `get_neo_streams`) over `stream_id`.

### Recording introspection

```python
recording.get_num_channels()
recording.get_total_duration()        # seconds
recording.get_sampling_frequency()    # Hz
recording.get_channel_locations()
recording.get_probe()
recording.frame_slice(start_frame, end_frame)
```

## Preprocessing

```python
si.highpass_filter(recording, freq_min=400.0)
si.bandpass_filter(recording, freq_min=300.0, freq_max=6000.0)
si.phase_shift(recording)                                  # ADC phase correction (NP 1.0)
si.detect_bad_channels(recording)                          # -> (bad_channel_ids, channel_labels)
recording.remove_channels(bad_channel_ids)
si.common_reference(recording, operator="median", reference="global")
si.highpass_spatial_filter(recording)                      # IBL-style destriping
si.get_noise_levels(recording, return_in_uV=False)
recording.save(folder="preprocessed/", format="binary")
```

> `detect_bad_channels` returns a 2-tuple; always unpack both values.

## Drift detection and motion correction

```python
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks

peaks = detect_peaks(rec, method="locally_exclusive", noise_levels=noise_levels,
                     detect_threshold=5, radius_um=50.0)
peak_locations = localize_peaks(rec, peaks, method="center_of_mass")

# One-call correction with a preset
rec_corrected = si.correct_motion(rec, preset="nonrigid_fast_and_accurate", folder="motion/")
```

**Presets:** `rigid_fast`, `kilosort_like`, `nonrigid_accurate`,
`nonrigid_fast_and_accurate` (recommended default), `dredge`, `dredge_fast`.

## Spike sorting

```python
si.installed_sorters()
si.available_sorters()
si.get_default_sorter_params("kilosort4")

sorting = si.run_sorter(
    "kilosort4",            # sorter name
    recording,
    folder="ks4_output",   # NOT output_folder (deprecated)
    verbose=True,
    # sorter-specific kwargs, e.g. Th_universal=9, Th_learned=8, nblocks=5, batch_size=60000
)

# Containerized external sorters (no local install needed)
si.run_sorter("kilosort2_5", recording, folder="ks25/", docker_image=True)

# Read a sorter folder back
sorting = si.read_sorter_folder("ks4_output")
```

**Sorting introspection:**

```python
sorting.unit_ids
sorting.get_total_num_spikes()
sorting.get_unit_spike_train(unit_id)
sorting.select_units(unit_ids)
sorting.to_spike_vector()
```

## Postprocessing: SortingAnalyzer

```python
analyzer = si.create_sorting_analyzer(
    sorting, recording,
    sparse=True,
    format="binary_folder",   # or "memory" / "zarr"
    folder="analyzer/",
)

# Extensions (order matters: random_spikes -> waveforms -> templates -> ...)
analyzer.compute("random_spikes", method="uniform", max_spikes_per_unit=500)
analyzer.compute("waveforms", ms_before=1.0, ms_after=2.0)
analyzer.compute("templates", operators=["average", "std"])
analyzer.compute("noise_levels")
analyzer.compute("spike_amplitudes")
analyzer.compute("correlograms", window_ms=50.0, bin_ms=1.0)
analyzer.compute("unit_locations", method="monopolar_triangulation")
analyzer.compute("spike_locations", method="center_of_mass")
analyzer.compute("template_similarity")
analyzer.compute("principal_components", n_components=5, mode="by_channel_local")

# Or compute several at once
analyzer.compute(["random_spikes", "waveforms", "templates", "noise_levels"])

# Access extension data
analyzer.get_extension("quality_metrics").get_data()
analyzer.get_extension("templates").get_unit_template(unit_id, operator="average")

# Persist / reload / subset
si.load_sorting_analyzer("analyzer/")
analyzer.select_units(unit_ids, folder="analyzer_clean/", format="binary_folder")
analyzer.remove_units(unit_ids)
```

## Quality metrics

```python
metric_names = ["firing_rate", "presence_ratio", "snr", "isi_violation",
                "amplitude_cutoff", "amplitude_cv", "sliding_rp_violation"]
analyzer.compute("quality_metrics", metric_names=metric_names)
metrics = analyzer.get_extension("quality_metrics").get_data()

# Equivalent standalone helper
metrics = si.compute_quality_metrics(analyzer, metric_names=metric_names)
```

**Common columns:** `snr`, `firing_rate`, `presence_ratio`, `amplitude_cutoff`,
`isi_violations_ratio`, `isi_violations_count`. PCA-based metrics
(`isolation_distance`, `l_ratio`, `d_prime`, `nn_hit_rate`) require
`analyzer.compute("principal_components")` first.

## Curation

### Threshold-based

```python
query = "(amplitude_cutoff < 0.1) & (isi_violations_ratio < 0.5) & (presence_ratio > 0.9)"
good_unit_ids = metrics.query(query).index.values
clean = sorting.select_units(good_unit_ids)
```

### Model-based (UnitRefine / Hugging Face)

```python
import spikeinterface.curation as sc

labels = sc.model_based_label_units(
    sorting_analyzer=analyzer,
    repo_id="SpikeInterface/UnitRefine_noise_neural_classifier",
    trust_model=True,
)
# labels -> DataFrame with 'prediction' and 'probability' columns

# Load a model object explicitly (e.g. to inspect feature_names_in_)
model, model_info = sc.load_model(repo_id="SpikeInterface/toy_tetrode_model", trusted=["numpy.dtype"])
```

### Manual edits

```python
from spikeinterface.curation import CurationSorting
cur = CurationSorting(sorting)
cur.remove_units(noise_unit_ids)
sorting_curated = cur.sorting
```

## Visualization (widgets)

```python
sw.plot_probe_map(recording, with_channel_ids=True)
sw.plot_traces({"filtered": rec1, "cmr": rec2}, backend="matplotlib", clim=(-50, 50))
si.plot_drift_raster_map(peaks=peaks, peak_locations=peak_locations, recording=rec, clim=(-50, 50))
sw.plot_unit_waveforms(analyzer, unit_ids=[0])
sw.plot_unit_templates(analyzer, unit_ids=[0, 1, 2])
sw.plot_autocorrelograms(analyzer, unit_ids=[0])
sw.plot_amplitudes(analyzer, unit_ids=[0], plot_histograms=True)
sw.plot_unit_locations(analyzer)
si.plot_sorting_summary(analyzer, backend="sortingview")  # web-based viewer
```

See [plotting_guide.md](plotting_guide.md) for publication-quality figure recipes.

## Export

```python
si.export_to_phy(analyzer, output_folder="phy_export/",
                 compute_pc_features=True, compute_amplitudes=True, copy_binary=True)
si.export_report(analyzer, "report/", format="png")

from spikeinterface.exporters import export_to_nwb
export_to_nwb(analyzer, "output.nwb")

si.read_phy("phy_export/")   # load Phy curation back
```

> Note: `export_to_phy` / `export_report` take `output_folder` — this is correct and
> distinct from `run_sorter`/`create_sorting_analyzer`, which take `folder`.

### `references/plotting_guide.md`

# Plotting Guide

Comprehensive guide for creating publication-quality visualizations from Neuropixels data.

## Setup

```python
import matplotlib.pyplot as plt
import numpy as np
import spikeinterface.full as si
import spikeinterface.widgets as sw

# High-quality settings
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
```

## Drift and Motion Plots

### Basic Drift Map

```python
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks

noise_levels = si.get_noise_levels(recording, return_in_uV=False)
peaks = detect_peaks(recording, method='locally_exclusive', noise_levels=noise_levels,
                     detect_threshold=5, radius_um=50.0)
peak_locations = localize_peaks(recording, peaks, method='center_of_mass')

si.plot_drift_raster_map(
    peaks=peaks,
    peak_locations=peak_locations,
    recording=recording,
    clim=(-50, 50),
)
plt.savefig('drift_raster.png', bbox_inches='tight')
```

### Motion Estimate Visualization

`correct_motion(..., output_motion_info=True)` returns `(recording, motion_info)`. The
`motion_info` dict can be plotted directly with the built-in widget:

```python
rec_corrected, motion_info = si.correct_motion(
    recording, preset='nonrigid_fast_and_accurate', output_motion_info=True, folder='motion/'
)

# Built-in motion visualization (drift raster + motion field)
sw.plot_motion_info(motion_info, recording=recording)
plt.savefig('motion_analysis.png', dpi=300, bbox_inches='tight')

# Or inspect the Motion object directly
motion = motion_info['motion']
displacement = motion.displacement[0]          # (n_temporal_bins, n_spatial_bins)
temporal_bins = motion.temporal_bins_s[0]
plt.figure(figsize=(10, 4))
plt.plot(temporal_bins, displacement, alpha=0.5)
plt.xlabel('Time (s)'); plt.ylabel('Displacement (um)'); plt.title('Estimated Motion')
plt.savefig('motion_traces.png', dpi=300, bbox_inches='tight')
```

## Waveform Plots

### Single Unit Waveforms

```python
unit_id = 0

# Basic waveforms
sw.plot_unit_waveforms(analyzer, unit_ids=[unit_id])
plt.savefig(f'unit_{unit_id}_waveforms.png')

# With density map
sw.plot_unit_waveform_density_map(analyzer, unit_ids=[unit_id])
plt.savefig(f'unit_{unit_id}_density.png')
```

### Template Comparison

```python
# Compare multiple units
unit_ids = [0, 1, 2, 3]
sw.plot_unit_templates(analyzer, unit_ids=unit_ids)
plt.savefig('template_comparison.png')
```

### Waveforms on Probe

```python
# Show waveforms spatially on probe
sw.plot_unit_waveforms_on_probe(
    analyzer,
    unit_ids=[unit_id],
    plot_channels=True,
)
plt.savefig(f'unit_{unit_id}_probe.png')
```

## Quality Metrics Visualization

### Metrics Overview

```python
# Built-in quality-metrics widget (scatter matrix of all computed metrics)
sw.plot_quality_metrics(analyzer)
plt.savefig('quality_overview.png', dpi=300, bbox_inches='tight')
```

### Metrics Distribution

```python
fig, axes = plt.subplots(2, 3, figsize=(12, 8))

metric_names = ['snr', 'isi_violations_ratio', 'presence_ratio',
                'amplitude_cutoff', 'firing_rate', 'amplitude_cv']

for ax, metric in zip(axes.flat, metric_names):
    if metric in metrics.columns:
        values = metrics[metric].dropna()
        ax.hist(values, bins=30, edgecolor='black', alpha=0.7)
        ax.axvline(values.median(), color='red', linestyle='--', label='median')
        ax.set_xlabel(metric)
        ax.set_ylabel('Count')
        ax.legend()

plt.tight_layout()
plt.savefig('metrics_distribution.png', dpi=300)
```

### Metrics Scatter Matrix

```python
import pandas as pd

key_metrics = ['snr', 'isi_violations_ratio', 'presence_ratio', 'firing_rate']
pd.plotting.scatter_matrix(
    metrics[key_metrics],
    figsize=(10, 10),
    alpha=0.5,
    diagonal='hist',
)
plt.savefig('metrics_scatter.png', dpi=300)
```

### Metrics vs Labels

```python
labels_series = pd.Series(labels)

fig, axes = plt.subplots(1, 3, figsize=(12, 4))

for ax, metric in zip(axes, ['snr', 'isi_violations_ratio', 'presence_ratio']):
    for label in ['good', 'mua', 'noise']:
        mask = labels_series == label
        if mask.any():
            ax.hist(metrics.loc[mask.index[mask], metric],
                   alpha=0.5, label=label, bins=20)
    ax.set_xlabel(metric)
    ax.legend()

plt.tight_layout()
plt.savefig('metrics_by_label.png', dpi=300)
```

## Correlogram Plots

### Autocorrelogram

```python
sw.plot_autocorrelograms(
    analyzer,
    unit_ids=[unit_id],
    window_ms=50,
    bin_ms=1,
)
plt.savefig(f'unit_{unit_id}_acg.png')
```

### Cross-correlograms

```python
unit_pairs = [(0, 1), (0, 2), (1, 2)]
sw.plot_crosscorrelograms(
    analyzer,
    unit_pairs=unit_pairs,
    window_ms=50,
    bin_ms=1,
)
plt.savefig('crosscorrelograms.png')
```

### Correlogram Matrix

```python
sw.plot_autocorrelograms(
    analyzer,
    unit_ids=analyzer.sorting.unit_ids[:10],  # First 10 units
)
plt.savefig('acg_matrix.png')
```

## Spike Train Plots

### Raster Plot

```python
sw.plot_rasters(
    sorting,
    time_range=(0, 30),  # First 30 seconds
    unit_ids=unit_ids[:5],
)
plt.savefig('raster.png')
```

### Firing Rate Over Time

```python
unit_id = 0
spike_train = sorting.get_unit_spike_train(unit_id)
fs = recording.get_sampling_frequency()
times = spike_train / fs

# Compute firing rate histogram
bin_width = 1.0  # seconds
bins = np.arange(0, recording.get_total_duration(), bin_width)
hist, _ = np.histogram(times, bins=bins)
firing_rate = hist / bin_width

plt.figure(figsize=(12, 3))
plt.bar(bins[:-1], firing_rate, width=bin_width, edgecolor='none')
plt.xlabel('Time (s)')
plt.ylabel('Firing rate (Hz)')
plt.title(f'Unit {unit_id} firing rate')
plt.savefig(f'unit_{unit_id}_firing_rate.png', dpi=300)
```

## Probe and Location Plots

### Probe Layout

```python
sw.plot_probe_map(recording, with_channel_ids=True)
plt.savefig('probe_layout.png')
```

### Unit Locations on Probe

```python
sw.plot_unit_locations(analyzer, with_channel_ids=True)
plt.savefig('unit_locations.png')
```

### Spike Locations

```python
sw.plot_spike_locations(analyzer, unit_ids=[unit_id])
plt.savefig(f'unit_{unit_id}_spike_locations.png')
```

## Amplitude Plots

### Amplitudes Over Time

```python
sw.plot_amplitudes(
    analyzer,
    unit_ids=[unit_id],
    plot_histograms=True,
)
plt.savefig(f'unit_{unit_id}_amplitudes.png')
```

### Amplitude Distribution

```python
amplitudes = analyzer.get_extension('spike_amplitudes').get_data()
spike_vector = sorting.to_spike_vector()
unit_idx = list(sorting.unit_ids).index(unit_id)
unit_mask = spike_vector['unit_index'] == unit_idx
unit_amps = amplitudes[unit_mask]

fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(unit_amps, bins=50, edgecolor='black', alpha=0.7)
ax.axvline(np.median(unit_amps), color='red', linestyle='--', label='median')
ax.set_xlabel('Amplitude (uV)')
ax.set_ylabel('Count')
ax.set_title(f'Unit {unit_id} Amplitude Distribution')
ax.legend()
plt.savefig(f'unit_{unit_id}_amp_dist.png', dpi=300)
```

## ISI Plots

### ISI Histogram

```python
sw.plot_isi_distribution(
    analyzer,
    unit_ids=[unit_id],
    window_ms=100,
    bin_ms=1,
)
plt.savefig(f'unit_{unit_id}_isi.png')
```

### ISI with Refractory Markers

```python
spike_train = sorting.get_unit_spike_train(unit_id)
fs = recording.get_sampling_frequency()
isis = np.diff(spike_train) / fs * 1000  # ms

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(isis[isis < 100], bins=100, edgecolor='black', alpha=0.7)
ax.axvline(1.5, color='red', linestyle='--', label='1.5ms refractory')
ax.axvline(3.0, color='orange', linestyle='--', label='3ms threshold')
ax.set_xlabel('ISI (ms)')
ax.set_ylabel('Count')
ax.set_title(f'Unit {unit_id} ISI Distribution')
ax.legend()
plt.savefig(f'unit_{unit_id}_isi_detailed.png', dpi=300)
```

## Summary Plots

### Unit Summary Panel

```python
# Built-in one-call summary (waveform, template, ACG, amplitudes, location)
sw.plot_unit_summary(analyzer, unit_id=unit_id)
plt.savefig(f'unit_{unit_id}_summary.png', dpi=300, bbox_inches='tight')
```

### Manual Multi-Panel Summary

```python
fig = plt.figure(figsize=(16, 12))

# Waveforms
ax1 = fig.add_subplot(2, 3, 1)
wfs = analyzer.get_extension('waveforms').get_waveforms(unit_id)
for i in range(min(50, wfs.shape[0])):
    ax1.plot(wfs[i, :, 0], 'k', alpha=0.1, linewidth=0.5)
template = wfs.mean(axis=0)[:, 0]
ax1.plot(template, 'b', linewidth=2)
ax1.set_title('Waveforms')

# Template
ax2 = fig.add_subplot(2, 3, 2)
templates_ext = analyzer.get_extension('templates')
template = templates_ext.get_unit_template(unit_id, operator='average')
template_std = templates_ext.get_unit_template(unit_id, operator='std')
x = range(template.shape[0])
ax2.plot(x, template[:, 0], 'b', linewidth=2)
ax2.fill_between(x, template[:, 0] - template_std[:, 0],
                 template[:, 0] + template_std[:, 0], alpha=0.3)
ax2.set_title('Template')

# Autocorrelogram
ax3 = fig.add_subplot(2, 3, 3)
correlograms = analyzer.get_extension('correlograms')
ccg, bins = correlograms.get_data()
unit_idx = list(sorting.unit_ids).index(unit_id)
ax3.bar(bins[:-1], ccg[unit_idx, unit_idx, :], width=bins[1]-bins[0], color='gray')
ax3.axvline(0, color='r', linestyle='--', alpha=0.5)
ax3.set_title('Autocorrelogram')

# Amplitudes
ax4 = fig.add_subplot(2, 3, 4)
amps_ext = analyzer.get_extension('spike_amplitudes')
amps = amps_ext.get_data()
spike_vector = sorting.to_spike_vector()
unit_mask = spike_vector['unit_index'] == unit_idx
unit_times = spike_vector['sample_index'][unit_mask] / fs
unit_amps = amps[unit_mask]
ax4.scatter(unit_times, unit_amps, s=1, alpha=0.3)
ax4.set_xlabel('Time (s)')
ax4.set_ylabel('Amplitude')
ax4.set_title('Amplitudes')

# ISI
ax5 = fig.add_subplot(2, 3, 5)
isis = np.diff(sorting.get_unit_spike_train(unit_id)) / fs * 1000
ax5.hist(isis[isis < 100], bins=50, color='gray', edgecolor='black')
ax5.axvline(1.5, color='r', linestyle='--')
ax5.set_xlabel('ISI (ms)')
ax5.set_title('ISI Distribution')

# Metrics
ax6 = fig.add_subplot(2, 3, 6)
unit_metrics = metrics.loc[unit_id]
text_lines = [f"{k}: {v:.4f}" for k, v in unit_metrics.items() if not np.isnan(v)]
ax6.text(0.1, 0.9, '\n'.join(text_lines[:8]), transform=ax6.transAxes,
         verticalalignment='top', fontsize=10, family='monospace')
ax6.axis('off')
ax6.set_title('Metrics')

plt.tight_layout()
plt.savefig(f'unit_{unit_id}_full_summary.png', dpi=300)
```

## Publication-Quality Settings

### Figure Sizes

```python
# Single column (3.5 inches)
fig, ax = plt.subplots(figsize=(3.5, 3))

# Double column (7 inches)
fig, ax = plt.subplots(figsize=(7, 4))

# Full page
fig, ax = plt.subplots(figsize=(7, 9))
```

### Font Settings

```python
plt.rcParams.update({
    'font.size': 8,
    'axes.titlesize': 9,
    'axes.labelsize': 8,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'font.family': 'Arial',
})
```

### Export Settings

```python
# For publications
plt.savefig('figure.pdf', format='pdf', bbox_inches='tight')
plt.savefig('figure.svg', format='svg', bbox_inches='tight')

# High-res PNG
plt.savefig('figure.png', dpi=600, bbox_inches='tight', facecolor='white')
```

### Color Palettes

```python
# Colorblind-friendly
colors = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#F0E442']

# For good/mua/noise
label_colors = {'good': '#2ecc71', 'mua': '#f39c12', 'noise': '#e74c3c'}
```

### `references/standard_workflow.md`

# Standard Neuropixels Analysis Workflow

Complete step-by-step guide for analyzing Neuropixels recordings from raw data to curated
units, using the SpikeInterface API directly.

## Overview

```
Raw Recording → Preprocessing → Motion Correction → Spike Sorting →
Postprocessing → Quality Metrics → Curation → Export
```

```python
import spikeinterface.full as si
import spikeinterface.curation as sc

si.set_global_job_kwargs(n_jobs=-1, chunk_duration="1s", progress_bar=True)
```

## 1. Data Loading

### Supported formats

```python
# Inspect streams first
stream_names, stream_ids = si.get_neo_streams("spikeglx", "/path/to/run_g0/")

# SpikeGLX (most common)
recording = si.read_spikeglx("/path/to/run_g0/", stream_name="imec0.ap", load_sync_channel=False)

# Open Ephys
recording = si.read_openephys("/path/to/experiment/")

# NWB
recording = si.read_nwb("/path/to/file.nwb")
```

### Verify recording properties

```python
print(f"Channels: {recording.get_num_channels()}")
print(f"Duration: {recording.get_total_duration():.1f}s")
print(f"Sampling rate: {recording.get_sampling_frequency()}Hz")
print(f"Probe: {recording.get_probe()}")
locations = recording.get_channel_locations()
```

## 2. Preprocessing

### Standard chain (IBL-style)

```python
rec = si.highpass_filter(recording, freq_min=400.0)
bad_channel_ids, channel_labels = si.detect_bad_channels(rec)
rec = rec.remove_channels(bad_channel_ids)
rec = si.phase_shift(rec)                                   # ADC phase (NP 1.0)
rec = si.common_reference(rec, operator="median", reference="global")
```

A bandpass alternative (some labs prefer an explicit passband):

```python
rec = si.bandpass_filter(recording, freq_min=300.0, freq_max=6000.0)
rec = si.phase_shift(rec)
bad_channel_ids, _ = si.detect_bad_channels(rec)
rec = rec.remove_channels(bad_channel_ids)
rec = si.common_reference(rec, operator="median", reference="global")
```

### Spatial destriping (strong artifacts)

```python
rec = si.highpass_filter(recording, freq_min=400.0)
rec = si.phase_shift(rec)
rec = si.highpass_spatial_filter(rec)                       # destriping
rec = si.common_reference(rec, operator="median", reference="global")
```

### Save preprocessed data

```python
rec = rec.save(folder="preprocessed/", format="binary")
```

## 3. Motion/Drift Correction

### Check whether correction is needed

```python
from spikeinterface.sortingcomponents.peak_detection import detect_peaks
from spikeinterface.sortingcomponents.peak_localization import localize_peaks

noise_levels = si.get_noise_levels(rec, return_in_uV=False)
peaks = detect_peaks(rec, method="locally_exclusive", noise_levels=noise_levels,
                     detect_threshold=5, radius_um=50.0)
peak_locations = localize_peaks(rec, peaks, method="center_of_mass")

si.plot_drift_raster_map(peaks=peaks, peak_locations=peak_locations, recording=rec, clim=(-50, 50))
```

### Apply correction

```python
# One-call correction with a preset
rec_corrected = si.correct_motion(rec, preset="nonrigid_fast_and_accurate", folder="motion/")
```

See [MOTION_CORRECTION.md](MOTION_CORRECTION.md) for the full estimate/interpolate pipeline
and DREDge usage.

## 4. Spike Sorting

### Recommended: Kilosort4

```python
sorting = si.run_sorter("kilosort4", rec_corrected, folder="sorting_KS4/", verbose=True)

# With custom parameters
sorting = si.run_sorter(
    "kilosort4", rec_corrected, folder="sorting_KS4/",
    nblocks=5,           # non-rigid drift blocks
    Th_universal=9,      # detection threshold
    Th_learned=8,
    batch_size=60000,
)
```

### Alternative sorters

```python
sorting = si.run_sorter("spykingcircus2", rec_corrected, folder="sc2/")   # CPU
sorting = si.run_sorter("tridesclous2", rec_corrected, folder="tdc2/")    # CPU
sorting = si.run_sorter("mountainsort5", rec_corrected, folder="ms5/")    # CPU
```

### Compare multiple sorters

```python
sortings = {s: si.run_sorter(s, rec_corrected, folder=f"{s}/")
            for s in ["kilosort4", "spykingcircus2"]}

comparison = si.compare_multiple_sorters(list(sortings.values()),
                                         name_list=list(sortings.keys()))
agreement = comparison.get_agreement_sorting(minimum_agreement_count=2)
```

## 5. Postprocessing

### Create analyzer and compute extensions

```python
analyzer = si.create_sorting_analyzer(sorting, rec_corrected, sparse=True,
                                      format="binary_folder", folder="analyzer/")

analyzer.compute("random_spikes", method="uniform", max_spikes_per_unit=500)
analyzer.compute("waveforms", ms_before=1.0, ms_after=2.0)
analyzer.compute("templates", operators=["average", "std"])
analyzer.compute("noise_levels")
analyzer.compute("spike_amplitudes")
analyzer.compute("correlograms", window_ms=50.0, bin_ms=1.0)
analyzer.compute("unit_locations", method="monopolar_triangulation")
analyzer.compute("template_similarity")
```

## 6. Quality Metrics

```python
metric_names = ["snr", "isi_violation", "presence_ratio", "amplitude_cutoff",
                "firing_rate", "amplitude_cv", "sliding_rp_violation"]
analyzer.compute("quality_metrics", metric_names=metric_names)
metrics = analyzer.get_extension("quality_metrics").get_data()
print(metrics.head())
```

### Key metrics

| Metric (column) | Good value | Description |
|-----------------|------------|-------------|
| `snr` | > 5 | Signal-to-noise ratio |
| `isi_violations_ratio` | < 0.5 (strict: < 0.01) | Refractory period violations |
| `presence_ratio` | > 0.9 | Fraction of recording with spikes |
| `amplitude_cutoff` | < 0.1 | Estimated missed spikes |
| `firing_rate` | > 0.1 Hz | Average firing rate |

## 7. Curation

### Threshold-based

```python
query = "(amplitude_cutoff < 0.1) & (isi_violations_ratio < 0.5) & (presence_ratio > 0.9)"
good_unit_ids = metrics.query(query).index.values
```

For `allen` / `ibl` / `strict` presets in one call, use `scripts/compute_metrics.py`.

### Model-based (UnitRefine)

```python
noise_labels = sc.model_based_label_units(
    sorting_analyzer=analyzer,
    repo_id="SpikeInterface/UnitRefine_noise_neural_classifier",
    trust_model=True,
)
neural = analyzer.remove_units(noise_labels[noise_labels["prediction"] == "noise"].index)
sua_mua = sc.model_based_label_units(
    sorting_analyzer=neural,
    repo_id="SpikeInterface/UnitRefine_sua_mua_classifier",
    trust_model=True,
)
```

### AI-assisted (uncertain units)

Read API keys from the environment — never hardcode them (see [AI_CURATION.md](AI_CURATION.md)):

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
uncertain = metrics.query("snr > 3 and snr < 8").index.tolist()
# Render each uncertain unit's summary image and ask the model to classify it.
```

## 8. Export Results

### Export to Phy

```python
analyzer_clean = analyzer.select_units(good_unit_ids, folder="analyzer_clean/", format="binary_folder")
si.export_to_phy(analyzer_clean, output_folder="phy_export/",
                 compute_pc_features=True, compute_amplitudes=True)
```

### Export to NWB

```python
from spikeinterface.exporters import export_to_nwb
export_to_nwb(analyzer_clean, "results.nwb")
```

### Save quality summary

```python
metrics.to_csv("quality_metrics.csv")

import json
labels = {int(uid): ("good" if uid in good_unit_ids else "other") for uid in metrics.index}
with open("curation_labels.json", "w") as f:
    json.dump(labels, f, indent=2)

si.export_report(analyzer_clean, "report/", format="png")
```

## Full Pipeline Example

```python
import spikeinterface.full as si

si.set_global_job_kwargs(n_jobs=-1, chunk_duration="1s", progress_bar=True)

# Load
recording = si.read_spikeglx("/data/experiment/", stream_name="imec0.ap", load_sync_channel=False)

# Preprocess
rec = si.highpass_filter(recording, freq_min=400.0)
bad_channel_ids, _ = si.detect_bad_channels(rec)
rec = rec.remove_channels(bad_channel_ids)
rec = si.phase_shift(rec)
rec = si.common_reference(rec, operator="median", reference="global")

# Motion correction
rec = si.correct_motion(rec, preset="nonrigid_fast_and_accurate", folder="motion/")

# Sort
sorting = si.run_sorter("kilosort4", rec, folder="ks4/")

# Postprocess + metrics
analyzer = si.create_sorting_analyzer(sorting, rec, sparse=True, format="binary_folder", folder="analyzer/")
analyzer.compute(["random_spikes", "waveforms", "templates", "noise_levels",
                  "spike_amplitudes", "correlograms", "unit_locations"])
analyzer.compute("quality_metrics",
                 metric_names=["snr", "isi_violation", "presence_ratio", "amplitude_cutoff", "firing_rate"])
metrics = analyzer.get_extension("quality_metrics").get_data()

# Curate
query = "(amplitude_cutoff < 0.1) & (isi_violations_ratio < 0.5) & (presence_ratio > 0.9)"
good_unit_ids = metrics.query(query).index.values
print(f"Good units: {len(good_unit_ids)}/{len(metrics)}")
```

Or run it as a script:

```bash
python scripts/neuropixels_pipeline.py /data/experiment/ output/ --sorter kilosort4 --curation allen
```

## Tips for Success

1. **Always visualize drift** before deciding on motion correction.
2. **Save preprocessed data** to avoid recomputing (and Kilosort needs a binary file).
3. **Compare multiple sorters** for critical experiments.
4. **Review uncertain units manually** — don't trust automated curation blindly.
5. **Document parameters and model repo IDs** for reproducibility.
6. **Use a GPU** for Kilosort4.

### `scripts/compute_metrics.py`

```python
#!/usr/bin/env python
"""
Compute quality metrics and curate units.

Usage:
    python compute_metrics.py sorting/ preprocessed/ --output metrics/
"""

import argparse
from pathlib import Path
import json

import pandas as pd
import spikeinterface.full as si


# Curation criteria presets. snr and presence_ratio are minima, the other two are
# maxima, and each preset is at least as strict as the one above it. The ISI,
# presence, and amplitude thresholds follow references/QUALITY_METRICS.md:
# Allen Visual Coding uses isi_violations_ratio < 0.5, IBL's reproducible-ephys
# criteria tighten that to < 0.1, and the strict single-unit set to < 0.01.
CURATION_CRITERIA = {
    'allen': {
        'snr': 3.0,
        'isi_violations_ratio': 0.5,
        'presence_ratio': 0.9,
        'amplitude_cutoff': 0.1,
    },
    'ibl': {
        'snr': 4.0,
        'isi_violations_ratio': 0.1,
        'presence_ratio': 0.9,
        'amplitude_cutoff': 0.1,
    },
    'strict': {
        'snr': 5.0,
        'isi_violations_ratio': 0.01,
        'presence_ratio': 0.95,
        'amplitude_cutoff': 0.05,
    },
}


def compute_metrics(
    sorting_path: str,
    recording_path: str,
    output_dir: str,
    curation_method: str = 'allen',
    n_jobs: int = -1,
):
    """Compute quality metrics and apply curation."""

    print(f"Loading sorting from: {sorting_path}")
    sorting = si.load_extractor(Path(sorting_path) / 'sorting')

    print(f"Loading recording from: {recording_path}")
    recording = si.load_extractor(Path(recording_path) / 'preprocessed')

    print(f"Units: {len(sorting.unit_ids)}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create analyzer
    print("Creating SortingAnalyzer...")
    analyzer = si.create_sorting_analyzer(
        sorting,
        recording,
        format='binary_folder',
        folder=output_path / 'analyzer',
        sparse=True,
    )

    # Compute extensions
    print("Computing waveforms...")
    analyzer.compute('random_spikes', max_spikes_per_unit=500)
    analyzer.compute('waveforms', ms_before=1.0, ms_after=2.0)
    analyzer.compute('templates', operators=['average', 'std'])

    print("Computing additional extensions...")
    analyzer.compute('noise_levels')
    analyzer.compute('spike_amplitudes')
    analyzer.compute('correlograms', window_ms=50.0, bin_ms=1.0)
    analyzer.compute('unit_locations', method='monopolar_triangulation')

    # Compute quality metrics
    print("Computing quality metrics...")
    metrics = si.compute_quality_metrics(
        analyzer,
        metric_names=[
            'snr',
            'isi_violations_ratio',
            'presence_ratio',
            'amplitude_cutoff',
            'firing_rate',
            'amplitude_cv',
            'sliding_rp_violation',
        ],
        n_jobs=n_jobs,
    )

    # Save metrics
    metrics.to_csv(output_path / 'quality_metrics.csv')
    print(f"Saved metrics to: {output_path / 'quality_metrics.csv'}")

    # Apply curation
    criteria = CURATION_CRITERIA.get(curation_method, CURATION_CRITERIA['allen'])
    print(f"\nApplying {curation_method} curation criteria: {criteria}")

    labels = {}
    for unit_id in metrics.index:
        row = metrics.loc[unit_id]

        # Check each criterion
        is_good = True

        if criteria.get('snr') and row.get('snr', 0) < criteria['snr']:
            is_good = False

        if criteria.get('isi_violations_ratio') and row.get('isi_violations_ratio', 1) > criteria['isi_violations_ratio']:
            is_good = False

        if criteria.get('presence_ratio') and row.get('presence_ratio', 0) < criteria['presence_ratio']:
            is_good = False

        if criteria.get('amplitude_cutoff') and row.get('amplitude_cutoff', 1) > criteria['amplitude_cutoff']:
            is_good = False

        # Classify
        if is_good:
            labels[int(unit_id)] = 'good'
        elif row.get('snr', 0) < 2:
            labels[int(unit_id)] = 'noise'
        else:
            labels[int(unit_id)] = 'mua'

    # Save labels
    with open(output_path / 'curation_labels.json', 'w') as f:
        json.dump(labels, f, indent=2)

    # Summary
    label_counts = {}
    for label in labels.values():
        label_counts[label] = label_counts.get(label, 0) + 1

    print(f"\nCuration summary:")
    print(f"  Good: {label_counts.get('good', 0)}")
    print(f"  MUA: {label_counts.get('mua', 0)}")
    print(f"  Noise: {label_counts.get('noise', 0)}")
    print(f"  Total: {len(labels)}")

    # Metrics summary
    print(f"\nMetrics summary:")
    for col in ['snr', 'isi_violations_ratio', 'presence_ratio', 'firing_rate']:
        if col in metrics.columns:
            print(f"  {col}: {metrics[col].median():.4f} (median)")

    return analyzer, metrics, labels


def main():
    parser = argparse.ArgumentParser(description='Compute quality metrics')
    parser.add_argument('sorting', help='Path to sorting directory')
    parser.add_argument('recording', help='Path to preprocessed recording')
    parser.add_argument('--output', '-o', default='metrics/', help='Output directory')
    parser.add_argument('--curation', '-c', default='allen',
                       choices=['allen', 'ibl', 'strict'])
    parser.add_argument('--n-jobs', type=int, default=-1, help='Number of parallel jobs')

    args = parser.parse_args()

    compute_metrics(
        args.sorting,
        args.recording,
        args.output,
        curation_method=args.curation,
        n_jobs=args.n_jobs,
    )


if __name__ == '__main__':
    main()
```

### `scripts/explore_recording.py`

```python
#!/usr/bin/env python3
"""
Quick exploration of Neuropixels recording.

Usage:
    python explore_recording.py /path/to/spikeglx/data
"""

import argparse
import spikeinterface.full as si
import matplotlib.pyplot as plt
import numpy as np


def explore_recording(data_path: str, stream_name: str = 'imec0.ap'):
    """Explore a Neuropixels recording."""

    print(f"Loading: {data_path}")
    recording = si.read_spikeglx(data_path, stream_name=stream_name)

    # Basic info
    print("\n" + "="*50)
    print("RECORDING INFO")
    print("="*50)
    print(f"Channels: {recording.get_num_channels()}")
    print(f"Duration: {recording.get_total_duration():.2f} s ({recording.get_total_duration()/60:.2f} min)")
    print(f"Sampling rate: {recording.get_sampling_frequency()} Hz")
    print(f"Total samples: {recording.get_num_samples()}")

    # Probe info
    probe = recording.get_probe()
    print(f"\nProbe: {probe.manufacturer} {probe.model_name if hasattr(probe, 'model_name') else ''}")
    print(f"Probe shape: {probe.ndim}D")

    # Channel groups
    if recording.get_channel_groups() is not None:
        groups = np.unique(recording.get_channel_groups())
        print(f"Channel groups (shanks): {len(groups)}")

    # Check for bad channels
    print("\n" + "="*50)
    print("BAD CHANNEL DETECTION")
    print("="*50)
    bad_ids, labels = si.detect_bad_channels(recording)
    if len(bad_ids) > 0:
        print(f"Bad channels found: {len(bad_ids)}")
        for ch, label in zip(bad_ids, labels):
            print(f"  Channel {ch}: {label}")
    else:
        print("No bad channels detected")

    # Sample traces
    print("\n" + "="*50)
    print("SIGNAL STATISTICS")
    print("="*50)

    # Get 1 second of data
    n_samples = int(recording.get_sampling_frequency())
    traces = recording.get_traces(start_frame=0, end_frame=n_samples)

    print(f"Sample mean: {np.mean(traces):.2f}")
    print(f"Sample std: {np.std(traces):.2f}")
    print(f"Sample min: {np.min(traces):.2f}")
    print(f"Sample max: {np.max(traces):.2f}")

    return recording


def plot_probe(recording, output_path=None):
    """Plot probe layout."""
    fig, ax = plt.subplots(figsize=(4, 12))
    si.plot_probe_map(recording, ax=ax, with_channel_ids=False)
    ax.set_title('Probe Layout')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()


def plot_traces(recording, duration=1.0, output_path=None):
    """Plot raw traces."""
    n_samples = int(duration * recording.get_sampling_frequency())
    traces = recording.get_traces(start_frame=0, end_frame=n_samples)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot subset of channels
    n_channels = min(20, recording.get_num_channels())
    channel_idx = np.linspace(0, recording.get_num_channels()-1, n_channels, dtype=int)

    time = np.arange(n_samples) / recording.get_sampling_frequency()

    for i, ch in enumerate(channel_idx):
        offset = i * 200  # Offset for visibility
        ax.plot(time, traces[:, ch] + offset, 'k', linewidth=0.5)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Channel (offset)')
    ax.set_title(f'Raw Traces ({n_channels} channels)')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()


def plot_power_spectrum(recording, output_path=None):
    """Plot power spectrum."""
    from scipy import signal

    # Get data from middle channel
    mid_ch = recording.get_num_channels() // 2
    n_samples = min(int(10 * recording.get_sampling_frequency()), recording.get_num_samples())

    traces = recording.get_traces(
        start_frame=0,
        end_frame=n_samples,
        channel_ids=[recording.channel_ids[mid_ch]]
    ).flatten()

    fs = recording.get_sampling_frequency()

    # Compute power spectrum
    freqs, psd = signal.welch(traces, fs, nperseg=4096)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.semilogy(freqs, psd)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Power Spectral Density')
    ax.set_title(f'Power Spectrum (Channel {mid_ch})')
    ax.set_xlim(0, 5000)
    ax.axvline(300, color='r', linestyle='--', alpha=0.5, label='300 Hz')
    ax.axvline(6000, color='r', linestyle='--', alpha=0.5, label='6000 Hz')
    ax.legend()
    ax.grid(True, alpha=0.3)

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Explore Neuropixels recording')
    parser.add_argument('data_path', help='Path to SpikeGLX recording')
    parser.add_argument('--stream', default='imec0.ap', help='Stream name (e.g. imec0.ap)')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    parser.add_argument('--output', default=None, help='Output directory for plots')

    args = parser.parse_args()

    recording = explore_recording(args.data_path, args.stream)

    if args.plot:
        import os
        if args.output:
            os.makedirs(args.output, exist_ok=True)
            plot_probe(recording, f"{args.output}/probe_map.png")
            plot_traces(recording, output_path=f"{args.output}/raw_traces.png")
            plot_power_spectrum(recording, f"{args.output}/power_spectrum.png")
        else:
            plot_probe(recording)
            plot_traces(recording)
            plot_power_spectrum(recording)
```

### `scripts/export_to_phy.py`

```python
#!/usr/bin/env python
"""
Export sorting results to Phy for manual curation.

Usage:
    python export_to_phy.py metrics/analyzer --output phy_export/
"""

import argparse
from pathlib import Path

import spikeinterface.full as si
from spikeinterface.exporters import export_to_phy


def export_phy(
    analyzer_path: str,
    output_dir: str,
    copy_binary: bool = True,
    compute_amplitudes: bool = True,
    compute_pc_features: bool = True,
    n_jobs: int = -1,
):
    """Export to Phy format."""

    print(f"Loading analyzer from: {analyzer_path}")
    analyzer = si.load_sorting_analyzer(analyzer_path)

    print(f"Units: {len(analyzer.sorting.unit_ids)}")

    output_path = Path(output_dir)

    # Compute required extensions if missing
    if compute_amplitudes and analyzer.get_extension('spike_amplitudes') is None:
        print("Computing spike amplitudes...")
        analyzer.compute('spike_amplitudes')

    if compute_pc_features and analyzer.get_extension('principal_components') is None:
        print("Computing principal components...")
        analyzer.compute('principal_components', n_components=5, mode='by_channel_local')

    print(f"Exporting to Phy: {output_path}")
    export_to_phy(
        analyzer,
        output_folder=output_path,
        copy_binary=copy_binary,
        compute_amplitudes=compute_amplitudes,
        compute_pc_features=compute_pc_features,
        n_jobs=n_jobs,
    )

    print("\nExport complete!")
    print(f"To open in Phy, run:")
    print(f"  phy template-gui {output_path / 'params.py'}")


def main():
    parser = argparse.ArgumentParser(description='Export to Phy')
    parser.add_argument('analyzer', help='Path to sorting analyzer')
    parser.add_argument('--output', '-o', default='phy_export/', help='Output directory')
    parser.add_argument('--no-binary', action='store_true', help='Skip copying binary file')
    parser.add_argument('--no-amplitudes', action='store_true', help='Skip amplitude computation')
    parser.add_argument('--no-pc', action='store_true', help='Skip PC feature computation')
    parser.add_argument('--n-jobs', type=int, default=-1, help='Number of parallel jobs')

    args = parser.parse_args()

    export_phy(
        args.analyzer,
        args.output,
        copy_binary=not args.no_binary,
        compute_amplitudes=not args.no_amplitudes,
        compute_pc_features=not args.no_pc,
        n_jobs=args.n_jobs,
    )


if __name__ == '__main__':
    main()
```

### `scripts/neuropixels_pipeline.py`

```python
#!/usr/bin/env python3
"""
Neuropixels Data Analysis Pipeline (Best Practices Version)

Based on SpikeInterface, Allen Institute, and IBL recommendations.

Usage:
    python neuropixels_pipeline.py /path/to/spikeglx/data /path/to/output

References:
    - https://spikeinterface.readthedocs.io/en/stable/how_to/analyze_neuropixels.html
    - https://github.com/AllenInstitute/ecephys_spike_sorting
"""

import argparse
from pathlib import Path
import json
import spikeinterface.full as si
import numpy as np


def load_recording(data_path: str, stream_name: str = 'imec0.ap') -> si.BaseRecording:
    """Load a SpikeGLX or Open Ephys recording."""

    data_path = Path(data_path)

    # Auto-detect format
    if any(data_path.rglob('*.ap.bin')) or any(data_path.rglob('*.ap.meta')):
        # SpikeGLX format
        streams, _ = si.get_neo_streams('spikeglx', data_path)
        print(f"Available streams: {streams}")
        recording = si.read_spikeglx(data_path, stream_name=stream_name)
    elif any(data_path.rglob('*.oebin')):
        # Open Ephys format
        recording = si.read_openephys(data_path)
    else:
        raise ValueError(f"Unknown format in {data_path}")

    print(f"Loaded recording:")
    print(f"  Channels: {recording.get_num_channels()}")
    print(f"  Duration: {recording.get_total_duration():.2f} s")
    print(f"  Sampling rate: {recording.get_sampling_frequency()} Hz")

    return recording


def preprocess(
    recording: si.BaseRecording,
    apply_phase_shift: bool = True,
    freq_min: float = 400.,
) -> tuple:
    """
    Apply standard Neuropixels preprocessing.

    Following SpikeInterface recommendations:
    1. High-pass filter at 400 Hz (not 300)
    2. Detect and remove bad channels
    3. Phase shift (NP 1.0 only)
    4. Common median reference
    """
    print("Preprocessing...")

    # Step 1: High-pass filter
    rec = si.highpass_filter(recording, freq_min=freq_min)
    print(f"  Applied high-pass filter at {freq_min} Hz")

    # Step 2: Detect bad channels
    bad_channel_ids, channel_labels = si.detect_bad_channels(rec)
    if len(bad_channel_ids) > 0:
        print(f"  Detected {len(bad_channel_ids)} bad channels: {bad_channel_ids}")
        rec = rec.remove_channels(bad_channel_ids)
    else:
        print("  No bad channels detected")

    # Step 3: Phase shift (for Neuropixels 1.0)
    if apply_phase_shift:
        rec = si.phase_shift(rec)
        print("  Applied phase shift correction")

    # Step 4: Common median reference
    rec = si.common_reference(rec, operator='median', reference='global')
    print("  Applied common median reference")

    return rec, bad_channel_ids


def check_drift(recording: si.BaseRecording, output_folder: str) -> dict:
    """
    Detect peaks and check for drift before spike sorting.
    """
    print("Checking for drift...")

    from spikeinterface.sortingcomponents.peak_detection import detect_peaks
    from spikeinterface.sortingcomponents.peak_localization import localize_peaks

    job_kwargs = dict(n_jobs=8, chunk_duration='1s', progress_bar=True)

    # Get noise levels
    noise_levels = si.get_noise_levels(recording, return_in_uV=False)

    # Detect peaks
    peaks = detect_peaks(
        recording,
        method='locally_exclusive',
        noise_levels=noise_levels,
        detect_threshold=5,
        radius_um=50.,
        **job_kwargs
    )
    print(f"  Detected {len(peaks)} peaks")

    # Localize peaks
    peak_locations = localize_peaks(
        recording, peaks,
        method='center_of_mass',
        **job_kwargs
    )

    # Save drift plot
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 6))

    # Subsample for plotting
    n_plot = min(100000, len(peaks))
    idx = np.random.choice(len(peaks), n_plot, replace=False)

    ax.scatter(
        peaks['sample_index'][idx] / recording.get_sampling_frequency(),
        peak_locations['y'][idx],
        s=1, alpha=0.1, c='k'
    )
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Depth (μm)')
    ax.set_title('Peak Activity (Check for Drift)')

    plt.savefig(f'{output_folder}/drift_check.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved drift plot to {output_folder}/drift_check.png")

    # Estimate drift magnitude
    y_positions = peak_locations['y']
    drift_estimate = np.percentile(y_positions, 95) - np.percentile(y_positions, 5)
    print(f"  Estimated drift range: {drift_estimate:.1f} μm")

    return {
        'peaks': peaks,
        'peak_locations': peak_locations,
        'drift_estimate': drift_estimate
    }


def correct_motion(
    recording: si.BaseRecording,
    output_folder: str,
    preset: str = 'nonrigid_fast_and_accurate'
) -> si.BaseRecording:
    """Apply motion correction if needed."""
    print(f"Applying motion correction (preset: {preset})...")

    # correct_motion returns just the corrected recording by default. Pass
    # output_motion_info=True only if you also want the motion info dict (a tuple is
    # returned in that case).
    rec_corrected = si.correct_motion(
        recording,
        preset=preset,
        folder=f'{output_folder}/motion',
        n_jobs=8,
        chunk_duration='1s',
        progress_bar=True
    )

    print("  Motion correction complete")
    return rec_corrected


def run_spike_sorting(
    recording: si.BaseRecording,
    output_folder: str,
    sorter: str = 'kilosort4'
) -> si.BaseSorting:
    """Run spike sorting."""
    print(f"Running spike sorting with {sorter}...")

    sorter_folder = f'{output_folder}/sorting_{sorter}'

    sorting = si.run_sorter(
        sorter,
        recording,
        folder=sorter_folder,
        verbose=True
    )

    print(f"  Found {len(sorting.unit_ids)} units")
    print(f"  Total spikes: {sorting.get_total_num_spikes()}")

    return sorting


def postprocess(
    sorting: si.BaseSorting,
    recording: si.BaseRecording,
    output_folder: str
) -> tuple:
    """Run post-processing and compute quality metrics."""
    print("Post-processing...")

    job_kwargs = dict(n_jobs=8, chunk_duration='1s', progress_bar=True)

    # Create analyzer
    analyzer = si.create_sorting_analyzer(
        sorting, recording,
        sparse=True,
        format='binary_folder',
        folder=f'{output_folder}/analyzer'
    )

    # Compute extensions (order matters)
    print("  Computing waveforms...")
    analyzer.compute('random_spikes', method='uniform', max_spikes_per_unit=500)
    analyzer.compute('waveforms', ms_before=1.5, ms_after=2.0, **job_kwargs)
    analyzer.compute('templates', operators=['average', 'std'])
    analyzer.compute('noise_levels')

    print("  Computing spike features...")
    analyzer.compute('spike_amplitudes', **job_kwargs)
    analyzer.compute('correlograms', window_ms=100, bin_ms=1)
    analyzer.compute('unit_locations', method='monopolar_triangulation')
    analyzer.compute('template_similarity')

    print("  Computing quality metrics...")
    analyzer.compute('quality_metrics')

    qm = analyzer.get_extension('quality_metrics').get_data()

    return analyzer, qm


def curate_units(qm, method: str = 'allen') -> dict:
    """
    Classify units based on quality metrics.

    Methods:
        'allen': Allen Institute defaults (more permissive)
        'ibl': IBL standards
        'strict': Strict single-unit criteria
    """
    methods = ('allen', 'ibl', 'strict')
    if method not in methods:
        # Without this, an unrecognised method leaves every non-noise unit out of
        # `labels` entirely, so export_results() silently reports zero good units.
        raise ValueError(
            f"unknown curation method {method!r}; choose one of {', '.join(methods)}"
        )

    print(f"Curating units (method: {method})...")

    labels = {}

    for unit_id in qm.index:
        row = qm.loc[unit_id]

        # Noise detection (universal)
        if row['snr'] < 1.5:
            labels[unit_id] = 'noise'
            continue

        if method == 'allen':
            # Allen Institute defaults
            if (row['presence_ratio'] > 0.9 and
                row['isi_violations_ratio'] < 0.5 and
                row['amplitude_cutoff'] < 0.1):
                labels[unit_id] = 'good'
            elif row['isi_violations_ratio'] > 0.5:
                labels[unit_id] = 'mua'
            else:
                labels[unit_id] = 'unsorted'

        elif method == 'ibl':
            # IBL standards
            if (row['presence_ratio'] > 0.9 and
                row['isi_violations_ratio'] < 0.1 and
                row['amplitude_cutoff'] < 0.1 and
                row['firing_rate'] > 0.1):
                labels[unit_id] = 'good'
            elif row['isi_violations_ratio'] > 0.1:
                labels[unit_id] = 'mua'
            else:
                labels[unit_id] = 'unsorted'

        elif method == 'strict':
            # Strict single-unit
            if (row['snr'] > 5 and
                row['presence_ratio'] > 0.95 and
                row['isi_violations_ratio'] < 0.01 and
                row['amplitude_cutoff'] < 0.01):
                labels[unit_id] = 'good'
            elif row['isi_violations_ratio'] > 0.05:
                labels[unit_id] = 'mua'
            else:
                labels[unit_id] = 'unsorted'

    # Summary
    from collections import Counter
    counts = Counter(labels.values())
    print(f"  Classification: {dict(counts)}")

    return labels


def export_results(
    analyzer,
    sorting,
    recording,
    labels: dict,
    output_folder: str
):
    """Export results to various formats."""
    print("Exporting results...")

    # Get good units
    good_ids = [u for u, l in labels.items() if l == 'good']
    sorting_good = sorting.select_units(good_ids)

    # Export to Phy
    phy_folder = f'{output_folder}/phy_export'
    si.export_to_phy(analyzer, phy_folder,
                     compute_pc_features=True,
                     compute_amplitudes=True)
    print(f"  Phy export: {phy_folder}")

    # Generate report
    report_folder = f'{output_folder}/report'
    si.export_report(analyzer, report_folder, format='png')
    print(f"  Report: {report_folder}")

    # Save quality metrics
    qm = analyzer.get_extension('quality_metrics').get_data()
    qm.to_csv(f'{output_folder}/quality_metrics.csv')

    # Save labels
    with open(f'{output_folder}/unit_labels.json', 'w') as f:
        json.dump({str(k): v for k, v in labels.items()}, f, indent=2)

    # Save summary
    summary = {
        'total_units': len(sorting.unit_ids),
        'good_units': len(good_ids),
        'total_spikes': int(sorting.get_total_num_spikes()),
        'duration_s': float(recording.get_total_duration()),
        'n_channels': int(recording.get_num_channels()),
    }
    with open(f'{output_folder}/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"  Summary: {summary}")


def run_pipeline(
    data_path: str,
    output_path: str,
    sorter: str = 'kilosort4',
    stream_name: str = 'imec0.ap',
    apply_motion_correction: bool = True,
    curation_method: str = 'allen'
):
    """Run complete Neuropixels analysis pipeline."""

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    recording = load_recording(data_path, stream_name)

    # 2. Preprocess
    rec_preprocessed, bad_channels = preprocess(recording)

    # Save preprocessed
    preproc_folder = output_path / 'preprocessed'
    job_kwargs = dict(n_jobs=8, chunk_duration='1s', progress_bar=True)
    rec_preprocessed = rec_preprocessed.save(
        folder=str(preproc_folder),
        format='binary',
        **job_kwargs
    )

    # 3. Check drift
    drift_info = check_drift(rec_preprocessed, str(output_path))

    # 4. Motion correction (if needed)
    if apply_motion_correction and drift_info['drift_estimate'] > 20:
        print(f"Drift > 20 μm detected, applying motion correction...")
        rec_final = correct_motion(rec_preprocessed, str(output_path))
    else:
        print("Skipping motion correction (low drift)")
        rec_final = rec_preprocessed

    # 5. Spike sorting
    sorting = run_spike_sorting(rec_final, str(output_path), sorter)

    # 6. Post-processing
    analyzer, qm = postprocess(sorting, rec_final, str(output_path))

    # 7. Curation
    labels = curate_units(qm, method=curation_method)

    # 8. Export
    export_results(analyzer, sorting, rec_final, labels, str(output_path))

    print("\n" + "="*50)
    print("Pipeline complete!")
    print(f"Output directory: {output_path}")
    print("="*50)

    return analyzer, sorting, qm, labels


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Neuropixels analysis pipeline (best practices)'
    )
    parser.add_argument('data_path', help='Path to SpikeGLX/OpenEphys recording')
    parser.add_argument('output_path', help='Output directory')
    parser.add_argument('--sorter', default='kilosort4',
                        choices=['kilosort4', 'kilosort3', 'spykingcircus2', 'mountainsort5'],
                        help='Spike sorter to use')
    parser.add_argument('--stream', default='imec0.ap', help='Stream name')
    parser.add_argument('--no-motion-correction', action='store_true',
                        help='Skip motion correction')
    parser.add_argument('--curation', default='allen',
                        choices=['allen', 'ibl', 'strict'],
                        help='Curation method')

    args = parser.parse_args()

    run_pipeline(
        args.data_path,
        args.output_path,
        sorter=args.sorter,
        stream_name=args.stream,
        apply_motion_correction=not args.no_motion_correction,
        curation_method=args.curation
    )
```

### `scripts/preprocess_recording.py`

```python
#!/usr/bin/env python
"""
Preprocess Neuropixels recording.

Usage:
    python preprocess_recording.py /path/to/data --output preprocessed/ --format spikeglx
"""

import argparse
from pathlib import Path

import spikeinterface.full as si


def preprocess_recording(
    input_path: str,
    output_dir: str,
    format: str = 'auto',
    stream_name: str = None,
    freq_min: float = 300,
    freq_max: float = 6000,
    phase_shift: bool = True,
    common_ref: bool = True,
    detect_bad: bool = True,
    n_jobs: int = -1,
):
    """Preprocess a Neuropixels recording."""

    print(f"Loading recording from: {input_path}")

    # Load recording
    if format == 'spikeglx' or (format == 'auto' and 'imec' in str(input_path).lower()):
        recording = si.read_spikeglx(input_path, stream_name=stream_name or 'imec0.ap')
    elif format == 'openephys':
        recording = si.read_openephys(input_path)
    elif format == 'nwb':
        recording = si.read_nwb(input_path)
    else:
        # Try auto-detection
        try:
            recording = si.read_spikeglx(input_path, stream_name=stream_name or 'imec0.ap')
        except Exception:
            recording = si.load_extractor(input_path)

    print(f"Recording: {recording.get_num_channels()} channels, {recording.get_total_duration():.1f}s")

    # Preprocessing chain
    rec = recording

    # Bandpass filter
    print(f"Applying bandpass filter ({freq_min}-{freq_max} Hz)...")
    rec = si.bandpass_filter(rec, freq_min=freq_min, freq_max=freq_max)

    # Phase shift correction (for Neuropixels ADC)
    if phase_shift:
        print("Applying phase shift correction...")
        rec = si.phase_shift(rec)

    # Bad channel detection
    if detect_bad:
        print("Detecting bad channels...")
        bad_channel_ids, bad_labels = si.detect_bad_channels(rec)
        if len(bad_channel_ids) > 0:
            print(f"  Removing {len(bad_channel_ids)} bad channels: {bad_channel_ids[:10]}...")
            rec = rec.remove_channels(bad_channel_ids)

    # Common median reference
    if common_ref:
        print("Applying common median reference...")
        rec = si.common_reference(rec, operator='median', reference='global')

    # Save preprocessed
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Saving preprocessed recording to: {output_path}")
    rec.save(folder=output_path / 'preprocessed', n_jobs=n_jobs)

    # Save probe info
    probe = rec.get_probe()
    if probe is not None:
        from probeinterface import write_probeinterface
        write_probeinterface(output_path / 'probe.json', probe)

    print("Done!")
    print(f"  Output channels: {rec.get_num_channels()}")
    print(f"  Output duration: {rec.get_total_duration():.1f}s")

    return rec


def main():
    parser = argparse.ArgumentParser(description='Preprocess Neuropixels recording')
    parser.add_argument('input', help='Path to input recording')
    parser.add_argument('--output', '-o', default='preprocessed/', help='Output directory')
    parser.add_argument('--format', '-f', default='auto', choices=['auto', 'spikeglx', 'openephys', 'nwb'])
    parser.add_argument('--stream-name', default=None, help='Stream name for multi-probe recordings (e.g. imec0.ap)')
    parser.add_argument('--freq-min', type=float, default=300, help='Highpass cutoff (Hz)')
    parser.add_argument('--freq-max', type=float, default=6000, help='Lowpass cutoff (Hz)')
    parser.add_argument('--no-phase-shift', action='store_true', help='Skip phase shift correction')
    parser.add_argument('--no-cmr', action='store_true', help='Skip common median reference')
    parser.add_argument('--no-bad-channel', action='store_true', help='Skip bad channel detection')
    parser.add_argument('--n-jobs', type=int, default=-1, help='Number of parallel jobs')

    args = parser.parse_args()

    preprocess_recording(
        args.input,
        args.output,
        format=args.format,
        stream_name=args.stream_name,
        freq_min=args.freq_min,
        freq_max=args.freq_max,
        phase_shift=not args.no_phase_shift,
        common_ref=not args.no_cmr,
        detect_bad=not args.no_bad_channel,
        n_jobs=args.n_jobs,
    )


if __name__ == '__main__':
    main()
```

### `scripts/run_sorting.py`

```python
#!/usr/bin/env python
"""
Run spike sorting on preprocessed recording.

Usage:
    python run_sorting.py preprocessed/ --sorter kilosort4 --output sorting/
"""

import argparse
from pathlib import Path

import spikeinterface.full as si


# Default parameters for each sorter
SORTER_DEFAULTS = {
    'kilosort4': {
        'batch_size': 30000,
        'nblocks': 1,
        'Th_learned': 8,
        'Th_universal': 9,
    },
    'kilosort3': {
        'do_CAR': False,  # Already done in preprocessing
    },
    'spykingcircus2': {
        'apply_preprocessing': False,
    },
    'mountainsort5': {
        'filter': False,
        'whiten': False,
    },
}


def run_sorting(
    input_path: str,
    output_dir: str,
    sorter: str = 'kilosort4',
    sorter_params: dict = None,
    n_jobs: int = -1,
):
    """Run spike sorting."""

    print(f"Loading preprocessed recording from: {input_path}")
    recording = si.load_extractor(Path(input_path) / 'preprocessed')

    print(f"Recording: {recording.get_num_channels()} channels, {recording.get_total_duration():.1f}s")

    # Get sorter parameters
    params = SORTER_DEFAULTS.get(sorter, {}).copy()
    if sorter_params:
        params.update(sorter_params)

    print(f"Running {sorter} with params: {params}")

    output_path = Path(output_dir)

    # Run sorter (note: parameter is 'folder' not 'output_folder' in newer SpikeInterface)
    sorting = si.run_sorter(
        sorter,
        recording,
        folder=output_path / f'{sorter}_output',
        verbose=True,
        **params,
    )

    print(f"\nSorting complete!")
    print(f"  Units found: {len(sorting.unit_ids)}")
    print(f"  Total spikes: {sum(len(sorting.get_unit_spike_train(uid)) for uid in sorting.unit_ids)}")

    # Save sorting
    sorting.save(folder=output_path / 'sorting')
    print(f"  Saved to: {output_path / 'sorting'}")

    return sorting


def main():
    parser = argparse.ArgumentParser(description='Run spike sorting')
    parser.add_argument('input', help='Path to preprocessed recording')
    parser.add_argument('--output', '-o', default='sorting/', help='Output directory')
    parser.add_argument('--sorter', '-s', default='kilosort4',
                       choices=['kilosort4', 'kilosort3', 'spykingcircus2', 'mountainsort5'])
    parser.add_argument('--n-jobs', type=int, default=-1, help='Number of parallel jobs')

    args = parser.parse_args()

    run_sorting(
        args.input,
        args.output,
        sorter=args.sorter,
        n_jobs=args.n_jobs,
    )


if __name__ == '__main__':
    main()
```

### `assets/analysis_template.py`

```python
#!/usr/bin/env python
"""
Neuropixels Analysis Template

Complete analysis workflow from raw data to curated units.
Copy and customize this template for your analysis.

Usage:
    1. Copy this file to your analysis directory
    2. Update the PARAMETERS section
    3. Run: python analysis_template.py
"""

# =============================================================================
# PARAMETERS - Customize these for your analysis
# =============================================================================

# Input/Output paths
DATA_PATH = '/path/to/your/spikeglx/data/'
OUTPUT_DIR = 'analysis_output/'
DATA_FORMAT = 'spikeglx'  # 'spikeglx', 'openephys', or 'nwb'
STREAM_ID = 'imec0.ap'    # For multi-probe recordings

# Preprocessing parameters
FREQ_MIN = 300           # Highpass filter (Hz)
FREQ_MAX = 6000          # Lowpass filter (Hz)
APPLY_PHASE_SHIFT = True
APPLY_CMR = True
DETECT_BAD_CHANNELS = True

# Motion correction
CORRECT_MOTION = True
MOTION_PRESET = 'nonrigid_accurate'  # 'kilosort_like', 'nonrigid_fast_and_accurate'

# Spike sorting
SORTER = 'kilosort4'     # 'kilosort4', 'spykingcircus2', 'mountainsort5'
SORTER_PARAMS = {
    'batch_size': 30000,
    'nblocks': 1,        # Increase for long recordings with drift
}

# Quality metrics and curation
CURATION_METHOD = 'allen'  # 'allen', 'ibl', 'strict'

# Processing
N_JOBS = -1              # -1 = all cores

# =============================================================================
# ANALYSIS PIPELINE - Usually no need to modify below
# =============================================================================

from pathlib import Path
import json

import spikeinterface.full as si
from spikeinterface.exporters import export_to_phy


def main():
    """Run the full analysis pipeline."""

    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # 1. LOAD DATA
    # =========================================================================
    print("=" * 60)
    print("1. LOADING DATA")
    print("=" * 60)

    if DATA_FORMAT == 'spikeglx':
        recording = si.read_spikeglx(DATA_PATH, stream_name=STREAM_ID)
    elif DATA_FORMAT == 'openephys':
        recording = si.read_openephys(DATA_PATH)
    elif DATA_FORMAT == 'nwb':
        recording = si.read_nwb(DATA_PATH)
    else:
        raise ValueError(f"Unknown format: {DATA_FORMAT}")

    print(f"Recording: {recording.get_num_channels()} channels")
    print(f"Duration: {recording.get_total_duration():.1f} seconds")
    print(f"Sampling rate: {recording.get_sampling_frequency()} Hz")

    # =========================================================================
    # 2. PREPROCESSING
    # =========================================================================
    print("\n" + "=" * 60)
    print("2. PREPROCESSING")
    print("=" * 60)

    rec = recording

    # Bandpass filter
    print(f"Applying bandpass filter ({FREQ_MIN}-{FREQ_MAX} Hz)...")
    rec = si.bandpass_filter(rec, freq_min=FREQ_MIN, freq_max=FREQ_MAX)

    # Phase shift correction
    if APPLY_PHASE_SHIFT:
        print("Applying phase shift correction...")
        rec = si.phase_shift(rec)

    # Bad channel detection
    if DETECT_BAD_CHANNELS:
        print("Detecting bad channels...")
        bad_ids, _ = si.detect_bad_channels(rec)
        if len(bad_ids) > 0:
            print(f"  Removing {len(bad_ids)} bad channels")
            rec = rec.remove_channels(bad_ids)

    # Common median reference
    if APPLY_CMR:
        print("Applying common median reference...")
        rec = si.common_reference(rec, operator='median', reference='global')

    # Save preprocessed
    print("Saving preprocessed recording...")
    rec.save(folder=output_path / 'preprocessed', n_jobs=N_JOBS)

    # =========================================================================
    # 3. MOTION CORRECTION
    # =========================================================================
    if CORRECT_MOTION:
        print("\n" + "=" * 60)
        print("3. MOTION CORRECTION")
        print("=" * 60)

        print(f"Estimating and correcting motion (preset: {MOTION_PRESET})...")
        rec = si.correct_motion(
            rec,
            preset=MOTION_PRESET,
            folder=output_path / 'motion',
        )

    # =========================================================================
    # 4. SPIKE SORTING
    # =========================================================================
    print("\n" + "=" * 60)
    print("4. SPIKE SORTING")
    print("=" * 60)

    print(f"Running {SORTER}...")
    sorting = si.run_sorter(
        SORTER,
        rec,
        folder=output_path / f'{SORTER}_output',
        verbose=True,
        **SORTER_PARAMS,
    )

    print(f"Found {len(sorting.unit_ids)} units")

    # =========================================================================
    # 5. POSTPROCESSING
    # =========================================================================
    print("\n" + "=" * 60)
    print("5. POSTPROCESSING")
    print("=" * 60)

    print("Creating SortingAnalyzer...")
    analyzer = si.create_sorting_analyzer(
        sorting,
        rec,
        format='binary_folder',
        folder=output_path / 'analyzer',
        sparse=True,
    )

    print("Computing extensions...")
    analyzer.compute('random_spikes', max_spikes_per_unit=500)
    analyzer.compute('waveforms', ms_before=1.0, ms_after=2.0)
    analyzer.compute('templates', operators=['average', 'std'])
    analyzer.compute('noise_levels')
    analyzer.compute('spike_amplitudes')
    analyzer.compute('correlograms', window_ms=50.0, bin_ms=1.0)
    analyzer.compute('unit_locations', method='monopolar_triangulation')

    # =========================================================================
    # 6. QUALITY METRICS
    # =========================================================================
    print("\n" + "=" * 60)
    print("6. QUALITY METRICS")
    print("=" * 60)

    print("Computing quality metrics...")
    metrics = si.compute_quality_metrics(
        analyzer,
        metric_names=[
            'snr', 'isi_violations_ratio', 'presence_ratio',
            'amplitude_cutoff', 'firing_rate', 'amplitude_cv',
        ],
        n_jobs=N_JOBS,
    )

    metrics.to_csv(output_path / 'quality_metrics.csv')
    print(f"Saved metrics to: {output_path / 'quality_metrics.csv'}")

    # Print summary
    print("\nMetrics summary:")
    for col in ['snr', 'isi_violations_ratio', 'presence_ratio', 'firing_rate']:
        if col in metrics.columns:
            print(f"  {col}: {metrics[col].median():.4f} (median)")

    # =========================================================================
    # 7. CURATION
    # =========================================================================
    print("\n" + "=" * 60)
    print("7. CURATION")
    print("=" * 60)

    # Curation criteria
    criteria = {
        'allen': {'snr': 3.0, 'isi_violations_ratio': 0.1, 'presence_ratio': 0.9},
        'ibl': {'snr': 4.0, 'isi_violations_ratio': 0.5, 'presence_ratio': 0.5},
        'strict': {'snr': 5.0, 'isi_violations_ratio': 0.01, 'presence_ratio': 0.95},
    }[CURATION_METHOD]

    print(f"Applying {CURATION_METHOD} criteria: {criteria}")

    labels = {}
    for unit_id in metrics.index:
        row = metrics.loc[unit_id]
        is_good = (
            row.get('snr', 0) >= criteria['snr'] and
            row.get('isi_violations_ratio', 1) <= criteria['isi_violations_ratio'] and
            row.get('presence_ratio', 0) >= criteria['presence_ratio']
        )
        if is_good:
            labels[int(unit_id)] = 'good'
        elif row.get('snr', 0) < 2:
            labels[int(unit_id)] = 'noise'
        else:
            labels[int(unit_id)] = 'mua'

    # Save labels
    with open(output_path / 'curation_labels.json', 'w') as f:
        json.dump(labels, f, indent=2)

    # Count
    good_count = sum(1 for v in labels.values() if v == 'good')
    mua_count = sum(1 for v in labels.values() if v == 'mua')
    noise_count = sum(1 for v in labels.values() if v == 'noise')

    print(f"\nCuration results:")
    print(f"  Good: {good_count}")
    print(f"  MUA: {mua_count}")
    print(f"  Noise: {noise_count}")
    print(f"  Total: {len(labels)}")

    # =========================================================================
    # 8. EXPORT
    # =========================================================================
    print("\n" + "=" * 60)
    print("8. EXPORT")
    print("=" * 60)

    print("Exporting to Phy...")
    export_to_phy(
        analyzer,
        output_folder=output_path / 'phy_export',
        copy_binary=True,
    )

    print(f"\nAnalysis complete!")
    print(f"Results saved to: {output_path}")
    print(f"\nTo open in Phy:")
    print(f"  phy template-gui {output_path / 'phy_export' / 'params.py'}")


if __name__ == '__main__':
    main()
```
