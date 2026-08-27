---
name: pufferlib
description: Version-aware guidance for PufferLib reinforcement-learning environments, vectorization, policies, PuffeRL training, evaluation, and safe checkpoint review. Use when adapting Gymnasium/PettingZoo environments to published PufferLib 3.0.0 or working with the redesigned native 4.0 source line.
---

# PufferLib

Use PufferLib with an explicit version profile. Upstream currently has two
incompatible surfaces:

| Profile | Status on 2026-07-23 | Main use |
|---|---|---|
| `pufferlib==3.0.0` | Latest stable PyPI release, published 2025-06-23 | Python/Gymnasium/PettingZoo emulation, `pufferlib.vector`, Torch PuffeRL |
| source `4.0` | Upstream default branch; not the latest stable PyPI artifact | Native C Ocean environments, native CUDA trainer, optional Torch fallback |

Do not combine 3.0 imports with 4.0 config/CLI examples. The 4.0 redesign
removed the 3.0 `emulation`, `vector`, and `pytorch` modules from the current
package tree.

## Safe defaults

1. Start with bundled synthetic, CPU-only, network-free tools.
2. Do not import an arbitrary environment by dotted path. Bundled tools accept
   only allowlisted built-ins and slug identifiers.
3. Do not install or execute an unreviewed environment package, native
   extension, ROM, map, checkpoint, or pickle file.
4. Verify official source, immutable revision, licenses, checksums or
   attestations, and build hooks. Sandbox native builds and first execution.
5. Cap steps, environments, agents, workers, threads, buffers, memory, disk,
   render size, and wall time.
6. Keep training and evaluation environments/seeds separate.
7. Default logging to local/none. External logging requires explicit opt-in,
   disclosure acknowledgment, and separate artifact-upload approval.
8. Never pass W&B or Neptune credentials via CLI, INI, JSON, tags, run names, or
   logger configuration. Never print them.
9. Never dump all environment variables or recursively search for `.env`.
10. Hash checkpoint bytes before trusted, sandboxed loading; metadata inspection
    is not proof of safety.

## First local checks

All bundled CLIs are dependency-free and emit strict JSON:

```bash
python3 scripts/env_template.py --help
python3 scripts/env_contract_validator.py
python3 scripts/benchmark_vectorization.py --backend serial
python3 scripts/train_template.py
python3 scripts/validate_plan.py
python3 scripts/repro_plan.py
```

Defaults are synthetic, deterministic, bounded, local, CPU-only, no-network,
and dry-run where training would otherwise occur.

## Installation and provenance

### Published 3.0.0

PyPI supplies only `pufferlib-3.0.0.tar.gz`:

```text
sha256: 7df3a3e3f5f894d78d2a1f5374097890aec01473183e748abefe4f3faa10eaa9
Requires-Python: >=3.9
```

After source/build review, create a pinned uv project:

```bash
uv venv --python 3.11
uv add --exact --no-sync "pufferlib==3.0.0"
uv lock
uv sync --frozen
```

Commit `pyproject.toml` and `uv.lock`; verify the archive digest and every
resolved dependency. The source build can compile native code and fetch build
assets, so resolve/build in a sandbox without credentials or sensitive mounts.
The uploaded metadata does not pin Torch or CUDA; do not claim a supported CUDA
matrix that PyPI does not declare.

### Current 4.0 source

The reviewed branch head on 2026-07-23 was:

```text
25647630e1b15330bb3153a5a0d3ff8d234c3acf
```

Pin the commit, not branch `4.0`:

```bash
uv add --no-sync \
  "pufferlib @ git+https://github.com/PufferAI/PufferLib.git@25647630e1b15330bb3153a5a0d3ff8d234c3acf"
uv lock
```

The current package declares Python `>=3.10` and Torch `>=2.9`. Upstream
PufferTank currently uses Ubuntu 24.04, Python 3.12, and an NVIDIA CUDA
13.0.2/cuDNN development image with the `cu130` Torch index, but does not pin
the exact Torch wheel or all system packages. Treat it as a reference, not a
complete lock. Never execute a remote installer directly from a pipe.

Read `references/training.md` before any installation or build.

## Environment workflow

### 1. Validate the contract

Gymnasium reset returns `(observation, info)`. Step returns:

```python
(observation, reward, terminated, truncated, info)
```

Validate spaces, shapes, dtypes, finite rewards, booleans, reset-before-step,
reset-after-end, seeding, and cleanup. `terminated` is an MDP terminal;
`truncated` is an external cutoff such as a time limit. Preserve the distinction
for bootstrapping and metrics.

```bash
python3 scripts/env_contract_validator.py \
  --steps 64 --episodes 8 --seed 42
```

### 2. Adapt only after review

Published 3.0 uses explicit wrappers:

```python
import pufferlib.emulation

wrapped = pufferlib.emulation.GymnasiumPufferEnv(reviewed_gymnasium_instance)
```

For a reviewed PettingZoo Parallel environment:

```python
wrapped = pufferlib.emulation.PettingZooPufferEnv(reviewed_parallel_instance)
```

There is no supported 3.0 `pufferlib.emulate(...)` shortcut matching the old
skill. Read `references/environments.md` and `references/integration.md`.

### 3. Native environments

Published 3.0 `PufferEnv` requires
`single_observation_space`, `single_action_space`, and `num_agents` before
`super().__init__(buf)`. It uses in-place vector buffers and returns separate
terminal/truncation arrays plus a list of info dictionaries.

Current 4.0 uses C bindings. Start from upstream `ocean/squared` (single-agent)
or `ocean/target` (multi-agent), build one environment in local/sanitized mode,
and verify every buffer size/type/index before optimization.

## Vectorization workflow

Published 3.0:

```python
import pufferlib.vector

vecenv = pufferlib.vector.make(
    reviewed_creator,
    backend=pufferlib.vector.Serial,
    num_envs=4,
    seed=42,
)
```

Move to `Multiprocessing` only after serial traces pass. Record
`num_envs`, `num_workers`, `batch_size`, zero-copy mode, start method, agent
count, masks, and actual returned shapes. For multi-agent environments, batch
length is based on agent slots, not necessarily `num_envs`.

Current 4.0 config instead uses:

```ini
[vec]
total_agents = 4096
num_buffers = 2
num_threads = 16
```

Read `references/vectorization.md`. Benchmark fixed work with warmup and at least
three repeats; report simulation and end-to-end training SPS separately. The
bundled benchmark measures only its synthetic harness.

## Policy workflow

Published 3.0 policies are Torch modules sized from
`single_observation_space`/`single_action_space`. Stable recurrent composition
uses `encode_observations` and `decode_actions`; structured emulation uses
`pufferlib.pytorch.nativize_dtype` and `nativize_tensor`.

Current 4.0 Torch fallback composes:

```python
pufferlib.models.Policy(encoder=encoder, decoder=decoder, network=network)
```

It provides MLP, MinGRU, LSTM, and GRU network choices; `--slowly` selects this
fallback instead of the native backend. Check output/state shapes, masks,
finite values, gradients, and eager-versus-compiled behavior. See
`references/policies.md`.

## Training and evaluation

Published 3.0 trainer import:

```python
from pufferlib import pufferl

trainer = pufferl.PuffeRL(train_config, vecenv, policy)
```

Current 4.0 CLI:

```bash
puffer train ENV_NAME
puffer eval ENV_NAME --load-model-path EXACT_TRUSTED_PATH
puffer sweep ENV_NAME
```

Generate a plan instead of launching by default:

```bash
python3 scripts/train_template.py \
  --profile pypi-3.0.0 \
  --environment synthetic \
  --device cpu \
  --total-timesteps 10000
```

Validate a custom strict-JSON plan:

```bash
python3 scripts/validate_plan.py --root . --config plan.json
```

The schema rejects secret-bearing keys, unbounded resources, dotted environment
paths, invalid vector divisibility, mixed-version options, and coupled
train/eval seeds. See `references/training.md`.

## Logging

PufferLib 3.0 exposes W&B and Neptune; current 4.0 CLI exposes W&B. Both are
optional external services. They may transmit configuration, metrics, source
metadata, hardware telemetry, output, and approved artifacts, with privacy,
retention, access-control, and cost implications.

- W&B credential: named environment variable `WANDB_API_KEY`.
- Neptune credential: named environment variable `NEPTUNE_API_TOKEN`.
- Never put values in arguments/config/logs.
- Sanitize config keys before logging.
- Keep source/model upload off unless explicitly approved.

The planner requires both:

```bash
python3 scripts/train_template.py \
  --logger wandb \
  --enable-external-logging \
  --acknowledge-external-disclosure
```

It reports only the required variable name and never reads its value.

## Checkpoint workflow

PufferLib 3.0 and the 4.0 Torch fallback use Torch serialization; current native
4.0 writes opaque `.bin` weights. PyTorch warns that untrusted models are
programs and that `torch.load` uses unpickling.

```bash
python3 scripts/inspect_checkpoint.py checkpoint.pt \
  --root . \
  --expected-sha256 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

The inspector hashes and classifies only. It does not call `torch.load`, import
pickle/Torch, inspect archive members, or extract files. Verify source, license,
architecture, environment revision, sidecar metadata, and checksum before any
sandboxed load. Never use `latest` in a reproducible evaluation.

## Bundled files

### Scripts

- `scripts/env_template.py` — deterministic synthetic Gymnasium-style template.
- `scripts/env_contract_validator.py` — bounded contract and seed checks.
- `scripts/benchmark_vectorization.py` — capped serial/spawn synthetic benchmark.
- `scripts/train_template.py` — non-executing 3.0/4.0 training-plan generator.
- `scripts/validate_plan.py` — strict config/resource/security validator.
- `scripts/inspect_checkpoint.py` — metadata/hash inspection without deserialization.
- `scripts/repro_plan.py` — separate-seed evaluation and benchmark plan.

### References

- `references/environments.md` — Gymnasium, stable PufferEnv, emulation, native C.
- `references/vectorization.md` — backends, shapes, start methods, benchmarks.
- `references/policies.md` — stable/current policy contracts and state safety.
- `references/training.md` — installs, config, CLI, PuffeRL, eval, logs, checkpoints.
- `references/integration.md` — migration matrix, third-party and credential safety.

## Dated upstream sources

- [PyPI pufferlib 3.0.0](https://pypi.org/project/pufferlib/3.0.0/) —
  released 2025-06-23; checked 2026-07-23.
- [PyPI 3.0.0 metadata](https://pypi.org/pypi/pufferlib/3.0.0/json) —
  digest/dependencies; checked 2026-07-23.
- [PufferLib official docs](https://puffer.ai/docs.html) — current 4.0 docs;
  checked 2026-07-23.
- [PufferLib source](https://github.com/PufferAI/PufferLib) — default branch and
  implementation; checked 2026-07-23.
- [PufferTank 4.0 Dockerfile](https://github.com/PufferAI/PufferTank/blob/4.0/puffertank.dockerfile)
  — CUDA/Python reference; checked 2026-07-23.
- [PufferLib 2.0 paper](https://openreview.net/forum?id=qRyteMTgn0) —
  Reinforcement Learning Journal, 2025; use only for its stated benchmarks.
- [PufferLib compatibility paper](https://arxiv.org/abs/2406.12905) —
  submitted 2024-06-18; describes an earlier API/performance profile.

---

## Bundled files (Open WebUI single-file edition)

> This is a conversion of `skills/pufferlib/` from the K-Dense scientific-agent-skills package (https://github.com/K-Dense-AI/scientific-agent-skills) for Open WebUI, which stores each skill as a single markdown blob. Sibling files the skill text refers to (references, scripts, assets) are inlined below: when instructions mention `references/foo.md`, its content is here.

### `references/environments.md`

# Environment Contracts and Native Environments

Research snapshot: **2026-07-23**.

## Start from the Gymnasium contract

A current single-agent Gymnasium environment defines `observation_space` and
`action_space`, then implements:

```python
def reset(self, *, seed=None, options=None):
    super().reset(seed=seed)
    return observation, info

def step(self, action):
    return observation, reward, terminated, truncated, info
```

Contract requirements:

- `observation` must be contained in `observation_space` after reset and every
  step, with the documented shape and dtype.
- `action` must be contained in `action_space`.
- `reward` is a finite scalar for ordinary single-agent tasks.
- `terminated` means the task's MDP reached a terminal state.
- `truncated` means an external limit ended the episode, commonly a time limit.
- `info` is a dictionary; never hide the only termination signal in it.
- Call `reset()` after either `terminated` or `truncated`.
- Seed the environment through `reset(seed=...)`. Seed the action space
  separately when sampled actions must be reproducible.
- Always call `close()`.

Do not collapse `terminated` and `truncated` during learning. A time-limit
truncation can still permit value bootstrapping; a true terminal state does not.

Run the local contract tool before involving PufferLib:

```bash
python3 scripts/env_contract_validator.py
```

It validates only the bundled synthetic environment. It intentionally has no
module-path option, so it cannot dynamically import an untrusted package.

## Published PufferLib 3.0.0 native contract

For a native Python `PufferEnv`, assign these attributes **before** calling
`super().__init__(buf)`:

```python
import gymnasium
import numpy as np
import pufferlib


class ReviewedEnv(pufferlib.PufferEnv):
    def __init__(self, buf=None, seed=0):
        self.single_observation_space = gymnasium.spaces.Box(
            low=-1.0, high=1.0, shape=(4,), dtype=np.float32
        )
        self.single_action_space = gymnasium.spaces.Discrete(3)
        self.num_agents = 2
        super().__init__(buf)
```

The stable base accepts a Box observation space and Discrete, MultiDiscrete, or
Box action space. It allocates or attaches:

- `observations`
- `actions`
- `rewards`
- `terminals`
- `truncations`
- `masks`

Native methods operate on those buffers:

```python
def reset(self, seed=None):
    # update self.observations in place
    return self.observations, []

def step(self, actions):
    # update all buffers in place
    return (
        self.observations,
        self.rewards,
        self.terminals,
        self.truncations,
        [],
    )
```

The `infos` value for native Puffer environments is a list of dictionaries.
PufferLib's native interface expects vector rows for agents, even when there is
one agent. Native environments handle their own resets; clear rewards,
terminals, truncations, masks, and partially written observations explicitly.
Never leave a previous step's buffer values in place.

### Native shape checklist

For `A = num_agents` and single observation shape `S`:

- observations: `(A, *S)`
- rewards: `(A,)`
- terminals: `(A,)`
- truncations: `(A,)`
- masks: `(A,)`
- actions: joint shape derived from the single action space and `A`

Validate the exact allocated action shape rather than assuming `(A,)`, especially
for MultiDiscrete and Box actions.

## Stable Gymnasium and PettingZoo adaptation

PufferLib 3.0 uses explicit adapters:

```python
import pufferlib.emulation

wrapped = pufferlib.emulation.GymnasiumPufferEnv(reviewed_gymnasium_instance)
```

or:

```python
wrapped = pufferlib.emulation.PettingZooPufferEnv(reviewed_parallel_instance)
```

There is no supported 3.0 `pufferlib.emulate(...)` convenience function matching
the old skill examples. Pass either an `env` instance or an `env_creator`
callable according to the class signature; do not pass both.

The Gymnasium adapter:

- maps structured observation/action spaces to flat arrays;
- checks the first observation and action against the original spaces;
- returns separate terminal and truncation values;
- requires reset before step and reset after episode end.

The PettingZoo adapter:

- targets the Parallel API;
- uses `possible_agents` as the fixed slot set;
- pads missing agents and exposes masks;
- canonicalizes per-agent spaces and flattened buffers.

Validate heterogeneous-agent spaces before use. The adapter derives its single
spaces from the first possible agent, so environments with incompatible spaces
need an explicit reviewed transformation.

### Structured spaces

Stable emulation supports Box, Discrete, MultiDiscrete, Tuple, and Dict patterns
through a packed NumPy dtype. This is byte-layout conversion, not semantic
feature engineering. Check:

- deterministic Dict key order;
- leaf shape and dtype;
- finite numeric values;
- lossless action reconstruction;
- policy-side unflattening;
- padding/mask handling for variable populations.

## Current 4.0 Ocean contract

The 4.0 default branch focuses on first-party C environments. It no longer
provides the 3.0 Python emulation/vector modules. The official starting points
are:

- `ocean/squared`: commented single-agent template
- `ocean/target`: commented multi-agent template

A binding defines compile-time metadata such as:

```c
#define OBS_SIZE 121
#define NUM_ATNS 1
#define ACT_SIZES {5}
#define OBS_TENSOR_T ByteTensor

#define Env Squared
#include "vecenv.h"
```

The environment struct must include pointers for observations, actions,
rewards, and terminals, plus `num_agents` and a log struct. It implements
`c_reset`, `c_step`, `c_render`, and `c_close`; `binding.c` supplies `my_init`
and `my_log`.

Security and correctness rules:

1. Treat the C environment and every linked library as native code.
2. Verify repository/commit, license, asset rights, and checksums before build.
3. Build only the selected environment in a disposable container or VM.
4. Start with the local/address-sanitizer build described by upstream.
5. Match `OBS_SIZE`, tensor dtype, action branch count/sizes, and actual writes.
6. Bounds-check every index and allocation; use checked arithmetic for sizes.
7. Initialize every output element each step. Reset reward/terminal buffers
   before early returns.
8. Use an environment-owned RNG seeded per instance; do not use global RNG
   state for reproducibility.
9. Free only memory owned by the environment. Do not free framework buffers.
10. Fuzz reset/step/action boundaries before optimization.

`c_step` may reset immediately after marking a terminal. Record this autoreset
behavior when interpreting terminal observations.

## Environment provenance

An environment package may execute arbitrary Python/native code and may fetch
assets at import, build, reset, or render time. Before execution:

- use the official repository and immutable revision;
- inspect package/build scripts and transitive dependencies;
- verify artifact hashes or attestations;
- review license compatibility for code, datasets, media, ROMs, maps, and model
  opponents separately;
- reject unlicensed ROMs or “accept ROM license” automation without proof of
  rights;
- disable network and credentials in the first-run sandbox;
- cap disk, memory, processes, threads, episode length, agents, and render size;
- do not load bundled checkpoints or pickle files during environment import.

An entry in Ocean/config is not a blanket security, quality, or licensing
approval.

## Testing ladder

1. Built-in synthetic contract validator.
2. One environment, one seed, serial, tens of steps.
3. Boundary actions and intentionally invalid actions.
4. Termination and time-limit truncation tests.
5. Same-seed trace comparison.
6. Independent-seed diversity check.
7. Structured-space round trip.
8. Multi-agent join/leave and mask tests.
9. Serial versus vectorized trace equivalence where ordering permits.
10. Bounded throughput benchmark only after correctness passes.

## Sources

- [Gymnasium Env API](https://gymnasium.farama.org/api/env/) — current reset,
  step, spaces, and seeding contract; accessed 2026-07-23.
- [Gymnasium terminated/truncated explanation](https://farama.org/Gymnasium-Terminated-Truncated-Step-API)
  — published 2023-10-27; accessed 2026-07-23.
- [PufferLib 3.0 core environment source](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/pufferlib.py)
  — stable native contract; accessed 2026-07-23.
- [PufferLib 3.0 emulation source](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/emulation.py)
  — stable adapters; accessed 2026-07-23.
- [PufferLib 3.0 Gymnasium example](https://github.com/PufferAI/PufferLib/blob/3.0/examples/gymnasium_env.py)
  — stable example; accessed 2026-07-23.
- [PufferLib 3.0 PettingZoo example](https://github.com/PufferAI/PufferLib/blob/3.0/examples/pettingzoo_env.py)
  — stable example; accessed 2026-07-23.
- [PufferLib 4.0 Squared template](https://github.com/PufferAI/PufferLib/tree/4.0/ocean/squared)
  — current single-agent native template; accessed 2026-07-23.
- [PufferLib 4.0 Target template](https://github.com/PufferAI/PufferLib/tree/4.0/ocean/target)
  — current multi-agent native template; accessed 2026-07-23.
- [PufferLib Ocean](https://puffer.ai/ocean.html) — current first-party
  collection; accessed 2026-07-23.

### `references/integration.md`

# Integration, Security, and Migration Guide

Research snapshot: **2026-07-23**.

## Compatibility matrix

| Need | Published `pufferlib==3.0.0` | Current `4.0` source |
|---|---|---|
| Gymnasium instance adaptation | `pufferlib.emulation.GymnasiumPufferEnv` | Removed from current source |
| PettingZoo Parallel adaptation | `pufferlib.emulation.PettingZooPufferEnv` | Removed from current source |
| Python vector backends | `pufferlib.vector` | Removed from current source |
| Native Python `PufferEnv` | Supported | Replaced by current C/Ocean interface |
| Trainer | `pufferlib.pufferl.PuffeRL` | Native backend or `pufferlib.torch_pufferl.PuffeRL` |
| External logging | W&B and Neptune | W&B in current CLI |
| Primary config | merged INI sections | different INI schema |
| Checkpoints | Torch state dict plus trainer state | native `.bin`; Torch fallback state dict |

Pin a profile. Do not import from a floating branch or blend examples across
columns.

## Correct stable adaptation patterns

### Gymnasium

```python
import gymnasium
import pufferlib.emulation
import pufferlib.vector


def make_env():
    raw = gymnasium.make("CartPole-v1")
    return pufferlib.emulation.GymnasiumPufferEnv(raw)


vecenv = pufferlib.vector.make(
    make_env,
    backend=pufferlib.vector.Serial,
    num_envs=2,
    seed=42,
)
try:
    observations, infos = vecenv.reset(seed=42)
    actions = vecenv.action_space.sample()
    observations, rewards, terminals, truncations, infos = vecenv.step(actions)
finally:
    vecenv.close()
```

This example is an API pattern, not authorization to install or execute
`CartPole-v1` or another plug-in. Review the exact environment and dependencies
first.

### PettingZoo

Use a reviewed Parallel environment instance:

```python
wrapped = pufferlib.emulation.PettingZooPufferEnv(reviewed_parallel_env)
```

The stable source does not document automatic AEC-to-Parallel conversion in
this adapter. Convert explicitly with PettingZoo's supported utilities only
when the environment's turn semantics permit it, then test action ordering,
dead-agent handling, masks, and termination/truncation dictionaries.

### Native stable environment

Subclass `pufferlib.PufferEnv`, define `single_observation_space`,
`single_action_space`, and `num_agents` before `super().__init__`, then update
the provided arrays in place. Native Puffer environments are already vector
interfaces; do not return Gym's scalar four-tuple.

## Unsupported shortcuts from the old skill

Remove or migrate these historical patterns:

| Historical pattern | Current guidance |
|---|---|
| `pufferlib.make("name", ...)` | Stable: import an audited creator and use `pufferlib.vector.make`; 4.0: build/configure a named native environment |
| `pufferlib.emulate(...)` | Stable: instantiate `GymnasiumPufferEnv` or `PettingZooPufferEnv` explicitly |
| `pufferlib.vectorization.Serial` | Stable module is `pufferlib.vector.Serial` |
| `from pufferlib import PuffeRL` | Stable trainer is `pufferlib.pufferl.PuffeRL`; 4.0 fallback is in `torch_pufferl` |
| define native `observation_space`/`action_space` | Stable native class requires `single_observation_space`/`single_action_space` before `super()` |
| return `(obs, reward, done, info)` | Return separate termination and truncation values |
| native multi-agent dictionaries and `dones["__all__"]` | Use stable vector buffers or a reviewed PettingZoo Parallel adapter |
| arbitrary dotted `entry_point` registration | Import an audited callable directly; bundled tools reject dotted paths |
| top-level `WandbLogger`/`NeptuneLogger` | Stable logger classes live in `pufferlib.pufferl`; prefer the CLI and sanitized config |
| assume Atari/Procgen/NetHack names exist everywhere | Verify the chosen version's config/source and install the separately reviewed environment |

## Migrating 3.0 to 4.0

This is a redesign, not a drop-in upgrade:

1. Preserve the 3.0 lock, source digest, config, checkpoint hashes, and baseline
   evaluation before changing anything.
2. Inventory use of `emulation`, `vector`, `PufferEnv`, third-party environments,
   policy wrappers, INI keys, logger flags, and Torch checkpoints.
3. Decide whether the application should stay on published 3.0.0 or port to a
   native 4.0 C environment. The current docs say the Python/third-party layer
   was removed from 4.0.
4. Port environment logic to the reviewed Squared/Target C binding contract.
5. Recreate configuration using 4.0 `[vec]`, `[policy]`, `[torch]`, and `[train]`
   keys. Do not mechanically rename old keys.
6. Rebuild policy composition around 4.0 encoder/decoder/network modules or the
   native backend.
7. Treat old `.pt` and new `.bin` files as incompatible unless an official,
   tested converter says otherwise. Do not improvise binary conversion.
8. Re-run contract, same-seed trace, throughput, and held-out learning
   baselines. Attribute behavior changes; do not compare headline SPS alone.

The default branch contains some stale 3.0-style examples even though the
corresponding modules are absent. Prefer current implementation and docs over
those copied examples.

## Third-party environments and native code

Environment extras can pull old Gym versions, native libraries, renderers,
emulators, datasets, model opponents, and ROM tooling. A package name in a
PufferLib optional extra is not a security or license endorsement.

Before install/import/build:

1. Identify the official repository and immutable revision.
2. Read build/install hooks and all network downloads.
3. Verify licenses for code and assets separately.
4. Verify hashes/attestations; record missing provenance.
5. Use a disposable sandbox without credentials, home-directory mounts, or
   network after required artifacts are staged.
6. Cap processes, threads, memory, disk, render resolution, agents, and steps.
7. Do not execute bundled native extensions, ROMs, checkpoints, or pickle files
   until separately trusted.

For Atari and similar systems, the user must supply legally obtained assets.
Never download ROM sets or auto-accept a license on the user's behalf.

## Logging integration

External tracking is disabled by default. The stable logger implementations can
log the full argument mapping and can upload model artifacts. Therefore:

- sanitize arguments before logger construction;
- keep `WANDB_API_KEY` and `NEPTUNE_API_TOKEN` only in an approved environment
  injection or secret manager;
- never add credential keys to nested INI/JSON/config objects;
- do not pass a token on the command line;
- disable model/source upload unless explicitly approved;
- review project visibility, retention, residency, access controls, and cost;
- use vendor offline/disabled modes only after confirming what is written
  locally and how later sync behaves.

Do not print all environment variables or recursively discover `.env` files.
Checking whether one explicitly named credential variable exists can be
acceptable; reading or logging its value is not.

## Integration acceptance test

For each reviewed environment/profile:

1. Create one instance without network or GPU.
2. Validate spaces and reset return.
3. Step a fixed action trace until both ordinary and episode-end paths run.
4. Verify terminated/truncated semantics and final observation behavior.
5. Close and confirm no child processes/resources remain.
6. Run stable Serial or one 4.0 local native instance.
7. Compare a same-seed trace.
8. Scale to two workers/threads with small caps.
9. Run policy shape and finite-value checks.
10. Run held-out evaluation with logging still disabled.

Only then consider GPU training, external logging, or larger parallelism.

## Sources

- [PufferLib PyPI 3.0.0](https://pypi.org/project/pufferlib/3.0.0/) —
  published 2025-06-23; accessed 2026-07-23.
- [PufferLib 3.0 emulation source](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/emulation.py)
  — stable adapters; accessed 2026-07-23.
- [PufferLib 3.0 vector source](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/vector.py)
  — stable vector API; accessed 2026-07-23.
- [PufferLib 3.0 trainer source](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/pufferl.py)
  — stable logger/checkpoint behavior; accessed 2026-07-23.
- [PufferLib 4.0 package tree](https://github.com/PufferAI/PufferLib/tree/4.0/pufferlib)
  — current modules; accessed 2026-07-23.
- [PufferLib 4.0 docs](https://puffer.ai/docs.html) — current architecture and
  removal note; accessed 2026-07-23.
- [PufferLib releases](https://github.com/PufferAI/PufferLib/releases) —
  checked for source releases on 2026-07-23.
- [Gymnasium Env API](https://gymnasium.farama.org/api/env/) — current
  single-agent contract; accessed 2026-07-23.
- [PyTorch security policy](https://github.com/pytorch/pytorch/security) —
  model/native-package safety; accessed 2026-07-23.

### `references/policies.md`

# Policies and Model Contracts

Research snapshot: **2026-07-23**. Policy APIs changed substantially between
published PufferLib 3.0.0 and current 4.0 source.

## Published 3.0.0

PufferLib 3.0 policies are ordinary `torch.nn.Module` objects. The environment
exposes `single_observation_space` and `single_action_space`; size heads from
those single-agent spaces, not from the batched spaces.

### Minimal feed-forward policy

Build an `nn.Module` with an encoder sized from
`env.single_observation_space.shape`, an action head sized from
`env.single_action_space`, and a one-value critic head. The official stable
example defines a rollout method named `forward_eval(observations, state=None)`
and makes the normal `forward` method use the same contract. Here, `forward_eval`
is a PufferLib/PyTorch method name; it does **not** invoke Python's dangerous
`eval()` builtin.

For a discrete action space, the first output contains action logits and the
second is the value estimate. Preserve the leading agent-batch dimension.

### Recurrent composition

The stable `pufferlib.models.LSTMWrapper` expects a base policy with:

```python
def encode_observations(self, observations, state=None):
    ...

def decode_actions(self, hidden):
    ...
```

The wrapper uses an `LSTMCell` during rollout inference and an `LSTM` over
time-batched data during training. Do not manually reshape recurrent state
without checking the source's batch/time convention. Reset hidden state on
actual terminations and truncations according to the trainer's mask behavior.

### Structured observations

Stable emulation flattens `Dict` and `Tuple` spaces into a homogeneous array.
The byte layout is described by `env.emulated`. In policy setup:

```python
native_dtype = pufferlib.pytorch.nativize_dtype(env.emulated)
```

In the forward pass:

```python
structured = pufferlib.pytorch.nativize_tensor(observations, native_dtype)
```

Keep the original flattened dtype. Constructing a new float tensor before
unflattening can destroy the packed representation. Validate every recovered
leaf shape and dtype before training.

### Action spaces

The 3.0 source handles:

- `Discrete`: one categorical logits tensor.
- `MultiDiscrete`: one logits tensor per action branch.
- `Box`: a Normal distribution path for continuous actions.

Do not infer support from the 2024 paper's limitations section; that paper
describes an earlier release. Test clipping/scaling against the environment's
actual `Box.low`, `Box.high`, shape, and dtype. A `tanh` output is not a general
substitute for affine mapping to arbitrary bounds.

### Stable model utilities

Useful 3.0 symbols include:

- `pufferlib.pytorch.layer_init`
- `pufferlib.pytorch.nativize_dtype`
- `pufferlib.pytorch.nativize_tensor`
- `pufferlib.models.Default`
- `pufferlib.models.LSTMWrapper`
- `pufferlib.models.Convolutional`
- `pufferlib.models.ProcgenResnet`

Inspect the exact 3.0 source before copying signatures. Do not use top-level
`from pufferlib import PuffeRL`; the trainer is
`pufferlib.pufferl.PuffeRL`.

## Current 4.0 source

The current PyTorch fallback composes a policy from three modules:

```python
policy = pufferlib.models.Policy(
    encoder=encoder,
    decoder=decoder,
    network=network,
)
```

The source contract is:

- `Policy.initial_state(batch_size, device)`
- `Policy.forward_eval(x, state)` for rollout inference
- `Policy.forward(x)` for time-batched training
- encoder maps observations to hidden vectors
- recurrent/network module maps hidden vectors and state
- decoder maps hidden vectors to action logits and values

Current built-ins include `DefaultEncoder`, `DefaultDecoder`, `MLP`, `MinGRU`,
`LSTM`, `GRU`, `NatureEncoder`, and `ImpalaEncoder`. INI config selects the
Torch fallback components:

```ini
[torch]
network = MinGRU
encoder = DefaultEncoder
decoder = DefaultDecoder

[policy]
hidden_size = 128
num_layers = 4
```

The default 4.0 backend is the native implementation, not this Torch fallback.
The CLI flag `--slowly` selects the fallback.

## Shape and numerical checks

Run these checks before a long job:

1. Reset the reviewed environment and record observation shape/dtype/range.
2. Run one policy inference under `torch.no_grad()`.
3. For discrete actions, require logits shape
   `(agent_batch, action_space.n)`.
4. Require values to represent one scalar per active agent.
5. For `MultiDiscrete`, verify branch count and each branch width.
6. For recurrent policies, verify state batch matches active agent rows and
   that masks reset state at episode boundaries.
7. Reject NaN/Infinity in observations, logits, values, losses, and gradients.
8. Confirm inactive/padded multi-agent rows do not contribute to loss.
9. Run backward once and verify finite, non-missing gradients.
10. Compare eager and compiled outputs before enabling compilation.

`torch.compile` and reduced precision can alter performance and numerical
behavior. Record PyTorch, CUDA, compiler mode, precision, and deterministic
settings. Do not claim determinism solely because seeds are fixed.

## Checkpoint-safe policy workflow

- Save weights/state dictionaries, architecture config, environment revision,
  package lock, seed, and checksum separately.
- Do not serialize arbitrary policy objects.
- Never call `torch.load` on an untrusted file. PufferLib 3.0 and the 4.0 Torch
  fallback use `torch.load` for model paths; provenance review is therefore a
  precondition, not an optional cleanup.
- Inspect metadata first with `scripts/inspect_checkpoint.py`; it never imports
  Torch or deserializes.
- Verify an expected SHA-256 and license before loading.
- If business requirements force inspection of an untrusted model, isolate the
  operation in a disposable sandbox with no credentials, network, host mounts,
  or sensitive data. PyTorch warns that models are programs and that even
  inspection tools may execute model code.

## Sources

- [PufferLib 3.0 policy example](https://github.com/PufferAI/PufferLib/blob/3.0/examples/pufferl.py)
  — stable example; accessed 2026-07-23.
- [PufferLib 3.0 PyTorch utilities](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/pytorch.py)
  — stable implementation; accessed 2026-07-23.
- [PufferLib 3.0 models](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/models.py)
  — stable model classes; accessed 2026-07-23.
- [PufferLib 4.0 models](https://github.com/PufferAI/PufferLib/blob/4.0/pufferlib/models.py)
  — current source model contract; accessed 2026-07-23.
- [PufferLib 4.0 Torch trainer](https://github.com/PufferAI/PufferLib/blob/4.0/pufferlib/torch_pufferl.py)
  — current fallback and checkpoint loading; accessed 2026-07-23.
- [PyTorch security policy](https://github.com/pytorch/pytorch/security) —
  untrusted-model guidance; accessed 2026-07-23.
- [PyTorch `torch.load` documentation](https://docs.pytorch.org/docs/stable/generated/torch.load.html)
  — deserialization warning; accessed 2026-07-23.

### `references/training.md`

# Training, Evaluation, Configuration, and Logging

Research snapshot: **2026-07-23**.

## Choose a version profile first

### Published stable package

PyPI's latest stable `pufferlib` release is **3.0.0**, published
**2025-06-23**. It declares Python `>=3.9` and is distributed only as a
60.7 MB source archive:

```text
pufferlib-3.0.0.tar.gz
sha256: 7df3a3e3f5f894d78d2a1f5374097890aec01473183e748abefe4f3faa10eaa9
```

The uploaded metadata depends on NumPy `<2.0`, Gym `<=0.23`, Gymnasium
`<=0.29.1`, PettingZoo `<=1.24.1`, Shimmy, Torch, Neptune, W&B, and other
packages without a complete transitive lock. It does not declare a CUDA
version or a minimum Torch version. Do not invent compatibility guarantees.

### Current source line

The upstream default branch is `4.0`; its `pyproject.toml` says version `4.0.0`,
Python `>=3.10`, and Torch `>=2.9`. As of the research date, this source line
is not the latest stable PyPI artifact.

The current PufferTank Dockerfile uses:

- Ubuntu 24.04
- NVIDIA CUDA `13.0.2` cuDNN development image
- Python 3.12
- the CUDA 13.0 PyTorch wheel index
- Nsight Systems `2025.6.3`

The Dockerfile does **not** pin an exact Torch wheel, uv version, PufferLib
commit, or every apt package. It is an upstream convenience environment, not a
complete reproducibility lock.

## Reproducible uv workflow

Do not use an unpinned `uv pip install pufferlib`. Work in a disposable,
project-specific environment and commit `pyproject.toml` plus `uv.lock`.

For the published profile, after reviewing the source archive and build:

```bash
uv venv --python 3.11
uv add --exact --no-sync "pufferlib==3.0.0"
uv lock
uv sync --frozen
```

Confirm the lock records the published SHA-256 above and review every resolved
dependency. The 3.0.0 source build can compile native code and may fetch build
assets. Resolve and build in a sandbox with no credentials or sensitive mounts.
Do not treat a successful resolver run as a security review.

For 4.0 source work, pin an immutable revision rather than branch `4.0`:

```bash
uv add --no-sync \
  "pufferlib @ git+https://github.com/PufferAI/PufferLib.git@25647630e1b15330bb3153a5a0d3ff8d234c3acf"
uv lock
```

The commit above is the reviewed 4.0 branch head on 2026-07-23. Re-review before
updating it. Native training still requires an audited build of a specific
environment; uv locking does not lock compilers, CUDA, NCCL, cuDNN, Raylib, or
system libraries.

Never run remote install scripts directly from a pipe. Download, inspect, pin,
verify, and execute only in an appropriate sandbox.

## Published 3.0.0 training

### CLI

The 3.0 console entry point is `puffer = pufferlib.pufferl:main`:

```bash
puffer train ENV_NAME [OPTIONS]
puffer eval ENV_NAME [OPTIONS]
puffer sweep ENV_NAME [OPTIONS]
puffer autotune ENV_NAME [OPTIONS]
puffer profile ENV_NAME [OPTIONS]
puffer export ENV_NAME [OPTIONS]
```

Environment, vector, policy, recurrent, training, and sweep values come from
INI sections. Overrides use section-qualified flags:

```bash
puffer train puffer_breakout \
  --train.device cpu \
  --train.total-timesteps 100000 \
  --vec.backend Serial \
  --vec.num-envs 2
```

Run `puffer train ENV_NAME --help` against the exact locked environment because
available options are generated from merged INI files.

### Python API

The stable trainer is `pufferlib.pufferl.PuffeRL`, not a top-level
`pufferlib.PuffeRL`:

```python
from pufferlib import pufferl

args = pufferl.load_config("puffer_breakout")
vecenv = pufferl.load_env("puffer_breakout", args)
policy = pufferl.load_policy(args, vecenv, "puffer_breakout")
trainer = pufferl.PuffeRL(args["train"], vecenv, policy)

try:
    while trainer.epoch < trainer.total_epochs:
        trainer.evaluate()
        trainer.train()
        trainer.mean_and_log()
finally:
    trainer.close()
```

The exact public methods include `evaluate`, `train`, `mean_and_log`,
`save_checkpoint`, `print_dashboard`, and `close`. Use the CLI when possible;
the Python trainer is a relatively low-level implementation surface.

### Stable configuration checks

- Make rollout/batch relationships explicit; do not rely on `auto` in a
  published experiment.
- Record environment, vector, policy, recurrent, and train sections verbatim.
- Fix `seed` in both `[vec]` and `[train]`, then run multiple independent seeds.
- Record `torch_deterministic`, precision, compile settings, optimizer, horizon,
  minibatch, and total timesteps.
- Keep evaluation seeds, instances, and metrics separate from training.

## Current 4.0 training

Build one audited environment, then use:

```bash
puffer train breakout
puffer eval breakout --load-model-path checkpoints/.../weights.bin
puffer sweep breakout
puffer match breakout \
  --load-model-path trusted-a.bin \
  --load-enemy-model-path trusted-b.bin
```

Current modes are `train`, `eval`, `sweep`, `paretosweep`, and `match`.
Native training is the default. `--slowly` selects the Torch fallback.
Configuration uses sections such as:

```ini
[vec]
total_agents = 4096
num_buffers = 2
num_threads = 16

[train]
total_timesteps = 10_000_000
minibatch_size = 8192
horizon = 64

[torch]
network = MinGRU
encoder = DefaultEncoder
decoder = DefaultDecoder
```

Current source validates that `minibatch_size` is divisible by `horizon` and
does not exceed `horizon * total_agents`. Multi-GPU launch uses spawn. Do a
small CPU/local build and contract test before CUDA training.

## Held-out evaluation

Training rollouts are not evaluation. For every reported result:

1. Freeze one checkpoint-selection rule before inspecting held-out scores.
2. Construct fresh evaluation environment instances.
3. Use evaluation seeds disjoint from training seeds.
4. Disable optimizer updates, exploration noise unless explicitly measuring it,
   curriculum updates, normalization-stat updates, and reward shaping used only
   for training.
5. Report deterministic and stochastic policy protocols separately.
6. Run enough episodes for uncertainty; report per-seed results and aggregate
   intervals, not only a best run.
7. Preserve terminated versus truncated semantics in return/length accounting.
8. Record wrappers, frame skip, autoreset mode, opponent pool, policy state
   reset, and rendering state.

Generate a starting plan:

```bash
python3 scripts/repro_plan.py --environment synthetic
```

## Checkpoints

PufferLib 3.0 saves a policy `state_dict` with `torch.save` and a separate
trainer state containing optimizer state, global step, epoch, and run ID. Its
loading paths call `torch.load`. The 4.0 native backend writes `.bin` weight
files; the 4.0 Torch fallback also uses `torch.save`/`torch.load`.

Rules:

- Never load an untrusted checkpoint, even to “inspect” it.
- Record SHA-256, size, source URL, immutable revision, license, environment,
  policy architecture, package lock, and training config in a strict JSON
  sidecar.
- Do not use `latest` in a reproducible run; resolve and record the exact path
  and digest.
- Do not auto-download a run artifact by ID.
- Test restore and evaluation in a disposable environment before a long resume.
- A model-only checkpoint is not a bitwise resume; optimizer, scheduler,
  normalizer, RNG, environment, and recurrent state may also matter.

Safe metadata inspection:

```bash
python3 scripts/inspect_checkpoint.py trusted/model.pt \
  --expected-sha256 EXPECTED_DIGEST
```

The helper hashes and classifies bytes only. It never imports Torch, invokes
pickle, opens archive members, or extracts files.

## External logging

Local logging is the default. W&B and Neptune are optional network services
that may transmit configuration, metrics, source metadata, hardware telemetry,
stdout/stderr, and explicitly uploaded checkpoints/artifacts. They can create
storage, seat, compute, or retention costs and are subject to vendor privacy,
access, and retention policies.

Credential rules:

- W&B: use the named environment variable `WANDB_API_KEY` or an approved secret
  manager.
- Neptune: use `NEPTUNE_API_TOKEN` or an approved secret manager.
- Never pass either secret as a CLI argument, INI/JSON value, logger config,
  tag, run name, or chat/tool input.
- Never print the value or include it in a broad environment dump.
- Do not recursively search for `.env` files. If policy permits a local secret
  file, read only the explicitly named key from the explicitly named file.
- Sanitize configuration before logging; reject keys containing token, secret,
  password, credential, authorization, private key, or API key.
- Disable checkpoint/source upload unless separately approved.

PufferLib 3.0 supports both `--wandb` and `--neptune`; its sweep mode requires
one. Current 4.0 source exposes W&B but no Neptune CLI integration. In either
profile, require explicit logging opt-in and disclosure acknowledgment. The
bundled training planner enforces this without reading credential values:

```bash
python3 scripts/train_template.py \
  --logger wandb \
  --enable-external-logging \
  --acknowledge-external-disclosure
```

## Sources

- [PyPI: pufferlib 3.0.0](https://pypi.org/project/pufferlib/3.0.0/) —
  released 2025-06-23; accessed 2026-07-23.
- [PyPI 3.0.0 JSON metadata](https://pypi.org/pypi/pufferlib/3.0.0/json) —
  package requirements and digest; accessed 2026-07-23.
- [PufferLib 3.0 trainer](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/pufferl.py)
  — stable CLI, logger, and checkpoint source; accessed 2026-07-23.
- [PufferLib 3.0 default config](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/config/default.ini)
  — stable parameters; accessed 2026-07-23.
- [PufferLib 4.0 docs](https://puffer.ai/docs.html) — current CLI and
  architecture; accessed 2026-07-23.
- [PufferLib 4.0 trainer](https://github.com/PufferAI/PufferLib/blob/4.0/pufferlib/pufferl.py)
  — current modes/config/checkpoints; accessed 2026-07-23.
- [PufferLib 4.0 package metadata](https://github.com/PufferAI/PufferLib/blob/4.0/pyproject.toml)
  — current Python/Torch requirements; accessed 2026-07-23.
- [PufferTank 4.0 Dockerfile](https://github.com/PufferAI/PufferTank/blob/4.0/puffertank.dockerfile)
  — CUDA/Python reference environment; accessed 2026-07-23.
- [Neptune Run API](https://docs.neptune.ai/run) — token and offline-mode
  guidance; accessed 2026-07-23.
- [W&B documentation](https://docs.wandb.ai/) — logging and credential
  guidance; accessed 2026-07-23.

### `references/vectorization.md`

# Vectorization and Throughput

Research snapshot: **2026-07-23**. PufferLib's published 3.0.0 package and
current 4.0 source line expose different vectorization systems. Never mix their
configuration names.

## Version split

| Profile | Vectorization surface | Use for |
|---|---|---|
| PyPI `pufferlib==3.0.0` | `pufferlib.vector.make`; `Serial`, `Multiprocessing`, optional `Ray`, and native `PufferEnv` backends | Published Python/Gymnasium/PettingZoo compatibility workflows |
| Source `4.0` at a pinned commit | Native C vector interface configured by `[vec] total_agents`, `num_buffers`, and `num_threads` | Current Ocean/native trainer source |

The 4.0 package directory no longer contains the 3.0 `vector.py`,
`emulation.py`, or `pytorch.py` modules. Treat old examples importing those
modules as 3.0 examples, even if a stale copy remains under the 4.0 `examples/`
tree.

## Published 3.0.0 API

The source signature is:

```python
pufferlib.vector.make(
    env_creator_or_creators,
    env_args=None,
    env_kwargs=None,
    backend=pufferlib.PufferEnv,
    num_envs=1,
    seed=0,
    **kwargs,
)
```

Select a backend explicitly during development:

```python
import pufferlib.vector

serial = pufferlib.vector.make(
    reviewed_env_creator,
    backend=pufferlib.vector.Serial,
    num_envs=4,
    seed=42,
)

parallel = pufferlib.vector.make(
    reviewed_env_creator,
    backend=pufferlib.vector.Multiprocessing,
    num_envs=16,
    num_workers=4,
    batch_size=8,
    zero_copy=True,
    seed=42,
)
```

Do not replace `reviewed_env_creator` with a dotted import string. Import the
audited callable directly in trusted code. Environment construction executes
package code and may initialize native libraries.

### Stable backends

- `PufferEnv` is the default native backend. `vector.make` requires
  `num_envs=1` for this backend because that one native environment can manage
  many agents internally.
- `Serial` runs multiple environment instances in the caller process. Use it
  for contract debugging and deterministic comparisons.
- `Multiprocessing` uses worker processes and shared arrays. It supports the
  synchronous `reset`/`step` facade and asynchronous `async_reset`/`recv` plus
  `send`/`recv`.
- `Ray` is an optional 3.0 backend and requires the package's pinned Ray extra.
  It introduces a separate distributed runtime and is not a safe local default.

### Shape semantics

Do not assume `num_envs == returned batch length`.

- A single environment advertises `num_agents`,
  `single_observation_space`, and `single_action_space`.
- The full stable batch contains agent slots. For fixed-population environments,
  serial batch length is normally `num_envs * num_agents`.
- `vecenv.agents_per_batch` is the number of agent rows returned by one receive.
- Observations have leading agent-batch dimension; rewards, terminals,
  truncations, agent IDs, and masks have matching leading length.
- A synchronous call returns
  `(observations, rewards, terminals, truncations, infos)`.
- The asynchronous `recv()` additionally returns `agent_ids` and `masks`.
- Structured observations/actions are flattened by emulation. Preserve the
  recorded dtype metadata and unflatten in the policy; do not cast arbitrary
  byte views to float first.

Validate actual shapes and dtypes at reset and the first step. In multi-agent
workflows, use masks to exclude padded or inactive slots from loss and metrics.

### Multiprocessing constraints

The 3.0 source validates these relationships:

1. `num_envs` must be divisible by `num_workers`.
2. `batch_size` defaults to `num_envs`.
3. `batch_size` must be divisible by `num_envs / num_workers`.
4. With zero-copy enabled, `num_envs` must be divisible by `batch_size`.
5. Physical-core oversubscription is rejected unless `overwork=True`; do not
   bypass this for benchmark headline numbers.

Always call `close()` in `finally`. Keep constructors top-level and serializable.
Protect process creation with `if __name__ == "__main__":`.

### Start methods

The stable API does not expose a `start_method` argument. The process context is
therefore affected by Python and platform defaults. Set an application-wide
method before constructing workers if your program requires one:

```python
import multiprocessing as mp

if __name__ == "__main__":
    mp.set_start_method("spawn")
    main()
```

Prefer `spawn` when CUDA, threads, or non-fork-safe native libraries may already
be initialized. Do not call `set_start_method(..., force=True)` inside a library.
Record the effective method in benchmark output. `forkserver` can also be
appropriate when available and tested. Never compare results that silently use
different methods.

### Seeding

- Pass one integer seed to `vector.make`; the stable implementation derives
  per-environment seeds.
- `reset(seed=base_seed)` similarly offsets seeds across serial environments.
- Seed action-space sampling separately when random actions are part of a test.
- A deterministic seed does not guarantee bitwise deterministic GPU training or
  deterministic third-party simulators.
- Recreate workers and environments for independent replicates; do not treat
  adjacent episodes from one long run as independent seeds.

## Current 4.0 source

The current default branch uses native C environments and a different vector
layout:

```ini
[vec]
total_agents = 4096
num_buffers = 2
num_threads = 16
```

Environment instances are grouped into buffers. Native execution uses OpenMP
threads inside those buffers; rollout workers coordinate buffer transfers and,
for GPU training, pinned memory and CUDA streams. The default trainer backend is
native; `--slowly` selects the PyTorch fallback. Multi-GPU launch code explicitly
uses a `spawn` multiprocessing context.

Build and test one audited Ocean environment at a time. The C binding defines
observation size/type and action branches. A mismatch can cause memory
corruption rather than a friendly Python shape error.

## Benchmark methodology

Throughput is not a library constant. Report enough detail to reproduce it:

1. Pin source/package, Python, dependencies, compiler, and environment revision.
2. Record CPU model/core topology, GPU/driver/CUDA, OS, precision, backend,
   start method, env count, agent count, workers/threads, buffers, and batch.
3. State whether timing includes construction, reset, policy inference,
   host-device transfer, learning, rendering, logging, and checkpoint I/O.
4. Warm up separately; use a fixed number of **agent steps**, not only wall time.
5. Run at least three independent repeats; report all samples plus median and
   spread. Report failures and memory use.
6. Validate equivalent observations, actions, reset/autoreset behavior, frame
   skip, and policy workload before comparing backends.
7. Distinguish simulation SPS from end-to-end training SPS.

The 2024 compatibility paper benchmarked PufferLib 1.x-style vectorization on an
i9-14900K/RTX 4090 desktop and an i7-10750H/RTX 3070 laptop. The 2025 PufferLib
2.0 paper reports a different Ocean/training system. Those results are scoped to
their listed hardware and workloads; they are not expected values for 3.0 or
4.0.

Run the bundled bounded harness first:

```bash
python3 scripts/benchmark_vectorization.py --backend serial
python3 scripts/benchmark_vectorization.py \
  --backend multiprocessing --start-method spawn \
  --envs 8 --workers 2 --steps-per-env 2000
```

It benchmarks only the bundled synthetic environment, never imports PufferLib,
and cannot substantiate an upstream PufferLib performance claim.

## Sources

- [PufferLib 3.0 vector source](https://github.com/PufferAI/PufferLib/blob/3.0/pufferlib/vector.py)
  — stable API source; accessed 2026-07-23.
- [PufferLib 3.0 vectorization example](https://github.com/PufferAI/PufferLib/blob/3.0/examples/vectorization.py)
  — stable usage example; accessed 2026-07-23.
- [PufferLib 4.0 documentation](https://puffer.ai/docs.html) — current native
  architecture and CLI; accessed 2026-07-23.
- [PufferLib 4.0 trainer source](https://github.com/PufferAI/PufferLib/blob/4.0/pufferlib/pufferl.py)
  — current config and spawn behavior; accessed 2026-07-23.
- [PufferLib compatibility paper](https://arxiv.org/abs/2406.12905) — submitted
  2024-06-18.
- [PufferLib 2.0 paper](https://openreview.net/forum?id=qRyteMTgn0) —
  Reinforcement Learning Journal, 2025.

### `scripts/__init__.py`

```python
"""Local, dependency-free helpers for the PufferLib skill."""
```

### `scripts/_common.py`

```python
#!/usr/bin/env python3
"""Shared safety and strict-JSON helpers for bundled PufferLib CLIs."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

MAX_JSON_BYTES = 1_048_576
MAX_STEPS = 1_000_000_000
MAX_ENVS = 65_536
MAX_WORKERS = 256
MAX_EVAL_EPISODES = 10_000

STABLE_SDIST_SHA256 = (
    "7df3a3e3f5f894d78d2a1f5374097890aec01473183e748abefe4f3faa10eaa9"
)
SOURCE_4_COMMIT = "25647630e1b15330bb3153a5a0d3ff8d234c3acf"

LOGGER_CREDENTIAL_ENV = {
    "none": None,
    "wandb": "WANDB_API_KEY",
    "neptune": "NEPTUNE_API_TOKEN",
}

_SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SECRET_KEY = re.compile(
    r"(?:^|_)(?:api_?key|token|secret|password|credential|"
    r"private_?key|authorization)(?:$|_)",
    re.IGNORECASE,
)


class UserInputError(ValueError):
    """Raised for bounded, user-correctable input errors."""


def bounded_int(value: str | int, *, name: str, minimum: int, maximum: int) -> int:
    """Parse an integer while rejecting bools and out-of-range values."""
    if isinstance(value, bool):
        raise UserInputError(f"{name} must be an integer, not bool")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise UserInputError(f"{name} must be an integer") from exc
    if not minimum <= parsed <= maximum:
        raise UserInputError(f"{name} must be between {minimum} and {maximum}")
    return parsed


def validate_slug(value: str, *, name: str = "name") -> str:
    """Accept a local identifier, never a dotted import path."""
    if not isinstance(value, str) or not _SLUG.fullmatch(value):
        raise UserInputError(
            f"{name} must match {_SLUG.pattern!r}; dotted import paths are not accepted"
        )
    return value


def validate_sha256(value: str, *, name: str = "sha256") -> str:
    """Validate a lowercase SHA-256 digest."""
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise UserInputError(f"{name} must be 64 lowercase hexadecimal characters")
    return value


def _reject_constant(value: str) -> None:
    raise UserInputError(f"non-finite JSON number is not allowed: {value}")


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise UserInputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _assert_finite_json(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise UserInputError(f"{path} contains a non-finite number")
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite_json(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_finite_json(item, f"{path}[{index}]")


def strict_json_loads(text: str) -> Any:
    """Load JSON with duplicate-key and non-finite-number rejection."""
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise UserInputError(
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    _assert_finite_json(value)
    return value


def strict_json_dumps(value: Any, *, pretty: bool = True) -> str:
    """Serialize deterministic JSON and reject NaN or Infinity."""
    _assert_finite_json(value)
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        sort_keys=True,
    )


def emit_json(value: Any, *, pretty: bool = True) -> None:
    print(strict_json_dumps(value, pretty=pretty))


def resolve_local_path(
    value: str | Path,
    *,
    root: str | Path,
    must_exist: bool = True,
    reject_symlink: bool = True,
) -> Path:
    """Resolve a path beneath an explicit root without directory traversal."""
    root_path = Path(root).expanduser().resolve(strict=True)
    raw_path = Path(value).expanduser()
    candidate = raw_path if raw_path.is_absolute() else root_path / raw_path
    if reject_symlink and candidate.is_symlink():
        raise UserInputError(f"symlinks are not accepted: {candidate}")
    try:
        resolved = candidate.resolve(strict=must_exist)
    except OSError as exc:
        raise UserInputError(f"cannot resolve path: {candidate}") from exc
    try:
        resolved.relative_to(root_path)
    except ValueError as exc:
        raise UserInputError(f"path escapes root {root_path}: {candidate}") from exc
    return resolved


def load_json_object(
    path: str | Path,
    *,
    root: str | Path,
    max_bytes: int = MAX_JSON_BYTES,
) -> dict[str, Any]:
    """Read one explicitly named, bounded UTF-8 JSON object."""
    resolved = resolve_local_path(path, root=root, must_exist=True)
    size = resolved.stat().st_size
    if size > max_bytes:
        raise UserInputError(f"JSON file exceeds {max_bytes} bytes: {resolved}")
    try:
        text = resolved.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise UserInputError(f"cannot read UTF-8 JSON file: {resolved}") from exc
    value = strict_json_loads(text)
    if not isinstance(value, dict):
        raise UserInputError("top-level JSON value must be an object")
    return value


def secret_key_paths(value: Any, path: str = "$") -> list[str]:
    """Return key paths that look like credential-bearing configuration."""
    matches: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")
            child_path = f"{path}.{key}"
            if _SECRET_KEY.search(normalized):
                matches.append(child_path)
            matches.extend(secret_key_paths(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            matches.extend(secret_key_paths(item, f"{path}[{index}]"))
    return matches


def require_keys(
    mapping: dict[str, Any],
    *,
    allowed: set[str],
    required: set[str],
    path: str,
) -> list[str]:
    """Return schema errors for missing and unknown mapping keys."""
    errors = [f"{path}.{key} is required" for key in sorted(required - mapping.keys())]
    errors.extend(f"{path}.{key} is not allowed" for key in sorted(mapping.keys() - allowed))
    return errors
```

### `scripts/benchmark_vectorization.py`

```python
#!/usr/bin/env python3
"""Bounded synthetic vectorization benchmark with no PufferLib import."""

from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import platform
import statistics
import time
from typing import Any

try:
    from ._common import UserInputError, bounded_int, emit_json
    from .env_template import SyntheticGymEnv
except ImportError:  # Direct script execution.
    from _common import UserInputError, bounded_int, emit_json
    from env_template import SyntheticGymEnv


def _run_partition(payload: tuple[int, int, int, int, int]) -> dict[str, Any]:
    """Run an allowlisted synthetic partition in one process."""
    start_index, num_envs, steps_per_env, seed, max_steps = payload
    agent_steps = 0
    checksum = 0.0
    resets = 0
    for offset in range(num_envs):
        env_index = start_index + offset
        env = SyntheticGymEnv(max_steps=max_steps)
        env.reset(seed=seed + env_index)
        env_resets = 0
        for step_index in range(steps_per_env):
            action = (seed + 17 * env_index + step_index) % env.action_space.n
            observation, reward, terminated, truncated, _ = env.step(action)
            checksum += reward + observation[0] * 1e-6
            agent_steps += 1
            if terminated or truncated:
                env_resets += 1
                resets += 1
                env.reset(seed=seed + env_index + env_resets * 1_000_003)
        env.close()
    return {"agent_steps": agent_steps, "checksum": checksum, "resets": resets}


def _partitions(
    *,
    num_envs: int,
    workers: int,
    steps_per_env: int,
    seed: int,
    max_steps: int,
) -> list[tuple[int, int, int, int, int]]:
    parts: list[tuple[int, int, int, int, int]] = []
    base, remainder = divmod(num_envs, workers)
    start = 0
    for worker_index in range(workers):
        count = base + int(worker_index < remainder)
        if count:
            parts.append((start, count, steps_per_env, seed, max_steps))
            start += count
    return parts


def _summarize(samples: list[float]) -> dict[str, float]:
    ordered = sorted(samples)

    def percentile(fraction: float) -> float:
        index = round((len(ordered) - 1) * fraction)
        return ordered[index]

    return {
        "maximum": max(samples),
        "median": statistics.median(samples),
        "minimum": min(samples),
        "p10": percentile(0.10),
        "p90": percentile(0.90),
    }


def benchmark(
    *,
    backend: str,
    num_envs: int,
    workers: int,
    steps_per_env: int,
    repeats: int,
    warmup_steps: int,
    seed: int,
    max_steps: int,
    start_method: str,
) -> dict[str, Any]:
    """Measure a fixed synthetic workload; never claim upstream PufferLib SPS."""
    workers = min(workers, num_envs)
    payloads = _partitions(
        num_envs=num_envs,
        workers=workers,
        steps_per_env=steps_per_env,
        seed=seed,
        max_steps=max_steps,
    )
    warmup_payloads = _partitions(
        num_envs=num_envs,
        workers=workers,
        steps_per_env=warmup_steps,
        seed=seed,
        max_steps=max_steps,
    )

    elapsed_samples: list[float] = []
    throughput_samples: list[float] = []
    checksums: list[float] = []
    observed_steps: list[int] = []

    pool: Any = None
    try:
        if backend == "multiprocessing":
            context = mp.get_context(start_method)
            pool = context.Pool(processes=workers)
            if warmup_steps:
                pool.map(_run_partition, warmup_payloads)
        elif warmup_steps:
            for payload in warmup_payloads:
                _run_partition(payload)

        for repeat_index in range(repeats):
            adjusted = [
                (start, count, steps, run_seed + repeat_index, limit)
                for start, count, steps, run_seed, limit in payloads
            ]
            started = time.perf_counter()
            if backend == "multiprocessing":
                results = pool.map(_run_partition, adjusted)
            else:
                results = [_run_partition(payload) for payload in adjusted]
            elapsed = time.perf_counter() - started
            agent_steps = sum(int(item["agent_steps"]) for item in results)
            checksum = sum(float(item["checksum"]) for item in results)
            elapsed_samples.append(elapsed)
            throughput_samples.append(agent_steps / elapsed)
            observed_steps.append(agent_steps)
            checksums.append(checksum)
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    return {
        "backend": backend,
        "benchmark": "bundled-synthetic-harness",
        "checksums": checksums,
        "elapsed_seconds": _summarize(elapsed_samples),
        "environment_construction_in_timed_region": True,
        "hardware": {
            "logical_cpus": os.cpu_count(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "network_used": False,
        "parameters": {
            "max_steps": max_steps,
            "num_envs": num_envs,
            "repeats": repeats,
            "seed": seed,
            "start_method": start_method if backend == "multiprocessing" else None,
            "steps_per_env": steps_per_env,
            "warmup_steps": warmup_steps,
            "workers": workers,
        },
        "steps_per_second": _summarize(throughput_samples),
        "total_agent_steps_per_repeat": observed_steps,
        "warning": (
            "This measures the bundled synthetic harness, not PufferLib, an Ocean "
            "environment, training throughput, or cross-machine performance."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    safe_methods = [method for method in ("spawn", "forkserver") if method in mp.get_all_start_methods()]
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark only the built-in synthetic environment. Defaults are CPU-only, "
            "network-free, and intentionally small."
        )
    )
    parser.add_argument(
        "--backend", choices=["serial", "multiprocessing"], default="serial"
    )
    parser.add_argument("--envs", type=int, default=4, help="1..128")
    parser.add_argument("--workers", type=int, default=2, help="1..32")
    parser.add_argument("--steps-per-env", type=int, default=1_000, help="1..100000")
    parser.add_argument("--repeats", type=int, default=3, help="1..7")
    parser.add_argument("--warmup-steps", type=int, default=32, help="0..1000")
    parser.add_argument("--max-steps", type=int, default=32, help="1..10000")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--start-method",
        choices=safe_methods,
        default="spawn" if "spawn" in safe_methods else safe_methods[0],
        help="fork is intentionally unavailable",
    )
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        num_envs = bounded_int(args.envs, name="envs", minimum=1, maximum=128)
        workers = bounded_int(args.workers, name="workers", minimum=1, maximum=32)
        steps = bounded_int(
            args.steps_per_env,
            name="steps_per_env",
            minimum=1,
            maximum=100_000,
        )
        repeats = bounded_int(args.repeats, name="repeats", minimum=1, maximum=7)
        warmup = bounded_int(
            args.warmup_steps, name="warmup_steps", minimum=0, maximum=1_000
        )
        max_steps = bounded_int(
            args.max_steps, name="max_steps", minimum=1, maximum=10_000
        )
        report = benchmark(
            backend=args.backend,
            num_envs=num_envs,
            workers=workers,
            steps_per_env=steps,
            repeats=repeats,
            warmup_steps=warmup,
            seed=args.seed,
            max_steps=max_steps,
            start_method=args.start_method,
        )
    except (UserInputError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    emit_json(report, pretty=not args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/env_contract_validator.py`

```python
#!/usr/bin/env python3
"""Validate a built-in synthetic environment without importing plug-ins."""

from __future__ import annotations

import argparse
import math
import random
from typing import Any

try:
    from ._common import UserInputError, bounded_int, emit_json
    from .env_template import SyntheticGymEnv
except ImportError:  # Direct script execution.
    from _common import UserInputError, bounded_int, emit_json
    from env_template import SyntheticGymEnv


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _validate_reset(result: Any, env: SyntheticGymEnv, errors: list[str]) -> Any:
    _require(
        isinstance(result, tuple) and len(result) == 2,
        "reset() must return (observation, info)",
        errors,
    )
    if not isinstance(result, tuple) or len(result) != 2:
        return None
    observation, info = result
    _require(
        env.observation_space.contains(observation),
        "reset observation is outside observation_space",
        errors,
    )
    _require(isinstance(info, dict), "reset info must be a dict", errors)
    return observation


def _validate_step(result: Any, env: SyntheticGymEnv, errors: list[str]) -> tuple[bool, bool]:
    _require(
        isinstance(result, tuple) and len(result) == 5,
        "step() must return (observation, reward, terminated, truncated, info)",
        errors,
    )
    if not isinstance(result, tuple) or len(result) != 5:
        return False, False
    observation, reward, terminated, truncated, info = result
    _require(
        env.observation_space.contains(observation),
        "step observation is outside observation_space",
        errors,
    )
    _require(
        isinstance(reward, (int, float))
        and not isinstance(reward, bool)
        and math.isfinite(float(reward)),
        "reward must be a finite scalar",
        errors,
    )
    _require(type(terminated) is bool, "terminated must be bool", errors)
    _require(type(truncated) is bool, "truncated must be bool", errors)
    _require(isinstance(info, dict), "step info must be a dict", errors)
    _require(
        not (terminated and truncated),
        "synthetic environment must not terminate and truncate simultaneously",
        errors,
    )
    return bool(terminated), bool(truncated)


def _check_determinism(seed: int, max_steps: int, errors: list[str]) -> None:
    env_a = SyntheticGymEnv(max_steps=max_steps)
    env_b = SyntheticGymEnv(max_steps=max_steps)
    first_a = env_a.reset(seed=seed)
    first_b = env_b.reset(seed=seed)
    _require(first_a == first_b, "same reset seed produced different results", errors)
    actions = [0, 2, 1, 2, 0, 1]
    for action in actions:
        result_a = env_a.step(action)
        result_b = env_b.step(action)
        _require(result_a == result_b, "same action trace produced different results", errors)
        if result_a[2] or result_a[3]:
            break
    env_a.close()
    env_b.close()


def validate_synthetic(
    *,
    seed: int,
    steps: int,
    episodes: int,
    max_steps: int,
) -> dict[str, Any]:
    """Run bounded API, space, reset, termination, and determinism checks."""
    errors: list[str] = []
    env = SyntheticGymEnv(max_steps=max_steps)
    _require(hasattr(env, "observation_space"), "missing observation_space", errors)
    _require(hasattr(env, "action_space"), "missing action_space", errors)

    action_rng = random.Random(seed + 1)
    observation = _validate_reset(env.reset(seed=seed), env, errors)
    total_steps = 0
    completed_episodes = 0
    terminations = 0
    truncations = 0

    while total_steps < steps and completed_episodes < episodes:
        action = env.action_space.sample(action_rng)
        _require(env.action_space.contains(action), "sampled action is invalid", errors)
        terminated, truncated = _validate_step(env.step(action), env, errors)
        total_steps += 1
        if terminated or truncated:
            completed_episodes += 1
            terminations += int(terminated)
            truncations += int(truncated)
            observation = _validate_reset(
                env.reset(seed=seed + completed_episodes), env, errors
            )

    _require(
        observation is None or env.observation_space.contains(observation),
        "final observation is invalid",
        errors,
    )
    _check_determinism(seed, max_steps, errors)
    env.close()
    return {
        "checks": {
            "deterministic_seed": "passed" if not errors else "see errors",
            "reset_two_tuple": True,
            "spaces": True,
            "step_five_tuple": True,
        },
        "contract": "gymnasium",
        "environment": "synthetic",
        "errors": errors,
        "network_used": False,
        "observed": {
            "episodes": completed_episodes,
            "steps": total_steps,
            "terminations": terminations,
            "truncations": truncations,
        },
        "seed": seed,
        "status": "passed" if not errors else "failed",
        "vector_shape_expectation": {
            "actions": ["num_envs"],
            "observations": ["num_envs", 4],
            "rewards": ["num_envs"],
            "terminations": ["num_envs"],
            "truncations": ["num_envs"],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate only the allowlisted built-in synthetic environment; "
            "external modules and dotted import paths are not supported."
        )
    )
    parser.add_argument("--environment", choices=["synthetic"], default="synthetic")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=64, help="1..10000")
    parser.add_argument("--episodes", type=int, default=8, help="1..100")
    parser.add_argument("--max-steps", type=int, default=16, help="1..10000")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        steps = bounded_int(args.steps, name="steps", minimum=1, maximum=10_000)
        episodes = bounded_int(args.episodes, name="episodes", minimum=1, maximum=100)
        max_steps = bounded_int(
            args.max_steps, name="max_steps", minimum=1, maximum=10_000
        )
        report = validate_synthetic(
            seed=args.seed,
            steps=steps,
            episodes=episodes,
            max_steps=max_steps,
        )
    except (UserInputError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    emit_json(report, pretty=not args.compact)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/env_template.py`

```python
#!/usr/bin/env python3
"""Dependency-free synthetic Gymnasium-style environment template.

This module is intentionally local and synthetic. It does not import PufferLib,
Gymnasium, environment plug-ins, native extensions, or ROMs. Port the contract
to a separately reviewed Gymnasium or PufferLib environment only after the
validator passes.
"""

from __future__ import annotations

import argparse
import math
import random
from dataclasses import dataclass
from typing import Any

try:
    from ._common import UserInputError, bounded_int, emit_json
except ImportError:  # Direct script execution.
    from _common import UserInputError, bounded_int, emit_json


@dataclass(frozen=True)
class DiscreteSpace:
    """Minimal stand-in for a discrete action space."""

    n: int

    @property
    def shape(self) -> tuple[int, ...]:
        return ()

    def contains(self, value: Any) -> bool:
        return isinstance(value, int) and not isinstance(value, bool) and 0 <= value < self.n

    def sample(self, rng: random.Random) -> int:
        return rng.randrange(self.n)


@dataclass(frozen=True)
class BoxSpace:
    """Minimal one-dimensional finite box used by the synthetic environment."""

    low: float
    high: float
    shape: tuple[int, ...]
    dtype: str = "float32"

    def contains(self, value: Any) -> bool:
        if len(self.shape) != 1 or not isinstance(value, (list, tuple)):
            return False
        if len(value) != self.shape[0]:
            return False
        for item in value:
            if isinstance(item, bool) or not isinstance(item, (int, float)):
                return False
            if not math.isfinite(float(item)) or not self.low <= float(item) <= self.high:
                return False
        return True


class SyntheticGymEnv:
    """Small deterministic environment implementing Gymnasium's five-tuple API."""

    metadata = {"render_modes": []}

    def __init__(self, *, max_steps: int = 16) -> None:
        if not 1 <= max_steps <= 10_000:
            raise UserInputError("max_steps must be between 1 and 10000")
        self.max_steps = max_steps
        self.observation_space = BoxSpace(-1.0, 1.0, (4,))
        self.action_space = DiscreteSpace(3)
        self._rng = random.Random()
        self._initialized = False
        self._done = False
        self._position = 0.0
        self._target = 0.75
        self._step_count = 0
        self._last_action = 0.0

    def _observation(self) -> list[float]:
        return [
            float(self._position),
            float(self._target),
            float(self._step_count / self.max_steps),
            float(self._last_action),
        ]

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[list[float], dict[str, Any]]:
        """Reset state and return ``(observation, info)``."""
        if seed is not None:
            self._rng.seed(seed)
        if options is not None and set(options) - {"position", "target"}:
            raise UserInputError("reset options may contain only position and target")

        self._position = self._rng.uniform(-0.5, 0.5)
        self._target = self._rng.choice((-0.75, 0.75))
        if options:
            self._position = float(options.get("position", self._position))
            self._target = float(options.get("target", self._target))
        if not -1.0 <= self._position <= 1.0 or not -1.0 <= self._target <= 1.0:
            raise UserInputError("position and target options must be within [-1, 1]")

        self._step_count = 0
        self._last_action = 0.0
        self._initialized = True
        self._done = False
        observation = self._observation()
        return observation, {"seed": seed, "synthetic": True}

    def step(
        self, action: int
    ) -> tuple[list[float], float, bool, bool, dict[str, Any]]:
        """Advance one step and return the Gymnasium five-tuple."""
        if not self._initialized:
            raise RuntimeError("reset() must be called before step()")
        if self._done:
            raise RuntimeError("reset() must be called after termination or truncation")
        if not self.action_space.contains(action):
            raise ValueError(f"action {action!r} is outside the action space")

        movement = (-0.125, 0.0, 0.125)[action]
        self._position = max(-1.0, min(1.0, self._position + movement))
        self._last_action = movement / 0.125
        self._step_count += 1

        distance = abs(self._target - self._position)
        terminated = distance <= 0.0625
        truncated = self._step_count >= self.max_steps and not terminated
        reward = 1.0 if terminated else -distance
        self._done = terminated or truncated
        info = {
            "distance": float(distance),
            "episode_step": self._step_count,
        }
        return self._observation(), float(reward), terminated, truncated, info

    def close(self) -> None:
        self._initialized = False
        self._done = True


def run_demo(*, seed: int, steps: int, max_steps: int) -> dict[str, Any]:
    """Run a bounded deterministic rollout for documentation and smoke tests."""
    env = SyntheticGymEnv(max_steps=max_steps)
    action_rng = random.Random(seed + 1)
    observation, _ = env.reset(seed=seed)
    total_reward = 0.0
    resets = 0
    terminated_count = 0
    truncated_count = 0

    for index in range(steps):
        action = env.action_space.sample(action_rng)
        observation, reward, terminated, truncated, _ = env.step(action)
        total_reward += reward
        terminated_count += int(terminated)
        truncated_count += int(truncated)
        if terminated or truncated:
            resets += 1
            observation, _ = env.reset(seed=seed + resets + index + 1)

    env.close()
    return {
        "environment": "synthetic",
        "last_observation": observation,
        "network_used": False,
        "resets": resets,
        "seed": seed,
        "steps": steps,
        "terminated": terminated_count,
        "total_reward": total_reward,
        "truncated": truncated_count,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the dependency-free synthetic environment template."
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=16, help="1..10000")
    parser.add_argument("--max-steps", type=int, default=16, help="1..10000")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        steps = bounded_int(args.steps, name="steps", minimum=1, maximum=10_000)
        max_steps = bounded_int(
            args.max_steps, name="max_steps", minimum=1, maximum=10_000
        )
        result = run_demo(seed=args.seed, steps=steps, max_steps=max_steps)
    except (UserInputError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    emit_json(result, pretty=not args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/inspect_checkpoint.py`

```python
#!/usr/bin/env python3
"""Inspect checkpoint file metadata without deserializing checkpoint contents."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
from pathlib import Path
from typing import Any, BinaryIO

try:
    from ._common import (
        UserInputError,
        bounded_int,
        emit_json,
        load_json_object,
        resolve_local_path,
        secret_key_paths,
        validate_sha256,
    )
except ImportError:  # Direct script execution.
    from _common import (
        UserInputError,
        bounded_int,
        emit_json,
        load_json_object,
        resolve_local_path,
        secret_key_paths,
        validate_sha256,
    )

_SIDECAR_FIELDS = {
    "created_at",
    "environment",
    "format",
    "framework",
    "framework_version",
    "license",
    "notes",
    "parent_sha256",
    "policy",
    "schema_version",
    "seed",
    "sha256",
    "source_commit",
    "source_url",
    "training_steps",
}


def _open_regular_no_follow(path: Path) -> tuple[BinaryIO, os.stat_result]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise UserInputError(f"cannot open checkpoint safely: {path}") from exc
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise UserInputError("checkpoint must be a regular file")
        return os.fdopen(descriptor, "rb"), file_stat
    except Exception:
        os.close(descriptor)
        raise


def _detect_format(prefix: bytes, suffix: str) -> dict[str, Any]:
    if prefix.startswith(b"PK\x03\x04"):
        return {
            "family": "zip-container",
            "risk": "may contain a torch.save pickle payload; not opened",
        }
    if prefix.startswith(b"\x80"):
        protocol = prefix[1] if len(prefix) > 1 else None
        return {
            "family": "pickle-like",
            "pickle_protocol_byte": protocol,
            "risk": "unsafe to deserialize unless provenance is trusted",
        }
    if suffix.lower() == ".bin":
        return {
            "family": "opaque-bin",
            "risk": "could be PufferLib native weights or another binary format",
        }
    return {
        "family": "opaque",
        "risk": "format not identified; no deserialization attempted",
    }


def _hash_and_prefix(handle: BinaryIO, *, chunk_bytes: int = 1_048_576) -> tuple[str, bytes]:
    digest = hashlib.sha256()
    prefix = b""
    while True:
        chunk = handle.read(chunk_bytes)
        if not chunk:
            break
        if not prefix:
            prefix = chunk[:16]
        digest.update(chunk)
    return digest.hexdigest(), prefix


def _safe_sidecar(
    metadata_path: str | None, *, root: str | Path
) -> tuple[dict[str, Any] | None, list[str]]:
    if metadata_path is None:
        return None, []
    raw = load_json_object(metadata_path, root=root, max_bytes=262_144)
    secret_paths = secret_key_paths(raw)
    if secret_paths:
        raise UserInputError(
            "sidecar contains credential-bearing keys: " + ", ".join(secret_paths)
        )
    safe = {key: raw[key] for key in sorted(raw) if key in _SIDECAR_FIELDS}
    unknown = sorted(set(raw) - _SIDECAR_FIELDS)
    return safe, unknown


def inspect_checkpoint(
    checkpoint_path: str,
    *,
    root: str | Path,
    metadata_path: str | None,
    expected_sha256: str | None,
    max_bytes: int,
) -> dict[str, Any]:
    """Hash and classify one local regular file without importing torch or pickle."""
    resolved = resolve_local_path(
        checkpoint_path,
        root=root,
        must_exist=True,
        reject_symlink=True,
    )
    handle, file_stat = _open_regular_no_follow(resolved)
    with handle:
        if file_stat.st_size > max_bytes:
            raise UserInputError(
                f"checkpoint is {file_stat.st_size} bytes; cap is {max_bytes}"
            )
        digest, prefix = _hash_and_prefix(handle)

    expected = validate_sha256(expected_sha256) if expected_sha256 else None
    sidecar, unknown_fields = _safe_sidecar(metadata_path, root=root)
    sidecar_digest = sidecar.get("sha256") if sidecar else None
    if sidecar_digest is not None:
        validate_sha256(sidecar_digest, name="sidecar sha256")

    return {
        "checkpoint": {
            "format_detection": _detect_format(prefix, resolved.suffix),
            "name": resolved.name,
            "sha256": digest,
            "size_bytes": file_stat.st_size,
        },
        "deserialized": False,
        "expected_sha256_matches": None if expected is None else digest == expected,
        "metadata": sidecar,
        "metadata_sha256_matches": (
            None if sidecar_digest is None else digest == sidecar_digest
        ),
        "network_used": False,
        "sidecar_unknown_fields_omitted": unknown_fields,
        "warning": (
            "Inspection does not establish trust. Verify source, license, signature or "
            "attestation, and checksum before sandboxed loading."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Hash and classify one local checkpoint without torch.load, pickle, "
            "archive extraction, dynamic imports, or network access."
        )
    )
    parser.add_argument("checkpoint", help="Checkpoint path beneath --root")
    parser.add_argument("--root", default=".", help="Allowed local path root")
    parser.add_argument("--metadata", help="Explicit strict-JSON sidecar beneath --root")
    parser.add_argument("--expected-sha256")
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=2_147_483_648,
        help="1..68719476736",
    )
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        max_bytes = bounded_int(
            args.max_bytes,
            name="max_bytes",
            minimum=1,
            maximum=68_719_476_736,
        )
        report = inspect_checkpoint(
            args.checkpoint,
            root=args.root,
            metadata_path=args.metadata,
            expected_sha256=args.expected_sha256,
            max_bytes=max_bytes,
        )
    except (UserInputError, OSError, ValueError) as exc:
        report = {
            "deserialized": False,
            "errors": [str(exc)],
            "network_used": False,
            "status": "invalid",
        }
        emit_json(report, pretty=not args.compact)
        return 1
    emit_json(report, pretty=not args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/repro_plan.py`

```python
#!/usr/bin/env python3
"""Generate a bounded reproducibility and held-out evaluation plan."""

from __future__ import annotations

import argparse
from typing import Any

try:
    from ._common import (
        SOURCE_4_COMMIT,
        STABLE_SDIST_SHA256,
        UserInputError,
        bounded_int,
        emit_json,
        validate_slug,
    )
    from .validate_plan import PROFILES
except ImportError:  # Direct script execution.
    from _common import (
        SOURCE_4_COMMIT,
        STABLE_SDIST_SHA256,
        UserInputError,
        bounded_int,
        emit_json,
        validate_slug,
    )
    from validate_plan import PROFILES


def generate_plan(
    *,
    profile: str,
    environment: str,
    base_seed: int,
    replicates: int,
    eval_episodes: int,
    benchmark_repeats: int,
) -> dict[str, Any]:
    """Create non-overlapping train/eval seeds and reporting requirements."""
    train_seeds = [base_seed + index for index in range(replicates)]
    eval_seed_base = base_seed + 1_000_000
    eval_seeds = [eval_seed_base + index for index in range(replicates)]
    if set(train_seeds) & set(eval_seeds):
        raise UserInputError("training and evaluation seeds overlap")

    if profile == "pypi-3.0.0":
        upstream = {
            "artifact": "pufferlib-3.0.0.tar.gz",
            "package": "pufferlib==3.0.0",
            "python": ">=3.9",
            "sha256": STABLE_SDIST_SHA256,
            "warning": (
                "PyPI provides only an sdist. Its build can download and compile native "
                "dependencies; audit and sandbox the build before installation."
            ),
        }
    else:
        upstream = {
            "commit": SOURCE_4_COMMIT,
            "package": "pufferlib source 4.0",
            "python": ">=3.10",
            "torch": ">=2.9",
            "warning": (
                "The 4.0 default branch is not the latest stable PyPI artifact. Pin the "
                "commit and use an audited CUDA/CPU build environment."
            ),
        }

    return {
        "benchmarking": {
            "aggregate": ["median", "p10", "p90"],
            "exclude_setup": False,
            "fixed_workload": True,
            "record": [
                "CPU model and logical/physical cores",
                "GPU model, driver, CUDA, and precision when applicable",
                "OS, Python, PufferLib, NumPy, Gymnasium, and PyTorch versions",
                "backend, start method, workers, envs, buffers, and batch size",
                "warmup, repeats, wall time, agent steps, and reset count",
            ],
            "repeats": benchmark_repeats,
            "warning": "Do not compare SPS across changed workloads or hardware.",
        },
        "environment": {
            "name": environment,
            "record": [
                "source URL and immutable revision",
                "license and asset/ROM rights",
                "environment and wrapper configuration",
                "observation/action spaces and dtypes",
                "termination, truncation, autoreset, and frame-skip semantics",
            ],
        },
        "evaluation": {
            "checkpoint_selected_without_eval_feedback": True,
            "deterministic_policy_pass": True,
            "episodes_per_seed": eval_episodes,
            "learning_disabled": True,
            "report_per_seed_and_aggregate": True,
            "seeds": eval_seeds,
            "separate_environment_instances": True,
            "stochastic_policy_pass": True,
        },
        "network_used": False,
        "profile": profile,
        "provenance": {
            "checkpoint_sha256_required": True,
            "dependency_lock_required": True,
            "record_git_diff": True,
            "record_source_commit": True,
            "upstream": upstream,
        },
        "schema_version": 1,
        "training": {
            "determinism_limitations_recorded": True,
            "seeds": train_seeds,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit a local reproducibility/evaluation plan; no packages, checkpoints, "
            "environments, GPU, or network services are opened."
        )
    )
    parser.add_argument("--profile", choices=PROFILES, default="pypi-3.0.0")
    parser.add_argument("--environment", default="synthetic")
    parser.add_argument("--base-seed", type=int, default=42)
    parser.add_argument("--replicates", type=int, default=3, help="1..32")
    parser.add_argument("--eval-episodes", type=int, default=100, help="1..10000")
    parser.add_argument("--benchmark-repeats", type=int, default=5, help="3..20")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        environment = validate_slug(args.environment, name="environment")
        base_seed = bounded_int(
            args.base_seed, name="base_seed", minimum=0, maximum=2**32 - 1_000_033
        )
        replicates = bounded_int(
            args.replicates, name="replicates", minimum=1, maximum=32
        )
        eval_episodes = bounded_int(
            args.eval_episodes,
            name="eval_episodes",
            minimum=1,
            maximum=10_000,
        )
        repeats = bounded_int(
            args.benchmark_repeats,
            name="benchmark_repeats",
            minimum=3,
            maximum=20,
        )
        plan = generate_plan(
            profile=args.profile,
            environment=environment,
            base_seed=base_seed,
            replicates=replicates,
            eval_episodes=eval_episodes,
            benchmark_repeats=repeats,
        )
    except (UserInputError, ValueError) as exc:
        parser.error(str(exc))
    emit_json(plan, pretty=not args.compact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/train_template.py`

```python
#!/usr/bin/env python3
"""Safe PufferLib training-plan template.

This script never imports PufferLib, starts training, loads checkpoints, uses a
GPU, or contacts an external logger. It emits a validated argv preview for a
human to review in an appropriately sandboxed, pinned environment.
"""

from __future__ import annotations

import argparse
import copy
from typing import Any

try:
    from ._common import LOGGER_CREDENTIAL_ENV, UserInputError, bounded_int, emit_json, validate_slug
    from .validate_plan import PROFILES, default_plan, validate_plan
except ImportError:  # Direct script execution.
    from _common import LOGGER_CREDENTIAL_ENV, UserInputError, bounded_int, emit_json, validate_slug
    from validate_plan import PROFILES, default_plan, validate_plan


def _command_preview(plan: dict[str, Any]) -> list[str]:
    """Build argv without shell interpolation or execution."""
    environment = plan["environment"]["name"]
    if environment == "synthetic":
        return []

    training = plan["training"]
    vector = plan["vectorization"]
    command = [
        "puffer",
        "train",
        environment,
        "--train.total-timesteps",
        str(training["total_timesteps"]),
        "--train.seed",
        str(training["seed"]),
    ]
    if plan["profile"] == "pypi-3.0.0":
        backend_name = {
            "serial": "Serial",
            "multiprocessing": "Multiprocessing",
            "native": "PufferEnv",
        }[vector["backend"]]
        command.extend(
            [
                "--train.device",
                training["device"],
                "--vec.backend",
                backend_name,
                "--vec.num-envs",
                str(vector["num_envs"]),
                "--vec.num-workers",
                str(vector["num_workers"]),
                "--vec.batch-size",
                str(vector["batch_size"]),
            ]
        )
    else:
        command.extend(
            [
                "--vec.total-agents",
                str(vector["total_agents"]),
                "--vec.num-buffers",
                str(vector["num_buffers"]),
                "--vec.num-threads",
                str(vector["num_threads"]),
            ]
        )
        if vector["backend"] == "torch":
            command.append("--slowly")

    logger = plan["logging"]["backend"]
    if logger != "none":
        command.append(f"--{logger}")
    if not plan["logging"]["upload_checkpoints"] and plan["profile"] == "pypi-3.0.0":
        command.append("--no-model-upload")
    return command


def make_plan(args: argparse.Namespace) -> dict[str, Any]:
    plan = default_plan(args.profile)
    environment = validate_slug(args.environment, name="environment")
    plan["environment"]["name"] = environment
    plan["environment"]["adapter"] = args.adapter
    plan["environment"]["provenance_verified"] = (
        environment == "synthetic" or args.provenance_verified
    )

    plan["training"].update(
        {
            "device": args.device,
            "horizon": bounded_int(
                args.horizon, name="horizon", minimum=1, maximum=65_536
            ),
            "minibatch_size": bounded_int(
                args.minibatch_size,
                name="minibatch_size",
                minimum=1,
                maximum=16_777_216,
            ),
            "seed": bounded_int(
                args.seed, name="seed", minimum=0, maximum=2**32 - 1
            ),
            "total_timesteps": bounded_int(
                args.total_timesteps,
                name="total_timesteps",
                minimum=1,
                maximum=1_000_000_000,
            ),
        }
    )
    plan["evaluation"].update(
        {
            "deterministic": args.deterministic_eval,
            "episodes": bounded_int(
                args.eval_episodes,
                name="eval_episodes",
                minimum=1,
                maximum=10_000,
            ),
            "seed": bounded_int(
                args.eval_seed, name="eval_seed", minimum=0, maximum=2**32 - 1
            ),
            "separate": True,
        }
    )
    plan["logging"].update(
        {
            "backend": args.logger,
            "disclosure_ack": args.acknowledge_external_disclosure,
            "external_opt_in": args.enable_external_logging,
            "upload_checkpoints": args.upload_checkpoints,
        }
    )
    if args.profile == "pypi-3.0.0":
        backend = args.backend or "serial"
        plan["vectorization"].update(
            {
                "backend": backend,
                "batch_size": bounded_int(
                    args.batch_size,
                    name="batch_size",
                    minimum=1,
                    maximum=65_536,
                ),
                "num_envs": bounded_int(
                    args.num_envs, name="num_envs", minimum=1, maximum=65_536
                ),
                "num_workers": bounded_int(
                    args.num_workers,
                    name="num_workers",
                    minimum=1,
                    maximum=256,
                ),
                "start_method": args.start_method,
                "zero_copy": args.zero_copy,
            }
        )
    else:
        backend = args.backend or "torch"
        plan["vectorization"].update(
            {
                "backend": backend,
                "num_buffers": bounded_int(
                    args.num_buffers, name="num_buffers", minimum=1, maximum=256
                ),
                "num_threads": bounded_int(
                    args.num_threads, name="num_threads", minimum=1, maximum=256
                ),
                "start_method": "spawn",
                "total_agents": bounded_int(
                    args.total_agents,
                    name="total_agents",
                    minimum=1,
                    maximum=65_536,
                ),
            }
        )
        plan["checkpoint"]["format"] = (
            "state_dict" if backend == "torch" else "native-bin"
        )
    return plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a bounded, local PufferLib dry-run plan. This command never "
            "executes the generated argv."
        )
    )
    parser.add_argument("--profile", choices=PROFILES, default="pypi-3.0.0")
    parser.add_argument("--environment", default="synthetic")
    parser.add_argument(
        "--adapter",
        choices=["synthetic", "gymnasium", "pettingzoo", "native-ocean"],
        default="synthetic",
    )
    parser.add_argument(
        "--provenance-verified",
        action="store_true",
        help="Explicitly attest review for a non-synthetic environment",
    )
    parser.add_argument(
        "--backend",
        choices=["serial", "multiprocessing", "native", "torch"],
        default=None,
    )
    parser.add_argument("--num-envs", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--zero-copy", action="store_true")
    parser.add_argument(
        "--start-method", choices=["spawn", "forkserver"], default="spawn"
    )
    parser.add_argument("--total-agents", type=int, default=64)
    parser.add_argument("--num-buffers", type=int, default=2)
    parser.add_argument("--num-threads", type=int, default=1)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--total-timesteps", type=int, default=10_000)
    parser.add_argument("--horizon", type=int, default=16)
    parser.add_argument("--minibatch-size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--eval-seed", type=int, default=1_000_042)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument(
        "--stochastic-eval",
        dest="deterministic_eval",
        action="store_false",
        default=True,
    )
    parser.add_argument("--logger", choices=["none", "wandb", "neptune"], default="none")
    parser.add_argument("--enable-external-logging", action="store_true")
    parser.add_argument("--acknowledge-external-disclosure", action="store_true")
    parser.add_argument("--upload-checkpoints", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan = make_plan(args)
        errors = validate_plan(plan)
        logger = plan["logging"]["backend"]
        report = {
            "command_preview": _command_preview(plan) if not errors else [],
            "credential": {
                "environment_variable": LOGGER_CREDENTIAL_ENV.get(logger),
                "value_read_or_logged": False,
            },
            "dry_run": True,
            "errors": errors,
            "external_logging_disclosure": (
                "External services may receive configuration, metrics, source metadata, "
                "hardware telemetry, and explicitly enabled artifacts; review vendor "
                "privacy, retention, access, and pricing before use."
                if logger != "none"
                else None
            ),
            "network_used": False,
            "plan": copy.deepcopy(plan),
            "status": "valid" if not errors else "invalid",
        }
    except (UserInputError, KeyError, ValueError) as exc:
        report = {
            "command_preview": [],
            "dry_run": True,
            "errors": [str(exc)],
            "network_used": False,
            "plan": None,
            "status": "invalid",
        }
    emit_json(report, pretty=not args.compact)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### `scripts/validate_plan.py`

```python
#!/usr/bin/env python3
"""Strict, dependency-free validator for PufferLib training plans."""

from __future__ import annotations

import argparse
import copy
import re
from typing import Any

try:
    from ._common import (
        LOGGER_CREDENTIAL_ENV,
        MAX_ENVS,
        MAX_EVAL_EPISODES,
        MAX_STEPS,
        MAX_WORKERS,
        SOURCE_4_COMMIT,
        STABLE_SDIST_SHA256,
        UserInputError,
        emit_json,
        load_json_object,
        require_keys,
        secret_key_paths,
        validate_slug,
    )
except ImportError:  # Direct script execution.
    from _common import (
        LOGGER_CREDENTIAL_ENV,
        MAX_ENVS,
        MAX_EVAL_EPISODES,
        MAX_STEPS,
        MAX_WORKERS,
        SOURCE_4_COMMIT,
        STABLE_SDIST_SHA256,
        UserInputError,
        emit_json,
        load_json_object,
        require_keys,
        secret_key_paths,
        validate_slug,
    )

PROFILES = ("pypi-3.0.0", "source-4.0")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")


def default_plan(profile: str = "pypi-3.0.0") -> dict[str, Any]:
    """Return a bounded local plan that never starts training."""
    if profile not in PROFILES:
        raise UserInputError(f"profile must be one of {PROFILES}")
    common: dict[str, Any] = {
        "schema_version": 1,
        "profile": profile,
        "environment": {
            "adapter": "synthetic",
            "name": "synthetic",
            "provenance_verified": True,
        },
        "training": {
            "device": "cpu",
            "horizon": 16,
            "minibatch_size": 256,
            "seed": 42,
            "total_timesteps": 10_000,
        },
        "evaluation": {
            "deterministic": True,
            "episodes": 10,
            "seed": 1_000_042,
            "separate": True,
        },
        "logging": {
            "backend": "none",
            "disclosure_ack": False,
            "external_opt_in": False,
            "upload_checkpoints": False,
        },
        "checkpoint": {
            "format": "state_dict",
            "trusted_only": True,
        },
    }
    if profile == "pypi-3.0.0":
        common["package"] = {
            "name": "pufferlib",
            "sha256": STABLE_SDIST_SHA256,
            "version": "3.0.0",
        }
        common["vectorization"] = {
            "backend": "serial",
            "batch_size": 4,
            "num_envs": 4,
            "num_workers": 1,
            "start_method": "spawn",
            "zero_copy": False,
        }
    else:
        common["package"] = {
            "commit": SOURCE_4_COMMIT,
            "name": "pufferlib",
            "version": "4.0.0-source",
        }
        common["vectorization"] = {
            "backend": "torch",
            "num_buffers": 2,
            "num_threads": 1,
            "start_method": "spawn",
            "total_agents": 64,
        }
    return common


def _mapping(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def _integer(
    value: Any,
    *,
    path: str,
    minimum: int,
    maximum: int,
    errors: list[str],
) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{path} must be an integer")
        return None
    if not minimum <= value <= maximum:
        errors.append(f"{path} must be between {minimum} and {maximum}")
        return None
    return value


def _boolean(value: Any, *, path: str, errors: list[str]) -> bool | None:
    if type(value) is not bool:
        errors.append(f"{path} must be boolean")
        return None
    return value


def _validate_package(
    package: dict[str, Any], profile: str, errors: list[str]
) -> None:
    if profile == "pypi-3.0.0":
        errors.extend(
            require_keys(
                package,
                allowed={"name", "version", "sha256"},
                required={"name", "version", "sha256"},
                path="$.package",
            )
        )
        if package.get("version") != "3.0.0":
            errors.append("$.package.version must equal 3.0.0")
        if package.get("sha256") != STABLE_SDIST_SHA256:
            errors.append("$.package.sha256 must match the published 3.0.0 sdist")
    elif profile == "source-4.0":
        errors.extend(
            require_keys(
                package,
                allowed={"name", "version", "commit"},
                required={"name", "version", "commit"},
                path="$.package",
            )
        )
        commit = package.get("commit")
        if not isinstance(commit, str) or not _COMMIT.fullmatch(commit):
            errors.append("$.package.commit must be a pinned 40-character commit")
        if package.get("version") != "4.0.0-source":
            errors.append("$.package.version must equal 4.0.0-source")
    if package.get("name") != "pufferlib":
        errors.append("$.package.name must equal pufferlib")


def _validate_environment(environment: dict[str, Any], errors: list[str]) -> None:
    errors.extend(
        require_keys(
            environment,
            allowed={"adapter", "name", "provenance_verified"},
            required={"adapter", "name", "provenance_verified"},
            path="$.environment",
        )
    )
    try:
        validate_slug(environment.get("name"), name="environment.name")
    except UserInputError as exc:
        errors.append(str(exc))
    if environment.get("adapter") not in {
        "synthetic",
        "gymnasium",
        "pettingzoo",
        "native-ocean",
    }:
        errors.append("$.environment.adapter is not allowlisted")
    if environment.get("name") == "synthetic" and environment.get("adapter") != "synthetic":
        errors.append("the synthetic environment must use the synthetic adapter")
    if environment.get("name") != "synthetic" and environment.get("adapter") == "synthetic":
        errors.append("a non-synthetic environment cannot use the synthetic adapter")
    if environment.get("provenance_verified") is not True:
        errors.append("$.environment.provenance_verified must be true")


def _validate_training(training: dict[str, Any], errors: list[str]) -> None:
    errors.extend(
        require_keys(
            training,
            allowed={"device", "horizon", "minibatch_size", "seed", "total_timesteps"},
            required={"device", "horizon", "minibatch_size", "seed", "total_timesteps"},
            path="$.training",
        )
    )
    if training.get("device") not in {"cpu", "cuda"}:
        errors.append("$.training.device must be cpu or cuda")
    _integer(
        training.get("seed"),
        path="$.training.seed",
        minimum=0,
        maximum=2**32 - 1,
        errors=errors,
    )
    _integer(
        training.get("total_timesteps"),
        path="$.training.total_timesteps",
        minimum=1,
        maximum=MAX_STEPS,
        errors=errors,
    )
    horizon = _integer(
        training.get("horizon"),
        path="$.training.horizon",
        minimum=1,
        maximum=65_536,
        errors=errors,
    )
    minibatch = _integer(
        training.get("minibatch_size"),
        path="$.training.minibatch_size",
        minimum=1,
        maximum=16_777_216,
        errors=errors,
    )
    if horizon and minibatch and minibatch % horizon:
        errors.append("$.training.minibatch_size must be divisible by horizon")


def _validate_vectorization(
    vectorization: dict[str, Any],
    profile: str,
    training: dict[str, Any],
    errors: list[str],
) -> None:
    if profile == "pypi-3.0.0":
        allowed = {
            "backend",
            "batch_size",
            "num_envs",
            "num_workers",
            "start_method",
            "zero_copy",
        }
        errors.extend(
            require_keys(
                vectorization,
                allowed=allowed,
                required=allowed,
                path="$.vectorization",
            )
        )
        backend = vectorization.get("backend")
        if backend not in {
            "serial",
            "multiprocessing",
            "native",
        }:
            errors.append("$.vectorization.backend is invalid for PufferLib 3.0.0")
        num_envs = _integer(
            vectorization.get("num_envs"),
            path="$.vectorization.num_envs",
            minimum=1,
            maximum=MAX_ENVS,
            errors=errors,
        )
        workers = _integer(
            vectorization.get("num_workers"),
            path="$.vectorization.num_workers",
            minimum=1,
            maximum=MAX_WORKERS,
            errors=errors,
        )
        batch = _integer(
            vectorization.get("batch_size"),
            path="$.vectorization.batch_size",
            minimum=1,
            maximum=MAX_ENVS,
            errors=errors,
        )
        zero_copy = _boolean(
            vectorization.get("zero_copy"),
            path="$.vectorization.zero_copy",
            errors=errors,
        )
        if vectorization.get("start_method") not in {"spawn", "forkserver"}:
            errors.append("$.vectorization.start_method must be spawn or forkserver")
        if num_envs and workers and num_envs % workers:
            errors.append("$.vectorization.num_envs must be divisible by num_workers")
        if num_envs and batch and batch > num_envs:
            errors.append("$.vectorization.batch_size cannot exceed num_envs")
        if num_envs and batch and zero_copy and num_envs % batch:
            errors.append(
                "$.vectorization.num_envs must be divisible by batch_size "
                "when zero_copy is true"
            )
        if num_envs and workers and batch:
            envs_per_worker = num_envs // workers if num_envs % workers == 0 else 0
            if envs_per_worker and batch % envs_per_worker:
                errors.append(
                    "$.vectorization.batch_size must be divisible by envs_per_worker"
                )
        if backend == "native" and num_envs != 1:
            errors.append(
                "$.vectorization.num_envs must equal 1 for the stable native backend"
            )
    else:
        allowed = {
            "backend",
            "num_buffers",
            "num_threads",
            "start_method",
            "total_agents",
        }
        errors.extend(
            require_keys(
                vectorization,
                allowed=allowed,
                required=allowed,
                path="$.vectorization",
            )
        )
        if vectorization.get("backend") not in {"native", "torch"}:
            errors.append("$.vectorization.backend must be native or torch")
        agents = _integer(
            vectorization.get("total_agents"),
            path="$.vectorization.total_agents",
            minimum=1,
            maximum=MAX_ENVS,
            errors=errors,
        )
        buffers = _integer(
            vectorization.get("num_buffers"),
            path="$.vectorization.num_buffers",
            minimum=1,
            maximum=256,
            errors=errors,
        )
        _integer(
            vectorization.get("num_threads"),
            path="$.vectorization.num_threads",
            minimum=1,
            maximum=MAX_WORKERS,
            errors=errors,
        )
        if vectorization.get("start_method") != "spawn":
            errors.append("$.vectorization.start_method must be spawn for 4.0")
        if agents and buffers and agents % buffers:
            errors.append("$.vectorization.total_agents must be divisible by num_buffers")
        horizon = training.get("horizon")
        minibatch = training.get("minibatch_size")
        if (
            isinstance(agents, int)
            and isinstance(horizon, int)
            and isinstance(minibatch, int)
            and minibatch > agents * horizon
        ):
            errors.append(
                "$.training.minibatch_size cannot exceed total_agents * horizon"
            )


def _validate_evaluation(
    evaluation: dict[str, Any], training: dict[str, Any], errors: list[str]
) -> None:
    allowed = {"deterministic", "episodes", "seed", "separate"}
    errors.extend(
        require_keys(
            evaluation,
            allowed=allowed,
            required=allowed,
            path="$.evaluation",
        )
    )
    _boolean(evaluation.get("deterministic"), path="$.evaluation.deterministic", errors=errors)
    _boolean(evaluation.get("separate"), path="$.evaluation.separate", errors=errors)
    _integer(
        evaluation.get("episodes"),
        path="$.evaluation.episodes",
        minimum=1,
        maximum=MAX_EVAL_EPISODES,
        errors=errors,
    )
    _integer(
        evaluation.get("seed"),
        path="$.evaluation.seed",
        minimum=0,
        maximum=2**32 - 1,
        errors=errors,
    )
    if evaluation.get("separate") is not True:
        errors.append("$.evaluation.separate must be true")
    if evaluation.get("seed") == training.get("seed"):
        errors.append("training and evaluation seeds must differ")


def _validate_logging(
    logging: dict[str, Any], profile: str, errors: list[str]
) -> None:
    allowed = {
        "backend",
        "disclosure_ack",
        "external_opt_in",
        "upload_checkpoints",
    }
    errors.extend(
        require_keys(logging, allowed=allowed, required=allowed, path="$.logging")
    )
    backend = logging.get("backend")
    if backend not in LOGGER_CREDENTIAL_ENV:
        errors.append("$.logging.backend must be none, wandb, or neptune")
        return
    if profile == "source-4.0" and backend == "neptune":
        errors.append("Neptune is not a current source-4.0 integration")
    opt_in = _boolean(
        logging.get("external_opt_in"),
        path="$.logging.external_opt_in",
        errors=errors,
    )
    disclosure = _boolean(
        logging.get("disclosure_ack"),
        path="$.logging.disclosure_ack",
        errors=errors,
    )
    upload = _boolean(
        logging.get("upload_checkpoints"),
        path="$.logging.upload_checkpoints",
        errors=errors,
    )
    if backend == "none" and any(value is True for value in (opt_in, disclosure, upload)):
        errors.append("external logging flags must be false when backend is none")
    if backend != "none" and (opt_in is not True or disclosure is not True):
        errors.append(
            "external logging requires external_opt_in=true and disclosure_ack=true"
        )


def _validate_checkpoint(checkpoint: dict[str, Any], errors: list[str]) -> None:
    allowed = {"format", "trusted_only"}
    errors.extend(
        require_keys(
            checkpoint,
            allowed=allowed,
            required=allowed,
            path="$.checkpoint",
        )
    )
    if checkpoint.get("format") not in {"state_dict", "native-bin", "opaque"}:
        errors.append("$.checkpoint.format is invalid")
    if checkpoint.get("trusted_only") is not True:
        errors.append("$.checkpoint.trusted_only must be true")


def validate_plan(plan: Any) -> list[str]:
    """Return all deterministic schema and safety errors."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["$ must be an object"]
    secret_paths = secret_key_paths(plan)
    if secret_paths:
        errors.append(
            "credential-bearing keys are forbidden in plans: " + ", ".join(secret_paths)
        )
    top_allowed = {
        "checkpoint",
        "environment",
        "evaluation",
        "logging",
        "package",
        "profile",
        "schema_version",
        "training",
        "vectorization",
    }
    errors.extend(
        require_keys(
            plan,
            allowed=top_allowed,
            required=top_allowed,
            path="$",
        )
    )
    if plan.get("schema_version") != 1:
        errors.append("$.schema_version must equal 1")
    profile = plan.get("profile")
    if profile not in PROFILES:
        errors.append(f"$.profile must be one of {PROFILES}")
        return errors

    package = _mapping(plan.get("package"), "$.package", errors)
    environment = _mapping(plan.get("environment"), "$.environment", errors)
    training = _mapping(plan.get("training"), "$.training", errors)
    vectorization = _mapping(plan.get("vectorization"), "$.vectorization", errors)
    evaluation = _mapping(plan.get("evaluation"), "$.evaluation", errors)
    logging = _mapping(plan.get("logging"), "$.logging", errors)
    checkpoint = _mapping(plan.get("checkpoint"), "$.checkpoint", errors)

    _validate_package(package, profile, errors)
    _validate_environment(environment, errors)
    _validate_training(training, errors)
    _validate_vectorization(vectorization, profile, training, errors)
    _validate_evaluation(evaluation, training, errors)
    _validate_logging(logging, profile, errors)
    _validate_checkpoint(checkpoint, errors)
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a strict local JSON plan. With no --config, validate the "
            "bounded built-in dry-run plan."
        )
    )
    parser.add_argument("--config", help="Explicit JSON file beneath --root")
    parser.add_argument("--root", default=".", help="Allowed local path root")
    parser.add_argument("--profile", choices=PROFILES, default="pypi-3.0.0")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        plan = (
            load_json_object(args.config, root=args.root)
            if args.config
            else default_plan(args.profile)
        )
        errors = validate_plan(plan)
        report = {
            "errors": errors,
            "network_used": False,
            "plan": copy.deepcopy(plan),
            "status": "valid" if not errors else "invalid",
        }
    except UserInputError as exc:
        report = {
            "errors": [str(exc)],
            "network_used": False,
            "plan": None,
            "status": "invalid",
        }
    emit_json(report, pretty=not args.compact)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
```
