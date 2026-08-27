---
name: fluidsim
description: Plan, configure, inspect, restart, and analyze bounded FluidSim computational-fluid-dynamics simulations with explicit numerical-validity and HPC safety checks. Use for FluidSim solver selection, parameter review, FFT/MPI setup, output diagnostics, or restart compatibility.
---

# FluidSim

Use FluidSim 0.9.0 as a framework for Python-defined numerical solvers, especially
periodic Cartesian pseudospectral CFD. Upstream FluidSim is CeCILL-2.1; the MIT
frontmatter license applies only to this skill.

This skill does **not** treat a completed run, a stable time step, a smooth plot,
or a closed program exit as evidence of numerical convergence or physical
validity.

## Required workflow

1. State equations, units or nondimensionalization, geometry, boundaries,
   initial conditions, forcing, observables, and acceptance criteria.
2. Select a verified solver and inspect its generated default parameters.
3. Create a strict JSON plan with explicit CPU, RAM, disk, wall-time, output-file,
   timestep, CFL, resolution, and dealiasing bounds.
4. Run the bundled validator and resource estimator.
5. Generate and review a dry-run script. It does nothing unless executed with an
   explicit config-ID acknowledgement.
6. Run one tiny serial pilot. Inspect budgets, divergence/constraints, spectral
   tails, CFL/time-step history, and output growth.
7. Refine grid and time step independently. Check conservation/budget residuals
   and observable sensitivity.
8. Only then prepare a site-specific MPI job. Never submit or launch MPI
   automatically.
9. Preserve config, script, `uv.lock`, package/platform/backend versions, logs,
   output inventory, checksums, and restart lineage.

Stop if physical assumptions, units, boundary conditions, forcing semantics,
resolution criteria, resource limits, or acceptance criteria are missing.

## Version and installation

As verified on 2026-07-23:

- Latest stable PyPI release: `fluidsim==0.9.0` (2025-12-04).
- Package metadata requires Python `>=3.11` and lists Python 3.11–3.14.
- Pseudospectral parameter creation needs FluidFFT; bare `fluidsim` imported in
  the smoke test, but `ns2d.create_default_params()` failed until the `fft` extra
  was installed.
- Current companion versions tested here: `fluidfft==0.4.5` and
  `pyFFTW==0.15.1`.

Prefer a project lock:

```bash
uv init --python 3.11
uv add "fluidsim[fft]==0.9.0" "fluidfft==0.4.5" "pyFFTW==0.15.1"
uv lock
uv sync --frozen
```

For an isolated disposable environment:

```bash
uv venv --python 3.11
uv pip install "fluidsim[fft]==0.9.0" "fluidfft==0.4.5" "pyFFTW==0.15.1"
```

The project lock is the reproducibility record; direct pins alone do not freeze
all transitive artifacts. Do not reuse a lock across incompatible platforms or
MPI ABIs.

MPI is optional and native:

```bash
uv add "mpi4py==4.1.2" "fluidfft-mpi-with-fftw==0.0.1" "fluidfft-fftwmpi==0.0.1"
uv lock
```

Those packages still require a compatible MPI runtime and FFTW development
libraries. The optional native plugins are:

- `fluidfft-fftw==0.0.1`: sequential
  `fft2d.with_fftw1d`, `fft2d.with_fftw2d`, `fft3d.with_fftw3d`.
- `fluidfft-mpi-with-fftw==0.0.1`: MPI
  `fft2d.mpi_with_fftw1d`, `fft3d.mpi_with_fftw1d`.
- `fluidfft-fftwmpi==0.0.1`: MPI-enabled FFTW
  `fft2d.mpi_with_fftwmpi2d`, `fft3d.mpi_with_fftwmpi3d`.
- `fluidfft-p3dfft==0.0.1`: `fft3d.mpi_with_p3dfft`; requires P3DFFT.
- FluidFFT also declares PFFT and P3DFFT extras; audit and pin their native
  stacks for the target cluster.

FluidFFT documents cuFFT historically, but FluidFFT 0.4.5 declares no CUDA extra
or installed GPU plugin in its package metadata, and its CUDA installation page
is unfinished. Do not claim GPU acceleration or install an unrelated CUDA wheel
as a FluidSim backend. Treat GPU work as source-level experimental integration
requiring separate validation.

See [installation](references/installation.md) for system dependencies, MPI ABI,
HDF5-MPI, backend discovery, and verification.

## API snapshot

Use direct, versioned imports:

```python
from fluidsim.solvers.ns2d.solver import Simul

params = Simul.create_default_params()
params.oper.nx = params.oper.ny = 32
params.oper.Lx = params.oper.Ly = 2 * 3.141592653589793
params.oper.coef_dealiasing = 2 / 3
params.time_stepping.USE_CFL = True
params.time_stepping.cfl_coef = 0.5
params.time_stepping.deltat0 = 0.001
params.time_stepping.deltat_max = 0.01
params.time_stepping.t_end = 0.1
params.time_stepping.max_elapsed = "00:05:00"
params.init_fields.type = "noise"
params.init_fields.noise.velo_max = 0.01
params.output.HAS_TO_SAVE = False
params.output.ONLINE_PLOT_OK = False
```

Important 0.9 corrections:

- CFL field: `params.time_stepping.cfl_coef`, not `CFL`.
- Time-correlated forcing:
  `params.forcing.tcrandom.time_correlation`, not a flat
  `tcrandom_time_correlation`.
- NS2D default initial types include `constant`, `noise`, `jet`, `dipole`,
  `from_file`, `from_simul`, and `in_script`; do not invent a universal list for
  every solver.
- Output state files default to `state_phys_t*.nc`; spectra use
  `spectra1D.h5`/`spectra2D.h5`; scalar means are solver-dependent
  `spatial_means.txt` or JSON-lines.
- `params.output.sub_directory` is relative under `FLUIDSIM_PATH`.

`ParamContainer` rejects undeclared attributes. Always generate defaults from the
selected `Simul` class and inspect them before changing values. See
[parameters](references/parameters.md).

## Solvers

Primary Cartesian CFD keys and imports:

```python
from fluidsim.solvers.ns2d.solver import Simul       # ns2d
from fluidsim.solvers.ns2d.bouss.solver import Simul # ns2d.bouss
from fluidsim.solvers.ns2d.strat.solver import Simul # ns2d.strat
from fluidsim.solvers.ns3d.solver import Simul       # ns3d
from fluidsim.solvers.ns3d.bouss.solver import Simul # ns3d.bouss
from fluidsim.solvers.ns3d.strat.solver import Simul # ns3d.strat
```

The 0.9 registry also includes `plate2d`, `sw1l` variants, `waves2d`, 1D models,
0D models, spherical solvers, and framework adapters. Availability in the
registry does not make a solver appropriate for a scientific question. Verify
equations, variables, geometry, boundaries, and diagnostics in the solver
source. See [solvers](references/solvers.md).

## Forcing and time advancement

Forcing is solver-specific. A current normalized random example is:

```python
params.forcing.enable = True
params.forcing.type = "tcrandom"
params.forcing.forcing_rate = 1.0
params.forcing.nkmin_forcing = 4
params.forcing.nkmax_forcing = 5
params.forcing.tcrandom.time_correlation = "based_on_forcing_rate"
```

Record the forced variable, normalization definition, wave-number band, random
seed/state, injection target, and measured injection. FluidSim 0.9 saves state
parameters for restart; 0.8.6 fixed time-correlated forcing restart behavior.

Available pseudospectral schemes include Euler/RK2 phase-shift variants,
`RK2_trapezoid`, and `RK4`. A named order does not establish accuracy. Check CFL,
fast-wave/diffusive limits, `deltat_max`, and time-step refinement. See
[advanced features](references/advanced_features.md).

## Outputs, loading, and restart

For read-only analysis:

```python
from fluidsim import load_sim_for_plot

sim = load_sim_for_plot("run-directory", hide_stdout=True)
sim.output.spatial_means.plot()
sim.output.spectra.plot1d()
sim.output.phys_fields.plot(time=1.0)
```

`load_sim_for_plot` uses a coarse operator and disables saving/online plotting.
For a state-bearing object:

```python
from fluidsim import load_state_phys_file

sim = load_state_phys_file("run-directory", t_approx="last")
```

For a controlled restart, prefer `load_for_restart` or first run
`fluidsim-restart --only-check`. Do not use `--modify-params` with untrusted text:
the upstream CLI executes Python code supplied to that option. This skill's
generator never emits it. Verify solver, grid/domain, state variables, versions,
forcing state, checksum, target time, output destination, and resource bounds.
Resolution changes require the dedicated reviewed workflow, not a silent grid
edit. See [simulation workflow](references/simulation_workflow.md) and
[output analysis](references/output_analysis.md).

## Scientific acceptance gate

Before interpreting results, require:

- Explicit dimensional units or a complete nondimensionalization map.
- Correct equations, periodic geometry/boundaries, initial state, forcing, and
  diagnostic definitions.
- Resolution and dealiasing evidence: spectra/tails, resolved gradients, and
  solver-appropriate small-scale criteria.
- Timestep evidence: CFL history, fastest-wave and dissipative limits, and
  smaller-step comparison.
- Conservation and budget checks including forcing, dissipation, transfers, and
  residuals.
- Grid/time refinement with uncertainty or sensitivity for reported
  observables.
- Comparison to an analytical solution, manufactured solution, benchmark, or
  independently reproduced result where appropriate.
- Complete provenance and restart lineage.

Never label a run “DNS,” “converged,” “validated,” “steady,” or “physically
correct” from parameter values or plots alone.

## Bundled local tools

All tools emit strict JSON, reject URLs/traversal/symlinks, enforce hard bounds,
use no network or subprocess, and never launch a simulation:

```bash
python3 scripts/solver_config_validator.py --example
python3 scripts/solver_config_validator.py --config config.json
python3 scripts/grid_resource_estimator.py --config config.json
python3 scripts/simulation_dry_run.py --config config.json --output run.py
python3 scripts/output_inventory.py --path run-directory
python3 scripts/budget_summary.py --path run-directory
python3 scripts/restart_compatibility.py --source state.nc --target-config config.json
```

The HDF5 tools lazily require `h5py`, inspect bounded metadata/hyperslabs, and
never follow external links or load full field arrays.

## References

- [Installation and FFT/MPI backends](references/installation.md)
- [Solver registry and selection](references/solvers.md)
- [Simulation, pilot, and restart workflow](references/simulation_workflow.md)
- [Verified parameter surface](references/parameters.md)
- [Output, plotting, and budget analysis](references/output_analysis.md)
- [Forcing, operators, MPI, and migrations](references/advanced_features.md)

## Dated upstream basis

Verified 2026-07-23 against
[PyPI 0.9.0](https://pypi.org/project/fluidsim/),
[FluidSim 0.9 docs](https://fluidsim.readthedocs.io/en/latest/),
[release notes](https://fluidsim.readthedocs.io/en/latest/changes.html),
[official source mirror](https://github.com/fluiddyn/fluidsim),
[FluidFFT 0.4.5 docs](https://fluidfft.readthedocs.io/en/latest/), and the
primary FluidSim ([DOI 10.5334/jors.239](https://doi.org/10.5334/jors.239))
and FluidFFT ([DOI 10.5334/jors.238](https://doi.org/10.5334/jors.238))
papers. API claims use official docs/source; method/performance claims in the
references are scoped to the cited primary papers and their benchmark setups.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/fluidsim/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/advanced_features.md`

# Forcing, operators, MPI, extensions, and migrations

## Forcing architecture

FluidSim assembles forcing classes through the selected solver's registry.
NS2D 0.9 advertises:

- `in_script`
- `in_script_coarse`
- `pseudo_spectral`
- `proportional`
- `tcrandom`
- `tcrandom_anisotropic`

Availability and default forced variable are solver-specific.

Base fields:

```python
params.forcing.enable = True
params.forcing.type = "tcrandom"
params.forcing.forcing_rate = 1.0
params.forcing.key_forced = None
params.forcing.nkmin_forcing = 4
params.forcing.nkmax_forcing = 5
params.forcing.tcrandom.time_correlation = "based_on_forcing_rate"
```

Current source converts `nkmin_forcing`/`nkmax_forcing` to dimensional
wave-number bounds using the operator's wave-number spacing. Inspect the
resulting forced region; the integers are not necessarily physical wave
numbers.

### Normalization

Current normalized-forcing fields include:

```python
params.forcing.normalized.constant_rate_of = None
params.forcing.normalized.type = "2nd_degree_eq"
params.forcing.normalized.which_root = "minabs"
```

The implementation can solve a quadratic normalization so the time-step-mean
injection of a quadratic quantity matches `forcing_rate`. The exact quadratic
quantity and key depend on the solver/forced field. Therefore:

- State the intended injected invariant and units.
- Confirm `key_forced`.
- Measure forcing power in output.
- Check the global/spectral budget using the same convention.
- Test time-step sensitivity of the measured injection.

Do not call `forcing_rate` “energy input” without verifying the selected class.

### Time-correlated random forcing

The 0.9 field is:

```python
params.forcing.tcrandom.time_correlation = "based_on_forcing_rate"
```

or a finite time value. Current source derives the default period as a power of
the forcing rate and stores two random seeds plus the last-change time in state
parameters. FluidSim 0.9.0 writes these state parameters into restart files;
0.8.6 fixed a time-correlated forcing restart bug.

For reproducibility, preserve:

- Initial random seed strategy.
- Saved forcing state parameters.
- MPI rank count/decomposition and package versions.
- Correlation-time setting and measured autocorrelation.
- Restart boundary diagnostics.

### In-script forcing

Use the solver's registered `InScriptForcing*` interface and documented
`compute_forcing_fft_each_time` or coarse equivalent. Do not monkey-patch a
method with a lambda copied from an old example:

- State keys have changed in some solvers.
- Local spectral layout depends on FFT/MPI backend.
- Hermitian/reality constraints and normalization must be preserved.
- A literal global Fourier index is not portable across decompositions.

Implement a reviewed subclass/extension with unit tests on tiny sequential and
MPI layouts. Validate zero-net/target injection, symmetry, and budget effects.

## Operators and array ownership

`sim.oper` provides solver-selected grids, FFT/IFFT, differentiation, vector
calculus, projections, spectra, dealiasing, and distributed-array helpers.
Method names and array layouts depend on operator class.

Never assume:

- Axis order from `nx`, `ny`, `nz`.
- Full global arrays on every rank.
- A Fourier mode has the same local index under another backend/rank count.
- All FFT backends use the same spectral shape.
- A gathered array fits rank-0 memory.
- Direct NumPy sums have the same normalization as
  `oper.sum_wavenumbers`.

Use documented operator methods and inspect:

```python
print(type(sim.oper))
print(sim.oper.axes)
print(sim.params.oper)
```

For custom diagnostics, test sequential and distributed shapes and compare
against analytical transforms at tiny resolution.

## Dealiasing

The common Cartesian field is:

```python
params.oper.coef_dealiasing = 2 / 3
params.oper.truncation_shape = "cubic"
```

FluidSim also implements phase-shift time schemes. A coefficient or scheme name
does not prove alias removal for a custom nonlinearity. Verify:

- Polynomial/nonlinear form and expected alias interactions.
- Where dealiasing is applied.
- Truncation geometry.
- Spectral tails and invariant transfer.
- Results under stricter truncation or exact phase-shift method.

Do not combine an aggressive cutoff and high-order dissipation merely to obtain
a visually smooth spectrum.

## Time schemes

Documented pseudospectral names:

- `Euler`
- `Euler_phaseshift`
- `Euler_phaseshift_random`
- `RK2`
- `RK2_trapezoid`
- `RK2_phaseshift`
- `RK2_phaseshift_random`
- `RK2_phaseshift_random_split`
- `RK2_phaseshift_exact`
- `RK4`

The implementation treats linear terms with exact coefficients in its
pseudospectral stepper and evaluates nonlinear tendencies according to the
named scheme. Verify source and solver coupling before making an order/stability
claim.

Always check:

- Advective CFL.
- Wave frequency limits (stratification, rotation, shallow-water waves).
- Diffusive/hyperdiffusive limits.
- Forcing correlation and output cadence relative to `deltat`.
- Smaller `cfl_coef`/`deltat_max` comparison.

`USE_CFL=True` only activates the solver's CFL logic; it does not guarantee all
accuracy/stability constraints are resolved.

## Custom initial conditions

`in_script` gives direct control, but use current state keys:

1. Construct `Simul` with `init_fields.type = "in_script"`.
2. Inspect the solver's state documentation/keys.
3. Fill canonical physical or spectral variables.
4. Call the documented conversion in the correct direction.
5. Apply projection/dealiasing/constraints as required.
6. Save an initialization checkpoint and verify budgets before stepping.

Old examples that fill `vx`/`vy` and then call a
spectral-to-physical conversion can overwrite the intended state. NS2D 0.9
documentation shows physical keys including `ux`, `uy`, and `rot`; use the
selected solver's actual keys.

## Extending a solver

FluidSim's `InfoSolver`/class registry supports extensions. For a research
extension:

- Pin FluidSim/FluidSim Core source and version.
- Subclass the closest solver and extend default parameters through the current
  class mechanism.
- Register state variables, operators, initialization, forcing, outputs, and
  restart state explicitly.
- Define nonlinear tendencies with documented sign and normalization.
- Add unit/manufactured-solution tests and budget identities.
- Test serialization/restart and old/new parameter merging.
- Benchmark only after correctness tests.

Avoid private-method snippets from old versions without source review.

## FluidFFT backend selection

Installed methods are entry points. Discover them:

```python
from fluidfft import get_methods

print(sorted(get_methods(ndim=2)))
print(sorted(get_methods(ndim=3)))
```

Set per run:

```python
params.oper.type_fft = "fft2d.with_pyfftw"
```

or use `FLUIDSIM_TYPE_FFT2D`/`FLUIDSIM_TYPE_FFT3D` before process start.
Record actual method and plugin distribution.

FluidFFT's 2019 primary paper demonstrates:

- Unified C++/Python APIs for multiple FFT libraries.
- One-dimensional and pencil/two-dimensional MPI decompositions.
- Hardware/shape/process-count-dependent fastest methods.
- Scaling beyond the limits of slab decomposition in the tested cases.

Do not transfer its fastest-method or wall-time numbers to current hardware.
Benchmark a bounded representative shape in the target environment.

## MPI planning and safety

Never call `mpirun`, `mpiexec`, `srun`, `qsub`, `sbatch`, OAR tools, or a
FluidDyn cluster submitter automatically.

Required preflight:

- Written resource estimate and output estimate.
- Approved allocation and partition/account.
- Exact MPI implementation/ABI and launcher.
- FFT plugin/native library compatibility.
- Rank/thread placement and oversubscription check.
- Per-rank local shapes and no zero-sized unsupported decomposition.
- Memory/rank and rank-0 gather/output risk.
- Wall-time signal/checkpoint behavior.
- Filesystem quota, inode count, stripe policy, and cleanup.
- Tiny serial then two-rank smoke.
- Restart plan with immutable parent state.

Output behavior can differ with MPI-enabled h5py. Standard h5py usually causes
rank 0 to write assembled state; MPI h5py can use an `mpio` driver. Verify the
locked h5py build and output path with a tiny test.

## Parametric studies

Do not loop over simulations and start them directly in one script by default.
Instead:

1. Materialize one strict config per case.
2. Assign a stable case ID and seed.
3. Validate/estimate each case.
4. Sum aggregate CPU, memory concurrency, disk, files, and wall time.
5. Generate scripts only.
6. Review sampling design and avoid changing multiple factors ambiguously.
7. Submit through an approved external workflow.
8. Track failures/missing cases without silently resampling.

Analyze observables with refinement and stochastic uncertainty, not only final
values.

## Checkpoint and restart

Physical-state saving is checkpoint creation:

```python
params.output.periods_save.phys_fields = 1.0
```

But checkpoint usability requires:

- Complete `/state_phys` datasets.
- `/info_simul/params` and solver metadata.
- 0.9 state parameters where needed.
- Matching solver/grid/domain/state.
- SHA-256 and parent lineage.
- Enough disk for parent and child.

Use the bundled compatibility checker before every continuation. A mechanically
compatible state can still be scientifically invalid after changed viscosity,
forcing, timestep, backend, or resolution.

## Migration notes to 0.9.0

### 0.9.0 (release notes dated 2025-12-03)

- Restart files store state parameters.
- Added basic physical-field utilities.
- Fixed restart filenames.
- Improved post-initialization information and profile analysis.

### 0.8.6 (2025-11-23)

- h5netcdf 1.7 compatibility.
- Fixed incorrect restart for time-correlated forcing.

### 0.8.5 (2025-10-23)

- Python 3.14 support.

### 0.8.2 (2024-08-17)

- Python 3.12, NumPy 2.0, and mpi4py 4.0 compatibility.

### 0.8.0 (2024-01-31)

- Meson/meson-python build system.

Practical migrations from the previous skill:

- Python baseline: `>=3.11`, not `>=3.9` for 0.9.0.
- Use exact `fluidsim==0.9.0` and lock dependencies.
- Pseudospectral defaults need the `fft` extra.
- Use `time_stepping.cfl_coef`, not `CFL`.
- Use `forcing.tcrandom.time_correlation`, not a flat field.
- Use `plate2d`, not `fvk`.
- Physical states default to `.nc`, not `.h5`; spectra remain `.h5`.
- Use `spect_energy_budg.h5`, not a timestamped budget glob.
- Prefer `load_for_restart`/`fluidsim-restart --only-check`; preserve state
  parameters and hashes.
- Do not advertise ParaView direct compatibility without an explicit tested
  conversion/plugin.

## Sources (verified 2026-07-23)

- [FluidSim forcing base source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/forcing/base.py).
- [Specific forcing source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/forcing/specific.py).
- [Pseudospectral time-step API](https://fluidsim.readthedocs.io/en/latest/generated/fluidsim.base.time_stepping.pseudo_spect.html).
- [FluidSim development tutorial](https://fluidsim.readthedocs.io/en/latest/ipynb/tuto_dev.html).
- [FluidSim release notes](https://fluidsim.readthedocs.io/en/latest/changes.html).
- [FluidFFT plugins](https://fluidfft.readthedocs.io/en/latest/plugins.html).
- [FluidFFT supported libraries](https://fluidfft.readthedocs.io/en/latest/install/fft_libs.html).
- Mohanan et al., [FluidFFT primary paper](https://doi.org/10.5334/jors.238),
  published 2019-04-01.
- Mohanan et al., [FluidSim primary paper](https://doi.org/10.5334/jors.239),
  published 2019-04-26.

### `references/installation.md`

# Installation, native dependencies, and backends

## Supported baseline

Verified 2026-07-23:

- `fluidsim==0.9.0`, released on PyPI 2025-12-04.
- FluidSim package metadata requires Python `>=3.11` and classifies Python
  3.11–3.14.
- `fluidsim-core==0.9.0`, released 2025-12-03.
- `fluidfft==0.4.5`, released 2025-10-13, requires Python `>=3.11`.
- `pyFFTW==0.15.1`, released 2025-10-22, requires Python `>=3.11`.
- `mpi4py==4.1.2`, released 2026-05-16, requires Python `>=3.8`.

The FluidSim installation page still says Python `>=3.9`; current PyPI and
`pyproject.toml` metadata say `>=3.11`. Use the package metadata for 0.9.0.

FluidSim 0.9.0 declares:

- Core: `fluidsim-core>=0.8.6,<0.9.1`, `h5py`, `h5netcdf`,
  `transonic>=0.6.2`, `xarray`, `rich`, `matplotlib>=3.3`, and `scipy`.
- `fft`: `pyfftw>=0.10.4`, `fluidfft>=0.4.0`.
- `mpi`: `mpi4py`.
- Other extras: `test`, `test-mpi`, and `pulp`.

The broad upstream constraints are compatibility ranges, not a reproducible
environment. Record the generated lock and artifact hashes.

## Reproducible uv environment

Preferred project workflow:

```bash
uv init --python 3.11
uv add "fluidsim[fft]==0.9.0" "fluidfft==0.4.5" "pyFFTW==0.15.1"
uv lock
uv sync --frozen
```

Check the lock into the study repository. Record:

- `uv.lock` SHA-256 and target platform.
- Python implementation/build.
- FluidSim, FluidSim Core, FluidDyn, FluidFFT, Transonic, Pythran, NumPy,
  SciPy, h5py, h5netcdf, xarray, and pyFFTW versions.
- Wheel/sdist hashes and package index.
- Compiler and native-library versions if any package builds locally.

For an isolated smoke environment:

```bash
uv venv --python 3.11
uv pip install "fluidsim[fft]==0.9.0" "fluidfft==0.4.5" "pyFFTW==0.15.1"
```

This pins direct dependencies but does not replace a lock for transitive
reproducibility.

Bare `fluidsim==0.9.0` supports parts of the framework and analysis stack, but a
verified local smoke test found that importing NS2D succeeded while
`Simul.create_default_params()` failed without `fluidfft`. Install the `fft`
extra for pseudospectral solvers.

## Sequential FFT choices

The non-compiling path is:

```bash
uv add "fluidsim[fft]==0.9.0" "fluidfft==0.4.5" "pyFFTW==0.15.1"
```

FluidFFT 0.4.5 registers:

- `fft2d.with_pyfftw`
- `fft3d.with_pyfftw`
- `fft2d.with_dask` when Dask is installed

The native FFTW plugin is separately versioned:

```bash
uv add "fluidfft-fftw==0.0.1"
```

The `0.0.1` plugin versions are stable PyPI releases from February 2024 and are
versioned independently from FluidFFT 0.4.5; they are not proof of compatibility
with a particular native stack. Before installation, verify that each PyPI
project links to the official `fluiddyn/fluidfft` monorepo, review the plugin
source, resolve through `uv.lock`, retain artifact hashes, and use
`uv sync --frozen`. Do not trust a familiar distribution name alone.

It provides:

- `fft2d.with_fftw1d`
- `fft2d.with_fftw2d`
- `fft3d.with_fftw3d`

It requires discoverable FFTW headers/libraries and a working native build
toolchain. pyFFTW wheels bundle supported binaries on many 64-bit platforms;
source builds require FFTW `>=3.3`, Cython, and a compiler.

Discover only methods actually installed on the current host:

```bash
fluidfft-get-methods
```

Do not copy a method name from documentation and assume its plugin or ABI is
usable. Run a tiny transform/FluidSim pilot and record the selected method.

## MPI and distributed FFT

Nothing in this skill launches MPI or submits a scheduler job. First identify:

- Site MPI implementation and version: Open MPI, MPICH derivative, Intel MPI,
  Cray MPICH, or another vendor stack.
- Compiler wrappers and ABI.
- FFTW and `fftw3_mpi` versions/build options.
- Scheduler, process placement, cores/rank, threads/rank, memory/rank, wall time,
  filesystem, and module/container environment.

Then lock Python packages:

```bash
uv add "mpi4py==4.1.2" \
  "fluidfft-mpi-with-fftw==0.0.1" \
  "fluidfft-fftwmpi==0.0.1"
uv lock
```

Plugin methods:

- `fluidfft-mpi-with-fftw==0.0.1`:
  `fft2d.mpi_with_fftw1d`, `fft3d.mpi_with_fftw1d`.
- `fluidfft-fftwmpi==0.0.1`:
  `fft2d.mpi_with_fftwmpi2d`, `fft3d.mpi_with_fftwmpi3d`.
- `fluidfft-p3dfft==0.0.1`:
  `fft3d.mpi_with_p3dfft`, requiring P3DFFT.
- FluidFFT also declares `pfft` and `p3dfft` extras. Both require separately
  installed native MPI FFT libraries.

The package names use hyphens on PyPI; FluidFFT's optional dependency keys map
to distributions such as `fluidfft-mpi_with_fftw`. Let the lock resolve the
canonical distribution and preserve it.

`mpi4py` wheels still need a compatible MPI runtime. Convenience MPI wheels can
lack GPU awareness or site fabric support; mpi4py recommends system/vendor MPI
for production. Never mix an `mpi4py` build from one implementation with a
different launcher/runtime. Verify import and rank identity inside a manually
allocated tiny job before FluidSim.

The primary FluidFFT paper shows that the fastest backend depends on array
shape, machine, and process count; one-dimensional decomposition can be useful
at low rank count, while pencil/two-dimensional decomposition is needed to
avoid decomposition limits at high rank count. These are benchmark-context
claims, not universal backend recommendations.

## GPU status

The 2019 FluidFFT paper describes a cuFFT path, and the repository README still
lists cuFFT. However:

- FluidFFT 0.4.5 `pyproject.toml` declares no CUDA dependency/extra or cuFFT
  plugin entry point.
- The current supported-library page's CUDA section is an unfinished TODO.
- FluidSim 0.9.0 declares no GPU extra.

Therefore there is no supported one-line GPU installation in this skill. Do not
install `nvidia-cufft-*` and claim FluidSim acceleration: a runtime library alone
does not provide a registered FluidFFT method. A GPU experiment must pin CUDA,
driver, compiler, plugin source revision, Python packages, precision, hardware,
and validation tests separately.

## Native build prerequisites

Depending on selected plugins:

- C/C++11 and sometimes Fortran compilers.
- Meson/meson-python, Ninja, Pythran, Transonic, Cython, and development headers.
- FFTW3, threaded FFTW, and/or FFTW MPI.
- MPI compiler wrappers and runtime.
- PFFT or P3DFFT headers/libraries.
- BLAS configuration used by NumPy/Pythran.
- `CPATH`, `LIBRARY_PATH`, and runtime loader paths where site modules do not
  provide them.

The P3DFFT plugin also recognizes `P3DFFT_DIR`, or
`P3DFFT_LIB_DIR`/`P3DFFT_INCLUDE_DIR`. Record values but never alter global shell
startup files automatically.

## HDF5 and netCDF4

FluidSim 0.9 physical-state files default to netCDF4/HDF5 `.nc`; spectra remain
HDF5 `.h5`. Standard h5py wheels are usually non-MPI, which is normally
appropriate because output is coordinated by FluidSim. Parallel HDF5 is a
separate native build requiring:

- MPI-enabled HDF5.
- `h5py` built from source against the same MPI.
- Matching compiler wrappers and runtime libraries.

Do not build MPI-enabled h5py merely because the simulation uses MPI. Confirm
the intended I/O path and test a tiny file first.

## Runtime paths and backend selection

Official variables:

```bash
export FLUIDSIM_PATH="/approved/bounded/results-root"
export FLUIDDYN_PATH_SCRATCH="/approved/bounded/scratch-root"
export FLUIDSIM_TYPE_FFT2D="fft2d.with_pyfftw"
export FLUIDSIM_TYPE_FFT3D="fft3d.with_pyfftw"
```

Set only after checking:

- Paths exist or will be created in an approved parent.
- No symlink redirects outside the allocation.
- Quota and inode limits cover the estimate.
- The method appears in `fluidfft-get-methods`.
- Scratch retention and purge policy are recorded.

Prefer `params.oper.type_fft` for an explicit per-run choice. Environment
variables affect process-wide behavior and must be captured in provenance.

FluidFFT is also sensitive to `TRANSONIC_BACKEND`; changing it changes generated
code/performance and belongs in provenance.

## Verification ladder

Run in this order:

1. Dependency-free bundled CLI helps.
2. Import/version/solver parameter smoke in an isolated pinned environment.
3. Tiny serial `8x8` or `16x16` no-output initialization and one step.
4. Tiny serial output round-trip and restart.
5. Backend-specific FFT test.
6. Manually allocated two-rank smoke, only if MPI is required.
7. Representative bounded pilot with resource monitoring.

Do not run the full upstream test suite or MPI tests on a login node without
approval; they can compile, spawn processes, and consume resources.

## Sources (verified 2026-07-23)

- [FluidSim PyPI](https://pypi.org/project/fluidsim/) — 0.9.0 metadata and
  2025-12-04 release.
- [FluidSim 0.9 source metadata](https://github.com/fluiddyn/fluidsim/blob/branch/default/pyproject.toml)
  — dependencies, extras, entry points, Python requirement.
- [Install and configure](https://fluidsim.readthedocs.io/en/latest/install.html)
  — extras, native plugins, MPI/HDF5, and environment variables.
- [FluidFFT 0.4.5 source metadata](https://github.com/fluiddyn/fluidfft/blob/branch/default/pyproject.toml)
  — plugin extras and methods.
- [Official FluidFFT plugin source tree](https://github.com/fluiddyn/fluidfft/tree/branch/default/plugins)
  — provenance for separately distributed native plugins.
- [FluidFFT plugins](https://fluidfft.readthedocs.io/en/latest/plugins.html) and
  [installation](https://fluidfft.readthedocs.io/en/latest/install.html).
- [pyFFTW PyPI](https://pypi.org/project/pyFFTW/) — 0.15.1 metadata and build
  requirements.
- [mpi4py PyPI](https://pypi.org/project/mpi4py/) — 4.1.2 metadata and MPI ABI
  guidance.
- [FluidFFT primary paper](https://doi.org/10.5334/jors.238), published
  2019-04-01 — architecture and scoped backend/scaling benchmarks.

### `references/output_analysis.md`

# Output inventory, plotting, and budget analysis

## Analyze without overclaiming

Output analysis can detect errors and quantify diagnostics. It cannot by itself
establish:

- Correct equations, units, or boundary/initial/forcing conditions.
- Adequate resolution or dealiasing.
- Stable/accurate time integration.
- Conservation or budget closure.
- Statistical stationarity.
- Grid/time convergence.
- Physical validity.

Keep plotting descriptive until those checks pass.

## FluidSim 0.9 physical-state format

Official 0.9 source selects:

- `.nc` with `h5netcdf` when h5py lacks MPI support (normal default).
- `.h5` with h5py when h5py is MPI-enabled.

Filename:

```text
state_phys_t<TIME>[_it<ITERATION>].nc
```

or `.h5`, depending on the backend. The file is HDF5-backed in either current
path. It contains:

- `/state_phys`: solver state datasets.
- `/state_phys` attributes including `time`, `it`, variable type, and purpose.
- `/info_simul`: solver and parameter provenance.
- Saved state parameters when available, including restart-relevant forcing
  state in 0.9.
- Root attributes such as run/solver identity, axes, and save date.

Do not infer the latest valid checkpoint solely from a filename. Verify HDF5
readability, `/state_phys`, time/iteration attributes, expected datasets,
parameters, state parameters, size, and checksum.

## Other common outputs

Exact outputs depend on the solver and enabled classes.

### Spatial means

- Legacy/solver-specific: `spatial_means.txt`, generally repeated
  `key = value` records.
- Some output classes use `spatial_means.json`, JSON-lines records.
- Typical content can include time, energy/enstrophy, forcing power,
  dissipation, and solver-specific quantities.

Use the solver's `load()` implementation. It can return a dictionary, pandas
object, or another solver-specific structure; do not assume one universal
DataFrame schema.

### Spectra

Current 2D base spectra initialize:

```text
spectra1D.h5
spectra2D.h5
```

Common datasets include:

- `times`
- `kxE`, `kyE`, or `khE`
- solver-specific `spectrum1D*` or `spectrum2D*` arrays

NS2D/NS3D and stratified variants define different keys and dimensions.
`load1d_mean()`/`load2d_mean()` return dictionaries in the base implementation;
inspect keys before use.

### Spectral energy budget

The current base filename is:

```text
spect_energy_budg.h5
```

For NS2D, current source computes `transfer2D_E` and `transfer2D_Z` and derives
fluxes with a reverse cumulative sum multiplied by wave-number spacing. Other
solvers define different transfer/budget terms.

Do not interpret a transfer sign, flux plateau, or cascade without verifying:

- Fourier/spectrum normalization.
- Wave-number coordinate and shell/bin measure.
- Sign convention.
- Time averaging interval and stationarity.
- Forcing/dissipation ranges.
- Finite-domain and dealiased cutoff effects.
- Closure against the corresponding global budget.

### Logs and parameter files

A normal run may include:

- `params_simul.xml`
- `info_solver.xml`
- `stdout.txt`
- a run lock while advancing
- solver/output-specific HDF5, netCDF4, text, or JSON files

Inventory actual contents instead of assuming all files exist.

## Bounded metadata inventory

```bash
python3 scripts/output_inventory.py \
  --path run-directory \
  --max-files 256 \
  --max-hdf5-files 32 \
  --max-datasets 2000 \
  --max-attributes 5000
```

The helper:

- Accepts only local paths inside `--root`.
- Rejects URLs, parent traversal, symlinks, hard links, special files, and
  unbounded counts.
- Lazily imports h5py only for HDF5/netCDF4 candidates.
- Reports dataset shape, dtype, chunks, compression, and allocated storage.
- Reads only a short allowlist of scalar provenance attributes.
- Does not index datasets.
- Does not follow soft or external HDF5 links.
- Emits strict JSON and no raw field values.

If a `.nc` file is classic netCDF rather than HDF5, it reports it unreadable
rather than trying another unbounded parser.

## Read-only FluidSim object

```python
from fluidsim import load_sim_for_plot

sim = load_sim_for_plot(
    "run-directory",
    merge_missing_params=False,
    hide_stdout=True,
)
```

Official 0.9 source uses a coarse operator and disables saving/online plots.
This is appropriate for output-class analysis, not full-resolution arbitrary
field operations.

Examples:

```python
sim.output.phys_fields.plot(time=1.0)
sim.output.spatial_means.plot()
sim.output.spectra.plot1d(tmin=0.5, tmax=1.0)
sim.output.spect_energy_budg.plot(tmin=0.5, tmax=1.0)
```

Methods and accepted arguments vary by solver/output class. Check the selected
class API. A successful plot says nothing about correctness.

## Full state loading

```python
from fluidsim import load_state_phys_file

sim = load_state_phys_file(
    "run-directory",
    t_approx="last",
    modif_save_params=True,
    merge_missing_params=False,
    init_with_initialized_state=True,
    hide_stdout=True,
)
```

This can allocate full-resolution state/operators. Run the memory estimator
first and do not use it merely to inspect metadata.

`modif_save_params=True` disables saving/online plotting. To continue a run,
use the reviewed restart workflow rather than toggling saving casually.

## Scalar and spectral summary helper

```bash
python3 scripts/budget_summary.py \
  --path run-directory \
  --max-files 128 \
  --max-records 200000 \
  --max-datasets 256 \
  --max-values-per-dataset 4096
```

It:

- Aggregates finite spatial-mean values in constant memory.
- Supports FluidSim key/value text and strict JSON-lines.
- Summarizes only bounded spectral/budget hyperslabs.
- Uses the latest first-axis record for multidimensional datasets.
- Emits a sum only when the entire latest record fits the value bound.
- Does not follow external links or load full large arrays.
- Explicitly reports that convergence/physical validity are not established.

This is a triage summary, not a solver-aware closure calculation.

## Budget checks

Construct a table or plot for each governing budget:

1. Stored quantity change over the same interval.
2. Measured forcing/input.
3. Physical and numerical dissipation.
4. Transfer terms with consistent sign/normalization.
5. Boundary terms (zero only if justified by periodicity/model).
6. Residual after all terms.

Report absolute and normalized residuals, time interval, differencing method,
save cadence, and uncertainty. A small instantaneous residual can be accidental;
inspect trends and refinement.

For forced turbulence, compare requested `forcing_rate` to measured forcing
power. They are not interchangeable without checking the implementation's
normalization and time discretization.

## Resolution and dealiasing diagnostics

At minimum:

- Plot/inspect spectra up to the dealiased cutoff.
- Quantify energy/variance in a documented high-wave-number tail band.
- Check pile-up, aliasing signatures, anisotropy, and directional spectra where
  relevant.
- Check physical-space extrema/gradients and solver constraints.
- Repeat at finer resolution with the same physical/nondimensional problem.
- Avoid choosing an “inertial range” after seeing the desired slope without
  reporting selection criteria and sensitivity.

Power-law fitting alone does not verify a cascade or resolved simulation.

## Time-step diagnostics

Use stdout/output time-step history to inspect:

- Initial and maximum `deltat`.
- CFL-driven changes.
- Fast-wave or buoyancy/rotation scales.
- Diffusive/hyperdiffusive limits.
- Discontinuities around restart.
- Sensitivity to lower `deltat_max`/`cfl_coef`.

Do not infer stability from the absence of NaNs.

## Stationarity and averaging

Before time averaging:

- Define stationarity metrics and burn-in independently of the desired result.
- Plot energy, dissipation, forcing, and key observables.
- Check drift and autocorrelation/integral times.
- Report effective sample duration/count.
- Repeat across seeds or independent intervals where stochastic uncertainty
  matters.

Do not label “statistically steady” from a short visual plateau.

## Custom HDF5 reading

If built-in loaders are insufficient, keep access bounded:

```python
import h5py

with h5py.File("spectra2D.h5", "r") as handle:
    dataset = handle["spectrum2D_E"]
    latest = dataset[-1, :4096]
```

Before indexing, inspect shape, dtype, chunks, and expected bytes. Never use
`dataset[...]` or `[:]` on an unknown large field. Check HDF5 links before
traversal; an external link can open another file.

## Plot/report provenance

Every exported result should carry:

- Parent run/config/script/lock hashes.
- Solver and package/backend versions.
- Grid/domain/dealiasing/time scheme/CFL.
- Initial/forcing/dissipation definitions.
- State/output file hashes or immutable manifest.
- Exact dataset keys and time window.
- Averaging/binning/normalization and plotting code revision.
- Refinement and budget-check results.

Avoid manual GUI-only transformations that cannot be reconstructed.

## Sources (verified 2026-07-23)

- [Physical-field save source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/util/phys_fields.py)
  — `.nc`/`.h5` selection, groups, attributes, state parameters, filename.
- [Physical-fields output source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/output/phys_fields.py).
- [Spatial-means source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/output/spatial_means.py).
- [Spectra source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/output/spectra.py).
- [Spectral-budget base source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/output/spect_energy_budget.py).
- [NS2D spectral-budget source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/solvers/ns2d/output/spect_energy_budget.py).
- [Load utilities](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/util/util.py).
- Mohanan et al., [FluidSim primary paper](https://doi.org/10.5334/jors.239),
  published 2019-04-26 — architecture and output-class method claims.

### `references/parameters.md`

# Parameter surface and validation

## Source of truth

Create parameters from the exact selected class:

```python
from fluidsim.solvers.ns2d.solver import Simul

params = Simul.create_default_params()
print(params)
```

FluidSim composes parameters from registered operator, state, time-stepping,
initialization, forcing, and output classes. The tree is solver- and
extension-specific. There is no universal flat FluidSim parameter schema.

`ParamContainer` rejects assignment to undeclared attributes, which catches many
typos. It does not check units, physical interpretation, numerical convergence,
or whether a valid option is appropriate.

The following snapshot was introspected from a pinned
`fluidsim[fft]==0.9.0`/`fluidfft==0.4.5` NS2D environment on 2026-07-23.

## Top-level controls

Common pseudospectral fields:

```python
params.NEW_DIR_RESULTS = True
params.ONLY_COARSE_OPER = False
params.short_name_type_run = ""

params.nu_2 = 1e-3
params.nu_4 = 0.0
params.nu_8 = 0.0
params.nu_m4 = 0.0
```

- `NEW_DIR_RESULTS` primarily controls loading/restart output behavior. Official
  docs say a loaded simulation creates a new directory when true and appends to
  the old directory when false. Choose explicitly and preserve the parent.
- `ONLY_COARSE_OPER` is for fast loading/plotting and cannot process full fields.
- `nu_2`, `nu_4`, `nu_8`, and `nu_m4` are solver dissipation coefficients. Their
  dimensions depend on derivative order and nondimensionalization.

Do not use higher-order dissipation merely to hide insufficient resolution.
State its definition and verify budgets/tails/refinement.

Solver-specific top-level examples include:

- `N` for constant stratification in `.strat` solvers.
- `f` for rotation where implemented.
- `beta`, `c2`, projections, and other fields in specific solvers.

Inspect the selected solver documentation rather than copying these blindly.

## Operators

NS2D defaults:

```python
params.oper.nx = 48
params.oper.ny = 48
params.oper.Lx = 8
params.oper.Ly = 8
params.oper.coef_dealiasing = 2 / 3
params.oper.truncation_shape = "cubic"
params.oper.type_fft = "default"
params.oper.NO_KY0 = False
params.oper.NO_SHEAR_MODES = False
```

NS3D adds `nz`/`Lz` and solver-specific options. Never infer physical spacing
without the domain convention. Record:

- `nx`, `ny`, `nz` and `Lx`, `Ly`, `Lz`.
- Grid spacing and maximum represented/dealiased wave numbers.
- `coef_dealiasing`, truncation shape, and phase-shift scheme if used.
- Actual selected FluidFFT method and decomposition.
- Removed modes/symmetries.

Powers of two are not a universal requirement or guarantee of fastest FFT.
Benchmark representative allowed shapes on the target backend.

`type_fft="default"` delegates selection. For provenance-critical runs, inspect
and record the actual method; set an explicit tested method if the environment
supports it.

## Time stepping

NS2D 0.9.0 defaults:

```python
params.time_stepping.USE_CFL = True
params.time_stepping.USE_T_END = True
params.time_stepping.cfl_coef = None
params.time_stepping.deltat0 = 0.2
params.time_stepping.deltat_max = 0.2
params.time_stepping.it_end = 10
params.time_stepping.max_elapsed = None
params.time_stepping.t_end = 10.0
params.time_stepping.type_time_scheme = "RK4"
```

The current field is `cfl_coef`, **not** `CFL`.

For reproducible bounded plans, set explicitly:

```python
params.time_stepping.USE_CFL = True
params.time_stepping.cfl_coef = 0.5
params.time_stepping.deltat0 = 1e-3
params.time_stepping.deltat_max = 1e-2
params.time_stepping.USE_T_END = True
params.time_stepping.t_end = 0.1
params.time_stepping.max_elapsed = "00:05:00"
```

`cfl_coef=0.5` here is an explicit pilot choice, not a universal recommendation.
The acceptable value depends on equations, scheme, waves, dissipation, and
resolution. Check recorded `deltat` and refine.

Current pseudospectral scheme names documented in 0.9:

- `Euler`
- `Euler_phaseshift`
- `Euler_phaseshift_random`
- `RK2`
- `RK2_trapezoid`
- `RK2_phaseshift`
- `RK2_phaseshift_random`
- `RK2_phaseshift_random_split`
- `RK2_phaseshift_exact`
- `RK4`

Random phase-shift schemes also expose:

```python
params.time_stepping.phaseshift_random.nb_pairs = 1
params.time_stepping.phaseshift_random.nb_steps_compute_new_pair = None
```

Do not infer exact dealiasing or convergence from a scheme name. Verify its
implementation and test a smaller time step.

## Initial fields

NS2D advertises:

```python
params.init_fields.type = "constant"
params.init_fields.modif_after_init = False
```

Available types in the pinned NS2D profile:

- `constant`
- `noise`
- `jet`
- `dipole`
- `from_file`
- `from_simul`
- `in_script`

Nested fields include:

```python
params.init_fields.constant.value = 0.0
params.init_fields.noise.velo_max = 1.0
params.init_fields.noise.length = 0.0
params.init_fields.from_file.path = "state_phys_t001.000.nc"
```

Other solvers advertise different types/variables. For random initial fields,
record seed, process count, backend, generated spectrum/amplitude, and resulting
constraints. A seed alone may not guarantee bitwise identity across MPI
decompositions or versions.

For in-script initialization:

1. Inspect `sim.state.keys_state_phys`/solver state documentation.
2. Fill the solver's canonical variables.
3. Use the solver's documented physical-to-spectral conversion method.
4. Enforce divergence/constraints and dealias if required.
5. Save and inspect the initialized state before advancement.

Do not reuse old examples with guessed keys such as `vx` versus `ux`, or call a
spectral-to-physical method after modifying physical fields.

## Forcing

Base fields:

```python
params.forcing.enable = False
params.forcing.type = ""
params.forcing.forcing_rate = 1.0
params.forcing.key_forced = None
params.forcing.nkmin_forcing = 4
params.forcing.nkmax_forcing = 5
```

NS2D advertises `in_script`, `in_script_coarse`, `pseudo_spectral`,
`proportional`, `tcrandom`, and `tcrandom_anisotropic`.

Nested current fields:

```python
params.forcing.normalized.constant_rate_of = None
params.forcing.normalized.type = "2nd_degree_eq"
params.forcing.normalized.which_root = "minabs"
params.forcing.random.only_positive = False
params.forcing.tcrandom.time_correlation = "based_on_forcing_rate"
```

The old flat field `tcrandom_time_correlation` is not current.

For a time-correlated random plan:

```python
params.forcing.enable = True
params.forcing.type = "tcrandom"
params.forcing.forcing_rate = 1.0
params.forcing.nkmin_forcing = 4
params.forcing.nkmax_forcing = 5
params.forcing.tcrandom.time_correlation = "based_on_forcing_rate"
```

The integers multiply an operator wave-number spacing; they are not necessarily
physical wave numbers. Verify the resulting forced region. Measure actual input
in spatial means/budgets.

FluidSim 0.9.0 restart files store state parameters, including time-correlated
forcing seeds/state. Do not drop these groups when copying or converting
checkpoints.

## Output

Common controls:

```python
params.output.HAS_TO_SAVE = True
params.output.ONLINE_PLOT_OK = False
params.output.period_refresh_plots = 1
params.output.sub_directory = "bounded-pilot"

params.output.periods_print.print_stdout = 0.1
params.output.periods_plot.phys_fields = 0.0
params.output.periods_save.phys_fields = 0.5
params.output.periods_save.spatial_means = 0.05
params.output.periods_save.spectra = 0.5
params.output.periods_save.spect_energy_budg = 0.0
```

NS2D's 0.9 output tree also includes `increments`, `spectra_multidim`,
`temporal_spectra`, and `spatiotemporal_spectra`. A period of zero disables that
specific output.

`sub_directory` is created under `FLUIDSIM_PATH`. Use a safe one-component
identifier. Preflight quota, collision, and symlink behavior. `HAS_TO_SAVE=False`
is the correct smoke-test setting, but produces no restart checkpoint.

Physical-field settings include:

```python
params.output.phys_fields.field_to_plot = "rot"
params.output.phys_fields.file_with_it = False
```

Field names are solver-specific. Disable online plotting for unattended jobs.

## Strict JSON validator

The bundled validator covers reviewed Cartesian CFD profiles and requires
scientific and resource metadata in addition to FluidSim parameters:

```bash
python3 scripts/solver_config_validator.py --example
python3 scripts/solver_config_validator.py --config config.json
```

It rejects:

- Unknown keys and old `CFL`.
- Non-finite numbers and duplicate JSON keys.
- Unbounded grid/resources/output.
- Unsafe output or restart paths.
- Missing units/nondimensionalization, boundaries, initialization, forcing,
  resolution/dealiasing, CFL/timestep, budget, refinement, or acceptance
  statements.
- CPU oversubscription and inconsistent serial/MPI preview modes.

It validates a plan mechanically. It explicitly reports that physical validity
and numerical convergence are not established.

## Parameter provenance

Preserve:

- Exact parameter file from the run.
- Canonical strict JSON plan and SHA-256.
- Generated launch script and SHA-256.
- `uv.lock` and SHA-256.
- Solver module/key and package versions.
- FFT method, MPI size, threads, hardware, compiler/native libraries.
- Environment variables affecting FluidSim, FluidFFT, Transonic, OpenMP, MPI,
  and HDF5.
- Every restart parent/child and changed parameter.

Do not rely only on directory names; they are summaries, not canonical
configuration.

## Sources (verified 2026-07-23)

- [FluidSim user tutorial](https://fluidsim.readthedocs.io/en/latest/ipynb/tuto_user.html)
  — defaults, mutation behavior, output and loaders.
- [NS2D generated parameter documentation](https://fluidsim.readthedocs.io/en/latest/generated/fluidsim.solvers.ns2d.solver.html).
- [Pseudospectral time-stepping API](https://fluidsim.readthedocs.io/en/latest/generated/fluidsim.base.time_stepping.pseudo_spect.html).
- [Forcing base source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/forcing/base.py).
- [Specific forcing source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/base/forcing/specific.py).
- [FluidSim 0.9 package source](https://github.com/fluiddyn/fluidsim/blob/branch/default/pyproject.toml).

### `references/simulation_workflow.md`

# Bounded simulation, pilot, and restart workflow

## 1. Define the scientific contract

Before code, record:

- Equations, dependent variables, approximations, and solver key.
- Units for every dimensional quantity, or reference scales and a complete
  nondimensionalization map.
- Domain lengths, geometry, periodic boundary conditions, and symmetries.
- Initial-condition construction, constraints, amplitude/spectrum, and seed.
- Forcing field, band, normalization, correlation, and expected/measured input.
- Dissipation and any hypo-/hyper-viscosity.
- Observables and acceptance thresholds.
- Conservation/budget identities and expected numerical residual behavior.
- Grid, dealiasing, timestep/CFL, and refinement plan.
- Independent benchmark or verification target.

Do not proceed from a prompt that only says “simulate turbulence” or supplies a
Reynolds number without its definition and scaling.

## 2. Declare operational bounds

Every plan must explicitly bound:

- CPU cores.
- MPI ranks and threads/rank.
- Total and per-rank RAM envelope.
- Disk bytes and file/inode count.
- Wall time and FluidSim `max_elapsed`.
- Grid dimensions and total points.
- State snapshot and diagnostic save periods.
- Safe output root and subdirectory.

The bundled JSON schema requires these fields. Start from:

```bash
python3 scripts/solver_config_validator.py --example
```

Save the reviewed JSON locally, then:

```bash
python3 scripts/solver_config_validator.py --config config.json
python3 scripts/grid_resource_estimator.py --config config.json
python3 scripts/simulation_dry_run.py --config config.json --output run.py
```

The generator does not import FluidSim or run anything. The generated script
prints a JSON dry run by default. Execution requires both `--execute` and the
exact reviewed config ID. An MPI plan is only a command preview; the tool never
invokes a launcher or scheduler.

## 3. Verify the locked environment

In an isolated exact environment:

```python
from importlib.metadata import version
from fluidfft import get_methods

assert version("fluidsim") == "0.9.0"
assert version("fluidfft") == "0.4.5"
print(sorted(get_methods()))
```

Record the actual FFT methods. A documented method that is absent from
`get_methods()` is not installed. Importing a package is not enough: construct
the selected solver's defaults.

## 4. Tiny no-output serial smoke

After approval, use a trivial, bounded state:

```python
from fluidsim.solvers.ns2d.solver import Simul

params = Simul.create_default_params()
params.oper.nx = params.oper.ny = 8
params.oper.Lx = params.oper.Ly = 2.0
params.oper.coef_dealiasing = 2 / 3
params.time_stepping.USE_CFL = False
params.time_stepping.deltat0 = 0.001
params.time_stepping.deltat_max = 0.001
params.time_stepping.t_end = 0.001
params.time_stepping.max_elapsed = "00:01:00"
params.init_fields.type = "constant"
params.init_fields.constant.value = 0.0
params.output.HAS_TO_SAVE = False
params.output.ONLINE_PLOT_OK = False

sim = Simul(params)
sim.time_stepping.start()
```

This checks import, FFT construction, initialization, and one bounded step. It
does not test the intended physics, forcing, conservation, convergence,
performance, output, or restart.

## 5. Tiny output/restart smoke

Use a dedicated empty output root under a quota. Keep:

- `params.output.sub_directory` a safe one-component study identifier.
- `ONLINE_PLOT_OK = False` for unattended runs.
- Short `t_end`, short `max_elapsed`, and low resolution.
- One or two physical-state saves and a bounded scalar diagnostic.
- Spectra/budget outputs disabled unless they are the feature being tested.

Inspect before analysis:

```bash
python3 scripts/output_inventory.py --path fluidsim-runs
python3 scripts/budget_summary.py --path fluidsim-runs
```

Confirm exact filenames and growth. FluidSim 0.9 defaults to
`state_phys_t*.nc` for physical states; spectra remain HDF5.

## 6. Representative scientific pilot

Increase only enough to exercise the intended:

- Initial-condition path.
- Forcing type and injection normalization.
- Solver-specific state and outputs.
- FFT backend.
- Checkpoint and restart.
- Analysis code.

During and after the pilot, check:

- CFL and `deltat` history against all relevant wave/advection/diffusion limits.
- Divergence or other constraints.
- Energy/enstrophy/scalar/potential-energy budgets as appropriate.
- Measured forcing input and dissipation.
- Spectral tails and dealiasing contamination.
- Runtime, peak RSS, per-rank imbalance, file count, and disk growth.
- NaN/Inf, stalled advancement, unexpected truncation, and incomplete files.

A passing pilot permits planning a refinement study; it does not validate a
production run.

## 7. Running a reviewed serial plan

The generated script is deliberately gated:

```bash
python3 run.py
python3 run.py --execute --acknowledge-config-id REVIEWED_CONFIG_ID
```

The first command is dry-run only. The second is a real simulation and must be
issued by the user or approved operator after reviewing limits and output
destination.

Never silently increase resolution, duration, save frequency, rank count, or
wall time after approval.

## 8. Read-only loading

Use the lightweight loader:

```python
from fluidsim import load_sim_for_plot

sim = load_sim_for_plot(
    "run-directory",
    merge_missing_params=False,
    hide_stdout=True,
)
```

Official 0.9 source shows that it:

- Loads solver and parameters from the result directory.
- Sets a constant initialization and coarse operator.
- Sets `NEW_DIR_RESULTS = False`.
- Sets `output.HAS_TO_SAVE = False` and `ONLINE_PLOT_OK = False`.
- Selects default/sequential FFT for plotting.
- Can merge missing defaults for older runs when explicitly requested.

`merge_missing_params=True` helps load old metadata but does not prove that an
old result is scientifically or numerically equivalent under the new version.

## 9. State-bearing loading

```python
from fluidsim import load_state_phys_file

sim = load_state_phys_file(
    "run-directory",
    t_approx="last",
    modif_save_params=True,
    merge_missing_params=False,
    init_with_initialized_state=True,
    hide_stdout=True,
)
```

This constructs a full-resolution operator and loads state; it can be expensive.
With the default `modif_save_params=True`, saving and online plotting are
disabled. Loading a state object is not the same as approving a restart.

## 10. Reviewed Python restart

First compare metadata:

```bash
python3 scripts/restart_compatibility.py \
  --source state_phys_t001.000.nc \
  --target-config restart-config.json
```

Then, after approval:

```python
from fluidsim import load_for_restart

params, Simul = load_for_restart(
    "run-directory",
    t_approx="last",
    merge_missing_params=False,
)
params.time_stepping.t_end = 2.0
params.time_stepping.max_elapsed = "00:10:00"
params.NEW_DIR_RESULTS = True

sim = Simul(params)
sim.time_stepping.start()
```

`load_for_restart` reads parameters from `/info_simul/params`, sets
`init_fields.type = "from_file"`, points it to the selected state file, and by
default sets `NEW_DIR_RESULTS = False`. Explicitly choose append versus new
directory. Never append to an irreplaceable run without a backup and checksum.

Record:

- Parent run ID/path and state SHA-256.
- Selected state time/iteration.
- Parent and child package/backend/platform versions.
- Every changed parameter and justification.
- Append/new-directory decision.
- Forcing state continuity.
- Child output inventory and lock/script/config hashes.

FluidSim 0.9.0 stores “state parameters” in restarting files. FluidSim 0.8.6
fixed incorrect restart of time-correlated forcing; old checkpoints need extra
review.

## 11. Upstream restart CLI

Safe first action:

```bash
fluidsim-restart --only-check run-directory --t_end 2.0
```

Current options include `--only-check`, `--only-init`, `--new-dir-results`,
`--t_approx`, target/additive time or iteration bounds,
`--merge-missing-params`, and `--max-elapsed`.

Avoid `--modify-params` with any untrusted or generated text. Official source
passes that string to Python code execution. The bundled generator never emits
this option.

The CLI does not supply scheduler resource limits. Running it under MPI or a
scheduler remains a separate, explicit operational action.

## 12. Resolution changes

Do not change `oper.nx/ny/nz` and treat an old state file as directly compatible.
FluidSim provides:

```bash
fluidsim-modif-resolution run-directory 5/4
```

This creates a new state at modified resolution. Before use:

- Inventory free memory and disk; interpolation/FFT can be expensive.
- Preserve the original state.
- Record coefficient, source/output hashes, and implementation version.
- Check domain, state keys, normalization, and constraints.
- Treat the child as a new numerical experiment.
- Re-run transient, budget, spectral, and refinement checks.

Do not run this automatically or on a large state by default.

## 13. MPI/HPC handoff

After a serial pilot:

1. Ask the site scheduler for the intended allocation; never submit from this
   skill.
2. Verify the pinned MPI/FluidFFT environment inside that allocation.
3. Run a manually launched tiny two-rank smoke.
4. Benchmark candidate FFT methods on representative small shapes.
5. Confirm decomposition compatibility and local array sizes.
6. Set explicit process/thread affinity.
7. Set memory/rank, wall time, scratch, output quota, and signal/checkpoint
   behavior.
8. Use a short restartable pilot before scale-up.

The 2019 FluidSim/FluidFFT performance results are hardware- and shape-specific.
Do not extrapolate their wall times or fastest backend to another cluster.

## Failure and interruption handling

- Preserve logs and last complete checkpoint.
- Treat a signal-terminated or wall-time-limited run as incomplete until the
  checkpoint is inventoried and validated.
- Do not pick the lexically latest file without checking its time, iteration,
  HDF5 readability, and checksum.
- Never overwrite the parent state during recovery.
- Re-run the compatibility checker before every continuation.
- Explain any budget discontinuity at the restart boundary.

## Sources (verified 2026-07-23)

- [FluidSim user tutorial](https://fluidsim.readthedocs.io/en/latest/ipynb/tuto_user.html).
- [Restart and resolution change](https://fluidsim.readthedocs.io/en/latest/ipynb/restart_modif_resol.html).
- [FluidSim load/restart source](https://github.com/fluiddyn/fluidsim/blob/branch/default/fluidsim/util/util.py).
- [Restart CLI source](https://fluidsim.readthedocs.io/en/latest/_modules/fluidsim_core/scripts/restart.html).
- [FluidSim 0.9 release notes](https://fluidsim.readthedocs.io/en/latest/changes.html).
- Mohanan et al., [FluidSim primary paper](https://doi.org/10.5334/jors.239),
  published 2019-04-26; performance claims are limited to its documented
  benchmark setup.

### `references/solvers.md`

# Solver registry and selection

## Do not select by name alone

A solver key only identifies an implementation. Before use, verify in the
solver's 0.9.0 API/source:

1. Governing equations and prognostic variables.
2. Dimensional or nondimensional parameter definitions.
3. Geometry and boundary conditions.
4. Spatial discretization, truncation, and dealiasing.
5. Time integration and stability constraints.
6. Initial-condition and forcing classes registered for that solver.
7. Conserved/dissipated quantities and output definitions.
8. Known validation examples and limits of applicability.

Most primary FluidSim package CFD solvers use periodic domains and Fourier
pseudospectral methods. They are not general wall-bounded, free-surface,
industrial-geometry, multiphase, compressible, or shock-capturing solvers.

## FluidSim 0.9.0 registry

The following keys/modules come from the official 0.9.0 `pyproject.toml` entry
points and were cross-checked with the installed pinned package.

### Cartesian fluid and wave solvers

| Key | Direct import | Scope to verify |
|---|---|---|
| `ns2d` | `fluidsim.solvers.ns2d.solver.Simul` | 2D incompressible Navier–Stokes |
| `ns2d.bouss` | `fluidsim.solvers.ns2d.bouss.solver.Simul` | 2D Boussinesq variant |
| `ns2d.strat` | `fluidsim.solvers.ns2d.strat.solver.Simul` | 2D stratified Boussinesq, constant `N` |
| `ns3d` | `fluidsim.solvers.ns3d.solver.Simul` | 3D incompressible Navier–Stokes |
| `ns3d.bouss` | `fluidsim.solvers.ns3d.bouss.solver.Simul` | 3D Boussinesq variant |
| `ns3d.strat` | `fluidsim.solvers.ns3d.strat.solver.Simul` | 3D stratified Boussinesq, constant `N` |
| `sw1l` | `fluidsim.solvers.sw1l.solver.Simul` | One-layer shallow-water equations |
| `sw1l.exactlin` | `fluidsim.solvers.sw1l.exactlin.solver.Simul` | SW1L exact-linear variant |
| `sw1l.modified` | `fluidsim.solvers.sw1l.modified.solver.Simul` | Modified SW1L equations |
| `sw1l.onlywaves` | `fluidsim.solvers.sw1l.onlywaves.solver.Simul` | SW1L wave-only variant |
| `plate2d` | `fluidsim.solvers.plate2d.solver.Simul` | 2D Föppl–von Kármán elastic plate |
| `waves2d` | `fluidsim.solvers.waves2d.solver.Simul` | 2D wave model |

`fvk` is **not** the current entry-point key. Use `plate2d` after verifying its
equations and parameters.

### Lower-dimensional models

| Key | Module |
|---|---|
| `ad1d` | `fluidsim.solvers.ad1d.solver` |
| `ad1d.pseudo_spect` | `fluidsim.solvers.ad1d.pseudo_spect.solver` |
| `burgers1d` | `fluidsim.solvers.burgers1d.solver` |
| `burgers1d.skew_sym` | `fluidsim.solvers.burgers1d.skew_sym.solver` |
| `nl1d` | `fluidsim.solvers.nl1d.solver` |
| `models0d.lorenz` | `fluidsim.solvers.models0d.lorenz.solver` |
| `models0d.predaprey` | `fluidsim.solvers.models0d.predaprey.solver` |

These are useful for model studies, testing, and teaching. Do not apply the
Cartesian CFD configuration schema mechanically to 0D/1D solvers.

### Spherical solvers

| Key | Module |
|---|---|
| `sphere.ns2d` | `fluidsim.solvers.sphere.ns2d.solver` |
| `sphere.sw1l` | `fluidsim.solvers.sphere.sw1l.solver` |

FluidSim 0.9.0 source contains these entry points, but the `sphere` optional
dependency is commented out in package metadata. Confirm and pin compatible
`fluidsht`/spherical-harmonic dependencies before import. Spherical resolution,
operators, geometry, and diagnostics differ from Cartesian `nx`/`ny` plans.

### Framework/base adapters

The registry also declares:

- `Base` → `fluidsim.base.solvers.base`
- `BasePS` → `fluidsim.base.solvers.pseudo_spect`
- `BaseSH` → `fluidsim.base.sphericalharmo.solver`
- `basil` → `fluidsim.base.basilisk.solver`
- `dedalus` → `fluidsim.base.dedalus.solver`

These are framework/base or external-interface entry points, not evidence that
all external runtimes are installed. Check the external project's current API,
license, and environment separately.

## Imports

Prefer direct imports in reproducible scripts:

```python
from fluidsim.solvers.ns3d.strat.solver import Simul

params = Simul.create_default_params()
```

FluidSim also supports registry lookup:

```python
from fluidsim import import_simul_class_from_key

Simul = import_simul_class_from_key("ns2d.strat")
```

Only pass a reviewed literal or a value checked against a fixed allowlist. Do not
derive module names or solver keys from untrusted text. The bundled generator
uses a static key-to-module map and never performs a dynamic import.

## Selection questions

### NS2D versus NS3D

- Dimensionality changes the equations and invariant/cascade structure; a 2D
  run is not a cheaper approximation to arbitrary 3D physics.
- NS3D memory and FFT communication grow rapidly. Estimate before
  instantiation.
- State keys, forcing normalization, spectra, and budget outputs differ.

### Boussinesq versus stratified

Do not use `.bouss` and `.strat` interchangeably. Inspect the solver equation
documentation, variable definitions, background state, buoyancy sign, `N`,
rotation, and energy definitions. Record dimensional mapping for buoyancy and
density variables.

### Shallow water

Verify the exact SW1L variant, layer-depth/height variable, wave speed
parameterization, Coriolis convention, potential-vorticity definition, and
whether the planned regime satisfies the model assumptions. A SW1L run does not
by itself validate tsunami or geophysical predictions.

### Elastic plate

Use `plate2d`, not the old `fvk` label. Verify plate parameters, forcing,
dissipation, dimensional scaling, and whether the output represents displacement,
velocity, or derived quantities.

## Default-parameter discovery

Every selected solver should be interrogated in the exact locked environment:

```python
from fluidsim.solvers.ns2d.solver import Simul

params = Simul.create_default_params()
print(params)
```

Use IPython completion or the generated parameter documentation. `ParamContainer`
prevents silently adding unknown attributes, but it does not establish that a
valid attribute is physically meaningful.

For NS2D 0.9.0, the pinned smoke test found:

- `oper`: `nx`, `ny`, `Lx`, `Ly`, `coef_dealiasing`,
  `truncation_shape`, `type_fft`, `NO_KY0`, `NO_SHEAR_MODES`.
- Time stepping: `USE_CFL`, `USE_T_END`, `cfl_coef`, `deltat0`,
  `deltat_max`, `it_end`, `max_elapsed`, `t_end`, `type_time_scheme`.
- Initial types advertised by the solver:
  `from_file`, `from_simul`, `in_script`, `constant`, `noise`, `jet`, `dipole`.
- Forcing types advertised:
  `in_script`, `in_script_coarse`, `pseudo_spectral`, `proportional`,
  `tcrandom`, `tcrandom_anisotropic`.

Do not generalize that list to other solvers.

## Evidence required before interpretation

For any solver:

- Map each code variable and coefficient to the stated model.
- Verify sign conventions, normalization, and Fourier conventions.
- Confirm periodicity and domain lengths.
- Check initial-condition constraints (for example divergence-free velocity).
- Check forcing injection in measured output, not only requested parameters.
- Check all relevant invariant/budget residuals.
- Inspect spectral support and dealiased tails.
- Repeat at refined grid and time step.
- Compare with a suitable independent benchmark.

## Sources (verified 2026-07-23)

- [FluidSim 0.9.0 package entry points](https://github.com/fluiddyn/fluidsim/blob/branch/default/pyproject.toml).
- [FluidSim solver API index](https://fluidsim.readthedocs.io/en/latest/generated/fluidsim.solvers.html).
- [NS2D solver API](https://fluidsim.readthedocs.io/en/latest/generated/fluidsim.solvers.ns2d.solver.html).
- [NS3D solver API](https://fluidsim.readthedocs.io/en/latest/generated/fluidsim.solvers.ns3d.solver.html).
- [FluidSim documentation overview](https://fluidsim.readthedocs.io/en/latest/).
- Mohanan et al., [FluidSim primary paper](https://doi.org/10.5334/jors.239),
  published 2019-04-26. Method and performance statements in this reference are
  limited to the implementations and benchmarks described there.

### `scripts/__init__.py`

```python
"""Bounded local planning and inspection tools for the FluidSim skill."""
```

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared dependency-free safety and JSON helpers for FluidSim skill CLIs."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
import sys
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path, PurePath
from typing import Any


SCHEMA_VERSION = "1.1"
MIB = 1024**2
GIB = 1024**3
MAX_JSON_BYTES = 4 * MIB
MAX_REPORT_BYTES = 8 * MIB
MAX_TEXT_BYTES = 256 * MIB
MAX_HDF5_BYTES = 8 * 1024 * GIB
MAX_FILES = 10_000
MAX_DATASETS = 100_000
MAX_ATTRIBUTES = 100_000
MAX_RECORDS = 2_000_000
MAX_GRID_POINTS = 2**48
MAX_DIMENSION = 131_072
MAX_OUTPUT_FILES = 1_000_000
MAX_CPU_CORES = 1_048_576
MAX_WALL_MINUTES = 10 * 365 * 24 * 60

_URI_PREFIXES = (
    "http:",
    "https:",
    "ftp:",
    "file:",
    "s3:",
    "gs:",
    "ssh:",
    "data:",
)
_SAFE_SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ToolError(ValueError):
    """Expected validation or local-I/O failure."""


def bounded_int(
    value: Any, *, name: str, minimum: int, maximum: int
) -> int:
    """Validate a non-boolean integer against fixed limits."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise ToolError(f"{name} must be an integer")
    if not minimum <= value <= maximum:
        raise ToolError(f"{name} must be between {minimum} and {maximum}")
    return value


def finite_float(
    value: Any,
    *,
    name: str,
    minimum: float | None = None,
    maximum: float | None = None,
    allow_none: bool = False,
) -> float | None:
    """Validate a finite JSON number."""

    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ToolError(f"{name} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ToolError(f"{name} must be a finite number")
    if minimum is not None and number < minimum:
        raise ToolError(f"{name} must be at least {minimum}")
    if maximum is not None and number > maximum:
        raise ToolError(f"{name} must be at most {maximum}")
    return number


def validate_keys(
    value: Mapping[str, Any],
    *,
    allowed: Iterable[str],
    required: Iterable[str] = (),
    context: str,
) -> None:
    """Reject unknown keys and require declared keys."""

    allowed_set = set(allowed)
    required_set = set(required)
    unknown = sorted(set(value) - allowed_set)
    missing = sorted(required_set - set(value))
    if unknown:
        raise ToolError(f"{context} contains unsupported keys: {', '.join(unknown)}")
    if missing:
        raise ToolError(f"{context} is missing keys: {', '.join(missing)}")


def require_mapping(value: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ToolError(f"{context} must be a JSON object")
    return value


def require_text(
    value: Any, *, name: str, minimum: int = 1, maximum: int = 2_000
) -> str:
    if not isinstance(value, str):
        raise ToolError(f"{name} must be a string")
    if not minimum <= len(value) <= maximum:
        raise ToolError(f"{name} length must be between {minimum} and {maximum}")
    if any(ord(character) < 32 and character not in "\t" for character in value):
        raise ToolError(f"{name} contains control characters")
    return value


def require_text_list(
    value: Any, *, name: str, minimum: int = 1, maximum: int = 100
) -> list[str]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ToolError(f"{name} must contain {minimum}..{maximum} strings")
    return [
        require_text(item, name=f"{name} item", minimum=1, maximum=1_000)
        for item in value
    ]


def safe_slug(value: Any, *, name: str) -> str:
    """Validate one local path component."""

    text = require_text(value, name=name, maximum=128)
    if not _SAFE_SLUG.fullmatch(text) or text in {".", ".."}:
        raise ToolError(
            f"{name} must use only letters, digits, '.', '_', or '-'"
        )
    return text


def safe_relative_path(
    value: Any,
    *,
    name: str,
    suffixes: Iterable[str] | None = None,
    allow_nested: bool = False,
) -> str:
    """Validate a local relative path without traversal or URI syntax."""

    text = require_text(value, name=name, maximum=512).strip()
    lowered = text.casefold()
    if (
        text.startswith(("~", "/", "\\"))
        or "://" in lowered
        or lowered.startswith(_URI_PREFIXES)
    ):
        raise ToolError(f"{name} must be a local relative path")
    path = PurePath(text)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ToolError(f"{name} must not contain traversal")
    if not allow_nested and len(path.parts) != 1:
        raise ToolError(f"{name} must be one path component")
    for part in path.parts:
        safe_slug(part, name=name)
    if suffixes is not None and not any(
        text.casefold().endswith(suffix.casefold()) for suffix in suffixes
    ):
        raise ToolError(f"{name} has an unsupported suffix")
    return text


def _reject_unsafe_path_text(value: str) -> None:
    stripped = value.strip()
    lowered = stripped.casefold()
    if not stripped or "\x00" in value:
        raise ToolError("path must be nonempty and contain no NUL byte")
    if (
        stripped.startswith("~")
        or "://" in lowered
        or lowered.startswith(_URI_PREFIXES)
    ):
        raise ToolError("only local filesystem paths are accepted")
    if ".." in PurePath(stripped).parts:
        raise ToolError("parent traversal is not accepted")


def _absolute_lexical(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path)))


def _reject_symlink_components(path: Path) -> None:
    absolute = _absolute_lexical(path)
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ToolError("a path component could not be inspected") from exc
        if stat.S_ISLNK(mode):
            raise ToolError("symlink path components are not accepted")


def checked_root(value: str | os.PathLike[str]) -> Path:
    """Resolve an existing, non-symlink local directory."""

    raw = os.fspath(value)
    _reject_unsafe_path_text(raw)
    supplied = _absolute_lexical(Path(raw))
    _reject_symlink_components(supplied)
    try:
        resolved = supplied.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise ToolError("root directory is not accessible") from exc
    if not stat.S_ISDIR(info.st_mode):
        raise ToolError("root must be a directory")
    return resolved


def _within_root(path: Path, root: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ToolError("path escapes the declared root") from exc


def checked_input(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    kind: str = "file",
    suffixes: Iterable[str] | None = None,
    max_bytes: int = MAX_HDF5_BYTES,
) -> Path:
    """Resolve a bounded local file or directory without following symlinks."""

    raw = os.fspath(value)
    _reject_unsafe_path_text(raw)
    root_path = checked_root(root)
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root_path / candidate
    candidate = _absolute_lexical(candidate)
    _reject_symlink_components(candidate)
    try:
        resolved = candidate.resolve(strict=True)
        info = resolved.stat()
    except OSError as exc:
        raise ToolError("input path is not accessible") from exc
    _within_root(resolved, root_path)
    if kind == "file" and not stat.S_ISREG(info.st_mode):
        raise ToolError("input must be a regular file")
    if kind == "dir" and not stat.S_ISDIR(info.st_mode):
        raise ToolError("input must be a directory")
    if kind == "any" and not (
        stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)
    ):
        raise ToolError("input must be a regular file or directory")
    if stat.S_ISREG(info.st_mode):
        if info.st_nlink != 1:
            raise ToolError("multiply linked input files are not accepted")
        if not 0 <= info.st_size <= max_bytes:
            raise ToolError("input file exceeds the configured byte limit")
        if suffixes is not None and not any(
            resolved.name.casefold().endswith(suffix.casefold())
            for suffix in suffixes
        ):
            raise ToolError("input file has an unsupported suffix")
    return resolved


def checked_output(
    value: str | os.PathLike[str],
    *,
    root: str | os.PathLike[str] = ".",
    suffixes: Iterable[str],
    force: bool = False,
) -> Path:
    """Resolve a safe local output file within root."""

    relative = safe_relative_path(
        os.fspath(value),
        name="output",
        suffixes=suffixes,
        allow_nested=True,
    )
    root_path = checked_root(root)
    candidate = _absolute_lexical(root_path / relative)
    parent = candidate.parent
    _reject_symlink_components(parent)
    try:
        parent = parent.resolve(strict=True)
    except OSError as exc:
        raise ToolError("output parent must already exist") from exc
    _within_root(parent, root_path)
    destination = parent / candidate.name
    if destination.exists():
        if destination.is_symlink() or not destination.is_file():
            raise ToolError("existing output is not a regular file")
        if not force:
            raise ToolError("refusing to overwrite existing output")
    return destination


def atomic_write(
    destination: Path, payload: bytes, *, force: bool = False
) -> None:
    """Write a private file atomically without creating parent directories."""

    if len(payload) > MAX_REPORT_BYTES:
        raise ToolError("generated output exceeds the hard report-size limit")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        if destination.exists() and not force:
            raise ToolError("refusing to overwrite existing output")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _reject_json_constant(value: str) -> None:
    raise ToolError(f"non-finite JSON number is not accepted: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ToolError(f"duplicate JSON key is not accepted: {key}")
        result[key] = value
    return result


def load_json(path: Path, *, max_bytes: int = MAX_JSON_BYTES) -> Any:
    """Load bounded strict UTF-8 JSON."""

    if path.stat().st_size > max_bytes:
        raise ToolError("JSON input exceeds the parsing limit")
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(
                handle,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_json_constant,
            )
    except ToolError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ToolError("input is not bounded, valid UTF-8 JSON") from exc


def strict_json_loads(text: str) -> Any:
    try:
        return json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except ToolError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ToolError("record is not strict JSON") from exc


def json_bytes(document: Any) -> bytes:
    try:
        payload = (
            json.dumps(
                document,
                allow_nan=False,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ToolError("report cannot be serialized as strict JSON") from exc
    if len(payload) > MAX_REPORT_BYTES:
        raise ToolError("report exceeds the hard report-size limit")
    return payload


def emit_json(document: Any) -> None:
    sys.stdout.buffer.write(json_bytes(document))


def fail_json(tool: str, exc: Exception) -> int:
    emit_json(
        {
            "error": type(exc).__name__,
            "message": str(exc)[:500],
            "ok": False,
            "tool": tool,
        }
    )
    return 2


def sha256_file(path: Path, *, max_bytes: int) -> str | None:
    """Hash a regular file when it is within an explicit bound."""

    size = path.stat().st_size
    if size > max_bytes:
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(MIB), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_local_files(
    path: Path,
    *,
    suffixes: Iterable[str] | None,
    max_files: int,
    recursive: bool = True,
) -> list[Path]:
    """List bounded regular files without traversing symlinks."""

    bounded_int(max_files, name="max_files", minimum=1, maximum=MAX_FILES)
    if path.is_file():
        candidates = [path]
    else:
        candidates = []
        stack = [path]
        while stack:
            directory = stack.pop()
            try:
                entries = sorted(
                    os.scandir(directory), key=lambda entry: entry.name.casefold()
                )
            except OSError as exc:
                raise ToolError("directory cannot be scanned") from exc
            for entry in entries:
                try:
                    if entry.is_symlink():
                        raise ToolError("symlinks in scanned directories are rejected")
                    if entry.is_dir(follow_symlinks=False):
                        if recursive:
                            stack.append(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        file_path = Path(entry.path)
                        info = file_path.stat()
                        if info.st_nlink != 1:
                            raise ToolError(
                                "multiply linked files in scanned directories are rejected"
                            )
                        candidates.append(file_path)
                        if len(candidates) > max_files:
                            raise ToolError("file-count limit exceeded")
                except OSError as exc:
                    raise ToolError("directory entry cannot be inspected") from exc
    if suffixes is None:
        return candidates
    lowered = tuple(suffix.casefold() for suffix in suffixes)
    return [
        candidate
        for candidate in candidates
        if candidate.name.casefold().endswith(lowered)
    ]


def relative_display(path: Path, root: Path) -> str:
    """Return a bounded path relative to the caller-declared root."""

    try:
        relative = path.relative_to(root)
    except ValueError:
        return "<outside-root>"
    text = relative.as_posix()
    return text[:512]
```

### `scripts/_schema.py`

```python
#!/usr/bin/env python3
"""Static FluidSim 0.9 configuration schema and scientific guardrails."""

from __future__ import annotations

import re
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

try:
    from ._common import (
        MAX_CPU_CORES,
        MAX_DIMENSION,
        MAX_GRID_POINTS,
        MAX_OUTPUT_FILES,
        MAX_WALL_MINUTES,
        ToolError,
        bounded_int,
        finite_float,
        require_mapping,
        require_text,
        require_text_list,
        safe_relative_path,
        safe_slug,
        validate_keys,
    )
except ImportError:  # Direct script execution.
    from _common import (
        MAX_CPU_CORES,
        MAX_DIMENSION,
        MAX_GRID_POINTS,
        MAX_OUTPUT_FILES,
        MAX_WALL_MINUTES,
        ToolError,
        bounded_int,
        finite_float,
        require_mapping,
        require_text,
        require_text_list,
        safe_relative_path,
        safe_slug,
        validate_keys,
    )


FLUIDSIM_VERSION = "0.9.0"
FLUIDFFT_VERSION = "0.4.5"
PYFFTW_VERSION = "0.15.1"
MPI4PY_VERSION = "4.1.2"
REVIEW_DATE = "2026-07-23"

# Static allowlist from FluidSim 0.9.0 pyproject entry points. No module name is
# ever derived from user text.
SOLVER_IMPORTS = {
    "ad1d": "fluidsim.solvers.ad1d.solver",
    "ad1d.pseudo_spect": "fluidsim.solvers.ad1d.pseudo_spect.solver",
    "burgers1d": "fluidsim.solvers.burgers1d.solver",
    "burgers1d.skew_sym": "fluidsim.solvers.burgers1d.skew_sym.solver",
    "models0d.lorenz": "fluidsim.solvers.models0d.lorenz.solver",
    "models0d.predaprey": "fluidsim.solvers.models0d.predaprey.solver",
    "nl1d": "fluidsim.solvers.nl1d.solver",
    "ns2d": "fluidsim.solvers.ns2d.solver",
    "ns2d.bouss": "fluidsim.solvers.ns2d.bouss.solver",
    "ns2d.strat": "fluidsim.solvers.ns2d.strat.solver",
    "ns3d": "fluidsim.solvers.ns3d.solver",
    "ns3d.bouss": "fluidsim.solvers.ns3d.bouss.solver",
    "ns3d.strat": "fluidsim.solvers.ns3d.strat.solver",
    "plate2d": "fluidsim.solvers.plate2d.solver",
    "sphere.ns2d": "fluidsim.solvers.sphere.ns2d.solver",
    "sphere.sw1l": "fluidsim.solvers.sphere.sw1l.solver",
    "sw1l": "fluidsim.solvers.sw1l.solver",
    "sw1l.exactlin": "fluidsim.solvers.sw1l.exactlin.solver",
    "sw1l.modified": "fluidsim.solvers.sw1l.modified.solver",
    "sw1l.onlywaves": "fluidsim.solvers.sw1l.onlywaves.solver",
    "waves2d": "fluidsim.solvers.waves2d.solver",
}

# These Cartesian pseudospectral solvers share the parameter surface validated
# and rendered by the bundled tools.
CONFIG_SOLVER_DIMENSIONS = {
    "ns2d": 2,
    "ns2d.bouss": 2,
    "ns2d.strat": 2,
    "ns3d": 3,
    "ns3d.bouss": 3,
    "ns3d.strat": 3,
    "plate2d": 2,
    "sw1l": 2,
    "sw1l.exactlin": 2,
    "sw1l.modified": 2,
    "sw1l.onlywaves": 2,
    "waves2d": 2,
}

STATE_FIELD_COUNTS = {
    "ns2d": (3, 2),
    "ns2d.bouss": (4, 3),
    "ns2d.strat": (4, 3),
    "ns3d": (3, 4),
    "ns3d.bouss": (4, 5),
    "ns3d.strat": (4, 5),
    "plate2d": (3, 3),
    "sw1l": (3, 4),
    "sw1l.exactlin": (3, 4),
    "sw1l.modified": (3, 4),
    "sw1l.onlywaves": (3, 4),
    "waves2d": (2, 3),
}

TIME_SCHEMES = {
    "Euler",
    "Euler_phaseshift",
    "Euler_phaseshift_random",
    "RK2",
    "RK2_phaseshift",
    "RK2_phaseshift_exact",
    "RK2_phaseshift_random",
    "RK2_phaseshift_random_split",
    "RK2_trapezoid",
    "RK4",
}
FORCING_TYPES = {
    "in_script",
    "in_script_coarse",
    "pseudo_spectral",
    "proportional",
    "tcrandom",
    "tcrandom_anisotropic",
}
INIT_TYPES = {
    "constant",
    "dipole",
    "from_file",
    "from_simul",
    "in_script",
    "jet",
    "noise",
}
_DURATION = re.compile(r"^(?:\d{1,4}):[0-5]\d:[0-5]\d$")

TOP_LEVEL_KEYS = {
    "schema_version",
    "solver",
    "parameters",
    "scientific",
    "resources",
    "execution",
    "provenance",
}
PARAMETER_KEYS = {
    "NEW_DIR_RESULTS",
    "ONLY_COARSE_OPER",
    "N",
    "beta",
    "c2",
    "f",
    "nu_2",
    "nu_4",
    "nu_8",
    "nu_m4",
    "oper",
    "time_stepping",
    "init_fields",
    "forcing",
    "output",
    "short_name_type_run",
}
OPER_KEYS = {
    "Lx",
    "Ly",
    "Lz",
    "NO_KY0",
    "NO_SHEAR_MODES",
    "coef_dealiasing",
    "nx",
    "ny",
    "nz",
    "truncation_shape",
    "type_fft",
}
TIME_KEYS = {
    "USE_CFL",
    "USE_T_END",
    "cfl_coef",
    "deltat0",
    "deltat_max",
    "it_end",
    "max_elapsed",
    "phaseshift_random",
    "t_end",
    "type_time_scheme",
}
INIT_KEYS = {"type", "constant", "from_file", "noise"}
FORCING_KEYS = {
    "enable",
    "forcing_rate",
    "key_forced",
    "nkmax_forcing",
    "nkmin_forcing",
    "normalized",
    "random",
    "tcrandom",
    "type",
}
OUTPUT_KEYS = {
    "HAS_TO_SAVE",
    "ONLINE_PLOT_OK",
    "period_refresh_plots",
    "periods_plot",
    "periods_print",
    "periods_save",
    "phys_fields",
    "sub_directory",
}
PERIOD_SAVE_KEYS = {
    "increments",
    "phys_fields",
    "spatial_means",
    "spatiotemporal_spectra",
    "spect_energy_budg",
    "spectra",
    "spectra_multidim",
    "temporal_spectra",
}


def _record(
    target: list[dict[str, str]], code: str, message: str
) -> None:
    target.append({"code": code, "message": message})


def _validate_parameter_structure(parameters: Mapping[str, Any]) -> None:
    validate_keys(
        parameters, allowed=PARAMETER_KEYS, required={"oper", "time_stepping"}, context="parameters"
    )
    nested_specs: tuple[tuple[str, set[str]], ...] = (
        ("oper", OPER_KEYS),
        ("time_stepping", TIME_KEYS),
        ("init_fields", INIT_KEYS),
        ("forcing", FORCING_KEYS),
        ("output", OUTPUT_KEYS),
    )
    for name, keys in nested_specs:
        if name in parameters:
            validate_keys(
                require_mapping(parameters[name], context=f"parameters.{name}"),
                allowed=keys,
                context=f"parameters.{name}",
            )

    init = parameters.get("init_fields", {})
    if "constant" in init:
        validate_keys(
            require_mapping(init["constant"], context="init_fields.constant"),
            allowed={"value"},
            context="init_fields.constant",
        )
    if "from_file" in init:
        validate_keys(
            require_mapping(init["from_file"], context="init_fields.from_file"),
            allowed={"path"},
            context="init_fields.from_file",
        )
    if "noise" in init:
        validate_keys(
            require_mapping(init["noise"], context="init_fields.noise"),
            allowed={"length", "velo_max"},
            context="init_fields.noise",
        )

    forcing = parameters.get("forcing", {})
    nested_forcing = {
        "normalized": {"constant_rate_of", "type", "which_root"},
        "random": {"only_positive"},
        "tcrandom": {"time_correlation"},
    }
    for name, keys in nested_forcing.items():
        if name in forcing:
            validate_keys(
                require_mapping(forcing[name], context=f"forcing.{name}"),
                allowed=keys,
                context=f"forcing.{name}",
            )

    output = parameters.get("output", {})
    for name, keys in (
        ("periods_save", PERIOD_SAVE_KEYS),
        ("periods_print", {"print_stdout"}),
        ("periods_plot", {"phys_fields"}),
        ("phys_fields", {"field_to_plot", "file_with_it"}),
    ):
        if name in output:
            validate_keys(
                require_mapping(output[name], context=f"output.{name}"),
                allowed=keys,
                context=f"output.{name}",
            )

    time = parameters["time_stepping"]
    if "phaseshift_random" in time:
        validate_keys(
            require_mapping(
                time["phaseshift_random"], context="time_stepping.phaseshift_random"
            ),
            allowed={"nb_pairs", "nb_steps_compute_new_pair"},
            context="time_stepping.phaseshift_random",
        )


def validate_config(document: Any) -> dict[str, Any]:
    """Validate a strict FluidSim planning configuration without imports."""

    config = require_mapping(document, context="configuration")
    validate_keys(
        config,
        allowed=TOP_LEVEL_KEYS,
        required=TOP_LEVEL_KEYS,
        context="configuration",
    )
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if config["schema_version"] != "1.1":
        _record(errors, "schema_version", "schema_version must be '1.1'")

    solver = require_text(config["solver"], name="solver", maximum=80)
    if solver not in SOLVER_IMPORTS:
        _record(errors, "unknown_solver", "solver is not a FluidSim 0.9 entry-point key")
    if solver not in CONFIG_SOLVER_DIMENSIONS:
        _record(
            errors,
            "unsupported_parameter_profile",
            "bundled config tools cover Cartesian FluidSim CFD solver profiles only",
        )

    parameters = require_mapping(config["parameters"], context="parameters")
    _validate_parameter_structure(parameters)
    oper = require_mapping(parameters["oper"], context="parameters.oper")
    time = require_mapping(
        parameters["time_stepping"], context="parameters.time_stepping"
    )

    dimension = CONFIG_SOLVER_DIMENSIONS.get(solver)
    dimensions: list[int] = []
    if dimension is not None:
        required_axes = ("x", "y", "z")[:dimension]
        for axis in required_axes:
            n_key, length_key = f"n{axis}", f"L{axis}"
            if n_key not in oper or length_key not in oper:
                _record(
                    errors,
                    "incomplete_grid",
                    f"oper requires {n_key} and {length_key} for {solver}",
                )
                continue
            try:
                size = bounded_int(
                    oper[n_key],
                    name=f"oper.{n_key}",
                    minimum=2,
                    maximum=MAX_DIMENSION,
                )
                dimensions.append(size)
                finite_float(
                    oper[length_key], name=f"oper.{length_key}", minimum=1e-15
                )
            except ToolError as exc:
                _record(errors, "invalid_grid", str(exc))
        for axis in ("x", "y", "z")[dimension:]:
            if f"n{axis}" in oper or f"L{axis}" in oper:
                _record(
                    errors,
                    "extra_grid_axis",
                    f"{solver} does not use Cartesian {axis}-axis grid fields",
                )
        if dimensions:
            points = 1
            for size in dimensions:
                points *= size
            if points > MAX_GRID_POINTS:
                _record(errors, "grid_too_large", "grid-point product exceeds hard bound")
    if "coef_dealiasing" not in oper:
        _record(errors, "missing_dealiasing", "oper.coef_dealiasing must be explicit")
    else:
        try:
            coefficient = finite_float(
                oper["coef_dealiasing"],
                name="oper.coef_dealiasing",
                minimum=1e-12,
                maximum=1.0,
            )
            if coefficient is not None and coefficient > 2 / 3 + 1e-12:
                _record(
                    warnings,
                    "dealiasing_above_two_thirds",
                    "justify truncation above 2/3 or use a verified phase-shift scheme",
                )
        except ToolError as exc:
            _record(errors, "invalid_dealiasing", str(exc))
    if not isinstance(oper.get("type_fft", "default"), str):
        _record(errors, "invalid_fft_method", "oper.type_fft must be a string")

    required_time = {
        "USE_CFL",
        "USE_T_END",
        "cfl_coef",
        "deltat0",
        "deltat_max",
        "max_elapsed",
        "t_end",
        "type_time_scheme",
    }
    missing_time = sorted(required_time - set(time))
    if missing_time:
        _record(
            errors,
            "incomplete_time_bounds",
            f"time_stepping must explicitly set: {', '.join(missing_time)}",
        )
    else:
        if not isinstance(time["USE_CFL"], bool) or not isinstance(
            time["USE_T_END"], bool
        ):
            _record(errors, "invalid_time_flags", "USE_CFL and USE_T_END must be booleans")
        try:
            finite_float(time["deltat0"], name="deltat0", minimum=1e-15)
            finite_float(time["deltat_max"], name="deltat_max", minimum=1e-15)
            finite_float(time["t_end"], name="t_end", minimum=0.0)
            if time["USE_CFL"]:
                finite_float(
                    time["cfl_coef"], name="cfl_coef", minimum=1e-6, maximum=2.0
                )
        except ToolError as exc:
            _record(errors, "invalid_time_bound", str(exc))
        if not isinstance(time["max_elapsed"], str) or not _DURATION.fullmatch(
            time["max_elapsed"]
        ):
            _record(
                errors,
                "invalid_max_elapsed",
                "max_elapsed must use bounded HH:MM:SS text",
            )
        if time["type_time_scheme"] not in TIME_SCHEMES:
            _record(errors, "unknown_time_scheme", "unsupported FluidSim 0.9 time scheme")
        if not time["USE_T_END"]:
            _record(
                warnings,
                "iteration_termination",
                "USE_T_END is false; verify it_end is explicit and bounded",
            )

    for key in ("nu_2", "nu_4", "nu_8", "nu_m4"):
        if key in parameters:
            try:
                finite_float(parameters[key], name=key, minimum=0.0)
            except ToolError as exc:
                _record(errors, "invalid_dissipation", str(exc))

    init = require_mapping(parameters.get("init_fields", {}), context="init_fields")
    init_type = init.get("type")
    if init_type not in INIT_TYPES:
        _record(errors, "unknown_initialization", "init_fields.type is not recognized")
    if init_type == "from_file":
        try:
            source = require_mapping(init.get("from_file"), context="from_file")
            safe_relative_path(
                source.get("path"),
                name="init_fields.from_file.path",
                suffixes={".nc", ".h5", ".hdf5"},
                allow_nested=True,
            )
        except ToolError as exc:
            _record(errors, "unsafe_restart_path", str(exc))

    forcing = require_mapping(parameters.get("forcing", {}), context="forcing")
    forcing_enabled = forcing.get("enable", False)
    if not isinstance(forcing_enabled, bool):
        _record(errors, "invalid_forcing_enable", "forcing.enable must be a boolean")
    if forcing_enabled:
        if forcing.get("type") not in FORCING_TYPES:
            _record(errors, "unknown_forcing", "forcing.type is not recognized")
        for key in ("forcing_rate", "nkmin_forcing", "nkmax_forcing"):
            if key not in forcing:
                _record(errors, "incomplete_forcing", f"forcing.{key} must be explicit")
        try:
            finite_float(
                forcing.get("forcing_rate"), name="forcing_rate", minimum=0.0
            )
            minimum_k = finite_float(
                forcing.get("nkmin_forcing"), name="nkmin_forcing", minimum=0.0
            )
            maximum_k = finite_float(
                forcing.get("nkmax_forcing"), name="nkmax_forcing", minimum=0.0
            )
            if (
                minimum_k is not None
                and maximum_k is not None
                and maximum_k < minimum_k
            ):
                _record(errors, "forcing_band", "nkmax_forcing is below nkmin_forcing")
        except ToolError as exc:
            _record(errors, "invalid_forcing", str(exc))
        if forcing.get("type") == "tcrandom":
            tcrandom = forcing.get("tcrandom")
            if not isinstance(tcrandom, Mapping) or "time_correlation" not in tcrandom:
                _record(
                    errors,
                    "missing_time_correlation",
                    "forcing.tcrandom.time_correlation must be explicit",
                )

    output = require_mapping(parameters.get("output", {}), context="output")
    for key in ("HAS_TO_SAVE", "ONLINE_PLOT_OK"):
        if key not in output or not isinstance(output[key], bool):
            _record(errors, "output_flag", f"output.{key} must be an explicit boolean")
    try:
        safe_slug(output.get("sub_directory"), name="output.sub_directory")
    except ToolError as exc:
        _record(errors, "unsafe_output_subdirectory", str(exc))
    periods_save = output.get("periods_save")
    if not isinstance(periods_save, Mapping):
        _record(errors, "missing_output_periods", "output.periods_save must be explicit")
    else:
        for key, value in periods_save.items():
            try:
                finite_float(value, name=f"periods_save.{key}", minimum=0.0)
            except ToolError as exc:
                _record(errors, "invalid_output_period", str(exc))
    if output.get("ONLINE_PLOT_OK"):
        _record(
            warnings,
            "online_plotting",
            "disable online plotting for unattended/HPC runs",
        )
    if output.get("HAS_TO_SAVE") and isinstance(periods_save, Mapping):
        if float(periods_save.get("phys_fields", 0.0)) <= 0:
            _record(
                warnings,
                "no_restart_checkpoint",
                "physical-field saves are disabled, so no new restart checkpoint is planned",
            )

    scientific = require_mapping(config["scientific"], context="scientific")
    scientific_required = {
        "units_or_nondimensionalization",
        "boundary_conditions",
        "initial_conditions",
        "forcing",
        "resolution_and_dealiasing",
        "timestep_and_cfl",
        "conservation_and_budgets",
        "convergence_and_refinement",
        "acceptance_criteria",
    }
    validate_keys(
        scientific,
        allowed=scientific_required,
        required=scientific_required,
        context="scientific",
    )
    for key in scientific_required - {"conservation_and_budgets", "acceptance_criteria"}:
        require_text(scientific[key], name=f"scientific.{key}", maximum=2_000)
    require_text_list(
        scientific["conservation_and_budgets"],
        name="scientific.conservation_and_budgets",
    )
    require_text_list(
        scientific["acceptance_criteria"], name="scientific.acceptance_criteria"
    )
    if "periodic" not in scientific["boundary_conditions"].casefold():
        _record(
            errors,
            "boundary_conditions",
            "Cartesian bundled pseudospectral solver plans must state periodic boundaries",
        )

    resources = require_mapping(config["resources"], context="resources")
    resource_keys = {
        "cpu_cores",
        "mpi_ranks",
        "threads_per_rank",
        "ram_gib",
        "disk_gib",
        "wall_time_minutes",
        "max_output_files",
    }
    validate_keys(
        resources,
        allowed=resource_keys,
        required=resource_keys,
        context="resources",
    )
    try:
        cores = bounded_int(
            resources["cpu_cores"],
            name="cpu_cores",
            minimum=1,
            maximum=MAX_CPU_CORES,
        )
        ranks = bounded_int(
            resources["mpi_ranks"],
            name="mpi_ranks",
            minimum=1,
            maximum=MAX_CPU_CORES,
        )
        threads = bounded_int(
            resources["threads_per_rank"],
            name="threads_per_rank",
            minimum=1,
            maximum=MAX_CPU_CORES,
        )
        finite_float(resources["ram_gib"], name="ram_gib", minimum=0.001)
        finite_float(resources["disk_gib"], name="disk_gib", minimum=0.001)
        bounded_int(
            resources["wall_time_minutes"],
            name="wall_time_minutes",
            minimum=1,
            maximum=MAX_WALL_MINUTES,
        )
        bounded_int(
            resources["max_output_files"],
            name="max_output_files",
            minimum=1,
            maximum=MAX_OUTPUT_FILES,
        )
        if ranks * threads > cores:
            _record(
                errors,
                "cpu_oversubscription",
                "mpi_ranks * threads_per_rank exceeds cpu_cores",
            )
    except ToolError as exc:
        _record(errors, "invalid_resource_bound", str(exc))

    execution = require_mapping(config["execution"], context="execution")
    execution_keys = {"mode", "output_root", "random_seed", "script_name"}
    validate_keys(
        execution,
        allowed=execution_keys,
        required=execution_keys,
        context="execution",
    )
    mode = execution["mode"]
    if mode not in {"serial", "mpi-preview"}:
        _record(errors, "execution_mode", "mode must be serial or mpi-preview")
    try:
        safe_slug(execution["output_root"], name="execution.output_root")
        safe_relative_path(
            execution["script_name"],
            name="execution.script_name",
            suffixes={".py"},
        )
        bounded_int(
            execution["random_seed"],
            name="random_seed",
            minimum=0,
            maximum=2**32 - 1,
        )
    except ToolError as exc:
        _record(errors, "invalid_execution", str(exc))
    if mode == "serial" and resources.get("mpi_ranks") != 1:
        _record(errors, "serial_ranks", "serial mode requires mpi_ranks = 1")
    if mode == "mpi-preview" and isinstance(resources.get("mpi_ranks"), int):
        if resources["mpi_ranks"] < 2:
            _record(errors, "mpi_ranks", "mpi-preview requires at least two ranks")

    provenance = require_mapping(config["provenance"], context="provenance")
    provenance_keys = {
        "config_id",
        "created_utc",
        "dependency_lock_sha256",
        "fluidfft",
        "fluidsim",
        "python",
        "restart",
    }
    validate_keys(
        provenance,
        allowed=provenance_keys,
        required={
            "config_id",
            "created_utc",
            "dependency_lock_sha256",
            "fluidfft",
            "fluidsim",
            "python",
        },
        context="provenance",
    )
    for key in (
        "config_id",
        "created_utc",
        "dependency_lock_sha256",
        "fluidfft",
        "fluidsim",
        "python",
    ):
        require_text(provenance[key], name=f"provenance.{key}", maximum=256)
    if provenance["fluidsim"] != FLUIDSIM_VERSION:
        _record(errors, "fluidsim_version", f"pin fluidsim to {FLUIDSIM_VERSION}")
    if provenance["fluidfft"] != FLUIDFFT_VERSION:
        _record(errors, "fluidfft_version", f"pin fluidfft to {FLUIDFFT_VERSION}")
    if "restart" in provenance:
        restart = require_mapping(provenance["restart"], context="provenance.restart")
        validate_keys(
            restart,
            allowed={"path", "sha256", "source_fluidsim"},
            required={"path", "sha256", "source_fluidsim"},
            context="provenance.restart",
        )
        safe_relative_path(
            restart["path"],
            name="provenance.restart.path",
            suffixes={".nc", ".h5", ".hdf5", ".json"},
            allow_nested=True,
        )
        if not re.fullmatch(r"[0-9a-f]{64}", str(restart["sha256"])):
            _record(errors, "restart_digest", "restart sha256 must be 64 lowercase hex")

    return {
        "errors": errors,
        "numerical_convergence_established": False,
        "ok": not errors,
        "physical_validity_established": False,
        "recognized_solver_keys": sorted(SOLVER_IMPORTS),
        "review_date": REVIEW_DATE,
        "schema_version": "1.1",
        "solver": solver,
        "warnings": warnings,
    }


def example_config() -> dict[str, Any]:
    """Return a bounded pilot configuration used by docs and tests."""

    return {
        "schema_version": "1.1",
        "solver": "ns2d",
        "parameters": {
            "nu_2": 0.001,
            "nu_4": 0.0,
            "nu_8": 0.0,
            "nu_m4": 0.0,
            "oper": {
                "nx": 32,
                "ny": 32,
                "Lx": 6.283185307179586,
                "Ly": 6.283185307179586,
                "coef_dealiasing": 0.6666666666666666,
                "truncation_shape": "cubic",
                "type_fft": "default",
            },
            "time_stepping": {
                "USE_CFL": True,
                "USE_T_END": True,
                "cfl_coef": 0.5,
                "deltat0": 0.001,
                "deltat_max": 0.01,
                "max_elapsed": "00:05:00",
                "t_end": 0.1,
                "type_time_scheme": "RK4",
            },
            "init_fields": {
                "type": "noise",
                "noise": {"length": 0.0, "velo_max": 0.01},
            },
            "forcing": {
                "enable": False,
                "type": "",
                "forcing_rate": 1.0,
                "nkmin_forcing": 4,
                "nkmax_forcing": 5,
                "key_forced": None,
            },
            "output": {
                "HAS_TO_SAVE": True,
                "ONLINE_PLOT_OK": False,
                "sub_directory": "bounded-pilot",
                "periods_save": {
                    "phys_fields": 0.05,
                    "spatial_means": 0.01,
                    "spectra": 0.05,
                    "spect_energy_budg": 0.0,
                    "increments": 0.0,
                    "spectra_multidim": 0.0,
                    "temporal_spectra": 0.0,
                    "spatiotemporal_spectra": 0.0,
                },
                "periods_print": {"print_stdout": 0.01},
                "periods_plot": {"phys_fields": 0.0},
                "phys_fields": {"field_to_plot": "rot", "file_with_it": False},
            },
        },
        "scientific": {
            "units_or_nondimensionalization": (
                "All quantities are nondimensionalized by stated L0 and U0 scales."
            ),
            "boundary_conditions": "Periodic in x and y.",
            "initial_conditions": (
                "Seeded low-amplitude noise; document spectrum and amplitude."
            ),
            "forcing": "No forcing in this pilot.",
            "resolution_and_dealiasing": (
                "32x32 pilot with cubic 2/3 truncation; not a production resolution."
            ),
            "timestep_and_cfl": (
                "Adaptive CFL with cfl_coef=0.5 and deltat_max=0.01."
            ),
            "conservation_and_budgets": [
                "Track energy and enstrophy balances including dissipation.",
                "Check divergence and spectral-tail contamination.",
            ],
            "convergence_and_refinement": (
                "Repeat at finer grids and smaller CFL/deltat_max before inference."
            ),
            "acceptance_criteria": [
                "No unexplained budget residual trend.",
                "Reported observables stable under planned refinement.",
            ],
        },
        "resources": {
            "cpu_cores": 1,
            "mpi_ranks": 1,
            "threads_per_rank": 1,
            "ram_gib": 2.0,
            "disk_gib": 1.0,
            "wall_time_minutes": 5,
            "max_output_files": 32,
        },
        "execution": {
            "mode": "serial",
            "output_root": "fluidsim-runs",
            "random_seed": 12345,
            "script_name": "run_ns2d.py",
        },
        "provenance": {
            "config_id": "replace-with-study-config-id",
            "created_utc": "2026-07-23T00:00:00Z",
            "dependency_lock_sha256": "replace-with-uv-lock-sha256",
            "fluidfft": FLUIDFFT_VERSION,
            "fluidsim": FLUIDSIM_VERSION,
            "python": "3.11",
        },
    }


def flatten_parameters(
    parameters: Mapping[str, Any], prefix: tuple[str, ...] = ()
) -> list[tuple[tuple[str, ...], Any]]:
    """Flatten validated parameter mappings into deterministic assignments."""

    flattened: list[tuple[tuple[str, ...], Any]] = []
    for key in sorted(parameters):
        value = parameters[key]
        path = (*prefix, key)
        if isinstance(value, Mapping):
            flattened.extend(flatten_parameters(value, path))
        else:
            flattened.append((path, value))
    return flattened


def normalized_copy(document: Any) -> dict[str, Any]:
    """Return an isolated JSON-compatible copy after successful validation."""

    report = validate_config(document)
    if not report["ok"]:
        messages = "; ".join(item["message"] for item in report["errors"][:5])
        raise ToolError(f"configuration is not valid: {messages}")
    return deepcopy(dict(document))
```

### `scripts/budget_summary.py`

```python
#!/usr/bin/env python3
"""Summarize bounded FluidSim scalar and spectral diagnostics."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any

try:
    from ._common import (
        MAX_FILES,
        MAX_RECORDS,
        MAX_TEXT_BYTES,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        relative_display,
        strict_json_loads,
    )
except ImportError:  # Direct script execution.
    from _common import (
        MAX_FILES,
        MAX_RECORDS,
        MAX_TEXT_BYTES,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        relative_display,
        strict_json_loads,
    )


TOOL = "fluidsim-budget-summary"
_ASSIGNMENT = re.compile(
    r"^\s*([A-Za-z][A-Za-z0-9_.-]{0,127})\s*=\s*"
    r"([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)\s*(?:$|;)"
)
_SPECTRAL_PREFIXES = (
    "budget",
    "diss",
    "flux",
    "forcing",
    "spectr",
    "transfer",
)
_HDF5_SUFFIXES = (".h5", ".hdf5", ".nc")


class OnlineStats:
    """Constant-memory finite scalar aggregation."""

    def __init__(self) -> None:
        self.count = 0
        self.first: float | None = None
        self.last: float | None = None
        self.minimum = math.inf
        self.maximum = -math.inf
        self.mean = 0.0

    def add(self, value: Any) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return
        number = float(value)
        if not math.isfinite(number):
            return
        if self.first is None:
            self.first = number
        self.last = number
        self.minimum = min(self.minimum, number)
        self.maximum = max(self.maximum, number)
        self.count += 1
        # Weighted form avoids overflowing a same-sign finite running sum.
        self.mean = self.mean * ((self.count - 1) / self.count) + number / self.count

    def report(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "first": self.first,
            "last": self.last,
            "max": self.maximum if self.count else None,
            "mean": self.mean if self.count and math.isfinite(self.mean) else None,
            "min": self.minimum if self.count else None,
        }


def _iter_text(path: Path, *, max_records: int):
    if path.stat().st_size > MAX_TEXT_BYTES:
        raise ToolError("scalar diagnostic exceeds the text-size limit")
    consumed = 0
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if line_number > max_records:
                raise ToolError("scalar diagnostic record limit exceeded")
            consumed += len(raw)
            if consumed > MAX_TEXT_BYTES or len(raw) > 1024**2:
                raise ToolError("scalar diagnostic line/byte limit exceeded")
            if b"\x00" in raw:
                raise ToolError("NUL byte in scalar diagnostic")
            try:
                yield line_number, raw.decode("utf-8").rstrip("\r\n")
            except UnicodeDecodeError as exc:
                raise ToolError("scalar diagnostic is not UTF-8") from exc


def summarize_scalar_file(path: Path, *, max_records: int) -> dict[str, Any]:
    metrics: dict[str, OnlineStats] = {}
    parsed_lines = 0
    json_lines = path.name.casefold().endswith(".json")
    for _, line in _iter_text(path, max_records=max_records):
        if not line.strip():
            continue
        if json_lines:
            record = strict_json_loads(line)
            if not isinstance(record, dict):
                raise ToolError("spatial_means JSON line must be an object")
            parsed_lines += 1
            for key, value in record.items():
                if not isinstance(key, str) or not re.fullmatch(
                    r"[A-Za-z][A-Za-z0-9_.-]{0,127}", key
                ):
                    continue
                metrics.setdefault(key, OnlineStats()).add(value)
        else:
            match = _ASSIGNMENT.match(line)
            if match is None:
                continue
            parsed_lines += 1
            key, text = match.groups()
            metrics.setdefault(key, OnlineStats()).add(float(text))
    return {
        "format": "json-lines" if json_lines else "FluidSim key-value text",
        "metrics": {
            key: metrics[key].report()
            for key in sorted(metrics)
            if metrics[key].count
        },
        "parsed_lines": parsed_lines,
        "raw_records_emitted": False,
    }


def _bounded_slice(shape: tuple[int, ...], maximum: int) -> tuple[Any, ...]:
    if not shape:
        return ()
    if len(shape) == 1:
        return (slice(0, min(shape[0], maximum)),)
    slices: list[Any] = [slice(max(0, shape[0] - 1), shape[0])]
    remaining = maximum
    for size in shape[1:]:
        take = min(size, max(1, remaining))
        slices.append(slice(0, take))
        remaining = max(1, remaining // max(1, take))
    return tuple(slices)


def _summarize_values(values: Any, *, complete_record: bool) -> dict[str, Any]:
    flat = values.reshape(-1)
    if flat.dtype.kind == "c":
        flat = abs(flat)
        statistic = "magnitude"
    else:
        statistic = "value"
    finite = flat[flat == flat]
    finite = finite[abs(finite) != math.inf]
    count = int(finite.size)

    def converted(operation: str) -> float | None:
        if not count:
            return None
        value = float(getattr(finite, operation)())
        return value if math.isfinite(value) else None

    return {
        "complete_latest_record": complete_record,
        "finite_values": count,
        "max": converted("max"),
        "mean": converted("mean"),
        "min": converted("min"),
        "sampled_values": int(flat.size),
        "statistic": statistic,
        "sum": converted("sum") if complete_record else None,
    }


def summarize_spectral_file(
    path: Path, *, max_datasets: int, max_values: int
) -> dict[str, Any]:
    try:
        import h5py  # Lazy optional dependency.
    except ImportError as exc:
        raise ToolError(
            "spectral summary requires optional h5py from the pinned environment"
        ) from exc

    results: dict[str, Any] = {}
    time_range = None
    external_links = 0
    try:
        with h5py.File(path, "r") as handle:
            if "times" in handle and isinstance(handle["times"], h5py.Dataset):
                times = handle["times"]
                if times.ndim == 1 and times.shape[0]:
                    time_range = [
                        float(times[0]),
                        float(times[times.shape[0] - 1]),
                    ]
            stack = [(handle, "/")]
            seen: set[int] = set()
            while stack:
                group, prefix = stack.pop()
                try:
                    address = int(h5py.h5o.get_info(group.id).addr)
                except (AttributeError, TypeError, ValueError):
                    address = hash(group.id)
                if address in seen:
                    continue
                seen.add(address)
                for name in sorted(group.keys(), reverse=True):
                    link = group.get(name, getlink=True)
                    if isinstance(link, h5py.ExternalLink):
                        external_links += 1
                        continue
                    if isinstance(link, h5py.SoftLink):
                        continue
                    obj = group.get(name, getlink=False)
                    object_path = f"/{name}" if prefix == "/" else f"{prefix}/{name}"
                    if isinstance(obj, h5py.Group):
                        stack.append((obj, object_path))
                        continue
                    if not isinstance(obj, h5py.Dataset):
                        continue
                    leaf = name.casefold()
                    if (
                        obj.dtype.kind not in "iufc"
                        or not leaf.startswith(_SPECTRAL_PREFIXES)
                    ):
                        continue
                    if len(results) >= max_datasets:
                        raise ToolError("spectral dataset-count limit exceeded")
                    shape = tuple(int(size) for size in obj.shape)
                    if not shape or math.prod(shape) == 0:
                        continue
                    selection = _bounded_slice(shape, max_values)
                    values = obj[selection]
                    latest_record_size = (
                        math.prod(shape[1:]) if len(shape) > 1 else shape[0]
                    )
                    results[object_path[:300]] = {
                        "dtype": str(obj.dtype)[:100],
                        "shape": list(shape),
                        **_summarize_values(
                            values,
                            complete_record=latest_record_size <= max_values,
                        ),
                    }
    except OSError as exc:
        return {
            "datasets": {},
            "external_links_followed": False,
            "external_links_not_followed": external_links,
            "hdf5_readable": False,
            "message": str(exc)[:300],
            "time_range": None,
        }
    return {
        "datasets": dict(sorted(results.items())),
        "external_links_followed": False,
        "external_links_not_followed": external_links,
        "hdf5_readable": True,
        "time_range": time_range,
    }


def summarize(
    path: Path,
    *,
    root: Path,
    max_files: int,
    max_records: int,
    max_datasets: int,
    max_values: int,
) -> dict[str, Any]:
    files = iter_local_files(
        path, suffixes=None, max_files=max_files, recursive=True
    )
    scalar: list[dict[str, Any]] = []
    spectra: list[dict[str, Any]] = []
    for file_path in files:
        lowered = file_path.name.casefold()
        if lowered in {"spatial_means.txt", "spatial_means.json"}:
            scalar.append(
                {
                    "path": relative_display(file_path, root),
                    "summary": summarize_scalar_file(
                        file_path, max_records=max_records
                    ),
                }
            )
        elif lowered.endswith(_HDF5_SUFFIXES) and lowered.startswith(
            ("spectra", "spect_energy", "spectra_multidim")
        ):
            spectra.append(
                {
                    "path": relative_display(file_path, root),
                    "summary": summarize_spectral_file(
                        file_path,
                        max_datasets=max_datasets,
                        max_values=max_values,
                    ),
                }
            )
    return {
        "arrays_fully_loaded": False,
        "interpretation": (
            "Descriptive diagnostics only. Budget closure, conservation, spectral "
            "resolution, stationarity, and convergence require solver-aware checks."
        ),
        "network_used": False,
        "numerical_convergence_established": False,
        "ok": bool(scalar or spectra),
        "physical_validity_established": False,
        "scalar_outputs": scalar,
        "spectral_outputs": spectra,
        "tool": TOOL,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize bounded local spatial means and latest spectral/budget "
            "hyperslabs. Large arrays are never loaded in full."
        )
    )
    parser.add_argument("--path", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-files", type=int, default=128)
    parser.add_argument("--max-records", type=int, default=200_000)
    parser.add_argument("--max-datasets", type=int, default=256)
    parser.add_argument("--max-values-per-dataset", type=int, default=4_096)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        max_files = bounded_int(
            args.max_files, name="max_files", minimum=1, maximum=MAX_FILES
        )
        max_records = bounded_int(
            args.max_records,
            name="max_records",
            minimum=1,
            maximum=MAX_RECORDS,
        )
        max_datasets = bounded_int(
            args.max_datasets,
            name="max_datasets",
            minimum=1,
            maximum=10_000,
        )
        max_values = bounded_int(
            args.max_values_per_dataset,
            name="max_values_per_dataset",
            minimum=1,
            maximum=65_536,
        )
        root = checked_root(args.root)
        path = checked_input(args.path, root=root, kind="any")
        report = summarize(
            path,
            root=root,
            max_files=max_files,
            max_records=max_records,
            max_datasets=max_datasets,
            max_values=max_values,
        )
        emit_json(report)
        return 0 if report["ok"] else 2
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/grid_resource_estimator.py`

```python
#!/usr/bin/env python3
"""Estimate bounded FluidSim grid memory and output storage envelopes."""

from __future__ import annotations

import argparse
import math
from typing import Any

try:
    from ._common import (
        GIB,
        ToolError,
        bounded_int,
        checked_input,
        emit_json,
        fail_json,
        finite_float,
        load_json,
    )
    from ._schema import (
        CONFIG_SOLVER_DIMENSIONS,
        STATE_FIELD_COUNTS,
        normalized_copy,
    )
except ImportError:  # Direct script execution.
    from _common import (
        GIB,
        ToolError,
        bounded_int,
        checked_input,
        emit_json,
        fail_json,
        finite_float,
        load_json,
    )
    from _schema import (
        CONFIG_SOLVER_DIMENSIONS,
        STATE_FIELD_COUNTS,
        normalized_copy,
    )


TOOL = "fluidsim-grid-resource-estimator"


def _records(t_end: float, period: float, maximum: int) -> int:
    if period <= 0:
        return 0
    return min(maximum, int(math.floor(t_end / period + 1e-12)) + 2)


def estimate(
    config: dict[str, Any],
    *,
    precision_bytes: int,
    workspace_factor: float,
    safety_factor: float,
    compression_ratio: float,
) -> dict[str, Any]:
    solver = config["solver"]
    dimension = CONFIG_SOLVER_DIMENSIONS[solver]
    parameters = config["parameters"]
    oper = parameters["oper"]
    axes = ("x", "y", "z")[:dimension]
    shape = [int(oper[f"n{axis}"]) for axis in axes]
    grid_points = math.prod(shape)
    spectral_shape = [*shape[:-1], shape[-1] // 2 + 1]
    spectral_points = math.prod(spectral_shape)

    real_fields, complex_fields = STATE_FIELD_COUNTS[solver]
    real_state_bytes = grid_points * real_fields * precision_bytes
    complex_state_bytes = spectral_points * complex_fields * 2 * precision_bytes
    resident_state_bytes = real_state_bytes + complex_state_bytes
    peak_bytes = math.ceil(
        resident_state_bytes * workspace_factor * safety_factor
    )

    output = parameters.get("output", {})
    periods = output.get("periods_save", {})
    time = parameters["time_stepping"]
    t_end = float(time["t_end"])
    file_limit = int(config["resources"]["max_output_files"])
    state_records = (
        _records(t_end, float(periods.get("phys_fields", 0.0)), file_limit)
        if output.get("HAS_TO_SAVE")
        else 0
    )
    spectra_records = (
        _records(t_end, float(periods.get("spectra", 0.0)), file_limit)
        if output.get("HAS_TO_SAVE")
        else 0
    )
    budget_records = (
        _records(
            t_end,
            float(periods.get("spect_energy_budg", 0.0)),
            file_limit,
        )
        if output.get("HAS_TO_SAVE")
        else 0
    )
    scalar_records = (
        _records(t_end, float(periods.get("spatial_means", 0.0)), file_limit)
        if output.get("HAS_TO_SAVE")
        else 0
    )

    snapshot_bytes = math.ceil(real_state_bytes / compression_ratio)
    state_storage = state_records * snapshot_bytes
    bins = sum(size // 2 + 1 for size in shape)
    spectra_storage = math.ceil(
        spectra_records * max(1, bins) * max(4, real_fields) * 8
        / compression_ratio
    )
    budget_storage = math.ceil(
        budget_records * max(1, bins) * max(6, complex_fields) * 8
        / compression_ratio
    )
    scalar_storage = scalar_records * 16 * 32
    metadata_storage = 4 * 1024**2 if output.get("HAS_TO_SAVE") else 0
    storage_bytes = (
        state_storage
        + spectra_storage
        + budget_storage
        + scalar_storage
        + metadata_storage
    )
    estimated_files = (
        state_records
        + (2 if spectra_records else 0)
        + (1 if budget_records else 0)
        + (1 if scalar_records else 0)
        + (4 if output.get("HAS_TO_SAVE") else 0)
    )

    resources = config["resources"]
    ram_bytes = float(resources["ram_gib"]) * GIB
    disk_bytes = float(resources["disk_gib"]) * GIB
    ranks = int(resources["mpi_ranks"])
    memory_ok = peak_bytes <= ram_bytes
    storage_ok = storage_bytes <= disk_bytes
    files_ok = estimated_files <= int(resources["max_output_files"])
    return {
        "assumptions": {
            "compression_ratio": compression_ratio,
            "complex_fields": complex_fields,
            "precision_bytes": precision_bytes,
            "real_fields": real_fields,
            "safety_factor": safety_factor,
            "spectra_and_budget_layout_is_approximate": True,
            "workspace_factor": workspace_factor,
        },
        "declared_bounds": {
            "cpu_cores": resources["cpu_cores"],
            "disk_gib": resources["disk_gib"],
            "max_output_files": resources["max_output_files"],
            "mpi_ranks": ranks,
            "ram_gib": resources["ram_gib"],
            "threads_per_rank": resources["threads_per_rank"],
            "wall_time_minutes": resources["wall_time_minutes"],
        },
        "estimates": {
            "estimated_output_files": estimated_files,
            "idealized_peak_bytes_per_rank": math.ceil(peak_bytes / ranks),
            "peak_memory_bytes": peak_bytes,
            "peak_memory_gib": peak_bytes / GIB,
            "resident_state_bytes": resident_state_bytes,
            "state_snapshot_bytes": snapshot_bytes,
            "state_snapshots": state_records,
            "storage_bytes": storage_bytes,
            "storage_gib": storage_bytes / GIB,
        },
        "grid": {
            "dimensions": dimension,
            "points": grid_points,
            "shape": shape,
            "spectral_points_estimate": spectral_points,
            "spectral_shape_estimate": spectral_shape,
        },
        "limits": {
            "files_within_bound": files_ok,
            "memory_within_bound": memory_ok,
            "storage_within_bound": storage_ok,
        },
        "notes": [
            "This is a conservative planning envelope, not a measured FluidSim allocation.",
            "FFT decomposition, backend buffers, Python overhead, diagnostics, and MPI imbalance are backend-specific.",
            "Runtime is not inferred from grid size; benchmark a tiny representative pilot on the target machine.",
            "A resource fit does not establish numerical convergence or physical validity.",
        ],
        "ok": memory_ok and storage_ok and files_ok,
        "runtime_estimated": False,
        "solver": solver,
        "tool": TOOL,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Estimate a conservative FluidSim memory/storage envelope from strict "
            "local JSON. No arrays are allocated and no package is imported."
        )
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--precision-bytes",
        type=int,
        choices=(4, 8),
        default=8,
        help="Real scalar bytes in planning model (default: 8).",
    )
    parser.add_argument(
        "--workspace-factor",
        type=float,
        default=8.0,
        help="Resident-state multiplier, 2..64 (default: 8).",
    )
    parser.add_argument(
        "--safety-factor",
        type=float,
        default=1.5,
        help="Additional margin, 1..10 (default: 1.5).",
    )
    parser.add_argument(
        "--compression-ratio",
        type=float,
        default=1.0,
        help="Optimistic output compression ratio, 1..20 (default: 1).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        bounded_int(
            args.precision_bytes,
            name="precision_bytes",
            minimum=4,
            maximum=8,
        )
        workspace = finite_float(
            args.workspace_factor,
            name="workspace_factor",
            minimum=2.0,
            maximum=64.0,
        )
        safety = finite_float(
            args.safety_factor,
            name="safety_factor",
            minimum=1.0,
            maximum=10.0,
        )
        compression = finite_float(
            args.compression_ratio,
            name="compression_ratio",
            minimum=1.0,
            maximum=20.0,
        )
        path = checked_input(
            args.config,
            root=args.root,
            kind="file",
            suffixes={".json"},
        )
        config = normalized_copy(load_json(path))
        report = estimate(
            config,
            precision_bytes=args.precision_bytes,
            workspace_factor=float(workspace),
            safety_factor=float(safety),
            compression_ratio=float(compression),
        )
        report["commands_executed"] = False
        report["arrays_allocated"] = False
        emit_json(report)
        return 0 if report["ok"] else 2
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/output_inventory.py`

```python
#!/usr/bin/env python3
"""Inventory bounded FluidSim output and HDF5/netCDF4 metadata lazily."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

try:
    from ._common import (
        MAX_ATTRIBUTES,
        MAX_DATASETS,
        MAX_FILES,
        MAX_HDF5_BYTES,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        relative_display,
    )
except ImportError:  # Direct script execution.
    from _common import (
        MAX_ATTRIBUTES,
        MAX_DATASETS,
        MAX_FILES,
        MAX_HDF5_BYTES,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        relative_display,
    )


TOOL = "fluidsim-output-inventory"
HDF5_SUFFIXES = (".h5", ".hdf5", ".nc")
SAFE_SCALAR_ATTRIBUTES = {
    "Lx",
    "Ly",
    "Lz",
    "class_name",
    "fluidfft",
    "fluidsim",
    "it",
    "module_name",
    "name_run",
    "nx",
    "ny",
    "nz",
    "solver",
    "time",
    "version",
}


def _clean_name(value: str) -> str:
    cleaned = "".join(
        character if character.isprintable() else "?" for character in value
    )
    return cleaned[:300]


def _scalar(value: Any) -> Any:
    """Convert a known scalar attribute without retaining arbitrary arrays."""

    if hasattr(value, "item"):
        try:
            value = value.item()
        except (TypeError, ValueError):
            return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[:300]
    if isinstance(value, str):
        return value[:300]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return None


def _attributes(
    obj: Any, *, count: list[int], max_attributes: int
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for name in sorted(obj.attrs):
        count[0] += 1
        if count[0] > max_attributes:
            raise ToolError("HDF5 attribute-count limit exceeded")
        identifier = obj.attrs.get_id(name)
        entry: dict[str, Any] = {
            "dtype": str(identifier.dtype)[:100],
            "name": _clean_name(str(name)),
            "shape": list(identifier.shape),
            "value": None,
        }
        if name in SAFE_SCALAR_ATTRIBUTES and identifier.shape == ():
            entry["value"] = _scalar(obj.attrs[name])
        result.append(entry)
    return result


def _object_address(h5py: Any, obj: Any) -> int:
    try:
        return int(h5py.h5o.get_info(obj.id).addr)
    except (AttributeError, TypeError, ValueError):
        return hash(obj.id)


def inspect_hdf5_metadata(
    path: Path,
    *,
    max_datasets: int,
    max_attributes: int,
    max_depth: int,
) -> dict[str, Any]:
    """Read only object/link metadata; never index a dataset."""

    try:
        import h5py  # Lazy optional dependency.
    except ImportError as exc:
        raise ToolError(
            "HDF5 inspection requires optional h5py; install the pinned FluidSim environment"
        ) from exc

    datasets: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    links = {"external_not_followed": 0, "soft_not_followed": 0}
    attribute_count = [0]
    try:
        with h5py.File(path, "r") as handle:
            stack: list[tuple[Any, str, int]] = [(handle, "/", 0)]
            seen_groups: set[int] = set()
            while stack:
                group, group_path, depth = stack.pop()
                address = _object_address(h5py, group)
                if address in seen_groups:
                    continue
                seen_groups.add(address)
                groups.append(
                    {
                        "attributes": _attributes(
                            group,
                            count=attribute_count,
                            max_attributes=max_attributes,
                        ),
                        "path": _clean_name(group_path),
                    }
                )
                if depth >= max_depth:
                    continue
                for name in sorted(group.keys(), reverse=True):
                    link = group.get(name, getlink=True)
                    child_path = (
                        f"/{name}" if group_path == "/" else f"{group_path}/{name}"
                    )
                    if isinstance(link, h5py.ExternalLink):
                        links["external_not_followed"] += 1
                        continue
                    if isinstance(link, h5py.SoftLink):
                        links["soft_not_followed"] += 1
                        continue
                    child = group.get(name, getlink=False)
                    if isinstance(child, h5py.Dataset):
                        if len(datasets) >= max_datasets:
                            raise ToolError("HDF5 dataset-count limit exceeded")
                        datasets.append(
                            {
                                "attributes": _attributes(
                                    child,
                                    count=attribute_count,
                                    max_attributes=max_attributes,
                                ),
                                "chunks": (
                                    list(child.chunks)
                                    if child.chunks is not None
                                    else None
                                ),
                                "compression": child.compression,
                                "dtype": str(child.dtype)[:100],
                                "path": _clean_name(child_path),
                                "shape": list(child.shape),
                                "storage_bytes": int(child.id.get_storage_size()),
                            }
                        )
                    elif isinstance(child, h5py.Group):
                        stack.append((child, child_path, depth + 1))
    except OSError as exc:
        return {
            "attributes": 0,
            "datasets": [],
            "groups": [],
            "hdf5_readable": False,
            "links": links,
            "message": str(exc)[:300],
        }
    return {
        "attributes": attribute_count[0],
        "datasets": datasets,
        "groups": groups,
        "hdf5_readable": True,
        "links": links,
    }


def _kind(path: Path) -> str:
    name = path.name.casefold()
    if name.startswith("state_phys"):
        return "physical_state"
    if name.startswith(("spectra", "spect_energy", "spectra_multidim")):
        return "spectral_output"
    if name.startswith("spatial_means"):
        return "scalar_output"
    if name in {"params_simul.xml", "info_solver.xml", "stdout.txt"}:
        return "provenance_or_log"
    if name.endswith(HDF5_SUFFIXES):
        return "hdf5_or_netcdf"
    return "other"


def inventory(
    path: Path,
    *,
    root: Path,
    max_files: int,
    max_hdf5_files: int,
    max_datasets: int,
    max_attributes: int,
    max_depth: int,
) -> dict[str, Any]:
    files = iter_local_files(
        path, suffixes=None, max_files=max_files, recursive=True
    )
    entries: list[dict[str, Any]] = []
    hdf5_entries: list[dict[str, Any]] = []
    total_bytes = 0
    for file_path in files:
        size = file_path.stat().st_size
        if size > MAX_HDF5_BYTES:
            raise ToolError("a file exceeds the hard inspection-size bound")
        total_bytes += size
        kind = _kind(file_path)
        entries.append(
            {
                "kind": kind,
                "path": relative_display(file_path, root),
                "size_bytes": size,
            }
        )
        if (
            file_path.name.casefold().endswith(HDF5_SUFFIXES)
            and len(hdf5_entries) < max_hdf5_files
        ):
            hdf5_entries.append(
                {
                    "metadata": inspect_hdf5_metadata(
                        file_path,
                        max_datasets=max_datasets,
                        max_attributes=max_attributes,
                        max_depth=max_depth,
                    ),
                    "path": relative_display(file_path, root),
                    "size_bytes": size,
                }
            )
    counts: dict[str, int] = {}
    for entry in entries:
        counts[entry["kind"]] = counts.get(entry["kind"], 0) + 1
    return {
        "arrays_loaded": False,
        "external_links_followed": False,
        "file_count": len(entries),
        "files": entries,
        "hdf5_files_inspected": len(hdf5_entries),
        "hdf5_metadata": hdf5_entries,
        "kind_counts": dict(sorted(counts.items())),
        "network_used": False,
        "ok": True,
        "root": ".",
        "total_bytes": total_bytes,
        "tool": TOOL,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory local FluidSim output. HDF5/netCDF4 datasets are described "
            "by shape/dtype/chunks only; array values and external links are not read."
        )
    )
    parser.add_argument("--path", required=True, help="Run directory or one file.")
    parser.add_argument("--root", default=".", help="Local I/O boundary.")
    parser.add_argument("--max-files", type=int, default=256)
    parser.add_argument("--max-hdf5-files", type=int, default=32)
    parser.add_argument("--max-datasets", type=int, default=2_000)
    parser.add_argument("--max-attributes", type=int, default=5_000)
    parser.add_argument("--max-depth", type=int, default=16)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        max_files = bounded_int(
            args.max_files, name="max_files", minimum=1, maximum=MAX_FILES
        )
        max_hdf5_files = bounded_int(
            args.max_hdf5_files,
            name="max_hdf5_files",
            minimum=0,
            maximum=MAX_FILES,
        )
        max_datasets = bounded_int(
            args.max_datasets,
            name="max_datasets",
            minimum=1,
            maximum=MAX_DATASETS,
        )
        max_attributes = bounded_int(
            args.max_attributes,
            name="max_attributes",
            minimum=1,
            maximum=MAX_ATTRIBUTES,
        )
        max_depth = bounded_int(
            args.max_depth, name="max_depth", minimum=1, maximum=64
        )
        root = checked_root(args.root)
        path = checked_input(args.path, root=root, kind="any")
        report = inventory(
            path,
            root=root,
            max_files=max_files,
            max_hdf5_files=max_hdf5_files,
            max_datasets=max_datasets,
            max_attributes=max_attributes,
            max_depth=max_depth,
        )
        emit_json(report)
        return 0
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/restart_compatibility.py`

```python
#!/usr/bin/env python3
"""Check FluidSim restart metadata against a validated target configuration."""

from __future__ import annotations

import argparse
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    from ._common import (
        GIB,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        load_json,
        relative_display,
        sha256_file,
        validate_keys,
    )
    from ._schema import FLUIDSIM_VERSION, SOLVER_IMPORTS, normalized_copy
except ImportError:  # Direct script execution.
    from _common import (
        GIB,
        ToolError,
        bounded_int,
        checked_input,
        checked_root,
        emit_json,
        fail_json,
        iter_local_files,
        load_json,
        relative_display,
        sha256_file,
        validate_keys,
    )
    from _schema import FLUIDSIM_VERSION, SOLVER_IMPORTS, normalized_copy


TOOL = "fluidsim-restart-compatibility"
_MODULE_TO_SOLVER = {module: key for key, module in SOLVER_IMPORTS.items()}
_STATE_SUFFIXES = (".nc", ".h5", ".hdf5")
_COMPATIBLE_OPER_KEYS = ("nx", "ny", "nz", "Lx", "Ly", "Lz")
_PHYSICS_KEYS = ("N", "beta", "c2", "f", "nu_2", "nu_4", "nu_8", "nu_m4")


def _safe_scalar(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (TypeError, ValueError):
            return None
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[:500]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value if not isinstance(value, str) else value[:500]
    return None


def _attrs(group: Any, names: tuple[str, ...]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in names:
        if name not in group.attrs:
            continue
        identifier = group.attrs.get_id(name)
        if identifier.shape != ():
            continue
        value = _safe_scalar(group.attrs[name])
        if value is not None:
            result[name] = value
    return result


def _find_state_file(path: Path) -> Path:
    if path.is_file():
        return path
    candidates = [
        item
        for item in iter_local_files(
            path, suffixes=_STATE_SUFFIXES, max_files=10_000, recursive=True
        )
        if item.name.casefold().startswith("state_phys")
    ]
    if not candidates:
        raise ToolError("no state_phys .nc/.h5 file found in restart directory")
    return sorted(candidates, key=lambda item: item.name)[-1]


def load_hdf5_state(path: Path, *, digest_limit: int) -> dict[str, Any]:
    """Read restart metadata and dataset names without reading field arrays."""

    try:
        import h5py  # Lazy optional dependency.
    except ImportError as exc:
        raise ToolError(
            "restart HDF5 inspection requires optional h5py from the pinned environment"
        ) from exc

    try:
        with h5py.File(path, "r") as handle:
            if "state_phys" not in handle or not isinstance(
                handle["state_phys"], h5py.Group
            ):
                raise ToolError("restart file has no /state_phys group")
            state_group = handle["state_phys"]
            state = {
                "datasets": sorted(
                    name
                    for name in state_group
                    if isinstance(state_group.get(name, getlink=False), h5py.Dataset)
                ),
                "iteration": _attrs(state_group, ("it",)).get("it"),
                "state_parameters_present": any(
                    name in handle
                    for name in ("state_params", "info_state", "state_parameters")
                ),
                "time": _attrs(state_group, ("time",)).get("time"),
            }
            parameters: dict[str, Any] = {}
            solver = None
            source_version = None
            if "info_simul" in handle:
                info = handle["info_simul"]
                if "params" in info:
                    params_group = info["params"]
                    parameters.update(_attrs(params_group, _PHYSICS_KEYS))
                    for child, keys in (
                        ("oper", _COMPATIBLE_OPER_KEYS + ("coef_dealiasing", "type_fft")),
                        (
                            "time_stepping",
                            ("t_end", "it_end", "type_time_scheme"),
                        ),
                        ("forcing", ("enable", "type", "forcing_rate")),
                    ):
                        if child in params_group:
                            parameters[child] = _attrs(params_group[child], keys)
                if "solver" in info:
                    solver_attrs = _attrs(
                        info["solver"],
                        ("module_name", "short_name", "version", "fluidsim"),
                    )
                    module_name = solver_attrs.get("module_name")
                    solver = _MODULE_TO_SOLVER.get(str(module_name), None)
                    source_version = solver_attrs.get(
                        "fluidsim", solver_attrs.get("version")
                    )
            # FluidSim 0.9 stores forcing state parameters in restart files. Their
            # exact group path can vary with extensions, so inspect object names only.
            names: list[str] = []
            handle.visit(names.append)
            state["state_parameters_present"] = state[
                "state_parameters_present"
            ] or any("state_params" in name for name in names)
    except OSError as exc:
        raise ToolError("restart file is not readable HDF5/netCDF4") from exc

    return {
        "parameters": parameters,
        "provenance": {
            "fluidfft": None,
            "fluidsim": source_version,
            "state_sha256": sha256_file(path, max_bytes=digest_limit),
        },
        "solver": solver,
        "state": state,
    }


def load_manifest(path: Path) -> dict[str, Any]:
    document = load_json(path)
    if not isinstance(document, Mapping):
        raise ToolError("restart manifest must be a JSON object")
    validate_keys(
        document,
        allowed={"schema_version", "solver", "parameters", "state", "provenance"},
        required={"schema_version", "solver", "parameters", "state", "provenance"},
        context="restart manifest",
    )
    if document["schema_version"] != "1.1":
        raise ToolError("restart manifest schema_version must be '1.1'")
    if document["solver"] not in SOLVER_IMPORTS:
        raise ToolError("restart manifest solver is unknown")
    parameters = document["parameters"]
    state = document["state"]
    provenance = document["provenance"]
    if not all(isinstance(item, Mapping) for item in (parameters, state, provenance)):
        raise ToolError("restart manifest parameters/state/provenance must be objects")
    validate_keys(
        state,
        allowed={"datasets", "iteration", "state_parameters_present", "time"},
        required={"datasets", "iteration", "state_parameters_present", "time"},
        context="restart manifest state",
    )
    validate_keys(
        provenance,
        allowed={"fluidfft", "fluidsim", "state_sha256"},
        required={"fluidfft", "fluidsim", "state_sha256"},
        context="restart manifest provenance",
    )
    if not isinstance(state["datasets"], list) or not all(
        isinstance(item, str) and 0 < len(item) <= 128 for item in state["datasets"]
    ):
        raise ToolError("restart manifest datasets must be bounded strings")
    digest = provenance["state_sha256"]
    if digest is not None and not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
        raise ToolError("restart manifest state_sha256 must be lowercase SHA-256")
    return {
        "parameters": dict(parameters),
        "provenance": dict(provenance),
        "solver": document["solver"],
        "state": dict(state),
    }


def _same(left: Any, right: Any) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        scale = max(1.0, abs(float(left)), abs(float(right)))
        return abs(float(left) - float(right)) <= 1e-12 * scale
    return left == right


def compare(source: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def add(target_list: list[dict[str, str]], code: str, message: str) -> None:
        target_list.append({"code": code, "message": message})

    if source.get("solver") is None:
        add(blockers, "missing_solver", "source solver metadata is unavailable")
    elif source["solver"] != target["solver"]:
        add(blockers, "solver_mismatch", "source and target solver keys differ")

    source_params = source.get("parameters", {})
    target_params = target["parameters"]
    source_oper = source_params.get("oper", {})
    target_oper = target_params.get("oper", {})
    for key in _COMPATIBLE_OPER_KEYS:
        if key not in target_oper:
            continue
        if key not in source_oper:
            add(warnings, "missing_grid_metadata", f"source oper.{key} is unavailable")
        elif not _same(source_oper[key], target_oper[key]):
            add(
                blockers,
                "grid_or_domain_mismatch",
                f"oper.{key} differs; use the reviewed resolution-change workflow",
            )
    for key in ("coef_dealiasing", "type_fft"):
        if key in source_oper and key in target_oper and not _same(
            source_oper[key], target_oper[key]
        ):
            add(
                warnings,
                "operator_change",
                f"oper.{key} changes across restart and requires justification",
            )

    for key in _PHYSICS_KEYS:
        if key in source_params and key in target_params and not _same(
            source_params[key], target_params[key]
        ):
            add(
                warnings,
                "physics_parameter_change",
                f"{key} changes across restart; reassess equations and budgets",
            )

    source_state = source.get("state", {})
    if not source_state.get("datasets"):
        add(blockers, "empty_state", "source contains no state datasets")
    source_time = source_state.get("time")
    target_end = target_params["time_stepping"].get("t_end")
    if isinstance(source_time, (int, float)) and isinstance(target_end, (int, float)):
        if float(target_end) <= float(source_time):
            add(blockers, "nonadvancing_end_time", "target t_end does not exceed state time")
    else:
        add(warnings, "missing_time", "source time or target t_end is unavailable")

    init = target_params.get("init_fields", {})
    if init.get("type") != "from_file":
        add(
            blockers,
            "target_not_from_file",
            "target init_fields.type must be 'from_file' for this restart plan",
        )

    source_provenance = source.get("provenance", {})
    source_version = source_provenance.get("fluidsim")
    if source_version is None:
        add(
            warnings,
            "missing_source_version",
            "source FluidSim version is unavailable; do not assume migration compatibility",
        )
    elif source_version != FLUIDSIM_VERSION:
        add(
            warnings,
            "version_migration",
            "source version differs from 0.9.0; review release notes and merge_missing_params",
        )

    target_restart = target["provenance"].get("restart")
    if not isinstance(target_restart, Mapping):
        add(blockers, "missing_restart_provenance", "target provenance.restart is required")
    else:
        expected_digest = target_restart.get("sha256")
        observed_digest = source_provenance.get("state_sha256")
        if observed_digest is None:
            add(
                blockers,
                "digest_not_checked",
                "source state exceeded the hash bound or lacks a manifest digest",
            )
        elif expected_digest != observed_digest:
            add(blockers, "digest_mismatch", "restart SHA-256 does not match target provenance")

    forcing = target_params.get("forcing", {})
    if (
        forcing.get("enable")
        and forcing.get("type") == "tcrandom"
        and not source_state.get("state_parameters_present")
    ):
        add(
            blockers,
            "forcing_state_missing",
            "time-correlated forcing restart lacks saved state parameters",
        )

    return {
        "blockers": blockers,
        "compatible_for_mechanical_restart": not blockers,
        "numerical_convergence_established": False,
        "ok": not blockers,
        "physical_validity_established": False,
        "source": {
            "dataset_count": len(source_state.get("datasets", [])),
            "fluidfft": source_provenance.get("fluidfft"),
            "fluidsim": source_version,
            "iteration": source_state.get("iteration"),
            "sha256_checked": source_provenance.get("state_sha256") is not None,
            "solver": source.get("solver"),
            "state_parameters_present": source_state.get(
                "state_parameters_present"
            ),
            "time": source_time,
        },
        "target": {
            "fluidfft": target["provenance"]["fluidfft"],
            "fluidsim": target["provenance"]["fluidsim"],
            "solver": target["solver"],
            "t_end": target_end,
        },
        "tool": TOOL,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare local restart metadata with validated target JSON. Field arrays "
            "are never loaded; no restart, MPI launch, or job submission occurs."
        )
    )
    parser.add_argument("--source", required=True, help="State file, run directory, or manifest.")
    parser.add_argument("--target-config", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--hash-max-gib",
        type=int,
        default=1,
        help="Hash source state only up to this many GiB, 0..8 (default: 1).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        hash_gib = bounded_int(
            args.hash_max_gib, name="hash_max_gib", minimum=0, maximum=8
        )
        root = checked_root(args.root)
        source_path = checked_input(args.source, root=root, kind="any")
        target_path = checked_input(
            args.target_config,
            root=root,
            kind="file",
            suffixes={".json"},
        )
        target = normalized_copy(load_json(target_path))
        if source_path.is_file() and source_path.name.casefold().endswith(".json"):
            source = load_manifest(source_path)
            selected = source_path
        else:
            selected = _find_state_file(source_path)
            source = load_hdf5_state(
                selected,
                digest_limit=hash_gib * GIB,
            )
        report = compare(source, target)
        report.update(
            {
                "arrays_loaded": False,
                "commands_executed": False,
                "network_used": False,
                "selected_source": relative_display(selected, root),
            }
        )
        emit_json(report)
        return 0 if report["ok"] else 2
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/simulation_dry_run.py`

```python
#!/usr/bin/env python3
"""Generate a reviewable, opt-in FluidSim launch script without running it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from ._common import (
        ToolError,
        atomic_write,
        checked_input,
        checked_output,
        emit_json,
        fail_json,
        load_json,
    )
    from ._schema import SOLVER_IMPORTS, flatten_parameters, normalized_copy
except ImportError:  # Direct script execution.
    from _common import (
        ToolError,
        atomic_write,
        checked_input,
        checked_output,
        emit_json,
        fail_json,
        load_json,
    )
    from _schema import SOLVER_IMPORTS, flatten_parameters, normalized_copy


TOOL = "fluidsim-simulation-dry-run"


def _literal(value: Any) -> str:
    """Render validated JSON scalars as fixed Python literals."""

    if value is None or isinstance(value, (bool, int, float, str)):
        return repr(value)
    raise ToolError("only JSON scalar parameter values can be rendered")


def render_script(config: dict[str, Any]) -> str:
    """Render a script with a dry-run default and explicit execution gate."""

    solver = config["solver"]
    module_name = SOLVER_IMPORTS[solver]
    assignments = []
    for path, value in flatten_parameters(config["parameters"]):
        dotted = ".".join(("params", *path))
        assignments.append(f"    {dotted} = {_literal(value)}")

    resources = config["resources"]
    execution = config["execution"]
    provenance = config["provenance"]
    plan = {
        "config_id": provenance["config_id"],
        "cpu_cores": resources["cpu_cores"],
        "disk_gib": resources["disk_gib"],
        "fluidfft": provenance["fluidfft"],
        "fluidsim": provenance["fluidsim"],
        "max_output_files": resources["max_output_files"],
        "mode": execution["mode"],
        "mpi_ranks": resources["mpi_ranks"],
        "output_root": execution["output_root"],
        "ram_gib": resources["ram_gib"],
        "solver": solver,
        "threads_per_rank": resources["threads_per_rank"],
        "wall_time_minutes": resources["wall_time_minutes"],
    }
    plan_json = json.dumps(plan, allow_nan=False, sort_keys=True)
    assignment_block = "\n".join(assignments)
    expected_ranks = int(resources["mpi_ranks"])
    return f'''#!/usr/bin/env python3
"""Generated FluidSim {provenance["fluidsim"]} plan. Dry-run unless explicitly approved."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


PLAN = json.loads({plan_json!r})
CONFIG_ID = {provenance["config_id"]!r}
OUTPUT_ROOT = {execution["output_root"]!r}
EXPECTED_RANKS = {expected_ranks}
MODE = {execution["mode"]!r}


def _detected_mpi_size() -> int:
    for name in ("OMPI_COMM_WORLD_SIZE", "PMI_SIZE", "PMIX_SIZE", "MPI_LOCALNRANKS"):
        value = os.environ.get(name)
        if value and value.isdecimal():
            return int(value)
    return 1


def _prepare_output_root() -> Path:
    base = Path(__file__).resolve().parent
    destination = base / OUTPUT_ROOT
    if destination.exists() and destination.is_symlink():
        raise RuntimeError("refusing a symlink output root")
    destination.mkdir(mode=0o700, exist_ok=True)
    resolved = destination.resolve(strict=True)
    if resolved.parent != base:
        raise RuntimeError("output root escaped the script directory")
    os.environ["FLUIDSIM_PATH"] = str(resolved)
    return resolved


def run() -> None:
    size = _detected_mpi_size()
    if MODE == "serial" and size != 1:
        raise RuntimeError("serial plan detected an MPI launcher")
    if MODE == "mpi-preview" and size != EXPECTED_RANKS:
        raise RuntimeError("launch manually with exactly the reviewed MPI rank count")
    _prepare_output_root()
    os.environ.setdefault("OMP_NUM_THREADS", {str(resources["threads_per_rank"])!r})

    import numpy as np
    from {module_name} import Simul

    np.random.seed({int(execution["random_seed"])})
    params = Simul.create_default_params()
{assignment_block}
    sim = Simul(params)
    sim.time_stepping.start()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--acknowledge-config-id")
    args = parser.parse_args()
    if not args.execute:
        print(json.dumps({{"dry_run": True, "plan": PLAN}}, indent=2, sort_keys=True))
        return 0
    if args.acknowledge_config_id != CONFIG_ID:
        parser.error("--execute requires the exact reviewed --acknowledge-config-id")
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def build_plan(config: dict[str, Any], script: str) -> dict[str, Any]:
    execution = config["execution"]
    resources = config["resources"]
    execute_argv = [
        "<python>",
        execution["script_name"],
        "--execute",
        "--acknowledge-config-id",
        config["provenance"]["config_id"],
    ]
    mpi_preview = None
    if execution["mode"] == "mpi-preview":
        mpi_preview = [
            "<site-mpi-launcher>",
            "-n",
            str(resources["mpi_ranks"]),
            *execute_argv,
        ]
    return {
        "approval_gate": [
            "review the validated scientific assumptions and acceptance criteria",
            "review the resource estimate against CPU, RAM, disk, wall-time, and file limits",
            "verify FFT/MPI backend on the target host with a tiny pilot",
            "record the config, script, lock, environment, and restart hashes",
        ],
        "commands_executed": False,
        "dry_run": True,
        "execute_argv_after_approval": execute_argv,
        "job_submitted": False,
        "mpi_launch_preview_only": mpi_preview,
        "mpi_launched": False,
        "network_used": False,
        "physical_validity_established": False,
        "script": script,
        "script_sha256": hashlib.sha256(script.encode("utf-8")).hexdigest(),
        "tool": TOOL,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an opt-in FluidSim script from validated local JSON. The "
            "generator never imports FluidSim, invokes MPI, submits a job, or runs code."
        )
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument(
        "--output",
        help="Optional .py file within --root; parent must exist.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacement of an existing regular output file.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config_path = checked_input(
            args.config,
            root=args.root,
            kind="file",
            suffixes={".json"},
        )
        config = normalized_copy(load_json(config_path))
        script = render_script(config)
        report = build_plan(config, script)
        if args.output:
            output = checked_output(
                args.output,
                root=args.root,
                suffixes={".py"},
                force=args.force,
            )
            atomic_write(output, script.encode("utf-8"), force=args.force)
            report["script"] = None
            report["script_written"] = output.name
        else:
            report["script_written"] = None
        emit_json(report)
        return 0
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/solver_config_validator.py`

```python
#!/usr/bin/env python3
"""Validate a bounded FluidSim 0.9 JSON simulation plan."""

from __future__ import annotations

import argparse

try:
    from ._common import ToolError, checked_input, emit_json, fail_json, load_json
    from ._schema import example_config, validate_config
except ImportError:  # Direct script execution.
    from _common import ToolError, checked_input, emit_json, fail_json, load_json
    from _schema import example_config, validate_config


TOOL = "fluidsim-solver-config-validator"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate strict local JSON against the static FluidSim 0.9 CFD "
            "configuration profile. No FluidSim package is imported and nothing runs."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--config", help="Configuration JSON within --root.")
    source.add_argument(
        "--example",
        action="store_true",
        help="Emit a bounded example configuration as strict JSON.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Local I/O boundary (default: current directory).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.example:
            emit_json(example_config())
            return 0
        path = checked_input(
            args.config,
            root=args.root,
            kind="file",
            suffixes={".json"},
        )
        report = validate_config(load_json(path))
        report.update(
            {
                "commands_executed": False,
                "dynamic_imports_used": False,
                "network_used": False,
                "source": path.name,
                "tool": TOOL,
            }
        )
        emit_json(report)
        return 0 if report["ok"] else 2
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
```
