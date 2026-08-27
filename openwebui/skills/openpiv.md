---
name: openpiv
description: Particle Image Velocimetry (PIV) analysis with OpenPIV. Use when extracting velocity fields from PIV image pairs, analyzing fluid dynamics or flow visualization experiments, cross-correlating interrogation windows, validating and replacing spurious PIV vectors, or computing vorticity, strain rate, and turbulence statistics from measured velocity fields.
---

# OpenPIV

## Overview

OpenPIV (Open Particle Image Velocimetry) analyzes fluid flow from PIV image pairs. It covers
preprocessing, cross-correlation, vector validation, outlier replacement, smoothing, and scaling to
physical units.

Everything below is verified against **openpiv 0.25.4**. The API moves between releases — check
`inspect.signature()` before trusting a snippet against a different version.

## When to use

Use this skill when working with experimental PIV or flow-visualization image pairs: measuring 2D
velocity fields, tuning interrogation-window parameters, validating vectors, or deriving vorticity,
strain rate, and turbulence statistics. For *simulating* flow rather than measuring it, use a CFD
skill instead.

## Quick Start

Install OpenPIV:

```bash
uv pip install openpiv

# Pin it when the analysis needs to be reproducible -- this is the version every
# snippet below was checked against.
uv pip install "openpiv==0.25.4"
```

Run PIV analysis on an image pair:

```python
import numpy as np
from openpiv import tools, pyprocess, validation, filters, scaling

frame_a = tools.imread("image_a.bmp")
frame_b = tools.imread("image_b.bmp")

# Cross-correlate. Returns (u, v, s2n) whenever sig2noise_method is not None.
u, v, s2n = pyprocess.extended_search_area_piv(
    frame_a.astype(np.int32),
    frame_b.astype(np.int32),
    window_size=32,
    overlap=12,
    dt=0.02,
    search_area_size=38,
    correlation_method="linear",   # required for search_area_size > window_size
    sig2noise_method="peak2peak",
)

x, y = pyprocess.get_coordinates(
    image_size=frame_a.shape,
    search_area_size=38,
    overlap=12,
)

# flags is a boolean array: True marks a spurious vector.
flags = validation.sig2noise_val(s2n, threshold=1.05)
u, v = filters.replace_outliers(u, v, flags, method="localmean", max_iter=3, kernel_size=2)

# Scale to physical units, then flip to image coordinates for plotting.
x, y, u, v = scaling.uniform(x, y, u, v, scaling_factor=96.52)
x, y, u, v = tools.transform_coordinates(x, y, u, v)

tools.save("vectors.txt", x, y, u, v, flags)
```

Or use the bundled CLI, which wraps exactly that pipeline:

```bash
python skills/openpiv/scripts/runner.py \
    --image frame_a.bmp --image frame_b.bmp --output_dir results --verbose
```

## Core Concepts

### PIV Fundamentals

Particle Image Velocimetry is an optical method for measuring fluid velocity by tracking illuminated
tracer particles between two images.

**Process flow:**

1. Capture an image pair (`frame_a`, `frame_b`) separated by a known time `dt`.
2. Divide the images into interrogation windows.
3. Cross-correlate matching windows to find peak displacement.
4. Validate vectors (signal-to-noise, global range, local median).
5. Replace spurious vectors with interpolated values.
6. Scale pixel displacements to physical units.

### Interrogation Window Parameters

**`window_size`** — correlation window in pixels (typically 16–128). Larger windows give better
correlation but coarser spatial resolution.

**`overlap`** — pixels shared between adjacent windows (typically 50–75% of `window_size`). Higher
overlap raises vector density and cost, but adjacent vectors become correlated rather than
independent.

**`search_area_size`** — the window searched in the second frame. Must be ≥ `window_size`; a few
pixels larger accommodates larger displacements. Pair an extended search area with
`correlation_method="linear"` — the default `"circular"` relies on FFT wrap-around and aliases large
displacements into small ones. See `references/advanced_algorithms.md`.

Rules of thumb: keep the largest displacement under about a quarter of `window_size`, and aim for
5–10 particles per window.

### Signal-to-Noise Ratio

`s2n` measures how distinct the correlation peak is. `sig2noise_method` controls how it is computed —
`"peak2mean"` (the function default) or `"peak2peak"`. **The two are on different scales**, so a
threshold tuned for one is meaningless for the other. Typical `peak2peak` thresholds are 1.05–1.3.

```python
flags = validation.sig2noise_val(s2n, threshold=1.05)
# flags is bool: True == spurious. `~flags` selects the good vectors.
```

## Common Operations

### Dynamic Masking

Masking lives in `openpiv.preprocess`, **not** in an `openpiv.masking` module. It returns an
`(image, mask)` tuple and expects a float image.

```python
from openpiv import preprocess

# method="edges" for dark, sharp-edged objects; "intensity" for high-contrast objects.
frame_a_masked, mask_a = preprocess.dynamic_masking(
    frame_a.astype(np.float64), method="intensity", filter_size=7, threshold=0.005
)
frame_b_masked, mask_b = preprocess.dynamic_masking(
    frame_b.astype(np.float64), method="intensity", filter_size=7, threshold=0.005
)
```

Feed the **returned image** into the correlation step — it already has the masked region zeroed. Do
not multiply the original frame by `mask`: masking is already applied, and for `method="edges"` the
mask comes back as `uint8` 0/255 rather than boolean, so multiplying rescales the image by 255.

### Multi-Pass Processing

Multi-pass (window deformation) lives in `openpiv.windef`, driven by a `PIVSettings` dataclass.
`pyprocess` has no multi-pass entry point.

```python
import numpy as np
from openpiv import scaling, windef

settings = windef.PIVSettings()
settings.windowsizes = (64, 32, 16)   # one entry per pass, decreasing (this is also the default)
settings.overlap = (32, 16, 8)        # same length as windowsizes
settings.num_iterations = 3           # number of passes to actually run
settings.sig2noise_threshold = 1.05

x, y, u, v, flags = windef.simple_multipass(
    frame_a.astype(np.int32), frame_b.astype(np.int32), settings
)

# Output is in PIXELS PER FRAME -- convert yourself. scaling.uniform only divides
# by scaling_factor, so apply dt separately.
dt = 0.02
x, y, u, v = scaling.uniform(x, y, u, v, scaling_factor=96.52)
u, v = u / dt, v / dt
```

`simple_multipass` already validates, replaces outliers, fills remaining NaNs with zeros, and calls
`transform_coordinates` — do not repeat those steps.

**Units trap:** `PIVSettings` has `dt` and `scaling_factor` fields, but `windef` never uses either —
`first_pass` calls `extended_search_area_piv` without `dt`, so the whole multi-pass chain works in
pixels per frame. Setting `settings.dt = 0.02` changes nothing about the returned values. Convert
after the fact, as above.

For control over individual passes, `windef.first_pass` and `windef.multipass_img_deform` are the
lower-level building blocks.

## Validation and Post-Processing

### Validation Methods

Every validator returns a boolean array where **True marks a spurious vector**.

```python
# Signal-to-noise
flags = validation.sig2noise_val(s2n, threshold=1.05)

# Global range -- takes (min, max) TUPLES, positionally or as u_thresholds/v_thresholds.
flags = validation.global_val(u, v, (-300, 300), (-300, 300))

# Local median -- u_threshold and v_threshold are REQUIRED; size is the neighbourhood half-width.
flags = validation.local_median_val(u, v, u_threshold=30.0, v_threshold=30.0, size=1)

# Combine with boolean OR (not np.maximum -- these are bool arrays).
flags = (
    validation.sig2noise_val(s2n, threshold=1.05)
    | validation.global_val(u, v, (-300, 300), (-300, 300))
    | validation.local_median_val(u, v, u_threshold=30.0, v_threshold=30.0)
)
```

**Set these thresholds in the units of `u` and `v`, not in pixels per frame.**
`extended_search_area_piv` divides by `dt`, so with `dt=0.02` a 3 px/frame displacement arrives as
150 px/s. The thresholds above suit that case; the `(-30, 30)` figure that PIV literature and
`PIVSettings.min_max_u_disp` use is a px/frame limit, and applying it to px/s output rejects the
entire field. Either validate before scaling, or scale the thresholds by `1/dt` too.

### Outlier Replacement

```python
u, v = filters.replace_outliers(
    u, v, flags, method="localmean", max_iter=3, tol=1e-3, kernel_size=2
)
```

`method` accepts `"localmean"`, `"disk"`, or `"distance"` — and only those three. An unrecognized
name is not rejected; it falls through to an all-zero kernel and silently returns a useless field.
Note that replacement *fills* the flagged
positions with interpolated values — if you then overwrite them with NaN, the replacement was
wasted. Choose one or the other:

```python
# Keep flagged vectors out of the analysis entirely, instead of interpolating them.
u = np.where(flags, np.nan, u)
v = np.where(flags, np.nan, v)
```

### Smoothing

Smoothing is `openpiv.smoothn.smoothn`; there is no `openpiv.smooth` module. It returns a tuple
whose first element is the smoothed field, and it does not accept NaN input.

```python
from openpiv.smoothn import smoothn

u_smooth, *_ = smoothn(np.nan_to_num(u), s=0.5)  # s: larger == smoother
v_smooth, *_ = smoothn(np.nan_to_num(v), s=0.5)
u_smooth = np.asarray(u_smooth)
```

## Visualization

### Vector Field Plotting

`display_vector_field` reads a saved vectors file and calls `plt.show()` internally, so select a
non-interactive backend for batch runs.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpiv import tools

fig, ax = plt.subplots(figsize=(8, 8))
tools.display_vector_field(
    "vectors.txt",
    ax=ax,
    scaling_factor=96.52,   # same factor used in scaling.uniform, to map back onto the image
    scale=50,
    width=0.0035,
    on_img=True,
    image_name="frame_a.bmp",
)
fig.savefig("vector_field.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

### Custom Visualization

```python
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

mag = np.sqrt(u**2 + v**2)
for ax, field, title, cmap in [
    (axes[0], mag, "Velocity Magnitude", "viridis"),
    (axes[1], u, "U Velocity", "RdBu_r"),
    (axes[2], v, "V Velocity", "RdBu_r"),
]:
    im = ax.imshow(field, cmap=cmap)
    ax.set_title(title)
    plt.colorbar(im, ax=ax)

fig.tight_layout()
fig.savefig("velocity_components.png")
plt.close(fig)
```

## Analysis Functions

`scripts/analyze.py` bundles these against a `params.npz` written by `runner.py`. It infers the
physical grid spacing from the saved coordinates, so the derivatives come out per unit length:

```python
import sys
sys.path.insert(0, "skills/openpiv/scripts")
from analyze import PIVAnalyzer

piv = PIVAnalyzer("results/params.npz")
vorticity = piv.compute_vorticity()          # dv/dx - du/dy
exx, eyy, exy = piv.compute_strain()
stats = piv.compute_statistics()             # u_mean, v_mean, rms_u, rms_v, tke
piv.plot_vector_field(save_path="quiver.png")
```

The standalone forms, if you would rather compute them inline:

### Vorticity

```python
def compute_vorticity(u, v, dx=1.0, dy=None):
    """Out-of-plane vorticity dv/dx - du/dy. Pass the physical grid spacing, not 1.0."""
    dy = dx if dy is None else dy
    return np.gradient(v, dx, axis=1) - np.gradient(u, dy, axis=0)
```

The grid spacing is `(window_size - overlap) / scaling_factor` in physical units, so leaving `dx=1.0`
yields vorticity per grid cell, not per unit length.

**Sign convention:** `runner.py` ends with `transform_coordinates`, which relabels the grid into a
right-handed y-up frame but leaves the rows in image order, so the saved `y` *decreases* as the row
index grows. The standalone forms above assume the opposite, so on a `params.npz` field they return
`-du/dy` and flip the sign of the vorticity and the shear strain — negate the `axis=0` derivatives, or
use `PIVAnalyzer`, which reads the orientation off the saved coordinates.

### Strain Rate

```python
def compute_strain(u, v, dx=1.0, dy=None):
    """Return (exx, eyy, exy) of the 2D strain-rate tensor."""
    dy = dx if dy is None else dy
    du_dx = np.gradient(u, dx, axis=1)
    du_dy = np.gradient(u, dy, axis=0)
    dv_dx = np.gradient(v, dx, axis=1)
    dv_dy = np.gradient(v, dy, axis=0)
    return du_dx, dv_dy, 0.5 * (du_dy + dv_dx)
```

### Turbulence Statistics

```python
def compute_statistics(u, v):
    """Single-frame spatial statistics. NOT Reynolds decomposition."""
    u_prime = u - np.nanmean(u)
    v_prime = v - np.nanmean(v)
    rms_u, rms_v = np.nanstd(u_prime), np.nanstd(v_prime)
    return {
        "u_mean": np.nanmean(u),
        "v_mean": np.nanmean(v),
        "rms_u": rms_u,
        "rms_v": rms_v,
        "tke": 0.5 * (rms_u**2 + rms_v**2),
    }
```

**Caveat:** subtracting the *spatial* mean of one frame measures spatial variance, which equals
turbulent intensity only for a homogeneous field. Genuine Reynolds decomposition needs an ensemble of
image pairs: average over the time axis, then subtract that mean field from each realization.

## CLI Usage

```bash
# Basic run
python skills/openpiv/scripts/runner.py \
    --image img1.bmp --image img2.bmp --output_dir results --verbose

# Tuned parameters with dynamic masking
python skills/openpiv/scripts/runner.py \
    --image frame_a.bmp \
    --image frame_b.bmp \
    --output_dir results \
    --window_size 32 \
    --overlap 12 \
    --search_area 38 \
    --dt 0.02 \
    --scaling 96.52 \
    --threshold 1.05 \
    --mask dynamic \
    --mask_method intensity \
    --verbose
```

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--image` | required | Image file; specify exactly twice for the pair |
| `--output_dir` | `results` | Output directory (created if absent) |
| `--window_size` | 32 | Interrogation window size (px) |
| `--overlap` | 12 | Window overlap (px) |
| `--search_area` | 38 | Search area size (px), must be ≥ `--window_size` |
| `--dt` | 0.02 | Time between frames (s) |
| `--scaling` | 96.52 | Scaling factor, pixels per physical unit (e.g. px/mm) |
| `--threshold` | 1.05 | `peak2peak` signal-to-noise threshold |
| `--mask` | `none` | `none` or `dynamic` (`openpiv.preprocess.dynamic_masking`) |
| `--mask_method` | `intensity` | `edges` or `intensity`, used only with `--mask dynamic` |
| `--drop_invalid` | off | NaN out flagged vectors instead of keeping interpolated values |
| `--verbose` | off | Print progress messages |

Verify an install end to end against OpenPIV's own bundled image pair:

```bash
python skills/openpiv/scripts/run_example.py --output_dir /tmp/openpiv-demo
```

## Output Files

- **vectors.txt** — tab-delimited, `%.4e` formatted, with a `# x y u v flags mask` comment header
- **params.npz** — NumPy archive with `x`, `y`, `u`, `v`, `flags` arrays
- **vector_field.png** — vector field drawn over the first frame

```text
# x	y	u	v	flags	mask
2.1757e-01	3.5226e+00	-6.2220e-02	-2.7081e+00	0.0000e+00	0.0000e+00
4.8695e-01	3.5226e+00	-3.1587e-01	-2.9800e+00	0.0000e+00	0.0000e+00
```

`flags` is written as a float, `0` for a valid vector and `1` for a flagged one.

## Best Practices

### Parameter Selection

1. **Window size** — 32×32 suits most cases. 64/128 for better correlation at coarser resolution;
   16/24 for finer resolution at the cost of noise.
2. **Overlap** — 50–75% of window size.
3. **Threshold** — raise it to reject more vectors; always re-tune after switching
   `sig2noise_method`.
4. **Scaling factor** — calibrate against a known reference such as a calibration grid, and keep the
   units straight (`96.52` in OpenPIV's `test1` tutorial data is px/mm).

### Image Quality

- Particles visible and evenly distributed, 5–10 per interrogation window
- No saturated or overexposed regions
- Minimal background noise; consider background subtraction across a run

### Processing Tips

1. Start from the defaults, then tune against the vector field you get.
2. Inspect the `s2n` distribution — a low median means poor correlation, not a bad threshold.
3. Visualize early; obvious problems (uniform vectors, edge artifacts) show up immediately.
4. Use multi-pass (`windef`) for flows with large velocity gradients or displacements.
5. Mask reflections and solid boundaries rather than letting them generate vectors.

## Resources

### references/

- `advanced_algorithms.md` — correlation and subpixel methods, multi-pass window deformation,
  `PIVSettings` fields, 3D and phase-separation modules

Load the reference when detailed algorithm or settings information is needed.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/openpiv/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/advanced_algorithms.md`

# Advanced OpenPIV Algorithms and Settings

Everything here is checked against **openpiv 0.25.4**. Confirm with `inspect.signature()` against
other releases — names and defaults have moved between versions.

## Correlation methods

`pyprocess.extended_search_area_piv(..., correlation_method=...)`:

| Value | Behaviour |
|-------|-----------|
| `"circular"` (default) | FFT correlation with no zero-padding. Fastest and lowest memory. Wrap-around means a displacement past half the window aliases back as a small one in the opposite direction. |
| `"linear"` | FFT correlation zero-padded to `2*window_size`. No wrap-around, so large displacements survive, at roughly 2–4× the cost. |

**Only those two exist in 0.25.4.** `"direct"` appears in the docstrings but the branch is missing —
it prints `correlation method direct is not implemented` and then raises
`UnboundLocalError: cannot access local variable 'corr'`. Do not offer it as an option.

Use `"linear"` whenever `search_area_size > window_size`. `"circular"` accepts an extended search
area without complaining but keeps relying on wrap-around, and on OpenPIV's own `test1` pair at
`window_size=32, search_area_size=38` it produced a peak |u| of 255 px/s against 87 px/s for
`"linear"` — the difference is aliased vectors, not physics.

`normalized_correlation=True` normalizes intensities per window before correlating, making peak
heights comparable across windows of differing brightness — useful under uneven illumination. It also
shifts the `s2n` scale, so re-tune the threshold after switching it on.

`use_vectorized=True` swaps the per-window loop for the batched
`vectorized_correlation_to_displacements` path. Same results, faster on large fields, higher peak
memory since all correlation maps exist at once.

## Subpixel peak fitting

`subpixel_method` selects how the integer correlation peak is refined:

| Value | Notes |
|-------|-------|
| `"gaussian"` (default) | Three-point Gaussian fit per axis. Standard choice; biased toward integer values ("peak locking") when particle images are under 2 px. |
| `"parabolic"` | Three-point parabolic fit. Cheaper, slightly less accurate for Gaussian particle images. |
| `"centroid"` | Intensity-weighted centroid. More robust for wide or saturated peaks. |

Peak locking is a particle-imaging problem, not a fitting problem: aim for 2–3 px particle image
diameter rather than switching estimators.

## Signal-to-noise measures

`pyprocess.sig2noise_ratio(correlation, sig2noise_method="peak2peak", width=2)`:

- `"peak2mean"` — first peak divided by the mean of the correlation map. This is the default of both
  `extended_search_area_piv` and `PIVSettings`. Values run higher and depend on map size.
- `"peak2peak"` — first peak divided by the second-highest peak, excluding a `width`-pixel
  neighbourhood around the first. The classic PIV detectability ratio; usable thresholds are
  ~1.05–1.3.

The two scales are not interchangeable. A threshold copied from one to the other silently rejects
everything or nothing.

## Multi-pass window deformation (`openpiv.windef`)

`windef.simple_multipass(frame_a, frame_b, settings)` runs the full loop:

1. `windef.first_pass` — coarse correlation on `windowsizes[0]`.
2. `validation.typical_validation` — applies every enabled check in `settings` at once.
3. `filters.replace_outliers` — fills flagged vectors.
4. `windef.multipass_img_deform` for iterations `1 .. num_iterations-1` — deforms the interrogation
   windows using the previous pass as a predictor, then re-correlates on the next smaller window.
5. Remaining NaNs filled with zeros; `transform_coordinates` applied.

It returns `(x, y, u, v, flags)` in **pixels per frame**. `settings.dt` and
`settings.scaling_factor` exist on the dataclass but the `windef` chain applies neither —
`first_pass` calls `extended_search_area_piv` without passing `dt`. Convert afterwards:

```python
x, y, u, v = scaling.uniform(x, y, u, v, scaling_factor=96.52)
u, v = u / dt, v / dt      # scaling.uniform does not divide by dt
```

The upside of working in px/frame is that the validation defaults (`min_max_u_disp=(-30, 30)`,
`median_threshold=3`) are stated in px/frame and therefore mean what the PIV literature says they
mean. The same numbers applied to `extended_search_area_piv` output, which *has* been divided by
`dt`, would reject the whole field.

`deformation_method="symmetric"` (the default) deforms both frames toward the midpoint, which halves
the interpolation bias of deforming only the second frame. `interpolation_order` (default 3) is the
spline order used for that deformation.

Window deformation is what makes multi-pass worth the cost: it handles velocity gradients within a
window, which a fixed-window single pass cannot.

## `PIVSettings` reference

`windef.PIVSettings()` is a dataclass; set attributes on an instance.

**Input and region**

| Field | Default | Meaning |
|-------|---------|---------|
| `filepath_images`, `save_path`, `frame_pattern_a`, `frame_pattern_b` | OpenPIV's bundled `data/test1` | Batch-mode paths; irrelevant when calling `simple_multipass` with arrays |
| `roi` | `"full"` | `"full"` or `(y1, y2, x1, x2)` crop |
| `invert` | `False` | Invert intensities, for dark particles on a bright background |

**Masking**

| Field | Default | Meaning |
|-------|---------|---------|
| `dynamic_masking_method` | `None` | `None`, `"edges"`, or `"intensity"` |
| `dynamic_masking_threshold` | `0.005` | Edge-strength threshold for `"edges"` |
| `dynamic_masking_filter_size` | `7` | Gaussian/median filter size in px |
| `static_mask` | `None` | Boolean array marking permanently excluded pixels |

**Correlation**

| Field | Default |
|-------|---------|
| `correlation_method` | `"circular"` (or `"linear"`) |
| `normalized_correlation` | `False` |
| `windowsizes` | `(64, 32, 16)` |
| `overlap` | `(32, 16, 8)` |
| `num_iterations` | `3` |
| `subpixel_method` | `"gaussian"` |
| `use_vectorized` | `False` |
| `deformation_method` | `"symmetric"` |
| `interpolation_order` | `3` |

`windowsizes` and `overlap` must be at least `num_iterations` long — each pass reads its own entry.

**Scaling**

| Field | Default | Meaning |
|-------|---------|---------|
| `dt` | `1.0` | Seconds between frames — **ignored by the `windef` chain** |
| `scaling_factor` | `1.0` | Pixels per physical unit — **ignored by the `windef` chain** |

**Validation** — all consumed by `validation.typical_validation`

| Field | Default | Meaning |
|-------|---------|---------|
| `sig2noise_method` | `"peak2mean"` | See above |
| `sig2noise_mask` | `2` | `width` around the first peak for `"peak2peak"` |
| `sig2noise_threshold` | `1.0` | Reject below this |
| `sig2noise_validate` | `True` | Enable the s2n check |
| `validation_first_pass` | `True` | Also validate the coarse pass |
| `min_max_u_disp`, `min_max_v_disp` | `(-30, 30)` | Global range in px/frame |
| `std_threshold` | `10` | Reject beyond N standard deviations |
| `median_threshold` | `3` | Local-median residual threshold |
| `median_size` | `1` | Neighbourhood half-width for the median test |
| `median_normalized` | `False` | Normalize the median residual by local fluctuation |

**Replacement and smoothing**

| Field | Default | Meaning |
|-------|---------|---------|
| `replace_vectors` | `True` | Run `replace_outliers` after validation |
| `filter_method` | `"localmean"` | `"localmean"`, `"disk"`, or `"distance"` |
| `max_filter_iteration` | `4` | Inpainting iterations |
| `filter_kernel_size` | `2` | Inpainting kernel size |
| `smoothn` | `False` | Apply `smoothn` between passes |
| `smoothn_p` | `0.05` | Smoothing strength when enabled |

Smoothing between passes stabilizes the predictor for the next pass. It also propagates smoothing
into the final result, so report it as part of the processing chain.

**Output**

| Field | Default |
|-------|---------|
| `save_plot`, `show_plot`, `show_all_plots` | `False` |
| `scale_plot` | `100` |
| `fmt` | `"%.4e"` |

## Volumetric PIV (`openpiv.pyprocess3D`)

```python
from openpiv import pyprocess3D

u, v, w, s2n = pyprocess3D.extended_search_area_piv3D(
    vol_a, vol_b,
    window_size=(32, 32, 32),
    overlap=(16, 16, 16),
    dt=(1.0, 1.0, 1.0),
    search_area_size=(38, 38, 38),
    correlation_method="fft",       # note: "fft" here, not the 2D "circular"/"linear"
    subpixel_method="gaussian",
    sig2noise_method="peak2peak",
)

# Note the extra window_size argument -- this signature differs from pyprocess.get_coordinates.
x, y, z = pyprocess3D.get_coordinates(
    vol_a.shape, search_area_size=(38, 38, 38), window_size=(32, 32, 32), overlap=(16, 16, 16)
)
```

Inputs are 3D intensity volumes — this module correlates reconstructed volumes; it does not perform
the tomographic reconstruction itself. `dt` is a per-axis tuple. Memory scales with the cube of
window size, so 32³ windows on a large volume are already demanding.

## Phase separation (`openpiv.phase_separation`)

For two-phase flows where large particles (droplets, bubbles) must be separated from tracers before
correlation:

```python
from openpiv import phase_separation

big, small = phase_separation.khalitov_longmire(
    image,
    big_particles_criteria={"min_size": 20, "min_brightness": 30},
    small_particles_criteria={"max_size": 20, "min_brightness": 5},
    blur_kernel_size=1,
    I_sat=230,
)
```

Criteria dicts accept `min_size`, `max_size`, `min_brightness`, and `max_brightness`. `min_size` is
mandatory for the big-particle dict and `max_size` for the small-particle dict; unrecognized keys are
ignored silently, so check spelling.

Also available: `median_filter_method(image, kernel_size)` (Kiger & Pan) and
`opening_method(image, kernel_size, iterations=1, thresh_factor=1.1)` for simpler size-based
separation. Run PIV separately on each returned phase — tracer statistics computed on an unseparated
image are contaminated by the dispersed phase.

## Choosing an approach

| Situation | Approach |
|-----------|----------|
| Small displacements, uniform flow | `extended_search_area_piv`, `correlation_method="circular"` |
| Displacements above ~1/4 window | `search_area_size > window_size` with `correlation_method="linear"` |
| Strong velocity gradients, shear layers | `windef.simple_multipass` with decreasing `windowsizes` |
| Uneven illumination | `normalized_correlation=True`, plus background subtraction |
| Solid bodies, reflections, free surfaces | `preprocess.dynamic_masking` or a `static_mask` |
| Two-phase flow | `phase_separation` first, then PIV per phase |
| Volumetric data | `pyprocess3D.extended_search_area_piv3D` |

### `scripts/__init__.py`

```python
"""OpenPIV skill scripts."""
```

### `scripts/analyze.py`

```python
"""Post-processing helpers for a params.npz written by runner.py.

Verified against openpiv 0.25.4. Pure numpy -- no OpenPIV import needed here.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np


class PIVAnalyzer:
    """Derived quantities from a saved PIV velocity field.

    The fields in params.npz are already scaled to physical units by runner.py, so
    x and y are in the same unit as the scaling factor and u and v are that unit per
    second. Pass the matching grid spacing to the gradient methods -- the default
    dx=1.0 yields per-grid-cell derivatives, not per-unit-length ones.
    """

    def __init__(self, params_file: str):
        self.params_file = Path(params_file)

        data = np.load(self.params_file)
        self.x = data["x"]
        self.y = data["y"]
        self.u = data["u"]
        self.v = data["v"]
        # Boolean: True marks a vector flagged as spurious during processing.
        self.flags = data["flags"].astype(bool)

    @property
    def grid_spacing(self) -> Tuple[float, float]:
        """(dx, dy) inferred from the coordinate arrays, in physical units."""
        dx = float(np.abs(np.diff(self.x, axis=1)).mean()) if self.x.shape[1] > 1 else 1.0
        dy = float(np.abs(np.diff(self.y, axis=0)).mean()) if self.y.shape[0] > 1 else 1.0
        return dx, dy

    @property
    def axis_signs(self) -> Tuple[float, float]:
        """(+-1, +-1): whether x and y increase or decrease along the array axes.

        runner.py finishes with openpiv.tools.transform_coordinates(), which relabels
        the grid into a physical right-handed (y-up) frame while leaving the rows in
        image order -- so physical y *decreases* as the row index grows. np.gradient
        only sees the array, so differentiating with a positive spacing would return
        -du/dy there and silently flip the sign of the vorticity and of the shear
        strain rate. These signs put the derivatives back on the physical axes.
        """
        x_sign = -1.0 if self.x.shape[1] > 1 and self.x[0, 1] < self.x[0, 0] else 1.0
        y_sign = -1.0 if self.y.shape[0] > 1 and self.y[1, 0] < self.y[0, 0] else 1.0
        return x_sign, y_sign

    def _steps(
        self, dx: Optional[float], dy: Optional[float]
    ) -> Tuple[float, float, float, float]:
        """(dx, dy, x_sign, y_sign) for a gradient call, defaulting to the grid."""
        gx, gy = self.grid_spacing
        x_sign, y_sign = self.axis_signs
        return (
            gx if dx is None else abs(float(dx)),
            gy if dy is None else abs(float(dy)),
            x_sign,
            y_sign,
        )

    def plot_vector_field(
        self,
        scale: int = 50,
        width: float = 0.0035,
        save_path: Optional[str] = None,
    ):
        """Quiver plot of the valid vectors. Saves to save_path, or shows interactively."""
        import matplotlib.pyplot as plt

        valid = ~self.flags
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.quiver(
            self.x[valid],
            self.y[valid],
            self.u[valid],
            self.v[valid],
            scale=scale,
            width=width,
        )
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title("Velocity Field")
        ax.set_aspect("equal")
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches="tight")
            plt.close(fig)
        else:
            plt.show()
        return fig

    def get_velocity_magnitude(self) -> np.ndarray:
        return np.sqrt(self.u**2 + self.v**2)

    def compute_vorticity(
        self, dx: Optional[float] = None, dy: Optional[float] = None
    ) -> np.ndarray:
        """Out-of-plane vorticity, dv/dx - du/dy. Defaults to the inferred grid spacing.

        dx and dy are spacing magnitudes; the axis orientation comes from the saved
        coordinates (see axis_signs), so a counter-clockwise flow gives positive
        vorticity whichever way the rows run.
        """
        dx, dy, x_sign, y_sign = self._steps(dx, dy)
        dv_dx = x_sign * np.gradient(self.v, dx, axis=1)
        du_dy = y_sign * np.gradient(self.u, dy, axis=0)
        return dv_dx - du_dy

    def compute_strain(
        self, dx: Optional[float] = None, dy: Optional[float] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return (exx, eyy, exy) of the 2D strain-rate tensor."""
        dx, dy, x_sign, y_sign = self._steps(dx, dy)
        du_dx = x_sign * np.gradient(self.u, dx, axis=1)
        du_dy = y_sign * np.gradient(self.u, dy, axis=0)
        dv_dx = x_sign * np.gradient(self.v, dx, axis=1)
        dv_dy = y_sign * np.gradient(self.v, dy, axis=0)
        return du_dx, dv_dy, 0.5 * (du_dy + dv_dx)

    def compute_statistics(self) -> Dict[str, float]:
        """Spatial mean and RMS over this single frame.

        This is NOT Reynolds decomposition: subtracting one frame's spatial mean
        measures spatial variance, which equals turbulent intensity only for a
        homogeneous field. True turbulence statistics need an ensemble of pairs --
        average over the time axis, then subtract that mean field from each frame.
        """
        u_prime = self.u - np.nanmean(self.u)
        v_prime = self.v - np.nanmean(self.v)
        rms_u = float(np.nanstd(u_prime))
        rms_v = float(np.nanstd(v_prime))
        return {
            "u_mean": float(np.nanmean(self.u)),
            "v_mean": float(np.nanmean(self.v)),
            "rms_u": rms_u,
            "rms_v": rms_v,
            "tke": 0.5 * (rms_u**2 + rms_v**2),
        }
```

### `scripts/run_example.py`

```python
"""End-to-end smoke test of the OpenPIV pipeline on OpenPIV's own bundled data.

Runs the full runner.py pipeline against the exp1_001 image pair that ships inside the
openpiv package, so it needs no external files. Use it to confirm an install works
before pointing the CLI at real experiment data.

    python skills/openpiv/scripts/run_example.py --output_dir /tmp/openpiv-demo
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyze import PIVAnalyzer  # noqa: E402
from runner import run_openpiv  # noqa: E402


def bundled_image_pair() -> tuple[Path, Path]:
    """Locate the exp1_001 pair inside the installed openpiv package."""
    import openpiv

    data_dir = Path(openpiv.__file__).parent / "data" / "test1"
    frame_a = data_dir / "exp1_001_a.bmp"
    frame_b = data_dir / "exp1_001_b.bmp"
    if not frame_a.exists() or not frame_b.exists():
        raise FileNotFoundError(
            f"OpenPIV's bundled test1 images are missing from {data_dir}. "
            "Pass your own image pair to runner.py instead."
        )
    return frame_a, frame_b


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output_dir", default="openpiv-example")
    parser.add_argument("--window_size", type=int, default=32)
    parser.add_argument("--overlap", type=int, default=12)
    parser.add_argument("--search_area", type=int, default=38)
    args = parser.parse_args()

    frame_a, frame_b = bundled_image_pair()
    print(f"Using bundled pair: {frame_a.name}, {frame_b.name}")

    # dt and scaling here are the values from OpenPIV's own test1 tutorial (px/mm).
    output_path = run_openpiv(
        image1=str(frame_a),
        image2=str(frame_b),
        output_dir=args.output_dir,
        window_size=args.window_size,
        overlap=args.overlap,
        search_area=args.search_area,
        dt=0.02,
        scaling_factor=96.52,
        threshold=1.05,
        verbose=True,
    )

    analyzer = PIVAnalyzer(output_path / "params.npz")
    dx, dy = analyzer.grid_spacing
    stats = analyzer.compute_statistics()
    vorticity = analyzer.compute_vorticity()

    print(f"\nField shape: {analyzer.u.shape}")
    print(f"Grid spacing: dx={dx:.4f}, dy={dy:.4f} (physical units)")
    print(f"Flagged vectors: {int(analyzer.flags.sum())}/{analyzer.flags.size}")
    print(f"Mean velocity: u={stats['u_mean']:.4f}, v={stats['v_mean']:.4f}")
    print(f"RMS: u={stats['rms_u']:.4f}, v={stats['rms_v']:.4f}, tke={stats['tke']:.4f}")
    print(f"Vorticity range: {vorticity.min():.4f} to {vorticity.max():.4f}")

    analyzer.plot_vector_field(save_path=str(output_path / "quiver.png"))
    print(f"\nWrote quiver.png alongside runner.py's output in {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/runner.py`

```python
"""CLI for OpenPIV processing of a single image pair.

Verified against openpiv 0.25.4. Writes vectors.txt, params.npz, and vector_field.png
into the output directory.
"""

import argparse
import warnings
from pathlib import Path

import matplotlib

# openpiv.tools.display_vector_field() calls plt.show() internally, so pick a
# non-interactive backend before pyplot is imported anywhere.
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from openpiv import filters, preprocess, pyprocess, scaling, tools, validation  # noqa: E402


def run_openpiv(
    image1: str,
    image2: str,
    output_dir: str = "results",
    mask: str = "none",
    mask_method: str = "intensity",
    window_size: int = 32,
    overlap: int = 12,
    search_area: int = 38,
    dt: float = 0.02,
    scaling_factor: float = 96.52,
    threshold: float = 1.05,
    drop_invalid: bool = False,
    verbose: bool = False,
) -> Path:
    """Run PIV analysis on an image pair and return the output directory.

    scaling_factor is in pixels per physical unit (px/mm for OpenPIV's own test1 data),
    so u and v come out in that unit per second.
    """
    if search_area < window_size:
        raise ValueError(
            f"search_area ({search_area}) must be >= window_size ({window_size})"
        )
    if overlap >= window_size:
        raise ValueError(
            f"overlap ({overlap}) must be < window_size ({window_size})"
        )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"Loading images: {image1}, {image2}")

    frame_a = tools.imread(image1)
    frame_b = tools.imread(image2)

    if mask == "dynamic":
        if verbose:
            print(f"Applying dynamic mask (method={mask_method})")
        # dynamic_masking returns (masked_image, mask); the returned image already
        # has the masked region zeroed, so use it directly rather than multiplying
        # by the mask -- for method="edges" the mask is uint8 0/255, not boolean.
        frame_a, _ = preprocess.dynamic_masking(
            frame_a.astype(np.float64), method=mask_method
        )
        frame_b, _ = preprocess.dynamic_masking(
            frame_b.astype(np.float64), method=mask_method
        )

    u, v, s2n = pyprocess.extended_search_area_piv(
        frame_a.astype(np.int32),
        frame_b.astype(np.int32),
        window_size=window_size,
        overlap=overlap,
        dt=dt,
        search_area_size=search_area,
        # "circular" wraps around and aliases displacements once the search area
        # exceeds the window; "linear" zero-pads instead.
        correlation_method="linear" if search_area > window_size else "circular",
        sig2noise_method="peak2peak",
    )

    x, y = pyprocess.get_coordinates(
        image_size=frame_a.shape,
        search_area_size=search_area,
        overlap=overlap,
    )

    # flags is boolean: True marks a spurious vector.
    flags = validation.sig2noise_val(s2n, threshold=threshold)
    if verbose:
        total = flags.size
        print(f"Flagged {int(np.sum(flags))}/{total} vectors below s2n {threshold}")

    u, v = filters.replace_outliers(
        u, v, flags, method="localmean", max_iter=3, kernel_size=2
    )

    if drop_invalid:
        # Discard the interpolated values and leave holes instead.
        u = np.where(flags, np.nan, u)
        v = np.where(flags, np.nan, v)

    x, y, u, v = scaling.uniform(x, y, u, v, scaling_factor=scaling_factor)
    x, y, u, v = tools.transform_coordinates(x, y, u, v)

    np.savez(output_path / "params.npz", x=x, y=y, u=u, v=v, flags=flags)

    vectors_file = output_path / "vectors.txt"
    tools.save(vectors_file, x, y, u, v, flags)

    fig, ax = plt.subplots(figsize=(8, 8))
    with warnings.catch_warnings():
        # display_vector_field() ends in plt.show(), which warns under Agg.
        warnings.filterwarnings("ignore", message=".*non-interactive.*")
        tools.display_vector_field(
            vectors_file,
            ax=ax,
            scaling_factor=scaling_factor,
            scale=50,
            width=0.0035,
            on_img=True,
            image_name=image1,
        )
    fig.savefig(output_path / "vector_field.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    if verbose:
        print(f"Results saved to {output_path}")
        for name in ("vectors.txt", "params.npz", "vector_field.png"):
            print(f"  - {name}")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="OpenPIV - Particle Image Velocimetry processing"
    )
    parser.add_argument(
        "--image",
        action="append",
        required=True,
        help="Image file; specify exactly twice for the pair",
    )
    parser.add_argument("--output_dir", default="results", help="Output directory")
    parser.add_argument(
        "--mask",
        default="none",
        choices=["none", "dynamic"],
        help="Masking mode (default: none)",
    )
    parser.add_argument(
        "--mask_method",
        default="intensity",
        choices=["edges", "intensity"],
        help="openpiv.preprocess.dynamic_masking method, used with --mask dynamic",
    )
    parser.add_argument(
        "--window_size", type=int, default=32, help="Window size in pixels"
    )
    parser.add_argument("--overlap", type=int, default=12, help="Overlap in pixels")
    parser.add_argument(
        "--search_area", type=int, default=38, help="Search area size in pixels"
    )
    parser.add_argument(
        "--dt", type=float, default=0.02, help="Time between frames (s)"
    )
    parser.add_argument(
        "--scaling",
        type=float,
        default=96.52,
        help="Scaling factor, pixels per physical unit (e.g. px/mm)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=1.05,
        help="peak2peak signal-to-noise threshold",
    )
    parser.add_argument(
        "--drop_invalid",
        action="store_true",
        help="NaN out flagged vectors instead of keeping interpolated values",
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if len(args.image) != 2:
        parser.error("Exactly two --image arguments required")

    run_openpiv(
        image1=args.image[0],
        image2=args.image[1],
        output_dir=args.output_dir,
        mask=args.mask,
        mask_method=args.mask_method,
        window_size=args.window_size,
        overlap=args.overlap,
        search_area=args.search_area,
        dt=args.dt,
        scaling_factor=args.scaling,
        threshold=args.threshold,
        drop_invalid=args.drop_invalid,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
```
